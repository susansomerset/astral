# AST-1538 — Manage Email modal copy + dark purple

**Linear:** [AST-1538](https://linear.app/astralcareermatch/issue/AST-1538/manage-email-modal-copy-dark-purple-manage-email-gives-html-for-the)  
**Parent:** [AST-1533](https://linear.app/astralcareermatch/issue/AST-1533/manage-email-gives-html-for-the-body-of-the-message-not-for-the-header) — Manage Email gives HTML for the body of the message, not for the header, and it must include both.  
**Publish ref:** `sub/AST-1533/AST-1538-manage-email-modal-copy-dark-purple`

Owns the Manage Email popup: render the assembled header+body HTML from the inbox get API, add the copy control, and set the reading-surface background to dark purple theme tokens. Does not own land/qualify blob assembly (sibling AST-1537).

## Scope gate

Ticket **## Scope** (verbatim partition):

- `src/ui/frontend/src/pages/AdminManageEmail.tsx` (render assembled HTML; copy control)
- `src/ui/frontend/src/App.css` (dark purple email popup reading surface)

All Files Changed / Stages stay inside that set.

**Out of scope (siblings / keep):**

- `config.py` / `inbox.py` / `meteorite_email.py` / `gmail.py` / `api_inbox.py` — **AST-1537** (already exposes `assembled_html` on `GET /api/admin/inbox/messages/<id>`).
- Land Meteorite multi-select semantics, list toolbar, checkbox selection — leave behavior as today (Parent AC6 / this ticket AC4: no regression).
- Non-email meteorite ingress — unchanged.
- New Flask routes, NAV_CONFIG, Modal component API changes.

**Depends on:** AST-1537 (User Testing; merged onto `origin/ftr/AST-1533-manage-email-header-html`). Message get returns `assembled_html` (header+body wrapper) plus the prior Gmail keys (`html_body`, etc.).

**AC partition (this ticket):** Parent AC1, AC2, AC3, AC6 — modal shows header+body HTML; copy puts that same HTML on the clipboard; dark purple reading surface; Land Meteorite multi-select remains.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminManageEmail.tsx` | Prefer `assembled_html` for the message popup; add Copy control that clips that string | ui |
| `src/ui/frontend/src/App.css` | `.email-html-source` background → dark purple theme token (retire `#fff`) | ui |

## Stage 1: Modal — assembled HTML + copy control

**Done when:** Opening a Manage Email message fills the popup `<pre>` from `data.assembled_html` (not body-only `html_body`); a `btn secondary` Copy control copies that same string via `navigator.clipboard.writeText` and surfaces success on the existing Toast; list-page Land Meteorite / multi-select code paths are untouched; `npx tsc --noEmit` in `src/ui/frontend` succeeds (or the repo’s usual frontend typecheck if that is the established command).

1. In `src/ui/frontend/src/pages/AdminManageEmail.tsx`, rename state `htmlBody` / `setHtmlBody` to `assembledHtml` / `setAssembledHtml` (same `useState("")` shape). Update every read/write site in this file (`openMessage`, `closeModal`, the modal `<pre>` children).

2. In `openMessage`, after a successful GET of `/api/admin/inbox/messages/${id}`, set display content from **`assembled_html` only**:

```ts
setAssembledHtml(
  typeof data.assembled_html === "string" ? data.assembled_html : "",
)
```

Do **not** fall back to `data.html_body` for the popup — body-only would violate AC1. If the field is missing/empty, show the empty pre (same loading/error gates as today).

3. Keep the modal body as the existing source pane: `<pre className="email-html-source" …>{assembledHtml || ""}</pre>` inside `.email-html-frame`. Do **not** switch to `dangerouslySetInnerHTML` / iframe — AST-1040 established raw-HTML source view; this ticket only changes **which string** is shown and adds copy + chrome.

4. Add a Copy control visible when the message body is loaded (`!bodyLoading && !bodyError`), placed in a small toolbar **above** the `.email-html-frame` (inside the Modal children, after the match line). Pattern (mirror `AdminPerformanceMonitor` / `AdminDataManagement`):

```tsx
<div className="manage-email-modal-toolbar">
  <button
    type="button"
    className="btn secondary"
    disabled={!assembledHtml}
    onClick={() => {
      void navigator.clipboard.writeText(assembledHtml).then(() => {
        setToast({ text: "Copied to clipboard", variant: "success" })
      })
    }}
    title="Copy header+body HTML"
  >
    Copy
  </button>
</div>
```

⚠️ **Decision — copy the display string only:** Clipboard content must equal what the `<pre>` shows (`assembledHtml`). Do not re-fetch or reassemble headers on the client.

⚠️ **Decision — `btn secondary`, not primary:** Shared button roles — Copy is a secondary action; Land Meteorite on the list stays `btn primary`. Do not invent new button CSS classes.

⚠️ **Decision — Toast on success, no local “Copied” label state:** Reuse the page’s existing `toast` / `Toast` path (same as Land Meteorite / error paths). Skip the Performance Monitor `copied` boolean + timeout unless Toast is somehow unavailable — it is already wired on this page.

5. Do **not** edit the list toolbar, checkbox column, `onLandMeteorite`, selection helpers, or row click wiring. Modal `Cancel` footer from `Modal` stays as today (`showFooter` default).

## Stage 2: Dark purple reading surface

**Done when:** `.email-html-source` no longer uses `background: #fff`; it uses an existing dark-purple admin CSS variable so the popup reading surface matches admin chrome; text still uses `var(--text-primary)`.

1. In `src/ui/frontend/src/App.css`, update the `.email-html-source` rule (AST-1040 block near the manage-email styles). Change only the background line:

```css
  background: var(--bg-elevated);
```

Leave margin/padding/height/overflow/font/color/`white-space`/`word-break` as they are.

⚠️ **Decision — `--bg-elevated`:** Root theme already defines `--bg-deep` / `--bg-card` / `--bg-elevated` as the dark purple palette (`App.css` `:root`). Elevated is the reading-pane step used elsewhere for inset surfaces; do not hardcode a new hex or invent a new token.

2. Optional class for the Stage 1 toolbar — add only if Stage 1 introduced `.manage-email-modal-toolbar`:

```css
.manage-email-modal-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  padding: 12px 20px 0;
}
```

Place it with the other `.manage-email-*` rules. No other CSS changes.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

```
[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1538
**Overall:** APPROVED
**Publish ref:** `sub/AST-1533/AST-1538-manage-email-modal-copy-dark-purple` @ `93cf11e0ee366120490c72e5b15e69f0cf8f051c`

## Traceability
AC1 → Stage 1 (`assembled_html` in `<pre>`, no `html_body` fallback); AC2 → Stage 1 (Copy clips `assembledHtml`); AC3 → Stage 2 (`--bg-elevated` on `.email-html-source`); AC4 → Scope gate + Stage 1 step 5 (Land Meteorite / multi-select untouched).

## Findings

### discuss
- **Location:** Linear gate — assignee Katherine Johnson, not Joan
- **Finding:** `validate-plan` §1 expects Joan assigned during this pass; ticket is still on the implementer.
- **Recommendation:** Chuckles-only — no plan change; restore assignee after writeback per skill §8.

### acceptable
- **Location:** Stage 1 — Copy `onClick`
- **Finding:** `navigator.clipboard.writeText` has no `.catch()`; failures would be unhandled rejections.
- **Recommendation:** Matches existing admin copy patterns (`AdminPerformanceMonitor`, `AdminDataManagement`); optional hardening, not blocking.

### acceptable
- **Location:** Stage 1 — `<pre title="Email body">`
- **Finding:** Plan does not rename the `title` after switching to header+body source.
- **Recommendation:** Cosmetic polish only.

context_tokens≈58000
```

## Review

**Build tip:** `origin/sub/AST-1533/AST-1538-manage-email-modal-copy-dark-purple` @ `c81121f1`
**Stages:** assembled_html modal + copy → dark purple `.email-html-source`
