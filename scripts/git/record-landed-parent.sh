#!/usr/bin/env bash
# record-landed-parent.sh — record parent epic id on dev after prep-uat land (AST-683/693).
# Usage: record-landed-parent.sh <main-repo-path> <parent-id>
set -euo pipefail
MAIN="${1:?main repo path}"
PARENT_ID="${2:?parent id e.g. AST-675}"
REPO_ROOT="$(git -C "$MAIN" rev-parse --show-toplevel)"
REBUILD="${REPO_ROOT}/scripts/rebuild_merge_ticket_log.py"
if [[ -n "${ASTRAL_PYTHON:-}" ]]; then
  PYTHON="$ASTRAL_PYTHON"
else
  PYTHON="${REPO_ROOT}/.venv/bin/python"
fi
if [ ! -x "$PYTHON" ]; then
  echo "BLOCKED: repo venv python missing at ${PYTHON} — run setup_dev.sh or set ASTRAL_PYTHON (AST-806)" >&2
  exit 1
fi
if [ ! -f "$REBUILD" ]; then
  echo "BLOCKED: rebuild script missing at ${REBUILD} — AST-800 must be on dev before record (AST-683)" >&2
  exit 1
fi
"$PYTHON" "$REBUILD" --landing-parent "$PARENT_ID"
git -C "$MAIN" add data/merge_ticket_log.json
if git -C "$MAIN" diff --cached --quiet; then
  echo "BLOCKED: merge ticket log unchanged after rebuild for ${PARENT_ID}" >&2
  exit 1
fi
git -C "$MAIN" commit -m "prep-uat(${PARENT_ID}): rebuild merge ticket log"
git -C "$MAIN" push origin dev
echo "RESULT: record-landed-parent status=ok parent=${PARENT_ID}"
