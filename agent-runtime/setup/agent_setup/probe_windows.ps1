# Read-only, fixed metadata projection. Never return native stderr, environment,
# process command lines, authentication stores, user names or distro names.
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$result = @{volumes=@(); wsl_version_text=''; wslc_state='UNKNOWN'; wslc_active_count=$null}
try {
    foreach ($volume in Get-Volume) {
        if (-not $volume.DriveLetter) { continue }
        $disk = $null
        try { $disk = Get-Partition -DriveLetter $volume.DriveLetter | Get-Disk | Select-Object -First 1 } catch {}
        $media = 'UNKNOWN'
        if ($disk) {
            # Match the provider identity in memory; DeviceId/DiskNumber are
            # different namespaces on Storage Spaces and must not be guessed.
            try { $physical = Get-PhysicalDisk | Where-Object { $disk.UniqueId -and $_.UniqueId -eq $disk.UniqueId } | Select-Object -First 1; if ($physical) { $media = [string]$physical.MediaType } } catch {}
        }
        $result.volumes += @{
            mount=([string]$volume.DriveLetter + ':\'); fs=[string]$volume.FileSystem;
            capacity_bytes=[long]$volume.Size; free_bytes=[long]$volume.SizeRemaining;
            device_id=$(if ($disk) {'disk-' + [string]$disk.Number} else {'UNKNOWN'});
            media_type=$media; bus_type=$(if ($disk) {[string]$disk.BusType} else {'UNKNOWN'})
        }
    }
} catch {}
$wsl = Get-Command wsl.exe -ErrorAction SilentlyContinue
if ($wsl) {
    try {
        # wsl.exe emits UTF-16LE on redirected stdout, even when Console uses
        # UTF-8. Decode at the pipe rather than guessing from corrupted labels.
        $start = New-Object System.Diagnostics.ProcessStartInfo
        $start.FileName = $wsl.Source; $start.Arguments = '--version'
        $start.UseShellExecute = $false; $start.CreateNoWindow = $true
        $start.RedirectStandardOutput = $true; $start.RedirectStandardError = $true
        $start.StandardOutputEncoding = [System.Text.Encoding]::Unicode
        $process = New-Object System.Diagnostics.Process
        $process.StartInfo = $start
        [void]$process.Start()
        $read = $process.StandardOutput.ReadToEndAsync()
        $discard = $process.StandardError.ReadToEndAsync()
        if ($process.WaitForExit(10000)) {
            if ($process.ExitCode -eq 0) { $result.wsl_version_text = $read.Result }
        } else { $process.Kill() }
        $process.Dispose()
    } catch {}
}
$wslc = Get-Command wslc.exe -ErrorAction SilentlyContinue
if (-not $wslc) { $result.wslc_state='BLOCKED' }
else {
    # ps is read-only. No run/start/upgrade/shutdown/terminate probe.
    try {
        $containers = & $wslc.Source ps --format json 2>$null
        if ($LASTEXITCODE -eq 0) {
            $parsed = ($containers -join "`n") | ConvertFrom-Json
            $result.wslc_state='PASS'; $result.wslc_active_count=$(if ($null -eq $parsed) {0} else {@($parsed).Count})
        }
    } catch {}
}
$result | ConvertTo-Json -Depth 5 -Compress
