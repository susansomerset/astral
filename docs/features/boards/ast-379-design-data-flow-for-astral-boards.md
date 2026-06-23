# AST-379 — Design data flow for Astral Boards

<!-- linear-archive: AST-379 archived 2026-06-15 -->

## Linear archive (AST-379)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-379/design-data-flow-for-astral-boards  
**Status at archive:** Done  
**Project:** Astral Boards  
**Assignee:** unassigned  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-383; related: AST-397; related: AST-389

### Description

## Purpose

Astral ingests jobs through two channels:

1. **Company-centric** — qualify a company, find its job page, scrape listings, consult pipeline.
2. **Board-centric** — candidate-defined **saved searches** on **adopted** external job boards where the employer is not known upfront.

This epic is the **architecture and functional definition** for the boards channel — not a spike and not single-board implementation. Spikes prove boards; production work follows the **implementation sequence** below.

**Repo docs:** `docs/features/boards/board-spike-phases.md`, `board-config-entry.schema.md`.

---

## Data model (resolved)

### Boards live in config only — no `board` table

* `BOARD_CONFIG` in `src/utils/config.py` — keyed by stable `board_key` (`a16z`, `gv`, `ycombinator`, `general-catalyst`, `heavybit`, …).
* Each entry: `label`, `entry_url`, `adopted`, `parse_instructions`, `search_criteria_schema`, `criteria_param_map`, `craft_task_key`, and `scrape_mode`: `deep_link` | `interactive`.
* Boards are **never** added through the UI (too site-specific). Engineers land entries after spike **Phase 4** ([AST-414](https://linear.app/astralcareermatch/issue/AST-414/spike-a16z-board-profile-phase-4-board-profile-draftjson-spike-only) pattern for a16z).
* `adopted: false` until Susan approves production use for that key.

### `board_search` table — UI-owned only

* Sibling concept to **company** in the candidate workflow: one row = one saved search for that candidate.
* `board_key` — validated against `BOARD_CONFIG` keys (enum / CHECK in app).
* `criteria` — JSON; shape defined by `TASK_CONFIG[craft_task_key]` for that board.
* Multiple `board_search` rows per candidate per board allowed.
* **Only** candidate/UI-mutable board data goes in the database.

### Per-board craft profile

* Each board in `BOARD_CONFIG` references a `craft_task_key` (e.g. `craft_board_search_a16z`).
* UI runs that craft task so the candidate defines search criteria; output is stored in `board_search.criteria`.
* Same pattern family as `craft_company_prefilter` → artifact criteria.

### Job provenance

* `job.board_search_id` — FK to the `board_search` that introduced the listing (when board-sourced).
* At ingest: `company` is **null** or sentinel `from_board` if the column is non-nullable.
* **Company resolution** (real employer row from JD) is **out of scope** for the first production slice — see implementation step 7.

---

## `gaze_board` (dispatch + gazer)

Periodic batch task (**same scheduling pattern** as `gaze_company` — `dispatch_tasks` row, no new scheduler abstraction).

**Claims** `board_search` **rows** (not boards globally). For each row:

1. Load `BOARD_CONFIG[board_key]` + row `criteria`.
2. **Pre-scrape (board-specific):**
   * `deep_link` — build URL from criteria / board template → `goto` → scrape.
   * `interactive` — Playwright applies `criteria_param_map` (widget ids from spike Phase 2), then Search → scrape. *Ship deep-link path first; add interactive per board when spikes require it.*
3. **Scrape → parse → ingest** — **same mechanical depth as** `gaze_company` **today** (no extra analysis in gazer: no qualify/evaluate/consult).
4. Call **board-aware ingest** (implementation step 4).

Playwright widget work for interactive boards lives in **gazer + playwright**, promoted from spike artifacts.

---

## Implementation sequence (production build order)

| Step | Work | Tickets |
| -- | -- | -- |
| **0** | Board spikes (Phases 1–4 per board) | [AST-397](https://linear.app/astralcareermatch/issue/AST-397/spike-a16z-board-search-job-shaped-json-playwright-anthropic) (400–402 Done), [AST-414](https://linear.app/astralcareermatch/issue/AST-414/spike-a16z-board-profile-phase-4-board-profile-draftjson-spike-only), AST-410–413 |
| **1** | `BOARD_CONFIG` + craft tasks in [config.py](<http://config.py>) | Spike Phase 4; [AST-403](https://linear.app/astralcareermatch/issue/AST-403/design-data-flow-for-astral-boards-adopted-board-catalog-and-research) |
| **2** | `board_search` table + API | [AST-404](https://linear.app/astralcareermatch/issue/AST-404/design-data-flow-for-astral-boards-candidate-board-links-and-saved) |
| **3** | `gaze_board` (scrape, parse, ingest; interactive when needed) | Fold [AST-405](https://linear.app/astralcareermatch/issue/AST-405/design-data-flow-for-astral-boards-board-search-scrape-driver) into gazer |
| **4** | Tracker ingest fork (`board_search_id`, dedup, `invalid_title`) | [AST-406](https://linear.app/astralcareermatch/issue/AST-406/design-data-flow-for-astral-boards-ingest-pipeline-dedup-title) |
| **5** | Verify `qualify_job_listings` | Verification manifest |
| **6** | Verify `evaluate_jd` | Verification manifest |
| **7** | Plan company resolution + consult parity | New plan ticket (not [AST-409](https://linear.app/astralcareermatch/issue/AST-409/design-data-flow-for-astral-boards-jd-evaluation-agency-gate-consult) as written) |

[AST-408](https://linear.app/astralcareermatch/issue/AST-408/design-data-flow-for-astral-boards-admin-catalog-and-candidate-saved) **(UI):** board picker from config, craft + `board_search` CRUD — after step 2 or parallel with seeded rows.

**Ingest fork (step 4):** before `save_job` — `source.company` → existing path; `source.board_search_id` → board path (placeholder company, candidate-wide dedup).

---

## Pipeline (full north star)

After `gaze_board` + ingest, jobs enter existing dispatch:

`NEW` → title patterns → `qualify_job_listings` → JD scrape → `evaluate_jd` → *(future: agency gate, company resolution)* → `consult_*` when employer is known.

Steps **5–6** prove qualify/evaluate on board jobs with placeholder company. Step **7** plans employer resolution before full consult parity.

### Per-run metrics (target)

`scraped`, `duplicates`, `invalid_title` (align rename with [AST-389](https://linear.app/astralcareermatch/issue/AST-389/save-valid-titles-to-new)), listing_qualified, jd_pass/fail, agency_rejected, handed_to_consult — exact storage TBD.

### Automation rules

* **Anonymous only** — no board-site login or stored credentials.
* **Research vs adopted** — `BOARD_CONFIG[].adopted` + spike queue ([AST-342](https://linear.app/astralcareermatch/issue/AST-342/investigate-for-boards)); no UI to add boards.

---

## Boundaries

* Not mega-boards (Indeed, LinkedIn) unless explicitly spiked and adopted.
* Not the Playwright spikes themselves.
* Not company roster flows (prefilter, locate job page).
* Not [AST-381](https://linear.app/astralcareermatch/issue/AST-381/pushing-database-content-to-github) / [AST-383](https://linear.app/astralcareermatch/issue/AST-383/corebootstrap-runtime-startup-orchestration-from-uiserverpy) DB export/bootstrap.
* Not artifact / application UI beyond board search setup.
* **Not** employer company creation in v1 build slice (step 7 plans it).
* **Not** consult handoff with resolved company until after step 7 plan is approved.

---

## Acceptance criteria

**v1 build slice (steps 1–6):**

 1. **Config catalog:** Operator can list adopted boards from `BOARD_CONFIG` (`adopted: true`); each has shared parse/scrape contract.
 2. **Saved search:** Candidate can have ≥2 `board_search` rows on the same board with different `criteria` (API/UI or seeded rows for UAT).
 3. **Gaze path:** `gaze_board` on a `board_search` produces jobs with `board_search_id` set and placeholder/null company.
 4. **Title validation:** With title patterns, non-matching listings are not inserted; run shows `invalid_title` > 0 when appropriate.
 5. **Title validation off:** No patterns → `invalid_title` = 0.
 6. **Dedup:** Duplicates increment logged count; no duplicate job rows (candidate-wide).
 7. **Qualify / evaluate:** Board-sourced jobs reach qualify and evaluate dispatch without bypassing state machine.
 8. **Anonymous only:** No board credentials required.
 9. **Run metrics:** Per board search run, stage counts including `invalid_title` are retrievable.
10. **Research vs adopted:** Non-adopted keys are not runnable in production gazer.

**Deferred (step 7+):** agency gate hardening, real `company_id`, full consult parity.

---

## Resolved decisions

1. **Dedup:** Candidate-wide; search-blob-with-known-job-id pattern. Title validation at ingest.
2. **Company at ingest:** `board_search_id` on job; `company` null or `from_board`. Real employer row after qualify/evaluate — future.
3. **Job identity before company:** Board listing URL/blob + `board_search` provenance.
4. **Title metrics:** Per-run `invalid_title` count only in v1.
5. **Dispatch:** `gaze_company` and `gaze_board` periodically.
6. **Multiple boards:** Each needs spike Phases 1–4 before config entry (AST-410–413).

---

## Related spikes

| board_key | Parent |
| -- | -- |
| `a16z` | [AST-397](https://linear.app/astralcareermatch/issue/AST-397/spike-a16z-board-search-job-shaped-json-playwright-anthropic) — Phase 4: [AST-414](https://linear.app/astralcareermatch/issue/AST-414/spike-a16z-board-profile-phase-4-board-profile-draftjson-spike-only) |
| `general-catalyst` | [AST-410](https://linear.app/astralcareermatch/issue/AST-410/spike-general-catalyst-jobs-board-profile-playwright-phased) |
| `gv` | [AST-411](https://linear.app/astralcareermatch/issue/AST-411/spike-gv-jobs-board-profile-playwright-phased) |
| `ycombinator` | [AST-412](https://linear.app/astralcareermatch/issue/AST-412/spike-y-combinator-jobs-board-profile-playwright-phased) |
| `heavybit` | [AST-413](https://linear.app/astralcareermatch/issue/AST-413/spike-heavybit-jobs-board-profile-playwright-phased) |

---

## Child tickets (rescope plans to this doc)

| ID | Role |
| -- | -- |
| 403 | `BOARD_CONFIG` block + read API |
| 404 | `board_search` table + craft wiring |
| 405 | Fold into `gaze_board` / playwright |
| 406 | Tracker ingest fork + metrics |
| 408 | Candidate UI |
| 409 | **Paused** — after step 7 plan |
| 407 | Canceled |

---

## Dependencies

* [AST-389](https://linear.app/astralcareermatch/issue/AST-389/save-valid-titles-to-new) — valid title patterns / `invalid_title` naming.
* Existing consult, tracker, dispatch.
* [AST-342](https://linear.app/astralcareermatch/issue/AST-342/investigate-for-boards) — research list input.

### Comments

#### chuckles — 2026-05-26T01:31:50.159Z
`origin/dev` @ `e3030e47` — boards epic landed (icebox). Engineers: merge into `dev-<agent>`:

```bash
git fetch origin && git checkout dev-<agent> && git merge origin/dev
```

(not rebase unless Susan directs)

— Chuckles

#### chuckles — 2026-05-25T04:30:18.513Z
**AST-487 landed** @ `e8104a75` — rolled to **`ftr/AST-379`** for UAT.

- Deeplink rows skip the interactive `NotImplementedError` gate
- Navigates stored `deeplink_url` directly
- Gaze failures now `_log.error` with board_search_id + message

Restart app on local **`dev`**, **Resume ACTIVE** on your search, re-run **`gaze_board`**. You should see either success (and `last_scan_at`) or a concrete error line in logs.

— Chuckles

#### chuckles — 2026-05-25T04:28:08.081Z
**UAT blocker — gaze_board → ERROR (blocks AST-482 validation)**

Susan's logs (`total_failed: 1`, `total_passed: 0`) mean **`run_board_search_gaze` raised** for that row — not "zero jobs found." Success with empty parse would be **`total_passed: 1`** with `new: 0`.

**Likely exception for your deeplink a16z search:**

```423:425:src/core/boards.py
    scrape_mode = profile.get("scrape_mode", "deep_link")
    if scrape_mode == "interactive":
        raise NotImplementedError("interactive gaze_board — follow-on after BOARD_CONFIG profiles")
```

Promoted **`BOARD_CONFIG`** entries (**a16z**, **heavybit**, **general-catalyst**) have **`scrape_mode: interactive`**. Gaze checks the **profile** before the **saved row**. Deeplink mode never gets a chance — **`NotImplementedError`** → **`process_gaze_board_batch`** **`except`** → **`state=ERROR`**. No **`last_scan_at`** bump (**AST-482** success-only path).

**Gap:** AST-459 deeplink branch (`search_mode` → stored URL) is **not** in current `boards.py` on **`ftr/379`** — always navigates `entry_url` + criteria params.

**Logging gap:** failure **`except`** does not **`_log.error`** the exception — DEBUG on dispatch doesn't show why gaze failed.

**Dispatching AST-484** (Hedy): deeplink bypasses interactive gate + restore deeplink navigation + gaze error logging.

— Chuckles

#### susan — 2026-05-25T04:26:24.113Z
Still getting this issue on gaze_board:

\[2026-05-25 04:21:57\] INFO dispatch.scheduler: Dispatching gaze_board — 1 available, batch gaze_board-88b11520-370b-45b0-96e7-6d80911a8fa3

\[2026-05-25 04:21:57\] INFO src.core.dispatcher: \[DEBUG\] \_run_task: running 'gaze_board' batch_size=5 batch_id=gaze_board-88b11520-370b-45b0-96e7-6d80911a8fa3...

\[2026-05-25 04:21:57\] INFO src.core.dispatcher: \[DEBUG\] \_run_unified\[board_search/ACTIVE\]: claimed 1 entities (batch=gaze_board-88b11520-370b-45b0-96e7-6d80911a8fa3)

\[2026-05-25 04:21:57\] INFO src.core.dispatcher: \[DEBUG\] \_run_task: runner returned summary={'total_processed': 1, 'total_passed': 0, 'total_failed': 1, 'total_errors': 0}

\[2026-05-25 04:21:57\] INFO dispatch.scheduler: Loop mode gaze_board: 0 remaining — stopping after 1 run(s)

With DEBUG flagged ON, there's no additional detail showing in the actual gaze_board function itself.  We need a LOT more visibility on this function to see if it's actually opening the page and finding the container and any matches, paginating, etc., as gaze does for company job boards.

#### hedy — 2026-05-25T04:11:17.743Z
[check-linear]

- **§0a** (`astral-hedy` / `dev-hedy`): `git fetch` → `checkout dev-hedy` → `git merge origin/dev` — **already up to date**.
- **Session scope:** `assigned issue ids` was **none** → no `[check-linear]` §3 publish / merge toward **`origin/sub/AST-472/…`** or other refs; Ada owns **AST-483** per Chuckles dispatch.
- **Susan’s gaze_board summary question:** In `run_consult_task` → `process_gaze_board_batch`, **`total_processed` / `total_passed` / `total_failed` count `board_search` rows**, not job listings.
  - **`total_failed: 1` with `total_passed: 0`** for one row ⇒ that gaze **raised** before success (validation, connectivity, Playwright scrape, parse template, ingest, etc.) → row **`state`** should be **ERROR**; check traceback lines **above** the dispatcher summary.
  - Contrast: **`total_passed: 1`** means the row finished without exception — **zero new jobs ingested** can still happen (empty parse, title gate, dup-only) **without** incrementing **`total_failed`**.
- **Where to confirm:** `board_search.state`, **`last_scan_at`** only on success path (**AST-482**), and full error message in logs for failed runs.

#### chuckles — 2026-05-25T04:07:49.199Z
## do-all-the-things — AST-482 run complete

**Parent:** AST-379
**New child:** AST-482 — Board search `last_scan_at` gaze cadence

| Ticket | Status | Assignee |
|--------|--------|----------|
| **AST-482** | User Testing | Hedy |
| AST-457 | PR Ready | Katherine |
| (other 379 children) | User Testing | various |

### Completed path
- Sub-dispatch → **Hedy**
- Plan Ready → Plan Approved (Chuckles validate)
- Code Complete → Tests Ready (Betty manifest) → Tests Passed → Review Posted (Radia, 0 fix-now) → User Testing
- **rollup-child:** `sub/AST-379/AST-482-…` → `ftr/AST-379-design-data-flow-for-astral-boards` @ **`b3211bdd`**

### What shipped
- `board_search.last_scan_at` column + migration
- `BOARDS_CONFIG.gaze_board.scan_interval_hours` (24h, mirror WATCH)
- Claim + `count_eligible` staleness filter; `gaze_board` sorts by `last_scan_at`
- Success-only bump in `process_gaze_board_batch`
- Tests + bible **§7.13za**

### prep-uat
- Parent already **User Testing**; **AST-482** rolled into **`ftr/379`** incrementally
- Local **`dev`** merged **`origin/ftr/AST-379-design-data-flow-for-astral-boards`** for your restart
- **`sub/AST-379/AST-482-…`** kept until full parent finish-up

### Susan UAT (AST-482)
1. Restart app on local **`dev`** (or pull **`ftr/379`** tip)
2. Run **`gaze_board`** twice within 24h on same ACTIVE search — second run should **not** claim it
3. After successful gaze, row should have **`last_scan_at`** set

— Chuckles

#### chuckles — 2026-05-25T03:49:41.824Z
## Sub-dispatch — AST-482 (UAT follow-up)

Susan flagged **`gaze_board`** re-gazing the same ACTIVE search every tick. Company **`gaze`** already throttles via **`company.last_scan_at`**; **`board_search`** never got the same column.

| Ticket | Title | Assigned to | Branch | Blocked by |
|--------|-------|-------------|--------|------------|
| **AST-482** | Board search last_scan_at gaze cadence | Hedy | `sub/AST-379/AST-482-board-search-last-scan-at-gaze-cadence` | — |

**Rationale:** Hedy owns **`gazer.py`**, **`database.claim_board_search_batch`**, boards dispatch — same domain as **AST-418** / **AST-459**.

**Git:** Child branched from **`origin/ftr/AST-379-design-data-flow-for-astral-boards`** @ `e8007424` (includes BOARD_CONFIG fix). Parent **`ftr/AST-379-design-data-flow-for-astral-boards`** unchanged.

Running **`do-all-the-things`** scoped to **AST-482** only (sibling children already User Testing).

— Chuckles

#### chuckles — 2026-05-25T03:44:30.296Z
**UAT bug — blank board picker + resume ACTIVE fails on deeplink**

**Root cause:** AST-471 merge left **two** `BOARD_CONFIG` blocks in `config.py`. Python kept the **second** one: `BOARD_CONFIG = {}`, which overwrote the spike-promoted profiles (`a16z`, `heavybit`, `general-catalyst`).

**Symptoms:**
- `GET /api/boards` → `[]` → edit modal board `<select>` empty (only "Select board…").
- Saved rows still show `board_key: a16z` in the list (from DB).
- **Resume ACTIVE** on a **deeplink** row PATCHes `{state: ACTIVE}` but `update_board_search` still re-runs deeplink domain validation → `_board_entry_url_for_domain` → `validate_board_key_adopted('a16z')` → error.

**Fix:** removed duplicate empty block + duplicate helpers. Pushed to `origin/ftr/AST-379-design-data-flow-for-astral-boards`.

Restart app after pulling/merging ftr tip onto local `dev`.

— Chuckles

#### susan — 2026-05-25T03:39:02.927Z
debug log from running board_search:

\[2026-05-25 03:37:41\] INFO dispatch.scheduler: Dispatching gaze_board — 1 available, batch gaze_board-cea4c66c-2444-472f-a1ca-be456cdaac82

\[2026-05-25 03:37:41\] INFO src.core.dispatcher: \[DEBUG\] \_run_task: running 'gaze_board' batch_size=5 batch_id=gaze_board-cea4c66c-2444-472f-a1ca-be456cdaac82...

\[2026-05-25 03:37:41\] INFO src.core.dispatcher: \[DEBUG\] \_run_unified\[board_search/ACTIVE\]: claimed 1 entities (batch=gaze_board-cea4c66c-2444-472f-a1ca-be456cdaac82)

\[2026-05-25 03:37:41\] INFO src.core.dispatcher: \[DEBUG\] \_run_task: runner returned summary={'total_processed': 1, 'total_passed': 0, 'total_failed': 1, 'total_errors': 0}

\[2026-05-25 03:37:41\] INFO dispatch.scheduler: Loop mode gaze_board: 0 remaining — stopping after 1 run(s)

It's not clear if any jobs were found in the search but they should have been given the generosity of the filter.  What was the expected outcome of gaze_board based on the code?

#### chuckles — 2026-05-25T02:46:06.376Z
**Stale `sub/AST-379/*` cleanup** — @susan requested.

Deleted from origin (superseded by AST-471 on `ftr/AST-379-design-data-flow-for-astral-boards` @ `582c784c`):

- `sub/AST-379/AST-419-design-data-flow-for-astral-boards-verify-qualify-and-evaluate-for`
- `sub/AST-379/AST-457-manage-candidate-board-searches`
- `sub/AST-379/AST-458-design-data-flow-for-astral-boards-board-search-enabled-deeplink-mode`
- `sub/AST-379/AST-459-design-data-flow-for-astral-boards-gaze-board-enabled-flag-and-user-deeplink-urls`

No `sub/AST-379/*` refs remain on origin.

— Chuckles

#### chuckles — 2026-05-25T02:42:13.980Z
## prep-uat AST-379 — partial (sub merge blocked)

**Gate A:** All non-cancelled children rollup-safe (457 + 471 at **PR Ready**; others **User Testing**). ✅

**Child `sub/*` merges:** **Blocked** on first merge (**AST-458**). Stale publish tips still use pre-**AST-471** `enabled`/`status` model; **`origin/ftr/AST-379-design-data-flow-for-astral-boards`** already includes **AST-471** (`board_search.state` ACTIVE|INACTIVE|ERROR) @ `582c784c`.

**Conflict files (458 → ftr):**
- `docs/ASTRAL_TEST_BIBLE.md`
- `docs/features/boards/ast-416-…`, `ast-418-…`, `ast-459-…`
- `src/core/boards.py`, `consult.py`, `dispatcher.py`, `gazer.py`, `tracker.py`
- `src/data/database.py`, `src/ui/api/api_boards.py`
- `src/ui/frontend/src/pages/AdminTaskPrompts.tsx`
- `tests/component/core/test_*.py`, `test_board_search_integration.py`

**Did not merge:** AST-458, AST-459, AST-419, AST-457 subs (458 blocked; 457/459/419 would hit same divergence).

**Did not delete** any `sub/*` (merge incomplete per skill).

**Current rollup (authoritative):** `origin/ftr/AST-379-design-data-flow-for-astral-boards` @ `582c784c`
- Includes: AST-471 state model, BOARD_CONFIG spike promotion (`ee372bd7`), AST-457 nav + tests (`f7fcc0b5`), prior prep-uat children.

**§6 tests:** `./scripts/testing/run_component_tests.sh` on ftr tip — **green** (208 frontend + python suite passed).

**§8 local `dev`:** ftr tip is already an **ancestor** of local `dev` (merged via `a92fba6c`). Your `dev` also has **AST-376** commits ahead of ftr — expected if you're UAT-ing multiple epics on one branch.

### @susan — to finish rollup hygiene
1. **Do not** blind-merge stale `sub/AST-379/AST-458|459|457|419` — superseded by AST-471 on ftr.
2. When satisfied, delete stale subs: `458`, `459`, `457`, `419` (and confirm `471` sub already gone).
3. Re-run prep-uat only if new child work lands on fresh `sub/*` tips.

## Manual test steps (current ftr / dev with AST-379 content)

1. Restart app on local `dev`.
2. **Nav:** Candidate → **Board Searches** (not Title Patterns in sidebar).
3. **Board picker:** a16z, Heavybit, General Catalyst from `BOARD_CONFIG`.
4. **Create search (criteria):** save with JSON criteria; list shows label/board/dates only.
5. **State toggle:** ACTIVE ↔ INACTIVE (not legacy enabled boolean) — verify inactive excluded from gaze claim.
6. **Deeplink mode:** URL must match board entry domain; duplicate normalized URL rejected.
7. **API smoke:** `GET /api/boards`, `GET /api/boards/searches?candidate_id=…`
8. **Gaze (optional):** run `gaze_board` dispatch on ACTIVE search; jobs get `board_search_id`.
9. **Deferred:** AST-470 criteria pre-fill (Backlog).

— Chuckles

#### chuckles — 2026-05-24T04:06:17.920Z
## Incremental UAT — AST-471 rolled up

**Child merged:** [AST-471](https://linear.app/astralcareermatch/issue/AST-471) — `board_search.state` (`ACTIVE` | `INACTIVE` | `ERROR`) replaces `enabled` + batch `status`; §2.4 claim parity; `gaze_board` in dispatch seed.

**Parent branch:** `origin/ftr/AST-379-design-data-flow-for-astral-boards` @ **`582c784c`**

**Local `dev`:** merged @ **`a92fba6c`** (prep-uat §8). Restart the app if running.

**Deleted:** `origin/sub/AST-379/AST-471-board-search-replace-enabledstatus-with-state`

**Merge notes:** Resolved `config.py` (promoted `BOARD_CONFIG` + AST-466 consult shim + `BOARD_SEARCH_STATES`) and UI tests; `TestAdoptedBoardHelpers` updated for non-empty registry.

---

## Manual test steps — AST-471 delta (state model)

**Supersedes** prior UAT steps that reference `enabled` / batch `status` for board searches.

1. **Admin → Scheduled Actions / dispatch task keys** — **`gaze_board`** appears in task dropdown (seed from `_DISPATCH_TASK_SEED`).
2. **Board Searches UI** — toggle uses **workflow state** (`ACTIVE` / `INACTIVE`), not a boolean `enabled`. New search defaults **ACTIVE**; **Paused** → `INACTIVE`.
3. **ERROR recovery** — if a search shows **ERROR** (failed gaze), **Resume ACTIVE** PATCH sets `state=ACTIVE`.
4. **API** — `POST/PATCH /api/boards/searches` accepts **`state`**; rejects legacy **`enabled`** field.
5. **Gaze claim** — only **`state=ACTIVE`** rows with clear `batch_id` are claimed; **`INACTIVE`** and **`ERROR`** skipped.
6. **Clear semantics** — after gaze batch, only **`batch_id`** cleared (state unchanged until gazer success/failure).
7. Re-run prior gaze + ingest steps (415–419) unchanged except state vocabulary above.

If testing fails on `dev`:
  `git reset --hard origin/dev`

— Chuckles

#### hedy — 2026-05-24T02:53:24.484Z
[check-linear]

- **§0a** (`astral-hedy` / `dev-hedy`): `git fetch` → `git merge origin/dev` — **already up to date**; `origin/dev` is ancestor of HEAD (`origin/dev` @ `952f0e56`).
- **§0b:** `@hedy` team + **Astral Boards** search → **55** issue ids unioned; **`list_comments`** on assignee backlog (**416**, **417**, **418**, **458**, **459**, **421**, **469**) + parent **AST-379** / **AST-373** baselines.
- **Actionable threads:** **none** — no non-Hedy comment after my latest `[check-linear]` that `@hedy`’s me or expects a reply (Chuckles **UAT Ready** / **finish-up** notes are broadcast; **AST-469** resolve already posted on child).
- **§6:** Not running pipeline skills from this pass.

#### chuckles — 2026-05-24T01:32:34.179Z
**Post-UAT fix — AST-457 nav gap**

Prep-uat cherry-picked 457 UI commits but missed `NAV_CONFIG` (sidebar still showed Title Patterns) and 457 test files.

**Fixed:** `NAV_CONFIG` → Board Searches; added `test_CandidateBoardSearches.test.tsx` + `TestBoardRegistryAst457`.

- `ftr/AST-379-design-data-flow-for-astral-boards` @ `f7fcc0b5`
- local `dev` @ `b76169c6` (not pushed to origin/dev)

Restart app — Candidate sidebar should show **Board Searches**.

— Chuckles

#### chuckles — 2026-05-24T01:11:09.009Z
## UAT Ready — Chuckles

All **9** child branches integrated into parent branch; **9** `sub/AST-379/*` branches deleted from origin.

Parent branch: `origin/ftr/AST-379-design-data-flow-for-astral-boards` @ `84dfddd9`

**Pre-prep:** AST-415/416 `api_boards.py` add/add conflict resolved (catalog + searches in one module). AST-458/457/459 integrated from published `ftr/*` tips (stale `sub/*` branches were plan-only or behind).

Merged in order:
  1. **AST-415** — BOARD_CONFIG + read API (`sub/…/AST-415-…` — deleted)
  2. **AST-416** — board_search table + CRUD API (`sub/…/AST-416-…` — deleted)
  3. **AST-458** — enabled flag, deeplink mode, duplicate validation (`ftr/AST-458` commits cherry-picked; `sub/…/AST-458-…` — deleted)
  4. **AST-417** — board ingest fork, invalid_title, board_search_run (`sub/…/AST-417-…` — deleted)
  5. **AST-418** — gaze_board dispatch + gazer batch (`sub/…/AST-418-…` — deleted)
  6. **AST-459** — gaze honors enabled + deeplink URLs (`ftr/AST-459` commits cherry-picked; `sub/…/AST-459-…` — deleted)
  7. **AST-457** — Board Searches UI + nav (`ftr/AST-457` UI/fix commits cherry-picked; `sub/…/AST-457-…` — deleted)
  8. **AST-419** — qualify/evaluate verification tests (`sub/…/AST-419-…` — deleted)
  9. **AST-421** — company resolution architecture plan (`sub/…/AST-421-…` — deleted)

Local `dev` merged (prep-uat §8) @ `5ecb689d`. Restart the app if it is running, then test.

**Engineers — after Susan runs finish-up and pushes `origin/dev`:** merge **`origin/dev`** into your integration branch: `git fetch origin && git checkout dev-<agent> && git merge origin/dev` — do **not** rebase **`origin/dev`** onto **`dev-<agent>`** unless Susan directs.

## Manual test steps

**Prerequisites:** App restarted on local `dev`. Select a candidate with title patterns configured (Profile → Title Patterns still on Candidate Profile). At least one `BOARD_CONFIG` entry with `adopted: true` (engineer may need to seed `a16z` from spike AST-414).

### AST-415 — Board catalog
1. `GET /api/boards` (auth) — returns only adopted boards.
2. `GET /api/boards/{board_key}` — full config for an adopted key; 404 for non-adopted or unknown keys.

### AST-416 + AST-458 — Saved searches API
3. `POST /api/boards/searches` — create a search with label, board_key, criteria; 201 response.
4. Create a **second** search on the **same board** with different criteria — both persist.
5. `POST` with duplicate normalized criteria or deeplink — **409** duplicate error.
6. `POST` with `mode: deeplink` + valid `deeplink_url` (domain matches board `entry_url`) — saves; wrong domain — **400**.
7. `PATCH` to set `enabled: false` — row persists but is disabled for gaze.

### AST-457 — Board Searches UI
8. Sidebar: **Board Searches** under Candidate; no standalone **Title Patterns** nav item.
9. Open Board Searches with candidate selected — list shows label, board name, created/updated only.
10. Create/edit searches via UI — criteria mode and deeplink mode (confirm before mode switch clears other field).
11. Toggle **enabled** off — search remains visible; verify it is skipped on next gaze (step 13).

### AST-417 + AST-418 + AST-459 — Gaze + ingest
12. Trigger `gaze_board` (scheduled action or manual dispatch) for an **enabled** search with criteria.
13. Confirm jobs appear with `board_search_id` set and placeholder `__board__{board_key}` company.
14. With title patterns active, re-run with a listing that fails patterns — run metrics show `invalid_title` > 0; no duplicate job rows on re-ingest.
15. Deeplink-mode search: gaze navigates stored URL (not synthesized query params).
16. Disabled search: not claimed by gaze batch.

### AST-419 — Qualify / evaluate (verification)
17. Board-sourced jobs in `NEW` reach `qualify_job_listings` and `evaluate_jd` dispatch (component test `test_board_sourced_qualify_evaluate.py` green, or observe dispatch ledger).

### AST-421 — Architecture plan (docs-only)
18. Read `docs/features/boards/ast-421-design-data-flow-for-astral-boards-plan-company-resolution-and-consult-parity.md` — sign off on step 7 design before follow-on build dispatch.

**Deferred (out of v1 UAT scope):** real employer resolution, consult handoff with resolved company (AST-421 build slices not dispatched).

If testing fails on `dev`:
  `git reset --hard origin/dev`

— Chuckles

#### chuckles — 2026-05-24T00:50:42.030Z
prep-uat merge conflict — child branch **AST-416** conflicts with the parent branch after merging **AST-415**.

Conflict is in:
- `src/ui/api/api_boards.py`
- `tests/component/ui/api/test_api_boards.py`

Both branches added the same files (add/add). **AST-415** landed on `origin/ftr/AST-379-design-data-flow-for-astral-boards`; remaining children (**416–421, 457–459**) were **not** merged.

@susan — please resolve and push to `origin/ftr/AST-379-design-data-flow-for-astral-boards`, then re-run prep-uat (remaining merges start at AST-416) or merge the remaining children manually.

— Chuckles

#### chuckles — 2026-05-24T00:46:24.280Z
**AST-421** → **User Testing** (assignee **Hedy** unchanged). Plan-only step 7 — Susan UAT is the architecture plan doc, not product code. Clears the **AST-379** prep-uat sibling gate with the other children.

— Chuckles

#### chuckles — 2026-05-24T00:33:51.991Z
## do-all-the-things — resume run complete

**Parent:** AST-379

### This session (after local unblock)
- **AST-458:** Tests Ready → Tests Passed → Review Posted → **User Testing** (`origin/ftr/AST-458` @ `ce9701cd`)
- **AST-457:** Tests Ready → Tests Passed → Review Posted → **User Testing** (`origin/ftr/AST-457` @ `c0f0ddcf`)
- **AST-459:** unchanged **User Testing** (completed prior run)
- Betty qa-handoff loops cleared AST-455 test drift + coverage gates on 457/458

### Children snapshot
| ID | Status | Assignee |
|----|--------|----------|
| 415 | User Testing | Ada |
| 416 | User Testing | Hedy |
| 417 | User Testing | Hedy |
| 418 | User Testing | Hedy |
| 457 | User Testing | Katherine |
| 458 | User Testing | Hedy |
| 459 | User Testing | Hedy |
| 419 | Review Posted | Betty |
| 421 | Todo | Chuckles |

### Stalled / needs Susan
- **prep-uat:** blocked on **AST-419** (Review Posted) and **AST-421** (Todo). Product slice is UAT-ready; rollup waits on verification + deferred plan ticket disposition.
- **AST-421:** cancel or move out of parent if step-7 plan is intentionally deferred past this UAT rollup.
- **AST-419:** Betty finish resolve → User Testing (or cancel if verification absorbed elsewhere).

### prep-uat
- **Failed** (gate) — blocking comment posted

— Chuckles

#### chuckles — 2026-05-24T00:33:48.002Z
prep-uat blocked — not all children are rollup-safe.

Still in flight:
- **AST-419** — Review Posted — Betty (qualify/evaluate verification)
- **AST-421** — Todo — Chuckles (company resolution plan — deferred step 7)

All product children (415–418, 457–459) are **User Testing**. Cannot merge until siblings above are User Testing, Done, PR Ready, or canceled.

— Chuckles

#### chuckles — 2026-05-24T00:31:57.872Z
## do-all-the-things — run complete

**Parent:** AST-379
**Children:**
- AST-415 — User Testing — Ada
- AST-416 — User Testing — Hedy
- AST-417 — User Testing — Hedy
- AST-418 — User Testing — Hedy
- AST-458 — User Testing — Hedy
- AST-459 — User Testing — Hedy
- AST-419 — Review Posted — Betty
- AST-457 — Review Posted — Katherine
- AST-421 — Todo — Chuckles
- AST-420 — Canceled — Katherine

### Completed path
- **Dispatch:** skipped (parent already In Progress with children)
- **Earlier stages (plan/build/qa):** no new work — six children already at User Testing from prior runs
- **test-astral:** Katherine → AST-457 Tests Passed; aligned `origin/sub/AST-379/AST-457-…` with `origin/ftr/AST-457` @ e8d4d4de
- **review-astral:** Radia → AST-419 Review Posted (fix-now: verification tests need board stack on integrated line, not orphan ftr tip vs origin/dev); Radia → AST-457 Review Posted (4 fix-now)

### Stalled / needs Susan
- **AST-419:** Review Posted — Betty resolve or `[qa-handoff]`; tests fail collection on origin/dev without 415–418 product code merged
- **AST-457:** Review Posted — Katherine **resolve-astral** for adopted validation, JSON parse, loadBoards error handling, board_search_id through ingest
- **AST-421:** Todo — step 7 plan (company resolution); definition approved; needs plan-astral assignee (engineer, not Chuckles long-term)
- **prep-uat:** blocked until 419 + 457 reach User Testing (421 may stay Todo/out of rollup per step 7 scope — confirm whether to exclude from prep-uat gate)

### prep-uat
- **Failed** — 419 and 457 not User Testing; 421 still Todo

### After finish-up (Susan)
- Engineers **rebase** `dev-<agent>` onto `origin/dev` per **orientation-astral § Rebase integration line** — **not** `git merge origin/dev`

— Chuckles

#### chuckles — 2026-05-24T00:31:49.119Z
prep-uat blocked — not all children rollup-safe.

Still in flight:
- **AST-419** — Review Posted (Betty) — Radia fix-now: tests target board APIs not on origin/dev baseline; needs integrated replay
- **AST-457** — Review Posted (Katherine) — 4 fix-now items (adopted validation, JSON parse, loadBoards errors, board_search_id in ingest)
- **AST-421** — Todo (Chuckles) — step 7 plan ticket; not build scope for v1 UAT rollup

User Testing (rollup-ready): AST-415, 416, 417, 418, 458, 459

Cannot merge child branches until every sibling is User Testing, Done, PR Ready, or canceled.

— Chuckles

#### chuckles — 2026-05-23T22:02:24.524Z
## do-all-the-things — run complete

**Parent:** AST-379
**Children:**
- AST-415 — User Testing — Ada
- AST-416 — User Testing — Hedy
- AST-417 — User Testing — Hedy
- AST-418 — User Testing — Hedy
- AST-419 — Todo — Betty
- AST-457 — Plan Approved — Katherine
- AST-458 — Tests Ready — Hedy
- AST-459 — User Testing — Hedy
- AST-420 — Canceled — Katherine
- AST-421 — Backlog — Chuckles

### Completed path
- **Dispatch:** skipped (parent already In Progress with children)
- **plan-astral:** Hedy → AST-458/459 Plan Ready; Katherine → AST-457 Plan Ready
- **validate-plan:** AST-457, 458, 459 → Plan Approved
- **build-astral:** Hedy → AST-458/459 Code Complete; Katherine → AST-457 blocked (dev-kath lacks boards API/table from 415/416/458)
- **qa-astral:** Betty → AST-458/459 manifests on `origin/ftr/*`; AST-419 refused (Todo, not Code Complete)
- **test-astral:** Hedy → AST-459 Tests Passed; AST-458 pytest 866/866 green but script exit 1 on LOCKED_AT_100 coverage gate (candidate.py, agent.py, api_admin.py)
- **review-astral:** Radia → AST-459 Review Posted (0 fix-now)
- **resolve-astral:** Hedy → AST-459 User Testing
- **check-linear:** Ada dev-ada rebase conflict on ast-438 doc persists; Kath dev-kath rebased onto origin/dev

### Stalled / needs Susan
- **AST-457:** Plan Approved — build preflight: merge boards stack (415/416/458 minimum) into integration line before Katherine can implement UI
- **AST-458:** Tests Ready — Betty: reconcile LOCKED_AT_100 branch coverage or adjust gate; then Hedy retest → Radia → resolve
- **AST-419:** Todo — verification work not started; Betty qa blocked until Code Complete
- **dev-ada:** rebase conflict `docs/features/administrator/ast-438-production-readiness-admin-prompt-and-rubric-diagnostic.md` — manual merge before Ada aligns with origin/dev
- **Linear MCP:** engineer agents report `save_issue` assignee updates failing intermittently (JSON/create-without-title error)

### prep-uat
- **Failed** — siblings AST-457 (Plan Approved), AST-458 (Tests Ready), AST-419 (Todo) not rollup-safe; blocking comment posted

— Chuckles

#### chuckles — 2026-05-23T22:02:19.423Z
prep-uat blocked — not all children are rollup-safe.

Still in flight:
- **AST-457** — Plan Approved — Katherine (build blocked: boards stack not on dev-kath)
- **AST-458** — Tests Ready — Hedy (pytest green; `run_component_tests.sh` exits 1 on LOCKED_AT_100 branch coverage — `[qa-handoff]` to Betty)
- **AST-419** — Todo — Betty (verification ticket; no Code Complete yet)

Cannot merge until every sibling is User Testing, Done, PR Ready, or canceled.

— Chuckles

#### ada — 2026-05-23T21:24:29.095Z
[check-linear]

- **§0a — blocked:** On `astral-ada`, `git rebase origin/dev` on `dev-ada` hit an add/add conflict replaying `docs/features/administrator/ast-438-production-readiness-admin-prompt-and-rubric-diagnostic.md` (`3ee9e102`). Rebase aborted; `dev-ada` still diverges from `origin/dev` (needs a human integration pass before this tree matches §6 “synced” wording).
- **§0b–§2 (full pass):** `mention-issue-ids` = **33** issues from `list_issues` **`query: "@ada"`** + **Team Astral**, `includeArchived: true` (unioned with project-scoped **`@ada`** query for **Astral Boards** — same id set). **`list_comments`** on **all 33** plus explicit **AST-458** / **AST-459** threads under parent **AST-379**.
- **Actionable for Ada:** **None** — no non-me comment with **`@ada`** or a direct Ada question that is still open **after** my latest `[check-linear]` / Ada reply pattern on those issues (e.g. **AST-458** `[qa-handoff]` is **`@Betty White`** → **qa-astral**, not Ada execution here).
- **§1 add-on:** `list_issues` **`assignee`** filter returns invalid JSON from this MCP host (unquoted value bug). Surrogate **Astral Boards + Ada** from subtree listing remains **AST-415** (**User Testing**). Session note **assigned issue ids: (none)** taken as “no pre-seeded subset,” not “skip §0b.”
- **Hygiene:** Removed duplicate `[check-linear]` at **2026-05-23T21:22Z**; this comment is canonical for the second pass.

#### chuckles — 2026-05-23T20:34:38.098Z
Delta child tickets created from **AST-457** consolidation:

- **AST-458** (Hedy, Todo) — `board_search` enabled flag, deeplink mode, normalized dup validation, domain check. Blocked by **AST-416**.
- **AST-459** (Hedy, Todo) — `gaze_board` honors enabled + user deeplink URLs. Blocked by **AST-418**, **AST-458**.
- **AST-457** parented here; assigned Katherine; replaces **AST-420** (canceled).

— Chuckles

#### chuckles — 2026-05-19T16:12:02.059Z
## prep-uat batch — blocked — Chuckles

Not all children are at **User Testing** or **Done**.

Still in flight:
- **AST-417** — Review Posted (Hedy)
- **AST-415** — Todo (Ada)
- **AST-419** — Todo (Betty)
- **AST-420** — Plan Approved (Kath)
- **AST-421** — Backlog

Ready for rollup when merged:
- **AST-416** — User Testing
- **AST-418** — User Testing

Cannot merge child branches into `origin/ftr/AST-379-design-data-flow-for-astral-boards` until the gate clears (or Susan overrides in chat).

— Chuckles

#### hedy — 2026-05-18T23:32:05.294Z
[check-linear]
- **resolve-astral:** AST-416 → User Testing (`f33b9e75`); AST-418 → User Testing (`8b72f1e3`); AST-417 stays Review Posted — `[qa-handoff]` for Betty (`test_tracker` → `invalid_title`).
- **dev-hedy:** `git merge origin/dev` OK; `git rebase origin/dev` still conflicts replaying stacked history (AST-302 era) — not blocking publish; `merge-base --is-ancestor origin/dev HEAD` true.
- **Pipeline:** no Tests Ready / Plan Approved / Todo for Hedy on Astral Boards.

#### chuckles — 2026-05-17T15:07:20.305Z
## Dispatch — Chuckles (re-dispatch 2026-05-17)

Susan requested cancel of pre-architecture children (**AST-403–406, 408–409**; **407** was already canceled) and fresh dispatch from the updated **AST-379** definition.

### Canceled (superseded)

AST-403, AST-404, AST-405, AST-406, AST-408, AST-409 — plans on old `ftr/*` branches are obsolete; use new tickets below.

### New children (v1 slice + plan)

| Ticket | Title | Assigned | Branch | Blocked by |
|--------|-------|----------|--------|------------|
| AST-415 | BOARD_CONFIG + boards read API | Ada | ftr/AST-415 | — |
| AST-416 | board_search table, craft, API | Hedy | ftr/AST-416 | AST-415 |
| AST-417 | Board ingest fork | Hedy | ftr/AST-417 | AST-416 |
| AST-418 | gaze_board dispatch + gazer | Hedy | ftr/AST-418 | AST-415, 416, 417 |
| AST-419 | Verify qualify + evaluate | Betty | ftr/AST-419 | AST-417, 418 |
| AST-420 | Candidate board_search UI | Katherine | ftr/AST-420 | AST-416 |
| AST-421 | Plan company resolution (backlog) | Chuckles | ftr/AST-421 | AST-419 |

**Assignment rationale:**
- **Ada:** `BOARD_CONFIG` + read API in config/utils.
- **Hedy:** DB, tracker ingest fork, gazer/dispatch (`gaze_board`).
- **Betty:** verification manifest (qualify/evaluate on board jobs).
- **Katherine:** candidate UI (no admin board CRUD).
- **Chuckles:** step 7 plan only (**AST-421**).

**Upstream spikes (unchanged):** AST-397/414 (a16z), AST-410–413. Phase 4 config can land before or with **AST-415** — coordinate in plans.

**Git (authoritative):** Parent `origin/ftr/AST-379`; children `origin/ftr/AST-415` … `421`. Ignore Linear `gitBranchName`.

— Chuckles

#### chuckles — 2026-05-17T15:03:21.845Z
**Description rewritten** (2026-05-17) — architecture pass from today's thread:

* `BOARD_CONFIG` only (no board table); `board_search` in DB; per-board craft
* `gaze_board` = same scrape/parse/ingest as company + optional widget pre-scrape (`deep_link` vs `interactive`)
* Implementation steps 0–7; **409 paused** until company-resolution plan
* v1 AC = steps 1–6; consult/employer deferred

Child plans should align to the **Child tickets** table in the description before build.

— Chuckles

#### chuckles — 2026-05-17T14:11:05.564Z
**Metric naming:** Run counter / column header is **`invalid_title`** (aligns with job state **`INVALID_TITLE`**), not `title_rejected` or `title_mismatch`. Same title-pattern semantics as [AST-389](https://linear.app/astralcareermatch/issue/AST-389). Gazer scan may still say `title_mismatch` until renamed in code.

— Chuckles

#### chuckles — 2026-05-17T14:04:22.097Z
## Child tickets reconciled to updated definition (2026-05-17)

Reviewed parent **Open questions** answers vs dispatched children from the premature dispatch.

| Ticket | Action |
|--------|--------|
| **AST-403**–**405**, **408** | Appended **§ Parent definition updates** — plan revisions only |
| **AST-406** | Appended dedup scope, title gate inline, `board_search` FK / `from_board`, narrowed title audit |
| **AST-407** | **Canceled** — assumed full company resolution |
| **AST-409** | **New** — JD eval, agency gate, consult handoff with placeholder company (blocks on **406**) |

**Hedy:** Refresh plans on **403–406** and **409**; treat **407** plan as obsolete.

— Chuckles

#### chuckles — 2026-05-16T23:37:52.821Z
## Dispatch — Chuckles

Dispatched **6** child tickets from the approved definition on [AST-379](https://linear.app/astralcareermatch/issue/AST-379/design-data-flow-for-astral-boards).

| Ticket | Title | Assigned to | Branch | Blocked by |
|--------|-------|-------------|--------|------------|
| [AST-403](https://linear.app/astralcareermatch/issue/AST-403) | Adopted board catalog and research list | Hedy | `ftr/AST-403` | — |
| [AST-404](https://linear.app/astralcareermatch/issue/AST-404) | Candidate board links and saved searches | Hedy | `ftr/AST-404` | AST-403 |
| [AST-405](https://linear.app/astralcareermatch/issue/AST-405) | Board search scrape driver | Hedy | `ftr/AST-405` | AST-403 |
| [AST-406](https://linear.app/astralcareermatch/issue/AST-406) | Ingest pipeline — dedup, title gate, metrics | Hedy | `ftr/AST-406` | AST-403, AST-404, AST-405, AST-389 |
| [AST-407](https://linear.app/astralcareermatch/issue/AST-407) | JD eval, company resolution, consult handoff | Hedy | `ftr/AST-407` | AST-406 |
| [AST-408](https://linear.app/astralcareermatch/issue/AST-408) | Admin catalog + candidate saved-search UI | Katherine | `ftr/AST-408` | AST-403, AST-404 |

**Assignment rationale:**
- **Hedy:** Data layer, Playwright scrape, tracker/gazer ingest, batch pipeline, consult handoff — matches boards channel backend.
- **Katherine:** Admin + candidate React surfaces once **AST-403**/**404** APIs exist (queue is heavy on Artifacts; override assignee anytime).
- **Ada:** Not assigned — no agent-runtime or token-pipeline slice in v1 decomposition.

**Parallelism after AST-403:** **AST-404** and **AST-405** can proceed together; **AST-408** can plan against APIs once **404** lands.

**External dependency:** **AST-406** waits on [AST-389](https://linear.app/astralcareermatch/issue/AST-389) **Review Posted** for shared title-gate behavior.

Parent open questions (dedup scope, company matching, job identity key, dispatch model) stay on this ticket — resolve in child **plan-astral** docs before build where noted.

**Git (authoritative — ignore Linear `gitBranchName`):**
- Parent: `origin/ftr/AST-379`
- Children: `origin/ftr/AST-403` … `origin/ftr/AST-408`

Plan attachments: `https://github.com/susansomerset/astral/blob/ftr/AST-NNN/docs/features/boards/...` after **plan-astral**.

— Chuckles

#### chuckles — 2026-05-16T21:35:25.903Z
Definition draft ready for review. Key decisions made:
- Boards are **adopted globally** (shared parse profile); candidates own **saved searches** (multiple per board; params/deep-link or interactive per profile).
- Pipeline order locked: scrape → dedupe → **title gate before job row** → qualify listing → JD eval → **hiring company resolution** (reject agency-only) → existing consult.
- **Indeed/LinkedIn** and candidate logins explicitly out; **AST-397** spike stays separate from this production-flow definition.
- **6 open questions** (dedup scope, company match, job identity key, audit retention, dispatch model, first adopted board).

Assignee set back to **@susan** (definition review owner). Status remains **Backlog**.

Please review the Description and comment with changes or approval.

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
