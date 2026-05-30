param(
    [switch]$Push,
    [int]$Id,
    [string]$Address
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$RepoRoot = Resolve-Path (Join-Path $ProjectRoot "..\..")
$LockFile = Join-Path $ProjectRoot "data\hourly.lock"
$LogDir = Join-Path $ProjectRoot "logs"
$LogFile = Join-Path $LogDir ("hourly-" + (Get-Date -Format "yyyyMMdd") + ".log")

New-Item -ItemType Directory -Force -Path (Join-Path $ProjectRoot "data") | Out-Null
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Write-Log {
    param([string]$Message)
    $line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Message
    Add-Content -Path $LogFile -Value $line
    Write-Host $line
}

if (Test-Path $LockFile) {
    $age = (Get-Date) - (Get-Item $LockFile).LastWriteTime
    if ($age.TotalHours -lt 2) {
        Write-Log "Another atlas run appears active; exiting."
        exit 0
    }
    Write-Log "Removing stale lock file."
    Remove-Item -LiteralPath $LockFile -Force
}

try {
    Set-Content -Path $LockFile -Value (Get-Date -Format o)
    Write-Log "Starting Syracuse Property Atlas run."

    Push-Location $ProjectRoot
    try {
        $AtlasArgs = @("scripts\property_atlas.py", "run-once")
        if ($Id) {
            $AtlasArgs += @("--id", $Id)
        }
        if ($Address) {
            $AtlasArgs += @("--address", $Address)
        }
        python @AtlasArgs
    }
    finally {
        Pop-Location
    }

    Push-Location $RepoRoot
    try {
        git add .gitignore index.html public/syracuse_property_atlas.svg projects/syracuse-property-atlas

        $changes = git status --porcelain
        if (-not $changes) {
            Write-Log "No site changes to commit."
            exit 0
        }

        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
        git commit -m "Publish Syracuse Property Atlas update $timestamp"
        Write-Log "Committed Syracuse Property Atlas update."

        if ($Push) {
            git push origin main
            Write-Log "Pushed update to origin/main."
        }
        else {
            Write-Log "Push not requested; commit remains local."
        }
    }
    finally {
        Pop-Location
    }
}
catch {
    Write-Log ("ERROR: " + $_.Exception.Message)
    throw
}
finally {
    if (Test-Path $LockFile) {
        Remove-Item -LiteralPath $LockFile -Force
    }
}
