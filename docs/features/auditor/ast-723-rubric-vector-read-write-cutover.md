# AST-723 — Rubric_vector read/write cutover and RUBRIC_VECTORS token (Runtime Rubric Validation)

- **Linear:** [AST-723](https://linear.app/astralcareermatch/issue/AST-723/rubric-vector-read-write-cutover-and-rubric-vectors-token-runtime-rubric)
- **Parent (context only):** [AST-378](https://linear.app/astralcareermatch/issue/AST-378/runtime-rubric-validation)
- **Publish ref:** `origin/sub/AST-378/AST-723-rubric-vector-read-write-cutover`
- **Depends on:** [AST-722](https://linear.app/astralcareermatch/issue/AST-722/rubric-storage-schema-backfill-and-feedback-config-runtime-rubric) schema + backfill landed on `origin/ftr/AST-378-runtime-rubric-validation`

## Summary

Cut runtime rubric authority from `candidate_data.artifacts` JSON to **`rubric_vector`** rows (`current = 1`). Artifacts save and craft review flows **write** the table (retire prior row + insert new UUID when label+content fingerprint changes; importance-only or reorder-only edits update in place). Consult, roster, token resolution, and Artifacts UI **read** from `list_rubric_vectors(candidate_id, owner_task_key)` — no artifact JSON reads after cutover. Replace per-artifact prompt tokens (`{$JOBLIST_RUBRIC}`, `{$GET_RUBRIC}`, etc.) with a single **`{$RUBRIC_VECTORS}`** resolved from current rows for the active task's rubric owner. **Does not** parse vector feedback envelopes (**AST-724**), build Admin Vector Feedback UI (**AST-725**), change letter-grade scoring math, or remove `TASK_CONFIG["rubric_artifact"]` keys (**AST-723+** — keep for UI manifest / display wiring only).

## Out of scope (explicit)

| Item | Owner ticket |
|------|----------------|
| `vector_feedback` row creation at runtime | AST-724 |
| Admin Vector Feedback screen | AST-725 |
| Letter-grade scoring math changes | — |
| Removing `rubric_artifact` from `TASK_CONFIG` / `JOB_TOKEN_CONFIG` | AST-723+ |
| Legacy artifact JSON purge (`--purge-artifacts`) | AST-722 script; run after this ticket merges |
| Betty test files / test-bible | Betty at Code Complete |

## Owner task_key model

Rubric rows are keyed by **consumer** `task_key` (same mapping as `scripts/migrations/backfill_rubric_vectors.py` `_ARTIFACT_KEY_TO_TASK_KEY`). Craft UI pages still use legacy **artifact keys** for routing; core maps artifact → owner task at save/load boundaries.

| Artifact key (UI / legacy) | Owner `task_key` (`rubric_vector.task_key`) |
|----------------------------|-----------------------------------------------|
| `company_prefilter` | `prefilter_company` |
| `joblist_rubric` | `qualify_job_listings` |
| `jobdesc_rubric` | `evaluate_jd` |
| `do_rubric` | `grade_do` |
| `get_rubric` | `grade_get` |
| `like_rubric` | `grade_like` |

Craft generate task keys (`craft_prefilter_rubric`, …) resolve **`{$RUBRIC_VECTORS}`** via the same owner mapping when a craft task prompt references the token.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Owner-task maps; `RUBRIC_VECTORS` token; remove legacy rubric tokens from `TOKEN_SOURCES`; `resolve_tokens` rubric source | utils |
| `src/data/database.py` | `sync_rubric_vectors_from_criteria`, retire/update helpers; idempotent AST-723 `agent_task` token migration | data |
| `src/core/candidate.py` | `apply_rubric_vectors_save`, `hydrate_rubric_artifacts_for_response`, `rubric_criteria_for_task` | core |
| `src/core/consult.py` | Replace `_rubric_criteria_from_cd` reads with table-backed `rubric_criteria_for_task`; update `build_job_token_context` phase rubric load | core |
| `src/core/roster.py` | Replace `_rubric_criteria_from_cd(..., "company_prefilter")` with `rubric_criteria_for_task(candidate_id, "prefilter_company")` | core |
| `src/core/agent.py` | Pass `candidate_id` into token resolution for rubric source (mirror company_search_terms overlay pattern) | core |
| `src/ui/api/api_candidate.py` | Wire save + GET hydration | ui |

**Tests:** Betty owns **`tests/`** at Code Complete — engineer does **not** add test files in **build-child**.

## Stage 1: Config maps and RUBRIC_VECTORS token registry

**Done when:** `RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY`, `CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY`, and `rubric_owner_task_key(task_key)` exist in `config.py`; `TOKEN_SOURCES` registers `RUBRIC_VECTORS` with `"source": "rubric"`; legacy keys `COMPANY_PREFILTER`, `JOBLIST_RUBRIC`, `JOBDESC_RUBRIC`, `GET_RUBRIC`, `DO_RUBRIC`, `LIKE_RUBRIC` are **removed** from `TOKEN_SOURCES`; `resolve_tokens` handles `"source": "rubric"` by calling a new resolver (step 5 wires the import to avoid cycles).

1. In **`src/utils/config.py`**, after **`RUBRIC_CRITERIA_ARTIFACT_KEYS`** (~line 1070), add:

   ```python
   RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY: Dict[str, str] = {
       "company_prefilter": "prefilter_company",
       "joblist_rubric": "qualify_job_listings",
       "jobdesc_rubric": "evaluate_jd",
       "do_rubric": "grade_do",
       "get_rubric": "grade_get",
       "like_rubric": "grade_like",
   }
   CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY: Dict[str, str] = {
       "craft_prefilter_rubric": "company_prefilter",
       "craft_joblist_rubric": "joblist_rubric",
       "craft_jobdesc_rubric": "jobdesc_rubric",
       "craft_get_rubric": "get_rubric",
       "craft_do_rubric": "do_rubric",
       "craft_like_rubric": "like_rubric",
   }
   _RUBRIC_OWNER_TASK_BY_CONSUMER_TASK_KEY = frozenset(RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY.values())
   ```

2. Add **`rubric_owner_task_key(task_key: str) -> Optional[str]`** in the same file:

   - If `task_key in _RUBRIC_OWNER_TASK_BY_CONSUMER_TASK_KEY`: return `task_key`.
   - If `task_key in CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY`: return `RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY[CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY[task_key]]`.
   - Else: return `None`.

3. In **`TOKEN_SOURCES`**, **remove** entries: `COMPANY_PREFILTER`, `JOBLIST_RUBRIC`, `JOBDESC_RUBRIC`, `GET_RUBRIC`, `DO_RUBRIC`, `LIKE_RUBRIC`.

4. Add **`"RUBRIC_VECTORS": {"source": "rubric"}`** to **`TOKEN_SOURCES`**.

5. In **`resolve_tokens`**, inside `_replace`, after the `"pronoun"` branch and before `return match.group(0)`, add:

   ```python
   if spec["source"] == "rubric":
       from src.core.candidate import rubric_criteria_for_token
       owner = rubric_owner_task_key(task_key)
       if not owner:
           _log.warning("Token {$%s} unresolved — task %r has no rubric owner", name, task_key)
           return ""
       cid = (candidate_data or {}).get("_astral_candidate_id") or ""
       if not cid:
           _log.warning("Token {$%s} unresolved — missing candidate id (task=%s)", name, task_key)
           return ""
       return _value_to_str(rubric_criteria_for_token(cid, owner))
   ```

   ⚠️ **Decision:** Token resolution requires `candidate_data["_astral_candidate_id"]` injected by `do_task` / preview paths (Stage 5). Do not read artifact JSON as fallback.

6. Extend **`JOB_TOKEN_CONFIG["analysis_phases"]`** each phase dict with **`"rubric_owner_task_key"`** using the owner table above (e.g. `"ANALYSIS_JD": {..., "rubric_owner_task_key": "evaluate_jd"}`). Keep existing **`rubric_artifact`** keys for manifest/display — do not remove.

## Stage 2: Data-layer sync with retire/insert semantics

**Done when:** `sync_rubric_vectors_from_criteria(candidate_id, owner_task_key, criteria_list)` performs full upsert with AST-378 versioning rules; manual REPL can save criteria, re-save with unchanged fingerprint (importance-only change updates same row), re-save with changed content (old row `current=0`, new UUID inserted); removed codes get retired.

1. In **`src/data/database.py`**, in the rubric_vector section after **`count_rubric_vectors_for_candidate_task`**, add **`_retire_rubric_vector_row_on_connection(conn, rubric_vector_uuid: str) -> None`**:

   ```sql
   UPDATE rubric_vector SET current = 0, updated_at = ? WHERE rubric_vector_uuid = ?
   ```

2. Add **`_update_rubric_vector_importance_on_connection(conn, rubric_vector_uuid, importance: int) -> None`**:

   ```sql
   UPDATE rubric_vector SET importance = ?, updated_at = ? WHERE rubric_vector_uuid = ?
   ```

3. Add **`sync_rubric_vectors_from_criteria(candidate_id: str, owner_task_key: str, criteria_list: List[dict]) -> None`**:

   - Resolve **`task_key_uuid = _resolve_current_agent_task_uuid(conn, owner_task_key)`**; if missing, raise **`ValueError(f"No current agent_task for {owner_task_key!r}")`**.
   - Load current rows: **`list_rubric_vectors(candidate_id, owner_task_key, current_only=True)`** (use connection-scoped query inside `_with_conn`, not nested public calls).
   - Build **`current_by_code: Dict[str, dict]`** from current rows (codes uppercased for match).
   - Build **`incoming_by_code`** from **`criteria_list`** (each item must have non-empty **`content`** after strip; coerce **`code`** default `V{n:02d}`; compute **`fingerprint = rubric_text.rubric_vector_content_fingerprint(label, content)`**).
   - For each **incoming code**:
     - If code exists in **`current_by_code`**:
       - Same **`content_fingerprint`**: call **`_update_rubric_vector_importance_on_connection`** only (label/content cosmetic drift already normalized by fingerprint).
       - Different fingerprint: **`_retire_rubric_vector_row_on_connection`** on old UUID; **`_insert_rubric_vector_row_on_connection`** with new UUID, `current=1`.
     - If code new: **`_insert_rubric_vector_row_on_connection`**.
   - For each **current code** not in incoming: **`_retire_rubric_vector_row_on_connection`**.
   - Single transaction; **`conn.commit()`** once at end.

4. Export **`sync_rubric_vectors_from_criteria`** as public API (no `conn` param — mirror **`sync_company_search_terms`** wrapper pattern).

## Stage 3: Core save/load helpers and API write path

**Done when:** PUT `/api/candidates/:id/data` with rubric artifact keys syncs **`rubric_vector`** and **does not** persist rubric lists into `candidate_data.artifacts`; GET `/api/candidates/:id` overlays rubric artifact keys from table for Artifacts UI; `normalize_rubric_artifacts_on_save` still validates before sync.

1. In **`src/core/candidate.py`**, add **`def _rubric_rows_to_criteria(rows: list) -> list`**:

   - Map each DB row to `{code, label, content, importance}` dict.
   - Call **`rubric_text.ensure_criterion_grade_table(item)`** on each (sets **`grade_descriptions`**) — same shape consult expects today.

2. Add **`def rubric_criteria_for_task(candidate_id: str, owner_task_key: str) -> list`**:

   - **`rows = database.list_rubric_vectors(candidate_id, owner_task_key, current_only=True)`**
   - **`criteria = _rubric_rows_to_criteria(rows)`**
   - If **`owner_task_key == "prefilter_company"`**: merge **`EMBEDDED_COMPANY_PREFILTER_CRITERIA`** + tail criteria whose codes are not in embedded set (mirror existing **`_rubric_criteria_from_cd`** logic in **`consult.py`** lines 116–129 — move merge here, do not duplicate in consult).
   - Return list.

3. Add **`def rubric_criteria_for_token(candidate_id: str, owner_task_key: str) -> list`** — alias returning same list (token path uses markdown via **`value_to_str`**).

4. Add **`def apply_rubric_vectors_save(candidate_id: str, artifacts: dict) -> None`** (mirror **`apply_company_search_terms_save`**):

   - For each **`key, val in list(artifacts.items())`** where **`key in RUBRIC_CRITERIA_ARTIFACT_KEYS`**:
     - Skip if **`val is None`**.
     - **`owner = RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY[key]`** — raise **`ValueError`** if key missing from map.
     - Require **`val`** is **`list`** (already validated by **`normalize_rubric_artifacts_on_save`**).
     - **`database.sync_rubric_vectors_from_criteria(candidate_id, owner, val)`**
     - **`del artifacts[key]`**

5. Add **`def hydrate_rubric_artifacts_for_response(candidate_id: str, cd: dict) -> None`**:

   - Mutates **`cd["artifacts"]`** in place.
   - For each **`artifact_key, owner`** in **`RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY.items()`**:
     - Set **`cd["artifacts"][artifact_key] = rubric_criteria_for_task(candidate_id, owner)`** (empty list when no rows).

6. In **`src/ui/api/api_candidate.py`**, in **`update_candidate_data`** (~line 160), **before** **`save_candidate_data`**:

   - After **`normalize_rubric_artifacts_on_save(arts)`**, call **`apply_rubric_vectors_save(candidate_id, arts)`** (same block as **`apply_company_search_terms_save`**).

7. In **`get_candidate_detail`** (~line 121), after loading candidate:

   ```python
   cd = candidate.get("candidate_data") or {}
   hydrate_rubric_artifacts_for_response(candidate_id, cd)
   candidate["candidate_data"] = cd
   ```

   Response overlay only — does not write artifact JSON back to DB.

## Stage 4: Consult and roster read cutover

**Done when:** No production code path calls **`_rubric_criteria_from_cd`** for runtime rubric load; consult grading, grade-reason hydration, job-list columns, and prefilter encoded batches use **`rubric_criteria_for_task`**.

1. In **`src/core/consult.py`**, replace **`_rubric_criteria_from_cd(cd, rubric_key)`** with **`rubric_criteria_for_task(candidate_id, owner_task_key)`** at every call site. Derive **`candidate_id`** from **`ctx["astral_candidate_id"]`**, **`(ctx or {}).get("astral_candidate_id")`**, or job raft context as already available at each site.

2. Mapping at each site (use **`TASK_CONFIG[task_key]["rubric_artifact"]`** only to look up owner — do not read artifacts):

   ```python
   from src.utils.config import RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY
   rk = task_config.get("rubric_artifact")  # or phase_cfg / cfg
   owner = RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY.get(rk) if rk else None
   rubric = rubric_criteria_for_task(candidate_id, owner) if owner and candidate_id else []
   ```

3. In **`_format_analysis_phase_text`** (~line 631), replace **`_rubric_criteria_from_cd(candidate_data, phase_cfg.get("rubric_artifact"))`** with:

   ```python
   owner = phase_cfg.get("rubric_owner_task_key")
   cid = (candidate_data or {}).get("_astral_candidate_id") or ""
   rubric_criteria = rubric_criteria_for_task(cid, owner) if owner and cid else []
   ```

   Stage 5 ensures **`candidate_data["_astral_candidate_id"]`** is set before job token build.

4. Delete **`_rubric_criteria_from_cd`** from **`consult.py`** once all references are migrated (grep must be clean in **`src/`**).

5. In **`src/core/roster.py`**, replace all **`_rubric_criteria_from_cd(..., "company_prefilter")`** imports/calls with **`rubric_criteria_for_task(candidate_id, "prefilter_company")`**. Pass **`candidate_id`** from existing ctx/cd (`ctx.get("astral_candidate_id")` or company batch candidate id).

6. Keep **`entry["rubric_artifact"] = task_cfg.get("rubric_artifact")`** in roster enrichment for frontend display keys — GET hydration supplies table-backed content under that artifact key.

## Stage 5: Agent token overlay, prompt migration, and candidate_id injection

**Done when:** Rubric-backed **`agent_task`** prompts use **`{$RUBRIC_VECTORS}`** only (migration idempotent); **`do_task`** / **`preview_prompt`** inject **`_astral_candidate_id`** into **`cd`** for rubric and analysis token paths; rubric-backed runs resolve **`{$RUBRIC_VECTORS}`** from table.

1. In **`src/data/database.py`**, add idempotent migration **`_apply_ast723_rubric_vectors_token_migration(conn) -> None`** wired from **`_ensure_agent_task_schema`** (same pattern as AST-678):

   - Module constant **`_AST723_RUBRIC_TOKEN_REPLACEMENTS: Tuple[Tuple[str, str], ...]`**:
     ```
     ("{$COMPANY_PREFILTER}", "{$RUBRIC_VECTORS}"),
     ("{$JOBLIST_RUBRIC}", "{$RUBRIC_VECTORS}"),
     ("{$JOBDESC_RUBRIC}", "{$RUBRIC_VECTORS}"),
     ("{$GET_RUBRIC}", "{$RUBRIC_VECTORS}"),
     ("{$DO_RUBRIC}", "{$RUBRIC_VECTORS}"),
     ("{$LIKE_RUBRIC}", "{$RUBRIC_VECTORS}"),
     ```
   - Guard flag **`_ast723_rubric_token_migration_applied`** (module-level bool, set True after success).
   - For each **`current = 1`** **`agent_task`** row, for each prompt column in **`("user_prompt", "cache_prompt", "cache_prompt_b", "cache_prompt_c", "cache_prompt_d", "nocache_prompt", "system_prompt")`**: apply replacements; if any column changed, retire row + insert new current row (full **`agent_task`** versioning — mirror AST-678 retire+insert, do not UPDATE in place).
   - Marker comment **`AST-723_RUBRIC_VECTORS_TOKEN`** in patched **`user_prompt`** when any replacement occurred (idempotency check — skip rows already containing marker).

2. In **`src/core/agent.py`**, in **`do_task`** after building **`cd`** (~line 1310), when **`candidate_id`** is truthy:

   ```python
   cd = dict(cd)
   cd["_astral_candidate_id"] = candidate_id
   ```

   (Keep existing **`company_search_terms`** overlay block immediately after.)

3. In **`src/core/candidate.py`** **`preview_task_prompt`**, before calling **`preview_prompt`**, set **`cd["_astral_candidate_id"] = candidate_id`** when **`candidate_id`** is provided.

4. In **`build_job_token_context`** (**`consult.py`**), ensure **`candidate_data["_astral_candidate_id"]`** is set by callers, or accept optional **`candidate_id`** param — prefer mutating a **`cd = dict(candidate_data); cd["_astral_candidate_id"] = ...`** copy at start of **`build_job_token_context`** when job dict includes candidate id. **`_job_context_for_call`** already has **`cd`** from ctx — inject id from **`ctx.get("astral_candidate_id")`** before calling builder.

5. Verify no remaining references to legacy rubric **`TOKEN_SOURCES`** keys in **`src/`** (admin token picker will show **`RUBRIC_VECTORS`** only).

## Stage 6: Verification and hardening

**Done when:** Grep confirms no runtime reads of rubric keys from **`candidate_data.artifacts`** in **`src/core/`** or **`src/utils/config.py` `resolve_tokens`** artifact paths; manual smoke: Artifacts save → `list_rubric_vectors` reflects change; consult batch resolves rubric from table; **`{$RUBRIC_VECTORS}`** appears in resolved admin preview for a rubric-backed task.

1. Grep **`src/`** for **`artifacts.*rubric`**, **`_rubric_criteria_from_cd`**, and legacy token names in Python — must be zero hits outside comments/tests.

2. Confirm **`normalize_rubric_artifacts_on_save`** still runs **before** **`apply_rubric_vectors_save`** (grade table validation unchanged).

3. Confirm empty rubric (zero current rows) behavior matches today: consult paths that require rubric raise **`ValueError("rubric criteria missing or empty...")`** where they did before; token resolves to empty string with warning log.

4. Document in code comment at **`apply_rubric_vectors_save`**: legacy artifact purge is **`scripts/migrations/backfill_rubric_vectors.py --purge-artifacts --confirm-purge`** after AC#9 verify — not automatic in this ticket.

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — Touches config token registry, data-layer sync/versioning, core consult/roster/candidate read-write paths, agent prompt migration, and candidate API save/GET overlay across utils, data, core, and ui layers.

**Conf:** `Medium` — AST-722 established table shape and backfill mapping; company_search_terms cutover is the direct pattern for save/sync and GET overlay; open coordination is ensuring `agent_task` token migration runs before legacy tokens are removed from `TOKEN_SOURCES`.

**Risk:** `HIGH` — Incorrect sync versioning or a missed artifact read path would desync consult grading from Susan's rubrics; mitigation is fingerprint-gated retire/insert, explicit grep gate in Stage 6, and AST-722 backfill + AC#9 verify before artifact purge.

## ASTRAL_CODE_RULES self-review

| Rule | Plan compliance |
|------|-----------------|
| §1.1 inventory | Uses existing **`rubric_vector`** table from AST-722; no new tables. |
| §1.3 DRY | Single **`rubric_criteria_for_task`** + **`sync_rubric_vectors_from_criteria`**; delete **`_rubric_criteria_from_cd`**. |
| §2.1 config | Owner maps and token registry in **`config.py`**; no inline artifact-key sets in core. |
| §2.4 batch | N/A — candidate-scoped sync, not batch claim. |
| §2.6 state machine | No job/company state transitions. |
| §3.3 imports | Lazy imports in **`resolve_tokens`** / **`do_task`** to avoid agent↔candidate cycles (same as company_search_terms). |
| §3.5 naming | **`snake_case`** helpers; owner **`task_key`** matches existing **`TASK_CONFIG`** keys. |

No conflicts requiring plan revision.

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-378/AST-723-rubric-vector-read-write-cutover` (tip `9ed0c99`)  
**Reviewed:** 2026-06-18  
**Note:** Three-dot diff includes sibling **AST-722** commits not yet on `origin/dev`; AST-723 cutover review below is scoped to Stages 1–6 of this plan.

### What's solid

| Area | Notes |
|------|-------|
| Plan fidelity | Owner maps + `{$RUBRIC_VECTORS}` registry; `sync_rubric_vectors_from_criteria` fingerprint retire/insert; API save strips rubric keys + GET hydrates; consult/roster read cutover; AST-723 `agent_task` token migration wired in `_ensure_agent_task_schema`. |
| Cutover grep | `_rubric_criteria_from_cd` removed from `src/`; legacy per-rubric `TOKEN_SOURCES` keys gone; no `{$COMPANY_PREFILTER}` / `{$GET_RUBRIC}` etc. in `src/`. |
| §2.1 config | `RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY`, `rubric_owner_task_key`, `JOB_TOKEN_CONFIG` phase `rubric_owner_task_key` fields — no inline artifact-key sets in core. |
| §3.3 layers | Lazy `core.candidate` import in `resolve_tokens` mirrors existing resume-token pattern; UI API uses core helpers like `apply_company_search_terms_save`. |
| Sync semantics | Single-transaction upsert; retire on fingerprint change; importance-only update in place; removed codes retired. |
| Agent overlay | `do_task`, `_job_context_for_call`, and `build_job_token_context` inject `_astral_candidate_id` for rubric + analysis tokens. |
| Tests / bible | Betty manifest covers save/hydrate, embedded prefilter merge, consult table reads, API overlay, token config. |

### Issues

| Sev | Location | Finding |
|-----|----------|---------|
| **fix-now** | `src/core/candidate.py` `preview_task_prompt` ~L297 | `build_job_token_context(..., candidate_id=cid or "")` runs **before** `cid = candidate.get("astral_candidate_id") or candidate_id` (~L298). Any preview with `astral_job_id` raises `UnboundLocalError`. Move `cid` assignment above the job block. |
| discuss | `src/core/candidate.py` `_rubric_rows_to_criteria` | `except ValueError: pass` around `ensure_criterion_grade_table` on DB load — silent swallow. Add comment if legacy-backfill tolerance is intentional. |
| discuss | `src/data/database.py` `sync_rubric_vectors_from_criteria` | `importance = int(item.get("importance") or 5)` uses magic `5` vs config default; safe post-normalize, but §1.4 literal if path called without normalize. |
| advisory | Diff baseline | `origin/dev...` includes full **AST-722** stack until ftr lands on dev. |
| advisory | `_fetch_prefilter_notes` | Table-backed read fixes prior wrong-level artifact access — good incidental fix. |

### Recommended actions

| Priority | Action |
|----------|--------|
| **resolve** | Fix `preview_task_prompt` `cid` ordering; add preview-with-`astral_job_id` test if manifest gap. |
| ops | Ensure AST-722 backfill ran before cutover UAT; defer artifact purge until read-switch verified. |
| AST-724 | `_ensure_vector_feedback_table` on first feedback write (carried from AST-722 discuss). |

**Verdict:** One fix-now — resolve then UAT. Cutover architecture is sound.

## Resolution

**Resolved:** 2026-06-18 (Hedy, `resolve-child`)

| Item | Action |
|------|--------|
| fix-now — `preview_task_prompt` `cid` before job block | Moved `cid = candidate.get("astral_candidate_id") or candidate_id` above `build_job_token_context(..., candidate_id=cid)` so job-scoped previews no longer raise `UnboundLocalError`. |
| discuss — `_rubric_rows_to_criteria` silent parse | Comment documents intentional tolerance for legacy/backfill rows without trailing grade tables. |
| discuss — sync `importance` default `5` | No change — path always runs after `normalize_rubric_artifacts_on_save` on API save; backfill script normalizes separately. |

**Publish tip after resolve:** `origin/sub/AST-378/AST-723-rubric-vector-read-write-cutover` (see git log).
