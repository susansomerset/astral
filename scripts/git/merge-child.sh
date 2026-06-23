#!/usr/bin/env bash
# merge-child.sh — merge origin/sub into origin/ftr for a child ticket.
# Usage: merge-child.sh <parent-segment> <publish-ref>
# Example: merge-child.sh AST-593 sub/AST-593/AST-595-some-slug
set -euo pipefail
PARENT="${1:?parent segment e.g. AST-593}"
SUB_REF="${2:?sub ref e.g. sub/AST-593/AST-595-slug}"
MAIN="${ASTRAL_MAIN:-/Users/susan/chuckles/astral}"
FTR="ftr/${PARENT}"

git -C "$MAIN" fetch origin

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHILD="$(echo "$SUB_REF" | cut -d/ -f3 | grep -oE '^AST-[0-9]+' || true)"
"${SCRIPT_DIR}/validate-sub-log.sh" "$SUB_REF" "$CHILD" "$FTR" || exit 1

# Idempotent: sub already on ftr
if git -C "$MAIN" merge-base --is-ancestor "origin/${SUB_REF}" "origin/${FTR}" 2>/dev/null; then
  echo "RESULT: merge-child status=skip reason=already-on-ftr ref=origin/${FTR}"
  exit 0
fi

# Sub must be stacked on ftr
if ! git -C "$MAIN" merge-base --is-ancestor "origin/${FTR}" "origin/${SUB_REF}" 2>/dev/null; then
  echo "BLOCKED: sub not stacked on ftr — republish from ftr first" >&2
  exit 1
fi

WT=$(mktemp -d)
TMP_BRANCH="tmp-merge-child-${PARENT}"
cleanup() {
  git -C "$MAIN" worktree remove --force "$WT" 2>/dev/null || rm -rf "$WT"
  git -C "$MAIN" branch -D "$TMP_BRANCH" 2>/dev/null || true
}
trap cleanup EXIT

git -C "$MAIN" worktree add "$WT" -B "$TMP_BRANCH" "origin/${FTR}"
git -C "$WT" merge --no-edit "origin/${SUB_REF}"
git -C "$WT" push origin "HEAD:${FTR}"

echo "RESULT: merge-child status=ok ref=origin/${FTR} sub=origin/${SUB_REF}"
