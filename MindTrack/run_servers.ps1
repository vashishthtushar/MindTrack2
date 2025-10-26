<#
run_servers.ps1

Launches the backend (FastAPI) and frontend (Streamlit) in separate PowerShell windows
and opens the frontend + API docs in the browser when the backend is ready.

Usage (PowerShell):
    .\run_servers.ps1

#>

$BackendPort = 8000
$FrontendPort = 8501

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$repoRoot = $scriptDir

$backendDir = Join-Path $repoRoot 'backend'
$frontendDir = Join-Path $repoRoot 'frontend'

Write-Host "Repository root: $repoRoot"
Write-Host "Backend dir: $backendDir"
Write-Host "Frontend dir: $frontendDir"

Write-Host "Starting backend in a new PowerShell window..."
$backendCmd = "cd `"$backendDir`"; python -m uvicorn app.main:app --host 127.0.0.1 --port $BackendPort"
Start-Process -FilePath "pwsh.exe" -ArgumentList "-NoExit", "-Command", $backendCmd

Start-Sleep -Seconds 2

Write-Host "Starting frontend in a new PowerShell window..."
$frontendCmd = "cd `"$frontendDir`"; streamlit run MindTracker_frontend/app.py --server.port $FrontendPort"
Start-Process -FilePath "pwsh.exe" -ArgumentList "-NoExit", "-Command", $frontendCmd

# Wait for backend health endpoint
$healthUrl = "http://127.0.0.1:$BackendPort/health"
$maxAttempts = 30
$attempt = 0
while ($attempt -lt $maxAttempts) {
    try {
        $resp = Invoke-RestMethod -Uri $healthUrl -TimeoutSec 2
        Write-Host "Backend is healthy:" ($resp | ConvertTo-Json -Depth 2)
        break
    } catch {
        Write-Host "Waiting for backend to be ready... (attempt $($attempt+1)/$maxAttempts)"
        Start-Sleep -Seconds 2
        $attempt++
    }
}

if ($attempt -ge $maxAttempts) {
    Write-Warning "Backend did not become healthy within timeout. Check backend logs in the opened window."
} else {
    Start-Sleep -Seconds 1
    $frontendUrl = "http://localhost:$FrontendPort"
    Write-Host "Opening frontend at $frontendUrl"
    Start-Process $frontendUrl

    $docsUrl = "http://127.0.0.1:$BackendPort/docs"
    Write-Host "Opening API docs at $docsUrl"
    Start-Process $docsUrl
}

Write-Host "Done."