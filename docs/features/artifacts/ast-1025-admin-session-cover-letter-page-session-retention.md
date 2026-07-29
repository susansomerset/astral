# Admin Session Cover Letter page + session retention (Session Cover Letter)

**Linear:** [AST-1025](https://linear.app/astralcareermatch/issue/AST-1025/admin-session-cover-letter-page-session-retention-session-cover-letter)
**Parent:** [AST-1023](https://linear.app/astralcareermatch/issue/AST-1023/session-cover-letter) — Session Cover Letter
**Publish ref:** `origin/sub/AST-1023/AST-1025-admin-session-cover-letter-page-session-retention`
**Blocked by (landed):** [AST-1024](https://linear.app/astralcareermatch/issue/AST-1024/session-cover-letter-html-builder-admin-html-api-session-cover-letter) — consume `POST /api/admin/session_cover_letter/html` only; do not re-implement emit/CSS

New Admin nav page (sibling of Session Resume Paste): cover-letter field inputs, browser `localStorage` retention, call the AST-1024 HTML API, open rendered HTML in a new tab. Does **not** own core session cover emit or golden CSS parity.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add Admin `NAV_CONFIG` item for Session Cover Letter (after Session Resume Paste) | utils |
| `src/ui/frontend/src/routes.tsx` | Register `/admin/session_cover_letter` under `AdminRoute` | ui |
| `src/ui/frontend/src/pages/AdminSessionCoverLetter.tsx` | New page: field inputs, Open HTML, Toast, `useLocalStorage` retention, optional `candidate_id` | ui |

**Out of scope (do not touch):** `src/core/builder.py` / SomersetCover CSS / `build_session_cover_letter`, `POST /api/admin/session_cover_letter/html` body validation beyond calling it, job cover HTML routes, Session Resume Paste page/routes, Base Resume Content / JAR / Materials Preview, `TASK_CONFIG` / Manage Tasks / dispatch, candidate or job artifact writers, `tests/`, bible, repo-root `artifacts/`, `App.css` unless a class is truly missing (prefer existing `dep-btn` / `dep-input` tokens).

## Dependency contract (AST-1024 — call site only)

**`POST /api/admin/session_cover_letter/html`** (already on `origin/ftr/ast-1023-session-cover-letter` after merge):

- Auth: `@require_admin` (via `api()` Bearer, same as Session Resume Paste).
- Request JSON field keys from `BUILD_CONFIG["session_cover_letter"]["fields"]`:
  - Required: `from_block`, `letter_date`, `letter`, `signoff_closing`, `signature`
  - Optional: `to_block`, `subject`
  - Optional: `candidate_id` — omit / `null` / `""` → name-only sign-off; non-empty string → optional profile signature-image read on server
- Success **200**: raw HTML body, `Content-Type: text/html; charset=utf-8`
- Failure **400**: `{ "success": false, "error": "<clear message>" }` — treat any non-ok as failure; **never** open the HTML tab

## Stage 1: Admin nav + route registration

**Done when:** Admin sidebar shows **Session Cover Letter** immediately after **Session Resume Paste**; navigating to `/admin/session_cover_letter` renders inside `AdminRoute` (page stub OK until Stage 2 fills UI).

1. In `src/utils/config.py` `NAV_CONFIG` Admin `items` list, immediately after the Session Resume Paste entry, add:
   ```python
   {"label": "Session Cover Letter", "path": "/admin/session_cover_letter"},
   ```
2. In `src/ui/frontend/src/routes.tsx`:
   - Import `SessionCoverLetter` from `./pages/AdminSessionCoverLetter`.
   - Add child route next to `admin/session_resume_paste`:
     ```tsx
     { path: "admin/session_cover_letter", element: <AdminRoute><SessionCoverLetter /></AdminRoute> },
     ```
3. Create `src/ui/frontend/src/pages/AdminSessionCoverLetter.tsx` as a default-export page component named `SessionCoverLetter` (file name matches Admin section prefix; export default function `SessionCoverLetter`). Stage 1 may ship a minimal shell (title + helper line only) if Stage 2 is the same commit wave — prefer implementing Stage 2 in the same build pass so the route is not empty in production.

⚠️ **Decision:** Separate Admin nav item (not nested inside Session Resume Paste), matching parent UI inventory and ticket Boundaries.

## Stage 2: Session Cover Letter page + localStorage + Open HTML

**Done when:** From Admin → Session Cover Letter, Susan can enter field values, Open HTML opens a new tab with styled cover HTML on success; failed validation/render shows a clear error and does **not** open a blank/broken tab; leave/return within the same browser session restores field values and last successful render inputs via `localStorage`; clearing site data wipes them; no candidate/job artifact writes occur from this page.

1. **Field spine (page-local mirror of config):** At the top of `AdminSessionCoverLetter.tsx`, define:
   ```ts
   /** Must match BUILD_CONFIG["session_cover_letter"]["fields"] keys/required (AST-1024). */
   const SESSION_COVER_FIELDS = [
     { key: "from_block", label: "From block", required: true, rows: 3 },
     { key: "letter_date", label: "Date", required: true, rows: 1 },
     { key: "to_block", label: "To block", required: false, rows: 2 },
     { key: "subject", label: "Subject", required: false, rows: 1 },
     { key: "letter", label: "Letter body", required: true, rows: 12 },
     { key: "signoff_closing", label: "Sign-off closing", required: true, rows: 1 },
     { key: "signature", label: "Signature name", required: true, rows: 1 },
   ] as const
   type SessionCoverFieldKey = (typeof SESSION_COVER_FIELDS)[number]["key"]
   type SessionCoverFields = Record<SessionCoverFieldKey, string>
   ```
   Empty default: every key → `""`.

   ⚠️ **Decision:** Mirror keys/required in the page (Session Resume Paste also keeps client payload shape local). Server remains validation source of truth; React uses this list for labels, required UX, and JSON assembly. Do **not** add a new GET config endpoint in this ticket.

2. **localStorage retention** (reuse `useLocalStorage` from `src/ui/frontend/src/lib/useLocalStorage.ts`):
   - Key `session_cover_letter:fields` — type `SessionCoverFields`, default all `""`. Bind every input; writes through on change.
   - Key `session_cover_letter:last_render` — type:
     ```ts
     type SessionCoverLastRender = {
       fields: SessionCoverFields
       candidate_id: string | null
     } | null
     ```
     default `null`. Set **only** after a successful Open HTML (200 + non-empty HTML). Do **not** clear on failed Open HTML (keep prior success). Clearing site data wipes both keys (browser behavior — no extra code).

3. **Selected candidate (optional signature only):**
   - `const { selectedId } = useCandidate()` from `../contexts/CandidateContext`.
   - Helper line must state: letter fields come from this form; if a candidate is selected and has a profile signature image, the server may include it in the sign-off; otherwise name-only. Render still works with no candidate selected. This tool does not save to the database.
   - On Open HTML, set `candidate_id` to `selectedId` when it is a non-empty string; otherwise send `null` (or omit — API accepts both).

4. **UI layout** (clone Session Resume Paste patterns — `dep-btn`, `dep-input`, CSS variables; do **not** edit `App.css` unless a class is missing):
   - Page title: `Session Cover Letter`.
   - Short helper paragraph (see step 3).
   - For each entry in `SESSION_COVER_FIELDS` in order: label (append ` (optional)` when `!required`), then:
     - `rows === 1`: `<input className="dep-input" type="text" … />` (full width)
     - `rows > 1`: `<textarea className="dep-input" rows={rows} … />` (full width, `spellCheck={false}` for letter body; monospace optional for letter only)
   - Buttons row:
     - **Open HTML** — disabled when any `required` field has `trim() === ""`, or when `opening` is true.
   - Inline error `<p>` for the latest failure; clear when Open HTML starts.
   - `<Toast message={toast} onDone={clearToast} />` for success/error feedback.

5. **Open HTML handler** (`POST /api/admin/session_cover_letter/html`):
   - Guard: if required fields incomplete or `opening`, return.
   - `setOpening(true)`; clear inline error.
   - Build body:
     ```ts
     const body = {
       ...fields,
       candidate_id: selectedId && selectedId.trim() ? selectedId.trim() : null,
     }
     ```
   - `api("/api/admin/session_cover_letter/html", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) })`.
   - If `!r.ok`: parse JSON error when possible (`data.error`); set inline error + Toast `error`; **do not** open a tab; **do not** update `last_render`.
   - If ok: `const html = await r.text()`; if empty/whitespace-only → error Toast, no tab, no `last_render` update.
   - On success HTML:
     ```ts
     setLastRender({ fields: { ...fields }, candidate_id: body.candidate_id })
     const blobUrl = URL.createObjectURL(new Blob([html], { type: "text/html;charset=utf-8" }))
     const win = window.open(blobUrl, "_blank", "noopener,noreferrer")
     if (!win) {
       setToast({ text: "Popup blocked — allow popups to open the HTML tab.", variant: "error" })
     }
     window.setTimeout(() => URL.revokeObjectURL(blobUrl), 60_000)
     ```
     Toast success optional (e.g. `Opened cover letter HTML.`) — keep quiet if popup succeeded; always Toast on popup blocked / errors.
   - `finally`: `setOpening(false)`.

6. **Hard rules for this page:**
   - Do **not** call any candidate/job save API, parse API, or artifact endpoints.
   - Do **not** auto-open a tab on mount or on field change — only the Open HTML control.
   - Do **not** merge this UI into `AdminSessionResumePaste.tsx`.
   - Do **not** change `POST /api/admin/session_cover_letter/html` or builder emit.

7. **Verify by hand (builder):**
   - `cd src/ui/frontend && npx tsc --noEmit` (or the repo’s usual frontend typecheck) on touched TS files.
   - Confirm nav label + route load; Open HTML with required fields filled returns a tab; blank required field keeps button disabled; force a 400 (e.g. empty `from_block` via temporary bypass only if needed — prefer relying on disabled button + server message) and confirm no tab opens.

## Self-Assessment

**Scope:** `Single-Component` — Admin nav config + one React route/page with localStorage; no core/data changes.

**Conf:** `high` — direct twin of AST-987 Session Resume Paste UX against a landed AST-1024 HTML contract already merged on `ftr`.

**Risk:** `Medium` — Admin nav/routing surface; a bad Open HTML handler could open empty tabs or confuse users, but Session Resume Paste stays untouched and failures must stay on-page.

## Code-rules self-review

- **§1.3 DRY:** Reuse `useLocalStorage`, `api()`, `Toast`, `dep-*` classes, and the blob-URL new-tab pattern from `AdminSessionResumePaste.tsx`; do not fork a second storage helper.
- **§2.1 / config-source-of-truth:** Nav path/label from `NAV_CONFIG`; field key/required spine remains `BUILD_CONFIG["session_cover_letter"]` on the server — page mirrors keys for UX only (Decision in Stage 2).
- **§2.4 batch / §2.6 state machine:** N/A — no batch or state-machine work.
- **§3.3 imports:** React page imports only frontend libs/contexts/components; no new Python ui→data paths.
- **§3.5 naming:** `AdminSessionCoverLetter.tsx`, route `/admin/session_cover_letter`, snake_case API path already provided by AST-1024.
- **§1.5.1 debug:** No React debug contract; do not add frontend debug logging.
- **in-scope-only / no-cross-contamination:** No artifact persistence; optional `candidate_id` is read-only for signature on the server.

## Review stub (Katherine / build)

**Publish ref:** `origin/sub/AST-1023/AST-1025-admin-session-cover-letter-page-session-retention`
**Tip:** `ac23db55`

**Stages delivered:**
- Stage 1 — `NAV_CONFIG` Session Cover Letter + `/admin/session_cover_letter` under `AdminRoute`
- Stage 2 — `AdminSessionCoverLetter.tsx` field form, `useLocalStorage` retention, Open HTML → AST-1024 API + blob tab

## Radia review (code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1025
**Publish ref tip (pre-docs):** `f3061950`
**Overall:** DISCUSS

### What’s solid
- Stages 1–2 match plan: `NAV_CONFIG` + `/admin/session_cover_letter` under `AdminRoute`, page twin of Session Resume Paste.
- Open HTML failure path never opens a tab; empty HTML treated as error; `last_render` only on success.
- Field/key mirror Decision matches Joan-approved plan; server remains validation SoT.
- Engineer `code()` touched only planned files (no builder/API rewrite).

### Issues
**discuss (C4 stragglers — Joan Excluded; in-scope on `origin/dev...publish-ref` which includes AST-1024 + Betty tests):** 14 statutes (agent/batch/core-bright-line/patterns/state + spikes/features/engineer-test-tree). All substance **conforms** (untouched or process-clean).

**fix-now:** none

### Recommended actions
- Katherine: acknowledge C4 stragglers in resolve (no product change) → User Testing.

## Resolution

**2026-07-29** — Radia `[code-rubric] revision=1` Overall DISCUSS; tip intake `f7320b88` (docs-only) after product/tests `f3061950`.

- **fix-now:** none — no product changes.
- **discuss (C4 stragglers):** acknowledged — Joan Excluded statutes became in-scope via three-dot ancestry (AST-1024 + features/test-tree); substance already **conforms**. No product or plan-stage change.
- **advisory:** none.
