#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

if [[ -n "${ASTRAL_PYTHON:-}" ]]; then
  PYTHON="$ASTRAL_PYTHON"
else
  # Component tests match product runtime (3.10+); default venv uses newest available 3.10+.
  "$ROOT/scripts/testing/ensure_component_venv.sh"
  PYTHON="$ROOT/.venv/bin/python"
fi

export ASTRAL_DB_DIR="${ASTRAL_DB_DIR:-$ROOT/data}"
mkdir -p "$ASTRAL_DB_DIR"

COV_DIR="$ROOT/tests/.coverage"
mkdir -p "$COV_DIR/frontend/.tmp"
export COVERAGE_FILE="$COV_DIR/pytest-component"

# With no args we run full tests/component coverage gate; callers may pass narrowed
# paths or `-k`/node IDs (manifest §7.13w relies on `./run_component_tests.sh <paths>`).
PY_TARGETS=(tests/component)
if (("$#" > 0)); then
  PY_TARGETS=("$@")
fi

"$PYTHON" -m pytest "${PY_TARGETS[@]}" \
  --cov=src \
  --cov-branch \
  --cov-report=term-missing:skip-covered \
  --cov-report=json:"$COV_DIR/component.json"

# LOCKED_AT_100 compares branch % for every tracked src file; a narrowed pytest list
# still records partial branch hits under --cov=src—gate only when we're running the
# whole component tree from this script ($# == 0 → PY_TARGETS defaulted to tests/component).
if (("$#" == 0)); then
  # Prep-uat §6 on origin/ftr/*: composite product may trail dev on LOCKED_AT_100 branches.
  if [[ "${ASTRAL_FTR_COVERAGE_INTEGRATION:-}" != "1" ]] && [[ -n "$(git rev-parse --verify HEAD 2>/dev/null || true)" ]]; then
    if git branch -r --contains HEAD 2>/dev/null | grep -qE 'origin/ftr/'; then
      export ASTRAL_FTR_COVERAGE_INTEGRATION=1
    fi
  fi
  "$PYTHON" "$ROOT/scripts/testing/check_per_file_coverage.py" "$COV_DIR/component.json"
fi

# Narrowed pytest manifests (trailing paths) gate backend-only tickets; full Vitest tail is §6b zero-arg harness only.
if (("$#" == 0)) && [[ -f "$ROOT/src/ui/frontend/package.json" ]]; then
  export ASTRAL_VITEST_MAX_WORKERS="${ASTRAL_VITEST_MAX_WORKERS:-2}"
  (cd "$ROOT/src/ui/frontend" && npm install --silent && npm run test:component:coverage)
  # Frontend gate: Vitest exits 0 above. check_frontend_coverage.py enforces LOCKED_AT_100 only;
  # that list stays empty unless Product adopts per-file branch locks (docs/test-bible/README.md §6b).
  "$PYTHON" "$ROOT/scripts/testing/check_frontend_coverage.py" "$COV_DIR/frontend/coverage-summary.json" "$ROOT"
fi
