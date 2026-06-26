<!-- linear-archive: AST-674 archived 2026-06-23 -->

## Linear archive (AST-674)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-674/job-site-aware-find-job-page-and-dispatch-agent-data-inspection-find  
**Status at archive:** Done  
**Project:** Astral Roster  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-669 — find_job_page job doesn't display the agent content  
**Blocked by / blocks / related:** parent: AST-669; related: AST-671; related: AST-528

### Description

## What this implements

Fix **find_job_page** dispatch so companies at **TO_WATCH** with a verified **job_site** (distinct from **company_website**) follow the known-careers-URL locate path instead of instant **NO_JOBLIST** when **possible job links** (PJL) from prefilter are empty. Ensure roster LLM steps invoked by that path (**select_job_page**, chained **parse_job_list**) persist **agent_data** under the dispatch **batch_id** so Execution History agent-data inspection shows prompt and response — not an empty modal.

## Acceptance criteria

1. On staging, re-run **find_job_page** for komodohealth (or equivalent company at **TO_WATCH** with a verified **job_site** distinct from **company_website** and 0 PJLs): the run does **not** instantly land **NO_JOBLIST** solely because PJLs are empty when **job_site** is usable.
2. When that run invokes roster LLM steps, Execution History agent-data inspection for the batch shows readable **TASK** and **RESPONSE** (and related prompt block types).
3. Agent-data rows use the batch_id on the Execution History row Susan clicked.
4. If no LLM call is genuinely correct after the job-site path is evaluated, Susan can determine that from execution logs and history without a misleading empty modal that looks like a persistence failure.
5. Other dispatch task types and ad-hoc workbench history rows still show agent data as before.

## Boundaries

* Does **not** fix **job_site** field overwritten with **company_website** on failure paths — sibling [AST-673](https://linear.app/astralcareermatch/issue/AST-673/preserve-job-site-on-find-job-page-failure-companyjob-site-is) under [AST-671](https://linear.app/astralcareermatch/issue/AST-671/companyjob-site-is-overwritten-with-companycompany-website); coordinate if both touch the same `_save_company` paths.
* Does **not** include [AST-666](https://linear.app/astralcareermatch/issue/AST-666/find-job-page-is-well-and-truly-borked).
* Does **not** add company-modal agent-story tabs.
* Does **not** invent synthetic agent-data blocks.

## Notes for planning

* Reference behavior: **JOBS_FOUND** / **job_site** scrape path ([AST-469](https://linear.app/astralcareermatch/issue/AST-469)).
* Per-hop Execution History ([AST-528](https://linear.app/astralcareermatch/issue/AST-528)) — batch_id on ledger rows must match **agent_data** lookup.
* Primary layer: `src/core/roster.py`; verify dispatch **ctx** passes **batch_id** into **do_task** for **select_job_page**.

## Git branch (authoritative)

Per **orientation** § Branch law: parent `ftr/AST-669-find-job-page-job-doesnt-display-the-agent-content`, child `sub/AST-669/AST-674-job-site-find-job-page-agent-data`. Created at **dispatch-parent**.

### Comments

#### radia — 2026-06-15T18:44:10.274Z
**Review** — `origin/dev...origin/sub/AST-669/AST-674-job-site-find-job-page-agent-data` (incl. `cd270ad5` doc)

**Verdict:** Clean — no **fix-now** items.

### Solid (plan fidelity + rules)

- **Stage 1:** `_is_verified_job_site_distinct` reuses `_normalize_company_url_for_dedupe`; `find_job_page` redirects only when stored **job_site** ≠ **company_website** (AC #1). §1.3 DRY, §2.6 routing-only.
- **Stage 2:** Both no-LLM **NO_JOBLIST** exits emit INFO `reason=no_pjl_or_nav` / `all_pjl_scrapes_failed` with counts (AC #4). §1.5 production INFO only — no debug-contract noise.
- **Stage 3 audit:** `dispatcher._dispatch_one` already `log_batch_id.set(entity_batch_id)` before `run_company_task`; no roster guard needed. `TestFindJobPageAst674::test_find_assembled_select_job_page_uses_entity_log_batch_id` locks AC #2–#3.
- **Tests:** `TestJobSiteDistinct674` + `TestFindJobPageAst674` cover AC 1–4 per bible manifest.

### Advisory

- Sub tip also carries **AST-676** / **AST-679** test-bible commits from `origin/tests` merge (`a0e02d28`, `d997407b`) — tests/docs only, no AST-674 product scope creep.
- Helper placed immediately above `find_job_page` (plan line hint said after `_job_site_for_persist`) — better locality; no action.

**Doc:** `docs/features/roster/ast-674-job-site-find-job-page-agent-data.md` § Radia review

**resolve-child** may proceed.

#### betty — 2026-06-15T18:41:03.249Z
## QA test manifest (AST-674)

**Publish ref:** `origin/sub/AST-669/AST-674-job-site-find-job-page-agent-data` @ `75dad248`  
**Tests commit:** `da53a7b2` on `origin/tests`  
**Bible:** `docs/test-bible/core/roster.md` shasum `87614e3ddd9f39b805a0b03b0ad408e6a62dcae14006d4b2526b7dd160af9fbd`

### Existing coverage (unchanged)

- **AST-673** persistence + coarse redirect: `TestFindJobPageAst673`, `TestJobSiteForPersist673`, `TestJobsFoundProcessJobSite469` — still required; AST-674 tightens redirect predicate only.
- **AC #5** (other dispatch paths): existing `tests/component/core/test_agent.py` **`do_task`** / **AST-531** hop-ledger tests — no new roster smoke.

### New / revised (this pass)

1. **`TestJobSiteDistinct674::test_is_verified_job_site_distinct`** — helper: distinct vs equal vs empty URLs (normalization).
2. **`TestFindJobPageAst674::test_distinct_job_site_delegates_before_empty_pjl_exit`** — AC #1: 0 PJLs + distinct **job_site** → **`jobs_found_process_job_site`**, not PJL **NO_JOBLIST**.
3. **`TestFindJobPageAst674::test_equal_job_site_falls_through_to_pjl_path`** — AC #1 (neg): **job_site** == **company_website** → PJL path; **`jobs_found_process_job_site`** not called.
4. **`TestFindJobPageAst674::test_find_assembled_select_job_page_uses_entity_log_batch_id`** — AC #2–3: **`select_job_page`** **`do_task`** sees entity **`log_batch_id`** + dispatcher **`ctx`** keys.
5. **`TestFindJobPageAst674::test_no_pjl_emits_no_llm_log`** — AC #4: INFO log `NO_JOBLIST without LLM — reason=no_pjl_or_nav`.
6. **`TestFindJobPageAst674::test_all_pjl_scrapes_failed_emits_no_llm_log`** — AC #4: INFO log `reason=all_pjl_scrapes_failed`.

### Run (test-child)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_roster.py::TestJobSiteDistinct674 \
  tests/component/core/test_roster.py::TestFindJobPageAst674
```

**Pass criterion:** pytest green on narrowed args (no zero-arg **`LOCKED_AT_100`** gate required for this manifest).

### Stage 3 audit note

Plan Stage 3 confirmed **`dispatcher._dispatch_one`** already sets **`log_batch_id.set(entity_batch_id)`** before **`run_company_task`** for **`find_job_page`** — no roster guard added; manifest item #4 locks the contract via **`_find_job_page_from_assembled`** + **`log_batch_id`** monkeypatch.

— Betty

#### hedy — 2026-06-15T18:18:02.082Z
Plan: [`docs/features/roster/ast-674-job-site-find-job-page-agent-data.md`](https://github.com/susansomerset/astral/blob/sub/AST-669/AST-674-job-site-find-job-page-agent-data/docs/features/roster/ast-674-job-site-find-job-page-agent-data.md) on `origin/sub/AST-669/AST-674-job-site-find-job-page-agent-data` @ `b500b6f6`.

**Scope:** `scope-Single-Component` — `roster.py` entry gate + no-LLM logging; optional `log_batch_id` guard only if audit finds a gap.

**Conf:** `conf-high` — AST-469 stored-URL chain and AST-531 agent_data plumbing already on ftr; this ticket adds Susan's distinct-URL predicate and documents batch_id contract.

**Risk:** `risk-Medium` — locate/parse is production-critical; predicate uses existing `_normalize_company_url_for_dedupe`; Betty manifest locks AC cases.

**Approach (4 stages):**
1. `_is_verified_job_site_distinct` — redirect to `jobs_found_process_job_site` only when job_site ≠ company_website (tightens AST-673 coarse `if pre_job_site`).
2. INFO logs on NO_JOBLIST exits that skip LLM (`reason=no_pjl_or_nav` / `all_pjl_scrapes_failed`) for AC #4.
3. Read-only agent_data batch_id audit; conditional `log_batch_id` restore from `ctx.entity_batch_id` only if dispatcher ledger gap found.
4. Betty manifest for distinct redirect, homepage-equal fallback, and batch_id threading.

---

# AST-674 — Job_site-aware find_job_page and dispatch agent-data inspection

**Linear:** [AST-674 — Job_site-aware find_job_page and dispatch agent-data inspection](https://linear.app/astralcareermatch/issue/AST-674/job-site-aware-find-job-page-and-dispatch-agent-data-inspection-find)

**Parent (reference only):** [AST-669 — find_job_page job doesn't display the agent content](https://linear.app/astralcareermatch/issue/AST-669/find-job-page-job-doesnt-display-the-agent-content)

**Publish ref:** `origin/sub/AST-669/AST-674-job-site-find-job-page-agent-data` (origin only)

## Summary

Staging repro (`find_job_page-22f8263f-…`, komodohealth): dispatch logged `0 PJLs`, transitioned **TO_WATCH → NO_JOBLIST** in under one second, and Execution History agent-data inspection was empty — no LLM ran. Susan expects companies with a verified **job_site** URL **distinct from** **company_website** to follow the known-careers-URL locate path (**AST-469** `jobs_found_process_job_site` → `select_job_page` → `parse_job_list` via `run_next`), producing real **agent_data** under the dispatch **batch_id** Susan clicked. This ticket tightens the **find_job_page** entry gate (distinct stored URL only), adds observable logging when a legitimate no-LLM exit occurs, and verifies **agent_data** / per-hop ledger **batch_id** threading on that path without changing other dispatch tasks.

**Sibling dependency:** [AST-673](https://linear.app/astralcareermatch/issue/AST-673) (merged on `origin/ftr/AST-669-…`) already adds `_job_site_for_persist` and a coarse `if pre_job_site:` redirect. AST-674 adds the **distinct-from-homepage** predicate and agent-data observability; it does **not** re-implement AST-673 persistence rules.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/roster.py` | `_is_verified_job_site_distinct` helper; tighten `find_job_page` redirect; INFO log on no-LLM **NO_JOBLIST** exits; entry log when stored-URL path runs | core |
| `tests/component/core/test_roster.py` | Betty manifest — distinct-job_site redirect, homepage-equal fallback to PJL path, no-LLM log reason (engineer does not edit in build-child) | test |

**Verify only (no change expected unless audit finds a gap):**

| File | Role |
|------|------|
| `src/core/agent.py` | `do_task` stores **agent_data** under `hop_ledger_batch_id or log_batch_id.get()`; `run_next` child hops open per-hop ledger ([AST-531](https://linear.app/astralcareermatch/issue/AST-531)) |
| `src/core/dispatcher.py` | Sets `log_batch_id` to `entity_batch_id` for `find_job_page` dispatch (no `run_next` on `find_job_page` task row) |
| `src/ui/api/api_system.py`, `BatchAgentDataModal.tsx` | Lookup by `batch_id` — unchanged |

**Out of scope:** **job_site** overwrite on failure ([AST-673](https://linear.app/astralcareermatch/issue/AST-673)), long-run hang ([AST-666](https://linear.app/astralcareermatch/issue/AST-666)), company-modal agent tabs, synthetic agent-data blocks, UI changes to the modal.

---

## Stage 1: Verified distinct job_site gate in `find_job_page`

**Done when:** `find_job_page` delegates to `jobs_found_process_job_site` only when the company row has a **job_site** URL that normalizes to a non-empty value **different from** **company_website**; when **job_site** is empty or equals **company_website**, the PJL discovery path is unchanged.

1. In `src/core/roster.py`, immediately above `find_job_page` (after `_job_site_for_persist`, ≈ line 1677), add:

   ```python
   def _is_verified_job_site_distinct(job_site: str, company_website: str) -> bool:
       """True when stored job_site is non-empty and not the same URL as company_website (Susan AC)."""
       js = _normalize_company_url_for_dedupe(job_site)
       cw = _normalize_company_url_for_dedupe(company_website)
       return bool(js) and js != cw
   ```

   Reuse existing `_normalize_company_url_for_dedupe` (≈ line 175) — do not add a second URL normalizer.

2. In `find_job_page` (≈ lines 1326–1330), replace the coarse redirect:

   ```python
   if pre_job_site:
       return await jobs_found_process_job_site(...)
   ```

   with:

   ```python
   if _is_verified_job_site_distinct(pre_job_site, company_website):
       logger.info(
           "[%s] find_job_page: stored job_site path (%s)",
           short_name,
           pre_job_site,
       )
       return await jobs_found_process_job_site(
           short_name, company_website, pre_job_site, debug=debug, ctx=ctx,
       )
   ```

3. Do **not** change `jobs_found_process_job_site`, `_find_job_page_from_assembled`, or `run_company_task` **JOBS_FOUND** branch — they already accept `ctx` and run the AST-469 chain.

4. Run `python3 -m py_compile src/core/roster.py`.

⚠️ **Decision:** Require **distinct** URLs (Susan parent AC + staging komodohealth brief), not merely non-empty **job_site**. When **job_site** equals **company_website**, fall through to PJL discovery so we do not scrape the homepage twice as a faux careers URL.

### Self-review (Stage 1 vs ASTRAL_CODE_RULES)

- **§1.3 DRY:** One helper; reuses `_normalize_company_url_for_dedupe`.
- **§2.6 state machine:** No new states; only entry routing.
- **§3.3 imports:** No new cross-layer imports.

---

## Stage 2: Observable no-LLM exits (AC #4)

**Done when:** Every `find_job_page` terminal path that returns **NO_JOBLIST** (or other failure) **without** calling `do_task` emits a single INFO log naming the reason, so Susan can distinguish “no LLM by design” from “LLM ran but agent_data missing.”

1. In `find_job_page`, at the early **NO_JOBLIST** block when `not possible_job_links or not nav_links` (≈ lines 1339–1347), **before** `_save_company`, add:

   ```python
   logger.info(
       "[%s] find_job_page: NO_JOBLIST without LLM — reason=no_pjl_or_nav "
       "pjl_count=%d nav_links_chars=%d verified_job_site=%s",
       short_name,
       len(possible_job_links),
       len(nav_links or ""),
       "yes" if _is_verified_job_site_distinct(pre_job_site, company_website) else "no",
   )
   ```

   Use `pre_job_site` already resolved above (do not re-fetch company).

2. At the **all PJL scrapes failed** block (≈ lines 1353–1361), add the same log shape with `reason=all_pjl_scrapes_failed` instead of `no_pjl_or_nav`.

3. Do **not** add synthetic **agent_data** rows or change Execution History UI — logs + existing batch log view are the AC #4 surface.

4. Run `python3 -m py_compile src/core/roster.py`.

### Self-review (Stage 2)

- **§1.5:** INFO only on production path; no debug-contract noise when `debug=False`.

---

## Stage 3: Agent_data batch_id audit on stored-URL path

**Done when:** Code review confirms (and tests/manifest lock) that when `find_job_page` dispatch runs the stored-URL path and invokes LLM steps, **agent_data** for **select_job_page** is keyed to the **entity** `batch_id` (`find_job_page-{uuid}`) on the Execution History row Susan clicked; **parse_job_list** hop data lives on the per-hop ledger row ([AST-528](https://linear.app/astralcareermatch/issue/AST-528)/[AST-531](https://linear.app/astralcareermatch/issue/AST-531)).

1. **Read-only audit** (no edit unless a gap is found):

   - `dispatcher._dispatch_one`: `has_run_next_chain = _current_agent_task_run_next("find_job_page")` must be **falsy** (confirm `agent_task.run_next` for `find_job_page` is blank in DB). When falsy, `log_batch_id.set(entity_batch_id)` before `run_company_task`.
   - `run_company_task` → `find_job_page(..., ctx=ctx)` → `jobs_found_process_job_site(..., ctx=ctx)` → `_find_job_page_from_assembled`: `merged_ctx = dict(ctx) if ctx else {}` then `resolve_run_next_live` — must preserve `astral_candidate_id` and `candidate_data` from dispatcher `ctx`.
   - `do_task("select_job_page", ..., ctx=merged_ctx)`: first hop `in_chain=False` → `batch_id = log_batch_id.get()` (= entity batch). `_should_store = store_agent_data and batch_id and entity_type` with `entity_type="company"` from **TASK_CONFIG** → prompt/response blocks stored under entity batch.
   - `do_task` `run_next` → `parse_job_list`: `in_chain=True` → `_open_run_next_hop_ledger` → child **agent_data** under `parse_job_list-{uuid}`; Susan inspects that row separately (existing product behavior).

2. **If audit finds `log_batch_id` unset** when `select_job_page` runs (e.g. `find_job_page` gained a DB `run_next` and dispatcher skipped entity ledger): in `_find_job_page_from_assembled`, before `await do_task("select_job_page", ...)`, add a guard:

   ```python
   from src.utils.logging import log_batch_id
   if ctx and ctx.get("entity_batch_id") and not log_batch_id.get():
       log_batch_id.set(ctx["entity_batch_id"])
   ```

   Only add this if the audit in step 1 proves it is needed — do not add preemptively.

3. After `jobs_found_process_job_site` successfully calls `do_task` (inside `_find_job_page_from_assembled`), existing `do_task` completion logs (`do_task(select_job_page) completed successfully batch_id=…`) are sufficient for AC #2–#3 — no duplicate roster logging.

4. Run `python3 -m py_compile src/core/roster.py` (and `src/core/agent.py` only if step 2 edit applied).

⚠️ **Decision:** Do not change **agent.py** hop-ledger design — per-hop **parse_job_list** batch_ids are intentional ([AST-528](https://linear.app/astralcareermatch/issue/AST-528)). AC #3 applies to the **find_job_page** entity row Susan clicked; that row must carry **select_job_page** blocks once the stored-URL path runs.

### Self-review (Stage 3)

- **§2.4 batch_id:** Uses existing `log_batch_id` / hop ledger — no parallel batch scheme.
- **§3.3:** Optional guard imports `log_batch_id` from `utils` only (allowed).

---

## Stage 4: Betty test manifest (qa-child — engineer does not edit `tests/`)

**Done when:** Betty's manifest covers AC 1–5 below; engineer runs manifest in **test-child**.

Add or extend tests in `tests/component/core/test_roster.py`:

| AC | Test intent |
|----|-------------|
| 1 | Company at **TO_WATCH** with distinct **job_site**, 0 PJLs, nav present → `find_job_page` calls `jobs_found_process_job_site` (mock), does **not** instant **NO_JOBLIST** solely for empty PJLs |
| 1 (neg) | **job_site** equals **company_website** → does **not** redirect; falls through to PJL path |
| 2–3 | Mock `do_task` for stored-URL path → assert `select_job_page` invoked with `ctx` containing dispatcher keys; assert `store_agent_data` path receives `log_batch_id` matching `entity_batch_id` (monkeypatch `log_batch_id`) |
| 4 | Mock empty PJL exit → assert INFO log contains `NO_JOBLIST without LLM` |
| 5 | Smoke: unrelated task `do_task` mock unchanged (no roster import side effects on consult path) — optional one-liner if existing suite already covers |

---

## Staging verification (Susan / UAT)

After **prep-uat** lands on staging:

1. Pick komodohealth (or equivalent) with **job_site** distinct from **company_website** and 0 PJLs.
2. Run **find_job_page** dispatch; confirm run duration > 1s when LLM path executes.
3. Open Execution History row `find_job_page-{uuid}` → agent-data modal shows **TASK** + **RESPONSE** for **select_job_page**.
4. If run legitimately skips LLM (no distinct **job_site**), batch logs show `NO_JOBLIST without LLM — reason=…`.

---

## Self-Assessment

**Scope:** `scope-Single-Component` — Touches `src/core/roster.py` entry routing and logging plus focused roster tests; optional one-line `log_batch_id` guard in roster only if audit requires it.

**Conf:** `conf-high` — AST-469 `jobs_found_process_job_site` path and AST-531 agent_data storage already exist on `origin/ftr/AST-669-…`; this ticket tightens the gate Susan specified and documents the batch_id contract.

**Risk:** `risk-Medium` — Wrong distinct-URL predicate could skip valid careers URLs or scrape homepages; mitigated by reusing `_normalize_company_url_for_dedupe` and Betty manifest cases; locate/parse chain is production-critical but unchanged when predicate matches.

### Self-review vs ASTRAL_CODE_RULES (plan-wide)

- **§1.3 DRY:** Reuses `_normalize_company_url_for_dedupe`, `jobs_found_process_job_site`, existing `do_task` chain.
- **§2.1 config:** No new config literals.
- **§2.4 batch:** Entity batch via `log_batch_id`; hop batch for `parse_job_list` unchanged.
- **§2.6 state machine:** No new states or transitions.
- **§3.3 imports:** Roster → agent via `do_task` only; no `agent` → `roster` import.
- **§3.5 naming:** `_is_verified_job_site_distinct` follows roster `_` helper convention.

No `conf-!!-NONE` conflicts identified.

---

## Review stub (Hedy / build)

**Publish ref:** `origin/sub/AST-669/AST-674-job-site-find-job-page-agent-data`  
**Product commits:** `d58c8900` (Stage 1 — `_is_verified_job_site_distinct` + distinct job_site redirect gate), `bfea6ed2` (Stage 2 — NO_JOBLIST without LLM INFO logs on both early-exit paths)  
**Stage 3 audit:** `dispatcher._dispatch_one` already sets `log_batch_id.set(entity_batch_id)` before `run_company_task` for `find_job_page`; no roster guard added.

---

## Radia review (2026-06-15)

**Diff:** `origin/dev...origin/sub/AST-669/AST-674-job-site-find-job-page-agent-data`  
**Verdict:** Clean — no fix-now items.

### What's solid

| Stage | Check |
|-------|-------|
| 1 | `_is_verified_job_site_distinct` reuses `_normalize_company_url_for_dedupe`; redirect gate matches plan and AC #1 |
| 2 | Both no-LLM **NO_JOBLIST** exits in `find_job_page` emit INFO with `reason=` + counts (AC #4) |
| 3 | `dispatcher._dispatch_one` sets `log_batch_id.set(entity_batch_id)` before `run_company_task`; no preemptive roster guard needed |
| 4 | Betty manifest (`TestJobSiteDistinct674`, `TestFindJobPageAst674`) covers AC 1–4 including entity `log_batch_id` on `select_job_page` |

### Advisory

- Sub tip includes **AST-676** / **AST-679** test-bible commits from `origin/tests` merge (`a0e02d28`, `d997407b`) — tests/docs only, no AST-674 product scope creep; harmless at merge time.
- `_is_verified_job_site_distinct` sits immediately above `find_job_page` (not after `_job_site_for_persist` per plan line hint) — better locality; no action.

### Recommended actions

None — **resolve-child** may proceed.

---

## Resolution (2026-06-15)

**Outcome:** — clean (no product changes; Radia review had no fix-now items).

**Publish ref:** `origin/sub/AST-669/AST-674-job-site-find-job-page-agent-data` @ `cd270ad5` (includes Radia `docs(AST-674): Radia review — clean`).

**§9a:** publish ref merges cleanly into `origin/dev` and `origin/ftr/AST-669-find-job-page-job-doesnt-display-the-agent-content`.
