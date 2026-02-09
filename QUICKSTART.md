# Quick Start (OS별 재현 가이드)
아래 명령은 프로젝트 루트(`README.md`가 있는 위치)에서 실행합니다.

### 1) 환경 세팅 스크립트로 한 번에 실행 (권장)
- Unix/macOS (현재 쉘에 활성화 반영): `source scripts/setup_mac.sh`
- Windows PowerShell (현재 세션에 활성화 반영): `. .\scripts\setup_windows.ps1`
- 스크립트는 기본적으로 pip/setuptools/wheel 업데이트를 시도합니다. 불필요하거나 네트워크 이슈가 있으면 macOS는 `SKIP_PIP_SETUP=1 source scripts/setup_mac.sh`, Windows는 `. .\scripts\setup_windows.ps1 -SkipPipSetup`를 사용합니다.
- 커스텀 인터프리터/venv (Unix/macOS): `PYTHON_BIN=python3.11 VENV_DIR=.venv-dev source scripts/setup_mac.sh`
- 커스텀 인터프리터/venv (Windows): `. .\scripts\setup_windows.ps1 -PythonBin "C:\Path\to\python.exe" -VenvDir ".venv-dev"`

### 2) Unix/macOS (bash, zsh, 수동 설정)
```bash
# 프로젝트 폴더로 이동
cd /path/to/ocr-parsing-project

# 가상환경 생성 (Python 3 명시)
python3 -m venv .venv

# 가상환경 활성화
source .venv/bin/activate

# 버전 확인
which python
python --version
python -m pip --version
```

### 3) Windows (PowerShell, 수동 설정)
```powershell
# 프로젝트 폴더로 이동
cd C:\path\to\ocr-parsing-project

# Python 설치 확인 (없으면 설치)
python --version
# winget install -e --id Python.Python.3.12

# 가상환경 생성/활성화
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 실행 정책 오류 시 1회 허용
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 버전 확인
python --version
python -m pip --version
```

### 4) 패키징 도구 관련 (선택 / 문제 발생 시)
- 선택(환경 정리): `python -m pip install --upgrade pip setuptools wheel`
- 문제 발생 시(Python 3.9): `python -m pip install "setuptools<70"` (`distutils` 관련 오류 대응)

### 5) Windows 트러블슈팅: `python`이 Store 별칭으로 잡힐 때
PowerShell에서 `python`이 실제 인터프리터가 아니라 Store 별칭이면 실행이 실패할 수 있습니다.

```powershell
# 현재 python이 무엇을 가리키는지 확인
Get-Command python
where.exe python

# 현재 세션에서만 실제 python.exe로 별칭 강제 (예시 경로)
Set-Alias python "C:\Users\<USER>\AppData\Local\Programs\Python\Python312\python.exe"

# 확인
python --version
python .\src\ocr-parser\cli.py
```

추가로 Windows 설정에서 `App execution aliases`의 `python.exe`, `python3.exe`를 끄면 재발을 줄일 수 있습니다.

### 6) `python3` vs `python` 사용 기준
- 가상환경 생성 전: `python3`(Unix/macOS) 또는 `python`(Windows)로 Python 3를 명시
- 가상환경 활성화 후: `python -m pip`와 `python ...`를 사용해 현재 venv 인터프리터와 pip를 강제로 일치
- 목적: OS/셸별 실행기 이름 차이와 pip/python 불일치 문제를 줄여 재현성 확보

## 로컬 실행 방법 (재현 가능)
환경 세팅(스크립트 또는 수동)이 끝났다는 전제에서 실행합니다.

1. 기본 실행 (`data/` 하위 JSON 탐색)
- Unix/macOS: `python src/ocr-parser/cli.py`
- Windows PowerShell: `python .\src\ocr-parser\cli.py`

2. 특정 파일만 실행
- Unix/macOS: `python src/ocr-parser/cli.py data/sample_01.json`
- Windows PowerShell: `python .\src\ocr-parser\cli.py .\data\sample_01.json`

3. 디렉터리 재귀 탐색 + 수집 로그 출력
- Unix/macOS: `python src/ocr-parser/cli.py data -r -v`
- Windows PowerShell: `python .\src\ocr-parser\cli.py .\data -r -v`

4. 샘플 4개 일괄 실행
- Unix/macOS: `python src/ocr-parser/cli.py data/sample_01.json data/sample_02.json data/sample_03.json data/sample_04.json`
- Windows PowerShell: `python .\src\ocr-parser\cli.py .\data\sample_01.json .\data\sample_02.json .\data\sample_03.json .\data\sample_04.json`

5. 결과 확인
- Unix/macOS: `ls -lah result`
- Windows PowerShell: `Get-ChildItem .\result`
- 예시 산출물: `result/sample_04_parsed.json`, `result/sample_04_parsed.csv`
