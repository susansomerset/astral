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

## Radia review

```
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1538
**Publish ref:** `sub/AST-1533/AST-1538-manage-email-modal-copy-dark-purple` @ `759f8508db8d5e6a63c070de72cdf8f2785799ab`
**Overall:** DISCUSS

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | no agent/prompt paths |
| astral.agent.do-task-delegation | scoped | not-applicable | no `do_task` changes |
| astral.agent.grade-vector-validation | scoped | not-applicable | no grade-vector paths |
| astral.batch.batch-id-first | scoped | not-applicable | no batch claim paths |
| astral.batch.batch-id-format | scoped | not-applicable | no batch id formatting |
| astral.batch.claim-process-release | scoped | not-applicable | no claim/release helpers |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | no entity-agent-response persistence |
| astral.config.config-source-of-truth | scoped | not-applicable | no config edits on 1538 product line (1537 stack on branch only) |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | no secrets/env wiring |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no artifact dirs |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | no spike scripts |
| astral.dispatch.seed-auto-false | scoped | not-applicable | no dispatch seed |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | no `run_next` |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single plan doc `ast-1538-manage-email-modal-copy-dark-purple.md` |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty commits touch test-tree only |
| astral.git.engineer-test-tree-ban | scoped | conforms | `code(AST-1538)` excludes `tests/**` / bible; Betty `test()` + `merge-tests()` own test-tree |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | no `src/core` / `src/external` on 1538 product line |
| astral.layers.import-direction | scoped | conforms | frontend uses existing `api()` to admin inbox route; no `src.data` / `src.external` in TS |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no `scripts/**` |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | no hardcoded job/candidate state strings; display reads API payload |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | no coat-check paths |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | consult untouched |
| astral.idioms.require-auth-on-protected-endpoints | scoped | conforms | message GET still via authenticated `api()` helper |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | no seed JSON |
| astral.seed.archie-catalog-wins | scoped | not-applicable | no catalog overrides |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | no boot seed |
| astral.seed.define-approved | scoped | not-applicable | no define flow |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | no operator seed |
| astral.seed.other-via-coverage-join | scoped | not-applicable | no coverage-join seed |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | no `src/data/**` on 1538 product line |
| astral.standards.database-header-inventory | scoped | not-applicable | no DB/migrations |
| astral.standards.debug-contract-gated | scoped | not-applicable | no backend debug paths on 1538 product line |
| astral.standards.dry-and-focused-functions | scoped | conforms | thin modal change; reuses Toast + existing admin copy pattern |
| astral.standards.in-scope-only | scoped | needs-discussion | publish-ref diff bundles AST-1534 test/bible via `merge-tests`; engineer `code(AST-1538)` stays in scope gate |
| astral.standards.logging-via-utils | scoped | not-applicable | no backend logging changes on 1538 product line |
| astral.standards.names-not-ticket-ids | scoped | conforms | `assembledHtml` naming; no ticket ids in identifiers |
| astral.standards.no-cross-contamination | scoped | needs-discussion | `0f3785db test(AST-1534)` (AST-1532 epic) merged through `merge-tests(AST-1538)` |
| astral.standards.no-hardcoded-sets | scoped | conforms | CSS uses `--bg-elevated` token, not new hex |
| astral.standards.public-then-helpers | scoped | not-applicable | no new Python modules on 1538 product line |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | no utils→data |
| astral.state.core-decides-transitions | scoped | not-applicable | no state transitions |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no job prior-state enforcement |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no run-chain changes |
| astral.ui.frontend-file-placement | scoped | conforms | `pages/AdminManageEmail.tsx` + `App.css` per placement rules |
| astral.ui.naming-conventions | scoped | conforms | camelCase state; BEM-ish manage-email classes |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no server worker config |
| orch.git.betty-merge-tests-one-sha | universal | conforms | tip `merge-tests(AST-1538): origin/tests 3dd075d8` |
| orch.git.commit-vocabulary | universal | conforms | `code`/`test`/`docs`/`merge-tests` vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | `sub/AST-1533/AST-1538-*` publish ref |
| orch.git.ftr-sub-topology | universal | conforms | child on `sub/<parent>/…` |
| orch.git.merge-on-checkout | universal | conforms | no forbidden merge pattern in reviewed commits |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | no cherry-pick/rebase/force |
| orch.git.no-dev-agent-branches | universal | conforms | no agent-named branches |
| orch.git.one-epic-worktree-per-parent | universal | conforms | review in `astral-AST-1533` |
| orch.git.three-permanent-branches | universal | conforms | branch topology respected |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | product tradeoffs in plan ⚠️ decisions |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–2 match plan on product line |
| orch.pipeline.project-scoped-queues | universal | conforms | scoped under AST-1533 |
| orch.pipeline.status-gates-skill-entry | universal | conforms | reviewed at Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | no statute edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty manifest + Vitest block on tip |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee Katherine (engineer) |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Katherine assignee at Tests Passed |
| orch.roles.pre-commit-path-bans | universal | conforms | no banned-path engineer commits evident |

**Active-set count:** 64 rows from `canon/statutes/README.md` § Harvested corpus + universal.

## Pattern conformance

none cited

## Plan adherence

**AST-1538 product (`code(AST-1538)` @ `18ccbc83`–`c81121f1`):** Stage 1 — `htmlBody`→`assembledHtml`; `openMessage` sets `assembled_html` only (no `html_body` fallback); Copy toolbar (`btn secondary`, `navigator.clipboard.writeText`, Toast success); list Land Meteorite / multi-select untouched. Stage 2 — `.email-html-source` background `var(--bg-elevated)`; `.manage-email-modal-toolbar` added. Estimate **2** matches footprint.

**Dependency stack:** Three-dot diff vs `origin/dev` also carries full **AST-1537** product+tests (not on `origin/dev` yet) — expected per plan `Depends on: AST-1537`.

**Joan plan-rubric:** APPROVED @ `93cf11e0`; no Excluded-statute list → no straggler callout.

**C6 lenses:** No `dangerouslySetInnerHTML`; raw `<pre>` source view preserved (AST-1040). Clipboard `.catch()` absent — matches `AdminPerformanceMonitor` / `AdminDataManagement` (Joan acceptable). §5f/§5g N/A (frontend-only ticket).

## Findings

### discuss — cross-epic test bundle on publish ref

- **Location:** `merge-tests(AST-1538)` @ `759f8508` ← `origin/tests` `3dd075d8` ← `0f3785db test(AST-1534)`
- **Finding:** Three-dot diff vs `origin/dev` includes Ad Hoc scoped-list test/bible changes for **AST-1534** (parent **AST-1532**) — `tests/component/{core/test_agent,data/database/test_agent_data,ui/api/test_api_admin,utils/test_config}.py` + bible blocks — merged via Betty's `origin/tests` branch, not in AST-1538 scope gate.
- **Recommendation:** Chuckles/Betty confirm hygiene before ftr rollup: AST-1534 tests should land on `sub/AST-1532/AST-1534-*` (or documented intentional stack). Does **not** block AST-1538 product UT — engineer commits are clean.

### advisory — clipboard error handling

- **Location:** `AdminManageEmail.tsx` Copy `onClick`
- **Finding:** `writeText` has no `.catch()` — unhandled rejection if clipboard denied.
- **Recommendation:** Matches existing admin copy pages; optional hardening, not blocking (Joan acceptable).

### advisory — `<pre title="Email body">`

- **Location:** `AdminManageEmail.tsx` modal source pane
- **Finding:** Title still says "Email body" after switching to header+body source.
- **Recommendation:** Cosmetic polish for AST-1538 or a follow-up Task.

## What's solid

- No `html_body` fallback — explicit test `ignores html_body when assembled_html missing` guards AC1.
- Copy clips the exact `<pre>` string (`assembledHtml`), not a client-side reassembly.
- Dark purple uses existing `--bg-elevated` token — no new hex.
- Betty Vitest manifest covers assembled modal, copy+toast, CSS token, and preserves AST-1142 Land Meteorite regression describe.

## Frame diff

Prior issue-doc stub (`docs(AST-1538): review stub — build complete` @ `c81121f1`) covered product only. Tip adds:

- `test(AST-1538): Manage Email assembled modal copy + dark purple` — `test_AdminManageEmail.test.tsx` + `docs/test-bible/frontend/pages.md`
- `merge-tests(AST-1538): origin/tests 3dd075d8` — also folds **`test(AST-1534)`** test/bible from `origin/tests` (see discuss finding)

Product `AdminManageEmail.tsx` / `App.css` unchanged since `c81121f1`.

## Notes

- C7 complete — Chuckles may append, `docs()` push, post slim upshot, move to **Review Posted**.
- **resolve-child:** product findings none; discuss item is merge/tests hygiene only — Chuckles decides whether to re-merge tests or document stack before UT.
- **Downstream:** Parent AC1–AC3 satisfied once AST-1537+AST-1538 both on ftr; modal depends on `assembled_html` from 1537 API.

context_tokens≈45000

---
```

## Resolution

**Date:** 2026-08-29  
**Tip before resolve:** `origin/sub/AST-1533/AST-1538-manage-email-modal-copy-dark-purple` @ `87aeec2d` (Radia `docs()` intake)

| Bucket | Action |
|--------|--------|
| **fix-now** | none |
| **discuss** — AST-1534 test/bible via `merge-tests` | No engineer product change. Out of AST-1538 scope gate; Radia: does **not** block product UT. Chuckles spawned `resolve-child` → proceed. Hygiene (re-merge vs documented stack) remains Chuckles/Betty before ftr rollup if needed. |
| **advisory** — clipboard `.catch()` | Left as-is — matches `AdminPerformanceMonitor` / `AdminDataManagement` (Joan + Radia acceptable). |
| **advisory** — `<pre title>` | Deferred — Betty Vitest selects via `getByTitle("Email body")`; renaming needs `[qa-handoff]` / bible+test revise. Cosmetic only. |

Product delta this pass: none (Resolution doc only).
