# AST-460 — recheck_no_openings: 24h Playwright recheck for NO_OPENINGS

<!-- linear-archive: AST-460 archived 2026-06-15 -->

## Linear archive (AST-460)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-460/recheck-no-openings-24h-playwright-recheck-for-no-openings  
**Status at archive:** Done  
**Project:** Astral Roster  
**Assignee:** susan  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-461

### Description

## Purpose

Companies in **NO_OPENINGS** have a known `job_site` and a stored `no_jobs_message` from an earlier roster pass. They need a cheap, periodic recheck—not full job-page discovery—to confirm the careers page still shows that message. This ticket delivers that recheck and correct routing when openings may have returned.

Supersedes the **NO_OPENINGS recheck** portion of [AST-375](https://linear.app/astralcareermatch/issue/AST-375) (canceled). Sibling: locate/parse refactor ticket (handles **JOBS_FOUND** downstream).

## Functional scope

* **Dedicated batch task** (`recheck_no_openings` or equivalent) claims companies in **NO_OPENINGS** only when eligible for scan (see cadence).
* **Cadence:** Respect a **24-hour** minimum between successful rechecks using the company `last_scan_at` column (same staleness idea as **WATCH** / gaze). Companies not yet due are not claimed.
* **Playwright only:** Open the stored `job_site` URL (not the company homepage, not AI). Extract visible text from the page.
* **Still no openings:** If the stored `no_jobs_message` string appears in the visible text, remain **NO_OPENINGS**, update `last_scan_at` to now, and optionally refresh stored no-jobs context for audit.
* **Openings may exist:** If the stored message is **not** found in visible text, transition the company to **JOBS_FOUND** (new company state). Do not run parse or select in this task.
* **Mis-route fix:** Ensure this task is what runs on scheduled **NO_OPENINGS** recheck—not full `locate_job_page` / homepage discovery (align dispatch rows in a follow-up; not required to ship this ticket).

## Boundaries

* Does **not** run AI tasks (no `select_job_page`, no `parse_job_list`).
* Does **not** persist job-list visible text or DOM (nothing to cache while still **NO_OPENINGS**).
* Does **not** implement parse, `run_next`, or the locate/parse split (sibling ticket).
* Does **not** reconfigure dispatch table rows (follow-up after both siblings land).
* Does **not** auto-backfill companies in **ERROR_LOCATE_JOB_PAGE** (manual cleanup).
* Adds **JOBS_FOUND** to the config-driven company state machine with transitions defined here and in the sibling ticket.

## Acceptance criteria

1. **Eligible cadence:** A **NO_OPENINGS** company with `last_scan_at` within the last 24 hours is not claimed by the recheck task.
2. **Playwright path:** Recheck loads `job_site` and obtains visible text without homepage discovery.
3. **Message still present:** When `no_jobs_message` is found in visible text, state stays **NO_OPENINGS** and `last_scan_at` updates.
4. **Message absent:** When `no_jobs_message` is not found in visible text, state becomes **JOBS_FOUND** (not **WATCH**, not parse yet).
5. **No AI spend:** Recheck batch produces no agent/Anthropic calls for the happy path.
6. **Regression:** **TO_WATCH** locate flow and **WATCH** gaze behavior are unchanged.

## Dependencies and blockers

* None blocking start.
* **Sibling ticket (locate/parse refactor):** Defines processing for companies in **JOBS_FOUND** after this ticket routes them there. Ticket 1 may ship first; **JOBS_FOUND** companies wait for sibling parse/verify path.

## Open questions

None.

### Comments

#### chuckles — 2026-05-24T01:05:27.983Z
## Landed on origin/dev — Chuckles

- Merged `origin/ftr/AST-460-recheck-no-openings-24h-playwright-recheck-for-no-openings` → local `dev` → pushed `origin/dev`
- Deleted `origin/ftr/AST-460-recheck-no-openings-24h-playwright-recheck-for-no-openings`
- Moved to **Done** (were PR Ready): **AST-460** (parent), **AST-463** (child — assignee Hedy unchanged)

**Push tip:** `a2699e94` (`merge(AST-460): finish-up — land feature branch on dev`)

**Note:** Local `dev` also contained other prep-UAT rollups already on your machine; this push advanced `origin/dev` from `394fa9bb` → `a2699e94` (full local integration line, not AST-460 commits in isolation).

**Engineers — merge before your next skill** (orientation-astral § Merge integration line):

```bash
git fetch origin
git checkout dev-<agent>
git merge origin/dev
```

Do **not** rebase `origin/dev` onto `dev-<agent>` unless Susan directs.

— Chuckles

#### chuckles — 2026-05-24T00:36:01.765Z
## UAT Ready — Chuckles

All **1** child branch merged into parent branch and child branch deleted.

**Parent branch:** `origin/ftr/AST-460-recheck-no-openings-24h-playwright-recheck-for-no-openings` (tip **`6879990a`**)

**Merged in order:**
1. **AST-463** — recheck_no_openings: JOBS_FOUND state and Playwright recheck batch (`sub/AST-460/AST-463-recheck-no-openings-jobs-found-state-and-playwright-recheck-batch` — **deleted**)

Local **`dev`** already merged (prep-uat §8). Restart the app if it is running, then test.

**Engineers — after Susan runs finish-up and pushes `origin/dev`:** merge **`origin/dev`** into your integration branch (**orientation-astral § Rebase integration line**): `git fetch origin && git checkout dev-<agent> && git rebase origin/dev` — do **not** merge **`origin/dev`** onto **`dev-<agent>`** unless Susan directs.

## Manual test steps

**Prerequisites:** Local `dev` at **`6879990a`** (or `git merge origin/ftr/AST-460-recheck-no-openings-24h-playwright-recheck-for-no-openings`). DB migrated (dispatch seed runs on startup or apply migration). At least one **NO_OPENINGS** company with `job_site`, `no_jobs_message`, and `last_scan_at` old enough to be eligible (>24h).

### Dispatch / config
1. Admin → dispatch tasks: confirm row **`recheck_no_openings`** exists; legacy **`find_job_page`** row for NO_OPENINGS recheck should be migrated/absent.
2. Confirm **`locate_job_page`** dispatch input states do **not** include **NO_OPENINGS** (mis-route fix).
3. Confirm **JOBS_FOUND** appears in company state config with transition from **NO_OPENINGS**.

### Recheck batch (Playwright, no AI)
4. Run **`recheck_no_openings`** batch (CLI or admin ad-hoc) for an eligible **NO_OPENINGS** company.
5. **Message still present:** page visible text still contains stored `no_jobs_message` → company stays **NO_OPENINGS**, `last_scan_at` updates.
6. **Message absent:** edit page or use a company where message no longer appears → company becomes **JOBS_FOUND** (not WATCH, no parse).
7. **Cadence:** company with `last_scan_at` within 24h should **not** be claimed by recheck task.
8. Confirm no Anthropic/agent calls on happy path (logs or cost).

### Regression
9. **TO_WATCH** → locate flow still works for a non–NO_OPENINGS company.
10. **WATCH** gaze / `company_job_scan`: after ingest with title matchers, **`invalid_title`** counts surface correctly in gaze outcome (Radia fix-now regression).

### Out of scope (defer)
- **JOBS_FOUND** parse/verify (**AST-461**).
- Admin dispatch table row cleanup for all tasks.
- Backfill **ERROR_LOCATE_JOB_PAGE**.

If testing fails on `dev`:
```bash
git fetch origin && git reset --hard origin/dev
```

— Chuckles

#### chuckles — 2026-05-23T22:33:21.768Z
## do-all-the-things — run complete

**Parent:** AST-460
**Children:**
- AST-463 — recheck_no_openings: JOBS_FOUND state and Playwright recheck batch — **Tests Ready** — Hedy

### Completed path
- **Dispatch:** 1 child (Hedy), branches `ftr/AST-460-…` + `sub/AST-460/AST-463-…`
- **Plan:** AST-463 Plan Ready → **Plan Approved** (Chuckles validate-plan)
- **Build:** AST-463 → **Code Complete** (feature on `origin/sub/AST-460/AST-463-recheck-no-openings-jobs-found-state-and-playwright-recheck-batch`, tip through Hedy/Betty pushes)
- **QA:** Betty → **Tests Ready** + manifest + `test_api_admin` / roster component tests

### Stalled / needs Susan
- **AST-463** — **Tests Ready** (not **Tests Passed**): `check_per_file_coverage.py` fails on **`dev-hedy`** after merge (`candidate.py`, `agent.py`, `api_admin.py` branch %). Hedy posted **`[qa-handoff]`**; Betty added config lock tests on **`dev-betty`** but full component suite on Betty’s line still has unrelated integration drift. **Assign Betty** on AST-463 if not already; she should close coverage + confirm manifest item 1 green on **`dev-hedy`**, then Hedy re-runs **test-astral**.
- **dev-hedy / dev-betty rebase onto `origin/dev`:** conflicts in `tracker.py` / `config.py` (and others on Betty) — engineers should resolve per **orientation-astral § Rebase integration line** before next pipeline pass.
- **Radia review:** Skipped — gate requires **Tests Passed**.
- **resolve-astral:** Not run.

### prep-uat
- **Skipped** — AST-463 is not **User Testing** / **Review Posted**; parent not UAT-ready.

### After finish-up (Susan)
- When children reach **PR Ready** after UAT: **`finish-up AST-460`**
- Engineers **rebase** `dev-<agent>` onto `origin/dev` per **orientation-astral § Rebase integration line** — **not** `git merge origin/dev`

— Chuckles

#### ada — 2026-05-23T22:15:18.700Z
[check-linear]

- **§0a — blocked:** `git fetch origin` then `git rebase origin/dev` on `dev-ada` conflicts on **`docs/features/administrator/ast-438-production-readiness-admin-prompt-and-rubric-diagnostic.md`** (replay hits add/add vs `origin/dev`; first failing replay referenced **`3ee9e102`**). **`git rebase --abort`** — `dev-ada` unchanged, still ahead of **`origin/dev`**. Needs Susan/Chuckles on reconcile (merge vs manual integration of that doc / history).

- **§0b:** `list_issues` **`query: "@ada"`**, **Team Astral**, **`includeArchived: true`**, paginated (**5** ids: **AST-368**, **AST-453**, **AST-379**, **AST-454**, **AST-359**). Same query scoped to **Astral Roster** returned **0** hits (union unchanged). **`list_comments`** on all five; **§2 actionable:** **none** — no non-Ada comment after Ada’s latest **`[check-linear]`** / handoff that **`@ada`**’s Ada or expects a reply still open.

- **§1 (assignee add-on):** **`list_issues` with `assignee: "me"` fails from this MCP client** (JSON `"me"` not honored). Surrogate read: parent **AST-460** assignee Chuckles; dispatched child **AST-463** assignee **Hedy** — **no Ada card** on Astral Roster under this epic. Explicit session **“assigned issue ids: (none)”** interpreted as **no supplemental ID allowlist**; **§0b still ran** (skill cannot skip @-mention coverage).

- **§6:** On **`dev-ada`** (not rebased-clean). Did **not** run **`plan-astral`** / **`build-astral`** / **`test-astral`** / **`resolve-astral`** / **`qa-astral`** / **`review-astral`** from this pass.

#### katherine — 2026-05-23T22:14:34.734Z
[check-linear] blocked:

**§0a** `git rebase origin/dev` on `dev-kath` failed (aborted to restore branch).

- **Conflict:** `docs/features/boards/ast-457-manage-candidate-board-searches.md` (add/add while replaying commit `575b8438` — docs(AST-457): plan — manage candidate board searches)
- **Context:** `dev-kath` is 9 commits ahead of `origin/dev` before rebase.

Susan: resolve the add/add (or align `origin/dev` with that doc) and I can rerun §0a, or direct how you want `dev-kath` reconciled.

**Session scope:** Assigned issue allowlist was empty — no §2–§4 comment pass beyond this blocker.

#### chuckles — 2026-05-23T22:10:13.274Z
## Dispatch — Chuckles

Dispatched **1** child ticket from the approved definition.

| Ticket | Title | Assigned to | Branch | Blocked by |
|--------|-------|-------------|--------|------------|
| AST-463 | recheck_no_openings: JOBS_FOUND state and Playwright recheck batch | Hedy | sub/AST-460/AST-463-recheck-no-openings-jobs-found-state-and-playwright-recheck-batch | — |

**Assignment rationale:**
- **Hedy:** Roster pipeline (`roster.py`), company state machine, batch claim/`last_scan_at` cadence, CLI dispatch task — single cohesive unit.
- **Ada / Katherine:** Not assigned this dispatch.

Parent **In Progress**, assignee Chuckles. **prep-uat** merges child branch when **Review Posted**.

**Git (authoritative — ignore Linear `gitBranchName`):**
- Parent: `origin/ftr/AST-460-recheck-no-openings-24h-playwright-recheck-for-no-openings`
- Child: `origin/sub/AST-460/AST-463-recheck-no-openings-jobs-found-state-and-playwright-recheck-batch`

— Chuckles

#### chuckles — 2026-05-23T21:46:41.713Z
Sibling **AST-461** covers locate/`parse_job_list` split and **JOBS_FOUND** verify+parse. This ticket can ship first.

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._

## Bug: AST-1821 — recheck_no_openings Avail honors last_scan_at frequency window

Parent bug: AST-1820 (orphaned mini-parent). Susan approved stamping `last_scan_at` on failed recheck attempts, which overturns AST-463's Stage-2 "do not bump `last_scan_at` on exception" line (`docs/features/roster/ast-463-recheck-no-openings-jobs-found-state-and-playwright-recheck-batch.md`).

### As-is

The `recheck_no_openings` dispatch row (entity `company`, trigger `NO_OPENINGS`) shows an Available count that doesn't move when `freq_hrs` changes. Three defects cause it:

1. `process_recheck_no_openings` (`src/core/roster.py`) stamps `company.last_scan_at` only on its two success paths (`no_jobs_message_present`, `no_jobs_message_absent`). Three attempted-but-failed returns leave `last_scan_at` as it was: `missing job_site`, `no_jobs_message missing`, and the Playwright `except Exception` branch. The dispatcher does no failure routing for company rows, so these companies stay in `NO_OPENINGS` with a NULL or stale `last_scan_at`. They count at every frequency and get reclaimed on every run.
2. In `count_eligible_for_dispatch_task` (`src/data/database.py`), the company branch returns `count_companies_in_state_with_score_floor(...)` as soon as `task["score_floor"]` is non-null. That return skips the `last_scan_at` staleness filter entirely. The claim (`set_company_batch`, via `get_new_company_batch`) applies **both** filters, so Avail is greater than or equal to the claim.
3. The same branch reads `COMPANY_STATES.get(state)` with the literal trigger. For a `{base}_RETRY` trigger (such as `NO_OPENINGS_RETRY`), that returns `{}`, so `scan_interval_hours` is None and the staleness filter is dropped. `get_new_company_batch` resolves `batch_criteria` through `registered_base` (AST-1806), so its claim keeps the 24h default.

`freq_hrs` 0 and 24 are equivalent on this row by design: 0 falls back to `COMPANY_STATES["NO_OPENINGS"]["batch_criteria"]["scan_interval_hours"] = 24`. That is not a defect and stays unchanged.

### To-be

A `NO_OPENINGS` company whose last recheck **attempt** (success or failure) falls within the row's window is neither counted nor claimed. The window is `freq_hrs` when > 0, otherwise the 24h state default. Changing `freq_hrs` changes Available to exactly the unclaimed companies whose `last_scan_at` is NULL or older than the window. Every count path (admin dispatch list `api_admin.py`, `get_due_tasks`, and the dispatcher loop's `count_eligible_for_dispatch_task` calls) returns the same set that `set_company_batch` would claim for the row, with and without `score_floor`, and for primary and `_RETRY` triggers.

### Repro

SQLite fixture (company table, one candidate `c1821`), with the `recheck_no_openings` dispatch row: `entity_type=company`, `trigger_state=NO_OPENINGS`, `candidate_id=c1821`, `freq_hrs=48`, `score_floor=NULL`.

| short_name | state | job_site | company_data.no_jobs_message | last_scan_at |
|---|---|---|---|---|
| `acme` | NO_OPENINGS | `https://acme.test/jobs` | `No open positions` | NULL |
| `beta` | NO_OPENINGS | NULL | `No open positions` | NULL |
| `gamma` | NO_OPENINGS | `https://gamma.test/jobs` | `No open positions` | now − 1h |

1. `count_eligible_for_dispatch_task(row)` returns 2 (`acme`, `beta`). Correct today.
2. Run the row once. `beta` hits `missing job_site`, and `acme` raises in Playwright (unreachable host).
3. Count again. **As-is:** still 2, because neither `last_scan_at` moved. Changing `freq_hrs` to 1 or 168 also leaves 2. **To-be:** 0, because both were stamped just now. `freq_hrs=1` still gives 0 until an hour passes, and `gamma` joins once its `last_scan_at` falls outside the window.
4. Set `score_floor=0` on the row and give all three companies `company_data.prefilter_score=5`. **As-is:** count returns 3 (`gamma` included despite scanning 1h ago), while the claim takes only the stale ones. **To-be:** count equals the claim.
5. Set `trigger_state=NO_OPENINGS_RETRY` with a company in `NO_OPENINGS_RETRY`, `last_scan_at` = now − 1h, `freq_hrs=0`. **As-is:** counted, because `COMPANY_STATES.get("NO_OPENINGS_RETRY")` has no `batch_criteria`. **To-be:** not counted (24h base default), matching `get_new_company_batch`.

### Root cause

- `roster.py`: AST-463 deliberately tied the cadence stamp to success. With no failure routing for company rows, a failed company never leaves the eligible pool.
- `database.py`: the company branch of `count_eligible_for_dispatch_task` treats the `score_floor` count and the staleness count as mutually exclusive early returns, while the claim ANDs them. It also resolves `batch_criteria` by the literal trigger rather than the registered base state.

### Proposed change

**1. `src/core/roster.py` — `process_recheck_no_openings`**

Call `update_company_last_scan_at(short_name)` immediately before each of the three failure returns:

- `if not job_site:` → stamp, then `return {"success": False, "message": "missing job_site", "new_state": ""}`.
- `if not no_jobs_message:` → stamp, then return `"no_jobs_message missing"` unchanged.
- `except Exception as ex:` → keep `logger.exception(...)` as is, stamp, then return `f"playwright scrape: {ex}"` unchanged.

The `if not short_name:` return is **not** stamped, because there's no row key to stamp. The return payloads, `success: False`, state (stays `NO_OPENINGS`), and the two success paths are unchanged. Add a short comment above the first stamp: failed attempts stamp too, so the frequency window covers every attempt (AST-1821 overturns AST-463's no-bump-on-failure rule). Update the docstring's first line to mention that every attempted recheck stamps `last_scan_at`.

**2. `src/data/database.py` — `count_eligible_for_dispatch_task`, company branch**

Reorder the branch so that the window is resolved first and both filters compose:

```python
if entity_type == "company":
    # Implicit {base}_RETRY shares the base's batch_criteria (same lookup as get_new_company_batch, AST-1806).
    bc = (COMPANY_STATES.get(registered_base(COMPANY_STATES, state) or state) or {}).get("batch_criteria") or {}
    freq = float(task.get("freq_hrs") or 0)
    scan_from_state = bc.get("scan_interval_hours")
    scan_h = freq if freq > 0 else scan_from_state
    use_stale = scan_h is not None and float(scan_h) > 0 and (state == "WATCH" or scan_from_state is not None)
    floor_raw = task.get("score_floor")
    if floor_raw is not None:
        # Claim ANDs score_floor with the last_scan_at window; Avail must too.
        return count_companies_in_state_with_score_floor(
            candidate_id, state, float(floor_raw), states=claim_states,
            scan_interval_hours=float(scan_h) if use_stale else None,
        )
    if use_stale:
        ...  # existing staleness COUNT query, unchanged
```

- Add `registered_base` to the existing `from src.utils.config import (...)` block at the top of `database.py`. It isn't imported there today.
- The `use_stale` predicate is carried over **unchanged**. The only difference is that `bc` now comes from the base state.
- Update the function docstring's company sentence: the staleness filter applies with or without `score_floor`, and `batch_criteria` resolves through the registered base.

**3. `src/data/database.py` — `count_companies_in_state_with_score_floor`**

Add a keyword-only `scan_interval_hours: Optional[float] = None`. When it is not None, append `AND (last_scan_at IS NULL OR last_scan_at < datetime('now', '-' || ? || ' hours'))` to the WHERE clause and bind `scan_interval_hours`. This is the same fragment `set_company_batch` uses. The default None keeps the existing call shape and result (its only other caller is the component test `test_count_companies_in_state_with_score_floor`).

**4. `src/data/database.py` — `update_company_last_scan_at` docstring**

The docstring currently says "Called on success paths only". Change it to "Set last_scan_at = now for company (cadence stamp)." This is a comment-only change; the behavior stays the same.

No new table, column, config key, or state. NO_OPENINGS → JOBS_FOUND routing is untouched.

### Blast radius

- **Other company dispatch rows with `score_floor` set** (such as PREFILTER_PASSED-family rows): their base states define no `scan_interval_hours` and aren't WATCH, so `use_stale` stays False and their Avail doesn't change. Only rows whose base defines `scan_interval_hours` (NO_OPENINGS, WATCH) gain the filter.
- **`WATCH_RETRY` rows:** with the base lookup, Avail now applies the WATCH 24h/`freq_hrs` window. This matches the claim, which already did.
- **Gaze (`gazer.py`)** keeps calling `update_company_last_scan_at` on its own paths; only the docstring changes.
- **Consumers of the count:** `get_due_tasks` (auto-mode due gate: a row with only recently failed companies stops being due), the admin dispatch list (`api_admin.py`), and the dispatcher's Avail calls. After this change their values drop to the claimable set, which is intended.
- **Tests (Betty's call):** `tests/component/core/test_roster.py` (recheck routing test; recheck failure paths now call `update_company_last_scan_at`, so a real DB or unpatched helper will see the write), `tests/component/data/database/test_dispatch_tasks.py` (score-floor and company Avail counts), and `tests/component/ui/api/test_api_admin.py` / `test_dispatcher.py` (Avail values for company rows).
- **Known and left alone:** for a company row whose base has no `scan_interval_hours` and isn't WATCH, the claim still applies `freq_hrs > 0` as a window but the count doesn't. That gap predates this bug, is outside AST-1820's approved steps, and doesn't affect `recheck_no_openings`. It needs its own ticket if wanted.

### What must still hold

- AST-460 AC 1: a NO_OPENINGS company with `last_scan_at` inside the window (24h default) is not claimed. It is now also not counted, and "inside the window" includes failed attempts.
- AST-460 AC 2–5: Playwright loads `job_site` only, message present → stays NO_OPENINGS + stamp, message absent → JOBS_FOUND + stamp, no Anthropic calls. All unchanged.
- AST-460 AC 6: TO_WATCH locate and WATCH gaze behavior are unchanged, and WATCH Avail for primary triggers is identical.
- `freq_hrs=0` on the recheck row still means the 24h state default.
- Company Avail for rows with no `score_floor` and a primary trigger is identical to today.
- `count_companies_in_state_with_score_floor(cid, state, floor)` with no new kwarg returns the same result as today.

### Fix board — AST-1821

[board-betty] TESTS: REVISE: failure-path stamp tests (`TestProcessRecheckNoOpenings::test_guards_missing_fields` / `test_playwright_failure_no_state_change`) leave `update_company_last_scan_at` unpatched; no coverage for Avail with `score_floor` + the `last_scan_at` window, `{base}_RETRY` base-state `batch_criteria` lookup, or the new `scan_interval_hours` kwarg. Filed as a sibling gap child (orphaned branch).

[board-joan] CANON: OK

**Findings (AST-1821 — fix-board Joan pass)**

**Roster:** `canon/docs/DIRECTIVES-DIRECTORY.md` (no `docs/canon-index.md` on publish ref; same resolution as prior fix-board passes).

**Plan-fix read:** `docs/features/roster/ast-460-recheck-no-openings-24h-playwright-recheck-for-no-openings.md` § Bug: AST-1821 (`origin/sub/AST-1820/AST-1821-recheck-no-openings-avail-count`). Parent AST-1820 has no Canon Scope list; triage is overlap against the directive roster only (not R1–R7).

**`patt.entity.batch-criteria` — conforming, no edit required**

- **Arc 2:** `freq_hrs` and `score_floor` are eligibility predicates composed into the same claim shape as `last_scan_at` staleness. Today’s bug is exactly that the company **count** path skips staleness when `score_floor` is set and resolves `batch_criteria` on the literal `_RETRY` trigger instead of the registered base. The proposed `count_eligible_for_dispatch_task` / `count_companies_in_state_with_score_floor` work **implements** this pattern; it does not carve around it.
- **Arc 4 (`last_scan_at` on “completion”):** Stamping failed `process_recheck_no_openings` attempts so the frequency window applies is cadence enforcement for rows that remain in `NO_OPENINGS`, consistent with arc 2’s eligibility story. Susan’s overturn of AST-463’s feature-plan “no bump on failure” is product/plan authority (ticket + plan-fix), not an in-force statute. No new exception text is required for F5 to proceed.

**`astral.dispatch.entity-state-bound` — conforming**

- `registered_base` for `_RETRY` triggers in the **count** path matches the claim path (AST-1806 shape). Avail for `NO_OPENINGS_RETRY` / `WATCH_RETRY` moving to match `set_company_batch` is count/claim honesty, not a registry violation.

**`stat.batch.claim-process-release` / `patt.entity.batch-processing` — no impact**

- No change to claim → process → release or batch locking; only eligibility counting and when `update_company_last_scan_at` runs inside an existing company batch handler.

**`patt.task.dispatch-retry` — pre-existing tension, not introduced by this fix**

- Arc 5 (“failure does not persist in state”) still disagrees with **already-shipped** behavior: failed recheck returns stay in `NO_OPENINGS` without `_RETRY` routing. AST-1821 does not change that routing; it only stamps `last_scan_at` and fixes count/claim parity. Routing failures through retry states would be a **different** product decision (parent step 2 alternative), not a canon patch required by this plan-fix. Not ESCALATE here — Susan already chose throttle-via-stamp on AST-1820.

**Blast radius (canon lens)**

- `get_due_tasks` / admin Avail dropping to the claimable set is intended alignment with batch-criteria, not a new dispatch precedent.
- Plan’s known left-alone gap (company rows with `freq_hrs > 0` but no state `scan_interval_hours` and not WATCH) is explicitly out of AST-1820 scope; no statute touch.

### Radia review-fix — AST-1821

[code-rubric] PROCEED (Commit: 4dd0af80): clean.

#### Fix-specific checks

- **[bug-repro]** not applicable — clean board opt-out: `[board-betty] TESTS: REVISE` is owned by sibling **AST-1822**; qa-fix did not run on this tip; no `[bug-repro]` expected here.
- **## What must still hold — OK** — Traced all six bullets against the tip diff: success paths and JOBS_FOUND routing untouched; `freq_hrs=0` → state default unchanged; `count_companies_in_state_with_score_floor` default kwarg preserves prior SQL; primary-trigger Avail without `score_floor` unchanged for `NO_OPENINGS` (base lookup is identity); intentional `WATCH_RETRY` / `NO_OPENINGS_RETRY` count alignment matches plan blast radius without altering primary WATCH claim behavior.

#### Canon scores

**Notes:** Linear Description has no **Canon Scope (frozen at plan)** block (same as fix-board Joan read). Scored the overlap Joan triaged in the issue doc § Fix board — AST-1821 (`patt.entity.batch-criteria`, `astral.dispatch.entity-state-bound`, `patt.entity.batch-processing`, `astral.batch.claim-process-release`, `patt.task.dispatch-retry`). Process gap for Archie if fix bugs should carry explicit frozen lists; not product **ESCALATE**.

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.entity.batch-criteria | A | | |
| astral.dispatch.entity-state-bound | A | | |
| patt.entity.batch-processing | X | | diff does not touch claim/process/release |
| astral.batch.claim-process-release | X | | diff does not touch claim/process/release |
| patt.task.dispatch-retry | A | | stamp-only; arc-5 routing tension pre-existing on ftr |

#### Column diff vs plan stage

no plan-stage scores attached (fix-board Joan narrative only; no validate-plan F3 score table)

#### Frame diff

(none)

#### Findings

**fix-now:** (none)

**discuss:** (none)

**advisory:**

- **Canon Scope on ticket:** Description lacks a frozen canon list; scored board overlap per `docs/features/meteorite/ast-1784-…` precedent.
- **`patt.task.dispatch-retry` arc 5:** Failed recheck still leaves companies in `NO_OPENINGS` without `_RETRY` routing — unchanged by this diff; Susan already chose throttle-via-`last_scan_at` on AST-1820; not introduced here.
- **Test gap:** Failure-path stamp and Avail composition assertions land on **AST-1822**; existing `TestProcessRecheckNoOpenings` nodes still pass unpatched (per Hedy test-fix comment).

#### What's solid

- `process_recheck_no_openings` stamps `update_company_last_scan_at` on the three failure returns, not on `missing short_name`, matching plan-fix.
- Company branch resolves `batch_criteria` via `registered_base`, composes `score_floor` with the same `use_stale` / `scan_h` logic as the non-floor path, and threads `scan_interval_hours` into `count_companies_in_state_with_score_floor` with SQL bind order matching placeholders.
- Docstring-only `update_company_last_scan_at` update matches behavior.

#### Chuckles — post-review branching

| Gate | Parent shape | Next action |
|------|--------------|-------------|
| **PROCEED** (C7 complete) | **Orphaned** mini-parent AST-1820 | → **Review Posted** → skip `resolve-child` / `merge-child` / `prep-uat` → merge `sub/AST-1820/AST-1821-recheck-no-openings-avail-count` **straight to `origin/dev`** (finish-up-style) once Susan’s lane allows. |

**Plan fidelity:** Diff implements plan-fix § Bug: AST-1821 **Proposed change** (roster stamps + database count composition + kwarg). **Estimate 3** footprint fits (two modules, no schema). **Cross-ticket scope:** Product diff is AST-1821-only; no sibling product smuggle.

#### Chuckles disposition

Clean review: Review Posted → User Testing (resolve-child skipped). Docs-acceptance on this tip: the test/bible delivery is sibling gap AST-1822. merge-child goes into this bug's own `ftr/AST-1820-recheck-no-openings-avail-count` (orphaned mini-parent), not straight to dev.
