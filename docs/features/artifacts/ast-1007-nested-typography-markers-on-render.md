<!-- linear-archive: AST-1007 archived 2026-08-05 -->

## Linear archive (AST-1007)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1007/nested-typography-markers-on-render-resume-render-format-discrepancies  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** Urgent / —  
**Parent:** AST-993 — Resume Render Format discrepancies  
**Blocked by / blocks / related:** parent: AST-993; blocks: AST-1010; blocks: AST-1009; blocks: AST-1008

### Description

## What this implements

Markers (`__` → non-breaking space, `~~` → non-breaking hyphen, bullet spacing) apply through nested strings on all shared resume HTML emits. Fixture-driven proof that markers are not left literal in experience bullets/accomplishments, skills lines, contact, competencies, or prior experience.

## Acceptance criteria

2. In that rendered HTML, legacy markers from the input are visible as non-breaking spaces and non-breaking hyphens in header/title, contact, competencies, experience text, prior experience, and skills — not left as literal `__` / `~~`.

## Boundaries

Does **not** own role/education/skills layout chrome (siblings). Does **not** re-implement AST-994 experience job-array parse.

## Notes for planning

Consumes AST-994 job-array content; markers must recurse into nested job/accomplishments strings. Shared builder surfaces: session, base, job-tailored.

## Git branch (authoritative)

Parent `ftr/ast-993-resume-render-format-discrepancies`; child `sub/AST-993/AST-1007-nested-typography-markers-on-render`. Publish to `origin/sub/AST-993/AST-1007-nested-typography-markers-on-render` only.

### Comments

#### radia — 2026-07-28T16:30:34.950Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1007
**Publish ref:** `94671581` on `origin/sub/AST-993/AST-1007-nested-typography-markers-on-render`
**Overall:** DISCUSS

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | conforms | No graded confidence / consult math in builder markers change |
| astral.agent.do-task-delegation | scoped | conforms | No AI / do_task delegation touched |
| astral.agent.grade-vector-validation | scoped | conforms | No grade vectors |
| astral.batch.batch-id-first | scoped | conforms | No batch claim APIs |
| astral.batch.batch-id-format | scoped | conforms | No batch_id generation |
| astral.batch.claim-process-release | scoped | conforms | No claim/process/release |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | No agent_data latest-ref work |
| astral.config.config-source-of-truth | scoped | conforms | Reuses grandfathered `_resume_site_markers`; no new config constants |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | No scoring thresholds |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No secrets/env values |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss repo-root `artifacts/**` / `scripts/spikes/**` |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Plan doc under `docs/features/**` only; no spike notes committed |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Single plan file `docs/features/artifacts/ast-1007-….md` |
| astral.git.betty-no-src-or-features | scoped | conforms | Engineer owns `src/` + features; Betty stayed on tests/bible |
| astral.git.engineer-test-tree-ban | scoped | conforms | Test tree via Betty `test(AST-1007)` + one engineer `merge-tests` |
| astral.layers.core-vs-external-bright-line | scoped | conforms | Pure core string transform; no external I/O |
| astral.layers.import-direction | scoped | conforms | No new cross-layer imports; `Any` already imported |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers/paths miss `scripts/**` |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | layers/paths miss `src/ui/**` / `config.py` |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | No coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | No consult / render_verdict |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | layers/paths miss `src/ui/**` |
| astral.standards.data-raises-caller-logs | scoped | conforms | No data-layer error handling |
| astral.standards.database-header-inventory | scoped | not-applicable | layers/paths miss `src/data/**` |
| astral.standards.debug-contract-gated | scoped | conforms | Diff does not add/change debug-contract emission |
| astral.standards.dry-and-focused-functions | scoped | conforms | One recursive helper; reuses `_resume_site_markers`; emit-time calls kept |
| astral.standards.in-scope-only | scoped | conforms | Only markers deep-walk; no sibling layout/parse/config |
| astral.standards.logging-via-utils | scoped | conforms | No logging changes |
| astral.standards.no-cross-contamination | scoped | conforms | Product diff stays in `src/core/builder.py` markers helpers |
| astral.standards.no-hardcoded-sets | scoped | conforms | No new state/enum sets; marker pairs unchanged |
| astral.standards.public-then-helpers | scoped | conforms | `_mark_resume_value` beside `_apply_resume_text_markers` in helpers |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | layers/paths miss `src/utils/**` |
| astral.state.core-decides-transitions | scoped | conforms | No state transitions |
| astral.state.job-prior-states-enforced | scoped | conforms | No job state work |
| astral.state.no-daisy-chain-in-run | scoped | conforms | No dispatch run chaining |
| astral.ui.frontend-file-placement | scoped | not-applicable | layers/paths miss `src/ui/frontend/**` |
| astral.ui.naming-conventions | scoped | not-applicable | layers/paths miss `src/ui/**` |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | layers/paths miss ui/scripts/config |
| orch.git.betty-merge-tests-one-sha | universal | conforms | One `merge-tests(AST-1007): origin/tests 634e5fdf…` |
| orch.git.commit-vocabulary | universal | conforms | plan/code/docs/test/merge-tests subjects only |
| orch.git.flow-direction-inviolable | universal | conforms | Published to child `sub/AST-993/AST-1007-…` only |
| orch.git.ftr-sub-topology | universal | conforms | Child sub under parent ftr topology |
| orch.git.merge-on-checkout | universal | conforms | `origin/ftr/…` is ancestor of review tip |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No cherry-pick/rebase/force in child history |
| orch.git.no-dev-agent-branches | universal | conforms | Authoritative sub publish-ref, not Linear agent branch |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Review in `astral-AST-993/` epic worktree |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | No improvisation beyond plan marker contract |
| orch.pipeline.plan-is-bible | universal | conforms | Stage 1 deep-walk implemented as planned |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Artifacts child only |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Entered from Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty owns tests/bible; engineer merge-tests only |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee remains Ada |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada stays assignee through Review Posted |
| orch.roles.pre-commit-path-bans | universal | conforms | Engineer `code()` touched builder only; tests via merge-tests |

## Pattern conformance

none cited

## Plan adherence

Diff matches Stage 1 (deep `_apply_resume_text_markers` / `_mark_resume_value`, unchanged `_resume_site_markers`, emit-time experience markers retained, no layout chrome). Stage 2 proof landed as Betty component tests on all three surfaces. Self-Assessment **Single-Component** matches; sibling AST-1008/1009/1010 boundaries not smuggled. Call sites vs `origin/dev` unchanged (four pre-existing).

## Findings

**discuss (C4 straggler):** `astral.debug.spikes-under-debug-dir` — Joan excluded at plan time; in-scope on diff via `docs/features/**`. Substance conforms (plan only; no spike dumps).

**discuss (C4 straggler):** `astral.docs.features-single-file-per-ticket` — Joan excluded; in-scope on diff. Substance conforms (one features file).

**discuss (C4 straggler):** `astral.git.engineer-test-tree-ban` — Joan excluded; in-scope on diff via tests/bible. Substance conforms (Betty `test` + one `merge-tests`).

No **fix-now** findings.

## What’s solid

Localized recursion deepen; idempotent overlap with AST-998 emit markers; fixture-shaped Betty proof for nested `__`/`~~`.

## Notes

Joan plan-rubric verdict attached (APPROVED). Three-dot file set vs `origin/dev`: plan + bible + `builder.py` + `test_builder.py` only.

**Recommended:** `resolve-child` — acknowledge C4 stragglers; no product code change required for them.

context_tokens≈45000

#### betty — 2026-07-28T16:26:23.604Z
1. `tests/component/core/test_builder.py::TestAst1007NestedTypographyMarkers` — deep-walk helper + session/base/job HTML (no literal `__`/`~~`; NBSP/`\u2011` present)
2. `tests/component/core/test_builder.py::TestBuilderHelpers::test_applies_profile_contact_and_markers` — existing top-level markers regression
3. `tests/component/core/test_builder.py::TestAst998ExperienceJobRender` — experience job-array emit still green

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_builder.py::TestAst1007NestedTypographyMarkers \
  tests/component/core/test_builder.py::TestBuilderHelpers::test_applies_profile_contact_and_markers \
  tests/component/core/test_builder.py::TestAst998ExperienceJobRender \
  -q
```

**Broken / obsolete:** none
**Integration:** no existing scenario asserts resume typography markers — no revision

`origin/sub/AST-993/AST-1007-nested-typography-markers-on-render` @ `178f54ff` (`merge-tests(AST-1007): origin/tests 634e5fdf…`)

**Bible shasum:** `docs/test-bible/core/builder.md` → `22ff92bf53c4b6efb096cafaba18eedea4d86271c174bf1dee1fc61392b311fc`

#### joan — 2026-07-28T16:19:38.801Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1007
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 body structure (header/roles/education/skills) | N/A — boundary (AST-1008 / AST-1009 / AST-1010 own layout chrome) |
| AC2 nested markers (`__`/`~~`/bullet spacing) not left literal | Stage 1 (deep-walk) + Stage 2 (three-surface proof) |
| AC3 Somerset lead vs bullets | N/A — boundary (AST-1008) |
| AC4 education/skills markup | N/A — boundary (AST-1009) |
| AC5 meta description / tagline not body | N/A — boundary (AST-1010) |
| AC6 session/base/job surface parity | Stage 2 typography parity across three builders; structure N/A siblings |
| AC7 embedded stylesheet | N/A — boundary (AST-1010) |
| AC8 eye verify vs desired HTML | Stage 2 marker visibility proof (structure/chrome remain sibling UAT) |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 deep-walk `_apply_resume_text_markers` | Parent Purpose / Functional scope “Legacy typography markers end-to-end”; child AC2; Boundaries (no layout/parse) |
| Stage 2 fixture-driven proof on three surfaces | Child AC2 fixture proof; Functional scope “All shared builder surfaces”; AC6 typography portion |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | Plan leaves tests to Betty; no merge-tests SHA work here |
| orch.git.commit-vocabulary | conforms | Plan does not prescribe forbidden commit subjects |
| orch.git.flow-direction-inviolable | conforms | Publish ref is child `sub/AST-993/AST-1007-…` only |
| orch.git.ftr-sub-topology | conforms | Child sub under parent ftr topology preserved |
| orch.git.merge-on-checkout | conforms | No plan step that skips merge-on-checkout duties |
| orch.git.no-cherry-pick-rebase-force | conforms | No cherry-pick/rebase/force in plan |
| orch.git.no-dev-agent-branches | conforms | Uses authoritative sub publish ref, not Linear agent branch |
| orch.git.one-epic-worktree-per-parent | conforms | Single epic worktree assumed; no extra worktree |
| orch.git.three-permanent-branches | conforms | Does not invent permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Stage 2 stop+parent comment on broken assumptions |
| orch.pipeline.plan-is-bible | conforms | Stages/steps are executable and binding; no improvise path |
| orch.pipeline.project-scoped-queues | conforms | No cross-project queue work |
| orch.pipeline.status-gates-skill-entry | conforms | Plan stays within plan→build gate expectations |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | Explicitly bans engineer `tests/`/bible edits |
| orch.roles.chuckles-never-ticket-assignee | conforms | No assignee-policy contradiction in plan |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer build path after Plan Approved |
| orch.roles.pre-commit-path-bans | conforms | Files Changed stay in engineer-allowed product path |
| astral.agent.confidence-bounds | conforms | No graded confidence / consult math touched |
| astral.agent.do-task-delegation | conforms | No AI/do_task work |
| astral.agent.grade-vector-validation | conforms | No grade vectors |
| astral.batch.batch-id-first | conforms | No batch claim APIs |
| astral.batch.batch-id-format | conforms | No batch_id generation |
| astral.batch.claim-process-release | conforms | No claim/process/release |
| astral.batch.entity-agent-responses-latest-only | conforms | No agent_data latest-ref work |
| astral.config.config-source-of-truth | conforms | No new behavior constants; reuses grandfathered `_resume_site_markers` (AST-998) |
| astral.config.pass-threshold-vs-score-floor | conforms | No scoring thresholds |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env values |
| astral.git.betty-no-src-or-features | conforms | Engineer owns `src/core/builder.py`; Betty not editing src/features |
| astral.layers.core-vs-external-bright-line | conforms | Pure core transform; no I/O in external |
| astral.layers.import-direction | conforms | Core-only Files Changed; no new cross-layer imports |
| astral.patterns.coat-check-never-store-empty | conforms | No coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | conforms | No consult/render_verdict |
| astral.standards.data-raises-caller-logs | conforms | No data-layer error handling changes |
| astral.standards.debug-contract-gated | conforms | No new debug-contract lines planned |
| astral.standards.dry-and-focused-functions | conforms | One recursive helper; reuses `_resume_site_markers`; keep emit-time calls |
| astral.standards.in-scope-only | conforms | Explicit sibling/layout/parse/config out-of-scope list |
| astral.standards.logging-via-utils | conforms | No logging changes |
| astral.standards.no-cross-contamination | conforms | Stays inside `src/core` |
| astral.standards.no-hardcoded-sets | conforms | No new state/enum sets; marker pairs unchanged |
| astral.standards.public-then-helpers | conforms | Private `_mark_resume_value` beside existing helper section |
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

**acceptable:** Stage 1 “Done when” says “AST-996 experience job array”; intro correctly cites AST-994/998. Treat as AST-994 job-array nests — typo only, not a scope change.

No `fix-now` or `discuss` findings. Self-assessment (Single-Component / high / Medium) is honest for a localized recursive deepen of an existing markers pass.

— Joan

context_tokens≈62000

#### ada — 2026-07-28T16:16:28.850Z
Plan: [`docs/features/artifacts/ast-1007-nested-typography-markers-on-render.md`](https://github.com/susansomerset/astral/blob/sub/AST-993/AST-1007-nested-typography-markers-on-render/docs/features/artifacts/ast-1007-nested-typography-markers-on-render.md) on `origin/sub/AST-993/AST-1007-nested-typography-markers-on-render` @ `920b0378`.

**Self-assessment**
- **Scope:** Single-Component — deep-walk of `_apply_resume_text_markers` in `src/core/builder.py` only; no layout chrome, parse, or config marker moves.
- **Conf:** high — markers helper + three-surface call sites already exist (AST-998 emit-time experience markers); gap is shallow vs recursive string leaves.
- **Risk:** Medium — bad recursion could leave `__`/`~~` literal or mishandle list/dict nests across session/base/job HTML typography.

---

# Nested typography markers on render (Resume Render Format discrepancies)

**Linear:** [AST-1007](https://linear.app/astralcareermatch/issue/AST-1007/nested-typography-markers-on-render-resume-render-format-discrepancies)
**Parent:** [AST-993](https://linear.app/astralcareermatch/issue/AST-993/resume-render-format-discrepancies) — Resume Render Format discrepancies
**Publish ref:** `origin/sub/AST-993/AST-1007-nested-typography-markers-on-render`

Shared resume HTML builders already run `_apply_resume_text_markers` before emit, but that helper only transforms **top-level** string values. Nested string leaves — especially AST-994/998 experience job-array fields (`company`, `title`, `dates`, `location`, `accomplishments`) and any list/dict nests under other render keys — stay unmarked in the markers dict. Parent AC2 requires `__` → NBSP (`\u00a0`), `~~` → non-breaking hyphen (`\u2011`), and `" • "` → `\u00a0• ` through those nested strings on session, base, and job-tailored HTML, with fixture-driven proof that literal `__` / `~~` are gone from the rendered body sections this ticket owns. This plan deepens the existing markers pass only — it does **not** own role/education/skills layout chrome (AST-1008 / AST-1009 / AST-1010) or re-parse experience job arrays (AST-994).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/builder.py` | Deep-walk `_apply_resume_text_markers` over dict/list nests; apply `_resume_site_markers` to every string leaf; keep emit-time experience markers (idempotent); no layout/CSS/emit-structure changes | core |

**Out of scope (do not touch):** `_emit_experience_jobs_html` role chrome / lead-vs-bullets (AST-1008); education line / skills category grid / prior-list markup (AST-1009); header `Name • Title` composition, meta description, embedded stylesheet expansion (AST-1010); cover-letter body marker policy; `candidate.py` parse / job-array contract; `config.py` marker literals (leave `_resume_site_markers` transforms as-is); `tests/`, bible (Betty).

## Marker contract (existing — do not redefine)

`_resume_site_markers(text)` in `src/core/builder.py` already implements:

1. `__` → `\u00a0` (NBSP)
2. `~~` → `\u2011` (non-breaking hyphen)
3. `" • "` → `"\u00a0• "` (legacy bullet spacing)

Do **not** change these three substitutions, add new marker pairs, or move them into `BUILD_CONFIG` in this ticket.

## Stage 1: Deep-walk `_apply_resume_text_markers`

**Done when:** Calling `_apply_resume_text_markers` on a render dict that contains (a) top-level strings with `__` / `~~` / `" • "` and (b) an AST-996 experience job array whose nested string fields also contain those markers returns a new structure where **every** string leaf has been passed through `_resume_site_markers`, with no literal `__` or `~~` remaining in those leaves; non-string leaves and empty strings behave as today; `build_session_base_resume`, `build_base_resume`, and `build_resume_from_job` still call this helper once before `_emit_html_document` (no new call sites).

1. In `src/core/builder.py`, replace the body of `_apply_resume_text_markers(render: dict) -> dict` so it returns a **new** top-level dict (same keys as `render`) whose values are produced by a private recursive helper (name it `_mark_resume_value` or similar, defined immediately below `_apply_resume_text_markers` in the helpers section):
   - **`str`:** return `_resume_site_markers(v)`.
   - **`dict`:** return `{k: recurse(v) for k, v in obj.items()}` (new dict; do not mutate the input).
   - **`list` / `tuple`:** return a new `list` of `recurse(item)` for each item (preserve list type in the output even if input was a tuple).
   - **Anything else** (`None`, `bool`, `int`, unexpected objects): return unchanged.
2. Update the docstring of `_apply_resume_text_markers` from “shallow copy” to state that it deep-walks dict/list nests and applies `_resume_site_markers` to every string leaf.
3. Do **not** change `_resume_site_markers` itself.
4. Do **not** remove or alter the existing `_resume_site_markers(...)` calls inside `_emit_experience_jobs_html` (AST-998). Double application is idempotent for the three substitutions above; leave them as defense-in-depth for direct helper calls.
   ⚠️ **Decision:** Single authoritative transform for the shared render dict is the deep `_apply_resume_text_markers` pass used by all three resume HTML surfaces; emit-time markers on experience fields stay. Do not invent a second marker vocabulary or a config block for marker pairs.
5. Do **not** change `_emit_body_sections_html`, `_emit_html_document` CSS, header/contact join chrome, education/skills markup, or cover-letter emit.
6. Do **not** edit `tests/` or bible — Betty owns fixture assertions after Code Complete.

## Stage 2: Fixture-driven proof on all three surfaces (manual / build verification)

**Done when:** With a minimal in-memory render (or session paste content) that plants `__` / `~~` / `" • "` in `candidate_name` or `candidate_title`, `candidate_contact_detail` (or profile-derived contact), `core_competencies`, at least one experience job’s `company`/`title`/`accomplishments`, `prior_experience`, and `technical_skills`, each of `build_session_base_resume`, `build_base_resume`, and `build_resume_from_job` produces HTML whose corresponding visible text contains `\u00a0` / `\u2011` (or the escaped/HTML-equivalent forms after `html.escape`) and does **not** contain the literal two-character sequences `__` or `~~` in those sections’ body text. Layout classes (`.role`, skills grid, education lines, meta description) are **not** asserted here — siblings own those.

1. During **build-child**, verify Stage 1 by exercising the three public builders with marker-laden nested content (REPL, ad-hoc script under `debug/spikes/AST-1007/`, or temporary local calls — **do not** commit spike output; **do not** add files under repo-root `artifacts/`). Prefer content shaped like the parent AST-993 paste fixture’s marker substrings (e.g. `Fractional__TPM`, `AI~~Assisted__Delivery`, `Somerset__Consulting`, `sprint~~level`, `Jira__•__Confluence`) rather than inventing a new marker dialect.
2. Confirm HTML source for those sections has no leftover literal `__` / `~~` in the escaped text nodes for header/title, contact, competencies, experience job strings, prior experience, and skills (string section path as today).
3. If deep-walk changes break an assumption documented in this plan (e.g. a non-string leaf that must not be copied), **stop**, comment on the **parent** AST-993 with the Stage blocked template, and wait — do not improvise.

## Self-Assessment

**Scope:** `Single-Component` — one core helper in `src/core/builder.py` (deep-walk of the existing markers pass); no UI, config, or parse-layer files.

**Conf:** `high` — `_resume_site_markers` and the three-surface call sites already exist; AST-998 already applies markers at experience emit; the gap is shallow vs deep walk, which is a localized recursion change with idempotent overlap.

**Risk:** `Medium` — wrong recursion (mutating inputs, walking non-render blobs, skipping list leaves) could leave markers literal or double-transform unexpected values; impact is typography in resume HTML across session/base/job surfaces, not dispatch or DB state.

## Code rules check

- §1.3 DRY: one deep markers pass for the render dict; reuse existing `_resume_site_markers`; leave emit-time experience calls (idempotent) rather than forking a second transform.
- §1.1 / scope isolation: only `builder.py` markers helper; no sibling layout chrome.
- §2.1: no new config keys; marker literals stay in the existing helper (grandfathered with AST-998).
- §2.4 / §2.6: N/A (no batch/state-machine work).
- §3.3: core-only change; no new imports across layers.
- §3.5 naming: private helper `_mark_resume_value` (or equivalent) beside `_apply_resume_text_markers`.
- §3.6: spike/debug under `debug/spikes/AST-1007/` only if used; never commit spike dumps.

## Review (build stub)

**Publish ref:** `origin/sub/AST-993/AST-1007-nested-typography-markers-on-render`
**Plan path:** `docs/features/artifacts/ast-1007-nested-typography-markers-on-render.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `74e6a669` | Deep-walk `_apply_resume_text_markers` via `_mark_resume_value` |
| 2 | (verify) | Three-surface fixture proof — no leftover `__` / `~~` in HTML |

**Tip:** `74e6a669` on `origin/sub/AST-993/AST-1007-nested-typography-markers-on-render`

## Radia review (code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1007
**Publish ref tip (pre-docs):** `178f54ff` — `origin/sub/AST-993/AST-1007-nested-typography-markers-on-render`
**Overall:** DISCUSS

### What’s solid

- Stage 1 matches plan: `_apply_resume_text_markers` deep-walks via `_mark_resume_value` (str / dict / list|tuple→list / else unchanged); `_resume_site_markers` untouched; emit-time experience markers retained; no layout/CSS/sibling chrome.
- Three-surface call sites unchanged vs `origin/dev`; Betty `TestAst1007NestedTypographyMarkers` covers deep-walk + session/base/job HTML proof.
- Self-Assessment Single-Component footprint holds; sibling AST-1008/1009/1010 boundaries respected.

### Issues

**discuss (C4 straggler):** `astral.debug.spikes-under-debug-dir` — excluded at plan time; in-scope on diff via `docs/features/**`. Substance **conforms** (plan doc only; no spike notes under features).

**discuss (C4 straggler):** `astral.docs.features-single-file-per-ticket` — excluded at plan time; in-scope on diff. Substance **conforms** (single `docs/features/artifacts/ast-1007-….md`).

**discuss (C4 straggler):** `astral.git.engineer-test-tree-ban` — excluded at plan time; in-scope on diff via Betty bible/tests. Substance **conforms** (`test(AST-1007)` + one `merge-tests(AST-1007)`).

No **fix-now** product findings.

### Recommended actions

Engineer (`resolve-child`): acknowledge C4 stragglers (pipeline docs/tests appearing after Joan’s plan-time exclude) — no product code change required for those three.

## Resolution

**Date:** 2026-07-28  
**Radia tip:** `94671581` · Overall DISCUSS · no fix-now

| Finding | Action |
|---------|--------|
| discuss C4 `astral.debug.spikes-under-debug-dir` | Acknowledged — substance conforms; no product change |
| discuss C4 `astral.docs.features-single-file-per-ticket` | Acknowledged — substance conforms; no product change |
| discuss C4 `astral.git.engineer-test-tree-ban` | Acknowledged — substance conforms; no product change |

No product or test-tree edits in resolve. Proceeding to User Testing after §9a dry-run.
