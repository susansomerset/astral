#!/usr/bin/env bash
# Post-deploy integration gate: Railway harness + GitHub status + Linear on fail (AST-818).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
git fetch origin
SHA="$(git rev-parse origin/dev)"
SHORT="${SHA:0:7}"
LOG=""
HARNESS_STATUS=0
GATE_LOG_DIR="$ROOT/debug/integration-operator"
mkdir -p "$GATE_LOG_DIR"

WAIT="${ASTRAL_INTEGRATION_GATE_WAIT_SEC:-30}"
MAX_TRIES="${ASTRAL_INTEGRATION_GATE_MAX_TRIES:-40}"
TRIES=0
until "$ROOT/scripts/testing/verify_integration_deploy_ref.sh" "$SHA"; do
  TRIES=$((TRIES + 1))
  if (( TRIES >= MAX_TRIES )); then
    "$ROOT/scripts/post_github_commit_status.sh" "$SHA" failure "deploy pin timeout @ ${SHORT}"
    exit 1
  fi
  sleep "$WAIT"
done

RAILWAY_SHA="$(railway run -- printenv RAILWAY_GIT_COMMIT_SHA 2>/dev/null | tr -d '[:space:]' || true)"

"$ROOT/scripts/post_github_commit_status.sh" "$SHA" pending "integration harness running @ ${SHORT}" || true

set +e
"$ROOT/scripts/testing/run_railway_integration_tests.sh"
HARNESS_STATUS=$?
set -e

LOG="$(ls -t "$GATE_LOG_DIR"/run-*.log 2>/dev/null | head -1 || true)"

if (( HARNESS_STATUS == 0 )); then
  "$ROOT/scripts/post_github_commit_status.sh" "$SHA" success "integration tests passed @ ${SHORT}"
  echo "gate ok: $SHA"
  exit 0
fi

"$ROOT/scripts/post_github_commit_status.sh" "$SHA" failure "integration tests failed @ ${SHORT}"
if command -v python3 >/dev/null 2>&1; then
  python3 "$ROOT/scripts/create_integration_failure_discussion.py" \
    --sha "$SHA" \
    --railway-sha "${RAILWAY_SHA:-}" \
    --log "${LOG:-}" || true
fi
echo "gate failed: $SHA log=${LOG:-none}"
exit "$HARNESS_STATUS"
