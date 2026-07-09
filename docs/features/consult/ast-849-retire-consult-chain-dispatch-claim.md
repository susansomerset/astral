# Retire consult chain wrapper and dispatch claim for DB hop labels

**Linear:** [AST-849 — Retire consult chain wrapper and dispatch claim for DB hop labels](https://linear.app/astralcareermatch/issue/AST-849/retire-consult-chain-wrapper-and-dispatch-claim-for-db-hop-labels-unify)  
**Parent:** [AST-847 — Unify BUILD_ARTIFACTS chain in do_task (per-hop state + terminal graduation)](https://linear.app/astralcareermatch/issue/AST-847/unify-build-artifacts-chain-in-do-task-per-hop-state-terminal) (AC reference only — do not expand epic scope)  
**Publish ref:** `origin/sub/AST-847/AST-849-retire-consult-chain-dispatch-claim`

Remove the consult-only BUILD_ARTIFACTS chain orchestrator (`do_chain_for_job`, `_run_build_artifacts_chain_batch`, and all `_chain_*` helpers). Wire **generic** dispatcher and tracker claim/validation so jobs at runtime `<trigger_state>.<hop>` DB labels (written by sibling **AST-848** `do_task` recursion) are claimable and counted correctly. Consult and dispatcher invoke **`do_task` only** — no parallel chain wrapper, no post-run graduation, no persist gate, no separate cover-letter batch path.

**Prerequisite (blockedBy):** [AST-848](./ast-848-do-task-run-next-chain.md) must be **built, published, and merged into `origin/ftr/AST-847-unify-build-artifacts-chain-do-task`** before **build-child** on this ticket. AST-848 owns `do_task` recursion, per-hop DB writes, terminal graduation, and the `dispatch_trigger_state` / `dispatch_chain_graduate_on_terminal` ctx contract. This ticket owns dispatch claim/validation and consult/dispatcher routing only.

**Supersedes (remove, do not extend):** AST-803 consult chain wrapper; AST-844 consult graduation fixes; `_run_craft_job_cover_letter_batch` routing; `build_artifacts_claim_states()` dispatcher expansion; `resume_artifact_hop_task_keys()` claim guards in dispatcher/admin; all `_chain_*` / `do_chain_for_job` machinery in `consult.py`.

**Out of scope:** `do_task` recursion / hop writes / terminal graduation (**AST-848**); hop prompts or `run_next` graph edits; `JOB_STATES` compound hop registry; `tests/` edits (Betty at Code Complete); post-run artifact body harvest into `job_data`.

**Related:** [AST-848 plan on publish ref](https://github.com/susansomerset/astral/blob/sub/AST-847/AST-848-do-task-run-next-chain/docs/features/consult/ast-848-do-task-run-next-chain.md), [AST-803](./ast-803-build-artifacts-chain-dispatch.md), [AST-828](../roster/ast-828-uat-draft-cover-letter-compound-state-claim.md) (claim-only hop labels).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `dispatch_chain_claim_states_for_row`, `dispatch_chain_row_matches_job`, `is_dispatch_chain_trigger`; retire `build_artifacts_claim_states` dispatcher usage | utils |
| `src/data/database.py` | `count_eligible_for_dispatch_task` uses chain claim states for dispatch-chain trigger rows | data |
| `src/core/dispatcher.py` | Generic chain claim + row/job validation; remove `resume_artifact_hop_task_keys` guard | core |
| `src/core/tracker.py` | Generalize `list_dispatch_tasks_for_candidate` hop-label filter | core |
| `src/core/consult.py` | Delete chain wrapper; `_run_dispatch_chain_job_batch` → `do_task` only | core |
| `src/ui/api/api_admin.py` | Generic dispatch row validation for chain hops | ui |

**Verify only (no change expected unless AST-848 drift):**

| File | Role |
|------|------|
| `src/core/agent.py` | Chain recursion + graduation — **AST-848** |
| `src/core/roster.py` | Non-chain `run_next` (`select_job_page` → `parse_job_list`) unchanged |

**Tests:** Betty owns **`tests/`** — engineer does **not** edit test files. Stage 6 documents Betty manifest additions.

---

## Stage 0: Merge AST-848 and verify integration contract

**Done when:** `origin/sub/AST-847/AST-848-do-task-run-next-chain` is merged into epic worktree; `parse_dispatch_hop_label`, `dispatch_hop_label`, `DISPATCH_CHAIN_TERMINAL_GRADUATION`, `write_job_dispatch_hop_label`, `graduate_job_from_dispatch_chain` exist; `do_task` reads `dispatch_trigger_state` and `dispatch_chain_graduate_on_terminal` from ctx per AST-848 plan §3a.

1. On epic worktree:
   ```bash
   git fetch origin
   git merge origin/sub/AST-847/AST-848-do-task-run-next-chain
   ```
2. Confirm AST-848 symbols (read-only):
   ```bash
   rg -n "parse_dispatch_hop_label|write_job_dispatch_hop_label|dispatch_chain_graduate_on_terminal" src/utils/config.py src/core/tracker.py src/core/agent.py
   ```
3. **Stop gate:** If merge conflicts or AST-848 symbols missing — post 🛑 on **AST-849** naming missing prerequisite; do not implement claim logic against pre-848 code.

⚠️ **Decision:** Do not re-implement AST-848 helpers in this ticket — extend config only for **claim/count/validation**, not hop writes or graduation.

---

## Stage 1: Config — generic dispatch-chain claim and row matching

**Done when:** `dispatch_chain_claim_states_for_row("BUILD_ARTIFACTS", "contemplate_job")` returns `["BUILD_ARTIFACTS", "BUILD_ARTIFACTS.anticipate_scan"]` when agent_task `anticipate_scan.run_next == "contemplate_job"`; `dispatch_chain_row_matches_job` returns True for job at `BUILD_ARTIFACTS.anticipate_scan` and dispatch row `(BUILD_ARTIFACTS, contemplate_job)`; `python3 -m py_compile src/utils/config.py` passes.

1. In `src/utils/config.py`, import `get_agent_task` only inside functions (lazy — config must not import data at module load; match existing `legacy_build_artifacts_hop` pattern).

2. Add:
   ```python
   def is_dispatch_chain_trigger(trigger_state: str) -> bool:
       """True when trigger_state has a terminal graduation map entry (dispatch run_next chain)."""
       return dispatch_chain_graduation_target((trigger_state or "").strip()) is not None
   ```

3. Add `_agent_task_parents_with_run_next(child_task_key: str) -> tuple[str, ...]`:
   - Lazy-import `database.list_agent_tasks` (or iterate `TASK_CONFIG` keys and `get_agent_task` each — prefer single DB list if available).
   - Return sorted unique parent `task_key` values where `(row.get("run_next") or "").strip() == child_task_key`.

4. Add:
   ```python
   def dispatch_chain_claim_states_for_row(trigger_state: str, task_key: str) -> list[str]:
       """Job states eligible for claim on this dispatch row (bare trigger + parent hop labels)."""
       ts = (trigger_state or "").strip()
       tk = (task_key or "").strip()
       if not ts or not tk or not is_dispatch_chain_trigger(ts):
           return [ts] if ts else []
       states: list[str] = [ts]
       for parent in _agent_task_parents_with_run_next(tk):
           states.append(dispatch_hop_label(ts, parent))
       # De-dupe preserve order
       seen: set[str] = set()
       out: list[str] = []
       for s in states:
           if s not in seen:
               seen.add(s)
               out.append(s)
       return out
   ```

5. Add:
   ```python
   def dispatch_chain_row_matches_job(
       trigger_state: str,
       task_key: str,
       job_state: str,
   ) -> bool:
       """True when job_state is claimable for this dispatch chain row before do_task runs."""
       ts = (trigger_state or "").strip()
       tk = (task_key or "").strip()
       st = (job_state or "").strip()
       if not ts or not tk:
           return False
       if st == ts:
           return True
       parsed = parse_dispatch_hop_label(st)
       if not parsed:
           return False
       label_trigger, completed_hop = parsed
       if label_trigger != ts:
           return False
       parent_row = get_agent_task(completed_hop) or {}
       return (parent_row.get("run_next") or "").strip() == tk
   ```

6. Keep `legacy_build_artifacts_hop` / `build_artifacts_claim_states` for backward-compatible reads in tracker graduation (AST-848) — **remove dispatcher import** of `build_artifacts_claim_states` in Stage 3; grep `build_artifacts_claim_states` in `src/` after Stage 3 — only config definition + tests may remain.

7. Extend `is_valid_job_batch_claim_state` if AST-848 left gap: any `parse_dispatch_hop_label(s)` where trigger is in `DISPATCH_CHAIN_TERMINAL_GRADUATION` must return True (should already hold from AST-848 Stage 1 — verify; patch only if missing).

8. `python3 -m py_compile src/utils/config.py`

⚠️ **Decision:** Claim states are derived from **live `agent_task.run_next` graph**, not `resume_artifact_hop_task_keys()` — chain topology stays DB-driven per parent AST-847.

---

## Stage 2: Data layer — eligible count uses chain claim states

**Done when:** `count_eligible_for_dispatch_task` row with `trigger_state=BUILD_ARTIFACTS`, `task_key=propose_application_responses` counts jobs at bare `BUILD_ARTIFACTS` and at parent hop labels from `dispatch_chain_claim_states_for_row`; admin **Available** column matches claim pool; `python3 -m py_compile src/data/database.py` passes.

1. In `src/data/database.py`, import `is_dispatch_chain_trigger`, `dispatch_chain_claim_states_for_row` from `src.utils.config`.

2. In `count_eligible_for_dispatch_task` (job branch), after resolving `trigger_state` / `task_key` from the row:
   - When `is_dispatch_chain_trigger(trigger_state)`:
     - `claim_states = dispatch_chain_claim_states_for_row(trigger_state, task_key)`
     - Use existing `_state_in_sql(claim_states)` / multi-state COUNT path (same as AST-641 union claim).
   - Else: keep existing `dispatch_claim_states(trigger_state, entity_type)` behavior.

3. Do **not** change `claim_job_batch` SQL shape — dispatcher passes resolved `states=` into tracker (Stage 3).

4. `python3 -m py_compile src/data/database.py`

---

## Stage 3: Dispatcher — generic chain claim and pre-claim validation

**Done when:** `_run_unified` no longer special-cases `resume_artifact_hop_task_keys()`; BUILD_ARTIFACTS artifact rows claim via `dispatch_chain_claim_states_for_row`; rows with trigger/job mismatch log skip before claim (zero-work batch avoided for terminal hops); `python3 -m py_compile src/core/dispatcher.py` passes.

1. In `src/core/dispatcher.py`, replace imports:
   - Remove: `build_artifacts_claim_states`, `legacy_build_artifacts_hop`, `resume_artifact_hop_task_keys` (if only used for chain guard).
   - Add: `dispatch_chain_claim_states_for_row`, `dispatch_chain_row_matches_job`, `is_dispatch_chain_trigger`.

2. **Delete** the pre-claim block (~lines 197–218) that compares `legacy_build_artifacts_hop(ts) == dispatch_task_key`.

3. In job claim branch (~lines 237–248), replace:
   ```python
   if (input_state or "").strip() == BUILD_ARTIFACTS_BASE_STATE:
       claim_states = list(build_artifacts_claim_states())
   ```
   with:
   ```python
   if is_dispatch_chain_trigger((input_state or "").strip()):
       claim_states = dispatch_chain_claim_states_for_row(
           (input_state or "").strip(),
           task_key_run,
       )
   ```

4. After `get_new_job_batch` returns entities, **filter** claimed jobs before `run_consult_task`:
   ```python
   if entity_type == "job" and is_dispatch_chain_trigger((input_state or "").strip()):
       entities = [
           e for e in entities
           if dispatch_chain_row_matches_job(
               (input_state or "").strip(),
               dispatch_task_key,
               (e.get("state") or ""),
           )
       ]
   ```
   If `entities` becomes empty after filter, return `_SUMMARY_ZERO` (same as no claim).

5. Preserve scored `score_floor`, `claim_cap`, AST-502 chunk exhaustion, and debug_detail `claim_states=` logging.

6. `python3 -m py_compile src/core/dispatcher.py`

⚠️ **Decision:** Post-claim filter ensures mid-chain rows do not process jobs on the wrong hop label even if SQL union claim is broader than one row.

---

## Stage 4: Tracker — dispatch task listing for hop labels

**Done when:** `list_dispatch_tasks_for_candidate(candidate_id, trigger_state="BUILD_ARTIFACTS")` returns rows whose `trigger_state` is `BUILD_ARTIFACTS` or any `BUILD_ARTIFACTS.<hop>` hop label under that trigger; `python3 -m py_compile src/core/tracker.py` passes.

1. In `src/core/tracker.py`, import `parse_dispatch_hop_label` from config.

2. In `list_dispatch_tasks_for_candidate`, replace BUILD_ARTIFACTS-only prefix check with generic:
   ```python
   if ts:
       if row_ts == ts:
           pass  # include
       else:
           parsed = parse_dispatch_hop_label(row_ts)
           if not (parsed and parsed[0] == ts):
               continue
   ```

3. Do **not** change `start_artifact_build` / `cancel_artifact_build` / `release_job_dispatch_claim`.

4. `python3 -m py_compile src/core/tracker.py`

---

## Stage 5: Consult — delete chain wrapper; `do_task`-only batch

**Done when:** Zero hits for `do_chain_for_job`, `_run_build_artifacts_chain_batch`, `_chain_dispatch_row_ok`, `_resolve_chain_start_task_key`, `_chain_graduate_to_candidate_review`, `_run_craft_job_cover_letter_batch` call sites; artifact hops route through `_run_dispatch_chain_job_batch`; `python3 -m py_compile src/core/consult.py` passes.

1. **Delete** from `src/core/consult.py` (entire functions + helpers):
   - `_chain_run_next_targets`
   - `_build_artifacts_chain_entry_task_key`
   - `_chain_entry_dispatch_task_key`
   - `_resolve_chain_start_task_key`
   - `_chain_dispatch_row_ok`
   - `_chain_failure_mode` (if unused after delete — agent owns failure routing per AST-848)
   - `_chain_fail_result`
   - `_chain_graduate_to_candidate_review`
   - `_chain_hop_has_run_next`
   - `_chain_single_hop_dispatch_only`
   - `do_chain_for_job`
   - `_run_build_artifacts_chain_batch`
   - `_run_craft_job_cover_letter_batch`
   - `_maybe_run_cover_letter_after_resume` only if unused after unified routing (grep first)
   - `_artifact_entry_hop_failed` — replace with inline `tracker.release_job_dispatch_claim(aid)` on failure

2. Add `_run_dispatch_chain_job_batch`:
   ```python
   async def _run_dispatch_chain_job_batch(
       batch_id: str,
       entities: List[Dict[str, Any]],
       ctx: Optional[Dict[str, Any]],
       debug: bool,
       dispatch_task_key: str,
       input_state: str,
   ) -> Dict[str, int]:
       from src.core.agent import _current_agent_task_run_next, do_task

       passed = errors = 0
       trigger = (input_state or "").strip()
       for job in entities:
           aid = job["astral_job_id"]
           row = tracker.get_job(aid) or job
           if not dispatch_chain_row_matches_job(
               trigger, dispatch_task_key, (row.get("state") or ""),
           ):
               continue
           cd = tracker._candidate_data_for_job(aid)
           if not cd:
               tracker.release_job_dispatch_claim(aid)
               errors += 1
               continue
           task_ctx: Dict[str, Any] = {
               **(ctx or {}),
               "batch_entities": [row],
               "batch_size": 1,
               "job": row,
               "candidate_data": cd,
               "dispatch_trigger_state": trigger,
               "dispatch_chain_graduate_on_terminal": bool(
                   _current_agent_task_run_next(dispatch_task_key)
               ),
           }
           company_key = row.get("company")
           if isinstance(company_key, str) and company_key.strip():
               co = tracker.get_company(company_key.strip())
               if co and co.get("candidate_id"):
                   task_ctx["astral_candidate_id"] = str(co["candidate_id"])
           if "vector_labels" not in task_ctx:
               task_ctx["vector_labels"] = {}
           result = await do_task(
               dispatch_task_key,
               index=aid,
               ctx=task_ctx,
               debug=debug,
           )
           if not result.get("success"):
               tracker.release_job_dispatch_claim(aid)
               errors += 1
               continue
           passed += 1
       return {
           "total_processed": len(entities),
           "total_passed": passed,
           "total_failed": 0,
           "total_errors": errors,
       }
   ```

3. In `run_consult_task`, replace job branches:
   - Remove `elif task_key == "draft_cover_letter": return await _run_craft_job_cover_letter_batch(...)`.
   - Replace `elif task_key in _JOB_ARTIFACT_ENTRY_KEYS: return await _run_build_artifacts_chain_batch(...)` with:
     ```python
     elif is_dispatch_chain_trigger((input_state or "").strip()) and task_key in TASK_CONFIG:
         return await _run_dispatch_chain_job_batch(
             batch_id, entities, ctx, debug, task_key, input_state,
         )
     ```
   - Import `is_dispatch_chain_trigger` from config; import `TASK_CONFIG` if not already present.

4. Remove unused imports: `build_artifacts_chain_task_keys`, `resume_artifact_hop_task_keys`, `is_build_artifacts_in_progress`, etc. — grep cleanup.

5. Grep `src/core/consult.py` for `_chain_`, `do_chain_for_job`, `persist_gate` — zero hits.

6. `python3 -m py_compile src/core/consult.py`

⚠️ **Decision:** No caller-hydration seeding in consult — mid-chain resume hydration stays in `do_task` / agent (AST-769). Consult sets ctx keys only; single `do_task(dispatch_task_key)` entry per job.

---

## Stage 6: Admin API — generic chain row validation

**Done when:** `_dispatch_task_key_trigger_error` accepts `trigger_state=BUILD_ARTIFACTS` for any schedulable chain hop `task_key`; rejects hop rows where `trigger_state` is a hop label but `task_key` does not match `parse_dispatch_hop_label(trigger_state)[1]`; `python3 -m py_compile src/ui/api/api_admin.py` passes.

1. In `src/ui/api/api_admin.py`, import `is_dispatch_chain_trigger`, `parse_dispatch_hop_label`, `dispatch_chain_row_matches_job` (matching only if needed for save validation).

2. Replace `resume_artifact_hop_task_keys()` block in `_dispatch_task_key_trigger_error` (~lines 1027–1029):
   ```python
   if is_dispatch_chain_trigger(ts):
       parsed = parse_dispatch_hop_label(ts)
       if parsed and parsed[1] != tk:
           return (
               f"task_key {tk!r} requires trigger_state {BUILD_ARTIFACTS_BASE_STATE!r} "
               f"or matching hop label (got {ts!r})"
           )
       if not parsed and tk not in TASK_CONFIG:
           return f"task_key {tk!r} is not a valid dispatch chain hop"
   ```
   Use generic message without hardcoding `BUILD_ARTIFACTS` in the error string:
   ```python
   if is_dispatch_chain_trigger(ts):
       parsed = parse_dispatch_hop_label(ts)
       if parsed and parsed[1] != tk:
           return f"task_key {tk!r} does not match hop in trigger_state {ts!r}"
   ```

3. `python3 -m py_compile src/ui/api/api_admin.py`

---

## Stage 7: Betty test manifest (engineer documents only — no `tests/` edits)

**Done when:** Linear comment or plan section lists manifest for qa-child; engineer does not commit test files.

Betty should extend/replace consult + dispatcher coverage for AST-849 AC #3–#6:

| Area | Suggested tests |
|------|-----------------|
| Config claim states | `TestDispatchChainClaimStates` — parent `run_next` → child maps to hop label in claim list |
| Config row match | `dispatch_chain_row_matches_job` true/false for entry vs mid-chain vs wrong hop |
| Dispatcher | Terminal hop row (`propose_application_responses`) claims job at parent hop label; no zero-work skip |
| Consult | `run_consult_task` routes artifact hop through `do_task` (mock); no `do_chain_for_job` |
| Mid-chain resume | Job at `BUILD_ARTIFACTS.<hop>` + dispatch next hop → `do_task` called once with `dispatch_chain_graduate_on_terminal` per row `run_next` |
| Regression | Non-chain consult (`qualify_job_listings`, `grade_do`) and roster `select_job_page` `run_next` unchanged |

---

## Execution contract (for build-child)

- **Merge AST-848 first** (Stage 0) — blockedBy until Ada's ticket is on `origin/ftr/AST-847-unify-build-artifacts-chain-do-task`.
- Execute stages 1–6 in order; one commit per stage on epic worktree; publish each to `origin/sub/AST-847/AST-849-retire-consult-chain-dispatch-claim`.
- Do **not** edit `src/core/agent.py` except import grep cleanup if consult drops symbols — chain behavior is **AST-848**.
- Do **not** edit `tests/` or `docs/test-bible/**`.
- If `get_agent_task` / `list_agent_tasks` graph lookup fails during claim (missing row), stop and comment on **AST-847** — do not hardcode hop order.

---

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — Removes the entire consult chain layer and rewires dispatch claim/count/validation across config, data, dispatcher, consult, tracker, and admin API; behavior depends on AST-848 `do_task` ctx contract.

**Conf:** `Medium` — AST-848 plan defines the integration surface (`dispatch_trigger_state`, hop labels, graduation); claim logic follows established AST-641 multi-state SQL and AST-828 claim-only label patterns, but live `run_next` parent lookup is new.

**Risk:** `HIGH` — Wrong claim states or row matching would skip terminal hops (UAT AC #4), break mid-chain resume (AC #3), or leave batch locks stuck; must stay aligned with `agent_task.run_next` in DB.

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Single `dispatch_chain_claim_states_for_row` + `dispatch_chain_row_matches_job`; count and claim share the same resolver. |
| §2.1 config | Chain trigger detection via `DISPATCH_CHAIN_TERMINAL_GRADUATION` (AST-848); no new state lists in dispatcher. |
| §2.4 batch | Claim → `do_task` → release on failure; `batch_id` unchanged; post-claim filter prevents wrong-hop processing. |
| §2.6 state machine | Hop labels remain claim-only; `transition_job_state` only for registered keys (graduation in AST-848). |
| §3.3 imports | Lazy `get_agent_task` inside config helpers; consult imports agent `do_task` / `_current_agent_task_run_next` only. |
| §3.5 naming | `dispatch_chain_*` prefix distinguishes from retired `_chain_*` consult helpers. |

No unresolved conflicts requiring `!!-NONE`.

---

## Review (build stub)

**Branch:** `origin/sub/AST-847/AST-849-retire-consult-chain-dispatch-claim`

**Commits:**
- `4877799` — `code(AST-849): dispatch chain claim helpers in config`
- `4b43cf7` — `code(AST-849): chain claim states in count_eligible_for_dispatch_task`
- `43ef616` — `code(AST-849): generic dispatch chain claim and row filter in dispatcher`
- `a114efb` — `code(AST-849): generic hop-label filter in list_dispatch_tasks_for_candidate`
- `b25092c` — `code(AST-849): retire consult chain wrapper; do_task-only dispatch batch`
- `7a00f8c` — `code(AST-849): generic dispatch chain row validation in admin API`

**Manual verify:** `dispatch_chain_claim_states_for_row` / `dispatch_chain_row_matches_job` drive dispatcher claim + consult `_run_dispatch_chain_job_batch`; no `do_chain_for_job` in `consult.py`.

---
