# AST-1511 — Show Differences modal does not scroll

<!-- linear-archive: AST-1511 archived 2026-09-09 -->

## Linear archive (AST-1511)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1511/show-differences-modal-does-not-scroll  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1455 — Add "Show Differences" and "Update file with table version"  
**Blocked by / blocks / related:** parent: AST-1455

### Description

[bug]

The modal screen does not scroll, so I can only see the first three differences.

## As-is

- [X] The Show Differences modal on Manage Agents / Manage Tasks does not scroll, so only the first few row/field differences are visible (Susan saw three).

## To-be

- [X] The Show Differences modal scrolls (or otherwise shows all differences) so the operator can review every added/removed/changed row and field.

## Suggested engineer

Katherine Johnson (AST-1506 — Show Differences banner/modal UI)

### Comments

#### katherine — 2026-08-27T12:53:15.377Z
origin/sub/AST-1455/AST-1511-show-differences-modal-does-not-scroll @ `b612660d` · §9a clean · ftr dry-run clean

#### radia — 2026-08-27T12:50:41.760Z
[code-rubric] PROCEED (Commit: 46870882) modal scroll wrapper fixed

#### chuckles — 2026-08-27T03:58:29.922Z
[check-linear] Tests Passed — not UAT yet; fix lane still needs review-fix, then User Testing, then merge into parent ftr. Parent prep-uat waits until AST-1511 is UT with AST-1505/AST-1506.

#### susan — 2026-08-27T03:57:28.404Z
@chuckles What's next? Is this ready for uat?

#### katherine — 2026-08-27T00:55:02.251Z
origin/sub/AST-1455/AST-1511-show-differences-modal-does-not-scroll @ `46870882` · modal scrolls

#### betty — 2026-08-27T00:52:00.453Z
[bug-repro]
`origin/sub/AST-1455/AST-1511-show-differences-modal-does-not-scroll` @ `dbc44800` · repro lands red, awaits fix

#### betty — 2026-08-27T00:51:49.593Z
[bug-repro]
`origin/sub/AST-1455/AST-1511-show-differences-modal-does-not-scroll` @ `PENDING` · repro lands red, awaits fix

#### joan — 2026-08-27T00:50:38.295Z
[board-joan]  CANON: OK

#### betty — 2026-08-27T00:42:08.608Z
[board-betty] TESTS: REVISE
What: docs/test-bible/frontend/components.md § AST-1506 — missing modal scroll reachability — extend test_RepoJsonDivergenceBanner.test.tsx with ≥4 changed_rows and assert 4th row_key reachable after scroll (plan-fix § Repro)

#### katherine — 2026-08-27T00:25:52.403Z
origin/sub/AST-1455/AST-1511-show-differences-modal-does-not-scroll @ `daaef3d1829adc9f1c19a076f69a94eafa8728b8` · modal scroll wrapper

---

_Implementation detail may live in git history on `origin/dev`._

## Bug: AST-1764 — shared Modal vertically scrollable

### As-is

New and existing admin modals keep shipping without reliable vertical scroll. Default `.modal-body` already uses `overflow-y: auto`, but `.modal-card--wide .modal-body` sets `overflow: hidden` (and `padding: 0`) so nested SideTabPanel / email-html layouts can own scroll. Callers that put tall content **directly** in the wide body (no inner scroll wrapper) clip below the first viewport — the same failure AST-1511 fixed only for Show Differences with a local wrapper. The clip keeps recurring on every new wide modal that skips that wrapper.

### To-be

The shared `Modal` / `App.css` shell owns vertical scroll by default: when body content exceeds the card height, the operator can scroll the rest while the header (and footer, when present) stay put. Wide modals that nest their own scroll region (SideTabPanel, `.email-html-source`, batch-agent wrappers, etc.) still fill height and scroll correctly. New modals inherit scroll without inventing another per-screen wrapper.

### Repro

1. Sign in as admin; open any screen that mounts `<Modal size="wide">` with tall content placed **directly** in the body (no inner `height: 100%; overflow: auto` wrapper) — e.g. Manage Tasks / Manage Agents **Show Differences** with the AST-1511 wrapper temporarily ignored, or any wide modal whose children are unconstrained tall markup.
2. Observe the modal card at ~`90vh` with header visible and body content cut off below the fold.
3. Attempt to scroll the body (wheel / trackpad / scrollbar).
4. **Actual:** no shell scroll; content below the first viewport is unreachable unless that screen invented its own wrapper. **Expected:** `.modal-body` (wide included) scrolls so all body content is reachable; header/footer stay put.

Component-test shape (Betty, if board asks): mount shared `Modal` with `size="wide"` and ≥N tall direct children (or a fixture taller than the card); assert a below-the-fold node is reachable via body `scrollTop` / `scrollIntoView` without a call-site wrapper. Nested-owner smoke: wide Modal → `SideTabPanel` (or `.email-html-source`) still fills height and scrolls inside its own region.

### Root cause

`Modal.tsx` applies `modal-card--wide` when `size="wide"`. In `App.css`, `.modal-card--wide .modal-body` intentionally sets `overflow: hidden` so nested panels stretch to the flex body and own scroll. That contract is correct for SideTabPanel / email-html / batch wrappers, but it makes the **shell** a clip box for any tall direct child. AST-1511 papered over one call site (`RepoJsonDivergenceBanner` inline scroll div) and explicitly avoided changing global wide-modal CSS — so the same clip returns on every new wide modal that forgets a wrapper.

### Proposed change

**In scope only:** `src/ui/frontend/src/App.css`, `src/ui/frontend/src/components/Modal.tsx`. Do **not** rewrite feature screens (including removing the AST-1511 Show Differences wrapper) unless a call site fights the new shell contract after the CSS change.

#### 1. Primary — `App.css` (preferred; try first)

Update the wide-body block (~lines 2157–2162):

```css
/* Wide body fills remaining height; shell scrolls tall direct children.
   Nested owners that set height:100% still fill the body and keep their
   own overflow — they do not grow the body's scrollHeight. */
.modal-card--wide .modal-body {
  flex: 1;
  min-height: 0;       /* required so the flex child can shrink and scroll */
  overflow-y: auto;    /* was: overflow: hidden — that clipped direct children */
  padding: 0;          /* keep edge-to-edge for SideTabPanel / email-html */
}
```

Also update the stale comment above `.batch-agent-data-wrapper` (~line 2092) that still says the wide modal “sets overflow:hidden” so it matches the new contract.

Default (non-wide) `.modal-body` already has `overflow-y: auto` + `flex: 1` — leave it; confirm header/footer stay outside the scrolling region (they are siblings of `.modal-body` inside the column flex card).

#### 2. Contingency — nested owners fight shell scroll

If after (1) a known nested-scroll layout double-scrolls, collapses, or clips (spot-check: Job/Company `SideTabPanel`, Read email `.email-html-source` / `.email-html-frame`, `BatchAgentDataModal` `.batch-agent-data-wrapper`, entity `.entity-summary`, Recommended report `.recommended-report-shell`):

Add App.css contain rules that restore `overflow: hidden` **only** when the body has a known nested scroll root as a **direct** child (no call-site edits):

```css
.modal-card--wide .modal-body:has(> .side-tab-panel),
.modal-card--wide .modal-body:has(> .email-html-frame),
.modal-card--wide .modal-body:has(> .batch-agent-data-wrapper),
.modal-card--wide .modal-body:has(> .entity-summary),
.modal-card--wide .modal-body:has(> .recommended-report-shell) {
  overflow: hidden;
}
```

Extend the `:has(> …)` list only for roots that actually regress — do not pre-emptively contain every wide child.

#### 3. Contingency — `Modal.tsx` only if CSS alone cannot express the contract

If `:has()` is insufficient (or a nested owner is not a direct child / lacks a stable class):

- Always attach a size-aware body class when `size="wide"` (e.g. `modal-body--wide`) so CSS can target the shell without relying on `.modal-card--wide .modal-body` alone — **no call-site API change**.
- Only if that still fails: add an optional prop (e.g. `scrollContain?: boolean`) that adds `modal-body--contain` → `overflow: hidden`, defaulting to shell scroll. Using the prop on Job/Company/email call sites is allowed **only** under the ticket Boundary “unless a call site fights the new shell contract”; prefer the CSS contingencies first so new modals keep inheriting scroll with zero props.

No other files. Do not resurrect AST-1511’s ftr. Leave `RepoJsonDivergenceBanner`’s local wrapper in place (harmless once the shell scrolls; removing it is out of scope).

### Blast radius

- Every `size="wide"` `Modal` consumer: Job/Company detail (`SideTabPanel`), Recommended report, Meteorite detail, Materials preview, Batch agent data, Manage Email HTML source, Candidate intake, Admin data management, Show Differences (`RepoJsonDivergenceBanner`), etc.
- Default (non-wide) modals should be unchanged.
- AST-1511’s local wrapper remains; scroll may be nested (wrapper inside scrolling body) but content stays reachable.
- CSS comments / mental model that “wide ⇒ overflow:hidden” become wrong — update the one known comment in `App.css` as part of the change.
- Tests that assumed wide body never scrolls (if any) need Betty’s board call; this ticket does not invent test-tree work.

### What must still hold

- Tall content in a **default** `Modal` still scrolls inside `.modal-body`; header/footer stay put.
- Tall content in a **wide** `Modal` with direct body children is reachable via vertical scroll (AC for this bug).
- Wide modals that nest their own scroll region (SideTabPanel, email HTML source, batch-agent wrapper) still fill the card height and scroll correctly inside that region — no regression from lifting the shell contract.
- New modals inherit scroll without a per-screen wrapper.
- Show Differences (AST-1511 AC) remains fully reviewable end-to-end (wrapper and/or shell).
- Dirty-close / footer / `showFooter={false}` / `stacked` overlay behavior on `Modal` unchanged.

## Review — Radia (AST-1764)

**Overall:** CLEAN / PROCEED @ `8a8510f4`

**What must still hold:** OK (default Modal scroll; wide direct-child scroll via `min-height:0` + `overflow-y:auto`; nested SideTabPanel/email/batch owners preserved; dirty-close/footer untouched — Modal.tsx not in diff).

**fix-now:** none. **discuss:** none.

**Advisory:** sibling AST-1767 owns Betty TESTS: REVISE (shared Modal shell scroll coverage). Stale RepoJsonDivergenceBanner comment about overflow:hidden is out of scope.

## Bug: AST-1767 — gap: shared Modal shell scroll test coverage

### As-is

`docs/test-bible/frontend/components.md` § Modal / `test_Modal.test.tsx` cover footer catalog classes, icon-control ×, and `showFooter` — not shell scroll. The only modal-scroll `[bug-repro]` is **AST-1511** on `RepoJsonDivergenceBanner` (call-site inner wrapper). Nothing asserts that a **wide shared `Modal`** with tall content placed **directly** in `.modal-body` (no wrapper) is scroll-reachable after AST-1764’s shell contract.

### To-be

Bible + component coverage names and asserts shared wide Modal shell scroll: a below-the-fold direct child is reachable via `.modal-body` scroll. The `[bug-repro]` node is red against pre-AST-1764 product (`overflow: hidden` on `.modal-card--wide .modal-body`) and green after AST-1764 (`overflow-y: auto` + `min-height: 0`). No product code on this ticket.

### Repro

**Pre-fix (red):** product tip **before** `code(AST-1764)` (`8a8510f4`) — wide body still `overflow: hidden`.

**Post-fix (green):** product tip at/after `8a8510f4` (or current `ftr` / this gap’s synced tree with AST-1764 merged).

1. Import `App.css` in the Modal component suite (same pattern as `test_AdminPerformanceMonitor.test.tsx` for computed styles).
2. Mount `<Modal open size="wide" showFooter={false} …>` with **only** tall direct children (no inner scroll wrapper) — e.g. ≥6 markers each with a large `minHeight` (≈120px+), last marker text `below-fold-marker`.
3. Optionally pin `.modal-card--wide { height: 240px }` (or similar) in the test so jsdom has a definite card height.
4. Select `document.querySelector(".modal-card--wide .modal-body")`.
5. **Assert (gate):** `getComputedStyle(modalBody).overflowY` matches `/auto|scroll/` (not `hidden`).
6. **Assert (reachability):** set `modalBody.scrollTop = modalBody.scrollHeight` (or `scrollIntoView` on the last marker); expect `below-fold-marker` visible / in the document after scroll.

**Actual pre-fix:** step 5 fails (`overflowY === "hidden"`); tall direct children clipped. **Expected post-fix:** steps 5–6 pass.

Narrowed run:

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_Modal.test.tsx \
  -t "AST-1767"
```

### Root cause

Betty `[board-betty] TESTS: REVISE` on AST-1764: bible/suite hole — AST-1511 only locks the Show Differences **call-site** wrapper, so a future regression that reverts wide `.modal-body` to `overflow: hidden` would not fail any shared-`Modal` test. Product fix already landed on AST-1764; this gap owns the missing lock.

### Proposed change

**In scope only (tests + bible — no product):**

1. **`tests/component/frontend/components/test_Modal.test.tsx`** (astral-tests / worktree test tree — Betty delivery path):
   - Add `import "../../../../src/ui/frontend/src/App.css"` (or path consistent with sibling suites).
   - Add describe **`Modal — AST-1767`** with one it titled exactly:
     **`[bug-repro] AST-1767: wide Modal body scrolls tall direct children`**
   - Body: mount shared `Modal` `size="wide"` with tall **direct** children only; assert `getComputedStyle(.modal-card--wide .modal-body).overflowY` is `auto`/`scroll`; assert last marker reachable after `scrollTop` / `scrollIntoView`.
   - Do **not** assert RepoJsonDivergenceBanner or any feature-screen wrapper; do **not** edit product `Modal.tsx` / `App.css`.

2. **`docs/test-bible/frontend/components.md`**:
   - Add section **`### AST-1767 · AST-1754 (gap — shared Modal shell scroll)`** near other Modal / AST-1511 entries.
   - Table row: Area = shared wide Modal shell scroll for tall direct children; Source = `Modal.tsx` + `App.css` (product owned by AST-1764); Component tests = **`test_Modal.test.tsx`** — the `[bug-repro]` node above.
   - Note: does **not** obsolete AST-1511 (call-site wrapper still covered separately).
   - QA manifest + narrowed vitest command matching the Repro block.

**Out of scope:** any `src/ui/frontend/**` product edit (AST-1764). Nested-owner smoke (SideTabPanel / email-html) is optional advisory only — not required for this gap’s AC.

### Blast radius

- Extends `test_Modal.test.tsx` only (existing AST-1301 / AST-1302 / AST-1334 nodes must stay green).
- Bible `components.md` gains one section; AST-1511 section unchanged.
- Product tree / AST-1764 CSS contract unchanged by this ticket.
- Future shell regressions that set wide `.modal-body` back to `overflow: hidden` fail this `[bug-repro]` instead of only failing (or missing) call-site coverage.

### What must still hold

- AST-1764 product AC remains true on the synced tree (wide shell scrolls; nested owners still work) — this ticket does not re-implement or weaken it.
- Existing `test_Modal.test.tsx` cases (closed render, dirty-close, AST-1301/1302/1334) stay green.
- AST-1511 `[bug-repro]` on `RepoJsonDivergenceBanner` remains the call-site wrapper lock — not deleted or rewritten as the shell test.
- No product files in the gap diff.

## Review — Radia (AST-1767)

**Overall:** REVIEW @ `2033f32a` — `[bug-repro]` OK; fix-now: trim publish tip.

**fix-now:** `merge-tests(AST-1767)` pulled unrelated `origin/tests` paths onto the publish ref. `origin/ftr/AST-1754-all-modals-must-be-vertically-scrollable...origin/sub/AST-1754/AST-1767-gap-modal-shell-scroll-tests` must contain only AST-1767-owned paths (plus plan doc).

## Resolution — AST-1767 (2026-09-22)

**Fix-now status:** Engineer cannot land the trim — pre-commit path ban blocks Katherine from committing under `tests/` / `docs/test-bible/**` (even restores-to-ftr). Working-tree restore of non-owned paths to `origin/ftr/AST-1754-all-modals-must-be-vertically-scrollable` was prepared and verified locally, then discarded uncommitted.

**Betty must republish** `origin/sub/AST-1754/AST-1767-gap-modal-shell-scroll-tests` so `origin/ftr/AST-1754-all-modals-must-be-vertically-scrollable...origin/sub/…` contains **only**:

- `docs/features/agent/ast-1511-show-differences-modal-does-not-scroll.md`
- `docs/test-bible/frontend/components.md` (§ AST-1767)
- `tests/component/frontend/components/test_Modal.test.tsx` (`[bug-repro] AST-1767`)

Restore every other path in the current ftr…sub diff to the ftr tip (delete `tests/component/frontend/pages/test_CandidateWritingPreferences.test.tsx` if absent on ftr). Keep `[bug-repro]` green. Then reassign Katherine.

