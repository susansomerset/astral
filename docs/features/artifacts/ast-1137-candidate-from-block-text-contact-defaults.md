<!-- linear-archive: AST-1137 archived 2026-08-07 -->

## Linear archive (AST-1137)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1137/candidate-from-block-text-contact-defaults-cover-letter-header-is  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1124 — Cover Letter Header is incorrect  
**Blocked by / blocks / related:** parent: AST-1124; blocks: AST-1139; blocks: AST-1138

### Description

## What this implements

Owns the candidate-controlled from-block: config/field contract, persist + edit on the candidate (alongside existing cover signature contact fields), and default composition `Name • City, ST` / `email • phone` when unset. Does **not** own job SomersetCover document emit or session golden CSS parity.

## In scope

- [X] `pattern.config.config-block` — `COVER_FROM_BLOCK_CONFIG` + `contact.cover_letter_from_block` field contract
- [X] `pattern.ui.admin-endpoint` — Candidate Profile edit via existing `PUT …/data` merge (config-driven textarea)
- [X] `astral.config.config-source-of-truth` — separators, contact paths, sources live in config
- [X] `astral.layers.ui-config-driven-business-logic` — profile field from `UI_CONFIG`; composition in core resolve helper
- [X] `astral.standards.no-hardcoded-sets` — no ad-hoc from-block path/separator literals outside config
- [X] `astral.standards.in-scope-only` — candidate field + resolve only; no job/session HTML emit
- [X] `astral.layers.import-direction` — core imports utils; UI does not own composition logic

## Considered but excluded

- [X] Job Print Cover Letter SomersetCover `fromBlock` HTML emit — sibling AST-1138 (`src/core/builder.py` cover path)
- [X] Session Admin Cover Letter golden CSS / empty-form defaults wiring — sibling AST-1139
- [X] `{$SIGNATURE_IMAGE}` token semantics — AST-1123
- [X] Resume header/contact emit — out of epic; no resume golden reopen
- [X] New `resolve_tokens` / TOKEN_SOURCES surface for from-block — no current consumer on this ticket

## Acceptance criteria

2. [x] When the candidate has not set custom from-block text, that header defaults to `Name • City, ST` then `email • phone` from candidate contact (empty segments/lines omitted). — via `resolve_cover_from_block` (`source=default`); HTML emit is AST-1138.
3. [x] When the candidate has set their own from-block text, Print Cover Letter shows that text in `fromBlock` instead of the contact default. — via `resolve_cover_from_block` (`source=candidate`); HTML emit is AST-1138.

## Boundaries

- [X] Does **not** own job SomersetCover document emit or session golden CSS parity (siblings). Does **not** own AST-1123 signature-image token semantics.

## Notes for planning

Candidate-owned from-block beside existing cover signature contact fields; defaults when unset. Plan delivers `resolve_cover_from_block` for siblings to consume.

## Git branch (authoritative)

Parent `ftr/AST-1124-cover-letter-header-is-incorrect`. Child `sub/AST-1124/AST-1137-candidate-from-block-text-contact-defaults`.

### Comments

#### chuckles — 2026-08-02T21:17:58.045Z
[merge-child] blocked: git pull merge on sub — use: git fetch && git merge origin/ftr/<parent-segment>

Offending tip commit: `d5146ebd` — subject `Merge remote-tracking branch 'origin/dev' into sub/AST-1124/AST-1137-candidate-from-block-text-contact-defaults` (under resolve tip `3e2bdd44`).

@Ada Lovelace — rewrite publish ref so the sub-only range has no `Merge remote-tracking branch` subject (e.g. remake the origin/dev integrate with an explicit `merge(AST-1137): …` message, keep resolve tip, force-with-lease push). Then Chuckles will re-run merge-child.

— Chuckles

#### radia — 2026-08-02T20:51:10.863Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1137
**Publish ref:** `2f18e7a8eec48e69d0d0759fd19dd06cfca36aaf` (`origin/sub/AST-1124/AST-1137-candidate-from-block-text-contact-defaults`)
**Overall:** FIX-NOW

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | conforms | no graded agent_task / confidence path |
| astral.agent.do-task-delegation | scoped | conforms | no do_task changes |
| astral.agent.grade-vector-validation | scoped | conforms | no graded tasks |
| astral.batch.batch-id-first | scoped | conforms | no batch claim APIs |
| astral.batch.batch-id-format | scoped | conforms | no batch_id generation |
| astral.batch.claim-process-release | scoped | conforms | no batch processing |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | no agent_data RESPONSE writes |
| astral.config.config-source-of-truth | scoped | conforms | COVER_FROM_BLOCK_CONFIG + library/UI field; composition from config |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | no scoring floors |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | no secrets/env values |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths match none of ['artifacts/**', 'scripts/spikes/**'] |
| astral.debug.spikes-under-debug-dir | scoped | conforms | feature plan under docs/features/; not a spike dump |
| astral.dispatch.run-next-is-chain-authority | scoped | conforms | no run_next edits |
| astral.dispatch.seed-auto-false | scoped | conforms | no dispatch_task seed rows |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single docs/features/artifacts/ast-1137-….md |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty commits touch tests/bible only; engineer owns src/features |
| astral.git.engineer-test-tree-ban | scoped | conforms | test-tree changes on Betty test/merge-tests SHAs only |
| astral.layers.core-vs-external-bright-line | scoped | conforms | no external I/O; resolve in core |
| astral.layers.import-direction | scoped | conforms | core→utils only; no layer inversion |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers ['scripts'] ∩ diff ['core', 'docs', 'utils'] empty |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | profile textarea via DATA_SHAPES; composition in core |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | no coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | no consult/render_verdict |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | layers ['ui'] ∩ diff ['core', 'docs', 'utils'] empty |
| astral.seed.agent-tables-in-repo-json | scoped | conforms | no seed JSON changes |
| astral.seed.archie-catalog-wins | scoped | conforms | no catalog seed |
| astral.seed.boot-only-not-hot-path | scoped | conforms | no seed boot path |
| astral.seed.define-approved | scoped | conforms | no seed define |
| astral.seed.operator-rows-stay-deleted | scoped | conforms | no operator seed rows |
| astral.seed.other-via-coverage-join | scoped | conforms | no seed coverage join |
| astral.standards.data-raises-caller-logs | scoped | conforms | no data-layer product changes |
| astral.standards.database-header-inventory | scoped | not-applicable | layers ['data'] ∩ diff ['core', 'docs', 'utils'] empty |
| astral.standards.debug-contract-gated | scoped | violates | resolve_cover_from_block gates with if debug but never set_debug_flag — Style D no-ops |
| astral.standards.dry-and-focused-functions | scoped | conforms | one focused resolve helper |
| astral.standards.in-scope-only | scoped | conforms | no builder/HTML/session emit; siblings own Print |
| astral.standards.logging-via-utils | scoped | conforms | uses module get_logger / debug helpers |
| astral.standards.names-not-ticket-ids | scoped | conforms | API name resolve_cover_from_block; ticket only in docstring |
| astral.standards.no-cross-contamination | scoped | conforms | candidate field+resolve only; no resume header mix-in |
| astral.standards.no-hardcoded-sets | scoped | conforms | separators/paths/sources from COVER_FROM_BLOCK_CONFIG |
| astral.standards.public-then-helpers | scoped | conforms | public resolve after recompute_full_name |
| astral.standards.utils-data-late-import-only | scoped | conforms | config.py add is literals only; no utils→data |
| astral.state.core-decides-transitions | scoped | conforms | no candidate state transitions |
| astral.state.job-prior-states-enforced | scoped | conforms | no job state work |
| astral.state.no-daisy-chain-in-run | scoped | conforms | no dispatch run chaining |
| astral.ui.frontend-file-placement | scoped | not-applicable | layers ['ui'] ∩ diff ['core', 'docs', 'utils'] empty |
| astral.ui.naming-conventions | scoped | not-applicable | layers ['ui'] ∩ diff ['core', 'docs', 'utils'] empty |
| astral.ui.single-gunicorn-worker | scoped | conforms | config touch unrelated to gunicorn workers |
| orch.git.betty-merge-tests-one-sha | universal | conforms | one merge-tests(AST-1137) @ 4917e54b pinning tests 494d78b2 |
| orch.git.commit-vocabulary | universal | conforms | docs/code/test/merge-tests vocabulary on sub |
| orch.git.flow-direction-inviolable | universal | conforms | publish on origin/sub/AST-1124/AST-1137-… |
| orch.git.ftr-sub-topology | universal | conforms | child sub under parent ftr/AST-1124-… |
| orch.git.merge-on-checkout | universal | conforms | no illegal merge recipe in commits |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | no cherry-pick/rebase/force on tip |
| orch.git.no-dev-agent-branches | universal | conforms | sub publish-ref only |
| orch.git.one-epic-worktree-per-parent | universal | conforms | astral-AST-1124 epic worktree |
| orch.git.three-permanent-branches | universal | conforms | no permanent-branch invention |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | no open product decisions in diff |
| orch.pipeline.plan-is-bible | universal | conforms | stages 1–3 match plan Files Changed |
| orch.pipeline.project-scoped-queues | universal | conforms | Artifacts child scope only |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | no canon/statutes edits |
| orch.roles.betty-owns-test-tree | universal | conforms | test/bible via Betty test+merge-tests commits |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee remains Ada |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada stays assignee through Tests Passed |
| orch.roles.pre-commit-path-bans | universal | conforms | no banned-path product edits |

## Pattern conformance

- `pattern.config.config-block` — conforms (`COVER_FROM_BLOCK_CONFIG` + library/UI field)
- `pattern.ui.admin-endpoint` — conforms (existing `PUT …/data` merge; no new route)
- Ticket-cited astral statutes covered in table above
- Invented pattern catalog: none

## Plan adherence

Stages 1–3 match the plan and Self-Assessment Single-Component footprint: utils config + `resolve_cover_from_block` + config-driven profile textarea; no builder/HTML or session golden CSS (siblings AST-1138/1139). Cross-ticket boundary held. Plan Stage 2 debug steps followed except missing `set_debug_flag` (below).

## Findings

**fix-now:** `astral.standards.debug-contract-gated` / §5f — `resolve_cover_from_block` (`src/core/candidate.py`) calls `logger.debug_index` / `debug_detail` under `if debug:` but never `logger.set_debug_flag(debug)`. Module logger defaults `_debug_flag=False`, so Style D helpers early-return when callers pass `debug=True`. Fix: set the flag at function entry (same pattern as `save_candidate_data` / `get_candidate_id_for_query` in this module).

**discuss (C4 straggler):** Joan excluded `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, and `astral.debug.spikes-under-debug-dir` at plan time; three-dot diff puts them in-scope. Sweep scores all three **conforms**.

**advisory:** `COVER_FROM_BLOCK_CONFIG["name_column"]` declared but resolve hardcodes `candidate.get("full")` per plan Stage 2 literal — AC-correct; optional later config read.

## What's solid

Config contract + resolve defaults + omit-empty segments; profile field beside signature; one merge-tests SHA; no layer inversion.

## Notes

Joan plan-rubric APPROVED attached. §5g N/A. Docs append on plan file @ tip above.

context_tokens≈22000

#### betty — 2026-08-02T20:45:05.384Z
1. **Existing / new coverage**
   - `tests/component/core/test_candidate.py::TestAst1137ResolveCoverFromBlock` — custom vs default `resolve_cover_from_block`, omit empty segments/lines, DB-row vs token-view contact, Style D debug on/off
   - `tests/component/utils/test_config.py::TestAst1137CoverFromBlockConfig` — `COVER_FROM_BLOCK_CONFIG`, library `contact_keys` order, profile textarea under Cover Letter Signature, not in packet/`TOKEN_SOURCES`

2. **Broken / obsolete:** none — additive optional contact field + resolve helper. Job/session HTML emit stays siblings AST-1138 / AST-1139.

3. **Gaps closed this pass:** resolve + config contract (above).

**§6c:** N/A — no `CandidateProfile.tsx` product change (config-driven textarea only).

**Run:**
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst1137ResolveCoverFromBlock \
  tests/component/utils/test_config.py::TestAst1137CoverFromBlockConfig \
  -q
```

**Publish:** `origin/sub/AST-1124/AST-1137-candidate-from-block-text-contact-defaults` @ `4917e54b` (`merge-tests(AST-1137): origin/tests 494d78b2b8dd87eed62db1268b1a5bbd2c234da9`)

**Bible shasums on publish tip:**
- `docs/test-bible/core/candidate.md` `b959038dde32d2dfd9f1f8915bc1ee9832c4c772`
- `docs/test-bible/utils/config.md` `8b2c559d17ee16020b7ca14f7103c5b551107745`

— Betty

#### joan — 2026-08-02T20:39:51.953Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1137
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 Print Cover Letter shows SomersetCover fromBlock (not resume header) | N/A — boundary (AST-1138 job emit) |
| AC2 unset → default `Name • City, ST` / `email • phone` (omit empties) | Stages 1–2: `COVER_FROM_BLOCK_CONFIG` + `resolve_cover_from_block` default path (`location` + `contact_email`/`phone`) |
| AC3 custom from-block text used in fromBlock | Stages 1–3: persist `contact.cover_letter_from_block` + resolve `source=candidate`; Print HTML consume is AST-1138 |
| AC4 embedded golden stylesheet blocks | N/A — boundary (AST-1138) |
| AC5 Session Cover Letter fromBlock + stylesheet; empty form defaults | N/A — boundary (AST-1139); helper is the shared default source |
| AC6 Resume HTML unchanged | N/A — plan does not touch resume emit (in-scope-only) |
| AC7 debug=True Style D on touched cover emit | Partial — Stage 2 optional Style D on resolve; emit-path debug remains AST-1138/1139 |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 Config contract | Purpose/Functional scope candidate-controlled from-block; proposed child #1 config/field |
| Stage 2 Resolve helper | Functional scope defaults + custom-vs-default source for sibling emit |
| Stage 3 Profile edit path | Functional scope persist + edit beside cover signature; PUT …/data merge |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests in this plan |
| orch.git.commit-vocabulary | conforms | Publish on sub via engineer commit vocabulary |
| orch.git.flow-direction-inviolable | conforms | Publish only to origin/sub/… |
| orch.git.ftr-sub-topology | conforms | Child ref matches parent Git table |
| orch.git.merge-on-checkout | conforms | No illegal merge recipe |
| orch.git.no-cherry-pick-rebase-force | conforms | No cherry-pick/rebase/force |
| orch.git.no-dev-agent-branches | conforms | Uses sub/AST-1124/AST-1137-… only |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree astral-AST-1124 |
| orch.git.three-permanent-branches | conforms | No permanent-branch invention |
| orch.pipeline.call-susan-for-product-decisions | conforms | Decisions documented; no product ambiguity blocking |
| orch.pipeline.plan-is-bible | conforms | Binding stages + Files Changed present |
| orch.pipeline.project-scoped-queues | conforms | Single-child Artifacts scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate-plan only |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | No tests/ edits |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Ada) owns build |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer path after Plan Approved |
| orch.roles.pre-commit-path-bans | conforms | No banned-path edits |
| astral.agent.confidence-bounds | conforms | No graded agent_task / confidence path touched |
| astral.agent.do-task-delegation | conforms | No do_task / new agent_task |
| astral.agent.grade-vector-validation | conforms | No graded tasks |
| astral.batch.batch-id-first | conforms | No batch claim APIs |
| astral.batch.batch-id-format | conforms | No batch_id generation |
| astral.batch.claim-process-release | conforms | No batch processing |
| astral.batch.entity-agent-responses-latest-only | conforms | No agent_data RESPONSE writes |
| astral.config.config-source-of-truth | conforms | COVER_FROM_BLOCK_CONFIG + UI_CONFIG field; composition from config |
| astral.config.pass-threshold-vs-score-floor | conforms | No scoring/dispatch floors |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env values |
| astral.dispatch.run-next-is-chain-authority | conforms | No dispatch chain / run_next edits |
| astral.dispatch.seed-auto-false | conforms | No dispatch_task seed rows |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src/features; Betty excluded |
| astral.layers.core-vs-external-bright-line | conforms | No external I/O; resolve in core |
| astral.layers.import-direction | conforms | core→utils; UI config-driven; no layer inversion |
| astral.layers.ui-config-driven-business-logic | conforms | Profile textarea from UI_CONFIG; composition in core helper |
| astral.patterns.coat-check-never-store-empty | conforms | No coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | conforms | No consult/render_verdict |
| astral.patterns.require-auth-on-protected-endpoints | conforms | Uses existing auth’d PUT …/data; no new routes |
| astral.seed.agent-tables-in-repo-json | conforms | No seed JSON / agent table changes |
| astral.seed.archie-catalog-wins | conforms | No catalog seed work |
| astral.seed.boot-only-not-hot-path | conforms | No seed boot path |
| astral.seed.define-approved | conforms | No seed define path |
| astral.seed.operator-rows-stay-deleted | conforms | No operator seed rows |
| astral.seed.other-via-coverage-join | conforms | No seed coverage join |
| astral.standards.data-raises-caller-logs | conforms | No data-layer changes |
| astral.standards.debug-contract-gated | conforms | Optional Style D on resolve only when debug=True |
| astral.standards.dry-and-focused-functions | conforms | One resolve helper; mirrors signature field pattern |
| astral.standards.in-scope-only | conforms | No builder/HTML/session emit; siblings own Print |
| astral.standards.logging-via-utils | conforms | Uses existing candidate.py logger/debug helpers |
| astral.standards.names-not-ticket-ids | conforms | Public API name resolve_cover_from_block; ticket only in docstring |
| astral.standards.no-cross-contamination | conforms | Stays in config/candidate/profile; no resume header mix-in |
| astral.standards.no-hardcoded-sets | conforms | Separators/paths/sources in COVER_FROM_BLOCK_CONFIG |
| astral.standards.public-then-helpers | conforms | Public resolve after recompute_full_name |
| astral.standards.utils-data-late-import-only | conforms | No utils→data import changes |
| astral.state.core-decides-transitions | conforms | No candidate state transitions |
| astral.state.job-prior-states-enforced | conforms | No job state work |
| astral.state.no-daisy-chain-in-run | conforms | No dispatch run chaining |
| astral.ui.frontend-file-placement | conforms | Page stay CandidateProfile.tsx; no new dirs |
| astral.ui.naming-conventions | conforms | snake_case contact key; existing page PascalCase |
| astral.ui.single-gunicorn-worker | conforms | No gunicorn/worker changes |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.dispatch.run-next-is-chain-authority, astral.dispatch.seed-auto-false, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.patterns.require-auth-on-protected-endpoints, astral.seed.agent-tables-in-repo-json, astral.seed.archie-catalog-wins, astral.seed.boot-only-not-hot-path, astral.seed.define-approved, astral.seed.operator-rows-stay-deleted, astral.seed.other-via-coverage-join, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.names-not-ticket-ids, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.frontend-file-placement, astral.ui.naming-conventions, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths match none of plan paths
- astral.debug.spikes-under-debug-dir — paths match none of plan paths
- astral.docs.features-single-file-per-ticket — layers {docs} ∩ plan {core,ui,utils} empty
- astral.git.engineer-test-tree-ban — paths match none of plan paths
- astral.layers.scripts-exempt-from-layer-rules — layers {scripts} ∩ plan empty
- astral.standards.database-header-inventory — layers {data} ∩ plan empty

## Findings

None fix-now.

**discuss (non-blocking):** Child AC3 wording says “Print Cover Letter shows…” while Boundaries exclude job emit. Plan correctly delivers field + `resolve_cover_from_block` and documents sibling consume (AST-1138/1139). Matches parent proposed child #1.

**acceptable:** Self-assessment Single-Component / Conf high / Risk low matches additive optional contact field + helper with no HTML emit.

**R6 checklist:** Definition fidelity pass for child #1 ownership. Layer/import pass. Config source of truth pass. File placement pass. No batch/state-machine creep. DRY via signature field pattern. Scope does not reopen resume golden or AST-1123 tokens.

context_tokens≈48000

— Joan

#### chuckles — 2026-08-02T20:37:50.801Z
[thread-orphan] Joan session `da0027e7-276d-4fe2-a6e6-65c8eb77e24d` relocated into epic workspace chat hash for AST-1124.
found: `/home/susan/.cursor/chats/0f41bf986cfef9e06ea903e586d6d4d9/da0027e7-276d-4fe2-a6e6-65c8eb77e24d/store.db`
expected: `/home/susan/.cursor/chats/f7ffac3298a0695c4cb085be242377e5/da0027e7-276d-4fe2-a6e6-65c8eb77e24d/store.db`

— Chuckles

#### ada — 2026-08-02T20:37:28.843Z
Plan: [`docs/features/artifacts/ast-1137-candidate-from-block-text-contact-defaults.md`](https://github.com/susansomerset/astral/blob/sub/AST-1124/AST-1137-candidate-from-block-text-contact-defaults/docs/features/artifacts/ast-1137-candidate-from-block-text-contact-defaults.md) @ `22cbb782` on `sub/AST-1124/AST-1137-candidate-from-block-text-contact-defaults`.

- **Scope:** Single-Component — utils config + `resolve_cover_from_block` in `candidate.py` + config-driven profile textarea; no builder/HTML emit.
- **Conf:** high — mirrors `cover_letter_signature` library/UI pattern; composition rules fully specified in `COVER_FROM_BLOCK_CONFIG`.
- **Risk:** low — additive optional contact field; empty = defaults; job/session render unchanged until AST-1138/1139 wire the helper.

— Ada

---

# AST-1137 — Candidate from-block text + contact defaults

**Linear:** https://linear.app/astralcareermatch/issue/AST-1137/candidate-from-block-text-contact-defaults-cover-letter-header-is  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1124/cover-letter-header-is-incorrect  
**Publish ref:** `sub/AST-1124/AST-1137-candidate-from-block-text-contact-defaults`

Owns the candidate-controlled cover from-block: config field contract, persist + edit on Candidate Profile beside cover signature fields, and a shared resolve helper that returns custom text or the default `Name • City, ST` / `email • phone` composition when unset. Does **not** change job Print Cover Letter HTML emit or session Admin Cover Letter golden CSS (siblings AST-1138 / AST-1139 consume this contract).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `cover_letter_from_block` to `CANDIDATE_LIBRARY_CONFIG["contact_keys"]`; add `COVER_FROM_BLOCK_CONFIG` (field path, separators, contact segment paths, name source); add Candidate Profile textarea beside Cover Letter Signature; optional `TOKEN_SOURCES` entry only if an existing cover token map already documents sibling keys — **do not** invent a new resolve_tokens surface unless a current consumer requires it (none in this ticket). | utils |
| `src/core/candidate.py` | Add `resolve_cover_from_block(candidate: dict, *, debug: bool = False) -> dict` returning `{"text": str, "source": "candidate"\|"default"}` using `COVER_FROM_BLOCK_CONFIG` + name columns + `contact`. Optional Style D index/detail when `debug=True` (found custom vs recorded default). No builder / HTML emit. | core |
| `src/ui/frontend/src/pages/CandidateProfile.tsx` | No custom panel required — config-driven textarea via existing profile field renderer (same path as `contact.cover_letter_signature`). Touch only if the page hardcodes a field allowlist that would hide the new key; otherwise leave unchanged. | ui |

**Out of files (siblings):** `src/core/builder.py` job/session cover HTML, `AdminSessionCoverLetter.tsx`, job cover CSS golden — AST-1138 / AST-1139.

## Stage 1: Config contract

**Done when:** `COVER_FROM_BLOCK_CONFIG` and library/`UI_CONFIG` profile field declare the from-block key and composition rules; no business logic yet.

1. In `src/utils/config.py`, add `cover_letter_from_block` to `CANDIDATE_LIBRARY_CONFIG["contact_keys"]` (after `cover_letter_signature_image`, before `title_patterns`).
2. In `src/utils/config.py`, add module-level `COVER_FROM_BLOCK_CONFIG` (near `CANDIDATE_LIBRARY_CONFIG` / cover signature config) with exactly these keys:
   - `"contact_key": "cover_letter_from_block"`
   - `"segment_separator": " • "` (bullet with surrounding spaces, matching parent brief)
   - `"line_separator": "\n"`
   - `"name_column": "full"` — primary display name; when empty after strip, builder of the default line uses `recompute_full_name(first, last)` from name columns (same join as library)
   - `"line_1_contact_paths": ("location",)` — after name, join non-empty stripped segments with `segment_separator`
   - `"line_2_contact_paths": ("contact_email", "phone")` — join non-empty stripped segments with `segment_separator`
   - `"sources": ("candidate", "default")` — allowed `source` values returned by resolve (no hardcoded sets in core)
3. In `UI_CONFIG["detail"]["profile"]`, in the existing **"Cover Letter Signature"** group (immediately before or after the `contact.cover_letter_signature` textarea field), add:
   ```python
   {
       "key": "contact.cover_letter_from_block",
       "label": "Cover letter from-block",
       "type": "textarea",
   }
   ```
   Do **not** mark required. Empty / whitespace = unset (defaults apply at resolve time).
4. Do **not** add `cover_letter_from_block` to `TOPIC_MENU_GEN_CONFIG["packet_contact_keys"]` unless that tuple already lists signature keys (it does not today) — keep Estelle packet scope unchanged.
5. Do **not** change `BUILD_CONFIG["session_cover_letter"]` required `from_block` (session form field stays AST-1139).

⚠️ **Decision:** Field key is `contact.cover_letter_from_block` (not bare `from_block`) so it sits beside `cover_letter_signature*` and cannot be confused with session Admin `from_block` payload keys.

## Stage 2: Resolve helper (core)

**Done when:** `resolve_cover_from_block` returns custom text or default two-line composition; empty segments/lines omitted; `source` is always one of `COVER_FROM_BLOCK_CONFIG["sources"]`.

1. In `src/core/candidate.py`, after `recompute_full_name` (public section), add:

   ```python
   def resolve_cover_from_block(candidate: dict, *, debug: bool = False) -> dict:
       """Return cover from-block text + source for emit consumers (AST-1137).

       Returns ``{"text": str, "source": "candidate"|"default"}``.
       Custom wins when ``contact.cover_letter_from_block`` strips non-empty;
       otherwise compose defaults from name + contact per COVER_FROM_BLOCK_CONFIG.
       """
   ```

2. Implementation rules (literal):
   - Import `COVER_FROM_BLOCK_CONFIG` from `src.utils.config` (add to existing config import block).
   - Read `contact = (candidate.get("candidate_data") or {}).get("contact")` — if not a dict, treat as `{}`. Also accept a pre-built token view: if `candidate` already has top-level `"contact"` dict and no `"candidate_data"`, use that contact + top-level `first`/`last`/`full` (same shape as `build_candidate_token_view` output) so AST-1138 can pass either a DB row or a token view without a second adapter.
   - Custom path: `raw = contact.get(COVER_FROM_BLOCK_CONFIG["contact_key"])`; if `isinstance(raw, str)` and `raw.strip()` → return `{"text": raw.strip(), "source": "candidate"}` (strip outer whitespace only; preserve internal newlines).
   - Default path:
     - Name: `full = str(candidate.get("full") or "").strip()`; if empty, `full = recompute_full_name(str(candidate.get("first") or ""), str(candidate.get("last") or ""))`.
     - Build line 1: start with `[full]` if non-empty, then for each path in `line_1_contact_paths` append `str(contact.get(path) or "").strip()` when non-empty; join with `segment_separator`.
     - Build line 2: for each path in `line_2_contact_paths` append stripped non-empty values; join with `segment_separator`.
     - Join non-empty lines with `line_separator`.
     - Return `{"text": composed, "source": "default"}` (composed may be `""` if all contact/name empty).
   - `source` must be taken from / validated against `COVER_FROM_BLOCK_CONFIG["sources"]` (e.g. assign literals that appear in that tuple — do not invent a third source string).
3. When `debug=True`, emit one Style D index header (`func="candidate.resolve_cover_from_block"`, `identifier` = `candidate.get("astral_candidate_id")` or `candidate.get("_astral_candidate_id")` or `""`) with outcome `success — from_block {source}`, then `|` detail lines: `source=…`, `text_chars=N`, and for default path which line segments were non-empty (`line1_segments=…`, `line2_segments=…`). Use existing `logger` / `debug_index` / `debug_detail` patterns already in this module.
4. Do **not** call builder, do **not** write HTML, do **not** mutate `contact`.

⚠️ **Decision:** Resolve lives in `candidate.py` (not `builder.py`) so job/session emit siblings import one contract without pulling cover HTML into the candidate library layer.

## Stage 3: Profile edit path (UI)

**Done when:** Candidate Profile shows the from-block textarea and `PUT /api/candidates/<id>/data` persists `contact.cover_letter_from_block` via existing merge save (no new endpoint).

1. Confirm `CandidateProfile.tsx` renders `UI_CONFIG` profile fields generically (including textareas under `contact.*`). If it does, **no frontend code change** — Stage 1 config is sufficient.
2. If the page has a hardcoded skip-list / custom panel map that would omit unknown keys, extend it only as needed so `contact.cover_letter_from_block` renders as a normal textarea (no custom panel like signature image).
3. API: no new validation in `api_candidate.py` for this field (plain optional string). Do **not** add JPEG-style validation. Existing `save_candidate_data` merge already persists arbitrary contact keys.
4. Manual check (builder notes in Linear comment is enough; no product test tree edits): save a non-empty from-block → GET candidate shows it under `candidate_data.contact.cover_letter_from_block`; clear to empty → resolve returns `source=default` with composed lines from name/email/phone/location.

## Contract for siblings (non-goals for this ticket)

AST-1138 / AST-1139 **must** call `resolve_cover_from_block` (or equivalent import) when filling SomersetCover `fromBlock` / empty session from-block defaults. This ticket only guarantees the field + helper. Print Cover Letter AC 2–3 on the parent are satisfied when those siblings consume `text` / `source`.

## Self-Assessment

**Scope:** `Single-Component` — utils config + one core resolve helper + config-driven profile field; no builder/HTML emit.

**Conf:** `high` — mirrors `cover_letter_signature` profile + library key pattern; composition rules are fully specified in config.

**Risk:** `low` — additive optional contact field; empty default is backward-compatible; job/session render unchanged until siblings wire the helper.

## Code Rules check

- §1.1 in-scope-only: no job/session HTML, no AST-1123 token work.
- §1.4 / `no-hardcoded-sets`: separators and contact paths live in `COVER_FROM_BLOCK_CONFIG`.
- §2.1 config source of truth: field key + UI label in config.
- §3.2 / §3.3: UI stays config-driven; core imports utils only; ui does not grow business composition logic.
- §3.2 ui-config-driven: profile textarea from `UI_CONFIG`, not a React-only field.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1124/AST-1137-candidate-from-block-text-contact-defaults`

| Stage | Summary |
|-------|---------|
| 1 | `COVER_FROM_BLOCK_CONFIG` + `contact.cover_letter_from_block` library/UI field |
| 2 | `resolve_cover_from_block` — custom text or `Name • City, ST` / `email • phone` defaults |
| 3 | Profile: config-driven textarea (no `CandidateProfile.tsx` change) |

## Radia review (code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1137
**Publish ref:** `4917e54b1d2de7ac8bd291c66d2229b38c40afd1` (`origin/sub/AST-1124/AST-1137-candidate-from-block-text-contact-defaults`)
**Overall:** FIX-NOW

### What's solid

- Stages 1–3 match the plan: `COVER_FROM_BLOCK_CONFIG`, library contact key, DATA_SHAPES profile textarea beside signature, `resolve_cover_from_block` with custom-vs-default + omit-empty segments/lines.
- Boundaries held: no builder/HTML emit, no session golden CSS, no frontend panel invent.
- Config drives separators, contact paths, and source labels; core imports utils only.
- One `merge-tests(AST-1137)` pins Betty's tip; engineer commits stay off the test tree.

### Issues

**fix-now:** `astral.standards.debug-contract-gated` — `resolve_cover_from_block` calls `logger.debug_index` / `debug_detail` under `if debug:` but never `logger.set_debug_flag(debug)`. Module logger defaults `_debug_flag=False`, so Style D helpers early-return even when the caller passes `debug=True`. Sibling emit paths (AST-1138/1139) will get silent debug. Fix: `logger.set_debug_flag(debug)` at function entry (same pattern as `save_candidate_data` / `get_candidate_id_for_query` in this module). Location: `src/core/candidate.py` `resolve_cover_from_block`.

**discuss (C4 straggler):** Joan excluded `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, and `astral.debug.spikes-under-debug-dir` at plan time; three-dot diff puts them in-scope. Sweep scores all three **conforms** (single feature file; Betty-owned test/bible; plan doc not a spike dump).

**advisory:** `COVER_FROM_BLOCK_CONFIG["name_column"]` is declared but resolve hardcodes `candidate.get("full")` per plan Stage 2 literal. Behavior matches AC; consider reading `name_column` later for true config-source symmetry.

### Recommended actions

1. Ada: add `logger.set_debug_flag(debug)` at the top of `resolve_cover_from_block` (resolve-child).
2. Optional: use `COVER_FROM_BLOCK_CONFIG["name_column"]` instead of literal `"full"`.

### Pattern conformance

Cited from ticket/plan: `pattern.config.config-block` — conforms; `pattern.ui.admin-endpoint` — conforms (existing PUT …/data; no new route); `astral.config.config-source-of-truth` / `astral.layers.ui-config-driven-business-logic` / `astral.standards.no-hardcoded-sets` / `astral.standards.in-scope-only` / `astral.layers.import-direction` — covered in statutes table.

### Plan adherence

Diff footprint matches Self-Assessment Single-Component (utils config + one core helper + config-driven profile field). No builder/HTML smuggle from AST-1138/1139. Plan Stage 2 debug steps followed except missing `set_debug_flag` (above).

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | conforms | no graded agent_task / confidence path |
| astral.agent.do-task-delegation | scoped | conforms | no do_task changes |
| astral.agent.grade-vector-validation | scoped | conforms | no graded tasks |
| astral.batch.batch-id-first | scoped | conforms | no batch claim APIs |
| astral.batch.batch-id-format | scoped | conforms | no batch_id generation |
| astral.batch.claim-process-release | scoped | conforms | no batch processing |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | no agent_data RESPONSE writes |
| astral.config.config-source-of-truth | scoped | conforms | COVER_FROM_BLOCK_CONFIG + library/UI field; composition from config |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | no scoring floors |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | no secrets/env values |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths match none of ['artifacts/**', 'scripts/spikes/**'] |
| astral.debug.spikes-under-debug-dir | scoped | conforms | feature plan under docs/features/; not a spike dump |
| astral.dispatch.run-next-is-chain-authority | scoped | conforms | no run_next edits |
| astral.dispatch.seed-auto-false | scoped | conforms | no dispatch_task seed rows |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single docs/features/artifacts/ast-1137-….md |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty commits touch tests/bible only; engineer owns src/features |
| astral.git.engineer-test-tree-ban | scoped | conforms | test-tree changes on Betty test/merge-tests SHAs only |
| astral.layers.core-vs-external-bright-line | scoped | conforms | no external I/O; resolve in core |
| astral.layers.import-direction | scoped | conforms | core→utils only; no layer inversion |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers ['scripts'] ∩ diff ['core', 'docs', 'utils'] empty |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | profile textarea via DATA_SHAPES; composition in core |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | no coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | no consult/render_verdict |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | layers ['ui'] ∩ diff ['core', 'docs', 'utils'] empty |
| astral.seed.agent-tables-in-repo-json | scoped | conforms | no seed JSON changes |
| astral.seed.archie-catalog-wins | scoped | conforms | no catalog seed |
| astral.seed.boot-only-not-hot-path | scoped | conforms | no seed boot path |
| astral.seed.define-approved | scoped | conforms | no seed define |
| astral.seed.operator-rows-stay-deleted | scoped | conforms | no operator seed rows |
| astral.seed.other-via-coverage-join | scoped | conforms | no seed coverage join |
| astral.standards.data-raises-caller-logs | scoped | conforms | no data-layer product changes |
| astral.standards.database-header-inventory | scoped | not-applicable | layers ['data'] ∩ diff ['core', 'docs', 'utils'] empty |
| astral.standards.debug-contract-gated | scoped | violates | resolve_cover_from_block gates with if debug but never set_debug_flag — Style D no-ops |
| astral.standards.dry-and-focused-functions | scoped | conforms | one focused resolve helper |
| astral.standards.in-scope-only | scoped | conforms | no builder/HTML/session emit; siblings own Print |
| astral.standards.logging-via-utils | scoped | conforms | uses module get_logger / debug helpers |
| astral.standards.names-not-ticket-ids | scoped | conforms | API name resolve_cover_from_block; ticket only in docstring |
| astral.standards.no-cross-contamination | scoped | conforms | candidate field+resolve only; no resume header mix-in |
| astral.standards.no-hardcoded-sets | scoped | conforms | separators/paths/sources from COVER_FROM_BLOCK_CONFIG |
| astral.standards.public-then-helpers | scoped | conforms | public resolve after recompute_full_name |
| astral.standards.utils-data-late-import-only | scoped | conforms | config.py add is literals only; no utils→data |
| astral.state.core-decides-transitions | scoped | conforms | no candidate state transitions |
| astral.state.job-prior-states-enforced | scoped | conforms | no job state work |
| astral.state.no-daisy-chain-in-run | scoped | conforms | no dispatch run chaining |
| astral.ui.frontend-file-placement | scoped | not-applicable | layers ['ui'] ∩ diff ['core', 'docs', 'utils'] empty |
| astral.ui.naming-conventions | scoped | not-applicable | layers ['ui'] ∩ diff ['core', 'docs', 'utils'] empty |
| astral.ui.single-gunicorn-worker | scoped | conforms | config touch unrelated to gunicorn workers |
| orch.git.betty-merge-tests-one-sha | universal | conforms | one merge-tests(AST-1137) @ 4917e54b pinning tests 494d78b2 |
| orch.git.commit-vocabulary | universal | conforms | docs/code/test/merge-tests vocabulary on sub |
| orch.git.flow-direction-inviolable | universal | conforms | publish on origin/sub/AST-1124/AST-1137-… |
| orch.git.ftr-sub-topology | universal | conforms | child sub under parent ftr/AST-1124-… |
| orch.git.merge-on-checkout | universal | conforms | no illegal merge recipe in commits |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | no cherry-pick/rebase/force on tip |
| orch.git.no-dev-agent-branches | universal | conforms | sub publish-ref only |
| orch.git.one-epic-worktree-per-parent | universal | conforms | astral-AST-1124 epic worktree |
| orch.git.three-permanent-branches | universal | conforms | no permanent-branch invention |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | no open product decisions in diff |
| orch.pipeline.plan-is-bible | universal | conforms | stages 1–3 match plan Files Changed |
| orch.pipeline.project-scoped-queues | universal | conforms | Artifacts child scope only |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | no canon/statutes edits |
| orch.roles.betty-owns-test-tree | universal | conforms | test/bible via Betty test+merge-tests commits |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee remains Ada |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada stays assignee through Tests Passed |
| orch.roles.pre-commit-path-bans | universal | conforms | no banned-path product edits |

## Notes

- no plan-rubric verdict attachment missing — Joan APPROVED attached; stragglers noted above.
- §5f applied (debug= surface); §5g N/A (no LLM external).
- Three-dot vs `origin/dev` also includes unrelated Betty corpus from `merge-tests` (dispatcher/gazer/inbox/etc.); product surface for this ticket is `candidate.py` + `config.py` + plan/tests named above.

context_tokens≈22000

## Resolution

**2026-08-02 — Ada (`resolve-child`)**

- **fix-now** (`astral.standards.debug-contract-gated`): `resolve_cover_from_block` now calls `logger.set_debug_flag(debug)` at entry (same pattern as `save_candidate_data`), so Style D `debug_index` / `debug_detail` emit when callers pass `debug=True`.
- **discuss / advisory:** left as-is — C4 stragglers scored conforms; `name_column` unused is optional later config read, not required for AC.
