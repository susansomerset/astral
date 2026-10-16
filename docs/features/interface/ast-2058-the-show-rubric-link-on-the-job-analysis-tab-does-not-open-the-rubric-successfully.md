# AST-2058 — the "show rubric" link on the job analysis tab does not open the rubric successfully.

<!-- linear-archive: AST-2058 archived 2026-10-16 -->

## Linear archive (AST-2058)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2058/the-show-rubric-link-on-the-job-analysis-tab-does-not-open-the-rubric  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

I get a popup with the vector title but: `No rubric found for this vector`

## As-is

On the Job Analysis report (and the agent story tab, which uses the same header), clicking **show rubric** next to a vector opens `RubricModal` with the right title, but the body always reads `No rubric found for this vector.`

Root cause read (origin/dev `06df211db`): `AgentAnalysisHeader.tsx` gets rubric **content** from `candidates[].candidate_data.artifacts[rubricArtifact]` in `CandidateContext`. That list comes from `GET /api/candidates`, which returns the raw `candidate_data` blob. Since AST-723, rubric criteria live in the `rubric_vector` table, not the artifacts blob, and they are only overlaid into `artifacts` by `hydrate_rubric_artifacts_for_response`, which runs on the single-candidate `GET /api/candidates/<id>` route and not on the list route. So the live list is empty. The fallback is the job-carried `{prefix}_rubric` snapshot (AST-1063), which intentionally leaves out `content`. With both sources empty, `content` is `null` and the modal shows the fallback text.

## To-be

**show rubric** opens the modal with the vector's current rubric prompt (criterion `content`) for the selected candidate, matched by label or code the same way it is today. The fallback text only appears when that vector really has no rubric row.

## Proposed steps

1. In `AgentAnalysisHeader`, stop treating `CandidateContext`'s list payload as the source of rubric content. When the modal opens, load the hydrated candidate artifacts from `GET /api/candidates/<selectedId>`, which already runs `hydrate_rubric_artifacts_for_response`, and build `liveList` from that `artifacts[rubricArtifact]`.
2. Keep the existing match order: live row by vector, then live row by the job-carried row's `code`, then the job-carried row.
3. Show a loading state in the modal while the fetch is in flight, so the fallback text doesn't flash before the content arrives.
4. Check both callers: `JobAnalysisReportModal` (job analysis tabs) and `AgentStoryTab`.

## Component scope

* `src/ui/frontend/src/components/AgentAnalysisHeader.tsx` (modified): load rubric content from the hydrated candidate detail instead of the unhydrated list payload in `CandidateContext`.
* `src/ui/frontend/src/components/RubricModal.tsx` (modified, if needed): tell "still loading" apart from "no rubric found."

## Technical scope

* `AgentAnalysisHeader.tsx`: modified component function. Add a fetch, triggered when the modal opens, of the selected candidate's hydrated artifacts, and point the `liveList` derivation at it. The props stay the same, so `JobAnalysisReportModal` and `AgentStoryTab` need no changes. The API endpoint already exists, so no backend change is expected.
* `RubricModal.tsx`: possibly a modified props interface (a loading flag), so a pending fetch doesn't render the not-found fallback.

## Ancestor candidates

- [ ] AST-1063 — Job-carried rubric hydration for list columns (`docs/features/interface/ast-1063-job-carried-rubric-hydration-for-list-columns.md`). Owns the `rubricItems` vs live `rubricArtifact` split in `AgentAnalysisHeader` and the snapshot that omits `content`.
- [ ] AST-723 — Rubric vector read/write cutover (`docs/features/auditor/ast-723-rubric-vector-read-write-cutover.md`). Moved rubrics out of `candidate_data.artifacts`. Only the detail GET is hydrated, so the list-backed reader broke.
- [ ] AST-1327 — Fix missing vector grades in rubric headers (`docs/features/interface/ast-1327-fix-missing-vector-grades-in-rubric-headers-ast-1321.md`). Added the `rubricItems` prop and the label/content precedence in `AgentAnalysisHeader`.
- [ ] AST-1200 — Restore rubric criteria prompts on Artifacts pages (`docs/features/interface/ast-1200-restore-rubric-criteria-prompts-on-artifacts-pages.md`). Same symptom family (rubric prompt bodies missing after the cutover), fixed on the ArtifactEditor path only.
- [ ] AST-352 — Job modal updates (`docs/features/interface/ast-352-job-modal-updates.md`). Original `RubricModal` and **show rubric** link.
- [ ] AST-950 — Analysis tab grades confidence (`docs/features/interface/ast-950-analysis-tab-grades-confidence.md`). Analysis tab header that renders the link.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
