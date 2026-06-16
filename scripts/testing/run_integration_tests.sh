#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
# Reuse component venv bootstrap
if [[ -n "${ASTRAL_PYTHON:-}" ]]; then
  PYTHON="$ASTRAL_PYTHON"
else
  "$ROOT/scripts/testing/ensure_component_venv.sh"
  PYTHON="$ROOT/.venv/bin/python"
fi
export ASTRAL_INTEGRATION_MODE=1
unset ASTRAL_ALLOW_LIVE_EXTERNAL_IO
export ASTRAL_DB_DIR="${ASTRAL_DB_DIR:-$ROOT/data}"
mkdir -p "$ASTRAL_DB_DIR"
PY_TARGETS=(tests/integration)
if (("$#" > 0)); then
  PY_TARGETS=("$@")
fi
exec "$PYTHON" -m pytest "${PY_TARGETS[@]}"
