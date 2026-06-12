# AST-530 — Structured run_next hop logging and empty-caller guard

**Linear:** [AST-530](https://linear.app/astralcareermatch/issue/AST-530/structured-run-next-hop-logging-and-empty-caller-guard-daisy-chain-hop)  
**Parent:** [AST-527](https://linear.app/astralcareermatch/issue/AST-527/daisy-chain-hop-debug-logging)  
**Publish ref (origin only):** `sub/AST-527/AST-530-chain-hop-debug-logging`

Structured observability at every `run_next` hop boundary: parent `task_key`, child `task_key`, `batch_id`, and populated/empty status plus character length for each `CALLER_*` chain key passed to the child. Distinguishes chain-entry hops from mid-chain hops in log and warning shape. Mid-chain hops fail fast (no LLM call) when a prompt references a `{$CALLER_*}` token that resolves empty. Debug enabled on the dispatch entry hop continues to apply to all hops in that chain (existing `debug=` passthrough — verify only, no behavior change unless broken).

**Out of scope (this ticket):** caller-token propagation correctness (**AST-529**), Execution History rows (**AST-528**), Manage Tasks prompt/`run_next` wiring (**AST-313**).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `CALLER_HOP_TOKEN_NAMES`; extend `resolve_tokens` with chain-hop logging knobs | utils |
| `src/core/agent.py` | Chain-entry detection, hop-boundary logs, mid-chain empty-caller guard before API | core |
| `tests/component/utils/test_config.py` | Chain-entry vs mid-chain `resolve_tokens` warning behavior | tests |
| `tests/component/core/test_agent.py` | Hop-boundary logs, fail-fast guard, chain-entry marker | tests |

## Stage 1: Config — caller hop token list and resolve_tokens logging

**Done when:** `CALLER_HOP_TOKEN_NAMES` is importable; `resolve_tokens` accepts hop-context kwargs and emits the correct warning shape for chain-entry vs mid-chain empty `CALLER_*` tokens without changing non-`CALLER_*` chain tokens (e.g. `SELECTED_AGENT`, `JOB_LIST_VISIBLE`).

1. In `src/utils/config.py`, immediately after `get_manage_tasks_chain_tokens()`, add:

   ```python
   CALLER_HOP_TOKEN_NAMES: tuple[str, ...] = tuple(
       k for k in get_manage_tasks_chain_tokens() if k.startswith("CALLER_")
   )
   ```

   Order must match sorted registry order (`CALLER_CACHE_A` … `CALLER_SYSTEM`, `CALLER_RESPONSE`).

2. Extend `resolve_tokens` signature (add optional keyword-only args after existing params):

   ```python
   def resolve_tokens(
       text: str,
       candidate_data: dict,
       task_key: str,
       chain_context: Optional[Dict[str, str]] = None,
       job_context: Optional[Dict[str, str]] = None,
       *,
       chain_entry: bool = False,
       parent_task_key: Optional[str] = None,
       parent_caller_summary: Optional[Dict[str, str]] = None,
   ) -> str:
   ```

3. In the `spec["source"] == "chain"` branch, replace the unconditional empty warning with:

   - If `name` is in `CALLER_HOP_TOKEN_NAMES` and `raw` is empty/missing:
     - **Chain entry** (`chain_entry=True`): **do not** emit `logging.warning` (no mid-chain “unexpected empty” shape). Optional: `logger.debug` only when a module-level debug flag is not available here — **omit debug** in `resolve_tokens`; entry hop INFO is owned by `agent.py` (Stage 2).
     - **Mid-chain** (`chain_entry=False`): emit **one** warning per empty token:

       ```
       Token {$CALLER_SYSTEM} resolved to empty on mid-chain hop (task=<callee_task_key>, parent=<parent_task_key>, parent_caller=<summary>)
       ```

       where `<summary>` is a compact comma-separated list built from `parent_caller_summary` if provided, else from `chain_context` keys in `CALLER_HOP_TOKEN_NAMES`, each entry `KEY=populated|empty(len=N)` using stripped string length (0 for empty).

   - For non-`CALLER_*` chain tokens (`SELECTED_AGENT`, `JOB_LIST_VISIBLE`, etc.): keep today's warning:

     ```
     Token {$NAME} resolved to empty (chain_context, task=%s)
     ```

4. Update every **in-repo** call site of `resolve_tokens` to pass through the new kwargs only from `agent.py` / `resolved_task_system` — all other call sites keep defaults (backward compatible). Grep `resolve_tokens(` after edits; expected non-agent callers unchanged.

5. Do **not** change candidate-path, config-path, or output_type empty warnings.

**Stage 1 commit:** `docs(AST-530): plan — …` is already separate; product commit subject: `feat(AST-530): chain-hop resolve_tokens logging knobs`

## Stage 2: Agent — chain entry, hop-boundary logs, fail-fast guard

**Done when:** A multi-hop `run_next` run emits hop-boundary INFO lines; the first hop logs chain entry; a mid-chain hop with an empty required `{$CALLER_*}` in any prompt segment returns `success: False` without calling `send_to_anthropic` / `send_to_deepseek`; recursive hops still receive the same `debug=` value as the entry hop.

### 2a. Helpers (private, top of chain section in `agent.py`, after `_merge_chain_context_for_next_hop`)

1. Add `_incoming_chain_context(chain_context)` → treat `None` as `{}`.

2. Add `_is_chain_entry(incoming: Optional[Dict[str, str]]) -> bool`:

   - Return `True` when **no** key in `incoming` starts with `"CALLER_"` (including `{}` and `None`).
   - Return `False` when any `CALLER_*` key is present (even if values are empty strings — that is a mid-chain hop per Susan on **AST-527**).

3. Add `_caller_key_status(caller_map: Dict[str, str]) -> str`:

   - For each name in `CALLER_HOP_TOKEN_NAMES`, read `caller_map.get(name, "")`, strip, report `NAME=empty` or `NAME=populated(len=N)` where `N = len(stripped)`.
   - Return comma-joined string in registry order.

4. Add `_referenced_caller_tokens(*texts: Optional[str]) -> set[str]`:

   - Use existing `_TOKEN_RE` from `config` (import `from src.utils.config import _TOKEN_RE, CALLER_HOP_TOKEN_NAMES`) or duplicate the same pattern locally if import of `_TOKEN_RE` is undesirable — prefer importing `_TOKEN_RE` only if not exported; otherwise inline `re.compile(r"\{\$([A-Z_]+)\}")` matching config.
   - Union all `{ $TOKEN }` names found across `texts`; intersect with `CALLER_HOP_TOKEN_NAMES`.

5. Add `_mid_chain_empty_caller_tokens(
       *,
       callee_task_key: str,
       parent_task_key: str,
       chain_context: Dict[str, str],
       parent_caller_summary: Dict[str, str],
       segment_texts: Dict[str, str],
   ) -> Optional[str]`:

   - If `_is_chain_entry(chain_context)` is effectively true for the **incoming** context passed to this hop: return `None` (no guard).
   - Compute `needed = _referenced_caller_tokens(*segment_texts.values())`.
   - For each `tok in needed`, if `(chain_context.get(tok) or "").strip() == ""`, return an error string:

     `Required caller token {$TOK} is empty on mid-chain hop (task=<callee>, parent=<parent>)`

   - Return `None` when all referenced caller tokens are non-empty.

6. Add `_log_chain_entry(task_key: str, batch_id: Optional[str]) -> None`:

   ```python
   logger.info("run_next chain entry: task=%s batch_id=%s", task_key, batch_id or "")
   ```

7. Add `_log_run_next_hop_boundary(
       *,
       parent_task_key: str,
       child_task_key: str,
       batch_id: Optional[str],
       hop_ctx: Dict[str, str],
   ) -> None`:

   ```python
   logger.info(
       "run_next hop: %s -> %s batch_id=%s caller_keys=%s",
       parent_task_key,
       child_task_key,
       batch_id or "",
       _caller_key_status(hop_ctx),
   )
   ```

### 2b. Thread hop context through prompt resolution

1. At the start of `do_task`, after `_cc = _chain_context(agent_row, chain_context)`:

   ```python
   chain_entry = _is_chain_entry(chain_context)
   parent_task_key = (chain_context or {}).get("_hop_parent_task_key")  # see below
   parent_caller_summary = {
       k: (chain_context or {}).get(k, "")
       for k in CALLER_HOP_TOKEN_NAMES
       if k in (chain_context or {})
   }
   if chain_entry:
       _log_chain_entry(task_key, log_batch_id.get())
   ```

   Use `log_batch_id.get()` for batch_id at entry (may be `None` for ad-hoc — still log empty string).

2. Add optional internal-only keys on merged chain context passed childward (stripped before token resolution where they would leak into prompts — they must **not** appear in `TOKEN_SOURCES`):

   - When building `merged_ctx` before recursive `do_task`, set:

     ```python
     merged_ctx["_hop_parent_task_key"] = task_key
     ```

   - In `_chain_context`, when merging `extra`, **drop** keys starting with `"_"` so `_hop_parent_task_key` never reaches `resolve_tokens` as a chain token (filter in `_chain_context` update loop: skip keys starting with `_`).

3. Update `resolved_task_system` to accept and forward `chain_entry`, `parent_task_key`, `parent_caller_summary` to `resolve_tokens`.

4. Update all `resolve_tokens(...)` calls inside `do_task` (system, user, cache A–D, nocache) to pass:

   ```python
   chain_entry=chain_entry,
   parent_task_key=parent_task_key or None,
   parent_caller_summary=parent_caller_summary or None,
   ```

5. After all segments are resolved (immediately before `_assemble_blocks_seven_segment`), call `_mid_chain_empty_caller_tokens` with:

   ```python
   segment_texts = {
       "system": system_content or "",
       "user": user_content or "",
       "cache_a": rca or "",
       "cache_b": rcb or "",
       "cache_c": rcc or "",
       "cache_d": rcd or "",
       "nocache": nocache_content or "",
       "live": live_content or "",
   }
   ```

   Also include **unresolved** template strings from `agent_task_row` for `cache_prompt`, `cache_prompt_b`, `cache_prompt_c`, `cache_prompt_d`, `nocache_prompt`, `user_prompt`, and raw `system_prompt` / agent `content` — the guard must key off **prompt templates**, not only resolved text, so a token that resolves to empty still counts as referenced. Pass both raw template fields and resolved strings into `_referenced_caller_tokens`.

   If error string returned: log at `logger.warning` with `_caller_key_status(_cc)` appended; return:

   ```python
   {
       "success": False,
       "error": err,
       "api_response": None,
       "parsed_response": None,
       "timesheet": {},
   }
   ```

   Do **not** store prompt/response blocks for this failure (same as early validation failures elsewhere in `do_task`).

### 2c. Hop boundary log at run_next transition

1. In the existing `run_next` success path, immediately before `inner = await do_task(...)` (after `merged_ctx = _merge_chain_context_for_next_hop(...)` and after setting `merged_ctx["_hop_parent_task_key"] = task_key`):

   ```python
   _log_run_next_hop_boundary(
       parent_task_key=task_key,
       child_task_key=effective_next,
       batch_id=batch_id,
       hop_ctx=hop_ctx,
   )
   ```

2. Confirm recursive `do_task` call already passes `debug=debug` — no change unless grep shows a regression.

3. `preview_prompt` and `simulated_chain_context_for_preview`: **no fail-fast** (no API). Optionally pass `chain_entry=False` defaults only — do not add hop-boundary logs to preview paths.

**Stage 2 commit subject:** `feat(AST-530): run_next hop logging and empty-caller guard`

## Stage 3: Tests

**Done when:** New tests pass; existing daisy-chain tests in `test_agent.py` (`test_chains_run_next_when_configured`, `_chain_tokens_for_next_hop`, `_merge_chain_context_for_next_hop`, AST-370/455 cases) and `test_config.py` chain token tests remain green.

### 3a. `tests/component/utils/test_config.py`

1. Add class `TestAst530ChainHopResolveTokens`:

   - `test_chain_entry_empty_caller_no_warning`: `caplog` at WARNING; `resolve_tokens("{$CALLER_SYSTEM}", {}, "contemplate_job", chain_context={}, chain_entry=True)` → no WARNING containing `mid-chain`.
   - `test_mid_chain_empty_caller_enhanced_warning`: `chain_entry=False`, `parent_task_key="anticipate_scan"`, `parent_caller_summary={"CALLER_SYSTEM": "", "CALLER_RESPONSE": "x"}` → WARNING contains `parent=anticipate_scan` and `parent_caller=` substring with `CALLER_SYSTEM=empty`.
   - `test_selected_agent_empty_still_warns`: empty `SELECTED_AGENT` with `chain_entry=True` still emits legacy `(chain_context, task=)` warning (non-`CALLER_*` unchanged).

### 3b. `tests/component/core/test_agent.py`

1. Add class `TestAst530RunNextHopLogging`:

   - `test_chain_entry_log`: caplog INFO; stub `_resolve_task_prompts` + `send_to_anthropic` success; `await do_task("evaluate_jd", ...)` with no `chain_context` → assert one log line contains `run_next chain entry` and `task=evaluate_jd`.

   - `test_hop_boundary_log_on_run_next`: two-hop stub like `test_chains_run_next_when_configured`; caplog INFO → assert `run_next hop:` line contains `qualify_job_listings -> evaluate_jd` and `caller_keys=` with `CALLER_RESPONSE=populated(len=`.

   - `test_mid_chain_empty_caller_skips_api`: parent row `run_next="child_task"`; child prompts reference `{$CALLER_SYSTEM}` via stub `agent_task_row` with `system_prompt` or `cache_prompt` containing token; pass merged context with `CALLER_SYSTEM: ""` and `CALLER_RESPONSE: "x"` via monkeypatched chain — `send_to_anthropic` **not** called; result `success is False`; error mentions `CALLER_SYSTEM`.

   - `test_debug_flag_passed_to_child`: two-hop chain; capture `debug` kwarg on inner `do_task` via wrapper mock — inner call receives `debug=True` when outer `debug=True`.

**Stage 3 commit subject:** `test(AST-530): chain hop logging and empty-caller guard`

## Execution contract (developer agent)

- Execute stages in order; one commit per stage on `dev-ada`, then Joan publish each AST-530 SHA to `origin/sub/AST-527/AST-530-chain-hop-debug-logging`.
- Do not modify `src/data/database.py`, dispatcher wiring, or Manage Tasks UI.
- Do not fix empty caller **values** from parent hops (**AST-529**).
- If prompt templates use a `{$CALLER_*}` name outside `CALLER_HOP_TOKEN_NAMES`, stop and comment on **AST-530** — do not expand scope.
- If `preview_prompt` tests fail due to `_chain_context` underscore filter, adjust filter to only drop `_hop_parent_task_key`, not legitimate keys.

## Self-Assessment

**Scope — `scope-Single-Component`**  
Touches `config.py` token resolution and `agent.py` `do_task` hop orchestration only; no UI, data layer, or dispatcher schema changes.

**Conf — `conf-high`**  
Extends established AST-303/455 chain patterns with explicit logging and a guard at the existing prompt-resolution boundary; test patterns mirror `test_chains_run_next_when_configured`.

**Risk — `risk-Medium`**  
Incorrect guard could block legitimate consult/roster chains if prompts reference `{$CALLER_*}` on hops that are not true mid-chain; mitigated by chain-entry detection and template-only references on artifact hops.

## Self-review vs ASTRAL_CODE_RULES

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Reuse `CALLER_HOP_TOKEN_NAMES`, `_TOKEN_RE`, existing `_chain_tokens_for_next_hop`; one helper set in `agent.py`. |
| §1.5 Logging | Warnings/info in utils/core only; data layer unchanged. |
| §2.1 config | Caller name list derived from `TOKEN_SOURCES` registry, not hardcoded duplicates. |
| §2.4 batch | Same `batch_id` / `log_batch_id` across hops; no new batch per hop. |
| §2.6 state machine | No entity state transitions added. |
| §3.3 imports | Core imports utils; utils does not import core. |
| §3.5 naming | Log lines use existing `task_key`, `batch_id` vocabulary. |

No unresolved conflicts — plan is implementable as written.

## Review (build stub)

**Built:** `origin/sub/AST-527/AST-530-chain-hop-debug-logging` @ `783ba141` (product + tests); Radia doc @ `e29b3643`.

**Stages delivered:**
- Stage 1: `CALLER_HOP_TOKEN_NAMES`, `resolve_tokens` chain-entry vs mid-chain warning shapes (`6a61e9fd`).
- Stage 2: `do_task` chain-entry INFO, hop-boundary INFO, mid-chain empty-caller fail-fast before API (`c0c3d647`).
- Stage 3: `TestAst530ChainHopResolveTokens` + hop `TestDoTask` cases (`2250ec60`, Betty harness `783ba141`).

**Manual smoke:** Run a multi-hop artifact task from Scheduled Actions with debug on; confirm `run_next chain entry` on first hop and `run_next hop: parent -> child` lines through terminal hop.

---

## Radia review (2026-05-29)

**Diff:** `origin/dev...origin/sub/AST-527/AST-530-chain-hop-debug-logging` (8 commits, 783ba141 tip).

### What's solid

| Area | Notes |
|------|-------|
| Plan fidelity (hop logging) | `CALLER_HOP_TOKEN_NAMES`, chain-entry INFO, hop-boundary INFO with `caller_keys=` summary, mid-chain enhanced warnings in `resolve_tokens`, fail-fast guard before LLM — matches AC #1–3 and plan Stages 1–2. |
| §1.5 Logging | `get_logger` in `agent.py`; warnings in `config.resolve_tokens`; data layer untouched. |
| §2.4 batch | Same `batch_id` threaded through hop logs and recursive `do_task`; no per-hop batch split. |
| §3.3 layers | Core → utils only for hop helpers; `_chain_context` strips `_`-prefixed internal keys. |
| Tests | `TestAst530ChainHopResolveTokens` + four `TestDoTask` hop cases; daisy-chain regression helpers (`_strict_batch_llm_ok`, provider pin) keep strict consult mocks stable. |
| Self-assessment | Scope/conf/risk labels fit the hop-logging footprint (ignoring bundled AST-513 — see Issues). |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| **discuss** | `src/core/consult.py`, `src/utils/config.py` (`JOB_TOKEN_CONFIG`, job `source`), `src/core/agent.py` (`_job_context_for_call`) — commits `ec15c39a`, `98b0b5c9` | **AST-513** job-token plumbing restored on this branch (~150 LOC). AST-530 boundaries exclude sibling scope; **AST-513** is separate (User Testing). Confirm intentional co-land vs split before prep-uat to avoid double-merge / attribution noise. |
| **discuss** | `src/utils/config.py` — `get_active_llm_provider` | New `ASTRAL_LLM_PROVIDER` env override (`.get()` fallback) not in AST-530 plan; diverges from §2.1 literal-config guidance for non-secret behavior. Document or drop if test-only. |
| **advisory** | `src/core/agent.py` — `_caller_key_status` vs `config._caller_key_status_line` | Duplicate populated/empty formatter (§1.3 DRY nit). |
| **advisory** | `src/core/agent.py` — strict-batch `agent_performance: {}` normalization | Undocumented test-stabilization hook; fine if kept, note in plan or drop when envelope mocks always include the field. |

No **fix-now** items on the hop-logging / empty-caller guard path itself.

### Recommended actions (resolve-astral)

| Item | Action |
|------|--------|
| AST-513 bundle | Ada + Susan: keep on this sub ref intentionally, or revert AST-513 hunks and land via AST-513 publish ref only. |
| `ASTRAL_LLM_PROVIDER` | Either document in plan/config header or remove if redundant with `_patch_strict_batch_anthropic`. |
| DRY / envelope shim | Optional cleanup; not blocking. |

## Resolution (2026-05-29)

**Radia discuss items — closed per Susan resolve direction:**

| Item | Resolution |
|------|------------|
| **AST-513 job-token bundle** (`ec15c39a`, `98b0b5c9`) | **Kept intentionally.** Not on `origin/dev` yet; restored after integration-line merge dropped AST-513 plumbing required for `do_task` hop tests (`build_job_token_context` / `_job_context_for_call`). AST-513 remains separate for attribution; prep-uat will co-land via parent **AST-527** rollup. |
| **`ASTRAL_LLM_PROVIDER` env override** | **Removed** from `get_active_llm_provider` — test-only concern. Betty's `_patch_strict_batch_anthropic` monkeypatches `get_active_llm_provider` and `send_to_deepseek`; bible §7.13zo documents no env export needed for narrowed pytest. Restores §2.1 literal-config pattern. |
| **Advisory DRY / envelope shim** | Deferred — not blocking User Testing. |

**Product delta vs Radia review tip:** revert `ASTRAL_LLM_PROVIDER` hunks in `config.py` only; hop logging / empty-caller guard unchanged.
