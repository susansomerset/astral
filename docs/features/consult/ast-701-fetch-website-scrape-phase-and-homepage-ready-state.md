<!-- linear-archive: AST-701 archived 2026-06-23 -->

## Linear archive (AST-701)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-701/fetch-website-scrape-phase-and-homepage-ready-state-prefilter-as-batch  
**Status at archive:** Done  
**Project:** Astral Consult  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-700 — prefilter as batch process  
**Blocked by / blocks / related:** parent: AST-700; blocks: AST-702

### Description

## What this implements

Phase 1 of the two-phase company prefilter pipeline: a **fetch_website** dispatch task that claims companies in **WEBSITE_FOUND** and **WEBSITE_FOUND_RETRY**, scrapes homepage visible text and **nav_links**, persists prepared content in **company_data**, and transitions successful rows to a new **HOMEPAGE_READY** holding state. Scrape failures use today's **CANNOT_READ_WEBSITE** semantics with notes persisted. Redirect detection normalizes **company_website**.

## Acceptance criteria

1. A company in **WEBSITE_FOUND** with a valid **company_website**, when claimed by **fetch_website**, ends in **HOMEPAGE_READY** with homepage content persisted in **company_data** (and redirect normalized if the site moved).
2. A company whose homepage cannot be scraped ends in **CANNOT_READ_WEBSITE** with notes persisted — same observable behavior as today's prefilter scrape failure.
3. With **debug=True** on a dispatch batch, Susan can trace each company's scrape step via distinct index headers and substantive detail lines — not batch summaries alone.

## Boundaries

* Does **not** implement batch prefilter agent evaluation — sibling **AST-702**.
* Does **not** change **prefilter_company** rubric, prompt, or decode contract.
* Does **not** remove the monolithic single-company prefilter path — **AST-702** owns cutover.

## Notes for planning

* Mirror **scrape_jd_batch** / **GAZER_CONFIG** patterns for company-side scrape batching.
* **nav_links** extraction is in scope (Susan confirmed).
* New **HOMEPAGE_READY** state + transitions in **COMPANY_STATES** / **ASTRAL_CONFIG**.
* **dispatch_tasks** seed row for **fetch_website**; config mirror in **ROSTER_CONFIG** / **GAZER_CONFIG** as appropriate.
* Primary files: [**gazer.py**](<http://gazer.py>), [**roster.py**](<http://roster.py>), [**config.py**](<http://config.py>), [**database.py**](<http://database.py>), [**dispatcher.py**](<http://dispatcher.py>).

## Git branch (authoritative)

Per **orientation** § Branch law: parent **ftr/AST-700-prefilter-as-batch-process**, child **sub/AST-700/AST-701-fetch-website-scrape-phase-and-homepage-ready-state**.

### Comments

#### radia — 2026-06-16T05:13:55.164Z
### Plan fidelity

All five stages match the combined plan: `HOMEPAGE_READY` + transitions + `GAZER_CONFIG["fetch_website"]` + dispatch registry; `scrape_company_homepage_content` with `prefilter_company` refactor (same fail paths); `fetch_website_batch` (connectivity gate, semaphore=3, config-driven pass/fail states); consult routes `fetch_website` before `run_company_task`; `_RETRY_TASK_SEED` companion row. AST-702 scope not smuggled.

### ASTRAL_CODE_RULES

- **§1.3 / §2.1 / §2.6 / §2.8:** Config-driven states; DRY scrape helper; core owns transitions; `homepage_text` explicit storage only.
- **§2.4:** Normalized batch counts returned through consult.
- **§1.5.1:** Debug gated on `debug=True`; per-company `index N/M` headers + `debug_detail` metadata + batch summary — consistent with `scrape_jd_batch`.
- **§5a:** Lazy import in `consult.py` matches existing `scrape_jd_batch` routing pattern. No layer violations, silent failures, or hardcoded state sets in new paths.

### Issues

**fix-now:** none  
**discuss:** none

### Advisory

- Plan Stage 3 mentions truncated homepage preview in `debug_detail`; code logs char counts + URLs only — same as `scrape_jd_batch` success path. Optional UAT polish, not blocking.
- Ops: do not run `auto_mode=1` on both `prefilter` and `fetch_website` until AST-702 cutover (plan decision).

**Doc:** `docs/features/consult/ast-701-fetch-website-scrape-phase-and-homepage-ready-state.md` @ `bcc5630` on `origin/sub/AST-700/AST-701-fetch-website-scrape-phase-and-homepage-ready-state`.

#### betty — 2026-06-16T05:08:34.214Z
## QA test manifest (AST-701)

**Publish ref:** `origin/sub/AST-700/AST-701-fetch-website-scrape-phase-and-homepage-ready-state` @ `cb6cc37`

1. **`fetch_website_batch`** connectivity abort, missing `company_website`, scrape error, success persist (`homepage_text` + `nav_links`) — `tests/component/core/test_gazer.py::TestFetchWebsiteBatch`

2. **`run_consult_task`** routes `dispatch_task_key=fetch_website` to gazer batch — `tests/component/core/test_consult.py::TestRunConsultTaskRoutes::test_routes_fetch_website_batch`

3. **`scrape_company_homepage_content`** scrape error, redirect canonical URL, empty text, non-fatal nav failure — `tests/component/core/test_roster.py::TestAst701ScrapeCompanyHomepageContent`

4. Config: `HOMEPAGE_READY`, `GAZER_CONFIG["fetch_website"]`, dispatch registry, `homepage_text` key — `tests/component/utils/test_config.py::TestAst701FetchWebsiteConfig`

5. Dispatch retry seed clones `fetch_website` → `WEBSITE_FOUND_RETRY` on schema backfill — `tests/component/data/database/test_dispatch_tasks.py::TestAst701FetchWebsiteRetrySeed`

**Narrowed run:**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_gazer.py::TestFetchWebsiteBatch \
  tests/component/core/test_consult.py::TestRunConsultTaskRoutes::test_routes_fetch_website_batch \
  tests/component/core/test_roster.py::TestAst701ScrapeCompanyHomepageContent \
  tests/component/utils/test_config.py::TestAst701FetchWebsiteConfig \
  tests/component/data/database/test_dispatch_tasks.py::TestAst701FetchWebsiteRetrySeed
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

**Bible shasum (`origin/sub/...`):**
- `docs/test-bible/core/consult.md` e6281cf12a5eef6a2320b8095a225615bec4ee847ce77cd4f5d7b5a3f32ba33a
- `docs/test-bible/core/gazer.md` 898066845985996c2f2ad591ae8b4900625d44f73228944dfa9eafcb1c38b3bb
- `docs/test-bible/core/roster.md` 82b80b8b5bf78ff65d30e8ae18c6961cf91a3bed249fb5662dfe00d3eae7dff6
- `docs/test-bible/utils/config.md` d460d3b2bb6e64640bd30b1e0e99bdc7cffa9c14aa3232c4c594c7f56d6b1521

— Betty

#### chuckles — 2026-06-16T04:57:27.186Z
Plan doc: https://github.com/susansomerset/astral/blob/sub/AST-700/AST-701-fetch-website-scrape-phase-and-homepage-ready-state/docs/features/consult/ast-701-fetch-website-scrape-phase-and-homepage-ready-state.md

**Self-assessment**
- **Scope:** Single-Component — config state registry, shared roster scrape helper, gazer `fetch_website_batch`, consult routing, dispatch retry seed; scrape phase only (no agent/rubric).
- **Conf:** Medium — mirrors `scrape_jd_batch` + existing `prefilter_company` scrape steps; operational note that `prefilter` and `fetch_website` must not both auto-run on `WEBSITE_FOUND` until AST-702 cutover.
- **Risk:** Medium — bad scrape persistence or transitions block companies before batch prefilter but do not touch grades or job consult pipelines.

---

# fetch_website scrape phase and HOMEPAGE_READY state (prefilter as batch process)

**Linear:** [AST-701](https://linear.app/astralcareermatch/issue/AST-701/fetch-website-scrape-phase-and-homepage-ready-state-prefilter-as-batch-process)  
**Parent:** [AST-700](https://linear.app/astralcareermatch/issue/AST-700/prefilter-as-batch-process)  
**Publish ref:** `origin/sub/AST-700/AST-701-fetch-website-scrape-phase-and-homepage-ready-state`

Phase 1 of the AST-700 two-phase company prefilter pipeline: a new **`fetch_website`** dispatch task claims companies in **`WEBSITE_FOUND`** / **`WEBSITE_FOUND_RETRY`**, scrapes homepage visible text and **nav_links**, persists prepared content in **`company_data`**, and transitions successful rows to **`HOMEPAGE_READY`**. Scrape failures keep today's **`CANNOT_READ_WEBSITE`** semantics with notes persisted. Redirect detection normalizes **`company_website`**. Does **not** run the prefilter agent, change rubric/decode, or cut over from the monolithic **`prefilter`** dispatch path (**AST-702** owns evaluate-phase batching and cutover).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add **`HOMEPAGE_READY`** to **`COMPANY_STATES`**; add **`WEBSITE_FOUND`/`WEBSITE_FOUND_RETRY` → `HOMEPAGE_READY`/`CANNOT_READ_WEBSITE`** transitions; add **`GAZER_CONFIG["fetch_website"]`**; add **`homepage_text`** to **`ROSTER_CONFIG["company_data_keys"]`**; register **`fetch_website`** in **`DISPATCH_SCHEDULABLE_TASK_KEYS`**, **`_DISPATCH_COMPANY_ENTITY_TASK_KEYS`**, **`_dispatch_trigger_state_for_task_key`** | utils |
| `src/core/roster.py` | Extract shared **`async def scrape_company_homepage_content(...)`** from **`prefilter_company`** steps 1–2; refactor **`prefilter_company`** to call the helper (behavior unchanged) | core |
| `src/core/gazer.py` | Add **`fetch_website_batch`** mirroring **`scrape_jd_batch`** (connectivity gate, semaphore=3, per-company debug_index, summary dict) | core |
| `src/core/consult.py` | Route **`entity_type == "company"`** + **`dispatch_task_key == "fetch_website"`** to **`fetch_website_batch`** before **`run_company_task`** | core |
| `src/data/database.py` | Add **`("fetch_website", "WEBSITE_FOUND_RETRY")`** to **`_RETRY_TASK_SEED`** so retry companion dispatch rows clone from base **`fetch_website`** rows | data |

**Out of scope (AST-702 / later):** batch prefilter agent evaluation, disabling **`prefilter`** dispatch on **`WEBSITE_FOUND`**, changes to **`prefilter_company`** rubric/decode/persist beyond the scrape-helper refactor, UI work, tests (Betty manifest during **qa-child**).

---

## Stage 1: State machine and config scaffolding

**Done when:** **`HOMEPAGE_READY`** is a valid company state with batch criteria, transitions from **`WEBSITE_FOUND`** / **`WEBSITE_FOUND_RETRY`** to **`HOMEPAGE_READY`** and **`CANNOT_READ_WEBSITE`** exist in config, and **`fetch_website`** is a schedulable dispatch task key with admin defaults pointing at **`WEBSITE_FOUND`**.

1. In **`src/utils/config.py`**, block **`COMPANY_STATES`**, add after **`WEBSITE_FOUND_RETRY`**:
   ```python
   "HOMEPAGE_READY": {"batch_criteria": {"limit": 10, "sort_by": "updated_at"}},
   ```

2. In **`src/utils/config.py`**, list **`ASTRAL_CONFIG["company_state_transitions"]`**, append (do not remove existing rows):
   - `("WEBSITE_FOUND", "HOMEPAGE_READY")`
   - `("WEBSITE_FOUND", "CANNOT_READ_WEBSITE")`
   - `("WEBSITE_FOUND_RETRY", "HOMEPAGE_READY")`
   - `("WEBSITE_FOUND_RETRY", "CANNOT_READ_WEBSITE")`

   ⚠️ **Decision:** Add explicit transitions even though **`prefilter_company`** already transitions to **`CANNOT_READ_WEBSITE`** without a listed edge — keeps the state graph honest for roster UI / future validation.

3. In **`src/utils/config.py`**, block **`GAZER_CONFIG`**, add after **`scrape_jd`**:
   ```python
   "fetch_website": {
       "fallback_batch_size": 10,
       "pass_state": "HOMEPAGE_READY",
       "fail_state": "CANNOT_READ_WEBSITE",
   },
   ```

4. In **`src/utils/config.py`**, block **`ROSTER_CONFIG["company_data_keys"]`**, add:
   ```python
   "homepage_text": "homepage_text",
   ```
   (Explicit storage only — **not** a coat-check handler; same pattern as **`job_list_visible`**.)

5. In **`src/utils/config.py`**, dispatch registry updates:
   - Add **`"fetch_website"`** to **`DISPATCH_SCHEDULABLE_TASK_KEYS`**.
   - Add **`"fetch_website"`** to **`_DISPATCH_COMPANY_ENTITY_TASK_KEYS`**.
   - In **`_dispatch_trigger_state_for_task_key`**, before the final **`KeyError`**, add:
     ```python
     if task_key == "fetch_website":
         return "WEBSITE_FOUND"
     ```
   - Leave **`_dispatch_batch_call_mode_for`** unchanged — **`fetch_website`** stays **`batch_call_mode=0`** (same as **`scrape_jd`**: dispatcher **`_warm_then_gather`** calls **`fetch_website_batch`** once per claimed company).

   ⚠️ **Decision:** **`fetch_website`** and legacy **`prefilter`** both default to **`trigger_state=WEBSITE_FOUND`**. This ticket seeds schedulability only; Susan must not run **`auto_mode=1`** on both simultaneously. **AST-702** cutover disables **`prefilter`** on **`WEBSITE_FOUND`** when batch evaluate goes live.

---

## Stage 2: Shared homepage scrape helper (roster)

**Done when:** **`prefilter_company`** still passes/fails exactly as before (manual verification on one company), and **`scrape_company_homepage_content`** returns structured scrape output usable by **`fetch_website_batch`**.

1. In **`src/core/roster.py`**, immediately above **`async def prefilter_company`**, add:

   ```python
   async def scrape_company_homepage_content(
       short_name: str,
       company_website: str,
       *,
       browser_context=None,
   ) -> Dict[str, Any]:
   ```

   **Return dict keys (always present):** `company_website` (possibly updated canonical URL), `visible_text` (str), `enumerated_nav_links` (str, may be empty), `error` (str or None).

2. Move **`prefilter_company`** steps 1–2 into the helper without semantic change:
   - Call **`get_visible_text(company_website, context=browser_context, return_final_url=True)`**; on exception return `{..., "error": str(scrape_err)}` **without** transitioning state (caller decides).
   - If **`final_url`** differs from input, call **`update_company(short_name, company_website=final_url)`** and update local **`company_website`** variable.
   - If visible text is empty/whitespace-only, return `{..., "visible_text": visible_text or "", "error": "No visible text extracted"}`.
   - Call **`extract_site_page_list(company_website, max_depth=1, verify=False, context=browser_context)`** inside **`try/except`**; on success with URLs, set **`enumerated_nav_links = enumerate_array("", url_list)`**; on nav failure log **`logger.warning`** (non-fatal) and leave **`enumerated_nav_links=""`** — same as today.

3. Refactor **`prefilter_company`** body:
   - Replace inline steps 1–2 with **`scrape = await scrape_company_homepage_content(short_name, company_website, browser_context=browser_context)`**.
   - If **`scrape.get("error")`**: transition **`CANNOT_READ_WEBSITE`**, **`save_company_data(short_name, {"prefilter_company_notes": scrape["error"]})`**, set result fields, **`return result`** — identical observable outcomes to today.
   - Set **`company_website = scrape["company_website"]`**, **`visible_text = scrape["visible_text"]`**, **`enumerated_nav_links = scrape["enumerated_nav_links"]`**; continue with step 3 assembly unchanged.

---

## Stage 3: `fetch_website_batch` (gazer)

**Done when:** Calling **`fetch_website_batch(batch_id, [company_dict], debug=True)`** on a **`WEBSITE_FOUND`** row with a reachable homepage transitions it to **`HOMEPAGE_READY`** with **`homepage_text`** (+ **`nav_links`** when extracted) in **`company_data`**; scrape failures land in **`CANNOT_READ_WEBSITE`** with **`prefilter_company_notes`** set.

1. In **`src/core/gazer.py`**, add imports from roster:
   ```python
   from src.core.roster import scrape_company_homepage_content, transition_company_state
   from src.utils.config import ROSTER_CONFIG
   ```
   ( **`transition_company_state`** may already be available via roster import path — dedupe imports.)

2. Add **`async def fetch_website_batch(batch_id, companies, debug=False) -> Dict[str, int]`** beside **`scrape_jd_batch`**, matching its outer structure:
   - **`check_connectivity()`** gate — raise **`ConnectionError`** with batch id + count on failure.
   - Read **`cfg = GAZER_CONFIG["fetch_website"]`**, **`pass_state`**, **`fail_state`**, notes key **`notes_key = ROSTER_CONFIG["company_data_keys"]["prefilter_company_notes"]`**.
   - **`debug`**: call **`_log.set_debug_flag(True)`**; log batch start via **`_log.debug_index(func="gazer.fetch_website_batch", ...)`** mirroring **`scrape_jd_batch`**.
   - **`async with create_browser_context() as browser_context:`** for the whole batch; pass **`browser_context`** into each scrape call (reuse session across companies in one dispatch batch when **`batch_call_mode=1`** later; safe for per-entity **`batch_call_mode=0`** too).

3. Inner **`async def _fetch_one(company, company_index)`**:
   - **`short_name = company.get("short_name") or ""`**, **`company_website = (company.get("company_website") or "").strip()`**.
   - If no **`company_website`**: **`transition_company_state(short_name, fail_state)`**, **`save_company_data(short_name, {notes_key: "No company_website"})`**, increment **`failed`**, debug_index outcome **`failed — no company_website`**, **`return`**.
   - **`scrape = await scrape_company_homepage_content(short_name, company_website, browser_context=browser_context)`**.
   - If **`scrape.get("error")`**: **`transition_company_state(short_name, fail_state)`**, **`save_company_data(short_name, {notes_key: scrape["error"]})`**, increment **`failed`**, debug_index with redirect/char counts when known, **`return`**.
   - Success path — build **`data_to_save`**:
     ```python
     data_to_save = {"homepage_text": scrape["visible_text"]}
     if scrape.get("enumerated_nav_links"):
         data_to_save["nav_links"] = scrape["enumerated_nav_links"]
     save_company_data(short_name, data_to_save)
     transition_company_state(short_name, pass_state)
     ```
   - Increment **`passed`**; **`debug_index`** outcome must include: homepage char count, whether redirect normalized (**`final_url != original`**), nav link count or **non-fatal nav failure** — e.g. **`passed -> HOMEPAGE_READY (12345 chars redirect=yes nav=42 links)`**; use **`_log.debug_detail`** for **`company_website`**, canonical URL, and truncated homepage preview per AST-538 truncation contract.

4. Concurrency: **`asyncio.Semaphore(3)`** + **`asyncio.gather`** over companies (same cap as **`scrape_jd_batch`**).

5. Return **`{"passed": passed, "failed": failed, "total": len(companies)}`**; debug batch-end summary line like **`scrape_jd_batch`**.

   ⚠️ **Decision:** Persist scrape failures under **`prefilter_company_notes`** (not a new key) so roster UI and existing admin preview strings stay consistent until **AST-702** batch evaluate owns outcomes.

---

## Stage 4: Dispatcher routing (consult)

**Done when:** A dispatch run with **`task_key=fetch_website`**, **`entity_type=company`**, **`trigger_state=WEBSITE_FOUND`** invokes **`fetch_website_batch`** and returns normalized **`total_processed/passed/failed/errors`** counts.

1. In **`src/core/consult.py`**, function **`run_consult_task`**, in the **`if entity_type == "company":`** block **before** **`run_company_task`**:
   ```python
   task_key = (dispatch_task_key or "").strip()
   if task_key == "fetch_website":
       from src.core.gazer import fetch_website_batch
       r = await fetch_website_batch(batch_id, entities, debug=debug)
       total = r.get("total", len(entities))
       passed = r.get("passed", 0)
       failed = r.get("failed", 0)
       errors = max(0, total - passed - failed)
       return {
           "total_processed": total,
           "total_passed": passed,
           "total_failed": failed,
           "total_errors": errors,
       }
   ```

2. Leave the existing **`WEBSITE_FOUND` → `prefilter_company`** path in **`run_company_task`** untouched (**AST-702** cutover).

3. Manual verification (no test edits in this ticket):
   - Admin UI or SQL: ensure a candidate has a **`dispatch_task`** row with **`task_key='fetch_website'`**, **`trigger_state='WEBSITE_FOUND'`**, **`entity_type='company'`**, **`batch_call_mode=0`**, **`auto_mode=0`** initially.
   - Place one test company in **`WEBSITE_FOUND`** with valid **`company_website`**; run dispatch with **`debug=1`**; confirm **`HOMEPAGE_READY`**, **`company_data.homepage_text`**, and debug index lines.

---

## Stage 5: Dispatch retry seed (database)

**Done when:** Existing candidates with a base **`fetch_website`** dispatch row receive an **`INSERT OR IGNORE`** companion row with **`trigger_state='WEBSITE_FOUND_RETRY'`** on schema ensure (same mechanism as **`prefilter`** retry rows).

1. In **`src/data/database.py`**, tuple list **`_RETRY_TASK_SEED`**, append:
   ```python
   ("fetch_website", "WEBSITE_FOUND_RETRY"),
   ```

2. No change to **`save_dispatch_task`** — Susan creates base **`fetch_website`** rows via admin when enabling the task; schema backfill clones retry rows from each base row on next DB open/migration.

---

## Self-Assessment

### Scope — **Single-Component**

Touches config state registry, roster scrape helper, gazer batch runner, consult dispatch routing, and dispatch retry seed — one vertical slice (scrape phase only) with no agent or rubric changes.

### Conf — **Medium**

Pattern is established (**`scrape_jd_batch`** + existing **`prefilter_company`** scrape steps); open operational dependency is Susan not running **`prefilter`** and **`fetch_website`** dispatch concurrently until **AST-702** cutover.

### Risk — **Medium**

Incorrect scrape persistence or state transitions would block companies between **`WEBSITE_FOUND`** and batch prefilter, but would not corrupt grades or job consult pipelines.

---

## Plan vs ASTRAL_CODE_RULES cross-check

- **§1.3 DRY:** Scrape logic lives once in **`scrape_company_homepage_content`**; **`prefilter_company`** and **`fetch_website_batch`** both call it.
- **§2.1 config:** States, transitions, and **`GAZER_CONFIG`** orchestration fields live in **`config.py`** — no hard-coded state names in dispatcher.
- **§2.4 batch processing:** Uses existing claim/release via dispatcher **`get_new_company_batch`** / **`clear_company_batch`**; batch function returns pass/fail counts.
- **§2.6 state machine:** Core (**roster/gazer**) chooses target states; data layer only persists via **`transition_company_state`** / **`save_company_data`**.
- **§2.8 coat-check:** **`homepage_text`** is explicit storage only — no empty failure caching.
- **§3.5 naming:** Dispatch task key **`fetch_website`** matches job-side **`scrape_jd`** verb_noun pattern; holding state **`HOMEPAGE_READY`** mirrors **`JD_READY`**.

No conflicts requiring plan revision.

---

## Review

**Diff:** `origin/dev...origin/sub/AST-700/AST-701-fetch-website-scrape-phase-and-homepage-ready-state` @ `cb6cc37`

**Built:** five `code(AST-701)` commits + `test(AST-701)` manifest — config (`HOMEPAGE_READY`, `fetch_website` dispatch registry), `scrape_company_homepage_content`, `fetch_website_batch`, consult routing, `_RETRY_TASK_SEED` for `fetch_website`; Betty manifest in gazer/consult/roster/config/database component tests.

### What's solid

- **Plan fidelity:** All five stages land — config scaffolding, shared scrape helper with `prefilter_company` refactor (observable outcomes preserved), `fetch_website_batch` mirroring `scrape_jd_batch`, consult routing before `run_company_task`, retry seed. Scope stays scrape-phase only; no AST-702 cutover or agent/rubric changes.
- **§2.1 / §2.6:** States, transitions, and `GAZER_CONFIG["fetch_website"]` pass/fail targets live in `config.py`; core chooses states via `transition_company_state` / `save_company_data`.
- **§1.3 DRY:** Homepage scrape logic centralized in `scrape_company_homepage_content`; both call paths share it.
- **§2.4 batch:** Returns normalized pass/fail/total counts; consult maps to dispatcher totals; semaphore=3 matches `scrape_jd_batch`.
- **§1.5.1 debug:** `debug=True` gates `set_debug_flag`, per-company `debug_index` (`index N/M`), `debug_detail` metadata, batch-end summary — aligned with sibling gazer batch pattern.
- **§5d boundaries:** Legacy `prefilter` / `WEBSITE_FOUND` path untouched; operational dual-dispatch note documented in plan (AST-702 cutover).

### Issues

| Severity | Location | Finding |
| --- | --- | --- |
| — | — | **None (fix-now / discuss).** |

### Recommended actions

| Priority | Action |
| --- | --- |
| — | Proceed to **resolve-child** — no engineer changes required. |
| Advisory | Plan Stage 3 mentions truncated homepage preview in `debug_detail`; implementation logs char counts + URLs only (same as `scrape_jd_batch` success path). Optional polish if operators want content snippets during UAT — not blocking. |
| Advisory | Do not enable `auto_mode=1` on both `prefilter` and `fetch_website` until AST-702 cutover (plan decision; ops, not code). |

---

## Resolution (`resolve-child`)

**Date:** 2026-06-16

**Against:** Radia `review-child` on `origin/sub/AST-700/AST-701-fetch-website-scrape-phase-and-homepage-ready-state` @ **`bcc5630`**.

**Product / plan**

- **fix-now:** None — review clean; no product commits in this pass.
- **Advisory (debug_detail homepage preview):** Accepted as parity with `scrape_jd_batch`; no change in AST-701.
- **Advisory (dual dispatch ops):** Documented in plan Stage 1 decision; AST-702 owns cutover.

**§9a dry-run:** `origin/sub/AST-700/AST-701-fetch-website-scrape-phase-and-homepage-ready-state` merges cleanly into **`origin/dev`** and **`origin/ftr/AST-700-prefilter-as-batch-process`**.

**Manifest:** Betty narrowed run (11 tests) green @ **`cb6cc37`** — no `[qa-handoff]`.
