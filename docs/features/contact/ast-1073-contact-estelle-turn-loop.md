<!-- linear-archive: AST-1073 archived 2026-08-14 -->

## Linear archive (AST-1073)

**Archived:** 2026-08-14  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1073/contact-estelle-turn-loop-over-ast-1043-contact-contact-estelle  
**Status at archive:** Archive  
**Project:** Astral Contact  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-1046 — Contact Estelle conversational envelope  
**Blocked by / blocks / related:** parent: AST-1046

### Description

## What this implements

Wire resolve + Slack context + ACL + listen gate into turns consuming the envelope. After #1; after **AST-1043**.

## Acceptance criteria

- [X] Estelle can complete a multi-turn Slack conversation using **AST-1043** Contact plumbing.
- [X] Each agent turn yields a structured envelope outcome of success, failure, or concern.
- [X] Honor Manage Slack listen gate and non-production `[<environment>]` prefix from **AST-1043**.
- [X] Debug=True paths emit contract index + `|` detail for turn outcomes.

## Boundaries

Does **not** own the conversational envelope schema (sibling AST-1072). Does **not** re-implement Slack Events ingress, Manage Slack switch, resolve-util, Slack context cache, or Contact ACL skill catalog (**AST-1043**).

## In scope

- [X] `pattern.core.contact-agent` (proposed) — `run_contact_estelle_turn` + hook from `handle_slack_event` (`src/core/contact.py`)
- [X] `astral.agent.do-task-delegation` — turn calls `do_task(CONTACT_ESTELLE_CONFIG["task_key"])` only; no direct Anthropic assembly
- [X] `astral.standards.debug-contract-gated` — Style D on turn outcomes when `debug=True`
- [X] `pattern.config.config-block` — `CONTACT_ESTELLE_CONFIG` turn trim keys + optional `skill_calls` on `contact_estelle_turn` response_schema (`src/utils/config.py`)
- [X] `astral.layers.core-vs-external-bright-line` / `astral.layers.import-direction` — core orchestrates; Slack I/O only via existing Contact helpers (no UI→external)
- [X] `astral.standards.in-scope-only` — consume AST-1043 helpers + AST-1072 envelope; no Events/Manage Slack/resolve/cache/ACL registration rewrite
- [X] `astral.standards.dry-and-focused-functions` — reuse context load, `run_contact_skill`, format+post helpers, `conversational_turn_from_do_task_result`
- [X] `astral.standards.no-hardcoded-sets` — skill keys / trim limits from config
- [X] `astral.standards.logging-via-utils` — concern aside via logger; no ad-hoc print
- [X] Prompt enrich for `contact_estelle_turn` in `data/admin/agent_task.json` (skill_calls + Slack context)

## Considered but excluded

* Conversational envelope performance schema / CHAT validation / Medium brain override — AST-1072 (`src/utils/config.py` CONVERSATIONAL_*, `src/core/agent.py`)
* Slack Events verify/ack, Manage Slack UI, resolve/PROSPECT, context cache implementation, CONTACT_CONFIG skills ACL registration — AST-1043 children (`src/external/slack.py`, `api_slack.py`, `api_contact.py`, etc.)
* Mutating `principal_recruiter_estelle.brain_setting` globally — AST-1072 decision (Big for upshot)
* Full-exchange DB transcript store — forbidden by AST-1070 / parent boundaries
* Universal `orch.*` statutes — not listed per-child

## Notes for planning

Turn loop over AST-1043 Contact plumbing; consumes envelope from sibling.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at dispatch-parent.

### Comments

#### radia — 2026-07-31T00:01:20.051Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1073
**Publish ref:** `origin/sub/AST-1046/AST-1073-contact-estelle-turn-loop` tip `641f35e0caab0d0ce153f0c788b86279abba9212`
**Baseline:** `origin/dev` three-dot
**Overall:** DISCUSS

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | conforms | no graded confidence path in turn loop |
| `astral.agent.do-task-delegation` | scoped | conforms | run_contact_estelle_turn → do_task(task_key) only |
| `astral.agent.grade-vector-validation` | scoped | conforms | no grade vectors on CHAT turn |
| `astral.batch.batch-id-first` | scoped | conforms | no batch claim/process work |
| `astral.batch.batch-id-format` | scoped | conforms | no batch_id invention |
| `astral.batch.claim-process-release` | scoped | conforms | no dispatcher claim/release |
| `astral.batch.entity-agent-responses-latest-only` | scoped | conforms | store_agent_data=True via existing do_task |
| `astral.config.config-source-of-truth` | scoped | conforms | trim limits + task_key in CONTACT_ESTELLE_CONFIG |
| `astral.config.pass-threshold-vs-score-floor` | scoped | conforms | no scoring floor changes |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | conforms | no new secrets/env reads |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | paths miss |
| `astral.debug.spikes-under-debug-dir` | scoped | conforms | feature plan docs only; no spike scripts |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | ast-1073 plan file; sibling 1072 separate |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty tip is tests/bible/uat only |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | tests via test()+merge-tests; no engineer test edits |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | core orchestrates; Slack via Contact helpers |
| `astral.layers.import-direction` | scoped | conforms | late agent import in contact; no UI inversion |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | layers miss (scripts) |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | config extensions only; no React |
| `astral.patterns.coat-check-never-store-empty` | scoped | conforms | no coat-check work |
| `astral.patterns.render-verdict-orchestrates-consult` | scoped | conforms | no consult/render-verdict work |
| `astral.patterns.require-auth-on-protected-endpoints` | scoped | not-applicable | layers miss (ui) |
| `astral.standards.data-raises-caller-logs` | scoped | conforms | no data-layer Python; admin JSON seed only |
| `astral.standards.database-header-inventory` | scoped | not-applicable | layers miss (data) |
| `astral.standards.debug-contract-gated` | scoped | conforms | Style D gated on debug=True; lengths/counts |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | reuses context/skill/post/envelope helpers |
| `astral.standards.in-scope-only` | scoped | conforms | turn loop only; no Events/Manage/resolve rewrite |
| `astral.standards.logging-via-utils` | scoped | conforms | get_logger; concern via warning; no print |
| `astral.standards.no-cross-contamination` | scoped | conforms | product footprint core/utils + admin seed |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | trim + skills ACL from config |
| `astral.standards.public-then-helpers` | scoped | conforms | public run_contact_estelle_turn above handler |
| `astral.standards.utils-data-late-import-only` | scoped | conforms | no new utils→data import |
| `astral.state.core-decides-transitions` | scoped | conforms | no candidate state transitions |
| `astral.state.job-prior-states-enforced` | scoped | conforms | no job prior-state work |
| `astral.state.no-daisy-chain-in-run` | scoped | conforms | one turn per accepted event; no run_next |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | layers miss (ui) |
| `astral.ui.naming-conventions` | scoped | not-applicable | layers miss (ui) |
| `astral.ui.single-gunicorn-worker` | scoped | conforms | config.py touched; no worker/RAILWAY change |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | merge-tests(AST-1073) brings single tip 870c0690 |
| `orch.git.commit-vocabulary` | universal | conforms | code/docs/test/merge-tests vocabulary on sub tip |
| `orch.git.flow-direction-inviolable` | universal | conforms | publish stays on origin/sub; no reverse onto dev |
| `orch.git.ftr-sub-topology` | universal | conforms | sub/AST-1046/AST-1073-… under parent ftr |
| `orch.git.merge-on-checkout` | universal | conforms | origin/dev ancestor of tip; graft documented |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | no cherry-pick/rebase/force on review tip |
| `orch.git.no-dev-agent-branches` | universal | conforms | uses sub/AST-1046/AST-1073-contact-estelle-turn-loop |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | review on astral-AST-1046 epic worktree |
| `orch.git.three-permanent-branches` | universal | conforms | no new permanent branch invented |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | no new product fork; plan Decisions held |
| `orch.pipeline.plan-is-bible` | universal | conforms | stages match tip: config, turn+hook, prompts |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Astral Contact child scope only |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Tests Passed → review-child |
| `orch.roles.archie-approves-statutes` | universal | conforms | no canon/statutes edits |
| `orch.roles.betty-owns-test-tree` | universal | conforms | test() + bible via Betty tip; engineer merge-tests only |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | assignee remains Hedy |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Hedy assignee through Tests Passed |
| `orch.roles.pre-commit-path-bans` | universal | conforms | no banned path additions in product commits |

## Pattern conformance

- `pattern.core.contact-agent` (proposed) — conforms (`run_contact_estelle_turn` + `handle_slack_event` hook)
- `pattern.config.config-block` — conforms (`CONTACT_ESTELLE_CONFIG` turn keys + optional `skill_calls` schema)
- Active `astral.patterns.*` — covered in Statutes checked

## Plan adherence

Stages 1–3 match the tip. Consumes AST-1072 envelope (`conversational_turn_from_do_task_result` / CHAT performance) and AST-1043 Contact helpers without re-owning Events/Manage Slack/resolve/cache/ACL registration. Self-Assessment Single-Component / high / Medium matches footprint. Sibling AST-1072 `agent.py` / envelope config present on tip by plan prerequisite (graft) — not 1073 scope creep.

## Findings

**discuss (C4 straggler):** `astral.debug.spikes-under-debug-dir` — Joan excluded; code sweep in-scope via `docs/features/**`. Merits: conforms (plan docs, not spikes). No product action.

**discuss (C4 straggler):** `astral.docs.features-single-file-per-ticket` — Joan excluded; feature docs in diff. Merits: conforms (one file per ticket). No product action.

**discuss (C4 straggler):** `astral.git.engineer-test-tree-ban` — Joan excluded; `tests/**` + bible on tip via Betty `test()` + engineer `merge-tests`. Merits: conforms. No product action.

**advisory:** `data/admin/agent_task.json` also normalizes unicode escapes across unrelated task rows (merge noise); `contact_estelle_turn` row matches Stage 3.

## What's solid

Listen re-check, ACL `run_contact_skill`, `format_contact_reply_text` + `contact_post_message`, no Slack post on failure/empty reply, concern aside via `logger.warning` only, Style D lengths/counts when `debug=True`, late `agent` import with cycle comment.

## Notes

Joan plan-rubric verdict attached (APPROVED). Stragglers above are C4 belt-and-suspenders only.

context_tokens≈72000

#### betty — 2026-07-30T23:55:58.333Z
## QA test manifest — AST-1073

**Publish:** `origin/sub/AST-1046/AST-1073-contact-estelle-turn-loop` @ `17a94c64` (`merge-tests(AST-1073): origin/tests 870c06900da5bb384458548e3871d85edb2a534d`)

### 1. Existing coverage (bible-backed)

- AST-1072 envelope / Medium brain / CHAT registration — still required; turn loop consumes it.
- AST-1069 / AST-1068 / AST-1070 accept-path Contact tests — revised to stub Estelle turn (below).

### 2. Broken / obsolete

1. Accept-path `handle_slack_event` tests (AST-1069 / AST-1068 / AST-1070 / HTTP schedule) — now call `run_contact_estelle_turn`; stubbed via `_stub_estelle_turn` so ingress stays transport-focused.
2. `TestAst786AgentTaskRepoJsonSeed` — catalog **43 → 46** (fixture byte-lock); tip includes `contact_estelle_turn` + preamble + topic_menu rows.
3. `TestAst1072ContactEstelleTurnCatalogRow` — prompts now require `skill_calls` + live_content/Slack language.

### 3. Gaps (new this pass)

1. `tests/component/utils/test_config.py::TestAst1073ContactEstelleTurnConfig` — turn trim keys + optional `skill_calls` schema.
2. `tests/component/core/test_contact.py::TestAst1073ContactEstelleTurnLoop` — listen_off; success post + thread_ts; concern aside log (not Slack); failure no-post; skill_calls ACL / no_candidate; Style D; `handle_slack_event` attaches `estelle_turn`.

**Integration:** no existing scenario asserts Estelle turn loop — no revision.

### Run

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1073ContactEstelleTurnConfig \
  tests/component/core/test_contact.py::TestAst1073ContactEstelleTurnLoop \
  tests/component/core/test_contact.py::TestAst1069ContactSlackIngress \
  tests/component/core/test_contact.py::TestAst1068ResolveSlackUser::test_handle_accept_wires_resolve \
  tests/component/core/test_contact.py::TestAst1070ContactConversationContext::test_dm_cache_key_ignores_message_ts \
  tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed \
  tests/component/core/test_repo_admin_json.py::TestAst1072ContactEstelleTurnCatalogRow \
  -q
```

### Bible shasums on publish-ref

- `docs/test-bible/utils/config.md` `a1de3faed2e8601182abb8c83af6b6bcd94ec3bf`
- `docs/test-bible/core/contact.md` `15cb5d8d186e848598159247c3d43ce5d8773469`
- `docs/test-bible/core/repo_admin_json.md` `99506affdb5fc8ee7dd32a34cc398dc0eef09dad`

— Betty

#### joan — 2026-07-30T23:46:20.989Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1073
**Overall:** APPROVED

**Notes:** Files Changed layer cell `data/admin seed` unrecognized by matching enum → treated as `docs`.

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 multi-turn Slack via AST-1043 Contact | Stage 2 hook + context history + reply/cache; Stage 3 prompts |
| AC2 structured envelope success\|failure\|concern | Stage 2 consumes AST-1072 via `do_task` + `conversational_turn_from_do_task_result` |
| AC3 concern → admin-visible aside | Stage 2.g `logger.warning` aside (not Slack); envelope aside from AST-1072 |
| AC4 default brain medium / non-thinking | N/A — boundary (AST-1072); plan does not touch brain override |
| AC5 Debug=True index + `\|` detail | Stage 2.h Style D on turn outcomes |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 config trim + skill_calls schema | Functional scope wire ACL skills; config SoT; pattern.config.config-block |
| Stage 2 run_contact_estelle_turn + handle_slack_event | Purpose turn loop; AC1–AC3/AC5; do-task-delegation; listen gate + non-prod prefix |
| Stage 3 agent_task prompt enrich | Functional scope Slack context + ACL skill_calls; keeps envelope rules |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work |
| orch.git.commit-vocabulary | conforms | Sub publish + per-stage commits |
| orch.git.flow-direction-inviolable | conforms | Publish to origin/sub only |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | Prerequisite graft from 1072/ftr documented; no reverse flow |
| orch.git.no-cherry-pick-rebase-force | conforms | None proposed |
| orch.git.no-dev-agent-branches | conforms | Uses sub/AST-1046/AST-1073-… |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree astral-AST-1046 |
| orch.git.three-permanent-branches | conforms | No permanent-branch invention |
| orch.pipeline.call-susan-for-product-decisions | conforms | Explicit Decisions; block→parent on drift |
| orch.pipeline.plan-is-bible | conforms | Binding stages + Files Changed |
| orch.pipeline.project-scoped-queues | conforms | Single-child Contact scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate-plan only |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | No tests/ edits |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Hedy) owns build |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer path after Plan Approved |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | No graded confidence path |
| astral.agent.do-task-delegation | conforms | Turn calls do_task(task_key) only; no Anthropic assembly |
| astral.agent.grade-vector-validation | conforms | No grade vectors |
| astral.batch.batch-id-first | conforms | No batch claim work |
| astral.batch.batch-id-format | conforms | No batch_id invention |
| astral.batch.claim-process-release | conforms | No dispatcher batch |
| astral.batch.entity-agent-responses-latest-only | conforms | store_agent_data=True via existing do_task |
| astral.config.config-source-of-truth | conforms | Trim limits + task_key in CONTACT_ESTELLE_CONFIG; skills from CONTACT_CONFIG |
| astral.config.pass-threshold-vs-score-floor | conforms | No scoring floor changes |
| astral.config.secrets-and-env-specific-from-environ | conforms | No new secrets/env |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src/features |
| astral.layers.core-vs-external-bright-line | conforms | Core orchestrates; Slack I/O via existing Contact helpers |
| astral.layers.import-direction | conforms | Late import agent from contact; no UI/external inversion |
| astral.layers.ui-config-driven-business-logic | conforms | Config extensions only; no React |
| astral.patterns.coat-check-never-store-empty | conforms | No coat-check work |
| astral.patterns.render-verdict-orchestrates-consult | conforms | No consult work |
| astral.standards.data-raises-caller-logs | conforms | No data-layer Python; seed JSON only |
| astral.standards.debug-contract-gated | conforms | Style D only when debug=True; lengths/counts |
| astral.standards.dry-and-focused-functions | conforms | Reuses context/skill/post/envelope helpers |
| astral.standards.in-scope-only | conforms | Consumes 1043/1072; no Events/Manage/resolve rewrite |
| astral.standards.logging-via-utils | conforms | Concern aside via logger; no print |
| astral.standards.no-cross-contamination | conforms | Stays utils/core + admin seed |
| astral.standards.no-hardcoded-sets | conforms | Trim limits + skill ACL from config |
| astral.standards.public-then-helpers | conforms | Public run_contact_estelle_turn placement specified |
| astral.standards.utils-data-late-import-only | conforms | No new utils→data import |
| astral.state.core-decides-transitions | conforms | No candidate state transitions |
| astral.state.job-prior-states-enforced | conforms | No job state work |
| astral.state.no-daisy-chain-in-run | conforms | One turn per event; no run_next chain |
| astral.ui.single-gunicorn-worker | conforms | Touches config.py but not worker/RAILWAY |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths match none of plan paths
- astral.debug.spikes-under-debug-dir — paths match none of plan paths
- astral.docs.features-single-file-per-ticket — paths match none of plan paths
- astral.git.engineer-test-tree-ban — paths match none of plan paths
- astral.layers.scripts-exempt-from-layer-rules — layers ∩ plan empty
- astral.patterns.require-auth-on-protected-endpoints — layers ∩ plan empty
- astral.standards.database-header-inventory — layers ∩ plan empty
- astral.ui.frontend-file-placement — layers ∩ plan empty
- astral.ui.naming-conventions — layers ∩ plan empty

## Findings

None fix-now.

**discuss (non-blocking):** Concern “admin-visible” surface here is `logger.warning` (+ AST-1072 agent_data). No operator UI in scope — acceptable vs Boundaries; richer admin surfacing would be a follow-up.

**acceptable:** Self-assessment Single-Component / high / Medium matches; listen re-check, ACL allowlists, no-post on failure are specific mitigations. Optional `skill_calls` on CHAT payload correctly claimed as turn-loop (not envelope) scope.

**R6:** Definition fidelity pass for child #2. Layers/import pass. Config SoT for trim limits. Debug gated. DRY reuse of AST-1043 helpers. No Events/Manage Slack/envelope redesign creep.

context_tokens≈55000

— Joan

#### hedy — 2026-07-30T16:50:27.581Z
Plan: [`docs/features/contact/ast-1073-contact-estelle-turn-loop.md`](https://github.com/susansomerset/astral/blob/sub/AST-1046/AST-1073-contact-estelle-turn-loop/docs/features/contact/ast-1073-contact-estelle-turn-loop.md) on `origin/sub/AST-1046/AST-1073-contact-estelle-turn-loop` @ `9bb5cead`.

**Scope:** Single-Component — Contact turn orchestration + config/schema/prompt; consumes AST-1072 envelope + AST-1043 helpers.
**Conf:** high — listen/resolve/context/ACL/post and `conversational_turn_from_do_task_result` already shipped; daemon-thread handler hosts the turn.
**Risk:** Medium — wrong Slack text or ACL writes possible; mitigated by listen re-check, `run_contact_skill` allowlists, no-post on failure.

— Hedy

#### chuckles — 2026-07-30T16:46:19.259Z
[thread-missing] Cursor chat `ad8b54d5-afe8-4be2-bc6a-ac631ff5cbca` has no local `store.db` on this host. Minted Hedy engineer Team thread `afd2a1f0-a51a-4617-b76c-f88b76e63c22` and persisted on parent AST-1046 ## Team.

— Chuckles

---

# AST-1073 — Contact Estelle turn loop over AST-1043 Contact

**Linear:** [AST-1073](https://linear.app/astralcareermatch/issue/AST-1073/contact-estelle-turn-loop-over-ast-1043-contact-contact-estelle)  
**Parent:** [AST-1046](https://linear.app/astralcareermatch/issue/AST-1046/contact-estelle-conversational-envelope)  
**Publish ref:** `sub/AST-1046/AST-1073-contact-estelle-turn-loop`

Wire **AST-1043** Contact plumbing (listen gate, Slack resolve, conversation context, ACL skills, non-prod reply prefix) into a multi-turn Estelle loop that consumes the **AST-1072** conversational envelope via `do_task("contact_estelle_turn")`. Each accepted inbound DM / `@` mention becomes one turn: load context → `do_task` → structured outcome → optional ACL skill writes → Slack reply (prefix when non-prod). Does **not** redefine the envelope schema (sibling AST-1072). Does **not** re-implement Events ingress, Manage Slack UI, resolve-util internals, context cache, or skill ACL registration (AST-1043 children).

**Branch prerequisite (already applied on this sub):** `origin/ftr/AST-1046-…` held AST-1072 without full `CONTACT_CONFIG`; `origin/dev` held Contact without the CHAT envelope. Before Stages below, the sub tip must expose both `CONTACT_CONFIG` (listen / skills / context keys) **and** `CONTACT_ESTELLE_CONFIG` / `is_conversational_task` / `conversational_turn_from_do_task_result`. If a fresh checkout loses the envelope, restore from `origin/sub/AST-1046/AST-1072-conversational-agent-envelope` (or re-graft as in commit `merge(AST-1073): restore AST-1072 envelope…`) — do not re-implement AST-1072.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Extend `CONTACT_ESTELLE_CONFIG` with turn-loop keys; extend `TASK_CONFIG["contact_estelle_turn"]["response_schema"]` with optional `skill_calls` | utils |
| `src/core/contact.py` | Add `run_contact_estelle_turn`; invoke it from `handle_slack_event` after accept + resolve + inbound append; Style D on turn outcomes | core |
| `data/admin/agent_task.json` | Enrich `contact_estelle_turn` prompts: Slack context + ACL skill_calls contract (still Estelle / envelope rules from AST-1072) | data/admin seed |

**Out of plan:** `src/external/slack.py`, Manage Slack UI, `api_slack.py` transport, changing global Estelle `brain_setting`, mutating `BASE_SCHEMA`, new DB transcript tables, astral-faq / activity-summary.

## Stage 1: Config — turn-loop keys + optional `skill_calls` schema

**Done when:** `CONTACT_ESTELLE_CONFIG` exposes the turn-loop keys below; `TASK_CONFIG["contact_estelle_turn"]["response_schema"]` allows optional `skill_calls`; import asserts pass; non-CHAT tasks unchanged.

1. In `src/utils/config.py`, extend the existing `CONTACT_ESTELLE_CONFIG` block (do **not** remove `default_brain_setting` / `task_key` / the `BRAIN_MEDIUM` assert) with:

```python
CONTACT_ESTELLE_CONFIG = {
    "default_brain_setting": "Medium",  # existing; keep assert == BRAIN_MEDIUM
    "task_key": "contact_estelle_turn",
    # Max Slack messages included in live_content (trim from oldest).
    "turn_context_message_limit": 40,
    # Max chars per message text in live_content (truncate with …).
    "turn_context_text_max_chars": 500,
}
```

2. Asserts (next to the existing Medium assert):

```python
assert isinstance(CONTACT_ESTELLE_CONFIG["turn_context_message_limit"], int)
assert CONTACT_ESTELLE_CONFIG["turn_context_message_limit"] > 0
assert isinstance(CONTACT_ESTELLE_CONFIG["turn_context_text_max_chars"], int)
assert CONTACT_ESTELLE_CONFIG["turn_context_text_max_chars"] > 0
```

3. Extend `TASK_CONFIG["contact_estelle_turn"]["response_schema"]` from reply-only to:

```python
"response_schema": {
    "reply": {"type": "str", "required": True},
    "skill_calls": {
        "type": "list",
        "required": False,
        "items_schema": {
            "skill_key": {"type": "str", "required": True},
            "fields": {"type": "object", "required": True},
        },
    },
},
```

⚠️ **Decision — optional `skill_calls` on the CHAT payload (this ticket):** AST-1072 owns envelope performance (`success` \| `failure` \| `concern` + `admin_aside`). ACL invocation is turn-loop scope: the agent may request zero or more allowlisted Contact skills in the same turn. Contact executes them via `run_contact_skill` after a successful envelope parse — never by inventing writes outside `CONTACT_CONFIG["skills"]`.

⚠️ **Decision — trim limits in config, not literals in core:** Context assembly caps live in `CONTACT_ESTELLE_CONFIG` so operators can tune without editing `contact.py`.

## Stage 2: Core — `run_contact_estelle_turn` + hook from `handle_slack_event`

**Done when:** An accepted inbound event (listen on, resolved user when present) runs one Estelle turn: context load → `do_task(contact_estelle_turn)` → `conversational_turn_from_do_task_result` → ACL skill_calls → Slack reply with non-prod prefix + cache append; `debug=True` emits Style D for the turn; listen-off / reject paths still never call `do_task`.

1. In `src/core/contact.py` module docstring, replace the “Estelle turn loop: AST-1046 — not here” line with: turn loop owned here (AST-1073); envelope contract AST-1072.

2. Add imports (lazy `do_task` inside the turn function is OK to avoid import cycles — prefer late import of `do_task` / `conversational_turn_from_do_task_result` from `src.core.agent` inside `run_contact_estelle_turn`, matching other core→agent call sites).

3. Add public helper **above** `handle_slack_event` (public-then-helpers: place with other public Contact APIs):

```python
def run_contact_estelle_turn(
    *,
    channel: str,
    text: str,
    thread_ts: Optional[str] = None,
    message_ts: Optional[str] = None,
    astral_candidate_id: Optional[str] = None,
    candidate_state: Optional[str] = None,
    debug: bool = False,
) -> dict:
    """One Contact Estelle conversational turn (AST-1073).

    Returns a dict with at least:
      ok, outcome, reply, admin_aside, skill_results, slack_post, error
    """
```

4. Behavior (literal order):

   a. **Listen re-check:** If not `slack_listen_enabled()`, return `{"ok": False, "error": "listen_off", ...}` without `do_task` / Slack post. (Defense in depth — `handle_slack_event` already gates.)

   b. **Context:** `ctx = load_slack_conversation_context(channel=channel, thread_ts=thread_ts, debug=debug)`. Build `live_content` as a single string:

      - Header lines: `channel=…`, `thread_ts=…`, `astral_candidate_id=…`, `candidate_state=…`.
      - Section `## Available Contact skills (ACL)` — for each `contact_skills()` entry: `skill_key`, `description`, comma-joined `allowed_paths`. Instruct: only emit `skill_calls` entries whose `skill_key` is listed; `fields` keys must be allowlisted paths; omit `skill_calls` when none.
      - Section `## Conversation` — take the last `CONTACT_ESTELLE_CONFIG["turn_context_message_limit"]` messages from `ctx["messages"]`; each line `[{user or bot_id or "unknown"}] {truncated text}` using `turn_context_text_max_chars`.
      - Section `## Latest inbound` — the current `text` (truncated the same way).

   c. **Candidate raft for tokens:** If `astral_candidate_id` is a non-empty string, `row = get_candidate(astral_candidate_id)` (already imported); build `candidate_data` from `row["candidate_data"]` if present else `{}`. Else `candidate_data = {}`.

   d. **`do_task`:** `import asyncio` at module top if not present. Call:

```python
task_key = CONTACT_ESTELLE_CONFIG["task_key"]
result = asyncio.run(
    do_task(
        task_key,
        live_content=live_content,
        index=astral_candidate_id or channel,
        candidate_data=candidate_data,
        debug=debug,
        store_agent_data=True,
    )
)
turn = conversational_turn_from_do_task_result(result)
```

   e. **Skill calls:** From `result["parsed_response"]` (dict), read optional `skill_calls` (default `[]`). If not a list, treat as `[]`. For each item that is a dict with `skill_key` + `fields` dict: if `astral_candidate_id` is missing/blank, append `{"ok": False, "error": "no_candidate", "skill_key": …}` and continue; else call `run_contact_skill(skill_key, astral_candidate_id=…, fields=fields, debug=debug)` inside try/except — on `ValueError` / other Exception, append `{"ok": False, "error": str(exc), "skill_key": …}` without raising out of the turn. Collect `skill_results`.

   f. **Outbound reply:** Let `reply = turn["reply"]`. Post to Slack only when `turn["success"]` is True **and** `reply` is a non-empty stripped string **and** outcome is `success` or `concern`. Build `reply_thread_ts = thread_ts or message_ts` (nest channel `@` replies under the triggering message when Slack omitted `thread_ts`). Then:

```python
outbound = format_contact_reply_text(reply)
slack_post = contact_post_message(
    channel=channel,
    text=outbound,
    thread_ts=reply_thread_ts,
    debug=debug,
)
```

   Do **not** call `post_contact_reply` here (it posts without cache append). Do **not** put `admin_aside` into the Slack text.

   g. **Admin aside:** When `turn["outcome"] == "concern"` and `admin_aside` is a non-empty string, emit `logger.warning("contact estelle concern aside candidate=%s aside=%s", astral_candidate_id, aside_preview)` with aside truncated to `_TEXT_DEBUG_MAX` — admin-visible via logs, not Slack.

   h. **Debug (only `debug=True`):** After the turn settles, Style D:

      - `debug_index(func="contact.run_contact_estelle_turn", index=1, total=1, identifier=<event channel or candidate id>, outcome=<turn outcome or error>)`
      - `debug_detail` with `outcome=… success=… reply_len=… admin_aside_len=… skill_calls=N skill_ok=M slack_ok=…` (lengths / counts only — no full reply/aside blobs unless passed through `truncate_debug_content`).

   i. **Return** a dict:

```python
{
    "ok": bool(turn["success"]) and error is None,
    "outcome": turn["outcome"],
    "reply": turn["reply"],
    "admin_aside": turn["admin_aside"],
    "skill_results": skill_results,
    "slack_post": slack_post,  # or None if skipped
    "error": result.get("error") if not result.get("success") else None,
}
```

5. Hook into `handle_slack_event` **after** resolve + inbound `append_slack_conversation_message` and **before** the final accept debug block: when `result["accepted"]` is True and `channel` is a non-empty str, call:

```python
turn_out = run_contact_estelle_turn(
    channel=channel,
    text=text,
    thread_ts=event.get("thread_ts"),
    message_ts=msg_ts if isinstance(msg_ts, str) else None,
    astral_candidate_id=result.get("astral_candidate_id"),
    candidate_state=result.get("candidate_state"),
    debug=debug,
)
result["estelle_turn"] = turn_out
```

   Wrap in try/except so a turn failure still returns the accepted ingress result (log exception at ERROR; set `result["estelle_turn"] = {"ok": False, "error": str(exc)}`). Never raise out of the daemon thread uncaught in a way that skips the accept return.

⚠️ **Decision — sync `asyncio.run` on the daemon thread:** `receive_slack_events_http` already acks then runs `handle_slack_event` on a daemon thread (AST-1069). Running `do_task` via `asyncio.run` on that thread keeps the Flask request fast and matches other sync Contact/UI wrappers (`api_intake`, `candidate` paths). Do **not** move ack onto the turn or call `do_task` on the request thread.

⚠️ **Decision — compose `format_contact_reply_text` + `contact_post_message`:** Prefix (AST-1067) + cache append (AST-1070) without double-prefixing. Do not invent a third poster.

⚠️ **Decision — failure / empty reply = no Slack message:** Envelope `failure` or missing reply must not spam Slack; operators still see debug / ERROR logs.

## Stage 3: Prompt seed — context + ACL skill_calls

**Done when:** `data/admin/agent_task.json` row `task_key=contact_estelle_turn` instructs Estelle to use conversation + latest inbound from live_content, emit ternary envelope + optional `skill_calls`, and keep admin asides out of `reply`.

1. Update the existing `contact_estelle_turn` row (do **not** change `agent_id=principal_recruiter_estelle` or mint a new `task_key_uuid`):

   - **system_prompt** (keep AST-1072 envelope rules) and add:
     - User-visible text goes only in `agent_payload.reply`.
     - `admin_aside` only on `concern`, never copied into `reply`.
     - Optional `agent_payload.skill_calls`: list of `{skill_key, fields}` drawn **only** from the ACL section in live_content; `fields` values are strings (or omit nulls); empty / omitted when no save is needed.
     - Prefer one short Slack-appropriate `reply` (no markdown fences around the JSON envelope).

   - **user_prompt** / nocache as needed so live_content (passed as the TASK / live block by `do_task`) is clearly “this turn’s Slack context.” Keep `{$SELECTED_AGENT}` if already present.

2. Do **not** add new TASK_CONFIG keys. Do **not** register Contact skills in `TASK_CONFIG`.

## Self-Assessment

**Scope:** `Single-Component` — Contact core turn orchestration + small config/schema/prompt extensions; consumes AST-1072 `do_task` contract and AST-1043 Contact helpers; no new external/UI modules.

**Conf:** `high` — listen/resolve/context/ACL/post helpers already exist; envelope helper `conversational_turn_from_do_task_result` is shipped; daemon-thread ack pattern already hosts the handler.

**Risk:** `Medium` — a bad turn could post wrong Slack text or write candidate fields via skills; mitigated by listen re-check, ACL path allowlists in `run_contact_skill`, no-post on failure, and debug-gated tracing. Brain override remains AST-1072’s Medium path (not touched here).

## Code rules self-check

- **§1.3 DRY:** Reuse `load_slack_conversation_context`, `run_contact_skill`, `format_contact_reply_text`, `contact_post_message`, `conversational_turn_from_do_task_result` — no second resolver/poster/envelope parser.
- **§2.1 config:** Turn trim limits + task_key from `CONTACT_ESTELLE_CONFIG`; skills ACL remains `CONTACT_CONFIG["skills"]`; no new hardcoded skill key sets in core.
- **§2.4 / §2.6:** No new dispatch batch or candidate state machine transitions in this ticket.
- **§3.3 imports:** UI unchanged (still core-only). Contact may late-import `agent.do_task`; Contact must not import UI. External Slack only via existing Contact helpers.
- **§1.5.1 debug:** New Style D lines only when `debug=True`; lengths/counts in detail lines.
- **§1.1 in-scope:** No Events verify rewrite, no Manage Slack page, no envelope performance schema redesign, no transcript table.

## Execution contract

The plan is binding. Execute stages in order. One commit per stage on the epic worktree, then `git push origin HEAD:sub/AST-1046/AST-1073-contact-estelle-turn-loop`. On ambiguity or codebase drift vs this plan — stop and comment on **parent AST-1046** with the 🛑 Stage N blocked template. Do not invent files outside the Files Changed table.

## Review

| Field | Value |
|-------|-------|
| Status | Review Posted |
| Publish ref | `origin/sub/AST-1046/AST-1073-contact-estelle-turn-loop` |
| Tip | `17a94c645659e9762f874c72dee086f1e3c11fea` (pre-review; docs tip follows) |
| Branch | `sub/AST-1046/AST-1073-contact-estelle-turn-loop` |

### Radia — code-rubric.v1 (`[code-rubric] revision=1`)

**Overall:** DISCUSS (C4 stragglers only — no product fix-now)

**What's solid**
- Stage 1–3 match tip: `CONTACT_ESTELLE_CONFIG` trim keys + optional `skill_calls`; `run_contact_estelle_turn` + `handle_slack_event` hook; prompt seed with ACL/`skill_calls`.
- `do_task(CONTACT_ESTELLE_CONFIG["task_key"])` only; Slack via existing Contact helpers; Style D gated on `debug=True` with lengths/counts.
- Listen re-check, no-post on failure/empty reply, concern aside via `logger.warning` (not Slack), late `agent` import with cycle comment.

**Findings**
- **discuss (C4 straggler):** `astral.debug.spikes-under-debug-dir` — Joan excluded; diff touches `docs/features/**`. Merits: conforms (plan docs, not spikes). No product action.
- **discuss (C4 straggler):** `astral.docs.features-single-file-per-ticket` — Joan excluded; feature docs in diff. Merits: conforms (one file per ticket). No product action.
- **discuss (C4 straggler):** `astral.git.engineer-test-tree-ban` — Joan excluded; `tests/**` + bible in tip via Betty `test()` + engineer `merge-tests`. Merits: conforms. No product action.

**advisory:** `data/admin/agent_task.json` also normalizes unicode escapes across unrelated task rows (merge noise); `contact_estelle_turn` row itself matches Stage 3.

**Recommended:** Engineer may treat Overall DISCUSS as non-blocking for resolve unless they want a plan-rubric exclusion refresh; no code changes required for the stragglers.

## Resolution

**Date:** 2026-07-31  
**Engineer:** Hedy  
**Outcome:** clean — no product code changes

Radia `[code-rubric] revision=1` Overall **DISCUSS** with **zero fix-now**. C4 discuss stragglers (`spikes-under-debug-dir`, `features-single-file-per-ticket`, `engineer-test-tree-ban`) explicitly **no product action**. Advisory unicode-escape noise in `agent_task.json` left as merge artifact (Stage 3 `contact_estelle_turn` row already correct).

Publish tip at resolve: see commit after this section lands.
