<!-- linear-archive: AST-1020 archived 2026-08-05 -->

## Linear archive (AST-1020)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1020/embedded-stylesheet-golden-parity-take-2-resume-render-format  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1019 — Take 2: Resume Render Format discrepancies  
**Blocked by / blocks / related:** parent: AST-1019; blocks: AST-1021

### Description

## What this implements

Align the shared resume embedded stylesheet with the AST-1019 golden `<style>` block: contact flex, role/education/skills spacing and type, skills CSS grid, all-caps skills/competencies treatment, mobile and print rules, and any config-driven token updates needed for fonts/colors already partially correct. Does not own DOM emit changes beyond what CSS alone can fix.

## Acceptance criteria

1. Pasting the ticket’s input fixture through Session Resume Paste Parse → Open HTML yields HTML whose embedded stylesheet carries the golden rules from this ticket (fonts, accent/header colors, decorative `h2` rules, contact flex, education indent, skills grid, mobile and print blocks) — verifiable in the HTML `<style>` block and print/preview view.
2. In that render, experience roles show golden compact-title / compact-location / lead-paragraph / bullet spacing and typography; education shows the indented per-line credential layout; Technical Skills shows the multi-column category grid with uppercase category headings and item lines.
3. Contact renders as one centered flex line matching the golden treatment; header remains `Name • Title` with markers applied (AST-993 contract preserved) — for this fixture, `Susan Somerset • Senior Technical Program Manager` with non-breaking spaces from `__` markers.
4. No external stylesheet link appears; styles are embedded.
5. Candidate base-resume HTML and job-tailored resume HTML that share the builder family show the same cosmetic treatment for equivalent structured content.
6. Susan can verify by eye against the desired HTML in this ticket for the listed style/format/alignment gaps; no judgment call on “close enough” for those items.

## Boundaries

Does not own residual DOM emit / document title / meta string tweaks (sibling Ada). Does not rework AST-993 structural contracts. Does not change cover-letter HTML.

## Notes for planning

Parent AST-1019 Take 2 golden HTML+CSS is the stylesheet fixture. Prefer AST-993 landed / ftr stack. Config-driven style tokens stay in config.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/ast-1019-take-2-resume-render-format-discrepancies`, child `sub/AST-1019/<this-id>-<slug>`. Created at dispatch-parent. Publish to origin/<publish-ref> only.

### Comments

#### radia — 2026-07-28T20:27:36.766Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1020
**Publish ref:** bbb8eb4b5b3cea9d7200f6ba638ba306ae3b0e35
**Overall:** DISCUSS

Diff: `origin/dev...origin/sub/AST-1019/AST-1020-embedded-stylesheet-golden-parity` (product @ `24a466ce` + this `docs()` append).

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| orch.git.betty-merge-tests-one-sha | universal | conforms | One `merge-tests(AST-1020): origin/tests 4c04e20f` on sub tip |
| orch.git.commit-vocabulary | universal | conforms | `code`/`docs`/`test`/`merge-tests` vocabulary on AST-1020 commits |
| orch.git.flow-direction-inviolable | universal | conforms | Published forward to `origin/sub/AST-1019/…` only |
| orch.git.ftr-sub-topology | universal | conforms | Child sub under AST-1019 parent ftr topology |
| orch.git.merge-on-checkout | universal | conforms | No inventiveness vs merge-on-checkout |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No cherry-pick/rebase/force in history |
| orch.git.no-dev-agent-branches | universal | conforms | Authoritative sub publish-ref; no agent-named branch |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Review in astral-AST-1019 epic worktree |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branch |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Golden CSS fixture applied; no product fork |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–2 match plan Done-when + CSS contract |
| orch.pipeline.project-scoped-queues | universal | conforms | Single Artifacts child; no cross-project queue |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Reviewed from Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty `test` + `merge-tests`; engineer avoided test tree |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee remains Katherine |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Implementer stays assignee through review |
| orch.roles.pre-commit-path-bans | universal | conforms | Engineer commits only config + builder + features plan |
| astral.agent.confidence-bounds | scoped | conforms | No confidence/consult path touched |
| astral.agent.do-task-delegation | scoped | conforms | No `do_task` / agent assembly changes |
| astral.agent.grade-vector-validation | scoped | conforms | No grade/vector work |
| astral.batch.batch-id-first | scoped | conforms | No batch claim APIs |
| astral.batch.batch-id-format | scoped | conforms | No batch_id generation |
| astral.batch.claim-process-release | scoped | conforms | Not a batch processor |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | No agent_data / latest-refs |
| astral.config.config-source-of-truth | scoped | conforms | Text/border tokens in `BUILD_CONFIG["default_style"]["colors"]` |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | No scoring thresholds |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | Style literals only; no secrets/env |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss — no repo-root `artifacts/**` / `scripts/spikes/**` |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Plan file under `docs/features/`; no spike pollution |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Single `docs/features/artifacts/ast-1020-….md` |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty commits only tests/bible (+ merge-tests) |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer code/docs commits omit tests/bible |
| astral.layers.core-vs-external-bright-line | scoped | conforms | CSS emit stays core builder; no external |
| astral.layers.import-direction | scoped | conforms | No new imports; utils config + core only |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers/paths miss — no `scripts/**` |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | Config tokens only; no UI business logic |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | No coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | No consult/render_verdict |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | layers/paths miss — no `src/ui/**` |
| astral.standards.data-raises-caller-logs | scoped | conforms | No data-layer error/logging path |
| astral.standards.database-header-inventory | scoped | not-applicable | layers/paths miss — no `src/data/**` |
| astral.standards.debug-contract-gated | scoped | conforms | No debug-contract emission |
| astral.standards.dry-and-focused-functions | scoped | conforms | Single CSS path in `_emit_html_document` |
| astral.standards.in-scope-only | scoped | conforms | Stylesheet slice only; AST-1021 owns title/meta |
| astral.standards.logging-via-utils | scoped | conforms | No new logging |
| astral.standards.no-cross-contamination | scoped | conforms | Stays utils config + core builder |
| astral.standards.no-hardcoded-sets | scoped | conforms | Colors in config; spacing px literals per Stage 1 Decision |
| astral.standards.public-then-helpers | scoped | conforms | Edits existing helper CSS string |
| astral.standards.utils-data-late-import-only | scoped | conforms | No utils→data imports |
| astral.state.core-decides-transitions | scoped | conforms | No state transitions |
| astral.state.job-prior-states-enforced | scoped | conforms | No job state work |
| astral.state.no-daisy-chain-in-run | scoped | conforms | No dispatch daisy-chain |
| astral.ui.frontend-file-placement | scoped | not-applicable | layers/paths miss — no `src/ui/frontend/**` |
| astral.ui.naming-conventions | scoped | not-applicable | layers/paths miss — no `src/ui/**` |
| astral.ui.single-gunicorn-worker | scoped | conforms | Config colors only; no worker/RAILWAY knobs |

## Pattern conformance

none cited

## Plan adherence

Stages 1–2 match the combined plan: five color tokens + golden embedded CSS with cover/ATS/`.prose-block` appendages; `#prior-experience` print break always emitted; no emit/markup/title/meta/cover-letter scope creep into AST-1021. Self-Assessment Scope `Single-Component` matches the src footprint. Diff also carries Betty test/bible + prior sibling test history vs `origin/dev` — expected on sub tip after merge-tests.

## Findings

**discuss (straggler):** Joan excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, and `astral.git.engineer-test-tree-ban` against plan Files Changed; three-dot diff brings them in-scope (plan file + Betty test/bible trees). Each scores **conforms** — no product fix.

### What’s solid

Contact flex, skills grid, education indent, mobile block, always-on prior-experience print rule, config-driven text/border tokens, Astral appendages retained, no external stylesheet link.

### Recommended actions

Acknowledge stragglers (no code change). resolve-child → User Testing when clear.

**Notes:** Shared repo `core.hooksPath` currently points at astral-tests Betty hook; Radia `docs()` commit used epic worktree hooks via one-shot `-c` override (did not rewrite git config).

— Radia
context_tokens≈52000

#### betty — 2026-07-28T20:24:25.336Z
## QA test manifest (AST-1020)

**Publish:** `origin/sub/AST-1019/AST-1020-embedded-stylesheet-golden-parity` @ `24a466ce` (`merge-tests(AST-1020): origin/tests 4c04e20f`)

### Classification

1. **Existing coverage (bible-backed):** AST-1010 header/meta/CSS selectors; AST-998 / AST-1008 / AST-1009 experience/education/skills emit regressions.
2. **Broken / obsolete:** `TestAst1010HeaderContactMetaStyles` pre–Take-2 negative assert that contact flex was absent — removed; golden flex covered by new `TestAst1020GoldenStylesheet`.
3. **Gaps:** golden embedded stylesheet contract (three surfaces) + `BUILD_CONFIG` text/border color tokens.

**Integration:** no existing scenario asserts resume stylesheet — no revision.

### Manifest (test-child)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_builder.py::TestAst1020GoldenStylesheet \
  tests/component/utils/test_config.py::TestAst1020DefaultStyleColorTokens \
  tests/component/core/test_builder.py::TestAst1010HeaderContactMetaStyles \
  tests/component/core/test_builder.py::TestAst998ExperienceJobRender \
  tests/component/core/test_builder.py::TestAst1008ExperienceGoldenLayout \
  tests/component/core/test_builder.py::TestAst1009EducationSkillsPrior \
  -q
```

### Bible shasums (on publish tip)

- `docs/test-bible/core/builder.md` `4d7930c98d6aceb4713d34e442beb01b66115e30`
- `docs/test-bible/utils/config.md` `06c0584f688ae3e201f03cacebd93d19a38d8afe`

— Betty

#### joan — 2026-07-28T20:14:24.273Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1020
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
|-----------|---------------|
| 1. Embedded `<style>` carries golden rules for laundry items 3–12 | Stages 1–2 (tokens + wholesale CSS replace); Stage 3 spot-check |
| 2. Experience / education / skills match golden spacing/typography (items 7–9) | Stage 2 CSS contract; markup assumed from AST-1008/1009 (out of scope) |
| 3. Contact golden flex; header `Name • Title` with markers | Stage 2 `.contact` flex rules; header/contact emit left unchanged (preserve AST-993) |
| 4. No external stylesheet link; styles embedded | Stage 2 / contract: do not emit `<link rel="stylesheet">` |
| 5. Document `<title>` is `{candidate_name} Resume` | N/A — boundary: sibling AST-1021 (plan Out of scope) |
| 6. Candidate-specific meta description | N/A — boundary: sibling AST-1021 (plan Out of scope) |
| 7. Shared builders (session / base / job-tailored) same cosmetics | Stage 3 three-surface proof via shared `_emit_html_document` |
| 8. Eye verify vs desired HTML; no “close enough” | Stage 2 “verbatim golden” Decision + Stage 3 / UAT eye-check |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| 1 Config text/border tokens | Purpose + laundry item 3 (colors); Code Rules §2.1 / config tokens |
| 2 Replace resume embedded CSS | Functional scope laundry items 3–12; child owns stylesheet slice |
| 3 Three-surface stylesheet proof | Laundry item 14 / parent AC 7; shared builder family |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | Plan does not invent Betty merge/test SHA mechanics; engineer-only CSS/config |
| orch.git.commit-vocabulary | conforms | Plan doc already published under child `sub/` tip; no commit-vocab conflict |
| orch.git.flow-direction-inviolable | conforms | Publish ref is child `sub/AST-1019/…`; no reverse-flow instructions |
| orch.git.ftr-sub-topology | conforms | Files Changed stay on child publish ref under parent ftr topology |
| orch.git.merge-on-checkout | conforms | No alternate merge/rebase inventiveness in plan stages |
| orch.git.no-cherry-pick-rebase-force | conforms | Plan does not direct cherry-pick/rebase/force |
| orch.git.no-dev-agent-branches | conforms | Uses authoritative `sub/AST-1019/AST-1020-…` publish ref |
| orch.git.one-epic-worktree-per-parent | conforms | Scoped to epic worktree AST-1019 / this child only |
| orch.git.three-permanent-branches | conforms | No new permanent branch proposed |
| orch.pipeline.call-susan-for-product-decisions | conforms | Golden CSS is Archie/Susan fixture; Stage 1 Decision is implementation, not product fork |
| orch.pipeline.plan-is-bible | conforms | Stages are concrete Done-when + verbatim CSS contract vs parent fixture |
| orch.pipeline.project-scoped-queues | conforms | Single-child Artifacts ticket; no cross-project queue inventiveness |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validation path only; no status-skip instructions |
| orch.roles.archie-approves-statutes | conforms | Does not author/amend statutes |
| orch.roles.betty-owns-test-tree | conforms | Explicit engineer test-tree ban; Betty owns assertions after Code Complete |
| orch.roles.chuckles-never-ticket-assignee | conforms | N/A to plan content; no Chuckles-assignee inventiveness |
| orch.roles.engineer-assignee-through-resolve | conforms | Build stays engineer-owned; no role inversion |
| orch.roles.pre-commit-path-bans | conforms | Touches only allowed engineer paths (config + builder); no banned trees |
| astral.agent.confidence-bounds | conforms | No graded/consult confidence path touched |
| astral.agent.do-task-delegation | conforms | No `do_task` / agent assembly changes |
| astral.agent.grade-vector-validation | conforms | No grade/vector work |
| astral.batch.batch-id-first | conforms | No batch claim APIs |
| astral.batch.batch-id-format | conforms | No batch_id generation |
| astral.batch.claim-process-release | conforms | Not a batch entity processor |
| astral.batch.entity-agent-responses-latest-only | conforms | No agent_data / latest-refs changes |
| astral.config.config-source-of-truth | conforms | New color tokens land in `BUILD_CONFIG["default_style"]["colors"]` |
| astral.config.pass-threshold-vs-score-floor | conforms | No scoring/dispatch thresholds |
| astral.config.secrets-and-env-specific-from-environ | conforms | Plain style literals only; no secrets/env |
| astral.git.betty-no-src-or-features | conforms | Engineer plan edits `src/` + features plan; Betty banned from those trees |
| astral.layers.core-vs-external-bright-line | conforms | CSS emit stays core builder; no external I/O for stylesheet |
| astral.layers.import-direction | conforms | utils config + core builder only; no illegal imports proposed |
| astral.layers.ui-config-driven-business-logic | conforms | No UI/React changes; cosmetics stay builder/config |
| astral.patterns.coat-check-never-store-empty | conforms | No coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | conforms | No consult/render_verdict |
| astral.standards.data-raises-caller-logs | conforms | No data-layer logging/error path changes |
| astral.standards.debug-contract-gated | conforms | No debug-contract emission added |
| astral.standards.dry-and-focused-functions | conforms | Single CSS construction path in `_emit_html_document`; no second template |
| astral.standards.in-scope-only | conforms | Strict stylesheet slice; title/meta/markup/cover left to boundaries/sibling |
| astral.standards.logging-via-utils | conforms | No new logging |
| astral.standards.no-cross-contamination | conforms | Stays in layered `src/utils` + `src/core` |
| astral.standards.no-hardcoded-sets | conforms | Colors promoted to config; spacing px stay CSS literals per explicit Stage 1 Decision (existing emit pattern) |
| astral.standards.public-then-helpers | conforms | Edits existing helper CSS string; no public/helper reorder inventiveness |
| astral.standards.utils-data-late-import-only | conforms | No utils→data imports |
| astral.state.core-decides-transitions | conforms | No state transitions |
| astral.state.job-prior-states-enforced | conforms | No job state work |
| astral.state.no-daisy-chain-in-run | conforms | No dispatch daisy-chain |
| astral.ui.single-gunicorn-worker | conforms | Touches `config.py` colors only; no worker/RAILWAY changes |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths miss plan Files Changed
- astral.debug.spikes-under-debug-dir — paths miss plan Files Changed (spikes mentioned as optional gitignored only)
- astral.docs.features-single-file-per-ticket — layers/paths miss (plan file already published; Files Changed is src only)
- astral.git.engineer-test-tree-ban — paths miss plan Files Changed (ban still honored in prose)
- astral.layers.scripts-exempt-from-layer-rules — layers/paths miss
- astral.patterns.require-auth-on-protected-endpoints — ui layer/paths miss
- astral.standards.database-header-inventory — data layer/paths miss
- astral.ui.frontend-file-placement — ui layer/paths miss
- astral.ui.naming-conventions — ui layer/paths miss

## Findings

None (fix-now).

**acceptable:** Astral-only `.cover-block` / `.ats-keywords` / `.prose-block` rules are appended between golden skills and mobile — `<style>` will not be byte-identical to the parent fixture; Stage 3 correctly gates on golden selectors/declarations, matching child AC “carries the golden rules.”

**Self-assessment:** Scope Single-Component / Conf high / Risk Medium — honest for a shared-builder CSS wholesale replace.

— Joan
context_tokens≈48000

#### katherine — 2026-07-28T19:58:22.064Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-1019/AST-1020-embedded-stylesheet-golden-parity/docs/features/artifacts/ast-1020-embedded-stylesheet-golden-parity.md

**Scope:** Single-Component — `BUILD_CONFIG["default_style"]["colors"]` text/border tokens + the embedded CSS string in `builder._emit_html_document` only (no emit markup).

**Conf:** high — parent golden `<style>` is the fixture; fonts/accent already interpolate from config; AST-1008/1009 already emit the class names this CSS paints.

**Risk:** Medium — stylesheet is shared across session / base / job-tailored resume HTML; a miss regresses cosmetics and Prior Experience print break on all three surfaces.

Tip `a0b70b47` on `origin/sub/AST-1019/AST-1020-embedded-stylesheet-golden-parity`.

---

# Embedded stylesheet golden parity (Take 2: Resume Render Format discrepancies)

**Linear:** [AST-1020](https://linear.app/astralcareermatch/issue/AST-1020/embedded-stylesheet-golden-parity-take-2-resume-render-format)
**Parent:** [AST-1019](https://linear.app/astralcareermatch/issue/AST-1019/take-2-resume-render-format-discrepancies) — Take 2: Resume Render Format discrepancies
**Publish ref:** `origin/sub/AST-1019/AST-1020-embedded-stylesheet-golden-parity`

Align the shared resume embedded `<style>` block with the AST-1019 Take 2 golden CSS: contact flex, role/education/skills spacing and type, skills CSS grid, all-caps competencies/skills treatment, unused-but-present `.title` / `.specialties` / `.job-title` / `.dates` rules, mobile and print blocks, and config-driven font/color token updates where the builder already interpolates style. Does **not** own document title / meta emit (AST-1021), DOM structure beyond what CSS alone can fix, AST-993 structural contracts, or cover-letter HTML.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add golden text/border color tokens under `BUILD_CONFIG["default_style"]["colors"]` | utils |
| `src/core/builder.py` | Replace the resume-body CSS string inside `_emit_html_document` with the golden stylesheet (interpolating config tokens); keep Astral-only cover + ATS CSS appendages; always emit golden print `#prior-experience` rule | core |

**Out of scope (do not touch):** `<title>` / `<meta name="description">` emit (AST-1021); header `Name • Title` / contact string join / marker vocabulary; `_emit_experience_jobs_html` / education / skills / prior **markup**; cover-letter HTML structure; external `styles07.css`; `tests/`, bible (Betty).

## Golden CSS contract (stylesheet only)

Authoritative source: parent AST-1019 Original-brief desired HTML `<style>` block (laundry-list items **3–12**). After this ticket, the embedded `<style>` in HTML from `build_session_base_resume` / `build_base_resume` / `build_resume_from_job` must carry these rules (token values may be interpolated from `style` / `BUILD_CONFIG["default_style"]`, but selectors and declarations must match):

| Area | Required golden behavior |
|------|--------------------------|
| `:root` | `--max-width: 800px`; `--accent-color` / `--header-color` from style; `--text-primary` / `--text-secondary` / `--text-tertiary`; `--border-light` / `--border-medium`; three font stacks |
| Typography alignment | `h1,h2,h3,.title,.specialties` header font + center; `.contact,.competencies-list,.skill-category p` list font + center; `.skill-category h4` header font + center; `p,.role-description,ul,li` body font + left + `line-height: 1.25`; `p { margin-bottom: 12px }`; `.job-title` / `.dates` unused-but-present rules |
| All-caps | `.competencies-list` and `.skill-category p`: uppercase, `letter-spacing: 0.2px`, `font-size: 13.5px` |
| Contact | `.contact`: flex, wrap, `gap: 8px 16px`, `justify-content: center`; `.contact span { white-space: nowrap }` |
| Decorative `h2` | flex + `::before`/`::after` hairlines (already present — keep exact golden sizes/margins) |
| Experience | `.role` `margin-bottom: 12px` + `page-break-inside: avoid`; `.role-header` `margin-top: 20px; margin-bottom: 8px`; `.compact-title` / `.compact-location` (14.5px tertiary body font; `em` italic 14.5px); `.role ul` `padding-left: 20px`; bullet `margin-bottom: 6px` |
| Education | `.education-list` `margin-left: 0.5in`; tight `line-height: 1.1`; `strong` on header font |
| Skills | `.skills-grid` CSS grid `repeat(auto-fit, minmax(280px, 1fr))` + gap; category `h4` centered uppercase accent-colored |
| Mobile | Full `@media (max-width: 600px)` block from golden |
| Print | Full `@media print` from golden **including** `#prior-experience { page-break-before: always }` always (not gated on `emit_prior_experience`) |

Astral-only appendages that must **remain** after the golden resume rules (not in the desired HTML fixture, but required by existing builder surfaces):

- `.cover-block` / `.cover-signoff` rules (unchanged)
- `.ats-keywords` rules from `ats_keyword_block` config (unchanged)
- `.prose-block { white-space: pre-wrap; }` so the legacy string-`experience` emit path does not collapse newlines when golden general `p` rules drop `white-space: pre-wrap`

Do **not** emit `<link rel="stylesheet" …>`.

## Stage 1: Config — golden text/border color tokens

**Done when:** `BUILD_CONFIG["default_style"]["colors"]` exposes the golden text and border literals below; fonts / accent / header / page_background remain as today (`#3c2c6e`, `#f5f5f5`, Helvetica Neue / Palatino stacks). No other `BUILD_CONFIG` keys change.

1. In `src/utils/config.py`, inside `BUILD_CONFIG["default_style"]["colors"]`, **add** (do not rename existing `ink` / `muted` / `rule` / `surface` — leave them for other consumers):
   ```python
   "text_primary": "#1a1a1a",
   "text_secondary": "#444",
   "text_tertiary": "#666",
   "border_light": "#e0e0e0",
   "border_medium": "#ccc",
   ```
2. Confirm `default_accent`, `default_header`, `page_background`, and the three font stacks already match the golden `:root` values — if any drift exists vs `#3c2c6e` / `#f5f5f5` / Helvetica Neue / Palatino / list stack, correct those literals in the same edit so Stage 2 interpolation has no judgment call.
   ⚠️ **Decision:** Promote only the CSS custom-property colors that the golden `:root` defines and that Stage 2 interpolates. Do **not** move spacing/type-scale px values into config for this ticket — those stay as literal declarations in the CSS string copied from the golden block (same pattern as AST-1010 / current `_emit_html_document`).

## Stage 2: Replace resume embedded CSS with golden parity

**Done when:** The `css` f-string inside `_emit_html_document` produces a `<style>` body whose resume rules match the golden contract table above (selectors + declarations), interpolating `accent` / `header_c` / `page_bg` / font stacks / the five new color tokens from Stage 1; contact is flex-centered; skills use CSS grid; education has `0.5in` indent; mobile and print blocks are present; `#prior-experience { page-break-before: always }` is always in the print block; cover + ATS + `.prose-block` appendages remain; no external stylesheet link; title/meta/header/contact **emit** code paths are unchanged.

1. In `src/core/builder.py` `_emit_html_document`, after reading `fonts` / `colors` / `ak` as today, also read:
   ```python
   text_primary = colors.get("text_primary", "#1a1a1a")
   text_secondary = colors.get("text_secondary", "#444")
   text_tertiary = colors.get("text_tertiary", "#666")
   border_light = colors.get("border_light", "#e0e0e0")
   border_medium = colors.get("border_medium", "#ccc")
   ```
2. **Delete** the conditional `prior_rule` construction (`if emit_prior_experience: prior_rule = …`). Keep the `emit_prior_experience` parameter on the function signature (callers still pass it for body-section inclusion) — it must no longer affect CSS.
3. **Replace** the resume portion of the `css = f"""…"""` string (everything currently from `:root` through the skills / competencies rules, **before** cover/ATS) with the golden stylesheet translated to an f-string:
   - Interpolate `{accent}`, `{header_c}`, `{page_bg}`, `{hstack}`, `{bstack}`, `{lstack}`, `{text_primary}`, `{text_secondary}`, `{text_tertiary}`, `{border_light}`, `{border_medium}` into the matching `:root` / `body` declarations.
   - Copy every golden rule listed in the contract table **verbatim** (including unused `.title` / `.specialties` / `.job-title` / `.dates`).
   - Use `.role-description` (not `.prose-block`) in the body typography group, matching golden.
   - Do **not** put `white-space: pre-wrap` on the general `p, .role-description, ul, li` rule (golden does not).
4. **Immediately after** the golden skills rules and **before** the mobile block, append Astral-only:
   ```css
   .prose-block { white-space: pre-wrap; }
   .cover-block { … existing unchanged … }
   .cover-block p { white-space: pre-wrap; }
   .cover-signoff img { … }
   .cover-signoff p { … }
   .ats-keywords { … existing ak interpolations unchanged … }
   ```
5. Append the golden **Mobile** `@media (max-width: 600px)` block exactly.
6. Append the golden **Print** `@media print` block exactly, including `#prior-experience { page-break-before: always }` and `#competencies { page-break-after: avoid }` — no `{prior_rule}` splice.
7. Remove obsolete/divergent current declarations that conflict with golden (examples that must not survive): `.contact` without flex; `.compact-location` on list font / 13px / secondary; `.role ul { padding-left: 1.25em }`; `.skills-grid` without `display: grid`; `.skill-category h4` left-aligned primary color; `.education-list` without `margin-left: 0.5in`; duplicate `article.role` margin rule if golden only uses `.role`.
8. Do **not** change the HTML template below the CSS (`<!doctype…>`, `<title>`, meta, header `h1` / `.contact` span, body sections). Title/meta remain AST-1021.
9. Do **not** change `_emit_experience_jobs_html`, `_emit_education_list_html`, `_emit_skills_grid_html`, or section wrappers — markup already emits golden class names from AST-1008/1009; this stage only paints them.
   ⚠️ **Decision:** One wholesale CSS replacement against the parent golden `<style>` block, plus the three Astral appendages (cover / ATS / `.prose-block`), rather than piecemeal patches — avoids leaving half-updated AST-1010/1008 spacing values that fail UAT “no close enough.”

## Stage 3: Three-surface stylesheet proof (manual / build verification)

**Done when:** For fixture-shaped content matching the AST-1019 paste (or equivalent in-memory markers dict), each of `build_session_base_resume`, `build_base_resume`, and `build_resume_from_job` yields HTML whose embedded `<style>` contains the golden selectors/declarations from Stage 2 (spot-check at minimum: `.contact{` flex + gap; `.skills-grid` `minmax(280px`; `.education-list` `0.5in`; `.compact-location` `14.5px`; `@media (max-width: 600px)`; `#prior-experience { page-break-before: always }`); no `<link rel="stylesheet"`; header still `Name • Title` with markers; cover HTML path untouched when not requested. Spike dumps only under `debug/spikes/AST-1020/` if used — never commit; never repo-root `artifacts/`.

1. During **build-child**, exercise the three public builders (REPL or ad-hoc under `debug/spikes/AST-1020/`).
2. Confirm the `<style>` source carries the Stage 2 contract (string search is enough for “Done when”; eye-check in browser print/preview is UAT, not a build gate inventing Betty tests).
3. If a golden rule cannot be applied because emit markup lacks a class this ticket was told already exists (e.g. missing `.skills-grid`), **stop**, comment on **parent** AST-1019 with the Stage blocked template, and wait — do not invent DOM changes (that is AST-1021 or a re-scope).

## Self-Assessment

**Scope:** `Single-Component` — `BUILD_CONFIG["default_style"]["colors"]` tokens plus the embedded CSS string inside `src/core/builder.py` `_emit_html_document`; no emit markup or UI layer changes.

**Conf:** `high` — golden `<style>` is pasted in the parent Original brief; builder already interpolates fonts/accent into one CSS f-string; AST-1008/1009 already emit the class names this CSS paints.

**Risk:** `Medium` — wrong stylesheet would visually regress all three resume surfaces (session / base / job-tailored) that share `_emit_html_document`, including print pagination for Prior Experience.

## Code Rules self-review

- §1.3 DRY: one CSS construction path inside `_emit_html_document`; no second document template.
- §1.4 / §2.1: fonts and colors stay in `BUILD_CONFIG["default_style"]`; Stage 1 adds the missing text/border tokens; spacing literals stay in the CSS string copied from golden (explicit Decision).
- §2.5 / §3.2: stylesheet emit remains core (`builder.py`); no UI/React duplication of resume cosmetics.
- §3.3: no new imports; utils config only + core builder.
- §3.5 naming: unchanged.
- §3.6: spikes under `debug/spikes/AST-1020/` only if used; never commit; never repo-root `artifacts/`.
- Engineer test-tree ban: no `tests/` or bible edits — Betty owns assertions after Code Complete.
- Sibling scope: title/meta emit left to AST-1021; no cover-letter HTML rewrite.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1019/AST-1020-embedded-stylesheet-golden-parity`
**Plan path:** `docs/features/artifacts/ast-1020-embedded-stylesheet-golden-parity.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | 6104b15b | `BUILD_CONFIG` text/border color tokens |
| 2 | 89c3f44c | Golden embedded CSS in `_emit_html_document` + cover/ATS/prose-block |

**Tip:** `89c3f44c` on `origin/sub/AST-1019/AST-1020-embedded-stylesheet-golden-parity`

## Review (Radia — code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1020
**Publish ref:** `24a466ce420fa770b816603c01d4ce83f34d877a`
**Overall:** DISCUSS

### What’s solid

- Stage 1 tokens land in `BUILD_CONFIG["default_style"]["colors"]`; Stage 2 wholesale CSS replace matches the golden contract (contact flex, skills grid, education `0.5in`, mobile + always-on `#prior-experience` print break).
- Astral appendages (cover / ATS / `.prose-block`) retained; no `<link rel="stylesheet">`; title/meta/markup left for AST-1021.
- Engineer commits touch only `src/utils/config.py` + `src/core/builder.py` + plan; Betty owns one `merge-tests(AST-1020)` SHA.

### Issues / findings

**discuss (straggler):** Joan excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, and `astral.git.engineer-test-tree-ban` against plan Files Changed; three-dot diff vs `origin/dev` brings them in-scope (plan file + Betty test/bible trees). Diff conforms on each — no product fix.

### Recommended actions

- Engineer: acknowledge stragglers (no code change). Proceed resolve-child → User Testing when clear.

## Resolution

**Date:** 2026-07-28  
**Outcome:** clean — no product code changes.

Acknowledged Radia’s **discuss (straggler)** items (`astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`). Joan excluded them at plan time; three-dot diff brought them in-scope; each **conforms** in substance. No **fix-now** items. Publish tip after resolve remains product+Betty+Radia stack on `origin/sub/AST-1019/AST-1020-embedded-stylesheet-golden-parity`.
