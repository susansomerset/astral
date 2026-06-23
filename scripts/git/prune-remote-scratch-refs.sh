#!/usr/bin/env bash
# prune-remote-scratch-refs.sh — delete stray origin refs (worktree/*, tmp-*).
# Usage: prune-remote-scratch-refs.sh [--dry-run]
set -euo pipefail

MAIN="${ASTRAL_MAIN:-/Users/susan/chuckles/astral}"
DRY=0
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY=1
fi

git -C "$MAIN" fetch origin -q

REFS=()
while IFS= read -r line; do
  REFS+=("$line")
done < <(
  git -C "$MAIN" ls-remote --heads origin 'worktree/*' 'tmp-*' 'tmp-fix-*' 2>/dev/null \
    | awk '{print $2}' | sed 's|refs/heads/||'
)

if ((${#REFS[@]} == 0)); then
  echo "RESULT: prune-remote-scratch-refs status=ok deleted=0"
  exit 0
fi

for ref in "${REFS[@]}"; do
  if (( DRY )); then
    echo "would delete origin/${ref}"
  else
    git -C "$MAIN" push origin --delete "$ref"
    echo "deleted origin/${ref}"
  fi
done

echo "RESULT: prune-remote-scratch-refs status=ok deleted=${#REFS[@]} dry_run=${DRY}"
