<!-- linear-archive: AST-983 archived 2026-08-05 -->

## Linear archive (AST-983)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-983/docs-bible-and-test-sweep-for-agent-responses-table-retirement  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-975 — Decommission table AGENT_RESPONSES  
**Blocked by / blocks / related:** parent: AST-975; blocks: AST-984

### Description

## What this implements

Updates mandate/config comments and tests so nothing still assumes the standalone `agent_responses` table exists; keeps entity-column contract language accurate until the column-retirement sibling lands (then aligns with that mandate change).

## Acceptance criteria

4. Mandate docs and Test Bible text no longer list the standalone `agent_responses` table as live inventory; if entity columns remain temporarily, prose clearly distinguishes **table (retired)** vs **entity JSON column (live until later sibling)**.

## Boundaries

* Does **not** drop the table (sibling schema drop).
* Does **not** remove runtime table writes (sibling AST-981).
* Does **not** drop entity columns (sibling: Retire entity columns) — may note pending retirement.

## Notes for planning

* Code Rules / config comments still mention the table alongside entity columns — split the language carefully.
* Component tests that mock `add_agent_response_entry` need cleanup after AST-981.

## Git branch (authoritative)

Per orientation § Branch law. Publish to `origin/<publish-ref>` only.

### Comments

#### katherine — 2026-07-25T19:55:05.402Z
origin/sub/AST-975/AST-983-docs-bible-test-sweep-agent-responses @ 3a0c8ce · §9a clean · ftr dry-run clean (rebuilt stack on ftr; drop polluted origin/dev pull-merge).

#### radia — 2026-07-25T19:52:45.154Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-983
**Publish ref:** `87b68899222491990b5237532450f18e0fa95c39` (`origin/sub/AST-975/AST-983-docs-bible-test-sweep-agent-responses`)
**Overall:** DISCUSS

Diff baseline: `origin/dev...origin/sub/AST-975/AST-983-docs-bible-test-sweep-agent-responses` (includes AST-981/982 ancestors not yet on `origin/dev`).

## Statutes checked

| id | tier | verdict | one-line |
| -- | -- | -- | -- |
| astral.agent.confidence-bounds | scoped | conforms | Comment-only `config.py`; no confidence math |
| astral.agent.do-task-delegation | scoped | conforms | AST-983 does not alter `do_task`; core delta is ancestor |
| astral.agent.grade-vector-validation | scoped | conforms | Grade-vector validation untouched |
| astral.batch.batch-id-first | scoped | conforms | No claim/get/clear changes |
| astral.batch.batch-id-format | scoped | conforms | No batch_id format changes |
| astral.batch.claim-process-release | scoped | conforms | No claim→process→release edits |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | §2.4.1 column contract preserved; table marked retired only |
| astral.config.config-source-of-truth | scoped | conforms | ENTITY_TYPES values unchanged; comment split only |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | Scoring thresholds untouched |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No secrets/env handling changes |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Plan docs under `docs/features/`; not misplaced spikes |
| astral.docs.features-single-file-per-ticket | scoped | conforms | One features file per ticket (981/982/983) |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty bible commit avoided `src/` and features |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer `code()` = Code Rules + config + plan stub |
| astral.layers.core-vs-external-bright-line | scoped | conforms | No external I/O moves |
| astral.layers.import-direction | scoped | conforms | No import-graph changes |
| astral.layers.scripts-exempt-from-layer-rules | scoped | conforms | Script paths are ancestors; AST-983 has none |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | No UI behavior; utils comment only |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | Coat-check untouched |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | Consult orchestrator not in AST-983 delta |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | layers miss (no ui) |
| astral.standards.data-raises-caller-logs | scoped | conforms | No data-layer logging changes in AST-983 |
| astral.standards.database-header-inventory | scoped | conforms | Header already cleared by AST-982 ancestor |
| astral.standards.debug-contract-gated | scoped | conforms | No debug-contract edits |
| astral.standards.dry-and-focused-functions | scoped | conforms | No new helpers; prose split only |
| astral.standards.in-scope-only | scoped | conforms | Mandate/bible lane only; no schema/runtime/statute steal |
| astral.standards.logging-via-utils | scoped | conforms | No logging facade changes |
| astral.standards.no-cross-contamination | scoped | conforms | Stays in docs + utils comment |
| astral.standards.no-hardcoded-sets | scoped | conforms | No new inline sets |
| astral.standards.public-then-helpers | scoped | conforms | No function layout changes |
| astral.standards.utils-data-late-import-only | scoped | conforms | Comment-only in config; no utils→data import |
| astral.state.core-decides-transitions | scoped | conforms | No state-transition logic |
| astral.state.job-prior-states-enforced | scoped | conforms | No JOB_STATES edits |
| astral.state.no-daisy-chain-in-run | scoped | conforms | No run_next / daisy-chain changes |
| astral.ui.frontend-file-placement | scoped | not-applicable | layers miss (no ui) |
| astral.ui.naming-conventions | scoped | not-applicable | layers miss (no ui) |
| astral.ui.single-gunicorn-worker | scoped | conforms | No gunicorn/start path edits |
| orch.git.betty-merge-tests-one-sha | universal | conforms | One `merge-tests(AST-983): origin/tests 19e8e97…` |
| orch.git.commit-vocabulary | universal | conforms | `code`/`docs`/`merge-tests` vocab (Betty bible via `docs`) |
| orch.git.flow-direction-inviolable | universal | conforms | Tip on child `sub/` publish-ref |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-975/AST-983-docs-bible-test-sweep-agent-responses` |
| orch.git.merge-on-checkout | universal | conforms | Merged `origin/dev` + ftr before Stage 1 |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No cherry-pick/rebase/force |
| orch.git.no-dev-agent-branches | universal | conforms | No agent-named publish branch |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Reviewed in `astral-AST-975` |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branch |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | OQ1 keep-columns until AST-984; no new fork |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–2 match delivery |
| orch.pipeline.project-scoped-queues | universal | conforms | Single-child review |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Entered from Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No `canon/statutes/**` edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Bible via Betty; tests already cleaned by 981/982 |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Implementer Katherine |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Review does not flip assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | Docs-only Radia commit |

## Pattern conformance

none cited

## Plan adherence

Matches Stages 1–2 and Self-Assessment Scope `minor`. Mandate/config prose distinguishes table(retired) vs column(live until AST-984); §2.4.1 contract body untouched. Betty bible cross-links updated; engineer avoided test-tree. AST-982 `blockedBy` / ftr ancestor satisfied.

## Findings

**discuss (C4 straggler):** Joan Excluded these 16 statutes; three-dot scores them in-scope due to AST-981/982 ancestor paths still absent from `origin/dev`: `astral.agent.do-task-delegation`, `astral.agent.grade-vector-validation`, `astral.batch.batch-id-first`, `astral.batch.batch-id-format`, `astral.batch.claim-process-release`, `astral.batch.entity-agent-responses-latest-only`, `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.layers.core-vs-external-bright-line`, `astral.layers.scripts-exempt-from-layer-rules`, `astral.patterns.coat-check-never-store-empty`, `astral.patterns.render-verdict-orchestrates-consult`, `astral.standards.data-raises-caller-logs`, `astral.standards.database-header-inventory`, `astral.state.core-decides-transitions`, `astral.state.no-daisy-chain-in-run`. Substance for all: **conforms**. No product fix expected.

**advisory:** Plan Review stub tip string was mangled (`"'76d4979'"`) — cosmetic.

### What’s solid

- Clear table-vs-column language in Code Rules + config + bible.
- Column latest-only contract preserved for AST-984.
- One Betty merge-tests SHA.

### Recommended actions

1. Acknowledge C4 stragglers at resolve-child (no code).
2. AST-984 for entity-column retirement + statute rewrite.

**Notes:** Joan plan-rubric verdict attached (APPROVED). Docs append on plan file @ tip.

context_tokens≈36000

#### betty — 2026-07-25T19:49:45.718Z
## QA test manifest

**Publish:** `origin/sub/AST-975/AST-983-docs-bible-test-sweep-agent-responses` @ `abc6d2c` (`merge-tests(AST-983): origin/tests 19e8e97e73ff9776d0efdbee7f2ad2b7ac36e596`)

### 1. Existing coverage (bible-backed — no new pytest)
AST-981/982 already removed `add_agent_response_entry` mocks, table insert/list cases, and `_ensure_*`; sunset + entity upsert coverage stays.

1. `TestAst981StandaloneTableIoRetired`
2. `TestAst982StandaloneTableSunset`
3. `TestAst726AppendAgentResponseUpsert`
4. `TestAst981StandaloneTableAuditRetired`

### 2. Bible / docs this pass
1. `docs/test-bible/data/database/agent_responses.md` — entity-column title/intro; table retired; `### AST-983` docs-acceptance block.
2. Cross-link wording: `core/roster.md`, `core/consult.md`, `dev/backfill_latest_only_rubric_entity_data.md` — entity-row JSON only.
3. Engineer `code(AST-983)` already split `docs/ASTRAL_CODE_RULES.md` + `src/utils/config.py` (verify via rg below).

### 3. Run (test-child)
```bash
rg -n 'agent_responses' docs/ASTRAL_CODE_RULES.md src/utils/config.py
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_agent_responses.py::TestAst981StandaloneTableIoRetired \
  tests/component/data/database/test_agent_responses.py::TestAst982StandaloneTableSunset \
  tests/component/data/database/test_agent_responses.py::TestAst726AppendAgentResponseUpsert \
  tests/component/core/test_agent.py::TestAst981StandaloneTableAuditRetired \
  -q
```

**Pass:** rg hits are column-scoped or mark table retired; pytest green.

### Bible shasums on publish-ref
- `docs/test-bible/data/database/agent_responses.md` `3693e543f2449e14cc116d99ec8f2e05af28280e`
- `docs/test-bible/core/roster.md` `df0665f3babb033ae42d07a9bac8ed6f4179cc34`
- `docs/test-bible/core/consult.md` `c696428c163e2ae67a5cda72a8ef2ec94552cf34`
- `docs/test-bible/dev/backfill_latest_only_rubric_entity_data.md` `d2f5c55e8acfe4e30643547e18fead0559dd26ee`

— Betty

#### katherine — 2026-07-25T19:48:37.700Z
origin/sub/AST-975/AST-983-docs-bible-test-sweep-agent-responses @ 76c2085 — Stage 2 bible/tests still Betty (plan checklist).

#### joan — 2026-07-25T19:11:52.945Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-983
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-975/AST-983-docs-bible-test-sweep-agent-responses`
**Implementer:** Katherine (parent Team table / plan author)
**Notes:** Layer cells `bible (Betty)` / `tests (Betty)` mapped to `docs` per unrecognized→docs rule. `astral.batch.entity-agent-responses-latest-only` excluded by path match (no `src/core|data` in Files Changed); §2.4.1 preservation still scored under R6.

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
| -- | -- |
| AC1 — table gone after bootstrap | N/A — boundary: “Does not drop the table (sibling schema drop)” |
| AC2 — no create/read/write under src/scripts/tests | Runtime/schema N/A — AST-981/982; test mocks of table I/O → Stage 2 Betty expectations |
| AC3 — do_task / agent_data without writing table | N/A — boundary AST-981 |
| AC4 — mandate + Test Bible distinguish table(retired) vs column(live) | Stage 1 (Code Rules + config comment); Stage 2 (Betty bible/tests) |
| AC5 — drop entity columns | N/A — AST-984; plan explicitly rejects rewriting §2.4.1 statute |
| AC6 — keep columns / latest-only | Stage 1 keeps §2.4.1 column contract; Stage 2 retains `append_agent_response` coverage |

### Plan stages → definition

| Stage | Maps to |
| -- | -- |
| Stage 1 — Code Rules ENTITY_TYPES / §2.4.1 label / §3.2 wording + config ENTITY_TYPES comment | Parent Functional scope §3; parent AC4; child AC4; OQ1 keep-columns |
| Stage 2 — Betty bible + component test expectations; engineer test-tree ban | Parent Functional scope §3 (tests/bible); parent AC4; child Notes |
| Build gate — blockedBy AST-982 + ftr ancestor check | Parent child sequencing (#3 after #2) |

## Statute verdicts

| id | verdict | one-line |
| -- | -- | -- |
| astral.agent.confidence-bounds | conforms | Comment-only touch of `config.py`; no confidence math changes |
| astral.config.config-source-of-truth | conforms | ENTITY_TYPES values unchanged; comment split only |
| astral.config.pass-threshold-vs-score-floor | conforms | Scoring thresholds untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env handling changes |
| astral.git.betty-no-src-or-features | conforms | Engineer edits Code Rules + config comment; Betty owns test/bible rows |
| astral.git.engineer-test-tree-ban | conforms | Stage 2 forbids engineer commits to `tests/` / bible; `[qa-handoff]` path stated |
| astral.layers.import-direction | conforms | No import-graph changes |
| astral.layers.ui-config-driven-business-logic | conforms | No UI behavior changes |
| astral.standards.debug-contract-gated | conforms | No debug-contract edits |
| astral.standards.dry-and-focused-functions | conforms | No new helpers; reuse §2.4.1 column contract |
| astral.standards.in-scope-only | conforms | Explicit out-of-scope: schema, runtime I/O, statutes, historical plans, AST-984 |
| astral.standards.logging-via-utils | conforms | No logging changes |
| astral.standards.no-cross-contamination | conforms | Stays in docs + utils comment |
| astral.standards.no-hardcoded-sets | conforms | No new inline sets |
| astral.standards.public-then-helpers | conforms | No function layout changes |
| astral.standards.utils-data-late-import-only | conforms | Comment-only in config; no utils→data import |
| astral.state.job-prior-states-enforced | conforms | No JOB_STATES edits |
| astral.ui.single-gunicorn-worker | conforms | No gunicorn/start path edits |
| orch.git.betty-merge-tests-one-sha | conforms | No merge-tests work in this plan |
| orch.git.commit-vocabulary | conforms | Normal engineer commits on publish-ref |
| orch.git.flow-direction-inviolable | conforms | Child `sub/AST-975/...` per parent Git table |
| orch.git.ftr-sub-topology | conforms | Publish ref matches parent Git table |
| orch.git.merge-on-checkout | conforms | Build gate requires ftr merge before Stage 1 |
| orch.git.no-cherry-pick-rebase-force | conforms | No cherry-pick/rebase/force instructed |
| orch.git.no-dev-agent-branches | conforms | Uses `sub/` publish-ref |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree AST-975 |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | OQ1 already answered keep-columns-until-984 |
| orch.pipeline.plan-is-bible | conforms | Concrete Stage 1 edits + Stage 2 Betty inventory |
| orch.pipeline.project-scoped-queues | conforms | Single-child scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate path |
| orch.roles.archie-approves-statutes | conforms | Explicitly does not edit `canon/statutes/**` |
| orch.roles.betty-owns-test-tree | conforms | Stage 2 is Betty qa-child expectations |
| orch.roles.chuckles-never-ticket-assignee | conforms | Implementer is Katherine |
| orch.roles.engineer-assignee-through-resolve | conforms | Returns to Katherine on Plan Approved |
| orch.roles.pre-commit-path-bans | conforms | Engineer path avoids banned test-tree paths |

## Considered and excluded

**Considered:** astral.agent.confidence-bounds; astral.config.config-source-of-truth; astral.config.pass-threshold-vs-score-floor; astral.config.secrets-and-env-specific-from-environ; astral.git.betty-no-src-or-features; astral.git.engineer-test-tree-ban; astral.layers.import-direction; astral.layers.ui-config-driven-business-logic; astral.standards.debug-contract-gated; astral.standards.dry-and-focused-functions; astral.standards.in-scope-only; astral.standards.logging-via-utils; astral.standards.no-cross-contamination; astral.standards.no-hardcoded-sets; astral.standards.public-then-helpers; astral.standards.utils-data-late-import-only; astral.state.job-prior-states-enforced; astral.ui.single-gunicorn-worker; orch.git.betty-merge-tests-one-sha; orch.git.commit-vocabulary; orch.git.flow-direction-inviolable; orch.git.ftr-sub-topology; orch.git.merge-on-checkout; orch.git.no-cherry-pick-rebase-force; orch.git.no-dev-agent-branches; orch.git.one-epic-worktree-per-parent; orch.git.three-permanent-branches; orch.pipeline.call-susan-for-product-decisions; orch.pipeline.plan-is-bible; orch.pipeline.project-scoped-queues; orch.pipeline.status-gates-skill-entry; orch.roles.archie-approves-statutes; orch.roles.betty-owns-test-tree; orch.roles.chuckles-never-ticket-assignee; orch.roles.engineer-assignee-through-resolve; orch.roles.pre-commit-path-bans

**Excluded:**
- astral.agent.do-task-delegation — layers/paths miss
- astral.agent.grade-vector-validation — layers/paths miss
- astral.batch.batch-id-first — layers/paths miss
- astral.batch.batch-id-format — layers/paths miss
- astral.batch.claim-process-release — layers/paths miss
- astral.batch.entity-agent-responses-latest-only — layers/paths miss (R6 still checks §2.4.1 keep)
- astral.debug.no-repo-root-artifacts-dir — paths miss
- astral.debug.spikes-under-debug-dir — paths miss
- astral.docs.features-single-file-per-ticket — paths miss (`docs/features/**` not in Files Changed)
- astral.layers.core-vs-external-bright-line — layers/paths miss
- astral.layers.scripts-exempt-from-layer-rules — layers/paths miss
- astral.patterns.coat-check-never-store-empty — layers/paths miss
- astral.patterns.render-verdict-orchestrates-consult — layers/paths miss
- astral.patterns.require-auth-on-protected-endpoints — layers/paths miss
- astral.standards.data-raises-caller-logs — layers miss
- astral.standards.database-header-inventory — layers/paths miss
- astral.state.core-decides-transitions — layers/paths miss
- astral.state.no-daisy-chain-in-run — layers/paths miss
- astral.ui.frontend-file-placement — layers/paths miss
- astral.ui.naming-conventions — layers/paths miss

## Findings

None fix-now.

- **acceptable** — Files Changed lists Betty `tests/` / bible rows while Stages forbid engineer commits there; ownership split is explicit and matches `orch.roles.betty-owns-test-tree` / engineer-test-tree-ban.
- **acceptable** — Monolith `docs/ASTRAL_TEST_BIBLE.md` not in Stage 2 inventory; active decomposed `docs/test-bible/**` is listed; parent AC4 “Test Bible” satisfied via Betty checklist.
- **acceptable** — Self-assessment Scope minor / Conf high / Risk low matches comment-only engineer path.

## R6 checklist (summary)

Definition fidelity: AC4 prose split only; §2.4.1 column contract preserved for AST-984. Layers: docs + utils comment. Config: comment-only. Placement: no new files. Patterns: latest-only language kept. DRY/scope: siblings named; statutes untouched. Self-assessment: honest.

context_tokens≈95000

— Joan

#### katherine — 2026-07-25T18:57:53.791Z
Plan: [docs/features/foundation/ast-983-docs-bible-test-sweep-agent-responses.md](https://github.com/susansomerset/astral/blob/sub/AST-975/AST-983-docs-bible-test-sweep-agent-responses/docs/features/foundation/ast-983-docs-bible-test-sweep-agent-responses.md) on `origin/sub/AST-975/AST-983-docs-bible-test-sweep-agent-responses` @ `4f07422`.

**Scope — minor:** Engineer path is Code Rules + `config.py` ENTITY_TYPES comment only; bible/`tests/` cleanup listed as Betty qa-child expectations (engineer test-tree ban).

**Conf — high:** Parent AC 4 + OQ1 already decide table-retired / columns-live-until-AST-984; sibling ownership (981 write-stop, 982 schema drop, 984 column retirement) is unambiguous.

**Risk — low:** Mandate/comment wording on the engineer path; wrong rewrite of §2.4.1 column contract is explicitly rejected in-plan as AST-984 scope.

---

# AST-983: Docs, bible, and test sweep for agent_responses table retirement

**Linear:** [AST-983](https://linear.app/astralcareermatch/issue/AST-983/docs-bible-and-test-sweep-for-agent-responses-table-retirement)  
**Parent:** [AST-975](https://linear.app/astralcareermatch/issue/AST-975/decommission-table-agent-responses) — Decommission table AGENT_RESPONSES  
**Publish ref:** `origin/sub/AST-975/AST-983-docs-bible-test-sweep-agent-responses`

After AST-981 (stop writing the standalone table) and AST-982 (drop schema), mandate prose, config comments, Test Bible language, and component tests still conflate the retired standalone `agent_responses` **table** with the live entity-row `agent_responses` JSON **columns**. This ticket updates engineer-owned mandate/config comments so inventory language matches reality, and specifies Betty’s bible/test cleanup so nothing still assumes the standalone table exists — without touching entity-column contract language that AST-984 will retire later.

## UAT fitness

- **AC restored:** Parent AST-975 AC 4 — “Mandate docs and Test Bible text no longer list the standalone `agent_responses` table as live inventory; if entity columns remain, prose clearly distinguishes **table (retired)** vs **entity JSON column (live)**.” Child AST-983 AC matches that sentence (entity columns remain until AST-984).
- **Correct outcome:** A reader of Code Rules / config comments / Test Bible sees the standalone table as **retired**, and entity-row `agent_responses` JSON columns as **still live** (latest-only refs into `agent_data`) until the column-retirement sibling lands. Component tests no longer mock or require `add_agent_response_entry` after AST-981 removes that call site.
- **Sibling check:** AST-981 removes runtime/script writes to the standalone table (including `add_agent_response_entry` usage). AST-982 removes table create/ensure/inventory from the data layer. AST-984 (later) drops entity columns and revises §2.4.1 / statute — **out of this plan**. Verify after merging `origin/ftr/AST-975-decommission-table-agent-responses` that 981+982 tips are present before editing prose that claims the table is gone.
- **Not sufficient:** Removing the stacktrace / exception / 5xx alone is **not** done. (N/A as runtime symptom — this ticket is docs/test inventory honesty.)
- **Wrong fix rejected:** Deleting or rewriting §2.4.1 / `astral.batch.entity-agent-responses-latest-only` / `pattern.batch.entity-agent-responses` to drop entity-column language — that is AST-984. Also rejected: engineer commits under `tests/` or `docs/test-bible/**` (Betty owns those; pre-commit bans engineer edits).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `docs/ASTRAL_CODE_RULES.md` | Split ENTITY_TYPES bullet and §2.4.1 / layer-rules mentions so standalone **table** is retired and entity JSON **column** stays live | docs |
| `src/utils/config.py` | ENTITY_TYPES comment: same table-vs-column split | utils |
| `docs/test-bible/data/database/agent_responses.md` | Betty at qa-child: title/body state entity-column upsert scope; note standalone table retired (AST-975) | bible (Betty) |
| `docs/test-bible/core/roster.md` | Betty at qa-child: only if prose still implies a live standalone table (entity-column refs stay) | bible (Betty) |
| `docs/test-bible/dev/backfill_latest_only_rubric_entity_data.md` | Betty at qa-child: same — entity-column backfill language only | bible (Betty) |
| `tests/component/core/test_agent.py` | Betty at qa-child: remove `add_agent_response_entry` monkeypatches / imports after AST-981 deletes the product call | tests (Betty) |
| `tests/component/data/database/test_agent_responses.py` | Betty at qa-child: keep entity-column `append_agent_response` coverage; drop any cases that exercise the standalone table / `add_agent_response_entry` / `_ensure_agent_responses_schema` | tests (Betty) |

**Explicitly not in this ticket:** `src/data/database.py` schema/API (AST-982), runtime call sites (AST-981), entity-column DDL or §2.4.1 statute retirement (AST-984), historical feature plan docs under `docs/features/**` (leave as archaeology), `canon/statutes/**` / `canon/patterns/**` entity-column entries (still correct until AST-984).

**Build gate:** Linear `blockedBy` AST-982. Before Stage 1, merge `origin/ftr/AST-975-decommission-table-agent-responses` (and confirm AST-981 + AST-982 commits are ancestors). If ftr still creates/writes the standalone table, **stop** and comment on AST-983 — do not claim retirement in mandate prose while siblings are unfinished.

## Stage 1: Mandate + config comment split

**Done when:** `docs/ASTRAL_CODE_RULES.md` and `src/utils/config.py` no longer list the standalone `agent_responses` table as live inventory, and every remaining `agent_responses` mention in those two files is explicitly the entity JSON column (or clearly labeled pending AST-984). Grep of those two files for `agent_responses` shows no “table inventory” framing.

1. In `docs/ASTRAL_CODE_RULES.md`, locate the **ENTITY_TYPES** bullet under the config inventory (currently: “Single source of truth used across `agent_data`, `dispatch_ledger`, `agent_responses`, and config”). Replace so it names **entity-row `agent_responses` JSON columns** (company / job / candidate), not a table, and add a short clause that the standalone `agent_responses` **table** is retired (AST-975).

2. In the same file, §2.4.1 **Entity Agent Responses**: keep the latest-only entity-column contract unchanged. Immediately under the section heading (before “Every entity table…”), add one sentence: the standalone `agent_responses` **table** is retired; this section describes only the entity-row JSON **column** (live until AST-984). Do **not** delete the JSON example, `prompt_blocks` / `agent_data` FK language, or the statute id line.

3. In the same file, §3.2 / External layer paragraph that lists “data-layer interactions (agent_data, agent_responses, prompt resolution)”: reword `agent_responses` to **entity-row `agent_responses` refs** (or equivalent) so it cannot be read as the retired table.

4. In `src/utils/config.py`, update the `ENTITY_TYPES` comment block (the three lines above `ENTITY_TYPES = [...]`) to the same table-retired / column-live split as step 1. Do not change the `ENTITY_TYPES` list values.

5. Repo grep (engineer verification only — do not edit Betty trees):  
   `rg -n 'agent_responses' docs/ASTRAL_CODE_RULES.md src/utils/config.py`  
   Confirm every hit is column-scoped or explicitly marks the table retired. If a hit still treats the standalone table as live inventory, fix it in this stage.

⚠️ **Decision:** Engineer edits stop at Code Rules + `config.py` comments. Bible and `tests/` cleanup are Betty’s at **qa-child** (see Stage 2 expectations). Historical plans and entity-column statutes stay until AST-984.

## Stage 2: Betty expectations (no engineer commits)

**Done when:** This stage’s checklist is written into the plan (already below) so Betty’s qa-child pass has a concrete inventory; engineer does **not** create commits under `tests/`, `docs/test-bible/**`, or `docs/ASTRAL_TEST_BIBLE.md`.

1. At **Code Complete**, Betty owns:
   - `docs/test-bible/data/database/agent_responses.md` — scope line must say **entity JSON column** / `append_agent_response` upsert; add one line that the standalone table is retired (AST-975). Keep AST-726 upsert nodeids that still apply.
   - Cross-links in `docs/test-bible/core/roster.md`, `docs/test-bible/core/consult.md`, `docs/test-bible/dev/backfill_latest_only_rubric_entity_data.md` — only amend wording that implies a live standalone table; leave entity-column / dedupe stories intact.
   - `tests/component/core/test_agent.py` — after AST-981 removes `add_agent_response_entry` from `src/core/agent.py`, delete every `monkeypatch.setattr(..., "add_agent_response_entry", ...)` and any import/assert that requires that symbol. Prefer deleting dead mocks over rewiring them to a no-op.
   - `tests/component/data/database/test_agent_responses.py` — retain entity-column upsert coverage; remove cases that call `add_agent_response_entry`, `_ensure_agent_responses_schema`, or otherwise assert the standalone table exists.

2. Engineer must not patch those files if tests fail after merge — post `[qa-handoff]` and assign Betty (stay Tests Ready).

## Self-Assessment

- **Scope:** `minor` — two engineer files (Code Rules + config comment); Betty trees listed as expectations only.
- **Conf:** `high` — AC is a prose split already decided by parent OQ1 (keep columns until AST-984); sibling ownership is clear.
- **Risk:** `low` — comment/mandate wording only on the engineer path; wrong column-mandate edit would be caught by Joan/Radia and by AST-984’s later mandate change.

## Code Rules self-review

| Rule | Check |
|------|-------|
| §1.3 DRY | No new helpers; reuse existing §2.4.1 column contract. |
| §2.1 config | Comment-only change to `ENTITY_TYPES` block; no new config keys. |
| §2.4 / §2.4.1 | Column contract preserved; table marked retired only. |
| §2.6 state machine | Untouched. |
| §3.3 imports | Untouched. |
| §3.5 naming | Untouched. |
| Engineer test-tree ban | Stages forbid engineer commits to `tests/` / bible. |

## Review

**Branch:** `sub/AST-975/AST-983-docs-bible-test-sweep-agent-responses`
**Build tip:** `0bcb4e5`
**Notes:** Stage 1 mandate/config comment split only; Betty owns bible/tests at qa-child (Stage 2).

## Radia review (code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-983
**Publish ref tip (pre-docs):** `abc6d2ca8c303fe488fe8b7d43c246b3cd6a73b9`
**Overall:** DISCUSS

### What’s solid

- Stage 1: Code Rules ENTITY_TYPES / §2.4.1 label / §3.2 external wording + `config.py` ENTITY_TYPES comment split table(retired) vs entity JSON column(live until AST-984); column contract body kept.
- Stage 2 Betty: bible prose updated (`agent_responses.md` title/scope + cross-links); prior AST-981/982 test cleanup reused; one `merge-tests(AST-983)` of `19e8e97`.
- rg on mandate/config: every `agent_responses` hit is column-scoped or marks table retired.
- Engineer path avoided `tests/` / `docs/test-bible/**`.

### Issues

**discuss (C4 straggler):** Joan Excluded 16 statutes that this three-dot scores in-scope because `origin/dev...publish-ref` still carries AST-981/982 ancestor paths (`src/core/**`, `src/data/**`, `scripts/**`, `docs/features/**`). Substance for all is **conforms**. No product fix expected.

**advisory:** Plan Review stub tip was mangled (`"'76d4979'"`) — cosmetic only; real tip is publish-ref HEAD.

### Recommended actions

1. Acknowledge C4 stragglers at resolve-child (no code).
2. AST-984 owns entity-column retirement + §2.4.1 / statute rewrite.

### Pattern conformance

none cited

### Plan adherence

Self-Assessment Scope `minor` matches engineer delta (Code Rules + config comment + plan stub). Sibling boundaries held.

## Resolution

**Date:** 2026-07-25  
**Publish rebuild:** Clean stack on `origin/ftr/AST-975-decommission-table-agent-responses` (dropped polluted `merge origin/dev` history that carried `Merge remote-tracking branch` into `sub --not ftr`).

| Finding | Action |
|---------|--------|
| **discuss (C4 straggler)** — 16 Joan-excluded statutes in-scope only via AST-981/982 ancestors vs `origin/dev` | Acknowledged. Substance **conforms**; no product change. |
| **advisory** — mangled Review stub tip | Fixed Build tip to `0bcb4e5` (code commit on rebuilt stack). |

No fix-now items. AST-984 remains owner of entity-column retirement + statute rewrite.

