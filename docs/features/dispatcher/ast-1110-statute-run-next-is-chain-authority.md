<!-- linear-archive: AST-1110 archived 2026-08-07 -->

## Linear archive (AST-1110)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1110/statute-run-next-is-chain-authority-hard-coded-daisy-chain-in-configpy  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1109 — Hard-coded daisy chain in config.py  
**Blocked by / blocks / related:** parent: AST-1109; blocks: AST-1113; blocks: AST-1112; blocks: AST-1111

### Description

## What this implements

Land Archie-approved statute(s) + CODE_RULES pointer + catalog note for proposed `pattern.dispatch.run-next-chain-authority` / `astral.dispatch.run-next-is-chain-authority`. No product routing changes in this child. Blocks all anomaly remediations.

## In scope

- [X] `orch.roles.archie-approves-statutes` — statute lands only with Archie approval frontmatter
- [X] `astral.dispatch.run-next-is-chain-authority` — new statute (this child’s deliverable)
- [X] `astral.config.config-source-of-truth` — clarify config must not duplicate DB `run_next` topology
- [X] `astral.standards.no-hardcoded-sets` — config shadow of `run_next` is not a conforming escape
- [X] `astral.state.no-daisy-chain-in-run` — complements carve-out; membership must match `run_next` data
- [X] `astral.docs.features-single-file-per-ticket` — plan at `docs/features/dispatcher/ast-1110-statute-run-next-is-chain-authority.md`
- [X] `astral.standards.in-scope-only` — statute/pattern/CODE_RULES pointer only; no anomaly remediations

## Considered but excluded

- [X] `astral.standards.database-header-inventory` — boot SQL confirm/correct is AST-1113 only
- [X] Product consult/dispatcher/craft routing — siblings AST-1111–AST-1113
- [X] Deleting `JOB_ARTIFACT_ENTRY_TASK_KEYS` / hop_task_keys / craft_task_keys — siblings 2–4
- [X] AST-1108 seed-data ghost cleanup — Foundation; related context only
- [X] Approving `pattern.dispatch.run-next-chain-authority` — lands **proposed**; Archie approve later before implementation depends on catalog id
- [X] Amending bodies of `astral.state.no-daisy-chain-in-run` or `astral.standards.no-hardcoded-sets` — new statute is the boundary clarification

## Acceptance criteria

1. [x] New Archie-approved statute under `canon/statutes/` bans config shadow of DB-owned `run_next` topology; CODE_RULES points at it — lands before anomaly remediations claim conformance.
2. [x] Proposed catalog entry `pattern.dispatch.run-next-chain-authority` exists under `canon/patterns/` (`status: proposed`).
3. [x] Statute registered in `canon/statutes/README.md` + `HARVEST.md` (active count includes this create).

## Boundaries

Does **not** change consult/dispatcher/craft routing. Does **not** delete config frozensets (siblings 2–4). Does **not** own AST-1108 seed cleanup.

## Notes for planning

Statute-first vertical decomposition — this child is the law gate for siblings.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-1109-hard-coded-daisy-chain-in-configpy`, child `sub/AST-1109/AST-1110-statute-run-next-is-chain-authority`. Created at dispatch-parent.

### Comments

#### radia — 2026-07-31T19:20:31.896Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1110
**Publish ref:** `origin/sub/AST-1109/AST-1110-statute-run-next-is-chain-authority` tip `fc651c68` (reviewed product tip `27130c72` + docs review append)
**Overall:** DISCUSS

Diff: `origin/dev...origin/sub/AST-1109/AST-1110-statute-run-next-is-chain-authority` — layers `{docs}`; change_types `{add, modify}`; 9 paths (canon statute/pattern + registers, CODE_RULES §2.6.0, plan, test-bible README). No `src/**`.

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | layers/paths require core/utils src |
| astral.agent.do-task-delegation | scoped | not-applicable | layers/paths require src/core |
| astral.agent.grade-vector-validation | scoped | not-applicable | layers/paths require src/core |
| astral.batch.batch-id-first | scoped | not-applicable | layers/paths require data/core src |
| astral.batch.batch-id-format | scoped | not-applicable | layers/paths require core/data src |
| astral.batch.claim-process-release | scoped | not-applicable | layers/paths require core/data src |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | layers/paths require core/data src |
| astral.config.config-source-of-truth | scoped | not-applicable | layers/paths require src/** |
| astral.config.pass-threshold-vs-score-floor | scoped | not-applicable | layers/paths require core/data/utils src |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | layers/paths require src/scripts |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths artifacts/** / scripts/spikes/** unmatched |
| astral.debug.spikes-under-debug-dir | scoped | conforms | plan under docs/features is feature plan, not spike notes |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | new statute’s applies_when is core/utils src; this diff is docs/canon only |
| astral.dispatch.seed-auto-false | scoped | not-applicable | layers/paths require dispatcher/config src |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single plan at docs/features/dispatcher/ast-1110-….md |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty commits touch test-bible/merge-tests only; features by engineer docs |
| astral.git.engineer-test-tree-ban | scoped | conforms | AST-1110 test-bible edit is Betty docs(); no engineer test-tree |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | layers/paths require core/external src |
| astral.layers.import-direction | scoped | not-applicable | layers/paths require src/** |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers/paths require scripts |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | layers/paths require ui/config src |
| astral.patterns.coat-check-never-store-empty | scoped | not-applicable | layers/paths require src/core |
| astral.patterns.render-verdict-orchestrates-consult | scoped | not-applicable | layers/paths require src/core |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | layers/paths require src/ui |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | layers/paths require src/** |
| astral.standards.database-header-inventory | scoped | not-applicable | layers/paths require src/data |
| astral.standards.debug-contract-gated | scoped | not-applicable | layers/paths require src/** |
| astral.standards.dry-and-focused-functions | scoped | not-applicable | layers/paths require src/scripts |
| astral.standards.in-scope-only | scoped | not-applicable | layers/paths require src/** |
| astral.standards.logging-via-utils | scoped | not-applicable | layers/paths require src/** |
| astral.standards.no-cross-contamination | scoped | not-applicable | layers/paths require src/** |
| astral.standards.no-hardcoded-sets | scoped | not-applicable | layers/paths require src/** |
| astral.standards.public-then-helpers | scoped | not-applicable | layers/paths require src/** |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | layers/paths require src/utils |
| astral.state.core-decides-transitions | scoped | not-applicable | layers/paths require core/data src |
| astral.state.job-prior-states-enforced | scoped | not-applicable | layers/paths require core/data/config src |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | layers/paths require src/core |
| astral.ui.frontend-file-placement | scoped | not-applicable | layers/paths require frontend |
| astral.ui.naming-conventions | scoped | not-applicable | layers/paths require src/ui |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | layers/paths require ui/scripts/config |
| orch.git.betty-merge-tests-one-sha | universal | conforms | merge-tests(AST-1110) one SHA from origin/tests |
| orch.git.commit-vocabulary | universal | conforms | docs/code/test/merge-tests vocabulary on sub tip |
| orch.git.flow-direction-inviolable | universal | conforms | publish to origin/sub/AST-1109/AST-1110-… only |
| orch.git.ftr-sub-topology | universal | conforms | matches parent Git table sub under ftr/AST-1109 |
| orch.git.merge-on-checkout | universal | conforms | no illegal merge recipe in diff |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | none in history reviewed |
| orch.git.no-dev-agent-branches | universal | conforms | sub/AST-1109/AST-1110-… publish-ref |
| orch.git.one-epic-worktree-per-parent | universal | conforms | epic worktree astral-AST-1109 |
| orch.git.three-permanent-branches | universal | conforms | no permanent-branch invention |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | pattern stays proposed; statute id from parent Arch definition |
| orch.pipeline.plan-is-bible | universal | conforms | stages + Files Changed match landed canon/docs |
| orch.pipeline.project-scoped-queues | universal | conforms | single-child Dispatcher scope |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | statute `approved_by: Archie` / `approved_at: 2026-07-31`; pattern proposed |
| orch.roles.betty-owns-test-tree | universal | conforms | bible + merge-tests by Betty path; engineer no tests/** |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | implementer path through Tests Passed |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | no Radia product edits; docs() review only |
| orch.roles.pre-commit-path-bans | universal | conforms | canon/docs only; no banned product paths |

Active-set count: **58** (matches HARVEST/README).

## Pattern conformance

- `pattern.dispatch.run-next-chain-authority` — **conforms** (cited deliverable; lands `status: proposed`, not approved)
- No other pattern ids cited for implementation dependency

## Plan adherence

Stages 1–3 match tip: Archie-approved statute + register (58), proposed pattern + register, CODE_RULES §2.6.0 pointer. Self-Assessment Scope `Single-Component` matches docs/canon-only footprint. No AST-1111–1113 deletes / boot SQL / `src/**`. Betty bible note is expected Tests Passed path outside engineer Files Changed.

## Findings

### discuss (C4 stragglers)

Joan plan-rubric Excluded list vs this sweep in-scope (statute scores themselves `conforms` above):

1. `astral.debug.spikes-under-debug-dir` — excluded at plan time; `docs/features/**` in diff
2. `astral.docs.features-single-file-per-ticket` — excluded at plan time; plan file in diff
3. `astral.git.betty-no-src-or-features` — excluded at plan time; `docs/features/**` in diff
4. `astral.git.engineer-test-tree-ban` — excluded at plan time; `docs/test-bible/**` in diff

No fix-now. No product/layer/import/debug/external issues (§5a–§5g N/A — no `src/**`).

### Notes

Plan-rubric verdict attached (Joan APPROVED). Stragglers are plan Files Changed vs landed plan+bible path mismatch, not deliverable defects.

**What’s solid:** statute/pattern SCHEMA paths, Archie frontmatter, proposed-only pattern, CODE_RULES pointer, register counts 58, sibling boundaries held.

context_tokens≈52000

#### chuckles — 2026-07-31T19:17:54.901Z
[thread-missing] Radia Team store.db missing on host; minted 66e94f9d-7cc5-4173-ad21-68135118514f for review-child first-spawn.

— Chuckles

#### betty — 2026-07-31T19:16:11.955Z
## QA test manifest

**Publish:** `origin/sub/AST-1109/AST-1110-statute-run-next-is-chain-authority` @ `f16f1ea5` (`merge-tests(AST-1110): origin/tests f0f5671da65a0a25e61e5eb8615005d48b56cade`)

**Classification:** docs-only statute/pattern/CODE_RULES — no `src/**`; no pytest; no integration-scenario drift.

1. **docs-acceptance — statute** — On publish tip, `canon/statutes/astral/dispatch/astral.dispatch.run-next-is-chain-authority.md` exists with `status: active`, `approved_by: Archie`, `approved_at: "2026-07-31"`, id `astral.dispatch.run-next-is-chain-authority`.
2. **docs-acceptance — register** — `canon/statutes/README.md` lists the statute; active count text is **58**. `canon/statutes/HARVEST.md` has create (AST-1110) crosswalk row and **58 total active mappings**.
3. **docs-acceptance — pattern** — `canon/patterns/dispatch/pattern.dispatch.run-next-chain-authority.md` has `status: proposed` (not approved); patterns README + HARVEST list it as proposed.
4. **docs-acceptance — CODE_RULES** — `docs/ASTRAL_CODE_RULES.md` §2.6.0 has `**Statute:** \`astral.dispatch.run-next-is-chain-authority\`` and the clarifying sentence that config must not restate `run_next` hop membership/order.
5. **No pytest** — zero-arg harness / branch-lock gate not required. Commit `test(AST-1110): docs-acceptance …` when green (no src fixes).

**Broken / obsolete tests:** none (no product surface).

**Bible (this pass):** `docs/test-bible/README.md` shasum `1b5f9785ac9eec97d26746331a433ca556d96642`

— Betty

#### chuckles — 2026-07-31T19:13:10.917Z
[thread-missing] Betty Team store.db missing on host; minted 89442dba-5528-46e5-bb16-0c445b61f5b2 for qa-child first-spawn.

— Chuckles

#### joan — 2026-07-31T19:08:16.694Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1110
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 Archie-approved statute + CODE_RULES pointer before remediations | Stages 1 + 3 |
| AC2 JOB_ARTIFACT_ENTRY_TASK_KEYS gone | N/A — boundary (AST-1111) |
| AC3 resume hop_task_keys not authority | N/A — boundary (AST-1112) |
| AC4 craft_task_keys not authority | N/A — boundary (AST-1113) |
| AC5 craft boot SQL confirm/correct | N/A — boundary (AST-1113) |
| AC6 product paths stop consulting retired lists | N/A — boundary (siblings 2–4) |

### Child AC → plan stages

| Child AC | Plan coverage |
|----------|---------------|
| 1. New Archie-approved statute + CODE_RULES pointer | Stages 1 + 3 |
| 2. Proposed pattern.dispatch.run-next-chain-authority | Stage 2 |
| 3. Register in README + HARVEST (active count includes create) | Stage 1 §§3–4 |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 statute + register | Purpose/Functional scope “Statute first”; Architectural proposed statute id; child AC1/AC3 |
| Stage 2 proposed pattern | Architectural “New patterns proposed”; child AC2; AUTHORING propose lifecycle |
| Stage 3 CODE_RULES §2.6.0 pointer | Parent AC1 CODE_RULES pointer; complements no-daisy-chain carve-out |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work |
| orch.git.commit-vocabulary | conforms | Stage commits on sub publish-ref |
| orch.git.flow-direction-inviolable | conforms | Publish only to origin/sub/… |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | No illegal merge recipe |
| orch.git.no-cherry-pick-rebase-force | conforms | None proposed |
| orch.git.no-dev-agent-branches | conforms | sub/AST-1109/AST-1110-… only |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree astral-AST-1109 |
| orch.git.three-permanent-branches | conforms | No permanent-branch invention |
| orch.pipeline.call-susan-for-product-decisions | conforms | Pattern stays proposed pending Archie; statute body from parent-named id |
| orch.pipeline.plan-is-bible | conforms | Binding stages + Files Changed present |
| orch.pipeline.project-scoped-queues | conforms | Single-child scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate-plan only |
| orch.roles.archie-approves-statutes | conforms | Lands `approved_by: Archie` / `approved_at`; mirrors AST-1098 Notes (id approved on parent definition); pattern stays proposed |
| orch.roles.betty-owns-test-tree | conforms | No tests/ edits |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Katherine) build path |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer implementer after Plan Approved |
| orch.roles.pre-commit-path-bans | conforms | Canon/docs only; no banned product paths |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans

**Excluded:** (layers ∩ plan {docs} empty, or paths match none of Files Changed)
- astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation
- astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only
- astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ
- astral.debug.no-repo-root-artifacts-dir — paths match none
- astral.debug.spikes-under-debug-dir — paths match none
- astral.dispatch.seed-auto-false — layers ∩ {docs} empty
- astral.docs.features-single-file-per-ticket — paths docs/features/** match none of Files Changed
- astral.git.betty-no-src-or-features, astral.git.engineer-test-tree-ban — paths match none
- astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.scripts-exempt-from-layer-rules, astral.layers.ui-config-driven-business-logic
- astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.patterns.require-auth-on-protected-endpoints
- astral.standards.data-raises-caller-logs, astral.standards.database-header-inventory, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only
- astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run
- astral.ui.frontend-file-placement, astral.ui.naming-conventions, astral.ui.single-gunicorn-worker

**Notes:** Files Changed Layer cells `docs/canon` / `docs` → plan layer `docs` (rubric map). Corpus active count tip=57; Stage 1 bumps to 58.

## Findings

None fix-now.

**acceptable:** Self-assessment Single-Component / Conf high / Risk Medium is honest; Medium risk (wording / pattern approve / register miss) is mitigated by verbatim Statement + proposed-only pattern + explicit README/HARVEST steps. Statute Statement preserves true config catalogs; violating examples name exactly the three tip shadows. Pattern AUTHORING respected (`proposed`, remediations bind statute first). No `src/**`; siblings own deletes/boot SQL.

**R6:** Definition fidelity pass for statute-first child. No layer/import product violations. No config product edits. File placement under canon SCHEMA paths. DRY via AST-1098 precedent. No sibling scope creep.

context_tokens≈48000

— Joan

#### katherine — 2026-07-31T19:04:54.396Z
Plan published on `origin/sub/AST-1109/AST-1110-statute-run-next-is-chain-authority` @ `252241ef`.

[Plan doc](https://github.com/susansomerset/astral/blob/sub/AST-1109/AST-1110-statute-run-next-is-chain-authority/docs/features/dispatcher/ast-1110-statute-run-next-is-chain-authority.md)

**Scope:** Single-Component — one new statute + register, one proposed pattern + register, CODE_RULES §2.6.0 pointer; no `src/**`.

**Conf:** high — mirrors AST-1098 statute landing + patterns propose lifecycle; parent already named both ids; violating examples are the three tip shadows.

**Risk:** Medium — wrong statute wording could mis-bind sibling remediations or over-ban legitimate config catalogs; approving the pattern here would violate AUTHORING; missing README/HARVEST register leaves corpus incomplete.

#### chuckles — 2026-07-31T19:01:39.347Z
[thread-orphan] Joan session da0027e7-276d-4fe2-a6e6-65c8eb77e24d relocated from /home/susan/.cursor/chats/0f41bf986cfef9e06ea903e586d6d4d9/… → epic hash 117f212c4fcaac22ac7085f5eb813d1b. Same UUID retained for --resume.

— Chuckles

#### chuckles — 2026-07-31T19:01:21.122Z
[thread-missing] Katherine Team store.db was nowhere on this host for the prior UUID; minted new session a7e3dff5-71ee-497b-9943-14de068278ea and persisted via populate-team. Continuing pipeline with first-spawn.

— Chuckles

---

# Statute — run_next is chain authority

**Linear:** [AST-1110](https://linear.app/astralcareermatch/issue/AST-1110/statute-run-next-is-chain-authority-hard-coded-daisy-chain-in-configpy)  
**Parent:** [AST-1109](https://linear.app/astralcareermatch/issue/AST-1109/hard-coded-daisy-chain-in-configpy) — Hard-coded daisy chain in config.py  
**Publish ref:** `sub/AST-1109/AST-1110-statute-run-next-is-chain-authority`

Land Archie-approved statute `astral.dispatch.run-next-is-chain-authority` (config must not shadow DB-owned `agent_task.run_next` chain membership / hop succession), register it in the statute corpus, point CODE_RULES at it, and add a **proposed** catalog entry `pattern.dispatch.run-next-chain-authority` for sibling remediations. No product routing, config frozenset deletes, or boot SQL in this child — those are AST-1111 / AST-1112 / AST-1113.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `canon/statutes/astral/dispatch/astral.dispatch.run-next-is-chain-authority.md` | New active scoped statute (SCHEMA + AUTHORING) | docs/canon |
| `canon/statutes/README.md` | Add harvested-corpus row; bump active count 57→58 | docs/canon |
| `canon/statutes/HARVEST.md` | Add crosswalk row; bump Counts | docs/canon |
| `canon/patterns/dispatch/pattern.dispatch.run-next-chain-authority.md` | New **proposed** pattern (SCHEMA + AUTHORING) | docs/canon |
| `canon/patterns/README.md` | Add harvested-corpus row; note proposed status | docs/canon |
| `canon/patterns/HARVEST.md` | Add crosswalk row for the proposed pattern | docs/canon |
| `docs/ASTRAL_CODE_RULES.md` | Pointer to new statute at §2.6.0 (+ one clarifying sentence) | docs |

## Stage 1: Canon statute `astral.dispatch.run-next-is-chain-authority`

**Done when:** Active statute file exists at the SCHEMA path; README harvested table + HARVEST crosswalk list it; id is `astral.dispatch.run-next-is-chain-authority`; active corpus count text is **58**.

1. Create `canon/statutes/astral/dispatch/astral.dispatch.run-next-is-chain-authority.md` with YAML frontmatter (all SCHEMA keys, no extras):

```yaml
---
id: astral.dispatch.run-next-is-chain-authority
title: run_next is dispatch chain authority
tier: scoped
checkable: judgment
status: active
applies_when:
  layers: ["core", "utils"]
  paths: ["src/core/**", "src/utils/config.py"]
  change_types: ["add", "modify"]
source_docs:
  - docs/features/dispatcher/ast-1110-statute-run-next-is-chain-authority.md
  - docs/ASTRAL_CODE_RULES.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-31"
---
```

2. Body sections in SCHEMA order (use this text verbatim):

   - `# Statement` — When `agent_task.run_next` already encodes a dispatch multi-hop chain, config must not define a parallel allowed-key set, hop-order list, or membership frozenset that restates that chain’s membership or succession. Chain membership and hop succession for those flows come from current `agent_task.run_next` rows (and helpers that read them). Config may still name graduation maps, trigger registries, task specs, and other true config-owned catalogs that do **not** duplicate `run_next` topology. Putting such a shadow list in `config.py` does **not** satisfy `astral.standards.no-hardcoded-sets`.

   - `## Rationale` — Config frozensets that copy `run_next` look statute-compliant while drifting from the live database topology and inventing carve-outs (e.g. excluding a hop from a membership set). The documented §2.6.0 carve-out already uses `run_next`; shadow lists create a second authority and hide that drift.

   - `## Examples` / `### Conforming` —
     - Hop-label claim/graduation helpers that derive parent/child eligibility from `agent_task.run_next` (e.g. `_agent_task_parents_with_run_next`, `_current_agent_task_run_next`) without consulting a config hop-membership frozenset.
     - Config that owns `DISPATCH_CHAIN_TERMINAL_GRADUATION` / trigger→registry maps without listing every hop task key as chain membership.

   - `### Violating` —
     - `JOB_ARTIFACT_ENTRY_TASK_KEYS` (or any wrapper) used as authority for which consult hops are “in” the job-artifact chain while `run_next` already encodes those hops.
     - `BUILD_CONFIG.resume_artifact_chain.hop_task_keys` / `_RESUME_ARTIFACT_HOP_TASK_KEYS` used as authority for resume/artifact hop succession instead of `run_next`.
     - `CANDIDATE_STAGE_DISPATCH[…]["craft_task_keys"]` used as authority for craft daisy-chain succession instead of `run_next`.

   - Optional `## Notes` — Does not delete the named shadows (AST-1111–AST-1113). Does not change Manage Tasks UI, `dispatch_tasks` uniqueness, or AUTO/CLICK semantics. Complements `astral.state.no-daisy-chain-in-run` (carve-out exists) by requiring the carve-out’s **data** be the membership authority. Archie approved working id on parent AST-1109 Architectural definition (2026-07-31); statute body lands with this child.

3. In `canon/statutes/README.md`, add a harvested-corpus table row for `astral.dispatch.run-next-is-chain-authority` immediately after the existing `astral.dispatch.seed-auto-false` row (same table columns/style), path `` `astral/dispatch/astral.dispatch.run-next-is-chain-authority.md` ``. Bump the active-statute count text from **57** to **58**.

4. In `canon/statutes/HARVEST.md`, add one crosswalk row after the `astral.dispatch.seed-auto-false` create row:

   `| create (AST-1110) | \`astral.dispatch.run-next-is-chain-authority\` | scoped | judgment | AST-1109 / AST-1110 | \`astral/dispatch/astral.dispatch.run-next-is-chain-authority.md\` |`

   Update the **Counts** line so the AST-1110 create is included and the total active mappings read **58** (e.g. keep prior create tallies and add `; 1 created by AST-1110; 58 total active mappings in this register`).

⚠️ **Decision:** Domain folder remains `dispatch` (already created by AST-1098). `approved_by: Archie` / `approved_at: 2026-07-31` per parent Architectural definition naming this working id + AUTHORING lifecycle (same pattern as AST-1098 / `astral.dispatch.seed-auto-false`). Do **not** invent a second statute id; do **not** amend `astral.state.no-daisy-chain-in-run` or `astral.standards.no-hardcoded-sets` bodies in this child — the new statute is the boundary clarification.

## Stage 2: Proposed pattern `pattern.dispatch.run-next-chain-authority`

**Done when:** Pattern file exists at SCHEMA path with `status: proposed`; patterns README + HARVEST list it; no `approved` claim.

1. Create directory `canon/patterns/dispatch/` if missing.
2. Create `canon/patterns/dispatch/pattern.dispatch.run-next-chain-authority.md` with YAML frontmatter (all SCHEMA keys, no extras):

```yaml
---
id: pattern.dispatch.run-next-chain-authority
name: run_next as dispatch chain authority
status: proposed
proposed_in: AST-1109
approved_by: null
approved_at: null
canonical_refs:
  - path: src/core/agent.py
    symbol: _current_agent_task_run_next
  - path: src/utils/config.py
    symbol: _agent_task_parents_with_run_next
  - path: docs/ASTRAL_CODE_RULES.md
    symbol: "§2.6.0"
related_statutes:
  - astral.dispatch.run-next-is-chain-authority
  - astral.state.no-daisy-chain-in-run
  - astral.config.config-source-of-truth
  - astral.standards.no-hardcoded-sets
supersedes: null
superseded_by: null
---
```

3. Body sections in SCHEMA order (use this text verbatim):

   - `# Problem` — Dispatch multi-hop membership and succession get restated as config frozensets / hop-order lists that drift from live `agent_task.run_next` rows and invent carve-outs.

   - `# Solution shape` — Treat current `agent_task.run_next` as the authority for chain membership and hop succession on job/candidate dispatch chains that already use the §2.6.0 carve-out. Read succession via existing helpers (`_current_agent_task_run_next`, `_agent_task_parents_with_run_next`, and claim/graduation helpers that already follow `run_next`). Config may own graduation maps and trigger registries; it must not restate hop sets. Point at `canonical_refs` — do not paste large code into this catalog entry. Sibling anomaly remediations (AST-1111–AST-1113) delete the named shadows end-to-end against `astral.dispatch.run-next-is-chain-authority`.

   - `## When not to use` —
     - True config-owned catalogs that are not `run_next` topology (grades, normalize gates, `TASK_CONFIG` specs, seed AUTO defaults).
     - Replacing the §2.6.0 hop-label claim/graduation path with a new config list.
     - Depending on this pattern id for implementation until `status: approved` (AUTHORING).

   - Optional `## Notes` — Lands as `proposed` from AST-1109 / AST-1110. Archie may approve later; remediations bind to the statute first. Does not own AST-1108 seed cleanup.

4. In `canon/patterns/README.md`:
   - Add a harvested-corpus table row for this id with `status` **proposed** and path `` `dispatch/pattern.dispatch.run-next-chain-authority.md` ``.
   - Update the prose that currently says “All six catalog entries below are `status: approved`” so it remains accurate (e.g. note six approved plus this proposed entry, or count approved vs proposed explicitly — do not claim this entry is approved).

5. In `canon/patterns/HARVEST.md`, add one Crosswalk row:

   `| create (AST-1110) | \`pattern.dispatch.run-next-chain-authority\` | dispatch | \`dispatch/pattern.dispatch.run-next-chain-authority.md\` | AST-1109 | proposed — run_next chain authority; not yet Archie-approved |`

   Optionally add one Supporting / AC cite-map line that dispatch chain membership remediations cite this id **after** Archie approves — or leave AC cite map unchanged until approved (prefer: leave the AC cite map table unchanged; note in Crosswalk only).

⚠️ **Decision:** Land pattern as **`proposed`**, not `approved`. Parent Architectural definition requires Archie approval before implementation depends on the catalog id; AUTHORING forbids depending on proposed ids. Sibling remediations cite the **statute** (Stage 1) as binding; the pattern is the affirmative catalog note. Do **not** flip to approved in this child without an explicit Archie Linear comment naming this pattern id.

## Stage 3: CODE_RULES pointer

**Done when:** `docs/ASTRAL_CODE_RULES.md` cites `astral.dispatch.run-next-is-chain-authority` at §2.6.0 with one clarifying sentence; no other sections rewritten; no product code touched.

1. In `docs/ASTRAL_CODE_RULES.md`, under `#### 2.6.0 Dispatch run_next chains (AST-848)`, immediately after the existing `**Narrative (not a statute):** …` line (or immediately before the prose paragraph that starts “Within a **single** `do_task` invocation”), insert:

   `**Statute:** \`astral.dispatch.run-next-is-chain-authority\``

2. In the same §2.6.0 subsection, after the existing carve-out prose paragraph (the one ending with roster/consult / company batches), add exactly one clarifying sentence:

   `Config must not define parallel hop-membership or hop-order lists that restate chains already encoded in \`agent_task.run_next\` — see statute \`astral.dispatch.run-next-is-chain-authority\`.`

3. Do **not** edit §1.4, §2.1 body catalogs, or other statutes’ files. Do **not** change `src/**`.

⚠️ **Decision:** Single pointer at §2.6.0 (the carve-out home) rather than scattering new **Statute:** lines under §1.4 / §2.1 — those statutes stay as-is; the new statute is the loophole ban. Sibling tickets perform the deletes.

## Execution contract

- Stages in order; one commit per stage on the epic worktree sub branch; publish to `origin/<publish-ref>` after each stage per build-child.
- No files outside the Files Changed table.
- Ambiguity or codebase drift → stop and comment on **parent** AST-1109 with the Stage N blocked template.
- Leave consult/dispatcher/craft routing, frozenset deletes, boot SQL, Manage Tasks UI, and AST-1108 untouched.

## Self-Assessment

**Scope:** `Single-Component` — one new statute + register, one proposed pattern + register, and a CODE_RULES pointer. No `src/**` product changes.

**Conf:** `high` — mirrors AST-1098 statute landing + patterns AUTHORING propose lifecycle; parent already named both ids; violating examples are the three named shadows on tip.

**Risk:** `Medium` — wrong statute wording could mis-bind sibling remediations or over-ban legitimate config catalogs; landing the pattern as `approved` without Archie would violate AUTHORING; forgetting README/HARVEST register leaves Joan/Radia corpus incomplete.

## Self-review vs ASTRAL_CODE_RULES

- **§2.6.0 / no-daisy-chain-in-run:** Statute complements the carve-out (membership must match `run_next` data); does not remove or rewrite hop-label rules.
- **§2.1 / config-source-of-truth / pattern.config.config-block:** Clarifies when config must **not** duplicate DB topology; does not move true config catalogs out of `config.py`.
- **§1.4 / no-hardcoded-sets:** Explicitly states a config shadow of `run_next` is not a conforming “put it in config” escape.
- **§1.1 / in-scope-only:** No anomaly deletes, no boot SQL, no AST-1108.
- **Statute AUTHORING / orch.roles.archie-approves-statutes:** `status: active` + `approved_by: Archie`; pattern stays `proposed`.
- **No conflict requiring conf-!!-NONE.**

## Review

**Publish ref:** `origin/sub/AST-1109/AST-1110-statute-run-next-is-chain-authority`
**Tip:** `b962895c`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `d530d452` | statute astral.dispatch.run-next-is-chain-authority + register |
| 2 | `fc645e23` | proposed pattern.dispatch.run-next-chain-authority |
| 3 | `b962895c` | CODE_RULES §2.6.0 pointer |

### Radia — code-rubric.v1 (AST-1110)

`[code-rubric] revision=1` · tip reviewed `27130c72` · **Overall: DISCUSS** (C4 stragglers only; deliverable conforms)

**What's solid**

- Active Archie-approved statute at SCHEMA path; README/HARVEST count **58**.
- Pattern lands `proposed` (not approved); remediations bind statute first.
- CODE_RULES §2.6.0 statute pointer + clarifying sentence; no `src/**` / frozenset deletes.
- Betty test-bible docs-acceptance + merge-tests; no engineer test-tree edits for AST-1110.

**Discuss (C4 stragglers)** — Joan excluded at plan time; three-dot diff brings them in-scope (statute scores themselves `conforms`):

- `astral.debug.spikes-under-debug-dir`
- `astral.docs.features-single-file-per-ticket`
- `astral.git.betty-no-src-or-features`
- `astral.git.engineer-test-tree-ban`

**Recommended:** resolve-child can treat as acknowledge-and-proceed unless implementer wants plan Files Changed to list the plan path + Betty bible for future Joan runs.

## Resolution

**Date:** 2026-07-31  
**Publish tip before resolve:** `fc651c68` (`docs(AST-1110): Radia review — findings`)

Radia overall **DISCUSS** — no fix-now product or plan-doc edits. Deliverable statutes all **conforms**.

| Finding | Disposition |
|---------|-------------|
| discuss (Joan Excluded C4 stragglers on three-dot tip: spikes-under-debug-dir, features-single-file-per-ticket, betty-no-src-or-features, engineer-test-tree-ban) | Accepted as non-blocking; each scored **conforms** in Radia’s sweep; no product change. Files Changed left as engineer canon/docs deliverables (Betty bible stays Betty-owned, not retrofitted into plan Files Changed). |

No product commits on this resolve pass.
