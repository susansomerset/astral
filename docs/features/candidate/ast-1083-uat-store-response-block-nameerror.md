# UAT: NameError in `_store_response_block` RESPONSE debug log

**Linear:** [AST-1083](https://linear.app/astralcareermatch/issue/AST-1083/uat-nameerror-in-store-response-block-response-debug-log)
**Parent:** [AST-952](https://linear.app/astralcareermatch/issue/AST-952)
**Publish ref:** `sub/AST-952/AST-1083-uat-store-response-block-nameerror`

After Estelle `intake_initiate_candidate` succeeds, `_store_response_block` persists the RESPONSE `agent_data` row but crashes under `debug=True` because the `save_agent_data(...)` return is never bound to `result`, yet the found/recorded-style detail log calls `result.get(...)`. Bind the return like the sibling non-RESPONSE store path already does so the write completes and the debug line emits without a NameError.

## UAT fitness

- **AC restored:** Parent AC 8 — “Touched backend `debug=True` validation/write paths emit per-step found/recorded debug lines per the contract above.” Parent AC 9 — “Candidate can complete the mechanical preamble UI driven by PREAMBLE_CONFIG; Valid answers persist to the correct columns/blobs; UI calls Ruth validation rather than inlining a checker.” (intake open / Estelle initiate must not dump a RESPONSE-store traceback that breaks the debug contract on the write path.)
- **Correct outcome:** RESPONSE block write returns cleanly; when `debug=True`, the `agent_data_write block_type=RESPONSE …` detail line logs the write outcome; intake open-message path does not dump a `_store_response_block failed` traceback.
- **Sibling check:** AST-1015 (Ruth / `preamble_validate_response`) and AST-1017 (mechanical intake UI) contracts unchanged — this ticket only fixes `src/core/agent.py` RESPONSE store/debug binding. No PREAMBLE_CONFIG, Ruth outcomes, or intake UI edits. Verified by plan file scope + Files Changed table.
- **Not sufficient:** Removing the stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Bare `try/except` swallow around the debug line; deleting RESPONSE storage; turning off debug to hide the error; returning empty success without persisting `agent_data` — all rejected by Diagnosis. Correct fix is bind `result = save_agent_data(...)` (mirror sibling store at ~L1208).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/agent.py` | In `_store_response_block`, bind `result = save_agent_data(...)` so the existing `debug=True` `agent_data_write` detail line can read `outcome` / `agent_data_id` / `ref_agent_data_id` without NameError | core |

## Stage 1: Bind `save_agent_data` return in `_store_response_block`

**Done when:** With `debug=True`, calling `_store_response_block` (or completing a `do_task` that stores a RESPONSE) persists the RESPONSE row and emits the `agent_data_write block_type=RESPONSE outcome=…` detail line without raising `NameError: name 'result' is not defined`. Function still returns `agent_data_id`.

1. In `src/core/agent.py`, locate `_store_response_block` (currently ~L1520–1553). The call:

   ```python
   save_agent_data(
       agent_data_id=agent_data_id,
       ...
       entity_id=index if index else None,
   )
   ```

   is followed by a `if debug:` block that interpolates `result.get('outcome')`, `result.get('agent_data_id')`, and `result.get('ref_agent_data_id')`.

2. Change that call to bind the return value, matching the sibling store path immediately above (~L1208–1224):

   ```python
   result = save_agent_data(
       agent_data_id=agent_data_id,
       entity_type=entity_type,
       task_key=task_key,
       batch_id=batch_id,
       block_type="RESPONSE",
       block_data=response_text,
       token_size=len(response_text) // CHARS_PER_TOKEN,
       created_at=created_at,
       entity_id=index if index else None,
   )
   ```

3. Leave the existing `if debug:` `dbg.debug_detail(...)` block and the `return agent_data_id` unchanged — do not wrap the debug line in `try/except`, do not delete RESPONSE storage, do not alter `save_agent_data` kwargs beyond the binding.

⚠️ **Decision:** One-line bind to `result` rather than rewriting the debug line to use local `agent_data_id` only — preserves the found/recorded-style contract that logs `outcome` / `ref_agent_data_id` from the write result, identical to the non-RESPONSE store path.

## Self-Assessment

**Scope:** minor — single binding in `src/core/agent.py` `_store_response_block`.

**Conf:** high — Diagnosis matches the source; sibling pattern at ~L1208 already shows the correct bind.

**Risk:** low — restores debug logging on an already-successful write; no schema, config, or intake UI change. Wrong bind would still NameError or log incomplete detail only in this helper.

## Code Rules self-review

| Rule | Check |
|------|--------|
| §1.3 DRY | Reuse the existing `result = save_agent_data(...)` + `agent_data_write` detail pattern from the sibling store in the same file |
| §1.5.1 | Debug detail remains gated on `debug=True`; no new unconditional logs |
| §2.2 | Core-only change; no UI→external |
| §3.3 | No new imports |
| Boundaries | No PREAMBLE_CONFIG / Ruth / library / Estelle prompt edits |

## Review

**Publish ref:** 
**Build tip:** 

### Stages delivered

1.  —  so   detail line no longer NameErrors.
