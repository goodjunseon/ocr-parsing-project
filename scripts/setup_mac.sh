#!/usr/bin/env bash
# Usage:
#   source scripts/setup_mac.sh
#   PYTHON_BIN=python3.11 VENV_DIR=.venv-dev source scripts/setup_mac.sh
#   SKIP_PIP_SETUP=1 source scripts/setup_mac.sh
#
# Note: source로 실행해야 현재 쉘에 venv 활성화가 반영됩니다.

if [[ -n "${ZSH_VERSION:-}" ]]; then
  SCRIPT_SOURCE="${(%):-%N}"
elif [[ -n "${BASH_SOURCE[0]:-}" ]]; then
  SCRIPT_SOURCE="${BASH_SOURCE[0]}"
else
  SCRIPT_SOURCE="$0"
fi

SCRIPT_DIR="$(cd "$(dirname "${SCRIPT_SOURCE}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}"

PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="${VENV_DIR:-.venv}"
SKIP_PIP_SETUP="${SKIP_PIP_SETUP:-0}"

echo "[setup] python bin: ${PYTHON_BIN}"
echo "[setup] venv dir : ${VENV_DIR}"

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  echo "[setup] 오류: ${PYTHON_BIN} 명령을 찾을 수 없습니다."
  return 1 2>/dev/null || exit 1
fi

"${PYTHON_BIN}" -m venv "${VENV_DIR}"
# shellcheck disable=SC1091
source "${PROJECT_ROOT}/${VENV_DIR}/bin/activate"

if [[ "${SKIP_PIP_SETUP}" == "1" ]]; then
  echo "[setup] pip/setuptools/wheel 설치 단계를 건너뜁니다 (SKIP_PIP_SETUP=1)."
else
  if ! python -m pip install --upgrade pip setuptools wheel; then
    echo "[setup] 경고: pip/setuptools/wheel 업데이트에 실패했습니다. 실행은 계속합니다."
  fi

  # Python 3.9에서 distutils 관련 이슈 예방용 (필요 시만 적용)
  PY_VER="$(python -c 'import sys; print(sys.version.split()[0])')"
  if [[ "${PY_VER}" == 3.9.* ]]; then
    if ! python -m pip install "setuptools<70"; then
      echo "[setup] 경고: setuptools<70 적용에 실패했습니다. 필요 시 수동으로 재시도하세요."
    fi
  fi
fi

echo "[setup] python: $(python --version)"
echo "[setup] pip   : $(python -m pip --version)"
