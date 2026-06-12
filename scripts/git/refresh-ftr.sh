#!/usr/bin/env bash
# refresh-ftr.sh — merge origin/dev into origin/ftr to keep epic branch current.
# Usage: refresh-ftr.sh <parent-segment>
set -euo pipefail
PARENT="${1:?parent segment}"
MAIN="${ASTRAL_MAIN:-/Users/susan/chuckles/astral}"
FTR="ftr/${PARENT}"

git -C "$MAIN" fetch origin
WT=$(mktemp -d)
TMP_BRANCH="tmp-refresh-${PARENT}"
cleanup() {
  git -C "$MAIN" worktree remove --force "$WT" 2>/dev/null || rm -rf "$WT"
  git -C "$MAIN" branch -D "$TMP_BRANCH" 2>/dev/null || true
}
trap cleanup EXIT

git -C "$MAIN" worktree add "$WT" -B "$TMP_BRANCH" "origin/${FTR}"
git -C "$WT" merge --no-edit origin/dev
git -C "$WT" push origin "HEAD:${FTR}"

echo "RESULT: refresh-ftr status=ok ref=origin/${FTR}"
