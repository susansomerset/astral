# AST-513 — Token Gap Correction

**Linear:** [AST-513 — Token Gap Correction](https://linear.app/astralcareermatch/issue/AST-513/token-gap-correction)  
**Parent:** [AST-313 — Artifact pipeline prompt authoring](https://linear.app/astralcareermatch/issue/AST-313/artifact-pipeline-prompt-authoring)  
**Feature ref:** `sub/AST-313/AST-513-token-gap-correction` (origin only)

Susan needs five job-scoped prompt tokens so artifact pipeline prompts (parent **AST-313**) can reference the canonical visible JD and persisted consult analysis for **one job per call**, without hand-pasting consult output or relying on opaque `live_content` alone. This ticket adds registry entries, a core formatter, and call-site threading so `do_task`, Manage Tasks preview, and Ad-hoc preview resolve the same strings production artifact runs use.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add five `TOKEN_SOURCES` rows with `"source": "job"` (skip any name already present); add `JOB_TOKEN_CONFIG` phase map (`grades_key` + `rubric_artifact` per `ANALYSIS_*` token); extend `resolve_tokens(..., job_context=None)` with a `job` branch mirroring `chain` empty-token warnings. | utils |
| `src/core/consult.py` | Add `build_job_token_context(job, candidate_data) -> Dict[str, str]` and `_format_analysis_phase_text(...)` implementing CONSIDER / rubric blob / ANALYSIS RESULT layout; reuse `_rubric_criteria_from_cd` and `_strip_code` for vector↔criterion matching. | core |
| `src/core/agent.py` | Add `_single_job_in_scope(ctx, index)` and `_job_context_for_call(ctx, index, cd)`; pass `job_context` into every `resolve_tokens` / `resolved_task_system` path in `do_task`, `preview_prompt`, and `simulated_chain_context_for_preview`. | core |
| `src/core/candidate.py` | Extend `preview_task_prompt(..., astral_job_id=None)` to load job row and pass `job_context` into `preview_prompt`. | core |
| `src/ui/api/api_admin.py` | Accept optional `astral_job_id` on `GET /tasks/<task_key>/preview`; pass through to `preview_task_prompt`. Thread `job_context` in `_resolve_adhoc` when `entity_id` resolves to a job row. | ui |
| `src/ui/frontend/src/pages/AdminTaskPrompts.tsx` | Preview modal: optional job picker (text input or select from `/api/admin/adhoc/entities?task_key=…`) when `TASK_CONFIG[task_key].entity_type === "job"`; append `astral_job_id` to preview query string. | ui |
| `tests/component/utils/test_config.py` | `resolve_tokens` job-source present/absent/empty-warning cases. | tests |
| `tests/component/core/test_consult.py` | Formatter unit tests: multi-vector layout, missing phase data, missing criterion skip. | tests |
| `tests/component/core/test_agent.py` | `do_task` passes built `job_context` when `batch_size==1` and one job entity. | tests |
| `tests/component/ui/api/test_api_admin.py` | Preview endpoint forwards `astral_job_id`; adhoc preview resolves job tokens when entity is job. | tests |

**Spike / investigation output:** none.

## Stage 1: Registry and `resolve_tokens` job source

**Done when:** `get_tokens()` includes the five new names (unless already present); `resolve_tokens` reads `job_context[name]` for `"source": "job"` entries and logs the same empty-token warning pattern as `chain` / `candidate` when the prompt mentions the token but the value is missing or empty.

1. In `src/utils/config.py`, before editing, `grep` `TOKEN_SOURCES` for `VISIBLE_JD`, `ANALYSIS_JD`, `ANALYSIS_DO`, `ANALYSIS_GET`, `ANALYSIS_LIKE`. **Do not duplicate** any name that already exists.
2. Add `JOB_TOKEN_CONFIG` near `TOKEN_SOURCES`:

```python
JOB_TOKEN_CONFIG = {
    "analysis_phases": {
        "ANALYSIS_JD":   {"grades_key": "jd_grades",   "rubric_artifact": "jobdesc_rubric"},
        "ANALYSIS_DO":   {"grades_key": "do_grades",   "rubric_artifact": "do_rubric"},
        "ANALYSIS_GET":  {"grades_key": "get_grades",  "rubric_artifact": "get_rubric"},
        "ANALYSIS_LIKE": {"grades_key": "like_grades", "rubric_artifact": "like_rubric"},
    },
}
```

3. Register missing tokens in `TOKEN_SOURCES` (group after chain tokens, before closing `}`):

```python
"VISIBLE_JD":    {"source": "job"},
"ANALYSIS_JD":   {"source": "job"},
"ANALYSIS_DO":   {"source": "job"},
"ANALYSIS_GET":  {"source": "job"},
"ANALYSIS_LIKE": {"source": "job"},
```

4. Extend `resolve_tokens` signature to `resolve_tokens(text, candidate_data, task_key, chain_context=None, job_context=None)`.
5. In `_replace`, after the `chain` branch, add:

```python
if spec["source"] == "job":
    raw = (job_context or {}).get(name)
    if raw is None or raw == "" or raw == []:
        _log.warning("Token {$%s} resolved to empty (job_context, task=%s)", name, task_key)
    return _value_to_str(raw) if raw is not None else ""
```

6. Preserve forward-compat: unknown token names still leave literal `{$FOO}`; registered job tokens with no value resolve to `""` (not literal).

⚠️ **Decision:** Job tokens use a **`job_context` dict** (precomputed strings injected by core/UI), not dot-paths into `job_data` inside `config.py`. Keeps `utils` free of data-layer imports and matches the `chain_context` pattern from **AST-304** / **AST-455**.

## Stage 2: Formatters in `consult.py`

**Done when:** Given a job row with populated `job_data` and a candidate with rubric artifacts, `build_job_token_context` returns non-empty strings for `VISIBLE_JD` and each `ANALYSIS_*` phase that has persisted grades; missing phases return `""`.

1. In `src/core/consult.py`, add `_format_analysis_phase_text(phase_token: str, job_data: dict, candidate_data: dict) -> str`:
   - Look up `JOB_TOKEN_CONFIG["analysis_phases"][phase_token]`; if missing, return `""`.
   - Read `grades = job_data.get(grades_key)`; if not a non-empty `list`, return `""`.
   - Load rubric criteria via `_rubric_criteria_from_cd(candidate_data, rubric_artifact)`; if empty list, return `""`.
   - For each grade dict in `grades` (skip non-dicts):
     - `vector_label = str(g.get("vector") or "").strip()`; if empty, skip.
     - Find criterion where `_strip_code(str(c.get("label") or "")) == _strip_code(vector_label)`.
     - If no criterion match, log warning and **skip that vector** (do not fail the whole token).
     - `title = str(criterion.get("label") or vector_label).strip()`
     - `rubric_blob = str(criterion.get("content") or "").strip()` — full editable rubric markdown blob, **not** parsed `grade_descriptions`.
     - `letter = str(g.get("grade") or "").strip().upper()`
     - `conf = g.get("confidence")`; format confidence as integer `/5` when numeric, else `0/5`.
     - Emit block:

```
CONSIDER: {title}
{rubric_blob}
ANALYSIS RESULT: {letter} ({conf}/5 confidence)
```

   - Join vector blocks with `\n\n`. No JSON anywhere in output.

2. Add `build_job_token_context(job: Dict[str, Any], candidate_data: dict) -> Dict[str, str]`:
   - `jd_data = job.get("job_data") if isinstance(job.get("job_data"), dict) else {}`
   - `visible = (jd_data.get("job_description") or "").strip()` — plain JD text only: **no** `[index=NNN]:` prefix, **no** company website appendix (contrast `_prep_live_content` in the same file).
   - For each key in `("ANALYSIS_JD", "ANALYSIS_DO", "ANALYSIS_GET", "ANALYSIS_LIKE")`, set value to `_format_analysis_phase_text(key, jd_data, candidate_data)`.
   - Return `{"VISIBLE_JD": visible, "ANALYSIS_JD": ..., ...}` with all five keys always present (values may be empty strings).

3. Do **not** add `{$ANALYSIS_UPSHOT}` or any token beyond the five named in the ticket.

## Stage 3: Thread `job_context` through `do_task` and preview

**Done when:** A single-job artifact `do_task` call (e.g. `contemplate_job` via `run_resume_artifact_chain_for_job` with `batch_size: 1`) resolves `{$VISIBLE_JD}` and `{$ANALYSIS_*}` in system/cache/user/nocache segments; multi-job batches leave job tokens empty with warnings.

1. In `src/core/agent.py`, add helpers:

```python
def _single_job_in_scope(ctx: Optional[Dict[str, Any]], index: Optional[str]) -> bool:
    if not ctx or not index:
        return False
    bs = ctx.get("batch_size")
    if bs is not None and int(bs) != 1:
        return False
    entities = ctx.get("batch_entities") or []
    if isinstance(entities, list) and len(entities) == 1:
        return str(entities[0].get("astral_job_id") or "") == str(index)
    job = ctx.get("job")
    if isinstance(job, dict) and str(job.get("astral_job_id") or "") == str(index):
        return True
    return False

def _job_row_from_ctx(ctx: Dict[str, Any], index: str) -> Dict[str, Any]:
    for key in ("job",):
        row = ctx.get(key)
        if isinstance(row, dict) and str(row.get("astral_job_id") or "") == str(index):
            return row
    for ent in ctx.get("batch_entities") or []:
        if isinstance(ent, dict) and str(ent.get("astral_job_id") or "") == str(index):
            return ent
    return {"astral_job_id": index, "job_data": {}}
```

2. Add `_job_context_for_call(ctx, index, cd) -> Optional[Dict[str, str]]`: when `_single_job_in_scope(ctx, index)`, `from src.core import consult as _consult` and return `_consult.build_job_token_context(_job_row_from_ctx(ctx, index), cd)`; else return `None` (or `{}` — pick one and use consistently so warnings fire only when token appears in text).

3. Update `resolved_task_system(...)` to accept optional `job_context` and pass it into `resolve_tokens`.

4. In `do_task`, after `cd` is resolved and before prompt assembly, set `jc = _job_context_for_call(ctx or {}, index, cd)`. Pass `jc` into **every** `resolve_tokens` call and into `resolved_task_system` for system block resolution.

5. In `preview_prompt`, add parameter `job_context: Optional[Dict[str, str]] = None` and pass through all six segment resolutions the same way.

6. In `simulated_chain_context_for_preview`, accept optional `job_context` and pass it into nested `resolve_tokens` / `resolved_task_system` calls so chain-sim previews still resolve job tokens when a job is selected.

7. Recursive `do_task` / `run_next` hops: **reuse the same outer `ctx` and `index`** (already true per **AST-303** Revision 1). Recompute `job_context` on each hop from the same ctx — do not narrow or drop job scope between hops.

## Stage 4: Admin preview parity (Manage Tasks + Ad-hoc)

**Done when:** `GET /api/admin/tasks/contemplate_job/preview?candidate_id=…&astral_job_id=…` returns resolved segments with non-empty job tokens when that job has consult data; Ad-hoc preview with a job `entity_id` matches for the same inputs.

1. In `src/core/candidate.py`, extend `preview_task_prompt(..., astral_job_id: Optional[str] = None)`:
   - When `astral_job_id` is non-empty, `job = database.get_job(astral_job_id)`; if missing, raise `ValueError(f"Job not found: {astral_job_id}")`.
   - `jc = build_job_token_context(job, cd)` when job loaded; else `jc = None`.
   - Pass `job_context=jc` into `preview_prompt`.

2. In `src/ui/api/api_admin.py` `preview_task`, read `astral_job_id = (request.args.get("astral_job_id") or "").strip()` and pass to `preview_task_prompt`.

3. In `_resolve_adhoc`, after `cd` is loaded and before the return dict:
   - When `task_cfg.get("entity_type") == "job"` and `body.get("entity_id")` is non-empty, load job via `database.get_job(entity_id.strip())`.
   - If job exists, `jc = build_job_token_context(job, cd)` (import from `src.core.consult`).
   - Pass `job_context=jc` into all four `resolve_tokens` calls (and system path if split).

4. In `src/ui/frontend/src/pages/AdminTaskPrompts.tsx`:
   - Add state `previewJobId` (string).
   - When opening preview for a task whose `entity_type` is `"job"` (read from loaded task row or `TASK_CONFIG` — use whichever the page already has; if neither, fetch task detail once), show a labeled text input **Job ID (optional)** above Preview Resolved.
   - On preview fetch, append `&astral_job_id=${encodeURIComponent(previewJobId)}` when non-empty.
   - No change to token picker merge logic — new names appear automatically via `/api/admin/tasks/meta/tokens` (`get_tokens()`).

## Stage 5: Tests

**Done when:** Component tests cover formatter layout, registry resolution, single-job `do_task` threading, and admin preview query param — pytest green for touched files.

1. `tests/component/utils/test_config.py`: job token resolves value; empty `job_context` + registered token → `""` + warning (mock logger if existing tests do); unknown token unchanged.
2. `tests/component/core/test_consult.py`: `_format_analysis_phase_text` / `build_job_token_context` with fixture job_data + rubric criteria — assert CONSIDER line, rubric `content` body, ANALYSIS RESULT line; missing `do_grades` → empty `ANALYSIS_DO`; `VISIBLE_JD` excludes index prefix and company block.
3. `tests/component/core/test_agent.py`: minimal `do_task` with `batch_entities=[job]`, `batch_size=1`, prompt containing `{$VISIBLE_JD}` — assert resolved system/user contains JD substring (monkeypatch Anthropic path as existing tests do).
4. `tests/component/ui/api/test_api_admin.py`: preview route passes `astral_job_id` into `preview_task_prompt` spy; adhoc preview resolves job token when entity is job.

## Self-Assessment

**Scope:** `Single-Component` — Touches token registry and `resolve_tokens` in `config.py`, formatting helpers in `consult.py`, call-site threading in `agent.py` / `candidate.py`, admin preview API, and a small Manage Tasks preview UI field; no consult grading, dispatch wiring, or artifact chain `run_next` changes.

**Conf:** `high` — Reuses established `chain_context` injection, existing rubric criteria helpers, and persisted `job_data` keys (`jd_grades`, `do_grades`, etc.) already written by consult; acceptance criteria are fully specified in the Linear description.

**Risk:** `Medium` — Incorrect single-job detection or formatter drift would produce empty or wrong prompt substitutions for artifact tasks only; existing candidate and chain tokens are unaffected when not referenced.

## Self-review vs `ASTRAL_CODE_RULES.md`

| Section | Check |
|---------|--------|
| §1.3 DRY | One formatter (`_format_analysis_phase_text`) and one builder (`build_job_token_context`); one `_job_context_for_call` helper in `agent.py` — no duplicated format strings in UI or admin. |
| §2.1 config | Token names and phase→key map live in `TOKEN_SOURCES` / `JOB_TOKEN_CONFIG`; no scattered magic token strings outside registry, formatter, and tests. |
| §2.4 batch | Job tokens apply only when `_single_job_in_scope` is true; multi-job consult batches unchanged. |
| §2.6 state machine | Read-only use of persisted consult outputs; no new transitions. |
| §3.3 imports | `config.py` does not import `database` or `tracker`; job strings built in core and passed as `job_context`. |
| §3.5 naming | Snake_case Python; token names remain `UPPER_SNAKE` per registry convention. |

**Conflicts:** None identified. Depends on merged baseline (**AST-304** / **AST-455** `chain_context`, **AST-450** artifact task keys, **AST-479** / **AST-480** consult persistence) already on `dev-ada` after §4 merge.

## Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-313/AST-513-token-gap-correction`  
**Product commits:** `420c6f56` (config — `JOB_TOKEN_CONFIG`, five job tokens, `resolve_tokens` job branch), `21a4d216` (core — `build_job_token_context`, CONSIDER/rubric/ANALYSIS RESULT formatter), `116d2667` (core — `_single_job_in_scope`, `do_task` / preview threading), `d827f33a` (ui — admin preview `astral_job_id`, adhoc job tokens, Manage Tasks job picker)

## Review

**Diff:** `origin/dev...origin/sub/AST-313/AST-513-token-gap-correction` (13 files, +681 / −28)  
**Reviewed:** 2026-05-28 (Radia)

### What's solid

- All five job tokens registered in `TOKEN_SOURCES` with `"source": "job"`; phase map in `JOB_TOKEN_CONFIG` matches persisted keys (`jd_grades`, `do_grades`, `get_grades`, `like_grades`) and rubric artifacts — aligns with ticket AC 1–3 and §2.1 config-as-truth.
- `build_job_token_context` / `_format_analysis_phase_text` emit CONSIDER / rubric blob / ANALYSIS RESULT text (not JSON); `VISIBLE_JD` uses plain `job_description` without coat-check index prefix or company appendix — matches functional scope.
- `job_context` threading mirrors `chain_context` (AST-304/455): utils stays free of data imports; core precomputes strings and passes dict through `do_task`, `preview_prompt`, `simulated_chain_context_for_preview`, admin preview, and adhoc resolve.
- `_single_job_in_scope` gates tokens correctly; `run_resume_artifact_chain_for_job` already sets `batch_size: 1` + `batch_entities: [job]`, so production artifact entry resolves tokens on first hop and recomputes on `run_next` hops via shared `ctx`.
- Manage Tasks preview forwards `astral_job_id`; `get_task` exposes `entity_type` so the job ID field renders for job-entity tasks; adhoc preview resolves when `entity_type === "job"`.
- Component tests cover registry, formatter layout, single-job `do_task` threading, API param forwarding, and frontend query string — matches Betty manifest §7.13zj.

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| **fix-now** | `src/core/agent.py` — `_job_context_for_call` | Function-scoped `from src.core import consult` lacks the cycle-break comment used elsewhere in the same file (`run_resume_artifact_chain_for_job` L647–648). **B1** — add one line explaining consult imports `do_task` at module load. |
| **advisory** | `src/ui/frontend/src/pages/AdminTaskPrompts.tsx` | Job preview uses text input only; plan Stage 4 mentioned optional entity dropdown from `/api/admin/adhoc/entities`. AC 4 is met without dropdown — Susan may prefer picker UX in a follow-up. |

### Recommended actions

| Item | Action |
|------|--------|
| Lazy import comment | In `_job_context_for_call`, add comment matching `run_resume_artifact_chain_for_job` before the consult import; re-publish to `origin/sub/AST-313/AST-513-token-gap-correction`. |
| Resolve | Engineer runs `resolve-astral` for the fix-now row; no other code changes required for merge. |

## Resolution

**Resolved:** 2026-05-28 (Ada)

| Radia item | Action |
|------------|--------|
| **fix-now** — `_job_context_for_call` lazy import comment | Added cycle-break comment matching `run_resume_artifact_chain_for_job` (consult imports `do_task` at module load). |
| **advisory** — Manage Tasks job entity dropdown | No change; AC 4 met with text input per Radia sign-off. |
