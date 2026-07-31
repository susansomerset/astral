<!-- linear-archive: AST-874 archived 2026-07-29 -->

## Linear archive (AST-874)

**Archived:** 2026-07-29  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-874/fetch-culture-pages-gazer-task-and-culture-ready-gate-fetch-culture  
**Status at archive:** Archive  
**Project:** Astral Consult  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-872 — Fetch culture pages task is missing?  
**Blocked by / blocks / related:** parent: AST-872

### Description

## What this implements

Add a dispatchable **fetch_culture_pages** gazer batch step that claims jobs in **PASSED_GET** (with a dispatch score floor), ensures company culture page content is available only via the existing roster coat-check, and lands successful jobs in **CULTURE_READY**. Scrape/coat-check failures go to **NEED_CULTURE_CONTENT**; missing culture links go to **NO_CULTURE_LINKS**. Rewire LIKE grading to claim from **CULTURE_READY** instead of **PASSED_GET**. Debug=True batches emit per-job index headers and working-detail lines for found vs recorded culture content.

## Acceptance criteria

1. A job in **PASSED_GET** that meets the task score floor, claimed by **fetch_culture_pages**, ends in **CULTURE_READY** when coat-check returns culture page content (fresh fetch or already stored).
2. A job whose company culture content is already in company_data (or whose in-flight coat-check resolves successfully) still ends in **CULTURE_READY** without requiring a redundant scrape when content is already available.
3. A job whose culture scrape / coat-check fails to produce content ends in **NEED_CULTURE_CONTENT**.
4. A job with no culture links identified ends in **NO_CULTURE_LINKS**.
5. LIKE grading no longer claims jobs solely because they are in **PASSED_GET**; it claims from **CULTURE_READY**.
6. Jobs never skip **CULTURE_READY** on the happy path from GET to LIKE (every successful GET→LIKE path passes through **CULTURE_READY**).
7. With `debug=True` on a fetch_culture_pages batch, Susan can trace each job via distinct index headers and working-detail lines showing what was found and what was recorded for culture content.

## Boundaries

* Does not re-select culture page links (prefilter stays upstream). Does not change LIKE rubric, prompts, or grade scoring.
* Does not replace the coat-check handler; this task orchestrates and state-gates it. Does not invent a parallel scrape path.
* Does not remove or repurpose **NEED_WEBSITE_CONTENT** (LIKE-prep failure path remains). Does not change **fetch_website** / **HOMEPAGE_READY** or **fetch_jd** / **JD_READY** beyond edges needed for the new states.
* Does not strip culture coat-check from `_prep_live_content` — that path stays; this hop guarantees content availability earlier for cycle time and cache.

## Notes for planning

* Mirror **fetch_website** / **HOMEPAGE_READY** and **fetch_jd** / **JD_READY** patterns for gazer batch + pass/fail states.
* Primary domains: gazer batch, job state graph, consult dispatch routing / LIKE trigger, roster coat-check call site only (no new scrape path).
* Config is source of truth for states, task keys, score floors (§2.1).

## Git branch (authoritative)

Per orientation § Branch law: parent **ftr/AST-872-fetch-culture-pages**, child **sub/AST-872/AST-874-fetch-culture-pages-culture-ready-gate**. Created at dispatch-parent.

### Comments

#### chuckles — 2026-07-12T18:26:48.310Z
[merge-child] blocked: missing plan(AST-874): on origin/sub/AST-872/AST-874-fetch-culture-pages-culture-ready-gate

Plan landed as `docs(AST-874): plan — …` @ 1093ade. Add empty marker commit `plan(AST-874): sub-log marker — plan published as docs(AST-874) 1093ade` on the publish ref and push (same pattern as AST-843/AST-855). Then Chuckles re-runs merge-child.

@Hedy Lamarr
— Chuckles

#### radia — 2026-07-12T18:24:53.299Z
### Radia review — AST-874

**Diff:** `origin/dev...origin/sub/AST-872/AST-874-fetch-culture-pages-culture-ready-gate` @ `f1d80d9` (review doc @ `7df4491`)
**Doc:** https://github.com/susansomerset/astral/blob/7df4491c06fe688b28b9786c61d4f80f166a33d5/docs/features/consult/ast-874-fetch-culture-pages-gazer-task-and-culture-ready-gate.md

**What's solid**
- Stages 1–3 match plan: CULTURE_READY states + GAZER_CONFIG + registry; `fetch_culture_pages_batch` + consult route; dispatch seed + `grade_like` → CULTURE_READY.
- §2.1 / §2.6 / §2.8: config-owned states; coat-check only; no LIKE from PASSED_GET.
- §1.5.1: per-job debug index/detail when `debug=True`.
- Migration bind shape matches qualify-retry seed; score_floor cloned.

**Issues**

| Severity | Location | Finding |
|----------|----------|---------|
| advisory | `src/core/gazer.py` imports | `get_company` imported from tracker and database; database shadows tracker (same thin-delegate behavior). Dead tracker import — tidy if touching the file. |

**Recommended actions:** 0 fix-now · 0 discuss · 1 advisory — ready for `resolve-child`.

**Outcome:** Clean — ship.

#### betty — 2026-07-12T18:19:54.675Z
## QA test manifest (AST-874)

**Publish:** `origin/sub/AST-872/AST-874-fetch-culture-pages-culture-ready-gate` @ `f1d80d9` (`merge-tests(AST-874): origin/tests 65e23d6019858bd341179685435010048f7c7a4f`)

**Broken / obsolete:** none — new hop; existing `fetch_jd` / `fetch_website` / LIKE grading tests unchanged.

**Bible shasums (publish ref):**
- `docs/test-bible/core/gazer.md` — `bc9f0edcf4e86ad6405d3bd5186a6fc69ddb993798031d7aa8749b62ae74cd19`
- `docs/test-bible/core/consult.md` — `6087316c723f1083540b3ab71b56cf27fe2ec3a0c4244158251b043dcbfd6939`
- `docs/test-bible/utils/config.md` — `c0f002309cdbfe7271427ec6d4b4e2163ed2533c2632a81adf9d87f75b09aa1b`
- `docs/test-bible/data/database/dispatch_tasks.md` — `0eeca3d7deeeaee39f76546e01c2426ff0cddee8144dd1012e7e350c07a89a5f`

**Manifest (test-child) — narrowed run:**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_gazer.py::TestWebsiteContentHelpers \
  tests/component/core/test_gazer.py::TestFetchCulturePagesBatch \
  tests/component/core/test_consult.py::TestRunConsultTaskRoutes::test_routes_fetch_culture_pages_batch \
  tests/component/utils/test_config.py::TestAst874FetchCulturePagesConfig \
  tests/component/data/database/test_dispatch_tasks.py::TestAst874FetchCulturePagesDispatchMigration \
  -q
```

1. **Helpers + batch outcomes** — connectivity abort; missing company → `NEED_CULTURE_CONTENT`; cached `website_content` → `CULTURE_READY` (no coat-check); empty links → `NO_CULTURE_LINKS`; coat-check pass/fail; same-company in-memory writeback cache (`TestWebsiteContentHelpers`, `TestFetchCulturePagesBatch`)
2. **Consult route** — `dispatch_task_key=fetch_culture_pages` → `fetch_culture_pages_batch` (`test_routes_fetch_culture_pages_batch`)
3. **Config** — job states / LIKE priors; `GAZER_CONFIG["fetch_culture_pages"]`; schedulable defaults; `grade_like` trigger `CULTURE_READY`; score-gate + UI manifests (`TestAst874FetchCulturePagesConfig`)
4. **Dispatch migration** — seed `fetch_culture_pages` @ `PASSED_GET` from `grade_like`; retarget `PASSED_GET` → `CULTURE_READY`; re-seed when already at `CULTURE_READY`; idempotent (`TestAst874FetchCulturePagesDispatchMigration`)

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

— Betty

#### hedy — 2026-07-12T18:13:18.768Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-872/AST-874-fetch-culture-pages-culture-ready-gate/docs/features/consult/ast-874-fetch-culture-pages-gazer-task-and-culture-ready-gate.md

**Scope:** Single-Component — config state machine + one gazer batch + consult route + dispatch_task schema migration; no roster scrape rewrite and no LIKE scoring changes.

**Conf:** high — mirrors fetch_jd / fetch_website registration and batch shapes; coat-check call site is the existing get_company_data(..., "website_content") path from AST-183.

**Risk:** Medium — retargeting grade_like off PASSED_GET will stall LIKE until fetch_culture_pages is scheduled and green; wrong prior_states or a missed migration leaves jobs unclaimable or skips the gate.

---

# AST-874 — Fetch culture pages gazer task and CULTURE_READY gate

**Linear:** [AST-874](https://linear.app/astralcareermatch/issue/AST-874/fetch-culture-pages-gazer-task-and-culture-ready-gate-fetch-culture)
**Parent:** [AST-872](https://linear.app/astralcareermatch/issue/AST-872/fetch-culture-pages-task-is-missing)
**Publish ref:** `origin/sub/AST-872/AST-874-fetch-culture-pages-culture-ready-gate`

Insert an explicit **`fetch_culture_pages`** gazer batch hop between GET and LIKE: claim jobs in **`PASSED_GET`** (score-floor gated), ensure company culture page bodies via the existing roster **`website_content`** coat-check only, land successes in **`CULTURE_READY`**, and retarget **`grade_like`** to claim from **`CULTURE_READY`**. Coat-check / scrape failures → **`NEED_CULTURE_CONTENT`**; missing culture link selection → **`NO_CULTURE_LINKS`**. Does not re-select links, invent a parallel scrape path, or change LIKE rubric / scoring.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add job states + UI manifests; `GAZER_CONFIG["fetch_culture_pages"]`; register schedulable task + trigger/entity helpers; retarget `grade_like` default trigger to `CULTURE_READY`; score-gate `CULTURE_READY` | utils |
| `src/core/gazer.py` | Add `fetch_culture_pages_batch` (coat-check orchestration + debug contract); update module header | core |
| `src/core/consult.py` | Route `dispatch_task_key == "fetch_culture_pages"` to `fetch_culture_pages_batch` (job path, beside `fetch_jd`) | core |
| `src/data/database.py` | Idempotent `_ensure_dispatch_task_schema` migration: seed `fetch_culture_pages` @ `PASSED_GET`, retarget `grade_like` `PASSED_GET` → `CULTURE_READY` | data |

**Out of scope:** prefilter / culture link selection; LIKE prompts, rubric, or score math; replacing `_fetch_website_content` / coat-check; removing `_prep_live_content` coat-check; `fetch_website` / `HOMEPAGE_READY` / `fetch_jd` / `JD_READY` beyond `JOB_STATES` prior edges named below; Betty tests (qa-child).

---

## Stage 1: Job states, GAZER_CONFIG, dispatch registry, UI manifests

**Done when:** `CULTURE_READY`, `NEED_CULTURE_CONTENT`, and `NO_CULTURE_LINKS` are valid `JOB_STATES` with correct `prior_states`; LIKE outcomes accept only `CULTURE_READY` as prior; `fetch_culture_pages` is schedulable with admin defaults `entity_type=job`, `trigger_state=PASSED_GET`; `grade_like` admin default trigger is `CULTURE_READY`; `CULTURE_READY` is score-floor gated for claims; skipped/in-review UI lists include the new states.

1. In `src/utils/config.py`, block `JOB_STATES`, after `PASSED_GET` / GET fail rows and **before** `NEED_WEBSITE_CONTENT`, insert:

   ```python
   "CULTURE_READY":           {"prior_states": ["PASSED_GET"]},
   "NEED_CULTURE_CONTENT":    {"prior_states": ["PASSED_GET"]},
   "NO_CULTURE_LINKS":        {"prior_states": ["PASSED_GET"]},
   ```

2. In the same `JOB_STATES` block, change LIKE-related priors from `PASSED_GET` to `CULTURE_READY`:

   - `PASSED_LIKE`: `{"prior_states": ["CULTURE_READY"]}`
   - `FAILED_LIKE`: `{"prior_states": ["CULTURE_READY"]}`
   - `FAILED_TECHNICAL_LIKE`: `{"prior_states": ["CULTURE_READY"]}`

3. Extend `NEED_WEBSITE_CONTENT` priors to include `CULTURE_READY` (keep existing `PASSED_DO`, `PASSED_GET`) so `_prep_live_content` can still transition there if coat-check fails during LIKE after this hop:

   ```python
   "NEED_WEBSITE_CONTENT": {"prior_states": ["PASSED_DO", "PASSED_GET", "CULTURE_READY"]},
   ```

4. In `GAZER_CONFIG`, after `fetch_jd` (before `fetch_website`), add:

   ```python
   "fetch_culture_pages": {
       "fallback_batch_size": 10,
       "pass_state": "CULTURE_READY",
       "fail_state": "NEED_CULTURE_CONTENT",
       "no_links_state": "NO_CULTURE_LINKS",
   },
   ```

   ⚠️ **Decision:** Fail destinations live in `GAZER_CONFIG` (not hardcoded in gazer) — same pattern as `fetch_jd` / `fetch_website` pass/fail keys. `no_links_state` is an extra config key for the distinct AC4 outcome.

5. Dispatch registry updates in `src/utils/config.py`:

   - Add `"fetch_culture_pages"` to `DISPATCH_SCHEDULABLE_TASK_KEYS` (next to `fetch_jd`).
   - In `_dispatch_trigger_state_for_task_key`, add:
     ```python
     if task_key == "fetch_culture_pages":
         return "PASSED_GET"
     ```
   - Change the `grade_like` branch from `return "PASSED_GET"` to `return "CULTURE_READY"`.
   - In `_dispatch_entity_type_for_task_key`, add `"fetch_culture_pages"` to the job-entity tuple that already lists `fetch_jd`, `qualify_job_listings`, `evaluate_jd`, `grade_*`, etc.

6. Score / UI manifests in `src/utils/config.py`:

   - Add `"CULTURE_READY"` to `IN_REVIEW_STATES` after `"PASSED_GET"` and before `"PASSED_LIKE"`.
   - Add `"CULTURE_READY"` to `PASSED_SCORE_GATED_STATES` so LIKE claims at `CULTURE_READY` still enforce `dispatch_task.score_floor` (fetch at `PASSED_GET` already gates via existing membership).
   - In `JOBS_IN_REVIEW_UI_SECTIONS`, insert `{"state": "CULTURE_READY", "label": "Culture Ready"}` after Passed GET.
   - Add `"NEED_CULTURE_CONTENT"` and `"NO_CULTURE_LINKS"` to `SKIPPED_STATES`.
   - Insert both into `JOBS_SKIPPED_SECTION_ORDER` immediately after `"NEED_WEBSITE_CONTENT"`.
   - Add labels in `JOBS_SKIPPED_SECTION_LABELS`:
     - `"NEED_CULTURE_CONTENT": "Need Culture Content"`
     - `"NO_CULTURE_LINKS": "No Culture Links"`

7. Update the `GAZER_CONFIG` header comment (top of that block and `gazer.py` module docstring later) so it lists `fetch_culture_pages` beside `fetch_jd`.

**Commit message:** `code(AST-874): stage 1 — CULTURE_READY states and fetch_culture_pages registry`

---

## Stage 2: `fetch_culture_pages_batch` + consult routing

**Done when:** A claimed job batch with `dispatch_task_key=fetch_culture_pages` routes through consult into gazer; each job ends in `CULTURE_READY`, `NEED_CULTURE_CONTENT`, or `NO_CULTURE_LINKS` per the decision tree below; `debug=True` emits per-job index headers and working-detail lines for found vs recorded culture content; no new scrape path outside `roster.get_company_data(..., "website_content")`.

1. In `src/core/gazer.py`, update the module header `In-scope:` list to include `fetch_culture_pages_batch`.

2. In `src/core/gazer.py`, after `fetch_jd_batch` (before `fetch_website_batch`), add:

   ```python
   async def fetch_culture_pages_batch(
       batch_id: str,
       jobs: List[Dict[str, Any]],
       debug: bool = False,
   ) -> Dict[str, int]:
   ```

   Behavior (literal):

   - If `debug`: `_log.set_debug_flag(True)`.
   - Read `cfg = GAZER_CONFIG["fetch_culture_pages"]`; bind `pass_state`, `fail_state`, `no_links_state` from cfg.
   - Connectivity: if coat-check may scrape, gate with `await check_connectivity()` and raise `ConnectionError` with the same style as `fetch_jd_batch` when offline (include `batch_id` and job count).
   - Optional batch-start debug index when `debug and len(jobs) > 0` (same shape as `fetch_jd_batch`).
   - Process jobs **sequentially** in list order (no gather / no parallel browser sessions at the batch layer).

     ⚠️ **Decision:** Sequential processing — ticket says coat-check fetch is one company at a time; parallel jobs sharing a company would race the coat-check handler. After a successful fetch, write `website_content` onto the in-memory `company["company_data"]` so later jobs for the same company in this batch hit the coat-check cache without a second scrape.

   - Per job (1-indexed for debug):

     a. Resolve `aid = job["astral_job_id"]`, `company_key = (job.get("company") or "").strip()`.
     b. If no `company_key` or `tracker.get_company(company_key)` returns `None`: transition to `fail_state`; if debug, index header outcome `failed — no company -> {fail_state}`; count failed; continue.
     c. Let `cd = company.get("company_data") or {}` (ensure dict).
     d. **Already recorded:** if `cd.get("website_content")` is a non-empty list (or non-empty string), transition to `pass_state` without calling coat-check. Debug: outcome `passed -> {pass_state} (cached)`; detail line with page count or content length and `"recorded=cached"`.
     e. **No links:** let `links = cd.get("culture_links_to_explore") or []`. If empty: transition to `no_links_state`. Debug: outcome `failed — no culture links -> {no_links_state}`; detail `culture_links_to_explore=[]`.
     f. **Coat-check:** `from src.core.roster import get_company_data` (or use existing gazer import of `get_company_data`). `content = await get_company_data(company, "website_content")`.
     g. If `content` is truthy: write back into `company.setdefault("company_data", {})["website_content"] = content`; transition to `pass_state`. Debug: outcome `passed -> {pass_state}`; detail with found page count / urls (or char length) and `"recorded=coat-check"`.
     h. Else: transition to `fail_state`. Debug: outcome `failed — coat-check empty -> {fail_state}`; detail that links were present but content unresolved.

   - Use `transition_job_state([aid], …)` from tracker (already imported in gazer).
   - Return `{"passed": N, "failed": N, "total": len(jobs)}` where `passed` counts only `pass_state` transitions; `failed` counts both fail destinations (`NEED_CULTURE_CONTENT` + `NO_CULTURE_LINKS`).
   - When `debug`, emit a final `debug_detail` summary line with passed/failed/total and the three config state names (same style as `fetch_jd_batch`).

3. In `src/core/consult.py`, inside `run_consult_task` on the job path, immediately after the `fetch_jd` branch (same summary-normalization path), add:

   ```python
   elif task_key == "fetch_culture_pages":
       from src.core.gazer import fetch_culture_pages_batch
       r = await fetch_culture_pages_batch(batch_id, entities, debug=debug)
   ```

   Do not add this task to the `grade_*` / chain branches.

**Commit message:** `code(AST-874): stage 2 — fetch_culture_pages_batch and consult route`

---

## Stage 3: Dispatch row migration (grade_like retarget + seed)

**Done when:** On next `_ensure_dispatch_task_schema` run, every existing `grade_like` row with `trigger_state='PASSED_GET'` moves to `CULTURE_READY`, and each candidate that had such a row (or already has `grade_like` @ `CULTURE_READY`) has a `fetch_culture_pages` row at `PASSED_GET` when missing — so happy-path GET→LIKE cannot skip the culture hop.

1. In `src/data/database.py`, function `_ensure_dispatch_task_schema`, **after** the existing AST-794 / scrape_jd→fetch_jd rename block and **before** `_dispatch_task_schema_ensured = True`, append an AST-874 block that:

   a. For each row matching `task_key='grade_like' AND trigger_state='PASSED_GET'`, `INSERT` a sibling `fetch_culture_pages` row when absent, cloning scheduling columns from that `grade_like` row (`entity_type`, `sort_by`, `batch_call_mode`, `freq_hrs`, `min_count`, `batch_size`, `auto_mode`, `debug`, `skip_cache`, `max_runs`, `score_floor`, `updated_at`) with `trigger_state='PASSED_GET'` and `task_key='fetch_culture_pages'`. Use `WHERE NOT EXISTS` on `(candidate_id, task_key, trigger_state)` like the qualify retry seed.

   b. `UPDATE dispatch_task SET trigger_state = 'CULTURE_READY' WHERE task_key = 'grade_like' AND trigger_state = 'PASSED_GET'`.

   c. Also seed `fetch_culture_pages` @ `PASSED_GET` for candidates that already have `grade_like` @ `CULTURE_READY` but lack `fetch_culture_pages` (clone from that `grade_like` row) — covers re-runs after partial apply.

   d. `conn.commit()` after the block.

   ⚠️ **Decision:** Clone `score_floor` / `auto_mode` from the LIKE row so operators keep the same floor they had for LIKE-at-PASSED_GET on the new fetch hop; they can tune floors independently in Scheduled Actions afterward. Do **not** invent a global default score_floor literal in Python.

2. Do not create a separate `*_RETRY` companion dispatch row for this task (no `retry_state` on `CULTURE_READY`).

**Commit message:** `code(AST-874): stage 3 — retarget grade_like and seed fetch_culture_pages`

---

## Execution contract

The plan is binding. Execute stages in order; one commit per stage on the epic worktree sub checkout; publish each stage to `origin/sub/AST-872/AST-874-fetch-culture-pages-culture-ready-gate`. Do not add files outside the table. If a step is ambiguous or the codebase drifted, stop and comment on **AST-872** with the `🛑 Stage N blocked` template — do not improvise.

---

## Self-Assessment

**Scope:** `Single-Component` — one consult/gazer culture-fetch gate: config state machine + one gazer batch + consult route + dispatch_task schema migration; no roster scrape rewrite and no LIKE scoring changes.

**Conf:** `high` — mirrors `fetch_jd` / `fetch_website` registration and batch shapes; coat-check call site is the existing `get_company_data(..., "website_content")` path from AST-183.

**Risk:** `Medium` — retargeting `grade_like` off `PASSED_GET` will stall LIKE until `fetch_culture_pages` is scheduled and green; wrong prior_states or a missed migration leaves jobs unclaimable or skips the gate.

---

## Self-review vs ASTRAL_CODE_RULES

- **§2.1 config:** states, pass/fail/no_links, task key, triggers live in `config.py` — no hardcoded state sets in gazer beyond reading `GAZER_CONFIG`.
- **§2.4 batch:** dispatcher still owns claim/release; gazer only transitions claimed jobs (same as `fetch_jd_batch`).
- **§2.6 state machine:** `prior_states` updated so GET→CULTURE_READY→LIKE is enforced; LIKE cannot enter from `PASSED_GET` after this change.
- **§2.8 coat-check:** task orchestrates `get_company_data`; does not duplicate scrape logic.
- **§1.5.1 debug:** per-job `debug_index` + `debug_detail` only when `debug=True`.
- **§1.3 DRY / §3.3 imports:** consult lazy-imports gazer batch (existing pattern); gazer already imports `get_company_data`.
- **§3.5 naming:** `fetch_culture_pages` / `fetch_culture_pages_batch` align with `fetch_jd` / `fetch_website`.

## Review (build stub)

**Built:** `astral-AST-872` @ `4b1222e` on `origin/sub/AST-872/AST-874-fetch-culture-pages-culture-ready-gate`

| Stage | Commit | Summary |
|-------|--------|---------|
| plan | `1093ade` | Plan doc |
| 1 | `a2ba6d6` | CULTURE_READY states, GAZER_CONFIG, dispatch registry, UI manifests |
| 2 | `b2e8087` | `fetch_culture_pages_batch` + consult route |
| 3 | `4b1222e` | Seed `fetch_culture_pages` @ PASSED_GET; retarget `grade_like` → CULTURE_READY |

**Verify:** `python3 -m py_compile` on `config.py`, `gazer.py`, `consult.py`, `database.py` — pass. Migration SQL smoke on in-memory sqlite — pass.

**Note for Betty:** new dispatch task key + job states; LIKE trigger moved off PASSED_GET.

## Radia review

**Diff:** `origin/dev...origin/sub/AST-872/AST-874-fetch-culture-pages-culture-ready-gate` @ `f1d80d9`

### What’s solid

- Plan stages 1–3 match the product diff: `JOB_STATES` / UI manifests / `GAZER_CONFIG["fetch_culture_pages"]` / dispatch registry; `fetch_culture_pages_batch` + consult route; `_ensure_dispatch_task_schema` seed + `grade_like` retarget.
- §2.1 / §2.6: pass/fail/no_links and LIKE priors live in config; GET → CULTURE_READY → LIKE is enforced; no LIKE from `PASSED_GET`.
- §2.8: coat-check only via `get_company_data(..., "website_content")` — no parallel scrape path.
- §1.5.1 / §5f: per-job `debug_index` + `debug_detail` (found/recorded) gated on `debug=True`; batch summary detail present.
- §2.4: gazer only transitions claimed jobs; sequential batch avoids same-company coat-check races; in-memory writeback covered by tests.
- Migration bind counts match the qualify-retry seed pattern; `score_floor` cloned from LIKE (no invented default).
- Self-Assessment Scope `Single-Component` matches the footprint.

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| advisory | `src/core/gazer.py` imports | `get_company` imported from both `tracker` and `database`; database shadows tracker. Behavior is identical (tracker is a thin delegate), but the tracker import is dead. Drop one import on a tidy-up if touching the file. |

### Recommended actions

| Action | Item |
|--------|------|
| none (ship) | 0 fix-now · 0 discuss · 1 advisory |

**Outcome:** Clean — ready for `resolve-child`.

## Resolution

**Date:** 2026-07-12  
**Review:** Radia clean sign-off @ `7df4491` (0 fix-now · 0 discuss · 1 advisory)

| Item | Action |
|------|--------|
| advisory — dual `get_company` import | Dropped `get_company` from tracker import; keep `database.get_company` (same thin-delegate behavior). |

**§9a:** dry-run publish ref vs `origin/dev` and `origin/ftr/AST-872-fetch-culture-pages` — recorded on resolve commit.
