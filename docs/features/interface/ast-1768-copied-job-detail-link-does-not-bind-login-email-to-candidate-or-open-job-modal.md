# AST-1768 — Copied job detail link does not bind login email to candidate or open job modal

<!-- linear-archive: AST-1768 archived 2026-10-07 -->

## Linear archive (AST-1768)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1768/copied-job-detail-link-does-not-bind-login-email-to-candidate-or-open  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1687 — Copy single page access link from recommended job modal  
**Blocked by / blocks / related:** parent: AST-1687

### Description

## UAT report (verbatim)

\[bug\] I expected the link to open the platform, bind to the authenticated candidate user (e.g. Jolane Abrams), and open on the specific linked-from-job-modal recommended job modal open.  Right now, I log in as [soosomerset@gmail.com](<mailto:soosomerset@gmail.com>) (set on Jolane Abrams profile as a valid email), and it shows me Susan Somerset as a candidate and no direct popup to the job I wanted to look at.

## As-is

Logging in via the copied `/jobs/detail/<id>` link as `soosomerset@gmail.com` (an email set on Jolane Abrams's profile) lands on candidate Susan Somerset and does not open the recommended-job modal for that job.

## To-be

Opening that link binds to the authenticated candidate matching the login (e.g. Jolane Abrams) and opens the recommended-job modal for the linked job.

## Suggested engineer

Katherine Johnson (sibling AST-1696 — Copy detail deeplink from report header)

### Comments

#### radia — 2026-09-27T04:20:42.033Z
[code-rubric] PROCEED (Commit: 2e537f49) magic-link deeplink bind fixed

#### katherine — 2026-09-27T04:19:26.982Z
`origin/sub/AST-1687/AST-1768-copied-job-detail-link-bind-candidate-open-modal` @ `2e537f49` · [bug-repro] red→green verified

#### katherine — 2026-09-27T04:17:53.880Z
`origin/sub/AST-1687/AST-1768-copied-job-detail-link-bind-candidate-open-modal` @ `2e537f49` · all [bug-repro] green

- Env note for test-fix: `~/astral/.venv` is missing `asyncpg` (declared in `requirements.txt`), so every `tests/component/ui` test errors at conftest import. I ran the API repro with a temporary `--target` install; the shared venv is unchanged.
- Lint: one existing `react-hooks/refs` error at `JobsJobDetail.tsx:18` (untouched line, also on the pre-change tree). One `exhaustive-deps` warning on `CandidateContext`'s load effect, matching the existing `[authLoading]` pattern.

#### betty — 2026-09-27T04:15:41.220Z
[bug-repro]
`origin/sub/AST-1687/AST-1768-copied-job-detail-link-bind-candidate-open-modal` @ `63b02b60` · repro lands red, awaits fix

#### joan — 2026-09-27T04:03:27.720Z
[board-joan]  CANON: OK

#### betty — 2026-09-27T04:03:06.883Z
[board-betty] TESTS: REVISE
What: frontend/lib.md § AST-1482 + contexts/pages (CandidateContext, JobsJobDetail) + no bible entry for `/api/candidates/by_email` — missing repro (return path survives a new tab via localStorage; login email binds unique candidate; non-admin host waits on hydration) + broken `test_sessionAuthMark` L75–77 sessionStorage assert, `stytchMock` needs `useStytchUser` + localStorage cleanup, `test_JobsJobDetail` non-admin cases must resolve `/api/candidates` first.

#### katherine — 2026-09-27T04:02:06.632Z
`origin/sub/AST-1687/AST-1768-copied-job-detail-link-bind-candidate-open-modal` @ `d1043f470da59da7035bca5e15c10c03fbce68d9` · return path + candidate bind

#### chuckles — 2026-09-27T04:00:25.598Z
Re-seeded refs: PR #61 merged to dev (2026-09-17) and the ftr/sub branches were deleted, but AST-1687 was never finished-up. Re-created `ftr/AST-1687-copy-single-page-access-link-from-recommended-job-modal` and `sub/AST-1687/AST-1768-copied-job-detail-link-bind-candidate-open-modal` off `origin/dev` (dev already contains all AST-1696 work). UAT-batch flow unchanged — merge-child lands into that ftr; datt prep-uat opens a new PR.

#### katherine — 2026-09-27T03:59:33.239Z
[plan-fix] blocked: publish ref missing — `origin/sub/AST-1687/AST-1768-copied-job-detail-link-bind-candidate-open-modal` no longer exists on origin (sync-child exit 2).

Parent `ftr/AST-1687-copy-single-page-access-link-from-recommended-job-modal` is also gone: PR #61 merged to `dev` 2026-09-17, and its `sub/*` refs were cleaned up with it. The scope widen is in place; I can't publish the plan without a ref, and plan-fix never creates refs.

@chuckles please re-seed the bug ref (likely ORPHANED — target dev, not ftr, since the parent has shipped) and kick this back to plan-fix.

#### chuckles — 2026-09-27T03:57:26.586Z
[check-linear] unblocked: AST-1687's Component and Technical scope now include AST-1768.

- **Auth return path:** `RequireAuth` / `Authenticate` / `sessionAuthMark`, so a logged-out open of `/jobs/detail/<id>` lands back there after login and the modal opens.
- **Candidate bind:** `CandidateContext` / `JobsJobDetail` / `api_candidate.py`, so the selected candidate is the one whose profile email matches the login (e.g. Jolane Abrams).

Kicked: assigned to Chuckles, so it resumes at plan-fix with Katherine.

#### susan — 2026-09-27T03:56:04.039Z
@chuckles Please do the needful to unblock this ticket.

#### chuckles — 2026-09-24T18:13:39.427Z
Plan Discuss still open: [scope-gate] needs parent/bug Component+Technical scope widened for auth return-path and/or candidate bind (or re-file against deeplink epic). Assign this bug to Chuckles after amending.

#### katherine — 2026-09-24T18:12:57.104Z
[scope-gate] AST-1768 cannot be planned inside parent AST-1687 Component/Technical scope.

**Needed for the reported fix (not in scope):**
- Auth return-path restore of `/jobs/detail/<id>` after login (`RequireAuth.tsx` / `Authenticate.tsx` / `sessionAuthMark.ts`) — so the modal host actually mounts after “I log in as …”.
- Candidate selection: either login-email → candidate bind (`CandidateContext` / Stytch session ↔ profile email aliases), or verifying/fixing `JobsJobDetail` + `alignSelectedCandidateForJobCompany` so the open job’s company owner is selected. Neither is a change to the Copy Link chrome.

**Scope lines that do not cover it (AST-1687):**
- Component: only `RecommendedJobReportHeader.tsx` and `JobAnalysisReportModal.tsx` are **modified**; `JobsJobDetail.tsx` is **unchanged expected**; auth/candidate modules are not listed.
- Technical: clipboard assemble + header Copied feedback only — “no new API call.”
- Boundaries / child #1: does **not** own deeplink routing, auth return-path, or any Stytch↔candidate bind.

**Why not within those lines:** Copy Link already writes `origin + /jobs/detail/<jobId>` (AST-1696). Susan’s UAT is post-login landing (wrong candidate + no modal) — that path is AST-1463/1481/1482 territory, excluded here by design.

**Ask:** widen this bug’s (or parent’s) Component/Technical scope to name the auth return-path and/or candidate-bind files and the kind of change, **or** re-parent/re-file against the deeplink epic that owns that behavior. After amending, assign this bug to Chuckles so plan-fix can resume.

@susan — material widen (auth + candidate bind), not a small Chuckles tweak to the copy-chrome row.

---

_Implementation detail may live in git history on `origin/dev`._
