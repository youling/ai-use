"""Publishing evidence cannot collapse synthetic stages into BOSS acceptance."""
import copy
from pathlib import Path
import runpy
import pytest
import json
from types import SimpleNamespace


validate = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'scripts/smoke_exe.py'),
                         run_name='synthetic_exe_acceptance')['validate_acceptance_receipt']


@pytest.mark.parametrize('stage', ['FOLDER_PICKER_SEAM', 'FOLDER_PICKER_PARENT', 'FOLDER_PICKER_AUTO', 'FOLDER_PICKER_CUSTOM', 'FOLDER_PICKER_CANCEL'])
def test_timeout_failure_retains_only_latest_public_stage(tmp_path, stage):
    functions = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'scripts/smoke_exe.py'))
    output = tmp_path / 'owned-evidence'
    (output / 'screens').mkdir(parents=True)
    (output / 'screens/acceptance-progress.json').write_text(json.dumps({
        'acceptance_stage': stage, 'acceptance_scenario': 'legacy_v1',
        'raw_error': 'PUBLIC_SYNTHETIC_TOKEN', 'path': 'PUBLIC_SYNTHETIC_PRIVATE_PATH'}))
    exe = tmp_path / 'public-synthetic-exe'
    exe.write_bytes(b'PUBLIC_SYNTHETIC_TEST_BYTES')
    functions['safe_failure'](output, exe, '--self-test', SimpleNamespace(
        returncode=124, stdout=json.dumps({'reason': 'ACTUAL_FROZEN_EXE_PROCESS_TIMEOUT'})))
    content = (output / 'failure-diagnostic.json').read_text()
    diagnostic = json.loads(content)
    assert diagnostic['reason'] == 'ACTUAL_FROZEN_EXE_PROCESS_TIMEOUT'
    assert diagnostic['acceptance_stage'] == stage
    assert diagnostic['acceptance_scenario'] == 'legacy_v1'
    assert 'PUBLIC_SYNTHETIC_TOKEN' not in content and 'PUBLIC_SYNTHETIC_PRIVATE_PATH' not in content
    assert diagnostic['host_apply'] == 'DENIED' and diagnostic['credentials_read'] is False


def receipt():
    scenarios = ['fresh', 'legacy_v1', 'malformed_state', 'malformed_exchange',
                 'extra_state', 'extra_exchange', 'stale', 'collision', 'junction']
    return {'acceptance': {'BUNDLE_EXECUTION_PASS': True, 'SYNTHETIC_HOST_WIZARD_PASS': True,
                          'NATIVE_READ_ONLY_PLANNING_PASS': True, 'BOSS_CANARY': 'NOT_RETESTED',
                          'LAST_REPORTED_BOSS_CANARY': 'FAIL_EXISTING_ROOT_METADATA_INVALID'},
            'context_cases': [{'scenario': scenario, 'production_pipeline': 'WINDOWS_ADAPTER_PROBE_ENGINE_PROBE_PLAN',
                               'exchange_schema': 'ANNOTATED_V1' if scenario == 'legacy_v1' else 'DIRECTIONS_ONLY',
                               'existing_files': 'UNCHANGED', 'context_source': 'OWNED_PUBLIC_FIXTURE',
                               'inventory_source': 'WINDOWS_POWERSHELL',
                               'runtime_capability': 'SYNTHETIC_WSLC_ONLY', 'host_apply': 'DENIED'}
                              for scenario in scenarios],
            'native_read_only_planning': {'status': 'PASS', 'meaning': 'READ_ONLY_PLAN_COMPUTED_NOT_RUNTIME_READY',
                                         'volume_metadata': 'PASS', 'runtime_gates': {'WSLC': 'BLOCKED'}},
            'native_metadata_scan': {'inventory_source': 'WINDOWS_POWERSHELL'},
            'exchange_schema_variants': [{'schema': 'DIRECTIONS_ONLY', 'first_next': 'PASS', 'metadata_authority': 'NONE'},
                                         {'schema': 'ANNOTATED_V1', 'first_next': 'PASS', 'metadata_authority': 'NONE'}],
            'forced_fallback_cases': [{'scenario': name, 'provider_fault': 'FORCED_PS_TIMEOUT',
                                     'inventory_source': 'WINDOWS_WIN32_FALLBACK', 'first_next': 'PASS',
                                     'existing_files': 'UNCHANGED', 'host_apply': 'DENIED',
                                     'runtime_capability': 'SYNTHETIC_WSLC_ONLY'} for name in ['fresh', 'legacy_v1']],
            'fallback_without_runtime_fixture': {'runtime_fixture': False, 'plan_status': 'BLOCKED',
                                                'wslc_state': 'UNKNOWN', 'inventory_source': 'WINDOWS_WIN32_FALLBACK'},
            'native_folder_picker': {'status': 'PASS', 'evidence': 'NATIVE_COM_CONFIGURE_ONLY',
                                     'ui_show': 'NOT_EXERCISED', 'history_cleanup': 'UNVERIFIED'},
            'folder_picker_cases': [{'scenario': name, 'chooser_boundary': 'INJECTED_OWNED_DIRECTORY_OR_CANCEL',
                                    'native_dialog': 'NOT_EXERCISED_BY_SEAM', 'keyboard_browse': 'PASS',
                                    'cancel': 'UNCHANGED', 'scope_escape': 'BLOCKED',
                                    'parent_scope': 'FRESH_DESCENDANT_NOT_CREATED', 'auto_custom': 'PASS', 'custom_new_children': 'PASS',
                                    'prior_consent': 'INVALIDATED_ON_SELECTION', 'existing_files': 'UNCHANGED',
                                    'host_apply': 'DENIED'} for name in ['fresh', 'legacy_v1']],
            'screens': [{'scenario': name, 'size': [80, 24], 'first_next': state} for name, state in
                        [('fresh', 'PASS'), ('legacy_v1', 'PASS'), ('malformed_exchange', 'BLOCKED_OWNER_REVIEW')]]}


def test_native_wscl_blocked_is_honest_read_only_planning_not_runtime_success():
    validate(receipt())


@pytest.mark.parametrize('missing', ['legacy_v1', 'malformed_exchange', 'stale', 'junction'])
def test_missing_production_existing_context_counterexample_refuses_artifact_acceptance(missing):
    value = receipt()
    value['context_cases'] = [case for case in value['context_cases'] if case['scenario'] != missing]
    with pytest.raises(RuntimeError, match='EVIDENCE_INCOMPLETE'):
        validate(value)


def test_duplicate_case_cannot_substitute_missing_context_case():
    value = receipt()
    value['context_cases'][-1] = copy.deepcopy(value['context_cases'][0])
    with pytest.raises(RuntimeError, match='EVIDENCE_INCOMPLETE'):
        validate(value)


def test_synthetic_host_never_promotes_boss_canary_to_pass():
    value = receipt()
    value['acceptance']['BOSS_CANARY'] = 'PASS'
    with pytest.raises(RuntimeError, match='EVIDENCE_INCOMPLETE'):
        validate(value)


def test_empty_adapter_probe_override_evidence_is_not_production_pipeline():
    value = receipt()
    value['context_cases'][0]['production_pipeline'] = 'SYNTHETIC_ADAPTER_PROBE_OVERRIDE'
    with pytest.raises(RuntimeError, match='BOUNDARY_INVALID'):
        validate(value)


def test_existing_context_changes_or_runtime_claims_refuse_artifact_acceptance():
    value = receipt()
    value['context_cases'][1]['existing_files'] = 'CHANGED'
    with pytest.raises(RuntimeError, match='BOUNDARY_INVALID'):
        validate(value)


def test_empty_or_fresh_only_screens_do_not_prove_existing_context_next():
    value = receipt()
    value['screens'] = value['screens'][:1]
    with pytest.raises(RuntimeError, match='UI_EVIDENCE_INCOMPLETE'):
        validate(value)


def test_truthful_actual_win32_inventory_source_can_satisfy_same_planning_evidence():
    value = receipt()
    value['native_metadata_scan']['inventory_source'] = 'WINDOWS_WIN32_FALLBACK'
    for case in value['context_cases']:
        case['inventory_source'] = 'WINDOWS_WIN32_FALLBACK'
    validate(value)


def test_unknown_or_invented_inventory_source_cannot_publish_verified_artifact():
    value = receipt()
    value['context_cases'][0]['inventory_source'] = 'SYNTHETIC_NVME_PASS'
    with pytest.raises(RuntimeError, match='BOUNDARY_INVALID'):
        validate(value)


def test_real_volume_fallback_cannot_promote_unknown_runtime_capability_to_pass():
    value = receipt()
    value['fallback_without_runtime_fixture']['wslc_state'] = 'PASS'
    with pytest.raises(RuntimeError, match='RUNTIME_GATE_UNVERIFIED'):
        validate(value)


def test_directions_only_legacy_case_cannot_claim_annotated_context_coverage():
    value = receipt()
    value['context_cases'][1]['exchange_schema'] = 'DIRECTIONS_ONLY'
    with pytest.raises(RuntimeError, match='ANNOTATED_LEGACY_EXCHANGE'):
        validate(value)


def test_classification_annotation_never_grants_metadata_authority():
    value = receipt()
    value['exchange_schema_variants'][1]['metadata_authority'] = 'HOST_APPLY_AUTHORIZED'
    with pytest.raises(RuntimeError, match='SCHEMA_EVIDENCE_INCOMPLETE'):
        validate(value)


def test_injected_chooser_cannot_claim_actual_native_dialog_show():
    value = receipt()
    value['folder_picker_cases'][0]['native_dialog'] = 'ACTUAL_NATIVE_SHOW_PASS'
    with pytest.raises(RuntimeError, match='BOUNDARY_INVALID'):
        validate(value)


def test_native_configure_only_does_not_claim_visible_show_or_verified_history():
    value = receipt()
    validate(value)  # UNVERIFIED history is reported, never promoted to absence.
    value['native_folder_picker']['ui_show'] = 'PASS'
    with pytest.raises(RuntimeError, match='CONFIGURE_UNVERIFIED'):
        validate(value)


def test_empty_picker_case_evidence_cannot_publish_artifact():
    value = receipt()
    value['folder_picker_cases'] = []
    with pytest.raises(RuntimeError, match='SEAM_EVIDENCE_INCOMPLETE'):
        validate(value)
    value = receipt()
    value['native_metadata_scan']['inventory_source'] = 'UNVERIFIED'
    with pytest.raises(RuntimeError, match='INVENTORY_SOURCE_UNVERIFIED'):
        validate(value)
