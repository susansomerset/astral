<!-- linear-archive: AST-2173 archived 2026-10-16 -->

## Linear archive (AST-2173)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2173/search-backend-config-reads-core-route-add-universal-entity-search  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** ada  
**Priority / estimate:** None / 3  
**Parent:** AST-2168 — Add Universal Entity Search  
**Blocked by / blocks / related:** parent: AST-2168; blocks: AST-2174

### Description

## What this implements

Delivers `GET /api/search`: the config search registry and job-modal map, the candidate-scoped `job`/`company`/`meteorite` reads, the core function that tiers/orders hits and names each job's Jobs list and modal kind, and the route + blueprint registration. Does **not** touch any frontend file (#2).

## Citations

`stat.logging.debug`, `stat.logging.error`, `stat.logging.info.api`.

## Scope

`src/utils/config.py`, `src/data/database.py`, `src/core/search.py`, `src/ui/api/api_search.py`, `src/ui/server.py`. Technical scope: the `config.py`, `database.py`, `core/search.py`, `api_search.py`, and `server.py` items above, verbatim.

* `config.py`
  * **Search registry.** A new constant keyed by entity type (`job`, `company`, `meteorite`). Each entry holds the display label, the base field list, and the payload field list. Lists (confirmed by Susan, define round 1):
    * job — base: `astral_job_id`, `company_job_id`, `job_title`, `job_link`, `company_id`, `source_entity_id`, `state`, `batch_id`; payload: `job_data`.
    * company — base: `short_name`, `company_name`, `company_website`, `job_site`, `originating_search_term`, `state`, `batch_id`; payload: `company_data`.
    * meteorite — base: `id`, `astral_job_id`, `job_title`, `employer_name`, `link`, `electronic_contact`, `source_id`, `source_ref`, `state`, `batch_id`; payload: `content`, `classify_outcome`, `error`.
  * **Job modal map.** A new mapping from Jobs list (`ready`, `review`, `applied`, `processing`, `skipped`) to modal kind (`report` / `detail`). A module-level assert checks every Jobs list has exactly one modal kind.
* `database.py` — one new read (or one per table; `plan-child`'s call) that, for one candidate and one search string, returns every row whose configured base or payload fields contain the string (case-insensitive, `LIKE` with `%`/`_`/escape-char escaped), with which fields matched. Field lists come from the config registry, not from literals in SQL. Candidate scope is `candidate_id = ?` on all three tables. No `LIMIT`. The module header inventory lists the new read.
* `core/search.py` — new public function that takes the candidate id and search string, calls the new read(s), and returns the results keyed by entity type (`job`, `company`, `meteorite`), each an ordered list (base tier, then payload tier, most recently changed first within a tier); a type with no matches is an empty list. Each result has: entity id, display name, state, tier (`base` / `payload`), matched field names, and for jobs the Jobs list name and modal kind. A job's Jobs list is decided from `READY_JOB_STATES`, `REVIEW_JOB_STATES`, `APPLIED_JOB_STATES`, `SKIPPED_STATES`, processing as the complement, and below-floor via the existing `tracker` score-floor helpers (`score_floor_by_trigger_for_candidate`, `job_misses_dispatch_score_floor`). Debug lines at loop start/end per `stat.logging.debug`.
* `api_search.py` — new blueprint at `/api/search`, one `@require_auth` GET taking `q` and `candidate_id`. Blank `q` or missing `candidate_id` → 400 with an `error` message. Otherwise returns the core result (keyed by entity type) as JSON. Exceptions go through `server_error_from_exception` (logged once there). No info line — idempotent GET (`stat.logging.info.api`).
* `server.py` — registers the new blueprint beside the others.

## Acceptance criteria

 1. **Candidate scope.** With candidates A and B each owning a job whose `job_title` contains `Zebra`, `GET /api/search?q=zebra&candidate_id=<A>` returns A's job and not B's. Same for a company and a meteorite. **Fail:** any row owned by another candidate.
 2. **Required params.** `GET /api/search?q=%20&candidate_id=<A>` and `GET /api/search?q=x` (no candidate) each return 400 with an `error` field. **Fail:** 200, or a 500.
 3. **Ids are findable.** For one job of candidate A, searching its full `astral_job_id`, its `company_job_id`, and a 6-character middle substring of its `astral_job_id` each returns that job as a `base` tier result. A meteorite's numeric `id` and its `astral_job_id` each return that meteorite as `base`. **Fail:** missing, or tier `payload`.
 4. **Base before payload.** Candidate A has job J1 with `job_title` containing `Quokka` and job J2 whose `job_data` (only) contains `quokka`. The response's `job` list has J1 (`tier: base`) before J2 (`tier: payload`), and each appears once. **Fail:** J2 before J1, a duplicate entity, or J1 tagged `payload`.
 5. **Case-insensitive, literal wildcards.** `q=QUOKKA` returns the same set as `q=quokka`. `q=%` returns only entities with a literal `%` in a searched field, and `q=_` only those with a literal `_` — not every row. **Fail:** a different set by case, or `%` / `_` matching everything.
 6. **No cap.** A candidate with 600 jobs whose `job_title` contains `Engineer` gets all 600 back for `q=engineer`. `rg -n "LIMIT" src/core/search.py` returns nothing, and the new read in `database.py` has no `LIMIT`. **Fail:** a truncated list or a `LIMIT`.
 7. **Field lists come from config.** `rg -n "company_job_id|originating_search_term|electronic_contact" src/core/search.py src/ui/api/api_search.py` returns nothing, and removing `job_link` from the job base list in config makes a job findable only by its link stop appearing. **Fail:** a field name hard-coded outside config, or the removal changes nothing.
 8. **Job modal by list.** For candidate A, one job each on Ready (`CANDIDATE_REVIEW`), Review (`RECOMMENDED`), an Applied state, a Processing state, a Skipped state, and a Processing-state job below its dispatch score floor: the API's Jobs list for each is `ready`, `review`, `applied`, `processing`, `skipped`, `skipped`, and modal kind is `report` for the first three and `detail` for the last three. Clicking each in the UI opens `JobAnalysisReportModal` or `JobDetailModal` to match. **Fail:** any mismatch.
 9. **Grouped by type.** `GET /api/search` returns an object whose keys are exactly `job`, `company`, `meteorite`, each a list. For a string matching two jobs and one meteorite but no company, the page shows a Jobs (2) section then a Meteorites (1) section, and no Companies section. A string matching nothing shows "No results" and no section headings. **Fail:** other keys, a Companies heading, wrong order or count, or an empty section heading.
10. **No info line.** `rg -n "logger.info" src/ui/api/api_search.py src/core/search.py` returns nothing. **Fail:** any hit.
11. **Builds clean.** From repo root, `PYTHONPATH=.:src python -c "import src.utils.config, src.core.search, ui.api.api_search"` exits 0. In `src/ui/frontend`, `npm run build` exits 0 and `npm run lint` reports no problem absent on `origin/dev`. **Fail:** non-zero exit or a new lint problem.

## Boundaries

Does not touch any frontend file — the search input, `/search` route, results page, and modal hosting are the sibling child (#2). For ACs 8 and 11, this child owns the API half (Jobs list + modal kind per job; response keyed by `job`/`company`/`meteorite`); the UI clicks/sections are #2's. For AC 15, this child owns the Python import check.

## Notes for planning

Citations: `stat.logging.debug`, `stat.logging.error`, `stat.logging.info.api`. Search field lists confirmed by Susan (define round 1): base-first ranking, no cap, `state_history` / timestamps / compressed stores not searched. Applied jobs → report modal.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-2168-universal-entity-search`, child `sub/AST-2168/AST-2173-search-backend`. Created at dispatch-parent.

### Comments

#### radia — 2026-10-12T23:17:40.394Z
[code-rubric] REVIEW (Commit: bb3236f02) debug callee pair discuss

#### betty — 2026-10-12T23:14:11.652Z
`origin/sub/AST-2168/AST-2173-search-backend` @ `bb3236f02` · search backend tests landed

#### joan — 2026-10-12T23:04:47.832Z
[plan-rubric] PROCEED (Commit: 11c0b7ad) Backend search plan solid.

#### ada — 2026-10-12T23:03:01.901Z
`origin/sub/AST-2168/AST-2173-search-backend` @ `11c0b7ad3` · plan ready, estimate agreed

---

# AST-2173 — Search backend: config, reads, core, route

- **Ticket:** [AST-2173](https://linear.app/astralcareermatch/issue/AST-2173) (child of [AST-2168](https://linear.app/astralcareermatch/issue/AST-2168) — Add Universal Entity Search)
- **Publish ref:** `sub/AST-2168/AST-2173-search-backend` (origin only)
- **Canon Scope:** `stat.logging.debug`, `stat.logging.error`, `stat.logging.info.api` (statutes only — no patterns cited)

Delivers `GET /api/search?q=…&candidate_id=…`: a config search registry (per entity type: label, id field, display-name fields, base fields, payload fields) and a Jobs-list → modal-kind map; one candidate-scoped `LIKE` read in `database.py` that searches the configured columns of `job` / `company` / `meteorite` and reports which fields matched; a core function that tiers (base before payload), keeps newest-changed first within a tier, and names each job's Jobs list and modal kind; and the route + blueprint registration. No frontend file is touched — the search box, `/search` page and modal hosting are [AST-2174](https://linear.app/astralcareermatch/issue/AST-2174) (Hedy), which consumes the response contract defined in Stage 2.

**Verified on the synced tree at plan time (`3988bbf36`):**

- All three tables have `candidate_id` and `state_changed_at` columns. `company.candidate_id` is added by `_ensure_company_candidate_fk` (`database.py` ~L3765), not by `_ensure_company_schema` — the new read calls the former, same as `list_companies`.
- `job_data`, `company_data`, meteorite `content` / `classify_outcome` / `error` are plain `TEXT` (zlib compression in `database.py` is only on `agent_data` / `artifact` blobs), so `LIKE` sees inside them.
- `meteorite.id` is `INTEGER`; SQLite `LIKE` coerces it to text, so a substring of the numeric id matches (AC 3).
- SQLite `LIKE` is case-insensitive for ASCII by default and `rg -n case_sensitive_like src` is empty (AC 5). Runtime SQLite is 3.46.1 (supports `NULLS LAST`, already used by `list_jobs`).
- `GET /api/jobs?view=processing` drops below-floor jobs and `view=skipped` adds them (`api_jobs.py` ~L162–187). The core classifier below reproduces that exactly, using the explicit lists first and the floor check only for the complement.
- Error idiom at routes (`api_jobs.get_job_resume_structure` ~L417–432): `logger.exception("<cid> | api <route> failed\n  <Type>: <exc>\n  <next step>")` then `return server_error_from_exception(exc)`. `server_error_from_exception` itself does **not** log, so the route's `logger.exception` is the one log line (`stat.logging.error`).
- Jobs list pages display `job.company`, which is `company_id` (`_job_row_to_dict` compat alias). Job display name therefore uses `company_id`.

## Explicit scope gate

Ticket `## Scope`: `src/utils/config.py`, `src/data/database.py`, `src/core/search.py`, `src/ui/api/api_search.py`, `src/ui/server.py`. Every code row in Files Changed is one of those five, and each change is the kind the Technical scope names: config search registry + job modal map (+ assert); one new read + header inventory line; new core public function; new blueprint with one GET; blueprint registration. No `tests/`, bible, or `src/ui/frontend/**` edits.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `SEARCH_ENTITY_CONFIG` registry and `SEARCH_JOB_MODAL_BY_LIST` map + module-level assert, after the `JOBS_PROCESSING_EXCLUDED_STATES` assert | utils |
| `src/data/database.py` | Import `SEARCH_ENTITY_CONFIG`; add `search_entity_rows()` after `list_jobs_below_dispatch_score_floor`; add one header inventory line | data |
| `src/core/search.py` | **New** — `search_entities()` public function + `_jobs_list()` helper | core |
| `src/ui/api/api_search.py` | **New** — `search_bp` blueprint, `GET /api/search` | ui |
| `src/ui/server.py` | Register `search_bp` after `meteorite_bp` | ui |
| `docs/features/interface/ast-2173-search-backend-config-reads-core-route.md` | This plan (plan-child) + review stub (build-child §10) | docs |

**Lint baseline** (`NO_COLOR=1 ruff check <file> | grep '^Found'` at plan time): `config.py` 102, `database.py` 707, `server.py` 28. New files must report `All checks passed!`; existing files must not exceed their baseline.

---

## Stage 1: Config registry and the candidate-scoped read

**Done when:** `PYTHONPATH=.:src python3 -c "import src.utils.config, src.data.database"` exits 0; in a Python shell against the local DB, `database.search_entity_rows("job", <cid>, "<a known job_title substring>")` returns that candidate's matching job rows, each with a `matched_fields` list containing `"job_title"`, and no row with another `candidate_id`.

1. In `src/utils/config.py`, find the line
   `assert len(JOBS_PROCESSING_EXCLUDED_STATES) == len(set(JOBS_PROCESSING_EXCLUDED_STATES)), "Jobs lists overlap"` (~L4250). Insert this block immediately after it (one blank line before, one blank line after — the existing `# AST-1974: Skip is legal from …` comment follows):

   ```python
   # AST-2173: Universal search — per entity type (keys double as table names), the columns searched
   # by case-insensitive literal substring. A hit on any base field ranks the entity in the base tier;
   # payload-only hits rank after. id_field keys the result; name_fields join (non-empty, " — ") into
   # its display name. Field names live here only — database/core read them from this registry.
   SEARCH_ENTITY_CONFIG = {
       "job": {
           "label": "Jobs",
           "id_field": "astral_job_id",
           "name_fields": ["job_title", "company_id"],
           "base_fields": [
               "astral_job_id", "company_job_id", "job_title", "job_link",
               "company_id", "source_entity_id", "state", "batch_id",
           ],
           "payload_fields": ["job_data"],
       },
       "company": {
           "label": "Companies",
           "id_field": "short_name",
           "name_fields": ["company_name"],
           "base_fields": [
               "short_name", "company_name", "company_website", "job_site",
               "originating_search_term", "state", "batch_id",
           ],
           "payload_fields": ["company_data"],
       },
       "meteorite": {
           "label": "Meteorites",
           "id_field": "id",
           "name_fields": ["job_title", "employer_name"],
           "base_fields": [
               "id", "astral_job_id", "job_title", "employer_name", "link",
               METEORITE_CONFIG["electronic_contact_column"], "source_id", "source_ref", "state", "batch_id",
           ],
           "payload_fields": ["content", "classify_outcome", "error"],
       },
   }

   # AST-2173: which modal a job search result opens, by the Jobs list it sits on (list rules = the
   # Jobs pages': READY/REVIEW/APPLIED/SKIPPED_STATES, Processing = complement, below-floor = Skipped).
   SEARCH_JOB_MODAL_BY_LIST = {
       "ready": "report",
       "review": "report",
       "applied": "report",
       "processing": "detail",
       "skipped": "detail",
   }
   assert set(SEARCH_JOB_MODAL_BY_LIST) == {"ready", "review", "applied", "processing", "skipped"} and set(
       SEARCH_JOB_MODAL_BY_LIST.values()
   ) <= {"report", "detail"}, "every Jobs list needs exactly one search modal kind (report|detail)"
   ```

   ⚠️ **Decision:** `id_field` and `name_fields` are added to each registry entry alongside the ticket's label / base / payload lists, so core never types a column name (AC 7's spirit, not just its three-name grep). `label` is carried as specified; the backend response does not use it (the response keys are exactly `job`/`company`/`meteorite` per AC 9) — it is there for config readers.

   ⚠️ **Decision:** meteorite's contact column is `METEORITE_CONFIG["electronic_contact_column"]` (defined ~L2900, value `"electronic_contact"`), not a retyped literal — that literal already has one home (AST-1688/1689).

2. In `src/data/database.py`, in the `from src.utils.config import (` block (L74–127), add `SEARCH_ENTITY_CONFIG,` on its own line directly after `RUBRIC_FEEDBACK_CONFIG,`.

3. In the `database.py` module docstring, directly after the line beginning `Agent: save_agent (upsert), …` (L55), add exactly:

   ```
   Search (AST-2173): search_entity_rows(entity_type, candidate_id, needle) — candidate-scoped case-insensitive literal LIKE over SEARCH_ENTITY_CONFIG base+payload fields of job / company / meteorite; rows carry matched_fields; newest state_changed_at first; no LIMIT.
   ```

4. In `database.py`, after the end of `list_jobs_below_dispatch_score_floor` (the `return [r for r in rows if job_misses_dispatch_score_floor(r, floors)]` line, ~L2511) and before the `# ---- Timesheets ----` comment, insert (two blank lines before and after):

   ```python
   def search_entity_rows(entity_type: str, candidate_id: str, needle: str) -> List[Dict[str, Any]]:
       """AST-2173: one candidate's rows of one SEARCH_ENTITY_CONFIG type (key = table) whose base or payload
       fields contain needle — case-insensitive, with % _ and \\ matched literally (ESCAPE '\\').
       Each row dict gains matched_fields (names in config order). Newest state_changed_at first; no LIMIT.
       Raises ValueError on blank candidate_id or needle; KeyError on an unknown entity_type."""
       cid = (candidate_id or "").strip()
       if not cid:
           raise ValueError("candidate_id required")
       if not (needle or "").strip():
           raise ValueError("needle required")
       entry = SEARCH_ENTITY_CONFIG[entity_type]
       fields = [*entry["base_fields"], *entry["payload_fields"]]
       # Escape char first, then the two LIKE wildcards, so the needle is matched as typed.
       pattern = "%" + needle.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
       hits = [f"({f} LIKE ? ESCAPE '\\')" for f in fields]
       # company.candidate_id comes from _ensure_company_candidate_fk (it also ensures the company table).
       ensure = {
           "job": _ensure_job_schema,
           "company": _ensure_company_candidate_fk,
           "meteorite": _ensure_meteorite_schema,
       }[entity_type]

       def _with_conn() -> List[Dict[str, Any]]:
           conn = _get_connection()
           try:
               ensure(conn)
               # One 0/1 flag column per searched field tells the caller which fields matched.
               flags = ", ".join(f"{h} AS __hit_{i}" for i, h in enumerate(hits))
               rows = conn.execute(
                   f"SELECT *, {flags} FROM {entity_type} WHERE candidate_id = ? AND ({' OR '.join(hits)}) "
                   "ORDER BY state_changed_at DESC NULLS LAST",
                   [*([pattern] * len(fields)), cid, *([pattern] * len(fields))],
               ).fetchall()
               out: List[Dict[str, Any]] = []
               for r in rows:
                   d = _row_to_dict(r)
                   d["matched_fields"] = [f for i, f in enumerate(fields) if d.pop(f"__hit_{i}")]
                   out.append(d)
               return out
           finally:
               conn.close()

       return _run_with_retry(_with_conn)
   ```

   ⚠️ **Decision:** one generic read (not one per table). Table and column names come only from `SEARCH_ENTITY_CONFIG`, so AC 7's "remove `job_link` from config → stops matching" holds with no SQL literal to keep in sync. Interpolating names into SQL is safe here: they are config constants, never request input; only `pattern` and `cid` are bound parameters.

   ⚠️ **Decision:** "most recently changed" = `state_changed_at DESC NULLS LAST` on all three tables — the column every Jobs list and `list_meteorites_for_candidate` already sort by. `updated_at` was rejected because batch claim/clear bumps it with no user-visible change.

   ⚠️ **Decision:** rows are returned raw (`_row_to_dict`, no `job_data` JSON parse) — core only reads scalar columns, so parsing payloads would be wasted work.

5. Compile and lint:
   - `python3 -m py_compile src/utils/config.py src/data/database.py`
   - `PYTHONPATH=.:src python3 -c "import src.utils.config, src.data.database"` exits 0.
   - `NO_COLOR=1 ruff check src/utils/config.py | grep '^Found'` ≤ 102; `NO_COLOR=1 ruff check src/data/database.py | grep '^Found'` ≤ 707.

6. Commit: `code(AST-2173): search registry, job modal map, candidate-scoped search read`. Publish per build-child §9.

---

## Stage 2: Core search — tier, order, Jobs list and modal kind

**Done when:** `PYTHONPATH=.:src python3 -c "import src.core.search"` exits 0; `rg -n "LIMIT|logger.info|company_job_id|originating_search_term|electronic_contact" src/core/search.py` returns nothing; `search_entities(<cid>, "<a known title substring>")` returns a dict with exactly the keys `job`, `company`, `meteorite`, each a list, base-tier results before payload-tier results.

**Response contract** (what AST-2174 renders; each list item):

| Key | Type | All types | Notes |
|-----|------|-----------|-------|
| `entity_id` | str (int for meteorite) | yes | value of the registry `id_field` |
| `display_name` | str | yes | non-empty `name_fields` joined with `" — "`; falls back to `str(entity_id)` |
| `state` | str | yes | row `state` |
| `tier` | `"base"` \| `"payload"` | yes | `base` if any matched field is a base field |
| `matched_fields` | list[str] | yes | field names, config order |
| `jobs_list` | `"ready"`\|`"review"`\|`"applied"`\|`"processing"`\|`"skipped"` | job only | |
| `modal_kind` | `"report"` \| `"detail"` | job only | `SEARCH_JOB_MODAL_BY_LIST[jobs_list]` |

⚠️ **Decision:** each type is an ordered **list**, not an id-keyed object — the ticket and AC 9 require lists, and order is the payload (meteorite ids are integers, which JS objects would re-sort numerically).

1. Create `src/core/search.py` with exactly:

   ```python
   """Universal entity search (AST-2173): one candidate's jobs, companies and meteorites by any string.

   Which columns are searched, how results are named, and which modal a job opens all live in config
   (SEARCH_ENTITY_CONFIG / SEARCH_JOB_MODAL_BY_LIST). This module tiers, orders and labels the hits.
   """

   from typing import Any, Dict, List

   from src.core import tracker
   from src.data import database
   from src.utils.config import (
       APPLIED_JOB_STATES,
       READY_JOB_STATES,
       REVIEW_JOB_STATES,
       SEARCH_ENTITY_CONFIG,
       SEARCH_JOB_MODAL_BY_LIST,
       SKIPPED_STATES,
   )
   from src.utils.logging import get_logger

   logger = get_logger(__name__)


   def _jobs_list(job: Dict[str, Any], floors: Dict[str, float]) -> str:
       """The Jobs page a job shows on — same rules as GET /api/jobs?view=… (a below-floor job is a virtual skip)."""
       state = job.get("state")
       if state in READY_JOB_STATES:
           return "ready"
       if state in REVIEW_JOB_STATES:
           return "review"
       if state in APPLIED_JOB_STATES:
           return "applied"
       if state in SKIPPED_STATES or tracker.job_misses_dispatch_score_floor(job, floors):
           return "skipped"
       return "processing"


   def search_entities(candidate_id: str, query: str) -> Dict[str, List[Dict[str, Any]]]:
       """Every job, company and meteorite of candidate_id with query in a configured field.

       Keyed by entity type (all three keys always present; no match = empty list). Within a type:
       base-field hits first, then payload-only hits, each newest state_changed_at first (read order).
       """
       floors = tracker.score_floor_by_trigger_for_candidate(candidate_id)
       out: Dict[str, List[Dict[str, Any]]] = {}
       for entity_type, entry in SEARCH_ENTITY_CONFIG.items():
           rows = database.search_entity_rows(entity_type, candidate_id, query)
           logger.debug("Beginning %s search result loop on %d items", entity_type, len(rows))
           base: List[Dict[str, Any]] = []
           payload: List[Dict[str, Any]] = []
           for row in rows:
               entity_id = row[entry["id_field"]]
               name = " — ".join(str(row[f]).strip() for f in entry["name_fields"] if str(row.get(f) or "").strip())
               tier = "base" if any(f in entry["base_fields"] for f in row["matched_fields"]) else "payload"
               result: Dict[str, Any] = {
                   "entity_id": entity_id,
                   "display_name": name or str(entity_id),
                   "state": row.get("state"),
                   "tier": tier,
                   "matched_fields": row["matched_fields"],
               }
               if entity_type == "job":
                   result["jobs_list"] = _jobs_list(row, floors)
                   result["modal_kind"] = SEARCH_JOB_MODAL_BY_LIST[result["jobs_list"]]
               # Stable split keeps the read's newest-first order inside each tier.
               (base if tier == "base" else payload).append(result)
           out[entity_type] = base + payload
           logger.debug("End %s search result loop after %d items", entity_type, len(out[entity_type]))
       return out
   ```

   ⚠️ **Decision:** `stat.logging.debug` lines are the loop begin/end pair per entity type, as the ticket's Technical scope specifies. No callee in/out lines around `database.search_entity_rows`: its "response string" is every matched row including full `job_data` / `company_data` payloads — and `stat.logging.debug` forbids truncating it — so the loop counts are the debug record. No `info`, no `error` here: exceptions propagate to the route (`stat.logging.error` — log once at the handler).

   ⚠️ **Decision:** `src/core/search.py` imports `src.data.database` directly (17 `src/core` modules already do, including `tracker`, `roster`, `meteorite`) and uses the two `tracker` floor helpers the ticket names. No tracker facade is added — `tracker.py` is outside this ticket's Scope.

   ⚠️ **Decision:** floors are read once per search, unconditionally (one small `dispatch_task` read), rather than lazily only when a job matches — one fewer branch.

2. Compile and lint:
   - `python3 -m py_compile src/core/search.py`
   - `PYTHONPATH=.:src python3 -c "import src.core.search"` exits 0.
   - `ruff check src/core/search.py` → `All checks passed!`
   - `rg -n "LIMIT|logger.info|company_job_id|originating_search_term|electronic_contact" src/core/search.py` → no output.

3. Commit: `code(AST-2173): core search — tiers, order, Jobs list and modal kind`. Publish.

---

## Stage 3: `GET /api/search` route and registration

**Done when:** with the app running locally and auth satisfied, `GET /api/search?q=%20&candidate_id=<A>` and `GET /api/search?q=x` each return 400 with an `error` field; `GET /api/search?q=<known title substring>&candidate_id=<A>` returns 200 with keys exactly `job`, `company`, `meteorite`; `rg -n "logger.info|LIMIT|company_job_id|originating_search_term|electronic_contact" src/ui/api/api_search.py` returns nothing.

1. Create `src/ui/api/api_search.py` with exactly:

   ```python
   """Universal entity search API (AST-2173): GET /api/search?q=…&candidate_id=…"""

   from flask import Blueprint, jsonify, request

   from ui.auth import require_auth
   from ui.api_errors import error_json, server_error_from_exception
   from src.core.search import search_entities
   from src.utils.logging import get_logger

   search_bp = Blueprint("search", __name__, url_prefix="/api/search")
   logger = get_logger(__name__)


   @search_bp.route("")
   @require_auth
   def search():
       """Results keyed by job / company / meteorite. q is searched as sent (blank = 400).
       Idempotent read — no api info line (stat.logging.info.api)."""
       q = request.args.get("q") or ""
       candidate_id = (request.args.get("candidate_id") or "").strip()
       if not q.strip():
           return error_json("q required")
       if not candidate_id:
           return error_json("candidate_id required")
       try:
           return jsonify(search_entities(candidate_id, q))
       except Exception as exc:
           logger.exception(
               "%s | api %s failed\n  %s: %s\n  Returning 500; the search results page shows no results",
               candidate_id,
               "/api/search",
               type(exc).__name__,
               exc,
           )
           return server_error_from_exception(exc)
   ```

   ⚠️ **Decision:** `q` is passed to core exactly as received — only the blank check strips. Functional scope 3 says "any string, literally"; the sidebar box (AST-2174) already trims before navigating.

   ⚠️ **Decision:** 400s use the shared `error_json` helper from `ui/api_errors.py` (body `{"error": "<msg>"}`) — same file the ticket names for `server_error_from_exception`.

2. In `src/ui/server.py`, directly after

   ```python
   from ui.api.api_meteorite import meteorite_bp  # noqa: E402
   app.register_blueprint(meteorite_bp)
   ```

   (L58–59), insert one blank line and then:

   ```python
   from ui.api.api_search import search_bp  # noqa: E402
   app.register_blueprint(search_bp)
   ```

3. Compile and lint:
   - `python3 -m py_compile src/ui/api/api_search.py src/ui/server.py`
   - AC 11 (Python half): from repo root, `PYTHONPATH=.:src python3 -c "import src.utils.config, src.core.search, ui.api.api_search"` exits 0.
   - `ruff check src/ui/api/api_search.py` → `All checks passed!`; `NO_COLOR=1 ruff check src/ui/server.py | grep '^Found'` ≤ 28.
   - `rg -n "logger.info" src/ui/api/api_search.py src/core/search.py` → no output (AC 10).
   - `rg -n "LIMIT" src/core/search.py` → no output, and `search_entity_rows` in `database.py` contains no `LIMIT` (AC 6).

4. Commit: `code(AST-2173): GET /api/search route and blueprint registration`. Publish.

---

## AC ownership (this child)

Child-ticket numbering: AC 1–7, AC 10, the API half of AC 8 (`jobs_list` + `modal_kind` per job), the API half of AC 9 (response keyed by exactly `job`/`company`/`meteorite`, each a list), and AC 11's Python import check. UI clicks, sections, and `npm run build` / `lint` are AST-2174's.

## Estimate

Confirm Chuckles estimate: 3 — agree


## Joan validate

[plan-rubric]
**Ticket:** AST-2173
**Overall:** APPROVED
**Corpus:** 0d01e20d2b313a4e35cf3d07434b6cd69f615768
**Publish ref:** `origin/sub/AST-2168/AST-2173-search-backend` @ `11c0b7ad37926683dfd7f2f331010e5369b048f8`

## Canon scores
stat.logging.debug | C | 2 | Stage 2: loop begin/end per entity type only; no Calling/Response debug around `database.search_entity_rows` (documented payload-size rationale).
stat.logging.error | A
stat.logging.info.api | A

## Traceability
AC1→S1+S3; AC2→S3; AC3→S1; AC4→S2; AC5→S1; AC6→S1+S2; AC7→S1; AC8 (API `jobs_list`/`modal_kind`)→S2; AC9 (API keys/lists)→S2; AC10→S2+S3; AC11 (Python import)→S3; parent AC8 UI clicks, AC9 company/meteorite modals, AC11 `npm`→N/A — AST-2174 per Boundaries.

### discuss
- **Location:** Stage 2 (`src/core/search.py` decisions)
- **Finding:** Plan omits `Calling search_entity_rows` / `Response from search_entity_rows` debug pair required by `stat.logging.debug` Statement, relying on loop counts because full row payloads would be the only honest “response string.”
- **Recommendation:** Accept loop-only debug for this read (statute Resolution #3 vs. practical log volume), or add callee in/out with an explicit Archie carve-out — not a build blocker if team accepts the documented tradeoff.

### discuss (Canon Scope gap — do not score)
- **Location:** Parent Canon Scope vs. plan footprint
- **Finding:** `astral.config.config-source-of-truth` and `astral.layers.import-direction` plainly govern registry placement and `core`→`data` imports but are not on the frozen list.
- **Recommendation:** Archie may amend parent Canon Scope at Discussion if those should be Radia-comparable columns; this pass scored only the three logging statutes.

### acceptable
- **Location:** Child Description vs. plan Stage 3
- **Finding:** Ticket text says exceptions are “logged once” in `server_error_from_exception`; plan correctly follows `api_jobs` + `stat.logging.error` (`logger.exception` at route; helper does not log). Verified against `src/ui/api_errors.py`.
- **Recommendation:** None — implement the plan, not the stale Description clause.

## Review (build stub)

**Built:** `origin/sub/AST-2168/AST-2173-search-backend` @ `6bef3f1e2`.

**Stages delivered:**
- Stage 1: `SEARCH_ENTITY_CONFIG` + `SEARCH_JOB_MODAL_BY_LIST` (+ assert) in `config.py`; `search_entity_rows()` + import + header inventory line in `database.py` — `8e4ecfbfd`
- Stage 2: `src/core/search.py` (`search_entities`, `_jobs_list`) — `618fe8f63`
- Stage 3: `src/ui/api/api_search.py` (`search_bp`, `GET /api/search`) + registration in `server.py` after `meteorite_bp` — `6bef3f1e2`

**Deviations from plan text (lint gate vs verbatim code — plan contradicted itself; asked Susan in chat, no answer, took the behavior-neutral option):**
- `database.py` / `core/search.py`: annotations are built-in `list[...]` / `dict[...]` instead of `typing.List` / `Dict` (ruff UP006). Keeps `database.py` at its 707 baseline and `search.py` at `All checks passed!`. No behavior change.
- `api_search.py`: imports ordered by `ruff --select I001 --fix` (`src.*` before `ui.*`). 1 remaining finding, TRY401 (`exc` inside `logger.exception`) — that message body is `stat.logging.error`'s prescribed live-facts line, the same idiom flagged 23× across `src/ui/api/`; kept per canon.
- `server.py`: 28 → 30. The new `# noqa: E402` line reproduces every sibling registration (RUF100 + split I001 block); kept for consistency with the eleven neighbours.

**Smoke-verified (throwaway seeded SQLite, not committed):** candidate scope (B's row never returned to A); `astral_job_id` substring / `company_job_id` / meteorite integer `id` substring → `base`; `QUOKKA` = `quokka`; `%` and `_` literal only; base hit listed before a newer payload-only hit; Ready/Review/Applied/Skipped/Processing → `ready`/`review`/`applied`/`skipped`/`processing` with `report`/`report`/`report`/`detail`/`detail`; below-floor Processing → `skipped`; no match → three empty lists; route 400s (`q=%20`, no candidate), 200 keys exactly `job`/`company`/`meteorite`, forced exception → one `logger.exception` at the route + 500 JSON.

**Notes:**
- The only `LIMIT` text in `search_entity_rows` is its docstring ("no LIMIT"); the SQL has none (AC 6).
- Joan's Canon Scope gap note (`astral.config.config-source-of-truth`, `astral.layers.import-direction`) is for Archie; not acted on here.


## Radia review

[code-rubric]

**Ticket:** AST-2173  
**Publish ref:** `bb3236f02568a97acf8a3e79745847fe5a85e496` (`origin/sub/AST-2168/AST-2173-search-backend`)  
**Corpus:** `0d01e20d2b313a4e35cf3d07434b6cd69f615768`  
**Overall:** DISCUSS  

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| stat.logging.debug | C | 2 | `src/core/search.py`: per-type loop begin/end only; no `Calling search_entity_rows` / `Response from search_entity_rows` around the data read (plan/build documented omission). |
| stat.logging.error | A | | |
| stat.logging.info.api | A | | |

## Column diff vs plan stage

(aligned) — Joan: `stat.logging.debug` C/2; `stat.logging.error` A; `stat.logging.info.api` A. Implementation matches the plan’s loop-only debug choice; no plan-stage vs diff downgrade.

## Frame diff

(none)

## Findings

### discuss

- **Location:** `src/core/search.py` (~L47–48), `database.search_entity_rows` call site  
- **Finding:** `stat.logging.debug` Statement requires callee in/out (`Calling <fn>: …` / `Response from <fn>: <full response string>`) at logic joints. The diff implements only the outer loop begin/end pair per `SEARCH_ENTITY_CONFIG` key; there is no debug around the `database.search_entity_rows` invocation. Resolution §3 (“huge response”) requires logging the whole string, not omitting the pair. `src/data/database.py` correctly has no debug in the new read.  
- **@susan:** Keep the documented loop-only debug for universal search (avoid serializing full `job_data` / `company_data` rows in `app_log`), or require callee in/out per statute (full row dicts as the response string)?  
- **Default:** Accept loop-only; no logging change on `resolve-child` (status quo matches plan, build smoke, and Joan plan discuss).

### advisory

- **Canon Scope (off-list, unchanged from Joan plan validate):** `astral.config.config-source-of-truth` and `astral.layers.import-direction` plainly touch `SEARCH_ENTITY_CONFIG` placement and `core`→`data` imports but are not on the frozen list — Archie-only; not scored this pass.  
- **Plan/build deviations (documented in issue doc):** built-in `list`/`dict` annotations vs plan `typing` types; `api_search.py` I001 import order; `server.py` ruff 28→30 from sibling `E402` pattern; TRY401 on `exc` in `logger.exception` body (matches `api_jobs` idiom). Behavior-neutral per build stub.  
- **Sibling test carry:** none for product scope — `tests/**` and `docs/test-bible/**` in the diff belong to this child’s Tests Passed manifest, not a sibling product leak.

### fix-now

(none)

## What's solid

- Delivers planned five-file footprint: `SEARCH_ENTITY_CONFIG` / `SEARCH_JOB_MODAL_BY_LIST` (+ assert), `search_entity_rows` (candidate scope, `ESCAPE` literals, `NULLS LAST`, no SQL `LIMIT`), `search_entities` tiering + `_jobs_list` parity with Jobs views, `GET /api/search` + blueprint registration.  
- `stat.logging.error`: single `logger.exception` at route with live facts and product next step; `server_error_from_exception` does not double-log (`src/ui/api_errors.py`).  
- `stat.logging.info.api`: idempotent GET — no `logger.info` on success path; docstring states intent.  
- SQL placeholder count for `search_entity_rows` matches bind tuple (`2 × len(fields) + 1`).

## Recommended actions (Chuckles / downstream — not Radia)

- Append this artifact to `docs/features/interface/ast-2173-search-backend-config-reads-core-route.md`, `docs()` push, post slim upshot `--as radia`, move **Review Posted**.  
- Route **DISCUSS** on debug: if Susan affirms **Default**, `resolve-child` can clear the discuss without code; if she rejects loop-only, add callee debug in `search.py` only (effort 2).  
- Do not amend frozen Canon Scope in this pass; parent scope gap is Archie’s channel.

## Resolution

**2026-10-12 — resolve-child (Ada)** against Radia review `a3676ce07` (reviewed tip `bb3236f02`).

- **fix-now:** none.
- **discuss — `stat.logging.debug` callee pair around `database.search_entity_rows`:** no Susan direction in the Linear thread, so took Radia's **Default** — accept loop-only debug, no code change. Matches the plan's Stage 2 decision and Joan's plan discuss. To reverse: add `Calling search_entity_rows: [entity_type, candidate_id, query]` / `Response from search_entity_rows: <rows>` debug lines in `src/core/search.py` only (Radia effort 2).
- **advisory — Canon Scope gap** (`astral.config.config-source-of-truth`, `astral.layers.import-direction`): Archie's channel; not acted on.
- **advisory — build deviations** (built-in generics, I001 order, `server.py` 28→30, TRY401): already recorded in the build stub; behavior-neutral; no change.
- **Product diff this pass:** none.
