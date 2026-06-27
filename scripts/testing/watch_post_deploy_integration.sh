#!/usr/bin/env bash
# Poll origin/dev + Railway deploy; run post_deploy_integration_gate once per SHA (AST-818).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
STATE_FILE="$ROOT/debug/integration-operator/last_gate_sha"
git fetch origin
SHA="$(git rev-parse origin/dev)"
if [[ -f "$STATE_FILE" ]] && [[ "$(cat "$STATE_FILE")" == "$SHA" ]]; then
  echo "skip: already gated $SHA"
  exit 0
fi
"$ROOT/scripts/testing/post_deploy_integration_gate.sh"
echo "$SHA" > "$STATE_FILE"
