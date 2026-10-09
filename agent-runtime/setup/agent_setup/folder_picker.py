"""Windows Common Item Dialog, with COM objects confined to one fresh STA.

Selection only: this module does not create/move directories, read credentials,
or authorize an installation. The caller must replan and restore Textual focus.
"""
from __future__ import annotations
import ctypes
from pathlib import Path, PureWindowsPath
import queue
import re
import sys
import threading
import uuid

COINIT_APARTMENTTHREADED=0x2
COINIT_DISABLE_OLE1DDE=0x4
FOS_NOCHANGEDIR=0x8
FOS_PICKFOLDERS=0x20
FOS_FORCEFILESYSTEM=0x40
FOS_PATHMUSTEXIST=0x800
FOS_DONTADDTORECENT=0x02000000
FOLDER_FLAGS=FOS_NOCHANGEDIR|FOS_PICKFOLDERS|FOS_FORCEFILESYSTEM|FOS_PATHMUSTEXIST|FOS_DONTADDTORECENT
SIGDN_FILESYSPATH=0x80058000
SFGAO_FOLDER=0x20000000
ERROR_CANCELLED_HRESULT=0x800704C7
HRESULT=ctypes.c_int32

class FolderPickerError(RuntimeError):
    """Fixed public category, without native errors or selected path output."""

class GUID(ctypes.Structure):
    _fields_=[('data1',ctypes.c_uint32),('data2',ctypes.c_uint16),('data3',ctypes.c_uint16),('data4',ctypes.c_ubyte*8)]
    @classmethod
    def parse(cls,value):return cls.from_buffer_copy(uuid.UUID(value).bytes_le)

CLSID_FILE_OPEN_DIALOG=GUID.parse('DC1C5A9C-E88A-4DDE-A5A1-60F82A20AEF7')
IID_FILE_OPEN_DIALOG=GUID.parse('D57C7288-D4AD-4768-BE02-9D969532D960')
IID_SHELL_ITEM=GUID.parse('43826D1E-E718-42EE-BC55-A1E261C37BFE')

def _check(hr,code):
    if int(hr)&0x80000000:raise FolderPickerError(code)

def _call(pointer,index,result_type,arg_types,*args):
    vtable=ctypes.cast(pointer,ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
    function=ctypes.WINFUNCTYPE(result_type,ctypes.c_void_p,*arg_types)(vtable[index])
    return function(pointer,*args)

class _NativeDialog:
    """Trusted OS DLLs; no DLL or executable lookup through PATH/extraction."""
    def __init__(self):
        self.ole=ctypes.WinDLL('ole32.dll',winmode=0x800)
        self.shell=ctypes.WinDLL('shell32.dll',winmode=0x800)
        self.kernel=ctypes.WinDLL('kernel32.dll',winmode=0x800)
        self.user=ctypes.WinDLL('user32.dll',winmode=0x800)
        self.ole.CoInitializeEx.argtypes=[ctypes.c_void_p,ctypes.c_uint32];self.ole.CoInitializeEx.restype=HRESULT
        self.ole.CoUninitialize.argtypes=[];self.ole.CoUninitialize.restype=None
        self.ole.CoCreateInstance.argtypes=[ctypes.POINTER(GUID),ctypes.c_void_p,ctypes.c_uint32,ctypes.POINTER(GUID),ctypes.POINTER(ctypes.c_void_p)];self.ole.CoCreateInstance.restype=HRESULT
        self.ole.CoTaskMemFree.argtypes=[ctypes.c_void_p];self.ole.CoTaskMemFree.restype=None
        self.shell.SHCreateItemFromParsingName.argtypes=[ctypes.c_wchar_p,ctypes.c_void_p,ctypes.POINTER(GUID),ctypes.POINTER(ctypes.c_void_p)];self.shell.SHCreateItemFromParsingName.restype=HRESULT
        self.kernel.GetConsoleWindow.argtypes=[];self.kernel.GetConsoleWindow.restype=ctypes.c_void_p
        self.user.IsWindowVisible.argtypes=[ctypes.c_void_p];self.user.IsWindowVisible.restype=ctypes.c_int
    def initialize(self):return self.ole.CoInitializeEx(None,COINIT_APARTMENTTHREADED|COINIT_DISABLE_OLE1DDE)
    def uninitialize(self):self.ole.CoUninitialize()
    def create(self):
        dialog=ctypes.c_void_p()
        _check(self.ole.CoCreateInstance(ctypes.byref(CLSID_FILE_OPEN_DIALOG),None,1,ctypes.byref(IID_FILE_OPEN_DIALOG),ctypes.byref(dialog)),'FOLDER_PICKER_CREATE_FAILED')
        if not dialog.value:raise FolderPickerError('FOLDER_PICKER_CREATE_FAILED')
        return dialog
    def options(self,dialog):
        options=ctypes.c_uint32()
        _check(_call(dialog,10,HRESULT,[ctypes.POINTER(ctypes.c_uint32)],ctypes.byref(options)),'FOLDER_PICKER_OPTIONS_FAILED')
        _check(_call(dialog,9,HRESULT,[ctypes.c_uint32],options.value|FOLDER_FLAGS),'FOLDER_PICKER_OPTIONS_FAILED')
    def title(self,dialog,title):
        _check(_call(dialog,17,HRESULT,[ctypes.c_wchar_p],title),'FOLDER_PICKER_DIALOG_FAILED')
    def private_history(self,dialog):
        # A per-dialog GUID prevents touching another app/user's remembered
        # locations. Clear only this new owned bucket when the dialog closes.
        client=GUID.parse(str(uuid.uuid4()))
        _check(_call(dialog,24,HRESULT,[ctypes.POINTER(GUID)],ctypes.byref(client)),'FOLDER_PICKER_OPTIONS_FAILED')
    def clear_history(self,dialog):
        return not (int(_call(dialog,25,HRESULT,[]))&0x80000000)
    def initial(self,dialog,path):
        item=ctypes.c_void_p()
        try:
            _check(self.shell.SHCreateItemFromParsingName(path,None,ctypes.byref(IID_SHELL_ITEM),ctypes.byref(item)),'FOLDER_PICKER_INITIAL_FOLDER_FAILED')
            _check(_call(dialog,12,HRESULT,[ctypes.c_void_p],item),'FOLDER_PICKER_INITIAL_FOLDER_FAILED')
        finally:
            if item.value:self.release(item)
    def show(self,dialog):
        owner=self.kernel.GetConsoleWindow()
        if not owner or not self.user.IsWindowVisible(owner):owner=None
        return _call(dialog,3,HRESULT,[ctypes.c_void_p],owner)
    def result(self,dialog):
        item=ctypes.c_void_p();name=ctypes.c_void_p()
        try:
            _check(_call(dialog,20,HRESULT,[ctypes.POINTER(ctypes.c_void_p)],ctypes.byref(item)),'FOLDER_PICKER_RESULT_FAILED')
            if not item.value:raise FolderPickerError('FOLDER_PICKER_RESULT_FAILED')
            attrs=ctypes.c_uint32()
            _check(_call(item,6,HRESULT,[ctypes.c_uint32,ctypes.POINTER(ctypes.c_uint32)],SFGAO_FOLDER,ctypes.byref(attrs)),'FOLDER_PICKER_RESULT_FAILED')
            if not attrs.value&SFGAO_FOLDER:raise FolderPickerError('FOLDER_PICKER_NOT_FILESYSTEM_FOLDER')
            _check(_call(item,5,HRESULT,[ctypes.c_uint32,ctypes.POINTER(ctypes.c_void_p)],SIGDN_FILESYSPATH,ctypes.byref(name)),'FOLDER_PICKER_NOT_FILESYSTEM_FOLDER')
            if not name.value:raise FolderPickerError('FOLDER_PICKER_RESULT_FAILED')
            return ctypes.wstring_at(name.value)
        finally:
            if name.value:self.ole.CoTaskMemFree(name)
            if item.value:self.release(item)
    def release(self,pointer):_call(pointer,2,ctypes.c_uint32,[])

def _nearest_existing_folder(initial_path):
    if initial_path is None:return None
    if (not isinstance(initial_path,str) or len(initial_path)>4096 or not initial_path
        or any(ord(ch)<32 for ch in initial_path) or not PureWindowsPath(initial_path).is_absolute()
        or not re.fullmatch(r'[A-Za-z]:',PureWindowsPath(initial_path).drive)
        or ':' in initial_path[2:] or '..' in PureWindowsPath(initial_path).parts):
        raise FolderPickerError('FOLDER_PICKER_INPUT_INVALID')
    path=Path(initial_path)
    for ancestor in (path,*path.parents):
        if ancestor.is_dir():return str(ancestor)
    return None

def _run_dialog(initial_path,title,api_factory=None,*,configure_only=False):
    api=None;initialized=False;dialog=None;private_history=False;report=None
    try:
        api=(api_factory or _NativeDialog)()
        _check(api.initialize(),'FOLDER_PICKER_COM_INITIALIZATION_FAILED');initialized=True
        dialog=api.create();api.private_history(dialog);private_history=True;api.options(dialog);api.title(dialog,title)
        if configure_only:
            report={'status':'PASS','evidence':'NATIVE_COM_CONFIGURE_ONLY','ui_show':'NOT_EXERCISED',
                    'history_cleanup':'UNVERIFIED'}
            return report
        if initial_path:api.initial(dialog,initial_path)
        hr=api.show(dialog)
        if int(hr)&0xffffffff==ERROR_CANCELLED_HRESULT:return None
        _check(hr,'FOLDER_PICKER_DIALOG_FAILED')
        path=api.result(dialog)
        if (not isinstance(path,str) or not path or len(path)>4096 or any(ord(ch)<32 for ch in path)
            or not PureWindowsPath(path).is_absolute()):raise FolderPickerError('FOLDER_PICKER_NOT_FILESYSTEM_FOLDER')
        return path
    except FolderPickerError:raise
    except Exception:raise FolderPickerError('FOLDER_PICKER_UNAVAILABLE') from None
    finally:
        try:
            if dialog is not None:
                try:
                    if private_history:
                        try:history_cleared=api.clear_history(dialog) is True
                        except Exception:history_cleared=False
                        if report is not None:report['history_cleanup']='VERIFIED' if history_cleared else 'UNVERIFIED'
                finally:api.release(dialog)
        except FolderPickerError:raise
        except Exception:raise FolderPickerError('FOLDER_PICKER_COM_CLEANUP_FAILED') from None
        finally:
            if initialized:api.uninitialize()

def _on_sta(function):
    results=queue.Queue(maxsize=1)
    def sta():
        try:results.put((True,function()))
        except FolderPickerError as error:results.put((False,str(error)))
        except Exception:results.put((False,'FOLDER_PICKER_THREAD_FAILED'))
    thread=threading.Thread(target=sta,name='agent-folder-picker-sta',daemon=False)
    try:thread.start();thread.join()
    except Exception:raise FolderPickerError('FOLDER_PICKER_THREAD_FAILED') from None
    try:ok,value=results.get_nowait()
    except queue.Empty:raise FolderPickerError('FOLDER_PICKER_THREAD_FAILED') from None
    if not ok:raise FolderPickerError(value)
    return value

def native_capability_check()->dict:
    """Real OS COM configuration proof, without displaying/browsing a dialog.

    MRU cleanup is best effort on a fresh owned GUID. Failure is UNVERIFIED,
    never proof of absent history; it cannot change cancel/selection semantics.
    """
    if sys.platform!='win32':raise FolderPickerError('FOLDER_PICKER_UNAVAILABLE')
    return _on_sta(lambda:_run_dialog(None,'Folder picker capability',configure_only=True))

def choose_folder(initial_path: str|None=None,title: str='选择文件夹')->str|None:
    """Modal native selection; cancellation is None and never changes a plan.

    Invoke with asyncio.to_thread from Textual. The modal COM apartment always
    lives in its own thread; restore focus to the originating Browse/Input after
    return. Selection is not authority: callers must invalidate consent/replan.
    """
    if sys.platform!='win32':raise FolderPickerError('FOLDER_PICKER_UNAVAILABLE')
    if not isinstance(title,str) or not title or len(title)>256 or any(ord(ch)<32 for ch in title):
        raise FolderPickerError('FOLDER_PICKER_INPUT_INVALID')
    initial=_nearest_existing_folder(initial_path)
    return _on_sta(lambda:_run_dialog(initial,title))
