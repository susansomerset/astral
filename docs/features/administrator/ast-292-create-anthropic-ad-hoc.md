# AST-292: Create Anthropic Ad Hoc

## Summary

Replace the "Script Sandbox" stub in the Admin nav with **Anthropic Ad Hoc** — a prompt development workbench that lets the administrator compose prompts, test them live against the Anthropic API using the astral internal key, and save results back to existing task definitions.

This page is intentionally **outside the normal orchestration pipeline**. It does not use `do_task`, does not require a `response_schema`, and does not go through the consult/candidate dispatch flow. It calls the Anthropic API layer directly. It may break any architectural rule in `ASTRAL_CODE_RULES.md` if needed to stay self-contained — the existing pipeline must not be retrofitted to accommodate this tool.

---

## Scope

### Nav & Routing

- Rename "Script Sandbox" to "Anthropic Ad Hoc" in `NAV_CONFIG` and update the route path/component accordingly.
- Page lives under Admin, same position (bottom of Admin nav group).

### Page Layout

The page layout mirrors the Manage Tasks edit modal, but as a full page rather than a modal:

1. **Agent Selector** — dropdown of all configured agents (from `/api/admin/agents/ids`). Selecting an agent loads its system prompt (`agent.content`) and model parameters (`model_code`, `temperature`, `max_tokens`).

2. **Three prompt tabs** (using the existing `TabBar` component):
   - **User Prompt** — `TokenTextarea` with token autocomplete
   - **Cache Prompt** — `TokenTextarea` with token autocomplete
   - **NoCache Prompt** — `TokenTextarea` with token autocomplete

3. **PREVIEW PROMPT button** — Resolves tokens and displays the full prompt content without calling Anthropic:
   - Calls `POST /api/admin/adhoc/preview` with the agent_id, three prompts, and selected candidate_id.
   - Returns and displays all four resolved prompt sections (System Prompt, User Prompt, Cache Prompt, NoCache Prompt) in a tabbed view.
   - All `{$TOKEN}` patterns are replaced with the selected candidate's actual data.
   - Use case: inspect exactly what will be sent to Anthropic before pulling the trigger.

4. **TEST button** — Executes the prompt:
   - Resolves `{$TOKEN}` patterns in all three prompts using `resolve_tokens` against the selected candidate's `candidate_data`.
   - Calls the Anthropic API directly (via a new backend endpoint) using the **astral internal API key** (`ANTHROPIC_API_KEY` from env), the selected agent's model parameters, and the composed prompt content.
   - Does **not** go through `do_task`. Calls `_fetch_response_from_content` (or an equivalent purpose-built function) directly, bypassing task_key lookup, response_schema validation, grade validation, and agent_response logging.
   - Displays the response in a large read-only text area below the prompt tabs.

5. **Response display area**:
   - Attempts to parse the response as JSON and displays it pretty-printed (`JSON.stringify(parsed, null, 2)`).
   - If the response is not valid JSON, displays it as plain text. No crash on natural language responses.
   - Scrollable, monospace, themed to match the existing preview modal style.

6. **FETCH FROM button** — Loads prompt content from an existing task definition into the editor:
   - Opens a dropdown/selector listing all task keys from `TASK_CONFIG`.
   - On select, fetches the full task record via `GET /api/admin/tasks/:task_key` and populates the three prompt tabs with that task's `user_prompt`, `cache_prompt`, and `nocache_prompt`.
   - If the editor already has content in any tab, display a warning: "This will replace your current prompt content. Continue?"
   - Does **not** change the agent selector — the loaded prompts may be intended for a different agent than the source task uses.
   - Use case: pull in an existing task's prompts as a starting point, tweak them, test, then SAVE AS to the same task (update) or a different task (duplicate).

7. **SAVE AS button** — Saves the current prompt content to an existing task definition:
   - Opens a dropdown/selector listing all task keys from `TASK_CONFIG`.
   - If the selected task already has prompt content (any of user/cache/nocache is non-empty), display a warning: "This will overwrite existing prompt content for [task_key]. Continue?"
   - On confirm, writes the three prompt fields to the `agent_task` row for that task key via the existing `PUT /api/admin/tasks/:task_key` endpoint.
   - Does **not** save the agent selection — the task's agent assignment is managed separately via Manage Tasks.

### Candidate Context

- The page needs a **candidate selector** (or uses the globally selected candidate if one is active) so that `resolve_tokens` has a `candidate_data` dict to work with during TEST.
- If no candidate is selected, tokens resolve to empty strings (existing `resolve_tokens` behavior).

### Backend

- **Shared helper** `_resolve_adhoc(body)`: Loads agent record, resolves model params, loads candidate data if provided, resolves tokens in all prompt strings. Used by both endpoints below.
- **`POST /api/admin/adhoc/preview`** — accepts `{ agent_id, user_prompt, cache_prompt, nocache_prompt, candidate_id? }`.
  - Resolves tokens and returns `{ system, user, cache, nocache }` — the four prompt sections as they would be sent to Anthropic.
  - No API call is made.
- **`POST /api/admin/adhoc/test`** — same request body as preview.
  - Calls `_fetch_response_from_content` directly with the astral API key (no `api_key_override`).
  - Returns `{ success, response_text, timesheet?, error? }`.
  - Response text is the raw text from the first content block — no JSON parsing, no schema validation, no grade checking. The frontend handles display formatting.
- These endpoints are self-contained. They import what they need from `anthropic.py` and `config.py` directly. The private `_fetch_response_from_content` function is imported directly — do not refactor the existing pipeline.

### What This Is NOT

- Not a prompt version control system.
- Not a batch runner.
- Not part of the candidate dispatch flow.
- Not a replacement for Manage Tasks (which handles task-agent assignment, preview, and prompt storage). This is the **authoring workbench** where prompts are developed and tested before being saved to tasks.

---

## Acceptance Criteria

1. "Script Sandbox" nav item is renamed to "Anthropic Ad Hoc".
2. Page renders with agent selector, three prompt tabs with token autocomplete, and FETCH FROM/PREVIEW PROMPT/TEST/SAVE AS buttons.
3. PREVIEW PROMPT resolves tokens and displays all four prompt sections (system, user, cache, nocache) in a tabbed view.
4. TEST calls the Anthropic API via the astral internal key with the selected agent's model params and displays the response.
5. Response area handles both JSON and plain text without crashing.
6. FETCH FROM loads an existing task's prompts into the editor with an overwrite warning if content is present.
7. SAVE AS writes prompts to an existing task definition with an overwrite warning.
8. No changes to `do_task`, `_send_and_parse`, the consult pipeline, or any existing orchestration code.
9. Page uses the astral internal `ANTHROPIC_API_KEY`, never a candidate key.

---

## Notes

- The SAVE AS flow intentionally does not save the agent assignment. The administrator sets agent-to-task bindings in Manage Tasks. This tool is purely for prompt content development.
- Timesheet logging from the test call is optional but acceptable — the existing `_send_and_parse` logs timesheets automatically, and there's no reason to suppress that. The session_id can be something like `"adhoc"` to distinguish these calls in the timesheet table.
- This page is expected to evolve. Future iterations may add: prompt version history, A/B comparison, batch testing across candidates, response grading. None of that is in scope for this issue.
