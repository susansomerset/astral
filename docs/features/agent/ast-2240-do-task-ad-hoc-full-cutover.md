# AST-2240 — do_task + Ad Hoc full cutover

- **Linear:** [AST-2240](https://linear.app/astralcareermatch/issue/AST-2240) · parent [AST-2235](https://linear.app/astralcareermatch/issue/AST-2235) (Build astral-agent microservice)
- **Publish ref:** `origin/sub/AST-2235/AST-2240-do-task-ad-hoc-full-cutover`
- **Assignee:** Ada
- **Canon Scope:** `astral.agent.do-task-delegation`; `patt.task.daisy-chain`; `patt.task.dispatch-retry`; `astral.batch.entity-agent-responses-latest-only`; `astral.standards.debug-contract-gated`; `patt.agent.provider-io-via-queue` (pending Archie)

Route `do_task` and Ad Hoc Test provider I/O through `src.external.astral_agent.submit`. Prompt rows stay written before enqueue. RESPONSE / failure-audit, decode, daisy-chain, and timesheet stay on the platform after the await returns. No `database.py` sync.

## Explicit scope gate

Ticket **## Scope** names exactly:

- `src/core/agent.py` — **modified** — provider hand-off via client for production and Ad Hoc; preserve assemble/validate/store/daisy-chain.

Every **Files Changed** row is that one path. No `service/**`, no `src/external/astral_agent.py`, no `src/external/{anthropic,llm_compat,openrouter}.py`, no `src/utils/config.py`, no `src/data/database.py`, no tests/bible.

**Prerequisite:** `submit` / `AstralAgentError` (AST-2238) and the AST-2239 request/result field names must exist before Stage 1. This sub’s sync with `--ftr AST-2235` skips (short ref is not on origin). Before editing, re-run:

```bash
~/.cursor/scripts/git/sync-child.sh sub/AST-2235/AST-2240-do-task-ad-hoc-full-cutover --ftr AST-2235-astral-agent-microservice --worktree /home/susan/astral-AST-2235
```

If `src/external/astral_agent.py` is still absent after that, stop and comment on **AST-2240**. Do not invent a second client.

## Canon notes (planner)

- **`astral.agent.do-task-delegation` (read in full):** Callers still enter through `do_task`. `_send_to_server` stops calling `send_to_*` and does not open HTTP. It builds the opaque request dict (blocks already assembled) and calls `astral_agent.submit`. That is the external I/O boundary.
- **`patt.task.daisy-chain` (read in full):** Do not change `run_next` / hop-ledger control flow. A successful hop still continues inside the same `do_task` call. Queue await is inside the hop, not a new dispatch claim.
- **`patt.task.dispatch-retry` (read in full):** Do not change empty-token or schema-failure routing. Provider soft-fails still return `{success: False, failure_class, error}` so existing hop-failure code can move the entity to `_RETRY` / error.
- **`astral.batch.entity-agent-responses-latest-only` (read in full):** Keep `_store_response_block` / `entity_id` stamping and `get_entity_agent_story` → `list_entity_latest_agent_refs`. No Postgres read for latest refs.
- **`astral.standards.debug-contract-gated`:** Keep existing `logger.debug` call sites. Do not log `api_key`, full messages, or a new `logger.info("[DEBUG] …")`.
- **`patt.agent.provider-io-via-queue`:** pending Archie — id-only. Still perform the cutover the parent locked.

## Contract (do not redefine)

Request and result field names are AST-2239’s. Client behavior is AST-2238:

- `await submit(request) -> dict` on job `done` (includes soft provider failure dicts with `success: False`).
- `AstralAgentError` for connectivity, deadline, cancel, and job `failed` (`failure_class` on the exception).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/agent.py` | `_send_to_server` enqueues the assembled request and adapts the queue result; prompt-before and post-return store/decode/chain unchanged | core |

**Out of this ticket:** service tree (AST-2237), platform client module (AST-2238), provider wrappers / `send_to_*` stubs (AST-2239), Railway/CI (AST-2241), `database.py`.

## Stage 1: `_send_to_server` enqueue/await

**Done when:** `rg -n "send_to_anthropic|send_to_llm_compat" src/core/agent.py` is empty. `do_task` still calls `_store_prompt_blocks` before `_send_to_server` and still stores RESPONSE / failure-audit after. `run_adhoc` still calls `_send_to_server` only. `get_entity_agent_story` and any `run_next` call in `do_task` are unchanged. `database.py` is untouched.

1. Replace the imports of `send_to_anthropic` and `send_to_llm_compat` with:
   - `from src.external.astral_agent import AstralAgentError, submit`
   - Keep `getTimestampPrefix` from `src.external.anthropic`.
   - Also import from `src.external.anthropic`: `_effort_body`, `_forced_tool_body`, `_parse_json_response`, `_parse_python_code_response`.
   - Import `calculate_cost_components_from_counts`, `CALC_COST_KEYS` from `src.utils.cost_calculator`.
   - Import `get_model_routing`, `PROVIDER_CALL_BUDGET` from `src.utils.config` (add to the existing config import).

2. Add `_provider_answer_text(api_resp) -> str` in `agent.py`:
   - If `api_resp` is a `str`, return it.
   - Else call `extract_api_response_text(api_resp)` (SDK-shaped leftovers).
   - Replace the two `extract_api_response_text(api_resp)` uses that read `result["api_response"]` inside `do_task` (failure-audit raw text and success `raw_text`) with `_provider_answer_text`. Leave the import of `extract_api_response_text` for the helper.

3. Replace the body of `_send_to_server` (keep the signature). It must not call `send_to_anthropic` or `send_to_llm_compat`.

   Build `request` (omit keys whose value is None / empty dict):

   | Key | Source |
   |-----|--------|
   | `protocol` | `get_llm_server(server_id)["protocol"]` |
   | `server_id` | argument |
   | `model` | `sku` |
   | `api_key` | argument (already required by callers) |
   | `messages` | `[{"role": "user", "content": user_blocks}]` |
   | `system` | `system_blocks` when non-empty |
   | `max_tokens` | argument |
   | `temperature` | argument when not None |
   | `extra_body` | anthropic protocol: `_effort_body(tier.get("reasoning_effort"))` when non-empty. compat: `{**_effort_body(...), **server["request_extras"], **provider}` where `provider` is `{"provider": provider_obj}` if `provider_obj` else `{}`, and `provider_obj` is `dict(tier.get("provider") or {})` plus `require_parameters: True` when `forced_tool` and `get_model_routing(server_id, sku) == "openrouter"` |
   | `extra_headers` | `{"anthropic-beta": "files-api-2025-04-14"}` when any user block is `type == "document"` |
   | `tools` / `tool_choice` | from `_forced_tool_body(forced_tool)` when `forced_tool` is set |
   | `base_url` / `auth` | server catalog, only when protocol is `anthropic_compat` |
   | `concurrency` | `server["concurrency"]` when it is a dict |
   | `probe` | `True` when `get_model_routing(server_id, sku) == "openrouter"` |
   | `routing` | `get_model_routing(server_id, sku)` |
   | `timeout_seconds` / `grace_seconds` / `max_retries` | `PROVIDER_CALL_BUDGET` |
   | `batch_id` | `log_batch_id.get()` when set |

   Do not put `record_timesheet`, `debug`, or prompt text into log lines. `logger.debug` may name `server_id`, `sku`, and `protocol` only.

4. `start = datetime.now(timezone.utc)` immediately before `await submit(request)`.
   - On `AstralAgentError`: return `{"success": False, "api_response": None, "parsed_response": None, "timesheet": {"calltime": start.strftime("%Y-%m-%d %H:%M:%S"), "duration": <seconds since start>, "inputtotal": 0, "inputcached": 0, "outputtotal": 0, "cache_creation_tokens": 0}, "error": exc.detail, "failure_class": exc.failure_class}`. Do not record a timesheet row (the call never returned usage).
   - On a dict with `success` not True: same timesheet shape using `usage` counts when present (else 0), `error` / `failure_class` from the dict, `api_response` from the dict, `parsed_response: None`, `host` if present. Still record the timesheet (step 5) so a soft fail has a row, matching today’s `record_timesheet(..., agent_performance="failure")`.
   - On success: `api_response` is the returned string. `parsed_response`:
     - `forced_tool`: `json.loads(api_response)` when the string is non-empty, else None. `JSONDecodeError` → success False, `failure_class` omitted, `error` the decode message (do_task already treats missing class as `provider_failed`).
     - `response_format == "json"`: `_parse_json_response(api_response)`.
     - `response_format == "python"`: `_parse_python_code_response(api_response)`.
     - else: None.
     - `host` from the result when present.

5. Timesheet after a returned dict (success or soft fail), not after `AstralAgentError`. Build kwargs and call `record_timesheet_entry` inside try/except that logs `logger.error_exc` once and continues (a timesheet miss must not change the call outcome):

   - usage keys: `input_tokens`, `output_tokens`, `cache_read_input_tokens`, `cache_creation_input_tokens` (missing → 0).
   - `cache_miss` for pricing = `input_tokens` (same bucket `calculate_cost_components` treats as non-cached input). `cache_read` / `cache_write` / `output` from the matching usage keys.
   - Costs: if protocol is `anthropic` **or** `get_model_routing(server_id, sku) == "direct"`, `calculate_cost_components_from_counts(..., sku=sku, server_id=server_id)`. Else `dict.fromkeys(CALC_COST_KEYS, 0.0)` (OpenRouter reconcile stays the platform receipt path).
   - `record_timesheet_entry(agent_req_id=result.get("response_id"), task_key_uuid=..., model_code=sku, candidate_id=..., batch_id=log_batch_id.get(), batch_size=..., cache_write_tokens, cache_read_tokens, no_cache_prompt_tokens, no_cache_live_tokens, total_no_cache_input_tokens=input_tokens, total_output_tokens=output_tokens, calc_cost_*, provider=server_id, request_type, entity_type, entity_id, call_start=start.isoformat(), call_stop=now.isoformat(), response_item_count=1 if answer text else 0, response_char_length=len(text), agent_performance="success" if success else "failure", failure_note=error or None)`.
   - Also set `result["timesheet"]` to the small dict `do_task` already reads (`calltime`, `duration`, `inputtotal`, `inputcached`, `outputtotal`, `cache_creation_tokens`).

6. Do not reorder `_store_prompt_blocks` vs `_send_to_server` in `do_task`. Do not edit `run_adhoc` except that it already calls `_send_to_server`. Do not edit `get_entity_agent_story`, hop ledger, or `run_next`.

⚠️ **Decision — one choke point:** `do_task` and `run_adhoc` both call `_send_to_server`. Replacing that function covers production and Ad Hoc without a second client call.

⚠️ **Decision — soft fails stay dicts:** `do_task`’s existing `if not result.get("success")` branch owns RESPONSE failure-audit and retry routing. `AstralAgentError` is converted to that dict here so daisy-chain / retry code does not grow a new exception type.

⚠️ **Decision — parse from the text the worker returns:** AST-2239’s `api_response` is a string, not an SDK object. `parsed_response` is produced here with the existing anthropic parse helpers so schema validation in `do_task` is unchanged.

**Stage 1 commit message:** `code(AST-2240): do_task and Ad Hoc enqueue via astral_agent`

## Traceability

| AC | Check | Satisfied by |
|----|--------|----------------|
| 4 | Prompt rows before the provider job; RESPONSE / failure-audit after | Stage 1 step 6 (order unchanged) + await inside `_send_to_server` |
| 5 | No `send_to_anthropic` / `send_to_llm_compat` in `agent.py`; Ad Hoc uses the client | Stage 1 steps 1 and 3; `run_adhoc` stays on `_send_to_server` |
| 6 | Latest refs still from SQLite `agent_data` | `get_entity_agent_story` not edited |
| 7 | No `agent_job` / `astral_agent` sync in `database.py` | File not in **Files Changed** |
| 8 | Two-hop `run_next` still inside one `do_task`, no extra claim | `run_next` / hop ledger not edited; await is inside the hop |
| 9 | Ad Hoc Test uses the queue path | `run_adhoc_workbench_test` → `run_adhoc` → `_send_to_server` |

Parent AC **1–3, 9–11** → **N/A** (service tree, fence, claim lifecycle, service secrets, console logs — other children). No orphan stages.

## Execution contract

- One stage, one commit, push to `origin/sub/AST-2235/AST-2240-do-task-ad-hoc-full-cutover`.
- Do not add files. Do not edit `database.py` or `service/`.
- If `_effort_body` / `_parse_json_response` are gone after AST-2239, stop and comment on **AST-2240** — do not reimplement JSON healing.
- Ambiguity → stop and comment on **AST-2240**.

## Estimate

Confirm Chuckles estimate: 5 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-2240
**Overall:** APPROVED
**Corpus:** b7ab2203048ce0beb2869a12200ab7fa696c8066
**Publish ref:** `ed16ca81734253e9a6e4a8294b287e0c69b74212` (`origin/sub/AST-2235/AST-2240-do-task-ad-hoc-full-cutover`)

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| astral.agent.do-task-delegation | A | | |
| patt.task.daisy-chain | A | | |
| patt.task.dispatch-retry | A | | |
| astral.batch.entity-agent-responses-latest-only | A | | |
| astral.standards.debug-contract-gated | A | | |
| patt.agent.provider-io-via-queue | X | | pending Archie / not in `canon_clerk` active corpus; plan id-only |

(Worst grade **A** on roll-up ids. Statutes/patterns resolved from `canon/statutes/**` and `canon/directives/active/**` at corpus tip.)

## Traceability

Child AC: **4→S1 step 6 + await in step 3**; **5→S1 steps 1, 3, 6**; **6→S1 step 6** (`get_entity_agent_story` untouched); **7→scope** (no `database.py`); **8→S1 step 6** (`run_next`/hop ledger untouched); **9→S1** (`run_adhoc` → `_send_to_server`). Parent AC **1–3, 9–11** N/A per plan table (parent numbering — service/fence/claim/service-secrets/console logs). Single stage; no orphans.

## Findings

**acceptable** — **Parent vs child AC 9:** traceability N/A line refers to **parent** AC 9 (service secrets); child AC 9 (Ad Hoc queue path) is mapped in the table.

**acceptable** — **`_effort_body` / parse helpers** imported from `src.external.anthropic`; plan stop-gate if AST-2239 removes them.

**acceptable** — **`AstralAgentError` → failure dict** preserves `patt.task.dispatch-retry` hop routing without new exception paths in `do_task`.

## R6 (summary)

Faithful to child #4 scope (single-file cutover); prerequisites AST-2238/2239 explicit; prompt-before / post-return store/decode/chain preserved. DRY: one `_send_to_server` choke for production + Ad Hoc. No **D**/**F**; no `fix-now`.

context_tokens≈58000

## Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-2235/AST-2240-do-task-ad-hoc-full-cutover`
**Product commit:** `96c9500c3` — `_send_to_server` enqueues via `astral_agent.submit`

**Implemented:**
- `src/core/agent.py` only. Prompt store stays before the call; RESPONSE / failure-audit, hop ledger, and `run_next` stay after. `get_entity_agent_story` and `database.py` untouched.
- Queue result text is parsed with the existing anthropic helpers. `AstralAgentError` becomes the existing failure dict (no timesheet row). Soft fails and successes record `record_timesheet_entry`.
- Ad Hoc workbench failure-audit also uses `_provider_answer_text` (same string-vs-SDK extract as the two `do_task` sites).

**Canon (self-check):** `do_task` remains the entry; HTTP stays in the external client. Daisy-chain and retry routing unchanged. Latest refs still SQLite. Debug lines do not include the request body or `api_key`.

**Tests:** Betty at Code Complete. No test-tree edits.


## Radia review

[code-rubric]
**Ticket:** AST-2240
**Publish ref:** `a1b48d1d5b2529675083b3359e08125b0f7209d7` (`origin/sub/AST-2235/AST-2240-do-task-ad-hoc-full-cutover`)
**Corpus:** `b7ab2203048ce0beb2869a12200ab7fa696c8066`
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| astral.agent.do-task-delegation | A | | |
| patt.task.daisy-chain | A | | |
| patt.task.dispatch-retry | A | | |
| astral.batch.entity-agent-responses-latest-only | A | | |
| astral.standards.debug-contract-gated | A | | |
| patt.agent.provider-io-via-queue | X | | pending Archie / not in `canon_clerk` active corpus; plan id-only |

(Worst grade **A** on roll-up ids. `astral.agent.*` / `astral.batch.*` / `astral.standards.*` from `canon/statutes/astral/`; patterns via `canon_clerk expand` at corpus tip.)

## Column diff vs plan stage

(aligned) — Joan all **A**; code review matches.

## Frame diff

(none)

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **sibling carry on `origin/dev...` three-dot diff:** full epic stack (AST-2237–2241 service/client/providers/railway/fence, sibling docs, Betty harness) rides this publish ref after **ftr** sync; **AST-2240 product commit** `96c9500c3` touches **`src/core/agent.py` only** — matches scope gate.
- **`database.py`:** `agent_job` / `astral_agent` grep clean on publish ref (AC **7**); file not in cutover commit.

## What's solid

- **AC 5:** no `send_to_anthropic` / `send_to_llm_compat` in `agent.py`; imports `AstralAgentError`, `submit` from `src.external.astral_agent`.
- **AC 4:** `do_task` still runs `_store_prompt_blocks` (via `asyncio.to_thread`) **before** `_send_to_server`; RESPONSE / failure-audit paths use `_provider_answer_text` for queue-returned text.
- **`_send_to_server`:** builds AST-2239-shaped `_provider_request` (protocol, wire fields, `api_key`, probe/routing, `batch_id`); `await submit(request)`; maps `AstralAgentError` → existing failure dict **without** timesheet row; soft fails + successes call `_record_queue_timesheet` with `calculate_cost_components_from_counts` where planned.
- **AC 8–9:** `run_next` / hop ledger logic not reworked; await is inside the hop. Ad Hoc workbench failure-audit uses `_provider_answer_text` (small touch in `run_adhoc_workbench_test` only).
- **Delegation / layers:** provider I/O boundary is external `astral_agent.submit`; core still orchestrates assemble/store/decode/chain — matches `astral.agent.do-task-delegation`.
- **Debug:** submit debug line logs `server_id`, `sku`, `protocol` only — no `api_key` or message bodies in new logs.
- Plan fidelity + estimate **5** fit single-file cutover with prerequisites on branch.

## Recommended actions (downstream only — not executed in this session)

- Chuckles: append artifact, `docs(AST-2240): Radia review — clean`, push publish ref, post slim upshot `--as radia`, **Review Posted** → datt **PROCEED** to **User Testing**.

context_tokens≈22000
