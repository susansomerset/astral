<!-- linear-archive: AST-863 archived 2026-07-29 -->

## Linear archive (AST-863)

**Archived:** 2026-07-29  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-863/uat-contemplate-job-unhandled-from-build-artifactsanticipate-scan-mid  
**Status at archive:** Archive  
**Project:** Astral Roster  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-752 — Use agent_data for the "caller" content  
**Blocked by / blocks / related:** parent: AST-752

### Description

## What failed

Manual Run on dispatch task `contemplate_job` with trigger state `BUILD_ARTIFACTS.anticipate_scan` shows Avail=1, but dispatch processes zero jobs. Console logs:
`run_consult_task: unhandled task_key=contemplate_job for input_state=BUILD_ARTIFACTS.anticipate_scan` then `Loop mode contemplate_job: 0 processed — stopping`.

## Expected

Mid-chain resume-artifact dispatch from compound holding state `BUILD_ARTIFACTS.anticipate_scan` routes `contemplate_job` through the dispatch-chain consult path, runs `do_task` for the claimed job using stored upstream `agent_data` for caller tokens, and advances or fails with a domain error — not an unhandled consult routing warning with zero processed.

## Repro

1. Have a job in `BUILD_ARTIFACTS.anticipate_scan` with upstream artifact hops already completed (Susan: candidate `somerset`, Avail=1 on contemplate_job dispatch row for that trigger state).
2. Admin → Scheduled Actions → Run on that dispatch task (POST `/api/admin/dispatch_tasks/11172/run`).
3. Observe `run_consult_task: unhandled task_key=contemplate_job for input_state=BUILD_ARTIFACTS.anticipate_scan` and 0 processed.

## Parent AC (quoted inline)

> 3. Given an entity whose upstream hop(s) already completed successfully in a prior dispatch, starting dispatch at the next downstream hop completes without re-running upstream LLM calls — caller tokens come from stored `agent_data`.
> 4. Given a chain that failed on hop *N* after hop *N−1* stored successfully, retrying from hop *N* (or re-dispatching at hop *N*) succeeds using stored caller content from hop *N−1* — no manual chain reconstruction.
> 5. AST-597 resume-artifact mid-chain entry behavior is preserved through the refactored general hydration path (no parallel resume-only branch left behind).

## Boundaries

* Does not change Manage Tasks prompt text or `run_next` wiring on agent_task rows.
* Does not change flat `BUILD_ARTIFACTS` entry dispatch (Generate Artifacts from RECOMMENDED) unless required for parity.
* Does not re-open AST-828 batch-claim validation scope unless claim succeeds but consult still no-ops.

## Git branch (authoritative)

Parent **ftr/AST-752-agent-data-caller-content**; child **sub/AST-752/<bug-id>-<slug>**. Seed from **origin/ftr/AST-752-agent-data-caller-content**.

### Comments

#### betty — 2026-07-11T00:22:58.164Z
## QA test manifest (AST-863)

**Publish:** `origin/sub/AST-752/AST-863-contemplate-job-mid-chain-dispatch` @ `5b5973e`
**Tests commit:** `origin/tests` @ `7e85bf0`

1. `tests/component/utils/test_config.py::TestAst863MidChainHopLabelChainTrigger` — `is_dispatch_chain_trigger` / `dispatch_chain_registry_trigger` / mid-chain claim states
2. `tests/component/core/test_consult.py::TestAst534DispatchTaskKeyHonesty::test_contemplate_job_hop_label_trigger_routes_chain_batch` — hop-label `input_state` routes `_run_dispatch_chain_job_batch`
3. `tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch::test_dispatch_chain_batch_hop_label_input_sets_registry_trigger` — ctx `dispatch_trigger_state=BUILD_ARTIFACTS`

**Regression:** `TestAst849DispatchChainClaimStates`, `TestAst534DispatchTaskKeyHonesty::test_mid_chain_hop_label_routes_dispatch_chain_batch`

**Bible shasums (publish ref):**
- `docs/test-bible/utils/config.md` → `e5873d94602717dc242826cb22cd25de059d4537`
- `docs/test-bible/core/consult.md` → `dba731c1d3fda81effa5c01822083d9bb28ce01a`

**Narrowed run:**
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst863MidChainHopLabelChainTrigger \
  tests/component/utils/test_config.py::TestAst849DispatchChainClaimStates \
  tests/component/core/test_consult.py::TestAst534DispatchTaskKeyHonesty::test_contemplate_job_hop_label_trigger_routes_chain_batch \
  tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch::test_dispatch_chain_batch_hop_label_input_sets_registry_trigger \
  -q
```

— Betty

#### hedy — 2026-07-11T00:19:24.411Z
**Plan doc:** [`docs/features/roster/ast-863-uat-contemplate-job-mid-chain-dispatch.md`](https://github.com/susansomerset/astral/blob/sub/AST-752/AST-863-contemplate-job-mid-chain-dispatch/docs/features/roster/ast-863-uat-contemplate-job-mid-chain-dispatch.md)

**Root cause:** `is_dispatch_chain_trigger` only accepts bare `BUILD_ARTIFACTS`; mid-chain dispatch rows with `trigger_state=BUILD_ARTIFACTS.anticipate_scan` claim successfully but `run_consult_task` hits the unhandled branch before `_run_dispatch_chain_job_batch`.

**Fix (2 stages):** Add `dispatch_chain_registry_trigger`; extend chain-trigger predicate; normalize `dispatch_trigger_state` ctx to registry key; narrow mid-chain claim states to the row label only.

**Self-Assessment**
- **Scope:** Single-Component — config normalization + consult/dispatcher routing gates.
- **Conf:** high — reproduced locally (`is_dispatch_chain_trigger False` while row match True).
- **Risk:** low — entry-row `BUILD_ARTIFACTS` behavior preserved via registry branch in claim helper.

---

# AST-863 — UAT: contemplate_job dispatch no-ops on BUILD_ARTIFACTS.anticipate_scan mid-chain trigger

- **Linear:** [AST-863 — UAT: contemplate_job dispatch no-ops on BUILD_ARTIFACTS.anticipate_scan mid-chain trigger](https://linear.app/astralcareermatch/issue/AST-863/uat-contemplate-job-dispatch-no-ops-on-build-artifactsanticipate-scan-mid)
- **Parent:** [AST-752 — Use agent_data for the "caller" content](https://linear.app/astralcareermatch/issue/AST-752/use-agent-data-for-the-caller-content)
- **Publish ref:** `origin/sub/AST-752/AST-863-contemplate-job-mid-chain-dispatch`
- **UAT bug of:** [AST-752](https://linear.app/astralcareermatch/issue/AST-752/use-agent-data-for-the-caller-content) — Susan staging run 2026-07-10 (`contemplate_job-37a65399-5527-45b9-b437-8546b2985402`, candidate `somerset`, Avail=1)
- **Related:** [AST-848](https://linear.app/astralcareermatch/issue/AST-848) / [AST-849](https://linear.app/astralcareermatch/issue/AST-849) (dispatch-chain `do_task` routing + claim), [AST-828](https://linear.app/astralcareermatch/issue/AST-828) (batch claim validation for hop labels — claim succeeds here; consult routing fails)

Manual Run on dispatch task **`contemplate_job`** with **`trigger_state='BUILD_ARTIFACTS.anticipate_scan'`** shows **Avail=1**, claims one job, then processes zero: **`run_consult_task: unhandled task_key=contemplate_job for input_state=BUILD_ARTIFACTS.anticipate_scan`** and **`Loop mode contemplate_job: 0 processed — stopping`**.

**Root cause:** AST-848/849 dispatch-chain routing gates on **`is_dispatch_chain_trigger(input_state)`**, which only recognizes bare registry triggers in **`DISPATCH_CHAIN_TERMINAL_GRADUATION`** (e.g. **`BUILD_ARTIFACTS`**). Susan's mid-chain dispatch row uses the hop holding label **`BUILD_ARTIFACTS.anticipate_scan`** as **`trigger_state`**. Claim/count succeed (**`is_valid_job_batch_claim_state`** + **`dispatch_chain_row_matches_job`** return true), but **`run_consult_task`** falls through to the unhandled branch because **`is_dispatch_chain_trigger('BUILD_ARTIFACTS.anticipate_scan')`** is false. **`_run_dispatch_chain_job_batch`** never runs; **`do_task`** never starts.

**Boundaries:** Fix dispatch-chain trigger normalization and consult/dispatcher routing only — mid-chain rows whose **`trigger_state`** is a hop holding label must route through **`_run_dispatch_chain_job_batch`** and pass registry **`dispatch_trigger_state=BUILD_ARTIFACTS`** into **`do_task`** ctx. Does not change Manage Tasks **`run_next`** wiring, hop prompts, or caller hydration (**AST-769**). Does not re-open AST-828 batch-claim validation unless claim regresses.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add **`dispatch_chain_registry_trigger`**; extend **`is_dispatch_chain_trigger`**; fix **`dispatch_chain_claim_states_for_row`** for mid-chain row triggers | utils |
| `src/core/consult.py` | Route mid-chain hop-label **`input_state`** through **`_run_dispatch_chain_job_batch`**; pass registry trigger into ctx | core |
| `src/core/dispatcher.py` | Use registry trigger for post-claim chain filter when row **`trigger_state`** is a hop label | core |

**Verify only (Betty / qa-child — engineer does not edit in build-child):**

| File | Change |
|------|--------|
| `tests/component/utils/test_config.py` | Assert **`is_dispatch_chain_trigger('BUILD_ARTIFACTS.anticipate_scan')`** true; **`dispatch_chain_registry_trigger`** returns **`BUILD_ARTIFACTS`** |
| `tests/component/core/test_consult.py` | Mid-chain row: **`run_consult_task`** with **`input_state=BUILD_ARTIFACTS.anticipate_scan`**, **`dispatch_task_key=contemplate_job`** invokes **`_run_dispatch_chain_job_batch`** (mock), not unhandled zero |

**No changes expected:** `src/core/agent.py` (already reads **`dispatch_trigger_state`** from ctx), `src/core/tracker.py`, `src/data/database.py`, admin UI beyond existing hop-label validation in **`api_admin.py`**.

---

## Stage 1: Confirm routing gap (investigation — no product commit unless regression)

**Done when:** Engineer records **`is_dispatch_chain_trigger('BUILD_ARTIFACTS.anticipate_scan') == False`** while **`dispatch_chain_row_matches_job(...)`** and claim path accept the label; **`run_consult_task`** log line matches Susan's repro.

1. Read-only repro:
   ```bash
   python3 -c "
   from src.utils.config import (
       is_dispatch_chain_trigger, parse_dispatch_hop_label,
       dispatch_chain_row_matches_job, dispatch_chain_claim_states_for_row,
   )
   ts = 'BUILD_ARTIFACTS.anticipate_scan'
   print('is_dispatch_chain_trigger', is_dispatch_chain_trigger(ts))
   print('parse', parse_dispatch_hop_label(ts))
   print('claim_states', dispatch_chain_claim_states_for_row(ts, 'contemplate_job'))
   print('matches', dispatch_chain_row_matches_job(ts, 'contemplate_job', ts))
   "
   ```
   Expect: **`is_dispatch_chain_trigger False`**, **`parse ('BUILD_ARTIFACTS', 'anticipate_scan')`**, **`claim_states ['BUILD_ARTIFACTS.anticipate_scan']`**, **`matches True`**.

2. Confirm consult gate:
   ```bash
   rg -n "is_dispatch_chain_trigger|unhandled task_key" src/core/consult.py
   ```
   Expect single chain branch guarded by **`is_dispatch_chain_trigger((input_state or '').strip())`**.

3. **Stop gate:** If **`is_dispatch_chain_trigger('BUILD_ARTIFACTS.anticipate_scan')`** is already true on this branch — post 🛑 on **AST-752** with evidence; different root cause (likely **`do_task`** / hydration).

---

## Stage 2: Normalize hop-label triggers and wire consult/dispatcher routing

**Done when:** Manual Run on **`contemplate_job`** / **`BUILD_ARTIFACTS.anticipate_scan`** reaches **`_run_dispatch_chain_job_batch`** → **`do_task('contemplate_job', …)`** with **`ctx['dispatch_trigger_state']=='BUILD_ARTIFACTS'`**; bare **`BUILD_ARTIFACTS`** entry rows unchanged; **`python3 -m py_compile`** on touched files passes.

1. In **`src/utils/config.py`**, immediately after **`dispatch_chain_graduation_target`** (~line 3063), add:

   ```python
   def dispatch_chain_registry_trigger(trigger_state: str) -> str | None:
       """Registry trigger (e.g. BUILD_ARTIFACTS) for bare or hop-label dispatch row trigger_state."""
       ts = (trigger_state or "").strip()
       if not ts:
           return None
       if dispatch_chain_graduation_target(ts) is not None:
           return ts
       parsed = parse_dispatch_hop_label(ts)
       if parsed and dispatch_chain_graduation_target(parsed[0]) is not None:
           return parsed[0]
       return None
   ```

2. Replace **`is_dispatch_chain_trigger`** body (~line 3067):

   ```python
   def is_dispatch_chain_trigger(trigger_state: str) -> bool:
       return dispatch_chain_registry_trigger((trigger_state or "").strip()) is not None
   ```

3. In **`dispatch_chain_claim_states_for_row`** (~line 3086), after resolving **`registry = dispatch_chain_registry_trigger(ts)`**:
   - If not **`registry`**: return **`[ts]`** if **`ts`** else **`[]`** (unchanged fallback).
   - If **`parse_dispatch_hop_label(ts)`** is not **`None`** (mid-chain row — trigger **is** the holding label): return **`[ts]`** only.
   - Else (chain-entry row with bare registry trigger): keep existing logic — **`[ts]`** plus **`dispatch_hop_label(registry, parent)`** for each parent from **`_agent_task_parents_with_run_next(tk)`**, de-duped.

   ⚠️ **Decision:** Mid-chain rows claim exactly the hop label on the dispatch row; entry rows keep expanded parent hop labels from AST-849.

4. In **`src/core/consult.py`**, update **`_run_dispatch_chain_job_batch`** (~line 1646):
   - **`row_trigger = (input_state or "").strip()`**
   - **`registry_trigger = dispatch_chain_registry_trigger(row_trigger) or row_trigger`**
   - Use **`row_trigger`** as first arg to **`dispatch_chain_row_matches_job`**
   - Set **`task_ctx['dispatch_trigger_state'] = registry_trigger`** (not **`row_trigger`**)

   Add import: **`dispatch_chain_registry_trigger`** from **`src.utils.config`**.

5. In **`run_consult_task`** chain branch (~line 1822), no structural change needed once **`is_dispatch_chain_trigger`** recognizes hop labels — verify the branch fires for **`BUILD_ARTIFACTS.anticipate_scan`**.

6. In **`src/core/dispatcher.py`**, post-claim filter (~line 230): when filtering entities, pass **`row_trigger=(input_state or '').strip()`** to **`dispatch_chain_row_matches_job`** unchanged; gate on **`is_dispatch_chain_trigger(row_trigger)`** (now true for hop labels).

7. Compile:
   ```bash
   python3 -m py_compile src/utils/config.py src/core/consult.py src/core/dispatcher.py
   ```

8. Manual sanity (engineer): re-run Stage 1 snippet — expect **`is_dispatch_chain_trigger True`**; dispatch Run logs **`do_task(contemplate_job)`** start, not unhandled warning.

---

## Self-Assessment

**Scope:** `Single-Component` — config trigger normalization plus two consult/dispatcher routing call sites; no agent hydration or prompt changes.

**Conf:** `high` — Reproduced locally; claim/match helpers already accept hop labels; gap is exclusively **`is_dispatch_chain_trigger`** gate before **`_run_dispatch_chain_job_batch`**.

**Risk:** `low` — Bare **`BUILD_ARTIFACTS`** entry rows use unchanged expanded claim list; mid-chain rows only widen the chain-trigger predicate and fix **`dispatch_trigger_state`** ctx to registry key **`do_task`** already expects.

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Single **`dispatch_chain_registry_trigger`** helper; **`is_dispatch_chain_trigger`** delegates — no duplicated parse logic in consult/dispatcher. |
| §2.1 Config as source of truth | Registry map stays **`DISPATCH_CHAIN_TERMINAL_GRADUATION`**; hop labels resolve to registry key in config only. |
| §2.4 Batch processing | Claim expansion for mid-chain rows narrowed to **`[ts]`** — avoids over-claiming sibling hop labels. |
| §2.6 State machine | No **`JOB_STATES`** registry changes; hop labels remain runtime holding states. |
| §3.3 Imports | Lazy **`get_agent_task`** pattern unchanged; consult adds one config symbol. |
| §3.5 Naming | **`dispatch_chain_registry_trigger`** vs row hop label **`trigger_state`** distinction explicit in plan steps. |

No conflicts requiring plan revision.

---

## Review

**Diff:** `origin/ftr/AST-752-agent-data-caller-content...origin/sub/AST-752/AST-863-contemplate-job-mid-chain-dispatch` @ `002156f`

| Area | Notes |
|------|-------|
| Stage 2 | `dispatch_chain_registry_trigger`; `is_dispatch_chain_trigger` accepts hop labels; mid-chain claim `[ts]` only; `dispatch_trigger_state` ctx uses registry key |
| Boundaries | No agent/hydration changes; entry-row `BUILD_ARTIFACTS` claim expansion preserved |

Betty manifest green @ `0742e21`. Awaiting Radia **review-child**.

---

## Resolution

**Date:** 2026-07-11  
**Sub-log hygiene:** Republished from `origin/ftr/AST-752-agent-data-caller-content` — linear AST-863 commits only; no `Merge remote-tracking branch` in ftr..sub range.

**Product:** mid-chain hop-label dispatch-chain trigger routing (`05a2dc8`).  
**Tests:** Betty manifest 6/6 green (`706b117`).

**§9a dry-run:** pending Radia review + merge-child.
