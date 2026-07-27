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

## Radia review (code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-986
**Publish ref tip (pre-docs):** `066bbe625c6741bd6f3695c52f4103025de8b902`
**Overall:** DISCUSS

### What’s solid
- Stages 1–2 match plan: `run_session_resume_parse` + `POST /api/admin/session_resume/parse` (`@require_admin`), synthetic ctx omits `astral_candidate_id`, ledger sentinel `session`, response-only split payload.
- No `get_candidate` / `save_candidate` / persist helpers in the new path; `craft_resume_base` `entity_type: None` preserved.
- Debug Style D gated on `debug=True` via `ui_llm_debug()`; `debug_detail_block` truncates.
- Betty `merge-tests(AST-986)` + manifest coverage for core/API; UI/HTML left to AST-987.

### Findings
**discuss** — straggler — Joan excluded `astral.debug.spikes-under-debug-dir` / `astral.docs.features-single-file-per-ticket` / `astral.git.engineer-test-tree-ban` at plan time; three-dot tip brings `docs/features/**` + `tests/**`/`docs/test-bible/**` in scope. Code scores **conforms** (plan file only; Betty owns tests). No product action required unless Archie wants plan-time exclusion wording tightened.

### Recommended actions
- Engineer: no fix-now; proceed resolve-child when ready (or acknowledge stragglers).
- AST-987: consume success/`success:false` contract only.

### Statutes checked
| id | tier | verdict | one-line |
| -- | -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | universal | conforms | Tip ends with single `merge-tests(AST-986)` SHA |
| orch.git.commit-vocabulary | universal | conforms | `docs`/`code`/`test`/`merge-tests` vocabulary on tip |
| orch.git.flow-direction-inviolable | universal | conforms | Sub publish-ref only; no reverse-flow |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-985/AST-986-…` matches parent Git table |
| orch.git.merge-on-checkout | universal | conforms | No checkout/merge violation in reviewed commits |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No cherry-pick/rebase/force on tip |
| orch.git.no-dev-agent-branches | universal | conforms | No `dev-<agent>` / agent-named publish ref |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Review on `astral-AST-985` epic worktree |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Synthetic ctx / ledger sentinel are planned impl choices |
| orch.pipeline.plan-is-bible | universal | conforms | Diff matches plan stages + API contract |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Artifacts child only |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Review at Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Test/bible via `test`/`merge-tests`; not engineer product commits |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee remains Ada |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada stays implementer through review |
| orch.roles.pre-commit-path-bans | universal | conforms | Role path bans respected on tip vocabulary |
| astral.agent.confidence-bounds | scoped | conforms | Not a graded confidence task |
| astral.agent.do-task-delegation | scoped | conforms | Core calls `do_task("craft_resume_base")` |
| astral.agent.grade-vector-validation | scoped | conforms | Not a graded-vector path |
| astral.batch.batch-id-first | scoped | conforms | Opens ledger with `batch_id` then `log_batch_id` |
| astral.batch.batch-id-format | scoped | conforms | `user-session-parse-resume-{uuid}` prefix form |
| astral.batch.claim-process-release | scoped | conforms | Cost ledger only; not dispatch claim |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | TASK_CONFIG `entity_type: None` skips entity response store |
| astral.config.config-source-of-truth | scoped | conforms | Uses `default_resume_structure` / TASK_CONFIG; no schema edit |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | No scoring / score_floor path |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No new secrets or env literals |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss (no `artifacts/**` / spikes) |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Feature plan only; no spike notes under features |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Single `docs/features/artifacts/ast-986-….md` |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty path is tests/bible; Ada owns src + features |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer `code` commits omit tests/bible |
| astral.layers.core-vs-external-bright-line | scoped | conforms | LLM I/O behind `do_task` |
| astral.layers.import-direction | scoped | conforms | ui→core; core→data/agent/utils |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers/paths miss (no `scripts/**`) |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | Thin Admin route validate+delegate |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | No coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | Not consult/render_verdict |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | `@require_admin` on POST |
| astral.standards.database-header-inventory | scoped | not-applicable | layers/paths miss (no `src/data/**`) |
| astral.standards.data-raises-caller-logs | scoped | conforms | Core/UI return JSON errors; caller logs |
| astral.standards.debug-contract-gated | scoped | conforms | Style D only when `debug=True` |
| astral.standards.dry-and-focused-functions | scoped | conforms | Parallel session fn; not a persist-path flag |
| astral.standards.in-scope-only | scoped | conforms | Product delta is core+admin API; UI is AST-987 |
| astral.standards.logging-via-utils | scoped | conforms | `get_logger` / debug helpers |
| astral.standards.no-cross-contamination | scoped | conforms | Stays in layered src |
| astral.standards.no-hardcoded-sets | scoped | conforms | No new state enums; intentional ledger key |
| astral.standards.public-then-helpers | scoped | conforms | Public `run_session_resume_parse` beside craft helpers |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | layers/paths miss (no `src/utils/**`) |
| astral.state.core-decides-transitions | scoped | conforms | No candidate/job transitions |
| astral.state.job-prior-states-enforced | scoped | conforms | No job state machine work |
| astral.state.no-daisy-chain-in-run | scoped | conforms | Single craft hop |
| astral.ui.frontend-file-placement | scoped | not-applicable | paths miss (no `src/ui/frontend/**`) |
| astral.ui.naming-conventions | scoped | conforms | snake_case `/session_resume/parse` |
| astral.ui.single-gunicorn-worker | scoped | conforms | No gunicorn/worker changes |

### Pattern conformance
none cited

### Plan adherence
Self-Assessment Scope `Single-Component` matches (core orchestrator + Admin POST). Boundaries held vs AST-987. Joan discuss items (distinct ledger key; agent_data vs entity_type None) implemented as planned — no new product discuss beyond C4 stragglers.

### Notes
Joan plan-rubric verdict attached (APPROVED). Stragglers listed under Findings.

context_tokens≈45000

## Resolution (Ada / resolve-child) — 2026-07-27

**Review tip:** `origin/sub/AST-985/AST-986-session-parse-api-no-persist-no-candidate-bind` @ `6d1f8db` (Radia `docs(AST-986): Radia review — findings`).

**fix-now:** none.

**Discuss:** C4 straggler (Joan plan-time exclusions vs three-dot tip paths) — acknowledged; Radia scored **conforms** and called out no product action. Left as-is (no plan-wording churn without Archie ask).

**Product delta this resolve:** none — clean resolve.
