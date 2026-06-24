# AST-591 — UAT: Generate Artifacts must transition job to BUILD_ARTIFACTS (405 + wrong UX)

<!-- linear-archive: AST-591 archived 2026-06-23 -->

## Linear archive (AST-591)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-591/uat-generate-artifacts-must-transition-job-to-build-artifacts-405  
**Status at archive:** Done  
**Project:** Astral Artifacts  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-300 — Build Resume Artifact  
**Blocked by / blocks / related:** parent: AST-300

### Description

## What failed

* Clicking **Generate Artifacts** in the Job Analysis Report does not transition the job to **BUILD_ARTIFACTS**; UI appears to open artifact tabs for content that has not been built yet.
* Server log: `POST /api/jobs/<job_id>/generate_artifacts` returns **405 Method Not Allowed**.

## Expected

Recommended list → click job → Job Analysis Report → **Generate Artifacts** → job transitions to **BUILD_ARTIFACTS**, modal closes, job appears **In Progress** on Recommended → batch dispatch builds artifacts → job reaches **CANDIDATE_REVIEW** → clicking from the ready section opens JAR with editable resume and cover letter text.

## Repro

1. Jobs → Recommended; open a **RECOMMENDED** job in Job Analysis Report.
2. Click **Generate Artifacts**.
3. Observe 405 in server log; job state unchanged / wrong UI (empty artifact tabs instead of closing modal and starting build).

## Parent AC (quoted inline)

> A job at **RECOMMENDED** does **not** start the resume chain until the candidate's explicit approval sets **BUILD_ARTIFACTS**.

> On chain success, the job is **CANDIDATE_REVIEW** and the Job Analysis Report shows editable resume draft content loaded from `resume_content`.

## Boundaries

* Does **not** change Preview Materials (AST-581), recommended row click (AST-587), or resume chain wiring (AST-551).
* Does **not** auto-dispatch without explicit Generate Artifacts approval.

### Comments

#### betty — 2026-06-06T04:32:22.130Z
## [fix-uat-qa] no test changes

**Triage:** Dev commit wires `POST …/generate_artifacts` and `POST …/cancel_artifact_build` (AST-562 routes missing on the ftr integration line) and closes JAR after generate/cancel — `TestAst562GenerateCancelRoutes` already exercises all six API paths; `test_JobAnalysisReportModal.test.tsx` already clicks Generate Artifacts and asserts the POST. No bible delta for parent AST-300 §7.13zs.

**Bible:** unchanged

**Tests:** none

**Publish ref:** n/a (no qa commit)

#### katherine — 2026-06-06T04:31:17.956Z
## [fix-uat-dev] report

**Summary:** UAT hit **405** because `POST /api/jobs/<id>/generate_artifacts` was never registered on the `origin/ftr/AST-300-build-resume-artifact` integration line (Flask only exposed GET on `/<job_id>`). Added AST-562 `generate_artifacts` and `cancel_artifact_build` routes calling `start_artifact_build` / `cancel_artifact_build`. After a successful generate or cancel, the Job Analysis Report modal now closes and refreshes the Recommended list so **BUILD_ARTIFACTS** shows under In Progress instead of staying open on empty artifact tabs.

**Publish ref:** `origin/sub/AST-300/AST-591-uat-generate-artifacts-must-transition-job-to-build-artifacts-405-wrong-ux` @ `9cb5b033`

**Files:**
- `src/ui/api/api_jobs.py` — POST `generate_artifacts`, POST `cancel_artifact_build`, tracker imports
- `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` — close modal on generate/cancel success

**Verification:** Joan `store-code-commit` ok; route handlers reviewed against AST-562 plan; ftr-base commit cherry-picks cleanly onto publish ref.

**Open questions:** none

---

_Implementation detail may live in git history on `origin/dev`._
