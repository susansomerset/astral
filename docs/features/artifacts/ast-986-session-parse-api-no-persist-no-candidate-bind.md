# Session parse API (no persist, no candidate bind) (Save resume pdf)

**Linear:** [AST-986](https://linear.app/astralcareermatch/issue/AST-986/session-parse-api-no-persist-no-candidate-bind-save-resume-pdf)
**Parent:** [AST-985](https://linear.app/astralcareermatch/issue/AST-985/save-resume-pdf) — Save resume pdf
**Publish ref:** `origin/sub/AST-985/AST-986-session-parse-api-no-persist-no-candidate-bind`

Admin convenience backend: accept pasted resume text, run the existing `craft_resume_base` parse-to-structure pipeline against the **default** resume-structure contract, and return structure-keyed JSON **without** reading or writing the selected candidate (or any job artifacts). Katherine’s sibling **AST-987** owns the Admin paste page, session retention, and HTML new-tab open — this ticket exposes the API contract she calls.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/candidate.py` | Add `run_session_resume_parse(resume_text, *, debug=False)` — synthetic default-structure ctx, `do_task("craft_resume_base")`, split payload, **never** `save_candidate` / `get_candidate` | core |
| `src/ui/api/api_admin.py` | Add `POST /api/admin/session_resume/parse` (`@require_admin`) — validate body, call core, return JSON contract | ui |

**Out of scope (do not touch):** React pages/nav, HTML builder routes, `run_candidate_artifact_generation` persist path, `parse_candidate_resume`, Manage Tasks prompts / `TASK_CONFIG["craft_resume_base"]` schema shape, job artifact paths, `tests/`, bible.

## API contract (for AST-987)

**`POST /api/admin/session_resume/parse`**
- Auth: `@require_admin` (same as other Admin tools).
- Request JSON: `{ "resume_text": "<pasted full resume text>" }` — required; after strip, must be non-empty.
- Success **200**:
  ```json
  {
    "success": true,
    "resume_structure": { "sections": { "...": { "id", "title", "enabled", "order", "job_agent_editable" } } },
    "base_resume": { "<section_id>": "<string content>", "...": "..." },
    "parsed_response": { "...": "full craft_resume_base agent JSON" },
    "batch_id": "<ledger batch id or null>",
    "timesheet": {}
  }
  ```
  - `resume_structure` / `base_resume` come from `split_craft_resume_base_payload(parsed)` — same shape Base Resume Content persists under `artifacts.*`, but **response-only**.
  - `base_resume` keys are enabled section ids from the resolved structure (default catalog when the model omits/invalidates structure).
- Client errors **400**: `{ "success": false, "error": "<clear message>" }` — e.g. missing/empty `resume_text`, non-object body.
- Server / agent failures **500**: `{ "success": false, "error": "<clear message>", "batch_id": "..." }` — never imply success; Katherine must not open an HTML tab on non-success.

**Detached rules (hard):**
- Do **not** read Flask/session candidate selector, `request` candidate id, or `database.get_candidate` for this flow.
- Do **not** call `database.save_candidate`, `_persist_craft_dispatch_success`, or job artifact writers.
- Synthetic `ctx` must **omit** `astral_candidate_id` so `do_task` does not overlay company_search_terms / candidate API key from a real row.

## Stage 1: Core session parse (no persist)

**Done when:** `run_session_resume_parse` accepts paste text, invokes `craft_resume_base` with default structure + synthetic ctx, returns `(body, status)` matching the success/error shapes above, and a grep of the function shows no `get_candidate` / `save_candidate`.

1. In `src/core/candidate.py`, add public function `run_session_resume_parse(resume_text: str, *, debug: bool = False) -> Tuple[Dict[str, Any], int]` near `run_candidate_artifact_generation` / `parse_candidate_resume` (same module owns craft resume split helpers).
2. Validate input: if `resume_text` is not a `str` or `not resume_text.strip()`, return `({"success": False, "error": "resume_text is required"}, 400)` — do not call `do_task`.
3. Build synthetic token ctx (**no** `astral_candidate_id` key):
   ```python
   structure = default_resume_structure()
   paste = resume_text.strip()
   ctx = {
       "candidate_data": {
           "context": {"starting_resume_text": paste},
           "artifacts": {"resume_structure": structure},
       },
   }
   ```
   ⚠️ **Decision:** Satisfy `TASK_CONFIG["craft_resume_base"]["requires_candidate_key"]` with an in-memory `candidate_data` dict only — do **not** flip `requires_candidate_key` or change the response_schema. Default structure comes from `default_resume_structure()` / `RESUME_STRUCTURE_DEFAULT`, not from any selected candidate’s `artifacts.resume_structure`.
4. Ledger + batch (mirror UI generate cost trail without binding a real candidate):
   - `ledger_task_key = "user-session-parse-resume"`
   - `batch_id = f"{ledger_task_key}-{uuid.uuid4()}"`
   - `database.save_dispatch_ledger(batch_id, ledger_task_key, "session", started_at, entity_type=None, batch_size=1)` then `log_batch_id.set(batch_id)`.
   - ⚠️ **Decision:** Ledger `candidate_id="session"` is a sentinel for Admin cost visibility — **not** an `astral_candidate_id`. Do not resolve or create a candidate row for it.
5. Set debug flag: `logger.set_debug_flag(debug)`. When `debug=True`, Style D: one `debug_index` header for the parse hop (`func="run_session_resume_parse"`, `index=1`, `total=1`, identifier=`batch_id` or `"session"`, outcome success/fail) plus `debug_detail` / `debug_detail_block` for error text or truncated payload — no new ungated `[DEBUG]` info lines (§1.5.1).
6. Call `asyncio.run(do_task(task_key="craft_resume_base", live_content=paste, index=batch_id, ctx=ctx, debug=debug))` inside try/except.
   - ⚠️ **Decision:** Pass `index=batch_id` (session-scoped), **not** a real candidate id. `craft_resume_base` has `entity_type: None`, so `_store_agent_response` skips entity `agent_responses` mutation; agent_data blocks (if stored via effective entity_type) key off the session batch id, never a live candidate.
7. On exception or `not result.get("success")`: update ledger `FAILED` (when batch opened), return 500 body with `success: false` and `error` from exception / `result["error"]` / `"do_task returned None"`.
8. On success: `parsed = result["parsed_response"]`; require `isinstance(parsed, dict)` else 500 with clear error. Call `structure_out, content = split_craft_resume_base_payload(parsed)`. Update ledger `COMPLETED` + `compute_batch_cost` like `run_candidate_artifact_generation`. Return 200 body with `success`, `resume_structure=structure_out`, `base_resume=content`, `parsed_response=parsed`, `batch_id`, `timesheet=result.get("timesheet", {})`.
9. **Forbidden in this function:** any call to `database.get_candidate`, `database.save_candidate`, `_persist_craft_dispatch_success`, `_stash_pending_craft_generation`, or job/tracker artifact writers. Do not reuse `run_candidate_artifact_generation` (it persists `craft_resume_base` today) or `parse_candidate_resume` (same).
10. `finally`: `flush_log_buffer()`; `log_batch_id.set(None)`.

## Stage 2: Admin API route

**Done when:** `POST /api/admin/session_resume/parse` is registered on `admin_bp`, requires admin auth, validates JSON, delegates to `run_session_resume_parse`, and returns its `(body, status)` unchanged; `py_compile` clean on touched files.

1. In `src/ui/api/api_admin.py`, import `run_session_resume_parse` from `src.core.candidate` (keep ui → core only).
2. Add route:
   ```python
   @admin_bp.route("/session_resume/parse", methods=["POST"])
   @require_admin
   def session_resume_parse():
       body = request.get_json(silent=True) or {}
       resume_text = body.get("resume_text")
       result_body, status = run_session_resume_parse(
           resume_text if isinstance(resume_text, str) else "",
           debug=ui_llm_debug(),
       )
       return jsonify(result_body), status
   ```
   - Pass `""` when `resume_text` is missing/non-string so core returns the 400 `resume_text is required` message (single validation home).
   - Use existing `ui_llm_debug()` (already imported in this module) for the debug flag — same pattern as adhoc / candidate generate.
3. Do **not** register a new blueprint or touch `server.py` (admin_bp already registered).
4. Do **not** add NAV_CONFIG entries or frontend files (AST-987).
5. Compile: `python3 -m py_compile src/core/candidate.py src/ui/api/api_admin.py`.

## Self-Assessment

**Scope:** `Single-Component` — one core orchestrator beside existing craft helpers plus one Admin POST route; no schema/registry/UI surface.

**Conf:** `high` — reuses `do_task("craft_resume_base")`, `default_resume_structure()`, and `split_craft_resume_base_payload`; the only new behavior is synthetic ctx + skipping persist.

**Risk:** `Medium` — a mistaken `astral_candidate_id` or reuse of `run_candidate_artifact_generation` would write `artifacts.base_resume` / `resume_structure` on a real candidate; the plan forbids those paths and uses a session ledger sentinel.

## Code rules check

- §1.3 DRY: new function parallel to `parse_candidate_resume` / UI generate, not a silent flag on the persist path.
- §2.1: no new behavior literals outside existing `RESUME_STRUCTURE_DEFAULT` / TASK_CONFIG; no TASK_CONFIG schema edit.
- §2.4: optional session ledger with batch_id-first; not a dispatch claim batch.
- §2.6: no candidate/job state transitions.
- §3.3: ui → core only; core → data/agent/utils as today.
- §1.5.1: debug Style D only when `debug=True`.
- §3.6: no repo-root `artifacts/` directory.

## Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-985/AST-986-session-parse-api-no-persist-no-candidate-bind`  
**Tip:** `9c49edb`

**Stages delivered:**
- Stage 1 — `run_session_resume_parse` in `src/core/candidate.py` (synthetic default structure, ledger sentinel `session`, no `get_candidate`/`save_candidate`)
- Stage 2 — `POST /api/admin/session_resume/parse` on `admin_bp` (`@require_admin`, `ui_llm_debug`)
