#!/usr/bin/env bash
# finish-up-land.sh — PR (ftr → dev), land, delete origin/local ftr + sub/* for parent.
# Usage: finish-up-land.sh <parent-segment>
set -euo pipefail
PARENT="${1:?parent segment e.g. ast-539-slug}"
MAIN="${ASTRAL_MAIN:-/Users/susan/chuckles/astral}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PARENT_ID="$(printf '%s' "$PARENT" | grep -oiE 'AST-[0-9]+' | head -1 || true)"
if [ -z "$PARENT_ID" ]; then
  echo "BLOCKED: parent segment must contain AST-NNN — got: $PARENT" >&2
  exit 1
fi
PARENT_NUM="$(printf '%s' "$PARENT_ID" | grep -oE '[0-9]+' | head -1)"

branch_belongs_to_parent() {
  local ref="$1" num="$2"
  case "$ref" in dev|main|tests) return 1 ;; esac
  printf '%s' "$ref" | grep -qiE "^sub/AST-${num}/" && return 0
  printf '%s' "$ref" | grep -qiE "^worktree/AST-${num}$" && return 0
  printf '%s' "$ref" | grep -qiE "^ftr/.*AST-${num}([^0-9]|$)" && return 0
  printf '%s' "$ref" | grep -qiE "^tmp-(refresh|merge-child|fix).*-AST-${num}(-|$)" && return 0
  printf '%s' "$ref" | grep -qiE "^review-ast-${num}(-|$)" && return 0
  return 1
}

worktree_path_for_parent() {
  local path="$1" id="$2" num="$3"
  [[ "$path" == *"-${id}" ]] && return 0
  [[ "$path" == *"-ast-${num}" ]] && return 0
  [[ "$path" == *"-AST-${num}" ]] && return 0
  return 1
}

remove_epic_worktrees() {
  local id="$1" num="$2"
  local removed=0 main_top wt_path branch line should_remove

  "$SCRIPT_DIR/../agent-worktrees.sh" epic-remove "$(basename "$MAIN")" "$id" 2>/dev/null && removed=$((removed + 1)) || true

  main_top="$(git -C "$MAIN" rev-parse --show-toplevel)"
  while IFS= read -r line; do
    wt_path="${line%% *}"
    [[ "$wt_path" == "$main_top" ]] && continue
    branch=""
    if [[ "$line" == *"["*"]"* ]]; then
      branch="${line##*[}"
      branch="${branch%]*}"
    fi
    should_remove=0
    if [[ -n "$branch" ]] && branch_belongs_to_parent "$branch" "$num"; then
      should_remove=1
    elif worktree_path_for_parent "$wt_path" "$id" "$num"; then
      should_remove=1
    fi
    if (( should_remove )); then
      if git -C "$MAIN" worktree remove --force "$wt_path" 2>/dev/null; then
        echo "removed worktree ${wt_path}"
        removed=$((removed + 1))
      else
        echo "warn: could not remove worktree ${wt_path}" >&2
      fi
    fi
  done < <(git -C "$MAIN" worktree list)

  printf '%s' "$removed"
}

delete_local_branches_for_parent() {
  local num="$1"
  local deleted=0 current ref

  current="$(git -C "$MAIN" symbolic-ref --short HEAD 2>/dev/null || echo dev)"
  while IFS= read -r ref; do
    [[ -z "$ref" ]] && continue
    [[ "$ref" == "$current" ]] && continue
    branch_belongs_to_parent "$ref" "$num" || continue
    if git -C "$MAIN" branch -D "$ref" 2>/dev/null; then
      echo "deleted local ${ref}"
      deleted=$((deleted + 1))
    else
      echo "warn: could not delete local ${ref}" >&2
    fi
  done < <(git -C "$MAIN" for-each-ref --format='%(refname:short)' refs/heads/)

  printf '%s' "$deleted"
}

FTR="$(git -C "$MAIN" ls-remote --heads origin "refs/heads/ftr/${PARENT}*" "refs/heads/ftr/*${PARENT_ID}*" 2>/dev/null \
  | awk '{print $2}' | sed 's|refs/heads/||' | head -1)"
if [ -z "$FTR" ]; then
  echo "BLOCKED: no origin ftr branch for ${PARENT_ID} (segment ${PARENT})" >&2
  exit 1
fi

python3 "$SCRIPT_DIR/create-dev-pr.py" --repo "$MAIN" --parent-id "$PARENT_ID" --ftr "$FTR" --create
"$SCRIPT_DIR/merge-parent.sh" "$PARENT"

# Child publish refs are merged into ftr before land; delete origin/sub/<parent>/* with ftr.
DELETED_SUBS=0
while IFS= read -r sub; do
  [[ -z "$sub" ]] && continue
  if git -C "$MAIN" push origin --delete "$sub" 2>/dev/null; then
    echo "deleted origin/${sub}"
    DELETED_SUBS=$((DELETED_SUBS + 1))
  else
    echo "warn: could not delete origin/${sub}" >&2
  fi
done < <(
  git -C "$MAIN" ls-remote origin 'refs/heads/sub/*' 2>/dev/null \
    | awk '{print $2}' | sed 's|refs/heads/||' \
    | grep -iE "^sub/AST-${PARENT_NUM}/" || true
)

REMOVED_WORKTREES="$(remove_epic_worktrees "$PARENT_ID" "$PARENT_NUM")"
DELETED_LOCAL="$(delete_local_branches_for_parent "$PARENT_NUM")"

python3 "$SCRIPT_DIR/create-dev-pr.py" --repo "$MAIN" --parent-id "$PARENT_ID" --ftr "$FTR" --merge

echo "RESULT: finish-up-land status=ok parent=${PARENT_ID} ftr=${FTR} deleted_subs=${DELETED_SUBS} deleted_local=${DELETED_LOCAL} removed_worktrees=${REMOVED_WORKTREES} dev=$(git -C "$MAIN" rev-parse --short HEAD)"
