# AST-1687 — Copy single page access link from recommended job modal

<!-- linear-archive: AST-1687 archived 2026-10-07 -->

## Linear archive (AST-1687)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1687/copy-single-page-access-link-from-recommended-job-modal  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / 2  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Susan already has a bookmarkable Recommended Job Report URL from AST-1463 (`/jobs/detail/<astral_job_id>`). Operators still have to assemble that path by hand when sharing a job. This epic adds a control on the Recommended Job Report modal that shows and copies that absolute access URL to the clipboard so a pasteable link is one click away — without rebuilding the deeplink host, changing auth, or inventing a second report surface.

## Functional scope

* **Copy access link.** On the Recommended Job Report modal, a labeled control copies the absolute single-job access URL for the open job (origin + `/jobs/detail/<astral_job_id>`) to the clipboard.
* **Copied feedback.** After a successful clipboard write, the control shows brief Copied feedback, then returns to its idle label — same operator cue as the existing Copy / email / LinkedIn controls. A blocked clipboard write is silent (no error toast required).
* **Reuse the shipped deeplink.** The button targets the existing AST-1463 detail path and opens the same report modal today; this epic does not add a parallel public page, change session rules, or alter how `/jobs/detail/:jobId` loads.
* **Leave sibling copy actions alone.** Diagnostic Copy, Copy Application Email, Copy LinkedIn Profile, and Print Resume / Cover stay as they are — this is an additional link-copy control, not a replacement.

## Component scope

* `src/ui/frontend/src/components/RecommendedJobReportHeader.tsx` — **modified** — add the labeled Copy Link (or equivalent) control and Copied feedback in the existing header links row beside the other copy actions.
* `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` — **modified** — build the absolute detail URL from the open `jobId` and wire the header copy handler (clipboard write + feedback), without changing report tabs, load, or primary actions.
* `src/ui/frontend/src/pages/JobsJobDetail.tsx` — **unchanged expected** — deeplink host already opens the modal; this epic only surfaces its URL from the modal chrome.
* `src/utils/config.py` — **unchanged expected** — `JOBS_DETAIL_ROUTE_PREFIX` already defines `/jobs/detail`; do not invent a second path string. Touch only if plan-child must expose that constant to the frontend instead of staying in SYNC with `routes.tsx`.
* `src/ui/frontend/src/components/RequireAuth.tsx` / `src/ui/frontend/src/pages/Authenticate.tsx` / `src/ui/frontend/src/lib/sessionAuthMark.ts` — **modified if needed (AST-1768)** — a logged-out open of `/jobs/detail/<id>` must land back on that path after login (return-path capture/restore), so `JobsJobDetail` mounts and opens the modal.
* `src/ui/frontend/src/contexts/CandidateContext.tsx` / `src/ui/frontend/src/pages/JobsJobDetail.tsx` / `src/ui/api/api_candidate.py` — **modified if needed (AST-1768)** — after login via the deeplink, the selected candidate is the one bound to the login email (profile email aliases, e.g. Jolane Abrams), not the stored/first candidate; the job-company align must not undo that.

## Technical scope

* `RecommendedJobReportHeader.tsx` — new optional callback + Copied state props for the link-copy control; render a `.btn secondary` labeled control in the existing `recommended-report-links` row; idle label returns after brief Copied feedback.
* `JobAnalysisReportModal.tsx` — when `jobId` is set, assemble `window.location.origin` + `/jobs/detail/` + encoded job id (same path `JobsJobDetail` / `JOBS_DETAIL_ROUTE_PREFIX` already use); on click, `navigator.clipboard.writeText` that absolute URL and drive header Copied feedback; no new API call.
* Path string stays aligned with `JOBS_DETAIL_ROUTE_PREFIX` / `routes.tsx` `jobs/detail/:jobId` — no second deeplink shape.
* **AST-1768** — post-login deeplink landing: restore the captured `/jobs/detail/<id>` return path and open the recommended-job modal; bind the selected candidate to the authenticated login email (profile email aliases) when one matches. Reuse the existing `captureAuthReturnPath` / `alignSelectedCandidateForJobCompany` plumbing; no second deeplink shape.

## Architectural definition

* **Patterns to reuse** — `no established pattern applies` (active corpus has no UI/clipboard pattern; follow the in-tree Recommended Job Report header copy controls — `.btn secondary` + brief Copied feedback — already used for diagnostic Copy / email / LinkedIn).
* **New patterns proposed:** none
* **Applicable statutes** — none of the directives currently in force (`canon/canon_clerk.py index`) constrain this UI-only clipboard affordance; say so explicitly rather than citing retired `astral.ui.*` / `pattern.ui.*` ids.

## Acceptance criteria

1. With a Recommended Job Report modal open for job id `J`, clicking the new link-copy control puts an absolute URL on the clipboard whose path is exactly `/jobs/detail/J` (same origin as the app). **Fail:** clipboard text missing, relative-only path, wrong job id, or a path other than `/jobs/detail/<id>`.
2. After a successful copy, the control label reads Copied briefly, then returns to the idle link-copy label. **Fail:** label never changes, or stays on Copied permanently.
3. Opening that copied URL while authenticated opens the same Recommended Job Report modal for that job (existing AST-1463 behavior). **Fail:** 404 document body, blank page, or a different report UI.
4. Diagnostic Copy, Copy Application Email, Copy LinkedIn Profile, Print Resume, and Print Cover Letter still appear and behave as before when their data is present. **Fail:** any of those controls removed, relabeled as the link control, or broken by the new wiring.
5. No new unauthenticated/public job-report route is added in this epic. **Fail:** `grep` / route table shows a new public detail path beyond the existing authenticated `/jobs/detail/:jobId`.

## Open questions

none

## Proposed child tickets

#### 1: **Copy detail deeplink from report header - Katherine**

Adds the labeled link-copy control on the Recommended Job Report header and wires clipboard write of the absolute `/jobs/detail/<jobId>` URL from the open modal. Does **not** own deeplink routing, auth return-path, diagnostic/email/LinkedIn copy payloads, or any Stytch↔candidate bind.

**Citations:** none — no in-force pattern/statute fits; follow existing header `.btn secondary` copy feedback.

**Scope:** `src/ui/frontend/src/components/RecommendedJobReportHeader.tsx` — **modified** — add the labeled Copy Link (or equivalent) control and Copied feedback in the existing header links row beside the other copy actions. `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` — **modified** — build the absolute detail URL from the open `jobId` and wire the header copy handler (clipboard write + feedback), without changing report tabs, load, or primary actions. `src/ui/frontend/src/pages/JobsJobDetail.tsx` — **unchanged expected** — deeplink host already opens the modal; this epic only surfaces its URL from the modal chrome. `src/utils/config.py` — **unchanged expected** — `JOBS_DETAIL_ROUTE_PREFIX` already defines `/jobs/detail`; do not invent a second path string. Touch only if plan-child must expose that constant to the frontend instead of staying in SYNC with `routes.tsx`. Path string stays aligned with `JOBS_DETAIL_ROUTE_PREFIX` / `routes.tsx` `jobs/detail/:jobId` — no second deeplink shape. `RecommendedJobReportHeader.tsx` — new optional callback + Copied state props for the link-copy control; render a `.btn secondary` labeled control in the existing `recommended-report-links` row; idle label returns after brief Copied feedback. `JobAnalysisReportModal.tsx` — when `jobId` is set, assemble `window.location.origin` + `/jobs/detail/` + encoded job id (same path `JobsJobDetail` / `JOBS_DETAIL_ROUTE_PREFIX` already use); on click, `navigator.clipboard.writeText` that absolute URL and drive header Copied feedback; no new API call.

**Estimate:** 2

**Monolith check:** Functional scope has four capabilities but one inseparable chrome slice (header control + modal URL wiring for the same clipboard write) — single child intentional.

**Scope partition check:** every Component / Technical scope item is owned by child #1 (unchanged-expected files listed as out-of-touch, not dual-claimed).

---

## Original brief

I think we have already written the code to allow for a single Page access point that will display an individual recommended job from a deep link without explicit authentication. If that is the case, I'd like to add a button on the job model for recommended jobs that will display and copy that URL to the clipboard.

### Comments

#### chuckles — 2026-09-27T04:01:51.758Z
[fix-intake] Not blocked anymore. Both blockers on AST-1768 are cleared:
- Scope: the parent Description now names the AST-1768 lines (check-linear amended it).
- Refs: PR #61 merged ftr into dev and deleted `ftr/AST-1687-…` and the AST-1768 sub. I re-created both off origin/dev.

Katherine's plan-fix is running on AST-1768 right now. Next stop is Plan Ready, then fix-board. No new bugs filed from this pass.

#### susan — 2026-09-27T04:01:02.607Z
@chuckles Is this still blocked?

#### chuckles — 2026-09-22T00:22:11.873Z
[fix-intake] Filed AST-1768 (Discussion, assignee Susan) for the [bug] comment — waiting her diagnosis confirm.

#### susan — 2026-09-22T00:18:59.888Z
\[bug\] I expected the link to open the platform, bind to the authenticated candidate user (e.g. Jolane Abrams), and open on the specific linked-from-job-modal recommended job modal open.  Right now, I log in as soosomerset@gmail.com (set on Jolane Abrams profile as a valid email), and it shows me Susan Somerset as a candidate and no direct popup to the job I wanted to look at.

#### chuckles — 2026-09-16T22:18:14.783Z
@susan

1. For **this** epic, confirm Copy Link only copies the existing authenticated `/jobs/detail/<id>` URL for people who already have an Astral Stytch session (operators / existing logins) — no new Stytch↔candidate bind, no public/unauthenticated share URL, no candidate-scoped RBAC. Candidate login binding is a separate epic if you want it later. Agree?
2. If you do **not** agree with (1): do you want this ticket expanded to design Stytch↔candidate binding and scoped deeplink access now (new schema + auth scoping — much larger than a header copy button)?

#### chuckles — 2026-09-16T22:18:09.708Z
Today there is **no** Stytch ↔ candidate bind.

- Opening `/jobs/detail/<id>` requires a Stytch session (except local deploy passthrough). Any Stytch B2C user who can log in can load the page; admin is only the env allowlists (`ASTRAL_ADMIN_USER_IDS` / `ASTRAL_ADMIN_EMAILS`), not candidate membership.
- Candidate rows bind **Slack** (`contact.slack_user_id`), not Stytch. Creating someone as a Stytch user gets them past Login — it does **not** attach them to one Astral candidate, and job detail has **no** ownership gate by Stytch user.
- Binding Stytch accounts to candidates (and scoping the deeplink to that candidate) is new product work — schema + auth scoping — not part of a Copy Link button on the existing URL.

#### chuckles — 2026-09-16T21:58:01.627Z
@susan

1. The shipped single-page access point (`/jobs/detail/<astral_job_id>`, AST-1463) requires an authenticated session to open the report — it is not a public, no-login URL. Confirm Copy Link should copy that existing authenticated deeplink. If you instead need a true unauthenticated share link, that is a different epic (new auth/public surface) — say so before we treat this definition as approved.

---

_Implementation detail may live in git history on `origin/dev`._
