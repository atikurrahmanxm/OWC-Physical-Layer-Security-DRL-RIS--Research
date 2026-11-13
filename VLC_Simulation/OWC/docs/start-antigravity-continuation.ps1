$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot
$agyExe = Join-Path $env:LOCALAPPDATA 'agy\bin\agy.exe'
$settingsPath = Join-Path $PSScriptRoot 'antigravity-continuation-settings.json'
$stdoutPath = Join-Path $projectRoot 'paper_audit\antigravity-continuation.stdout.log'
$stderrPath = Join-Path $projectRoot 'paper_audit\antigravity-continuation.stderr.log'
$statusPath = Join-Path $projectRoot 'ANTIGRAVITY_STATUS.md'
$taskPrompt = 'Read docs/ANTIGRAVITY_CONTINUE.md and execute the user-authorized continuation now. Update ANTIGRAVITY_STATUS.md at milestones; finish with ANTIGRAVITY_REPORT.md and actual test and experiment evidence. Do not merely plan.'
$cliArgs = @('--conversation','dcabdedc-5411-4145-9748-516ca60c380f','--mode','accept-edits','--settings',('"' + $settingsPath + '"'),'--print-timeout','0','--output-format','text','--print',('"' + $taskPrompt + '"'))
$worker = Start-Process -FilePath $agyExe -ArgumentList $cliArgs -WorkingDirectory $projectRoot -WindowStyle Hidden -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath -PassThru
@{pid=$worker.Id;started=(Get-Date).ToString('o');executable=$agyExe;stdout=$stdoutPath;stderr=$stderrPath;status=$statusPath} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $projectRoot 'paper_audit\antigravity-continuation-process.json') -Encoding UTF8
$Host.UI.RawUI.WindowTitle = 'Antigravity - LIVE project continuation'
while (-not $worker.HasExited) {
    Clear-Host
    Write-Host 'ANTIGRAVITY CLI - LIVE PROJECT CONTINUATION' -ForegroundColor Cyan
    Write-Host ('Actual worker PID: ' + $worker.Id + ' | Running: ' + (-not $worker.HasExited) + ' | ' + (Get-Date)) -ForegroundColor Green
    Write-Host ('Executable: ' + $agyExe)
    Write-Host ('Project: ' + $projectRoot)
    Write-Host 'Status written by the agent:' -ForegroundColor Yellow
    if (Test-Path -LiteralPath $statusPath) { Get-Content -LiteralPath $statusPath -Tail 28 }
    if ((Test-Path -LiteralPath $stderrPath) -and (Get-Item -LiteralPath $stderrPath).Length -gt 0) {
        Write-Host 'Latest CLI messages:' -ForegroundColor Yellow
        Get-Content -LiteralPath $stderrPath -Tail 8
    }
    Write-Host 'CLI final output: paper_audit\antigravity-continuation.stdout.log'
    Write-Host 'Final user report: ANTIGRAVITY_REPORT.md'
    Write-Host 'This window monitors the worker. Closing it does not intentionally cancel the worker.'
    Start-Sleep -Seconds 5
    $worker.Refresh()
}
Write-Host ('Antigravity exited. Exit code: ' + $worker.ExitCode) -ForegroundColor Yellow
if (Test-Path -LiteralPath $stdoutPath) { Get-Content -LiteralPath $stdoutPath -Tail 80 }
if (Test-Path -LiteralPath $stderrPath) { Get-Content -LiteralPath $stderrPath -Tail 20 }
Write-Host 'Check ANTIGRAVITY_STATUS.md and ANTIGRAVITY_REPORT.md for verified results.'
Read-Host 'Press Enter to close this monitor'
