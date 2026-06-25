<!-- linear-archive: AST-520 archived 2026-06-15 -->

## Linear archive (AST-520)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-520/register-anticipate-scan-task-key-insert-task-anticipate-scan-in-the  
**Status at archive:** Done  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-516 — Insert task "anticipate_scan" in the daisy chain  
**Blocked by / blocks / related:** parent: AST-516

### Description

## What this implements

Add `anticipate_scan` as a tenth Phase E artifact-pipeline task key using the same dumb-chain registry pattern as **AST-450**. The key must appear in the authoritative task registry, sync a blank `agent_task` row on startup, and remain a non-dispatch hop ( `BUILD_ARTIFACTS` still enters at `contemplate_job` only). Susan wires `contemplate_job` **→** `anticipate_scan` **→** `advise_job_resume` via `run_next` in Manage Tasks; code must not encode chain order.

## Acceptance criteria

1. `anticipate_scan` appears as a configured task key in Manage Tasks and in the authoritative task-key registry.
2. App startup sync creates a current `agent_task` row for `anticipate_scan` (blank until Susan authors prompts).
3. With Susan’s `run_next` wiring (`contemplate_job` **→** `anticipate_scan` **→** `advise_job_resume`), a full resume artifact chain run executes all three hops in order for a single job.
4. `advise_job_resume` receives `anticipate_scan` output through `{$CALLER_RESPONSE}` (or equivalent chain token Susan wires), not stale output from `contemplate_job` alone.
5. `BUILD_ARTIFACTS` dispatch still enters at `contemplate_job` only.
6. Susan can assign the Atlas agent and save all prompt segments for `anticipate_scan` in Manage Tasks without code changes.
7. Manage Tasks preview for `anticipate_scan` with a selected job entity resolves job-scoped tokens (`{$VISIBLE_JD}`, `{$ANALYSIS_*}`, etc.) the same way `contemplate_job` preview does after **AST-513** lands.
8. For a job in the **ready** state, opening it in the **Recommended** Job Analysis Report modal shows the `anticipate_scan` agent response in the same agent-response section pattern as other artifact pipeline hops.

## Boundaries

* Does **not** author Atlas prompt prose — Susan’s **AST-313** work.
* Does **not** change cover letter chain, dispatch seeds, or hardcoded pipeline step lists.
* Does **not** persist Atlas output to dedicated `job_data` fields.
* Does **not** modify `consult.py` dispatch routing unless a grep shows a required string-literal update (unlikely for a non-entry key).

## Notes for planning

* Follow **AST-450** / `docs/features/artifacts/ast-450-register-artifact-pipeline-task-keys-dumb-chain-registry.md`: minimal `TASK_CONFIG` stub between `contemplate_job` and `advise_job_resume` `seq` values; registry-only response schema.
* `print_label` (or equivalent) if Job Analysis Report labels hops via `TASK_CONFIG` — verify acceptance **#8** without UI code if possible.
* Betty owns `docs/ASTRAL_TEST_BIBLE.md` and test updates after **Code Complete**.

## Git branch (authoritative)

Per `orientation-astral` **§ Branch law**`**: parent **`**ftr/AST-516-insert-task-anticipate_scan-in-the-daisy-chain**`**, child **`**sub/AST-516/<child-segment>**`**. Created at **dispatch-linear**. Engineers cherry-pick to **`**origin/<sub-ref>**`** — never Linear **`**gitBranchName\`** when it disagrees.

### Comments

#### radia — 2026-05-28T23:19:20.461Z
**Review** — `git diff origin/dev...origin/sub/AST-516/AST-520-register-anticipate_scan-task-key` @ `d4911f11` (8 files, +282/−14).

### Plan fidelity
- **Registry (AC #1–2, #5):** `anticipate_scan` inserted between `contemplate_job` and `advise_job_resume` with registry-only stub (`trigger_state: None`, minimal `response_schema`); Phase E `seq` renumbered 1→10; `BUILD_CONFIG["resume_artifact_chain"]["first_task_key"]` still `contemplate_job`; `anticipate_scan` absent from `_DISPATCH_TASK_TRIGGER_SEED` and `database._DISPATCH_TASK_SEED` — grep confirms only `config.py` product reference.
- **Report UI (AC #8):** `get_entity_agent_story` adds `phase` + `label` from `TASK_CONFIG`; `JobAnalysisReportModal` filters `phase === "E. Job Artifacts"` and renders dynamic `CollapsiblePanel` + `AgentStoryTab` (no hardcoded hop list). `/api/jobs/:id` already attaches `agent_story` via `get_entity_agent_story` — enrichment flows without API change.
- **Self-assessment:** `scope-Single-Component` / `conf-high` / `risk-low` still match the diff footprint (config + small roster + one modal).

### ASTRAL_CODE_RULES
- **§2.1 / §2.6:** Config-driven task key; no pipeline step arrays; dispatch entry unchanged (`consult.py` `BUILD_ARTIFACTS` → `contemplate_job` only).
- **§3.3 (B2):** Core reads `TASK_CONFIG` in roster; UI consumes JSON only — no `src.data` / `src.external` in the TSX change.
- **§3.5:** Key name `anticipate_scan`; `print_label` "Anticipate Scan" on the new entry only (per plan).

### Rubric (5a)
- No new silent failure, `print()`, or layer violations in the diff.
- **G1 note:** `PHASE_E_ARTIFACTS = "E. Job Artifacts"` in the modal mirrors `TASK_CONFIG` phase text (not job-state literals) — acceptable per plan Stage 3.

### Tests / bible
- Betty manifest paths covered: `TestAst520AnticipateScanTaskKey`, roster label test, modal Phase E panel test; `ASTRAL_TEST_BIBLE.md` §7.13m updated for ten keys — aligned with publish ref.

### Advisory (Susan / UAT — not code gaps)
- **AC #3–4, #6–7:** Chain order, `{$CALLER_RESPONSE}` wiring, Atlas prompts, and Manage Tasks preview tokens depend on Susan `run_next` + **AST-313** / **AST-513** — verify in UAT after wiring.
- Other Phase E hops in the report modal use raw `task_key` as panel title until `print_label` is added elsewhere (plan decision).

### fix-now
None.

### discuss
None.

**Handoff:** Ada may run `resolve-astral` when ready (no blockers from this review).

#### ada — 2026-05-28T23:17:52.137Z
[check-linear]

**Inbox (parent AST-516 / Astral Artifacts, assigned AST-520):**

- **§0a:** `dev-ada` @ `/Users/susan/chuckles/astral-ada`; merged `origin/dev` — **merge-clean** (`BEHIND=0`, `origin/dev` ancestor of `HEAD`).
- **§0b:** `@ada` issue search (team + **Astral Artifacts** project); union with assignee-me in project. Full threads on **AST-520**, parent **AST-516**, sibling **AST-513**, and other @ada / assignee hits in session project.
- **0** actionable comments — nothing `@ada` or directed at Ada needing reply or small fix after Ada’s plan doc comment (`fe6718eb`).

**AST-520:** **Tests Passed**, assignee Ada — Betty QA manifest on publish ref `origin/sub/AST-516/AST-520-register-anticipate_scan-task-key` @ `d4911f11`; no `@ada` thread work. Next gate is **`resolve-astral`** when Radia posts review (not invoked from this pass).

**Session scope:** Happy path — no `plan-astral` / `build-astral` / `test-astral` / `resolve-astral` from check-linear.

#### betty — 2026-05-28T23:13:15.597Z
## QA test manifest

**Publish ref:** `origin/sub/AST-516/AST-520-register-anticipate_scan-task-key` @ `d4911f11`

**`docs/ASTRAL_TEST_BIBLE.md` shasum (publish ref):** `80487d37115882eccdca297699334393a25607c9` — see §7.13m (AST-450 + AST-520).

Run on **`dev-ada`** after `git fetch origin` and `git merge origin/sub/AST-516/AST-520-register-anticipate_scan-task-key`:

1. `./scripts/testing/run_component_tests.sh tests/component/utils/test_config.py::TestAst450ArtifactPipelineTaskKeys tests/component/utils/test_config.py::TestAst520AnticipateScanTaskKey`
2. `./scripts/testing/run_component_tests.sh tests/component/core/test_roster.py::TestEntityAgentStory::test_ast520_agent_story_phase_and_print_label`
3. `cd src/ui/frontend && npx vitest run ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx`

**Coverage intent:**
- **#1–2:** tenth Phase E key `anticipate_scan` in `TASK_CONFIG` (seq renumber, no dispatch seed); `BUILD_ARTIFACTS` still enters at `contemplate_job`; legacy `craft_job_*` absent.
- **#2:** `get_entity_agent_story` attaches `phase` + `print_label` display (`Anticipate Scan`).
- **#3:** Recommended Job Analysis Report renders Phase E `agent_story` panels dynamically (not hardcoded hop list); non–Phase E entries filtered out.

**Susan manual (not in manifest):** wire `contemplate_job` → `anticipate_scan` → `advise_job_resume` in Manage Tasks; chain run AC **#3–4**, **#6–7** after wiring + **AST-313** prompts.

— Betty

#### ada — 2026-05-28T23:07:58.572Z
Plan doc: [ast-520-register-anticipate-scan-task-key-insert-task-anticipate-scan-in-the-daisy-chain.md](https://github.com/susansomerset/astral/blob/sub/AST-516/AST-520-register-anticipate_scan-task-key/docs/features/artifacts/ast-520-register-anticipate-scan-task-key-insert-task-anticipate-scan-in-the-daisy-chain.md)

**Scope:** `scope-Single-Component` — one new `TASK_CONFIG` entry + Phase E `seq` renumber; small `get_entity_agent_story` metadata and Job Analysis Report Phase E panels for acceptance #8.

**Conf:** `conf-high` — direct extension of **AST-450** dumb-chain registry; chain execution and tokens already shipped (**AST-303**, **AST-304**, **AST-513**).

**Risk:** `risk-low` — non-dispatch hop; `seq` affects Manage Tasks sort only, not runtime chain order.

Publish SHA: `fe6718eb` on `origin/sub/AST-516/AST-520-register-anticipate_scan-task-key`.

---

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
