#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   source scripts/setup_mac.sh
#   PYTHON_BIN=python3.11 VENV_DIR=.venv-dev source scripts/setup_mac.sh
#
# Note: source로 실행해야 현재 쉘에 venv 활성화가 반영됩니다.

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="${VENV_DIR:-.venv}"

echo "[setup] python bin: ${PYTHON_BIN}"
echo "[setup] venv dir : ${VENV_DIR}"

"${PYTHON_BIN}" -m venv "${VENV_DIR}"
# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

python -m pip install --upgrade pip setuptools wheel

# Python 3.9에서 distutils 관련 이슈 예방용 (필요 시만 적용)
PY_VER="$(python -c 'import sys; print(sys.version.split()[0])')"
if [[ "${PY_VER}" == 3.9.* ]]; then
  python -m pip install "setuptools<70"
fi

echo "[setup] python: $(python --version)"
echo "[setup] pip   : $(python -m pip --version)"
