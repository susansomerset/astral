<!-- linear-archive: AST-1040 archived 2026-08-05 -->

## Linear archive (AST-1040)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1040/uat-read-email-modal-shows-raw-html-source-not-rendered-preview  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** hedy  
**Priority / estimate:** High / —  
**Parent:** AST-1031 — Receive email on gmail account for astral  
**Blocked by / blocks / related:** parent: AST-1031

### Description

## What failed

On **Read email**, opening a message shows the HTML body as a **rendered browser view** inside the scrollable modal. Susan wants to see the **raw HTML source** in that panel instead.

## Expected

The scrollable modal shows the message’s HTML body **as raw source text** (as returned by Gmail), not as a live rendered email preview.

## Repro

1. Open admin **Read email**.
2. Click any inbox message that has an HTML body.
3. Observe the modal — content renders like a browser email view rather than raw markup.

## Parent AC (quoted inline)

> Clicking a listed message opens a scrollable modal showing that message’s HTML body as returned by Gmail.

## Diagnosis

* **Hypothesis:** The modal mounts the HTML body via DOM/HTML rendering (e.g. `dangerouslySetInnerHTML` or equivalent) instead of displaying the returned string as escaped/preformatted source text.
* **Correct outcome:** Admin can inspect the literal HTML markup Gmail returned (scrollable source), which is what she needs for this ingest-seed spike.
* **Wrong fix to avoid:** Stripping the HTML body entirely; keeping only a rendered preview with no raw view; “fixing” by catching/hiding render errors without showing source.
* **Related siblings / contracts:** AST-1033 owns the admin modal; AST-1032 list/get payload contract (HTML body string) must stay unchanged.

## Boundaries

* This bug does **not** change Gmail fetch/OAuth (AST-1032).
* This bug does **not** add ingest/routing.
* “No more rendered preview” alone is **not** done — Parent AC + Correct outcome (raw HTML visible) must hold.

### Comments

#### radia — 2026-07-29T17:07:20.650Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1040
**Publish ref:** `origin/sub/AST-1031/AST-1040-uat-read-email-modal-raw-html` @ `eca02653` (product tip `88cf0033` + docs review)
**Overall:** CLEAN

**Diff:** `origin/dev...origin/sub/AST-1031/AST-1040-uat-read-email-modal-raw-html` — `AdminReadEmail.tsx` + `App.css` (+ plan + Betty tests/bible).
**Notes:** no plan-rubric verdict attached — not a block. UAT bug fix matches plan Stage 1 exactly.

## Statutes checked

| id | tier | verdict | one-line |
| -- | -- | -- | -- |
| astral.agent.confidence-bounds | scoped | not-applicable | layers miss (`core`/`utils`) |
| astral.agent.do-task-delegation | scoped | not-applicable | layers miss (`core`) |
| astral.agent.grade-vector-validation | scoped | not-applicable | layers miss (`core`) |
| astral.batch.batch-id-first | scoped | not-applicable | layers miss (`core`/`data`) |
| astral.batch.batch-id-format | scoped | not-applicable | layers miss (`core`/`data`) |
| astral.batch.claim-process-release | scoped | not-applicable | layers miss (`core`/`data`) |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | layers miss (`core`/`data`) |
| astral.config.config-source-of-truth | scoped | conforms | No config.py change; display-only UI |
| astral.config.pass-threshold-vs-score-floor | scoped | not-applicable | layers miss |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No secrets; Gmail/API untouched |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Plan under `docs/features/` — not a misplaced spike |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Single plan file for AST-1040 |
| astral.git.betty-no-src-or-features | scoped | conforms | Engineer owns src/features; Betty owns tests/bible |
| astral.git.engineer-test-tree-ban | scoped | conforms | `test()`/`merge-tests()` are Betty |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | layers miss (`core`/`external`) |
| astral.layers.import-direction | scoped | conforms | UI-only; no new imports / no ui→external |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers miss (`scripts`) |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | Display-only; no new inbox rules in React |
| astral.patterns.coat-check-never-store-empty | scoped | not-applicable | layers miss (`core`) |
| astral.patterns.render-verdict-orchestrates-consult | scoped | not-applicable | layers miss (`core`) |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | Auth/nav/`@require_admin` untouched |
| astral.standards.data-raises-caller-logs | scoped | conforms | No API/data path changes |
| astral.standards.database-header-inventory | scoped | not-applicable | layers miss (`data`) |
| astral.standards.debug-contract-gated | scoped | conforms | No Style D `debug=` surface |
| astral.standards.dry-and-focused-functions | scoped | conforms | One-line modal body swap + CSS retarget |
| astral.standards.in-scope-only | scoped | conforms | Modal presentation only; no Gmail/ingest creep |
| astral.standards.logging-via-utils | scoped | conforms | No new logging |
| astral.standards.no-cross-contamination | scoped | conforms | Frontend-only |
| astral.standards.no-hardcoded-sets | scoped | conforms | No new behavior enums |
| astral.standards.public-then-helpers | scoped | conforms | No new helpers |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | layers miss (`utils`) |
| astral.state.core-decides-transitions | scoped | not-applicable | layers miss (`core`/`data`) |
| astral.state.job-prior-states-enforced | scoped | not-applicable | layers miss |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | layers miss (`core`) |
| astral.ui.frontend-file-placement | scoped | conforms | Existing flat `pages/AdminReadEmail.tsx`; CSS in `App.css` |
| astral.ui.naming-conventions | scoped | conforms | Existing page/path naming unchanged |
| astral.ui.single-gunicorn-worker | scoped | conforms | Untouched |
| orch.git.betty-merge-tests-one-sha | universal | conforms | Single `merge-tests(AST-1040)` @ `88cf0033` |
| orch.git.commit-vocabulary | universal | conforms | `docs`/`code`/`test`/`merge-tests` vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | Child work on `sub/*` |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1031/AST-1040-uat-read-email-modal-raw-html` |
| orch.git.merge-on-checkout | universal | conforms | `origin/ftr/...` already ancestor before docs() |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No rewrite ops in tip history |
| orch.git.no-dev-agent-branches | universal | conforms | Ticket sub only |
| orch.git.one-epic-worktree-per-parent | universal | conforms | `astral-AST-1031` |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | UAT expected outcome already decided (raw source) |
| orch.pipeline.plan-is-bible | universal | conforms | Stage 1 matches shipped `<pre>` + CSS |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Meteorite child |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Review from Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty owns tests/bible on publish ref |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee remains Hedy |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Hedy stays assignee through Review Posted |
| orch.roles.pre-commit-path-bans | universal | conforms | Docs-only Radia commit |

## Pattern conformance

none cited (ticket citations are layer/auth statutes already covered above; plan cites ui-config / require-auth / in-scope — all conform).

## Plan adherence

Self-Assessment **minor** / high / low matches the two-file UI tip. Iframe `srcDoc` → escaped `<pre class="email-html-source">` text child; CSS scrollable source; no API/core/external/auth changes. Parent AC + Correct outcome (raw HTML visible) restored.

## Findings

### fix-now
(none)

### discuss
(none)

### What’s solid
- React text child escapes markup; no `dangerouslySetInnerHTML` / iframe regression.
- Wide-modal scroll via `.email-html-source { overflow: auto }`.

### Recommended actions
- Hedy: resolve-child → User Testing.

context_tokens≈28000

#### betty — 2026-07-29T17:05:10.845Z
1. `tests/component/frontend/pages/test_AdminReadEmail.test.tsx` — revised modal body: escaped `<pre title="Email body">` raw source (no iframe/`srcdoc`); empty source panel; list/body error paths unchanged

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminReadEmail.test.tsx
```

**Pass:** Vitest green on narrowed args.

**Broken/revised:** AST-1033 iframe/`sandbox`/`srcdoc` assertions → raw `<pre class="email-html-source">` text content.
**Integration:** none.

**Publish:** `origin/sub/AST-1031/AST-1040-uat-read-email-modal-raw-html` @ `88cf0033` (`merge-tests(AST-1040): origin/tests 9392af242d6d309f82f55600d046b4babf8d3123`)

**Bible shasums on publish ref:**
- `docs/test-bible/frontend/pages.md` `e04a0763a86cfbed5aaeec5e8a356401c6629574`

— Betty

#### hedy — 2026-07-29T17:02:01.367Z
Plan published on `origin/sub/AST-1031/AST-1040-uat-read-email-modal-raw-html` @ `b652179b`.

**Plan:** [docs/features/meteorite/ast-1040-uat-read-email-modal-raw-html.md](https://github.com/susansomerset/astral/blob/sub/AST-1031/AST-1040-uat-read-email-modal-raw-html/docs/features/meteorite/ast-1040-uat-read-email-modal-raw-html.md)

**Self-assessment**
- **Scope:** minor — two UI files; swap iframe `srcDoc` render for escaped `<pre>` source text in the Read email modal.
- **Conf:** high — Diagnosis matches the AST-1033 iframe implementation; React text child is the direct raw-source fix.
- **Risk:** low — presentation-only; AST-1032 payload and auth/nav untouched. Betty’s iframe Vitest cases will need her Code Complete revise.

---

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

**Tip:** `17ec6714635c325c13ff77748eda0a072a7bc053` on `origin/sub/AST-1031/AST-1040-uat-read-email-modal-raw-html`

## Radia review (code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1040
**Publish ref tip (pre-docs):** `88cf003339550e389c11347d0ad85ab09e0576f7`
**Overall:** CLEAN

### What’s solid
- Iframe/`srcDoc` replaced with escaped `<pre>` text child — raw source, React-escaped tags.
- CSS retargeted for scrollable monospace source; list/auth/API untouched.
- Scope matches Self-Assessment **minor**; Betty revised Vitest accordingly.

### Issues
(none)

### Recommended actions
- Hedy: resolve-child → User Testing.

## Resolution

**Date:** 2026-07-29
**Review:** Radia @ `eca02653` — **Overall:** CLEAN; **fix-now:** none; **discuss:** none.

No product changes. Advanced to **User Testing**.
