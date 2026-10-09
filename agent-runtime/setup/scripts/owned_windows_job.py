"""Acceptance harness only: suspended child assigned to an unnamed owned job.

The job includes only this newly launched process and descendants. No process
inventory or name-based termination is used. Windows 8+ supports nested jobs.
Output reads are bounded and use temporary files, so descendant pipe handles
cannot turn a deadline into an unbounded communicate() wait.
"""
from __future__ import annotations
import ctypes as C
from ctypes import wintypes as W
import os
import subprocess
import tempfile
import time


class BasicLimit(C.Structure):
    _fields_ = [('process_time', C.c_int64), ('job_time', C.c_int64), ('flags', W.DWORD),
                ('min_working', C.c_size_t), ('max_working', C.c_size_t), ('active', W.DWORD),
                ('affinity', C.c_size_t), ('priority', W.DWORD), ('scheduling', W.DWORD)]


class IOCounters(C.Structure):
    _fields_ = [(name, C.c_uint64) for name in
                ['read_ops', 'write_ops', 'other_ops', 'read_bytes', 'write_bytes', 'other_bytes']]


class ExtendedLimit(C.Structure):
    _fields_ = [('basic', BasicLimit), ('io', IOCounters), ('process_memory', C.c_size_t),
                ('job_memory', C.c_size_t), ('peak_process', C.c_size_t), ('peak_job', C.c_size_t)]


class Startup(C.Structure):
    _fields_ = [('size', W.DWORD), ('reserved', W.LPWSTR), ('desktop', W.LPWSTR), ('title', W.LPWSTR),
                ('x', W.DWORD), ('y', W.DWORD), ('x_size', W.DWORD), ('y_size', W.DWORD),
                ('x_chars', W.DWORD), ('y_chars', W.DWORD), ('fill', W.DWORD), ('flags', W.DWORD),
                ('show', W.WORD), ('reserved_size', W.WORD), ('reserved_data', C.c_void_p),
                ('stdin', W.HANDLE), ('stdout', W.HANDLE), ('stderr', W.HANDLE)]


class StartupEx(C.Structure):
    _fields_ = [('startup', Startup), ('attributes', C.c_void_p)]


class ProcessInfo(C.Structure):
    _fields_ = [('process', W.HANDLE), ('thread', W.HANDLE), ('pid', W.DWORD), ('tid', W.DWORD)]


def _kernel():
    kernel = C.WinDLL('kernel32', use_last_error=True, winmode=0x800)
    declarations = {
        'CreateJobObjectW': ([C.c_void_p, W.LPCWSTR], W.HANDLE),
        'SetInformationJobObject': ([W.HANDLE, C.c_int, C.c_void_p, W.DWORD], W.BOOL),
        'AssignProcessToJobObject': ([W.HANDLE, W.HANDLE], W.BOOL),
        'CreateProcessW': ([W.LPCWSTR, W.LPWSTR, C.c_void_p, C.c_void_p, W.BOOL, W.DWORD,
                            C.c_void_p, W.LPCWSTR, C.c_void_p, C.POINTER(ProcessInfo)], W.BOOL),
        'ResumeThread': ([W.HANDLE], W.DWORD),
        'WaitForSingleObject': ([W.HANDLE, W.DWORD], W.DWORD),
        'GetExitCodeProcess': ([W.HANDLE, C.POINTER(W.DWORD)], W.BOOL),
        'TerminateJobObject': ([W.HANDLE, W.UINT], W.BOOL),
        'TerminateProcess': ([W.HANDLE, W.UINT], W.BOOL),
        'CloseHandle': ([W.HANDLE], W.BOOL),
        'InitializeProcThreadAttributeList': ([C.c_void_p, W.DWORD, W.DWORD, C.POINTER(C.c_size_t)], W.BOOL),
        'UpdateProcThreadAttribute': ([C.c_void_p, W.DWORD, C.c_size_t, C.c_void_p,
                                      C.c_size_t, C.c_void_p, C.c_void_p], W.BOOL),
        'DeleteProcThreadAttributeList': ([C.c_void_p], None),
    }
    for name, (arguments, result) in declarations.items():
        function = getattr(kernel, name)
        function.argtypes, function.restype = arguments, result
    return kernel


def run_owned(arguments, *, cwd, env, timeout):
    """Return bounded stdout; every failure terminates only our own tree."""
    if os.name != 'nt':
        raise RuntimeError('OWNED_WINDOWS_JOB_REQUIRED')
    import msvcrt
    kernel = _kernel()
    job = kernel.CreateJobObjectW(None, None)
    process = ProcessInfo()
    attributes = None
    assigned = False
    try:
        limits = ExtendedLimit()
        limits.basic.flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not job or not kernel.SetInformationJobObject(job, 9, C.byref(limits), C.sizeof(limits)):
            raise RuntimeError('OWNED_JOB_SETUP_FAILED')
        with open(os.devnull, 'rb') as source, tempfile.TemporaryFile() as output, tempfile.TemporaryFile() as errors:
            handles = [msvcrt.get_osfhandle(file.fileno()) for file in [source, output, errors]]
            for handle in handles:
                os.set_handle_inheritable(handle, True)
            size = C.c_size_t()
            kernel.InitializeProcThreadAttributeList(None, 1, 0, C.byref(size))
            attributes = C.create_string_buffer(size.value)
            if not kernel.InitializeProcThreadAttributeList(attributes, 1, 0, C.byref(size)):
                attributes = None
                raise RuntimeError('OWNED_JOB_HANDLES_FAILED')
            allowed = (W.HANDLE * 3)(*handles)
            # Explicit inherited handle list: no unrelated parent handles.
            if not kernel.UpdateProcThreadAttribute(attributes, 0, 0x20002, allowed, C.sizeof(allowed), None, None):
                raise RuntimeError('OWNED_JOB_HANDLES_FAILED')
            startup = StartupEx()
            startup.startup.size = C.sizeof(startup)
            startup.startup.flags = 0x100 | 1  # USESTDHANDLES | USESHOWWINDOW
            startup.startup.stdin, startup.startup.stdout, startup.startup.stderr = handles
            startup.attributes = C.cast(attributes, C.c_void_p)
            command = C.create_unicode_buffer(subprocess.list2cmdline([str(value) for value in arguments]))
            block = C.create_unicode_buffer('\0'.join(f'{key}={value}' for key, value in sorted(env.items())) + '\0\0')
            # Suspended + Unicode environment + extended startup + no window.
            if not kernel.CreateProcessW(str(arguments[0]), command, None, None, True,
                                          0x4 | 0x400 | 0x80000 | 0x08000000,
                                          block, str(cwd), C.byref(startup), C.byref(process)):
                raise RuntimeError('OWNED_PROCESS_CREATE_FAILED')
            for handle in handles:
                os.set_handle_inheritable(handle, False)
            if not kernel.AssignProcessToJobObject(job, process.process):
                raise RuntimeError('OWNED_PROCESS_ASSIGN_FAILED')
            assigned = True
            if kernel.ResumeThread(process.thread) == 0xFFFFFFFF:
                raise RuntimeError('OWNED_PROCESS_RESUME_FAILED')
            deadline = time.monotonic() + timeout
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise subprocess.TimeoutExpired(arguments, timeout)
                result = kernel.WaitForSingleObject(process.process, max(1, min(1000, int(remaining * 1000))))
                if result == 0:
                    break
                if result != 258:
                    raise RuntimeError('OWNED_PROCESS_WAIT_FAILED')
            code = W.DWORD()
            if not kernel.GetExitCodeProcess(process.process, C.byref(code)):
                raise RuntimeError('OWNED_PROCESS_EXIT_FAILED')
            kernel.TerminateJobObject(job, 124)
            output.seek(0)
            return subprocess.CompletedProcess(arguments, code.value,
                                               output.read(100001).decode('utf-8', errors='replace'), '')
    finally:
        if process.process:
            if assigned:
                kernel.TerminateJobObject(job, 124)
            else:
                # Assignment failed: the exclusively owned child never resumed.
                kernel.TerminateProcess(process.process, 124)
            kernel.WaitForSingleObject(process.process, 10000)
        if attributes is not None:
            kernel.DeleteProcThreadAttributeList(attributes)
        for handle in [process.thread, process.process, job]:
            if handle:
                kernel.CloseHandle(handle)
