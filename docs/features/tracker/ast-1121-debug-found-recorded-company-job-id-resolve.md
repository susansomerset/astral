<!-- linear-archive: AST-1121 archived 2026-08-11 -->

## Linear archive (AST-1121)

**Archived:** 2026-08-11  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1121/debug-foundrecorded-for-company-job-id-resolve-fallback-for-company  
**Status at archive:** Archive  
**Project:** Astral Tracker  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-1119 — Fallback for company job id  
**Blocked by / blocks / related:** parent: AST-1119

### Description

## What this implements

After #1: on the touched `debug=` qualify apply path, Style D index + `|` detail for found source (AI vs UUID-from-`job_link` vs neither), `job_link` used when falling back, and recorded `company_job_id`. No new product behavior beyond observability.

## Acceptance criteria

- [X] 4. With `debug=True` on the touched apply run, each job index shows found source (AI vs UUID-from-`job_link` vs neither) and recorded `company_job_id` under Style D / `|` detail.

## Boundaries

- [X] Does not own the resolve rule or wire into the empty-id gate (sibling #1 / AST-1120).
- [X] Does not change create-time meteorite ingest.
- [X] Does not use company `job_site` for fallback debug link.
- [X] Does not expand to `qualify_job_listings`.

## In scope

- [X] `astral.standards.debug-contract-gated` — Style D found source + recorded `company_job_id` (and fallback `job_link` when used) on touched `qualify_meteorite` apply path when `debug=True`

## Considered but excluded

- [X] Resolve rule / empty-id gate wire — AST-1120 owns `_resolve_company_job_id` and gate placement; this ticket must not change outcomes
- [X] Meteorite create / gazer ingest leaving `company_job_id` empty — out of Boundaries
- [X] `qualify_job_listings` — parent forbids expansion; no empty-id content fail gate there today
- [X] Company `job_site` / non-`job_link` URLs — never used for fallback or fallback debug link
- [X] New config keys / formatting helpers — labels are fixed AC vocabulary; reuse AST-1120 resolve inputs for classification

## Notes for planning

After #1 (AST-1120). Debug contract only on touched `qualify_meteorite` apply path.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1119-fallback-for-company-job-id`, child `sub/AST-1119/AST-1121-debug-found-recorded-company-job-id-resolve`. Created at dispatch-parent.

### Comments

#### radia — 2026-08-09T22:53:25.978Z
#proxy-test

second version

#### radia — 2026-08-09T22:52:11.939Z
proxy smoke test — ignore

#### chuckles — 2026-08-02T17:58:55.693Z
[merge-child] blocked: missing test(AST-1121) on origin/sub/AST-1119/AST-1121-debug-found-recorded-company-job-id-resolve

validate-sub-log failed — need the canonical test() commit in the sub log (plan/code/merge-tests/test/docs/resolve). @Hedy Lamarr please publish test(AST-1121) on the publish ref and leave status User Testing.

— Chuckles

#### radia — 2026-08-02T17:57:34.811Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1121
**Publish ref:** `origin/sub/AST-1119/AST-1121-debug-found-recorded-company-job-id-resolve` @ `57c850e3`
**Overall:** DISCUSS

Diff baseline: `origin/dev...origin/sub/AST-1119/AST-1121-debug-found-recorded-company-job-id-resolve` — layers `{core, docs, utils}`; change_types `{add, modify}`. Tip includes resolved AST-1120 sibling work plus this ticket’s debug labels.

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | conforms | no confidence/grade bound changes |
| `astral.agent.do-task-delegation` | scoped | conforms | no new do_task |
| `astral.agent.grade-vector-validation` | scoped | conforms | no graded-task changes |
| `astral.batch.batch-id-first` | scoped | conforms | no new claim/batch_id helpers |
| `astral.batch.batch-id-format` | scoped | conforms | batch_id untouched |
| `astral.batch.claim-process-release` | scoped | conforms | debug labels inside existing qualify process |
| `astral.batch.entity-agent-responses-latest-only` | scoped | conforms | no RESPONSE storage change |
| `astral.config.config-source-of-truth` | scoped | conforms | no new config keys; AC-fixed label strings |
| `astral.config.pass-threshold-vs-score-floor` | scoped | conforms | thresholds untouched |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | conforms | no secrets/env reads added |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | paths no match among ['artifacts/**', 'scripts/spikes/**'] |
| `astral.debug.spikes-under-debug-dir` | scoped | conforms | docs/features plans only; not spike notes |
| `astral.dispatch.run-next-is-chain-authority` | scoped | conforms | no run_next/dispatch chain edits |
| `astral.dispatch.seed-auto-false` | scoped | conforms | config touch is UUID pattern only; no seed/dispatch_task |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | one features file per ticket (1120+1121) |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty commits only tests/bible; merge-tests ok |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | tests/bible only in test()+merge-tests commits |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | core-only debug enrichment; no external I/O |
| `astral.layers.import-direction` | scoped | conforms | 1121 code adds no new imports; consult→utils retained |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | layers ['scripts'] ∩ diff ['core', 'docs', 'utils'] empty |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | no UI rule surface; config from sibling only |
| `astral.patterns.coat-check-never-store-empty` | scoped | conforms | coat-check paths untouched |
| `astral.patterns.render-verdict-orchestrates-consult` | scoped | conforms | qualify_meteorite process debug only |
| `astral.patterns.require-auth-on-protected-endpoints` | scoped | not-applicable | layers ['ui'] ∩ diff ['core', 'docs', 'utils'] empty |
| `astral.seed.agent-tables-in-repo-json` | scoped | conforms | no seed JSON |
| `astral.seed.archie-catalog-wins` | scoped | conforms | no catalog edits |
| `astral.seed.boot-only-not-hot-path` | scoped | conforms | not seed/boot work |
| `astral.seed.define-approved` | scoped | conforms | no seed define |
| `astral.seed.operator-rows-stay-deleted` | scoped | conforms | untouched |
| `astral.seed.other-via-coverage-join` | scoped | conforms | untouched |
| `astral.standards.data-raises-caller-logs` | scoped | conforms | no data-layer edits |
| `astral.standards.database-header-inventory` | scoped | not-applicable | layers ['data'] ∩ diff ['core', 'docs', 'utils'] empty |
| `astral.standards.debug-contract-gated` | scoped | conforms | source labels only via existing debug_detail under if debug |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | classify from AI strip + resolved id; no second resolve |
| `astral.standards.in-scope-only` | scoped | conforms | qualify_meteorite apply debug only for 1121 |
| `astral.standards.logging-via-utils` | scoped | conforms | uses existing get_logger debug helpers |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | AC vocabulary labels; no ticket ids in symbols |
| `astral.standards.no-cross-contamination` | scoped | conforms | stays in consult.py apply path |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | fixed AC debug labels; no behavior-driving sets |
| `astral.standards.public-then-helpers` | scoped | conforms | no new public API; locals in process |
| `astral.standards.utils-data-late-import-only` | scoped | conforms | formatting pure; no data import |
| `astral.state.core-decides-transitions` | scoped | conforms | no fail_reason/state changes |
| `astral.state.job-prior-states-enforced` | scoped | conforms | prior_states untouched |
| `astral.state.no-daisy-chain-in-run` | scoped | conforms | no daisy-chain invent |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | layers ['ui'] ∩ diff ['core', 'docs', 'utils'] empty |
| `astral.ui.naming-conventions` | scoped | not-applicable | layers ['ui'] ∩ diff ['core', 'docs', 'utils'] empty |
| `astral.ui.single-gunicorn-worker` | scoped | conforms | no worker/deployment changes |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | one merge-tests(AST-1121) on sub tip |
| `orch.git.commit-vocabulary` | universal | conforms | docs/code/resolve/test/merge-tests vocabulary |
| `orch.git.flow-direction-inviolable` | universal | conforms | publish stays on origin/sub child ref |
| `orch.git.ftr-sub-topology` | universal | conforms | sub/AST-1119/AST-1121-… matches parent Git table |
| `orch.git.merge-on-checkout` | universal | conforms | no illegal merge recipe in tip commits |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | linear commits; no cherry-pick/rebase/force |
| `orch.git.no-dev-agent-branches` | universal | conforms | child publish-ref is sub/… not agent-named |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | review in astral-AST-1119 epic worktree |
| `orch.git.three-permanent-branches` | universal | conforms | no new permanent branch |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | observability-only; no product fork |
| `orch.pipeline.plan-is-bible` | universal | conforms | Stage 1 + Files Changed match tip |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Tracker child AST-1121 only |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Tests Passed → review-child |
| `orch.roles.archie-approves-statutes` | universal | conforms | no canon/statutes edits |
| `orch.roles.betty-owns-test-tree` | universal | conforms | tests/bible via test()+merge-tests only |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | assignee remains Hedy |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Hedy stays assignee through Tests Passed |
| `orch.roles.pre-commit-path-bans` | universal | conforms | no banned path edits in product commits |

## Pattern conformance

none cited (statute `astral.standards.debug-contract-gated` covered in checked-list)

## Plan adherence

Stage 1 matches tip: pre-resolve `ai_company_job_id`, classify `AI` / `UUID-from-job_link` / `neither`, enrich existing fail/pass Style D `debug_detail` with `found source=` + `fallback_job_link=` when not AI (pass: UUID-only), keep `|` recorded half. Self-Assessment Scope `minor` matches. Boundaries held — `_resolve_company_job_id` semantics / gates / create / `job_site` / `qualify_job_listings` untouched in `code(AST-1121)`.

## Findings

**fix-now:** none

**discuss (C4 straggler — excluded at plan time but in-scope on tip vs `origin/dev`):** mostly inherited sibling AST-1120 + plan/tests on tip; all scored `conforms`:
1. `astral.debug.spikes-under-debug-dir`
2. `astral.dispatch.seed-auto-false`
3. `astral.docs.features-single-file-per-ticket`
4. `astral.git.engineer-test-tree-ban`
5. `astral.layers.ui-config-driven-business-logic`
6. `astral.seed.agent-tables-in-repo-json`
7. `astral.seed.archie-catalog-wins`
8. `astral.seed.operator-rows-stay-deleted`
9. `astral.seed.other-via-coverage-join`
10. `astral.standards.utils-data-late-import-only`
11. `astral.ui.single-gunicorn-worker`

No product code action required.

## What's solid

Debug-gated Style D source labels from AI strip + resolved id; no second resolve; pass/fail detail shapes match plan; one `merge-tests` SHA.

## Recommended actions

Resolve-child can proceed without product edits for these discuss items.

**Notes:** Joan plan-rubric verdict attached (APPROVED). Active statute count checked: 65. §5f: new detail only under existing `if debug:` blocks.

context_tokens≈48000

#### betty — 2026-08-02T17:54:57.056Z
1. `tests/component/core/test_consult.py::TestAst1121CompanyJobIdDebugSource` — `debug=True` pass `found source=AI` (no `fallback_job_link`); pass `UUID-from-job_link` + `fallback_job_link` + recorded UUID; fail AI (other gate) omits fallback link; fail `neither` + `gate=empty company_job_id` + `fallback_job_link`; `debug=False` omits Style D source labels.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_consult.py::TestAst1121CompanyJobIdDebugSource \
  -q
```

**Broken / obsolete:** none — prior AST-1062 / AST-1120 manifests do not assert pre-label detail strings.

**Integration:** none revised.

**Publish:** `origin/sub/AST-1119/AST-1121-debug-found-recorded-company-job-id-resolve` @ `2ea3894d` (`merge-tests(AST-1121): origin/tests 9b31527c`).

**Bible shasum on publish tip:**
- `docs/test-bible/core/consult.md` `a4c4142af2e39f0fe75c139bc8c8d6451a7f8483`

— Betty

#### joan — 2026-08-02T17:34:27.017Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1121
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 AI `company_job_id` unchanged | N/A — boundary (AST-1120); plan forbids resolve/outcome changes |
| AC2 Empty AI + UUID records UUID | N/A — boundary (AST-1120) |
| AC3 Empty AI + no UUID still empty-id fail | N/A — boundary (AST-1120); debug labels only |
| AC4 debug=True found source + recorded `company_job_id` Style D / `|` | Stage 1 — enrich existing fail/pass `debug_detail` with `AI` / `UUID-from-job_link` / `neither` + `fallback_job_link` when not AI |
| AC5 Meteorite create-without-id unchanged | N/A — boundary; no create edits |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 Found-source Style D detail on `qualify_meteorite` apply | Parent Functional scope debug bullet; `astral.standards.debug-contract-gated`; child AC4 |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests |
| orch.git.commit-vocabulary | conforms | Sub publish / plan vocabulary |
| orch.git.flow-direction-inviolable | conforms | Publish to origin/sub only |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | No illegal merge recipe |
| orch.git.no-cherry-pick-rebase-force | conforms | None proposed |
| orch.git.no-dev-agent-branches | conforms | Uses sub/AST-1119/AST-1121-… |
| orch.git.one-epic-worktree-per-parent | conforms | astral-AST-1119 epic worktree |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | No product fork; observability only |
| orch.pipeline.plan-is-bible | conforms | Binding stage + Files Changed |
| orch.pipeline.project-scoped-queues | conforms | Single-child Tracker scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate only |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | No tests/bible edits |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Hedy) implements |
| orch.roles.engineer-assignee-through-resolve | conforms | Implementer path after approve |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | Untouched |
| astral.agent.do-task-delegation | conforms | Untouched |
| astral.agent.grade-vector-validation | conforms | Untouched |
| astral.batch.batch-id-first | conforms | Untouched |
| astral.batch.batch-id-format | conforms | Untouched |
| astral.batch.claim-process-release | conforms | Observability inside existing process only |
| astral.batch.entity-agent-responses-latest-only | conforms | No RESPONSE storage change |
| astral.config.config-source-of-truth | conforms | No new config; AC-fixed label vocabulary |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env |
| astral.dispatch.run-next-is-chain-authority | conforms | Untouched |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src |
| astral.layers.core-vs-external-bright-line | conforms | Core-only debug enrichment |
| astral.layers.import-direction | conforms | No new imports / layers |
| astral.patterns.coat-check-never-store-empty | conforms | Untouched |
| astral.patterns.render-verdict-orchestrates-consult | conforms | qualify_meteorite process debug only |
| astral.seed.boot-only-not-hot-path | conforms | Not seed work |
| astral.seed.define-approved | conforms | Untouched |
| astral.standards.data-raises-caller-logs | conforms | No data-layer edits |
| astral.standards.debug-contract-gated | conforms | Extends existing `if debug:` Style D `|` detail; no ungated noise |
| astral.standards.dry-and-focused-functions | conforms | Classify from AI strip + resolved id; no second resolve |
| astral.standards.in-scope-only | conforms | qualify_meteorite apply debug only |
| astral.standards.logging-via-utils | conforms | Uses existing debug helpers path |
| astral.standards.names-not-ticket-ids | conforms | Domain labels from AC vocabulary |
| astral.standards.no-cross-contamination | conforms | Stays in consult.py |
| astral.standards.no-hardcoded-sets | conforms | Fixed AC debug labels; no new behavior-driving sets/config |
| astral.standards.public-then-helpers | conforms | No new public API; locals in process |
| astral.state.core-decides-transitions | conforms | Explicitly no fail_reason/state changes |
| astral.state.job-prior-states-enforced | conforms | Untouched |
| astral.state.no-daisy-chain-in-run | conforms | Untouched |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.dispatch.run-next-is-chain-authority, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.seed.boot-only-not-hot-path, astral.seed.define-approved, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.names-not-ticket-ids, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths match none of plan paths
- astral.debug.spikes-under-debug-dir — paths match none of plan paths
- astral.dispatch.seed-auto-false — paths match none of plan paths
- astral.docs.features-single-file-per-ticket — layers {docs} ∩ plan empty
- astral.git.engineer-test-tree-ban — paths match none of plan paths
- astral.layers.scripts-exempt-from-layer-rules — layers ∩ plan empty
- astral.layers.ui-config-driven-business-logic — layers ∩ plan empty
- astral.patterns.require-auth-on-protected-endpoints — layers ∩ plan empty
- astral.seed.agent-tables-in-repo-json — paths match none of plan paths
- astral.seed.archie-catalog-wins — paths match none of plan paths
- astral.seed.operator-rows-stay-deleted — paths match none of plan paths
- astral.seed.other-via-coverage-join — paths match none of plan paths
- astral.standards.database-header-inventory — layers ∩ plan empty
- astral.standards.utils-data-late-import-only — layers ∩ plan empty
- astral.ui.frontend-file-placement — layers ∩ plan empty
- astral.ui.naming-conventions — layers ∩ plan empty
- astral.ui.single-gunicorn-worker — layers ∩ plan empty

## Findings

None fix-now.

**acceptable:** Scope minor / Conf high / Risk low honest for debug-only enrichment. Classification from pre-resolve AI strip + resolved id avoids a second resolve path (DRY). `fallback_job_link=link_for_id` respects no-`job_site` boundary. Parent AC1–3/5 correctly left to AST-1120.

**R6:** Definition fidelity pass for child #2 debug. Layer/import pass. No resolve/create/`qualify_job_listings` creep. Debug gated on existing `if debug:` only.

context_tokens≈42000

— Joan

#### hedy — 2026-08-02T17:32:19.722Z
Plan: [`docs/features/tracker/ast-1121-debug-found-recorded-company-job-id-resolve.md`](https://github.com/susansomerset/astral/blob/sub/AST-1119/AST-1121-debug-found-recorded-company-job-id-resolve/docs/features/tracker/ast-1121-debug-found-recorded-company-job-id-resolve.md) on `origin/sub/AST-1119/AST-1121-debug-found-recorded-company-job-id-resolve` @ `329179d9`.

**Scope:** minor — enrich existing `qualify_meteorite` apply Style D detail with found-source labels only.
**Conf:** high — AST-1120 already resolves + logs values; classify from pre-resolve AI strip + resolved id.
**Risk:** low — `debug=True` observability only; resolve/gate paths untouched.

---

# AST-1121 — Debug found/recorded for company_job_id resolve

**Linear:** [AST-1121](https://linear.app/astralcareermatch/issue/AST-1121/debug-foundrecorded-for-company-job-id-resolve-fallback-for-company)
**Parent:** [AST-1119](https://linear.app/astralcareermatch/issue/AST-1119/fallback-for-company-job-id) — Fallback for company job id
**Publish ref:** `origin/sub/AST-1119/AST-1121-debug-found-recorded-company-job-id-resolve`

After AST-1120’s resolve rule, the touched `qualify_meteorite` `debug=True` apply path already emits Style D index + `|` detail with resolved/recorded `company_job_id` values, but does **not** label **how** the id was found. This ticket adds found-source observability only: `AI` vs `UUID-from-job_link` vs `neither`, the `job_link` used when falling back, and recorded `company_job_id`. No resolve-rule or gate-behavior change.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/consult.py` | In `qualify_meteorite` `process`, classify found source from pre-resolve AI strip + post-resolve id; enrich existing `debug=True` fail/pass `|` detail lines (and keep Style D `debug_index`) | core |

No `tests/` / bible / config / formatting / meteorite create / `qualify_job_listings` / resolve-rule edits. Do **not** change `_resolve_company_job_id` return semantics or empty-id gate outcomes.

## Stage 1: Found-source Style D detail on qualify_meteorite apply

**Done when:** With `debug=True`, each processed job’s Style D `|` detail shows `source=AI` | `source=UUID-from-job_link` | `source=neither`; when source is `UUID-from-job_link`, detail includes the `job_link` used for fallback (`link_for_id`); pass path still shows recorded `company_job_id`; `debug=False` adds no new lines; resolve/gate behavior unchanged.

1. In `src/core/consult.py`, inside `qualify_meteorite`’s nested `process(input_job, response_job, cfg)`, **keep** the AST-1120 resolve wire exactly as it is today:

```python
company_job_id = (response_job.get("company_job_id") or "").strip()
job_title = (response_job.get("job_title") or "").strip()
job_link = (response_job.get("job_link") or "").strip()
jd_text = (response_job.get("jd_text") or "").strip()
link_for_id = job_link or (input_job.get("job_link") or "").strip()
company_job_id = _resolve_company_job_id(company_job_id, link_for_id)
```

Before calling `_resolve_company_job_id`, bind the pre-resolve AI strip to a local (do not change what is passed into resolve):

```python
ai_company_job_id = (response_job.get("company_job_id") or "").strip()
# … job_title / job_link / jd_text strips unchanged …
link_for_id = job_link or (input_job.get("job_link") or "").strip()
company_job_id = _resolve_company_job_id(ai_company_job_id, link_for_id)
```

⚠️ **Decision — classify from AI strip + resolved id, do not change `_resolve_company_job_id` signature:** AST-1120 already owns prefer-AI-else-UUID-else-empty. Source labels are derived for debug only: non-empty `ai_company_job_id` → `AI`; else non-empty resolved `company_job_id` → `UUID-from-job_link`; else `neither`. Recomputing via `uuid_path_segment_from_url` is unnecessary and would drift if resolve ever gains another branch.

2. Still inside `process`, after resolve and **only for use under existing `if debug:` blocks**, compute:

```python
if ai_company_job_id:
    id_source = "AI"
elif company_job_id:
    id_source = "UUID-from-job_link"
else:
    id_source = "neither"
```

Literal label strings must be exactly `AI`, `UUID-from-job_link`, and `neither` (parent AC / sibling plan wording).

3. Enrich the **existing** content-fail `debug_detail` (still under `if fail_reason:` / `if debug:`) so the `|` line includes found source and, when falling back, the link used. Replace the current fail detail string with one built as follows (keep `gate=` / title / link / jd_chars already present):

- Always include `found source={id_source}` and `company_job_id={company_job_id!r}` (resolved value, same as today).
- When `id_source == "UUID-from-job_link"` **or** `id_source == "neither"`, also include `fallback_job_link={link_for_id!r}` (the URL consulted for UUID fallback — response `job_link` else input `job_link`).
- When `id_source == "AI"`, do **not** require `fallback_job_link=` (AI won; fallback was not used). Other existing fields (`gate=`, `title=`, `link=`, `jd_chars=`) stay.

Concrete fail detail shape (single `debug_detail` call; one line):

```python
# AI fail (other gates) example fragments:
#   gate=… found source=AI company_job_id='…' title=… link=… jd_chars=…
# UUID fallback then other-gate fail:
#   gate=… found source=UUID-from-job_link fallback_job_link='…' company_job_id='…' …
# neither (empty-id fail):
#   gate=empty company_job_id found source=neither fallback_job_link='…' company_job_id='' …
```

Keep the existing `debug_index` header on the fail path (same `func` / identifier / outcome). Do **not** add a second index header.

4. Enrich the **existing** pass-path `debug_detail` (after `initialize_job` + `get_job` recorded snapshot) the same way:

- Keep `debug_index` as today.
- Prefixed found half: `found source={id_source}` then, if `id_source` is `UUID-from-job_link`, `fallback_job_link={link_for_id!r}`, then existing found fields (`company_job_id`, `title`, `link`, `jd_chars`).
- Keep the `|` recorded half exactly as today (`recorded company_job_id=… title=… link=… jd_chars=…`).
- When `id_source == "AI"`, omit `fallback_job_link=`.
- When `id_source == "neither"` cannot occur on the pass path after a successful empty-id gate — do not special-case pass for `neither`.

⚠️ **Decision — extend existing Style D lines, do not add parallel debug surfaces:** Input-job Style D at the top of `qualify_meteorite` stays untouched. Only the per-job apply `process` fail/pass details gain source labels. No new `logger.info("[DEBUG]")`, no config keys, no changes when `debug=False`.

⚠️ **Decision — `fallback_job_link` is `link_for_id`, not company `job_site`:** Matches AST-1120’s resolve input. Response `job_link` used for the http gate / recorded link is still logged as today’s `link=`; `fallback_job_link=` is only the URL fed to resolve when source is not `AI`.

5. Do **not** edit `_resolve_company_job_id`, `uuid_path_segment_from_url`, `TRACKER_CONFIG`, meteorite create, or `qualify_job_listings`. Do **not** change fail_reason strings, state transitions, or `parsed_job` contents.

**Done when (recheck):** Manual trace under `debug=True`:

1. AI non-empty → detail has `found source=AI` and `recorded company_job_id` matching AI; no `fallback_job_link=`.
2. AI empty + UUID in `link_for_id` → `found source=UUID-from-job_link`, `fallback_job_link=` that URL, recorded id = UUID.
3. AI empty + no UUID → fail detail `found source=neither` + `fallback_job_link=`; still `gate=empty company_job_id`.
4. `debug=False` → no new contract lines (existing non-debug `logger.info` paths unchanged).

`python3 -m py_compile src/core/consult.py` succeeds.

## Self-Assessment

**Scope:** `minor` — one apply-path debug enrichment in `consult.qualify_meteorite` `process`; no new modules or resolve behavior.

**Conf:** `high` — AST-1120 already wires resolve and Style D found/recorded values; this ticket only labels source from the pre-resolve AI strip + resolved id using parent AC vocabulary.

**Risk:** `low` — observability only under `debug=True`; wrong labels would mislead operators but cannot change gate outcomes if resolve call and fail/pass branches stay untouched.

## Code Rules check

| Rule | Notes |
|------|-------|
| §1.5.1 debug-contract-gated | New/changed detail only inside existing `if debug:` blocks; Style D index + `\|` detail; no ungated noise |
| §1.3 DRY / public-then-helpers | No new public API; classification is three locals next to existing debug blocks (not a second resolve implementation) |
| §2.1 config | No new config — labels are fixed AC vocabulary |
| §3.3 imports | No new imports required |
| in-scope-only | Touched surface = `qualify_meteorite` apply debug only; resolve rule remains AST-1120 |

## Statute frame (Linear description)

**In scope**

- [ ] `astral.standards.debug-contract-gated` — Style D found source + recorded `company_job_id` (and fallback `job_link` when used) on touched `qualify_meteorite` apply path when `debug=True`

**Considered but excluded**

- [ ] Resolve rule / empty-id gate wire — AST-1120 owns `_resolve_company_job_id` and gate placement; this ticket must not change outcomes
- [ ] Meteorite create / gazer ingest leaving `company_job_id` empty — out of Boundaries
- [ ] `qualify_job_listings` — parent forbids expansion; no empty-id content fail gate there today
- [ ] Company `job_site` / non-`job_link` URLs — never used for fallback or fallback debug link

## Review

**Publish ref:** `origin/sub/AST-1119/AST-1121-debug-found-recorded-company-job-id-resolve`
**Tip (pre-review):** `2ea3894d` (`merge-tests` + Betty coverage)

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `2fc5bbe7` | Style D found source + optional `fallback_job_link` on `qualify_meteorite` apply fail/pass |
| tests | `9b31527c` / `2ea3894d` | Betty Style D source-label coverage + `merge-tests` |

### Radia — code-rubric.v1 (`[code-rubric] revision=1`)

**Overall:** DISCUSS (C4 stragglers only; no product fix-now)

**What's solid**
- Labels `AI` / `UUID-from-job_link` / `neither` from pre-resolve AI strip + resolved id; no second resolve path.
- Enrichment only inside existing `if debug:` `debug_index` / `debug_detail` (pass keeps `|` recorded half); `debug=False` unchanged.
- Resolve/gate outcomes untouched; no create / `job_site` / `qualify_job_listings` creep.

**Issues**
- **discuss (straggler):** Joan plan-time Excluded → in-scope on tip vs `origin/dev` (mostly sibling AST-1120 + plan/tests on tip): `astral.debug.spikes-under-debug-dir`, `astral.dispatch.seed-auto-false`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, `astral.layers.ui-config-driven-business-logic`, `astral.seed.agent-tables-in-repo-json`, `astral.seed.archie-catalog-wins`, `astral.seed.operator-rows-stay-deleted`, `astral.seed.other-via-coverage-join`, `astral.standards.utils-data-late-import-only`, `astral.ui.single-gunicorn-worker` — all scored `conforms`; no product action.

**Recommended actions**
- Resolve-child: no code changes required for stragglers.

## Resolution

**2026-08-02** — `resolve(AST-1121): — clean`

- Radia **fix-now:** none.
- C4 discuss stragglers accepted as-is (all scored `conforms`; no product edits).
- Tip before resolve: `57c850e3` (Radia `docs()` on publish-ref).
