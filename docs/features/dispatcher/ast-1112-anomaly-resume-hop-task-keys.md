# Anomaly — resume hop_task_keys shadow

**Linear:** [AST-1112](https://linear.app/astralcareermatch/issue/AST-1112/anomaly-resume-hop-task-keys-shadow-hard-coded-daisy-chain-in-configpy)  
**Parent:** [AST-1109](https://linear.app/astralcareermatch/issue/AST-1109/hard-coded-daisy-chain-in-configpy) — Hard-coded daisy chain in config.py  
**Publish ref:** `sub/AST-1109/AST-1112-anomaly-resume-hop-task-keys`

Retire `BUILD_CONFIG.resume_artifact_chain.hop_task_keys` / `_RESUME_ARTIFACT_HOP_TASK_KEYS` / `resume_artifact_hop_task_keys()` as chain-membership and hop-succession authority. Resume/artifact parent resolution and hop succession on this surface come from live `agent_task.run_next` (existing §2.6.0 helpers). Does **not** delete `JOB_ARTIFACT_ENTRY_TASK_KEYS` / craft_task_keys (siblings AST-1111 / AST-1113). Does **not** author statutes (AST-1110 already landed `astral.dispatch.run-next-is-chain-authority`).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Delete hop-key tuple + BUILD_CONFIG key + `resume_artifact_hop_task_keys()`; stop deriving legacy compound lists from that tuple; rewrite `legacy_build_artifacts_hop` + trigger-default membership; drop dead compound helpers / `_RAH` asserts | utils |
| `src/core/agent.py` | Remove all `resume_artifact_hop_task_keys` imports/usages; parent/succession via run_next helpers only; simplify debug hop index fallback | core |

## Stage 1: Config — delete hop-list authority

**Done when:** `_RESUME_ARTIFACT_HOP_TASK_KEYS`, `BUILD_CONFIG["resume_artifact_chain"]["hop_task_keys"]`, and `resume_artifact_hop_task_keys()` are gone; no product path in `config.py` consults a hop-order list for membership/succession; `python3 -m py_compile src/utils/config.py` passes.

1. In `src/utils/config.py`, **delete** the module-level tuple `_RESUME_ARTIFACT_HOP_TASK_KEYS` (currently ~lines 152–159, the six resume hop strings).

2. In `BUILD_CONFIG["resume_artifact_chain"]`, **keep** `"first_task_key": "contemplate_job"` and **delete** the `"hop_task_keys": _RESUME_ARTIFACT_HOP_TASK_KEYS` entry. Update the adjacent comment so it still says dispatch entry TASK_CONFIG key only; further hops via `run_next` — do **not** mention `hop_task_keys`.

3. **Delete** the function `resume_artifact_hop_task_keys()` entirely (including its `KeyError` for missing `hop_task_keys`).

4. **Delete** `_legacy_build_artifacts_compound_state_names()`, the module binding `_LEGACY_BUILD_ARTIFACTS_COMPOUND_STATES`, and every `*_LEGACY_BUILD_ARTIFACTS_COMPOUND_STATES` unpack inside `JOB_STATES` `prior_states` lists (`RECOMMENDED`, `ERROR_BUILD_ARTIFACTS`, `BUILD_FAILED`, `CANDIDATE_REVIEW`, `CANDIDATE_APPLIED`, `CANDIDATE_SKIPPED`). Leave `BUILD_ARTIFACTS_BASE_STATE` / `ERROR_BUILD_ARTIFACTS_STATE` entries as they are today.

   ⚠️ **Decision:** Explicit compound-state spreads are redundant with `tracker._job_state_matches_prior`, which already treats any `legacy_build_artifacts_hop(state)` as matching when `BUILD_ARTIFACTS_BASE_STATE` is in `prior_states`. Removing the spreads avoids a second hop-membership catalog while preserving in-flight `BUILD_ARTIFACTS.<hop>` transitions.

5. Keep `_legacy_build_artifacts_compound_state_for_hop(task_key)` and `resume_artifact_compound_state(task_key)` as pure formatters (`f"{LEGACY_BUILD_ARTIFACTS_PREFIX}{task_key}"`) — they do **not** assert membership in a hop list.

6. Rewrite `legacy_build_artifacts_hop(state: str) -> str | None`:
   - If `state` does not start with `LEGACY_BUILD_ARTIFACTS_PREFIX`, return `None`.
   - Let `hop = state[len(LEGACY_BUILD_ARTIFACTS_PREFIX):]`.
   - Return `hop` if `hop` is non-empty **and** `hop in TASK_CONFIG`; else `None`.
   - Do **not** call any hop-list helper.

7. In `_dispatch_task_default_trigger_state`, replace `if task_key in resume_artifact_hop_task_keys(): return BUILD_ARTIFACTS_BASE_STATE` with:

   ```python
   _tc = TASK_CONFIG.get(task_key) or {}
   if _tc.get("task_type") == "CHAIN" and _tc.get("error_state") == ERROR_BUILD_ARTIFACTS_STATE:
       return BUILD_ARTIFACTS_BASE_STATE
   ```

   Leave the subsequent `draft_cover_letter` / cover-letter mid-hop `CANDIDATE_REVIEW` branches unchanged and still **after** this check.

   ⚠️ **Decision:** Membership for admin/default trigger uses existing TASK_CONFIG orchestration markers (`task_type` + `error_state`) already on the resume CHAIN hops — not a parallel hop-order list and not `JOB_ARTIFACT_ENTRY_TASK_KEYS` (AST-1111 owns that frozenset). Cover-letter tasks lack `task_type: CHAIN` / `ERROR_BUILD_ARTIFACTS` today, so they keep their dedicated `CANDIDATE_REVIEW` defaults.

8. **Delete** unused helpers that only existed to re-export the hop-derived compound tuple: `build_artifacts_claim_states()` and `all_resume_artifact_compound_states()`. Grep confirms no `src/` callers outside their definitions.

9. Replace the module-tail `_RAH = resume_artifact_hop_task_keys()` block and its three asserts with:

   ```python
   _rac = BUILD_CONFIG.get("resume_artifact_chain") or {}
   _rac_first = (_rac.get("first_task_key") or "").strip()
   assert _rac_first and _rac_first in TASK_CONFIG
   assert (TASK_CONFIG[_rac_first] or {}).get("entity_type") == "job"
   assert all(v in JOB_STATES for v in DISPATCH_CHAIN_TERMINAL_GRADUATION.values())
   for _tk, _tc in TASK_CONFIG.items():
       _tt = (_tc or {}).get("task_type")
       if _tt is not None:
           assert _tt in TASK_TYPES, f"TASK_CONFIG[{_tk!r}].task_type invalid: {_tt!r}"
   ```

   (Preserve any adjacent asserts that were not hop-list-specific; do not reintroduce hop-key iteration.)

10. Do **not** edit `JOB_ARTIFACT_ENTRY_TASK_KEYS`, `build_artifacts_chain_task_keys()`, `cover_letter_artifact_chain`, craft stage lists, statutes, or CODE_RULES.

11. Grep `src/` for `resume_artifact_hop_task_keys`, `_RESUME_ARTIFACT_HOP_TASK_KEYS`, and `hop_task_keys` — only allowed remaining hits after Stage 2 are comments/docs outside this ticket’s files, or zero. Product code must have zero.

## Stage 2: Agent — succession and debug without hop list

**Done when:** `agent.py` has no import or call of `resume_artifact_hop_task_keys`; parent resolution for resume hydration uses run_next parents only; `python3 -m py_compile src/core/agent.py src/utils/config.py` passes.

1. In `src/core/agent.py`, remove `resume_artifact_hop_task_keys` from the `src.utils.config` import list.

2. **Delete** `_resume_artifact_parent_hop_key` entirely (it walks the retired hop-order tuple).

3. In `_parent_hop_task_key_for_child`:
   - Keep the single-match path (`len(matches) == 1` → return that parent).
   - When `len(matches) > 1`: **remove** the `if child_task_key in resume_artifact_hop_task_keys(): return _resume_artifact_parent_hop_key(...)` branch. Always log the existing warning and return `None`.
   - Zero matches → return `None` (unchanged).

   ⚠️ **Decision:** Live seed topology is a linear `run_next` chain (one parent per child). Ambiguous parents are a data error; do not paper over them with a config hop-order tie-break (that was the shadow authority).

4. In `_hydrate_resume_entry_chain_context`, replace `parent = _resume_artifact_parent_hop_key(entry_task_key)` with `parent = _parent_hop_task_key_for_child(entry_task_key)`. Keep the `parent is None → ({}, None)` short-circuit and the `_hydrate_caller_chain_context(...)` call unchanged.

5. In `_do_task_debug_entry`, remove the `if task_key in resume_artifact_hop_task_keys():` branch that computed `hop_idx` / `hop_total` from the hop tuple. Always use the existing non-hop path (`index=1`, `total=1`, outcome `"task start"`) for the Style D header when this helper runs. Keep the `debug_detail` line with `in_run_next_chain=...` unchanged.

6. In `_resume_hop_debug_index`:
   - Keep the early return when `not debug`.
   - Keep the dispatch-trigger path (`_dispatch_chain_ctx` → `_dispatch_chain_hop_debug_counts`) unchanged.
   - When there is **no** dispatch trigger: **delete** the `if task_key not in resume_artifact_hop_task_keys(): return` / hop-tuple index block. Simply `return` (no Style D hop index from a config list). Dispatch-chain debug remains the authority when `ctx` carries `dispatch_trigger_state` (AST-855).

7. Grep `src/core/agent.py` and `src/utils/config.py` for `resume_artifact_hop_task_keys`, `_RESUME_ARTIFACT_HOP_TASK_KEYS`, `_resume_artifact_parent_hop_key`, `hop_task_keys` — expect **no** matches.

8. Run `python3 -m py_compile src/utils/config.py src/core/agent.py` (use the project venv if needed). Do **not** edit `tests/` or bible paths — Betty owns those if manifests break on the retired helper name.

## Self-Assessment

**Scope:** Single-Component — `config.py` hop-list retirement plus `agent.py` succession/debug call-site cleanup on the resume-artifact surface only.

**Conf:** high — statute `astral.dispatch.run-next-is-chain-authority` is active; every product consumer of `resume_artifact_hop_task_keys` is in these two files; §2.6.0 claim/match helpers already use `run_next`.

**Risk:** Medium — wrong parent resolution would break mid-chain caller-token hydration on BUILD_ARTIFACTS hops; linear `run_next` topology and existing `_parent_hop_task_key_for_child` keep the blast radius to that path.

## CODE_RULES self-review

| Rule | Status |
|------|--------|
| §1.3 DRY | Pass — delete duplicate hop-order authority; reuse `_parent_hop_task_key_for_child` / `_agent_task_parents_with_run_next` pattern |
| §2.1 config | Pass — `first_task_key` + TASK_CONFIG task specs remain; hop-order list removed as shadow topology |
| §2.4 batch | Pass — no batch API signature changes |
| §2.6 / §2.6.0 | Pass — succession via `run_next`; claim/match helpers untouched; statute pointer already on CODE_RULES from AST-1110 |
| §3.3 imports | Pass — drop config import of deleted helper; no new layer violations |
| §3.5 naming | Pass — no new public APIs; dead helpers removed |
| `astral.standards.in-scope-only` | Pass — no JOB_ARTIFACT_ENTRY / craft / statute edits |
| `astral.standards.no-hardcoded-sets` | Pass — not “moving the set into config”; deleting the shadow |
