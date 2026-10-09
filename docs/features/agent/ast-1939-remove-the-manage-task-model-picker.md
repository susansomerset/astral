<!-- linear-archive: AST-1939 archived 2026-10-08 -->

## Linear archive (AST-1939)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1939/remove-the-manage-task-model-picker-openrouter-support-models  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** ada  
**Priority / estimate:** None / 1  
**Parent:** AST-1937 — OpenRouter Support Models  
**Blocked by / blocks / related:** parent: AST-1937

### Description

## What this implements

Makes the agent row the only model source in the UI. The Manage Task modal drops the Model / Brain size selects that [AST-1909](https://linear.app/astralcareermatch/issue/AST-1909/manage-task-modal-no-model-dropdown-of-config-driven-model-keys) added, and saving a task no longer writes the agent. The list's read-only Model column stays. Runs in parallel with #1, and does **not** touch the catalog or compat client (#1).

## Citations

none. Frontend-only removal, and no active pattern or statute governs this page.

## Scope

* `src/ui/frontend/src/pages/AdminTaskPrompts.tsx`:
  * **Removed:** the model-catalog fetch, the agent model/brain load, the model-change handler, the Model and Brain size selects with their "Applies to agent" note, and the post-save agent `PUT`. Plus the related state, types, and helper that only those used.
  * **Unchanged:** the Agent select, the task save, and the list's read-only Model column.
* `tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx`: the modified AST-1909 modal-select cases are removed or replaced by an assertion that the modal has no Model / Brain size select and that save issues no agent `PUT`.
* `docs/test-bible/frontend/pages.md`: the modified Manage Task entries drop the AST-1909 model-select rows.

## Acceptance criteria

All `python -c` checks run from the repo root on the shipped tree.

9. **No task-level model picker.**
   * **Check:**
     * `rg -n "agents/models|editModelId|editBrainSetting|loadAgentModel|Brain size" src/ui/frontend/src/pages/AdminTaskPrompts.tsx` returns nothing.
     * A component test opens the Manage Task modal and finds no Model or Brain size select.
     * Saving the task issues only the task update, with no request to `/api/admin/agents/<id>`.
     * The task list still shows the read-only Model column.
   * **Fails if:** any grep hit, a select renders, an agent `PUT` goes out, or the Model column disappears.

## Boundaries

Does **not** touch `config.py` or `llm_compat.py` (sibling #1 — OpenRouter model shortlist in the catalog). Manage Agents is unchanged; the task list read-only Model column stays.

## Notes for planning

Citations: none. Reverses the AST-1909 modal selects (commit 9c7591ea9 on dev). Susan: the agent row is the one and only model source. Test/bible rows are Betty’s in qa-child.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-1937-openrouter-support-models`, child `sub/AST-1937/AST-1939-remove-task-model-picker`. Created at dispatch-parent.

### Comments

#### radia — 2026-10-02T18:16:14.106Z
[code-rubric] PROCEED (Commit: fb6a5e37e) Task picker removal clean

#### betty — 2026-10-02T18:13:38.658Z
`origin/sub/AST-1937/AST-1939-remove-task-model-picker` @ `fb6a5e37e` · picker tests retired, guards added

#### joan — 2026-10-02T18:06:03.694Z
[plan-rubric] PROCEED (Commit: 0afbf60cb) Task modal picker removal clean

#### ada — 2026-10-02T18:04:04.755Z
`origin/sub/AST-1937/AST-1939-remove-task-model-picker` @ `0afbf60cb` · plan: one-stage removal

---

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

## Review

- **Branch:** `origin/sub/AST-1937/AST-1939-remove-task-model-picker`
- **Build tip:** `28cb84c7e` (Stage 1: `AdminTaskPrompts.tsx` picker, catalog fetch, agent load, and agent `PUT` removed; 2 insertions, 100 deletions)
- **Build notes:** Built as planned, steps 1–11 in order, with no deviations. Both Compile / lint greps are empty, and `model_code`, `<th>Model</th>`, and the `row.model_code` cell are still present. `npm ci` was run in `src/ui/frontend`. `npm run build` passes. `npx eslint src/pages/AdminTaskPrompts.tsx` is clean. Repo-wide `npm run lint` reports the same 32 pre-existing problems (27 errors, 5 warnings) with and without this change, none of them in this file.
- **For qa-child:** see **Tests expected to move** above. All 7 tests in the AST-1909 describe should now fail (no labelled Model select, no agent fetch).

## Radia review

[code-rubric]
**Ticket:** AST-1939
**Publish ref:** `fb6a5e37e3039bd52f87ad2b1cab0c27f281732b` (`origin/sub/AST-1937/AST-1939-remove-task-model-picker`)
**Corpus:** `bd68954dc854ca80fca1fc391821dff9ff288a7a`
**Overall:** CLEAN

## Canon scores

Frozen list empty (Linear **Citations:** none; plan **Canon Scope:** none). No directive rows to score.

## Column diff vs plan stage

(aligned) — Joan recorded no canon rows; implementation matches Stage 1 steps 1–11 and ticket AC 9 on the product file.

## Frame diff

(none)

## Findings

### discuss

- **Severity:** discuss  
- **Location:** Manage Task modal UX (plan **Observations** / Joan discuss)  
- **Finding:** After AST-1939, the edit modal shows Agent → Run next with no model surfaced in the modal; `model_code` remains only on the list column (AST-1909 had already removed the read-only `Model:` header). Plan explicitly chose not to restore that header.  
- **@susan:** For UAT on AST-1937, is list-only model visibility on Manage Tasks acceptable, or should a follow-up ticket add a read-only model line in the modal?  
- **Default:** Treat as acceptable for this ticket; no `resolve-child` UI add unless Susan amends Scope.

### advisory

- **Severity:** advisory  
- **Location:** `tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx`, `docs/test-bible/frontend/pages.md`  
- **Finding:** Three-dot diff includes Betty/merge-tests work (AST-1909 describe retired → **AST-1939 no task-level model picker** with 3 tests; bible manifest updated). Expected on **Tests Passed**; not cross-ticket product scope.

### fix-now

(none)

## What's solid

- `AdminTaskPrompts.tsx` at tip: `useRef` and all catalog/agent-picker symbols removed; both AC greps are empty on the shipped file.  
- `handleSave` is task `PUT` only (no agent `PUT` chain). Agent `onChange` no longer calls `loadAgentModel`.  
- List **Model** column preserved (`model_code` type, `<th>Model</th>`, `row.model_code` cell).  
- Component tests assert no Model/Brain selects, no `/api/admin/agents/models` or per-agent row fetch in the modal flow, save PUT set is only the task URL, and column still shows `claude` for `task_a`.  
- Boundaries respected: no `config.py` / `llm_compat.py` / `AdminAgentPrompts.tsx` in diff.

## Recommended actions

- Chuckles: append this block to the issue doc, commit `docs(AST-1939): Radia review — clean`, push, post slim upshot `--as radia`, move **Review Posted**; datt **PROCEED** → **User Testing** path (no `resolve-child` unless Susan answers the discuss Default away from list-only).  
- UAT: exercise Manage Task save after changing Agent only; confirm model edits happen in Manage Agents, not the task modal.

context_tokens≈28000
