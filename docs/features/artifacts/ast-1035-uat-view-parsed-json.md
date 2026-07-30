# UAT: View Parsed JSON button on Session Resume Paste

**Linear:** [AST-1035](https://linear.app/astralcareermatch/issue/AST-1035/uat-view-parsed-json-button-on-session-resume-paste)
**Parent:** [AST-1019](https://linear.app/astralcareermatch/issue/AST-1019/take-2-resume-render-format-discrepancies) — Take 2: Resume Render Format discrepancies
**Publish ref:** `origin/sub/AST-1019/AST-1035-uat-view-parsed-json`

Session Resume Paste already keeps the successful Parse payload in `lastParse` (`resume_structure` + `base_resume`) and posts that same object to Open HTML — but the UI only exposes Parse and Open HTML controls. Susan cannot inspect the intermediate JSON to tell whether a remaining UAT gap is structure vs renderer. Add a **View Parsed JSON** control between those two buttons that shows the current `lastParse` payload read-only.

## UAT fitness

- **AC restored:** Parent AC (quoted on the bug): *“Susan can verify by eye against the desired HTML for every laundry-list item; no judgment call on ‘close enough.’”* / *“Fixture-driven UAT: Original-brief input paste → Open HTML matches desired structure + cosmetics (eye + HTML source). No ‘close enough.’”* Susan confirmed this debug affordance is **in scope for AST-1019** (under-defined original specification).
- **Correct outcome:** After a successful Parse, Susan can click **View Parsed JSON** (placed between Parse and Open HTML) and see the structured resume JSON — the same `resume_structure` + `base_resume` object Open HTML consumes — in a read-only display. Button disabled when there is no successful parse payload.
- **Sibling check:** AST-1020/1021 render cosmetics unchanged. AST-1027–1030 emit/marker contracts unchanged. AST-985/986/987 Session Resume Paste → Open HTML path unchanged (same `lastParse` body to `/api/admin/session_resume/html`). Verify: no new API; no candidate DB write; no JSON dumped into resume HTML.
- **Not sufficient:** Button label alone is **not** done — the view must show the same parse payload Open HTML uses.
- **Wrong fix rejected:** Dumping JSON into the resume HTML body; changing renderer contracts to invent missing fields; persisting session paste to the candidate DB; inventing new resume sections; a separate fetch that could diverge from `lastParse`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminSessionResumePaste.tsx` | Add **View Parsed JSON** between Parse and Open HTML; read-only display of `lastParse` (same object Open HTML posts) | ui/frontend |

**Out of scope (do not touch):** `src/core/builder.py` / stylesheet / marker emit; `/session_resume/parse` or `/html` contracts except as already consumed; cover-letter page; candidate DB persistence; `tests/` / bible (Betty).

## Root cause (plan-time)

`AdminSessionResumePaste.tsx` already stores `SessionResumeParse = { resume_structure, base_resume }` in `session_resume:last_parse` and `handleOpenHtml` POSTs `JSON.stringify(lastParse)` to `/api/admin/session_resume/html`. The button row only renders Parse + Open HTML — no inspect control. No backend gap for this UAT ask; the payload is already in memory/localStorage after Parse.

**Git hygiene:** Keep `origin/sub/AST-1019/AST-1035-uat-view-parsed-json` rooted on current `origin/ftr/ast-1019-take-2-resume-render-format-discrepancies` with only AST-1035 vocabulary commits in the `ftr..sub` range. Do **not** leave subjects matching `Merge remote-tracking branch` (validate-sub-log / merge-child gate).

## Stage 1: View Parsed JSON control + read-only display

**Done when:** On Session Resume Paste, after a successful Parse, a **View Parsed JSON** button sits between **Parse** and **Open HTML**; it is disabled when `lastParse` is null (and while parsing/opening as appropriate); activating it shows a read-only pretty-printed JSON of the **exact** `lastParse` object (`resume_structure` + `base_resume`) that Open HTML would POST; closing the view returns to the page without clearing `lastParse` or changing paste text. No new API routes. No changes to parse/html backend handlers.

1. In `src/ui/frontend/src/pages/AdminSessionResumePaste.tsx`:
   - Import the shared `Modal` component used by other admin pages (same pattern as `AdminManageCandidates.tsx` JSON view modal).
   - Add React state for whether the JSON modal is open (e.g. `jsonOpen` boolean), default `false`.
   - In the button row (`display: flex` after the textarea), insert a **View Parsed JSON** button **between** Parse and Open HTML:
     - `type="button"`, class consistent with siblings (`dep-btn` is fine — not the primary `save` style unless Parse stays primary).
     - Label: `View Parsed JSON`.
     - `disabled={!lastParse || parsing || opening}` (same gating spirit as Open HTML — no payload → disabled).
     - `onClick` sets the modal open (`true`). Does **not** call any API.
   - Render `<Modal open={jsonOpen} onClose={…} title="Parsed resume JSON">` (title may be tightened; must clearly identify the parse payload) containing a `<pre>` with `JSON.stringify(lastParse, null, 2)` when `lastParse` is non-null. Style the `<pre>` like Manage Candidates’ view modal (`whiteSpace: pre-wrap`, scrollable `maxHeight`, monospace-friendly font size) — reuse that look, do not invent a new design system.
   - Modal close must only clear `jsonOpen`; leave `lastParse` / localStorage intact.
2. Optionally tighten the page blurb one sentence to mention View Parsed JSON between Parse and Open HTML (keep it short; do not rewrite the whole help text).
3. Do **not** change `handleParse` / `handleOpenHtml` request/response contracts.
4. Do **not** add backend routes or persist JSON to the candidate DB.
5. Do **not** edit `tests/` or bible — Betty owns assertions after Code Complete.
   ⚠️ **Decision:** Modal + `JSON.stringify(lastParse)` (not a new-tab blob and not an inline always-visible dump). Modal matches existing admin “view JSON” UX (`AdminManageCandidates`); showing `lastParse` guarantees identity with the Open HTML POST body without a second fetch. New-tab would work but adds popup-blocker noise next to Open HTML.

## Stage 2: Compile check + manual smoke (build verification)

**Done when:** `npx tsc -b --noEmit` under `src/ui/frontend` passes after Stage 1. Manual/build smoke: with mocked or live session, Parse success → View Parsed JSON enabled → modal shows both `resume_structure` and `base_resume` keys; Open HTML still posts the same object; before Parse, View Parsed JSON is disabled. Spike dumps only under `debug/spikes/AST-1035/` if used — never commit; never repo-root `artifacts/`.

1. During **build-child**, run `cd src/ui/frontend && npx tsc -b --noEmit` after the TSX edit.
2. Confirm `git diff` does not touch `src/core/**`, `data/admin/**`, or test-tree paths.
3. Note for UAT: after deploy, Session Resume Paste → Parse → View Parsed JSON → confirm JSON matches what Open HTML uses; then Open HTML still works.
4. If Modal import path or shared Modal API differs from Manage Candidates in a way that blocks a literal reuse, **stop**, comment on **bug** AST-1035 with the Stage blocked template (propose the concrete Modal import that exists), and wait.

## Self-Assessment

**Scope:** `Single-Component` — `AdminSessionResumePaste.tsx` only (UI control + read-only Modal over existing `lastParse`).

**Conf:** `high` — payload already in `lastParse`; Open HTML already posts it; Manage Candidates Modal+`<pre>` pattern exists on the same frontend.

**Risk:** `low` — additive UI only; no parse/html contract change; disabled state mirrors Open HTML gating.

## Code Rules self-review

- §1.3 DRY: reuse shared `Modal` + existing `lastParse`; no parallel parse fetch.
- §1.1 / scope isolation: no builder/CSS/marker edits; no DB persistence; no cover-letter page edits.
- §3.5 naming: button label matches ticket (**View Parsed JSON**).
- §3.6: spikes under `debug/spikes/AST-1035/` only if used.
- Engineer test-tree ban: no `tests/` or bible edits.

## Review (Radia — code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1035
**Publish ref tip (pre-docs):** `91d25515c9cd4c458394a4e8351556d5569ac68c`
**Overall:** CLEAN

### What’s solid

- **View Parsed JSON** between Parse and Open HTML; disabled when `!lastParse` (and while parsing/opening).
- Modal + `JSON.stringify(lastParse, null, 2)` — same object Open HTML POSTs; shared `Modal` + Manage Candidates `<pre>` look.
- No new API / DB / builder edits. Engineer footprint is one TSX file + plan.

### Issues / findings

None (fix-now / discuss).

### Recommended actions

resolve-child → User Testing.
