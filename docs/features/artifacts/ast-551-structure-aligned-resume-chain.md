# AST-551 — Structure-aligned resume chain after AST-477 (Build Resume Artifact)

**Linear:** [AST-551](https://linear.app/astralcareermatch/issue/AST-551/structure-aligned-resume-chain-after-ast-477-build-resume-artifact)  
**Parent:** [AST-300](https://linear.app/astralcareermatch/issue/AST-300/build-resume-artifact)  
**Publish ref:** `sub/AST-300/AST-551-structure-aligned-resume-chain` (origin only)  
**Parent integration ref:** `ftr/AST-300-build-resume-artifact`

Align the Phase E resume **`do_task`** daisy-chain with the post-**AST-477** per-candidate section catalog: hops consume and produce JSON keyed to **enabled section ids** from `artifacts.resume_structure`, pass revised text hop-to-hop via **`run_next`** / **`{$CALLER_*}`** tokens (**AST-450** / **AST-370**), and read the candidate base resume via **`{$BASE_RESUME}`** (and job tokens) — not code-orchestrated cache promotion or a global **`BUILD_CONFIG.artifact_shapes.resume_content`** required-key gate. The terminal hop (**`finalize_job_resume`** per Manage Tasks **`run_next`**) must emit structure-keyed prose the tracker can persist through **`save_job_artifact_resume_content`** (**AST-518** filtering + contact snapshot).

**Out of scope (sibling tickets):** **AST-552** (Hedy) — BUILD_ARTIFACTS dispatch row, job state **BUILD_ARTIFACTS** → **CANDIDATE_REVIEW** / **BUILD_FAILED**, and batch orchestration around failed runs. **Katherine** — Job Analysis Report resume draft tabs. **AST-313** (Done) — Manage Tasks prompt prose and **`run_next`** wiring (Susan); this plan registers tokens and code hooks prompts may use, but does not edit **`agent_task`** rows.

**Dependency note:** Linear **`blockedBy`** **AST-552**. This ticket can land chain + persist-handoff code first; full acceptance criteria 2–4 need **AST-552** on the integration branch for dispatch gate and failure transitions. If **AST-552** is not merged when **build-astral** runs integration tests, stop at stage boundaries and comment on **AST-551** with the blocking issue id.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/tracker.py` | Structure-aware resume persist match; extract flat section dict from terminal parsed JSON; keep **`_prepare_job_resume_content`** / **`save_job_artifact_resume_content`** as the only write path. | core |
| `src/core/agent.py` | **`run_resume_artifact_chain_for_job`**: load **`candidate_data`** + **`astral_candidate_id`** into **`ctx`**; restrict terminal **`persist_job_artifact_from_parsed`** to resume terminal task key(s). | core |
| `src/core/consult.py` | Extend **`build_job_token_context`** with **`RESUME_SECTION_CATALOG`** (enabled section ids + titles for active candidate). | core |
| `src/utils/config.py` | Register **`RESUME_SECTION_CATALOG`** in **`TOKEN_SOURCES`** (`source: job`); comment **`artifact_shapes.resume_content`** as documentation catalog only. | utils |
| `tests/component/core/test_tracker.py` | Tests for structure-keyed persist match (subset catalog, no global required-key gate). | tests |
| `tests/component/core/test_agent.py` | Test chain entry seeds **`candidate_data`** so **`{$BASE_RESUME}`** resolves. | tests |

**Not in this ticket:** `src/core/dispatcher.py`, `src/core/consult.py` batch state transitions (**AST-552**), UI routes, new ordered pipeline arrays in config.

---

## Stage 1: Structure-aware terminal persist handoff

**Done when:** A terminal-hop parsed dict containing only a **subset** of one candidate's enabled section ids (e.g. three sections enabled, three keys in JSON) persists to **`job_data.artifacts.resume_content`** via **`save_job_artifact_resume_content`**; orphans are stripped; contact sections snapshot per **AST-518**; the legacy **`parsed_matches_artifact_shape(..., "resume_content")`** global required-key gate is not used for chain terminal writes.

1. In **`src/core/tracker.py`**, add **`_resume_payload_body(parsed: Any) -> dict`** that returns a flat `dict[str, str]`:
   - If **`parsed`** has **`agent_payload`** dict, use that dict; else use **`parsed`** when it is a dict.
   - Keep only keys whose values are strings (strip non-strings).
   - Do not require metadata keys (`astral_job_id`, `company`, `title`, `grades`, etc.) to be absent — **`filter_content_to_resume_structure`** already drops them.

2. Add **`parsed_matches_resume_content_shape(parsed: Any, candidate_data: dict) -> bool`**:
   - Resolve structure via **`candidate_mod.resolve_resume_structure(candidate_data)`**.
   - **`enabled = set(candidate_mod.enabled_resume_section_ids(structure))`**; if empty, return **`False`**.
   - **`body = _resume_payload_body(parsed)`**.
   - Return **`True`** iff **at least one** `sid` in **`enabled`** has **`body.get(sid)`** a non-empty stripped string.
   - ⚠️ **Decision:** Do **not** require every **`BUILD_CONFIG["artifact_shapes"]["resume_content"]`** required field — that catalog is pre-**AST-477** and breaks per-candidate subsets (**AST-477** AC3).

3. Update **`persist_job_artifact_from_parsed(astral_job_id, parsed)`**:
   - Load **`cd = _candidate_data_for_job(astral_job_id)`**.
   - If **`parsed_matches_resume_content_shape(parsed, cd)`**: call **`save_job_artifact_resume_content(astral_job_id, _resume_payload_body(parsed))`**; set **`wrote = True`**.
   - Leave cover-letter branch unchanged (**`parsed_matches_artifact_shape(..., "cover_letter")`**).
   - Remove or bypass the resume branch that used **`parsed_matches_artifact_shape(parsed, "resume_content")`** + **`slice_parsed_for_artifact_shape`** (global shape keys only).

4. In **`tests/component/core/test_tracker.py`**:
   - Add **`test_parsed_matches_resume_content_subset_of_enabled_catalog`**: candidate with only **`professional_summary`** and **`experience`** enabled; payload with those two keys only → match **`True`**.
   - Add **`test_persist_resume_content_without_global_required_keys`**: same setup; **`persist_job_artifact_from_parsed`** writes filtered **`resume_content`** (monkeypatch **`save_job_data`** / **`_candidate_data_for_job`**).
   - Add **`test_parsed_matches_resume_content_false_when_no_enabled_body`**: enabled contact-only or empty strings → **`False`**.

5. Run **`python3 -m py_compile`** on touched modules.

---

## Stage 2: Chain entry — candidate context and base resume tokens

**Done when:** **`run_resume_artifact_chain_for_job`** always passes **`candidate_data`** (and **`astral_candidate_id`** when known) into **`do_task`** **`ctx`** so chain-entry hops resolve **`{$BASE_RESUME}`** as JSON of **`artifacts.base_resume`** (filtered keys only in DB; token emits full dict JSON per **`value_to_str`**) and **`{$VISIBLE_JD}`** / analysis tokens via existing **`build_job_token_context`**.

1. In **`src/core/agent.py`**, inside **`run_resume_artifact_chain_for_job`**, after **`job`** is resolved:
   - **`cd = tracker._candidate_data_for_job(astral_job_id)`** (or equivalent without new **`get_*`** if a thin helper already exists on tracker).
   - If **`cd`** is empty and the job row has a resolvable candidate, **stop** with return dict **`success: False`**, **`error`** explaining missing candidate data (do not run chain blind).
   - Set **`task_ctx["candidate_data"] = cd`**.
   - If **`company`** on job yields **`candidate_id`**, set **`task_ctx["astral_candidate_id"] = str(candidate_id)`** (same pattern as other job-scoped tasks).

2. Confirm **`do_task`** already calls **`_job_context_for_call(ctx, index, cd)`** when **`cd`** is present — no change unless **`ctx`** omits **`job`**; keep **`task_ctx["job"] = job`**.

3. ⚠️ **Decision:** No code path replaces or “promotes” a cache slot for base resume. Revised resume text for later hops must come from prior hop **`{$CALLER_RESPONSE}`** / **`{$CALLER_CACHE_*}`** per **AST-370** — do not add promotion helpers in **`agent.py`**.

4. In **`tests/component/core/test_agent.py`**, add **`test_run_resume_artifact_chain_seeds_candidate_data`** (async test with monkeypatched **`do_task`** / **`tracker.get_job`**): assert **`ctx["candidate_data"]`** is non-empty when job has candidate.

5. Run **`python3 -m py_compile`** on touched modules.

---

## Stage 3: Terminal-hop persist guard + section catalog token

**Done when:** Only the resume **terminal** craft hop triggers structure-aware persist (not intermediate hops that happen to return section-shaped JSON); Manage Tasks authors can reference **`{$RESUME_SECTION_CATALOG}`** listing enabled section ids and titles for the active candidate.

1. In **`src/core/agent.py`**, in the **`do_task`** block where **`not effective_next`** and terminal success call **`persist_job_artifact_from_parsed`** (lazy import):
   - Before calling persist for **`entity_type == "job"`**, require **`task_key == "finalize_job_resume"`** for resume-content persist.
   - If the terminal hop is **`finalize_job_resume`** and persist returns **`False`** but **`parsed_matches_resume_content_shape`** would be **`False`**, treat as normal (no write); if shape matches but persist fails, log warning (existing patterns).
   - ⚠️ **Decision:** Terminal task key name is **`finalize_job_resume`** as registered in **`TASK_CONFIG`**; Susan may rename hops in Manage Tasks, but **`run_next`** must still end on that key for persist to fire. If DB **`run_next`** ends on a different key, **stop** and comment on **AST-551** — do not guess alternate keys.

2. In **`src/core/consult.py`**, extend **`build_job_token_context(job, candidate_data)`**:
   - Import **`resolve_resume_structure`** and **`enabled_resume_structure_sections`** from **`src.core.candidate`** (lazy import if needed for cycle safety).
   - Set **`out["RESUME_SECTION_CATALOG"]`** to newline-separated lines: **`{id}: {title} (job_agent_editable={true|false})`** for each enabled section in catalog order.

3. In **`src/utils/config.py`**:
   - Register **`"RESUME_SECTION_CATALOG": {"source": "job"}`** in **`TOKEN_SOURCES`** (same pattern as **`VISIBLE_JD`** / **AST-513**).
   - Add one-line comment on **`BUILD_CONFIG["artifact_shapes"]["resume_content"]`**: documents known ids; runtime allowed keys are per-candidate structure subset (**AST-477** / **AST-518**).

4. Do **not** add **`RESUME_PIPELINE_STEPS`** or any ordered hop list to config (**AST-450**).

5. Extend **`tests/component/utils/test_config.py`** or consult tests: **`build_job_token_context`** includes non-empty **`RESUME_SECTION_CATALOG`** for a fixture candidate with default structure.

6. Run **`python3 -m py_compile`**; run targeted tests:
   - **`python3 -m pytest tests/component/core/test_tracker.py::TestPersistJobArtifactFromParsed tests/component/core/test_tracker.py::TestAst518JobResumeArtifacts -q`**
   - **`python3 -m pytest tests/component/core/test_agent.py -k resume_artifact -q`** (or the new test name).

---

## Stage 4: Verify chain contract (no dispatch/state)

**Done when:** Component tests green; manual harness note posted if **AST-552** not merged (optional).

1. Grep **`src/core/agent.py`** for **`artifact_shapes`** / **`promot`** in resume chain paths — confirm no new promotion or global-shape persist gate remains.

2. Document in a **AST-551** Linear comment (after build, not plan): Susan should confirm Manage Tasks resume chain ends at **`finalize_job_resume`** and that early-hop prompts reference **`{$BASE_RESUME}`** and mid-hop **`{$CALLER_RESPONSE}`** — code-only verification cannot assert DB **`run_next`** graph.

3. Full E2E (BUILD_ARTIFACTS job → chain → **`resume_content`** on job → no false **CANDIDATE_REVIEW** on failure) is validated with **AST-552** + parent UAT — not required to pass in **AST-551**-only pytest scope.

---

## Execution contract (for the developer agent)

- Execute stages in order; one commit per stage on **`dev-ada`**, then **`git-store-code-commit`** (or plan commit only for stage 0 — this doc is plan-only; build uses code store).
- Do not edit **`dispatch_tasks`** rows, **`consult.py`** BUILD_ARTIFACTS transitions, or frontend report UI.
- Do not add ordered pipeline arrays to **`BUILD_CONFIG`**.
- If Manage Tasks terminal key ≠ **`finalize_job_resume`**, or **`run_next`** graph is missing from DB, **stop** and comment on **AST-551** with 🛑 format from **plan-astral**.
- If **AST-552** is required for a stage's "Done when" and is not on **`dev-ada`** after merge steps, **stop** at that stage boundary.

---

## Self-Assessment

**Scope — `scope-Single-Component`**  
Core changes are confined to resume chain entry context, terminal persist matching, and one config token — no dispatcher, UI, or prompt table edits.

**Conf — `conf-Medium`**  
Patterns are established (**AST-370**, **AST-518**, **AST-517**); remaining uncertainty is Manage Tasks **`run_next`** graph and prompt token usage (Susan), plus merge order with **AST-552**.

**Risk — `HIGH`**  
Incorrect persist or token gaps write wrong **`resume_content`** or leave jobs without artifacts while later hops appear successful; structure filtering limits blast radius but job-level data is user-facing.

---

## Self-review vs ASTRAL_CODE_RULES

| Rule | Check |
|------|--------|
| §1.3 DRY | Reuse **`filter_content_to_resume_structure`** / **`save_job_artifact_resume_content`**; one persist match helper. |
| §2.1 config | No pipeline order in config; token + comments only. |
| §2.4 batch | No change to **`batch_id`** assignment; chain inherits existing hop ledger behavior. |
| §2.6 state machine | No job state transitions in this ticket (**AST-552**). |
| §3.3 imports | Tracker → candidate module for structure helpers; agent → tracker lazy import preserved. |
| §3.5 naming | snake_case helpers prefixed by domain (`parsed_matches_resume_content_shape`). |

**Conflicts:** None if terminal key remains **`finalize_job_resume`**. If Susan renames the terminal task in **TASK_CONFIG**, update Stage 3 guard to match — do not implement without a plan revision.

---

## Review (build stub)

**Built:** `origin/sub/AST-300/AST-551-structure-aligned-resume-chain` @ `ffcb0a85`.

**Stages delivered:**
- Stage 1: structure-aware `parsed_matches_resume_content_shape` + persist handoff (`e8a4ac62`).
- Stage 2: `run_resume_artifact_chain_for_job` seeds `candidate_data` / `astral_candidate_id` (`2c99bceb`).
- Stage 3: terminal persist guard (`finalize_job_resume` / `finalize_cover_letter`) + `{$RESUME_SECTION_CATALOG}` token (`ffcb0a85`).

**Susan manual:** Confirm Manage Tasks resume chain ends at **`finalize_job_resume`** and early-hop prompts use **`{$BASE_RESUME}`** / mid-hop **`{$CALLER_RESPONSE}`** — code cannot assert DB **`run_next`** graph.

**E2E with AST-552:** Full BUILD_ARTIFACTS dispatch → chain → **`resume_content`** persist + failure transitions deferred to **AST-552** + parent UAT.

---

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-300/AST-551-structure-aligned-resume-chain` @ `77ee996f`.

### What's solid

- **Plan fidelity (Stages 1–3):** `parsed_matches_resume_content_shape` / `_resume_payload_body` replace the global `artifact_shapes.resume_content` required-key gate; persist still flows through `save_job_artifact_resume_content` → `_prepare_job_resume_content` (AST-518 filter + contact snapshot).
- **Terminal guard:** `do_task` only calls `persist_job_artifact_from_parsed` when `task_key` is `finalize_job_resume` or `finalize_cover_letter`, with explicit `allow_resume` / `allow_cover_letter` flags — intermediate hops cannot accidentally write `resume_content`.
- **Chain context:** `run_resume_artifact_chain_for_job` seeds `job`, `candidate_data`, and `astral_candidate_id` so `{$BASE_RESUME}` and job tokens resolve on the first hop.
- **Token:** `RESUME_SECTION_CATALOG` registered in `TOKEN_SOURCES` and emitted from `build_job_token_context` in catalog order.
- **Tests / bible:** Component tests cover subset catalog match, `agent_payload` wrapper, persist without global shape keys, chain seeding, and token registration; §7.13zs manifest matches Betty’s narrowed run.

### Issues

| Severity | Finding | Location | Recommended action |
| --- | --- | --- | --- |
| **discuss** | Chain aborts only when `not candidate_data and candidate_id`; jobs with empty `candidate_data` but no `company` → `candidate_id` still enter the chain (weak `{$BASE_RESUME}`). | `src/core/agent.py` `run_resume_artifact_chain_for_job` | Confirm intentional for orphan jobs, or tighten guard to fail whenever `candidate_data` is empty after `_candidate_data_for_job`. |
| **advisory** | Parent AC 2–4 (full BUILD_ARTIFACTS run, BUILD_FAILED, no false CANDIDATE_REVIEW) are **AST-552** scope — not gaps in this diff. | sibling **AST-552** | Parent UAT should not fail **AST-551** on missing dispatch/state wiring. |
| **advisory** | `BUILD_CONFIG.artifact_shapes.resume_content` doc comment was plan Stage 3; already on `origin/dev` (not in this diff). | `src/utils/config.py` | No action unless Susan wants the comment duplicated in this branch. |
| **advisory** | DB `run_next` graph and prompt token usage cannot be verified in code. | Manage Tasks | Susan: confirm chain ends at `finalize_job_resume`; early hops use `{$BASE_RESUME}` / mid-hop `{$CALLER_RESPONSE}`. |

### Recommended actions (engineer / resolve-astral)

| Priority | Action |
| --- | --- |
| — | No **fix-now** code items from this review. |
| discuss | Reply on thread if empty-`candidate_data` without `candidate_id` should hard-fail before chain start. |
| manual | Susan: Manage Tasks terminal key + prompt tokens (see advisory above). |
| merge | **AST-552** before expecting full parent epic UAT on BUILD_ARTIFACTS failure paths. |

---

## Resolution (resolve-astral)

**Date:** 2026-06-03

**Radia discuss (empty `candidate_data`):** Tightened `run_resume_artifact_chain_for_job` to return `success: False` whenever `_candidate_data_for_job` is empty — including jobs with no `company` / `candidate_id` — so the chain never starts without `{$BASE_RESUME}` context (plan Stage 2).

**fix-now:** none (unchanged).

**advisory:** Parent AC 2–4 remain **AST-552**; Susan manual on Manage Tasks `run_next` / prompt tokens unchanged.
