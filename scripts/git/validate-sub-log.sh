#!/usr/bin/env bash
# validate-sub-log.sh — gate merge-child: canonical sub commit sequence + hygiene.
# Usage: validate-sub-log.sh <publish-ref> [child-id]
# Example: validate-sub-log.sh sub/AST-633/AST-647-list-table-layout-freeze-sticky-tooltips AST-647
set -euo pipefail

SUB_REF="${1:?sub ref e.g. sub/AST-633/AST-647-slug}"
CHILD="${2:-}"
FTR_REF="${3:-}"
MAIN="${ASTRAL_MAIN:-/Users/susan/chuckles/astral}"

if [[ -z "$CHILD" ]]; then
  CHILD="$(echo "$SUB_REF" | cut -d/ -f3 | grep -oE '^AST-[0-9]+' || true)"
fi
if [[ -z "$CHILD" ]]; then
  echo "BLOCKED: could not parse child id from ${SUB_REF}" >&2
  exit 1
fi

git -C "$MAIN" fetch origin -q

if ! git -C "$MAIN" show-ref --verify --quiet "refs/remotes/origin/${SUB_REF}"; then
  echo "BLOCKED: missing origin/${SUB_REF}" >&2
  exit 1
fi

LOG_RANGE="origin/${SUB_REF}"
if [[ -n "$FTR_REF" ]]; then
  if ! git -C "$MAIN" show-ref --verify --quiet "refs/remotes/origin/${FTR_REF}"; then
    echo "BLOCKED: missing origin/${FTR_REF} for sub-log scope" >&2
    exit 1
  fi
  LOG_RANGE="origin/${SUB_REF} --not origin/${FTR_REF}"
fi

SUBJECTS=()
while IFS= read -r line; do
  SUBJECTS+=("$line")
done < <(git -C "$MAIN" log $LOG_RANGE --format='%s')

_fail() {
  echo "BLOCKED: $1" >&2
  exit 1
}

# Duplicate Betty delivery
merge_tests=0
for s in "${SUBJECTS[@]}"; do
  if [[ "$s" =~ ^merge-tests\(${CHILD}\): ]]; then
    merge_tests=$((merge_tests + 1))
  fi
done
if (( merge_tests > 1 )); then
  _fail "duplicate merge-tests(${CHILD}) on sub — count=${merge_tests} (amend on tests, one merge-tests only)"
fi

# git pull on sub
for s in "${SUBJECTS[@]}"; do
  if [[ "$s" =~ ^Merge\ remote-tracking\ branch ]]; then
    _fail "git pull merge on sub — use: git fetch && git merge origin/ftr/<parent-segment>"
  fi
done

# Required sequence (mandatory commit types for this child)
_require() {
  local label="$1"
  local found=0
  for s in "${SUBJECTS[@]}"; do
    if [[ "$s" =~ ^${label}\(${CHILD}\): ]]; then
      found=1
      break
    fi
  done
  if (( ! found )); then
    _fail "missing ${label}(${CHILD}): on origin/${SUB_REF}"
  fi
}

_require plan
_require code
if (( merge_tests < 1 )); then
  _fail "missing merge-tests(${CHILD}): on origin/${SUB_REF}"
fi
_require test
_require docs
_require resolve

echo "RESULT: validate-sub-log status=ok child=${CHILD} ref=origin/${SUB_REF}"
