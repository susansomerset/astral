#!/usr/bin/env bash
# Agent worktrees: sibling folders astral-ada, astral-hedy, astral-kath, astral-betty, astral-radia
# next to the main repo. Each gets its own branch (worktree/<name>) tracking origin/dev so Cursor
# sessions can run in parallel without fighting the same checkout.
#
# Betty uses astral-betty for bugfix branches like everyone else — feature branch, review, then merge
# to local dev (not direct commits on main checkout for shared bugfix work).
#
# Shared local-only files (not in git): symlink main repo's data/astral.db and .env into each
# worktree so ASTRAL_DB_DIR + dotenv match the canonical dev database unless you remove symlinks.
#
# Usage (from main repo root, once):
#   chmod +x scripts/agent-worktrees.sh && ./scripts/agent-worktrees.sh create
#   ./scripts/agent-worktrees.sh link     # re-run if you recreate data/ or .env in main
#
# Cursor: File → Open Folder → …/chuckles/astral-ada (or -hedy / -kath / -betty / -radia). Tell the agent to cwd there.
#
# Git: from a worktree, merge or rebase origin/dev often; push feature branches as usual.

set -euo pipefail
MAIN="$(cd "$(dirname "$0")/.." && pwd)"
PARENT="$(dirname "$MAIN")"

link_one() {
  local wt="$1"
  mkdir -p "$wt/data"
  if [[ -f "$MAIN/data/astral.db" ]]; then
    ln -sf "$MAIN/data/astral.db" "$wt/data/astral.db"
    echo "symlink $wt/data/astral.db -> main"
  else
    echo "warn: $MAIN/data/astral.db missing — no symlink"
  fi
  if [[ -f "$MAIN/.env" ]]; then
    ln -sf "$MAIN/.env" "$wt/.env"
    echo "symlink $wt/.env -> main"
  else
    echo "warn: $MAIN/.env missing — no symlink"
  fi
}

create_worktree() {
  local name="$1" branch="$2"
  local path="$PARENT/$name"
  if [[ -d "$path" ]]; then
    echo "skip create: $path already exists"
    return 0
  fi
  git -C "$MAIN" fetch origin
  git -C "$MAIN" worktree add "$path" -b "$branch" origin/dev
  echo "created $path on $branch (tracks origin/dev)"
}

case "${1:-}" in
  create)
    create_worktree astral-ada worktree/ada
    create_worktree astral-hedy worktree/hedy
    create_worktree astral-kath worktree/kath
    create_worktree astral-betty worktree/betty
    create_worktree astral-radia worktree/radia
    "$0" link
    git -C "$MAIN" worktree list
    ;;
  link)
    for wt in "$PARENT/astral-ada" "$PARENT/astral-hedy" "$PARENT/astral-kath" "$PARENT/astral-betty" "$PARENT/astral-radia"; do
      [[ -d "$wt" ]] || { echo "skip link: $wt not a directory"; continue; }
      link_one "$wt"
    done
    ;;
  *)
    echo "usage: $0 {create|link}" >&2
    exit 1
    ;;
esac
