# AST-515 — Ad hoc workbench Test runs in Execution History

**Linear:** https://linear.app/astralcareermatch/issue/AST-515/ad-hoc-workbench-test-runs-in-execution-history-include-ad-hoc-calls  
**Parent:** https://linear.app/astralcareermatch/issue/AST-514/include-ad-hoc-calls-from-ui-in-execution-history  
**Feature ref:** `sub/AST-514/AST-515-ad-hoc-workbench-test-runs-in-execution-history` (origin only)

Wire **Anthropic Ad Hoc** workbench **Test** (`POST /api/admin/adhoc/test`) so each real provider call creates a `dispatch_ledger` row, attaches logs via `log_batch_id`, and persists prompt/response `agent_data` blocks — matching dispatch/craft audit behavior. **Preview** (`POST /api/admin/adhoc/preview`) stays read-only with no ledger row.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/agent.py` | Add `run_adhoc_workbench_test` (ledger + `log_batch_id` + `agent_data` around existing `run_adhoc`) | core |
| `src/ui/api/api_admin.py` | `adhoc_test` calls `run_adhoc_workbench_test` instead of bare `run_adhoc` | ui |
| `tests/component/core/test_agent.py` | Unit tests for ledger/agent_data on success, failure, and exception paths | tests |
| `tests/component/ui/api/test_api_admin.py` | Point adhoc test mocks at `run_adhoc_workbench_test`; assert preview still does not create ledger | tests |

No changes to `AdminPerformanceMonitor.tsx`, `BatchAgentDataModal.tsx`, or `/api/admin/dispatch_ledger` — they already list by `task_key`, expand logs by `batch_id`, and load blocks from `/api/agent_data/<batch_id>`.

---

## Stage 1: Core — `run_adhoc_workbench_test`

**Done when:** A new async function in `src/core/agent.py` wraps `run_adhoc` with batch lifecycle; `adhoc/preview` is untouched; no UI changes.

1. At top of `run_adhoc` section (before `run_adhoc`), add imports via existing pattern: `from src.data import database` (same as `candidate.py` — do not add new `database` calls in `api_admin.py`).

2. Add `async def run_adhoc_workbench_test(...)` immediately above `run_adhoc`, with the **same keyword parameters** as `run_adhoc` plus required:
   - `workbench_task_key: str` — workbench selection (e.g. `evaluate_jd`)
   - `candidate_id: str` — from `_resolve_adhoc`
   - `entity_id: Optional[str]` — optional; used only for failure RESPONSE prefix (same as `do_task` `index`)

3. Inside the function, define:
   - `ledger_task_key = f"adhoc-{workbench_task_key}"` (Execution History **Task** column)
   - `batch_id = f"{ledger_task_key}-{uuid.uuid4()}"` (readable + unique per §2.4 batch_id prefix rule)
   - `entity_type = (TASK_CONFIG.get(workbench_task_key) or {}).get("entity_type") or "candidate"` — `agent_data` requires a non-empty entity_type; workbench always has a selected candidate
   - `started_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")`
   - `completed_at` helper: same format when closing the row

4. Before the API call:
   - `database.save_dispatch_ledger(batch_id, ledger_task_key, candidate_id, started_at, status="RUNNING", entity_type=entity_type, batch_size=1)`
   - `log_batch_id.set(batch_id)`

5. In a `try` / `finally`:
   - `finally`: `log_batch_id.set(None)` always
   - `try`: `result = await run_adhoc(...)` passing through all prompt/provider kwargs unchanged

6. After `run_adhoc` returns, persist **agent_data** (best-effort, same try/except swallow pattern as `do_task`):
   - Call `_store_prompt_blocks(entity_type=entity_type, task_key=workbench_task_key, batch_id=batch_id, system_content=..., cache_content=cache_content or None, nocache_content=nocache_content, user_content=user_content, live_content=live_content)` using the **same string arguments** passed into `run_adhoc` (not re-resolved from DB).
   - On failure (`not result.get("success")`): build audit body with `_audit_response_body` from `result` (mirror `do_task` failure path); `_store_response_block(entity_type, workbench_task_key, batch_id, _failure_response_block_data(entity_id, audit_body), index=entity_id)`.
   - On success: extract display text — if `parsed_response` is a `dict` with `agent_payload`, use that string; else `str(parsed_response)`; `_store_response_block(..., response_text, index=entity_id)`.

7. Close the ledger row **before** returning to the API layer:
   - `total_cost = compute_batch_cost(batch_id)` (existing function in this module)
   - If `result.get("success")`: `database.update_dispatch_ledger(batch_id, status="COMPLETED", completed_at=completed_at, total_processed=1, total_passed=1, total_failed=0, total_errors=0, total_cost=total_cost)`
   - Else: `database.update_dispatch_ledger(batch_id, status="FAILED", completed_at=completed_at, total_processed=1, total_passed=0, total_failed=1, total_errors=0, total_cost=total_cost)`
   - On **exception** around `run_adhoc`: `database.update_dispatch_ledger(batch_id, status="FAILED", completed_at=started_at, total_processed=1, total_failed=0, total_errors=1)` then re-raise (API still returns 500)

8. Return the same `result` dict shape `run_adhoc` returns today (no new required JSON fields for the workbench UI).

9. Update the `run_adhoc` docstring comment block header from `# run_adhoc — workbench / ad-hoc calls (no agent_data storage)` to note that **workbench Test** uses `run_adhoc_workbench_test`; bare `run_adhoc` remains storage-free for any other callers.

⚠️ **Decision:** Implement audit in **`agent.py`** (not `candidate.py`) because `run_adhoc`, `_store_prompt_blocks`, and `_store_response_block` already live here — avoids duplicating block-storage logic or pulling UI resolution into core.

⚠️ **Decision:** Store `agent_data` with **workbench** `task_key` (`evaluate_jd`), while `dispatch_ledger.task_key` is **`adhoc-<task_key>`** — UI Task column reads ledger; inspection uses batch_id only.

---

## Stage 2: API — wire `adhoc_test`

**Done when:** `POST /api/admin/adhoc/test` uses the wrapper; `POST /api/admin/adhoc/preview` unchanged.

1. In `src/ui/api/api_admin.py`, change the import line from `from src.core.agent import run_adhoc, ...` to import `run_adhoc_workbench_test` (keep `run_adhoc` only if still referenced elsewhere in the file — if not, drop it).

2. In `adhoc_test`, replace `asyncio.run(run_adhoc(...))` with:

```python
result = asyncio.run(run_adhoc_workbench_test(
    workbench_task_key=task_key,
    candidate_id=resolved["candidate_id"],
    entity_id=entity_id or None,
    system_content=resolved["system"],
    user_content=resolved["user"],
    cache_content=resolved["cache"] or None,
    nocache_content=resolved["nocache"] or None,
    live_content=live_content,
    response_format=task_response_format,
    model_code=resolved["model_code"],
    tier_meta=resolved.get("tier_meta"),
    temperature=resolved["temperature"],
    max_tokens=resolved["max_tokens"],
    api_key_override=resolved["api_key_override"],
    task_key_uuid=resolved["task_key_uuid"],
))
```

3. Leave exception handling and `success` / `hydrated` response shaping **unchanged** after the call.

4. Do **not** call `run_adhoc_workbench_test` from `adhoc_preview`.

---

## Stage 3: Tests

**Done when:** Component tests pass; Betty manifest note below is satisfied for `qa-astral`.

1. In `tests/component/core/test_agent.py`, add tests for `run_adhoc_workbench_test` with monkeypatched `database.save_dispatch_ledger`, `update_dispatch_ledger`, `run_adhoc`, `_store_prompt_blocks`, `_store_response_block`, and `compute_batch_cost`:
   - Success: ledger `COMPLETED`, `total_passed=1`, blocks stored, `log_batch_id` cleared in `finally`
   - `success: False`: ledger `FAILED`, failure RESPONSE stored
   - Exception from `run_adhoc`: ledger `FAILED` with `total_errors=1`, exception propagates

2. In `tests/component/ui/api/test_api_admin.py`, change adhoc test monkeypatches from `run_adhoc` to `run_adhoc_workbench_test` (same return shapes). Add one assertion that `adhoc_preview` does **not** call `save_dispatch_ledger` (monkeypatch `database.save_dispatch_ledger` on admin module path or patch via `agent` if imported).

3. Run:

```bash
cd /Users/susan/chuckles/astral-ada && python -m pytest tests/component/core/test_agent.py -k adhoc_workbench -q
cd /Users/susan/chuckles/astral-ada && python -m pytest tests/component/ui/api/test_api_admin.py -k adhoc -q
```

**Betty manifest (for `qa-astral`, not run in build):** extend coverage for `api_admin` adhoc routes, `agent` storage helpers, ledger list/detail if new DB helpers are added (none expected beyond existing `save_dispatch_ledger` / `update_dispatch_ledger`).

---

## Stage 4: Manual verification (Susan / UAT on parent)

**Done when:** Acceptance criteria 1–6 on AST-515 are observable in Execution History.

1. Select a candidate with timezone set; open **Execution History** (today filter).
2. **Anthropic Ad Hoc** → pick task `evaluate_jd`, entity, run **Test** (real call) → new row with **Task** `adhoc-evaluate_jd`, terminal success, cost if billed, counts `1/1/0/0`.
3. Force a failure (invalid key or bad payload) → row with **Task** `adhoc-…`, status **FAILED**, not missing.
4. Expand row → log lines present when the run logged.
5. Open prompt inspection (batch link / modal) → SYSTEM / CACHE / TASK / RESPONSE blocks populated.
6. **Preview** only → no new row.
7. Confirm an older dispatch row still shows plain task name (no `adhoc-` prefix) and still expands/inspects.

---

## Self-Assessment

**Scope:** `scope-Single-Component` — Core wrapper in `agent.py`, one API route swap, and focused component tests; no Execution History UI or dispatcher scheduler changes.

**Conf:** `conf-Medium` — Patterns are established in `candidate.run_candidate_artifact_generation` and `do_task` storage, but adhoc uses pre-resolved prompt strings and dual providers (Anthropic/DeepSeek) through `run_adhoc`.

**Risk:** `risk-Medium` — Execution History and `agent_data` are operator-critical; incorrect ledger updates could clutter or hide runs, but dispatch-only rows are untouched.

---

## Review (build)

**Branch:** `sub/AST-514/AST-515-ad-hoc-workbench-test-runs-in-execution-history`  
**Build commit:** `9cbaefae` on `origin/sub/AST-514/AST-515-ad-hoc-workbench-test-runs-in-execution-history`

**Implemented:**
- `run_adhoc_workbench_test` in `src/core/agent.py` — ledger + `log_batch_id` + agent_data around `run_adhoc`
- `adhoc_test` in `src/ui/api/api_admin.py` calls the wrapper; preview unchanged

**Pending:** Betty component tests per Stage 3 plan (`qa-astral`).

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Plan compliance |
|------|-----------------|
| §1.3 DRY | Reuses `_store_prompt_blocks`, `_store_response_block`, `compute_batch_cost`, `run_adhoc` — no parallel storage implementation |
| §2.1 config | `entity_type` from `TASK_CONFIG`; ledger task_key prefix is ticket-specified, not a new config block |
| §2.4 batch | `batch_id` + `log_batch_id` + ledger save/update + `batch_size=1` |
| §2.6 state machine | N/A — no entity state transitions |
| §3.3 imports | Ledger writes in **core** only; API calls core wrapper |
| §3.5 naming | `run_adhoc_workbench_test` matches `run_candidate_artifact_generation` naming |

No `conf-!!-NONE` conflicts.

---

## Resolution

**Resolved:** 2026-05-28 (Ada)

| Radia item | Action |
|------------|--------|
| **fix-now** | None — plan fidelity and ASTRAL_CODE_RULES sign-off on `origin/sub/AST-514/AST-515-ad-hoc-workbench-test-runs-in-execution-history` @ `87b80fac`. |
| **discuss** | None. |
| **advisory** — dual `database` import style in `agent.py` | No change; matches `candidate.py` precedent. |
| **advisory** — parent UAT dispatch regression (AST-514 Stage 4) | Deferred to parent UAT (`AdminPerformanceMonitor` §7.13k); no UI diff in this child. |

**Publish ref:** `origin/sub/AST-514/AST-515-ad-hoc-workbench-test-runs-in-execution-history` · Betty manifest green · §9a clean.
