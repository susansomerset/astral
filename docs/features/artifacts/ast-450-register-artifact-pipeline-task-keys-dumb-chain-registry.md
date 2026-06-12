# AST-450 — Register artifact pipeline task keys (dumb chain registry)

**Linear:** [AST-450 — Register artifact pipeline task keys (dumb chain registry)](https://linear.app/astralcareermatch/issue/AST-450/register-artifact-pipeline-task-keys-dumb-chain-registry)  
**Feature ref:** `ftr/AST-450` (origin only)  
**Blocks:** [AST-313 — Artifact pipeline prompt authoring](https://linear.app/astralcareermatch/issue/AST-313/artifact-pipeline-prompt-authoring)

## Summary

Replace legacy Phase E `craft_job_*` task keys with nine registry keys Susan uses in **Manage Tasks** (`run_next` + chain tokens). The runtime stays **dumb**: `do_task` runs one `task_key`, then follows `agent_task.run_next` — **no** step lists, hop counts, or pipeline choreography in code. This ticket registers keys in `TASK_CONFIG`, seeds `agent_task` rows via `sync_agent_tasks`, and updates **dispatch entry points only** (`BUILD_ARTIFACTS`, `CANDIDATE_REVIEW`). Prompt text and `run_next` wiring remain Susan’s work in **AST-313**.

⚠️ **Decision:** The ticket’s narrative chain mentions `guide_resume_revisions` / `check_resume`; the authoritative **nine-key table** in the Linear description uses `advise_job_resume`, `check_job_resume`, etc. This plan implements **only the nine keys in that table**. Susan wires `run_next` in Admin after keys exist.

⚠️ **Decision:** No alias period for `craft_job_*` in `TASK_CONFIG` — remove legacy keys and update all references in one pass (grep-driven). Existing `agent_task` rows for old keys may remain in SQLite but are not valid `run_next` targets once removed from `TASK_CONFIG`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add nine `TASK_CONFIG` entries; remove `craft_job_resume`, `craft_job_cover_letter`, `craft_application_responses`; update `BUILD_CONFIG.resume_artifact_chain` / `cover_letter_artifact_chain` `first_task_key`. | utils |
| `src/core/consult.py` | `_INPUT_STATE_TO_TASK`: `BUILD_ARTIFACTS` → `contemplate_job`, `CANDIDATE_REVIEW` → `draft_cover_letter`; batch routing + `_prep_live_content` `scoring_task_key` strings; `_run_cover_letter_for_job` uses `draft_cover_letter` or `run_cover_letter_artifact_chain_for_job`. | core |
| `src/core/agent.py` | No chain logic changes; `run_resume_artifact_chain_for_job` / `run_cover_letter_artifact_chain_for_job` already read `BUILD_CONFIG` `first_task_key`. | core |
| `src/data/database.py` | `_DISPATCH_TASK_SEED`: replace `craft_job_resume` / `craft_job_cover_letter` rows with `contemplate_job` / `draft_cover_letter`. | data |
| `src/utils/config.py` (comment) | Short comment near Phase E block: cache tokens / `{$CACHE_BLOCK_B/C/D}` — no `--- CACHED CONTEXT ---` duplication (AST-303 Radia note); details for **AST-313**. | utils |

**Out of scope (do not touch):** `tests/`, `scripts/test_*.py`, `docs/ASTRAL_TEST_BIBLE.md` — Betty updates via **qa-astral** after **Code Complete**.

**Spike / investigation output:** none.

## Stage 1: `TASK_CONFIG` registry (nine keys)

**Done when:** `get_task_keys()` includes all nine keys below; none of `craft_job_resume`, `craft_job_cover_letter`, `craft_application_responses` remain in `TASK_CONFIG`; `python3 -m py_compile src/utils/config.py` passes.

1. In `src/utils/config.py`, **delete** the three `craft_job_*` entries under Phase E.
2. Add entries (phase `"E. Job Artifacts"`, `entity_type: "job"`, `requires_candidate_key: True`, `trigger_state: None` unless noted):

| `task_key` | `seq` | `response_schema` / notes |
|------------|-------|---------------------------|
| `contemplate_job` | 1 | Minimal stub: `astral_job_id`, `company`, `title` optional strings — dispatch entry; Susan authors prompts in **AST-313**. |
| `advise_job_resume` | 2 | Registry-only minimal stub (same minimal fields). |
| `draft_job_resume` | 3 | **Move** full schema from former `craft_job_resume`: `grades` list, twelve `vectors` names only, `grading_mode: "scored"`, `response_format: "json"`, `context_format: "grade_like_{index}"`. |
| `check_job_resume` | 4 | Registry-only minimal stub. |
| `finalize_job_resume` | 5 | Stub with fields aligned to `BUILD_CONFIG["artifact_shapes"]["resume_content"]` keys (`technical_skills`, etc. — copy exact keys from `artifact_shapes` on branch tip). |
| `draft_cover_letter` | 6 | **Move** full entry from former `craft_job_cover_letter` (`nocache_prompt`, `re_line` / `body` / `signature` schema). |
| `check_cover_letter` | 7 | Registry-only minimal stub. |
| `finalize_cover_letter` | 8 | Registry-only minimal stub (optional: mirror `artifact_shapes["cover_letter"]` field names as optional strings). |
| `propose_application_responses` | 9 | **Move** schema from former `craft_application_responses`. |

3. Add a 2–3 line comment above the Phase E block pointing prompt authors to **AST-313** for `{$CACHE_BLOCK_*}` usage (no duplicated cache headers per AST-303).

⚠️ **Decision:** `draft_job_resume` keeps scored vectors (not a blank stub) so existing consult/grade paths and **AST-428** vector-name-only config stay valid until Susan replaces prompts.

## Stage 2: `BUILD_CONFIG` entry keys only

**Done when:** `BUILD_CONFIG["resume_artifact_chain"]["first_task_key"] == "contemplate_job"` and `BUILD_CONFIG["cover_letter_artifact_chain"]["first_task_key"] == "draft_cover_letter"`.

1. In `src/utils/config.py` `BUILD_CONFIG`, set `resume_artifact_chain.first_task_key` to `"contemplate_job"`.
2. Set `cover_letter_artifact_chain.first_task_key` to `"draft_cover_letter"`.
3. Do **not** add arrays, step indices, or promotion logic.

## Stage 3: Dispatch routing (`consult.py` + `database.py`)

**Done when:** `run_consult_task(..., "BUILD_ARTIFACTS", ...)` routes to resume batch using `contemplate_job`; `run_consult_task(..., "CANDIDATE_REVIEW", ...)` routes to cover batch using `draft_cover_letter`; `_DISPATCH_TASK_SEED` matches.

1. In `src/core/consult.py` `_INPUT_STATE_TO_TASK`, set:
   - `"BUILD_ARTIFACTS": "contemplate_job"`
   - `"CANDIDATE_REVIEW": "draft_cover_letter"`
2. In `run_consult_task`, change `elif task_key == "craft_job_resume"` → `elif task_key == "contemplate_job"` (same body: `_run_craft_job_resume_batch` or rename function to `_run_build_artifacts_batch` — optional rename for clarity).
3. Change `elif task_key == "craft_job_cover_letter"` → `elif task_key == "draft_cover_letter"`.
4. In `_run_craft_job_resume_batch`, keep `run_resume_artifact_chain_for_job` (reads `BUILD_CONFIG` — no hardcoded first key).
5. In `_run_cover_letter_for_job` and `_run_craft_job_cover_letter_batch`, replace every `"craft_job_cover_letter"` string with `"draft_cover_letter"`; prefer `run_cover_letter_artifact_chain_for_job` in `_run_craft_job_cover_letter_batch` if it reduces duplication (same behavior as today).
6. In `src/data/database.py` `_DISPATCH_TASK_SEED`, replace:
   - `"craft_job_resume": {... trigger_state: BUILD_ARTIFACTS ...}` → `"contemplate_job": {...}`
   - `"craft_job_cover_letter": {... trigger_state: CANDIDATE_REVIEW ...}` → `"draft_cover_letter": {...}`
7. Grep `src/` for `craft_job_resume`, `craft_job_cover_letter`, `craft_application_responses` — update every hit (including `scoring_task_key=` and `do_task(` first args). **Do not** change `craft_joblist_rubric` / `craft_jobdesc_rubric`.

## Stage 4: Startup sync + admin validation

**Done when:** After app import, `sync_agent_tasks(get_task_keys())` inserts blank `agent_task` rows for new keys; saving `run_next` to any new key in Manage Tasks succeeds.

1. Confirm `src/ui/server.py` still calls `database.sync_agent_tasks(get_task_keys())` on startup (no code change unless missing).
2. Manually verify (document in build comment): `_validate_run_next` accepts edges between new keys because each target ∈ `TASK_CONFIG`.
3. **Do not** implement migration copying prompts from old `craft_*` rows to new keys — Susan re-authors in **AST-313**.

## Stage 5: Compile + publish

**Done when:** `python3 -m py_compile` on all changed `.py` files passes; branch published to `origin/ftr/AST-450`.

1. `python3 -m py_compile src/utils/config.py src/core/consult.py src/data/database.py` (add any other touched modules).
2. Commit on `dev-ada`: `feat(AST-450): register artifact pipeline task keys — registry and dispatch entries`.
3. Cherry-pick to `origin/ftr/AST-450` per **build-astral** §6.

## QA test manifest (Betty — post Code Complete)

1. `python3 -m py_compile src/utils/config.py src/core/consult.py src/data/database.py tests/component/utils/test_config.py tests/component/core/test_agent.py`
2. `pytest tests/component/utils/test_config.py -q -k "Ast450 or Ast309CoverLetter or test_resolves_writing_preferences_from_context or test_resolves_cover_letter_signature_from_profile"`
3. `pytest tests/component/core/test_consult.py -q -k "candidate_review_to_cover or Ast371Resume or Ast369CoverLetter"`
4. `pytest tests/component/core/test_agent.py -q` (key rename touches many `do_task` paths — full file quicker than brittle `-k`.)
5. Full gate before merge: `./scripts/testing/run_component_tests.sh` (`test-astral`).
## Execution contract (for the developer agent)

- **Forbidden:** `RESUME_PIPELINE_STEPS`, step-index constants, cache-promotion-at-step-N, ordered hop arrays, or any code that encodes chain length/order beyond `BUILD_CONFIG.first_task_key`.
- **Allowed:** Renaming dispatch batch helpers; grep-updating string literals; minimal `TASK_CONFIG` stubs.
- **Stop with 🛑** on Linear if Susan’s admin chain requires keys **not** in the nine-key table (e.g. `guide_resume_revisions`) without a Linear description update.

## Self-Assessment

### Scope

**scope-MAJOR-CHANGE** — Touches `TASK_CONFIG`, consult dispatch, dispatch DB seed, and grep-updates across `src/` (tests deferred to Betty).

### Conf

**conf-Medium** — Patterns exist (`run_next`, `BUILD_CONFIG` chains, `_DISPATCH_TASK_SEED`); exact stub shapes for five registry-only keys follow existing Phase E conventions.

### Risk

**risk-Medium** — Wrong dispatch entry key breaks `BUILD_ARTIFACTS` / `CANDIDATE_REVIEW` batches; mitigated by consult routing tests in Betty’s manifest.

## Self-review vs ASTRAL_CODE_RULES

- **§2.1** — All thresholds and chain entry keys in `config.py` / `BUILD_CONFIG`; no hardcoded pipeline steps.
- **§2.6** — No new job states; dispatch still state-driven via `dispatch_tasks` seed.
- **§3.3** — Consult imports agent helpers only; no new UI→database shortcuts.
- **§3.5** — New keys use `snake_case` per ticket table.

## Review

**Radia (`review-astral`).** Baseline **`origin/dev`**, feature **`origin/ftr/AST-450`**. Engineer tip reviewed: **`abfdd73aea2e31eeac278bc5a2de202e09f5580b`** (component gate restores LOCKED coverage + registry work below).

### Counts

- **fix-now:** 0
- **discuss:** 0
- **advisory:** 4

### What’s solid

- **Plan fidelity (`AST-450` scope):** All nine **`TASK_CONFIG`** keys are registered under Phase E with **`BUILD_CONFIG.resume_artifact_chain.first_task_key` → `contemplate_job`** and **`cover_letter_artifact_chain.first_task_key` → `draft_cover_letter`**; **`_INPUT_STATE_TO_TASK`** and **`_DISPATCH_TASK_SEED`** align (no orphaned legacy dispatch rows for the retired keys).
- **Dumb-chain constraint:** Diff shows **entry keys + `agent_task.run_next` only**—no pipeline step arrays or hop choreography added.
- **`draft_job_resume` / `draft_cover_letter` migration:** Former graded resume vectors and **`AST-309`** cover schema move cleanly; **`craft_job_resume` / `craft_job_cover_letter` / `craft_application_responses`** are absent from runtime **`src/*.py`** (remaining hits are **`_run_craft_*` helper names**, tests asserting legacy absent, and historical mentions in unrelated feature docs).
- **Consult routing improvement:** Replacing inlined **`do_task("craft_job_cover_letter")`** with **`run_cover_letter_artifact_chain_for_job`** keeps cover dispatch consistent with **`BUILD_CONFIG`** first-hop indirection (**`AST-300` / `AST-301`** pattern).
- **QA signal:** Expanded component coverage for consult agent/dispatch paths (`ASTRAL_TEST_BIBLE §7.13m` documents the matrix).

### Recommended actions

| Severity | Topic | Recommendation |
| --- | --- | --- |
| **Advisory** | Lazy imports (`consult.py`) | **`run_cover_letter_artifact_chain_for_job`** is imported inside **`_run_cover_letter_for_job`** / **`_run_craft_job_cover_letter_batch`** without a rationale comment—the same omission already existed for **`run_resume_artifact_chain_for_job`**. Prefer a one-line **`# consult ↔ agent` cycle-break** note on **all three** lazies during **`resolve-astral`** if Susan wants parity with **`ASTRAL_CODE_RULES` §1 import** scrutiny. |
| **Advisory** | **`finalize_job_resume` stub strictness** | **`TASK_CONFIG`** uses optional fields while **`BUILD_CONFIG["artifact_shapes"]["resume_content"]`** marks several keys **`required: True`**—expected for pre-prompt stubs, but converge when **`AST-313`** lands so authors do not perceive conflicting contracts. |
| **Advisory** | Dispatcher tick test (**`test_dispatcher.py`**) | PEP 479 **`StopIteration` → RuntimeError** guard fix is orthogonal to **`AST-450`** but low-risk; keep as a housekeeping note when summarizing blast radius to Susan. |
| **Advisory** | Historical sibling docs (`ast-309`, `ast-369`, **`ast-371`**, **`ast-428`**) | Still cite **`craft_job_*`** naming in narrative tables—informational backlog for doc gardeners; runtime is already migrated. |

### Engineer implementation note (Ada — Code Complete)

- **Branch:** `ftr/AST-450` on `origin`; validation against **`TASK_CONFIG`** / **`sync_agent_tasks`** paths matches the **`AST-313`** unblock goal.
- Detail SHAs preceding Radia doc commit remain on **`origin/ftr/AST-450`** engineering history (`abfdd73a` cited above).

_Radia doc amend SHA: appears in git tip after **`docs(AST-450): Radia review — …`** push._

## Resolution

**2026-05-23 — Review Posted → User Testing (Ada)**

- **fix-now:** 0 — no additional product changes; engineering tip **`abfdd73a`** per Radia review stands.
- **discuss:** none.
- **advisory:** noted for backlog — lazy-import rationale parity on consult ↔ agent helpers; **`finalize_job_resume`** stub vs **`artifact_shapes["resume_content"]`** **`required`** flags to converge when **AST-313** prompts land; PEP 479 guard in **`test_dispatcher.py`** as orthogonal housekeeping; historical feature docs still naming **`craft_job_*`** until doc gardeners sweep.
- **Plan doc:** Radia sign-off **`docs(AST-450): Radia review — artifact registry dumb-chain sign-off`** merged from **`origin/ftr/AST-450`** (`57681373`); this **Resolution** section records close-out vs that thread.
