$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot
$Host.UI.RawUI.WindowTitle = 'Antigravity - ACTUAL INTERACTIVE CLI'
Write-Host 'Actual Antigravity CLI. If a command needs approval, its prompt appears HERE.' -ForegroundColor Cyan
& (Join-Path $env:LOCALAPPDATA 'agy\bin\agy.exe') --conversation dcabdedc-5411-4145-9748-516ca60c380f --mode accept-edits --settings (Join-Path $PSScriptRoot 'antigravity-continuation-settings.json') --prompt-interactive 'The headless continuation stopped because a command permission was denied. This is now an interactive terminal: show specific permission prompts here if needed. Read docs/ANTIGRAVITY_CONTINUE.md and continue implementation, tests and real studies from current files. Update ANTIGRAVITY_STATUS.md immediately with actual progress and write ANTIGRAVITY_REPORT.md. Do not claim the prior run completed. Preserve all existing work.'
Read-Host 'Antigravity ended. Press Enter to close'
