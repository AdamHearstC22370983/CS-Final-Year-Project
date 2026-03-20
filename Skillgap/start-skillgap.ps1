# Skillgap launcher
# Skillgap/start-skillgap.ps1

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=============================" -ForegroundColor Cyan
Write-Host " Starting Skillgap..." -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan
Write-Host ""

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendPath = Join-Path $projectRoot "backend"
$frontendPath = Join-Path $projectRoot "frontend"
$venvPython = Join-Path $projectRoot "venv\Scripts\python.exe"
$pidFile = Join-Path $projectRoot ".skillgap-pids.json"

if (-not (Test-Path $venvPython)) {
    Write-Host "Backend Python executable not found." -ForegroundColor Red
    exit 1
}

Write-Host "Starting backend..." -ForegroundColor Green

$backendProcess = Start-Process `
    -FilePath $venvPython `
    -ArgumentList "-m", "uvicorn", "app.main:app", "--reload" `
    -WorkingDirectory $backendPath `
    -PassThru `
    -WindowStyle Hidden

Start-Sleep -Seconds 2

if ($backendProcess.HasExited) {
    Write-Host "Backend failed to start." -ForegroundColor Red
    exit 1
}

Write-Host "Backend started." -ForegroundColor Green
Write-Host ""

Write-Host "Starting frontend..." -ForegroundColor Green

$frontendProcess = Start-Process `
    -FilePath "cmd.exe" `
    -ArgumentList "/c", "npm", "run", "dev" `
    -WorkingDirectory $frontendPath `
    -PassThru `
    -WindowStyle Hidden

Start-Sleep -Seconds 5

if ($frontendProcess.HasExited) {
    Write-Host "Frontend failed to start." -ForegroundColor Red
    exit 1
}

$pids = @{
    backendPid = $backendProcess.Id
    frontendPid = $frontendProcess.Id
}

$pids | ConvertTo-Json | Set-Content $pidFile

Write-Host "Frontend started." -ForegroundColor Green
Write-Host ""
Write-Host "Skillgap is now running." -ForegroundColor Green
Write-Host ""
Write-Host "Links:" -ForegroundColor Yellow
Write-Host " - Website:  http://localhost:5173" -ForegroundColor White
Write-Host " - Backend:  http://127.0.0.1:8000" -ForegroundColor White
Write-Host " - API Docs: http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Use stop-skillgap.ps1 to stop both services." -ForegroundColor Yellow
Write-Host ""

Start-Process "http://localhost:5173"