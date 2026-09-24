# AST-1781 — Revalidate on agent_task + artifact version

- **Linear:** https://linear.app/astralcareermatch/issue/AST-1781
- **Parent:** AST-1766 — Dispatch Validation
- **Publish ref:** `sub/AST-1766/AST-1781-revalidate-on-agent-task-artifact-version`

After a new current `agent_task` version lands, revalidate every `dispatch_task` with that `task_key` and force `auto_mode` off when candidate-scoped empty-render is true. After a candidate artifact current rotation (write-operative), revalidate related `dispatch_task` rows whose prompts reference tokens backed by that artifact and force AUTO off the same way. Uses sibling #1’s `empty_render_for_prompts` (AST-1779, already on `ftr`); shares the same force-off persistence semantics sibling #2 will use in list enrichment — do not reimplement the predicate. Does not own list UI, AUTO/Run API gates, or React.

## Explicit scope gate

Ticket **## Scope** covers only:

- `src/data/database.py` — after new current `agent_task` version, revalidate that `task_key` across `dispatch_task` rows (force AUTO off when empty-render)
- `src/core/candidate.py` — after candidate artifact current rotation, revalidate related `dispatch_task` rows (force AUTO off when empty-render)

No other files. Do not edit `src/utils/config.py`, `src/ui/api/api_admin.py`, or `AdminScheduledActions.tsx`. Do not import `src.core` from `src.data` (layer direction: data → utils only).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Add revalidation helpers (prompt texts, operative-aware token view, force AUTO off); hook `save_agent_task` after a new current version commits; add `list_dispatch_tasks_for_task_key` | data |
| `src/core/candidate.py` | After real write-operative rotate in `save_candidate_data` str-path, call artifact revalidation; per-item WARNING when a row cannot be evaluated | core |

## Stage 1: Shared revalidation + force AUTO off (database)

**Done when:** From a Python REPL against a DB that has (1) a current `agent_task` for `task_key=T` whose prompts reference `{$FIRST_NAME}`, (2) a `dispatch_task` row for candidate `C` with `task_key=T` and `auto_mode=1`, and (3) candidate `C` with empty `first`, calling `revalidate_dispatch_tasks_for_task_key("T")` persists `auto_mode=0` on that row. Calling it again is a no-op write (already off). A row with non-empty `first` keeps `auto_mode=1`.

1. In `src/data/database.py`, add imports from `src.utils.config` (extend the existing import block): `TOKEN_SOURCES`, `ARTIFACT_CONFIG`, `empty_render_for_prompts`, `list_artifact_keys_in_prompt_texts`.

2. Add `list_dispatch_tasks_for_task_key(task_key: str) -> List[Dict[str, Any]]` next to `list_dispatch_tasks_for_candidate`: `SELECT * FROM dispatch_task WHERE task_key = ? ORDER BY id ASC` (schema ensure + `_row_to_dict`). Empty/blank `task_key` → `[]`.

3. Add private helper `_agent_task_prompt_texts(agent_task: dict, agent_row: Optional[dict]) -> list[str]` that returns strings in this exact order (skip only if the value is not a `str`; include empty strings so order stays stable — `empty_render_for_prompts` already ignores empty strings):

   - `agent_task["system_prompt"]`
   - `agent_task["cache_prompt"]`, `cache_prompt_b`, `cache_prompt_c`, `cache_prompt_d`
   - `agent_task["nocache_prompt"]`
   - `agent_task["user_prompt"]`
   - Effective agent system text for gating: `(agent_task.get("system_prompt") or "").strip()` then if that is empty, `(agent_row or {}).get("content") or ""` (same base as `resolved_task_system` before token resolve — do **not** import `src.core.agent`). Always append this effective system string as the **last** entry even when it duplicates a non-empty `agent_task["system_prompt"]` already listed first (duplicate names are fine; first-seen wins inside the helper). When `agent_task["system_prompt"]` is non-empty after strip, the last entry is that same stripped text (agent `content` unused). When it is empty, the last entry is agent `content` (or `""`).

   ⚠️ **Decision:** Effective system is raw text before `resolve_tokens` — `empty_render_for_prompts` scores tokens itself. Duplicating the task `system_prompt` in the list when non-empty is harmless and keeps the “agent system always last” contract from AST-1779 caller notes.

4. Add private helper `_token_view_for_empty_render(candidate_row: dict) -> dict` that builds the same walkable shape as `build_candidate_token_view` **without importing core**:

   ```python
   cd = candidate_row.get("candidate_data") or {}
   if not isinstance(cd, dict):
       cd = {}
   view = {
       "first": candidate_row.get("first") or "",
       "last": candidate_row.get("last") or "",
       "full": candidate_row.get("full") or "",
       "pronouns": candidate_row.get("pronouns") or "",
       "contact": cd.get("contact") if isinstance(cd.get("contact"), dict) else {},
       "context": dict(cd.get("context") or {}) if isinstance(cd.get("context"), dict) else {},
       "artifacts": dict(cd.get("artifacts") or {}) if isinstance(cd.get("artifacts"), dict) else {},
       "_astral_candidate_id": candidate_row.get("astral_candidate_id") or "",
   }
   ```

   Then overlay **current operative** bodies for every `TOKEN_SOURCES` entry where `source == "candidate"` and `source_type == "artifact"`:

   - Resolve `artifact_key = spec["artifact_key"]`, look up `ARTIFACT_CONFIG[artifact_key]`, `artifact_type = artifact_key.rsplit(".", 1)[-1]`, `cid = view["_astral_candidate_id"]`.
   - `row = get_current_artifact(entry["entity_type"], cid, artifact_type)` (same module).
   - On miss (`row is None`): leave the library path untouched (same migration window as core hydrate).
   - On hit: write `row["artifact_data"]` onto `view` at `spec["path"]` (dot path: split on `.`, ensure parent dicts exist, set leaf). For `path == "artifacts.base_resume"` / `context.strengths` / etc. this mirrors `hydrate_operative_*_for_response`.

   ⚠️ **Decision:** Overlay in data via `get_current_artifact` instead of calling `candidate.get_candidate` / `build_candidate_token_view` — keeps `data → utils` import direction. `{$BASE_RESUME}` still works because `format_base_resume_for_token` (late-imported inside `resolve_tokens`) reads operative current via `_astral_candidate_id`.

5. Add private helper `_force_auto_off_if_empty_render(dtask: dict) -> None`:

   - If not `bool(dtask.get("auto_mode"))`: return (already off).
   - `task_key = dtask.get("task_key") or ""`; `candidate_id = (dtask.get("candidate_id") or "").strip()`.
   - If either blank: `_log.warning` once with candidate_id / task_key / id + reason `missing candidate_id or task_key — skipping empty-render revalidation`; return. (Every real row has `candidate_id` per `astral.dispatch.entity-state-bound`; blank is a soft skip, not a carve-out.)
   - `agent_task = get_agent_task(task_key)`; if None: warning `no current agent_task` + skip.
   - `agent_row = get_agent(agent_task.get("agent_id") or "")` if agent_id else `None` (missing agent is OK — effective system becomes `""`).
   - `candidate_row = get_candidate(candidate_id)`; if None: warning `candidate not found` + skip.
   - `texts = _agent_task_prompt_texts(agent_task, agent_row)`.
   - `view = _token_view_for_empty_render(candidate_row)`.
   - `result = empty_render_for_prompts(texts, view, task_key)` — **do not** pass `entity_contexts` (epic default: job emptiness must not flip the flag).
   - If `result["empty_render"]` is true: `update_dispatch_task(int(dtask["id"]), auto_mode=0)`.
   - Wrap the body above (after the auto_mode early return) in `try/except Exception`: on exception `_log.warning` with task id, candidate_id, task_key, `type(exc).__name__`, `exc`, reason `empty-render revalidation failed — leaving auto_mode unchanged`; do **not** re-raise; do **not** `logger.exception` here (data layer does not own crash logging for soft per-item misses — `stat.logging.error` stays for thrown handler paths elsewhere).

6. Add public `revalidate_dispatch_tasks_for_task_key(task_key: str) -> None`:

   - Blank key → return.
   - For each row in `list_dispatch_tasks_for_task_key(task_key)`, call `_force_auto_off_if_empty_render(row)`.

7. Add public `revalidate_dispatch_tasks_for_artifact(candidate_id: str, artifact_key: str) -> None`:

   - Strip both; blank → return.
   - If `artifact_key` is not a value of any `TOKEN_SOURCES[*]["artifact_key"]` with `source == "candidate"` and `source_type == "artifact"`: return (no prompt token backs this catalog key — e.g. `candidate.artifacts.resume_structure`).
   - Load all current agent_task **full** rows once: private `_list_current_agent_tasks_full() -> List[Dict]` = `SELECT * FROM agent_task WHERE current = 1` (do not reuse `list_candidate_tasks`, which only has lengths).
   - For each agent_task row: load agent via `get_agent` when `agent_id` set; `texts = _agent_task_prompt_texts(...)`; if `artifact_key in list_artifact_keys_in_prompt_texts(*texts)`: collect that `task_key` into an ordered-unique list.
   - For each collected `task_key`, for each row in `list_dispatch_tasks_for_task_key(task_key)` where `(row.get("candidate_id") or "").strip() == candidate_id`, call `_force_auto_off_if_empty_render(row)`.

   ⚠️ **Decision:** Related rows are only this candidate’s `dispatch_task` rows for task_keys whose **current** prompts reference the artifact — matches parent “re-check every related `dispatch_task` whose prompts reference tokens backed by that artifact” scoped to the candidate that just rotated.

8. Module header inventory (top-of-file comment block that lists dispatch_task / agent_task helpers): add one-line mentions of `revalidate_dispatch_tasks_for_task_key`, `revalidate_dispatch_tasks_for_artifact`, `list_dispatch_tasks_for_task_key`.

## Stage 2: Hook new current agent_task version

**Done when:** Calling `save_agent_task(T, user_prompt=...)` with a prompt change that versions the row runs revalidation for `T`. A metadata-only `save_agent_task(T, run_next=...)` (no seven-segment content change) does **not** call revalidation. First insert for a brand-new `task_key` **does** call revalidation.

1. Change `_save_agent_task_on_connection` to return `bool`: `True` when it **inserted** a new `current=1` row (first insert branch **or** `content_changed` retire+insert branch); `False` on metadata-only update of the existing current row.

2. Update every in-module caller of `_save_agent_task_on_connection` to accept the return value (assign to `_` where revalidation is not wanted).

3. In public `save_agent_task`, after successful `conn.commit()` inside `_with_conn` (or immediately after `_run_with_retry(_with_conn)` returns): if the save versioned (`True`), call `revalidate_dispatch_tasks_for_task_key(task_key)`. Capture the bool from `_save_agent_task_on_connection` inside `_with_conn` and return it from `_with_conn` / `_run_with_retry` so the outer function can call revalidation **after** the connection is closed and committed (revalidation opens its own connections via existing helpers).

   ⚠️ **Decision:** Hook **only** public `save_agent_task` (Manage Tasks / operator save). Copy-Output upsert and repo-JSON startup also version rows via `_save_agent_task_on_connection` but are out of this ticket’s AC wording (“Saving a new current…”) — do not add revalidation there unless a later ticket asks. Document for sibling awareness.

4. Do **not** fail `save_agent_task` if revalidation soft-skips; revalidation never raises to the save caller (per-row catch in step 5 of Stage 1). If `revalidate_dispatch_tasks_for_task_key` itself raises unexpectedly, catch at the `save_agent_task` call site with `_log.warning` + task_key and leave the new agent_task version committed.

## Stage 3: Hook candidate artifact current rotation

**Done when:** `save_candidate_data(cid, "candidate.context.strengths", "x")` that performs retire+insert (not identical no-op) calls `revalidate_dispatch_tasks_for_artifact(cid, "candidate.context.strengths")`. An identical re-save that returns the existing uuid without `save_artifact` does **not** call revalidation. After rotate, a `dispatch_task` for that candidate whose task prompts reference `{$STRENGTHS}` and whose strengths body is blank (or would empty-render) ends with `auto_mode=0` if it was on.

1. In `src/core/candidate.py`, in `save_candidate_data` str-path, **after** `new_uuid = database.save_artifact(...)` succeeds and **before** the existing per-key `logger.info` blocks / `return new_uuid`:

   - Call `database.revalidate_dispatch_tasks_for_artifact(candidate_id, artifact_key)`.
   - Wrap that call in `try/except Exception`: on failure `logger.warning` with `candidate_id`, `artifact_key`, `type(exc).__name__`, `exc`, and product consequence `AUTO revalidation skipped after artifact save`; do not re-raise (artifact pin must still return). Use existing `logger` / `get_logger(__name__)` already in this module — this is the `stat.logging.warning` site for the artifact hook.

2. Do **not** call revalidation on the identical-to-current early return (pattern `patt.artifact.write-operative` — no new version).

3. Do **not** call revalidation on the dict (library merge) path of `save_candidate_data`.

## Execution contract

- Stages in order; one commit per stage on the epic worktree; publish to `origin/sub/AST-1766/AST-1781-revalidate-on-agent-task-artifact-version` after each stage.
- Do not add files outside the Files Changed table.
- Sibling #2 (AST-1780) may later call `_force_auto_off_if_empty_render` / `revalidate_dispatch_tasks_for_task_key` from list enrichment — leave those names stable; do not move them into `api_admin.py` in this ticket.
- Depends on AST-1779 helper already present on the integration line (`empty_render_for_prompts`). Before Stage 1 coding, run `sync-child.sh` with `--ftr AST-1766-dispatch-validation` so the helper is on HEAD.

## Estimate

Confirm Chuckles estimate: 5 — agree




## Review (build stub)

**Publish ref:** `origin/sub/AST-1766/AST-1781-revalidate-on-agent-task-artifact-version`
**Tip:** `2f73c1ad`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `5d24f9af` | empty-render revalidate helpers + force AUTO off |
| 2 | `beb48171` | revalidate dispatch AUTO after agent_task version |
| 3 | `2f73c1ad` | revalidate dispatch AUTO after artifact rotate |

## Joan validate

**Ticket:** AST-1781
**Overall:** APPROVED
**Corpus:** 2ac86c3f693409c364f8630a97198c8dbfa9c6f3
**Publish ref:** `0caf0c6b3b31ab7b720689372354f29346f136f9`

## Canon scores

| slug | grade | effort | note |
|------|-------|--------|------|
| astral.dispatch.entity-state-bound | A | | |
| patt.artifact.write-operative | A | | |
| stat.logging.warning | A | | |
| stat.logging.error | X | | Plan adds no new `logger.exception` sites; soft per-row misses use warning + leave state unchanged (stat.logging.warning Resolution #1). |

## Traceability

AC5→Stage 1 `_force_auto_off_if_empty_render` (persist `auto_mode=0` when `empty_render` true); AC6→Stage 2 `save_agent_task` post-commit `revalidate_dispatch_tasks_for_task_key`; AC7→Stage 3 `save_candidate_data` str-path post-`save_artifact` + Stage 1 `revalidate_dispatch_tasks_for_artifact`. Parent AC 5–7 → Stages 1–3; parent AC 1–4, 8–10 out of child Scope (siblings #1–#2, #4).

## Findings

### discuss — Copy Output / migration version paths skip revalidation

- **Severity:** discuss
- **Location:** Stage 2 step 3 Decision
- **Finding:** Child AC 6 text covers any new current `agent_task` version for a `task_key`. Plan hooks only public `save_agent_task`; `apply_agent_task_copy_upsert` and startup migrations also call `_save_agent_task_on_connection` and can version prompts without triggering revalidation.
- **Recommendation:** Acceptable if product treats Manage Tasks save as the operative path and sibling #2 list enrichment covers residual AUTO-on rows (parent AC 5). If Copy Output must satisfy AC 6 literally, extend the hook to that caller or narrow AC wording at Discussion.

### discuss — Token view builder parallel to core

- **Severity:** discuss
- **Location:** Stage 1 step 4 `_token_view_for_empty_render`
- **Finding:** Data-layer view + operative overlay duplicates `build_candidate_token_view` + `hydrate_operative_*` behavior (layer-law tradeoff). Sibling #2 list eval uses plain `build_candidate_token_view` without operative overlay.
- **Recommendation:** Intentional for `data → utils` import direction and AC 7 artifact rotation. Flag for epic awareness so list enrichment and revalidation do not diverge on operative artifact tokens; no AST-1781 plan change required if #2 later hydrates or shares this helper.

### discuss — Canon Scope gap (do not score)

- **Severity:** discuss
- **Location:** Ticket Citations vs plan footprint
- **Finding:** `astral.layers.import-direction` and `astral.standards.in-scope-only` plainly govern this slice but are absent from the frozen four-id list. Plan explicitly honors both via scope gate and “no `src.core` from `src.data`”.
- **Recommendation:** Archie may amend Canon Scope for Radia comparability; no plan defect.

context_tokens≈32000


## Radia review

**Ticket:** AST-1781
**Publish ref:** cbacd9210e3b96116fcca44a8774d0625608db8f
**Corpus:** 2ac86c3f693409c364f8630a97198c8dbfa9c6f3
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| astral.dispatch.entity-state-bound | A | | |
| patt.artifact.write-operative | A | | |
| stat.logging.warning | A | | |
| stat.logging.error | X | | |

## Column diff vs plan stage

(aligned) — Joan graded all four ids **A** / **X** at validate-plan; code review agrees on every row.

## Frame diff

(none)

## Findings

### discuss — Copy Output / migration version paths skip revalidation

- **Severity:** discuss
- **Location:** `src/data/database.py` — `save_agent_task` post-commit hook only; `apply_agent_task_copy_upsert` / `_apply_ast723_*` / `_apply_ast561_*` call `_save_agent_task_on_connection` with `_ =` and no revalidation
- **Finding:** Child AC6 wording covers any new current `agent_task` version for a `task_key`. Implementation hooks only public `save_agent_task` (Manage Tasks path), matching plan Stage 2 Decision. Copy Output and startup migrations can version prompts without triggering `revalidate_dispatch_tasks_for_task_key`.
- **Recommendation:** Acceptable if Manage Tasks is the operative path and sibling #2 list enrichment covers residual AUTO-on rows (parent AC 5). If Copy Output must satisfy AC6 literally, extend the hook or narrow AC at Discussion — same Joan plan finding, still true on tip.

### discuss — Token view builder parallel to core (layer-law tradeoff)

- **Severity:** discuss
- **Location:** `src/data/database.py::_token_view_for_empty_render`
- **Finding:** Data-layer view + operative overlay via `get_current_artifact` duplicates `build_candidate_token_view` / hydrate behavior intentionally to keep `data → utils` import direction. Sibling #2 list enrichment may use plain `build_candidate_token_view` without operative overlay.
- **Recommendation:** Epic awareness only — ensure list gates and revalidation hooks do not diverge on operative artifact tokens when #2 lands; no AST-1781 code change required if #2 later shares or hydrates this path.

### discuss — Canon Scope gaps (do not score; Joan raised at plan)

- **Severity:** discuss
- **Location:** Ticket Citations vs plan footprint
- **Finding:** `astral.layers.import-direction` and `astral.standards.in-scope-only` plainly govern this slice but are absent from the frozen four-id list. Plan scope gate + implementation honor both (`database.py` / `candidate.py` only; no `src.core` from `src.data`).
- **Recommendation:** Archie may amend Canon Scope for Radia comparability; no plan or code defect.

### discuss — Epic rollup files on sub tip (not AST-1781 product scope)

- **Severity:** discuss
- **Location:** Full branch diff vs `origin/dev` also includes `src/utils/config.py` + `tests/component/utils/test_config.py` (AST-1779 dependency), `docs/features/dispatcher/ast-1780-*.md` (plan only), `tests/component/ui/api/test_api_jobs.py` + bible § AST-1769 (bug-repro spill from #1 branch)
- **Finding:** AST-1781 product footprint is confined to `database.py`, `candidate.py`, and their tests/bible (~503 lines). Integration-line merge of sibling #1 helper is expected; AST-1769 test has no `api_jobs.py` make-fix on tip.
- **Recommendation:** Chuckles/merge-child hygiene before ftr rollup — not a canon violation for AST-1781 implementation quality.

### advisory — Whitespace-only `system_prompt` edge

- **Severity:** advisory
- **Location:** `src/data/database.py::_agent_task_prompt_texts`
- **Finding:** Whitespace-only `system_prompt` is appended in the segment loop as-is, but effective-system last entry falls through to agent `content` (because `.strip()` is empty). Harmless for token scoring (`empty_render_for_prompts` ignores empty strings) but slightly off the “duplicate stripped system last” mental model.
- **Recommendation:** No action unless UAT surfaces a prompt with whitespace-only system text.

## What's solid

- Stage 1 helpers match plan: `list_dispatch_tasks_for_task_key`, `_agent_task_prompt_texts` (caller order + effective system last), `_token_view_for_empty_render` (operative overlay, no core import), `_force_auto_off_if_empty_render` (no `entity_contexts`, per-row try/except + warning, `auto_mode=0` persist), `revalidate_dispatch_tasks_for_task_key` / `revalidate_dispatch_tasks_for_artifact`.
- Stage 2: `_save_agent_task_on_connection` returns `bool`; public `save_agent_task` revalidates post-commit only when versioned; metadata-only save does not revalidate (tested).
- Stage 3: `save_candidate_data` str-path calls `revalidate_dispatch_tasks_for_artifact` only after real `save_artifact` rotate; identical-to-current and dict paths skip (tested).
- Nine manifest tests cover AC5–AC7 paths including job-token non-force, unbacked artifact key, other-candidate isolation, and hook wiring.
- Estimate **5** fits footprint.

## Recommended actions (Chuckles downstream — not Radia)

1. Append this verdict to `docs/features/dispatcher/ast-1781-revalidate-on-agent-task-artifact-version.md` and push `docs(AST-1781): Radia review — clean` on `origin/sub/AST-1766/AST-1781-revalidate-on-agent-task-artifact-version`.
2. Post slim upshot via `linear_proxy --as radia save-comment`.
3. Move to **Review Posted**; datt routes PROCEED per §3h.
4. Track Copy Output / migration revalidation gap and operative-view vs list-enrichment parity as epic discuss items for #2 / Archie — no resolve-child work required on this tip.
