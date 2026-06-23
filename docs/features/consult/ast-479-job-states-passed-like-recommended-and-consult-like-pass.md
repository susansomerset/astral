<!-- linear-archive: AST-479 archived 2026-06-15 -->

## Linear archive (AST-479)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-479/job-states-passed-like-recommended-and-consult-like-pass-synthesize  
**Status at archive:** Done  
**Project:** Astral Consult  
**Assignee:** hedy  
**Priority / estimate:** High / 3  
**Parent:** AST-478 — Synthesize job analysis report (Estelle Opus upshot)  
**Blocked by / blocks / related:** parent: AST-478; blocks: AST-481; blocks: AST-480

### Description

## What this implements

Restore `PASSED_LIKE` as the post-`consult_like` queue state (not `BUILD_ARTIFACTS`). Add `PASSED_LIKE_RETRY` and `RECOMMENDED` to `JOB_STATES` with legal transitions. Set `consult_like` `pass_state` **→** `PASSED_LIKE`. Ensure `BUILD_ARTIFACTS` is only reachable from `RECOMMENDED` via candidate/UI transition (not from any task `pass_state`). Update `RECOMMENDED_JOB_STATES` and UI manifest lists so Recommended jobs surface `RECOMMENDED` (and related) correctly.

## Acceptance criteria

1. `consult_like` pass → `PASSED_LIKE` only (grep/config: no path sets `BUILD_ARTIFACTS` on LIKE pass).
2. **Regression:** No scheduled/dispatch/consult path assigns `BUILD_ARTIFACTS` without a documented UI transition (artifact $$ gate).

(Parent AC 2–3 owned by sibling **analysis_upshot** child.)

## Boundaries

* Does **not** implement `analysis_upshot` task body or Opus prompt (**AST-313** / Ada sibling).
* Does **not** build JAR report UI (**Katherine** sibling).
* Does **not** add Approve button `RECOMMENDED` **→** `BUILD_ARTIFACTS` (separate workflow epic).

## Notes for planning

* `src/utils/config.py`: `JOB_STATES`, `consult_like` orchestration via `TASK_CONFIG` / `_consult_orchestration`.
* Reverse/dev migration: stop auto `PASSED_LIKE` **→** `BUILD_ARTIFACTS` on DB open for new LIKE passes; coordinate with existing rows on `dev`.
* `docs/features/consult/` plan path per **plan-astral** §3.

## Git branch (authoritative)

Parent `ftr/AST-478-synthesize-job-analysis-report-estelle-opus-upshot`, child `sub/AST-478/AST-479-job-states-passed-like-recommended-and-consult-like-pass` (segment finalized at dispatch). Engineers cherry-pick to `origin/<publish-ref>` — not Linear `gitBranchName`.

### Comments

#### chuckles — 2026-05-25T04:04:25.629Z
[rollup-child] sub → ftr

Child: AST-479
Publish ref: origin/sub/AST-478/AST-479-job-states-passed-like-recommended-and-consult-like-pass
Parent ftr: origin/ftr/AST-478-synthesize-job-analysis-report-estelle-opus-upshot @ 13e03b39

sub/* kept for fixes until prep-uat.

— Chuckles

#### hedy — 2026-05-25T04:01:20.402Z
Review feedback resolved. Branch **`sub/AST-478/AST-479-job-states-passed-like-recommended-and-consult-like-pass`** ready for **`prep-uat`** (parent **AST-478**).

**Commit:** `28eb2add` — Hedy  
**Publish tip:** **`origin/sub/AST-478/AST-479-job-states-passed-like-recommended-and-consult-like-pass`** @ **`28eb2add`**

**Radia:** fix-now **0**; **discuss** (RECOMMENDED vs **`CANDIDATE_*`** `prior_states` until **AST-480**) acknowledged in plan **`## Resolution`** — parent integration order **479 → 480**; no emergency solo-cherry-pick path.

**`origin/dev` dry-run (§9a): clean** · **`origin/ftr/AST-478-synthesize-job-analysis-report-estelle-opus-upshot` dry-run: clean**

#### radia — 2026-05-25T03:59:25.644Z
## Radia review (`review-astral`)

**Diff:** `origin/dev…origin/sub/AST-478/AST-479-job-states-passed-like-recommended-and-consult-like-pass`  
**Code tip reviewed:** `2457bc413ed43f1c356d6fa80dc5c26faee65a31`

**Counts:** fix-now **0** · discuss **1** · advisory **0**

**Summary:** LIKE pass cleanly lands **`PASSED_LIKE`**; AST-302 auto-migrate to **`BUILD_ARTIFACTS`** removed; **`RECOMMENDED`**, **`PASSED_SCORE_GATED`**, and in-review manifests align with AC. **`BOARD_CONFIG`** dedupe is mechanical post-merge hygiene.

**Discuss:** On this publish tip **`JOB_STATES["RECOMMENDED"]`** exists but **`CANDIDATE_*` outcomes** omit **`RECOMMENDED`** from **`prior_states`** until **`AST-480`** (already in your graph). No issue for parent integration order (**479→480**); flag only if **`479`** were ever cherry-picked alone onto **`dev`**.

**Doc commit (cherry-pick target):** `1ed3175d` → `origin/sub/AST-478/AST-479-job-states-passed-like-recommended-and-consult-like-pass`  
Markdown: [`ast-479-job-states-…`](https://github.com/susansomerset/astral/blob/sub/AST-478/AST-479-job-states-passed-like-recommended-and-consult-like-pass/docs/features/consult/ast-479-job-states-passed-like-recommended-and-consult-like-pass.md) — appendix **## Review**

**Tolerances accepted:** none required.

#### hedy — 2026-05-25T03:47:34.157Z
**Hedy — test-astral (green)**

**Commands (Betty manifest — full harness):**
- `./scripts/testing/run_component_tests.sh`

**Result:** 924 pytest + 65 Vitest files passed; **Per-file branch coverage OK** for `LOCKED_AT_100` (including `src/utils/config.py`).

**Product fix on this pass:** merge of `origin/dev` + publish ref had duplicated `BOARDS_CONFIG` / `BOARD_CONFIG` / `list_adopted_boards` in `config.py`, leaving final `BOARD_CONFIG = {}` at import. Removed the stale duplicate block so the real registry and helpers are the live definitions.

**SHAs:**
- `dev-hedy`: `2931398488cc26e61f854af19d6d99a4a8da3af9` (`fix(AST-479): dedupe BOARD_CONFIG after integration merge`)
- `origin/sub/AST-478/AST-479-job-states-passed-like-recommended-and-consult-like-pass`: **`2457bc413ed43f1c356d6fa80dc5c26faee65a31`** (cherry-picked the above; replaces prior tip `3e04a500` for replay)

#### betty — 2026-05-25T03:44:19.108Z
QA manifest by Betty (Tests Ready handoff).

1. **`tests/component/utils/test_config.py`** — **`TestAst479LikePassStates`** (`TASK_CONFIG["grade_like"]["pass_state"]` → **`PASSED_LIKE`**, **`RECOMMENDED_JOB_STATES`**); **`TestAst309CoverLetterTaskConfig`** per prior manifest if run in narrow suite.
2. **`tests/component/ui/api/test_api_jobs.py`** — **`TestJobsRoutes.test_list_recommended_and_default`** (recommended **`list_jobs`** `states`).
3. **Vitest / RTL** — **`tests/component/frontend/test-utils.tsx`** provider wiring; **`test_JobsRecommended.test.tsx`**; **`test_Modal.test.tsx`** / **`test_RubricModal.test.tsx`** (unchanged **`alertdialog`** flow).
4. **`docs/ASTRAL_TEST_BIBLE.md`** §**7.13y** (+ §**7.13w** `TestAst479LikePassStates`).

**Published tip:** **`origin/sub/AST-478/AST-479-job-states-passed-like-recommended-and-consult-like-pass`** @ **`3e04a500`** ( **`test(AST-479):`** already on tip — **`test-astral`** verifies there).

Full harness: `./scripts/testing/run_component_tests.sh`

#### betty — 2026-05-25T03:32:15.462Z
QA manifest by Betty.

1. **`tests/component/utils/test_config.py`** — `TestAst479LikePassStates` (`TASK_CONFIG["grade_like"]["pass_state"]` → `PASSED_LIKE`, `RECOMMENDED_JOB_STATES` shape); **`TestAst309CoverLetterTaskConfig`** (`draft_cover_letter` schema only; duplicate class cleanup; legacy **`craft_job_cover_letter`** absent per **AST-450**).

2. **`tests/component/ui/api/test_api_jobs.py`** — **`TestJobsRoutes.test_list_recommended_and_default`** (recommended **`list_jobs`** `states` includes **`RECOMMENDED`** and **`BUILD_ARTIFACTS`**).

3. **Frontend RTL / Vitest** — **`tests/component/frontend/test-utils.tsx`** wraps **`UserPromptProvider`** (`Modal` → **`useUserConfirm`**); **`test_JobsRecommended.test.tsx`** (fixtures **`RECOMMENDED`**); **`test_Modal.test.tsx`** / **`test_RubricModal.test.tsx`** (**`alertdialog`** discard flow).

**`docs/ASTRAL_TEST_BIBLE.md`** — **§7.13y**; **§7.13w** references **`TestAst479LikePassStates`**.

**Full verification (**`test-astral`):** `./scripts/testing/run_component_tests.sh`

**Publish tip:** `origin/sub/AST-478/AST-479-job-states-passed-like-recommended-and-consult-like-pass` @ **`3e04a500`**.

#### hedy — 2026-05-25T03:22:47.289Z
Built by Hedy.

**Publish ref:** `sub/AST-478/AST-479-job-states-passed-like-recommended-and-consult-like-pass`

**Commits (dev-hedy, cherry-picked to publish ref tip `fc5c49b0`):**
- `bc85e6f268c4e86234771b556f05b7281adad5a8` — feat(AST-479): PASSED_LIKE / RECOMMENDED / manifests, DB migration removal, `CandidateJobRowActions` RECOMMENDED, AST-302 superseded note.
- `1c97ae404681ebf11cee99211037cd3c7bdde90d` — docs(AST-479): review stub on plan doc.

**Code Complete handoff — Betty (`qa-astral`):** plan listed `tests/component/utils/test_config.py` (`TestConsultLikePassState`), `tests/component/core/test_consult.py`, `tests/component/ui/api/test_api_jobs.py`, frontend JobsRecommended/tests — expectations likely need updates for `RECOMMENDED_JOB_STATES`, `TASK_CONFIG["grade_like"]["pass_state"]`, and nav/job filters. Engineer did not edit `tests/` per build-astral test-tree ban.

**Persist job_data key:** N/A (this ticket).

#### hedy — 2026-05-25T03:19:58.663Z
Label review (build agent):

Conf: agree — current conf-high matches JOB_STATES / TASK_CONFIG / migration touch surface per plan Self-Assessment.

Risk: agree — current risk-Medium matches prior_states / RECOMMENDED_JOB_STATES / migration removal blast radius; mitigated by grep AC and QA handoff.

Scope: agree — current scope-MAJOR-CHANGE matches multi-layer state machine + UI Set + DB ensure change.

#### chuckles — 2026-05-25T03:19:04.463Z
## Plan Validation — Chuckles

**Verdict: APPROVED**

Faithful to parent **AST-478** AC1/AC4: `consult_like` → `PASSED_LIKE`, removes PASSED_LIKE→BUILD_ARTIFACTS migration, `RECOMMENDED` + retry states, `BUILD_ARTIFACTS` prior = `RECOMMENDED` only, manifest/list updates. Layer and config discipline look sound.

**discuss** — `CandidateJobRowActions.tsx` touch is minimal; Betty will update tests per Code Complete note.

— Chuckles

#### hedy — 2026-05-25T02:43:36.711Z
**Plan:** `docs/features/consult/ast-479-job-states-passed-like-recommended-and-consult-like-pass.md` (on `origin/sub/AST-478/AST-479-job-states-passed-like-recommended-and-consult-like-pass`).

**Self-assessment (labels updated accordingly)**

| Axis | Value | Justification |
|------|-------|---------------|
| **Scope** | `MAJOR-CHANGE` | Touches global `JOB_STATES` / `TASK_CONFIG`, DB migration hook, optional consult routing table check, React review Set, and artifact doc cross-ref—one coherent machine fix spanning layers. |
| **Conf** | `high` | Reuses established config + state-machine patterns from **ASTRAL_CODE_RULES** §2.1 / §2.6; sibling tickets own dispatch seeds and task body. |
| **Risk** | `Medium` | Bad `prior_states` or leftover auto-migration would mis-queue jobs or break recommended/nav counts; mitigated by ticket AC grep + explicit **Code Complete** list for Betty on tests that currently assert LIKE→`BUILD_ARTIFACTS`. |

— Hedy (plan-astral)

---

# AST-479 — Job states PASSED_LIKE, RECOMMENDED, and consult_like pass

**Parent:** [AST-478 — Synthesize job analysis report (Estelle Opus upshot)](https://linear.app/astralcareermatch/issue/AST-478/synthesize-job-analysis-report-estelle-opus-upshot)

**Feature ref (publish target on `origin` only):** `sub/AST-478/AST-479-job-states-passed-like-recommended-and-consult-like-pass`

**Linear:** [AST-479](https://linear.app/astralcareermatch/issue/AST-479/job-states-passed-like-recommended-and-consult-like-pass-synthesize)

Restore the pipeline segment **after LIKE** so `consult_like` passes land in **`PASSED_LIKE`** (queue for sibling **`analysis_upshot`**), not **`BUILD_ARTIFACTS`**. Introduce **`RECOMMENDED`** and **`PASSED_LIKE_RETRY`** in **`JOB_STATES`** with explicit `prior_states` aligned to the parent epic: synthesis dispatch claims **`PASSED_LIKE`** and moves to **`RECOMMENDED`** on success (implemented under **AST-480** / config seed — *out of scope here* except for empty legal graph + comments). **`BUILD_ARTIFACTS`** must not be reachable from any graded consult task’s **`pass_state`**; it is reserved for a future **UI-only** transition from **`RECOMMENDED`** (separate epic — no Approve button in this ticket). Remove the DB-open migration that rewrote **`PASSED_LIKE` → `BUILD_ARTIFACTS`**, which contradicted the new model.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `grade_like.pass_state` → `PASSED_LIKE`; extend `JOB_STATES` (`PASSED_LIKE`, `PASSED_LIKE_RETRY`, `RECOMMENDED`, tighten `BUILD_ARTIFACTS`); `RECOMMENDED_JOB_STATES`; `PASSED_SCORE_GATED_STATES`; `IN_REVIEW_STATES` / `JOBS_IN_REVIEW_*` / `JOBS_IN_REVIEW_GRADE_FIELD` for LIKE review row; grep-driven manifest touch-ups | utils |
| `src/data/database.py` | Remove or replace AST-302 `UPDATE job SET state = 'BUILD_ARTIFACTS' WHERE state = 'PASSED_LIKE'` on schema ensure; update comment to AST-479 semantics | data |
| `src/core/consult.py` | Only if `_INPUT_STATE_TO_TASK` or nearby consult routing must know `PASSED_LIKE` / `RECOMMENDED` for non-dispatch helpers—keep minimal; do **not** implement `analysis_upshot` | core |
| `src/ui/frontend/src/components/CandidateJobRowActions.tsx` | Extend `REVIEW_LIKE` (or equivalent) so **`RECOMMENDED`** jobs get the same review affordances as current recommended-like rows | ui |
| `docs/features/artifacts/ast-302-job-state-machine-artifacts-and-candidate-states.md` | Short note that LIKE→`PASSED_LIKE` supersedes the old “retire PASSED_LIKE” migration—**doc only**, one paragraph, no behavior | docs |

**Out of scope (ticket boundaries):** `analysis_upshot` task body, dispatch seed rows for **`analysis_upshot`**, JAR UI, Approve **`RECOMMENDED` → `BUILD_ARTIFACTS`** button, changes under `tests/` (Betty / `qa-astral` per **build-astral** test-tree ban—see **Code Complete** note below).

---

## Stage 1: Config — TASK_CONFIG and JOB_STATES

**Done when:** `TASK_CONFIG["grade_like"]["pass_state"]` is **`PASSED_LIKE`**. `JOB_STATES` contains **`PASSED_LIKE`**, **`PASSED_LIKE_RETRY`**, and **`RECOMMENDED`** with `prior_states` that match the parent epic’s narrative and **do not** allow `BUILD_ARTIFACTS` as a direct successor of `PASSED_GET` except via the chain **`PASSED_GET` → `PASSED_LIKE` → … → `RECOMMENDED` → (UI) → `BUILD_ARTIFACTS`**.

1. In `src/utils/config.py`, set **`TASK_CONFIG["grade_like"]["pass_state"]`** to **`"PASSED_LIKE"`** (string literal exactly that).

2. In **`JOB_STATES`**, replace the legacy comment on **`PASSED_LIKE`** / **`BUILD_ARTIFACTS`** with accurate AST-479 text. Define:
   - **`PASSED_LIKE`**: `prior_states` **`["PASSED_GET"]`** — normal success exit of `consult_like` / `grade_like`.
   - **`PASSED_LIKE_RETRY`**: `prior_states` **`["PASSED_LIKE"]`** — holding state after a **technical** failure on the **post-LIKE** synthesis step (sibling); consult_like technical failures remain **`FAILED_TECHNICAL_LIKE`** / existing error path—do not route LIKE API errors here unless the ticket description explicitly demands it (it does not).
   - **`RECOMMENDED`**: `prior_states` **`["PASSED_LIKE", "PASSED_LIKE_RETRY"]`** so a job can return from retry into the same queue shape the sibling dispatch will use.
   - **`BUILD_ARTIFACTS`**: set **`prior_states`** to **`["RECOMMENDED"]` only** — explicit **UI / candidate action** entry for the artifact chain; **no** `PASSED_GET` in `prior_states`.

3. Propagate **`BUILD_ARTIFACTS`** `prior_states` change to every other **`JOB_STATES` entry** that lists **`BUILD_ARTIFACTS`** in its own `prior_states` (e.g. candidate flow rows). Each must remain consistent: if a state could previously be entered from `BUILD_ARTIFACTS` when the job had never been `RECOMMENDED`, re-derive legal predecessors so the graph stays coherent **without** reintroducing silent `PASSED_GET → BUILD_ARTIFACTS`.

⚠️ **Decision:** **`BUILD_ARTIFACTS` predecessors are `RECOMMENDED` only.** Until the UI epic lands, **no automated path** should call `tracker.transition_job_state(..., "BUILD_ARTIFACTS")` from dispatch. Existing **dev** rows that still sit in `BUILD_ARTIFACTS` from the old LIKE migration may be **historically inconsistent** with `prior_states`; fixing them is **data cleanup** optional for this ticket—do **not** add a blind `UPDATE` that breaks in-flight **`contemplate_job`** runs. If a migration is unavoidable, restrict it to idempotent no-ops or document the edge case in the Stage 1 commit comment for Susan.

4. Set **`RECOMMENDED_JOB_STATES`** to surface the **Recommended** nav/list for jobs the candidate should review **after** synthesis. Use **`["RECOMMENDED", "BUILD_ARTIFACTS", "CANDIDATE_REVIEW"]`** (drop **`PASSED_LIKE`** from this list so “Recommended” is not conflated with “waiting for upshot”). If product intent requires showing **pre-synthesis** LIKE passes elsewhere, that is **`IN_REVIEW`**, not **`RECOMMENDED`**.

5. Add **`PASSED_LIKE`** to **`PASSED_SCORE_GATED_STATES`** (frozen set beside the existing PASSED_* entries) so future sibling dispatch with **score floor** on **`PASSED_LIKE` queues** matches the same gating pattern as other scored consult steps.

6. Add **`PASSED_LIKE`** (and **`PASSED_LIKE_RETRY`** if product should list retries separately) to **`IN_REVIEW_STATES`** and **`JOBS_IN_REVIEW_UI_SECTIONS`** with human-readable labels (e.g. “Passed LIKE”, “LIKE (retry)”). Extend **`JOBS_IN_REVIEW_GRADE_FIELD`** with **`PASSED_LIKE`: `like_grades`** (and retry row if present).

7. Run **`python3 -m py_compile`** on every edited `.py` file in this stage.

**Code Complete note for Betty:** Expect **`tests/component/utils/test_config.py`** (`TestConsultLikePassState`), **`tests/component/core/test_consult.py`**, **`tests/component/ui/api/test_api_jobs.py`**, and frontend **`JobsRecommended`** tests to need expectation updates when **`RECOMMENDED_JOB_STATES`** / API job list filters change. **Engineer does not edit `tests/`** during **build-astral**; list these paths in the **Code Complete** Linear comment.

---

## Stage 2: Consult routing map + UI affordance

**Done when:** No consult/dispatch **task `pass_state`** targets **`BUILD_ARTIFACTS`**. `_INPUT_STATE_TO_TASK` does not send **`PASSED_LIKE`** to **`contemplate_job`** (artifacts). **`RECOMMENDED`** appears in the **review-like** UI set where **`BUILD_ARTIFACTS` / `PASSED_LIKE`** already do.

1. In `src/core/consult.py`, inspect **`_INPUT_STATE_TO_TASK`** (this map is **`input_state` → dispatch `task_key`** for `run_consult_task`). **`consult_like`** is already reached from **`PASSED_GET`**, not from **`PASSED_LIKE`**. Ensure **`PASSED_LIKE`** is **absent** from this map **or** entries only when sibling adds **`analysis_upshot`**—**never** **`PASSED_LIKE` → `contemplate_job`** and **never** **`PASSED_LIKE` → `consult_like`**. Keep **`BUILD_ARTIFACTS` → `contemplate_job`** for the artifact chain after UI sets **`BUILD_ARTIFACTS`**. **Do not** add **`analysis_upshot`** here (sibling).

2. Grep **`src/`** for **`pass_state`**, **`BUILD_ARTIFACTS`**, **`consult_like`**, **`grade_like`** and confirm **no** orchestration assigns **`BUILD_ARTIFACTS`** on LIKE pass (ticket AC + regression).

3. In **`src/ui/frontend/src/components/CandidateJobRowActions.tsx`**, add **`RECOMMENDED`** to **`REVIEW_LIKE`** (same Set as **`BUILD_ARTIFACTS`** / **`PASSED_LIKE`** / **`CANDIDATE_REVIEW`**).

4. If **`resolve_dispatch_task_config_key`** / **`NAV_CONFIG`** / **`api_system`** job counts implicitly depend on **`RECOMMENDED_JOB_STATES`** only, no further edits; else align **recommended counts** with the updated list.

5. **`python3 -m py_compile`** on changed `.py` files. If any **`.tsx`** changed: `cd src/ui/frontend && npx tsc -b --noEmit`.

---

## Stage 3: Database — stop clobbering PASSED_LIKE

**Done when:** Opening the DB no longer runs **`UPDATE job SET state = 'BUILD_ARTIFACTS' WHERE state = 'PASSED_LIKE'`**.

1. In `src/data/database.py`, in **`_ensure_job_schema`** (or the function that contains the AST-302 comment), **delete** the **`UPDATE`** that rewrites **`PASSED_LIKE` → `BUILD_ARTIFACTS`**. Replace the comment with a short AST-479 note: LIKE passes remain **`PASSED_LIKE`** for the synthesis queue; **`BUILD_ARTIFACTS`** is not auto-set here.

2. **`python3 -m py_compile`** on `src/data/database.py`.

---

## Stage 4: Artifact plan doc cross-reference (optional, one commit or fold into Stage 3)

**Done when:** **AST-302** feature doc states that the old migration is obsolete relative to AST-478/479.

1. In `docs/features/artifacts/ast-302-job-state-machine-artifacts-and-candidate-states.md`, add a **“Superseded by AST-479”** note: automatic promotion **PASSED_LIKE → BUILD_ARTIFACTS** removed; see parent **AST-478**.

---

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — Touches the global job state registry, TASK_CONFIG pass_state, DB migration hook, consult state→task map, and a React Set; multiple layers but one coherent state-machine correction.

**Conf:** `high` — Follows existing `JOB_STATES` / `TASK_CONFIG` / `PASSED_SCORE_GATED_STATES` patterns from **ASTRAL_CODE_RULES** §2.1 and §2.6; sibling tickets fill in dispatch rows and task body.

**Risk:** `Medium` — Wrong `prior_states` or leftover **`BUILD_ARTIFACTS`** auto-migration would mis-route jobs, break recommended counts, or strand rows; mitigated by grep AC and explicit **Code Complete** test handoff list.

---

## Plan vs ASTRAL_CODE_RULES (self-review)

- **§1.3 DRY:** Single edits in `JOB_STATES` / `TASK_CONFIG`; no duplicate state lists in React beyond the one Set update.
- **§2.1 config:** All new state strings and lists live in `config.py`; no inline magic job-state sets in UI beyond importing existing constants where already done.
- **§2.4 batch processing:** No change to claim/clear patterns in this ticket.
- **§2.6 state machine:** All transitions confined to config + documented migration removal; **`tracker.transition_job_state`** remains the enforced gate.
- **§3.3 imports:** Consult/UI changes preserve layer rules (`ui` does not import `data`).
- **§3.5 naming:** Keep `PASSED_LIKE`, `PASSED_LIKE_RETRY`, `RECOMMENDED`, `BUILD_ARTIFACTS` spellings aligned with Linear/parent AST-478.

---

## Review stub (build)

Built by Hedy.

- **Publish ref:** `sub/AST-478/AST-479-job-states-passed-like-recommended-and-consult-like-pass`
- **Commit:** `bc85e6f268c4e86234771b556f05b7281adad5a8`

## Review

**Radia** · 2026-05-24 · three-dot diff `origin/dev…origin/sub/AST-478/AST-479-job-states-passed-like-recommended-and-consult-like-pass`

| | |
|--|--|
| **Tip reviewed** | `2457bc413ed43f1c356d6fa80dc5c26faee65a31` |

**What’s solid**

- `TASK_CONFIG["grade_like"].pass_state` → `PASSED_LIKE`; removal of idempotent `PASSED_LIKE → BUILD_ARTIFACTS` on DB open matches AC and keeps the artifact gate off the LIKE pass path.
- `JOB_STATES` / `RECOMMENDED_JOB_STATES` / `PASSED_SCORE_GATED_STATES` / jobs UI config slices (`IN_REVIEW_*`, section order, grade-field map) read as one coherent machine: pre-upshot LIKE rows stay in review pipelines; post-upshot surface uses `RECOMMENDED` in the recommended list tuple.
- `BOARD_CONFIG` dedupe is explained in the tip commit; narrows merge-artifact risk without changing consult behavior in the reviewed hunks.
- Component tests and bible touch points align with the new state names (Betty **Tests Passed**).

**Issues**

| Sev | Topic | Notes |
|-----|--------|--------|
| discuss | Merge order vs **AST-480** | On this tip, `RECOMMENDED` exists but `CANDIDATE_REVIEW` / `CANDIDATE_APPLIED` / `CANDIDATE_SKIPPED` do not yet list `RECOMMENDED` in `prior_states` — that wiring is on the **AST-480** publish tip. Do not release **479** alone to production without **480** (or fold the same `prior_states` edits into **479**). Parent **AST-478** ordering already implies **480** follows. |

**Recommended actions**

- None for the **479 → 480 → 481** integration path under the parent branch.
- Emergency cherry-pick of **479** only: mirror **AST-480**’s `RECOMMENDED` edges on candidate outcome states before ship.

**Radia doc commit:** see tip of `origin/sub/AST-478/AST-479-job-states-passed-like-recommended-and-consult-like-pass` after push.

---

## Resolution

**2026-05-25 · Hedy — closure after Radia (`review-astral`), code tip `2457bc41`**

| Category | Action |
|---|---|
| **fix-now** | None (Radia count 0). BOARD_CONFIG dedupe already on the reviewed tip (`fix(AST-479): dedupe BOARD_CONFIG …`). |
| **discuss** | **AST-480 ordering:** Accepted per parent **AST-478**: `RECOMMENDED` stays in **`JOB_STATES`** here; widening **`CANDIDATE_*`** `prior_states` to include **`RECOMMENDED`** ships with **AST-480**, not deferred as a blocker for **479** on the parent integration branch. Emergency solo-cherry-pick path remains documented in Radia’s **Recommended actions**. |
| **advisory** | None. |

**Integration:** **`dev-hedy`** merged **`origin/dev`** (already current) then **`origin/sub/AST-478/AST-479-job-states-passed-like-recommended-and-consult-like-pass`**; Radia appendix was already at publish tip **`1ed3175d`** — this section appended for **User Testing** handoff only.
