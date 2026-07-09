# do_task run_next chain recursion and DB hop labels

**Linear:** [AST-848 — do_task run_next chain recursion and DB hop labels](https://linear.app/astralcareermatch/issue/AST-848/do-task-run-next-chain-recursion-and-db-hop-labels-unify-build)  
**Parent:** [AST-847 — Unify BUILD_ARTIFACTS chain in do_task (per-hop state + terminal graduation)](https://linear.app/astralcareermatch/issue/AST-847/unify-build-artifacts-chain-in-do-task-per-hop-state-terminal) (AC reference only — do not expand epic scope)  
**Publish ref:** `origin/sub/AST-847/AST-848-do-task-run-next-chain`

Move synchronous `run_next` daisy-chain ownership into `do_task`: after each successful job hop, write a runtime DB label `<dispatch_trigger_state>.<completed_task_key>` to `job.state`; recurse into the next hop via existing `run_next` dispatch; when the terminal hop succeeds and graduation is enabled for this dispatch, transition to the config-defined successor job state (UAT: `BUILD_ARTIFACTS.*` → `CANDIDATE_REVIEW`) in the same invocation — no persist gates, no consult-layer graduation wrapper. Retire AST-803 consult-only graduation paths touched by this ticket. Dispatch claim/validation changes are **AST-849** — do not implement here.

**Supersedes (remove, do not extend):** AST-803 `do_chain_for_job` graduation + persist gate; consult-layer `_chain_graduate_to_candidate_review`; `_chain_single_hop_dispatch_only` graduation gating; separate `_run_craft_job_cover_letter_batch` path when `draft_cover_letter` is reachable via `run_next` at the same trigger state.

**Out of scope:** Dispatcher claim/validation / eligibility expansion (**AST-849**); hop prompts or `run_next` graph edits in Manage Tasks; `JOB_STATES` compound hop registry entries; `tests/` edits (Betty at Code Complete); post-run artifact body harvest into `job_data`.

**Related (context only):** [AST-803](./ast-803-build-artifacts-chain-dispatch.md), [AST-844](./ast-844-uat-build-artifacts-chain-terminal-graduation.md), sibling [AST-849](https://linear.app/astralcareermatch/issue/AST-849/retire-consult-chain-dispatch-claim) (dispatch claim).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Generic hop-label helpers; `DISPATCH_CHAIN_TERMINAL_GRADUATION` map; relax claim-state predicate for `{trigger}.{hop}` labels | utils |
| `src/core/tracker.py` | `write_job_dispatch_hop_label`, `graduate_job_from_dispatch_chain` | core |
| `src/core/agent.py` | Per-hop DB writes, terminal graduation, failure routing, chain ctx propagation, AST-538 hop debug | core |
| `src/core/consult.py` | Remove consult graduation/persist gate; thin `do_chain_for_job`; pass chain ctx; retire cover-letter batch exclusion when in graph | core |
| `docs/ASTRAL_CODE_RULES.md` | §2.6 daisy-chain carve-out for `do_task` | docs |

**Verify only (no product change expected in this ticket):**

| File | Role |
|------|------|
| `src/core/roster.py` | Existing `select_job_page` → `parse_job_list` `resolve_run_next_live` suppression unchanged |
| `src/core/dispatcher.py` | Claim/validation — **AST-849** |

---

## Stage 1: Config — hop labels and terminal graduation map

**Done when:** Helpers parse/build `{trigger}.{hop}` labels generically; `DISPATCH_CHAIN_TERMINAL_GRADUATION` maps `BUILD_ARTIFACTS` → `CANDIDATE_REVIEW`; `is_valid_job_batch_claim_state` accepts any `{registered_trigger}.{known_task_key}` pattern for job dispatch resume; `python3 -m py_compile src/utils/config.py` passes.

1. In `src/utils/config.py`, after `BUILD_ARTIFACTS_BASE_STATE` / `LEGACY_BUILD_ARTIFACTS_PREFIX` constants (~line 1096), add module-level graduation map (config-driven — no state-name branches in agent):

   ```python
   # Dispatch trigger_state -> JOB_STATES key when a full run_next chain completes (terminal hop, graduation enabled).
   DISPATCH_CHAIN_TERMINAL_GRADUATION: dict[str, str] = {
       BUILD_ARTIFACTS_BASE_STATE: "CANDIDATE_REVIEW",
   }
   ```

2. Add helpers (generic — not BUILD_ARTIFACTS-specific logic in callers):

   ```python
   def dispatch_hop_label(trigger_state: str, completed_task_key: str) -> str:
       ts = (trigger_state or "").strip()
       tk = (completed_task_key or "").strip()
       if not ts or not tk:
           raise ValueError("dispatch_hop_label requires non-empty trigger_state and task_key")
       return f"{ts}.{tk}"

   def parse_dispatch_hop_label(state: str) -> tuple[str, str] | None:
       """Return (trigger_state, completed_task_key) when state matches trigger.hop pattern."""
       st = (state or "").strip()
       if "." not in st:
           return None
       trigger, hop = st.split(".", 1)
       trigger = trigger.strip()
       hop = hop.strip()
       if not trigger or not hop:
           return None
       if hop not in TASK_CONFIG:
           return None
       return trigger, hop

   def dispatch_chain_graduation_target(trigger_state: str) -> str | None:
       return DISPATCH_CHAIN_TERMINAL_GRADUATION.get((trigger_state or "").strip())
   ```

3. Extend `is_valid_job_batch_claim_state(state: str) -> bool` (~line 3000): after existing `JOB_STATES` and `legacy_build_artifacts_hop` checks, return `True` when `parse_dispatch_hop_label(s)` is not `None` **and** the parsed `trigger_state` is a key in `DISPATCH_CHAIN_TERMINAL_GRADUATION` (claim-only runtime labels — not `JOB_STATES` registry entries).

4. Add assert after map definition: every value in `DISPATCH_CHAIN_TERMINAL_GRADUATION` is a key in `JOB_STATES`.

5. `python3 -m py_compile src/utils/config.py`

⚠️ **Decision:** Graduation targets live in config map keyed by dispatch `trigger_state`, not hardcoded in `agent.py`. Adding a new chain trigger in the future is a config row only.

---

## Stage 2: Tracker — runtime hop writes and chain graduation

**Done when:** Hop labels write to `job.state` + `state_history` without `JOB_STATES` registry validation; graduation accepts compound runtime labels whose trigger is in the graduation map; `python3 -m py_compile src/core/tracker.py` passes.

1. In `src/core/tracker.py`, add import: `parse_dispatch_hop_label`, `dispatch_chain_graduation_target`, `dispatch_hop_label` from `src.utils.config`.

2. Add `write_job_dispatch_hop_label(job_id: str, trigger_state: str, completed_task_key: str) -> str`:
   - Compute `label = dispatch_hop_label(trigger_state, completed_task_key)`.
   - Load job via `database.get_job`; raise `ValueError` if missing.
   - Append `state_history` entry: `{"to_state": label, "timestamp": now_iso, "batch_id": job.get("batch_id")}`.
   - `database.save_job(job_id, state=label, state_history=history, state_changed_at=now)`.
   - Return `label`.
   - **Do not** call `validate_value` / `JOB_STATES` — runtime label only.

3. Add `graduate_job_from_dispatch_chain(job_id: str, trigger_state: str) -> str`:
   - Load job; raise if missing.
   - `to_state = dispatch_chain_graduation_target(trigger_state)`.
   - If not `to_state`: raise `ValueError(f"No graduation target for trigger_state={trigger_state!r}")`.
   - `from_state = (job.get("state") or "").strip()`.
   - Validate `from_state` is a legal predecessor for graduation:
     - Accept if `from_state == trigger_state`.
     - Accept if `parse_dispatch_hop_label(from_state)` returns `(ts, _)` where `ts == trigger_state`.
     - Accept legacy `legacy_build_artifacts_hop(from_state)` when `trigger_state == BUILD_ARTIFACTS_BASE_STATE` (in-flight rows until flattened).
     - Else raise `ValueError(f"Invalid chain graduation from {from_state!r} trigger={trigger_state!r}")`.
   - Call existing `transition_job_state([job_id], to_state)` (registered target state — normal validation).
   - Return `to_state`.

4. `python3 -m py_compile src/core/tracker.py`

⚠️ **Decision:** Per-hop writes bypass `transition_job_state` registry checks; terminal graduation uses `transition_job_state` for the registered successor only.

---

## Stage 3: Agent — per-hop state, terminal graduation, failures, debug

**Done when:** Successful job hops in dispatch chains write DB labels; terminal full-chain hops graduate; single-hop dispatch writes label only; retryable failures hold position; hard failures use hop `error_state`; AST-538 debug headers on chain hops; roster `select_job_page` chain unchanged; `python3 -m py_compile src/core/agent.py` passes.

### 3a. Chain context contract (ctx keys set by consult before `do_task`)

Add module comment above `do_task` documenting required ctx keys for dispatch chains:

| Key | Type | Meaning |
|-----|------|---------|
| `dispatch_trigger_state` | `str` | Dispatch row `trigger_state` (e.g. `BUILD_ARTIFACTS`) |
| `dispatch_chain_graduate_on_terminal` | `bool` | `True` = after terminal hop (empty `run_next`), call graduation; `False` = single-hop row (write label only) |

Consult sets `dispatch_chain_graduate_on_terminal = bool(_current_agent_task_run_next(dispatch_task_key))` when starting a hop from a dispatch row (non-empty `run_next` on the **dispatched** agent_task row → full chain; empty → single hop).

Propagate both keys unchanged through `run_next` recursion in the existing `merged_ctx = dict(ctx)` path (~line 2419) — do not drop on hop boundaries.

### 3b. Helpers in `agent.py`

1. Add `_dispatch_chain_ctx(ctx) -> tuple[str, bool]` returning `(trigger_state.strip(), graduate_on_terminal)`; empty trigger → `("", False)` (non-dispatch chain — roster paths unchanged).

2. Add `_should_write_dispatch_hop_label(*, entity_type: str, index: Optional[str], ctx: Optional[Dict], trigger_state: str) -> bool`:
   - `True` when `entity_type == "job"`, `index` set, `trigger_state` non-empty, and `dispatch_chain_graduation_target(trigger_state)` is not `None`.

3. Add `_maybe_graduate_dispatch_chain(*, job_id: str, trigger_state: str, graduate_on_terminal: bool, debug: bool) -> None`:
   - No-op unless `graduate_on_terminal` and `dispatch_chain_graduation_target(trigger_state)`.
   - Call `tracker.graduate_job_from_dispatch_chain(job_id, trigger_state)`.
   - Always `logger.info("dispatch chain graduated job=%s trigger=%s → %s", job_id, trigger_state, to_state)` (non-debug).
   - When `debug`: `get_logger(__name__, debug_flag=True).debug_index(func="do_task chain graduation", index=1, total=1, identifier=job_id, outcome="graduated")` plus `debug_detail` with from/to states.

4. Replace `_resume_hop_debug_index` body: when `_dispatch_chain_ctx(ctx)` has non-empty trigger, compute hop index by walking `run_next` from chain entry stored in ctx (`dispatch_chain_entry_task_key` — set once at chain entry to first executed `task_key`) **or** use sequential counter in ctx `_dispatch_chain_hop_index` incremented each successful hop write. Prefer counter approach:

   - At first hop write in an invocation tree, init `ctx["_dispatch_chain_hop_index"] = 1`; each write increments.
   - Total hops: optional `ctx.get("_dispatch_chain_hop_total")` — if unset, use `total=0` in header (Style D allows unknown total) or omit total segment.
   - Keep existing `resume_artifact_hop_task_keys()` index fallback when no dispatch trigger in ctx (legacy debug paths).

### 3c. Success path — after LLM success, before `run_next` branch (~line 2288)

After `_store_agent_response(...)` and before `planned_next = ...`:

1. Read `(trigger_state, graduate_on_terminal) = _dispatch_chain_ctx(ctx)`.

2. If `_should_write_dispatch_hop_label(...)`:
   - Capture `before_state = (tracker.get_job(index) or {}).get("state")`.
   - `label = tracker.write_job_dispatch_hop_label(index, trigger_state, task_key)`.
   - If `debug`: emit Style D header — `func=f"do_task({task_key})"`, `identifier=index`, `outcome="hop ok"`, detail `state_before={before_state!r} state_after={label!r} trigger={trigger_state!r}`.

3. Fall through to existing `planned_next` / `effective_next` logic (preserve `select_job_page` / `parse_job_list` suppressions unchanged).

### 3d. Terminal hop — when `not effective_next` (~line 2335)

Before `_close_hop_ledger` / `return result`:

1. If hop succeeded and `_should_write_dispatch_hop_label(...)`:
   - Call `_maybe_graduate_dispatch_chain(job_id=index, trigger_state=trigger_state, graduate_on_terminal=graduate_on_terminal, debug=debug)`.
   - **Do not** call `persist_job_artifact_from_parsed` gates that blocked graduation — keep existing finalize_cover/finalize_resume persist calls as today (unchanged side effect).

2. Preserve existing non-chain terminal behavior (finalize artifact persist, logging).

### 3e. Failure path — before each early `return {"success": False, ...}` after hop ledger opened

When `_should_write_dispatch_hop_label(...)` and hop failed:

1. Classify retry vs hard using existing consult pattern (`_chain_failure_mode` logic — copy minimal inline test: `"Job not found"` / `"Missing candidate_data"` → hard; else retry):

   ```python
   err_state = (task_config.get("error_state") or "").strip()
   hard = err_state and (
       "Job not found" in str(result.get("error") or "")
       or "Missing candidate_data" in str(result.get("error") or "")
   )
   ```

   ⚠️ **Decision:** Retryable API/validation failures **do not** change `job.state` (hold last successful label or bare trigger). Hard failures transition to hop `error_state` when configured (`ERROR_BUILD_ARTIFACTS` for artifact hops).

2. On hard + `err_state`: `tracker.transition_job_state([index], err_state)` inside try/except; log warning on `ValueError`.

3. When `debug`: detail line `chain_hop_failed retryable={not hard} error={...}`.

### 3f. Recursion ctx propagation (~line 2394)

In the block building `inner = await do_task(effective_next, ...)`:

- Ensure `merged_ctx` copies `dispatch_trigger_state`, `dispatch_chain_graduate_on_terminal`, and hop counter keys from `ctx`.
- Set `merged_ctx["_hop_parent_task_key"] = task_key` (existing).

### 3g. Compile

`python3 -m py_compile src/core/agent.py`

---

## Stage 4: Consult — remove AST-803 graduation wrapper; pass chain ctx

**Done when:** `_chain_graduate_to_candidate_review` and persist gate deleted; `do_chain_for_job` is a thin `do_task` launcher with ctx only; `_run_build_artifacts_chain_batch` no longer calls consult graduation; cover-letter hops in `run_next` graph run inside `do_task` recursion; `python3 -m py_compile src/core/consult.py` passes.

1. Delete `_chain_graduate_to_candidate_review` entirely (~lines 1771–1807).

2. Delete `_chain_single_hop_dispatch_only` (~lines 1817–1827).

3. Rewrite `do_chain_for_job` (~1830):
   - Keep job/candidate validation and `_resolve_chain_start_task_key` / caller hydration seeding (unchanged).
   - Build `task_ctx` as today.
   - Set chain ctx on `task_ctx`:

     ```python
     task_ctx["dispatch_trigger_state"] = (input_state or "").strip() or BUILD_ARTIFACTS_BASE_STATE
     from src.core.agent import _current_agent_task_run_next
     task_ctx["dispatch_chain_graduate_on_terminal"] = bool(
         _current_agent_task_run_next(dispatch_task_key)
     )
     ```

   - `result = await do_task(start_key, index=astral_job_id, ctx=task_ctx, debug=debug, chain_context=seed_chain)`.
   - Return `result` directly — **no** post-call graduation, **no** persist gate, **no** `chain_incomplete` flag.

4. In `_chain_fail_result`: keep hard-failure `ERROR_BUILD_ARTIFACTS` transition; remove any references to deleted graduation helper.

5. In `run_consult_task`, replace the `elif task_key == "draft_cover_letter": return await _run_craft_job_cover_letter_batch(...)` branch (~2114–2115): route `draft_cover_letter` through `_run_build_artifacts_chain_batch` when `input_state` has a graduation map entry (same path as other artifact hops). Leave `_run_craft_job_cover_letter_batch` function in file but unused — **AST-849** may delete; do not call it from `run_consult_task`.

6. Grep `src/` for `_chain_graduate_to_candidate_review`, `_chain_single_hop_dispatch_only`, `persist_gate_failed` — zero hits.

7. `python3 -m py_compile src/core/consult.py`

⚠️ **Decision:** Graduation moves entirely into `do_task` terminal path; consult batch wrapper only sets ctx and invokes `do_task` once per job.

---

## Stage 5: Code rules — daisy-chain carve-out

**Done when:** `docs/ASTRAL_CODE_RULES.md` §2.6 documents the exception; no other sections changed.

1. In §2.6 opening paragraph (~line 181), after the “no daisy-chaining” sentence, add subsection **§2.6.0 Dispatch run_next chains (AST-848)**:

   - Within a **single** `do_task` invocation, when `ctx` carries `dispatch_trigger_state`, successful hops may write runtime DB labels `{trigger}.{task_key}` and recurse via `run_next` until the terminal hop.
   - Terminal graduation to a registered `JOB_STATES` key happens in the same invocation when `dispatch_chain_graduate_on_terminal` is true and the last hop's `run_next` is empty.
   - Runtime hop labels are **not** `JOB_STATES` registry keys; batch claim may accept them (see `is_valid_job_batch_claim_state`).
   - This carve-out does **not** apply to roster/consult score transitions (`render_verdict`) or company batches.

2. Do not edit other §2.6 subsections.

---

## Execution contract (for build-child)

- Execute stages in order; one commit per stage on epic worktree; publish each to `origin/sub/AST-847/AST-848-do-task-run-next-chain`.
- Do not modify `src/core/dispatcher.py` claim logic — **AST-849**.
- Do not edit `tests/` or `docs/test-bible/**`.
- Preserve AST-769 caller hydration and AST-469 roster `select_job_page` suppressions exactly.
- If `transition_job_state` rejects graduation from a runtime label during build, stop and comment on **AST-847** — do not patch dispatcher claim in this ticket.

---

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — Touches agent chain orchestration, tracker state writes, config graduation map, and consult wrapper removal across core layers; primary behavior change is per-hop DB labels plus in-`do_task` terminal graduation.

**Conf:** `Medium` — Existing `run_next` recursion and caller hydration are proven; new pieces are runtime hop labels outside `JOB_STATES` and graduation gating via ctx, with dispatch claim alignment deferred to AST-849.

**Risk:** `HIGH` — Incorrect graduation or hop writes would leave jobs stuck or falsely promoted to Ready; retry/hold semantics must match UAT AC #4–#6.

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Hop label + graduation helpers centralized in config/tracker; agent calls helpers — no duplicated string formatting. |
| §2.1 config | Graduation targets and label parsing in `config.py`; no inline state sets in agent. |
| §2.4 batch | Hop ledger behavior unchanged; dispatch `entity_batch_id` unchanged. |
| §2.6 state machine | Carve-out documented; per-hop writes explicitly bypass registry; terminal step uses `transition_job_state`. |
| §3.3 imports | Tracker lazy-import in agent preserved for cycle break; consult imports agent helpers only where already patterned. |
| §3.5 naming | New functions prefixed by domain (`dispatch_hop_label`, `write_job_dispatch_hop_label`, `graduate_job_from_dispatch_chain`). |

No unresolved conflicts.

---

## Review (build stub)

**Built:** `astral-AST-847` @ `3c1a648` on `origin/sub/AST-847/AST-848-do-task-run-next-chain`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `421dd15` | Config: `DISPATCH_CHAIN_TERMINAL_GRADUATION`, hop label helpers, claim-state predicate |
| 2 | `18894f0` | Tracker: `write_job_dispatch_hop_label`, `graduate_job_from_dispatch_chain`, prior-state flex |
| 3 | `37948f4` | Agent: per-hop DB writes, terminal graduation, failure routing, chain ctx |
| 4 | `8d8d2d9` | Consult: remove graduation wrapper; pass chain ctx; unify draft_cover_letter path |
| 5 | `3c1a648` | Code rules §2.6.0 carve-out |

**Verify:** `python3 -m py_compile` on all touched `.py` files — pass.

**Out of scope (AST-849):** dispatcher claim/validation for runtime hop labels.
