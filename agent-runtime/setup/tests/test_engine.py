"""Inert filesystem/adapter fixtures; never the real Windows Host."""
import copy
import json
from pathlib import Path
import pytest
from agent_setup.engine import SetupEngine,FixtureAdapter,SetupError,IMAGE,digest

@pytest.fixture
def setup(tmp_path):
    docs=tmp_path/'Documents';docs.mkdir()
    observation={'platform':'windows','python_version':'3.14.8','python_verified':True,'wsl_app_version':'3.0.1.0',
        'wslc_capability':{'state':'PASS'},'documents':str(docs),'existing_roots':{},'active_workloads':[],
        'volumes':[{'mount':str(tmp_path/'volume'),'fs':'NTFS','free_bytes':80*1024**3,'capacity_bytes':200*1024**3,'device_id':'fixture','media_type':'SSD','bus_type':'NVMe'}]}
    adapter=FixtureAdapter(observation,tmp_path);engine=SetupEngine(adapter)
    plan=engine.plan(engine.probe(),overrides={'host_authorized':True})
    return engine,adapter,plan

def test_engine_does_not_import_textual():
    import inspect
    import agent_setup.engine as engine
    assert 'from textual' not in inspect.getsource(engine)

@pytest.mark.parametrize('field,value',[('wsl_app_version','2.6.1'),('wsl_app_version','6.18.40'),('python_version','3.13.9'),('python_verified',False),('platform','darwin')])
def test_support_and_python_fail_closed(setup,field,value):
    engine,adapter,_=setup;adapter.data[field]=value
    if field=='wsl_app_version' and value=='6.18.40':adapter.data['wsl_app_version']=None # kernel alone is not application evidence
    assert engine.plan(engine.probe())['status']=='BLOCKED'

def test_wsl3_requires_actual_wslc_and_capacity(setup):
    engine,adapter,_=setup
    adapter.data['wslc_capability']={'state':'UNKNOWN'}
    assert engine.plan(engine.probe())['status']=='BLOCKED'
    adapter.data['wslc_capability']={'state':'PASS'};adapter.data['volumes'][0]['free_bytes']=1
    assert engine.plan(engine.probe())['status']=='BLOCKED'

def test_apply_without_approval_never_writes(setup):
    engine,adapter,plan=setup
    with pytest.raises(SetupError,match='APPROVAL'):engine.apply(plan)
    assert not Path(plan['host_agent']).exists()

def test_apply_no_move_and_truthful_partial_readiness(setup):
    engine,adapter,plan=setup
    result=engine.apply(plan,approved=True)
    assert result['status']=='CONFIGURED_PENDING_AUTH'
    assert result['checks']['runtime']=='NOT_AUTHORIZED'
    assert result['checks']['github_fresh_recovery']=='NOT_AUTHORIZED'
    assert plan['placement']=='NO_MOVE' and len(plan['domains'])==7
    assert not 'token' in Path(plan['host_agent']).read_text()

def test_idempotent_exact_plan_and_rerun(setup):
    engine,adapter,plan=setup
    first=engine.apply(plan,approved=True)
    assert engine.apply(plan,approved=True)['host_agent_sha256']==first['host_agent_sha256']
    new=engine.plan(engine.probe(),overrides={'host_authorized':True})
    assert new['install_binding']==plan['install_binding']
    assert engine.apply(new,approved=True)['host_agent_sha256']==first['host_agent_sha256']

def test_stale_context_blocks_apply(setup):
    engine,adapter,plan=setup
    Path(plan['host_agent']).write_text('user unique edits')
    with pytest.raises(SetupError,match='STALE'):engine.apply(plan,approved=True)
    assert Path(plan['host_agent']).read_text()=='user unique edits'

def test_concurrent_attempt_lock(setup):
    engine,adapter,plan=setup
    control=Path(plan['roots']['config']['path'])/'.agent-runtime-setup';control.mkdir(parents=True)
    (control/'apply.lock').write_text('existing owner')
    with pytest.raises(SetupError,match='CONCURRENT'):engine.apply(plan,approved=True)

@pytest.mark.parametrize('override',['../escape','bad,readonly','bad\nline'])
def test_path_injection(setup,override):
    engine,adapter,plan=setup
    with pytest.raises(SetupError):engine.plan(engine.probe(),overrides={'workspace':override})

def test_symlink_path_injection(setup,tmp_path):
    engine,adapter,plan=setup
    link=tmp_path/'link'
    try:link.symlink_to(tmp_path/'Documents',target_is_directory=True)
    except OSError:pytest.skip('Windows symlink privilege unavailable')
    with pytest.raises(SetupError,match='REPARSE'):engine.plan(engine.probe(),overrides={'workspace':str(link/'work')})

def test_existing_unowned_directory_and_active_writer(setup):
    engine,adapter,plan=setup
    root=Path(plan['roots']['workspace']['path']);root.mkdir(parents=True)
    assert engine.plan(engine.probe())['status']=='BLOCKED'
    adapter.data['active_workloads']=[{'path':str(root)}]
    with pytest.raises(SetupError,match='ACTIVE_WRITER'):engine.plan(engine.probe())

def test_preserve_existing_classified_root_never_move(setup,tmp_path):
    engine,adapter,plan=setup
    root=tmp_path/'existing';root.mkdir()
    adapter.data['existing_roots']['workspace']={'path':str(root),'owner':'HOST_MANAGED','relocatable':True,'exists':True}
    preserved=engine.plan(engine.probe())
    assert preserved['roots']['workspace']['path']==str(root)
    with pytest.raises(SetupError,match='NEVER_RELOCATES'):engine.plan(engine.probe(),overrides={'workspace':str(tmp_path/'other')})

def test_missing_private_destination_blocks_recovery_claim(setup):
    engine,_,_=setup
    plan=engine.plan(engine.probe(),github={'recovery_requested':True,'authorized':True})
    assert plan['status']=='READY' and plan['recovery_authorized'] is False
    result=engine.apply({**plan,'host_authorized':True,'fingerprint':digest({**{k:v for k,v in plan.items() if k!='fingerprint'},'host_authorized':True})},approved=True)
    assert result['capabilities']['fresh_recovery']['state']=='NOT_VERIFIED'

def test_credentials_values_rejected(setup):
    engine,_,_=setup
    with pytest.raises(SetupError,match='REFERENCE_ONLY'):engine.plan(engine.probe(),github={'ref':'token=not-a-reference'})
    with pytest.raises(SetupError,match='REFERENCE_ONLY'):engine.plan(engine.probe(),github={'helper':('gh'+'p_')+'A'*40})

def test_network_interruption_checkpoint_and_resume(setup):
    engine,adapter,_=setup
    plan=engine.plan(engine.probe(),overrides={'host_authorized':True,'runtime':True})
    adapter.data['network_interruption']=True
    with pytest.raises(SetupError,match='NETWORK'):engine.apply(plan,approved=True)
    assert engine.repair(plan)['checkpoint_status']=='INTERRUPTED'
    adapter.data['network_interruption']=False
    assert engine.apply(plan,approved=True)['checks']['image']=='PASS'

def test_rollback_preserves_new_unique_data(setup):
    engine,_,plan=setup;engine.apply(plan,approved=True)
    root=Path(plan['roots']['workspace']['path']);unique=root/'user.txt';unique.write_text('preserve')
    outcome=engine.rollback(plan,approved=True)
    assert outcome['status']=='ROLLED_BACK' and unique.read_text()=='preserve'
    assert not Path(plan['host_agent']).exists()

def test_plan_tamper_and_apply_time_pressure(setup):
    engine,adapter,plan=setup
    changed=copy.deepcopy(plan);changed['image']='floating:latest'
    with pytest.raises(SetupError,match='PLAN_DRIFT'):engine.apply(changed,approved=True)
    adapter.data['volumes'][0]['free_bytes']=1
    with pytest.raises(SetupError,match='STORAGE_PRESSURE'):engine.apply(plan,approved=True)

def test_unknown_config_created_after_plan_is_not_touched(setup):
    engine,_,plan=setup
    config=Path(plan['roots']['config']['path']);config.mkdir(parents=True)
    with pytest.raises(SetupError,match='UNKNOWN_OWNER'):engine.apply(plan,approved=True)
    assert list(config.iterdir())==[]

def test_full_reviewed_plan_is_recoverable_after_interruption(setup):
    engine,adapter,_=setup
    plan=engine.plan(engine.probe(),overrides={'host_authorized':True,'runtime':True})
    adapter.data['network_interruption']=True
    with pytest.raises(SetupError):engine.apply(plan,approved=True)
    stored=Path(engine.repair(plan)['reviewed_plan'])
    assert json.loads(stored.read_text())['fingerprint']==plan['fingerprint']
    adapter.data['network_interruption']=False
    assert engine.apply(json.loads(stored.read_text()),approved=True)['checks']['image']=='PASS'

def test_rollback_requires_transaction_lock_and_stops_ready_runtime(setup):
    engine,_,plan=setup;engine.apply(plan,approved=True)
    control=Path(plan['roots']['config']['path'])/'.agent-runtime-setup'
    (control/'apply.lock').write_text('other owner')
    with pytest.raises(SetupError,match='CONCURRENT'):engine.rollback(plan,approved=True)
    (control/'apply.lock').unlink()
    receipt=json.loads((control/'receipt.json').read_text());receipt['runtime']={'state':'READY'}
    (control/'receipt.json').write_text(json.dumps(receipt))
    with pytest.raises(SetupError,match='RUNTIME_STOP'):engine.rollback(plan,approved=True)
    assert Path(plan['host_agent']).exists() and not (control/'apply.lock').exists()

def test_secret_bearing_old_context_is_not_backed_up(setup):
    engine,_,plan=setup
    Path(plan['host_agent']).write_text('```yaml\nhost_agent_version: 1.0.0\npassword: synthetic-prohibited\n```')
    with pytest.raises(SetupError,match='SECRET'):engine.plan(engine.probe())
    assert not (Path(plan['roots']['config']['path'])/'.agent-runtime-setup/HOST_AGENT.previous').exists()

def test_fixture_cannot_create_documents_outside_sandbox(tmp_path,monkeypatch):
    from agent_setup.__main__ import main
    sandbox=tmp_path/'sandbox';outside=tmp_path/'outside';fixture=tmp_path/'fixture.json'
    fixture.write_text(json.dumps({'documents':str(outside)}))
    import sys
    monkeypatch.setattr(sys,'argv',['agent_setup','cli','probe','--fixture',str(fixture),'--sandbox',str(sandbox)])
    with pytest.raises(SetupError,match='FIXTURE_ESCAPE'):main()
    assert not outside.exists()

def test_control_reparse_and_random_atomic_temp(setup,tmp_path):
    engine,_,plan=setup
    config=Path(plan['roots']['config']['path']);config.mkdir(parents=True)
    outside=tmp_path/'outside';outside.mkdir()
    link=config/'.agent-runtime-setup'
    try:link.symlink_to(outside,target_is_directory=True)
    except OSError:pytest.skip('Windows symlink privilege unavailable')
    with pytest.raises(SetupError,match='REPARSE'):engine.apply(plan,approved=True)
    assert list(outside.iterdir())==[]

@pytest.mark.parametrize('marker',[{'schema':'1.0.0'}, {'schema':'1.0.0','owner':'foreign','attempt':'a'*32}])
def test_schema_only_or_foreign_marker_never_claims_unknown_root(setup,marker):
    engine,_,plan=setup
    root=Path(plan['roots']['workspace']['path']);root.mkdir(parents=True)
    (root/'.agent-runtime-setup-owner.json').write_text(json.dumps(marker))
    reviewed=engine.plan(engine.probe())
    assert reviewed['status']=='BLOCKED' and reviewed['roots']['workspace']['owner']=='UNKNOWN'

@pytest.mark.parametrize('field,value',[('attempt','f'*32),('root','foreign/root'),('install_binding','f'*64),('config_root','foreign/config')])
def test_foreign_complete_marker_binding_rejected(setup,field,value):
    engine,_,plan=setup;engine.apply(plan,approved=True)
    root=Path(plan['roots']['workspace']['path']);marker=root/'.agent-runtime-setup-owner.json'
    record=json.loads(marker.read_text());record[field]=value;marker.write_text(json.dumps(record))
    assert engine.plan(engine.probe())['roots']['workspace']['owner']=='UNKNOWN'

def test_checkbox_and_image_do_not_enable_context(setup):
    import yaml
    engine,_,plan=setup
    plan['github']['authorized']=True
    context=engine.context(plan,'sha256:'+'a'*64)
    projection=yaml.safe_load(context.split('```yaml\n')[1].split('```')[0])
    assert projection['agents']['opencode']['enabled'] is False
    assert projection['agents']['opencode']['readiness']=='CONFIGURED_PENDING_AUTH'

def test_incomplete_canonical_classification_cannot_claim_unknown_root(setup):
    engine,adapter,plan=setup
    root=Path(plan['roots']['workspace']['path']);root.mkdir(parents=True)
    adapter.data['existing_roots']['workspace']={'path':str(root),'owner':'HOST_MANAGED','relocatable':True,'exists':True}
    adapter.data['canonical_classification']={'verified':True,'sha256':None,'owner_pointer':'owner:canonical'}
    assert engine.plan(engine.probe())['roots']['workspace']['owner']=='UNKNOWN'

def test_verified_github_cannot_hide_missing_model(setup,monkeypatch):
    engine,adapter,plan=setup;engine.apply(plan,approved=True)
    receipt_path=Path(plan['roots']['config']['path'])/'.agent-runtime-setup/receipt.json'
    receipt=json.loads(receipt_path.read_text());receipt['runtime']={'state':'READY'}
    receipt['image']={'state':'PASS','config_id':'sha256:'+'a'*64};receipt['durable']={'state':'PASS'}
    receipt_path.write_text(json.dumps(receipt))
    adapter.fixture=False
    monkeypatch.setattr(adapter,'verify_runtime',lambda *a,**kw:{'state':'PASS'},raising=False)
    plan['github'].update(helper_approved=True,helper='approved',repo='example/repo',work='example/repo#1')
    plan.pop('fingerprint');plan['fingerprint']=digest(plan)
    proof={'state':'PASS','repo':'example/repo','work':'example/repo#1','context_sha256':receipt['context_after_sha256'],
           'authenticated_api':True,'github_read':True,'github_write':True,'fresh_recovery':True}
    monkeypatch.setattr(adapter,'helper_status',lambda *a,**kw:proof,raising=False)
    monkeypatch.setattr(adapter,'runtime_readiness',lambda _: {'credentials':'PASS','model':'NOT_AUTHORIZED'},raising=False)
    outcome=engine.verify(plan)
    assert outcome['status']=='RUNTIME_GITHUB_READY' and outcome['checks']['model']=='NOT_AUTHORIZED'
    # A past checkpoint alone cannot hide revoked/unverified current model auth.
    receipt['readiness']={'model':'PASS','credentials':'PASS'};receipt_path.write_text(json.dumps(receipt))
    assert engine.verify(plan)['status']=='RUNTIME_GITHUB_READY'
    monkeypatch.setattr(adapter,'runtime_readiness',lambda _: {'credentials':'PASS','model':'PASS'},raising=False)
    assert engine.verify(plan)['status']=='READY'

def test_denied_runtime_start_clears_preflight_enabled_projection(setup,monkeypatch):
    import yaml
    engine,adapter,_=setup
    plan=engine.plan(engine.probe(),overrides={'host_authorized':True,'runtime':True},github={'authorized':True},model={'ref':'fixture.model'})
    monkeypatch.setattr(adapter,'runtime_readiness',lambda _: {'credentials':'PASS','model':'PASS'},raising=False)
    outcome=engine.apply(plan,approved=True)
    projection=yaml.safe_load(Path(plan['host_agent']).read_text().split('```yaml\n')[1].split('```')[0])
    assert outcome['status']=='CONFIGURED_PENDING_AUTH'
    assert projection['agents']['opencode']['enabled'] is False
