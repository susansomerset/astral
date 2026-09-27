# AST-1696 — Copy detail deeplink from report header

- **Linear:** [AST-1696](https://linear.app/astralcareermatch/issue/AST-1696/copy-detail-deeplink-from-report-header-copy-single-page-access-link)
- **Parent:** [AST-1687](https://linear.app/astralcareermatch/issue/AST-1687/copy-single-page-access-link-from-recommended-job-modal) — Copy single page access link from recommended job modal
- **Publish ref:** `sub/AST-1687/AST-1696-copy-detail-deeplink-from-report-header`

Adds a labeled **Copy Link** control on the Recommended Job Report header that copies the absolute authenticated detail URL (`origin` + `/jobs/detail/<jobId>`) for the open modal job to the clipboard, with the same brief **Copied** feedback used by the existing diagnostic Copy control. Reuses the shipped AST-1463 / AST-1481 deeplink host — does not add routes, change auth, or alter other header copy/print actions.

## UAT fitness

- **AC restored:** Parent AST-1687 AC 1–5 (mirrored on this child): (1) with modal open for job `J`, link-copy puts absolute URL whose path is exactly `/jobs/detail/J` on the clipboard; (2) control reads Copied briefly then idle label; (3) opening that URL while authenticated opens the same Recommended Job Report modal (existing AST-1463 behavior); (4) Diagnostic Copy, Copy Application Email, Copy LinkedIn Profile, Print Resume, and Print Cover Letter still appear and behave as before when their data is present; (5) no new unauthenticated/public job-report route beyond existing `/jobs/detail/:jobId`.
- **Correct outcome:** Operator opens a Recommended Job Report, clicks **Copy Link**, pastes an absolute same-origin URL ending in `/jobs/detail/<that job's id>`, and that URL reopens the same report modal when authenticated.
- **Sibling check:** AST-1481 `JobsJobDetail` deeplink host and `routes.tsx` `jobs/detail/:jobId` stay untouched — verified by not listing them in Files Changed and by AC 3 relying on existing behavior. Existing header copy/print controls (AST-1421 snapshot Copy; email / LinkedIn; print) keep their labels, handlers, and conditional visibility — new control is additive.
- **Not sufficient:** Removing an error / adding a dead button that does not write the absolute `/jobs/detail/<id>` URL, or only showing a relative path.
- **Wrong fix rejected:** Inventing a second public/detail route or touching `JobsJobDetail.tsx` / auth return-path; replacing or relabeling Diagnostic Copy / email / LinkedIn as the link control; exposing a new path string in `config.py` when the frontend already stays in SYNC with `JOBS_DETAIL_ROUTE_PREFIX` via the literal `/jobs/detail/` used by `routes.tsx`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/RecommendedJobReportHeader.tsx` | Add optional link-copy callback + copied-state props; render `.btn secondary` **Copy Link** in `recommended-report-links`; include the new callback in the row visibility condition | ui |
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | Assemble absolute detail URL from open `jobId`; clipboard write + 2s Copied state; pass props into the header; reset copied state when `jobId` changes | ui |

**Do not touch:** `src/ui/frontend/src/pages/JobsJobDetail.tsx`; `src/ui/frontend/src/routes.tsx`; `src/utils/config.py`; `RequireAuth` / auth return-path; Diagnostic Copy / email / LinkedIn / print handlers or labels (except coexistence); report tabs / load / primary actions; `tests/**`; `docs/test-bible/**`.

## Stage 1: Header Copy Link control

**Done when:** `RecommendedJobReportHeader` accepts optional `onCopyDetailLink` and `detailLinkCopied` props, renders a `.btn secondary` labeled **Copy Link** (reads **Copied** when `detailLinkCopied` is true) inside the existing `recommended-report-links` row, and the links row is visible whenever `onCopyDetailLink` is provided even if snapshot / email / LinkedIn are absent.

1. In `src/ui/frontend/src/components/RecommendedJobReportHeader.tsx`, extend `Props` with:
   - `onCopyDetailLink?: () => void`
   - `detailLinkCopied?: boolean`
2. Destructure those props in the component signature (same style as `onCopySnapshot` / `snapshotCopied`).
3. Change the links-row visibility condition from `(onCopySnapshot || applicationEmail || linkedInUrl)` to `(onCopyDetailLink || onCopySnapshot || applicationEmail || linkedInUrl)` so the new control can stand alone.
4. Inside `recommended-report-links`, **before** the diagnostic Copy button, render:

```tsx
{onCopyDetailLink && (
  <button
    type="button"
    className="btn secondary"
    onClick={() => onCopyDetailLink()}
  >
    {detailLinkCopied ? "Copied" : "Copy Link"}
  </button>
)}
```

⚠️ **Decision:** Idle label is **Copy Link** (parent Component scope “Copy Link (or equivalent)”). Feedback label is **Copied**, matching the snapshot Copy control — not the separate `copyFeedback` span used by email/LinkedIn.

5. Do not change title/company links, print actions, email/LinkedIn buttons, snapshot Copy button, or the `copyFeedback` span.

## Stage 2: Modal URL assembly and clipboard wiring

**Done when:** With `JobAnalysisReportModal` open for a non-null `jobId`, clicking **Copy Link** writes `window.location.origin + "/jobs/detail/" + encodeURIComponent(jobId)` to the clipboard, the header shows **Copied** for ~2 seconds then **Copy Link** again, and a failed clipboard write leaves the label unchanged (no toast). Existing header actions still receive the same props as today.

1. In `src/ui/frontend/src/components/JobAnalysisReportModal.tsx`, add state next to `snapshotCopied`:

```tsx
const [detailLinkCopied, setDetailLinkCopied] = useState(false)
```

2. Add a reset effect beside the existing `setSnapshotCopied(false)` on `jobId` change:

```tsx
useEffect(() => { setDetailLinkCopied(false) }, [jobId])
```

3. Add handler (near `handleCopySnapshot` / email / LinkedIn handlers):

```tsx
function handleCopyDetailLink() {
  if (!jobId) return
  const url =
    `${window.location.origin}/jobs/detail/${encodeURIComponent(jobId)}`
  navigator.clipboard.writeText(url).then(() => {
    setDetailLinkCopied(true)
    window.setTimeout(() => setDetailLinkCopied(false), 2000)
  })
}
```

⚠️ **Decision:** Use the open modal’s `jobId` prop (already the deeplink id) and the literal path prefix `/jobs/detail/` — same string as `routes.tsx` / `JOBS_DETAIL_ROUTE_PREFIX`. Do **not** edit `config.py` or invent a second path. Clipboard rejection is silent (no `.catch` toast) per parent Functional scope.

4. On the `<RecommendedJobReportHeader … />` call site, pass:
   - `onCopyDetailLink={handleCopyDetailLink}`
   - `detailLinkCopied={detailLinkCopied}`
   Leave every other header prop unchanged.

5. Do not change report load, tabs, primary actions, snapshot/email/LinkedIn/print handlers, or navigate/route tables.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-1696
**Overall:** APPROVED
**Corpus:** fc0c368e59
**Publish-ref:** `2c1923c2aee9bfb779fa4a0584abdc5ed8287fbd` (`origin/sub/AST-1687/AST-1696-copy-detail-deeplink-from-report-header`)

## Canon scores

(none — parent Architectural definition and child Citations declare no in-force directives apply; clerk index has 12 active ids, all logging/entity/dispatch — none govern this UI-only clipboard slice)

## Traceability

1 → Stage 1 (Copy Link control) + Stage 2 (`handleCopyDetailLink` absolute URL + `navigator.clipboard.writeText`) · 2 → Stage 1 (`detailLinkCopied` label) + Stage 2 (2s reset + `jobId` effect) · 3 → UAT fitness sibling check (existing AST-1463/AST-1481 `JobsJobDetail` host; no new stage) · 4 → Stage 1 step 5 + Stage 2 step 5 (do-not-touch diagnostic/email/LinkedIn/print) · 5 → Files Changed + do-not-touch list (no `routes.tsx`, `config.py`, or `JobsJobDetail.tsx`)

## Findings

### discuss — No `## Self-assessment` section

**Location:** Plan doc tail  
**Finding:** Only `## Estimate` confirm present; no confidence axes block.  
**Recommendation:** Optional template polish; staged scope is small and estimate (2) is honest — not blocking.

### acceptable — Empty frozen canon list is intentional

**Location:** Child `## Citations`; parent Architectural definition  
**Finding:** Parent explicitly states no in-force directives constrain this UI-only clipboard affordance; child mirrors with `Citations: none`. Clerk roster confirms UI placement/import/config statutes are draft, not active — parent's determination is correct.  
**Recommendation:** No Canon Scope amendment needed.

### acceptable — DRY / pattern reuse

**Location:** Stage 2 handler; existing `handleCopySnapshot` / `snapshotCopied` in `JobAnalysisReportModal.tsx`  
**Finding:** Plan mirrors established snapshot-copy state machine (2s Copied feedback, reset on `jobId` change, silent clipboard failure) without duplicating new abstractions.  
**Recommendation:** None.

### acceptable — Path alignment without config touch

**Location:** Stage 2 step 3  
**Finding:** Literal `/jobs/detail/` + `encodeURIComponent(jobId)` matches `routes.tsx` / `JOBS_DETAIL_ROUTE_PREFIX` SYNC comment; plan correctly avoids `config.py` per parent Technical scope.  
**Recommendation:** None.

context_tokens≈28000

## Review (build)

**Built:** `origin/sub/AST-1687/AST-1696-copy-detail-deeplink-from-report-header` @ `b40369ec`

Stage 1: `RecommendedJobReportHeader` — optional `onCopyDetailLink` / `detailLinkCopied`; **Copy Link** `.btn secondary` before diagnostic Copy; links row visible when link-copy alone.

Stage 2: `JobAnalysisReportModal` — absolute `origin + /jobs/detail/<jobId>` clipboard write, 2s Copied feedback, reset on `jobId` change.

Tests deferred to Betty (`qa-child`).

## Radia review

[code-rubric]
**Ticket:** AST-1696
**Publish ref:** `0934b72c1a982c768deab14a95e7a38ca7290eca` (`origin/sub/AST-1687/AST-1696-copy-detail-deeplink-from-report-header`)
**Corpus:** fc0c368e59
**Overall:** CLEAN

## Canon scores

(empty frozen list — child `## Citations` is `none`; Joan and clerk roster agree no in-force directives govern this UI-only clipboard slice)

## Column diff vs plan stage

(aligned) — Joan scored an empty list; diff introduces no new canon obligations.

## Frame diff

(none)

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

**Branch diff carries sibling epic work beyond AST-1696 product scope**
**Location:** `git diff origin/dev...origin/sub/AST-1687/AST-1696-copy-detail-deeplink-from-report-header` (26 files; ~2k insertions)
**Finding:** AST-1696 product changes are confined to `RecommendedJobReportHeader.tsx` and `JobAnalysisReportModal.tsx` (+ Betty’s AST-1696 component tests and bible block). The three-dot diff also includes merged sibling slices (e.g. AST-1692 Meteorite tab tests in `test_JobAnalysisReportModal.test.tsx`, core/meteorite/tracker/api_jobs work, etc.). Expected on a shared `sub/*` tip — not AST-1696 implementing out-of-scope product.
**Recommendation:** Chuckles/issue doc should attribute sibling files to their tickets when appending review; no product fix for AST-1696.

**Issue doc missing qa-child / test-child sections**
**Location:** `docs/features/interface/ast-1696-copy-detail-deeplink-from-report-header.md` tail (ends at `## Review (build)`)
**Finding:** Betty’s manifest is on tip in `docs/test-bible/frontend/components.md` and tests land in diff; Linear status is Tests Passed, but the issue doc has no `## QA` or test-run block yet.
**Recommendation:** Chuckles append Betty/Katherine evidence on writeback — not blocking review.

**`jobId` change resets `detailLinkCopied` without dedicated test**
**Location:** `JobAnalysisReportModal.tsx` `useEffect(() => { setDetailLinkCopied(false) }, [jobId])`
**Finding:** Plan Stage 2 step 2 implemented; manifest does not require an assertion.
**Recommendation:** Optional hardening in a future pass; not blocking.

## What's solid

- Product diff matches plan Stages 1–2 verbatim: optional props, **Copy Link** `.btn secondary` before diagnostic Copy, links-row visibility when link-copy alone, absolute `origin + /jobs/detail/` + `encodeURIComponent(jobId)`, 2s **Copied** feedback, silent clipboard rejection (no `.catch`), props wired at header call site.
- Do-not-touch list honored for AST-1696 scope: no `JobsJobDetail.tsx`, `routes.tsx`, `config.py`, or auth changes.
- Betty manifest (`AST-1696` + `AST-1421` regression) aligns with bible: header alone/coexistence/Copied prop; JAR clipboard URL, label flip, coexistence with snapshot/email/LinkedIn; no integration invention.
- Estimate 2 fits: ~29 lines product + focused component tests.

## Recommended actions

- Chuckles: append this verdict to issue doc, commit `docs(AST-1696): Radia review — clean`, post slim upshot, move to Review Posted.
- datt: **PROCEED** → User Testing (no canon fix-now items; empty frozen list).


## Bug: AST-1768 — Copied job detail link does not bind login email to candidate or open job modal

### As-is

Susan opens a copied `/jobs/detail/<id>` link while logged out, signs in as `soosomerset@gmail.com` (an email on Jolane Abrams's profile), and lands on `/` with candidate **Susan Somerset** selected — no Recommended Job Report modal for the linked job.

### To-be

After sign-in the app returns to that same `/jobs/detail/<id>` URL, `JobsJobDetail` opens the Recommended Job Report modal for the job, and the selected candidate is the one whose profile emails uniquely match the login email (Jolane Abrams).

### Repro

1. Deployed (non-local) env. Candidate row fixture — Jolane Abrams: `candidate_data.contact.contact_email = "soosomerset@gmail.com"` (or listed in `contact.extra_emails`); a second candidate Susan Somerset is first in `/api/candidates` order / stored in `localStorage["astral_selected_candidate"]`.
2. Logged out, open `https://<host>/jobs/detail/<jolane_job_id>` → `RequireAuth` renders `Login` and captures the return path into **sessionStorage** (`astral-auth-return-path`).
3. Choose email magic link, enter `soosomerset@gmail.com`, click the link in the email → it opens a **new tab** at `/authenticate?token=…`.
4. New tab's sessionStorage has no return path → `consumeAuthReturnPath()` returns `null` → navigate to `/`.
5. `CandidateContext.load()` keeps the stored/first candidate (Susan Somerset); nothing consults the login email.

### Root cause

1. **Return path is tab-scoped.** `sessionAuthMark.ts` stores `astral-auth-return-path` in `sessionStorage`. Magic-link sign-in completes in a different tab from the one that captured it, so `Authenticate.postAuthNavigate` finds nothing and goes to `/`. (Google OAuth redirects in the same tab and already works.)
2. **No login-email → candidate bind exists.** `CandidateContext.load()` picks the stored or first candidate; `setSelectedId` is admin-only; no code path matches the authenticated email against profile email homes. The server-side matcher already exists (`get_candidate_id_for_query` in `src/core/candidate.py`, unique hit over `CANDIDATE_LOOKUP_CONFIG` email paths incl. `contact.extra_emails`) but is not exposed to the SPA.
3. **Host does not wait for candidate resolution for non-admins.** `JobsJobDetail` only waits on `candidatesHydrated` when `isAdmin`, so a late candidate change would remount the modal's candidate-scoped loads.

### Proposed change

**A. Return path survives the magic-link tab — `src/ui/frontend/src/lib/sessionAuthMark.ts`**

1. In `captureAuthReturnPath`, `peekAuthReturnPath`, and `consumeAuthReturnPath`, replace `sessionStorage` with `localStorage` for `AUTH_RETURN_PATH_KEY` only. `HAD_SESSION_KEY` and `LOGOFF_REASON_KEY` stay in `sessionStorage` (unchanged).
2. Keep the same `try { … } catch { /* private mode */ }` wrappers and `isSafeAuthReturnPath` checks. No other API change.

⚠️ **Decision:** `localStorage`, no expiry/TTL. A stale path cannot leak: every Login render re-captures the current path (`RequireAuth` effect overwrites the key, including `/`), and `consumeAuthReturnPath` removes it on sign-in. No limit is added.

`RequireAuth.tsx` and `Authenticate.tsx` — **no change**; they already call capture/consume.

**B. Server email → candidate lookup — `src/ui/api/api_candidate.py`**

1. Import `get_candidate_id_for_query` from `src.core.candidate` (add to the existing import block).
2. Add a route **directly after** `get_candidate_states` (before any `/<candidate_id>` route):

```python
@candidate_bp.route("/by_email")
@require_auth
def get_candidate_by_email():
    """AST-1768: unique candidate id whose profile emails match ?email= (login bind)."""
    email = (request.args.get("email") or "").strip()
    if "@" not in email:
        return jsonify({"error": "email required"}), 400
    return jsonify({"candidate_id": get_candidate_id_for_query(email)})
```

Returns `{"candidate_id": "<id>"}` on a unique match, `{"candidate_id": null}` on no/ambiguous match.

⚠️ **Decision:** The email comes from the client's Stytch user, not `g.user` — `normalize_user` (`src/utils/auth.py`) drops email and that file is outside AST-1687 scope. This is safe: the lookup only drives UI selection, and `GET /api/candidates` already returns every candidate to any authenticated user, so no new data is exposed and no authorization changes.

**C. Bind selection once per login — `src/ui/frontend/src/contexts/CandidateContext.tsx`**

1. Import `useStytchUser` from `@stytch/react`. In `CandidateProvider`: `const { user: stytchUser } = useStytchUser()` and derive `loginEmail`: first `stytchUser.emails` entry with `verified === true`, else `emails[0]`, `.email.trim().toLowerCase()`; `""` when no user (local passthrough). Same verified-first rule as `src/external/stytch.py` `_primary_email`.
2. Add `const boundEmailRef = useRef<string | null>(null)`.
3. Rewrite `load()` so hydration completes **after** the bind check:
   - Fetch `/api/candidates` as today and compute `next` (stored-if-present else first) as today.
   - If `loginEmail` is non-empty **and** `boundEmailRef.current !== loginEmail`: set `boundEmailRef.current = loginEmail`, then call `api` on the path `/api/candidates/by_email?email=` + `encodeURIComponent(loginEmail)` (template literal). If `res.ok` and the body's `candidate_id` is a non-empty string present in the fetched list, use it as `next`. Any failure/null → keep `next`.
   - Call `_setSelectedId(next)` + `localStorage.setItem(STORAGE_KEY, next)` (bypasses the admin-only `setSelectedId` guard, same as today's `load()`).
   - `setCandidatesHydrated(true)` in `finally`, after the above.
4. Add `loginEmail` to the effect that calls `load()`: `[authLoading, loginEmail]`.

⚠️ **Decision:** The bind runs **once per login email** (ref guard), for admins and non-admins alike. Later `refresh()` calls (profile saves) and the admin picker are not overridden.

**D. Host waits for candidate resolution — `src/ui/frontend/src/pages/JobsJobDetail.tsx`**

1. In the align effect, change `if (isAdmin && !candidatesHydrated) return` to `if (!candidatesHydrated) return`. Leave the dependency array unchanged.
2. No other change. For admins, `alignSelectedCandidateForJobCompany` still runs after the bind. When the job's company owner is the bound candidate (Susan's case) it is a no-op; when an admin opens another candidate's job, AST-1481 behavior (select the job owner) still applies. For non-admins, align stays a no-op, so the bind stands.

### Blast radius

- `sessionAuthMark.ts` is used by `RequireAuth`, `Authenticate`, `LogOffScreen` (`clearSessionAuthMarks`, unchanged). Existing test `tests/component/frontend/lib/test_sessionAuthMark.test.ts` asserts `sessionStorage` directly for `astral-auth-return-path` (lines ~75–77), and several suites clear only `sessionStorage` in setup (`stytchMock.tsx`, `test_Authenticate`, `test_RequireAuth`, `test_LogOffScreen`) → return-path tests need `localStorage` expectations and cleanup (Betty).
- `CandidateContext` is mounted app-wide; the new `useStytchUser` call needs a mock in `tests/component/frontend/stytchMock.tsx` for suites that render `CandidateProvider` (Betty).
- `JobsJobDetail` non-admin path now waits for hydration → `test_JobsJobDetail.test.tsx` non-admin cases must resolve `/api/candidates` before the modal appears (Betty).
- `api_candidate.py` gains one route before the `/<candidate_id>` catch-all. No change to existing routes or `get_candidate_id_for_query`.
- AST-1482 return-path behavior (same-tab / OAuth) stays the same, just backed by `localStorage`.

### What must still hold

- AST-1687 AC 1–5: Copy Link writes the absolute `/jobs/detail/<id>` URL; Copied→idle; the link opens the same report modal when authenticated; diagnostic Copy / email / LinkedIn / print unchanged; **no new unauthenticated route** (`/api/candidates/by_email` is `@require_auth`).
- AST-1481: admin with multiple candidates opening another candidate's job deeplink still selects the job owner; unknown id still shows the error + back link; close → `/jobs/recommended`.
- AST-1482: `isSafeAuthReturnPath` rejects `/authenticate*` and `//…`; `clearSessionAuthMarks` does not clear the return path.
- Local passthrough: no Stytch user → no bind call; selection behaves as today.
- No match / ambiguous email (more than one candidate) → no bind; today's stored/first selection stays.

### Fix board — Joan (canon)

## Fix-board Joan pass — AST-1768

**Ticket:** AST-1768 (bug child of AST-1687)  
**Read:** `plan-fix` patch on `origin/sub/AST-1687/AST-1768-copied-job-detail-link-bind-candidate-open-modal` in `docs/features/interface/ast-1696-copy-detail-deeplink-from-report-header.md` (sections As-is → What must still hold)  
**Roster:** `canon/canon_clerk.py index` — 21 directives in force @ `a0bc2f0e5b` (up from 12 at AST-1696 plan validate; no `DIRTY` flag observed on this pass)  
**Question (F2):** Does the proposed fix conflict with or require updating any directive **in force**?

### Proposed change (summary)

| Part | Layer / files | Shape |
|------|----------------|--------|
| **A** | `sessionAuthMark.ts` | Move `AUTH_RETURN_PATH_KEY` only from `sessionStorage` → `localStorage`; other keys unchanged |
| **B** | `api_candidate.py` | New `@require_auth` `GET /api/candidates/by_email?email=` wrapping existing `get_candidate_id_for_query` |
| **C** | `CandidateContext.tsx` | Once-per-login-email bind via Stytch verified email + new API |
| **D** | `JobsJobDetail.tsx` | Wait on `candidatesHydrated` for all users, not only admins |

Blast radius is mostly tests/mocks (Betty’s lane). Product surface: auth return-path storage, one read-only API route, candidate hydration ordering.

### Roster overlap (in-force only)

**Entity / dispatch / batch (`astral.batch.*`, `astral.dispatch.*`, `astral.entity.*`, `patt.entity.*`, `patt.task.*`)** — No batch claim, dispatch_task, or entity-schema work. **No canon impact.**

**Artifact patterns (`patt.artifact.*`)** — No catalog, operative read/write, or editor consistency changes. **No canon impact.**

**Logging — `stat.logging.info.api`** (`src/ui/api/**`, add/modify)  
The new route is an authenticated idempotent GET that returns current lookup state (`candidate_id` or `null`). The statute explicitly says idempotent GETs that only return current state are **not** progress — **no** `logger.info` at the route. The plan does not require an API progress line; implementation should mirror `get_candidate_states()` (jsonify, no info). That is **conformance**, not a carve-out or statute edit.

**Logging — `stat.logging.error`**  
Planned handler is a thin wrapper with 400 on bad email and JSON otherwise; no log-and-rethrow pattern proposed. Aligns with existing list/state GET routes in the same file. **No canon update required** (make-fix should still avoid introducing duplicate exception logging if core ever raises).

**Logging — `stat.logging.info.contact`, `stat.logging.info.entity`, `stat.logging.info.dispatcher`, `stat.logging.debug`, `stat.logging.warning`, `stat.logging.info`** — No contact-listen, entity-pipe, dispatcher, or new warning/error rollup in the patch. **No canon impact.**

**Draft / retired law (not in roster)** — Parent/child “Citations: none” and items like `astral.idioms.require-auth-on-protected-endpoints`, `astral.standards.in-scope-only`, UI placement statutes remain **draft**; fix-board does not score them. Part **B** uses `@require_auth` like neighboring routes — consistent with product practice, not an active-statute gap.

### Conflicts / carve-outs / new precedent?

- **localStorage for return path:** No in-force statute defines tab vs origin storage for auth return paths. AST-1482 guards (`isSafeAuthReturnPath`, `clearSessionAuthMarks` not clearing return path) are preserved in **What must still hold**. Storage backend change is product behavior, not a corpus amendment.
- **Client-supplied email on authenticated lookup:** Plan documents threat model (UI selection only; no new data vs `GET /api/candidates`). That is an implementation/security judgment for make-fix and review, not “update canon” unless Archie wants a new **in-force** idiom — fix-board does not treat that as REVISE without an active directive being contradicted.
- **Login-email → candidate bind:** Reuses server matcher already in core; no new matching algorithm in callers (would matter for `patt.entity.batch-criteria` if literals appeared in dispatch paths — they do not).

### What must still hold (canon-relevant)

- New route stays **`@require_auth`** (draft idiom honored in code; satisfies “no new unauthenticated route” in the patch).
- **`GET /by_email`** should not emit **`stat.logging.info.api`** progress lines.
- No change to entity/batch/dispatch/artifact statutes.

### Verdict rationale

No active statute or pattern needs text changed, and the proposed product change does not force a documented exception in the in-force corpus. Engineer guidance at build time: implement **B** like other idempotent candidate GETs (no API info log); keep **A** scoped to `AUTH_RETURN_PATH_KEY` only.

---

```
[board-joan]  CANON: OK
```

```
AST-1768 board-joan done — CANON: OK.
```
