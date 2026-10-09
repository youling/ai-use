"""Frozen integration rejects distribution shortcuts using synthetic metadata."""
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import pytest

from agent_setup.windows import WindowsAdapter, PINNED_IMAGE, frozen_provenance
from agent_setup.engine import SetupEngine, FixtureAdapter, SetupError


@pytest.mark.parametrize('proof', [
    {'state': 'VERIFIED_CONTENT_UNSIGNED_TEST_ONLY', 'bundle_verified': True, 'python_verified': False},
    {'state': 'BUNDLE_UNVERIFIED', 'python_verified': False},
    # Even a fabricated flag cannot create release authority in this candidate.
    {'state': 'VERIFIED_CONTENT_UNSIGNED_TEST_ONLY', 'python_verified': True},
])
def test_frozen_apply_flag_never_promotes_unsigned_distribution(proof):
    with patch.object(sys, 'frozen', True, create=True), patch.object(sys, 'platform', 'win32'), patch('agent_setup.windows.shutil.which', return_value=None):
        adapter = WindowsAdapter(apply_authorized=True, runner=lambda *a, **k: pytest.fail('Must not mutate'))
        with patch('agent_setup.windows.frozen_provenance', return_value=proof):
            assert adapter.apply_authorized is False
            assert adapter.pull_image(PINNED_IMAGE)['state'] == 'NOT_AUTHORIZED'
            assert adapter.start_local_runtime({}, Path('not-read'))['state'] == 'NOT_AUTHORIZED'
            assert adapter.connect_credential('github', approved=True)['state'] == 'HUMAN_GATE'


def test_frozen_probe_never_checks_exe_as_psf_python_or_uses_path_powershell():
    calls=[]
    def run(argv, **kwargs):
        calls.append(argv)
        return SimpleNamespace(returncode=0, stdout=json.dumps({'volumes':[]}))
    package=SimpleNamespace(verified_bundle_root=lambda: Path('/verified-bundle'))
    proof={'state':'VERIFIED_CONTENT_UNSIGNED_TEST_ONLY','bundle_verified':True,'python_verified':False}
    with patch.object(sys,'frozen',True,create=True), patch.object(sys,'platform','win32'), patch.dict(sys.modules,{'agent_setup.packaging':package}), patch('agent_setup.windows.frozen_provenance',return_value=proof), patch('agent_setup.windows.trusted_windows_powershell',return_value='OS-provided-powershell'), patch('agent_setup.windows.documents_known_folder',return_value=None), patch('agent_setup.windows.shutil.which',return_value='untrusted-pwsh'):
        observed=WindowsAdapter(runner=run).probe()
    assert observed['python_verified'] is False
    assert observed['runtime_provenance']==proof
    assert len(calls)==1 and calls[0][0]=='OS-provided-powershell'
    assert calls[0][-1]==str(Path('/verified-bundle/agent_setup/probe_windows.ps1'))
    assert '-Command' not in calls[0]


@pytest.mark.parametrize('state,bundle,python,expected', [
    ('VERIFIED_CONTENT_UNSIGNED_TEST_ONLY',True,True,True),
    ('BUNDLE_UNVERIFIED',True,True,False),
    ('VERIFIED_CONTENT_UNSIGNED_TEST_ONLY',False,True,False),
    ('VERIFIED_CONTENT_UNSIGNED_TEST_ONLY',True,False,False),
])
def test_embedded_python_content_proof_is_distinct_from_host_distribution(state,bundle,python,expected):
    proof={'state':state,'bundle_verified':bundle,'python_verified':python,
           'distribution_trust':'UNSIGNED_TEST_ONLY','publisher_trusted':False}
    class Version:
        releaselevel='final'
        def __getitem__(self,key):return (3,14)
    with patch.object(sys,'frozen',True,create=True),patch.object(sys,'platform','win32'),patch.object(sys,'version_info',Version()),patch('agent_setup.windows.frozen_provenance',return_value=proof),patch('agent_setup.windows.documents_known_folder',return_value=None),patch('agent_setup.windows.trusted_windows_powershell',return_value=None),patch('agent_setup.windows.shutil.which',return_value=None):
        adapter=WindowsAdapter(apply_authorized=True)
        observed=adapter.probe()
    assert observed['python_verified'] is expected
    assert adapter.apply_authorized is False


def test_missing_bundle_policy_fails_closed_and_script_is_distinct():
    with patch.object(sys,'frozen',True,create=True), patch.dict(sys.modules,{'agent_setup.packaging':None}):
        assert frozen_provenance()['state']=='BUNDLE_UNVERIFIED'
    with patch.object(sys,'frozen',False,create=True):
        assert frozen_provenance()['state']=='SCRIPT_MODE'


def test_frozen_launcher_dispatch_uses_fixed_internal_mode_and_verified_root():
    seen=[]
    package=SimpleNamespace(verified_bundle_root=lambda: seen.append(True))
    with patch.object(sys,'frozen',True,create=True), patch.dict(sys.modules,{'agent_setup.packaging':package}):
        argv=WindowsAdapter._launcher_command()
    assert seen==[True]
    assert argv==[sys.executable,'--launcher-dispatch']


def test_frozen_resource_tampering_prevents_launcher_dispatch():
    def reject():raise RuntimeError('BUNDLE_RESOURCE_HASH_MISMATCH')
    with patch.object(sys,'frozen',True,create=True), patch.dict(sys.modules,{'agent_setup.packaging':SimpleNamespace(verified_bundle_root=reject)}):
        with pytest.raises(RuntimeError,match='HASH_MISMATCH'):WindowsAdapter._launcher_command()


def test_unsigned_frozen_direct_engine_apply_denied_before_any_host_write(tmp_path):
    docs=tmp_path/'Documents';docs.mkdir()
    observation={'platform':'windows','python_version':'3.14.8','python_verified':True,'wsl_app_version':'3.0.1.0',
        'wslc_capability':{'state':'PASS'},'documents':str(docs),'existing_roots':{},'active_workloads':[],
        'volumes':[{'mount':str(tmp_path/'volume'),'fs':'NTFS','free_bytes':80*1024**3,'capacity_bytes':200*1024**3,'device_id':'fixture','media_type':'SSD','bus_type':'NVMe'}]}
    source=SetupEngine(FixtureAdapter(observation,tmp_path))
    plan=source.plan(source.probe(),overrides={'host_authorized':True,'runtime':False})
    assert plan['status']=='READY'
    with patch.object(sys,'frozen',True,create=True),patch.object(sys,'platform','win32'):
        engine=SetupEngine(WindowsAdapter(apply_authorized=True,runner=lambda *a,**k:pytest.fail('No command authorized')))
        with pytest.raises(SetupError,match='UNSUPPORTED_PLATFORM'):engine.apply(plan,approved=True)
    assert list(tmp_path.iterdir())==[docs]
    assert not Path(plan['host_agent']).exists()
