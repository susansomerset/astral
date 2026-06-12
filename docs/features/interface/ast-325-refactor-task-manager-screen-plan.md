<!-- linear-archive: AST-325 archived 2026-06-03 -->

## Linear archive (AST-325)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-325/refactor-task-manager-screen  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** susan  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

—

### Comments

_No comments._

---

# Plan: AST-325 — Refactor Task Manager Screen

**Branch:** `interface`
**Commit slug:** `<agent>/ast-325-refactor-task-manager-screen`
**Depends on:** AST-324 (AGENT_CONFIG rename, cache_min_tokens, task versioning, new timesheets schema must be merged first)

---

## Goals

Redesign the Manage Tasks admin screen from a flat `ListPage` table to a grouped, collapsible section view that shows live token analysis and cache threshold status per task, resolved against the currently selected candidate.

---

## Step 1 — Core Layer: list_enriched_tasks()

**`src/core/consult.py`** — Add `list_enriched_tasks(candidate_id: str) -> list`:

Per SS 3.2/3.3, the enriched data must be assembled in core, not the API layer. This function:

1. Calls `database.list_agent_tasks()` for current task rows (current=1 only, post AST-324)
2. For each task, calls `database.get_agent(agent_id)` to get model_code and system prompt content
3. Gets candidate_data for the given candidate_id via `get_candidate(candidate_id)`
4. For each task, calls `resolve_tokens()` on each prompt field against candidate_data
5. Estimates token counts: `len(text) // CHARS_PER_TOKEN` (using `CHARS_PER_TOKEN` from config)
6. Detects unresolved tokens: checks if resolved output still contains `{$...}` patterns → sets `task_ready = False`
7. Looks up `cache_min_tokens` from `AGENT_CONFIG[model_code]`
8. Computes `cache_satisfied`: `system_prompt_tokens + parsed_cache_tokens >= cache_min_tokens`
9. Queries timesheet averages filtered by `task_key_uuid` (current version only):
   - `avg_live_tokens`: AVG(no_cache_live_tokens) WHERE task_key_uuid = ?
   - `avg_output_tokens`: AVG(total_output_tokens) WHERE task_key_uuid = ?
   - Returns `None` for tasks with no timesheet rows
10. Merges `phase` and `seq` from `TASK_CONFIG`

Returns a list of dicts, one per task, with all fields the frontend needs.

### Returned shape per task row

```python
{
    "task_key": str,
    "task_key_uuid": str,
    "agent_id": str,
    "phase": str,
    "seq": int,
    "model_code": str,
    "system_prompt_tokens": int,
    "base_cache_tokens": int,        # raw template (unresolved)
    "parsed_cache_tokens": int | None,  # None = TBD (unresolved tokens remain)
    "cache_min_tokens": int,
    "cache_satisfied": bool,
    "nocache_prompt_tokens": int,
    "avg_live_tokens": float | None,    # None = never run
    "avg_output_tokens": float | None,  # None = never run
    "task_ready": bool,
    "updated_at": str,
}
```

---

## Step 2 — API Layer: Update /api/admin/tasks

**`src/ui/api/api_admin.py`** — `list_tasks()`:

Replace current inline `_enrich_task()` enrichment with a call to `consult.list_enriched_tasks(candidate_id)`.

```python
@admin_bp.route("/tasks")
@require_auth
def list_tasks():
    candidate_id = request.args.get("candidate_id", "")
    return jsonify(consult.list_enriched_tasks(candidate_id))
```

The existing `_enrich_task()` helper is no longer needed and can be removed.

---

## Step 3 — Frontend: Rewrite AdminTaskPrompts.tsx

**`src/ui/frontend/src/pages/AdminTaskPrompts.tsx`**

### Interface

```typescript
interface AgentTask {
  task_key: string
  task_key_uuid: string
  agent_id: string
  phase: string
  seq: number | null
  model_code: string | null
  system_prompt_tokens: number
  base_cache_tokens: number
  parsed_cache_tokens: number | null   // null = TBD
  cache_min_tokens: number
  cache_satisfied: boolean
  nocache_prompt_tokens: number
  avg_live_tokens: number | null       // null = never run
  avg_output_tokens: number | null     // null = never run
  task_ready: boolean
  updated_at: string | null
}
```

### Section pattern (same as JobsInReview.tsx)

- Use `useCandidate()` for `selectedId`
- Fetch `/api/admin/tasks?candidate_id=<selectedId>` on mount and when `selectedId` changes
- Group tasks by `phase` using `useMemo`
- Sort sections alphabetically by phase string (A., B., C., D., E.)
- Within each section, sort rows by `seq`
- Collapsible sections with toggle (same chevron + count pattern as InReview)

### Columns per row

| Column | Notes |
|--------|-------|
| Seq | narrow, right-aligned |
| Task Key | red dot (●) prefix if `task_ready === false` |
| Agent | agent_id |
| Model | model_code |
| System Tokens | system_prompt_tokens |
| Base Cache | base_cache_tokens |
| Parsed Cache | parsed_cache_tokens ?? "TBD" |
| Cache Min | cache_min_tokens; green text when cache_satisfied, plain otherwise |
| NoCache | nocache_prompt_tokens |
| Avg Live | avg_live_tokens ?? "N/A" |
| Avg Output | avg_output_tokens ?? "N/A" |
| Version | updated_at formatted as date |

### Preserved behavior

- Row click still opens the existing edit modal (no changes to modal logic)
- Edit modal save still calls `PUT /api/admin/tasks/<task_key>` (unchanged)
- Preview button in modal still works (unchanged)
- Toast notifications unchanged

---

## Files Changed Summary

| File | Change |
|------|--------|
| `src/core/consult.py` | Add list_enriched_tasks() |
| `src/ui/api/api_admin.py` | Replace _enrich_task() with consult.list_enriched_tasks() call |
| `src/ui/frontend/src/pages/AdminTaskPrompts.tsx` | Full rewrite: sections, new columns, candidate context |
