"""One-file end-user entry: preview only; fixed and sanitized diagnostics."""
from __future__ import annotations
import argparse
import asyncio
import json
from pathlib import Path
import sys
import tempfile
import shutil

from .engine import SetupEngine, SetupError
from .packaging import BundleError, bundle_provenance, verified_bundle_root, validate_bundle
from .windows import WindowsAdapter


def readonly_native_bundle_scan() -> dict:
    """Exercise the bundled native PS5 scanner; discard all path metadata.

    Call adapter.probe only, never engine.probe: existing HOST_AGENT contents,
    authentication files and native application databases remain unread.
    """
    adapter = WindowsAdapter(apply_authorized=False)
    metadata = adapter.probe()
    proof = metadata.get('runtime_provenance', {})
    if (adapter.can_apply or metadata.get('platform') != 'windows'
        or not isinstance(metadata.get('documents'), str) or not metadata['documents']
        or not isinstance(metadata.get('volumes'), list) or not metadata['volumes']
        or metadata.get('python_verified') is not True
        or proof.get('bundle_verified') is not True or proof.get('python_verified') is not True
        or proof.get('state') != 'VERIFIED_CONTENT_UNSIGNED_TEST_ONLY'):
        raise SetupError('FROZEN_NATIVE_RESOURCE_SCAN_FAILED')
    return {'platform': 'windows', 'volume_count': len(metadata['volumes']),
            'resource_scan': 'PASS', 'host_apply': 'DENIED',
            'context_contents_read': False, 'credentials_read': False, 'paths_emitted': False}


async def frozen_self_test(output: Path) -> dict:
    """Read-only native resource scan, then synthetic Textual/engine flow."""
    from .tui import SetupApp
    from textual.widgets import Button
    proof = bundle_provenance()
    if proof.get('bundle_verified') is not True or proof.get('python_verified') is not True:
        raise BundleError('BUNDLE_PROVENANCE_UNVERIFIED')
    native_scan = readonly_native_bundle_scan()
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='setup-exe-fixture-') as scratch:
        root = Path(scratch)
        document = root / 'Documents'
        document.mkdir()
        native = root / 'native-opencode-sentinel.txt'
        native.write_text('PUBLIC_SYNTHETIC_PRESERVE', encoding='utf-8')
        class SyntheticWindowsAdapter(WindowsAdapter):
            def probe(self):
                return {'platform': 'windows', 'python_version': proof['python_version'],
                        'python_verified': proof['python_verified'], 'runtime_provenance': proof,
                        'wsl_app_version': '3.0.1', 'wslc_capability': {'state': 'PASS'},
                        'documents': str(document), 'existing_roots': {}, 'active_workloads': [],
                        'volumes': [{'mount': Path(scratch).anchor, 'fs': 'NTFS',
                                     'free_bytes': 80 * 2**30, 'capacity_bytes': 200 * 2**30,
                                     'device_id': 'PUBLIC_SYNTHETIC_VOLUME', 'media_type': 'SSD', 'bus_type': 'NVMe'}]}
            def pull_image(self, *args):
                raise SetupError('SELF_TEST_HOST_EFFECT_DENIED')
            def start_runtime(self, *args):
                raise SetupError('SELF_TEST_HOST_EFFECT_DENIED')
        adapter = SyntheticWindowsAdapter(apply_authorized=False)
        engine = SetupEngine(adapter)
        negatives = []
        for name in ['WSLC_ABSENT', 'LOW_DISK']:
            metadata = engine.probe()
            if name == 'WSLC_ABSENT':
                metadata['wslc_capability'] = {'state': 'BLOCKED'}
            else:
                metadata['volumes'][0]['free_bytes'] = 1
            plan = engine.plan(metadata)
            if plan['status'] != 'BLOCKED':
                raise SetupError('SELF_TEST_PREFLIGHT_NOT_FAIL_CLOSED')
            negatives.append({'case': name, 'result': 'BLOCKED'})
        copied = root / 'corrupt-extraction'
        shutil.copytree(verified_bundle_root(), copied)
        (copied / 'agent_setup/probe_windows.ps1').write_text('PUBLIC_SYNTHETIC_TAMPER', encoding='utf-8')
        try:
            validate_bundle(copied)
        except BundleError:
            negatives.append({'case': 'CORRUPT_EXTRACTION', 'result': 'BLOCKED'})
        else:
            raise SetupError('SELF_TEST_CORRUPTION_NOT_FAIL_CLOSED')
        records = []
        for size in [(80, 24), (120, 40)]:
            app = SetupApp(engine, host_authorized=False)
            async with app.run_test(size=size) as pilot:
                await pilot.pause(0.3)
                if app.probe_data.get('python_verified') is not True:
                    raise SetupError('SELF_TEST_FIRST_SCREEN_NOT_VERIFIED')
                (output / f'actual-exe-check-{size[0]}x{size[1]}.svg').write_text(
                    app.export_screenshot(title='ACTUAL FROZEN EXE / SYNTHETIC HOST / COMPUTER CHECK'), encoding='utf-8')
                app.query_one('#next', Button).focus()
                await pilot.press('enter')
                await pilot.pause(0.5)
                if app.step != 1 or not app.plan_data.get('roots'):
                    raise SetupError('SELF_TEST_FIRST_NEXT_FAILED')
                if app.host_authorized or app.approved_fingerprint is not None:
                    raise SetupError('SELF_TEST_AUTHORITY_LEAK')
                (output / f'actual-exe-placement-{size[0]}x{size[1]}.svg').write_text(
                    app.export_screenshot(title='ACTUAL FROZEN EXE / SYNTHETIC HOST / FIRST NEXT PASS'), encoding='utf-8')
                records.append({'size': list(size), 'first_next': 'PASS', 'host_authorized': False})
        if native.read_text(encoding='utf-8') != 'PUBLIC_SYNTHETIC_PRESERVE' or (document / 'HOST_AGENT.md').exists():
            raise SetupError('SELF_TEST_PRESERVATION_FAILED')
    return {'status': 'PASS', 'execution': 'ACTUAL_FROZEN_EXE', 'metadata': 'SYNTHETIC_WINDOWS_ADAPTER',
            'screens': records, 'host_apply': 'DENIED', 'native_opencode': 'UNCHANGED_SYNTHETIC_SENTINEL',
            'credentials_read': False, 'network': 'NO_CREDENTIAL_OR_MODEL_CALLS',
            'provenance': proof, 'negative_cases': negatives,
            'native_metadata_scan': native_scan}


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
        raise BundleError('BUNDLE_PROVENANCE_UNVERIFIED')
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
    try:
        result = main(argv)
    except Exception as error:
        reason = str(error) if isinstance(error, (SetupError, BundleError)) else 'STARTUP_FAILED'
        print(json.dumps({'status': 'BLOCKED', 'reason': reason, 'raw_error': 'SUPPRESSED'}, ensure_ascii=False), flush=True)
        result = 2
    # Double-click owns the console. Retain both successful exit and errors;
    # noninteractive diagnostics/CI have arguments and must never hang.
    if not (sys.argv[1:] if argv is None else argv) and sys.stdin and sys.stdin.isatty():
        try:
            input('按 Enter 关闭窗口。 / Press Enter to close. ')
        except (EOFError, KeyboardInterrupt):
            pass
    return result
