# AST-1015 — Preamble Valid / Try Again / Escalate via Ruth

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1015/preamble-valid-try-again-escalate-via-ruth-candidate-profile-preamble  
**Parent:** https://linear.app/astralcareermatch/issue/AST-952/candidate-profile-preamble-to-intake  

**Publish ref (origin):** `sub/AST-952/AST-1015-preamble-validation-ruth`  
**Parent integration ref:** `ftr/AST-952-candidate-profile-preamble-to-intake`

Ship a **reusable Ruth (Little Brain) validation call** for preamble answers: one new `agent_task` + config-driven task key + core callable (+ thin API) that returns exactly **Valid**, **Try Again**, or **Escalate**. Callers (AST-1017) use the outcome to decide whether to advance; this ticket never writes library fields and never advances preamble steps.

Boundaries (do **not** implement): contact/context/artifacts library (AST-1014), `PREAMBLE_CONFIG` Intro/1st/2nd Try copy or step sequence (AST-1016), mechanical intake UI (AST-1017), Estelle confirm (AST-953), new agent personas or agent-framework patterns, candidate state-machine vocabulary changes.

Depends on AST-1014 library already on `origin/ftr/AST-952-candidate-profile-preamble-to-intake` (User Testing) — merge that ftr tip before build; do not re-implement library work.

**Sibling contract (AST-1016, Plan Approved):** `PREAMBLE_CONFIG["validation_task_key"]` is already bound to **`preamble_validate_response`**. This ticket registers that **exact** `task_key` (config + `TASK_CONFIG` + `agent_task.json` + `do_task`). Do not invent a second key.

---

## Revisions

### Revision 1 — 2026-07-28
Driven by: Joan `[plan-discuss] round=1 concern` — task_key `validate_preamble_answer` diverged from approved AST-1016 `PREAMBLE_CONFIG["validation_task_key"]` = `preamble_validate_response` (§2.1 / DRY).
Changes: Renamed agent/`TASK_CONFIG`/`PREAMBLE_VALIDATION_CONFIG` task_key to `preamble_validate_response` everywhere; kept Python callable name `validate_preamble_answer`; added equality assert vs `PREAMBLE_CONFIG["validation_task_key"]` when that block is present; consumer-facing string remains AST-1016’s `validation_task_key`.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `PREAMBLE_VALIDATION_CONFIG` (task_key=`preamble_validate_response` + outcomes); add `TASK_CONFIG["preamble_validate_response"]` with `response_schema`; assert equality with `PREAMBLE_CONFIG["validation_task_key"]` when that block exists | utils |
| `data/admin/agent_task.json` | New row `preamble_validate_response` assigned to `college_intern_ruth` with Valid/Try Again/Escalate prompts | data (repo admin JSON) |
| `src/core/intake.py` | Public `validate_preamble_answer(...)` — ledger + `do_task(task_key=preamble_validate_response)` + outcome parse; `debug=` contract lines; widen module docstring | core |
| `src/ui/api/api_intake.py` | `POST /api/candidates/<candidate_id>/preamble/validate` thin wrapper | ui |

---

## Stage 1: Config — task key, outcomes, TASK_CONFIG schema

**Done when:** `PREAMBLE_VALIDATION_CONFIG["task_key"]` is `"preamble_validate_response"` (same string as approved AST-1016 `validation_task_key`); outcomes are exactly the three AC strings; `TASK_CONFIG` has a matching entry with `response_schema.outcome` required string; `get_task_keys()` includes the new key; if `PREAMBLE_CONFIG` is already defined in `config.py`, a module-level assert enforces key equality. No agent_task JSON or core/UI yet.

1. In `src/utils/config.py`, immediately after `CANDIDATE_LIBRARY_CONFIG` (or after `PREAMBLE_CONFIG` if AST-1016 has already landed on this tree — place this block **after** `PREAMBLE_CONFIG` when both exist so the assert can see it), add:

```python
# AST-1015: Ruth preamble answer validation (Valid / Try Again / Escalate).
# task_key MUST match PREAMBLE_CONFIG["validation_task_key"] (AST-1016) = preamble_validate_response.
PREAMBLE_VALIDATION_CONFIG = {
    "task_key": "preamble_validate_response",
    "outcomes": ("Valid", "Try Again", "Escalate"),
    "outcome_field": "outcome",  # agent_payload key
}
```

2. Immediately after both blocks exist in the file, add (skip only if `PREAMBLE_CONFIG` is not yet defined on this checkout — then the literal alone is the contract; when ftr/sibling merge brings `PREAMBLE_CONFIG`, add the assert in the same stage before Code Complete):

```python
assert PREAMBLE_VALIDATION_CONFIG["task_key"] == PREAMBLE_CONFIG["validation_task_key"]
```

⚠️ **Decision:** Consumer-facing task_key string lives on AST-1016 as `PREAMBLE_CONFIG["validation_task_key"]`. This ticket’s `PREAMBLE_VALIDATION_CONFIG["task_key"]` is the **same literal** (`preamble_validate_response`) plus outcome vocabulary — not a second name. Outcomes stay here (not in PREAMBLE_CONFIG). AST-1017 may read `validation_task_key` from ui_config/`PREAMBLE_CONFIG` and/or call this ticket’s API without choosing between two keys.

⚠️ **Decision:** Do **not** invent `validate_preamble_answer` as a task_key. That name is reserved for the Python callable only (Stage 3).

3. In `TASK_CONFIG`, add an entry keyed `"preamble_validate_response"` (place with other candidate intake tasks, after `intake_build_request`):

```python
"preamble_validate_response": {
    "response_schema": {
        "outcome": {"type": "str", "required": True},
    },
    "response_format": "json",
    "context_format": "preamble_validate_{index}",
    "entity_type": "candidate",
    "requires_candidate_key": True,
    "trigger_state": None,
},
```

4. Do **not** add a `dispatch_tasks` row. This task is on-demand (UI/API), not a scheduler batch.

---

## Stage 2: Repo agent_task row — Ruth only

**Done when:** `data/admin/agent_task.json` contains one new object with `task_key` == `"preamble_validate_response"` (== `PREAMBLE_VALIDATION_CONFIG["task_key"]`), `agent_id` == `"college_intern_ruth"`, prompts that force the three-outcome envelope, and no other agent/persona rows changed. Startup apply of repo JSON would load Ruth on this key (no blank `sync_agent_tasks` stub left as the live row).

1. Append a new object to the JSON array in `data/admin/agent_task.json` with these fields (generate a fresh `task_key_uuid` via `uuid.uuid4()`; set `updated_at` to current UTC `YYYY-MM-DD HH:MM:SS`; leave unused cache slots empty strings):

| Field | Value |
|-------|--------|
| `task_key` | `preamble_validate_response` |
| `agent_id` | `college_intern_ruth` |
| `task_name` | `Validate Preamble Answer` |
| `task_group_name` | `Candidate Preamble` |
| `task_group_order` | `1` |
| `task_seq` | `1` |
| `current` | `1` |
| `run_next` | `""` |
| `system_prompt` | `""` (persona lives on the Ruth agent row) |
| `cache_prompt_b` / `_c` / `_d` / `nocache_prompt` | `""` |

2. Set `cache_prompt` to the standing instructions (exact text):

```
## PREAMBLE ANSWER VALIDATION

You judge whether a candidate ANSWER is a valid response to a QUESTION.
The QUESTION and ANSWER are in the live CONTENT / TASK block as:

QUESTION:
<question text>

ANSWER:
<answer text>

## OUTCOMES (pick exactly one)

- Valid — the answer is recognizably the kind of content the question asked for (even if imperfect, informal, or short).
- Try Again — empty, whitespace-only, off-topic, nonsense, or clearly not what the question asked; the candidate should re-enter.
- Escalate — cannot be judged safely (ambiguous, contradictory, or needs human review). Escalate is never Valid.

## OUTPUT

Return the standard Astral JSON envelope only.
agent_payload must be a JSON object with exactly one key: "outcome"
"outcome" must be exactly one of: Valid | Try Again | Escalate
No extra keys. No commentary outside the envelope. Prefer Try Again over Valid when the answer type is doubtful. Use Escalate only when human review is truly needed.
```

3. Set `user_prompt` to the turn instruction (exact text):

```
Validate the QUESTION/ANSWER pair in the CONTENT block using your PREAMBLE ANSWER VALIDATION instructions. Respond with the envelope and agent_payload.outcome only.
```

⚠️ **Decision:** One generic task for every preamble step (question text supplied at call time), not per-field task keys. AST-1016/1017 pass the step’s `validation_question` string; Ruth does not own PREAMBLE_CONFIG.

⚠️ **Decision:** Do not create or edit any `data/admin/agent.json` persona. Existing `college_intern_ruth` (Little brain) is mandatory.

---

## Stage 3: Core callable — parse outcomes, debug contract, no library writes

**Done when:** `validate_preamble_answer` exists on `src/core/intake.py`, calls `do_task` with `task_key` from `PREAMBLE_VALIDATION_CONFIG` (`preamble_validate_response`), returns one of the three config outcomes on success, never writes `candidate_data` / name columns, treats unrecognized model text as failure (not Valid), and with `debug=True` emits style-D found/recorded lines. Manual call with mocked/`do_task` success path can return `"Try Again"` without advancing anything.

1. Widen the module docstring of `src/core/intake.py` to state it owns mechanical preamble validation **and** Estelle multi-turn sessions.

2. Import `PREAMBLE_VALIDATION_CONFIG` from `src.utils.config`. Import `get_logger` / `truncate_debug_content` from `src.utils.logging` (reuse existing `flush_log_buffer` / `log_batch_id` imports).

3. Add public async function (public section, before session helpers):

```python
async def validate_preamble_answer(
    candidate_id: str,
    question: str,
    answer: str,
    *,
    step_index: int = 1,
    step_total: int = 1,
    debug: bool = False,
) -> dict:
```

**Behavior (literal):**

- Resolve `task_key = PREAMBLE_VALIDATION_CONFIG["task_key"]` (must be `"preamble_validate_response"`).
- Load candidate via `get_candidate(candidate_id)`; if missing → raise `ValueError(f"Candidate not found: {candidate_id}")`.
- If `(question or "").strip()` is empty → raise `ValueError("question required")`.
- Strip `answer` for the model input but **allow** empty answer (Ruth should return Try Again) — do not raise on empty answer.
- Build `live_content` exactly:

```
QUESTION:
{question.strip()}

ANSWER:
{(answer or "").strip()}
```

- Open a dispatch ledger like `_run_intake_task`: `batch_id = f"preamble-{task_key}-{uuid.uuid4()}"`, `save_dispatch_ledger(..., entity_type="candidate", batch_size=1)`, `log_batch_id.set(batch_id)`.
- `await do_task(task_key=task_key, live_content=live_content, index=candidate_id, ctx=candidate, debug=debug)`.
- On `do_task` failure / missing success: update ledger FAILED; return `{"success": False, "outcome": None, "error": <msg>, "batch_id": batch_id}` — **do not** invent Valid.
- On success: read `parsed = result.get("parsed_response")`. After `do_task` unwrap, `parsed` is the `agent_payload` dict (same as other JSON tasks). Read `raw = parsed.get(PREAMBLE_VALIDATION_CONFIG["outcome_field"])` if `parsed` is a dict; else treat as failure.
- If `raw` is not in `PREAMBLE_VALIDATION_CONFIG["outcomes"]` (exact string match): ledger FAILED; return success False with error `invalid preamble validation outcome: {raw!r}` — **never** coerce Escalate or unknown → Valid.
- Else: ledger COMPLETED with `total_passed=1`; return `{"success": True, "outcome": raw, "error": None, "batch_id": batch_id}`.
- `finally`: `flush_log_buffer()`; `log_batch_id.set(None)`.

4. **Debug contract** (`debug=True` only), after the outcome is known (success or typed failure):

- One `logger.debug_index(func="validate_preamble_answer", index=step_index, total=step_total, identifier=candidate_id, outcome=...)` where outcome is `found|Valid` / `found|Try Again` / `found|Escalate` on success, or `found|error` on failure.
- `logger.debug_detail` lines: `question=` and `answer=` via `truncate_debug_content(...)` on the stripped strings; on failure also `error=...`.

5. **Hard rules in this function:** no `save_candidate_data`, no column writes, no candidate state transitions, no PREAMBLE_CONFIG step/Intro reads (task_key may come only from `PREAMBLE_VALIDATION_CONFIG`, which is asserted equal to AST-1016’s key). Try Again / Escalate “do not advance” is satisfied because this callable never advances or persists preamble progress — AST-1017 must not write library fields unless `outcome == "Valid"`.

⚠️ **Decision:** Place the callable in `intake.py` (not a new module, not `candidate.py`) so AST-1017 shares the intake API blueprint and the existing single-shot ledger/`do_task` pattern (`_run_intake_task`), while keeping library persistence owned by AST-1014 helpers.

---

## Stage 4: Thin API — callable from mechanical UI later

**Done when:** Authenticated `POST /api/candidates/<candidate_id>/preamble/validate` with JSON `{question, answer, step_index?, step_total?}` returns `{success, outcome, batch_id}` on Ruth success, 400 on validation ValueErrors, 404 when candidate missing, and never writes candidate data. No React changes.

1. In `src/ui/api/api_intake.py`, import `validate_preamble_answer` from `src.core.intake`.

2. Add route on `intake_bp`:

```
POST /<candidate_id>/preamble/validate
@require_auth
```

3. Handler body:

- `body = request.get_json(silent=True) or {}`
- `question = body.get("question")`; `answer = body.get("answer")` (default `""` if key missing for answer only)
- Optional `step_index` / `step_total`: ints defaulting to `1` / `1`; if present and not int-coercible → 400 `{"error": "step_index and step_total must be integers"}`
- `asyncio.run(validate_preamble_answer(..., debug=_debug_flag()))`
- On `ValueError` with `"Candidate not found"` → 404; other `ValueError` → 400 `{"error": str(e)}`
- On success dict with `success is False` → HTTP 200 still with the JSON body (caller inspects `success` / `outcome`) — same pattern as other LLM wrappers that return structured failure without 500, unless `RuntimeError`/unexpected → 500
- Return `jsonify({k: result[k] for k in ("success", "outcome", "error", "batch_id")})` with status 200 when the callable returns normally

4. Do **not** add frontend pages, PREAMBLE_CONFIG prompts, or library write endpoints.

---

## Execution contract

The plan is binding. The agent:

- Executes steps in order within a stage, and stages in order.
- Does not skip, reorder, combine, or expand steps.
- Does not add files, modules, configs, or dependencies that aren't in the Files Changed table.
- When a step is ambiguous, contradicts another step, references something that doesn't exist, or fails when executed literally — **stops, comments on the Linear parent issue, and waits.**
- Completes a stage on the epic worktree, commits, publishes to `origin/sub/AST-952/AST-1015-preamble-validation-ruth`, then proceeds.

Blocking comment format (parent AST-952):

```
🛑 Stage N blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

---

## Self-Assessment

**Scope:** Single-Component — one new Ruth `agent_task` (`preamble_validate_response`) + config/`TASK_CONFIG` + intake core callable + one intake API route; no UI, no library schema, no PREAMBLE_CONFIG ownership.

**Conf:** high — aligned to approved AST-1016 `validation_task_key`; reuses `do_task` envelope/`response_schema`, existing Ruth agent, intake ledger pattern, and repo `agent_task.json` apply-at-startup; outcomes are a closed three-string set.

**Risk:** Medium — a wrong coerce-to-Valid path would let bad preamble answers persist once AST-1017 wires writes; mitigated by exact outcome membership check and no writes in this ticket. Key-clash risk with AST-1016 is closed by Revision 1.

---

## Code Rules self-review

| Rule | Check |
|------|--------|
| §1.3 DRY | One epic task_key string shared with AST-1016 (`preamble_validate_response`); reuse `_run_intake_task`-style ledger/`do_task` |
| §1.4 / §2.1 | Task key matches `PREAMBLE_CONFIG["validation_task_key"]`; outcomes only in `PREAMBLE_VALIDATION_CONFIG`; no inline Valid/Try Again/Escalate sets in core/UI |
| §1.5.1 | Debug lines only when `debug=True`; style-D index + ` \| ` detail; truncate long Q/A |
| §2.2 | Core calls `do_task`; no UI→external |
| §2.6 | No candidate state transitions |
| §3.3 | UI imports core only; core does not import UI; no new persona JSON beyond the task row |
| New agents | Forbidden — `college_intern_ruth` only |

## Review

**Publish ref:** `sub/AST-952/AST-1015-preamble-validation-ruth`
**Build tip:** `3a6444b16efae68f0f1bf1180dc04772d7256f31`

### Radia — code-rubric.v1 (`[code-rubric] revision=1`)

**Tip reviewed:** `7ff0ac90955ae70340c4ec1efe57f1e99f6c6ebc` (`origin/sub/AST-952/AST-1015-preamble-validation-ruth` vs `origin/dev`)
**Overall:** DISCUSS

#### What’s solid
- Stages 1–4 match Revision 1: `PREAMBLE_VALIDATION_CONFIG["task_key"]` == `PREAMBLE_CONFIG["validation_task_key"]` == `preamble_validate_response`; Ruth-only `agent_task` row; `validate_preamble_answer` via `do_task` with closed outcomes (no coerce-to-Valid); no library writes / state transitions.
- Debug style-D gated on `debug=True` with truncated Q/A detail; API `POST …/preamble/validate` keeps `@require_auth` and `_debug_flag()`.
- Betty catalog lock 39 + fixture sync for `preamble_validate_response` on ftr base (no polluted origin/dev merge).

#### Issues
1. **discuss** — C4 stragglers: Joan excluded statutes that the three-dot tip scores in-scope (tip carries AST-1014/1016 + frontend/tests): `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, `astral.standards.database-header-inventory`, `astral.ui.frontend-file-placement`. All **conform**; no product fix for AST-1015.

#### Notes
Joan plan-rubric APPROVED (Revision 1 after Plan Discuss). No fix-now on the Ruth validation delta.

## Resolution

**2026-07-30** — `resolve(AST-1015): — clean`

- **fix-now:** none (Radia Overall DISCUSS; recommended proceed).
- **discuss (C4 stragglers):** noted — tip-topology statute in-scope vs Joan plan exclude; all scored **conform**; no AST-1015 product change.
- Tip after resolve publish: `origin/sub/AST-952/AST-1015-preamble-validation-ruth` (this commit).

