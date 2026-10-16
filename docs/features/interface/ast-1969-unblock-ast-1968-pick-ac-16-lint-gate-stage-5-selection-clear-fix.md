# AST-1969 — Unblock AST-1968: pick AC 16 lint gate + Stage 5 selection-clear fix

<!-- linear-archive: AST-1969 archived 2026-10-08 -->

## Linear archive (AST-1969)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1969/unblock-ast-1968-pick-ac-16-lint-gate-stage-5-selection-clear-fix  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** unassigned  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** blocks: AST-1967

### Description

**Need:** pick a lint gate for AST-1968's AC 16 ("`npm run lint` exits 0"), plus one Stage 5 fix choice. Ada has built all six stages (build + tsc clean) and is holding Code Complete until you answer.

**Why:** `npm run lint` already fails on `origin/dev` @ `79c4f9b44` with 27 errors / 5 warnings in \~25 files outside AST-1968's scope, so AC 16 cannot pass as written. One baseline hit is in scope: `JobsRecommended.tsx:78` (`react-hooks/set-state-in-effect`, the existing error-toast effect). Separately, the plan's Stage 5 selection-clear `useEffect` adds one new error of the same rule.

**Q1 — AC 16 gate** (pick one):

1. "No new lint problems vs `origin/dev`" — no extra code.
2. Option 1 plus fix the in-scope hit at `JobsRecommended.tsx:78`.
3. Clear all baseline errors (separate ticket recommended).

**Q2 — Stage 5 new lint error** (pick one):

1. **(Ada recommends)** Drop the effect; clear selection in `load` when `showSpinner` is true — same behaviour, zero new lint, one line.
2. Keep the effect and accept the +1.
3. Hold selection as `{ owner: candidateId, ids }` and derive empty on candidate switch (\~4 lines, no effect).

Full detail: Ada's two comments on [AST-1967](https://linear.app/astralcareermatch/issue/AST-1967).

Reply here with your picks; the agents will apply them in the repo — you do not need to push. Move this ticket to **Done** when answered. Neither AST-1968 (stays with Ada) nor AST-1967 (stays with Chuckles) is assigned to you.

### Comments

#### susan — 2026-10-04T14:34:54.867Z
Q1: 2

Q2: 1

---

_Implementation detail may live in git history on `origin/dev`._
