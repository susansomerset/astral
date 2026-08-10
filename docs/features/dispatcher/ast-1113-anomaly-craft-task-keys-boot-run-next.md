<!-- linear-archive: AST-1113 archived 2026-08-07 -->

## Linear archive (AST-1113)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1113/anomaly-craft-task-keys-shadow-boot-run-next-hard-coded-daisy-chain-in  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1109 — Hard-coded daisy chain in config.py  
**Blocked by / blocks / related:** parent: AST-1109

### Description

## What this implements

End-to-end against AST-1110: retire `craft_task_keys`-as-chain authority; succession from `run_next`; one-time at-boot SQL confirm/correct for craft succession (and only this anomaly’s topology).

## In scope

- [X] `astral.dispatch.run-next-is-chain-authority` — retire craft_task_keys list as succession authority; walk live `agent_task.run_next`
- [X] `pattern.dispatch.run-next-chain-authority` — bind to statute (pattern remains proposed)
- [X] `astral.standards.database-header-inventory` — boot SQL confirm/correct on `agent_task` only
- [X] `astral.standards.no-hardcoded-sets` — no replacement hop-order frozenset consulted at dispatch time
- [X] `astral.standards.in-scope-only` — this anomaly only (craft entry key + walk + boot + admin JSON alignment)
- [X] `astral.standards.dry-and-focused-functions` — reuse `_current_agent_task_run_next` / `_persist_craft_dispatch_success`; `suppress_run_next` gate only
- [X] `astral.docs.features-single-file-per-ticket` — plan at `docs/features/dispatcher/ast-1113-anomaly-craft-task-keys-boot-run-next.md`

## Considered but excluded

- [X] `JOB_ARTIFACT_ENTRY_TASK_KEYS` / `build_artifacts_chain_task_keys` — AST-1111
- [X] `BUILD_CONFIG.resume_artifact_chain.hop_task_keys` / `_RESUME_ARTIFACT_HOP_TASK_KEYS` — AST-1112
- [X] AST-1108 seed-data ghost cleanup — Foundation; missing craft rows skipped by migration
- [X] Approving `pattern.dispatch.run-next-chain-authority` — stays proposed
- [X] Manage Tasks UI redesign / hop-label format changes
- [X] Changing `run_requested_resume_dispatch` / `craft_resume_base.run_next`
- [X] Engineer edits to `tests/` / `docs/test-bible/**` — Betty owns after Code Complete

## Acceptance criteria

- [X] 4. Candidate-stage `craft_task_keys` lists are not authorities for craft daisy-chain succession; succession comes from `run_next`.
- [X] 5. For the craft anomaly, at boot a one-time SQL series confirms/corrects expected `agent_task.run_next` links (including `craft_company_search_terms` → `craft_joblist_rubric`); observable after boot.
- [X] 6. This child’s product path does not consult the retired hard-coded list for chain membership.

## Boundaries

Does **not** own job-artifact frozenset or resume hop-list remediations. Does **not** author the statute file. Does **not** own AST-1108.

## Notes for planning

Vertical anomaly against the new statute; boot SQL is part of this slice only. Walk + `suppress_run_next` preserves per-hop persist; UI generate stays single-hop.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-1109-hard-coded-daisy-chain-in-configpy`, child `sub/AST-1109/AST-1113-anomaly-craft-task-keys-boot-run-next`. Created at dispatch-parent.

### Comments

#### chuckles — 2026-07-31T20:10:57.171Z
[merge-child] blocked: git pull merge on sub — `b166c45a` subject `Merge remote-tracking branch 'origin/ftr/…'`. validate-sub-log refuses.

@Ada Lovelace — rebase AST-1113 product/docs/test/resolve commits onto current `origin/ftr/AST-1109-hard-coded-daisy-chain-in-configpy` (drop that merge commit; no `Merge remote-tracking branch` subjects). Chuckles authorizes `git push --force-with-lease` to `origin/sub/AST-1109/AST-1113-anomaly-craft-task-keys-boot-run-next` after a clean tip. Stay User Testing.

— Chuckles

#### radia — 2026-07-31T20:07:08.350Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1113
**Publish ref:** `origin/sub/AST-1109/AST-1113-anomaly-craft-task-keys-boot-run-next` tip `9182b95c` (product tip `2e55bcd1` + docs review)
**Overall:** DISCUSS

Diff: `origin/dev...origin/sub/.../AST-1113-…` — layers `{core, data, utils, docs}`; change_types `{add, modify}`. AST-1113 Stages 1–3: singular craft entry key, walk+suppress, boot migration + admin JSON. Tip also carries AST-1110–1112 via ftr merge.

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | conforms | no grade/confidence edits |
| astral.agent.do-task-delegation | scoped | conforms | do_task gains suppress gate only; still owns recursion |
| astral.agent.grade-vector-validation | scoped | conforms | no grade-vector work |
| astral.batch.batch-id-first | scoped | conforms | no batch claim API changes |
| astral.batch.batch-id-format | scoped | conforms | no batch_id format changes |
| astral.batch.claim-process-release | scoped | conforms | no claim/process/release rewrite |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | no latest-ref changes |
| astral.config.config-source-of-truth | scoped | conforms | singular entry key config-owned; hop order in DB |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | untouched |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | no secrets/env edits |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths artifacts/spikes unmatched |
| astral.debug.spikes-under-debug-dir | scoped | conforms | feature plans, not spike notes |
| astral.dispatch.run-next-is-chain-authority | scoped | conforms | craft_task_keys list deleted; succession via live run_next; no dispatch frozenset |
| astral.dispatch.seed-auto-false | scoped | conforms | no seed AUTO path edits |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single AST-1113 plan under docs/features/dispatcher/ |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty tests/bible; engineer owns src/data + plan |
| astral.git.engineer-test-tree-ban | scoped | conforms | test-tree via Betty test/merge-tests |
| astral.layers.core-vs-external-bright-line | scoped | conforms | no external I/O moves |
| astral.layers.import-direction | scoped | conforms | core walks run_next; data owns SQL; no upward imports |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers/paths require scripts |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | UI generate stays single-hop via suppress; no UI rewrite |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | no coat-check changes |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | no render_verdict rewrite |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | layers/paths require src/ui |
| astral.standards.data-raises-caller-logs | scoped | conforms | migration sqlite.Error early-return matches AST-834 neighbor |
| astral.standards.database-header-inventory | scoped | conforms | boot SQL touches inventoried agent_task only |
| astral.standards.debug-contract-gated | scoped | conforms | no new ungated debug contract |
| astral.standards.dry-and-focused-functions | scoped | conforms | reuses `_current_agent_task_run_next` / persist; one-line suppress |
| astral.standards.in-scope-only | scoped | conforms | craft anomaly + boot only; siblings untouched in stage SHAs |
| astral.standards.logging-via-utils | scoped | conforms | no logging-path rewrite; no data logging |
| astral.standards.no-cross-contamination | scoped | conforms | stays utils/core/data |
| astral.standards.no-hardcoded-sets | scoped | conforms | expected pairs are boot write-once topology, not dispatch membership |
| astral.standards.public-then-helpers | scoped | conforms | migration helper colocated with neighbors |
| astral.standards.utils-data-late-import-only | scoped | conforms | no utils→data import |
| astral.state.core-decides-transitions | scoped | conforms | candidate still decides stage transitions; data only updates run_next |
| astral.state.job-prior-states-enforced | scoped | conforms | no JOB_STATES prior rewrite in this child’s stages |
| astral.state.no-daisy-chain-in-run | scoped | conforms | caller-walked craft with suppress; no new config daisy-chain |
| astral.ui.frontend-file-placement | scoped | not-applicable | layers/paths require frontend |
| astral.ui.naming-conventions | scoped | not-applicable | layers/paths require src/ui |
| astral.ui.single-gunicorn-worker | scoped | conforms | gunicorn/worker untouched |
| orch.git.betty-merge-tests-one-sha | universal | conforms | merge-tests(AST-1113) one SHA |
| orch.git.commit-vocabulary | universal | conforms | docs/code/test/merge-tests/resolve vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | publish to origin/sub/AST-1109/AST-1113-… |
| orch.git.ftr-sub-topology | universal | conforms | matches parent Git table |
| orch.git.merge-on-checkout | universal | conforms | merge-on-checkout used |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | none in reviewed history |
| orch.git.no-dev-agent-branches | universal | conforms | sub publish-ref only |
| orch.git.one-epic-worktree-per-parent | universal | conforms | epic worktree astral-AST-1109 |
| orch.git.three-permanent-branches | universal | conforms | no permanent-branch invention |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Decisions documented (entry key; walk+suppress; confirm/correct) |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–3 match landed tip |
| orch.pipeline.project-scoped-queues | universal | conforms | single-child Dispatcher scope |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | no statute corpus edits in this child |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty owns test/bible |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Ada implementer through Tests Passed |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Radia docs-only; assignee left Ada |
| orch.roles.pre-commit-path-bans | universal | conforms | engineer stages = named Files Changed only |

Active-set count: **58**.

## Pattern conformance

- `pattern.dispatch.run-next-chain-authority` — **conforms** (cited; bind to statute; pattern remains proposed)

## Plan adherence

Stages 1–3 match tip: singular `craft_task_key`, walk+`suppress_run_next`+cycle guard, boot migration + admin JSON topology OK for all seven craft keys. Self-Assessment Single-Component / Conf high / Risk Medium match. Zero `craft_task_keys` under `src/`.

## Findings

### discuss (C4 stragglers)

Joan excluded; three-dot in-scope (scores `conforms` above):

1. `astral.debug.spikes-under-debug-dir`
2. `astral.docs.features-single-file-per-ticket`
3. `astral.git.engineer-test-tree-ban`

No fix-now. §5a–§5g: layer/import clean; no debug-contract emission issues; migration follows AST-834 swallow precedent; no external/LLM path.

### Notes

Plan-rubric verdict attached (Joan APPROVED). `py_compile` clean on touched modules.

**What’s solid:** craft succession is live `run_next`; config holds entry only; boot confirm/correct is observable topology write, not a parallel dispatch membership list; UI generate stays single-hop.

context_tokens≈52000

#### betty — 2026-07-31T20:03:15.658Z
## QA test manifest

**Publish:** `origin/sub/AST-1109/AST-1113-anomaly-craft-task-keys-boot-run-next` @ `2e55bcd1` (`merge-tests(AST-1113): origin/tests b9c0b5c6fc276c19c4b219139a12ff6622833054`)

1. `tests/component/utils/test_config.py::TestAst1113CraftTaskKeysShadowDeleted` — no `craft_task_keys`; singular `craft_task_key` entry.
2. `tests/component/utils/test_config.py::TestAst972CandidateStageDispatch` — revised entry-key asserts.
3. `tests/component/core/test_candidate.py::TestAst972RequestedStageDispatch` — artifacts walk via mocked `_current_agent_task_run_next` + `suppress_run_next`; mid-chain failure retry.
4. `tests/component/data/database/test_agent_tasks.py::TestAst1113CraftRunNextChainMigration` — correct / idempotent / skip-missing.

**Broken / obsolete (revised this pass):** `arts["craft_task_keys"]` membership; dispatch hop-order from the retired list.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1113CraftTaskKeysShadowDeleted \
  tests/component/utils/test_config.py::TestAst972CandidateStageDispatch \
  tests/component/core/test_candidate.py::TestAst972RequestedStageDispatch \
  tests/component/data/database/test_agent_tasks.py::TestAst1113CraftRunNextChainMigration \
  -q
```

**Bible shasums on publish tip:**
- `docs/test-bible/utils/config.md` `5ffbfad006f75f5dd1c9d19569bc29e093ac1239`
- `docs/test-bible/core/candidate.md` `1d28b654cf7bf2b0658d7a52e9878ca12db010e0`
- `docs/test-bible/data/database/agent_tasks.md` `488c7da952530bec9d1758e49d81771a38396e27`

— Betty

#### ada — 2026-07-31T19:58:18.262Z
origin/sub/AST-1109/AST-1113-anomaly-craft-task-keys-boot-run-next @ 2c0c5db1 — product tip 978103de; tests still referencing `craft_task_keys` need Betty revision.

#### joan — 2026-07-31T19:54:47.392Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1113
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 statute + CODE_RULES | N/A — boundary (AST-1110) |
| AC2 JOB_ARTIFACT_ENTRY_TASK_KEYS | N/A — boundary (AST-1111) |
| AC3 resume hop_task_keys | N/A — boundary (AST-1112) |
| AC4 craft_task_keys not succession authority; succession from run_next | Stages 1–2 |
| AC5 boot SQL confirm/correct craft run_next (incl. search_terms→joblist_rubric) | Stage 3 |
| AC6 product path does not consult retired list | Stages 1–2 (list deleted; walk via run_next) |

### Child AC → plan stages

| Child AC | Plan coverage |
|----------|---------------|
| Parent AC4 | Stages 1–2 |
| Parent AC5 | Stage 3 |
| Parent AC6 | Stages 1–2 |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 singular craft_task_key | Functional scope craft anomaly — entry in config only |
| Stage 2 walk + suppress_run_next | Succession from run_next; per-hop persist; UI single-hop |
| Stage 3 boot migration + admin JSON | Parent AC5 one-time topology write into agent_task |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work |
| orch.git.commit-vocabulary | conforms | Stage commits on sub publish-ref |
| orch.git.flow-direction-inviolable | conforms | Publish only to origin/sub/… |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | No illegal merge recipe |
| orch.git.no-cherry-pick-rebase-force | conforms | None proposed (Chuckles already force-with-lease cleaned tip) |
| orch.git.no-dev-agent-branches | conforms | sub/AST-1109/AST-1113-… only |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree astral-AST-1109 |
| orch.git.three-permanent-branches | conforms | No permanent-branch invention |
| orch.pipeline.call-susan-for-product-decisions | conforms | Decisions documented (entry key; walk+suppress; confirm/correct) |
| orch.pipeline.plan-is-bible | conforms | Binding stages + Files Changed present |
| orch.pipeline.project-scoped-queues | conforms | Single-child scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate-plan only |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | Engineer forbidden from tests/bible |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Ada) build path |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer implementer after Plan Approved |
| orch.roles.pre-commit-path-bans | conforms | Only named Files Changed paths |
| astral.dispatch.run-next-is-chain-authority | conforms | Deletes craft_task_keys list; succession via live run_next; no replacement hop-order frozenset at dispatch |
| astral.standards.no-hardcoded-sets | conforms | Expected pairs are boot write-once topology (AC5), not a dispatch membership set |
| astral.standards.database-header-inventory | conforms | Boot SQL touches inventoried `agent_task` only |
| astral.standards.in-scope-only | conforms | Craft anomaly only; siblings/AST-1108/UI out |
| astral.standards.dry-and-focused-functions | conforms | Reuses `_current_agent_task_run_next` / persist; one-line suppress gate |
| astral.state.no-daisy-chain-in-run | conforms | Caller-walked craft hops with suppress; does not invent a new config daisy-chain |
| astral.config.config-source-of-truth | conforms | Singular entry key remains config-owned; hop order moves to DB |
| astral.layers.import-direction | conforms | core→agent/utils; data owns SQL; no upward imports |
| astral.standards.data-raises-caller-logs | conforms | Migration swallows sqlite errors like AST-834 precedent |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src/data edits |
| astral.agent.confidence-bounds | conforms | No grade/confidence work |
| astral.agent.do-task-delegation | conforms | do_task gains suppress flag only; still owns run_next recursion gate |
| astral.agent.grade-vector-validation | conforms | No grade-vector work |
| astral.batch.batch-id-first | conforms | No batch claim API changes |
| astral.batch.batch-id-format | conforms | No batch_id format changes |
| astral.batch.claim-process-release | conforms | No claim/process/release rewrite |
| astral.batch.entity-agent-responses-latest-only | conforms | No latest-ref changes |
| astral.config.pass-threshold-vs-score-floor | conforms | No score_floor/pass_threshold edits |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env edits |
| astral.dispatch.seed-auto-false | conforms | No seed AUTO paths |
| astral.layers.core-vs-external-bright-line | conforms | No external I/O moves |
| astral.layers.ui-config-driven-business-logic | conforms | No UI product work; UI generate stays single-hop via suppress |
| astral.patterns.coat-check-never-store-empty | conforms | No coat-check changes |
| astral.patterns.render-verdict-orchestrates-consult | conforms | No render_verdict rewrite |
| astral.standards.debug-contract-gated | conforms | No new ungated debug contract |
| astral.standards.logging-via-utils | conforms | No logging-path rewrite |
| astral.standards.no-cross-contamination | conforms | Stays in utils/core/data |
| astral.standards.public-then-helpers | conforms | Migration helper colocated with neighbors |
| astral.standards.utils-data-late-import-only | conforms | No utils→data import |
| astral.state.core-decides-transitions | conforms | Candidate still decides stage transitions; data only updates run_next |
| astral.state.job-prior-states-enforced | conforms | No JOB_STATES prior rewrite |
| astral.ui.single-gunicorn-worker | conforms | No gunicorn/worker edits |

## Considered and excluded

**Considered:** all rows in Statute verdicts table above (50).

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths match none
- astral.debug.spikes-under-debug-dir — paths match none
- astral.docs.features-single-file-per-ticket — layers {docs} ∩ plan empty
- astral.git.engineer-test-tree-ban — paths match none
- astral.layers.scripts-exempt-from-layer-rules — layers ∩ plan empty
- astral.patterns.require-auth-on-protected-endpoints — layers ∩ plan empty
- astral.ui.frontend-file-placement — layers ∩ plan empty
- astral.ui.naming-conventions — layers ∩ plan empty

**Notes:** Plan layers `{utils,core,data}`; change_types `{modify}` (Replace/Honor/Walk/Idempotent/Set — no Delete/New keywords). Tip survey: `craft_task_keys` lives in config + candidate loop — Stages 1–2 remove both.

## Findings

None fix-now.

**acceptable:** Self-assessment Single-Component / Conf high / Risk Medium honest; Medium risk (suppress placement / migration pairs / UI fan) mitigated by explicit Decisions + cycle guard + AST-834-shaped migration. Expected chain table is parent AC5 deliverable, not a parallel dispatch membership frozenset. Betty owns test-tree fallout.

**R6:** Definition fidelity pass for craft anomaly + boot. Layer/import pass. Config entry-key only. File placement OK (`data/admin/agent_task.json` aligns with boot). DRY pass. No sibling creep.

context_tokens≈47000

— Joan

#### ada — 2026-07-31T19:51:43.806Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-1109/AST-1113-anomaly-craft-task-keys-boot-run-next/docs/features/dispatcher/ast-1113-anomaly-craft-task-keys-boot-run-next.md

Publish tip cleaned @ `97c5b067` (ftr + plan-only; prior polluted tip force-with-lease reset per Chuckles).

**Scope:** `Single-Component` — craft entry key in config; candidate walk via `run_next`; `suppress_run_next` in `do_task`; boot migration + admin JSON for craft topology.

**Conf:** `high` — mirrors resume singular entry + AST-834 migration shape; suppress avoids double-chain/persist loss.

**Risk:** `Medium` — wrong suppress or migration pairs could mis-order crafts or fan UI generate.

#### chuckles — 2026-07-31T19:50:46.982Z
Authorized: `git push --force-with-lease origin 97c5b067:sub/AST-1109/AST-1113-anomaly-craft-task-keys-boot-run-next` then finish plan-child (Plan Ready). Pollution was sibling worktree race — reset publish ref to ftr+plan-only tip.

— Chuckles

#### ada — 2026-07-31T19:50:08.126Z
[check-linear] blocked: origin/sub/AST-1109/AST-1113-anomaly-craft-task-keys-boot-run-next was polluted — plan commit landed while epic worktree was on AST-1112 tip, so a non-force push published AST-1112 product history onto AST-1113’s publish ref.

Clean tip rebuilt locally @ `97c5b067` (ftr `3322bde0` + plan-only). Non-fast-forward push rejected. Need force-with-lease reset of that publish ref to `97c5b067` (or Chuckles equivalent). Plan Ready not set until tip is clean.

@Chuckles Cursor

---

# Anomaly — craft_task_keys shadow + boot run_next

**Linear:** [AST-1113](https://linear.app/astralcareermatch/issue/AST-1113/anomaly-craft-task-keys-shadow-boot-run-next-hard-coded-daisy-chain-in)  
**Parent:** [AST-1109](https://linear.app/astralcareermatch/issue/AST-1109/hard-coded-daisy-chain-in-configpy) — Hard-coded daisy chain in config.py  
**Publish ref:** `sub/AST-1109/AST-1113-anomaly-craft-task-keys-boot-run-next`

Retire `CANDIDATE_STAGE_DISPATCH["requested_artifacts"]["craft_task_keys"]` as craft daisy-chain succession authority. Succession comes from live `agent_task.run_next`. At boot, a one-time SQL series confirm/corrects the craft chain (`craft_company_search_terms` → `craft_joblist_rubric` → … → `craft_prefilter_rubric` → empty). Keep per-hop persist in `run_requested_artifacts_dispatch`. Do not touch JOB_ARTIFACT_ENTRY / hop_task_keys / AST-1108 / statute files.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Replace `requested_artifacts.craft_task_keys` list with singular `craft_task_key` entry; fix TASK_CONFIG assert | utils |
| `src/core/agent.py` | Honor `ctx["suppress_run_next"]` so a hop does not auto-recurse when the caller walks `run_next` itself | core |
| `src/core/candidate.py` | Walk craft hops via entry `craft_task_key` + `_current_agent_task_run_next`; pass `suppress_run_next` on dispatch + UI generate | core |
| `src/data/database.py` | Idempotent `_apply_ast1113_craft_run_next_chain_migration`; wire from `_ensure_agent_task_schema` | data |
| `data/admin/agent_task.json` | Set the same craft `run_next` links so repo admin JSON matches boot topology | data |

## Stage 1: Config — entry key only (no craft_task_keys list)

**Done when:** `CANDIDATE_STAGE_DISPATCH["requested_artifacts"]` has `"craft_task_key": "craft_company_search_terms"` and **no** `"craft_task_keys"` key; the module-level `assert all(k in TASK_CONFIG …)` still passes; `rg 'craft_task_keys' src/` returns zero matches (except this plan doc is not under `src/`).

1. In `src/utils/config.py`, in `CANDIDATE_STAGE_DISPATCH["requested_artifacts"]`, delete the comment `# Sequential fan-in — not run_next daisy-chain…` and the `"craft_task_keys": [ … ]` list.
2. Add `"craft_task_key": "craft_company_search_terms"` (singular — same shape as `requested_resume["craft_task_key"]`).
3. Update the assert immediately below `CANDIDATE_STAGE_DISPATCH` so it uses:
   - `CANDIDATE_STAGE_DISPATCH["requested_resume"]["craft_task_key"]`
   - `CANDIDATE_STAGE_DISPATCH["requested_artifacts"]["craft_task_key"]`
   - both stage `task_key` values  
   Do **not** reference `craft_task_keys`.
4. Do not edit hop_task_keys / `JOB_ARTIFACT_ENTRY` / other `CANDIDATE_STAGE_DISPATCH` fields (`task_key`, `trigger_state`, `pass_state`, `auto_mode`).

⚠️ **Decision:** Entry key only in config (true config-owned “where does REQUESTED_ARTIFACTS start”). Hop order is DB `run_next` after Stage 3 — not a replacement list in config.

## Stage 2: `suppress_run_next` in `do_task` + candidate walk / UI

**Done when:** `run_requested_artifacts_dispatch` no longer reads `craft_task_keys`; it walks `run_next` from the entry key with per-hop `_persist_craft_dispatch_success`; each `do_task` call passes `suppress_run_next=True` so `do_task` does not auto-recurse; `run_candidate_artifact_generation` also passes `suppress_run_next=True` so UI one-shot generate stays single-hop after boot wires `run_next`; `python3 -m py_compile` succeeds on touched `.py` files.

1. In `src/core/agent.py`, where `planned_next` / `effective_next` is taken from `agent_task_row.get("run_next")` (~line 2706), if `(ctx or {}).get("suppress_run_next")` is truthy, force `effective_next = ""` (do not recurse). Leave all other run_next behavior unchanged.
2. In `src/core/candidate.py`, rewrite `run_requested_artifacts_dispatch` succession:
   - `craft_key = stage["craft_task_key"]` (singular).
   - Loop while `craft_key` is non-empty:
     - Refresh candidate from DB (same as today).
     - `await do_task(..., ctx={**candidate, "suppress_run_next": True}, ...)` (candidate dict as ctx today — merge the flag onto a shallow copy: `task_ctx = {**(candidate or {}), "suppress_run_next": True}`).
     - On success, `_persist_craft_dispatch_success(...)` as today.
     - `craft_key = _current_agent_task_run_next(craft_key)` (already imported / available via existing import of `_current_agent_task_run_next` in this module — if not imported at top, add `from src.core.agent import _current_agent_task_run_next` next to existing agent imports).
   - Cycle guard: if a `craft_key` repeats in the walk, raise `RuntimeError` with the cycle key (do not infinite-loop).
   - Empty `run_next` on the entry key → one hop only then graduate to `pass_state` (same as a single-item chain).
   - Failure / transition behavior unchanged (`_requested_stage_failure_target`).
3. In `run_candidate_artifact_generation`, when calling `do_task`, pass ctx as a shallow copy of `candidate` plus `"suppress_run_next": True` so Manage UI generate remains one craft per click after Stage 3 sets `run_next` links.
4. Do not change `run_requested_resume_dispatch` (already singular `craft_task_key`; leave `craft_resume_base.run_next` alone).

⚠️ **Decision:** Walk + suppress, not a single unsuppressed `do_task` entry. Craft hops must persist per hop via `_persist_craft_dispatch_success`; unsuppressed `do_task` recursion would skip mid-hop persist and would also make UI entry-hop generate fan through the whole chain.

## Stage 3: Boot SQL confirm/correct + admin JSON alignment

**Done when:** After `_ensure_agent_task_schema`, current `agent_task` rows for the seven craft keys have the expected `run_next` values (queryable); migration is idempotent; `data/admin/agent_task.json` matches the same topology; `python3 -m py_compile src/data/database.py` passes.

Expected chain (former `craft_task_keys` order → terminal empty):

| task_key | run_next |
|----------|----------|
| `craft_company_search_terms` | `craft_joblist_rubric` |
| `craft_joblist_rubric` | `craft_jobdesc_rubric` |
| `craft_jobdesc_rubric` | `craft_do_rubric` |
| `craft_do_rubric` | `craft_get_rubric` |
| `craft_get_rubric` | `craft_like_rubric` |
| `craft_like_rubric` | `craft_prefilter_rubric` |
| `craft_prefilter_rubric` | `` (empty string) |

1. In `src/data/database.py`, add `_apply_ast1113_craft_run_next_chain_migration(conn)` modeled on `_apply_ast834_clear_select_job_page_run_next_migration`:
   - For each `(task_key, expected_run_next)` pair above: `SELECT task_key_uuid, run_next FROM agent_task WHERE task_key = ? AND current = 1 LIMIT 1`.
   - If no row, skip that key (do not insert ghost rows — AST-1108 out of scope).
   - If `(row.run_next or "").strip() == expected_run_next.strip()`, skip.
   - Else `UPDATE agent_task SET run_next = ?, updated_at = CURRENT_TIMESTAMP WHERE task_key_uuid = ?` with the expected value (empty string for terminal).
   - `conn.commit()` once after the series (or after each update — match neighboring migrations’ commit style; AST-834 commits per successful clear).
   - Swallow `sqlite3.Error` on the initial select the same way AST-834 does (early return).
2. Call it from `_ensure_agent_task_schema` immediately after `_apply_ast834_clear_select_job_page_run_next_migration(conn)` (before rubric prompt migrations).
3. In `data/admin/agent_task.json`, set the same seven `run_next` values on the matching `task_key` objects so repo-wins JSON does not disagree with the migration’s intended topology (schema ensure still runs after admin JSON at bootstrap and re-confirms).
4. Do **not** change `craft_resume_base` or non-craft `run_next` rows. Do **not** edit Manage Tasks UI.

⚠️ **Decision:** Confirm/correct = set `run_next` to the expected successor whenever the current row differs (including clearing a wrong non-empty value). Missing current rows are skipped (no seed invent). Observable = after boot, those seven current rows show the table above.

## Execution contract

- Stages in order; one commit per stage on the epic worktree sub; publish to `origin/<publish-ref>` after each stage per build-child.
- No files outside the Files Changed table.
- Ambiguity or drift → stop and comment on **parent** AST-1109 with the Stage N blocked template.
- Leave hop_task_keys (AST-1112), JOB_ARTIFACT_ENTRY (AST-1111), statute/pattern files, AST-1108, and Betty’s test tree untouched.

## Self-Assessment

**Scope:** `Single-Component` — candidate-stage craft succession + `agent_task` boot migration; touches utils/core/data for one anomaly surface.

**Conf:** `high` — succession walk mirrors reading `_current_agent_task_run_next`; boot migration mirrors AST-834; entry-key config mirrors `requested_resume`; suppress flag is a one-line gate at the existing `planned_next` site.

**Risk:** `Medium` — wrong suppress placement would double-run hops or skip persist; wrong migration pairs would mis-order craft artifacts; UI generate without suppress would fan the whole chain after boot.

## Self-review vs ASTRAL_CODE_RULES

- **§2.6.0 / `astral.dispatch.run-next-is-chain-authority`:** Deletes config hop-order list; succession from live `run_next`; boot writes topology into `agent_task` only.
- **§1.4 / no-hardcoded-sets:** Expected chain pairs live in the migration (and matching admin JSON) as the one-time topology write — not a parallel membership frozenset consulted at dispatch time.
- **§1.1 / database-header-inventory:** Only `agent_task` (already inventoried).
- **§1.1 / in-scope-only:** No hop_task_keys, JOB_ARTIFACT_ENTRY, AST-1108, Manage Tasks UI.
- **§3.3 / layers:** `suppress_run_next` stays in agent; persist stays in candidate; SQL in data.
- **Betty test-tree ban:** Engineer does not edit `tests/` / bible.
- **No conflict requiring conf-!!-NONE.**

## Review

**Publish ref:** `origin/sub/AST-1109/AST-1113-anomaly-craft-task-keys-boot-run-next`
**Tip:** `978103de`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `56a9635d` | craft entry key only — drop craft_task_keys list |
| 2 | `b511d46b` | walk craft run_next with suppress_run_next |
| 3 | `978103de` | boot craft run_next chain + admin JSON |

### Radia — code-rubric.v1 (AST-1113)

`[code-rubric] revision=1` · tip reviewed `2e55bcd1` · **Overall: DISCUSS** (C4 stragglers only; deliverable conforms)

**What's solid**

- `craft_task_keys` gone under `src/`; singular `craft_task_key` entry only; walk via `_current_agent_task_run_next` + cycle guard.
- `suppress_run_next` keeps per-hop persist and UI single-hop generate.
- Boot migration + admin JSON match expected seven-hop craft topology; missing rows skipped (no AST-1108 invent).

**Discuss (C4 stragglers)** — Joan excluded; three-dot in-scope (scores `conforms`): `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`.

## Resolution

**Date:** 2026-07-31  
**Publish tip before resolve:** `9182b95c` (`docs(AST-1113): Radia review — findings`)

Radia overall **DISCUSS** — no fix-now product or plan-doc edits. Deliverable statutes all **conforms**.

| Finding | Disposition |
|---------|-------------|
| discuss (C4 stragglers: spikes-under-debug-dir, features-single-file-per-ticket, engineer-test-tree-ban) | Accepted as non-blocking; each scored **conforms** in Radia’s sweep; no product change. |

No product commits on this resolve pass.
