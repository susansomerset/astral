# AST-520 — Register `anticipate_scan` task key

**Linear:** [AST-520 — Register anticipate_scan task key](https://linear.app/astralcareermatch/issue/AST-520/register-anticipate-scan-task-key-insert-task-anticipate-scan-in-the-daisy-chain)  
**Parent:** [AST-516 — Insert task "anticipate_scan" in the daisy chain](https://linear.app/astralcareermatch/issue/AST-516/insert-task-anticipate-scan-in-the-daisy-chain)  
**Publish ref:** `sub/AST-516/AST-520-register-anticipate_scan-task-key` (origin only)

## Summary

Register `anticipate_scan` as the **tenth** Phase E artifact-pipeline task key using the same dumb-chain registry pattern as **AST-450**. The key must appear in `TASK_CONFIG`, sync a blank `agent_task` row on startup, and remain a **non-dispatch** hop (`BUILD_ARTIFACTS` still enters at `contemplate_job` only). Chain order (`contemplate_job` → `anticipate_scan` → `advise_job_resume`) is Susan’s **`run_next`** wiring in Manage Tasks — not encoded in product code. Prompt prose, Atlas assignment, and cache layout are **AST-313** (Susan); job-scoped token resolution depends on **AST-513** landing on `dev`.

⚠️ **Decision:** Insert `anticipate_scan` **between** `contemplate_job` and `advise_job_resume` in `TASK_CONFIG` and bump **`seq`** on every later Phase E key by **+1** (Manage Tasks sort only — not chain order). Do **not** add a fractional `seq`.

⚠️ **Decision:** Acceptance **#8** (Job Analysis Report modal) cannot pass with registry-only work today — `JobAnalysisReportModal.tsx` does not render `agent_story`. Stage 3 adds a **dynamic** Phase E agent-response section (no hardcoded hop list) so `anticipate_scan` appears when present in `job.agent_responses`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `anticipate_scan` `TASK_CONFIG` stub; renumber Phase E `seq` 2→10; optional `print_label` on new key only. | utils |
| `src/core/roster.py` | In `get_entity_agent_story`, attach `phase` and display `label` (`print_label` or `task_key`) on each enriched entry for UI filtering. | core |
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | Render CollapsiblePanel + `AgentStoryTab` for Phase E `agent_story` entries (dynamic by response data, not task-key list). | ui |

**Out of scope (do not touch):** `src/core/consult.py` dispatch routing (grep must stay clean); `_DISPATCH_TASK_SEED` / `BUILD_CONFIG.first_task_key`; cover-letter chain keys; `tests/`, `docs/ASTRAL_TEST_BIBLE.md` — Betty updates after **Code Complete**.

**Spike / investigation output:** none.

## Stage 1: `TASK_CONFIG` registry (tenth Phase E key)

**Done when:** `get_task_keys()` includes `anticipate_scan`; `contemplate_job` remains the only Phase E key with a dispatch `trigger_state`; `python3 -m py_compile src/utils/config.py` passes.

1. In `src/utils/config.py`, **after** the `contemplate_job` block and **before** `advise_job_resume`, add:

```python
"anticipate_scan": {
    "phase": "E. Job Artifacts",
    "seq": 2,
    "print_label": "Anticipate Scan",
    "response_schema": {
        "astral_job_id": {"type": "str", "required": False},
        "company": {"type": "str", "required": False},
        "title": {"type": "str", "required": False},
    },
    "entity_type": "job",
    "requires_candidate_key": True,
    "trigger_state": None,
},
```

2. Renumber **`seq`** on existing Phase E keys (values only — do not reorder dict keys beyond inserting the new block):

| `task_key` | new `seq` |
|------------|-----------|
| `contemplate_job` | 1 (unchanged) |
| `anticipate_scan` | 2 (new) |
| `advise_job_resume` | 3 |
| `draft_job_resume` | 4 |
| `check_job_resume` | 5 |
| `finalize_job_resume` | 6 |
| `draft_cover_letter` | 7 |
| `check_cover_letter` | 8 |
| `finalize_cover_letter` | 9 |
| `propose_application_responses` | 10 |

3. Do **not** add `anticipate_scan` to `_DISPATCH_TASK_TRIGGER_SEED`, `database._DISPATCH_TASK_SEED`, or `_INPUT_STATE_TO_TASK` in `consult.py`.

4. Leave `BUILD_CONFIG["resume_artifact_chain"]["first_task_key"]` as `"contemplate_job"`.

⚠️ **Decision:** Registry-only minimal stub (same three optional strings as `contemplate_job` / `advise_job_resume`) — Susan authors Atlas JSON shape in Manage Tasks under **AST-313**.

## Stage 2: Startup sync + dispatch grep gate

**Done when:** Fresh app import calls `sync_agent_tasks(get_task_keys())` and inserts a blank current `agent_task` row for `anticipate_scan`; grep shows no erroneous dispatch wiring.

1. Confirm `src/ui/server.py` still calls `database.sync_agent_tasks(get_task_keys())` on startup (no change unless missing).
2. Run grep from repo root:

```bash
rg 'anticipate_scan' src/
rg 'craft_job_' src/
```

Expected: only `config.py` hits for `anticipate_scan` after Stage 1. If `consult.py` or `database.py` require a string-literal update, **stop** and comment on **AST-520** with grep output — do not improvise dispatch rows.

3. Confirm `_validate_run_next` in admin API accepts `run_next` targets that exist in `TASK_CONFIG` (no code change — `anticipate_scan` is a valid target once registered).

**Susan manual (not build steps):** wire `contemplate_job.run_next` → `anticipate_scan` → `advise_job_resume` in Manage Tasks; assign Atlas agent and prompts (**AST-313**). Acceptance **#3**, **#4**, **#6** verify only after Susan’s wiring + a chain run.

## Stage 3: Job Analysis Report — Phase E agent responses (acceptance #8)

**Done when:** For a **RECOMMENDED** (or other `RECOMMENDED_JOB_STATES`) job whose `agent_responses` includes an `anticipate_scan` hop, opening **Recommended → Job Analysis Report** shows that hop in a collapsible agent-response panel labeled **Anticipate Scan** (or `print_label`), using the same `AgentStoryTab` content pattern as `JobDetailModal`.

1. In `src/core/roster.py` `get_entity_agent_story`, after `task_cfg = TASK_CONFIG.get(task_key, {})`, add to each enriched entry:
   - `"phase": task_cfg.get("phase")`
   - `"label": (task_cfg.get("print_label") or task_key).strip()`

2. In `src/ui/frontend/src/components/JobAnalysisReportModal.tsx`:
   - Extend `JobDetail` interface with `agent_story?: AgentStoryEntry[]` (import type from `./AgentStoryTab`).
   - After the analysis upshot block and before the JD block, render one `CollapsiblePanel` per `agent_story` entry where `entry.phase === "E. Job Artifacts"`, panel title = `entry.label`, body = `<AgentStoryTab entry={entry} />`.
   - Do **not** hardcode a list of Phase E task keys — filter on `phase` from the API only.
   - If no Phase E entries, render nothing (no placeholder).

3. Manual verify (document in build Linear comment): job with stored `anticipate_scan` response → open Recommended report → panel visible with response content.

⚠️ **Decision:** `print_label` lives only on `anticipate_scan` for now; other Phase E keys fall back to raw `task_key` in the panel title until Susan adds labels elsewhere.

## Stage 4: Compile + publish

**Done when:** `python3 -m py_compile` on touched `.py` files passes; frontend typecheck if the repo gate requires it for TSX; branch published to `origin/sub/AST-516/AST-520-register-anticipate_scan-task-key`.

1. `python3 -m py_compile src/utils/config.py src/core/roster.py`
2. From `src/ui/frontend`, run `npm run build` or project-standard TS check if that is the local gate before commit (match **build-astral** habit).
3. Commit on `dev-ada`: `feat(AST-520): register anticipate_scan task key — registry and report UI`.
4. Cherry-pick to publish ref per **build-astral** §6.

## QA test manifest (Betty — post Code Complete)

1. `python3 -m py_compile src/utils/config.py src/core/roster.py`
2. Extend `TestAst450ArtifactPipelineTaskKeys.KEYS` to **ten** keys including `anticipate_scan` (between `contemplate_job` and `advise_job_resume`); keep legacy `craft_job_*` absent assertions.
3. Component test: `anticipate_scan` ∉ `_DISPATCH_TASK_TRIGGER_SEED` keys / dispatch seed mirror (if covered).
4. Frontend: Job Analysis Report renders Phase E `agent_story` panel when fixture includes `phase: "E. Job Artifacts"` (new or extended test alongside `JobAnalysisReportModal` tests).
5. Full gate: `./scripts/testing/run_component_tests.sh` per **test-astral**.

## Execution contract (for the developer agent)

- **Forbidden:** `RESUME_PIPELINE_STEPS`, ordered hop arrays, dispatch seed for `anticipate_scan`, changing `BUILD_ARTIFACTS` entry key, hardcoded chain order in code, editing Susan’s `run_next` in DB from product code.
- **Allowed:** `TASK_CONFIG` stub + `seq` renumber; minimal `get_entity_agent_story` metadata; dynamic Phase E panels in Job Analysis Report.
- **Stop with 🛑** on **AST-520** if grep shows dispatch wiring is required and the plan’s “no dispatch” decision is wrong, or if `JobAnalysisReportModal` product spec conflicts with CollapsiblePanel placement (quote conflicting acceptance text).

## Self-Assessment

### Scope

**scope-Single-Component** — Primary change is one new `TASK_CONFIG` entry plus `seq` renumber in `config.py`; small roster enrichment and one modal component for acceptance #8.

### Conf

**conf-high** — Mirrors **AST-450** registry pattern exactly; chain execution and tokens already exist (**AST-303**, **AST-304**, **AST-513**).

### Risk

**risk-low** — Wrong dispatch attachment would break `BUILD_ARTIFACTS` entry, but plan forbids it; `seq` renumber affects Manage Tasks sort only, not runtime chain order.

## Self-review vs ASTRAL_CODE_RULES

- **§2.1** — Task key and stub schema in `TASK_CONFIG`; no hardcoded pipeline step lists; dispatch entry unchanged.
- **§2.6** — No new job states; chain remains `run_next`-driven.
- **§3.3** — Roster enrichment stays core→data; UI consumes API JSON only.
- **§3.5** — Key name `anticipate_scan` matches ticket; optional `print_label` for display.

## Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-516/AST-520-register-anticipate_scan-task-key`  
**Product commit:** `decbdae4` — `TASK_CONFIG` tenth Phase E key + `seq` renumber; `get_entity_agent_story` `phase`/`label`; Job Analysis Report Phase E `CollapsiblePanel` + `AgentStoryTab`

## Resolution

**Resolved:** 2026-05-28 (Ada)

| Radia item | Action |
|------------|--------|
| **fix-now** | None — plan fidelity and ASTRAL_CODE_RULES sign-off on `origin/sub/AST-516/AST-520-register-anticipate_scan-task-key` @ `d4911f11` (Radia review 2026-05-28). |
| **discuss** | None. |
| **advisory** — AC #3–4, #6–7 Susan wiring + **AST-313** / **AST-513** | Deferred to parent UAT; chain order and tokens are Manage Tasks / prompt work, not code gaps. |
| **advisory** — other Phase E panel titles use raw `task_key` | Per plan Stage 3; `print_label` only on `anticipate_scan` until Susan adds labels elsewhere. |

**Publish ref:** `origin/sub/AST-516/AST-520-register-anticipate_scan-task-key` · Betty manifest green · §9a clean (dev + parent ftr).
