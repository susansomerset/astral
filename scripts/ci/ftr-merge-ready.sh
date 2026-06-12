#!/usr/bin/env bash
# Verify every origin/ftr/* branch can absorb origin/dev cleanly (merge-tree).
# CI: --check only (no writes). Local Joan: git.sh refresh-ftr merges + pushes.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
MODE="check"
PARENT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --check) MODE="check"; shift ;;
    --apply) MODE="apply"; shift ;;
    -h|--help)
      echo "Usage: ftr-merge-ready.sh [--check|--apply] [AST-parent-id]"
      exit 0
      ;;
    AST-*|ast-*)
      PARENT="$1"
      shift
      ;;
    *) echo "unknown arg: $1" >&2; exit 1 ;;
  esac
done

cd "$REPO_ROOT"
git fetch origin

list_ftrs() {
  if [[ -n "$PARENT" ]]; then
    local num="${PARENT#AST-}" manifest="$REPO_ROOT/debug/epic-sessions/${PARENT}/manifest.json" ftr=""
    if [[ -f "$manifest" ]]; then
      ftr=$(python3 -c "import json; print(json.load(open('$manifest')).get('ftr',''))" 2>/dev/null || true)
      if [[ -n "$ftr" ]] && git ls-remote --exit-code origin "refs/heads/$ftr" >/dev/null 2>&1; then
        echo "$ftr"
        return
      fi
    fi
    git ls-remote origin 'refs/heads/ftr/*' | awk '{print $2}' | sed 's|refs/heads/||' | grep -i "ast-${num}" | head -1
    return
  fi
  git ls-remote origin 'refs/heads/ftr/*' | awk '{print $2}' | sed 's|refs/heads/||' | sort
}

conflict_files_for_ftr() {
  local ftr="$1" base out
  base=$(git merge-base origin/dev "origin/$ftr")
  out=$(git merge-tree "$base" "origin/$ftr" origin/dev 2>&1) || true
  if echo "$out" | grep -qE 'changed in both|<<<<<<<'; then
    echo "$out" | awk '/^changed in both/{getline; if ($NF ~ /\//) print $NF}'
    return 1
  fi
  return 0
}

apply_refresh_ftr() {
  local ftr="$1" wt
  if git merge-base --is-ancestor origin/dev "origin/$ftr" 2>/dev/null; then
    echo "refresh-ftr: $ftr OK (already contains origin/dev)"
    return 0
  fi
  wt="$(mktemp -d)"
  trap 'git worktree remove "$wt" --force 2>/dev/null || rm -rf "$wt"' RETURN
  git worktree add -d "$wt" "origin/$ftr"
  if git -C "$wt" merge origin/dev --no-edit \
    -m "merge: refresh-ftr — integrate origin/dev into $ftr"; then
    git -C "$wt" push origin "HEAD:refs/heads/$ftr"
    echo "refresh-ftr: $ftr OK @ $(git rev-parse --short "origin/$ftr") (merged origin/dev)"
    git worktree remove "$wt" --force
    trap - RETURN
    return 0
  fi
  echo "refresh-ftr: $ftr CONFLICT files:" >&2
  git -C "$wt" diff --name-only --diff-filter=U >&2 || true
  git -C "$wt" merge --abort 2>/dev/null || true
  return 1
}

failed=0
total=0
while IFS= read -r ftr; do
  [[ -z "$ftr" ]] && continue
  total=$((total + 1))
  if [[ "$MODE" == "apply" ]]; then
    apply_refresh_ftr "$ftr" || failed=$((failed + 1))
  else
    if git merge-base --is-ancestor origin/dev "origin/$ftr" 2>/dev/null; then
      echo "ftr-merge-ready: $ftr OK (already contains origin/dev)"
    elif conflict_files_for_ftr "$ftr"; then
      echo "ftr-merge-ready: $ftr OK"
    else
      echo "ftr-merge-ready: $ftr CONFLICT" >&2
      failed=$((failed + 1))
    fi
  fi
done < <(list_ftrs)

if [[ "$total" -eq 0 ]]; then
  echo "ftr-merge-ready: no ftr/* refs on origin"
  exit 0
fi

if [[ "$failed" -gt 0 ]]; then
  echo "ftr-merge-ready: BLOCKED $failed/$total ftr branch(es) conflict with origin/dev" >&2
  exit 1
fi

echo "ftr-merge-ready: all $total ftr branch(es) merge-ready with origin/dev"
exit 0
