<!-- linear-archive: AST-643 archived 2026-06-23 -->

## Linear archive (AST-643)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-643/trigger-adjacent-token-lookup-placement-token-lookup-list  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-638 — Token lookup list  
**Blocked by / blocks / related:** parent: AST-638

### Description

## What this implements

Fix the shared token-autocomplete textarea so the lookup list appears below the active `{$` trigger line instead of covering the textarea. Preserve existing open/filter/dismiss/keyboard behavior. Handle viewport edge cases by flipping above the trigger when there is insufficient room below. All current consumers (Manage Tasks, Manage Agents, Anthropic Ad Hoc) inherit the fix from the shared component.

## Acceptance criteria

1. On Manage Tasks, open any task's edit modal, type `{$` in any prompt segment — the lookup list appears below the trigger line and the partial token text in the textarea remains visible while typing.
2. Typing `}` to close a token manually dismisses the lookup list without requiring Escape or a click.
3. Manage Agents (Add and Edit modals) and Anthropic Ad Hoc (User, Cache, NoCache prompt tabs) show the same corrected placement when triggering autocomplete.
4. Selecting a token from the list or via keyboard still inserts the full `{$TOKEN}` and dismisses the list, with cursor restored as today.
5. Existing `TokenTextarea` component tests pass; tests cover that the dropdown no longer overlays the textarea origin when open.

## Boundaries

* Does not change which tokens appear in the list, token registry, or any admin API endpoints.
* Does not alter token insertion format or preview/resolve behavior on parent screens.
* Does not add autocomplete to new surfaces.
* No backend work.

## Notes for planning

* Shared component used across admin prompt editors; fix once in the component layer.
* plan-child §3.5 — component lives in the flat components directory per Code Rules.

## Git branch (authoritative)

Per **orientation § Branch law**: parent **ftr/ast-638**, child **sub/AST-638/<child-segment>**. Created at dispatch-parent.

### Comments

#### radia — 2026-06-14T20:56:16.309Z
**Review** — `origin/dev...origin/sub/AST-638/AST-643-trigger-adjacent-token-lookup-placement` · doc `d79ec810`

### What's solid
- Stage 1 matches plan: `menuAnchor(ta, triggerCharIndex)` subtracts `scrollTop`, anchors from `{$` index, viewport flip constants, `triggerPos` on scroll/resize reposition. Single-file `TokenTextarea.tsx`; consumers unchanged.
- §3.5 flat `components/`; no layer violations.
- AC5: `AST-643` test — menu `style.top` > textarea `getBoundingClientRect().top` on first-line trigger; AST-636 portal + existing behavior rows intact.

### Advisory
- `docs/ASTRAL_TEST_BIBLE.md` ~1665 — orphan ` ``` ` before §7.13zzp (AST-644 bible merge). Betty cleanup on next bible touch; not blocking.
- Flip-above / scrolled-textarea: manual smoke only per plan; no automated flip test (OK for this ticket).

**Verdict:** clean — no fix-now. Katherine may proceed `resolve-child`.

#### betty — 2026-06-14T20:50:44.952Z
## QA test manifest (AST-643)

**Publish:** `origin/sub/AST-638/AST-643-trigger-adjacent-token-lookup-placement` @ `9dc4b750` (`merge-tests(AST-643): origin/tests 7baf09b1`)

**`docs/ASTRAL_TEST_BIBLE.md` shasum on publish ref:** `4c2934dce05d94b27a765b5091a8ebad96e21ff85a04834d8eb7a77b6b60d964`

### 1. Existing coverage (bible-backed)

Full **`tests/component/frontend/components/test_TokenTextarea.test.tsx`** — open/filter/dismiss/keyboard, **`AST-636`** portal, tab/Enter insertion, outside-click/Escape/closed-token paths.

### 2. New / revised (this pass)

1. **`AST-643`** — `portaled menu anchors below first-line trigger` — menu fixed `style.top` strictly greater than textarea origin when `{$` is on line 1 (AC5).

### 3. Run command

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_TokenTextarea.test.tsx
```

**Bible:** §7.13zzq (parent AST-638). Component-only — no routed-page §6c (shared component; consumers inherit).

#### katherine — 2026-06-14T20:46:04.277Z
Plan: [ast-643-trigger-adjacent-token-lookup-placement.md](https://github.com/susansomerset/astral/blob/sub/AST-638/AST-643-trigger-adjacent-token-lookup-placement/docs/features/interface/ast-643-trigger-adjacent-token-lookup-placement.md)

**Root cause:** `menuAnchor` computes trigger-line Y from line index but omits `textarea.scrollTop`, so the portaled menu (AST-636) anchors to full content height instead of the visible viewport — dropdown overlaps typed text / textarea origin when content scrolls or in tall modals.

**Fix (Stage 1, `TokenTextarea.tsx` only):** subtract `scrollTop`, anchor line index from `triggerPos` (`{$` start), flip above trigger when insufficient room below; no consumer page changes.

**Self-assessment**
- **Scope:** `scope-Single-Component` — one shared component file; pages inherit automatically.
- **Conf:** `conf-high` — extends AST-636 portal pattern with localized scroll/trigger math.
- **Risk:** `risk-low` — isolated dropdown positioning; no API or data impact.

**QA note for Betty:** add placement assertion in `test_TokenTextarea.test.tsx` — open menu `top` must be strictly below textarea `top` on first-line `{$` trigger (AC5).

---

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
- **Diff baseline:** `origin/dev...origin/sub/AST-638/AST-643-trigger-adjacent-token-lookup-placement` (2026-06-14)
- **Built:** 2026-06-14 — Stage 1 complete (`41957eb7`); Betty manifest + placement test landed (`7baf09b1` / merge-tests).

### What's solid

- **Plan fidelity:** `menuAnchor(ta, triggerCharIndex)` matches Stage 1 — subtracts `scrollTop`, anchors from `{$` index (not `selectionStart`), viewport flip via `MENU_MAX_HEIGHT` / `MENU_GAP_PX`, `triggerPos` wired through scroll/resize reposition. No consumer page or backend changes.
- **§3 layer / §3.5:** Single-file change in flat `components/`; no cross-layer imports.
- **AC5 coverage:** `AST-643` test asserts portaled menu `style.top` strictly below textarea viewport origin on first-line trigger; existing AST-636 portal + keyboard/dismiss rows preserved.
- **Scope:** Self-assessment `scope-Single-Component` / `conf-high` / `risk-low` matches diff footprint.

### Issues

| Severity | Location | Note |
| --- | --- | --- |
| advisory | `docs/ASTRAL_TEST_BIBLE.md` ~1665 | Stray orphan ` ``` ` fence inserted before §7.13zzp (AST-644) during bible merge — breaks markdown nesting; Betty cleanup, not AST-643 product scope. |
| advisory | — | Flip-above and scrolled-textarea reposition rely on manual smoke per plan; no automated flip/scrollTop test (acceptable for this ticket). |

### Recommended actions

- **Engineer:** None — proceed to `resolve-child` / User Testing.
- **Betty (optional):** Remove orphan fence in `ASTRAL_TEST_BIBLE.md` §7.13zzp boundary on next bible touch.

## Resolution

- **2026-06-14 — Katherine (`resolve-child`):** Radia review clean — no fix-now items. No product code changes; Stage 1 (`41957eb7`) and Betty placement test (`7baf09b1` / merge-tests `9dc4b750`) stand as shipped. Advisory bible fence (§7.13zzp) deferred to Betty per review. §9a dry-run clean vs `origin/dev` and `origin/ftr/ast-638`. Ticket → **User Testing**.
