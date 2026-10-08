"""Publishing evidence cannot collapse synthetic stages into BOSS acceptance."""
import copy
from pathlib import Path
import runpy
import pytest


validate = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'scripts/smoke_exe.py'),
                         run_name='synthetic_exe_acceptance')['validate_acceptance_receipt']


def receipt():
    scenarios = ['fresh', 'legacy_v1', 'malformed_state', 'malformed_exchange',
                 'extra_state', 'extra_exchange', 'stale', 'collision', 'junction']
    return {'acceptance': {'BUNDLE_EXECUTION_PASS': True, 'SYNTHETIC_HOST_WIZARD_PASS': True,
                          'NATIVE_READ_ONLY_PLANNING_PASS': True, 'BOSS_CANARY': 'NOT_RETESTED',
                          'LAST_REPORTED_BOSS_CANARY': 'FAIL_EXISTING_ROOT_METADATA_INVALID'},
            'context_cases': [{'scenario': scenario, 'production_pipeline': 'WINDOWS_ADAPTER_PROBE_ENGINE_PROBE_PLAN',
                               'existing_files': 'UNCHANGED', 'context_source': 'OWNED_PUBLIC_FIXTURE',
                               'inventory_source': 'WINDOWS_POWERSHELL',
                               'runtime_capability': 'SYNTHETIC_WSLC_ONLY', 'host_apply': 'DENIED'}
                              for scenario in scenarios],
            'native_read_only_planning': {'status': 'PASS', 'meaning': 'READ_ONLY_PLAN_COMPUTED_NOT_RUNTIME_READY',
                                         'volume_metadata': 'PASS', 'runtime_gates': {'WSLC': 'BLOCKED'}},
            'native_metadata_scan': {'inventory_source': 'WINDOWS_POWERSHELL'},
            'forced_fallback_cases': [{'scenario': name, 'provider_fault': 'FORCED_PS_TIMEOUT',
                                     'inventory_source': 'WINDOWS_WIN32_FALLBACK', 'first_next': 'PASS',
                                     'existing_files': 'UNCHANGED', 'host_apply': 'DENIED',
                                     'runtime_capability': 'SYNTHETIC_WSLC_ONLY'} for name in ['fresh', 'legacy_v1']],
            'fallback_without_runtime_fixture': {'runtime_fixture': False, 'plan_status': 'BLOCKED',
                                                'wslc_state': 'UNKNOWN', 'inventory_source': 'WINDOWS_WIN32_FALLBACK'},
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
    value = receipt()
    value['native_metadata_scan']['inventory_source'] = 'UNVERIFIED'
    with pytest.raises(RuntimeError, match='INVENTORY_SOURCE_UNVERIFIED'):
        validate(value)
