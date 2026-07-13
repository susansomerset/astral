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
