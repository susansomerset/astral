<!-- linear-archive: AST-998 archived 2026-08-05 -->

## Linear archive (AST-998)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-998/base-session-job-builders-experience-job-render-parse-resume-json  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-994 — Parse resume json output is incomplete  
**Blocked by / blocks / related:** parent: AST-994

### Description

## What this implements

Resume HTML builders (candidate base, session/Admin paste, and job-tailored) recognize the experience job array and render consistent role subheaders/metadata (including location) plus the accomplishments block. Does **not** own Judith prompt/schema or AST-993 education/skills/header chrome.

## Acceptance criteria

4. Opening HTML from Session Resume Paste (or equivalent session HTML) for that parse shows each experience job with consistent role subheaders/metadata (company, title, dates, location) and the accomplishments body — not one merged experience blob.
5. Candidate base-resume HTML built from the same structured experience job array shows the same role subheader/metadata pattern (parity with the session builder path).
6. Job-tailored resume HTML recognizes the job array and renders the same consistent subheader/metadata pattern as base/session.

## Boundaries

* Does **not** own Judith craft-base or job-tailored prompt/schema — siblings AST-996 and job-tailored child.
* Does **not** absorb AST-993 richer golden-fixture role layout (lead vs bullets / exact phrasing chrome) — single accomplishments block + consistent subheaders only for this epic.
* Does **not** change cover-letter HTML.

## Notes for planning

* Depends on AST-996 job-array shape existing in structured content.
* Shared builder path — session and base (and job) stay aligned.

## Git branch (authoritative)

Per **orientation** § Branch law: parent **ftr/<parent-segment>**, child **sub/<parent-id>/<child-segment>**. Created at dispatch-parent. Publish to **origin/<sub-ref>** only.

### Comments

#### chuckles — 2026-07-28T03:10:13.693Z
[merge-child] blocked: validate-sub-log — git pull merge on sub (`588d8291 Merge remote-tracking branch 'origin/ftr/ast-994-parse-resume-json-output-is-incomplete' into sub/...`). @Hedy Lamarr republish clean stack from `origin/ftr/ast-994-parse-resume-json-output-is-incomplete` with canonical plan|code|merge-tests|test|docs|resolve only (no Merge remote-tracking subjects in ftr..sub). Stay User Testing. Chuckles will re-run merge-child after tip is clean.

— Chuckles

#### radia — 2026-07-28T03:07:31.466Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-998
**Publish ref:** `d5b0383b` on `origin/sub/AST-994/AST-998-base-session-job-builders-experience-job-render` (baseline `origin/dev`)
**Overall:** DISCUSS

## Statutes checked

| id | tier | verdict | one-line |
| --- | --- | --- | --- |
| astral.agent.confidence-bounds | scoped | conforms | core/utils touched; no graded confidence changes |
| astral.agent.do-task-delegation | scoped | conforms | no new do_task ownership in 998 code |
| astral.agent.grade-vector-validation | scoped | conforms | no graded vectors |
| astral.batch.batch-id-first | scoped | conforms | no new batch APIs |
| astral.batch.batch-id-format | scoped | conforms | untouched |
| astral.batch.claim-process-release | scoped | conforms | no new claim pattern |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | untouched |
| astral.config.config-source-of-truth | scoped | conforms | only `body_kind` → `experience_jobs`; wire shape stays AST-996 |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | thresholds untouched |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | no secrets/env literals |
| astral.debug.no-repo-root-artifacts-dir | scoped | conforms | no repo-root `artifacts/` dump |
| astral.debug.spikes-under-debug-dir | scoped | conforms | plan under `docs/features/**` |
| astral.docs.features-single-file-per-ticket | scoped | conforms | one combined plan/review file for AST-998 |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty `test`/`merge-tests` touch tests/bible only |
| astral.git.engineer-test-tree-ban | scoped | conforms | engineer `code(AST-998)` has no tests/ |
| astral.layers.core-vs-external-bright-line | scoped | conforms | HTML emit stays in core builder |
| astral.layers.import-direction | scoped | conforms | builder → candidate/config only; tip UI from siblings |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers/paths miss (no `scripts/**`) |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | 998 has no UI; tip UI from 996 |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | no coat-check changes |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | no consult/render-verdict |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | no new endpoints |
| astral.standards.data-raises-caller-logs | scoped | conforms | no data-layer logging |
| astral.standards.database-header-inventory | scoped | not-applicable | layers/paths miss (`src/data/**`) |
| astral.standards.debug-contract-gated | scoped | conforms | only extends existing `debug=True` `render_keys` |
| astral.standards.dry-and-focused-functions | scoped | conforms | one shared `_emit_experience_jobs_html` for all surfaces |
| astral.standards.in-scope-only | scoped | conforms | no prompts/schemas/ArtifactEditor/cover-letter/AST-993 chrome |
| astral.standards.logging-via-utils | scoped | conforms | existing Style D helpers |
| astral.standards.no-cross-contamination | scoped | conforms | layer boundaries held |
| astral.standards.no-hardcoded-sets | scoped | conforms | field keys are AST-996 wire contract; emit shape-driven |
| astral.standards.public-then-helpers | scoped | conforms | helper + unchanged public builder signatures |
| astral.standards.utils-data-late-import-only | scoped | conforms | body_kind-only utils; no utils→data |
| astral.state.core-decides-transitions | scoped | conforms | no state machine |
| astral.state.job-prior-states-enforced | scoped | conforms | untouched |
| astral.state.no-daisy-chain-in-run | scoped | conforms | untouched |
| astral.ui.frontend-file-placement | scoped | conforms | tip UI from siblings; no new UI files in 998 |
| astral.ui.naming-conventions | scoped | conforms | no new UI routes/files in 998 |
| astral.ui.single-gunicorn-worker | scoped | conforms | untouched |
| orch.git.betty-merge-tests-one-sha | universal | conforms | tip includes `merge-tests(AST-998)` |
| orch.git.commit-vocabulary | universal | conforms | `code`/`docs`/`test`/`merge-tests`/`merge` vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | publish to child `sub/*` only |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-994/AST-998-…` matches branch law |
| orch.git.merge-on-checkout | universal | conforms | tip merges ftr/996 lineage as precondition |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | no rewrite ops |
| orch.git.no-dev-agent-branches | universal | conforms | work on ticket sub |
| orch.git.one-epic-worktree-per-parent | universal | conforms | review in `astral-AST-994` |
| orch.git.three-permanent-branches | universal | conforms | no new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | subheader/meta vs AST-993 chrome followed plan |
| orch.pipeline.plan-is-bible | universal | conforms | stages 1–2 match tip; siblings excluded |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Artifacts child |
| orch.pipeline.status-gates-skill-entry | universal | conforms | review from Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | no statute edits |
| orch.roles.betty-owns-test-tree | universal | conforms | tests/bible via Betty |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Chuckles not assignee |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | implementer Hedy; assignee left untouched |
| orch.roles.pre-commit-path-bans | universal | conforms | role path bans respected |

## Pattern conformance

none cited

## Plan adherence

Stages 1–2 match: `body_kind` flip; shared `_emit_experience_jobs_html` on value shape (public `is_experience_job_array`); title/company subheader + meta + accomplishments; role CSS + print `page-break-inside`; legacy string path; `render_keys` honesty. Cover letter untouched. Self-Assessment Single-Component still fits. Joan plan-rubric APPROVED.

## Findings

### fix-now
(none)

### discuss
1. **C4 straggler** — Joan excluded `astral.debug.no-repo-root-artifacts-dir`; tip in-scope — **conforms**.
2. **C4 straggler** — Joan excluded `astral.debug.spikes-under-debug-dir`; tip has `docs/features/**` — **conforms**.
3. **C4 straggler** — Joan excluded `astral.docs.features-single-file-per-ticket`; tip adds AST-998 plan — **conforms**.
4. **C4 straggler** — Joan excluded `astral.git.engineer-test-tree-ban`; tip includes Betty tests — **conforms**.
5. **C4 straggler** — Joan excluded `astral.patterns.require-auth-on-protected-endpoints`; tip has UI via sibling merge — **conforms**.
6. **C4 straggler** — Joan excluded `astral.ui.frontend-file-placement`; tip UI from siblings — **conforms**.
7. **C4 straggler** — Joan excluded `astral.ui.naming-conventions`; tip UI from siblings — **conforms**.

### advisory
(none)

## What’s solid

Shape-driven emit (not `body_kind`); one shared role chrome for base/session/job; markers before escape; empty arrays omit section; print avoid-split retained.

## Notes

Plan-rubric verdict attached (Joan APPROVED). Three-dot vs `origin/dev` includes merged AST-996/997; stragglers are process notes only — no product fix-now.

context_tokens≈38000

#### betty — 2026-07-28T02:44:24.538Z
## Merge-conflict resolve (ftr → publish-ref)

Merged `origin/ftr/ast-994-parse-resume-json-output-is-incomplete` into publish-ref. Resolved Betty paths keeping AST-998 + rolled-up siblings:
- `docs/test-bible/core/tracker.md`
- `docs/test-bible/utils/config.md`
- `tests/component/utils/test_config.py`

**Publish tip:** `origin/sub/AST-994/AST-998-base-session-job-builders-experience-job-render` @ `c92a9007`

Staying **Tests Ready** — reassigned to Hedy for test-child re-run.

#### hedy — 2026-07-28T02:42:19.981Z
[check-linear] blocked: merge conflict merging `origin/ftr/ast-994-parse-resume-json-output-is-incomplete` into `sub/AST-994/AST-998-base-session-job-builders-experience-job-render` — docs/test-bible/core/tracker.md (@Betty White); docs/test-bible/utils/config.md (@Betty White); tests/component/utils/test_config.py (@Betty White). Engineer hook blocks me from committing those paths; merge aborted on clean tip `672e4a8d`. Need Betty resolve + push to publish-ref before test-child can re-run.

#### betty — 2026-07-28T02:40:40.897Z
## QA test manifest — AST-998

**Publish:** `origin/sub/AST-994/AST-998-base-session-job-builders-experience-job-render` @ `672e4a8d` (`merge-tests(AST-998): origin/tests 690f267e`)

### Classification
1. **Existing coverage:** `TestAst987BuildSessionBaseResume` (session/base HTML surfaces still exercised)
2. **Broken / obsolete:** none
3. **Gaps (new):** `TestAst998ExperienceJobRender` (per-role chrome across emit / session / base / job; legacy string path); `TestAst998ExperienceBodyKind` (`BUILD_CONFIG` experience → `experience_jobs`)

### Manifest (test-child)

1. `./scripts/testing/run_component_tests.sh tests/component/core/test_builder.py::TestAst998ExperienceJobRender tests/component/core/test_builder.py::TestAst987BuildSessionBaseResume tests/component/utils/test_config.py::TestAst998ExperienceBodyKind -q`

**Pass:** narrowed pytest green (not zero-arg / branch-lock).

### Bible (publish tip)

| File | sha256 |
| --- | --- |
| `docs/test-bible/core/builder.md` | `1dd9a35234236460fc609c784c8359a6211f011e2c15f49446ca78df8aba0cc3` |
| `docs/test-bible/utils/config.md` | `06b24ae4f18a0a3b50c4555d5136ff9a324a9a615f083d911ab3ed63a21357fc` |

#### joan — 2026-07-28T01:46:26.098Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-998
**Overall:** APPROVED

**Notes:** First Plan Ready pass. Tip `c5e7b697`. Blocked-by AST-996 Plan Approved acknowledged; build precondition + value-shape emit (not `body_kind`) preserve legacy string experience correctly.
**Implementer:** Hedy (plan author / parent Team table).

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
| -- | -- |
| 1–3 craft-base parse / facts / accomplishments | N/A — boundary: AST-996 |
| 4 Session HTML role subheaders/metadata + accomplishments | Stage 2 via `build_session_base_resume` shared emit |
| 5 Candidate base-resume HTML same pattern | Stage 2 via `build_base_resume` shared emit |
| 6 Job-tailored hops accept/emit job-array | N/A — boundary: AST-997 |
| 7 Job-tailored HTML same subheader/metadata pattern | Stage 2 via `build_resume_from_job` shared emit (once job `resume_content.experience` is a job array) |
| 8 Dates freeform | Render as freeform meta string; no start/end schema |
| 9 Style D parse/tailor hops | N/A — Stage 2 only extends existing builder `render_keys` honesty; no new parse-hop debug |

### Child AC → plan stages

| Child AC | Stages |
| -- | -- |
| 4 Session HTML per-role chrome | 1–2 |
| 5 Base-resume HTML parity | 1–2 |
| 6 Job-tailored HTML same pattern | 1–2 |

### Plan stages → definition

| Stage | Maps to |
| -- | -- |
| 1 `body_kind` → `experience_jobs` | Catalog/docs for supported_sections; emit still shape-driven |
| 2 Shared `_emit_experience_jobs_html` + CSS + legacy string | Parent AC4/5/7; Functional scope shared HTML recognition; Boundaries (no AST-993 chrome) |

## Statute verdicts

| id | verdict | one-line |
| -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests |
| orch.git.commit-vocabulary | conforms | Plan `docs(AST-998):` path |
| orch.git.flow-direction-inviolable | conforms | Child `sub/*` only |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | 996/ftr merge precondition correct |
| orch.git.no-cherry-pick-rebase-force | conforms | No rewrite ops |
| orch.git.no-dev-agent-branches | conforms | Ticket sub only |
| orch.git.one-epic-worktree-per-parent | conforms | `astral-AST-994` |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Subheader/meta vs AST-993 chrome decided in plan; no product ambiguity |
| orch.pipeline.plan-is-bible | conforms | Stages binding; prompts/schemas excluded |
| orch.pipeline.project-scoped-queues | conforms | Single-child Astral Artifacts |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | tests/bible out of scope |
| orch.roles.chuckles-never-ticket-assignee | conforms | Implementer Hedy |
| orch.roles.engineer-assignee-through-resolve | conforms | Reassign Hedy on approve |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | Untouched |
| astral.agent.do-task-delegation | conforms | No new do_task ownership |
| astral.agent.grade-vector-validation | conforms | Untouched |
| astral.batch.batch-id-first | conforms | Untouched |
| astral.batch.batch-id-format | conforms | Untouched |
| astral.batch.claim-process-release | conforms | Untouched |
| astral.batch.entity-agent-responses-latest-only | conforms | Untouched |
| astral.config.config-source-of-truth | conforms | Only `body_kind` literal; wire fields owned by AST-996 |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env |
| astral.git.betty-no-src-or-features | conforms | Engineer-owned src |
| astral.layers.core-vs-external-bright-line | conforms | HTML emit stays in core builder |
| astral.layers.import-direction | conforms | builder → candidate/config/formatting/logging only |
| astral.layers.ui-config-driven-business-logic | conforms | No UI changes |
| astral.patterns.coat-check-never-store-empty | conforms | Untouched |
| astral.patterns.render-verdict-orchestrates-consult | conforms | Untouched |
| astral.standards.data-raises-caller-logs | conforms | No data-layer logging |
| astral.standards.debug-contract-gated | conforms | Only extend existing `debug=True` render_keys |
| astral.standards.dry-and-focused-functions | conforms | One shared `_emit_experience_jobs_html` for all three surfaces |
| astral.standards.in-scope-only | conforms | Excludes prompts, schemas, ArtifactEditor, AST-993, cover letter |
| astral.standards.logging-via-utils | conforms | Existing logging helpers |
| astral.standards.no-cross-contamination | conforms | Layered structure |
| astral.standards.no-hardcoded-sets | conforms | No new behavior enums; field keys are AST-996 wire contract |
| astral.standards.public-then-helpers | conforms | New helper + unchanged public builder signatures |
| astral.standards.utils-data-late-import-only | conforms | No new utils→data |
| astral.state.core-decides-transitions | conforms | No state machine |
| astral.state.job-prior-states-enforced | conforms | Untouched |
| astral.state.no-daisy-chain-in-run | conforms | Untouched |
| astral.ui.single-gunicorn-worker | conforms | Untouched |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths miss
- astral.debug.spikes-under-debug-dir — paths miss
- astral.docs.features-single-file-per-ticket — layers/paths miss
- astral.git.engineer-test-tree-ban — paths miss
- astral.layers.scripts-exempt-from-layer-rules — layers/paths miss
- astral.patterns.require-auth-on-protected-endpoints — layers/paths miss
- astral.standards.database-header-inventory — layers/paths miss
- astral.ui.frontend-file-placement — layers/paths miss
- astral.ui.naming-conventions — layers/paths miss

## Findings

### fix-now
(none)

### discuss
(none)

### acceptable
1. Emit branches on value shape (`_is_experience_job_array`), not `body_kind` — required so legacy string experience survives the Stage 1 catalog flip; `body_kind` is unused at runtime today across sections (catalog metadata).
2. Prefer public `is_experience_job_array` alias if AST-996/997 expose it; importing `candidate_mod._is_experience_job_array` matches existing builder↔candidate pattern.
3. AST-997 not a hard plan blocker for base/session HTML; job-tailored HTML AC waits on job_array in job `resume_content` (997) but shares this emit.
4. Self-assessment Single-Component / high / Medium — honest.
5. Explicit AST-993 non-goals (Title•Company chrome, lead/bullet split) — correct boundary.

— Joan
context_tokens≈72000

#### hedy — 2026-07-28T01:38:40.873Z
Plan: [`docs/features/artifacts/ast-998-base-session-job-builders-experience-job-render.md`](https://github.com/susansomerset/astral/blob/sub/AST-994/AST-998-base-session-job-builders-experience-job-render/docs/features/artifacts/ast-998-base-session-job-builders-experience-job-render.md) on `origin/sub/AST-994/AST-998-base-session-job-builders-experience-job-render` @ `c5e7b697`.

**Scope:** Single-Component — shared `builder.py` Experience emit + one `BUILD_CONFIG` `body_kind` flip; no Judith prompts.

**Conf:** high — session/base/job already share `_emit_body_sections_html`; AST-996 defines the wire shape; recognition gap is localized where lists are JSON-dumped today.

**Risk:** Medium — bad subheader/meta join or stringify would regress Session Paste / base / job-tailored Experience HTML; legacy string path must stay for pre-996 blobs.

Build precondition: merge AST-996 (or ftr after merge-child) before product stages so filter preserve + `_is_experience_job_array` exist.

---

# Base + session + job builders: experience job render (Parse resume json output is incomplete)

**Linear:** [AST-998](https://linear.app/astralcareermatch/issue/AST-998/base-session-job-builders-experience-job-render-parse-resume-json)
**Parent:** [AST-994](https://linear.app/astralcareermatch/issue/AST-994/parse-resume-json-output-is-incomplete) — Parse resume json output is incomplete
**Publish ref:** `origin/sub/AST-994/AST-998-base-session-job-builders-experience-job-render`
**Blocked by:** [AST-996](https://linear.app/astralcareermatch/issue/AST-996/judith-craft-base-experience-job-array-parse-resume-json-output-is) — Plan Approved job-array contract (`_EXPERIENCE_JOB_*`, filter/split preserve). Plan HTML recognition of that shape; do **not** own Judith prompts or tailor hops.

Resume HTML builders (candidate base, session/Admin paste, and job-tailored) recognize Experience as the AST-996 ordered job array and render each role with consistent subheaders/metadata (company, title, dates, location) plus one accomplishments block — not a JSON dump or a single merged prose blob. Shared emit path keeps the three surfaces aligned. Does **not** own craft-base/job-tailored prompts (AST-996 / AST-997) or AST-993 lead/bullet / Title•Company chrome.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Set `BUILD_CONFIG["supported_sections"]["experience"]["body_kind"]` to `"experience_jobs"` (render kind docs; emit still keys off value shape) | utils |
| `src/core/builder.py` | Recognize experience job arrays in `_emit_body_sections_html`; emit per-role HTML + CSS; apply resume-site markers to job string fields; keep legacy string path; tighten debug `render_keys` for job arrays | core |

**Out of scope (do not touch):** `data/admin/agent_task.json` / Judith prompts; `craft_resume_base` / `draft_job_resume` / `finalize_job_resume` schemas (AST-996 / AST-997); `ArtifactEditor.tsx`; cover-letter emit; `prior_experience` (stays prose string); AST-993 education/skills/header chrome or lead-vs-bullets role layout; `tests/`, bible.

**Build precondition:** Before Stage 1 product commits, merge `origin/sub/AST-994/AST-996-judith-craft-base-experience-job-array` (or rolled-up `origin/ftr/ast-994-parse-resume-json-output-is-incomplete` once Chuckles merges 996) so `filter_content_to_resume_structure` / session+base content preserve the job array and `candidate._is_experience_job_array` exists. If those landings are missing after merge, **stop** and comment on the parent — do not re-implement craft-base preserve logic here. AST-997 is **not** required to emit job-array HTML from base/session content; job-tailored HTML uses the same emit once job `resume_content.experience` is a job array (997’s responsibility to produce it).

## Contract reference (AST-996 — do not redefine)

Each experience job object (wire keys fixed):

| Field | Type | Render |
|-------|------|--------|
| `company` | str | Meta (or subheader fallback when title empty) |
| `title` | str | Role subheader when non-empty |
| `dates` | str (freeform) | Meta |
| `location` | str (`""` if absent) | Meta when non-empty; omit empty |
| `accomplishments` | str (one block) | Role body (`prose-block`) |

## Stage 1: Config — experience body_kind

**Done when:** `BUILD_CONFIG["supported_sections"]["experience"]["body_kind"]` is `"experience_jobs"`; no TASK_CONFIG / artifact_shapes / craft-base edits.

1. In `src/utils/config.py`, change only:
   ```python
   "experience": {
       "heading_level": "section_heading",
       "body_kind": "experience_jobs",
       "page_break_policy": "avoid_split",
   },
   ```
2. Do **not** change `prior_experience` or other sections’ `body_kind`.
3. Do **not** duplicate `_EXPERIENCE_JOB_*` here — those stay owned by AST-996.

## Stage 2: Shared HTML emit — recognize job array + consistent role chrome

**Done when:** Calling `build_session_base_resume`, `build_base_resume`, or `build_resume_from_job` with `experience` as a non-empty AST-996 job array produces HTML where `#experience` contains one `.role` per job (not a JSON dump and not one undifferentiated prose blob); each role shows title (or company fallback) as subheader, a meta line with the non-empty subset of company/dates/location, and the accomplishments body; legacy string `experience` still renders as today’s single `prose-block`; cover-letter HTML unchanged.

1. In `src/core/builder.py`, replace the generic “any dict/list → `_format_experience_value`” path inside `_emit_body_sections_html` so **`experience` is handled first**:
   - If `key == "experience"` and `candidate_mod._is_experience_job_array(raw)`:
     - Build inner HTML via new helper `_emit_experience_jobs_html(raw)`.
     - If that helper returns empty/whitespace, `continue` (omit the Experience section).
     - Else append the Experience `<section>` with `<h2>` + the roles HTML (no wrapping JSON/`prose-block` for the whole section).
     - `continue` (do not fall through to string coercion).
   - Else keep today’s behavior for other keys and for legacy string `experience` (string → escape → section-specific wrappers).
   - For unexpected non-job-array `list`/`dict` on **non-experience** keys, keep `_format_experience_value` (JSON visibility) as today.
   ⚠️ **Decision:** Branch on **value shape** via AST-996’s `_is_experience_job_array`, not on `body_kind`. Legacy stored string experience must keep working after Stage 1’s `body_kind` flip; reading `body_kind` for emit would break that.
2. Add `_emit_experience_jobs_html(jobs: list) -> str`:
   - For each item in order: skip if not a `dict`.
   - Read fields with `str(... or "").strip()` for `title`, `company`, `dates`, `location`, `accomplishments`.
   - Skip the role entirely when all five stripped values are empty.
   - Apply `_resume_site_markers` to each non-empty field **before** `html.escape`.
   - **Subheader (`h3.role-subheader`):** prefer `title`; if title empty and company non-empty, use `company` as the subheader text; if both empty, omit the `h3`.
   - **Meta (`p.role-meta`):** build an ordered list of non-empty parts:
     - If subheader used `title`, include `company` in meta when non-empty.
     - If subheader used `company` (title was empty), **do not** repeat company in meta.
     - Then append `dates` and `location` when non-empty.
     - Join with `" • "` (existing `_resume_site_markers` will turn `" • "` into NBSP•).
     - If no meta parts, omit the `<p>`.
   - **Body:** if `accomplishments` non-empty, emit `<div class="role-accomplishments prose-block">{escaped}</div>` (same `white-space: pre-wrap` as other prose — preserves paste newlines/bullets without inventing `<ul>` lead/bullet chrome).
   - Wrap each role in `<div class="role">…</div>`.
   - Return the concatenated role HTML (no outer section — caller owns `<section>` / `<h2>`).
   ⚠️ **Decision:** Subheader = title (company fallback); meta = company (when not already in the subheader) + dates + location. This is **consistent metadata**, not AST-993’s `Title • Company` / dates:place phrasing chrome or lead-vs-bullets split. Accomplishments stay **one** text block.
3. In `_emit_html_document` CSS (screen rules, not only `@media print`), add left-aligned role styles so role `h3` is not centered by the existing `h1, h2, h3 { text-align: center }` rule:
   ```css
   .role { margin: 10px 0 14px; }
   .role-subheader {
     text-align: left;
     font-family: var(--header-font-family);
     font-size: 16px;
     font-weight: 700;
     line-height: 1.25;
     margin: 8px 0 2px;
     color: var(--text-primary);
     text-transform: none;
     letter-spacing: normal;
   }
   .role-meta {
     text-align: left;
     font-family: var(--list-font-family);
     font-size: 13px;
     line-height: 1.35;
     margin: 0 0 6px;
     color: var(--text-secondary);
   }
   .role-accomplishments { margin: 0; }
   ```
   Keep the existing print rule `.role { page-break-inside: avoid; }` (already present).
4. Keep `_format_experience_value` for unexpected structured values on other paths; update its docstring to note experience job arrays are handled by `_emit_experience_jobs_html`, not this helper.
5. In `build_resume_from_job` / `build_base_resume` / `build_session_base_resume` debug blocks that compute `content_keys` as “string values with strip”, also treat a non-empty experience job array as present (e.g. include `"experience"` when `_is_experience_job_array(markers.get("experience"))` and the list is non-empty) so Style D `render_keys` is not falsely missing Experience after the array lands. Do **not** add new parse-hop debug (AST-996 / AST-997 own AC9).
6. Confirm all three public entry points already share `_emit_html_document` → `_emit_body_sections_html` (`build_base_resume`, `build_session_base_resume`, `build_resume` / `build_resume_from_job`) — no per-surface duplicate emit. Do **not** add a fourth builder.
7. Do **not** change cover-letter helpers (`_emit_cover_sections_html`, etc.).
8. Do **not** edit `candidate.filter_content_to_resume_structure` here — if arrays are dropped before emit, that is an AST-996 merge/precondition failure (stop + parent comment).

## Self-Assessment

**Scope:** `Single-Component` — builder HTML emit + one `BUILD_CONFIG` `body_kind` literal; no prompt/schema/UI ownership.

**Conf:** `high` — all three surfaces already share `_emit_body_sections_html`; AST-996 defines the wire shape and preserve helpers; current code already JSON-dumps lists, so the recognition gap is localized.

**Risk:** `Medium` — wrong subheader/meta join or accidental stringification would regress Session Paste / base / job-tailored Experience HTML; legacy string path must remain for pre-996 blobs.

## Code rules check

- §1.3 DRY: one `_emit_experience_jobs_html` used by the single body-emit path (session + base + job).
- §2.1: only `body_kind` literal in config; field names come from AST-996 contract (not re-hardcoded as a second schema).
- §2.4 / §2.6: no batch or state-machine changes.
- §3.3: builder stays core; continues to import `candidate` / `config` / `formatting` / `logging` only — no ui/external.
- §3.5: helpers `_emit_experience_jobs_html`; public builders unchanged in signature.
- §1.5.1: no new ungated debug; only extend existing `debug=True` `render_keys` honesty.
- §3.6: no repo-root `artifacts/` directory.

## Review (build stub)

**Publish ref:** `origin/sub/AST-994/AST-998-base-session-job-builders-experience-job-render`
**Plan path:** `docs/features/artifacts/ast-998-base-session-job-builders-experience-job-render.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `631db63d` | `BUILD_CONFIG` experience `body_kind` → `experience_jobs` |
| 2 | `cfa1c7cf` | shared `_emit_experience_jobs_html` + role CSS + legacy string path + `render_keys` honesty |

**Tip:** see `origin/sub/AST-994/AST-998-base-session-job-builders-experience-job-render` HEAD after this commit.

## Review (Radia — code-rubric.v1)

`[code-rubric] revision=1`

**Publish ref tip:** (see Linear / post-push SHA) on `origin/sub/AST-994/AST-998-base-session-job-builders-experience-job-render`
**Baseline:** `origin/dev`
**Overall:** DISCUSS

### What’s solid
- `body_kind` → `experience_jobs`; emit branches on `is_experience_job_array` (legacy string preserved).
- Shared `_emit_experience_jobs_html` + role CSS for base/session/job; markers before escape; empty roles omitted.
- Style D `render_keys` honesty via `_render_content_keys`; Betty `test`/`merge-tests` on builder tests only.

### Issues
**discuss (C4 stragglers):** Joan excluded debug/docs/engineer-test-tree/UI statutes that the tip brings in-scope via 996/997 merge + features/tests — all scored **conforms**.

### Recommended actions
No fix-now. Stragglers are process notes — resolve-child may proceed without product edits.

## Resolution

**Date:** 2026-07-28
**Review:** Radia `[code-rubric] revision=1` — Overall **DISCUSS**; **fix-now** none; discuss items are Joan C4 statute-exclusion stragglers (all scored **conforms** on tip) — no product changes.
**Outcome:** Clean resolve — no code delta vs `d5b0383b` (Radia docs tip). Proceed to User Testing per resolve-child / spawn direction.

