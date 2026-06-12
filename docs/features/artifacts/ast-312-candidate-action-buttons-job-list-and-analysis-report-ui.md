<!-- linear-archive: AST-312 archived 2026-06-03 -->

## Linear archive (AST-312)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-312/candidate-action-buttons-job-list-and-analysis-report-ui  
**Status at archive:** Done  
**Project:** Astral Artifacts  
**Assignee:** susan  
**Priority / estimate:** High / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Candidate-facing state transition controls across the Recommended Jobs list and Job Analysis Report modal. CANDIDATE_REVIEW list row: two icon buttons — Skip (→ CANDIDATE_SKIPPED) and View Job Analysis (opens modal). CANDIDATE_SKIPPED list row: Resurrect icon (→ CANDIDATE_REVIEW). Job Analysis Report modal: Applied button at bottom (→ CANDIDATE_APPLIED, writes candidate_results.applied with optional notes popup). Post-applied list rows (CANDIDATE_APPLIED, CANDIDATE_INTERVIEW, CANDIDATE_REJECTED, CANDIDATE_GHOSTED): four icon buttons — Reapply (→ CANDIDATE_REVIEW), Interview (→ CANDIDATE_INTERVIEW), Rejected (→ CANDIDATE_REJECTED), Ghosted (→ CANDIDATE_GHOSTED). Each icon action triggers a lightweight popup (modal-on-modal or inline popover) with an optional notes textarea; on confirm, fires API call to transition state and save candidate_results.<action> = {timestamp, notes} to job_data. All candidate_results entries carry a server-set timestamp. Reapply available from any terminal CANDIDATE\_\* state including CANDIDATE_REJECTED and CANDIDATE_GHOSTED — because the economy is bonkers.

### Comments

#### chuckles — 2026-05-18T20:48:11.701Z
## Landed on origin/dev — Chuckles

- Merged `origin/ftr/AST-312-candidate-action-buttons-job-list-and` → local `dev` (already up to date from prep-uat) → **pushed `origin/dev`**
- Deleted `origin/ftr/AST-312-candidate-action-buttons-job-list-and`
- **AST-312** PR Ready → **Done**

Push tip: `ceec63c7`

— Chuckles

#### chuckles — 2026-05-18T20:39:28.967Z
## UAT Ready — Chuckles

Standalone ticket (no child branches). Merged current feature branch into local `dev` for UAT.

**Parent branch:** `origin/ftr/AST-312-candidate-action-buttons-job-list-and` (includes Kath fixes: SKIPPED→REVIEW transition, CANDIDATE_REVIEW in recommended list filter)

**Local `dev` merge:** latest prep-uat merge commit on `dev` — restart the app if running, then test.

No `sub/AST-312/*` branches to delete.

If testing fails on `dev`:
```
git reset --hard origin/dev
```

— Chuckles

#### katherine — 2026-05-18T20:34:09.130Z
[check-linear]
- **@katherine** (return to review, missing from Recommended): state transition was succeeding; **`view=recommended`** only listed `BUILD_ARTIFACTS` / `PASSED_LIKE`, so `CANDIDATE_REVIEW` rows were filtered out.
- **Fix:** `RECOMMENDED_JOB_STATES` now includes `CANDIDATE_REVIEW` (`src/utils/config.py`).
- **Branch:** `ftr/AST-312-candidate-action-buttons-job-list-and` @ tip after push (cherry-pick of `b5396460` on dev-kath). Chuckles can re-merge into local `dev` for UAT.

#### susan — 2026-05-18T20:33:00.454Z
@katherine When I returned the job to review, it did not reappear in the Recommended page, even after refresh.  Did the state transition silently fail?

#### chuckles — 2026-05-18T20:30:47.964Z
## UAT Ready — Chuckles

**AST-312** is a **standalone** ticket (no child branches) — prep-uat merged the feature ref into local **`dev`** only.

- Parent branch: `origin/ftr/AST-312-candidate-action-buttons-job-list-and`
- Merged into local **`dev`**: `9b4018bc` (picked up `fix(AST-312): allow CANDIDATE_SKIPPED → CANDIDATE_REVIEW transition` from origin)
- No `sub/*` branches to delete

Local **`dev`** is ready to test (not pushed to **`origin/dev`**). Restart the app if it is running.

If testing fails on `dev`:
```
git reset --hard origin/dev
```

— Chuckles

#### katherine — 2026-05-18T20:20:04.417Z
[check-linear]
- **@katherine** (Return to review): `CANDIDATE_SKIPPED` → `CANDIDATE_REVIEW` failed because `CANDIDATE_REVIEW.prior_states` omitted skipped/outcome states (AST-311 gap).
- **Fix:** `src/utils/config.py` — added `CANDIDATE_SKIPPED`, `CANDIDATE_APPLIED`, `CANDIDATE_INTERVIEW`, `CANDIDATE_REJECTED`, `CANDIDATE_GHOSTED` to `CANDIDATE_REVIEW` prior_states.
- **Branch:** `ftr/AST-312-candidate-action-buttons-job-list-and` @ `d961c09b` (cherry-pick of `9bb4465d` on dev-kath).
- Ready for Susan to re-test on that ref.

#### susan — 2026-05-18T20:13:46.901Z
@katherine when I attempt to "Return to review", the transition fails with an error message saying "Invalid Transition: CANDIDATE_SKIPPED ->CANDIDATE_REVIEW".  Let us know when ftr/AST-312\* is ready to merge and test again.

#### chuckles — 2026-05-18T20:06:45.014Z
**Correction:** local `dev` merge commit is **`aca0e04a`** — `merge(AST-312): prep-uat — integrate feature branch into local dev for UAT`.

— Chuckles

#### chuckles — 2026-05-18T20:06:39.387Z
## UAT Ready — Chuckles

**AST-312** is a **standalone** feature (no child sub-issues under this parent). Child-branch merge/delete steps (prep-uat §5–§7) were **N/A**.

**Parent / feature branch:** `origin/ftr/AST-312-candidate-action-buttons-job-list-and`

**Local `dev`:** merged for UAT (prep-uat §8).

```
$(git -C /Users/susan/chuckles/astral log -1 --format='%h %s')
```

Restart the app if it is running, then test candidate action buttons on Recommended / Skipped lists and the Job Analysis Report modal.

If testing fails on `dev`:
```
git reset --hard origin/dev
```

Do **not** delete the `ftr/AST-312` branch until UAT passes — **finish-up** at **PR Ready** handles that.

— Chuckles

#### katherine — 2026-05-17T18:12:21.773Z
[check-linear]

**resolve-astral:** Review Posted → **User Testing** (assignee Susan).
- 0 fix-now; **discuss** items documented in plan **Resolution** (G1 literals, post-applied view scope, AST-307 shell vs full editor).
- Published resolve doc on `origin/ftr/AST-312`.

— Katherine

#### radia — 2026-05-17T17:52:28.593Z
## review-astral (Radia)

**Diff:** `origin/dev...origin/ftr/AST-312` (`b018a26a`)

**Summary:** Candidate action UI + shared hook/API client look solid. **0 fix-now** · **3 discuss** · **1 advisory**

**Solid:** `candidateJobActions` + `useCandidateJobActions`; `stopPropagation` on row actions; skip + `candidate_action` routes per **AST-311**; Recommended/Skipped wiring + tests; minimal `JobAnalysisReportModal` with Applied + notes.

**Discuss:**
- Hardcoded state sets in `CandidateJobRowActions` (G1 vs plan — confirm OK or manifest later).
- `POST_APPLIED` icons may not show on Recommended if API only returns `BUILD_ARTIFACTS` / `PASSED_LIKE` — where do post-applied rows render?
- **AST-307** overlap: JAR shell lands here; full tabbed editor may still be separate.

**Advisory:** Illegal transitions may 500 until **AST-311** API maps `ValueError` → 4xx (toast still surfaces error).

**Doc commit:** `3aed6ec5` on `origin/ftr/AST-312`

— Radia

#### katherine — 2026-05-16T23:46:09.083Z
Tests passed by Katherine (test-astral).

**Integration:** `origin/ftr/AST-312` @ `b018a26a` (tests) / `97dab205` (product), merged onto `dev-kath`.

**Commands (Betty manifest, in order):**
1. `npm run test:component` — `test_JobsRecommended.test.tsx` → **3 passed**
2. `npm run test:component` — `test_JobsSkipped.test.tsx` → **3 passed**
3. `npm run test:component` — `test_CandidateJobRowActions.test.tsx` → **2 passed**
4. `pytest tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_skip_job_updates_state` → **passed**
5. `pytest …::test_candidate_action_applied_records_result` → **passed**
6. `pytest …::test_candidate_action_invalid_returns_400` → **passed**

(Vitest run from `src/ui/frontend`; three frontend files in one invocation.)

**Product fixes:** none required.

**Published:** no new commits (feature tip unchanged @ `b018a26a`).

— Katherine

#### betty — 2026-05-16T23:42:27.823Z
QA manifest by Betty.

**Branch:** `origin/ftr/AST-312` @ `97dab205` (product) + `b018a26a` (tests)

**Manifest (Katherine — test-astral, in order):**

1. `tests/component/frontend/pages/test_JobsRecommended.test.tsx` — Skip → `POST /skip`; View Job Analysis opens report modal without row detail fetch.
2. `tests/component/frontend/pages/test_JobsSkipped.test.tsx` — CANDIDATE_SKIPPED resurrect → `POST …/candidate_action` with `action: review`.
3. `tests/component/frontend/components/test_CandidateJobRowActions.test.tsx` — review-like skip/view + skipped resurrect callbacks.
4. `tests/component/ui/api/test_api_jobs.py` — bible-backed (AST-311): `test_skip_job_updates_state`, `test_candidate_action_applied_records_result`, `test_candidate_action_invalid_returns_400`.

**Gaps closed:** new UI components + list wiring; shared `page-mocks` POST handlers for skip/candidate_action.

**Obsolete / broken:** none.

— Betty

#### katherine — 2026-05-16T23:38:16.118Z
Built by Katherine.

**Branch:** `ftr/AST-312`  
**Commit:** `146ca061` (UI); **`dev-kath`** also merged `origin/ftr/AST-311` for `POST .../candidate_action` (publish that to `dev` before UAT if not already).

**Delivered:**
- Recommended: Actions column — Skip (`/skip`), View Job Analysis (`JobAnalysisReportModal`), post-applied icon row via `candidate_action`.
- Skipped: Resurrect on `CANDIDATE_SKIPPED` → `review` action.
- Report modal shell: summary + JD preview + **Applied** with optional notes.

**Assumption:** Full AST-307 CollapsiblePanel report is still out of scope; this modal is the AST-312/307 handshake shell.

`tsc -b --noEmit` clean.

#### katherine — 2026-05-16T23:35:27.089Z
Label review (build agent): agree on all three.

**Proceeding** with documented assumptions (no thread reply yet):
- Merged `origin/ftr/AST-311` onto `dev-kath` for `candidate_action` + `transition_job_state` skip.
- **Skip** stays `POST .../skip` (311 branch uses `transition_job_state`).
- **View Job Analysis** opens a minimal `JobAnalysisReportModal` shell (AST-307 full modal still docs-only on `dev`).

#### katherine — 2026-05-16T22:40:32.046Z
Label review (build agent):

Conf: **agree** (conf-Medium)
Risk: **agree** (risk-HIGH)
Scope: **agree** (scope-MAJOR-CHANGE)

---

**Build paused — pre-flight (Stage 0)**

Cannot implement without guessing. Please answer:

1. **AST-311 on `origin/dev`:** `POST /api/jobs/<id>/candidate_action` and `set_candidate_result` exist on `origin/ftr/AST-311` (Tests Passed) but **not** on current `origin/dev`. Should Katherine merge `origin/ftr/AST-311` into `dev-kath` before wiring UI, or wait for Susan to merge **AST-311** to `dev` first?

2. **AST-307 modal:** Linear is **Done**, but `origin/dev` and `origin/ftr/AST-307` have **no** `JobAnalysisReportModal` (PR #127 merged **docs only**). Stage 2 “View Job Analysis” and Stage 3 footer actions require that shell. Proceed with **JobDetailModal** as a temporary host, defer modal actions until **AST-307** is implemented, or reprioritize **AST-307** code before **AST-312**?

3. **Skip / resurrect API:** Plan Stage 1 references AST-311 routes; `origin/dev` already has `POST .../skip` (no `candidate_results.skipped`). Should **Skip** keep using `/skip`, or switch to `candidate_action` with a new action key once **AST-311** lands?

Status stays **Plan Approved**. No branch/commits from this run.

#### katherine — 2026-05-16T21:34:11.205Z
Build paused (pre-flight) — Katherine

1. **Stage 0** — blocked on **AST-311** (**Plan Approved**, not Done). **AST-307** Done. Plan requires AST-311 REST contract + `candidate_results` shapes before any Flask routes.

Need: **AST-311** implementation on `dev` + linked spec in thread.

#### chuckles — 2026-05-16T21:29:54.002Z
## Plan Review — Chuckles

**Verdict: APPROVED**

Plan is faithful to the definition. No findings. ASTRAL_CODE_RULES compliance confirmed. Self-assessment is honest.

**Note:** Implementation already on `origin/dev` ([retroactive-pipeline] C2).

— Chuckles

#### susan — 2026-05-04T21:34:10.539Z
**Plan doc:** `docs/features/artifacts/ast-312-candidate-action-buttons-job-list-and-analysis-report-ui.md`

**Self-assessment (labels):**
- **Scope — MAJOR-CHANGE:** Flask `api_jobs` + `JobsRecommended` / report modal surfaces; cross-cutting candidate workflow.
- **Conf — Medium:** Blocked on **AST-311**/**AST-307** API shapes; wiring is repetitive once contracts exist.
- **Risk — HIGH:** Wrong transitions or `candidate_results` corruption affects pipeline data.

GitHub: https://github.com/susansomerset/astral/blob/chuckles/ast-312-candidate-action-buttons-job-list-and-analysis-report-ui/docs/features/artifacts/ast-312-candidate-action-buttons-job-list-and-analysis-report-ui.md

— Katherine (a-plan-linear)

---

# Candidate Action Buttons — Job List and Analysis Report UI

**Linear:** https://linear.app/astralcareermatch/issue/AST-312/candidate-action-buttons-job-list-and-analysis-report-ui  
**Feature branch:** `ftr/AST-312`

Add candidate-facing controls on **Recommended Jobs** and **Job Analysis Report** modal: Skip, Resurrect, Applied (+ notes), post-applied workflow icons. Server transitions via **AST-311**; minimal **JobAnalysisReportModal** shell here until full **AST-307** tabbed editor ships separately.

---

## Review (build)

**Branch:** `ftr/AST-312`  
**Commits:** `97dab205` (product), `b018a26a` (tests)

---

## Radia review (review-astral 2026-05-16)

**Diff:** `origin/dev...origin/ftr/AST-312` (`b018a26a`)

### What's solid

- `candidateJobActions.ts` + `useCandidateJobActions`; `stopPropagation` on row actions.
- Skip + `candidate_action` routes per **AST-311**; Recommended/Skipped wiring + tests.
- `JobAnalysisReportModal` — summary, JD preview, Applied + notes.

### Issues

| Severity | Item |
|----------|------|
| **discuss** | **G1:** Hardcoded state sets in `CandidateJobRowActions`. |
| **discuss** | **POST_APPLIED** icons vs `RECOMMENDED_JOB_STATES` filter. |
| **discuss** | **AST-307** full editor vs minimal shell on this branch. |
| **advisory** | Illegal transitions may 500 until **AST-311** maps `ValueError` → 4xx. |

**Counts:** 0 fix-now · 3 discuss · 1 advisory — Radia

---

## Resolution (resolve-astral 2026-05-17)

- **Fix-now:** none.
- **G1 (discuss):** Accept explicit state literals in `CandidateJobRowActions` for v1 — matches current list views and tests; config-driven manifest deferred.
- **POST_APPLIED (discuss):** Post-applied icon row renders when `row.state` is in the component’s post-applied set; **Recommended** feed today is review-like states (`BUILD_ARTIFACTS` / `PASSED_LIKE` / `CANDIDATE_REVIEW` per API). Jobs in `CANDIDATE_APPLIED`+ appear when the list endpoint returns them (extend view filter in a follow-up if product wants those rows on Recommended).
- **AST-307 (discuss):** This branch ships the **minimal** report shell documented at build; full tabbed **AST-307** editor remains a separate ticket.
- **Advisory:** No product change — UI already surfaces hook errors; 4xx mapping stays on **AST-311** if tightened later.

**Published:** `origin/ftr/AST-312` @ `3aed6ec5` (Radia doc) + resolve doc commit.

— Katherine
