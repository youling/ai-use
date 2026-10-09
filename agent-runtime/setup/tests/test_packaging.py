"""Synthetic corruption and authority counterexamples, no Host secrets."""
import json
from pathlib import Path
import sys
import platform
from types import SimpleNamespace
import subprocess
import runpy
import asyncio
import os
import pytest

from agent_setup import packaging
from agent_setup.engine import SetupError
from agent_setup import exe_main


def contract(tmp_path):
    root = tmp_path / 'contract'
    root.mkdir()
    resources = {}
    for name in packaging.REQUIRED:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('PUBLIC_SYNTHETIC_RESOURCE', encoding='utf-8')
        resources[name] = packaging.sha256(path)
    manifest = {'schema': 1, 'distribution': 'UNSIGNED_TEST_ONLY', 'source_head': 'a' * 40,
                'python_version': platform.python_version(), 'architecture': 'AMD64', 'resources': resources,
                'python_signature': {'status': 'Valid', 'signer': 'Python Software Foundation'}}
    (root / 'bundle-manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
    return root, manifest


def write_manifest(root, manifest):
    (root / 'bundle-manifest.json').write_text(json.dumps(manifest), encoding='utf-8')


@pytest.mark.parametrize('name', sorted(packaging.REQUIRED))
def test_every_required_resource_corruption_fails_closed(tmp_path, name):
    root, _ = contract(tmp_path)
    (root / name).write_text('TAMPERED', encoding='utf-8')
    with pytest.raises(packaging.BundleError, match='BUNDLE_RESOURCE_HASH_MISMATCH'):
        packaging.validate_bundle(root)


@pytest.mark.parametrize('name', sorted(packaging.REQUIRED))
def test_required_missing_resource_fails_closed(tmp_path, name):
    root, _ = contract(tmp_path)
    (root / name).unlink()
    with pytest.raises(packaging.BundleError, match='BUNDLE_RESOURCE_HASH_MISMATCH'):
        packaging.validate_bundle(root)


@pytest.mark.parametrize('value', ['../../evil.py', '/evil.py', 'C:/evil.py', 'a\\evil.py'])
def test_manifest_path_escape_rejected(tmp_path, value):
    root, manifest = contract(tmp_path)
    manifest['resources'][value] = 'a' * 64
    write_manifest(root, manifest)
    with pytest.raises(packaging.BundleError, match='BUNDLE_RESOURCE_INVALID'):
        packaging.validate_bundle(root)


def test_manifest_claiming_trusted_release_cannot_create_authority(tmp_path):
    root, manifest = contract(tmp_path)
    manifest['distribution'] = 'SIGNED_TRUSTED_RELEASE'
    write_manifest(root, manifest)
    with pytest.raises(packaging.BundleError, match='BUNDLE_MANIFEST_INVALID'):
        packaging.validate_bundle(root)


def test_missing_inventory_entry_fails_closed(tmp_path):
    root, manifest = contract(tmp_path)
    manifest['resources'].pop('requirements.lock')
    write_manifest(root, manifest)
    with pytest.raises(packaging.BundleError, match='BUNDLE_INVENTORY_INCOMPLETE'):
        packaging.validate_bundle(root)


def test_loaded_python_dll_must_match_verified_original(tmp_path, monkeypatch):
    root, _ = contract(tmp_path)
    monkeypatch.setattr(sys, 'frozen', True, raising=False)
    monkeypatch.setattr(sys, '_MEIPASS', str(tmp_path), raising=False)
    (tmp_path / 'python314.dll').write_text('TAMPERED', encoding='utf-8')
    monkeypatch.setattr(packaging, 'loaded_python_dll', lambda: tmp_path / 'python314.dll')
    with pytest.raises(packaging.BundleError, match='LOADED_RUNTIME_HASH_MISMATCH'):
        packaging.verified_bundle_root()


def test_matching_disk_dll_does_not_verify_a_different_loaded_runtime(tmp_path, monkeypatch):
    root, _ = contract(tmp_path)
    monkeypatch.setattr(sys, 'frozen', True, raising=False)
    monkeypatch.setattr(sys, '_MEIPASS', str(tmp_path), raising=False)
    (tmp_path / 'python314.dll').write_text('PUBLIC_SYNTHETIC_RESOURCE', encoding='utf-8')
    other = tmp_path / 'outside-loaded.dll'
    other.write_text('PUBLIC_SYNTHETIC_RESOURCE', encoding='utf-8')
    monkeypatch.setattr(packaging, 'loaded_python_dll', lambda: other)
    with pytest.raises(packaging.BundleError, match='LOADED_RUNTIME_MODULE_OUTSIDE_BUNDLE'):
        packaging.verified_bundle_root()


def test_runtime_signature_failure_does_not_grant_python_or_host(tmp_path, monkeypatch):
    root, _ = contract(tmp_path)
    monkeypatch.setattr(packaging, 'verified_bundle_root', lambda: root)
    monkeypatch.setattr(packaging, 'psf_signature', lambda path: {'status': 'NotSigned', 'signer': 'UNVERIFIED'})
    proof = packaging.bundle_provenance()
    assert proof['state'] == 'BLOCKED'
    assert proof['python_verified'] is False and proof['host_apply'] == 'DENIED'


def test_verified_runtime_content_is_distinct_from_publisher_and_host_authority(tmp_path, monkeypatch):
    root, _ = contract(tmp_path)
    monkeypatch.setattr(packaging, 'verified_bundle_root', lambda: root)
    monkeypatch.setattr(packaging, 'psf_signature', lambda path: {'status': 'Valid', 'signer': 'Python Software Foundation'})
    proof = packaging.bundle_provenance()
    assert proof['python_verified'] and proof['bundle_verified']
    assert proof['publisher_trusted'] is False and proof['host_apply'] == 'DENIED'
    assert proof['state'] == 'VERIFIED_CONTENT_UNSIGNED_TEST_ONLY'


def test_manifest_cannot_claim_a_different_loaded_python_version(tmp_path,monkeypatch):
    root,manifest=contract(tmp_path)
    manifest['python_version']='3.14.999'
    write_manifest(root,manifest)
    monkeypatch.setattr(packaging,'verified_bundle_root',lambda:root)
    monkeypatch.setattr(packaging,'psf_signature',lambda path:{'status':'Valid','signer':'Python Software Foundation'})
    proof=packaging.bundle_provenance()
    assert proof['state']=='BLOCKED' and proof['python_verified'] is False


@pytest.mark.parametrize('args', [['--host-authorized'], ['--launcher-dispatch', '--local-only']])
def test_unsigned_exe_rejects_every_host_dispatch_before_provenance_or_resource_access(monkeypatch, args):
    monkeypatch.setattr(exe_main, 'bundle_provenance', lambda: pytest.fail('must reject before access'))
    with pytest.raises(SetupError, match='UNSIGNED_DISTRIBUTION_HOST_APPLY_DENIED'):
        exe_main.main(args)


def test_frozen_marker_alone_never_grants_content_trust(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, 'frozen', True, raising=False)
    monkeypatch.setattr(sys, '_MEIPASS', str(tmp_path), raising=False)
    proof = packaging.bundle_provenance()
    assert proof['state'] == 'BLOCKED' and proof['python_verified'] is False


def test_startup_error_is_fixed_category_and_does_not_dump_trace(monkeypatch, capsys):
    def fail(argv):
        raise ValueError('PRIVATE_EXTERNAL_DETAIL_NEVER_PRINT')
    monkeypatch.setattr(exe_main, 'main', fail)
    assert exe_main.guarded_main(['--check-only']) == 2
    output = capsys.readouterr().out
    assert 'STARTUP_FAILED' in output
    assert 'PRIVATE_EXTERNAL_DETAIL' not in output and 'Traceback' not in output


@pytest.mark.parametrize('receipt', ['[]', 'null', 'false', '"Valid"', '{"status":"Valid","psf":"true"}', '{}'])
def test_malformed_signature_receipts_never_verify_runtime(monkeypatch, receipt):
    from agent_setup import windows
    monkeypatch.setattr(windows, 'trusted_windows_powershell', lambda: 'PUBLIC_SYNTHETIC_NATIVE_PS')
    monkeypatch.setattr(packaging.subprocess, 'run', lambda *a, **kw: SimpleNamespace(returncode=0, stdout=receipt))
    signature = packaging.psf_signature(Path('public-synthetic-python314.dll'))
    assert signature != {'status': 'Valid', 'signer': 'Python Software Foundation'}


def test_double_click_shows_progress_before_slow_provenance_check(monkeypatch, capsys):
    def check():
        assert '核验内嵌运行时' in capsys.readouterr().out
        return {'bundle_verified': False, 'python_verified': False}
    monkeypatch.setattr(exe_main, 'bundle_provenance', check)
    with pytest.raises(packaging.BundleError, match='BUNDLE_PROVENANCE_UNVERIFIED'):
        exe_main.main([])


def test_explicit_root_diagnostics_reuse_engine_safe_context_diagnosis(monkeypatch, capsys):
    expected = {'status': 'BLOCKED', 'code': 'ROOT_OVERLAP', 'conflicts':
                [{'roles': ['config', 'cache'], 'relation': 'SAME_DIRECTORY',
                  'sources': ['EXISTING_CONTEXT', 'EXISTING_CONTEXT']}], 'host_apply': 'NOT_AUTHORIZED'}
    class Engine:
        def __init__(self, adapter):
            assert adapter == 'SYNTHETIC_ADAPTER'
        def diagnose_root_plan(self):
            return expected
    monkeypatch.setattr(exe_main, 'bundle_provenance', lambda: {'bundle_verified': True, 'python_verified': True})
    monkeypatch.setattr(exe_main, 'WindowsAdapter', lambda **kw: 'SYNTHETIC_ADAPTER')
    monkeypatch.setattr(exe_main, 'SetupEngine', Engine)
    assert exe_main.main(['--diagnose-root-plan']) == 0
    assert json.loads(capsys.readouterr().out) == expected


def native_scan_fixture():
    return {'platform': 'windows', 'documents': 'C:/PUBLIC_SYNTHETIC_PATH_NOT_EMITTED',
            'volumes': [{'mount': 'C:/', 'fs': 'NTFS'}], 'python_verified': True,
            'runtime_provenance': {'state': 'VERIFIED_CONTENT_UNSIGNED_TEST_ONLY',
                                   'bundle_verified': True, 'python_verified': True},
            'existing_roots': {'host_agent': True}}


def test_native_resource_scan_emits_only_finite_metadata_without_engine_context_read(monkeypatch):
    class Adapter:
        can_apply = False
        def __init__(self, **kw):
            assert kw == {'apply_authorized': False}
        def probe(self):
            return native_scan_fixture()
    monkeypatch.setattr(exe_main, 'WindowsAdapter', Adapter)
    monkeypatch.setattr(exe_main, 'SetupEngine', lambda *a: pytest.fail('must not read context'))
    receipt = exe_main.readonly_native_bundle_scan()
    assert receipt['resource_scan'] == 'PASS' and receipt['volume_count'] == 1
    assert 'PUBLIC_SYNTHETIC_PATH_NOT_EMITTED' not in json.dumps(receipt)
    assert receipt['context_contents_read'] is False and receipt['credentials_read'] is False


@pytest.mark.parametrize('missing', ['documents', 'volumes', 'python_verified', 'runtime_provenance'])
def test_native_scanner_missing_proof_is_fail_closed(monkeypatch, missing):
    fixture = native_scan_fixture()
    fixture.pop(missing)
    class Adapter:
        can_apply = False
        def __init__(self, **kw):
            pass
        def probe(self):
            return fixture
    monkeypatch.setattr(exe_main, 'WindowsAdapter', Adapter)
    with pytest.raises(SetupError, match='FROZEN_NATIVE_RESOURCE_SCAN_FAILED'):
        exe_main.readonly_native_bundle_scan()


def test_native_child_dll_directory_is_reset_then_restored_even_on_failure(monkeypatch):
    calls = []
    def get_directory(length, buffer):
        buffer.value = 'PUBLIC_SYNTHETIC_BUNDLE_DIRECTORY'
        return len(buffer.value)
    def set_directory(value):
        calls.append(value)
        return 1
    kernel = SimpleNamespace(GetDllDirectoryW=get_directory, SetDllDirectoryW=set_directory)
    monkeypatch.setattr(packaging.sys, 'platform', 'win32')
    monkeypatch.setattr(packaging.sys, 'frozen', True, raising=False)
    monkeypatch.setattr(packaging.ctypes, 'WinDLL', lambda *a, **kw: kernel, raising=False)
    with pytest.raises(RuntimeError, match='SYNTHETIC_CHILD_FAILURE'):
        with packaging.native_system_dll_search():
            assert calls == [None]
            raise RuntimeError('SYNTHETIC_CHILD_FAILURE')
    assert calls == [None, 'PUBLIC_SYNTHETIC_BUNDLE_DIRECTORY']


def test_signature_timeout_is_fixed_category_without_child_paths_or_raw_errors(monkeypatch):
    from agent_setup import windows
    monkeypatch.setattr(windows, 'trusted_windows_powershell', lambda: 'PUBLIC_SYNTHETIC_NATIVE_PS')
    def timeout(*a, **kw):
        raise subprocess.TimeoutExpired('PRIVATE_PROCESS_ARGUMENTS_NOT_LOGGED', 30,
                                        output='PRIVATE_RAW_OUTPUT_NOT_LOGGED')
    monkeypatch.setattr(packaging.subprocess, 'run', timeout)
    signature = packaging.psf_signature(Path('PUBLIC_SYNTHETIC_RUNTIME'))
    assert signature['reason'] == 'SIGNATURE_PROCESS_TIMEOUT'
    assert 'PRIVATE' not in json.dumps(signature)


def test_signature_timeout_phase_is_finite_and_never_echoes_child_text(monkeypatch):
    from agent_setup import windows
    monkeypatch.setattr(windows, 'trusted_windows_powershell', lambda: 'PUBLIC_SYNTHETIC_NATIVE_PS')
    def timeout(*a, **kw):
        assert kw['stdin'] == subprocess.DEVNULL and 'input' not in kw
        assert '-EncodedCommand' in a[0] and '-Command' not in a[0]
        raise subprocess.TimeoutExpired('not-printed', 30,
            output=b'{"phase":"STARTED"}\n{"phase":"SIGNATURE_ENTER"}\nPRIVATE_EXTERNAL_TEXT\n')
    monkeypatch.setattr(packaging.subprocess, 'run', timeout)
    signature = packaging.psf_signature(Path('PUBLIC_SYNTHETIC_RUNTIME'))
    assert signature['signature_phase'] == 'SIGNATURE_ENTER'
    assert 'PRIVATE_EXTERNAL_TEXT' not in json.dumps(signature)


@pytest.mark.parametrize('raw', [None, '', 'PRIVATE_EXTERNAL_TEXT', '{"phase":"PRIVATE_EXTERNAL_VALUE"}', 'x'*4097])
def test_unknown_signature_phase_is_not_echoed(raw):
    assert packaging.last_signature_phase(raw) == 'UNKNOWN'


def test_bundle_retains_only_finite_failure_cause(monkeypatch, tmp_path):
    root, _ = contract(tmp_path)
    monkeypatch.setattr(packaging, 'verified_bundle_root', lambda: root)
    monkeypatch.setattr(packaging, 'psf_signature', lambda path:
                        {'status': 'UnknownError', 'signer': 'UNVERIFIED', 'reason': 'SIGNATURE_PROCESS_TIMEOUT'})
    proof = packaging.bundle_provenance()
    assert proof['reason'] == 'SIGNATURE_PROCESS_TIMEOUT' and not proof['python_verified']
    def private_failure():
        raise packaging.BundleError('PRIVATE_EXTERNAL_VALUE_NOT_LOGGED')
    monkeypatch.setattr(packaging, 'verified_bundle_root', private_failure)
    proof = packaging.bundle_provenance()
    assert proof['reason'] == 'BUNDLE_PROVENANCE_UNVERIFIED'
    assert 'PRIVATE' not in json.dumps(proof)


def test_exe_reports_fixed_provenance_timeout_instead_of_generic_reason(monkeypatch, capsys):
    monkeypatch.setattr(exe_main, 'bundle_provenance', lambda:
                        {'bundle_verified': False, 'python_verified': False, 'reason': 'SIGNATURE_PROCESS_TIMEOUT'})
    assert exe_main.guarded_main(['--version']) == 2
    assert json.loads(capsys.readouterr().out)['reason'] == 'SIGNATURE_PROCESS_TIMEOUT'


def test_smoke_failure_artifact_rejects_arbitrary_child_output(tmp_path, capsys):
    script = Path(__file__).resolve().parents[1] / 'scripts/smoke_exe.py'
    safe_failure = runpy.run_path(str(script), run_name='synthetic_smoke_test')['safe_failure']
    exe = tmp_path / 'synthetic.exe'
    exe.write_text('PUBLIC_SYNTHETIC_BINARY', encoding='utf-8')
    run = SimpleNamespace(returncode=2, stdout=json.dumps({'reason': 'PRIVATE_EXTERNAL_DETAIL_NOT_LOGGED'}))
    safe_failure(tmp_path, exe, '--version', run)
    artifact = (tmp_path / 'failure-diagnostic.json').read_text(encoding='utf-8')
    assert 'PRIVATE_EXTERNAL_DETAIL' not in artifact
    assert 'FROZEN_CHILD_OUTPUT_UNVERIFIED' in artifact and 'NOT_RETAINED' in artifact
    assert 'PRIVATE_EXTERNAL_DETAIL' not in capsys.readouterr().out


def test_selftest_fixed_native_failure_retains_finite_stage_and_boolean_checks(monkeypatch, capsys):
    def fail(argv):
        exe_main.acceptance_stage('NATIVE_RESOURCE_SCAN')
        raise exe_main.ExeAcceptanceError('FROZEN_NATIVE_RESOURCE_SCAN_FAILED', checks=
            {'volumes_metadata_present': False, 'documents_metadata_present': True,
             'PRIVATE_EXTERNAL_FIELD': 'PRIVATE_EXTERNAL_VALUE', 'python_verified': 'unsafe-scalar'})
    monkeypatch.setattr(exe_main, 'main', fail)
    assert exe_main.guarded_main(['--self-test']) == 2
    output = capsys.readouterr().out
    result = json.loads(output)
    assert result['reason'] == 'FROZEN_NATIVE_RESOURCE_SCAN_FAILED'
    assert result['acceptance_stage'] == 'NATIVE_RESOURCE_SCAN'
    assert result['native_checks'] == {'volumes_metadata_present': False, 'documents_metadata_present': True}
    assert 'PRIVATE_EXTERNAL' not in output


def test_smoke_keeps_registered_setup_reason_and_rejects_arbitrary_stage_scenario(tmp_path, capsys):
    script = Path(__file__).resolve().parents[1] / 'scripts/smoke_exe.py'
    safe_failure = runpy.run_path(str(script), run_name='synthetic_smoke_test')['safe_failure']
    exe = tmp_path / 'synthetic.exe'
    exe.write_text('PUBLIC_SYNTHETIC_BINARY', encoding='utf-8')
    payload = {'reason': 'SELF_TEST_EXISTING_CONTEXT_CASE_FAILED',
               'acceptance_stage': 'CONTEXT_PLAN', 'acceptance_scenario': 'legacy_v1',
               'native_checks': {'volumes_metadata_present': False, 'private_path': 'PRIVATE_VALUE'}}
    safe_failure(tmp_path, exe, '--self-test', SimpleNamespace(returncode=2, stdout=json.dumps(payload)))
    artifact = json.loads((tmp_path / 'failure-diagnostic.json').read_text())
    assert artifact['reason'] == payload['reason'] and artifact['acceptance_scenario'] == 'legacy_v1'
    assert artifact['acceptance_stage'] == 'CONTEXT_PLAN' and 'PRIVATE_VALUE' not in json.dumps(artifact)
    payload.update(acceptance_stage='PRIVATE_VALUE', acceptance_scenario='PRIVATE_VALUE')
    safe_failure(tmp_path, exe, '--self-test', SimpleNamespace(returncode=2, stdout=json.dumps(payload)))
    assert 'PRIVATE_VALUE' not in (tmp_path / 'failure-diagnostic.json').read_text()


@pytest.mark.skipif(os.name != 'nt', reason='Actual native Windows public fixture pipeline')
def test_frozen_picker_seam_uses_production_pipeline_with_owned_directories(tmp_path):
    from agent_setup.read_only_acceptance import owned_fixture_pipeline
    pipelines = {}
    for name in ['fresh', 'legacy_v1']:
        root = tmp_path / name
        root.mkdir()
        pipelines[name] = owned_fixture_pipeline(root, name)
    output = tmp_path / 'public-ui-evidence'
    output.mkdir()
    records = asyncio.run(exe_main.frozen_folder_picker_seams(tmp_path, output, pipelines))
    assert {record['scenario'] for record in records} == {'fresh', 'legacy_v1'}
    assert all(record['cancel'] == 'UNCHANGED' and record['scope_escape'] == 'BLOCKED' for record in records)
    assert all(record['native_dialog'] == 'NOT_EXERCISED_BY_SEAM' and record['host_apply'] == 'DENIED' for record in records)
    assert len(list(output.glob('*.svg'))) == 4
