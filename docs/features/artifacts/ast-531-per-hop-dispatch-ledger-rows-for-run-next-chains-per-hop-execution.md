<!-- linear-archive: AST-531 archived 2026-06-23 -->

## Linear archive (AST-531)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-531/per-hop-dispatch-ledger-rows-for-run-next-chains-per-hop-execution  
**Status at archive:** Done  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-528 — Per-hop Execution History for daisy-chained tasks  
**Blocked by / blocks / related:** parent: AST-528; blocks: AST-532

### Description

## What this implements

Each `run_next` hop in a daisy chain gets its own `dispatch_ledger` row with a distinct batch identifier, scoped `agent_data` / audit storage, and app log association for that hop's execution window. Applies to **all** `run_next` chains (consult, roster, artifacts, scheduled dispatch). No parent/summary row for the entry task Susan clicked — only rows for hops that actually executed.

## Acceptance criteria

1. After a manual **Run** on a dispatch task whose chain includes at least two hops (e.g. `anticipate_scan` → `contemplate_job`), Execution History lists **separate rows** for each executed hop, each showing the correct task key in the Task column.
2. Opening prompt/response inspection on the `anticipate_scan` row shows that hop's prompt blocks and model response only; opening inspection on the `contemplate_job` row shows that hop's content only — no commingling of prior-hop blocks under one batch view.
3. Expanding app logs on each hop row shows log lines for that hop's execution window, not the entire chain under the entry task row only.
4. Each hop row reports its own status (RUNNING / COMPLETED / FAILED) and cost; a failure on a mid-chain hop does not appear as success on that hop's row.

## Boundaries

* Does **not** change console/server debug logging — **AST-527**.
* Does **not** fix caller-token propagation — **AST-529**.
* Does not author prompts or `run_next` wiring — **AST-313**.
* Frontend polish and regression verification for Execution History UI is **AST-532** (sibling).

## Notes for planning

* **AST-303** intentionally used one batch id across hops; this ticket **reverses that for Execution History** — do not revert to one row per chain.
* Reference **AST-515** ad-hoc workbench test ledger pattern (one inspectable row per LLM call).
* Hot files: `src/core/agent.py`, `src/core/dispatcher.py`, `src/data/database.py`, possibly `src/ui/api/api_admin.py`.
* Rows appear individually — no chain grouping metadata required (parent open Q #3).

## Git branch (authoritative)

Per `orientation-astral` **§ Branch law**: parent `ftr/AST-528-per-hop-execution-history`, child `sub/AST-528/AST-531-per-hop-dispatch-ledger`. Created at **dispatch-linear**.

### Comments

#### radia — 2026-05-30T00:38:56.244Z
**Review** (`origin/dev`…`origin/sub/AST-528/AST-531-per-hop-dispatch-ledger`)

### What's solid
- **Plan fidelity (Stages 1–4):** `_open_run_next_hop_ledger` / `_finalize_run_next_hop_ledger`, `batch_id = hop_ledger_batch_id or log_batch_id.get()`, parent hop finalized before child `do_task`, `log_batch_id` cleared between hops — matches AST-515 one-row-per-call pattern and acceptance #1–#4 intent.
- **§2.4 batch split:** `_dispatch_one` always sets `ctx["entity_batch_id"]`; dispatch-level `save_dispatch_ledger` / `update_dispatch_ledger` / `monitor.auto_run_error` gated when `has_run_next_chain`; `_run_unified` claims with `entity_batch_id` only. Component test `test_run_next_chain_skips_dispatch_level_ledger` covers the skip path.
- **UI wrappers:** `candidate.py` / `boards.py` skip outer ledger when `run_next` set; `batch_id` in API response falls back to final hop via `log_batch_id.get()` — aligns with plan Stage 4.
- **Tests:** `TestAst531RunNextHopLedger` — two-hop `qualify_job_listings` → `evaluate_jd` asserts two distinct ledger `batch_id`s, hop `task_key`s, COMPLETED updates, `log_batch_id` cleared. Bible §7.13zm documents manifest.

### discuss
- **AST-529 scope in this diff (§5d):** Ticket boundary says caller-token propagation is **AST-529**, but this branch also adds `CALLER_HOP_TOKEN_NAMES`, `_mid_chain_empty_caller_tokens` hard-fail, `_chain_context` stripping `_hop_*` keys, `resolve_tokens` `chain_entry` / `parent_caller_summary` logging, and hop-boundary logs. Substantive sibling work — confirm Susan approved co-ship on AST-531 vs split before UAT, or track residual AST-529 acceptance separately.
- **`_dispatch_one` lazy import (§3 / B1):** `from src.core.agent import _current_agent_task_run_next` inside the function has no in-code rationale; prefer module-top import or a one-line comment if kept lazy to avoid cycles.

### advisory
- **Hop ledger without `astral_candidate_id`:** Warn-and-skip leaves `batch_id` on outer `log_batch_id` (entity claim id) for that hop’s `agent_data` — acceptable only if that path cannot occur for production `run_next` dispatch; worth a manual check on consult/roster chains.
- **No `try/finally` around hop open:** `_close_hop_ledger` on known return paths is thorough; an uncaught exception after `_open_run_next_hop_ledger` could leave a RUNNING row (pre-existing class of risk, not introduced uniquely here).
- **Minor:** `agent_performance: {}` backfill on strict batch consult path is outside AST-531 plan stages — harmless if intentional fix from test manifest.
- **Coverage gap:** No component test asserting FAILED hop ledger on mid-chain API/validation failure (acceptance #4) — optional before parent UAT.

**Verdict:** Per-hop ledger mechanics look correct for happy path and sibling **AST-532** UI work; resolve AST-529 bundling question before treating AST-529 as Done.

#### ada — 2026-05-30T00:36:46.301Z
[check-linear]

**Session scope:** Parent **AST-528** / **Astral Artifacts** — assigned **AST-531**.

**§0a:** `dev-ada` @ `/Users/susan/chuckles/astral-ada`; `git fetch origin`, `merge origin/dev` — already up to date. Gate: **BEHIND=0**, `origin/dev` ancestor of **HEAD** (`9f1dfc12`).

**§0b:** `@ada` issue search (Team Astral + **Astral Artifacts** project). Full threads on **AST-531**, parent **AST-528**, sibling **AST-532**.

**§2:** **0** actionable comments — nothing `@ada` or directed at Ada needing reply or small fix after Ada’s **Tests Passed** post (`0bbbc0ee`). Katherine’s AST-532 build-pause note (plan-only publish ref) is superseded by product on **`origin/sub/AST-528/AST-531-per-hop-dispatch-ledger` @ `634707cc`**.

**Pipeline:** **Tests Passed** — inbox quiet; next gate is **`review-astral`** (not invoked from this pass). No `build-astral` / `test-astral` / `resolve-astral`.

#### ada — 2026-05-30T00:35:47.364Z
**Tests Passed** — Betty manifest green after product fix.

**Fix:** `fix(AST-531): add CALLER_HOP config symbols` — `CALLER_HOP_TOKEN_NAMES`, `_caller_key_status_line`, `resolve_tokens` hop kwargs (AST-527 parity) so `agent.py` imports and `do_task` token resolution work on the sub branch.

**Manifest:**
1. `./scripts/testing/run_component_tests.sh tests/component/core/test_agent.py::TestAst531RunNextHopLedger` — **pass** (2/2)
2. `./scripts/testing/run_component_tests.sh tests/component/core/test_dispatcher.py::TestDispatchOne::test_run_next_chain_skips_dispatch_level_ledger` — **pass** (pytest node; script also runs frontend vitest suite)

**Publish:** `origin/sub/AST-528/AST-531-per-hop-dispatch-ledger` @ `634707cc`

#### betty — 2026-05-30T00:32:12.812Z
**Bible shasum** on `origin/sub/AST-528/AST-531-per-hop-dispatch-ledger`: `a432caf70569246cace1a2d20c8aca449b801b19`

#### betty — 2026-05-30T00:32:08.323Z
**Product fix before manifest:** `origin/sub/AST-528/AST-531-per-hop-dispatch-ledger` @ `247d9033` — `src/core/agent.py` imports `CALLER_HOP_TOKEN_NAMES` / `_TOKEN_RE` from `src/utils/config.py`, but that sub branch has no AST-530 config symbols. Pytest collection fails with `ImportError` until Ada lands the missing config (or removes accidental AST-530 hunks from the AST-531 build commit). AST-527 ftr has the config; not merged to this sub yet.

**QA test manifest** (`origin/sub/AST-528/AST-531-per-hop-dispatch-ledger` @ `ca6306cd`):

1. `./scripts/testing/run_component_tests.sh tests/component/core/test_agent.py::TestAst531RunNextHopLedger`
2. `./scripts/testing/run_component_tests.sh tests/component/core/test_dispatcher.py::TestDispatchOne::test_run_next_chain_skips_dispatch_level_ledger`

**Bible:** `docs/ASTRAL_TEST_BIBLE.md` §7.13zm — shasum on publish ref: `$(git show origin/sub/AST-528/AST-531-per-hop-dispatch-ledger:docs/ASTRAL_TEST_BIBLE.md | shasum | awk '{print $1}')` (run locally after fetch).

**Coverage intent:** Two-hop `run_next` → two distinct `save_dispatch_ledger` rows with hop `task_key`s; single-hop `do_task` with outer `log_batch_id` does not open hop ledger; dispatch **Run** on a task with planned `run_next` skips dispatch-level ledger row (hop rows only from `do_task`).

#### ada — 2026-05-30T00:25:42.245Z
[check-linear]

**Session scope:** Parent **AST-528** / **Astral Artifacts** — assigned **AST-531**.

**§0a:** `dev-ada` @ `/Users/susan/chuckles/astral-ada`; `git fetch origin`, `merge origin/dev` — already up to date. Gate: **BEHIND=0**, `origin/dev` ancestor of **HEAD** (`32da2acb`).

**§0b:** `@ada` issue search (Team Astral + **Astral Artifacts** project); union with assignee-me in session project. Full threads on **AST-531**, parent **AST-528**, sibling **AST-532**, and other @ada / assignee hits (**AST-313**, **AST-530**, …).

**§2:** **0** actionable comments — nothing `@ada` or directed at Ada needing reply or small fix after Ada’s plan doc post (`590e18a0`).

**Pipeline:** **Plan Approved** — no comment inbox work. Publish ref unchanged: `origin/sub/AST-528/AST-531-per-hop-dispatch-ledger` @ `3287b80e`. Next gate is **`build-astral`** (not invoked from this pass).

#### ada — 2026-05-30T00:24:21.953Z
Plan doc: https://github.com/susansomerset/astral/blob/sub/AST-528/AST-531-per-hop-dispatch-ledger/docs/features/artifacts/ast-531-per-hop-dispatch-ledger-rows-for-run-next-chains-per-hop-execution.md

**Self-assessment**
- **Scope:** MAJOR-CHANGE — `do_task` hop ledger, dispatcher entity/audit split, craft/board wrappers.
- **Conf:** Medium — AST-515 pattern is clear; dispatcher `entity_batch_id` vs hop `log_batch_id` needs care.
- **Risk:** HIGH — wrong batch scoping breaks per-hop inspection and blocks AST-528 UAT.

Published @ `3287b80e` on `origin/sub/AST-528/AST-531-per-hop-dispatch-ledger`.

---

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
