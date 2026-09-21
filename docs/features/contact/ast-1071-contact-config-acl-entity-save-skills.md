<!-- linear-archive: AST-1071 archived 2026-08-11 -->

## Linear archive (AST-1071)

**Archived:** 2026-08-11  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1071/contact-config-acl-predetermined-entity-save-skills  
**Status at archive:** Archive  
**Project:** Astral Contact  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1043 — Slack Bot Agent  
**Blocked by / blocks / related:** parent: AST-1043

### Description

## What this implements

CONTACT_CONFIG ACL + predetermined entity-save skills for Contact. Does not own CONTACT_CONFIG scaffold (#1), webhook (#2), Manage Slack (#3), resolve (#4), or context (#5).

## Acceptance criteria

- [X] 1. CONTACT_CONFIG exposes ACL / skill wiring for Contact entity-save paths.
- [X] 2. Predetermined entity-save skills are registered for Contact use.

## Boundaries

Does not own CONTACT_CONFIG core scaffold, Events ingress, resolve, conversation cache, or Estelle turn loop.

## In scope

- [X] `pattern.config.config-block` — populate `CONTACT_CONFIG["skills"]` ACL metadata
- [X] `pattern.core.contact-agent` (proposed) — `run_contact_skill` / `contact_skill_meta` in `src/core/contact.py`
- [X] `pattern.ui.admin-endpoint` — thin `api_contact` list/run under `/api/admin/contact`
- [X] `astral.patterns.require-auth-on-protected-endpoints` — `@require_admin` on skill routes
- [X] `astral.config.config-source-of-truth` — allowlisted paths only in `CONTACT_CONFIG`
- [X] `astral.standards.no-hardcoded-sets` — no inline path allowlists in core
- [X] `astral.standards.dry-and-focused-functions` — call existing `save_candidate_data` / `get_candidate`
- [X] `astral.layers.import-direction` — UI → core contact → core candidate; no UI→data
- [X] `astral.layers.core-vs-external-bright-line` — no Slack I/O in this ticket
- [X] `astral.standards.debug-contract-gated` — Style D on `run_contact_skill` only when `debug=True`
- [X] `astral.standards.logging-via-utils` — `get_logger` / truncate helpers
- [X] `astral.standards.data-raises-caller-logs` — core `ValueError`; API maps 400/502
- [X] `astral.standards.public-then-helpers` — public meta/run before private nest/merge
- [X] `astral.standards.in-scope-only` / `astral.standards.no-cross-contamination` — sibling scopes excluded
- [X] `astral.git.engineer-test-tree-ban` — no tests/bible in engineer commits
- [X] `astral.ui.naming-conventions` — snake_case admin contact routes

## Considered but excluded

- [X] `pattern.external.slack-events` — AST-1069 owns Events verify/ack/post
- [X] `pattern.state.entity-state-transitions` / PROSPECT — AST-1068
- [X] `astral.config.secrets-and-env-specific-from-environ` — no new secrets; Slack env names already on CONTACT_CONFIG
- [X] `astral.standards.database-header-inventory` — no new tables; reuse candidate_data via `save_candidate_data`
- [X] `astral.batch.*` / `astral.agent.*` — not dispatch/do_task skill catalog; CONTACT ≠ TASK_CONFIG
- [X] `astral.ui.frontend-file-placement` / Manage Slack UI — AST-1067; no Contact frontend page here
- [X] `astral.layers.scripts-exempt-from-layer-rules` — no scripts/
- [X] `astral.debug.spikes-under-debug-dir` / `no-repo-root-artifacts-dir` — no spike paths
- [X] `astral.docs.features-single-file-per-ticket` — plan-only docs path (planner)
- [X] `astral.git.betty-no-src-or-features` — engineer owns these paths

## Notes for planning

After #1 (AST-1066). Calls existing candidate save; ACL gates paths.

## Git branch (authoritative)

Parent `ftr/AST-1043-slack-bot-agent`; child `sub/AST-1043/AST-1071-contact-config-acl-entity-save-skills`. Created at dispatch-parent.

## Plan

`docs/features/contact/ast-1071-contact-config-acl-entity-save-skills.md` @ `origin/sub/AST-1043/AST-1071-contact-config-acl-entity-save-skills` tip `d5800f37` (build; review stub follows product `91ced0bc`).

### Comments

#### radia — 2026-07-30T03:23:12.507Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1071
**Publish ref:** `93058b63` on `origin/sub/AST-1043/AST-1071-contact-config-acl-entity-save-skills`
**Overall:** DISCUSS

**Diff change set:** `origin/dev...93058b63` — layers `{core, utils, ui, docs}`; paths include `src/core/contact.py` (A), `src/utils/config.py` (M), `src/ui/api/api_contact.py` (A), `src/ui/server.py` (M), plan/bible/tests; change_types `{add, modify}`. Tip carries AST-1066 scaffold ancestry not yet on `origin/dev`.

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | conforms | Contact skills are ACL saves, not graded agent tasks |
| astral.agent.do-task-delegation | scoped | conforms | CONTACT_CONFIG skills stay out of TASK_CONFIG / do_task |
| astral.agent.grade-vector-validation | scoped | conforms | no grade vectors |
| astral.batch.batch-id-first | scoped | conforms | no batch claim API |
| astral.batch.batch-id-format | scoped | conforms | no batch_id generation |
| astral.batch.claim-process-release | scoped | conforms | no batch processing |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | no agent_data entity refs |
| astral.config.config-source-of-truth | scoped | conforms | skill keys + allowed_paths only in CONTACT_CONFIG |
| astral.config.pass-threshold-vs-score-floor | scoped | not-applicable | no threshold/score-floor edits |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | Slack env names only; no new secret literals |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss artifacts/** / scripts/spikes/** |
| astral.debug.spikes-under-debug-dir | scoped | conforms | docs/features plans only — not spike notes |
| astral.docs.features-single-file-per-ticket | scoped | conforms | one plan file per ticket under docs/features/contact/ |
| astral.git.betty-no-src-or-features | scoped | conforms | merge-tests `da2d070b` tests/bible only |
| astral.git.engineer-test-tree-ban | scoped | conforms | tests/bible via Betty test/merge-tests vocabulary |
| astral.layers.core-vs-external-bright-line | scoped | conforms | no Slack I/O; persist via candidate core |
| astral.layers.import-direction | scoped | conforms | UI→core contact→core candidate; no UI→data |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no scripts/** in diff |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | ACL in config; thin API; logic in core |
| astral.patterns.coat-check-never-store-empty | scoped | not-applicable | no coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | scoped | not-applicable | no consult/render_verdict |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | GET/POST skills routes `@require_admin` |
| astral.standards.data-raises-caller-logs | scoped | conforms | core ValueError; API maps 400/502 |
| astral.standards.database-header-inventory | scoped | not-applicable | no data/schema paths |
| astral.standards.debug-contract-gated | scoped | conforms | Style D found→recorded only in run_contact_skill when debug=True |
| astral.standards.dry-and-focused-functions | scoped | conforms | reuses get_candidate / save_candidate_data |
| astral.standards.in-scope-only | scoped | conforms | no Slack Events / PROSPECT / turn-loop / Manage Slack |
| astral.standards.logging-via-utils | scoped | conforms | get_logger + truncate_debug_content |
| astral.standards.no-cross-contamination | scoped | conforms | TASK_CONFIG untouched; skill keys collision-asserted |
| astral.standards.no-hardcoded-sets | scoped | conforms | paths/skills from CONTACT_CONFIG only |
| astral.standards.public-then-helpers | scoped | conforms | meta/run public before private nest/merge |
| astral.standards.utils-data-late-import-only | scoped | conforms | config.py has no data import |
| astral.state.core-decides-transitions | scoped | not-applicable | no state transitions |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no job state work |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no dispatch run_next |
| astral.ui.frontend-file-placement | scoped | not-applicable | no src/ui/frontend/** |
| astral.ui.naming-conventions | scoped | conforms | snake_case /api/admin/contact/skills |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no gunicorn/worker changes |
| orch.git.betty-merge-tests-one-sha | universal | conforms | single merge-tests SHA on tip |
| orch.git.commit-vocabulary | universal | conforms | plan/code/test/merge-tests vocabulary on sub |
| orch.git.flow-direction-inviolable | universal | conforms | publish on origin/sub/AST-1043/AST-1071-… |
| orch.git.ftr-sub-topology | universal | conforms | matches parent Git table |
| orch.git.merge-on-checkout | universal | conforms | depends on AST-1066 on ftr; no illegal merge |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | none in tip history |
| orch.git.no-dev-agent-branches | universal | conforms | uses sub/AST-1043/AST-1071-… |
| orch.git.one-epic-worktree-per-parent | universal | conforms | astral-AST-1043 epic worktree |
| orch.git.three-permanent-branches | universal | conforms | no new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | v1 skill inventory Decision held |
| orch.pipeline.plan-is-bible | universal | conforms | stages 1–3 match tip product |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Contact child scope |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | no statute corpus edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty owns tests/bible |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee Katherine through Tests Passed |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | implementer Katherine remains assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | doc-only review commit paths |

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.config.config-block | conforms | CONTACT_CONFIG skills ACL populated |
| pattern.core.contact-agent (proposed) | conforms | contact_skill_meta / run_contact_skill |
| pattern.ui.admin-endpoint | conforms | thin api_contact list/run under /api/admin/contact |

## Plan adherence

Stages 1–3 land: two entity-save skills with narrow allowed_paths (no slack_user_id), ACL-gated runners + Style D, `@require_admin` GET/POST + server register. Self-Assessment Single-Component / high / Medium matches write-power risk and mitigations. Sibling scopes clean.

## Findings

**discuss** — C4 straggler: Joan Excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban` now in-scope on tip (docs/features + tests/bible). All three score **conforms** — no product action.

## What’s solid

Narrow ACL tuples; reject-unknown paths; debug gated with ui_llm_debug on API; UI→core→candidate import chain; Betty revised AST-1066 empty-skills asserts for populated ACL.

Plan append: `docs/features/contact/ast-1071-contact-config-acl-entity-save-skills.md` @ `93058b63`.

context_tokens≈56000

— Radia

#### betty — 2026-07-30T03:18:03.475Z
## QA test manifest — AST-1071

`origin/sub/AST-1043/AST-1071-contact-config-acl-entity-save-skills` @ `da2d070b` (`merge-tests(AST-1071): origin/tests 26fe570b08f1590235b2f507ed0b7f38a7917cb1` — ours-strategy + Betty path overlay; tip vs product `91ced0bc` is tests/bible (+ review stub) only).

### Manifest

1. `tests/component/utils/test_config.py::TestAst1071ContactSkillsConfig`
2. `tests/component/core/test_contact.py::TestAst1071ContactSkillRunners`
3. `tests/component/ui/api/test_api_contact.py::TestAst1071ContactSkillsApi`
4. `tests/component/utils/test_config.py::TestAst1066ContactConfig` (revised — empty-skills dropped)
5. `tests/component/core/test_contact.py::TestAst1066ContactScaffold` (revised — shallow-copy vs populated ACL)

### Run

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1071ContactSkillsConfig \
  tests/component/core/test_contact.py::TestAst1071ContactSkillRunners \
  tests/component/ui/api/test_api_contact.py::TestAst1071ContactSkillsApi \
  tests/component/utils/test_config.py::TestAst1066ContactConfig \
  tests/component/core/test_contact.py::TestAst1066ContactScaffold \
  -q
```

(23 passed vs tip product.)

### Broken / obsolete

- AST-1066 `skills == {}` / empty `contact_skill_keys()` — revised for populated ACL

### Bible shasums (`origin/sub/…` tip, sha256)

- `docs/test-bible/core/contact.md` — `a8baddface4487145ec537d4b1e04d499390fb31aaf986f962ccb75abff33815`
- `docs/test-bible/ui/api/api_contact.md` — `015e0def1283627ba0e16e6260629040e824f5ec4e07abca990b1f1c3352627a`
- `docs/test-bible/utils/config.md` — `c0c08083fb44fe602477db2a9e1cd2713daa185dc7c5a9b8700df74617459e7e`

#### joan — 2026-07-30T03:07:00.244Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1071
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 Estelle DM/@ ingress | N/A — boundary (AST-1069 / AST-1073) |
| AC2 Events webhook verify/ack | N/A — boundary (AST-1069) |
| AC3 Manage Slack listen | N/A — boundary (AST-1067) |
| AC4 Slack resolve + PROSPECT | N/A — boundary (AST-1068); ACL excludes `contact.slack_user_id` |
| AC5 routing / candidate state | N/A — boundary (AST-1068) |
| AC6 conversation load/cache | N/A — boundary (AST-1070) |
| AC7 CONTACT_CONFIG skills/ACL only entity-write paths | Stages 1–3 — populate skills, `run_contact_skill` ACL gate, admin list/run |
| AC8 debug=True found/recorded | Stage 2 Style D on `run_contact_skill` when `debug=True` |

### Child AC → plan stages

| Child AC | Plan coverage |
|----------|---------------|
| CONTACT_CONFIG exposes ACL / skill wiring | Stage 1 + Stage 2 meta/gate |
| Predetermined entity-save skills registered | Stage 1 two skills; Stage 2 runners; Stage 3 admin invoke |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 populate CONTACT_CONFIG skills | Purpose Contact ACL; Functional scope CONTACT_CONFIG ≠ TASK_CONFIG; parent child #6 |
| Stage 2 run_contact_skill + nest/merge | pattern.core.contact-agent; entity-save only via allowlist; debug contract |
| Stage 3 api_contact admin list/run | Thin UI admin endpoint; require_admin; in-process Estelle calls core directly |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work |
| orch.git.commit-vocabulary | conforms | Publish on sub with plan/code vocabulary |
| orch.git.flow-direction-inviolable | conforms | Publish only to origin/sub/… |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | Depends on AST-1066 on ftr; no illegal merge |
| orch.git.no-cherry-pick-rebase-force | conforms | None proposed |
| orch.git.no-dev-agent-branches | conforms | Uses sub/AST-1043/AST-1071-… |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree astral-AST-1043 |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | v1 skill inventory Decision documented; stop→parent on drift |
| orch.pipeline.plan-is-bible | conforms | Binding stages + Files Changed |
| orch.pipeline.project-scoped-queues | conforms | Single-child Contact scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate-plan only |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | No tests/ edits |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Katherine) builds after approve |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer implementer path |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | Skills are Contact ACL saves, not graded tasks |
| astral.agent.do-task-delegation | conforms | Explicit CONTACT ≠ TASK_CONFIG / do_task |
| astral.agent.grade-vector-validation | conforms | No grade vectors |
| astral.batch.batch-id-first | conforms | No batch claim |
| astral.batch.batch-id-format | conforms | No batch_id |
| astral.batch.claim-process-release | conforms | No batch processing |
| astral.batch.entity-agent-responses-latest-only | conforms | No agent_data entity refs |
| astral.config.config-source-of-truth | conforms | Skill keys + allowed_paths only in CONTACT_CONFIG |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | No new secrets; Slack env names untouched |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src/features |
| astral.layers.core-vs-external-bright-line | conforms | No Slack I/O; persistence via candidate core |
| astral.layers.import-direction | conforms | UI→core contact→core candidate; no UI→data |
| astral.layers.ui-config-driven-business-logic | conforms | ACL in config; thin API; logic in core |
| astral.patterns.coat-check-never-store-empty | conforms | No coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | conforms | No consult |
| astral.patterns.require-auth-on-protected-endpoints | conforms | New routes `@require_admin` |
| astral.standards.data-raises-caller-logs | conforms | Core ValueError; API maps 400/502 |
| astral.standards.debug-contract-gated | conforms | Style D only in run_contact_skill when debug=True |
| astral.standards.dry-and-focused-functions | conforms | Reuses get_candidate / save_candidate_data |
| astral.standards.in-scope-only | conforms | Sibling scopes Out of scope |
| astral.standards.logging-via-utils | conforms | get_logger + truncate_debug_content |
| astral.standards.no-cross-contamination | conforms | No TASK_CONFIG / Slack / turn-loop edits |
| astral.standards.no-hardcoded-sets | conforms | Paths/skills from CONTACT_CONFIG only |
| astral.standards.public-then-helpers | conforms | Public meta/run before private nest/merge |
| astral.standards.utils-data-late-import-only | conforms | No utils→data |
| astral.state.core-decides-transitions | conforms | No state transitions |
| astral.state.job-prior-states-enforced | conforms | No job state work |
| astral.state.no-daisy-chain-in-run | conforms | No dispatch run_next |
| astral.ui.naming-conventions | conforms | snake_case `/api/admin/contact/skills` |
| astral.ui.single-gunicorn-worker | conforms | No gunicorn/worker changes |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.patterns.require-auth-on-protected-endpoints, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.naming-conventions, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths match none of plan paths
- astral.debug.spikes-under-debug-dir — paths match none of plan paths
- astral.docs.features-single-file-per-ticket — layers {docs} ∩ plan empty
- astral.git.engineer-test-tree-ban — paths match none of plan paths
- astral.layers.scripts-exempt-from-layer-rules — layers {scripts} ∩ plan empty
- astral.standards.database-header-inventory — layers {data} ∩ plan empty
- astral.ui.frontend-file-placement — paths src/ui/frontend/** match none

## Findings

None fix-now.

**discuss (non-blocking):** Parent AC7 requires predetermined skills but does not name keys/paths. Plan Decision registers `save_candidate_profile` + `save_candidate_contact` with narrow `allowed_paths`. Acceptable for v1 Contact intake; expand via config later. If Archie wants different path homes (e.g. high-frequency name columns vs `profile.*`), that is a product follow-up — not a fidelity break vs child boundaries.

**acceptable:** Self-assessment Single-Component / Conf high / Risk Medium matches ACL write-power risk and mitigations (narrow tuples + reject unknown).

**R6 checklist:** Definition fidelity pass (child #6 only). Layer/import pass. Config ACL + no hardcoded path sets. Auth on new admin routes. Debug gated. DRY via existing candidate save. No Slack/turn-loop/PROSPECT creep.

context_tokens≈55000

— Joan

#### katherine — 2026-07-30T03:03:06.639Z
Plan: `docs/features/contact/ast-1071-contact-config-acl-entity-save-skills.md`

https://github.com/susansomerset/astral/blob/sub/AST-1043/AST-1071-contact-config-acl-entity-save-skills/docs/features/contact/ast-1071-contact-config-acl-entity-save-skills.md

**Self-Assessment**
- **Scope:** `Single-Component` — populate `CONTACT_CONFIG["skills"]`, extend `contact.py` with ACL-gated `run_contact_skill`, thin admin `api_contact` list/run + server register.
- **Conf:** `high` — AST-1066 empty skills home + helpers already on ftr; persistence reuses `save_candidate_data`; admin blueprint mirrors inbox auth/debug. Skill key inventory is an explicit plan Decision (parent named ACL, not keys).
- **Risk:** `Medium` — over-broad allowlists expand Contact write power; under-broad lists block intake fields — mitigated by narrow path tuples + reject-unknown. No listen/Slack change.

Three stages: (1) register `save_candidate_profile` + `save_candidate_contact` ACL, (2) core runners + Style D, (3) `@require_admin` GET/POST `/api/admin/contact/skills`.

Publish ref `origin/sub/AST-1043/AST-1071-contact-config-acl-entity-save-skills` @ `c27449a9`.

---

# AST-1071 — CONTACT_CONFIG ACL / predetermined entity-save skills

**Linear:** [AST-1071](https://linear.app/astralcareermatch/issue/AST-1071/contact-config-acl-predetermined-entity-save-skills)  
**Parent:** [AST-1043](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent) — Slack Bot Agent  
**Publish ref:** `origin/sub/AST-1043/AST-1071-contact-config-acl-entity-save-skills`

Register Contact’s predetermined **entity-save** skills on `CONTACT_CONFIG["skills"]` (ACL distinct from `TASK_CONFIG`), implement core runners that only write allowlisted `candidate_data` paths via existing `save_candidate_data`, and expose thin admin HTTP entrypoints (`@require_admin`) so the ACL can be listed/invoked without going through Slack. Does **not** own Contact scaffold (AST-1066 — already on `ftr`), Events ingress, Manage Slack, resolve/PROSPECT, conversation cache, or Estelle turn loop (AST-1046 / AST-1073).

**Depends on:** AST-1066 on `origin/ftr/AST-1043-slack-bot-agent` (merge that tip before build — empty `skills` dict + `contact_skills` / `contact_skill_keys` helpers exist).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Populate `CONTACT_CONFIG["skills"]` with v1 entity-save ACL entries + required metadata keys | utils |
| `src/core/contact.py` | Add ACL gate + `run_contact_skill` (+ private nest/merge helpers); Style D when `debug=True` | core |
| `src/ui/api/api_contact.py` | New admin blueprint: list skills + run skill (`@require_admin`) | ui |
| `src/ui/server.py` | Register `contact_bp` | ui |

No edits to `TASK_CONFIG`, `src/core/candidate.py` signatures, Slack external, or Estelle turn loop.

---

## Stage 1: Populate `CONTACT_CONFIG["skills"]` ACL

**Done when:** `CONTACT_CONFIG["skills"]` is a non-empty dict of two skill keys with the metadata below; keys do not appear in `TASK_CONFIG`; existing import-time collision assert still holds; no core/UI runners yet.

1. In `src/utils/config.py`, replace the empty `"skills": {}` inside `CONTACT_CONFIG` with:

```python
    # skill_key → ACL metadata. Contact-only entity-save paths (AST-1071).
    # Keys must never appear in TASK_CONFIG (assert below).
    "skills": {
        "save_candidate_profile": {
            "entity": "candidate",
            "write": True,
            "description": (
                "Merge allowlisted profile fields into candidate_data.profile "
                "for Slack Contact intake."
            ),
            # Dotted paths under candidate_data. Payload field keys must match exactly.
            "allowed_paths": (
                "profile.first",
                "profile.last",
                "profile.pronoun_preference",
                "profile.contact_email",
            ),
        },
        "save_candidate_contact": {
            "entity": "candidate",
            "write": True,
            "description": (
                "Merge allowlisted contact.* fields into candidate_data "
                "(not slack_user_id — AST-1068 owns that)."
            ),
            "allowed_paths": (
                "contact.contact_email",
                "contact.reply_email",
            ),
        },
    },
```

2. Immediately after the existing `for _skill_key in CONTACT_CONFIG["skills"]: assert _skill_key not in TASK_CONFIG` loop, add shape asserts (keep them next to the block so drift fails import):

```python
for _skill_key, _skill_meta in CONTACT_CONFIG["skills"].items():
    assert isinstance(_skill_meta, dict), _skill_key
    assert _skill_meta.get("entity") == "candidate", _skill_key
    assert _skill_meta.get("write") is True, _skill_key
    assert isinstance(_skill_meta.get("description"), str) and _skill_meta["description"].strip(), _skill_key
    _paths = _skill_meta.get("allowed_paths")
    assert isinstance(_paths, tuple) and len(_paths) > 0, _skill_key
    for _p in _paths:
        assert isinstance(_p, str) and "." in _p, (_skill_key, _p)
```

⚠️ **Decision — v1 skill inventory:** Parent AC7 requires an ACL of predetermined entity-save skills, but does not name keys. For Slack Contact intake, register exactly two candidate-write skills: profile identity/email fields and contact-blob email fields. Do **not** allowlist `contact.slack_user_id` (AST-1068), job/company writes, state transitions, or unrestricted `candidate_data` roots.

⚠️ **Decision — CONTACT_CONFIG ≠ TASK_CONFIG:** Skill keys stay out of `TASK_CONFIG` / `do_task` catalogs. Estelle turn loop (AST-1073) will call Contact runners, not dispatch these as agent tasks.

⚠️ **Decision — payload keys = full dotted paths:** Callers pass `fields` whose keys are exact `allowed_paths` members (e.g. `"profile.first"`). Avoids ambiguous relative-key mapping and keeps the ACL auditable as a single string set.

**Done when (recheck):** `len(CONTACT_CONFIG["skills"]) == 2`; `"save_candidate_profile" in CONTACT_CONFIG["skills"]`; `"save_candidate_profile" not in TASK_CONFIG`; `contact_skill_keys()` (unchanged helper) returns both keys in dict insertion order.

---

## Stage 2: Core skill runners in `src/core/contact.py`

**Done when:** `run_contact_skill` persists only allowlisted paths via `save_candidate_data`; unknown skill / unknown field path / missing candidate raise `ValueError`; `debug=True` emits Style D found → recorded; `debug=False` is quiet.

1. Update the module docstring to note AST-1071 skill runners (still no Slack HTTP).

2. Extend imports:

```python
from typing import Any, Dict, List, Tuple

from src.core.candidate import get_candidate, save_candidate_data
from src.utils.config import CONTACT_CONFIG
from src.utils.logging import get_logger, truncate_debug_content
```

⚠️ **Decision — import candidate from core:** Contact orchestrates; persistence stays on existing `save_candidate_data` (DRY). Do **not** import `src.data` from Contact.

3. Keep existing public helpers (`slack_listen_enabled`, `contact_skills`, `contact_skill_keys`, `slack_env_names`, `non_production_reply_prefix`) unchanged and **above** new helpers (public-then-helpers: add new public API immediately after those five, then private helpers below).

4. Add public:

```python
def contact_skill_meta(skill_key: str) -> Dict[str, Any]:
    """Return a shallow copy of one skill ACL entry, or raise ValueError if unknown."""
```

Concrete behavior:
- `key = (skill_key or "").strip()`
- If `key` not in `CONTACT_CONFIG["skills"]` → `raise ValueError(f"unknown contact skill: {key!r}")`
- Return `dict(CONTACT_CONFIG["skills"][key])` with `"allowed_paths"` as `tuple(meta["allowed_paths"])`.

5. Add public:

```python
def run_contact_skill(
    skill_key: str,
    *,
    astral_candidate_id: str,
    fields: Dict[str, Any],
    debug: bool = False,
) -> Dict[str, Any]:
    """ACL-gated entity save for Contact. Writes only allowlisted candidate_data paths."""
```

Concrete behavior:

- If `debug`: `logger.set_debug_flag(True)`.
- `cid = (astral_candidate_id or "").strip()` — empty → `raise ValueError("astral_candidate_id is required")`.
- `meta = contact_skill_meta(skill_key)` (raises on unknown).
- If `meta.get("write") is not True` → `raise ValueError(...)` (defensive; v1 entries are all write).
- If `fields` is not a `dict` → `raise ValueError("fields must be a dict")`.
- `allowed = set(meta["allowed_paths"])`.
- For each `path, value` in `fields.items()`:
  - If `path not in allowed` → `raise ValueError(f"path not allowlisted for skill {skill_key!r}: {path!r}")`
  - If `value` is not `None` and not a `str` → `raise ValueError(f"field {path!r} must be a string or null")`
- Load candidate: `row = get_candidate(cid)` — if missing → `raise ValueError(f"candidate not found: {cid}")`.
- If `debug`: Style D index `func="run_contact_skill"`, `index=1`, `total=2`, `identifier=cid[:80]`, `outcome="found"`; detail lines for `skill_key=` and each requested path (use `truncate_debug_content` for values).
- Build merge dict: for each path/value in `fields`, deep-merge `_nest_dotted_path(path, value)` into an accumulator (private helper below). Skip keys whose value is `None` (treat as omit, not write-null) **or** write empty string when value is `""` — **Decision:** empty string is allowed and written; `None` means omit that path from the merge.
- Call `save_candidate_data(cid, merge_dict)` (merge mode default).
- If `debug`: index `2/2`, `outcome="recorded"`; detail `paths_written=` comma-joined sorted paths actually merged.
- Return:

```python
{
    "ok": True,
    "skill_key": skill_key.strip(),
    "astral_candidate_id": cid,
    "paths_written": sorted(paths_actually_merged),
}
```

6. Private helpers (below public API):

```python
def _nest_dotted_path(path: str, value: Any) -> Dict[str, Any]:
    """Turn 'a.b.c' + value into {'a': {'b': {'c': value}}}."""
    ...


def _deep_merge(dst: Dict[str, Any], src: Dict[str, Any]) -> Dict[str, Any]:
    """Merge src into dst in place; dict values recurse. Return dst."""
    ...
```

⚠️ **Decision — no job/company skills in v1:** Parent forbids unrestricted admin mutation; candidate profile/contact is the Contact intake surface. Expand ACL later via config only (no runner rewrite for new path lists).

⚠️ **Decision — debug contract:** Only `run_contact_skill` emits Style D; list helpers stay quiet. Gate with `debug=`.

**Done when (recheck):** Calling `run_contact_skill("save_candidate_profile", astral_candidate_id=<existing>, fields={"profile.first": "Ada"})` merges into `candidate_data.profile.first`; `fields={"profile.middle": "X"}` raises; unknown skill raises; `debug=False` produces no new debug-contract lines.

---

## Stage 3: Admin HTTP — list + run Contact skills

**Done when:** `GET /api/admin/contact/skills` and `POST /api/admin/contact/skills/<skill_key>` exist, both `@require_admin`; POST maps core `ValueError` → 400 and other errors → 502; blueprint registered in `server.py`.

1. Create `src/ui/api/api_contact.py`:

```python
"""Admin Contact skill ACL API (AST-1071). Thin wrappers over src.core.contact."""

from flask import Blueprint, jsonify, request

from ui.auth import require_admin
from src.core.contact import contact_skills, run_contact_skill
from src.utils.deploy_status import ui_llm_debug
from src.utils.logging import get_logger

logger = get_logger(__name__)

contact_bp = Blueprint("contact", __name__, url_prefix="/api/admin/contact")
```

2. Routes:

- `GET /skills` + `@require_admin` → `jsonify({"skills": contact_skills()}), 200`. Serialize `allowed_paths` as lists in JSON by building a JSON-safe copy: for each skill, `dict(meta)` with `allowed_paths=list(meta["allowed_paths"])`.

- `POST /skills/<skill_key>` + `@require_admin`:
  - Body JSON: `astral_candidate_id` (str, required), `fields` (object, required), optional `debug` bool.
  - `debug = ui_llm_debug(explicit_debug=(query debug flag OR body.debug))` — same OR pattern as `api_inbox` create-job.
  - Call `run_contact_skill(skill_key, astral_candidate_id=..., fields=..., debug=debug)`.
  - `ValueError` → `jsonify({"error": str(e)}), 400`
  - Other `Exception` → log warning `[api_contact] skill failed …` → 502
  - Success → `jsonify(result), 200`

3. In `src/ui/server.py`, register next to other admin blueprints (after inbox is fine):

```python
from ui.api.api_contact import contact_bp  # noqa: E402
app.register_blueprint(contact_bp)
```

⚠️ **Decision — admin API, not Slack webhook:** Skill HTTP is for ACL inspect/invoke under admin auth. Estelle production turns (AST-1073) should call `run_contact_skill` in-process; they must not depend on this HTTP surface. Do **not** put skill routes on the Slack Events blueprint.

⚠️ **Decision — no frontend Manage Contact page:** Out of scope. Admin API only.

**Done when (recheck):** Unauthenticated GET/POST → 401/403 per existing `require_admin` behavior; authenticated GET returns both skill keys; POST with allowlisted field returns `ok: true`; POST with non-allowlisted path → 400.

---

## Out of scope (do not implement here)

- Slack Events verify/ack/post (AST-1069).
- Manage Slack listen UI / persist listen flag (AST-1067).
- PROSPECT create / `slack_user_id` persistence / lookup matcher teach-in (AST-1068).
- Conversation context load/cache (AST-1070).
- Estelle turn loop / skill tool-calling from `do_task` (AST-1046 / AST-1073).
- Job/company/roster entity-save skills; state-machine transitions; unrestricted `save_candidate_data` without ACL.
- Editing `tests/` or `docs/test-bible/**` (Betty after Code Complete).

---

## Self-Assessment

**Scope:** `Single-Component` — populate one config ACL map, extend one core module with runners, add one thin admin blueprint + server register.

**Conf:** `high` — AST-1066 scaffold + empty `skills` home already on `ftr`; persistence reuses `save_candidate_data`; admin blueprint mirrors `api_inbox` auth/debug patterns. Skill key inventory is an explicit plan Decision (parent named ACL, not keys).

**Risk:** `Medium` — over-broad allowlists would expand Contact write power; under-broad lists block intake fields Estelle needs — mitigated by narrow path tuples and rejecting unknown keys. No Slack listen change, so production Estelle stays off until Manage Slack + turn loop land.

## Rules self-review

- **§2.1 / config-source-of-truth / no-hardcoded-sets:** Allowlisted paths and skill keys live only in `CONTACT_CONFIG["skills"]`.
- **§2.1 / secrets-from-environ:** No new secrets; Slack env-name contracts untouched.
- **§2.5 / §3.3 import-direction:** UI → core contact → core candidate → data; UI does not import data/external.
- **§2.9 / require-auth:** New admin routes use `@require_admin`.
- **§1.3 DRY:** Call existing `save_candidate_data` / `get_candidate`; no duplicate upsert SQL.
- **§1.5.1 debug-contract-gated:** Style D only inside `run_contact_skill` when `debug=True`; API uses `ui_llm_debug`.
- **§1.1 in-scope-only:** Sibling scopes listed under Out of scope; no turn loop / Slack I/O.
- **public-then-helpers:** New public `contact_skill_meta` + `run_contact_skill` before private nest/merge helpers.

## Execution contract

The plan is binding. Execute stages in order; one commit per stage on epic worktree; publish to `origin/sub/AST-1043/AST-1071-contact-config-acl-entity-save-skills`. On ambiguity or codebase drift, stop and comment on parent **AST-1043** with the Stage-blocked format — do not improvise.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1043/AST-1071-contact-config-acl-entity-save-skills`  
**Tip:** `91ced0bc` — Contact skills ACL + runners + admin API (stages 1–3)  
**Stage commits:** `615f39b6` (config), `20361b54` (core runners), `91ced0bc` (admin API)

---

## Review (Radia / code-rubric.v1)

[code-rubric] revision=1  
**Rubric:** code-rubric.v1  
**Ticket:** AST-1071  
**Publish ref:** `da2d070b` on `origin/sub/AST-1043/AST-1071-contact-config-acl-entity-save-skills` (docs tip follows)  
**Overall:** DISCUSS

**Diff change set:** `origin/dev...da2d070b` — layers `{core, utils, ui, docs}`; paths include `src/core/contact.py` (A), `src/utils/config.py` (M), `src/ui/api/api_contact.py` (A), `src/ui/server.py` (M), plan/bible/tests; change_types `{add, modify}`. Tip carries AST-1066 scaffold ancestry not yet on `origin/dev`.

### Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | conforms | Contact skills are ACL saves, not graded agent tasks |
| astral.agent.do-task-delegation | scoped | conforms | CONTACT_CONFIG skills stay out of TASK_CONFIG / do_task |
| astral.agent.grade-vector-validation | scoped | conforms | no grade vectors |
| astral.batch.batch-id-first | scoped | conforms | no batch claim API |
| astral.batch.batch-id-format | scoped | conforms | no batch_id generation |
| astral.batch.claim-process-release | scoped | conforms | no batch processing |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | no agent_data entity refs |
| astral.config.config-source-of-truth | scoped | conforms | skill keys + allowed_paths only in CONTACT_CONFIG |
| astral.config.pass-threshold-vs-score-floor | scoped | not-applicable | no threshold/score-floor edits |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | Slack env names only; no new secret literals |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss artifacts/** / scripts/spikes/** |
| astral.debug.spikes-under-debug-dir | scoped | conforms | docs/features plans only — not spike notes |
| astral.docs.features-single-file-per-ticket | scoped | conforms | one plan file per ticket under docs/features/contact/ |
| astral.git.betty-no-src-or-features | scoped | conforms | merge-tests `da2d070b` tests/bible only |
| astral.git.engineer-test-tree-ban | scoped | conforms | tests/bible via Betty test/merge-tests vocabulary |
| astral.layers.core-vs-external-bright-line | scoped | conforms | no Slack I/O; persist via candidate core |
| astral.layers.import-direction | scoped | conforms | UI→core contact→core candidate; no UI→data |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no scripts/** in diff |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | ACL in config; thin API; logic in core |
| astral.patterns.coat-check-never-store-empty | scoped | not-applicable | no coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | scoped | not-applicable | no consult/render_verdict |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | GET/POST skills routes `@require_admin` |
| astral.standards.data-raises-caller-logs | scoped | conforms | core ValueError; API maps 400/502 |
| astral.standards.database-header-inventory | scoped | not-applicable | no data/schema paths |
| astral.standards.debug-contract-gated | scoped | conforms | Style D found→recorded only in run_contact_skill when debug=True |
| astral.standards.dry-and-focused-functions | scoped | conforms | reuses get_candidate / save_candidate_data |
| astral.standards.in-scope-only | scoped | conforms | no Slack Events / PROSPECT / turn-loop / Manage Slack |
| astral.standards.logging-via-utils | scoped | conforms | get_logger + truncate_debug_content |
| astral.standards.no-cross-contamination | scoped | conforms | TASK_CONFIG untouched; skill keys collision-asserted |
| astral.standards.no-hardcoded-sets | scoped | conforms | paths/skills from CONTACT_CONFIG only |
| astral.standards.public-then-helpers | scoped | conforms | meta/run public before private nest/merge |
| astral.standards.utils-data-late-import-only | scoped | conforms | config.py has no data import |
| astral.state.core-decides-transitions | scoped | not-applicable | no state transitions |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no job state work |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no dispatch run_next |
| astral.ui.frontend-file-placement | scoped | not-applicable | no src/ui/frontend/** |
| astral.ui.naming-conventions | scoped | conforms | snake_case /api/admin/contact/skills |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no gunicorn/worker changes |
| orch.git.betty-merge-tests-one-sha | universal | conforms | single merge-tests SHA on tip |
| orch.git.commit-vocabulary | universal | conforms | plan/code/test/merge-tests vocabulary on sub |
| orch.git.flow-direction-inviolable | universal | conforms | publish on origin/sub/AST-1043/AST-1071-… |
| orch.git.ftr-sub-topology | universal | conforms | matches parent Git table |
| orch.git.merge-on-checkout | universal | conforms | depends on AST-1066 on ftr; no illegal merge |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | none in tip history |
| orch.git.no-dev-agent-branches | universal | conforms | uses sub/AST-1043/AST-1071-… |
| orch.git.one-epic-worktree-per-parent | universal | conforms | astral-AST-1043 epic worktree |
| orch.git.three-permanent-branches | universal | conforms | no new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | v1 skill inventory Decision held |
| orch.pipeline.plan-is-bible | universal | conforms | stages 1–3 match tip product |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Contact child scope |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | no statute corpus edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty owns tests/bible |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee Katherine through Tests Passed |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | implementer Katherine remains assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | doc-only review commit paths |

### Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.config.config-block | conforms | CONTACT_CONFIG skills ACL populated |
| pattern.core.contact-agent (proposed) | conforms | contact_skill_meta / run_contact_skill |
| pattern.ui.admin-endpoint | conforms | thin api_contact list/run under /api/admin/contact |

### Plan adherence

Stages 1–3 land: two entity-save skills with narrow allowed_paths (no slack_user_id), ACL-gated runners + Style D, `@require_admin` GET/POST + server register. Self-Assessment Single-Component / high / Medium matches write-power risk and mitigations. Sibling scopes clean.

### Findings

**discuss** — C4 straggler: Joan Excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban` now in-scope on tip (docs/features + tests/bible). All three score **conforms** — no product action.

### What’s solid

Narrow ACL tuples; reject-unknown paths; debug gated with ui_llm_debug on API; UI→core→candidate import chain; Betty revised AST-1066 empty-skills asserts for populated ACL.

context_tokens≈56000

## Resolution

**Date:** 2026-07-30  
**Tip before resolve:** `93058b63` (Radia `docs(AST-1071): Radia review — findings`)  
**Overall (Radia):** DISCUSS — **no fix-now**

- **fix-now:** none — no product changes.
- **discuss (C4 stragglers):** Joan Excluded statutes that became tip-applicable (`spikes-under-debug-dir`, `features-single-file-per-ticket`, `engineer-test-tree-ban`) scored **conforms** in Radia’s sweep — acknowledged; no plan/product edit.
- **advisory:** none.

Shipped product remains stages 1–3 @ `91ced0bc` (+ Betty merge-tests `da2d070b`).
