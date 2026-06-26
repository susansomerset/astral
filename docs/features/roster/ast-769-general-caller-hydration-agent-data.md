# General caller hydration from agent_data

**Linear:** [AST-769](https://linear.app/astralcareermatch/issue/AST-769/general-caller-hydration-from-agent-data-use-agent-data-for-the-caller)  
**Parent:** [AST-752](https://linear.app/astralcareermatch/issue/AST-752/use-agent-data-for-the-caller-content)  
**Publish ref (origin):** `sub/AST-752/AST-769-general-caller-hydration-agent-data`

Replace in-memory `{$CALLER_*}` propagation during `run_next` chains with hydration from persisted `agent_data`, anchored by the batch id tied to entity state advancement. Refactor AST-597 resume-artifact hydration helpers into one general caller lookup path for all tasks whose prompts reference caller tokens — job, company, and candidate indexed chains. Preserve non-caller chain tokens (`{$JOB_LIST_VISIBLE}`, `{$SELECTED_AGENT}`, `resolve_run_next_live`) and admin preview simulation.

**Sibling boundaries (do not implement here):** `{$CALLER_*}` token registry / Manage Tasks authoring; per-hop `agent_data` storage shape or Execution History UI (AST-531 / AST-528); roster `resolve_run_next_live` DOM/visible threading (AST-469); dispatch_task / agent_task seeding (AST-741 / AST-745); admin `simulated_chain_context_for_preview`; per-hop compound `BUILD_ARTIFACTS` transitions (`_maybe_transition_resume_hop_progress` — keep as-is).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/agent.py` | General caller hydration helpers; wire into `do_task` entry and `run_next` child dispatch; consolidate AST-597 resume entry onto general path; extend Style D debug for all hydration hops | core |

**Out of scope — do not touch:**

| Area | Reason |
|------|--------|
| `src/utils/config.py` | Token registry unchanged per ticket boundaries |
| `src/core/roster.py` | `resolve_run_next_live` unchanged; hydration is inside `do_task` |
| `src/core/consult.py` | Terminal transitions / batch exit unchanged |
| `src/core/dispatcher.py` | Dispatch seeding unchanged |
| `src/core/tracker.py` | State transition rules unchanged |
| `tests/`, bible | Betty after Code Complete |
| `simulated_chain_context_for_preview` | Admin preview stays simulated |

## Stage 1: General hydration helpers (`agent.py`)

**Done when:** Pure helpers load caller tokens from any entity type's stored hop row, with batch anchoring; unit-testable without LLM; no `do_task` wiring yet.

Add a private section **after** the existing AST-597 helpers (~line 680). **Generalize** rather than duplicate — repurpose `_latest_job_hop_agent_ref` into entity-scoped lookup; keep `_resume_artifact_parent_hop_key` only as a fallback when `run_next` reverse lookup is ambiguous (see step 4).

1. **`_entity_row(entity_type: str, entity_id: str) -> Optional[Dict[str, Any]]`**
   - Lazy import `tracker` (`get_job`, `get_company`) and `candidate.get_candidate` for `entity_type` in `ENTITY_TYPES`.
   - Return `None` when missing.

2. **`_anchor_batch_id_from_state_history(entity: Dict[str, Any]) -> Optional[str]`**
   - If `entity.get("state_history")` is empty: return `None`.
   - Let `current_state = (entity.get("state") or "").strip()`.
   - Scan `state_history` **reversed**; return `batch_id` from the **first** entry where `to_state == current_state` and `batch_id` is a non-empty stripped string.
   - ⚠️ **Decision:** Anchors on the history row that advanced the entity **into its current state** — matches parent AC #5 (the batch that completed upstream for this chain attempt, not today's claim batch).

3. **`_caller_anchor_batch_id(entity: Dict[str, Any], chain_context: Optional[Dict[str, str]]) -> Optional[str]`**
   - Priority:
     1. `(chain_context or {}).get("_caller_anchor_batch_id")` stripped
     2. `log_batch_id.get()` when set (same dispatch / synchronous `run_next`)
     3. `_anchor_batch_id_from_state_history(entity)`
   - Return first non-empty or `None`.

4. **`_parent_hop_task_key_for_child(child_task_key: str) -> Optional[str]`**
   - Scan `get_task_keys()`; for each `tk`, `row = get_agent_task(tk)`; collect `tk` where `(row.get("run_next") or "").strip() == child_task_key`.
   - If **one** match: return it.
   - If **multiple** matches: if `child_task_key in resume_artifact_hop_task_keys()`, return `_resume_artifact_parent_hop_key(child_task_key)` (ordered chain wins).
   - Else if **zero** matches: return `None`.
   - Else: return `None` and log `warning` listing ambiguous parents (build-child should stop and comment on AST-752 if this fires in tests).

5. **`_hop_agent_ref_for_parent(entity: Dict[str, Any], parent_task_key: str, anchor_batch_id: Optional[str]) -> Optional[Dict[str, Any]]`**
   - Replace `_latest_job_hop_agent_ref` body with this generalized version; delete `_latest_job_hop_agent_ref` and update any internal callers to use this function.
   - Scan `entity.get("agent_responses") or []` **reversed**.
   - Match `task_key == parent_task_key`, non-empty `prompt_blocks` with a `RESPONSE` block.
   - Skip RESPONSE text starting with `_HOP_FAILURE_RESPONSE_PREFIXES` (reuse existing tuple).
   - When `anchor_batch_id` is set: require `ref.get("batch_id") == anchor_batch_id`.
   - When `anchor_batch_id` is `None`: keep first successful match (candidate fallback — see step 8).
   - Return first match or `None`.

6. **`_task_prompt_texts(agent_task_row: Dict[str, Any], live_content: Optional[str]) -> Dict[str, str]`**
   - Return dict with keys `system`, `user`, `cache_a`…`cache_d`, `nocache`, `live` — raw prompt fields from `agent_task_row` plus `live_content`.

7. **`_task_references_caller_tokens(agent_task_row: Dict[str, Any], live_content: Optional[str]) -> bool`**
   - `return bool(_referenced_caller_tokens(*_task_prompt_texts(...).values()))`.

8. **`_hydrate_caller_chain_context(entity_type: str, entity_id: str, entry_task_key: str, parent_task_key: str, chain_context: Optional[Dict[str, str]]) -> Tuple[Optional[Dict[str, str]], Optional[str]]`**
   - Returns `(hydrated_caller_ctx, error)` — `error` when hydration was required but failed.
   - `entity = _entity_row(...)`; if missing: `(None, f"{entity_type} not found: {entity_id}")`.
   - `anchor = _caller_anchor_batch_id(entity, chain_context)`.
   - `ref = _hop_agent_ref_for_parent(entity, parent_task_key, anchor)`.
   - If `ref is None` and anchor: retry `_hop_agent_ref_for_parent(entity, parent_task_key, None)` once (tolerate batch_id drift on entity row vs ref when history anchor is stale).
   - If still `None`: `(None, f"No stored agent_data for upstream hop {parent_task_key!r} on {entity_type} {entity_id}")`.
   - `ctx = _caller_chain_context_from_hop_agent_ref(ref, parent_task_key)` (existing function).
   - If no non-empty `CALLER_*` values: `(None, f"Stored hop {parent_task_key!r} has empty caller payload")`.
   - Return `(ctx, None)`.

9. **`_merge_hydrated_caller_context(incoming: Optional[Dict[str, str]], hydrated: Dict[str, str]) -> Dict[str, str]`**
   - Start from `dict(incoming or {})`.
   - For each key in `CALLER_HOP_TOKEN_NAMES`: set from `hydrated`.
   - Set `_caller_hydration_source`, `_hop_parent_task_key` from `hydrated`.
   - **Do not** overwrite non-caller keys already on `incoming` (`JOB_LIST_VISIBLE`, `SELECTED_AGENT`, outer chain keys).

10. **Repurpose `_hydrate_resume_entry_chain_context`**
    - Body becomes:
      ```python
      parent = _resume_artifact_parent_hop_key(entry_task_key)
      if parent is None:
          return ({}, None)
      return _hydrate_caller_chain_context("job", astral_job_id, entry_task_key, parent, None)
      ```
    - Keep function name so `run_resume_artifact_chain_for_job` call site unchanged in this stage (Stage 3 consolidates).

⚠️ **Decision:** Candidate entities have no `state_history` batch_id today. For `entity_type == "candidate"`, step 2 returns `None`; step 5 without anchor uses latest successful parent ref per `task_key` (same practical behavior as AST-597 job scan). Document in Betty handoff — full candidate batch anchoring is out of scope until candidate `state_history` exists.

## Stage 2: Hydrate at `do_task` entry before token resolution

**Done when:** Any hop whose prompts reference `{$CALLER_*}` and has a resolvable parent hop loads caller tokens from `agent_data` before `_chain_context` / `resolve_tokens` run; mid-chain dispatch entry (empty incoming `chain_context`) works; first hop in chain still skips hydration.

1. In `do_task`, **after** `_resolve_task_prompts` and **before** `_chain_context(agent_row, …)` (~line 1458), insert:

   ```python
   effective_chain_context = chain_context
   entity_type_pre = _effective_entity_type(task_config, index)
   parent_for_hydration = (chain_context or {}).get("_hop_parent_task_key")
   if not parent_for_hydration and index and entity_type_pre:
       if _task_references_caller_tokens(agent_task_row, live_content):
           parent_for_hydration = _parent_hop_task_key_for_child(task_key)
   if parent_for_hydration and index and entity_type_pre:
       if _task_references_caller_tokens(agent_task_row, live_content):
           hydrated, hydr_err = _hydrate_caller_chain_context(
               entity_type_pre, index, task_key, parent_for_hydration, chain_context,
           )
           if hydr_err:
               return {
                   "success": False,
                   "error": hydr_err,
                   "api_response": None,
                   "parsed_response": None,
                   "timesheet": {},
               }
           effective_chain_context = _merge_hydrated_caller_context(chain_context, hydrated)
   ```

2. Replace all downstream uses of `chain_context` in the **pre-LLM** path of this `do_task` invocation with `effective_chain_context`:
   - `_in_run_next_chain(chain_context=…)` — keep original `chain_context` for `in_chain` detection (parent merge semantics unchanged).
   - `_is_chain_entry(effective_chain_context)`
   - `parent_task_key` extraction from `effective_chain_context`
   - `_chain_context(…, effective_chain_context, …)`
   - `_mid_chain_empty_caller_tokens` segment guard uses `effective_chain_context` mapped through `_cc`
   - Debug `caller_source` / `caller_hydration` blocks (~1469, ~1619): read from `effective_chain_context`

3. **First hop in chain:** when `_parent_hop_task_key_for_child` returns `None` and incoming context has no `_hop_parent_task_key`, skip hydration (chain entry with no upstream caller requirement).

4. **Do not** hydrate when `_task_references_caller_tokens` is false — avoids DB reads on hops that never use `{$CALLER_*}`.

## Stage 3: `run_next` child dispatch — storage-first caller tokens

**Done when:** Synchronous `run_next` child hops resolve `{$CALLER_*}` from parent's just-persisted `agent_data` (via Stage 2 entry hydration), not from in-memory `hop_ctx` merge; `JOB_LIST_VISIBLE` and other non-caller keys still flow through merge.

1. In the `run_next` block (~2235), **before** `_merge_chain_context_for_next_hop`:

   ```python
   caller_only_hop = {
       k: v for k, v in hop_ctx.items()
       if k.startswith("CALLER_") or k in ("CACHE_BLOCK_A", "CACHE_BLOCK_B", "CACHE_BLOCK_C", "CACHE_BLOCK_D")
   }
   non_caller_hop = {k: v for k, v in hop_ctx.items() if k not in caller_only_hop}
   ```

   ⚠️ **Decision:** Strip legacy `CACHE_BLOCK_*` from merged child context too — child hydration rebuilds `CALLER_*` from stored blocks; legacy ABI keys must not mask hydration.

2. Build child dispatch context:

   ```python
   merged_ctx = _merge_chain_context_for_next_hop(chain_context, non_caller_hop)
   merged_ctx["_hop_parent_task_key"] = task_key
   merged_ctx["_caller_anchor_batch_id"] = batch_id or ""
   for k in CALLER_HOP_TOKEN_NAMES:
       merged_ctx.pop(k, None)
   merged_ctx.pop("_caller_hydration_source", None)
   ```

   Remove the old `merged_ctx["_hop_parent_task_key"] = task_key` line (now above).

3. Inner `await do_task(effective_next, …, chain_context=merged_ctx)` — Stage 2 hydrates `CALLER_*` from `agent_data` using `_caller_anchor_batch_id` + parent `task_key`.

4. Keep `hop_ctx` intact for `_log_run_next_hop_boundary(..., hop_ctx=hop_ctx)` and debug `caller_keys=` lines (logs show what parent **would** have passed in-memory for parity debugging).

5. **`run_resume_artifact_chain_for_job`:** replace explicit `_hydrate_resume_entry_chain_context` seed block (~1288–1299) with:

   ```python
   seed_chain: Optional[Dict[str, str]] = None
   parent = _resume_artifact_parent_hop_key(entry_key)
   if parent:
       hydrated, err = _hydrate_caller_chain_context("job", astral_job_id, entry_key, parent, None)
       if err:
           return {"success": False, "error": err, ...}
       seed_chain = _merge_hydrated_caller_context(None, hydrated)
   ```

   (Equivalent to Stage 2 entry path but avoids double-fetch when seeding — seed supplies hydrated context directly.)

## Stage 4: Style D debug for all hydration hops

**Done when:** With `debug=True`, any hop that loaded caller content from storage emits `caller_source=agent_data` and `caller_hydration=agent_data upstream=…` detail lines; hops that consumed live parent output in the same batch still report `caller_source=live_llm` when `_caller_hydration_source` was not set on effective context.

1. Remove the guard `if debug and task_key in resume_artifact_hop_task_keys()` around the **pre-LLM** caller_source block (~1469) and the **token_overlay** block (~1619). Gate instead on:

   ```python
   if debug and (effective_chain_context or {}).get("_caller_hydration_source") == "agent_data":
   ```

   for the dedicated `caller_hydration=agent_data` line.

2. Keep the broader `token_overlay` / `caller_source` line for **any** `debug=True` `do_task` where `_task_references_caller_tokens` is true (not resume-only).

3. Keep `_resume_hop_debug_index` / `_do_task_debug_entry` resume-artifact hop indexing unchanged (AST-597 scope — not part of this ticket).

4. On `run_next` child boundary when `debug`: keep existing `caller_hydration=live_llm parent=%s` detail **after** parent success, before inner `do_task` — documents that the child will hydrate from storage (parent batch id already persisted).

5. No new `logger.info("[DEBUG] …")` strings — `debug_index` / `debug_detail` only per ASTRAL_CODE_RULES §1.5.1.

## Stage 5: Verify (product compile + Betty handoff)

**Done when:** `src/core/agent.py` compiles; no `tests/` edits.

1. `python3 -m py_compile src/core/agent.py`

2. Linear comment for Betty (post Code Complete — do not edit tests in this ticket):

   - **Regression:** existing `TestAst597MidChainResumeHydrationAndTransitions` and daisy-chain tests (AST-303, AST-455, AST-469) remain green.
   - **New coverage — roster:** `do_task("parse_job_list", …)` at chain entry with mocked `company.agent_responses` + `get_agent_data_for_ids` for upstream `select_job_page` — assert zero LLM calls would satisfy caller tokens; `CALLER_*` populated from storage; `JOB_LIST_VISIBLE` still passed via `chain_context` when set.
   - **New coverage — non-roster:** cover-letter or consult chain entry hop with stored parent `agent_responses` — assert hydration path parallel to AST-597 job test.
   - **Batch anchor:** test that `_hop_agent_ref_for_parent` prefers ref matching `state_history` anchor `batch_id` over a newer unrelated ref with same `task_key`.
   - **Failure:** hydration miss returns `success: False` with clear error, no LLM call (extend AST-597 hydration-failure pattern).
   - **Debug:** caplog contains `caller_hydration=agent_data` when `debug=True` on a hydrated hop (roster or resume).

## Execution contract (for the developer agent)

- Execute stages in order. **Stop** on ambiguity — comment on **AST-752** parent with `🛑 Stage N blocked:` template.
- Do **not** edit config, roster `resolve_run_next_live`, consult terminal transitions, dispatcher, tracker, tests, or `simulated_chain_context_for_preview`.
- When hydration cannot find upstream `agent_data`, return `success: False` with clear `error` — do **not** call LLM and hope (`_mid_chain_empty_caller_tokens` remains second-line defense).
- `_maybe_transition_resume_hop_progress` — **do not** move or gate differently.

## Self-Assessment

**Scope — `Single-Component`**  
All product changes live in `src/core/agent.py` — general hydration helpers, `do_task` entry wiring, `run_next` merge adjustment, debug extension. No config, data schema, or UI changes.

**Conf — `Medium`**  
AST-597 patterns and AST-531 storage shape are established; batch anchoring via `state_history` is new but follows existing `transition_*_state` batch_id writes. Candidate anchoring without `state_history` is an explicit documented fallback.

**Risk — `HIGH`**  
Incorrect caller hydration causes silent empty `{$CALLER_*}` or expensive full-chain re-runs; wrong batch anchor could load a prior attempt's caller payload and corrupt downstream prompts.

## Self-review vs ASTRAL_CODE_RULES

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Generalizes AST-597 helpers into one path; reuses `_chain_tokens_for_next_hop`, `get_agent_data_for_ids`, `_caller_chain_context_from_hop_agent_ref`. |
| §1.5.1 debug | Hydration lines gated on `debug=True`; no new unguarded `[DEBUG]` info in touched paths. |
| §2.1 config | No new config keys; `get_task_keys` / `get_agent_task` for parent resolution only. |
| §2.4 batch | Entity claim / release unchanged; reads `batch_id` from history and `log_batch_id` context var only. |
| §2.6 state machine | No new transitions; `_maybe_transition_resume_hop_progress` untouched. |
| §3.3 imports | `agent.py` may import `database.get_agent_data_for_ids`, lazy `tracker` / `candidate` — core→data allowed. |
| §3.5 naming | `_hydrate_caller_*`, `_hop_agent_ref_*`, `_caller_anchor_*` prefix distinguishes from roster DOM hydration. |

No unresolved conflicts.

## Review stub (build)

**Publish ref:** `origin/sub/AST-752/AST-769-general-caller-hydration-agent-data`  
**Product commit:** `174a747` — general caller hydration helpers; `do_task` entry hydration; `run_next` storage-first caller dispatch; debug extension for all hydration hops

## Radia review (2026-06-23)

**Diff:** `origin/dev...origin/sub/AST-752/AST-769-general-caller-hydration-agent-data` @ `ec7e710`  
**Product commit reviewed:** `174a747` (`src/core/agent.py` only)

### What’s solid

| Area | Notes |
|------|-------|
| Plan fidelity (Stages 1–4) | Helpers generalized from AST-597; `do_task` entry hydration; `run_next` strips in-memory `CALLER_*` and re-hydrates via `_caller_anchor_batch_id`; resume seed uses `_hydrate_caller_chain_context` + merge. |
| Fail-closed | Hydration miss returns `success: False` with clear error before LLM; `_mid_chain_empty_caller_tokens` remains second-line on `_cc` built from `effective_chain_context`. |
| Chain semantics | `in_chain` still reads original `chain_context`; token resolution / `_chain_context` use `effective_chain_context` — matches plan Stage 2. |
| Batch anchor | `_anchor_batch_id_from_state_history` + anchor retry without batch on miss; candidate no-`state_history` fallback documented. |
| §1.5.1 debug | `debug_detail` only when `debug=True`; `caller_hydration=agent_data` gated on `_caller_hydration_source`; run_next boundary adds `caller_hydration=live_llm parent=…`. |
| §3.3 layer | Lazy `tracker` / `candidate` in `_entity_row` matches existing `agent.py` precedent; core→data reads only. |
| Tests (AST-769) | `TestAst769GeneralCallerHydration` covers anchor, merge, roster company hop, job cover letter, miss-without-LLM, debug; AST-597 class updated for storage-first debug path. |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| **fix-now** | Publish ref tip vs `origin/dev` — `tests/component/` | ~14 component test methods **removed** on sub tip vs dev (tracker placeholder ingest ×4, `TestBoardRegistryAst457` ×6, gaze_board admin + config ×4). Not AST-769 scope — restore via proper `merge origin/dev` + `merge-tests` on publish ref before resolve; do not land with regressed dev coverage. |
| **fix-now** | `src/utils/config.py`, `src/ui/api/api_admin.py`, `docs/features/roster/ast-750-…` | AST-750 product (score_floor dropdown API + config labels) on **this** publish ref; plan **Out of scope** for AST-769. Split or re-sync sub tip so resolve-child only carries AST-769 (+ tests) unless Susan approved intentional rollup. |
| **discuss** | `agent.py` `_hydrate_caller_chain_context` | Parameter `entry_task_key` unused in body (plan signature only) — drop or include in error strings. |
| **advisory** | `agent.py` `_parent_hop_task_key_for_child` | Full `get_task_keys()` scan on each caller-token `do_task` — fine for current chain size; revisit if task catalog grows. |

### Recommended actions

| Action | Owner |
|--------|-------|
| Re-sync `origin/sub/AST-752/AST-769-general-caller-hydration-agent-data` with `origin/dev` + Betty `merge-tests`; restore deleted non–AST-769 tests | Engineer (`resolve-child`) |
| Remove or relocate AST-750 product delta off this sub ref (or confirm rollup intent with Susan on AST-752) | Engineer / Chuckles |
| Optional: remove or use `entry_task_key` in `_hydrate_caller_chain_context` | Engineer |

## Resolution

**Resolved:** 2026-06-23 (Ada)

| Radia item | Action |
| --- | --- |
| **fix-now** — deleted component tests vs `origin/dev` | Restored `test_tracker.py`, `test_config.py`, `test_api_admin.py`, `test_playwright.py`, and conftest deltas from `origin/dev` on publish ref. |
| **fix-now** — AST-750 sibling product on sub tip | Reverted `dispatch_score_floor_option_labels` / admin route from `origin/dev`; removed `ast-750` feature doc from this ref. |
| **discuss** — unused `entry_task_key` | Included in hydration error strings for traceability. |
| **advisory** — `get_task_keys()` scan | No change — acceptable per review. |

**Publish tip after resolve:** `2263d8a`

