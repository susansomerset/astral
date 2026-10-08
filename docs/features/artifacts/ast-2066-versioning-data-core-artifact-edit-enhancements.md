# AST-2066 — Versioning: data/core (Artifact Edit Enhancements)

- **Ticket:** [AST-2066](https://linear.app/astralcareermatch/issue/AST-2066)
- **Parent:** [AST-2043 — Artifact Edit Enhancements](https://linear.app/astralcareermatch/issue/AST-2043)
- **Publish ref:** `origin/sub/AST-2043/AST-2066-versioning-core`

This ticket adds the backend for version arrows. It adds data-layer functions that move `current=1` to a named older or newer row of an `artifact` key or a `rubric_vector` criterion, without changing any body. It adds a chronological history listing for one rubric criterion, and core list-versions and set-current functions for candidate catalog keys, job catalog keys, and one rubric criterion. It also adds the identical-to-current no-op to `tracker.save_job_artifact`. Saves after a move need no change, because retire+insert (`save_artifact`) and the fingerprint retire+insert (`sync_rubric_vectors_from_criteria`) already append the new row at the end. HTTP routes belong to sibling #2 and UI to sibling #3; neither is planned here.

## Canon Scope (this ticket)

`patt.artifact.write-operative`, `patt.artifact.read-current`, `patt.artifact.read-operative`, `patt.artifact.traceability`, `stat.logging.info.entity`.

Resolved at `canon/directives/active/<id>.md`. The repo has no `docs/canon-index.md`, so the paths come from the parent's Architectural definition links.

## Explicit scope gate

Every file and change kind below comes from this ticket's `## Scope`:

- `src/data/database.py` — "move-current primitives for `artifact` rows and for `rubric_vector` rows, plus chronological history listing for one rubric criterion." This covers Stage 1 and Stage 2. The `rowid` tie-break added to `list_artifacts` is part of the chronological history listing (see the Decision in Stage 1).
- `src/core/candidate.py` — "list versions / set current version for candidate catalog keys and for one rubric criterion." This covers Stage 3.
- `src/core/tracker.py` — "list versions / set current version for job catalog keys. Identical-to-current no-op in `save_job_artifact`." This covers Stage 4.

No other files are touched.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | New `set_current_artifact`, new `set_current_rubric_vector`, `code=` filter + chronological order on `list_rubric_vectors`, `rowid` tie-break on `list_artifacts` | data |
| `src/core/candidate.py` | New `artifact_versions_by_uuid`, `_candidate_catalog_entry`, `list_candidate_artifact_versions`, `set_candidate_artifact_current`, `list_rubric_criterion_versions`, `set_rubric_criterion_current` | core |
| `src/core/tracker.py` | New `_job_catalog_entry`, `list_job_artifact_versions`, `set_job_artifact_current`. Identical-to-current no-op in `save_job_artifact` | core |

## Shared conventions (apply to every stage)

- **Version map shape.** All list-versions functions return a `dict` keyed by row uuid, in chronological order (oldest first, using Python dict insertion order). Each value is `{"created_at": <str>, "current": <int 0|1>, "position": <int, 1-based>}`. The total count is `len(result)`. An empty key returns `{}`.
  - ⚠️ **Decision:** The parent Technical scope lists the fields as "(uuid, created_at, current, position)". Susan's standing rule is that array elements are indexed by their IDs rather than carrying the id as a field of an unindexed item. So the uuid is the dict key, not a field. `position` makes order explicit even if a consumer re-sorts keys.
- **Errors.** Every validation failure raises `ValueError` with a message naming the bad input. Sibling #2 maps `ValueError` to 400. Core does not check whether the job or candidate exists. Sibling #2 already loads the entity and returns 404.
- **Timestamps.** `_utc_now()` has whole-second resolution (`%Y-%m-%d %H:%M:%S`), so two versions saved in the same second share a `created_at`. All chronological ordering in this ticket is `ORDER BY created_at ASC, rowid ASC`. `rowid` is insertion order: `artifact` and `rubric_vector` both use a `TEXT PRIMARY KEY` without `WITHOUT ROWID`, so both have an implicit `rowid`.
- **Never touch bodies.** No statement in this ticket writes `artifact_data`, `source_artifact_ids`, `content`, `label`, or `content_fingerprint` (`patt.artifact.read-operative`, `patt.artifact.traceability`). The only columns written are `current`, `updated_at`, and for rubric rows `importance` (see the Decision in Stage 2).

---

## Stage 1: Artifact move-current primitive + deterministic history order

**Done when:** `database.set_current_artifact(et, eid, at, uuid)` makes exactly that row current for its key in one transaction and raises `ValueError` for a uuid outside the key, without changing anything. `list_artifacts` orders same-second rows by insertion order.

1. In `src/data/database.py`, `list_artifacts`, change the line `sql += " ORDER BY created_at ASC"` to `sql += " ORDER BY created_at ASC, rowid ASC"`. Change nothing else in that function.

   ⚠️ **Decision:** This adds a tie-break to an existing function instead of writing a second artifact-history lister. The parent Technical scope says "Artifact history reuses `list_artifacts`". Without the tie-break, same-second versions have no defined order, so arrow positions could change between calls. Existing callers only gain deterministic order for ties.

2. In `src/data/database.py`, directly after `list_artifacts`, add:

   ```python
   def set_current_artifact(
       entity_type: str, entity_id: str, artifact_type: str, artifact_uuid: str
   ) -> str:
       """Move current=1 to artifact_uuid within its natural key (AST-2066).

       One transaction: mark the target current, retire every other current row for
       (entity_type, entity_id, artifact_type). Never touches artifact_data or
       source_artifact_ids (patt.artifact.read-operative / traceability). Raises
       ValueError when the uuid is not a row of this key; nothing changes then.
       """
       et, eid, at = _normalize_artifact_identity(entity_type, entity_id, artifact_type)
       uid = (artifact_uuid or "").strip()
       if not uid:
           raise ValueError("artifact_uuid required")
       now = _utc_now()

       def _with_conn() -> str:
           conn = _get_connection()
           try:
               _ensure_artifact_table(conn)
               # Key match lives in the WHERE, so a foreign uuid updates 0 rows (cross-key guard).
               cur = conn.execute(
                   """UPDATE artifact
                         SET current = 1, updated_at = ?
                       WHERE artifact_uuid = ?
                         AND entity_type = ? AND entity_id = ? AND artifact_type = ?""",
                   (now, uid, et, eid, at),
               )
               if cur.rowcount == 0:
                   conn.rollback()
                   raise ValueError(f"artifact_uuid {uid!r} is not a version of {et}/{eid}/{at}")
               conn.execute(
                   """UPDATE artifact
                         SET current = 0, updated_at = ?
                       WHERE entity_type = ? AND entity_id = ? AND artifact_type = ?
                         AND current = 1 AND artifact_uuid != ?""",
                   (now, et, eid, at, uid),
               )
               conn.commit()
               return uid
           finally:
               conn.close()

       return _run_with_retry(_with_conn)
   ```

   ⚠️ **Decision:** The function issues a guarded UPDATE first and checks `rowcount`, rather than SELECTing and then updating. Python `sqlite3` opens its implicit transaction at the first DML statement, so both UPDATEs and the guard share one transaction with no read-then-write race. `ValueError` is not caught by `_run_with_retry` (that catches only `sqlite3.OperationalError` / `IntegrityError`), so it reaches the caller after rollback. Setting a row that is already current is allowed: the call succeeds and only `updated_at` changes.

## Stage 2: Rubric criterion move-current primitive + per-criterion history

**Done when:** `database.list_rubric_vectors(cid, task, code="V01", current_only=False)` returns V01's rows oldest first. `database.set_current_rubric_vector(cid, task, "V01", uuid)` makes exactly that row current for V01, leaves every other code untouched, and raises `ValueError` for a uuid outside `(cid, task, V01)`.

1. In `src/data/database.py`, `list_rubric_vectors`, add a keyword parameter `code: Optional[str] = None` after `current_only`. Inside `_with_conn`, replace:

   ```python
               if current_only:
                   sql += " AND current = 1"
               sql += " ORDER BY code ASC"
   ```

   with:

   ```python
               if current_only:
                   sql += " AND current = 1"
               if code is not None:
                   # One criterion's history, chronological (AST-2066); code match is case-insensitive like sync.
                   sql += " AND UPPER(code) = ? ORDER BY created_at ASC, rowid ASC"
                   params.append(str(code).strip().upper())
               else:
                   sql += " ORDER BY code ASC"
   ```

   Change nothing else. Existing callers pass no `code` and keep the same behavior.

   ⚠️ **Decision:** This extends `list_rubric_vectors` instead of adding a new lister. The parent Technical scope allows either. Extending reuses the 12-field row mapping instead of copying it. Codes are compared uppercased because `sync_rubric_vectors_from_criteria` keys `current_by_code` on `code.upper()`.

2. In `src/data/database.py`, directly after `list_rubric_vectors`, add:

   ```python
   def set_current_rubric_vector(
       candidate_id: str, task_key: str, code: str, rubric_vector_uuid: str
   ) -> str:
       """Move current=1 to rubric_vector_uuid within (candidate_id, task_key, code) (AST-2066).

       One transaction. Never touches content/label/fingerprint. Importance is not
       versioned: the leaving current row's importance carries onto the target.
       Raises ValueError when the uuid is not a row of this criterion.
       """
       cid = (candidate_id or "").strip()
       tk = (task_key or "").strip()
       ck = (code or "").strip().upper()
       uid = (rubric_vector_uuid or "").strip()
       if not cid or not tk or not ck or not uid:
           raise ValueError("candidate_id, task_key, code and rubric_vector_uuid required")
       now = _utc_now()

       def _with_conn() -> str:
           conn = _get_connection()
           try:
               _ensure_rubric_vector_table(conn)
               # Carry live importance from the leaving current row; target keeps its own when none.
               cur = conn.execute(
                   """UPDATE rubric_vector
                         SET current = 1, updated_at = ?,
                             importance = COALESCE((
                                 SELECT importance FROM rubric_vector
                                  WHERE candidate_id = ? AND task_key = ? AND UPPER(code) = ?
                                    AND current = 1 AND rubric_vector_uuid != ?
                                  LIMIT 1), importance)
                       WHERE rubric_vector_uuid = ?
                         AND candidate_id = ? AND task_key = ? AND UPPER(code) = ?""",
                   (now, cid, tk, ck, uid, uid, cid, tk, ck),
               )
               if cur.rowcount == 0:
                   conn.rollback()
                   raise ValueError(f"rubric_vector_uuid {uid!r} is not a version of {cid}/{tk}/{ck}")
               conn.execute(
                   """UPDATE rubric_vector
                         SET current = 0, updated_at = ?
                       WHERE candidate_id = ? AND task_key = ? AND UPPER(code) = ?
                         AND current = 1 AND rubric_vector_uuid != ?""",
                   (now, cid, tk, ck, uid),
               )
               conn.commit()
               return uid
           finally:
               conn.close()

       return _run_with_retry(_with_conn)
   ```

   ⚠️ **Decision:** Importance carries over. The parent says "Importance is not versioned." Today `sync_rubric_vectors_from_criteria` updates importance in place on the current row only. Without the carry, stepping back would quietly restore an old importance value. Copying the leaving row's importance onto the target keeps importance as a property of the criterion. Only `importance`, `current`, and `updated_at` are written, never `content`, `label`, or `content_fingerprint`. If Archie prefers importance to travel with the version instead, delete the `importance = COALESCE(...)` assignment. Nothing else in the plan depends on it.

## Stage 3: Candidate core — list versions / set current (catalog keys + rubric criterion)

**Done when:** For a candidate catalog key, `list_candidate_artifact_versions` returns the version map and `set_candidate_artifact_current` moves current and logs one entity line. For a rubric criterion, `list_rubric_criterion_versions` and `set_rubric_criterion_current` do the same through `RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY`. Job keys, unknown keys, and blank inputs raise `ValueError`.

1. In `src/core/candidate.py`, directly after `get_candidate_current_artifact_uuid` (ends `return uuid`), add the shared version-map builder. `tracker.py` reuses it in Stage 4:

   ```python
   def artifact_versions_by_uuid(rows: list, uuid_field: str) -> Dict[str, Dict[str, Any]]:
       """Chronological rows → {uuid: {created_at, current, position}} (AST-2066; position 1-based)."""
       return {
           row[uuid_field]: {
               "created_at": row.get("created_at"),
               "current": row.get("current"),
               "position": i,
           }
           for i, row in enumerate(rows, start=1)
       }
   ```

2. Directly after it, add the candidate catalog resolver. It mirrors `get_candidate_current`, plus an `entity_type == "candidate"` check:

   ```python
   def _candidate_catalog_entry(candidate_id: str, artifact_key: str) -> Tuple[str, str, str]:
       """Resolve (entity_type, candidate_id, artifact_type) for a candidate catalog key (AST-2066)."""
       key = (artifact_key or "").strip()
       if not key:
           raise ValueError("artifact_key required")
       entry = ARTIFACT_CONFIG.get(key)
       if entry is None:
           raise ValueError(f"unknown catalog key: {key!r}")
       if not entry.get("candidate_scoped") or entry.get("entity_type") != "candidate":
           raise ValueError(f"catalog key not candidate-owned: {key!r}")
       cid = (candidate_id or "").strip()
       if not cid:
           raise ValueError("candidate_id required")
       return entry["entity_type"], cid, key.rsplit(".", 1)[-1]
   ```

   ⚠️ **Decision:** Add the `entity_type == "candidate"` check. `get_candidate_current` checks only `candidate_scoped`, but both job keys are also `candidate_scoped: True`. Without the check, `job.artifacts.cover_letter` with a candidate id would quietly list nothing instead of being rejected. `get_candidate_current` is not refactored to use this helper (that would be out of scope).

3. Directly after it, add:

   ```python
   def list_candidate_artifact_versions(
       candidate_id: str, artifact_key: str
   ) -> Dict[str, Dict[str, Any]]:
       """Version map for a candidate catalog key, oldest first (AST-2066 / patt.artifact.read-current)."""
       et, cid, at = _candidate_catalog_entry(candidate_id, artifact_key)
       return artifact_versions_by_uuid(database.list_artifacts(et, cid, at), "artifact_uuid")


   def set_candidate_artifact_current(
       candidate_id: str, artifact_key: str, artifact_uuid: str
   ) -> str:
       """Move current to artifact_uuid for a candidate catalog key; body untouched (AST-2066)."""
       et, cid, at = _candidate_catalog_entry(candidate_id, artifact_key)
       uid = database.set_current_artifact(et, cid, at, artifact_uuid)
       # Same post-rotate AUTO revalidation as the save_candidate_data str-path (AST-1781).
       try:
           database.revalidate_dispatch_tasks_for_artifact(cid, artifact_key.strip())
       except Exception as exc:
           logger.warning(
               "%s | artifact_key=%r %s: %s — AUTO revalidation skipped after set-current",
               cid,
               artifact_key,
               type(exc).__name__,
               exc,
           )
       logger.info(
           "%s | candidate %s: %s -> %s (batch: %s)",
           cid,
           "artifact current set",
           artifact_key.strip(),
           uid,
           "-",
       )
       return uid
   ```

   ⚠️ **Decision:** set-current calls `revalidate_dispatch_tasks_for_artifact`, the same as the `save_candidate_data` str-path. Moving current changes the body that every prompt token consumer reads, which is the same effect as a save rotate. The `try/except` + `logger.warning` block copies the existing save-path block exactly.

   ⚠️ **Decision:** Logging follows `stat.logging.info.entity`: one `logger.info` line in the `<id> | candidate <event>: <detail> (batch: -)` form, using `"-"` for batch like the existing save-path lines.

4. Directly after it, add the rubric criterion pair:

   ```python
   def _rubric_owner_task(artifact_key: str) -> str:
       """Owner task_key for a rubric criteria artifact key (AST-2066 / AST-723)."""
       owner = RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY.get((artifact_key or "").strip())
       if not owner:
           raise ValueError(f"not a rubric criteria key: {artifact_key!r}")
       return owner


   def list_rubric_criterion_versions(
       candidate_id: str, artifact_key: str, code: str
   ) -> Dict[str, Dict[str, Any]]:
       """Version map for one rubric criterion (shared code), oldest first (AST-2066)."""
       owner = _rubric_owner_task(artifact_key)
       cid = (candidate_id or "").strip()
       ck = (code or "").strip()
       if not cid or not ck:
           raise ValueError("candidate_id and code required")
       rows = database.list_rubric_vectors(cid, owner, current_only=False, code=ck)
       return artifact_versions_by_uuid(rows, "rubric_vector_uuid")


   def set_rubric_criterion_current(
       candidate_id: str, artifact_key: str, code: str, rubric_vector_uuid: str
   ) -> str:
       """Move current to rubric_vector_uuid for one criterion; other codes untouched (AST-2066)."""
       owner = _rubric_owner_task(artifact_key)
       cid = (candidate_id or "").strip()
       uid = database.set_current_rubric_vector(cid, owner, code, rubric_vector_uuid)
       logger.info(
           "%s | candidate %s: %s %s -> %s (batch: %s)",
           cid,
           "rubric criterion current set",
           artifact_key.strip(),
           (code or "").strip().upper(),
           uid,
           "-",
       )
       return uid
   ```

   No AUTO revalidation here: `apply_rubric_vectors_save` (the rubric save path) does not call it, so set-current matches. `RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY`, `Dict`, `Any`, and `Tuple` are already imported in `candidate.py`. Do not add imports.

## Stage 4: Tracker core — job list versions / set current + identical no-op

**Done when:** `tracker.list_job_artifact_versions` and `tracker.set_job_artifact_current` work for both job catalog keys and reject candidate keys. PUTting the same cover letter body twice adds exactly one `artifact` row.

1. In `src/core/tracker.py`, `save_job_artifact`, insert directly after:

   ```python
       cid = _candidate_id_for_job(jid)
       if not cid:
           raise ValueError("candidate_id required")
   ```

   and before `if key == "job.artifacts.job_resume":` (the sources block):

   ```python
       # AST-2066 / patt.artifact.write-operative #4: identical-to-current → existing pin, no retire+insert.
       current_row = database.get_current_artifact(entry["entity_type"], jid, artifact_type)
       if current_row is not None and current_row.get("artifact_data") == prepared:
           return current_row.get("artifact_uuid")
   ```

   ⚠️ **Decision:** The comparison uses the **prepared** body (after `_prepare_job_resume_content` / `normalize_cover_letter_artifact`), because that is what `save_artifact` would persist. It sits after the candidate check and before the `job_resume` base-resume citation, so a no-op skips the extra base_resume read. Identical bodies are a no-op even when the caller passes different `source_artifact_ids`, as in the candidate reference implementation. Existing callers (`api_jobs.py` PUTs, `persist_job_artifact_from_parsed`, `agent.py` land) only test the return for truthiness or `None`, and the existing uuid is truthy, so their behavior is unchanged.

2. Directly after `save_job_artifact`, add:

   ```python
   def _job_catalog_entry(astral_job_id: str, artifact_key: str) -> Tuple[str, str, str]:
       """Resolve (entity_type, astral_job_id, artifact_type) for a job catalog key (AST-2066)."""
       key = (artifact_key or "").strip()
       if not key:
           raise ValueError("artifact_key required")
       entry = ARTIFACT_CONFIG.get(key)
       if entry is None:
           raise ValueError(f"unknown catalog key: {key!r}")
       if entry.get("entity_type") != JOB_ARTIFACT_ENTITY_TYPE:
           raise ValueError(f"catalog key not job-scoped: {key!r}")
       jid = (astral_job_id or "").strip()
       if not jid:
           raise ValueError("astral_job_id required")
       return entry["entity_type"], jid, key.rsplit(".", 1)[-1]


   def list_job_artifact_versions(
       astral_job_id: str, artifact_key: str
   ) -> Dict[str, Dict[str, Any]]:
       """Version map for a job catalog key, oldest first (AST-2066; mirrors get_job_current)."""
       et, jid, at = _job_catalog_entry(astral_job_id, artifact_key)
       return candidate_mod.artifact_versions_by_uuid(
           database.list_artifacts(et, jid, at), "artifact_uuid"
       )


   def set_job_artifact_current(
       astral_job_id: str, artifact_key: str, artifact_uuid: str
   ) -> str:
       """Move current to artifact_uuid for a job catalog key; body untouched (AST-2066)."""
       et, jid, at = _job_catalog_entry(astral_job_id, artifact_key)
       return database.set_current_artifact(et, jid, at, artifact_uuid)
   ```

   ⚠️ **Decision:** `set_job_artifact_current` does not log. `stat.logging.info.entity` Notes say "`src/core/tracker` does not log; core callers emit this line", and its `applies_when.paths` leave out `tracker.py`. The completing route in sibling #2 logs per `stat.logging.info.api`. `get_job_current` and `save_job_artifact` are not refactored to use `_job_catalog_entry` (out of scope).

   `Tuple`, `Dict`, `Any`, `ARTIFACT_CONFIG`, `JOB_ARTIFACT_ENTITY_TYPE`, and `candidate_mod` are already imported in `tracker.py`. Do not add imports.

## Verification (build-child §7)

- `python3 -m py_compile src/data/database.py src/core/candidate.py src/core/tracker.py`
- No `.ts`/`.tsx` changes, so no `tsc`.
- Run each stage's **Done when** by hand in a Python REPL against a scratch DB (`debug/spikes/AST-2066/`, never committed).

## Notes for QA (Betty — informational only, no test-tree work in this ticket)

- AC 5 ("v4 `created_at` greater than v3's"): `created_at` has whole-second resolution, so a fast test may see equal timestamps. Order is still correct through the `rowid` tie-break (`list_artifacts` / version map `position`).
- AC 6: the importance carry (Stage 2 Decision) means V01's current `importance` after set-current equals the value before the move.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-2066
**Overall:** APPROVED
**Corpus:** 2d1b73da19cf1d14276e5c26f52b37aa8047d159
**Publish ref:** 54510c2abeb5e928e4a2b405af294f03f06a0765

## Canon scores

patt.artifact.write-operative | A | | 
patt.artifact.read-current | A | | 
patt.artifact.read-operative | A | | 
patt.artifact.traceability | A | | 
stat.logging.info.entity | A | | 

## Traceability

AC4→St1+St3+St4; AC5→no new stages (intro + existing save_artifact / sync_rubric_vectors_from_criteria); AC6→St2+St3; AC7→St4

## Findings

### acceptable
- **Location:** Plan (whole doc)
- **Finding:** No Conf/Risk self-assessment block (Estimate confirm only).
- **Recommendation:** Optional parity with larger plans; not blocking for this bounded data/core slice.

### discuss
- **Location:** Stage 2 Decision (importance carry)
- **Finding:** Plan flags an Archie preference fork (carry live importance vs travel with version); parent already resolved “importance is not versioned.”
- **Recommendation:** Default carry matches parent intent; Susan/Archie can close the fork at build without plan rewrite.

- **Location:** Verification
- **Finding:** AC5 is satisfied by existing write paths but has no explicit REPL bullet (unlike AC4 chain in sibling QA notes).
- **Recommendation:** Optional one-line manual verify after St3 set-current + save; Betty can cover in qa-child.

context_tokens≈42000

## Review

- **Branch:** `origin/sub/AST-2043/AST-2066-versioning-core`
- **Build commits:** `321430c6b` (Stage 1), `4b2531211` (Stage 2), `2b19732fe` (Stage 3), `cb147dada` (Stage 4)
- **Verified by hand (scratch DB, not committed):** each stage's Done when, plus AC 4 (one current row, no row or body change), AC 5 (an edit after a back move appends at the end, same-second rows ordered by `rowid`), AC 6 (V01 moves alone, importance carried), AC 7 (identical cover letter save adds one row, not two), and the cross-key / cross-code guards (`ValueError`, current unchanged).
- **Build note:** `sync-child.sh --ftr AST-2043` skips the parent merge because the parent branch is `ftr/AST-2043-artifact-versions`. It is already an ancestor of this branch, so nothing was missed.
