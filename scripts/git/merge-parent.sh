#!/usr/bin/env bash
# merge-parent.sh — final land: merge ftr into dev, push dev, delete ftr branch.
# Usage: merge-parent.sh <parent-segment>
set -euo pipefail
PARENT="${1:?parent segment e.g. AST-593}"
MAIN="${ASTRAL_MAIN:-/Users/susan/chuckles/astral}"
FTR="ftr/${PARENT}"

git -C "$MAIN" fetch origin
git -C "$MAIN" checkout dev
git -C "$MAIN" merge --no-edit origin/dev
git -C "$MAIN" merge --no-edit "origin/${FTR}"
git -C "$MAIN" push origin dev
PARENT_ID="$(printf '%s' "$PARENT" | grep -oiE 'AST-[0-9]+' | head -1 || true)"
if [ -z "$PARENT_ID" ]; then
  echo "BLOCKED: parent segment must contain AST-NNN — got: $PARENT" >&2
  exit 1
fi
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
"$SCRIPT_DIR/record-landed-parent.sh" "$MAIN" "$PARENT_ID"
git -C "$MAIN" push origin --delete "${FTR}" 2>/dev/null || true

echo "RESULT: merge-parent status=ok dev=$(git -C "$MAIN" rev-parse --short HEAD) deleted=origin/${FTR}"
