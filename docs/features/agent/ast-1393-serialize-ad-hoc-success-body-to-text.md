# Serialize Ad Hoc success body to text

- **Linear:** [AST-1393](https://linear.app/astralcareermatch/issue/AST-1393)
- **Parent:** [AST-1392](https://linear.app/astralcareermatch/issue/AST-1392)
- **Publish ref:** `sub/AST-1392/AST-1393-serialize-ad-hoc-success-body-to-text`

Agent Ad Hoc Test currently extracts `agent_payload` (or the whole `parsed_response`) and passes that value straight into `_store_response_block`. When the payload is an object — the `craft_company_search_terms` envelope in the parent brief — `save_agent_data` raises `block_data must be a str`, and logs show `_store_response_block failed`. This ticket stringifies that success body to text **before** the RESPONSE write (JSON text for dict/list, otherwise the raw text), using the existing `_caller_response_blob` habit rather than a second store helper, persists that text, and emits found type/shape → recorded text under Style D when `debug=True`.

Sibling #2 owns Admin Test HTTP overlay and React chrome. This ticket does **not** edit `src/ui/api/api_admin.py` or `AdminAnthropicAdHoc.tsx`. Production `do_task` schema validation / AST-1289 coerce is unchanged.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/agent.py` | Stringify workbench success body via `_caller_response_blob` before `_store_response_block`; Style D found→recorded when `debug=True` | core |

Do **not** edit: `src/data/database.py` (`save_agent_data` still raises on non-text), `_store_response_block` signature, `do_task` schema validation / coerce, `src/ui/api/api_admin.py`, `src/ui/frontend/src/pages/AdminAnthropicAdHoc.tsx`, `tests/`, bible.

## Stages

### Stage 1: Stringify workbench success body before RESPONSE write

**Done when:** `run_adhoc_workbench_test` on a successful result whose `parsed_response` is a JSON envelope with an object `agent_payload` (the `craft_company_search_terms` shape) passes a `str` into `_store_response_block` — compact JSON text of that payload, not a dict, not a Python `str(dict)` dump — and the Test still completes success (`dispatch_ledger` `COMPLETED`). A successful plain-text `parsed_response` is stored unchanged (no extra JSON wrapping). With `debug=True`, Style D shows found type/shape → recorded text for that serialize; with `debug=False`, this path adds no new debug-contract lines. `python3 -m py_compile src/core/agent.py` passes.

1. In `src/core/agent.py`, in `run_adhoc_workbench_test`, replace **only** the success-path body that currently reads:

   ```python
           parsed = result.get("parsed_response")
           if isinstance(parsed, dict) and "agent_payload" in parsed:
               response_text = parsed["agent_payload"] or ""
           else:
               response_text = str(parsed) if parsed is not None else ""
           try:
               _store_response_block(
                   entity_type,
                   workbench_task_key,
                   batch_id,
                   response_text,
                   index=entity_id,
                   debug=debug)
           except Exception:
               logger.debug("_store_response_block failed", exc_info=True)
   ```

   with this exact sequence (still inside the existing `else:` of `if not result.get("success"):`):

   ```python
           parsed = result.get("parsed_response")
           if isinstance(parsed, dict) and "agent_payload" in parsed:
               body = parsed["agent_payload"]
           else:
               body = parsed
           try:
               response_text = _caller_response_blob(body)
               if debug:
                   dbg = get_logger(__name__, debug_flag=True)
                   if isinstance(body, dict):
                       shape = f"keys={sorted(body.keys())}"
                   elif isinstance(body, list):
                       shape = f"len={len(body)}"
                   elif isinstance(body, str):
                       shape = f"len={len(body)}"
                   elif body is None:
                       shape = "none"
                   else:
                       shape = type(body).__name__
                   dbg.debug_index(
                       func="run_adhoc_workbench_test",
                       index=1,
                       total=1,
                       identifier=workbench_task_key,
                       outcome="serialized store",
                   )
                   dbg.debug_detail(
                       f"found type={type(body).__name__} shape={shape}"
                   )
                   dbg.debug_detail_block(response_text)
               _store_response_block(
                   entity_type,
                   workbench_task_key,
                   batch_id,
                   response_text,
                   index=entity_id,
                   debug=debug)
           except Exception:
               logger.debug("_store_response_block failed", exc_info=True)
   ```

   `get_logger` is already imported in this module. `_caller_response_blob` already lives in this file (`json.dumps(..., ensure_ascii=False, default=str)` for dict/list; `str(body)` for other non-`None`; `""` for `None`). Do **not** add a second stringify helper. Do **not** call `json.dumps` inline here.

2. Do **not** change the failure branch (`if not result.get("success"):`) — it already stores `_failure_response_block_data(...)` as text. Provider/API failures stay failed Tests.

3. Do **not** change `_store_response_block` to accept non-text. Do **not** change `save_agent_data`. Do **not** route Ad Hoc Test through production `do_task` validation to get a store. Do **not** change `do_task`'s own `store_content = json.dumps(parsed) if isinstance(parsed, (dict, list)) else (parsed or raw_text)` line.

4. Do **not** mutate `result["parsed_response"]`. Do **not** add a new key on `result`. `return result` at the end of the function stays as-is. Sibling #2 owns returning this text from `POST /api/admin/adhoc/test` and pretty-printing it in React.

5. Do **not** pretty-print the stored JSON (`indent=`). Compact JSON from `_caller_response_blob` is the stored RESPONSE body. Do **not** wrap an already-`str` body in extra JSON quotes.

6. Do **not** edit `tests/` or `docs/test-bible/**`. Existing component test `test_success_completes_ledger_and_stores_blocks` still sees `_store_response_block` arg `[3] == "ok"` for a string payload. Betty owns any new object-payload coverage.

⚠️ **Decision:** Reuse `_caller_response_blob` instead of a new workbench-only dumps helper or a second `_store_response_block` that accepts objects. That function is already the dict/list → JSON text / else `str` habit in this file (`astral.standards.dry-and-focused-functions`). Data still raises on non-text (`astral.standards.data-raises-caller-logs`).

⚠️ **Decision:** Keep extracting `agent_payload` when that key is present, then stringify **that** body — not the full `{agent_performance, agent_payload}` envelope. Parent: when a payload key is present, store that payload body. `do_task` dumps the full `parsed` envelope; workbench stays on the payload (existing extract, now JSON text). Empty dict/list become `"{}"` / `"[]"` (structured JSON text), not `""` from the old `or ""` falsy collapse.

⚠️ **Decision:** Do not change `do_task` store or Admin HTTP/React in this ticket. Production ingest and sibling #2 display are out of Boundaries. One stringify call site for the workbench success path is enough.

⚠️ **Decision:** Debug is Style D on `run_adhoc_workbench_test` (index `1/1`, identifier=`workbench_task_key`, outcome=`serialized store`), found type/shape on one `|` detail line, recorded text via `debug_detail_block` (truncation contract). Emit only when `debug=True`. Do not log the raw found object.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Traceability

AC1 persist/no-traceback → S1 | AC2 RESPONSE body → S1 | AC3 plain text → S1 | AC4 debug found→recorded → S1
(AC1 workbench **display** / pretty-print → sibling #2, not this plan)

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
revision: 1
**Ticket:** AST-1393
**Overall:** APPROVED
**Publish ref:** `sub/AST-1392/AST-1393-serialize-ad-hoc-success-body-to-text` @ `2a87dcd5`

## Traceability
AC1 persist/no-traceback → S1 (workbench display → sibling #2) | AC2 RESPONSE body → S1 | AC3 plain text → S1 | AC4 debug found→recorded → S1

## Findings

### acceptable — epic split / AC1 display clause
- **Location:** Plan Boundaries + `## Traceability` note; child Description AC1
- **Finding:** Child AC1 quotes “workbench shows … as JSON text,” but this plan correctly limits scope to core stringify + store; Admin HTTP/React display is sibling #2. Boundaries and traceability call this out explicitly.
- **Recommendation:** No plan change required. UAT for #1 should verify RESPONSE persistence and absence of `_store_response_block failed` / `block_data must be a str`; workbench display parity lands with #2.

### acceptable — Stage 1 done-when vs AC2 wording
- **Location:** Stage 1 “Done when”
- **Finding:** Done-when specifies `str` into `_store_response_block` and ledger `COMPLETED`; AC2’s “equal to text shown in the workbench” is only fully testable after #2. Store path implies AC2 for Execution History.
- **Recommendation:** Optional clarity only — Betty may assert RESPONSE row content in component tests when she adds object-payload coverage.

context_tokens≈11500

## Review (build stub)

**Publish ref:** `origin/sub/AST-1392/AST-1393-serialize-ad-hoc-success-body-to-text`
**Tip (pre-review):** `7fed10d1`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `7fed10d1` | Workbench success body via `_caller_response_blob` before RESPONSE write; Style D found→recorded when `debug=True` |
