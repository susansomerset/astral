#!/usr/bin/env bash
# validate-tests-branch.sh — Betty gate before push to origin/tests.
# Usage: validate-tests-branch.sh [--depth N]
set -euo pipefail

MAIN="${ASTRAL_MAIN:-/Users/susan/chuckles/astral}"
DEPTH=20
if [[ "${1:-}" == "--depth" && -n "${2:-}" ]]; then
  DEPTH="$2"
fi

git -C "$MAIN" fetch origin -q

TESTS_WT="${ASTRAL_TESTS:-$(dirname "$MAIN")/astral-tests}"
if [[ -d "$TESTS_WT/.git" ]] || [[ -f "$TESTS_WT/.git" ]]; then
  REPO="$TESTS_WT"
else
  REPO="$MAIN"
fi

TESTS_REF="refs/heads/tests"
if ! git -C "$REPO" show-ref --verify --quiet "$TESTS_REF" 2>/dev/null; then
  echo "BLOCKED: local tests branch missing in ${REPO}" >&2
  exit 1
fi

SUBJECTS=()
while IFS= read -r line; do
  SUBJECTS+=("$line")
done < <(
  git -C "$REPO" log refs/heads/tests --not origin/tests --format='%s' 2>/dev/null | head -n "$DEPTH"
)
if ((${#SUBJECTS[@]} == 0)); then
  while IFS= read -r line; do
    SUBJECTS+=("$line")
  done < <(git -C "$REPO" log origin/tests -n "$DEPTH" --format='%s')
fi

_fail() {
  echo "BLOCKED: $1" >&2
  exit 1
}

for s in "${SUBJECTS[@]}"; do
  if [[ "$s" =~ ^fix\(astral-tests\): ]]; then
    _fail "forbidden commit on tests: ${s} — never merge dev/sub/ftr into tests; use land preflight (merge-tree) locally only, do not push merge commits"
  fi
  if [[ "$s" =~ [Mm]erge\ origin/(dev|sub/|ftr/) ]]; then
    _fail "forbidden merge into tests: ${s} — tests branch is additive (test/docs commits only)"
  fi
  if [[ "$s" =~ ^Merge\ remote-tracking\ branch ]]; then
    _fail "forbidden git pull merge on tests: ${s}"
  fi
done

echo "RESULT: validate-tests-branch status=ok repo=${REPO}"
