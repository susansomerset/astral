#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
VENV="$ROOT/.venv"

if [[ ! -x "$VENV/bin/python" ]]; then
  PY=""
  for candidate in python3.12 python3.11 python3.10; do
    if command -v "$candidate" >/dev/null 2>&1; then
      PY="$candidate"
      break
    fi
  done
  if [[ -z "$PY" ]]; then
    echo "Python 3.10+ required for component tests (install python3.12 or set ASTRAL_PYTHON)." >&2
    exit 1
  fi
  "$PY" -m venv "$VENV"
  "$VENV/bin/pip" install -q -r "$ROOT/requirements.txt"
fi

"$VENV/bin/python" -c 'import sys; assert sys.version_info >= (3, 10), sys.version'
