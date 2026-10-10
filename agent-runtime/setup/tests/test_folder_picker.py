"""No real dialogs/Host browse in synthetic COM ownership and STA tests."""
import ctypes
import threading
from unittest.mock import patch
import pytest
from agent_setup import folder_picker as picker

class FakeDialog:
    def __init__(self,*,initialize=0,show=0,result='C:\\Public Synthetic\\文件夹',fail=None):
        self.init_hr=initialize;self.show_hr=show;self.selected=result;self.fail=fail;self.calls=[]
    def record(self,name):
        self.calls.append((name,threading.get_ident()))
        if name==self.fail:raise OSError('private path or native detail must not escape')
    def initialize(self):self.record('initialize');return self.init_hr
    def uninitialize(self):self.record('uninitialize')
    def create(self):self.record('create');return 'OWNED_DIALOG'
    def private_history(self,dialog):assert dialog=='OWNED_DIALOG';self.record('private_history')
    def clear_history(self,dialog):assert dialog=='OWNED_DIALOG';self.record('clear_history');return True
    def options(self,dialog):assert dialog=='OWNED_DIALOG';self.record('options')
    def title(self,dialog,title):self.record('title')
    def initial(self,dialog,path):self.record('initial')
    def show(self,dialog):self.record('show');return self.show_hr
    def result(self,dialog):self.record('result');return self.selected
    def release(self,dialog):assert dialog=='OWNED_DIALOG';self.record('release')
    @property
    def names(self):return [name for name,_ in self.calls]


@pytest.mark.parametrize('hr',[0,1])
def test_success_com_ownership_order_and_matching_uninitialize(hr):
    api=FakeDialog(initialize=hr)
    assert picker._run_dialog('C:\\Public Synthetic','Public title',lambda:api)==api.selected
    assert api.names==['initialize','create','private_history','options','title','initial','show','result','clear_history','release','uninitialize']


@pytest.mark.parametrize('cancel',[picker.ERROR_CANCELLED_HRESULT,ctypes.c_int32(picker.ERROR_CANCELLED_HRESULT).value])
def test_cancel_is_none_no_result_and_cleanup_owned_history(cancel):
    api=FakeDialog(show=cancel)
    assert picker._run_dialog(None,'Public title',lambda:api) is None
    assert 'result' not in api.names
    assert api.names[-3:]==['clear_history','release','uninitialize']


def test_failed_initialize_does_not_create_dialog_or_uninitialize():
    api=FakeDialog(initialize=0x80010106)
    with pytest.raises(picker.FolderPickerError,match='^FOLDER_PICKER_COM_INITIALIZATION_FAILED$'):
        picker._run_dialog(None,'Title',lambda:api)
    assert api.names==['initialize']


@pytest.mark.parametrize('failure',['create','private_history','options','title','initial','show','result','release'])
def test_unexpected_native_failures_are_sanitized_and_release_apartment(failure):
    api=FakeDialog(fail=failure)
    with pytest.raises(picker.FolderPickerError) as caught:picker._run_dialog('C:\\Public Synthetic','Title',lambda:api)
    assert str(caught.value).startswith('FOLDER_PICKER_') and 'private' not in str(caught.value)
    assert api.names[-1]=='uninitialize'
    if failure not in {'create'}:assert 'release' in api.names
    if failure not in {'create','private_history'}:assert 'clear_history' in api.names


@pytest.mark.parametrize('show',[0,picker.ERROR_CANCELLED_HRESULT])
def test_history_cleanup_failure_preserves_selection_cancel_semantics(show):
    api=FakeDialog(show=show,fail='clear_history')
    selected=picker._run_dialog(None,'Title',lambda:api)
    assert selected==(None if show else api.selected)
    assert api.names[-3:]==['clear_history','release','uninitialize']


def test_capability_is_configure_only_real_sta_no_show_and_honest_history():
    api=FakeDialog(fail='clear_history');caller=threading.get_ident()
    with patch.object(picker.sys,'platform','win32'),patch.object(picker,'_NativeDialog',return_value=api):
        result=picker.native_capability_check()
    assert result=={'status':'PASS','evidence':'NATIVE_COM_CONFIGURE_ONLY','ui_show':'NOT_EXERCISED','history_cleanup':'UNVERIFIED'}
    assert 'show' not in api.names and 'result' not in api.names and 'initial' not in api.names
    assert {tid for _,tid in api.calls}!={caller}


def test_failed_show_is_not_cancel_or_selection():
    api=FakeDialog(show=0x80070005)
    with pytest.raises(picker.FolderPickerError,match='^FOLDER_PICKER_DIALOG_FAILED$'):
        picker._run_dialog(None,'Title',lambda:api)
    assert 'result' not in api.names


@pytest.mark.parametrize('result',['relative','',None,'C:\\bad\npath','C:\\'+('x'*4097)])
def test_result_requires_bounded_absolute_filesystem_path(result):
    api=FakeDialog(result=result)
    with pytest.raises(picker.FolderPickerError,match='^FOLDER_PICKER_NOT_FILESYSTEM_FOLDER$'):
        picker._run_dialog(None,'Title',lambda:api)
    assert api.names[-3:]==['clear_history','release','uninitialize']


def test_choose_folder_fresh_sta_not_caller_thread_for_all_com_operations():
    api=FakeDialog();caller=threading.get_ident()
    with patch.object(picker.sys,'platform','win32'),patch.object(picker,'_NativeDialog',return_value=api):
        assert picker.choose_folder(None,'Public title')==api.selected
    ids={identifier for _,identifier in api.calls}
    assert len(ids)==1 and caller not in ids


def test_choose_folder_cancel_on_sta_does_not_change_callers_path():
    api=FakeDialog(show=picker.ERROR_CANCELLED_HRESULT);initial='C:\\Public Synthetic'
    with patch.object(picker.sys,'platform','win32'),patch.object(picker,'_NativeDialog',return_value=api),patch.object(picker,'_nearest_existing_folder',return_value=initial):
        assert picker.choose_folder(initial,'Title') is None
    assert initial=='C:\\Public Synthetic'


@pytest.mark.parametrize('title',['',None,'bad\nlabel','x'*257])
def test_bad_title_rejected_before_native_factory(title):
    with patch.object(picker.sys,'platform','win32'),patch.object(picker,'_NativeDialog',side_effect=AssertionError('No dialog')):
        with pytest.raises(picker.FolderPickerError,match='^FOLDER_PICKER_INPUT_INVALID$'):picker.choose_folder(None,title)


def test_nonwindows_has_explicit_unavailable_no_external_helper():
    with patch.object(picker.sys,'platform','linux'),patch.object(picker,'_NativeDialog',side_effect=AssertionError('No dialog')):
        with pytest.raises(picker.FolderPickerError,match='^FOLDER_PICKER_UNAVAILABLE$'):picker.choose_folder()


def test_options_include_folder_filesystem_existing_path_no_chdir_no_recent():
    assert picker.FOLDER_FLAGS==0x02000868
    assert ctypes.sizeof(picker.GUID)==16
    assert picker.CLSID_FILE_OPEN_DIALOG.data1==0xDC1C5A9C


def test_native_options_preserve_existing_flags_and_use_correct_com_slots():
    calls=[]
    def invoke(pointer,index,restype,arg_types,*args):
        calls.append((index,args))
        if index==10:args[0]._obj.value=0x1000
        return 0
    dialog=object();api=object.__new__(picker._NativeDialog)
    with patch.object(picker,'_call',side_effect=invoke):api.options(dialog)
    assert [index for index,_ in calls]==[10,9]
    assert calls[1][1]==(0x1000|picker.FOLDER_FLAGS,)


def test_initial_nonexisting_leaf_uses_existing_owned_ancestor(tmp_path):
    if picker.sys.platform!='win32':pytest.skip('Native WindowsPath initial selection')
    leaf=tmp_path/'not-created'/'another'
    assert picker._nearest_existing_folder(str(leaf))==str(tmp_path)
    assert not leaf.exists()


@pytest.mark.parametrize('initial',['relative','',False,'C:\\bad\npath',r'\\server\share\folder',
    r'\\?\C:\folder',r'\\.\C:\folder',r'C:\folder:stream',r'C:\folder\..\other'])
def test_initial_bad_shape_fixed_error_no_dialog(initial):
    with pytest.raises(picker.FolderPickerError,match='^FOLDER_PICKER_INPUT_INVALID$'):picker._nearest_existing_folder(initial)
