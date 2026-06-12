# AST-292: Create Anthropic Ad Hoc — Plan

**Branch:** `<agent>/ast-292-create-anthropic-ad-hoc`
**Issue:** `docs/astral/administrator/ast-292-create-anthropic-ad-hoc.md`

---

## Overview

Replace the "Script Sandbox" stub with a fully functional prompt development workbench. This page bypasses the `do_task` orchestration entirely — it calls the Anthropic API directly via a self-contained backend endpoint.

---

## Implementation Steps

### Step 1 — Backend endpoints

**New file:** `src/ui/api/admin_adhoc.py`

Blueprint: `admin_adhoc_bp` at `/api/admin/adhoc`

Both endpoints accept the same JSON body:
```json
{
  "agent_id": "string",
  "user_prompt": "string",
  "cache_prompt": "string",
  "nocache_prompt": "string",
  "candidate_id": "string (optional)"
}
```

**Shared helper `_resolve_adhoc(body)`:**
1. Load agent record via `database.get_agent(agent_id)` — get `content` (system prompt), `model_code`, `temperature`, `max_tokens`.
2. Resolve model defaults via `get_model(model_code)` for any null temperature/max_tokens.
3. If `candidate_id` provided, load candidate via `database.get_candidate(candidate_id)`, extract `candidate_data`, call `resolve_tokens` on all four prompt strings (system + user + cache + nocache).
4. Return resolved prompts + model params dict, or error tuple.

**`POST /preview`** — calls `_resolve_adhoc`, returns `{ system, user, cache, nocache }`. No API call.

**`POST /test`** — calls `_resolve_adhoc`, then calls `_fetch_response_from_content` directly (import the private function — this page breaks rules by design). Returns `{ success, response_text, timesheet, error }`.

No response_schema validation. No grade checking. No agent_response logging beyond the automatic timesheet entry that `_send_and_parse` already does (session_id = `"adhoc"`).

Register blueprint in `src/ui/server.py`.

### Step 2 — Nav & route update

**`config.py`:** Rename `"Script Sandbox"` → `"Anthropic Ad Hoc"`, update path to `/admin/anthropic_ad_hoc`.

**`routes.tsx`:** Replace the StubPage import/route with a new `AnthropicAdHoc` component at `admin/anthropic_ad_hoc`.

### Step 3 — Frontend page

**New file:** `src/ui/frontend/src/pages/Admin/AnthropicAdHoc.tsx`

Layout (top to bottom):
1. **Header row:** Title + Agent dropdown (left), Candidate indicator from global `useCandidate()` context (right).
2. **TabBar:** User Prompt | Cache Prompt | NoCache Prompt — uses existing `TabBar` component.
3. **TokenTextarea:** One per tab, with token autocomplete from `/api/admin/tasks/meta/tokens`.
4. **Button row:** FETCH FROM | PREVIEW PROMPT | TEST | SAVE AS
5. **Preview area:** Tabbed view (System / User / Cache / NoCache) showing resolved prompt content with tokens replaced.
6. **Response area:** Read-only `<pre>` block. Attempts JSON pretty-print; falls back to plain text.

**FETCH FROM flow:**
- Click opens a dropdown of task keys (fetched from `/api/admin/tasks`).
- Select a task → `GET /api/admin/tasks/:task_key` → populate all three prompt tabs.
- If any tab already has content, confirm before overwriting.

**PREVIEW PROMPT flow:**
- Validates agent is selected.
- `POST /api/admin/adhoc/preview` with agent_id, three prompts, and `selectedId` as candidate_id.
- Displays all four resolved prompt sections in a tabbed `<pre>` view.

**TEST flow:**
- Validates agent is selected.
- `POST /api/admin/adhoc/test` with agent_id, three prompts, and `selectedId` as candidate_id.
- On success, display `response_text` in the response area with timesheet stats.
- On error, display error message.

**SAVE AS flow:**
- Click opens a dropdown of task keys.
- Select a task → check if the task has existing prompt content.
- If yes, show inline confirmation warning.
- On confirm, `PUT /api/admin/tasks/:task_key` with the three prompt fields (no agent_id — agent assignment stays as-is).

**State management:** All local state — no new context needed. Uses `useCandidate()` for the globally selected candidate.

### Step 4 — Cleanup

Remove `StubPage` import from routes.tsx if no other route uses it.

---

## Files touched

| File | Change |
|------|--------|
| `src/ui/api/admin_adhoc.py` | **New** — adhoc preview + test endpoints |
| `src/ui/server.py` | Register `admin_adhoc_bp` |
| `src/utils/config.py` | Rename nav item + path |
| `src/ui/frontend/src/routes.tsx` | Replace StubPage route with AnthropicAdHoc |
| `src/ui/frontend/src/pages/Admin/AnthropicAdHoc.tsx` | **New** — full page component |

## Files NOT touched

- `src/external/anthropic.py` — no changes to `do_task`, `_send_and_parse`, or any orchestration function.
- `src/core/` — no changes to consult, candidate, or roster pipelines.
- `src/data/database.py` — no schema changes.

---

## Design decisions

1. **Import `_fetch_response_from_content` directly** — it's underscore-prefixed, but the issue spec says this page can break rules. Duplicating 50 lines of prompt assembly would be worse than a direct import.

2. **Use global candidate selector** — the nav shell already has a candidate dropdown via `useCandidate()`. No need for a second selector on the page; just read `selectedId` from context and show the candidate name for confirmation.

3. **No agent_id in SAVE AS** — the task's agent binding is managed in Manage Tasks. SAVE AS only writes prompt content.

4. **Timesheet logging is automatic** — `_send_and_parse` always logs a timesheet entry. Context/session_id will be `"adhoc"` so these are distinguishable from real task runs.

5. **No prompt persistence on the page** — closing the page loses unsaved prompts. This is a workbench, not an editor. If you want to keep prompts, use SAVE AS. Future iterations could add localStorage draft persistence.

6. **Shared `_resolve_adhoc` helper** — both `/preview` and `/test` need the same agent lookup + token resolution. Extracting this avoids duplicated logic and ensures preview shows exactly what test will send.
