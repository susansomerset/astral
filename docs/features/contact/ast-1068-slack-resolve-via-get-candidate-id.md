<!-- linear-archive: AST-1068 archived 2026-08-11 -->

## Linear archive (AST-1068)

**Archived:** 2026-08-11  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1068/slack-resolve-via-get-candidate-id-for-query-prospect-create  
**Status at archive:** Archive  
**Project:** Astral Contact  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1043 — Slack Bot Agent  
**Blocked by / blocks / related:** parent: AST-1043

### Description

## What this implements

Extend get_candidate_id_for_query for Slack user id; on miss create PROSPECT, store Slack user id, seed names from Slack metadata. Create only when @Estelle is in play. Does not own webhook (#2), CONTACT_CONFIG (#1), Manage Slack (#3), or context (#5).

## Acceptance criteria

- [X] Slack user id resolves via get_candidate_id_for_query / CANDIDATE_LOOKUP_CONFIG (AST-1047).
- [X] On miss: create PROSPECT, store Slack user id, seed names from Slack metadata.
- [X] No PROSPECT create without @Estelle in play.

## Boundaries

Does not own Events ingress, Manage Slack, conversation cache, or CONTACT_CONFIG scaffold.

## In scope

- [X] `pattern.state.entity-state-transitions` — register PROSPECT on CANDIDATE_STATES
- [X] AST-1047 `get_candidate_id_for_query` / `pattern.config.config-block` — scan slack_user_id_paths
- [X] `pattern.core.contact-agent` (proposed) — resolve_slack_user + wire into handle_slack_event accept
- [X] `astral.layers.core-vs-external-bright-line` / `astral.layers.import-direction` — [users.info](<http://users.info>) in external; Contact orchestrates
- [X] `astral.config.config-source-of-truth` / `astral.standards.no-hardcoded-sets` — prospect id template + registry
- [X] `astral.config.secrets-and-env-specific-from-environ` — bot token at call time via CONTACT_CONFIG env name
- [X] `astral.state.core-decides-transitions` — core chooses PROSPECT on create
- [X] `astral.standards.debug-contract-gated` / `astral.standards.logging-via-utils` — Style D on resolve when debug=True
- [X] `astral.standards.in-scope-only` / `astral.standards.no-cross-contamination` / `astral.standards.public-then-helpers`

## Considered but excluded

- [X] `pattern.external.slack-events` Events verify/ack/dedupe — AST-1069 (already shipped)
- [X] `pattern.ui.admin-endpoint` / Manage Slack — AST-1067
- [X] Conversation cache — AST-1070
- [X] CONTACT_CONFIG skill ACL bodies — AST-1071
- [X] Estelle turn loop — AST-1046
- [X] `astral.standards.database-header-inventory` — no new tables/columns (existing candidate_data JSON)
- [X] `pattern.db.prospect-create` citation — no catalog file; use initiate_prospect_candidate + state registry instead

## Notes for planning

After #2. AST-1047 Done — extend shipped helper.

## Git branch (authoritative)

Parent `ftr/AST-1043-slack-bot-agent`; child `sub/AST-1043/AST-1068-slack-resolve-via-get-candidate-id`. Created at dispatch-parent.

## Plan

`docs/features/contact/ast-1068-slack-resolve-via-get-candidate-id.md` @ `origin/sub/AST-1043/AST-1068-slack-resolve-via-get-candidate-id` tip `7216151c`.

### Comments

#### betty — 2026-07-30T16:41:11.103Z
[check-linear] merge-tests hygiene: collapsed duplicate `merge-tests(AST-1068)` (was 18fb05d3 / a4acd2f2 / 4bdda264) to exactly one — tip `63b57a60` / `14932dcc` → `origin/tests` `dad4818e` (AST-1017 restore retained). Tip tree unchanged. Stay **User Testing**; assignee Ada for merge-child.

— Betty

#### chuckles — 2026-07-30T16:39:26.758Z
[merge-child] blocked: duplicate merge-tests(AST-1068) on sub — count=3 (amend on tests, one merge-tests only)

@Betty White — validate-sub-log failed. Tips present:
- `18fb05d3` merge-tests (initial)
- `a4acd2f2` merge-tests (AST-1014 revise)
- `4bdda264` merge-tests (AST-1017 restore)

Please consolidate to **one** `merge-tests(AST-1068)` on `origin/sub/AST-1043/AST-1068-slack-resolve-via-get-candidate-id` (amend on `tests`, single merge-tests onto tip), reassign Ada when clean. Status stays **User Testing**.

— Chuckles

#### betty — 2026-07-30T16:37:46.545Z
[check-linear] Cleared [qa-handoff]: restored AST-1017 intake preamble coverage from `origin/dev` onto publish tip (`test_IntakePreamblePanel.test.tsx`, `ast1017PreambleConfig.ts`, `test_CandidateIntake.test.tsx`). Single `merge-tests(AST-1068)` @ `4bdda264` (`origin/tests dad4818e`). Stay **Review Posted**; reassigned Ada for resolve-child.

— Betty

#### ada — 2026-07-30T16:35:41.147Z
[qa-handoff]

@Betty White — Radia **fix-now** on AST-1068 is test-tree restore (engineer ban). Staying **Review Posted**.

**Action (restore from `origin/dev` onto publish tip — no new assertions):**
```bash
git checkout origin/dev -- \
  tests/component/frontend/components/test_IntakePreamblePanel.test.tsx \
  tests/component/frontend/fixtures/ast1017PreambleConfig.ts \
  tests/component/frontend/pages/test_CandidateIntake.test.tsx
```
Then `merge-tests(AST-1068)` / publish to `origin/sub/AST-1043/AST-1068-slack-resolve-via-get-candidate-id` and reassign Ada.

**Why:** During engineer `merge origin/dev` for test-child, banned paths were stripped so the merge commit could pass the engineer hook — tip is missing those AST-1017 files / intake preamble coverage (Radia `54d12f7c` findings).

**Discuss (plan):** Stage 2 profile-seed text updated to AST-1014 columns on tip — see `resolve(AST-1068): — plan AST-1014 seed; qa-handoff for AST-1017 tests`.

— Ada

#### radia — 2026-07-30T16:32:47.186Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1068
**Publish ref:** `54d12f7c` on `origin/sub/AST-1043/AST-1068-slack-resolve-via-get-candidate-id`
**Overall:** FIX-NOW

**Diff change set:** `origin/dev...54d12f7c` — layers `{core, data, external, utils, ui, docs, scripts}`; tip carries Contact ancestry (1066/1067/1069/1071) + AST-1068 resolve/PROSPECT; change_types `{add, modify, delete}`.

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
| astral.config.config-source-of-truth | scoped | conforms | PROSPECT registry + prospect_candidate_id_template in config |
| astral.config.pass-threshold-vs-score-floor | scoped | not-applicable | no threshold/score-floor edits |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | bot token via CONTACT_CONFIG env name at call time |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss artifacts/** / scripts/spikes/** |
| astral.debug.spikes-under-debug-dir | scoped | conforms | docs/features plans only — not spike notes |
| astral.docs.features-single-file-per-ticket | scoped | conforms | one plan file per ticket under docs/features/contact/ |
| astral.git.betty-no-src-or-features | scoped | conforms | merge-tests tips touch tests/bible only |
| astral.git.engineer-test-tree-ban | scoped | needs-discussion | tip drops origin/dev AST-1017 frontend tests after merge (restore) |
| astral.layers.core-vs-external-bright-line | scoped | conforms | users.info in external; Contact orchestrates |
| astral.layers.import-direction | scoped | conforms | core→external/utils; UI never fetches users.info |
| astral.layers.scripts-exempt-from-layer-rules | scoped | conforms | Socket Mode script under scripts/ (ancestry) |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | no React resolve logic; Manage Slack ancestry only |
| astral.patterns.coat-check-never-store-empty | scoped | not-applicable | no coat-check |
| astral.patterns.render-verdict-orchestrates-consult | scoped | not-applicable | no consult |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | no new open data routes this ticket |
| astral.standards.data-raises-caller-logs | scoped | conforms | external raises; Contact handles create/lookup |
| astral.standards.database-header-inventory | scoped | not-applicable | no new tables; existing candidate_data JSON |
| astral.standards.debug-contract-gated | scoped | conforms | Style D on resolve when debug=True |
| astral.standards.dry-and-focused-functions | scoped | conforms | extends AST-1047 matcher; separate prospect initiator |
| astral.standards.in-scope-only | scoped | conforms | no Manage Slack/cache/skills/turn-loop ownership |
| astral.standards.logging-via-utils | scoped | conforms | Contact logger; external users.info silent |
| astral.standards.no-cross-contamination | scoped | violates | tip deletes origin/dev AST-1017 frontend test files |
| astral.standards.no-hardcoded-sets | scoped | conforms | PROSPECT + id template from config |
| astral.standards.public-then-helpers | scoped | conforms | public resolve_slack_user / initiate_prospect surface |
| astral.standards.utils-data-late-import-only | scoped | conforms | config has no data import |
| astral.state.core-decides-transitions | scoped | conforms | core chooses PROSPECT on create |
| astral.state.job-prior-states-enforced | scoped | not-applicable | candidate registry only |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no dispatch chain |
| astral.ui.frontend-file-placement | scoped | conforms | Manage Slack page placement (ancestry) |
| astral.ui.naming-conventions | scoped | conforms | existing snake_case admin/events routes |
| astral.ui.single-gunicorn-worker | scoped | conforms | no worker config change |
| orch.git.betty-merge-tests-one-sha | universal | conforms | merge-tests SHAs present; tip re-merged |
| orch.git.commit-vocabulary | universal | conforms | plan/code/test/merge-tests/merge/resolve vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | publish on origin/sub/AST-1043/AST-1068-… |
| orch.git.ftr-sub-topology | universal | conforms | matches parent Git table |
| orch.git.merge-on-checkout | universal | needs-discussion | merge origin/dev dropped AST-1017 frontend tests |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | none observed |
| orch.git.no-dev-agent-branches | universal | conforms | uses sub/AST-1043/AST-1068-… |
| orch.git.one-epic-worktree-per-parent | universal | conforms | astral-AST-1043 |
| orch.git.three-permanent-branches | universal | conforms | no new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Decisions held; AST-1014 column seed is correct adaptation |
| orch.pipeline.plan-is-bible | universal | needs-discussion | Stage 2 still shows profile seed; tip uses AST-1014 columns |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Contact child |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | no statute authorship |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty owns tests/bible revisions |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee Ada through Tests Passed |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | implementer Ada remains assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | doc-only review commit paths |

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.state.entity-state-transitions | conforms | PROSPECT on CANDIDATE_STATES |
| pattern.config.config-block | conforms | slack_user_id_paths scan + id template |
| pattern.core.contact-agent (proposed) | conforms | resolve_slack_user + Events accept wire |

## Plan adherence

Stages 1–2 product intent lands: PROSPECT registry, lookup scan, `fetch_user_profile`, `resolve_slack_user` gated by `estelle_in_play`, accept-path wire, race re-lookup. Tip correctly seeds names via AST-1014 columns (`first=`/`last=`) instead of plan’s stale `profile` blob. Self-Assessment MAJOR-CHANGE / high / HIGH matches create-gate risk.

## Findings

**fix-now** — `astral.standards.no-cross-contamination` / merge integrity  
**Location:** tip vs `origin/dev` — missing `tests/component/frontend/components/test_IntakePreamblePanel.test.tsx`, `tests/component/frontend/fixtures/ast1017PreambleConfig.ts`; `test_CandidateIntake.test.tsx` regressed (AST-1017 preamble coverage stripped after `cdf5b307` merge origin/dev).  
**Action:** Restore those paths from `origin/dev` onto this publish tip (`git checkout origin/dev -- <paths>` then publish). Do not invent new assertions — restore integration-line coverage.

**discuss** — Stage 2 plan text still shows `profile` seed; tip uses AST-1014 name columns + `initiate_prospect_candidate(..., first=, last=)`. Product is correct; update plan stub to match.

**discuss** — C4 straggler: Joan Excluded docs/tests/scripts/ui statutes now in-scope via tip ancestry — score **conforms** except engineer-test-tree-ban noted above.

## What’s solid

Create gated by `estelle_in_play`; lookup never creates; users.info external-only; PROSPECT separate from `initiate_candidate`; Style D outcomes; Betty revised tests for AST-1014 columns.

Plan append: `docs/features/contact/ast-1068-slack-resolve-via-get-candidate-id.md` @ `54d12f7c`.

context_tokens≈58000

— Radia

#### betty — 2026-07-30T16:25:46.417Z
[check-linear] Tests Ready — cleared [qa-handoff]: revised prospect initiate/resolve asserts for AST-1014 name columns (`first=`/`last=` + `contact.slack_user_id`); single `merge-tests(AST-1068)` @ `a4acd2f2` (`origin/tests 5530072d`). Reassigned Ada for test-child.

**Manifest (unchanged node ids):**
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1068ProspectConfig \
  tests/component/utils/test_config.py::TestAst970CandidateStateRegistry \
  tests/component/core/test_candidate.py::TestAst1068CandidateSlackLookup \
  tests/component/external/test_slack.py::TestAst1068FetchUserProfile \
  tests/component/core/test_contact.py::TestAst1068ResolveSlackUser \
  tests/component/core/test_contact.py::TestAst1069ContactSlackIngress \
  -q
```

**Bible sha256:**
- `docs/test-bible/core/candidate.md` — `2c4b7c9ebb9b8f4ee4e9e9ae0eaa4a499e8fb3ba76008c47ea95f2fc2c32da65`
- `docs/test-bible/core/contact.md` — `0a854cfc70911febe86cde603922d6a03ff336ebc69ce6e636a22a0531438c7b`

— Betty

#### ada — 2026-07-30T16:19:18.590Z
[qa-handoff]

@Betty White — AST-1068 manifest is red on **test contract**, not product.

**Command** (tip `origin/sub/AST-1043/AST-1068-slack-resolve-via-get-candidate-id` @ `951758cc`):
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1068ProspectConfig \
  tests/component/utils/test_config.py::TestAst970CandidateStateRegistry \
  tests/component/core/test_candidate.py::TestAst1068CandidateSlackLookup \
  tests/component/external/test_slack.py::TestAst1068FetchUserProfile \
  tests/component/core/test_contact.py::TestAst1068ResolveSlackUser \
  tests/component/core/test_contact.py::TestAst1069ContactSlackIngress \
  -q
```
**Result:** 3 failed, 27 passed.

**Why tests are wrong (post AST-1014 on origin/dev):**
- `save_candidate_data` / initiate paths **refuse legacy `profile` writes** (`profile was renamed to contact; refuse shadow write`). Names live in **columns** (`first`/`last`/`full`); Slack id stays under **`contact.slack_user_id`**.
- Product after merge: `initiate_prospect_candidate(..., first=, last=)` + `candidate_data={"contact": {"slack_user_id": ...}}` only — see `test(AST-1068): seed Slack names via columns not profile` @ `951758cc`.

**Failing cases still assert pre-1014 `profile` blob:**
1. `TestAst1068CandidateSlackLookup::test_initiate_prospect_candidate` — passes `profile` in `candidate_data` → ValueError.
2. `TestAst1068ResolveSlackUser::test_resolve_create_prospect` — asserts `args[1]["profile"]["first"]`.
3. `TestAst1068ResolveSlackUser::test_resolve_create_seeds_display_name` — same `profile` assert.

Please revise those cases (and bible notes if needed) for name columns + kwargs, re-`merge-tests`, reassign me. Staying **Tests Ready**.

#### betty — 2026-07-30T16:14:36.555Z
## QA test manifest

`origin/sub/AST-1043/AST-1068-slack-resolve-via-get-candidate-id` @ `18fb05d3` (`merge-tests(AST-1068): origin/tests 15220228`).

1. `tests/component/utils/test_config.py::TestAst1068ProspectConfig` — `PROSPECT` on `CANDIDATE_STATES` + `prospect_candidate_id_template`
2. `tests/component/utils/test_config.py::TestAst970CandidateStateRegistry` — **revised** (was assert PROSPECT absent)
3. `tests/component/core/test_candidate.py::TestAst1068CandidateSlackLookup` — `get_candidate_id_for_query` slack path + `initiate_prospect_candidate`
4. `tests/component/external/test_slack.py::TestAst1068FetchUserProfile` — gated `users.info`
5. `tests/component/core/test_contact.py::TestAst1068ResolveSlackUser` — resolve hit/miss/create + Events accept wire
6. `tests/component/core/test_contact.py::TestAst1069ContactSlackIngress` — **revised** (stub `resolve_slack_user` on accept)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1068ProspectConfig \
  tests/component/utils/test_config.py::TestAst970CandidateStateRegistry \
  tests/component/core/test_candidate.py::TestAst1068CandidateSlackLookup \
  tests/component/external/test_slack.py::TestAst1068FetchUserProfile \
  tests/component/core/test_contact.py::TestAst1068ResolveSlackUser \
  tests/component/core/test_contact.py::TestAst1069ContactSlackIngress \
  -q
```

**Bible sha256** (`git show origin/sub/AST-1043/AST-1068-slack-resolve-via-get-candidate-id:<path>`):
- `docs/test-bible/core/contact.md` `b8040d93847966a67e2e6797fd5e5264e051533a6a6da397487d3ad1720d4b90`
- `docs/test-bible/core/candidate.md` `20e04e0a258f81b40e792e440d9f3f64742a1230c21576509b94cd0521ad1cc0`
- `docs/test-bible/external/slack.md` `42ce355becbe7b5c24d805d66e19df648040c129d3e28e16e7dab5071dfb5e6b`
- `docs/test-bible/utils/config.md` `68bbd3bfa05df703023c8dd37e94c453459231a8ab8036ff5368d18e6f7696ab`

— Betty

#### joan — 2026-07-30T03:59:14.653Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1068
**Overall:** APPROVED

Plan tip `5ea73df5` on `origin/sub/AST-1043/AST-1068-slack-resolve-via-get-candidate-id`. Layers: utils, docs, core, external. Change types: add, modify.

## Traceability

### Parent AC → plan stages

| Parent AC | Map |
| -- | -- |
| AC1 Estelle DM/@ ingress ready | N/A — boundary; Events ingress AST-1069 |
| AC2 Events Request URL / verify / ack | N/A — AST-1069 |
| AC3 Manage Slack listen switch | N/A — AST-1067 |
| AC4 Slack resolve via `get_candidate_id_for_query`; PROSPECT create-on-miss; no create without Estelle | Stages 1–2 |
| AC5 Resolve exposes candidate + state-machine status | Stage 2 (`astral_candidate_id`, `candidate_state` on accept result) |
| AC6 Conversation history / cache | N/A — AST-1070 |
| AC7 CONTACT_CONFIG skill ACL | N/A — AST-1071 / AST-1066 scaffold |
| AC8 debug Style D on Contact/Slack paths | Stage 2 (`resolve_slack_user` gated debug) |

### Child AC → plan stages

| Child AC | Map |
| -- | -- |
| Slack user id resolves via lookup / `CANDIDATE_LOOKUP_CONFIG` | Stage 1 (`slack_user_id_paths` scan) |
| On miss: PROSPECT + store Slack user id + seed names | Stage 2 (`initiate_prospect_candidate` + `users.info`) |
| No PROSPECT without @Estelle in play | Stage 2 (`estelle_in_play` + wire only on accept) |

### Plan stages → definition

| Stage | Maps to |
| -- | -- |
| 1 PROSPECT registry + lookup matcher | Purpose/Functional scope resolve; Architectural `pattern.state.entity-state-transitions` + AST-1047 extend |
| 2 users.info + resolve + Events accept wire | Parent AC4/AC5; child create gate; layers bright-line |

## Statute verdicts

| id | verdict | one-line |
| -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | conforms | Plan does not touch Betty merge / test SHA rules |
| orch.git.commit-vocabulary | conforms | Execution contract: one commit per stage |
| orch.git.flow-direction-inviolable | conforms | Publish to child `sub/AST-1043/AST-1068-…` only |
| orch.git.ftr-sub-topology | conforms | Child sub under parent ftr topology |
| orch.git.merge-on-checkout | conforms | No contrary merge instructions |
| orch.git.no-cherry-pick-rebase-force | conforms | No rewrite ops planned |
| orch.git.no-dev-agent-branches | conforms | Uses dispatched sub ref |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree contract stated |
| orch.git.three-permanent-branches | conforms | No new permanent branch |
| orch.pipeline.call-susan-for-product-decisions | conforms | Decisions recorded in plan; Stage-blocked escalate path |
| orch.pipeline.plan-is-bible | conforms | Binding execution contract present |
| orch.pipeline.project-scoped-queues | conforms | Single-child scope; no queue invention |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate path only |
| orch.roles.archie-approves-statutes | conforms | No statute authorship |
| orch.roles.betty-owns-test-tree | conforms | Explicit: do not edit tests/bible |
| orch.roles.chuckles-never-ticket-assignee | conforms | No assignee instructions for Chuckles-as-implementer |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer owns build after approve |
| orch.roles.pre-commit-path-bans | conforms | No banned-path edits planned |
| astral.agent.confidence-bounds | conforms | No agent grade/confidence surface |
| astral.agent.do-task-delegation | conforms | No `do_task` / DeepSeek in this child |
| astral.agent.grade-vector-validation | conforms | No grade vectors |
| astral.batch.batch-id-first | conforms | Not a batch claim path |
| astral.batch.batch-id-format | conforms | No batch ids |
| astral.batch.claim-process-release | conforms | No batch claim/process/release |
| astral.batch.entity-agent-responses-latest-only | conforms | No agent_data latest-ref writes |
| astral.config.config-source-of-truth | conforms | PROSPECT + template + paths in config |
| astral.config.pass-threshold-vs-score-floor | conforms | No pass-threshold edits |
| astral.config.secrets-and-env-specific-from-environ | conforms | Bot token via `CONTACT_CONFIG["bot_token_env"]` strict environ |
| astral.git.betty-no-src-or-features | conforms | Engineer-owned src/features plan |
| astral.layers.core-vs-external-bright-line | conforms | `users.info` in external; Contact orchestrates |
| astral.layers.import-direction | conforms | Files table respects core→external/utils; external→utils |
| astral.layers.ui-config-driven-business-logic | conforms | Config touch is registry/template only; no UI logic |
| astral.patterns.coat-check-never-store-empty | conforms | No coat-check usage |
| astral.patterns.render-verdict-orchestrates-consult | conforms | No Consult/render_verdict |
| astral.standards.data-raises-caller-logs | conforms | External raises; core handles create/lookup |
| astral.standards.debug-contract-gated | conforms | Style D only when `debug=True` |
| astral.standards.dry-and-focused-functions | conforms | Extends AST-1047 matcher; separate prospect initiator |
| astral.standards.in-scope-only | conforms | Sibling scopes listed Out of scope |
| astral.standards.logging-via-utils | conforms | Debug via logger contract; external `users.info` no log |
| astral.standards.no-cross-contamination | conforms | Stays in layered `src/*` |
| astral.standards.no-hardcoded-sets | conforms | Registry key + id template in config |
| astral.standards.public-then-helpers | conforms | New public entrypoints named; no helper scatter mandated |
| astral.standards.utils-data-late-import-only | conforms | No utils↔data import change |
| astral.state.core-decides-transitions | conforms | Core chooses `PROSPECT` on create; data saves param |
| astral.state.job-prior-states-enforced | conforms | Candidate registry only; no job transition rewrite |
| astral.state.no-daisy-chain-in-run | conforms | No daisy-chain run path |
| astral.ui.single-gunicorn-worker | conforms | No gunicorn/worker config change |

## Considered and excluded

**Considered:** all rows in Statute verdicts (47).

**Excluded:**
- `astral.debug.no-repo-root-artifacts-dir` — paths miss plan files
- `astral.debug.spikes-under-debug-dir` — paths miss plan files
- `astral.docs.features-single-file-per-ticket` — paths miss plan files (plan doc already published; Files Changed has no `docs/features/**`)
- `astral.git.engineer-test-tree-ban` — paths miss tests/bible
- `astral.layers.scripts-exempt-from-layer-rules` — layers/paths miss scripts
- `astral.patterns.require-auth-on-protected-endpoints` — layers/paths miss ui
- `astral.standards.database-header-inventory` — layers/paths miss data (reuses `save_candidate` / existing JSON)
- `astral.ui.frontend-file-placement` — layers/paths miss ui frontend
- `astral.ui.naming-conventions` — layers/paths miss ui

## Findings

**discuss** — Parent AC4 says “no @ means no candidate”; plan treats Estelle-in-play as AST-1069 accept (DM `message` **or** `app_mention`). Reading aligns with Purpose (DM or @) and child AC “Estelle in play”; not a fix-now.

**acceptable** — Self-assessment `HIGH` risk with explicit create-gate, separate initiator, and controlled external I/O mitigations; honest.

No `fix-now`. R1–R6 pass.

context_tokens≈32000

— Joan

#### joan — 2026-07-30T03:53:19.619Z
validate-plan blocked — AGENTS.md is Katherine, not Joan.

context_tokens≈6000

— Joan

#### joan — 2026-07-30T03:49:18.514Z
validate-plan stopped — worktree AGENTS.md is **Hedy**, not Joan.

Epic worktree `/home/susan/astral-AST-1043/` header reads `# Hedy — Dev Agent`. Skill requires `# Joan — Statute Validator` (Chuckles seed) before validate-plan runs.

Linear identity is Joan; assignee on AST-1068 is Joan; status Plan Ready — only the worktree seed is wrong.

Chuckles: re-seed `joan-AGENTS.md` into this epic worktree, then re-spawn validate-plan for AST-1068.

context_tokens≈8000

— Joan

#### joan — 2026-07-30T03:44:22.571Z
validate-plan blocked: assignee is Ada Lovelace, not Joan. Chuckles must assign Joan before validate-plan runs.

Status is Plan Ready — no rubric pass until assignee is Joan.

context_tokens≈42000

— Joan

#### ada — 2026-07-30T03:42:15.188Z
Plan published.

**Doc:** https://github.com/susansomerset/astral/blob/sub/AST-1043/AST-1068-slack-resolve-via-get-candidate-id/docs/features/contact/ast-1068-slack-resolve-via-get-candidate-id.md
**Tip:** `5ea73df5` on `origin/sub/AST-1043/AST-1068-slack-resolve-via-get-candidate-id`

**Self-assessment**
- **Scope:** MAJOR-CHANGE — PROSPECT registry + lookup teach-in + Contact resolve create + external users.info.
- **Conf:** high — extends AST-1047/1066; Estelle-in-play = AST-1069 accept path; separate initiate_prospect_candidate.
- **Risk:** HIGH — create-gate / registry / users.info I/O; mitigated by estelle_in_play flag + controlled external I/O.

---

# AST-1068 — Slack resolve via get_candidate_id_for_query + PROSPECT create

**Linear:** [AST-1068](https://linear.app/astralcareermatch/issue/AST-1068/slack-resolve-via-get-candidate-id-for-query-prospect-create)  
**Parent:** [AST-1043](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent) — Slack Bot Agent  
**Publish ref:** `origin/sub/AST-1043/AST-1068-slack-resolve-via-get-candidate-id`

Extend shipped AST-1047 **`get_candidate_id_for_query`** to scan **`CANDIDATE_LOOKUP_CONFIG["slack_user_id_paths"]`**, register **`PROSPECT`** on **`CANDIDATE_STATES`**, and add Contact **`resolve_slack_user`** that looks up by Slack user id and, **only when Estelle is in play** (accepted DM / `app_mention`), creates a PROSPECT with `contact.slack_user_id` + Slack-seeded name fields. Does **not** own Events verify/ack (AST-1069), Manage Slack UI (AST-1067), conversation cache (AST-1070), skill ACL bodies (AST-1071), or Estelle turn loop (AST-1046).

**Depends on (already on `origin/ftr/AST-1043-slack-bot-agent`):** AST-1066 (`slack_user_id_paths` + Contact scaffold), AST-1069 (`handle_slack_event` accept path).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Register `PROSPECT` on `CANDIDATE_STATES`; drop “not a registry key” assert/comment; optional `CONTACT_CONFIG` id template | utils |
| `docs/ASTRAL_CODE_RULES.md` | One-line `CANDIDATE_STATES` catalog: PROSPECT is a real key (was “No PROSPECT”) | docs |
| `src/core/candidate.py` | Teach `get_candidate_id_for_query` to scan `slack_user_id_paths`; add `initiate_prospect_candidate(...)` | core |
| `src/external/slack.py` | Add `fetch_user_profile(user_id)` via Slack `users.info` (call-time token) | external |
| `src/core/contact.py` | Add `resolve_slack_user(...)`; call it from `handle_slack_event` after accept | core |

---

## Stage 1: PROSPECT registry + lookup matcher

**Done when:** `PROSPECT` is a real `CANDIDATE_STATES` key; `get_candidate_id_for_query` returns a unique id when the needle matches `contact.slack_user_id`; no Contact create yet.

1. In `src/utils/config.py` `CANDIDATE_STATES` block:

   - Replace the header comment line that says `PROSPECT is conceptual only — not a registry key` with: `PROSPECT = Slack-created candidate (AST-1068); prior_states None (entry state).`
   - Add as the **first** registry entry (before `NEW_CANDIDATE`):

```python
    "PROSPECT": {"prior_states": None, "progress_rank": -1},
```

   - **Delete** `assert "PROSPECT" not in CANDIDATE_STATES`.
   - Keep `assert CANDIDATE_CONFIG["initial_state"] in CANDIDATE_STATES` (still `NEW_CANDIDATE` for admin/`initiate_candidate` — do **not** change `initial_state` to PROSPECT).

⚠️ **Decision — PROSPECT vs NEW_CANDIDATE:** Slack create-on-miss lands in **`PROSPECT`**. Admin/`initiate_candidate` stays on **`NEW_CANDIDATE`**. `prior_states: None` on both entry states (same unrestricted pattern as `INACTIVE` / `DELETED`). Downstream intake may later transition PROSPECT → NEW_CANDIDATE / INTAKE (out of scope here — `NEW_CANDIDATE` already allows unrestricted entry).

2. In `CONTACT_CONFIG`, add (after `app_token_env` is fine):

```python
    # Deterministic astral_candidate_id for Slack-created PROSPECTs (format with slack_user_id=).
    "prospect_candidate_id_template": "slack-{slack_user_id}",
```

   Assert: `"{slack_user_id}" in CONTACT_CONFIG["prospect_candidate_id_template"]`.

3. In `docs/ASTRAL_CODE_RULES.md` §2.1 **CANDIDATE_STATES** bullet, change the trailing `No PROSPECT.` to: `Includes PROSPECT (Slack create-on-miss; AST-1068).`

4. In `src/core/candidate.py` `get_candidate_id_for_query`:

   - Change the path tuple to:

```python
    paths = (
        tuple(CANDIDATE_LOOKUP_CONFIG["email_paths"])
        + tuple(CANDIDATE_LOOKUP_CONFIG["name_paths"])
        + tuple(CANDIDATE_LOOKUP_CONFIG["slack_user_id_paths"])
    )
```

   - Keep existing needle normalization (`parseaddr` / `@` rule) and `match_casefold` behavior for **all** paths (Slack ids are opaque tokens; casefold is harmless and keeps one compare path).
   - Do **not** create candidates here. Do **not** invent a second matcher function.

5. Still in `candidate.py`, add public:

```python
def initiate_prospect_candidate(
    astral_candidate_id: str,
    candidate_data: Optional[Dict[str, Any]] = None,
) -> None:
    """Create a candidate row in PROSPECT (Slack create-on-miss). Not NEW_CANDIDATE."""
```

   Behavior (literal):

   - Strip `astral_candidate_id`; if empty → `ValueError("astral_candidate_id is required")`.
   - If `get_candidate(astral_candidate_id)` is not None → `ValueError` (already exists).
   - `state="PROSPECT"` (literal from registry — do not use `CANDIDATE_CONFIG["initial_state"]`).
   - `database.save_candidate(...)` with `candidate_data=candidate_data or {}` and `state_history` via existing `_append_candidate_state_history({}, "", "PROSPECT", now)` (same timestamp format as `initiate_candidate`).

⚠️ **Decision — separate initiator:** Do not overload `initiate_candidate` with a state kwarg that admin POST might misuse. Slack-only create uses `initiate_prospect_candidate`.

**Done when (recheck):** `from src.utils.config import CANDIDATE_STATES` → `"PROSPECT" in CANDIDATE_STATES`; `get_candidate_id_for_query` matches a row whose `candidate_data.contact.slack_user_id` equals the needle (unique).

---

## Stage 2: Slack `users.info` + Contact resolve + wire into Events accept

**Done when:** Accepted DM / `app_mention` events resolve to an `astral_candidate_id` + candidate `state`; first unknown Slack user creates PROSPECT with stored Slack id and seeded names; bare lookup miss outside Estelle-in-play does **not** create.

1. In `src/external/slack.py`, export and implement:

```python
def fetch_user_profile(user_id: str) -> dict:
    """GET users.info; return a small profile dict. Call-time bot token. No logging."""
```

   Behavior (literal):

   - `require_controlled_external_io("slack.fetch_user_profile")`.
   - `token = os.environ[CONTACT_CONFIG["bot_token_env"]]` (strict — no `.get`).
   - `POST` or `GET` `https://slack.com/api/users.info` with `user=<stripped user_id>` and Bearer/token auth matching existing `post_message` style in this file.
   - On HTTP/transport failure → raise (same family as `post_message`).
   - Parse JSON; if `ok` is not true → raise `RuntimeError` with Slack `error` string when present.
   - From `user.profile` (and top-level `user` as fallback), return **only**:

```python
{
    "slack_user_id": <stripped user_id>,
    "first": <profile.first_name or "">,
    "last": <profile.last_name or "">,
    "display_name": <profile.display_name or profile.real_name or "">,
}
```

   - All string values stripped; missing → `""`. Do **not** log. Do **not** return email/phone/token fields.

2. In `src/core/contact.py`, add public:

```python
def resolve_slack_user(
    slack_user_id: str,
    *,
    estelle_in_play: bool,
    debug: bool = False,
) -> dict:
    """Lookup Slack user → astral candidate; create PROSPECT only when estelle_in_play."""
```

   Behavior (literal):

   - `sid = (slack_user_id or "").strip()`. If empty → `ValueError("slack_user_id is required")`.
   - If `debug`: `logger.set_debug_flag(True)`.
   - **Lookup:** `cid = get_candidate_id_for_query(sid, debug=debug)`.
   - If `cid` is not None:
     - `row = get_candidate(cid)` (must exist).
     - If `debug`: Style D `func="contact.resolve_slack_user"`, outcome `found|matched`, details `slack_user_id=`, `candidate_id=`, `state=`.
     - Return `{"astral_candidate_id": cid, "state": row["state"], "created": False}`.
   - If `cid` is None and **`estelle_in_play` is not True**:
     - If `debug`: outcome `found|none` (no create).
     - Return `{"astral_candidate_id": None, "state": None, "created": False}`.
   - If `cid` is None and **`estelle_in_play` is True** (create path):
     - `slack_profile = fetch_user_profile(sid)` from `src.external.slack` (returns first/last/display_name — Slack API fields, not a candidate `profile` blob).
     - `new_id = CONTACT_CONFIG["prospect_candidate_id_template"].format(slack_user_id=sid)`. Strip/lower the id the same way admin create does for consistency: `.strip().lower()`.
     - Seed names via **AST-1014 name columns** (do **not** write legacy `candidate_data["profile"]` — refused by `save_candidate_data` / initiate paths):
       - `first = slack_profile.get("first") or ""`, `last = slack_profile.get("last") or ""`.
       - If `slack_profile["display_name"]` is non-empty and both first/last empty, set `first = display_name` (single-field seed — do not invent a last name).
     - Build `candidate_data` with Slack id only under contact:

```python
{"contact": {"slack_user_id": sid}}
```

     - Call `initiate_prospect_candidate(new_id, candidate_data, first=first, last=last)`.
     - If `debug`: outcome `recorded|created`, details `slack_user_id=`, `candidate_id=`, `state=PROSPECT`.
     - Return `{"astral_candidate_id": new_id, "state": "PROSPECT", "created": True}`.

⚠️ **Decision — AC3 “no create without @Estelle in play”:** Create is gated by the explicit `estelle_in_play=True` kw-only flag. `get_candidate_id_for_query` never creates. Callers that are not Contact Events accept must pass `False` (or omit create by not calling resolve).

⚠️ **Decision — id template:** `slack-{slack_user_id}` lowercased keeps create idempotent under races (second create hits “already exists” — on `ValueError` from `initiate_prospect_candidate`, re-lookup via `get_candidate_id_for_query(sid)` and return matched row with `created=False` if found; else re-raise).

3. In `handle_slack_event`, **after** building the accepted `result` dict and **before** the final debug/return (only on the `accepted=True` path):

   - Read `user = result.get("user")`.
   - If `user` is a non-empty `str`:
     - `resolved = resolve_slack_user(user, estelle_in_play=True, debug=debug)`
     - Set `result["astral_candidate_id"] = resolved["astral_candidate_id"]`
     - Set `result["candidate_state"] = resolved["state"]`
     - Set `result["candidate_created"] = resolved["created"]`
   - Else leave those keys absent / set to `None` (do not create).

⚠️ **Decision — wire site:** AST-1069 left `handle_slack_event` without resolve by design. Estelle-in-play **is** that function’s accept path (DM `message` or `app_mention` after listen/dedupe/type filters). Do **not** create from URL verification, signature failure, or `accepted=False` returns.

4. Do **not** edit Manage Slack UI, conversation cache, skill runners, `TASK_CONFIG`, or Estelle turn loop. Do **not** edit `tests/` / bible.

**Done when (recheck):** With listen on and an accepted `app_mention`/`message` DM payload for an unknown Slack user, Contact returns `astral_candidate_id` + `candidate_state="PROSPECT"` and a row stores `contact.slack_user_id`; a second event for the same user matches without a second row; `resolve_slack_user(..., estelle_in_play=False)` on a miss returns null id and creates nothing.

---

## Out of scope (do not implement here)

- Events signature / challenge / dedupe / Socket Mode (AST-1069 — already shipped).
- Manage Slack listen flip UI (AST-1067).
- Conversation history load/cache (AST-1070).
- CONTACT_CONFIG skill runner inventory changes (AST-1071 — do not allowlist `contact.slack_user_id` there).
- Estelle conversational turn / `post_message` reply loop (AST-1046).
- Formal PROSPECT → NEW_CANDIDATE intake automation (future; registry only enables the hop).
- Editing `tests/` or `docs/test-bible/**` (Betty after Code Complete).

---

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — candidate state registry + lookup matcher + Contact resolve create path + external `users.info`; touches utils/core/external and a one-line code-rules catalog fix.

**Conf:** `high` — extends AST-1047 matcher and AST-1066 path home; mirrors `initiate_candidate` for PROSPECT; Events accept hook is the natural Estelle-in-play gate from AST-1069.

**Risk:** `HIGH` — wrong create gate could invent candidates without @/DM; wrong PROSPECT registry could break candidate transitions; `users.info` needs controlled I/O. Mitigated by `estelle_in_play` flag, separate initiator, and `require_controlled_external_io`.

## Rules self-review

- **§2.1 / no-hardcoded-sets:** Slack id path + prospect id template + PROSPECT key live in config.
- **§2.6 / core-decides-transitions:** Core chooses PROSPECT on create; data only saves the state parameter.
- **§2.5 / §3.3:** `users.info` in external; Contact orchestrates; candidate matcher stays in `candidate.py`.
- **§1.5.1 debug-contract:** Style D only when `debug=True` on resolve.
- **§1.1 in-scope-only:** Sibling scopes listed Out of scope.
- **secrets-from-environ:** Token via `CONTACT_CONFIG["bot_token_env"]` at call time (existing 1069 pattern).

## Execution contract

The plan is binding. Execute stages in order; one commit per stage on epic worktree; publish to `origin/sub/AST-1043/AST-1068-slack-resolve-via-get-candidate-id`. On ambiguity or drift, stop and comment on parent **AST-1043** with the Stage-blocked format — do not improvise.

## Review (build stub)

- **Publish ref:** `origin/sub/AST-1043/AST-1068-slack-resolve-via-get-candidate-id`
- **Tip:** `7216151c` — resolve_slack_user + users.info + Events wire
- **Stage commits:** `0856416a` (PROSPECT registry + lookup), `7216151c` (resolve + wire)

---

## Review (Radia / code-rubric.v1)

[code-rubric] revision=1  
**Rubric:** code-rubric.v1  
**Ticket:** AST-1068  
**Publish ref:** `2b0a4352` on `origin/sub/AST-1043/AST-1068-slack-resolve-via-get-candidate-id` (docs tip follows)  
**Overall:** FIX-NOW

**Diff change set:** `origin/dev...2b0a4352` — layers `{core, data, external, utils, ui, docs, scripts}`; tip carries Contact ancestry (1066/1067/1069/1071) + AST-1068 resolve/PROSPECT; change_types `{add, modify, delete}`.

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
| astral.config.config-source-of-truth | scoped | conforms | PROSPECT registry + prospect_candidate_id_template in config |
| astral.config.pass-threshold-vs-score-floor | scoped | not-applicable | no threshold/score-floor edits |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | bot token via CONTACT_CONFIG env name at call time |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss artifacts/** / scripts/spikes/** |
| astral.debug.spikes-under-debug-dir | scoped | conforms | docs/features plans only — not spike notes |
| astral.docs.features-single-file-per-ticket | scoped | conforms | one plan file per ticket under docs/features/contact/ |
| astral.git.betty-no-src-or-features | scoped | conforms | merge-tests tips touch tests/bible only |
| astral.git.engineer-test-tree-ban | scoped | needs-discussion | tip drops origin/dev AST-1017 frontend tests after merge (restore) |
| astral.layers.core-vs-external-bright-line | scoped | conforms | users.info in external; Contact orchestrates |
| astral.layers.import-direction | scoped | conforms | core→external/utils; UI never fetches users.info |
| astral.layers.scripts-exempt-from-layer-rules | scoped | conforms | Socket Mode script under scripts/ (ancestry) |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | no React resolve logic; Manage Slack ancestry only |
| astral.patterns.coat-check-never-store-empty | scoped | not-applicable | no coat-check |
| astral.patterns.render-verdict-orchestrates-consult | scoped | not-applicable | no consult |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | no new open data routes this ticket |
| astral.standards.data-raises-caller-logs | scoped | conforms | external raises; Contact handles create/lookup |
| astral.standards.database-header-inventory | scoped | not-applicable | no new tables; existing candidate_data JSON |
| astral.standards.debug-contract-gated | scoped | conforms | Style D on resolve when debug=True |
| astral.standards.dry-and-focused-functions | scoped | conforms | extends AST-1047 matcher; separate prospect initiator |
| astral.standards.in-scope-only | scoped | conforms | no Manage Slack/cache/skills/turn-loop ownership |
| astral.standards.logging-via-utils | scoped | conforms | Contact logger; external users.info silent |
| astral.standards.no-cross-contamination | scoped | violates | tip deletes origin/dev AST-1017 frontend test files |
| astral.standards.no-hardcoded-sets | scoped | conforms | PROSPECT + id template from config |
| astral.standards.public-then-helpers | scoped | conforms | public resolve_slack_user / initiate_prospect surface |
| astral.standards.utils-data-late-import-only | scoped | conforms | config has no data import |
| astral.state.core-decides-transitions | scoped | conforms | core chooses PROSPECT on create |
| astral.state.job-prior-states-enforced | scoped | not-applicable | candidate registry only |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no dispatch chain |
| astral.ui.frontend-file-placement | scoped | conforms | Manage Slack page placement (ancestry) |
| astral.ui.naming-conventions | scoped | conforms | existing snake_case admin/events routes |
| astral.ui.single-gunicorn-worker | scoped | conforms | no worker config change |
| orch.git.betty-merge-tests-one-sha | universal | conforms | merge-tests SHAs present; tip re-merged |
| orch.git.commit-vocabulary | universal | conforms | plan/code/test/merge-tests/merge/resolve vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | publish on origin/sub/AST-1043/AST-1068-… |
| orch.git.ftr-sub-topology | universal | conforms | matches parent Git table |
| orch.git.merge-on-checkout | universal | needs-discussion | merge origin/dev dropped AST-1017 frontend tests |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | none observed |
| orch.git.no-dev-agent-branches | universal | conforms | uses sub/AST-1043/AST-1068-… |
| orch.git.one-epic-worktree-per-parent | universal | conforms | astral-AST-1043 |
| orch.git.three-permanent-branches | universal | conforms | no new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Decisions held; AST-1014 column seed is correct adaptation |
| orch.pipeline.plan-is-bible | universal | needs-discussion | Stage 2 still shows profile seed; tip uses AST-1014 columns |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Contact child |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | no statute authorship |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty owns tests/bible revisions |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee Ada through Tests Passed |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | implementer Ada remains assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | doc-only review commit paths |

### Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.state.entity-state-transitions | conforms | PROSPECT on CANDIDATE_STATES |
| pattern.config.config-block | conforms | slack_user_id_paths scan + id template |
| pattern.core.contact-agent (proposed) | conforms | resolve_slack_user + Events accept wire |

### Plan adherence

Stages 1–2 product intent lands: PROSPECT registry, lookup scan, `fetch_user_profile`, `resolve_slack_user` gated by `estelle_in_play`, accept-path wire, race re-lookup. Tip correctly seeds names via AST-1014 columns (`first=`/`last=`) instead of plan’s stale `profile` blob. Self-Assessment MAJOR-CHANGE / high / HIGH matches create-gate risk.

### Findings

**fix-now** — `astral.standards.no-cross-contamination` / merge integrity  
**Location:** tip vs `origin/dev` — missing `tests/component/frontend/components/test_IntakePreamblePanel.test.tsx`, `tests/component/frontend/fixtures/ast1017PreambleConfig.ts`; `test_CandidateIntake.test.tsx` regressed (AST-1017 preamble coverage stripped after `cdf5b307` merge origin/dev).  
**Action:** Restore those paths from `origin/dev` onto this publish tip (`git checkout origin/dev -- <paths>` then publish). Do not invent new assertions — restore integration-line coverage.

**discuss** — Stage 2 plan text still shows `profile` seed; tip uses AST-1014 name columns + `initiate_prospect_candidate(..., first=, last=)`. Product is correct; update plan stub to match.

**discuss** — C4 straggler: Joan Excluded docs/tests/scripts/ui statutes now in-scope via tip ancestry — score **conforms** except engineer-test-tree-ban noted above.

### What’s solid

Create gated by `estelle_in_play`; lookup never creates; users.info external-only; PROSPECT separate from `initiate_candidate`; Style D outcomes; Betty revised tests for AST-1014 columns.

context_tokens≈58000

---

## Resolution

**2026-07-30** — resolve-child after Radia `Review Posted` @ `54d12f7c`.

| Finding | Disposition |
| -- | -- |
| **fix-now** — restore AST-1017 frontend tests dropped when engineer merge of `origin/dev` stripped banned paths | **Cleared** — Betty `merge-tests(AST-1068)` @ `4bdda264` (`origin/tests dad4818e`); tip matches `origin/dev` for the three paths |
| **discuss** — Stage 2 plan still showed `profile` seed | **Addressed** — Stage 2 create path now documents AST-1014 name columns (`first=`/`last=`) + `contact.slack_user_id` only |
| **discuss** — C4 ancestry statutes | **Noted** — no product change |

Also merged `origin/ftr/AST-1043-slack-bot-agent` (AST-1070 context) keeping both `resolve_slack_user` / `fetch_user_profile` and conversation cache / `fetch_conversation_history`.

**2026-07-30 (resume):** Absorbed Betty tip; AST-1017 paths verified identical to `origin/dev`; graduating to User Testing after §9a.
