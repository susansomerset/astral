#!/usr/bin/env bash
# prep-uat-land.sh — merge origin/ftr into local dev and push origin dev.
# Usage: prep-uat-land.sh <parent-segment>
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

echo "RESULT: prep-uat-land status=ok dev=$(git -C "$MAIN" rev-parse --short HEAD)"
