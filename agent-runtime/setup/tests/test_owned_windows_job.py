"""Owned disposable children: no system process enumeration or termination."""
import ctypes
from ctypes import wintypes
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import time
import pytest

path = Path(__file__).resolve().parents[1] / 'scripts/owned_windows_job.py'
spec = importlib.util.spec_from_file_location('test_owned_job_helper', path)
job = importlib.util.module_from_spec(spec)
spec.loader.exec_module(job)
pytestmark = pytest.mark.skipif(os.name != 'nt', reason='Windows job API')


def environment(tmp_path):
    return {key: os.environ[key] for key in ['SystemRoot', 'WINDIR'] if key in os.environ} | {
        'PATH': '', 'TEMP': str(tmp_path), 'TMP': str(tmp_path)}


def test_owned_job_capture_and_nested_job(tmp_path):
    code = f"import sys;sys.path.insert(0,{str(path.parent)!r});from owned_windows_job import run_owned;import os;print(run_owned([sys.executable,'-c','print(123)'],cwd={str(tmp_path)!r},env=dict(os.environ),timeout=10).stdout.strip())"
    result = job.run_owned([sys.executable, '-c', code], cwd=tmp_path, env=environment(tmp_path), timeout=15)
    assert result.returncode == 0 and result.stdout.strip() == '123'


def test_assignment_failure_never_resumes_owned_child(tmp_path, monkeypatch):
    actual = job._kernel()
    class FailAssignment:
        resumes = 0
        def __getattr__(self, name):
            return getattr(actual, name)
        def AssignProcessToJobObject(self, *_):
            return 0
        def ResumeThread(self, *_):
            self.resumes += 1
            return 0
    fake = FailAssignment()
    monkeypatch.setattr(job, '_kernel', lambda: fake)
    marker = tmp_path / 'must-not-start'
    with pytest.raises(RuntimeError, match='OWNED_PROCESS_ASSIGN_FAILED'):
        job.run_owned([sys.executable, '-c', f"from pathlib import Path;Path({str(marker)!r}).write_text('bad')"],
                      cwd=tmp_path, env=environment(tmp_path), timeout=5)
    assert fake.resumes == 0 and not marker.exists()


def test_timeout_kills_only_owned_descendants(tmp_path):
    # The unrelated control process is also our disposable test fixture.
    control = subprocess.Popen([sys.executable, '-c', 'import time;time.sleep(30)'],
                               env=environment(tmp_path), stdin=subprocess.DEVNULL,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    pidfile = tmp_path / 'owned-grandchild-pid'
    code = ("import subprocess,sys,time;from pathlib import Path;"
            "p=subprocess.Popen([sys.executable,'-c','import time;time.sleep(30)']);"
            f"Path({str(pidfile)!r}).write_text(str(p.pid));time.sleep(30)")
    begun = time.monotonic()
    try:
        with pytest.raises(subprocess.TimeoutExpired):
            job.run_owned([sys.executable, '-c', code], cwd=tmp_path, env=environment(tmp_path), timeout=3)
        assert time.monotonic() - begun < 13
        assert control.poll() is None
        assert pidfile.is_file()
        kernel = job._kernel()
        kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel.OpenProcess.restype = wintypes.HANDLE
        handle = kernel.OpenProcess(0x100000, False, int(pidfile.read_text()))
        if handle:
            try:
                assert kernel.WaitForSingleObject(handle, 3000) == 0
            finally:
                kernel.CloseHandle(handle)
    finally:
        control.terminate()
        control.wait(timeout=5)
