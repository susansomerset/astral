#!/usr/bin/env bash
# validate-tests-branch.sh — Betty gate before push to origin/tests.
# Scans the full additive range (tip --not tests-clean-base), not just the
# last N unpushed commits — so a forbidden merge already on origin/tests
# still fails on every subsequent run.
# Usage: validate-tests-branch.sh [--depth N]
set -euo pipefail

MAIN="${ASTRAL_MAIN:-/Users/susan/chuckles/astral}"
DEPTH=""
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

# Durable grandfather marker (AST-1574 option A). History under this tip is
# not re-litigated; everything after it must stay additive.
BASE_REF=""
for cand in refs/remotes/origin/tests-clean-base refs/heads/tests-clean-base; do
  if git -C "$REPO" show-ref --verify --quiet "$cand" 2>/dev/null; then
    BASE_REF="$cand"
    break
  fi
done
if [[ -z "$BASE_REF" ]]; then
  echo "BLOCKED: tests-clean-base ref missing — push origin/tests-clean-base (AST-1574 marker)" >&2
  exit 1
fi

_fail() {
  echo "BLOCKED: $1" >&2
  exit 1
}

# One line per commit: <sha> <parent-count> <subject>
LOG_ARGS=(log "$TESTS_REF" --not "$BASE_REF" --format='%H %P %s')
if [[ -n "$DEPTH" ]]; then
  LOG_ARGS+=(-n "$DEPTH")
fi

while IFS= read -r line; do
  [[ -z "$line" ]] && continue
  sha="${line%% *}"
  rest="${line#* }"
  # parents are hex tokens before the subject; subject may contain spaces
  parents=()
  subject=""
  while [[ -n "$rest" ]]; do
    tok="${rest%% *}"
    if [[ "$tok" =~ ^[0-9a-f]{40}$ ]]; then
      parents+=("$tok")
      rest="${rest#"$tok"}"
      rest="${rest## }"
    else
      subject="$rest"
      break
    fi
  done
  pc="${#parents[@]}"

  if [[ "$subject" =~ ^fix\(astral-tests\): ]]; then
    _fail "forbidden commit on tests: ${subject} — never merge dev/sub/ftr into tests; use land preflight (merge-tree) locally only, do not push merge commits"
  fi
  if [[ "$subject" =~ ^Merge\ remote-tracking\ branch ]]; then
    _fail "forbidden git pull merge on tests: ${subject}"
  fi
  if [[ "$subject" =~ [Mm]erge\ origin/(dev|sub/|ftr/) ]]; then
    _fail "forbidden merge into tests: ${subject} — tests branch is additive (test/docs commits only)"
  fi
  if [[ "$subject" =~ ^Merge\  ]]; then
    _fail "forbidden merge commit on tests: ${subject}"
  fi
  if ((pc > 1)) && ! [[ "$subject" =~ ^merge-tests\(AST-[0-9]+\): ]]; then
    _fail "forbidden multi-parent commit on tests (${sha:0:9}, ${pc} parents): ${subject} — only merge-tests(AST-NNN): merges are allowed"
  fi
done < <(git -C "$REPO" "${LOG_ARGS[@]}")

echo "RESULT: validate-tests-branch status=ok repo=${REPO} base=${BASE_REF}"
