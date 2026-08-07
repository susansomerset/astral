<!-- linear-archive: AST-1009 archived 2026-08-05 -->

## Linear archive (AST-1009)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1009/education-lines-skills-category-grid-prior-list-resume-render-format  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** katherine  
**Priority / estimate:** Urgent / —  
**Parent:** AST-993 — Resume Render Format discrepancies  
**Blocked by / blocks / related:** parent: AST-993

### Description

## What this implements

Education as per-line emphasized credentials; technical skills as category grid; prior experience as competencies list with markers.

## Acceptance criteria

1. Prior Experience as competencies list, Education as per-line emphasized credentials, Technical Skills as a category grid (parent AC1).
2. Education lines and skill categories are not a single escaped dump; they show the per-line / per-category markup described above.

## Boundaries

Does **not** rework experience roles (sibling). Does **not** own header/meta/styles (sibling).

## Notes for planning

Depends on nested markers from sibling AST-1007.

## Git branch (authoritative)

Parent `ftr/ast-993-resume-render-format-discrepancies`; child `sub/AST-993/AST-1009-education-skills-prior`. Publish to `origin/sub/AST-993/AST-1009-education-skills-prior` only.

### Comments

#### radia — 2026-07-28T17:41:15.422Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1009
**Publish ref:** `9a9520de` on `origin/sub/AST-993/AST-1009-education-skills-prior`
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
| astral.config.config-source-of-truth | scoped | conforms | Emit separators grandfathered beside markers; no BUILD_CONFIG |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | No scoring thresholds |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No secrets/env values |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss repo-root `artifacts/**` / `scripts/spikes/**` |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Features plan docs only; no spike dumps |
| astral.docs.features-single-file-per-ticket | scoped | conforms | One features file per ticket (1009 + 1007 ancestry) |
| astral.git.betty-no-src-or-features | scoped | conforms | Engineer owns src/features; Betty on tests/bible |
| astral.git.engineer-test-tree-ban | scoped | conforms | Betty `test(AST-1009)` + one engineer `merge-tests` |
| astral.layers.core-vs-external-bright-line | scoped | conforms | Pure core HTML emit helpers |
| astral.layers.import-direction | scoped | conforms | No new cross-layer imports |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers/paths miss `scripts/**` |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | layers/paths miss `src/ui/**` / `config.py` |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | No coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | No consult / render_verdict |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | layers/paths miss `src/ui/**` |
| astral.standards.data-raises-caller-logs | scoped | conforms | No data-layer error handling |
| astral.standards.database-header-inventory | scoped | not-applicable | layers/paths miss `src/data/**` |
| astral.standards.debug-contract-gated | scoped | conforms | No new debug-contract emission |
| astral.standards.dry-and-focused-functions | scoped | conforms | Two focused emit helpers; prior reuses competencies-list |
| astral.standards.in-scope-only | scoped | conforms | Education/skills/prior emit only; no 1008/1010/1007 edits |
| astral.standards.logging-via-utils | scoped | conforms | No logging changes |
| astral.standards.no-cross-contamination | scoped | conforms | Product delta in `builder.py` emit neighborhood |
| astral.standards.no-hardcoded-sets | scoped | conforms | No new state/enum sets; fixture separators only |
| astral.standards.public-then-helpers | scoped | conforms | `_emit_education_list_html` / `_emit_skills_grid_html` beside body emit |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | layers/paths miss `src/utils/**` |
| astral.state.core-decides-transitions | scoped | conforms | No state transitions |
| astral.state.job-prior-states-enforced | scoped | conforms | No job state work |
| astral.state.no-daisy-chain-in-run | scoped | conforms | No dispatch run chaining |
| astral.ui.frontend-file-placement | scoped | not-applicable | layers/paths miss `src/ui/frontend/**` |
| astral.ui.naming-conventions | scoped | not-applicable | layers/paths miss `src/ui/**` |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | layers/paths miss ui/scripts/config |
| orch.git.betty-merge-tests-one-sha | universal | conforms | One `merge-tests(AST-1009): origin/tests 35f7f9b1…` |
| orch.git.commit-vocabulary | universal | conforms | plan/code/docs/test/merge-tests subjects |
| orch.git.flow-direction-inviolable | universal | conforms | Published to child `sub/AST-993/AST-1009-…` only |
| orch.git.ftr-sub-topology | universal | conforms | Child sub under parent ftr |
| orch.git.merge-on-checkout | universal | conforms | `origin/ftr/…` ancestor of tip |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No cherry-pick/rebase/force in child history |
| orch.git.no-dev-agent-branches | universal | conforms | Authoritative sub publish-ref |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Review in `astral-AST-993/` |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | No improvised separators beyond plan |
| orch.pipeline.plan-is-bible | universal | conforms | Stage 1 emit contracts implemented as planned |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Artifacts child only |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Entered from Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty owns tests/bible; engineer merge-tests only |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee remains Katherine |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Katherine stays assignee through Review Posted |
| orch.roles.pre-commit-path-bans | universal | conforms | Engineer `code()` on builder; tests via merge-tests |

## Pattern conformance

none cited

## Plan adherence

Diff matches Stage 1: education per-line strong + post-marker bullet; skills category grid via first `": "`; prior kept as `p.competencies-list`. No CSS / experience / markers helper changes vs AST-1007 tip. Self-Assessment **Single-Component** matches. Betty Stage 2 proof present (`TestAst1009EducationSkillsPrior`). Sibling AST-1008/1010 not smuggled; AST-1007 content is blockedBy ancestry only.

## Findings

**discuss (C4 straggler):** `astral.debug.spikes-under-debug-dir` — Joan excluded; in-scope via `docs/features/**`. Substance conforms.

**discuss (C4 straggler):** `astral.docs.features-single-file-per-ticket` — Joan excluded; in-scope on diff. Substance conforms.

**discuss (C4 straggler):** `astral.git.engineer-test-tree-ban` — Joan excluded; in-scope via tests/bible. Substance conforms (`test` + one `merge-tests`).

No **fix-now** findings.

## What’s solid

Localized emit helpers; post-marker education split; prior/competencies reuse; fixture-class names without AST-1010 CSS expansion.

## Notes

Joan plan-rubric verdict attached (APPROVED). Three-dot vs `origin/dev` includes AST-1007 ancestry (expected blockedBy).

**Recommended:** `resolve-child` — acknowledge C4 stragglers; no product code change required for them.

context_tokens≈48000

#### betty — 2026-07-28T17:38:18.709Z
1. `tests/component/core/test_builder.py::TestAst1009EducationSkillsPrior` — education per-line helpers + skills category grid + prior competencies-list; session/base/job HTML
2. `tests/component/core/test_builder.py::TestBuilderHelpers::test_emits_body_sections_and_cover_blocks` — existing body-section regression

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_builder.py::TestAst1009EducationSkillsPrior \
  tests/component/core/test_builder.py::TestBuilderHelpers::test_emits_body_sections_and_cover_blocks \
  -q
```

**Broken / obsolete:** none
**Integration:** no existing scenario asserts these section shapes — no revision

`origin/sub/AST-993/AST-1009-education-skills-prior` @ `210fc16b` (`merge-tests(AST-1009): origin/tests 35f7f9b1…`)

**Bible shasum:** `docs/test-bible/core/builder.md` → `3c8ee284d1913b147633770c7415d6966ffb06aa2c960902bab083a5ae3f40ff`

#### joan — 2026-07-28T17:25:50.097Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1009
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 body structure (header/roles/education/skills/prior) | Stage 1+2 for prior / education / technical skills only; experience→AST-1008; header→AST-1010 |
| AC2 nested markers not left literal | Relies on AST-1007 deep-walk; Stage 2 verifies no leftover `__`/`~~` in prior/skills text |
| AC3 Somerset lead vs bullets | N/A — boundary (AST-1008) |
| AC4 education/skills not a single escaped dump | Stage 1 helpers + Stage 2 ≥3 education lines / ≥8 skill-category nodes |
| AC5 meta description / tagline not body | N/A — boundary (AST-1010) |
| AC6 session/base/job surface parity | Stage 2 three-surface proof for these sections |
| AC7 embedded stylesheet | N/A — boundary (AST-1010; plan emits fixture class names only) |
| AC8 eye verify vs desired HTML | Stage 2 structure proof for the three sections (chrome/CSS remain siblings) |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 education + skills emit helpers; keep prior competencies-list | Parent Functional scope Education/skills/prior; child AC1+AC2; Boundaries (no experience/header/styles/markers) |
| Stage 2 three-surface fixture proof | Child AC1+AC2; Functional scope all shared builders; AC4; AC6 for these sections |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | Tests left to Betty; no merge-tests work |
| orch.git.commit-vocabulary | conforms | No forbidden commit subjects prescribed |
| orch.git.flow-direction-inviolable | conforms | Publish ref is child `sub/AST-993/AST-1009-…` only |
| orch.git.ftr-sub-topology | conforms | Child sub under parent ftr topology |
| orch.git.merge-on-checkout | conforms | No skip of merge-on-checkout duties |
| orch.git.no-cherry-pick-rebase-force | conforms | No cherry-pick/rebase/force |
| orch.git.no-dev-agent-branches | conforms | Authoritative sub publish ref, not Linear agent branch |
| orch.git.one-epic-worktree-per-parent | conforms | Single epic worktree; no extra |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Stage 2 stop+parent comment on unanticipated separators |
| orch.pipeline.plan-is-bible | conforms | Executable stages; no improvise path |
| orch.pipeline.project-scoped-queues | conforms | No cross-project queue work |
| orch.pipeline.status-gates-skill-entry | conforms | Stays within plan→build gate |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | Explicit ban on engineer tests/bible edits |
| orch.roles.chuckles-never-ticket-assignee | conforms | No assignee-policy contradiction |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer build after Plan Approved |
| orch.roles.pre-commit-path-bans | conforms | Files Changed in engineer-allowed product path |
| astral.agent.confidence-bounds | conforms | No graded confidence work |
| astral.agent.do-task-delegation | conforms | No do_task / AI work |
| astral.agent.grade-vector-validation | conforms | No grade vectors |
| astral.batch.batch-id-first | conforms | No batch claim APIs |
| astral.batch.batch-id-format | conforms | No batch_id generation |
| astral.batch.claim-process-release | conforms | No claim/process/release |
| astral.batch.entity-agent-responses-latest-only | conforms | No agent_data latest-ref work |
| astral.config.config-source-of-truth | conforms | No new config; emit separators grandfathered beside markers |
| astral.config.pass-threshold-vs-score-floor | conforms | No scoring thresholds |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env values |
| astral.git.betty-no-src-or-features | conforms | Engineer owns builder emit; Betty not editing src/features |
| astral.layers.core-vs-external-bright-line | conforms | Pure core HTML emit; no external I/O |
| astral.layers.import-direction | conforms | Core-only Files Changed; no new cross-layer imports |
| astral.patterns.coat-check-never-store-empty | conforms | No coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | conforms | No consult/render_verdict |
| astral.standards.data-raises-caller-logs | conforms | No data-layer error handling |
| astral.standards.debug-contract-gated | conforms | No new debug-contract lines |
| astral.standards.dry-and-focused-functions | conforms | Two focused emit helpers; prior reuses competencies-list |
| astral.standards.in-scope-only | conforms | Explicit sibling out-of-scope list (1007/1008/1010) |
| astral.standards.logging-via-utils | conforms | No logging changes |
| astral.standards.no-cross-contamination | conforms | Stays inside `src/core` |
| astral.standards.no-hardcoded-sets | conforms | No new state/enum sets; emit literals are fixture separators |
| astral.standards.public-then-helpers | conforms | `_emit_*` helpers beside existing emit neighborhood |
| astral.state.core-decides-transitions | conforms | No state transitions |
| astral.state.job-prior-states-enforced | conforms | No job state work |
| astral.state.no-daisy-chain-in-run | conforms | No dispatch run chaining |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths miss `src/core/builder.py`
- astral.debug.spikes-under-debug-dir — paths miss `src/core/builder.py`
- astral.docs.features-single-file-per-ticket — layers/paths miss core builder
- astral.git.engineer-test-tree-ban — paths miss (tests/bible not in Files Changed)
- astral.layers.scripts-exempt-from-layer-rules — layers/paths miss
- astral.layers.ui-config-driven-business-logic — layers/paths miss
- astral.patterns.require-auth-on-protected-endpoints — layers/paths miss
- astral.standards.database-header-inventory — layers/paths miss
- astral.standards.utils-data-late-import-only — layers/paths miss
- astral.ui.frontend-file-placement — layers/paths miss
- astral.ui.naming-conventions — layers/paths miss
- astral.ui.single-gunicorn-worker — layers/paths miss

## Findings

No `fix-now` or `discuss` findings. Post-marker `"\u00a0• "` education split and first `": "` skills split match the marker pass + parent fixture. Self-assessment (Single-Component / high / Medium) is honest. CSS polish correctly deferred to AST-1010 while this plan emits golden class/structure names.

— Joan

context_tokens≈75000

#### katherine — 2026-07-28T17:23:34.578Z
**Plan:** [docs/features/artifacts/ast-1009-education-skills-prior.md](https://github.com/susansomerset/astral/blob/sub/AST-993/AST-1009-education-skills-prior/docs/features/artifacts/ast-1009-education-skills-prior.md) on `origin/sub/AST-993/AST-1009-education-skills-prior` @ `8fbe3eeb`.

**Scope — Single-Component:** Emit-only change in `src/core/builder.py` — education per-line `<strong>` + bullet rest, skills `Category: items` → `skill-category` grid, prior kept as `competencies-list` (markers from AST-1007).

**Conf — high:** Parent golden HTML spells the three section shapes; prior already matches; education/skills are localized string-split emits beside existing summary/experience patterns.

**Risk — Medium:** Wrong post-marker bullet or colon split would garble education/skills HTML on session/base/job surfaces; no dispatch/DB impact.

---

# Education lines + skills category grid + prior list (Resume Render Format discrepancies)

**Linear:** [AST-1009](https://linear.app/astralcareermatch/issue/AST-1009/education-lines-skills-category-grid-prior-list-resume-render-format)
**Parent:** [AST-993](https://linear.app/astralcareermatch/issue/AST-993/resume-render-format-discrepancies) — Resume Render Format discrepancies
**Publish ref:** `origin/sub/AST-993/AST-1009-education-skills-prior`

Shared resume HTML builders still emit `education_certifications` and `technical_skills` as a single escaped dump inside one wrapper (`education-list` / `skills-grid`), and parent AC1/AC4 require golden-fixture structure instead: education as per-line paragraphs with the credential name in `<strong>` and the issuer/dates after a bullet separator; technical skills as a category grid (`Category: items` → `skill-category` with `h4` + items `<p>`); prior experience as the competencies-list style with markers already applied by AST-1007. This plan changes emit markup for those three body keys only — it does **not** rework experience role chrome (AST-1008), header/contact/meta/stylesheet expansion (AST-1010), or the markers vocabulary (AST-1007, already on `origin/ftr`).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/builder.py` | Replace education / technical-skills dumps in `_emit_body_sections_html` with per-line education list + category skills grid helpers; keep prior as `competencies-list` (markers via existing deep-walk); no CSS expansion, no experience/header/meta changes | core |

**Out of scope (do not touch):** `_emit_experience_jobs_html` / lead-vs-bullets / compact title-location (AST-1008); header `Name • Title`, contact join, meta description, embedded stylesheet expansion for `.education-list` / `.skills-grid` layout polish (AST-1010); `_resume_site_markers` / `_apply_resume_text_markers` / `_mark_resume_value` (AST-1007); cover-letter emit; `candidate.py` parse / schemas; `config.py` section catalog; `tests/`, bible (Betty).

## Emit contracts (this ticket)

Markers run **before** emit via `_apply_resume_text_markers` on all three resume surfaces. After that pass, `" • "` has already become `"\u00a0• "` (`NBSP` + `•` + space). Education / skills helpers must split on the **post-marker** separator, not re-apply markers.

### Prior experience

Keep the existing emit shape:

```html
<section aria-labelledby="prior-experience">
  <h2 id="prior-experience">…</h2>
  <p class="competencies-list">{escaped marked text}</p>
</section>
```

Do **not** change this branch except to leave it intact when editing neighboring `elif` arms. Markers are already applied on the string leaf.

### Education & certifications

Source is a **string** (schema `str`) with one credential per line (newlines), as in the parent fixture. Emit:

```html
<div class="education-list">
  <p><strong>{credential}</strong>\u00a0• {rest}</p>
  …
</div>
```

Rules:

1. Split on `str.splitlines()`, keep non-empty stripped lines only.
2. For each line, split on the **first** `"\u00a0• "` (post-marker bullet). Left = credential (wrapped in `<strong>` after `html.escape`); right = issuer/dates (escaped, no strong).
3. If a line has no `"\u00a0• "`, emit `<p><strong>{escaped whole line}</strong></p>` (credential-only line — do not invent an issuer).
4. Do **not** wrap the whole section in a single `<p class="prose-block">`.

### Technical skills

Source is a **string** with one `Category: items` line per newline. Emit:

```html
<div class="skills-grid">
  <div class="skill-category">
    <h4>{category}</h4>
    <p>{items}</p>
  </div>
  …
</div>
```

Rules:

1. Split on `str.splitlines()`, keep non-empty stripped lines only.
2. For each line, split on the **first** `": "` (colon + space). Left = category → `<h4>` (escaped); right = items → `<p>` (escaped; markers already applied).
3. If a line has no `": "`, emit one `skill-category` with **no** `<h4>` and a single `<p>{escaped whole line}</p>` so content is not dropped.
4. Do **not** emit one outer `skill-category` wrapping the entire multi-line dump.

⚠️ **Decision:** Separator and category-split literals stay in `builder.py` next to the existing marker helpers (same grandfather as AST-1007 / AST-998). Do **not** add a `BUILD_CONFIG` block for `"\u00a0• "` or `": "` — these are emit conventions tied to the marker pass and the golden fixture, not environment-tunable behavior. Stylesheet rules for grid/education polish remain AST-1010; this ticket only emits the golden class/structure names already referenced in the fixture (`.education-list`, `.skills-grid`, `.skill-category`).

## Stage 1: Education + skills emit helpers; keep prior competencies-list

**Done when:** Given marked string values shaped like the parent fixture’s Prior Experience / Education & Certifications / Technical Skills sections, `_emit_body_sections_html` (via the three public builders) produces: prior as one `p.competencies-list`; education as `div.education-list` with one `<p><strong>…</strong>\u00a0• …</p>` per non-empty line; skills as `div.skills-grid` with one `div.skill-category` per non-empty `Category: items` line (`h4` + `p`). No single escaped dump remains for education or skills. Experience / header / CSS / markers helpers are unchanged.

1. In `src/core/builder.py`, add a private helper `_emit_education_list_html(text: str) -> str` immediately above `_emit_body_sections_html` (or directly below it in the helpers section — same neighborhood as `_emit_experience_jobs_html`):
   - Implement the education contract above (splitlines → per-line strong + post-marker bullet rest).
   - Return the inner HTML for the education section body only (the `div.education-list` … block, indented consistently with neighboring section bodies — leading spaces matching current `      <div class="education-list">…` style).
   - Use `html.escape` on credential and rest separately; do not escape the `<strong>` tags.
2. In `src/core/builder.py`, add a private helper `_emit_skills_grid_html(text: str) -> str` beside the education helper:
   - Implement the skills contract above (splitlines → per-line category / items).
   - Return the inner `div.skills-grid` … block with the same indentation conventions.
3. In `_emit_body_sections_html`, replace the `education_certifications` arm so that after the existing empty-text skip, it builds the section with `_emit_education_list_html(str(text))` instead of `<div class="education-list"><p class="prose-block">{inner}</p></div>`. Keep the same `<section aria-labelledby=…>` / `<h2>` wrapper pattern used by neighboring arms.
4. Replace the `technical_skills` arm to use `_emit_skills_grid_html(str(text))` instead of the single-category dump.
5. Leave the `prior_experience` arm as `p.competencies-list` with the already-escaped `inner` (or equivalent: escape once after confirming markers already ran — same as today). Do not convert prior into a list or grid.
6. Do **not** change how `dict`/`list` non-string values are coerced via `_format_experience_value` before these arms — schemas keep these keys as `str`; structured dumps stay the existing JSON visibility path if somehow present.
7. Do **not** edit `_emit_html_document` CSS, `_emit_experience_jobs_html`, header/contact join, cover letter, or marker helpers.
8. Do **not** edit `tests/` or bible — Betty owns assertions after Code Complete.

## Stage 2: Three-surface fixture proof (manual / build verification)

**Done when:** With in-memory / session content whose `prior_experience`, `education_certifications`, and `technical_skills` strings match the parent AST-993 fixture lines (including `__` / `~~` on skills and prior), each of `build_session_base_resume`, `build_base_resume`, and `build_resume_from_job` yields HTML where: Prior Experience is one `p.competencies-list` with no leftover literal `__`/`~~`; Education has ≥3 `div.education-list > p > strong` lines (CSM, CSPO, UW Milwaukee) and is not one `prose-block` dump; Technical Skills has ≥8 `div.skill-category` nodes with `h4` category titles (e.g. `Program & Delivery`, `AI Development & Orchestration`) and item `<p>` text without literal `__`/`~~`. Experience role chrome, header composition, and meta description are **not** asserted here.

1. During **build-child**, exercise the three public builders with fixture-shaped section strings (REPL, or ad-hoc under `debug/spikes/AST-1009/` — **do not** commit spike output; **do not** add repo-root `artifacts/`).
2. Confirm HTML source structure for the three sections matches the contracts in this plan.
3. If a fixture line fails the split rules in a way this plan did not anticipate (e.g. education using a different bullet glyph), **stop**, comment on the **parent** AST-993 with the Stage blocked template, and wait — do not improvise alternate separators.

## Self-Assessment

**Scope:** `Single-Component` — emit helpers and `_emit_body_sections_html` arms in `src/core/builder.py` only; no UI, config, parse, or CSS expansion.

**Conf:** `high` — golden HTML in the parent description is explicit; prior already matches; education/skills are localized string-split emits beside the existing summary paragraph and experience job-array patterns; markers already deep-walked by AST-1007.

**Risk:** `Medium` — wrong split (pre- vs post-marker bullet, or splitting on every colon) would garble education/skills HTML across session/base/job surfaces; impact is resume body typography/structure, not dispatch or DB state.

## Code rules check

- §1.3 DRY: two focused helpers for education/skills; prior reuses existing competencies-list arm; no duplicated marker vocabulary.
- §1.1 / scope isolation: only `builder.py` emit for these three keys; siblings own experience and header/styles.
- §2.1: no new config keys; emit separators stay next to existing marker literals (grandfathered).
- §2.4 / §2.6: N/A (no batch/state-machine work).
- §3.3: core-only change; no new cross-layer imports.
- §3.5 naming: `_emit_education_list_html` / `_emit_skills_grid_html` beside existing `_emit_*` helpers.
- §3.6: spike/debug under `debug/spikes/AST-1009/` only if used; never commit spike dumps.

## Review (build stub)

**Publish ref:** `origin/sub/AST-993/AST-1009-education-skills-prior`
**Plan path:** `docs/features/artifacts/ast-1009-education-skills-prior.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `8c4539e3` / `d2765707` | Education per-line + skills category grid emit; prior competencies-list kept |
| 2 | `35f7f9b1` | Betty three-surface fixture proof |

## Radia review (code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1009
**Publish ref tip (pre-docs):** `210fc16b` — `origin/sub/AST-993/AST-1009-education-skills-prior`
**Overall:** DISCUSS

### What’s solid

- Stage 1 matches plan: `_emit_education_list_html` / `_emit_skills_grid_html` beside `_emit_body_sections_html`; post-marker `"\u00a0• "` education split; first `": "` skills split; prior stays `p.competencies-list`; no CSS / experience / markers changes.
- Betty `TestAst1009EducationSkillsPrior` covers education-list / skills-grid / prior structure.
- Self-Assessment Single-Component holds; AST-1008/1010/1007 boundaries respected (1007 present via blockedBy merge only).

### Issues

**discuss (C4 straggler):** `astral.debug.spikes-under-debug-dir` — excluded at plan time; in-scope on diff via `docs/features/**`. Substance **conforms**.

**discuss (C4 straggler):** `astral.docs.features-single-file-per-ticket` — excluded at plan time; in-scope on diff. Substance **conforms** (one features file per ticket; AST-1007 plan is dependency ancestry).

**discuss (C4 straggler):** `astral.git.engineer-test-tree-ban` — excluded at plan time; in-scope via Betty bible/tests. Substance **conforms** (`test(AST-1009)` + one `merge-tests(AST-1009)`).

No **fix-now** product findings.

### Recommended actions

Engineer (`resolve-child`): acknowledge C4 stragglers — no product code change required for those three.

## Resolution

**Date:** 2026-07-28  
**Outcome:** clean — no product code changes.

Acknowledged Radia’s three **discuss (C4 straggler)** items (`astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`). Each was Joan-excluded at plan time, in-scope on the three-dot diff, and marked **conforms** in substance. No **fix-now** items. Publish tip after resolve remains product+Betty+Radia stack on `origin/sub/AST-993/AST-1009-education-skills-prior`.

