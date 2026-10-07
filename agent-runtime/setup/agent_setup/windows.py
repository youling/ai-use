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
from datetime import datetime, timezone

PINNED_IMAGE = "ghcr.io/youling/opencode-foreman@sha256:fa92f37752ff6132b161ed4c2563897c94b014ab70d650846dcb09f354f55261"


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
    def __init__(self, *, apply_authorized: bool = False, runner=None):
        self.platform = "windows" if sys.platform == "win32" else sys.platform
        self.can_apply = sys.platform == "win32"
        self.apply_authorized = apply_authorized
        self._runner = runner or subprocess.run

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
        if not self.can_apply:
            return observation
        observation["documents"] = documents_known_folder()
        powershell = shutil.which("pwsh.exe") or shutil.which("powershell.exe")
        gh=shutil.which('gh.exe')
        if gh:
            try:
                state=self._runner([gh,'auth','status','--active','--hostname','github.com','--json','hosts'],capture_output=True,encoding='utf-8',timeout=15)
                metadata=json.loads(state.stdout) if state.returncode==0 and len(state.stdout)<16384 else {}
                entries=metadata.get('hosts',{}).get('github.com',[])
                observation['github']['native_store_discovered']=any(item.get('active') is True for item in entries if isinstance(item,dict))
                observation['github']['runtime_projection']='NOT_AUTHORIZED_HOST_LOGIN_IS_NOT_RUNTIME_CUSTODY'
            except (OSError,ValueError,TypeError,subprocess.TimeoutExpired):
                observation['github']['native_store_discovered']=False
        if powershell:
            observation["python_signature"] = self._python_signature(powershell)
            observation["python_verified"] = (sys.version_info[:2] == (3, 14)
                                              and sys.version_info.releaselevel == "final"
                                              and observation["python_signature"]["state"] == "PASS")
            try:
                result = self._runner([powershell, "-NoLogo", "-NoProfile", "-NonInteractive",
                                       "-File", str(Path(__file__).with_name("probe_windows.ps1"))],
                                      capture_output=True, encoding="utf-8", errors="replace", timeout=25)
                if result.returncode == 0:
                    raw = json.loads(result.stdout)
                    if isinstance(raw, dict):
                        observation.update(normalize_inventory(raw))
            except (OSError, ValueError, subprocess.TimeoutExpired):
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
                if isinstance(value, str) and len(value) <= 4096 and not any(c in value for c in "\r\n\x00") and Path(value).is_absolute():
                    output[key] = value
            for key, pattern in (("work", r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+#[1-9][0-9]*"),
                                 ("repo", r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+"),
                                 ("context_sha256", r"[a-f0-9]{64}"),
                                 ("durable_destination", r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/blob/[A-Za-z0-9_./-]+")):
                if isinstance(raw.get(key), str) and re.fullmatch(pattern, raw[key]):
                    output[key] = raw[key]
            for key in ("authenticated_api", "github_read", "github_write", "fresh_recovery", "private_destination"):
                if type(raw.get(key)) is bool:
                    output[key] = raw[key]
            return output
        except (OSError, ValueError, subprocess.TimeoutExpired):
            return {"state": "BLOCKED", "reason": "HELPER_METADATA_UNAVAILABLE"}

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
        launcher = Path(__file__).resolve().parents[2] / "host" / "windows" / "launch.py"
        argv = [sys.executable, str(launcher), "--host-agent", str(host_path), "--wslc", wslc,
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

    def verify_runtime(self, name: str, host_path: Path, *, expected_config_id: str) -> dict:
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
            # Fixed command with no auth/env printing; read only the bounded context.
            script = "import os,hashlib,json;print(json.dumps({'uid':os.getuid(),'hash':hashlib.sha256(open('/host-context/HOST_AGENT.md','rb').read()).hexdigest()}))"
            result = self._runner([wslc, "exec", name, "python3", "-c", script], capture_output=True, encoding="utf-8", timeout=15)
            observed = json.loads(result.stdout) if result.returncode == 0 else {}
            if observed.get("uid") != 1000 or observed.get("hash") != hashlib.sha256(Path(host_path).read_bytes()).hexdigest():
                return {"state": "BLOCKED", "reason": "NONROOT_CONTEXT_READ_UNVERIFIED"}
            return {"state": "PASS", "nonroot": True, "local_context_read": True, "config_id": expected_config_id}
        except (OSError, ValueError, TypeError, IndexError, subprocess.TimeoutExpired):
            return {"state": "BLOCKED", "reason": "RUNTIME_READBACK_FAILED"}
