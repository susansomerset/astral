# Execution History copy control left-aligned (Move the "copy" link to the left side of the page)

**Linear:** [AST-672](https://linear.app/astralcareermatch/issue/AST-672/execution-history-copy-control-left-aligned-move-the-copy-link-to-the)  
**Parent:** [AST-670](https://linear.app/astralcareermatch/issue/AST-670/move-the-copy-link-to-the-left-side-of-the-page)  
**Publish ref:** `sub/AST-670/AST-672-execution-history-copy-left`

On Execution History (`/admin/performance`), the expanded batch log panel shows a **Copy logs to clipboard** control on the right edge of the toolbar because `.dispatch-log-toolbar` uses `justify-content: flex-end`. Susan must horizontal-scroll past the wide ledger to reach it. This ticket left-aligns that toolbar only; copy payload, feedback text, and all other Execution History behavior stay unchanged.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/App.css` | `.dispatch-log-toolbar`: `justify-content: flex-start` (replace `flex-end`) | ui |
| `tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx` | Import `App.css`; assert toolbar flex alignment after log expand | ui (QA) |

**Out of scope:** `AdminPerformanceMonitor.tsx` markup/logic (unless a test import is required), other admin screens, backend, log fetch, ledger columns, frozen-column layout, candidate filter, Agent Data modal.

## Stage 1: Left-align log toolbar

**Done when:** Expanded batch log panel shows the **Copy** button on the left side of the toolbar (flex start). Loading and empty log panels remain unchanged (no copy control). No TSX or copy-handler changes.

1. In `src/ui/frontend/src/App.css`, in the `.dispatch-log-toolbar` rule (~line 1753), change:
   ```css
   justify-content: flex-end;
   ```
   to:
   ```css
   justify-content: flex-start;
   ```
2. Leave `.dispatch-log-copy-btn`, `.dispatch-log-panel`, and all other dispatch-log rules unchanged.
3. Do **not** edit `LogViewer` in `src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx` — placement is CSS-only.

⚠️ **Decision:** Toolbar-level `flex-start` rather than reordering DOM or adding a wrapper. The toolbar has a single control today; flex alignment is the minimal change and matches how right alignment was implemented.

## Stage 2: Component regression — copy placement (ticket AC1 / Notes)

**Done when:** Existing expand + copy integration test still passes; toolbar alignment is asserted when logs are visible. Vitest file green.

1. At the top of `tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx` (after existing imports), add:
   ```ts
   import "../../../../src/ui/frontend/src/App.css"
   ```
2. In the existing test `loads ledger rows, filters, expands logs, and opens batch modal`, after `await waitFor(() => expect(screen.getByText("failed")).toBeInTheDocument())` and **before** the copy click:
   ```ts
   const copyBtn = screen.getByTitle("Copy logs to clipboard")
   const toolbar = copyBtn.closest(".dispatch-log-toolbar")
   expect(toolbar).not.toBeNull()
   expect(getComputedStyle(toolbar!).justifyContent).toMatch(/flex-start|start/)
   ```
3. Keep the existing clipboard assertions (`userEvent.click(copyBtn)` and `expect(navigator.clipboard.writeText).toHaveBeenCalled()`).
4. Run from repo root:
   ```bash
   npm run test -- tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx
   ```
   All tests in that file must pass before `code()` commit.

⚠️ **Decision:** Assert computed `justify-content` after importing `App.css` so jsdom applies the rule. If a future Vitest/CSS pipeline change breaks computed-style reads, stop and comment on AST-672 with 🛑 — do not add TSX or inline styles to satisfy the test.

## Self-Assessment

**Scope:** `minor` — one CSS property in `App.css` plus a small extension to an existing component test file; no backend or shared hook changes.

**Conf:** `high` — right alignment is explicitly `flex-end` on `.dispatch-log-toolbar`; ticket and parent AST-670 scope UI placement only with no open questions.

**Risk:** `low` — only the expanded log toolbar flex alignment changes; copy behavior, ledger table, filters, and modals are untouched.

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Reuses existing toolbar markup and classes; no duplicate copy UI. |
| §2.1 Config | No config changes. |
| §2.4 Batch | N/A — no batch processing. |
| §2.6 State machine | N/A — no state transitions. |
| §3.3 Imports | Test file adds one CSS import only; no layer violations. |
| §3.5 Naming / placement | No new components; styles stay in `App.css` § dispatch-log block. |
| §3.6 Spike output | N/A — no spike artifacts. |

No conflicts flagged. Plan is implementable as written.

## Review

- **Branch:** `origin/sub/AST-670/AST-672-execution-history-copy-left` @ `4460e707`
- **Baseline:** `origin/dev` (three-dot diff)
- **Reviewed:** 2026-06-15 — Radia

### What's solid

| Area | Notes |
|------|--------|
| Plan Stage 1 | `App.css` `.dispatch-log-toolbar` `flex-end` → `flex-start` only; no TSX or copy-handler edits — matches ticket AC1–5 and boundaries. |
| Scope | `scope-minor` footprint holds: one CSS property + test extension; no backend, ledger, or sibling-ticket smuggling. |
| §3.2 / G1 | No new hardcoded state; placement stays in global CSS where dispatch-log styles already live. |
| Copy behavior | `LogViewer` clipboard join + **Copied** feedback unchanged; integration test still clicks copy and asserts `writeText`. |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| **discuss** | `test_AdminPerformanceMonitor.test.tsx` — `ensureDispatchLogToolbarCss()` | Plan Stage 2 ⚠️ said: if Vitest/jsdom cannot read `App.css`, stop with 🛑 — **do not** inject inline styles. Betty documented the inject workaround in the QA manifest; product CSS is correct, but the assertion is sourced from the injected `<style>` tag, so reverting `App.css` to `flex-end` would **not** fail this test. Confirm Susan accepts documented inject vs Vitest CSS pipeline fix. |
| **advisory** | `docs/test-bible/frontend/pages.md` § AST-672 | Manifest row cites `import App.css` as the guard; actual test relies on `beforeAll` inject per Betty's note — align bible wording when inject stays. |

### Recommended actions

| Item | Action |
|------|--------|
| discuss (test inject) | **Susan / Katherine:** accept inject as standing jsdom workaround **or** remove inject and fix component-test CSS loading so `getComputedStyle` reads real `App.css`. |
| advisory (bible) | Betty or resolve-child: update AST-672 manifest bullet to match chosen approach. |
