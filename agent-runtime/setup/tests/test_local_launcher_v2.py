"""Existing launcher local profile, with only synthetic subprocess/owner data."""
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import yaml
import pytest
from agent_setup.windows import PINNED_IMAGE, WindowsAdapter

SPEC=importlib.util.spec_from_file_location('setup_local_launch',Path(__file__).resolve().parents[2]/'host/windows/launch.py')
launch=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(launch)
CONFIG='sha256:'+'a'*64

def fixture(tmp_path):
    incoming=tmp_path/'in';outgoing=tmp_path/'out';temp=tmp_path/'temp'
    for root in (incoming,outgoing,temp):root.mkdir()
    host=tmp_path/'HOST_AGENT.md'
    context={'host_agent_version':'1.0.0','agents':{'opencode':{'enabled':False,'image':CONFIG,'github':{'recovery_required':True}}},
             'paths':{'temp':{'path':str(temp)},'exchange':{'in':str(incoming),'out':str(outgoing)}}}
    host.write_text('```yaml\n'+yaml.safe_dump(context)+'```\n',encoding='utf-8')
    args=['launch','--host-agent',str(host),'--wslc','synthetic-wslc','--name','setup-fixture','--attempt',str(temp/'attempt'),
          '--input',str(incoming),'--output',str(outgoing),'--local-only']
    return host,args,temp/'attempt'


def mount_evidence(args, attempt):
    sources={'/host-context':str(attempt/'context'), '/exchange/in':args[args.index('--input')+1],
             '/exchange/out':args[args.index('--output')+1]}
    return sources,[{'Destination':name,'Type':'bind','Source':source,'RW':name=='/exchange/out'}
                    for name,source in sources.items()]

def test_local_profile_uses_existing_launcher_no_external_mount_or_host_publish(tmp_path,capsys):
    host,args,attempt=fixture(tmp_path);calls=[]
    def run(argv,**kwargs):
        calls.append(argv)
        if argv[1]=='inspect':return SimpleNamespace(returncode=0,stdout=json.dumps([{'Id':CONFIG,'RepoDigests':[PINNED_IMAGE]}]))
        return SimpleNamespace(returncode=0,stdout='')
    with patch.object(launch.subprocess,'run',side_effect=run),patch('sys.argv',args),patch.object(launch,'local_server_auth',return_value=attempt/'auth/server.env'):
        launch.main()
    actual=calls[-1]
    assert '--network' in actual and actual[actual.index('--network')+1]=='none'
    assert '--publish' not in actual and '--user' in actual
    assert actual[actual.index('--hostname')+1]=='127.0.0.1'
    assert '/run/secrets/github' not in ' '.join(actual)
    assert not (attempt/'credential.json').exists()
    assert json.loads(capsys.readouterr().out)['local_only']
    assert not launch.read_host(host,local_only=True)['agents']['opencode']['enabled']
    with pytest.raises(ValueError,match='PROJECTION_DISABLED'):launch.read_host(host)

def test_wrong_manifest_and_reparse_injection_stop_before_attempt(tmp_path):
    _,args,attempt=fixture(tmp_path)
    with patch.object(launch.subprocess,'run',return_value=SimpleNamespace(returncode=0,stdout=json.dumps([{'Id':CONFIG,'RepoDigests':[]}]))),patch('sys.argv',args):
        with pytest.raises(ValueError,match='RELEASED_LOCAL_IMAGE'):launch.main()
    assert not attempt.exists()
    for path in ('bad,root','bad\nroot','../root'):
        with pytest.raises(ValueError):launch.ordinary(path)

def test_local_auth_secret_never_in_receipt_argv_or_context(tmp_path):
    if launch.os.name=='nt':pytest.skip('Synthetic POSIX custody mode; Windows ACL protocol separately tested')
    target=launch.local_server_auth(tmp_path)
    assert target.stat().st_mode & 0o077 == 0
    assert target.parent.stat().st_mode & 0o077 == 0
    assert target.name=='server.env'
    # Test metadata/existence only; deliberately never read generated contents.

def test_local_auth_acl_unverified_fails_before_secret_file(tmp_path):
    proxy=SimpleNamespace(name='nt',open=launch.os.open,fdopen=launch.os.fdopen,O_WRONLY=launch.os.O_WRONLY,O_CREAT=launch.os.O_CREAT,O_EXCL=launch.os.O_EXCL)
    with patch.object(launch,'os',proxy),patch.object(launch,'trusted_windows_powershell',return_value='synthetic-os-powershell'),patch.object(launch.subprocess,'run',return_value=SimpleNamespace(returncode=0,stdout='{"protected":false}')):
        with pytest.raises(ValueError,match='CUSTODY_UNVERIFIED'):launch.local_server_auth(tmp_path)
    assert not (tmp_path/'auth/server.env').exists()


@pytest.mark.parametrize('output',['[]','null','{"protected":1}','not-json','{"protected":false}'])
def test_native_ps5_acl_invalid_evidence_never_writes_auth(tmp_path,output):
    proxy=SimpleNamespace(name='nt',open=launch.os.open,fdopen=launch.os.fdopen,O_WRONLY=launch.os.O_WRONLY,O_CREAT=launch.os.O_CREAT,O_EXCL=launch.os.O_EXCL)
    calls=[]
    def run(argv,**kwargs):
        calls.append((argv,kwargs))
        return SimpleNamespace(returncode=0,stdout=output)
    with patch.object(launch,'os',proxy),patch.object(launch,'trusted_windows_powershell',return_value='WindowsPowerShell-v1.0'),patch.object(launch.subprocess,'run',side_effect=run):
        with pytest.raises(ValueError,match='CUSTODY_UNVERIFIED'):launch.local_server_auth(tmp_path)
    assert not (tmp_path/'auth/server.env').exists()
    assert calls[0][0][0]=='WindowsPowerShell-v1.0'
    assert calls[0][1]['encoding']=='utf-8'
    assert '[Console]::InputEncoding' in calls[0][0][-1]

def test_verification_requires_local_network_uid_scope_and_api_auth(tmp_path):
    host,args,attempt=fixture(tmp_path)
    sources,mounts=mount_evidence(args,attempt)
    import hashlib
    info={'Image':CONFIG,'Config':{'User':'1000:1000','Labels':{'agent.attempt':'setup-fixture','agent.setup.profile':'local-only'}},'HostConfig':{'NetworkMode':'none','PortBindings':{}},'Mounts':mounts}
    for denied,authenticated,state in [(True,True,'PASS'),(False,True,'NOT_VERIFIED'),(True,False,'NOT_VERIFIED')]:
        results=iter([SimpleNamespace(returncode=0,stdout=json.dumps([info])),SimpleNamespace(returncode=0,stdout=json.dumps({'uid':1000,'hash':hashlib.sha256(host.read_bytes()).hexdigest()})),SimpleNamespace(returncode=0,stdout=json.dumps({'denied':denied,'authenticated':authenticated}))])
        with patch('agent_setup.windows.sys.platform','win32'),patch('agent_setup.windows.shutil.which',return_value='synthetic-wslc'):
            observed=WindowsAdapter(runner=lambda *a,**k:next(results)).verify_runtime('setup-fixture',host,expected_config_id=CONFIG,expected_local=True,expected_mount_sources=sources)
        assert observed['server_authenticated']==state
    for bad in ({'Config':{'User':'1000','Labels':{'agent.attempt':'setup-fixture'}}},{'HostConfig':{'NetworkMode':'default'}}):
        mutated={**info,**bad}
        responses=iter([SimpleNamespace(returncode=0,stdout=json.dumps([mutated])),SimpleNamespace(returncode=0,stdout=json.dumps({'uid':1000,'hash':hashlib.sha256(host.read_bytes()).hexdigest()}))])
        with patch('agent_setup.windows.sys.platform','win32'),patch('agent_setup.windows.shutil.which',return_value='synthetic-wslc'):
            assert WindowsAdapter(runner=lambda *a,**k:next(responses)).verify_runtime('setup-fixture',host,expected_config_id=CONFIG,expected_local=True,expected_mount_sources=sources)['state']=='BLOCKED'

def test_synthetic_windows_custody_protects_before_auth_generation(tmp_path):
    proxy=SimpleNamespace(name='nt',open=launch.os.open,fdopen=launch.os.fdopen,O_WRONLY=launch.os.O_WRONLY,O_CREAT=launch.os.O_CREAT,O_EXCL=launch.os.O_EXCL)
    events=[]
    def protect(argv,**kwargs):
        events.append('acl')
        assert 'server.env' not in kwargs['input']
        return SimpleNamespace(returncode=0,stdout='{"protected":true}')
    def generate(*a):
        events.append('generate')
        return 'SYNTHETIC_TEST_VALUE'
    with patch.object(launch,'os',proxy),patch.object(launch,'trusted_windows_powershell',return_value='synthetic-os-powershell'),patch.object(launch.subprocess,'run',side_effect=protect),patch.object(launch.secrets,'token_urlsafe',side_effect=generate):
        path=launch.local_server_auth(tmp_path)
    assert events==['acl','generate']
    assert path.is_file()

def test_adapter_local_start_needs_authority_and_metadata_binding(tmp_path):
    host,args,attempt=fixture(tmp_path)
    plan={'runtime':{'name':'setup-fixture','attempt':str(attempt),'incoming':args[args.index('--input')+1],'outgoing':args[args.index('--output')+1]}}
    assert WindowsAdapter().start_local_runtime(plan,host)['state']=='NOT_AUTHORIZED'
    import hashlib
    metadata={'started':True,'name':'setup-fixture','image':CONFIG,'host_agent_sha256':hashlib.sha256(host.read_bytes()).hexdigest(),'local_only':True,'network':'none','scoped_auth':True}
    calls=[]
    for override,expected in [({},'READY'),({'network':'default'},'BLOCKED'),({'host_agent_sha256':'0'*64},'BLOCKED')]:
        def run(argv,**kwargs):
            calls.append(argv)
            return SimpleNamespace(returncode=0,stdout=json.dumps({**metadata,**override}))
        with patch('agent_setup.windows.sys.platform','win32'),patch('agent_setup.windows.shutil.which',return_value='synthetic-wslc'):
            assert WindowsAdapter(apply_authorized=True,runner=run).start_local_runtime(plan,host)['state']==expected
        assert '--local-only' in calls[-1] and '--github-projection' not in calls[-1]

def test_full_profile_rejects_credential_exchange_same_directory(tmp_path):
    host,args,attempt=fixture(tmp_path)
    text=host.read_text(encoding='utf-8').replace('enabled: false','enabled: true')
    host.write_text(text,encoding='utf-8')
    incoming=Path(args[args.index('--input')+1])
    (incoming/'credential.json').write_text('{}',encoding='utf-8')
    args.remove('--local-only');args.extend(['--github-projection',str(incoming)])
    with patch('sys.argv',args),patch.object(launch.subprocess,'run',side_effect=AssertionError('No command on overlapping projection')):
        with pytest.raises(ValueError,match='PROJECTION_OVERLAP'):launch.main()
    assert not attempt.exists()

def test_local_verification_rejects_secret_or_writable_context_mount(tmp_path):
    host,args,attempt=fixture(tmp_path)
    sources,mounts=mount_evidence(args,attempt)
    import hashlib
    for changed in ([*mounts,{'Destination':'/run/secrets/github','Type':'bind','RW':False}], [{**mounts[0],'RW':True},*mounts[1:]]):
        info={'Image':CONFIG,'Config':{'User':'1000:1000','Labels':{'agent.attempt':'setup-fixture','agent.setup.profile':'local-only'}},'HostConfig':{'NetworkMode':'none','PortBindings':{}},'Mounts':changed}
        results=iter([SimpleNamespace(returncode=0,stdout=json.dumps([info])),SimpleNamespace(returncode=0,stdout=json.dumps({'uid':1000,'hash':hashlib.sha256(host.read_bytes()).hexdigest()}))])
        with patch('agent_setup.windows.sys.platform','win32'),patch('agent_setup.windows.shutil.which',return_value='synthetic-wslc'):
            assert WindowsAdapter(runner=lambda *a,**k:next(results)).verify_runtime('setup-fixture',host,expected_config_id=CONFIG,expected_local=True,expected_mount_sources=sources)['reason']=='LOCAL_MOUNT_BOUNDARY_UNVERIFIED'


@pytest.mark.parametrize('case', ['missing','null','empty','not-list','non-object','duplicate','missing-mode',
    'integer-mode','string-mode','missing-source','relative-source','wrong-source','bad-type','bad-destination',
    'extra-secret','extra-root','writable-context','writable-input','readonly-output','missing-expected-sources'])
def test_local_mount_evidence_fails_closed_before_any_container_exec(tmp_path,case):
    host,args,attempt=fixture(tmp_path)
    sources,mounts=mount_evidence(args,attempt)
    if case=='null':mounts=None
    elif case=='empty':mounts=[]
    elif case=='not-list':mounts={'mounts':mounts}
    elif case=='non-object':mounts[0]=None
    elif case=='duplicate':mounts[1]=dict(mounts[0])
    elif case=='missing-mode':mounts[0].pop('RW')
    elif case=='integer-mode':mounts[0]['RW']=0
    elif case=='string-mode':mounts[0]['RW']='false'
    elif case=='missing-source':mounts[0].pop('Source')
    elif case=='relative-source':mounts[0]['Source']='relative/context'
    elif case=='wrong-source':mounts[0]['Source']=str(tmp_path/'foreign-context')
    elif case=='bad-type':mounts[0]['Type']='volume'
    elif case=='bad-destination':mounts[0]['Destination']=['/host-context']
    elif case=='extra-secret':mounts.append({'Destination':'/run/secrets/github','Type':'bind','Source':str(tmp_path/'secret'),'RW':False})
    elif case=='extra-root':mounts.append({'Destination':'/','Type':'bind','Source':str(tmp_path),'RW':True})
    elif case=='writable-context':mounts[0]['RW']=True
    elif case=='writable-input':mounts[1]['RW']=True
    elif case=='readonly-output':mounts[2]['RW']=False
    elif case=='missing-expected-sources':sources=None
    info={'Image':CONFIG,'Config':{'User':'1000:1000','Labels':{'agent.attempt':'setup-fixture','agent.setup.profile':'local-only'}},'HostConfig':{'NetworkMode':'none','PortBindings':{}}}
    if case!='missing':info['Mounts']=mounts
    calls=[]
    def run(argv,**kwargs):
        calls.append(argv)
        assert argv[1]=='inspect','Unproven mounts must stop before exec/authentication'
        return SimpleNamespace(returncode=0,stdout=json.dumps([info]))
    with patch('agent_setup.windows.sys.platform','win32'),patch('agent_setup.windows.shutil.which',return_value='synthetic-wslc'):
        observed=WindowsAdapter(runner=run).verify_runtime('setup-fixture',host,expected_config_id=CONFIG,expected_local=True,expected_mount_sources=sources)
    assert observed=={'state':'BLOCKED','reason':'LOCAL_MOUNT_BOUNDARY_UNVERIFIED'}
    assert len(calls)==1
