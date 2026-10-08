"""Synthetic V2 placement and independently staged readiness counterexamples."""
import copy
import json
from pathlib import Path
import pytest
from agent_setup.engine import SetupEngine, FixtureAdapter, SetupError, IMAGE

GIB=1024**3

@pytest.fixture
def machine(tmp_path):
    documents=tmp_path/'OneDrive - Synthetic'/'Documents';documents.mkdir(parents=True)
    disks=[{'mount':str(tmp_path/name),'fs':'NTFS','device_id':physical,'media_type':media,'bus_type':bus,
            'capacity_bytes':capacity*GIB,'free_bytes':free*GIB} for name,physical,media,bus,capacity,free in [
            ('C','disk-0','SSD','NVMe',256,48),('E','disk-1','SSD','SATA',512,256),('D','disk-2','HDD','SATA',2048,1800)]]
    data={'platform':'windows','python_version':'3.14.8','python_verified':True,'wsl_app_version':'3.0.1',
          'wslc_capability':{'state':'PASS'},'documents':str(documents),'volumes':disks,'existing_roots':{},'active_workloads':[]}
    adapter=FixtureAdapter(data,tmp_path)
    return SetupEngine(adapter),adapter,tmp_path


def test_nvme_not_hdd_capacity_and_onedrive_explanation(machine):
    engine,adapter,_=machine;plan=engine.plan(engine.probe())
    assert plan['storage']['device_id']=='disk-0'
    assert plan['documents_state']=='ONEDRIVE_REDIRECTED'
    assert len(plan['placement_rows'])==6
    assert plan['roots']['state']['owner']=='VENDOR_OWNED' and plan['placement']=='NO_MOVE'
    assert plan['expected_host_agent_sha256'] is None
    assert all(row['bus_type']=='NVMe' for row in plan['placement_rows'] if row['name']!='host_agent')


def test_pressure_falls_back_to_ssd_then_hdd_only_when_needed(machine):
    engine,adapter,_=machine;adapter.data['volumes'][0]['free_bytes']=7*GIB
    assert engine.plan(engine.probe())['storage']['device_id']=='disk-1'
    adapter.data['volumes'][1]['free_bytes']=7*GIB
    assert engine.plan(engine.probe())['storage']['device_id']=='disk-2'


def test_physical_disk_partitions_locality_and_headroom(machine):
    engine,adapter,tmp=machine
    # Same physical disk has two partitions: locality doesn't manufacture capacity.
    other=copy.deepcopy(adapter.data['volumes'][0]);other.update(mount=str(tmp/'F'),free_bytes=192*GIB)
    adapter.data['volumes'].append(other)
    plan=engine.plan(engine.probe())
    assert plan['storage']['mount']==str(tmp/'F') and plan['storage']['device_id']=='disk-0'
    # On equally fast devices, actual WSLC locality is preferred; C is not privileged.
    faster=copy.deepcopy(other);faster.update(mount=str(tmp/'G'),device_id='disk-3',free_bytes=80*GIB)
    adapter.data['volumes'].append(faster);adapter.data['wslc_storage_device_id']='disk-3'
    assert engine.plan(engine.probe())['storage']['mount']==str(tmp/'G')


def test_network_or_usb_volume_never_silently_recommended(machine):
    engine,adapter,_=machine
    adapter.data['volumes'][0]['local']=False
    adapter.data['volumes'][1]['bus_type']='USB'
    assert engine.plan(engine.probe())['storage']['device_id']=='disk-2'


def test_advanced_override_rechecks_capacity_and_topology(machine):
    engine,adapter,tmp=machine
    adapter.data['volumes'][1]['free_bytes']=1
    plan=engine.plan(engine.probe(),overrides={'cache':str(tmp/'E'/'cache')})
    assert plan['status']=='BLOCKED'
    adapter.data['volumes'][1]['free_bytes']=20*GIB
    plan=engine.plan(engine.probe(),overrides={'cache':str(tmp/'E'/'cache'),'host_authorized':True})
    assert len(plan['storage_bindings'])==2
    adapter.data['volumes'][1]['device_id']='swapped-physical-disk'
    with pytest.raises(SetupError,match='TOPOLOGY_DRIFT'):engine.apply(plan,approved=True)


def test_unknown_dirty_collision_preserved_and_move_refused(machine):
    engine,adapter,tmp=machine
    existing=tmp/'D'/'existing';existing.mkdir(parents=True);unique=existing/'dirty-worktree.txt';unique.write_text('unique')
    adapter.data['existing_roots']['workspace']={'path':str(existing),'owner':'UNKNOWN','relocatable':False,'exists':True}
    plan=engine.plan(engine.probe())
    assert plan['roots']['workspace']['path']==str(existing) and plan['status']=='BLOCKED'
    assert 'NO_MOVE' in plan['roots']['workspace']['reason'] and unique.read_text()=='unique'
    with pytest.raises(SetupError,match='NEVER_RELOCATES'):engine.plan(engine.probe(),overrides={'workspace':str(tmp/'C'/'new')})
    with pytest.raises(SetupError,match='ROOT_OVERLAP'):engine.plan(engine.probe(),overrides={'config':str(existing)})


def test_onedrive_hash_drift_never_overwrites(machine):
    engine,adapter,_=machine
    plan=engine.plan(engine.probe(),overrides={'host_authorized':True})
    target=Path(plan['host_agent']);target.write_text('sync conflict / owner edits')
    with pytest.raises(SetupError,match='HOST_AGENT_STALE'):engine.apply(plan,approved=True)
    assert target.read_text()=='sync conflict / owner edits'


def test_local_stage_without_helpers_never_promotes_auth(machine,monkeypatch):
    engine,adapter,_=machine
    calls=[]
    def start(plan,target):
        calls.append((plan['image'],target));return {'state':'PASS','server_authenticated':'PASS','profile':'local'}
    monkeypatch.setattr(adapter,'start_local_runtime',start,raising=False)
    plan=engine.plan(engine.probe(),overrides={'host_authorized':True,'runtime':True},
         github={'recovery_requested':True},durable={'destination':'https://github.com/synthetic/private','authorized':False})
    assert plan['status']=='READY'
    result=engine.apply(plan,approved=True)
    assert calls[0][0]==IMAGE and result['capabilities']['local_install']['state']=='PASS'
    assert result['capabilities']['github']['state']=='NEEDS_CONNECTION'
    assert result['capabilities']['model']['state']=='NOT_AUTHORIZED'
    assert result['capabilities']['fresh_recovery']['state']=='NOT_VERIFIED' and result['status']!='READY'
    material=Path(plan['host_agent']).read_text()+Path(result['receipt']).read_text()
    assert 'private_key' not in material and 'access_token' not in material
    assert engine.verify(plan)['capabilities']==result['capabilities']


def test_credential_metadata_boundary_and_consent(machine,monkeypatch):
    engine,adapter,_=machine
    assert engine.discover_credentials()['github']['state']=='REUSE_NOT_SUPPORTED'
    with pytest.raises(SetupError,match='APPROVAL'):engine.connect_credential('github','auto')
    assert engine.connect_credential('github','skip')['state']=='SKIPPED'
    monkeypatch.setattr(adapter,'discover_credentials',lambda:{'github':{'access_token':'synthetic-forbidden'}},raising=False)
    with pytest.raises(SetupError,match='UNSAFE_CREDENTIAL_METADATA'):engine.discover_credentials()


@pytest.mark.parametrize('payload',[{'api_key':'opaque-value'}, {'access_token':'opaque-value'}, {'unexpected':'unbounded-provider-output'}, {'plan_inputs':{'github':{'authorized':True}}}, {'account':'line1\nline2'}, {'state':'PROVIDER_INVENTED_PASS'}])
def test_unknown_credential_fields_never_reach_ui(machine,monkeypatch,payload):
    engine,adapter,_=machine
    monkeypatch.setattr(adapter,'discover_credentials',lambda:{'github':payload},raising=False)
    with pytest.raises(SetupError,match='CREDENTIAL'):engine.discover_credentials()


def test_local_and_model_proofs_are_independent_and_revocation_is_current(machine,monkeypatch):
    engine,adapter,_=machine
    monkeypatch.setattr(adapter,'start_local_runtime',lambda *args:{'state':'PASS','server_authenticated':'PASS','local_only':True},raising=False)
    model={'model':'PASS','credentials':'NOT_AUTHORIZED'}
    monkeypatch.setattr(adapter,'runtime_readiness',lambda _:dict(model),raising=False)
    plan=engine.plan(engine.probe(),overrides={'host_authorized':True,'runtime':True})
    result=engine.apply(plan,approved=True)
    assert result['capabilities']['local_install']['state']=='PASS'
    assert result['capabilities']['model']['state']=='PASS'
    assert result['capabilities']['github']['state']!='PASS' and result['status']!='READY'
    # A previous PASS cannot mask a revoked provider on the next verification.
    model['model']='NOT_AUTHORIZED'
    assert engine.verify(plan)['capabilities']['model']['state']=='NOT_AUTHORIZED'
    adapter.fixture=False
    options=[]
    def native_verify(*args,**kwargs):
        options.append(kwargs);return {'state':'PASS','server_authenticated':'NOT_VERIFIED'}
    monkeypatch.setattr(adapter,'verify_runtime',native_verify,raising=False)
    assert engine.verify(plan)['capabilities']['local_install']['state']=='NOT_VERIFIED'
    assert options[0]['expected_local'] is True
    assert options[0]['expected_mount_sources']=={
        '/host-context':str(Path(plan['runtime']['attempt'])/'context'),
        '/exchange/in':plan['runtime']['incoming'],'/exchange/out':plan['runtime']['outgoing']}


@pytest.mark.parametrize('failure',['missing','denied','exception','wrong_hash'])
def test_optional_writeback_failure_keeps_local_install(machine,monkeypatch,failure):
    engine,adapter,_=machine
    starts=[]
    def start(*args):
        starts.append(True);return {'state':'PASS','server_authenticated':'PASS','local_only':True}
    monkeypatch.setattr(adapter,'start_local_runtime',start,raising=False)
    if failure!='missing':
        def writeback(*args):
            if failure=='exception':raise RuntimeError('opaque raw upstream credential output MUST NOT PERSIST')
            return {'state':'PASS' if failure=='wrong_hash' else 'NOT_AUTHORIZED','context_sha256':'f'*64,'raw':'NEVER_PERSIST'}
        monkeypatch.setattr(adapter,'writeback_context',writeback,raising=False)
    plan=engine.plan(engine.probe(),overrides={'host_authorized':True,'runtime':True},
         github={'authorized':True,'recovery_requested':True},durable={'destination':'https://github.com/synthetic/private','authorized':True})
    result=engine.apply(plan,approved=True)
    assert len(starts)==1 and result['capabilities']['local_install']['state']=='PASS'
    assert result['checks']['durable_context']=='BLOCKED' and result['capabilities']['fresh_recovery']['state']!='PASS'
    assert result['status']!='READY'
    receipt=Path(result['receipt']);raw=receipt.read_text()
    assert 'NEVER_PERSIST' not in raw and 'opaque raw' not in raw
    # Crash after a recorded successful start: retry re-verifies the same bound
    # attempt, keeping recovery failure separate and without creating dirs again.
    saved=json.loads(raw);saved['status']='INTERRUPTED';receipt.write_text(json.dumps(saved))
    resumed=engine.apply(plan,approved=True)
    assert len(starts)==1 and resumed['capabilities']['local_install']['state']=='PASS'
    assert json.loads(receipt.read_text())['status']=='APPLIED'


def test_writeback_local_projection_mutation_remains_currentness_gate(machine,monkeypatch):
    engine,adapter,_=machine;starts=[]
    monkeypatch.setattr(adapter,'start_local_runtime',lambda *args:starts.append(True),raising=False)
    def writeback(plan,target,expected):
        target.write_text('owner concurrent mutation')
        return {'state':'BLOCKED'}
    monkeypatch.setattr(adapter,'writeback_context',writeback,raising=False)
    plan=engine.plan(engine.probe(),overrides={'host_authorized':True,'runtime':True},github={'authorized':True},
         durable={'destination':'https://github.com/synthetic/private','authorized':True})
    with pytest.raises(SetupError,match='HOST_AGENT_STALE'):engine.apply(plan,approved=True)
    assert starts==[] and Path(plan['host_agent']).read_text()=='owner concurrent mutation'
