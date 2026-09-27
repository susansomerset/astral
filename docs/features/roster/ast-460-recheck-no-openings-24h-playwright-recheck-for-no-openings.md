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

## Bug: AST-1822 — recheck_no_openings failure-stamp + Avail window tests (AST-1821 board)

Test-gap sibling of AST-1821. It answers AST-1821's `[board-betty] TESTS: REVISE`. **Test and bible only:** Betty lands every item below at qa-fix, and there are no product edits. The product change under test is AST-1821's § "Bug: AST-1821 — recheck_no_openings Avail honors last_scan_at frequency window" in this doc. That section and the code live on `origin/sub/AST-1820/AST-1821-recheck-no-openings-avail-count` @ `4dd0af80` until merge-child rolls them into `origin/ftr/AST-1820-recheck-no-openings-avail-count`.

### As-is

- `TestProcessRecheckNoOpenings::test_guards_missing_fields` and `::test_playwright_failure_no_state_change` (`tests/component/core/test_roster.py`) **pass** on the AST-1821 tip, but they don't patch `roster_mod.update_company_last_scan_at` and assert nothing about it. The new failure-path stamp goes unverified, and the real helper runs against the test DB.
- There's no `test_dispatch_tasks.py` coverage for: (a) company Avail with `score_floor` set that still honors the `last_scan_at` window, (b) a `{base}_RETRY` trigger resolving `batch_criteria` through the base state, (c) Avail equal to the claim under `score_floor` + window, and (d) the new `scan_interval_hours` kwarg on `count_companies_in_state_with_score_floor`.
- The bible rows for recheck (`docs/test-bible/core/roster.md` § AST-463 · AST-460) and for company Avail (`docs/test-bible/data/database.md`) don't mention any of this.

### To-be

Every AST-1821 behavior has a named test that **fails against pre-AST-1821 product** (`4dd0af80~1`) and **passes on `4dd0af80`**. The bible names those nodes.

### Repro

Run the nodes below against `4dd0af80~1`: each fails as noted per case. Run them against `4dd0af80`: all pass. Seed rules for every database case:

- `candidate_id = "c1821"`. All companies are created with `db.save_company(short_name, state=..., candidate_id="c1821", company_name=short_name, company_data={"prefilter_score": 5.0, "no_jobs_message": "none"}, last_scan_at=...)`. `save_company` accepts `last_scan_at`, and implicit `NO_OPENINGS_RETRY` passes its `is_registered_state` check.
- **`last_scan_at` must use the SQLite text format `YYYY-MM-DD HH:MM:SS` (space, no `T`, no offset)**, the same as `database._utc_now()`. The window compares text against `datetime('now', '-N hours')`, and an ISO `T` value always sorts after a same-day space value, which silently breaks the window. Use a local helper in the class: `_ago(h) = (datetime.now(timezone.utc) - timedelta(hours=h)).strftime("%Y-%m-%d %H:%M:%S")`.
- Fixture `sqlite_in_memory`, the same one used by `TestAst508PrefilterPassedEligible`.

### Root cause

AST-1821 changed behavior (failure paths stamp; count composes window + `score_floor`; base-state `batch_criteria`; a new kwarg) without corresponding assertions. The existing recheck failure tests predate the stamp and never mocked it.

### Proposed change

**1. `tests/component/core/test_roster.py`, class `TestProcessRecheckNoOpenings` (revise two nodes, keep their names)**

- `test_guards_missing_fields`: at the top, `bump = MagicMock()` and `monkeypatch.setattr(roster_mod, "update_company_last_scan_at", bump)`.
  - After the `short_name=""` call: `bump.assert_not_called()`. The short_name guard stays unstamped.
  - After the `job_site=""` call: `bump.assert_called_once_with("co")`.
  - After the `company_data={}` call: `assert bump.call_count == 2` and `bump.call_args == call("co")`. `call` is already imported from `unittest.mock`.
  - Existing `success` / `message` assertions stay.
  - Pre-fix: fails on the `job_site` assertion (not called).
- `test_playwright_failure_no_state_change`: add `bump = MagicMock()`, `tran = MagicMock()`, patched onto `roster_mod.update_company_last_scan_at` / `roster_mod.transition_company_state`. After the call, keep the existing asserts, then add `bump.assert_called_once_with("acme")` and `tran.assert_not_called()`. Pre-fix: fails on `bump` (not called).
- Update the class docstring to add: "failed attempts (missing job_site / no_jobs_message / Playwright error) stamp last_scan_at; missing short_name does not (AST-1821)."

**2. `tests/component/data/database/test_dispatch_tasks.py`: new class `TestAst1821CompanyAvailWindow`**

Place it after `TestAst508PrefilterPassedEligible`. Docstring: "AST-1821: company Avail honors last_scan_at window with score_floor, via base-state batch_criteria; equals claim."

Seed helper `_seed(db)`, all in state `NO_OPENINGS`: `never` (`last_scan_at=None`), `stale` (`_ago(48)`), `fresh` (`_ago(1)`).

The task dict for the cases below is `{"entity_type": "company", "trigger_state": "NO_OPENINGS", "task_key": "recheck_no_openings", "candidate_id": "c1821", "score_floor": 0.0, "freq_hrs": <per case>}`.

| Node | Setup / call | Assert | Pre-fix result |
|---|---|---|---|
| `test_score_floor_default_window_excludes_recent` | `_seed`; task `freq_hrs=0` | `count_eligible_for_dispatch_task(task) == 2` (never, stale; 24h default) | 3 → fails |
| `test_score_floor_window_follows_freq_hrs` | `_seed`; `freq_hrs=72`, then the same task with `freq_hrs=0.5` | `== 1` (never), then `== 3` | first assert 3 → fails |
| `test_score_floor_count_equals_claim` | `_seed`; `n_avail` = count with `freq_hrs=0`; then `db.claim_company_batch("b1821", "NO_OPENINGS", 10, candidate_id="c1821", scan_interval_hours=24, score_floor=0.0, states=["NO_OPENINGS", "NO_OPENINGS_RETRY"])` | `n_avail == n_claimed == 2`; `{r["short_name"] for r in db.get_company_batch("b1821")} == {"never", "stale"}` | `n_avail` 3 ≠ 2 → fails |
| `test_retry_trigger_uses_base_batch_criteria` | Seed `r_fresh` (`_ago(1)`) and `r_stale` (`_ago(48)`) in state `NO_OPENINGS_RETRY`; task `trigger_state="NO_OPENINGS_RETRY"`, **no** `score_floor` key, `freq_hrs=0` | `== 1` (r_stale only; base NO_OPENINGS 24h) | 2 → fails |
| `test_score_floor_helper_scan_interval_kwarg` | `_seed`; call `count_companies_in_state_with_score_floor("c1821", "NO_OPENINGS", 0.0, states=["NO_OPENINGS", "NO_OPENINGS_RETRY"])` with no kwarg, then `scan_interval_hours=24`, then `scan_interval_hours=72` | `3`, `2`, `1` | `TypeError` on the kwarg → fails |

Unchanged and still required green: `TestAst508PrefilterPassedEligible` (all three nodes). PREFILTER_PASSED has no `scan_interval_hours` and isn't WATCH, so its Avail doesn't change.

**3. `docs/test-bible/core/roster.md`, § AST-463 · AST-460**

- Add a sentence to the paragraph: "**AST-1821:** failed attempts (missing **`job_site`**, missing **`no_jobs_message`**, Playwright exception) also stamp **`last_scan_at`**; missing **`short_name`** does not."
- In the table row for `process_recheck_no_openings`, append to the tests cell: "(**AST-1821** stamp asserts in **`test_guards_missing_fields`**, **`test_playwright_failure_no_state_change`**)".

**4. `docs/test-bible/data/database.md`: new section `### AST-1821 · AST-1820`, appended after the last section**

One-line summary: company **`count_eligible_for_dispatch_task`** composes the **`last_scan_at`** window with **`score_floor`**, resolves **`batch_criteria`** through **`registered_base`**, and equals **`claim_company_batch`**; **`count_companies_in_state_with_score_floor(scan_interval_hours=)`**. Then a table `| Area | Source | Component tests |` with one row: `src/data/database.py` (**`count_eligible_for_dispatch_task`**, **`count_companies_in_state_with_score_floor`**) → `tests/component/data/database/test_dispatch_tasks.py::TestAst1821CompanyAvailWindow` (all five nodes) + **`TestAst508PrefilterPassedEligible`** regression.

**Manifest (for test-fix):**

```bash
pytest -q tests/component/core/test_roster.py::TestProcessRecheckNoOpenings \
  tests/component/data/database/test_dispatch_tasks.py::TestAst1821CompanyAvailWindow \
  tests/component/data/database/test_dispatch_tasks.py::TestAst508PrefilterPassedEligible
```

### Blast radius

- Test tree and bible only; no product files.
- The `test_guards_missing_fields` revision stops a real `update_company_last_scan_at` write to the test DB (currently unmocked).
- The new class is self-contained (`c1821` candidate, its own batch id). It doesn't touch the shared seeds of other `test_dispatch_tasks.py` classes.
- Pre-existing failures in `test_roster.py` / `test_dispatch_tasks.py` (18 at `4dd0af80`, identical at `4dd0af80~1` per AST-1821 test-fix) are unrelated and not in this manifest.

### What must still hold

- The recheck success-path nodes (`test_message_present_updates_scan_only`, `test_message_absent_to_jobs_found`, `test_redirect_normalizes_job_site`) are unchanged and green.
- `TestAst508PrefilterPassedEligible` stays green unchanged: no `score_floor` Avail regression for states without a window.
- `TestRunCompanyTask::test_no_openings_routes_to_recheck_not_find_job_page` is unchanged: NO_OPENINGS still routes to the recheck.
- Every new or revised node fails on `4dd0af80~1` and passes on `4dd0af80`. That is the repro bar for qa-fix.
