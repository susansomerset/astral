<!-- linear-archive: AST-1070 archived 2026-08-11 -->

## Linear archive (AST-1070)

**Archived:** 2026-08-11  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1070/slack-sourced-conversation-context-load-and-cache  
**Status at archive:** Archive  
**Project:** Astral Contact  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-1043 — Slack Bot Agent  
**Blocked by / blocks / related:** parent: AST-1043

### Description

## What this implements

Load recent Slack thread/channel history for Contact turns with an optional **process-local** cache and append of new inbound/outbound messages. Conversation source of truth remains Slack (Web API); no full-exchange DB transcript table. Does not own Events ingress, resolve/PROSPECT, Manage Slack, skill runners, or Estelle turn loop.

## Acceptance criteria

- [X] Contact can load recent Slack conversation context for a turn (`load_slack_conversation_context`).
- [X] Conversation SoT stays Slack; process-local cache + append only — not a DB transcript SoT.
- [X] Inbound accepted events append into cache; `contact_post_message` posts then appends outbound.
- [X] Config drives history limit, cache capacity, and TTL (no hardcoded limits in call sites).

## Boundaries

Does not own Events verify/ack (AST-1069), Manage Slack (AST-1067), resolve/PROSPECT (AST-1068), CONTACT_CONFIG skill runners (AST-1071), Estelle turn loop (AST-1046), or a full-exchange transcript table.

## In scope

- [X] `pattern.core.contact-agent` (proposed) — `load_slack_conversation_context` / `append_slack_conversation_message` / `contact_post_message`
- [X] `pattern.external.slack-events` (proposed) — `fetch_conversation_history` on `src/external/slack.py`
- [X] `pattern.config.config-block` — CONTACT_CONFIG context_history_limit / cache max / TTL
- [X] `astral.config.config-source-of-truth` — limits/TTL in config, not literals
- [X] `astral.config.secrets-and-env-specific-from-environ` — bot token via env name at call time
- [X] `astral.layers.import-direction` — ui → core → external; UI never fetches history
- [X] `astral.layers.core-vs-external-bright-line` — Slack HTTP history I/O only in external
- [X] `astral.standards.no-hardcoded-sets` — history limit / cache caps from CONTACT_CONFIG
- [X] `astral.standards.debug-contract-gated` — Style D on load/append when `debug=True`
- [X] `astral.standards.in-scope-only` / `astral.standards.no-cross-contamination` — sibling scopes excluded
- [X] `astral.standards.public-then-helpers` / `astral.standards.dry-and-focused-functions` — load/append/fetch split
- [X] `astral.standards.logging-via-utils` — Contact logs; external does not log outcomes
- [X] `astral.ui.single-gunicorn-worker` — process-local cache assumes single worker

## Considered but excluded

- [X] `pattern.ui.admin-endpoint` / `astral.patterns.require-auth-on-protected-endpoints` — no new UI routes
- [X] `pattern.state.entity-state-transitions` / PROSPECT — AST-1068
- [X] `astral.standards.database-header-inventory` — no schema/table; process-local cache only
- [X] `astral.patterns.coat-check-never-store-empty` — no coat-check conversation store
- [X] Full-exchange DB transcript SoT — parent forbids
- [X] Estelle turn loop / CHAT envelope — AST-1046

## Notes for planning

After AST-1069. Slack SoT via `conversations.history` / `conversations.replies`; cache is process-local with TTL + `refresh=`.

## Git branch (authoritative)

Parent `ftr/AST-1043-slack-bot-agent`; child `sub/AST-1043/AST-1070-slack-sourced-conversation-context`. Created at dispatch-parent.

## Plan

`docs/features/contact/ast-1070-slack-sourced-conversation-context.md` @ `origin/sub/AST-1043/AST-1070-slack-sourced-conversation-context` tip `6244ecc3`.

### Comments

#### betty — 2026-07-30T16:30:43.961Z
merge-tests hygiene: collapsed duplicate `merge-tests(AST-1070)` (was 5ce882c8 + 0fec6e28) to exactly one — tip `e007142d` / `76ac99fd` → `origin/tests` `2558d0e9` (Stage 3 envelope). Tip tree unchanged. Stay User Testing; assignee Hedy for merge-child.

#### chuckles — 2026-07-30T16:28:39.523Z
[merge-child] blocked: duplicate merge-tests(AST-1070) on sub — count=2 (amend on tests, one merge-tests only)

@Betty White — publish-ref `origin/sub/AST-1043/AST-1070-slack-sourced-conversation-context` has two `merge-tests(AST-1070)` commits:
- `5ce882c8` — origin/tests `79d130b1`
- `0fec6e28` — origin/tests `b29932eb`

Please leave a single `merge-tests(AST-1070)` on the tip (amend/squash hygiene on tests lineage), then Chuckles will re-run merge-child.

— Chuckles

#### betty — 2026-07-30T16:22:54.887Z
[check-linear]

Revised `TestAst1070ContactConversationContext` + bible for Stage 3 dict envelope (`channel` / `thread_ts` / `messages` / `source`), channel strip, empty-channel `ValueError`. Republished `merge-tests(AST-1070): origin/tests b29932eb` → tip `0fec6e28`. Assignee → Hedy (Review Posted) for resolve resume.

**Manifest (updated)**
1. `TestAst1070ContactContextConfig`
2. `TestAst1070FetchConversationHistory`
3. `TestAst1070ContactConversationContext` — envelope hit/miss/TTL/refresh; empty channel; strip; append; DM key; post append

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1070ContactContextConfig \
  tests/component/external/test_slack.py::TestAst1070FetchConversationHistory \
  tests/component/core/test_contact.py::TestAst1070ContactConversationContext \
  -q
```

**Bible sha256**
- `docs/test-bible/core/contact.md` `0a854cfc70911febe86cde603922d6a03ff336ebc69ce6e636a22a0531438c7b`
- `docs/test-bible/utils/config.md` `f8ffaef59e2d134f1a7001ac721dd9e6c0451be946395e1d8e1a79987c1fccbc`
- `docs/test-bible/external/slack.md` `f530c2f0f0ad34b13f5493639e56bf494853d8cbe1da7179065278de78d40e2a`

— Betty

#### hedy — 2026-07-30T16:18:49.241Z
[qa-handoff]

@Betty White — Radia FIX-NOW restored Stage 3 `load_slack_conversation_context` contract on product tip.

**Product tip:** `origin/sub/AST-1043/AST-1070-slack-sourced-conversation-context` @ `3c3501a9` (`resolve(AST-1070): — findings addressed`; envelope landed in parent `ed66d7cc`).

**Why tests/manifest:** Betty’s `TestAst1070ContactConversationContext` asserts `load_slack_conversation_context` returns a bare `list[dict]` (and her Tests Ready note already flagged list vs plan dict). Tip now returns Stage 3 envelope:
`{"channel", "thread_ts", "messages", "source": "cache"|"slack"}`
plus strip channel + `ValueError` on empty; Style D uses `source=`.

**Please revise:** bible `docs/test-bible/core/contact.md` + `tests/component/core/test_contact.py::TestAst1070ContactConversationContext` for dict envelope / `source` / empty-channel raise; republish `merge-tests` + reassign Hedy with updated manifest.

Staying **Review Posted**.

#### radia — 2026-07-30T16:15:04.486Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1070
**Publish ref:** `d8f607ea` on `origin/sub/AST-1043/AST-1070-slack-sourced-conversation-context`
**Overall:** FIX-NOW

**Diff change set:** `origin/dev...d8f607ea` — layers `{core, external, utils, ui, docs, scripts}`; tip carries AST-1066/1069/1071 ancestry plus AST-1070 context load/cache; change_types `{add, modify}`.

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
| astral.config.config-source-of-truth | scoped | conforms | history limit / cache max / TTL in CONTACT_CONFIG |
| astral.config.pass-threshold-vs-score-floor | scoped | not-applicable | no threshold/score-floor edits |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | bot token via env name at call time in external |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss artifacts/** / scripts/spikes/** |
| astral.debug.spikes-under-debug-dir | scoped | conforms | docs/features plans only — not spike notes |
| astral.docs.features-single-file-per-ticket | scoped | conforms | one plan file per ticket under docs/features/contact/ |
| astral.git.betty-no-src-or-features | scoped | conforms | merge-tests `5ce882c8` tests/bible only |
| astral.git.engineer-test-tree-ban | scoped | conforms | tests/bible via Betty vocabulary |
| astral.layers.core-vs-external-bright-line | scoped | conforms | history HTTP only in external fetch_conversation_history |
| astral.layers.import-direction | scoped | conforms | core→external; no UI history fetch |
| astral.layers.scripts-exempt-from-layer-rules | scoped | conforms | Socket Mode script under scripts/ (ancestry) |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | limits from config; thin API ancestry only |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | process-local cache only — no coat-check transcript |
| astral.patterns.render-verdict-orchestrates-consult | scoped | not-applicable | no consult |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | no new unprotected data routes this ticket |
| astral.standards.data-raises-caller-logs | scoped | conforms | external raises; Contact decides |
| astral.standards.database-header-inventory | scoped | not-applicable | no data/schema paths |
| astral.standards.debug-contract-gated | scoped | needs-discussion | Style D present; detail omits plan `source=` field (tied to return-shape drift) |
| astral.standards.dry-and-focused-functions | scoped | conforms | load/append/fetch/post split |
| astral.standards.in-scope-only | scoped | conforms | no Manage Slack / resolve / turn-loop product |
| astral.standards.logging-via-utils | scoped | conforms | Contact get_logger; external silent on outcomes |
| astral.standards.no-cross-contamination | scoped | conforms | context keys only; skills/Events/ACL boundaries held |
| astral.standards.no-hardcoded-sets | scoped | conforms | limit/max/TTL from CONTACT_CONFIG |
| astral.standards.public-then-helpers | scoped | needs-discussion | `_context_cache_*` helpers sit above public load/append API |
| astral.standards.utils-data-late-import-only | scoped | conforms | config.py has no data import |
| astral.state.core-decides-transitions | scoped | not-applicable | no state transitions |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no job state |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no dispatch chain |
| astral.ui.frontend-file-placement | scoped | not-applicable | no frontend paths |
| astral.ui.naming-conventions | scoped | conforms | existing snake_case admin/events routes (ancestry) |
| astral.ui.single-gunicorn-worker | scoped | conforms | process-local cache; multi-worker OOS |
| orch.git.betty-merge-tests-one-sha | universal | conforms | merge-tests `5ce882c8` then publish-ref merge |
| orch.git.commit-vocabulary | universal | conforms | plan/code/test/merge-tests/merge vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | publish on origin/sub/AST-1043/AST-1070-… |
| orch.git.ftr-sub-topology | universal | conforms | matches parent Git table |
| orch.git.merge-on-checkout | universal | conforms | merge origin/dev + publish-ref present |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | none observed |
| orch.git.no-dev-agent-branches | universal | conforms | uses sub/AST-1043/AST-1070-… |
| orch.git.one-epic-worktree-per-parent | universal | conforms | astral-AST-1043 |
| orch.git.three-permanent-branches | universal | conforms | no new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Joan r1 DM-key Decision held in code |
| orch.pipeline.plan-is-bible | universal | violates | load return type/shape + missing channel empty raise vs Stage 3 |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Contact child |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | no statute edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty owns tests/bible |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee Hedy through Tests Passed |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | implementer Hedy remains assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | doc-only review commit paths |

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.core.contact-agent (proposed) | needs-discussion | load/append/post present; load return shape ≠ plan Stage 3 dict |
| pattern.external.slack-events (proposed) | conforms | fetch_conversation_history on external slack |
| pattern.config.config-block | conforms | context_history_limit / cache max / TTL |

## Plan adherence

Stages 1–2 and most of Stage 3 land (config keys, external fetch, process-local cache, DM key = `thread_ts` only, inbound append on accept, `contact_post_message`). **Breaks Stage 3 binding return contract** and channel normalize/raise. Betty already noted list return vs plan dict envelope. Self-Assessment MAJOR-CHANGE / high / MEDIUM still honest for the intended design.

## Findings

**fix-now** — `orch.pipeline.plan-is-bible` / Stage 3 `load_slack_conversation_context`  
**Location:** `src/core/contact.py` `load_slack_conversation_context`  
**Issue:** Plan requires `-> dict` returning `{"channel", "thread_ts", "messages", "source": "cache"|"slack"}`. Tip returns `list[dict]` (messages only). Also plan requires strip channel + `ValueError` on empty — not implemented.  
**Action:** Restore Stage 3 envelope (and channel validate); Betty will need bible/test revision for the dict shape (or engineer `[qa-handoff]` if tests were written to the list drift).

**discuss** — C4 straggler: Joan Excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, `astral.layers.scripts-exempt-from-layer-rules`, `astral.patterns.require-auth-on-protected-endpoints`, `astral.ui.naming-conventions` now in-scope via tip ancestry (docs/tests/scripts/ui). All score **conforms** / expected — no product action.

**discuss** — `astral.standards.public-then-helpers`: `_context_cache_key` / `_context_cache_put` appear before public load/append (prefer public-first section then helpers).

**discuss** — `astral.standards.debug-contract-gated`: Style D fires, but detail uses `count=` / outcomes `cache_hit`|`fetched` rather than plan’s `source=` field (same envelope drift).

## What’s solid

DM cache key uses Slack `thread_ts` only (Joan Revision 1); history I/O stays in external; TTL + `refresh=` + config caps; inbound append on accept; no DB transcript SoT.

Plan append: `docs/features/contact/ast-1070-slack-sourced-conversation-context.md` @ `d8f607ea`.

context_tokens≈56000

— Radia

#### betty — 2026-07-30T16:11:17.440Z
Tests Ready — run on `origin/sub/AST-1043/AST-1070-slack-sourced-conversation-context` @ `5ce882c8` (`merge-tests(AST-1070): origin/tests 79d130b1`).

**Manifest**
1. `tests/component/utils/test_config.py::TestAst1070ContactContextConfig` — `context_history_limit` / `context_cache_max_conversations` / `context_cache_ttl_seconds`
2. `tests/component/external/test_slack.py::TestAst1070FetchConversationHistory` — history vs replies; gate; `ok:false`
3. `tests/component/core/test_contact.py::TestAst1070ContactConversationContext` — load hit/miss/TTL/`refresh`; append warm+trim; DM cache key `(channel,"")` never message `ts`; `contact_post_message` appends outbound

Keep green (tip already carries): `TestAst1066ContactScaffold`, `TestAst1069ContactSlackIngress` / `TestAst1069ExternalSlack`, `TestAst1071ContactSkillRunners` / `TestAst1071ContactSkillsConfig`.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1070ContactContextConfig \
  tests/component/external/test_slack.py::TestAst1070FetchConversationHistory \
  tests/component/core/test_contact.py::TestAst1070ContactConversationContext \
  -q
```

**Bible sha256** (`git show origin/sub/AST-1043/AST-1070-slack-sourced-conversation-context:<path> | sha256sum`)
- `docs/test-bible/core/contact.md` `ff500712a62543c2f4b7e1d4f144c88d04a6880f284b1c52a82254c2219eab17`
- `docs/test-bible/external/slack.md` `f530c2f0f0ad34b13f5493639e56bf494853d8cbe1da7179065278de78d40e2a`
- `docs/test-bible/utils/config.md` `4d807611bd4a5a866c394ff9735dcff7c7464d7edd69fba8eeaa4af214876f3b`

Note: shipped `load_slack_conversation_context` returns `list[dict]` (not plan Stage-3 dict envelope) — tests assert list + cache behavior.

— Betty

#### joan — 2026-07-30T03:45:42.495Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1070
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 Estelle DM/@ ingress | N/A — boundary (AST-1069) |
| AC2 Events verify/ack | N/A — boundary (AST-1069) |
| AC3 Manage Slack listen | N/A — boundary (AST-1067) |
| AC4 resolve + PROSPECT | N/A — boundary (AST-1068) |
| AC5 routing / state | N/A — boundary (AST-1068) |
| AC6 Slack history load + optional cache; no transcript table | Stages 1–3 (primary) |
| AC7 CONTACT_CONFIG skills/ACL | N/A — extends context limit/TTL keys only |
| AC8 debug=True found/recorded | Stage 3 Style D on load/append |

### Child AC → plan stages

| Child AC | Plan coverage |
|----------|---------------|
| `load_slack_conversation_context` | Stage 3 |
| Slack SoT; process-local cache only | Stages 1–3; Decision no DB table |
| Inbound append + `contact_post_message` | Stage 3 §§5–6 |
| Config drives limit/capacity/TTL | Stage 1 |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 CONTACT_CONFIG context keys | config-source-of-truth; no-hardcoded-sets; parent AC6 |
| Stage 2 `fetch_conversation_history` | external Slack SoT; core-vs-external |
| Stage 3 load/cache/append + inbound hook | pattern.core.contact-agent; parent AC6 |
| Stage 4 self-check no UI | import-direction; in-scope-only |

**Notes:** Prior Plan Discuss round=1 (concern+reply) completed; re-validate from Plan Ready on tip `ebf1dbb1`.

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests |
| orch.git.commit-vocabulary | conforms | Sub publish vocabulary |
| orch.git.flow-direction-inviolable | conforms | origin/sub only |
| orch.git.ftr-sub-topology | conforms | Parent Git table match |
| orch.git.merge-on-checkout | conforms | No illegal merge |
| orch.git.no-cherry-pick-rebase-force | conforms | None |
| orch.git.no-dev-agent-branches | conforms | sub/AST-1043/AST-1070-… |
| orch.git.one-epic-worktree-per-parent | conforms | astral-AST-1043 |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Decisions documented |
| orch.pipeline.plan-is-bible | conforms | Revision 1 aligned Decision + step 6; prior contradict fixed |
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
| astral.config.config-source-of-truth | conforms | History limit/cache/TTL in CONTACT_CONFIG |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | Bot token via env name at call time |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src |
| astral.layers.core-vs-external-bright-line | conforms | History HTTP only in external |
| astral.layers.import-direction | conforms | core→external; no UI history fetch |
| astral.layers.ui-config-driven-business-logic | conforms | No React rules; utils config only |
| astral.patterns.coat-check-never-store-empty | conforms | Explicitly no coat-check transcript store |
| astral.patterns.render-verdict-orchestrates-consult | conforms | No consult |
| astral.standards.data-raises-caller-logs | conforms | External raises; Contact decides |
| astral.standards.debug-contract-gated | conforms | Style D on load/append when debug=True |
| astral.standards.dry-and-focused-functions | conforms | load/append/fetch split |
| astral.standards.in-scope-only | conforms | Sibling Out of scope list |
| astral.standards.logging-via-utils | conforms | Contact logs; external does not |
| astral.standards.no-cross-contamination | conforms | No Events/Manage Slack/resolve/skills/turn |
| astral.standards.no-hardcoded-sets | conforms | Limits from CONTACT_CONFIG only |
| astral.standards.public-then-helpers | conforms | Public load/append/fetch/post surface |
| astral.standards.utils-data-late-import-only | conforms | No utils→data |
| astral.state.core-decides-transitions | conforms | No state transitions |
| astral.state.job-prior-states-enforced | conforms | No jobs |
| astral.state.no-daisy-chain-in-run | conforms | No dispatch chain |
| astral.ui.single-gunicorn-worker | conforms | Process-local cache; multi-worker OOS |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths match none of plan paths
- astral.debug.spikes-under-debug-dir — paths match none of plan paths
- astral.docs.features-single-file-per-ticket — layers {docs} ∩ plan empty
- astral.git.engineer-test-tree-ban — paths match none of plan paths
- astral.layers.scripts-exempt-from-layer-rules — layers {scripts} ∩ plan empty
- astral.patterns.require-auth-on-protected-endpoints — layers {ui} ∩ plan empty
- astral.standards.database-header-inventory — layers {data} ∩ plan empty
- astral.ui.frontend-file-placement — layers {ui} ∩ plan empty
- astral.ui.naming-conventions — layers {ui} ∩ plan empty

## Findings

None fix-now.

**Round 1 disposition:** DM cache-key contradict resolved — inbound append uses `event.get("thread_ts")` only; message `ts` stays in the message dict; Decision aligned.

**acceptable:** Self-assessment MAJOR-CHANGE / Conf high / Risk MEDIUM with TTL+`refresh=True`+Slack SoT is honest. Outbound cache-local bot placeholders clarified in Revision 1.

**R6 checklist:** Definition fidelity pass (parent AC6). Layer/import pass. Config limits pass. No DB transcript. No sibling creep.

context_tokens≈54000

— Joan

#### hedy — 2026-07-30T03:43:19.454Z
[plan-discuss] round=1 reply

**Delta:** Fixed Joan fix-now on DM cache key contradiction (`orch.pipeline.plan-is-bible`).

- Stage 3 step 6: inbound append uses `thread_ts=event.get("thread_ts")` only; missing → `""` for the key. Message `ts` stays inside the appended message dict — never the cache-key thread component.
- Decision aligned: key is `(channel, thread_ts or "")` only.
- Step 5: outbound append prefers Slack response fields; bot placeholder is cache-local only (discuss non-blocking).

**Plan tip:** `ebf1dbb1` — https://github.com/susansomerset/astral/blob/sub/AST-1043/AST-1070-slack-sourced-conversation-context/docs/features/contact/ast-1070-slack-sourced-conversation-context.md

Returning to **Plan Ready**.

#### joan — 2026-07-30T03:41:34.593Z
[plan-discuss] round=1 concern
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1070
**Overall:** REVISE

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 Estelle DM/@ ingress | N/A — boundary (AST-1069) |
| AC2 Events verify/ack | N/A — boundary (AST-1069) |
| AC3 Manage Slack listen | N/A — boundary (AST-1067) |
| AC4 resolve + PROSPECT | N/A — boundary (AST-1068) |
| AC5 routing / state | N/A — boundary (AST-1068) |
| AC6 Slack history load + optional cache; no transcript table | Stages 1–3 (primary) |
| AC7 CONTACT_CONFIG skills/ACL | N/A — extends context limit/TTL keys only (AST-1066/1071) |
| AC8 debug=True found/recorded | Stage 3 Style D on load/append |

### Child AC → plan stages

| Child AC | Plan coverage |
|----------|---------------|
| `load_slack_conversation_context` | Stage 3 |
| Slack SoT; process-local cache only | Stages 1–3; Decision no DB table |
| Inbound append + `contact_post_message` | Stage 3 §§5–6 |
| Config drives limit/capacity/TTL | Stage 1 |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 CONTACT_CONFIG context keys | config-source-of-truth; no-hardcoded-sets; parent AC6 |
| Stage 2 `fetch_conversation_history` | external Slack SoT; core-vs-external |
| Stage 3 load/cache/append + inbound hook | pattern.core.contact-agent; parent AC6 |
| Stage 4 self-check no UI | import-direction; in-scope-only |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests |
| orch.git.commit-vocabulary | conforms | Sub publish vocabulary |
| orch.git.flow-direction-inviolable | conforms | origin/sub only |
| orch.git.ftr-sub-topology | conforms | Parent Git table match |
| orch.git.merge-on-checkout | conforms | No illegal merge |
| orch.git.no-cherry-pick-rebase-force | conforms | None |
| orch.git.no-dev-agent-branches | conforms | sub/AST-1043/AST-1070-… |
| orch.git.one-epic-worktree-per-parent | conforms | astral-AST-1043 |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Decisions documented |
| orch.pipeline.plan-is-bible | **violates** | Stage 3.6 vs Decision contradict on DM cache key (`ts` vs `""`) |
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
| astral.config.config-source-of-truth | conforms | History limit/cache/TTL in CONTACT_CONFIG |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | Bot token via env name at call time |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src |
| astral.layers.core-vs-external-bright-line | conforms | History HTTP only in external |
| astral.layers.import-direction | conforms | core→external; no UI history fetch |
| astral.layers.ui-config-driven-business-logic | conforms | No React rules; utils config only |
| astral.patterns.coat-check-never-store-empty | conforms | Explicitly no coat-check transcript store |
| astral.patterns.render-verdict-orchestrates-consult | conforms | No consult |
| astral.standards.data-raises-caller-logs | conforms | External raises; Contact decides |
| astral.standards.debug-contract-gated | conforms | Style D on load/append when debug=True |
| astral.standards.dry-and-focused-functions | conforms | load/append/fetch split |
| astral.standards.in-scope-only | conforms | Sibling Out of scope list |
| astral.standards.logging-via-utils | conforms | Contact logs; external does not |
| astral.standards.no-cross-contamination | conforms | No Events/Manage Slack/resolve/skills/turn |
| astral.standards.no-hardcoded-sets | conforms | Limits from CONTACT_CONFIG only |
| astral.standards.public-then-helpers | conforms | Public load/append/fetch/post surface |
| astral.standards.utils-data-late-import-only | conforms | No utils→data |
| astral.state.core-decides-transitions | conforms | No state transitions |
| astral.state.job-prior-states-enforced | conforms | No jobs |
| astral.state.no-daisy-chain-in-run | conforms | No dispatch chain |
| astral.ui.single-gunicorn-worker | conforms | Process-local cache; multi-worker OOS |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths match none of plan paths
- astral.debug.spikes-under-debug-dir — paths match none of plan paths
- astral.docs.features-single-file-per-ticket — layers {docs} ∩ plan empty
- astral.git.engineer-test-tree-ban — paths match none of plan paths
- astral.layers.scripts-exempt-from-layer-rules — layers {scripts} ∩ plan empty
- astral.patterns.require-auth-on-protected-endpoints — layers {ui} ∩ plan empty
- astral.standards.database-header-inventory — layers {data} ∩ plan empty
- astral.ui.frontend-file-placement — layers {ui} ∩ plan empty
- astral.ui.naming-conventions — layers {ui} ∩ plan empty

## Findings

### fix-now — DM cache key: Stage 3.6 vs Decision contradict

**Location:** Stage 3 Decision (“DMs without threads use channel-only key (`thread_ts=""`)”) vs Stage 3 step 6 (“prefer `thread_ts` or `ts` for DM root”).

**Finding:** Binding plan text conflicts. Using message `ts` as the cache key’s thread component would create a new key per DM message and break conversation continuity for `load_slack_conversation_context`. Parent AC6 / child AC need a single coherent keying rule.

**Recommendation:** Rewrite step 6 literally: pass `thread_ts=event.get("thread_ts")` only (may be `None`/absent → normalize to `""` for the key). Put message `ts` **inside** the appended message dict, never as the cache-key thread component. Align the Decision and step 6 wording.

### discuss (non-blocking)

- Outbound append shape `{user: "bot", bot_id: "self"}` is a small invented cache envelope vs “Slack API shapes pass-through” on load — acceptable for process-local cache if documented; prefer Slack response fields when present (already stated).

**acceptable:** Scope MAJOR-CHANGE / Conf high / Risk MEDIUM with TTL+refresh mitigation is honest. Layering, no DB transcript, config limits look sound once keying is fixed.

context_tokens≈52000

— Joan

#### hedy — 2026-07-30T03:38:01.131Z
Plan published on `origin/sub/AST-1043/AST-1070-slack-sourced-conversation-context`.

**Plan:** https://github.com/susansomerset/astral/blob/sub/AST-1043/AST-1070-slack-sourced-conversation-context/docs/features/contact/ast-1070-slack-sourced-conversation-context.md (`d70630a5`)

**Scope:** `MAJOR-CHANGE` — Slack history fetch in external, Contact load/cache/append + inbound append on accept, CONTACT_CONFIG context limits/TTL.

**Conf:** `high` — `conversations.history` / `replies` are fixed; AST-1069 left slack + Contact; parent forbids transcript SoT so process-local cache matches.

**Risk:** `MEDIUM` — stale cache could mislead later Estelle turns; mitigated by TTL + `refresh=True` + Slack refetch as SoT. No new open HTTP surface.

---

# AST-1070 — Slack-sourced conversation context load and cache

**Linear:** [AST-1070](https://linear.app/astralcareermatch/issue/AST-1070/slack-sourced-conversation-context-load-and-cache)  
**Parent:** [AST-1043](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent) — Slack Bot Agent  
**Publish ref:** `origin/sub/AST-1043/AST-1070-slack-sourced-conversation-context`

Give Contact a way to **load recent Slack thread/channel history** for Estelle turns, with an **optional process-local cache** and **append** of new inbound/outbound messages. **Source of truth remains Slack** (Web API history/replies). Does **not** add a full-exchange DB transcript table. Does **not** own Events verify/ack (AST-1069), Manage Slack (AST-1067), resolve/PROSPECT (AST-1068), skill runners (AST-1071), or the Estelle turn loop (AST-1046).

Depends on **AST-1069** (`src/external/slack.py` + Contact ingress already on `ftr`).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Extend `CONTACT_CONFIG` with history limit, cache capacity, cache TTL | utils |
| `src/external/slack.py` | Add `fetch_conversation_history` (`conversations.history` / `conversations.replies`) | external |
| `src/core/contact.py` | `load_slack_conversation_context`, `append_slack_conversation_message`; append on accepted inbound; optional `contact_post_message` (post + append) | core |

No UI blueprint. No `database.py` schema / transcript table. No Manage Slack / resolve / skills / turn-loop changes beyond inbound append hook on existing `handle_slack_event` accept path.

---

## Stage 1: Config — context load / cache contracts

**Done when:** `CONTACT_CONFIG` exposes history page size, cache conversation capacity, and cache TTL; asserts pass; no secret values in config.

1. Extend `CONTACT_CONFIG` (keep existing listen / skills / Events / Socket keys) with:

```python
    # AST-1070: Slack history page size for context loads (Web API limit param).
    "context_history_limit": 50,
    # Process-local cache: max distinct (channel, thread) keys retained.
    "context_cache_max_conversations": 256,
    # Seconds before a cached conversation is considered stale (force Slack refetch).
    "context_cache_ttl_seconds": 300,
```

2. Asserts: all three are `int` and `> 0`; `context_history_limit` is the Slack `limit` passed to external (no hardcoded limit in core/external call sites).

⚠️ **Decision — process-local cache, not a DB transcript table:** Parent AC6 and Boundaries forbid a separate full-exchange transcript SoT in DB. Single gunicorn worker (RAILWAY_CONFIG) makes an in-process cache sufficient for this epic. Document that multi-worker would need shared cache (out of scope). Do **not** add `CREATE TABLE` / coat-check transcript storage.

---

## Stage 2: External — `fetch_conversation_history`

**Done when:** External can pull recent messages from a channel or thread via Slack Web API; no Contact/cache logic; no outcome logging.

1. In `src/external/slack.py`, add:

```python
def fetch_conversation_history(
    *,
    channel: str,
    thread_ts: Optional[str] = None,
    limit: int,
) -> list[dict]:
    """Fetch recent messages from Slack (SoT). Raise on HTTP/transport / ok:false."""
```

2. Behavior (literal):

   - `require_controlled_external_io("slack.fetch_conversation_history")`.
   - Token: `os.environ[CONTACT_CONFIG["bot_token_env"]]` (strict).
   - If `thread_ts` is set → `POST`/`GET` **`conversations.replies`** with `channel`, `ts=thread_ts`, `limit`.
   - Else → **`conversations.history`** with `channel`, `limit`.
   - Return the `messages` list from the JSON response (each item a Slack message dict). Raise on non-2xx or `ok is not True` (include Slack `error` in exception message; do not log).
   - Do **not** filter bot/subtype here — Contact decides what to keep for context.

3. Keep existing verify / challenge / `post_message` / Socket Mode helpers unchanged.

---

## Stage 3: Contact — load, cache, append

**Done when:** Core loads context (Slack SoT + process-local cache), can append messages, Style D when `debug=True`; UI never imports external.

1. Module-level process-local cache (same spirit as `event_id` dedupe):

   - Key: `(channel, thread_ts or "")`.
   - Value: `{ "messages": list[dict], "fetched_at": float }` (monotonic or `time.time()`).
   - Cap keys by `CONTACT_CONFIG["context_cache_max_conversations"]` (OrderedDict LRU).
   - Thread-safe with a lock.

2. Public functions (names exact):

```python
def load_slack_conversation_context(
    *,
    channel: str,
    thread_ts: Optional[str] = None,
    refresh: bool = False,
    debug: bool = False,
) -> dict:
    """Return recent conversation messages for a channel or thread.

    SoT is Slack. Cache is process-local only — never a DB transcript store.
    """

def append_slack_conversation_message(
    *,
    channel: str,
    thread_ts: Optional[str] = None,
    message: dict,
    debug: bool = False,
) -> None:
    """Append one message into the process-local cache for that conversation key."""

def contact_post_message(
    *,
    channel: str,
    text: str,
    thread_ts: Optional[str] = None,
    debug: bool = False,
) -> dict:
    """Post via external slack.post_message, then append outbound text into cache."""
```

3. `load_slack_conversation_context` behavior:

   - Normalize `channel` (strip); empty → raise `ValueError`.
   - If cache hit and not `refresh` and age `< context_cache_ttl_seconds`: return  
     `{"channel", "thread_ts", "messages", "source": "cache"}`.
   - Else: `messages = fetch_conversation_history(channel=…, thread_ts=…, limit=CONTACT_CONFIG["context_history_limit"])`; store in cache; return  
     `{"channel", "thread_ts", "messages", "source": "slack"}`.
   - Message dicts returned are the Slack API shapes (pass-through); do not invent a parallel transcript schema.
   - `debug=True`: Style D index + detail (`source`, channel, thread_ts, `len(messages)`); truncate long text previews.

4. `append_slack_conversation_message` behavior:

   - If no cache entry for the key yet, create one with `messages=[message]` and `fetched_at=now` (warm without Slack round-trip).
   - Else append `message` and trim to `context_history_limit` (keep newest).
   - `message` must be a `dict` with at least `text` and `ts` (string); raise `ValueError` otherwise.

5. `contact_post_message`: call `post_message`; on success append an outbound message dict using Slack response fields when present (`ts` from the API response; `text` as posted). Placeholder `user`/`bot_id` only for cache-local identity of Estelle’s own outbound — document that load still returns Slack API shapes from history fetches. Return the Web API JSON. AST-1046 should prefer this helper for outbound so cache stays warm.

6. Wire **inbound append** into existing `handle_slack_event`: when result `accepted` is True, call `append_slack_conversation_message` with:
   - `channel=event["channel"]`
   - `thread_ts=event.get("thread_ts")` only — if missing/`None`, normalize to `""` for the cache key (channel-only DM / channel root). **Never** pass message `ts` as the cache-key thread component.
   - `message={"user", "text", "ts"}` from the event (`ts` lives **inside** the message dict only).
   Do **not** fetch history inside `handle_slack_event` (ack path stays light).

⚠️ **Decision — cache key uses Slack thread_ts only:** Key is `(channel, thread_ts or "")`. Channel @-mention threads pass Slack’s `thread_ts`. DMs / channel roots without a thread use `""`. Message `ts` is never the key’s thread component (that would shard one DM into one key per message). Document in code comment.

⚠️ **Decision — no DB table:** Explicit parent boundary. Refresh always available via `refresh=True` / TTL expiry → Slack SoT.

---

## Stage 4: Self-check / no UI

**Done when:** No new blueprint; `api_slack` / `api_contact` unchanged except transitive core behavior; import direction holds (core→external only).

1. Confirm `src/ui/api/*` does not call `fetch_conversation_history`.
2. No frontend. No Manage Slack. No PROSPECT. No Estelle turn.

---

## Out of scope (explicit)

- Events signature verify / URL challenge / daemon ack (AST-1069 — already shipped).
- Manage Slack listen UI / env prefix (AST-1067).
- `get_candidate_id_for_query` / PROSPECT create (AST-1068).
- CONTACT_CONFIG skill runner bodies (AST-1071 — already on ftr).
- Estelle conversational turn + CHAT envelope (AST-1046).
- Full-exchange DB transcript table / coat-check conversation store.
- Multi-worker shared cache.
- Changing Socket Mode script beyond what Contact append provides for free.

---

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — new Slack history external I/O, Contact load/cache/append surface, config contracts, and inbound append hook on accept.

**Conf:** `high` — Slack `conversations.history` / `replies` are fixed APIs; AST-1069 left `post_message` + Contact module; parent forbids transcript SoT so process-local cache is the matching design.

**Risk:** `MEDIUM` — stale/wrong context could mislead Estelle turns (AST-1046); mitigated by TTL + `refresh=True` + Slack as SoT on miss/expiry. No open unauthenticated surface added.

---

## Revisions

### Revision 1 — 2026-07-30

Driven by: Joan `[plan-discuss] round=1 concern` — fix-now Stage 3.6 vs Decision contradict on DM cache key (`ts` vs `""`).

Changes:

- Stage 3 step 6: inbound append passes `thread_ts=event.get("thread_ts")` only; message `ts` stays inside the message dict, never as the cache-key thread component.
- Decision wording aligned: key is `(channel, thread_ts or "")` only.
- Step 5: clarify outbound append prefers Slack response fields; placeholder bot identity is cache-local only (Joan discuss non-blocking).

## Review (build stub)

- **Publish ref:** `origin/sub/AST-1043/AST-1070-slack-sourced-conversation-context`
- **Tip:** `c34507c9` — Contact load/cache/append + inbound warm (stages 1–3)
- **Stage commits:** `392d01f5` (config), `45ce50a0` (external), `c34507c9` (contact)

---

## Review (Radia / code-rubric.v1)

[code-rubric] revision=1  
**Rubric:** code-rubric.v1  
**Ticket:** AST-1070  
**Publish ref:** `8f936a1b` on `origin/sub/AST-1043/AST-1070-slack-sourced-conversation-context` (docs tip follows)  
**Overall:** FIX-NOW

**Diff change set:** `origin/dev...8f936a1b` — layers `{core, external, utils, ui, docs, scripts}`; tip carries AST-1066/1069/1071 ancestry plus AST-1070 context load/cache; change_types `{add, modify}`.

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
| astral.config.config-source-of-truth | scoped | conforms | history limit / cache max / TTL in CONTACT_CONFIG |
| astral.config.pass-threshold-vs-score-floor | scoped | not-applicable | no threshold/score-floor edits |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | bot token via env name at call time in external |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss artifacts/** / scripts/spikes/** |
| astral.debug.spikes-under-debug-dir | scoped | conforms | docs/features plans only — not spike notes |
| astral.docs.features-single-file-per-ticket | scoped | conforms | one plan file per ticket under docs/features/contact/ |
| astral.git.betty-no-src-or-features | scoped | conforms | merge-tests `5ce882c8` tests/bible only |
| astral.git.engineer-test-tree-ban | scoped | conforms | tests/bible via Betty vocabulary |
| astral.layers.core-vs-external-bright-line | scoped | conforms | history HTTP only in external fetch_conversation_history |
| astral.layers.import-direction | scoped | conforms | core→external; no UI history fetch |
| astral.layers.scripts-exempt-from-layer-rules | scoped | conforms | Socket Mode script under scripts/ (ancestry) |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | limits from config; thin API ancestry only |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | process-local cache only — no coat-check transcript |
| astral.patterns.render-verdict-orchestrates-consult | scoped | not-applicable | no consult |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | no new unprotected data routes this ticket |
| astral.standards.data-raises-caller-logs | scoped | conforms | external raises; Contact decides |
| astral.standards.database-header-inventory | scoped | not-applicable | no data/schema paths |
| astral.standards.debug-contract-gated | scoped | needs-discussion | Style D present; detail omits plan `source=` field (tied to return-shape drift) |
| astral.standards.dry-and-focused-functions | scoped | conforms | load/append/fetch/post split |
| astral.standards.in-scope-only | scoped | conforms | no Manage Slack / resolve / turn-loop product |
| astral.standards.logging-via-utils | scoped | conforms | Contact get_logger; external silent on outcomes |
| astral.standards.no-cross-contamination | scoped | conforms | context keys only; skills/Events/ACL boundaries held |
| astral.standards.no-hardcoded-sets | scoped | conforms | limit/max/TTL from CONTACT_CONFIG |
| astral.standards.public-then-helpers | scoped | needs-discussion | `_context_cache_*` helpers sit above public load/append API |
| astral.standards.utils-data-late-import-only | scoped | conforms | config.py has no data import |
| astral.state.core-decides-transitions | scoped | not-applicable | no state transitions |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no job state |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no dispatch chain |
| astral.ui.frontend-file-placement | scoped | not-applicable | no frontend paths |
| astral.ui.naming-conventions | scoped | conforms | existing snake_case admin/events routes (ancestry) |
| astral.ui.single-gunicorn-worker | scoped | conforms | process-local cache; multi-worker OOS |
| orch.git.betty-merge-tests-one-sha | universal | conforms | merge-tests `5ce882c8` then publish-ref merge |
| orch.git.commit-vocabulary | universal | conforms | plan/code/test/merge-tests/merge vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | publish on origin/sub/AST-1043/AST-1070-… |
| orch.git.ftr-sub-topology | universal | conforms | matches parent Git table |
| orch.git.merge-on-checkout | universal | conforms | merge origin/dev + publish-ref present |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | none observed |
| orch.git.no-dev-agent-branches | universal | conforms | uses sub/AST-1043/AST-1070-… |
| orch.git.one-epic-worktree-per-parent | universal | conforms | astral-AST-1043 |
| orch.git.three-permanent-branches | universal | conforms | no new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Joan r1 DM-key Decision held in code |
| orch.pipeline.plan-is-bible | universal | violates | load return type/shape + missing channel empty raise vs Stage 3 |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Contact child |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | no statute edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty owns tests/bible |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee Hedy through Tests Passed |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | implementer Hedy remains assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | doc-only review commit paths |

### Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.core.contact-agent (proposed) | needs-discussion | load/append/post present; load return shape ≠ plan Stage 3 dict |
| pattern.external.slack-events (proposed) | conforms | fetch_conversation_history on external slack |
| pattern.config.config-block | conforms | context_history_limit / cache max / TTL |

### Plan adherence

Stages 1–2 and most of Stage 3 land (config keys, external fetch, process-local cache, DM key = `thread_ts` only, inbound append on accept, `contact_post_message`). **Breaks Stage 3 binding return contract** and channel normalize/raise. Betty already noted list return vs plan dict envelope. Self-Assessment MAJOR-CHANGE / high / MEDIUM still honest for the intended design.

### Findings

**fix-now** — `orch.pipeline.plan-is-bible` / Stage 3 `load_slack_conversation_context`  
**Location:** `src/core/contact.py` `load_slack_conversation_context`  
**Issue:** Plan requires `-> dict` returning `{"channel", "thread_ts", "messages", "source": "cache"|"slack"}`. Tip returns `list[dict]` (messages only). Also plan requires strip channel + `ValueError` on empty — not implemented.  
**Action:** Restore Stage 3 envelope (and channel validate); Betty will need bible/test revision for the dict shape (or engineer `[qa-handoff]` if tests were written to the list drift).

**discuss** — C4 straggler: Joan Excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, `astral.layers.scripts-exempt-from-layer-rules`, `astral.patterns.require-auth-on-protected-endpoints`, `astral.ui.naming-conventions` now in-scope via tip ancestry (docs/tests/scripts/ui). All score **conforms** / expected — no product action.

**discuss** — `astral.standards.public-then-helpers`: `_context_cache_key` / `_context_cache_put` appear before public load/append (prefer public-first section then helpers).

**discuss** — `astral.standards.debug-contract-gated`: Style D fires, but detail uses `count=` / outcomes `cache_hit`|`fetched` rather than plan’s `source=` field (same envelope drift).

### What’s solid

DM cache key uses Slack `thread_ts` only (Joan Revision 1); history I/O stays in external; TTL + `refresh=` + config caps; inbound append on accept; no DB transcript SoT.

context_tokens≈56000

---

## Resolution

**2026-07-30** — Radia FIX-NOW (`orch.pipeline.plan-is-bible` / Stage 3 load contract).

- `load_slack_conversation_context` now returns Stage 3 envelope
  `{"channel", "thread_ts", "messages", "source": "cache"|"slack"}` (was bare `list[dict]`).
- Channel strip + `ValueError` on empty restored.
- Style D detail includes `source=` / channel / thread_ts / `len(messages)`.
- `_context_cache_*` helpers moved below public load/append/post (public-then-helpers discuss).
- C4 straggler discuss: no product action (ancestry statutes scored conforms).

**Blocked on Betty:** existing `TestAst1070ContactConversationContext` asserts list return — `[qa-handoff]` for bible/test revision to dict envelope + empty-channel raise.
