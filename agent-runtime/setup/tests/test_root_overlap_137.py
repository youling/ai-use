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
