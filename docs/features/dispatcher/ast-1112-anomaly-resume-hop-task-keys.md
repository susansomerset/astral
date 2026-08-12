<!-- linear-archive: AST-1112 archived 2026-08-07 -->

## Linear archive (AST-1112)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1112/anomaly-resume-hop-task-keys-shadow-hard-coded-daisy-chain-in-configpy  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-1109 — Hard-coded daisy chain in config.py  
**Blocked by / blocks / related:** parent: AST-1109

### Description

## What this implements

End-to-end against AST-1110: retire `hop_task_keys` / `_RESUME_ARTIFACT_HOP_TASK_KEYS` as membership authority; succession from `run_next` on this surface.

## In scope

- [X] `astral.dispatch.run-next-is-chain-authority` — retire hop-list shadow; succession from `run_next`
- [X] `pattern.dispatch.run-next-chain-authority` (proposed; bind to statute) — membership/succession via `agent_task.run_next` helpers
- [X] `astral.standards.no-hardcoded-sets` — deleting the shadow list, not relocating it as config authority
- [X] `astral.standards.in-scope-only` — `config.py` + `agent.py` resume-hop surface only
- [X] `astral.standards.dry-and-focused-functions` — delete dead hop helpers; reuse `_parent_hop_task_key_for_child`
- [X] `astral.state.no-daisy-chain-in-run` / CODE_RULES §2.6.0 — keep claim/match helpers that already read `run_next`
- [X] `astral.docs.features-single-file-per-ticket` — plan at `docs/features/dispatcher/ast-1112-anomaly-resume-hop-task-keys.md`

## Considered but excluded

- [X] `JOB_ARTIFACT_ENTRY_TASK_KEYS` / `build_artifacts_chain_task_keys()` — AST-1111
- [X] Candidate-stage `craft_task_keys` + boot SQL confirm/correct — AST-1113
- [X] Authoring/amending statutes or CODE_RULES pointer — AST-1110 (already User Testing)
- [X] Approving `pattern.dispatch.run-next-chain-authority` catalog status — remains proposed
- [X] AST-1108 seed-data ghost cleanup — Foundation; related context only
- [X] Manage Tasks UI / `dispatch_tasks` uniqueness / AUTO/CLICK semantics — parent Boundaries
- [X] `tests/` / `docs/test-bible/**` — Betty; engineer does not patch test tree

## Acceptance criteria

- [X] 3. `BUILD_CONFIG.resume_artifact_chain.hop_task_keys` / `_RESUME_ARTIFACT_HOP_TASK_KEYS` are not authorities for chain membership; resume/artifact hop succession comes from `run_next`.
- [X] 4. This child’s product path does not consult the retired hard-coded list for chain membership; §2.6.0 claim/match helpers that already use `run_next` remain the path for hop-label eligibility.

## Boundaries

Does **not** own JOB_ARTIFACT_ENTRY or craft remediations. Does **not** author the statute file.

## Notes for planning

Vertical anomaly against the new statute.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-1109-hard-coded-daisy-chain-in-configpy`, child `sub/AST-1109/AST-1112-anomaly-resume-hop-task-keys`. Created at dispatch-parent.

### Comments

#### chuckles — 2026-07-31T19:53:50.906Z
[merge-child] blocked: git pull merge on sub — use: git fetch && git merge origin/ftr/<parent-segment>

validate-sub-log failed on `origin/sub/AST-1109/AST-1112-anomaly-resume-hop-task-keys`. Offending commits:
- `81ad0345` Merge remote-tracking branch 'origin/sub/AST-1109/AST-1112-anomaly-resume-hop-task-keys' into sub/…
- `f0656d75` Merge remote-tracking branch 'origin/ftr/AST-1109-hard-coded-daisy-chain-in-configpy' into sub/…

@Hedy Lamarr — rewrite/republish the sub tip so the child range has no `Merge remote-tracking branch` commits (merge `origin/ftr/AST-1109-hard-coded-daisy-chain-in-configpy` with a normal merge message if needed; no `git pull`). Keep vocabulary commits intact. Push to `origin/sub/AST-1109/AST-1112-anomaly-resume-hop-task-keys` only.

— Chuckles

#### radia — 2026-07-31T19:50:58.842Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1112
**Publish ref:** `origin/sub/AST-1109/AST-1112-anomaly-resume-hop-task-keys` tip `b9aee42f` (product tip `81ad0345` + docs review)
**Overall:** DISCUSS

Diff: `origin/dev...origin/sub/.../AST-1112-…` — layers `{core, utils, docs}`; change_types `{add, modify}`. AST-1112 Stages 1–2 retire resume hop-list authority in `config.py` + `agent.py`; Betty tests/bible; tip also carries AST-1110 statute + AST-1111 JOB_ARTIFACT delete via ftr merge.

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | conforms | no grade/confidence edits |
| astral.agent.do-task-delegation | scoped | conforms | do_task signature/delegation unchanged |
| astral.agent.grade-vector-validation | scoped | conforms | no grade-vector work |
| astral.batch.batch-id-first | scoped | conforms | no batch API changes |
| astral.batch.batch-id-format | scoped | conforms | no batch_id format changes |
| astral.batch.claim-process-release | scoped | conforms | claim/match helpers untouched |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | no agent_responses latest-ref changes |
| astral.config.config-source-of-truth | scoped | conforms | keeps first_task_key + TASK_CONFIG; removes hop-order shadow |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | untouched |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | no secrets/env edits |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths artifacts/spikes unmatched |
| astral.debug.spikes-under-debug-dir | scoped | conforms | feature plans, not spike notes |
| astral.dispatch.run-next-is-chain-authority | scoped | conforms | deletes hop-list shadow; succession via run_next parents |
| astral.dispatch.seed-auto-false | scoped | conforms | no seed AUTO path edits |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single AST-1112 plan under docs/features/dispatcher/ |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty tests/bible; engineer owns src + plan |
| astral.git.engineer-test-tree-ban | scoped | conforms | test-tree via Betty test/merge-tests |
| astral.layers.core-vs-external-bright-line | scoped | conforms | no external I/O moves |
| astral.layers.import-direction | scoped | conforms | drops deleted helper import; core↔utils only |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers/paths require scripts |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | no UI business-logic edits |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | no coat-check changes |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | no render_verdict rewrite |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | layers/paths require src/ui |
| astral.standards.data-raises-caller-logs | scoped | conforms | no data-layer logging path |
| astral.standards.database-header-inventory | scoped | not-applicable | layers/paths require src/data |
| astral.standards.debug-contract-gated | scoped | conforms | debug stays gated; dispatch-chain index kept; hop-tuple index removed |
| astral.standards.dry-and-focused-functions | scoped | conforms | deletes dead hop helpers; reuses `_parent_hop_task_key_for_child` |
| astral.standards.in-scope-only | scoped | conforms | 1112 stages = config+agent resume surface; craft untouched in stage SHAs |
| astral.standards.logging-via-utils | scoped | conforms | get_logger / debug helpers retained |
| astral.standards.no-cross-contamination | scoped | conforms | stays core/utils |
| astral.standards.no-hardcoded-sets | scoped | conforms | deletes shadow rather than relocating hop set |
| astral.standards.public-then-helpers | scoped | conforms | removes dead helpers; no scatter |
| astral.standards.utils-data-late-import-only | scoped | conforms | no utils→data import |
| astral.state.core-decides-transitions | scoped | conforms | no transition-decision rewrite |
| astral.state.job-prior-states-enforced | scoped | conforms | compound spreads removed; legacy hop matcher + BASE prior retained (plan Decision) |
| astral.state.no-daisy-chain-in-run | scoped | conforms | §2.6.0 claim/match kept; succession from run_next |
| astral.ui.frontend-file-placement | scoped | not-applicable | layers/paths require frontend |
| astral.ui.naming-conventions | scoped | not-applicable | layers/paths require src/ui |
| astral.ui.single-gunicorn-worker | scoped | conforms | gunicorn/worker untouched |
| orch.git.betty-merge-tests-one-sha | universal | conforms | merge-tests(AST-1112) one SHA |
| orch.git.commit-vocabulary | universal | conforms | docs/code/test/merge-tests/resolve vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | publish to origin/sub/AST-1109/AST-1112-… |
| orch.git.ftr-sub-topology | universal | conforms | matches parent Git table |
| orch.git.merge-on-checkout | universal | conforms | merge-on-checkout used; no illegal recipe |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | none in reviewed history |
| orch.git.no-dev-agent-branches | universal | conforms | sub publish-ref only |
| orch.git.one-epic-worktree-per-parent | universal | conforms | epic worktree astral-AST-1109 |
| orch.git.three-permanent-branches | universal | conforms | no permanent-branch invention |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Decisions documented (spreads, TASK_CONFIG markers, ambiguous parents) |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–2 match landed config+agent |
| orch.pipeline.project-scoped-queues | universal | conforms | single-child Dispatcher scope |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | no statute corpus edits in this child |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty owns test/bible revisions |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Hedy implementer through Tests Passed |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Radia docs-only; assignee left Hedy |
| orch.roles.pre-commit-path-bans | universal | conforms | engineer stages = config.py + agent.py |

Active-set count: **58**.

## Pattern conformance

- `pattern.dispatch.run-next-chain-authority` — **conforms** (cited; bind to statute; pattern remains proposed)

## Plan adherence

Stages 1–2 match tip: hop-list authority gone; parent via `_parent_hop_task_key_for_child`; debug hop-tuple path removed; dispatch-chain debug kept. Self-Assessment Single-Component / Conf high / Risk Medium match. Stage SHAs did not delete JOB_ARTIFACT/craft (siblings).

## Findings

### discuss (C4 stragglers)

Joan excluded; three-dot in-scope (scores `conforms` above):

1. `astral.debug.spikes-under-debug-dir`
2. `astral.docs.features-single-file-per-ticket`
3. `astral.git.engineer-test-tree-ban`

### advisory

Admin default trigger membership now uses `TASK_CONFIG.task_type == "CHAIN"` + `error_state == ERROR_BUILD_ARTIFACTS` (plan Decision; Joan non-blocking discuss). Not a hop-order list; statute “true config catalogs” carve-out. No fix-now.

§5a–§5g: imports cleaned; debug remains gated; no external/LLM path; no silent `except`.

### Notes

Plan-rubric verdict attached (Joan APPROVED). Zero `src/` hits for retired hop symbols; `py_compile` clean.

**What’s solid:** resume hop succession is run_next-parent only; compound prior spreads removed without a replacement hop catalog; sibling craft surface untouched in 1112 stage commits.

context_tokens≈50000

#### betty — 2026-07-31T19:46:18.162Z
[check-linear]

Cleared `[qa-handoff]`: `_block_text_by_type` mocks in `TestAst597MidChainResumeHydrationAndTransitions` (and the matching AST-769 patch) now accept `debug=`.

**Publish tip:** `origin/sub/AST-1109/AST-1112-anomaly-resume-hop-task-keys` @ `89e05394` (tests SHA `3749e341`; still one `merge-tests(AST-1112)` @ `3b91322a`).

Reassigned Hedy for `test-child`. Manifest unchanged — re-run the same narrowed command.

— Betty

#### hedy — 2026-07-31T19:43:03.137Z
[qa-handoff]

@Betty White

Manifest command failed 1/29 on publish tip `3b91322a`:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1112ResumeHopTaskKeysShadowDeleted \
  tests/component/utils/test_config.py::TestAst803FlatBuildArtifactsChainDispatch \
  tests/component/utils/test_config.py::TestAst848DispatchHopLabels \
  tests/component/utils/test_config.py::TestAst849DispatchChainClaimStates \
  tests/component/core/test_agent.py::TestAst597MidChainResumeHydrationAndTransitions \
  -q
```

**Failing node:** `tests/component/core/test_agent.py::TestAst597MidChainResumeHydrationAndTransitions::test_hop_agent_ref_for_parent_skips_failed_response_rows`

**Error:** `TypeError: ….<locals>.<lambda>() got an unexpected keyword argument 'debug'`

**Why test/manifest (not product):** Product `_hop_agent_ref_for_parent` calls `_block_text_by_type(blocks, "RESPONSE", debug=debug)` — matching the real helper signature (`debug: bool = False`). The test monkeypatch uses `lambda blocks, typ: "Validation failed: schema"` and rejects `debug=`. AST-1112 product path did not change `_block_text_by_type` / this call site; please accept `debug` / `**kwargs` on the mock (or otherwise align the patch with the helper).

28 other nodes in the class/suite path passed. Staying Tests Ready.

#### betty — 2026-07-31T19:41:47.498Z
## QA test manifest

**Publish:** `origin/sub/AST-1109/AST-1112-anomaly-resume-hop-task-keys` @ `3b91322a` (`merge-tests(AST-1112): origin/tests 597bb485fac856009e2c40626e6ee4fa73d1b935`)

1. `tests/component/utils/test_config.py::TestAst1112ResumeHopTaskKeysShadowDeleted` — hop-list / claim-helper symbols absent; `resume_artifact_chain` keeps `first_task_key` only; legacy compound membership via `TASK_CONFIG`.
2. `tests/component/utils/test_config.py::TestAst803FlatBuildArtifactsChainDispatch` — flat BUILD_ARTIFACTS + CHAIN trigger defaults still green without `resume_artifact_hop_task_keys`.
3. `tests/component/utils/test_config.py::TestAst848DispatchHopLabels`
4. `tests/component/utils/test_config.py::TestAst849DispatchChainClaimStates`
5. `tests/component/core/test_agent.py::TestAst597MidChainResumeHydrationAndTransitions` — parent via `_parent_hop_task_key_for_child` + run_next mocks; hydrate entry contexts; ambiguous parents → `None`.

**Broken / obsolete (revised this pass):** `_resume_artifact_parent_hop_key` tests; hop-list membership asserts.

**Out of this narrowed run:** `TestAst1111JobArtifactEntryShadowDeleted` (sibling product still on this sub tip until merge-child rolls AST-1111).

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1112ResumeHopTaskKeysShadowDeleted \
  tests/component/utils/test_config.py::TestAst803FlatBuildArtifactsChainDispatch \
  tests/component/utils/test_config.py::TestAst848DispatchHopLabels \
  tests/component/utils/test_config.py::TestAst849DispatchChainClaimStates \
  tests/component/core/test_agent.py::TestAst597MidChainResumeHydrationAndTransitions \
  -q
```

**Bible shasums on publish tip:**
- `docs/test-bible/utils/config.md` `9da263ef7f72c77b9c74ea0dc7aa47bc66db8353`
- `docs/test-bible/core/agent.md` `29b6eb6fae4dfb703876fcf6f13d64b0d08b43ce`

— Betty

#### joan — 2026-07-31T19:33:32.635Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1112
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 statute + CODE_RULES | N/A — boundary (AST-1110) |
| AC2 JOB_ARTIFACT_ENTRY_TASK_KEYS | N/A — boundary (AST-1111) |
| AC3 resume hop_task_keys not authority; succession from run_next | Stages 1–2 |
| AC4 craft_task_keys | N/A — boundary (AST-1113) |
| AC5 craft boot SQL | N/A — boundary (AST-1113) |
| AC6 product path does not consult retired list; §2.6.0 helpers remain | Stages 1–2 (claim/match untouched; hop-list deleted) |

### Child AC → plan stages

| Child AC | Plan coverage |
|----------|---------------|
| Parent AC3 (hop_task_keys retired; succession from run_next) | Stages 1–2 |
| Parent AC6 slice (no consult of retired list) | Stages 1–2 |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 config hop-list retirement | Functional scope anomaly resume hop-key lists; Purpose config-as-loophole |
| Stage 2 agent succession/debug without hop list | Same anomaly product path; keep §2.6.0 run_next helpers |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work |
| orch.git.commit-vocabulary | conforms | Stage commits on sub publish-ref |
| orch.git.flow-direction-inviolable | conforms | Publish only to origin/sub/… |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | No illegal merge recipe |
| orch.git.no-cherry-pick-rebase-force | conforms | None proposed |
| orch.git.no-dev-agent-branches | conforms | sub/AST-1109/AST-1112-… only |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree astral-AST-1109 |
| orch.git.three-permanent-branches | conforms | No permanent-branch invention |
| orch.pipeline.call-susan-for-product-decisions | conforms | Decisions documented (compound spreads; TASK_CONFIG markers; ambiguous parents) |
| orch.pipeline.plan-is-bible | conforms | Binding stages + Files Changed present |
| orch.pipeline.project-scoped-queues | conforms | Single-child scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate-plan only |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | Engineer forbidden from tests/bible |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Hedy) build path |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer implementer after Plan Approved |
| orch.roles.pre-commit-path-bans | conforms | Only named config/agent files |
| astral.dispatch.run-next-is-chain-authority | conforms | Deletes hop-list shadow; succession via run_next helpers; no replacement hop-order list |
| astral.standards.no-hardcoded-sets | conforms | Deletes shadow rather than relocating membership set |
| astral.standards.in-scope-only | conforms | Resume hop surface only; JOB_ARTIFACT/craft/statute out |
| astral.standards.dry-and-focused-functions | conforms | Deletes dead hop helpers; reuses `_parent_hop_task_key_for_child` |
| astral.state.no-daisy-chain-in-run | conforms | Keeps §2.6.0 claim/match; succession from run_next |
| astral.config.config-source-of-truth | conforms | Keeps first_task_key + TASK_CONFIG specs; removes DB-topology shadow |
| astral.layers.import-direction | conforms | Core↔utils only; drops deleted helper import |
| astral.standards.debug-contract-gated | conforms | Debug remains gated; dispatch-chain debug path kept; hop-tuple index removed |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src edits |
| astral.agent.confidence-bounds | conforms | No grade/confidence changes |
| astral.agent.do-task-delegation | conforms | No do_task signature/delegation rewrite |
| astral.agent.grade-vector-validation | conforms | No grade-vector work |
| astral.batch.batch-id-first | conforms | No batch API changes |
| astral.batch.batch-id-format | conforms | No batch_id format changes |
| astral.batch.claim-process-release | conforms | Claim/match helpers untouched |
| astral.batch.entity-agent-responses-latest-only | conforms | No agent_responses/latest-ref changes |
| astral.config.pass-threshold-vs-score-floor | conforms | No score_floor/pass_threshold edits |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env edits |
| astral.dispatch.seed-auto-false | conforms | No seed AUTO paths |
| astral.layers.core-vs-external-bright-line | conforms | No external I/O moves |
| astral.layers.ui-config-driven-business-logic | conforms | No UI work |
| astral.patterns.coat-check-never-store-empty | conforms | No coat-check changes |
| astral.patterns.render-verdict-orchestrates-consult | conforms | No render_verdict rewrite |
| astral.standards.data-raises-caller-logs | conforms | No data-layer logging path |
| astral.standards.logging-via-utils | conforms | Existing logging helpers retained |
| astral.standards.no-cross-contamination | conforms | Stays in core/utils |
| astral.standards.public-then-helpers | conforms | Deletes dead helpers; no scatter |
| astral.standards.utils-data-late-import-only | conforms | No utils→data import |
| astral.state.core-decides-transitions | conforms | No transition-decision rewrite |
| astral.state.job-prior-states-enforced | conforms | Relies on existing prior_states + legacy hop matcher; no prior_states invent |
| astral.ui.single-gunicorn-worker | conforms | No gunicorn/worker edits |

## Considered and excluded

**Considered:** all rows in Statute verdicts table above (49).

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths match none
- astral.debug.spikes-under-debug-dir — paths match none
- astral.docs.features-single-file-per-ticket — layers {docs} ∩ plan empty
- astral.git.engineer-test-tree-ban — paths match none
- astral.layers.scripts-exempt-from-layer-rules — layers ∩ plan empty
- astral.patterns.require-auth-on-protected-endpoints — layers ∩ plan empty
- astral.standards.database-header-inventory — layers ∩ plan empty
- astral.ui.frontend-file-placement — layers ∩ plan empty
- astral.ui.naming-conventions — layers ∩ plan empty

**Notes:** Plan layers `{core,utils}`; change_types `{delete,modify}` from Delete/Remove + rewrite wording. Tip survey confirms hop-list consumers only in the two Files Changed paths.

## Findings

None fix-now.

**discuss (non-blocking):** Stage 1 §7 replaces hop-list membership for admin default trigger with `TASK_CONFIG.task_type == "CHAIN"` + `error_state == ERROR_BUILD_ARTIFACTS`. That is orchestration metadata already on the hops, not a hop-order list — acceptable under the statute’s “true config catalogs” carve-out; if Archie later wants even that derived only from `run_next`, follow-up — not required to meet parent AC3/AC6.

**acceptable:** Self-assessment Single-Component / Conf high / Risk Medium honest; Medium risk (parent resolution) mitigated by linear run_next Decision + drop config tie-break. Compound-state spread deletion relies on existing `legacy_build_artifacts_hop` prior matching — documented. Betty owns test-tree fallout.

**R6:** Definition fidelity pass. Layer/import pass. No new shadow frozenset. File placement N/A (edits existing). DRY pass. No sibling scope creep.

context_tokens≈45000

— Joan

#### hedy — 2026-07-31T19:31:03.657Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-1109/AST-1112-anomaly-resume-hop-task-keys/docs/features/dispatcher/ast-1112-anomaly-resume-hop-task-keys.md

**Scope:** Single-Component — `config.py` hop-list retirement + `agent.py` succession/debug call sites on the resume-artifact surface only.

**Conf:** high — statute already active; all product `resume_artifact_hop_task_keys` consumers are in those two files; §2.6.0 claim/match already uses `run_next`.

**Risk:** Medium — wrong parent resolution would break mid-chain caller-token hydration on BUILD_ARTIFACTS hops; linear `run_next` topology limits blast radius.

#### chuckles — 2026-07-31T19:24:14.927Z
[thread-missing] Hedy Team thread store.db absent on this host (old=947ba72b-c69b-41f2-ab11-163229f18a85). Reminted → `/home/susan/.cursor/chats/117f212c4fcaac22ac7085f5eb813d1b/61685e83-fe75-482d-b70b-9dac2d2603fe/store.db` (UUID `61685e83-fe75-482d-b70b-9dac2d2603fe`). Parent ## Team updated via populate-team.

— Chuckles

---

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

## Review

**Publish ref:** `origin/sub/AST-1109/AST-1112-anomaly-resume-hop-task-keys`
**Tip:** `e0939f15`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `e457b343` | retire resume hop_task_keys config authority |
| 2 | `e0939f15` | resume hop succession via run_next parents |

### Radia — code-rubric.v1 (AST-1112)

`[code-rubric] revision=1` · tip reviewed `81ad0345` · **Overall: DISCUSS** (C4 stragglers only; deliverable conforms)

**What's solid**

- Hop-list authority retired: `_RESUME_ARTIFACT_HOP_TASK_KEYS`, `hop_task_keys`, `resume_artifact_hop_task_keys()` gone; zero `src/` hits.
- Succession via `_parent_hop_task_key_for_child` / run_next; ambiguous-parent config tie-break removed.
- Debug: hop-tuple Style D index removed; dispatch-trigger debug path retained.
- Stage commits scoped to config.py + agent.py; JOB_ARTIFACT/craft left to siblings (tip also carries AST-1111 via ftr merge).

**Discuss (C4 stragglers)** — Joan excluded; three-dot brings in-scope (scores `conforms`): `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`.

## Resolution

**Date:** 2026-07-31  
**Publish tip before resolve:** `b9aee42f` (`docs(AST-1112): Radia review — findings`)

Radia overall **DISCUSS** — no fix-now product or plan-doc edits. Deliverable statutes all **conforms**.

| Finding | Disposition |
|---------|-------------|
| discuss (C4 stragglers: spikes-under-debug-dir, features-single-file-per-ticket, engineer-test-tree-ban) | Accepted as non-blocking; each scored **conforms** in Radia’s sweep; no product change. |
| advisory (TASK_CONFIG CHAIN + ERROR_BUILD_ARTIFACTS for admin default trigger) | Accepted as plan Decision / Joan non-blocking discuss; no change. |

No product commits on this resolve pass.

