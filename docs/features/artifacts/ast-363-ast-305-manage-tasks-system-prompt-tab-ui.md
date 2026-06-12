# AST-305 — Manage Tasks System Prompt Tab UI

**Linear:** https://linear.app/astralcareermatch/issue/AST-363/ast-305-manage-tasks-system-prompt-tab-ui  
**Feature branch:** `ftr/AST-363`

Child of **AST-305**. System prompt editing on **Admin → Task Prompts** (`AdminTaskPrompts.tsx`): **System** `CollapsiblePanel`, load/save `system_prompt` via `PUT /api/admin/tasks/:key` (**AST-361** on `origin/dev`). Empty value shows placeholder for agent default / `{$SELECTED_AGENT}`.

---

## Files Changed (as built)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminTaskPrompts.tsx` | System `CollapsiblePanel`, `editSystem`, PUT includes `system_prompt`. | ui |
| `src/ui/api/api_admin.py` | Uses existing task PUT (`system_prompt` column — **AST-361**). | ui |
| `tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx` | System panel + PUT body coverage. | tests |

*(Original plan named `ManageTasks.tsx` / `TASK_CONFIG` file edits; implementation correctly uses DB-backed admin tasks — see Radia **discuss** below.)*

---

## Stage 1–4

Delivered per build comment `881c16ce`; `tsc -b --noEmit` clean.

---

## Self-Assessment

**Scope — `Single-Component`** · **Conf — `LOW`** · **Risk — `Medium`**

---

## Review (build)

**Branch:** `ftr/AST-363`  
**Commits:** `881c16ce` (product), `1b5d4f41` (tests)

§3.5 CSS. **Conflicts:** none.

---

## Radia review (review-astral 2026-05-16)

**Diff:** `origin/dev...origin/ftr/AST-363`

### What's solid

- `AdminTaskPrompts.tsx`: System `CollapsiblePanel`, load/save `system_prompt` via `PUT /api/admin/tasks/:key`.
- Placeholder for empty → agent default / `{$SELECTED_AGENT}`.
- Tests: system panel + PUT body assertion.

### Issues

| Severity | Item |
|----------|------|
| **discuss** | Plan referenced `ManageTasks.tsx` / `TASK_CONFIG` — actual path is **AdminTaskPrompts** + admin API (addressed in **Resolution**). |

**Counts:** 0 fix-now · 1 discuss · 0 advisory — Radia

---

## Resolution (resolve-astral 2026-05-16)

- **Fix-now:** none.
- **Discuss:** Plan doc updated to match shipped paths (`AdminTaskPrompts`, admin API); removed stale `TASK_CONFIG` / `ManageTasks.tsx` assumptions.
- **Advisory:** none acted on.
- **Branch:** `origin/ftr/AST-363` ready for **prep-uat** under parent **AST-305**.

— Katherine

