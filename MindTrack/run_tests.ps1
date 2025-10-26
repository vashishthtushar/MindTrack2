<#
run_tests.ps1

Open a new PowerShell window and run the backend test suite independently.
This keeps the test run separate from any running servers/windows.

Usage (PowerShell):
    .\run_tests.ps1

Optional: edit the $EnvActivate line to activate a conda/venv before running tests.
#>

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$repoRoot = $scriptDir
$backendDir = Join-Path $repoRoot 'backend'

Write-Host "Starting tests in a new PowerShell window..."

# Command to optionally activate a virtual environment; edit if you use conda or venv.
# Example conda activation (uncomment and replace):
# $EnvActivate = "conda activate myenv;"
$EnvActivate = ""

$testCmd = "cd `"$backendDir`"; $EnvActivate python -m pytest -q"

Start-Process -FilePath "pwsh.exe" -ArgumentList "-NoExit", "-Command", $testCmd

Write-Host "Launched tests in a separate window. Check that window for test output."