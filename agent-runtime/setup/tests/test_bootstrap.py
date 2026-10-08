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
    assert "if ($AuthorizeHostApply) { $arguments += '--host-authorized' }" in source


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

@pytest.mark.skipif(os.name != 'nt' or not shutil.which('pwsh'),reason='Windows PowerShell boundary')
@pytest.mark.parametrize('authorized',[False,True])
def test_bootstrap_to_real_tui_fixture_review_and_apply(tmp_path,monkeypatch,authorized):
    import asyncio,json,sys
    from agent_setup.__main__ import main
    from agent_setup.tui import SetupApp
    from textual.widgets import Button,Checkbox
    fixture=ROOT/'tests/fixtures/windows-ready.json'
    command=['pwsh','-NoProfile','-File',str(ROOT/'bootstrap.ps1'),'-CheckOnly','-ShowLaunchArguments','-Fixture',str(fixture)]
    if authorized:command.append('-AuthorizeHostApply')
    result=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',timeout=30)
    assert result.returncode==0,result.stderr
    args=json.loads(result.stdout)
    assert ('--host-authorized' in args)==authorized
    sandbox=tmp_path/'fixture'
    monkeypatch.setattr(sys,'argv',['agent_setup',*args[3:],'--sandbox',str(sandbox)])
    def exercise(engine,**options):
        async def flow():
            app=SetupApp(engine,**options)
            async with app.run_test(size=(110,50)) as pilot:
                for _ in range(3):
                    await pilot.click('#next');await pilot.pause(0.25)
                assert app.step==3
                app.query_one('#approve',Checkbox).value=True
                await pilot.pause()
                assert app.query_one('#apply',Button).disabled is not authorized
                if authorized:
                    approved_fingerprint=app.plan_data['fingerprint']
                    app.query_one('#apply',Button).focus()
                    await pilot.press('enter');await pilot.pause(0.25)
                    assert app.step==4 and app.result['status']=='CONFIGURED_PENDING_AUTH'
                    receipt=json.loads(Path(app.result['receipt']).read_text())
                    assert receipt['fingerprint']==approved_fingerprint
                else:assert not (sandbox/'Documents/HOST_AGENT.md').exists()
        asyncio.run(flow())
    monkeypatch.setattr('agent_setup.tui.run_tui',exercise)
    main()
    assert (sandbox/'Documents/HOST_AGENT.md').exists()==authorized


@pytest.mark.skipif(os.name != "nt" or not shutil.which("pwsh"), reason="Windows PowerShell boundary")
def test_unsigned_python_first_on_path_does_not_abort_discovery(tmp_path):
    """Do not execute an unsigned PATH shim; keep the read-only check usable."""
    for name in ("bootstrap.ps1", "python-runtime.json", "requirements.lock"):
        shutil.copyfile(ROOT / name, tmp_path / name)
    untrusted = tmp_path / "untrusted-bin"
    untrusted.mkdir()
    (untrusted / "python.exe").write_bytes(b"fake executable: must never run")
    env = os.environ.copy()
    env["PATH"] = str(untrusted) + os.pathsep + env.get("PATH", "")
    result = subprocess.run(
        [shutil.which("pwsh"), "-NoProfile", "-File", str(tmp_path / "bootstrap.ps1"), "-CheckOnly"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30, env=env,
    )
    assert result.returncode == 0, result.stderr
    assert "HOST_UNCHANGED" in result.stdout
    assert "Python Authenticode signature" not in result.stderr
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
