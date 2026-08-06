# AST-1210 — Bible + component tests lock twin contract

**Linear:** [AST-1210](https://linear.app/astralcareermatch/issue/AST-1210/bible-component-tests-lock-twin-contract-evaluate-meteorite-fold)
**Parent:** [AST-1186](https://linear.app/astralcareermatch/issue/AST-1186/evaluate-meteorite-fold-recent-work-into-tests-statutepattern-check) — evaluate_meteorite: fold recent work into tests + statute/pattern check
**Publish ref:** `origin/sub/AST-1186/AST-1210-bible-component-tests-lock-twin-contract`

Retire obsolete test-bible claims that meteorite GDL entry is `evaluate_jd` overlay / `evaluate_jd`@**METEORITE_QUALIFIED**, and extend component tests so the standalone `evaluate_meteorite` twin cannot regress (dispatch key+trigger, rubric ownership, Analysis-JD override, incomplete→retry). Product twin already passes per [AST-1209 twin audit](https://linear.app/astralcareermatch/issue/AST-1209#comment-4a411d25-a6f5-43ed-9289-959a868d407b) (points 1–9 / 12 `pass`; point 11 `bible-drift` → this child). Does **not** invent aliases, rewrite qualify paths, fix product (AST-1209), or re-baseline AST-756 fixtures (AST-1211).

## Files Changed (planned)

| File | Change | Layer | Owner |
|------|--------|-------|-------|
| *(none under `src/`)* | No product edits — twin + retirement already shipped on AST-1209 | — | Engineer confirms only |
| `docs/test-bible/utils/config.md` | Correct AST-1054 / AST-1060 prose that still says `evaluate_jd`@**METEORITE_QUALIFIED**; document twin GDL entry + ownership maps | bible | Betty (`qa-child`) |
| `docs/test-bible/core/consult.md` | Correct AST-1054 overlay note (`evaluate_jd` in overlay keys); add / point twin locks (`TestEvaluateMeteoriteStandaloneTwin`, Analysis override, incomplete→retry) | bible | Betty (`qa-child`) |
| `docs/test-bible/core/dispatcher.md` | Align pre-AST-1209 sections that still say NEW-only retire / insert-as-`evaluate_jd` with twin truth; keep AST-1209 section honest | bible | Betty (`qa-child`) |
| `tests/component/utils/test_config.py` | Fix `TestAst1054MeteoriteGdlDispatch` to assert `evaluate_meteorite`@**METEORITE_QUALIFIED**; add rubric/craft owner + Analysis override config locks | component | Betty (`qa-child`) |
| `tests/component/core/test_consult.py` | Extend twin locks: Analysis-JD meteorite override path; incomplete→retry using `evaluate_meteorite` error_state (not classic `evaluate_jd`) | component | Betty (`qa-child`) |
| `tests/component/core/test_dispatcher.py` | Keep AST-1209 twin provision/retire coverage when that tip is on the line; no new invent — revise only if sync leaves stale insert-as-`evaluate_jd` asserts | component | Betty (`qa-child`) |

No fixture/catalog rows (AST-1211). No `qualify_meteorite` / gaze / alias / UI product edits. No new integration scenarios.

## Prerequisite (before Stage 1 Done)

AST-1209 is **User Testing** and owns dispatcher retirement (`evaluate_jd`@`METEORITE_*` when twin present). This publish tip must include that product before Betty’s twin dispatch asserts can stay green.

1. Re-run `~/.cursor/scripts/git/sync-child.sh sub/AST-1186/AST-1210-bible-component-tests-lock-twin-contract --ftr AST-1186 --worktree /home/susan/astral-AST-1186/`.
2. **Done gate for product on tip:** `src/core/dispatcher.py` `ensure_meteorite_dispatch_tasks` retires with `ts.startswith("METEORITE_")` guarded by `twin_present` / `("evaluate_meteorite", "METEORITE_QUALIFIED")` (AST-1209 Stage 2), **not** the AST-1060 `ts == "METEORITE_NEW"` only loop.
3. If `origin/ftr/AST-1186` is still missing and the tip lacks that retirement: **stop**, comment on parent **AST-1186** with the Stage N blocked template asking Chuckles to `merge-child` AST-1209 onto ftr — **do not** cherry-pick sibling `sub/AST-1186/AST-1209-*`.

## Stage 1: Engineer — no product delta; Code Complete gate

**Done when:** Prerequisite gate above is green on this publish tip; working tree has **no** `src/` edits for AST-1210; Linear status is **Code Complete** with assignee still Hedy so Betty can run `qa-child` against the Files Changed table.

1. Confirm on tip (read-only): `METEORITE_DISPATCH_TASKS` GDL entry is `evaluate_meteorite`@`METEORITE_QUALIFIED` with `score_floor` `None`; `evaluate_jd` absent from `METEORITE_GDL_OUTCOME_BY_TASK`; `TASK_CONFIG["evaluate_meteorite"]` owns pass/fail/error + `meteorite_jobdesc_rubric`; Analysis override + rubric/craft maps match AST-1209 audit points 1–9.
2. Do **not** edit `src/`, `tests/`, or `docs/test-bible/**` in this stage (engineer test-tree ban).
3. If any audit point 1–9 has regressed to a product defect: **stop**, comment on parent AST-1186 — do not absorb AST-1209 scope.
4. Move ticket to **Code Complete** (keep assignee Hedy). Betty’s `qa-child` executes Stages 2–4 below from this plan.

⚠️ **Decision — engineer ships zero product:** Parent split puts audit/product on AST-1209 and bible/tests on this child. Code Complete with an empty `src/` diff is correct; the plan’s Files Changed are Betty’s commit surface.

## Stage 2: Betty — retire obsolete bible claims (twin truth)

**Owner:** Betty (`qa-child`). **Done when:** Grep of `docs/test-bible/**` finds no live claim that meteorite GDL entry is `evaluate_jd` overlay or `evaluate_jd`@**METEORITE_QUALIFIED**; corrected sections name `evaluate_meteorite` and point at the component classes below.

1. In `docs/test-bible/utils/config.md`:
   - **AST-1054** block (~1174): replace “**AST-1060** retargets `evaluate_jd` trigger to **METEORITE_QUALIFIED**” with twin truth — GDL entry task key is `evaluate_meteorite`@**METEORITE_QUALIFIED** (`score_floor` `None`); `evaluate_jd` is classic @**JD_READY** only; `METEORITE_GDL_OUTCOME_BY_TASK` is DO/GET overlay only (no `evaluate_jd`).
   - **AST-1060** block (~1280): replace “retargets meteorite `evaluate_jd` claim to **METEORITE_QUALIFIED**” the same way; keep qualify@**METEORITE_NEW** prose.
   - Table rows that still name `TestAst1054MeteoriteGdlDispatch` as “evaluate_jd trigger revised AST-1060” → twin key+trigger; mark old evaluate_jd@METEORITE_* insert asserts **Broken / obsolete** superseded by **AST-1210** (and AST-1209 for live retirement).
2. In `docs/test-bible/core/consult.md`:
   - **AST-1054** (~709): change overlay keys from ``(`evaluate_jd` / `grade_do` / `grade_get`)`` to ``(`grade_do` / `grade_get`)`` only; state JD stage is standalone twin `evaluate_meteorite` (see `TestEvaluateMeteoriteStandaloneTwin` / `test_evaluate_jd_has_no_meteorite_overlay`).
   - Add a short **AST-1210 · AST-1186** section (or extend AST-1054) listing Analysis-JD meteorite override + incomplete→**METEORITE_QUALIFIED_RETRY** locks and their test classes.
3. In `docs/test-bible/core/dispatcher.md`:
   - Pre-AST-1209 sections (~213 / ~235) that still say “surgical delete of `evaluate_jd`@`METEORITE_NEW`” / insert-as-`evaluate_jd`: mark **Broken / obsolete** or rewrite to twin + AST-1209 `METEORITE_*` retirement when twin present. Do not contradict the existing **AST-1209** section (~354+) once that tip is merged.
4. Do **not** invent new integration bible scenarios.

## Stage 3: Betty — component locks (dispatch, rubric, Analysis, incomplete→retry)

**Owner:** Betty (`qa-child`). **Done when:** The named asserts fail if the twin contract regresses; classic `evaluate_jd`@**JD_READY** and non-meteorite Analysis-JD remain asserted unchanged.

1. In `tests/component/utils/test_config.py` class `TestAst1054MeteoriteGdlDispatch.test_dispatch_row_specs_and_job_states`:
   - Remove asserts that `("evaluate_jd", "METEORITE_QUALIFIED")` is in `METEORITE_DISPATCH_TASKS`.
   - Assert `rows[("evaluate_meteorite", "METEORITE_QUALIFIED")]["score_floor"] is None`.
   - Keep `("evaluate_jd", "METEORITE_NEW") not in rows`.
   - In `test_score_floor_gating_and_trigger_defaults`: add `assert cfg._dispatch_trigger_state_for_task_key("evaluate_meteorite") == "METEORITE_QUALIFIED"` (keep existing `evaluate_jd` → `JD_READY`).
2. Same file — add focused asserts (new methods on this class or a small `TestAst1210EvaluateMeteoriteTwinConfig` class):
   - `RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY["meteorite_jobdesc_rubric"] == "evaluate_meteorite"`.
   - `CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY["craft_evaluate_meteorite_rubric"] == "meteorite_jobdesc_rubric"`.
   - `JOB_TOKEN_CONFIG["analysis_phases_meteorite_override"]["ANALYSIS_JD"]` has `rubric_artifact == "meteorite_jobdesc_rubric"` and `rubric_owner_task_key == "evaluate_meteorite"`.
   - `JOB_TOKEN_CONFIG["analysis_phases"]["ANALYSIS_JD"]` still owns classic `jobdesc_rubric` / `evaluate_jd` (non-meteorite unchanged).
   - `"evaluate_jd" not in cfg.METEORITE_GDL_OUTCOME_BY_TASK`.
3. In `tests/component/core/test_consult.py`:
   - Keep `TestEvaluateMeteoriteStandaloneTwin` and `test_evaluate_jd_has_no_meteorite_overlay` (already twin-true).
   - Add a test that meteorite-sourced Analysis-JD formatting uses the override: call `_format_analysis_phase_text("ANALYSIS_JD", …)` (or the smallest public helper that merges `analysis_phases_meteorite_override`) with a job marked meteorite-sourced the same way production does (`is_meteorite_company` / existing consult helper — **match the live branch in `consult.py`**, do not invent a new detection API). Assert the resolved phase cfg / owner is `evaluate_meteorite` + `meteorite_jobdesc_rubric`. Assert a non-meteorite job still resolves to `evaluate_jd` + `jobdesc_rubric`.
   - In `TestAst1155IncompleteGradeRetry.test_consult_batch_fail_dest_graded_triggers`: add (or replace the meteorite JD line that currently passes classic `jd_err = TASK_CONFIG["evaluate_jd"]["error_state"]`) asserts:
     - `_consult_batch_fail_dest("METEORITE_QUALIFIED", TASK_CONFIG["evaluate_meteorite"]["error_state"]) == "METEORITE_QUALIFIED_RETRY"`.
     - `_consult_batch_fail_dest("METEORITE_QUALIFIED_RETRY", TASK_CONFIG["evaluate_meteorite"]["error_state"]) == TASK_CONFIG["evaluate_meteorite"]["error_state"]` (**METEORITE_ERROR_EVALUATE_JD**), proving second strike is twin technical/error, not classic `ERROR_EVALUATE_JD`.
4. In `tests/component/core/test_dispatcher.py`: after Prerequisite merge, ensure `TestAst1054MeteoriteDispatchProvision` matches AST-1209 Betty coverage (`evaluate_meteorite` insert; retire all `evaluate_jd`@`METEORITE_*` when twin present; skip retire when twin absent; keep `@JD_READY`). If sync already brought `0d926c08` / equivalent asserts, do not duplicate — only fix leftover insert-as-`evaluate_jd` stubs if any remain on tip.

⚠️ **Decision — no new Style D product instrumentation:** AC Style D applies only if backend `debug=` evaluate paths are touched. This child does not touch `src/`. Do **not** add Style D string tests “for completeness.” Existing Pattern-A gates on evaluate paths stay as-is. If Betty discovers ungated debug noise while reading evaluate paths, file `[qa-handoff]` back with evidence — do not expand product scope here.

## Stage 4: Betty — manifest + publish

**Owner:** Betty (`qa-child`). **Done when:** Tests Ready comment lists the exact pytest paths; bible sha noted; `test(AST-1210)` (+ `merge-tests` as required) published to **this** publish ref only.

Suggested run (adjust if class names differ after Stage 3):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1054MeteoriteGdlDispatch \
  tests/component/utils/test_config.py::TestAst1210EvaluateMeteoriteTwinConfig \
  tests/component/core/test_consult.py::TestAst1054MeteoriteGdlOutcomeOverlay \
  tests/component/core/test_consult.py::TestEvaluateMeteoriteStandaloneTwin \
  tests/component/core/test_consult.py::TestAst1155IncompleteGradeRetry \
  tests/component/core/test_dispatcher.py::TestAst1054MeteoriteDispatchProvision \
  -q
```

(Include the Analysis override test node id once named in Stage 3.)

## Self-Assessment

**Scope:** `Single-Component` — bible + component test fold-in only; no `src/` product surface on this child (product twin locked by AST-1209).

**Conf:** `high` — AST-1209 audit already listed exact bible-drift paths; consult already has twin smoke classes; remaining work is correcting stale AST-1060-era asserts and documenting the twin.

**Risk:** `Medium` — wrong bible/test rewrite could re-lock the obsolete `evaluate_jd`@**METEORITE_QUALIFIED** story or weaken classic `evaluate_jd`@**JD_READY** coverage; stages require both twin and classic asserts side by side.

## Rules check (ASTRAL_CODE_RULES)

- §1.1 / `astral.standards.in-scope-only`: no qualify/gaze/alias/fixture/UI product; siblings named.
- `astral.standards.no-hardcoded-sets`: tests assert config maps (`METEORITE_DISPATCH_TASKS`, rubric/craft owners, Analysis override) — do not invent parallel twin dicts in tests.
- `astral.batch.claim-process-release`: dispatcher tests only lock existing claim/retire behavior from AST-1209; no new claim shape.
- `astral.standards.debug-contract-gated`: no new ungated debug; Style D AC N/A without product touch.
- Engineer must not edit `tests/` or `docs/test-bible/**` — Betty owns Stages 2–4.
- `astral.seed.agent-tables-in-repo-json`: excluded (AST-1211).

## Review (build stub)

**Publish ref:** `origin/sub/AST-1186/AST-1210-bible-component-tests-lock-twin-contract`
**Plan path:** `docs/features/meteorite/ast-1210-bible-component-tests-lock-twin-contract.md`

**Built tip:** `d6e4b74d` (merge `origin/ftr/AST-1186-evaluate-meteorite-fold-recent-work-into-tests` onto plan tip `2cad8fbb` — AST-1209 twin retirement + Betty dispatcher tests on tip; no `src/` delta this child)

| Stage | Commit | Summary |
|-------|--------|---------|
| Prerequisite | `d6e4b74d` | sync-child merge full parent ftr (authoritative `ftr/AST-1186-evaluate-meteorite-fold-recent-work-into-tests`); gate: `twin_present` + `ts.startswith("METEORITE_")` on tip |
| 1 | (no product commit) | Twin audit points 1–9 re-verified read-only; zero `src/` / `tests/` / bible edits — Code Complete handoff for Betty Stages 2–4 |

**Joan fold-in (APPROVED discuss, for Betty):** Stage 3.1 repairs pre-existing red `rows[("evaluate_jd", "METEORITE_QUALIFIED")]` KeyError. Stage 3.3 Analysis override must use `_entity_state_is_meteorite(job_data.get("state"))` (state prefix), not `is_meteorite_company`.

### code-rubric.v1 verdict

[code-rubric] revision=1

| Field | Value |
|-------|-------|
| Rubric | code-rubric.v1 |
| Publish ref tip | `f37a0618a400565d6aecd7e5c6898ebafd5368fe` |
| Overall | FIX-NOW |

Full active statute corpus (65 leaves — 19 universal + 46 scoped) scored in-session against `git diff origin/dev...origin/sub/AST-1186/AST-1210-bible-component-tests-lock-twin-contract`. `orch.git.merge-on-checkout` **conforms** here — verified `origin/ftr/AST-1186-...` IS an ancestor of this sub's tip (the Prerequisite sync ran correctly, unlike the gap found on AST-1211), and `src/core/dispatcher.py` / the AST-756 fixture on this tip are byte-identical to `origin/ftr/AST-1186-...` — inherited from AST-1209/AST-1211 (both already reviewed clean/fix-now under their own tickets), not re-touched here. Zero `code(AST-1210)` commit exists — this ticket is 100% Betty's `test(AST-1210)` commit, correctly (`astral.git.engineer-test-tree-ban` / `orch.roles.betty-owns-test-tree` conform).

**fix-now — unscoped test-coverage deletion, stale bible left behind.** `test(AST-1210)` deletes the entire `TestAst1193AnalysisMatchParity` class from `tests/component/core/test_consult.py` (5 methods: `_find_rubric_criterion` label/code lookup, live-vs-snapshot fallback matching ×2, and — critically — the **only** Style D debug-contract lock on `build_job_token_context`: `test_build_job_token_context_debug_emits_found_recorded` / `test_build_job_token_context_debug_false_is_quiet`). Verified independently: `_find_rubric_criterion` and `rubric_criteria_for_task` are still live, unmodified functions in `src/core/consult.py` (this ticket has zero `src/` diff) — so this is a real coverage regression on unchanged product code, not cleanup of dead code. Neither the AST-1210 plan's Files Changed table nor Stage 3 authorizes touching this class (scope is Analysis-override + incomplete→retry twin locks only) — `astral.standards.in-scope-only`. Betty's own QA manifest for this ticket does not mention the deletion either. Worse: `docs/test-bible/core/consult.md` §**AST-1193 · AST-1163** (lines 939–953, untouched by this diff) still names `TestAst1193AnalysisMatchParity` as the current test for that coverage — the bible now documents a class that does not exist. `astral.standards.debug-contract-gated` conforms for AST-1210's own scope (no new `debug=` path touched), but this deletion silently removes existing debug-contract lock with no replacement. **Remedy:** restore `TestAst1193AnalysisMatchParity` (or fold its assertions into the surviving `TestAst513JobTokenContext` methods) and update/keep the AST-1193 bible row accurate; if Betty has a real reason the class no longer applies, that belongs in a `[qa-handoff]` / bible "Broken / obsolete" note, not a silent drop.

**What's solid:** everything else in this diff is precise and independently verified against live `src/utils/config.py` / `src/core/consult.py` — `TestAst1210EvaluateMeteoriteTwinConfig` (rubric/craft/Analysis-override maps) and `test_format_analysis_jd_uses_twin_owner_when_state_meteorite` both assert exactly what the unmodified product code does today (confirmed by reading `config.py:2017-2034`, `5219-5232` and `consult.py:86-87,811-812` directly, not by trusting the test). `test_dispatch_row_specs_and_job_states` correctly repairs Joan's plan-rubric finding #1 (pre-existing `KeyError` on `("evaluate_jd", "METEORITE_QUALIFIED")`). `_consult_batch_fail_dest` twin second-strike assert (`METEORITE_QUALIFIED_RETRY` → `METEORITE_ERROR_EVALUATE_JD`, not classic `ERROR_EVALUATE_JD`) is registry-accurate. All three bible files (`config.md`, `consult.md`, `dispatcher.md`) correctly retire the `evaluate_jd`@`METEORITE_QUALIFIED` claims per Stage 2 and cross-reference AST-1209/1210/1211 consistently.

**Pattern conformance:** none cited (ticket description cites statute ids only, no `pattern.*`).

## Frame diff
(none) — description Acceptance Criteria / In-scope boxes are unchecked (`[ ]`) on this ticket unlike its siblings; Radia does not tick engineer/QA checkboxes on review, noting only as an advisory Linear-hygiene item, not a C7 blocker.

context_tokens≈78000

— Radia

## Resolution

**Date:** 2026-08-06  
**Review tip:** `95f6dec7` (Radia docs) · resolve tip after Betty return: `e8744b4c`

| Item | Disposition |
|------|-------------|
| Fix-now — restore `TestAst1193AnalysisMatchParity` + AST-1193 bible honesty | **Cleared by Betty.** `test(AST-1210)` `653bf749` restored the class (5 methods incl. Style D); `merge-tests` → publish `e8744b4c`. Bible AST-1193 row already named the class (unchanged). Hedy re-ran twin manifest + `TestAst1193AnalysisMatchParity` — **22 passed**. |
| Advisory — unchecked description AC boxes | Ticked on UT flip (validated on tip). |

No `src/` resolve commit after Betty return.
