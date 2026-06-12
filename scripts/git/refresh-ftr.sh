#!/usr/bin/env bash
# refresh-ftr.sh — merge origin/dev into origin/ftr to keep epic branch current.
# Usage: refresh-ftr.sh <parent-segment>
set -euo pipefail
PARENT="${1:?parent segment}"
MAIN="${ASTRAL_MAIN:-/Users/susan/chuckles/astral}"
FTR="ftr/${PARENT}"

git -C "$MAIN" fetch origin
WT=$(mktemp -d)
trap 'git -C "$WT" worktree remove --force "$WT" 2>/dev/null || rm -rf "$WT"' EXIT

git -C "$MAIN" worktree add "$WT" -B "tmp-refresh-${PARENT}" "origin/${FTR}"
git -C "$WT" merge --no-edit origin/dev
git -C "$WT" push origin "HEAD:${FTR}"

echo "RESULT: refresh-ftr status=ok ref=origin/${FTR}"
