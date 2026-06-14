# Trigger-adjacent token lookup placement (Token lookup list)

**Linear:** [AST-643](https://linear.app/astralcareermatch/issue/AST-643/trigger-adjacent-token-lookup-placement-token-lookup-list)  
**Parent:** [AST-638](https://linear.app/astralcareermatch/issue/AST-638/token-lookup-list)  
**Publish ref:** `sub/AST-638/AST-643-trigger-adjacent-token-lookup-placement`

Susan reported the token lookup dropdown covers the textarea while typing partial `{$…` names. AST-636 fixed modal clipping by portaling the menu to `document.body` with `position: fixed`, but `menuAnchor` still computes Y from the trigger line index **without subtracting `textarea.scrollTop`**, so the menu is anchored to the full content height instead of the visible viewport — it appears too low (often overlapping typed text or the textarea origin). This ticket corrects trigger-line anchoring, adds viewport flip when there is insufficient room below, and leaves open/filter/dismiss/keyboard behavior unchanged. All consumers inherit the fix from the shared component.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/TokenTextarea.tsx` | Fix `menuAnchor` scroll/trigger math; viewport flip; wire `triggerPos` through reposition | ui |

**QA manifest (Betty — not engineer commits):** extend `tests/component/frontend/components/test_TokenTextarea.test.tsx` so an open menu’s `getBoundingClientRect().top` is **strictly greater** than the textarea’s `getBoundingClientRect().top` when `{$` is triggered on the first line (AC5 — dropdown must not overlay the textarea origin). Preserve existing AST-636 portal test and all current behavior tests.

## Stage 1: Correct trigger-line anchoring and viewport flip

**Done when:** Typing `{$` in any `TokenTextarea` shows the portaled menu immediately below the trigger line (partial token text remains visible); when the trigger is on the last visible line inside a short modal and there is not enough room below, the menu flips above the trigger line without clipping off-screen; `}` still dismisses; keyboard/mouse selection unchanged; existing component tests still pass (Betty adds placement assertion in qa-child).

1. In `src/ui/frontend/src/components/TokenTextarea.tsx`, add a module-level constant immediately after the imports:
   ```typescript
   const MENU_MAX_HEIGHT = 180
   const MENU_GAP_PX = 4
   ```

2. Replace the existing `menuAnchor` helper (lines 14–27) with a function that accepts the trigger character index and returns placement side:

   ```typescript
   type MenuAnchor = { top: number; left: number; width: number; placement: "below" | "above" }

   function menuAnchor(ta: HTMLTextAreaElement, triggerCharIndex: number): MenuAnchor {
     const style = getComputedStyle(ta)
     const lineHeight = Number.parseFloat(style.lineHeight) || 18
     const padTop = Number.parseFloat(style.paddingTop) || 0
     const padLeft = Number.parseFloat(style.paddingLeft) || 0
     const padRight = Number.parseFloat(style.paddingRight) || 0
     const rect = ta.getBoundingClientRect()
     const triggerLine = ta.value.substring(0, triggerCharIndex).split("\n").length - 1
     const triggerLineTop = rect.top + padTop + triggerLine * lineHeight - ta.scrollTop
     const triggerLineBottom = triggerLineTop + lineHeight
     const belowTop = triggerLineBottom + MENU_GAP_PX
     const spaceBelow = window.innerHeight - belowTop
     const spaceAbove = triggerLineTop - rect.top
     const left = rect.left + padLeft
     const width = rect.width - padLeft - padRight
     if (spaceBelow >= MENU_MAX_HEIGHT || spaceBelow >= spaceAbove) {
       return { top: belowTop, left, width, placement: "below" }
     }
     return {
       top: Math.max(8, triggerLineTop - MENU_MAX_HEIGHT - MENU_GAP_PX),
       left,
       width,
       placement: "above",
     }
   }
   ```

   ⚠️ **Decision:** Subtract `ta.scrollTop` so line math matches the visible textarea viewport (standard caret-in-scrollable-textarea pattern). Without it, scrolled textareas misplace the menu over the textarea origin — the reported bug.

   ⚠️ **Decision:** Anchor line index from `triggerCharIndex` (the `{$` start), not `selectionStart`, so reposition-on-scroll stays tied to the active trigger even if selection and trigger diverge briefly.

3. Extend `menuPos` state to carry placement (or add parallel `menuPlacement` state). Minimal approach — widen the state object:

   ```typescript
   const [menuPos, setMenuPos] = useState<{ top: number; left: number; width: number; placement: "below" | "above" }>({
     top: 0, left: 0, width: 0, placement: "below",
   })
   ```

4. In `checkTrigger` (line ~68), replace `setMenuPos(menuAnchor(ta))` with:

   ```typescript
   setMenuPos(menuAnchor(ta, lastOpen))
   ```

   Use `lastOpen` (the computed `{$` index) — the same value already stored via `setTriggerPos(lastOpen)`.

5. In the scroll/resize `useEffect` reposition callback (line ~109), replace:

   ```typescript
   if (ref.current) setMenuPos(menuAnchor(ref.current))
   ```

   with:

   ```typescript
   if (ref.current && triggerPos >= 0) setMenuPos(menuAnchor(ref.current, triggerPos))
   ```

   Add `triggerPos` to the effect dependency array alongside `show`.

6. In the portaled menu `style` block (line ~148), replace hard-coded `maxHeight: 180` with `maxHeight: MENU_MAX_HEIGHT`. No other visual or z-index changes.

7. Do **not** change: trigger regex/filter rules, `insertToken`, keyboard handlers, outside-click handler, portal target (`document.body`), or consumer pages (`AdminTaskPrompts.tsx`, `AdminAgentPrompts.tsx`, `AdminAnthropicAdHoc.tsx`).

8. Manual smoke (build-child, before Code Complete): in Manage Tasks edit modal, type `{$` on line 1 — menu below typed text; scroll textarea so trigger is on last visible row in a short modal — menu flips above or stays on-screen; type `}` — menu dismisses; Enter/click still inserts `{$TOKEN}`.

## Execution contract

- Execute Stage 1 only; one `code()` commit on publish ref during **build-child** (this plan stage is planning-only).
- Do not edit `tests/` or `docs/ASTRAL_TEST_BIBLE.md`.
- Blocking ambiguity → comment on **AST-638** with 🛑 template from **plan-child**.

## Self-Assessment

**Scope:** `scope-Single-Component` — Only `TokenTextarea.tsx` in the flat components directory; no page wiring or backend.

**Conf:** `conf-high` — AST-636 established the portal pattern; this is a localized math fix plus flip logic with a clear repro and existing test harness.

**Risk:** `risk-low` — Isolated UI positioning; worst case is dropdown placement regression recoverable without data or API impact.

## Self-review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Extends existing `menuAnchor`; no duplicate positioning logic in pages. |
| §2.1 config | No new config keys; UI-only constants at module scope. |
| §2.4 batch | N/A — no batch processing. |
| §2.6 state machine | N/A — no entity states. |
| §3.3 imports | Stays within `src/ui/frontend/`; no cross-layer imports. |
| §3.5 naming | Component remains in flat `components/` per Code Rules header inventory. |

No conflicts flagged.

## Review

- **Branch:** `origin/sub/AST-638/AST-643-trigger-adjacent-token-lookup-placement`
- **Built:** 2026-06-14 — Stage 1 complete (`41957eb7`); Betty manifest pending for AC5 placement test.
