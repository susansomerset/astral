#!/usr/bin/env bash
# Joan operator entry — run integration harness on Railway test service (AST-712).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
"$ROOT/scripts/testing/verify_integration_deploy_ref.sh"
LOG_DIR="$ROOT/debug/integration-operator"
mkdir -p "$LOG_DIR"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
LOG="$LOG_DIR/run-${STAMP}.log"
if ! command -v railway >/dev/null 2>&1; then
  echo "BLOCKED: railway CLI not installed" >&2
  exit 2
fi
set +e
railway run -- bash -lc 'cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" && ./scripts/testing/run_integration_tests.sh' 2>&1 | tee "$LOG"
STATUS=${PIPESTATUS[0]}
set -e
echo "log: $LOG"
exit "$STATUS"
