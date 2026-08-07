<!-- linear-archive: AST-1074 archived 2026-08-07 -->

## Linear archive (AST-1074)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1074/topic-menu-model-and-persistence-topic-menu-generation  
**Status at archive:** Archive  
**Project:** Astral Candidate  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-953 — Topic Menu Generation  
**Blocked by / blocks / related:** parent: AST-953; blocks: AST-1075

### Description

## What this implements

Durable Topic Menu storage: topic name, ask, required flag, closed `informs` catalog (rubrics, base resume, strengths, priorities, deal breakers, backstory), and status triad `open` / `ready` / `retired` (revise without wipe). Does **not** own Estelle confirm/generation (sibling) or later satisfaction/state-hops work.

## Acceptance criteria

- [X] Given a confirmed preamble, Estelle produces a persisted Topic Menu (pure Estelle authorship) whose topics each have name, ask, required flag, status (`open` / `ready` / `retired`), and non-empty `informs` drawn only from rubrics, base resume, strengths, priorities, deal breakers, and/or backstory. *(persistence/model half — generation is sibling)*
- [X] Revising the menu keeps prior topic content and uses `open` / `ready` / `retired` rather than wiping the menu wholesale.

## Boundaries

Does **not** own Estelle preamble confirm or Topic Menu generation (sibling). Does **not** own later satisfaction conversation or REQUIRED/ALL_TOPICS_READY hops. Does **not** craft artifacts.

## In scope

- [X] `pattern.config.config-block` — `TOPIC_MENU_CONFIG` closed informs + statuses
- [X] Topic Menu + closed informs pattern (proposed) — `candidate_data.topic_menu` meta sibling + topic shape
- [X] Topic status triad pattern (proposed) — `open` / `ready` / `retired`; revise retires missing ids
- [X] `astral.config.config-source-of-truth` — informs/status literals live in config
- [X] `astral.standards.no-hardcoded-sets` — helpers read `TOPIC_MENU_CONFIG`, not inline enums
- [X] `astral.standards.debug-contract-gated` — Style D on `save_topic_menu` when `debug=True`
- [X] `astral.layers.import-direction` — core helpers via existing `save_candidate_data`; no UI in this ticket
- [X] `astral.docs.features-single-file-per-ticket` — plan at `docs/features/candidate/ast-1074-topic-menu-model-and-persistence.md`
- [X] `CANDIDATE_DATA_MODEL.md` update for `topic_menu`

## Considered but excluded

- [X] Estelle preamble confirm + Topic Menu generation agent tasks / prompts — AST-1075
- [X] Satisfaction conversation / progress UI / REQUIRED_TOPICS_READY / ALL_TOPICS_READY — follow-on epic
- [X] Per-rubric informs keys (`like_rubric`, …) — parent closed catalog uses umbrella `rubrics`
- [X] `GET /api/ui_config` exposure of `TOPIC_MENU_CONFIG` — no UI consumer yet; AST-1075 imports Python config
- [X] `astral.agent.do-task-delegation` — no agent_task in this child
- [X] Database schema migration — meta key under existing `candidate_data` JSON
- [X] `tests/` / `docs/test-bible/**` — Betty after Code Complete

## Notes for planning

Config-driven informs + status enums. Default save path is revise-by-id (retire dropped topics).

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-953-topic-menu-generation`, child `sub/AST-953/AST-1074-topic-menu-model-and-persistence`. Created at dispatch-parent.

### Comments

#### radia — 2026-07-30T16:35:11.791Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1074
**Publish ref:** `origin/sub/AST-953/AST-1074-topic-menu-model-and-persistence` @ `b4b0cfb3` (product tip was `9cb1928f`; docs review appended)
**Baseline:** `origin/dev` (three-dot)
**Overall:** DISCUSS

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | conforms | no graded agent_task / confidence fields |
| `astral.agent.do-task-delegation` | scoped | conforms | no do_task / agent_task — AST-1075 |
| `astral.agent.grade-vector-validation` | scoped | conforms | no grade vectors |
| `astral.batch.batch-id-first` | scoped | conforms | no batch claim/process |
| `astral.batch.batch-id-format` | scoped | conforms | no batch_id generation |
| `astral.batch.claim-process-release` | scoped | conforms | no batch locking |
| `astral.batch.entity-agent-responses-latest-only` | scoped | conforms | no agent_data RESPONSE writes |
| `astral.config.config-source-of-truth` | scoped | conforms | informs/statuses/fields live in TOPIC_MENU_CONFIG |
| `astral.config.pass-threshold-vs-score-floor` | scoped | conforms | no scoring / score_floor |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | conforms | no secrets/env introduced |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | paths miss tip (no artifacts/** / scripts/spikes/**) |
| `astral.debug.spikes-under-debug-dir` | scoped | conforms | amends production CANDIDATE_DATA_MODEL — not spike |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | one plan file + shared data-model amend |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty test SHA touches tests/bible only |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | engineer code/docs SHAs omit tests/bible; Betty owns tip tests |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | core helpers only; no external I/O |
| `astral.layers.import-direction` | scoped | conforms | core→utils/config + save_candidate_data; no UI |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | layers ∩ tip empty (no scripts/**) |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | catalog in config; no ui_config expose yet |
| `astral.patterns.coat-check-never-store-empty` | scoped | conforms | no coat-check keys |
| `astral.patterns.render-verdict-orchestrates-consult` | scoped | conforms | no consult/render_verdict |
| `astral.patterns.require-auth-on-protected-endpoints` | scoped | not-applicable | layers ∩ tip empty (no src/ui/**) |
| `astral.standards.data-raises-caller-logs` | scoped | conforms | missing candidate raises ValueError; no data logging invent |
| `astral.standards.database-header-inventory` | scoped | not-applicable | layers ∩ tip empty (no src/data/**) |
| `astral.standards.debug-contract-gated` | scoped | conforms | Style D on save_topic_menu only when debug=True |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | reuses get_candidate / save_candidate_data |
| `astral.standards.in-scope-only` | scoped | conforms | model/persistence only; 1075/satisfaction excluded |
| `astral.standards.logging-via-utils` | scoped | conforms | module logger + debug_index/detail |
| `astral.standards.no-cross-contamination` | scoped | conforms | utils/core/docs surfaces only |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | helpers read TOPIC_MENU_CONFIG for informs/statuses |
| `astral.standards.public-then-helpers` | scoped | conforms | public get/validate/revise/save + small key helper |
| `astral.standards.utils-data-late-import-only` | scoped | conforms | no new utils→data import |
| `astral.state.core-decides-transitions` | scoped | conforms | no candidate state transitions |
| `astral.state.job-prior-states-enforced` | scoped | conforms | no job state work |
| `astral.state.no-daisy-chain-in-run` | scoped | conforms | no dispatch run_next chains |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | layers ∩ tip empty (no frontend) |
| `astral.ui.naming-conventions` | scoped | not-applicable | layers ∩ tip empty (no src/ui/**) |
| `astral.ui.single-gunicorn-worker` | scoped | conforms | config touched but no gunicorn/worker change |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | single merge-tests(AST-1074) SHA on tip |
| `orch.git.commit-vocabulary` | universal | conforms | plan/code/docs/test/merge-tests vocabulary on child SHAs |
| `orch.git.flow-direction-inviolable` | universal | conforms | publish only on origin/sub/AST-953/AST-1074-… |
| `orch.git.ftr-sub-topology` | universal | conforms | sub under AST-953 parent |
| `orch.git.merge-on-checkout` | universal | conforms | no illegal merge recipe in product commits |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | none in tip history for this child |
| `orch.git.no-dev-agent-branches` | universal | conforms | sub/AST-953/AST-1074-… only |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | epic worktree astral-AST-953 |
| `orch.git.three-permanent-branches` | universal | conforms | no new permanent branches |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | no new product open questions in code |
| `orch.pipeline.plan-is-bible` | universal | conforms | stages match TOPIC_MENU_CONFIG + helpers + data-model |
| `orch.pipeline.project-scoped-queues` | universal | conforms | single-child review scope |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Tests Passed → review-child |
| `orch.roles.archie-approves-statutes` | universal | conforms | no statute corpus edits |
| `orch.roles.betty-owns-test-tree` | universal | conforms | test(AST-1074)+merge-tests on tip; engineer omitted tests |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | assignee remains Ada |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Ada still assignee at Tests Passed |
| `orch.roles.pre-commit-path-bans` | universal | conforms | no banned path edits by engineer |

## Pattern conformance

| cited | verdict |
|-------|---------|
| `pattern.config.config-block` | conforms — `TOPIC_MENU_CONFIG` |
| Topic Menu + closed informs (proposed) | conforms — meta sibling + closed catalog |
| Topic status triad (proposed) | conforms — open/ready/retired + revise retires missing ids |

## Plan adherence

Stages 1–3 match tip: config block + get/validate/revise/save + `CANDIDATE_DATA_MODEL.md`. No UI/Estelle/state-hop creep. Self-assessment Single-Component / high / Medium still fits. Style D debug on `save_topic_menu` present.

## Findings

**discuss (C4 straggler):** Joan Excluded `astral.git.engineer-test-tree-ban` (plan paths empty); tip three-dot now includes Betty `tests/**` + bible. Statute row still **conforms** (engineer SHAs clean). No product fix required.

**discuss (carry Joan):** `revise=False` can drop retired history if callers omit retired topics — AST-1075 must keep default `revise=True` or pass complete lists.

**advisory:** `TOPIC_MENU_CONFIG` placed after `PREAMBLE_VALIDATION_CONFIG` asserts (plan prose said after PREAMBLE); placement-only.

**fix-now:** none

### What’s solid

Config-driven informs/statuses, revise-by-id default, Style D gating, boundaries held.

### Notes

Joan plan-rubric verdict recovered from Linear comment (attachment URL not required). Active statutes enumerated: 56.

context_tokens≈52000

— Radia

#### betty — 2026-07-30T16:30:51.907Z
1. `tests/component/utils/test_config.py::TestAst1074TopicMenuConfig` — `TOPIC_MENU_CONFIG` closed informs + status triad + library homes
2. `tests/component/core/test_candidate.py::TestAst1074TopicMenuPersistence` — validate / revise (retire missing ids) / get / save (`revise` default + `revise=False`) / Style D debug gating

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1074TopicMenuConfig \
  tests/component/core/test_candidate.py::TestAst1074TopicMenuPersistence \
  -q
```

`origin/sub/AST-953/AST-1074-topic-menu-model-and-persistence` @ `9cb1928f` (`merge-tests(AST-1074): origin/tests f9d9b827`)

Bible shasums on publish-ref:
- `4d132b64c1f7205aa3398322d9452cfe21373ac555528b235ec429f723982fef` `docs/test-bible/core/candidate.md`
- `54bbfef484010cea1c2ddf9928eaa6778145683abfb9f364b76f402a76180008` `docs/test-bible/utils/config.md`

Broken / obsolete: none (additive). Integration: no existing scenario — no revision.

— Betty

#### joan — 2026-07-30T16:17:45.902Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1074
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 Estelle preamble confirm pass | N/A — boundary (AST-1075) |
| AC2 persisted Topic Menu with name/ask/required/status/informs | Stages 1–2 — `TOPIC_MENU_CONFIG` + validate/get/save/revise; generation authorship is AST-1075 |
| AC3 Estelle confirms informs coverage; reject topics without allowed informs | Stage 2 `validate_topic` enforces non-empty closed `informs`; Estelle coverage pass is AST-1075 |
| AC4 directed / few-minute topics | N/A — generation judgment (AST-1075); model does not encode length |
| AC5 revise keeps prior content via open/ready/retired | Stage 2 `revise_topic_menu` + default `revise=True` |
| AC6 no REQUIRED/ALL_TOPICS_READY / satisfaction loop required | N/A — boundary (explicitly out of Files Changed / stages) |
| AC7 backend debug=True found/recorded on touched paths | Stage 2 `save_topic_menu(..., debug=)` Style D; confirm/generation debug remains AST-1075 |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 TOPIC_MENU_CONFIG | Architectural `pattern.config.config-block`; closed informs + status triad; Purpose durable Topic Menu model |
| Stage 2 core helpers | Functional scope topic shape + lifecycle without wipe; child persistence ACs |
| Stage 3 CANDIDATE_DATA_MODEL.md | Document meta sibling `topic_menu`; informs declare intent only |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work in this plan |
| orch.git.commit-vocabulary | conforms | Publish on sub ref with plan/code vocabulary |
| orch.git.flow-direction-inviolable | conforms | Publish only to origin/sub/AST-953/AST-1074-… |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | No illegal merge recipe |
| orch.git.no-cherry-pick-rebase-force | conforms | None proposed |
| orch.git.no-dev-agent-branches | conforms | Uses sub/AST-953/AST-1074-… only |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree astral-AST-953 |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Open questions none; Decisions (umbrella rubrics, meta sibling, no ui_config) documented |
| orch.pipeline.plan-is-bible | conforms | Binding stages + Files Changed present |
| orch.pipeline.project-scoped-queues | conforms | Single-child scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate-plan gate |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | No tests/bible edits |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Ada) owns build |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer implementer path after approve |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | No graded agent_task in this child |
| astral.agent.do-task-delegation | conforms | No do_task / agent_task — AST-1075 |
| astral.agent.grade-vector-validation | conforms | No graded tasks |
| astral.batch.batch-id-first | conforms | No batch claim/process |
| astral.batch.batch-id-format | conforms | No batch_id generation |
| astral.batch.claim-process-release | conforms | No batch locking |
| astral.batch.entity-agent-responses-latest-only | conforms | No agent_data RESPONSE writes |
| astral.config.config-source-of-truth | conforms | Informs/statuses/field contract in TOPIC_MENU_CONFIG |
| astral.config.pass-threshold-vs-score-floor | conforms | No scoring / score_floor work |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env introduced |
| astral.debug.spikes-under-debug-dir | conforms | Amends production CANDIDATE_DATA_MODEL — not spike output |
| astral.docs.features-single-file-per-ticket | conforms | Ticket plan is one features file; shared data-model amend is appropriate |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src/features; Betty excluded |
| astral.layers.core-vs-external-bright-line | conforms | Core helpers only; no external I/O |
| astral.layers.import-direction | conforms | core → utils + existing save_candidate_data; no UI |
| astral.layers.ui-config-driven-business-logic | conforms | Catalog in config; intentionally no ui_config expose yet |
| astral.patterns.coat-check-never-store-empty | conforms | No coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | conforms | No consult/render_verdict |
| astral.standards.data-raises-caller-logs | conforms | Missing candidate raises ValueError; no data-layer logging invent |
| astral.standards.debug-contract-gated | conforms | Style D on save_topic_menu only when debug=True |
| astral.standards.dry-and-focused-functions | conforms | Reuses get_candidate / save_candidate_data; focused helpers |
| astral.standards.in-scope-only | conforms | Persistence/model only; 1075/satisfaction/state hops excluded |
| astral.standards.logging-via-utils | conforms | Uses module logger debug_index/detail pattern |
| astral.standards.no-cross-contamination | conforms | Stays in utils/core/docs surfaces named |
| astral.standards.no-hardcoded-sets | conforms | Helpers read TOPIC_MENU_CONFIG; asserts lock parent six informs |
| astral.standards.public-then-helpers | conforms | Public get/validate/revise/save with small private key helper |
| astral.standards.utils-data-late-import-only | conforms | No new utils→data import |
| astral.state.core-decides-transitions | conforms | Explicitly no candidate state transitions |
| astral.state.job-prior-states-enforced | conforms | No job state work |
| astral.state.no-daisy-chain-in-run | conforms | No dispatch run_next chains |
| astral.ui.single-gunicorn-worker | conforms | No gunicorn/worker changes |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.debug.spikes-under-debug-dir, astral.docs.features-single-file-per-ticket, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths match none of plan paths
- astral.git.engineer-test-tree-ban — paths match none of plan paths
- astral.layers.scripts-exempt-from-layer-rules — layers ∩ plan empty
- astral.patterns.require-auth-on-protected-endpoints — layers {ui} ∩ plan empty
- astral.standards.database-header-inventory — layers {data} ∩ plan empty
- astral.ui.frontend-file-placement — layers {ui} ∩ plan empty
- astral.ui.naming-conventions — layers {ui} ∩ plan empty

## Findings

None fix-now.

**discuss (non-blocking):** Stage 2 `revise=False` full-replace path can drop retired history if a caller omits them — default `revise=True` and “no wipe API” match parent AC5; AST-1075 must keep default revise (or pass complete lists including retired).

**acceptable:** Self-assessment Single-Component / high / Medium matches; Medium risk mitigation (default revise + retired retention + config asserts) is specific. Stage 1 `base_resume` cross-check is string-literal (no `artifacts_keys` in `CANDIDATE_LIBRARY_CONFIG`) — workable as written.

**R6 checklist:** Definition fidelity pass (model/persistence only). Layer/import pass. Config block + no-hardcoded-sets pass. File placement pass (utils/core/docs). No batch/state/UI/agent creep. DRY via existing save_candidate_data.

context_tokens≈48000

— Joan

#### ada — 2026-07-30T16:13:30.480Z
Plan published on `origin/sub/AST-953/AST-1074-topic-menu-model-and-persistence` @ `19caecf1`.

**Plan:** [docs/features/candidate/ast-1074-topic-menu-model-and-persistence.md](https://github.com/susansomerset/astral/blob/sub/AST-953/AST-1074-topic-menu-model-and-persistence/docs/features/candidate/ast-1074-topic-menu-model-and-persistence.md)

**Self-assessment**
- **Scope:** Single-Component — `TOPIC_MENU_CONFIG` + core get/validate/revise/save helpers + `CANDIDATE_DATA_MODEL.md`; no UI/agent tasks/schema migration.
- **Conf:** high — same meta-sibling + `save_candidate_data` / config-assert patterns as AST-1014 / PREAMBLE_CONFIG; revise-by-id algorithm is fully specified.
- **Risk:** Medium — bad revise semantics would lose topic history for AST-1075 regenerations; default `revise=True` + retired retention mitigate.

---

# AST-1074 — Topic Menu model and persistence

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1074/topic-menu-model-and-persistence-topic-menu-generation  
**Parent:** https://linear.app/astralcareermatch/issue/AST-953/topic-menu-generation  

**Publish ref (origin):** `sub/AST-953/AST-1074-topic-menu-model-and-persistence`  
**Parent integration ref:** `ftr/AST-953-topic-menu-generation`

Ship the durable **Topic Menu** model: config-driven closed `informs` catalog + status triad, a `candidate_data.topic_menu` meta sibling, and core validate / get / save / revise helpers that keep prior topic content (retire instead of wipe). Sibling **AST-1075** owns Estelle preamble confirm and menu generation; this ticket stops at persistence contracts those callers will use.

Boundaries (do **not** implement): Estelle confirm/generation agent tasks or prompts (AST-1075); satisfaction conversation / progress UI; REQUIRED_TOPICS_READY / ALL_TOPICS_READY hops; artifact crafting; candidate state-machine vocabulary changes; mechanical preamble (AST-952 family already on `dev`).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `TOPIC_MENU_CONFIG` (informs catalog, statuses, topic field contract); module asserts | utils |
| `src/core/candidate.py` | Topic Menu get / validate / save / revise helpers + `debug=` found/recorded lines | core |
| `docs/features/candidate/CANDIDATE_DATA_MODEL.md` | Document `topic_menu` meta sibling + topic shape | docs |

No UI pages, no `TASK_CONFIG` / agent_task rows, no database schema migration (meta key under existing `candidate_data` JSON), no `tests/` / bible edits (Betty after Code Complete).

---

## Stage 1: `TOPIC_MENU_CONFIG` contract

**Done when:** `TOPIC_MENU_CONFIG` is importable from `src.utils.config` with a closed `informs` tuple, a closed `statuses` tuple, and topic field/name literals; module-level asserts fail loudly if the catalog drifts from parent AC vocabulary.

1. In `src/utils/config.py`, immediately **after** `PREAMBLE_CONFIG` asserts (before the next unrelated candidate config block), add:

```python
# AST-1074: Topic Menu closed informs + status triad (generation = AST-1075).
TOPIC_MENU_CONFIG = {
    # Parent AC closed vocabulary — Estelle may not invent new target kinds.
    "informs": (
        "rubrics",
        "base_resume",
        "strengths",
        "priorities",
        "deal_breakers",
        "backstory",
    ),
    "statuses": ("open", "ready", "retired"),
    "default_status": "open",
    # Stable key under candidate_data (meta sibling of contact/context/artifacts).
    "candidate_data_key": "topic_menu",
    "topic_required_fields": ("id", "name", "ask", "required", "informs", "status"),
}
```

2. Immediately after the block, add asserts:

   - `informs` is a non-empty `tuple` of unique non-empty `str`; equals exactly the six parent targets above (order as written).
   - `statuses` is a `tuple` equal to `("open", "ready", "retired")`.
   - `default_status` is in `statuses`.
   - `candidate_data_key == "topic_menu"`.
   - `topic_required_fields` is a non-empty `tuple` of unique non-empty `str` and includes at least `id`, `name`, `ask`, `required`, `informs`, `status`.
   - Cross-check library homes (documentation contract, not path writes): `strengths` / `priorities` / `deal_breakers` / `backstory` are members of `CANDIDATE_LIBRARY_CONFIG["context_keys"]`; `base_resume` is an artifacts key name (string literal match only — do not invent a new library key).

⚠️ **Decision:** Use umbrella `rubrics` (parent AC wording) rather than per-rubric keys (`like_rubric`, `do_rubric`, …). Parent closed catalog is six targets; per-artifact rubric mapping is later satisfaction / craft work, not this model.

⚠️ **Decision:** Store the menu as meta sibling `candidate_data.topic_menu` (same class as `lifecycle` / `intakes_old` / `pending_craft_generations`), **not** inside `context` or `artifacts`. Topics are intake orchestration state; library blobs stay prose/artifact content only (AST-1014).

⚠️ **Decision:** Do **not** expose `TOPIC_MENU_CONFIG` on `GET /api/ui_config` in this ticket — no UI consumer yet; AST-1075 imports config in Python. If a later UI ticket needs the catalog, add ui_config there.

3. If `config.py`’s top-of-file comment inventory lists named `*_CONFIG` blocks, add a one-line entry for `TOPIC_MENU_CONFIG` next to `PREAMBLE_CONFIG`.

---

## Stage 2: Core Topic Menu helpers (validate / get / revise / save)

**Done when:** `src/core/candidate.py` exposes public helpers that load/store `candidate_data.topic_menu`, validate topics against `TOPIC_MENU_CONFIG`, and revise without wiping prior topics (missing ids → `retired`); `debug=True` emits Style D found/recorded lines on save/revise paths; no Estelle / agent_task calls.

1. Near other library helpers in `src/core/candidate.py`, import `TOPIC_MENU_CONFIG` from `src.utils.config`.

2. Add `_topic_menu_key() -> str` returning `str(TOPIC_MENU_CONFIG["candidate_data_key"])`.

3. Add `empty_topic_menu() -> dict` returning:

```python
{"topics": []}
```

No other top-level keys in this ticket (generation timestamps / preamble-confirm markers belong to AST-1075 if needed).

4. Add `normalize_topic_menu(raw: Any) -> dict`:

   - If `raw` is not a `dict`, return `empty_topic_menu()`.
   - Read `topics = raw.get("topics")`; if not a `list`, treat as `[]`.
   - Return `{"topics": list(topics)}` (shallow copy of the list only — callers validate members separately).

5. Add `get_topic_menu(candidate_id: str) -> dict`:

   - Load candidate via existing `get_candidate`; if missing, raise `ValueError(f"Candidate not found: {candidate_id}")` (same pattern as intake archive helpers).
   - Return `normalize_topic_menu((candidate.get("candidate_data") or {}).get(_topic_menu_key()))`.

6. Add `validate_topic(topic: Any) -> dict` — returns a **new** normalized topic dict or raises `ValueError` with a safe message:

   - `topic` must be a `dict`.
   - `id`: non-empty `str` after strip (stable identity for revise).
   - `name`: non-empty `str` after strip.
   - `ask`: non-empty `str` after strip.
   - `required`: must be `bool` (reject truthy strings / ints).
   - `informs`: non-empty `list` of unique non-empty `str`; every entry must be in `TOPIC_MENU_CONFIG["informs"]`; reject empty list (parent: every topic informs at least one allowed target).
   - `status`: must be in `TOPIC_MENU_CONFIG["statuses"]`; if missing, use `TOPIC_MENU_CONFIG["default_status"]`.
   - Ignore unknown extra keys for forward-compat (do not persist them in the returned dict — only the required fields).
   - Returned shape:

```python
{
    "id": id,
    "name": name,
    "ask": ask,
    "required": required,
    "informs": list(informs),  # preserved order, deduped first-seen
    "status": status,
}
```

7. Add `validate_topic_menu(menu: Any) -> dict`:

   - Normalize via `normalize_topic_menu`.
   - Validate each topic; collect ids; raise `ValueError` if duplicate `id` values.
   - Return `{"topics": [validated…]}`.

8. Add `revise_topic_menu(existing: Any, incoming: Any) -> dict` — **revise without wipe**:

   - `existing_n = validate_topic_menu(existing)` (empty ok).
   - `incoming_n = validate_topic_menu(incoming)` (may be empty → retire all existing).
   - Index existing topics by `id`.
   - Build `out: list` in **incoming order**:
     - For each incoming topic: if id known, keep that identity and take incoming field values (name/ask/required/informs/status as validated); else append as new.
   - Then append every existing topic whose `id` is **not** in incoming, with `status` forced to `"retired"` (preserve name/ask/required/informs).
   - Return `{"topics": out}`.

⚠️ **Decision:** Revision identity is topic `id` (string), not name. AST-1075 must mint stable ids on generation (UUID or equivalent). Renaming a topic keeps the same `id` and updates `name`/`ask`. Topics dropped from an incoming generation are **retired**, never deleted from the list.

⚠️ **Decision:** Do **not** provide a `wipe=True` / hard-delete API in this ticket. Parent AC3 forbids wholesale wipe; retired retention is the only remove path.

9. Add `save_topic_menu(candidate_id: str, menu: Any, *, revise: bool = True, debug: bool = False) -> dict`:

   - `logger.set_debug_flag(debug)` at entry (same pattern as `save_candidate_data`).
   - Load current via `get_topic_menu(candidate_id)`.
   - If `revise` is `True`: `to_store = revise_topic_menu(current, menu)`.
   - If `revise` is `False`: `to_store = validate_topic_menu(menu)` (full replace of the `topics` list content **after** validation — still no partial deep-merge of individual topics; used only when caller intentionally supplies the complete authoritative list including any retired rows they want kept). Default remains `revise=True`.
   - Persist with `save_candidate_data(candidate_id, {_topic_menu_key(): to_store}, debug=debug)` (lists overwrite under `_deep_merge` — do not manually merge topic arrays).
   - When `debug=True`, emit Style D lines before/after persist:
     - found: current topic count + ids (truncated if long via existing `truncate_debug_content` if already imported in this module; otherwise short `len` + first/last id only).
     - recorded: stored topic count, counts by status (`open`/`ready`/`retired`), and whether `revise` was used.
     - Use `logger.debug_index` / `logger.debug_detail` with `func="candidate.save_topic_menu"`, identifier=`candidate_id`, outcome `found` then `recorded` (index `1/2`, `2/2`).
   - Return `to_store`.

10. Do **not** add Flask routes in this ticket. AST-1075 / a later UI ticket will call these helpers.

---

## Stage 3: Document the data model

**Done when:** `CANDIDATE_DATA_MODEL.md` documents `topic_menu` as a meta sibling and the topic field/status/informs contract; no stale claim that meta is only lifecycle/intakes/pending_craft.

1. In `docs/features/candidate/CANDIDATE_DATA_MODEL.md`, under the `candidate_data (library + meta)` section:

   - Extend the meta-siblings sentence to include `topic_menu` (AST-1074).
   - Add a subsection **### topic_menu (AST-1074 / AST-953)** describing:

```text
candidate_data.topic_menu = {
  "topics": [
    {
      "id": "<stable str>",
      "name": "<display name>",
      "ask": "<directed question>",
      "required": true|false,
      "informs": ["backstory", ...],  # ⊆ TOPIC_MENU_CONFIG["informs"], non-empty
      "status": "open" | "ready" | "retired"
    },
    ...
  ]
}
```

   - Note: revise keeps prior topics; dropped ids become `retired` rather than deleted.
   - Note: generation/confirm lives in AST-1075; this epic does not craft artifacts — `informs` declares intent only.
   - Cross-link `TOPIC_MENU_CONFIG` in `src/utils/config.py`.

2. Do **not** add Topic Menu fields under `contact` / `context` / `artifacts` tables in that doc.

---

## Self-Assessment

**Scope:** `Single-Component` — config contract + core candidate persistence helpers + data-model doc; no UI, no agent tasks, no schema migration.

**Conf:** `high` — mirrors AST-1014 meta-sibling + `save_candidate_data` / `PREAMBLE_CONFIG` assert patterns already on `dev`; revise-by-id is a concrete algorithm with no open product questions (parent Open questions: none).

**Risk:** `Medium` — wrong revise semantics would lose topic history for AST-1075 regenerations; mitigated by default `revise=True` and retired retention. Informs catalog mistakes would block valid menus — asserts lock the six parent targets.

---

## Code Rules check

- **§2.1 / config-source-of-truth / no-hardcoded-sets:** informs + statuses only in `TOPIC_MENU_CONFIG`; helpers read the config block, not inline frozensets.
- **§3.3 import direction:** core → utils/config + data via existing `save_candidate_data`; no UI → data shortcuts; no external Slack/LLM in this ticket.
- **§1.3 DRY:** reuse `save_candidate_data` / `get_candidate`; do not reimplement JSON merge.
- **debug-contract-gated:** Style D only when `debug=True` on `save_topic_menu`.
- **Out of scope enforced:** no Estelle tasks, no state hops, no satisfaction UI, no `tests/` edits.

---

## Review

**Publish ref:** `sub/AST-953/AST-1074-topic-menu-model-and-persistence`

**Build tip:** `ce0c64c12fd413b66c3e43f0d627f65a2fa9a338`

**Reviewed tip:** `9cb1928f` (`merge-tests(AST-1074)`) vs `origin/dev`

**Overall:** DISCUSS (C4 straggler only; no product fix-now)

### What’s solid

- `TOPIC_MENU_CONFIG` closed informs + status triad with asserts; helpers validate/revise/save via `save_candidate_data`.
- Style D on `save_topic_menu(..., debug=)` gated; default `revise=True` retires missing ids.
- Boundaries held: no UI, no Estelle generation, no state hops.

### Findings

**discuss (C4):** Joan Excluded `astral.git.engineer-test-tree-ban` (plan paths); tip three-dot now includes Betty `tests/**` + bible. Statute still **conforms** (engineer SHAs omit test tree). No engineer action unless Archie wants plan-rubric exclude lists re-scored after Tests Ready.

**discuss (carry Joan):** `revise=False` full-replace can drop retired history if callers omit them — AST-1075 must keep default revise or pass complete lists.

**advisory:** `TOPIC_MENU_CONFIG` sits after `PREAMBLE_VALIDATION_CONFIG` asserts (plan said after PREAMBLE); placement-only.

### Recommended actions

None for resolve-child product code. Acknowledge discuss items or leave for AST-1075 caller contract.

---

## Resolution

**Date:** 2026-07-30  
**Review:** Radia `[code-rubric] revision=1` Overall DISCUSS @ `b4b0cfb3` (product tip `9cb1928f`).

**fix-now:** none — no product code changes.

**discuss (C4 straggler):** Acknowledged. Joan Excluded `astral.git.engineer-test-tree-ban` on plan paths; post–Tests Ready tip includes Betty `tests/**` + bible. Statute remains conforms (engineer SHAs omit test tree). No Archie re-score requested; no plan-rubric rewrite.

**discuss (carry Joan / AST-1075 caller contract):** Acknowledged. `save_topic_menu(..., revise=False)` can drop retired topics if the caller omits them. Callers (AST-1075) must keep default `revise=True` or pass a complete list including retired rows. Documented here for Hedy; no API change on this tip.

**advisory:** Acknowledged. `TOPIC_MENU_CONFIG` placement after `PREAMBLE_VALIDATION_CONFIG` asserts is intentional adjacency; no move.

**Outcome:** resolve clean → User Testing.

