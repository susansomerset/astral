# Per-hop transitions and agent_data mid-chain resume

**Linear:** [AST-597](https://linear.app/astralcareermatch/issue/AST-597/per-hop-transitions-and-agent-data-mid-chain-resume-need-to-pick-up)  
**Parent:** [AST-593](https://linear.app/astralcareermatch/issue/AST-593/need-to-pick-up-and-parse-daisy-chained-prompts-from-the-middle-using)  
**Publish ref (origin):** `sub/AST-593/AST-597-agent-data-mid-chain-resume`

After each successful resume-artifact `run_next` hop, transition the job to the next compound **`BUILD_ARTIFACTS.<task_key>`** state (registry from **AST-595**). When dispatch starts at a mid-chain hop, seed **`chain_context`** with **`{$CALLER_*}`** values rebuilt from persisted **`agent_data`** for the immediate upstream hop — no LLM re-run for hops already completed in a prior successful run. With **`debug=True`**, emit Style D hop index lines and detail lines that distinguish **agent_data reuse** vs **live LLM** caller content.

**Sibling boundaries (do not implement here):** compound **`JOB_STATES`** / **`hop_task_keys`** (**AST-595**); dispatch claim, **`BUILD_FAILED`** removal, batch release on hop failure (**AST-596**); Execution History UI (**AST-528**); terminal **`finalize_job_resume`** persist rules (**AST-552** — unchanged).

## Prerequisite gate (mandatory before Stage 1)

**AST-595** helpers must exist on **`dev-ada`** (merged from **`origin/ftr/AST-593-mid-chain-artifact-resume`** or sibling **`sub/AST-593/AST-595-*`**):

```bash
python3 -c "from src.utils.config import resume_artifact_hop_task_keys, resume_artifact_next_compound_state; k=resume_artifact_hop_task_keys(); print(resume_artifact_next_compound_state(k[0]))"
```

Expected: **`BUILD_ARTIFACTS.contemplate_job`** (or the compound state for the hop after **`hop_task_keys[0]`** per **AST-595** plan).

If import fails or flat **`BUILD_ARTIFACTS`** is still the only in-progress state: **stop**, comment on **AST-597** naming **AST-595**, do not patch **`config.py`** here.

**AST-596** is **not** a build blocker for Stages 1–4 (hydration + per-hop transitions). Full parent AC #3 (failure release) and consult **`BUILD_FAILED`** removal require **AST-596** before UAT sign-off — note in Linear comment after Code Complete.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/agent.py` | Resume-chain caller hydration from **`agent_data`**; seed **`run_resume_artifact_chain_for_job`**; per-hop **`transition_job_state`** after successful hop; Style D debug lines on resume hops | core |

**Out of scope — do not touch:**

| Area | Owner ticket |
|------|----------------|
| `src/utils/config.py` compound states / **`hop_task_keys`** | **AST-595** |
| `src/core/consult.py` **`BUILD_FAILED`**, batch release, terminal batch exit shape | **AST-596** |
| `src/core/dispatcher.py` claim / **`trigger_state`** guard | **AST-596** |
| `src/core/tracker.py` (unless a one-line import-only change is impossible — prefer **`transition_job_state`** already on tracker) | — |
| `tests/`, **`docs/ASTRAL_TEST_BIBLE.md`**, frontend | Betty after Code Complete |

## Stage 1: Resume-chain hydration helpers (`agent.py`)

**Done when:** Pure helpers load caller tokens from a job's stored hop row; unit-testable without LLM; no **`do_task`** wiring yet.

Add a private section **after** `_chain_tokens_for_next_hop` (near existing chain helpers):

1. **`_resume_artifact_parent_hop_key(entry_task_key: str) -> Optional[str]`**
   - Import **`resume_artifact_hop_task_keys`** from **`src.utils.config`** (inside function or module top with existing config imports).
   - Let **`keys = resume_artifact_hop_task_keys()`**.
   - If **`entry_task_key not in keys`**: return **`None`** (not a resume hop — caller skips hydration).
   - **`idx = keys.index(entry_task_key)`**; return **`None`** if **`idx == 0`**, else **`keys[idx - 1]`**.

2. **`_latest_job_hop_agent_ref(job: Dict[str, Any], hop_task_key: str) -> Optional[Dict[str, Any]]`**
   - Read **`entries = job.get("agent_responses") or []`** (newest last in DB — scan **reversed**).
   - Match **`e.get("task_key") == hop_task_key`** and **`e.get("prompt_blocks")`** is a non-empty list containing at least one block with **`type == "RESPONSE"`**.
   - Skip entries whose RESPONSE **`block_data`** (if already inlined) starts with **`Validation failed:`** or **`Required caller token`** — those are failed hops.
   - Return the first matching entry dict, or **`None`**.

   ⚠️ **Decision:** Prefer **`job["agent_responses"]`** refs ( **`append_agent_response`** path from **AST-531** hop **`batch_id`**) over scanning **`dispatch_ledger`** — refs already tie **`task_key`** + **`prompt_blocks`** to the job row.

3. **`_block_text_by_type(prompt_blocks: List[Dict], block_type: str) -> str`**
   - Given **`prompt_blocks`** `[{type, id}, …]`, collect ids for matching **`type`**, batch-fetch via **`database.get_agent_data_for_ids(ids)`** (import from **`src.data.database`** — same as **`roster.get_entity_agent_story`**).
   - Return stripped **`block_data`** for the **first** matching block; **`""`** if missing.
   - For multiple blocks of same type (rare), use first in list order (matches story expansion).

4. **`_parsed_response_from_stored_response_text(text: str, task_key: str) -> Any`**
   - Mirror **`do_task`** success unwrap used before **`_chain_tokens_for_next_hop`**:
     - Try **`json.loads(text)`** when text looks like JSON.
     - If dict with **`agent_payload`**, replace with inner payload; if inner is list, join with **`"\n".join(str(x) for x in parsed)`** (same as ~1472–1476 in **`do_task`**).
     - Else return string or parsed value unchanged.

5. **`_caller_chain_context_from_hop_agent_ref(agent_ref: Dict[str, Any], parent_task_key: str) -> Dict[str, str]`**
   - Load blocks from **`agent_ref["prompt_blocks"]`**:
     - **`system = _block_text_by_type(..., "SYSTEM")`**
     - **`cache_a` … `cache_d`** from **`CACHE_A`** … **`CACHE_D`**
     - **`response_raw = _block_text_by_type(..., "RESPONSE")`**
   - **`parsed = _parsed_response_from_stored_response_text(response_raw, parent_task_key)`**
   - Return **`_chain_tokens_for_next_hop(resolved_system=system, resolved_cache_a=cache_a, …, parsed=parsed)`** plus sentinel:
     - **`"_caller_hydration_source": "agent_data"`**
     - **`"_hop_parent_task_key": parent_task_key`**

6. **`_hydrate_resume_entry_chain_context(astral_job_id: str, entry_task_key: str) -> Tuple[Optional[Dict[str, str]], Optional[str]]`**
   - Returns **`(chain_context, error)`** — **`error`** set when mid-chain entry requires parent data but hydration failed.
   - **`parent = _resume_artifact_parent_hop_key(entry_task_key)`**; if **`parent is None`**: return **`({}, None)`** (first hop or non-resume key).
   - **`job = tracker.get_job(astral_job_id)`** (lazy **`from src.core import tracker`**); if no job: return **`(None, f"Job not found: {astral_job_id}")`**.
   - **`ref = _latest_job_hop_agent_ref(job, parent)`**; if **`ref is None`**: return **`(None, f"No stored agent_data for upstream hop {parent!r} on job {astral_job_id}")`**.
   - Build context via **`_caller_chain_context_from_hop_agent_ref(ref, parent)`**; if all **`CALLER_*`** values empty after build, return **`(None, f"Stored hop {parent!r} has empty caller payload")`**.
   - Return **`(ctx, None)`**.

⚠️ **Decision:** Only the **immediate** upstream hop in **`hop_task_keys`** order is hydrated. That matches **`run_next`** caller-token semantics (each hop consumes direct parent output). Resuming at **`draft_job_resume`** loads **`advise_job_resume`** only — not a full replay of **`anticipate_scan` → …**.

## Stage 2: Seed mid-chain entry in `run_resume_artifact_chain_for_job`

**Done when:** Calling with **`first_task_key`** set to a mid-chain hop preloads **`chain_context`**; first hop in chain still gets **`chain_context=None`**; hydration failure returns **`success: False`** without LLM.

1. In **`run_resume_artifact_chain_for_job`**, after **`entry_key`** is validated and **`job`** / **`cd`** resolved, before building **`task_ctx`**:

   ```python
   seed_chain: Optional[Dict[str, str]] = None
   parent = _resume_artifact_parent_hop_key(entry_key)
   if parent:
       hydrated, err = _hydrate_resume_entry_chain_context(astral_job_id, entry_key)
       if err:
           return {"success": False, "error": err, "api_response": None, "parsed_response": None, "timesheet": {}}
       seed_chain = hydrated
   ```

2. Pass to **`do_task`**:

   ```python
   return await do_task(
       entry_key,
       index=astral_job_id,
       ctx=task_ctx,
       debug=debug,
       store_agent_data=store_agent_data,
       chain_context=seed_chain,
   )
   ```

3. Do **not** change **`run_cover_letter_artifact_chain_for_job`** — cover letter out of scope.

4. Do **not** change default **`first_task_key`** when omitted — still **`BUILD_CONFIG['resume_artifact_chain']['first_task_key']`** (**AST-534** dispatch row override unchanged).

## Stage 3: Per-hop compound state transition after successful hop

**Done when:** After hop **`task_key`** succeeds (validation complete, before **`run_next`** recursion), job moves to **`resume_artifact_next_compound_state(task_key)`** when that hop is in **`resume_artifact_hop_task_keys()`**; last hop (**`finalize_job_resume`**) does **not** transition here (**`resume_artifact_next_compound_state`** returns **`None`** per **AST-595**); terminal **`CANDIDATE_REVIEW`** remains **`consult._run_job_artifact_entry_batch`**.

1. Import **`resume_artifact_hop_task_keys`**, **`resume_artifact_next_compound_state`** from **`src.utils.config`**.

2. Add **`_maybe_transition_resume_hop_progress(task_key: str, astral_job_id: Optional[str]) -> None`**:
   - No-op unless **`astral_job_id`**, **`task_key in resume_artifact_hop_task_keys()`**.
   - **`next_compound = resume_artifact_next_compound_state(task_key)`**; if **`next_compound is None`**: return (terminal hop).
   - Lazy **`from src.core import tracker`**; **`tracker.transition_job_state([astral_job_id], next_compound)`**.
   - On **`ValueError`**: **`logger.warning("resume hop transition failed job=%s from_hop=%s to=%s: %s", …)`** — do **not** fail the hop after LLM success (state drift is operational; Susan can fix data).

3. Call site: in **`do_task`**, on the **success path** after RESPONSE storage / **`_store_agent_response`**, immediately **before** computing **`hop_ctx = _chain_tokens_for_next_hop(...)`** (~1617):

   ```python
   if result.get("success") and entity_type == "job" and index:
       _maybe_transition_resume_hop_progress(task_key, index)
   ```

4. Do **not** call on failure returns or on early validation exits.

5. Do **not** transition to **`CANDIDATE_REVIEW`** or **`BUILD_FAILED`** here.

⚠️ **Decision:** Transition fires **after** hop **`task_key`** succeeds, **before** child hop runs — job row shows completed hop *N* and next entry *N+1* while the synchronous chain continues in one dispatch (parent AC #1).

## Stage 4: Style D debug — hop index and caller source (`agent.py`)

**Done when:** With **`debug=True`** on a resume-artifact chain run, each executed hop in **`resume_artifact_hop_task_keys()`** logs one Style D index header and at least one **` | `** detail line stating **`caller_source=agent_data`** or **`caller_source=live_llm`**.

1. At module level in **`agent.py`**, import **`get_logger`**, **`format_debug_index_header`** from **`src.utils.logging`** (if not already).

2. Add **`_resume_hop_debug_index(task_key: str, *, debug: bool) -> None`**:
   - No-op if not **`debug`** or **`task_key not in resume_artifact_hop_task_keys()`**.
   - **`keys = resume_artifact_hop_task_keys()`**; **`idx = keys.index(task_key) + 1`**; **`total = len(keys)`**.
   - **`dbg = get_logger(__name__, debug_flag=True)`** (only called when **`debug`**).
   - **`dbg.debug_index(func=f"do_task({task_key})", index=idx, total=total, identifier=task_key, outcome="hop")`**.

3. In **`do_task`**, after **`task_config = TASK_CONFIG[task_key]`** and **`in_chain`** resolved, call **`_resume_hop_debug_index(task_key, debug=debug)`**.

4. After **`_cc = _chain_context(agent_row, chain_context)`** (caller tokens resolved for this hop), when **`debug and task_key in resume_artifact_hop_task_keys()`**:
   - Determine **`source = (chain_context or {}).get("_caller_hydration_source") or ("live_llm" if (chain_context or {}).get("_hop_parent_task_key") else "chain_entry")`**.
   - **`get_logger(__name__, debug_flag=True).debug_detail(f"caller_source={source} parent={(chain_context or {}).get('_hop_parent_task_key') or 'none'} caller_keys={_caller_key_status(_cc)}")`**
   - When **`source == "agent_data"`**, add **`debug_detail(f"caller_hydration=agent_data upstream={(chain_context or {}).get('_hop_parent_task_key')}")`**.
   - When parent hop ran in same batch (live **`hop_ctx`** merge), child hop should show **`caller_source=live_llm`** (no **`_caller_hydration_source`** on child incoming context).

5. When building **`hop_ctx`** for **`run_next`** (~1627), if **`debug`**: **`debug_detail("caller_hydration=live_llm parent=%s" % task_key)`** on the **child-boundary** path (after successful LLM, before inner **`do_task`**). Keep existing **`_log_run_next_hop_boundary`** INFO line (production coexistence per **ASTRAL_CODE_RULES §1.5.1**).

6. Do **not** add new **`logger.info("[DEBUG] …")`** strings — use **`debug_index` / `debug_detail`** only.

## Stage 5: Verify (product compile + Betty handoff note)

**Done when:** Touched module compiles; no edits to **`tests/`**.

1. **`python3 -m py_compile src/core/agent.py`**

2. Linear comment for Betty (**post Code Complete**, do not edit tests in this ticket):

   - **`tests/component/core/test_agent.py`**: mid-chain **`run_resume_artifact_chain_for_job(first_task_key="draft_job_resume")`** with mocked parent **`agent_responses`** + **`get_agent_data_for_ids`** — assert **zero** LLM calls for upstream hop; **`chain_context`** populated; **`_maybe_transition_resume_hop_progress`** called with expected compound state after a mocked successful hop.
   - Extend existing hop-boundary tests: per-hop transition invoked once per successful resume hop.
   - Debug test: with **`debug=True`**, caplog contains Style D header and **`caller_source=agent_data`** on resumed entry.
   - Regression: full chain from first hop still transitions through compound states; terminal **`CANDIDATE_REVIEW`** still from consult batch (unchanged).

## Execution contract (for the developer agent)

- Execute stages in order. **Stop** on prerequisite failure — comment on **AST-597**, tag **AST-595** blocked-by.
- Do **not** edit **`config.py`**, **`consult.py`**, **`dispatcher.py`**, **`tracker.py`** (except if compile forces a re-export — unlikely), **`tests/`**, or UI.
- Do **not** remove or alter **`finalize_job_resume`** persist / **`CANDIDATE_REVIEW`** batch exit in **`consult.py`**.
- When hydration cannot find upstream **`agent_data`**, return **`success: False`** with clear **`error`** string — do **not** call LLM and hope (**AST-530** mid-chain empty-caller guard is second line of defense).
- Blocking ambiguity → comment on **AST-593** parent with **`🛑 Stage N blocked:`** template from **plan-astral**.

## Self-Assessment

**Scope — `Single-Component`**  
All product changes live in **`src/core/agent.py`** (hydration, entry seed, per-hop transition, debug). No config or dispatch edits.

**Conf — `Medium`**  
**AST-531** storage shape and **`_chain_tokens_for_next_hop`** are established; dependency on **AST-595** helper names is documented and gated. Hydration edge cases (failed RESPONSE rows, JSON unwrap) need careful mirroring of existing **`do_task`** paths.

**Risk — `HIGH`**  
Incorrect caller hydration causes silent empty **`{$CALLER_*}`** or expensive full-chain re-runs; wrong transition timing breaks **AST-596** dispatch **`trigger_state`** alignment and recommended-list progress display.

## Self-review vs ASTRAL_CODE_RULES

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Reuses **`_chain_tokens_for_next_hop`**, **`get_agent_data_for_ids`**, **`tracker.transition_job_state`** — no parallel token builder. |
| §1.5.1 debug | Style D via **`get_logger(..., debug_flag=debug)`**; no new unguarded **`[DEBUG]`** info lines. |
| §2.1 config | Hop order read only via **AST-595** helpers — no new config keys in this ticket. |
| §2.6 state machine | Transitions only through **`tracker.transition_job_state`** to **AST-595** compound states. |
| §2.4 batch | Entity claim / release unchanged (**AST-596**). |
| §3.3 imports | **`agent.py`** may import **`database.get_agent_data_for_ids`** (core→data allowed); lazy **`tracker`** import preserved for cycles. |
| §3.5 naming | **`_hydrate_*`**, **`_resume_artifact_*`** prefix distinguishes from consult/roster chains. |

No unresolved conflicts — plan assumes **AST-595** land first; **AST-596** required for full parent failure AC before UAT.

## Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-593/AST-597-agent-data-mid-chain-resume`  
**Product commit:** `e8e88c30` — agent_data caller hydration for mid-chain `run_resume_artifact_chain_for_job`; `_maybe_transition_resume_hop_progress` after each successful resume hop; Style D `caller_source` debug lines

## Radia review (2026-06-12)

**Diff:** `origin/dev...origin/sub/AST-593/AST-597-agent-data-mid-chain-resume` (5 commits; product `e8e88c30`, tests `c1c24299`, bible `b1dc4b0c`)

### What's solid

| Area | Notes |
| --- | --- |
| Plan fidelity | Stages 1–4 land in `agent.py` only; hydration helpers, mid-chain seed in `run_resume_artifact_chain_for_job`, per-hop `tracker.transition_job_state`, Style D hop index + caller detail — matches combined plan. |
| Hydration | Reuses `_chain_tokens_for_next_hop` + `get_agent_data_for_ids`; failed RESPONSE rows skipped via prefix tuple; mid-chain miss returns `success: False` without LLM (AC #2 guard). |
| Token safety | `_chain_context` omits `_`-prefixed sentinels from prompt resolution — `_caller_hydration_source` / `_hop_parent_task_key` do not reach `{$CALLER_*}` substitution. |
| §2.6 / §3.3 | Lazy `tracker` imports preserved; transitions only via `resume_artifact_next_compound_state` + `transition_job_state`. |
| §1.5.1 | Resume-hop `debug_index` / `debug_detail` gated on `debug=True`; no new `[DEBUG]` info strings in touched paths. |
| Tests | `TestAst597MidChainResumeHydrationAndTransitions` + consult terminal regression named in bible — covers hydration, transition, debug, hydration-failure skip. |

### Issues

| Sev | Location | Finding |
| --- | --- | --- |
| **fix-now** | `agent.py` — `_merge_chain_context_for_next_hop` + resume debug source (~1815) | Mid-chain seed sets `_caller_hydration_source=agent_data`. Parent merge copies that key into child `chain_context`. Child-hop debug uses `(chain_context or {}).get("_caller_hydration_source") or …`, so hop 2+ in the **same** dispatch can log `caller_source=agent_data` while caller tokens came from live LLM — contradicts plan Stage 4 (“child hop should show `live_llm`”). Strip `_caller_hydration_source` when merging for `run_next` (or overwrite before inner `do_task`). |
| **discuss** | `agent.py` — `_maybe_transition_resume_hop_progress` call site (~1731) | Compound transition fires on **any** successful job `do_task` whose `task_key` is in `resume_artifact_hop_task_keys()`, not gated on resume-artifact chain / `in_chain`. Confirm these keys are never run outside the resume chain; otherwise add a gate. |
| **discuss** | Land order vs `origin/dev` | Imports `resume_artifact_hop_task_keys` / `resume_artifact_next_compound_state` from **AST-595** (`origin/sub/AST-593/AST-595-*`); not on `origin/dev` yet. Rollup **595 → ftr → 597** before dev land (plan prerequisite; Linear blockedBy **AST-595**). |
| **advisory** | `_parsed_response_from_stored_response_text` | `task_key` parameter unused — harmless; drop or use in a follow-up cleanup. |
| **advisory** | `_maybe_transition_resume_hop_progress` | `ValueError` on transition → warning only (per plan). UAT with **AST-596** should confirm compound `trigger_state` stays aligned when transition fails silently. |

### Recommended actions (resolve-astral)

1. **fix-now:** In `_merge_chain_context_for_next_hop` (or immediately before inner `do_task`), omit `_caller_hydration_source` from merged context so chained-hop debug reports `caller_source=live_llm` per plan.
2. **discuss:** Confirm resume hop `task_key`s are chain-exclusive, or gate `_maybe_transition_resume_hop_progress` on resume chain context.
3. No product changes needed for AST-595 ordering — ensure sibling lands on ftr before this sub merges to dev.

## Resolution

**Resolved:** 2026-06-12 (Ada)

| Radia item | Action |
| --- | --- |
| **fix-now** — strip `_caller_hydration_source` on `run_next` merge | `_merge_chain_context_for_next_hop` omits `_caller_hydration_source` from parent context so hop 2+ debug shows `caller_source=live_llm`. |
| **discuss** — transition gate outside resume chain | No change — resume hop keys are resume-artifact chain only per plan; UAT if a stray path appears. |
| **discuss** — AST-595 land order | Orchestration — sibling rollup before dev land; no code change in this ticket. |
| **advisory** | Deferred — unused `task_key` param; transition warning-only per plan. |
