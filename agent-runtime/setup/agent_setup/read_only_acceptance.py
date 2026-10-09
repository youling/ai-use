"""Disposable acceptance fixtures using the production Windows probe/parser.

Native OS inventory and Python provenance execute unchanged. Only unavailable
WSLC metadata is synthetic; no runtime mutation or credential custody is used.
This module exposes no command-line or environment Host-root override.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace
import yaml

from .engine import SetupEngine
from .windows import WindowsAdapter, trusted_windows_powershell

SCENARIOS = ('fresh','legacy_v1','malformed_state','malformed_exchange',
             'extra_state','extra_exchange','stale','collision','junction')


def owned_fixture_pipeline(root: Path, scenario: str = 'fresh', *, synthetic_wslc: bool = True, force_ps_timeout: bool = False,
                           annotated_exchange: bool = True) -> dict:
    if scenario not in SCENARIOS:
        raise ValueError('ACCEPTANCE_SCENARIO_INVALID')
    root = Path(root).resolve(strict=True)
    documents = root / 'OneDrive - Public Synthetic' / 'Documents'
    documents.mkdir(parents=True)
    folders = {name: root / name for name in ('workspace','config','cache','temp','state','exchange-in','exchange-out')}
    for name,path in folders.items():
        if scenario!='fresh' or name in {'state','exchange-in','exchange-out'}:
            path.mkdir()
    state_canary = folders['state'] / 'native-state-canary.txt'
    state_canary.write_text('PUBLIC_SYNTHETIC_NATIVE_STATE_PRESERVED',encoding='utf-8')
    exchange_canary=folders['exchange-in']/'exchange-canary.txt'
    exchange_canary.write_text('PUBLIC_SYNTHETIC_EXCHANGE_PRESERVED',encoding='utf-8')
    paths = {name:{'path':str(folders[name]),'owner':'HOST_OWNER','relocatable':False}
             for name in ('workspace','config','cache','temp','state')}
    paths['exchange'] = {'in':str(folders['exchange-in']),'out':str(folders['exchange-out'])}
    if scenario == 'legacy_v1' and annotated_exchange:
        # Public shape replay only, never copied Host paths/identity/reason.
        # A classification declaration is not an owner receipt or permission.
        paths['exchange'].update(owner='HOST_MANAGED', relocatable=False,
                                 reason='PUBLIC_SYNTHETIC_EXCHANGE_CLASSIFICATION')
    context = {'host_agent_version':'1.0.0','paths':paths}
    target = documents / 'HOST_AGENT.md'
    if scenario == 'malformed_state':
        paths['state'] = 'PUBLIC_INVALID_TYPE'
    elif scenario == 'malformed_exchange':
        paths['exchange']['out'] = False
    elif scenario == 'extra_state':
        paths['state']['unexpected_root'] = str(root / 'unexpected')
    elif scenario == 'extra_exchange':
        paths['exchange']['unexpected_root'] = str(root / 'unexpected')
    elif scenario == 'stale':
        context['host_agent_version'] = '0.0.0'
    elif scenario == 'collision':
        paths['cache']['path'] = paths['config']['path']
    elif scenario == 'junction':
        junction = root / 'synthetic-junction'
        ps=trusted_windows_powershell()
        if not ps:raise RuntimeError('ACCEPTANCE_NATIVE_PS5_UNAVAILABLE')
        cmd=Path(ps).parents[2]/'cmd.exe'
        made = subprocess.run([str(cmd),'/d','/c','mklink','/J',str(junction),str(folders['config'])],
                              capture_output=True,encoding='utf-8',errors='replace',timeout=10)
        if made.returncode:
            raise RuntimeError('ACCEPTANCE_JUNCTION_UNAVAILABLE')
        paths['config']['path'] = str(junction)
    if scenario != 'fresh':
        target.write_text('# Public synthetic context\n```yaml\n'+yaml.safe_dump(context)+'```\n',encoding='utf-8')
    watched = [state_canary,exchange_canary] + ([target] if target.exists() else [])
    snapshot = {str(path):hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    powershell = trusted_windows_powershell()
    if not powershell:
        raise RuntimeError('ACCEPTANCE_NATIVE_PS5_UNAVAILABLE')
    # Frozen bundles must reset their injected DLL lookup before native children.
    from .packaging import native_system_run
    native_calls = []
    def runner(argv, **kwargs):
        actual = list(argv)
        actual[0] = powershell
        native_calls.append('OS_INVENTORY' if '-File' in actual else 'PYTHON_SIGNATURE')
        if force_ps_timeout and '-File' in actual:
            raise subprocess.TimeoutExpired('OWNED_SCANNER_TIMEOUT_FIXTURE',25)
        result = native_system_run(actual, **kwargs)
        if '-File' in actual and result.returncode == 0:
            raw = json.loads(result.stdout)
            if not isinstance(raw,dict):raise RuntimeError('ACCEPTANCE_NATIVE_INVENTORY_INVALID')
            return SimpleNamespace(returncode=0,stdout=json.dumps(raw))
        return result
    runtime_resolver=(lambda:{'wsl_version_text':'WSL version: 3.0.1.0','wslc_state':'PASS','wslc_active_count':0}) if synthetic_wslc else None
    adapter = WindowsAdapter(runner=runner, known_folder_resolver=lambda:str(documents),runtime_capability_resolver=runtime_resolver)
    adapter.can_apply = False
    adapter.apply_authorized = False
    engine = SetupEngine(adapter)
    observation = engine.probe()
    overrides = {name:str(folders[name]) for name in ('workspace','config','cache','temp')} if scenario in {'fresh','stale'} else {}
    codes={'malformed_state':'EXISTING_ROOT_METADATA_INVALID','malformed_exchange':'EXISTING_ROOT_METADATA_INVALID',
           'extra_state':'EXISTING_ROOT_METADATA_INVALID','extra_exchange':'EXISTING_ROOT_METADATA_INVALID',
           'stale':'EXISTING_ROOT_METADATA_INVALID','collision':'ROOT_OVERLAP','junction':'EXISTING_ROOT_METADATA_INVALID'}
    return {'engine':engine,'adapter':adapter,'observation':observation,'overrides':overrides,
            'snapshot':snapshot,'documents':documents,'root':root,'native_calls':native_calls,
            'scenario':scenario,'expected_status':'READY' if scenario=='fresh' else 'BLOCKED',
            'exchange_schema':'ANNOTATED_V1' if scenario=='legacy_v1' and annotated_exchange else 'DIRECTIONS_ONLY',
            'expected_code':codes.get(scenario),
            'evidence':{'native_metadata':observation.get('inventory_source','UNVERIFIED'),'wslc_capability':'SYNTHETIC_ONLY' if synthetic_wslc else 'NATIVE_OBSERVED',
                        'context_source':'OWNED_PUBLIC_FIXTURE','host_apply':'DENIED'}}


def assert_fixture_unchanged(pipeline: dict) -> None:
    for name, expected in pipeline['snapshot'].items():
        if hashlib.sha256(Path(name).read_bytes()).hexdigest()!=expected:
            raise RuntimeError('ACCEPTANCE_EXISTING_FILE_CHANGED')
    if (pipeline['root']/'config'/'.agent-runtime-setup').exists():
        raise RuntimeError('ACCEPTANCE_UNEXPECTED_INSTALLER_WRITE')
    if not pipeline['snapshot'].get(str(pipeline['documents']/'HOST_AGENT.md')) and (pipeline['documents']/'HOST_AGENT.md').exists():
        raise RuntimeError('ACCEPTANCE_UNEXPECTED_CONTEXT_WRITE')


def native_read_only_planning(root: Path) -> dict:
    pipeline=owned_fixture_pipeline(root,synthetic_wslc=False)
    plan=pipeline['engine'].plan(pipeline['observation'],overrides=pipeline['overrides'])
    assert_fixture_unchanged(pipeline)
    return {'status':'PASS','meaning':'READ_ONLY_PLAN_COMPUTED_NOT_RUNTIME_READY',
            'plan_status':plan['status'],'volume_metadata':'PASS' if pipeline['observation'].get('volumes') else 'NOT_VERIFIED',
            'runtime_gates':{gate['code']:gate['state'] for gate in plan['gates'] if gate['code'] in {'WSL_APP_3','WSLC','PYTHON_314'}},
            'evidence':pipeline['evidence']}
