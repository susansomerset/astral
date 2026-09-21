<!-- linear-archive: AST-1125 archived 2026-08-07 -->

## Linear archive (AST-1125)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1125/cover-letter-signature-image-token-contract-support-signature-image-as  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1123 — Support Signature_Image as a token in the cover letter  
**Blocked by / blocks / related:** parent: AST-1123; blocks: AST-1126

### Description

## What this implements

Owns the config-side contract: register `{$SIGNATURE_IMAGE}` for cover-letter render resolution (cover-only; not a general LLM prompt binary injection), tied to the existing candidate signature-image source. Does **not** own HTML emit placement.

## Acceptance criteria

- [X] Rendering a job cover letter whose signature text contains `{$SIGNATURE_IMAGE}` between the closing and the name/title shows the signature image in that position — not above the closing. *(contract enables; emit is sibling)*
- [X] The literal token string `{$SIGNATURE_IMAGE}` does not appear in the rendered cover HTML when a valid image is available. *(contract enables; emit is sibling)*
- [X] Resume (base / job / session) HTML render paths do not resolve or display `{$SIGNATURE_IMAGE}` as an image. *(cover-only contract)*

## Boundaries

* Does **not** own HTML emit placement / stop-auto-above (sibling Cover HTML emit).
* Does **not** change Candidate Profile upload/validation UI.
* Does **not** invent a new signature-image storage field.
* Does **not** register `SIGNATURE_IMAGE` in `TOKEN_SOURCES` / `resolve_tokens`.

## In scope

- [X] `pattern.config.config-block` — `BUILD_CONFIG["cover_letter_render_tokens"]` owns the cover render-token contract
- [X] `astral.config.config-source-of-truth` — token literal, candidate path, surfaces, and omit policies live only in that config block
- [X] `astral.standards.no-hardcoded-sets` — emit must read `get_cover_letter_render_token` / the BUILD_CONFIG block; no parallel hardcoded `{$SIGNATURE_IMAGE}` set invented outside config

## Considered but excluded

- [X] `astral.standards.debug-contract-gated` — Style D debug belongs to AST-1126 cover emit paths, not this config-only ticket
- [X] `astral.layers.import-direction` / `pattern.layers.import-discipline` — no core/ui changes here; utils contract only
- [X] `astral.standards.in-scope-only` — resume emit, profile UI, and HTML replacement are sibling/out-of-scope (surfaces list encodes cover-only)
- [X] `astral.standards.no-cross-contamination` — resume builders must not consume `cover_letter_render_tokens` (enforced by not editing resume paths; emit sibling respects surfaces)
- [X] `astral.standards.dry-and-focused-functions` — safe-image validation reuse is AST-1126; this ticket does not fork a validator

## Notes for planning

Cover-only render token; source is existing `contact.cover_letter_signature_image`. Sibling Hedy (AST-1126) owns emit after this lands.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1123-support-signature-image-as-a-token-in-the-cover-letter`, child `sub/AST-1123/AST-1125-cover-letter-signature-image-token-contract`. Created at dispatch-parent.

### Comments

#### radia — 2026-08-02T17:57:00.407Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1125
**Publish ref:** `origin/sub/AST-1123/AST-1125-cover-letter-signature-image-token-contract` tip `3dd4db02eb60360c73193f7f9b990301cad134e1` (product reviewed through `26bfa458` + docs review append)
**Overall:** DISCUSS

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | conforms | no graded-task / confidence edits |
| `astral.agent.do-task-delegation` | scoped | not-applicable | layers+paths predicate miss vs utils+docs diff |
| `astral.agent.grade-vector-validation` | scoped | not-applicable | layers+paths predicate miss vs utils+docs diff |
| `astral.batch.batch-id-first` | scoped | not-applicable | layers+paths predicate miss vs utils+docs diff |
| `astral.batch.batch-id-format` | scoped | not-applicable | layers+paths predicate miss vs utils+docs diff |
| `astral.batch.claim-process-release` | scoped | not-applicable | layers+paths predicate miss vs utils+docs diff |
| `astral.batch.entity-agent-responses-latest-only` | scoped | not-applicable | layers+paths predicate miss vs utils+docs diff |
| `astral.config.config-source-of-truth` | scoped | conforms | literal/path/surfaces/policies only in BUILD_CONFIG cover_letter_render_tokens |
| `astral.config.pass-threshold-vs-score-floor` | scoped | conforms | thresholds untouched |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | conforms | no secrets/env keys added |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | paths predicate miss vs utils+docs diff |
| `astral.debug.spikes-under-debug-dir` | scoped | conforms | plan doc under docs/features/artifacts/; not a spike |
| `astral.dispatch.run-next-is-chain-authority` | scoped | conforms | no run_next / dispatch edits |
| `astral.dispatch.seed-auto-false` | scoped | conforms | no seed/dispatch_task edits |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | single docs/features/artifacts/ast-1125-….md |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty commits are test/bible only; engineer owns config+plan |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | Ada code() touched only src/utils/config.py; Betty owns tests |
| `astral.layers.core-vs-external-bright-line` | scoped | not-applicable | layers+paths predicate miss vs utils+docs diff |
| `astral.layers.import-direction` | scoped | conforms | utils-only product change; no layer inversion |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | layers+paths predicate miss vs utils+docs diff |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | contract in config for emit; no React rules |
| `astral.patterns.coat-check-never-store-empty` | scoped | not-applicable | layers+paths predicate miss vs utils+docs diff |
| `astral.patterns.render-verdict-orchestrates-consult` | scoped | not-applicable | layers+paths predicate miss vs utils+docs diff |
| `astral.patterns.require-auth-on-protected-endpoints` | scoped | not-applicable | layers+paths predicate miss vs utils+docs diff |
| `astral.seed.agent-tables-in-repo-json` | scoped | conforms | no seed JSON edits |
| `astral.seed.archie-catalog-wins` | scoped | conforms | no catalog edits |
| `astral.seed.boot-only-not-hot-path` | scoped | conforms | not seed/boot work |
| `astral.seed.define-approved` | scoped | conforms | not seed work |
| `astral.seed.operator-rows-stay-deleted` | scoped | conforms | not seed/dispatch work |
| `astral.seed.other-via-coverage-join` | scoped | conforms | not seed work |
| `astral.standards.data-raises-caller-logs` | scoped | not-applicable | layers predicate miss vs utils+docs diff |
| `astral.standards.database-header-inventory` | scoped | not-applicable | layers+paths predicate miss vs utils+docs diff |
| `astral.standards.debug-contract-gated` | scoped | conforms | no debug emission; Style D deferred to AST-1126 |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | thin accessor; no forked image validator |
| `astral.standards.in-scope-only` | scoped | conforms | config contract only; emit/resume/profile untouched |
| `astral.standards.logging-via-utils` | scoped | conforms | no logging changes |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | keys use SIGNATURE_IMAGE / cover_letter_render_tokens names |
| `astral.standards.no-cross-contamination` | scoped | conforms | separate from TOKEN_SOURCES; resume paths not consumers |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | BUILD_CONFIG block + accessor own the set |
| `astral.standards.public-then-helpers` | scoped | conforms | accessor with other BUILD helpers after BUILD_CONFIG |
| `astral.standards.utils-data-late-import-only` | scoped | conforms | no utils→data import added |
| `astral.state.core-decides-transitions` | scoped | not-applicable | layers+paths predicate miss vs utils+docs diff |
| `astral.state.job-prior-states-enforced` | scoped | conforms | no JOB_STATES / transition edits |
| `astral.state.no-daisy-chain-in-run` | scoped | not-applicable | layers+paths predicate miss vs utils+docs diff |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | layers+paths predicate miss vs utils+docs diff |
| `astral.ui.naming-conventions` | scoped | not-applicable | layers+paths predicate miss vs utils+docs diff |
| `astral.ui.single-gunicorn-worker` | scoped | conforms | no RAILWAY_CONFIG / worker changes |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | one merge-tests(AST-1125) SHA on sub |
| `orch.git.commit-vocabulary` | universal | conforms | plan/code/docs/test/merge-tests vocabulary |
| `orch.git.flow-direction-inviolable` | universal | conforms | publish on origin/sub/AST-1123/AST-1125-… |
| `orch.git.ftr-sub-topology` | universal | conforms | matches parent Git table topology |
| `orch.git.merge-on-checkout` | universal | conforms | no illegal merge recipe in diff |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | linear history; no force/rebase/cherry-pick |
| `orch.git.no-dev-agent-branches` | universal | conforms | sub/ topology only |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | epic worktree astral-AST-1123 |
| `orch.git.three-permanent-branches` | universal | conforms | no new permanent branches |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | OQ1/OQ2 encoded as omit policies; no new product Q |
| `orch.pipeline.plan-is-bible` | universal | conforms | Stage 1 block+accessor match plan literally |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Artifacts child scope |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Tests Passed → review-child |
| `orch.roles.archie-approves-statutes` | universal | conforms | no statute corpus edits |
| `orch.roles.betty-owns-test-tree` | universal | conforms | Betty test()+merge-tests own tests/test-bible |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | assignee remains Ada |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Ada stays assignee through Tests Passed |
| `orch.roles.pre-commit-path-bans` | universal | conforms | no banned path smuggling in product commit |

## Pattern conformance

- `pattern.config.config-block` — **conforms** (BUILD_CONFIG owns cover render-token contract; accessor reads that block)
- `astral.config.config-source-of-truth` / `astral.standards.no-hardcoded-sets` — covered via statute sweep (conforms)

## Plan adherence

Stage 1 shipped as planned: `BUILD_CONFIG["cover_letter_render_tokens"]["SIGNATURE_IMAGE"]` fields match the plan block; `get_cover_letter_render_token` returns that dict and raises `KeyError` for unknown names; `SIGNATURE_IMAGE` not in `TOKEN_SOURCES` / `get_tokens()`; no emit/resume/profile/UI edits. Self-Assessment Scope `Single-Component` / Conf `high` / Risk `low` matches the utils-only footprint. Blocks AST-1126 correctly left for emit.

## Findings

**discuss (C4 straggler):** Joan excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, and `astral.git.engineer-test-tree-ban` (plan Files Changed = utils only). Code-time three-dot diff includes the plan doc + Betty test tree, so those statutes are in-scope and **conform**. No product action — expected expansion.

No **fix-now**. No product layer / silent-failure / fallback / logging / debug-contract / external-cleanliness issues in the product diff.

## What’s solid

- Cover-only contract with omit policies encoding parent OQ1 for AST-1126.
- Explicit BUILD_CONFIG vs TOKEN_SOURCES separation prevents LLM binary injection.
- One `merge-tests(AST-1125)`; Ada stayed on `src/utils/config.py` only for `code()`.

## Notes

- Joan plan-rubric verdict attached (APPROVED). Stragglers called out above.
- Three-dot range also carries Betty `test(AST-1120)` bible/test paths not yet on `origin/dev` (skip-guarded). Advisory baseline drift — not AST-1125 product scope.
- §5f / §5g not applicable (no `debug=` surfaces; no LLM external modules).

## Recommended actions

- Ada / resolve-child: acknowledge the three C4 stragglers; no product patch required → User Testing.
- AST-1126: read `get_cover_letter_render_token("SIGNATURE_IMAGE")` on cover emit only.

context_tokens≈42000

#### chuckles — 2026-08-02T17:54:21.744Z
[thread-missing] Cursor chat `d3ff29e3-ad11-4b2a-b54f-287ac048a05d` has no local `store.db` on **chuckles** (expected `/home/susan/.cursor/chats/c949585722c8f009c0bb68bfaec8882f/d3ff29e3-ad11-4b2a-b54f-287ac048a05d/store.db`; blob-search also empty).

Minting a **new** conversation on this host and continuing (history from the old UUID is not recovered).

— Chuckles

#### betty — 2026-08-02T17:53:08.464Z
**QA test manifest — AST-1125**

`origin/sub/AST-1123/AST-1125-cover-letter-signature-image-token-contract` @ `26bfa458` (`merge-tests(AST-1125): origin/tests 11703177bbd3bf27e09a4c2c5b4e3940b8d1a02a`)

**Classification**
1. **Gaps (new):** `TestAst1125CoverLetterRenderTokenContract` — `BUILD_CONFIG["cover_letter_render_tokens"]["SIGNATURE_IMAGE"]` field contract; `get_cover_letter_render_token` success + unknown `KeyError`; `SIGNATURE_IMAGE` absent from `TOKEN_SOURCES` / `get_tokens()`; `resolve_tokens` leaves `{$SIGNATURE_IMAGE}` unchanged.
2. **Broken / obsolete:** none.
3. **Existing coverage:** none sufficient for this contract (new `BUILD_CONFIG` block + accessor).
4. **Integration:** none (config-only; no existing scenario invalidated).

**Run (test-child):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1125CoverLetterRenderTokenContract \
  -q
```

**Bible (publish tip):**
`docs/test-bible/utils/config.md` shasum `6c4ea1f97f22cf3a1f16c480ea63e4b176510562`

— Betty

#### chuckles — 2026-08-02T17:50:31.360Z
[thread-missing] Cursor chat `003557b9-f207-4f13-ba37-5e1fbe43db27` has no local `store.db` on **chuckles** (expected `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/003557b9-f207-4f13-ba37-5e1fbe43db27/store.db`; blob-search also empty).

Minting a **new** conversation on this host and continuing (history from the old UUID is not recovered).

— Chuckles

#### joan — 2026-08-02T17:48:20.659Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1125
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 image between closing and name/title | Stage 1 — contract (`literal`, path, policies); HTML placement owned by AST-1126 |
| AC2 literal absent when valid image available | Stage 1 — `literal` + `missing_or_rejected_image_policy`; emit owned by AST-1126 |
| AC3 no img / no broken placeholder when unusable | N/A — boundary (AST-1126 emit + `_safe_image_src`) |
| AC4 stop unconditional prepend above signature | N/A — boundary (AST-1126) |
| AC5 resume paths do not resolve token as image | Stage 1 — `surfaces: ["cover_letter"]`; no resume/TOKEN_SOURCES edits |
| AC6 Style D debug on cover render | N/A — boundary (AST-1126); child excludes debug-contract |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 BUILD_CONFIG cover render-token contract | Purpose cover-only `{$SIGNATURE_IMAGE}`; Functional scope #1; Architectural `pattern.config.config-block`; child #1 (Ada) |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work |
| orch.git.commit-vocabulary | conforms | Plan publish on sub ref; build will use plan()/code() |
| orch.git.flow-direction-inviolable | conforms | Publish only to origin/sub/AST-1123/AST-1125-… |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | No illegal merge recipe |
| orch.git.no-cherry-pick-rebase-force | conforms | Not proposed |
| orch.git.no-dev-agent-branches | conforms | Uses sub/ topology only |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree astral-AST-1123 |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | OQ1/OQ2 already resolved on parent; policies encoded in config |
| orch.pipeline.plan-is-bible | conforms | Binding Files Changed + Stage 1 steps |
| orch.pipeline.project-scoped-queues | conforms | Single-child Artifacts scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate-plan only |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | tests/ / test-bible excluded |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Ada) owns build |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer implementer path after approve |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | No graded-task / confidence changes |
| astral.config.config-source-of-truth | conforms | Token literal/path/surfaces/policies only in BUILD_CONFIG block |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env introduced |
| astral.dispatch.run-next-is-chain-authority | conforms | No dispatch/run_next edits |
| astral.dispatch.seed-auto-false | conforms | No seed/dispatch_task edits |
| astral.git.betty-no-src-or-features | conforms | Engineer owns config.py; Betty excluded |
| astral.layers.import-direction | conforms | utils-only Files Changed; no layer inversion |
| astral.layers.ui-config-driven-business-logic | conforms | Contract in config for core emit; no React rules |
| astral.seed.agent-tables-in-repo-json | conforms | No seed JSON edits |
| astral.seed.archie-catalog-wins | conforms | No catalog edits |
| astral.seed.boot-only-not-hot-path | conforms | Not seed work |
| astral.seed.define-approved | conforms | Not seed work |
| astral.seed.operator-rows-stay-deleted | conforms | Not seed work |
| astral.seed.other-via-coverage-join | conforms | Not seed work |
| astral.standards.debug-contract-gated | conforms | Explicitly deferred to AST-1126 emit |
| astral.standards.dry-and-focused-functions | conforms | Thin accessor; no forked image validator |
| astral.standards.in-scope-only | conforms | Config contract only; emit/resume/profile out |
| astral.standards.logging-via-utils | conforms | No logging changes |
| astral.standards.names-not-ticket-ids | conforms | Keys use SIGNATURE_IMAGE / cover_letter_render_tokens names |
| astral.standards.no-cross-contamination | conforms | Separate from TOKEN_SOURCES; resume must ignore |
| astral.standards.no-hardcoded-sets | conforms | Accessor + BUILD_CONFIG own the set for emit |
| astral.standards.public-then-helpers | conforms | Accessor placed with other BUILD helpers after BUILD_CONFIG |
| astral.standards.utils-data-late-import-only | conforms | No utils→data import added |
| astral.state.job-prior-states-enforced | conforms | No JOB_STATES / transition edits |
| astral.ui.single-gunicorn-worker | conforms | No RAILWAY_CONFIG / worker changes |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.dispatch.run-next-is-chain-authority, astral.dispatch.seed-auto-false, astral.git.betty-no-src-or-features, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.seed.agent-tables-in-repo-json, astral.seed.archie-catalog-wins, astral.seed.boot-only-not-hot-path, astral.seed.define-approved, astral.seed.operator-rows-stay-deleted, astral.seed.other-via-coverage-join, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.names-not-ticket-ids, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.job-prior-states-enforced, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.agent.do-task-delegation — layers ∩ plan {utils} empty
- astral.agent.grade-vector-validation — layers ∩ plan {utils} empty
- astral.batch.batch-id-first — layers ∩ plan {utils} empty
- astral.batch.batch-id-format — layers ∩ plan {utils} empty
- astral.batch.claim-process-release — layers ∩ plan {utils} empty
- astral.batch.entity-agent-responses-latest-only — layers ∩ plan {utils} empty
- astral.debug.no-repo-root-artifacts-dir — paths match none of plan paths
- astral.debug.spikes-under-debug-dir — paths match none of plan paths
- astral.docs.features-single-file-per-ticket — layers {docs} ∩ plan {utils} empty
- astral.git.engineer-test-tree-ban — paths match none of plan paths
- astral.layers.core-vs-external-bright-line — layers ∩ plan {utils} empty
- astral.layers.scripts-exempt-from-layer-rules — layers ∩ plan {utils} empty
- astral.patterns.coat-check-never-store-empty — layers ∩ plan {utils} empty
- astral.patterns.render-verdict-orchestrates-consult — layers ∩ plan {utils} empty
- astral.patterns.require-auth-on-protected-endpoints — layers ∩ plan {utils} empty
- astral.standards.data-raises-caller-logs — layers ∩ plan {utils} empty
- astral.standards.database-header-inventory — layers ∩ plan {utils} empty
- astral.state.core-decides-transitions — layers ∩ plan {utils} empty
- astral.state.no-daisy-chain-in-run — layers ∩ plan {utils} empty
- astral.ui.frontend-file-placement — layers ∩ plan {utils} empty
- astral.ui.naming-conventions — layers ∩ plan {utils} empty

## Findings

None fix-now.

**acceptable:** Self-assessment Single-Component / Conf high / Risk low matches a one-file config contract. Explicit BUILD_CONFIG vs TOKEN_SOURCES Decision prevents LLM binary injection. Integration note correctly parks emit with AST-1126.

**R6:** Definition fidelity pass (child #1 only). Config source-of-truth pass. Layer utils-only pass. No scope creep into emit/resume/profile. DRY pass (no second validator).

context_tokens≈38000

— Joan

#### chuckles — 2026-08-02T17:46:40.839Z
[thread-orphan] Joan chat `da0027e7-276d-4fe2-a6e6-65c8eb77e24d` found under wrong workspace hash; relocated → `/home/susan/.cursor/chats/c949585722c8f009c0bb68bfaec8882f/da0027e7-276d-4fe2-a6e6-65c8eb77e24d/store.db`. Same UUID — resume (not first-spawn).

— Chuckles

#### ada — 2026-08-02T17:46:20.129Z
Plan published on `origin/sub/AST-1123/AST-1125-cover-letter-signature-image-token-contract` @ `62f2bfa5`.

[Plan doc](https://github.com/susansomerset/astral/blob/sub/AST-1123/AST-1125-cover-letter-signature-image-token-contract/docs/features/artifacts/ast-1125-cover-letter-signature-image-token-contract.md)

**Scope — Single-Component:** One `BUILD_CONFIG["cover_letter_render_tokens"]` block plus `get_cover_letter_render_token` in `src/utils/config.py`; no core/ui/data edits.

**Conf — high:** Same config-ahead-of-emit pattern as AST-365 / AST-1024; path already exists on contact; deliberately kept out of `TOKEN_SOURCES` so image bytes never hit LLM prompts.

**Risk — low:** Config-only; wrong path would blank the image once AST-1126 lands (easy QA catch). Accidental `TOKEN_SOURCES` registration is the failure mode Stage 1 forbids.

#### chuckles — 2026-08-02T17:44:49.201Z
[thread-missing] Cursor chat `daf1a80f-7993-4d8b-b509-e3e74e1fdd3e` has no local `store.db` on **chuckles** (expected `/home/susan/.cursor/chats/c949585722c8f009c0bb68bfaec8882f/daf1a80f-7993-4d8b-b509-e3e74e1fdd3e/store.db`; blob-search also empty).

Minting a **new** conversation on this host and continuing (history from the old UUID is not recovered).

— Chuckles

---

# AST-1125 — Cover-letter SIGNATURE_IMAGE token contract

**Linear:** [AST-1125](https://linear.app/astralcareermatch/issue/AST-1125/cover-letter-signature-image-token-contract-support-signature-image-as)  
**Parent:** [AST-1123](https://linear.app/astralcareermatch/issue/AST-1123/support-signature-image-as-a-token-in-the-cover-letter) — Support Signature_Image as a token in the cover letter  
**Publish ref:** `origin/sub/AST-1123/AST-1125-cover-letter-signature-image-token-contract`  
**Unblocks:** [AST-1126](https://linear.app/astralcareermatch/issue/AST-1126/cover-html-emit-token-replace-and-stop-auto-above) — Cover HTML emit (Hedy)

Register a cover-only `{$SIGNATURE_IMAGE}` **render** contract in `BUILD_CONFIG` so cover HTML emit can resolve the candidate’s existing signature image at the token position. This is **not** an LLM prompt token (`TOKEN_SOURCES` / `resolve_tokens`) and does **not** change HTML emit or profile upload.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `BUILD_CONFIG["cover_letter_render_tokens"]` with `SIGNATURE_IMAGE` contract; add thin accessor `get_cover_letter_render_token` | utils |

**Out of scope (do not touch):**

| Item | Owner |
|------|--------|
| Cover HTML token replace / stop auto-above / Style D debug on emit | AST-1126 |
| Resume (base / job / session) HTML emit | excluded — resume must ignore this contract |
| `TOKEN_SOURCES` / `resolve_tokens` / Manage Tasks token pickers | excluded — binary image must not inject into prompts |
| Candidate Profile signature-image upload/validation UI | excluded |
| New signature-image storage field | excluded — reuse `contact.cover_letter_signature_image` |
| `tests/` / `docs/test-bible/**` | Betty |

## Stage 1: BUILD_CONFIG cover render-token contract

**Done when:** `BUILD_CONFIG["cover_letter_render_tokens"]["SIGNATURE_IMAGE"]` exists with the fields below; `get_cover_letter_render_token("SIGNATURE_IMAGE")` returns that dict; `"SIGNATURE_IMAGE"` is **absent** from `TOKEN_SOURCES` / `get_tokens()`; `python3 -m py_compile src/utils/config.py` passes.

1. In `src/utils/config.py`, inside `BUILD_CONFIG`, immediately after the `"session_cover_letter"` block (before the closing `}` of `BUILD_CONFIG`), add:

```python
    # AST-1125: cover HTML render tokens (NOT TOKEN_SOURCES / resolve_tokens).
    # Emit (AST-1126) reads this contract; resume builders must ignore it.
    "cover_letter_render_tokens": {
        "SIGNATURE_IMAGE": {
            "literal": "{$SIGNATURE_IMAGE}",
            "surfaces": ["cover_letter"],
            "source": "candidate",
            "path": "contact.cover_letter_signature_image",
            "value_kind": "safe_image_src",
            # Parent OQ1: no token in signature content → omit image (no fallback insert).
            "absent_token_policy": "omit",
            "missing_or_rejected_image_policy": "omit",
        },
    },
```

2. Immediately after the `BUILD_CONFIG = { ... }` closing brace (near other BUILD helpers such as `resume_artifact_compound_state`), add:

```python
def get_cover_letter_render_token(name: str) -> dict:
    """Return BUILD_CONFIG cover render-token contract for ``name``.

    Raises KeyError when ``name`` is not registered. Cover HTML emit (AST-1126)
    must use this (or the same BUILD_CONFIG path) — do not hardcode the literal
    or candidate path. Not part of TOKEN_SOURCES / resolve_tokens.
    """
    return BUILD_CONFIG["cover_letter_render_tokens"][name]
```

3. Do **not** add `SIGNATURE_IMAGE` (or `{$SIGNATURE_IMAGE}`) to `TOKEN_SOURCES`.
4. Do **not** change `resolve_tokens`, `get_tokens`, `get_manage_tasks_chain_tokens`, or `get_manage_agents_tokens`.
5. Do **not** edit `src/core/builder.py`, session/job cover emit, resume emit, UI, or Candidate Profile.
6. Do **not** invent a new storage key — path stays `contact.cover_letter_signature_image` (same field as today’s profile signature image after AST-1014 contact migration).

⚠️ **Decision:** Live in `BUILD_CONFIG`, not `TOKEN_SOURCES`. `TOKEN_SOURCES` feeds `resolve_tokens()` for LLM prompt text; a data-URL / image src must never be injected into prompts. `BUILD_CONFIG` already owns artifact **rendering** tokens (module header). Sibling AST-1126 consumes this contract for cover emit only.

⚠️ **Decision:** `surfaces: ["cover_letter"]` is the cover-only gate for AC3. Resume builders do not read `cover_letter_render_tokens`. Emit must check surface / only import this helper on cover paths — resume code stays untouched on this ticket.

⚠️ **Decision:** Policies `absent_token_policy` / `missing_or_rejected_image_policy` are declared here so emit does not invent product rules. Actual replacement and removal of auto-above prepend are AST-1126.

## Integration note for AST-1126 (not this ticket)

Emit should:

1. Read `tok = get_cover_letter_render_token("SIGNATURE_IMAGE")`.
2. Search cover signature text for `tok["literal"]`.
3. If present: resolve candidate blob at `tok["path"]` through existing `_safe_image_src`; on accept replace the literal with a safe `<img>`; on reject/missing apply `missing_or_rejected_image_policy` (`omit` — remove literal, no broken img).
4. If absent: apply `absent_token_policy` (`omit` — no auto-insert between closing and name).
5. Stop unconditional image prepend above the signature block (parent OQ2).
6. Leave resume HTML paths alone.

## Self-Assessment

**Scope — `Single-Component`**  
One `BUILD_CONFIG` sub-block plus one accessor in `src/utils/config.py`; no core/ui/data changes.

**Conf — `high`**  
Mirrors the AST-365 / AST-1024 pattern of registering a contract in config ahead of emit; path already exists on contact; deliberate non-registration in `TOKEN_SOURCES` is explicit in the ticket.

**Risk — `low`**  
Config-only. Wrong path would blank the image once emit lands (easy to spot); accidental `TOKEN_SOURCES` registration would be the high-risk mistake and is forbidden by Stage 1 step 3.

## Self-review vs ASTRAL_CODE_RULES

| Rule | Check |
|------|--------|
| §2.1 / `astral.config.config-source-of-truth` | Token literal, path, surfaces, and omit policies live only in `BUILD_CONFIG["cover_letter_render_tokens"]`. |
| §1.4 / `astral.standards.no-hardcoded-sets` | Accessor + config block are the set; emit must not invent a parallel literal. |
| §1.3 DRY | No second validator; emit reuses `_safe_image_src` (sibling). |
| §3.3 import direction | utils only; no core/ui edits. |
| §3.5 naming | `cover_letter_render_tokens` / `get_cover_letter_render_token` / `SIGNATURE_IMAGE` snake/SCREAMING aligned with `TOKEN_SOURCES` key style for the name, but separate registry. |
| `astral.standards.in-scope-only` | Cover render contract only; resume/profile/emit excluded. |
| `astral.standards.debug-contract-gated` | Not applicable this ticket (emit owns Style D). |

## Review (stub — build-child)

**Branch:** `sub/AST-1123/AST-1125-cover-letter-signature-image-token-contract`  
**Code:** `314f39e1`

**Shipped**

- `BUILD_CONFIG["cover_letter_render_tokens"]["SIGNATURE_IMAGE"]` — literal, cover-only surfaces, `contact.cover_letter_signature_image`, omit policies.
- `get_cover_letter_render_token(name)` accessor for emit (AST-1126).
- `SIGNATURE_IMAGE` not in `TOKEN_SOURCES` / `get_tokens()`.

## Radia review — code-rubric.v1

`[code-rubric] revision=1`  
**Overall:** DISCUSS (C4 stragglers only — no product fix-now)  
**Publish tip reviewed:** `26bfa458ac6eae4fabbd94cf22c602afe6192c0f` (`origin/sub/AST-1123/AST-1125-cover-letter-signature-image-token-contract`)  
**Baseline:** `origin/dev`

### What’s solid

- Stage 1 plan matches `src/utils/config.py` literally: `cover_letter_render_tokens.SIGNATURE_IMAGE` fields + `get_cover_letter_render_token`.
- `SIGNATURE_IMAGE` absent from `TOKEN_SOURCES` / `get_tokens()`; `resolve_tokens` leaves the literal untouched.
- Cover-only gate encoded as `surfaces: ["cover_letter"]`; omit policies encode parent OQ1 for AST-1126.
- Engineer product commit is utils-only; Betty owns test/bible; one `merge-tests(AST-1125)`.

### Findings

**discuss (C4 straggler):** Joan excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, and `astral.git.engineer-test-tree-ban` at plan time (Files Changed = utils only). Code-time three-dot diff includes the plan doc + Betty test tree, so those statutes score in-scope and **conform**. No product action — acknowledge and continue.

### Recommended actions

- Ada: no `fix-now` product work. On resolve-child, acknowledge the three C4 stragglers (expected docs + Betty expansion) and move to User Testing.
- AST-1126: consume `get_cover_letter_render_token("SIGNATURE_IMAGE")` only on cover emit paths.

## Resolution

**Date:** 2026-08-02  
**Ref:** Radia `[code-rubric] revision=1` Overall DISCUSS (no fix-now)

- **fix-now:** none — product tip unchanged (`314f39e1` / publish through Radia docs tip).
- **discuss (C4 stragglers):** Acknowledged. `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, and `astral.git.engineer-test-tree-ban` were plan-time exclusions (Files Changed = utils); code-time three-dot diff correctly expands to plan doc + Betty test tree and those statutes **conform**. No product patch.
- **advisory:** Betty `test(AST-1120)` baseline drift noted; out of AST-1125 product scope.
