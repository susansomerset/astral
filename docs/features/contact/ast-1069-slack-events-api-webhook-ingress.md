<!-- linear-archive: AST-1069 archived 2026-08-11 -->

## Linear archive (AST-1069)

**Archived:** 2026-08-11  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1069/slack-events-api-webhook-ingress-external-slack-contact  
**Status at archive:** Archive  
**Project:** Astral Contact  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-1043 — Slack Bot Agent  
**Blocked by / blocks / related:** parent: AST-1043; blocks: AST-1070

### Description

## What this implements

Production Slack **Events API HTTP Request URL** ingress: verify signing secret, answer URL verification challenge, ack within ~3s, dedupe `event_id`, and route Estelle-relevant DMs / `@` mentions into Contact when listen is on. Web API `postMessage` for reply plumbing. Socket Mode stays **local/dev only** and feeds the same Contact handler. Does not own Manage Slack UI, resolve/PROSPECT, conversation cache, skill runners, or Estelle turn loop.

## Acceptance criteria

- [X] Production ingress is Events API HTTP Request URL (`POST /api/slack/events`), not Socket Mode.
- [X] Signature verify + URL challenge + immediate 200 ack; process-local `event_id` dedupe.
- [X] Mentions / DM messages route into Contact via `handle_slack_event` once listen is on.
- [X] Socket Mode remains available for local/dev only (`scripts/slack_socket_mode_dev.py`).
- [X] Railway/Slack Request URL operator checklist documented in the plan.

## Boundaries

Does not own CONTACT_CONFIG product surface (extends Events/Socket keys only), Manage Slack UI (AST-1067), candidate resolve/PROSPECT (AST-1068), conversation cache (AST-1070), skill runners (AST-1071), or Estelle conversational turn (AST-1046).

## In scope

- [X] `pattern.external.slack-events` (proposed) — `src/external/slack.py` verify / challenge / postMessage / Socket Mode helper
- [X] `pattern.api.routes` — thin `api_slack` blueprint registered on Flask (transport only; no ui→external)
- [X] `pattern.core.contact-agent` (proposed) — `receive_slack_events_http` + `handle_slack_event` on Contact
- [X] `pattern.config.config-block` — CONTACT_CONFIG Events path / bot_event_types / dedupe / app_token_env
- [X] `astral.config.config-source-of-truth` — ingress constants in config, not literals in UI/external
- [X] `astral.config.secrets-and-env-specific-from-environ` — bot/signing/app tokens via env names at call time (core/external, not UI)
- [X] `astral.layers.import-direction` — ui → core → external; UI never imports external
- [X] `astral.layers.core-vs-external-bright-line` — HMAC/HTTP/Socket I/O only in external
- [X] `astral.patterns.require-auth-on-protected-endpoints` — Events route intentionally open; Slack signature is auth
- [X] `astral.standards.no-hardcoded-sets` — event types / path / dedupe max from CONTACT_CONFIG
- [X] `astral.standards.debug-contract-gated` — Style D found/recorded on Contact inbound when `debug=True`
- [X] `astral.standards.in-scope-only` / `astral.standards.no-cross-contamination` — sibling scopes excluded
- [X] `astral.standards.public-then-helpers` / `astral.standards.dry-and-focused-functions` — receive/verify/post/handle as public surface
- [X] `astral.standards.logging-via-utils` — Contact debug/outcome via get_logger; external does not log outcomes

## Considered but excluded

- [X] `pattern.ui.admin-endpoint` — Manage Slack listen flip is AST-1067
- [X] `pattern.state.entity-state-transitions` / PROSPECT registry — AST-1068 resolve + create
- [X] `pattern.agent.estelle-turn` (proposed) — conversational envelope is AST-1046 / AST-1072
- [X] `astral.standards.database-header-inventory` — no schema/table changes; process-local dedupe only
- [X] Socket Mode as production ingress — parent AC forbids; local script only

## Notes for planning

Depends on AST-1066 (`CONTACT_CONFIG` + `slack_listen_enabled()`). Request URL = webhook; Socket Mode = local listener. Slack subscription `message.im` vs payload type `message` — see plan Stage 5.

## Git branch (authoritative)

Parent `ftr/AST-1043-slack-bot-agent`; child `sub/AST-1043/AST-1069-slack-events-api-webhook-ingress`. Created at dispatch-parent.

## Plan

`docs/features/contact/ast-1069-slack-events-api-webhook-ingress.md` @ `origin/sub/AST-1043/AST-1069-slack-events-api-webhook-ingress` tip `3069520f`.

### Comments

#### betty — 2026-07-30T03:33:50.887Z
merge-tests hygiene: collapsed duplicate `merge-tests(AST-1069)` commits on `origin/sub/AST-1043/AST-1069-slack-events-api-webhook-ingress` → exactly one: `9107d11f` (`origin/tests 1d2bf80e`). Tip tree unchanged (product + tests). Dropped empty `0c9d89c3`.

#### chuckles — 2026-07-30T03:31:48.534Z
[merge-child] blocked: duplicate merge-tests(AST-1069) on sub — count=2 (amend on tests, one merge-tests only)

Commits:
- `650a0d51` merge-tests(AST-1069): origin/tests 1d2bf80e…
- `0c9d89c3` merge-tests(AST-1069): origin/tests 26fe570b…

@Betty White — tests hygiene: leave exactly one `merge-tests(AST-1069)` on `origin/sub/AST-1043/AST-1069-slack-events-api-webhook-ingress`, then Chuckles will re-run merge-child.

— Chuckles

#### radia — 2026-07-30T03:27:33.399Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1069
**Publish ref:** `3462a2fd` on `origin/sub/AST-1043/AST-1069-slack-events-api-webhook-ingress`
**Overall:** DISCUSS

**Diff change set:** `origin/dev...3462a2fd` — layers `{core, external, utils, ui, docs, scripts}`; paths `src/external/slack.py` (A), `src/core/contact.py` (A), `src/ui/api/api_slack.py` (A), `src/ui/server.py` (M), `src/utils/config.py` (M), `scripts/slack_socket_mode_dev.py` (A), `requirements.txt` (M), plan/bible/tests; change_types `{add, modify}`. Tip carries AST-1066 scaffold ancestry (empty skills); not AST-1071.

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | conforms | no graded agent tasks |
| astral.agent.do-task-delegation | scoped | conforms | no do_task; CONTACT ≠ TASK_CONFIG |
| astral.agent.grade-vector-validation | scoped | conforms | no grade vectors |
| astral.batch.batch-id-first | scoped | conforms | no batch claim API |
| astral.batch.batch-id-format | scoped | conforms | no batch_id |
| astral.batch.claim-process-release | scoped | conforms | no batch processing |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | no agent_data entity refs |
| astral.config.config-source-of-truth | scoped | conforms | events path / bot_event_types / dedupe / env names in CONTACT_CONFIG |
| astral.config.pass-threshold-vs-score-floor | scoped | not-applicable | no threshold/score-floor edits |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | strict os.environ at call time in core/external; no import-time reads |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss artifacts/** / scripts/spikes/** |
| astral.debug.spikes-under-debug-dir | scoped | conforms | docs/features plans only — not spike notes |
| astral.docs.features-single-file-per-ticket | scoped | conforms | one plan file per ticket under docs/features/contact/ |
| astral.git.betty-no-src-or-features | scoped | conforms | tip merge-tests `650a0d51` tests/bible only |
| astral.git.engineer-test-tree-ban | scoped | conforms | tests/bible via Betty test/merge-tests vocabulary |
| astral.layers.core-vs-external-bright-line | scoped | conforms | HMAC/HTTP/Socket I/O only in external |
| astral.layers.import-direction | scoped | conforms | ui→core only; core→external; script exempt callers |
| astral.layers.scripts-exempt-from-layer-rules | scoped | conforms | Socket Mode local script under scripts/ |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | path/event types/listen from config via Contact |
| astral.patterns.coat-check-never-store-empty | scoped | not-applicable | no coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | scoped | not-applicable | no consult/render_verdict |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | Events route open; Slack signature auth via core |
| astral.standards.data-raises-caller-logs | scoped | conforms | external raises on post; Contact decides verify outcomes |
| astral.standards.database-header-inventory | scoped | not-applicable | no data/schema paths |
| astral.standards.debug-contract-gated | scoped | conforms | Style D on receive/handle when debug=True; quiet when False |
| astral.standards.dry-and-focused-functions | scoped | conforms | receive / verify / post / handle split |
| astral.standards.in-scope-only | scoped | conforms | no Manage Slack / resolve / skills / turn-loop |
| astral.standards.logging-via-utils | scoped | conforms | Contact get_logger Style D; external does not log outcomes |
| astral.standards.no-cross-contamination | scoped | conforms | skills stay empty; no TASK_CONFIG / sibling product |
| astral.standards.no-hardcoded-sets | scoped | conforms | event types/path/dedupe from config; skew/timeout named module constants |
| astral.standards.public-then-helpers | scoped | conforms | public ingress API present; private helpers grouped with handle path |
| astral.standards.utils-data-late-import-only | scoped | conforms | config.py has no data import |
| astral.state.core-decides-transitions | scoped | not-applicable | no state transitions |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no job state work |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no dispatch run_next |
| astral.ui.frontend-file-placement | scoped | not-applicable | no src/ui/frontend/** |
| astral.ui.naming-conventions | scoped | conforms | snake_case /api/slack/events |
| astral.ui.single-gunicorn-worker | scoped | conforms | process-local dedupe; multi-worker OOS as planned |
| orch.git.betty-merge-tests-one-sha | universal | conforms | authoritative merge-tests tip `650a0d51` (prior empty merge ignored) |
| orch.git.commit-vocabulary | universal | conforms | plan/code/test/merge-tests vocabulary on sub |
| orch.git.flow-direction-inviolable | universal | conforms | publish on origin/sub/AST-1043/AST-1069-… |
| orch.git.ftr-sub-topology | universal | conforms | matches parent Git table |
| orch.git.merge-on-checkout | universal | conforms | no illegal merge recipe |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | none in tip history |
| orch.git.no-dev-agent-branches | universal | conforms | uses sub/AST-1043/AST-1069-… |
| orch.git.one-epic-worktree-per-parent | universal | conforms | astral-AST-1043 epic worktree |
| orch.git.three-permanent-branches | universal | conforms | no new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Joan round=1 import-direction fixed; Decisions held |
| orch.pipeline.plan-is-bible | universal | conforms | stages 1–5 + Revision 1 match tip |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Contact child scope |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | no statute corpus edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty owns tests/bible |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee Hedy through Tests Passed |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | implementer Hedy remains assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | doc-only review commit paths |

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.external.slack-events (proposed) | conforms | verify / challenge / postMessage / Socket Mode helper |
| pattern.api.routes | conforms | thin api_slack transport-only |
| pattern.core.contact-agent (proposed) | conforms | receive_slack_events_http + handle_slack_event |
| pattern.config.config-block | conforms | CONTACT_CONFIG Events/Socket keys |

## Plan adherence

Stages 1–5 land; Revision 1 import-direction fix present (UI never imports external; signing secret read in Contact). Listen gate, signature verify, URL challenge, daemon-thread ack, process-local dedupe, Socket Mode script local-only. Self-Assessment MAJOR-CHANGE / high / HIGH matches open-webhook risk and mitigations. Sibling scopes clean (empty skills; no resolve/Manage Slack/turn-loop).

## Findings

**discuss** — C4 straggler: Joan Excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban` now in-scope on tip (docs/features + tests/bible). All three score **conforms** — no product action.

## What’s solid

ui→core→external after Joan Plan Discuss; HMAC + listen gate + empty 200 ack; config-driven path/types/dedupe; external silent on outcomes; Socket Mode confined to scripts/.

Plan append: `docs/features/contact/ast-1069-slack-events-api-webhook-ingress.md` @ `3462a2fd`.

context_tokens≈58000

— Radia

#### betty — 2026-07-30T03:23:50.912Z
## QA test manifest — AST-1069

`origin/sub/AST-1043/AST-1069-slack-events-api-webhook-ingress` @ `650a0d51`

- `merge-tests(AST-1069): origin/tests 1d2bf80ea8abd4d4596ebd8350ea655a0994dda3` (Betty paths overlay via `-s ours`; tip vs `3069520f` is tests/bible only)
- Prior empty `merge-tests` @ `0c9d89c3` was a no-op against wrong SHA — ignore; tip `650a0d51` is authoritative.

### Manifest

1. `tests/component/utils/test_config.py::TestAst1069ContactEventsConfig`
2. `tests/component/external/test_slack.py::TestAst1069ExternalSlack`
3. `tests/component/core/test_contact.py::TestAst1069ContactSlackIngress`
4. `tests/component/ui/api/test_api_slack.py::TestAst1069SlackEventsApi`
5. `tests/component/core/test_contact.py::TestAst1066ContactScaffold` (scaffold still green; empty skills)
6. `tests/component/utils/test_config.py::TestAst1066ContactConfig`

### Run

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1069ContactEventsConfig \
  tests/component/external/test_slack.py::TestAst1069ExternalSlack \
  tests/component/core/test_contact.py::TestAst1069ContactSlackIngress \
  tests/component/ui/api/test_api_slack.py::TestAst1069SlackEventsApi \
  tests/component/core/test_contact.py::TestAst1066ContactScaffold \
  tests/component/utils/test_config.py::TestAst1066ContactConfig \
  -q
```

(21 passed vs tip product.)

### Broken / obsolete
none — additive Events/Socket keys + ingress handlers + external slack + thin blueprint.

### Bible shasums (`origin/sub/…` tip, sha256)

- `docs/test-bible/core/contact.md` — `3c5b16b5d72bd3266274f3a139375f0657b417e5a05efcf94d8f7c00625dd24c`
- `docs/test-bible/external/slack.md` — `e87a70ec5908e1aeb080452e6bff19e6c7ea33ffd16a25e27dfc3da91e5d2092`
- `docs/test-bible/ui/api/api_slack.md` — `ea16176b3604650c382819bb94e2965a195d1a00611a56663229dbad8c198f11`
- `docs/test-bible/utils/config.md` — `38b120e6af0dabe00b54420d5a45e21149ac379000ee0982b3f529e9b253dd7e`

#### joan — 2026-07-30T03:13:08.343Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1069
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 Estelle DM/@ ingress + reply plumbing | Stages 2–4 (ingress); `post_message` for reply plumbing; turn loop N/A (AST-1046) |
| AC2 Events Request URL verify/ack; DM/@ reach Contact when listen on | Stages 2–4 + Stage 5 Production Request URL |
| AC3 Manage Slack listen + `[env]` prefix | N/A — boundary (AST-1067); this child only reads `listen_enabled` |
| AC4 resolve + PROSPECT | N/A — boundary (AST-1068) |
| AC5 routing exposes state | N/A — boundary (AST-1068) |
| AC6 conversation load/cache | N/A — boundary (AST-1070) |
| AC7 CONTACT_CONFIG skills/ACL | N/A — extends Events/Socket keys only; skills ACL is AST-1066/1071 |
| AC8 debug=True found/recorded | Stage 3 Style D on receive/handle when `debug=True` |

### Child AC → plan stages

| Child AC | Plan coverage |
|----------|---------------|
| Production ingress Events HTTP Request URL | Stages 4–5 |
| Signature verify + challenge + 200 ack; event_id dedupe | Stages 2–3 |
| Mentions/DM → Contact via `handle_slack_event` when listen on | Stage 3 |
| Socket Mode local/dev only | Stages 2, 5 |
| Railway/Slack Request URL checklist in plan | Stage 5 |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 CONTACT_CONFIG Events/Socket keys | config-source-of-truth; no-hardcoded-sets |
| Stage 2 `src/external/slack.py` | pattern.external.slack-events; core-vs-external I/O |
| Stage 3 `receive_slack_events_http` + `handle_slack_event` | ui→core→external; listen gate; debug contract |
| Stage 4 `api_slack` transport-only | thin Events webhook entry; parent AC2 |
| Stage 5 Socket script + Railway checklist | Socket Mode local-only; operator wiring |

**Notes:** Files Changed layer `deps` for `requirements.txt` mapped as `docs` for matching. Prior Plan Discuss round=1 (concern+reply) completed; re-validate from Plan Ready on tip `433b8574`.

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests |
| orch.git.commit-vocabulary | conforms | Sub publish vocabulary |
| orch.git.flow-direction-inviolable | conforms | origin/sub only |
| orch.git.ftr-sub-topology | conforms | Parent Git table match |
| orch.git.merge-on-checkout | conforms | No illegal merge |
| orch.git.no-cherry-pick-rebase-force | conforms | None |
| orch.git.no-dev-agent-branches | conforms | sub/AST-1043/AST-1069-… |
| orch.git.one-epic-worktree-per-parent | conforms | astral-AST-1043 |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Decisions + stop→parent on Socket underspec |
| orch.pipeline.plan-is-bible | conforms | Binding stages + Revision 1 delta |
| orch.pipeline.project-scoped-queues | conforms | Contact child only |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready re-validate after discuss |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | No tests/ |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Hedy) builds |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer path |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | No graded tasks |
| astral.agent.do-task-delegation | conforms | No do_task |
| astral.agent.grade-vector-validation | conforms | No grades |
| astral.batch.batch-id-first | conforms | No batch claim |
| astral.batch.batch-id-format | conforms | No batch_id |
| astral.batch.claim-process-release | conforms | No batch |
| astral.batch.entity-agent-responses-latest-only | conforms | No agent_data |
| astral.config.config-source-of-truth | conforms | Path/event types/dedupe/env names in CONTACT_CONFIG |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | Strict environ at call time in core/external |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src |
| astral.layers.core-vs-external-bright-line | conforms | HMAC/HTTP/Socket helpers in external only |
| astral.layers.import-direction | conforms | UI→core only; core→external; Revision 1 fixed prior violate |
| astral.layers.scripts-exempt-from-layer-rules | conforms | Socket Mode script under scripts/ |
| astral.layers.ui-config-driven-business-logic | conforms | Listen/event types from config via Contact |
| astral.patterns.coat-check-never-store-empty | conforms | No coat-check |
| astral.patterns.render-verdict-orchestrates-consult | conforms | No consult |
| astral.patterns.require-auth-on-protected-endpoints | conforms | Events route open; Slack signature auth via core |
| astral.standards.data-raises-caller-logs | conforms | External raises; Contact decides |
| astral.standards.debug-contract-gated | conforms | Style D on Contact inbound when debug=True |
| astral.standards.dry-and-focused-functions | conforms | receive/verify/post/handle split |
| astral.standards.in-scope-only | conforms | Sibling Out of scope list |
| astral.standards.logging-via-utils | conforms | Contact logs; external does not log outcomes |
| astral.standards.no-cross-contamination | conforms | No resolve/Manage Slack/skills |
| astral.standards.no-hardcoded-sets | conforms | Event types/path/dedupe from config |
| astral.standards.public-then-helpers | conforms | Public receive/handle/verify/post surface |
| astral.standards.utils-data-late-import-only | conforms | No utils→data |
| astral.state.core-decides-transitions | conforms | No state transitions |
| astral.state.job-prior-states-enforced | conforms | No jobs |
| astral.state.no-daisy-chain-in-run | conforms | No dispatch chain |
| astral.ui.naming-conventions | conforms | snake_case `/api/slack/events` |
| astral.ui.single-gunicorn-worker | conforms | Process-local dedupe; multi-worker OOS |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.scripts-exempt-from-layer-rules, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.patterns.require-auth-on-protected-endpoints, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.naming-conventions, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths match none of plan paths
- astral.debug.spikes-under-debug-dir — paths match none of plan paths
- astral.docs.features-single-file-per-ticket — paths match none of plan paths
- astral.git.engineer-test-tree-ban — paths match none of plan paths
- astral.standards.database-header-inventory — layers {data} ∩ plan empty
- astral.ui.frontend-file-placement — paths match none of plan paths

## Findings

None fix-now.

**Round 1 disposition:** Prior import-direction violate resolved — `receive_slack_events_http` in core; Stage 4 transport-only; Stage 5 `message.im` vs payload `message` clarified.

**acceptable:** Self-assessment MAJOR-CHANGE / Conf high / Risk HIGH remains honest; signature (core→external) + listen gate + empty 200 ack are adequate mitigations. Not escalate.

**R6 checklist:** Definition fidelity pass. Layer/import pass after Revision 1. Config/secrets pass. Open Events route intentional (§2.9). No sibling creep.

context_tokens≈58000

— Joan

#### hedy — 2026-07-30T03:09:15.889Z
[plan-discuss] round=1 reply

**Delta:** Fixed Joan fix-now on `astral.layers.import-direction`.

- Stage 3: added Contact `receive_slack_events_http(raw_body, timestamp=, signature=, debug=)` — loads signing secret, calls external verify + challenge parse, daemon-threads `handle_slack_event`, returns `(status, body)`.
- Stage 4: `api_slack` is transport-only (raw body + Slack headers → core). **No** ui→external imports; **no** signing-secret environ reads in UI.
- Stage 2 / Files Changed: external callers = core + scripts only.
- Stage 5: clarified Slack subscription `message.im` vs payload `event.type == "message"` in `bot_event_types`.

**Plan tip:** `433b8574` — https://github.com/susansomerset/astral/blob/sub/AST-1043/AST-1069-slack-events-api-webhook-ingress/docs/features/contact/ast-1069-slack-events-api-webhook-ingress.md

Returning to **Plan Ready**.

#### joan — 2026-07-30T03:07:13.060Z
[plan-discuss] round=1 concern
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1069
**Overall:** REVISE

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 Estelle DM/@ ingress + reply plumbing | Stages 2–4 (ingress); `post_message` for reply plumbing; turn loop N/A (AST-1046) |
| AC2 Events Request URL verify/ack; DM/@ reach Contact when listen on | Stages 2–4 + Stage 5 Production Request URL |
| AC3 Manage Slack listen + `[env]` prefix | N/A — boundary (AST-1067); this child only reads `listen_enabled` |
| AC4 resolve + PROSPECT | N/A — boundary (AST-1068) |
| AC5 routing exposes state | N/A — boundary (AST-1068) |
| AC6 conversation load/cache | N/A — boundary (AST-1070) |
| AC7 CONTACT_CONFIG skills/ACL | N/A — extends Events/Socket keys only; skills ACL is AST-1066/1071 |
| AC8 debug=True found/recorded | Stage 3 `handle_slack_event(..., debug=)` Style D |

### Child AC → plan stages

| Child AC | Plan coverage |
|----------|---------------|
| Production ingress Events HTTP Request URL | Stages 4–5 |
| Signature verify + challenge + 200 ack; event_id dedupe | Stages 2–4 |
| Mentions/DM → Contact via `handle_slack_event` when listen on | Stage 3–4 |
| Socket Mode local/dev only | Stages 2, 5 |
| Railway/Slack Request URL checklist in plan | Stage 5 |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 CONTACT_CONFIG Events/Socket keys | config-source-of-truth; no-hardcoded-sets |
| Stage 2 `src/external/slack.py` | pattern.external.slack-events; core-vs-external I/O |
| Stage 3 `handle_slack_event` | pattern.core.contact-agent inbound; listen gate; debug contract |
| Stage 4 `api_slack` + register | thin Events webhook entry; parent AC2 |
| Stage 5 Socket script + Railway checklist | Socket Mode local-only; operator wiring |

**Notes:** Files Changed layer `deps` for `requirements.txt` mapped as `docs` for matching (unrecognized layer).

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests |
| orch.git.commit-vocabulary | conforms | Sub publish vocabulary |
| orch.git.flow-direction-inviolable | conforms | origin/sub only |
| orch.git.ftr-sub-topology | conforms | Parent Git table match |
| orch.git.merge-on-checkout | conforms | No illegal merge |
| orch.git.no-cherry-pick-rebase-force | conforms | None |
| orch.git.no-dev-agent-branches | conforms | sub/AST-1043/AST-1069-… |
| orch.git.one-epic-worktree-per-parent | conforms | astral-AST-1043 |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Decisions documented; stop→parent on Socket underspec |
| orch.pipeline.plan-is-bible | conforms | Binding stages present |
| orch.pipeline.project-scoped-queues | conforms | Contact child only |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready gate |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | No tests/ |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Hedy) builds |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer path |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | No graded tasks |
| astral.agent.do-task-delegation | conforms | No do_task |
| astral.agent.grade-vector-validation | conforms | No grades |
| astral.batch.batch-id-first | conforms | No batch claim |
| astral.batch.batch-id-format | conforms | No batch_id |
| astral.batch.claim-process-release | conforms | No batch |
| astral.batch.entity-agent-responses-latest-only | conforms | No agent_data |
| astral.config.config-source-of-truth | conforms | Path/event types/dedupe/env names in CONTACT_CONFIG |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | Strict environ at call time; no import-time crash |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src |
| astral.layers.core-vs-external-bright-line | conforms | HMAC/HTTP/Socket helpers live in external (Stage 2) |
| astral.layers.import-direction | **violates** | Stage 4 UI calls external verify/challenge — ui may import core/utils only |
| astral.layers.scripts-exempt-from-layer-rules | conforms | Socket Mode script under scripts/ |
| astral.layers.ui-config-driven-business-logic | conforms | Listen/event types from config via Contact |
| astral.patterns.coat-check-never-store-empty | conforms | No coat-check |
| astral.patterns.render-verdict-orchestrates-consult | conforms | No consult |
| astral.patterns.require-auth-on-protected-endpoints | conforms | Events route intentionally open; Slack signature is auth (§2.9) |
| astral.standards.data-raises-caller-logs | conforms | External raises; Contact/UI decide |
| astral.standards.debug-contract-gated | conforms | Style D on Contact inbound when debug=True |
| astral.standards.dry-and-focused-functions | conforms | verify/post/handle split |
| astral.standards.in-scope-only | conforms | Sibling Out of scope list |
| astral.standards.logging-via-utils | conforms | Contact logs; external does not log outcomes |
| astral.standards.no-cross-contamination | conforms | No resolve/UI Manage Slack/skills |
| astral.standards.no-hardcoded-sets | conforms | Event types/path/dedupe from config |
| astral.standards.public-then-helpers | conforms | Public verify/post/handle surface |
| astral.standards.utils-data-late-import-only | conforms | No utils→data |
| astral.state.core-decides-transitions | conforms | No state transitions |
| astral.state.job-prior-states-enforced | conforms | No jobs |
| astral.state.no-daisy-chain-in-run | conforms | No dispatch chain |
| astral.ui.naming-conventions | conforms | snake_case `/api/slack/events` |
| astral.ui.single-gunicorn-worker | conforms | Process-local dedupe assumes single worker; multi-worker noted OOS |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.scripts-exempt-from-layer-rules, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.patterns.require-auth-on-protected-endpoints, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.naming-conventions, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths match none of plan paths
- astral.debug.spikes-under-debug-dir — paths match none of plan paths
- astral.docs.features-single-file-per-ticket — paths match none of plan paths
- astral.git.engineer-test-tree-ban — paths match none of plan paths
- astral.standards.database-header-inventory — layers {data} ∩ plan empty
- astral.ui.frontend-file-placement — paths match none of plan paths

## Findings

### fix-now — Stage 4 UI → external import (import-direction)

**Location:** Stage 4 `api_slack.py` — calls `verify_slack_signature` / `parse_url_verification` from `src.external.slack`, and reads `os.environ[CONTACT_CONFIG["signing_secret_env"]]` in the UI layer.

**Finding:** `astral.layers.import-direction` — **ui may import core and utils only; never external**. Existing `src/ui/api/*` modules do not import `src.external`. Stage 2 correctly puts HMAC/HTTP in external, but Stage 4 wires the blueprint to call external directly.

**Recommendation:** Keep blueprint thin: read raw body + Slack headers only; call a **core** entrypoint (e.g. extend Contact with `receive_slack_events_http(raw_body, timestamp, signature) -> (status_code, body_dict_or_bytes)`) that (1) loads signing secret / calls external verify + challenge parse, (2) returns challenge response or 401, (3) on event payloads schedules/calls `handle_slack_event`. UI must not import `src.external.slack`. Daemon-thread ack-then-process can stay in UI **or** move into that core entry — either is fine if UI→external is gone.

### discuss (non-blocking)

- **HIGH risk** self-assessment is honest; signature check + listen gate + empty 200 ack are adequate mitigations **after** the layering fix — not an Archie escalate by itself.
- Stage 5 checklist `message.im` vs config `bot_event_types` containing payload type `message` is a Slack subscription-vs-payload naming quirk — clarify in plan so operators subscribe correctly without changing Contact filters.

context_tokens≈55000

— Joan

#### hedy — 2026-07-30T03:03:15.462Z
Plan published on `origin/sub/AST-1043/AST-1069-slack-events-api-webhook-ingress`.

**Plan:** https://github.com/susansomerset/astral/blob/sub/AST-1043/AST-1069-slack-events-api-webhook-ingress/docs/features/contact/ast-1069-slack-events-api-webhook-ingress.md (`fd5e8439`)

**Scope:** `MAJOR-CHANGE` — new `src/external/slack.py`, Events webhook blueprint, Contact `handle_slack_event`, Socket Mode local script, and CONTACT_CONFIG ingress keys.

**Conf:** `high` — AST-1066 left env-name + listen contracts; Slack verify/ack/post is a fixed Events API contract; layering matches existing external modules.

**Risk:** `HIGH` — bad verify/ack can take Estelle offline workspace-wide or leave an open webhook; mitigated by HMAC signature check, listen gate, empty immediate 200, and no Bearer-protected data on this route.

---

# AST-1069 — Slack Events API webhook ingress

**Linear:** [AST-1069](https://linear.app/astralcareermatch/issue/AST-1069/slack-events-api-webhook-ingress-external-slack-contact)  
**Parent:** [AST-1043](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent) — Slack Bot Agent  
**Publish ref:** `origin/sub/AST-1043/AST-1069-slack-events-api-webhook-ingress`

Ship production **Slack Events API HTTP Request URL** ingress: verify signing secret, answer URL verification challenge, **ack within ~3s**, dedupe `event_id`, and route Estelle-relevant DMs / `@` mentions into **Contact** when listen is on. Provide **Web API postMessage** for reply plumbing (AST-1046). Keep **Socket Mode** as a **local/dev-only** listener that feeds the same Contact handler. Does **not** own Manage Slack UI, resolve/PROSPECT, conversation cache, CONTACT_CONFIG skills ACL bodies, or Estelle turn loop.

Depends on **AST-1066** (`CONTACT_CONFIG` env-name contracts + `slack_listen_enabled()`).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Extend `CONTACT_CONFIG` with Events path, bot event types, dedupe max, Socket Mode app-token env name | utils |
| `src/external/slack.py` | New module: signature verify, URL challenge parse, `post_message`, Socket Mode connect helper | external |
| `src/core/contact.py` | HTTP ingress entry (`receive_slack_events_http`) + inbound `handle_slack_event`: verify/challenge via external, listen gate, event_id dedupe, mention/DM filter, optional `debug=` found/recorded lines | core |
| `src/ui/api/api_slack.py` | Thin blueprint `POST /api/slack/events` — raw body + Slack headers only; calls Contact core; **never** imports `src.external` | ui |
| `src/ui/server.py` | Register `slack_bp` | ui |
| `scripts/slack_socket_mode_dev.py` | Local/dev Socket Mode listener → same Contact handler | scripts |
| `requirements.txt` | Add `websocket-client` for Socket Mode local script only | deps |

No frontend pages. No Manage Slack. No `get_candidate_id_for_query` / PROSPECT. No conversation cache table. No Estelle dialogue (AST-1046).

---

## Stage 1: Config — Events + Socket Mode contracts

**Done when:** `CONTACT_CONFIG` exposes ingress path, subscribed bot event types, dedupe capacity, and Socket Mode app-token env name; secrets remain env **names** only; asserts pass.

1. In `src/utils/config.py`, **extend** existing `CONTACT_CONFIG` (do not replace listen/skills/env names from AST-1066) with:

```python
    # AST-1069: Events API Request URL path (Flask route under /api).
    "events_http_path": "/slack/events",
    # Bot events Contact accepts when listen is on (Slack Event Subscriptions must match).
    "bot_event_types": ("app_mention", "message"),
    # Process-local event_id dedupe capacity (single gunicorn worker — AST/Railway).
    "event_id_dedupe_max": 4096,
    # Socket Mode (local/dev only) — app-level token env name (xapp-…).
    "app_token_env": "SLACK_APP_TOKEN",
```

2. Asserts: `events_http_path` starts with `/`; `bot_event_types` non-empty tuple of str; `event_id_dedupe_max` int `> 0`; `app_token_env == "SLACK_APP_TOKEN"`.

3. Module docstring Required env list: add `SLACK_APP_TOKEN — Socket Mode app token (local/dev only; AST-1069)`.

⚠️ **Decision — extend CONTACT_CONFIG here:** Ticket Boundaries say this child does not *own* CONTACT_CONFIG as a product surface, but ingress constants must live in config (§2.1 / no-hardcoded-sets). Only add Events/Socket Mode keys; do not change `listen_enabled`, `skills`, or bot/signing env names.

⚠️ **Decision — process-local dedupe:** Single gunicorn worker (RAILWAY_CONFIG) makes an in-process ring/set sufficient for Slack retries in this epic. Do **not** add a DB table. Document in plan Railway section that multi-worker would need shared dedupe (out of scope).

---

## Stage 2: `src/external/slack.py`

**Done when:** External module verifies signatures, extracts URL challenges, posts chat messages via Web API, and can open a Socket Mode connection for the local script — **no Contact business logic**, no logging of outcomes (caller logs).

1. Create `src/external/slack.py` with module docstring stating: Events HTTP + Web API post for production; Socket Mode helper for local/dev only; secrets from `os.environ[CONTACT_CONFIG[…]]` at **call time** (strict, no `.get`); never read secrets at import (unlike gmail — missing Slack env must not break unrelated processes).

2. Public functions:

| Function | Behavior |
|----------|----------|
| `verify_slack_signature(*, signing_secret: str, timestamp: str, body: bytes, signature: str) -> bool` | Slack v0 HMAC-SHA256 over `v0:{timestamp}:{body}`; reject if timestamp skew > 60s |
| `parse_url_verification(payload: dict) -> Optional[str]` | If `type == "url_verification"`, return `challenge` string; else `None` |
| `post_message(*, channel: str, text: str, thread_ts: Optional[str] = None) -> dict` | `require_controlled_external_io`; `POST https://slack.com/api/chat.postMessage` with `os.environ[CONTACT_CONFIG["bot_token_env"]]`; return JSON; raise on HTTP/transport failure; do not log |
| `open_socket_mode_connection(handler)` | Local/dev: use `SLACK_APP_TOKEN` + bot token to open Socket Mode websocket; invoke `handler(payload_dict)` per Events API-shaped envelope; **must not** be imported by production UI path |

3. Signature verify uses stdlib `hmac` / `hashlib`. HTTP uses existing `requests`. Socket Mode uses `websocket-client`.

4. **Callers of external:** only **core** (`contact.py`) and **scripts** (Socket Mode). UI must **not** import `src.external.slack` or reimplement HMAC/Slack HTTP.

⚠️ **Decision — no `slack_sdk` package:** Prefer `requests` + `websocket-client` + stdlib HMAC to avoid a heavy SDK. If Socket Mode handshake proves underspecified at build time, stop and comment on the parent — do not invent a second HTTP polling path.

---

## Stage 3: Contact HTTP ingress + inbound handler

**Done when:** Core owns verify/challenge + event routing; UI never touches external. `receive_slack_events_http` returns HTTP status/body for the blueprint; `handle_slack_event` accepts a verified payload, respects listen, dedupes `event_id`, accepts `app_mention` and DM `message` events; `debug=True` emits Style D found/recorded lines.

1. In `src/core/contact.py`, add **two** public functions:

```python
def receive_slack_events_http(
    raw_body: bytes,
    *,
    timestamp: str,
    signature: str,
    debug: bool = False,
) -> tuple[int, object]:
    """Verify Slack signature, answer URL challenge, or accept an event payload.

    Returns (status_code, body) where body is ``dict`` (JSON), ``bytes``, or ``str``.
    """

def handle_slack_event(payload: dict, *, debug: bool = False) -> dict:
    """Route one Slack Events API payload into Contact (listen-gated)."""
```

2. `receive_slack_events_http` behavior (literal):

   - `signing_secret = os.environ[CONTACT_CONFIG["signing_secret_env"]]` (strict; missing → raise / surface as 500 to UI).
   - Call `verify_slack_signature(...)` from `src.external.slack`; if false → return `(401, "")`.
   - `payload = json.loads(raw_body)` (invalid JSON → `(400, "")`).
   - If `challenge := parse_url_verification(payload)` → return `(200, {"challenge": challenge})`.
   - Else: schedule `handle_slack_event(payload, debug=debug)` on a **daemon thread** inside core (so ack stays fast without UI owning process logic); **immediately** return `(200, "")`.

3. `handle_slack_event` behavior (literal):

   - If not `slack_listen_enabled()`: return `{"accepted": False, "reason": "listen_off"}` (no external I/O).
   - Read `event_id` from payload; if missing, return `{"accepted": False, "reason": "missing_event_id"}`.
   - Process-local dedupe: module-level ordered set/deque capped by `CONTACT_CONFIG["event_id_dedupe_max"]`; if seen, return `{"accepted": False, "reason": "duplicate_event"}`.
   - `event = payload.get("event") or {}`; `etype = event.get("type")`.
   - Accept only if `etype` in `CONTACT_CONFIG["bot_event_types"]`.
   - For `type == "message"`: ignore `subtype` bot/message_changed/etc.; ignore messages with `bot_id`; require DM channel shape — prefer `event.get("channel_type") == "im"` when present (else channel id starting with `D` — document in code comment).
   - For `app_mention`: accept (channel @Estelle).
   - On accept: return `{"accepted": True, "event_id": …, "event_type": etype, "user": event.get("user"), "channel": event.get("channel"), "ts": event.get("ts"), "thread_ts": event.get("thread_ts"), "text": event.get("text")}`.
   - Do **not** call resolve/PROSPECT (AST-1068), do **not** load history (AST-1070), do **not** run Estelle turn (AST-1046), do **not** `post_message` in this handler (reply loop is AST-1046; post helper exists for plumbing tests/siblings).

4. When `debug=True` on either path: use `get_logger` + existing debug helpers (`debug_detail` / Style D index pattern per Code Rules §1.5.1 / AST-538) for found/recorded lines (event_id, type, accepted/reason). Truncate long `text`.

5. Socket Mode script calls `handle_slack_event` directly (already past Slack's Socket Mode envelope auth). UI calls **only** `receive_slack_events_http`.

⚠️ **Decision — core owns verify + ack scheduling:** Joan `[plan-discuss]` round=1 — `astral.layers.import-direction` forbids ui→external. HMAC/HTTP stay in external; Contact core is the only production caller. Daemon-thread ack-then-process lives in core so the blueprint stays a pass-through.

---

## Stage 4: HTTP webhook UI + server register

**Done when:** Slack can POST the Request URL; challenge returns; signed events ack with 200 within the request; UI imports **core/utils only**.

1. Create `src/ui/api/api_slack.py`:

   - Blueprint `slack_bp`, `url_prefix="/api"`.
   - `POST` route = `CONTACT_CONFIG["events_http_path"]` (i.e. `/api` + `/slack/events` → **`/api/slack/events`**).
   - **No** `@require_auth` — Slack cannot send Astral Bearer tokens; **signing secret verification is the auth** (performed in Contact core).
   - Read **raw** body: `request.get_data()` (required for HMAC).
   - Headers: `X-Slack-Request-Timestamp`, `X-Slack-Signature` only.
   - `status, body = receive_slack_events_http(raw_body, timestamp=…, signature=…, debug=ui_llm_debug())`.
   - Return Flask response: if `body` is `dict` → `jsonify(body), status`; else → `body, status` (empty string for 200 ack / 401).
   - **Forbidden:** `from src.external…`, `os.environ[CONTACT_CONFIG["signing_secret_env"]]`, or any HMAC/challenge logic in this file.

2. Register blueprint in `src/ui/server.py` next to other API blueprints.

⚠️ **Decision — open route + signature:** This matches webhook norms and Code Rules §2.9 (endpoints without `@require_auth` are open; Slack signature replaces Bearer). Do not put this route behind admin auth.

⚠️ **Decision — thin UI:** Blueprint is transport only (raw body + headers → core → status/body). Matches existing `src/ui/api/*` import graph.

---

## Stage 5: Socket Mode local script + Railway docs (in this plan)

**Done when:** Local script exists and plan documents production Request URL wiring; production code path never opens Socket Mode.

1. Add `websocket-client` to `requirements.txt`.

2. Add `scripts/slack_socket_mode_dev.py`:

   - Docstring: **local/dev only**; production must use Events Request URL.
   - Load dotenv; call `open_socket_mode_connection` / equivalent loop; for each event envelope call `handle_slack_event`.
   - Exit non-zero with clear message if `SLACK_APP_TOKEN` / bot token missing.

3. **Railway / Slack app wiring** (operator checklist — keep in this plan file under a short `### Production Request URL` subsection; no separate ops repo file):

   - Slack app → Event Subscriptions → Enable → Request URL = `https://<railway-host>/api/slack/events`
   - Subscribe bot events: `app_mention` and **`message.im`** (Slack Event Subscriptions UI name). Payload `event.type` for DMs is still **`message`** — that is what `CONTACT_CONFIG["bot_event_types"]` filters on. Do **not** put `message.im` in `bot_event_types`.
   - Environ on Railway: `SLACK_BOT_TOKEN`, `SLACK_SIGNING_SECRET` (no `SLACK_APP_TOKEN` required in production)
   - Manage Slack listen (AST-1067) must be on before Contact accepts; until then handler returns `listen_off`

### Production Request URL

| Step | Action |
|------|--------|
| 1 | Deploy Astral with `SLACK_BOT_TOKEN` + `SLACK_SIGNING_SECRET` set |
| 2 | Slack app **Event Subscriptions** Request URL → `https://<prod-host>/api/slack/events` |
| 3 | Verify URL (Slack sends `url_verification`; endpoint returns `challenge`) |
| 4 | Subscribe bot events: `app_mention` + `message.im` (subscription names); Contact filters payload types `app_mention` + `message` |
| 5 | Install app to Astral Career Match workspace; invite Estelle to channels as needed |
| 6 | Turn Manage Slack listen **on** (AST-1067) per environment |

---

## Out of scope (explicit)

- Manage Slack listen UI / per-env flip (AST-1067) — only **read** `listen_enabled`.
- `get_candidate_id_for_query` / PROSPECT create / Slack user id persist (AST-1068).
- Slack history load/cache (AST-1070).
- CONTACT_CONFIG skill runners (AST-1071).
- Estelle conversational turn + success/failure/concern envelope (AST-1046).
- Using Socket Mode as production ingress.
- Full-exchange DB transcript store.
- Frontend React pages.

---

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — new external Slack module, webhook blueprint, Contact HTTP ingress + inbound path, Socket Mode dev script, and CONTACT_CONFIG ingress keys.

**Conf:** `high` — AST-1066 left env-name contracts and listen gate; Events verify/ack/post is a well-specified Slack contract; ui→core→external layering now explicit after Joan round=1.

**Risk:** `HIGH` — a broken verify/ack can disable Estelle workspace-wide or open an unauthenticated webhook; mitigated by signature check (in core→external), listen gate, and no Bearer-open data APIs on this route.

---

## Revisions

### Revision 1 — 2026-07-30

Driven by: Joan `[plan-discuss] round=1 concern` — fix-now `astral.layers.import-direction` (Stage 4 UI called external verify/challenge + read signing secret).

Changes:

- Stage 3: add `receive_slack_events_http` on Contact core (verify, challenge, daemon-thread schedule of `handle_slack_event`); core is the sole production caller of `src.external.slack`.
- Stage 4: blueprint is transport-only (raw body + Slack headers → core → status/body); **forbids** ui→external imports and environ signing-secret reads.
- Stage 2 / Files Changed: document callers of external = core + scripts only.
- Stage 5: clarify Slack subscription name `message.im` vs payload `event.type == "message"` in `bot_event_types` (Joan discuss non-blocking).

---

## Review (build stub)

- **Publish ref:** `origin/sub/AST-1043/AST-1069-slack-events-api-webhook-ingress`
- **Tip:** `d00b8e7e` — Socket Mode script + websocket-client (stages 1–5 complete)
- **Stage commits:** `8733b3ae` (config), `0dba2471` (external), `dc83dd82` (contact), `26584cad` (api_slack), `d00b8e7e` (script/deps)

---

## Review (Radia / code-rubric.v1)

[code-rubric] revision=1  
**Rubric:** code-rubric.v1  
**Ticket:** AST-1069  
**Publish ref:** `650a0d51` on `origin/sub/AST-1043/AST-1069-slack-events-api-webhook-ingress` (docs tip follows)  
**Overall:** DISCUSS

**Diff change set:** `origin/dev...650a0d51` — layers `{core, external, utils, ui, docs, scripts}`; paths `src/external/slack.py` (A), `src/core/contact.py` (A), `src/ui/api/api_slack.py` (A), `src/ui/server.py` (M), `src/utils/config.py` (M), `scripts/slack_socket_mode_dev.py` (A), `requirements.txt` (M), plan/bible/tests; change_types `{add, modify}`. Tip carries AST-1066 scaffold ancestry (empty skills); not AST-1071.

### Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | conforms | no graded agent tasks |
| astral.agent.do-task-delegation | scoped | conforms | no do_task; CONTACT ≠ TASK_CONFIG |
| astral.agent.grade-vector-validation | scoped | conforms | no grade vectors |
| astral.batch.batch-id-first | scoped | conforms | no batch claim API |
| astral.batch.batch-id-format | scoped | conforms | no batch_id |
| astral.batch.claim-process-release | scoped | conforms | no batch processing |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | no agent_data entity refs |
| astral.config.config-source-of-truth | scoped | conforms | events path / bot_event_types / dedupe / env names in CONTACT_CONFIG |
| astral.config.pass-threshold-vs-score-floor | scoped | not-applicable | no threshold/score-floor edits |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | strict os.environ at call time in core/external; no import-time reads |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss artifacts/** / scripts/spikes/** |
| astral.debug.spikes-under-debug-dir | scoped | conforms | docs/features plans only — not spike notes |
| astral.docs.features-single-file-per-ticket | scoped | conforms | one plan file per ticket under docs/features/contact/ |
| astral.git.betty-no-src-or-features | scoped | conforms | tip merge-tests `650a0d51` tests/bible only |
| astral.git.engineer-test-tree-ban | scoped | conforms | tests/bible via Betty test/merge-tests vocabulary |
| astral.layers.core-vs-external-bright-line | scoped | conforms | HMAC/HTTP/Socket I/O only in external |
| astral.layers.import-direction | scoped | conforms | ui→core only; core→external; script exempt callers |
| astral.layers.scripts-exempt-from-layer-rules | scoped | conforms | Socket Mode local script under scripts/ |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | path/event types/listen from config via Contact |
| astral.patterns.coat-check-never-store-empty | scoped | not-applicable | no coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | scoped | not-applicable | no consult/render_verdict |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | Events route open; Slack signature auth via core |
| astral.standards.data-raises-caller-logs | scoped | conforms | external raises on post; Contact decides verify outcomes |
| astral.standards.database-header-inventory | scoped | not-applicable | no data/schema paths |
| astral.standards.debug-contract-gated | scoped | conforms | Style D on receive/handle when debug=True; quiet when False |
| astral.standards.dry-and-focused-functions | scoped | conforms | receive / verify / post / handle split |
| astral.standards.in-scope-only | scoped | conforms | no Manage Slack / resolve / skills / turn-loop |
| astral.standards.logging-via-utils | scoped | conforms | Contact get_logger Style D; external does not log outcomes |
| astral.standards.no-cross-contamination | scoped | conforms | skills stay empty; no TASK_CONFIG / sibling product |
| astral.standards.no-hardcoded-sets | scoped | conforms | event types/path/dedupe from config; skew/timeout named module constants |
| astral.standards.public-then-helpers | scoped | conforms | public ingress API present; private helpers grouped with handle path |
| astral.standards.utils-data-late-import-only | scoped | conforms | config.py has no data import |
| astral.state.core-decides-transitions | scoped | not-applicable | no state transitions |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no job state work |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no dispatch run_next |
| astral.ui.frontend-file-placement | scoped | not-applicable | no src/ui/frontend/** |
| astral.ui.naming-conventions | scoped | conforms | snake_case /api/slack/events |
| astral.ui.single-gunicorn-worker | scoped | conforms | process-local dedupe; multi-worker OOS as planned |
| orch.git.betty-merge-tests-one-sha | universal | conforms | authoritative merge-tests tip `650a0d51` (prior empty merge ignored) |
| orch.git.commit-vocabulary | universal | conforms | plan/code/test/merge-tests vocabulary on sub |
| orch.git.flow-direction-inviolable | universal | conforms | publish on origin/sub/AST-1043/AST-1069-… |
| orch.git.ftr-sub-topology | universal | conforms | matches parent Git table |
| orch.git.merge-on-checkout | universal | conforms | no illegal merge recipe |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | none in tip history |
| orch.git.no-dev-agent-branches | universal | conforms | uses sub/AST-1043/AST-1069-… |
| orch.git.one-epic-worktree-per-parent | universal | conforms | astral-AST-1043 epic worktree |
| orch.git.three-permanent-branches | universal | conforms | no new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Joan round=1 import-direction fixed; Decisions held |
| orch.pipeline.plan-is-bible | universal | conforms | stages 1–5 + Revision 1 match tip |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Contact child scope |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | no statute corpus edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty owns tests/bible |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee Hedy through Tests Passed |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | implementer Hedy remains assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | doc-only review commit paths |

### Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.external.slack-events (proposed) | conforms | verify / challenge / postMessage / Socket Mode helper |
| pattern.api.routes | conforms | thin api_slack transport-only |
| pattern.core.contact-agent (proposed) | conforms | receive_slack_events_http + handle_slack_event |
| pattern.config.config-block | conforms | CONTACT_CONFIG Events/Socket keys |

### Plan adherence

Stages 1–5 land; Revision 1 import-direction fix present (UI never imports external; signing secret read in Contact). Listen gate, signature verify, URL challenge, daemon-thread ack, process-local dedupe, Socket Mode script local-only. Self-Assessment MAJOR-CHANGE / high / HIGH matches open-webhook risk and mitigations. Sibling scopes clean (empty skills; no resolve/Manage Slack/turn-loop).

### Findings

**discuss** — C4 straggler: Joan Excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban` now in-scope on tip (docs/features + tests/bible). All three score **conforms** — no product action.

### What’s solid

ui→core→external after Joan Plan Discuss; HMAC + listen gate + empty 200 ack; config-driven path/types/dedupe; external silent on outcomes; Socket Mode confined to scripts/.

context_tokens≈58000

---

## Resolution

**2026-07-30** — Radia Overall **DISCUSS**; **no fix-now**. Discuss C4 straggler (Excluded→in-scope statutes on tip) scored conforms — no product change.

Also merged `origin/ftr/AST-1043-slack-bot-agent` (AST-1071 skills ACL on tip) into this publish ref so Events ingress + skill runners coexist: CONTACT_CONFIG keeps Events/Socket keys **and** AST-1071 `skills`; `contact.py` keeps `receive_slack_events_http` / `handle_slack_event` **and** `run_contact_skill`; both blueprints registered. Merge commit: `b62a2a8e`.
