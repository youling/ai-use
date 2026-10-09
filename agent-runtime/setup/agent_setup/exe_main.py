"""One-file end-user entry: preview only; fixed and sanitized diagnostics."""
from __future__ import annotations
import argparse
import asyncio
import json
from pathlib import Path
import sys
import tempfile
import shutil
import copy

from .engine import SetupEngine, SetupError
from .packaging import BundleError, bundle_provenance, verified_bundle_root, validate_bundle, PUBLIC_BUNDLE_CODES
from .windows import WindowsAdapter
from .packaging import PUBLIC_EXE_CODES, ACCEPTANCE_STAGES, ACCEPTANCE_SCENARIOS, INVENTORY_SOURCES

_CURRENT_STAGE = None
_CURRENT_SCENARIO = None


def acceptance_stage(stage, scenario=None):
    global _CURRENT_STAGE, _CURRENT_SCENARIO
    _CURRENT_STAGE = stage if stage in ACCEPTANCE_STAGES else None
    _CURRENT_SCENARIO = scenario if scenario in ACCEPTANCE_SCENARIOS else None


class ExeAcceptanceError(SetupError):
    def __init__(self, code, *, checks=None, plan_gates=None):
        super().__init__(code)
        self.checks = checks or {}
        self.plan_gates = plan_gates or {}


def readonly_native_bundle_scan() -> dict:
    """Exercise the bundled native PS5 scanner; discard all path metadata.

    Call adapter.probe only, never engine.probe: existing HOST_AGENT contents,
    authentication files and native application databases remain unread.
    """
    adapter = WindowsAdapter(apply_authorized=False)
    metadata = adapter.probe()
    proof = metadata.get('runtime_provenance', {})
    checks = {'platform_windows': metadata.get('platform') == 'windows',
              'mutation_disabled': not adapter.can_apply,
              'documents_metadata_present': isinstance(metadata.get('documents'), str) and bool(metadata['documents']),
              'volumes_metadata_present': isinstance(metadata.get('volumes'), list) and bool(metadata['volumes']),
              'python_verified': metadata.get('python_verified') is True,
              'bundle_verified': proof.get('bundle_verified') is True,
              'bundle_python_verified': proof.get('python_verified') is True,
              'bundle_state_verified': proof.get('state') == 'VERIFIED_CONTENT_UNSIGNED_TEST_ONLY'}
    if not all(checks.values()):
        raise ExeAcceptanceError('FROZEN_NATIVE_RESOURCE_SCAN_FAILED', checks=checks)
    return {'platform': 'windows', 'volume_count': len(metadata['volumes']),
            'resource_scan': 'PASS', 'host_apply': 'DENIED',
            'inventory_source': metadata.get('inventory_source') if metadata.get('inventory_source') in INVENTORY_SOURCES else 'UNVERIFIED',
            'context_contents_read': False, 'credentials_read': False, 'paths_emitted': False}


async def frozen_self_test(output: Path) -> dict:
    """Actual production probe/parser/planner on disposable public contexts.

    Native OS inventory, resource loading and Python provenance stay real.
    Wizard runtime capability is an explicitly labelled WSLC fixture; actual
    native WSLC gates are separately reported without a runtime READY claim.
    """
    from .tui import SetupApp
    from textual.widgets import Button
    from .read_only_acceptance import (SCENARIOS, owned_fixture_pipeline,
                                       assert_fixture_unchanged, native_read_only_planning)
    acceptance_stage('BUNDLE_PROVENANCE')
    proof = bundle_provenance()
    if proof.get('bundle_verified') is not True or proof.get('python_verified') is not True:
        raise BundleError('BUNDLE_PROVENANCE_UNVERIFIED')
    acceptance_stage('NATIVE_RESOURCE_SCAN')
    native_scan = readonly_native_bundle_scan()
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='setup-exe-fixture-') as scratch:
        root = Path(scratch)
        native_root = root / 'native-read-only'
        native_root.mkdir()
        acceptance_stage('NATIVE_READ_ONLY_PLANNING')
        native_plan = native_read_only_planning(native_root)
        if native_plan['status'] != 'PASS' or native_plan['volume_metadata'] != 'PASS':
            raise SetupError('SELF_TEST_NATIVE_PLANNING_FAILED')
        pipelines, cases, records = {}, [], []
        for scenario in SCENARIOS:
            scenario_root = root / scenario
            scenario_root.mkdir()
            acceptance_stage('CONTEXT_FIXTURE_BUILD', scenario)
            pipeline = owned_fixture_pipeline(scenario_root, scenario)
            pipelines[scenario] = pipeline
            if not isinstance(pipeline['adapter'], WindowsAdapter) or pipeline['adapter'].can_apply:
                raise SetupError('SELF_TEST_PRODUCTION_ADAPTER_OR_AUTHORITY_FAILED')
            if pipeline['native_calls'].count('OS_INVENTORY') < 1:
                raise SetupError('SELF_TEST_NATIVE_PIPELINE_NOT_EXERCISED')
            code, plan_status, plan_gates = None, 'BLOCKED', {}
            acceptance_stage('CONTEXT_PLAN', scenario)
            try:
                plan = pipeline['engine'].plan(pipeline['observation'], overrides=pipeline['overrides'])
                plan_status = plan['status']
                plan_gates = {gate['code']: gate['state'] for gate in plan['gates']}
            except SetupError as error:
                code = str(error)
            if code != pipeline['expected_code'] or plan_status != pipeline['expected_status']:
                raise ExeAcceptanceError('SELF_TEST_EXISTING_CONTEXT_CASE_FAILED', plan_gates=plan_gates,
                    checks={'case_plan_ready': plan_status == 'READY',
                            'storage_capacity_pass': plan_gates.get('STORAGE_CAPACITY') == 'PASS',
                            'root_placement_capacity_pass': all(state == 'PASS' for gate, state in plan_gates.items()
                                                               if gate.startswith('PLACEMENT_'))})
            acceptance_stage('CONTEXT_SNAPSHOT_CHECK', scenario)
            assert_fixture_unchanged(pipeline)
            diagnostic = pipeline['engine'].diagnose_root_plan(pipeline['observation'], overrides=pipeline['overrides'])
            cases.append({'scenario': scenario, 'plan_status': plan_status, 'code': code,
                          'exchange_schema': pipeline['exchange_schema'],
                          'metadata_errors': diagnostic.get('metadata_errors', []),
                          'production_pipeline': 'WINDOWS_ADAPTER_PROBE_ENGINE_PROBE_PLAN',
                          'existing_files': 'UNCHANGED', 'context_source': 'OWNED_PUBLIC_FIXTURE',
                          'inventory_source': pipeline['evidence']['native_metadata'],
                          'runtime_capability': 'SYNTHETIC_WSLC_ONLY', 'host_apply': 'DENIED'})
        bare_root = root / 'legacy-v1-directions-only'
        bare_root.mkdir()
        acceptance_stage('CONTEXT_FIXTURE_BUILD', 'legacy_v1')
        bare = owned_fixture_pipeline(bare_root, 'legacy_v1', annotated_exchange=False)
        bare_plan = bare['engine'].plan(bare['observation'], overrides=bare['overrides'])
        if set(bare_plan['exchange']) != {'in', 'out'} or bare_plan.get('exchange_classification'):
            raise SetupError('SELF_TEST_LEGACY_EXCHANGE_SCHEMA_FAILED')
        annotated_plan = pipelines['legacy_v1']['engine'].plan(pipelines['legacy_v1']['observation'])
        classification = {'owner': 'HOST_MANAGED', 'relocatable': False,
                          'reason': 'PUBLIC_SYNTHETIC_EXCHANGE_CLASSIFICATION'}
        if (set(annotated_plan['exchange']) != {'in', 'out'}
            or annotated_plan.get('exchange_classification') != classification):
            raise SetupError('SELF_TEST_LEGACY_EXCHANGE_SCHEMA_FAILED')
        bare_app = SetupApp(bare['engine'], host_authorized=False)
        acceptance_stage('TUI_PROBE', 'legacy_v1')
        async with bare_app.run_test(size=(80, 24)) as pilot:
            acceptance_stage('TUI_NEXT', 'legacy_v1')
            bare_app.query_one('#next', Button).focus()
            await pilot.press('enter')
            await pilot.pause(0.5)
            if bare_app.step != 1 or bare_app.host_authorized:
                raise SetupError('SELF_TEST_LEGACY_EXCHANGE_FIRST_NEXT_FAILED')
            (output / 'actual-exe-legacy-v1-directions-only-80x24.svg').write_text(
                bare_app.export_screenshot(title='NATIVE PIPELINE / OWNED BARE V1 EXCHANGE / WSLC FIXTURE / FIRST NEXT PASS'),
                encoding='utf-8')
        assert_fixture_unchanged(bare)
        exchange_schemas = [{'schema': 'DIRECTIONS_ONLY', 'first_next': 'PASS', 'metadata_authority': 'NONE'},
                            {'schema': 'ANNOTATED_V1', 'first_next': 'PASS', 'metadata_authority': 'NONE'}]
        fallback_cases = []
        for scenario in ['fresh', 'legacy_v1']:
            forced_root = root / ('forced-timeout-' + scenario)
            forced_root.mkdir()
            acceptance_stage('CONTEXT_FIXTURE_BUILD', scenario)
            forced = owned_fixture_pipeline(forced_root, scenario, force_ps_timeout=True)
            acceptance_stage('CONTEXT_PLAN', scenario)
            forced_plan = forced['engine'].plan(forced['observation'], overrides=forced['overrides'])
            if (forced['observation'].get('inventory_source') != 'WINDOWS_WIN32_FALLBACK'
                or forced['observation'].get('runtime_inventory_source') != 'OWNED_CAPABILITY_FIXTURE'
                or forced_plan['status'] != forced['expected_status']):
                raise ExeAcceptanceError('SELF_TEST_FORCED_NATIVE_FALLBACK_FAILED',
                    plan_gates={gate['code']: gate['state'] for gate in forced_plan['gates']})
            app = SetupApp(forced['engine'], host_authorized=False)
            app.overrides.update(forced['overrides'])
            acceptance_stage('TUI_PROBE', scenario)
            async with app.run_test(size=(80, 24)) as pilot:
                acceptance_stage('TUI_NEXT', scenario)
                app.query_one('#next', Button).focus()
                await pilot.press('enter')
                await pilot.pause(0.5)
                if app.step != 1:
                    raise SetupError('SELF_TEST_FORCED_NATIVE_FALLBACK_FIRST_NEXT_FAILED')
                (output / f'actual-exe-forced-ps-timeout-{scenario}-80x24.svg').write_text(
                    app.export_screenshot(title=f'FORCED PS TIMEOUT / ACTUAL WIN32 / OWNED {scenario} / WSLC FIXTURE'),
                    encoding='utf-8')
            assert_fixture_unchanged(forced)
            fallback_cases.append({'scenario': scenario, 'provider_fault': 'FORCED_PS_TIMEOUT',
                                   'inventory_source': 'WINDOWS_WIN32_FALLBACK',
                                   'runtime_capability': 'SYNTHETIC_WSLC_ONLY', 'first_next': 'PASS',
                                   'existing_files': 'UNCHANGED', 'host_apply': 'DENIED'})
        no_fixture_root = root / 'forced-timeout-without-capability-fixture'
        no_fixture_root.mkdir()
        no_fixture = owned_fixture_pipeline(no_fixture_root, 'fresh', synthetic_wslc=False, force_ps_timeout=True)
        no_fixture_plan = no_fixture['engine'].plan(no_fixture['observation'], overrides=no_fixture['overrides'])
        if (no_fixture_plan['status'] != 'BLOCKED'
            or no_fixture['observation']['wslc_capability']['state'] == 'PASS'):
            raise SetupError('SELF_TEST_NATIVE_FALLBACK_RUNTIME_GATE_BYPASS')
        assert_fixture_unchanged(no_fixture)
        fallback_runtime = {'provider_fault': 'FORCED_PS_TIMEOUT',
                            'inventory_source': no_fixture['observation']['inventory_source'],
                            'runtime_fixture': False, 'plan_status': 'BLOCKED',
                            'wslc_state': no_fixture['observation']['wslc_capability']['state']}
        engine = pipelines['fresh']['engine']
        negatives = []
        for name in ['WSLC_ABSENT', 'LOW_DISK']:
            acceptance_stage('PREFLIGHT_COUNTEREXAMPLE', 'fresh')
            metadata = copy.deepcopy(engine.probe())
            if name == 'WSLC_ABSENT':
                metadata['wslc_capability'] = {'state': 'BLOCKED'}
            else:
                for volume in metadata['volumes']:
                    volume['free_bytes'] = 1
            plan = engine.plan(metadata, overrides=pipelines['fresh']['overrides'])
            if plan['status'] != 'BLOCKED':
                raise SetupError('SELF_TEST_PREFLIGHT_NOT_FAIL_CLOSED')
            expected_gate = 'WSLC' if name == 'WSLC_ABSENT' else 'STORAGE_CAPACITY'
            if not any(gate['code'] == expected_gate and gate['state'] == 'BLOCKED' for gate in plan['gates']):
                raise SetupError('SELF_TEST_EXPECTED_PREFLIGHT_GATE_NOT_BLOCKED')
            negatives.append({'case': name, 'result': 'BLOCKED'})
        copied = root / 'corrupt-extraction'
        acceptance_stage('CORRUPTION_COUNTEREXAMPLE')
        shutil.copytree(verified_bundle_root(), copied)
        (copied / 'agent_setup/probe_windows.ps1').write_text('PUBLIC_SYNTHETIC_TAMPER', encoding='utf-8')
        try:
            validate_bundle(copied)
        except BundleError:
            negatives.append({'case': 'CORRUPT_EXTRACTION', 'result': 'BLOCKED'})
        else:
            raise SetupError('SELF_TEST_CORRUPTION_NOT_FAIL_CLOSED')
        for scenario in ['fresh', 'legacy_v1', 'malformed_exchange']:
            pipeline = pipelines[scenario]
            sizes = [(80, 24), (120, 40)] if scenario != 'malformed_exchange' else [(80, 24)]
            for size in sizes:
                app = SetupApp(pipeline['engine'], host_authorized=False)
                app.overrides.update(pipeline['overrides'])
                acceptance_stage('TUI_PROBE', scenario)
                async with app.run_test(size=size) as pilot:
                    await pilot.pause(0.3)
                    if app.probe_data.get('python_verified') is not True:
                        raise SetupError('SELF_TEST_FIRST_SCREEN_NOT_VERIFIED')
                    title = f'NATIVE PIPELINE / OWNED CONTEXT {scenario} / WSLC FIXTURE'
                    (output / f'actual-exe-{scenario}-check-{size[0]}x{size[1]}.svg').write_text(
                        app.export_screenshot(title=title), encoding='utf-8')
                    acceptance_stage('TUI_NEXT', scenario)
                    app.query_one('#next', Button).focus()
                    await pilot.press('enter')
                    await pilot.pause(0.5)
                    blocked = scenario == 'malformed_exchange'
                    if app.step != (0 if blocked else 1) or (not blocked and not app.plan_data.get('roots')):
                        raise SetupError('SELF_TEST_EXISTING_CONTEXT_FIRST_NEXT_FAILED')
                    if blocked and not all(text in app.status_text for text in
                                           ['EXISTING_ROOT_METADATA_INVALID', 'Exchange', 'PATH_TYPE', '只读目录诊断']):
                        raise SetupError('SELF_TEST_METADATA_OWNER_ACTION_NOT_VISIBLE')
                    if app.host_authorized or app.approved_fingerprint is not None:
                        raise SetupError('SELF_TEST_AUTHORITY_LEAK')
                    (output / f'actual-exe-{scenario}-next-{size[0]}x{size[1]}.svg').write_text(
                        app.export_screenshot(title=title + (' / BLOCKED OWNER REVIEW' if blocked else ' / FIRST NEXT PASS')),
                        encoding='utf-8')
                    records.append({'scenario': scenario, 'size': list(size),
                                    'first_next': 'BLOCKED_OWNER_REVIEW' if blocked else 'PASS',
                                    'context_source': 'OWNED_PUBLIC_FIXTURE', 'host_authorized': False})
                acceptance_stage('TUI_SNAPSHOT', scenario)
                assert_fixture_unchanged(pipeline)
        for pipeline in pipelines.values():
            assert_fixture_unchanged(pipeline)
    acceptance_stage('COMPLETE')
    return {'status': 'PASS', 'execution': 'ACTUAL_FROZEN_EXE', 'metadata': 'NATIVE_WINDOWS_WITH_OWNED_CONTEXT_FIXTURES',
            'acceptance': {'BUNDLE_EXECUTION_PASS': True, 'SYNTHETIC_HOST_WIZARD_PASS': True,
                           'NATIVE_READ_ONLY_PLANNING_PASS': True, 'BOSS_CANARY': 'NOT_RETESTED',
                           'LAST_REPORTED_BOSS_CANARY': 'FAIL_EXISTING_ROOT_METADATA_INVALID'},
            'screens': records, 'context_cases': cases, 'host_apply': 'DENIED', 'native_opencode': 'UNCHANGED_OWNED_FIXTURE_STATE',
            'forced_fallback_cases': fallback_cases, 'fallback_without_runtime_fixture': fallback_runtime,
            'exchange_schema_variants': exchange_schemas,
            'credentials_read': False, 'network': 'NO_CREDENTIAL_OR_MODEL_CALLS',
            'provenance': proof, 'negative_cases': negatives,
            'native_metadata_scan': native_scan, 'native_read_only_planning': native_plan}


def main(argv=None) -> int:
    if not (sys.argv[1:] if argv is None else argv):
        print('正在启动安全预览，核验内嵌运行时…', flush=True)
    parser = argparse.ArgumentParser(description='Agent Runtime 安全预览安装向导（未签名测试版本）')
    parser.add_argument('--check-only', '-CheckOnly', action='store_true')
    parser.add_argument('--version', action='store_true')
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--diagnose-root-plan', action='store_true')
    parser.add_argument('--launcher-dispatch', action='store_true')
    # Accepted solely to reject clearly, never as a authority switch.
    parser.add_argument('--host-authorized', action='store_true')
    args, remaining = parser.parse_known_args(argv)
    if args.host_authorized or args.launcher_dispatch:
        raise SetupError('UNSIGNED_DISTRIBUTION_HOST_APPLY_DENIED')
    if remaining:
        raise SetupError('UNKNOWN_ARGUMENT')
    proof = bundle_provenance()
    if not proof.get('bundle_verified') or not proof.get('python_verified'):
        reason = proof.get('reason', 'BUNDLE_PROVENANCE_UNVERIFIED')
        raise BundleError(reason if reason in PUBLIC_BUNDLE_CODES else 'BUNDLE_PROVENANCE_UNVERIFIED',
                          signature_phase=proof.get('signature_phase'))
    if args.version:
        print(json.dumps({'product': 'AgentRuntimeSetup', 'source_head': proof['source_head'],
                          'python': proof['python_version'], 'distribution': 'UNSIGNED_TEST_ONLY'}))
    elif args.check_only:
        verified_bundle_root()
        print(json.dumps({'status': 'PASS', 'provenance': proof, 'host_probe': False,
                          'host_apply': 'DENIED', 'credentials_read': False, 'resources': 'VERIFIED'}))
    elif args.self_test:
        if args.output_dir is None:
            raise SetupError('SELF_TEST_OUTPUT_REQUIRED')
        result = asyncio.run(frozen_self_test(args.output_dir))
        acceptance_stage('SELF_TEST_RECEIPT_WRITE')
        (args.output_dir / 'frozen-self-test.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(result))
    elif args.diagnose_root_plan:
        # Explicit local user invocation permits the existing read-only context
        # parser. Only finite role/source/relation categories leave this path;
        # no raw HOST_AGENT values, identities, credentials or paths are output.
        adapter = WindowsAdapter(apply_authorized=False)
        result = SetupEngine(adapter).diagnose_root_plan()
        print(json.dumps(result))
    else:
        print('核验完成，打开安装向导… 未签名测试版本，仅检查与规划，不安装、不读取密钥。', flush=True)
        from .tui import run_tui
        # WindowsAdapter content provenance validates the embedded PSF runtime;
        # publisher trust remains unsigned and every mutation is denied.
        run_tui(SetupEngine(WindowsAdapter(apply_authorized=False)), host_authorized=False)
    return 0


def guarded_main(argv=None) -> int:
    acceptance_stage(None)
    try:
        result = main(argv)
    except Exception as error:
        raw_code = str(error)
        reason = raw_code if raw_code in (PUBLIC_EXE_CODES | PUBLIC_BUNDLE_CODES) else 'STARTUP_FAILED'
        failure = {'status': 'BLOCKED', 'reason': reason, 'raw_error': 'SUPPRESSED'}
        if isinstance(error, BundleError) and error.signature_phase:
            failure['signature_phase'] = error.signature_phase
        if _CURRENT_STAGE in ACCEPTANCE_STAGES:
            failure['acceptance_stage'] = _CURRENT_STAGE
        if _CURRENT_SCENARIO in ACCEPTANCE_SCENARIOS:
            failure['acceptance_scenario'] = _CURRENT_SCENARIO
        if isinstance(error, ExeAcceptanceError):
            from .packaging import NATIVE_CHECKS, PUBLIC_PLAN_GATES
            failure['native_checks'] = {key: value for key, value in error.checks.items()
                                       if key in NATIVE_CHECKS and type(value) is bool}
            if error.plan_gates:
                failure['plan_gates'] = {key: value for key, value in error.plan_gates.items()
                                        if key in PUBLIC_PLAN_GATES and type(value) is str and value in {'PASS', 'BLOCKED'}}
        print(json.dumps(failure, ensure_ascii=False), flush=True)
        result = 2
    # Double-click owns the console. Retain both successful exit and errors;
    # noninteractive diagnostics/CI have arguments and must never hang.
    if not (sys.argv[1:] if argv is None else argv) and sys.stdin and sys.stdin.isatty():
        try:
            input('按 Enter 关闭窗口。 / Press Enter to close. ')
        except (EOFError, KeyboardInterrupt):
            pass
    return result
