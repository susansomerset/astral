<!-- linear-archive: AST-1010 archived 2026-08-05 -->

## Linear archive (AST-1010)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1010/headercontact-ats-meta-description-embedded-styles-resume-render  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** katherine  
**Priority / estimate:** Urgent / —  
**Parent:** AST-993 — Resume Render Format discrepancies  
**Blocked by / blocks / related:** parent: AST-993

### Description

## What this implements

Header/contact match desired composition; tagline feeds HTML meta description (`Resume of <Candidate>, <title>, specializing in <tagline>`) and is not shown as a body line; expand embedded stylesheet for fonts/structure needed by experience/education/skills layout.

## Acceptance criteria

1. Header (`Name • Title` + contact) matches desired composition (parent AC1).
2. The document `<head>` includes a meta description of the form `Resume of <Candidate>, <title>, specializing in <tagline>`.
3. Embedded stylesheet supports the role/education/skills/header layout without requiring an external legacy CSS file.

## Boundaries

Does **not** own experience/education/skills emit logic (siblings). No external `styles07.css` swap.

## Notes for planning

Depends on nested markers from sibling AST-1007.

## Git branch (authoritative)

Parent `ftr/ast-993-resume-render-format-discrepancies`; child `sub/AST-993/AST-1010-header-contact-meta-styles`. Publish to `origin/sub/AST-993/AST-1010-header-contact-meta-styles` only.

### Comments

#### chuckles — 2026-07-28T17:45:18.871Z
[merge-child] blocked: validate-sub-log — git pull merge on sub (`Merge remote-tracking branch 'origin/ftr/…'`). Also sub not stacked on current `origin/ftr/ast-993-resume-render-format-discrepancies` (AST-1008 tip). @Katherine Johnson — on epic worktree: fetch, checkout `sub/AST-993/AST-1010-header-contact-meta-styles`, merge `origin/ftr/ast-993-resume-render-format-discrepancies` with a proper non-pull merge message (no `Merge remote-tracking branch`), ensure publish tip has ftr as ancestor, push `origin/sub/AST-993/AST-1010-header-contact-meta-styles` only. Do not push origin/dev.

— Chuckles

#### radia — 2026-07-28T17:43:47.547Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1010
**Publish ref:** `9dbb4242` on `origin/sub/AST-993/AST-1010-header-contact-meta-styles`
**Overall:** DISCUSS

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | conforms | No graded confidence / consult math |
| astral.agent.do-task-delegation | scoped | conforms | No AI / do_task work |
| astral.agent.grade-vector-validation | scoped | conforms | No grade vectors |
| astral.batch.batch-id-first | scoped | conforms | No batch claim APIs |
| astral.batch.batch-id-format | scoped | conforms | No batch_id generation |
| astral.batch.claim-process-release | scoped | conforms | No claim/process/release |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | No agent_data latest-ref work |
| astral.config.config-source-of-truth | scoped | conforms | Tagline schema + structure ids in `config.py`; CSS uses existing style tokens |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | No scoring thresholds |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No secrets/env values |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss repo-root `artifacts/**` / `scripts/spikes/**` |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Plan docs only under `docs/features/**`; no spike dumps |
| astral.docs.features-single-file-per-ticket | scoped | conforms | One features file per ticket; sibling plans are ancestry |
| astral.git.betty-no-src-or-features | scoped | conforms | Engineer owns src/config/features; Betty on tests/bible |
| astral.git.engineer-test-tree-ban | scoped | conforms | Test tree via Betty `test(AST-1010)` + one `merge-tests` |
| astral.layers.core-vs-external-bright-line | scoped | conforms | No external I/O in core emit |
| astral.layers.import-direction | scoped | conforms | core + utils only; no new illegal imports |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers/paths miss `scripts/**` |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | Config contract only; no React business logic |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | No coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | No consult / render_verdict |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | layers/paths miss `src/ui/**` |
| astral.standards.data-raises-caller-logs | scoped | conforms | No data-layer error handling |
| astral.standards.database-header-inventory | scoped | not-applicable | layers/paths miss `src/data/**` |
| astral.standards.debug-contract-gated | scoped | conforms | No new debug-contract emission |
| astral.standards.dry-and-focused-functions | scoped | conforms | One header/meta path in `_emit_html_document` |
| astral.standards.in-scope-only | scoped | conforms | `code(AST-1010)` is header/meta/CSS + tagline config only; experience still `role-subheader` |
| astral.standards.logging-via-utils | scoped | conforms | No logging changes |
| astral.standards.no-cross-contamination | scoped | conforms | Product stays in builder emit shell + `config.py` |
| astral.standards.no-hardcoded-sets | scoped | conforms | Structure ids via config; no new state enums |
| astral.standards.public-then-helpers | scoped | conforms | Changes inside existing `_emit_html_document` / config neighborhoods |
| astral.standards.utils-data-late-import-only | scoped | conforms | No utils→data imports in config touch |
| astral.state.core-decides-transitions | scoped | conforms | No state transitions |
| astral.state.job-prior-states-enforced | scoped | conforms | No job state work |
| astral.state.no-daisy-chain-in-run | scoped | conforms | No dispatch run chaining |
| astral.ui.frontend-file-placement | scoped | not-applicable | layers/paths miss `src/ui/frontend/**` |
| astral.ui.naming-conventions | scoped | not-applicable | layers/paths miss `src/ui/**` |
| astral.ui.single-gunicorn-worker | scoped | conforms | Touches `config.py` but not RAILWAY worker count |
| orch.git.betty-merge-tests-one-sha | universal | conforms | One `merge-tests(AST-1010): origin/tests 87c99e5f…` |
| orch.git.commit-vocabulary | universal | conforms | plan/code/docs/test/merge-tests subjects |
| orch.git.flow-direction-inviolable | universal | conforms | Published to child `sub/AST-993/AST-1010-…` only |
| orch.git.ftr-sub-topology | universal | conforms | Child sub under parent ftr |
| orch.git.merge-on-checkout | universal | conforms | `origin/ftr/…` ancestor of tip at review |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No cherry-pick/rebase/force in child history |
| orch.git.no-dev-agent-branches | universal | conforms | Authoritative sub publish-ref |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Review in `astral-AST-993/` |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | No invent-tagline improvisation |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–3 implemented as planned |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Artifacts child only |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Entered from Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty owns tests/bible; engineer merge-tests only |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee remains Katherine |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Katherine stays assignee through Review Posted |
| orch.roles.pre-commit-path-bans | universal | conforms | Engineer `code()` touched builder+config only |

## Pattern conformance

none cited

## Plan adherence

Diff matches Stages 1–3: optional `candidate_tagline` contract + CONTACT exclusion; ` • ` header join; ATS meta only when name/title/tagline all present; no tagline body section; embedded CSS for golden classes; no external `styles07.css`. Stage 4 proof via Betty `TestAst1010HeaderContactMetaStyles`. Self-Assessment Single-Component matches. Sibling experience/education emit not in `code(AST-1010)`.

## Findings

**discuss (C4 straggler):** `astral.debug.spikes-under-debug-dir` — Joan excluded; in-scope via `docs/features/**`. Substance conforms.

**discuss (C4 straggler):** `astral.docs.features-single-file-per-ticket` — Joan excluded; in-scope on diff. Substance conforms.

**discuss (C4 straggler):** `astral.git.engineer-test-tree-ban` — Joan excluded; in-scope via tests/bible. Substance conforms.

No **fix-now** findings.

## What’s solid

Clean header/meta/CSS + tagline plumbing; experience tip still `role-subheader` until AST-1008 lands on ftr.

## Notes

Joan plan-rubric verdict attached (APPROVED). Three-dot vs `origin/dev` also carries AST-1007 ancestry + sibling plan/tests SHAs; product scope of `8a00e5eb` remains header/meta/CSS + config.

**Recommended:** `resolve-child` — acknowledge C4 stragglers; no product code change required for them.

context_tokens≈52000

#### betty — 2026-07-28T17:40:36.961Z
1. `tests/component/core/test_builder.py::TestAst1010HeaderContactMetaStyles` — `Name\u00a0• Title` header; ATS meta present/omit; tagline excluded from header/main; golden CSS selectors; no `styles07.css`
2. `tests/component/utils/test_config.py::TestAst1010CandidateTaglineConfig` — optional `candidate_tagline` contract + contact-adjacent structure orders
3. `tests/component/utils/test_config.py::TestAst517ResumeStructureConfig` — default catalog still equals known ids
4. `tests/component/core/test_builder.py::TestAst1007NestedTypographyMarkers` — nested markers regression

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_builder.py::TestAst1010HeaderContactMetaStyles \
  tests/component/utils/test_config.py::TestAst1010CandidateTaglineConfig \
  tests/component/utils/test_config.py::TestAst517ResumeStructureConfig \
  tests/component/core/test_builder.py::TestAst1007NestedTypographyMarkers \
  -q
```

**Broken / obsolete:** none for this ticket’s header/meta/CSS surface.
**Integration:** no existing scenario asserts resume header/meta/CSS — no revision.

`origin/sub/AST-993/AST-1010-header-contact-meta-styles` @ `d446ab31` (`merge-tests(AST-1010): origin/tests 87c99e5f…`)

**Bible shasum:**
- `docs/test-bible/core/builder.md` → `daf87117577b943212d287c61581292a967aafa71b5774bc7bd5aa385faa94ee`
- `docs/test-bible/utils/config.md` → `4dd5a516616ba9d9103a85cfca3b1d400dbd25774462dd712c3ded80823c8eff`

#### joan — 2026-07-28T17:26:39.581Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1010
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 body structure (header Name • Title + contact portion) | Stage 2 header join + contact span; body section markup N/A — siblings AST-1008/1009 |
| AC2 nested markers | N/A — boundary (AST-1007); markers assumed already applied before emit |
| AC3 Somerset lead vs bullets | N/A — boundary (AST-1008) |
| AC4 education/skills markup | N/A — boundary (AST-1009); Stage 3 CSS readiness only |
| AC5 meta description from tagline (not body) | Stage 1 `candidate_tagline` contract + Stage 2 meta emit + Stage 4 omit/present proof |
| AC6 session/base/job surface parity | Stage 4 three-surface verification for header/meta/CSS |
| AC7 embedded stylesheet (no external styles07) | Stage 3 CSS expansion; explicitly bans external link |
| AC8 eye verify | Stage 4 inspection of header/meta/CSS selectors |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 optional `candidate_tagline` config + contact-adjacent structure | Functional scope “Header and contact” / tagline feeds meta not body; Boundaries (no Manage Tasks prompt redesign); child AC2 plumbing |
| Stage 2 header `\u00a0• ` join + ATS meta | Parent AC1 header composition; AC5 meta form; child AC1–AC2 |
| Stage 3 embedded CSS for golden classes | Parent AC7; child AC3; Functional scope stylesheet coverage for sibling layouts |
| Stage 4 three-surface verification | AC6 typography/header/meta parity; child AC verification |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | Tests left to Betty |
| orch.git.commit-vocabulary | conforms | No forbidden commit subjects prescribed |
| orch.git.flow-direction-inviolable | conforms | Publish ref is child `sub/AST-993/AST-1010-…` only |
| orch.git.ftr-sub-topology | conforms | Child sub under parent ftr |
| orch.git.merge-on-checkout | conforms | No skip of merge-on-checkout |
| orch.git.no-cherry-pick-rebase-force | conforms | No cherry-pick/rebase/force |
| orch.git.no-dev-agent-branches | conforms | Authoritative sub publish ref |
| orch.git.one-epic-worktree-per-parent | conforms | Single epic worktree |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Stop+parent escalate if tagline never returned / assumptions fail |
| orch.pipeline.plan-is-bible | conforms | Stages/steps binding and executable |
| orch.pipeline.project-scoped-queues | conforms | No cross-project queue work |
| orch.pipeline.status-gates-skill-entry | conforms | Stays in plan→build gate |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | Explicit ban on engineer tests/bible |
| orch.roles.chuckles-never-ticket-assignee | conforms | No assignee-policy contradiction |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer build after Plan Approved |
| orch.roles.pre-commit-path-bans | conforms | Files Changed in engineer-allowed paths |
| astral.agent.confidence-bounds | conforms | No graded confidence work |
| astral.agent.do-task-delegation | conforms | No new do_task orchestration |
| astral.agent.grade-vector-validation | conforms | No grade vectors |
| astral.batch.batch-id-first | conforms | No batch claim APIs |
| astral.batch.batch-id-format | conforms | No batch_id generation |
| astral.batch.claim-process-release | conforms | No claim/process/release |
| astral.batch.entity-agent-responses-latest-only | conforms | No agent_data latest-ref work |
| astral.config.config-source-of-truth | conforms | Tagline schema + structure ids in `config.py`; CSS reuses existing style tokens |
| astral.config.pass-threshold-vs-score-floor | conforms | No scoring thresholds |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env values |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src/config; Betty not editing |
| astral.layers.core-vs-external-bright-line | conforms | No external I/O in core |
| astral.layers.import-direction | conforms | core + utils only; no illegal imports |
| astral.layers.ui-config-driven-business-logic | conforms | Config contract only; no React business logic |
| astral.patterns.coat-check-never-store-empty | conforms | No coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | conforms | No consult |
| astral.standards.data-raises-caller-logs | conforms | No data-layer error handling |
| astral.standards.debug-contract-gated | conforms | No new debug-contract lines |
| astral.standards.dry-and-focused-functions | conforms | One meta/header path in `_emit_html_document` |
| astral.standards.in-scope-only | conforms | Explicit sibling emit / prompts / cover-letter / external CSS out of scope |
| astral.standards.logging-via-utils | conforms | No logging changes |
| astral.standards.no-cross-contamination | conforms | Stays in core/utils |
| astral.standards.no-hardcoded-sets | conforms | Structure ids via config; no new state enums |
| astral.standards.public-then-helpers | conforms | Changes inside existing emit/config neighborhoods |
| astral.standards.utils-data-late-import-only | conforms | No utils→data imports planned |
| astral.state.core-decides-transitions | conforms | No state transitions |
| astral.state.job-prior-states-enforced | conforms | No job state work |
| astral.state.no-daisy-chain-in-run | conforms | No dispatch chaining |
| astral.ui.single-gunicorn-worker | conforms | Touches config.py but not RAILWAY worker count |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths miss Files Changed
- astral.debug.spikes-under-debug-dir — paths miss Files Changed
- astral.docs.features-single-file-per-ticket — layers/paths miss
- astral.git.engineer-test-tree-ban — paths miss
- astral.layers.scripts-exempt-from-layer-rules — layers/paths miss
- astral.patterns.require-auth-on-protected-endpoints — layers/paths miss
- astral.standards.database-header-inventory — layers/paths miss
- astral.ui.frontend-file-placement — layers/paths miss
- astral.ui.naming-conventions — layers/paths miss

## Findings

**acceptable:** Session-paste population of `candidate_tagline` relies on optional `craft_resume_base` schema without Manage Tasks prompt edits (parent boundary). Plan correctly forbids inventing tagline text and documents parent escalate if the model never returns the field — Stage 4 still proves emit when the key is present.

**acceptable:** Parent desired-HTML fixture meta omits the comma before `specializing`; structured AC5 / child AC use `Resume of {name}, {title}, specializing in {tagline}`. Plan follows the AC template (correct fidelity).

No `fix-now` or `discuss` findings. Self-assessment (Single-Component / high / Medium) is honest.

— Joan

context_tokens≈78000

#### katherine — 2026-07-28T17:24:32.137Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-993/AST-1010-header-contact-meta-styles/docs/features/artifacts/ast-1010-header-contact-meta-styles.md

**Scope:** `Single-Component` — optional `candidate_tagline` contract in `config.py` (contact-adjacent) plus header join, ATS meta emit, and embedded CSS expansion in `builder.py` only.

**Conf:** `high` — `_emit_html_document` already owns header/contact/CSS; AST-294 anticipated optional tagline; body exclusion via `RESUME_STRUCTURE_CONTACT_SECTION_IDS` is established; sibling emit chrome stays out of scope.

**Risk:** `Medium` — bad meta escaping or tagline leaking into the body breaks ATS/PDF metadata and golden header composition on all three resume surfaces; `.contact` CSS changes are immediately visible.

---

# Header/contact + ATS meta description + embedded styles (Resume Render Format discrepancies)

**Linear:** [AST-1010](https://linear.app/astralcareermatch/issue/AST-1010/headercontact-ats-meta-description-embedded-styles-resume-render)
**Parent:** [AST-993](https://linear.app/astralcareermatch/issue/AST-993/resume-render-format-discrepancies) — Resume Render Format discrepancies
**Publish ref:** `origin/sub/AST-993/AST-1010-header-contact-meta-styles`

Shared resume HTML builders already emit a header (`Name` + optional ` • Title`) and a single contact span, with an embedded `<style>` block driven by `BUILD_CONFIG["default_style"]`. Parent AC1 / AC5 / AC7 still fail: the name–title separator is not the legacy NBSP bullet spacing; there is no `<meta name="description">` from a paste tagline; the tagline has no render-key home so it cannot feed meta without appearing as body content; and the embedded stylesheet lacks rules for the golden-layout classes siblings will emit (`.role-header`, `.compact-title`, `.compact-location`, `.role-description`, richer `.education-list` / `.skills-grid` / `.skill-category`). This plan owns header/contact composition, optional `candidate_tagline` plumbing for ATS meta only, and stylesheet expansion — it does **not** own experience/education/skills emit markup (AST-1008 / AST-1009), nested markers (AST-1007, already on `ftr`), Manage Tasks prompt text, cover-letter HTML, or an external `styles07.css` link.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Optional `candidate_tagline` on craft schema + `BUILD_CONFIG` artifact_shapes / supported_sections; add id to `RESUME_STRUCTURE_CONTACT_SECTION_IDS`, `RESUME_STRUCTURE_KNOWN_SECTION_IDS`, and `RESUME_STRUCTURE_DEFAULT` (contact-adjacent, not a body section) | utils |
| `src/core/builder.py` | Header join with legacy `\u00a0• `; emit `<meta name="description">` from name/title/tagline; never emit tagline in header/body; expand embedded CSS for golden header/role/education/skills classes; tighten `.contact` to one centered line | core |

**Out of scope (do not touch):** `_emit_experience_jobs_html` lead-vs-bullets / compact title–location emit (AST-1008); education per-line / skills category / prior-list emit structure (AST-1009); `_apply_resume_text_markers` / `_resume_site_markers` (AST-1007); Manage Tasks / `agent_task` prompt bodies; cover-letter emit; `<title>` string shape (parent: no legacy document-title chrome chase); external CSS file; `tests/`, bible (Betty).

## Stage 1: Optional `candidate_tagline` in config + resume structure

**Done when:** `candidate_tagline` is an optional string on the craft_resume_base / resume_content contracts; it is a known contact-adjacent section id (enabled in the default structure, excluded from body emission via `RESUME_STRUCTURE_CONTACT_SECTION_IDS`); `filter_content_to_resume_structure` keeps a non-empty tagline string when present in content; no Manage Tasks prompt files are edited.

1. In `src/utils/config.py`, add `"candidate_tagline": {"type": "str", "required": False}` to:
   - `TASK_CONFIG["craft_resume_base"]["response_schema"]` (after `candidate_contact_detail`)
   - `BUILD_CONFIG["artifact_shapes"]["resume_content"]` (after `candidate_contact_detail`)
2. In `BUILD_CONFIG["supported_sections"]`, add a `candidate_tagline` entry with `"heading_level": "none"`, `"body_kind": "prose"`, `"page_break_policy": "keep_with_next"` (peer to `candidate_title` — meta/header identity, not a section heading).
3. Extend `RESUME_STRUCTURE_CONTACT_SECTION_IDS` to include `"candidate_tagline"` (tuple order: name, title, tagline, contact — tagline before contact so body exclusion still covers it).
4. Extend `RESUME_STRUCTURE_KNOWN_SECTION_IDS` to include `"candidate_tagline"` in the same relative position among the contact trio.
5. In `RESUME_STRUCTURE_DEFAULT["sections"]`, add:
   ```python
   "candidate_tagline": {
       "id": "candidate_tagline",
       "title": "Candidate Tagline",
       "enabled": True,
       "order": 2,  # after title (1); bump candidate_contact_detail order to 3; shift later sections by +1
       "job_agent_editable": False,
   },
   ```
   Re-number existing `order` values for `candidate_contact_detail` and all later default sections so orders stay unique and ascending (contact was 2 → 3; professional_summary 3 → 4; … through technical_skills).
   ⚠️ **Decision:** Key name is `candidate_tagline` (same `candidate_*` spine as name/title/contact). It is contact-adjacent identity for ATS meta, not a new body section catalog entry with its own `<section>`. Parent forbids Manage Tasks prompt redesign — do **not** edit `agent_task` prompt content; optional schema + structure only so parse may return the field and filter will keep it. If UAT shows the model never returns `candidate_tagline`, escalate on parent AST-993 — do not invent tagline text from summary/title/contact in the builder.
6. Do **not** add admin UI field rows unless an existing admin field list for base_resume already enumerates the contact trio in the same config neighborhood and omitting tagline would leave a broken parallel — if such a list exists next to the trio (e.g. artifact field catalog around `candidate_contact_detail`), add one optional `{key: "candidate_tagline", label: "Candidate Tagline", type: "str"}` entry; otherwise leave admin lists alone.

## Stage 2: Header composition + ATS meta description in `_emit_html_document`

**Done when:** For a markers dict with non-empty `candidate_name`, `candidate_title`, and `candidate_tagline`, `_emit_html_document` (via all three public resume builders) produces (a) `<h1>` text `Name\u00a0• Title` (after escape; markers already applied on name/title strings), (b) one `.contact` span with the contact string (unchanged field source), (c) `<meta name="description" content="Resume of {name}, {title}, specializing in {tagline}">` with HTML-escaped attribute values from the marker-applied strings, and (d) **no** visible tagline under the header or in `<main>`. When any of name/title/tagline is empty/missing, omit the meta description tag entirely (do not emit a partial or placeholder meta).

1. In `src/core/builder.py` `_emit_html_document`, after reading `name` / `title` / `contact` escapes, also read:
   ```python
   tagline_raw = str(render.get("candidate_tagline") or "").strip()
   tagline = html.escape(tagline_raw) if tagline_raw else ""
   ```
   (Markers already ran on the render dict before this helper; do not call `_resume_site_markers` again here.)
2. Build the `<h1>` inner HTML as:
   - both name and title non-empty: `f"{name}\u00a0• {title}"`
   - name only: `name`
   - title only (no name): `title`
   - neither: empty string
   ⚠️ **Decision:** Use `\u00a0• ` (NBSP before the bullet, regular space after) to match `_resume_site_markers` / contact separator convention — not a plain `" • "` join.
3. Keep contact markup as:
   ```html
   <div class="contact"><span>{contact}</span></div>
   ```
   Do not split contact into multiple spans/chips.
4. Build meta description only when `name`, `title`, and `tagline` are all non-empty after the escapes above (empty escape means missing input). Content string **before** attribute escape assembly:
   `Resume of {unescaped_name}, {unescaped_title}, specializing in {unescaped_tagline}`
   where the three pieces are the marker-applied raw strings (`str(render.get(...)).strip()`), then `html.escape` the **entire** content value for the attribute. Exact template (comma after name, comma after title, literal ` specializing in `):
   `Resume of {name}, {title}, specializing in {tagline}`.
5. Insert the meta tag in `<head>` after `<title>…</title>` and before `<style>`:
   ```html
   <meta name="description" content="{meta_esc}" />
   ```
   When the three fields are not all present, insert nothing (no empty meta).
6. Confirm `_structure_ordered_body_ids` / `_RESUME_BODY_KEYS` never include `candidate_tagline` (contact-set exclusion + body-keys tuple already omit it — do not add it to `_RESUME_BODY_KEYS` or `_KEY_TO_SECTION_ID`).
7. Do **not** change `_apply_profile_to_render_dict` to invent a tagline from profile (no profile tagline field). Session paste continues to supply header fields from parse section strings (`build_session_base_resume` already skips profile overwrite).
8. Do **not** change the document `<title>` text construction (leave `{name} — Resume` / `Resume` fallback).

## Stage 3: Expand embedded stylesheet for golden layout classes

**Done when:** The CSS string inside `_emit_html_document` includes rules that style the golden-fixture class names for header/contact and for the role / education / skills structures siblings will emit, without linking an external stylesheet; existing rules used by current emit (`.role-subheader`, `.role-meta`, `.competencies-list`, `.summary-intro`, etc.) remain so AST-994 emit still paints until AST-1008/1009 land.

1. In the embedded `css` f-string in `_emit_html_document`, **keep** existing rules for `:root`, `body`, `h1`/`h2`/`h3`, `.header`, `.contact` (modify `.contact` only as in step 2), `.content`, `.summary-intro`, `.competencies-list`, `.role`, `.role-subheader`, `.role-meta`, `.role-accomplishments`, cover/ATS/print blocks.
2. Change `.contact` so it is one centered line (not flex chips): remove `display: flex; flex-wrap: wrap; gap: 8px 16px; justify-content: center;` and use block centering consistent with `.competencies-list` / list stack (keep `margin`, `font-size`, `color`, and the shared `font-family` / `text-align: center` rule that already targets `.contact`).
3. **Add** the following rules (use existing CSS variables `--header-font-family`, `--body-font-family`, `--list-font-family`, `--text-primary`, `--text-secondary`, `--header-color`, `--accent-color`, `--max-width` — do not invent new `:root` tokens or new `BUILD_CONFIG` keys in this ticket):
   - `.role-header` — left-aligned block wrapping title + location; margin matching current `.role` header spacing.
   - `.compact-title` — left-aligned; header font; ~16px; weight 700; margin `8px 0 2px`; color `var(--text-primary)`; no uppercase / no letter-spacing stretch.
   - `.compact-location` — left-aligned; list font; ~13px; margin `0 0 6px`; color `var(--text-secondary)`.
   - `.role-description` — body font; left-aligned; margin `6px 0`; line-height ~1.25 (lead paragraph under role header).
   - `article.role` — same vertical margin as `.role` (siblings may emit `<article class="role">`).
   - `.role ul` — left-aligned body list; margin `6px 0 0`; padding-left standard list indent (~1.25em).
   - `.role li` — body font; line-height ~1.25; margin `0 0 4px`.
   - `.education-list` — block container; margin `6px 0 0`.
   - `.education-list p` — body font; left-aligned; margin `4px 0`; line-height ~1.25.
   - `.skills-grid` — block/grid container; margin `6px 0 0`; gap between categories ~8px (CSS grid with `1fr` columns or stacked block — pick **stacked block** with each `.skill-category { margin: 0 0 8px; }` so print stays simple).
   - `.skill-category h4` — header font; left-aligned; ~14px; weight 700; margin `0 0 2px`; color `var(--text-primary)`; no flanking rules (those stay on `h2` only).
   - `.skill-category p` — keep/extend the existing shared rule that already includes `.skill-category p` for list font + center; **override inside `.skills-grid .skill-category p`** to `text-align: left` and secondary color so category items match the golden left-aligned items line (do not change `.competencies-list` centering).
4. Do **not** add `<link rel="stylesheet" href="styles07.css">`. Do **not** emit role/education/skills HTML structure changes — only CSS readiness for sibling class names.
5. Do **not** edit `tests/` or bible — Betty owns fixture assertions after Code Complete.

## Stage 4: Three-surface verification (manual / build verification)

**Done when:** With an in-memory render (or session content) that supplies `candidate_name`, `candidate_title`, `candidate_tagline`, and `candidate_contact_detail` (markers optional), each of `build_session_base_resume`, `build_base_resume`, and `build_resume_from_job` produces HTML whose `<head>` contains the exact meta description form above, whose `<header>` has `Name\u00a0• Title` and one contact span with **no** tagline text in the header/main, and whose `<style>` contains the new class selectors from Stage 3. Spike output only under `debug/spikes/AST-1010/` if used — never commit spike dumps; never repo-root `artifacts/`.

1. During **build-child**, exercise the three public builders with a minimal content dict including `candidate_tagline` (string shaped like the parent fixture line: `Program Delivery • Cross-Functional Alignment • Cloud SaaS • AI-Assisted Engineering`).
2. Assert by inspection: meta content matches `Resume of …, …, specializing in …`; h1 uses NBSP-bullet join; tagline absent from body text; CSS source includes `.compact-title`, `.role-description`, `.skills-grid`, `.education-list`.
3. Repeat once with `candidate_tagline` omitted — confirm **no** `<meta name="description"` in the HTML.
4. If Stage 1–3 assumptions fail against current helpers (e.g. filter drops unknown keys despite CONTACT inclusion), **stop**, comment on **parent** AST-993 with the Stage blocked template, and wait — do not improvise.

## Self-Assessment

**Scope:** `Single-Component` — `config.py` optional tagline contract + contact-adjacent structure ids; `builder.py` header join, meta emit, and embedded CSS expansion only.

**Conf:** `high` — header/contact emit and embedded CSS already live in `_emit_html_document`; AST-294 already anticipated optional tagline; contact-section exclusion pattern is established; sibling emit chrome is explicitly out of scope.

**Risk:** `Medium` — wrong meta escaping or tagline leaking into body would break ATS/PDF metadata and golden header composition across session/base/job surfaces; CSS mistakes are visual-only until siblings emit new classes, but a bad `.contact` change is immediately user-visible.

## Code rules check

- §1.3 DRY: one meta builder path inside `_emit_html_document`; reuse existing escape + style merge; no second HTML document template.
- §1.1 / scope isolation: no experience/education/skills emit changes; no Manage Tasks prompts; no cover letter.
- §2.1: tagline contract and structure ids live in `config.py`; CSS continues to consume style tokens already merged from `BUILD_CONFIG["default_style"]`; no new magic marker pairs.
- §1.4: no new hardcoded state sets; CSS sizing follows existing embedded-px pattern rather than inventing unused type_scale wiring in this ticket.
- §2.4 / §2.6: N/A.
- §3.3: core + utils only; no new cross-layer imports.
- §3.5 naming: `candidate_tagline` matches `candidate_*` spine.
- §3.6: spikes under `debug/spikes/AST-1010/` only if used; never commit.

## Review (build stub)

**Publish ref:** `origin/sub/AST-993/AST-1010-header-contact-meta-styles`
**Plan path:** `docs/features/artifacts/ast-1010-header-contact-meta-styles.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1–3 | `8a00e5eb` | Optional `candidate_tagline` + header/meta emit + embedded golden CSS |
| 4 | `87c99e5f` | Betty three-surface meta/header/CSS + config coverage |

**Tip:** `8a00e5eb` on `origin/sub/AST-993/AST-1010-header-contact-meta-styles`

## Radia review (code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1010
**Publish ref tip (pre-docs):** `d446ab31` — `origin/sub/AST-993/AST-1010-header-contact-meta-styles`
**Overall:** DISCUSS

### What’s solid

- Stages 1–3 match plan: optional `candidate_tagline` in craft/BUILD/DATA_SHAPES + CONTACT/KNOWN/DEFAULT structure; `<h1>` uses `\u00a0• `; meta `Resume of {name}, {title}, specializing in {tagline}` only when all three present; tagline not in body keys; embedded CSS adds golden class rules without `styles07.css`; `.contact` no longer flex chips.
- Experience emit on this tip still AST-994 `role-subheader` — sibling emit not smuggled into `code(AST-1010)`.
- Betty `TestAst1010HeaderContactMetaStyles` covers meta present/omit + CSS selectors.

### Issues

**discuss (C4 straggler):** `astral.debug.spikes-under-debug-dir` — Joan excluded; in-scope via `docs/features/**`. Substance conforms.

**discuss (C4 straggler):** `astral.docs.features-single-file-per-ticket` — Joan excluded; in-scope on diff. Substance conforms (one features file per ticket; sibling plans are ancestry).

**discuss (C4 straggler):** `astral.git.engineer-test-tree-ban` — Joan excluded; in-scope via bible/tests. Substance conforms (`test(AST-1010)` + one `merge-tests(AST-1010)`).

No **fix-now** product findings.

### Recommended actions

Engineer (`resolve-child`): acknowledge C4 stragglers — no product code change required for those three.

## Resolution

**Date:** 2026-07-28  
**Outcome:** clean — no product code changes.

Acknowledged Radia’s three **discuss (C4 straggler)** items (`astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`). Each was Joan-excluded at plan time, in-scope on the three-dot diff, and marked **conforms** in substance. No **fix-now** items. Publish tip after resolve remains product+Betty+Radia stack on `origin/sub/AST-993/AST-1010-header-contact-meta-styles` (plus mandatory `origin/ftr` merge-on-checkout).
