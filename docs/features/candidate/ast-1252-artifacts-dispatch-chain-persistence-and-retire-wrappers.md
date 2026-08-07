# Artifacts dispatch chain, persistence, and retire wrappers

**Linear:** [AST-1252](https://linear.app/astralcareermatch/issue/AST-1252/artifacts-dispatch-chain-persistence-and-retire-wrappers-candidate)  
**Parent:** [AST-1243](https://linear.app/astralcareermatch/issue/AST-1243/candidate-artifacts-now-daisy-chain) — Candidate Artifacts now daisy chain  
**Publish ref:** `sub/AST-1243/AST-1252-artifacts-dispatch-chain`

Wire `REQUESTED_ARTIFACTS` so dispatch opens at live `craft_get_rubric`, follows `agent_task.run_next` (no hop-order list in `config.py`), persists each craft hop into candidate artifact fields the way job `BUILD_ARTIFACTS` persists per hop, surfaces hop progress in execution history via per-hop ledgers, graduates to `ARTIFACTS_READY` (or fails to retry/error), and removes all live `candidate_requested_artifacts` / `candidate_requested_resume` task-key wiring. `REQUESTED_RESUME` and `REQUESTED_ARTIFACTS` stay selectable triggers for `craft_get_rubric` with no new pairing validation. Does **not** own Generate/Regenerate UI (AST-1253). Resume daisy-chain generation stays out of scope.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Retire wrapper TASK_CONFIG keys; point `CANDIDATE_STAGE_DISPATCH` artifacts at `craft_get_rubric`; drop live resume stage entry; add wrappers to `DISPATCH_RETIRED_TASK_KEYS`; fix trigger/entity helpers + asserts | utils |
| `src/core/agent.py` | On dispatch craft chain: per-hop persist hook + debug found/recorded; keep UI `suppress_run_next` untouched | core |
| `src/core/candidate.py` | Rewrite `run_requested_artifacts_dispatch` to single `do_task(craft_get_rubric)` (native `run_next`); remove `run_requested_resume_dispatch`; debug per hop | core |
| `src/core/consult.py` | Route candidate entity on `craft_get_rubric` / stage `task_key`; drop resume-wrapper route | core |
| `src/core/dispatcher.py` | Stage AUTO-off debug / any stage-key sets use new `task_key`; add provision/retire for old wrapper dispatch rows → `craft_get_rubric`@`REQUESTED_ARTIFACTS` | core |
| `data/admin/agent_task.json` | Remove `candidate_requested_resume` / `candidate_requested_artifacts` rows (or mark non-current); leave craft `run_next` chain as on `origin/dev` | data |

**Out of this ticket’s file list (do not touch):** frontend Generate/Regenerate (AST-1253), `tests/` / bible (Betty), job `BUILD_ARTIFACTS` behavior, hop-order lists in config, resume daisy-chain prompts.

## Stage 1: Config — retire wrappers; entry hop is `craft_get_rubric`

**Done when:** `rg 'candidate_requested_(resume|artifacts)' src/` returns zero product references as live dispatch keys (retired set / comments naming the retired strings are OK only inside `DISPATCH_RETIRED_TASK_KEYS` and retire messages); `CANDIDATE_STAGE_DISPATCH` has a single live stage entry for artifacts whose `task_key` and entry craft key are both `craft_get_rubric`, trigger `REQUESTED_ARTIFACTS`, pass `ARTIFACTS_READY`, `auto_mode` False; no `craft_task_keys` list; `dispatch_task_admin_defaults("craft_get_rubric")` yields `entity_type="candidate"` and default `trigger_state="REQUESTED_ARTIFACTS"`; `_dispatch_task_key_trigger_error` / admin create still allow `craft_get_rubric` + `REQUESTED_RESUME` (trigger in `CANDIDATE_STATES`, no new pairing block); `python3 -m py_compile src/utils/config.py` succeeds.

1. In `src/utils/config.py`, delete TASK_CONFIG entries `candidate_requested_resume` and `candidate_requested_artifacts`.
2. Replace `CANDIDATE_STAGE_DISPATCH` with artifacts-only (drop `requested_resume` live entry — resume daisy-chain / wrapper worker are out of scope; `REQUESTED_RESUME` state remains in `CANDIDATE_STATES`):
   - `"requested_artifacts": { "task_key": "craft_get_rubric", "trigger_state": "REQUESTED_ARTIFACTS", "pass_state": "ARTIFACTS_READY", "auto_mode": False, "craft_task_key": "craft_get_rubric" }`
   - Comment: entry hop only; succession via live `agent_task.run_next`; no hop-order list.
3. Update the module-level assert under `CANDIDATE_STAGE_DISPATCH` to require only the artifacts `task_key` / `craft_task_key` membership in `TASK_CONFIG` (and `auto_mode` falsy assert still covers remaining entries).
4. Add `"candidate_requested_resume"` and `"candidate_requested_artifacts"` to `DISPATCH_RETIRED_TASK_KEYS`. Add retire messages in `_RETIRED_DISPATCH_TASK_KEY_REPLACEMENTS` (or static messages) directing operators to `craft_get_rubric` with `REQUESTED_ARTIFACTS` (and noting `REQUESTED_RESUME` remains a valid trigger choice for that task_key).
5. Update `_dispatch_trigger_state_for_task_key` / `_dispatch_entity_type_for_task_key` so `craft_get_rubric` resolves via the stage entry (`trigger_state=REQUESTED_ARTIFACTS`, `entity_type=candidate`). Remove branches that keyed off the old wrapper `task_key` strings. Do **not** add validation that forbids `REQUESTED_RESUME` as a create-time trigger for `craft_get_rubric` (admin `_dispatch_task_key_trigger_error` already only checks registry membership — leave that alone).
6. Do **not** add any craft-hop sequencing list/frozenset in config. Do **not** change `CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY` / rubric maps except as needed if a helper referenced the old stage `craft_task_key` value `craft_company_search_terms` as the artifacts entry (entry is now `craft_get_rubric`).

⚠️ **Decision:** Dispatch `task_key` **is** the chain entry hop (`craft_get_rubric`), matching job `BUILD_ARTIFACTS` / `contemplate_job`. Wrapper keys are retired, not aliased forever. Resume wrapper + `run_requested_resume_dispatch` go away with this epic; operators may still bind `REQUESTED_RESUME` to `craft_get_rubric` in Scheduled Actions without new validation — running that pairing as a resume builder is out of scope.

## Stage 2: Agent persist hook + artifacts dispatch worker (native `run_next`)

**Done when:** Dispatch path for `REQUESTED_ARTIFACTS` calls `do_task("craft_get_rubric", …)` **once** with **no** `suppress_run_next`, so child hops open hop ledgers (BUILD_ARTIFACTS-comparable execution history); each successful craft hop persists via `_persist_craft_dispatch_success` before the next hop; terminal success transitions the candidate to `ARTIFACTS_READY`; failure uses `_requested_stage_failure_target` (primary → retry, else error); UI `run_candidate_artifact_generation` still passes `suppress_run_next=True` (single-hop generate until AST-1253); `debug=True` emits per-hop found/recorded Style D lines; `run_requested_resume_dispatch` is removed; `python3 -m py_compile` on touched core modules succeeds.

1. In `src/core/agent.py`, after a successful craft hop has `parsed_response` (same success region as job artifact pin / before or beside `_write_dispatch_hop_label_on_success`), when `(ctx or {}).get("persist_candidate_craft_hops")` is truthy and `index` is set:
   - Call `candidate._persist_craft_dispatch_success(index, task_key, parsed)` (late-import `src.core.candidate` to avoid cycles, same style as tracker pin import).
   - On persist `ValueError` / unexpected failure: treat as hop failure (do not continue `run_next`); surface error on the result the same way other post-success failures do in this function.
   - When `debug=True`: Style D `debug_index` / `debug_detail` for this hop — found (task_key, artifact key or search-terms path) and recorded (truncated payload via `truncate_debug_content` when long). No new debug lines when `debug=False`.
2. Do **not** set `dispatch_chain_graduate_on_terminal` for this candidate path (job graduation map stays job-only). Do **not** write job hop labels for candidates (`_should_write_dispatch_hop_label` stays `entity_type == "job"`).
3. In `src/core/candidate.py`, rewrite `run_requested_artifacts_dispatch`:
   - Load candidate; resolve stage from `CANDIDATE_STAGE_DISPATCH["requested_artifacts"]`.
   - Build `task_ctx` from candidate dict plus `"persist_candidate_craft_hops": True` and ensure candidate id is visible to hop ledgers (`astral_candidate_id` / index = candidate_id — match whatever existing craft/`do_task` already expects for this module).
   - **Do not** set `suppress_run_next`.
   - `await do_task(task_key=stage["craft_task_key"], live_content="", index=candidate_id, ctx=task_ctx, debug=debug)`.
   - On success: `transition_candidate_state(candidate_id, stage["pass_state"])`; return passed counts.
   - On failure: existing `_requested_stage_failure_target` + transition; return failed/error counts.
   - Delete the manual `while craft_key` walk that used `suppress_run_next`.
4. Delete `run_requested_resume_dispatch` and any imports/callers of it.
5. Leave `_persist_craft_dispatch_success` behavior for rubric keys + `craft_company_search_terms` (+ `craft_resume_base` if still used by UI) unchanged except as required by the hook call site.
6. Confirm `run_candidate_artifact_generation` still passes `suppress_run_next=True` so Manage UI one-shot craft does not fan the whole chain.

⚠️ **Decision:** Dispatch uses native `do_task` `run_next` (hop ledgers + `run_next hop:` lines) with an explicit persist flag — not the AST-1113 manual walk — so execution history matches `BUILD_ARTIFACTS` feel. UI generate keeps suppress. Graduation stays in the candidate worker (not `DISPATCH_CHAIN_TERMINAL_GRADUATION`) so job chain map stays uncontaminated.

## Stage 3: Consult routing + dispatcher provision/retire + admin JSON

**Done when:** `run_consult_task` for `entity_type=candidate` routes `dispatch_task_key == craft_get_rubric` (stage `task_key`) to `run_requested_artifacts_dispatch` and no longer routes wrapper keys; dispatcher stage-key sets / AUTO-off debug use the new key; boot or provision path retires live `dispatch_task` rows whose `task_key` is a retired wrapper and ensures template + candidates-with-rows have `(craft_get_rubric, REQUESTED_ARTIFACTS)` with `auto_mode=False` (seed law); `data/admin/agent_task.json` no longer carries live wrapper task rows; `rg 'candidate_requested_(resume|artifacts)' src/ data/admin/agent_task.json` shows only retire messaging / absence; `python3 -m py_compile` on touched files succeeds.

1. In `src/core/consult.py`, replace wrapper `task_key` branches with a match on `CANDIDATE_STAGE_DISPATCH["requested_artifacts"]["task_key"]` → `run_requested_artifacts_dispatch`. Remove resume-wrapper import/route.
2. In `src/core/dispatcher.py`:
   - Update `_debug_log_auto_off_stage_skips` (and any other `CANDIDATE_STAGE_DISPATCH` task_key frozensets) for the new key.
   - Add `ensure_candidate_artifacts_dispatch_tasks(candidate_id)` (name may match existing meteorite ensure style): idempotent insert of `(craft_get_rubric, REQUESTED_ARTIFACTS)` via `dispatch_task_admin_defaults` + `save_dispatch_task` with `auto_mode=False`; delete rows on that candidate whose `task_key` is in the retired wrapper set.
   - Add `provision_candidate_artifacts_dispatch_tasks()` mirroring meteorite provision: template candidate first, then every candidate that already has ≥1 dispatch row; invoke from the same scheduler/boot hook that previously provisioned stage rows (or the current peer provision call site next to meteorite/gaze_email — if stage provision was removed, wire beside `provision_meteorite_dispatch_tasks` in `start_scheduler` / tick setup).
3. In `data/admin/agent_task.json`, remove the `candidate_requested_resume` and `candidate_requested_artifacts` objects entirely (do not leave them as current rows). Do **not** reorder the live craft `run_next` chain in this ticket — trust `origin/dev` topology headed by `craft_get_rubric`.
4. Do not edit React/UI handoff (AST-1253). Do not edit `tests/` or bible.

⚠️ **Decision:** Provision retires wrapper rows rather than leaving zombies that still match old keys in the DB. New seed AUTO stays **off** (`astral.dispatch.seed-auto-false`).

## Execution contract

- Stages in order; one commit per stage on the epic worktree sub; publish to `origin/sub/AST-1243/AST-1252-artifacts-dispatch-chain` after each stage per build-child.
- No files outside the Files Changed table.
- Ambiguity or drift → stop and comment on **parent** AST-1243 with the Stage N blocked template.
- Betty owns test/bible updates after Code Complete — engineer does not patch `tests/`.

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — retires two live dispatch task keys, rewires candidate stage orchestration onto `craft_get_rubric`, and changes how craft hops persist/ledger during dispatch (utils + core + admin seed).

**Conf:** `high` — entry hop and `run_next` authority already exist on `origin/dev`; persist helper and stage failure targets already exist; BUILD_ARTIFACTS hop-ledger behavior is the explicit template; AST-1113 suppress remains only for UI one-shot.

**Risk:** `HIGH` — wrong persist placement skips mid-chain artifact writes or double-writes; retiring resume wrapper removes the old REQUESTED_RESUME → craft_resume_base automation; provision mistakes leave operators on dead task_keys or auto-on seeds.

## Self-review vs ASTRAL_CODE_RULES

- **§2.6.0 / `astral.dispatch.run-next-is-chain-authority`:** Succession from live `agent_task.run_next` only; no craft-hop list in config.
- **`astral.state.no-daisy-chain-in-run`:** Uses documented `run_next` carve-out inside `do_task`; worker does one transition to ready/retry/error after the chain returns.
- **§2.1 / §1.4:** States and stage entry key in config; no hardcoded hop sets.
- **§1.5.1 debug contract:** Gated `debug=True` found/recorded per hop; truncation for long payloads.
- **§1.3 / layers:** Persist stays in candidate; hook late-imports from agent; consult routes; dispatcher provisions.
- **Betty test-tree ban:** No `tests/` / bible edits in this plan.
- **No conflict requiring conf-!!-NONE.**
