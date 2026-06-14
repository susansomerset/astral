# AST-636 — UAT: Manage Agents {$ token autocomplete dropdown missing

- **Linear (this ticket):** [AST-636](https://linear.app/astralcareermatch/issue/AST-636/uat-manage-agents-dollar-token-autocomplete-dropdown-missing)
- **Parent:** [AST-574](https://linear.app/astralcareermatch/issue/AST-574/support-tokens-in-agent-prompts) (AC4 — Manage Agents token autocomplete)
- **Publish ref:** `origin/sub/AST-574/AST-636-uat-manage-agents-token-autocomplete-dropdown-missing`
- **Sibling reference:** [AST-632 plan](ast-632-manage-agents-token-autocomplete-and-preview.md) — wiring landed; UAT shows picker still invisible in browser

## Summary

AST-632 wired `TokenTextarea` and `GET /api/admin/agents/meta/tokens` into `AdminAgentPrompts.tsx`. Unit tests pass when the token list loads, but Susan's UAT repro shows **no visible picker** when typing `{$` in Add/Edit Agent modals while Manage Tasks works. Investigation narrowed this to two concrete failure modes: (1) the autocomplete menu is `position: absolute; top: 0` inside ancestors with `overflow: hidden` / `overflow-y: auto` (`.modal-card`, `.modal-body`), so the menu can render off-screen or clipped in the taller Manage Agents modal; (2) `useAgentTokenList` silently sets `[]` when `/api/admin/agents/meta/tokens` is non-OK or returns a non-array, and `TokenTextarea` only renders the menu when `filtered.length > 0`. This bug fix restores visible, usable autocomplete in Manage Agents without changing token registry, runtime resolution, or Manage Tasks behavior.

## Out of scope

| Item | Owner |
|------|--------|
| Runtime token resolution (AST-631) | Shipped |
| New registry tokens | — |
| Manage Tasks UI changes beyond shared `TokenTextarea` fix | — |
| Betty test manifest / `tests/` edits | Betty (`qa-child`) |

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/TokenTextarea.tsx` | Portal autocomplete menu to `document.body`; anchor near caret; z-index above modals; fix outside-click target | ui |
| `src/ui/frontend/src/pages/AdminAgentPrompts.tsx` | Harden `useAgentTokenList` — check `r.ok` before parsing JSON | ui |

## Stage 1: TokenTextarea — portaled, caret-anchored autocomplete menu

**Done when:** Typing `{$` in Manage Agents Add/Edit modal shows a visible token list (same tokens as `GET /api/admin/agents/meta/tokens`); selecting a token inserts `{$TOKEN_NAME}`; Manage Tasks autocomplete still works; existing `test_TokenTextarea.test.tsx` cases remain green.

1. In `src/ui/frontend/src/components/TokenTextarea.tsx`, add `import { createPortal } from "react-dom"`.

2. In the same file, **above** the component export, add a helper that returns viewport coordinates for the menu (no new dependencies):

```typescript
function menuAnchor(ta: HTMLTextAreaElement): { top: number; left: number; width: number } {
  const style = getComputedStyle(ta)
  const lineHeight = Number.parseFloat(style.lineHeight) || 18
  const padTop = Number.parseFloat(style.paddingTop) || 0
  const padLeft = Number.parseFloat(style.paddingLeft) || 0
  const padRight = Number.parseFloat(style.paddingRight) || 0
  const lines = ta.value.substring(0, ta.selectionStart).split("\n").length - 1
  const rect = ta.getBoundingClientRect()
  return {
    top: rect.top + padTop + (lines + 1) * lineHeight,
    left: rect.left + padLeft,
    width: rect.width - padLeft - padRight,
  }
}
```

3. Inside `TokenTextarea`, add:
   - `const menuRef = useRef<HTMLDivElement>(null)`
   - `const [menuPos, setMenuPos] = useState({ top: 0, left: 0, width: 0 })`

4. In `checkTrigger`, after the existing logic sets `setShow(true)` (and before return paths that call `dismiss()`), when the trigger is active and `ref.current` exists, call `setMenuPos(menuAnchor(ref.current))`.

5. Add a `useEffect` that runs when `show` is true:
   - Define `reposition = () => { if (ref.current) setMenuPos(menuAnchor(ref.current)) }`
   - `window.addEventListener("scroll", reposition, true)` (capture — catches `.modal-body` scroll)
   - `window.addEventListener("resize", reposition)`
   - Cleanup both listeners on unmount / when `show` becomes false.

6. Replace the inline `{show && filtered.length > 0 && (<div style={{ position: "absolute", top: 0, ...` block with a portaled menu:

```tsx
{show && filtered.length > 0 && createPortal(
  <div
    ref={menuRef}
    style={{
      position: "fixed",
      top: menuPos.top,
      left: menuPos.left,
      width: menuPos.width,
      maxHeight: 180,
      overflowY: "auto",
      background: "var(--bg-elevated)",
      border: "1px solid var(--border)",
      borderRadius: 4,
      zIndex: 3000,
      boxShadow: "0 4px 12px rgba(0,0,0,0.4)",
    }}
  >
    {/* existing filtered.map token rows — unchanged click/keyboard handlers */}
  </div>,
  document.body,
)}
```

7. Update the outside-click `useEffect` handler (lines ~88–95) so dismissal only happens when the event target is **outside both** the textarea wrapper **and** `menuRef.current`:

```typescript
const handler = (e: MouseEvent) => {
  const t = e.target as Node
  if (ref.current?.parentElement?.contains(t)) return
  if (menuRef.current?.contains(t)) return
  dismiss()
}
```

⚠️ **Decision:** Fix the shared `TokenTextarea` (portal + caret anchor) instead of a Manage Agents–only CSS override. AST-632 avoided touching this component, but both Manage Tasks and Manage Agents render it inside scrollable modals; absolute `top: 0` is the common failure. Portaling matches existing patterns (`Modal.tsx`, `Toast.tsx`) and fixes clipping for all consumers.

## Stage 2: AdminAgentPrompts — harden agent token list fetch

**Done when:** `useAgentTokenList` ignores non-OK `/api/admin/agents/meta/tokens` responses (empty list, no throw); when the endpoint returns a JSON array, `TokenTextarea` receives it in both Add and Edit modals.

1. In `src/ui/frontend/src/pages/AdminAgentPrompts.tsx`, in `useAgentTokenList` (~lines 42–50), replace the `api(...).then(r => r.json())` chain with:

```typescript
api("/api/admin/agents/meta/tokens")
  .then(async r => {
    if (!r.ok) { setTokenList([]); return }
    const data = await r.json()
    setTokenList(Array.isArray(data) ? data : [])
  })
  .catch(() => setTokenList([]))
```

No other changes to `AdminAgentPrompts.tsx` in this ticket.

## Manual verification (Susan UAT repro)

1. Log in as admin → **Manage Agents**.
2. **Add Agent** → focus System Prompt Content → type `{$` → token list appears; pick `{$FIRST_NAME}` (or similar) → placeholder inserted.
3. **Edit** an existing agent → repeat step 2 at end of long content (scroll modal if needed) → list still visible near cursor.
4. **Manage Tasks** → edit a task prompt → type `{$` → list still works (regression check).

## Self-Assessment

**Scope:** `Single-Component` — primary change is `TokenTextarea.tsx` (shared UI component); one small fetch guard in `AdminAgentPrompts.tsx`.

**Conf:** `high` — failure modes reproduced in component tests (empty token list → no menu; loaded tokens → menu renders); fix reuses existing `createPortal` patterns and does not touch backend or token registry.

**Risk:** `Medium` — `TokenTextarea` is shared by Manage Tasks and Manage Agents; incorrect portal/position logic could regress task authoring, but the change is localized to menu rendering and outside-click handling.

## Code rules check

- §1.3 DRY: extend shared `TokenTextarea`; no duplicate autocomplete in page files.
- §3.3 imports: `createPortal` from `react-dom` (already used in `Modal.tsx`).
- §3.5 UI: no new dependencies; frontend-only; API token list remains config-driven via existing endpoint.
- No `tests/` or `ASTRAL_TEST_BIBLE.md` edits in this ticket (Betty manifest).

## Review (build-child)

**Built:** `origin/sub/AST-574/AST-636-uat-manage-agents-token-autocomplete-dropdown-missing` @ `2e20662a`

| Commit | Summary |
|--------|---------|
| `6ff12ac0` | Stage 1: portal `TokenTextarea` autocomplete menu to fix modal clipping |
| `2e20662a` | Stage 2: harden `useAgentTokenList` for non-OK API responses |

**Verification:** `cd src/ui/frontend && npx tsc -b --noEmit`

## Review (Radia)

**Diff:** `origin/ftr/ast-574-support-tokens-in-agent-prompts...origin/sub/AST-574/AST-636-uat-manage-agents-token-autocomplete-dropdown-missing` @ `151d4968` (product: `6ff12ac0`, `2e20662a`; tests merge `151d4968`).

### What's solid

| Area | Notes |
|------|--------|
| Plan fidelity | Stage 1–2 match plan: `menuAnchor` + portaled `createPortal` menu (`zIndex: 3000` above `.modal-overlay` 1000/2000); scroll/resize reposition; outside-click includes `menuRef`; `useAgentTokenList` checks `r.ok` before JSON |
| UAT repro | Root causes from ticket (modal clipping + empty list on non-OK meta) addressed without backend/registry/Manage Tasks scope creep |
| §1.3 DRY | Shared `TokenTextarea` fix benefits all consumers; matches `Modal.tsx` / `Toast.tsx` portal pattern |
| §3.5 | Frontend-only; token list still config-driven via existing `GET /agents/meta/tokens` |
| Tests | `test_TokenTextarea` portal-to-`document.body` under `overflow:hidden`; `test_AdminAgentPrompts` edit-modal autocomplete + non-OK meta tolerance |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| — | — | No fix-now items |

### Recommended actions

| Priority | Action |
|----------|--------|
| Advisory | `menuAnchor` uses line-count vertical offset only (plan-approved); wrapped long lines may anchor menu at textarea left edge rather than horizontal caret — acceptable vs prior `top:0` clipping |
| — | Katherine: **`resolve-child`** — no code changes required from this review |
