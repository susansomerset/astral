# AST-531 — Per-hop dispatch_ledger rows for run_next chains

**Linear:** [AST-531](https://linear.app/astralcareermatch/issue/AST-531/per-hop-dispatch-ledger-rows-for-run-next-chains-per-hop-execution)  
**Parent:** [AST-528](https://linear.app/astralcareermatch/issue/AST-528/per-hop-execution-history-for-daisy-chained-tasks)  
**Feature ref:** `sub/AST-528/AST-531-per-hop-dispatch-ledger` (origin only; see orientation-astral § Branch law)

Each `run_next` hop that actually executes an LLM call gets its own `dispatch_ledger` row, its own `batch_id` for `agent_data` / `app_log`, and its own terminal status and cost. This reverses the AST-303 decision to keep one `log_batch_id` across hops for Execution History only. Sibling **AST-532** owns UI verification; this ticket is backend ledger + `log_batch_id` scoping only.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/agent.py` | Per-hop ledger open/close helpers; wire into `do_task` for `run_next` chains; mirror **AST-515** `run_adhoc_workbench_test` pattern | core |
| `src/core/dispatcher.py` | Split **entity claim** `batch_id` from **hop audit** `log_batch_id`; skip dispatch-level ledger when current `agent_task.run_next` is set | core |
| `src/core/candidate.py` | `run_craft_generate_with_ledger`: skip outer ledger when task has `run_next` (hops owned by `do_task`) | core |
| `src/core/boards.py` | Same as candidate for board UI generate wrapper when `run_next` set | core |
| `tests/component/core/test_agent.py` | Two-hop chain: assert two `save_dispatch_ledger` / two `update_dispatch_ledger` with distinct `batch_id` and correct `task_key` | tests |

No changes to `src/ui/api/api_admin.py`, `AdminPerformanceMonitor.tsx`, or `database.py` schema (no chain-grouping columns per parent open Q #3).

---

## Stage 1: Per-hop ledger helpers in `agent.py`

**Done when:** Private helpers exist and are unit-testable in isolation; `do_task` not wired yet.

1. Near `run_adhoc_workbench_test` (after existing imports: `uuid`, `datetime`, `database`, `compute_batch_cost`), add:

```python
def _current_agent_task_run_next(task_key: str) -> str:
    """Return stripped run_next from current agent_task row, or ''."""
    _, row = _resolve_task_prompts(task_key)
    return (row.get("run_next") or "").strip()

def _in_run_next_chain(*, chain_context: Optional[Dict[str, str]], task_key: str, agent_task_row: Dict[str, Any]) -> bool:
    """True when this do_task invocation is a run_next hop (child or entry with a planned next hop)."""
    if (chain_context or {}).get("_hop_parent_task_key"):
        return True
    return bool((agent_task_row.get("run_next") or "").strip())
```

2. Add `_open_run_next_hop_ledger(task_key, candidate_id, entity_type, batch_size=1) -> str`:
   - `hop_batch_id = f"{task_key}-{uuid.uuid4()}"`
   - `started_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")`
   - `database.save_dispatch_ledger(hop_batch_id, task_key, candidate_id, started_at, status="RUNNING", entity_type=entity_type, batch_size=batch_size)`
   - `log_batch_id.set(hop_batch_id)`
   - Return `hop_batch_id`

3. Add `_finalize_run_next_hop_ledger(hop_batch_id, *, success: bool, batch_size: int = 1) -> None`:
   - `completed_at` same format as started_at
   - `total_cost = compute_batch_cost(hop_batch_id)`
   - On `success`: `update_dispatch_ledger(..., status="COMPLETED", total_processed=1, total_passed=1, total_failed=0, total_errors=0, total_cost=total_cost, entity_cost=total_cost, completed_at=completed_at)`
   - On failure: `update_dispatch_ledger(..., status="FAILED", total_processed=1, total_passed=0, total_failed=1, total_errors=0, total_cost=total_cost, entity_cost=total_cost, completed_at=completed_at)`
   - Do **not** call `log_batch_id.set(None)` here when a child hop will run immediately after — caller clears only when chain ends or on exception path.

4. Add module-level comment above helpers: **AST-531** — Execution History one row per executed `run_next` hop; entity-batch dispatch still uses a separate claim `batch_id` (dispatcher), not commingled with hop audit rows.

⚠️ **Decision:** `dispatch_ledger.task_key` is the **hop** `task_key` (e.g. `anticipate_scan`, `contemplate_job`), not `adhoc-*` and not the Susan-clicked dispatch row — matches acceptance “correct task key in Task column” and parent Q #2 (no entry summary row).

---

## Stage 2: Wire per-hop ledger inside `do_task`

**Done when:** A two-hop `run_next` chain creates two ledger rows with distinct `batch_id` values; single-hop `do_task` without `run_next` unchanged when outer `log_batch_id` already set.

1. In `do_task`, immediately after `agent_row, agent_task_row = _resolve_task_prompts(task_key)` (before `chain_entry = _is_chain_entry(...)`):
   - `planned_next = (agent_task_row.get("run_next") or "").strip()` (keep existing later read; hoist one copy for ledger gate).
   - `in_chain = _in_run_next_chain(chain_context=chain_context, task_key=task_key, agent_task_row=agent_task_row)`
   - `hop_ledger_batch_id: Optional[str] = None`
   - If `in_chain`:
     - `entity_type_hop = _effective_entity_type(task_config, index)` — call `_effective_entity_type` only after `task_config = TASK_CONFIG[task_key]` is loaded (move this block to after `task_config` assignment if needed; today `task_config` is loaded earlier at line ~1008 — place open after `task_config` exists).
     - `candidate_id_ledger = (ctx.get("astral_candidate_id") if ctx else None) or ""`
     - If not `candidate_id_ledger`: log warning and skip hop ledger (fail closed: no ledger row without candidate — same as dispatch tasks today).
     - Else: `hop_ledger_batch_id = _open_run_next_hop_ledger(task_key, candidate_id_ledger, entity_type_hop, batch_size=ctx.get("batch_size", 1) if ctx else 1)`

2. Replace `batch_id = log_batch_id.get()` (current ~1142) with:
   - `batch_id = hop_ledger_batch_id or log_batch_id.get()`
   - All `_store_prompt_blocks`, `_store_response_block`, `append_agent_response`, and timesheet paths continue using this `batch_id`.

3. On every **early return** from `do_task` after hop ledger was opened (validation failures after open, caller-token guard, API failure, schema failure): call `_finalize_run_next_hop_ledger(hop_ledger_batch_id, success=False)` then `log_batch_id.set(None)` in a `try`/`finally` scoped to that return path, OR use a single `try`/`finally` wrapping the LLM+storage tail — prefer one `try`/`finally` around the block from first `_open_run_next_hop_ledger` through success/fail return so early returns after open always finalize.

4. On **success path** before `if not effective_next:` return (leaf hop, no further `run_next`):
   - If `hop_ledger_batch_id`: `_finalize_run_next_hop_ledger(hop_ledger_batch_id, success=True)`; `log_batch_id.set(None)`.

5. On **success path** before `await do_task(effective_next, ...)` (parent hop, chain continues):
   - If `hop_ledger_batch_id`: `_finalize_run_next_hop_ledger(hop_ledger_batch_id, success=True)` — parent hop closed before child opens its own ledger.
   - `log_batch_id.set(None)` before inner `await do_task(...)` so child `_open_run_next_hop_ledger` sets a fresh id.

6. On **inner failure** (`not inner.get("success")`): child hop finalizes inside child `do_task`; parent already finalized at step 5 — return inner dict unchanged.

7. Remove or update log line `_log_chain_entry(task_key, log_batch_id.get())` to log the hop-local `batch_id` after open.

8. **Do not** change `run_next` recursion kwargs (`live_content`, `index`, `ctx`, `chain_context` merge) — AST-529 / AST-304 stay as-is.

⚠️ **Decision:** Mid-chain hops that never run (chain aborted) get **no** ledger row — only hops that entered `do_task` and opened a ledger (parent Q #4). Dispatcher must not pre-create an entry row.

---

## Stage 3: Dispatcher — entity batch vs hop audit

**Done when:** Manual **Run** on a dispatch task with `run_next` produces hop rows only (no duplicate entry row); single-hop dispatch (empty `run_next`) still has one Execution History row tied to the dispatch run.

1. In `_dispatch_one` (`src/core/dispatcher.py`), after `task_key` / `candidate_id` known and before `save_dispatch_ledger`:
   - `from src.core.agent import _current_agent_task_run_next` (or duplicate minimal DB read in dispatcher — prefer import of helper from agent to avoid drift).
   - `has_run_next_chain = bool(_current_agent_task_run_next(task_key))`
   - `entity_batch_id = f"{task_key}-{uuid.uuid4()}"` — **always** generated for claim/release paths.
   - If `has_run_next_chain`:
     - **Do not** call `save_dispatch_ledger` or `log_batch_id.set`.
     - Pass `entity_batch_id` into `_run_dispatch_loop` / `_run_unified` via `ctx` key `entity_batch_id` (add to `ctx` dict copy at start of `_dispatch_one`: `ctx = {**ctx, "entity_batch_id": entity_batch_id}`).
   - Else (no `run_next`):
     - Keep today’s behavior: `save_dispatch_ledger(entity_batch_id, ...)`, `log_batch_id.set(entity_batch_id)` — `entity_batch_id` remains the audit batch for the whole dispatch thread.

2. In `_run_unified`, replace `bid = log_batch_id.get()` for **entity claim** with:
   - `bid = (ctx.get("entity_batch_id") or log_batch_id.get())`
   - Use `bid` only for `claim_*_batch` / `clear_*_batch` / consult `batch_id` parameter — not for hop audit.

3. In `_dispatch_one` `finally` block: wrap `update_dispatch_ledger(batch_id, ...)` so it runs **only when** `not has_run_next_chain` (dispatch-level ledger was created). Hop chains finalize inside `do_task`.

4. Mid-run `database.update_dispatch_ledger(batch_id, **accumulated)` inside `_run_dispatch_loop` — same guard: only when dispatch-level ledger exists.

⚠️ **Decision:** Entity locking stays one `entity_batch_id` per Susan **Run** click; Execution History shows N hop rows for N executed LLM hops. Consult batch paths without `run_next` keep one dispatch ledger row per thread.

---

## Stage 4: UI craft / board wrappers

**Done when:** Artifact **Generate** and board **Generate** for tasks with `run_next` do not create a duplicate outer ledger row; single-hop generate unchanged.

1. In `src/core/candidate.py` `run_craft_generate_with_ledger` (~line 517):
   - Before `save_dispatch_ledger`, `if _current_agent_task_run_next(task_key):` then skip outer ledger + `log_batch_id.set`; call `do_task` directly inside existing try/finally (still `flush_log_buffer` in finally).
   - Else keep existing outer ledger wrapper.

2. In `src/core/boards.py` board generate function (~line 497): same guard as candidate.

3. API responses that return `batch_id` today: when outer ledger skipped, return `result.get("batch_id")` from final hop if added to result, or omit — **minimal change:** return last `log_batch_id` from successful `do_task` only if needed for UI; if no field today on craft response except existing `batch_id` key, set `batch_id` to the **final hop’s** `log_batch_id` by reading `log_batch_id.get()` after `do_task` returns (child hop wins). Document in build stage comment only; do not change response shape beyond using final hop id when outer skipped.

---

## Stage 5: Tests

**Done when:** Component test proves two-hop chain issues two distinct ledger inserts; existing agent tests still pass.

1. In `tests/component/core/test_agent.py`, add `test_do_task_run_next_two_hop_ledger_rows`:
   - Patch `database.save_dispatch_ledger`, `database.update_dispatch_ledger`, `send_to_anthropic` (or provider path) to succeed for two task keys `hop_a` / `hop_b`.
   - Stub `_resolve_task_prompts` or seed TASK_CONFIG + agent_task rows: `hop_a.run_next = hop_b`, `hop_b.run_next = ''`.
   - `asyncio.run(do_task("hop_a", ...))` with minimal ctx (`astral_candidate_id`, `candidate_api_key`).
   - Assert `save_dispatch_ledger` called twice with different first arg (`batch_id`) and task_key args `hop_a` then `hop_b`.
   - Assert two `update_dispatch_ledger` with `status` COMPLETED or FAILED per hop.

2. Add `test_do_task_single_hop_preserves_outer_log_batch_id`:
   - Pre-set `log_batch_id.set("outer-batch-123")`, task with empty `run_next`, mock API success.
   - Assert `save_dispatch_ledger` **not** called from hop open (only outer id used for storage mocks if any).

---

## Self-Assessment

**Scope — `scope-MAJOR-CHANGE`**  
Touches `do_task` orchestration, dispatcher batch/audit split, and two UI generate wrappers — every `run_next` chain site (consult, roster, artifacts, scheduled dispatch) flows through `do_task`.

**Conf — `conf-Medium`**  
**AST-515** provides a clear per-call ledger template; the subtle part is separating dispatcher **entity** `batch_id` from hop **audit** `batch_id` without breaking consult batch locking.

**Risk — `risk-HIGH`**  
Wrong batch scoping commingles prompts/logs (acceptance #2–#3) or duplicates/missing rows; blocks **AST-528** UAT and **AST-532** UI verification.

---

## Self-review vs ASTRAL_CODE_RULES

| Rule | Check |
|------|-------|
| §1.3 DRY | Hop open/close centralized in two helpers; no copy in candidate/boards beyond one-line skip guard. |
| §2.1 config | No new magic numbers; hop detection from DB `run_next` + existing `chain_context` keys. |
| §2.4 batch | **Entity** claim `batch_id` unchanged for dispatch; **hop** `batch_id` per LLM hop for audit/agent_data/app_log only. |
| §2.6 state machine | No job/company state transitions added. |
| §3.3 imports | Dispatcher → agent helper import is core→core; data via existing `database` in agent. |
| §3.5 naming | `hop_batch_id` / `entity_batch_id` locals distinguish roles. |

No unresolved conflicts requiring `conf-!!-NONE`.

---

## Execution contract (developer)

- Stages in order; one commit per stage on `dev-ada`, cherry-pick to `origin/sub/AST-528/AST-531-per-hop-dispatch-ledger` per **build-astral**.
- Out-of-scope: **AST-527** logging, **AST-529** caller tokens, **AST-313** prompts, **AST-532** UI.
- Manual verify after Stage 2+3: manual **Run** on `anticipate_scan` → `contemplate_job` chain; Execution History shows two rows with distinct batch ids; inspect each row’s agent_data blocks — no cross-hop commingling.

---

## Review (build)

| Field | Value |
|-------|-------|
| Branch | `origin/sub/AST-528/AST-531-per-hop-dispatch-ledger` |
| Commit | _(published via Joan after build commit)_ |
| Scope | Stages 1–4 implemented; Stage 5 tests deferred to Betty (`qa-astral`) per build-astral test-tree ban |

---

## Resolution (2026-05-29, resolve-astral)

| Radia item | Action |
|------------|--------|
| **discuss — AST-529 co-ship** | **Co-ship on this sub ref** per Susan resolve direction: `CALLER_HOP_TOKEN_NAMES`, mid-chain caller hard-fail, `_chain_context` `_hop_*` stripping, and hop-boundary logging stay on `origin/sub/AST-528/AST-531-per-hop-dispatch-ledger` with per-hop ledger work. **AST-529** remains the Linear ticket for caller-token acceptance; residual AST-529-only scope (if any) is tracked there after parent UAT — not split to a second publish ref for this epic. |
| **discuss — `_dispatch_one` lazy import** | Moved `_current_agent_task_run_next` to module-level import in `dispatcher.py` (core→core; no `agent`→`dispatcher` cycle). |
| **advisory — hop ledger without `astral_candidate_id`** | Unchanged warn-and-skip; production `run_next` dispatch paths always pass `astral_candidate_id` in ctx (manual UAT on consult/roster chains). |
| **advisory — FAILED mid-chain test** | Deferred; Betty manifest covers two-hop COMPLETED path; optional FAILED-hop component test left for parent UAT if needed. |

**Publish:** `origin/sub/AST-528/AST-531-per-hop-dispatch-ledger` after resolve commit. **§9a:** clean vs `origin/dev` and `origin/ftr/AST-528-per-hop-execution-history`.
