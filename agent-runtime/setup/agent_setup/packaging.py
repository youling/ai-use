"""Content provenance is distinct from distributor trust and Host authority.

The embedded manifest detects corruption of resources/runtime. An unsigned
manifest/EXE cannot establish publisher identity: installation remains denied.
The reviewed CI provenance and externally checked EXE SHA256 are the evidence
for this preview artifact; no synthetic manifest can create release authority.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import platform
import subprocess
import sys
import ctypes
from contextlib import contextmanager
import threading
import base64


class BundleError(RuntimeError):
    def __init__(self, code, *, signature_phase=None):
        super().__init__(code)
        self.signature_phase = signature_phase if signature_phase in SIGNATURE_PHASES else None


NATIVE_PROCESS_LOCK = threading.RLock()
SIGNATURE_PHASES = frozenset({'STARTED', 'MODULE_LOADED', 'SIGNATURE_ENTER', 'SIGNATURE_RETURN'})
PUBLIC_EXE_CODES = frozenset({
    'STARTUP_FAILED', 'FROZEN_NATIVE_RESOURCE_SCAN_FAILED', 'SELF_TEST_NATIVE_PLANNING_FAILED',
    'SELF_TEST_PRODUCTION_ADAPTER_OR_AUTHORITY_FAILED', 'SELF_TEST_NATIVE_PIPELINE_NOT_EXERCISED',
    'SELF_TEST_EXISTING_CONTEXT_CASE_FAILED', 'SELF_TEST_PREFLIGHT_NOT_FAIL_CLOSED',
    'SELF_TEST_EXPECTED_PREFLIGHT_GATE_NOT_BLOCKED', 'SELF_TEST_CORRUPTION_NOT_FAIL_CLOSED',
    'SELF_TEST_FIRST_SCREEN_NOT_VERIFIED', 'SELF_TEST_EXISTING_CONTEXT_FIRST_NEXT_FAILED',
    'SELF_TEST_METADATA_OWNER_ACTION_NOT_VISIBLE', 'SELF_TEST_AUTHORITY_LEAK',
    'SELF_TEST_FORCED_NATIVE_FALLBACK_FAILED', 'SELF_TEST_FORCED_NATIVE_FALLBACK_FIRST_NEXT_FAILED',
    'SELF_TEST_NATIVE_FALLBACK_RUNTIME_GATE_BYPASS',
    'UNSIGNED_DISTRIBUTION_HOST_APPLY_DENIED', 'UNKNOWN_ARGUMENT', 'SELF_TEST_OUTPUT_REQUIRED',
    'ACCEPTANCE_SCENARIO_INVALID', 'ACCEPTANCE_NATIVE_PS5_UNAVAILABLE', 'ACCEPTANCE_JUNCTION_UNAVAILABLE',
    'ACCEPTANCE_NATIVE_INVENTORY_INVALID', 'ACCEPTANCE_EXISTING_FILE_CHANGED',
    'ACCEPTANCE_UNEXPECTED_INSTALLER_WRITE', 'ACCEPTANCE_UNEXPECTED_CONTEXT_WRITE'})
ACCEPTANCE_STAGES = frozenset({'BUNDLE_PROVENANCE', 'NATIVE_RESOURCE_SCAN', 'NATIVE_READ_ONLY_PLANNING',
    'CONTEXT_FIXTURE_BUILD', 'CONTEXT_PLAN', 'CONTEXT_SNAPSHOT_CHECK', 'PREFLIGHT_COUNTEREXAMPLE',
    'CORRUPTION_COUNTEREXAMPLE', 'TUI_PROBE', 'TUI_NEXT', 'TUI_SNAPSHOT', 'SELF_TEST_RECEIPT_WRITE', 'COMPLETE'})
ACCEPTANCE_SCENARIOS = frozenset({'fresh', 'legacy_v1', 'malformed_state', 'malformed_exchange',
    'extra_state', 'extra_exchange', 'stale', 'collision', 'junction'})
NATIVE_CHECKS = frozenset({'platform_windows', 'mutation_disabled', 'documents_metadata_present',
    'volumes_metadata_present', 'python_verified', 'bundle_verified', 'bundle_python_verified', 'bundle_state_verified',
    'case_plan_ready', 'storage_capacity_pass', 'root_placement_capacity_pass'})
INVENTORY_SOURCES = frozenset({'WINDOWS_POWERSHELL', 'WINDOWS_WIN32_FALLBACK', 'UNVERIFIED'})
PUBLIC_PLAN_GATES = frozenset({'WINDOWS_V1', 'PYTHON_314', 'WSL_APP_3', 'WSLC', 'CONTEXT_CURRENT',
    'STORAGE_CAPACITY', 'ROOT_WORKSPACE', 'ROOT_CONFIG', 'ROOT_CACHE', 'ROOT_TEMP', 'ACTIVE_WORKLOAD_UNKNOWN',
    'DOCUMENTS_KNOWN_FOLDER', 'PLACEMENT_WORKSPACE', 'PLACEMENT_CONFIG', 'PLACEMENT_CACHE', 'PLACEMENT_TEMP',
    'PLACEMENT_EXCHANGE', 'PLACEMENT_HOST_AGENT'})
PUBLIC_BUNDLE_CODES = frozenset({
    'BUNDLE_MANIFEST_MISSING', 'BUNDLE_MANIFEST_INVALID', 'BUNDLE_INVENTORY_INCOMPLETE',
    'BUNDLE_RESOURCE_INVALID', 'BUNDLE_RESOURCE_REPARSE', 'BUNDLE_RESOURCE_HASH_MISMATCH',
    'FROZEN_BUNDLE_REQUIRED', 'WINDOWS_LOADED_RUNTIME_REQUIRED', 'LOADED_RUNTIME_MODULE_UNKNOWN',
    'LOADED_RUNTIME_MODULE_OUTSIDE_BUNDLE', 'LOADED_RUNTIME_HASH_MISMATCH',
    'BUNDLED_RUNTIME_VERSION_MISMATCH', 'BUNDLED_RUNTIME_PSF_SIGNATURE_UNVERIFIED',
    'SIGNATURE_NATIVE_POWERSHELL_MISSING', 'SIGNATURE_PROCESS_TIMEOUT',
    'SIGNATURE_PROCESS_FAILED', 'SIGNATURE_METADATA_INVALID', 'SIGNATURE_PROCESS_OS_ERROR',
    'NATIVE_DLL_SEARCH_RESET_FAILED', 'NATIVE_DLL_SEARCH_RESTORE_FAILED',
    'SIGNATURE_NATIVE_WINDOWS_REQUIRED', 'SIGNATURE_NATIVE_PROVIDER_UNAVAILABLE',
    'SIGNATURE_SIGNER_UNVERIFIED', 'SIGNATURE_DIGEST_MISMATCH', 'SIGNATURE_CERT_REVOKED',
    'SIGNATURE_REVOCATION_UNAVAILABLE', 'SIGNATURE_NATIVE_TRUST_UNVERIFIED', 'SIGNATURE_NATIVE_METADATA_INVALID',
    'BUNDLE_PROVENANCE_UNVERIFIED'})


@contextmanager
def native_system_dll_search():
    """Do not make native PS5 inherit PyInstaller's private DLL directory.

    PyInstaller's documented Windows external-process contract requires this
    reset. Restore the exact prior process DLL directory in finally; neither
    PATH nor machine/user settings are changed. Serialized for our native calls.
    """
    if sys.platform != 'win32' or not getattr(sys, 'frozen', False):
        yield
        return
    with NATIVE_PROCESS_LOCK:
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.GetDllDirectoryW.argtypes = [ctypes.c_uint32, ctypes.c_wchar_p]
        kernel.GetDllDirectoryW.restype = ctypes.c_uint32
        kernel.SetDllDirectoryW.argtypes = [ctypes.c_wchar_p]
        kernel.SetDllDirectoryW.restype = ctypes.c_int
        buffer = ctypes.create_unicode_buffer(32768)
        length = kernel.GetDllDirectoryW(len(buffer), buffer)
        if length >= len(buffer) or not kernel.SetDllDirectoryW(None):
            raise BundleError('NATIVE_DLL_SEARCH_RESET_FAILED')
        original = buffer.value if length else None
        try:
            yield
        finally:
            if not kernel.SetDllDirectoryW(original):
                raise BundleError('NATIVE_DLL_SEARCH_RESTORE_FAILED')


def native_system_run(*args, **kwargs):
    with native_system_dll_search():
        return subprocess.run(*args, **kwargs)


REQUIRED = {'agent_setup/probe_windows.ps1', 'agent-runtime/host/windows/launch.py',
            'requirements.lock', 'requirements-build.lock', 'python-runtime.json',
            'runtime/python314.dll', 'runtime/Python-LICENSE.txt', 'exe_entry.py',
            'agent_setup/engine.py', 'agent_setup/windows.py', 'agent_setup/tui.py',
            'agent_setup/credentials.py', 'agent_setup/packaging.py', 'agent_setup/exe_main.py',
            'agent_setup/read_only_acceptance.py', 'agent_setup/signature_wintrust.py'}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_bundle(root: Path) -> dict:
    """Validate a complete inventory without trusting path traversal/symlinks."""
    root = root.resolve(strict=True)
    manifest_path = root / 'bundle-manifest.json'
    if not manifest_path.is_file() or manifest_path.is_symlink():
        raise BundleError('BUNDLE_MANIFEST_MISSING')
    try:
        if manifest_path.stat().st_size > 2**20:
            raise BundleError('BUNDLE_MANIFEST_INVALID')
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        if (manifest.get('schema') != 1 or manifest.get('distribution') != 'UNSIGNED_TEST_ONLY'
            or not re.fullmatch(r'[a-f0-9]{40}', manifest.get('source_head', ''))
            or not re.fullmatch(r'3\.14\.\d+', manifest.get('python_version', ''))
            or manifest.get('architecture') != 'AMD64'
            or manifest.get('python_signature') != {'status': 'Valid', 'signer': 'Python Software Foundation'}):
            raise BundleError('BUNDLE_MANIFEST_INVALID')
        inventory = manifest['resources']
        if not isinstance(inventory, dict) or not REQUIRED.issubset(inventory):
            raise BundleError('BUNDLE_INVENTORY_INCOMPLETE')
        for name, expected in inventory.items():
            relative = PurePosixPath(name)
            if (relative.is_absolute() or '..' in relative.parts or '\\' in name or ':' in name
                or not re.fullmatch(r'[a-f0-9]{64}', expected)):
                raise BundleError('BUNDLE_RESOURCE_INVALID')
            path = root.joinpath(*relative.parts)
            if any(p.is_symlink() or (p.exists() and getattr(p.lstat(), 'st_file_attributes', 0) & 0x400)
                   for p in (path, *path.parents) if p == root or root in p.parents):
                raise BundleError('BUNDLE_RESOURCE_REPARSE')
            if not path.is_file() or not path.resolve().is_relative_to(root) or sha256(path) != expected:
                raise BundleError('BUNDLE_RESOURCE_HASH_MISMATCH')
        return manifest
    except (KeyError, TypeError, ValueError, OSError) as error:
        raise BundleError('BUNDLE_MANIFEST_INVALID') from error


def loaded_python_dll() -> Path:
    """Ask the native loader, not sys.executable or an on-disk lookalike."""
    if sys.platform != 'win32':
        raise BundleError('WINDOWS_LOADED_RUNTIME_REQUIRED')
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.GetModuleHandleW.argtypes = [ctypes.c_wchar_p]
    kernel.GetModuleHandleW.restype = ctypes.c_void_p
    kernel.GetModuleFileNameW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_uint32]
    kernel.GetModuleFileNameW.restype = ctypes.c_uint32
    module = kernel.GetModuleHandleW('python314.dll')
    if not module:
        raise BundleError('LOADED_RUNTIME_MODULE_UNKNOWN')
    buffer = ctypes.create_unicode_buffer(32768)
    length = kernel.GetModuleFileNameW(module, buffer, len(buffer))
    if not length or length >= len(buffer):
        raise BundleError('LOADED_RUNTIME_MODULE_UNKNOWN')
    return Path(buffer.value).resolve(strict=True)


def verified_bundle_root() -> Path:
    if not getattr(sys, 'frozen', False) or not hasattr(sys, '_MEIPASS'):
        raise BundleError('FROZEN_BUNDLE_REQUIRED')
    root = Path(sys._MEIPASS) / 'contract'
    validate_bundle(root)
    # PyInstaller actually loads this DLL from extraction root, not contract.
    # Both must match the authenticated original runtime bytes.
    actual = loaded_python_dll()
    if actual != (root.parent / 'python314.dll').resolve(strict=True):
        raise BundleError('LOADED_RUNTIME_MODULE_OUTSIDE_BUNDLE')
    if sha256(actual) != sha256(root / 'runtime/python314.dll'):
        raise BundleError('LOADED_RUNTIME_HASH_MISMATCH')
    return root


def psf_signature(path: Path) -> dict:
    if getattr(sys, 'frozen', False):
        from .signature_wintrust import psf_native_signature
        return psf_native_signature(path)
    from .windows import trusted_windows_powershell
    powershell = trusted_windows_powershell()
    if not powershell:
        return {'status': 'UnknownError', 'signer': 'UNVERIFIED', 'reason': 'SIGNATURE_NATIVE_POWERSHELL_MISSING'}
    # This is a public runtime file path, encoded as data into fixed source.
    # DEVNULL avoids PS5 ReadToEnd/EOF behavior inside the frozen process.
    encoded_path = base64.b64encode(str(path).encode('utf-8')).decode('ascii')
    script = r"""$ErrorActionPreference='Stop'; [Console]::OutputEncoding=[System.Text.UTF8Encoding]::new($false);
[Console]::WriteLine('{"phase":"STARTED"}'); [Console]::Out.Flush();
try { $env:PSModulePath=Join-Path $PSHOME 'Modules';
Import-Module (Join-Path $PSHOME 'Modules\Microsoft.PowerShell.Security\Microsoft.PowerShell.Security.psd1') -ErrorAction Stop;
[Console]::WriteLine('{"phase":"MODULE_LOADED"}'); [Console]::Out.Flush();
$path=[System.Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('__PUBLIC_RUNTIME_PATH__'));
[Console]::WriteLine('{"phase":"SIGNATURE_ENTER"}'); [Console]::Out.Flush();
$s=Get-AuthenticodeSignature -LiteralPath $path;
[Console]::WriteLine('{"phase":"SIGNATURE_RETURN"}'); [Console]::Out.Flush();
$psf=$s.SignerCertificate -and $s.SignerCertificate.Subject -match '(?:^|,\s*)(?:CN|O)\s*=\s*"?Python Software Foundation"?(?:,|$)';
@{status=[string]$s.Status;psf=[bool]$psf}|ConvertTo-Json -Compress
} catch { @{status='UnknownError';psf=$false}|ConvertTo-Json -Compress }"""
    script = script.replace('__PUBLIC_RUNTIME_PATH__', encoded_path)
    encoded_command = base64.b64encode(script.encode('utf-16-le')).decode('ascii')
    try:
        with native_system_dll_search():
            run = subprocess.run([powershell, '-NoLogo', '-NoProfile', '-NonInteractive', '-EncodedCommand', encoded_command],
                                 stdin=subprocess.DEVNULL, capture_output=True,
                                 encoding='utf-8', errors='replace', timeout=30)
        if run.returncode != 0 or len(run.stdout) > 4096:
            return {'status': 'UnknownError', 'signer': 'UNVERIFIED', 'reason': 'SIGNATURE_PROCESS_FAILED'}
        lines = run.stdout.strip().splitlines()
        if not lines:
            raise ValueError('SIGNATURE_METADATA_MISSING')
        result = json.loads(lines[-1])
        if not isinstance(result, dict):
            raise ValueError('SIGNATURE_METADATA_INVALID')
        status = result.get('status')
        if status not in {'Valid', 'NotSigned', 'HashMismatch', 'NotTrusted', 'UnknownError',
                          'NotSupportedFileFormat', 'Incompatible'}:
            status = 'UnknownError'
        return {'status': status,
                'signer': 'Python Software Foundation' if result.get('psf') is True else 'UNVERIFIED'}
    except subprocess.TimeoutExpired as error:
        return {'status': 'UnknownError', 'signer': 'UNVERIFIED', 'reason': 'SIGNATURE_PROCESS_TIMEOUT',
                'signature_phase': last_signature_phase(error.stdout)}
    except OSError:
        return {'status': 'UnknownError', 'signer': 'UNVERIFIED', 'reason': 'SIGNATURE_PROCESS_OS_ERROR'}
    except ValueError:
        return {'status': 'UnknownError', 'signer': 'UNVERIFIED', 'reason': 'SIGNATURE_METADATA_INVALID'}


def last_signature_phase(raw) -> str:
    if isinstance(raw, bytes):
        raw = raw.decode('utf-8', errors='replace')
    if not isinstance(raw, str) or len(raw) > 4096:
        return 'UNKNOWN'
    phase = 'UNKNOWN'
    for line in raw.splitlines():
        try:
            value = json.loads(line)
            if isinstance(value, dict) and value.get('phase') in SIGNATURE_PHASES:
                phase = value['phase']
        except (ValueError, TypeError):
            pass
    return phase


def bundle_provenance() -> dict:
    try:
        root = verified_bundle_root()
        manifest = validate_bundle(root)
        if manifest['python_version'] != platform.python_version() or sys.version_info.releaselevel != 'final':
            raise BundleError('BUNDLED_RUNTIME_VERSION_MISMATCH')
        signature = psf_signature(root / 'runtime/python314.dll')
        if signature != {'status': 'Valid', 'signer': 'Python Software Foundation'}:
            reason = signature.get('reason', 'BUNDLED_RUNTIME_PSF_SIGNATURE_UNVERIFIED')
            raise BundleError(reason if reason in PUBLIC_BUNDLE_CODES else 'BUNDLED_RUNTIME_PSF_SIGNATURE_UNVERIFIED',
                              signature_phase=signature.get('signature_phase'))
        return {'state': 'VERIFIED_CONTENT_UNSIGNED_TEST_ONLY', 'bundle_verified': True,
                'python_verified': True, 'source_head': manifest['source_head'],
                'python_version': manifest['python_version'], 'runtime_signature': signature,
                'runtime_verifier': 'NATIVE_WINVERIFYTRUST_CACHE_ONLY_WHOLECHAIN_NO_UI',
                'distribution': 'UNSIGNED_TEST_ONLY', 'publisher_trusted': False,
                'host_apply': 'DENIED', 'reason': 'REVIEWED_SIGNED_DISTRIBUTION_AND_HUMAN_GATE_REQUIRED'}
    except (BundleError, OSError) as error:
        reason = str(error) if isinstance(error, BundleError) and str(error) in PUBLIC_BUNDLE_CODES else 'BUNDLE_PROVENANCE_UNVERIFIED'
        proof = {'state': 'BLOCKED', 'bundle_verified': False, 'python_verified': False,
                 'publisher_trusted': False, 'host_apply': 'DENIED', 'reason': reason}
        if isinstance(error, BundleError) and error.signature_phase:
            proof['signature_phase'] = error.signature_phase
        return proof
