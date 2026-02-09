<#
Usage (PowerShell):
  . .\scripts\setup_windows.ps1
  . .\scripts\setup_windows.ps1 -PythonBin "C:\Path\to\Python312\python.exe" -VenvDir ".venv"
  . .\scripts\setup_windows.ps1 -SkipPipSetup

Note: dot-sourcing (앞에 점과 공백)으로 실행해야 현재 세션에 venv 활성화가 반영됩니다.
#>
param(
  [string]$PythonBin = "python",
  [string]$VenvDir = ".venv",
  [switch]$SkipPipSetup
)

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "[setup] python bin: $PythonBin"
Write-Host "[setup] venv dir : $VenvDir"

& $PythonBin -m venv $VenvDir
. "$ProjectRoot\$VenvDir\Scripts\Activate.ps1"

function Invoke-PipCommand {
  param(
    [string[]]$Args,
    [string]$WarningMessage
  )

  & python -m pip @Args
  if ($LASTEXITCODE -ne 0) {
    Write-Warning $WarningMessage
    return $false
  }
  return $true
}

if ($SkipPipSetup) {
  Write-Host "[setup] pip/setuptools/wheel 설치 단계를 건너뜁니다 (-SkipPipSetup)."
} else {
  Invoke-PipCommand `
    -Args @("install", "--upgrade", "pip", "setuptools", "wheel") `
    -WarningMessage "pip/setuptools/wheel 업데이트에 실패했습니다. 실행은 계속합니다." | Out-Null

  # Python 3.9에서 distutils 관련 이슈 예방용 (필요 시만 적용)
  $pyVer = python -c "import sys; print(sys.version.split()[0])"
  if ($pyVer.StartsWith("3.9.")) {
    Invoke-PipCommand `
      -Args @("install", "setuptools<70") `
      -WarningMessage "setuptools<70 적용에 실패했습니다. 필요 시 수동으로 재시도하세요." | Out-Null
  }
}

Write-Host "[setup] python: $(python --version)"
Write-Host "[setup] pip   : $(python -m pip --version)"
