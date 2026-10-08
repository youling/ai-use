"""Run the actual EXE under a deliberately empty prerequisite PATH.

All writes are constrained to an explicit new test sandbox. Existing Host,
profiles, Git, Python, pwsh7 and credential stores are never inspected.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import sys
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent_setup.packaging import PUBLIC_BUNDLE_CODES


def safe_failure(output: Path, exe: Path, mode: str, run) -> None:
    reason = 'FROZEN_CHILD_OUTPUT_UNVERIFIED'
    try:
        parsed = json.loads(run.stdout) if len(run.stdout) <= 100000 else {}
        if isinstance(parsed, dict) and parsed.get('reason') in PUBLIC_BUNDLE_CODES:
            reason = parsed['reason']
    except (ValueError, TypeError):
        pass
    diagnostic = {'status': 'BLOCKED', 'mode': mode, 'exit_code': run.returncode,
                  'reason': reason, 'raw_stdout_stderr': 'NOT_RETAINED',
                  'exe_sha256': hashlib.sha256(exe.read_bytes()).hexdigest(),
                  'host_apply': 'DENIED', 'paths_emitted': False, 'credentials_read': False}
    (output / 'failure-diagnostic.json').write_text(json.dumps(diagnostic, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(diagnostic), flush=True)


def smoke(exe: Path, output: Path):
    output.mkdir(parents=True, exist_ok=False)
    receipts = []
    with tempfile.TemporaryDirectory(prefix='setup-exe-smoke-') as scratch:
        sandbox = Path(scratch)
        cwd = sandbox / '中文 任意目录'
        cwd.mkdir()
        temporary = sandbox / 'bounded-temp'
        temporary.mkdir()
        empty_path = sandbox / 'no-python-no-pwsh-no-git'
        empty_path.mkdir()
        profile = sandbox / 'synthetic-profile'
        profile.mkdir()
        # Do not even read arbitrary environment values (they may be secrets).
        # Only public OS locations/architecture reach the synthetic child.
        env = {name: os.environ[name] for name in
               ['SystemRoot', 'WINDIR', 'COMSPEC', 'SYSTEMDRIVE', 'OS', 'PROCESSOR_ARCHITECTURE']
               if name in os.environ}
        env.update({'PATH': str(empty_path), 'TEMP': str(temporary), 'TMP': str(temporary),
                    'USERPROFILE': str(profile), 'HOMEDRIVE': profile.drive,
                    'HOMEPATH': str(profile)[len(profile.drive):],
                    'APPDATA': str(profile / 'AppData/Roaming'), 'LOCALAPPDATA': str(profile / 'AppData/Local'),
                    'PYTHONPATH': '', 'PYTHONHOME': '', 'PYTHONNOUSERSITE': '1'})
        before = sorted(p.name for p in temporary.iterdir())
        for arguments, expected in [(['--version'], 0), (['--check-only'], 0),
                                    (['--host-authorized', '--check-only'], 2),
                                    (['--launcher-dispatch', '--local-only'], 2),
                                    (['--self-test', '--output-dir', str(output / 'screens')], 0)]:
            try:
                run = subprocess.run([str(exe), *arguments], cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                                     capture_output=True, encoding='utf-8', errors='replace', timeout=180)
            except subprocess.TimeoutExpired:
                safe_failure(output, exe, arguments[0], SimpleNamespace(returncode=124, stdout=''))
                raise RuntimeError('ACTUAL_FROZEN_EXE_PROCESS_TIMEOUT') from None
            if run.returncode != expected:
                # Do not leak arbitrary stderr/tracebacks from third-party code.
                safe_failure(output, exe, arguments[0], run)
                raise RuntimeError('ACTUAL_FROZEN_EXE_RUN_FAILED:' + arguments[0])
            try:
                parsed = json.loads(run.stdout.strip())
                if not isinstance(parsed, dict):
                    raise ValueError('METADATA_OBJECT_REQUIRED')
            except ValueError:
                safe_failure(output, exe, arguments[0], run)
                raise RuntimeError('ACTUAL_FROZEN_EXE_OUTPUT_INVALID') from None
            if len(run.stdout) > 100000 or any(value in run.stdout for value in ['github_pat_', 'ghp_', '-----BEGIN PRIVATE KEY']):
                raise RuntimeError('UNSAFE_FROZEN_OUTPUT')
            receipts.append({'mode': arguments[0], 'exit_code': run.returncode, 'result': parsed})
            if sorted(p.name for p in temporary.iterdir()) != before:
                raise RuntimeError('ONEFILE_EXTRACTION_NOT_CLEANED')
        # Rerun is a read-only startup again, never repair/mutation implicitly.
        rerun = subprocess.run([str(exe), '--check-only'], cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                               capture_output=True, encoding='utf-8', errors='replace', timeout=90)
        if rerun.returncode != 0 or sorted(p.name for p in temporary.iterdir()) != before:
            raise RuntimeError('FROZEN_RERUN_FAILED')
    result = {'status': 'PASS', 'actual_exe_sha256': hashlib.sha256(exe.read_bytes()).hexdigest(),
              'prerequisites_on_path': [], 'cwd': 'ARBITRARY_UNICODE_SYNTHETIC_DIRECTORY',
              'temp': 'BOUNDED_EXTRACTION_CLEANED', 'host_apply': 'DENIED', 'credentials_read': False,
              'rerun': 'PASS', 'runs': receipts}
    (output / 'actual-exe-run-receipt.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': 'PASS', 'actual_exe_sha256': result['actual_exe_sha256'], 'runs': len(receipts)}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exe', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    smoke(args.exe.resolve(strict=True), args.output.resolve())
