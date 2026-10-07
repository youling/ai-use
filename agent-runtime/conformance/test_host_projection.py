"""Host integration adversarial tests; use synthetic credentials only."""
import datetime as dt
import importlib.util
import io
import json
from pathlib import Path
import sys
import pytest

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

cred=load('credential_test',BASE/'conformance/github_credential.py')
launcher=load('launcher_test',BASE/'host/windows/launch.py')
projector=load('projector_test',BASE/'host/windows/project_github.py')
sys.modules['github_credential']=cred
recovery=load('recovery_test',BASE/'conformance/github_recovery.py')

@pytest.fixture
def projection(tmp_path,monkeypatch):
    monkeypatch.setenv('GITHUB_WORK','owner/repo#123')
    monkeypatch.setenv('GITHUB_REPOSITORY','owner/repo')
    p=tmp_path/'credential.json'
    value={'token':'synthetic-old','expires_at':(dt.datetime.now(dt.timezone.utc)+dt.timedelta(hours=1)).isoformat(),
           'work':'owner/repo#123','repo':'owner/repo','permissions':{'contents':'write','issues':'write'}}
    p.write_text(json.dumps(value))
    monkeypatch.setenv('GITHUB_CREDENTIAL_FILE',str(p))
    return p,value

def test_reopens_atomic_replacement_per_operation(projection):
    p,v=projection
    assert cred.current()['token']=='synthetic-old'
    v['token']='synthetic-new'
    other=p.with_suffix('.new')
    other.write_text(json.dumps(v))
    other.replace(p)
    assert cred.current()['token']=='synthetic-new'

@pytest.mark.parametrize('field,value',[('repo','foreign/repo'),('work','owner/repo#124'),('token','bad\nvalue'),('token',''),('permissions',{'contents':'write','issues':'write','administration':'write'})])
def test_foreign_or_malformed_projection_rejected(projection,field,value):
    p,v=projection
    v[field]=value
    p.write_text(json.dumps(v))
    with pytest.raises(ValueError):
        cred.current()

def test_expired_or_partial_projection_rejected(projection):
    p,v=projection
    v['expires_at']='2000-01-01T00:00:00Z'
    p.write_text(json.dumps(v))
    with pytest.raises(ValueError):
        cred.current()
    p.write_text('{')
    with pytest.raises(ValueError):
        cred.current()

@pytest.mark.parametrize('fields',['protocol=http\nhost=github.com\npath=owner/repo.git\n','protocol=https\nhost=evil.example\npath=owner/repo.git\n','protocol=https\nhost=github.com\npath=foreign/repo.git\n'])
def test_git_credential_does_not_leak_to_wrong_target(projection,monkeypatch,fields):
    out=io.StringIO()
    monkeypatch.setattr(sys,'argv',['helper','get'])
    monkeypatch.setattr(sys,'stdin',io.StringIO(fields))
    monkeypatch.setattr(sys,'stdout',out)
    with pytest.raises(ValueError):
        cred.main()
    assert out.getvalue()==''

@pytest.mark.parametrize('action',['store','erase'])
def test_git_store_never_persists_or_echoes_credentials(projection,monkeypatch,action):
    out=io.StringIO()
    monkeypatch.setattr(sys,'argv',['helper',action])
    monkeypatch.setattr(sys,'stdin',io.StringIO('password=synthetic-input\n'))
    monkeypatch.setattr(sys,'stdout',out)
    before=projection[0].read_bytes()
    cred.main()
    assert out.getvalue()=='' and projection[0].read_bytes()==before

def test_git_get_only_protocol_pipe(projection,monkeypatch):
    out=io.StringIO()
    monkeypatch.setattr(sys,'argv',['helper','get'])
    monkeypatch.setattr(sys,'stdin',io.StringIO('protocol=https\nhost=github.com\npath=owner/repo.git\n'))
    monkeypatch.setattr(sys,'stdout',out)
    cred.main()
    assert out.getvalue()=='username=x-access-token\npassword=synthetic-old\n\n'

def test_reparse_and_mount_injection_denied(tmp_path):
    with pytest.raises(ValueError):
        launcher.ordinary(tmp_path/'bad,readonly')
    target=tmp_path/'real'
    target.mkdir()
    link=tmp_path/'link'
    try:
        link.symlink_to(target,target_is_directory=True)
    except OSError:
        pytest.skip('symlink permission unavailable')
    with pytest.raises(ValueError):
        launcher.ordinary(link/'child')

def test_discovery_requires_enabled_v1_runtime(tmp_path):
    p=tmp_path/'HOST_AGENT.md'
    p.write_text('not a projection')
    with pytest.raises(ValueError):
        launcher.read_host(p)
    p.write_text('```yaml\nhost_agent_version: 1.0.0\nagents:\n  opencode:\n    enabled: false\n```')
    with pytest.raises(ValueError):
        launcher.read_host(p)

def test_projector_never_follows_redirect():
    with pytest.raises(RuntimeError):
        projector.NoRedirect().redirect_request(None,None,None,None,None,None)

def test_projector_rejects_scope_widening_before_file_output(tmp_path,monkeypatch):
    binding=tmp_path/'binding.json'
    binding.write_text(json.dumps({'app_id':1,'app_slug':'test','installation_id':2,
        'repo':'owner/repo','repo_id':3,'work':'owner/repo#123','private_key_ref':str(tmp_path/'host-key')}))
    target=tmp_path/'secret'
    target.mkdir()
    monkeypatch.setattr(sys,'argv',['helper','--binding',str(binding),'--mode','project','--directory',str(target)])
    monkeypatch.setattr(projector,'jwt',lambda _: 'synthetic-jwt')
    answers=iter([{'id':1,'slug':'test'},{'id':2,'app_id':1},
        {'token':'synthetic-token','permissions':{'contents':'write','issues':'write','administration':'write'}}])
    monkeypatch.setattr(projector,'request',lambda *a,**k: next(answers))
    with pytest.raises(ValueError):
        projector.main()
    assert not list(target.iterdir())

@pytest.mark.parametrize('field,value',[('issue',124),('phase','other'),('source_ref','--upload-pack=bad'),('canary_path','../escape'),('canary_path','/run/secrets/github/credential.json')])
def test_canary_work_authority_and_paths_rejected_before_io(field,value):
    spec={'issue':123,'work':'owner/repo#123','repo':'owner/repo','phase':'a',
        'source_sha':'a'*40,'nonce':'b'*16,'source_ref':'work/approved',
        'canary_path':'owned/canary.json','allowed_canary_path':'owned/canary.json'}
    spec[field]=value
    with pytest.raises(ValueError):
        recovery.validate_work(spec)
