<!-- linear-archive: AST-1090 archived 2026-08-11 -->

## Linear archive (AST-1090)

**Archived:** 2026-08-11  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1090/gaze-email-runner-bind-route-scrape-dedupe-create-mailbox-outcomes-add  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-1087 — Add gaze_email as a dispatch task  
**Blocked by / blocks / related:** parent: AST-1087

### Description

## What this implements

After #1 and #2: core runner for the null-`candidate_id` `gaze_email` row that lists inbox, binds From→candidate, applies unbound age→Trash rules, routes bound shapes, calls Ruth with the bound candidate’s API key when required, scrapes links, per-candidate dedupes, creates **METEORITE_NEW**, archives on success **or** all-duplicate skip, Style D debug. Wire through normal dispatch like any other task body. Reuses meteorite create / gazer scrape helpers where they already match; does not own config shell or Ruth task definition.

## In scope

- [X] `pattern.state.entity-state-transitions` — create lands **METEORITE_NEW** only via `create_meteorite_job`
- [X] `astral.state.no-daisy-chain-in-run` — no qualify/GDL in the same hop
- [X] `astral.standards.debug-contract-gated` — Style D only when `debug=True` on the runner path
- [X] `astral.layers.core-vs-external-bright-line` — archive/trash/list I/O stay in `gmail.py` (via inbox wrappers where listed); policy/orchestration in core `gaze_email.py`
- [X] `astral.standards.in-scope-only` — no config shell / Ruth TASK_CONFIG / Manage Email UI / attachments / permanent delete
- [X] `astral.config.config-source-of-truth` — runner literals extend `GAZE_EMAIL_CONFIG`; Ruth key/modes via `METEORITE_EMAIL_PARSE_CONFIG`; scrape thresholds via `METEORITE_EMAIL_INGEST_CONFIG`
- [X] `astral.standards.no-hardcoded-sets` — retention / schemes / task keys not inlined outside config
- [X] `astral.layers.import-direction` — core←data/utils/external as existing patterns

## Considered but excluded

- [X] `pattern.config.config-block` shell / null-`candidate_id` schema / Gmail archive+trash capability — AST-1088 (already shipped; this ticket consumes)
- [X] Ruth `parse_meteorite_email` TASK_CONFIG / `agent_task.json` — AST-1089 (already shipped; this ticket calls `do_task`)
- [X] Global AST-1061 `job_link_exists` / `text_matches_known_company_job_id` on this path — parent Boundaries require **per-candidate** dedupe only
- [X] `qualify_meteorite` / GDL / Recommended / LIKE/upshot — parent Boundaries
- [X] Manage Email UI redesign / attachments / permanent Gmail delete — parent Boundaries
- [X] `tests/` / `docs/test-bible/**` — Betty after Code Complete

## Acceptance criteria

1. With a `gaze_email` `dispatch_task` row (`candidate_id` null, `auto_mode` true) running under normal dispatch, a bound inbox message matching each in-scope shape produces the corresponding **METEORITE_NEW** job(s) for that candidate (including subject+body appended when a job link was scraped), and the message is archived afterward.
2. A bound message with non-URL subject and empty body remains in the inbox (ignored); no job is created.
3. An unbound message newer than the configured retention window remains in the inbox unchanged.
4. An unbound message older than the configured retention window is moved to Gmail **Trash** and does not create a job.
5. When the same job link is ingested for two different candidates, both may receive a **METEORITE_NEW** row; when the same candidate receives a duplicate job already known for that candidate, create is skipped for that job; if a bound message produces only such skips, the message is still **archived**.
6. A single run does not advance jobs past **METEORITE_NEW** into qualify/GDL.
7. With `debug=True`, each processed message and each create/skip/trash/archive/ignore outcome is visible in Style D debug output (found + recorded); with `debug=False`, no new debug noise from this path.

## Boundaries

Does not own config shell or Ruth task definition (siblings #1 / #2). Does not run qualify/GDL in the same hop.

## Notes for planning

Citations migrated into In scope / Excluded above. After AST-1088 and AST-1089.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1087-add-gaze-email-as-a-dispatch-task`, child `sub/AST-1087/AST-1090-gaze-email-runner-bind-route-scrape-dedupe-create-mailbox`. Created at dispatch-parent.

### Comments

#### radia — 2026-07-31T02:45:30.339Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1090
**Publish ref:** `origin/sub/AST-1087/AST-1090-gaze-email-runner-bind-route-scrape-dedupe-create-mailbox` tip `11ffdeddec990e292f506e84b8564852b0472ac1` (product tip reviewed `cb049bd4`; docs() `11ffdedd`)
**Overall:** CLEAN

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| orch.git.betty-merge-tests-one-sha | universal | conforms | One `merge-tests(AST-1090): origin/tests e2819421…` on sub |
| orch.git.commit-vocabulary | universal | conforms | plan/code/test/docs/merge-tests vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | Published to origin/sub only |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1087/AST-1090-…` under parent ftr |
| orch.git.merge-on-checkout | universal | conforms | ftr already merged; no illegal merge |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | None in history |
| orch.git.no-dev-agent-branches | universal | conforms | No agent-named epic branch |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Review in astral-AST-1087 |
| orch.git.three-permanent-branches | universal | conforms | No permanent-branch invention |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Decisions documented in plan |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–3 match Files Changed |
| orch.pipeline.project-scoped-queues | universal | conforms | Meteorite child only |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | universal | conforms | tests/bible via Betty test + merge-tests |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee remains Hedy |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Implementer stays assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | Role path bans respected |
| astral.agent.confidence-bounds | scoped | conforms | No graded confidence path on gaze_email |
| astral.agent.do-task-delegation | scoped | conforms | Ruth via `do_task` + METEORITE_EMAIL_PARSE_CONFIG task_key |
| astral.agent.grade-vector-validation | scoped | conforms | Parse task scored False; no grade vectors |
| astral.batch.batch-id-first | scoped | conforms | Ledger/batch_id via `_dispatch_one` gaze path |
| astral.batch.batch-id-format | scoped | conforms | Uses dispatcher ledger pattern |
| astral.batch.claim-process-release | scoped | conforms | Mailbox poller available_count=1; not entity claim-queue |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | RESPONSE storage stays inside `do_task` |
| astral.config.config-source-of-truth | scoped | conforms | Runner literals extend GAZE_EMAIL_CONFIG; Ruth/ingest reused |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | No scored consult on this path |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | Gmail secrets untouched; candidate key from ctx |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths {artifacts/**,scripts/spikes/**} no match |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Feature plan docs, not spike findings |
| astral.docs.features-single-file-per-ticket | scoped | conforms | AST-1090 plan file; siblings are separate ticket files |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty commits touch tests/bible only |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer commits omit tests/bible |
| astral.layers.core-vs-external-bright-line | scoped | conforms | Archive/trash I/O in gmail.py; policy in gaze_email.py |
| astral.layers.import-direction | scoped | conforms | core←data/utils/external (+ inbox wrappers) as planned |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers {scripts} ∩ diff empty |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | No React |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | No coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | Not a render_verdict consult path |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | layers {ui} ∩ diff empty |
| astral.standards.data-raises-caller-logs | scoped | conforms | Data helpers query; core logs Style D / exceptions |
| astral.standards.database-header-inventory | scoped | conforms | Uses existing job table; no new tables |
| astral.standards.debug-contract-gated | scoped | conforms | Style D only when debug=True; index+detail+truncate |
| astral.standards.dry-and-focused-functions | scoped | conforms | Reuses inbox bind, gazer fetch, create_meteorite_job |
| astral.standards.in-scope-only | scoped | conforms | No shell/Ruth-catalog/UI/qualify/global dedupe creep |
| astral.standards.logging-via-utils | scoped | conforms | get_logger / Style D helpers |
| astral.standards.no-cross-contamination | scoped | conforms | Stays in layered src |
| astral.standards.no-hardcoded-sets | scoped | conforms | Schemes/retention/task keys/debug_func from config |
| astral.standards.public-then-helpers | scoped | conforms | Public run_gaze_email + private helpers |
| astral.standards.utils-data-late-import-only | scoped | conforms | No new utils→data load-time import |
| astral.state.core-decides-transitions | scoped | conforms | Landing via create_meteorite_job only |
| astral.state.job-prior-states-enforced | scoped | conforms | No ad-hoc job state hops |
| astral.state.no-daisy-chain-in-run | scoped | conforms | No qualify/GDL in-run |
| astral.ui.frontend-file-placement | scoped | not-applicable | layers {ui} ∩ diff empty |
| astral.ui.naming-conventions | scoped | not-applicable | layers {ui} ∩ diff empty |
| astral.ui.single-gunicorn-worker | scoped | conforms | No gunicorn/worker changes |

## Pattern conformance

- `pattern.state.entity-state-transitions` — **conforms** (METEORITE_NEW via `create_meteorite_job` only)
- Active `astral.patterns.*` — covered via statutes table

## Plan adherence

Self-Assessment Scope `MAJOR-CHANGE` matches runner + due wiring + data helper + gmail metadata footprint. Stages 1–3 delivered. AC1–7 branches present (ignore / unbound leave|trash / html_links / subject_url / subject_body / per-cand dedupe / all-skip archive / Style D). Sibling AST-1088/1089 product on tip via ftr lineage — expected.

## Findings

**discuss (straggler):** Joan Excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`; tip three-dot includes `docs/features/**` + Betty test-tree so sweep scores them in-scope (all still **conforms**). Joan artifact present.

**advisory:** Late `from src.core.gaze_email import run_gaze_email` in `_dispatch_one` lacks a cycle/lazy comment (peers in same file similarly uncommented). `ensure_gaze_email_dispatch_task` docstring still says runner unwired.

### What’s solid

`run_gaze_email` + due/`_dispatch_one` special-case; per-candidate link helper; Style D gated; create stops at METEORITE_NEW; archive/trash via external; Ruth uses bound candidate ctx.

### Recommended actions

None for fix-now.

context_tokens≈55000

#### betty — 2026-07-31T02:36:36.958Z
## QA test manifest

**Publish:** `origin/sub/AST-1087/AST-1090-gaze-email-runner-bind-route-scrape-dedupe-create-mailbox` @ `cb049bd4`
**Delivery:** `merge-tests(AST-1090): origin/tests e2819421686504aa235cabf9846e77012762689a`

### Gaps (new)

1. `tests/component/core/test_gaze_email.py` — subject-URL + unbound-stale helpers; runner unbound trash/leave, bound ignore, subject-URL create+archive, all-duplicate archive, html_links Ruth path, Style D on/off.
2. `tests/component/utils/test_config.py::TestAst1090GazeEmailRunnerConfig` — `subject_url_schemes` / `dispatch_ledger_candidate_id` / `debug_func`.
3. `tests/component/data/database/test_jobs.py::TestAst1090JobLinkExistsForCandidate` — per-candidate exact link (cross-candidate same URL allowed).
4. `tests/component/data/database/test_dispatch_tasks.py::TestAst1090GazeEmailDue` — `get_due_tasks` includes null-candidate shell; freq gate on `count_eligible`.
5. `tests/component/core/test_dispatcher.py::TestAst1090GazeEmailDispatchOne` — `_dispatch_one` calls `run_gaze_email` without candidate API key; skips `_run_unified`.
6. `tests/component/external/test_gmail.py::TestAst1090InternalDateMs` — `internalDate` parse + list field.

### Broken / obsolete (revised)

7. `TestListInboxMessages` exact dicts — add `internal_date_ms` (0 default).
8. `TestGmailHelpers::test_message_metadata_non_string_ids` — assert `internal_date_ms == 0`.

### Narrowed run (required)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_gaze_email.py \
  tests/component/utils/test_config.py::TestAst1090GazeEmailRunnerConfig \
  tests/component/data/database/test_jobs.py::TestAst1090JobLinkExistsForCandidate \
  tests/component/data/database/test_dispatch_tasks.py::TestAst1090GazeEmailDue \
  tests/component/core/test_dispatcher.py::TestAst1090GazeEmailDispatchOne \
  tests/component/external/test_gmail.py \
  -q
```

**Pass criterion:** pytest green on the lines above. Do **not** use zero-arg harness / branch-lock gate for this ticket. `src/external/gmail.py` remains **LOCKED_AT_100** (full `test_gmail.py` in the run).

### Bible shasums (`origin/<publish-ref>`)

- `docs/test-bible/core/gaze_email.md` `14c28fb4926ac1107770acf85dc077662543f6d3`
- `docs/test-bible/core/dispatcher.md` `034f79b2e39d89497e98e555424d64b752ee7e54`
- `docs/test-bible/utils/config.md` `091f3b7e00f9b6a45fa9f211b3b248e99684f242`
- `docs/test-bible/external/gmail.md` `918b745734936c7537a33e155db23c539ab96594`
- `docs/test-bible/data/database/dispatch_tasks.md` `edb146a9ab299464732f7aedf6aa71ba6d194266`

— Betty

#### joan — 2026-07-31T02:27:48.057Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1090
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 bound shapes → METEORITE_NEW + archive | Stages 2–3: dispatch wiring + shape routing + create + archive |
| AC2 non-URL subject + empty body ignored | Stage 3.4 ignore branch |
| AC3 unbound newer than retention stays | Stage 3.3 leave-inbox path |
| AC4 unbound older → Trash, no job | Stage 3.3 trash_message + no create |
| AC5 per-candidate dedupe; all-skip still archives | Stage 3.6 `job_link_exists_for_candidate` + Stage 3.7 finalize |
| AC6 account/retention/secrets + Ruth candidate API key | Retention/account consume AST-1088 config; Stage 3.5 `do_task` with bound `ctx` (Ruth catalog AST-1089) |
| AC7 no qualify/GDL in same hop | Stage 3.6 Decision — create_meteorite_job only |
| AC8 Style D debug found/recorded | Stage 3.8 |
| AC9 null candidate_id schema/provision | N/A — boundary (AST-1088; this ticket wires due + runner) |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 config + per-cand link helper + internalDate | Functional scope retention age + AC5 per-candidate dedupe foundation |
| Stage 2 due-task + `_dispatch_one` | Functional scope §1 normal dispatch / AUTO shell fires |
| Stage 3 runner bind/route/Ruth/scrape/create/mailbox + Style D | Purpose + Functional scope §2–6; child AC1–7 |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests |
| orch.git.commit-vocabulary | conforms | Sub publish only |
| orch.git.flow-direction-inviolable | conforms | origin/sub/… only |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | No illegal merge |
| orch.git.no-cherry-pick-rebase-force | conforms | None proposed |
| orch.git.no-dev-agent-branches | conforms | sub/AST-1087/AST-1090-… |
| orch.git.one-epic-worktree-per-parent | conforms | astral-AST-1087 |
| orch.git.three-permanent-branches | conforms | No permanent-branch invention |
| orch.pipeline.call-susan-for-product-decisions | conforms | Decisions explicit; block→parent on drift |
| orch.pipeline.plan-is-bible | conforms | Binding stages + Files Changed |
| orch.pipeline.project-scoped-queues | conforms | Single-child scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready gate |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | No tests/bible |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Hedy) owns build |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer path |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | No graded confidence path on gaze_email |
| astral.agent.do-task-delegation | conforms | Ruth via `do_task` + METEORITE_EMAIL_PARSE_CONFIG task_key |
| astral.agent.grade-vector-validation | conforms | Parse task scored False; no grade vectors |
| astral.batch.batch-id-first | conforms | Ledger/batch_id via existing `_dispatch_one` path |
| astral.batch.batch-id-format | conforms | Uses dispatcher ledger pattern |
| astral.batch.claim-process-release | conforms | Mailbox poller (available_count=1); not entity claim-queue |
| astral.batch.entity-agent-responses-latest-only | conforms | RESPONSE storage stays inside `do_task` |
| astral.config.config-source-of-truth | conforms | Runner literals extend GAZE_EMAIL_CONFIG; Ruth/ingest configs reused |
| astral.config.pass-threshold-vs-score-floor | conforms | No scored consult on this path |
| astral.config.secrets-and-env-specific-from-environ | conforms | Gmail secrets untouched; candidate key from candidate ctx |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src |
| astral.layers.core-vs-external-bright-line | conforms | Archive/trash/list I/O external; policy in gaze_email.py |
| astral.layers.import-direction | conforms | core←data/utils/external as specified |
| astral.layers.ui-config-driven-business-logic | conforms | No React |
| astral.patterns.coat-check-never-store-empty | conforms | No coat-check keys added |
| astral.patterns.render-verdict-orchestrates-consult | conforms | Not a render_verdict consult path |
| astral.standards.data-raises-caller-logs | conforms | Data helpers query/raise; core logs Style D |
| astral.standards.database-header-inventory | conforms | Uses existing job table; no new tables |
| astral.standards.debug-contract-gated | conforms | Style D only when debug=True |
| astral.standards.dry-and-focused-functions | conforms | Reuses inbox bind, gazer fetch, create_meteorite_job |
| astral.standards.in-scope-only | conforms | Excludes shell/Ruth catalog/UI/qualify/global dedupe |
| astral.standards.logging-via-utils | conforms | get_logger / Style D helpers |
| astral.standards.no-cross-contamination | conforms | Stays in layered src |
| astral.standards.no-hardcoded-sets | conforms | Schemes/retention/task keys from config |
| astral.standards.public-then-helpers | conforms | Public run_gaze_email + private helpers planned |
| astral.standards.utils-data-late-import-only | conforms | No new utils→data load-time import |
| astral.state.core-decides-transitions | conforms | Landing via create_meteorite_job config state only |
| astral.state.job-prior-states-enforced | conforms | No ad-hoc job state hops |
| astral.state.no-daisy-chain-in-run | conforms | Explicitly forbids qualify/GDL in-run |
| astral.ui.single-gunicorn-worker | conforms | No worker changes |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.standards.data-raises-caller-logs, astral.standards.database-header-inventory, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths match none
- astral.debug.spikes-under-debug-dir — paths match none
- astral.docs.features-single-file-per-ticket — layers {docs} ∩ plan empty
- astral.git.engineer-test-tree-ban — paths match none
- astral.layers.scripts-exempt-from-layer-rules — layers ∩ plan empty
- astral.patterns.require-auth-on-protected-endpoints — layers ∩ plan empty
- astral.ui.frontend-file-placement — layers ∩ plan empty
- astral.ui.naming-conventions — layers ∩ plan empty

## Findings

None fix-now.

**discuss (non-blocking):** Files Changed blurb mentions “body-text emptiness” among config runner literals, but Stage 1 only adds schemes / ledger placeholder / debug_func — emptiness is computed via `_body_is_empty`. Binding text is Stage 1; treat the table blurb as descriptive slip, not a missing config key.

**acceptable:** Scope MAJOR-CHANGE / Conf high / Risk Medium honest; mitigations (per-message try/except, unknown-age no-trash, available_count=1 vs live inbox count, forbid global AST-1061 helpers) are specific. `freq_hrs=0` → due every AUTO tick is intentional with runner listing once per fire.

**R6:** Definition fidelity pass for runner child. Layer/config/debug/no-daisy-chain/in-scope pass. No shell/Ruth-catalog creep.

context_tokens≈55000

— Joan

#### hedy — 2026-07-31T02:25:42.106Z
Plan: [docs/features/meteorite/ast-1090-gaze-email-runner-bind-route-scrape-dedupe-create-mailbox.md](https://github.com/susansomerset/astral/blob/sub/AST-1087/AST-1090-gaze-email-runner-bind-route-scrape-dedupe-create-mailbox/docs/features/meteorite/ast-1090-gaze-email-runner-bind-route-scrape-dedupe-create-mailbox.md) @ `3ccaf930`

**Scope:** MAJOR-CHANGE — new `gaze_email` core runner + due-path/data helper + Gmail `internal_date_ms` + dispatcher special-case across utils/data/external/core.

**Conf:** high — consumes AST-1088 shell/archive/trash and AST-1089 Ruth contract; reuses inbox From-bind, gazer Playwright fetch, `create_meteorite_job`; per-candidate `job_link` helper avoids AST-1061 global skip (parent Boundaries).

**Risk:** Medium — due wiring / archive-vs-trash branching can no-op or mishandle mailbox; mitigated by per-message try/except, unknown-age no-trash, and all-duplicate archive only after attempted ingest.

#### chuckles — 2026-07-31T02:23:04.550Z
[thread-missing] Hedy engineer Team UUID remapped to live store.db `4b78d50a-11c0-4c02-a2af-e4a793795bd6` (prior mint paths had no store.db on this host). Continuing first-spawn plan-child.

— Chuckles

#### chuckles — 2026-07-31T02:22:06.999Z
[thread-missing] Hedy engineer Team chat store.db absent on this host for prior UUID 6e6cf5b3-4d01-4954-9b0d-632f664135f6; reminted to 1b9a0eda-e179-4763-b764-79716c5d8dca (FQ path under epic chat hash). Continuing with first-spawn plan-child.

— Chuckles

---

# AST-1090 — gaze_email runner — bind, route, scrape, dedupe, create, mailbox outcomes

**Linear:** [AST-1090](https://linear.app/astralcareermatch/issue/AST-1090/gaze-email-runner-bind-route-scrape-dedupe-create-mailbox-outcomes-add)
**Parent:** [AST-1087](https://linear.app/astralcareermatch/issue/AST-1087/add-gaze-email-as-a-dispatch-task) — Add gaze_email as a dispatch task
**Publish ref:** `origin/sub/AST-1087/AST-1090-gaze-email-runner-bind-route-scrape-dedupe-create-mailbox`

Core runner for the null-`candidate_id` `gaze_email` `dispatch_task` row (shell from AST-1088): list Astral inbox, From→candidate bind, unbound age→Trash, bound shape routing, Ruth `parse_meteorite_email` with the bound candidate’s API key (AST-1089), Playwright scrape, **per-candidate** job_link dedupe, `create_meteorite_job` → **METEORITE_NEW**, archive on success **or** all-duplicate skip, Style D when `debug=True`. Wire due-task + `_dispatch_one` so the null-entity shell fires under normal AUTO dispatch. Does **not** own config shell / Gmail archive-trash capability / Ruth TASK_CONFIG (siblings). Does **not** run qualify/GDL in the same hop.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Extend `GAZE_EMAIL_CONFIG` with runner literals (subject-URL schemes, body-text emptiness, ledger placeholder candidate id, Style D func name); inventory comment | utils |
| `src/data/database.py` | Due-path special-case for `gaze_email`; `job_link_exists_for_candidate` (per-candidate exact link) | data |
| `src/external/gmail.py` | Add `internal_date_ms` on list metadata (Gmail `internalDate`) for retention age | external |
| `src/core/gaze_email.py` | **New** — async mailbox runner: list → bind → route → Ruth/scrape/dedupe/create → archive/trash + Style D | core |
| `src/core/dispatcher.py` | Route `gaze_email` in `_dispatch_one` / eligibility; skip candidate-API-key gate; call runner (not `_run_unified`) | core |

No `tests/` / bible / React / Ruth `agent_task.json` / Manage Email UI. Do **not** edit AST-1088/1089 plan docs. Do **not** call global `job_link_exists` / `text_matches_known_company_job_id` on this path (parent Boundaries — per-candidate dedupe only).

## Stage 1: Config runner literals + per-candidate link helper + list `internalDate`

**Done when:** `GAZE_EMAIL_CONFIG` exposes runner keys below; `database.job_link_exists_for_candidate` scopes exact `job_link` to that candidate’s meteorite company; `list_inbox_messages` rows include `internal_date_ms`; no dispatcher/runner yet.

1. In `src/utils/config.py`, extend the existing `GAZE_EMAIL_CONFIG` dict (do **not** invent a second config block) with:

```python
    # AST-1090 runner — subject-is-URL detection (urlparse.scheme).
    "subject_url_schemes": ("http", "https"),
    # Ledger / registry placeholder when dispatch_task.candidate_id is NULL.
    "dispatch_ledger_candidate_id": "",
    # Style D func= string for the runner.
    "debug_func": "gaze_email.run",
```

Keep existing keys (`task_key`, `account_address`, `unbound_retention_days`, `auto_mode`, `min_count`, `batch_size`, `freq_hrs`, `entity_type`, `trigger_state`) unchanged. Assert:

```python
assert set(GAZE_EMAIL_CONFIG["subject_url_schemes"]) == {"http", "https"}
assert GAZE_EMAIL_CONFIG["debug_func"] == "gaze_email.run"
```

Update the inventory comment line for `GAZE_EMAIL_CONFIG` to mention runner literals (AST-1090).

⚠️ **Decision — extend `GAZE_EMAIL_CONFIG`, do not add `GAZE_EMAIL_RUNNER_CONFIG`:** Parent already owns account/retention/task_key in that block; runner thresholds that are product policy live beside them. Ruth task key / parse modes stay in `METEORITE_EMAIL_PARSE_CONFIG`. Scrape concurrency / min JD chars stay in `METEORITE_EMAIL_INGEST_CONFIG` (reuse).

2. In `src/data/database.py`, near `job_link_exists`, add:

```python
def job_link_exists_for_candidate(candidate_id: str, job_link: str) -> bool:
    """True when a job under this candidate's meteorite company has this exact job_link."""
```

Concrete SQL:

- Resolve `company = METEORITE_CONFIG["short_name_template"].format(candidate_id=candidate_id)` (import `METEORITE_CONFIG` — data already imports config elsewhere).
- `SELECT 1 FROM job WHERE company = ? AND job_link = ? AND job_link IS NOT NULL AND TRIM(job_link) != '' LIMIT 1`.
- Empty `candidate_id` / empty `job_link` → `False` without querying.

⚠️ **Decision — per-candidate exact link only:** Parent AC5 + Boundaries forbid applying AST-1061 global `job_link_exists` across candidates on this path. Same URL for two candidates → both may create. Same candidate + same link → skip. Do **not** use `text_matches_known_company_job_id` here.

3. In `src/external/gmail.py`:

- Extend `GmailInboxMessage` with `internal_date_ms: int` (Gmail `internalDate` as int milliseconds since epoch; `0` if missing/unparseable).
- In `_message_metadata`, read `raw.get("internalDate")` (string or int from API) → int ms.
- Ensure `list_inbox_messages` metadata `get` still requests enough fields for `internalDate` (message resource `internalDate` is returned on metadata format without extra headers).

**Done when (recheck):** `python3 -c` imports the new config keys + helper; `GmailInboxMessage` typing includes `internal_date_ms`; `python3 -m py_compile` on the three files succeeds.

## Stage 2: Due-task + `_dispatch_one` wiring for null-candidate `gaze_email`

**Done when:** AUTO tick can select the provisioned null-candidate `gaze_email` row; `_dispatch_one` does not require a candidate API key for that key; one batch calls the Stage 3 runner and updates `last_run_at`.

1. In `src/data/database.py` `count_eligible_for_dispatch_task`, **before** the early `if not entity_type or not state or not candidate_id: return 0`:

```python
tk = (task.get("task_key") or "").strip()
if tk == GAZE_EMAIL_CONFIG["task_key"]:
    return _gaze_email_available_count(task)
```

Implement `_gaze_email_available_count(task) -> int`:

- Import `GAZE_EMAIL_CONFIG`.
- `freq = float(task.get("freq_hrs") or 0)`.
- If `freq > 0` and `last_run_at` is present and newer than `freq` hours (parse ISO/`%Y-%m-%d %H:%M:%S` the same way other dispatch time helpers do — reuse an existing parser if one exists beside inflow eligibility; otherwise `datetime.fromisoformat` with space→`T` fallback): return `0`.
- Else return `1`.

⚠️ **Decision — available_count=1 when due, not live inbox size:** Counting inbox every tick would hit Gmail on every scheduler wake. The runner lists inbox itself; tick only needs a due signal. `freq_hrs=0` (seeded) → due every tick when AUTO.

2. In `get_due_tasks`, change the skip gate:

```python
tk = (task.get("task_key") or "").strip()
if tk == GAZE_EMAIL_CONFIG["task_key"]:
    avail = count_eligible_for_dispatch_task(task)
    if avail >= (task.get("min_count") or 1):
        task["available_count"] = avail
        due.append(task)
    continue
if not et or not ts or not cid:
    continue
```

3. In `src/core/dispatcher.py` `_dispatch_one`:

- Immediately after reading `task_key` / `candidate_id`, if `task_key == GAZE_EMAIL_CONFIG["task_key"]`:
  - Do **not** call `database.get_candidate` / do **not** require `candidate_api_key`.
  - Build `ctx = {"gaze_email": True}` (or empty dict — runner loads per-message candidate ctx itself).
  - Set `debug` the same way as today.
  - Write ledger with `candidate_id=GAZE_EMAIL_CONFIG["dispatch_ledger_candidate_id"]` (empty string) when writing the batch ledger (same `entity_batch_id` pattern); `entity_type=None` is fine.
  - Await a single call: `summary = await run_gaze_email(task, debug=debug)` (import from `src.core.gaze_email`).
  - Map summary into `accumulated` (`total_processed` / `total_passed` / `total_failed` / `total_errors` — define keys in Stage 3 return).
  - Update ledger + `last_run_at` in the existing `finally` path.
  - **Return** — do **not** enter `_run_dispatch_loop` / `_run_unified`.

- Leave all other task keys on the existing path.

4. In `_debug_log_auto_off_stage_skips` and any other gate that requires `entity_type`+`trigger_state`+`candidate_id`, do **not** add `gaze_email` to stage-key frozensets unless needed — mailbox shell is not a candidate-stage row.

5. Stub `src/core/gaze_email.py` with:

```python
async def run_gaze_email(task: dict, *, debug: bool = False) -> dict[str, int]:
    """AST-1090: process Astral inbox for the null-candidate gaze_email dispatch row."""
    return {"total_processed": 0, "total_passed": 0, "total_failed": 0, "total_errors": 0}
```

Stage 3 replaces the stub body. Stage 2 may land the stub so dispatcher imports resolve.

**Done when (recheck):** With a provisioned null `gaze_email` row, `get_due_tasks()` includes it when `freq` allows; `_dispatch_one` for that task_id does not log “no candidate or API key”; stub runner returns zeros and `last_run_at` updates.

## Stage 3: Runner — bind, route, Ruth, scrape, dedupe, create, mailbox + Style D

**Done when:** `run_gaze_email` implements parent Functional scope shapes 3.1–3.4 + unbound trash + all-duplicate archive + Style D; lands jobs only in **METEORITE_NEW** via `create_meteorite_job`; never calls qualify/GDL.

### 3.0 Module layout (`src/core/gaze_email.py`)

Imports (allowed directions):

- `src.core.inbox`: `list_inbox_messages`, `get_message_html` (reuse bind enrichment on list).
- `src.core.candidate`: `get_candidate` (API key ctx for Ruth).
- `src.core.agent`: `do_task`.
- `src.core.meteorite`: `create_meteorite_job`.
- `src.core.gazer`: `_meteorite_fetch_link_visible_text` (existing Playwright helper — reuse, do not copy).
- `src.data.database`: `job_link_exists_for_candidate`.
- `src.external.gmail`: `archive_message`, `trash_message` (core→external allowed).
- Config: `GAZE_EMAIL_CONFIG`, `METEORITE_EMAIL_PARSE_CONFIG`, `METEORITE_EMAIL_INGEST_CONFIG`.
- Logging: `get_logger`, `truncate_debug_content` as needed.

Public entry: `async def run_gaze_email(task: dict, *, debug: bool = False) -> dict[str, int]`.

### 3.1 List + optional account diagnostic

1. `messages = list_inbox_messages(debug=debug)` (already binds `candidate_match` via From).
2. If `debug=True` and `os.environ.get("GMAIL_USER")` casefold-compare ≠ `GAZE_EMAIL_CONFIG["account_address"]` casefold: one Style D detail line `account_mismatch` — do **not** abort (1088 decision: environ owns live mailbox).
3. Counters: `processed`, `passed` (archived or intentionally ignored-without-error), `failed`, `errors`.
4. For each message index `i` in `1..N` (`N=len(messages)`), run 3.2–3.5. Catch unexpected exceptions per message: increment `errors`, Style D `outcome=error`, continue (do not abort the whole batch).

### 3.2 Helpers (module-private)

```python
def _subject_is_url(subject: str) -> bool:
    # strip; urlparse; scheme in GAZE_EMAIL_CONFIG["subject_url_schemes"] and netloc non-empty

def _body_text(html_body: str) -> str:
    # BeautifulSoup get_text(" ", strip=True) — lazy-import bs4 like inbox.strip_extract

def _body_is_empty(html_body: str) -> bool:
    return not _body_text(html_body)

def _unbound_is_stale(internal_date_ms: int, *, now_ms: int) -> bool:
    days = int(GAZE_EMAIL_CONFIG["unbound_retention_days"])
    if internal_date_ms <= 0:
        return False  # unknown age → leave untouched (same spirit as "newer than window")
    age_ms = now_ms - internal_date_ms
    return age_ms > days * 24 * 60 * 60 * 1000
```

⚠️ **Decision — unknown `internal_date_ms` does not trash:** Prefer leave-inbox over accidental Trash when Gmail omits the field.

### 3.3 Unbound path

For each list row:

- `match = msg["candidate_match"]` (from inbox list).
- If not `match["matched"]`:
  - If `_unbound_is_stale(msg["internal_date_ms"], now_ms=...)`: `trash_message(msg["id"])`; Style D `outcome=trashed`; `processed+=1`; `passed+=1`.
  - Else: Style D `outcome=ignored-unbound`; leave inbox; `processed+=1`; `passed+=1`.
  - Continue (no create).

### 3.4 Bound shape routing

`cid = match["astral_candidate_id"]`. Load `ctx = get_candidate(cid)`; if missing or no `candidate_api_key`: Style D `outcome=error` / `failed+=1`; leave inbox (do not trash/archive).

Fetch full payload: `payload = get_message_html(msg["id"])`.
`subject = (payload["subject"] or "").strip()`
`html = payload["html_body"] or ""`
`empty_body = _body_is_empty(html)`

Shape table (execute exactly one branch):

| Condition | Action |
|-----------|--------|
| `not subject` and `not empty_body` | **html_links** — Ruth `PARSE_MODE: html_links` + HTML; for each `jobs[].job_link`: scrape → per-cand dedupe → create; then mailbox finalize |
| `subject` and `_subject_is_url(subject)` and `empty_body` | **subject_url** — scrape `subject` as URL (no Ruth); dedupe → create; finalize |
| `subject` and `not empty_body` | **subject_body** — Ruth `PARSE_MODE: subject_body` + `SUBJECT:` line + HTML; if `jd_link`: scrape, append subject+body text to scraped JD; elif `content_text` (or subject+body text): create with that JD / `job_link=None`; finalize |
| `subject` and `not _subject_is_url(subject)` and `empty_body` | **ignore** — leave inbox; Style D `outcome=ignored`; no create |

⚠️ **Decision — “no subject + pure HTML” ≡ empty/whitespace subject + non-empty HTML body text or tags:** Parent’s “pure HTML” means the body carries HTML content with no useful subject. Use `not subject.strip()` + `not _body_is_empty(html)`. If both subject and body empty → treat as **ignore** (leave inbox).

⚠️ **Decision — subject+body with URL subject still uses subject_body Ruth path when body non-empty:** Parent lists “subject is URL + no body” separately; if body has text, use the subject+body branch (Ruth may still return `jd_link`).

### 3.5 Ruth call contract (bound html_links / subject_body)

```python
modes = METEORITE_EMAIL_PARSE_CONFIG["parse_modes"]  # ("html_links", "subject_body")
# live_content:
#   PARSE_MODE: html_links\n\n{html}
#   PARSE_MODE: subject_body\nSUBJECT: {subject}\n\n{html}
resp = await do_task(
    task_key=METEORITE_EMAIL_PARSE_CONFIG["task_key"],
    live_content=live,
    index=msg["id"],
    ctx=ctx,  # must include candidate_api_key
    debug=debug,
)
```

Parse `resp` fields per AST-1089 schema (`parse_mode`, `jobs`, optional `jd_link`, `content_text`). On Ruth failure / invalid shape: Style D `outcome=error`; leave inbox; `errors+=1`; do not archive.

### 3.6 Scrape + per-candidate dedupe + create

Shared helper `_ingest_link(cid, url, *, jd_suffix: str | None, debug) -> "created"|"skipped"|"error"`:

1. `text, final_url = await _meteorite_fetch_link_visible_text(url, debug=debug)`.
2. `link = (final_url or url).strip()`.
3. If `job_link_exists_for_candidate(cid, link)`: return `"skipped"` (Style D `skipped-duplicate`).
4. If `len(text.strip()) < METEORITE_EMAIL_INGEST_CONFIG["min_jd_chars"]`: return `"skipped"` (`skipped-short`) — do **not** create.
5. `jd = text` if not `jd_suffix` else `f"{text.rstrip()}\n\n{jd_suffix.lstrip()}"`.
6. `create_meteorite_job(cid, jd, job_link=link, debug=debug)` → `"created"`.

For **subject_url** branch: one `_ingest_link` with `jd_suffix=None`.

For **html_links**: iterate `jobs` list; skip entries with empty `job_link`; gather created/skipped counts.

For **subject_body**:

- If `jd_link` non-empty: `_ingest_link(..., jd_suffix=f"SUBJECT: {subject}\n\n{_body_text(html)}")` (parent: append email subject + body to scraped JD).
- Elif usable `content_text` or `f"{subject}\n\n{_body_text(html)}"` meets `min_jd_chars`: if creating **without** link, skip only when… **no link-based dedupe** — always `create_meteorite_job(cid, jd, job_link=None)` (AC5 is link-scoped). Style D `recorded`.
- Else: treat as no actionable JD → do **not** archive; Style D `ignored-empty`; leave inbox.

⚠️ **Decision — do not call `ingest_meteorite_jobs_from_email_html`:** That helper uses **global** `job_link_exists` + `text_matches_known_company_job_id`, which violate parent Boundaries for `gaze_email`. Reuse only Playwright fetch + `create_meteorite_job`.

⚠️ **Decision — no daisy-chain:** Never call `qualify_meteorite`, GDL, or transition out of `METEORITE_CONFIG["job_create_state"]` in this runner. `create_meteorite_job` already lands **METEORITE_NEW**.

### 3.7 Mailbox finalize (archive / leave)

After a bound **actionable** branch (html_links / subject_url / subject_body that attempted ≥1 create-or-skip decision):

- If at least one `"created"` **or** all attempted links/jobs were `"skipped"` (all-duplicate / short) and there was ≥1 attempt: `archive_message(msg["id"])`; Style D `outcome=archived` (detail `created=N skipped=M`).
- If Ruth returned zero jobs / no jd_link / no usable content (nothing to attempt): leave inbox; `ignored-empty`.
- **ignore** shape (non-URL subject + empty body): never archive.
- Unbound trash already handled in 3.3.

Parent AC5: “if a bound message produces only such skips, the message is still **archived**.”

### 3.8 Style D

When `debug=True` only (`logger.set_debug_flag(True)`):

- Per message: `debug_index(func=GAZE_EMAIL_CONFIG["debug_func"], index=i, total=N, identifier=message_id[:80], outcome=...)`.
- Outcomes used: `found`, `trashed`, `ignored-unbound`, `ignored`, `ignored-empty`, `archived`, `skipped-duplicate`, `skipped-short`, `recorded`, `error`.
- Detail lines: `  |  ` via `debug_detail` — from_address, astral_candidate_id, shape name, job_link truncated, astral_job_id. Truncate long HTML with `truncate_debug_content`.
- When `debug=False`: no new debug_index/detail from this module.

### 3.9 Return summary

```python
return {
    "total_processed": processed,
    "total_passed": passed,
    "total_failed": failed,
    "total_errors": errors,
}
```

`_dispatch_one` maps these into ledger accumulated fields (same keys as other runners).

**Done when (recheck):** Manual reasoning against AC1–7 covered by branches above; `python3 -m py_compile src/core/gaze_email.py src/core/dispatcher.py` succeeds; no imports of qualify/GDL on this path.

## Execution contract

- Stages in order; one commit per stage on epic worktree sub; publish to `origin/<publish-ref>` after each stage per build-child.
- No files outside the Files Changed table.
- Ambiguity or codebase drift → stop and comment on **parent** AST-1087 with the Stage N blocked template.
- Do not invent AUTO subtype, Manage Email UI, attachments, permanent Gmail delete, or global job_link skip.

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — new core runner module plus due-path/data helper, Gmail list metadata, and dispatcher special-case across utils/data/external/core.

**Conf:** `high` — reuses AST-1088 shell + archive/trash, AST-1089 Ruth contract, inbox From-bind, gazer Playwright fetch, `create_meteorite_job`; due-path special-case is localized; per-candidate link helper mirrors `job_link_exists` with company scope.

**Risk:** `Medium` — wrong due wiring could no-op or tick-storm Gmail; wrong archive/trash branching could trash bound mail or leave duplicates forever; Ruth/Playwright failures must leave mail in inbox (specified). Mitigation: per-message try/except, unknown-age no-trash, all-duplicate archive only after attempted ingest.

## Self-review vs ASTRAL_CODE_RULES

- **§2.1 / config-source-of-truth:** Retention, task key, URL schemes, debug func in `GAZE_EMAIL_CONFIG`; Ruth key/modes in `METEORITE_EMAIL_PARSE_CONFIG`; scrape thresholds in `METEORITE_EMAIL_INGEST_CONFIG`.
- **§2.1 / secrets-and-env-specific-from-environ:** Gmail secrets untouched; candidate API key from candidate row via `do_task` + `requires_candidate_key`.
- **§2.5 / core-vs-external:** List/get via inbox wrappers; archive/trash I/O only in `gmail.py`; policy in `gaze_email.py`.
- **§2.6 / no-daisy-chain:** Create stops at **METEORITE_NEW**.
- **§1.4 / no-hardcoded-sets:** No inline retention days / task keys / scheme tuples outside config.
- **§3.3 imports:** core←data/utils/external/core peers as existing patterns; no UI.
- **debug-contract-gated:** Style D only when `debug=True`.
- **in-scope-only:** No Ruth catalog edits, no schema shell rework, no qualify/GDL, no Manage Email redesign, no global AST-1061 dedupe on this path.
- **No conflict requiring conf-!!-NONE.**

## Review

**Publish ref:** `origin/sub/AST-1087/AST-1090-gaze-email-runner-bind-route-scrape-dedupe-create-mailbox`
**Tip:** `0966f52b`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `a5581978` | GAZE_EMAIL_CONFIG runner literals + per-cand link helper + internalDate |
| 2 | `88f96e2b` | due-task + `_dispatch_one` gaze_email wiring + stub |
| 3 | `0966f52b` | gaze_email runner bind/route/Ruth/scrape/dedupe/mailbox + Style D |

## Review (Radia — code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1090
**Publish ref tip (at review):** `cb049bd47bf31da0a90865dfecc685bbecd0d97a`
**Overall:** CLEAN

### What’s solid

- Stages 1–3 match plan: runner literals + per-cand `job_link_exists_for_candidate` + `internalDate`; due/`_dispatch_one` gaze special-case (`available_count=1` via freq); bind/route/Ruth/`create_meteorite_job`/archive-trash + Style D gated on `debug=True`.
- No qualify/GDL; no global AST-1061 `job_link_exists` on this path; archive on create or all-skip.
- Betty `test` + one `merge-tests(AST-1090)` SHA on the sub.

### Issues

**discuss (straggler):** Joan Excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`; three-dot tip includes `docs/features/**` + Betty test-tree so sweep scores them in-scope (all still **conforms**).

**advisory:** `from src.core.gaze_email import run_gaze_email` inside `_dispatch_one` has no lazy-import comment; matches other late imports in the same file. Stale ensure docstring still says runner unwired (AST-1088 text).

### Recommended actions

None for fix-now.

### Statutes checked (summary)

56 active statutes swept vs `origin/dev...origin/sub/AST-1087/AST-1090-…`. No violates. Full table in Linear review comment.

## Resolution

**2026-07-31** — `resolve(AST-1090)` after Radia CLEAN (`11ffdedd`).

| Finding | Action |
|---------|--------|
| fix-now | none |
| discuss (Joan straggler Excluded vs tip paths) | no product change — sweep scoring note only |
| advisory — late `run_gaze_email` import lacks comment | added `# late: keep gaze_email off module-top load` above the import in `_dispatch_one` |
| advisory — `ensure_gaze_email_dispatch_task` docstring still said runner unwired | docstring now points at AST-1090 due/`_dispatch_one` wiring |
