# AST-2261 — Version-scoped grade rollup and nav counts

- **Linear:** [AST-2261](https://linear.app/astralcareermatch/issue/AST-2261) · parent [AST-2257](https://linear.app/astralcareermatch/issue/AST-2257)
- **Publish ref:** `origin/sub/AST-2257/AST-2261-version-scoped-grade-rollup`
- **Assignee:** Ada

Read both Criteria screens need, and nothing they draw. For one candidate and one rubric, return each current vector's grading-run count, per-letter counts, and last-seen timestamp, counted only from consumer-task runs that recorded that vector version. Attach the live current-vector count to the seven criteria nav paths. Company Discovery Terms stays uncounted. The thermometer, `ArtifactEditor`, and `App.css` belong to the sibling ticket.

## Explicit scope gate

Ticket **## Scope** (only surfaces this plan may touch):

| File | Kind of change Scope allows |
|------|-----------------------------|
| `src/core/candidate.py` | **modified** — one new function. For the candidate and rubric, read each vector's current version, count grading runs of that rubric's consumer tasks whose recorded vector version is that one, tally letter grades on the grades those tasks save, and take the latest run timestamp per letter. Company Gazing reads company grades; the other six read job grades. Craft runs are not counted. Runs with no recorded vector version are not counted. |
| `src/ui/api/api_candidate.py` | **modified** — one new read that returns that function's result for the selected candidate and the screen's rubric. It does not change the candidate document payload. |
| `src/ui/api/api_system.py` | **modified** — the existing nav resolver gains a count on each of the seven criteria paths, equal to how many vectors are current for that screen's rubric. Other nav counts stay as they are. |

Every **Files Changed** row and Stage step names only those files and that kind of change. No `RubricGradeThermometer.tsx`, no `ArtifactEditor.tsx`, no `App.css`, no `src/data/database.py`, no `src/utils/config.py`.

## Canon Scope (patterns read at plan)

Ticket Citations: `patt.artifact.read-current`.

- **`patt.artifact.read-current`:** The live vector list is the current `rubric_vector` row (`current = 1`), via the existing `list_rubric_vectors(..., current_only=True)` / `rubric_criteria_for_task` path. The version a run used is the `rubric_vector_uuid` recorded on `vector_feedback` at capture time (`list_rubric_vector_uuid_by_code` of the then-current row). Do not read `candidate_data` / `job_data` / `company_data` blobs as the version pin, and do not hydrate this rollup from a stale copy of the rubric.

Parent Architectural definition lists no in-force statutes. Every other directive id stays **id-only** until build-child §8.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/candidate.py` | Add `rollup_current_vector_grades` | core |
| `src/ui/api/api_candidate.py` | `GET /api/candidates/<candidate_id>/rubric/<artifact_key>/grade_rollup` | ui |
| `src/ui/api/api_system.py` | Current-vector counts on the seven criteria nav paths | ui |

## Stages

### Stage 1: Version-scoped rollup

**Done when:** `rollup_current_vector_grades(candidate_id, artifact_key)` returns one entry per current vector on that rubric, and a vector's `run_count` / letter tallies include only consumer-task runs whose `vector_feedback.rubric_vector_uuid` is that vector's current uuid.

1. In `src/core/candidate.py`, immediately after `set_rubric_criterion_current`, add `rollup_current_vector_grades(candidate_id: str, artifact_key: str) -> Dict[str, Any]`. No new log lines.

2. Resolve the owner with the existing `_rubric_owner_task(artifact_key)` (raises `ValueError` for a non-rubric key). Let `cid = (candidate_id or "").strip()`. If `cid` is empty, raise `ValueError("candidate_id required")`.

3. Current vectors, in this order: `criteria = rubric_criteria_for_task(cid, owner)`. Current uuid by uppercased code from `database.list_rubric_vectors(cid, owner, current_only=True)`: first row wins if two current rows share a code. A criterion with no table uuid (embedded row never synced) still appears, with `rubric_vector_uuid` JSON `null`, `run_count` `0`, and `letters` `[]`.

4. Consumer task keys: every `TASK_CONFIG` key `tk` where `rubric_owner_task_key(tk) == owner` and `tk` is not in `CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY`. That set includes the owner and twins that share its `rubric_artifact` (`meteorite_grade_do`, `meteorite_grade_get`, `meteorite_like`, `evaluate_meteorite`, and the same shape for the other owners). It excludes every `craft_*` rubric task.

   ⚠️ **Decision:** `task_keys_for_rubric_owner` returns the owner plus craft tasks only, so twins would be dropped and craft would be included. Filter `TASK_CONFIG` with `rubric_owner_task_key` instead, then drop `CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY`.

5. Recorded version pins: `database.list_vector_feedback(candidate_id=cid, owner_task_key=owner)`. Keep a row only when `task_key` is in the consumer set from step 4 and `rubric_vector_uuid` is a non-empty string. Rows with no uuid are not counted. Group the kept rows by `rubric_vector_uuid`. For each uuid, the runs are the distinct `batch_id` values; the run timestamp is the max of `completed_at` or, when that is missing, `created_at`, compared as strings (`YYYY-MM-DD HH:MM:SS`).

6. Letter grades for those batches: for each distinct `(batch_id, task_key)` that pins at least one uuid still being rolled up, call `database.get_agent_data_by_batch(batch_id, block_type="RESPONSE")`. Keep rows whose `task_key` equals that consumer task. `json.loads` `block_data` when it is a string whose first non-space character is `{` or `[`. On `JSONDecodeError`, or when the value is not a dict, skip that block. Walk `parsed["jobs"]` and `parsed["companies"]` when each is a list. Entity id is `astral_job_id` on a job dict and `company_id` on a company dict; skip a dict with an empty id. Each `grades` entry that is a dict contributes at most one letter.

   ⚠️ **Decision:** `job_data` / `company_data` keep only the latest grade set, so a later run on a new version would erase the previous version's letters. AC 4 needs the old version's letters after the version arrows move. The grades the task saved for that run are the decoded JSON stored on the success `RESPONSE` block (`json.dumps(parsed)` in `do_task`). Company Gazing's consumer is `prefilter_company` (`companies` / `prefilter_grades`). The other six rubrics' consumers are job tasks (`jobs` / `*_grades`). Do not read `vector_feedback.value` — those are rubric-feedback codes, not A–X.

7. Match a grade line to one current criterion, not the whole rubric. Copy the consult label rule inline (do not import `consult`; `consult` already imports `candidate`):

   ```python
   _CODE_SUFFIX = re.compile(r"\s*\([A-Z]{2}\)\s*$")
   def _strip_code(name: str) -> str:
       return _CODE_SUFFIX.sub("", name).strip()
   ```

   A grade matches the criterion when `_strip_code(grade["vector"])` equals `_strip_code(criterion["label"])` or the stripped vector uppercased equals the criterion code uppercased. Letter is `str(grade["grade"] or "").strip().upper()`. Keep it only when it is in `ASTRAL_CONFIG["valid_grades"]` (`A`, `B`, `C`, `D`, `F`, `X`). Any other letter is not tallied and is not a run.

8. One run is one `(batch_id, entity_id, code)`. If two `RESPONSE` blocks in the same batch name that pair, keep the letter from the block with the later `created_at` and still count one run. The run counts toward the criterion whose current `rubric_vector_uuid` is the uuid that batch pinned for that code. A batch pinned to a different uuid of the same code does not count. A batch with no feedback row for that uuid does not count.

9. Return this dict and nothing else:

   ```python
   {
       "artifact_key": artifact_key.strip(),
       "vectors": [
           {
               "code": code,                  # as on the criterion
               "label": label,                # as on the criterion
               "rubric_vector_uuid": uuid or None,
               "run_count": int,              # number of (batch_id, entity_id) runs
               "letters": [                   # only letters with count > 0
                   {"grade": "A", "count": int, "last_seen": timestamp_str},
               ],
           },
       ],
   }
   ```

   `letters` order is `ASTRAL_CONFIG["valid_grades"]` order. `last_seen` is the max run timestamp among runs whose kept letter is that grade. `run_count` equals the sum of `letters[].count`. A vector with no counted runs has `run_count` `0` and `letters` `[]`.

### Stage 2: Criteria-editor read

**Done when:** `GET /api/candidates/<id>/rubric/<artifact_key>/grade_rollup` returns the Stage 1 dict for that candidate and rubric, and `GET /api/candidates/<id>` is unchanged.

1. In `src/ui/api/api_candidate.py`, import `rollup_current_vector_grades` next to the other `src.core.candidate` imports.

2. Add this route after `put_rubric_criterion_current_api` (before the candidate `POST`):

   - Path: `/<candidate_id>/rubric/<artifact_key>/grade_rollup`
   - Methods: `GET`
   - Decorator: `@require_auth`
   - Missing candidate: `404` `{"error": f"Candidate not found: {candidate_id}"}`, same as `get_rubric_criterion_versions_api`.
   - `ValueError` from the rollup: `400` `{"error": str(exc)}`, no log.
   - Any other exception: `logger.exception` with the same shape as `get_rubric_criterion_versions_api` (candidate id, route, exception type and message, and the line `Returning 500; the criteria editor has no grade rollup`), then `server_error_from_exception(exc)`.
   - Success: `jsonify` the rollup dict. Do not log an info line.

3. Do not edit the `GET /<candidate_id>` handler or `hydrate_rubric_artifacts_for_response`. The candidate document payload stays as it is.

### Stage 3: Criteria nav counts

**Done when:** `/api/nav_config?candidate_id=<id>` puts `count` on each of the seven criteria paths, equal to `len(rubric_criteria_for_task(...))` for that path's rubric, including `0`, and Company Discovery Terms has no `count` key. Recommendations and every other existing badge are unchanged.

1. In `src/ui/api/api_system.py`, import `rubric_criteria_for_task` from `src.core.candidate` and `RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY` from `src.utils.config`.

2. Add this module-level map next to `_CANDIDATE_FACING_NAV_LABELS`. Keys are the `NAV_CONFIG` paths; values are the artifact keys the criteria pages already pass to `ArtifactEditor`:

   ```python
   _CRITERIA_NAV_PATH_ARTIFACT = {
       "/artifacts/job_list_criteria": "joblist_rubric",
       "/artifacts/meteorite_criteria": "meteorite_jobdesc_rubric",
       "/artifacts/job_description_criteria": "jobdesc_rubric",
       "/artifacts/do_job_criteria": "do_rubric",
       "/artifacts/get_job_criteria": "get_rubric",
       "/artifacts/like_job_criteria": "like_rubric",
       "/artifacts/company_watch_criteria": "company_prefilter",
   }
   ```

   Do not add `/artifacts/company_search_terms`.

3. Add `_get_criteria_nav_counts(candidate_id: Optional[str]) -> dict` beside `_get_job_counts`. Empty `candidate_id` returns `{}`. Otherwise, for each path and artifact key, `owner = RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY[artifact_key]` and `counts[path] = len(rubric_criteria_for_task(candidate_id, owner))`. On any exception, `_log.debug("Failed to compute criteria nav counts", exc_info=True)` and return `{}` (same swallow as `_get_job_counts`). A successful return includes paths whose length is `0`.

4. In `_resolve_nav`, merge that dict into `nav_counts` with the company and job dicts: `{**company_counts, **job_counts, **criteria_counts}`. Leave the existing `if count is not None: nav_item["count"] = count` line as it is, so `0` is attached and a missing path is not.

## Sibling contract (Hedy consumes; this ticket does not draw)

`GET /api/candidates/<id>/rubric/<artifact_key>/grade_rollup` is the only feed for the vector header. `vectors[].run_count` is the header number. `vectors[].letters` is the bar: one segment per entry, already in A-B-C-D-F-X order, zeros omitted. `last_seen` is the stored timestamp string; this ticket does not format a calendar date. Reloading after a version move is a new GET of this route — the payload is always the versions that are current at request time. Nav badges stay on `GET /api/nav_config` `count`, rendered by the existing `[{item.count}]` span in `NavigationShell.tsx`. This ticket does not edit that component.

## Execution contract

The plan is binding. Execute steps in order within a stage, and stages in order. Do not add files. On ambiguity or drift, stop and comment on [AST-2257](https://linear.app/astralcareermatch/issue/AST-2257) with the Stage N blocked format from plan-child. One commit per stage on this epic worktree, published to `origin/sub/AST-2257/AST-2261-version-scoped-grade-rollup`.

## Estimate

Confirm Chuckles estimate: 5 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-2261
**Overall:** APPROVED
**Corpus:** b7ab2203048ce0beb2869a12200ab7fa696c8066
**Publish ref:** `sub/AST-2257/AST-2261-version-scoped-grade-rollup` @ `de0b2b919fab87342afbf0d6848a06d8dbd7d996`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.artifact.read-current | A | | |

## Traceability

`5 → Stage 3 (_CRITERIA_NAV_PATH_ARTIFACT` + `_get_criteria_nav_counts` merged into `_resolve_nav`, count `0` included); `6 → Stage 3 (map omits `/artifacts/company_search_terms`); parent AC `1–4` → N/A — thermometer / header UI sibling AST-2257 #2; child rollup + `grade_rollup` GET → Stages `1–2`

## Findings

### discuss — `list_vector_feedback` owner expansion

- **Severity:** discuss
- **Location:** Stage 1 step 5
- **Finding:** `database.list_vector_feedback(..., owner_task_key=owner)` expands via `task_keys_for_rubric_owner` (owner + craft). The plan correctly re-filters to the step-4 consumer set and drops craft / unpinned rows; behavior matches AC intent but the double filter is easy to mis-implement.
- **Recommendation:** Keep the explicit consumer-set filter in step 5 when building; no plan rewrite — worth a sharp comment in code at the call site during Stage 1.

### acceptable — Label-matching helper duplication

- **Severity:** acceptable
- **Location:** Stage 1 step 7
- **Finding:** Inline `_strip_code` duplicates `consult.py` to avoid `consult` ↔ `candidate` import cycle.
- **Recommendation:** As documented in the plan; no change.

## R6 checklist (summary)

- Definition fidelity: scope-limited to three files; explicit scope gate matches ticket **## Scope**; boundaries exclude thermometer sibling.
- DRY / scope: no sibling scope creep; `task_keys_for_rubric_owner` pit called out with a concrete alternative.
- Self-assessment: **Estimate** confirm `5 — agree` matches stage depth (detailed rollup + API + nav).

context_tokens≈24000

## Review

- **Publish ref:** `origin/sub/AST-2257/AST-2261-version-scoped-grade-rollup`
- **Tip:** `a7483a11d93c25c908ed69b8ffeee0dbdf4fc86e`
- **Stages landed:** 1 rollup · 2 grade_rollup GET · 3 criteria nav counts
