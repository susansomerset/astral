<!-- linear-archive: AST-595 archived 2026-06-23 -->

## Linear archive (AST-595)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-595/compound-build-artifacts-hop-states-and-chain-order-config-need-to  
**Status at archive:** Done  
**Project:** Astral Artifacts  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-593 — Need to pick up and parse daisy chained prompts from the middle using agent_data content  
**Blocked by / blocks / related:** parent: AST-593; blocks: AST-597; blocks: AST-596

### Description

## What this implements

Extend the artifact resume chain job lifecycle with explicit compound **BUILD_ARTIFACTS.<task_key>** entries in **JOB_STATES** and a config block listing hop order (explicit task keys for v1 — no runtime TASK_CONFIG ordering). **Generate Artifacts** approval transitions the job to the configured first compound state (Susan: e.g. **BUILD_ARTIFACTS.anticipate_scan** or first hop in the explicit list). Mid-chain failures do **not** move jobs to **BUILD_FAILED**; the job stays at the last successful compound state until a later hop succeeds or Susan intervenes.

## Acceptance criteria

1. After hop *N* succeeds in a resume artifact chain, the job's recorded progress reflects that *N* completed and identifies the next hop entry task — observable without re-running hop *N*. (state/progress half — compound state encodes completed + next entry)
2. A full successful chain still lands the job in **CANDIDATE_REVIEW** with non-empty structure-keyed `resume_content`; mid-chain progress alone never shows a candidate-ready draft in the Job Analysis Report. (terminal transition from final compound state only)

## Boundaries

* Does not hydrate **agent_data** into caller tokens — sibling Ada ticket.
* Does not change Manage Tasks `run_next` authoring (**AST-313**).
* Does not fix **draft_job_resume** validation (**AST-592**).
* Cover letter / consult / roster chains out of scope.

## Notes for planning

* **ASTRAL_CODE_RULES §2.1** — all state lists and hop order in `config.py`.
* Align compound states with Phase E task keys already registered (**AST-450**).
* Susan resolved: compound **JOB_STATES** strings, explicit config order, no **BUILD_FAILED** on daisy-chain hop failure.

## Git branch (authoritative)

Per **orientation-astral § Branch law**: parent **ftr/AST-593-mid-chain-artifact-resume**, child **sub/AST-593/<child-id>-compound-build-artifacts-hop-states**. Created at dispatch-linear.

### Comments

#### radia — 2026-06-12T16:51:31.895Z
**Review** — `origin/dev...origin/sub/AST-593/AST-595-compound-build-artifacts-hop-states` @ `8f23c644` (product @ `3d1651cf` + `8ab0fe54`, manifest @ `edd5eb1a`)

**Plan doc:** [`docs/features/artifacts/ast-595-compound-build-artifacts-hop-states.md`](https://github.com/susansomerset/astral/blob/sub/AST-593/AST-595-compound-build-artifacts-hop-states/docs/features/artifacts/ast-595-compound-build-artifacts-hop-states.md) — Radia review section @ `8f23c644`

### Solid (plan + rules)

- All four plan stages: `hop_task_keys`, compound `JOB_STATES` + helpers/asserts, generate/cancel/approve → `BUILD_ARTIFACTS.anticipate_scan`, dispatch `trigger_state` per hop, `_dispatch_sort_by_for` compound prefix.
- **§2.1 / §2.6:** Config-driven hop order; transitions via `tracker.transition_job_state` with registered `prior_states`.
- **§3.3:** `tracker.py` imports only `config` helpers.
- Self-Assessment scope holds (`Single-Component`); `first_task_key` vs `hop_task_keys[0]` split preserved for siblings.
- Betty `§7.13zz` manifest covers registry, dispatch, recommended UI manifest, generate/cancel/approve, mid-hop cancel.

### discuss

- `src/ui/frontend/src/components/CandidateJobRowActions.tsx:3` — `REVIEW_LIKE` still lists flat `"BUILD_ARTIFACTS"` only; compound hop jobs may miss row actions until frontend follow-up (out of scope here — confirm sibling ticket).
- `src/core/consult.py:56` — flat `"BUILD_ARTIFACTS"` → `contemplate_job` mapping remains; **AST-596** must align consult/dispatch claim before mid-chain production use.

### advisory

- `_dispatch_sort_by_for` retains legacy `"BUILD_ARTIFACTS"` tuple member alongside compound prefix check — harmless until flat state retired.
- Module-level `_RESUME_ARTIFACT_HOP_TASK_KEYS` seeds `JOB_STATES` before `BUILD_CONFIG`; public helpers read `BUILD_CONFIG` — same tuple reference, acceptable.

**No fix-now.** Hedy may proceed **`resolve-astral`** unless Susan wants frontend compound-state wiring tracked on epic before **AST-596**/**AST-597**.

#### betty — 2026-06-12T04:42:51.416Z
**QA manifest (AST-595)** — `origin/sub/AST-593/AST-595-compound-build-artifacts-hop-states` @ `edd5eb1a`

`docs/ASTRAL_TEST_BIBLE.md` shasum on publish ref: `fe6b16817b29bb48ba6e1816c1f4baa8e4f549df`

**§7.13zz** — compound `BUILD_ARTIFACTS.<task_key>` registry; generate/cancel/approve entry; dispatch `trigger_state` per hop. Sibling **AST-596** / **AST-597** consult/dispatcher flat-`BUILD_ARTIFACTS` tests intentionally **not** in this manifest.

1. `tests/component/utils/test_config.py::TestAst595CompoundBuildArtifactsHopStates`
2. `tests/component/utils/test_config.py::TestAst479LikePassStates::test_recommended_job_states_post_synthesis_exclude_passed_like`
3. `tests/component/utils/test_config.py::TestAst520AnticipateScanTaskKey::test_build_artifacts_entry_unchanged`
4. `tests/component/utils/test_config.py::TestBuildStateUiManifest::test_ast522_recommended_manifest_sections_and_phase_columns`
5. `tests/component/utils/test_config.py::TestBuildStateUiManifest::test_ast562_recommended_primary_actions_by_state`
6. `tests/component/utils/test_config.py::TestBuildStateUiManifest::test_ast562_recommended_prior_states_allow_cancel_from_build`
7. `tests/component/utils/test_config.py::TestAst549DispatchAdminDefaults::test_contemplate_job_artifact_trigger_sort`
8. `tests/component/core/test_tracker.py::TestAst562ArtifactBuildTransitions::test_start_artifact_build_from_recommended`
9. `tests/component/core/test_tracker.py::TestAst562ArtifactBuildTransitions::test_cancel_from_mid_hop_compound_state`
10. `tests/component/core/test_tracker.py::TestAst562ArtifactBuildTransitions::test_cancel_rejects_wrong_state`
11. `tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_list_recommended_and_default`
12. `tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_approve_artifacts_from_recommended`
13. `tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_approve_artifacts_wrong_state_returns_409`
14. `tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_approve_artifacts_missing_job_returns_404`
15. `tests/component/ui/api/test_api_jobs.py::TestAst562GenerateCancelRoutes::test_generate_artifacts_happy_path`
16. `tests/component/ui/api/test_api_jobs.py::TestAst562GenerateCancelRoutes::test_cancel_artifact_build_happy_path`
17. `tests/component/ui/api/test_api_jobs.py::TestAst562GenerateCancelRoutes::test_cancel_artifact_build_409_wrong_state`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst595CompoundBuildArtifactsHopStates \
  tests/component/utils/test_config.py::TestAst479LikePassStates::test_recommended_job_states_post_synthesis_exclude_passed_like \
  tests/component/utils/test_config.py::TestAst520AnticipateScanTaskKey::test_build_artifacts_entry_unchanged \
  tests/component/utils/test_config.py::TestBuildStateUiManifest::test_ast522_recommended_manifest_sections_and_phase_columns \
  tests/component/utils/test_config.py::TestBuildStateUiManifest::test_ast562_recommended_primary_actions_by_state \
  tests/component/utils/test_config.py::TestBuildStateUiManifest::test_ast562_recommended_prior_states_allow_cancel_from_build \
  tests/component/utils/test_config.py::TestAst549DispatchAdminDefaults::test_contemplate_job_artifact_trigger_sort \
  tests/component/core/test_tracker.py::TestAst562ArtifactBuildTransitions::test_start_artifact_build_from_recommended \
  tests/component/core/test_tracker.py::TestAst562ArtifactBuildTransitions::test_cancel_from_mid_hop_compound_state \
  tests/component/core/test_tracker.py::TestAst562ArtifactBuildTransitions::test_cancel_rejects_wrong_state \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_list_recommended_and_default \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_approve_artifacts_from_recommended \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_approve_artifacts_wrong_state_returns_409 \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_approve_artifacts_missing_job_returns_404 \
  tests/component/ui/api/test_api_jobs.py::TestAst562GenerateCancelRoutes::test_generate_artifacts_happy_path \
  tests/component/ui/api/test_api_jobs.py::TestAst562GenerateCancelRoutes::test_cancel_artifact_build_happy_path \
  tests/component/ui/api/test_api_jobs.py::TestAst562GenerateCancelRoutes::test_cancel_artifact_build_409_wrong_state
```

— Betty

#### hedy — 2026-06-11T23:44:44.690Z
Plan: [`docs/features/artifacts/ast-595-compound-build-artifacts-hop-states.md`](https://github.com/susansomerset/astral/blob/sub/AST-593/AST-595-compound-build-artifacts-hop-states/docs/features/artifacts/ast-595-compound-build-artifacts-hop-states.md) @ `381695ba`

**Scope — Single-Component:** `config.py` compound `JOB_STATES` + helpers; `tracker.py` / `api_jobs.py` generate/cancel/approve entry only.

**Conf — Medium:** Susan resolved compound encoding and explicit hop list; split between `hop_task_keys[0]` (Generate Artifacts) and legacy `first_task_key` (chain helper default) is documented for siblings.

**Risk — HIGH:** Wrong `prior_states` / `RECOMMENDED_JOB_STATES` breaks recommended list, cancel, and dispatch `trigger_state` alignment — **AST-596** and **AST-597** depend on this registry.

Four stages: (1) `hop_task_keys` + compound registry, (2) generate/cancel API, (3) dispatch `trigger_state` mapping, (4) compile verify. Out of scope: `consult.py`, `agent.py`, per-hop transitions (**AST-597**), batch release (**AST-596**).

---

# Compound BUILD_ARTIFACTS hop states and chain order config

**Linear:** [AST-595](https://linear.app/astralcareermatch/issue/AST-595/compound-build-artifacts-hop-states-and-chain-order-config-need-to)  
**Parent:** [AST-593](https://linear.app/astralcareermatch/issue/AST-593/need-to-pick-up-and-parse-daisy-chained-prompts-from-the-middle-using)  
**Publish ref (origin):** `sub/AST-593/AST-595-compound-build-artifacts-hop-states`

## Summary

Replace the flat **`BUILD_ARTIFACTS`** job state with explicit compound states **`BUILD_ARTIFACTS.<task_key>`** for each resume artifact chain hop, driven by an ordered **`hop_task_keys`** list in **`BUILD_CONFIG`**. **Generate Artifacts** / **approve_artifacts** transitions **`RECOMMENDED → BUILD_ARTIFACTS.<first_hop>`** (v1 first hop: **`anticipate_scan`**). Each compound state encodes “upstream hops through the prior key are done; the next dispatch entry is this **`task_key`**.” This ticket is **config + state registry + UI/dispatch alignment only** — per-hop transitions after **`run_next`**, mid-chain **`agent_data`** reuse, and hop-failure batch release are sibling tickets (**AST-597**, **AST-596**).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `hop_task_keys`, compound **`JOB_STATES`**, helpers, **`RECOMMENDED_JOB_STATES`**, UI manifest inputs, dispatch **`trigger_state`** mapping for resume hops | utils |
| `src/core/tracker.py` | **`start_artifact_build`**, **`cancel_artifact_build`**, import config helpers | core |
| `src/ui/api/api_jobs.py` | **`approve_artifacts`** uses **`start_artifact_build`** (not hardcoded flat state) | ui |

**Out of scope (sibling tickets — do not touch):**

| Ticket | Owner | Work |
|--------|-------|------|
| **AST-597** | Ada | Per-hop **`transition_job_state`** after each successful **`run_next`** hop; **`agent_data`** caller hydration; debug Style D reuse lines |
| **AST-596** | Hedy | Mid-chain dispatch claim on compound **`trigger_state`**; hop failure batch release; stop **`BUILD_FAILED`** on daisy-chain hop failure in **`consult.py`** |
| **AST-592** | — | **`draft_job_resume`** validation bug |
| **AST-313** | Susan | **`run_next`** authoring |

## Stage 1: Resume hop order + compound state helpers (`config.py`)

**Done when:** **`BUILD_CONFIG['resume_artifact_chain']['hop_task_keys']`** is the single ordered v1 list; helpers derive compound state strings; startup asserts pass; flat **`BUILD_ARTIFACTS`** is removed from **`JOB_STATES`**.

1. In **`BUILD_CONFIG['resume_artifact_chain']`**, set explicit v1 hop order (resume chain only — **no** cover-letter / application keys):

   ```python
   "hop_task_keys": (
       "anticipate_scan",
       "contemplate_job",
       "advise_job_resume",
       "draft_job_resume",
       "check_job_resume",
       "finalize_job_resume",
   ),
   ```

   Keep **`first_task_key": "contemplate_job"`** unchanged for **`run_resume_artifact_chain_for_job`** default when no dispatch row overrides (**AST-534**). **Generate Artifacts** uses **`hop_task_keys[0]`**, not **`first_task_key`**.

   ⚠️ **Decision:** Susan’s open-question answer names **`BUILD_ARTIFACTS.anticipate_scan`** as the first position state. **`hop_task_keys[0]`** is **`anticipate_scan`** even though legacy **`first_task_key`** remains **`contemplate_job`** for backward-compatible chain helper defaults until siblings land.

2. Immediately after **`BUILD_CONFIG`**, add helpers (names exact):

   - **`RESUME_ARTIFACT_COMPOUND_PREFIX = "BUILD_ARTIFACTS."`**
   - **`resume_artifact_hop_task_keys() -> tuple[str, ...]`** — reads **`hop_task_keys`** from **`BUILD_CONFIG`**
   - **`resume_artifact_compound_state(task_key: str) -> str`** — returns **`f"BUILD_ARTIFACTS.{task_key}"`**
   - **`resume_artifact_first_compound_state() -> str`** — **`resume_artifact_compound_state(hop_task_keys()[0])`**
   - **`resume_artifact_next_compound_state(task_key: str) -> str | None`** — next hop’s compound state, or **`None`** when **`task_key`** is the last hop (**`finalize_job_resume`** → terminal transition to **`CANDIDATE_REVIEW`** is **AST-597** / existing **AST-552** batch exit)
   - **`parse_resume_artifact_hop(state: str) -> str | None`** — returns **`task_key`** when **`state.startswith("BUILD_ARTIFACTS.")`**, else **`None`**
   - **`is_resume_artifact_in_progress(state: str) -> bool`** — prefix test on **`BUILD_ARTIFACTS.`**
   - **`all_resume_artifact_compound_states() -> tuple[str, ...]`** — one compound string per hop key

3. Startup asserts (after helpers, before **`JOB_STATES`** consumers):

   ```python
   _RAH = resume_artifact_hop_task_keys()
   assert len(_RAH) >= 1
   assert all(tk in TASK_CONFIG for tk in _RAH)
   assert all((TASK_CONFIG[tk] or {}).get("entity_type") == "job" for tk in _RAH)
   ```

4. Remove the flat **`"BUILD_ARTIFACTS"`** entry from **`JOB_STATES`**. For each index **`i`**, **`tk = _RAH[i]`**, add:

   ```python
   f"BUILD_ARTIFACTS.{tk}": {
       "prior_states": ["RECOMMENDED"] if i == 0 else [resume_artifact_compound_state(_RAH[i - 1])],
   }
   ```

   Semantics: job in **`BUILD_ARTIFACTS.contemplate_job`** means **`anticipate_scan`** completed and the next entry hop is **`contemplate_job`**. Hop failure stays on the same compound state (no self-loop in **`prior_states`** — redispatch does not require a state transition).

5. Update **`prior_states`** on existing states that referenced flat **`BUILD_ARTIFACTS`** — replace with **`list(all_resume_artifact_compound_states())`** where cancel/review return paths need it:

   - **`RECOMMENDED`**: replace **`BUILD_ARTIFACTS`** with all compound states (cancel from any in-progress hop)
   - **`CANDIDATE_REVIEW`**: replace **`BUILD_ARTIFACTS`** with all compound states; keep **`BUILD_FAILED`**
   - **`CANDIDATE_APPLIED`**, **`CANDIDATE_SKIPPED`**: same replacement
   - **`BUILD_FAILED`**: set **`prior_states`** to **`list(all_resume_artifact_compound_states())`** only (legacy flat **`BUILD_ARTIFACTS`** removed). Document in build comment: **AST-596** stops calling **`BUILD_FAILED`** on daisy-chain hop failure; compound jobs stay on last successful hop per parent AC.

   ⚠️ **Decision:** Do **not** delete **`BUILD_FAILED`** from **`JOB_STATES`** in v1 — consult batch may still reference it until **AST-596** lands; expanding **`prior_states`** avoids **`ValueError`** if a stray transition fires during epic rollout.

6. Replace **`RECOMMENDED_JOB_STATES`**:

   ```python
   RECOMMENDED_JOB_STATES = ["RECOMMENDED", *all_resume_artifact_compound_states(), "CANDIDATE_REVIEW"]
   ```

7. Replace **`JOBS_RECOMMENDED_PRIMARY_ACTIONS["BUILD_ARTIFACTS"]`**: delete that key. For **each** compound state in **`all_resume_artifact_compound_states()`**, set the same cancel action dict currently on flat **`BUILD_ARTIFACTS`** (**`action_key`: `cancel_build`**, **`path_suffix`: `cancel_artifact_build`**).

8. Replace **`JOBS_RECOMMENDED_UI_SECTIONS`**: remove flat **`BUILD_ARTIFACTS`** row. For each compound state, add **`{"state": "<compound>", "label": "In Progress"}`** (same label for all hops — recommended list still shows one visual bucket).

9. Re-run existing asserts that reference **`RECOMMENDED_JOB_STATES`** / **`JOBS_RECOMMENDED_PRIMARY_ACTIONS`** — they must still pass after expansion.

## Stage 2: Generate / cancel API paths (`tracker.py`, `api_jobs.py`)

**Done when:** **`POST …/generate_artifacts`** and **`POST …/approve_artifacts`** return the first compound state; cancel works from any compound in-progress state; no code path transitions to flat **`BUILD_ARTIFACTS`**.

1. In **`src/core/tracker.py`**, import **`resume_artifact_first_compound_state`**, **`is_resume_artifact_in_progress`**, **`parse_resume_artifact_hop`** from **`src.utils.config`**.

2. Change **`start_artifact_build(astral_job_id)`**:
   - Keep **`RECOMMENDED`-only guard and error message.
   - **`first = resume_artifact_first_compound_state()`**
   - **`transition_job_state([astral_job_id], first)`**
   - **`return first`**

3. Change **`cancel_artifact_build(astral_job_id)`**:
   - Replace **`job.get("state") != "BUILD_ARTIFACTS"`** with **`not is_resume_artifact_in_progress(job.get("state") or "")`**
   - Error message: **`"cancel only from BUILD_ARTIFACTS in-progress hop states"`**
   - Remaining logic unchanged (**`clear_job_build_artifacts`**, batch lock clear, **`RECOMMENDED`**).

4. In **`src/ui/api/api_jobs.py`**, change **`approve_artifacts`**:
   - Replace **`transition_job_state([astral_job_id], "BUILD_ARTIFACTS")`** with **`state = start_artifact_build(astral_job_id)`** (same pattern as **`generate_artifacts`**).
   - Return **`{"ok": True, "state": state}`** using the returned compound string.

5. Grep **`src/`** for hardcoded **`"BUILD_ARTIFACTS"`** transitions **outside** **`consult.py`**, **`agent.py`**, **`dispatcher.py`**. Fix only call sites in **this ticket’s files**; list remaining hits in the Linear build comment for **AST-596** / **AST-597** (do not patch **`consult.py`** here).

## Stage 3: Dispatch admin `trigger_state` alignment (`config.py`)

**Done when:** **`dispatch_task_admin_defaults(task_key)`** returns compound **`trigger_state`** for every resume hop key in **`hop_task_keys`**; **`_dispatch_sort_by_for`** sorts compound build states like legacy **`BUILD_ARTIFACTS`**.

1. In **`_dispatch_trigger_state_for_task_key`**, **before** the **`contemplate_job → BUILD_ARTIFACTS`** branch, add:

   ```python
   if task_key in resume_artifact_hop_task_keys():
       return resume_artifact_compound_state(task_key)
   ```

   Remove (or leave unreachable) the old **`if task_key == "contemplate_job": return "BUILD_ARTIFACTS"`** branch.

2. In **`_dispatch_sort_by_for`**, extend the job branch:

   ```python
   if trigger_state in ("BUILD_ARTIFACTS", "CANDIDATE_REVIEW"):
   ```

   to also match **`trigger_state.startswith("BUILD_ARTIFACTS.")`** → **`"state_changed_at"`**.

3. Do **not** add resume hop keys to **`DISPATCH_SCHEDULABLE_TASK_KEYS`** in this ticket (**`anticipate_scan`** stays non-schedulable per **AST-520**). Susan adds mid-chain Scheduled Actions manually; **AST-596** owns claim behavior once rows exist.

4. Grep **`tests/component/utils/test_config.py`** for assertions expecting **`contemplate_job`** **`trigger_state == "BUILD_ARTIFACTS"`** — do **not** edit tests; note expected Betty delta in Linear comment: compound strings for each hop key.

## Stage 4: Verify

**Done when:** **`python3 -m py_compile`** passes on touched modules; config asserts pass at import.

1. **`python3 -m py_compile src/utils/config.py src/core/tracker.py src/ui/api/api_jobs.py`**
2. **`python3 -c "from src.utils import config; print(config.resume_artifact_first_compound_state())"`** — must print **`BUILD_ARTIFACTS.anticipate_scan`**
3. Linear comment for Betty (**post Code Complete**): extend **`tests/component/utils/test_config.py`** (compound **`JOB_STATES`**, **`dispatch_task_admin_defaults`** per hop, **`RECOMMENDED_JOB_STATES`** length), **`tests/component/core/test_tracker.py`** (generate/cancel compound states), **`tests/component/ui/api/test_api_jobs.py`** (approve returns first compound state).

## Execution contract (for the developer agent)

- Execute stages in order. **Stop** if **`hop_task_keys`** references a missing **`TASK_CONFIG`** key — comment on **AST-595**, do not invent keys.
- Do **not** edit **`consult.py`**, **`agent.py`**, **`dispatcher.py`**, **`tests/`**, or frontend files.
- Do **not** implement per-hop success transitions or **`BUILD_FAILED`** removal — **AST-597** / **AST-596**.
- When grep finds hardcoded flat **`BUILD_ARTIFACTS`** in out-of-scope files, **stop only if** changing **this ticket’s** stages requires it; otherwise list for siblings in Linear comment.

## Self-Assessment

**Scope — `Single-Component`**  
Primary work is **`config.py`** state registry and helpers; **`tracker.py`** and **`api_jobs.py`** only adjust generate/cancel/approve entry to the first compound state.

**Conf — `Medium`**  
Susan resolved encoding (**compound JOB_STATES**, explicit hop list, no **`BUILD_FAILED`** on chain hops). Remaining nuance is **`prior_states`** sweep and keeping **`first_task_key`** vs **`hop_task_keys[0]`** split clear for siblings.

**Risk — `HIGH`**  
Wrong **`JOB_STATES`** / **`RECOMMENDED_JOB_STATES`** breaks recommended list grouping, cancel, and dispatch **`trigger_state`** alignment; siblings depend on this registry being correct before **AST-596** / **AST-597**.

## Self-review vs ASTRAL_CODE_RULES

| Rule | Assessment |
|------|------------|
| §2.1 config | All hop order and compound state strings live in **`config.py`**; no runtime **`TASK_CONFIG`** seq ordering. |
| §2.6 state machine | All transitions via **`tracker.transition_job_state`**; compound keys registered with **`prior_states`**. |
| §1.3 DRY | Single helper module in **`config.py`**; **`start_artifact_build`** reuses **`resume_artifact_first_compound_state()`**. |
| §2.4 batch | No batch claim changes in this ticket (**AST-596**). |
| §3.3 imports | **`tracker`** imports helpers from **`config`** only — no new cross-layer violations. |
| §3.5 naming | Helpers prefixed **`resume_artifact_*`** to distinguish from cover-letter chain. |

No unresolved conflicts — plan is implementable without sibling code.

## Review

**Built:** `dev-hedy` → `origin/sub/AST-593/AST-595-compound-build-artifacts-hop-states` (Joan publish after build commits).

**Betty delta (tests):** `tests/component/utils/test_config.py` — compound `JOB_STATES`, `dispatch_task_admin_defaults` per hop, `RECOMMENDED_JOB_STATES` length; `tests/component/core/test_tracker.py` — generate/cancel compound states; `tests/component/ui/api/test_api_jobs.py` — approve returns first compound state.

**Sibling grep (flat `BUILD_ARTIFACTS` left in scope):** `src/core/consult.py` — AST-596; per-hop transitions — AST-597.

### Radia review — 2026-06-12

**Diff:** `origin/dev...origin/sub/AST-593/AST-595-compound-build-artifacts-hop-states` @ `edd5eb1a`  
**Product commits reviewed:** `3d1651cf`, `8ab0fe54` (+ Betty manifest `edd5eb1a`)

#### What's solid

- All four plan stages land: `hop_task_keys` + compound `JOB_STATES` registry, generate/cancel/approve entry to `BUILD_ARTIFACTS.anticipate_scan`, dispatch `trigger_state` per hop, startup asserts on hop keys vs `TASK_CONFIG`.
- **§2.1 / §2.6:** Hop order and compound strings are config-driven; `start_artifact_build` / `cancel_artifact_build` / `approve_artifacts` route through `tracker.transition_job_state` with registered `prior_states`.
- **§3.3:** `tracker.py` imports only `config` helpers — no new layer violations.
- **Self-Assessment alignment:** Single-component scope holds; `first_task_key` vs `hop_task_keys[0]` split preserved for siblings.
- Betty manifest (`§7.13zz`) covers registry, dispatch defaults, recommended manifest, generate/cancel/approve API, and mid-hop cancel.

#### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| discuss | `src/ui/frontend/src/components/CandidateJobRowActions.tsx:3` | `REVIEW_LIKE` still lists flat `"BUILD_ARTIFACTS"` only — jobs in compound hop states may miss row-action wiring until a frontend follow-up (out of scope here; confirm sibling or separate ticket). |
| discuss | `src/core/consult.py:56` | `_TASK_KEY_BY_STATE` still maps flat `"BUILD_ARTIFACTS"` → `contemplate_job` — expected **AST-596** scope; dispatch claim must align before mid-chain runs in production. |
| advisory | `config.py` `_dispatch_sort_by_for` | Retains legacy `"BUILD_ARTIFACTS"` tuple member alongside `startswith(RESUME_ARTIFACT_COMPOUND_PREFIX)` — harmless until flat state is fully retired. |
| advisory | `config.py` import order | Module-level `_RESUME_ARTIFACT_HOP_TASK_KEYS` seeds `JOB_STATES` before `BUILD_CONFIG` block; `BUILD_CONFIG['hop_task_keys']` references the same tuple — acceptable; public helpers read `BUILD_CONFIG`. |

#### Recommended actions

| Action | Owner | Notes |
|--------|-------|-------|
| Proceed to `resolve-astral` | Hedy | No fix-now product items on this diff. |
| Track frontend compound-state set | Susan / epic | Extend `CandidateJobRowActions` (or server-resolved payload) when compound jobs need candidate-row actions. |
| Land consult/dispatcher alignment | Hedy (**AST-596**) | Replace flat `BUILD_ARTIFACTS` consult mapping; mid-chain claim on compound `trigger_state`. |
| Per-hop success transitions | Ada (**AST-597**) | `resume_artifact_next_compound_state` helper is ready; wire post-`run_next` transitions. |

## Resolution — 2026-06-12

**Review outcome:** Radia **no fix-now** @ `8f23c644`. No product commits in this resolve pass.

**Discuss (deferred):**

- Frontend `CandidateJobRowActions` flat `BUILD_ARTIFACTS` set — track on epic / sibling when compound jobs need candidate-row actions.
- `consult.py` flat mapping — **AST-596** (already in flight).

**Advisory:** Accepted as-is (legacy sort tuple member; module-level hop tuple vs `BUILD_CONFIG` reference).

**Publish ref @ resolve:** `origin/sub/AST-593/AST-595-compound-build-artifacts-hop-states` @ `8f23c644` (product `3d1651cf`, `8ab0fe54`; QA `edd5eb1a`; Radia review doc `8f23c644`).

**§9a:** Dry-run merge clean into `origin/dev` and `origin/ftr/AST-593-mid-chain-artifact-resume`.
