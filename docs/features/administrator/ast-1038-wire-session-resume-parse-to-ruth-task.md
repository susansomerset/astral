# AST-1038 — Wire Session Resume Parse to Ruth task

**Linear:** [AST-1038](https://linear.app/astralcareermatch/issue/AST-1038/wire-session-resume-parse-to-ruth-task-simple-resume-parse-function)  
**Parent:** [AST-1036](https://linear.app/astralcareermatch/issue/AST-1036/simple-resume-parse-function) — Simple Resume Parse function  
**Publish ref:** `sub/AST-1036/AST-1038-wire-session-resume-parse-to-ruth-task`

Point Admin Session Resume Paste parse at the Ruth `simple_resume_parse` task delivered by **AST-1037**, instead of Judith `craft_resume_base`. Keep the existing no-persist / no-candidate-bind response contract, session-sentinel ledger, and Style D debug on the hop. Prefer zero Paste UI change. Do **not** author task/schema/seed (sibling owns that). Do **not** change candidate-bound Judith craft.

**Prerequisite:** This sub must already include AST-1037 product tip via `origin/ftr/ast-1036-simple-resume-parse-function` (merge-on-checkout). `TASK_CONFIG["simple_resume_parse"]`, Ruth `agent_task` seed, and `_CRAFT_RESUME_NORMALIZE_TASK_KEYS` must exist before Stage 1.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/candidate.py` | In `run_session_resume_parse` only: `do_task` uses `task_key="simple_resume_parse"`; update docstring + non-dict error string; leave ledger / synthetic ctx / Style D / split helpers as they are | core |
| `src/ui/api/api_admin.py` | Docstring on `session_resume_parse` only — still thin `@require_admin` → `run_session_resume_parse`; no request/response shape change | ui |

**No changes expected:** `src/utils/config.py` / `data/admin/agent_task.json` (AST-1037), `parse_candidate_resume`, `run_candidate_artifact_generation`, Judith `craft_resume_base` row/meta, `AdminSessionResumePaste.tsx`, Open HTML / `session_resume/html`, `src/core/agent.py` normalize gate (already covers both keys).

## Stage 1: Core wire — `run_session_resume_parse` → Ruth

**Done when:** `run_session_resume_parse` calls `do_task` with `simple_resume_parse`; success/error JSON shapes and ledger sentinel behavior are unchanged; `parse_candidate_resume` / `run_candidate_artifact_generation` still use `craft_resume_base`.

1. In `src/core/candidate.py`, locate `run_session_resume_parse` (AST-986 session paste path). Keep validation, `default_resume_structure()`, synthetic `ctx` (no `astral_candidate_id`), ledger (`ledger_task_key = "user-session-parse-resume"`, `candidate_id="session"`), `log_batch_id`, `asyncio.run(do_task(...))`, `split_craft_resume_base_payload`, Style D `debug_index` / `debug_detail` / `_debug_experience_jobs`, and `finally` flush — **do not** redesign those.

2. Change the `do_task` call from:

```python
task_key="craft_resume_base",
```

to:

```python
task_key="simple_resume_parse",
```

Keep `live_content=paste`, `index=batch_id`, `ctx=ctx`, `debug=debug` unchanged.

⚠️ **Decision:** Use the literal TASK_CONFIG key `"simple_resume_parse"` at this single call site (same pattern as the prior `"craft_resume_base"` literal). Do **not** add a new config block for one caller; do **not** invent a second session-parse entrypoint. Shared schema + normalize membership already live in config from AST-1037.

⚠️ **Decision:** Keep reusing `split_craft_resume_base_payload` / `normalize_craft_resume_base_agent_payload` (via do_task normalize frozenset). Shared schema identity means the session response contract (`resume_structure` / `base_resume` / `parsed_response`) does not change for the Paste UI or Open HTML.

3. Update the function docstring to say paste is parsed via `simple_resume_parse` (Ruth / Little), not `craft_resume_base`.

4. Update the non-dict failure string from `"craft_resume_base returned non-dict parsed_response"` to `"simple_resume_parse returned non-dict parsed_response"` (same HTTP 500 shape).

5. **Forbidden in this stage:** editing `parse_candidate_resume`, `run_candidate_artifact_generation`, `_persist_craft_dispatch_success`, `TASK_CONFIG`, `agent_task` seeds, or any React file. Grep after edit must still show `task_key="craft_resume_base"` in those candidate craft paths.

## Stage 2: Admin route docstring (thin contract unchanged)

**Done when:** `POST /api/admin/session_resume/parse` still validates body, calls `run_session_resume_parse`, returns `(body, status)` unchanged; docstring no longer claims craft-base.

1. In `src/ui/api/api_admin.py`, update the `session_resume_parse` docstring from “paste → craft_resume_base …” to “paste → simple_resume_parse (Ruth) …” (or equivalent one-liner). Do **not** change route path, `@require_admin`, request fields, or response handling.

⚠️ **Decision:** Prefer zero Paste UI change — React already posts `resume_text` and consumes `success` / `resume_structure` / `base_resume` / `parsed_response`; the wire is core-only.

## Stage 3: Compile check (plan-owned files only)

**Done when:** Touched Python modules compile; no edits under `tests/` (Betty owns the test tree).

```bash
python3 -m compileall -q src/core/candidate.py src/ui/api/api_admin.py
```

Optional sanity (venv):

```bash
python3 -c "from src.utils import config as c; assert 'simple_resume_parse' in c.TASK_CONFIG"
```

## Self-Assessment

**Scope:** `Single-Component` — one core call-site swap (+ docstring/error string) and a thin Admin docstring; no catalog/seed/UI work.

**Conf:** `high` — AST-1037 already delivered the Ruth task, shared schema, and normalize membership; AST-986 established the session sentinel / response contract this ticket only re-keys.

**Risk:** `low` — candidate Judith craft paths stay on `craft_resume_base`; session response shape unchanged; wrong key would fail `do_task` / schema immediately rather than silently corrupt candidates.

## Code Rules check

- **§1.1 / in-scope-only:** No Judith craft / Open HTML / Paste chrome / sibling catalog edits.
- **§1.4 / no-hardcoded-sets:** No new membership frozensets; single task-key literal at the existing call site (catalog key authored in AST-1037 config).
- **§2.1 / config source of truth:** Task meta/schema remain in `TASK_CONFIG` from AST-1037; this ticket only selects that key.
- **§2.2 / do-task delegation:** Still reaches the model only via `do_task`.
- **§1.5.1 / debug-contract-gated:** Preserve existing Style D gated on `debug=True`; no new ungated debug lines.
- **§3.3 imports:** UI stays ui → core; no new data imports in Admin route.
- **pattern.ui.admin-endpoint / require-auth:** Route stays thin + `@require_admin`.

## Review (Radia — code-rubric.v1)

[code-rubric] revision=1  
**Rubric:** code-rubric.v1  
**Ticket:** AST-1038  
**Publish ref tip:** (post-docs) `origin/sub/AST-1036/AST-1038-wire-session-resume-parse-to-ruth-task`  
**Overall:** DISCUSS

### What's solid
- Thin wire: `run_session_resume_parse` → `task_key="simple_resume_parse"`; Admin docstring only; `@require_admin` kept.
- Style D / sentinel ledger / no-bind contract preserved; Judith craft call sites untouched in this ticket's `code()` SHA.
- Matches plan Stages 1–2; Self-Assessment Single-Component still accurate.

### Findings
**discuss (C4 straggler):** Joan Excluded `spikes-under-debug-dir`, `docs.features-single-file-per-ticket`, `engineer-test-tree-ban`, `utils-data-late-import-only`; tip three-dot (includes rolled AST-1037 + this child) makes them in-scope. Substance **conforms**. Acknowledge on resolve — no product edit expected.

### Recommended
Ada: acknowledge C4 stragglers → `resolve-child`.
