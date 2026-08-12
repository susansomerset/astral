<!-- linear-archive: AST-1120 archived 2026-08-11 -->

## Linear archive (AST-1120)

**Archived:** 2026-08-11  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1120/uuid-from-job-link-company-job-id-fallback-before-qualify-empty-id  
**Status at archive:** Archive  
**Project:** Astral Tracker  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1119 — Fallback for company job id  
**Blocked by / blocks / related:** parent: AST-1119; blocks: AST-1121

### Description

## What this implements

Owns resolve rule (AI wins; else UUID path segment from `job_link`; else empty) and wires it immediately before the `qualify_meteorite` empty-`company_job_id` content gate only. Does **not** own create-time meteorite ingest that leaves id empty; does **not** use `job_site`.

## Acceptance criteria

- [X] 1. Non-empty AI `company_job_id` is recorded unchanged even when `job_link` contains a different UUID path segment.
- [X] 2. Empty/missing AI `company_job_id` + `job_link` containing a UUID path segment (e.g. Dice `…/company-profile/<uuid>` or a job URL with a UUID segment) records that UUID as `company_job_id` and does not hit the empty-id fail gate.
- [X] 3. Empty/missing AI id + `job_link` with no UUID path segment still fails the empty-id gate (same fail kind as today).
- [X] 4. Meteorite create-without-`company_job_id` behavior outside the agreed qualify apply surface is unchanged.

## Boundaries

- [X] Does not own debug found/recorded instrumentation (sibling AST-1121).
- [X] Does not change meteorite create paths.
- [X] Does not use `job_site`.
- [X] Does not expand to `qualify_job_listings`.

## In scope

- [X] `pattern.batch.entity-claim-process-release` — fallback inside existing qualify claim/process/release apply
- [X] `pattern.batch.entity-agent-responses` — AI value from latest RESPONSE decode; fallback is post-decode apply only
- [X] `pattern.identity.url-uuid-path-external-id-fallback` (proposed) — prefer AI, else UUID path segment from `job_link`, else fail; introduced here for Archie approval before reuse
- [X] `astral.standards.no-hardcoded-sets` — UUID shape via `TRACKER_CONFIG["uuid_path_segment_pattern"]`, not host allowlists
- [X] `astral.standards.in-scope-only` — agreed qualify empty-id gate + resolve helper only
- [X] `astral.standards.dry-and-focused-functions` / `astral.standards.public-then-helpers` — one resolve helper + pure extract helper
- [X] `astral.layers.import-direction` — `consult` → `utils`; `formatting` stays pure (pattern passed as arg)
- [X] `astral.config.config-source-of-truth` — UUID regex literal in `TRACKER_CONFIG`
- [X] `astral.batch.claim-process-release` / `astral.batch.entity-agent-responses-latest-only` — no reinvent claim or RESPONSE storage

## Considered but excluded

- [X] `astral.standards.debug-contract-gated` — Style D found/recorded source logging is AST-1121 only; this ticket does not add source labels
- [X] Meteorite create / gazer ingest leaving `company_job_id` empty — intentional pre-qualify carve-out (AST-1061 / AST-1090); out of apply surface
- [X] `qualify_job_listings` — no empty-`company_job_id` content fail gate today; parent forbids expansion
- [X] Company `job_site` / non-`job_link` URLs — id must stay unique to the job
- [X] Arbitrary last path segment / query junk — UUID-shaped path token only (dedupe safety)
- [X] UI or prompt rewrites as primary fix — out of epic Boundaries

## Notes for planning

Quick-fix epic: wire only at `qualify_meteorite` content gate. Prefer AI `company_job_id`; else UUID-shaped path segment from `job_link`.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1119-fallback-for-company-job-id`, child `sub/AST-1119/AST-1120-uuid-from-job-link-company-job-id-fallback`. Created at dispatch-parent.

### Comments

#### radia — 2026-08-02T17:27:27.690Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1120
**Publish ref:** `origin/sub/AST-1119/AST-1120-uuid-from-job-link-company-job-id-fallback` @ `ab463454`
**Overall:** DISCUSS

Diff baseline: `origin/dev...origin/sub/AST-1119/AST-1120-uuid-from-job-link-company-job-id-fallback` — layers `{core, docs, utils}`; change_types `{add, modify}`.

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | conforms | no confidence/grade bound changes |
| `astral.agent.do-task-delegation` | scoped | conforms | no new do_task; post-decode apply only |
| `astral.agent.grade-vector-validation` | scoped | conforms | no graded-task changes |
| `astral.batch.batch-id-first` | scoped | conforms | no new claim/batch_id helpers |
| `astral.batch.batch-id-format` | scoped | conforms | batch_id untouched |
| `astral.batch.claim-process-release` | scoped | conforms | fallback inside existing qualify process |
| `astral.batch.entity-agent-responses-latest-only` | scoped | conforms | AI from RESPONSE decode; fallback post-decode |
| `astral.config.config-source-of-truth` | scoped | conforms | UUID regex in TRACKER_CONFIG |
| `astral.config.pass-threshold-vs-score-floor` | scoped | conforms | thresholds untouched |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | conforms | no secrets/env reads added |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | paths no match among ['artifacts/**', 'scripts/spikes/**'] |
| `astral.debug.spikes-under-debug-dir` | scoped | conforms | docs/features plan only; not spike notes |
| `astral.dispatch.run-next-is-chain-authority` | scoped | conforms | no run_next/dispatch chain edits |
| `astral.dispatch.seed-auto-false` | scoped | conforms | no seed/dispatch_task rows |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | single docs/features/tracker/ast-1120-….md |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty commits only tests/bible; merge-tests ok |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | tests/bible only in test()+merge-tests commits |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | no external I/O; utils extract only |
| `astral.layers.import-direction` | scoped | conforms | consult→utils; formatting has no config import |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | layers ['scripts'] ∩ diff ['core', 'docs', 'utils'] empty |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | TRACKER_CONFIG literal; no UI rule surface |
| `astral.patterns.coat-check-never-store-empty` | scoped | conforms | coat-check paths untouched |
| `astral.patterns.render-verdict-orchestrates-consult` | scoped | conforms | wire is qualify_meteorite process only |
| `astral.patterns.require-auth-on-protected-endpoints` | scoped | not-applicable | layers ['ui'] ∩ diff ['core', 'docs', 'utils'] empty |
| `astral.seed.agent-tables-in-repo-json` | scoped | conforms | no seed JSON |
| `astral.seed.archie-catalog-wins` | scoped | conforms | no catalog edits |
| `astral.seed.boot-only-not-hot-path` | scoped | conforms | resolve is apply logic not seed/boot |
| `astral.seed.define-approved` | scoped | conforms | no seed define |
| `astral.seed.operator-rows-stay-deleted` | scoped | conforms | untouched |
| `astral.seed.other-via-coverage-join` | scoped | conforms | untouched |
| `astral.standards.data-raises-caller-logs` | scoped | conforms | no data-layer edits |
| `astral.standards.database-header-inventory` | scoped | not-applicable | layers ['data'] ∩ diff ['core', 'docs', 'utils'] empty |
| `astral.standards.debug-contract-gated` | scoped | conforms | no new debug emission; source labels are AST-1121 |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | one resolve helper + one pure extract |
| `astral.standards.in-scope-only` | scoped | conforms | qualify empty-id gate + helpers only |
| `astral.standards.logging-via-utils` | scoped | conforms | no new logging framework; get_logger unchanged |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | domain helper/key names; ticket only in comments |
| `astral.standards.no-cross-contamination` | scoped | conforms | stays core/utils apply surface |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | UUID shape via TRACKER_CONFIG; no host allowlist |
| `astral.standards.public-then-helpers` | scoped | conforms | helper clustered with existing privates after qualify_meteorite |
| `astral.standards.utils-data-late-import-only` | scoped | conforms | formatting pure; no data import |
| `astral.state.core-decides-transitions` | scoped | conforms | same fail_state/pass_state; no new states |
| `astral.state.job-prior-states-enforced` | scoped | conforms | prior_states untouched |
| `astral.state.no-daisy-chain-in-run` | scoped | conforms | no daisy-chain invent |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | layers ['ui'] ∩ diff ['core', 'docs', 'utils'] empty |
| `astral.ui.naming-conventions` | scoped | not-applicable | layers ['ui'] ∩ diff ['core', 'docs', 'utils'] empty |
| `astral.ui.single-gunicorn-worker` | scoped | conforms | no worker/deployment changes |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | one merge-tests(AST-1120) on sub tip |
| `orch.git.commit-vocabulary` | universal | conforms | docs/code/test/merge-tests vocabulary only |
| `orch.git.flow-direction-inviolable` | universal | conforms | publish stays on origin/sub child ref |
| `orch.git.ftr-sub-topology` | universal | conforms | sub/AST-1119/AST-1120-… matches parent Git table |
| `orch.git.merge-on-checkout` | universal | conforms | no illegal merge recipe in tip commits |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | linear commits; no cherry-pick/rebase/force |
| `orch.git.no-dev-agent-branches` | universal | conforms | child publish-ref is sub/… not agent-named |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | review in astral-AST-1119 epic worktree |
| `orch.git.three-permanent-branches` | universal | conforms | no new permanent branch |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | AI-first/UUID-path decisions already in plan |
| `orch.pipeline.plan-is-bible` | universal | conforms | stages + Files Changed match tip |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Tracker child AST-1120 only |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Tests Passed → review-child |
| `orch.roles.archie-approves-statutes` | universal | conforms | no canon/statutes edits |
| `orch.roles.betty-owns-test-tree` | universal | conforms | tests/bible via test()+merge-tests only |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | assignee remains Ada |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Ada stays assignee through Tests Passed |
| `orch.roles.pre-commit-path-bans` | universal | conforms | no banned path edits in product commits |

## Pattern conformance

| pattern | verdict |
|---------|---------|
| `pattern.batch.entity-claim-process-release` | conforms — fallback inside existing qualify claim/process/release |
| `pattern.batch.entity-agent-responses` | conforms — AI from latest RESPONSE decode; fallback post-decode apply |
| `pattern.identity.url-uuid-path-external-id-fallback` (proposed) | conforms — AI wins; else UUID path segment from `job_link`; else empty |

## Plan adherence

Stages 1–2 match tip: `TRACKER_CONFIG["uuid_path_segment_pattern"]`, pure `uuid_path_segment_from_url`, `_resolve_company_job_id` wired immediately before the empty-`company_job_id` gate with `link_for_id = response job_link or input job_link`. Self-Assessment Scope `Single-Component` matches footprint. Boundaries held (no AST-1121 source labels, no create/`job_site`/`qualify_job_listings`). Joan discuss on helper placement: implementation clusters with existing privates after `qualify_meteorite` (publics-first for this insert).

## Findings

**fix-now:** none

**discuss (C4 straggler — excluded at plan time but in-scope on tip vs `origin/dev`):**
1. `astral.debug.spikes-under-debug-dir` — plan file under `docs/features/**`; scored conforms (not spike notes).
2. `astral.docs.features-single-file-per-ticket` — same plan path; scored conforms (single file).
3. `astral.git.engineer-test-tree-ban` — `tests/**` + bible via Betty `test()`/`merge-tests`; scored conforms.

No product code action required for stragglers.

## What's solid

AI-never-overwrite, path-segment-only UUID fullmatch from config, formatting stays config-free, qualify-only apply surface, one `merge-tests` SHA.

## Recommended actions

Resolve-child can proceed without product edits for these discuss items. AST-1121 still owns Style D found/recorded source labels.

**Notes:** Joan plan-rubric verdict attached (APPROVED). Active statute count checked: 65.

context_tokens≈52000

#### betty — 2026-08-02T17:24:32.962Z
1. `tests/component/core/test_consult.py::TestAst1120CompanyJobIdFallback` — AC1 AI wins over different UUID in `job_link`; AC2 empty AI + Dice UUID path → pass + recorded UUID; AC3 empty AI + no UUID → `empty company_job_id` fail; `_resolve_company_job_id` helper branches + `link_for_id` input fallback composition.
2. `tests/component/utils/test_formatting.py::TestUuidPathSegmentFromUrl` — empty URL; Dice rightmost UUID; multi-UUID rightmost; query/fragment ignored; percent-decode + case preserved.
3. `tests/component/utils/test_config.py::TestAst1120UuidPathSegmentPattern` — `TRACKER_CONFIG["uuid_path_segment_pattern"]` anchored fullmatch.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_consult.py::TestAst1120CompanyJobIdFallback \
  tests/component/utils/test_formatting.py::TestUuidPathSegmentFromUrl \
  tests/component/utils/test_config.py::TestAst1120UuidPathSegmentPattern \
  -q
```

**Broken / obsolete:** none — existing AST-1062 empty-id gate case still uses a non-UUID `job_link`.

**Integration:** no existing scenarios assert qualify empty-id / company_job_id resolve — none revised.

**Publish:** `origin/sub/AST-1119/AST-1120-uuid-from-job-link-company-job-id-fallback` @ `bea30019` (`merge-tests(AST-1120): origin/tests ea4716e7`).

**Bible shasums on publish tip:**
- `docs/test-bible/core/consult.md` `8836932387b00abba469f99168aa84d4d634e597`
- `docs/test-bible/utils/formatting.md` `68df4340b1d737a40780f83530060d3b769276df`
- `docs/test-bible/utils/config.md` `26cee476852eaaf3fa1a3d4c5928c8b0df66fdc6`

— Betty

#### joan — 2026-08-02T17:17:16.754Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1120
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 Non-empty AI `company_job_id` recorded unchanged | Stage 2 — `_resolve_company_job_id` returns AI immediately |
| AC2 Empty AI + UUID path segment in `job_link` records UUID; skips empty-id fail | Stage 1 extract + Stage 2 wire before empty-id gate |
| AC3 Empty AI + no UUID still empty-id fail | Stage 2 — resolve returns `""`; existing `fail_reason = "empty company_job_id"` |
| AC4 debug=True found source / recorded Style D | N/A — boundary (AST-1121); plan forbids source labels |
| AC5 Meteorite create-without-id outside qualify surface unchanged | Stage 2 Decision — no create / gazer / `qualify_job_listings` edits |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 TRACKER_CONFIG pattern + `uuid_path_segment_from_url` | Purpose/Functional scope UUID-from-`job_link`; `no-hardcoded-sets` / config SoT |
| Stage 2 `_resolve_company_job_id` + wire before `qualify_meteorite` empty-id gate | Functional scope apply surface; proposed `pattern.identity.url-uuid-path-external-id-fallback`; child AC1–3/5 |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work |
| orch.git.commit-vocabulary | conforms | Sub publish / plan vocabulary only |
| orch.git.flow-direction-inviolable | conforms | Publish to origin/sub only |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | No illegal merge recipe |
| orch.git.no-cherry-pick-rebase-force | conforms | None proposed |
| orch.git.no-dev-agent-branches | conforms | Uses sub/AST-1119/AST-1120-… |
| orch.git.one-epic-worktree-per-parent | conforms | astral-AST-1119 epic worktree |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Decisions documented; open questions none |
| orch.pipeline.plan-is-bible | conforms | Binding stages + Files Changed |
| orch.pipeline.project-scoped-queues | conforms | Single-child Tracker scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate only |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | No tests/bible edits |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Ada) implements |
| orch.roles.engineer-assignee-through-resolve | conforms | Implementer path after approve |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | No grade/confidence changes |
| astral.agent.do-task-delegation | conforms | No new do_task; post-decode apply only |
| astral.agent.grade-vector-validation | conforms | No graded-task changes |
| astral.batch.batch-id-first | conforms | No new claim helpers |
| astral.batch.batch-id-format | conforms | No batch_id invent |
| astral.batch.claim-process-release | conforms | Fallback inside existing qualify process |
| astral.batch.entity-agent-responses-latest-only | conforms | AI from RESPONSE decode; fallback post-decode |
| astral.config.config-source-of-truth | conforms | UUID regex in TRACKER_CONFIG |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env |
| astral.dispatch.run-next-is-chain-authority | conforms | No dispatch chain edits |
| astral.dispatch.seed-auto-false | conforms | No seed/dispatch_task rows |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src |
| astral.layers.core-vs-external-bright-line | conforms | No external I/O changes |
| astral.layers.import-direction | conforms | consult→utils; formatting pure (pattern arg) |
| astral.layers.ui-config-driven-business-logic | conforms | TRACKER_CONFIG literal only; no React UI rules |
| astral.patterns.coat-check-never-store-empty | conforms | Untouched |
| astral.patterns.render-verdict-orchestrates-consult | conforms | Wire is qualify_meteorite process, not new orchestrator |
| astral.seed.agent-tables-in-repo-json | conforms | No seed JSON |
| astral.seed.archie-catalog-wins | conforms | No catalog edits |
| astral.seed.boot-only-not-hot-path | conforms | Hot-path resolve is apply logic, not seed |
| astral.seed.define-approved | conforms | No seed define |
| astral.seed.operator-rows-stay-deleted | conforms | Untouched |
| astral.seed.other-via-coverage-join | conforms | Untouched |
| astral.standards.data-raises-caller-logs | conforms | No data-layer edits |
| astral.standards.debug-contract-gated | conforms | Found/recorded source logging deferred to AST-1121 per parent split |
| astral.standards.dry-and-focused-functions | conforms | One resolve + one extract helper |
| astral.standards.in-scope-only | conforms | qualify_meteorite empty-id gate + helpers only |
| astral.standards.logging-via-utils | conforms | No new logging framework; no source labels |
| astral.standards.names-not-ticket-ids | conforms | Keys/helpers named by domain, not ticket id |
| astral.standards.no-cross-contamination | conforms | Stays core/utils |
| astral.standards.no-hardcoded-sets | conforms | UUID shape via TRACKER_CONFIG; no host allowlist |
| astral.standards.public-then-helpers | conforms | Helper grouped with existing private helpers; publics remain primary API |
| astral.standards.utils-data-late-import-only | conforms | formatting stays pure; no data import |
| astral.state.core-decides-transitions | conforms | Same fail_state/pass_state; no new states |
| astral.state.job-prior-states-enforced | conforms | Untouched prior_states |
| astral.state.no-daisy-chain-in-run | conforms | No daisy-chain invent |
| astral.ui.single-gunicorn-worker | conforms | No worker/deployment changes |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.dispatch.run-next-is-chain-authority, astral.dispatch.seed-auto-false, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.seed.agent-tables-in-repo-json, astral.seed.archie-catalog-wins, astral.seed.boot-only-not-hot-path, astral.seed.define-approved, astral.seed.operator-rows-stay-deleted, astral.seed.other-via-coverage-join, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.names-not-ticket-ids, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths match none of plan paths
- astral.debug.spikes-under-debug-dir — paths match none of plan paths
- astral.docs.features-single-file-per-ticket — layers {docs} ∩ plan {core,utils} empty
- astral.git.engineer-test-tree-ban — paths match none of plan paths
- astral.layers.scripts-exempt-from-layer-rules — layers ∩ plan empty
- astral.patterns.require-auth-on-protected-endpoints — layers {ui} ∩ plan empty
- astral.standards.database-header-inventory — layers {data} ∩ plan empty
- astral.ui.frontend-file-placement — layers {ui} ∩ plan empty
- astral.ui.naming-conventions — layers {ui} ∩ plan empty

## Findings

None fix-now.

**discuss (non-blocking):** Stage 2 says place `_resolve_company_job_id` “near other private helpers above `qualify_meteorite`” while also claiming publics-first. Match the file’s existing helper cluster; do not invent a new helpers-before-publics layout if the file already keeps publics first.

**acceptable:** Scope Single-Component / Conf high / Risk Medium honest; AI-never-overwrite + path-segment fullmatch + create-path freeze mitigate Medium risk. Parent AC4 correctly left to AST-1121.

**R6:** Definition fidelity pass for child #1 resolve+wire. Layer/import pass. Config SoT pass. No create/`job_site`/`qualify_job_listings` creep. DRY pass.

context_tokens≈45000

— Joan

#### chuckles — 2026-08-02T17:15:37.994Z
[thread-orphan] Joan session `da0027e7-276d-4fe2-a6e6-65c8eb77e24d` was under wrong workspace hash; relocated `/home/susan/.cursor/chats/0f41bf986cfef9e06ea903e586d6d4d9/da0027e7-276d-4fe2-a6e6-65c8eb77e24d/store.db` → `/home/susan/.cursor/chats/3b42c17f1227be2507eadeb09fad46b8/da0027e7-276d-4fe2-a6e6-65c8eb77e24d/store.db`. Resuming same UUID.

— Chuckles

#### ada — 2026-08-02T17:15:22.643Z
Plan published on `origin/sub/AST-1119/AST-1120-uuid-from-job-link-company-job-id-fallback` @ `dba469fa`.

**Plan doc:** https://github.com/susansomerset/astral/blob/sub/AST-1119/AST-1120-uuid-from-job-link-company-job-id-fallback/docs/features/tracker/ast-1120-uuid-from-job-link-company-job-id-fallback.md

**Self-assessment**
- **Scope:** `Single-Component` — `TRACKER_CONFIG` UUID regex + pure `formatting.uuid_path_segment_from_url` + `_resolve_company_job_id` wired only at the `qualify_meteorite` empty-id gate.
- **Conf:** `high` — gate/fields already exist; change is AI-first then rightmost UUID path segment before the existing `empty company_job_id` fail.
- **Risk:** `Medium` — a bad overwrite or non-UUID path grab would poison external-id dedupe/identity; mitigated by AI-never-overwrite, path-segment fullmatch from config, and no create-path edits.

AST-1121 still owns Style D found/recorded source logging after this resolve lands.

#### chuckles — 2026-08-02T17:10:33.596Z
[thread-missing] Cursor chat `ab3b5b9a-f89f-48cc-bde1-4eacdaedd5eb` has no local `store.db` on **chuckles** (expected `/home/susan/.cursor/chats/3b42c17f1227be2507eadeb09fad46b8/ab3b5b9a-f89f-48cc-bde1-4eacdaedd5eb/store.db`; blob-search also empty).

Minting a **new** conversation on this host and continuing (history from the old UUID is not recovered). New Ada Team UUID: `d21f66a2-0d74-4041-97bc-0d2a9dd924d5`.

— Chuckles

---

# AST-1120 — UUID-from-job_link company_job_id fallback before qualify empty-id gate

**Linear:** [AST-1120](https://linear.app/astralcareermatch/issue/AST-1120/uuid-from-job-link-company-job-id-fallback-before-qualify-empty-id)
**Parent:** [AST-1119](https://linear.app/astralcareermatch/issue/AST-1119/fallback-for-company-job-id) — Fallback for company job id
**Publish ref:** `origin/sub/AST-1119/AST-1120-uuid-from-job-link-company-job-id-fallback`

When Ruth’s `qualify_meteorite` parse omits `company_job_id`, the empty-id content gate fails even if a UUID-shaped path segment already sits in `job_link`. This ticket owns the resolve rule (AI wins; else UUID path segment from `job_link`; else empty) and wires it immediately before that gate only — so empty-AI + UUID-in-`job_link` jobs can continue to title/link/JD gates and record a stable external id. Does **not** own Style D found/recorded source logging (**AST-1121**), meteorite create paths, `job_site`, or `qualify_job_listings`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `TRACKER_CONFIG["uuid_path_segment_pattern"]` (UUID-shaped full-segment regex) | utils |
| `src/utils/formatting.py` | Add pure `uuid_path_segment_from_url(url, segment_pattern) -> Optional[str]` | utils |
| `src/core/consult.py` | Add `_resolve_company_job_id`; call it in `qualify_meteorite` `process` immediately before the empty-`company_job_id` gate | core |

No `tests/` / bible / React / data / external / meteorite create / `qualify_job_listings` / debug source logging. Do **not** edit AST-1121’s plan or branch.

## Stage 1: Config pattern + pure URL UUID path helper

**Done when:** `TRACKER_CONFIG` exposes a UUID path-segment regex; `formatting.uuid_path_segment_from_url` returns the rightmost matching path segment (or `None`); neither touches consult apply yet.

1. In `src/utils/config.py`, inside `TRACKER_CONFIG` (after `jd_min_chars` / before or after `jd_prune_rules` — keep the block readable; do not invent a second top-level config dict), add:

```python
    # AST-1120: full path-segment match for UUID-shaped external job ids in job_link.
    "uuid_path_segment_pattern": (
        r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
        r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
    ),
```

Assert once near other TRACKER asserts if the file already has them for this block; otherwise add a single module-level assert after `TRACKER_CONFIG`:

```python
assert TRACKER_CONFIG["uuid_path_segment_pattern"].startswith("^")
```

⚠️ **Decision — pattern in `TRACKER_CONFIG`, not a Dice host allowlist:** Parent + `astral.standards.no-hardcoded-sets` require UUID shape via config/shared helper constants, not ad-hoc host lists. No `job_site` / vendor gate in this epic.

2. In `src/utils/formatting.py` (pure utils — **must not** import `config.py`; that module already imports formatting), add:

```python
def uuid_path_segment_from_url(url: str, segment_pattern: str) -> Optional[str]:
    """Return the rightmost path segment that fullmatches segment_pattern, else None."""
```

Concrete behavior (execute literally):

- If `(url or "").strip()` is empty → return `None`.
- `from urllib.parse import urlparse, unquote` (module-level imports preferred if not already present).
- `parsed = urlparse(url.strip())`.
- Split `parsed.path` on `/`; skip empty segments.
- Walk segments **right-to-left**; for each, `candidate = unquote(segment).strip()`; if `re.fullmatch(segment_pattern, candidate)` → return `candidate` unchanged (do **not** force lowercase).
- Ignore query string and fragment entirely (never scrape `?…` / `#…` for the id).
- If no segment matches → return `None`.
- Invalid / relative URLs: still parse path; if no match → `None` (do not raise).

⚠️ **Decision — rightmost matching path segment:** Dice/profile URLs put the resource UUID as the last path token; when multiple UUID-shaped segments exist, the last is the job/resource id. Query/fragment junk is out of scope for substring dedupe safety.

⚠️ **Decision — pattern passed as argument:** `formatting.py` must stay free of `config` imports; callers pass `TRACKER_CONFIG["uuid_path_segment_pattern"]`.

**Done when (recheck):** `python3 -c` imports `TRACKER_CONFIG["uuid_path_segment_pattern"]` and `uuid_path_segment_from_url`; Dice example `https://www.dice.com/company-profile/9f704ad3-7a18-506a-bd5e-6a84e73b7c00` returns that UUID; a URL with no UUID path segment returns `None`; `python3 -m py_compile` on both files succeeds.

## Stage 2: Resolve helper + wire before qualify_meteorite empty-id gate

**Done when:** Non-empty AI `company_job_id` is never overwritten; empty AI + UUID-in-`job_link` fills `company_job_id` before the empty-id fail; empty AI + no UUID still fails with `fail_reason = "empty company_job_id"`; meteorite create and other gates unchanged.

1. In `src/core/consult.py`, near other private helpers above `qualify_meteorite` (public functions stay first; helpers grouped — §1.3), add:

```python
def _resolve_company_job_id(ai_company_job_id: str, job_link: str) -> str:
    """Prefer non-empty AI company_job_id; else UUID path segment from job_link; else ''."""
```

Concrete body:

- `ai = (ai_company_job_id or "").strip()` — if non-empty, **return `ai` immediately** (do not inspect `job_link`, do not replace with a URL UUID even when different).
- `link = (job_link or "").strip()` — if empty, return `""`.
- `from src.utils.formatting import uuid_path_segment_from_url` (add to existing formatting import at top if preferred).
- `fallback = uuid_path_segment_from_url(link, TRACKER_CONFIG["uuid_path_segment_pattern"])`.
- Return `fallback` if truthy, else `""`.

⚠️ **Decision — one resolve helper in consult, extract pure in formatting:** Introduces proposed `pattern.identity.url-uuid-path-external-id-fallback` on the agreed apply surface without a parallel ingest path. AST-1121 may reuse `_resolve_company_job_id` / `uuid_path_segment_from_url` for source classification; this ticket does **not** add found-source Style D lines.

2. In `qualify_meteorite`’s nested `process(input_job, response_job, cfg)`, **immediately after** the existing strips of `company_job_id` / `job_title` / `job_link` / `jd_text` and **immediately before** `fail_reason = None` / the `if not company_job_id:` empty-id gate, replace the bare AI strip assignment path as follows:

- Keep reading AI fields exactly as today:

```python
company_job_id = (response_job.get("company_job_id") or "").strip()
job_title = (response_job.get("job_title") or "").strip()
job_link = (response_job.get("job_link") or "").strip()
jd_text = (response_job.get("jd_text") or "").strip()
```

- Compute the fallback URL (response link first, else input row link — never company `job_site`):

```python
link_for_id = job_link or (input_job.get("job_link") or "").strip()
company_job_id = _resolve_company_job_id(company_job_id, link_for_id)
```

- Leave the rest of `process` unchanged: empty-id fail still uses `fail_reason = "empty company_job_id"` and the same `cfg["fail_state"]` transition; title / `job_link` http / `jd_text` gates unchanged; success `parsed_job["company_job_id"]` uses the resolved value; existing debug/info lines may show the resolved id (do **not** add AI-vs-UUID source labels — **AST-1121**).

⚠️ **Decision — `link_for_id` = response `job_link` else input `job_link`:** Assemble sends the DB row’s link to Ruth; if the model empties `job_link` while omitting `company_job_id`, the ingest URL still carries the UUID. Never read company `job_site`. Recording of `job_link` on the job row still uses response `job_link` as today (this ticket does not change the link gate or recorded link field).

⚠️ **Decision — wire only in `qualify_meteorite` `process`:** Parent AC + Boundaries: apply surface is the empty-`company_job_id` content gate only. Do not touch `create_meteorite_job`, gazer ingest, or `qualify_job_listings`.

**Done when (recheck):** Manual trace of the three AC paths in `process` logic:

1. AI `company_job_id="abc"` + Dice UUID in link → recorded `"abc"`.
2. AI empty + Dice URL → recorded UUID; does not set `fail_reason = "empty company_job_id"`.
3. AI empty + `https://example.com/jobs/no-uuid-here` → still `empty company_job_id` fail.

`python3 -m py_compile` on `src/core/consult.py` succeeds. No new debug-contract source lines.

## Self-Assessment

**Scope:** `Single-Component` — config literal + one pure formatting helper + one consult resolve helper wired at a single gate in `qualify_meteorite`.

**Conf:** `high` — gate and fields already exist in `consult.qualify_meteorite`; change is a deterministic prefer-AI-else-UUID strip before the existing empty check, reusing claim/process/release unchanged.

**Risk:** `Medium` — wrong UUID selection or overwriting AI ids would poison `company_job_id` substring dedupe and identity triples; mitigated by AI-first rule, path-segment-only UUID fullmatch, and no create-path edits.

## Rules check (ASTRAL_CODE_RULES)

| Rule | Status |
|------|--------|
| §1.3 DRY / public-then-helpers | Resolve once in `_resolve_company_job_id`; extract once in formatting; helpers below publics in consult |
| §1.4 / §2.1 no-hardcoded-sets / config SoT | UUID regex lives in `TRACKER_CONFIG`; formatting takes pattern arg |
| §1.5.1 debug-contract-gated | **Out of scope** — no new found/recorded source logging (AST-1121) |
| §2.4 claim-process-release | Fallback inside existing qualify `process`; no parallel claim path |
| §2.4.1 entity-agent-responses | AI value still from RESPONSE decode; fallback is post-decode apply only |
| §2.6 state machine | Same `fail_state` / `pass_state` transitions; no new states |
| §3.3 import direction | `consult` → `utils` only for helper; `formatting` stays pure (no config import) |
| §3.6 spikes | N/A — no spike deliverables |

No plan conflicts requiring `conf-!!-NONE`.

## Review

**Publish ref:** `origin/sub/AST-1119/AST-1120-uuid-from-job-link-company-job-id-fallback`
**Tip (pre-review):** `bea30019` (`merge-tests` + Betty coverage)

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `ab433398` | `TRACKER_CONFIG["uuid_path_segment_pattern"]` + `formatting.uuid_path_segment_from_url` |
| 2 | `ba8254f2` | `_resolve_company_job_id` + wire before `qualify_meteorite` empty-id gate |
| tests | `ea4716e7` / `bea30019` | Betty component coverage + `merge-tests` |

### Radia — code-rubric.v1 (`[code-rubric] revision=1`)

**Overall:** DISCUSS (C4 stragglers only; no product fix-now)

**What's solid**
- AI-first resolve; rightmost UUID path-segment fullmatch from `TRACKER_CONFIG`; `formatting` stays config-free (pattern arg).
- Wire only in `qualify_meteorite` `process` before empty-id gate; no create / `job_site` / `qualify_job_listings` creep.
- Import direction and DRY match plan; Betty owns tests/bible via `test()` + one `merge-tests`.

**Issues**
- **discuss (straggler):** Joan plan-time Excluded → in-scope on tip vs `origin/dev`: `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban` — all scored `conforms` (plan file + Betty test tree); no product action.

**Recommended actions**
- Resolve-child: no code changes required for stragglers; proceed unless Ada wants a `[review-handoff]` on placement wording (helper already after `qualify_meteorite` with existing privates).
- AST-1121 still owns Style D found/recorded source labels.

## Resolution

**Date:** 2026-08-02  
**Radia tip:** `ab463454` (`docs(AST-1120): Radia review — findings`)

- **fix-now:** none — no product edits.
- **discuss (C4 stragglers):** accepted as non-blocking; tip already conforms (`spikes-under-debug-dir`, `features-single-file-per-ticket`, `engineer-test-tree-ban`). No code or plan-path change.
- **Helper placement:** left after `qualify_meteorite` with existing private helpers (matches Joan/Radia note).
- **Boundaries:** AST-1121 still owns Style D found/recorded source labels.
