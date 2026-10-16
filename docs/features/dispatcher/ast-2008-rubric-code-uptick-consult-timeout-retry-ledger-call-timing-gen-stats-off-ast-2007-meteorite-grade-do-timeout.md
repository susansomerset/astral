# AST-2008 — Rubric code uptick, consult timeout retry, ledger call timing, gen-stats off (AST-2007 meteorite_grade_do timeout)

<!-- linear-archive: AST-2008 archived 2026-10-13 -->

## Linear archive (AST-2008)

**Archived:** 2026-10-13  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2008/rubric-code-uptick-consult-timeout-retry-ledger-call-timing-gen-stats  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / 5  
**Parent:** AST-2007 — [✅/Somerset] meteorite_grade_do COMPLETED: 1 error(s) / 1 processed | meteorite_grade_do-10174658-7e64-4b31-9614-edec432f69c1  
**Blocked by / blocks / related:** parent: AST-2007

### Description

## What this implements

The `fix` child for orphaned bug AST-2007 (meteorite_grade_do provider timeout). Covers four parts, all approved by Susan on AST-2007:

1. Duplicate rubric codes self-heal before every rubric save (UI and craft) by upticking the later code's last letter (X, Y, Z, A, B, …) instead of raising.
2. A provider call-budget timeout on a consult task gets one retry-holding hop instead of going straight to `error_state`.
3. `dispatch_ledger` records the LLM call's duration and timeout/failure status, including on failed calls.
4. The OpenRouter generation-stats platform-cost reconcile is deactivated behind a config switch, to be revisited in a new epic.

## Scope

## Component scope

* `src/core/candidate.py`: modified. Home of the new pre-save rubric code dedupe helper, wired into `apply_rubric_vectors_save` (shared by UI and craft). `_assert_unique_rubric_codes`'s raise is retired.
* `src/core/consult.py`: modified. The single-job render-verdict failure branch must send a provider timeout to retry holding instead of directly to `error_state`.
* `src/data/database.py`: modified. `dispatch_ledger` schema gains call-duration and timeout/failure-class columns (create + idempotent migration). `update_dispatch_ledger`'s column allowlist picks them up.
* `src/core/agent.py`: modified. After `_send_to_server`, record call duration and failure class on the active ledger row for failed calls too, not just the success-only host write.
* `src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx`: modified, optional. Shows the new ledger columns if Susan wants them visible in the Performance Monitor rather than DB-only.
* `src/utils/config.py`: modified. Holds the new switch that deactivates the generation-stats platform-cost reconcile, next to its existing tunables.
* `src/core/timesheets.py`: modified. `record_timesheet_entry` must honor that switch and stop spawning the reconcile thread.
* `src/data/database.py` (rubric sync, amended per AST-2008 \[scope-gate\]): modified. `sync_rubric_vectors_from_criteria` must retire extra current `rubric_vector` rows that share a code, so stored duplicates (like somerset's `TP` pair) actually clear on the next save instead of piling up upticked copies.

## Technical scope

* `src/core/candidate.py`: new function, a pure code-dedupe helper (criteria list in, same list with later duplicate codes re-lettered). `apply_rubric_vectors_save` is modified to call it before sync. `normalize_rubric_artifacts_on_save` is modified to drop the raising duplicate check, so collisions are repaired rather than rejected.
* `src/core/consult.py`: modified function. The single-job render-verdict path adds a timeout branch that resolves its destination through the existing `_consult_batch_fail_dest`, so the timeout gets a retry hop, consistent with batch routing.
* `src/data/database.py`: modified functions and new fields. `_ensure_dispatch_ledger_schema` adds two columns, and the update path accepts them. Old rows stay NULL.
* `src/core/agent.py`: modified function. `do_task`'s post-call ledger write records duration and failure class from the provider result on every outcome. It stays off the event loop and non-fatal, like the host write.
* `src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx` (optional): modified component, adding two columns to the ledger table.
* `src/utils/config.py`: new field. A boolean enable flag for the timesheet platform-cost reconcile, default off, so deactivation is config-owned rather than deleted code.
* `src/core/timesheets.py`: modified function. `record_timesheet_entry` gets an early return when the flag is off. `reconcile_timesheet_platform` and `get_generation_stats` stay unchanged for the future epic.
* `src/data/database.py` (rubric sync): modified function. When several `current = 1` rows for one (candidate, task_key) share a code, `sync_rubric_vectors_from_criteria` keeps the first (rowid order) and retires the rest through the existing retire helper. Without this, the dict keyed by code masks the older duplicate and it is never retired.

## Defaults carried from AST-2007 (Susan approved)

* Duplicate codes are always upticked, including identical-label pairs. Nothing is collapsed.
* "Get a retry" means one retry-holding hop (AST-642 convention), not an immediate in-call re-send.

## Notes for planning

Approved ancestor: AST-1513 (archived; doc `docs/features/consult/ast-1513-reject-duplicate-do-rubric-codes-meteorite-grade-do-is-failing.md`). Patch that doc with a `## Bug: <this-id>` block. Full as-is/to-be lives on parent [AST-2007](https://linear.app/astralcareermatch/issue/AST-2007).

## Git branch (authoritative)

Orphaned mini-parent: `ftr/AST-2007-meteorite-grade-do-timeout`, child `sub/AST-2007/AST-2008-rubric-codes-timeout-ledger`. Seeded off `origin/dev` by bug-fix.

### Comments

#### radia — 2026-10-06T19:47:47.141Z
[code-rubric] PROCEED (Commit: 9efa75aa) four-part meteorite fix clean

#### betty — 2026-10-06T19:40:35.778Z
[bug-repro]
`origin/sub/AST-2007/AST-2008-rubric-codes-timeout-ledger` @ `4e14f509b` · repro lands red, awaits fix

#### joan — 2026-10-06T19:22:58.023Z
[board-joan]  CANON: OK

#### betty — 2026-10-06T19:22:44.931Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/{candidate,timesheets}.md + core/agent ledger (TestAst1960LedgerHost) — 3 broken tests + no repro coverage for Steps 1–5 — test_normalize_rejects_duplicate_do_rubric_codes (expects ValueError), TestAst1966RecordNeverWaits::test_openrouter_row_returns_before_blocked_lookup (waits on reconcile thread; flag off → platform_cost stays NULL), TestAst1960LedgerHost::test_ledger_write_failure_never_fails_the_call (asserts "Ledger host write failed" text Step 5 renames); no existing node covers uptick, sync duplicate-row retire, render_verdict provider_call_timeout → _RETRY/terminal, ledger llm_call_seconds/llm_failure_class columns+write, or flag-off no-spawn. candidate/consult/agent/timesheets are LOCKED_AT_100, so new branches need coverage. Integration tier unaffected.

#### hedy — 2026-10-06T19:21:27.686Z
`origin/sub/AST-2007/AST-2008-rubric-codes-timeout-ledger` @ `493b127a8` · uptick, sync retire, timeout hop

#### chuckles — 2026-10-06T19:19:23.079Z
Scope amended on AST-2008 and AST-2007: `src/data/database.py` `sync_rubric_vectors_from_criteria` (retire extra current rows sharing a code, keep first by rowid). Resuming plan-fix.

#### hedy — 2026-10-06T19:18:34.768Z
[scope-gate] @chuckles — plan-fix stopped before Proposed change; one database.py function missing from scope.

**Needed:** `src/data/database.py` → `sync_rubric_vectors_from_criteria` (modified function): when two or more `current = 1` rubric_vector rows for one (candidate, task_key) share a code, keep the first (rowid order) and retire the extras via `_retire_rubric_vector_row_on_connection`, so stored codes become unique on the next save.

**Scope lines that don't cover it:**
- Component: "`src/data/database.py`: modified. `dispatch_ledger` schema gains call-duration and timeout/failure-class columns … `update_dispatch_ledger`'s column allowlist picks them up."
- Technical: "`src/data/database.py`: modified functions and new fields. `_ensure_dispatch_ledger_schema` adds two columns, and the update path accepts them."

Both are ledger-only. Neither names rubric_vector sync.

**Why the fix can't stay inside them:** `sync_rubric_vectors_from_criteria` builds `current_by_code` as a dict, so with two stored `TP` rows only the *last* is tracked. Its retire loop only retires codes missing from the incoming list. The earlier `TP` row is never matched and never retired. With the uptick helper in place, re-saving somerset's Do rubric (AST-2007 step 5) sends `TP, TX`. Sync updates one `TP`, inserts `TX`, and leaves the orphan `TP` current, so the stored rows end up `TP, TP, TX`. The next read still has the duplicate, and every later save adds one more letter (`TY`, `TZ`, …). This same masking explains why AST-1513's staging re-save (HT vs TP) didn't clear the collision. Changing only `candidate.py` can't retire a stored row. The alternative is a manual staging-ops retire of the orphan row, but that repairs somerset only and leaves the sync defect for any other legacy duplicates.

This is a small omission, a one-function amendment on a file already in scope. It's not a change of approach.

After amending, assign this bug to Chuckles.

---

_Implementation detail may live in git history on `origin/dev`._
