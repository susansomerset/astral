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

