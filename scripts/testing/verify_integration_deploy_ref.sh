#!/usr/bin/env bash
# Pin integration operator run to origin/dev SHA vs Railway deploy (AST-712).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
git fetch origin
EXPECTED="${1:-$(git rev-parse origin/dev)}"
if ! command -v railway >/dev/null 2>&1; then
  echo "BLOCKED: railway CLI not installed (https://docs.railway.com/guides/cli)" >&2
  exit 2
fi
ACTUAL="$(railway run -- printenv RAILWAY_GIT_COMMIT_SHA | tr -d '[:space:]')"
if [[ -z "$ACTUAL" ]]; then
  echo "BLOCKED: RAILWAY_GIT_COMMIT_SHA empty — link test project (railway link) and ensure deploy finished" >&2
  exit 2
fi
if [[ "$ACTUAL" != "$EXPECTED" ]]; then
  echo "DEPLOY MISMATCH: origin/dev=$EXPECTED railway=$ACTUAL" >&2
  echo "Wait for test service deploy or re-run after push-dev." >&2
  exit 1
fi
echo "deploy-ref ok: $ACTUAL"
