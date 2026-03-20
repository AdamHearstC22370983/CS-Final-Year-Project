# Skillgap stopper
# Skillgap/stop-skillgap.ps1

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$pidFile = Join-Path $projectRoot ".skillgap-pids.json"

Write-Host ""
Write-Host "Stopping Skillgap..." -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $pidFile)) {
    Write-Host "No PID file found. Nothing to stop." -ForegroundColor Yellow
    exit 0
}

try {
    $pids = Get-Content $pidFile | ConvertFrom-Json

    if ($pids.backendPid) {
        $proc = Get-Process -Id $pids.backendPid -ErrorAction SilentlyContinue
        if ($proc) {
            Stop-Process -Id $pids.backendPid -Force
            Write-Host "Backend stopped." -ForegroundColor Green
        }
    }

    if ($pids.frontendPid) {
        $proc = Get-Process -Id $pids.frontendPid -ErrorAction SilentlyContinue
        if ($proc) {
            Stop-Process -Id $pids.frontendPid -Force
            Write-Host "Frontend stopped." -ForegroundColor Green
        }
    }

    Remove-Item $pidFile -ErrorAction SilentlyContinue
    Write-Host ""
    Write-Host "Skillgap has been stopped." -ForegroundColor Cyan
}
catch {
    Write-Host "Could not fully stop services. You may need to end them manually." -ForegroundColor Red
}