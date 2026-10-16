# AST-1617 — check_inbox total_errors without ERROR/WARNING logs

<!-- linear-archive: AST-1617 archived 2026-10-02 -->

## Linear archive (AST-1617)

**Archived:** 2026-10-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1617/check-inbox-total-errors-without-errorwarning-logs  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1555 — Meteorite ingress: staging table + inbox/meteorite consolidation  
**Blocked by / blocks / related:** parent: AST-1555

### Description

## What failed

`check_inbox` / `ingest_candidate_email_message` can return `counter=error` (and bump batch `total_errors`) without emitting ERROR/WARNING. Exception and classify-fail detail only goes through Style D (`_check_inbox_dbg` / `_check_inbox_detail`) when `debug=True`. Always-on monitoring covers post-classify info lines, not exception stacks.

## Expected

On every mid that ends `counter=error`, always-on log (prefer `logger.exception` / `logger.error` with mid + exception) so a Railway/admin paste shows why without requiring Style D reconstruction.

## Repro

1. Run candidate-bound `meteorite_email` / `check_inbox` with failures (classify/map/archive/exception).
2. Observe summary `total_errors > 0`.
3. Observe log has no ERROR/WARNING for those mids (DEBUG-only when debug=True).

## Parent AC (context)

[AST-1555](https://linear.app/astralcareermatch/issue/AST-1555/meteorite-ingress-staging-table-inboxmeteorite-consolidation) monitoring contract: always-on info for classify outcomes; this bug is the missing always-on path for error counters.

## Boundaries

* Does not change classify/land semantics or Style D contract when debug=True.
* Does not invent SKIPPED rows.

## Suggested engineer

Katherine Johnson (AST-1559 check_inbox + monitoring owner on parent Team)

## Remaining gap (confirmed 2026-09-24 on origin/dev)

Most `counter=error` exits in `ingest_candidate_email_message` (`src/core/meteorite.py`) already hit `_warn_item` / `logger.exception`. Two paths still don't:

* `ingest_candidate_email_message`: when `stage_meteorite` returns `stage["error"]`, ingest returns `_row(err_key, counter="error", ...)` with no always-on WARNING/ERROR for that mid.
* `stage_meteorite`: the classify-fail fallthrough (`err = classify.get("error") or "stage failed"` → `_save_error(...)`) returns `error` without a warning, even when the ERROR-row insert succeeds.

Fix target: one always-on warn (mid + error) on each of those paths. No change to classify/land semantics or Style D.

## QA test manifest

**Publish:** `origin/sub/AST-1555/AST-1617-check-inbox-total-errors-without-errorwarning-logs` @ `9ea87f04` (`merge-tests(AST-1617): origin/tests 948ebc3a`)

**Bible shasum:** `docs/test-bible/core/meteorite.md` — `27a84e4db20be3eb84b78ee297f4f4d066d2a53cb6fe17e5bc861cf71fbfd4b0`

1. Bug-repro: `tests/component/core/test_meteorite.py::TestAst1617StageErrorWarns`
   * `test_classify_fail_warns_once` — red pre-fix (0 WARNING lines; expects 1 with candidate id, source kind, source id, error)
   * `test_map_error_warns_once` — red pre-fix (same)
   * `test_error_row_insert_failure_logs_once_no_extra_warn` — guard, green before and after (the `if not failed` path keeps one `logger.exception` line)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_meteorite.py::TestAst1617StageErrorWarns \
  -q
```

**Broken / obsolete:** none. No existing test in `test_meteorite.py`, `test_contact.py`, `test_inbox.py`, or `test_api_inbox.py` asserts that there is no warning on these paths.

**Verified here:** red on the pre-fix tree (local sync and merged sub tip). Green side is for test-fix after make-fix.

### Comments

#### radia — 2026-09-26T23:12:26.804Z
[code-rubric] REVIEW (Commit: 21de0e95) fix faithful; rebase sub pre-merge

#### katherine — 2026-09-26T23:10:46.280Z
test-fix: **Tests Passed** — `origin/sub/AST-1555/AST-1617-check-inbox-total-errors-without-errorwarning-logs` @ `21de0e95` (sync-child ok, no new commits).

**[bug-repro] red→green verified** — `tests/component/core/test_meteorite.py::TestAst1617StageErrorWarns`:
- pre-fix `src/core/meteorite.py` (21de0e95~1): 2 failed, 1 passed (classify-fail + map-error warns missing; insert-fail guard already single-log)
- with fix: 3 passed

**Related suites** (board-betty's list: `test_meteorite.py`, `test_contact.py`, `test_inbox.py`), run on pre-fix and fixed trees: the fix only removes the 2 repro failures; the other 16 failures are identical on both trees → no regressions from this fix.

**The 4 pre-existing `test_meteorite.py` failures are NOT in AST-1617's scope** (none exercise the `stage_meteorite` classify/map error returns):
- `TestAst1559CheckInbox::test_sanitize_monitor_subject` — `AttributeError: _sanitize_meteorite_monitor_subject`; helper removed on dev by `bd1ba8c3` ("align meteorite.py with the four logging statutes"), test not updated.
- `TestAst1559CheckInbox::test_skip_outcome_zero_rows_monitor_archive`, `TestAst1517CreateContactMeteorite::test_debug_true_emits_style_d` — count asserts `0 == N` on the old check_inbox/debug paths.
- `TestAst1693RunLandBotBlocked::test_contentful_bot_blocked_lands_with_http_link` — `ValueError: state required for new job` (fixture predates the job-state requirement).
Also 12 `test_contact.py` failures (AST-1071/1073/1101/1207/1515 classes), same both trees. Unrelated pre-existing breakage from dev/ftr product drift — flagging for Betty/Chuckles, not blocking this bug.

Env note: epic worktree has no `.venv` and host has only python3.14; ran with `ASTRAL_PYTHON=/home/susan/astral-tests/.venv/bin/python`.

#### katherine — 2026-09-26T23:08:42.171Z
make-fix: `stage_meteorite` now emits one `_warn_item` on the classify-fail and map-error returns when the ERROR row saves (guarded so a failed insert still logs once). [bug-repro] `TestAst1617StageErrorWarns` 3/3 green. Published `sub/AST-1555/AST-1617-check-inbox-total-errors-without-errorwarning-logs` @ 21de0e95.

Note: 4 other tests in `test_meteorite.py` (TestAst1517CreateContactMeteorite::test_debug_true_emits_style_d, TestAst1559CheckInbox::test_skip_outcome_zero_rows_monitor_archive, TestAst1559CheckInbox::test_sanitize_monitor_subject, TestAst1693RunLandBotBlocked::test_contentful_bot_blocked_lands_with_http_link) fail identically without this change — pre-existing after the dev sync, not touched here.

#### betty — 2026-09-26T23:06:23.236Z
[bug-repro]
`origin/sub/AST-1555/AST-1617-check-inbox-total-errors-without-errorwarning-logs` @ `9ea87f04` · repro lands red, awaits fix

#### joan — 2026-09-26T23:03:48.524Z
[board-joan]  CANON: OK

#### betty — 2026-09-26T23:03:33.992Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/meteorite.md (stage_meteorite) — missing coverage — no test asserts an always-on WARNING (cid/kind/sid/err) on the classify-fail fallthrough or map-error paths when the ERROR-row insert succeeds; the fix needs a [bug-repro] caplog test for both paths plus a guard that the insert-fail path still warns only once. Katherine's concern is cleared: no existing test in test_meteorite.py, test_contact.py, or test_inbox.py asserts that there is NO warning on these fixtures (test_contact ~L774 is the Estelle turn, not stage), so nothing breaks.

#### katherine — 2026-09-26T23:02:19.248Z
`origin/sub/AST-1555/AST-1617-check-inbox-total-errors-without-errorwarning-logs` @ `04bd6c3d2ca15794eb30f4ad336c8a446768ec40` · warn at stage source

#### chuckles — 2026-09-26T22:58:44.012Z
[check-linear] Todo > bug-fix (UAT-batch) — armed

**What I did**
* **Git (parent AST-1555):** finish-up had deleted `ftr` + all `sub/*` and removed the epic worktree. Re-pushed `origin/ftr/AST-1555-meteorite-ingress-staging-table-inbox-meteorite-consolidation` and `origin/sub/AST-1555/AST-1617-check-inbox-total-errors-without-errorwarning-logs`, both at `origin/dev` tip `12edd9b3` (dev already has everything AST-1555 shipped). Re-created `/home/susan/astral-AST-1555` on that `ftr`. Epic registry refs already matched, so no change needed there.
* **AST-1617:** added `## Remaining gap` to the Description (the two paths still missing an always-on warn: ingest on `stage["error"]`, and `stage_meteorite` classify-fail fallthrough). Assignee Katherine → **Chuckles**, status stays **Todo**, `Bug` label already present. That's the `[bug-fix]` trigger. It takes the UAT-batch branch (parentId set) and restores Katherine before spawning plan-fix.
* **Parent AST-1555 in Linear:** no change. It stays User Testing / Chuckles with no Active label. `[uat]` holds, since AST-1617 isn't User Testing yet. When AST-1617 reaches User Testing, bug-fix does merge-child into the revived `ftr`, then moves the parent to In Progress, then datt runs prep-uat.

**Check-linear rules I overrode**
1. §3 "never change status/assignee/spawn": the Bug-ticket kick exception only covers fix-lane statuses. **Todo is not covered**, and I reassigned anyway.
2. §3 / §4c-1 "leave assignee alone": I took AST-1617 off Katherine.
3. §3 "do not run pipeline skills": I did bug-find §0-style git seeding and finish-up recovery (pushed `ftr`/`sub` refs, ran `epic-create`). check-linear has no git-write lane.
4. §4 "comment = status line only": this reply is a full report because you asked for one.

**Rule gaps worth closing**
* finish-up closes the parent while a non-Done Bug child is still open. It should block, or at least warn, when any child is short of Done.
* bug-find §0 assumes the parent `ftr` is alive. It has no step for reviving `ftr` from `origin/dev` when the parent was already finished.
* The check-linear Bug-kick exception should include **Todo** (with a git-seed preflight) or hand off to a dedicated skill.

#### susan — 2026-09-26T22:56:57.359Z
@chuckles Yes.  Please update this ticket and its parent to ensure that team-chuckles uat-fix will properly continue to finish the ticket.  Override any check-linear update constraints, and report back what you did, and what you had to override to make it happen so we can update the rules.

#### chuckles — 2026-09-24T18:18:45.541Z
[check-linear] not Done — confirm failed

Re-checked `origin/dev` `ingest_candidate_email_message`: most `counter=error` exits already hit `_warn_item` / `logger.exception`, but when `stage_meteorite` returns `error`, ingest still bumps `counter=error` with no always-on WARNING/ERROR on that mid (and `stage_meteorite` classify-fail can return `error` after a successful ERROR-row insert without warning either).

Leaving **Todo** / Katherine. Want her to land the one-line warn, or treat that path differently?

#### susan — 2026-09-24T18:16:53.585Z
@chuckles Confirm and done, please?

#### chuckles — 2026-09-15T11:53:45.969Z
[check-linear] answered

Linear truth: **Todo**, assignee **Katherine**, child of AST-1555 (parent **User Testing** / Susan). Never entered the build pipeline — siblings 1557–1562 are already at User Testing.

On current `origin/dev`, `ingest_candidate_email_message` error paths that return `counter=error` already call always-on `logger.warning` (`_warn_item`) or `logger.exception` — so the filed gap may already be closed in product, but this ticket was never verified or closed.

Leave Todo/Katherine until you want a quick confirm-and-Done vs keep as open Bug.

#### susan — 2026-09-15T11:50:56.631Z
@chuckles what is the true status of this issue?

#### susan — 2026-09-10T00:02:42.206Z
How are we logging errors for other task work like this? Is it different from what you are proposing here?

---

_Implementation detail may live in git history on `origin/dev`._
