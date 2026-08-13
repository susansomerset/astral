# AST-1353 — Save Base Resume writes base_resume snapshot

**Linear:** [AST-1353](https://linear.app/astralcareermatch/issue/AST-1353)
**Parent:** [AST-1340](https://linear.app/astralcareermatch/issue/AST-1340) — Create a table called astral_artifacts
**Publish ref:** `sub/AST-1340/AST-1353-save-base-resume-snapshot`

Wire the existing successful Save Base Resume path so that after live `candidate_data.artifacts.base_resume` is persisted, core records that blob into `astral_artifacts` via sibling AST-1352’s `save_astral_artifact` (`entity_type="candidate"`, `artifact_type="base_resume"`, `current=1`). Does **not** create the table/writers, does **not** add restore/Print UI, and does **not** snapshot on Generate/Regenerate.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/candidate.py` | Add `snapshot_saved_base_resume_astral_artifact`; extend module In-scope line | core |
| `src/ui/api/api_candidate.py` | After successful `save_candidate_data` when the PUT included `artifacts.base_resume`, call the new core helper | ui |

**Do not touch:** `src/data/database.py` (AST-1352 owns `save_astral_artifact` / table ensure), `src/ui/frontend/**` (no new Artifacts UI), craft/Generate/Regenerate persist paths that call `database.save_candidate` directly (`parse_candidate_resume`, craft_resume_base success writers in `candidate.py`), `src/utils/config.py`, Print routes (`api_resume_html.py` / AST-1337), `tests/**`, `docs/test-bible/**`, canon pattern catalog files.

**Dependency (already on tree):** AST-1352 is User Testing; `origin/ftr/AST-1340-astral-artifacts-table` (merged into this sub via `sync-child`) exposes `database.save_astral_artifact`, `get_current_astral_artifact`, and `list_astral_artifacts`. Do not reimplement versioning.

## Stage 1: Core snapshot helper + Save Base Resume wire

**Done when:** A successful `PUT /api/candidates/<id>/data` whose body includes `artifacts.base_resume` (the ArtifactEditor Save / autosave path) leaves exactly one `astral_artifacts` row with `current=1` for `(entity_type="candidate", entity_id=<id>, artifact_type="base_resume")` whose `artifact_data` equals the live post-save `artifacts.base_resume`. A second such Save retires the prior row to `current=0` and inserts a new current row (history still listable). Craft/Generate/Regenerate overwrites of live `artifacts.base_resume` that bypass this PUT do **not** call the helper (prior current row remains). No frontend changes.

1. In `src/core/candidate.py` module docstring **In-scope** line, append `snapshot_saved_base_resume_astral_artifact` (AST-1353) so the header inventory of public entry points stays honest.

2. In `src/core/candidate.py`, near the other artifact-save helpers (`apply_rubric_vectors_save` / `apply_company_search_terms_save` region — public functions first), add:

   ```python
   def snapshot_saved_base_resume_astral_artifact(candidate_id: str) -> str:
       """Record live artifacts.base_resume into astral_artifacts after Save Base Resume.

       Reads the post-persist candidate blob so the snapshot matches deep-merged
       candidate_data (AC2). Returns the new astral_artifact_uuid from the data layer.
       """
   ```

   Implementation (literal — do not invent extra kwargs or config):

   - `candidate = database.get_candidate(candidate_id)`; if missing, `raise ValueError` naming the candidate id.
   - `cd = candidate.get("candidate_data") or {}`; if not a `dict`, treat as `{}`.
   - `arts = cd.get("artifacts") or {}`; if not a `dict`, treat as `{}`.
   - `base = arts.get("base_resume")`; if `base is None`, `raise ValueError("artifacts.base_resume missing after save")`.
   - Return `database.save_astral_artifact("candidate", candidate_id, "base_resume", base)`.

   ⚠️ **Decision:** Snapshot **after** live persist and **re-read** via `get_candidate`, not the pre-save PUT payload. `save_candidate` deep-merges nested dicts; AC2 requires the row to match the saved live blob, not only the request fragment.

   ⚠️ **Decision:** Call only from the Save Base Resume API path (step 3). Do **not** invoke from `save_candidate_data` itself or from craft/Generate writers that use `database.save_candidate` — parent AC4 / Boundaries: Regenerate must not replace the last intentional Save snapshot.

   ⚠️ **Decision:** Artifact type string is the literal `"base_resume"` (same contract AST-1352 documented for this sibling). Do not add a new config block for a single epic-scoped type.

3. In `src/ui/api/api_candidate.py` `update_candidate_data`:

   - Import `snapshot_saved_base_resume_astral_artifact` from `src.core.candidate` alongside the existing candidate imports.
   - Before the artifacts processing block (same `try` as today’s save), initialize `base_resume_in_save = False`.
   - Inside the existing gate `if "base_resume" in arts and isinstance(arts["base_resume"], (list, dict)):`, after the ingest/filter assignments that update `arts["base_resume"]`, set `base_resume_in_save = True`.
   - Immediately after the successful `save_candidate_data(candidate_id, body, replace=False, debug=ui_llm_debug())` call (still inside `if body:`), when `base_resume_in_save` is True, call `snapshot_saved_base_resume_astral_artifact(candidate_id)`.
   - Do **not** catch snapshot failures separately — let them fall through the existing `except Exception` → `jsonify({"error": str(e)}), 400` so a failed preserve surfaces as a failed Save response (`astral.standards.data-raises-caller-logs`; UI already returns the error string).

   ⚠️ **Decision:** Wire in the API handler (thin) after core persist, mirroring how `apply_rubric_vectors_save` is orchestrated from `update_candidate_data`, rather than teaching every `save_candidate_data` caller about astral_artifacts. UI still never imports `database`.

4. Do **not** change ArtifactEditor, Base Resume Content Print, or craft_resume_base persistence. UAT for this child is DB/API-level (parent AC5): two successful Saves via the existing PUT, then `get_current_astral_artifact` / `list_astral_artifacts` (or SQL) to verify current-flag + history; optionally overwrite live base_resume via a craft path and confirm the prior `current=1` snapshot row is unchanged.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Review (build stub)

**Publish ref:** `origin/sub/AST-1340/AST-1353-save-base-resume-snapshot`
**Plan path:** `docs/features/artifacts/ast-1353-save-base-resume-writes-base-resume-snapshot.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `6e534039` | `snapshot_saved_base_resume_astral_artifact` + wire after Save Base Resume PUT |

**Tip:** `6e534039` on `origin/sub/AST-1340/AST-1353-save-base-resume-snapshot`

## Joan validate

**Rubric:** plan-rubric.v1
**Ticket:** AST-1353
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1340/AST-1353-save-base-resume-snapshot` @ `cced2c74`

## Traceability
AC2→Stage 1 (core re-read + `save_astral_artifact` after successful PUT persist); AC3→Stage 1 (second PUT with `base_resume` delegates retire-and-insert to AST-1352 writer); AC4→Stage 1 boundary (wire only `update_candidate_data` PUT; craft/Generate/Regenerate use `database.save_candidate` directly — verified `parse_candidate_resume`, `_persist_craft_dispatch_success`, `run_candidate_artifact_generation`); AC5→Stage 1 (no frontend changes; API/DB UAT).

## Findings

### acceptable
- **Location:** Plan structure — no Scope/Conf/Risk self-assessment
- **Finding:** Only `## Estimate` confirm; no formal axes block.
- **Recommendation:** Acceptable for a two-file, single-stage wire; estimate 2 matches footprint.

### discuss
- **Location:** Stage 1 step 3 — autosave path
- **Finding:** `ArtifactEditor` debounced autosave uses the same `PUT …/data` with `artifacts.base_resume`; each successful autosave will snapshot (and retire prior), not only explicit Save clicks.
- **Recommendation:** Plan explicitly names Save/autosave — intentional; operators may accumulate more history rows than manual Save alone. No plan change required unless product wants explicit-Save-only snapshots.

### discuss
- **Location:** Stage 1 step 3 — error handling after `save_candidate_data`
- **Finding:** Snapshot failure after a successful live persist returns 400 (Save failed) while `candidate_data` is already committed; no cross-table transaction.
- **Recommendation:** Reasonable fail-closed surface for this epic; note for UAT that a failed snapshot is a partial persist edge case, not a silent drop.

### acceptable
- **Location:** Stage 1 step 2 — literal `"base_resume"` / `"candidate"`
- **Finding:** No new config block for artifact types; plan documents epic-scoped literal contract matching AST-1352.
- **Recommendation:** Acceptable given sibling writer + parent scope; `ENTITY_TYPES` validation remains in data layer.

**R6 checklist (summary):** Definition fidelity ✓ — Save-path wire only; explicit do-not-touch for table, frontend, craft/Print, backfill. Layer compliance ✓ — `ui` → `core.candidate` → `database.save_astral_artifact`; no `ui`→`data`. Scope ✓ — does not reimplement AST-1352 writers; dependency present on publish ref (`save_astral_artifact` @ database.py). Pattern ✓ — mirrors `apply_rubric_vectors_save` orchestration from `update_candidate_data`. DRY ✓ — single core helper, no duplicate versioning.

**Statute pass (in-session):** All 18 universal orch statutes conform. Considered scoped statutes on `src/core/candidate.py` + `src/ui/api/api_candidate.py` modify — including `astral.layers.import-direction`, `astral.standards.in-scope-only`, `astral.standards.data-raises-caller-logs`, `astral.layers.ui-config-driven-business-logic`, `astral.standards.no-hardcoded-sets` — all `conforms`; no `violates`.

context_tokens≈52000
