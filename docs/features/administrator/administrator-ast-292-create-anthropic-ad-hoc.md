# AST-292 — Create Anthropic Ad Hoc
**Component:** administrator  
**Children:** — (single ticket)  
**Linear archived:** not recorded (no Linear archive block in the source docs)  

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-03-04 11:03 | AST-292 | — | `1ee3c6102` | ast-292: Anthropic Ad Hoc prompt workbench |
| 2026-03-04 11:03 | AST-292 | — | `4cf97af2c` | ast-292: review stub for independent reviewer |
| 2026-03-04 11:07 | AST-292 | — | `e26b221fb` | ast-292: address review — outside-click dismiss, inline confirm for Fetch From, r.ok guard on test, useMemo for candidateName, asyncio.run constraint documented |
| 2026-03-04 11:12 | AST-292 | merge | `3211ac8e3` | Merge pull request #44 from susansomerset/chuckles/ast-292-create-anthropic-ad-hoc |
| 2026-03-04 11:26 | AST-292 | — | `0494de304` | ast-292: layout tweaks — buttons above textareas, candidate indicator top-aligned, token dropdown anchored to top of textarea |
| 2026-03-04 11:27 | AST-292 | merge | `37a0080aa` | Merge pull request #45 from susansomerset/chuckles/ast-292-create-anthropic-ad-hoc |

_Pre-`verb(AST-NNN)` era. Path convention was `ui/…`. Three source docs — issue brief + plan + review — merged here._

## Epic — AST-292
_Linear URL: https://linear.app/astralcareermatch/issue/AST-292/create-anthropic-ad-hoc · Project: Astral Administrator (per doc context) · Reviewer: Chuckles · (no Linear archive block in source — archived date / status / assignee / estimate not recorded)_

### Summary

Replace the "Script Sandbox" stub in the Admin nav with **Anthropic Ad Hoc** — a prompt development workbench that lets the administrator compose prompts, test them live against the Anthropic API using the astral internal key, and save results back to existing task definitions.

This page is intentionally **outside the normal orchestration pipeline**. It does not use `do_task`, does not require a `response_schema`, and does not go through the consult/candidate dispatch flow. It calls the Anthropic API layer directly. It may break any architectural rule in `ASTRAL_CODE_RULES.md` if needed to stay self-contained — the existing pipeline must not be retrofitted to accommodate this tool. _(Historical citation — `docs/ASTRAL_CODE_RULES.md` was later deleted in `44b7d102b`, 2026-09-10.)_

### Scope

#### Nav & Routing

- Rename "Script Sandbox" to "Anthropic Ad Hoc" in `NAV_CONFIG` and update the route path/component accordingly.
- Page lives under Admin, same position (bottom of Admin nav group).

#### Page Layout

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

#### Candidate Context

- The page needs a **candidate selector** (or uses the globally selected candidate if one is active) so that `resolve_tokens` has a `candidate_data` dict to work with during TEST.
- If no candidate is selected, tokens resolve to empty strings (existing `resolve_tokens` behavior).

#### Backend

- **Shared helper** `_resolve_adhoc(body)`: Loads agent record, resolves model params, loads candidate data if provided, resolves tokens in all prompt strings. Used by both endpoints below.
- **`POST /api/admin/adhoc/preview`** — accepts `{ agent_id, user_prompt, cache_prompt, nocache_prompt, candidate_id? }`.
  - Resolves tokens and returns `{ system, user, cache, nocache }` — the four prompt sections as they would be sent to Anthropic.
  - No API call is made.
- **`POST /api/admin/adhoc/test`** — same request body as preview.
  - Calls `_fetch_response_from_content` directly with the astral API key (no `api_key_override`).
  - Returns `{ success, response_text, timesheet?, error? }`.
  - Response text is the raw text from the first content block — no JSON parsing, no schema validation, no grade checking. The frontend handles display formatting.
- These endpoints are self-contained. They import what they need from `anthropic.py` and `config.py` directly. The private `_fetch_response_from_content` function is imported directly — do not refactor the existing pipeline.

#### What This Is NOT

- Not a prompt version control system.
- Not a batch runner.
- Not part of the candidate dispatch flow.
- Not a replacement for Manage Tasks (which handles task-agent assignment, preview, and prompt storage). This is the **authoring workbench** where prompts are developed and tested before being saved to tasks.

### Acceptance Criteria

1. "Script Sandbox" nav item is renamed to "Anthropic Ad Hoc".
2. Page renders with agent selector, three prompt tabs with token autocomplete, and FETCH FROM/PREVIEW PROMPT/TEST/SAVE AS buttons.
3. PREVIEW PROMPT resolves tokens and displays all four prompt sections (system, user, cache, nocache) in a tabbed view.
4. TEST calls the Anthropic API via the astral internal key with the selected agent's model params and displays the response.
5. Response area handles both JSON and plain text without crashing.
6. FETCH FROM loads an existing task's prompts into the editor with an overwrite warning if content is present.
7. SAVE AS writes prompts to an existing task definition with an overwrite warning.
8. No changes to `do_task`, `_send_and_parse`, the consult pipeline, or any existing orchestration code.
9. Page uses the astral internal `ANTHROPIC_API_KEY`, never a candidate key.

### Notes

- The SAVE AS flow intentionally does not save the agent assignment. The administrator sets agent-to-task bindings in Manage Tasks. This tool is purely for prompt content development.
- Timesheet logging from the test call is optional but acceptable — the existing `_send_and_parse` logs timesheets automatically, and there's no reason to suppress that. The session_id can be something like `"adhoc"` to distinguish these calls in the timesheet table.
- This page is expected to evolve. Future iterations may add: prompt version history, A/B comparison, batch testing across candidates, response grading. None of that is in scope for this issue.

### Plan

#### Overview

Replace the "Script Sandbox" stub with a fully functional prompt development workbench. This page bypasses the `do_task` orchestration entirely — it calls the Anthropic API directly via a self-contained backend endpoint.

#### Step 1 — Backend endpoints

**New file:** `src/ui/api/admin_adhoc.py`. Blueprint: `admin_adhoc_bp` at `/api/admin/adhoc`. Both endpoints accept the same JSON body:

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

**`POST /test`** — calls `_resolve_adhoc`, then calls `_fetch_response_from_content` directly (import the private function — this page breaks rules by design). Returns `{ success, response_text, timesheet, error }`. No response_schema validation. No grade checking. No agent_response logging beyond the automatic timesheet entry that `_send_and_parse` already does (session_id = `"adhoc"`).

Register blueprint in `src/ui/server.py`.

#### Step 2 — Nav & route update

**`config.py`:** Rename `"Script Sandbox"` → `"Anthropic Ad Hoc"`, update path to `/admin/anthropic_ad_hoc`.
**`routes.tsx`:** Replace the StubPage import/route with a new `AnthropicAdHoc` component at `admin/anthropic_ad_hoc`.

#### Step 3 — Frontend page

**New file:** `src/ui/frontend/src/pages/Admin/AnthropicAdHoc.tsx`

Layout (top to bottom):
1. **Header row:** Title + Agent dropdown (left), Candidate indicator from global `useCandidate()` context (right).
2. **TabBar:** User Prompt | Cache Prompt | NoCache Prompt — uses existing `TabBar` component.
3. **TokenTextarea:** One per tab, with token autocomplete from `/api/admin/tasks/meta/tokens`.
4. **Button row:** FETCH FROM | PREVIEW PROMPT | TEST | SAVE AS
5. **Preview area:** Tabbed view (System / User / Cache / NoCache) showing resolved prompt content with tokens replaced.
6. **Response area:** Read-only `<pre>` block. Attempts JSON pretty-print; falls back to plain text.

**FETCH FROM flow:** click opens a dropdown of task keys (from `/api/admin/tasks`); select → `GET /api/admin/tasks/:task_key` → populate all three prompt tabs; if any tab already has content, confirm before overwriting.

**PREVIEW PROMPT flow:** validates agent selected; `POST /api/admin/adhoc/preview` with agent_id, three prompts, `selectedId` as candidate_id; displays all four resolved prompt sections in a tabbed `<pre>` view.

**TEST flow:** validates agent selected; `POST /api/admin/adhoc/test` with agent_id, three prompts, `selectedId` as candidate_id; on success display `response_text` in the response area with timesheet stats; on error display error message.

**SAVE AS flow:** click opens a dropdown of task keys; select → check if the task has existing prompt content; if yes show inline confirmation warning; on confirm `PUT /api/admin/tasks/:task_key` with the three prompt fields (no agent_id).

**State management:** all local state — no new context needed. Uses `useCandidate()` for the globally selected candidate.

#### Step 4 — Cleanup

Remove `StubPage` import from routes.tsx if no other route uses it.

#### Files touched / NOT touched (plan)

Touched: `src/ui/api/admin_adhoc.py` (new — adhoc preview + test endpoints); `src/ui/server.py` (register `admin_adhoc_bp`); `src/utils/config.py` (rename nav item + path); `src/ui/frontend/src/routes.tsx` (replace StubPage route with AnthropicAdHoc); `src/ui/frontend/src/pages/Admin/AnthropicAdHoc.tsx` (new — full page component).

NOT touched: `src/external/anthropic.py` (no changes to `do_task`, `_send_and_parse`, or any orchestration function); `src/core/` (no changes to consult, candidate, or roster pipelines); `src/data/database.py` (no schema changes).

#### Design decisions

1. **Import `_fetch_response_from_content` directly** — it's underscore-prefixed, but the issue spec says this page can break rules. Duplicating 50 lines of prompt assembly would be worse than a direct import.
2. **Use global candidate selector** — the nav shell already has a candidate dropdown via `useCandidate()`. No need for a second selector on the page; just read `selectedId` from context and show the candidate name for confirmation.
3. **No agent_id in SAVE AS** — the task's agent binding is managed in Manage Tasks. SAVE AS only writes prompt content.
4. **Timesheet logging is automatic** — `_send_and_parse` always logs a timesheet entry. Context/session_id will be `"adhoc"` so these are distinguishable from real task runs.
5. **No prompt persistence on the page** — closing the page loses unsaved prompts. This is a workbench, not an editor. If you want to keep prompts, use SAVE AS. Future iterations could add localStorage draft persistence.
6. **Shared `_resolve_adhoc` helper** — both `/preview` and `/test` need the same agent lookup + token resolution. Extracting this avoids duplicated logic and ensures preview shows exactly what test will send.

### Code review — Chuckles (commit `1ee3c61`)

**Overall Assessment: Ship it.** Well-scoped, self-contained tool. The backend is minimal and correct; the frontend covers the full workflow without unnecessary abstraction. A few real issues to flag — one with actual correctness risk — but nothing blocking.

#### `admin_adhoc.py`

- **`_resolve_adhoc` is clean.** Agent lookup, model param resolution, token resolution — all correct. The fallback for temperature/max_tokens (`if agent.get("temperature") is not None`) mirrors the pattern in `anthropic.py do_task` exactly.
- **`asyncio.run()` inside a Flask route — real risk.** `result = asyncio.run(_fetch_response_from_content(...))` creates a new event loop and blocks the thread. Fine in dev with a single-threaded Flask server, but under an async worker (`uvicorn`, `hypercorn`, any ASGI adapter) it raises `RuntimeError: This event loop is already running`. The existing `admin_agents.py` / `admin_tasks.py` don't call async functions — this is the only endpoint that does. Low risk given current deployment, but a landmine.
- **`response_format="text"` is hardcoded.** Right default for a general-purpose workbench — no response schema; avoids the JSON parsing path in `_send_and_parse`. Correct.
- **`cache_content=resolved["cache"] or None`** — the `or None` means an empty string cache prompt is treated as "no cache". Correct.
- **No agent_response logging — by design.** Spec says skip it; `_fetch_response_from_content` still logs a timesheet row via `_send_and_parse` (acceptable side effect noted in the plan).

#### `AnthropicAdHoc.tsx`

- **`candidateName` is an IIFE inside the component body** — runs on every render. Not a perf issue at this scale, but `useMemo` with `[candidates, selectedId]` deps would be more idiomatic.
- **Dropdown menus are hand-rolled inline** — Fetch From / Save As use inline `<div>` dropdowns with `position: absolute` that don't dismiss on outside click. Minor annoyance for an admin-only tool; the existing `Modal` pattern would handle dismissal properly, but the inline dropdown is lighter and acceptable.
- **`window.confirm()` for FETCH FROM overwrite warning** — blocks the main thread. SAVE AS uses a custom inline confirmation block (`confirmTask` state) which is much nicer. The inconsistency should be unified to the in-page pattern.
- **`handleTest` doesn't check `r.ok` before parsing** — always calls `.json()` regardless of HTTP status, unlike `handlePreview` / `handleFetchFrom`. On a 500 with an HTML error page, `.json()` throws "Unexpected token < in JSON…" rather than anything useful. Low severity; backend is well-guarded, but the error UX could be cleaner.
- **Timesheet field names** (`timesheet.duration`, `inputtotal`, `outputtotal`, `inputcached`) need to match what `_send_and_parse` actually returns. If the real keys differ (e.g. `tokens_input` vs `inputtotal`), the stats strip would silently show nothing (not a crash — `&&` guards handle missing fields).
- **No "clear" / "reset" button** — once you've run a test, no way to clear the editor short of manually deleting text. Fine for v1.
- **The `hasContent` guard on Save As is correct** — `userPrompt.trim() || cachePrompt.trim() || nocachePrompt.trim()` disables Save As when all three prompts are empty.

#### `routes.tsx` / `config.py`

The Artifacts routes and nav entries here are from ast-291 (in the diff because this branch was cut after 291 landed on main). The only ast-292-specific changes are the `AnthropicAdHoc` import and route swap. Both are clean.

#### Summary of actionable items

| # | Severity | Location | Issue |
|---|----------|----------|-------|
| 1 | Medium | `admin_adhoc.py` | `asyncio.run()` inside Flask route will crash under any async WSGI/ASGI server — note as a known constraint |
| 2 | Low | `AnthropicAdHoc.tsx` | FETCH FROM uses `window.confirm` for overwrite; SAVE AS uses inline confirm block — should be unified |
| 3 | Low | `AnthropicAdHoc.tsx` | `handleTest` doesn't check `r.ok` before `.json()` — non-JSON error responses produce confusing error messages |
| 4 | Low | `AnthropicAdHoc.tsx` | Timesheet field names (`inputtotal`, `outputtotal`, etc.) should be verified against actual `add_timesheet_entry` keys |
| 5 | Note | `AnthropicAdHoc.tsx` | Dropdowns don't dismiss on outside-click — minor UX rough edge for an admin tool |
| 6 | Note | `AnthropicAdHoc.tsx` | `candidateName` IIFE on every render — consider `useMemo` |

Item 1 is the one to keep in the back of your mind for deployment. Items 2–3 are worth fixing before real use. Items 4–6 are polish.

#### Review follow-up (`e26b221fb`)

Addressed: outside-click dismiss on the dropdowns; inline confirm for Fetch From (replacing `window.confirm`); `r.ok` guard on the test call; `useMemo` for `candidateName`; `asyncio.run` constraint documented in `admin_adhoc.py`. Later layout tweaks (`0494de304`): buttons moved above the textareas, candidate indicator top-aligned, token dropdown anchored to the top of the textarea (`TokenTextarea.tsx`).

### Files changed (plan vs actual)

Era path convention `ui/…`. Plan "Files touched" → actual across `1ee3c6102` (feature), `e26b221fb` (review fixes), `0494de304` (layout tweaks).

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/ui/api/admin_adhoc.py` (new) | Step 1 — `admin_adhoc_bp` `/preview` + `/test`, `_resolve_adhoc`, direct `_fetch_response_from_content` import | `1ee3c6102` `e26b221fb` (`ui/api/admin_adhoc.py`) |
| ✓ | `src/ui/server.py` | Step 1 — register `admin_adhoc_bp` | `1ee3c6102` (`ui/server.py`) |
| ✓ | `src/utils/config.py` | Step 2 — rename nav item `Script Sandbox` → `Anthropic Ad Hoc`, update path | `1ee3c6102` |
| ✓ | `src/ui/frontend/src/routes.tsx` | Step 2 / Step 4 — replace `StubPage` route with `AnthropicAdHoc` | `1ee3c6102` (`ui/frontend/…`) |
| ✓ | `src/ui/frontend/src/pages/Admin/AnthropicAdHoc.tsx` (new) | Step 3 — full page component | `1ee3c6102` `e26b221fb` `0494de304` |
| + unplanned | `src/ui/frontend/src/components/TokenTextarea.tsx` | — | `0494de304` — token dropdown anchored to top of textarea |
| ⚠ not touched | `src/external/anthropic.py`, `src/core/**`, `src/data/database.py` | plan: explicitly NOT touched | — (held) |
| | _issue + plan docs_ | — | `ast-292-create-anthropic-ad-hoc{,-plan}.md` (`1ee3c6102`); `ast-292-create-anthropic-ad-hoc-review.md` (`4cf97af2c`) |

_Implementation detail may live in git history on `origin/dev`._
