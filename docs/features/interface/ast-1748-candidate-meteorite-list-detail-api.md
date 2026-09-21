# AST-1748 — Candidate meteorite list/detail API

**Linear:** [AST-1748](https://linear.app/astralcareermatch/issue/AST-1748/candidate-meteorite-list-detail-api-add-meteorites-to-the-jobs)  
**Parent:** [AST-1741](https://linear.app/astralcareermatch/issue/AST-1741/add-meteorites-to-the-jobs-navigation) — Add "Meteorites" to the Jobs navigation  
**Publish ref:** `sub/AST-1741/AST-1748-candidate-meteorite-list-detail-api`

Authenticated GET list (candidate-scoped) and GET detail for `meteorite` staging rows, plus a data helper and list/modal config constants, so sibling AST-1749 can render Jobs → Meteorites without inventing SQL or column/section order. Does **not** own nav, routes, or React pages. Does **not** change retention or land/create routes.

## Explicit scope gate

This ticket’s **## Scope** names only:

- `src/data/database.py` — candidate-scoped list helper + header inventory; reuse `get_meteorite` for detail
- `src/utils/config.py` — list-column / modal-section constants consumed by the API (does **not** add the Jobs nav item)
- `src/ui/api/api_meteorite.py` — GET list by candidate + GET detail by id, projected fields, logging per citations

Stages below stay inside those three files and those change kinds. No `NAV_CONFIG`, no `routes.tsx`, no React, no retention, no land/create route changes, no `api_system.py`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Add `list_meteorites_for_candidate`; note helper on meteorite header inventory line | data |
| `src/utils/config.py` | Add `JOBS_METEORITES_LIST_COLUMNS` + `JOBS_METEORITES_MODAL_SECTIONS` | utils |
| `src/ui/api/api_meteorite.py` | Authenticated GET list + GET detail; project fields; debug/error logging per statutes | ui |

## Canon Scope (this ticket)

- `stat.logging.info.api` — **id + pattern read:** idempotent GETs that only return current state are **not** progress → **no** `logger.info` on the new list/detail GETs.
- `stat.logging.debug` — **pattern read:** `logger.debug` at API logic joints (callee in/out for list helper / `get_meteorite`); no `if debug` gate; **no** debug noise in `src/data/`.
- `stat.logging.error` — **pattern read:** on thrown list/detail failures handled in the API, one `logger.exception` at the handler with live facts + next step; data raises, does not log.

## Stages

### Stage 1: Candidate-scoped list helper

**Done when:** `list_meteorites_for_candidate(candidate_id)` returns every surviving `meteorite` row for that candidate ordered by `state_changed_at` descending; blank/missing candidate returns `[]` without querying; header inventory documents the helper. No config/API changes yet.

1. In `src/data/database.py`, on the `meteorite` line of the module header table inventory, append that candidate-scoped listing is via `list_meteorites_for_candidate(candidate_id)`.
2. Immediately after `get_meteorite` (before `get_meteorite_by_astral_job_id`), add:

```python
def list_meteorites_for_candidate(candidate_id: str) -> List[Dict[str, Any]]:
    """Return all meteorite rows for candidate_id, newest state_changed_at first."""
```

   Implementation mirrors sibling list helpers (`list_meteorites_by_source` / `get_meteorite`): `_run_with_retry` + `_get_connection` + `_ensure_meteorite_schema` + `_meteorite_row_to_dict`.

   - If `candidate_id` is `None` or `str(candidate_id).strip() == ""`, return `[]` **before** opening a connection.
   - Otherwise bind the stripped string and run:

```sql
SELECT * FROM meteorite
WHERE candidate_id = ?
ORDER BY state_changed_at DESC
```

   - Return the full row dicts (no state filter — all surviving rows; retention already removed purged ones). Do **not** invent placeholder rows.

⚠️ **Decision:** Order by `state_changed_at DESC` (not `updated_at`) — matches Jobs list `order_by="state_changed_at"` and parent Technical scope’s preferred recency field.

⚠️ **Decision:** No logging inside `database.py` (`stat.logging.debug` forbids data-layer debug noise; `stat.logging.error` — data raises, does not log).

⚠️ **Decision:** Do **not** add a new index in this ticket (not in Scope). Existing table scan by `candidate_id` is acceptable for operator UI volumes.

### Stage 2: List-column + modal-section config constants

**Done when:** Public `JOBS_METEORITES_LIST_COLUMNS` and `JOBS_METEORITES_MODAL_SECTIONS` exist in `config.py` with the exact rows below. API not wired yet. `NAV_CONFIG` unchanged.

1. In `src/utils/config.py`, immediately after `JOBS_RECOMMENDED_REPORT_METEORITE_SECTIONS` (AST-1691 block), add:

```python
# AST-1748: Jobs → Meteorites list columns + detail modal sections (config → API; React must not invent order).
JOBS_METEORITES_LIST_COLUMNS = [
    {"key": "state", "label": "State", "sortable": True},
    {"key": "job_title", "label": "Title", "sortable": True},
    {"key": "employer_name", "label": "Employer", "sortable": True},
    {"key": "classify_outcome", "label": "Classify", "sortable": True},
    {"key": "link", "label": "Link", "sortable": True},
    {"key": "astral_job_id", "label": "Job", "sortable": True},
    {
        "key": "state_changed_at",
        "label": "State Changed",
        "sortable": True,
        "defaultDesc": True,
        "type": "datetime",
    },
]

JOBS_METEORITES_MODAL_SECTIONS = [
    {"section_id": "meteorite_timestamps", "nav_label": "Timestamps", "default_expanded": True},
    {"section_id": "meteorite_link", "nav_label": "Link", "default_expanded": True},
    {"section_id": "meteorite_content", "nav_label": "Content", "default_expanded": True},
    {
        "section_id": "meteorite_provenance",
        "nav_label": "Provenance",
        "default_expanded": False,
    },
    {
        "section_id": "meteorite_job",
        "nav_label": "Linked Job",
        "default_expanded": True,
    },
]
```

⚠️ **Decision:** New constants (not reuse `JOBS_RECOMMENDED_REPORT_METEORITE_SECTIONS`) — Jobs → Meteorites modal is a different surface from the Recommended report Meteorite pane; list columns have no Recommended analogue.

⚠️ **Decision:** Do **not** add the Jobs → Meteorites `NAV_CONFIG` item here (sibling AST-1749). Do **not** edit `DATA_SHAPES["jobs"]` or `build_state_ui_manifest` — this ticket’s Scope delivers constants consumed by `api_meteorite` responses (Stage 3).

### Stage 3: GET list + GET detail on `api_meteorite`

**Done when:** Authenticated `GET /api/candidates/<candidate_id>/meteorites` returns `{columns, meteorites}` scoped to that candidate (empty honesty); authenticated `GET /api/meteorites/<meteorite_id>` returns `{sections, meteorite}` or 404; link/`astral_job_id` returned as stored; no `logger.info` on either GET; debug callee in/out present; thrown failures → one `logger.exception` + 500 JSON. Land/create routes unchanged.

1. In `src/ui/api/api_meteorite.py`, add imports:

   - `get_meteorite`, `list_meteorites_for_candidate` from `src.data.database`
   - `JOBS_METEORITES_LIST_COLUMNS`, `JOBS_METEORITES_MODAL_SECTIONS` from `src.utils.config`

2. Add a private projector used by both routes (field mapping only — no http(s) rewrite):

```python
_LIST_KEYS = (
    "id", "candidate_id", "state", "job_title", "employer_name",
    "classify_outcome", "link", "astral_job_id",
    "created_at", "updated_at", "state_changed_at",
    "source_kind", "source_id",
)

_DETAIL_KEYS = (
    "id", "candidate_id", "source_kind", "source_id", "source_ref",
    "state", "content", "classify_outcome", "link", "electronic_contact",
    "job_title", "employer_name", "astral_job_id", "error",
    "created_at", "updated_at", "state_changed_at", "estelle_notified_at",
)


def _project_meteorite(row: dict, keys: tuple) -> dict:
    return {k: row.get(k) for k in keys}
```

   `link` and `astral_job_id` must be the stored values (including null/blank/non-http) — UI http(s)-gates and deeplink-gates; API must not strip or invent.

3. Add list route on the existing `meteorite_bp` (`url_prefix="/api"`):

```python
@meteorite_bp.route("/candidates/<candidate_id>/meteorites", methods=["GET"])
@require_auth
def meteorite_list_for_candidate(candidate_id: str):
```

   Behavior:

   - `logger.debug("Calling list_meteorites_for_candidate: [candidate_id=%s]", candidate_id)` then call the helper, then `logger.debug("Response from list_meteorites_for_candidate: %s rows", len(rows))` (do **not** wrap in `if debug`).
   - Project each row with `_LIST_KEYS`.
   - Return `jsonify({"columns": list(JOBS_METEORITES_LIST_COLUMNS), "meteorites": projected})` with status 200.
   - Blank `candidate_id` path segment: helper returns `[]` → same shape with empty `meteorites` (no 4xx).
   - On unexpected exception: `logger.exception` with live facts (`candidate_id`, route path, exc type/message) and next step `"Returning 500; list not delivered"`, then `return jsonify({"error": "meteorite list failed"}), 500`.
   - **No** `logger.info` (idempotent GET — `stat.logging.info.api`).

4. Add detail route:

```python
@meteorite_bp.route("/meteorites/<int:meteorite_id>", methods=["GET"])
@require_auth
def meteorite_detail(meteorite_id: int):
```

   Behavior:

   - `logger.debug("Calling get_meteorite: [meteorite_id=%s]", meteorite_id)` then `get_meteorite(meteorite_id)`, then `logger.debug("Response from get_meteorite: %s", "hit" if row else "miss")`.
   - If `row is None`: return `jsonify({"error": "meteorite not found"}), 404` (soft-fail honesty — no exception log).
   - Else return `jsonify({"sections": list(JOBS_METEORITES_MODAL_SECTIONS), "meteorite": _project_meteorite(row, _DETAIL_KEYS)})` with status 200.
   - On unexpected exception: `logger.exception` with live facts (`meteorite_id`, route, exc) and next step `"Returning 500; detail not delivered"`, then `return jsonify({"error": "meteorite detail failed"}), 500`.
   - **No** `logger.info`.

5. Do **not** modify `meteorite_land` / `meteorite_create_job` handlers, payloads, or URLs. Blueprint is already registered in `src/ui/server.py` — no server edit.

⚠️ **Decision:** Path-param list under `/api/candidates/<candidate_id>/meteorites` (plural collection) to sit beside existing `/api/candidates/<candidate_id>/meteorite/land` on the same blueprint; detail at `/api/meteorites/<id>` (global id, like `/api/jobs/<id>`). Sibling AST-1749 consumes these exact paths.

⚠️ **Decision:** Wrap list/detail JSON with `columns` / `sections` so the config constants are literally consumed by this API (Scope) without touching `api_system.py` / `DATA_SHAPES`.

⚠️ **Decision:** List omits `content` (heavy) but still returns metadata keys the list needs; detail carries full `content` + AC4/AC5/AC6 fields. Both include `link` and `astral_job_id` as stored.

## Execution contract

The plan is binding. The builder:

- Executes steps in order within a stage, and stages in order.
- Does not skip, reorder, combine, or expand steps.
- Does not add files, modules, configs, or dependencies that aren't in the plan.
- When a step is ambiguous, contradicts another step, references something that doesn't exist, or fails when executed literally — **stops, comments on the Linear parent issue, and waits.**
- Completes each stage on the epic worktree, commits, and publishes to `origin/sub/AST-1741/AST-1748-candidate-meteorite-list-detail-api` per **build-child**.

## Estimate

Confirm Chuckles estimate: 3 — agree
