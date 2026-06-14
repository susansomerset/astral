#!/usr/bin/env bash
# Worktree helpers for Astral v3 git workflow.
# Sibling folders: astral (dev), astral-tests (tests), astral-<IssueID> (epic).
set -euo pipefail
MAIN="$(cd "$(dirname "$0")/.." && pwd)"
PARENT="$(dirname "$MAIN")"
REPO_NAME="$(basename "$MAIN")"

link_one() {
  local wt="$1"
  mkdir -p "$wt/data"
  if [[ -f "$MAIN/data/astral.db" ]]; then
    ln -sf "$MAIN/data/astral.db" "$wt/data/astral.db"
  fi
  if [[ -f "$MAIN/.env" ]]; then
    ln -sf "$MAIN/.env" "$wt/.env"
  fi
}

epic_create() {
  local repo="${1:?reponame e.g. astral}"
  local issue="${2:?parent issue id e.g. AST-593}"
  local path="$PARENT/${repo}-${issue}"
  if [[ -d "$path" ]]; then
    echo "skip: $path exists"
    return 0
  fi
  git -C "$MAIN" fetch origin
  git -C "$MAIN" worktree add "$path" -b "worktree/${issue}" origin/dev
  link_one "$path"
  echo "created epic worktree $path"
}

tests_create() {
  local repo="${1:-$REPO_NAME}"
  local path="$PARENT/${repo}-tests"
  if [[ -d "$path" ]]; then
    echo "skip: $path exists"
    return 0
  fi
  git -C "$MAIN" fetch origin
  if git -C "$MAIN" show-ref --verify --quiet refs/remotes/origin/tests; then
    git -C "$MAIN" worktree add "$path" -b tests origin/tests
  else
    git -C "$MAIN" worktree add "$path" -b tests origin/dev
    git -C "$path" push -u origin tests
  fi
  link_one "$path"
  echo "created tests worktree $path"
}

epic_remove() {
  local repo="${1:?reponame}"
  local issue="${2:?issue id}"
  local path="$PARENT/${repo}-${issue}"
  if [[ ! -d "$path" ]]; then
    echo "skip: no $path"
    return 0
  fi
  git -C "$MAIN" worktree remove --force "$path"
  git -C "$MAIN" branch -D "worktree/${issue}" 2>/dev/null || true
  echo "removed $path"
}

case "${1:-}" in
  epic-create) epic_create "${2:-}" "${3:-}" ;;
  epic-remove) epic_remove "${2:-}" "${3:-}" ;;
  tests-create) tests_create "${2:-}" ;;
  link)
    for wt in "$PARENT/${REPO_NAME}-tests" "$PARENT/${REPO_NAME}-"*; do
      [[ -d "$wt" ]] || continue
      link_one "$wt"
    done
    ;;
  *)
    echo "usage: $0 {epic-create|epic-remove|tests-create|link} [args]" >&2
    echo "  epic-create <reponame> <parent-id>" >&2
    echo "  epic-remove <reponame> <parent-id>" >&2
    echo "  tests-create [reponame]" >&2
    exit 1
    ;;
esac
