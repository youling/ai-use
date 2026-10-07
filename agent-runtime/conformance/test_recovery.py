"""Real local Git + inert durable Issue fixture; no network or real identity."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

BASE=Path(__file__).parent
spec=importlib.util.spec_from_file_location('github_credential',BASE/'github_credential.py')
credential=importlib.util.module_from_spec(spec)
spec.loader.exec_module(credential)
sys.modules['github_credential']=credential
spec=importlib.util.spec_from_file_location('recovery_fixture',BASE/'github_recovery.py')
client=importlib.util.module_from_spec(spec)
spec.loader.exec_module(client)

def test_fresh_runtime_recovers_durable_git_and_issue(tmp_path,monkeypatch):
    def gitrun(*args,cwd=None):
        return subprocess.check_output(['git',*args],cwd=cwd,text=True,stderr=subprocess.PIPE).strip()
    remote=tmp_path/'remote.git'
    gitrun('init','--bare',str(remote))
    seed=tmp_path/'seed'
    gitrun('init',str(seed))
    (seed/'owned').mkdir()
    (seed/'owned/base.txt').write_text('inert public fixture\n')
    gitrun('add','.',cwd=seed)
    gitrun('-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-m','fixture',cwd=seed)
    source=gitrun('rev-parse','HEAD',cwd=seed)
    gitrun('push',str(remote),'HEAD:refs/heads/work/approved',cwd=seed)
    issue_store=tmp_path/'issue.json'
    issue_store.write_text('[]')
    host=b'host_agent_version: 1.0.0\nrecovery_required: true\n'
    import hashlib
    work={'repo':'owner/repo','work':'owner/repo#123','issue':123,'phase':'a',
        'source_sha':source,'source_ref':'work/approved','nonce':'b'*16,
        'canary_path':'owned/canary.json','allowed_canary_path':'owned/canary.json',
        'host_agent_sha256':hashlib.sha256(host).hexdigest()}
    observed=[]
    current_workspace=None
    current_input=None
    current_output=None
    host_path=tmp_path/'HOST_AGENT.md'
    host_path.write_bytes(host)
    def projected_path(value):
        s=str(value)
        if s.startswith('/workspace'):
            return current_workspace/s.removeprefix('/workspace').lstrip('/')
        if s=='/exchange/in/work.json':
            return current_input/'work.json'
        if s.startswith('/exchange/out/'):
            return current_output/Path(s).name
        if s=='/host-context/HOST_AGENT.md':
            return host_path
        if s.startswith('/home/foreman/'):
            return current_workspace/'empty-home'/Path(s).name
        return Path(value)
    def git_transport(*args):
        argv=list(args)
        if argv[0]=='clone':
            argv=[str(remote) if s=='https://github.com/owner/repo.git' else s for s in argv]
        return gitrun(*argv,cwd=current_workspace)
    def api_transport(path,body=None,method=None):
        observed.append((work['phase'],path,method))
        if path=='':
            return {'private':True}
        if path=='/issues/123':
            return {'number':123,'state':'open'}
        if path.startswith('/issues/123/comments'):
            rows=json.loads(issue_store.read_text())
            if body:
                row={'id':len(rows)+1,'body':body['body'],'html_url':'https://example.invalid/checkpoint/'+str(len(rows)+1),'user':{'login':'fixture[bot]'}}
                rows.append(row)
                issue_store.write_text(json.dumps(rows))
                return row
            return rows
        prefix='/git/ref/heads/'
        if path.startswith(prefix):
            return {'object':{'sha':gitrun('rev-parse','refs/heads/'+path[len(prefix):],cwd=remote)}}
        if method=='DELETE' and path.startswith('/git/refs/heads/'):
            gitrun('update-ref','-d','refs/heads/'+path.removeprefix('/git/refs/heads/'),cwd=remote)
            return {}
        raise AssertionError('unexpected API path '+path)
    generations=iter(['a','b'])
    monkeypatch.setattr(client,'current',lambda: {'generation':next(generations)})
    monkeypatch.setattr(client,'api',api_transport)
    monkeypatch.setattr(client,'git',git_transport)
    monkeypatch.setattr(client,'Path',projected_path)
    monkeypatch.setattr(client.time,'sleep',lambda _: None)
    monkeypatch.setattr(client.os,'getuid',lambda:1000,raising=False)
    receipts=[]
    for phase in ['a','b']:
        work['phase']=phase
        current_workspace=tmp_path/('runtime-'+phase)
        current_input=tmp_path/('input-'+phase)
        current_output=tmp_path/('output-'+phase)
        for p in [current_workspace,current_input,current_output]:
            p.mkdir()
        current_input.joinpath('work.json').write_text(json.dumps(work))
        assert list(current_workspace.iterdir())==[]
        client.main()
        receipts.append(json.loads((current_output/('receipt-'+phase+'.json')).read_text()))
        assert current_workspace.resolve().is_relative_to(tmp_path.resolve())
        if os.name=='nt':
            for owned in current_workspace.rglob('*'):
                if owned.is_file():owned.chmod(0o600)
        shutil.rmtree(current_workspace)
    assert receipts[0]['live_atomic_refresh_visible']
    assert receipts[1]['fresh_recovery'] and receipts[1]['canary_sha']==receipts[0]['canary_sha']
    assert receipts[1]['owned_branch_deleted_after_durable_readback']
    assert not receipts[1]['prior_session_db_required']
    assert len(json.loads(issue_store.read_text()))==2
    assert gitrun('show-ref','--heads',cwd=remote).splitlines()==[source+' refs/heads/work/approved']
