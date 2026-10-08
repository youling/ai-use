"""Build an unsigned Windows AMD64 preview from an exact, clean source head.

Build dependencies must already be installed with requirements-build.lock and
--require-hashes. This script never installs Python or changes the real Host.
"""
from __future__ import annotations
import argparse
import hashlib
from importlib import metadata
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys

SETUP = Path(__file__).resolve().parents[1]
REPO = SETUP.parents[1]
sys.path.insert(0, str(SETUP))
from agent_setup.packaging import psf_signature, sha256


def git(*args):
    return subprocess.check_output(['git', '-C', str(REPO), *args], encoding='utf-8').strip()


def build(output: Path, work: Path, *, allow_dirty=False):
    if sys.platform != 'win32' or platform.machine().upper() not in {'AMD64', 'X86_64'}:
        raise RuntimeError('WINDOWS_AMD64_NATIVE_BUILD_REQUIRED')
    if sys.version_info[:2] != (3, 14) or sys.version_info.releaselevel != 'final':
        raise RuntimeError('FINAL_PYTHON_314_REQUIRED')
    head = git('rev-parse', 'HEAD')
    dirty = bool(git('status', '--porcelain', '--untracked-files=all'))
    if dirty and not allow_dirty:
        raise RuntimeError('CLEAN_EXACT_SOURCE_REQUIRED')
    if metadata.version('pyinstaller') != '6.22.3':
        raise RuntimeError('LOCKED_PYINSTALLER_REQUIRED')
    python = Path(sys.base_prefix) / 'python.exe'
    dll = Path(sys.base_prefix) / 'python314.dll'
    expected = {'status': 'Valid', 'signer': 'Python Software Foundation'}
    if psf_signature(python) != expected or psf_signature(dll) != expected:
        raise RuntimeError('BUILD_PSF_RUNTIME_SIGNATURE_REQUIRED')
    # Build paths must be new task-owned paths, never delete arbitrary trees.
    output.mkdir(parents=True, exist_ok=False)
    work.mkdir(parents=True, exist_ok=False)
    contract = work / 'contract'
    contract.mkdir()
    resources = {}
    def include(source: Path, relative: str):
        destination = contract / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        resources[relative] = sha256(destination)
    for path in sorted((SETUP / 'agent_setup').glob('*')):
        if path.suffix in {'.py', '.ps1'}:
            include(path, 'agent_setup/' + path.name)
    include(REPO / 'agent-runtime/host/windows/launch.py', 'agent-runtime/host/windows/launch.py')
    for name in ['requirements.lock', 'requirements-build.lock', 'python-runtime.json', 'exe_entry.py']:
        include(SETUP / name, name)
    include(dll, 'runtime/python314.dll')
    license_file = Path(sys.base_prefix) / 'LICENSE.txt'
    if not license_file.is_file():
        raise RuntimeError('PYTHON_LICENSE_REQUIRED')
    include(license_file, 'runtime/Python-LICENSE.txt')
    dependencies = []
    for dist in sorted(metadata.distributions(), key=lambda d: d.metadata['Name'].lower()):
        name, version = dist.metadata['Name'], dist.version
        dependencies.append({'name': name, 'version': version})
        for path in dist.files or []:
            # Include official wheel license files. No pip/user config/store.
            if any(part.lower().startswith(('license', 'copying', 'notice')) for part in path.parts):
                source = Path(dist.locate_file(path))
                if source.is_file():
                    include(source, 'licenses/' + name + '/' + str(path).replace('\\', '/'))
    source_files = {}
    tracked = git('ls-files').splitlines()
    for name in tracked:
        if name.startswith(('agent-runtime/setup/', 'agent-runtime/host/windows/', '.github/workflows/agent-setup')):
            source_files[name] = sha256(REPO / name)
    manifest = {'schema': 1, 'product': 'AgentRuntimeSetup', 'source_head': head,
                'source_clean': not dirty, 'distribution': 'UNSIGNED_TEST_ONLY',
                'python_version': platform.python_version(), 'architecture': 'AMD64',
                'python_signature': expected, 'runtime_sha256': sha256(dll),
                'python_executable_sha256': sha256(python), 'resources': resources,
                'source_files': source_files, 'dependencies': dependencies,
                'permissions': 'USER_AS_INVOKER_NO_ELEVATION', 'host_apply': 'DENIED',
                'build_tool': 'PyInstaller 6.22.3', 'upx': False}
    (contract / 'bundle-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    command = [sys.executable, '-m', 'PyInstaller', '--onefile', '--console', '--noupx',
               '--name', 'AgentRuntimeSetup', '--distpath', str(output), '--workpath', str(work / 'pyinstaller'),
               '--specpath', str(work), '--paths', str(SETUP), '--add-data', str(contract) + ':contract',
               '--collect-all', 'textual', '--collect-all', 'rich', '--collect-all', 'yaml',
               '--collect-all', 'cryptography', '--copy-metadata', 'textual', str(SETUP / 'exe_entry.py')]
    subprocess.run(command, check=True)
    exe = output / 'AgentRuntimeSetup.exe'
    artifact_signature = psf_signature(exe)
    if artifact_signature['status'] != 'NotSigned':
        raise RuntimeError('UNSIGNED_TEST_ARTIFACT_SIGNATURE_STATE_UNEXPECTED')
    receipt = dict(manifest)
    receipt.update({'exe_sha256': sha256(exe), 'exe_bytes': exe.stat().st_size,
                    'code_signing': 'UNSIGNED_TEST_ONLY', 'artifact_authenticode': artifact_signature,
                    'os': platform.platform(),
                    'build_manifest_sha256': sha256(contract / 'bundle-manifest.json')})
    (output / 'build-provenance.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    (output / 'SHA256SUMS.txt').write_text(f"{receipt['exe_sha256']}  AgentRuntimeSetup.exe\n", encoding='ascii')
    shutil.copyfile(contract / 'bundle-manifest.json', output / 'bundle-manifest.json')
    print(json.dumps({'exe_sha256': receipt['exe_sha256'], 'exe_bytes': receipt['exe_bytes'],
                      'source_head': head, 'code_signing': 'UNSIGNED_TEST_ONLY'}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--work', required=True, type=Path)
    parser.add_argument('--allow-dirty-test-build', action='store_true')
    args = parser.parse_args()
    build(args.output.resolve(), args.work.resolve(), allow_dirty=args.allow_dirty_test_build)
