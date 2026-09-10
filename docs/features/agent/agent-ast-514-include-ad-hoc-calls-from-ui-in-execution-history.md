# AST-514 — Include Ad Hoc calls (from UI) in Execution History

**Component:** agent  
**Children:** AST-515, AST-521  
**Linear archived:** AST-514 2026-06-15; AST-515 2026-06-15; AST-521 2026-06-15

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-06-15 11:18 | AST-514 | docs | `8b0d6243a` | archive Linear issue content |

## Epic — AST-514

_Archived: 2026-06-15 · Linear URL: https://linear.app/astralcareermatch/issue/AST-514/include-ad-hoc-calls-from-ui-in-execution-history · Status at archive: Done · Project: Astral Agent · Assignee: susan · Priority / estimate: None / —_

### Purpose

Operators use **Execution History** to audit every meaningful agent call: cost, status, dispatcher logs, and stored prompt/response blocks. **Task dispatch** (scheduler **Auto**, background loops, and **Scheduled Actions Run**) already appears with **plain** task names. **Other Susan-initiated UI runs** — workbench tests, artifact **Generate**, board-search craft, and similar product flows — must be equally visible and **labeled distinctly** so experiments and craft generation are not confused with dispatch traffic. This feature closes that observability gap with consistent ledger, logs, and prompt/response inspection.

### Functional scope

* **Task column prefixes** (all **dispatch** rows stay **unprefixed**):
  * `adhoc-<task_key>` — **Test** from admin **Anthropic Ad Hoc** only (workbench task selection; editable prompts).
  * `user-<task_key>` — **Product UI buttons** that trigger a **real provider call** outside the dispatch runner, including at minimum:
    * **Artifacts** **Generate / Regenerate** (candidate generate endpoints for craft and related artifact tasks).
    * **Board Searches** craft **Generate** (board-search generate endpoints).
    * **Any current or future non-dispatch UI control** that invokes the agent stack with a provider call — same recording rules when added.
  * **Plain** `task_key` — **All dispatch**: background scheduler, **Auto**, and **Scheduled Actions manual Run** (Susan confirmed: dispatch stays plain whether triggered from admin or automation).
* **Recording parity** for every in-scope `adhoc-` and `user-` call: `dispatch_ledger` row, `log_batch_id` for app logs, stored prompt/response blocks inspectable from Execution History, terminal status, and cost — same affordances as dispatch batches today.
* **Ledger visibility:** Rows appear for the relevant candidate within existing Execution History filters.
* **Provider parity:** Anthropic and DeepSeek where the UI supports both.

### Boundaries

* **Preview-only is out of scope** — assembly with **no** provider call (Ad Hoc **Preview**, read-only task prompt preview) does not create a row.
* **Dispatch unchanged** — scheduler semantics, batch locking, multi-entity counts, ledger `task_key` labeling, and **Run** / **Auto** behavior stay as today (plain task names only).
* **Forward-only labeling** — existing ledger rows keep their stored `task_key` as-is; `user-` / `adhoc-` apply to **new** runs after ship (no migration or relabel).
* **No retroactive backfill** of older runs.
* **Does not replace runner UIs** — Ad Hoc, Artifacts, and Board Searches remain where work is triggered; Execution History is audit-only.
* **Must not break** existing dispatch rows (today filter, Skip Checks, log expand, prompt modal).
* **Saving generated content to candidate artifacts** is **out of scope** — remains Artifacts **Save**; this ticket is Execution History observability only.

### Acceptance criteria

1. **Ad Hoc Test** success → row with **Task** = `adhoc-<task_key>`, logs, prompt inspection, cost, terminal success.
2. **Ad Hoc Test** failure → row with **Task** = `adhoc-<task_key>`, terminal failure (never silent).
3. **Artifacts Generate / Regenerate** success → **Task** = `user-<task_key>` with full inspectability.
4. Same paths on failure → **Task** = `user-<task_key>`, terminal failure.
5. **Board Searches** craft **Generate** success/failure → **Task** = `user-<task_key>` with same inspectability.
6. **Scheduled Actions Run** and **background dispatch** for the same task → **plain** `task_key` (no `user-` or `adhoc-` prefix), behavior unchanged.
7. **Preview-only** does not create a row.
8. Expanding in-scope `adhoc-` / `user-` rows shows logs when emitted; prompt inspection shows stored blocks for that batch.

### Dependencies and blockers

none.

### Open questions

none. (Susan 2026-05-28: **forward-only**; product UI provider calls → `user-`; workbench Test → `adhoc-`; **dispatch stays plain**.)

---

### Original brief

Right now, execution History only shows results for task-dispatch calls.  We need to add the ad hoc calls as well so we can view logs and prompt contents for those just as we do for dispatched calls.

#### Comments


##### hedy — 2026-05-28T23:44:04.318Z

[check-linear]

**Session scope:** Parent **AST-514** / Astral Agent — assigned child ids **(none)**.

**§0a:** `dev-hedy` @ `/Users/susan/chuckles/astral-hedy`; `git fetch origin`, `checkout dev-hedy`, `merge origin/dev` — already up to date. Gate: **BEHIND=0**, `origin/dev` ancestor of **HEAD**.

**§0b:** `@hedy` team search (250, no status filter); Astral Agent project `@hedy` query; **14d** fallback (`updatedAt -P14D`, team-wide 250) — union is mostly historical branch-name hits, not comment @-mentions. Full threads on **AST-514**, children **AST-515** / **AST-521**, and Hedy-assignee roster children **AST-505** / **AST-506** / **AST-508** — **0** actionable comments (no `@hedy` or directed-at-Hedy replies after prior agent passes; latest parent activity is Betty **AST-521** QA manifest @ `2026-05-28T23:40`).

**§1:** Assignee-me — **AST-505**, **AST-506**, **AST-508** (User Testing); **AST-294**, **AST-479**, **AST-501**–**503** (Done). None require inbox action.

**Pipeline:** Inbox quiet; no plan/build/test/resolve from this pass. **AST-515** User Testing; **AST-521** Tests Passed (Ada → Radia/resolve track).

##### katherine — 2026-05-28T23:43:18.077Z

[check-linear]

**Inbox (parent AST-514 / Astral Agent):** `@katherine` issue search (team + Astral Agent project), fallback via recent project activity, full threads on **AST-514**, children **AST-515** / **AST-521**, and prior mention hits in session. **0** actionable comments — nothing `@katherine` or directed at Katherine needing reply or small fix after Katherine's **AST-521** `[check-linear]` @ `2026-05-28T23:34` (Betty QA manifest @ `23:40` is Ada **`test-astral`** handoff, no `@katherine`).

**§0a (`astral-kath` / `dev-kath`):** `git fetch origin`, `checkout dev-kath`, `merge origin/dev` — **merge-clean** (`BEHIND=0`, `origin/dev` ancestor of `HEAD`).

**§1:** `assignee = me` MCP query errored this pass; orchestrator assigned ids **(none)** — no Katherine-assignee tickets in Astral Agent scope.

**Session scope:** Idle — no publish merge or pipeline skills from this pass. **AST-521** **Tests Passed** (Ada); **AST-515** **User Testing** (Ada).

##### ada — 2026-05-28T23:43:13.178Z

[check-linear]

**Session scope:** Parent **AST-514** / Astral Agent — assigned child ids **(none)**.

**§0a:** `dev-ada` @ `/Users/susan/chuckles/astral-ada`; `git fetch origin`, `checkout dev-ada`, `merge origin/dev` — already up to date. Gate: **BEHIND=0**, `origin/dev` ancestor of **HEAD**.

**§0b:** `@ada` issue search (team + Astral Agent project); assignee **Ada Lovelace** union. Full threads on **AST-514**, children **AST-515** / **AST-521**, and other @ada / assignee hits — **0** actionable comments (nothing `@ada` or directed at Ada needing reply or small fix after Ada’s prior `[check-linear]` on **AST-521** @ `2026-05-28T23:35` and **AST-520** @ `23:17`). Betty’s **AST-521** QA manifest @ `23:40` is pipeline handoff, not inbox work.

**Pipeline:** Inbox quiet; no `plan-astral` / `build-astral` / `test-astral` / `resolve-astral` from this pass. **AST-521** is **Tests Passed** (assignee Ada); **AST-515** **User Testing**; parent still **In Progress** until **AST-521** lands.

##### betty — 2026-05-28T23:43:09.327Z

[check-linear]

**Session scope:** Parent **AST-514** / Astral Agent — assigned child ids **AST-515**, **AST-521**.

**§0a:** `dev-betty` @ `/Users/susan/chuckles/astral-betty`; `git fetch origin`, `checkout dev-betty`, `merge origin/dev` — already up to date. Gate: **BEHIND=0**, `origin/dev` ancestor of **HEAD**.

**§0b:** `@betty` issue search (team + Astral Agent project); **14d** Team Astral activity scan — union is mostly historical `betty/ast-*` branch-name hits, not comment @-mentions. Full threads on **AST-514**, **AST-515**, **AST-521** — **0** actionable comments (no `@betty` or directed-at-Betty replies after prior agent passes).

**§1:** `assignee = me` MCP query errored this pass; no Betty-assignee tickets identified in session project scan.

**§5b:** **Tests Ready** — team-wide and Astral Agent project: **0** issues. Assigned **AST-515** / **AST-521** scanned: neither is **Tests Ready**; latest comments are Radia review (**515**) and Betty QA manifest (**521**) — no **`[qa-handoff]`** to clear.

**Pipeline:** Inbox quiet; no manifest/test/bible work. **AST-515** **User Testing** (Ada); **AST-521** **Tests Passed** (Ada → **`review-astral`**).

##### betty — 2026-05-28T23:34:57.029Z

[check-linear]

**Session scope:** Parent **AST-514** / Astral Agent — assigned child ids **(none)**.

**§0a:** `dev-betty` @ `/Users/susan/chuckles/astral-betty`; `git fetch origin`, `checkout dev-betty`, `merge origin/dev` — already up to date. Gate: **BEHIND=0**, `origin/dev` ancestor of **HEAD**.

**§0b:** `@betty` issue search (team + Astral Agent project); **14d** fallback via recent Team Astral activity. Union is mostly historical branch-name hits; full threads on **AST-514**, **AST-515**, **AST-521**, **AST-477** — **0** actionable comments (no `@betty` or directed-at-Betty replies after prior agent passes; latest **AST-477** activity is Chuckles `@susan` rollup-blocked note).

**§1:** `assignee = me` MCP query errored this pass; no Betty-assignee tickets identified in Astral Agent project scan.

**§5b:** **Tests Ready** — team-wide and Astral Agent project: **0** issues. No latest-comment **`[qa-handoff]`** to clear.

**Pipeline:** Inbox quiet; no manifest/test/bible work. **AST-521** is **Plan Approved** (Ada → build); publish ref noted for future **qa-astral** when **Code Complete**.

##### chuckles — 2026-05-28T23:21:35.515Z

@susan Definition updated for **`user-`** UI runs (Artifacts Generate, Board Search craft generate) alongside **`adhoc-`** (AST-515). Parent is **not** UAT-complete until the follow-on child lands.

1. **Forward-only vs relabel** — keep existing plain `craft_*` ledger rows as-is, or one-time migration to `user-<task_key>`?
2. **Other UI runners** — any buttons beyond Ad Hoc Test, Artifacts Generate, Board Search generate, and scheduler Run that should get **`user-`**?

### Manual test steps

1. Restart the app on local **`dev`** if it is already running.
2. Select a candidate with a timezone set (Execution History defaults to today in that TZ).
3. Open **Anthropic Ad Hoc** → choose task **`evaluate_jd`** (or another task), pick an entity, run **Test** (real provider call).
4. Open **Execution History** → confirm a new row with **Task** = `adhoc-evaluate_jd` (or matching `adhoc-<task_key>`), terminal success status, cost if billed, counts consistent with a single run (1 processed / 1 pass or fail as appropriate).
5. Expand that row → confirm log lines appear when the run logged during the call.
6. Click the batch id / prompt inspection → confirm SYSTEM / cache / user / live / RESPONSE blocks are populated.
7. Run **Preview** only on the same workbench setup → confirm **no** new Execution History row.
8. Trigger a failed **Test** (e.g. bad key or forced failure) → confirm a row with `adhoc-<task_key>` and **FAILED** status (not missing).
9. Open an older **dispatch** row → confirm **Task** has no `adhoc-` prefix; expand logs and prompt inspection still work.

`origin/ftr/AST-514-include-ad-hoc-calls-from-ui-in-execution-history` @ `40a54c69` · local **`dev`** merged (prep-uat §8). Child **`sub/AST-514/AST-515-…`** deleted on origin.

Reset local dev to central: `git fetch origin && git reset --hard origin/dev`

##### katherine — 2026-05-28T22:01:19.286Z

[check-linear]

**Inbox (parent AST-514 / Astral Agent):** Scanned `@katherine` issue search (team + project), full threads on **AST-514**, child **AST-515**, and Katherine-assignee / recent mention candidates (**AST-513**, **AST-504**, **AST-481**). **0** actionable comments — nothing `@katherine` or directed at Katherine needing a reply or small fix after Katherine’s **AST-513** `[check-linear]` @ `2026-05-28T21:10`.

**§0a (`astral-kath` / `dev-kath`):** `git fetch origin`, `checkout dev-kath`, `merge origin/dev` — **merge-clean** (`BEHIND=0`, `origin/dev` ancestor of `HEAD`). Prior inbox pass reported merge conflicts; **not** reproduced this run.

**Session scope:** **Your assigned issue ids: (none)** — no ticket-specific publish merge or pipeline work from this pass. **AST-515** is **Plan Approved**, assignee **Ada** (`origin/sub/AST-514/AST-515-ad-hoc-workbench-test-runs-in-execution-history`); parent **AST-514** assignee Chuckles — Katherine pipeline queue idle per happy path.

##### hedy — 2026-05-28T22:01:09.988Z

[check-linear]

**Inbox (parent AST-514 / Astral Agent):** `@hedy` issue search (team + project), fallback scan (`updatedAt -P14D`), full threads on **AST-514**, child **AST-515**, and Hedy-assignee roster children (**AST-505**–**508**). **0** actionable comments — nothing `@hedy` or directed at Hedy needing reply or small fix after prior agent posts.

**§0a:** `dev-hedy` @ `/Users/susan/chuckles/astral-hedy`; merged `origin/dev` cleanly — `BEHIND=0`, `merge-clean: yes`.

**Session scope:** Orchestrator assigned issue ids **(none)** — no `plan-astral` / `build-astral` / `test-astral` / `resolve-astral` from this pass. **AST-515** is **Plan Approved**, assignee **Ada** (publish ref `origin/sub/AST-514/AST-515-ad-hoc-workbench-test-runs-in-execution-history`).

## Sub-issues

### AST-515 — Ad hoc workbench Test runs in Execution History

_Archived: 2026-06-15 · Linear URL: https://linear.app/astralcareermatch/issue/AST-515/ad-hoc-workbench-test-runs-in-execution-history-include-ad-hoc-calls · Status at archive: Done · Project: Astral Agent · Assignee: ada · Priority / estimate: None / — · Blocked by / blocks / related: parent: AST-514_

#### What this implements

Each **Test** from the admin **Anthropic Ad Hoc** workbench creates an Execution History row with a stable batch id, attached logs, stored prompt/response blocks (same inspection as dispatch batches), completion status and cost, and **Task** column value `adhoc-<task_key>`. Preview-only (no provider call) does not create a row. Anthropic and DeepSeek workbench paths follow the same rules.

#### Acceptance criteria

1. After a successful **Test** from Anthropic Ad Hoc, a new row appears in Execution History for the selected candidate (within the active date filter) with **Task** = `adhoc-<task_key>` (workbench task_key), a terminal success status, non-zero cost when the provider returns billing data, and count fields consistent with a single run.
2. After a failed **Test** (provider or validation failure surfaced to the workbench), a row appears with **Task** = `adhoc-<task_key>` and a terminal failure status so the attempt is auditable, not silently omitted.
3. Expanding that row loads log lines tied to the run’s batch identifier (not an empty panel when logging occurred during the call).
4. Opening prompt inspection for that row shows the assembled prompt segments and the model response stored for that run, comparable to inspecting a dispatch batch today.
5. **Preview** alone does not add or update any Execution History row.
6. Existing dispatch-only rows still show plain task names (no `adhoc-` prefix), and still load, filter, expand logs, and open prompt inspection without regression.

#### Boundaries

* Does not change scheduler dispatch batch semantics or multi-entity count rules.
* No retroactive backfill of past ad hoc runs.
* Does not replace the Anthropic Ad Hoc workbench UI as the runner.
* No new Execution History analytics beyond listing/filtering ad hoc rows.

#### Notes for planning

* Primary touch: `run_adhoc` / `adhoc/test` path today records timesheets but not `dispatch_ledger`, `log_batch_id`, or `agent_data` — mirror patterns from `candidate.py` craft ledger + dispatcher `log_batch_id` usage.
* Store ledger `task_key` as `adhoc-<task_key>` (workbench selection).
* `AdminPerformanceMonitor` likely needs no change if the API returns the prefixed task_key; verify during plan.
* Betty manifest: `api_admin` adhoc routes, agent storage, ledger list/detail if new helpers.

##### Comments


###### radia — 2026-05-28T22:16:03.384Z

**Diff:** `origin/dev...origin/sub/AST-514/AST-515-ad-hoc-workbench-test-runs-in-execution-history` (6 files, +494 / −13)

#### Plan fidelity

Implementation matches the combined plan (Stages 1–3): `run_adhoc_workbench_test` in core wraps `run_adhoc` with `adhoc-<task_key>` ledger row, `log_batch_id` for the provider call, `_store_prompt_blocks` / `_store_response_block` for inspection, and terminal ledger updates on success / soft-failure / exception. `adhoc_test` swaps to the wrapper; `adhoc/preview` unchanged. Tests cover success, `success: False`, exception re-raise, and preview not invoking the wrapper or `save_dispatch_ledger`.

Self-Assessment (`scope-Single-Component`, `conf-Medium`, `risk-Medium`) still matches the diff footprint.

#### ASTRAL_CODE_RULES

| Area | Verdict |
|------|---------|
| **§2.4 batch** | `batch_id` prefix, `log_batch_id` during `run_adhoc`, ledger save/update with `batch_size=1` — aligned with `run_candidate_artifact_generation` / `do_task` audit pattern |
| **§3.3 layers** | Ledger + `agent_data` writes in **core** only; `api_admin` imports core wrapper — no new UI→data business logic |
| **§1.5 / D2 storage** | `_store_*` failures logged at `debug` with `exc_info` — same bounded swallow as `do_task` (~L1007); acceptable with existing precedent |
| **§2.1 config** | `entity_type` from `TASK_CONFIG`; ledger task label is ticket-specified prefix, not a new magic string list |

#### Advisory (non-blocking)

- **`from src.data import database`** added alongside existing `from src.data.database import (...)` named imports in `agent.py`. Works and matches `candidate.py`; optional follow-up to fold `save_dispatch_ledger` / `update_dispatch_ledger` into the existing import block for one style.
- **Parent UAT (Stage 4):** dispatch-only Execution History regression still manual on parent **AST-514** (`AdminPerformanceMonitor` per bible §7.13k) — no UI diff in this child, as planned.

#### fix-now

None.

#### discuss

None.

###### betty — 2026-05-28T22:05:19.143Z

**QA test manifest** (`origin/sub/AST-514/AST-515-ad-hoc-workbench-test-runs-in-execution-history` @ `87b80fac`)

`docs/ASTRAL_TEST_BIBLE.md` shasum on publish ref: `455f85d9f0f61e4f46b7b5d5d22f43eb1bbe83cf95b4ddfa5e280ab39f0ff03b`

1. `./scripts/testing/run_component_tests.sh tests/component/core/test_agent.py::TestAst515AdhocWorkbenchLedger`
2. `./scripts/testing/run_component_tests.sh tests/component/ui/api/test_api_admin.py::TestAdhocRoutes`
3. `./scripts/testing/run_component_tests.sh tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_adhoc_test_decodes_encoded_payload`
4. `./scripts/testing/run_component_tests.sh tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_adhoc_test_hydrates_encoded_payload_with_entities`
5. `./scripts/testing/run_component_tests.sh tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_adhoc_test_skips_decode_without_response_text`

**Coverage added this pass:** `TestAst515AdhocWorkbenchLedger` (ledger COMPLETED/FAILED/exception paths, agent_data blocks, `log_batch_id` cleared); adhoc route tests retargeted to `run_adhoc_workbench_test`; `test_adhoc_preview_does_not_create_dispatch_ledger`.

**Regression (parent UAT, not required for child green):** `tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx` per bible §7.13k — dispatch rows unchanged.

###### ada — 2026-05-28T21:59:33.862Z

Plan: [ast-515-ad-hoc-workbench-test-runs-in-execution-history-include-ad-hoc-calls.md](https://github.com/susansomerset/astral/blob/sub/AST-514/AST-515-ad-hoc-workbench-test-runs-in-execution-history/docs/features/agent/ast-515-ad-hoc-workbench-test-runs-in-execution-history-include-ad-hoc-calls.md)

**Scope:** `scope-Single-Component` — `run_adhoc_workbench_test` in `agent.py`, wire `adhoc_test`, component tests only; Execution History UI unchanged.

**Conf:** `conf-Medium` — Reuses craft/dispatch ledger + `agent_data` patterns, but adhoc passes pre-resolved prompt strings and both Anthropic/DeepSeek paths.

**Risk:** `risk-Medium` — Wrong ledger rows could clutter Execution History; dispatch rows and preview-only path stay isolated.

---

#### Stage 1: Core — `run_adhoc_workbench_test`

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

#### Stage 2: API — wire `adhoc_test`

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

#### Stage 3: Tests

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

#### Stage 4: Manual verification (Susan / UAT on parent)

**Done when:** Acceptance criteria 1–6 on AST-515 are observable in Execution History.

1. Select a candidate with timezone set; open **Execution History** (today filter).
2. **Anthropic Ad Hoc** → pick task `evaluate_jd`, entity, run **Test** (real call) → new row with **Task** `adhoc-evaluate_jd`, terminal success, cost if billed, counts `1/1/0/0`.
3. Force a failure (invalid key or bad payload) → row with **Task** `adhoc-…`, status **FAILED**, not missing.
4. Expand row → log lines present when the run logged.
5. Open prompt inspection (batch link / modal) → SYSTEM / CACHE / TASK / RESPONSE blocks populated.
6. **Preview** only → no new row.
7. Confirm an older dispatch row still shows plain task name (no `adhoc-` prefix) and still expands/inspects.

---

#### Self-Assessment

**Scope:** `scope-Single-Component` — Core wrapper in `agent.py`, one API route swap, and focused component tests; no Execution History UI or dispatcher scheduler changes.

**Conf:** `conf-Medium` — Patterns are established in `candidate.run_candidate_artifact_generation` and `do_task` storage, but adhoc uses pre-resolved prompt strings and dual providers (Anthropic/DeepSeek) through `run_adhoc`.

**Risk:** `risk-Medium` — Execution History and `agent_data` are operator-critical; incorrect ledger updates could clutter or hide runs, but dispatch-only rows are untouched.

---

#### Review (build)

**Branch:** `sub/AST-514/AST-515-ad-hoc-workbench-test-runs-in-execution-history`
**Build commit:** `9cbaefae` on `origin/sub/AST-514/AST-515-ad-hoc-workbench-test-runs-in-execution-history`

**Implemented:**
- `run_adhoc_workbench_test` in `src/core/agent.py` — ledger + `log_batch_id` + agent_data around `run_adhoc`
- `adhoc_test` in `src/ui/api/api_admin.py` calls the wrapper; preview unchanged

**Pending:** Betty component tests per Stage 3 plan (`qa-astral`).

---

#### Self-Review (ASTRAL_CODE_RULES)

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

#### Resolution

**Resolved:** 2026-05-28 (Ada)

| Radia item | Action |
|------------|--------|
| **fix-now** | None — plan fidelity and ASTRAL_CODE_RULES sign-off on `origin/sub/AST-514/AST-515-ad-hoc-workbench-test-runs-in-execution-history` @ `87b80fac`. |
| **discuss** | None. |
| **advisory** — dual `database` import style in `agent.py` | No change; matches `candidate.py` precedent. |
| **advisory** — parent UAT dispatch regression (AST-514 Stage 4) | Deferred to parent UAT (`AdminPerformanceMonitor` §7.13k); no UI diff in this child. |

**Publish ref:** `origin/sub/AST-514/AST-515-ad-hoc-workbench-test-runs-in-execution-history` · Betty manifest green · §9a clean.

#### Files changed (plan vs actual)  _(no commit trail — plan only)_

| | file | planned | actual |
|---|---|---|---|
| · | `src/core/agent.py` | Add `run_adhoc_workbench_test` (ledger + `log_batch_id` + `a | — |
| · | `src/ui/api/api_admin.py` | `adhoc_test` calls `run_adhoc_workbench_test` instead of bar | — |
| · | `tests/component/core/test_agent.py` | Unit tests for ledger/agent_data on success, failure, and ex | — |
| · | `tests/component/ui/api/test_api_admin.py` | Point adhoc test mocks at `run_adhoc_workbench_test`; assert | — |

### AST-521 — Product UI `user-` prefix in Execution History

_Archived: 2026-06-15 · Linear URL: https://linear.app/astralcareermatch/issue/AST-521/product-ui-user-prefix-in-execution-history-include-ad-hoc-calls-from · Status at archive: Done · Project: Astral Agent · Assignee: ada · Priority / estimate: None / — · Blocked by / blocks / related: parent: AST-514_

#### What this implements

Every **product UI button** that triggers a **real provider call** outside the dispatch runner records Execution History with **Task** = `user-<task_key>`, with the same ledger, log, cost, and prompt/response inspection parity as dispatch batches. Covers **Artifacts Generate / Regenerate** and **Board Searches** craft **Generate** (and the same pattern for future non-dispatch UI agent calls). **Dispatch** (scheduler **Auto**, background loops, and **Scheduled Actions Run**) stays **plain** `task_key`.

#### Acceptance criteria

3. **Artifacts Generate / Regenerate** success → **Task** = `user-<task_key>` with full inspectability.
4. Same paths on failure → **Task** = `user-<task_key>`, terminal failure.
5. **Board Searches** craft **Generate** success/failure → **Task** = `user-<task_key>` with same inspectability.
6. Expanding in-scope `user-` rows shows logs when emitted; prompt inspection shows stored blocks for that batch.

(Parent criteria 1–2 `adhoc-` satisfied by **AST-515**. Criteria 6–7 dispatch plain / preview unchanged.)

#### Boundaries

* Does not change **Anthropic Ad Hoc** workbench (**AST-515** / `adhoc-`).
* Does not change **dispatch** ledger labeling or **Scheduled Actions Run** semantics.
* **Forward-only** — no relabel of existing plain `craft_*` ledger rows.
* No retroactive backfill.
* Does not save generated content to candidate artifacts (Artifacts **Save** remains separate).
* Sibling **AST-515** is **adhoc-** only; this ticket is `user-` only.

#### Notes for planning

* Primary touch: `run_candidate_artifact_generation` in `src/core/candidate.py`, `run_board_search_generation` in `src/core/boards.py` — mirror `run_adhoc_workbench_test` ledger/`log_batch_id`/`agent_data` pattern from **AST-515** (`ledger_task_key = f"user-{task_key}"`, `batch_id = f"{ledger_task_key}-{uuid}"`).
* `do_task` already stores **agent_data** when `log_batch_id` is set; verify logs and terminal ledger updates on success/failure.
* **AdminPerformanceMonitor** likely unchanged if API returns prefixed `task_key`.
* Betty manifest: candidate generate API, boards generate API, core wrappers, bible § for **user-** rows.

#### Radia review — `origin/sub/AST-514/AST-521-product-ui-user-prefix-in-execution-history`

**Diff:** `origin/dev...origin/sub/AST-514/AST-521-product-ui-user-prefix-in-execution-history` @ `49907d90`

**AST-521 product commits:** `321ede5e` (`run_candidate_artifact_generation`), `5308420a` (`run_board_search_generation`), `49907d90` (tests + bible §7.13zk).

Branch also carries **AST-515** rollup (`40a54c69`) — sibling already **User Testing**; not AST-521 scope. Review below is **AST-521 only** (`candidate.py`, `boards.py`, tests).

---

##### Plan fidelity (Stages 1–3)

| Stage | Verdict |
|-------|---------|
| Candidate artifact Generate/Regenerate | `ledger_task_key = f"user-{task_key}"`; `batch_id` prefixed; `save_dispatch_ledger` uses `ledger_task_key`; `do_task(task_key=task_key, …)` unchanged |
| Board search craft Generate | Same pattern in `run_board_search_generation` |
| Tests | `TestRunCandidateArtifactGeneration` asserts prefixed ledger + `batch_id`; `test_boards_generate_ast521.py` covers success, failure, 404 (no ledger) |
| Boundaries | No dispatcher, UI, or `adhoc-` changes in AST-521 commits; forward-only (no relabel) per parent |

Self-Assessment **scope-minor** / **conf-high** matches the diff footprint.

---

##### ASTRAL_CODE_RULES

| Rule | Verdict |
|------|---------|
| §1.3 DRY | Reuses existing wrappers; two-line prefix only |
| §2.4 batch | Prefixed `batch_id` + existing `log_batch_id` lifecycle |
| §3.3 imports | Ledger writes stay in **core**; API routes delegate unchanged |
| §3.2 UI | No frontend diff for this child (Execution History reads ledger `task_key` as-is) |
| B1 / B2 / D2 / E1 | No new violations in AST-521 hunks |

Ledger label vs storage key split (`user-*` in ledger, real `task_key` in `agent_data`) matches AST-515 precedent and plan decision.

---

##### fix-now

None.

##### discuss

None.

##### advisory

- **Exception-path ledger counts** (`update_dispatch_ledger` on `except` without `total_errors`) — pre-existing in both wrappers; unchanged by this ticket; acceptable for forward-only UI runs.
- **Parent UAT:** confirm dispatch rows stay plain `task_key` and pre-ship plain `craft_*` rows still expand (AST-514 Stage 4 / §7.13zk note on `AdminPerformanceMonitor`).

#### QA test manifest (AST-521)

**Publish ref:** `origin/sub/AST-514/AST-521-product-ui-user-prefix-in-execution-history` @ `49907d90`

**`docs/ASTRAL_TEST_BIBLE.md` shasum (publish ref):** `ca12dc805704a4b23a390aaaafb5a281aab8ba642e314cd701f3c8827227c273`

Run on **`dev-ada`** after merging this **`sub/*`** tip (same as **`test-astral`**):

1. `./scripts/testing/run_component_tests.sh tests/component/core/test_candidate.py::TestRunCandidateArtifactGeneration`
2. `./scripts/testing/run_component_tests.sh tests/component/core/test_boards_generate_ast521.py::TestRunBoardSearchGenerationAst521`

**Coverage intent:** **`user-<task_key>`** ledger rows + prefixed **`batch_id`** for **`run_candidate_artifact_generation`** and **`run_board_search_generation`** (success + failure); 404 paths skip ledger. No UI diff — Execution History display unchanged; parent UAT may still run **`test_AdminPerformanceMonitor.test.tsx`** per bible **§7.13k**.

**Boundary:** dispatch / Scheduled Actions **Run** stay plain **`task_key`**; **adhoc-** remains **AST-515** only.

###### hedy — 2026-05-28T23:35:08.051Z

[check-linear]

**Inbox (AST-521 / parent AST-514 / Astral Agent):** `@hedy` issue search (team + project), fallback scan (`updatedAt -P14D`), full thread on **AST-521** and parent **AST-514**. **0** actionable comments — nothing `@hedy` or directed at Hedy needing reply or small fix after Ada’s plan post @ `2026-05-28T23:33`.

**§0a:** `dev-hedy` @ `/Users/susan/chuckles/astral-hedy`; merged `origin/dev` cleanly — `BEHIND=0`, `origin/dev` ancestor of `HEAD`.

**Session scope:** Orchestrator assigned **AST-521**; Linear assignee **Ada**; status **Plan Approved** (plan on `origin/sub/AST-514/AST-521-product-ui-user-prefix-in-execution-history`). No publish merge or pipeline from this pass — **`build-astral`** when Ada (or reassigned engineer) picks up.

###### ada — 2026-05-28T23:35:00.427Z

[check-linear]

**Inbox (AST-521 / parent AST-514 / Astral Agent):** `@ada` issue search (team + project), fallback `-P14D` scan, full threads on **AST-521**, **AST-514**, sibling **AST-515**. **0** actionable comments — nothing `@ada` or directed at Ada needing reply or small fix after Ada’s plan post @ `2026-05-28T23:33`.

**§0a (`astral-ada` / `dev-ada`):** `git fetch origin`, `checkout dev-ada`, `merge origin/dev` — **merge-clean** (`BEHIND=0`, `origin/dev` ancestor of `HEAD`).

**Session scope:** **AST-521** only — **Plan Approved**, publish ref `origin/sub/AST-514/AST-521-product-ui-user-prefix-in-execution-history`; no `build-astral` / `test-astral` / `resolve-astral` from this pass per check-linear §6.

###### katherine — 2026-05-28T23:34:55.745Z

[check-linear]

**Inbox (session AST-521 / parent AST-514 / Astral Agent):** `@katherine` issue search (team + project), full threads on **AST-521**, **AST-514**, and Katherine-assignee roster in session project. **0** actionable comments — nothing `@katherine` or directed at Katherine needing reply or small fix after prior **AST-514** Katherine `[check-linear]` @ `2026-05-28T22:01`.

**§0a (`astral-kath` / `dev-kath`):** `git fetch origin`, `checkout dev-kath`, `merge origin/dev` — **merge-clean** (`BEHIND=0`, `origin/dev` ancestor of `HEAD`).

**Session scope:** **AST-521** only — **Plan Approved**, assignee **Ada**; publish ref `origin/sub/AST-514/AST-521-product-ui-user-prefix-in-execution-history`. No publish merge or pipeline skills from this pass (check-linear comments-only).

###### ada — 2026-05-28T23:33:41.485Z

Plan: [`agent-ast-514-include-ad-hoc-calls-from-ui-in-execution-history.md#ast-521--product-ui-user--prefix-in-execution-history`](https://github.com/susansomerset/astral/blob/sub/AST-514/AST-521-product-ui-user-prefix-in-execution-history/docs/features/agent/ast-521-product-ui-user-prefix-in-execution-history-include-ad-hoc-calls-from-ui-in-execution-history.md)

**Scope:** `scope-minor` — Two core wrappers (`run_candidate_artifact_generation`, `run_board_search_generation`) get `user-` ledger/`batch_id` prefix only; component tests; no UI or dispatcher changes.

**Conf:** `conf-high` — AST-515 established the prefix pattern; these paths already record ledger + `log_batch_id` + `do_task` agent_data.

**Risk:** `risk-Medium` — Mislabeled Task column would confuse operator audit, but dispatch and `adhoc-` paths are untouched and labeling is forward-only.

---

#### Stage 1: Candidate artifact generation — `user-` ledger prefix

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

#### Stage 2: Board search craft generation — `user-` ledger prefix

**Done when:** `POST /api/boards/searches/<board_search_id>/generate/<task_key>` creates ledger rows with **Task** = `user-<task_key>` and prefixed `batch_id`; validation and `do_task` behavior unchanged.

1. In `src/core/boards.py`, function `run_board_search_generation` (starts ~line 476), **after** row/candidate validation and **before** `save_dispatch_ledger`, add the same two lines as Stage 1 (`ledger_task_key`, prefixed `batch_id`).

2. Remove `batch_id = f"{task_key}-{uuid.uuid4()}"`.

3. Pass **`ledger_task_key`** as the `task_key` argument to `save_dispatch_ledger` (not the bare craft key).

4. Leave `ctx` merge, `do_task`, ledger terminal updates, and return tuple **unchanged**.

5. Do **not** change `run_board_search_gaze`, dispatch board gaze batches, or `_BOARD_SEARCH_TASK_KEYS`.

---

#### Stage 3: Component tests

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

#### Stage 4: Manual verification (Susan / UAT on parent)

**Done when:** AST-521 acceptance criteria 3–6 observable in Execution History (parent criteria 1–2 already covered by AST-515).

1. Select a candidate with API key; open **Execution History** (today filter).
2. **Artifacts** → run **Generate** or **Regenerate** on a craft task (e.g. base resume) → new row **Task** = `user-craft_resume_base` (or matching craft key), terminal success, cost if billed, expand logs, open prompt inspection → blocks present.
3. Force failure (bad key or invalid payload) on same path → row **Task** = `user-…`, status **FAILED**, not missing.
4. **Board Searches** → craft **Generate** (label or criteria task) → **Task** = `user-craft_board_search_*`, same inspectability on success and failure.
5. Run a **dispatch** task (Scheduled Actions **Run** or background Auto) → row still shows **plain** `task_key` (no `user-` / `adhoc-` prefix).
6. **Ad Hoc Preview** and artifact **preview-only** paths → no new row.
7. Confirm older plain `craft_*` rows (pre-ship) still display and expand unchanged.

---

#### Self-Assessment

**Scope:** `scope-minor` — Two core wrapper functions gain a ledger prefix constant; component tests only; no UI or dispatcher edits.

**Conf:** `conf-high` — AST-515 established the prefix pattern; these wrappers already had ledger + `log_batch_id` + `do_task` agent_data storage.

**Risk:** `risk-Medium` — Wrong prefix would mislabel operator audit rows, but dispatch and adhoc paths are untouched and the change is forward-only.

---

#### Self-Review (ASTRAL_CODE_RULES)

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

#### Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-514/AST-521-product-ui-user-prefix-in-execution-history`
**Product commits:** `321ede5e` (`run_candidate_artifact_generation` — `ledger_task_key = f"user-{task_key}"`), `5308420a` (`run_board_search_generation` — same prefix pattern)

**Implemented:**
- `src/core/candidate.py` — prefixed ledger Task + `batch_id`; `do_task` still uses real `task_key`
- `src/core/boards.py` — same pattern for board search craft Generate

**Betty:** Stage 3 component tests + bible § for **user-** rows (manifest in plan Stage 3).

---

#### Resolution

**Resolved:** 2026-05-28 (Ada)

| Radia item | Action |
|------------|--------|
| **fix-now** | None — plan fidelity and ASTRAL_CODE_RULES sign-off on `origin/sub/AST-514/AST-521-product-ui-user-prefix-in-execution-history` @ `49907d90`. |
| **discuss** | None. |
| **advisory** — exception-path ledger counts without `total_errors` | No change; pre-existing in both wrappers; forward-only UI runs. |
| **advisory** — parent UAT dispatch plain `task_key` / pre-ship plain `craft_*` rows | Deferred to parent AST-514 Stage 4 / bible §7.13zk; no UI diff in this child. |

**Publish ref:** `origin/sub/AST-514/AST-521-product-ui-user-prefix-in-execution-history` · Betty manifest green · §9a clean (dev + ftr dry-run).

#### Files changed (plan vs actual)  _(no commit trail — plan only)_

| | file | planned | actual |
|---|---|---|---|
| · | `src/core/candidate.py` | `run_candidate_artifact_generation`: `ledger_task_key = f"us | — |
| · | `src/core/boards.py` | Same prefix pattern in `run_board_search_generation` | — |
| · | `tests/component/core/test_candidate.py` | Assert ledger receives `user-<task_key>` and `batch_id` star | — |
| · | `tests/component/core/test_boards_generate_ast521.py` | New: core tests for `run_board_search_generation` ledger pre | — |
