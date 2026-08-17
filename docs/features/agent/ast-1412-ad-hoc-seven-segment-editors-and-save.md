# AST-1412 — Ad Hoc seven-segment editors and save

- **Linear:** [AST-1412](https://linear.app/astralcareermatch/issue/AST-1412)
- **Parent:** [AST-1403](https://linear.app/astralcareermatch/issue/AST-1403)
- **Publish ref:** `sub/AST-1403/AST-1412-ad-hoc-seven-segment-editors-and-save`

Agent Ad Hoc still authors three prompt slots (User / Cache / NoCache). Manage Tasks and `agent_task` already persist seven segments (System, Cache A–D, No Cache, User). This ticket makes the workbench editors, fetch-from-task, Save As, overwrite/has-content, and Preview/Test request bodies use those seven columns so a Cache-B-only task round-trips without sliding into Cache A, and so empty System is sent as `system_prompt: ""` (Preview/Test fall back to the selected agent via sibling #1; Save As leaves the column empty). Does **not** own preview-modal chrome or post-Test agent_data panes (sibling #3 / AST-1413). Does **not** own backend assemble/store (sibling #1 / AST-1411). Does **not** change Manage Tasks.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/api/api_admin.py` | Pass through the seven `*_len` fields `list_candidate_tasks` already computes so Save As overwrite/● can see Cache B–D and System | ui |
| `src/ui/frontend/src/pages/AdminAnthropicAdHoc.tsx` | Seven editors matching Manage Tasks labels/fields; fetch and Save As read/write all seven columns; Preview/Test POST always include all seven keys | ui |

Do **not** edit: `src/ui/frontend/src/pages/AdminTaskPrompts.tsx` (Manage Tasks), preview-modal / agent_data pane chrome (sibling #3), `src/core/agent.py` / `_resolve_adhoc` assemble-store (sibling #1), `PUT /api/admin/tasks/<task_key>` column handling (`save_agent_task` already accepts the seven kwargs; `system_prompt=""` writes empty), `src/utils/config.py`, `src/data/database.py`, `tests/`, bible. Do **not** extract a shared editor-label module (that would touch Manage Tasks or add an unplanned file).

## Stage 1: Seven editors, fetch, Save As, overwrite lens

**Done when:** Selecting a task whose GET `/api/admin/tasks/<task_key>` has distinct text in `system_prompt`, `cache_prompt`, `cache_prompt_b`, `cache_prompt_c`, `cache_prompt_d`, `nocache_prompt`, and `user_prompt` fills seven Ad Hoc tabs labeled exactly like Manage Tasks (System Prompt, Cache Block A–D, No Cache Block, User Prompt) with those strings in those slots. A task whose only cache content is `cache_prompt_b` loads into Cache Block B with Cache Block A empty. Save As PUT sends all seven keys (including `system_prompt: ""` when that editor is empty) and does **not** omit B–D. Save As is enabled when any of the seven editors has non-whitespace content. Overwrite confirm and the Save As ● mark fire when **any** of the seven list `*_len` values is `> 0`, including Cache-B-only (A empty). `python3 -m py_compile src/ui/api/api_admin.py` and `cd src/ui/frontend && npx tsc -b --noEmit` pass.

1. In `src/ui/api/api_admin.py`, in `_enrich_tasks`, the `rows.append({...})` dict currently drops the char-count columns that `database.list_candidate_tasks()` already selects (`user_prompt_len`, `cache_prompt_len`, `cache_prompt_b_len`, `cache_prompt_c_len`, `cache_prompt_d_len`, `nocache_prompt_len`, `system_prompt_len`). Add those seven keys onto the appended dict (same `int(... or 0)` pattern already used for `len_a` / `len_b` above in this function):

   ```python
               "user_prompt_len":       int(t.get("user_prompt_len") or 0),
               "cache_prompt_len":      int(t.get("cache_prompt_len") or 0),
               "cache_prompt_b_len":    int(t.get("cache_prompt_b_len") or 0),
               "cache_prompt_c_len":    int(t.get("cache_prompt_c_len") or 0),
               "cache_prompt_d_len":    int(t.get("cache_prompt_d_len") or 0),
               "nocache_prompt_len":    int(t.get("nocache_prompt_len") or 0),
               "system_prompt_len":     int(t.get("system_prompt_len") or 0),
   ```

   Place them immediately after `"updated_at": t.get("updated_at"),` and before `**_grouping_from_agent_task_row(t, task_key)`. Do **not** change token fields, grouping, or Manage Tasks columns. Extra JSON keys are unused by `AdminTaskPrompts.tsx`.

2. In `src/ui/frontend/src/pages/AdminAnthropicAdHoc.tsx`, replace the three-slot editor types/constants with Manage Tasks’ seven-segment edit keys and labels (same strings as `EDIT_PANEL_LABELS` / `VALID_EDIT_TAB_KEYS` in `AdminTaskPrompts.tsx`). Keep the existing inline **preview** tab type (`PreviewKey`) and `PREVIEW_TABS` unchanged (sibling #3 owns seven-tab preview chrome).

   Replace:

   ```ts
   type TabKey = "user" | "cache" | "nocache"
   ```

   and `const TABS: { key: TabKey; label: string }[] = [ ... User / Cache / NoCache ... ]`

   with:

   ```ts
   type TabKey = "system" | "cache" | "cache_b" | "cache_c" | "cache_d" | "nocache" | "user"

   const TABS: { key: TabKey; label: string }[] = [
     { key: "system",  label: "System Prompt" },
     { key: "cache",   label: "Cache Block A" },
     { key: "cache_b", label: "Cache Block B" },
     { key: "cache_c", label: "Cache Block C" },
     { key: "cache_d", label: "Cache Block D" },
     { key: "nocache", label: "No Cache Block" },
     { key: "user",    label: "User Prompt" },
   ]
   ```

   Tab order is System → Cache A–D → No Cache → User (same order as Manage Tasks accordion). Do **not** switch Ad Hoc from `TabBar` to `CollapsiblePanel`.

3. Extend `TaskSummary` with the seven lens (keep `task_key`):

   ```ts
   interface TaskSummary {
     task_key: string
     user_prompt_len?: number
     cache_prompt_len?: number
     cache_prompt_b_len?: number
     cache_prompt_c_len?: number
     cache_prompt_d_len?: number
     nocache_prompt_len?: number
     system_prompt_len?: number
   }
   ```

   Add a file-local helper (next to `byteSize`) used by Save As ● and overwrite:

   ```ts
   function taskHasExistingPrompts(t: TaskSummary): boolean {
     return (
       (t.system_prompt_len || 0) > 0 ||
       (t.user_prompt_len || 0) > 0 ||
       (t.cache_prompt_len || 0) > 0 ||
       (t.cache_prompt_b_len || 0) > 0 ||
       (t.cache_prompt_c_len || 0) > 0 ||
       (t.cache_prompt_d_len || 0) > 0 ||
       (t.nocache_prompt_len || 0) > 0
     )
   }
   ```

4. Keep `useLocalStorage` key `adhoc:cachePrompt` as **Cache A**. Add four more persisted editors (do **not** rename the existing three keys):

   ```ts
   const [systemPrompt, setSystemPrompt] = useLocalStorage<string>(`${LS}systemPrompt`, "")
   const [cachePromptB, setCachePromptB] = useLocalStorage<string>(`${LS}cachePromptB`, "")
   const [cachePromptC, setCachePromptC] = useLocalStorage<string>(`${LS}cachePromptC`, "")
   const [cachePromptD, setCachePromptD] = useLocalStorage<string>(`${LS}cachePromptD`, "")
   ```

   Keep `userPrompt` / `cachePrompt` / `nocachePrompt` / `activeTab` as they are (`activeTab` default remains `"user"`). Restored `"cache"` still means Cache A.

5. Add this helper inside the component (after the localStorage hooks, before `handlePreview`) so Save As / Preview / Test cannot drift field names. Request names are the Manage Tasks / `PUT /tasks/<task_key>` names — **not** `cache_a` on the request body (sibling #1 contract):

   ```ts
   function editorSegmentBody() {
     return {
       system_prompt: systemPrompt,
       user_prompt: userPrompt,
       cache_prompt: cachePrompt,
       cache_prompt_b: cachePromptB,
       cache_prompt_c: cachePromptC,
       cache_prompt_d: cachePromptD,
       nocache_prompt: nocachePrompt,
     }
   }
   ```

   Always include every key, including `""`. Omitting `system_prompt` is forbidden: sibling #1 treats a missing key as “use the DB task row,” and `save_agent_task(..., system_prompt=None)` means leave the column.

6. Replace `hasContent` with:

   ```ts
   const hasContent = [systemPrompt, userPrompt, cachePrompt, cachePromptB, cachePromptC, cachePromptD, nocachePrompt]
     .some(s => s.trim())
   ```

7. In the task-key `useEffect` fetch-confirm branch, replace `if (userPrompt || cachePrompt || nocachePrompt)` with the same seven strings (truthy, matching today’s three-slot confirm — whitespace counts as content for the replace banner).

8. In `doFetchFrom`, after `r.json()`, set all seven editors from the GET task row (`|| ""` when missing):

   ```ts
         setSystemPrompt(data.system_prompt || "")
         setUserPrompt(data.user_prompt || "")
         setCachePrompt(data.cache_prompt || "")
         setCachePromptB(data.cache_prompt_b || "")
         setCachePromptC(data.cache_prompt_c || "")
         setCachePromptD(data.cache_prompt_d || "")
         setNocachePrompt(data.nocache_prompt || "")
   ```

   Do **not** copy `cache_prompt_b` into `cachePrompt`. Do **not** fetch or write `run_next` / grouping / `agent_id` from this GET into the editors.

9. In `handleSaveAs`, replace the three-len `existing` check with `taskHasExistingPrompts(task)` (guard `task` the same way: `const task = tasks.find(...)`; `existing` is true only when `task` is found **and** `taskHasExistingPrompts(task)`). In the Save As dropdown row, replace the inline three-len `hasExisting` with `taskHasExistingPrompts(t)` (same ● suffix and gold color as today).

10. In `doSaveAs`, replace the PUT JSON body with:

    ```ts
      body: JSON.stringify({ agent_id: agentId || undefined, ...editorSegmentBody() }),
    ```

    Do **not** send `run_next`, `task_group_*`, or `task_name`. Empty System must be present as `system_prompt: ""` so PUT writes empty (`sp = body["system_prompt"]` when the key is in the body) and does **not** copy agent `content` into the row.

11. Replace the three-tab `TokenTextarea` switch with one textarea per `TABS` key. Placeholders and rows:

    | `activeTab` | placeholder | `rows` |
    |-------------|-------------|---------|
    | `system` | `Empty = use assigned agent content. {$SELECTED_AGENT} injects the agent system prompt at runtime.` | 16 |
    | `cache` | `Cache block A (ephemeral cached at API when non-empty).` | 22 |
    | `cache_b` | `Cache block B (optional).` | 22 |
    | `cache_c` | `Cache block C (optional).` | 22 |
    | `cache_d` | `Cache block D (optional).` | 22 |
    | `nocache` | `No-cache segment (dynamic context; not cached at API).` | 22 |
    | `user` | `User prompt content...` | 16 |

    Bind `value` / `onChange` to the matching state (`cache` → `cachePrompt` / `setCachePrompt`, `cache_b` → `cachePromptB` / `setCachePromptB`, …). Keep `className="dep-input"` and `tokens={tokenList}`.

12. Do **not** change Preview Prompt / ▶ Test button classes (`btn secondary` / `btn primary`), Save As (`btn secondary`), or confirm Yes/Cancel (`btn danger` / `btn secondary`). Do **not** restyle `.tabbed-ta-bar`. Do **not** edit the inline “Resolved Prompt Preview” block or the Test Response `<pre>` in this stage.

⚠️ **Decision:** Pass the existing `list_candidate_tasks` `*_len` columns through `_enrich_tasks` rather than GET-on-click for overwrite. The list query already has per-segment lengths; enrichment currently drops them, so today’s three-len check never sees Cache B–D (or System) on the real `/api/admin/tasks` payload. Spreading the seven ints onto the list JSON does not change Manage Tasks UI. Token fields (`system_prompt_tokens`) are the wrong signal — they include agent-content fallback and would false-positive overwrite on every tasked row.

⚠️ **Decision:** Keep Ad Hoc on `TabBar` (seven tabs) instead of copying Manage Tasks’ `CollapsiblePanel` accordion. Parent AC is segment parity (labels + columns), not chrome. Accordion would be an unplanned layout rewrite; sibling #3 already owns preview chrome.

⚠️ **Decision:** Duplicate Manage Tasks label strings in this page rather than a new shared module. Extracting labels would add a file or touch `AdminTaskPrompts.tsx` (out of scope). Editor tab keys are UI labels, not a `BLOCK_TYPES` / config enum (`BLOCK_TYPES` includes TASK / RESPONSE / FEEDBACK, which are not editors).

## Stage 2: Preview and Test send all seven fields

**Done when:** `POST /api/admin/adhoc/preview` and `POST /api/admin/adhoc/test` JSON bodies include `system_prompt`, `user_prompt`, `cache_prompt`, `cache_prompt_b`, `cache_prompt_c`, `cache_prompt_d`, and `nocache_prompt` on every call (empty string when that editor is empty). Cache B text is sent as `cache_prompt_b` only, not copied into `cache_prompt`. Empty System still sends `"system_prompt": ""` so sibling #1’s `"system_prompt" in body` path uses `resolved_task_system` (agent content) instead of the DB task row. The inline preview tabs and Test Response dump stay as they are (sibling #3). `cd src/ui/frontend && npx tsc -b --noEmit` passes.

1. In `handlePreview`, replace the three prompt fields in the `JSON.stringify({...})` object with a spread of `editorSegmentBody()` (keep `agent_id`, `task_key`, `entity_id`, `entity_ids`, `candidate_id` exactly as they are). Resulting prompt keys must be those seven names — do **not** send `cache_a`.

2. In `handleTest`, the same spread: replace `user_prompt` / `cache_prompt` / `nocache_prompt` with `...editorSegmentBody()`. Do **not** add `debug`. Do **not** read or display `batch_id` from the Test JSON (sibling #3 loads agent_data panes from that identity).

3. Leave `PREVIEW_TABS` as System / Cache / NoCache / User / Live Content. Sibling #1 keeps Preview JSON key `cache` as the Cache A alias, so today’s Cache preview tab still shows A. Do **not** add Cache B–D preview tabs here. Do **not** convert the inline preview into a modal. Do **not** replace the Test Response `<pre>` with agent_data panes.

4. Do **not** edit `tests/` or `docs/test-bible/**`. Existing Vitest cases that type “User prompt content...” and POST three prompt fields will need Betty’s manifest; if they fail because placeholders/body keys changed, `[qa-handoff]` — do not patch the test tree.

⚠️ **Decision:** Always send all seven keys (including `""`) rather than omitting empty ones. Sibling #1: omitted `system_prompt` means “use the DB task system until #2 lands”; empty string means production fallback to agent content at Preview/Test and empty column on Save As. Omitting `cache_prompt_b` on PUT would leave the column untouched (`None` = no write) and could not clear B.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric.v1
**Ticket:** AST-1412
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1403/AST-1412-ad-hoc-seven-segment-editors-and-save` @ `1bab7d00f97c398089dddec934bcaa84f6ff404f`

## Traceability

AC1→Stage 1 (seven editors, fetch/save all seven columns, seven-len overwrite ●); AC2→Stage 1 steps 8–10 (`cache_prompt_b` isolated, no slide into A); AC3→Stage 1 step 10 + Stage 2 (`system_prompt: ""` on Save/Preview/Test; sibling #1 resolves agent fallback).

## Findings

**acceptable** — Duplicated Manage Tasks label strings instead of a shared module; plan documents why (`AdminTaskPrompts.tsx` out of scope).

**acceptable** — `_enrich_tasks` additive `*_len` passthrough on shared `/api/admin/tasks`; backward-compatible, correct lens for Cache-B-only overwrite.

**acceptable** — Stage 2 Preview/Test contract depends on AST-1411 `"system_prompt" in body` behavior; ticket ordering “after #1” matches dispatch.

context_tokens≈48000
