# Artifacts table source references

**Linear:** [AST-1591](https://linear.app/astralcareermatch/issue/AST-1591/artifacts-table-source-references-support-jobartifactsjob-resume-and)
**Parent:** [AST-1588](https://linear.app/astralcareermatch/issue/AST-1588/support-jobartifactsjob-resume-and-jobartifactscover-letteras) — Support `job.artifacts.job_resume` and `job.artifacts.cover_letter` as artifacts
**Publish ref:** `sub/AST-1588/AST-1591-artifacts-table-source-references`

Data-layer support so each `artifacts` version can store an optional list of source `artifact_uuid` strings (seed bodies that informed that write). DDL/ensure migrates existing DBs; `save_artifact` persists the list; `get_current_artifact` / `get_artifact` return it. Does **not** register catalog keys (AST-1590) or wire tracker `job_resume` → `base_resume` citation (AST-1592).

## Explicit scope gate

Ticket **## Scope** names exactly:

- `src/data/database.py` — extend `artifacts` DDL/ensure for source-reference storage; `save_artifact` / get-current / get-by-uuid accept and return source artifact ids; header inventory updated; no unrelated schema churn
- `canon/directives/draft/patt.artifacts.traceability.md` — one-line alignment note only; do not promote draft to approved canon

Every row in **Files Changed** is one of those paths (plus this plan doc). Every Stage step is the kind of change Scope describes for that file.

**Out of this ticket (do not touch):** `src/utils/config.py` / `ARTIFACT_CONFIG`; `src/core/tracker.py` / `src/core/candidate.py` / `src/core/agent.py` / `src/core/builder.py`; `src/ui/api/api_jobs.py`; frontend; coat-check; UUID-existence or catalog validation on source ids; agent/task lineage columns beyond source artifact ids; promoting the draft pattern out of `canon/directives/draft/`. Engineer must not create or edit `tests/` or `docs/test-bible/**`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Add `source_artifact_ids` column (DDL + ensure migrate); extend `save_artifact` optional param; return field from get-current / get-by-uuid (and shared row mapper used by `list_artifacts`); update header inventory | data |
| `canon/directives/draft/patt.artifacts.traceability.md` | One-line note that AST-1588 lands source-artifact-id storage on `artifacts` for the job_resume→base_resume case | canon draft |

## Stage 1: Schema + header inventory

**Done when:** Fresh and existing DBs have an `artifacts.source_artifact_ids` TEXT column (JSON array of strings, default `[]`); module header inventory documents it; no other tables changed.

⚠️ **Decision:** Column name is `source_artifact_ids` (snake_case TEXT storing a JSON array of `artifact_uuid` strings). Matches parent wording (“list of source artifact ids”) and keeps storage on the `artifacts` row rather than a sidecar table (draft pattern left that choice to the implement ticket; parent AC is table storage on each version).

1. In `src/data/database.py` module header inventory, update the `artifacts` bullet so it lists `source_artifact_ids` TEXT (JSON array of artifact_uuid strings; default `[]`) beside the existing columns. Keep the current=1 / retire-and-insert note; cite AST-1591 for the new column.

2. In `_ensure_artifacts_table`, after the table exists under the name `artifacts` (both the “already `artifacts`” path and the `astral_artifacts` rename path) and before setting `_artifacts_schema_ensured = True`, ensure the column:

```python
cols = _column_names("artifacts")
if "source_artifact_ids" not in cols:
    conn.execute(
        "ALTER TABLE artifacts ADD COLUMN source_artifact_ids TEXT NOT NULL DEFAULT '[]'"
    )
```

Call `conn.commit()` after the ALTER (same pattern as `vector_feedback` batch_size/completed_at ensure). Re-fetch or reuse `cols` as needed so rename-of-uuid and add-column both run when required.

3. In the fresh `CREATE TABLE artifacts (...)` branch, add the column to the CREATE:

```sql
source_artifact_ids TEXT NOT NULL DEFAULT '[]'
```

Place it after `artifact_data` and before `current` (semantic grouping: body then provenance, then versioning timestamps).

4. Do **not** change indexes. Do **not** touch other tables. Do **not** reset `_artifacts_schema_ensured` outside this function’s normal flow.

## Stage 2: Persist + return source ids on save / get-current / get-by-uuid

**Done when:** `save_artifact(..., source_artifact_ids=None)` persists a JSON array on the new current row; callers that omit the arg still work and store `[]`; `get_current_artifact` and `get_artifact` return `source_artifact_ids` as a Python `list` of strings (legacy/missing → `[]`). No UUID-existence checks.

⚠️ **Decision:** No validation that source ids exist in `artifacts` or match any catalog key (parent: incremental add; validation would false-positive until the catalog is mature). Only normalize shape: `None` → `[]`; otherwise require a list/tuple of values that stringify+strip to non-empty strings (drop empties after strip so callers can pass sparse lists safely). Raise `ValueError` only for a non-list/non-tuple non-None argument — not for unknown uuids.

1. Extend `_ARTIFACT_SELECT` to include `source_artifact_ids` immediately after `artifact_data`:

```python
_ARTIFACT_SELECT = (
    "artifact_uuid, entity_type, entity_id, artifact_type, "
    "artifact_data, source_artifact_ids, current, created_at, updated_at"
)
```

2. Update `_artifact_row_dict(row)` for the new SELECT order:

- Keep parsing `artifact_data` from `row[4]`.
- Parse `source_artifact_ids` from `row[5]`: if the raw value is `None`/empty → `[]`; if already a list use it; if a string, `json.loads` and require a list (on decode failure → `[]`). Coerce each element to `str`.
- Shift `current` / `created_at` / `updated_at` to `row[6]` / `row[7]` / `row[8]`.
- Include `"source_artifact_ids": <list>` in the returned dict.

`list_artifacts` shares this SELECT/mapper — it will surface the field automatically; do not add a separate list API this ticket.

3. Change `save_artifact` signature to:

```python
def save_artifact(
    entity_type: str,
    entity_id: str,
    artifact_type: str,
    artifact_data: Any,
    source_artifact_ids: Optional[Sequence[str]] = None,
) -> str:
```

Import `Sequence` from `typing` if not already present (keep existing typing style in the file).

4. Inside `save_artifact`, after validating `artifact_data`, normalize sources:

```python
if source_artifact_ids is None:
    sources: list[str] = []
elif isinstance(source_artifact_ids, (list, tuple)):
    sources = [str(x).strip() for x in source_artifact_ids if str(x).strip()]
else:
    raise ValueError("source_artifact_ids must be a list of strings or None")
sources_payload = json.dumps(sources)
```

5. Extend the INSERT to include `source_artifact_ids`:

```sql
INSERT INTO artifacts (
    artifact_uuid, entity_type, entity_id, artifact_type,
    artifact_data, source_artifact_ids, current, created_at, updated_at)
VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)
```

Bind `sources_payload` in the matching position. Keep blind retire-by-key + insert (no prior-id SELECT; no in-place body UPDATE). Docstring: note optional `source_artifact_ids` (JSON array on the new row; default empty; no existence validation — AST-1591 / patt.artifacts.traceability table support).

6. Do **not** change `retire_current_artifact`. Do **not** add logging in the data layer. Do **not** change core/UI callers this ticket — existing positional `save_artifact(et, eid, at, data)` calls remain valid and store `[]`.

## Stage 3: Draft pattern alignment note

**Done when:** `canon/directives/draft/patt.artifacts.traceability.md` has a single new alignment sentence tying AST-1588 table storage to the job_resume→base_resume case; file stays under `draft/`; no other canon files edited.

1. In `canon/directives/draft/patt.artifacts.traceability.md`, under **Exceptions** or **Implementation** (prefer a new bullet under **Implementation** after the existing “Draft” bullet), add exactly one alignment line, e.g.:

   - **AST-1588** — Lands `source_artifact_ids` persistence on the `artifacts` table (data layer) so job_resume versions can cite base_resume; agent/task lineage and full token-catalog harvest remain out of that epic.

2. Do **not** move the file out of `draft/`. Do **not** rewrite the Abstract/Arc. Do **not** mark the pattern approved.

## Estimate

Confirm Chuckles estimate: 3 — agree
