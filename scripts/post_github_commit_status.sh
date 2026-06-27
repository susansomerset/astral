#!/usr/bin/env bash
# Post GitHub commit status for integration gate (AST-818). No GHA — Statuses API only.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

SHA="${1:?commit sha}"
STATE="${2:?state: pending|success|failure|error}"
DESCRIPTION="${3:-}"
CONTEXT="${ASTRAL_INTEGRATION_STATUS_CONTEXT:-integration/tests}"

if ! command -v gh >/dev/null 2>&1; then
  echo "BLOCKED: gh CLI not installed (https://cli.github.com/)" >&2
  exit 2
fi

REMOTE="$(git remote get-url origin)"
if [[ "$REMOTE" =~ github\.com[:/]([^/]+)/([^/.]+) ]]; then
  OWNER="${BASH_REMATCH[1]}"
  REPO="${BASH_REMATCH[2]%.git}"
else
  echo "BLOCKED: cannot parse owner/repo from origin: $REMOTE" >&2
  exit 2
fi

ARGS=(-f "state=$STATE" -f "context=$CONTEXT")
if [[ -n "$DESCRIPTION" ]]; then
  ARGS+=(-f "description=$DESCRIPTION")
fi

gh api "repos/${OWNER}/${REPO}/statuses/${SHA}" "${ARGS[@]}"
echo "github-status ok: $CONTEXT $STATE @ ${SHA:0:7}"
