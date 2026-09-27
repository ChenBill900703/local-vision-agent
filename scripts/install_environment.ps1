param()
$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
$taskPython = Join-Path $taskRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $taskPython)) {
    throw 'Create the project .venv with 64-bit Python 3.11 first; this script never changes system Python.'
}
& $taskPython -c "import sys,struct; assert sys.version_info[:2] == (3,11) and struct.calcsize('P') == 8, 'Requires CPython 3.11 x64'"
if ($LASTEXITCODE -ne 0) { throw 'Unsupported Python interpreter' }
& $taskPython -m pip install --index-url https://pypi.org/simple -r (Join-Path $taskRoot 'requirements-win-cu126.lock')
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed' }
& $taskPython -m pip install --no-deps --no-build-isolation -e $taskRoot
if ($LASTEXITCODE -ne 0) { throw 'Project installation failed' }
& $taskPython -m pip check
if ($LASTEXITCODE -ne 0) { throw 'Dependency consistency check failed' }
Write-Output 'Installed pinned environment. No GPU test or model download was performed.'
