<!-- linear-archive: AST-521 archived 2026-06-15 -->

## Linear archive (AST-521)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-521/product-ui-user-prefix-in-execution-history-include-ad-hoc-calls-from  
**Status at archive:** Done  
**Project:** Astral Agent  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-514 — Include Ad Hoc calls (from UI) in Execution History  
**Blocked by / blocks / related:** parent: AST-514

### Description

## What this implements

Every **product UI button** that triggers a **real provider call** outside the dispatch runner records Execution History with **Task** = `user-<task_key>`, with the same ledger, log, cost, and prompt/response inspection parity as dispatch batches. Covers **Artifacts Generate / Regenerate** and **Board Searches** craft **Generate** (and the same pattern for future non-dispatch UI agent calls). **Dispatch** (scheduler **Auto**, background loops, and **Scheduled Actions Run**) stays **plain** `task_key`.

## Acceptance criteria

3. **Artifacts Generate / Regenerate** success → **Task** = `user-<task_key>` with full inspectability.
4. Same paths on failure → **Task** = `user-<task_key>`, terminal failure.
5. **Board Searches** craft **Generate** success/failure → **Task** = `user-<task_key>` with same inspectability.
6. Expanding in-scope `user-` rows shows logs when emitted; prompt inspection shows stored blocks for that batch.

(Parent criteria 1–2 `adhoc-` satisfied by **AST-515**. Criteria 6–7 dispatch plain / preview unchanged.)

## Boundaries

* Does not change **Anthropic Ad Hoc** workbench (**AST-515** / `adhoc-`).
* Does not change **dispatch** ledger labeling or **Scheduled Actions Run** semantics.
* **Forward-only** — no relabel of existing plain `craft_*` ledger rows.
* No retroactive backfill.
* Does not save generated content to candidate artifacts (Artifacts **Save** remains separate).
* Sibling **AST-515** is **adhoc-** only; this ticket is `user-` only.

## Notes for planning

* Primary touch: `run_candidate_artifact_generation` in `src/core/candidate.py`, `run_board_search_generation` in `src/core/boards.py` — mirror `run_adhoc_workbench_test` ledger/`log_batch_id`/`agent_data` pattern from **AST-515** (`ledger_task_key = f"user-{task_key}"`, `batch_id = f"{ledger_task_key}-{uuid}"`).
* `do_task` already stores **agent_data** when `log_batch_id` is set; verify logs and terminal ledger updates on success/failure.
* **AdminPerformanceMonitor** likely unchanged if API returns prefixed `task_key`.
* Betty manifest: candidate generate API, boards generate API, core wrappers, bible § for **user-** rows.

## Git branch (authoritative)

Per `orientation-astral` **§ Branch law**: parent `ftr/AST-514-include-ad-hoc-calls-from-ui-in-execution-history`, child `sub/AST-514/AST-521-product-ui-user-prefix-in-execution-history`. Created at dispatch.

### Comments

#### radia — 2026-05-28T23:44:48.388Z
## Radia review — `origin/sub/AST-514/AST-521-product-ui-user-prefix-in-execution-history`

**Diff:** `origin/dev...origin/sub/AST-514/AST-521-product-ui-user-prefix-in-execution-history` @ `49907d90`

**AST-521 product commits:** `321ede5e` (`run_candidate_artifact_generation`), `5308420a` (`run_board_search_generation`), `49907d90` (tests + bible §7.13zk).

Branch also carries **AST-515** rollup (`40a54c69`) — sibling already **User Testing**; not AST-521 scope. Review below is **AST-521 only** (`candidate.py`, `boards.py`, tests).

---

### Plan fidelity (Stages 1–3)

| Stage | Verdict |
|-------|---------|
| Candidate artifact Generate/Regenerate | `ledger_task_key = f"user-{task_key}"`; `batch_id` prefixed; `save_dispatch_ledger` uses `ledger_task_key`; `do_task(task_key=task_key, …)` unchanged |
| Board search craft Generate | Same pattern in `run_board_search_generation` |
| Tests | `TestRunCandidateArtifactGeneration` asserts prefixed ledger + `batch_id`; `test_boards_generate_ast521.py` covers success, failure, 404 (no ledger) |
| Boundaries | No dispatcher, UI, or `adhoc-` changes in AST-521 commits; forward-only (no relabel) per parent |

Self-Assessment **scope-minor** / **conf-high** matches the diff footprint.

---

### ASTRAL_CODE_RULES

| Rule | Verdict |
|------|---------|
| §1.3 DRY | Reuses existing wrappers; two-line prefix only |
| §2.4 batch | Prefixed `batch_id` + existing `log_batch_id` lifecycle |
| §3.3 imports | Ledger writes stay in **core**; API routes delegate unchanged |
| §3.2 UI | No frontend diff for this child (Execution History reads ledger `task_key` as-is) |
| B1 / B2 / D2 / E1 | No new violations in AST-521 hunks |

Ledger label vs storage key split (`user-*` in ledger, real `task_key` in `agent_data`) matches AST-515 precedent and plan decision.

---

### fix-now

None.

### discuss

None.

### advisory

- **Exception-path ledger counts** (`update_dispatch_ledger` on `except` without `total_errors`) — pre-existing in both wrappers; unchanged by this ticket; acceptable for forward-only UI runs.
- **Parent UAT:** confirm dispatch rows stay plain `task_key` and pre-ship plain `craft_*` rows still expand (AST-514 Stage 4 / §7.13zk note on `AdminPerformanceMonitor`).

#### betty — 2026-05-28T23:40:00.663Z
## QA test manifest (AST-521)

**Publish ref:** `origin/sub/AST-514/AST-521-product-ui-user-prefix-in-execution-history` @ `49907d90`

**`docs/ASTRAL_TEST_BIBLE.md` shasum (publish ref):** `ca12dc805704a4b23a390aaaafb5a281aab8ba642e314cd701f3c8827227c273`

Run on **`dev-ada`** after merging this **`sub/*`** tip (same as **`test-astral`**):

1. `./scripts/testing/run_component_tests.sh tests/component/core/test_candidate.py::TestRunCandidateArtifactGeneration`
2. `./scripts/testing/run_component_tests.sh tests/component/core/test_boards_generate_ast521.py::TestRunBoardSearchGenerationAst521`

**Coverage intent:** **`user-<task_key>`** ledger rows + prefixed **`batch_id`** for **`run_candidate_artifact_generation`** and **`run_board_search_generation`** (success + failure); 404 paths skip ledger. No UI diff — Execution History display unchanged; parent UAT may still run **`test_AdminPerformanceMonitor.test.tsx`** per bible **§7.13k**.

**Boundary:** dispatch / Scheduled Actions **Run** stay plain **`task_key`**; **adhoc-** remains **AST-515** only.

— Betty

#### hedy — 2026-05-28T23:35:08.051Z
[check-linear]

**Inbox (AST-521 / parent AST-514 / Astral Agent):** `@hedy` issue search (team + project), fallback scan (`updatedAt -P14D`), full thread on **AST-521** and parent **AST-514**. **0** actionable comments — nothing `@hedy` or directed at Hedy needing reply or small fix after Ada’s plan post @ `2026-05-28T23:33`.

**§0a:** `dev-hedy` @ `/Users/susan/chuckles/astral-hedy`; merged `origin/dev` cleanly — `BEHIND=0`, `origin/dev` ancestor of `HEAD`.

**Session scope:** Orchestrator assigned **AST-521**; Linear assignee **Ada**; status **Plan Approved** (plan on `origin/sub/AST-514/AST-521-product-ui-user-prefix-in-execution-history`). No publish merge or pipeline from this pass — **`build-astral`** when Ada (or reassigned engineer) picks up.

#### ada — 2026-05-28T23:35:00.427Z
[check-linear]

**Inbox (AST-521 / parent AST-514 / Astral Agent):** `@ada` issue search (team + project), fallback `-P14D` scan, full threads on **AST-521**, **AST-514**, sibling **AST-515**. **0** actionable comments — nothing `@ada` or directed at Ada needing reply or small fix after Ada’s plan post @ `2026-05-28T23:33`.

**§0a (`astral-ada` / `dev-ada`):** `git fetch origin`, `checkout dev-ada`, `merge origin/dev` — **merge-clean** (`BEHIND=0`, `origin/dev` ancestor of `HEAD`).

**Session scope:** **AST-521** only — **Plan Approved**, publish ref `origin/sub/AST-514/AST-521-product-ui-user-prefix-in-execution-history`; no `build-astral` / `test-astral` / `resolve-astral` from this pass per check-linear §6.

#### katherine — 2026-05-28T23:34:55.745Z
[check-linear]

**Inbox (session AST-521 / parent AST-514 / Astral Agent):** `@katherine` issue search (team + project), full threads on **AST-521**, **AST-514**, and Katherine-assignee roster in session project. **0** actionable comments — nothing `@katherine` or directed at Katherine needing reply or small fix after prior **AST-514** Katherine `[check-linear]` @ `2026-05-28T22:01`.

**§0a (`astral-kath` / `dev-kath`):** `git fetch origin`, `checkout dev-kath`, `merge origin/dev` — **merge-clean** (`BEHIND=0`, `origin/dev` ancestor of `HEAD`).

**Session scope:** **AST-521** only — **Plan Approved**, assignee **Ada**; publish ref `origin/sub/AST-514/AST-521-product-ui-user-prefix-in-execution-history`. No publish merge or pipeline skills from this pass (check-linear comments-only).

#### ada — 2026-05-28T23:33:41.485Z
Plan: [`docs/features/agent/ast-521-product-ui-user-prefix-in-execution-history-include-ad-hoc-calls-from-ui-in-execution-history.md`](https://github.com/susansomerset/astral/blob/sub/AST-514/AST-521-product-ui-user-prefix-in-execution-history/docs/features/agent/ast-521-product-ui-user-prefix-in-execution-history-include-ad-hoc-calls-from-ui-in-execution-history.md)

**Scope:** `scope-minor` — Two core wrappers (`run_candidate_artifact_generation`, `run_board_search_generation`) get `user-` ledger/`batch_id` prefix only; component tests; no UI or dispatcher changes.

**Conf:** `conf-high` — AST-515 established the prefix pattern; these paths already record ledger + `log_batch_id` + `do_task` agent_data.

**Risk:** `risk-Medium` — Mislabeled Task column would confuse operator audit, but dispatch and `adhoc-` paths are untouched and labeling is forward-only.

---

# AST-521 — Product UI `user-` prefix in Execution History

**Linear:** https://linear.app/astralcareermatch/issue/AST-521/product-ui-user-prefix-in-execution-history-include-ad-hoc-calls-from-ui-in-execution-history  
**Parent:** https://linear.app/astralcareermatch/issue/AST-514/include-ad-hoc-calls-from-ui-in-execution-history  
**Feature ref:** `sub/AST-514/AST-521-product-ui-user-prefix-in-execution-history` (origin only)

Prefix **Execution History Task** labels for **product UI Generate** flows (`user-<task_key>`) on Artifacts **Generate / Regenerate** and Board Searches craft **Generate**. These paths already write `dispatch_ledger` rows, set `log_batch_id`, and persist prompt/response blocks via `do_task` — this ticket only changes ledger labeling and `batch_id` prefixing to match parent AST-514. **Dispatch**, **Scheduled Actions Run**, and **Ad Hoc** (`adhoc-`, AST-515) stay unchanged.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/candidate.py` | `run_candidate_artifact_generation`: `ledger_task_key = f"user-{task_key}"`, `batch_id = f"{ledger_task_key}-{uuid}"` passed to ledger + `log_batch_id` | core |
| `src/core/boards.py` | Same prefix pattern in `run_board_search_generation` | core |
| `tests/component/core/test_candidate.py` | Assert ledger receives `user-<task_key>` and `batch_id` starts with that prefix | tests |
| `tests/component/core/test_boards_generate_ast521.py` | New: core tests for `run_board_search_generation` ledger prefix (success + failure paths) | tests |

No changes to `src/ui/api/api_candidate.py`, `src/ui/api/api_boards.py`, `AdminPerformanceMonitor.tsx`, `BatchAgentDataModal.tsx`, or dispatcher — they already surface `task_key` and `batch_id` from the ledger/API unchanged.

---

## Stage 1: Candidate artifact generation — `user-` ledger prefix

**Done when:** `POST /api/candidates/<id>/generate/<task_key>` (and Regenerate, same handler) creates ledger rows with **Task** = `user-<task_key>` and `batch_id` = `user-<task_key>-<uuid>`; `do_task` still stores `agent_data` under the real `task_key` blocks (unchanged).

1. In `src/core/candidate.py`, function `run_candidate_artifact_generation` (starts ~line 415), **after** validating the candidate exists and **before** `save_dispatch_ledger`, add:

```python
ledger_task_key = f"user-{task_key}"
batch_id = f"{ledger_task_key}-{uuid.uuid4()}"
```

2. Remove the existing line `batch_id = f"{task_key}-{uuid.uuid4()}"`.

3. Change `database.save_dispatch_ledger(...)` second positional argument from `task_key` to **`ledger_task_key`** (keep `entity_type="candidate"`, `batch_size=1`, and all other kwargs as today).

4. Leave `log_batch_id.set(batch_id)`, the `do_task(task_key=task_key, ...)` call, success/failure `update_dispatch_ledger` blocks, and JSON response shape **unchanged** (`batch_id` in the response body is still the full prefixed id).

5. Do **not** change `parse_candidate_resume`, dispatch runners, or any other caller of `do_task`.

⚠️ **Decision:** Ledger column shows **`user-<task_key>`** while `agent_data` / `do_task` keep the real **`task_key`** (same split as AST-515: ledger label vs storage key). Execution History inspection uses `batch_id` only.

⚠️ **Decision:** **Forward-only** — no migration or relabel of existing plain `craft_*` ledger rows (per parent AST-514).

---

## Stage 2: Board search craft generation — `user-` ledger prefix

**Done when:** `POST /api/boards/searches/<board_search_id>/generate/<task_key>` creates ledger rows with **Task** = `user-<task_key>` and prefixed `batch_id`; validation and `do_task` behavior unchanged.

1. In `src/core/boards.py`, function `run_board_search_generation` (starts ~line 476), **after** row/candidate validation and **before** `save_dispatch_ledger`, add the same two lines as Stage 1 (`ledger_task_key`, prefixed `batch_id`).

2. Remove `batch_id = f"{task_key}-{uuid.uuid4()}"`.

3. Pass **`ledger_task_key`** as the `task_key` argument to `save_dispatch_ledger` (not the bare craft key).

4. Leave `ctx` merge, `do_task`, ledger terminal updates, and return tuple **unchanged**.

5. Do **not** change `run_board_search_gaze`, dispatch board gaze batches, or `_BOARD_SEARCH_TASK_KEYS`.

---

## Stage 3: Component tests

**Done when:** Tests assert prefixed ledger keys; existing candidate generate tests still pass with updated expectations.

1. In `tests/component/core/test_candidate.py`, class `TestRunCandidateArtifactGeneration`:
   - Add a module-level or test-local capture for `save_dispatch_ledger` calls.
   - In `test_returns_200_on_success` (and optionally one failure test), assert:
     - `save_dispatch_ledger` was called with positional args where arg[1] == `"user-craft_resume_base"` (second arg is task_key).
     - Returned `body["batch_id"]` starts with `"user-craft_resume_base-"`.
   - Update any test that hard-codes plain `craft_resume_base` in ledger expectations if present.

2. Create `tests/component/core/test_boards_generate_ast521.py` with class `TestRunBoardSearchGenerationAst521`:
   - Monkeypatch `database.get_board_search`, `database.get_candidate`, `database.save_dispatch_ledger`, `database.update_dispatch_ledger`, `asyncio.run`, `compute_batch_cost`, and `boards.get_board_search` as needed (mirror import style from `test_candidate.py` — `import src.core.boards as boards_mod`).
   - Fixture row: `{"board_search_id": "bs-1", "candidate_id": "somerset", "board_key": "linkedin"}`.
   - Test success: mock `do_task` success via `asyncio.run` return; assert `save_dispatch_ledger` second arg is `"user-craft_board_search_criteria"` and response `batch_id` prefix.
   - Test failure: mock `do_task` `success: False`; assert ledger `update_dispatch_ledger` called with `status="FAILED"` and initial save used `user-craft_board_search_criteria`.
   - Test 404 paths unchanged (no ledger save).

3. Run:

```bash
cd /Users/susan/chuckles/astral-ada && python -m pytest tests/component/core/test_candidate.py::TestRunCandidateArtifactGeneration -q
cd /Users/susan/chuckles/astral-ada && python -m pytest tests/component/core/test_boards_generate_ast521.py -q
```

**Betty manifest (for `qa-astral`, not run in build):** Extend bible § for **user-** Execution History rows — candidate `generate_artifact` API, boards `generate_search` API, core wrappers above; cross-link parent AST-514 acceptance criteria 3–5 and AST-515 `adhoc-` sibling boundary.

---

## Stage 4: Manual verification (Susan / UAT on parent)

**Done when:** AST-521 acceptance criteria 3–6 observable in Execution History (parent criteria 1–2 already covered by AST-515).

1. Select a candidate with API key; open **Execution History** (today filter).
2. **Artifacts** → run **Generate** or **Regenerate** on a craft task (e.g. base resume) → new row **Task** = `user-craft_resume_base` (or matching craft key), terminal success, cost if billed, expand logs, open prompt inspection → blocks present.
3. Force failure (bad key or invalid payload) on same path → row **Task** = `user-…`, status **FAILED**, not missing.
4. **Board Searches** → craft **Generate** (label or criteria task) → **Task** = `user-craft_board_search_*`, same inspectability on success and failure.
5. Run a **dispatch** task (Scheduled Actions **Run** or background Auto) → row still shows **plain** `task_key` (no `user-` / `adhoc-` prefix).
6. **Ad Hoc Preview** and artifact **preview-only** paths → no new row.
7. Confirm older plain `craft_*` rows (pre-ship) still display and expand unchanged.

---

## Self-Assessment

**Scope:** `scope-minor` — Two core wrapper functions gain a ledger prefix constant; component tests only; no UI or dispatcher edits.

**Conf:** `conf-high` — AST-515 established the prefix pattern; these wrappers already had ledger + `log_batch_id` + `do_task` agent_data storage.

**Risk:** `risk-Medium` — Wrong prefix would mislabel operator audit rows, but dispatch and adhoc paths are untouched and the change is forward-only.

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Plan compliance |
|------|-----------------|
| §1.3 DRY | Reuses existing wrappers; no duplicate ledger/agent_data implementation |
| §2.1 config | No new config keys; prefix is ticket-specified string format |
| §2.4 batch | Prefixed `batch_id` + existing `log_batch_id` + claim-free single-entity UI run |
| §2.6 state machine | N/A — no entity state transitions |
| §3.3 imports | Ledger writes remain in **core**; API routes unchanged |
| §3.5 naming | `ledger_task_key` matches AST-515 `run_adhoc_workbench_test` local naming |

No `conf-!!-NONE` conflicts.

---

## Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-514/AST-521-product-ui-user-prefix-in-execution-history`  
**Product commits:** `321ede5e` (`run_candidate_artifact_generation` — `ledger_task_key = f"user-{task_key}"`), `5308420a` (`run_board_search_generation` — same prefix pattern)

**Implemented:**
- `src/core/candidate.py` — prefixed ledger Task + `batch_id`; `do_task` still uses real `task_key`
- `src/core/boards.py` — same pattern for board search craft Generate

**Betty:** Stage 3 component tests + bible § for **user-** rows (manifest in plan Stage 3).

---

## Resolution

**Resolved:** 2026-05-28 (Ada)

| Radia item | Action |
|------------|--------|
| **fix-now** | None — plan fidelity and ASTRAL_CODE_RULES sign-off on `origin/sub/AST-514/AST-521-product-ui-user-prefix-in-execution-history` @ `49907d90`. |
| **discuss** | None. |
| **advisory** — exception-path ledger counts without `total_errors` | No change; pre-existing in both wrappers; forward-only UI runs. |
| **advisory** — parent UAT dispatch plain `task_key` / pre-ship plain `craft_*` rows | Deferred to parent AST-514 Stage 4 / bible §7.13zk; no UI diff in this child. |

**Publish ref:** `origin/sub/AST-514/AST-521-product-ui-user-prefix-in-execution-history` · Betty manifest green · §9a clean (dev + ftr dry-run).
