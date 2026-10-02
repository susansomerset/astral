# AST-1939 — Remove the Manage Task model picker

- **Parent:** [AST-1937 — OpenRouter Support Models](https://linear.app/astralcareermatch/issue/AST-1937)
- **Ticket:** [AST-1939](https://linear.app/astralcareermatch/issue/AST-1939)
- **Publish ref:** `origin/sub/AST-1937/AST-1939-remove-task-model-picker`
- **Canon Scope:** none. Frontend-only removal; no active pattern or statute governs this page (ticket § Citations).

Susan confirmed that the agent row is the one and only model source. [AST-1909](https://linear.app/astralcareermatch/issue/AST-1909) (commit `9c7591ea9` on `dev`) added Model and Brain size selects to the Manage Task modal. Those selects read the model catalog and the task's agent row, and on save they sent a second `PUT /api/admin/agents/<id>`. This ticket removes all of that from `AdminTaskPrompts.tsx`. After it lands, model and brain size are edited only in Manage Agents. The Agent select, the task `PUT`, and the list's read-only **Model** column (`row.model_code`) are untouched. Sibling [AST-1938](https://linear.app/astralcareermatch/issue/AST-1938) (catalog + compat client) is independent; this ticket does not touch `config.py` or `llm_compat.py`.

## Scope gate

Every row in **Files Changed** is named in this ticket's `## Scope`:

- `src/ui/frontend/src/pages/AdminTaskPrompts.tsx`: the Scope's **Removed** list (catalog fetch, agent model/brain load, model-change handler, the two selects + "Applies to agent" note, the post-save agent `PUT`, and the state/types/helper only those used). The **Unchanged** list (Agent select, task save, list Model column) is preserved.
- `tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx` and `docs/test-bible/frontend/pages.md`: in Scope, but they belong to **Betty** in qa-child. Engineers may not touch `tests/` or `docs/test-bible/**` (pre-commit hook).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminTaskPrompts.tsx` | Remove the AST-1909 model/brain picker code: `useRef` import, `BrainSizeRow` / `ModelRow` / `ModelCatalog` types, `byOrder` helper, the four model state hooks + `agentModelReq` ref, the catalog `useEffect`, `loadAgentModel`, `handleModelChange`, both `loadAgentModel` call sites, the agent-`PUT` `.then` in `handleSave`, and the Model / Brain size JSX block. | ui |

No other file is touched. No `tests/`, bible, backend, or `AdminAgentPrompts.tsx` edits.

## Stage 1: Remove the task-level model picker

**Done when:** The Manage Task modal shows Agent → Run next with no Model or Brain size select, saving a task sends only `PUT /api/admin/tasks/<key>`, the list still shows the Model column, and the AC 9 grep returns nothing.

Line numbers refer to `AdminTaskPrompts.tsx` at `0989ba69f` (the synced tip). If a quoted line doesn't match, stop and comment (Execution contract).

1. **Import (line 1).** Change `import { useCallback, useEffect, useMemo, useRef, useState } from "react"` to `import { useCallback, useEffect, useMemo, useState } from "react"`. `useRef` has no other use in the file (only `agentModelReq`, removed in step 4).
2. **Catalog types (lines 45–59).** Delete the whole block from the doc comment `/** \`GET /api/admin/agents/models\` — keyed by model id …` through `type ModelCatalog = Record<string, ModelRow>`. That covers `BrainSizeRow`, `ModelRow`, and `ModelCatalog`.
3. **`byOrder` helper (lines 61–64).** Delete the `/** Ids of a keyed catalog object in catalog order. */` comment and the `byOrder` function. Its only callers are `handleModelChange` and the two selects, all removed below.
4. **Model state (lines 202–209).** Delete the comment `// Model + brain size live on the task's agent row …` and everything through `const agentModelReq = useRef("")`. That covers `models`, `editModelId`, `editBrainSetting`, `loadedAgentModel`, `agentModelReq`, and their comments. Leave the blank line before `// Preview state`.
5. **Catalog fetch (lines 247–252).** Delete the `useEffect` that calls `api("/api/admin/agents/models")` and `setModels`. The `loadAll` `useEffect` just above it (lines 241–245) stays.
6. **`loadAgentModel` and `handleModelChange` (lines 254–277).** Delete both functions, including the `/** Keep the size when the new model offers it … */` comment.
7. **`openEdit` (line 365).** Delete the line `loadAgentModel(full.agent_id || "")`. `setEditAgentId(full.agent_id || "")` stays.
8. **`handleSave` (lines 410–421).** Delete the whole `.then(() => { // Task saved first; the agent PUT … })` block, which holds the `loadedAgentModel` comparison and the `api(\`/api/admin/agents/${…}\`, { method: "PUT", … })` call. The chain becomes: task `PUT` → `.then(r => { if (!r.ok) … ; return r.json() })` → `.then(() => { setEditOpen(false); … loadAll() })` → `.catch(...)`. Do not change the task `PUT` body or the success/error handling.
9. **Agent select `onChange` (line 553).** Change `onChange={e => { setEditAgentId(e.target.value); loadAgentModel(e.target.value) }}` to `onChange={e => setEditAgentId(e.target.value)}` (the pre-AST-1909 form).
10. **Model / Brain size JSX (lines 560–581).** Delete from the comment `{/* Options come only from the catalog response — no model/server literals here. */}` through the closing `</div>` of the Brain size `dep-field`, which includes the `Applies to agent …` hint. The Agent `dep-field` should be followed directly by the blank line and the `Run next` `dep-field`.
11. **Leave in place:** the `model_code` field on `AgentTask` (line 24), the `<th>Model</th>` header (line 486), and the `row.model_code` cell (line 506). Together these are the list's read-only Model column.

⚠️ **Decision:** Do **not** restore the read-only `Model: <model_code>` line that AST-1909 removed from the top of the modal. The ticket's Scope only lists removals, plus the list column as unchanged. Restoring the line would add UI the Scope doesn't name. It's listed under Observations for Chuckles instead.

## Compile / lint

- `cd src/ui/frontend && npm ci` (the worktree has no `node_modules` yet), then `npm run build` (`tsc -b && vite build`, with `noUnusedLocals` on, so any leftover removed symbol fails the build) and `npm run lint`.
- AC grep from the repo root: `rg -n "agents/models|editModelId|editBrainSetting|loadAgentModel|Brain size" src/ui/frontend/src/pages/AdminTaskPrompts.tsx` returns nothing.
- Also confirm nothing else is left over: `rg -n "useRef|byOrder|ModelCatalog|loadedAgentModel|agentModelReq|handleModelChange|setModels" src/ui/frontend/src/pages/AdminTaskPrompts.tsx` returns nothing.

## Acceptance mapping (this ticket)

AC 9 grep → steps 2, 4–6, 10 · no Model / Brain size select in the modal → step 10 (Betty's component test) · save sends no agent `PUT` → step 8 (Betty's component test) · list still shows the read-only Model column → step 11.

## Tests expected to move (Betty — qa-child; engineer does not edit `tests/`)

- `tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx`:
  - The `describe("AST-1909 task modal model + brain size")` block (7 tests, from line ~596) fails after this change. It should be retired or inverted: the modal has no Model / Brain size select, and Save issues no `/api/admin/agents/<id>` request.
  - The shared mock at lines ~15–49 (catalog fixture + `/api/admin/agents/models` and agent GET/PUT handlers) becomes unused.
  - A list-level check that the Model column still renders `model_code` covers the AC's last bullet.
- `docs/test-bible/frontend/pages.md`: the `### AST-1909 · AST-1851` section (line ~3155) and the `## QA test manifest (AST-1909)` (line ~3164).

## Observations (outside Scope — for Chuckles, not changed here)

- AST-1909 also removed the modal's read-only `Model: <model_code>` header line (`{editTask && (<div …><span><strong>Model:</strong> {editTask.model_code || "—"}</span></div>)}`). With the selects gone, the modal shows no model at all; the list column still does. If Susan wants that header line back, it needs a Scope line.

## Estimate

Confirm Chuckles estimate: 1 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-1939
**Overall:** APPROVED
**Corpus:** `bd68954dc854ca80fca1fc391821dff9ff288a7a` (tree `canon/` at publish tip; no `docs/canon-index.md` on ref)
**Publish ref:** `0afbf60cb7add117f4a2f5198128386e7cdeed57`

## Canon scores

(none on frozen list — ticket § Citations and plan § Canon Scope: none; R3 N/A)

## Traceability

9→S1 steps 1–11 (grep/no-select/no agent PUT/column preserved) + Betty `qa-child` for component assertions listed under **Tests expected to move** | parent FS item 6 (agent row only model source)→S1 | parent AC 1–8→N/A (AST-1938 catalog slice)

## Findings

### discuss

- **Severity:** discuss
- **Location:** **Observations** / AST-1909 regression
- **Finding:** After removal, the Manage Task modal shows no model at all (AST-1909 had already dropped the read-only `Model: <model_code>` header); only the list column still surfaces `model_code`. Plan explicitly defers restoring that header unless Scope is amended.
- **Recommendation:** No plan change for build — if Susan wants model visible in the modal again, add a Scope line in a follow-up or Plan Discuss; UAT should expect list-only visibility.

### acceptable

- **Severity:** acceptable
- **Location:** **Scope gate** vs ticket `## Scope`
- **Finding:** Ticket Scope names the component test file and `pages.md`; engineer **Files Changed** is only `AdminTaskPrompts.tsx` because pre-commit forbids `tests/` and bible edits — Betty owns the AST-1909 retire/invert pass in `qa-child`.
- **Recommendation:** None — matches epic partition and AST-1938 pattern.

- **Severity:** acceptable
- **Location:** **Boundaries** / sibling
- **Finding:** Plan and ticket repeat no `config.py` / `llm_compat.py`; no catalog or compat work.
- **Recommendation:** None.

- **Severity:** acceptable
- **Location:** Stage 1 **Execution contract**
- **Finding:** Line-numbered steps against a pinned file tip with “stop and comment if mismatch” reduces drift risk on a single-file deletion.
- **Recommendation:** None.

- **Severity:** acceptable
- **Location:** **Estimate**
- **Finding:** One-stage removal with build/lint + grep verification; estimate 1 confirmed.
- **Recommendation:** None.

context_tokens≈64000

[plan-rubric] PROCEED (Commit: 0afbf60cb) Task modal picker removal clean
