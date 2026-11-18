param([int]$RefreshSeconds = 5)

$ErrorActionPreference = 'SilentlyContinue'
$projectRoot = Split-Path -Parent $PSScriptRoot
$auditRoot = Join-Path $projectRoot 'manuscript\research_draft_v2\release_audit'
$workerFile = Join-Path $auditRoot 'ANTIGRAVITY_MASTER_WORKER.json'
$statusFile = Join-Path $auditRoot 'ANTIGRAVITY_MASTER_STATUS.md'
$reportFile = Join-Path $auditRoot 'ANTIGRAVITY_RELEASE_FINAL_REPORT.md'
$logFile = Join-Path $auditRoot 'antigravity_master_worker.log'
$Host.UI.RawUI.WindowTitle = 'Antigravity - LIVE research paper progress'

while ($true) {
    $worker = $null
    if (Test-Path -LiteralPath $workerFile) {
        try { $worker = Get-Content -LiteralPath $workerFile -Raw | ConvertFrom-Json } catch {}
    }
    $actualProcess = $null
    if ($worker.antigravity_pid) {
        $actualProcess = Get-Process -Id $worker.antigravity_pid -ErrorAction SilentlyContinue
    }
    $reportExists = Test-Path -LiteralPath $reportFile
    Clear-Host
    Write-Host 'ANTIGRAVITY - LIVE RESEARCH PAPER PROGRESS' -ForegroundColor Cyan
    Write-Host ('Refreshed: ' + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))
    Write-Host ('Project: ' + $projectRoot)
    Write-Host ''
    if ($actualProcess) {
        Write-Host ('Worker is RUNNING | PID ' + $worker.antigravity_pid) -ForegroundColor Green
    } elseif ($worker.status -eq 'RUNNING') {
        Write-Host 'Worker process is not currently found. The saved RUNNING label may be stale.' -ForegroundColor Yellow
    } else {
        Write-Host ('Worker status: ' + $worker.status + ' | exit code: ' + $worker.exit_code) -ForegroundColor Yellow
    }
    if (Test-Path -LiteralPath $statusFile) {
        $statusItem = Get-Item -LiteralPath $statusFile
        Write-Host ('Agent status file updated: ' + $statusItem.LastWriteTime.ToString('yyyy-MM-dd HH:mm:ss'))
        Write-Host ''
        Get-Content -LiteralPath $statusFile | Select-Object -First 65 | ForEach-Object {
            if ($_ -match 'BLOCKED|FAILED|ERROR') { Write-Host $_ -ForegroundColor Red }
            elseif ($_ -match 'COMPLETED|PASSED') { Write-Host $_ -ForegroundColor Green }
            elseif ($_ -match 'RUNNING|Current Phase') { Write-Host $_ -ForegroundColor Yellow }
            else { Write-Host $_ }
        }
    } else {
        Write-Host 'Waiting for the agent to write its first status update.' -ForegroundColor Yellow
    }
    Write-Host ''
    Write-Host 'RECENT CLI OUTPUT' -ForegroundColor Cyan
    if (Test-Path -LiteralPath $logFile) { Get-Content -LiteralPath $logFile -Tail 10 | ForEach-Object { Write-Host $_ } }
    Write-Host ''
    if ($reportExists) {
        Write-Host 'FINAL REPORT EXISTS - inspect its result; report presence alone does not prove all checks passed.' -ForegroundColor Cyan
        Write-Host $reportFile
        Get-Content -LiteralPath $reportFile -TotalCount 16 | ForEach-Object { Write-Host $_ }
    } else {
        Write-Host 'NOT FINISHED: no final release report yet.' -ForegroundColor Yellow
    }
    Write-Host ''
    Write-Host 'This window monitors the actual worker. Closing it does not stop the worker.' -ForegroundColor DarkGray
    Write-Host 'Ctrl+C stops this monitor only. Refresh every 5 seconds.' -ForegroundColor DarkGray
    Start-Sleep -Seconds $RefreshSeconds
}
