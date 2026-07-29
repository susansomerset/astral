# AST-1055 — meteorite_like + meteorite upshot agent tasks

**Linear:** [AST-1055](https://linear.app/astralcareermatch/issue/AST-1055/meteorite-like-meteorite-upshot-agent-tasks-processing-meteorites)
**Parent:** [AST-1052](https://linear.app/astralcareermatch/issue/AST-1052/processing-meteorites) — Processing meteorites
**Publish ref:** `origin/sub/AST-1052/AST-1055-meteorite-like-meteorite-upshot-agent-tasks`

Register company-absent **agent_task twins** `meteorite_like` and `meteorite_upshot`: same LIKE rubric / same upshot response schema as `grade_like` / `analysis_upshot`, but prompts that assume **no employer website / culture / vibe pages**, tell Grace to use grade **X** (confidence 0) liberally when signal is thin, and tell Estelle to emphasize lack of company visibility. Wire `TASK_CONFIG` + consult routing so AST-1054 can dispatch these keys. Does **not** own dispatch_task rows, Create landing, or the Recommended Meteorites UI section.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `TASK_CONFIG` twins; extend `RECOMMENDED` priors; resolve `rubric_owner_task_key` via `rubric_artifact`; add twins to batch-mode frozensets | utils |
| `data/admin/agent_task.json` | Add `meteorite_like` + `meteorite_upshot` rows (prompt twins) | data/admin |
| `src/core/consult.py` | Route twins through existing LIKE / upshot batch paths; JD-only prep (`requires_company: False`) | core |
| `src/core/agent.py` | Add `meteorite_like` to `_STRICT_ENCODED_BATCH_CONSULT_KEYS` | core |
| `src/core/dispatcher.py` | Add `meteorite_like` to `_CHUNK_EXHAUST_CONSULT_JOB_KEYS` | core |

## Stage 1: `TASK_CONFIG` twins + `RECOMMENDED` priors + rubric owner resolve

**Done when:** `meteorite_like` and `meteorite_upshot` exist in `TASK_CONFIG` with meteorite pass/fail/error states; `RECOMMENDED` accepts hops from `METEORITE_PASSED_LIKE` / `METEORITE_PASSED_LIKE_RETRY`; `rubric_owner_task_key("meteorite_like")` resolves to `grade_like` via `like_rubric`; no dispatch trigger rules and no Create / Recommended UI edits.

1. In `src/utils/config.py`, immediately after the existing `"grade_like"` / `"analysis_upshot"` blocks inside `TASK_CONFIG`, add:

```python
# AST-1052 / AST-1055: company-absent twins (no CULTURE_READY / vibe pages).
# Dispatch rows + trigger_state rules are AST-1054 — keys must match that sibling.
"meteorite_like": {
    "scored": True,
    "grades_key": "like_grades",
    "rubric_artifact": "like_rubric",
    "response_format": "json",
    "output_type": "grades_encoded_notes",
    "response_schema": {
        "jobs": {
            "type": "list",
            "required": True,
            "items_schema": _ENCODED_CONSULT_JOB_ITEM_SCHEMA,
        },
    },
    "fallback_batch_size": 10,
    "pass_state": "METEORITE_PASSED_LIKE",
    "fail_state": "METEORITE_FAILED_LIKE",
    "error_state": "METEORITE_FAILED_TECHNICAL_LIKE",
    "save_prefix": "like",
    "pass_threshold": 6.0,
    "requires_company": False,
    "grading_mode": "scored",
    "context_format": "meteorite_like_{index}",
    "entity_type": "job",
    "requires_candidate_key": True,
    "trigger_state": None,
    "agent_task": "meteorite_like",
},
"meteorite_upshot": {
    "scored": True,
    "response_format": "json",
    "response_schema": {
        # identical keys/types to analysis_upshot.response_schema — copy literally, do not invent fields
        "take_jd": {"type": "str", "required": True},
        "take_get": {"type": "str", "required": True},
        "take_do": {"type": "str", "required": True},
        "take_like": {"type": "str", "required": True},
        "whole_jd_upshot": {"type": "str", "required": True},
        "segment_upshots": {
            "type": "list",
            "required": True,
            "items_schema": {
                "segment_key": {"type": "str", "required": True},
                "upshot": {"type": "str", "required": True},
            },
        },
        "candidate_questions": {
            "type": "list",
            "required": True,
            "items_schema": {"text": {"type": "str", "required": True}},
        },
        "caveats": {
            "type": "list",
            "required": True,
            "items_schema": {"text": {"type": "str", "required": True}},
        },
    },
    "pass_state": "RECOMMENDED",
    "error_state": "METEORITE_PASSED_LIKE_RETRY",
    "context_format": "meteorite_upshot_{index}",
    "entity_type": "job",
    "requires_candidate_key": True,
    "requires_company": False,
    "agent_task": "meteorite_upshot",
    "trigger_state": None,
},
```

⚠️ **Decision — task keys `meteorite_like` + `meteorite_upshot`:** Matches parent/child naming (`meteorite_like`, “meteorite upshot”). AST-1054 must seed dispatch rows with these exact `task_key` strings.

⚠️ **Decision — `requires_company: False`:** `_prep_live_content` sends jobs to `NEED_WEBSITE_CONTENT` when a company is passed and `website_content` is missing. Meteorite placeholders have no culture/vibe pages; requiring company would yank jobs off the meteorite track onto a non-meteorite state. JD-only prep + prompt caveats satisfy AC3/AC4.

⚠️ **Decision — same LIKE rubric / same upshot schema:** Do **not** invent a new rubric artifact. `rubric_artifact: "like_rubric"` keeps Grace on the existing like rubric; upshot `response_schema` is a literal copy of `analysis_upshot`. Pass/fail math (`_render_pass_fail`) is unchanged — liberal **X** is prompt guidance, not a scoring rule change.

⚠️ **Decision — `pass_state: "RECOMMENDED"` for `meteorite_upshot`:** Mirrors `analysis_upshot` so post-upshot jobs land on the shared Recommended surface; AST-1057 owns the distinct Meteorites **section** filter/UI. Persist parsed JSON under job_data key `analysis_upshot` (same as the non-meteorite path) so report consumers keep working.

2. In the same file, extend `JOB_STATES["RECOMMENDED"]["prior_states"]` to also allow `"METEORITE_PASSED_LIKE"` and `"METEORITE_PASSED_LIKE_RETRY"` (append; do not remove existing priors).

⚠️ **Decision — extend `RECOMMENDED` priors on this ticket:** AST-1053 deferred Recommended membership UI to AST-1057 but upshot cannot lawfully transition without priors. Extending priors is required for AC4; the Meteorites **section** remains AST-1057. Do **not** change `RECOMMENDED_JOB_STATES` / Recommended UI section lists here.

3. Update `rubric_owner_task_key` so twin consumers resolve via `TASK_CONFIG["…"]["rubric_artifact"]`:

```python
def rubric_owner_task_key(task_key: str) -> Optional[str]:
    if task_key in _RUBRIC_OWNER_TASK_BY_CONSUMER_TASK_KEY:
        return task_key
    artifact = CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY.get(task_key)
    if artifact:
        return RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY.get(artifact)
    rk = (TASK_CONFIG.get(task_key) or {}).get("rubric_artifact")
    if isinstance(rk, str) and rk.strip():
        return RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY.get(rk.strip())
    return None
```

Do **not** add `meteorite_like` to `RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY` (owner stays `grade_like`).

4. Add `"meteorite_like"` to `_DISPATCH_BATCH_CALL_MODE_ONE` (next to `"grade_like"`). Do **not** add `_dispatch_trigger_state_for_task_key` branches for either twin (AST-1054). Do **not** edit `METEORITE_CONFIG`, Create paths, or Recommended UI constants beyond the `RECOMMENDED` prior list in step 2.

**Done when (recheck):** `TASK_CONFIG["meteorite_like"]["pass_state"] == "METEORITE_PASSED_LIKE"`; `TASK_CONFIG["meteorite_upshot"]["error_state"] == "METEORITE_PASSED_LIKE_RETRY"`; both have `requires_company is False`; `RECOMMENDED` priors include the two meteorite LIKE states; `rubric_owner_task_key("meteorite_like") == "grade_like"`; `python3 -m py_compile src/utils/config.py` succeeds.

## Stage 2: Repo `agent_task.json` prompt twins

**Done when:** `data/admin/agent_task.json` contains current rows for `meteorite_like` and `meteorite_upshot` with the prompt deltas below; same agents as the non-meteorite twins; Job Review grouping metadata is set.

1. Append two objects to the `data/admin/agent_task.json` array (flat scalars only — no nested JSON objects/arrays as field values).

**`meteorite_like` row**

| Field | Value |
|-------|--------|
| `task_key_uuid` | new random UUID4 string |
| `task_key` | `meteorite_like` |
| `current` | `1` |
| `agent_id` | `job_analyst_grace` (same as `grade_like`) |
| `user_prompt` | **copy** `grade_like.user_prompt` verbatim |
| `cache_prompt` | start from `grade_like.cache_prompt`, then apply the edits in step 2 |
| `cache_prompt_b` / `c` / `d` / `nocache_prompt` / `run_next` | `""` |
| `task_group_order` | `"4000"` |
| `task_group_name` | `Job Review` |
| `task_seq` | `10` |
| `task_name` | `Grade Job: Like (Meteorite)` |
| `updated_at` | current UTC `YYYY-MM-DD HH:MM:SS` |

**`meteorite_upshot` row**

| Field | Value |
|-------|--------|
| `task_key_uuid` | new random UUID4 string |
| `task_key` | `meteorite_upshot` |
| `current` | `1` |
| `agent_id` | `principal_recruiter_estelle` (same as `analysis_upshot`) |
| `user_prompt` | start from `analysis_upshot.user_prompt`, then apply the edits in step 3 |
| `cache_prompt` / `b` / `c` / `d` / `nocache_prompt` / `run_next` | `""` |
| `task_group_order` | `"4000"` |
| `task_group_name` | `Job Review` |
| `task_seq` | `11` |
| `task_name` | `Analysis Upshot (Meteorite)` |
| `updated_at` | current UTC `YYYY-MM-DD HH:MM:SS` |

2. **`meteorite_like` `cache_prompt` edits** (only these; keep rubric / payload / candidate blocks identical):

- In STEP 1, replace any “JD and company context” / employer-website implication with: grade meaningful fit from the **JD and candidate materials only** — **no employer website, culture pages, or vibe pages are available** for this meteorite-sourced job.
- After the existing **Embrace the X** paragraph, add one short paragraph: because company visibility is absent, use grade **X** with confidence **0** **more liberally** whenever the JD does not supply clear evidence for a vector; do not invent company culture or employer vibe.
- Replace wording that assumes provided company context pages with “JD text (company website/culture content is not provided).”
- Keep the existing **On F** / “Do not fail by vibe” dealbreaker rules (they still apply to JD text).

3. **`meteorite_upshot` `user_prompt` edits:**

- After `## INSTRUCTIONS` (before the required-keys list), insert a `### Meteorite context` subsection stating: this job is meteorite-sourced; Astral does **not** have hiring-company website / culture visibility; synthesis must not invent employer vibe; call out thin company signal in **caveats** and temper **take_like** / chemistry language accordingly.
- Keep the required top-level JSON keys identical to `analysis_upshot`.

⚠️ **Decision — prompts live only in `agent_task.json`:** Matches existing `grade_like` / `analysis_upshot` (no parallel `_taskprompts` files). Startup `apply_repo_admin_json` ships the rows; do not hand-edit DB.

**Done when (recheck):** both `task_key`s present in the JSON array; `meteorite_like.cache_prompt` contains “meteorite” / no-vibe / liberal **X** language; `meteorite_upshot.user_prompt` contains the Meteorite context subsection; JSON still parses as a flat-row array.

## Stage 3: Consult / agent / dispatcher routing for the twins

**Done when:** `run_consult_task` executes `meteorite_like` via the encoded LIKE path and `meteorite_upshot` via the upshot batch path; JD-only prep never transitions meteorite jobs to `NEED_WEBSITE_CONTENT`; upshot persists `job_data.analysis_upshot` and transitions with twin `TASK_CONFIG` states.

1. In `src/core/consult.py`:

- Add `"meteorite_like": "LIKE"` to `_GRADE_DISPATCH_TO_HEADER`.
- Extend the encoded-batch / single-job `run_consult_task` branches that currently special-case `("grade_do", "grade_get", "grade_like")` so they also accept `"meteorite_like"`. For the multi-job map, add `"meteorite_like":` a thin wrapper identical to `grade_like_batch` that calls `_consult_scored_dispatch_batch_encoded("meteorite_like", …)` (or fold into one helper keyed by `dispatch_task_key` — prefer one shared path; do not duplicate decode/pass-fail logic).
- Generalize `_run_analysis_upshot_batch` to take the orchestration `task_key` (default `"analysis_upshot"`). Use `TASK_CONFIG[task_key]` for `requires_company` / `error_state` / `pass_state` / `do_task(task_key=…)`. Always `tracker.save_job_data(aid, {"analysis_upshot": parsed})` regardless of twin key. Route `run_consult_task` so `task_key == "meteorite_upshot"` calls this batch with `task_key="meteorite_upshot"`.
- In `_prep_analysis_upshot_live_content`, pass `scoring_task_key` through (default `"analysis_upshot"`) instead of hardcoding — so any future company-required path uses the twin key. With `requires_company: False`, callers pass `company=None` and prep stays JD + listing + consult recap only.

2. In `src/core/agent.py`, add `"meteorite_like"` to `_STRICT_ENCODED_BATCH_CONSULT_KEYS`.

3. In `src/core/dispatcher.py`, add `"meteorite_like"` to `_CHUNK_EXHAUST_CONSULT_JOB_KEYS`.

4. Do **not** edit `_INPUT_STATE_TO_TASK` (legacy; dispatch uses explicit `dispatch_task_key`). Do **not** add gazer culture hops. Do **not** edit `tests/` or bible.

**Done when (recheck):** `python3 -m py_compile src/core/consult.py src/core/agent.py src/core/dispatcher.py src/utils/config.py` succeeds; grepping `run_consult_task` shows both twin keys handled; no new references to `fetch_culture_pages` / `CULTURE_READY` on the meteorite twin paths.

## Out of scope (do not implement here)

- Dispatch_task rows, `score_floor` 0, `_dispatch_trigger_state_for_task_key` rules for the twins (AST-1054).
- `JOB_STATES` meteorite track registration (AST-1053 — already on `ftr`).
- Create landing / `METEORITE_CONFIG["job_create_state"]` (AST-1056).
- Recommended page Meteorites **section** UI (AST-1057).
- Changing non-meteorite `grade_like` / `analysis_upshot` prompts or states.
- Editing `tests/` or `docs/test-bible/**` (Betty after Code Complete).

## Self-Assessment

**Scope:** `Single-Component` — config + agent_task prompts + consult/agent/dispatcher routing for two twin task keys; no UI.

**Conf:** `high` — mirrors existing `grade_like` / `analysis_upshot` orchestration; company-absent behavior is `requires_company: False` + prompt deltas; rubric stays `like_rubric`.

**Risk:** `Medium` — wrong `requires_company` or prep would send meteorites to `NEED_WEBSITE_CONTENT`; wrong pass/fail states or missing `RECOMMENDED` priors would block the track; mitigated by explicit twin tables and JD-only prep.

## Rules self-review

- **§2.1 / config-source-of-truth / no-hardcoded-sets:** Task keys, states, schemas only in `TASK_CONFIG` / `JOB_STATES`; prompts in repo `agent_task.json`.
- **§2.6 / job-prior-states-enforced:** `RECOMMENDED` priors extended for lawful meteorite upshot landing; LIKE fail/pass use AST-1053 meteorite states.
- **§1.3 DRY:** Reuse `_consult_scored_dispatch_batch_encoded` / generalized upshot batch; do not fork decode or pass/fail.
- **§3.3 import direction:** Core consult/agent/dispatcher; no UI → core violations.
- **Boundaries:** No dispatch seed, Create, or Recommended section work.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1052/AST-1055-meteorite-like-meteorite-upshot-agent-tasks`
**Plan path:** `docs/features/meteorite/ast-1055-meteorite-like-meteorite-upshot-agent-tasks.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `be9e9f73` | TASK_CONFIG meteorite_like/upshot twins + RECOMMENDED priors |
| 2 | `ca3fe5d9` | agent_task meteorite_like + meteorite_upshot prompts |
| 3 | `2c701210` | route meteorite_like + meteorite_upshot through consult |

**Tip:** `2c701210cff28b9678aad731a434e2e9bd99d952` on `origin/sub/AST-1052/AST-1055-meteorite-like-meteorite-upshot-agent-tasks`
