# AST-533 — BUG: Scheduled Actions ignore dispatch task_key — consult hardcodes state→task routing

<!-- linear-archive: AST-533 archived 2026-06-23 -->

## Linear archive (AST-533)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-533/bug-scheduled-actions-ignore-dispatch-task-key-consult-hardcodes  
**Status at archive:** Done  
**Project:** Astral Dispatcher  
**Assignee:** susan  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Susan discovered during [AST-528](https://linear.app/astralcareermatch/issue/AST-528/per-hop-execution-history-for-daisy-chained-tasks) UAT that clicking **Run** on a Scheduled Action row (e.g. `anticipate_scan` with Input State `BUILD_ARTIFACTS`) does **not** execute the task named on that row. The dispatcher reads `trigger_state` from the database to claim entities, then consult re-derives which LLM task to run from a **hardcoded Python map** (`_INPUT_STATE_TO_TASK`) — ignoring `dispatch_task.task_key` entirely. For `BUILD_ARTIFACTS`, execution always enters at `contemplate_job`, and may chain to other hops via `run_next`. The UI, ledger labels, and Susan's intent all say one task; runtime runs another.

This contradicts **ASTRAL_CODE_RULES** §2.1 (`dispatch_task` DB table as sole source of truth for dispatchable batch tasks) and makes Scheduled Actions untrustworthy — including for Phase E artifact chains, roster `TO_WATCH` trio rows, and any future dispatch row where `task_key` and the legacy state map diverge.

This epic fixes dispatch routing so **the row's** `task_key` **is the execution entry point**; `trigger_state` selects **which entities** to process, not **which task** runs.

## Functional scope

* **Honest Scheduled Actions Run:** When Susan clicks Run (or Auto fires) on a `dispatch_task` row, the first LLM hop executed for that run is the row's `task_key`, not a value inferred from `trigger_state` via hardcoded consult routing.
* **Entity claim unchanged:** `trigger_state` on the row continues to determine which jobs/companies/board rows/candidates are eligible and claimed for that run.
* **Job consult pipeline:** All job dispatch steps (validate, qualify, scrape, evaluate, DO/GET/LIKE, analysis_upshot, artifact entry, cover-letter entry) route by `task_key` **from the active dispatch row**, not by a parallel state→task dictionary in consult.
* **Company roster dispatch:** Company dispatch rows that share a `trigger_state` (e.g. multiple `TO_WATCH` task keys) each run the behavior matching **their** `task_key` — not a single hardcoded default for that state.
* **Phase E artifact chains:** When a dispatch row's `task_key` is a chain hop (e.g. `anticipate_scan`), Run starts the chain at **that** hop. Further hops follow `run_next` only. No second hidden entry task forced by state mapping or a separate hardcoded "first chain key" that overrides the dispatch row.
* **Retry trigger states:** Jobs in retry states (e.g. `VALID_TITLE_RETRY`, `JD_READY_RETRY`, `PASSED_LIKE_RETRY`) still run the correct task when the dispatch row's `trigger_state` matches — via the row's `task_key`, not a consult-side alias map (unless Susan chooses a minimal alias table in Open questions).
* **Admin UI alignment:** Scheduled Actions task picker, row display, and Execution History task column all reflect **what actually ran** — no cosmetic `task_key` on the row that runtime ignores.
* **Regression safety:** Existing seeded dispatch rows (one canonical row per trigger state per candidate) continue to behave as today when `task_key` matches the former map — no silent behavior change for correctly seeded production rows.

## Boundaries

* Does **not** change Manage Tasks `run_next` authoring model (still Susan's chain wiring in Admin).
* Does **not** reintroduce ordered pipeline step arrays in code.
* Does **not** fix [AST-529](https://linear.app/astralcareermatch/issue/AST-529/caller-system-empty-on-mid-chain-hops) caller-token propagation (separate ticket; may be easier to verify after honest entry routing).
* Does **not** redesign the `UNIQUE(candidate_id, trigger_state)` schema unless Susan approves in Open questions — schema change is optional follow-up, not assumed.
* Does **not** change ad-hoc workbench, craft Generate, or `user-` / `adhoc-` ledger prefix flows (non-dispatch paths).
* Does **not** remove `TASK_CONFIG` or move prompt definitions to the database.

Per **ASTRAL_CODE_RULES** §2.1: after this fix, `dispatch_task` is the runtime source of truth for **which task runs**, not just scheduling metadata.

## Acceptance criteria

1. **Repro fixed (Susan UAT case):** With `anticipate_scan` unlinked from downstream hops and a Scheduled Action row `task_key=anticipate_scan`, `trigger_state=BUILD_ARTIFACTS`, manual Run executes `anticipate_scan` **only** — `contemplate_job` **does not run** unless `run_next` or a separate dispatch row says so.
2. **Row task_key drives entry:** For every seeded job dispatch row (`evaluate_jd` @ `JD_READY`, `consult_do` @ `PASSED_JD`, `contemplate_job` @ `BUILD_ARTIFACTS`, etc.), Run executes that row's `task_key` as the first hop.
3. **TO_WATCH trio:** Separate dispatch rows for `find_job_page`, `select_job_page`, and `parse_job_list` (same `trigger_state=TO_WATCH`) each run their respective task on Run — not all routed to `find_job_page`.
4. **No consult state→task router for dispatch:** Dispatch execution paths do not consult a hardcoded `input_state → task_key` map to choose the runner. (Minimal retry alias, if Susan approves, is the only exception and must be documented.)
5. **No duplicate artifact entry override:** Phase E dispatch does not force a second hardcoded "chain first key" that overrides the dispatch row's `task_key` when starting a chain.
6. **Execution History honesty:** First hop ledger row's Task column matches the dispatch row's `task_key` for single-hop runs; chained runs show per-hop keys per [AST-531](https://linear.app/astralcareermatch/issue/AST-531/per-hop-dispatch-ledger-rows-for-run-next-chains-per-hop-execution) without a surprise extra entry hop.
7. **Tests:** Component tests lock dispatch-row `task_key` routing for at least: one job consult step, one artifact hop entry, and one `TO_WATCH` roster row — plus a regression test that `anticipate_scan` @ `BUILD_ARTIFACTS` does not invoke `contemplate_job` when unlinked.
8. **Bible / rules:** `ASTRAL_TEST_BIBLE` and any plan docs that assert `_INPUT_STATE_TO_TASK` as dispatch routing are updated to describe `dispatch_task.task_key` as the execution entry.

## Dependencies and blockers

* [AST-528](https://linear.app/astralcareermatch/issue/AST-528/per-hop-execution-history-for-daisy-chained-tasks) (User Testing): Susan's repro surfaced here; fix should land on integration line after UAT sign-off or as a hotfix branch — coordinate so UAT expectations are not confused with post-fix behavior.
* [AST-529](https://linear.app/astralcareermatch/issue/AST-529/caller-system-empty-on-mid-chain-hops) (Backlog): Related mid-chain caller tokens; not a hard blocker but verify after routing fix.
* None for starting definition / planning.

## Known root cause (for planners — not acceptance)

* `dispatcher._run_unified` passes `trigger_state` to `consult.run_consult_task`, not `task_key`.
* `consult._INPUT_STATE_TO_TASK` maps `BUILD_ARTIFACTS` → `contemplate_job` unconditionally.
* `run_resume_artifact_chain_for_job` uses `BUILD_CONFIG.resume_artifact_chain.first_task_key` = `contemplate_job`, ignoring dispatch row.
* [AST-516](https://linear.app/astralcareermatch/issue/AST-516/insert-task-anticipate-scan-in-the-daisy-chain) exposed all `TASK_CONFIG` keys in Scheduled Actions UI without wiring runtime to honor `task_key`.
* [AST-450](https://linear.app/astralcareermatch/issue/AST-450/register-artifact-pipeline-task-keys-dumb-chain-registry) / [AST-520](https://linear.app/astralcareermatch/issue/AST-520/register-anticipate-scan-task-key-insert-task-anticipate-scan-in-the) plans explicitly preserved this map; Radia reviewed those scopes as "plan fidelity," not end-to-end Scheduled Actions honesty.

## Open questions

1. **Schema — one row per state vs per task:** Today `UNIQUE(candidate_id, trigger_state)` allows only one dispatch row per Input State per candidate. Is that still the product rule? If Susan wants both `contemplate_job` and `anticipate_scan` rows @ `BUILD_ARTIFACTS`, we need a schema/UX change (e.g. unique on `(candidate_id, task_key)` instead). Which model do you want?
   1. Unique on all three: candidate_id, task_key, trigger_state ONLY, and ONLY as determined in the dispatch_task table for trigger state.
2. **Retry states:** OK to delete consult retry aliases entirely and require dispatch rows whose `trigger_state` is the retry state (already seeded for some)? Or keep a tiny alias map for retry states only?
   1. This should be resolved by my point in 1a.  ('somerset', 'consult_do', 'PASSED_JD') and ('somerset', 'consult_do', 'PASSED_JD_RETRY') should be perfectly valid combination of records in dispatch_task.
3. **Non-dispatch consult callers:** Confirm `run_consult_task` is dispatcher-only in production — if yes, signature can take `dispatch_task_key` explicitly; if no, list other callers before plan.
   1. If run_consult_task is for job evaluation only, then fine.  But if run_consult_task also does craft\_\* tasks and artifact daisy-chains, then it needs a consistent access point.
4. **Hotfix vs post-UAT:** Fix on current `dev` immediately, or wait until AST-528/527 UAT closes?
   1. Hot fix, because this is blocking 528 testing.

---

## Original brief

Susan UAT ([AST-528](https://linear.app/astralcareermatch/issue/AST-528/per-hop-execution-history-for-daisy-chained-tasks), May 29): Unlinked `anticipate_scan` from other tasks, ran Scheduled Action `anticipate_scan` for `BUILD_ARTIFACTS` jobs — both `anticipate_scan` and `contemplate_job` fired. Investigation: dispatcher ignores `dispatch_task.task_key`; consult `_INPUT_STATE_TO_TASK` hardcodes `BUILD_ARTIFACTS` → `contemplate_job`; artifact chain `first_task_key` reinforces same. [AST-516](https://linear.app/astralcareermatch/issue/AST-516/insert-task-anticipate-scan-in-the-daisy-chain) UI allows selecting any task key; runtime does not honor it. Susan: "create a HUGE FLIPPING BUG TICKET for this and fix it properly."

### Comments

#### chuckles — 2026-05-31T22:55:29.838Z
[check-linear]

Hotfix published:
- Local **`dev`** @ **`ba798d88`**
- **`origin/ftr/AST-533-dispatch-task-key-honesty`** @ **`9cc23d6c`** (cherry-pick; includes AST-531 helper block on ftr where it was missing)

Restart app on **`dev`** and retry **gaze** / scheduled dispatch.

— Chuckles

#### chuckles — 2026-05-31T22:53:09.524Z
[check-linear]

**@susan** — **hotfix** per your 2026-05-31 “hotfix, please.”

**Change (local `dev`, uncommitted on orchestration worktree):**
- `src/core/agent.py` — `_current_agent_task_run_next` uses `get_agent_task` only; returns `''` when no row (fixes **`gaze`**, **`recheck_no_openings`**, and any Playwright / non-`TASK_CONFIG` dispatch key).
- `tests/component/core/test_dispatcher.py` — `test_current_agent_task_run_next_missing_agent_task_row` (unit-level guard).

**Follow-up:** **[AST-537](https://linear.app/astralcareermatch/issue/AST-537)** (Backlog, Ada) — deeper `_dispatch_one` component coverage + optional LLM stub, per your ask on **AST-477**.

**UAT:** Restart app from `/Users/susan/chuckles/astral` on `dev` and re-run **gaze** / scheduled dispatch. Say **publish** if you want Ada to cherry-pick to `origin/ftr/AST-533-dispatch-task-key-honesty`.

— Chuckles

#### susan — 2026-05-31T22:52:13.193Z
hotfix, please.

#### chuckles — 2026-05-31T22:41:34.288Z
[check-linear]

**@susan** — triaged your `recheck_no_openings` traceback (2026-05-31).

**Root cause:** **AST-531** made `_dispatch_one` call `_current_agent_task_run_next(task_key)` for **every** dispatch row. That helper uses `_resolve_task_prompts`, which **requires** an `agent_task` row. **`recheck_no_openings`** is a **Playwright-only** roster batch (seed in `database.py` / `roster.py`) — it is **not** in `TASK_CONFIG`, so startup `sync_agent_tasks` never seeds it and Manage Tasks cannot fix it.

**Why it feels global:** Any tick that runs a **NO_OPENINGS** / `recheck_no_openings` scheduled row blows up in the background thread; you see it even while testing other dispatch keys.

**Workaround (UAT now):** Admin → **Scheduled Actions** — disable or delete rows with **`task_key=recheck_no_openings`** until we land a code fix.

**Fix (product, ~2 lines):** `_current_agent_task_run_next` should return `''` when `get_agent_task(task_key)` is missing (or key ∉ `TASK_CONFIG`) instead of raising — same “no run_next chain” path as today for single-hop dispatches.

Say **hotfix** if you want Ada on a child under **AST-533**; I won’t patch `src/` from orchestration without that signal.

— Chuckles

#### susan — 2026-05-31T19:51:24.559Z
Getting this error trying to run any dispatch job:

```
[recheck_no_openings] thread exited and cleared from registry
Exception in thread astral-task-2986-recheck_no_openings:
Traceback (most recent call last):
  File "/opt/homebrew/Cellar/python@3.12/3.12.13/Frameworks/Python.framework/Versions/3.12/lib/python3.12/threading.py", line 1075, in _bootstrap_inner
    self.run()
  File "/opt/homebrew/Cellar/python@3.12/3.12.13/Frameworks/Python.framework/Versions/3.12/lib/python3.12/threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "/Users/susan/chuckles/astral/src/core/dispatcher.py", line 513, in _task_thread_target
    loop.run_until_complete(_dispatch_one(task))
  File "/opt/homebrew/Cellar/python@3.12/3.12.13/Frameworks/Python.framework/Versions/3.12/lib/python3.12/asyncio/base_events.py", line 691, in run_until_complete
    return future.result()
           ^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/src/core/dispatcher.py", line 375, in _dispatch_one
    has_run_next_chain = bool(_current_agent_task_run_next(task_key))
                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/src/core/agent.py", line 1678, in _current_agent_task_run_next
    _, row = _resolve_task_prompts(task_key)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/src/core/agent.py", line 317, in _resolve_task_prompts
    raise ValueError(f"No agent_task row for '{task_key}'. Run sync_agent_tasks or configure via Manage Tasks.")
ValueError: No agent_task row for 'recheck_no_openings'. Run sync_agent_tasks or configure via Manage Tasks.
127.0.0.1 - - [31/May/2026 12:31:16] "GET /api/admin/scheduler/thread_status HTTP/1.1" 200 -
```

#### chuckles — 2026-05-30T02:04:16.210Z
## Manual test steps

Prerequisites: local **`dev`** @ **`8a153fd7`** (AST-533 merge landed). Restart app if already running.

### AST-534 — Susan repro (blocks AST-528 UAT)

1. **Manage Tasks:** Clear **`anticipate_scan.run_next`** (and ensure **`contemplate_job.run_next`** does not point to `anticipate_scan` unless you intend a chain).
2. **Scheduled Actions:** Row **`task_key=anticipate_scan`**, **Input State `BUILD_ARTIFACTS`**, your candidate.
3. **Run** on that row for a job in **`BUILD_ARTIFACTS`**.
4. **Execution History:** Expect **one hop** — **`anticipate_scan` only**. **`contemplate_job` must NOT appear** unless you wired `run_next`.
5. Repeat with row **`task_key=contemplate_job`**, same Input State — first hop should be **`contemplate_job`** (cover-letter follow-on still OK per resolve).

### AST-535 — schema + TO_WATCH (optional if rows exist)

6. **Scheduled Actions:** Create a second row with same candidate + **`trigger_state=TO_WATCH`** but different **`task_key`** (`select_job_page` vs `find_job_page`) — should **not** 409 unless exact triple duplicate.
7. **Run** each TO_WATCH row — verify Task column matches the row's **`task_key`**, not always `find_job_page`.

### Regression

8. Run any in-flight **AST-528** per-hop history check on a **chained** dispatch (with `run_next` wired) — per-hop rows still separate.

`origin/ftr/AST-533-dispatch-task-key-honesty` @ **eea58d4c** · local **`dev`** merged @ **8a153fd7**. Sub branches deleted.

— Chuckles

#### katherine — 2026-05-30T01:35:24.469Z
[check-linear]

- **§0a blocked:** `git merge origin/dev` on `dev-kath` conflicted before inbox scan could touch ticket work.
  - `docs/ASTRAL_TEST_BIBLE.md`
  - `src/core/candidate.py`
- Merge aborted; worktree back on `dev-kath` (no unmerged paths).
- **AST-533 scope:** Parent + children **AST-534** / **AST-535** — no `@katherine` threads; Katherine assigned issue ids **none** for this epic. Zero actionable comment work this pass.
- **Not run:** `plan-astral` / `build-astral` / pipeline (inbox-only pass).

#### chuckles — 2026-05-30T01:31:28.712Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-533 (parent) | ftr/AST-533-dispatch-task-key-honesty |
| AST-534 | sub/AST-533/AST-534-honor-dispatch-task-key-core-routing |
| AST-535 | sub/AST-533/AST-535-dispatch-task-triple-unique-and-roster-routing |

**blockedBy:** AST-535 → AST-534

— Chuckles

#### chuckles — 2026-05-30T01:24:30.645Z
@susan — **AST-533** definition is in the Description. Need your call on these before dispatch:

1. **Schema:** Keep `UNIQUE(candidate_id, trigger_state)` (one row per Input State), or move to unique per `task_key` so you can have both `contemplate_job` and `anticipate_scan` @ `BUILD_ARTIFACTS`?
2. **Retry states:** Drop consult retry aliases entirely (dispatch row `task_key` only), or keep a minimal retry alias map?
3. **Hotfix timing:** Land on `dev` now, or after AST-528/527 UAT closes?

Move to **Todo** + assign Chuckles when you're happy with the definition.

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
