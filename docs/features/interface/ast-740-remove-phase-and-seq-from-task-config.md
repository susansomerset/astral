<!-- linear-archive: AST-740 archived 2026-06-23 -->

## Linear archive (AST-740)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-740/remove-phase-and-seq-from-task-config-organizing-tasks  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-734 — Organizing Tasks  
**Blocked by / blocks / related:** parent: AST-734

### Description

## What this implements

After admin UI and APIs read grouping exclusively from persisted agent-task metadata, remove `phase` and `seq` from every TASK_CONFIG entry in [config.py](<http://config.py>). Grep and verify no runtime code path reads those keys for UI grouping, sort, or admin enrichment. Single source of truth for task organization is DB metadata edited via Manage Tasks.

## Acceptance criteria

8. `phase` and `seq` are removed from TASK_CONFIG; grep confirms no runtime read of those keys for UI grouping or sort.

## Boundaries

* Does not add new grouping fields or migration — completed by Hedy child.
* Does not change Manage Tasks / Scheduled Actions React — completed by Katherine child.
* Does not alter task execution, grading, dispatch orchestration, or non-UI uses of TASK_CONFIG.

## Notes for planning

* Run only after Katherine child merges grouping UI to DB fields; coordinate publish ref refresh with siblings.
* Acceptance is grep-clean for `phase`/`seq` on TASK_CONFIG entries and UI/admin read paths — backend consult paths that never used phase/seq are unchanged.

## Git branch (authoritative)

Per **orientation** § Branch law: parent `ftr/AST-734-organizing-tasks`, child `sub/AST-734/<child-id>-remove-phase-and-seq-from-task-config`. Blocked by metadata + admin UI children.

### Comments

#### radia — 2026-06-18T22:39:03.891Z
### AST-740 review

**Diff:** `origin/dev...origin/sub/AST-734/AST-740-remove-phase-and-seq-from-task-config` @ `0a0e0c7`. Publish tip includes sibling AST-738/739 + Betty manifests; AST-740 product delta = `1fb8582`.

**Plan fidelity:** Stages 1–3 satisfied — `JOB_ARTIFACT_ENTRY_TASK_KEYS` (9 keys, excludes `draft_cover_letter`); all `phase`/`seq` removed from `TASK_CONFIG`; `consult.py` imports constant at module top; `_grouping_from_agent_task_row` drops backward-compat `phase`/`seq`.

**ASTRAL_CODE_RULES:** §2.1 config split clean (UI grouping out of config; hop set explicit). §3.3 layer OK (`consult` → `utils` only). Stage 3 greps: zero `cfg.get("phase")` / `cfg.get("seq")` under `src/`.

**Tests:** `TestAst740RemoveConfigGrouping`, `TestAst740NoConfigPhaseSeqInApi` green on publish tip.

**Doc:** `docs/features/interface/ast-740-remove-phase-and-seq-from-task-config.md` (Review section @ `0a0e0c7`).

**Advisory:** `backfill_task_grouping_metadata.py` still reads config `phase`/`seq` for one-time seed — post-740 fresh catalog inserts default to `(unassigned)`; expected; Betty aligned tests.

No **fix-now** or **discuss** items. Ada may proceed **`resolve-child`** (no-op) or advance per epic rollup.

#### betty — 2026-06-18T22:31:34.899Z
**Bible shasum correction** (`origin/sub/...` @ `b12ed93`):
- `docs/test-bible/utils/config.md` `e31b6564180b46e7742164e107c486c7665d835e7c4c54ed812f4f5067c0bfc5`
- `docs/test-bible/data/database/agent_tasks.md` `fe5a4bd526b9b3bdd06daa4d8c550c897bd92fe55f01e1cb7972c1b81741e8bd`
- `docs/test-bible/ui/api/api_admin.md` `c3db77ba66220256f663634d4a339ef0a3576cfd1c145e2247a0038db0060cc5`

#### betty — 2026-06-18T22:31:29.845Z
## QA test manifest (AST-740)

**Publish:** `origin/sub/AST-734/AST-740-remove-phase-and-seq-from-task-config` @ `b12ed93` (`merge-tests(AST-740): origin/tests c99819b`)

**Prerequisites:** **AST-738** DB grouping + **AST-739** admin UI/API on publish tip (sibling `merge-tests` on ftr rollup).

### 1. New coverage
1. **`TestAst740RemoveConfigGrouping`** — every `TASK_CONFIG` entry lacks `phase`/`seq`; `JOB_ARTIFACT_ENTRY_TASK_KEYS` frozenset matches plan (excludes `draft_cover_letter`).
2. **`TestAst740NoConfigPhaseSeqInApi`** — Manage Tasks GET payload has grouping fields only; no backward-compat `phase`/`seq`.

### 2. Broken / revised tests
1. **`TestAst520AnticipateScanTaskKey`** — no config `phase`/`seq`; keeps print_label/trigger_state checks.
2. **`TestAst504CompanySearchTermsConfig`**, **`TestAst505InflowDiscoveryConfig::test_vet_inflow_discovery_task`** — assert keys absent, not phase labels.
3. **`TestAst738TaskGroupingMetadata`** — seed/new-row defaults are `(unassigned)` / `ZZZ` / `999.0` when config lacks phase/seq.
4. **`TestAst738TaskGroupingApi`** — `_grouping_from_agent_task_row` and GET task no longer emit `phase`/`seq`.
5. **`TestTaskRoutes::test_preview_task_and_get_update`** — same (grouping fields only).

### 3. Existing coverage (unchanged)
- **AST-739** Vitest page tests — still green; no AST-740 frontend product diff.

### Run (test-child)
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst740RemoveConfigGrouping \
  tests/component/utils/test_config.py::TestAst520AnticipateScanTaskKey \
  tests/component/utils/test_config.py::TestAst504CompanySearchTermsConfig \
  tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig::test_vet_inflow_discovery_task \
  tests/component/data/database/test_agent_tasks.py::TestAst738TaskGroupingMetadata \
  tests/component/ui/api/test_api_admin.py::TestAst740NoConfigPhaseSeqInApi \
  tests/component/ui/api/test_api_admin.py::TestAst738TaskGroupingApi \
  tests/component/ui/api/test_api_admin.py::TestTaskRoutes::test_preview_task_and_get_update \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

### Bible shasum (`origin/sub/...`)
- `docs/test-bible/utils/config.md` `701fd26a08051d6b55f4d3d25b51874f5f2d8ddbc6b0cd3b5f9041930daffcde`
- `docs/test-bible/data/database/agent_tasks.md` `db3c0a2aad3bc818d387b3b0a2f064c9587a6fe2496bdec49840aa546c742586`
- `docs/test-bible/ui/api/api_admin.md` `658553beaa0139e3db05dabeedfb7128f0d3f4c19f4765f66112ae6e716b1f23`

#### ada — 2026-06-18T22:15:42.607Z
Plan: `docs/features/interface/ast-740-remove-phase-and-seq-from-task-config.md`

https://github.com/susansomerset/astral/blob/sub/AST-734/AST-740-remove-phase-and-seq-from-task-config/docs/features/interface/ast-740-remove-phase-and-seq-from-task-config.md

**Self-assessment**
- **Scope:** Single-Component — `config.py` + `consult.py` only; explicit `JOB_ARTIFACT_ENTRY_TASK_KEYS` replaces phase probe; no frontend/DB/migration.
- **Conf:** Medium — key removal is mechanical, but build is gated on AST-738/739 on ftr and frozenset must match current Phase E membership minus `draft_cover_letter`.
- **Risk:** Medium — wrong entry-key set mis-routes artifact dispatch; config cleanup before AST-739 would break admin grouping.

Pre-build gate requires sibling merges on `origin/ftr/AST-734-organizing-tasks` before any `code()` stages.

---

# Remove phase and seq from TASK_CONFIG (Organizing Tasks)

**Linear:** [AST-740](https://linear.app/astralcareermatch/issue/AST-740/remove-phase-and-seq-from-task-config-organizing-tasks)  
**Parent:** [AST-734](https://linear.app/astralcareermatch/issue/AST-734/organizing-tasks)  
**Publish ref:** `sub/AST-734/AST-740-remove-phase-and-seq-from-task-config`

After [AST-738](https://linear.app/astralcareermatch/issue/AST-738/task-grouping-metadata-storage-and-seed) seeds grouping metadata on agent-task rows and [AST-739](https://linear.app/astralcareermatch/issue/AST-739/admin-ui-task-grouping-from-db-metadata) switches Manage Tasks and Scheduled Actions to read `task_group_order`, `task_group_name`, `task_seq`, and `task_name` from the database, this ticket deletes the legacy `phase` and `seq` keys from every `TASK_CONFIG` entry and removes all admin/API code paths that still read those keys for UI grouping or sort. Execution routing that previously inferred job-artifact dispatch hops from `"E. Job Artifacts"` phase labels is preserved via an explicit config constant — not UI metadata.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `JOB_ARTIFACT_ENTRY_TASK_KEYS`; remove `phase`/`seq` from every `TASK_CONFIG` entry | utils |
| `src/core/consult.py` | Route artifact entry hops via `JOB_ARTIFACT_ENTRY_TASK_KEYS` instead of `TASK_CONFIG` phase probe | core |

**Out of scope (sibling tickets — do not touch):**

| File / area | Owner |
|-------------|-------|
| `src/data/database.py`, migration/seed | AST-738 |
| `src/ui/api/api_admin.py` DB grouping fields, edit-modal save | AST-739 |
| `src/ui/frontend/src/pages/AdminTaskPrompts.tsx`, `AdminScheduledActions.tsx` | AST-739 |
| `tests/**` | Betty (qa-child) |

## Pre-build gate (mandatory — before Stage 1)

**Done when:** Epic worktree is on `sub/AST-734/AST-740-remove-phase-and-seq-from-task-config`, merge-clean vs `origin/dev`, and sibling work is present on `origin/ftr/AST-734-organizing-tasks`.

1. On epic worktree `astral-AST-734/`:
   ```bash
   git fetch origin
   git merge origin/dev
   git merge origin/ftr/AST-734-organizing-tasks
   ```
   Resolve conflicts; commit merge if needed. Re-check `BEHIND=0` vs `origin/dev` and `origin/dev` is ancestor of `HEAD`.
2. Verify AST-738 landed on ftr: `agent_task` (or equivalent storage) exposes persisted columns for `task_group_order`, `task_group_name`, `task_seq`, `task_name`; deploy seed populated rows for catalog keys.
3. Verify AST-739 landed on ftr: `GET /api/admin/tasks`, `GET /api/admin/tasks/<task_key>`, and `GET /api/admin/dispatch_tasks/task_keys` return the four DB grouping fields (not `phase`/`seq` from `TASK_CONFIG`); Manage Tasks and Scheduled Actions React pages group/sort on those fields.
4. If steps 2–3 fail, **stop** — post on [AST-740](https://linear.app/astralcareermatch/issue/AST-740/remove-phase-and-seq-from-task-config-organizing-tasks): `🛑 Pre-build gate blocked: sibling AST-738/AST-739 not on origin/ftr/AST-734-organizing-tasks`. Do not proceed.

⚠️ **Decision:** This ticket assumes Katherine's admin UI/API work is complete on ftr before build. Config cleanup without DB-backed grouping would break Manage Tasks and Scheduled Actions.

## Stage 1: Explicit job-artifact entry keys (preserve consult routing)

**Done when:** `_JOB_ARTIFACT_ENTRY_KEYS` in `consult.py` no longer reads `TASK_CONFIG[*]["phase"]`; dispatch routing for Phase E resume/artifact hops is unchanged (same keys as today, still excluding `draft_cover_letter` per AST-534).

1. In `src/utils/config.py`, after the `# Phase E. Job Artifacts` comment block (before the `"anticipate_scan"` entry), add a module-level constant:
   ```python
   # Dispatch consult hops that enter the job-artifact chain (AST-534 / AST-740).
   # Excludes draft_cover_letter — cover-letter chain uses _run_craft_job_cover_letter_batch.
   JOB_ARTIFACT_ENTRY_TASK_KEYS = frozenset({
       "anticipate_scan",
       "contemplate_job",
       "advise_job_resume",
       "draft_job_resume",
       "check_job_resume",
       "finalize_job_resume",
       "check_cover_letter",
       "finalize_cover_letter",
       "propose_application_responses",
   })
   ```
   ⚠️ **Decision:** Explicit frozenset replaces phase-string probe. Membership must match the current runtime set built from `str(v.get("phase") or "").startswith("E. Job Artifacts")` minus `draft_cover_letter` — verify with a one-liner in epic worktree before committing (compare sets; they must be equal).

2. In `src/core/consult.py`, replace the module-level `_JOB_ARTIFACT_ENTRY_KEYS` definition (lines ~1603–1607):
   ```python
   from src.utils.config import JOB_ARTIFACT_ENTRY_TASK_KEYS

   _JOB_ARTIFACT_ENTRY_KEYS = JOB_ARTIFACT_ENTRY_TASK_KEYS
   ```
   Prefer a single import at the top of `consult.py` with existing config imports if one exists; do not duplicate the frozenset in consult.

3. Do not change `run_consult_task` branching order (`draft_cover_letter` before `_JOB_ARTIFACT_ENTRY_KEYS`), `_run_job_artifact_entry_batch`, or any other consult logic.

## Stage 2: Remove phase and seq from TASK_CONFIG

**Done when:** No `TASK_CONFIG` entry contains `"phase"` or `"seq"` keys; unrelated config keys named with "phase" (e.g. `analysis_phases`, `phase_score_columns`, `JOBS_RECOMMENDED_REPORT_PHASE_TABS` tab ids) remain untouched.

1. In `src/utils/config.py`, delete every `"phase": "..."` and matching `"seq": <int>` line pair inside the `TASK_CONFIG = { ... }` dict only. There are entries across phases A–E (roughly 33 task keys); remove all pairs — do not leave partial cleanup.
2. Update the `# Phase E. Job Artifacts` header comment: remove references to ordering via `seq` in config (ordering is now DB `task_seq` / admin UI). Keep AST-450/AST-455 prompt-chain notes.
3. Do not add replacement `phase`/`seq` keys anywhere in `TASK_CONFIG`.

## Stage 3: Verify no config phase/seq reads remain in product code

**Done when:** Grep over `src/` finds zero reads of `TASK_CONFIG` grouping keys `phase`/`seq` for admin enrichment or UI sort; only unrelated "phase" tokens (Jobs Recommended report tabs, `analysis_phases`, etc.) may remain.

1. Run from repo root:
   ```bash
   rg '"phase"|"seq"' src/utils/config.py
   ```
   Expect **zero** matches inside `TASK_CONFIG` entries. Matches in `JOBS_RECOMMENDED_*`, `JOB_TOKEN_CONFIG["analysis_phases"]`, or tab ids like `phase_jd` are expected and must not be deleted.

2. Run:
   ```bash
   rg 'cfg\.get\("phase"\)|cfg\.get\("seq"\)|TASK_CONFIG\[.*\]\["phase"\]|TASK_CONFIG\[.*\]\["seq"\]' src/
   ```
   Expect **zero** matches. AST-739 should already have removed these from `api_admin.py`; if any remain in `src/ui/api/api_admin.py` (`_enrich_tasks`, `get_task`, `_dispatch_task_key_form_meta`, or unknown-key fallbacks), delete those `"phase"` / `"seq"` keys from response dicts — do **not** reintroduce config fallbacks.

3. Run:
   ```bash
   rg '\.get\("phase"\)|\.get\("seq"\)' src/core/consult.py
   ```
   Expect **zero** matches after Stage 1.

4. Do not edit `src/ui/frontend/**` — Katherine's AST-739 owns React grouping. If grep finds `phase`/`seq` on frontend task types, that is a sibling gap; stop and comment on AST-740 rather than patching UI here.

## Stage 4: QA handoff expectations (Betty — not engineer)

**Done when:** Betty's qa-child manifest covers updated assertions; engineer does not commit under `tests/`.

Document for Betty (Linear comment at Tests Ready if needed):

| Area | Expected bible/manifest update |
|------|--------------------------------|
| `tests/component/utils/test_config.py` | Remove or rewrite assertions on `TASK_CONFIG[*]["phase"]` / `["seq"]` (e.g. `TestAst520AnticipateScanTaskKey`, `TestAst504CompanySearchTermsConfig`, `TestAst505InflowDiscoveryConfig::test_vet_inflow_discovery_task`) — replace with checks that keys are absent or that `JOB_ARTIFACT_ENTRY_TASK_KEYS` membership is correct |
| `tests/component/ui/api/test_api_admin.py` | Replace `consult_do` phase/seq assertions with DB grouping fields; drop `phase`/`seq` expectations on list/get task payloads |
| `tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx`, `test_AdminScheduledActions.test.tsx` | AST-739 owns; Betty aligns if AST-740 merge exposes stale mocks |

Engineer runs product grep gates in Stage 3 only; full test green is **test-child** after Betty manifest.

## Self-Assessment

**Scope:** `Single-Component` — Two product files (`config.py`, `consult.py`) plus verification greps; no schema, dispatcher, or frontend changes.

**Conf:** `Medium` — Straightforward key removal, but pre-build gate depends on sibling merges and the explicit `JOB_ARTIFACT_ENTRY_TASK_KEYS` set must exactly match today's phase-derived membership.

**Risk:** `Medium` — Wrong frozenset membership would mis-route artifact dispatch hops; removing config keys before AST-739 lands would blank admin grouping.

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Reuses single `JOB_ARTIFACT_ENTRY_TASK_KEYS` constant; no duplicate frozenset in consult. |
| §2.1 config | Removes UI grouping from `TASK_CONFIG`; execution hop set stays an explicit config literal (not env, not DB). |
| §2.6 state machine | No state transition changes. |
| §3.3 imports | consult imports constant from utils only. |
| §3.5 naming | Constant name documents purpose; no new modules. |
| §1.5 logging | No new logging. |

No conflicts requiring `conf-!!-NONE`.

## Execution contract

Follow **build-child** stage commits on epic worktree; publish each `code(AST-740)` to `origin/sub/AST-734/AST-740-remove-phase-and-seq-from-task-config`. Blocking ambiguity → `🛑 Stage N blocked:` comment on [AST-734](https://linear.app/astralcareermatch/issue/AST-734/organizing-tasks) parent with step, issue, and options. Do not edit `tests/`, frontend pages, or database seed/migration.

## Review stub

**Built:** `origin/sub/AST-734/AST-740-remove-phase-and-seq-from-task-config` @ `1fb8582`

**Product:** Removed all `phase`/`seq` from `TASK_CONFIG`; added `JOB_ARTIFACT_ENTRY_TASK_KEYS`; consult routes artifact hops via explicit frozenset; dropped backward-compat `phase`/`seq` from `_grouping_from_agent_task_row`.

**Tests:** Betty — update `test_config.py` / `test_api_admin.py` phase/seq assertions per Stage 4 table.

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-734/AST-740-remove-phase-and-seq-from-task-config` @ `b12ed93` (publish tip includes sibling AST-738/739 + Betty manifests; AST-740 product delta = `1fb8582`).

### What's solid

| Lens | Result |
|------|--------|
| Plan fidelity | Stages 1–3 complete: `JOB_ARTIFACT_ENTRY_TASK_KEYS` frozenset (9 keys, excludes `draft_cover_letter`); all `phase`/`seq` removed from `TASK_CONFIG`; `consult.py` imports constant at module top; `_grouping_from_agent_task_row` drops backward-compat `phase`/`seq` per Stage 3. |
| §2.1 config | UI grouping excised from config; execution hop set is explicit literal in `config.py`. |
| §3.3 layers | `consult.py` → `utils.config` only for the new constant. |
| Stage 3 greps | Zero `cfg.get("phase")` / `cfg.get("seq")` reads under `src/`; no `phase`/`seq` inside `TASK_CONFIG` entries. |
| Tests | `TestAst740RemoveConfigGrouping` + `TestAst740NoConfigPhaseSeqInApi` green on publish tip. |

### Issues

None (**fix-now** / **discuss**).

### Advisory

- `scripts/migrations/backfill_task_grouping_metadata.py` still reads `TASK_CONFIG` `phase`/`seq` for one-time seed — after AST-740, fresh catalog inserts default to `(unassigned)` / `999.0` (Betty revised `TestAst738TaskGroupingMetadata` accordingly). Expected post-epic; new catalog keys added after deploy need admin grouping edits.
- `JOB_ARTIFACT_ENTRY_TASK_KEYS` lives after the `TASK_CONFIG` dict (not inline before `anticipate_scan` as plan sketch showed) — functionally correct and cleaner.

## Resolution

**2026-06-18** — Radia review @ `0a0e0c7`: **no fix-now or discuss items.** No product changes required.

§9a dry-run: `origin/sub/AST-734/AST-740-remove-phase-and-seq-from-task-config` merges cleanly into `origin/dev` and `origin/ftr/AST-734-organizing-tasks`.

**Shipped:** `JOB_ARTIFACT_ENTRY_TASK_KEYS` frozenset; all `phase`/`seq` removed from `TASK_CONFIG`; consult artifact-hop routing via constant; backward-compat `phase`/`seq` dropped from `_grouping_from_agent_task_row`. Betty manifest green @ `b12ed93`.
