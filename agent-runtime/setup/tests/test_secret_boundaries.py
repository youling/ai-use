"""RF-2 synthetic fine-grained tokens: refusal before rendering or persistence."""
import copy
import json
from pathlib import Path
import subprocess
import sys

import pytest
from agent_setup.engine import SetupEngine, FixtureAdapter, SetupError, atomic_json, digest, reference, safe_path
from agent_setup.credentials import validated_metadata


TOKEN = 'github_' + 'pat_' + 'SYNTHETIC_ONLY_' + 'a' * 50


@pytest.fixture
def engine(tmp_path):
    documents=tmp_path/'Documents';documents.mkdir()
    observation={'platform':'windows','python_version':'3.14.8','python_verified':True,
        'wsl_app_version':'3.0.1','wslc_capability':{'state':'PASS'},'documents':str(documents),
        'existing_roots':{},'active_workloads':[],
        'volumes':[{'mount':str(tmp_path/'volume'),'fs':'NTFS','free_bytes':80*2**30,
                    'capacity_bytes':200*2**30,'device_id':'fixture','media_type':'SSD','bus_type':'NVMe'}]}
    return SetupEngine(FixtureAdapter(observation,tmp_path))


@pytest.mark.parametrize('case',['synthetic-pat','case-normalized','embedded-value'])
def test_logical_references_and_paths_reject_fine_grained_tokens(case,tmp_path):
    value={'synthetic-pat':TOKEN,'case-normalized':TOKEN.upper(),'embedded-value':'host.identity/'+TOKEN}[case]
    with pytest.raises(SetupError,match='REFERENCE_ONLY_NO_SECRET_VALUE'):reference(value)
    with pytest.raises(SetupError,match='REFERENCE_ONLY_NO_SECRET_VALUE'):safe_path(tmp_path/value)


@pytest.mark.parametrize('value',['host.github.machine','owner/repository#132','host.model.provider-1'])
def test_benign_logical_references_remain_accepted(value):
    assert reference(value)==value


@pytest.mark.parametrize('kind',['github','model'])
def test_plan_and_rehashed_imported_plan_cannot_materialize_tokens(engine,kind,tmp_path):
    observation=engine.probe()
    with pytest.raises(SetupError,match='REFERENCE_ONLY_NO_SECRET_VALUE'):
        engine.plan(observation,**{kind:{'ref':TOKEN}})
    clean=engine.plan(observation,overrides={'host_authorized':True})
    hostile=copy.deepcopy(clean);hostile[kind]['ref']=TOKEN
    hostile.pop('fingerprint');hostile['fingerprint']=digest(hostile)
    # Recomputing the public plan fingerprint cannot bypass a value guard.
    for action in (lambda:engine.context(hostile),lambda:engine.apply(hostile,approved=True)):
        with pytest.raises(SetupError,match='REFERENCE_ONLY_NO_SECRET_VALUE'):action()
    assert not Path(clean['host_agent']).exists()
    assert not Path(clean['roots']['config']['path']).exists()
    assert not list(tmp_path.rglob('receipt.json'))


@pytest.mark.parametrize('field',['account','provider','repo','work'])
def test_credential_metadata_drops_token_without_reusable_attestation(field):
    value=validated_metadata('github',{field:TOKEN,'owner_approved':True,'authenticated':True})
    leaked=TOKEN in json.dumps(value)
    assert not leaked,'Sensitive metadata must not escape the guard'
    assert not value['reusable'] and value['reason_code']=='SENSITIVE_METADATA_REJECTED'
    with pytest.raises(SetupError,match='UNSAFE_CREDENTIAL_METADATA'):
        SetupEngine._credential_metadata({'state':'AVAILABLE',field:TOKEN})


def test_probe_and_atomic_checkpoint_reject_before_writing(engine,tmp_path):
    engine.adapter.data['model']={'provider':TOKEN}
    with pytest.raises(SetupError,match='UNSAFE_PROBE_DATA'):engine.probe()
    target=tmp_path/'checkpoint.json'
    with pytest.raises(SetupError,match='REFERENCE_ONLY_NO_SECRET_VALUE'):
        atomic_json(target,{'metadata':{'account':TOKEN}})
    assert not target.exists() and not list(tmp_path.glob('checkpoint.json.new-*'))


@pytest.mark.parametrize('option',['--github-ref','--model-ref','--output','--sandbox'])
def test_cli_suppresses_synthetic_token_and_creates_no_durable_plan(tmp_path,option):
    fixture=Path(__file__).parent/'fixtures/windows-ready.json'
    sandbox=tmp_path/'fixture'
    output=tmp_path/'plan.json'
    args=[sys.executable,'-m','agent_setup','cli','plan','--fixture',str(fixture),
          '--sandbox',str(sandbox),'--output',str(output)]
    if option in {'--github-ref','--model-ref'}:args += [option,TOKEN]
    elif option=='--output':args[args.index(option)+1]=str(tmp_path/TOKEN/'plan.json')
    else:args[args.index(option)+1]=str(tmp_path/TOKEN)
    result=subprocess.run(args,capture_output=True,text=True,encoding='utf-8',timeout=30)
    assert result.returncode!=0
    leaked=TOKEN in result.stdout+result.stderr
    assert not leaked,'CLI must expose only a fixed refusal code'
    assert 'REFERENCE_ONLY_NO_SECRET_VALUE' in result.stdout
    assert not output.exists() and not (sandbox/'Documents/HOST_AGENT.md').exists()
    assert not list(tmp_path.rglob('receipt.json'))
