param(
    [string]$TaskName = "DataCuse Syracuse Property Atlas Hourly",
    [int]$StartInMinutes = 5,
    [int]$IntervalMinutes = 15,
    [switch]$NoPush
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$Runner = Join-Path $ProjectRoot "scripts\run_hourly.ps1"
$PowerShell = Join-Path $env:SystemRoot "System32\WindowsPowerShell\v1.0\powershell.exe"
$PushArg = if ($NoPush) { "" } else { " -Push" }
$Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$Runner`"$PushArg"

$Action = New-ScheduledTaskAction `
    -Execute $PowerShell `
    -Argument $Arguments `
    -WorkingDirectory $ProjectRoot

$Start = (Get-Date).AddMinutes($StartInMinutes)
$Trigger = New-ScheduledTaskTrigger `
    -Once `
    -At $Start `
    -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes) `
    -RepetitionDuration (New-TimeSpan -Days 3650)

$Settings = New-ScheduledTaskSettingsSet `
    -MultipleInstances IgnoreNew `
    -StartWhenAvailable `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries

$Principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType Interactive `
    -RunLevel Limited

$Task = New-ScheduledTask `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Principal $Principal `
    -Description "Publishes one Syracuse Property Atlas entry, commits DataCuse updates, and pushes to origin/main."

Register-ScheduledTask `
    -TaskName $TaskName `
    -InputObject $Task `
    -Force | Out-Null

Write-Host "Registered scheduled task: $TaskName"
Write-Host "Starts: $Start"
Write-Host "Repeats: every $IntervalMinutes minutes"
Write-Host "Command: $PowerShell $Arguments"
