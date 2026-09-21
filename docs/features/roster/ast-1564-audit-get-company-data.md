# AST-1564 — Audit get_company_data

<!-- linear-archive: AST-1564 archived 2026-09-09 -->

## Linear archive (AST-1564)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1564/audit-get-company-data  
**Status at archive:** Archive  
**Project:** Astral Roster  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Execution plan

1. **Map the two** `get_company_data` **surfaces** — distinguish async coat-check `roster.get_company_data(company, key)` (fetch-on-missing via `_COATCHECK_HANDLERS` for registered `ROSTER_CONFIG["company_data_keys"]`) from sync contact-task handler `contact_task_get_company_data(candidate_id, short_name)` registered in `CONTACT_TASK_CONFIG`. Document signatures, return shapes, and which keys each path can hydrate.
2. **Inventory coat-check callers vs direct** `company_data` **reads** — ripgrep `src/` and `tests/` for:
   * `await get_company_data(` / `roster.get_company_data(`
   * `company["company_data"]`, `company.get("company_data")`, nested key access (`homepage_text`, `nav_links`, `website_content`, `prefilter_score`, PJL keys, etc.)
   * `save_company_data` writers (context for read patterns)
     Classify each site: faithful coat-check, justified direct read (e.g. batch paths where data was just written or guaranteed present), or potential end-run. Use coat-check statute as the bar.
3. **Trace company context at dispatch** — follow how company dicts enter runtime context:
   * Gazer/prefilter batch paths (`gazer.py`, `roster.prefilter_company_batch`, scrape readiness)
   * Consult paths that call `get_company_data` (`consult.py`)
   * Contact-task markup → `run_contact_task_dispatch` → `contact_task_get_company_data` (returns full company row, not per-key coat-check)
   * UI/API read paths (`api_admin.py`, `api_companies.py`) that lift `company_data` fields for display
     Note whether callers pass a live company dict with stale/missing keys vs going through coat-check first.
4. **Produce the** `company_data` **consumer file list** — every file under `src/` (and note test-only / migration mirrors) that reads or writes `company_data` content, one line each: file, keys/fields touched, why (scrape pipeline, prefilter, PJL parse, UI column lift, contact hydration, meteorite land, config keys registry, etc.).
5. **Write findings** — append a structured audit section to this ticket (comment or linked doc if large): coat-check fidelity summary table, context-assembly narrative with function names, full file list. **No product code changes.**

## Done when

* Findings are posted on AST-1564.
* Coat-check vs direct-access inventory covers all `src/` call sites with a clear faithful / justified / questionable classification.
* Company context assembly at dispatch is documented from ingress (gazer/consult/contact/UI) through read/write paths.
* File list of `company_data` consumers exists with brief per-file rationale.
* No commits to product code.

## Risks / open questions

* **Scope of "context object"** — Susan's brief may mean the company dict on batch `ctx`, Contact Estelle's assembled context, or any in-memory company row passed between roster helpers. Plan covers all three; confirm with Susan if a narrower slice is intended.
* `contact_task_get_company_data` **deliberately returns the full company row** (not async per-key coat-check) — audit must treat that as intentional contact-task boundary, not a violation.
* **Internal roster reads** — `roster.py` itself mixes `get_company_data` (e.g. `_fetch_website_content`) with many direct `company.get("company_data")` reads in batch/PJL paths; classify whether those are same-process cache hits vs end-runs.
* **Migration scripts** — `scripts/migrations/backfill_*.py` write `company_data` directly; include in file list but out of coat-check fidelity scope.

---

## Original brief

Perform an audit of the codebase to determine how faithfully the get_company_data function in [roster.py](<http://roster.py>) is called, versus assuming the data is available on the context object directly.

Do not change code.

Make a list of files that use content from company_data for any reason and a brief summary of how and why.

### Comments

#### chuckles — 2026-09-01T16:24:42.602Z
## Audit findings — `get_company_data` vs direct `company_data` access

Read-only audit on `origin/dev` ($ASTRAL_MAIN). No product code changed.

---

### 1. Two `get_company_data` surfaces

| Surface | Location | Signature | Behavior |
|---------|----------|-----------|----------|
| **Async coat-check** | `roster.get_company_data(company, key)` | `(company: dict, key: str) -> Any` | Returns `company["company_data"][key]` if present. For keys in `ROSTER_CONFIG["company_data_keys"]` **with** a `_COATCHECK_HANDLERS` entry, fetch-on-missing via async handler, persist via `save_company_data`, return value. Unregistered keys or keys without handlers → `None` if absent. Never stores empty/failed data. |
| **Contact task (sync)** | `tracker.contact_task_get_company_data(candidate_id, short_name)` | Registered in `CONTACT_TASK_CONFIG["get_company_data"]` | Loads company via `get_company(short_name)`, enforces candidate scope, returns **full company row** (+ `agent_story`). Does **not** call async `roster.get_company_data` or per-key coat-check. Intentional contact-task boundary. |

**Coat-check handlers today** (`_COATCHECK_HANDLERS` in `roster.py`):

- `nav_links` → `_fetch_nav_links` (scrape homepage link list)
- `prefilter_company_notes` → `_fetch_prefilter_notes` (runs `prefilter_company` task, saves notes/grades/nav/pjl/culture keys)
- `website_content` → `_fetch_website_content` (uses `culture_links_to_explore` + nav_links to scrape pages)

**Registered keys without handlers** (config `company_data_keys` includes these, but `get_company_data` returns `None` if missing): `homepage_text`, `parse_instructions`, `prefilter_score`, `job_list_visible`, `jobsite_scrape_issue_*`, `possible_joblist_links`, `pjl_*`, `selected_pjl_url`, etc.

---

### 2. Coat-check fidelity — `src/` call sites

| File | Function / context | Key(s) | Classification | Notes |
|------|-------------------|--------|----------------|-------|
| `consult.py` | `_prep_live_content` | `website_content` | **Faithful** | Async coat-check; transitions job to `NEED_WEBSITE_CONTENT` on miss. Pair with `tracker.get_job_data` for JD. |
| `gazer.py` | `fetch_culture_pages_batch` | `website_content` | **Faithful** (cache-aware) | Reads cache from in-memory `company_data` first (`_website_content_is_recorded`); on miss calls `get_company_data`. Justified cache shortcut — same row coat-check would re-read DB. |
| `gazer.py` | `process_gazer_batch` | `parse_instructions` | **Questionable** | Calls `get_company_data` but **no handler exists** for `parse_instructions` → cache-only lookup. Failure path says "re-run find_job_page". Should either add handler or read `company_data` directly (same effect today). |
| `roster.py` | `_fetch_website_content` (handler) | `nav_links` | **Faithful** | Nested coat-check before scraping culture pages. |
| `roster.py` | `get_company_data` | (all) | **N/A** | Definition / dispatch to handlers. |

**No other production callers** of `await get_company_data(` / `roster.get_company_data(` in `src/`.

---

### 3. Direct `company_data` reads — classification

**Justified (same-process / prior-stage / writer paths)**

- **`roster.py`** — Pipeline internals after `get_company()` or immediately after `save_company_data`: PJL assembly (`run_select_job_page_dispatch`, `_pjl_maps_from_company_data`), prefilter batch input (`nav_links` from batch input row at L2227 — data assembled for that batch turn), homepage readiness (`_company_homepage_ready`), inflow blurbs, terminal-state saves. Data is either just written in-process or loaded fresh from DB for the current pipeline stage.
- **`gazer.py`** — `fetch_website_batch` / `fetch_website_retry_batch`: reads `homepage_text` for AST-892 second-strike skip; writes `homepage_text`/`nav_links` via `save_company_data`. Producer stage, not consumer of missing data.
- **`gazer.py`** — `fetch_culture_pages_batch`: reads `culture_links_to_explore` from in-memory row before coat-check (required input for website_content handler).
- **`agent.py`** — `_enrich_entity_agent_responses`: reads `company_data[grades_key]` from entity dict already in batch context for scored-task display. Display-only; not a fetch path.
- **`meteorite.py`** — Seeds `company_data` on company create from `METEORITE_CONFIG`.

**Acceptable non-pipeline (UI / admin preview)**

- **`api_companies.py`** — `_flatten_for_view`: lifts `prefilter_company_notes` for list columns. Read-only display of persisted blob.
- **`api_admin.py`** — `_assemble_dispatch_preview_live_content`: reads `homepage_text`, `nav_links`, `website_content`, PJL DOM keys directly from `get_company()` for **admin preview only** — not production dispatch. Preview may show stale/missing data by design.
- **`api_admin.py`** — `backfill_culture_links_companies`: filters companies missing `culture_links_to_explore`.

**Intentional alternate API (not coat-check violations)**

- **`tracker.contact_task_get_company_data`** — Full-row contact task; Estelle gets stored company via extant getter, not per-key coat-check.

**Questionable / worth Susan's eye**

1. **`gazer.process_gazer_batch`** — `get_company_data(..., "parse_instructions")` looks like coat-check but behaves as direct read (no handler). Misleading API use.
2. **`api_admin` dispatch preview** — Direct reads for company dispatch preview could diverge from what production `consult`/`roster` paths would hydrate (e.g. missing `website_content` not coat-checked in preview). Admin-only, low risk.
3. **Most `homepage_text` / `parse_instructions` / PJL-key reads in `roster.py`** — Direct access is consistent with pipeline ordering (prior stage wrote the key), but there is **no coat-check safety net** if a company reaches a downstream state with a missing key. Failures are explicit state transitions rather than fetch-on-miss.

---

### 4. Company context at dispatch

**Gazer ingress** (`gazer.py` batch functions):

1. Dispatcher claims companies/jobs → passes entity dicts (often include embedded `company_data` from claim query).
2. `get_company(short_name)` reloads row when needed.
3. **Write path**: `save_company_data` after scrape/prefilter (homepage, nav, notes, culture links).
4. **Read path**: mix of direct `company.get("company_data")` for keys just written or gating fields (`culture_links_to_explore`, `homepage_text` skip), plus `get_company_data` for `website_content` (culture batch) and `parse_instructions` (gazer scan — cache-only).

**Consult ingress** (`consult.py`):

1. Job + company entities in batch context.
2. `_prep_live_content(job, company)` → `tracker.get_job_data(job, "job_description")` then `roster.get_company_data(company, "website_content")` — **faithful dual coat-check** before agent call.

**Roster dispatch ingress** (`roster.py` — `run_select_job_page_dispatch`, `run_company_task`, prefilter/locate/parse chains):

1. `get_company(short_name)` loads row from DB.
2. Direct `cdata = company.get("company_data")` for PJL maps, nav enumeration, parse inputs — assumes upstream stages (`find_job_page`, `select_job_page`, etc.) already persisted required keys.
3. `ctx` dict carries batch metadata (title patterns, chain flags); **not** a substitute for `company_data` — company blob stays on the company dict.

**Contact ingress** (`tracker.contact_task_get_company_data` via markup dispatch):

1. Slack turn → `run_contact_task_dispatch` → sync handler.
2. Returns full company row from `get_company()`; agent reads fields from result dict. Per-key coat-check deferred to caller (if ever needed).

**UI ingress** (`api_admin`, `api_companies`):

1. `database.get_company` / `list_companies` → direct `company_data` reads for display or preview assembly. No coat-check layer.

---

### 5. File list — `company_data` consumers (`src/`)

| File | Keys / fields touched | Why |
|------|----------------------|-----|
| `src/utils/config.py` | `company_data_keys` registry; `METEORITE_CONFIG["company_data"]`; `CONTACT_TASK_CONFIG["get_company_data"]` | Canonical key names; meteorite seed template; contact task registration. |
| `src/core/roster.py` | All pipeline keys (homepage, nav, parse_instructions, PJL maps, prefilter grades/notes, job_titles, etc.) | **Owner**: `get_company_data`, `save_company_data`, `_strip_company_data_keys`; read/write through full roster pipeline. |
| `src/core/gazer.py` | homepage_text, nav_links, website_content, culture_links_to_explore, prefilter_company_notes, parse_instructions | Scrape batches, culture coat-check, gazer job scan ingest. |
| `src/core/consult.py` | website_content (via coat-check) | JD scoring live_content assembly. |
| `src/core/tracker.py` | Full row (contact task) | Contact Estelle `get_company_data` task handler. |
| `src/core/agent.py` | `company_data[grades_key]` on entity | Batch response enrichment for scored company tasks. |
| `src/core/meteorite.py` | Config seed blob | Create synthetic meteorite company. |
| `src/ui/api/api_admin.py` | homepage_text, nav_links, website_content, job_page_dom, culture_links_to_explore | Admin dispatch preview + backfill eligibility. |
| `src/ui/api/api_companies.py` | prefilter_company_notes | List view column lift. |

**Test mirrors** (not production paths): `tests/component/core/test_roster.py`, `test_gazer.py`, `test_consult.py`, `test_tracker.py`, `test_agent.py`, `test_meteorite.py`, `tests/component/ui/api/test_api_admin.py`, `test_api_companies.py`, `tests/component/utils/test_config.py`.

**Migration / tooling** (out of coat-check scope): `scripts/migrations/backfill_collapse_blank_lines.py`, `backfill_culture_links.py`; `scripts/gen_ast382_src_review.py` (references coat-check pattern in review text).

---

### 6. Summary

- **Coat-check is narrow**: only 3 keys fetch-on-miss. Most of the roster pipeline relies on **direct `company_data` reads** after prior stages persist data — by design, not accidental widespread bypass.
- **Production coat-check usage is faithful** where it matters for cross-stage hydration: consult `website_content`, gazer culture batch `website_content`, nested `nav_links` inside website_content handler.
- **One misleading call**: gazer `parse_instructions` via `get_company_data` without a handler — functionally a direct read.
- **Contact task** correctly uses a separate full-row API; not a coat-check violation.
- **No code changes recommended** from this audit alone; any follow-up would be product decisions (e.g. add `parse_instructions` handler vs stop calling coat-check API for cache-only keys).

---

_Implementation detail may live in git history on `origin/dev`._
