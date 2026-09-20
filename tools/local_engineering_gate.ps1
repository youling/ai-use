[CmdletBinding()]
param(
  [ValidateSet("LOCAL","LOCAL_DEVICE")][string]$ExecutionProfile="LOCAL",
  [string]$Repository="",
  [string]$RepoPath=".",
  [string]$ExpectedBase="",
  [switch]$RequireExactBase,
  [switch]$RequireCleanRepo,
  [switch]$RequireLatest,
  [switch]$RequireCodex,
  [switch]$RequireOpenCode,
  [string[]]$RequiredOpenCodeAuthPattern=@(),
  [string[]]$RequiredOpenCodeModelPattern=@(),
  [switch]$ProbeProjectRemote,
  [switch]$RequireProjectRemote,
  [string]$ProjectProbeScript="",
  [switch]$Json,
  [switch]$SelfTest
)

Set-StrictMode -Version Latest
$ErrorActionPreference="Stop"
$ProgressPreference="SilentlyContinue"
$ContractVersion="1.0.0"
$AdapterId="windows-pwsh"
$AdapterVersion="0.1.0"
$Platform="windows"
$Checks=[System.Collections.Generic.List[object]]::new()

function Add-Check([string]$Name,[bool]$Required,[string]$State,[string]$Detail="",[string]$LocalVersion="",[string]$LatestVersion=""){
  $Checks.Add([pscustomobject]@{name=$Name;required=$Required;state=$State;local_version=$LocalVersion;latest_version=$LatestVersion;detail=$Detail}) | Out-Null
}

function Run([string]$File,[string[]]$Arguments=@()){
  try {
    $out=(& $File @Arguments 2>&1 | Out-String).Trim()
    $code=if($null -eq $LASTEXITCODE){0}else{[int]$LASTEXITCODE}
    return [pscustomobject]@{code=$code;out=$out}
  } catch {
    return [pscustomobject]@{code=1;out=""}
  }
}

function SemVer([string]$Raw){
  if([string]::IsNullOrWhiteSpace($Raw)){return $null}
  $m=[regex]::Match($Raw,'(?<!\d)(\d+)\.(\d+)\.(\d+)')
  if(-not $m.Success){return $null}
  return [Version]::new([int]$m.Groups[1].Value,[int]$m.Groups[2].Value,[int]$m.Groups[3].Value)
}

function LatestTag([string]$Repo){
  if(-not (Get-Command gh -ErrorAction SilentlyContinue)){return $null}
  $r=Run "gh" @("api","repos/$Repo/releases/latest","--jq",".tag_name")
  if($r.code -ne 0 -or [string]::IsNullOrWhiteSpace($r.out)){return $null}
  return $r.out.Trim()
}

function Add-Latest([string]$Name,[bool]$Required,[string]$LocalRaw,[string]$ReleaseRepo){
  $tag=LatestTag $ReleaseRepo
  if([string]::IsNullOrWhiteSpace($tag)){Add-Check "$Name.latest" $Required "UNKNOWN" "Current stable release could not be resolved." $LocalRaw "";return}
  $local=SemVer $LocalRaw;$latest=SemVer $tag
  if($null -eq $local -or $null -eq $latest){Add-Check "$Name.latest" $Required "UNKNOWN" "Local/latest version could not be parsed." $LocalRaw $tag;return}
  if($local -lt $latest){Add-Check "$Name.latest" $Required "UPDATE_REQUIRED" "Installed version is behind current stable." $local.ToString() $latest.ToString()}
  else{Add-Check "$Name.latest" $Required "PASS" "Installed version is current or newer than current stable." $local.ToString() $latest.ToString()}
}

function RepoFromRemote([string]$Remote){
  $m=[regex]::Match($Remote.Trim(),'github\.com[:/](?<owner>[^/]+)/(?<repo>[^/]+?)(?:\.git)?$')
  if(-not $m.Success){return ""}
  return "$($m.Groups['owner'].Value)/$($m.Groups['repo'].Value)"
}

function Check-Patterns([string]$Prefix,[string]$Raw,[string[]]$Patterns,[bool]$Required){
  foreach($p in $Patterns){
    try{$ok=$Raw -match $p}catch{$ok=$false}
    if($ok){Add-Check "$Prefix.pattern" $Required "PASS" "Required capability pattern visible: $p"}
    else{Add-Check "$Prefix.pattern" $Required "BLOCKED" "Required capability pattern missing/invalid: $p"}
  }
}

if($SelfTest){
  foreach($x in @(@("v1.2.3","1.2.3"),@("gh version 2.80.1","2.80.1"),@("rust-v0.154.0","0.154.0"))){
    $v=SemVer $x[0]
    if($null -eq $v -or $v.ToString() -ne $x[1]){throw "SelfTest failed"}
  }
  [pscustomobject]@{gate_contract_version=$ContractVersion;adapter_id=$AdapterId;adapter_version=$AdapterVersion;platform=$Platform;self_test="PASS";authority_effect="NONE"} | ConvertTo-Json
  exit 0
}

$pwshVersion=$PSVersionTable.PSVersion.ToString()
if($PSVersionTable.PSVersion.Major -ge 7){Add-Check "pwsh.runtime" $true "PASS" "PowerShell 7+ present." $pwshVersion ""}
else{Add-Check "pwsh.runtime" $true "BLOCKED" "PowerShell 7+ required." $pwshVersion ""}

if(Get-Command git -ErrorAction SilentlyContinue){$g=Run "git" @("--version");Add-Check "git.runtime" $true "PASS" "Git present." $g.out ""}
else{Add-Check "git.runtime" $true "BLOCKED" "Git not available in PATH."}

$ghVersion="";$ghAuth=$false
if(Get-Command gh -ErrorAction SilentlyContinue){
  $r=Run "gh" @("--version");$ghVersion=($r.out -split "\n")[0];Add-Check "gh.runtime" $true "PASS" "GitHub CLI present." $ghVersion ""
  $a=Run "gh" @("auth","status","-h","github.com")
  if($a.code -eq 0){$ghAuth=$true;Add-Check "gh.auth" $true "PASS" "GitHub CLI authenticated."}
  else{Add-Check "gh.auth" $true "BLOCKED" "GitHub CLI authentication unavailable/invalid."}
}else{
  Add-Check "gh.runtime" $true "BLOCKED" "GitHub CLI not available in PATH."
  Add-Check "gh.auth" $true "BLOCKED" "Cannot verify GitHub auth without gh."
}

if($Repository -and $ghAuth){
  $rv=Run "gh" @("repo","view",$Repository,"--json","nameWithOwner","--jq",".nameWithOwner")
  if($rv.code -eq 0 -and $rv.out.Trim().ToLowerInvariant() -eq $Repository.ToLowerInvariant()){Add-Check "gh.repo_read" $true "PASS" "Authenticated principal can read intended repo."}
  else{Add-Check "gh.repo_read" $true "BLOCKED" "Cannot read intended repo."}
  $rp=Run "gh" @("api","repos/$Repository","--jq",".permissions.push")
  if($rp.code -eq 0 -and $rp.out.Trim().ToLowerInvariant() -eq "true"){Add-Check "gh.repo_write" $true "PASS" "Repo reports push capability."}
  else{Add-Check "gh.repo_write" $true "BLOCKED" "Repo does not report push capability."}
}

$codexVersion=""
if($RequireCodex){
  if(Get-Command codex -ErrorAction SilentlyContinue){
    $cv=Run "codex" @("--version");$codexVersion=$cv.out;Add-Check "codex.runtime" $true "PASS" "Codex CLI present." $codexVersion ""
    $ca=Run "codex" @("login","status")
    if($ca.code -eq 0){Add-Check "codex.auth" $true "PASS" "Codex CLI reports authenticated session."}
    else{Add-Check "codex.auth" $true "BLOCKED" "Codex CLI auth unavailable/invalid."}
  }else{
    Add-Check "codex.runtime" $true "BLOCKED" "Codex CLI required but unavailable."
    Add-Check "codex.auth" $true "BLOCKED" "Cannot verify Codex auth."
  }
}else{Add-Check "codex.runtime" $false "NOT_REQUIRED" "Codex CLI not required by this invocation."}

$ocVersion=""
if($RequireOpenCode){
  if(Get-Command opencode -ErrorAction SilentlyContinue){
    $ov=Run "opencode" @("--version");$ocVersion=$ov.out;Add-Check "opencode.runtime" $true "PASS" "OpenCode present." $ocVersion ""
    $oa=Run "opencode" @("auth","list","--format","json");$txt=$oa.out.Trim()
    if($oa.code -eq 0 -and $txt -and $txt -notin @("[]","{}","null")){
      Add-Check "opencode.auth" $true "PASS" "OpenCode reports configured provider credentials."
      Check-Patterns "opencode.auth" $txt $RequiredOpenCodeAuthPattern $true
    }else{Add-Check "opencode.auth" $true "BLOCKED" "No detectable OpenCode provider credentials."}
    if($RequiredOpenCodeModelPattern.Count -gt 0){
      $om=Run "opencode" @("models","--refresh")
      if($om.code -eq 0){Add-Check "opencode.models" $true "PASS" "Model inventory refreshed without inference.";Check-Patterns "opencode.models" $om.out $RequiredOpenCodeModelPattern $true}
      else{Add-Check "opencode.models" $true "BLOCKED" "OpenCode model inventory refresh failed."}
    }else{Add-Check "opencode.models" $false "NOT_REQUIRED" "No model patterns required."}
  }else{
    Add-Check "opencode.runtime" $true "BLOCKED" "OpenCode required but unavailable."
    Add-Check "opencode.auth" $true "BLOCKED" "Cannot verify OpenCode credentials."
  }
}else{Add-Check "opencode.runtime" $false "NOT_REQUIRED" "OpenCode not required by this invocation."}

if($Repository){
  if(-not (Test-Path -LiteralPath $RepoPath)){Add-Check "repo.workspace" $true "BLOCKED" "Repo path does not exist."}
  else{
    $root=Run "git" @("-C",$RepoPath,"rev-parse","--show-toplevel")
    if($root.code -ne 0){Add-Check "repo.workspace" $true "BLOCKED" "RepoPath is not a readable Git worktree."}
    else{
      Add-Check "repo.workspace" $true "PASS" "Git worktree readable."
      $origin=Run "git" @("-C",$RepoPath,"remote","get-url","origin");$or=RepoFromRemote $origin.out
      if($origin.code -eq 0 -and $or.ToLowerInvariant() -eq $Repository.ToLowerInvariant()){Add-Check "repo.origin" $true "PASS" "Origin matches intended repo."}
      else{Add-Check "repo.origin" $true "BLOCKED" "Origin does not match intended repo."}

      if($ExpectedBase){
        $lh=Run "git" @("-C",$RepoPath,"rev-parse","HEAD")
        $rm=Run "git" @("-C",$RepoPath,"ls-remote","origin","refs/heads/main")
        $remoteSha=if($rm.code -eq 0 -and $rm.out){($rm.out -split "\s+")[0]}else{""}
        $ok=($lh.code -eq 0 -and $lh.out.Trim() -eq $ExpectedBase -and $remoteSha -eq $ExpectedBase)
        if($ok){Add-Check "repo.base" $RequireExactBase.IsPresent "PASS" "Local HEAD and remote main match expected base." $lh.out.Trim() $remoteSha}
        else{Add-Check "repo.base" $RequireExactBase.IsPresent "UPDATE_REQUIRED" "Base drift detected; live reconcile/rebase required." $(if($lh.code -eq 0){$lh.out.Trim()}else{""}) $remoteSha}
      }

      $dirty=Run "git" @("-C",$RepoPath,"status","--porcelain=v1")
      if($dirty.code -ne 0){Add-Check "repo.clean" $RequireCleanRepo.IsPresent "UNKNOWN" "Could not inspect worktree cleanliness."}
      elseif(-not $dirty.out){Add-Check "repo.clean" $RequireCleanRepo.IsPresent "PASS" "Worktree clean."}
      else{Add-Check "repo.clean" $RequireCleanRepo.IsPresent "BLOCKED" "Uncommitted changes present; no reset/clean/stash performed."}
    }
  }
}

if($ghAuth){
  Add-Latest "pwsh" $true $pwshVersion "PowerShell/PowerShell"
  if($ghVersion){Add-Latest "gh" $true $ghVersion "cli/cli"}
  if($RequireCodex -and $codexVersion){Add-Latest "codex" $true $codexVersion "openai/codex"}
  if($RequireOpenCode -and $ocVersion){Add-Latest "opencode" $true $ocVersion "anomalyco/opencode"}
}elseif($RequireLatest){Add-Check "release.currentness" $true "UNKNOWN" "Latest-version checks require working GitHub API access."}

if($ProbeProjectRemote -or $RequireProjectRemote){
  if(-not $ProjectProbeScript -or -not (Test-Path -LiteralPath $ProjectProbeScript)){
    Add-Check "project.remote" $RequireProjectRemote.IsPresent $(if($RequireProjectRemote){"BLOCKED"}else{"UNKNOWN"}) "No explicit project remote-probe adapter available."
  }else{
    try{
      $raw=(& $ProjectProbeScript -Json 2>&1 | Out-String).Trim();$probe=$raw|ConvertFrom-Json;$s=[string]$probe.state
      if($s -notin @("PASS","BLOCKED","UNKNOWN")){throw "bad state"}
      $d=if($null -ne $probe.detail){[string]$probe.detail}else{"Project adapter returned sanitized state."}
      Add-Check "project.remote" $RequireProjectRemote.IsPresent $s $d
    }catch{Add-Check "project.remote" $RequireProjectRemote.IsPresent $(if($RequireProjectRemote){"BLOCKED"}else{"UNKNOWN"}) "Project remote-probe adapter failed/returned invalid JSON."}
  }
}else{Add-Check "project.remote" $false "NOT_REQUIRED" "No project remote probe requested."}

$req=@($Checks|Where-Object{$_.required})
$block=@($req|Where-Object{$_.state -eq "BLOCKED"})
$unknown=@($req|Where-Object{$_.state -eq "UNKNOWN"})
$updates=@($req|Where-Object{$_.state -eq "UPDATE_REQUIRED"})
if($RequireLatest -and $updates.Count -gt 0){$block=@($block+$updates)}
$warnings=@($Checks|Where-Object{$_.state -eq "UPDATE_REQUIRED" -or ((-not $_.required) -and $_.state -in @("BLOCKED","UNKNOWN"))})
$overall=if($block.Count -gt 0){"BLOCKED"}elseif($unknown.Count -gt 0){"UNKNOWN"}elseif($warnings.Count -gt 0){"READY_WITH_WARNINGS"}else{"READY"}

$result=[ordered]@{gate_contract_version=$ContractVersion;adapter_id=$AdapterId;adapter_version=$AdapterVersion;platform=$Platform;execution_profile=$ExecutionProfile;repository=$Repository;checks=@($Checks);overall=$overall;blockers=@($block|ForEach-Object{$_.name});warnings=@($warnings|ForEach-Object{$_.name});authority_effect="NONE"}
if($Json){$result|ConvertTo-Json -Depth 8}else{Write-Host "Local Engineering Human Gate contract $ContractVersion / adapter $AdapterId $AdapterVersion";Write-Host "Overall: $overall";$Checks|Format-Table name,required,state,local_version,latest_version,detail -AutoSize}
if($overall -eq "BLOCKED"){exit 2}
if($overall -eq "UNKNOWN"){exit 3}
exit 0
