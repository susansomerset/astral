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

## Bug: AST-2259 — Cover admin selected-candidate reload in CandidateContext tests

### As-is

`CandidateProvider — AST-1768 login-email candidate bind` asserts the admin picker only through an in-memory `refresh()` on the same mount (`[bug-repro] binds once per login email — refresh and admin picker are not overridden`). A remount, which is the page reload, is not asserted. `docs/test-bible/frontend/lib.md` § AST-1768 names that describe as “once-per-login” and does not name an admin-reload assertion.

### To-be

One new case in that describe mounts an admin, lets the login-email bind select `c2`, calls `setSelectedId("c1")`, unmounts, and mounts again with the same login, then expects the picked id `c1`. The non-admin bind-over-storage case stays. § AST-1768 names this remount as coverage distinct from same-mount `refresh()`. No edit to `CandidateContext.tsx` — that product change is AST-2258.

### Repro

Same fixture as the existing admin picker test (no database seed): `c1` Susan Somerset and `c2` Jolane Abrams from `GET /api/candidates`; verified login `soosomerset@gmail.com`; `GET /api/candidates/by_email` returns `{ candidate_id: "c2" }`; `is_admin: true`. The current test stops after `setSelectedId("c1")` plus `refresh()` on that hook. The hole is the missing unmount and second `renderHook` with the same wrapper.

### Root cause

The once-per-email guard is a ref on the provider instance. `refresh()` on the same mount never clears it, so that test stays green even when a new mount would run the login-email lookup again and replace the stored pick. The bible row records “once-per-login” without saying the assertion is same-mount only.

### Proposed change

`tests/component/frontend/contexts/test_CandidateContext.test.tsx` only, inside `describe("CandidateProvider — AST-1768 login-email candidate bind")`. Add one `it` after the existing refresh case, reusing `bindWrapper(true, …)` and the by-email → `c2` response:

1. Mount, wait until `selectedId` is `"c2"`.
2. `setSelectedId("c1")`.
3. Unmount.
4. `renderHook` again with the same wrapper.
5. Wait until `candidatesHydrated` is true. Expect `selectedId` to be `"c1"`.

Title: `admin picker survives remount for the same login email`. Do not change the body of the same-mount `refresh()` test or the non-admin test that expects a stored `c1` to become `c2`.

`docs/test-bible/frontend/lib.md` § AST-1768, the login-email bind row only. Extend the Area cell from `match / verified-first / once-per-login / null+fail / unknown id / passthrough` so it also says `admin remount after setSelectedId (not the same-mount refresh())`, and name the new `it` title in the Component tests cell next to the describe name. Do not add a manifest entry and do not edit any other bible section.

Do not modify `src/ui/frontend/src/contexts/CandidateContext.tsx`.

### Blast radius

The new node fails on a tree where a remount still replaces the stored admin id with the by-email id. Turning it green is AST-2258’s `load` change, not a product edit on this ticket. Other cases in the describe, and tests that only set `astral_selected_candidate`, stay as they are. The bible edit is that one table row.

### What must still hold

- Non-admin load still selects the by-email candidate over a stored id (existing test unchanged).
- Same-mount `refresh()` still expects the admin pick `c1` and a single by-email call.
- Verified-first, null/fail, unknown id, and no-Stytch-user cases in the same describe stay.
- § AST-1768 return-path, `JobsJobDetail` hydration, and `by_email` API rows stay.

## Bug: AST-2258 — Keep the admin selected candidate across page reload

### As-is

An admin's sidebar pick is written to `localStorage` (`astral_selected_candidate`), but a full page reload snaps the picker back to the candidate bound to the login email. `CandidateProvider.load` applies that bind on every mount (`bound` wins over the stored id). The once-per-email guard is `boundEmailRef`, so it survives an in-memory `refresh()` and not a document reload.

### To-be

After an admin picks a candidate, reloading the page keeps that candidate. The login-email bind still wins when there is no valid stored id, and when the login email changes. A non-admin still binds to the candidate for their login email on load.

### Repro

Fixture (same rows as the AST-1768 bind tests; no database seed):

- `GET /api/candidates` → `c1` Susan Somerset, `c2` Jolane Abrams.
- Stytch user email `soosomerset@gmail.com` (verified). `GET /api/candidates/by_email?email=soosomerset@gmail.com` → `{ candidate_id: "c2" }`.
- Auth user `is_admin: true`.

Steps: mount `CandidateProvider`, wait until `selectedId` is `c2`, call `setSelectedId("c1")`, unmount, mount again with the same login. Today the second mount selects `c2`. After the fix it stays `c1`, and `localStorage["astral_selected_candidate"]` stays `"c1"`.

### Root cause

`lookupBoundCandidate` returns the by-email id only when `boundEmailRef.current !== loginEmail`, then `load` sets `next = bound ?? stored ?? first`. A reload constructs a new provider, so the ref is `null`, the lookup runs again, and a list id from that lookup replaces the stored admin pick. `setSelectedId` persists only the candidate id, not the login email the bind used.

### Proposed change

`src/ui/frontend/src/contexts/CandidateContext.tsx` only. New key beside `STORAGE_KEY`: `astral_bound_login_email`.

In the async body of `load`, after a non-empty candidate list is in hand and before `lookupBoundCandidate`:

- Read `storedEmail = localStorage.getItem("astral_bound_login_email")` and `storedId = selectedIdRef.current`.
- `storedValid` when `storedId` is a string and `list` contains that `astral_candidate_id`.
- When `isAdmin` and `loginEmail` and `storedEmail === loginEmail` and `storedValid`, set `boundEmailRef.current = loginEmail`. That hits the existing early return in `lookupBoundCandidate`, so this load does not call `/api/candidates/by_email` and `bound` is `null`. The existing `next = bound ?? (kept ? prev : list[0])` then keeps `storedId`.

In the same `_setSelectedId` updater that already writes `astral_selected_candidate`: when `bound` is a non-null string (the lookup applied an id that is in `list`), also `localStorage.setItem("astral_bound_login_email", loginEmail)`. Do not write that key when the lookup was skipped, returned null, or failed. Do not write it from `setSelectedId`.

A changed login email fails the `storedEmail === loginEmail` check, so the lookup runs and its id replaces the stored pick. A missing or not-in-list stored id fails `storedValid`, so the lookup runs. `isAdmin` false never sets the ref early, so every non-admin mount still runs the lookup and `bound` still wins.

`tests/component/frontend/contexts/test_CandidateContext.test.tsx`: add one case in `describe("CandidateProvider — AST-1768 login-email candidate bind")`, next to `[bug-repro] binds once per login email — refresh and admin picker are not overridden`. Same `bindWrapper(true, …)` and by-email → `c2` fixture. Mount, wait for `selectedId === "c2"`, `setSelectedId("c1")`, unmount, mount again with the same login, wait for hydration, expect `selectedId === "c1"` and `byEmailCalls()` length `1`. Leave the non-admin test that a stored id loses to the login-email candidate unchanged.

### Blast radius

`load` / `lookupBoundCandidate` / `setSelectedId` are the only writers of `astral_selected_candidate`. Readers (nav, admin pages, theme, `JobsJobDetail`) follow `selectedId` after hydration; they do not learn a new key. Tests that set only `astral_selected_candidate` and never `astral_bound_login_email` keep today's rule (a lookup id in the list still wins). The in-memory admin `refresh()` case stays green because `boundEmailRef` is already set. A later admin remount in the same jsdom, after a successful bind has written `astral_bound_login_email`, will keep a still-valid stored id instead of rebinding.

### What must still hold

AST-1768 bind, unchanged except the admin reload keep above:

- Non-admin mount selects the by-email candidate and overwrites `astral_selected_candidate` (existing test stays).
- Verified email wins over `emails[0]`.
- A lookup id missing from the list is ignored; null or failed lookup keeps a valid stored id, else the first candidate.
- No Stytch user → no by-email call.
- Same-mount `refresh()` does not run the lookup a second time, so an admin pick is not overridden.
- `candidatesHydrated` flips only after that resolution, so `JobsJobDetail` company align still runs after the bind.
- `alignSelectedCandidateForJobCompany` stays admin-only.
- Theme (`data-theme`) and the tab title still follow whatever `selectedId` this load kept.

### Radia review

[code-rubric] Ticket AST-2258. Publish ref `87fec5803a1f5007cb89869d82b441cae1766563`. Corpus `b7ab2203048ce0beb2869a12200ab7fa696c8066`. Overall CLEAN.

Canon scores: empty frozen Canon Scope. Joan `[board-joan] CANON: OK`.

[bug-repro] not applicable — remount coverage is sibling AST-2259. ## What must still hold — OK. fix-now: none. discuss: none.

Advisory: product diff is `CandidateContext.tsx` plus this plan; the remount test is AST-2259 (docs-acceptance for the product-vs-test split).

### Radia review — AST-2259

[code-rubric] Ticket AST-2259. Publish ref `278d31fb3889ffcb7aa529790ba772cb4f9011e7`. Corpus `b7ab2203048ce0beb2869a12200ab7fa696c8066`. Overall CLEAN.

[bug-repro] OK — `admin picker survives remount for the same login email` matches the plan. ## What must still hold — OK. fix-now: none. discuss: none.
