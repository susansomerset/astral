#!/usr/bin/env bash
# prune-finished-subs.sh — delete origin/sub/* when parent epic has no origin/ftr/* (finish-up backlog).
# Usage: prune-finished-subs.sh [--dry-run] [AST-NNN]
set -euo pipefail

MAIN="${ASTRAL_MAIN:-/Users/susan/chuckles/astral}"
DRY=0
PARENT_FILTER=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY=1; shift ;;
    -h|--help)
      echo "Usage: prune-finished-subs.sh [--dry-run] [AST-NNN]"
      echo "  No AST-NNN: delete sub/* for every parent with no matching origin/ftr/*"
      echo "  AST-NNN: delete sub/<parent>/* only; blocked if origin/ftr/* still exists"
      exit 0
      ;;
    AST-*|ast-*)
      PARENT_FILTER="$(printf '%s' "$1" | grep -oiE 'AST-[0-9]+' | head -1 || true)"
      if [[ -z "$PARENT_FILTER" ]]; then
        echo "BLOCKED: expected AST-NNN — got: $1" >&2
        exit 1
      fi
      shift
      ;;
    *) echo "unknown arg: $1" >&2; exit 1 ;;
  esac
done

git -C "$MAIN" fetch origin -q

parent_num_from_sub() {
  printf '%s' "$1" | grep -oiE '^sub/AST-[0-9]+' | grep -oE '[0-9]+' | head -1
}

ftr_num_from_ref() {
  printf '%s' "$1" | grep -oiE 'AST-[0-9]+' | grep -oE '[0-9]+' | head -1
}

# One line per parent ticket number that still has origin/ftr/*.
ACTIVE_FTR_NUMS="$(
  git -C "$MAIN" ls-remote origin 'refs/heads/ftr/*' 2>/dev/null \
    | awk '{print $2}' | sed 's|refs/heads/||' \
    | while IFS= read -r ftr; do
        [[ -z "$ftr" ]] && continue
        ftr_num_from_ref "$ftr"
      done | sort -u
)"

ftr_is_active() {
  local num="$1"
  [[ -z "$num" ]] && return 1
  printf '%s\n' "$ACTIVE_FTR_NUMS" | grep -qx "$num"
}

list_candidate_subs() {
  git -C "$MAIN" ls-remote origin 'refs/heads/sub/*' 2>/dev/null \
    | awk '{print $2}' | sed 's|refs/heads/||' \
    | while IFS= read -r sub; do
        [[ -z "$sub" ]] && continue
        num="$(parent_num_from_sub "$sub")"
        [[ -z "$num" ]] && continue
        if [[ -n "$PARENT_FILTER" ]]; then
          filter_num="$(printf '%s' "$PARENT_FILTER" | grep -oE '[0-9]+' | head -1)"
          [[ "$num" == "$filter_num" ]] && printf '%s\n' "$sub"
        elif ! ftr_is_active "$num"; then
          printf '%s\n' "$sub"
        fi
      done
}

if [[ -n "$PARENT_FILTER" ]]; then
  filter_num="$(printf '%s' "$PARENT_FILTER" | grep -oE '[0-9]+' | head -1)"
  if ftr_is_active "$filter_num"; then
    echo "BLOCKED: origin/ftr/* still exists for ${PARENT_FILTER} — run finish-up first" >&2
    exit 1
  fi
fi

REFS=()
while IFS= read -r sub; do
  [[ -z "$sub" ]] && continue
  REFS+=("$sub")
done < <(list_candidate_subs)

if ((${#REFS[@]} == 0)); then
  echo "RESULT: prune-finished-subs status=ok deleted=0 dry_run=${DRY}"
  exit 0
fi

DELETED=0
FAILED=0
for ref in "${REFS[@]}"; do
  if (( DRY )); then
    echo "would delete origin/${ref}"
    DELETED=$((DELETED + 1))
  elif git -C "$MAIN" push origin --delete "$ref" 2>/dev/null; then
    echo "deleted origin/${ref}"
    DELETED=$((DELETED + 1))
  else
    echo "warn: could not delete origin/${ref}" >&2
    FAILED=$((FAILED + 1))
  fi
done

echo "RESULT: prune-finished-subs status=ok deleted=${DELETED} failed=${FAILED} dry_run=${DRY}"
