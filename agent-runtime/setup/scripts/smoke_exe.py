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
from agent_setup.packaging import (PUBLIC_BUNDLE_CODES, PUBLIC_EXE_CODES, SIGNATURE_PHASES,
                                   ACCEPTANCE_STAGES, ACCEPTANCE_SCENARIOS, NATIVE_CHECKS)
from agent_setup.packaging import PUBLIC_PLAN_GATES


def validate_acceptance_receipt(receipt: dict) -> None:
    """Artifact publication cannot promote partial or empty evidence."""
    acceptance = receipt.get('acceptance', {})
    required = {'fresh', 'legacy_v1', 'malformed_state', 'malformed_exchange',
                'extra_state', 'extra_exchange', 'stale', 'collision', 'junction'}
    cases = receipt.get('context_cases', [])
    if (not isinstance(acceptance, dict)
        or any(acceptance.get(stage) is not True for stage in
               ['BUNDLE_EXECUTION_PASS', 'SYNTHETIC_HOST_WIZARD_PASS', 'NATIVE_READ_ONLY_PLANNING_PASS'])
        or acceptance.get('BOSS_CANARY') != 'NOT_RETESTED'
        or acceptance.get('LAST_REPORTED_BOSS_CANARY') != 'FAIL_EXISTING_ROOT_METADATA_INVALID'
        or not isinstance(cases, list) or len(cases) != len(required)
        or {case.get('scenario') for case in cases if isinstance(case, dict)} != required):
        raise RuntimeError('FROZEN_ACCEPTANCE_EVIDENCE_INCOMPLETE')
    for case in cases:
        if (case.get('production_pipeline') != 'WINDOWS_ADAPTER_PROBE_ENGINE_PROBE_PLAN'
            or case.get('existing_files') != 'UNCHANGED'
            or case.get('context_source') != 'OWNED_PUBLIC_FIXTURE'
            or case.get('runtime_capability') != 'SYNTHETIC_WSLC_ONLY'
            or case.get('host_apply') != 'DENIED'):
            raise RuntimeError('FROZEN_ACCEPTANCE_CONTEXT_BOUNDARY_INVALID')
    native = receipt.get('native_read_only_planning', {})
    if (native.get('status') != 'PASS' or native.get('meaning') != 'READ_ONLY_PLAN_COMPUTED_NOT_RUNTIME_READY'
        or native.get('volume_metadata') != 'PASS'):
        raise RuntimeError('FROZEN_NATIVE_PLANNING_EVIDENCE_INCOMPLETE')
    screens = receipt.get('screens', [])
    for scenario, result in [('fresh', 'PASS'), ('legacy_v1', 'PASS'), ('malformed_exchange', 'BLOCKED_OWNER_REVIEW')]:
        if not any(screen.get('scenario') == scenario and screen.get('size') == [80, 24]
                   and screen.get('first_next') == result for screen in screens):
            raise RuntimeError('FROZEN_EXISTING_CONTEXT_UI_EVIDENCE_INCOMPLETE')


def safe_failure(output: Path, exe: Path, mode: str, run) -> None:
    reason = 'FROZEN_CHILD_OUTPUT_UNVERIFIED'
    phase = None
    safe_stage = {}
    try:
        parsed = json.loads(run.stdout) if len(run.stdout) <= 100000 else {}
        if isinstance(parsed, dict) and parsed.get('reason') in (PUBLIC_BUNDLE_CODES | PUBLIC_EXE_CODES):
            reason = parsed['reason']
            if parsed.get('signature_phase') in SIGNATURE_PHASES:
                phase = parsed['signature_phase']
            for key, allowed in [('acceptance_stage', ACCEPTANCE_STAGES), ('acceptance_scenario', ACCEPTANCE_SCENARIOS)]:
                if parsed.get(key) in allowed:
                    safe_stage[key] = parsed[key]
            if isinstance(parsed.get('native_checks'), dict):
                safe_stage['native_checks'] = {key: value for key, value in parsed['native_checks'].items()
                                               if key in NATIVE_CHECKS and type(value) is bool}
            if isinstance(parsed.get('plan_gates'), dict):
                safe_stage['plan_gates'] = {key: value for key, value in parsed['plan_gates'].items()
                                           if key in PUBLIC_PLAN_GATES and type(value) is str and value in {'PASS', 'BLOCKED'}}
    except (ValueError, TypeError):
        pass
    diagnostic = {'status': 'BLOCKED', 'mode': mode, 'exit_code': run.returncode,
                  'reason': reason, 'raw_stdout_stderr': 'NOT_RETAINED',
                  'exe_sha256': hashlib.sha256(exe.read_bytes()).hexdigest(),
                  'host_apply': 'DENIED', 'paths_emitted': False, 'credentials_read': False}
    if phase:
        diagnostic['signature_phase'] = phase
    diagnostic.update(safe_stage)
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
                # The complete production metadata/context matrix performs
                # bounded real PS5 scans and signature checks for every case.
                # Individual native-process limits stay unchanged; only the
                # whole multi-case acceptance process gets a larger envelope.
                timeout = 600 if arguments[0] == '--self-test' else 180
                run = subprocess.run([str(exe), *arguments], cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                                     capture_output=True, encoding='utf-8', errors='replace', timeout=timeout)
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
            if arguments[0] == '--self-test':
                try:
                    validate_acceptance_receipt(parsed)
                except RuntimeError:
                    safe_failure(output, exe, arguments[0], run)
                    raise
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
