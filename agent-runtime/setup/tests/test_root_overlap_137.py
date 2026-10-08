"""Public synthetic conflict replay; never inspect real HOST_AGENT or credentials."""
import asyncio
import copy
import json
import os
from pathlib import Path
import shutil
import pytest
from textual.widgets import Button, Static
from agent_setup.engine import SetupEngine, FixtureAdapter, SetupError, safe_path
from agent_setup.tui import SetupApp
import yaml

GIB=1024**3

def machine(tmp_path,native=False):
    documents=tmp_path/'OneDrive - Public Synthetic'/'Documents';documents.mkdir(parents=True)
    mount=str(Path('C:/')) if native else str(tmp_path)
    capacity,_,free=shutil.disk_usage('C:/') if native else (256*GIB,128*GIB,128*GIB)
    data={'platform':'windows','python_version':'3.14.8','python_verified':True,'wsl_app_version':'3.0.1',
        'wslc_capability':{'state':'PASS'},'documents':str(documents),'documents_onedrive':True,'observed_at':'2026-10-09T00:00:00Z',
        'volumes':[{'mount':mount,'device_id':'public-synthetic-nvme','fs':'NTFS','media_type':'SSD','bus_type':'NVMe',
                    'capacity_bytes':capacity,'free_bytes':free}], 'active_workloads':[],'existing_roots':{}}
    if native and tmp_path.anchor.casefold()!='c:\\':
        data['volumes'].append({'mount':tmp_path.anchor,'device_id':'public-documents-volume','fs':'NTFS',
            'media_type':'HDD','bus_type':'SATA','capacity_bytes':256*GIB,'free_bytes':16*GIB})
    if native:
        class ReadOnlyInventory:
            can_apply=False
            def probe(self):return copy.deepcopy(data)
        adapter=ReadOnlyInventory()
    else:adapter=FixtureAdapter(data,tmp_path)
    return SetupEngine(adapter),data

@pytest.mark.parametrize('relation',['SAME_DIRECTORY','CONTAINS'])
def test_existing_conflict_preserved_diagnostic_only_roles(tmp_path,relation):
    engine,data=machine(tmp_path)
    existing=tmp_path/'preserved';existing.mkdir();(existing/'native-state.db').write_text('unique-public-fixture')
    config=existing if relation=='SAME_DIRECTORY' else existing/'config'
    data['existing_roots']={'workspace':{'path':str(existing),'exists':True},'config':{'path':str(config),'exists':True}}
    before=copy.deepcopy(data)
    with pytest.raises(SetupError,match='ROOT_OVERLAP') as caught:engine.plan(data)
    diagnostic=engine.diagnose_root_plan(data)
    assert diagnostic['conflicts']==caught.value.conflicts
    conflict=diagnostic['conflicts'][0]
    assert conflict['roles']==['workspace','config'] and conflict['sources']==['EXISTING_CONTEXT']*2
    assert conflict['relation']==relation and str(tmp_path) not in json.dumps(diagnostic)
    assert data==before and (existing/'native-state.db').read_text()=='unique-public-fixture'
    proposal=engine.propose_isolated_roots(data)
    assert data==before and not Path(proposal['isolated_scope']).exists()
    plan=engine.plan(data,overrides={'isolated_scope':proposal['isolated_scope']})
    assert plan['status']=='READY' and len(plan['placement_rows'])==6
    assert plan['preserved_existing_roles']==['workspace','config'] and plan['placement']=='NO_MOVE'
    assert all(Path(plan['roots'][n]['path']).is_relative_to(proposal['isolated_scope']) for n in ('workspace','config','cache','temp'))
    assert not Path(proposal['isolated_scope']).exists()
    assert (existing/'native-state.db').read_text()=='unique-public-fixture'

def test_existing_default_parent_collision_not_silently_rewritten(tmp_path):
    engine,data=machine(tmp_path)
    data['existing_roots']={'workspace':{'path':str(tmp_path/'AgentRuntime'),'exists':True}}
    with pytest.raises(SetupError,match='ROOT_OVERLAP') as caught:engine.plan(data)
    assert caught.value.conflicts[0]['sources']==['EXISTING_CONTEXT','NEW_DEFAULT']
    assert caught.value.conflicts[0]['relation']=='CONTAINS'

@pytest.mark.parametrize('existing',[None,[],{'workspace':'legacy-string'}, {'cache':{'path':False}}, {'config':None},
    {'state':'legacy-string'},{'exchange':{'path':'legacy-exchange'}},{'exchange':{'in':'value','out':False}}])
def test_malformed_existing_roots_fail_closed(tmp_path,existing):
    engine,data=machine(tmp_path);data['existing_roots']=existing
    result=engine.diagnose_root_plan(data)
    assert result['code']=='EXISTING_ROOT_METADATA_INVALID'
    assert not (tmp_path/'AgentRuntime').exists()

def test_explicit_paths_remain_checked_and_unknown_owner_cannot_move(tmp_path):
    engine,data=machine(tmp_path)
    with pytest.raises(SetupError,match='ROOT_OVERLAP'):engine.plan(data,overrides={'cache':str(tmp_path/'AgentRuntime/config')})
    old=tmp_path/'existing';old.mkdir();data['existing_roots']={'workspace':{'path':str(old),'exists':False}}
    with pytest.raises(SetupError,match='NEVER_RELOCATES'):engine.plan(data,overrides={'workspace':str(tmp_path/'new')})
    with pytest.raises(SetupError,match='ISOLATED_SCOPE_OVERLAP'):engine.plan(data,overrides={'isolated_scope':str(old/'nested')})
    with pytest.raises(SetupError,match='ISOLATED_SCOPE_TARGET_ESCAPE'):
        engine.plan(data,overrides={'isolated_scope':str(tmp_path/'separate-scope'),'workspace':str(old)})

def test_role_only_error_and_explicit_new_scope_pilot(tmp_path):
    engine,data=machine(tmp_path)
    data['existing_roots']={'workspace':{'path':str(tmp_path/'native')},'config':{'path':str(tmp_path/'native')}}
    engine.adapter.data=copy.deepcopy(data)
    async def scenario():
        app=SetupApp(engine)
        async with app.run_test(size=(100,32)) as pilot:
            app.query_one('#next',Button).focus();await pilot.press('enter');await pilot.pause(.5)
            assert app.step==0
            message=str(app.query_one('#status',Static).render())
            assert '工作区 / 配置' in message and '同一目录' in message
            assert str(tmp_path) not in message and 'Traceback' not in message
            app.query_one('#review-isolated-roots',Button).focus();await pilot.press('enter');await pilot.pause(.5)
            assert app.step==1 and len(app.plan_data['placement_rows'])==6
            assert not app.plan_data['host_authorized']
            assert not Path(app.overrides['isolated_scope']).exists()
    asyncio.run(scenario())

@pytest.mark.skipif(os.name!='nt',reason='Actual C: drive and WindowsPath semantics')
def test_native_c_default_plan_and_windows_first_next(tmp_path):
    engine,data=machine(tmp_path,native=True)
    with pytest.raises(SetupError,match='UNSAFE_ROOT'):safe_path('C:/')
    plan=engine.plan(engine.probe())
    assert len(plan['placement_rows'])==6
    assert plan['roots']['workspace']['path'].casefold()=='c:\\agentruntime\\workspaces'
    assert plan['documents_state']=='ONEDRIVE_REDIRECTED'
    async def scenario():
        app=SetupApp(engine)
        async with app.run_test(size=(100,32)) as pilot:
            app.query_one('#next',Button).focus();await pilot.press('enter');await pilot.pause(.5)
            assert app.step==1 and len(app.plan_data['placement_rows'])==6
            assert 'ROOT_OVERLAP' not in str(app.query_one('#status',Static).render())
            assert not app.plan_data['host_authorized']
    asyncio.run(scenario())

@pytest.mark.skipif(os.name!='nt',reason='Windows case-insensitive drive paths')
def test_native_drive_case_and_forward_slash_overlap(tmp_path):
    engine,data=machine(tmp_path,native=True)
    with pytest.raises(SetupError,match='ROOT_OVERLAP') as caught:
        engine.plan(data,overrides={'workspace':'C:/Public-Synthetic-Root','config':'c:/public-synthetic-root'})
    assert caught.value.conflicts[0]['relation']=='SAME_DIRECTORY'

@pytest.mark.skipif(os.name!='nt',reason='Actual Windows junction')
def test_native_junction_never_resolves_into_install_target(tmp_path):
    import subprocess
    target=tmp_path/'preserved-target';target.mkdir()
    (target/'native-state.db').write_text('unique-public-fixture')
    link=tmp_path/'junction'
    result=subprocess.run(['cmd','/d','/c','mklink','/J',str(link),str(target)],capture_output=True,timeout=10)
    assert result.returncode==0
    try:
        with pytest.raises(SetupError,match='REPARSE_PATH_DENIED'):safe_path(link/'config')
        assert (target/'native-state.db').read_text()=='unique-public-fixture'
    finally:link.rmdir()

def public_context(engine,paths,version='1.0.0'):
    target=Path(engine.adapter.data['documents'])/'HOST_AGENT.md'
    content={'host_agent_version':version,'paths':paths}
    target.write_text('```yaml\n'+yaml.safe_dump(content)+'```\n',encoding='utf-8')
    return target

def test_actual_probe_pipeline_canonical_v1_state_exchange_preserved(tmp_path):
    engine,data=machine(tmp_path)
    state=tmp_path/'native-state';state.mkdir();unique=state/'native-state.db';unique.write_bytes(b'public-unique-state')
    paths={name:{'path':str(tmp_path/('existing-'+name)),'owner':'HOST_MANAGED','relocatable':True}
        for name in ('workspace','config','cache','temp')}
    paths['state']={'path':str(state),'owner':'VENDOR_OWNED','relocatable':False,'reason':'public owner rule'}
    paths['exchange']={'in':str(tmp_path/'existing-exchange/in'),'out':str(tmp_path/'existing-exchange/out')}
    paths['secrets']={'catalog_ref':'public.logical-reference'}
    target=public_context(engine,paths);before=target.read_bytes()
    observation=engine.probe();plan=engine.plan(observation)
    assert len(plan['placement_rows'])==6 and plan['exchange']==paths['exchange']
    assert plan['roots']['state']['path']==str(state) and plan['roots']['state']['owner']=='VENDOR_OWNED'
    assert not plan['roots']['state']['relocatable'] and target.read_bytes()==before
    assert unique.read_bytes()==b'public-unique-state'
    async def scenario():
        app=SetupApp(engine)
        async with app.run_test(size=(100,32)) as pilot:
            app.query_one('#next',Button).focus();await pilot.press('enter');await pilot.pause(.5)
            assert app.step==1 and app.plan_data['exchange']==paths['exchange']
            assert target.read_bytes()==before and unique.read_bytes()==b'public-unique-state'
    asyncio.run(scenario())

@pytest.mark.parametrize('present',[False,True])
def test_legacy_inventory_presence_flag_is_not_root_or_owner(tmp_path,present):
    engine,data=machine(tmp_path);engine.adapter.data['existing_roots']={'host_agent':present}
    plan=engine.plan(engine.probe())
    assert len(plan['placement_rows'])==6 and plan['status']=='READY'
    # This flag was already ignored in the previous planner; not the proven BOSS cause.
    assert 'host_agent' not in plan['roots']

@pytest.mark.parametrize('paths,version,role,reason',[
    ({'state':'opaque-state'},'1.0.0','state','EXPECTED_MAPPING'),
    ({'state':{'path':'public/path','owner':False}},'1.0.0','state','OWNER_TYPE'),
    ({'state':{'path':'public/path','relocatable':'false'}},'1.0.0','state','RELOCATABLE_TYPE'),
    ({'state':{'path':'public/path','alternate_path':'must-not-ignore'}},'1.0.0','state','UNKNOWN_FIELD'),
    ({'exchange':{'in':'public/in','out':'public/out','other_path':'must-not-ignore'}},'1.0.0','exchange','DIRECTION_FIELDS_REQUIRED'),
    ({'exchange':{'in':{'path':'public/in'},'out':'public/out'}},'1.0.0','exchange','PATH_TYPE'),
    ({'exchange':{'in':'public/in'}},'1.0.0','exchange','DIRECTION_FIELDS_REQUIRED'),
    ({'workspace':{'owner':'HOST_MANAGED'}},'1.0.0','workspace','PATH_REQUIRED'),
    (['opaque'], '1.0.0','context','EXPECTED_MAPPING'),
    ({},'2.0.0','context','VERSION_UNSUPPORTED'),
    ({'unknown_private_field':{'path':'must-not-ignore'}},'1.0.0','context','UNKNOWN_ROLE'),
])
def test_context_shape_errors_atomic_private_safe_owner_gate(tmp_path,paths,version,role,reason):
    engine,data=machine(tmp_path);target=public_context(engine,paths,version);before=target.read_bytes()
    observation=engine.probe();diagnostic=engine.diagnose_root_plan(observation)
    assert diagnostic['code']=='EXISTING_ROOT_METADATA_INVALID'
    assert diagnostic['metadata_errors']==[{'role':role,'reason':reason}]
    assert str(tmp_path) not in json.dumps(diagnostic) and 'must-not-ignore' not in json.dumps(diagnostic)
    with pytest.raises(SetupError,match='EXISTING_ROOT_METADATA_INVALID'):engine.propose_isolated_roots(observation)
    assert target.read_bytes()==before and not (tmp_path/'AgentRuntime').exists()

@pytest.mark.parametrize('size',[(80,24),(120,36)])
def test_invalid_context_ui_has_owner_action_no_paths_or_override(tmp_path,size):
    engine,data=machine(tmp_path);target=public_context(engine,{'exchange':{'in':'sensitive/old-in','out':False}})
    before=target.read_bytes()
    async def scenario():
        app=SetupApp(engine)
        async with app.run_test(size=size) as pilot:
            app.query_one('#next',Button).focus();await pilot.press('enter');await pilot.pause(.5)
            assert app.step==0
            message=app.status_text
            assert 'Exchange' in message and 'PATH_TYPE' in message and '电脑所有者' in message
            assert 'sensitive' not in message and str(tmp_path) not in message and 'Traceback' not in message
            assert not app.query('#review-isolated-roots') and target.read_bytes()==before
            from rich.text import Text
            assert len(Text(message).wrap(app.console,app.query_one('#status',Static).content_region.width))<=3
    asyncio.run(scenario())

def test_unknown_diagnostic_fields_cannot_expose_paths(tmp_path):
    engine,data=machine(tmp_path);data['existing_root_metadata_errors']=[{'role':str(tmp_path),'reason':'private arbitrary output'}]
    diagnostic=engine.diagnose_root_plan(data)
    assert diagnostic['metadata_errors']==[{'role':'context','reason':'UNSAFE_CONTEXT'}]
    assert str(tmp_path) not in json.dumps(diagnostic) and 'private arbitrary' not in json.dumps(diagnostic)

def test_engine_emitted_context_probe_plan_roundtrip(tmp_path):
    engine,data=machine(tmp_path);initial=engine.plan(engine.probe())
    target=Path(data['documents'])/'HOST_AGENT.md';target.write_text(engine.context(initial),encoding='utf-8')
    before=target.read_bytes();observation=engine.probe();plan=engine.plan(observation)
    assert plan['roots']['state']['path']=='NATIVE_VENDOR_STATE'
    assert plan['roots']['state']['owner']=='VENDOR_OWNED' and not plan['roots']['state']['relocatable']
    assert plan['roots']['state']['exists'] is False
    assert plan['exchange']==initial['exchange'] and len(plan['placement_rows'])==6
    proposal=engine.propose_isolated_roots(observation)
    assert not Path(proposal['isolated_scope']).exists() and target.read_bytes()==before

def test_vendor_policy_sentinel_cannot_grant_relocation(tmp_path):
    engine,data=machine(tmp_path)
    public_context(engine,{'state':{'path':'NATIVE_VENDOR_STATE','owner':'HOST_MANAGED','relocatable':True}})
    diagnostic=engine.diagnose_root_plan()
    assert diagnostic['metadata_errors']==[{'role':'state','reason':'POLICY_SENTINEL_CLASSIFICATION'}]

@pytest.mark.parametrize('state', ['relative-state', '..', '/', '//private-server/state'])
def test_unsafe_or_sensitive_state_never_informational_bypass(tmp_path,state):
    engine,data=machine(tmp_path);public_context(engine,{'state':{'path':state,'owner':'VENDOR_OWNED','relocatable':False}})
    observation=engine.probe();diagnostic=engine.diagnose_root_plan(observation)
    assert diagnostic['status']=='BLOCKED' and diagnostic['metadata_errors'][0]['role'] in {'state','context'}
    with pytest.raises(SetupError,match='EXISTING_ROOT_METADATA_INVALID'):engine.propose_isolated_roots(observation)
    assert state not in json.dumps(diagnostic) or state=='/'

def test_token_shaped_state_refused_before_context_parse(tmp_path):
    engine,data=machine(tmp_path);public_context(engine,{'state':{'path':'github_pat_public-synthetic-not-a-key','owner':'VENDOR_OWNED','relocatable':False}})
    with pytest.raises(SetupError,match='SECRET'):engine.probe()
    diagnostic=engine.diagnose_root_plan()
    assert diagnostic['code']=='EXISTING_CONTEXT_SECRET_DATA_REFUSED'
    assert 'github_pat' not in json.dumps(diagnostic)

@pytest.mark.skipif(os.name!='nt',reason='Actual Windows state junction')
def test_native_state_junction_blocks_parser_and_new_scope(tmp_path):
    import subprocess
    engine,data=machine(tmp_path);target=tmp_path/'preserved-state';target.mkdir()
    link=tmp_path/'state-junction'
    assert subprocess.run(['cmd','/d','/c','mklink','/J',str(link),str(target)],capture_output=True,timeout=10).returncode==0
    try:
        public_context(engine,{'state':{'path':str(link),'owner':'VENDOR_OWNED','relocatable':False}})
        observation=engine.probe();diagnostic=engine.diagnose_root_plan(observation)
        assert diagnostic['metadata_errors']==[{'role':'state','reason':'UNSAFE_PATH'}]
        with pytest.raises(SetupError,match='EXISTING_ROOT_METADATA_INVALID'):engine.propose_isolated_roots(observation)
    finally:link.rmdir()
