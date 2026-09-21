<!-- linear-archive: AST-1252 archived 2026-08-17 -->

## Linear archive (AST-1252)

**Archived:** 2026-08-17  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1252/artifacts-dispatch-chain-persistence-and-retire-wrappers-candidate  
**Status at archive:** Archive  
**Project:** Astral Candidate  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1243 — Candidate Artifacts now daisy chain  
**Blocked by / blocks / related:** parent: AST-1243; blocks: AST-1253

### Description

## What this implements

Wire `REQUESTED_ARTIFACTS` to open at `craft_get_rubric`, follow live `agent_task.run_next` (no hop-order list in `config.py`), persist each hop into candidate artifact fields with `BUILD_ARTIFACTS`-style persistence, surface hop progress in execution history like `BUILD_ARTIFACTS`, graduate/fail via configured states, and remove all live `candidate_requested_artifacts` / `candidate_requested_resume` task-key wiring (seeds/config/workers/provisioning). Keep `REQUESTED_RESUME` and `REQUESTED_ARTIFACTS` selectable for `craft_get_rubric` without new trigger-state validation. Resume daisy-chain generation stays out of scope.

## In scope

- [X] `pattern.dispatch.run-next-chain-authority` — live `agent_task.run_next` is succession authority; entry hop `craft_get_rubric`
- [X] `pattern.state.entity-state-transitions` — candidate → `ARTIFACTS_READY` / retry / error via core transitions
- [X] `pattern.batch.entity-claim-process-release` — dispatch claim → process → release for the artifacts stage
- [X] `astral.dispatch.run-next-is-chain-authority` — no craft-hop sequencing list in `config.py`
- [X] `astral.state.no-daisy-chain-in-run` — `run_next` carve-out inside `do_task` only
- [X] `astral.state.core-decides-transitions` — core picks ready/retry/error targets from registries
- [X] `astral.config.config-source-of-truth` — stage entry / states in config; wrappers retired into `DISPATCH_RETIRED_TASK_KEYS`
- [X] `astral.standards.no-hardcoded-sets` — no parallel hop-order frozenset for craft succession
- [X] `astral.standards.debug-contract-gated` — per-hop found/recorded when `debug=True`
- [X] `astral.standards.in-scope-only` / `astral.standards.no-cross-contamination` / `astral.standards.dry-and-focused-functions` / `astral.standards.public-then-helpers` / `astral.standards.logging-via-utils` / `astral.standards.data-raises-caller-logs`

## Considered but excluded

- [X] `astral.ui.frontend-file-placement` / `astral.ui.naming-conventions` — Generate/Regenerate handoff is AST-1253 (sibling)
- [X] Job `BUILD_ARTIFACTS` / `DISPATCH_CHAIN_TERMINAL_GRADUATION` mutation — reference model only; candidate graduation stays in the candidate worker
- [X] Auto-provision / startup ensure of `(craft_get_rubric, REQUESTED_ARTIFACTS)` — no Seed needs on AST-1243; AC2 is selectability only; retire wrapper `dispatch_task` rows only
- [X] `astral.dispatch.seed-auto-false` — no new stage seed catalog in this ticket
- [X] Resume daisy-chain / `craft_resume_base` dispatch automation — intentional capability removal with wrapper retire (parent brief); `REQUESTED_RESUME` remains selectable for `craft_get_rubric` without new pairing validation
- [X] `tests/` / `docs/test-bible/**` — Betty after Code Complete

## Acceptance criteria

- [X] 1. No remaining product references to `candidate_requested_resume` or `candidate_requested_artifacts` as live dispatch/task keys.
- [X] 2. `REQUESTED_RESUME` and `REQUESTED_ARTIFACTS` remain selectable candidate states when creating a candidate-entity dispatch task for `craft_get_rubric` (opening hop), with no new validation that blocks either pairing.
- [X] 3. With the candidate in `REQUESTED_ARTIFACTS` and dispatch running, execution history shows the daisy chain progressing hop-by-hop comparably to `BUILD_ARTIFACTS`.
- [X] 4. On successful completion, candidate is in `ARTIFACTS_READY` (or the configured success state) and each chain rubric’s new content is visible and editable under Artifacts nav.
- [X] 5. Failure paths still land on the configured retry/error companions for the artifacts stage without silent stuck mid-chain.
- [X] 6. No craft-rubric hop sequencing list is introduced in `config.py`; succession remains `agent_task.run_next`, and per-hop persistence matches the `BUILD_ARTIFACTS` job-artifact persist posture.
- [X] 7. Backend `debug=True` on touched craft/dispatch paths emits per-hop found/recorded detail under the debug contract (index headers + `|` lines; long payloads truncated).

## Boundaries

Does **not** own Generate/Regenerate UI (sibling #2). Does **not** daisy-chain resume generation. Does **not** add hop-order lists in `config.py`.

## Notes for planning

Entry hop `craft_get_rubric`; succession via live `agent_task.run_next`. Mirror job `BUILD_ARTIFACTS` persistence + hop-visible execution history.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1243-candidate-artifacts-now-daisy-chain`, child `sub/AST-1243/AST-1252-artifacts-dispatch-chain`. Created at dispatch-parent.

### Comments

#### chuckles — 2026-08-07T07:36:09.248Z
[merge-child] blocked: git pull merge on sub — `5c98bce4` Merge remote-tracking branch 'origin/dev' into sub/...

@Ada Lovelace — rewrite `origin/sub/AST-1243/AST-1252-artifacts-dispatch-chain` so validate-sub-log passes (no `Merge remote-tracking branch`). Use `git fetch && git merge origin/ftr/AST-1243-candidate-artifacts-now-daisy-chain` (or equivalent sync-child), not pull-merge from origin/dev. Duplicate merge-tests already cleared by Betty (`c26c1c52`). Tip was `f13ef8af` after Betty hygiene.

— Chuckles

#### betty — 2026-08-07T07:35:12.734Z
[merge-child] hygiene: duplicate merge-tests(AST-1252) cleared — exactly one remains: `c26c1c52` → `origin/tests` `79c294f6` (squashed both prior test deliveries). Tip `f13ef8af` (Radia docs + resolve restored). Did not push ftr/dev.

Note: `validate-sub-log.sh` still fails on pre-existing `Merge remote-tracking branch 'origin/dev' into sub/...` (`5c98bce4`) — engineer pull-merge gate, not Betty merge-tests count.

#### chuckles — 2026-08-07T07:30:58.458Z
[merge-child] blocked: duplicate merge-tests(AST-1252) on sub — count=2 (amend on tests, one merge-tests only)

@Betty White — tests hygiene on `origin/sub/AST-1243/AST-1252-artifacts-dispatch-chain`. Deduplicate so validate-sub-log passes, then Chuckles re-runs merge-child.

— Chuckles

#### radia — 2026-08-07T07:27:59.916Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1252
**Publish ref:** `origin/sub/AST-1243/AST-1252-artifacts-dispatch-chain` @ `28686529` (docs commit) / code tip `2b127e9c`
**Overall:** FIX-NOW

Full 65-statute sweep (18 universal + 47 scoped) run in-session against `git diff origin/dev...origin/sub/AST-1243/AST-1252-artifacts-dispatch-chain`. Full checked-list is off-ticket per C1–C4; summary below.

## Plan adherence

- Diff matches the Files Changed table exactly — no `src/` files outside `config.py` / `agent.py` / `candidate.py` / `consult.py` / `dispatcher.py` / `data/admin/agent_task.json`.
- Stage 1–3 "Done when" criteria verified directly: `rg 'candidate_requested_(resume|artifacts)' src/` and the admin JSON only match retired-set/retire-message locations; `python3 -m py_compile` clean on all five touched modules; `CANDIDATE_STAGE_DISPATCH["requested_artifacts"]` has one `task_key` (no `craft_task_key`); `retire_candidate_requested_wrapper_dispatch_tasks` is delete-only (no `save_dispatch_task` insert).
- Self-Assessment `Scope: MAJOR-CHANGE` / `Conf: high` matches the diff's real footprint; no `!!-NONE` conflict. No Joan plan-rubric verdict attached on this issue — noting per C4 (not a block); the plan's own "Considered but excluded" list lines up with this sweep's `not-applicable`/`conforms` scores, no straggler drift.

## Findings

- **fix-now — B1 imports (`src/core/agent.py`):** the new persist-hook's `from src.core.candidate import _persist_craft_dispatch_success` lazy import has no comment explaining the cycle-break, unlike the established precedent a few lines above in the same function (`from src.core.tracker import pin_job_artifact_agent_data_id` — `# Lazy import breaks agent↔tracker cycle (consult imports agent).`). Add the equivalent one-liner.
- **discuss — no-hardcoded-sets (`src/core/dispatcher.py`):** `_RETIRED_CANDIDATE_REQUESTED_WRAPPER_KEYS` re-declares two literals that already live in `config.DISPATCH_RETIRED_TASK_KEYS`. Comment explains the narrowing intent but not why it's a second hardcoded set instead of config-sourced. Low risk (values match today), but drifts silently if the canonical set changes later.
- **discuss — `orch.git.betty-merge-tests-one-sha`:** publish ref carries two `merge-tests(AST-1252): origin/tests <sha>` commits (`2bbdaea6`→`e0b1bc89`, then `2b127e9c`→`3c004de7` after the repo-admin manifest was narrowed) — the statute's own "Violating" example is exactly this pattern. Not a product bug; flagging for Betty's process awareness.
- **advisory — `data/admin/agent_task.json` (commit `a26c403c`):** beyond removing the two wrapper rows, the file was re-serialized (em-dash/ellipsis → `\uXXXX` escapes) across ~15 unrelated prompt entries, likely `json.dump` without `ensure_ascii=False`. Functionally identical after JSON parse; unnecessary diff noise outside the plan's stated change. Not blocking.

## Cross-ticket boundary

`tests/component/extension/**` / `docs/test-bible/extension/**` (AST-1254, parent AST-1170) appear in the three-dot diff only via the single pinned `origin/tests` SHA merges — conforming per `orch.git.betty-merge-tests-one-sha`'s single-SHA mechanism, not scope creep by this ticket.

## Pattern conformance

`pattern.dispatch.run-next-chain-authority`, `pattern.state.entity-state-transitions`, `pattern.batch.entity-claim-process-release` — all cited, all exist under `canon/patterns/`, all conform per the sweep.

## What's solid

Stage 1–3 match the plan closely: single-`task_key` stage entry, native `do_task` run_next with no manual chain walk, gated Style-D debug on the persist hook with `truncate_debug_content`, retire-only wrapper cleanup called once from `start_scheduler`. Engineer/Betty test-tree boundary holds cleanly (checked per-commit).

## Frame diff

(none — ticket description AC/scope table already accurate, no edits needed)

context_tokens≈42000

— Radia

#### betty — 2026-08-07T07:15:22.867Z
[check-linear]

Cleared Ada `[qa-handoff]`: narrowed manifest item 10 to `TestAst1252RetiredWrapperTaskKeysAbsent` (wrapper keys absent from `data/admin/agent_task.json` + `AST786_EXPECTED_TASK_KEYS`). Did not expand whole-file tip-catalog lock (55→50 / meteorite rename drift stays out of this ticket).

`origin/sub/AST-1243/AST-1252-artifacts-dispatch-chain` @ `2b127e9c` (`merge-tests(AST-1252): origin/tests 3c004de7`)

**Manifest item 10 (replacement):**
`tests/component/core/test_repo_admin_json.py::TestAst1252RetiredWrapperTaskKeysAbsent`

Items 1–9 + 11 unchanged. Reassigned Ada for `test-child`.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1252ArtifactsDispatchChainConfig \
  tests/component/utils/test_config.py::TestAst972CandidateStageDispatch \
  tests/component/utils/test_config.py::TestAst1113CraftTaskKeysShadowDeleted \
  tests/component/utils/test_config.py::TestAst1022HonorAutoOffStageDispatch \
  tests/component/core/test_candidate.py::TestAst972RequestedStageDispatch \
  tests/component/core/test_agent.py::TestAst1252PersistCandidateCraftHops \
  tests/component/core/test_consult.py::TestAst972CandidateStageConsultRouting \
  tests/component/core/test_dispatcher.py::TestAst972CandidateStageDispatch \
  tests/component/core/test_dispatcher.py::TestAst1022HonorAutoOffStageDispatch \
  tests/component/core/test_repo_admin_json.py::TestAst1252RetiredWrapperTaskKeysAbsent \
  tests/component/data/database/test_dispatch_tasks.py::TestAst972CandidateStageEligibility \
  -q
```

Bible: `docs/test-bible/core/candidate.md` `571c12c093bb056149cfc1d642f1e73ad6e0f5e8`

— Betty

#### ada — 2026-08-07T07:13:03.797Z
[qa-handoff]
@Betty White

Manifest item 10 (`tests/component/core/test_repo_admin_json.py` whole file) is red; AST-1252 product cases are green.

**Green (30 passed)** — items 1–9 + 11 as listed:
```bash
ASTRAL_PYTHON=/home/susan/astral/.venv/bin/python ./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1252ArtifactsDispatchChainConfig \
  tests/component/utils/test_config.py::TestAst972CandidateStageDispatch \
  tests/component/utils/test_config.py::TestAst1113CraftTaskKeysShadowDeleted \
  tests/component/utils/test_config.py::TestAst1022HonorAutoOffStageDispatch \
  tests/component/core/test_candidate.py::TestAst972RequestedStageDispatch \
  tests/component/core/test_agent.py::TestAst1252PersistCandidateCraftHops \
  tests/component/core/test_consult.py::TestAst972CandidateStageConsultRouting \
  tests/component/core/test_dispatcher.py::TestAst972CandidateStageDispatch \
  tests/component/core/test_dispatcher.py::TestAst1022HonorAutoOffStageDispatch \
  tests/component/data/database/test_dispatch_tasks.py::TestAst972CandidateStageEligibility \
  -q --no-cov
```

**Red — test/manifest, not product:** running the entire `test_repo_admin_json.py` file fails 22 tests. AST-1252 only removed `candidate_requested_*` from `data/admin/agent_task.json`.

- `TestAst786…` still asserts `len == 55` while `AST786_EXPECTED_TASK_KEYS` is already 53 (wrappers dropped). Tip catalog is **50** keys: expected−actual = `{meteorite_email, meteorite_grade_do, meteorite_grade_get, propose_application_responses}`; actual−expected = `{parse_meteorite_email}` — lock/rename drift outside this ticket’s Files Changed.
- Remaining failures are unrelated classes (`TestAst1196…`, `TestAst1055…`, `TestAst1060…`, `TestAst878…`, `TestAst1015…`, `TestAst787…`, `TestAst1089…`, `TestAst1106…`, `TestAst1144…`, `TestAst1213…`, `TestAst1218…`, `TestAst1219…`, `TestAst1222…`) — fixture/prompt/seq locksteps, not wrapper retire.

Please narrow item 10 to the AST-1252 wrapper-removal assertions (or fix count + expected-set to the tip catalog) and drop unrelated classes from this ticket’s manifest. Staying **Tests Ready**.

`origin/sub/AST-1243/AST-1252-artifacts-dispatch-chain` @ `2bbdaea6`

#### betty — 2026-08-07T07:10:57.925Z
## QA test manifest

`origin/sub/AST-1243/AST-1252-artifacts-dispatch-chain` @ `2bbdaea6` (`merge-tests(AST-1252): origin/tests e0b1bc89`)

1. `tests/component/utils/test_config.py::TestAst1252ArtifactsDispatchChainConfig` — wrappers retired + messages; AC2 REQUESTED_RESUME selectable; no hop-order fields
2. `tests/component/utils/test_config.py::TestAst972CandidateStageDispatch` — revised: artifacts-only stage (`craft_get_rubric`); trigger/entity/admin defaults
3. `tests/component/utils/test_config.py::TestAst1113CraftTaskKeysShadowDeleted` — revised: no `craft_task_key`
4. `tests/component/utils/test_config.py::TestAst1022HonorAutoOffStageDispatch` — revised: `auto_mode` False on remaining stage entry
5. `tests/component/core/test_candidate.py::TestAst972RequestedStageDispatch` — revised: single `do_task(craft_get_rubric)` + `persist_candidate_craft_hops`; no `suppress_run_next`; fail→retry/error; resume worker gone; UI generate still suppresses
6. `tests/component/core/test_agent.py::TestAst1252PersistCandidateCraftHops` — persist hook in `do_task` source; `_persist_craft_dispatch_success` for `craft_get_rubric`
7. `tests/component/core/test_consult.py::TestAst972CandidateStageConsultRouting` — revised: routes `craft_get_rubric`; wrapper keys not routed
8. `tests/component/core/test_dispatcher.py::TestAst972CandidateStageDispatch` — revised: `retire_candidate_requested_wrapper_dispatch_tasks`; claim gate; scheduler retire hook
9. `tests/component/core/test_dispatcher.py::TestAst1022HonorAutoOffStageDispatch` — revised: Style D AUTO-off for `craft_get_rubric` only
10. `tests/component/core/test_repo_admin_json.py` — wrappers removed from `AST786_EXPECTED_TASK_KEYS`
11. `tests/component/data/database/test_dispatch_tasks.py::TestAst972CandidateStageEligibility` — revised: claim-state companions + list ids on `craft_get_rubric` (candidate Avail remains inflow-only)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1252ArtifactsDispatchChainConfig \
  tests/component/utils/test_config.py::TestAst972CandidateStageDispatch \
  tests/component/utils/test_config.py::TestAst1113CraftTaskKeysShadowDeleted \
  tests/component/utils/test_config.py::TestAst1022HonorAutoOffStageDispatch \
  tests/component/core/test_candidate.py::TestAst972RequestedStageDispatch \
  tests/component/core/test_agent.py::TestAst1252PersistCandidateCraftHops \
  tests/component/core/test_consult.py::TestAst972CandidateStageConsultRouting \
  tests/component/core/test_dispatcher.py::TestAst972CandidateStageDispatch \
  tests/component/core/test_dispatcher.py::TestAst1022HonorAutoOffStageDispatch \
  tests/component/core/test_repo_admin_json.py \
  tests/component/data/database/test_dispatch_tasks.py::TestAst972CandidateStageEligibility \
  -q
```

**Bible shasums** (`origin/sub/...` tip):
- `docs/test-bible/core/candidate.md` `599e80ee17a49d286700ae1626e89b1000f6e5c6`
- `docs/test-bible/utils/config.md` `ea1ea61e56e1e616a95fc90111459f75a26779cb`
- `docs/test-bible/core/agent.md` `6e093eb3aa3eb5a3179ea339ddbdf708f46a78f0`
- `docs/test-bible/core/consult.md` `8606b4a3a2c99c0b15b59addf62a566a8d9e07ed`
- `docs/test-bible/core/dispatcher.md` `9b9ce46fa1749501290337115a07557834f1987a`

**Integration:** none revised (no existing scenarios on wrapper keys).

— Betty

#### joan — 2026-08-07T06:46:08.110Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1252
**Overall:** APPROVED
**Publish ref tip:** `sub/AST-1243/AST-1252-artifacts-dispatch-chain` @ `1abfa1a8`

## Traceability

AC1→S1,S2,S3; AC2→S1; AC3→S2; AC4→S2; AC5→S2; AC6→S1,S2,S3; AC7→S2. No unmapped AC, no orphan stage — the Stage 3 retire helper now maps to AC1.

## Round 1 disposition

All four items cleared. The fix-now is gone: Stage 3 is retire-only, with an explicit "do not add `ensure_candidate_artifacts_dispatch_tasks` / `provision_candidate_artifacts_dispatch_tasks`" and the seed reasoning recorded in the plan, so `astral.seed.define-approved`, `astral.seed.operator-rows-stay-deleted`, and `astral.standards.in-scope-only` now score conforms. Delete-only passes are not seed, so the retained breadth (template + candidates with ≥1 dispatch row) is fine — nothing gets re-inserted. The resume removal and the partial-artifact behaviour are now explicit Decision blocks, and `craft_task_key` is collapsed into `task_key`.

I re-checked that the collapse does not break anything off the file list: the only readers of the stage `craft_task_key` field are `candidate.py:2456` and `:2496` (both rewritten or deleted) and the `config.py` asserts, and the only readers of `CANDIDATE_STAGE_DISPATCH["requested_resume"]` are `config.py`, `candidate.py`, and `consult.py` — all inside Files Changed. The `craft_task_key` hits in `api_candidate.py` are a local loop variable, not the config field.

## Findings

**discuss — a superseded hardcoded craft chain still lives in `src/data/database.py`.**
`_apply_ast1113_craft_run_next_chain_migration` (`database.py:4931`) hardcodes the old AST-1113 succession — head `craft_company_search_terms`, and `craft_do_rubric → craft_get_rubric → craft_like_rubric` — and actively `UPDATE`s `agent_task.run_next` wherever the DB disagrees. That is the exact topology this ticket is replacing, and its head is the same stale `craft_company_search_terms` value that today's `craft_task_key` points at, so it is a fossil of the pre-`origin/dev` chain. Its siblings for AST-469 and AST-834 were already neutered to bare `return`; this one was not.

I chased whether it can clobber AC6 and it cannot, today: `apply_agent_task_repo_json_startup` (`database.py:757`) calls `_ensure_agent_task_schema` first — which is where the migration fires, once per process behind the `_agent_task_schema_ensured` flag — and only then retires every current row and re-applies `data/admin/agent_task.json` with exact field values, so repo JSON wins the boot ordering and the live chain stays headed by `craft_get_rubric`. So Stage 3 step 3's "trust `origin/dev` topology" holds. It holds because of call ordering inside one function, though, which is a thin guarantee for something AC3/AC4/AC6 all sit on. Record that reasoning in the plan rather than leaving it as an assumption, and consider neutering the migration the way its siblings were — that would need `src/data/database.py` added to Files Changed, so it is equally reasonable as a follow-up ticket. Scored `needs-discussion` against `astral.dispatch.run-next-is-chain-authority` and `astral.standards.no-hardcoded-sets`; not blocking, since the statutes bind this ticket's own changes and the plan adds no new hop list.

**acceptable — no auto-seed is an operational consequence, honestly stated.** With provisioning dropped, nothing creates `(craft_get_rubric, REQUESTED_ARTIFACTS)`; operators or set-from-template must. The Risk line says so outright, which is the right call — UAT will need that row created by hand before the chain can be exercised.

**acceptable — retire messaging.** `dispatch_task_key_retired_message` raises `KeyError` if a retired key appears in neither the replacement map nor the static-message map; Stage 1 step 4 covers both wrappers explicitly.

**acceptable — self-assessment is honest.** MAJOR-CHANGE / high / HIGH is right, and the Risk line now names the resume-automation removal and the manual row creation rather than only the persist-placement hazard.

**Considered:** full active corpus scored in-session (18 universal + scoped matches on layers `utils`/`core`/`data`, unchanged from round 1 since Files Changed is the same six paths); UI, scripts, docs, and test-tree scoped statutes excluded on layer/path predicates. Zero `violates`.

context_tokens≈108000

— Joan

#### ada — 2026-08-07T06:41:06.893Z
[plan-discuss] round=1 reply

Plan revised on `origin/sub/AST-1243/AST-1252-artifacts-dispatch-chain` @ `1abfa1a8`.

**fix-now:** Dropped `ensure`/`provision` of `(craft_get_rubric, REQUESTED_ARTIFACTS)`. Stage 3 is retire-only delete of wrapper `dispatch_task` rows + consult routing + admin JSON cleanup. No new seed catalog.

**discuss (resume path):** Stated as intentional capability removal — REQUESTED_RESUME → `craft_resume_base` → RESUME_READY automation ends with the wrappers; parent brief “pull those elements out entirely.” AC2 selectability of REQUESTED_RESUME for `craft_get_rubric` unchanged.

**discuss (partial persist):** Mid-chain failure leaves hops 1..N−1 written; candidate still goes retry/error; retry re-enters at `craft_get_rubric` and overwrites — expected/self-healing.

**acceptable:** Collapsed to single `task_key` (no parallel `craft_task_key`).

Status stays Plan Discuss for Joan re-sweep.

#### joan — 2026-08-07T06:37:34.212Z
[plan-discuss] round=1 concern
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1252
**Overall:** REVISE
**Publish ref tip:** `sub/AST-1243/AST-1252-artifacts-dispatch-chain` @ `9144d909`

## Traceability

AC1→S1,S2,S3; AC2→S1; AC3→S2; AC4→S2; AC5→S2; AC6→S1,S2; AC7→S2. Orphan: S3 step 2 provision half maps to no AC (see fix-now).

## Findings

**fix-now — Stage 3 step 2 introduces a new, unapproved product seed catalog.**
There is no candidate-stage provisioning today. `CANDIDATE_STAGE_DISPATCH` is read in exactly three places — consult routing (`src/core/consult.py:2480`), the AUTO-off debug log (`src/core/dispatcher.py:1164`), and the config asserts — and the only provision peers in the tree are `provision_meteorite_dispatch_tasks` and `provision_gaze_email_dispatch_tasks`. So `ensure_candidate_artifacts_dispatch_tasks` / `provision_candidate_artifacts_dispatch_tasks` would be a brand-new startup ensure catalog covering the template candidate plus every candidate that already has a dispatch row. Parent AST-1243 carries no Seed needs section naming the table, row shape, coverage join, or CLICK/AUTO at seed, and no child AC asks for auto-provisioning — AC2 is about create-time *selectability*, not row creation. This violates `astral.seed.define-approved`, and because the catalog is not Archie-named it also re-inserts operator-deleted rows against `astral.seed.operator-rows-stay-deleted` (`astral.seed.archie-catalog-wins` only protects named catalogs). `astral.standards.in-scope-only` and R5 (orphan stage) fail on the same text.
*Recommendation:* drop ensure/provision from this ticket and keep only the retire half AC1 actually needs — delete live `dispatch_task` rows whose `task_key` is a retired wrapper. If auto-provisioning is genuinely wanted, it needs a Seed needs section on AST-1243 and Archie approval before build.

**discuss — the wiring instruction for that provision rests on a false premise.**
Stage 3 step 2 says to invoke it "from the same scheduler/boot hook that previously provisioned stage rows (or ... if stage provision was removed, wire beside `provision_meteorite_dispatch_tasks`)". No stage provision ever existed, so the conditional leaves the call site to the builder — `orch.pipeline.plan-is-bible`. Moot if the fix-now is applied by dropping provision.

**discuss — deleting the resume stage removes a working capability, not just a wrapper name.**
Stage 1 step 2 plus Stage 2 step 4 drop `CANDIDATE_STAGE_DISPATCH["requested_resume"]` and `run_requested_resume_dispatch`, which ends the REQUESTED_RESUME → `craft_resume_base` → RESUME_READY dispatch path entirely. AC1 only requires the wrapper *task key* to stop being a live dispatch key; the capability could survive as a stage whose `task_key` is `craft_resume_base`. Susan's brief ("pull those elements out entirely") probably authorizes the removal and you did flag it under Risk, but `orch.pipeline.call-susan-for-product-decisions` wants it stated as an intentional capability removal in the plan with an ack, not left as a side effect of retiring a name.

**discuss — partial persistence on mid-chain failure is unspecified.**
The live chain is eight hops. If hop N fails, hops 1..N−1 have already written candidate artifacts; the candidate then lands on retry/error, so AC5 holds and nothing is silently stuck, and a retry re-enters at `craft_get_rubric` and overwrites. Say that explicitly in the plan so Betty and UAT know partial artifacts are expected and self-healing rather than corruption.

**acceptable — redundant stage keys.** Stage 1 step 2 sets both `task_key` and `craft_task_key` to `"craft_get_rubric"`. Two fields holding one string invite drift; consider collapsing to `task_key` and having Stage 2 read that.

**acceptable — the core mechanism checks out.** I verified the load-bearing claims against the tree rather than taking them on trust: `run_next` recursion is gated only by `suppress_run_next` (`agent.py:2927`), so dropping the suppress flag is sufficient to fan the chain; the recursive call re-passes the same `ctx` object (`agent.py:3047`), so `persist_candidate_craft_hops` and `astral_candidate_id` reach every hop without extra plumbing; and hop ledgers open whenever the row has a `run_next` and a candidate id is present (`agent.py:2180`), which is what buys AC3. The live topology is `craft_get_rubric → do → like → evaluate_meteorite → jobdesc → joblist → prefilter → company_search_terms`, and every hop after the head consumes `{$CALLER_RESPONSE}` / `{$CALLER_CACHE_*}` — the AST-1113 suppressed manual walk structurally cannot feed those, so moving to native `run_next` is the right correction and the current `craft_task_key` pointing at the chain *tail* is a real bug this fixes. AC2 is also safe as you claimed: `_dispatch_task_key_trigger_error` checks registry membership only, so `craft_get_rubric` + `REQUESTED_RESUME` still passes with no `api_admin.py` edit needed.

**Considered:** full active corpus scored in-session (18 universal + scoped matches on layers `utils`/`core`/`data`); UI, scripts, docs, and test-tree scoped statutes excluded on layer/path predicates.

context_tokens≈82000

— Joan

#### ada — 2026-08-07T06:28:49.377Z
Plan published on `origin/sub/AST-1243/AST-1252-artifacts-dispatch-chain` @ `9144d909`.

[Plan doc](https://github.com/susansomerset/astral/blob/sub/AST-1243/AST-1252-artifacts-dispatch-chain/docs/features/candidate/ast-1252-artifacts-dispatch-chain-persistence-and-retire-wrappers.md)

**Scope:** MAJOR-CHANGE — retires wrapper dispatch keys, rewires REQUESTED_ARTIFACTS onto `craft_get_rubric` + native `run_next` with per-hop persist/ledgers (utils/core/admin seed).

**Conf:** high — entry hop and `run_next` already on origin/dev; `_persist_craft_dispatch_success` and stage failure targets exist; BUILD_ARTIFACTS hop ledgers are the template; UI keeps `suppress_run_next`.

**Risk:** HIGH — bad persist placement skips/double-writes mid-chain artifacts; retiring resume wrapper drops old REQUESTED_RESUME→craft_resume_base automation; provision mistakes leave dead task_keys or AUTO-on seeds.

---

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



## Bug: AST-1417 — save_candidate hop-label persist coverage

Test-gap sibling of AST-1416. Betty board REVISE: `save_candidate` persist of `REQUESTED_ARTIFACTS.<hop>` was uncovered (`TestSaveCandidate` only rejected `NOT_A_STATE`). qa-fix landed `[bug-repro]`; product carve-out is AST-1416. Product code is AST-1416; this child is test-only (docs-acceptance).

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
| Ada | engineer | `/home/susan/.cursor/chats/f1e754be6ffa4c3cfe10adfe0290f5f8/a3d3de92-1c3d-469a-945b-27540354d0a8/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/2be20b36-8d49-4b14-9291-39b983413666/store.db` |
| Radia | review | `/home/susan/.cursor/chats/f1e754be6ffa4c3cfe10adfe0290f5f8/97cc450a-880b-4a0e-b4f7-094aeee865ee/store.db` |

### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-1415 (parent) | ftr/AST-1415-candidate-state-validation-bug |
| AST-1416 | sub/AST-1415/AST-1416-restore-hop-label-membership |
| AST-1417 | sub/AST-1415/AST-1417-save-candidate-hop-label-coverage |

**Epic worktree:** `astral-AST-1415/` — one active sub checked out at a time.
