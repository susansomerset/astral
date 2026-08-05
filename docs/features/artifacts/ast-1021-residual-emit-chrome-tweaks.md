<!-- linear-archive: AST-1021 archived 2026-08-05 -->

## Linear archive (AST-1021)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1021/residual-emit-chrome-tweaks-take-2-resume-render-format-discrepancies  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1019 — Take 2: Resume Render Format discrepancies  
**Blocked by / blocks / related:** parent: AST-1019

### Description

## What this implements

Cosmetic emit adjustments the stylesheet cannot fix: document `<title>` → `{name} Resume` (no dashes); keep field-derived candidate-specific meta (do not force the golden HTML’s example meta string); plus any `white-space` / class alignment leftovers vs golden body. Does not rework AST-993 structural contracts. After stylesheet sibling; skip or thin if UAT shows CSS-only is enough.

## Acceptance criteria

 7. Document `<title>` is `{candidate_name} Resume` (space, no em/en dashes) — not `SomersetResume` and not `{name} — Resume`.
 8. ATS `<meta name="description">` is **candidate-specific** from paste name/title/tagline using the AST-993 field-derived template (`Resume of <name>, <title>, specializing in <tagline>`); the literal meta string in the desired HTML is an example of structure only, not a fixed string to force.
 9. Candidate base-resume HTML and job-tailored resume HTML that share the builder family show the same cosmetic treatment for equivalent structured content.
10. Susan can verify by eye against the desired HTML in this ticket for the listed style/format/alignment gaps; no judgment call on “close enough” for those items.

## Boundaries

Does not own embedded stylesheet golden parity (sibling Katherine). Does not rewrite resume content. Does not force literal golden meta example string.

## Notes for planning

Blocked by stylesheet child. Title shape: `{name} Resume` (Susan). Meta: candidate-specific field-derived.

## Git branch (authoritative)

Per orientation § Branch law. Created at dispatch-parent. Publish to origin/<publish-ref> only.

### Comments

#### radia — 2026-07-29T02:23:43.814Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1021
**Publish ref:** 73ab77f9a6bc1427f22d4f19c8cedfde4f5e06af
**Overall:** DISCUSS

Diff: `origin/dev...origin/sub/AST-1019/AST-1021-residual-emit-chrome-tweaks` (AST-1021 product @ `712bd324` / merge-tests tip `517faa96` + this `docs()` append). Includes prior AST-1020 stack on the sub.

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| orch.git.betty-merge-tests-one-sha | universal | conforms | One `merge-tests(AST-1021): origin/tests bcb2d83a` |
| orch.git.commit-vocabulary | universal | conforms | `code`/`docs`/`test`/`merge-tests`/`resolve` vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | Forward publish to child `origin/sub/…` only |
| orch.git.ftr-sub-topology | universal | conforms | Child sub under AST-1019; blockedBy AST-1020 honored |
| orch.git.merge-on-checkout | universal | conforms | No alternate merge inventiveness |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No cherry-pick/rebase/force |
| orch.git.no-dev-agent-branches | universal | conforms | Authoritative sub publish-ref |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Review in astral-AST-1019 |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branch |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Title/meta shapes from parent AC; residual table closed |
| orch.pipeline.plan-is-bible | universal | conforms | Stage 1 title fix + Stage 2–3 lock/no-op match plan |
| orch.pipeline.project-scoped-queues | universal | conforms | Single Artifacts child |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Reviewed from Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty `test` + `merge-tests`; Ada avoided test tree |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee remains Ada |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Implementer stays assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | Engineer product commit is `builder.py` only |
| astral.agent.confidence-bounds | scoped | conforms | No confidence/consult path |
| astral.agent.do-task-delegation | scoped | conforms | No `do_task` changes |
| astral.agent.grade-vector-validation | scoped | conforms | No grade/vector work |
| astral.batch.batch-id-first | scoped | conforms | No batch claim APIs |
| astral.batch.batch-id-format | scoped | conforms | No batch_id |
| astral.batch.claim-process-release | scoped | conforms | Not a batch processor |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | No agent_data latest-refs |
| astral.config.config-source-of-truth | scoped | conforms | No new config in AST-1021; prior tokens remain config-owned |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | No scoring thresholds |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No secrets/env |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss — no repo-root `artifacts/**` / `scripts/spikes/**` |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Plan under `docs/features/`; no spike pollution |
| astral.docs.features-single-file-per-ticket | scoped | conforms | One plan file per ticket (`ast-1021-….md`) |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty commits only tests/bible (+ merge-tests) |
| astral.git.engineer-test-tree-ban | scoped | conforms | Ada code/docs omit tests/bible |
| astral.layers.core-vs-external-bright-line | scoped | conforms | Title emit stays core builder |
| astral.layers.import-direction | scoped | conforms | No new imports |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers/paths miss — no `scripts/**` |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | No UI business logic; config touch is prior AST-1020 tokens |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | No coat-check |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | No consult |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | layers/paths miss — no `src/ui/**` |
| astral.standards.data-raises-caller-logs | scoped | conforms | No data-layer error/log path |
| astral.standards.database-header-inventory | scoped | not-applicable | layers/paths miss — no `src/data/**` |
| astral.standards.debug-contract-gated | scoped | conforms | No debug-contract emission |
| astral.standards.dry-and-focused-functions | scoped | conforms | Single shared `_emit_html_document` title path |
| astral.standards.in-scope-only | scoped | conforms | Title + meta lock only; stylesheet stays AST-1020 |
| astral.standards.logging-via-utils | scoped | conforms | No new logging |
| astral.standards.no-cross-contamination | scoped | conforms | Stays in core emit helper |
| astral.standards.no-hardcoded-sets | scoped | conforms | Title is AC-required literal (plan Decision) |
| astral.standards.public-then-helpers | scoped | conforms | One-line edit in existing helper |
| astral.standards.utils-data-late-import-only | scoped | conforms | No utils→data imports |
| astral.state.core-decides-transitions | scoped | conforms | No state transitions |
| astral.state.job-prior-states-enforced | scoped | conforms | No job state work |
| astral.state.no-daisy-chain-in-run | scoped | conforms | No dispatch daisy-chain |
| astral.ui.frontend-file-placement | scoped | not-applicable | layers/paths miss — no `src/ui/frontend/**` |
| astral.ui.naming-conventions | scoped | not-applicable | layers/paths miss — no `src/ui/**` |
| astral.ui.single-gunicorn-worker | scoped | conforms | No worker/RAILWAY knobs |

## Pattern conformance

none cited

## Plan adherence

Stage 1 matches the planned `name_raw` title construction. Stage 2 meta template unchanged (lock). Stage 3 residual inventory produced no further edits. Scope `minor` matches the one-line product footprint. Sibling AST-1020 CSS/tokens remain out of this ticket’s engineer commits.

## Findings

**discuss (straggler):** Joan excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, `astral.layers.ui-config-driven-business-logic`, `astral.standards.utils-data-late-import-only`, and `astral.ui.single-gunicorn-worker` against plan Files Changed; three-dot diff vs `origin/dev` brings them in-scope (plan/docs/test/config history incl. AST-1020). Each scores **conforms** — no product fix.

### What’s solid

`<title>{name} Resume</title>` / empty → `Resume`; meta stays field-derived `Resume of {name}, {title}, specializing in {tagline}`; no stylesheet/markup scope creep.

### Recommended actions

Acknowledge stragglers (no code change). resolve-child → User Testing when clear.

— Radia
context_tokens≈48000

#### betty — 2026-07-29T02:20:46.773Z
## QA test manifest (AST-1021)

**Publish:** `origin/sub/AST-1019/AST-1021-residual-emit-chrome-tweaks` @ `517faa96` (`merge-tests(AST-1021): origin/tests bcb2d83a`)

### Classification

1. **Existing coverage (bible-backed):** AST-1010 header/meta present-omit; AST-1020 stylesheet regression.
2. **Broken / obsolete:** none — no prior asserts locked `{name} — Resume`.
3. **Gaps:** document `<title>` `{name} Resume` (three surfaces + empty → `Resume`) + meta lock against golden example literal.

**Integration:** no existing scenario asserts resume title/meta chrome — no revision.

### Manifest (test-child)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_builder.py::TestAst1021DocumentTitleChrome \
  tests/component/core/test_builder.py::TestAst1010HeaderContactMetaStyles \
  tests/component/core/test_builder.py::TestAst1020GoldenStylesheet \
  -q
```

### Bible shasums (on publish tip)

- `docs/test-bible/core/builder.md` `48c1cac21b45afc67b6050066ab1cceb645fa282`

— Betty

#### joan — 2026-07-29T02:15:28.790Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1021
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
|-----------|---------------|
| 1. Embedded `<style>` golden rules (laundry 3–12) | N/A — boundary: sibling AST-1020 (plan Out of scope) |
| 2. Experience / education / skills spacing/typography | N/A — boundary: AST-993 stack / AST-1020 CSS; residual inventory excludes body markup |
| 3. Contact golden flex; header `Name • Title` with markers | N/A — preserve; Stage 3 table: contact single-span no change; header emit untouched |
| 4. No external stylesheet; styles embedded | N/A — boundary: AST-1020 |
| 5. Document `<title>` is `{candidate_name} Resume` | Stage 1 (fix em-dash construction + empty-name fallback) |
| 6. Candidate-specific meta (field-derived; not golden example literal) | Stage 2 lock / no-force on existing AST-1010 template |
| 7. Shared builders same cosmetics for equivalent content | Stage 4 three-surface chrome verification |
| 8. Eye verify; no “close enough” | Stage 4 string-checks + UAT; title/meta exact shapes |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| 1 Document `<title>` → `{name} Resume` | Purpose / laundry item 1; parent AC 5; child AC 7 |
| 2 Meta lock field-derived template | Laundry item 2; parent AC 6; child AC 8 |
| 3 Residual white-space / class emit leftovers | Child brief “CSS cannot fix” residual; closed inventory at plan time |
| 4 Three-surface chrome verification | Laundry item 14 / parent AC 7–8; child AC 9–10 |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge/test SHA inventiveness; engineer chrome-only |
| orch.git.commit-vocabulary | conforms | Plan on child `sub/` publish ref; no vocab conflict |
| orch.git.flow-direction-inviolable | conforms | Publish ref `sub/AST-1019/AST-1021-…`; no reverse flow |
| orch.git.ftr-sub-topology | conforms | Child sub under parent ftr; blockedBy AST-1020 noted |
| orch.git.merge-on-checkout | conforms | No alternate merge inventiveness in stages |
| orch.git.no-cherry-pick-rebase-force | conforms | No cherry-pick/rebase/force directed |
| orch.git.no-dev-agent-branches | conforms | Uses authoritative child publish ref |
| orch.git.one-epic-worktree-per-parent | conforms | Epic AST-1019 / this child only |
| orch.git.three-permanent-branches | conforms | No new permanent branch |
| orch.pipeline.call-susan-for-product-decisions | conforms | Title/meta shapes fixed by parent AC; Stage 3 stop-and-ask on new residuals |
| orch.pipeline.plan-is-bible | conforms | Concrete Done-when + closed residual inventory + verification |
| orch.pipeline.project-scoped-queues | conforms | Single Artifacts child |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready gate only |
| orch.roles.archie-approves-statutes | conforms | Does not amend statutes |
| orch.roles.betty-owns-test-tree | conforms | Engineer test-tree ban explicit |
| orch.roles.chuckles-never-ticket-assignee | conforms | No assignee inventiveness in plan |
| orch.roles.engineer-assignee-through-resolve | conforms | Build stays engineer-owned |
| orch.roles.pre-commit-path-bans | conforms | Touches `src/core/builder.py` only |
| astral.agent.confidence-bounds | conforms | No graded confidence path |
| astral.agent.do-task-delegation | conforms | No `do_task` changes |
| astral.agent.grade-vector-validation | conforms | No grade vectors |
| astral.batch.batch-id-first | conforms | No batch APIs |
| astral.batch.batch-id-format | conforms | No batch_id |
| astral.batch.claim-process-release | conforms | Not a batch processor |
| astral.batch.entity-agent-responses-latest-only | conforms | No agent_data latest-refs |
| astral.config.config-source-of-truth | conforms | Explicit Decision: title shape stays AC literal next to meta; no config overload of `type_scale.document_title` |
| astral.config.pass-threshold-vs-score-floor | conforms | No scoring thresholds |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env |
| astral.git.betty-no-src-or-features | conforms | Engineer edits `src/`; Betty banned |
| astral.layers.core-vs-external-bright-line | conforms | Emit chrome stays core builder |
| astral.layers.import-direction | conforms | Core-only Files Changed; no new imports |
| astral.patterns.coat-check-never-store-empty | conforms | No coat-check |
| astral.patterns.render-verdict-orchestrates-consult | conforms | No consult |
| astral.standards.data-raises-caller-logs | conforms | No data-layer error/log path |
| astral.standards.debug-contract-gated | conforms | No debug-contract adds |
| astral.standards.dry-and-focused-functions | conforms | Single `_emit_html_document` title/meta path for all three builders |
| astral.standards.in-scope-only | conforms | Title + meta lock + residual table only; stylesheet/structure out |
| astral.standards.logging-via-utils | conforms | No new logging |
| astral.standards.no-cross-contamination | conforms | Stays in `src/core` |
| astral.standards.no-hardcoded-sets | conforms | No new state sets; title is AC-required literal (Decision) |
| astral.standards.public-then-helpers | conforms | Edits existing helper construction line |
| astral.state.core-decides-transitions | conforms | No state transitions |
| astral.state.job-prior-states-enforced | conforms | No job states |
| astral.state.no-daisy-chain-in-run | conforms | No dispatch daisy-chain |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths miss plan Files Changed
- astral.debug.spikes-under-debug-dir — paths miss plan Files Changed
- astral.docs.features-single-file-per-ticket — layers/paths miss (Files Changed is core only)
- astral.git.engineer-test-tree-ban — paths miss (ban still honored in prose)
- astral.layers.scripts-exempt-from-layer-rules — layers/paths miss
- astral.layers.ui-config-driven-business-logic — layers/paths miss
- astral.patterns.require-auth-on-protected-endpoints — ui miss
- astral.standards.database-header-inventory — data miss
- astral.standards.utils-data-late-import-only — utils miss
- astral.ui.frontend-file-placement — ui miss
- astral.ui.naming-conventions — ui miss
- astral.ui.single-gunicorn-worker — layers/paths miss

## Findings

None (fix-now).

**acceptable:** Stage 2 is intentionally a no-diff lock when baseline already matches — correct adversarial guard against hardcoding the golden example meta string.

**Self-assessment:** Scope minor / Conf high / Risk low — honest for a one-line title fix plus meta lock.

— Joan
context_tokens≈52000

#### ada — 2026-07-29T02:12:14.384Z
Plan: [`docs/features/artifacts/ast-1021-residual-emit-chrome-tweaks.md`](https://github.com/susansomerset/astral/blob/sub/AST-1019/AST-1021-residual-emit-chrome-tweaks/docs/features/artifacts/ast-1021-residual-emit-chrome-tweaks.md) on `origin/sub/AST-1019/AST-1021-residual-emit-chrome-tweaks` @ `37527f56`.

**Scope:** `minor` — one document-title construction line in `builder.py` `_emit_html_document`, plus an explicit meta lock / residual no-op inventory; no config or UI changes.

**Conf:** `high` — title still uses `{name} — Resume` (and empty-name fallback is broken); meta template already matches AST-1010 field-derived contract; AST-1020 stylesheet is on ftr; residual table closed at plan time.

**Risk:** `low` — wrong title is tab/PDF chrome only; meta lock prevents forcing the golden example string; body structure and stylesheet stay untouched.

---

# Residual emit / chrome tweaks (Take 2: Resume Render Format discrepancies)

**Linear:** [AST-1021](https://linear.app/astralcareermatch/issue/AST-1021/residual-emit-chrome-tweaks-take-2-resume-render-format-discrepancies)
**Parent:** [AST-1019](https://linear.app/astralcareermatch/issue/AST-1019/take-2-resume-render-format-discrepancies) — Take 2: Resume Render Format discrepancies
**Publish ref:** `origin/sub/AST-1019/AST-1021-residual-emit-chrome-tweaks`

Cosmetic document-chrome adjustments the stylesheet sibling cannot fix: document `<title>` must be `{candidate_name} Resume` (single space; no em/en dashes) across the shared builder family; ATS `<meta name="description">` must stay candidate-specific from the AST-993/AST-1010 field-derived template (do **not** force the golden HTML’s example Product Manager / Cloud Platforms meta string); plus only emit-level `white-space` / class leftovers that CSS cannot paint. Does **not** rework AST-993 structural contracts, does **not** own embedded stylesheet golden parity ([AST-1020](https://linear.app/astralcareermatch/issue/AST-1020/embedded-stylesheet-golden-parity-take-2-resume-render-format) — already on `origin/ftr/ast-1019-take-2-resume-render-format-discrepancies`), and does **not** rewrite resume content.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/builder.py` | Fix `_emit_html_document` document `<title>` to `{name} Resume`; leave meta template as field-derived; apply only concrete residual emit chrome fixes found in Stage 3 (if any) | core |

**Out of scope (do not touch):** embedded `<style>` / `BUILD_CONFIG["default_style"]` tokens (AST-1020); header `Name • Title` / contact string join / marker vocabulary (AST-1010 / AST-1007); experience / education / skills / prior **markup** (AST-1008 / AST-1009); cover-letter HTML; external `styles07.css`; Manage Tasks prompts; `tests/`, bible (Betty).

## Current baseline (post–AST-1020 on ftr)

Inspected on epic worktree after `git merge origin/dev` + `git merge origin/ftr/ast-1019-take-2-resume-render-format-discrepancies`:

1. **Document `<title>` (must change):** `_emit_html_document` currently builds
   `html.escape(f"{render.get('candidate_name', '')} — Resume".strip() or "Resume")`
   — em dash between name and `Resume`. Empty name also fails the `or "Resume"` fallback because `"— Resume"` is truthy after strip. Parent / child AC require `{candidate_name} Resume` (space, no dashes), not `SomersetResume` and not `{name} — Resume`.
2. **Meta description (must keep):** When `candidate_name`, `candidate_title`, and `candidate_tagline` are all non-empty, emit already uses
   `Resume of {name}, {title}, specializing in {tagline}`
   with `html.escape` on the full content and omit-on-partial. The literal meta string in the desired HTML is structure-only — **do not** replace this template with that fixed example text.
3. **Stylesheet / structural emit:** Golden CSS + class names for body sections already land via AST-1020 / AST-993 stack. This ticket does not re-open those contracts.

## Stage 1: Document `<title>` → `{name} Resume`

**Done when:** For any render dict passed into `_emit_html_document` (via `build_session_base_resume`, `build_base_resume`, and `build_resume_from_job`), the HTML `<title>` text is `{candidate_name} Resume` when `candidate_name` is non-empty after strip, and exactly `Resume` when name is empty/missing — with no em dash (`—`), en dash (`–`), or hyphenated `SomersetResume`-style concatenation; value is HTML-escaped.

1. In `src/core/builder.py` `_emit_html_document`, replace the current `title_esc = …` line (today: `f"{render.get('candidate_name', '')} — Resume".strip() or "Resume"`) with construction from the already-computed `name_raw` (same strip source used for meta / h1):
   ```python
   title_esc = html.escape(f"{name_raw} Resume" if name_raw else "Resume")
   ```
2. Do **not** invent a last-name-only or camelCase title (no `SomersetResume`).
3. Do **not** put the title suffix / template into `BUILD_CONFIG` for this ticket.
   ⚠️ **Decision:** Keep the title string inline next to the existing meta template (same helper). Parent AC states the exact shape `{candidate_name} Resume`; `BUILD_CONFIG["default_style"]["type_scale"]["document_title"]` is CSS sizing metadata, not the HTML `<title>` text — do not overload it.
4. Do **not** change the `<title>…</title>` placement in the head template (stays after viewport meta, before `{meta_tag}` and `<style>`).
5. Do **not** edit `tests/` or bible — Betty owns assertions after Code Complete.

## Stage 2: Meta description — lock field-derived template (no golden-literal force)

**Done when:** Meta emit still matches the AST-1010 / parent laundry-list item 2 contract: content `Resume of {name}, {title}, specializing in {tagline}` only when all three of `name_raw` / `title_raw` / `tagline_raw` are non-empty; otherwise no `<meta name="description">`; values come from the paste/render fields (marker-applied strings already in `render`); the golden HTML’s example meta string about Product Manager / Cloud Platforms is **never** hardcoded.

1. In `src/core/builder.py` `_emit_html_document`, **read** the existing `meta_tag` block (the `if name_raw and title_raw and tagline_raw:` path). Confirm it still builds exactly:
   ```python
   meta_esc = html.escape(
       f"Resume of {name_raw}, {title_raw}, specializing in {tagline_raw}"
   )
   meta_tag = f'\n  <meta name="description" content="{meta_esc}" />'
   ```
2. **Do not change** that template, the omit-when-partial rule, escape order, or meta tag placement relative to `<title>` / `<style>`, unless Stage 1’s edit accidentally disturbed them — if disturbed, restore Stage 2 behavior to the contract above.
3. **Do not** assign the golden fixture’s literal `content="Resume of Susan Somerset, Senior Technical Product Manager / Program Manager specializing in Cloud Platforms, Agile Delivery, SaaS, and Healthcare."` (or any fixed paste-independent string) as the emit output.
   ⚠️ **Decision:** Meta work on this ticket is a **lock / no-force** pass, not a rewrite. AST-1010 already shipped the correct field-derived template; child AC 8 exists to prevent Take 2 from “matching” the desired HTML by hardcoding its example meta. If the inspected baseline already matches step 1, Stage 2 produces **no code diff** beyond Stage 1’s title line (still verify during build).

## Stage 3: Residual white-space / class emit leftovers (CSS cannot fix)

**Done when:** Against the shared `_emit_html_document` head + header chrome (and only emit attributes CSS cannot supply), either (a) no residual gaps remain beyond Stage 1 title, documented by the verification in Stage 4, or (b) any concrete leftover listed below is fixed in `builder.py` only. No AST-993 structural contract rework.

1. During **build-child**, after Stage 1–2, re-read the HTML template and header emit inside `_emit_html_document` (the `<header class="header">` / `<h1>` / `<div class="contact"><span>…</span></div>` block only — not section body emitters owned by AST-1008/1009).
2. Compare that chrome to parent laundry-list **document chrome** items 1–2 and child AC 7–10. Treat as **in-scope residual** only when **all** of the following are true:
   - It is emit markup / attribute / class-name on an element this helper already owns (document title, meta, h1 join already shipped, single contact span wrapper).
   - Golden CSS from AST-1020 cannot produce the desired look without the markup change.
   - Fixing it does **not** change experience / education / skills / prior section structure, marker vocabulary, or stylesheet rules.
3. **Pre-declared residual inventory from planning (authoritative):**
   | Gap | Disposition |
   |-----|-------------|
   | `<title>` `{name} — Resume` / empty-name `— Resume` | **Fix in Stage 1** |
   | Meta forced to golden example string | **Forbidden — Stage 2 lock** |
   | Contact multi-span vs single `<span>` | **No change** — desired HTML uses one contact `<span>`; AST-1020 CSS already has `.contact span { white-space: nowrap }` for that shape |
   | Meta tag order after `</style>` in desired HTML | **No change** — not in child AC; AST-1010 placement after `<title>` remains |
   | Body section class / role / education / skills markup | **Out of scope** — AST-993 / AST-1008 / AST-1009 / AST-1020 |
4. If build discovers a **new** residual that meets step 2 but is **not** in the table above, **stop**, comment on **parent** AST-1019 with the Stage blocked template (propose the markup delta), and wait — do not invent scope.
5. If the table’s dispositions cover everything found, Stage 3 adds **no further edits**.

## Stage 4: Three-surface chrome verification (manual / build verification)

**Done when:** With in-memory content that supplies non-empty `candidate_name`, `candidate_title`, `candidate_tagline`, and `candidate_contact_detail`, each of `build_session_base_resume`, `build_base_resume`, and `build_resume_from_job` produces HTML whose `<title>` is `{candidate_name} Resume` (space, no dash characters between name and Resume), whose `<meta name="description">` matches `Resume of {name}, {title}, specializing in {tagline}` from those fields (not the golden example Product Manager / Cloud Platforms string when title/tagline differ), and whose header/contact chrome class names match the existing shared builder (`header` / single contact `span`). Repeat once with empty `candidate_name` → `<title>Resume</title>`. Spike dumps only under `debug/spikes/AST-1021/` if used — never commit; never repo-root `artifacts/`.

1. During **build-child**, exercise the three public builders (REPL or ad-hoc under `debug/spikes/AST-1021/`).
2. String-check `<title>…</title>` and meta content on all three surfaces; confirm no `—` / `–` between name and `Resume` in the title.
3. Confirm one surface with a **non-golden** title/tagline still emits field-derived meta (proves AC 8).
4. If Stage 1–3 assumptions fail against current helpers, **stop**, comment on **parent** AST-1019 with the Stage blocked template, and wait — do not improvise.

## Self-Assessment

**Scope:** `minor` — one document-title construction line in `src/core/builder.py` `_emit_html_document`, plus an explicit meta lock / residual no-op inventory; no config or UI layer changes.

**Conf:** `high` — title bug and required shape are visible in current source; meta template already matches AST-1010 / parent AC; stylesheet sibling landed on ftr; residual table is closed at plan time.

**Risk:** `low` — wrong title string is cosmetic browser-tab / PDF chrome only; meta lock prevents regressing ATS description; body structure and stylesheet stay untouched.

## Code Rules self-review

- §1.3 DRY: title and meta remain the single path inside `_emit_html_document`; all three public resume builders already share it — no second document template.
- §1.1 / scope isolation: no stylesheet rewrite; no AST-993 structural emit changes; no cover letter; no Manage Tasks prompts.
- §1.4 / §2.1: no new magic sets; title shape stays a literal AC string (Decision); do not overload `type_scale.document_title` CSS metadata.
- §2.4 / §2.6: N/A.
- §3.3: core only; no new imports.
- §3.5 naming: unchanged field keys (`candidate_name` / `candidate_title` / `candidate_tagline`).
- §3.6: spikes under `debug/spikes/AST-1021/` only if used; never commit; never repo-root `artifacts/`.
- Engineer test-tree ban: no `tests/` or bible edits — Betty owns assertions after Code Complete.
- Sibling scope: AST-1020 owns CSS; this ticket owns title + meta lock + residual emit chrome only.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1019/AST-1021-residual-emit-chrome-tweaks`
**Plan path:** `docs/features/artifacts/ast-1021-residual-emit-chrome-tweaks.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `712bd324` | Document `<title>` → `{name} Resume` (empty → `Resume`) |
| 2–3 | — | Meta lock verified unchanged; residual inventory no further edits |
| 4 | — | Three-surface session/base/job + empty-name title checks (build verify) |

**Tip:** `712bd324` on `origin/sub/AST-1019/AST-1021-residual-emit-chrome-tweaks`

## Review (Radia — code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1021
**Publish ref tip (pre-docs):** `517faa964e4b670dd3f5332ef029b4ab0e6b610a`
**Overall:** DISCUSS

### What’s solid

- Stage 1: `<title>` is `{name_raw} Resume` / empty → `Resume`; em-dash + broken empty-name fallback gone.
- Stage 2–3: meta field-derived template unchanged (lock); residual inventory no further edits.
- Engineer footprint is the one title line in `_emit_html_document`; Betty owns tests via one `merge-tests(AST-1021)`.

### Issues / findings

**discuss (straggler):** Joan excluded several statutes against plan Files Changed; three-dot diff vs `origin/dev` brings in plan/docs/test/config history (incl. AST-1020). Each scores **conforms** — no product fix.

### Recommended actions

- Engineer: acknowledge stragglers (no code change). resolve-child → User Testing when clear.

## Resolution

**Date:** 2026-07-29  
**Outcome:** clean — no product code changes.

Acknowledged Radia’s **discuss (straggler)** items (Joan-excluded statutes brought in-scope by three-dot diff vs `origin/dev`, including AST-1020 history). Each **conforms** in substance. No **fix-now** items. Publish tip after resolve remains product + Betty + Radia stack on `origin/sub/AST-1019/AST-1021-residual-emit-chrome-tweaks`.
