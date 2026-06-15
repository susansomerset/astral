# finish-up auto-record landed parent

**Linear:** [AST-683 — finish-up auto-record landed parent](https://linear.app/astralcareermatch/issue/AST-683/finish-up-auto-record-landed-parent-create-a-ticket-log-in-utils)

**Parent:** [AST-675 — Create a ticket log in utils](https://linear.app/astralcareermatch/issue/AST-675/create-a-ticket-log-in-utils) (definition reference only)

**Publish ref:** `origin/sub/AST-675/ast-683-finish-up-auto-record-landed-parent` (origin only)

## Summary

When Chuckles runs finish-up and lands a parent epic on `origin/dev`, the merge ticket log must gain one append-only entry for that parent’s Linear id (not child ids). Sibling AST-681 shipped `scripts/append_merge_ticket_log.py` and `src/utils/merge_ticket_log.py`; this ticket wires the finish-up land path to invoke that CLI after a successful `dev` push, commit `data/merge_ticket_log.json`, and push `dev` again. No log format, deploy-status, or UI changes.

⚠️ **Decision:** Wire via **`scripts/git/merge-parent.sh`** (delegated helper), not `prep-uat-land.sh`. `finish-up-land.sh` (Chuckles skill) calls `merge-parent.sh` after PR create; `prep-uat-land.sh` lands `ftr` for UAT without finish-up semantics and must not append. `finish-up-land.sh` is not yet on `origin/dev`; landing behavior lives in `merge-parent.sh`, which is shipped in-repo.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `scripts/git/record-landed-parent.sh` | New helper: append log entry + commit + push on `dev` | scripts |
| `scripts/git/merge-parent.sh` | After successful land push, extract parent id and call helper | scripts |
| `tests/component/scripts/test_record_landed_parent.py` | Subprocess integration: append + commit in temp repo (Betty manifest — engineer runs in test-child) | test |

**Verify only (no change expected):**

| File | Role |
|------|------|
| `scripts/append_merge_ticket_log.py` | CLI from AST-681 — sole append API |
| `src/utils/merge_ticket_log.py` | Utils writer from AST-681 |
| `data/merge_ticket_log.json` | Shipped seed from AST-681 — updated by record helper |
| `scripts/git/prep-uat-land.sh` | Must **not** gain append wiring |
| `scripts/git/finish-up-land.sh` | Out of repo today; inherits behavior when it calls `merge-parent.sh` |

**Out of scope:** log module/API (AST-681), admin tooltip (AST-682), backfill, SHA in entries, child ticket ids, shipping `finish-up-land.sh` to the repo, changes to PR create/merge or sub/worktree cleanup steps.

---

## Stage 1: record-landed-parent helper script

**Done when:** `scripts/git/record-landed-parent.sh` exists, is executable, accepts `MAIN` repo path and `AST-NNN` parent id, appends one log entry via the AST-681 CLI, commits only `data/merge_ticket_log.json`, pushes `origin dev`, prints `RESULT: record-landed-parent status=ok`; exits non-zero with `BLOCKED:` stderr on failure; `bash -n scripts/git/record-landed-parent.sh` passes.

1. Create `scripts/git/record-landed-parent.sh`:

   ```bash
   #!/usr/bin/env bash
   # record-landed-parent.sh — append parent epic id to merge ticket log on dev after land (AST-683).
   # Usage: record-landed-parent.sh <main-repo-path> <parent-id>
   set -euo pipefail
   MAIN="${1:?main repo path}"
   PARENT_ID="${2:?parent id e.g. AST-675}"
   REPO_ROOT="$(git -C "$MAIN" rev-parse --show-toplevel)"
   APPEND="${REPO_ROOT}/scripts/append_merge_ticket_log.py"
   if [ ! -f "$APPEND" ]; then
     echo "BLOCKED: append script missing at ${APPEND} — AST-681 must be on dev before record (AST-683)" >&2
     exit 1
   fi
   python3 "$APPEND" "$PARENT_ID"
   git -C "$MAIN" add data/merge_ticket_log.json
   if git -C "$MAIN" diff --cached --quiet; then
     echo "BLOCKED: merge ticket log unchanged after append for ${PARENT_ID}" >&2
     exit 1
   fi
   git -C "$MAIN" commit -m "finish-up(${PARENT_ID}): record landed parent in merge ticket log"
   git -C "$MAIN" push origin dev
   echo "RESULT: record-landed-parent status=ok parent=${PARENT_ID}"
   ```

2. `chmod +x scripts/git/record-landed-parent.sh`

3. `bash -n scripts/git/record-landed-parent.sh`

   ⚠️ **Decision:** Second commit on `dev` (after ftr land push) matches parent note that SHA is unknown before the log file commit; the log entry timestamp reflects tool-run time at append, not the land merge commit.

   ⚠️ **Decision:** If append or the follow-up push fails after the ftr land push succeeded, the script exits non-zero (`BLOCKED:`). Chuckles finish-up reports blocked; land is already on `dev` — manual append or re-run is acceptable escalation, not silent skip.

**Ritual:** `code(AST-683): record-landed-parent helper for merge ticket log`

---

## Stage 2: Wire merge-parent.sh after successful land

**Done when:** `merge-parent.sh` invokes `record-landed-parent.sh` only after `git push origin dev` from the ftr merge succeeds; parent id is parsed from the `<parent-segment>` argument (same `AST-[0-9]+` extraction as `finish-up-land.sh`); missing parent id exits `BLOCKED`; `prep-uat-land.sh` is unchanged; `bash -n scripts/git/merge-parent.sh` passes.

1. In `scripts/git/merge-parent.sh`, after the existing `git -C "$MAIN" push origin dev` line (ftr land) and **before** `git push origin --delete "${FTR}"`, add:

   ```bash
   PARENT_ID="$(printf '%s' "$PARENT" | grep -oiE 'AST-[0-9]+' | head -1 || true)"
   if [ -z "$PARENT_ID" ]; then
     echo "BLOCKED: parent segment must contain AST-NNN — got: $PARENT" >&2
     exit 1
   fi
   SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
   "$SCRIPT_DIR/record-landed-parent.sh" "$MAIN" "$PARENT_ID"
   ```

2. Do **not** edit `scripts/git/prep-uat-land.sh`.

3. Do **not** add append logic to any other script in this ticket.

4. `bash -n scripts/git/merge-parent.sh`

**Ritual:** `code(AST-683): wire merge-parent to record landed parent in ticket log`

---

## Stage 3: Component test (Betty manifest — engineer runs in test-child)

**Done when:** `tests/component/scripts/test_record_landed_parent.py` passes; test uses a temporary git repo (not the real `data/merge_ticket_log.json`); documents that full finish-up bash flow is verified manually by Chuckles on next parent land.

1. Create `tests/component/scripts/test_record_landed_parent.py`:

   - **`test_record_landed_parent_appends_and_commits`:** In `tmp_path`, init a git repo with `user.email` / `user.name` configured; copy or symlink-minimal tree: `scripts/append_merge_ticket_log.py`, `src/utils/merge_ticket_log.py`, `src/utils/config.py` dependencies needed for import (follow import chain only — do not copy all of `config.py` if monkeypatching `MERGE_TICKET_LOG_CONFIG["log_path"]` to `tmp_path / "merge_ticket_log.json"` is sufficient); seed `[]` at that path; run `record-landed-parent.sh` via `subprocess.run` with `cwd` = repo root, args `[script_path, str(repo_root), "AST-999"]`, env includes unbuffered python; assert exit code 0; assert log file has one entry with `ticket_id == "AST-999"` and parseable `recorded_at`; assert `git log -1 --oneline` contains `finish-up(AST-999)`.

   - **`test_record_landed_parent_missing_append_script_blocks`:** Temp repo without `scripts/append_merge_ticket_log.py`; run helper; assert exit code ≠ 0 and stderr contains `BLOCKED`.

   - Use **`monkeypatch.setitem(MERGE_TICKET_LOG_CONFIG, "log_path", ...)`** only if the subprocess inherits the test process env — otherwise set log path via a minimal `config` stub or patch before subprocess by writing a tiny wrapper. Prefer monkeypatch on `MERGE_TICKET_LOG_CONFIG` in-process test of `append_merge_ticket_log` for the append half (already covered in AST-681) plus a **`test_merge_parent_shell_references_record_helper`** that reads `merge-parent.sh` text and asserts it contains `record-landed-parent.sh` (static guard).

2. Run: `.venv/bin/python -m pytest tests/component/scripts/test_record_landed_parent.py -q`

3. **Manual verify (Linear comment in test-child, not automated):** Document for Chuckles: after epic ships, next `finish-up AST-675` should leave `data/merge_ticket_log.json` on `origin/dev` with an `AST-675` entry.

**Ritual:** `test(AST-683): record-landed-parent wiring coverage`

---

## Execution contract (for the developer agent)

The plan is binding. Execute stages in order. Do not modify log format, deploy-status payload, UI, or `prep-uat-land.sh`. When `append_merge_ticket_log.py` is missing on `dev` after ftr merge (should not happen once AST-681 is on ftr), stop and escalate — do not stub a fallback writer.

Blocking questions use parent **AST-675** with:

```
🛑 Stage N blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

---

## Self-Assessment

**Scope:** `scope-minor` — Two bash scripts under `scripts/git/` plus one component test file; no Python product modules, UI, or config changes beyond invoking existing AST-681 CLI.

**Conf:** `conf-high` — AST-681 defines the append CLI and entry shape; `merge-parent.sh` already performs the land push; this ticket adds one helper call and a follow-up commit pattern documented in the parent epic.

**Risk:** `risk-Medium` — `merge-parent.sh` is on the finish-up critical path; a bad wire could block lands or double-push; mitigated by narrow helper, `set -euo pipefail`, and explicit `BLOCKED:` exits without altering pre-land steps.

---

## ASTRAL_CODE_RULES self-review

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Append logic stays in `merge_ticket_log.py` / CLI; bash only orchestrates git + subprocess |
| §2.1 config | Log path remains `MERGE_TICKET_LOG_CONFIG`; no new config keys |
| §3.3 imports | No new Python modules; bash invokes existing script |
| §3.5 naming | `record-landed-parent.sh`, `finish-up(${PARENT_ID})` commit message match domain |

No conflicts requiring `conf-!!-NONE`.

---

## Execution contract reminder

- Stages run in order; one commit ritual per stage on epic worktree; publish each to **`origin/sub/AST-675/ast-683-finish-up-auto-record-landed-parent`** via build-child / Joan.
- Do not implement AST-681 log storage, AST-682 tooltip, or backfill.

---

## Review stub (Hedy / build)

**Publish ref:** `origin/sub/AST-675/ast-683-finish-up-auto-record-landed-parent`  
**Product commits:** `f2742e3a` (`scripts/git/record-landed-parent.sh`), `efd736f1` (wire `merge-parent.sh` after ftr land push)

**Note for Betty (Stage 3):** Component test `tests/component/scripts/test_record_landed_parent.py` per plan — manifest at Code Complete.

---

## Radia review (AST-683)

**Ref:** `origin/dev...origin/sub/AST-675/ast-683-finish-up-auto-record-landed-parent`  
**Product commits reviewed:** `f2742e3a`, `efd736f1`, `de1a4dea` (test)

### What's solid

- **Plan fidelity:** `record-landed-parent.sh` matches Stage 1 verbatim; `merge-parent.sh` wires after ftr land push and before ftr delete per Stage 2; `prep-uat-land.sh` untouched.
- **Boundaries:** No log format, deploy-status, or UI changes in AST-683 commits; append stays on AST-681 CLI/utils; parent id only via `grep -oiE 'AST-[0-9]+'`.
- **Failure contract:** `set -euo pipefail`, `BLOCKED:` stderr on missing append script or unchanged log after append; land already on `dev` before record — matches plan escalation note.
- **Tests:** Manifest `test_record_landed_parent.py` — 3/3 pass (temp repo append+commit, missing CLI block, static `merge-parent.sh` guard); fake `git push` avoids network.
- **ASTRAL_CODE_RULES:** §1.3 DRY (bash orchestrates only); §2.1 config path via existing `MERGE_TICKET_LOG_CONFIG`; no new Python modules or layer violations in this ticket’s diff.

### Issues

None (fix-now).

### Recommended actions

- **Advisory:** On next real `finish-up` for AST-675, confirm `data/merge_ticket_log.json` on `origin/dev` gains one `AST-675` entry (plan Stage 3 manual verify — not automated).
- **Advisory:** Re-running `merge-parent.sh` after a successful record will append a duplicate parent id (append-only log by design); acceptable per parent epic unless dedup is added later.

---

## Resolution (2026-06-15)

**Publish ref:** `origin/sub/AST-675/ast-683-finish-up-auto-record-landed-parent` @ `b79c15a2` (Radia `docs(AST-683): Radia review — clean`)

Radia review clean — no fix-now, discuss, or product changes. Merged `origin/dev`, `origin/ftr/ast-675-create-a-ticket-log-in-utils`, and publish ref on epic worktree `work683`; §9a dry-run clean against `origin/dev` and `origin/ftr/ast-675-create-a-ticket-log-in-utils`.

**Outcome:** `merge-parent.sh` invokes `record-landed-parent.sh` after successful ftr land push; append-only merge ticket log entry + follow-up `dev` commit wired for finish-up.
