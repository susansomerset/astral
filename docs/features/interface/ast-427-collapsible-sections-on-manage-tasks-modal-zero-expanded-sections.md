# Collapsible sections on Manage Tasks Modal: zero expanded sections

**Linear:** https://linear.app/astralcareermatch/issue/AST-427/collapsible-sections-on-manage-tasks-modal-zero-expanded-sections  
**Parent:** [AST-426](https://linear.app/astralcareermatch/issue/AST-426/collapsible-sections-on-manage-tasks-modal)  
**Feature ref:** `sub/AST-426/AST-427-collapsible-sections-on-manage-tasks-modal` (origin only; child of AST-426)

Manage Tasks (`AdminTaskPrompts`) and artifact criteria (`ArtifactEditor`) both use **`CollapsiblePanel`** with parent-owned single-open state. Criteria already allow **zero** expanded sections (`setExpandedTabId("")` on collapse). The **edit modal** on Manage Tasks does not: each prompt panel’s `onExpandedChange` handler, on collapse, **opens the next panel in a fixed order** instead of clearing selection, so the user can never collapse all four prompt panels. The main list’s phase sections already allow `openPhase === null`. This plan aligns the edit modal with the criteria pattern, adds regression tests, and adjusts collapsed-stack CSS only if tests show a visual defect.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminTaskPrompts.tsx` | Allow `editOpenPanel === null`; collapse handlers clear selection; optional wrapper class for scoped Stage 2 CSS | ui |
| `src/ui/frontend/src/App.css` | Optional: collapsed-stack header borders scoped to edit-modal panel stack only | ui |
| `tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx` | Assert edit modal + list can hold zero expanded sections | ui |
| `tests/component/frontend/components/test_CollapsiblePanel.test.tsx` | Assert multiple controlled siblings all `expanded={false}` | ui |

Do **not** edit `CollapsiblePanel.tsx` unless Stage 2 proves a component-level fix is required (expected: parent handlers only). Do **not** change Flask, `src/ui/api`, or `src/core`.

---

## Stage 1: Edit modal — allow zero expanded prompt panels

**Done when:** Opening the edit modal, the user can collapse every prompt `CollapsiblePanel` so **no** prompt textarea is visible; Save/Preview/default-panel dropdown still work; `cd src/ui/frontend && npx tsc -b --noEmit` passes.

1. In `src/ui/frontend/src/pages/AdminTaskPrompts.tsx`, change **`editOpenPanel`** state from `useState<TabKey>("user")` to **`useState<TabKey | null>(null)`**. Keep **`openEdit`** behavior: after load, still call `setEditOpenPanel(def)` where `def = readDefaultEditPanel()` so the modal **opens** with the user’s preferred panel expanded (unchanged product behavior on open).

2. For **all four** edit-modal `CollapsiblePanel` blocks (System, User, Cache, NoCache), replace the `onExpandedChange` **`else`** branch that computes `order[i + 1] ?? order[i - 1] ?? …` with the same pattern as **`ArtifactEditor`** (lines ~412–415): **`else setEditOpenPanel(null)`**. The **`if (next)`** branch stays: set the matching `TabKey`. Remove the unused `order` / `indexOf` logic in those handlers.

3. Leave the **main list** phase `CollapsiblePanel` handlers unchanged (`else setOpenPhase(null)` — already correct).

4. Leave the **default panel** `<select>` `onChange` as-is: it may still call `setEditOpenPanel(v)` when the user picks a default (explicit expand). Do **not** add a “none” default option unless Susan asks — acceptance is **ability to collapse all**, not changing the persisted default preference enum.

5. Run `cd src/ui/frontend && npx tsc -b --noEmit`.

⚠️ **Decision:** Fix at the **consumer** (`AdminTaskPrompts`) only, mirroring **`ArtifactEditor`**, rather than teaching `CollapsiblePanel` about accordion groups. Keeps the shared component dumb and avoids changing criteria behavior.

---

## Stage 2: Collapsed-stack CSS (only if needed)

**Done when:** With all edit-modal panels collapsed, the modal body has no double borders, clipped overflow, or empty giant whitespace; if no defect is visible in Stage 3 tests, this stage is **skipped** with a one-line Linear comment: “Stage 2 skipped — no CSS defect observed.”

1. After Stage 1, run the new tests from Stage 3. If stacked collapsed panels show **double header borders** or broken spacing **inside the edit modal only**, add rules in `src/ui/frontend/src/App.css` scoped to the Manage Tasks edit modal stack — **not** global `.collapsible-panel` selectors that also hit `ArtifactEditor` criteria stacks. Prefer a wrapper on the prompt panel stack in `AdminTaskPrompts.tsx` if needed (e.g. class `admin-task-prompts-edit-panels` on the `dep-field` that wraps the four panels), then target collapsed headers under that wrapper only, for example:

   ```css
   .admin-task-prompts-edit-panels .collapsible-panel:not(.is-expanded) .collapsible-panel-header {
     border-bottom: none;
   }
   ```

   Apply only what fixes the observed defect; do **not** change expanded-panel styling on criteria pages.

2. Re-run `cd src/ui/frontend && npx tsc -b --noEmit`.

---

## Stage 3: Component and page tests

**Done when:** `npm run test -- --run tests/component/frontend/components/test_CollapsiblePanel.test.tsx tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx tests/component/frontend/components/test_ArtifactEditor.test.tsx` passes (from repo root or the path your Vitest config expects — match **qa-astral** / existing frontend component test invocation).

1. In `tests/component/frontend/components/test_CollapsiblePanel.test.tsx`, add **`it("supports multiple controlled siblings all collapsed", …)`**: render two `CollapsiblePanel` rows with `expanded={false}` and shared-style handlers; assert neither body text is visible; clicking one chevron calls `onExpandedChange(true)` for that row only (mock handlers).

2. In `tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx`, add **`it("allows zero expanded phase sections on the list page", …)`** (timeout 20000): after load, if a phase section is expanded, click **Collapse section** on that phase’s chevron; assert the task table row text (e.g. `task_a`) is **not visible** (or `hidden` / not in document per Testing Library).

3. In the same file, add **`it("allows zero expanded prompt panels in the edit modal", …)`** (timeout 20000): `localStorage.setItem("astral_admin_task_prompts_default_expanded", "user")`, mock API like existing tests, expand a phase, open `task_a`, wait for the default panel’s prompt value visible (e.g. `getByDisplayValue("user")`). With Stage 1 in place, only **one** panel is expanded at a time: click **Collapse section** **once** on that expanded panel (scope queries to the edit `Modal` dialog). Assert **`queryByDisplayValue("user")`**, **`queryByDisplayValue("cache")`**, **`queryByDisplayValue("nocache")`**, and the system prompt display value are all **not visible** (or absent). **Do not** click every chevron named “Collapse section” in the modal — after the first collapse the other three show **Expand section**; clicking them would re-expand panels and flake the test.

4. Run **`tests/component/frontend/components/test_ArtifactEditor.test.tsx`** unchanged as a **criteria regression** gate (no edits to that file unless a test fails — then stop and comment on Linear; do not “fix” criteria to match broken admin behavior).

---

## Stage 4: Smoke verification

**Done when:** Manual or agent smoke confirms acceptance criteria on a running dev UI.

1. **Admin → Manage Tasks:** collapse every phase section on the list (zero open). Re-expand one phase, open a task edit modal, collapse all four prompt panels. Confirm modal footer (default panel, Preview, Save) still usable; Save still persists (optional quick save).

2. **Any artifact criteria page** using `ArtifactEditor` (e.g. base resume content): expand a criterion, collapse it, confirm you can leave **all** criteria collapsed and the **+ Add** control remains reachable (existing AST-308 behavior — regression only).

---

## Execution contract (for the developer agent)

The plan is binding. The agent:

- Executes steps in order within a stage, and stages in order across the plan.
- Does not skip, reorder, combine, or expand steps (except Stage 2 may be skipped only per Stage 2 step 1 when no CSS defect is observed).
- Does not add files, modules, configs, or dependencies that aren't in the plan.
- When a step is ambiguous, contradicts another step, references something that doesn't exist, or fails when executed literally — **stops, comments on AST-427, and waits.** No fix-on-the-fly.
- When the codebase has drifted from what the plan assumes — **stops and comments.** Does not adapt silently.
- Completes a stage, performs the stage completion ritual (commit + Linear comment), and proceeds to the next stage only after the commit lands on **`origin/sub/AST-426/AST-427-collapsible-sections-on-manage-tasks-modal`** per **build-astral**.

Linear comment format for a block:

```
🛑 Stage N blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

---

## Self-Assessment

**Scope — `scope-Single-Component`**  
Touches one admin page’s controlled-collapse handlers, optional CSS for the shared panel class, and frontend Vitest only — no API or core layers.

**Conf — `conf-Medium`**  
Root cause is identified in `AdminTaskPrompts` edit-modal handlers; Stage 2 CSS is conditional on observed layout, which needs a quick visual check if tests do not catch spacing.

**Risk — `risk-Medium`**  
Wrong collapse logic only affects admin prompt editing UX; criteria path is regression-tested separately, but a mistaken shared CSS rule could affect every `CollapsiblePanel` stack.

---

## Self-review against ASTRAL_CODE_RULES

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Reuses existing `ArtifactEditor` collapse pattern instead of a new accordion abstraction. |
| §2.1 config | No config changes. |
| §2.4 batch | N/A. |
| §2.6 state machine | N/A. |
| §3.3 imports | No new cross-layer imports. |
| §3.5 naming | Stays in `src/ui/frontend` pages/components; tests under `tests/component/frontend/`. |

No conflicts requiring `conf-!!-NONE`.

---

## Revisions

```
Revision 1 — 2026-05-17
Driven by: Chuckles plan review on AST-427 (REVISE — fix-now Stage 3 step 3; discuss Stage 2 CSS scoping)
Changes:
- Stage 3 step 3: single Collapse click after default panel open; do not click all four chevrons
- Stage 2: scope CSS under edit-modal wrapper class, not global .collapsible-panel
- Execution contract: blockers comment on AST-427 (not parent AST-426)
```

---

## Review stub (build)

**Branch:** `sub/AST-426/AST-427-collapsible-sections-on-manage-tasks-modal`  
**Commits:** `cdd56c9c` (feat), `53eaf3c8` (test), `0853aae0` / tip `6ea62f07` (docs stub)

**Stage 2:** skipped — no CSS defect observed in Vitest; wrapper class `admin-task-prompts-edit-panels` added for future scoped CSS if needed.

## Radia review

**Reviewed:** `origin/dev`…`origin/sub/AST-426/AST-427-collapsible-sections-on-manage-tasks-modal` (no `origin/ftr/AST-427`; per ticket publish ref).

### What's solid

| Area | Notes |
|------|--------|
| Plan fidelity | `editOpenPanel` starts `null`; collapse clears selection (no auto-advance) on all four edit panels; list `openPhase` / `resolvedOpenPhase` allow zero expanded phases. |
| DRY | Matches `ArtifactEditor` controlled-collapse pattern; `CollapsiblePanel.tsx` unchanged per plan. |
| Tests | Vitest for zero-expanded list + edit modal; multi-sibling all-collapsed in `CollapsiblePanel`; bible §7.13h added. |
| Rubric | No layer violations, silent failure, logging, or config/state-machine scope in diff. |

### Issues

| Severity | Item |
|----------|------|
| **fix-now** | 0 |
| **discuss** | 1 — three-dot diff vs `origin/dev` may include **AST-363** system-prompt UI already on the sub branch; collapse behavior for AST-427 is correct either way. Confirm UAT merge order with parent **AST-426**. |
| **advisory** | Optional Stage 2 scoped CSS not in diff; acceptable if spacing looks fine in manual smoke. |

### Recommended actions

| Action | Owner |
|--------|------|
| Cherry-pick this doc commit onto `dev-kath` and re-publish to the sub branch if needed | Katherine |
| Resolve via `resolve-astral` only if discuss items need code changes | Katherine |

---

## Resolution (resolve-astral — 2026-05-17)

**Radia review:** `6736ae43` — **fix-now 0**, **discuss 1**, **advisory 1**.

| Item | Resolution |
|------|------------|
| **fix-now** | None — no product or test changes required. |
| **discuss** (AST-363 overlap in diff vs `origin/dev`) | Collapse behavior for AST-427 is correct on `sub/AST-426/AST-427-collapsible-sections-on-manage-tasks-modal`. Parent **AST-426** / **prep-uat** owns sibling merge order into the parent feature ref; no additional code on this child. |
| **advisory** (Stage 2 scoped CSS) | Declined — Vitest and Betty manifest green; `admin-task-prompts-edit-panels` wrapper retained if spacing regresses in UAT. |

**Re-verified:** Betty manifest (12/12 Vitest) on sub branch tip before resolve; `tsc -b --noEmit` clean.

**Publish ref:** `origin/sub/AST-426/AST-427-collapsible-sections-on-manage-tasks-modal` — ready for **prep-uat** under parent **AST-426**.
