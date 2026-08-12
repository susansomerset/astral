<!-- linear-archive: AST-1039 archived 2026-08-05 -->

## Linear archive (AST-1039)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1039/uat-summary-newlines-collapse-to-spaces-experience-ok  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1019 — Take 2: Resume Render Format discrepancies  
**Blocked by / blocks / related:** parent: AST-1019

### Description

## What failed

In Session Resume Paste → Open HTML, newline characters (`\n`) correctly become new bullets/paragraphs in the Experience section, but in Professional Summary the same newlines are converted to regular spaces — summary text collapses instead of splitting into multiple `.summary-intro` paragraphs.

## Expected

Summary newlines produce separate summary paragraphs (multiple `.summary-intro` `<p>` elements), consistent with how Experience treats newlines as structural breaks, and matching the desired HTML’s multi-paragraph Professional Summary.

## Repro

1. Open Session Resume Paste.
2. Paste a resume whose Professional Summary contains explicit newlines between paragraphs (and Experience lines that also use newlines).
3. Parse → Open HTML.
4. Confirm Experience honors newlines as new bullets/paragraphs.
5. Inspect Summary HTML: newlines appear as spaces within a single paragraph instead of separate `.summary-intro` paragraphs.

## Parent AC (quoted inline)

> Professional Summary as multiple `.summary-intro` paragraphs; … nested `__` / `~~` markers end-to-end.
> Susan can verify by eye against the desired HTML for every laundry-list item; no judgment call on "close enough."
> Fixture-driven UAT: Original-brief input paste → Open HTML matches desired structure + cosmetics (eye + HTML source). No "close enough."

## Diagnosis

* **Hypothesis:** Summary emit/join path collapses whitespace/newlines into a single string (or single paragraph), while Experience’s bullet/paragraph splitter still treats `\n` as a break — asymmetric newline handling between sections.
* **Correct outcome:** Paste newlines in Summary yield multiple `.summary-intro` paragraphs in HTML; Experience behavior stays correct.
* **Wrong fix to avoid:** Changing Experience newline rules to match the broken Summary; CSS-only visual fakes; rewriting summary *content*; treating this as stylesheet-only.
* **Related siblings / contracts:** AST-1021 residual emit; AST-993/1010 structural summary contracts; must not break AST-1027–1030 emit fixes or AST-1020 stylesheet.

## Boundaries

* This bug does **not** change: golden CSS block, document title/meta, competencies separators, `<no bullet>` lead rules, or Session Resume Paste chrome (AST-1035).
* "Fewer spaces" alone is not done — multi-paragraph Summary structure must match desired HTML.

### Comments

#### radia — 2026-07-29T17:00:09.094Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1039
**Publish ref:** 558b86f562f2378d62b6ca44c064c28f68b95e7e
**Overall:** CLEAN

Diff basis: required `origin/dev...` may report multiple merge bases. Product review uses AST-1039 commits + `origin/ftr/ast-1019-take-2-resume-render-format-discrepancies...HEAD`. Product @ `b76345ad` / merge-tests tip `c213ed4b` + this `docs()` append.

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| orch.git.betty-merge-tests-one-sha | universal | conforms | One `merge-tests(AST-1039): origin/tests 98103cee` |
| orch.git.commit-vocabulary | universal | conforms | `code`/`docs`/`test`/`merge-tests` vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | Forward publish to child `origin/sub/…` |
| orch.git.ftr-sub-topology | universal | conforms | Child sub under AST-1019; ftr..sub AST-1039 vocab |
| orch.git.merge-on-checkout | universal | conforms | No alternate merge inventiveness |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No cherry-pick/rebase/force |
| orch.git.no-dev-agent-branches | universal | conforms | Authoritative sub publish-ref |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Review in astral-AST-1019 |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branch |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | UAT diagnosis matches fixture; no product fork |
| orch.pipeline.plan-is-bible | universal | conforms | Stage 1 reuse cover-letter paragraph helper Done-when |
| orch.pipeline.project-scoped-queues | universal | conforms | Single Artifacts bug child |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Reviewed from Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty `test` + `merge-tests`; engineer avoided test tree |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | No Chuckles assignee inventiveness |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Review Posted without reassign |
| orch.roles.pre-commit-path-bans | universal | conforms | Engineer product path is `builder.py` + plan |
| astral.agent.confidence-bounds | scoped | conforms | No confidence/consult path |
| astral.agent.do-task-delegation | scoped | conforms | No `do_task` changes |
| astral.agent.grade-vector-validation | scoped | conforms | No grade/vector work |
| astral.batch.batch-id-first | scoped | conforms | No batch claim APIs |
| astral.batch.batch-id-format | scoped | conforms | No batch_id |
| astral.batch.claim-process-release | scoped | conforms | Not a batch processor |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | No agent_data latest-refs |
| astral.config.config-source-of-truth | scoped | conforms | No new config; reuse existing helper |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | No scoring thresholds |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No secrets/env |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss — no repo-root `artifacts/**` |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Plan under `docs/features/`; no spike pollution |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Single `docs/features/artifacts/ast-1039-….md` |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty commits only tests/bible (+ merge-tests) |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer code/docs omit tests/bible |
| astral.layers.core-vs-external-bright-line | scoped | conforms | Emit fix stays core builder; no external |
| astral.layers.import-direction | scoped | conforms | No new imports |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers/paths miss — no `scripts/**` |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | layers/paths miss — no UI/config src |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | No coat-check |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | No consult |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | layers/paths miss — no `src/ui/**` |
| astral.standards.data-raises-caller-logs | scoped | conforms | No data-layer error/log path |
| astral.standards.database-header-inventory | scoped | not-applicable | layers/paths miss — no `src/data/**` |
| astral.standards.debug-contract-gated | scoped | conforms | No debug-contract emission |
| astral.standards.dry-and-focused-functions | scoped | conforms | Reuses `_session_cover_letter_paragraphs` — no third dialect |
| astral.standards.in-scope-only | scoped | conforms | Summary split only; Experience/CSS/prompt untouched |
| astral.standards.logging-via-utils | scoped | conforms | No new logging |
| astral.standards.no-cross-contamination | scoped | conforms | Stays in core builder emit |
| astral.standards.no-hardcoded-sets | scoped | conforms | No new state sets; paragraph split logic only |
| astral.standards.public-then-helpers | scoped | conforms | Calls existing helper from emit path |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | layers/paths miss — no `src/utils/**` |
| astral.state.core-decides-transitions | scoped | conforms | No state transitions |
| astral.state.job-prior-states-enforced | scoped | conforms | No job state work |
| astral.state.no-daisy-chain-in-run | scoped | conforms | No dispatch daisy-chain |
| astral.ui.frontend-file-placement | scoped | not-applicable | layers/paths miss — no `src/ui/frontend/**` |
| astral.ui.naming-conventions | scoped | not-applicable | layers/paths miss — no `src/ui/**` |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | layers/paths miss — no worker/config/UI knobs |

## Pattern conformance

none cited

## Plan adherence

Stage 1 matches: replace blank-line-only `re.split` with `_session_cover_letter_paragraphs`. Experience path absent from code diff. Scope Single-Component matches.

## Findings

None.

### What’s solid

Single-`\n` Summary now becomes multiple `.summary-intro` paragraphs via proven cover-letter helper; blank-line behavior preserved.

### Recommended actions

resolve-child → User Testing.

**Notes:** no plan-rubric verdict attached. FIX-UAT mode. Ticket assignee was already Radia at review start — left unchanged.

— Radia
context_tokens≈32000

#### betty — 2026-07-29T16:56:48.429Z
## QA test manifest (AST-1039)

**Publish:** `origin/sub/AST-1019/AST-1039-uat-summary-newlines` @ `c213ed4b` (`merge-tests(AST-1039): origin/tests 98103cee`)

**FIX-UAT:** ftr bible advanced via rolled sibling merge-tests (incl. AST-1035) — skipped full bible re-read; grepped builder summary / cover-letter paragraph coverage.

### Classification

1. **Existing coverage:** AST-1024 cover-letter `_session_cover_letter_paragraphs` blank-line + single-`\n`; session/job summary emit paths (no prior `.summary-intro` count lock).
2. **Broken / obsolete:** none — blank-line `Para one\n\nPara two` preserved; only single-`\n` was missing.
3. **Gaps:** single-`\n` → multiple `.summary-intro`; blank-line regression; Experience `\n` → `<li>` unchanged.

### Manifest (narrowed)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_builder.py::TestAst1039SummaryNewlineParagraphs \
  tests/component/core/test_builder.py::TestAst1024BuildSessionCoverLetter::test_blank_line_paragraphs_and_single_chunk_newlines \
  -q
```

### Bible shasums (on publish ref)

- `docs/test-bible/core/builder.md` `6f90c56c64b41cefb45eb0ba974d9627c8daf5a5`

#### ada — 2026-07-29T16:53:16.228Z
Plan Ready — [docs/features/artifacts/ast-1039-uat-summary-newlines.md](https://github.com/susansomerset/astral/blob/sub/AST-1019/AST-1039-uat-summary-newlines/docs/features/artifacts/ast-1039-uat-summary-newlines.md) on `origin/sub/AST-1019/AST-1039-uat-summary-newlines` (`fc49b332`).

**Scope:** Single-Component — `builder.py` Professional Summary paragraph split only. Today `re.split(r"\n\s*\n")` ignores single `\n`, so one `.summary-intro` `<p>` collapses newlines to spaces; Experience already splits on `\n`. Reuse `_session_cover_letter_paragraphs` (blank-line then single-`\n` fallback).

**Conf:** high — emit path is explicit; cover-letter helper already has the contract; Experience contrast matches the bug Diagnosis.

**Risk:** low — blank-line behavior preserved; Experience/CSS/prompt/UI untouched.

---

# UAT: Summary newlines collapse to spaces (Experience ok)

**Linear:** [AST-1039](https://linear.app/astralcareermatch/issue/AST-1039/uat-summary-newlines-collapse-to-spaces-experience-ok)
**Parent:** [AST-1019](https://linear.app/astralcareermatch/issue/AST-1019/take-2-resume-render-format-discrepancies) — Take 2: Resume Render Format discrepancies
**Publish ref:** `origin/sub/AST-1019/AST-1039-uat-summary-newlines`

In Session Resume Paste → Open HTML, Experience already treats `\n` as structural breaks (accomplishment lines / bullets), but Professional Summary only splits on blank lines (`\n\s*\n`). Single newlines stay inside one `.summary-intro` `<p>`; the browser collapses them to spaces. Align Summary paragraph splitting with the existing cover-letter blank-line-then-single-`\n` fallback so paste newlines yield multiple `.summary-intro` paragraphs.

## UAT fitness

- **AC restored:** Parent AC (quoted on the bug): *“Professional Summary as multiple `.summary-intro` paragraphs; … nested `__` / `~~` markers end-to-end.”* / *“Susan can verify by eye against the desired HTML for every laundry-list item; no judgment call on ‘close enough.’”* / *“Fixture-driven UAT: Original-brief input paste → Open HTML matches desired structure + cosmetics (eye + HTML source). No ‘close enough.’”*
- **Correct outcome:** Paste newlines in Professional Summary produce separate `.summary-intro` `<p>` elements; Experience newline → bullet/paragraph behavior stays unchanged.
- **Sibling check:** AST-1020 stylesheet unchanged. AST-1021 residual emit / title-meta unchanged. AST-1027–1030 marker / keywords / competencies / `<no bullet>` contracts unchanged. AST-1035 View Parsed JSON chrome unchanged. AST-993/1010 structural summary contracts: still emit `.summary-intro` paragraphs — this restores multi-paragraph when the payload uses single `\n` (not only `\n\n`).
- **Not sufficient:** Fewer visual spaces inside one paragraph, or CSS `white-space` tricks — multi-paragraph Summary DOM must match desired HTML.
- **Wrong fix rejected:** Changing Experience newline rules to match broken Summary; CSS-only visual fakes; rewriting summary *content* in the prompt; treating this as stylesheet-only; inventing a second Summary fetch path.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/builder.py` | Summary paragraph split: blank lines first, then single-`\n` fallback (reuse existing cover-letter helper pattern) so each chunk becomes its own `.summary-intro` `<p>` | core |

**Out of scope (do not touch):** embedded golden CSS; Experience `_split_role_accomplishments`; `data/admin/agent_task.json` (prompt); Session Resume Paste UI; document title/meta; competencies; `<no bullet>`; `tests/` / bible (Betty).

## Root cause (plan-time)

In `_emit_body_sections_html`, the `professional_summary` branch does:

```python
paras = [p.strip() for p in re.split(r"\n\s*\n", str(text)) if p.strip()]
```

That only breaks on **blank lines**. A fixture / parse payload with single `\n` between summary paragraphs yields **one** `paras` entry containing embedded newlines; `html.escape` preserves those `\n` characters inside a single `<p class="summary-intro">`, and HTML whitespace collapsing turns them into spaces. Experience is fine because `_split_role_accomplishments` iterates `accomplishments.split("\n")`. Cover letter already solved the same asymmetry via `_session_cover_letter_paragraphs` (blank-line split, then if a single chunk still contains `\n`, split on `\n`).

**Git hygiene:** Keep `origin/sub/AST-1019/AST-1039-uat-summary-newlines` rooted on current `origin/ftr/ast-1019-take-2-resume-render-format-discrepancies` with only AST-1039 vocabulary commits in the `ftr..sub` range. Do **not** leave subjects matching `Merge remote-tracking branch`.

## Stage 1: Summary paragraph split honors single `\n`

**Done when:** Given `professional_summary` text with single `\n` between paragraphs (no blank line), `_emit_body_sections_html` / session Open HTML emits **two or more** `<p class="summary-intro">` elements (one per non-empty line/paragraph chunk). Blank-line-separated input (`Para one\n\nPara two`) still emits multiple paragraphs (existing behavior preserved). Experience emit path and `_split_role_accomplishments` are untouched. No CSS or prompt edits.

1. In `src/core/builder.py`, replace the inline `re.split(r"\n\s*\n", …)` in the `professional_summary` branch of `_emit_body_sections_html` with the **same** blank-line-then-single-`\n` semantics already used for session cover letters.
2. Prefer **reuse** of `_session_cover_letter_paragraphs(str(text))` (or a one-line rename to a shared helper e.g. `_paragraphs_blank_or_newline` called from both cover letter and summary) — do **not** duplicate a third split dialect.
3. Keep each non-empty chunk as `html.escape(p)` inside `<p class="summary-intro">` (markers still applied upstream via existing deep marker walk — do not invent a new marker pass here).
4. Do **not** change Experience branches, stylesheet CSS, parse API, or `craft_resume_base` prompts.
5. Do **not** edit `tests/` or bible — Betty owns assertions after Code Complete (existing blank-line case `"Para one\n\nPara two"` must keep passing; expect Betty to add a single-`\n` case).
   ⚠️ **Decision:** Builder emit fix only (reuse cover-letter paragraph helper). Prompt-only “emit `\n\n`” is **not** sufficient — Session Resume Paste fixtures and model output commonly use single `\n`, and Experience already treats `\n` as structural; Summary must match that contract in HTML structure. Always-split-on-every-`\n` without blank-line preference is acceptable only if reuse of the existing helper is blocked — default to the helper’s proven order (blank lines first, then `\n` fallback) so intentional multi-sentence paragraphs separated by `\n\n` stay intact when a paragraph itself has no internal newlines.

## Stage 2: Compile check (build verification)

**Done when:** `python3 -m py_compile src/core/builder.py` succeeds after Stage 1. Manual/build smoke: feed `build_session_base_resume` (or `_emit_body_sections_html`) a structure-enabled summary `"First para\nSecond para"` → two `.summary-intro` tags; `"First\n\nSecond"` still two; Experience job array with `\n` accomplishments unchanged. Spikes only under `debug/spikes/AST-1039/` if used — never commit; never repo-root `artifacts/`.

1. During **build-child**, run `python3 -m py_compile` on the changed builder file.
2. Confirm `git diff` does not touch CSS strings, Experience split helpers, prompts, or test-tree paths.
3. Note for UAT: Session Resume Paste fixture with multi-line Professional Summary → Open HTML → multiple `.summary-intro` paragraphs; Experience still correct.

## Self-Assessment

**Scope:** `Single-Component` — `src/core/builder.py` summary paragraph split only (reuse existing cover-letter helper semantics).

**Conf:** `high` — emit path is explicit; cover-letter helper already encodes the correct blank-line / `\n` contract; Experience contrast confirms diagnosis.

**Risk:** `low` — additive split fallback; blank-line behavior preserved; Experience/CSS/prompt untouched.

## Code Rules self-review

- §1.3 DRY: reuse `_session_cover_letter_paragraphs` (or shared rename) — no third newline dialect.
- §1.1 / scope isolation: no Experience/CSS/prompt/UI edits.
- Engineer test-tree ban: no `tests/` or bible edits.
- §3.6: spikes under `debug/spikes/AST-1039/` only if used.

## Review (Radia — code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1039
**Publish ref tip (pre-docs):** `c213ed4b1ef0d18dfaf9ae2b5463763e1967ec93`
**Overall:** CLEAN

### What’s solid

- `professional_summary` now uses `_session_cover_letter_paragraphs` (blank-line first, single-`\n` fallback) → multiple `.summary-intro`.
- Experience / CSS / prompts untouched. Engineer footprint is one builder line + plan.

### Issues / findings

None (fix-now / discuss).

### Recommended actions

resolve-child → User Testing.
