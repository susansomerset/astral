# Artifacts dispatch chain, persistence, and retire wrappers

**Linear:** [AST-1252](https://linear.app/astralcareermatch/issue/AST-1252/artifacts-dispatch-chain-persistence-and-retire-wrappers-candidate)  
**Parent:** [AST-1243](https://linear.app/astralcareermatch/issue/AST-1243/candidate-artifacts-now-daisy-chain) — Candidate Artifacts now daisy chain  
**Publish ref:** `sub/AST-1243/AST-1252-artifacts-dispatch-chain`

Wire `REQUESTED_ARTIFACTS` so dispatch opens at live `craft_get_rubric`, follows `agent_task.run_next` (no hop-order list in `config.py`), persists each craft hop into candidate artifact fields the way job `BUILD_ARTIFACTS` persists per hop, surfaces hop progress in execution history via per-hop ledgers, graduates to `ARTIFACTS_READY` (or fails to retry/error), and removes all live `candidate_requested_artifacts` / `candidate_requested_resume` task-key wiring. `REQUESTED_RESUME` and `REQUESTED_ARTIFACTS` stay selectable triggers for `craft_get_rubric` with no new pairing validation. Does **not** own Generate/Regenerate UI (AST-1253). Resume daisy-chain generation stays out of scope.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Retire wrapper TASK_CONFIG keys; point `CANDIDATE_STAGE_DISPATCH` artifacts at `craft_get_rubric` only (`task_key` = entry hop; no separate `craft_task_key`); drop live resume stage entry; add wrappers to `DISPATCH_RETIRED_TASK_KEYS`; fix trigger/entity helpers + asserts | utils |
| `src/core/agent.py` | On dispatch craft chain: per-hop persist hook + debug found/recorded; keep UI `suppress_run_next` untouched | core |
| `src/core/candidate.py` | Rewrite `run_requested_artifacts_dispatch` to single `do_task(craft_get_rubric)` (native `run_next`); remove `run_requested_resume_dispatch`; debug per hop | core |
| `src/core/consult.py` | Route candidate entity on stage `task_key` (`craft_get_rubric`); drop resume-wrapper route | core |
| `src/core/dispatcher.py` | Stage AUTO-off debug / stage-key sets use new `task_key`; **retire-only** delete of live `dispatch_task` rows whose `task_key` is a retired wrapper (no ensure/provision of replacement rows) | core |
| `data/admin/agent_task.json` | Remove `candidate_requested_resume` / `candidate_requested_artifacts` rows; leave craft `run_next` chain as on `origin/dev` | data |

**Out of this ticket’s file list (do not touch):** frontend Generate/Regenerate (AST-1253), `tests/` / bible (Betty), job `BUILD_ARTIFACTS` behavior, hop-order lists in config, resume daisy-chain prompts, auto-provision / startup seed catalogs for `(craft_get_rubric, REQUESTED_ARTIFACTS)`.

## Stage 1: Config — retire wrappers; entry hop is `craft_get_rubric`

**Done when:** `rg 'candidate_requested_(resume|artifacts)' src/` returns zero product references as live dispatch keys (retired set / comments naming the retired strings are OK only inside `DISPATCH_RETIRED_TASK_KEYS` and retire messages); `CANDIDATE_STAGE_DISPATCH` has a single live stage entry for artifacts with `"task_key": "craft_get_rubric"`, trigger `REQUESTED_ARTIFACTS`, pass `ARTIFACTS_READY`, `auto_mode` False, and **no** `craft_task_key` / `craft_task_keys` field; `dispatch_task_admin_defaults("craft_get_rubric")` yields `entity_type="candidate"` and default `trigger_state="REQUESTED_ARTIFACTS"`; `_dispatch_task_key_trigger_error` / admin create still allow `craft_get_rubric` + `REQUESTED_RESUME` (trigger in `CANDIDATE_STATES`, no new pairing block); `python3 -m py_compile src/utils/config.py` succeeds.

1. In `src/utils/config.py`, delete TASK_CONFIG entries `candidate_requested_resume` and `candidate_requested_artifacts`.
2. Replace `CANDIDATE_STAGE_DISPATCH` with artifacts-only:
   - `"requested_artifacts": { "task_key": "craft_get_rubric", "trigger_state": "REQUESTED_ARTIFACTS", "pass_state": "ARTIFACTS_READY", "auto_mode": False }`
   - Comment: entry hop only; succession via live `agent_task.run_next`; no hop-order list.
   - **Do not** add a parallel `craft_task_key` — `task_key` is the entry hop (avoids two fields holding one string).
3. Update the module-level assert under `CANDIDATE_STAGE_DISPATCH` to require only `CANDIDATE_STAGE_DISPATCH["requested_artifacts"]["task_key"]` membership in `TASK_CONFIG` (and `auto_mode` falsy assert still covers remaining entries).
4. Add `"candidate_requested_resume"` and `"candidate_requested_artifacts"` to `DISPATCH_RETIRED_TASK_KEYS`. Add retire messages in `_RETIRED_DISPATCH_TASK_KEY_REPLACEMENTS` (or static messages) directing operators to `craft_get_rubric` with `REQUESTED_ARTIFACTS` (and noting `REQUESTED_RESUME` remains a valid trigger choice for that task_key).
5. Update `_dispatch_trigger_state_for_task_key` / `_dispatch_entity_type_for_task_key` so `craft_get_rubric` resolves via the stage entry (`trigger_state=REQUESTED_ARTIFACTS`, `entity_type=candidate`). Remove branches that keyed off the old wrapper `task_key` strings. Do **not** add validation that forbids `REQUESTED_RESUME` as a create-time trigger for `craft_get_rubric` (admin `_dispatch_task_key_trigger_error` already only checks registry membership — leave that alone).
6. Do **not** add any craft-hop sequencing list/frozenset in config. Do **not** change `CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY` / rubric maps except as needed if a helper referenced the old stage entry `craft_company_search_terms` (entry is now `craft_get_rubric`).

⚠️ **Decision (intentional capability removal):** Dropping `CANDIDATE_STAGE_DISPATCH["requested_resume"]` and `run_requested_resume_dispatch` **ends** the automated `REQUESTED_RESUME` → `craft_resume_base` → `RESUME_READY` dispatch path — not merely renaming a wrapper. Parent Original brief (“pull those elements out entirely”) + child Boundaries (resume daisy-chain out of scope) authorize this. `REQUESTED_RESUME` stays in `CANDIDATE_STATES` and remains selectable as a trigger when creating a `craft_get_rubric` dispatch row (AC2); that pairing is **not** a resume builder in this epic. UI / ad-hoc `craft_resume_base` generate paths outside the retired wrapper stay as they are.

⚠️ **Decision:** Dispatch `task_key` **is** the chain entry hop (`craft_get_rubric`), matching job `BUILD_ARTIFACTS` / `contemplate_job`. Wrapper keys are retired, not aliased forever.

## Stage 2: Agent persist hook + artifacts dispatch worker (native `run_next`)

**Done when:** Dispatch path for `REQUESTED_ARTIFACTS` calls `do_task("craft_get_rubric", …)` **once** with **no** `suppress_run_next`, so child hops open hop ledgers (BUILD_ARTIFACTS-comparable execution history); each successful craft hop persists via `_persist_craft_dispatch_success` before the next hop; terminal success transitions the candidate to `ARTIFACTS_READY`; failure uses `_requested_stage_failure_target` (primary → retry, else error) with prior hops’ writes left in place (see Decision); UI `run_candidate_artifact_generation` still passes `suppress_run_next=True` (single-hop generate until AST-1253); `debug=True` emits per-hop found/recorded Style D lines; `run_requested_resume_dispatch` is removed; `python3 -m py_compile` on touched core modules succeeds.

1. In `src/core/agent.py`, after a successful craft hop has `parsed_response` (same success region as job artifact pin / before or beside `_write_dispatch_hop_label_on_success`), when `(ctx or {}).get("persist_candidate_craft_hops")` is truthy and `index` is set:
   - Call `candidate._persist_craft_dispatch_success(index, task_key, parsed)` (late-import `src.core.candidate` to avoid cycles, same style as tracker pin import).
   - On persist `ValueError` / unexpected failure: treat as hop failure (do not continue `run_next`); surface error on the result the same way other post-success failures do in this function.
   - When `debug=True`: Style D `debug_index` / `debug_detail` for this hop — found (task_key, artifact key or search-terms path) and recorded (truncated payload via `truncate_debug_content` when long). No new debug lines when `debug=False`.
2. Do **not** set `dispatch_chain_graduate_on_terminal` for this candidate path (job graduation map stays job-only). Do **not** write job hop labels for candidates (`_should_write_dispatch_hop_label` stays `entity_type == "job"`).
3. In `src/core/candidate.py`, rewrite `run_requested_artifacts_dispatch`:
   - Load candidate; resolve stage from `CANDIDATE_STAGE_DISPATCH["requested_artifacts"]`.
   - Build `task_ctx` from candidate dict plus `"persist_candidate_craft_hops": True` and ensure candidate id is visible to hop ledgers (`astral_candidate_id` / index = candidate_id — match whatever existing craft/`do_task` already expects for this module).
   - **Do not** set `suppress_run_next`.
   - `await do_task(task_key=stage["task_key"], live_content="", index=candidate_id, ctx=task_ctx, debug=debug)`.
   - On success: `transition_candidate_state(candidate_id, stage["pass_state"])`; return passed counts.
   - On failure: existing `_requested_stage_failure_target` + transition; return failed/error counts.
   - Delete the manual `while craft_key` walk that used `suppress_run_next`.
4. Delete `run_requested_resume_dispatch` and any imports/callers of it.
5. Leave `_persist_craft_dispatch_success` behavior for rubric keys + `craft_company_search_terms` (+ `craft_resume_base` if still used by UI) unchanged except as required by the hook call site.
6. Confirm `run_candidate_artifact_generation` still passes `suppress_run_next=True` so Manage UI one-shot craft does not fan the whole chain.

⚠️ **Decision:** Dispatch uses native `do_task` `run_next` (hop ledgers + `run_next hop:` lines) with an explicit persist flag — not the AST-1113 manual walk — so execution history matches `BUILD_ARTIFACTS` feel. UI generate keeps suppress. Graduation stays in the candidate worker (not `DISPATCH_CHAIN_TERMINAL_GRADUATION`) so job chain map stays uncontaminated.

⚠️ **Decision (mid-chain failure / partial artifacts):** The live chain is eight hops. If hop N fails after hops 1..N−1 already persisted, those earlier writes **remain** on the candidate; the worker still transitions to retry/error (AC5 — not silently stuck). A later successful run re-enters at `craft_get_rubric` and overwrites via the same persist helper. Partial artifacts after a failed run are **expected and self-healing**, not corruption. Betty/UAT should treat leftover mid-chain content after retry/error as normal until a full success lands `ARTIFACTS_READY`.

## Stage 3: Consult routing + wrapper-row retire + admin JSON

**Done when:** `run_consult_task` for `entity_type=candidate` routes `dispatch_task_key == craft_get_rubric` (stage `task_key`) to `run_requested_artifacts_dispatch` and no longer routes wrapper keys; dispatcher stage-key sets / AUTO-off debug use the new key; a retire-only path deletes live `dispatch_task` rows whose `task_key` is a retired wrapper (no insert of `(craft_get_rubric, REQUESTED_ARTIFACTS)`); `data/admin/agent_task.json` no longer carries live wrapper task rows; `rg 'candidate_requested_(resume|artifacts)' src/ data/admin/agent_task.json` shows only retire messaging / absence; `python3 -m py_compile` on touched files succeeds.

1. In `src/core/consult.py`, replace wrapper `task_key` branches with a match on `CANDIDATE_STAGE_DISPATCH["requested_artifacts"]["task_key"]` → `run_requested_artifacts_dispatch`. Remove resume-wrapper import/route.
2. In `src/core/dispatcher.py`:
   - Update `_debug_log_auto_off_stage_skips` (and any other `CANDIDATE_STAGE_DISPATCH` task_key frozensets) for the new key.
   - Add a **retire-only** helper (name e.g. `retire_candidate_requested_wrapper_dispatch_tasks`) that deletes `dispatch_task` rows whose `task_key` is in the retired wrapper set (`candidate_requested_resume` / `candidate_requested_artifacts`). Scope: template candidate + every candidate that already has ≥1 dispatch row (same breadth as a one-shot cleanup, **not** a seed catalog). Invoke once from the existing scheduler/boot peer site beside meteorite/gaze_email provision **only** as a delete pass — **do not** `save_dispatch_task` for `craft_get_rubric`.
   - **Do not** add `ensure_candidate_artifacts_dispatch_tasks` / `provision_candidate_artifacts_dispatch_tasks`. AC2 is create-time selectability only; operators / set-from-template create `(craft_get_rubric, REQUESTED_ARTIFACTS)` when wanted. No Archie Seed needs catalog on AST-1243 → no auto-provision (`astral.seed.define-approved` / `astral.seed.operator-rows-stay-deleted`).
3. In `data/admin/agent_task.json`, remove the `candidate_requested_resume` and `candidate_requested_artifacts` objects entirely (do not leave them as current rows). Do **not** reorder the live craft `run_next` chain in this ticket — trust `origin/dev` topology headed by `craft_get_rubric`.
4. Do not edit React/UI handoff (AST-1253). Do not edit `tests/` or bible.

⚠️ **Decision:** Retire wrapper rows only. Do **not** invent a startup ensure catalog for `craft_get_rubric` — that was unapproved seed scope (Joan fix-now). Replacement rows are operator-created (AC2).

## Execution contract

- Stages in order; one commit per stage on the epic worktree sub; publish to `origin/sub/AST-1243/AST-1252-artifacts-dispatch-chain` after each stage per build-child.
- No files outside the Files Changed table.
- Ambiguity or drift → stop and comment on **parent** AST-1243 with the Stage N blocked template.
- Betty owns test/bible updates after Code Complete — engineer does not patch `tests/`.

## Revisions

### Revision 1 — 2026-08-07
Driven by: Joan `[plan-discuss] round=1 concern` (plan-rubric.v1 REVISE @ `9144d909`).
Changes:
- **fix-now:** Dropped ensure/provision of `(craft_get_rubric, REQUESTED_ARTIFACTS)`; Stage 3 is retire-only delete of wrapper `dispatch_task` rows + consult/admin JSON.
- **discuss:** Stated intentional removal of REQUESTED_RESUME → `craft_resume_base` → RESUME_READY automation (brief-authorized).
- **discuss:** Documented mid-chain failure leaves partial artifacts; retry from head overwrites (expected/self-healing).
- **acceptable:** Collapsed redundant `craft_task_key`; worker reads `stage["task_key"]` only.

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — retires two live dispatch task keys, rewires candidate stage orchestration onto `craft_get_rubric`, and changes how craft hops persist/ledger during dispatch (utils + core + admin seed cleanup).

**Conf:** `high` — entry hop and `run_next` authority already exist on `origin/dev`; persist helper and stage failure targets already exist; BUILD_ARTIFACTS hop-ledger behavior is the explicit template; AST-1113 suppress remains only for UI one-shot; Joan’s load-bearing mechanism check retained.

**Risk:** `HIGH` — wrong persist placement skips mid-chain artifact writes or double-writes; intentional removal of resume-wrapper automation ends REQUESTED_RESUME → craft_resume_base dispatch until a future epic; operators must create `craft_get_rubric`@`REQUESTED_ARTIFACTS` rows themselves (no auto-seed).

## Self-review vs ASTRAL_CODE_RULES

- **§2.6.0 / `astral.dispatch.run-next-is-chain-authority`:** Succession from live `agent_task.run_next` only; no craft-hop list in config.
- **`astral.state.no-daisy-chain-in-run`:** Uses documented `run_next` carve-out inside `do_task`; worker does one transition to ready/retry/error after the chain returns.
- **§2.1 / §1.4:** States and stage entry key in config; no hardcoded hop sets.
- **§1.5.1 debug contract:** Gated `debug=True` found/recorded per hop; truncation for long payloads.
- **`astral.seed.define-approved` / operator-rows-stay-deleted:** No new provision catalog; retire-only deletes.
- **§1.3 / layers:** Persist stays in candidate; hook late-imports from agent; consult routes; dispatcher retires wrappers only.
- **Betty test-tree ban:** No `tests/` / bible edits in this plan.
- **No conflict requiring conf-!!-NONE.**

## Review

**Publish ref:** `origin/sub/AST-1243/AST-1252-artifacts-dispatch-chain`  
**Tip:** `a26c403c`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `a923e4d2` | retire wrapper TASK_CONFIG keys; craft_get_rubric stage entry |
| 2 | `f34c3b40` | native run_next + persist_candidate_craft_hops; drop resume worker |
| 3 | `a26c403c` | retire-only wrapper dispatch_task delete; drop admin agent_task seeds |

## Radia review

[code-rubric] revision=1

**Rubric:** code-rubric.v1
**Publish ref tip:** `2b127e9c`
**Overall:** FIX-NOW

**Full-set sweep:** all 65 active statutes scored in-session (18 universal + 47 scoped) against `git diff origin/dev...origin/sub/AST-1243/AST-1252-artifacts-dispatch-chain`. No violates beyond the finding below; scoped statutes outside `src/ui/**` / `src/data/**` / `debug/`-`artifacts/` predicates score `not-applicable` (no matching diff paths).

**What's solid:** Stage 1–3 match the plan closely — `CANDIDATE_STAGE_DISPATCH["requested_artifacts"]` collapses to a single `task_key`, `run_requested_artifacts_dispatch` drops the manual `craft_key` walk for one native `do_task` call with no `suppress_run_next`, the persist hook in `do_task` is gated on `persist_candidate_craft_hops` + `index` with Style D debug lines and `truncate_debug_content`, and `retire_candidate_requested_wrapper_dispatch_tasks` is a clean retire-only delete (no `save_dispatch_task` insert) called once from `start_scheduler`. `rg 'candidate_requested_(resume|artifacts)' src/` and the admin JSON only match the retired-set / retire-message locations. `python3 -m py_compile` clean on all five touched modules. Engineer/Betty test-tree boundary holds (`code(AST-1252)` commits touch only `src/` + `data/admin/`; `test(AST-1252)` commits touch only `tests/` + `docs/test-bible/`).

**Findings**

- **fix-now — B1 imports (`src/core/agent.py`, new persist-hook block):** `from src.core.candidate import _persist_craft_dispatch_success` is a lazy import with no comment explaining the cycle-break, unlike the established sibling precedent a few lines above it in the same function (`from src.core.tracker import pin_job_artifact_agent_data_id` — `# Lazy import breaks agent↔tracker cycle (consult imports agent).`). Add the equivalent one-liner for the candidate import.
- **discuss — no-hardcoded-sets (`src/core/dispatcher.py`):** `_RETIRED_CANDIDATE_REQUESTED_WRAPPER_KEYS = frozenset({"candidate_requested_resume", "candidate_requested_artifacts"})` re-declares two literals that already live in `config.DISPATCH_RETIRED_TASK_KEYS`. The in-code comment explains *why* it's a narrower subset, but not why it needs to be a second hardcoded set instead of sourced from config (e.g. a named constant in `config.py`, or filtered from the canonical set). Low risk today (values match, no functional bug), but drifts silently if the canonical set changes.
- **discuss — `orch.git.betty-merge-tests-one-sha`:** the publish ref carries two `merge-tests(AST-1252): origin/tests <sha>` commits (`2bbdaea6` → `e0b1bc89`, then `2b127e9c` → `3c004de7` after the repo-admin manifest was narrowed) — the statute's own "Violating" example is exactly two merge-tests commits after a test revision. Not a product bug; flagging for Betty's process awareness.
- **advisory — `data/admin/agent_task.json` (Stage 3 commit `a26c403c`):** beyond removing the two wrapper rows, the file was re-serialized (em-dash `—` / ellipsis `…` → `\u2014` / `\u2026`) across ~15 unrelated prompt entries, almost certainly `json.dump` without `ensure_ascii=False`. Functionally identical after JSON parse, but it's diff noise outside the plan's stated change ("remove the two objects... do not reorder"). Worth a clean re-serialize next touch, not blocking.

**Pattern conformance:** `pattern.dispatch.run-next-chain-authority`, `pattern.state.entity-state-transitions`, `pattern.batch.entity-claim-process-release` (all cited in description, all exist under `canon/patterns/`) — conforms per the sweep above.

**Plan adherence:** Diff matches the Files Changed table exactly (no extra `src/` files touched); Stage 1–3 "Done when" criteria verified directly (rg scope, compile, assert, retire-only semantics). Self-Assessment `Scope: MAJOR-CHANGE` / `Conf: high` matches the diff's real footprint; no `!!-NONE` conflict. No Joan plan-rubric verdict attachment on the Linear issue — noting per C4 (`no plan-rubric verdict attached`); the plan's own "Considered but excluded" list matches this sweep's `not-applicable` / `conforms` scores with no straggler drift.

**Cross-ticket boundary:** `tests/component/extension/**` / `docs/test-bible/extension/**` (AST-1254, parent AST-1170) appear in this three-dot diff only via the single pinned `origin/tests` SHA merges (Betty's shared test-corpus branch) — conforming per `orch.git.betty-merge-tests-one-sha`'s single-SHA mechanism, not scope creep by this ticket.

## Frame diff

(none — no ticket description changes needed; AC/scope table already accurate)

context_tokens≈38000

— Radia

## Resolution

**Date:** 2026-08-07  
**Publish tip before resolve:** `28686529` (`docs(AST-1252): Radia review — findings`)

| Finding | Disposition |
|---------|-------------|
| fix-now (B1: lazy candidate import missing cycle-break comment) | Fixed — added `# Lazy import breaks agent↔candidate cycle (candidate imports agent).` beside `_persist_craft_dispatch_success` import in `do_task`. |
| discuss (duplicated retired-key frozenset in dispatcher) | Fixed — `_RETIRED_CANDIDATE_REQUESTED_WRAPPER_KEYS` now filters `DISPATCH_RETIRED_TASK_KEYS` by `candidate_requested_` prefix (no second literal set). |
| discuss (two `merge-tests` commits on publish ref) | Accepted — Betty process / qa-handoff return path; not a product change. |
| advisory (agent_task.json unicode re-serialize noise) | Accepted — no re-touch; clean re-serialize on next intentional edit. |

## Bug: AST-1388 — REQUESTED_ARTIFACTS daisy-chain hop state labels

### As-is
When a candidate is in `REQUESTED_ARTIFACTS` and dispatch runs the craft daisy chain from `craft_get_rubric` onward (`persist_candidate_craft_hops`), each successful hop persists artifact fields and opens hop ledgers, but **does not** write a compound progress label on `candidate.state`. Jobs on `BUILD_ARTIFACTS` do write `{trigger}.{completed_task_key}` via `_write_dispatch_hop_label_on_success`. Mid-chain position is invisible on the entity state.

### To-be
After each successful craft hop on the `REQUESTED_ARTIFACTS` dispatch path, `candidate.state` is `REQUESTED_ARTIFACTS.<last_completed_task_key>` (same `dispatch_hop_label` shape as jobs). Terminal success still graduates to `ARTIFACTS_READY`. Mid-chain failure leaves the last successful compound label visible so UI/redispatch can see progress without reading execution history alone. Job `BUILD_ARTIFACTS` hop-label behavior is unchanged.

### Repro
1. Candidate in bare `REQUESTED_ARTIFACTS`; live `agent_task` chain `craft_get_rubric` → … with non-empty `run_next` links.
2. Run `run_requested_artifacts_dispatch(candidate_id)` (or consult route for `craft_get_rubric` @ `REQUESTED_ARTIFACTS`) with the first hop mocked to succeed and a later hop set to fail (or pause after hop 1).
3. **Broken:** after hop 1 success, `candidate.state` is still `REQUESTED_ARTIFACTS` (or jumps only at terminal `ARTIFACTS_READY` / retry / error). No `REQUESTED_ARTIFACTS.craft_get_rubric` (etc.) row state.
4. **Fixed:** after each success, state is `REQUESTED_ARTIFACTS.<that_task_key>`; after a mid-chain failure, state remains the last successful compound label (not wiped to bare trigger before retry/error handling decides).

### Root cause
AST-1252 Stage 2 **Decision** intentionally left `_should_write_dispatch_hop_label` as `entity_type == "job"` (and gated on `DISPATCH_CHAIN_TERMINAL_GRADUATION`, which only maps `BUILD_ARTIFACTS`). `run_requested_artifacts_dispatch` also never sets `ctx["dispatch_trigger_state"]`, so even a widened gate would see an empty trigger. Candidate hop labels therefore never write. Separately, `_should_write_dispatch_hop_label` is shared with `_apply_dispatch_chain_hop_failure` (job error_state / claim release) — flipping that gate for candidates would incorrectly enter the job failure path. Terminal `transition_candidate_state(..., ARTIFACTS_READY)` and UI in-flight hide only know bare `REQUESTED_ARTIFACTS` / `_RETRY`, so compound labels need prior-state + hide parity.

### Proposed change
Concrete enough for `make-fix` — do **not** add `REQUESTED_ARTIFACTS` to `DISPATCH_CHAIN_TERMINAL_GRADUATION` (graduation stays in the candidate worker; job map stays uncontaminated).

1. **`src/core/candidate.py` — `run_requested_artifacts_dispatch`**
   - On `task_ctx`, set `"dispatch_trigger_state": stage["trigger_state"]` (`REQUESTED_ARTIFACTS`).
   - Do **not** set `dispatch_chain_graduate_on_terminal` (unchanged AST-1252 Decision).
   - Keep `persist_candidate_craft_hops: True` and native `run_next` (no `suppress_run_next`).

2. **`src/core/candidate.py` — `write_candidate_dispatch_hop_label(candidate_id, trigger_state, completed_task_key) -> str`**
   - Mirror `tracker.write_job_dispatch_hop_label`: build label via `dispatch_hop_label`, append `state_history`, `database.save_candidate(..., state=label, ...)`.
   - Bypass `transition_candidate_state` / `CANDIDATE_STATES` membership (runtime labels are not registry keys — same carve-out as jobs in code-rules §2.6.0).

3. **`src/core/agent.py` — success write path (parallel to job gate, do not widen the shared gate)**
   - Keep `_should_write_dispatch_hop_label` **job-only** so `_apply_dispatch_chain_hop_failure` stays job-shaped.
   - Add a candidate-craft success gate, e.g. `_should_write_candidate_craft_hop_label`: `entity_type == "candidate"` and `index` and `(ctx or {}).get("persist_candidate_craft_hops")` and `trigger_state == CANDIDATE_STAGE_DISPATCH["requested_artifacts"]["trigger_state"]`.
   - In `_write_dispatch_hop_label_on_success`: after the existing job branch (or beside it), when the candidate-craft gate is true, call `write_candidate_dispatch_hop_label` (lazy-import `candidate` with the usual cycle-break comment). Reuse the same `_dispatch_chain_hop_index` / debug Style D “hop ok” lines already used for jobs when `debug=True`.
   - UI one-shot craft (`suppress_run_next` / no `persist_candidate_craft_hops`) must **not** write hop labels.

4. **`src/core/candidate.py` — `_candidate_state_allowed`**
   - Mirror `tracker._job_state_matches_prior`: if `from_state` parses as a dispatch hop label and `parsed[0]` is in the target’s `prior_states`, allow (so `ARTIFACTS_READY` / retry / error can legally follow `REQUESTED_ARTIFACTS.<hop>`).

5. **Failure vs last label (supersedes AST-1252 Stage 2 “always transition to retry/error” only when a compound label is already present)**
   - ⚠️ **Decision:** After a failed `do_task` chain, if the candidate’s current state is already a `parse_dispatch_hop_label` whose trigger equals the stage trigger, **leave that compound label** (do not call `transition_candidate_state` to `REQUESTED_ARTIFACTS_RETRY` / `REQUESTED_ARTIFACTS_ERROR`). First-hop failure while still on bare `REQUESTED_ARTIFACTS` (or `_RETRY`) still uses `_requested_stage_failure_target` as today.
   - Partial artifact field writes remain in place (AST-1252 Decision unchanged).

6. **Claim + UI in-flight (so hop-labeled candidates are not stuck and Generate stays hidden)**
   - Candidate batch claim today requires every `states=` entry ∈ `CANDIDATE_STATES` (`get_new_candidate_batch`). Add a claim carve-out parallel to `is_valid_job_batch_claim_state`: accept `REQUESTED_ARTIFACTS.<task_key>` when `parse_dispatch_hop_label` succeeds and trigger is the artifacts stage trigger (do **not** require graduation-map membership).
   - For dispatcher claim of `craft_get_rubric` @ `REQUESTED_ARTIFACTS`, expand claim states to bare trigger + retry + parent hop labels for the entry task (same idea as `dispatch_chain_claim_states_for_row`, but candidate-scoped — either a small helper next to the job one or an inline expansion used only for this stage). Redispatch re-enters at `craft_get_rubric` (full chain restart; persist overwrites — self-healing). Mid-hop resume (starting `do_task` at a mid key) is **out of scope**.
   - AST-1253 `inflight_hide_states` / any UI that keys on exact `REQUESTED_ARTIFACTS` / `_RETRY`: treat hop labels under trigger `REQUESTED_ARTIFACTS` as in-flight (hide Generate/Regenerate) — config or API resolution, not a hardcoded frontend set.

7. **Compile**
   - `python3 -m py_compile` on touched modules (`agent.py`, `candidate.py`, and any config/dispatcher helpers touched for claim/hide).

### Blast radius
- Shared `_should_write_dispatch_hop_label` / `_apply_dispatch_chain_hop_failure` (must stay job-only).
- `transition_candidate_state` / `_candidate_state_allowed` callers (any transition from a hop-labeled candidate).
- Candidate pool claim (`get_new_candidate_batch`, dispatcher candidate branch) and AST-1253 Generate hide.
- Job `BUILD_ARTIFACTS` path, `DISPATCH_CHAIN_TERMINAL_GRADUATION`, and AST-1264 CALLER succession must not change behavior.
- Tests that assert `_should_write_dispatch_hop_label` is job/graduation-map only remain valid; Betty may add candidate hop-label coverage via qa-fix — engineer does not patch `tests/`.

### What must still hold
- AST-1252: native `do_task` `run_next` + `persist_candidate_craft_hops`; per-hop artifact persist; terminal success → `ARTIFACTS_READY`; UI generate keeps `suppress_run_next=True`; no `REQUESTED_ARTIFACTS` entry in `DISPATCH_CHAIN_TERMINAL_GRADUATION`; no hop-order list in config.
- AST-1253: Generate/Regenerate hidden while artifacts chain is in flight (including compound hop labels).
- Job `BUILD_ARTIFACTS` hop labels + terminal graduation unchanged.
- Runtime hop labels are not `CANDIDATE_STATES` registry keys (write bypasses registry membership; registered transitions accept them via prior-state hop parse).

## Bug: AST-1416 — Restore REQUESTED_ARTIFACTS hop-label membership carve-out

AST-1388 shipped hop-label **writes**. This bug is membership **rejection** of the label that write produces. Do not reopen AST-1388 write-path scope (`write_candidate_dispatch_hop_label`, `_should_write_candidate_craft_hop_label`, `dispatch_trigger_state` on `run_requested_artifacts_dispatch`).

### As-is
`run_requested_artifacts_dispatch` for candidate `somerset` fails after the first successful craft hop with `Invalid candidate state 'REQUESTED_ARTIFACTS.craft_get_rubric'. Must be one of: [bare CANDIDATE_STATES keys]`. The compound hop label is treated as an illegal persistable state; the worker logs the error and the daisy chain stops.

### To-be
Compound hop labels `REQUESTED_ARTIFACTS.<completed_task_key>` are accepted as runtime candidate states on the artifacts dispatch persist path (same shape as job `BUILD_ARTIFACTS` hop labels, not `CANDIDATE_STATES` keys). `save_candidate` writes succeed; later hops and terminal `ARTIFACTS_READY` / retry / error can follow.

### Repro
1. Candidate (e.g. `somerset`) in bare `REQUESTED_ARTIFACTS`; live `agent_task` chain starting at `craft_get_rubric` with non-empty `run_next`.
2. Run `run_requested_artifacts_dispatch(candidate_id)` so hop 1 (`craft_get_rubric`) succeeds.
3. **Broken:** `write_candidate_dispatch_hop_label` calls `database.save_candidate(..., state="REQUESTED_ARTIFACTS.craft_get_rubric")` and `save_candidate` raises `ValueError: Invalid candidate state 'REQUESTED_ARTIFACTS.craft_get_rubric'. Must be one of: ['NEW_CANDIDATE', …, 'REQUESTED_ARTIFACTS', …]`. Chain stops; `candidate.state` is not the hop label.
4. **Fixed:** that save returns; `candidate.state` is `REQUESTED_ARTIFACTS.craft_get_rubric`; a following hop write or `transition_candidate_state(..., "ARTIFACTS_READY")` can proceed.

### Root cause
AST-1388 item 2 wrote labels via `write_candidate_dispatch_hop_label` → `database.save_candidate(..., state=label)` specifically to bypass `transition_candidate_state` / `CANDIDATE_STATES` membership. `save_candidate` itself still requires `state in CANDIDATE_STATES.keys()` on both INSERT and UPDATE (`src/data/database.py`, the two `Invalid candidate state '{state}'. Must be one of: {allowed}` raises). That check is the exact exception. `_candidate_state_allowed` hop-parse (AST-1388 item 4) is not on this path — it only governs registered *to_state* transitions. Job `save_job` has no registry membership check, which is why `BUILD_ARTIFACTS` hop labels already persist. Claim already accepts the labels via `is_valid_candidate_batch_claim_state`; persist does not call that helper.

### Proposed change
Do **not** add hop labels to `CANDIDATE_STATES`. Do **not** change `write_candidate_dispatch_hop_label`, the candidate-craft success gate, or `run_requested_artifacts_dispatch`.

1. **`src/data/database.py` — `save_candidate`**
   - Import `is_valid_candidate_batch_claim_state` from `src.utils.config` (same module already imported for `CANDIDATE_STATES`).
   - Replace **both** INSERT and UPDATE membership checks (`if state not in list(CANDIDATE_STATES.keys())`) with `if not is_valid_candidate_batch_claim_state(state)`. That helper is already true for registry keys **and** for `parse_dispatch_hop_label` whose trigger is `CANDIDATE_STAGE_DISPATCH["requested_artifacts"]["trigger_state"]` (`REQUESTED_ARTIFACTS`) and whose hop is a `TASK_CONFIG` key (so `REQUESTED_ARTIFACTS.craft_get_rubric` and later craft hops pass; `NEW` / garbage still fail).
   - Keep the existing error string for rejects: `Invalid candidate state '{state}'. Must be one of: {allowed}` with `allowed = list(CANDIDATE_STATES.keys())`. Hop labels are the carve-out, not listed in `allowed`.
   - Do **not** remove the check entirely (AST-988 still needs `'NEW'` rejected). Do **not** add a second hop-membership list.

2. **`src/utils/config.py` — `is_valid_candidate_batch_claim_state` docstring only**
   - Widen “batch claim only” to persist + claim so the shared predicate is honest. No logic change.

3. **Leave alone (already holding)**
   - `_candidate_state_allowed`: `ARTIFACTS_READY` / `REQUESTED_ARTIFACTS_RETRY` / `REQUESTED_ARTIFACTS_ERROR` already accept a hop-labeled prior when `parsed[0]` is in that target’s `prior_states` (`ARTIFACTS_READY.prior_states` includes `REQUESTED_ARTIFACTS`). Terminal `transition_candidate_state(candidate_id, pass_state)` after a successful chain does not need a new carve-out.
   - `transition_candidate_state` still requires `to_state in CANDIDATE_STATES` (hop labels are never transition *targets*).
   - Job `save_job` / `write_job_dispatch_hop_label` / `DISPATCH_CHAIN_TERMINAL_GRADUATION` unchanged.

4. **Compile**
   - `python3 -m py_compile src/data/database.py src/utils/config.py`

### Blast radius
- Every `database.save_candidate(..., state=...)` caller: registry keys still persist; `'NEW'` and other non-hop unknowns still raise; only `REQUESTED_ARTIFACTS.<TASK_CONFIG key>` is newly persistable.
- Candidate claim (`get_new_candidate_batch` / `is_valid_candidate_batch_claim_state`) already used this predicate — no behavior change there.
- `remap_legacy_candidate_state` still does not know hop labels (would map them to initial state). Not on this dispatch path; do not “fix” remap as part of this ticket.
- Job `BUILD_ARTIFACTS` hop-label writes stay on `save_job` with no new membership check.
- Tests that assert `save_candidate` rejects unknown registry strings remain valid for non-hop values; Betty may add a persist-accepts-hop-label repro via qa-fix — engineer does not patch `tests/`.

### What must still hold
- AST-1388: runtime hop labels are **not** `CANDIDATE_STATES` registry keys (write bypasses registry membership; registered transitions accept them via prior-state hop parse). Claim + inflight hide still treat hop labels as in-flight.
- AST-1252: native `do_task` `run_next` + `persist_candidate_craft_hops`; terminal success → `ARTIFACTS_READY`; no `REQUESTED_ARTIFACTS` entry in `DISPATCH_CHAIN_TERMINAL_GRADUATION`.
- Job `BUILD_ARTIFACTS` hop labels + terminal graduation unchanged.
- Invalid non-hop states (`NEW`, typos) still rejected by `save_candidate` with the existing `Must be one of:` message.


## Radia review (AST-1416)

[code-rubric] revision=2

**Rubric:** code-rubric.v2  
**Ticket:** AST-1416  
**Publish ref:** `origin/sub/AST-1415/AST-1416-restore-hop-label-membership` @ `1b16124c`  
**Diff base:** `origin/ftr/AST-1415-candidate-state-validation-bug` @ `bb5738af`  
**Overall:** CLEAN

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | layers miss — no `core` diff paths |
| astral.agent.do-task-delegation | scoped | not-applicable | layers miss — no `core` diff paths |
| astral.agent.grade-vector-validation | scoped | not-applicable | layers miss — no `core` diff paths |
| astral.batch.batch-id-first | scoped | conforms | No batch-id claim/lock logic touched |
| astral.batch.batch-id-format | scoped | conforms | No batch-id formatting changes |
| astral.batch.claim-process-release | scoped | conforms | Persist predicate aligned with existing claim helper; no unlocked dispatch path introduced |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | No agent-response storage changes |
| astral.config.config-source-of-truth | scoped | conforms | Reuses `is_valid_candidate_batch_claim_state` from config; no scattered literals |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No secrets/env lookups added |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss — no debug/artifact paths |
| astral.debug.spikes-under-debug-dir | scoped | conforms | No spike/debug-dir additions |
| astral.dispatch.run-next-is-chain-authority | scoped | conforms | No hop-order list or shadow `run_next` frozenset added |
| astral.dispatch.seed-auto-false | scoped | conforms | No dispatch seed/provision changes |
| astral.docs.features-single-file-per-ticket | scoped | conforms | plan-fix patch appended to existing parent feature doc |
| astral.git.betty-no-src-or-features | scoped | conforms | No Betty-owned tree edits |
| astral.git.engineer-test-tree-ban | scoped | not-applicable | paths miss — no `tests/` changes |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | layers miss — no `core`/`external` diff |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | layers miss — no `core` diff |
| astral.idioms.require-auth-on-protected-endpoints | scoped | not-applicable | layers miss — no API surface diff |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | layers miss — no `core`/`external` diff |
| astral.layers.import-direction | scoped | conforms | `database.py` imports config helper; no reverse/circular layer breach |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers miss — no `scripts` diff |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | No UI business-logic drift |
| astral.seed.agent-tables-in-repo-json | scoped | conforms | No agent_task JSON seed edits |
| astral.seed.archie-catalog-wins | scoped | conforms | No seed catalog invention |
| astral.seed.boot-only-not-hot-path | scoped | conforms | No boot/hot-path seed wiring |
| astral.seed.define-approved | scoped | conforms | No unapproved auto-provision |
| astral.seed.operator-rows-stay-deleted | scoped | conforms | No operator-row resurrection |
| astral.seed.other-via-coverage-join | scoped | conforms | No coverage-join seed changes |
| astral.standards.data-raises-caller-logs | scoped | conforms | `save_candidate` still raises `ValueError`; no data-layer logging |
| astral.standards.database-header-inventory | scoped | conforms | No new tables/queries; header inventory unchanged appropriately |
| astral.standards.debug-contract-gated | scoped | conforms | No debug output changes |
| astral.standards.dry-and-focused-functions | scoped | conforms | Single shared predicate instead of duplicating hop-parse logic |
| astral.standards.in-scope-only | scoped | conforms | Touches only `database.py`, `config.py` docstring, and plan doc per patch |
| astral.standards.logging-via-utils | scoped | conforms | No ad-hoc logging |
| astral.standards.names-not-ticket-ids | scoped | conforms | No ticket-id symbol names in product code |
| astral.standards.no-cross-contamination | scoped | conforms | Candidate persist fix does not bleed job dispatch paths |
| astral.standards.no-hardcoded-sets | scoped | conforms | Membership delegated to config helper, not inline hop frozenset |
| astral.standards.public-then-helpers | scoped | conforms | No API surface reordering issues |
| astral.standards.utils-data-late-import-only | scoped | conforms | Existing top-level config import pattern preserved |
| astral.state.core-decides-transitions | scoped | conforms | `save_candidate` validates membership only; does not choose next state |
| astral.state.job-prior-states-enforced | scoped | conforms | Job transition enforcement untouched |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | layers miss — no `core` diff |
| astral.ui.frontend-file-placement | scoped | not-applicable | layers miss — no `ui` diff |
| astral.ui.naming-conventions | scoped | not-applicable | layers miss — no `ui` diff |
| astral.ui.single-gunicorn-worker | scoped | conforms | `config.py` touch is docstring-only; worker count unchanged |
| orch.git.betty-merge-tests-one-sha | universal | conforms | No test-tree merge on this sub |
| orch.git.commit-vocabulary | universal | conforms | `code(AST-1416): …` commit on publish tip |
| orch.git.flow-direction-inviolable | universal | conforms | Fix sub stacked on live `ftr` |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1415/AST-1416-…` on `ftr/AST-1415-…` |
| orch.git.merge-on-checkout | universal | conforms | No checkout/merge violations in diff |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No history rewrite |
| orch.git.no-dev-agent-branches | universal | conforms | Publish ref is `sub/*`, not `dev-*` |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Review run from `astral-AST-1415/` |
| orch.git.three-permanent-branches | universal | conforms | No new long-lived branch classes |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Scoped membership carve-out already plan-approved |
| orch.pipeline.plan-is-bible | universal | conforms | Diff matches plan-fix `## Proposed change` exactly |
| orch.pipeline.project-scoped-queues | universal | conforms | Single-ticket fix review |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Spawned at Tests Passed per fix-lane F7 |
| orch.roles.archie-approves-statutes | universal | conforms | No statute amendments |
| orch.roles.betty-owns-test-tree | universal | conforms | Engineer did not patch `tests/` |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee Ada; Radia read-only |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada assignee through review gate |
| orch.roles.pre-commit-path-bans | universal | conforms | No banned-path commits in reviewed product diff |

**Active statute count:** 64 — **rows above:** 64

## Pattern conformance

none cited in AST-1416 plan-fix patch

## Plan adherence

Diff implements the approved AST-1416 patch precisely: both INSERT and UPDATE `save_candidate` membership gates now call `is_valid_candidate_batch_claim_state(state)`; error text for rejects unchanged; `write_candidate_dispatch_hop_label`, dispatch worker, and `CANDIDATE_STATES` registry untouched; `config.py` docstring widened to “persist + claim” with no logic change. Scope stays inside blast radius (shared predicate, no remap fix, no job path edits, no test-tree edits per board routing).

**C6 judgment aids (touched areas):** import direction data→utils OK; no silent swallow; no new fallbacks/logging; no UI/debug/external surface changes.

## Fix-specific checks

**[bug-repro]:** not applicable — board `[board-betty] TESTS: REVISE` routed repro to sibling **AST-1417**; no `[bug-repro]` expected on this ticket.

**## What must still hold:** OK
- **AST-1388:** Hop labels remain outside `CANDIDATE_STATES`; persist carve-out via existing parse helper; transition/claim paths unchanged in diff.
- **AST-1252:** No changes to `run_next` dispatch, `persist_candidate_craft_hops`, terminal graduation, or `DISPATCH_CHAIN_TERMINAL_GRADUATION`.
- **Job `BUILD_ARTIFACTS`:** `save_job` / job hop writes untouched.
- **Invalid non-hop states:** `NEW`, garbage, and non-`TASK_CONFIG` hops still fail `is_valid_candidate_batch_claim_state`.

## Findings

**fix-now:** none  
**discuss:** none  
**advisory:** none

## What's solid

Minimal, plan-faithful fix: one predicate reused for claim parity on persist, matching the root-cause analysis (AST-1388 write path vs `save_candidate` registry gate). Surgical three-file diff with honest docstring update.

## Frame diff

```
origin/ftr/AST-1415-candidate-state-validation-bug...origin/sub/AST-1415/AST-1416-restore-hop-label-membership
 docs/features/candidate/ast-1252-artifacts-dispatch-chain-persistence-and-retire-wrappers.md | +52
 src/data/database.py                                                                       |  9 +-
 src/utils/config.py                                                                        |  2 +-
 3 files changed, 58 insertions(+), 5 deletions(-)
```

## Notes

- **C4:** no plan-rubric verdict attached for this bug patch — straggler sweep N/A.
- **Board:** `[board-joan] CANON: OK`; `[board-betty] TESTS: REVISE` → AST-1417 (not scored against this ticket).
- **Parent shape:** normal (AST-1415 in flight; `ftr` base present).

## Chuckles branching

| Gate | Parent | Next action |
|------|--------|-------------|
| **PROCEED** | Normal | → **Review Posted** → `do-all-the-things` §3h clean-review shortcut → **User Testing** directly (`resolve-child` skipped) |

context_tokens≈28000

---

```
[code-rubric] PROCEED (Commit: 1b16124c) hop-label persist carve-out
```


## Radia review (AST-1417)

[code-rubric] revision=2

**Rubric:** code-rubric.v2  
**Ticket:** AST-1417  
**Publish ref:** `origin/sub/AST-1415/AST-1417-save-candidate-hop-label-coverage` @ `655fc40f`  
**Diff base:** `origin/ftr/AST-1415-candidate-state-validation-bug` @ `a4353e78` (includes AST-1416 product fix)  
**Overall:** DISCUSS

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | layers miss — no `core`/`utils` product paths |
| astral.agent.do-task-delegation | scoped | not-applicable | layers miss — no `core` diff |
| astral.agent.grade-vector-validation | scoped | not-applicable | layers miss — no `core` diff |
| astral.batch.batch-id-first | scoped | not-applicable | layers miss — no `core`/`data` product paths |
| astral.batch.batch-id-format | scoped | not-applicable | layers miss — no `core`/`data` product paths |
| astral.batch.claim-process-release | scoped | not-applicable | layers miss — no `core`/`data` product paths |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | layers miss — no `core`/`data` product paths |
| astral.config.config-source-of-truth | scoped | not-applicable | layers miss — no `src/**` product diff |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | layers miss — no `src/**` product diff |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss — no debug artifact paths |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | paths miss — no `debug/` paths |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | layers miss — no `core`/`utils` product diff |
| astral.dispatch.seed-auto-false | scoped | not-applicable | layers miss — no `core`/`utils` product diff |
| astral.docs.features-single-file-per-ticket | scoped | not-applicable | paths miss — no `docs/features/**` diff |
| astral.git.betty-no-src-or-features | scoped | conforms | Test/bible-only diff; no `src/` or feature-doc edits |
| astral.git.engineer-test-tree-ban | scoped | conforms | Test-gap child — test-tree edits are ticket scope (Betty gap / test-fix lane) |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | layers miss — no `core`/`external` product diff |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | layers miss — no `core` product diff |
| astral.idioms.require-auth-on-protected-endpoints | scoped | not-applicable | layers miss — no API product diff |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | layers miss — no `core`/`external` product diff |
| astral.layers.import-direction | scoped | not-applicable | layers miss — no `src/**` product diff |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers miss — no `scripts` diff |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | layers miss — no `ui` product diff |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | layers miss — no seed JSON diff |
| astral.seed.archie-catalog-wins | scoped | not-applicable | layers miss — no seed paths |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | layers miss — no boot/seed product diff |
| astral.seed.define-approved | scoped | not-applicable | paths miss — no `data/admin/**` diff |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | layers miss — no seed paths |
| astral.seed.other-via-coverage-join | scoped | not-applicable | layers miss — no seed paths |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | layers miss — no `data`/`core` product diff |
| astral.standards.database-header-inventory | scoped | not-applicable | layers miss — no `data` product diff |
| astral.standards.debug-contract-gated | scoped | not-applicable | layers miss — no product debug paths |
| astral.standards.dry-and-focused-functions | scoped | not-applicable | layers miss — no product diff |
| astral.standards.in-scope-only | scoped | not-applicable | layers miss — scoped predicate targets `src/**` product paths |
| astral.standards.logging-via-utils | scoped | not-applicable | layers miss — no product diff |
| astral.standards.names-not-ticket-ids | scoped | not-applicable | layers miss — no product diff |
| astral.standards.no-cross-contamination | scoped | not-applicable | layers miss — no product diff |
| astral.standards.no-hardcoded-sets | scoped | not-applicable | layers miss — no product diff |
| astral.standards.public-then-helpers | scoped | not-applicable | layers miss — no product diff |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | layers miss — no product diff |
| astral.state.core-decides-transitions | scoped | not-applicable | layers miss — no `core`/`data` product diff |
| astral.state.job-prior-states-enforced | scoped | not-applicable | layers miss — no `core`/`data` product diff |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | layers miss — no `core` diff |
| astral.ui.frontend-file-placement | scoped | not-applicable | layers miss — no `src/ui` product diff |
| astral.ui.naming-conventions | scoped | not-applicable | layers miss — no `src/ui` product diff |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | layers miss — no `utils`/`ui` product diff |
| orch.git.betty-merge-tests-one-sha | universal | conforms | Exactly one `merge-tests(AST-1417): origin/tests c705c0c5` on publish ref |
| orch.git.commit-vocabulary | universal | conforms | `test(AST-1417): bug-repro — …` on owned commit |
| orch.git.flow-direction-inviolable | universal | conforms | Gap sub stacked on live `ftr` (AST-1416 already merged) |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1415/AST-1417-…` on `ftr/AST-1415-…` |
| orch.git.merge-on-checkout | universal | conforms | No checkout/merge violations |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No history rewrite |
| orch.git.no-dev-agent-branches | universal | conforms | Publish ref is `sub/*` |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Review from `astral-AST-1415/` |
| orch.git.three-permanent-branches | universal | conforms | No new long-lived branch classes |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | No product-decision drift |
| orch.pipeline.plan-is-bible | universal | conforms | AST-1417 bible § + `[bug-repro]` match board REVISE intent (see discuss on stacked siblings) |
| orch.pipeline.project-scoped-queues | universal | conforms | Single-ticket fix-lane review |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Spawned at Tests Passed (F7) |
| orch.roles.archie-approves-statutes | universal | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Test/bible ownership respected |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee Ada; Radia read-only |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada assignee through review gate |
| orch.roles.pre-commit-path-bans | universal | conforms | No banned-path product commits |

**Active statute count:** 64 — **rows above:** 64

## Pattern conformance

none cited in AST-1417 test-bible §

## Plan adherence

**AST-1417-owned work** (`c705c0c5`, 2 files / 43 LOC) matches `docs/test-bible/data/database/candidates.md` § AST-1417: adds `TestAst1417SaveCandidateHopLabelPersist::test_update_persists_requested_artifacts_hop_label` with bible manifest + narrowed run command; no product `src/` delta. Sibling AST-1416 fix is already on `ftr`, so repro-first contract is satisfiable on this tip.

**Scope note (discuss):** the three-dot publish-ref diff also carries stacked test+bible deltas for **AST-1408, AST-1409, AST-1411, AST-1412** (~920 LOC / 16 extra files) committed on this sub before `test(AST-1417)`. One `merge-tests` SHA is present and correct; stacked sibling ticket commits on the same publish ref are outside the AST-1417 bible § — acknowledge on UT, not a product rework.

## Fix-specific checks

**[bug-repro]:** OK  
- Test: `tests/component/data/database/test_candidates.py::TestAst1417SaveCandidateHopLabelPersist::test_update_persists_requested_artifacts_hop_label`  
- Pins concrete post-fix behavior: `row["state"] == dispatch_hop_label(REQUESTED_ARTIFACTS, "craft_get_rubric")` after `save_candidate` UPDATE.  
- Uses config helpers (not tautology / not mocking the write path).  
- Would fail pre-AST-1416: second `save_candidate(..., state=hop)` raises `ValueError: Invalid candidate state 'REQUESTED_ARTIFACTS.craft_get_rubric'`.  
- Tagged in class docstring + bible row (consistent with AST-1274 / AST-1389 precedent).

**## What must still hold:** OK  
- `TestSaveCandidate::test_rejects_invalid_state` preserved (bible: “none obsolete”).  
- No hop labels added to `CANDIDATE_STATES`; test builds label via `dispatch_hop_label`.  
- No product-code changes on this ref.  
- Does not weaken AST-1416 carve-out semantics (persist-only data-layer check).

## Findings

**fix-now:** none

**discuss:**
- **Stacked sibling test tickets on publish ref** — `git log ftr..sub` shows `test(AST-1408)`, `test(AST-1409)`, `test(AST-1411)`, `test(AST-1412)` ahead of `test(AST-1417)`; three-dot diff is 18 files though AST-1417 bible § owns only `test_candidates.py` + `candidates.md`. Likely Betty mechanical stacking + single `merge-tests`; Chuckles should acknowledge in issue doc / UT handoff so reviewers do not attribute unrelated frontend/admin coverage to AST-1417.

**advisory:**
- `[bug-repro]` exercises UPDATE persist only (seed bare `REQUESTED_ARTIFACTS`, then hop UPDATE) — matches AST-1416 repro shape; INSERT-with-hop-label path untested (acceptable gap).

## What's solid

Focused, config-driven `[bug-repro]` at the right layer (`save_candidate` data contract) with honest bible manifest and repro-first pass criterion documented. Product sibling AST-1416 already on `ftr`; test pins the exact membership gate Betty flagged at board REVISE.

## Frame diff

```
origin/ftr/AST-1415-candidate-state-validation-bug...origin/sub/AST-1415/AST-1417-save-candidate-hop-label-coverage
 docs/test-bible/** (8 files)                                    | +~250
 tests/component/** (10 files)                                   | +~710
 18 files changed, 963 insertions(+), 21 deletions(-)

AST-1417-owned commit c705c0c5 only:
 docs/test-bible/data/database/candidates.md                    | +27
 tests/component/data/database/test_candidates.py                | +16
```

## Notes

- **C4:** no plan-rubric verdict attached for this gap ticket.
- **Parent shape:** normal (AST-1415 in flight; `ftr` includes AST-1416 @ `1b16124c`).
- **Relations:** sibling AST-1416 product fix merged to `ftr`; this ticket owns `[bug-repro]`.

## Chuckles branching

| Gate | Parent | Next action |
|------|--------|-------------|
| **REVIEW** (discuss only, C7 complete) | Normal | → **Review Posted** → `resolve-child` (if Chuckles wants discuss acknowledged in doc) → **User Testing**; or proceed directly if discuss is informational only |

context_tokens≈32000

---

```
[code-rubric] REVIEW (Commit: 655fc40f) hop-label bug-repro OK
```

## Threads (generated — epic_registry mirror)

_(generated from epic registry — do not hand-edit; edits are overwritten)_

### Team

| Agent | Role | Thread |
|--------|-------|--------|
| Ada | engineer | `/home/susan/.cursor/chats/239c81d3f0245237d5dcb232b9ab33e6/24328bcb-53dc-4db6-b09b-4f01e79d89ff/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/b81a5e9f-9f47-42cf-9f48-02e96b72a80b/store.db` |
| Radia | review | `/home/susan/.cursor/chats/239c81d3f0245237d5dcb232b9ab33e6/6683524c-8455-4de1-af0c-b9722bed2a72/store.db` |

### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-1387 (parent) | ftr/AST-1387-artifacts-requested-daisy-chain-state |
| AST-1388 | sub/AST-1387/AST-1388-requested-artifacts-hop-labels |
| AST-1389 | sub/AST-1387/AST-1389-requested-artifacts-hop-label-tests |

**Epic worktree:** `astral-AST-1387/` — one active sub checked out at a time.
