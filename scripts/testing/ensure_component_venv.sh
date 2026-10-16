#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
VENV="$ROOT/.venv"

if [[ ! -x "$VENV/bin/python" ]]; then
  PY=""
  for candidate in python3.12 python3.11 python3.10 python3; do
    if command -v "$candidate" >/dev/null 2>&1; then
      # Prefer a named 3.10–3.12 binary; accept python3 when it is 3.10+.
      if "$candidate" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)'; then
        PY="$candidate"
        break
      fi
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

# Telescope service component tests (AST-1725+) — FastAPI TestClient deps.
# Install fastapi/pydantic/httpx only (skip uvicorn[standard] — greenlet build
# fails on some host Pythons; routes under test do not need uvicorn).
if [[ -f "$ROOT/service/telescope/requirements.txt" ]]; then
  "$VENV/bin/pip" install -q 'fastapi>=0.115.0,<1' 'pydantic>=2,<3' 'httpx>=0.27'
fi

# Astral-agent service component tests (AST-2237+) — FastAPI + asyncpg import.
# Same uvicorn skip as Telescope; asyncpg needed for jobqueue/worker imports.
# AST-2239 provider wrappers also need anthropic SDK for import/collection.
if [[ -f "$ROOT/service/astral_agent/requirements.txt" ]]; then
  "$VENV/bin/pip" install -q 'fastapi>=0.115.0,<1' 'pydantic>=2,<3' 'httpx>=0.27' 'asyncpg>=0.30.0,<1' 'anthropic>=0.7.0,<1.0.0'
fi
