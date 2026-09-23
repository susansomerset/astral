# AST-1780 — List enrich, AUTO/Run gates, force AUTO off

- **Linear:** https://linear.app/astralcareermatch/issue/AST-1780
- **Parent:** AST-1766 — Dispatch Validation
- **Publish ref:** `sub/AST-1766/AST-1780-list-enrich-auto-run-gates-force-auto-off`

Wire sibling #1’s `empty_render_for_prompts` into Scheduled Actions admin API: enrich `GET /api/admin/dispatch_tasks` with boolean `empty_render`, reject AUTO-on create/update and `POST …/run` with HTTP 400 when the flag would be true, and persist AUTO off when list enrichment finds a row already AUTO-on with empty-render. Does not own the helper (AST-1779), version-hook revalidation (AST-1781), or React disable wiring (AST-1782).

## Explicit scope gate

Ticket **## Scope** covers only:

- `src/ui/api/api_admin.py` — list enrichment boolean; create/update AUTO-on + `run_dtask` gates; force AUTO off when enrichment shows empty-render.

No other files. Do not edit `src/utils/config.py`, `src/data/database.py`, `src/core/candidate.py`, or `AdminScheduledActions.tsx`. Import and call `empty_render_for_prompts` from config (shipped by AST-1779); do not reimplement token scoring.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/api/api_admin.py` | Shared empty-render eval helpers; `list_dtasks` enrichment + force AUTO off; create/update AUTO-on + `run_dtask` 400 gates beside `_candidate_dispatch_api_key_error` | ui |

## Stage 1: Eval helpers + list enrichment + force AUTO off

**Done when:** `GET /api/admin/dispatch_tasks` returns every non-hidden row with an `empty_render` boolean. For a row whose current `agent_task` + agent system texts reference a candidate-scoped token that resolves to `""` for that row’s candidate, `empty_render` is `true`. If that row’s `auto_mode` was on, after the response the DB row has `auto_mode` off and the JSON row reflects `auto_mode` falsy. A row whose candidate-scoped tokens all resolve non-empty has `empty_render: false` even when prompts also mention job tokens (no `entity_contexts` passed). No create/update/run gate changes yet.

1. In `src/ui/api/api_admin.py`, extend the existing `from src.utils.config import (` block to also import `empty_render_for_prompts`. Extend the existing `from src.core.agent import (` block to also import `_resolve_task_prompts` (same private-helper import style as `_chain_context` / `_decode_payload` already used in this file).

2. Immediately above `_candidate_dispatch_api_key_error` (scheduler / per-task thread control section), add three private helpers:

   ```python
   def _dispatch_empty_render_prompt_texts(task_key: str) -> list[str]:
       """Raw prompt segments for empty-render gating (AST-1780 / AST-1779 order)."""
       ...

   def _evaluate_dispatch_empty_render(
       candidate_id: Optional[str], task_key: str
   ) -> dict:
       """Return empty_render_for_prompts result; never raises for soft misses."""
       ...

   def _candidate_dispatch_empty_render_error(
       candidate_id: Optional[str], task_key: str
   ) -> Optional[str]:
       """If set, return a user-facing message; AUTO/Run need non-empty candidate-scoped fills."""
       ...
   ```

3. Implement `_dispatch_empty_render_prompt_texts(task_key)` literally:

   - Call `agent_row, agent_task_row = _resolve_task_prompts(task_key)` (raises `ValueError` on missing agent_task / agent_id / agent — caller handles).
   - Build the text list in this order (AST-1779 caller contract):
     1. `agent_task_row.get("system_prompt") or ""`
     2. `cache_prompt`, `cache_prompt_b`, `cache_prompt_c`, `cache_prompt_d`
     3. `nocache_prompt`
     4. `user_prompt`
     5. Agent system text: **only when** `(agent_task_row.get("system_prompt") or "").strip()` is empty, append `agent_row.get("content") or ""`. When task `system_prompt` is non-empty, runtime uses it instead of agent `content` (`resolved_task_system`) — do **not** append unused agent `content` (avoids false `empty_render` from tokens that never wire).
   - Return that list (helper skips non-str / empty entries itself).

4. Implement `_evaluate_dispatch_empty_render(candidate_id, task_key)`:

   - If `(candidate_id or "").strip()` is empty → `logger.warning` with who/why (dispatch_task task_key + “no candidate_id; treating as empty_render”) and return `{"empty_render": True, "empty_tokens": []}`.
   - `cand = database.get_candidate(candidate_id)`; if missing → warning (candidate_id + task_key + “candidate not found; treating as empty_render”) and return `{"empty_render": True, "empty_tokens": []}`.
   - `cd = build_candidate_token_view(cand)`.
   - Try `_dispatch_empty_render_prompt_texts(task_key)`; on `ValueError` → warning (candidate_id, task_key, reason from `str(exc)`) and return `{"empty_render": True, "empty_tokens": []}`.
   - On any other `Exception` → `logger.exception` with candidate_id, task_key, facts + “Leaving empty_render true for this row”, then return `{"empty_render": True, "empty_tokens": []}`.
   - Otherwise call and return:

     ```python
     empty_render_for_prompts(texts, cd, (task_key or "").strip(), entity_contexts=None)
     ```

     Never pass a job (or other) `entity_contexts` map for this epic’s gates (AST-1779 / parent AC 9–10).

5. Implement `_candidate_dispatch_empty_render_error(candidate_id, task_key)`:

   - `result = _evaluate_dispatch_empty_render(candidate_id, task_key)`.
   - If `result.get("empty_render")` is falsy → return `None`.
   - Else return a single user-facing string. If `empty_tokens` is non-empty:

     ```text
     Prompt tokens resolve empty for this candidate (cannot Auto/Run): TOKEN1, TOKEN2
     ```

     If soft-miss left `empty_tokens` empty but `empty_render` true:

     ```text
     Cannot Auto/Run: prompts could not be validated for empty-render on this candidate/task.
     ```

6. In `list_dtasks`, inside the existing `for row in rows:` enrichment loop (after `available_count` / `always_visible_under_avail_gt0` are set, before the loop ends), add:

   - `er = _evaluate_dispatch_empty_render(row.get("candidate_id"), row.get("task_key") or "")`
   - `row["empty_render"] = bool(er.get("empty_render"))`
   - If `row["empty_render"]` and `row.get("auto_mode")` is truthy (SQLite may store `1` / `True`):
     - `update_dispatch_task(row["id"], auto_mode=0)` (already imported via dispatcher).
     - Set `row["auto_mode"] = 0` (or `False` — match whatever type other rows already expose from `list_dispatch_tasks`; prefer the same integer `0` the DB uses so the list payload stays consistent).
     - `logger.warning` per forced-off row: candidate_id, task_key, dispatch id, and why (`empty_render`; include `empty_tokens` when present) — product consequence: AUTO forced off.
   - Do **not** add `logger.info` for the GET list itself (`stat.logging.info.api`: idempotent GET that returns current state is not progress). Force-off is the soft per-item miss → warning only.

⚠️ **Decision:** Fail closed when evaluation cannot run (missing candidate / agent_task / agent / unexpected throw) — `empty_render: true` + warning (or exception log). Matches epic intent: do not leave AUTO/Run open when we cannot prove fills.

⚠️ **Decision:** Agent `content` is included in prompt texts only when task `system_prompt` is blank — matches runtime `resolved_task_system`, avoids false positives from unused agent-default tokens.

⚠️ **Decision:** List field name is exactly `empty_render` (frozen by AST-1779). Do not add a second boolean under another name. `empty_tokens` may appear only inside warning/error strings, not as a required list-row field (AC asks for the boolean).

## Stage 2: AUTO-on create/update + run_dtask 400 gates

**Done when:** `POST /api/admin/dispatch_tasks` and `PUT /api/admin/dispatch_tasks/<id>` with `auto_mode: true` on an empty-render row return HTTP 400 and do not persist AUTO on (create never inserts AUTO on; update leaves prior `auto_mode`). `POST …/run` on such a row returns HTTP 400 with `started: false` and does not call `run_task`. API-key gate still runs first (unchanged). Rows that pass empty-render still proceed subject to existing API-key / Sweep rules.

1. In `create_dtask`, immediately after the existing `_candidate_dispatch_api_key_error` block that runs when `bool(data.get("auto_mode", False))` (today ~lines 1118–1121), still inside that `if` (AUTO-on only):

   ```python
   err = _candidate_dispatch_empty_render_error(
       data.get("candidate_id"), task_key
   )
   if err:
       return jsonify({"error": err}), 400
   ```

   Use the already-normalized `task_key` variable from earlier in the handler. Do not evaluate empty-render when AUTO is off on create.

2. In `update_dtask`, immediately after the existing `_candidate_dispatch_api_key_error` block inside `if updates.get("auto_mode") == 1:` (today ~lines 1308–1312), still inside that `if`:

   ```python
   err = _candidate_dispatch_empty_render_error(
       cid, effective_task_key
   )
   if err:
       return jsonify({"error": err}), 400
   ```

   `cid` is already `row.get("candidate_id")`; `effective_task_key` is already computed earlier in the handler (covers task_key change in the same PUT). Do not gate when AUTO is being turned off or left unchanged.

3. In `run_dtask`, immediately after the existing `_candidate_dispatch_api_key_error` check (today ~lines 1942–1944), before `run_task(...)`:

   ```python
   err = _candidate_dispatch_empty_render_error(
       row.get("candidate_id"), row.get("task_key") or ""
   )
   if err:
       return jsonify({"error": err, "started": False}), 400
   ```

   Mirror the API-key response shape (`started: False` on 400).

4. Do **not** add route-level `logger.info` completion lines for these 400 paths (`stat.logging.info.api` is for successful completing work). Soft reject → no warning spam beyond what `_evaluate_dispatch_empty_render` already emitted if evaluation failed; a clean empty-render reject does not need an extra warning (the 400 body is the operator signal). Unexpected exceptions in create/update/run remain on existing handler paths / `stat.logging.error` if you wrap new code in try/except — prefer letting the helpers absorb soft misses so the route stays exception-light.

⚠️ **Decision:** Gate shape mirrors `_candidate_dispatch_api_key_error` exactly (Optional[str] → 400 JSON `error`) so sibling #4 / operators see one consistent AUTO/Run refusal class. Empty-render runs **after** the API-key check so a missing key still wins the first error message.

## Estimate

Confirm Chuckles estimate: 5 — agree

## Traceability

| AC | Stage |
|----|-------|
| 1 list boolean `empty_render` | Stage 1 |
| 2 PUT AUTO-on → 400 | Stage 2 |
| 3 POST run → 400 `started: false` | Stage 2 |
| 4 force AUTO off on enrichment | Stage 1 |
| 5 job tokens alone do not flip flag | Stage 1 (`entity_contexts=None`) |
| Parent create AUTO-on gate (same class as PUT) | Stage 2 |
| Sibling #3 revalidation hooks | out of scope (AST-1781) |
| Sibling #4 React disable | out of scope (AST-1782) |
