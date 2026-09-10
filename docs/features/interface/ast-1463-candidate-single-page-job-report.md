# AST-1463 — Candidate single page job report

<!-- linear-archive: AST-1463 archived 2026-09-09 -->

## Linear archive (AST-1463)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1463/candidate-single-page-job-report  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** None / 8  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Candidates and Susan need a shareable, bookmarkable URL that opens one job's Recommended Job Report after authentication — without hunting the table first, and without building a second report UI. Today the report only lives in `JobAnalysisReportModal` opened from the Recommended list. This epic adds a `/jobs/detail/<astral_job_id>` deeplink that opens that **same modal**, works for any job state the modal already supports (including skipped), and returns the user to that same URL after session expiry / re-login.

## Functional scope

* **Detail deeplink.** Authenticated URL `/jobs/detail/<astral_job_id>` opens the existing Recommended Job Report **modal** for that job — no parallel full-page report UI and no duplicated Summary / Analysis / Artifacts chrome.
* **Reuse the modal.** List row-click and the deeplink share one interface (`JobAnalysisReportModal`). Closing the deeplink-opened modal returns the user to the Recommended list (or equivalent home for the shell).
* **Any job state.** No restriction to `RECOMMENDED_JOB_STATES`. A candidate may open details for skipped (and other) jobs the modal already loads by id.
* **SPA document GET.** Hard refresh or paste-in-address-bar on `/jobs/detail/<id>` returns `index.html` and boots the SPA on that path (same contract as other in-app routes after AST-1433).
* **Post-auth return path.** After session expiry on the deeplink (or opening the deeplink while logged out), successful authenticate lands back on the **same** `/jobs/detail/<id>` URL so the modal opens again — not a silent drop to `/` or `/jobs/recommended`.
* **Candidate context.** Opening a job deeplink selects that job's owning candidate when the admin session has multiple candidates, so report APIs and copy/print use the right profile.
* **Graceful miss.** Unknown or inaccessible job id shows a clear in-app error with a path back to Recommended — not a blank page.
* **Minimal nav deferred.** v1 does **not** build a reduced sidebar or RBAC nav classes. Full `NavigationShell` stays as today; a later epic may add minimal / RBAC chrome. This epic only needs the user to reach the report via deeplink.

## Component scope

* `src/ui/frontend/src/routes.tsx` — **modified** — register `/jobs/detail/:jobId` under authenticated `NavigationShell`; keep routes ↔ `NAV_CONFIG` sync (path constant may live in config; list nav item unchanged).
* `src/ui/frontend/src/pages/JobsJobDetail.tsx` — **new** — thin host: read `jobId` from the route, open `JobAnalysisReportModal`, handle miss/error, onClose navigate to `/jobs/recommended`.
* `src/ui/frontend/src/pages/JobsRecommended.tsx` — **unchanged expected** — list row-click modal path stays; no requirement to duplicate deeplink wiring here unless plan-child finds a cleaner shared hook (then claim the touch in that child only).
* `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` — **unchanged expected** — reuse as-is; only touch if a small prop is required for deeplink close/navigation (prefer host-owned onClose).
* `src/ui/frontend/src/contexts/CandidateContext.tsx` — **modified** — on detail deeplink load, align `selectedId` with the job's `astral_candidate_id` for admin multi-candidate sessions.
* `src/ui/frontend/src/pages/Authenticate.tsx` — **modified** — after successful auth, navigate to the stored return path when present (deeplink), instead of always `/`.
* `src/ui/frontend/src/pages/Login.tsx` and/or `src/ui/frontend/src/components/RequireAuth.tsx` (and any small session helper already used for Stytch redirects) — **modified** — capture the intended in-app path before login so Authenticate can restore it.
* `src/utils/config.py` — **modified** — route path constant for `/jobs/detail/...` if the project keeps path strings config-driven alongside `NAV_CONFIG` (no new minimal-nav block in this epic).

## Technical scope

* `routes.tsx` — add authenticated child route `jobs/detail/:jobId` → `JobsJobDetail` before the catch-all `*` → `/jobs/recommended` redirect.
* `JobsJobDetail.tsx` — read param; optionally prefetch `/api/jobs/<id>` for candidate alignment / 404; set `JobAnalysisReportModal` `jobId`; onClose → `navigate('/jobs/recommended')`; show explicit error UI when the job cannot load.
* `CandidateContext.tsx` — when detail route supplies a job whose candidate differs from `selectedId`, switch selection for admins; non-admin single-candidate users unchanged.
* `RequireAuth` **/ Login / Authenticate** — persist intended pathname (+ search) when auth is required; after Stytch / local authenticate success, `navigate(returnPath, { replace: true })` instead of hard-coded `/` when a safe same-origin in-app path was stored.
* `config.py` — optional path string for the detail route so React and any future nav/copy stay aligned; **no** minimal-nav group in this epic.

## Architectural definition

* **Patterns to reuse**
  * [`pattern.ui.shared-button-roles`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/ui/pattern.ui.shared-button-roles.md>) — any labeled back / error CTAs use existing `.btn` roles.
  * [`pattern.ui.icon-control`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/ui/pattern.ui.icon-control.md>) — modal dismiss stays the existing icon-control ×.
  * [`pattern.config.config-block`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/config/pattern.config.config-block.md>) — detail route path constant in config if paths are config-sourced.
* **New patterns proposed:** `none`
* **Applicable statutes**
  * [`astral.ui.frontend-file-placement`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/ui/astral.ui.frontend-file-placement.md>) — new page under `pages/`.
  * [`astral.ui.naming-conventions`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/ui/astral.ui.naming-conventions.md>) — PascalCase page name; existing modal components untouched in naming.
  * [`astral.layers.ui-config-driven-business-logic`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.ui-config-driven-business-logic.md>) — no hardcoded eligible-state allowlists in React; modal/API already decide loadability.
  * [`astral.config.config-source-of-truth`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/config/astral.config.config-source-of-truth.md>) — route path constant in config when applicable.
  * [`astral.idioms.require-auth-on-protected-endpoints`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/idioms/astral.idioms.require-auth-on-protected-endpoints.md>) — reuse authenticated `/api/jobs/<id>`; no public job detail API.
  * [`astral.standards.in-scope-only`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md>) — no second report UI; no RBAC / minimal-nav epic; no consult pipeline changes.
  * [`astral.standards.no-hardcoded-sets`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-hardcoded-sets.md>) — do not invent a React-side job-state allowlist for the deeplink.
  * [`orch.pipeline.plan-is-bible`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/orchestration/pipeline/orch.pipeline.plan-is-bible.md>) — child plans stay inside the scoped files above.

## Acceptance criteria

1. While authenticated, visiting `/jobs/detail/<astral_job_id>` for a loadable job opens the **existing** Recommended Job Report modal for that job (same tabs/header/actions as list entry).
2. Hard refresh and paste-in-address-bar on that URL return `index.html` and reopen the modal for the same job (no `{"error":"Not found"}` document body).
3. The deeplink works for jobs outside Recommended list scope when the modal can load them (e.g. skipped) — no client-side “recommended only” gate.
4. Closing the modal from a deeplink lands the user on `/jobs/recommended`.
5. Recommended list **row click still opens the same modal**; list layout and row actions unchanged.
6. After session expiry on the deeplink (or opening it logged out), successful login returns to **that same** `/jobs/detail/<id>` URL and the modal opens again.
7. Admin with multiple candidates: opening a job deeplink selects the job's candidate so report API calls and copy/print use the correct profile.
8. Unknown or inaccessible job id shows an explicit error with a path back to `/jobs/recommended`.
9. No second full-page report UI and no minimal-nav / RBAC shell in this epic.

## Open questions

none

## Proposed child tickets

#### 1!: **Detail deeplink opens existing report modal - Ada**

Add `/jobs/detail/:jobId`, thin `JobsJobDetail` host that opens `JobAnalysisReportModal` (no duplicate report UI), candidate alignment from the job record, miss/error UI, and close → `/jobs/recommended`. Any job state the API returns is allowed. Does **not** own auth return-path (#2).

**Citations:** `pattern.ui.shared-button-roles`, `pattern.ui.icon-control`, `pattern.config.config-block`, `astral.ui.frontend-file-placement`, `astral.ui.naming-conventions`, `astral.config.config-source-of-truth`, `astral.idioms.require-auth-on-protected-endpoints`, `astral.standards.in-scope-only`, `astral.standards.no-hardcoded-sets`

**Scope:** `routes.tsx`; new `JobsJobDetail.tsx`; `CandidateContext.tsx`; `config.py` (detail path constant if used); `JobAnalysisReportModal.tsx` only if a minimal host-driven prop is required (prefer unchanged).

**Estimate:** 5

#### 2: **Return to detail URL after re-auth - Katherine**

Capture the intended in-app path when auth is required; after successful authenticate, navigate back to that path (including `/jobs/detail/<id>`) instead of always `/`. Does **not** own the detail route or modal host (#1). after #1

**Citations:** `astral.idioms.require-auth-on-protected-endpoints`, `astral.standards.in-scope-only`, `astral.ui.frontend-file-placement`

**Scope:** `RequireAuth.tsx` and/or `Login.tsx`; `Authenticate.tsx`; any small existing session/redirect helper touched for Stytch return URLs.

**Estimate:** 3

**Monolith check:** Functional scope spans deeplink/modal host and post-auth return — two children; #1 blocks meaningful UAT of #2's return-to-detail path.

---

## Original brief

Allow a deeplink url to access the recommended reportfor an authenticated user to access a recommended job report with minimal menu accessibility to start.

### Comments

#### chuckles — 2026-08-25T22:30:47.884Z
AST-1482 REVIEW — Joan needs Stage 2 capture guard clarified (isInitialized || session gate).

#### chuckles — 2026-08-25T22:19:20.663Z
AST-1481 REVIEW — Radia fix-now: candidate hydration race + effect deps on JobsJobDetail.

#### chuckles — 2026-08-24T22:04:40.250Z
@susan

1. **Canonical URL path** — prefer `/jobs/report/<astral_job_id>`, `/jobs/recommended/<astral_job_id>`, or another stable shape? (Must not collide with Flask print routes or the list route.)
2. **Minimal nav v1** — which items stay visible: logo only, link back to Recommended list, logout/session, admin candidate switcher, anything else?
3. **Eligible job states** — restrict to `RECOMMENDED_JOB_STATES` (today's list scope), or allow deeplink for any job state where the modal works (applied/skipped/etc.)?
4. **Dual entry** — keep list→modal **and** deeplink page indefinitely, or is the page intended to replace modal entry in a follow-up?
5. **Post-login landing** — after session expiry on a deeplink refresh, should authenticate return the user to the same report URL (return-path), or is landing on `/jobs/recommended` acceptable for v1?

---

_Implementation detail may live in git history on `origin/dev`._
