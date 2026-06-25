<!-- linear-archive: AST-505 archived 2026-06-15 -->

## Linear archive (AST-505)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-505/discovery-search-vet-slugs-and-ingest-new-companies-roster-inflow  
**Status at archive:** Done  
**Project:** Astral Roster  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-490 — Roster inflow  
**Blocked by / blocks / related:** parent: AST-490; blocks: AST-506

### Description

## What this implements

Phase 1 of roster inflow: weekly per-candidate Google CSE discovery (100 results, 7-day date restrict, no site filters), AI vetting (slug / ignore / optional URL), **ingest_new_companies** with candidate-scoped URL pattern-match dedupe, and **NEW** company state. Uses existing dispatch/scheduler patterns (gaze-like cadence).

## Acceptance criteria

2. Phase 1 dispatch runs weekly per candidate (7-day scan interval) via task dispatcher configuration.
3. Phase 1 executes general Google CSE searches (no site filters), up to 100 results, with 7-day date restrict, using terms from the artifact.
4. Phase 1 vetting returns slug, ignore, and optional URL per hit; ignored hits do not create company rows.
5. ingest_new_companies creates **NEW** rows for accepted hits; URL pattern-match dedupe skips companies whose URLs already exist on the **candidate's** roster.
6. When Phase 1 supplies a URL, the company reaches **WEBSITE_FOUND** without Phase 2 dispatch.

## Boundaries

* Phase 2 website resolution — sibling ticket.
* **IMPORTED** manual path unchanged.
* No new DB columns without Susan flag (AST-490 pattern fidelity).

## Notes for planning

* Google CSE: AST-489 `search_google_cse` in external layer.
* Gazer/dispatch patterns — not a parallel orchestration model.
* Hot-file overlap with AST-491 on `origin/dev`; merge `origin/dev` into sub before publish.

## Git branch (authoritative)

`sub/AST-490/AST-505-discovery-search-vet-slugs-ingest-new-companies`

### Comments

#### radia — 2026-05-28T00:11:13.944Z
**Review** — `origin/dev...origin/sub/AST-490/AST-505-discovery-search-vet-slugs-and-ingest-new-companies` (tip `fcda6d67`)

Doc: `docs/features/roster/ast-505-discovery-search-vet-slugs-and-ingest-new-companies-roster-inflow.md` § Review (`fcda6d67`)

### fix-now

- **`src/core/roster.py` L34** — imports `company_search_terms_lines` from `src.core.candidate`, but that symbol is **not on this publish ref** (lives on **AST-504** sub only). **ImportError at module load** until AST-504 is on the integration line or cherry-picked here. Plan noted the dependency; ref is not self-contained.

### discuss

- **`database._candidate_search_term_lines` vs AST-504 `company_search_terms_lines`** — data-layer mirror is intentional; after AST-504 merge, two parsers exist — drift could split eligibility vs batch if normalization changes.
- **`consult.run_consult_task` candidate branch** — routes all `entity_type == "candidate"` to inflow discovery with no `task_key` guard. OK while `inflow_discovery` is the sole candidate task.

### advisory

- **`consult.py` lazy import** — add cycle-break comment (cf. `board_search`) — B1 polish.
- **`run_inflow_discovery_batch`** — `batch_id` / `debug` unused.
- **UAT:** Admin `vet_inflow_discovery` prompt row; **AST-504** before live dispatch.

### solid

Config/dispatch seed, `INFLOW_CONFIG`, `NEW` + transitions, weekly eligibility, dispatcher candidate routing (no company clear), CSE→vet→ingest, URL/slug dedupe, `NEW`/`WEBSITE_FOUND` branching, tests §7.13zg — align with plan and acceptance criteria. `IMPORTED` untouched; layers clean in diff.

#### betty — 2026-05-28T00:01:20.555Z
**QA manifest** — run on `origin/sub/AST-490/AST-505-discovery-search-vet-slugs-and-ingest-new-companies` @ `102e2acf`

1. `./scripts/testing/run_component_tests.sh tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig`
2. `./scripts/testing/run_component_tests.sh tests/component/data/database/test_dispatch_tasks.py::TestAst505InflowDiscoveryEligible`
3. `./scripts/testing/run_component_tests.sh tests/component/core/test_dispatcher.py::TestRunUnified::test_ast505_candidate_entity_routes_ctx_without_company_clear`
4. `./scripts/testing/run_component_tests.sh tests/component/core/test_roster.py::TestAst505InflowDiscovery`

`docs/ASTRAL_TEST_BIBLE.md` shasum on publish ref: `376263c591b1895e3415fea14d7e813878a9a266f6e8ed8e7673a8fbed929d84` (§7.13zg)

**Blocker note:** Phase 1 depends on **AST-504** search-terms artifact on the integration line for live dispatch/UAT; manifest above is Phase 1 test coverage only.

**Integration heads-up:** On `dev-betty` with **AST-507** merged alongside **AST-505**, `roster` ↔ `consult` top-level imports can circular-import when `test_consult` loads first — consult routing for candidate is covered in `TestAst505InflowDiscovery::test_consult_routes_candidate_entity` instead.

#### hedy — 2026-05-27T23:47:26.523Z
**Blocked:** AST-504 (Company search terms artifact and craft task) is **Plan Approved**, not **Code Complete**. Phase 1 discovery depends on the Phase 0 search-terms artifact and craft task.

**Needed:** AST-504 build → Code Complete before this ticket can proceed.

**Publish ref (unchanged):** `origin/sub/AST-490/AST-505-discovery-search-vet-slugs-and-ingest-new-companies`

#### hedy — 2026-05-27T23:43:47.327Z
Plan: `docs/features/roster/ast-505-discovery-search-vet-slugs-and-ingest-new-companies-roster-inflow.md`

https://github.com/susansomerset/astral/blob/sub/AST-490/AST-505-discovery-search-vet-slugs-and-ingest-new-companies/docs/features/roster/ast-505-discovery-search-vet-slugs-and-ingest-new-companies-roster-inflow.md

**Self-assessment**
- **Scope:** `MAJOR-CHANGE` — config + dispatch candidate entity type, consult routing, roster CSE/vet/ingest, and `NEW` company state.
- **Conf:** `Medium` — reuses AST-489 CSE and dispatch patterns, but task-level weekly cadence (`freq_hrs` + `last_run_at`) and candidate `entity_type` are new.
- **Risk:** `Medium` — slug/URL dedupe mistakes duplicate or drop companies; does not touch manual `IMPORTED` path.

Build blocked until **AST-504** (`company_search_terms_lines`) is on the integration line. Publish ref cherry-pick: `49883c9b`.

---

# AST-505 — Discovery search, vet slugs, and ingest NEW companies (Roster inflow)

- **Linear:** [AST-505](https://linear.app/astralcareermatch/issue/AST-505/discovery-search-vet-slugs-and-ingest-new-companies-roster-inflow)
- **Parent (coordination only):** [AST-490](https://linear.app/astralcareermatch/issue/AST-490/roster-inflow)
- **Publish ref:** `origin/sub/AST-490/AST-505-discovery-search-vet-slugs-and-ingest-new-companies`
- **Blocked by (build gate):** [AST-504](https://linear.app/astralcareermatch/issue/AST-504/company-search-terms-artifact-and-craft-task-roster-inflow) — **`company_search_terms_lines`** + artifact string must exist before Phase 1 runs.

## Summary

Phase 1 roster inflow: a **weekly per-candidate** schedulable dispatch task reads newline search terms from **`candidate_data.artifacts.company_search_terms`** (AST-504), runs **general Google CSE** (up to **100** hits per term, **`dateRestrict` 7 days**, **no site filters**), calls a new AI task to **vet** each hit (**slug + optional URL**, or **ignore**), then **`ingest_new_companies`** creates roster rows with candidate-scoped **URL pattern-match dedupe**. Companies without a vetted URL land in **`NEW`**; companies with a vetted URL transition directly to **`WEBSITE_FOUND`** (Phase 2 skipped). Uses existing **dispatcher → consult → roster** patterns — not a parallel orchestrator.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | **`INFLOW_CONFIG`** literals; **`COMPANY_STATES["NEW"]`**; company transitions **`NEW → WEBSITE_FOUND`**, **`NEW → NO_WEBSITE`** (Phase 2 sibling consumes **`NO_WEBSITE`** path); **`TASK_CONFIG["vet_inflow_discovery"]`**; dispatch mirror keys **`inflow_discovery`** | utils |
| `src/data/database.py` | **`_DISPATCH_TASK_SEED["inflow_discovery"]`**; optional **`count_candidate_inflow_discovery_eligible(candidate_id, freq_hrs, last_run_at)`** helper colocated with dispatch helpers | data |
| `src/core/dispatcher.py` | **`entity_type == "candidate"`** branch in **`_run_unified`**; pass **`freq_hrs` / `last_run_at`** cadence into eligibility for candidate tasks | core |
| `src/core/consult.py` | Route **`entity_type == "candidate"`** + **`input_state == "LIVE_PROMPTS"`** (see Stage 2) to roster | core |
| `src/core/roster.py` | **`run_inflow_discovery_batch`**, **`ingest_new_companies`**, URL dedupe helper | core |
| `src/core/candidate.py` | **Import only at runtime** — call **`company_search_terms_lines(ctx)`** from AST-504 (no duplicate split logic) | core |

**Tests:** Betty owns **`tests/`** and **`ASTRAL_TEST_BIBLE.md`** — engineer does **not** add test files in **build-astral** unless Betty’s manifest already lists them.

## Stage 1: Config, company state, and dispatch seed

**Done when:** **`NEW`** is a valid company state; **`INFLOW_CONFIG`** holds Phase 1 numeric literals; **`vet_inflow_discovery`** exists in **`TASK_CONFIG`**; **`inflow_discovery`** appears in **`_DISPATCH_TASK_SEED`** and **`config._DISPATCH_TASK_TRIGGER_SEED`** / **`DISPATCH_TASK_SEED_KEYS`** in the **same commit**.

1. In **`src/utils/config.py`**, after **`ROSTER_CONFIG`**, add **`INFLOW_CONFIG`**:

```python
INFLOW_CONFIG = {
    "discovery": {
        "max_results_per_query": 100,
        "date_restrict_days": 7,
        "dispatch_freq_hrs": 168,  # 7-day weekly cadence per candidate
        "dispatch_trigger_state": "LIVE_PROMPTS",
        "task_key": "inflow_discovery",
        "vet_task_key": "vet_inflow_discovery",
    },
}
```

2. In **`COMPANY_STATES`**, add **`"NEW": {}`** (no **`batch_criteria`** yet — Phase 2 adds claim criteria on **`NEW`** without URL).

3. In **`ASTRAL_CONFIG["company_state_transitions"]`**, append (do **not** remove **`IMPORTED`** manual paths):

   - **`("NEW", "WEBSITE_FOUND")`**
   - **`("NEW", "NO_WEBSITE")`** — consumed by **AST-506**; include now so state machine stays consistent.

4. In **`TASK_CONFIG`** (Phase **C. Company Roster**), after **`find_company_website`**, add **`vet_inflow_discovery`**:

   - **`phase`**: **`"C. Company Roster"`**
   - **`seq`**: **`1.5`** is invalid — use **`seq`: `7`** (after **`parse_job_list`** seq 6) or next free integer in that phase; **must be unique**.
   - **`response_format`**: **`"json"`**
   - **`entity_type`**: **`"candidate"`**
   - **`requires_candidate_key`**: **`True`**
   - **`context_format`**: **`"vet_inflow_discovery_{index}"`**
   - **`response_schema`**:

```python
"results": {
    "type": "list",
    "required": True,
    "items_schema": {
        "hit_index": {"type": "int", "required": True},
        "action": {"type": "str", "required": True},  # literal "slug" or "ignore"
        "short_name": {"type": "str", "required": False},
        "website": {"type": "str", "required": False},
    },
},
```

5. In **`database._DISPATCH_TASK_SEED`**, add **`inflow_discovery`**:

```python
"inflow_discovery": {
    "entity_type": "candidate",
    "trigger_state": "LIVE_PROMPTS",
    "sort_by": "updated_at",
    "batch_call_mode": 0,
},
```

6. Mirror in **`config._DISPATCH_TASK_TRIGGER_SEED`**: **`"inflow_discovery": {"trigger_state": "LIVE_PROMPTS", "entity_type": "candidate"}`**.

⚠️ **Decision:** Weekly cadence uses **`dispatch_task.freq_hrs = 168`** plus **`dispatch_task.last_run_at`** (task-level cooldown), **not** company **`last_scan_at`**. Candidate discovery is one run per candidate per interval — unlike **`WATCH`** gaze entity cadence.

⚠️ **Decision:** **`trigger_state: LIVE_PROMPTS`** means only candidates who finished profile setup are eligible; matches craft artifact gating on AST-504. If candidate is not **`LIVE_PROMPTS`**, **`available_count`** is **0**.

### Self-review (Stage 1)

| Rule | OK? |
|------|-----|
| §2.1 config | Literals in **`INFLOW_CONFIG`** / **`TASK_CONFIG`** only |
| §2.6 state machine | Transitions appended; **`IMPORTED`** path untouched |
| §1.4 magic numbers | No inline **100** / **7** / **168** outside config |

---

## Stage 2: Candidate dispatch eligibility and runner wiring

**Done when:** AUTO **`inflow_discovery`** rows show **`available_count == 1`** when terms exist and **`last_run_at`** is stale (or null); **`available_count == 0`** when terms missing or inside **`freq_hrs`** window; clicking Run executes one discovery batch and updates **`last_run_at`**.

1. In **`src/data/database.py`**, add **`count_candidate_inflow_discovery_eligible(candidate_id: str, freq_hrs: float, last_run_at: Optional[str]) -> int`**:
   - Return **0** if **`candidate_id`** blank.
   - Load candidate via **`get_candidate(candidate_id)`**; return **0** if missing or **`state != INFLOW_CONFIG["discovery"]["dispatch_trigger_state"]`** (import constant from config at call site).
   - Return **0** if **`company_search_terms_lines(candidate_data)`** (from **`src.core.candidate`**) is empty — **requires AST-504 merged on integration line before build/test**.
   - If **`freq_hrs > 0`** and **`last_run_at`** parses to within **`freq_hrs`** hours of now (UTC, same datetime style as other dispatch helpers), return **0**.
   - Else return **1**.

2. In **`count_eligible_for_dispatch_task`**, before the **`entity_type == "company"`** branch, add:

```python
if entity_type == "candidate":
    freq = float(task.get("freq_hrs") or 0)
    eff_freq = freq if freq > 0 else float(INFLOW_CONFIG["discovery"]["dispatch_freq_hrs"])
    return count_candidate_inflow_discovery_eligible(
        candidate_id, eff_freq, task.get("last_run_at"),
    )
```

3. In **`src/core/dispatcher.py`** **`_run_unified`**, after **`board_search`** branch and before **`job`** branch, add **`elif entity_type == "candidate":`**:
   - Do **not** call **`get_new_company_batch`**.
   - Set **`entities = [ctx]`** (candidate dict already loaded in **`_dispatch_one`** — must include **`candidate_id`**, **`state`**, **`candidate_data`**).
   - Skip claim/clear company batch in **`finally`** for this entity type (add **`elif entity_type == "candidate": pass`** before company clear, or guard **`clear_company_batch`**).

4. In **`src/core/consult.py`** **`run_consult_task`**, after **`board_search`** branch, add:

```python
if entity_type == "candidate":
    from src.core import roster
    return await roster.run_inflow_discovery_batch(
        entities[0], batch_id, ctx, debug,
    )
```

5. Default **`freq_hrs`** on new **`inflow_discovery`** **`dispatch_task`** rows: document in builder comment that Susan sets **`168`** on insert (seed does **not** embed **`freq_hrs`** — matches other seeds); admin template copy from an existing **`gaze`** row is acceptable when creating the first row per candidate.

### Self-review (Stage 2)

| Rule | OK? |
|------|-----|
| §2.4 batch | Single candidate entity per run; ledger + **`last_run_at`** unchanged |
| §3.3 imports | **`consult → roster`**, **`database → candidate`** helper only |

---

## Stage 3: CSE search, vet task, and ingest

**Done when:** Manual dispatch run with populated search terms creates **`NEW`** or **`WEBSITE_FOUND`** companies; ignored hits create no rows; duplicate URLs on the candidate roster are skipped; second run within 7 days does not execute ( **`available_count` 0** ).

1. In **`src/core/roster.py`**, add **`_normalize_company_url_for_dedupe(url: str) -> str`**:
   - Strip; if empty return **`""`**.
   - Delegate to **`src.external.playwright.normalize_url`** (already used for URL comparison elsewhere).
   - Additionally strip **`www.`** from netloc if present after normalize (document in one-line comment — dedupe is host-level for roster ingest).

2. Add **`_candidate_company_urls(candidate_id: str) -> set[str]`**:
   - Query **`list_companies`** or **`database`** helper scoped to **`candidate_id`**.
   - Collect normalized URLs from **`company_website`** and **`job_site`** when non-empty.

3. Add **`ingest_new_companies(candidate_id: str, slug: str, website: Optional[str], *, source_hit: Optional[dict] = None) -> bool`**:
   - **`slug`**: strip, lower, allow **`[a-z0-9_]`** only; if invalid or empty, log warning and return **`False`** (do not raise).
   - If **`get_company(slug)`** exists **and** **`existing["candidate_id"] == candidate_id`**, return **`False`** (duplicate slug — do not overwrite).
   - If **`get_company(slug)`** exists with **different** **`candidate_id`**, return **`False`** (global PK collision — skip).
   - URL dedupe: if **`website`** non-empty after strip and normalized URL ∈ **`_candidate_company_urls(candidate_id)`**, return **`False`**.
   - Target state: **`WEBSITE_FOUND`** if **`website`** non-empty else **`NEW`**.
   - Call **`database.save_company(short_name=slug, state=target_state, company_website=website or "", candidate_id=candidate_id, company_name=slug)`** — do **not** call **`transition_company_state`** separately ( **`save_company`** sets state).
   - Optional: append discovery provenance to **`company_data`** key **`inflow_discovery_notes`** (string with source URL from hit) via **`save_company_data`** when **`source_hit`** provided.
   - Return **`True`** when row inserted.

4. Add **`async def run_inflow_discovery_batch(candidate: Dict, batch_id: str, ctx: Optional[Dict], debug: bool) -> Dict`** returning **`_SUMMARY_ZERO`** shape:
   - **`zero = {total_processed: 1, ...}`** — one candidate run counts as one processed entity.
   - Read lines via **`company_search_terms_lines(candidate.get("candidate_data") or candidate)`**; if empty return **`zero`** with **`total_errors: 1`** and log.
   - **`cfg = INFLOW_CONFIG["discovery"]`**
   - Accumulate hits in list **`all_hits: list[GoogleCseHit]`** with dedupe by normalized **`hit["url"]`** across **all** term lines in this run.
   - For each term line, call **`search_google_cse(query=term, max_results=cfg["max_results_per_query"], site_filters=None, days=cfg["date_restrict_days"])`** inside **`try/except`**; on **`RuntimeError`/`ValueError`**, log, increment **`total_errors`**, continue to next term (do not abort whole batch unless **all** terms fail — then return errors).
   - If **`all_hits`** empty after searches, return **`zero`** (passed **0**, failed **0**, errors as counted).
   - Build **`live_content`** for vet task: header line **`Discovery hits (index|title|url|snippet)`**, then one line per hit: **`{i:03d}|{title}|{url}|{snippet}`** (truncate snippet to **500** chars like CSE client).
   - Call **`do_task(task_key=cfg["vet_task_key"], live_content=..., index=candidate_id, ctx=ctx or candidate)`**.
   - On **`do_task`** failure / missing **`results`**, return **`{**zero, total_errors: 1}`**.
   - For each result row:
     - Skip if **`action`** (case-insensitive) == **`ignore`**.
     - Require **`action == "slug"`** (case-insensitive); else log warning, skip.
     - Require non-empty **`short_name`** when slugging; optional **`website`**.
     - Map **`hit_index`** to **`all_hits[hit_index]`** when in range for provenance; ignore out-of-range indices but still ingest if slug valid.
     - Call **`ingest_new_companies(...)`**; count **`ingested`** vs **`skipped`**.
   - Return **`{total_processed: 1, total_passed: ingested, total_failed: skipped, total_errors: ...}`** where **`ingested + skipped`** equals accepted slug decisions count.

⚠️ **Decision:** Reuse **`find_company_website`** prompt slot is **not** used for vetting — separate **`vet_inflow_discovery`** task so Susan can tune discovery vetting without touching legacy website finder.

⚠️ **Decision:** **`save_company`** job-clear on state **`NEW`** ( **`company_state_clear_posting_jobs`** default) is harmless for new inflow rows (no jobs yet). Do **not** change that gate in this ticket.

### Self-review (Stage 3)

| Rule | OK? |
|------|-----|
| §2.5 external | CSE only via **`search_google_cse`** |
| §1.3 DRY | URL normalize delegated to **`playwright.normalize_url`** |
| §3.2 logging | Use roster module **`logger`** for skip/failure lines |

---

## Execution contract (developer agent)

Per **plan-astral**: execute stages in order; stop and **`🛑`** comment on **AST-490** if AST-504 helper missing on integration line; do **not** implement Phase 2 resolution, encoded prefilter, or **`PREFILTER_PASSED`** dispatch (**sibling tickets**).

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — touches config, database dispatch eligibility, dispatcher, consult routing, and new roster discovery/ingest paths.

**Conf:** `Medium` — patterns mirror gaze/dispatch and AST-489 CSE, but candidate **`entity_type`** and task-level weekly cadence are new wiring.

**Risk:** `Medium` — bad dedupe or slug validation could duplicate companies or skip valid hits; discovery mis-runs only affect inflow rows, not manual **`IMPORTED`** path.

## Self-Assessment justifications

- **Scope:** Five product modules plus dispatch seed — broader than a single-file tweak, still confined to inflow/dispatcher surfaces.
- **Conf:** AST-504 contract and candidate cadence need careful alignment with existing dispatcher comments about **`freq_hrs`**.
- **Risk:** Incorrect ingest logic corrupts roster data for a candidate but does not break job consult pipelines.

## Self-review (ASTRAL_CODE_RULES)

| Rule | Notes |
|------|-------|
| §1.3 DRY | Reuse **`company_search_terms_lines`**, **`search_google_cse`**, **`normalize_url`** |
| §2.1 config | All literals in **`INFLOW_CONFIG`** / **`TASK_CONFIG`** |
| §2.4 batch | One candidate per dispatch run; standard ledger |
| §2.6 state machine | **`NEW`**, transitions added; **`IMPORTED`** untouched |
| §3.3 imports | **`roster → external`**, **`database → candidate`** OK |
| §3.5 naming | **`inflow_discovery`**, **`vet_inflow_discovery`**, **`ingest_new_companies`** |

No **`conf-!!-NONE`** conflicts identified.

## Review stub (Hedy / build)

**Publish ref:** `origin/sub/AST-490/AST-505-discovery-search-vet-slugs-and-ingest-new-companies`  
**Product tip:** `34508106` — config + dispatch wiring + roster discovery/ingest (3 commits)

**Admin prerequisite:** `vet_inflow_discovery` task prompt row must exist in Admin → Task Prompts before vet step works in UAT.

## Review

**Diff:** `origin/dev...origin/sub/AST-490/AST-505-discovery-search-vet-slugs-and-ingest-new-companies` (tip `102e2acf`)

### What's solid

- **Plan fidelity:** Stages 1–3 land as specified — `INFLOW_CONFIG`, `NEW` company state, `(NEW → WEBSITE_FOUND|NO_WEBSITE)` transitions, `vet_inflow_discovery` task schema, `inflow_discovery` dispatch seed + mirror, candidate eligibility with task-level `freq_hrs` / `last_run_at`, dispatcher candidate branch (no company batch clear), CSE → vet → `ingest_new_companies` pipeline.
- **§2.1 config:** Discovery literals centralized; no magic numbers in roster paths.
- **§2.4 batch:** One candidate per run; ledger/`last_run_at` pattern preserved.
- **§2.6 state machine:** `IMPORTED` manual path untouched; ingest uses `save_company` state directly per plan.
- **§2.5 / §3.3 layers:** CSE via `search_google_cse`; URL normalize via `playwright.normalize_url`; no UI/data layer violations in diff.
- **Dedupe / ingest:** Slug validation, global PK collision skip, candidate-scoped URL dedupe (www-stripped), `NEW` vs `WEBSITE_FOUND` branching, discovery notes on provenance — matches acceptance criteria 4–6.
- **Tests:** Betty manifest §7.13zg targets present (config seed, eligibility, dispatcher routing, roster ingest/batch).

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| **fix-now** | `src/core/roster.py` L34 | Imports `company_search_terms_lines` from `src.core.candidate`, but that symbol is **not on this publish ref** (added on **AST-504** `origin/sub/AST-490/AST-504-…` only). **ImportError at module load** — Phase 1 cannot run until AST-504 is on the integration line or this branch cherry-picks the helper. Plan noted the dependency; shipped ref is not self-contained. |
| **discuss** | `src/data/database.py` `_candidate_search_term_lines` vs `src/core/candidate.company_search_terms_lines` (AST-504) | Data layer mirrors term parsing (layer constraint — OK). After AST-504 merge, two copies exist; if normalization diverges, eligibility vs batch could disagree. Prefer single shared helper (utils or post-504 import) once blocker clears. |
| **discuss** | `src/core/consult.py` candidate branch | Routes **all** `entity_type == "candidate"` to inflow discovery — no `input_state` / `task_key` guard. Safe while `inflow_discovery` is the only candidate dispatch task; needs router when a second candidate task appears. |
| **advisory** | `src/core/consult.py` candidate lazy import | Missing cycle-break comment (cf. `board_search` branch) — B1 polish only. |
| **advisory** | `src/core/roster.py` `run_inflow_discovery_batch` | `batch_id` / `debug` parameters unused (harmless; `do_task` may still pick up batch from context). |
| **advisory** | UAT | Admin **`vet_inflow_discovery`** prompt row required before vet step (per plan stub). **AST-504** must precede live dispatch eligibility. |

### Recommended actions

1. **Before resolve:** Cherry-pick AST-504's `company_search_terms_lines` (and any artifact normalization it depends on) onto `dev-hedy`, re-publish `origin/sub/AST-490/AST-505-…`, or merge AST-504 sub into the 505 integration line — verify `from src.core import roster` imports cleanly.
2. **Optional:** Add `input_state` / `task_key` guard in `run_consult_task` when a second candidate dispatch task is planned.
3. **UAT prep:** Seed `vet_inflow_discovery` prompts; confirm AST-504 artifact path in Artifacts UI.

## Resolution

**Date:** 2026-05-27 · **Review:** Radia @ `fcda6d67` · **Resolve:** Hedy

### fix-now

- **AST-504 dependency:** Merged `origin/sub/AST-490/AST-504-company-search-terms-artifact-and-craft-task` onto `dev-hedy` so `src/core/candidate.company_search_terms_lines` exists before `src/core/roster` import. Re-published `origin/sub/AST-490/AST-505-discovery-search-vet-slugs-and-ingest-new-companies` with AST-504 product + tests on the ref; `from src.core import roster` loads cleanly.

### discuss (unchanged — documented for UAT / follow-up)

- **`_candidate_search_term_lines` vs `company_search_terms_lines`:** Data-layer mirror remains intentional; watch for normalization drift after AST-504 lands on all integration lines.
- **`run_consult_task` candidate branch:** Still routes all `entity_type == "candidate"` to inflow discovery; add `task_key` guard when a second candidate dispatch task ships.

### advisory (no code change this pass)

- Cycle-break comment on consult lazy import; unused `batch_id`/`debug` in `run_inflow_discovery_batch`; Admin **`vet_inflow_discovery`** + **`craft_company_search_terms`** prompt rows for UAT.
