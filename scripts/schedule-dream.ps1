# Schedules dream.sh to run nightly with Windows Task Scheduler.
# Run from anywhere:
#   powershell -ExecutionPolicy Bypass -File scripts\schedule-dream.ps1            # 02:00 nightly
#   powershell -ExecutionPolicy Bypass -File scripts\schedule-dream.ps1 -Time 23:30
#   powershell -ExecutionPolicy Bypass -File scripts\schedule-dream.ps1 -Remove
# Needs Git for Windows (for Git Bash). The task runs while you're logged in.
param(
  [string]$Time = "02:00",
  [switch]$Remove
)
$ErrorActionPreference = "Stop"

# The repo is the folder above this script, wherever it was cloned.
$repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$taskName = "dream-lab dreaming ($(Split-Path $repo -Leaf))"

if ($Remove) {
  Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
  Write-Host "Removed '$taskName'."
  return
}

# Find Git Bash through git.exe (...\Git\cmd\git.exe -> ...\Git\bin\bash.exe).
# Don't use plain 'bash': on Windows that can be WSL's bash, which can't run this.
$git = (Get-Command git.exe -ErrorAction SilentlyContinue).Source
if (-not $git) { throw "git not found. Install Git for Windows: winget install --id Git.Git -e" }
$bash = Join-Path (Split-Path (Split-Path $git)) "bin\bash.exe"
if (-not (Test-Path $bash)) { throw "Git Bash not found at $bash" }

$repoBash = $repo -replace '\\', '/'          # C:/Users/... works in Git Bash
$cmd = "cd '$repoBash' && mkdir -p .dream-state && ./dream.sh >> .dream-state/dream.log 2>&1"

$action   = New-ScheduledTaskAction -Execute $bash -Argument "-lc `"$cmd`""
$trigger  = New-ScheduledTaskTrigger -Daily -At $Time
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger `
  -Settings $settings -Force | Out-Null

Write-Host "Scheduled '$taskName' daily at $Time."
Write-Host "Repo: $repo"
Write-Host "Log:  $repo\.dream-state\dream.log"
Write-Host "Test now: Start-ScheduledTask -TaskName '$taskName'"
