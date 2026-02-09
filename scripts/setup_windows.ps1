<#
Usage (PowerShell):
  . .\scripts\setup_windows.ps1
  . .\scripts\setup_windows.ps1 -PythonBin "C:\Path\to\Python312\python.exe" -VenvDir ".venv"

Note: dot-sourcing (앞에 점과 공백)으로 실행해야 현재 세션에 venv 활성화가 반영됩니다.
#>
param(
  [string]$PythonBin = "python",
  [string]$VenvDir = ".venv"
)

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "[setup] python bin: $PythonBin"
Write-Host "[setup] venv dir : $VenvDir"

& $PythonBin -m venv $VenvDir
. "$ProjectRoot\$VenvDir\Scripts\Activate.ps1"

python -m pip install --upgrade pip setuptools wheel

# Python 3.9에서 distutils 관련 이슈 예방용 (필요 시만 적용)
$pyVer = python -c "import sys; print(sys.version.split()[0])"
if ($pyVer.StartsWith("3.9.")) {
  python -m pip install "setuptools<70"
}

Write-Host "[setup] python: $(python --version)"
Write-Host "[setup] pip   : $(python -m pip --version)"
