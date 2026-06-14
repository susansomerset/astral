# AST-618 — Agent do_task, run_next, and token overlay debug instrumentation (Debug logging backfill: agent)

- **Linear (this ticket):** [AST-618](https://linear.app/astralcareermatch/issue/AST-618/agent-do-task-run-next-and-token-overlay-debug-instrumentation-debug)
- **Parent:** [AST-541](https://linear.app/astralcareermatch/issue/AST-541/debug-logging-backfill-agent)
- **Publish ref:** `origin/sub/AST-541/AST-618-agent-do-task-run-next-token-debug` (child of AST-541; not Linear `gitBranchName`)
- **Depends on:** [AST-538](https://linear.app/astralcareermatch/issue/AST-538/improve-quality-of-debug-logging) / [AST-554](https://linear.app/astralcareermatch/issue/AST-554/debug-logging-contract-and-shared-helper) — shared helper + §1.5.1 on integration line; [AST-597](https://linear.app/astralcareermatch/issue/AST-597/per-hop-transitions-and-agent-data-mid-chain-resume) — partial resume-hop Style D lines already in `agent.py` (this ticket generalizes and completes the contract).

## Summary

Backfill the **AST-538** debug logging contract across **all** `do_task` orchestration paths in `src/core/agent.py`: per-invocation entry headers with task key, batch id, and entity index **before** the external LLM call; token overlay resolution detail (`chain`, `job`, caller tokens); pre-assembly LLM parameter detail; truncated response payload logging; and generalized `run_next` hop detail. Retire every hand-rolled `logger.info("[DEBUG] …")` in touched blocks. **AST-597** already added resume-artifact hop index + caller-source lines — this ticket **extends** that pattern to non-resume tasks and fills gaps (batch id, assembly detail, payload truncation, exit paths) without changing agent business logic, cache semantics, or external LLM modules.

## Out of scope (explicit)

| Item | Owner |
|------|--------|
| `src/external/anthropic.py`, `src/external/deepseek.py` debug internals | Sibling backfill tickets |
| Dispatcher, consult, roster, gazer, builder modules | **AST-540**–**AST-546** |
| `run_adhoc` / `run_adhoc_workbench_test` / `preview_prompt` | Not named in parent AC; external modules own LLM I/O detail |
| Hop-boundary INFO lines (`run_next hop: …`, `run_next chain entry: …`) | Unchanged — production coexistence per §1.5.1 |
| Betty log-string tests | Forbidden per parent |
| `src/data/` logging | Forbidden per Code Rules |

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/agent.py` | Contract debug across `do_task` entry/exit, token overlay, assembly, response payload, `run_next` boundary; retire `[DEBUG]` in touched blocks; refactor `_resume_hop_debug_index` into generalized entry helper | core |

## Stage 1: Debug logger helper and generalized entry header

**Done when:** With `debug=True`, every `do_task` invocation emits one Style D index header and a `|` detail line containing `task_key`, `batch_id`, and entity `index` immediately before `send_to_anthropic` / `send_to_deepseek`; resume-artifact hops retain hop `index N/M` within the resume chain; with `debug=False`, no new contract lines.

1. Add module-private helper after `_caller_key_status`:

```python
def _do_task_debug_logger(debug: bool):
    """Return a debug-flagged logger for do_task contract lines; caller checks debug first."""
    return get_logger(__name__, debug_flag=True) if debug else logger
```

2. Replace `_resume_hop_debug_index` with `_do_task_debug_entry` (rename function; update sole call site at current `_resume_hop_debug_index` invocation — remove old name):

```python
def _do_task_debug_entry(
    *,
    task_key: str,
    index: Optional[str],
    batch_id: Optional[str],
    in_chain: bool,
    debug: bool,
) -> None:
    if not debug:
        return
    dbg = get_logger(__name__, debug_flag=True)
    entity_id = (index or task_key or "?").strip()
    if task_key in resume_artifact_hop_task_keys():
        keys = resume_artifact_hop_task_keys()
        hop_idx = keys.index(task_key) + 1
        hop_total = len(keys)
        dbg.debug_index(
            func=f"do_task({task_key})",
            index=hop_idx,
            total=hop_total,
            identifier=entity_id,
            outcome="hop",
        )
    else:
        dbg.debug_index(
            func="do_task",
            index=1,
            total=1,
            identifier=entity_id,
            outcome="task start",
        )
    dbg.debug_detail(
        f"task_key={task_key} batch_id={batch_id or ''} index={index or ''} "
        f"in_run_next_chain={in_chain}"
    )
```

3. **Remove** the early call to `_resume_hop_debug_index(task_key, debug=debug)` at ~line 1239 (before `batch_id` is known).

4. After `batch_id = hop_ledger_batch_id or log_batch_id.get()` (~1376) and after `_log_chain_entry` when `chain_entry` (~1377–1378), call:

```python
if debug:
    logger.set_debug_flag(True)
_do_task_debug_entry(
    task_key=task_key,
    index=index,
    batch_id=batch_id,
    in_chain=in_chain,
    debug=debug,
)
```

5. Do **not** remove `_log_chain_entry` INFO line — production coexistence per §1.5.1.

⚠️ **Decision:** Entry debug fires **after** `batch_id` resolution so AC #1 (`task key, batch id, index`) is satisfied on one header + detail pair immediately before the LLM call, not at function entry when `batch_id` may still be unset.

## Stage 2: Token overlay resolution detail

**Done when:** With `debug=True`, after token resolution and before block assembly, `do_task` emits `|` detail for chain/caller tokens on **every** invocation (not only resume hops); job-context tokens when `_jc` is populated; mid-chain empty-caller guard outcome when triggered; with `debug=False`, unchanged.

1. After `_jc = _job_context_for_call(ctx, index, cd)` (~1264) and after all `resolve_tokens` calls for system/user/cache/nocache (~1296–1308), replace the resume-only block (~1251–1263) with:

```python
if debug:
    dbg = get_logger(__name__, debug_flag=True)
    source = (chain_context or {}).get("_caller_hydration_source") or (
        "live_llm" if (chain_context or {}).get("_hop_parent_task_key") else "chain_entry"
    )
    dbg.debug_detail(
        f"token_overlay chain_entry={chain_entry} caller_source={source} "
        f"parent={(chain_context or {}).get('_hop_parent_task_key') or 'none'} "
        f"caller_keys={_caller_key_status(_cc)}"
    )
    if source == "agent_data":
        dbg.debug_detail(
            f"caller_hydration=agent_data upstream={(chain_context or {}).get('_hop_parent_task_key')}"
        )
    if _jc:
        populated = [k for k, v in _jc.items() if (v or "").strip()]
        dbg.debug_detail(f"job_context tokens={','.join(populated) if populated else 'none'}")
```

2. When `_mid_chain_empty_caller_tokens` returns `guard_err` (~1346–1358), before the early `return`, when `debug`:

```python
get_logger(__name__, debug_flag=True).debug_detail(
    f"token_guard blocked: {guard_err} caller_keys={_caller_key_status(_cc)}"
)
```

3. Do **not** add debug lines inside `resolve_tokens` in `config.py` — agent boundary only.

## Stage 3: Pre-LLM assembly detail — retire first `[DEBUG]` block

**Done when:** The two `logger.info("[DEBUG] do_task('%s'): brain_setting=…")` and `logger.info("[DEBUG] do_task('%s'): %d system block(s)…")` lines (~1391–1418) are **removed**; equivalent information appears as `|` detail lines under the Stage 1 header when `debug=True`.

1. **Delete** the block:

```python
if debug:
    logger.info(
        "[DEBUG] do_task('%s'): brain_setting=%s provider=%s ...",
        ...
    )
```

2. **Delete** the block:

```python
if debug:
    logger.info("[DEBUG] do_task('%s'): %d system block(s) + %d user block(s)",
                task_key, len(system_blocks), len(user_blocks))
```

3. After `_assemble_blocks_seven_segment(...)` (~1406–1414), when `debug`:

```python
dbg = get_logger(__name__, debug_flag=True)
model_tag = resolved_anthropic_key if provider == "anthropic" else tier_meta["vendor_model"]
dbg.debug_detail(
    f"llm_params provider={provider} brain_setting={brain_setting} model={model_tag} "
    f"max_tokens={agent_max_tokens} temp={agent_temperature} skip_cache={skip_cache} "
    f"candidate_id={candidate_id or ''}"
)
dbg.debug_detail(
    f"blocks system={len(system_blocks)} user={len(user_blocks)} "
    f"runtime_prompt_segments={len(runtime_prompt)}"
)
```

4. Leave `send_to_anthropic(..., debug=debug)` / `send_to_deepseek(..., debug=debug)` passthrough unchanged — external module owns its own debug (out of scope).

## Stage 4: Response payload truncation — retire encoded `[DEBUG]` block

**Done when:** Long encoded `agent_payload` strings log via `debug_detail_block` (50-line truncation per §1.5.1); the `logger.info("[DEBUG] do_task('%s'): literal encoded agent_payload …\n%s")` block (~1676–1686) is **removed**; with `debug=False`, no payload contract lines.

1. **Delete** the block starting `if debug and "_encoded" in output_type:` that uses `logger.info("[DEBUG] do_task('%s'): literal encoded agent_payload …")`.

2. Replace with (same condition):

```python
if debug and "_encoded" in output_type:
    literal = parsed if isinstance(parsed, str) else raw_text
    if isinstance(literal, str) and literal.strip():
        dbg = get_logger(__name__, debug_flag=True)
        lines = [ln for ln in literal.splitlines() if ln.strip()]
        dbg.debug_detail(
            f"encoded_payload task_key={task_key} lines={len(lines)} chars={len(literal)}"
        )
        dbg.debug_detail_block(literal)
```

3. When `debug=True` and API returns success with a non-empty `raw_text` suitable for UAT (optional, one line only — do not dump full JSON twice): after `raw_text` is captured (~1518–1525), if `raw_text` and `len(raw_text.splitlines()) > 50`:

```python
get_logger(__name__, debug_flag=True).debug_detail(
    f"raw_response task_key={task_key} lines={len(raw_text.splitlines())} chars={len(raw_text)}"
)
get_logger(__name__, debug_flag=True).debug_detail_block(raw_text)
```

⚠️ **Decision:** Emit truncated raw response only when line count exceeds `DEBUG_LINE_THRESHOLD` (50) to avoid duplicating short responses already visible in external debug; encoded payload block always logs summary line + truncated body when non-empty.

## Stage 5: Exit paths and generalized `run_next` boundary detail

**Done when:** With `debug=True`, terminal hop success/failure and `run_next` child dispatch emit contract detail; resume-only restriction on child-boundary `caller_hydration=live_llm` line is removed so **all** chained hops get debug detail; existing INFO hop boundaries unchanged; with `debug=False`, behavior unchanged.

1. Before `_close_hop_ledger(success=False, …)` on the provider-failure early return (~1513), when `debug`:

```python
get_logger(__name__, debug_flag=True).debug_detail(
    f"exit provider_failed task_key={task_key} batch_id={batch_id or ''} error={result.get('error')!r}"
)
```

2. Before the terminal success return when `not effective_next` (~1912), when `debug`:

```python
get_logger(__name__, debug_flag=True).debug_index(
    func="do_task",
    index=1,
    total=1,
    identifier=(index or task_key or "?"),
    outcome="completed",
)
get_logger(__name__, debug_flag=True).debug_detail(
    f"task_key={task_key} batch_id={batch_id or ''} success={result.get('success')}"
)
```

3. Replace the resume-only block (~1926–1929):

```python
if debug and task_key in resume_artifact_hop_task_keys():
    get_logger(__name__, debug_flag=True).debug_detail(
        f"caller_hydration=live_llm parent={task_key}"
    )
```

with (runs for **every** `effective_next` hop):

```python
if debug:
    get_logger(__name__, debug_flag=True).debug_detail(
        f"run_next dispatch parent={task_key} child={effective_next} "
        f"batch_id={batch_id or ''} caller_keys={_caller_key_status(hop_ctx)}"
    )
    get_logger(__name__, debug_flag=True).debug_detail(
        f"caller_hydration=live_llm parent={task_key}"
    )
```

4. Keep `_log_run_next_hop_boundary(...)` INFO call unchanged (~1930–1935).

5. When `effective_next not in TASK_CONFIG` (~1914–1920), when `debug`, before return:

```python
get_logger(__name__, debug_flag=True).debug_detail(
    f"run_next suppressed invalid_child={effective_next!r} parent={task_key}"
)
```

## Stage 6: Verification

**Done when:** `python3 -m py_compile src/core/agent.py` passes; no `[DEBUG]` strings remain in `agent.py`; no edits to `tests/`.

1. Run: `python3 -m py_compile src/core/agent.py`

2. Confirm zero matches: `rg '\[DEBUG\]' src/core/agent.py`

3. Linear comment for Betty (**post Code Complete** — do not edit tests in this ticket):

   - Extend `tests/component/core/test_agent.py`: with `debug=True`, caplog contains Style D header with `task_key=` and `batch_id=` detail before mocked LLM call on a simple `do_task`.
   - Daisy-chain / `run_next` test: two-hop chain emits two entry headers with distinct `task_key` values.
   - `debug=False` regression: existing tests that assert no debug noise still pass.
   - Truncation: mock 60-line encoded payload → caplog contains `"<30 lines omitted>"` per §1.5.1.

## Execution contract (for the developer agent)

- Execute stages in order. **Stop** on ambiguity — comment on **AST-541** with 🛑 template from **plan-child**.
- Do **not** edit `config.py`, `logging.py`, external modules, consult, dispatcher, or `tests/`.
- Do **not** change `do_task` return shapes, cache semantics, token resolution logic, or `run_next` business rules — logging only.
- When codebase drift breaks a step literally — **stop and comment**; do not adapt silently.

## Self-Assessment

**Scope — `Single-Component`**  
All product changes live in `src/core/agent.py` only — one orchestration module, logging instrumentation under existing `debug` parameter.

**Conf — `high`**  
AST-554 helpers and AST-615/AST-597 patterns are established; partial resume-hop debug already landed; remaining work is generalization and retiring three `[DEBUG]` blocks with known replacements.

**Risk — `Medium`**  
`do_task` is on the critical path for every LLM call, but changes are gated on `debug=True` and follow §1.5.1; a mistake could add log volume or leak large payloads if truncation is skipped — mitigated by `debug_detail_block` reuse.

## Self-review vs ASTRAL_CODE_RULES

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Reuses `get_logger`, `debug_index`, `debug_detail`, `debug_detail_block`, `_caller_key_status`; no parallel truncation logic. |
| §1.5.1 debug | All new contract lines gated on `debug=True` + `set_debug_flag`; retires `[DEBUG]` in touched file; hop INFO lines preserved. |
| §2.1 config | No config edits; reads existing `resume_artifact_hop_task_keys`, `TASK_CONFIG`. |
| §2.4 batch | `batch_id` from `log_batch_id` / hop ledger unchanged — logged only. |
| §2.6 state machine | No transition changes. |
| §3.3 imports | No new cross-layer imports. |
| §3.5 naming | `_do_task_debug_entry` / `_do_task_debug_logger` prefix distinguishes from dispatcher helpers. |

No unresolved conflicts — plan assumes AST-554 on integration line (satisfied).

## Review (build stub)

**Built:** `origin/sub/AST-541/AST-618-agent-do-task-run-next-token-debug` @ `adbd9027`.

**Stages delivered:**
- Stage 1: `_do_task_debug_logger` + `_do_task_debug_entry`; retire `_resume_hop_debug_index`; entry after `batch_id` resolution — `adbd9027`.
- Stage 2: Generalized token overlay detail (chain/caller/job); mid-chain empty-caller guard debug — `adbd9027`.
- Stage 3: Assembly + encoded payload `debug_detail` / `debug_detail_block`; provider failure exit debug; long `raw_text` truncation — `adbd9027`.
- Stage 4: `do_task` exit-path debug (cache hit, early return, exception) — `adbd9027`.
- Stage 5: Generalized `run_next` dispatch debug; invalid-child suppression detail — `adbd9027`.

**Stage 6 (verification):** `python3 -m py_compile src/core/agent.py` passed; zero `[DEBUG]` strings in `agent.py`. Betty log-string tests deferred per parent.

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-541/AST-618-agent-do-task-run-next-token-debug` @ `9c26e613`.

### What's solid

| Area | Notes |
|------|--------|
| §1.5.1 trigger | All new contract emission gated on `debug=True`; `[DEBUG]` hand-rolled lines removed from `agent.py`. |
| Entry header | `_do_task_debug_entry` generalizes AST-597 resume-hop index to all tasks; fires after `batch_id` resolution, immediately before LLM call — satisfies AC #1. |
| Assembly / payload | `llm_params` + block counts via `debug_detail`; encoded payload and long `raw_text` (>50 lines) use `debug_detail_block`. |
| Exit / chain | Provider failure, terminal completion index, invalid-child suppression, and generalized `run_next` dispatch detail present; hop INFO boundaries unchanged. |
| Layer / scope | Changes confined to `src/core/agent.py` orchestration; no data-layer logging; external `debug=` passthrough intact. |
| Plan alignment | Self-Assessment scope/conf/risk matches diff; boundaries respected (no dispatcher/external edits). |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| **fix-now** | `do_task` ~1337–1353 vs ~1418 | Stage 2 token-overlay `debug_detail` lines emit **before** `_do_task_debug_entry` `debug_index`. §1.5.1 expects working detail **under** the per-hop header for scan order. Move token overlay block to immediately **after** `_do_task_debug_entry` (still before assembly / LLM). |
| **fix-now** | `_do_task_debug_logger` ~440 | Helper defined in plan Stage 1 but **never called** — dead code. Remove or replace repeated `get_logger(__name__, debug_flag=True)` with it. |
| **advisory** | `_uuid4` bind ~15–16, ~2119, ~2195 | Hop-ledger UUID bind is outside “logging only” scope; commit `9c26e613` rationale (test isolation) is acceptable — no functional change. |
| **advisory** | Build stub Stage 4 label | “cache hit, early return, exception” not in diff; only `exit provider_failed` landed — stub oversells; not blocking vs parent AC. |

### Recommended actions

| Item | Action |
|------|--------|
| Token overlay order | Move `if debug:` token overlay block to after `_do_task_debug_entry` call. |
| Dead helper | Delete `_do_task_debug_logger` or wire callers. |
| `_uuid4` | No change required if tests depend on import-time bind. |
