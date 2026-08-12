<!-- linear-archive: AST-1067 archived 2026-08-11 -->

## Linear archive (AST-1067)

**Archived:** 2026-08-11  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1067/manage-slack-admin-listen-switch-per-environment-non-prod-reply-tag  
**Status at archive:** Archive  
**Project:** Astral Contact  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1043 — Slack Bot Agent  
**Blocked by / blocks / related:** parent: AST-1043

### Description

## What this implements

Manage Slack: admin listen switch for the current environment; non-prod replies tagged `[<environment>]`. Does not own webhook (#2), CONTACT_CONFIG (#1), resolve (#4), or context (#5).

## Acceptance criteria

- [X] Manage Slack can turn Slack listen on/off for the current environment.
- [X] Non-prod Contact replies are tagged with `[<environment>]`.

## Boundaries

Does not own Events ingress, resolve/PROSPECT, or conversation cache.

## In scope

- [X] `pattern.ui.manage-pages` / `pattern.ui.admin-endpoint` — Admin Manage Slack page + thin `@require_admin` listen API on `contact_bp`
- [X] `pattern.config.config-block` — `CONTACT_CONFIG` listen filename + production deploy label; NAV item
- [X] `pattern.core.contact-agent` (proposed) — hydrate/set listen; `format_contact_reply_text` / `post_contact_reply`
- [X] `astral.config.config-source-of-truth` — production env string + listen filename literals in config
- [X] `astral.config.secrets-and-env-specific-from-environ` — no Slack secrets in config; deploy label from `ASTRAL_DEPLOY_ENV` via existing helpers
- [X] `astral.layers.import-direction` — ui → core → data/external; UI never imports `external.slack`
- [X] `astral.layers.core-vs-external-bright-line` — prefix/post orchestration in Contact; raw `post_message` stays external
- [X] `astral.patterns.require-auth-on-protected-endpoints` — GET/PUT `/api/admin/contact/listen` `@require_admin`; page behind `AdminRoute`
- [X] `astral.standards.no-hardcoded-sets` — production label + filename from `CONTACT_CONFIG`
- [X] `astral.standards.debug-contract-gated` — Style D on set/post when `debug=True`
- [X] `astral.standards.in-scope-only` / `astral.standards.no-cross-contamination` — no Events/resolve/cache/skills/turn-loop ownership
- [X] `astral.standards.public-then-helpers` / `astral.standards.dry-and-focused-functions` — public listen/prefix/post surface; JSON I/O in data
- [X] `astral.standards.logging-via-utils` — Contact debug via `get_logger`; data layer silent

## Considered but excluded

- [X] `pattern.external.slack-events` — Events verify/ack/Socket Mode already AST-1069; this ticket only consumes `post_message` via Contact
- [X] `pattern.state.entity-state-transitions` / PROSPECT — AST-1068
- [X] Skill ACL runners / `CONTACT_CONFIG["skills"]` bodies — AST-1071 (already on ftr)
- [X] Conversation cache / Slack history — AST-1070
- [X] Estelle turn loop calling `post_contact_reply` — AST-1046
- [X] `astral.standards.database-header-inventory` — durable JSON under `db_dir`, no new SQLite table
- [X] Mutating Railway env vars from Manage Slack — UI cannot write deploy env; volume-backed JSON instead

## Notes for planning

After #2 (AST-1069 — User Testing / on ftr).

## Git branch (authoritative)

Parent `ftr/AST-1043-slack-bot-agent`; child `sub/AST-1043/AST-1067-manage-slack-admin-listen-switch`. Created at dispatch-parent.

## Plan

`docs/features/contact/ast-1067-manage-slack-admin-listen-switch.md` @ `origin/sub/AST-1043/AST-1067-manage-slack-admin-listen-switch` tip `dff0a9ae` (product) / build stub follows.

### Comments

#### chuckles — 2026-07-30T16:21:27.021Z
[merge-child] blocked: git pull merge on sub — use: git fetch && git merge origin/ftr/<parent-segment>

Offending commit on `origin/sub/AST-1043/AST-1067-manage-slack-admin-listen-switch`:
`5a7659e5 Merge remote-tracking branch 'origin/dev' into sub/AST-1043/AST-1067-manage-slack-admin-listen-switch`

@Katherine Johnson — drop that pull-merge from the publish tip; merge `origin/ftr/AST-1043-slack-bot-agent` (not `origin/dev` via pull) and republish so `validate-sub-log` is clean. Chuckles will re-run merge-child after.

— Chuckles

#### radia — 2026-07-30T16:19:44.625Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1067
**Publish ref:** `9b2c81ed` on `origin/sub/AST-1043/AST-1067-manage-slack-admin-listen-switch`
**Overall:** DISCUSS

**Diff change set:** `origin/dev...9b2c81ed` — layers `{core, data, external, utils, ui, docs, scripts}`; tip carries AST-1066/1069/1071 ancestry plus AST-1067 Manage Slack listen; change_types `{add, modify}`.

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | conforms | no graded agent tasks |
| astral.agent.do-task-delegation | scoped | conforms | no do_task |
| astral.agent.grade-vector-validation | scoped | conforms | no grade vectors |
| astral.batch.batch-id-first | scoped | conforms | no batch claim |
| astral.batch.batch-id-format | scoped | conforms | no batch_id |
| astral.batch.claim-process-release | scoped | conforms | no batch processing |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | no agent_data |
| astral.config.config-source-of-truth | scoped | conforms | listen filename + production label + NAV in config |
| astral.config.pass-threshold-vs-score-floor | scoped | not-applicable | no threshold/score-floor edits |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | no Slack secrets in config; deploy label via helpers |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss artifacts/** / scripts/spikes/** |
| astral.debug.spikes-under-debug-dir | scoped | conforms | docs/features plans only — not spike notes |
| astral.docs.features-single-file-per-ticket | scoped | conforms | one plan file per ticket under docs/features/contact/ |
| astral.git.betty-no-src-or-features | scoped | conforms | merge-tests `5e9e94cb` tests/bible only |
| astral.git.engineer-test-tree-ban | scoped | conforms | tests/bible via Betty vocabulary |
| astral.layers.core-vs-external-bright-line | scoped | conforms | prefix/post in Contact; raw post_message stays external |
| astral.layers.import-direction | scoped | conforms | ui→core→data/external; UI never imports external.slack |
| astral.layers.scripts-exempt-from-layer-rules | scoped | conforms | Socket Mode script under scripts/ (ancestry) |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | production/listen decisions in core; React renders API state |
| astral.patterns.coat-check-never-store-empty | scoped | not-applicable | no coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | scoped | not-applicable | no consult |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | GET/PUT listen `@require_admin`; page AdminRoute |
| astral.standards.data-raises-caller-logs | scoped | conforms | data silent; corrupt/missing → None; core/UI decide |
| astral.standards.database-header-inventory | scoped | conforms | JSON under db_dir; no new SQLite tables |
| astral.standards.debug-contract-gated | scoped | conforms | Style D found→recorded on set/post when debug=True |
| astral.standards.dry-and-focused-functions | scoped | conforms | reuses non_production_reply_prefix; one post helper |
| astral.standards.in-scope-only | scoped | conforms | no Events/resolve/cache/turn-loop ownership |
| astral.standards.logging-via-utils | scoped | conforms | Contact get_logger; data layer silent |
| astral.standards.no-cross-contamination | scoped | conforms | listen keys only; skills/Events boundaries held |
| astral.standards.no-hardcoded-sets | scoped | conforms | production label + filename from CONTACT_CONFIG |
| astral.standards.public-then-helpers | scoped | conforms | public set/format/post; private hydrate below |
| astral.standards.utils-data-late-import-only | scoped | conforms | config.py has no data import |
| astral.state.core-decides-transitions | scoped | not-applicable | no candidate state transitions |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no job state |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no dispatch chain |
| astral.ui.frontend-file-placement | scoped | conforms | AdminManageSlack in pages/; AdminRoute wired |
| astral.ui.naming-conventions | scoped | conforms | snake_case /admin/manage_slack + API listen routes |
| astral.ui.single-gunicorn-worker | scoped | conforms | in-process CONTACT_CONFIG hydrate; per-volume file |
| orch.git.betty-merge-tests-one-sha | universal | conforms | single merge-tests SHA then origin/dev merge |
| orch.git.commit-vocabulary | universal | conforms | plan/code/test/merge-tests/merge vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | publish on origin/sub/AST-1043/AST-1067-… |
| orch.git.ftr-sub-topology | universal | conforms | matches parent Git table |
| orch.git.merge-on-checkout | universal | conforms | merge origin/dev on tip present |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | none observed |
| orch.git.no-dev-agent-branches | universal | conforms | uses sub/AST-1043/AST-1067-… |
| orch.git.one-epic-worktree-per-parent | universal | conforms | astral-AST-1043 |
| orch.git.three-permanent-branches | universal | conforms | no new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | durable-file Decision held |
| orch.pipeline.plan-is-bible | universal | conforms | stages 1–5 match tip product |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Contact child |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | no statute edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty owns tests/bible |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee Katherine through Tests Passed |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | implementer Katherine remains assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | doc-only review commit paths |

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.ui.manage-pages | conforms | AdminManageSlack + NAV + AdminRoute |
| pattern.ui.admin-endpoint | conforms | thin GET/PUT /api/admin/contact/listen |
| pattern.config.config-block | conforms | listen_state_filename + production_deploy_env |
| pattern.core.contact-agent (proposed) | conforms | hydrate/set + format/post helpers |

## Plan adherence

Stages 1–5 land: config/NAV, data JSON under db_dir, Contact hydrate/set + Style D, `@require_admin` listen API, Manage Slack page. Fail-closed corrupt/missing file; production prefix skip via config; UI never imports external.slack. Self-Assessment MAJOR-CHANGE / high / HIGH matches listen risk and mitigations.

## Findings

**discuss** — C4 straggler: Joan Excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, `astral.layers.scripts-exempt-from-layer-rules` now in-scope via tip ancestry (docs/tests/scripts). All score **conforms** — no product action.

## What’s solid

Per-volume durable listen; default-off + fail-closed; Contact owns prefix / external stays dumb; auth on API + AdminRoute; NAV↔routes path match.

Plan append: `docs/features/contact/ast-1067-manage-slack-admin-listen-switch.md` @ `9b2c81ed`.

context_tokens≈54000

— Radia

#### betty — 2026-07-30T16:14:45.343Z
## QA test manifest

`origin/sub/AST-1043/AST-1067-manage-slack-admin-listen-switch` @ `5e9e94cb` (`merge-tests(AST-1067): origin/tests 834ed480`)

1. `tests/component/utils/test_config.py::TestAst1067ContactListenConfig` — `listen_state_filename` / `production_deploy_env`; Manage Slack NAV after Manage Email
2. `tests/component/data/test_contact_listen.py::TestAst1067ContactListenData` — load missing/invalid; save round-trip; TypeError
3. `tests/component/core/test_contact.py::TestAst1067ContactListenCore` — hydrate/set listen; production gate; format prefix; `post_contact_reply` → `post_message`
4. `tests/component/ui/api/test_api_contact.py::TestAst1067ContactListenApi` — GET/PUT listen; 400/502; auth 401/403
5. `tests/component/frontend/pages/test_AdminManageSlack.test.tsx` — §6c routed page first-paint + Enable listen toggle

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1067ContactListenConfig \
  tests/component/data/test_contact_listen.py::TestAst1067ContactListenData \
  tests/component/core/test_contact.py::TestAst1067ContactListenCore \
  tests/component/ui/api/test_api_contact.py::TestAst1067ContactListenApi \
  -q

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminManageSlack.test.tsx
```

**Bible sha256** (`git show origin/sub/AST-1043/AST-1067-manage-slack-admin-listen-switch:<path> | sha256sum`):
- `docs/test-bible/core/contact.md` — `ff500712a62543c2f4b7e1d4f144c88d04a6880f284b1c52a82254c2219eab17`
- `docs/test-bible/utils/config.md` — `4d807611bd4a5a866c394ff9735dcff7c7464d7edd69fba8eeaa4af214876f3b`
- `docs/test-bible/data/contact_listen.md` — `0ed0a656034a5e8f2eae8bcd04d6d348592af3c89a24b0ef7c2c1e2c2cffe930`
- `docs/test-bible/ui/api/api_contact.md` — `b65307cc6c48fdf3c1e5da723552881560cd3be176da3e8ab3f131cc38888ec8`
- `docs/test-bible/frontend/pages.md` — `022319ed3f924a2f94a0dc8435e4d2dfcea771b7c1cb4edbcab88335b499708d`

**Broken / obsolete:** none — additive Manage Slack listen surface.

**Integration:** no existing scenario — no revision.

— Betty

#### joan — 2026-07-30T03:43:14.231Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1067
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 Estelle DM/@ ingress plumbing | N/A — boundary (AST-1069) |
| AC2 Events Request URL verify/ack | N/A — boundary (AST-1069) |
| AC3 Manage Slack listen + non-prod `[env]` prefix | Stages 1–5 (persist/flip listen; `format_contact_reply_text` / `post_contact_reply`) |
| AC4 resolve + PROSPECT | N/A — boundary (AST-1068) |
| AC5 routing exposes state | N/A — boundary (AST-1068) |
| AC6 conversation load/cache | N/A — boundary (AST-1070) |
| AC7 CONTACT_CONFIG skills/ACL | N/A — boundary (AST-1066/1071); listen keys only |
| AC8 debug=True found/recorded | Stage 3 Style D on set/post when `debug=True` |

### Child AC → plan stages

| Child AC | Plan coverage |
|----------|---------------|
| Manage Slack on/off for current environment | Stages 1–5 (JSON under db_dir + admin API + page) |
| Non-prod replies tagged `[<environment>]` | Stage 3 `format_contact_reply_text` / `post_contact_reply` |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 config + NAV | config-source-of-truth; parent Manage Slack surface |
| Stage 2 data JSON helper | durable per-volume listen; no SQLite |
| Stage 3 Contact hydrate/set/prefix/post | pattern.core.contact-agent; core-vs-external |
| Stage 4 admin GET/PUT listen | pattern.ui.admin-endpoint; require_admin |
| Stage 5 AdminManageSlack + route | frontend-file-placement; AdminRoute |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests |
| orch.git.commit-vocabulary | conforms | Sub publish vocabulary |
| orch.git.flow-direction-inviolable | conforms | origin/sub only |
| orch.git.ftr-sub-topology | conforms | Parent Git table match |
| orch.git.merge-on-checkout | conforms | Depends on ftr tip; no illegal merge |
| orch.git.no-cherry-pick-rebase-force | conforms | None |
| orch.git.no-dev-agent-branches | conforms | sub/AST-1043/AST-1067-… |
| orch.git.one-epic-worktree-per-parent | conforms | astral-AST-1043 |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Durable-file vs env-var Decision documented |
| orch.pipeline.plan-is-bible | conforms | Binding stages + Files Changed |
| orch.pipeline.project-scoped-queues | conforms | Contact child only |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate-plan |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | No tests/ |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Katherine) builds |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer path |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | No graded tasks |
| astral.agent.do-task-delegation | conforms | No do_task |
| astral.agent.grade-vector-validation | conforms | No grades |
| astral.batch.batch-id-first | conforms | No batch |
| astral.batch.batch-id-format | conforms | No batch_id |
| astral.batch.claim-process-release | conforms | No batch |
| astral.batch.entity-agent-responses-latest-only | conforms | No agent_data |
| astral.config.config-source-of-truth | conforms | Filename + production label + NAV in config |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | No Slack secrets in config; deploy label via existing helpers |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src |
| astral.layers.core-vs-external-bright-line | conforms | Prefix/post in Contact; raw post_message stays external |
| astral.layers.import-direction | conforms | ui→core→data/external; UI never imports external.slack |
| astral.layers.ui-config-driven-business-logic | conforms | Production compare + listen in core/config; React renders |
| astral.patterns.coat-check-never-store-empty | conforms | No coat-check |
| astral.patterns.render-verdict-orchestrates-consult | conforms | No consult |
| astral.patterns.require-auth-on-protected-endpoints | conforms | GET/PUT `@require_admin`; page AdminRoute |
| astral.standards.data-raises-caller-logs | conforms | Data silent; core/UI decide |
| astral.standards.database-header-inventory | conforms | JSON under db_dir; no new SQLite tables |
| astral.standards.debug-contract-gated | conforms | Style D on set/post when debug=True |
| astral.standards.dry-and-focused-functions | conforms | Reuses non_production_reply_prefix; one post helper |
| astral.standards.in-scope-only | conforms | Out of scope list complete |
| astral.standards.logging-via-utils | conforms | Contact get_logger; data silent |
| astral.standards.no-cross-contamination | conforms | No Events/resolve/cache/skills ownership |
| astral.standards.no-hardcoded-sets | conforms | Production label + filename from CONTACT_CONFIG |
| astral.standards.public-then-helpers | conforms | Public set/format/post; private hydrate |
| astral.standards.utils-data-late-import-only | conforms | No utils→data |
| astral.state.core-decides-transitions | conforms | No candidate state transitions |
| astral.state.job-prior-states-enforced | conforms | No jobs |
| astral.state.no-daisy-chain-in-run | conforms | No dispatch chain |
| astral.ui.frontend-file-placement | conforms | AdminManageSlack in pages/; styles not required beyond patterns |
| astral.ui.naming-conventions | conforms | snake_case `/admin/manage_slack` + API |
| astral.ui.single-gunicorn-worker | conforms | In-process CONTACT_CONFIG hydrate; per-volume file |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.patterns.require-auth-on-protected-endpoints, astral.standards.data-raises-caller-logs, astral.standards.database-header-inventory, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.frontend-file-placement, astral.ui.naming-conventions, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths match none of plan paths
- astral.debug.spikes-under-debug-dir — paths match none of plan paths
- astral.docs.features-single-file-per-ticket — layers {docs} ∩ plan empty
- astral.git.engineer-test-tree-ban — paths match none of plan paths
- astral.layers.scripts-exempt-from-layer-rules — layers {scripts} ∩ plan empty

## Findings

None fix-now.

**acceptable:** Self-assessment MAJOR-CHANGE / Conf high / Risk HIGH is honest; default-off + fail-closed corrupt JSON + per-volume isolation + production prefix skip are adequate mitigations — not Archie escalate. Mutating in-process `CONTACT_CONFIG["listen_enabled"]` after hydrate/set is an explicit Decision that keeps Events readers one-line.

**R6 checklist:** Definition fidelity pass (parent AC3). Layer/import pass. Config/secrets pass. File placement pass. No sibling creep. Depends on ftr with `contact_bp` (AST-1071 already present).

context_tokens≈56000

— Joan

#### katherine — 2026-07-30T03:40:26.568Z
Plan published for AST-1067.

**Plan:** [`docs/features/contact/ast-1067-manage-slack-admin-listen-switch.md`](https://github.com/susansomerset/astral/blob/sub/AST-1043/AST-1067-manage-slack-admin-listen-switch/docs/features/contact/ast-1067-manage-slack-admin-listen-switch.md) @ `e7d5cc7d` on `origin/sub/AST-1043/AST-1067-manage-slack-admin-listen-switch`.

**Approach:** Durable `contact_slack_listen.json` under this env’s `ASTRAL_DB_DIR` (per Railway volume); Contact hydrates/sets `CONTACT_CONFIG["listen_enabled"]`; admin GET/PUT `/api/admin/contact/listen`; Manage Slack page + NAV. Outbound tagging via `format_contact_reply_text` / `post_contact_reply` (external `post_message` stays dumb). Production skip uses `CONTACT_CONFIG["production_deploy_env"]`.

**Self-assessment**
- **Scope:** MAJOR-CHANGE — utils config/NAV + new data JSON helper + Contact listen/prefix/post + admin API + new React admin page/route.
- **Conf:** high — extends shipped listen flag / prefix template / `contact_bp` / Manage Email patterns; one JSON file per volume, no schema migration.
- **Risk:** HIGH — listen stuck on could make Estelle respond in the wrong env; mitigated by default-off, fail-closed corrupt file, per-volume isolation, production prefix skip.

---

# AST-1067 — Manage Slack: admin listen switch (per environment) + non-prod reply tag

**Linear:** [AST-1067](https://linear.app/astralcareermatch/issue/AST-1067/manage-slack-admin-listen-switch-per-environment-non-prod-reply-tag)  
**Parent:** [AST-1043](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent) — Slack Bot Agent  
**Publish ref:** `origin/sub/AST-1043/AST-1067-manage-slack-admin-listen-switch`

Admin **Manage Slack** page flips Contact’s Slack listen/respond flag for the **current deploy environment**, persists that choice under the env’s `ASTRAL_DB_DIR` volume, and applies the existing `[{environment}] ` prefix to Contact outbound reply text when the deploy is not production. Does **not** own Events verify/ack (AST-1069), resolve/PROSPECT (AST-1068), conversation cache (AST-1070), skill runners (AST-1071), or Estelle turn loop (AST-1046).

**Depends on:** AST-1069 on `origin/ftr/AST-1043-slack-bot-agent` (`CONTACT_CONFIG["listen_enabled"]`, `slack_listen_enabled()`, `non_production_reply_prefix()`, `post_message` in external, `contact_bp` registered). Merge that tip before build.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `listen_state_filename` + `production_deploy_env` to `CONTACT_CONFIG`; NAV item for Manage Slack | utils |
| `src/data/contact_listen.py` | New: read/write listen JSON under `ASTRAL_CONFIG["db_dir"]` (values only) | data |
| `src/core/contact.py` | Hydrate/set listen; `format_contact_reply_text` + `post_contact_reply`; Style D when `debug=True` | core |
| `src/ui/api/api_contact.py` | GET/PUT `/listen` on existing `contact_bp` (`@require_admin`) | ui |
| `src/ui/frontend/src/pages/AdminManageSlack.tsx` | New Manage Slack admin page (env label + listen toggle) | ui |
| `src/ui/frontend/src/routes.tsx` | Route `/admin/manage_slack` behind `AdminRoute` | ui |

No edits to `src/external/slack.py` (keep `post_message` dumb), Events blueprint, resolve/PROSPECT, skills ACL, or Estelle turn loop. Do **not** add a SQLite table.

---

## Stage 1: Config — listen persistence filename + production env label + NAV

**Done when:** `CONTACT_CONFIG` exposes filename + production deploy string; Admin nav lists Manage Slack; import-time asserts pass; no data/core/UI behavior change yet.

1. In `src/utils/config.py`, inside `CONTACT_CONFIG` (immediately after `"listen_enabled": False,`), add:

```python
    # Durable listen flag filename under ASTRAL_CONFIG["db_dir"] (per Railway volume / env).
    "listen_state_filename": "contact_slack_listen.json",
    # ASTRAL_DEPLOY_ENV value (case-insensitive) that skips non-prod reply prefix.
    "production_deploy_env": "production",
```

2. After the existing `assert isinstance(CONTACT_CONFIG["listen_enabled"], bool)`, add:

```python
assert isinstance(CONTACT_CONFIG["listen_state_filename"], str) and CONTACT_CONFIG["listen_state_filename"].endswith(".json")
assert isinstance(CONTACT_CONFIG["production_deploy_env"], str) and CONTACT_CONFIG["production_deploy_env"].strip()
```

3. In `NAV_CONFIG` Admin `items`, immediately after the Manage Email entry, append:

```python
            {"label": "Manage Slack", "path": "/admin/manage_slack"},
```

⚠️ **Decision — durable file, not env var / not SQLite:** Parent requires a per-environment flip operators control from Manage Slack. `ASTRAL_DEPLOY_ENV` already labels the process; a JSON file under that env’s `ASTRAL_DB_DIR` volume persists across restarts without a schema migration. Do **not** use `os.environ["SLACK_LISTEN_ENABLED"]` (Manage Slack cannot write Railway env vars at runtime). Do **not** store a multi-env map in one file — each deploy only ever reads/writes **its own** volume.

⚠️ **Decision — production label literal in config:** Prefix skip uses `CONTACT_CONFIG["production_deploy_env"]` compared case-insensitively to stripped `ASTRAL_DEPLOY_ENV` (§2.1 / no-hardcoded-sets). Unset / empty / `"Astral"` fallback deploy labels are **non-production** and get the prefix.

**Done when (recheck):** `CONTACT_CONFIG["listen_state_filename"] == "contact_slack_listen.json"`; `CONTACT_CONFIG["production_deploy_env"] == "production"`; NAV includes Manage Slack path `/admin/manage_slack`.

---

## Stage 2: Data layer — listen JSON read/write

**Done when:** `src/data/contact_listen.py` can load/save the listen bool under `db_dir`; missing/corrupt file → treat as no override; no logging; no core/UI callers yet.

1. Create `src/data/contact_listen.py`:

```python
"""Durable Contact Slack listen flag (AST-1067). Values only — no logging."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from src.utils.config import ASTRAL_CONFIG, CONTACT_CONFIG


def _listen_path() -> Path:
    return Path(ASTRAL_CONFIG["db_dir"]) / str(CONTACT_CONFIG["listen_state_filename"])


def load_contact_listen_enabled() -> Optional[bool]:
    """Return persisted listen bool, or None if missing/unreadable/invalid."""
    path = _listen_path()
    if not path.is_file():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None
    if not isinstance(raw, dict):
        return None
    val = raw.get("listen_enabled")
    if not isinstance(val, bool):
        return None
    return val


def save_contact_listen_enabled(enabled: bool) -> None:
    """Write ``{"listen_enabled": <bool>}`` (creates parent dirs as needed)."""
    if not isinstance(enabled, bool):
        raise TypeError("enabled must be bool")
    path = _listen_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"listen_enabled": enabled}, indent=2) + "\n",
        encoding="utf-8",
    )
```

⚠️ **Decision — Optional[bool] load:** `None` means “no durable override → keep `CONTACT_CONFIG["listen_enabled"]` default (`False`)”. Corrupt files fail closed (no override), same as missing.

**Done when (recheck):** Importing the module does not require Slack secrets; round-trip save → load returns the same bool on a temp `ASTRAL_DB_DIR`.

---

## Stage 3: Core — set/hydrate listen + outbound reply prefix + post helper

**Done when:** `slack_listen_enabled()` reflects durable state; admin can flip via `set_slack_listen_enabled`; `format_contact_reply_text` / `post_contact_reply` apply non-prod prefix; `debug=True` emits Style D on set + post; Events path still only **reads** listen.

1. Update `src/core/contact.py` module docstring to note AST-1067 Manage Slack listen + outbound prefix (still no Estelle turn loop).

2. Extend imports:

```python
from typing import Any, Dict, List, Optional, Tuple

from src.data.contact_listen import (
    load_contact_listen_enabled,
    save_contact_listen_enabled,
)
from src.external.slack import parse_url_verification, post_message, verify_slack_signature
from src.utils.deploy_status import get_deploy_label
```

(Keep existing candidate / logging imports. `post_message` joins the existing external.slack import used by Events — do not import slack from UI.)

3. After module-level `_seen_lock` / `_TEXT_DEBUG_MAX`, add:

```python
_listen_hydrated = False
```

4. Replace `slack_listen_enabled` body so it hydrates once from data, then returns the in-process flag:

```python
def slack_listen_enabled() -> bool:
    """Return Contact listen flag (durable override under db_dir, else CONTACT_CONFIG default)."""
    _hydrate_listen_state()
    return bool(CONTACT_CONFIG["listen_enabled"])
```

5. Add public helpers **immediately after** `non_production_reply_prefix` (before `contact_skill_meta`) — public-then-helpers:

```python
def contact_is_production_deploy() -> bool:
    """True when ASTRAL_DEPLOY_ENV matches CONTACT_CONFIG production_deploy_env (case-insensitive)."""
    ...

def set_slack_listen_enabled(enabled: bool, *, debug: bool = False) -> bool:
    """Persist + apply listen flag for this deploy environment. Returns the stored bool."""
    ...

def format_contact_reply_text(text: str) -> str:
    """Prefix non-production Contact replies with ``[<environment>] ``; production unchanged."""
    ...

def post_contact_reply(
    *,
    channel: str,
    text: str,
    thread_ts: Optional[str] = None,
    debug: bool = False,
) -> dict:
    """Format outbound text (non-prod prefix) then ``external.slack.post_message``."""
    ...
```

Concrete behavior for `contact_is_production_deploy`:
- `raw = os.environ.get("ASTRAL_DEPLOY_ENV", "").strip()`
- Return `raw.lower() == str(CONTACT_CONFIG["production_deploy_env"]).strip().lower()`

Concrete behavior for `set_slack_listen_enabled`:
- If `debug`: `logger.set_debug_flag(True)`.
- `enabled` must be `bool` — else `raise TypeError("enabled must be bool")`.
- Call `save_contact_listen_enabled(enabled)`.
- Set `CONTACT_CONFIG["listen_enabled"] = enabled`.
- Set `_listen_hydrated = True`.
- If `debug`: Style D found (requested value) then recorded (persisted value + `get_deploy_label()`), using `func="contact.set_slack_listen_enabled"`, `identifier="listen"`.
- Return `bool(CONTACT_CONFIG["listen_enabled"])`.

Concrete behavior for `_hydrate_listen_state` (private, below public API):
- If `_listen_hydrated`: return.
- `loaded = load_contact_listen_enabled()`.
- If `loaded is not None`: `CONTACT_CONFIG["listen_enabled"] = loaded`.
- Set `_listen_hydrated = True`.

Concrete behavior for `format_contact_reply_text`:
- `body = text if isinstance(text, str) else ""`
- If `contact_is_production_deploy()`: return `body`
- Return `non_production_reply_prefix(get_deploy_label()) + body`

Concrete behavior for `post_contact_reply`:
- If `debug`: `logger.set_debug_flag(True)`.
- `outbound = format_contact_reply_text(text)`
- If `debug`: Style D found (channel + truncated raw text) then recorded (truncated outbound + whether prefix applied), `func="contact.post_contact_reply"`, `identifier=channel`.
- `return post_message(channel=channel, text=outbound, thread_ts=thread_ts)` — do not catch; let transport errors propagate to callers.

⚠️ **Decision — Contact owns prefix, external stays dumb:** AST-1069 left `post_message` as raw Web API. Estelle (AST-1046) and any future Contact reply path must call `post_contact_reply` (or at least `format_contact_reply_text`) so non-prod tagging cannot be skipped by accident. Do **not** change `external.slack.post_message` signature.

⚠️ **Decision — prefix whenever non-production:** Apply prefix based on deploy env only (not gated on listen). Inbound listen gate remains `handle_slack_event` / `slack_listen_enabled()`. Parent AC: when listen is on **and** non-prod, replies are tagged — production never tagged.

⚠️ **Decision — mutate CONTACT_CONFIG in-process:** After hydrate/set, `CONTACT_CONFIG["listen_enabled"]` is the process source of truth so existing `slack_listen_enabled()` readers (Events) stay one-line and process-local. Durable file is the cross-restart source.

**Done when (recheck):** With a temp db_dir, `set_slack_listen_enabled(True)` → new process/module re-import path that calls `slack_listen_enabled()` after hydrate returns `True`; `format_contact_reply_text("hi")` with `ASTRAL_DEPLOY_ENV=staging` returns `"[staging] hi"`; with `ASTRAL_DEPLOY_ENV=production` returns `"hi"`.

---

## Stage 4: Admin API — GET/PUT listen on `contact_bp`

**Done when:** Authenticated admin can read and flip listen for the current environment via `/api/admin/contact/listen`; non-admin → 403.

1. In `src/ui/api/api_contact.py`, extend imports:

```python
from src.core.contact import (
    contact_is_production_deploy,
    contact_skills,
    run_contact_skill,
    set_slack_listen_enabled,
    slack_listen_enabled,
)
from src.utils.deploy_status import get_deploy_label, ui_llm_debug
```

2. Add routes on existing `contact_bp` (keep skills routes unchanged):

```python
@contact_bp.route("/listen", methods=["GET"])
@require_admin
def contact_get_listen():
    ...

@contact_bp.route("/listen", methods=["PUT"])
@require_admin
def contact_put_listen():
    ...
```

`GET` response `200`:

```json
{
  "listen_enabled": false,
  "environment": "staging",
  "is_production": false
}
```

- `listen_enabled` = `slack_listen_enabled()`
- `environment` = `get_deploy_label()`
- `is_production` = `contact_is_production_deploy()` (import from core; do not re-implement the compare in the route)

`PUT` body: `{"listen_enabled": <bool>}`. Reject missing/non-bool with `400` `{"error": "listen_enabled must be a bool"}`. Optional `debug` via query/body same pattern as skills route → `ui_llm_debug`. Call `set_slack_listen_enabled(enabled, debug=debug)`. Response `200` same shape as GET after the flip.

⚠️ **Decision — extend `api_contact`, not a new blueprint:** Listen is Contact’s flag; skills already live under `/api/admin/contact`. One admin Contact surface.

**Done when (recheck):** `GET /api/admin/contact/listen` as admin returns JSON with the three keys; `PUT` with `true` then `GET` shows `listen_enabled: true`; non-admin → 403.

---

## Stage 5: Frontend — Manage Slack page + route

**Done when:** Admin can open Manage Slack from the nav, see current environment, and toggle listen; route is admin-gated.

1. Create `src/ui/frontend/src/pages/AdminManageSlack.tsx`:
   - On mount: `GET /api/admin/contact/listen` via existing `api` helper; show loading / error / toast on failure (mirror `AdminManageEmail` patterns: `Toast`, padding 24, h1 “Manage Slack”).
   - Display: environment label; listen status text (`On` / `Off`); production note when `is_production` (e.g. “Production — replies are not prefixed”); when not production, note that replies are prefixed with `[<environment>] `.
   - Primary control: button “Enable listen” when off / “Disable listen” when on. On click: `PUT /api/admin/contact/listen` with `{"listen_enabled": <next>}`; update local state from response; toast success/error.
   - Keep the page minimal — no inbox tables, no Slack message list, no skills UI.

2. In `src/ui/frontend/src/routes.tsx`:
   - Import `AdminManageSlack`.
   - Add `{ path: "admin/manage_slack", element: <AdminRoute><AdminManageSlack /></AdminRoute> }` immediately after the `manage_email` route.

**Done when (recheck):** Nav → Manage Slack renders; toggle calls PUT and reflects new state; non-admin route blocked by `AdminRoute`.

---

## Out of scope (do not implement)

- Events verify/ack/dedupe / Socket Mode (AST-1069 — already on ftr).
- Resolve Slack user / PROSPECT create (AST-1068).
- Conversation cache / history load (AST-1070).
- Skill ACL runners beyond existing AST-1071 surface.
- Estelle conversational turn / calling `post_contact_reply` from the turn loop (AST-1046) — this ticket only provides the helper.
- Changing `external.slack.post_message` to auto-prefix.
- Multi-environment map in one process; Railway env-var mutation from the UI.

---

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — new data helper + Contact listen mutate/prefix/post + admin API + new admin React page/nav/route; touches utils, data, core, and ui.

**Conf:** `high` — builds on shipped `CONTACT_CONFIG["listen_enabled"]`, `non_production_reply_prefix`, `contact_bp` / `@require_admin`, and Manage Email page patterns; persistence path is a single JSON file under existing `db_dir`.

**Risk:** `HIGH` — a stuck listen=on could make Estelle respond in the wrong env; mitigated by default-off + fail-closed corrupt-file handling + explicit per-volume file (no cross-env bleed) + production prefix skip via config literal.

---

## Self-review vs ASTRAL_CODE_RULES

| Rule | Notes |
|------|--------|
| §1.1 / in-scope-only | Stages stay on listen UI + durable flag + outbound prefix helper; no Events/resolve/cache/turn-loop |
| §1.3 DRY | Prefix formatting reuses `non_production_reply_prefix`; post goes through one Contact helper |
| §2.1 config | Filename + production label literals in `CONTACT_CONFIG`; secrets unchanged |
| §2.5 / import-direction | UI → core → data/external; UI never imports `external.slack` |
| §2.9 require_admin | Both listen routes `@require_admin`; page behind `AdminRoute` |
| §3.2 no core file I/O | JSON read/write lives in `src/data/contact_listen.py` |
| §3.5 NAV ↔ routes | NAV path and `routes.tsx` path both `/admin/manage_slack` |
| No-hardcoded-sets | Production env string + filename from config |
| Debug contract | Style D only when `debug=True` on set/post |
| Database header inventory | N/A — no SQLite table |

---

## Review (build stub)

**Publish ref:** `origin/sub/AST-1043/AST-1067-manage-slack-admin-listen-switch`  
**Tip:** `dff0a9ae` — Manage Slack listen switch + non-prod reply tag (stages 1–5)  
**Stage commits:** `e78c26ab` (config/NAV), `20279fb3` (data JSON), `6b169178` (core listen/prefix/post), `01a0df99` (admin API), `dff0a9ae` (Manage Slack page + route)

---

## Review (Radia / code-rubric.v1)

[code-rubric] revision=1  
**Rubric:** code-rubric.v1  
**Ticket:** AST-1067  
**Publish ref:** `5a7659e5` on `origin/sub/AST-1043/AST-1067-manage-slack-admin-listen-switch` (docs tip follows)  
**Overall:** DISCUSS

**Diff change set:** `origin/dev...5a7659e5` — layers `{core, data, external, utils, ui, docs, scripts}`; tip carries AST-1066/1069/1071 ancestry plus AST-1067 Manage Slack listen; change_types `{add, modify}`.

### Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | conforms | no graded agent tasks |
| astral.agent.do-task-delegation | scoped | conforms | no do_task |
| astral.agent.grade-vector-validation | scoped | conforms | no grade vectors |
| astral.batch.batch-id-first | scoped | conforms | no batch claim |
| astral.batch.batch-id-format | scoped | conforms | no batch_id |
| astral.batch.claim-process-release | scoped | conforms | no batch processing |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | no agent_data |
| astral.config.config-source-of-truth | scoped | conforms | listen filename + production label + NAV in config |
| astral.config.pass-threshold-vs-score-floor | scoped | not-applicable | no threshold/score-floor edits |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | no Slack secrets in config; deploy label via helpers |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss artifacts/** / scripts/spikes/** |
| astral.debug.spikes-under-debug-dir | scoped | conforms | docs/features plans only — not spike notes |
| astral.docs.features-single-file-per-ticket | scoped | conforms | one plan file per ticket under docs/features/contact/ |
| astral.git.betty-no-src-or-features | scoped | conforms | merge-tests `5e9e94cb` tests/bible only |
| astral.git.engineer-test-tree-ban | scoped | conforms | tests/bible via Betty vocabulary |
| astral.layers.core-vs-external-bright-line | scoped | conforms | prefix/post in Contact; raw post_message stays external |
| astral.layers.import-direction | scoped | conforms | ui→core→data/external; UI never imports external.slack |
| astral.layers.scripts-exempt-from-layer-rules | scoped | conforms | Socket Mode script under scripts/ (ancestry) |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | production/listen decisions in core; React renders API state |
| astral.patterns.coat-check-never-store-empty | scoped | not-applicable | no coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | scoped | not-applicable | no consult |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | GET/PUT listen `@require_admin`; page AdminRoute |
| astral.standards.data-raises-caller-logs | scoped | conforms | data silent; corrupt/missing → None; core/UI decide |
| astral.standards.database-header-inventory | scoped | conforms | JSON under db_dir; no new SQLite tables |
| astral.standards.debug-contract-gated | scoped | conforms | Style D found→recorded on set/post when debug=True |
| astral.standards.dry-and-focused-functions | scoped | conforms | reuses non_production_reply_prefix; one post helper |
| astral.standards.in-scope-only | scoped | conforms | no Events/resolve/cache/turn-loop ownership |
| astral.standards.logging-via-utils | scoped | conforms | Contact get_logger; data layer silent |
| astral.standards.no-cross-contamination | scoped | conforms | listen keys only; skills/Events boundaries held |
| astral.standards.no-hardcoded-sets | scoped | conforms | production label + filename from CONTACT_CONFIG |
| astral.standards.public-then-helpers | scoped | conforms | public set/format/post; private hydrate below |
| astral.standards.utils-data-late-import-only | scoped | conforms | config.py has no data import |
| astral.state.core-decides-transitions | scoped | not-applicable | no candidate state transitions |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no job state |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no dispatch chain |
| astral.ui.frontend-file-placement | scoped | conforms | AdminManageSlack in pages/; AdminRoute wired |
| astral.ui.naming-conventions | scoped | conforms | snake_case /admin/manage_slack + API listen routes |
| astral.ui.single-gunicorn-worker | scoped | conforms | in-process CONTACT_CONFIG hydrate; per-volume file |
| orch.git.betty-merge-tests-one-sha | universal | conforms | single merge-tests SHA then origin/dev merge |
| orch.git.commit-vocabulary | universal | conforms | plan/code/test/merge-tests/merge vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | publish on origin/sub/AST-1043/AST-1067-… |
| orch.git.ftr-sub-topology | universal | conforms | matches parent Git table |
| orch.git.merge-on-checkout | universal | conforms | merge origin/dev on tip present |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | none observed |
| orch.git.no-dev-agent-branches | universal | conforms | uses sub/AST-1043/AST-1067-… |
| orch.git.one-epic-worktree-per-parent | universal | conforms | astral-AST-1043 |
| orch.git.three-permanent-branches | universal | conforms | no new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | durable-file Decision held |
| orch.pipeline.plan-is-bible | universal | conforms | stages 1–5 match tip product |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Contact child |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | no statute edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty owns tests/bible |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee Katherine through Tests Passed |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | implementer Katherine remains assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | doc-only review commit paths |

### Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.ui.manage-pages | conforms | AdminManageSlack + NAV + AdminRoute |
| pattern.ui.admin-endpoint | conforms | thin GET/PUT /api/admin/contact/listen |
| pattern.config.config-block | conforms | listen_state_filename + production_deploy_env |
| pattern.core.contact-agent (proposed) | conforms | hydrate/set + format/post helpers |

### Plan adherence

Stages 1–5 land: config/NAV, data JSON under db_dir, Contact hydrate/set + Style D, `@require_admin` listen API, Manage Slack page. Fail-closed corrupt/missing file; production prefix skip via config; UI never imports external.slack. Self-Assessment MAJOR-CHANGE / high / HIGH matches listen risk and mitigations.

### Findings

**discuss** — C4 straggler: Joan Excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, `astral.layers.scripts-exempt-from-layer-rules` now in-scope via tip ancestry (docs/tests/scripts). All score **conforms** — no product action.

### What’s solid

Per-volume durable listen; default-off + fail-closed; Contact owns prefix / external stays dumb; auth on API + AdminRoute; NAV↔routes path match.

context_tokens≈54000

---

## Resolution

**Date:** 2026-07-30  
**Review tip:** `9b2c81ed` (`docs(AST-1067): Radia review — findings`)  
**Overall:** DISCUSS — **no fix-now**

- Acknowledged Radia **discuss** C4 stragglers (`astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, `astral.layers.scripts-exempt-from-layer-rules`): tip-applicable via ancestry; all **conforms**. No product or plan ACL change.
- No product code changes in resolve.
