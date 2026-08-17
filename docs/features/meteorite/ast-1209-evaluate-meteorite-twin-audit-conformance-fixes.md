<!-- linear-archive: AST-1209 archived 2026-08-17 -->

## Linear archive (AST-1209)

**Archived:** 2026-08-17  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1209/evaluate-meteorite-twin-audit-conformance-fixes-evaluate-meteorite  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1186 — evaluate_meteorite: fold recent work into tests + statute/pattern check  
**Blocked by / blocks / related:** parent: AST-1186; blocks: AST-1211; blocks: AST-1210

### Description

## What this implements

Owns inventory of the live twin contract vs Architectural definition (config, consult, dispatch, and evaluate_meteorite-related UI), and any narrow product fixes required for pass. Posts the audit pass/drift/defect list. Does **not** own bible/component fold-in (sibling #2) or fixture re-baseline (sibling #3).

## In scope

- [X] `pattern.config.config-block` — twin orchestration, dispatch specs, rubric ownership, Analysis-JD override stay config-owned
- [X] `pattern.batch.entity-claim-process-release` — evaluate hop keeps claim → process → release; retirement does not invent a new claim shape
- [X] `pattern.state.entity-state-transitions` — **METEORITE_PASSED_JD** / **METEORITE_FAILED_JD** / **METEORITE_ERROR_EVALUATE_JD** / **METEORITE_QUALIFIED_RETRY** stay registry-true
- [X] `astral.config.config-source-of-truth` — twin states, artifact keys, dispatch specs, Analysis override live in config
- [X] `astral.config.pass-threshold-vs-score-floor` — GDL entry remains ungated (`score_floor` None); no scored not_ready → score-floor coupling on **METEORITE_QUALIFIED**
- [X] `astral.patterns.render-verdict-orchestrates-consult` — incomplete vectors → retry holding, not technical fail
- [X] `astral.layers.ui-config-driven-business-logic` — Meteorite Criteria / craft path binds twin artifact/owner via config keys
- [X] `astral.standards.in-scope-only` — audit + narrow conformance only; no sibling bible/fixture/alias/gaze scope

## Considered but excluded

- [X] `astral.standards.debug-contract-gated` — only if a `debug=` evaluate path is edited for a product-defect; Style D then required. Not a default Stage 2 touch.
- [X] `astral.standards.no-hardcoded-sets` — sibling bible/component lock (AST-1210); this child uses existing `METEORITE_` prefix for retirement only
- [X] `astral.batch.claim-process-release` — duplicate of pattern.batch citation; claim/clear unchanged beyond stale-row delete
- [X] `astral.seed.agent-tables-in-repo-json` — fixture lockstep is AST-1211
- [X] `pattern.layers.import-discipline` — no new cross-layer imports planned; dispatcher already calls existing delete helper
- [X] `astral.state.job-prior-states-enforced` / `astral.state.core-decides-transitions` / `astral.agent.do-task-delegation` — twin already on registry + consult path; no transition redesign
- [X] qualify_meteorite, gaze_email, aliases (AST-1184), Gaze/Meteorite Review grouping (AST-1183), general UI hardcode audit (AST-1185), `meteorite_email` rename (AST-1182) — parent Boundaries / adjacent Discussion

## Acceptance criteria

- [X] A written audit (Linear comment or plan attachment on the child) lists the evaluate_meteorite contract points checked against the Architectural definition, each marked pass / bible-drift / product-defect.
- [X] After the epic, `evaluate_jd` is **not** the meteorite GDL entry key in config or live provisioned meteorite dispatch rows; `evaluate_meteorite` claims **METEORITE_QUALIFIED** (ungated).
- [X] `TASK_CONFIG["evaluate_meteorite"]` owns meteorite JD pass/fail/error directly; `evaluate_jd` is absent from `METEORITE_GDL_OUTCOME_BY_TASK`.
- [X] Analysis-JD for meteorite-sourced jobs resolves to `meteorite_jobdesc_rubric` / owner `evaluate_meteorite`, not classic `jobdesc_rubric` / `evaluate_jd`.
- [X] Incomplete/extra grade vectors on the meteorite evaluate hop land on **METEORITE_QUALIFIED_RETRY** (or the live retry holding for that trigger), never **METEORITE_ERROR_EVALUATE_JD** as a completeness misclassify.
- [X] Evaluate_meteorite-related UI (Meteorite Criteria / craft path) binds to the twin artifact/owner, not classic evaluate_jd ownership.
- [X] Classic `evaluate_jd` @ **JD_READY** behavior and non-meteorite Analysis-JD ownership remain unchanged.
- [X] If backend `debug=` evaluate paths are touched: Style D index headers show found/recorded detail; no new ungated debug noise.

## Boundaries

Does **not** own bible/component fold-in (sibling #2 / AST-1210) or fixture re-baseline (sibling #3 / AST-1211). Does **not** invent aliases, rename meteorite_email, or change qualify/gaze paths.

## Notes for planning

Parent: AST-1186. Twin audit + conformance only.

## Git branch (authoritative)

`origin/sub/AST-1186/AST-1209-evaluate-meteorite-twin-audit-conformance-fixes`

### Comments

#### radia — 2026-08-06T06:01:07.620Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1209
**Publish ref:** `origin/sub/AST-1186/AST-1209-evaluate-meteorite-twin-audit-conformance-fixes` @ `6f016bee`
**Overall:** DISCUSS

## Plan adherence
- Diff matches the plan's Stage 2 exactly: `ensure_meteorite_dispatch_tasks` retires `evaluate_jd`@`METEORITE_*` (NEW + QUALIFIED) only when the `evaluate_meteorite`@`METEORITE_QUALIFIED` twin row is present or was just inserted; `evaluate_jd`@`JD_READY` untouched. Stage 3 is a documented no-op — confirmed no `config.py`/`consult.py`/`ArtifactsMeteoriteCriteria.tsx` changes in the diff, matching the audit's point 1–9/12 `pass` marks.
- Commit-role separation clean: `code(AST-1209)` (`261fa01a`) touches `src/core/dispatcher.py` only; `test(AST-1209)` + one `merge-tests(AST-1209)` SHA land Betty's `tests/` + `docs/test-bible/**` only; `docs(AST-1209)` commits touch only the plan file. Sub stacks on `origin/ftr/AST-1186` on `origin/dev`.
- Self-Assessment (Scope: Single-Component, Conf: high, Risk: Medium) matches the diff's real footprint — one product file, dispatch claim surface.

Full active statute corpus (65 leaves — 19 universal + 46 scoped) scored in-session: zero fix-now, one needs-discussion (below). Ten not-applicable on layer/path predicates (`astral.debug.no-repo-root-artifacts-dir`, `astral.layers.scripts-exempt-from-layer-rules`, `astral.layers.ui-config-driven-business-logic`, `astral.patterns.require-auth-on-protected-endpoints`, `astral.seed.agent-tables-in-repo-json`, `astral.standards.database-header-inventory`, `astral.standards.utils-data-late-import-only`, `astral.ui.frontend-file-placement`, `astral.ui.naming-conventions`, `astral.ui.single-gunicorn-worker` — no matching diff paths). `astral.standards.no-hardcoded-sets` / `astral.dispatch.run-next-is-chain-authority` verified conforms independently: grepped `JOB_STATES` in `src/utils/config.py` — every meteorite state uses the `METEORITE_` prefix and `JD_READY` does not, so `ts.startswith("METEORITE_")` is a state-family match, not an invented parallel set.

**needs-discussion — mid-flight claim release on retirement.** `ensure_meteorite_dispatch_tasks` deletes the live `evaluate_jd`@`METEORITE_*` claim row via `delete_dispatch_task` with no `job.batch_id` release step (`astral.batch.claim-process-release` / `pattern.batch.entity-claim-process-release`). The `twin_present` guard (addressing Joan finding #3) stops an orphaned `METEORITE_QUALIFIED` with no claim row, but there is no code-level guard against retiring a row with in-flight claims — the docstring's "call when idle" and the audit comment's operator note are the only mitigation. This independently converges with Joan's plan-rubric finding #2. Acceptable given `auto_mode` is `False` on every meteorite row (operator/CLICK-driven per `astral.dispatch.seed-auto-false`, narrow window) and Joan already routed it to the builder as fold-in, not fix-now — flagging for visibility only, not blocking.

**Cross-ticket carry-over noted, not counted against this diff:** the `merge-tests(AST-1209)` commit also carries `test(AST-1206): contact debug flag foundation coverage` (already Radia-reviewed clean under AST-1206, not yet on `origin/dev`) — the contact/config/api_contact test + bible files in the three-dot diff are that carry-over, not AST-1209 scope. `astral.standards.in-scope-only` conforms on the actual `src/**` footprint (`dispatcher.py` only).

**Pattern conformance:** `pattern.config.config-block`, `pattern.state.entity-state-transitions` cited — conforms (no config/consult/state-transition edits this diff). `pattern.batch.entity-claim-process-release` — needs-discussion above.

## Frame diff
(none) — description AC/Boundaries/In-scope/Excluded checkboxes already reflect the shipped diff; no plan-time exclusions are stragglers (Joan's plan-rubric comment states a `Considered` scope, not a distinct Excluded attachment — noted under Notes, not a C4 block).

**What's solid:** `twin_present` guard is a real improvement over the plan's literal snippet — it also covers the case where `evaluate_meteorite` is missing from `TASK_CONFIG` (Joan finding #3), which the plan only flagged as a future-regression risk. Test coverage (`test_ensure_retires_evaluate_jd_on_meteorite_triggers_when_twin_present`, `test_ensure_skips_retire_when_twin_absent`) exercises both branches directly.

context_tokens≈68000

— Radia

#### betty — 2026-08-06T05:50:07.630Z
## QA test manifest (AST-1209)

**Publish:** `origin/sub/AST-1186/AST-1209-evaluate-meteorite-twin-audit-conformance-fixes` @ `224de458`
**merge-tests:** `origin/tests` `0d926c0887a6022b1e1e8bffcbb6459ea769a9cd`

### Classification

1. **Existing coverage (revised this pass):** `tests/component/core/test_dispatcher.py::TestAst1054MeteoriteDispatchProvision` — twin GDL insert is `evaluate_meteorite`@`METEORITE_QUALIFIED`; retirement covers all `evaluate_jd`@`METEORITE_*` when twin present; keeps `@JD_READY`; skips retire when twin absent from `TASK_CONFIG`; scheduler meteorite provision stub no longer assumes stage provision.
2. **Broken / obsolete (revised):** AST-1060 NEW-only retire + insert-as-`evaluate_jd` asserts; obsolete `provision_candidate_stage_dispatch_tasks` stub on meteorite start_scheduler test.
3. **Gaps deferred to siblings:** full twin bible/config/consult lock (config.md / consult.md still document `evaluate_jd`@`METEORITE_QUALIFIED` / overlay for JD) → **AST-1210**; fixture lockstep → **AST-1211**. No new integration scenarios.

### Run

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_dispatcher.py::TestAst1054MeteoriteDispatchProvision \
  -q
```

### Bible verify

`docs/test-bible/core/dispatcher.md` on publish-ref sha256 `be8cd00a054e652106d0fb46b3ce7a80606332a4`

— Betty

#### ada — 2026-08-06T05:45:55.089Z
Stage 3: no product defects beyond Stage 2 (or none at all)

#### ada — 2026-08-06T05:45:28.240Z
## Twin audit (AST-1209)

| # | Point | Mark | Evidence |
|---|-------|------|----------|
| 1 | GDL entry key is `evaluate_meteorite` in `METEORITE_DISPATCH_TASKS` + seed SQL | pass | `config.py` `METEORITE_DISPATCH_TASKS` task_key `evaluate_meteorite`; `SEED_CONFIG["dispatch_task-meteorite"]` inserts `evaluate_meteorite`@`METEORITE_QUALIFIED`; `evaluate_jd` absent from both |
| 2 | Claims **METEORITE_QUALIFIED**, `score_floor` None | pass | Dispatch row `trigger_state`/`score_floor`; `_dispatch_trigger_state_for_task_key("evaluate_meteorite")` → `METEORITE_QUALIFIED` |
| 3 | `TASK_CONFIG["evaluate_meteorite"]` owns pass/fail/error + rubric | pass | `METEORITE_PASSED_JD` / `METEORITE_FAILED_JD` / `METEORITE_ERROR_EVALUATE_JD` / `meteorite_jobdesc_rubric`; no `not_ready_state` |
| 4 | `evaluate_jd` absent from `METEORITE_GDL_OUTCOME_BY_TASK` | pass | Overlay keys: `grade_do`, `grade_get` only |
| 5 | Analysis-JD meteorite override | pass | `JOB_TOKEN_CONFIG["analysis_phases_meteorite_override"]["ANALYSIS_JD"]` → `meteorite_jobdesc_rubric` / `evaluate_meteorite`; merged in `_format_analysis_phase_text` (`consult.py`) |
| 6 | Incomplete → **METEORITE_QUALIFIED_RETRY** | pass | `JOB_STATES["METEORITE_QUALIFIED"]["retry_state"]`; `IncompleteGradeSetError` → `_consult_batch_fail_dest` |
| 7 | Rubric/craft ownership maps | pass | `RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY["meteorite_jobdesc_rubric"]`=`evaluate_meteorite`; craft → same artifact |
| 8 | Meteorite Criteria UI twin bind | pass | `ArtifactsMeteoriteCriteria.tsx`: `meteorite_jobdesc_rubric` + `craft_evaluate_meteorite_rubric` |
| 9 | Classic `evaluate_jd`@**JD_READY** unchanged | pass | `_dispatch_trigger_state_for_task_key("evaluate_jd")`→`JD_READY`; Analysis-JD still `jobdesc_rubric`/`evaluate_jd` |
| 10 | Live provision retires all `evaluate_jd`@`METEORITE_*` | product-defect | `dispatcher.py` still `ts == "METEORITE_NEW"` only — `@METEORITE_QUALIFIED` survives → **Stage 2** |
| 11 | Bible still documents `evaluate_jd`@**METEORITE_QUALIFIED** / overlay | bible-drift | `docs/test-bible/utils/config.md` (~1174, ~1280); `docs/test-bible/core/consult.md` overlay note → **AST-1210** |
| 12 | Statutes (config SoT, ungated entry, claim→release, incomplete→retry, UI config-driven) | pass | Twin in config; entry `score_floor` None; retirement does not invent claim shape; retry_state wired; UI presentational |

**In-flight claims (Joan discuss #2):** This epic worktree has no live candidate DB to inspect. Meteorite dispatch rows are `auto_mode` False — Stage 2 retirement must be provisioned when the meteorite evaluate hop is idle (no mid-flight `evaluate_jd`@`METEORITE_*` batch). Operators: run `provision_meteorite_dispatch_tasks` only then.

Product defects → Stage 2. Bible-drift → AST-1210 (out of scope here).

#### joan — 2026-08-06T05:43:04.867Z
[plan-rubric] revision=1

**Rubric:** plan-rubric.v1
**Ticket:** AST-1209
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1186/AST-1209-evaluate-meteorite-twin-audit-conformance-fixes` @ `3a6ac6c1`

## Traceability

AC1→S1; AC2→S1(config half)+S2(live rows); AC3→S1(+S3 if defect); AC4→S1(+S3); AC5→S1(+S3); AC6→S1(+S3); AC7→S2+S3 guard; AC8→S3. No unmapped AC, no orphan stage.

**Considered:** all universal active statutes + the 8 scoped citations from the parent Architectural definition; scored in-session. One `needs-discussion` (claim-process-release, finding 2); all others conform.

## Pre-survey re-verified independently

I checked the plan's Stage 1 pre-survey against the worktree tip rather than trusting it:

- Point 2/3 pass — `METEORITE_DISPATCH_TASKS` has `evaluate_meteorite`@`METEORITE_QUALIFIED` with `score_floor` `None`; `TASK_CONFIG["evaluate_meteorite"]` owns `METEORITE_PASSED_JD` / `METEORITE_FAILED_JD` / `METEORITE_ERROR_EVALUATE_JD` / `meteorite_jobdesc_rubric` directly. The shipped comment there already documents why no `not_ready_state` is set (`_TRANSITION_STATES_USED_BY_SCORED_TASKS` → `dispatch_claim_uses_score_floor`), which is exactly the coupling `astral.config.pass-threshold-vs-score-floor` forbids.
- Point 4 pass — `METEORITE_GDL_OUTCOME_BY_TASK` holds only `grade_do` / `grade_get`.
- Point 5 pass — `analysis_phases_meteorite_override["ANALYSIS_JD"]` → `meteorite_jobdesc_rubric` / `evaluate_meteorite`, merged in `_format_analysis_phase_text` (`consult.py:812`).
- Point 6 pass — `JOB_STATES["METEORITE_QUALIFIED"]["retry_state"]` is `METEORITE_QUALIFIED_RETRY`, and `METEORITE_PASSED_JD` / `FAILED_JD` / `ERROR_EVALUATE_JD` all accept the retry state as prior, so the holding is registry-true.
- Point 8 pass — `ArtifactsMeteoriteCriteria.tsx` is four lines that pass `meteorite_jobdesc_rubric` / `craft_evaluate_meteorite_rubric` into `ArtifactEditor`; presentational, config-keyed.
- Point 10 defect confirmed — `dispatcher.py:200` is `if tk == "evaluate_jd" and ts == "METEORITE_NEW":`, so live `evaluate_jd`@`METEORITE_QUALIFIED` rows do survive provision. The plan's replacement snippet drops in literally: the retirement loop's locals really are `tk` / `ts` (`:198–199`), and the insert loop genuinely runs first (`:175–194`), so the twin row exists before the classic row is deleted.

Every helper the plan cites by name exists at the cited path (`_dispatch_trigger_state_for_task_key`, `_consult_batch_fail_dest`, `IncompleteGradeSetError`, `evaluate_meteorite_batch`). `"JD_READY".startswith("METEORITE_")` is false, so AC7's classic track is safe by construction.

## Findings

**1. discuss — Stage 2 has no observable check for the live-rows half of AC2.**
AC2 asserts `evaluate_jd` is gone from *live provisioned* dispatch rows, but the retirement is only visible through the `retired` counter or direct DB inspection, and this child cannot write tests (AST-1210 owns that). Suggest one Manual Verify line in Stage 2: run `provision_meteorite_dispatch_tasks`, confirm `retired` > 0, `evaluate_meteorite`@`METEORITE_QUALIFIED` present, and `evaluate_jd`@`JD_READY` still present.

**2. discuss — retirement now deletes a claim row on an *active* trigger, with no batch release.**
The `METEORITE_NEW` row this code deletes today is dead; `evaluate_jd`@`METEORITE_QUALIFIED` is the row that has actually been claiming meteorite jobs. `delete_dispatch_task` removes the row but nothing clears `job.batch_id`, so a mid-flight batch would leave jobs claimed with no row to release them (`pattern.batch.entity-claim-process-release`). Every meteorite row is `auto_mode` False, so provision is operator-driven and the window is small — but Stage 1 is the right place to record whether any live `evaluate_jd`@`METEORITE_*` row has in-flight claims, and Stage 2 should say provision runs when that hop is idle.

**3. discuss — the delete is unconditional on the twin insert having succeeded.**
The insert loop skips silently via `skipped_missing_config` when a `METEORITE_DISPATCH_TASKS` key is absent from `TASK_CONFIG`, and there is no assert tying those two together. `evaluate_meteorite` is present today, so this is not a live bug — but as written, a future config regression would strip the classic row and leave `METEORITE_QUALIFIED` with no claim row at all. Cheap guard: retire only when the twin row is present in `existing` or was just added.

**4. acceptable.**
`ts.startswith("METEORITE_")` over a second equality or a hard-coded trigger pair — the state-name family is already the config-owned set, so this avoids a parallel map in `dispatcher` (`astral.standards.no-hardcoded-sets`). Audit posted as a child Linear comment rather than a second `docs/features/` file — parent AC allows the comment form and the plan is right to refuse a second artifact. Conditional Files Changed rows and the documented Stage 3 no-op are honest scoping, not hedging; the escape hatch to parent AST-1186 for out-of-Files-Changed defects keeps `astral.standards.in-scope-only` intact.

No `fix-now`. Cleared for build; findings 1–3 are for the builder to fold in as they go.

— Joan

context_tokens≈116000

#### ada — 2026-08-06T05:37:49.809Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-1186/AST-1209-evaluate-meteorite-twin-audit-conformance-fixes/docs/features/meteorite/ast-1209-evaluate-meteorite-twin-audit-conformance-fixes.md

`origin/sub/AST-1186/AST-1209-evaluate-meteorite-twin-audit-conformance-fixes` @ `3a6ac6c1`

**Scope:** Single-Component — dispatcher live-claim retirement is the expected product delta; config/consult/UI only if audit marks defects (pre-survey: those already pass).

**Conf:** high — twin already lives in TASK_CONFIG / consult / UI; open gap is retirement still only deleting `evaluate_jd`@`METEORITE_NEW`, not `@METEORITE_QUALIFIED`.

**Risk:** Medium — dispatch claim surface is critical; retirement is scoped to `evaluate_jd` + `METEORITE_*` triggers so classic `@JD_READY` stays.

---

# AST-1209 — evaluate_meteorite twin audit + conformance fixes

**Linear:** [AST-1209](https://linear.app/astralcareermatch/issue/AST-1209/evaluate-meteorite-twin-audit-conformance-fixes-evaluate-meteorite)
**Parent:** [AST-1186](https://linear.app/astralcareermatch/issue/AST-1186/evaluate-meteorite-fold-recent-work-into-tests-statutepattern-check) — evaluate_meteorite: fold recent work into tests + statute/pattern check
**Publish ref:** `origin/sub/AST-1186/AST-1209-evaluate-meteorite-twin-audit-conformance-fixes`

Inventory the live `evaluate_meteorite` twin contract (config, consult, dispatch, evaluate_meteorite-related UI) against the parent Architectural definition; post a written pass / bible-drift / product-defect audit; apply **narrow** product conformance fixes so meteorite GDL entry is the twin (not classic `evaluate_jd`). Does **not** own bible/component fold-in (AST-1210) or AST-756 fixture lockstep (AST-1211).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/dispatcher.py` | Extend `ensure_meteorite_dispatch_tasks` retirement so live meteorite claim rows never leave `evaluate_jd` on any `METEORITE_*` trigger (keep `evaluate_jd`@`JD_READY`); docstring honesty | core |
| `src/utils/config.py` | **Only if Stage 1 marks a product-defect here** — restore twin ownership / ungated entry / Analysis override / overlay absence to match Architectural definition. Pre-survey expects no change. | utils |
| `src/core/consult.py` | **Only if Stage 1 marks a product-defect here** — twin batch routing, incomplete→retry holding, Analysis-JD meteorite override, Style D on touched `debug=` evaluate paths. Pre-survey expects no change. | core |
| `src/ui/frontend/src/pages/ArtifactsMeteoriteCriteria.tsx` | **Only if Stage 1 marks a product-defect here** — bind Meteorite Criteria to `meteorite_jobdesc_rubric` + `craft_evaluate_meteorite_rubric`. Pre-survey expects no change. | ui |

No `tests/`, no `docs/test-bible/**`, no fixture/catalog rows (siblings AST-1210 / AST-1211). No `qualify_meteorite`, gaze, aliases, `meteorite_email` rename, or classic `evaluate_jd`@`JD_READY` behavior changes.

## Stage 1: Written twin-contract audit

**Done when:** A Linear comment on **AST-1209** lists every contract point below with exactly one mark — `pass` / `bible-drift` / `product-defect` — and cites the evidence path (config key, function, or bible file). Product-defect rows name the planned fix stage (Stage 2 or Stage 3). Bible-drift rows name sibling AST-1210 and do **not** edit bible here.

Re-verify each point on the epic worktree tip (do not trust this plan’s pre-survey alone). For each row, record the mark and one evidence line.

| # | Contract point (Architectural / AC) | How to verify |
|---|-------------------------------------|---------------|
| 1 | Meteorite GDL entry task key is `evaluate_meteorite`, not `evaluate_jd`, in `METEORITE_DISPATCH_TASKS` and `SEED_CONFIG["dispatch_task-meteorite"]` | Grep / read those blocks in `src/utils/config.py` |
| 2 | `evaluate_meteorite` claims **METEORITE_QUALIFIED** with `score_floor` `None` (ungated) | `METEORITE_DISPATCH_TASKS` row + `_dispatch_trigger_state_for_task_key("evaluate_meteorite")` |
| 3 | `TASK_CONFIG["evaluate_meteorite"]` owns `pass_state` / `fail_state` / `error_state` / `rubric_artifact` directly (`METEORITE_PASSED_JD` / `METEORITE_FAILED_JD` / `METEORITE_ERROR_EVALUATE_JD` / `meteorite_jobdesc_rubric`) | Read `TASK_CONFIG` row |
| 4 | `evaluate_jd` is **absent** from `METEORITE_GDL_OUTCOME_BY_TASK` (DO/GET overlay only) | Read overlay dict |
| 5 | Analysis-JD meteorite override → `meteorite_jobdesc_rubric` / owner `evaluate_meteorite` | `JOB_TOKEN_CONFIG["analysis_phases_meteorite_override"]` + `_format_analysis_phase_text` meteorite merge |
| 6 | Incomplete/extra grade vectors on meteorite evaluate hop → **METEORITE_QUALIFIED_RETRY** (via `JOB_STATES["METEORITE_QUALIFIED"]["retry_state"]` + `_consult_batch_fail_dest`), never first-touch **METEORITE_ERROR_EVALUATE_JD** as completeness misclassify | `JOB_STATES` + `IncompleteGradeSetError` path in `consult.py` |
| 7 | Rubric / craft ownership maps bind meteorite twin (`RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY`, `CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY`) | Read maps in `config.py` |
| 8 | Evaluate_meteorite-related UI (Meteorite Criteria) binds twin artifact/craft keys, not classic `jobdesc_rubric` / `craft_jobdesc_rubric` | `ArtifactsMeteoriteCriteria.tsx` + route |
| 9 | Classic `evaluate_jd`@**JD_READY** and non-meteorite Analysis-JD (`jobdesc_rubric` / `evaluate_jd`) unchanged | `TASK_CONFIG["evaluate_jd"]`, `_dispatch_trigger_state_for_task_key("evaluate_jd")`, `JOB_TOKEN_CONFIG["analysis_phases"]` |
| 10 | Live provision retirement: `ensure_meteorite_dispatch_tasks` removes stale meteorite `evaluate_jd` claim rows (not only `@METEORITE_NEW`) so live rows match twin | Read `src/core/dispatcher.py` retirement loop |
| 11 | Test bible still documenting meteorite entry as `evaluate_jd` overlay / `evaluate_jd`@**METEORITE_QUALIFIED** | Grep `docs/test-bible/**` (read-only; mark `bible-drift` only) |
| 12 | Pattern/statute check: config-owned twin; claim→process→release unchanged; pass_threshold vs score_floor (entry ungated); render-verdict incomplete→retry; UI config-driven | Cite evidence under each statute in the comment |

Comment format (required):

```
## Twin audit (AST-1209)

| # | Point | Mark | Evidence |
|---|-------|------|----------|
| 1 | … | pass \| bible-drift \| product-defect | … |

Product defects → Stage 2/3. Bible-drift → AST-1210 (out of scope here).
```

⚠️ **Decision — audit comment is the AC artifact:** Parent AC allows Linear comment or plan attachment; post on the **child** (AST-1209), not the parent. Do not invent a second audit file under `docs/features/`.

⚠️ **Decision — pre-survey baseline (must re-verify):** On current tip, points 1–9 look `pass` in product code; point 11 is `bible-drift` (sibling); point 10 is the expected `product-defect` — retirement still only deletes `evaluate_jd`@`METEORITE_NEW`, not `evaluate_jd`@`METEORITE_QUALIFIED` left by the AST-1060 era. If re-verification disagrees, the Linear marks win and Stage 2/3 follow those marks.

## Stage 2: Live dispatch retirement — no meteorite `evaluate_jd` claim rows

**Done when:** `ensure_meteorite_dispatch_tasks` still inserts missing `METEORITE_DISPATCH_TASKS` rows (including `evaluate_meteorite`@`METEORITE_QUALIFIED`), and after the scan deletes **every** candidate `dispatch_task` row where `task_key == "evaluate_jd"` and `trigger_state` starts with `METEORITE_` (covers `@METEORITE_NEW` and `@METEORITE_QUALIFIED`). `evaluate_jd`@`JD_READY` is never deleted. Docstring mentions both eras. No config/consult/UI edits in this stage unless Stage 1 marked them product-defect (then Stage 3).

1. In `src/core/dispatcher.py` `ensure_meteorite_dispatch_tasks`, keep the existing insert loop over `METEORITE_DISPATCH_TASKS` unchanged.

2. Replace the retirement condition that today matches only `evaluate_jd` + `METEORITE_NEW` with:

```python
# Twin contract (AST-1209): meteorite GDL entry is evaluate_meteorite@METEORITE_QUALIFIED.
# Retire any evaluate_jd row claiming a METEORITE_* trigger (AST-1060 NEW + QUALIFIED eras).
# Keep evaluate_jd@JD_READY (classic gazer track).
if tk == "evaluate_jd" and ts.startswith("METEORITE_"):
```

3. Update the function docstring from “retire stale evaluate_jd@METEORITE_NEW (AST-1060)” to mention AST-1209 twin retirement of all `evaluate_jd`@`METEORITE_*`.

4. Do **not** change `provision_meteorite_dispatch_tasks` beyond what already sums `retired` from `ensure_meteorite_dispatch_tasks`.

5. Do **not** delete or rewrite `evaluate_meteorite` rows; do **not** touch non-meteorite triggers.

⚠️ **Decision — prefix match on `METEORITE_`, not a hard-coded pair list:** AC requires `evaluate_jd` is not the meteorite GDL entry on live provisioned rows. Matching `ts.startswith("METEORITE_")` covers NEW + QUALIFIED and any future mistyped meteorite trigger without a second magic set in dispatcher (`astral.standards.no-hardcoded-sets` — trigger family already defined by state naming). Rejected: only adding `METEORITE_QUALIFIED` as a second equality — leaves other METEORITE_* evaluate_jd orphans possible.

**Skip Stage 2 only if** Stage 1 marks point 10 `pass` with evidence that retirement already covers all `evaluate_jd`@`METEORITE_*`. If skipped, say so in the Stage 2 Linear stage comment and make no dispatcher commit.

## Stage 3: Remaining product-defects (config / consult / UI) — only if Stage 1 marked them

**Done when:** Every Stage 1 `product-defect` outside point 10 is fixed in the matching file from Files Changed, **or** this stage is a documented no-op because Stage 1 had no such defects.

1. If Stage 1 has **no** product-defect marks on points 1–9 / 12 requiring config, consult, or UI: post a one-line Linear comment `Stage 3: no product defects beyond Stage 2 (or none at all)` and **do not** open those files. No empty commit.

2. If Stage 1 marks a product-defect in `src/utils/config.py`, `src/core/consult.py`, or `ArtifactsMeteoriteCriteria.tsx`: fix **only** that defect to restore the Architectural definition row for that point. Concrete restorations (use only the ones Stage 1 marked):

   - **Config twin ownership:** `TASK_CONFIG["evaluate_meteorite"]` pass/fail/error + `rubric_artifact`; remove `evaluate_jd` from `METEORITE_GDL_OUTCOME_BY_TASK` if present; `METEORITE_DISPATCH_TASKS` / seed SQL use `evaluate_meteorite`@`METEORITE_QUALIFIED` with `score_floor` `None`; `analysis_phases_meteorite_override` + rubric owner maps point at the twin.
   - **Consult:** `evaluate_meteorite_batch` / dispatch router call with `task_key="evaluate_meteorite"`; incomplete grades use `_consult_batch_fail_dest` (retry holding); `_format_analysis_phase_text` merges meteorite override; if a `debug=` evaluate path is edited, Style D index headers include found/recorded detail (`astral.standards.debug-contract-gated`) — no new ungated debug noise.
   - **UI:** `ArtifactsMeteoriteCriteria.tsx` keeps `artifactKey="meteorite_jobdesc_rubric"` and `taskKey="craft_evaluate_meteorite_rubric"` (never classic jobdesc craft keys).

3. If a product-defect requires a file **not** in Files Changed (e.g. qualify / gaze / alias / bible / fixture): **stop**, comment on Linear **parent AST-1186** with the Stage N blocked template, and wait. Do not absorb sibling scope.

⚠️ **Decision — classic evaluate_jd frozen:** Any Stage 3 edit must leave `evaluate_jd`@`JD_READY`, non-meteorite Analysis-JD (`jobdesc_rubric` / owner `evaluate_jd`), and vetted-company GDL outcomes unchanged. Verify those three after any config/consult touch.

## Self-Assessment

**Scope:** `Single-Component` — primary product change is dispatcher live-claim retirement; config/consult/UI only if audit finds defects (pre-survey expects pass there). Audit itself is documentation on Linear, not a second product surface.

**Conf:** `high` — twin already exists in TASK_CONFIG / consult / UI; the open conformance gap is a known retirement hole left from the AST-1060→twin transition, with a clear one-condition fix.

**Risk:** `Medium` — wrong retirement could delete `evaluate_jd`@`JD_READY` or fail to insert `evaluate_meteorite`; scoped `METEORITE_` prefix + insert-first order keeps classic track safe, but dispatch is claim-critical.

## Rules check (ASTRAL_CODE_RULES)

- §1.1 in-scope-only: bible/fixture/qualify/gaze/aliases excluded; sibling tickets named.
- §1.4 / `astral.standards.no-hardcoded-sets`: retirement uses existing `METEORITE_` state prefix family, not a parallel task-key map in dispatcher.
- §2.1 config-source-of-truth: twin orchestration stays in `TASK_CONFIG` / `METEORITE_DISPATCH_TASKS`; Stage 3 does not hardcode outcomes in consult.
- §2.1 pass_threshold vs score_floor: entry stays `score_floor` `None`; do not add `not_ready_state` that would score-gate **METEORITE_QUALIFIED**.
- §2.4 claim-process-release: no new claim shape; only retire stale rows.
- §2.6 / incomplete→retry: `astral.patterns.render-verdict-orchestrates-consult` — do not route incompleteness to `error_state` on first touch.
- §3.3 layers: dispatcher (core) may call data delete helpers already used; UI stays presentational.
- `astral.layers.ui-config-driven-business-logic`: Meteorite Criteria page only passes artifact/task keys into `ArtifactEditor`.
- Engineer must not edit `tests/` or `docs/test-bible/**`.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1186/AST-1209-evaluate-meteorite-twin-audit-conformance-fixes`
**Plan path:** `docs/features/meteorite/ast-1209-evaluate-meteorite-twin-audit-conformance-fixes.md`

**Built tip:** `261fa01a72a7cc02b58bd6f4cddef5c166b992d4` (`261fa01a`)

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | (Linear comment) | Twin audit table — point 10 product-defect; point 11 bible-drift → AST-1210 |
| 2 | `261fa01a` | `ensure_meteorite_dispatch_tasks`: retire `evaluate_jd`@`METEORITE_*` only when twin present; Manual Verify + idle-hop note in docstring |
| 3 | (no-op) | No config/consult/UI product defects |

---

## Radia review

[code-rubric] revision=1

| Field | Value |
|-------|-------|
| Rubric | code-rubric.v1 |
| Publish ref tip | `224de458b0c87aeffeb112a9eafcdb1b45b2954a` |
| Overall | DISCUSS |

Full active statute corpus (65 leaves — 19 universal + 46 scoped) scored in-session per the Full-set sweep algorithm against `git diff origin/dev...origin/sub/AST-1186/AST-1209-evaluate-meteorite-twin-audit-conformance-fixes`. Zero `violates`. One `needs-discussion` (`astral.batch.claim-process-release` — see below, converges independently with Joan's plan-rubric finding #2). Ten `not-applicable` on layer/path predicates (`astral.debug.no-repo-root-artifacts-dir`, `astral.layers.scripts-exempt-from-layer-rules`, `astral.layers.ui-config-driven-business-logic`, `astral.patterns.require-auth-on-protected-endpoints`, `astral.seed.agent-tables-in-repo-json`, `astral.standards.database-header-inventory`, `astral.standards.utils-data-late-import-only`, `astral.ui.frontend-file-placement`, `astral.ui.naming-conventions`, `astral.ui.single-gunicorn-worker` — no matching diff paths; the only product touch is `src/core/dispatcher.py`, plus a docs-only plan file and Betty's `test(AST-1209)` tests/bible commit). The rest score `conforms`.

**Needs-discussion — mid-flight claim release on retirement.** `ensure_meteorite_dispatch_tasks` deletes the live `evaluate_jd`@`METEORITE_*` claim row via `delete_dispatch_task` with no `job.batch_id` release step (`astral.batch.claim-process-release` / `pattern.batch.entity-claim-process-release`). The `twin_present` guard (addressing Joan finding #3) stops an orphaned `METEORITE_QUALIFIED` with no claim row, but there is still no code-level guard against retiring a row with in-flight claims — the docstring's "call when idle" and the Linear audit comment's operator note are the only mitigation. Acceptable given `auto_mode` is `False` on every meteorite row (operator/CLICK-driven, not scheduler-driven per `astral.dispatch.seed-auto-false`) so the window is narrow and Joan already routed this to the builder as fold-in, not fix-now — flagging for visibility only.

**Commit-role separation clean:** `code(AST-1209)` (`261fa01a`) touches `src/core/dispatcher.py` only; `test(AST-1209)` + one `merge-tests(AST-1209)` SHA land via Betty on `tests/` + `docs/test-bible/**` only (`astral.git.engineer-test-tree-ban` / `orch.git.betty-merge-tests-one-sha` conform). `docs(AST-1209)` commits touch only the plan file. Sub stacks cleanly on `origin/ftr/AST-1186` on `origin/dev` (`orch.git.merge-on-checkout` conforms).

**`METEORITE_` prefix check verified independently:** every state in `JOB_STATES` under the meteorite family uses the `METEORITE_` prefix (grepped `src/utils/config.py`), and `JD_READY` does not start with it — so `ts.startswith("METEORITE_")` retires the NEW+QUALIFIED eras without touching classic `evaluate_jd`@`JD_READY`, confirming `astral.standards.no-hardcoded-sets` / `astral.dispatch.run-next-is-chain-authority` conform (state family match, not an invented parallel set).

**Cross-ticket carry-over noted, not counted against this diff:** the `merge-tests(AST-1209)` commit also carries `test(AST-1206): contact debug flag foundation coverage` (already Radia-reviewed clean under AST-1206, not yet on `origin/dev`) — contact/config/api_contact test + bible files in the three-dot diff are that carry-over, not AST-1209 scope; `astral.standards.in-scope-only` conforms on the actual `src/**` footprint (`dispatcher.py` only).

**Pattern conformance:** `pattern.config.config-block`, `pattern.batch.entity-claim-process-release`, `pattern.state.entity-state-transitions` cited in the ticket — first and third conform (no config/consult/state-transition edits this diff); second is the needs-discussion above.

**Notes:** No formal Joan-Excluded-list straggler check triggered — Joan's plan-rubric comment states a `Considered` scope (universal + 8 parent-cited scoped statutes), not a distinct Excluded attachment; the ticket description's own "Considered but excluded" section is definition-time scoping, not a C4 artifact. Joan's plan-rubric `needs-discussion` (finding 2, claim-process-release) is the same item this independent full-sweep lands on.

context_tokens≈62000

— Radia

## Resolution

**Date:** 2026-08-06  
**Review tip:** `6f016bee` (Radia docs) · product tip `261fa01a`

| Item | Disposition |
|------|-------------|
| Fix-now | none |
| Discuss — mid-flight claim release on retirement | **Accepted as documented.** No product change. Mitigation remains: docstring + Stage 1 audit require `provision_meteorite_dispatch_tasks` only when the meteorite evaluate hop is idle; every meteorite `METEORITE_DISPATCH_TASKS` row is `auto_mode` False (`astral.dispatch.seed-auto-false`). Matches Joan fold-in #2 and Radia “visibility only / not blocking.” Adding a code-level batch clear would expand claim-process-release into provision — out of this child’s Files Changed. |
| Advisory | none |

No `src/` delta on resolve. `twin_present` guard and `METEORITE_*` retirement from Stage 2 stand.
