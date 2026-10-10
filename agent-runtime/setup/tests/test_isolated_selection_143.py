"""Owner-reviewed fresh parent selection; preview never creates or moves data."""
import copy
import os
from pathlib import Path
import subprocess
import pytest
from agent_setup.engine import SetupEngine,FixtureAdapter,SetupError

GIB=1024**3

@pytest.fixture
def machine(tmp_path):
    documents=tmp_path/'Documents';documents.mkdir()
    fast=tmp_path/'fast-volume';fast.mkdir()
    selected=tmp_path/'selected-volume';selected.mkdir()
    data={'platform':'windows','python_version':'3.14.8','python_verified':True,'wsl_app_version':'3.0.1',
        'wslc_capability':{'state':'PASS'},'documents':str(documents),'existing_roots':{},'active_workloads':[],
        'volumes':[{'mount':str(fast),'device_id':'public-fast','bus_type':'NVMe','media_type':'SSD','fs':'NTFS','capacity_bytes':256*GIB,'free_bytes':64*GIB},
            {'mount':str(selected),'device_id':'public-selected','bus_type':'SATA','media_type':'HDD','fs':'NTFS','capacity_bytes':1024*GIB,'free_bytes':128*GIB}]}
    adapter=FixtureAdapter(data,tmp_path)
    return SetupEngine(adapter),adapter,tmp_path

@pytest.mark.parametrize('volume_index',[0,1])
def test_explicit_parent_same_and_cross_volume_scopes_are_fresh(machine,volume_index):
    engine,adapter,tmp=machine
    parent=Path(adapter.data['volumes'][volume_index]['mount'])/'selected-parent';parent.mkdir()
    unique=parent/'existing-unique.db';unique.write_bytes(b'public-synthetic-unique')
    observation=engine.probe();before=copy.deepcopy(observation)
    original=engine.plan(observation)
    proposal=engine.propose_isolated_roots(observation,parent=parent)
    scope=Path(proposal['isolated_scope'])
    assert scope.parent==parent and scope.name.startswith('AgentRuntime-Setup-') and not scope.exists()
    plan=engine.plan(observation,overrides={'isolated_scope':str(scope)})
    assert plan['status']=='READY' and not plan['host_authorized'] and plan['placement']=='NO_MOVE'
    assert plan['storage']['device_id']==adapter.data['volumes'][volume_index]['device_id']
    for name in ('workspace','config','cache','temp'):
        assert Path(plan['roots'][name]['path']).is_relative_to(scope) and not Path(plan['roots'][name]['path']).exists()
    assert all(Path(path).is_relative_to(scope) for path in plan['exchange'].values())
    assert all(row['device_id']==plan['storage']['device_id'] for row in plan['placement_rows'] if row['name']!='host_agent')
    assert original['fingerprint']!=plan['fingerprint'] and original['install_binding']!=plan['install_binding']
    assert observation==before and unique.read_bytes()==b'public-synthetic-unique'
    with pytest.raises(SetupError,match='APPROVAL'):engine.apply(plan,approved=True)

@pytest.mark.parametrize('role',['workspace','config','cache','temp','state','exchange'])
def test_protected_parent_never_offers_new_child(machine,role):
    engine,adapter,tmp=machine
    protected=Path(adapter.data['volumes'][1]['mount'])/'protected';protected.mkdir()
    unique=protected/'old-native.db';unique.write_text('public-old-state')
    if role=='exchange':adapter.data['existing_roots'][role]={'in':str(protected),'out':str(protected/'out')}
    else:adapter.data['existing_roots'][role]={'path':str(protected),'owner':'UNKNOWN','relocatable':False}
    with pytest.raises(SetupError,match='ISOLATED_SCOPE_OVERLAP'):
        engine.propose_isolated_roots(engine.probe(),parent=protected)
    assert unique.read_text()=='public-old-state' and sorted(p.name for p in protected.iterdir())==['old-native.db']

@pytest.mark.parametrize('change',[
    {'free_bytes':GIB},{'fs':'FAT32'},{'local':False},{'bus_type':'USB'},{'bus_type':'network'},
])
def test_selected_volume_pressure_or_unsupported_never_falls_back(machine,change):
    engine,adapter,tmp=machine;adapter.data['volumes'][1].update(change)
    parent=Path(adapter.data['volumes'][1]['mount'])
    with pytest.raises(SetupError,match='ISOLATED_PARENT_STORAGE_UNSUPPORTED_OR_PRESSURE'):
        engine.propose_isolated_roots(engine.probe(),parent=parent)
    assert list(parent.iterdir())==[]

def test_unknown_parent_volume_or_non_directory_blocked(machine):
    engine,adapter,tmp=machine
    unknown=tmp/'not-in-volume';unknown.mkdir()
    with pytest.raises(SetupError,match='ISOLATED_SCOPE_VOLUME_UNKNOWN'):engine.propose_isolated_roots(engine.probe(),parent=unknown)
    with pytest.raises(SetupError,match='ISOLATED_PARENT_DIRECTORY_REQUIRED'):engine.propose_isolated_roots(engine.probe(),parent=tmp/'absent')
    file=Path(adapter.data['volumes'][0]['mount'])/'file';file.write_text('public-file')
    with pytest.raises(SetupError,match='ISOLATED_PARENT_DIRECTORY_REQUIRED'):engine.propose_isolated_roots(engine.probe(),parent=file)

def test_unknown_existing_metadata_no_isolation_bypass(machine):
    engine,adapter,tmp=machine
    adapter.data['existing_roots']={'state':{'path':str(tmp/'state'),'unrecognized_root':str(tmp/'other')}}
    with pytest.raises(SetupError,match='EXISTING_ROOT_METADATA_INVALID'):
        engine.propose_isolated_roots(engine.probe(),parent=Path(adapter.data['volumes'][1]['mount']))

def test_readonly_home_parent_never_grants_home_as_install_target(machine,monkeypatch):
    from agent_setup.engine import safe_path
    engine,adapter,tmp=machine
    parent=Path(adapter.data['volumes'][1]['mount'])/'public-synthetic-home';parent.mkdir()
    monkeypatch.setattr(Path,'home',classmethod(lambda cls:parent))
    with pytest.raises(SetupError,match='UNSAFE_ROOT'):safe_path(parent)
    proposal=engine.propose_isolated_roots(engine.probe(),parent=parent)
    scope=Path(proposal['isolated_scope'])
    assert scope.parent==parent and not scope.exists()
    with pytest.raises(SetupError,match='UNSAFE_PATH'):engine.propose_isolated_roots(engine.probe(),parent='relative-parent')

def test_scope_escape_existing_move_and_capacity_drift_still_blocked(machine):
    engine,adapter,tmp=machine
    parent=Path(adapter.data['volumes'][1]['mount']);observation=engine.probe()
    proposal=engine.propose_isolated_roots(observation,parent=parent)
    with pytest.raises(SetupError,match='ISOLATED_SCOPE_TARGET_ESCAPE'):
        engine.plan(observation,overrides={'isolated_scope':proposal['isolated_scope'],'workspace':str(tmp/'outside')})
    old=Path(adapter.data['volumes'][0]['mount'])/'old-workspace';old.mkdir()
    adapter.data['existing_roots']['workspace']={'path':str(old),'exists':True,'owner':'UNKNOWN','relocatable':False}
    with pytest.raises(SetupError,match='NEVER_RELOCATES'):
        engine.plan(engine.probe(),overrides={'workspace':str(parent/'replacement')})
    adapter.data['volumes'][1]['free_bytes']=GIB
    with pytest.raises(SetupError,match='ISOLATED_PARENT_STORAGE_UNSUPPORTED_OR_PRESSURE'):
        engine.propose_isolated_roots(engine.probe(),parent=parent)

@pytest.mark.skipif(os.name!='nt',reason='Actual Windows junction')
def test_native_parent_junction_rejected_without_touching_target(machine):
    engine,adapter,tmp=machine
    target=Path(adapter.data['volumes'][1]['mount']);link=tmp/'parent-junction'
    assert subprocess.run(['cmd','/d','/c','mklink','/J',str(link),str(target)],capture_output=True,timeout=10).returncode==0
    try:
        with pytest.raises(SetupError,match='REPARSE_PATH_DENIED'):engine.propose_isolated_roots(engine.probe(),parent=link)
        assert list(target.iterdir())==[]
    finally:link.rmdir()

@pytest.mark.skipif(os.name!='nt',reason='Actual native Windows drive anchors')
def test_native_drive_parent_is_readonly_child_scope_not_root_install(tmp_path):
    import shutil
    from agent_setup.engine import safe_path
    documents=tmp_path/'Documents';documents.mkdir()
    anchors=list(dict.fromkeys(['C:\\',tmp_path.anchor]))
    volumes=[]
    for index,anchor in enumerate(anchors):
        capacity,_,free=shutil.disk_usage(anchor)
        volumes.append({'mount':anchor,'device_id':f'public-native-anchor-{index}','fs':'NTFS',
            'bus_type':'NVMe' if index==0 else 'SATA','media_type':'SSD','capacity_bytes':capacity,'free_bytes':free})
    data={'platform':'windows','python_version':'3.14.8','python_verified':True,'wsl_app_version':'3.0.1',
        'wslc_capability':{'state':'PASS'},'documents':str(documents),'existing_roots':{},'active_workloads':[],'volumes':volumes}
    class ReadOnlyWindowsInventory:
        can_apply=False
        def probe(self):return copy.deepcopy(data)
    engine=SetupEngine(ReadOnlyWindowsInventory());observation=engine.probe()
    for volume in volumes:
        with pytest.raises(SetupError,match='UNSAFE_ROOT'):safe_path(volume['mount'])
        proposal=engine.propose_isolated_roots(observation,parent=volume['mount'])
        scope=Path(proposal['isolated_scope'])
        assert scope.parent==Path(volume['mount']) and not scope.exists()
        plan=engine.plan(observation,overrides={'isolated_scope':str(scope)})
        assert len(plan['placement_rows'])==6 and plan['storage']['device_id']==volume['device_id']
        assert not plan['host_authorized'] and not scope.exists()
