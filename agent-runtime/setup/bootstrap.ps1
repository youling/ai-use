# Run this checked-out, reviewed file; never pipe an unreviewed remote script into execution.
[CmdletBinding()]
param(
    [ValidateSet('tui', 'cli')][string]$Mode = 'tui',
    [string]$Fixture,
    [string]$PythonPath,
    [switch]$Prepare,
    [switch]$ApprovePythonInstall,
    [switch]$CheckOnly,
    [switch]$AuthorizeHostApply,
    [switch]$ShowLaunchArguments
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
if ($env:OS -ne 'Windows_NT') { throw 'Windows V1 only. Linux/macOS real apply is unsupported.' }
$setupRoot = [IO.Path]::GetFullPath($PSScriptRoot)
if ($AuthorizeHostApply -and $Mode -ne 'tui') { throw 'Host apply entry is the reviewed Textual flow only.' }
if ($ShowLaunchArguments -and -not $CheckOnly) { throw 'ShowLaunchArguments requires nonmutating CheckOnly.' }
$runtimeRoot = Join-Path $setupRoot '.setup-runtime'
$spec = Get-Content -LiteralPath (Join-Path $setupRoot 'python-runtime.json') -Raw | ConvertFrom-Json

function Assert-PlainPath([string]$Path) {
    $current = [IO.Path]::GetFullPath($Path)
    while ($current) {
        if (Test-Path -LiteralPath $current) {
            if ((Get-Item -LiteralPath $current -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) {
                throw 'Reparse-point path refused.'
            }
        }
        $parent = [IO.Directory]::GetParent($current)
        if ($null -eq $parent) { break }
        $current = $parent.FullName
    }
}
function Assert-PsfSignature([string]$Path) {
    $signature = Get-AuthenticodeSignature -LiteralPath $Path
    if ($signature.Status -ne 'Valid' -or $null -eq $signature.SignerCertificate -or
        $signature.SignerCertificate.Subject -notmatch '(^|,\s*)CN=Python Software Foundation(,|$)' -or
        $signature.SignerCertificate.Subject -notmatch '(^|,\s*)O=Python Software Foundation(,|$)') {
        throw 'Python Authenticode signature or PSF signer verification failed.'
    }
}
function Test-Python314([string]$Path) {
    Assert-PlainPath $Path
    Assert-PsfSignature $Path
    $version = & $Path -I -c 'import sys; print("%d.%d.%d %s" % (*sys.version_info[:3],sys.version_info.releaselevel))'
    if ($LASTEXITCODE -ne 0) { throw 'Python version probe failed.' }
    return ($version -match '^3\.14\.[0-9]+ final$')
}
function Invoke-Checked([string]$Exe, [string[]]$Arguments) {
    & $Exe @Arguments
    if ($LASTEXITCODE -ne 0) { throw 'Installer subprocess failed; no Host success claimed.' }
}
function Get-EngineArguments {
    $arguments = @('-s', '-m', 'agent_setup', $Mode)
    if ($Mode -eq 'cli') { $arguments += 'probe' }
    if ($Fixture) { $arguments += @('--fixture', [IO.Path]::GetFullPath($Fixture)) }
    # This only unlocks review controls; apply still needs fresh plan approval.
    if ($AuthorizeHostApply) { $arguments += '--host-authorized' }
    return $arguments
}
Assert-PlainPath $setupRoot
$lockPath = Join-Path $setupRoot 'requirements.lock'
$lockHash = (Get-FileHash -LiteralPath $lockPath -Algorithm SHA256).Hash
$ownerPath = Join-Path $runtimeRoot 'owner.json'
$ownedPython = Join-Path $runtimeRoot ('python-' + $spec.acquisition_version + '\python.exe')
$candidates = @()
if ($PythonPath) { $candidates += [IO.Path]::GetFullPath($PythonPath) }
if (Test-Path -LiteralPath $ownedPython) { $candidates += $ownedPython }
foreach ($name in @('python.exe', 'python3.exe')) {
    $command = Get-Command $name -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($command -and $command.Source -notmatch '\\WindowsApps\\') { $candidates += $command.Source }
}
$python = $null
foreach ($candidate in ($candidates | Select-Object -Unique)) {
    if (Test-Python314 $candidate) { $python = $candidate; break }
    if ($PythonPath) { throw 'Explicit PythonPath must be stable CPython 3.14.x.' }
}
if (-not $python) {
    # Metadata-only discovery prevents acquisition from upgrading a registered
    # 3.14 runtime absent from PATH. Unreadable metadata blocks acquisition.
    foreach ($registryPath in @('HKCU:\Software\Python\PythonCore\3.14\InstallPath',
        'HKLM:\Software\Python\PythonCore\3.14\InstallPath')) {
        if (Test-Path -LiteralPath $registryPath) {
            $installPath = (Get-Item -LiteralPath $registryPath).GetValue('')
            if ($installPath) {
                $registered = Join-Path $installPath 'python.exe'
                if (-not (Test-Python314 $registered)) { throw 'Registered Python 3.14 cannot be verified; no upgrade authorized.' }
                $python = $registered
                break
            }
        }
    }
}
if ($CheckOnly) {
    if ($ShowLaunchArguments) { ConvertTo-Json -InputObject @(Get-EngineArguments) -Compress; return }
    if ($python) { Write-Output 'PYTHON_314_VERIFIED; CHECK_ONLY; HOST_UNCHANGED' }
    else { Write-Output 'PYTHON_314_MISSING; EXPLICIT_INSTALL_APPROVAL_REQUIRED; HOST_UNCHANGED' }
    return
}
if (-not $python -and -not $ApprovePythonInstall) {
    throw 'Python 3.14 missing. Review python-runtime.json, then explicitly use -Prepare -ApprovePythonInstall.'
}
if (-not $Prepare) {
    throw 'Default is nonmutating. Use -CheckOnly to inspect, or -Prepare to create/reuse the isolated installer venv and open the dry-run wizard.'
}
Assert-PlainPath $runtimeRoot
if (Test-Path -LiteralPath $runtimeRoot) {
    if (-not (Test-Path -LiteralPath $ownerPath)) { throw 'Existing unowned setup runtime refused.' }
    $owner = Get-Content -LiteralPath $ownerPath -Raw | ConvertFrom-Json
    if ($owner.schema -ne 1 -or $owner.checkout -ne $setupRoot) { throw 'Setup runtime ownership mismatch.' }
} else {
    New-Item -ItemType Directory -Path $runtimeRoot | Out-Null
    @{schema=1; checkout=$setupRoot} | ConvertTo-Json | Set-Content -LiteralPath $ownerPath -Encoding UTF8
}
$lease = $null
$oldPythonPath = $env:PYTHONPATH
$oldNoUserSite = $env:PYTHONNOUSERSITE
try {
    $lease = [IO.File]::Open((Join-Path $runtimeRoot 'bootstrap.lock'), [IO.FileMode]::OpenOrCreate, [IO.FileAccess]::ReadWrite, [IO.FileShare]::None)
    if (-not $python) {
        if ([Environment]::Is64BitOperatingSystem -ne $true -or $env:PROCESSOR_ARCHITECTURE -ne 'AMD64') {
            throw 'Verified Python acquisition supports Windows AMD64 only; select a separately verified runtime.'
        }
        $target = Join-Path $runtimeRoot ('python-' + $spec.acquisition_version)
        if (Test-Path -LiteralPath $target) { throw 'Existing Python target refused; no repair/upgrade by inference.' }
        $download = Join-Path $runtimeRoot ('python-' + $spec.acquisition_version + '-amd64.exe')
        Assert-PlainPath $download
        if (-not (Test-Path -LiteralPath $download)) {
            # Fixed official HTTPS URI. No script execution, credential input, or alternate source.
            Invoke-WebRequest -Uri $spec.url -OutFile $download -MaximumRedirection 0 -UseBasicParsing
        }
        if ((Get-FileHash -LiteralPath $download -Algorithm SHA256).Hash.ToLowerInvariant() -ne $spec.sha256) {
            throw 'Python download SHA256 mismatch; refusing execution.'
        }
        Assert-PsfSignature $download
        $arguments = @('/quiet', 'InstallAllUsers=0', ('TargetDir="' + $target + '"'), 'PrependPath=0',
            'Include_launcher=0', 'InstallLauncherAllUsers=0', 'AssociateFiles=0', 'Shortcuts=0',
            'Include_doc=0', 'Include_test=0', 'Include_tcltk=0', 'Include_pip=1')
        $process = Start-Process -FilePath $download -ArgumentList $arguments -Wait -PassThru -WindowStyle Hidden
        if ($process.ExitCode -ne 0) { throw 'Python install failed or needs reboot; stop and inspect official installer recovery.' }
        if (-not (Test-Python314 $ownedPython)) { throw 'Installed runtime verification failed.' }
        $python = $ownedPython
    }
    $venv = Join-Path $runtimeRoot 'venv'
    $venvPython = Join-Path $venv 'Scripts\python.exe'
    $readyPath = Join-Path $venv 'setup-ready.json'
    Assert-PlainPath $venv
    if (Test-Path -LiteralPath $venv) {
        if (-not (Test-Path -LiteralPath $readyPath)) { throw 'Partial venv: preserve it and inspect; no automatic deletion.' }
        $ready = Get-Content -LiteralPath $readyPath -Raw | ConvertFrom-Json
        if ($ready.lock_sha256 -ne $lockHash -or $ready.base_python -ne $python) {
            throw 'Venv provenance/lock drift; explicit repair required, no silent package upgrades.'
        }
        if (-not (Test-Python314 $venvPython)) { throw 'Venv runtime verification failed.' }
    } else {
        Invoke-Checked -Exe $python -Arguments @('-I', '-m', 'venv', $venv)
        Invoke-Checked -Exe $venvPython -Arguments @('-I', '-m', 'pip', '--isolated', 'install', '--no-cache-dir',
            '--disable-pip-version-check', '--require-hashes', '-r', $lockPath)
        @{schema=1; lock_sha256=$lockHash; base_python=$python} | ConvertTo-Json | Set-Content -LiteralPath $readyPath -Encoding UTF8
    }
    $env:PYTHONPATH = $setupRoot
    $env:PYTHONNOUSERSITE = '1'
    $engineArgs = @(Get-EngineArguments)
    Invoke-Checked -Exe $venvPython -Arguments $engineArgs
} finally {
    $env:PYTHONPATH = $oldPythonPath
    $env:PYTHONNOUSERSITE = $oldNoUserSite
    if ($null -ne $lease) { $lease.Dispose() }
}
