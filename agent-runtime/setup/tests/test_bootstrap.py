"""Bootstrap safety boundary checks: never install Python or prepare a live venv."""
from pathlib import Path
import os
import shutil
import subprocess

import pytest

ROOT = Path(__file__).parents[1]


def test_acquisition_is_explicit_and_verified():
    import json

    spec = json.loads((ROOT / "python-runtime.json").read_text())
    source = (ROOT / "bootstrap.ps1").read_text()
    assert spec["url"] == "https://www.python.org/ftp/python/3.14.8/python-3.14.8-amd64.exe"
    assert len(spec["sha256"]) == 64
    assert "-MaximumRedirection 0" in source
    assert "Assert-PsfSignature $download" in source
    assert source.index("SHA256 mismatch") < source.index("Start-Process -FilePath $download")
    assert "-not $ApprovePythonInstall" in source
    assert "--require-hashes" in source
    assert "[IO.FileShare]::None" in source
    assert "'--host-authorized'" not in source


@pytest.mark.skipif(os.name != "nt" or not shutil.which("pwsh"), reason="Windows PowerShell boundary")
def test_unsigned_python_never_executes_or_creates_runtime(tmp_path):
    for name in ("bootstrap.ps1", "python-runtime.json", "requirements.lock"):
        shutil.copyfile(ROOT / name, tmp_path / name)
    fake = tmp_path / "fake.exe"
    fake.write_bytes(b"untrusted runtime must not execute")
    result = subprocess.run(
        ["pwsh", "-NoProfile", "-File", str(tmp_path / "bootstrap.ps1"),
         "-PythonPath", str(fake), "-Prepare", "-ApprovePythonInstall"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30,
    )
    assert result.returncode != 0
    assert "signature" in result.stderr.lower()
    assert not (tmp_path / ".setup-runtime").exists()


@pytest.mark.skipif(os.name != "nt" or not shutil.which("pwsh"), reason="Windows PowerShell boundary")
def test_check_only_is_nonmutating(tmp_path):
    for name in ("bootstrap.ps1", "python-runtime.json", "requirements.lock"):
        shutil.copyfile(ROOT / name, tmp_path / name)
    result = subprocess.run(
        ["pwsh", "-NoProfile", "-File", str(tmp_path / "bootstrap.ps1"), "-CheckOnly"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert "HOST_UNCHANGED" in result.stdout
    assert not (tmp_path / ".setup-runtime").exists()
