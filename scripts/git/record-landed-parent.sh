#!/usr/bin/env bash
# record-landed-parent.sh — record parent epic id on dev after prep-uat land (AST-683/693).
# Usage: record-landed-parent.sh <main-repo-path> <parent-id>
set -euo pipefail
MAIN="${1:?main repo path}"
PARENT_ID="${2:?parent id e.g. AST-675}"
REPO_ROOT="$(git -C "$MAIN" rev-parse --show-toplevel)"
APPEND="${REPO_ROOT}/scripts/append_merge_ticket_log.py"
if [ ! -f "$APPEND" ]; then
  echo "BLOCKED: append script missing at ${APPEND} — AST-681 must be on dev before record (AST-683)" >&2
  exit 1
fi
python3 "$APPEND" "$PARENT_ID"
git -C "$MAIN" add data/merge_ticket_log.json
if git -C "$MAIN" diff --cached --quiet; then
  echo "BLOCKED: merge ticket log unchanged after append for ${PARENT_ID}" >&2
  exit 1
fi
git -C "$MAIN" commit -m "prep-uat(${PARENT_ID}): record parent in merge ticket log"
git -C "$MAIN" push origin dev
echo "RESULT: record-landed-parent status=ok parent=${PARENT_ID}"
