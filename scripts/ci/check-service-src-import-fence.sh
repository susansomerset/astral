#!/usr/bin/env bash
# AST-1727 — fail if service/telescope ↔ src imports exist either direction.
# Matches real import lines only (not docstrings/comments saying "import src").
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

# Same spirit as tests/component/service/test_telescope_fence.py
SRC_IN_SERVICE="$(rg -n --glob '*.py' -e '^\s*(from|import)\s+src(\.|\s|,|$)' service/telescope || true)"
SERVICE_IN_SRC="$(rg -n --glob '*.py' -e '^\s*(from|import)\s+service(\.|\s|,|$)' src || true)"

fail=0
if [[ -n "$SRC_IN_SERVICE" ]]; then
  echo "import fence: service/telescope must not import src:"
  echo "$SRC_IN_SERVICE"
  fail=1
fi
if [[ -n "$SERVICE_IN_SRC" ]]; then
  echo "import fence: src must not import service:"
  echo "$SERVICE_IN_SRC"
  fail=1
fi
if [[ "$fail" -ne 0 ]]; then
  exit 1
fi
echo "import fence: ok (service/telescope ↔ src)"
