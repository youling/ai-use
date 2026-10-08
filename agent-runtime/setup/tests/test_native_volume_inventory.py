"""Native metadata failures cannot manufacture capacity/media or readiness."""
import ctypes
import json
from types import SimpleNamespace
from unittest.mock import patch
import pytest
from agent_setup.windows import WindowsAdapter, native_volume_inventory
from agent_setup.engine import SetupEngine, FixtureAdapter

GIB=2**30


def kernel(*,mask=4,drive_type=3,fs='NTFS',available=30*GIB,total=80*GIB,free=40*GIB,volume_ok=True,space_ok=True):
    def volume(mount,name,n,serial,max_component,flags,buffer,length):
        buffer.value=fs
        return volume_ok
    def space(mount,a,t,f):
        a._obj.value=available;t._obj.value=total;f._obj.value=free
        return space_ok
    return SimpleNamespace(GetLogicalDrives=lambda:mask,GetDriveTypeW=lambda mount:drive_type,
                           GetVolumeInformationW=volume,GetDiskFreeSpaceExW=space)


def scan(api):
    with patch('agent_setup.windows.sys.platform','win32'),patch('agent_setup.windows._volume_kernel',return_value=api):
        return native_volume_inventory()


def test_actual_api_metadata_no_media_guess_and_available_user_quota():
    observed=scan(kernel())
    assert observed==[{'mount':'C:\\','fs':'NTFS','free_bytes':30*GIB,'capacity_bytes':80*GIB,
                      'device_id':'UNKNOWN','media_type':'UNKNOWN','bus_type':'UNKNOWN'}]
    assert observed[0]['free_bytes']!=40*GIB


@pytest.mark.parametrize('raw,expected',[('ntfs','NTFS'),('REFS','ReFS'),('Fat32','Fat32')])
def test_native_filesystem_case_normalization_keeps_unsupported_labels(raw,expected):
    assert scan(kernel(fs=raw))[0]['fs']==expected


@pytest.mark.parametrize('inputs',[{'mask':0},{'drive_type':2},{'drive_type':4},{'drive_type':5},
    {'volume_ok':False},{'space_ok':False},{'fs':''},{'total':0},{'available':81*GIB},{'free':81*GIB}])
def test_invalid_absent_nonfixed_or_capacity_metadata_never_admitted(inputs):
    assert scan(kernel(**inputs))==[]


def test_native_api_load_failure_and_nonwindows_remain_unknown():
    with patch('agent_setup.windows.sys.platform','win32'),patch('agent_setup.windows._volume_kernel',side_effect=OSError('private error detail')):
        assert native_volume_inventory()==[]
    with patch('agent_setup.windows.sys.platform','linux'),patch('agent_setup.windows._volume_kernel',side_effect=AssertionError('No native command')):
        assert native_volume_inventory()==[]


def probe(raw,fallback):
    def runner(argv,**kwargs):
        return SimpleNamespace(returncode=0,stdout=json.dumps(raw if '-File' in argv else {'status':'Valid','psf_signer':True}))
    with patch('agent_setup.windows.sys.platform','win32'),patch('agent_setup.windows.shutil.which',return_value='fixture-powershell'),patch('agent_setup.windows.documents_known_folder',return_value=None),patch('agent_setup.windows.native_volume_inventory',side_effect=fallback):
        return WindowsAdapter(runner=runner).probe()


def test_complete_ps_inventory_is_retained_without_calling_fallback():
    volume=scan(kernel())
    volume[0].update(media_type='SSD',bus_type='NVMe',device_id='disk-0')
    observation=probe({'volumes':volume},lambda:pytest.fail('Valid richer PS inventory must not be overwritten'))
    assert observation['volumes']==volume
    assert observation['inventory_source']=='WINDOWS_POWERSHELL'


def test_one_valid_ps_volume_is_retained_even_when_another_is_incomplete():
    valid=scan(kernel())
    invalid={'mount':'D:\\','fs':'NTFS','free_bytes':None,'capacity_bytes':80*GIB}
    observation=probe({'volumes':[*valid,invalid]},lambda:pytest.fail('A valid PS volume is already observed'))
    assert observation['volumes']==valid
    assert observation['inventory_source']=='WINDOWS_POWERSHELL'


@pytest.mark.parametrize('raw',[{}, {'volumes':[]}, {'volumes':[{'mount':'C:\\','fs':'NTFS','free_bytes':None}]}])
def test_absent_or_invalid_ps_volume_inventory_uses_real_native_projection(raw):
    volume=scan(kernel())
    observation=probe(raw,lambda:volume)
    assert observation['volumes']==volume
    assert observation['inventory_source']=='WINDOWS_WIN32_FALLBACK'
    assert observation['python_verified'] is True
    assert observation['wslc_capability']['state']!='PASS'


def test_empty_native_fallback_does_not_create_capacity_or_success():
    observation=probe({},lambda:[])
    assert observation['volumes']==[]
    assert observation['storage_state']=='UNKNOWN'
    assert observation['inventory_source']=='UNVERIFIED'


@pytest.mark.parametrize('runtime',[{'volumes':[]}, {'wsl_version_text':'WSL version: 3.0.1.0','wslc_state':'PASS','wslc_active_count':True}])
def test_runtime_seam_cannot_override_inventory_or_accept_invalid_types(runtime):
    with patch('agent_setup.windows.sys.platform','win32'),patch('agent_setup.windows.shutil.which',return_value=None),patch('agent_setup.windows.trusted_windows_powershell',return_value=None),patch('agent_setup.windows.native_volume_inventory',return_value=[]):
        adapter=WindowsAdapter(apply_authorized=True,known_folder_resolver=lambda:None,runtime_capability_resolver=lambda:runtime)
        observation=adapter.probe()
    assert observation['volumes']==[]
    assert observation['runtime_inventory_source']=='UNVERIFIED'
    assert observation['wslc_capability']['state']=='UNKNOWN'
    assert adapter.can_apply is False and adapter.apply_authorized is False


@pytest.mark.parametrize('fs,free,ready',[('FAT32',30*GIB,False),('NTFS',7*GIB,False),('NTFS',30*GIB,True),('ReFS',30*GIB,True)])
def test_fallback_preserves_filesystem_headroom_and_owner_gates(tmp_path,fs,free,ready):
    native=scan(kernel(fs=fs,available=free))
    # Fixture mount confines plan-only reads to the task-owned sandbox; all
    # capacity/filesystem/media fields still come through the native API seam.
    native[0]['mount']=str(tmp_path)
    docs=tmp_path/'Documents';docs.mkdir()
    observation={'platform':'windows','python_version':'3.14.8','python_verified':True,
        'wsl_app_version':'3.0.1','wslc_capability':{'state':'PASS'},'documents':str(docs),
        'existing_roots':{},'active_workloads':[],'volumes':native}
    engine=SetupEngine(FixtureAdapter(observation,tmp_path));plan=engine.plan(engine.probe())
    assert (plan['status']=='READY') is ready
    assert next(g['state'] for g in plan['gates'] if g['code']=='STORAGE_CAPACITY')==('PASS' if ready else 'BLOCKED')
    assert not (tmp_path/'AgentRuntime').exists()
