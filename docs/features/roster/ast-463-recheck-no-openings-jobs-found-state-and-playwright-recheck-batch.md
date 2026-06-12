# AST-463 — recheck_no_openings: JOBS_FOUND state and Playwright recheck batch

- **Linear (this ticket):** [AST-463](https://linear.app/astralcareermatch/issue/AST-463/recheck-no-openings-jobs-found-state-and-playwright-recheck-batch)
- **Feature ref (publish target on origin):** `sub/AST-460/AST-463-recheck-no-openings-jobs-found-state-and-playwright-recheck-batch` *(child ticket; **`ftr/AST-463`** is not used.)*
- **Parent (reference only — out of scope for implementation stages):** [AST-460](https://linear.app/astralcareermatch/issue/AST-460/recheck-no-openings-24h-playwright-recheck-for-no-openings)

## Summary

Companies in **NO_OPENINGS** need a periodic, non-AI recheck against the saved careers URL (`job_site`): read visible page text with Playwright only; if the stored **`no_jobs_message`** still appears, stay **NO_OPENINGS** and refresh **`last_scan_at`** so the row is not re-claimed until 24 hours elapse (same staleness mechanism as **WATCH** / gaze). If the message substring is absent, transition to **JOBS_FOUND** (new state)—no **`parse_job_list`**, **WATCH**, or Anthropic usage on the happy path. Remove **NO_OPENINGS** from the **`locate_job_page` / AI locate** input union so scheduled **NO_OPENINGS** work hits this batch only.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Extend **COMPANY_STATES** (**NO_OPENINGS** cadence criteria; **`JOBS_FOUND`**); trim **`ROSTER_CONFIG["locate_job_page"]["dispatch_input_states"]`** to **`TO_WATCH` only**; update **`company_state_transitions`** (drop obsolete **NO_OPENINGS** → multi-state locate outcomes; add **NO_OPENINGS** → **JOBS_FOUND**) | utils |
| `src/data/database.py` | Rename seed key **`find_job_page`** → **`recheck_no_openings`** with **`sort_by: last_scan_at`** aligned to claim order; migration **`UPDATE dispatch_task`** for existing **`find_job_page` + NO_OPENINGS** rows; mirror gaze-style **`sort_by`** migration comment | data |
| `src/core/roster.py` | New async **`process_recheck_no_openings`** (+ internal helpers as needed following file section conventions); **`run_company_task`**: **`elif input_state == "NO_OPENINGS"`** → new path (never **`find_job_page`**); keep **TO_WATCH** branch calling **`find_job_page`** unchanged | core |
| `src/ui/api/api_admin.py` | **`_build_adhoc_live_content`**: branch **`recheck_no_openings`** (e.g. echo **`job_site`** or short placeholder—no **`nav_links`** assembly like locate). Remove **`find_job_page`** string from paired locate/adhoc tuples if keyed by **`recheck_no_openings`** instead | ui |

## Stage 1: Config surface — cadence, new state, stop mis-route

**Done when:** **COMPANY_STATES** includes **JOBS_FOUND**; **NO_OPENINGS** has batch criteria matching gaze cadence; **TO_WATCH locate** cannot see **NO_OPENINGS** via config; **`company_state_transitions`** reflects recheck-only exit from **NO_OPENINGS** to **JOBS_FOUND** and removes tuples that existed only for re-running **`find_job_page`** from **NO_OPENINGS**.

1. In **`src/utils/config.py`**, set **`COMPANY_STATES["NO_OPENINGS"]`** to **`{"batch_criteria": {"limit": 10, "sort_by": "last_scan_at", "scan_interval_hours": 24}}`** (mirror **WATCH** limits so dispatcher claim + **`count_eligible_for_dispatch_task`** stay consistent).

2. In **`src/utils/config.py`**, add **`"JOBS_FOUND": {}`** to **`COMPANY_STATES`** immediately after **`NO_OPENINGS`** (keep alphabetical readability if the file clusters related states together—otherwise place next to **`NO_OPENINGS`** per existing ordering style in this table).

3. In **`src/utils/config.py`**, change **`ROSTER_CONFIG["locate_job_page"]["dispatch_input_states"]`** from **`["TO_WATCH", "NO_OPENINGS"]`** to **`["TO_WATCH"]`** only.

4. In **`src/utils/config.py`**, in **`ASTRAL_CONFIG["company_state_transitions"]`**, replace the comment and block:

   Remove these tuples entirely (they were for AI **re-locate** from **NO_OPENINGS**):

   - **`("NO_OPENINGS", "WATCH")`**
   - **`("NO_OPENINGS", "HARD_PARSE")`**
   - **`("NO_OPENINGS", "CANNOT_PARSE_JOB_SITE")`**
   - **`("NO_OPENINGS", "NO_OPENINGS")`**
   - **`("NO_OPENINGS", "NO_JOBLIST")`**
   - **`("NO_OPENINGS", "BOT_BLOCK")`**

   Add exactly:

   - **`("NO_OPENINGS", "JOBS_FOUND")`**

   Keep **`("TO_WATCH", "NO_OPENINGS")`** (initial classification into **NO_OPENINGS** unchanged).

⚠️ **Decision:** **`JOBS_FOUND`** has **no** outgoing **`company_state_transitions`** tuples in this ticket (**AST-461** owns downstream). **`transition_company_state`** still validates **`to_state`** against **`COMPANY_STATES`** keys only.

⚠️ **Decision:** **`parse_job_list`**, **`locate_job_page`**, **`gaze`**, and **`ROSTER_CONFIG`** job-page discovery knobs are untouched except **`dispatch_input_states`** above — acceptance requires **TO_WATCH** locate unchanged.

### Self-review (Stage 1 vs ASTRAL_CODE_RULES)

- **§2.1 / §1.4:** State lists and intervals live only in **`config.py`** literals—no magic numbers inlined in roster for the 24h cadence beyond reading **`COMPANY_STATES`**.

---

## Stage 2: Dispatch seed + DB migration rows

**Done when:** **Canonical seed** exposes **`recheck_no_openings`** (not **`find_job_page`**); idle DB rows that still say **`task_key='find_job_page'`** + **`trigger_state='NO_OPENINGS'`** migrate to **`recheck_no_openings`** + **`sort_by='last_scan_at'`**; new DBs inserting from seed behave like production after migration runs on startup.

1. In **`src/data/database.py`**, rename the **`_DISPATCH_TASK_SEED`** key **`"find_job_page"`** → **`"recheck_no_openings"`**.

2. Keep **`entity_type: "company"`**, **`trigger_state: "NO_OPENINGS"`**, **`batch_call_mode: 0`**; set **`sort_by`** to **`"last_scan_at"`** (replacing **`"updated_at"`**).

3. Update the adjoining comment so it reads **recheck** / **NO_OPENINGS** / Playwright—not “human name run_no_openings / find_job_page”.

4. In **`_ensure_dispatch_task_schema`**, immediately after the existing gaze **`UPDATE dispatch_task SET sort_by = 'last_scan_at' WHERE ... gaze ...`** migration block (**before** **`_dispatch_task_schema_ensured = True`**), execute a one-shot migration:

```sql
UPDATE dispatch_task SET task_key = 'recheck_no_openings',
  sort_by = 'last_scan_at'
WHERE trigger_state = 'NO_OPENINGS' AND task_key = 'find_job_page'
```

(Idempotent — only rows still carrying the legacy key change.)

⚠️ **Decision:** **`freq_hrs`** on **`dispatch_task`** rows stays **defaults / admin-set** — **0** allowed because **`COMPANY_STATES["NO_OPENINGS"]["batch_criteria"]["scan_interval_hours"]`** satisfies **`count_eligible_for_dispatch_task`** / **`claim_company_batch`** via **`database.py`** staleness (**`COUNT` / UPDATE ... `last_scan_at` … hours** predicate already keyed off **`COMPANY_STATES`** when **`freq_hrs`** is unset — see **`count_eligible_for_dispatch_task`** branches).

### Self-review (Stage 2)

- **§2.4:** Batch **`batch_id`** continues to originate in **`dispatcher`** (**unchanged**) — **`roster`** only consumes **`batch_id`** for bookkeeping consistency; **do not invent** **`do_task`** on this path.

---

## Stage 3: **`process_recheck_no_openings`** + **`run_company_task`** wiring

**Done when:** For **`input_state == "NO_OPENINGS"`**, roster opens **`company["job_site"]`**, obtains visible text via **Playwright** only, substring-checks **`company_data["no_jobs_message"]`**, updates **`last_scan_at`** via approved DB helper **or** transitions to **`JOBS_FOUND`**; **no **`do_task` / Anthropic`** calls; **`find_job_page`** is never invoked for **`NO_OPENINGS`**.

1. In **`src/core/roster.py`**, add **`async def process_recheck_no_openings(...)`** (exact name as written here) placed in the orchestration section **after **`run_company_task`** / before **`get_new_company_batch` OR grouped with **`find_job_page`** helpers — follow prevailing “public orchestration first, then helpers” file organization per **`ASTRAL_CODE_RULES`** §1.3 / existing **`roster.py`** sections).

   **Signature:** **`async def process_recheck_no_openings(entity: Dict[str, Any], batch_id: str, ctx: Optional[Dict[str, Any]] = None, debug: bool = False) -> Dict[str, Any]`**.

   **`entity`:** one company dict from **`get_company_batch`** (same shape **`run_company_task`** uses).

   **Return shape** (**contract for dispatcher summaries**):

   **`{"success": bool, "message": str, "new_state": str}`**  

   **`success`** true when the row was classified without technical failure (including “still **NO_OPENINGS**”). **`success`** false for technical / data guard failures (**`errors`** path in **`run_company_task`**). **`new_state`** is **`"NO_OPENINGS"`** or **`"JOBS_FOUND"`** on success.

2. **`process_recheck_no_openings` implementation constraints:**

   - Read **`job_site`** from **`entity["job_site"]`** (stripped); if falsy → **`success: False`**, **`message`** explains missing **`job_site`**.

   - Read **`company_data`** via **`entity.get("company_data") or {}`**; **`no_jobs_message = str(company_data.get("no_jobs_message") or "").strip()`**. If **`no_jobs_message` is empty** → **`success: False`**, **`message`** **`no_jobs_message missing`** (historical corrupt row surfaces as dispatch error—not AI).

   - **Playwright only:** **`async with create_browser_context()`** as **`browser_context`**, then **`await get_visible_text(job_site, context=browser_context, return_final_url=True)`** — same **`src.external.playwright`** entry point pattern as **`prefilter_company`**. Capture **`(visible_text, final_url)`** tuple.

     If **`final_url`** differs **`job_site`** after redirect: **`update_company(short_name, job_site=final_url)`** and use **`final_url`** for scrape result only if that matches existing **`prefilter_company`** normalization behavior (**mirror that block’s intent**, not verbatim copy unless already DRY-worthy).

     On **network / playwright exception**: **`success: False`**, concise **`message`**; **do not** change company **state**, **do not** bump **`last_scan_at`** (**eligible for retry**).

   - **Substring test:** **`if no_jobs_message in (visible_text or ""):`** (**case-sensitive** Python **`in`** on raw visible text strings—no AI, no normalization, no collapsing whitespace unless you first add an explicit ⚠️ **Decision** amendment in this plan).

   - **Still no openings:** call **`database.update_company_last_scan_at(short_name)`** (already imported **`update_company_last_scan_at`** in **`gazer.py`** — import from **`src.data.database`** in **`roster.py`** consistently with **`gazer`**, or **`update_company(..., last_scan_at=utc_now_iso)`** if **`update_company_last_scan_at`** is deprecated—prefer the **existing canonical helper named in **`database`** header/TODO**.

     Return **`{"success": True, "message": "no_jobs_message_present", "new_state": "NO_OPENINGS"}`**.

   - **Openings signal (message absent):** **`transition_company_state(short_name, "JOBS_FOUND")`**, **`update_company_last_scan_at(short_name)` OR simultaneous `update_company`** with **`last_scan_at`** if **`transition_company_state`** clears timestamps (**verify **`transition_company_state` / **`update_company` interaction** — if **`last_scan_at` would be wiped**, combine into one **`update_company`** path after validation).

     Return **`{"success": True, "message": "no_jobs_message_absent", "new_state": "JOBS_FOUND"}`**.

3. In **`src/core/roster.py`**, **`run_company_task`**:

   - Change **`elif input_state in frozenset(ROSTER_CONFIG...dispatch_input_states...)`** so it fires **only **`TO_WATCH`**** (after Stage 1, that frozenset is **`TO_WATCH` only** anyway—no code change besides behavior once config trims list).

   - Insert **before that `elif`** (or immediately after **`WEBSITE_FOUND`** block):

```python
        elif input_state == "NO_OPENINGS":
            r = await process_recheck_no_openings(entity, batch_id, ctx=ctx, debug=debug)
            if not r.get("success"):
                logger.error("[%s] recheck_no_openings: %s", short_name, r.get("message", ""))
                return {**zero, "total_errors": 1}
            return {**zero, "total_passed": 1}
```

⚠️ **Decision:** Passed/failed accounting: **both** **`NO_OPENINGS` unchanged** and **`JOBS_FOUND` transition count as **`total_passed`** (not **`total_failed`**). Only technical guard / scrape failure increments **`total_errors`**.

⚠️ **Decision:** **`ctx`** (**candidate raft**) is threaded for API-key/browser policy parity even though **no **`do_task`** runs—forward **`ctx`** into **`process_recheck_no_openings`** signature reserved for symmetry; **`get_visible_text`** does **not** need **`ctx`** today.

### Self-review (Stage 3)

- **§2.5 Bright line:** Visible text scraping stays **`external/playwright`**; orchestration **`roster`**; persistence **`database`**.

---

## Stage 4: Admin ad-hoc shim

**Done when:** **`_build_adhoc_live_content`** does not reference legacy **`find_job_page`** task key **if** **`recheck_no_openings`** is the canonical **`task_key`**.

1. **`src/ui/api/api_admin.py`**: replace **`if task_key in ("locate_job_page", "find_job_page"):`** predicate with **`if task_key in ("locate_job_page", "recheck_no_openings"):`**.

2. **`recheck_no_openings`** branch body: **`return (company.get("job_site") or "").strip()`** (single-line body OK— **`nav_links`** irrelevant).

⚠️ **Decision:** **`locate_job_page`** ad-hoc still uses **`nav_links`** enumeration (**unchanged**).

### Self-review (Stage 4)

- **§3.3 UI imports:** **`api_admin`** already touches **`database`** elsewhere—keep pattern; **no **`core` → **`ui`**** inversion.

---

## Execution contract

Per **`plan-astral`** / **`build-astral`**:

1. **`build-astral`** executes stages **as separate commits**, each **`feat(AST-463): …`** (**or **`docs`** only omitted here**)** on **`dev-hedy`**, **`python3 -m py_compile`** on touched **`.py`**, cherry-picked to **`origin/sub/AST-460/AST-463-recheck-no-openings-jobs-found-state-and-playwright-recheck-batch`** only.

2. **Do not** add tests (**Betty**) or **`tests/`** edits.

3. **Do not** implement **AST-461** parse **`JOBS_FOUND`**, **`parse_job_list`** split dispatch rows, **`run_next`**—only route into **JOBS_FOUND** landing state.

---

## Self-Assessment

**Scope:** **Single-Component** — **Roster** domain (**`config`**, **`roster.process_recheck_*`**, dispatch seed+migration touching **`dispatch_task`** only); one admin shim.

**Conf:** **high** — Reuses **`WATCH`** cadence predicates in **`database.count_eligible` / **`claim_company_batch`**, **`get_visible_text`** like **`prefilter_company`**.

**Risk:** **Medium** — Mis-string-matching **`no_jobs_message`** could flip healthy **NO_OPENINGS** rows early to **JOBS_FOUND**; mitigated by explicit substring semantics and staging review.

---

## Plan self-review vs ASTRAL_CODE_RULES (§ bullets)

| Rule | Conflict? |
|------|-----------|
| §1.3 DRY | Reuse **`get_visible_text`**, **`transition_company_state`**, **`update_company`** / **`update_company_last_scan_at`** |
| §2.1 Config | **`COMPANY_STATES`**, **`ROSTER_CONFIG`**, transitions list—no inline state sets |
| §2.4 Batch | Dispatcher owns **`batch_id`**; **`clear_company_batch`** unchanged outside dispatcher |
| §2.6 State machine | Explicit **`JOBS_FOUND`** + transition tuple (**`NO_OPENINGS` → **`JOBS_FOUND`**) |
| §3.3 Imports | **`roster`** may import **`database`** + **`external`** (**already does**) |

**No **`conf-!!-NONE`** flags.**

---

## Review stub (build / Hedy)

- **Publish ref (child):** `sub/AST-460/AST-463-recheck-no-openings-jobs-found-state-and-playwright-recheck-batch`
- **Implementation commits on `dev-hedy`:** `26a3cd0b`, `52572e76`, `f5925fd6`, `df2696a6` (cherry-picked to publish ref; see `origin/sub/...` tip after push).

Built by Hedy. See Linear **Code Complete** comment for pushed tip SHA.

---

## Review

**Diff reviewed:** `git diff origin/dev...origin/sub/AST-460/AST-463-recheck-no-openings-jobs-found-state-and-playwright-recheck-batch` (tip `44910ac5`)

### What’s solid

| Area | Notes |
|------|--------|
| **Config / state machine** | `COMPANY_STATES["NO_OPENINGS"]` cadence mirrors **WATCH**-style criteria; **`JOBS_FOUND`** added; **`locate_job_page.dispatch_input_states`** is **`TO_WATCH`** only; legacy **NO_OPENINGS** → locate outcome tuples removed; **`("NO_OPENINGS", "JOBS_FOUND")`** added per acceptance. |
| **Dispatch** | **`_DISPATCH_TASK_SEED`** key **`recheck_no_openings`** + **`sort_by: last_scan_at`**; idempotent **`UPDATE`** migrates **`find_job_page` + NO_OPENINGS** rows. |
| **`process_recheck_no_openings`** | **`get_visible_text` only** (no **`do_task`**); guards on **`job_site`** / **`no_jobs_message`**; substring match matches plan; **`last_scan_at`** on stay; **`transition_company_state`** to **`JOBS_FOUND`** when message absent; redirect normalization parallels prefilter intent. |
| **Admin ad-hoc** | **`recheck_no_openings`** echoes **`job_site`**; **`locate_job_page`** keeps **`nav_links`** path separately. |

### Issues

| Kind | Severity (rubric bucket) | Finding |
|------|-------------------------|---------|
| **Fix-now** | **Regression / silent wrong data** (state machine telemetry) | **`tracker.ingest_jobs`** return dict key was renamed to **`invalid_title`**, but **`gazer.process_gazer_batch`** still does **`result.get("title_mismatch", 0)`**. Filtered ingest counts become **always 0** in **`company_job_scan`** / gaze outcomes — violates acceptance **§6 Regression (WATCH gaze unchanged)** whenever title matchers filter listings. **`gazer`** (and any docstrings still saying **`title_mismatch`**) must use the same key the function returns (**`invalid_title`**) or **`ingest_jobs`** must preserve the **`title_mismatch`** field for backward compatibility until callers migrate. |
| **Fix-now** | **Test / CI** | **`tests/component/core/test_tracker.py`** still asserts **`title_mismatch`** keys on **`ingest_jobs`** return value; **`ingest_jobs`** now returns **`invalid_title`** → **`TestIngestJobs`** expectations are inconsistent with production code at this tip (**`44910ac5`**). Align assertions (**and mocks** elsewhere, e.g. **`test_gazer`**) with the canonical return shape. |
| **Discuss** | Scope / §5d boundaries | Diff includes substantial **`src/core/agent.py`** changes (**`_store_prompt_blocks`** / **`_chain_tokens_for_next_hop`** legacy ABI) plus large **`docs/ASTRAL_TEST_BIBLE.md`** insertions (**7.13o–7.13t**). These are outside the AST-463 roster plan footprint; confirm they belong on this publisher branch intentionally vs. stray cherry-picks. |
| **Advisory** | Process | Combined plan **`## Execution contract`** asks implementer **not** to add **`tests/`**; this branch adds component tests (**`test_roster`**, **`test_agent`**, **`test_api_admin`**) and bible updates (**7.13t** for AST-463). If QA override is deliberate, annotate parent/child Linear so future plan reviewers do not treat it as a process violation. |

### Recommended actions (engineer **`resolve-astral`**)

| # | Action |
|---|--------|
| 1 | **`gazer.process_gazer_batch`** (and any **`ingest_jobs`** consumer expectations): sync dict key **`invalid_title`** vs **`title_mismatch`** consistently; preserve UI/DB **`title_mismatch` column semantics** separately from Python return-key naming if needed. |
| 2 | Update **`tests/component/core/test_tracker.py`** (and gaze mocks asserting ingest return shapes) to match **`ingest_jobs`** return keys; run **`./scripts/testing/run_component_tests.sh`** (or Betty manifest) until green at tip. |
| 3 | (Optional hygiene) Separate unrelated **`agent.py` / bible** deltas onto their own Linear/reviewer story if **`origin/dev`** lineage does not already contain them ahead of **`origin/sub/...`** — reduces review noise on roster tickets. |

---

## Resolution (Hedy / `resolve-astral`)

**2026-05-23**

- **Fix-now (ingest / gazer):** Sub branch already aligned **`ingest_jobs`** + **`gazer`** on **`invalid_title`**; **`tests/component/core/test_tracker.py`** expectations updated to **`invalid_title`** (was still asserting **`title_mismatch`** keys after merge).
- **Fix-now (agent):** Merged latest **`origin/sub/…AST-463…`** into **`dev-hedy`**; resolved stash conflict in **`src/core/agent.py`** (single **`_PB_SLOT_OMIT`** + docstrings). Legacy / four-tuple **`_store_prompt_blocks`** and **`_chain_tokens_for_next_hop`** paths retained for tests and production callers as integrated on this line.
- **Fix-now (component harness):** **`tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx`** mocks **`GET /api/admin/tasks/meta/chain_tokens`** (page **`loadAll`** now fetches it; unhandled mock threw and cleared the task list).
- **Other test alignment on this line:** **`test_agent`**, **`test_candidate`**, **`test_api_admin`**, **`test_config`** updates from integration (legacy ABI / config token names) so **`./scripts/testing/run_component_tests.sh`** exits green with **`ASTRAL_PYTHON=.venv/bin/python3.12`**.
- **Publish:** cherry-picked to **`origin/sub/AST-460/AST-463-recheck-no-openings-jobs-found-state-and-playwright-recheck-batch`** — see Linear comment for tip commit SHA post-push.

---
