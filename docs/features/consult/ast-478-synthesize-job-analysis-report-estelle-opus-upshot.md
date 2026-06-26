# AST-478 — Synthesize job analysis report (Estelle Opus upshot)

<!-- linear-archive: AST-478 archived 2026-06-15 -->

## Linear archive (AST-478)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-478/synthesize-job-analysis-report-estelle-opus-upshot  
**Status at archive:** Done  
**Project:** Astral Consult  
**Assignee:** susan  
**Priority / estimate:** High / 5  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-300; related: AST-313

### Description

## Purpose

After a job passes LIKE, the candidate needs a **single readable synthesis** of everything Astral already learned (joblist, JD, DO, GET, LIKE grades/scores/notes) — not raw panels only. **Estelle (Opus)** runs `analysis_upshot`: structured JSON that drives the **Job Analysis Report** (runtime UI render), including **Estelle's Take** on the G/D/L analysis and a **balanced upshot on the full job description**, plus segment-level upshots, candidate questions, and caveats.

Pipeline gate: `PASSED_LIKE` (output of `consult_like`) → dispatch claims batch (with **score floor**) → `analysis_upshot` → persist JSON on `job_data` → `RECOMMENDED`. Candidate reviews the report, then **explicitly approves in the UI** (separate workflow) — that approval is `BUILD_ARTIFACTS` (user-facing “Approved” / in progress for artifacts). **No dispatch task** may set `BUILD_ARTIFACTS` (cost control).

Stored analysis + upshots later feed artifact prompts when the user starts artifact generation from the report screen.

## Functional scope

* `analysis_upshot` **task** (`TASK_CONFIG` + Manage Tasks / [AST-313](https://linear.app/astralcareermatch/issue/AST-313/artifact-pipeline-prompt-authoring)): Opus-tier model via **existing agent-bound model** pattern. Response **schema** defines report sections (G/D/L takes, whole-JD upshot, per-segment upshots, questions, caveats).
* **Dispatch:** Seed row `trigger_state: PASSED_LIKE`, entity **job**, scored claim with **score floor**. `consult.run_consult_task` runs synthesis; success `pass_state` **→** `RECOMMENDED` only after report JSON is saved.
* `consult_like`**:** `pass_state` **→** `PASSED_LIKE` — **never** `BUILD_ARTIFACTS`.
* **Persistence:** Structured **JSON under** `job_data`. Schema-driven sections for runtime UI render.
* **Retry:** `PASSED_LIKE_RETRY` on technical failure.

## Boundaries

* **DOES NOT BUILD Artifact run (sibling epic):** After UI sets `BUILD_ARTIFACTS`, dispatcher may claim that state for `contemplate_job` / artifact chain. `BUILD_ARTIFACTS` **is candidate/UI-only entry** — not an automatic pass_state from `consult_like` or any other graded consult step.
* **DOES NOT Job report display:** **UI API + frontend** at runtime from `job_data` + grades/trail — not server-stored HTML. [AST-307](https://linear.app/astralcareermatch/issue/AST-307/job-analysis-report-modal-recommended-job-detail) modal. `builder.py` = resume/cover print only (unchanged).
* DOES NOT worry about **Board jobs, will be handled upstream.**
* Does **not** transition jobs to `BUILD_ARTIFACTS` (no dispatch, no `consult_like` pass_state).
* Does **not** run artifact daisy chains — those start only after UI approval → `BUILD_ARTIFACTS`.
* Does **not** pre-build HTML report files on the server.
* Does **not** replace `agent_responses` or grade blobs.
* Prompt prose: [AST-313](https://linear.app/astralcareermatch/issue/AST-313/artifact-pipeline-prompt-authoring) / Manage Tasks.

## Acceptance criteria

1. `consult_like` pass → `PASSED_LIKE` only (grep/config: no path sets `BUILD_ARTIFACTS` on LIKE pass).
2. `analysis_upshot` dispatch: `PASSED_LIKE` → `RECOMMENDED` when JSON saved.
3. Failure → `PASSED_LIKE_RETRY`, not `RECOMMENDED`.
4. **Regression:** No scheduled/dispatch/consult path assigns `BUILD_ARTIFACTS` without a documented UI transition (artifact $$ gate).

## Dependencies and blockers

* `PASSED_LIKE`, `PASSED_LIKE_RETRY`, `RECOMMENDED` in `JOB_STATES`; `BUILD_ARTIFACTS` prior state must include `RECOMMENDED` (UI transition only — sibling workflow).
* [AST-307](https://linear.app/astralcareermatch/issue/AST-307/job-analysis-report-modal-recommended-job-detail), [AST-313](https://linear.app/astralcareermatch/issue/AST-313/artifact-pipeline-prompt-authoring), [AST-302](https://linear.app/astralcareermatch/issue/AST-302/job-state-machine-artifacts-and-candidate-states), [AST-477](https://linear.app/astralcareermatch/issue/AST-477/candidate-resume-structure).

**NOTE: 307 may require a new enhancement ticket to reconcile the build report modal with the design changes driven by this ticket, but it is out of scope for this ticket.**

## Decisions (Susan 2026-05-25)

| Topic | Decision |
| -- | -- |
| Task key | `analysis_upshot` |
| Storage | **JSON in** `job_data`, schema-driven report |
| Model | **Agent-bound** (existing pattern) |
| Retry | `PASSED_LIKE_RETRY`; claim `PASSED_LIKE` + score floor → `RECOMMENDED` when saved |
| Tokens | Spend freely now; per-candidate caps later |
| Board jobs | Company + website + LIKE required; dealbreaker if employer not explicit |
| Report render | **UI API + frontend at runtime**; `builder.py` = resume/cover print only |
| **“Approved” =** `BUILD_ARTIFACTS` | **Definitively the same state.** UI label may say Approved / In Progress; DB state is `BUILD_ARTIFACTS`. Set **only** by **explicit candidate action in the UI** — **never** as `pass_state` or side effect of `consult_like`, `analysis_upshot`, or any other dispatch task (**$$**). Dispatcher **claims** `BUILD_ARTIFACTS` only after the user has approved. |

---

## Original brief

Susan (2026-05-25): Job REPORT via Estelle Opus upshot. Pipeline: `PASSED_LIKE` **→** `RECOMMENDED`. User approval for artifacts is separate; `BUILD_ARTIFACTS` is UI-only, not dispatch-driven.

### Comments

#### chuckles — 2026-05-26T20:24:45.091Z
`origin/dev` @ `8e696a4a` — AST-478 work already on dev (prep-uat merge `930e2654`). Deleted `ftr/AST-478-synthesize-job-analysis-report-estelle-opus-upshot`.

Engineers — merge into `dev-<agent>`: `git fetch origin && git checkout dev-<agent> && git merge origin/dev` (not rebase unless Susan directs).

— Chuckles

#### chuckles — 2026-05-25T04:45:46.461Z
## do-all-the-things — run complete

**Parent [AST-478](https://linear.app/astralcareermatch/issue/AST-478)** → **User Testing** @ Susan.

| Child | Engineer | End state |
|-------|----------|----------|
| AST-479 | Hedy | User Testing |
| AST-480 | Ada | User Testing |
| AST-481 | Katherine | User Testing |

**Integration:** `origin/ftr/AST-478-synthesize-job-analysis-report-estelle-opus-upshot` @ **`fe8e51eb`** · local **`dev`** @ **`930e2654`** · **`sub/*` deleted**

**Notable fixes during run:** 481 blocked until 479/480 code landed; Betty §5b pytest drift; Radia fix-now `REVIEW_LIKE` + `RECOMMENDED`; rollup merge conflicts; Betty branch-coverage + consult tracker/test alignment on ftr.

**Still out of scope:** AST-313 prompt authoring · UI Approve → `BUILD_ARTIFACTS` epic.

UAT checklist in comment above (**UAT Ready**).

— Chuckles

#### chuckles — 2026-05-25T04:45:37.173Z
## UAT Ready — Chuckles

All **3** child branches merged into parent branch; child **`sub/*`** deleted from origin.

**Parent branch:** `origin/ftr/AST-478-synthesize-job-analysis-report-estelle-opus-upshot` @ **`fe8e51eb`**

**Merged in order (rollup + Betty coverage fixes):**
1. **AST-479** — PASSED_LIKE / RECOMMENDED / consult_like pass
2. **AST-480** — `analysis_upshot` dispatch + `job_data.analysis_upshot` persist
3. **AST-481** — JAR runtime render + Recommended list

**Local `dev`:** merge commit **`930e2654`** (prep-uat §8). Restart app if running.

**Radia audit:** deferred this run — Susan may request **`audit-linear AST-478`** during UAT.

## Manual test steps

1. **Prereq:** Candidate with a job that has completed GET/DO/LIKE (or seed dev DB). Restart backend + frontend on local **`dev`**.
2. **AC1 — LIKE → PASSED_LIKE:** Run **`consult_like`** (or full consult through LIKE). Confirm job state **`PASSED_LIKE`**, **not** `BUILD_ARTIFACTS`. Grep/admin: no task `pass_state` sets `BUILD_ARTIFACTS` on LIKE.
3. **AC2 — synthesis:** With job in **`PASSED_LIKE`** and score above floor, run dispatch **`analysis_upshot`** (Manage Tasks prompt may still need **AST-313** — if task errors on missing prompt, note and use stub). On success: **`job_data.analysis_upshot`** JSON present; state **`RECOMMENDED`**.
4. **AC3 — retry:** Force technical failure (e.g. bad prompt / API off). State **`PASSED_LIKE_RETRY`**, not **`RECOMMENDED`**; no upshot blob written.
5. **AC4 — regression:** Confirm no automated path sets **`BUILD_ARTIFACTS`** (artifact $$ only after future UI Approve).
6. **UI — Recommended:** Jobs in **`RECOMMENDED`** appear on Recommended list; row shows Skip / View Job Analysis (**AST-481** `REVIEW_LIKE`).
7. **UI — Job Analysis Report:** Open report for job with upshot JSON — sections render (takes, whole-JD upshot, segments, questions, caveats). Empty/missing upshot shows neutral copy.
8. **Deferred:** Approve → **`BUILD_ARTIFACTS`** button (separate epic). **`builder.py`** still resume/cover only.

If testing fails on `dev`: `git reset --hard origin/dev` then re-merge ftr when fixed.

— Chuckles

#### betty — 2026-05-25T04:39:37.585Z
## Component tests green (consult mocks / tracker layering)

**What broke at `bd5bd60`:** Tests patch `consult_mod.tracker.get_job` / `tracker.get_company` (and `_run_analysis_upshot_batch` already calls `tracker.get_company`), but **`render_verdict` still imported DB `get_job` / `get_company`**, so monkeypatches never applied. **`tracker` had no `get_company` / `append_agent_response`** module attrs, so `monkeypatch.setattr(consult_mod.tracker, "get_company", …)` raised `AttributeError`.

**Fix:** Thin **tracker facades** (`get_company`, `append_agent_response`, `list_timesheets`) delegating to `database`, and **`consult.py` routes** `render_verdict`, `_run_batch_consult`, cover-letter hydration, and `list_timesheets` through **`tracker.get_job` / `tracker.get_company`** (no direct `consult → database` imports for those paths).

`scripts/testing/run_component_tests.sh` → **exit 0**, Python + Vitest + **per-file branch coverage OK**.

Branch pushed to **`origin/ftr/AST-478-synthesize-job-analysis-report-estelle-opus-upshot`** (tips with merge atop current `dev-betty` for full gate).

Canonical product commit for the façade delta: **`36d1e9f6`** (*fix(AST-478/486): route consult reads through tracker facades*) — cherry-pick that onto older `bd5`-only snapshots if needed without merging all of dev.

#### betty — 2026-05-25T04:34:24.089Z
**dev-betty integration + QA follow-up**

- Merged `origin/ftr/AST-478-synthesize-job-analysis-report-estelle-opus-upshot` into `dev-betty`.

- **Prod fix:** `_run_analysis_upshot_batch` was calling bare `get_job` / `get_company` (NameError); now uses `tracker.get_job` / `tracker.get_company` (`src/core/consult.py`).

- **Tests:** Consult component tests now monkeypatch `consult_mod.tracker` for `get_job`, `get_company`, `append_agent_response`, and `list_timesheets` (delegation moved under tracker). Added `TestBoardRegistryAdoptedBranches` in `tests/component/utils/test_config.py` for `list_adopted_boards` / `get_board_entry`: explicit `adopted:false`, missing `adopted` key, and `adopted:true`; unknown board key → `None`.

- `./scripts/testing/run_component_tests.sh` full run: green; Per-file branch coverage OK for locked files including `src/utils/config.py`.

- Same fix cherry-picked to feature branch and pushed: `bd5bd60e` on `origin/ftr/AST-478-synthesize-job-analysis-report-estelle-opus-upshot` (matching commit on dev-betty: `0e6fc706`).

#### betty — 2026-05-25T04:29:17.479Z
Cherry-picked **config** branch-coverage tests pushed to `origin/ftr/AST-478-synthesize-job-analysis-report-estelle-opus-upshot`:

`246787e439b683c201328831a03e46df663338af`

(`dev-betty` has the same patch as `f9f8ae61507e8f985914be276bd032f086653380`.)

#### betty — 2026-05-25T04:25:51.151Z
**Publish tip (`prep-uat` coverage gate):** `origin/ftr/AST-478-synthesize-job-analysis-report-estelle-opus-upshot` @ **`aaf6136119bba8bd55b7acdc7660e61b61b27cc6`** (cherry-pick of **`14de2694a582ebc188f24b089452fde81376e2ed`** from `dev-betty`).

**Verification:** `./scripts/testing/run_component_tests.sh` — **986** pytest + frontend Vitest; **Per-file branch coverage OK**.

Betty.

#### chuckles — 2026-05-25T04:07:30.975Z
## do-all-the-things — run status (prep-uat blocked)

### Completed
| Stage | Result |
|-------|--------|
| Dispatch | 3 children (AST-479 Hedy, AST-480 Ada, AST-481 Katherine) |
| plan-astral + validate-plan | All **Plan Approved** |
| build-astral | **Code Complete** on all three (480 folded 479 config when 479 sub was docs-only) |
| qa-astral + test-astral | **Tests Passed** (481 needed Betty §5b pytest/bible fix) |
| review-astral | **Review Posted** (481 fix-now: `RECOMMENDED` in `REVIEW_LIKE` — resolved) |
| resolve-astral | All children **User Testing** |
| rollup-child | **ftr** tip **`db2e395b`** — 479 → 480 → 481 (480/481 merge conflicts resolved on ftr) |

### Blocked — prep-uat §6
`./scripts/testing/run_component_tests.sh` on **`origin/ftr/AST-478-synthesize-job-analysis-report-estelle-opus-upshot`**:
- **927/927 pytest passed** (second run; first run had 3 flaky roster DB-order failures)
- **Per-file branch coverage gate failed** (100% required):
  - `src/utils/config.py` — **92.5%**
  - `src/core/consult.py` — **88.6%**
  - `src/core/roster.py` — **88.4%** (likely pre-existing drift; not AST-478-owned)

**Not done:** delete `sub/*`, merge ftr → local `dev`, parent **User Testing** @ Susan, §6.5 audit.

### Susan / Betty next
Add branch-coverage tests for new **`analysis_upshot`** / **`PASSED_LIKE`** / **`RECOMMENDED`** paths (especially `consult._run_analysis_upshot_batch`), re-run harness on ftr, then **`prep-uat AST-478`**.

### Out of epic scope (unchanged)
- **AST-313** — Manage Tasks prompt for `analysis_upshot`
- UI **RECOMMENDED → BUILD_ARTIFACTS** Approve workflow

— Chuckles

#### chuckles — 2026-05-25T02:38:43.708Z
## Dispatch — Chuckles

Dispatched **3** child tickets from the approved definition.

| Ticket | Title | Assigned to | Branch | Blocked by |
|--------|-------|-------------|--------|------------|
| AST-479 | Job states PASSED_LIKE RECOMMENDED and consult_like pass | Hedy | `sub/AST-478/AST-479-job-states-passed-like-recommended-and-consult-like-pass` | — |
| AST-480 | analysis_upshot consult dispatch and job_data persist | Ada | `sub/AST-478/AST-480-analysis-upshot-consult-dispatch-and-job-data-persist` | AST-479 |
| AST-481 | Job Analysis Report runtime render from job_data | Katherine | `sub/AST-478/AST-481-job-analysis-report-runtime-render-from-job-data` | AST-479, AST-480 |

**Assignment rationale:**
- **Hedy:** `JOB_STATES`, `consult_like` pass_state, `RECOMMENDED_JOB_STATES` / manifest — foundation before dispatch + UI.
- **Ada:** `analysis_upshot` task, `consult` routing, `do_task` + `job_data` persist.
- **Katherine:** AST-307 JAR + API runtime report render; blocked on state constants + JSON field contract.

**Related:** **AST-313** (prompt/schema) — Susan; not a child.

**Git (authoritative):**
- Parent: `origin/ftr/AST-478-synthesize-job-analysis-report-estelle-opus-upshot`
- Children: `origin/sub/AST-478/…` as above

**do-all-the-things** run starting — plan stage next.

— Chuckles

#### chuckles — 2026-05-25T02:28:47.642Z
Recorded clarification: **Approved = `BUILD_ARTIFACTS`** (one state). Only the **UI** may transition into it; **no task dispatch** sets `BUILD_ARTIFACTS` (including `consult_like` → must stay `PASSED_LIKE`). Dispatcher **claims** `BUILD_ARTIFACTS` after user approval for artifact $$ work.

Description + Decisions table updated.

— Chuckles

#### chuckles — 2026-05-25T02:26:04.585Z
Integrated your Open questions answers into the Description:
- Resolved **`analysis_upshot`**, JSON on **`job_data`**, **`PASSED_LIKE_RETRY`**, score-floor claim on **`PASSED_LIKE`**
- Report = **runtime UI/API render** (not server-stored HTML); **`builder.py`** unchanged for resume/cover print
- Board jobs: employer explicit + company/website/LIKE context required
- Replaced Open questions with **Decisions** table; assignee back to you for approval

If this matches intent, move to **Todo** when ready (or say if you want a sibling ticket for RECOMMENDED→APPROVED→READY first).

— Chuckles

#### chuckles — 2026-05-25T01:59:22.154Z
Definition draft ready for review. Key decisions made:
- Pipeline gate: **`PASSED_LIKE` → synthesis (Opus) → `RECOMMENDED`** — restores PASSED_LIKE as queue state; stops LIKE → BUILD_ARTIFACTS auto artifact run
- Upshot is **job_data** + **AST-307** top section, not builder HTML
- **`consult_like` pass_state** must align (→ PASSED_LIKE)

**6 open questions** in Description (task_key, storage shape, model, retry, token budget, board jobs).

Related workflow (**RECOMMENDED → APPROVED → READY**) is a separate define pass — this ticket only covers the analysis recap step.

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
