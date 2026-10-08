"""Read-only Windows inventory; mutations require the engine's apply authority.

No authentication stores, environment values, process arguments or secret files
are inspected. External command failures are converted to fixed reason codes.
"""
from __future__ import annotations

import ctypes
import hashlib
import json
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import socket

from .credentials import KINDS, unavailable, validated_metadata
from .engine import SECRET_PATTERN, SetupError, safe_path
from datetime import datetime, timezone

PINNED_IMAGE = "ghcr.io/youling/opencode-foreman@sha256:fa92f37752ff6132b161ed4c2563897c94b014ab70d650846dcb09f354f55261"


def trusted_windows_powershell() -> str | None:
    """Use the OS directory API, never PATH or caller-controlled SystemRoot."""
    if sys.platform != 'win32':
        return None
    try:
        buffer = ctypes.create_unicode_buffer(32768)
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.GetSystemDirectoryW.argtypes = [ctypes.c_wchar_p, ctypes.c_uint]
        kernel.GetSystemDirectoryW.restype = ctypes.c_uint
        count = kernel.GetSystemDirectoryW(buffer, len(buffer))
        if not 0 < count < len(buffer):
            return None
        path = Path(buffer.value) / 'WindowsPowerShell' / 'v1.0' / 'powershell.exe'
        if not path.is_file() or any(p.is_symlink() or (p.exists() and getattr(p.lstat(), 'st_file_attributes', 0) & 0x400) for p in (path, *path.parents)):
            return None
        return str(path)
    except (OSError, AttributeError):
        return None


def frozen_provenance() -> dict:
    if not getattr(sys, 'frozen', False):
        return {'state': 'SCRIPT_MODE', 'python_verified': False}
    try:
        from .packaging import bundle_provenance
        proof = bundle_provenance()
        return proof if isinstance(proof, dict) else {'state': 'BUNDLE_UNVERIFIED', 'python_verified': False}
    except Exception:
        return {'state': 'BUNDLE_UNVERIFIED', 'python_verified': False}


def wsl_app_version(text: str) -> str | None:
    """Only accept an explicitly labelled WSL application version, not a kernel."""
    text = text.replace("\x00", "")
    match = re.search(r"(?im)^\s*WSL\s*(?:version|版本)\s*[:：]\s*(\d+\.\d+\.\d+(?:\.\d+)?)\s*$", text)
    return match.group(1) if match else None


def wsl_supported(version: str | None) -> bool:
    return bool(version and re.fullmatch(r"\d+\.\d+\.\d+(?:\.\d+)?", version)
                and tuple(map(int, version.split("."))) >= (3, 0, 0))


def documents_known_folder() -> str | None:
    if sys.platform != "win32":
        return None
    import uuid

    class GUID(ctypes.Structure):
        _fields_ = [("data1", ctypes.c_uint32), ("data2", ctypes.c_uint16),
                    ("data3", ctypes.c_uint16), ("data4", ctypes.c_ubyte * 8)]

    guid = GUID.from_buffer_copy(uuid.UUID("FDD39AD0-238F-46AF-ADB4-6C85480369C7").bytes_le)
    shell = ctypes.WinDLL("shell32", use_last_error=True)
    ole = ctypes.WinDLL("ole32", use_last_error=True)
    shell.SHGetKnownFolderPath.argtypes = [ctypes.POINTER(GUID), ctypes.c_uint32,
                                          ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)]
    shell.SHGetKnownFolderPath.restype = ctypes.c_long
    ole.CoTaskMemFree.argtypes = [ctypes.c_void_p]
    pointer = ctypes.c_void_p()
    # DONT_VERIFY avoids creation or access repair of the Known Folder.
    result = shell.SHGetKnownFolderPath(ctypes.byref(guid), 0x4000, None, ctypes.byref(pointer))
    try:
        return ctypes.wstring_at(pointer) if result == 0 and pointer.value else None
    finally:
        if pointer.value:
            ole.CoTaskMemFree(pointer)


def normalize_inventory(raw: dict) -> dict:
    """Whitelist the scanner protocol. Never persist raw scanner output/errors."""
    volumes = []
    for item in raw.get("volumes", []):
        if not isinstance(item, dict) or not re.fullmatch(r"[A-Z]:[/\\]", str(item.get("mount", ""))):
            continue
        volume = {key: str(item.get(key, "UNKNOWN"))[:100]
                  for key in ("mount", "fs", "device_id", "media_type", "bus_type")}
        for key in ("capacity_bytes", "free_bytes"):
            value = item.get(key)
            volume[key] = value if type(value) is int and value >= 0 else None
        volumes.append(volume)
    version = wsl_app_version(str(raw.get("wsl_version_text", "")))
    state = raw.get("wslc_state")
    state = state if state in ("PASS", "BLOCKED", "UNKNOWN") else "UNKNOWN"
    count = raw.get("wslc_active_count")
    return {"volumes": volumes, "wsl_app_version": version,
            "wslc_capability": {"state": state, "reason": {
                "PASS": "NATIVE_WSLC_METADATA_ACCESS_PASS",
                "BLOCKED": "WSLC_EXECUTABLE_ABSENT",
                "UNKNOWN": "WSLC_METADATA_ACCESS_UNVERIFIED"}[state]},
            "active_workloads": [{"kind": "WSLC", "state": "ACTIVE", "count": count}]
            if type(count) is int and count > 0 else [],
            "storage_state": "PASS" if volumes else "UNKNOWN"}


class WindowsAdapter:
    def __init__(self, *, apply_authorized: bool = False, runner=None, credential_custodian=None):
        self.platform = "windows" if sys.platform == "win32" else sys.platform
        self.can_apply = sys.platform == "win32" and not getattr(sys, 'frozen', False)
        # This candidate is an unsigned CI artifact, not a distribution authority.
        # A flag cannot promote its content hashes into trusted Host permission.
        self.apply_authorized = apply_authorized and not getattr(sys, 'frozen', False)
        self._runner = runner or subprocess.run
        self._credential_custodian = credential_custodian

    def discover_credentials(self) -> dict:
        # Executable existence is only an installation hint. Never execute an
        # arbitrary gh on PATH or inspect native application authentication DBs.
        found = {kind: unavailable(kind, installed=kind == 'github' and bool(shutil.which('gh.exe'))) for kind in KINDS}
        if self._credential_custodian is not None:
            for kind in KINDS:
                try:
                    found[kind] = validated_metadata(kind, self._credential_custodian.discover(kind))
                except Exception:
                    found[kind] = unavailable(kind)
        return found

    def connect_credential(self, kind: str, mode: str = 'auto', approved: bool = False) -> dict:
        if kind not in KINDS or mode not in {'auto', 'manual'}:
            return {'state': 'BLOCKED', 'reason_code': 'CREDENTIAL_SELECTION_INVALID', 'plan_inputs': {}}
        entry = self.discover_credentials()[kind]
        if not approved:
            return {**entry, 'state': 'NOT_AUTHORIZED', 'reason_code': 'ACCOUNT_SCOPE_CONSENT_REQUIRED', 'plan_inputs': {}}
        if not self.can_apply or not self.apply_authorized:
            return {**entry, 'state': 'HUMAN_GATE', 'reason_code': 'REAL_HOST_CONNECTION_NOT_AUTHORIZED', 'plan_inputs': {}}
        # Manual OAuth belongs to the existing Host custody owner. The TUI never
        # runs a shell login or collects a raw credential as an installation input.
        if self._credential_custodian is None:
            return {**entry, 'state': 'NEEDS_CONNECTION', 'reason_code': 'TRUSTED_HOST_LOGIN_REQUIRED', 'plan_inputs': {}}
        if mode == 'auto' and not entry['reusable']:
            return {**entry, 'plan_inputs': {}}
        try:
            proof = validated_metadata(kind, self._credential_custodian.connect(kind, mode=mode))
        except Exception:
            proof = unavailable(kind)
        return {**proof, 'state': 'CONNECTION_PENDING_PROJECTION' if proof['reusable'] else proof['state'], 'plan_inputs': {}}

    def _python_signature(self, powershell: str) -> dict:
        # Verify the base executable, not a potentially unsigned venv launcher.
        # The path is JSON stdin data, never interpolated as PowerShell source.
        script = r"""$ErrorActionPreference='Stop';
[Console]::OutputEncoding=[System.Text.UTF8Encoding]::new($false);
try {
  $request=[Console]::In.ReadToEnd() | ConvertFrom-Json;
  $signature=Get-AuthenticodeSignature -LiteralPath $request.path;
  $psf=$false;
  if ($signature.SignerCertificate) {
    $subject=$signature.SignerCertificate.Subject;
    $psf=$subject -match '(?:^|,\s*)(?:CN|O)\s*=\s*"?Python Software Foundation"?(?:,|$)';
  }
  @{status=[string]$signature.Status; psf_signer=[bool]$psf} | ConvertTo-Json -Compress;
} catch { @{status='UnknownError';psf_signer=$false} | ConvertTo-Json -Compress }"""
        try:
            result = self._runner([powershell, "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", script],
                                  input=json.dumps({"path": getattr(sys, "_base_executable", sys.executable)}),
                                  capture_output=True, encoding="utf-8", errors="replace", timeout=20)
            raw = json.loads(result.stdout) if result.returncode == 0 and len(result.stdout) <= 4096 else {}
            if not isinstance(raw, dict):
                raise ValueError("signature metadata invalid")
            status = raw.get("status")
            if status not in {"Valid", "NotSigned", "HashMismatch", "NotTrusted", "UnknownError", "NotSupportedFileFormat", "Incompatible"}:
                status = "UnknownError"
            return {"state": "PASS" if status == "Valid" and raw.get("psf_signer") is True else "BLOCKED",
                    "status": status, "signer": "PYTHON_SOFTWARE_FOUNDATION" if raw.get("psf_signer") is True else "UNVERIFIED"}
        except (OSError, ValueError, subprocess.TimeoutExpired):
            return {"state": "UNKNOWN", "status": "UnknownError", "signer": "UNVERIFIED"}

    def probe(self) -> dict:
        observation = {"schema": "1.0.0", "platform": self.platform,
                       "python_version": platform.python_version(),
                       "python_verified": False,
                       "python_signature": {"state": "UNKNOWN", "status": "UnknownError", "signer": "UNVERIFIED"},
                       "documents": None, "volumes": [], "existing_roots": {},
                       "active_workloads": [], "wsl_app_version": None,
                       "wslc_capability": {"state": "UNKNOWN", "reason": "WINDOWS_REQUIRED"},
                       "github": {"state": "NOT_AUTHORIZED", "reason": "APPROVED_HELPER_PROJECTION_REQUIRED"},
                       "model": {"state": "NOT_AUTHORIZED", "reason": "PROVIDER_SELECTION_AND_AUTHORITY_REQUIRED"},
                       "observed_at": datetime.now(timezone.utc).isoformat()}
        if self.platform != 'windows':
            return observation
        observation["documents"] = documents_known_folder()
        frozen = bool(getattr(sys, 'frozen', False))
        powershell = trusted_windows_powershell() if frozen else (shutil.which("pwsh.exe") or trusted_windows_powershell() or shutil.which("powershell.exe"))
        observation['github'].update(self.discover_credentials()['github'])
        observation['model'].update(self.discover_credentials()['model'])
        observation['wslc_storage'] = {'state': 'UNKNOWN', 'reason': 'ACTUAL_WSLC_STORAGE_NOT_OBSERVED'}
        try:
            with socket.socket() as port_probe:
                port_probe.settimeout(0.2)
                observation['local_port'] = {'port': 4096, 'occupied': port_probe.connect_ex(('127.0.0.1', 4096)) == 0,
                                            'action': 'PRESERVE_EXISTING_SERVICE_LOCAL_PROFILE_HAS_NO_HOST_PUBLISH'}
        except OSError:
            observation['local_port'] = {'port': 4096, 'state': 'UNKNOWN'}
        if frozen:
            proof = frozen_provenance()
            observation['runtime_provenance'] = proof
            verified = (proof.get('state') == 'VERIFIED_CONTENT_UNSIGNED_TEST_ONLY'
                        and proof.get('bundle_verified') is True
                        and proof.get('python_verified') is True
                        and sys.version_info[:2] == (3, 14)
                        and sys.version_info.releaselevel == 'final')
            observation['python_signature'] = {'state': 'PASS' if verified else 'BLOCKED',
                'status': 'EMBEDDED_RUNTIME_VERIFIED' if verified else 'UnknownError',
                'signer': 'PSF_EMBEDDED_DLL_WITH_UNSIGNED_DISTRIBUTION' if verified else 'UNVERIFIED'}
            observation['python_verified'] = verified
        elif powershell:
            observation["python_signature"] = self._python_signature(powershell)
            observation["python_verified"] = (sys.version_info[:2] == (3, 14)
                                              and sys.version_info.releaselevel == "final"
                                              and observation["python_signature"]["state"] == "PASS")
        if powershell:
            try:
                probe_script = Path(__file__).with_name('probe_windows.ps1')
                if frozen:
                    from .packaging import verified_bundle_root
                    probe_script = verified_bundle_root() / 'agent_setup' / 'probe_windows.ps1'
                result = self._runner([powershell, "-NoLogo", "-NoProfile", "-NonInteractive",
                                       "-File", str(probe_script)],
                                      capture_output=True, encoding="utf-8", errors="replace", timeout=25)
                if result.returncode == 0:
                    raw = json.loads(result.stdout)
                    if isinstance(raw, dict):
                        observation.update(normalize_inventory(raw))
            except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired):
                pass
        # Existence metadata only, no traversal or reads of HOST_AGENT/credentials.
        documents = observation["documents"]
        observation["existing_roots"] = {"host_agent": bool(documents and (Path(documents) / "HOST_AGENT.md").is_file())}
        return observation

    def pull_image(self, pinnedref: str) -> dict:
        if pinnedref != PINNED_IMAGE:
            return {"state": "BLOCKED", "reason": "RELEASED_EXACT_DIGEST_REQUIRED"}
        if not self.can_apply or not self.apply_authorized:
            return {"state": "NOT_AUTHORIZED", "reason": "WINDOWS_APPLY_AUTHORITY_REQUIRED"}
        executable = shutil.which("wslc.exe")
        if not executable:
            return {"state": "BLOCKED", "reason": "WSLC_EXECUTABLE_ABSENT"}
        try:
            result = self._runner([executable, "pull", pinnedref], capture_output=True, timeout=300)
            if result.returncode:
                return {"state": "BLOCKED", "reason": "EXACT_IMAGE_PULL_FAILED"}
            result = self._runner([executable, "inspect", pinnedref, "--format", "json"],
                                  capture_output=True, encoding="utf-8", timeout=15)
            info = json.loads(result.stdout)[0] if result.returncode == 0 else {}
            config_id = info.get("Id", info.get("ID", ""))
            if not re.fullmatch(r"sha256:[a-f0-9]{64}", config_id):
                return {"state": "BLOCKED", "reason": "IMAGE_CONFIG_DIGEST_UNVERIFIED"}
            if pinnedref not in info.get("RepoDigests", []):
                return {"state": "BLOCKED", "reason": "IMAGE_MANIFEST_DIGEST_UNVERIFIED"}
            return {"state": "PASS", "manifest_digest": pinnedref.split("@", 1)[1], "config_id": config_id}
        except (OSError, ValueError, IndexError, TypeError, subprocess.TimeoutExpired):
            return {"state": "BLOCKED", "reason": "IMAGE_READBACK_FAILED"}

    def helper_status(self, path: str, *, approved: bool = False, operation: str = "status", request: dict | None = None) -> dict:
        """An explicitly approved owner helper returns metadata, never raw secrets.

        Approval is an engine review decision, never inferred from executable
        existence or a successful response. The helper owns actual credential
        custody, permission checks and proofs. No search through key catalogs.
        """
        if not approved or not self.can_apply:
            return {"state": "NOT_AUTHORIZED", "reason": "EXPLICIT_HELPER_APPROVAL_REQUIRED"}
        if operation not in {"status", "verify", "writeback"}:
            return {"state": "BLOCKED", "reason": "HELPER_OPERATION_DENIED"}
        if operation == "writeback" and (not self.apply_authorized or request is None):
            return {"state": "NOT_AUTHORIZED", "reason": "CONTEXT_WRITEBACK_AUTHORITY_REQUIRED"}
        executable = Path(path)
        if not executable.is_absolute() or not executable.is_file() or any(
                p.is_symlink() or (p.exists() and getattr(p.lstat(), "st_file_attributes", 0) & 0x400)
                for p in (executable, *executable.parents)):
            return {"state": "BLOCKED", "reason": "APPROVED_HELPER_PATH_INVALID"}
        try:
            result = self._runner([str(executable), operation, "--json"], capture_output=True,
                                  encoding="utf-8", input=json.dumps(request) if request is not None else None, timeout=30)
            if result.returncode or len(result.stdout) > 16384:
                return {"state": "BLOCKED", "reason": "HELPER_METADATA_UNAVAILABLE"}
            raw = json.loads(result.stdout)
            if not isinstance(raw, dict) or raw.get("state") not in {"READY", "PASS", "NOT_AUTHORIZED", "BLOCKED"}:
                raise ValueError("invalid helper metadata")
            output = {"state": raw["state"]}
            for key in ("projection_directory", "server_env"):
                value = raw.get(key)
                if isinstance(value, str) and not SECRET_PATTERN.search(value) and len(value) <= 4096 and not any(c in value for c in "\r\n\x00") and Path(value).is_absolute():
                    output[key] = value
            for key, pattern in (("work", r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+#[1-9][0-9]*"),
                                 ("model_ref", r"[A-Za-z0-9_.:/#-]{1,256}"),
                                 ("repo", r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+"),
                                 ("context_sha256", r"[a-f0-9]{64}"),
                                 ("durable_destination", r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/blob/[A-Za-z0-9_./-]+")):
                if isinstance(raw.get(key), str) and not SECRET_PATTERN.search(raw[key]) and re.fullmatch(pattern, raw[key]):
                    output[key] = raw[key]
            for key in ("authenticated_api", "github_read", "github_write", "fresh_recovery", "private_destination", "model_ready"):
                if type(raw.get(key)) is bool:
                    output[key] = raw[key]
            return output
        except (OSError, ValueError, subprocess.TimeoutExpired):
            return {"state": "BLOCKED", "reason": "HELPER_METADATA_UNAVAILABLE"}

    def runtime_readiness(self,plan:dict)->dict:
        github=plan.get('github',{})
        if not self.apply_authorized or not github.get('authorized') or not github.get('helper_approved'):
            return {'credentials':'NOT_AUTHORIZED','model':'NOT_AUTHORIZED'}
        status=self.helper_status(github.get('helper',''),approved=True)
        bound=(status.get('state') in {'READY','PASS'} and status.get('repo')==github.get('repo')
            and status.get('work')==github.get('work') and bool(status.get('projection_directory')) and bool(status.get('server_env')))
        # Model input/checkbox never becomes proof; the approved helper attests
        # the selected exact reference after metadata readiness verification.
        model_bound=bound and bool(plan.get('model',{}).get('ref')) and status.get('model_ref')==plan['model']['ref'] and status.get('model_ready') is True
        return {'credentials':'PASS' if bound else 'NOT_AUTHORIZED','model':'PASS' if model_bound else 'NOT_AUTHORIZED'}

    def writeback_context(self, plan: dict, target: Path, sha: str) -> dict:
        github = plan.get("github", {})
        if not self.can_apply or not self.apply_authorized or not github.get("authorized") or not github.get("helper_approved"):
            return {"state": "NOT_AUTHORIZED", "reason": "APPROVED_PRIVATE_DESTINATION_AUTHORITY_REQUIRED"}
        repo, work, destination = github.get("repo", ""), github.get("work", ""), github.get("durable_destination", "")
        if (not re.fullmatch(r"[a-f0-9]{64}", sha) or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo)
                or not work.startswith(repo + "#") or not re.fullmatch(re.escape(repo) + r"#[1-9][0-9]*", work)
                or not re.fullmatch(r"https://github\.com/" + re.escape(repo) + r"/blob/[A-Za-z0-9_./-]+", destination)
                or any(segment in {".", ".."} for segment in destination.split("/"))):
            return {"state": "BLOCKED", "reason": "CONCRETE_DURABLE_DESTINATION_REQUIRED"}
        target = Path(target)
        if not target.is_absolute() or target.is_symlink() or not target.is_file():
            return {"state": "BLOCKED", "reason": "CONTEXT_SOURCE_INVALID"}
        try:
            if hashlib.sha256(target.read_bytes()).hexdigest() != sha:
                return {"state": "BLOCKED", "reason": "CONTEXT_SOURCE_HASH_MISMATCH"}
        except OSError:
            return {"state": "BLOCKED", "reason": "CONTEXT_SOURCE_INVALID"}
        request = {"context_path": str(target), "sha256": sha, "durable_destination": destination, "repo": repo, "work": work}
        observed = self.helper_status(github.get("helper", ""), approved=True, operation="writeback", request=request)
        if (observed.get("state") == "PASS" and observed.get("context_sha256") == sha
                and observed.get("repo") == repo and observed.get("work") == work
                and observed.get("private_destination") is True
                and observed.get("durable_destination") == destination):
            return {"state": "PASS", "context_sha256": sha, "durable_destination": destination}
        return {"state": "NOT_AUTHORIZED", "reason": "DURABLE_CONTEXT_WRITEBACK_UNVERIFIED"}

    @staticmethod
    def _launcher_command() -> list[str]:
        if getattr(sys, 'frozen', False):
            # Fixed internal mode executes only the manifest-verified launcher;
            # never treat sys.executable as a general Python script interpreter.
            from .packaging import verified_bundle_root
            verified_bundle_root()
            return [sys.executable, '--launcher-dispatch']
        launcher = Path(__file__).resolve().parents[2] / 'host' / 'windows' / 'launch.py'
        return [sys.executable, str(launcher)]

    def start_local_runtime(self, plan: dict, host_path: Path) -> dict:
        if not self.can_apply or not self.apply_authorized:
            return {'state': 'NOT_AUTHORIZED', 'reason': 'WINDOWS_APPLY_AUTHORITY_REQUIRED'}
        runtime = plan.get('runtime', {})
        name = runtime.get('name', '')
        if not re.fullmatch(r'[a-z][a-z0-9-]{1,60}', name) or not all(runtime.get(k) for k in ('attempt', 'incoming', 'outgoing')):
            return {'state': 'BLOCKED', 'reason': 'BOUNDED_RUNTIME_PATHS_REQUIRED'}
        wslc = shutil.which('wslc.exe')
        if not wslc:
            return {'state': 'BLOCKED', 'reason': 'WSLC_EXECUTABLE_ABSENT'}
        argv = self._launcher_command() + ['--host-agent', str(host_path), '--wslc', wslc,
                '--attempt', str(runtime['attempt']), '--name', name, '--local-only',
                '--input', str(runtime['incoming']), '--output', str(runtime['outgoing'])]
        try:
            result = self._runner(argv, capture_output=True, encoding='utf-8', timeout=45)
            receipt = json.loads(result.stdout) if result.returncode == 0 and len(result.stdout) <= 16384 else {}
            local_hash = hashlib.sha256(Path(host_path).read_bytes()).hexdigest()
            if (receipt.get('started') is not True or receipt.get('name') != name
                or receipt.get('local_only') is not True or receipt.get('network') != 'none'
                or receipt.get('scoped_auth') is not True or receipt.get('host_agent_sha256') != local_hash
                or not re.fullmatch(r'sha256:[a-f0-9]{64}', receipt.get('image', ''))):
                return {'state': 'BLOCKED', 'reason': 'LOCAL_PROFILE_LAUNCH_UNVERIFIED'}
            return {'state': 'READY', 'name': name, 'config_id': receipt['image'],
                    'host_agent_sha256': local_hash, 'local_only': True, 'scoped_auth': 'CONFIGURED',
                    'reason': 'NETWORK_DISABLED_OWNED_LOCAL_PROFILE_VERIFY_REQUIRED'}
        except (OSError, ValueError, subprocess.TimeoutExpired):
            return {'state': 'BLOCKED', 'reason': 'LOCAL_PROFILE_LAUNCH_FAILED'}

    def start_runtime(self, plan: dict, host_path: Path) -> dict:
        if not self.can_apply or not self.apply_authorized:
            return {"state": "NOT_AUTHORIZED", "reason": "WINDOWS_APPLY_AUTHORITY_REQUIRED"}
        github = plan.get("github", {})
        if not github.get("authorized") or not github.get("helper_approved"):
            return {"state": "NOT_AUTHORIZED", "reason": "EXTERNAL_PROJECTION_OWNER_AND_AUTHENTICATED_LAUNCH_REQUIRED"}
        status = self.helper_status(github.get("helper", ""), approved=True)
        if status.get("state") not in {"READY", "PASS"} or not all(status.get(k) for k in ("projection_directory", "server_env", "repo", "work")):
            return {"state": "NOT_AUTHORIZED", "reason": "PROTECTED_PROJECTION_NOT_READY"}
        # Refuse a helper for a different durable destination than the review.
        if status["repo"] != github.get("repo") or status["work"] != github.get("work"):
            return {"state": "BLOCKED", "reason": "HELPER_DURABLE_SCOPE_MISMATCH"}
        runtime = plan.get("runtime", {})
        name = runtime.get("name", "")
        if not re.fullmatch(r"[a-z][a-z0-9-]{1,60}", name):
            return {"state": "BLOCKED", "reason": "OWNED_RUNTIME_NAME_REQUIRED"}
        if not all(runtime.get(k) for k in ("attempt", "incoming", "outgoing")):
            return {"state": "BLOCKED", "reason": "BOUNDED_RUNTIME_PATHS_REQUIRED"}
        wslc = shutil.which("wslc.exe")
        if not wslc:
            return {"state": "BLOCKED", "reason": "WSLC_EXECUTABLE_ABSENT"}
        argv = self._launcher_command() + ["--host-agent", str(host_path), "--wslc", wslc,
                "--attempt", str(runtime["attempt"]), "--name", name,
                "--github-projection", status["projection_directory"],
                "--input", str(runtime["incoming"]), "--output", str(runtime["outgoing"]),
                "--server-env", status["server_env"], "--host-port", str(runtime.get("port", 4096))]
        try:
            result = self._runner(argv, capture_output=True, encoding="utf-8", timeout=45)
            receipt = json.loads(result.stdout) if result.returncode == 0 and len(result.stdout) <= 16384 else {}
            digest = receipt.get("image", "")
            if receipt.get("started") is not True or receipt.get("name") != name or not re.fullmatch(r"sha256:[a-f0-9]{64}", digest):
                return {"state": "BLOCKED", "reason": "EXISTING_LAUNCHER_START_FAILED"}
            local_hash = hashlib.sha256(Path(host_path).read_bytes()).hexdigest()
            if receipt.get("host_agent_sha256") != local_hash:
                return {"state": "BLOCKED", "reason": "HOST_CONTEXT_COPY_UNVERIFIED", "name": name}
            return {"state": "READY", "name": name, "config_id": digest,
                    "host_agent_sha256": local_hash, "reason": "LAUNCHER_STARTED_RUNTIME_VERIFY_REQUIRED"}
        except (OSError, ValueError, subprocess.TimeoutExpired):
            return {"state": "BLOCKED", "reason": "EXISTING_LAUNCHER_START_FAILED"}

    @staticmethod
    def _local_mounts_verified(mounts, expected_sources) -> bool:
        """Missing backend evidence is denial, never a reason to skip isolation."""
        modes = {'/host-context': False, '/exchange/in': False, '/exchange/out': True}
        if (not isinstance(mounts, list) or len(mounts) != len(modes)
            or not isinstance(expected_sources, dict) or set(expected_sources) != set(modes)):
            return False
        seen = set()
        try:
            for mount in mounts:
                if not isinstance(mount, dict):return False
                destination = mount.get('Destination')
                if (not isinstance(destination, str) or destination not in modes or destination in seen
                    or mount.get('Type') != 'bind' or mount.get('RW') is not modes[destination]):return False
                source, expected = mount.get('Source'), expected_sources[destination]
                if (not isinstance(source, str) or not isinstance(expected, str)
                    or not Path(source).is_absolute() or not Path(expected).is_absolute()
                    or safe_path(source) != safe_path(expected)):return False
                seen.add(destination)
        except (SetupError, OSError, ValueError, TypeError):
            return False
        return seen == set(modes)

    def verify_runtime(self, name: str, host_path: Path, *, expected_config_id: str, expected_local: bool = False, expected_mount_sources: dict | None = None) -> dict:
        if not self.can_apply or not re.fullmatch(r"[a-z][a-z0-9-]{1,60}", name) or not re.fullmatch(r"sha256:[a-f0-9]{64}", expected_config_id):
            return {"state": "BLOCKED", "reason": "RUNTIME_VERIFICATION_INPUT_INVALID"}
        wslc = shutil.which("wslc.exe")
        if not wslc:
            return {"state": "BLOCKED", "reason": "WSLC_EXECUTABLE_ABSENT"}
        try:
            result = self._runner([wslc, "inspect", name, "--format", "json"], capture_output=True, encoding="utf-8", timeout=15)
            info = json.loads(result.stdout)[0] if result.returncode == 0 else {}
            if info.get("Config", {}).get("Labels", {}).get("agent.attempt") != name or info.get("Image") != expected_config_id:
                return {"state": "BLOCKED", "reason": "OWNED_IMAGE_OR_LEASE_UNVERIFIED"}
            if expected_local and info.get('Config', {}).get('Labels', {}).get('agent.setup.profile') != 'local-only':
                return {'state': 'BLOCKED', 'reason': 'LOCAL_PROFILE_IDENTITY_UNVERIFIED'}
            if (info.get('Config', {}).get('Labels', {}).get('agent.setup.profile') == 'local-only'
                and not self._local_mounts_verified(info.get('Mounts'), expected_mount_sources)):
                return {'state': 'BLOCKED', 'reason': 'LOCAL_MOUNT_BOUNDARY_UNVERIFIED'}
            # Fixed command with no auth/env printing; read only the bounded context.
            script = "import os,hashlib,json;print(json.dumps({'uid':os.getuid(),'hash':hashlib.sha256(open('/host-context/HOST_AGENT.md','rb').read()).hexdigest()}))"
            result = self._runner([wslc, "exec", name, "python3", "-c", script], capture_output=True, encoding="utf-8", timeout=15)
            observed = json.loads(result.stdout) if result.returncode == 0 else {}
            if observed.get("uid") != 1000 or observed.get("hash") != hashlib.sha256(Path(host_path).read_bytes()).hexdigest():
                return {"state": "BLOCKED", "reason": "NONROOT_CONTEXT_READ_UNVERIFIED"}
            proof = {"state": "PASS", "nonroot": True, "local_context_read": True, "config_id": expected_config_id}
            if info.get('Config', {}).get('Labels', {}).get('agent.setup.profile') == 'local-only':
                if (info.get('HostConfig', {}).get('NetworkMode') != 'none'
                    or info.get('HostConfig', {}).get('PortBindings')
                    or str(info.get('Config', {}).get('User')) not in {'1000', '1000:1000'}):
                    return {'state': 'BLOCKED', 'reason': 'LOCAL_NETWORK_BOUNDARY_UNVERIFIED'}
                # Auth is used internally, never exported in stdout or argv.
                script = """import os,json,base64,urllib.request,urllib.error
u='http://127.0.0.1:4096/global/health'
def call(auth=False):
 r=urllib.request.Request(u)
 if auth:r.add_header('Authorization','Basic '+base64.b64encode(('opencode:'+os.environ['OPENCODE_SERVER_PASSWORD']).encode()).decode())
 try:
  with urllib.request.urlopen(r,timeout=3) as x:return x.status
 except urllib.error.HTTPError as e:return e.code
try: print(json.dumps({'denied':call()==401,'authenticated':call(True)==200}))
except Exception: print(json.dumps({'denied':False,'authenticated':False}))
"""
                result = self._runner([wslc, 'exec', name, 'python3', '-c', script], capture_output=True, encoding='utf-8', timeout=15)
                api = json.loads(result.stdout) if result.returncode == 0 and len(result.stdout) <= 4096 else {}
                proof.update(local_only=True, network_disabled=True,
                             server_authenticated='PASS' if api.get('denied') is True and api.get('authenticated') is True else 'NOT_VERIFIED')
            return proof
        except (OSError, ValueError, TypeError, IndexError, subprocess.TimeoutExpired):
            return {"state": "BLOCKED", "reason": "RUNTIME_READBACK_FAILED"}
