<!-- linear-archive: AST-1061 archived 2026-08-07 -->

## Linear archive (AST-1061)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1061/gazer-email-meteorite-jobs-playwright-dedupe-qualify-meteorite  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1058 — Qualify Meteorite  
**Blocked by / blocks / related:** parent: AST-1058; blocks: AST-1062

### Description

## What this implements

Owns gazer email→meteorite create: interpret JD body / recruiter forward / single link / link list; Playwright visible-text fetch for links; post-fetch external job-id dedupe (skip known); insert into **METEORITE_NEW**. Introduces the **gazer reads email** new-pattern (Archie-flagged). Does **not** own Ruth qualify apply or GDL.

## Acceptance criteria

- [X] 1. Gazer can create meteorite jobs from email contents that are a JD body, a recruiter forward, a single job link, or a list of job links; when links are present, Playwright fetches visible text **before** create.
- [X] 2. After Playwright (when used), create is **skipped** when a known external job-id pattern match hits — no second job row for that id.
- [X] 3. New jobs from this path land on **METEORITE_NEW** with JD text and without Ruth metadata (pre-AI).
- [X] 4. Non-meteorite `qualify_job_listings` / scrape / GDL paths unchanged (smoke).
- [X] 5. With `debug=True` on touched ingest/qualify paths, Style D index + `|` detail shows found vs recorded; with `debug=False`, no new debug-contract lines from those paths. (ingest half)

## Boundaries

Does **not** own Ruth qualify apply or GDL. After AST-1060. Sibling Hedy owns qualify_meteorite batch apply.

## In scope

- [X] `pattern.layers.import-discipline` — gazer/inbox/meteorite/core vs ui/api edges
- [X] `astral.layers.core-vs-external-bright-line` — Playwright only via `src.external.playwright.get_visible_text`; Gmail stays inbox/external
- [X] `astral.standards.debug-contract-gated` — Style D on gazer + inbox ingest when `debug=True` only
- [X] `astral.config.config-source-of-truth` — `METEORITE_EMAIL_INGEST_CONFIG` owns link filters / concurrency / min JD length
- [X] gazer-reads-email (new-pattern) — classify + Playwright + dedupe live in `src/core/gazer.py`
- [X] Data helpers: global inverted `company_job_id` match + exact `job_link` existence
- [X] Optional `job_link=` on `create_meteorite_job`; Manage Email Create multi-result API/UI

## Considered but excluded

- [X] Ruth `qualify_meteorite` apply / UUID persist — AST-1062 (`consult` / apply)
- [X] METEORITE_QUALIFIED / qualify TASK_CONFIG / dispatch — AST-1060 (already landed)
- [X] Writing `company_job_id` on create from URL parsers — Ruth enrichment owns UUID
- [X] New dispatcher AUTO unread-mail poll — Create is the operator entry
- [X] `tests/` / `docs/test-bible/**` — Betty after Code Complete
- [X] Non-meteorite `process_gazer_batch` / listing scrape / GDL priors — AC4 smoke = no edits

## Notes for planning

Plan: `docs/features/meteorite/ast-1061-gazer-email-meteorite-jobs-playwright-dedupe.md` on publish ref.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1058-qualify-meteorite`, child `sub/AST-1058/AST-1061-gazer-email-meteorite-jobs-playwright-dedupe`. Created at dispatch-parent.

### Comments

#### chuckles — 2026-07-31T00:13:04.217Z
[check-linear] answered

There is no `gaze_email` dispatch task — by design. Roster `gaze` is company culture gaze only. Meteorite email ingest is **operator Create** on Admin → **Manage Email**: `POST /api/admin/inbox/messages/<id>/create-job` → strip/extract → `ingest_meteorite_jobs_from_email_html` → `METEORITE_NEW` (Playwright + dedupe). No AUTO unread-mail poll / no new TASK_CONFIG key.

Gmail is **not** labeled, archived, or marked processed after Create — that was explicitly out of scope on the Create ticket. Deduping is on job identity (`company_job_id` / `job_link`), not on the email message.

— Chuckles

#### susan — 2026-07-31T00:01:04.821Z
@chuckles How does gaze_email get set up?  It should be a task that can be added to dispatch, right?  I only see "gaze".  Also, how does an email get modified to indicate that the system has already processed it?

#### radia — 2026-07-30T01:53:56.830Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1061
**Publish ref:** `b6f80a7e5015513dd6f3cf0c8429035fabb1958f` (`origin/sub/AST-1058/AST-1061-gazer-email-meteorite-jobs-playwright-dedupe`)
**Overall:** DISCUSS

**Diff:** `origin/dev...origin/sub/AST-1058/AST-1061-gazer-email-meteorite-jobs-playwright-dedupe` — layers `{core, data, docs, ui, utils}` (includes stacked AST-1060).
**This ticket owns:** `METEORITE_EMAIL_INGEST_CONFIG`; `text_matches_known_company_job_id` / `job_link_exists`; optional `job_link` on `create_meteorite_job`; gazer email ingest (Playwright + dedupe); inbox/API/Manage Email multi-result Create + Style D ingest half.

## Statutes checked

| id | tier | verdict | one-line |
| -- | -- | -- | -- |
| `astral.agent.confidence-bounds` | scoped | conforms | No graded consult / confidence path |
| `astral.agent.do-task-delegation` | scoped | conforms | Playwright via external only; no do_task/Ruth |
| `astral.agent.grade-vector-validation` | scoped | conforms | No grade vectors |
| `astral.batch.batch-id-first` | scoped | conforms | Create/ingest; no new claim APIs |
| `astral.batch.batch-id-format` | scoped | conforms | Untouched |
| `astral.batch.claim-process-release` | scoped | conforms | Create/ingest not claim→process→release |
| `astral.batch.entity-agent-responses-latest-only` | scoped | conforms | Untouched |
| `astral.config.config-source-of-truth` | scoped | conforms | Link filters/concurrency/min JD in METEORITE_EMAIL_INGEST_CONFIG |
| `astral.config.pass-threshold-vs-score-floor` | scoped | conforms | No score_floor/pass_threshold on 1061 path |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | conforms | No secrets/env |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | paths miss (artifacts/**, scripts/spikes/**) |
| `astral.debug.spikes-under-debug-dir` | scoped | conforms | Plan under docs/features/; no spikes |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | Single AST-1061 plan (+ stacked 1060 plan) |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty test()/merge-tests; engineer code() owns src+features |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | test() owns tests/bible; engineer code() product only |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | Playwright only via get_visible_text; no new PW in core |
| `astral.layers.import-direction` | scoped | conforms | UI→core inbox; gazer→external/data; no UI→data |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | layers/paths miss (scripts) |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | Toast counts from API created/skipped; no React business rules |
| `astral.patterns.coat-check-never-store-empty` | scoped | conforms | Untouched |
| `astral.patterns.render-verdict-orchestrates-consult` | scoped | conforms | Untouched |
| `astral.patterns.require-auth-on-protected-endpoints` | scoped | conforms | Existing Create endpoint auth unchanged |
| `astral.standards.data-raises-caller-logs` | scoped | conforms | Data helpers query-only; logging in core |
| `astral.standards.database-header-inventory` | scoped | conforms | Existing job columns only; no new tables |
| `astral.standards.debug-contract-gated` | scoped | conforms | Style D on gazer+inbox when debug=True only |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | Reuses create_meteorite_job / get_visible_text / AST-80 LIKE |
| `astral.standards.in-scope-only` | scoped | conforms | No qualify apply / GDL; boundaries held |
| `astral.standards.logging-via-utils` | scoped | conforms | get_logger + Style D helpers |
| `astral.standards.no-cross-contamination` | scoped | conforms | Meteorite email ingest isolated from listing scrape |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | Exclude substrings / schemes / caps in config |
| `astral.standards.public-then-helpers` | scoped | conforms | Public ingest + private helpers match gazer style |
| `astral.standards.utils-data-late-import-only` | scoped | conforms | Config-only utils; no utils→data |
| `astral.state.core-decides-transitions` | scoped | conforms | Create still lands METEORITE_NEW via create path |
| `astral.state.job-prior-states-enforced` | scoped | conforms | No JOB_STATES edits on 1061 path |
| `astral.state.no-daisy-chain-in-run` | scoped | conforms | No multi-state hop in one run |
| `astral.ui.frontend-file-placement` | scoped | conforms | Edits flat AdminManageEmail.tsx |
| `astral.ui.naming-conventions` | scoped | conforms | No new routes/components rename |
| `astral.ui.single-gunicorn-worker` | scoped | conforms | Untouched |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | Single merge-tests(AST-1061) onto tip |
| `orch.git.commit-vocabulary` | universal | conforms | docs/code/test/merge-tests vocabulary |
| `orch.git.flow-direction-inviolable` | universal | conforms | Work on sub/* only |
| `orch.git.ftr-sub-topology` | universal | conforms | sub/AST-1058/AST-1061-… |
| `orch.git.merge-on-checkout` | universal | conforms | No conflicting checkout rewrite |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | No rewrite ops |
| `orch.git.no-dev-agent-branches` | universal | conforms | Ticket sub publish-ref |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | astral-AST-1058 |
| `orch.git.three-permanent-branches` | universal | conforms | No new permanent branches |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | False-positive Medium risk disclosed; no open blocker |
| `orch.pipeline.plan-is-bible` | universal | conforms | Stages 1–4 match tip |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Astral Meteorite child |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Tests Passed → review-child |
| `orch.roles.archie-approves-statutes` | universal | conforms | No canon/statutes edits |
| `orch.roles.betty-owns-test-tree` | universal | conforms | Betty owns tests/bible |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | Assignee Katherine |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Assignee remains Katherine |
| `orch.roles.pre-commit-path-bans` | universal | conforms | Role-appropriate paths per vocabulary |

## Pattern conformance

- `pattern.layers.import-discipline` — conforms (gazer/inbox/meteorite/core vs ui/api)
- gazer-reads-email (new-pattern) — conforms (classify + Playwright + dedupe in gazer.py)
- Cited statutes covered in Statutes checked

## Plan adherence

Stages 1–4 match tip: config + dedupe helpers; optional job_link; gazer ingest; inbox/API/UI multi-result. Self-Assessment MAJOR-CHANGE matches footprint. Boundaries held vs AST-1062 qualify apply / AST-1060 (stacked, not re-owned). Non-meteorite process_gazer_batch untouched.

## Findings

### fix-now
(none)

### discuss
1. **straggler ×3** — Joan excluded at plan time; in-scope on three-dot vs `origin/dev` via plan docs + Betty tests/bible (all substance **conforms**):
   - `astral.debug.spikes-under-debug-dir`
   - `astral.docs.features-single-file-per-ticket`
   - `astral.git.engineer-test-tree-ban`

### advisory
- Joan’s non-blocking global inverted-id false-positive risk remains a watch item (plan Self-Assessment Medium); exact `job_link` gate mitigates re-ingest.

### What’s solid
- Config-driven link filters; Style D gated; Playwright only via external; Create 201/200 + multi-result toasts.

### Recommended actions
- Katherine: acknowledge stragglers → resolve-child → User Testing.

**Notes:** Joan plan-rubric APPROVED. Docs append @ `b6f80a7e`. Product tip before docs: `259ebb33`.

context_tokens≈32000

#### betty — 2026-07-30T01:47:53.405Z
## QA test manifest — AST-1061

**Publish:** `origin/sub/AST-1058/AST-1061-gazer-email-meteorite-jobs-playwright-dedupe` @ `259ebb336d4265633f7f21e4ee47071d3a5bbcde`
**Betty delivery:** `merge-tests(AST-1061): origin/tests 598760d9da2956bd8b9dd06cdaf4cefc9fd7346f`
**FIX-UAT:** ftr bible delta vs `origin/tests` was `core/tracker.md` only (−2) — no full bible re-read; component greps + additive `### AST-1061` blocks.

### 1. Covered paths
1. `METEORITE_EMAIL_INGEST_CONFIG` — `TestAst1061MeteoriteEmailIngestConfig`
2. `text_matches_known_company_job_id` / `job_link_exists` — `TestAst1061MeteoriteEmailDedupeHelpers`
3. `create_meteorite_job(..., job_link=)` persist + `company_job_id is None` — `TestAst1042CreateMeteoriteJob`
4. Gazer ingest body/links/Playwright mock/dedupe/Style D — `TestAst1061MeteoriteEmailIngest`
5. Inbox Create → `ingest_meteorite_jobs_from_email_html_sync` — revised `TestAst1049CreateMeteoriteJobFromInboxMessage`
6. API 201 created / 200 all-skipped — revised `TestAst1049InboxCreateJobApi`
7. Manage Email multi-result toasts — revised `test_AdminManageEmail.test.tsx`

### 2. Broken / obsolete (revised)
- AST-1049 inbox mocks of `create_meteorite_job` → gazer ingest sync
- Create-job API single-job payload → `created`/`skipped`/`mode` + 200 skip path
- Manage Email toast mocks include `created`/`skipped` (+ all-skipped case)

### 3. Run
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1061MeteoriteEmailIngestConfig \
  tests/component/data/database/test_jobs.py::TestAst1061MeteoriteEmailDedupeHelpers \
  tests/component/core/test_meteorite.py::TestAst1042CreateMeteoriteJob \
  tests/component/core/test_gazer.py::TestAst1061MeteoriteEmailIngest \
  tests/component/core/test_inbox.py::TestAst1049CreateMeteoriteJobFromInboxMessage \
  tests/component/ui/api/test_api_inbox.py::TestAst1049InboxCreateJobApi \
  -q

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminManageEmail.test.tsx
```

### 4. Bible shasums on publish tip
- `docs/test-bible/utils/config.md` `c42ee2f731a5247a4f41028d2cd3f032f128973a`
- `docs/test-bible/data/database/jobs.md` `83343cf05286e8026fa87a95e98d317b39832151`
- `docs/test-bible/core/meteorite.md` `a4accbfc2b3e467bc2616c7be864ed833fd9688e`
- `docs/test-bible/core/gazer.md` `2beea5e51c6a2d20abe7ae073435369b4e44b7a2`
- `docs/test-bible/core/inbox.md` `2a1ba94d2d6fb68b94fcc29e9074cfef10aadbb0`
- `docs/test-bible/ui/api/api_inbox.md` `7cf7e26f6646b4a4210d376c94649ba0361b450e`
- `docs/test-bible/frontend/pages.md` `aa02b0892aa8f958a8cb31bb96a1c479934d2ed8`

#### joan — 2026-07-30T01:36:11.014Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1061
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1058/AST-1061-gazer-email-meteorite-jobs-playwright-dedupe`
**Plan:** `docs/features/meteorite/ast-1061-gazer-email-meteorite-jobs-playwright-dedupe.md`

## Traceability

### Parent AC → plan stages

| Parent AC (AST-1058) | Plan coverage |
| --- | --- |
| 1. Gazer create from JD body / forward / single link / link list; Playwright before create when links | Stages 3–4 (classify link vs body; links path Playwright; inbox Create wire) |
| 2. After Playwright, skip create on known external job-id | Stages 1 + 3 (`text_matches_known_company_job_id` + `job_link_exists`; skip reasons) |
| 3. Survivors land METEORITE_NEW with JD text, no Ruth metadata | Stages 2–3 (`create_meteorite_job` keeps `company_job_id=None`; optional `job_link`) |
| 4. `qualify_meteorite` batch → METEORITE_QUALIFIED | N/A — boundary (AST-1062; child Boundaries / Out of scope) |
| 5. Meteorite `evaluate_jd` from METEORITE_QUALIFIED only | N/A — boundary (AST-1060) |
| 6. Bogus extracts → METEORITE_FAILED_QUALIFY | N/A — boundary (AST-1062) |
| 7. Non-meteorite qualify/scrape/GDL unchanged | Stage 3 §7 + Stage 4 smoke + Out of scope (no edits) |
| 8. Style D debug gated (ingest/qualify) | Stages 3–4 Style D on gazer + inbox ingest; qualify half N/A (AST-1062) |

### Plan stage → definition

| Stage | Maps to |
| --- | --- |
| 1 Config + data dedupe helpers | Purpose/Functional scope dedupe; child AC2; `METEORITE_EMAIL_INGEST_CONFIG` |
| 2 Optional `job_link` on create | AC3 pre-AI create; link-sourced rows without Ruth UUID |
| 3 Gazer ingest orchestration | Purpose gazer-reads-email; AC1–3; AC5 ingest debug |
| 4 Inbox + API + Manage Email UI | Operator Create entry; multi-result; AC1/4/5 ingest surface |

## Statute verdicts

| id | verdict | one-line |
| --- | --- | --- |
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge / tests SHA work in this plan |
| orch.git.commit-vocabulary | conforms | Plan-only; commit vocab deferred to engineer build |
| orch.git.flow-direction-inviolable | conforms | Uses dispatched `sub/AST-1058/AST-1061-…` publish ref |
| orch.git.ftr-sub-topology | conforms | Child sub under parent ftr topology |
| orch.git.merge-on-checkout | conforms | No git ops in plan; topology assumed |
| orch.git.no-cherry-pick-rebase-force | conforms | No rewrite/cherry-pick proposed |
| orch.git.no-dev-agent-branches | conforms | No agent-named origin branches proposed |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree AST-1058; one child scope |
| orch.git.three-permanent-branches | conforms | Does not invent permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Residual Medium risk disclosed; no open product blocker |
| orch.pipeline.plan-is-bible | conforms | Stages are implementable bible for this child |
| orch.pipeline.project-scoped-queues | conforms | Meteorite project child; no queue invention |
| orch.pipeline.status-gates-skill-entry | conforms | Validated at Plan Ready via validate-plan |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | Explicitly excludes tests/bible (Betty after CC) |
| orch.roles.chuckles-never-ticket-assignee | conforms | Plan does not assign Chuckles to child |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer-owned build after approve |
| orch.roles.pre-commit-path-bans | conforms | No tests/bible/src bans violated by planned paths |
| astral.agent.confidence-bounds | conforms | No graded consult / confidence path touched |
| astral.agent.do-task-delegation | conforms | No `do_task` / Ruth I/O; Playwright via external only |
| astral.agent.grade-vector-validation | conforms | No grade vectors / TASK_CONFIG grades |
| astral.batch.batch-id-first | conforms | No batch claim helpers added |
| astral.batch.batch-id-format | conforms | No batch_id generation |
| astral.batch.claim-process-release | conforms | Create/ingest path, not claim→process→release |
| astral.batch.entity-agent-responses-latest-only | conforms | No agent_data RESPONSE / entity refs |
| astral.config.config-source-of-truth | conforms | Link filters/concurrency/min JD in `METEORITE_EMAIL_INGEST_CONFIG` |
| astral.config.pass-threshold-vs-score-floor | conforms | No score_floor / pass_threshold changes |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets or env-specific literals added |
| astral.git.betty-no-src-or-features | conforms | Engineer src/features plan; not Betty edits |
| astral.layers.core-vs-external-bright-line | conforms | Playwright only via `get_visible_text`; no new PW in core |
| astral.layers.import-direction | conforms | utils/data/core/ui edges respected; UI→core only |
| astral.layers.ui-config-driven-business-logic | conforms | Toast counts from API; no React business rules |
| astral.patterns.coat-check-never-store-empty | conforms | No coat-check keys / empty store |
| astral.patterns.render-verdict-orchestrates-consult | conforms | No consult/render_verdict |
| astral.patterns.require-auth-on-protected-endpoints | conforms | Existing Create endpoint auth unchanged |
| astral.standards.data-raises-caller-logs | conforms | Data helpers query-only; logging in core |
| astral.standards.database-header-inventory | conforms | Uses existing `job` table columns; no new tables |
| astral.standards.debug-contract-gated | conforms | Style D only when `debug=True`; no data-layer contract lines |
| astral.standards.dry-and-focused-functions | conforms | Reuses create/get_visible_text/AST-80 LIKE shape |
| astral.standards.in-scope-only | conforms | Boundaries/out-of-scope exclude qualify/GDL/tests |
| astral.standards.logging-via-utils | conforms | Plan cites `get_logger` / Style D helpers |
| astral.standards.no-cross-contamination | conforms | Stays in layered src paths |
| astral.standards.no-hardcoded-sets | conforms | Exclude substrings / schemes / caps in config |
| astral.standards.public-then-helpers | conforms | Public ingest entry + private helpers; match gazer style |
| astral.standards.utils-data-late-import-only | conforms | Config-only utils touch; no utils→data |
| astral.state.core-decides-transitions | conforms | Create still lands METEORITE_NEW via existing create path |
| astral.state.job-prior-states-enforced | conforms | No JOB_STATES / prior_states edits |
| astral.state.no-daisy-chain-in-run | conforms | No multi-state hop in one run |
| astral.ui.frontend-file-placement | conforms | Edits existing flat `AdminManageEmail.tsx` |
| astral.ui.naming-conventions | conforms | No new routes/components rename |
| astral.ui.single-gunicorn-worker | conforms | No gunicorn / RAILWAY_CONFIG changes |

## Considered and excluded

**Considered:** all rows in Statute verdicts (18 universal + 33 scoped matches).

**Excluded:**
- `astral.debug.no-repo-root-artifacts-dir` — paths `artifacts/**`, `scripts/spikes/**` miss plan Files Changed
- `astral.debug.spikes-under-debug-dir` — paths `debug/**`, `docs/features/**`, `scripts/spikes/**` miss plan Files Changed
- `astral.docs.features-single-file-per-ticket` — layers `docs` miss plan layers; paths miss Files Changed
- `astral.git.engineer-test-tree-ban` — paths `tests/**` / bible miss plan Files Changed
- `astral.layers.scripts-exempt-from-layer-rules` — layers `scripts` / paths `scripts/**` miss plan

## Findings

None fix-now.

- **discuss** (non-blocking): Global inverted `company_job_id` substring match can false-positive on short ids — already called out in Self-Assessment Medium risk/conf; exact `job_link` gate mitigates re-ingest. Accept as implementer watch item, not a plan rewrite.
- **acceptable:** Link-vs-body classify by surviving http(s) hrefs (no NLP forward detector) matches parent shapes and Archie-flagged new pattern already in approved parent definition.

## Checklist (R6)

Definition fidelity: pass. Layer/config/placement/pattern/DRY/self-assessment: pass (MAJOR-CHANGE / Medium / Medium honest).

— Joan
context_tokens≈45000

#### katherine — 2026-07-30T01:33:27.312Z
Plan ready on publish ref.

**Plan:** https://github.com/susansomerset/astral/blob/sub/AST-1058/AST-1061-gazer-email-meteorite-jobs-playwright-dedupe/docs/features/meteorite/ast-1061-gazer-email-meteorite-jobs-playwright-dedupe.md
**SHA:** `58b09a7358a03d381d91b452a72709db0470399d`
**Path:** `docs/features/meteorite/ast-1061-gazer-email-meteorite-jobs-playwright-dedupe.md`

**Self-assessment**
- **Scope:** `MAJOR-CHANGE` — new gazer email-ingest path + data dedupe helpers + meteorite `job_link` kwarg + inbox/API/UI multi-result Create wiring.
- **Conf:** `Medium` — reuses `create_meteorite_job` / `get_visible_text` / AST-80 inverted match; residual uncertainty is false-positive risk on short global id substrings (mitigated by exact `job_link` gate).
- **Risk:** `Medium` — bad dedupe skips a legitimate create; Playwright per-link failures skip that URL only; non-meteorite gazer paths untouched.

---

# AST-1061 — Gazer email → meteorite jobs (Playwright + dedupe)

**Linear:** [AST-1061](https://linear.app/astralcareermatch/issue/AST-1061/gazer-email-meteorite-jobs-playwright-dedupe-qualify-meteorite)
**Parent:** [AST-1058](https://linear.app/astralcareermatch/issue/AST-1058/qualify-meteorite) — Qualify Meteorite
**Publish ref:** `origin/sub/AST-1058/AST-1061-gazer-email-meteorite-jobs-playwright-dedupe`

Owns **gazer reads email** for meteorite ingest: classify stripped email HTML as JD body / recruiter-forward body / single job link / link list; Playwright `get_visible_text` for each link **before** create; skip create when a known external `company_job_id` (or exact `job_link`) already exists; insert survivors via `create_meteorite_job` into **METEORITE_NEW** with JD text and no Ruth metadata. Wire Manage Email Create through this path. Does **not** own Ruth `qualify_meteorite` apply (AST-1062) or qualify config/dispatch (AST-1060 — already on tip).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `METEORITE_EMAIL_INGEST_CONFIG` (link filters, concurrency, min JD length) | utils |
| `src/data/database.py` | Add global inverted `company_job_id` match + exact `job_link` existence helpers | data |
| `src/core/meteorite.py` | Optional `job_link=` on `create_meteorite_job` (still `company_job_id=None`) | core |
| `src/core/gazer.py` | Email shape classify → Playwright → dedupe → create orchestration + Style D | core |
| `src/core/inbox.py` | After strip, call gazer ingest instead of bare `create_meteorite_job`; multi-result return | core |
| `src/ui/api/api_inbox.py` | Create-job JSON shape for created/skipped lists (keep 201 when ≥1 created; 200 when all skipped) | ui |
| `src/ui/frontend/src/pages/AdminManageEmail.tsx` | Toast for N created / M skipped | ui |

No `consult.py` / dispatcher / `agent_task.json` / GDL / `qualify_*` TASK_CONFIG. No `tests/` / bible (Betty after Code Complete). No new Playwright primitives — call existing `get_visible_text`.

## Stage 1: Config + data-layer dedupe helpers

**Done when:** `METEORITE_EMAIL_INGEST_CONFIG` imports from `src.utils.config`; `database` exposes the two helpers below; no core/UI changes yet.

1. In `src/utils/config.py`, immediately after `METEORITE_CONFIG` (or `INBOX_CREATE_JOB_CONFIG` if adjacent is clearer — **prefer after `METEORITE_CONFIG`**), add:

```python
# AST-1061: gazer email → meteorite ingest (link detect, Playwright, external-id dedupe).
METEORITE_EMAIL_INGEST_CONFIG = {
    # Only http(s) hrefs are job-link candidates (mailto:/tel: excluded by scheme).
    "link_schemes": ("http", "https"),
    # Lowercased path/host fragments that disqualify an href (unsubscribe, tracking, etc.).
    "link_exclude_substrings": (
        "unsubscribe",
        "mailto:",
        "list-manage.com",
        "/preferences",
        "/email-settings",
    ),
    # Max concurrent Playwright fetches for a link list (same idea as gazer JD scrape caps).
    "playwright_concurrency": 3,
    # Skip create when visible/body text length is below this after strip/fetch.
    "min_jd_chars": 40,
}
```

If the top-of-file config inventory lists named `*_CONFIG` blocks, add a one-line `METEORITE_EMAIL_INGEST_CONFIG` entry next to meteorite / inbox bullets.

⚠️ **Decision — config owns link filters and thresholds:** No inline unsubscribe lists or magic length in gazer (§2.1 / config-source-of-truth).

2. In `src/data/database.py`, near `raw_job_listing_is_duplicate`, add:

```python
def text_matches_known_company_job_id(text: str) -> Optional[str]:
    """Global inverted match (AST-80 shape, no company filter).

    Returns the matched company_job_id when any non-empty company_job_id
    appears as a substring of text; else None.
    """
```

SQL (same LIKE pattern as `raw_job_listing_is_duplicate`, drop `company = ?`):

```sql
SELECT company_job_id FROM job
 WHERE company_job_id IS NOT NULL AND TRIM(company_job_id) != ''
   AND ? LIKE '%' || company_job_id || '%'
 LIMIT 1
```

Empty/`None` `text` → return `None` without querying.

3. In the same module, add:

```python
def job_link_exists(job_link: str) -> bool:
    """True when any job row has this exact job_link (non-empty)."""
```

SQL: `SELECT 1 FROM job WHERE job_link = ? AND job_link IS NOT NULL AND TRIM(job_link) != '' LIMIT 1`.

⚠️ **Decision — global id match + exact link match:** Meteorite creates today leave `company_job_id=None`, so company-scoped AST-80 alone cannot skip a second email for the same ATS URL. Exact `job_link` covers re-ingest of the same URL before Ruth fills the UUID; global inverted match covers ids already stored on any company (including post-qualify meteorite rows). Do **not** invent fuzzy URL normalization in this ticket.

**Done when (recheck):** `from src.utils.config import METEORITE_EMAIL_INGEST_CONFIG` works; helpers importable; `python3 -m py_compile src/utils/config.py src/data/database.py` succeeds.

## Stage 2: `create_meteorite_job` optional `job_link`

**Done when:** Callers can pass `job_link=`; omitted behavior matches today (`job_link=None`, `company_job_id=None`, state **METEORITE_NEW**, JD in `job_data`); no gazer/inbox changes yet.

1. In `src/core/meteorite.py`, extend signature:

```python
def create_meteorite_job(
    candidate_id: str,
    html_body: str,
    *,
    job_link: Optional[str] = None,
    debug: bool = False,
) -> dict[str, Any]:
```

2. Pass `job_link=(job_link.strip() if job_link and str(job_link).strip() else None)` into `save_job`. Keep `company_job_id=None` always on this path (Ruth / AST-1062 owns external UUID persist).

3. Update the module docstring one line: optional `job_link` for link-sourced ingest (AST-1061); still no Ruth metadata.

⚠️ **Decision — do not set `company_job_id` here:** Extracting ATS UUIDs from URLs is vendor-specific and belongs with qualify enrichment. Link-based dedupe uses `job_link_exists` + global inverted match on URL/visible text instead.

**Done when (recheck):** Existing inbox/API create without `job_link` still inserts **METEORITE_NEW**; with `job_link="https://example.com/j/1"` the row’s `job_link` column equals that string.

## Stage 3: Gazer ingest orchestration (new pattern)

**Done when:** Given `candidate_id` + stripped email HTML, gazer returns created/skipped summaries; link shapes Playwright before create; known id/link skips insert; body shapes create without Playwright; Style D only when `debug=True`.

1. In `src/core/gazer.py`, update the module docstring to note AST-1061 meteorite email ingest (gazer-reads-email). Keep existing scrape/listing functions unchanged.

2. Add private helpers (below existing public batch entry points is fine; keep public ingest function above them if the file’s public-first convention requires it — **match existing gazer style**: public async entry near other batch publics, privates nearby):

```python
def _meteorite_email_candidate_links(html: str) -> List[str]:
    """Ordered unique http(s) hrefs from html, minus METEORITE_EMAIL_INGEST_CONFIG excludes."""

def _meteorite_email_body_text(html: str) -> str:
    """Plain visible-ish text from stripped email HTML for body/forward shapes (bs4 get_text)."""

async def _meteorite_fetch_link_visible_text(
    url: str, *, debug: bool = False
) -> Tuple[str, str]:
    """Return (visible_text, final_url) via get_visible_text(..., return_final_url=True)."""
```

Link extraction: lazy-import `bs4.BeautifulSoup` (same B1 pattern as inbox strip). Walk `a[href]`; keep hrefs whose scheme (via `urllib.parse.urlparse`) is in `link_schemes`; drop when any `link_exclude_substrings` appears in the lowercased href; preserve first-seen order; de-dupe exact href strings.

3. Add the public async entry:

```python
async def ingest_meteorite_jobs_from_email_html(
    candidate_id: str,
    html: str,
    *,
    debug: bool = False,
) -> dict[str, Any]:
    """Classify email HTML → optional Playwright → dedupe → create_meteorite_job.

    Returns:
      {
        "astral_candidate_id": str,
        "mode": "links" | "body",
        "created": [ create_meteorite_job result dicts ... ],
        "skipped": [ {"reason": str, "url": Optional[str], "matched_company_job_id": Optional[str]} ... ],
      }
    """
```

Also add a thin sync wrapper for inbox (Flask is sync):

```python
def ingest_meteorite_jobs_from_email_html_sync(
    candidate_id: str,
    html: str,
    *,
    debug: bool = False,
) -> dict[str, Any]:
    return asyncio.run(
        ingest_meteorite_jobs_from_email_html(candidate_id, html, debug=debug)
    )
```

Import `asyncio` at module top if not already present.

4. **Classify:**
   - `links = _meteorite_email_candidate_links(html)`
   - If `links`: `mode = "links"`
   - Else: `mode = "body"` (covers JD-body and recruiter-forward — both are email text without qualifying job links)

⚠️ **Decision — no separate NLP “forward” detector:** AC names recruiter forward as a shape; after AST-1049 strip/subject wrap, forward bodies are still body text. Link presence is the only branch that requires Playwright. Do not call Anthropic here.

5. **Links path:**
   - Cap concurrency with `asyncio.Semaphore(METEORITE_EMAIL_INGEST_CONFIG["playwright_concurrency"])`.
   - For each URL (index `i` of `n`):
     - `text, final_url = await _meteorite_fetch_link_visible_text(url, debug=debug)` inside the semaphore.
     - On Playwright exception: append `skipped` with `reason="playwright_error"` and `url`; continue (do not abort the whole batch). Log a warning via `get_logger` (not Style D).
     - Build `haystack = f"{final_url or url}\n{text}"`.
     - If `job_link_exists(final_url or url)`: skip `reason="known_job_link"`.
     - Else if `(matched := text_matches_known_company_job_id(haystack))`: skip `reason="known_company_job_id"`, include `matched_company_job_id=matched`.
     - Else if `len(text.strip()) < min_jd_chars`: skip `reason="jd_too_short"`.
     - Else: `create_meteorite_job(candidate_id, text, job_link=(final_url or url), debug=debug)` and append to `created`.
     - Style D when `debug=True`: `debug_index(func="gazer.meteorite_email_ingest", index=i, total=n, identifier=(final_url or url)[:80], outcome="found"|"skipped-duplicate"|"skipped-short"|"skipped-error"|"recorded")` plus `debug_detail` lines for reason / astral_job_id / matched id as applicable.

6. **Body path:**
   - `text = _meteorite_email_body_text(html)` (if empty, fall back to raw `html` stripped of tags only if get_text is empty — prefer get_text; if still empty raise `ValueError("email body is empty")`).
   - Dedupe on `text` only via `text_matches_known_company_job_id` (no `job_link`).
   - If matched → `skipped` with `reason="known_company_job_id"`; `created=[]`.
   - Elif `len(text.strip()) < min_jd_chars` → skip `jd_too_short`.
   - Else → one `create_meteorite_job(candidate_id, html if html.strip() else text, job_link=None, debug=debug)`.
     - Prefer storing the **stripped HTML** as JD when non-empty (preserves AST-1049 subject wrapper); use plain `text` only when HTML is empty.

⚠️ **Decision — body create keeps HTML JD:** Matches AST-1049 create payload so qualify still sees subject+body structure; link path stores Playwright visible text (plain) because that is the fetched page content.

7. Do **not** change `process_gazer_batch`, `fetch_jd_batch`, listing ingest, or company scrape paths beyond adding the new functions/imports.

**Done when (recheck):** Unit-level manual calls (or a short spike under `debug/spikes/` only — not committed) show: body→one **METEORITE_NEW**; one link→Playwright then create with `job_link` set; second Create with same link→skipped `known_job_link`; text containing an existing `company_job_id`→skipped; `debug=False` emits no new `debug_index`/`debug_detail` from this path.

## Stage 4: Inbox + API + Manage Email Create UI

**Done when:** Manage Email Create runs gazer ingest after strip; API returns multi-result JSON; toast reports created/skipped counts; unmatched candidate / empty strip still 400.

1. In `src/core/inbox.py` `create_meteorite_job_from_inbox_message`:
   - Keep fetch / From→candidate / `strip_extract_email_html` / empty-strip `ValueError` / Style D steps 1–3 as today.
   - Replace the direct `create_meteorite_job(...)` call with:

```python
from src.core.gazer import ingest_meteorite_jobs_from_email_html_sync

ingest = ingest_meteorite_jobs_from_email_html_sync(cid, html, debug=debug)
```

   - Style D step 4: outcome `"recorded"` when `len(ingest["created"]) > 0`, else `"skipped"`; detail `created=N skipped=M mode=...`.
   - Return shape:

```python
{
  "astral_candidate_id": cid,
  "mode": ingest["mode"],
  "created": ingest["created"],
  "skipped": ingest["skipped"],
  # Back-compat for single-create callers/tests:
  "astral_job_id": ingest["created"][0]["astral_job_id"] if ingest["created"] else None,
  "company": ingest["created"][0]["company"] if ingest["created"] else METEORITE_CONFIG["short_name_template"].format(candidate_id=cid),
  "state": ingest["created"][0]["state"] if ingest["created"] else None,
  "latest_score": ingest["created"][0]["latest_score"] if ingest["created"] else None,
  "company_inserted": any(c.get("company_inserted") for c in ingest["created"]),
}
```

   - If `created` is empty and `skipped` is empty: raise `ValueError("no meteorite jobs created")`.
   - If `created` is empty and `skipped` is non-empty: **do not raise** — return the dict (API maps to 200).

2. In `src/ui/api/api_inbox.py` `inbox_create_job_from_message`:
   - Docstring note AST-1061 multi-create.
   - On success:
     - If `result["created"]`: status **201**, JSON:

```python
{
  "astral_candidate_id": result["astral_candidate_id"],
  "mode": result["mode"],
  "created": [
    {
      "astral_job_id": c["astral_job_id"],
      "company": c["company"],
      "state": c["state"],
      "latest_score": c["latest_score"],
      "company_inserted": c["company_inserted"],
    }
    for c in result["created"]
  ],
  "skipped": result["skipped"],
  # keep top-level astral_job_id for older UI:
  "astral_job_id": result["astral_job_id"],
  "company": result["company"],
  "state": result["state"],
  "latest_score": result["latest_score"],
  "company_inserted": result["company_inserted"],
}
```

     - If only skips: status **200**, same JSON with `created: []`.

3. In `AdminManageEmail.tsx` `onCreateClick` success branch:
   - Prefer `created` array length when present; toast e.g. `Created N job(s)` and if `skipped.length` append `; skipped M`.
   - If `created` empty and `skipped` non-empty: success-variant toast `Skipped M (already known or empty)` (not error).
   - Keep error path for non-OK responses.

4. Smoke (manual / existing component tests only if already covering Create — do not add Betty bible here): Create still works for body-only email; non-meteorite scrape/GDL untouched (no code edits there — AC4 is “do not change”).

**Done when (recheck):** `python3 -m py_compile` on touched Python files; frontend typechecks if the repo’s usual `npm` lint script is used for TS edits; Create toast shows multi counts; all-skipped returns 200 not 502.

## Out of scope (do not implement here)

- Ruth `qualify_meteorite` batch apply / persist UUID/title/link/JD (AST-1062).
- Qualify states / TASK_CONFIG / dispatch rows (AST-1060).
- Changing non-meteorite `process_gazer_batch` / `qualify_job_listings` / GDL priors.
- Auto-polling unread Gmail without Manage Email Create (no new dispatcher task).
- Vendor-specific URL→UUID parsers writing `company_job_id` on create.
- `tests/` / `docs/test-bible/**` (Betty after Code Complete).

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — new gazer email-ingest path plus data dedupe helpers, meteorite `job_link` kwarg, and inbox/API/UI Create multi-result wiring; layers utils/data/core/ui.

**Conf:** `Medium` — Playwright + `create_meteorite_job` reuse is clear; shape split is link-vs-body (no NLP); residual uncertainty is how noisy global inverted match is on short numeric ids (mitigated by existing id lengths on real ATS rows + exact `job_link` gate).

**Risk:** `Medium` — false-positive global id substring match could skip a legitimate create; Playwright failures skip that link rather than failing the whole Create; non-meteorite gazer paths are untouched.

## Rules self-review

- **§2.1 / config-source-of-truth:** Link schemes, excludes, concurrency, min JD length live in `METEORITE_EMAIL_INGEST_CONFIG` only.
- **§3.3 / core-vs-external:** Gazer (core) calls `get_visible_text` (external) and `database.*` / `create_meteorite_job`; no Playwright or Gmail imports in UI; inbox stays orchestration.
- **§ debug-contract-gated:** Style D only when `debug=True` on gazer + inbox paths; no new contract lines from data layer.
- **§1.3 DRY:** Reuse `create_meteorite_job`, `get_visible_text`, AST-80 LIKE shape (global variant); do not fork a second meteorite insert.
- **In-scope only:** No qualify apply, no GDL edits, no tests/bible.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1058/AST-1061-gazer-email-meteorite-jobs-playwright-dedupe`
**Plan path:** `docs/features/meteorite/ast-1061-gazer-email-meteorite-jobs-playwright-dedupe.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `8b01998c` | `METEORITE_EMAIL_INGEST_CONFIG` + global dedupe helpers |
| 2 | `99c51148` | optional `job_link=` on `create_meteorite_job` |
| 3 | `4b69107e` | gazer email ingest Playwright + dedupe |
| 4 | `f82be0d6` | inbox / API / Manage Email multi-result Create |

## Review (Radia — code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1061
**Publish ref:** `259ebb336d4265633f7f21e4ee47071d3a5bbcde` (`origin/sub/AST-1058/AST-1061-gazer-email-meteorite-jobs-playwright-dedupe`)
**Overall:** DISCUSS

### What’s solid
- `METEORITE_EMAIL_INGEST_CONFIG` + global `text_matches_known_company_job_id` / `job_link_exists`; optional `job_link` on create (still `company_job_id=None`).
- Gazer ingest: link→Playwright→dedupe→create; body path without PW; Style D gated; inbox/API/UI multi-result.
- Playwright only via `get_visible_text`; non-meteorite gazer scrape untouched.

### Issues
- **discuss (straggler ×3):** Joan excluded at plan time; in-scope on three-dot vs `origin/dev` via plan docs + Betty tests/bible — all substance **conforms**:
  - `astral.debug.spikes-under-debug-dir`
  - `astral.docs.features-single-file-per-ticket`
  - `astral.git.engineer-test-tree-ban`

### Recommended actions
- Katherine: acknowledge stragglers → resolve-child → User Testing.

## Resolution

**Date:** 2026-07-30  
**Outcome:** clean — no product changes.

- **fix-now:** none.
- **discuss (straggler ×3):** Acknowledged. Three-dot vs `origin/dev` pulls plan docs + Betty `tests/` / bible into the statute window; all three statutes **conform** (single plan file under `docs/features/`; no spikes at repo root; engineer did not edit test-tree). No code or plan rewrite.
- **advisory:** Global inverted-id false-positive remains a watch item; exact `job_link` gate stays the re-ingest mitigator (unchanged).
