# AST-673 — Preserve job_site on find_job_page failure

**Linear:** [AST-673 — Preserve job_site on find_job_page failure (company.job_site is overwritten with company.company_website)](https://linear.app/astralcareermatch/issue/AST-673/preserve-job-site-on-find-job-page-failure-companyjob-site-is)

**Parent (reference only):** [AST-671 — company.job_site is overwritten with company.company_website](https://linear.app/astralcareermatch/issue/AST-671/companyjob-site-is-overwritten-with-companycompany-website)

**Publish ref:** `origin/sub/AST-671/AST-673-preserve-job-site-on-find-job-page-failure` (origin only)

## Summary

When **find_job_page** dispatch runs on a company that already has a verified **job_site**, failure or early-exit paths must not overwrite that column with **company_website**. Today `_save_company` always writes `job_site=page_option_url`, and many failure branches pass `page_option_url=company_website`. Susan confirmed: existing **job_site** → use the stored-careers-URL path (like **JOBS_FOUND**); no pre-existing **job_site** → leave **job_site** empty on failure (never substitute the homepage).

This ticket fixes **data persistence only**. Agent-data / Execution History visibility for **find_job_page** is sibling [AST-674](https://linear.app/astralcareermatch/issue/AST-674) under **AST-669** — do not implement AST-674 here.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/roster.py` | `_job_site_for_persist` helper; wire into `_save_company`; early redirect in `find_job_page`; fix `jobs_found_process_job_site` missing-job_site return shape | core |
| `tests/component/core/test_roster.py` | Betty manifest — failure preserve, empty baseline, success update, stored-URL redirect (engineer does not edit in build-child) | test |

**Verify only (no change expected):**

| File | Role |
|------|------|
| `src/utils/config.py` | `locate_job_page.dispatch_input_states` already includes TO_WATCH / JOBS_FOUND / PREFILTER_PASSED |
| `src/core/dispatcher.py` | Passes entity + batch into `run_company_task` unchanged |

**Out of scope:** Execution History / agent-data ([AST-674](https://linear.app/astralcareermatch/issue/AST-674)), websearch fallback ([AST-180](https://linear.app/astralcareermatch/issue/AST-180)), **company_website** redirect cleanup ([AST-318](https://linear.app/astralcareermatch/issue/AST-318)), UI changes.

---

## Stage 1: Central job_site persistence in `_save_company`

**Done when:** Every `_save_company` call that today passes `page_option_url=company_website` on a **NO_JOBLIST** (or other locate failure) path persists **pre-run job_site** when non-empty, or **empty string** when there was no pre-run **job_site**; **WATCH** / **NO_OPENINGS** / **CANNOT_PARSE_JOB_SITE** paths still write the confirmed or attempted listings URL from `page_option_url`.

1. In `src/core/roster.py`, immediately above `_save_company` (≈ line 1646), add module-level constant and helper:

   ```python
   _PERSIST_PAGE_OPTION_URL_STATES = frozenset({"WATCH", "NO_OPENINGS", "CANNOT_PARSE_JOB_SITE"})
   ```

   ```python
   def _job_site_for_persist(
       *,
       terminal_state: str,
       page_option_url: str,
       pre_run_job_site: str,
   ) -> str:
       """Return job_site column value — never substitute company_website on locate failure."""
       st = (terminal_state or "").strip()
       pre = (pre_run_job_site or "").strip()
       purl = (page_option_url or "").strip()
       if st in _PERSIST_PAGE_OPTION_URL_STATES:
           return purl
       if pre:
           return pre
       return ""
   ```

   ⚠️ **Decision:** Centralize in one helper rather than editing each of the 14 `page_option_url=company_website` call sites individually — same semantics everywhere `_save_company` runs (including `run_select_job_page_dispatch` and `run_parse_job_list_dispatch` empty-DOM failures) without duplicating rules.

2. In `_save_company`, add optional parameter `pre_run_job_site: Optional[str] = None` after `parse_instructions`.

3. At the top of `_save_company` body (before building `cd`), resolve pre-run value:

   ```python
   if pre_run_job_site is None:
       row = get_company(short_name)
       pre_run_job_site = str((row or {}).get("job_site") or "")
   job_site_to_write = _job_site_for_persist(
       terminal_state=state,
       page_option_url=page_option_url,
       pre_run_job_site=pre_run_job_site,
   )
   ```

4. Change the `update_company(...)` call to use `job_site=job_site_to_write` instead of `job_site=page_option_url`.

5. Do **not** change any call-site arguments to `_save_company` in this stage — the helper reads pre-run **job_site** from the DB when callers omit `pre_run_job_site`.

6. Run `python3 -m py_compile src/core/roster.py`.

### Self-review (Stage 1 vs ASTRAL_CODE_RULES)

- **§1.3 DRY:** One helper replaces repeated failure semantics.
- **§2.6 state machine:** State transitions unchanged; only the **job_site** column write differs on failure.
- **§3.3 imports:** No new cross-layer imports.

---

## Stage 2: Stored job_site entry path in `find_job_page`

**Done when:** `find_job_page` invoked for a company with non-empty **job_site** delegates to `jobs_found_process_job_site` (same scrape/select/parse chain as **JOBS_FOUND** dispatch) instead of requiring PJL prefilter data; companies with empty **job_site** still use PJL discovery.

1. In `find_job_page`, after `short_name` / `company_website` are resolved and **before** reading `possible_job_links` (≈ line 1324), add:

   ```python
   pre_job_site = str((company or {}).get("job_site") or "").strip()
   if pre_job_site:
       return await jobs_found_process_job_site(
           short_name, company_website, pre_job_site, debug=debug, ctx=ctx,
       )
   ```

   Use the `company` row already loaded on the next lines — move the `get_company(short_name)` call **above** this check so it is not fetched twice:

   ```python
   company = get_company(short_name)
   pre_job_site = str((company or {}).get("job_site") or "").strip()
   if pre_job_site:
       return await jobs_found_process_job_site(...)
   cdata = (company.get("company_data") or {}) if company else {}
   ```

2. Remove the duplicate `company = get_company(short_name)` that follows today.

3. Do **not** add the same redirect to `run_select_job_page_dispatch` — that entry is **select_job_page** task_key, out of this ticket's dispatch surface; Stage 1 `_save_company` fix still protects its failure paths.

4. Run `python3 -m py_compile src/core/roster.py`.

⚠️ **Decision:** Reuse `jobs_found_process_job_site` verbatim (Susan open Q2 on **AST-671**) rather than duplicating single-page assembly logic inline.

### Self-review (Stage 2)

- **§2.4 batch:** `jobs_found_process_job_site` already participates in dispatch **ctx** / **do_task** the same way when called from `run_company_task` **JOBS_FOUND** branch — no batch_id threading change in this ticket.
- Coordinate with [AST-674](https://linear.app/astralcareermatch/issue/AST-674): that sibling adds agent-data / batch_id fixes on the same path; this stage only adds the redirect gate.

---

## Stage 3: Return-shape cleanup in `jobs_found_process_job_site`

**Done when:** Missing **job_site** baseline returns empty **job_site** in the result dict (not **company_website**); all other behavior unchanged.

1. In `jobs_found_process_job_site` (≈ line 1251–1252), change the empty **job_site** early return from:

   ```python
   return {"short_name": short_name, "state": "NO_JOBLIST", "job_site": company_website, "response_type": "MISSING_JOB_SITE"}
   ```

   to:

   ```python
   return {"short_name": short_name, "state": "NO_JOBLIST", "job_site": "", "response_type": "MISSING_JOB_SITE"}
   ```

2. Do **not** call `_save_company` on this path (unchanged — no DB row update when **job_site** arg is empty).

3. Run `python3 -m py_compile src/core/roster.py`.

---

## Stage 4: Betty test manifest (qa-child — engineer does not edit `tests/`)

**Done when:** Betty's manifest covers AC 1–5 below; engineer runs manifest in **test-child**.

Add or extend tests in `tests/component/core/test_roster.py`:

| Test | AC | Setup | Assert |
|------|-----|-------|--------|
| `test_find_job_page_failure_preserves_existing_job_site` | 1, 2 | Company with `job_site="https://careers.example/jobs"`, `company_website="https://example.com"`, PJL path fails (e.g. missing links → `_save_company` NO_JOBLIST) | `update_company` / `_save_company` receives `job_site="https://careers.example/jobs"` (not homepage) |
| `test_find_job_page_failure_empty_job_site_stays_empty` | 4 | Company with empty `job_site`, PJL failure | Persisted `job_site=""` — never `company_website` |
| `test_find_job_page_success_updates_job_site` | 3 | PJL path → WATCH with confirmed `job_site_url` | `job_site` equals confirmed listings URL |
| `test_find_job_page_with_job_site_delegates_jobs_found_path` | 1, 5 | Company with non-empty `job_site`, mock `jobs_found_process_job_site` | `find_job_page` does not require PJL; delegate called once with stored URL |
| `test_jobs_found_process_job_site_failure_preserves_job_site` | 1 | Stored URL scrape empty → `_save_company` NO_JOBLIST | Pre-run **job_site** preserved (Stage 1 helper) |

Use existing `TestFindJobPage` / `run_company_task` monkeypatch patterns in the file — no new test modules.

---

## Execution contract (for build-child)

- Execute stages **in order**; one commit per stage on **epic worktree**, then publish to **`origin/sub/AST-671/AST-673-preserve-job-site-on-find-job-page-failure`**.
- Do **not** edit `tests/` — Betty owns Stage 4 manifest via **qa-child**.
- Do **not** implement [AST-674](https://linear.app/astralcareermatch/issue/AST-674) agent-data / batch_id work.
- If `_save_company` pre-run read races with an intentional mid-flow `update_company(job_site=...)` redirect (e.g. **jobs_found** redirect normalization), that updated URL is the value to preserve on subsequent failure — **stop and comment on AST-671** only if behavior contradicts AC.

---

## Self-Assessment

**Scope:** `scope-Single-Component` — Touches only `src/core/roster.py` persistence and `find_job_page` entry routing; no config, dispatcher, or UI changes.

**Conf:** `conf-high` — Root cause is identified (`_save_company` + `page_option_url=company_website` on failures); **JOBS_FOUND** path already models the stored-URL behavior Susan confirmed.

**Risk:** `risk-Medium` — **job_site** feeds gaze and **parse_job_list** dispatch; a mistake here corrupts production roster data, but the change is localized to one helper and one entry redirect with explicit AC-backed semantics.

### Self-review (full plan vs ASTRAL_CODE_RULES)

- **§1.3 DRY:** Single `_job_site_for_persist` helper; reuses `jobs_found_process_job_site`.
- **§2.1 config:** No new config literals.
- **§2.4 batch:** No claim/get/clear changes.
- **§2.6 state machine:** Terminal states unchanged; only **job_site** column write on failure paths.
- **§3.3 imports:** No new cross-layer imports.
- **§3.5 naming:** Helper follows `_snake_case` private function convention in `roster.py`.

---

## Review stub (Hedy / build)

**Publish ref:** `origin/sub/AST-671/AST-673-preserve-job-site-on-find-job-page-failure`  
**Product commits:** `9244c148` (Stage 1 — `_job_site_for_persist` + `_save_company`), `80d15c71` (Stage 2 — `find_job_page` stored-URL redirect), `d2c1fd7f` (Stage 3 — `jobs_found_process_job_site` empty baseline return shape)

---

## Radia review (2026-06-15)

**Diff:** `origin/dev...origin/sub/AST-671/AST-673-preserve-job-site-on-find-job-page-failure` (`90d5115a`)

### What's solid

| Area | Notes |
|------|-------|
| Plan fidelity | Stages 1–3 match plan: `_job_site_for_persist` + `_save_company` wiring, stored-URL redirect in `find_job_page`, empty baseline return in `jobs_found_process_job_site`. |
| AC coverage | Betty manifest maps AC 1–5 (`TestJobSiteForPersist673`, `TestFindJobPageAst673`, `TestJobsFoundProcessJobSite469` extensions). |
| §2.6 state machine | Terminal states unchanged; only `job_site` column write semantics differ on failure. |
| §1.3 DRY | One helper covers all 14 `page_option_url=company_website` call sites — correct tradeoff vs per-callsite edits. |
| Boundaries | No AST-674 agent-data / batch_id work; no config/dispatcher/UI churn. |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| **advisory** | `find_job_page` lines ~1343, ~1353 | Return dict still sets `"job_site": company_website` on PJL-failure paths while `_save_company` persists `""` (empty baseline). `run_company_task` does not re-persist from the return dict — DB is correct per AC. Align return shape in a follow-up if any caller displays result `job_site`. |
| **advisory** | `_save_company` docstring ~1692 | Still says `page_option_url` "becomes job_site"; helper now mediates — docstring stale. |
| **advisory** | `_save_company` ~1700–1702 | Extra `get_company` read on every save when `pre_run_job_site` omitted — acceptable per plan; note if hot-path profiling ever matters. |

### Recommended actions

| Item | Action |
|------|--------|
| fix-now | None — ready for `resolve-child` / merge. |
| discuss | Optional: normalize `find_job_page` failure return `job_site` to match persisted column (empty or pre-run URL). |
| advisory | Update `_save_company` docstring when touching file next. |
