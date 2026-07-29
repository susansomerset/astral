# AST-1040 — UAT: Read email modal shows raw HTML source not rendered preview

**Linear:** [AST-1040](https://linear.app/astralcareermatch/issue/AST-1040/uat-read-email-modal-shows-raw-html-source-not-rendered-preview)
**Parent:** [AST-1031](https://linear.app/astralcareermatch/issue/AST-1031/receive-email-on-gmail-account-for-astral) — Receive email on gmail account for astral
**Publish ref:** `origin/sub/AST-1031/AST-1040-uat-read-email-modal-raw-html`

UAT bug on the AST-1033 **Read email** modal: the body panel currently mounts Gmail’s `html_body` via a sandboxed `iframe` `srcDoc`, which **renders** the email. Susan needs the **literal HTML source** (escaped/preformatted text) in that scrollable panel for the ingest-seed spike. No Gmail/API/contract changes.

## UAT fitness

- **AC restored:** Parent AC (quoted on the bug): “Clicking a listed message opens a scrollable modal showing that message’s HTML body as returned by Gmail.”
- **Correct outcome:** Admin can inspect the literal HTML markup Gmail returned (scrollable source) in the modal — not a live rendered email preview.
- **Sibling check:** AST-1032 list/get payload (`html_body` string) unchanged; AST-1033 nav/list/auth/`@require_admin` unchanged — only the modal body presentation in `AdminReadEmail.tsx` (+ CSS) changes. Verified by not touching `src/core/inbox.py`, `src/external/gmail.py`, or `api_inbox.py`.
- **Not sufficient:** Removing the stacktrace / exception / 5xx alone is **not** done. (N/A — this is a presentation AC miss, not a 5xx.)
- **Wrong fix rejected:** Do **not** strip the HTML body, keep-only a rendered preview with no raw view, or “fix” by catching/hiding render errors without showing source. Do **not** switch to `dangerouslySetInnerHTML` (that would still render). Replace the iframe with text that React escapes into a scrollable `<pre>`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminReadEmail.tsx` | Modal body: show `html_body` as escaped source text in `<pre>`, remove iframe/`srcDoc` | ui |
| `src/ui/frontend/src/App.css` | Retarget `.email-html-frame` for scrollable `<pre>` source (drop iframe rules) | ui |

## Stage 1: Raw HTML source in the Read email modal

**Done when:** Clicking an inbox row opens the wide modal and the body area shows the Gmail `html_body` string as visible raw markup (tags readable as text), scrollable inside the modal; empty `html_body` still opens the modal with an empty source panel; no iframe remains for the body.

1. In `src/ui/frontend/src/pages/AdminReadEmail.tsx`, inside the `Modal` success branch (where `!bodyLoading && !bodyError`), **replace** the iframe block:

```tsx
<div className="email-html-frame">
  <iframe title="Email body" sandbox="" srcDoc={htmlBody || ""} />
</div>
```

with:

```tsx
<div className="email-html-frame">
  <pre className="email-html-source" title="Email body">{htmlBody || ""}</pre>
</div>
```

⚠️ **Decision:** Put `{htmlBody || ""}` as a **text child** of `<pre>` so React escapes angle brackets — tags appear as source, never as DOM. Do **not** use `dangerouslySetInnerHTML`, `srcDoc`, or a new iframe. Keep `title="Email body"` on the `<pre>` so existing Betty selectors that look for that accessible name can be retargeted by Betty without inventing a new label.

2. Leave list fetch, row click, loading/error paths, Toast, Modal `size="wide"`, and Cancel-only footer unchanged. Do **not** change `/api/admin/inbox/*` or core/external Gmail modules.

3. In `src/ui/frontend/src/App.css`, replace the AST-1033 iframe block:

```css
/* AST-1033: Gmail HTML preview fills wide modal and scrolls inside the iframe */
.email-html-frame {
  height: 100%;
  overflow: hidden;
}
.email-html-frame iframe {
  display: block;
  width: 100%;
  height: 100%;
  border: 0;
  background: #fff;
}
```

with:

```css
/* AST-1040: Gmail HTML source fills wide modal; scroll inside the pre */
.email-html-frame {
  height: 100%;
  overflow: hidden;
}
.email-html-source {
  margin: 0;
  padding: 16px 20px;
  height: 100%;
  box-sizing: border-box;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 12px;
  line-height: 1.45;
  background: #fff;
  color: var(--text-primary);
}
```

4. Do **not** edit `tests/` or `docs/test-bible/**` (Betty owns those after Code Complete). Existing Vitest cases assert iframe/`srcdoc` — expect Betty to revise them when she picks up Code Complete.

**Done when (recheck):** Modal shows escaped HTML source; scrolling works in the wide modal body; list/auth/API contracts untouched.

## Out of scope (do not implement here)

- Gmail OAuth / list/get / `html_body` extraction (AST-1032).
- Ingest, routing, persistence, mark-read.
- Dual-mode UI (render + raw toggle) — this UAT asks for raw only.
- Editing `tests/` or `docs/test-bible/**`.

## Self-Assessment

**Scope:** `minor` — two UI files; presentation-only change to the AST-1033 modal body.

**Conf:** `high` — Diagnosis matches the iframe `srcDoc` implementation; escaped `<pre>` is the direct AC fix.

**Risk:** `low` — confined to Read email modal body display; API and siblings unchanged. Betty’s iframe assertions will fail until her Code Complete pass (expected).

## Rules self-review

- **§3.2 / §3.3:** UI only; still calls core via existing admin API; no ui→external.
- **`astral.layers.ui-config-driven-business-logic`:** No new inbox rules in React — display-only.
- **`astral.patterns.require-auth-on-protected-endpoints`:** Untouched (`@require_admin` / `AdminRoute` stay).
- **In-scope only:** Modal presentation; no Gmail/credential/ingest creep.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1031/AST-1040-uat-read-email-modal-raw-html`
**Plan path:** `docs/features/meteorite/ast-1040-uat-read-email-modal-raw-html.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `3a8027a6` | Modal body: escaped `<pre>` source; CSS for scrollable source |

**Tip:** `3a8027a6` on `origin/sub/AST-1031/AST-1040-uat-read-email-modal-raw-html`
