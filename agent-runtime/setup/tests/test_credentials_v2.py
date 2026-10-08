"""No credentials are read or minted by these synthetic adversarial tests."""
from datetime import datetime, timezone, timedelta
import json
from types import SimpleNamespace
from unittest.mock import patch
from agent_setup.windows import WindowsAdapter
from agent_setup.credentials import validated_metadata


def proof(kind='github'):
    return dict(owner_approved=True, authenticated=True, revoked=False, bounded_projection=True,
                account='synthetic-user', provider='GitHub', expires_at=(datetime.now(timezone.utc)+timedelta(minutes=5)).isoformat(),
                repo='example/repo', work='example/repo#1', permissions={'contents':'write','issues':'write'}, repository_scope=['example/repo'],
                provider_verified=True, model_verified=True)

def test_discovered_fake_gh_is_not_executed_or_reusable():
    with patch('agent_setup.windows.shutil.which',return_value='/untrusted/gh.exe'):
        a=WindowsAdapter(runner=lambda *a,**k: (_ for _ in ()).throw(AssertionError('untrusted executable')))
        value=a.discover_credentials()
        assert value['github']['state']=='REUSE_NOT_SUPPORTED'
        assert not value['github']['reusable']

def test_expiry_scope_permission_and_revocation_counterexamples():
    for change in ({'expires_at':'2000-01-01T00:00:00Z'}, {'permissions':{'contents':'read'}},
                   {'work':'other/repo#1'}, {'repository_scope':['other/repo']}, {'revoked':True},
                   {'owner_approved':'true'}, {'bounded_projection':False}):
        assert not validated_metadata('github',{**proof(),**change})['reusable']
    assert validated_metadata('github',proof())['reusable']
    assert not validated_metadata('model',{**proof(), 'model_verified':False})['reusable']

def test_consent_host_gate_and_revocation_are_fresh():
    class Custodian:
        revoked=False
        def discover(self,kind):return {**proof(kind), 'revoked':self.revoked}
        def connect(self,kind,mode='auto'):return self.discover(kind)
    owner=Custodian()
    # Model a Windows adapter without switching POSIX shutil into WinAPI calls.
    with patch('agent_setup.windows.sys.platform','win32'), patch('agent_setup.windows.shutil.which',return_value=None):
        a=WindowsAdapter(credential_custodian=owner)
        assert a.connect_credential('github')['state']=='NOT_AUTHORIZED'
        assert a.connect_credential('github',approved=True)['state']=='HUMAN_GATE'
        a.apply_authorized=True
        assert a.connect_credential('github',approved=True)['state']=='CONNECTION_PENDING_PROJECTION'
        owner.revoked=True
        assert not a.connect_credential('github',approved=True)['reusable']
        assert a.connect_credential('model','manual',True)['state']=='NEEDS_CONNECTION'

def test_metadata_drops_raw_secret_unrecognized_values():
    raw={**proof(),'token':'synthetic-secret','account':'ghp_'+'a'*40,'private_key':'secret'}
    value=validated_metadata('github',raw)
    assert 'synthetic-secret' not in json.dumps(value)
    assert 'ghp_' not in json.dumps(value)
    assert 'private_key' not in value
