# AST-1469 — Job source + Tracker meteorite save

**Linear:** [AST-1469](https://linear.app/astralcareermatch/issue/AST-1469/job-source-tracker-meteorite-save-meteorite-component)  
**Parent:** [AST-1457](https://linear.app/astralcareermatch/issue/AST-1457/meteorite-component) — Meteorite component  
**Publish ref:** `sub/AST-1457/AST-1469-job-source-tracker-meteorite-save`

Config-owned job `source` (`gazed` | `meteorite`), durable column + backfill, and Tracker meteorite save/dedupe (create / gazed-supersede / never-clobber existing meteorite). Shared foundation for `land_meteorite` and later ingress slices — this ticket does **not** implement `land_meteorite`, inbox, Contact, or the intake API.

## Scope gate

Ticket **## Scope** (verbatim partition):

- `src/utils/config.py` — source enum, `METEORITE_CONFIG` extensions, `fetch_email` seed literals, `qualify_meteorite` TASK_CONFIG adjustments for packet enrichment
- `src/data/database.py` — job source column, `save_job`, dedupe helpers
- `src/core/tracker.py` — meteorite save, gazed supersede, meteorite non-clobber

All Files Changed / Stages below stay inside that set. Out of scope (siblings): `meteorite.py` / `land_meteorite`, `agent.py` / `consult.py` invoke, Contact, intake API, inbox / `gaze_email` / gazer retarget, dispatcher ensure wiring for `fetch_email`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `JOB_SOURCES` + helpers; `METEORITE_CONFIG` land/outcome/dedupe keys; `FETCH_EMAIL_CONFIG` + `TASK_CONFIG["fetch_email"]` shell + `SEED_CONFIG` stub; `qualify_meteorite` schema packet fields | utils |
| `src/data/database.py` | `job.source` column + backfill; header inventory; `save_job` source R/W; candidate-scoped meteorite dedupe lookup helpers | data |
| `src/core/tracker.py` | `save_meteorite_job` (create / supersede / skip); one-way source promotion enforcement; Style D when `debug=True` | core |

## Stage 1: Config — job source, meteorite land literals, fetch_email seed, qualify schema

**Done when:** `JOB_SOURCES` is the sole allowed set; `METEORITE_CONFIG` carries land outcome + dedupe + employer metadata keys; `FETCH_EMAIL_CONFIG` + `TASK_CONFIG["fetch_email"]` + a `SEED_CONFIG` SQL stub exist; `qualify_meteorite` items_schema supports packet enrichment (`astral_job_id` optional, `employer_name` optional). No database or tracker changes yet.

1. In `src/utils/config.py` module header inventory, add one-line entries for `JOB_SOURCES`, `FETCH_EMAIL_CONFIG`, and note `METEORITE_CONFIG` land/source keys (AST-1469).

2. After `ENTITY_TYPES` (or immediately before `METEORITE_CONFIG` if that keeps related meteorite literals together — prefer a dedicated block **immediately above** `METEORITE_CONFIG`), add:

```python
# AST-1469: durable job provenance. gazed = roster/gazer ingest path; meteorite = land path.
# One-way promotion only: gazed → meteorite allowed; meteorite → gazed forbidden (enforced in tracker).
JOB_SOURCES = ["gazed", "meteorite"]
JOB_SOURCE_DEFAULT = "gazed"       # backfill + insert default when caller omits source
JOB_SOURCE_METEORITE = "meteorite"
```

   Assert `JOB_SOURCE_DEFAULT in JOB_SOURCES` and `JOB_SOURCE_METEORITE in JOB_SOURCES`. Add thin helpers next to `validate_value`:

```python
def is_valid_job_source(value: object) -> bool:
    return isinstance(value, str) and value in JOB_SOURCES

def validate_job_source(value: object) -> None:
    validate_value(JOB_SOURCES, value)

def job_source_transition_allowed(from_source: Optional[str], to_source: str) -> bool:
    """True when writing to_source is legal given current from_source (None/empty = unset)."""
    # unset → any JOB_SOURCES value OK; gazed → meteorite OK; same value OK;
    # meteorite → gazed forbidden; unknown from_source treated as unset only if blank.
```

3. Extend `METEORITE_CONFIG` (same dict, new keys only — do not rename existing keys) with:

| Key | Value | Purpose |
|-----|-------|---------|
| `"job_source"` | `JOB_SOURCE_METEORITE` | Source written on meteorite create/supersede |
| `"land_outcome_created"` | `"created"` | Tracker return `outcome` |
| `"land_outcome_duplicate_skip"` | `"duplicate_skip"` | Existing meteorite match — no overwrite |
| `"land_outcome_superseded"` | `"superseded"` | Gazed match promoted |
| `"land_outcome_error"` | `"error"` | Reserved for caller-visible failure shape (tracker raises; land may map) |
| `"employer_name_job_data_key"` | `"employer_name"` | Known employer string under `job_data` (parent AC5; land writes later) |
| `"dedupe_match_order"` | `("company_job_id", "job_link")` | Ordered match strategies for Stage 2 helpers |
| `"min_company_job_id_match_chars"` | reuse int from `METEORITE_EMAIL_INGEST_CONFIG["min_company_job_id_match_chars"]` (same literal reference, not a second magic number) | Exact-id match floor for dedupe helper |

   Assert new outcome strings are non-empty `str`; assert `dedupe_match_order` is exactly that two-tuple; assert `job_source == JOB_SOURCE_METEORITE`.

4. Add `FETCH_EMAIL_CONFIG` immediately after `GAZE_EMAIL_CONFIG` (mirror mailbox-shell shape; **literals only** — no dispatcher ensure in this ticket):

```python
# AST-1469: fetch_email dispatch seed literals (wired by sibling AST-1472 / inbox slice).
# Mailbox-style shell — not an ENTITY_TYPES claim queue. auto_mode stays CLICK (false).
FETCH_EMAIL_CONFIG = {
    "task_key": "fetch_email",
    "auto_mode": False,
    "min_count": 1,
    "batch_size": 1,
    "freq_hrs": 0.1,
    "entity_type": None,
    "trigger_state": None,
    "debug_func": "inbox.fetch_email",
}
```

   Assert `task_key == "fetch_email"`, `auto_mode is False`, `entity_type is None`, `trigger_state is None`.

5. In `TASK_CONFIG`, add a shell entry next to `"gaze_email"`:

```python
"fetch_email": {
    "entity_type": None,
    "requires_candidate_key": False,
    "trigger_state": None,
},
```

6. In `SEED_CONFIG`, add `"dispatch_task-fetch-email"` as a tuple with one idempotent `INSERT … SELECT … WHERE NOT EXISTS` stub that seeds a **null-candidate** shell row for `fetch_email` (same shape as `"dispatch_task-gaze-email"` historically: `candidate_id NULL`, `entity_type`/`trigger_state` NULL, `auto_mode` 0, `freq_hrs`/`min_count`/`batch_size` from `FETCH_EMAIL_CONFIG` literals inlined). Comment: not executed by this ticket; sibling owns provision/ensure. Do **not** edit `dispatcher.py`.

7. Adjust `TASK_CONFIG["qualify_meteorite"]["response_schema"]["jobs"]["items_schema"]`:

   - Set `"astral_job_id": {"type": "str", "required": False}` — dispatch qualify still passes it; land packet enrichment may omit it before first Tracker write.
   - Add `"employer_name": {"type": "str", "required": False}` — known employer for `job_data[METEORITE_CONFIG["employer_name_job_data_key"]]`.
   - Leave existing optional fields (`company_job_id`, `job_title`, `job_link`) and required `jd_text` unchanged.
   - Update the module-level asserts after `TASK_CONFIG` to include `astral_job_id` `required is False` and `employer_name` present with `required is False`.

⚠️ **Decision:** Packet enrichment reuses the same `qualify_meteorite` task_key/schema (parent “repurpose”), not a new Grace key. Making `astral_job_id` optional keeps the live METEORITE_NEW batch path valid (callers still send the id) while allowing pre-create land enrichment. Agent prompt text / `agent_task` seed edits are **not** this ticket — Hedy’s land slice owns invoke + any prompt delta.

⚠️ **Decision:** `FETCH_EMAIL_CONFIG` + `TASK_CONFIG` + `SEED_CONFIG` only — Katherine’s inbox child owns `ensure_fetch_email_*` / runner / retarget. Plan does not invent dispatcher files.

## Stage 2: Database — `job.source` column, save_job, dedupe helpers

**Done when:** Every job row has a non-null `source` in `{gazed, meteorite}` after schema ensure (existing NULLs backfilled to `gazed`); `save_job` reads/writes `source`; candidate-scoped dedupe helpers return the matching job (or None) without mutating. No Tracker meteorite API yet.

1. Update `database.py` header inventory line for `job` to include `source` (`gazed`|`meteorite`).

2. In `_ensure_job_schema`, after the existing `ALTER TABLE` loop that adds `job_link` / `latest_score`, add `("source", "TEXT")`. After columns exist:

   - Run a one-shot backfill: `UPDATE job SET source = ? WHERE source IS NULL OR TRIM(source) = ''` with `JOB_SOURCE_DEFAULT` (`gazed`). Use a process-level flag (e.g. `_job_source_backfill_applied`) so it runs once per process after ensure, same style as other ensure guards.
   - Do **not** add a CHECK constraint in SQLite; validation stays in config helpers + callers.

3. If `_job_col_defs` / board-sunset rebuild list still lists job columns for rebuild paths, append `("source", "TEXT")` so a future rebuild does not drop the column. Only touch the list that copies job columns — do not re-open board sunset behavior.

4. Extend `save_job(...)` signature with `source: Optional[str] = None`.

   - On **INSERT**: if `source` is None, write `JOB_SOURCE_DEFAULT`. If provided, call `validate_job_source(source)` (import from config) then write it. Include `source` in the INSERT column list.
   - On **UPDATE**: if `source is not None`, validate then set `source = ?`. Do **not** enforce one-way promotion in the data layer (core decides — Stage 3). Data layer still raises if `validate_job_source` fails (unknown value).
   - `_job_row_to_dict` already returns all columns — no special JSON parse for `source`.

5. Add dedupe helpers (public, next to `get_job_id_by_identity` / `job_link_exists_for_candidate`):

   **`find_candidate_job_by_company_job_id(candidate_id: str, company_job_id: str) -> Optional[Dict[str, Any]]`**
   - Strip inputs; empty → None.
   - Require `LENGTH(TRIM(company_job_id)) >= METEORITE_CONFIG["min_company_job_id_match_chars"]` (same floor as email ingest).
   - Select full job row where `company_job_id` equals the trimmed id (exact match, not LIKE) and `company IN (SELECT short_name FROM company WHERE candidate_id = ?)`.
   - `LIMIT 1`; return `_job_row_to_dict` or None.
   - Ensure company + job schemas before join (same pattern as `job_link_exists_for_candidate`).

   **`find_candidate_job_by_job_link(candidate_id: str, job_link: str) -> Optional[Dict[str, Any]]`**
   - Exact `job_link` match scoped to the candidate’s companies (same join as `job_link_exists_for_candidate`), return full row or None.

   **`find_meteorite_dedupe_match(candidate_id: str, *, company_job_id: Optional[str] = None, job_link: Optional[str] = None) -> Optional[Dict[str, Any]]`**
   - Walk `METEORITE_CONFIG["dedupe_match_order"]`:
     - `"company_job_id"`: if non-empty id, call `find_candidate_job_by_company_job_id`; return on hit.
     - `"job_link"`: if non-empty link, call `find_candidate_job_by_job_link`; return on hit.
   - Return None when no strategy hits.
   - Raise nothing for “no match”; raise `ValueError` only on empty `candidate_id`.

⚠️ **Decision:** Exact `company_job_id` equality (not inverted LIKE) for Tracker land dedupe — land receives a structured job object from qualify, not raw HTML haystacks. Email ingest LIKE helpers stay untouched for gazer paths.

⚠️ **Decision:** Match is **candidate-scoped across all that candidate’s companies**, so a gazed job under a real employer short_name can match a meteorite landing that will otherwise attach under `meteorite-{candidate_id}`.

## Stage 3: Tracker — `save_meteorite_job` (create / supersede / skip)

**Done when:** Callers can invoke `save_meteorite_job` and get a structured outcome: create new meteorite, supersede gazed→meteorite without prior-state gating, or duplicate-skip when a meteorite already matches; attempts to write `source` meteorite→gazed raise `ValueError`. `debug=True` emits Style D index headers; `debug=False` emits none from this path.

1. In `src/core/tracker.py`, add imports for `JOB_SOURCES`, `JOB_SOURCE_DEFAULT`, `JOB_SOURCE_METEORITE`, `METEORITE_CONFIG`, `job_source_transition_allowed`, `validate_job_source` (and existing `TRACKER_CONFIG` / logging helpers as needed). Prefer late-import of `ensure_meteorite_company` from `src.core.meteorite` **inside** `save_meteorite_job` only if needed to avoid import cycles — if a cycle appears, require `company` short_name to already be the meteorite placeholder passed by the caller and document that land owns ensure. **Preferred:** accept `company: str` (meteorite short_name) from the caller so this ticket does not import `meteorite.py` (sibling-owned). Land (Hedy) will ensure + call Tracker.

2. Add helper `_assert_job_source_write(current: Optional[str], new: str) -> None`:
   - `validate_job_source(new)`
   - If not `job_source_transition_allowed(current, new)`: raise `ValueError` with a message that includes both values (meteorite→gazed rejection is the AC4 case).

3. Add public **`save_meteorite_job`**:

```python
def save_meteorite_job(
    candidate_id: str,
    *,
    company: str,                          # meteorite-{candidate_id} short_name (caller-ensured)
    company_job_id: Optional[str] = None,
    job_title: Optional[str] = None,
    job_link: Optional[str] = None,
    job_data: Optional[Dict[str, Any]] = None,
    employer_name: Optional[str] = None,   # merged into job_data under config key when non-empty
    debug: bool = False,
) -> Dict[str, Any]:
```

   **Preconditions:** non-empty stripped `candidate_id` and `company`; else `ValueError`.

   **job_data prep:** start from `dict(job_data or {})`. If `employer_name` strips non-empty, set `job_data[METEORITE_CONFIG["employer_name_job_data_key"]] = stripped name`.

   **Dedupe (before insert):** `match = database.find_meteorite_dedupe_match(candidate_id, company_job_id=..., job_link=...)`.

   **Branch A — match with `source == JOB_SOURCE_METEORITE` (or missing source treated via backfill as gazed only — after Stage 2, source is always set):**
   - Do **not** update the row.
   - Return `{ "outcome": METEORITE_CONFIG["land_outcome_duplicate_skip"], "astral_job_id": match["astral_job_id"], "job": match, "source": JOB_SOURCE_METEORITE }`.
   - Style D: `outcome=duplicate_skip`.

   **Branch B — match with `source == JOB_SOURCE_DEFAULT` (`gazed`):**
   - Supersede **without** `transition_job_state` prior-state checks (create carve-out twin): build `state_history` append entry to `METEORITE_CONFIG["job_create_state"]` with timestamp + `job_create_latest_score`.
   - `_assert_job_source_write(match.get("source"), JOB_SOURCE_METEORITE)`.
   - `database.save_job(match["astral_job_id"], state=job_create_state, source=JOB_SOURCE_METEORITE, company_job_id=... if provided, job_title=..., job_link=..., job_data=prepared, merge=True, state_history=..., state_changed_at=now, latest_score=score)`.
   - ⚠️ **Decision:** Keep existing `company` on supersede (do not reassign gazed jobs onto the meteorite placeholder). Flip source + landing state/fields only. New creates (Branch C) still land under the caller-supplied meteorite company.
   - Return `{ "outcome": land_outcome_superseded, "astral_job_id": ..., "job": get_job(...), "source": JOB_SOURCE_METEORITE }`.
   - Style D: `outcome=superseded`.

   **Branch C — no match:**
   - Insert new `astral_job_id = str(uuid.uuid4())` via `database.save_job(..., company=company, state=job_create_state, source=JOB_SOURCE_METEORITE, company_job_id=..., job_title=..., job_link=..., job_data=prepared, state_history=[{to_state, timestamp, score}], state_changed_at=now, merge=False)`.
   - Then `database.save_job(id, latest_score=score)` if INSERT path omits score (same carve-out as `create_meteorite_job`).
   - If insert returns False (identity unique bounce): treat as duplicate — re-fetch via dedupe helpers / `get_job_id_by_identity` if possible and return `duplicate_skip` rather than raising, when a row is findable; otherwise raise `RuntimeError`.
   - Return `{ "outcome": land_outcome_created, "astral_job_id": ..., "job": row, "source": JOB_SOURCE_METEORITE }`.
   - Style D: `outcome=created`.

4. Style D contract (only when `debug=True`):
   - `logger.set_debug_flag(True)`
   - One `debug_index(func="tracker.save_meteorite_job", index=1, total=1, identifier=<astral_job_id or candidate_id>, outcome=<created|duplicate_skip|superseded>)`
   - `|` detail lines: candidate_id, company, matched_id (if any), source before/after as applicable.
   - No new debug-contract lines when `debug=False`.

5. Wire **one-way enforcement** on any Tracker path that writes `source` in this ticket: `_assert_job_source_write` inside `save_meteorite_job` only. Do **not** retrofit every `save_job` / `transition_job_state` caller in this ticket. Optional thin wrapper:

```python
def set_job_source(astral_job_id: str, source: str) -> None:
    """Admin/core helper: validate one-way source write on an existing job."""
```

   Load job, `_assert_job_source_write(job.get("source"), source)`, `database.save_job(..., source=source)`.

6. Do **not** change `ingest_jobs` beyond what Stage 2 INSERT default already does (omitted source → `gazed`). Do **not** edit `create_meteorite_job` (out of scope); Hedy/Katherine retarget to `save_meteorite_job`.

⚠️ **Decision:** Tracker owns meteorite non-clobber + gazed supersede; data helpers only find matches. Core decides transitions (statute `astral.state.core-decides-transitions`). Supersede uses direct `save_job` state write into `job_create_state` (`METEORITE_NEW`) — lawful unrestricted entry (`prior_states: None`), same carve-out family as current meteorite create.

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; publish to `origin/sub/AST-1457/AST-1469-job-source-tracker-meteorite-save`.
- Do not add files outside the Files Changed table.
- Do not edit `tests/`, bible, `meteorite.py`, `dispatcher.py`, inbox/gaze/contact/API.
- On ambiguity or codebase drift: stop and comment on **parent** AST-1457 with the Stage blocked template from plan-child.

## Estimate

Confirm Chuckles estimate: 5 — agree

Schema + backfill + Tracker three-way save/dedupe with one-way source law is a real multi-layer slice (config/data/core) and a new pattern (job source promotion / meteorite non-clobber); 5 matches Bang !!! foundation work. No revise.

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric.v1
**Ticket:** AST-1469
**Overall:** APPROVED
**Publish ref:** `sub/AST-1457/AST-1469-job-source-tracker-meteorite-save` @ `41118d5fe82a87088ba9fb4d4b9dbd9bddfe41b5`

### Traceability
AC2→Stage 3 (`save_meteorite_job` dedupe-before-write: duplicate_skip / gazed supersede / create); AC3→Stage 2 (`job.source` column, backfill to `gazed`, `save_job` R/W) + Stage 2 INSERT default; AC4→Stage 1 (`JOB_SOURCES`, `job_source_transition_allowed`) + Stage 3 (`_assert_job_source_write`, optional `set_job_source`); AC4 “test enforced” half→N/A out of this child’s Scope — `tests/component/core/test_meteorite.py` is AST-1470 / qa-child per parent partition. Parent AC1,5–10→N/A (land_meteorite, ingress, API, inbox retarget, debug observability, qualify invoke). Stages 1–3→child ## Scope + parent Functional scope #2–4 + Component scope config/database/tracker slice.

### Findings

#### discuss — AC4 test half unmapped in Stages
**Location:** Execution contract (“Do not edit `tests/`”) vs child AC4 “config/test enforced”
**Finding:** Config enforcement is staged; component tests for meteorite→gazed rejection and dedupe branches are explicitly deferred to sibling/qa scope.
**Recommendation:** Acceptable for this foundation slice — ensure AST-1470 / Betty manifest names AC2–4 cases so UAT does not rely on config asserts alone.

#### discuss — `job_source_transition_allowed` body abbreviated
**Location:** Stage 1 step 2 code block
**Finding:** Function spec is prose-complete but the printed snippet omits the body (unset→any, gazed→meteorite, meteorite→gazed forbidden).
**Recommendation:** Engineer should implement exactly the bullet rules before Stage 2; no plan rewrite required.

#### discuss — Supersede uses direct `save_job`, not `transition_job_state`
**Location:** Stage 3 Branch B
**Finding:** Matches existing `create_meteorite_job` carve-out and parent AC2 (“without checking the gazed job’s prior state”); `METEORITE_NEW` has `prior_states: None`. Multi-field supersede (source + landing state + payload) warrants one upsert.
**Recommendation:** Keep as planned; document in code comment pointing at parent AC + create carve-out.

#### acceptable — Procedural: assignee Ada, not Joan
**Location:** Linear ticket state
**Finding:** `validate-plan` §1 expects Joan assignee; ticket is Plan Ready with Ada. Review ran per spawn prompt.
**Recommendation:** Chuckles restores Joan assignee only when entering Plan Discuss; no plan change.

### R6 checklist (summary)
Definition fidelity, scope gate, layer/config/placement compliance, and cited patterns (`pattern.config.config-block`, `pattern.state.entity-state-transitions`) all pass. Self-assessment (estimate 5, foundation !!!) is honest. No scope creep beyond ticket ## Scope (fetch_email seed + qualify schema are explicitly in-scope).

context_tokens≈52000

## Review (build stub)

**Publish ref:** `origin/sub/AST-1457/AST-1469-job-source-tracker-meteorite-save`
**Plan path:** `docs/features/meteorite/ast-1469-job-source-tracker-meteorite-save.md`

**Built tip:** `42bdd5a78468b3bc2f17d0b2476a9d3f1190b8ac` (`42bdd5a7`)

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `56fbf4b1` | `JOB_SOURCES` + `METEORITE_CONFIG` land keys + `FETCH_EMAIL_CONFIG` seed + qualify schema |
| 2 | `f55ef14a` | `job.source` column + backfill + `save_job` R/W + dedupe helpers |
| 3 | `42bdd5a7` | `tracker.save_meteorite_job` create / gazed-supersede / meteorite non-clobber |

**Betty note:** AC2–4 component coverage (dedupe branches + meteorite→gazed reject) deferred to qa-child / sibling AST-1470 per Joan discuss — not in this child’s Scope.
