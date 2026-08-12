<!-- linear-archive: AST-1138 archived 2026-08-07 -->

## Linear archive (AST-1138)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1138/job-cover-html-somersetcover-fromblock-golden-css-cover-letter-header  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-1124 — Cover Letter Header is incorrect  
**Blocked by / blocks / related:** parent: AST-1124

### Description

## What this implements

After AST-1137: cover-only job HTML stops using resume header/contact as the cover header; emits SomersetCover `fromBlock` from candidate-owned text (fallback to defaults); applies the provided stylesheet for all cover style blocks; maps existing Subject / Letter / signature into letter body/signoff without dropping letter text; Style D debug on touched job cover emit. Does **not** own candidate from-block storage/UI, session Admin page, resume HTML, or AST-1123 token semantics.

## In scope

- [X] `pattern.layers.import-discipline` — config owns job→Somerset field map; builder emit applies it
- [X] `astral.standards.in-scope-only` — cover-only job Print Cover Letter path only
- [X] `astral.standards.no-cross-contamination` — do not mix resume header/contact into SomersetCover cover-only HTML
- [X] `astral.standards.debug-contract-gated` — Style D on `build_cover_letter_from_job` when `debug=True`
- [X] `astral.layers.import-direction` — builder → candidate resolve + utils config
- [X] `astral.standards.dry-and-focused-functions` — reuse session SomersetCover document helper for job cover-only
- [X] `astral.config.config-source-of-truth` — `BUILD_CONFIG["job_cover_somerset"]` artifact→field map

## Considered but excluded

- [X] Candidate from-block storage/UI + `resolve_cover_from_block` implementation — AST-1137 (consume only)
- [X] Session Admin Cover Letter empty-form defaults / golden parity tweaks — AST-1139
- [X] `{$SIGNATURE_IMAGE}` token semantics / omit policies — AST-1123 / AST-1125–1126 (reuse existing session emit path)
- [X] Resume Print / `build_resume` / `_emit_html_document` header+contact — out of epic; leave materials embed on legacy cover sections
- [X] `tests/` / bible — Betty

## Acceptance criteria

1. [x] Opening Print Cover Letter (cover-only HTML) for a job with a cover letter shows a `fromBlock` header matching the brief’s structure (identity lines with `<br>` between them), not a resume-style centered name/title + contact strip.
2. [x] The embedded `<style>` on cover-letter HTML includes rules for `.fromBlock`, `.toBlock`, `.letterdate`, `.lettersubject`, `.lettercontent`, `.letterSignoff`, and `.signature-img` that match the provided golden declarations (variable-backed colors/fonts allowed where the golden uses `var(--…)`).
3. [x] Resume Print / session base resume HTML is unchanged by this epic (still resume header/contact, not `fromBlock`).
4. [x] With `debug=True` on a touched cover emit path, debug output includes an index header and `|` detail for fromBlock source (candidate text vs default) and cover document path outcome.

## Boundaries

Does **not** own candidate from-block storage/UI (AST-1137), session Admin page (sibling), resume HTML, or AST-1123 token semantics.

## Notes for planning

After #1 (AST-1137). Reuse session SomersetCover emit where DRY allows.

## Git branch (authoritative)

Parent `ftr/AST-1124-cover-letter-header-is-incorrect`. Child `sub/AST-1124/AST-1138-job-cover-html-somersetcover-fromblock-golden-css`.

### Comments

#### chuckles — 2026-08-02T22:16:34.630Z
[merge-child] blocked: git pull merge on sub — `e7b3fe4f Merge remote-tracking branch 'origin/ftr/AST-1124-cover-letter-header-is-incorrect' into sub/AST-1124/AST-1138-…` fails validate-sub-log.

@Hedy Lamarr — republish `sub/AST-1124/AST-1138-job-cover-html-somersetcover-fromblock-golden-css` without `Merge remote-tracking branch` commits: `git fetch origin && git checkout sub/AST-1124/AST-1138-job-cover-html-somersetcover-fromblock-golden-css && git merge origin/ftr/AST-1124-cover-letter-header-is-incorrect` (not git pull), then push. Chuckles will re-run merge-child after.

— Chuckles

#### radia — 2026-08-02T21:57:51.270Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1138
**Publish ref:** `ef7e0776e4bdf95403b7e5b866c8649dc34c026d` (`origin/sub/AST-1124/AST-1138-job-cover-html-somersetcover-fromblock-golden-css`)
**Overall:** DISCUSS

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | conforms | not touched by this ticket’s behavior |
| astral.agent.do-task-delegation | scoped | conforms | not touched by this ticket’s behavior |
| astral.agent.grade-vector-validation | scoped | conforms | not touched by this ticket’s behavior |
| astral.batch.batch-id-first | scoped | conforms | not touched by this ticket’s behavior |
| astral.batch.batch-id-format | scoped | conforms | not touched by this ticket’s behavior |
| astral.batch.claim-process-release | scoped | conforms | not touched by this ticket’s behavior |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | not touched by this ticket’s behavior |
| astral.config.config-source-of-truth | scoped | conforms | BUILD_CONFIG[job_cover_somerset] artifact→field map |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | not touched by this ticket’s behavior |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | not touched by this ticket’s behavior |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths match none of ['artifacts/**', 'scripts/spikes/**'] |
| astral.debug.spikes-under-debug-dir | scoped | conforms | feature plans under docs/features/; not spike dumps |
| astral.dispatch.run-next-is-chain-authority | scoped | conforms | not touched by this ticket’s behavior |
| astral.dispatch.seed-auto-false | scoped | conforms | not touched by this ticket’s behavior |
| astral.docs.features-single-file-per-ticket | scoped | conforms | ast-1138 plan file present (sibling plans also on tip lineage) |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty commits touch tests/bible only |
| astral.git.engineer-test-tree-ban | scoped | conforms | test-tree on Betty test/merge-tests SHAs only |
| astral.layers.core-vs-external-bright-line | scoped | conforms | no external I/O |
| astral.layers.import-direction | scoped | conforms | builder→candidate resolve + utils |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers ['scripts'] ∩ diff ['core', 'docs', 'utils'] empty |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | config map only; no UI files |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | not touched by this ticket’s behavior |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | not touched by this ticket’s behavior |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | layers ['ui'] ∩ diff ['core', 'docs', 'utils'] empty |
| astral.seed.agent-tables-in-repo-json | scoped | conforms | not touched by this ticket’s behavior |
| astral.seed.archie-catalog-wins | scoped | conforms | not touched by this ticket’s behavior |
| astral.seed.boot-only-not-hot-path | scoped | conforms | not touched by this ticket’s behavior |
| astral.seed.define-approved | scoped | conforms | not touched by this ticket’s behavior |
| astral.seed.operator-rows-stay-deleted | scoped | conforms | not touched by this ticket’s behavior |
| astral.seed.other-via-coverage-join | scoped | conforms | not touched by this ticket’s behavior |
| astral.standards.data-raises-caller-logs | scoped | conforms | not touched by this ticket’s behavior |
| astral.standards.database-header-inventory | scoped | not-applicable | layers ['data'] ∩ diff ['core', 'docs', 'utils'] empty |
| astral.standards.debug-contract-gated | scoped | conforms | set_debug_flag + Style D only when debug=True |
| astral.standards.dry-and-focused-functions | scoped | conforms | shared _emit_somerset_cover_html_document; no CSS fork |
| astral.standards.in-scope-only | scoped | conforms | cover-only job path; resume emit untouched |
| astral.standards.logging-via-utils | scoped | conforms | builder _log debug helpers |
| astral.standards.names-not-ticket-ids | scoped | conforms | domain helper/API names; ticket only in comments/docs |
| astral.standards.no-cross-contamination | scoped | conforms | no resume header/contact shell on cover-only |
| astral.standards.no-hardcoded-sets | scoped | conforms | artifact_to_fields / unset_fields in config |
| astral.standards.public-then-helpers | scoped | conforms | private mappers beside cover emit helpers |
| astral.standards.utils-data-late-import-only | scoped | conforms | config literals only; no utils→data |
| astral.state.core-decides-transitions | scoped | conforms | not touched by this ticket’s behavior |
| astral.state.job-prior-states-enforced | scoped | conforms | not touched by this ticket’s behavior |
| astral.state.no-daisy-chain-in-run | scoped | conforms | not touched by this ticket’s behavior |
| astral.ui.frontend-file-placement | scoped | not-applicable | layers ['ui'] ∩ diff ['core', 'docs', 'utils'] empty |
| astral.ui.naming-conventions | scoped | not-applicable | layers ['ui'] ∩ diff ['core', 'docs', 'utils'] empty |
| astral.ui.single-gunicorn-worker | scoped | conforms | config touch unrelated to gunicorn |
| orch.git.betty-merge-tests-one-sha | universal | conforms | one merge-tests(AST-1138) @ 70b1f775 pinning tests 5427c279 |
| orch.git.commit-vocabulary | universal | conforms | docs/code/test/merge-tests vocabulary on sub |
| orch.git.flow-direction-inviolable | universal | conforms | publish on origin/sub/AST-1124/AST-1138-… |
| orch.git.ftr-sub-topology | universal | conforms | child sub under parent ftr/AST-1124-… |
| orch.git.merge-on-checkout | universal | conforms | no illegal merge recipe in commits |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | no cherry-pick/rebase/force on tip |
| orch.git.no-dev-agent-branches | universal | conforms | sub publish-ref only |
| orch.git.one-epic-worktree-per-parent | universal | conforms | astral-AST-1124 epic worktree |
| orch.git.three-permanent-branches | universal | conforms | no permanent-branch invention |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | no open product decisions in diff |
| orch.pipeline.plan-is-bible | universal | conforms | stages 1–4 match plan Files Changed |
| orch.pipeline.project-scoped-queues | universal | conforms | Artifacts child scope only |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | no canon/statutes edits |
| orch.roles.betty-owns-test-tree | universal | conforms | test/bible via Betty test+merge-tests commits |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee remains Hedy |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Hedy stays assignee through Tests Passed |
| orch.roles.pre-commit-path-bans | universal | conforms | no banned-path product edits |

## Pattern conformance

- Ticket-cited: `pattern.layers.import-discipline`, `in-scope-only`, `no-cross-contamination`, `debug-contract-gated`, `import-direction`, `dry-and-focused-functions`, `config-source-of-truth` — conforms (table)
- Invented pattern catalog: none

## Plan adherence

Stages 1–4 match Self-Assessment Single-Component: `job_cover_somerset` map + shared SomersetCover emit + `build_cover_letter_from_job` fromBlock rewrite + Style D. Resume `_emit_html_document` path unchanged. Session call site points at renamed helper.

## Findings

**discuss (C4 straggler):** Joan excluded `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, and `astral.debug.spikes-under-debug-dir` at plan time; three-dot vs `origin/dev` puts them in-scope. Sweep scores all three **conforms**.

**advisory:** Intermediate `a2eabbc7` briefly called helpers before defs; tip `c86c8be5`+ completes rename/defs before `merge-tests` — no tip defect.

## What's solid

Config map; shared emit + CSS selectors; no resume shell on cover-only; debug gated with `set_debug_flag` / `from_block_source` / `document_path=somerset_cover`; one merge-tests SHA.

## Notes

Joan plan-rubric APPROVED attached. §5f applied; §5g N/A. Docs append on plan file @ tip above.

context_tokens≈22000

#### betty — 2026-08-02T21:44:12.409Z
## QA test manifest

**Publish:** `origin/sub/AST-1124/AST-1138-job-cover-html-somersetcover-fromblock-golden-css` @ `70b1f775` (`merge-tests(AST-1138): origin/tests 5427c279`)

### 1. Existing coverage (bible-backed)
1. `tests/component/core/test_builder.py::TestAst1024BuildSessionCoverLetter` — shared SomersetCover DOM/CSS (helper rename; session behavior unchanged)
2. `tests/component/core/test_builder.py::TestAst1126CoverSignatureImageToken` — token-gated signature image on job cover path through Somerset emit
3. `tests/component/core/test_candidate.py::TestAst1137ResolveCoverFromBlock` — fromBlock resolve consumed by builder

### 2. Broken / obsolete (revised this pass)
1. `TestAst581ResumeCoverSplit::test_build_cover_letter_from_job_emits_cover_only` — was `aria-label="Cover body"` (resume shell); now SomersetCover `fromBlock` / `lettercontent`
2. `TestAst518BuilderResumeStructure::test_cover_letter_subject_letter_aliases_render_on_cover_route` — Subject/Letter → `lettersubject` / letter body (not resume cover-block)

### 3. Gaps (new)
1. `tests/component/core/test_builder.py::TestAst1138JobCoverSomersetFromBlock` — default + custom fromBlock, golden CSS selectors, no resume chrome, resume Print unchanged, Style D `from_block_source` / `document_path=somerset_cover`, mapper + candidate-shape helpers
2. `tests/component/utils/test_config.py::TestAst1138JobCoverSomersetConfig` — `BUILD_CONFIG["job_cover_somerset"]` map

### Run
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_builder.py::TestAst1138JobCoverSomersetFromBlock \
  tests/component/core/test_builder.py::TestAst581ResumeCoverSplit::test_build_cover_letter_from_job_emits_cover_only \
  tests/component/core/test_builder.py::TestAst518BuilderResumeStructure::test_cover_letter_subject_letter_aliases_render_on_cover_route \
  tests/component/core/test_builder.py::TestAst1126CoverSignatureImageToken \
  tests/component/utils/test_config.py::TestAst1138JobCoverSomersetConfig \
  -q
```

### Bible shasums (`origin/<publish-ref>`)
- `docs/test-bible/core/builder.md` — `c90b634bbc3c0589034d3adb6cc95a67fb9407476a1f2ec4b3bcf92947d813b2`
- `docs/test-bible/utils/config.md` — `0f621488c253e58101ee6492e8078766e6fe9934d4fb018454e67199bb1f6918`

— Betty

#### joan — 2026-08-02T21:24:03.118Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1138
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 Print Cover Letter shows SomersetCover fromBlock (not resume header) | Stages 2–3: rewrite `build_cover_letter_from_job` → shared SomersetCover emit + `resolve_cover_from_block` |
| AC2 unset → contact default composition | Stage 3: consume AST-1137 `resolve_cover_from_block` (`source=default`) |
| AC3 custom from-block text in fromBlock | Stage 3: same resolve (`source=candidate`) |
| AC4 embedded golden stylesheet for cover blocks | Stages 1–2: reuse `_emit_somerset_cover_html_document` CSS/DOM (parent brief / session golden) |
| AC5 Session Cover Letter fromBlock + stylesheet parity | N/A — boundary (AST-1139); Stage 2 keeps session call behavior-identical |
| AC6 Resume HTML unchanged | Stage 3 §4: leave `build_resume` / `_emit_html_document` / materials cover embed |
| AC7 debug=True Style D on touched cover emit | Stage 4: builder index + `from_block_source` / `document_path=somerset_cover` |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 job_cover_somerset config | Architectural config-block / field map; proposed child #2 |
| Stage 2 share SomersetCover emit | Functional scope DRY reuse of session SomersetCover; golden selectors |
| Stage 3 job cover-only → fromBlock | Purpose restore fromBlock header; AC1–3 emit side; no-cross-contamination |
| Stage 4 Style D debug | Functional scope / AC7 debug on job cover emit |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests |
| orch.git.commit-vocabulary | conforms | Publish on sub via engineer vocabulary |
| orch.git.flow-direction-inviolable | conforms | Publish only to origin/sub/… |
| orch.git.ftr-sub-topology | conforms | Child ref matches parent Git table |
| orch.git.merge-on-checkout | conforms | No illegal merge recipe |
| orch.git.no-cherry-pick-rebase-force | conforms | No cherry-pick/rebase/force |
| orch.git.no-dev-agent-branches | conforms | Uses sub/AST-1124/AST-1138-… only |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree astral-AST-1124 |
| orch.git.three-permanent-branches | conforms | No permanent-branch invention |
| orch.pipeline.call-susan-for-product-decisions | conforms | Decisions documented; Medium risk mitigated |
| orch.pipeline.plan-is-bible | conforms | Binding stages + Files Changed present |
| orch.pipeline.project-scoped-queues | conforms | Single-child Artifacts scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate-plan only |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | No tests/ edits |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Hedy) owns build |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer path after Plan Approved |
| orch.roles.pre-commit-path-bans | conforms | No banned-path edits |
| astral.agent.confidence-bounds | conforms | No graded agent_task path |
| astral.agent.do-task-delegation | conforms | No do_task changes |
| astral.agent.grade-vector-validation | conforms | No graded tasks |
| astral.batch.batch-id-first | conforms | No batch claim APIs |
| astral.batch.batch-id-format | conforms | No batch_id generation |
| astral.batch.claim-process-release | conforms | No batch processing |
| astral.batch.entity-agent-responses-latest-only | conforms | No agent_data RESPONSE writes |
| astral.config.config-source-of-truth | conforms | BUILD_CONFIG[job_cover_somerset] owns artifact→field map |
| astral.config.pass-threshold-vs-score-floor | conforms | No scoring/dispatch floors |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env values |
| astral.dispatch.run-next-is-chain-authority | conforms | No dispatch chain edits |
| astral.dispatch.seed-auto-false | conforms | No dispatch_task seed rows |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src; Betty excluded |
| astral.layers.core-vs-external-bright-line | conforms | Builder core emit; no external I/O added |
| astral.layers.import-direction | conforms | builder → candidate resolve + utils config |
| astral.layers.ui-config-driven-business-logic | conforms | No UI files; no React business rules |
| astral.patterns.coat-check-never-store-empty | conforms | No coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | conforms | No consult/render_verdict |
| astral.seed.agent-tables-in-repo-json | conforms | No seed JSON changes |
| astral.seed.archie-catalog-wins | conforms | No catalog seed work |
| astral.seed.boot-only-not-hot-path | conforms | No seed boot path |
| astral.seed.define-approved | conforms | No seed define path |
| astral.seed.operator-rows-stay-deleted | conforms | No operator seed rows |
| astral.seed.other-via-coverage-join | conforms | No seed coverage join |
| astral.standards.data-raises-caller-logs | conforms | No data-layer changes |
| astral.standards.debug-contract-gated | conforms | Stage 4 Style D only when debug=True |
| astral.standards.dry-and-focused-functions | conforms | Rename shared SomersetCover helper; no second CSS fork |
| astral.standards.in-scope-only | conforms | Cover-only job path; resume/session Admin left alone |
| astral.standards.logging-via-utils | conforms | Uses existing builder debug helpers |
| astral.standards.names-not-ticket-ids | conforms | Public/helper names describe function, not ticket ids |
| astral.standards.no-cross-contamination | conforms | Removes resume shell from cover-only; resume path untouched |
| astral.standards.no-hardcoded-sets | conforms | artifact_to_fields / unset_fields in BUILD_CONFIG |
| astral.standards.public-then-helpers | conforms | Private mappers beside cover emit helpers |
| astral.standards.utils-data-late-import-only | conforms | No utils→data import changes |
| astral.state.core-decides-transitions | conforms | No state transitions |
| astral.state.job-prior-states-enforced | conforms | No job state work |
| astral.state.no-daisy-chain-in-run | conforms | No dispatch run chaining |
| astral.ui.single-gunicorn-worker | conforms | No gunicorn/worker changes |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.dispatch.run-next-is-chain-authority, astral.dispatch.seed-auto-false, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.seed.agent-tables-in-repo-json, astral.seed.archie-catalog-wins, astral.seed.boot-only-not-hot-path, astral.seed.define-approved, astral.seed.operator-rows-stay-deleted, astral.seed.other-via-coverage-join, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.names-not-ticket-ids, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths match none
- astral.debug.spikes-under-debug-dir — paths match none
- astral.docs.features-single-file-per-ticket — layers {docs} ∩ plan empty
- astral.git.engineer-test-tree-ban — paths match none
- astral.layers.scripts-exempt-from-layer-rules — layers {scripts} ∩ plan empty
- astral.patterns.require-auth-on-protected-endpoints — layers {ui} ∩ plan empty
- astral.standards.database-header-inventory — layers {data} ∩ plan empty
- astral.ui.frontend-file-placement — layers {ui} ∩ plan empty
- astral.ui.naming-conventions — layers {ui} ∩ plan empty

## Findings

None fix-now.

**discuss (non-blocking):** Golden CSS stays in the shared emit helper (AST-1024) rather than moving into config; this child adds the field map in `BUILD_CONFIG` and reuses the helper — matches child citations / DRY. Empty `letter_date` still emits `.letterdate` on the job path (explicit Decision).

**acceptable:** Self-assessment Single-Component / Conf high / Risk Medium with concrete mitigations (reuse session emitter; resume paths untouched).

**R6 checklist:** Definition fidelity pass for proposed child #2. Layer/import pass. Config map in BUILD_CONFIG. No UI. Resume/session Admin boundaries held. Debug gated. No sibling scope creep into AST-1137/1139 ownership.

context_tokens≈42000

— Joan

#### hedy — 2026-08-02T21:22:02.228Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-1124/AST-1138-job-cover-html-somersetcover-fromblock-golden-css/docs/features/artifacts/ast-1138-job-cover-html-somersetcover-fromblock-golden-css.md

**Scope:** Single-Component — config map + `builder.py` cover-only emit rewrite reusing session SomersetCover helper; no UI.

**Conf:** high — AST-1137 resolve + AST-1024 SomersetCover emit already exist; this ticket is wiring and field mapping.

**Risk:** Medium — Print Cover Letter is user-visible; wrong mapping could drop Letter body or keep resume chrome. Mitigated by reusing the session emitter and leaving resume paths untouched.

---

# AST-1138 — Job cover HTML — SomersetCover fromBlock + golden CSS

**Linear:** https://linear.app/astralcareermatch/issue/AST-1138/job-cover-html-somersetcover-fromblock-golden-css-cover-letter-header  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1124/cover-letter-header-is-incorrect  
**Publish ref:** `sub/AST-1124/AST-1138-job-cover-html-somersetcover-fromblock-golden-css`

After AST-1137: Print Cover Letter (cover-only job HTML via `build_cover_letter` / `build_cover_letter_from_job`) stops using the resume document header/contact strip; emits SomersetCover `fromBlock` from `resolve_cover_from_block`; reuses the existing SomersetCover stylesheet/DOM (session emit) for all cover style blocks; maps job Subject / Letter / signature into letter subject/body/signoff without dropping letter text; Style D debug on the touched job cover emit path. Does **not** own candidate from-block storage/UI, session Admin page defaults/CSS parity (AST-1139), resume HTML, or AST-1123 token semantics.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `BUILD_CONFIG["job_cover_somerset"]` — document title reuse + which session field keys job artifacts map into (no new CSS literals in config). Optional empty-string defaults for fields job artifacts do not store (`letter_date`, `to_block`, `signoff_closing`). | utils |
| `src/core/builder.py` | Rename/generalize session SomersetCover HTML helper for shared job+session use; add job→Somerset field mapper; rewrite `build_cover_letter_from_job` to call `resolve_cover_from_block` + shared SomersetCover emit (no resume `_emit_html_document` for cover-only); Style D debug for fromBlock source + document path. | core |

**Out of files (siblings / boundaries):** `CandidateProfile.tsx` / `COVER_FROM_BLOCK_CONFIG` / `resolve_cover_from_block` implementation (AST-1137 — consume only); `AdminSessionCoverLetter.tsx` / session empty-form defaults (AST-1139); `build_resume` / `build_base_resume` / `_emit_html_document` resume header+contact path; AST-1123 token literal/policy changes; `tests/`, bible.

## Stage 1: Config — job Somerset field map

**Done when:** `BUILD_CONFIG["job_cover_somerset"]` declares document title and the mapping from normalized job cover keys (`re_line`/`body`/`signature`) to Somerset session field keys; no builder behavior change yet.

1. In `src/utils/config.py`, inside `BUILD_CONFIG` immediately after `"session_cover_letter"`, add:
   ```python
   "job_cover_somerset": {
       "document_title_key": "session_cover_letter",  # reuse BUILD_CONFIG[…]["document_title"]
       # Normalized job cover keys → session_cover_letter field keys
       "artifact_to_fields": {
           "re_line": "subject",
           "body": "letter",
           "signature": "signature",
       },
       # Session fields job artifacts do not store — always "" for job Print Cover Letter
       "unset_fields": ("from_block", "letter_date", "to_block", "signoff_closing"),
   },
   ```
   `from_block` is listed under `unset_fields` as the **artifact** default (filled at emit from `resolve_cover_from_block`, not from the job artifact).
2. Do **not** duplicate golden CSS declarations into config — CSS stays in the shared SomersetCover emit helper (already matches parent brief / session AST-1024).
3. Do **not** change `session_cover_letter` required flags or Admin API contracts.

⚠️ **Decision:** Job artifacts stay `Subject`/`Letter`/`signature` (normalize via existing `_cover_letter_fields_for_read`). Layout-only session keys (`letter_date`, `to_block`, `signoff_closing`) are empty on the job path — omit-empty optional blocks already handled by the SomersetCover emit helper for `to_block`/`subject`; empty `letter_date` still emits the `.letterdate` div (same as session with blank date) so the stylesheet selector remains exercised without inventing a date.

## Stage 2: Share SomersetCover emit (DRY)

**Done when:** Session and job cover-only HTML both call one SomersetCover document helper; session public API behavior unchanged; helper docstring no longer claims "session-only".

1. In `src/core/builder.py`, rename `_emit_session_cover_html_document` → `_emit_somerset_cover_html_document`.
2. Update the helper signature to accept optional `document_title: Optional[str] = None`. When `None`, read title from `BUILD_CONFIG["session_cover_letter"]["document_title"]` (current behavior). When provided (job path), use the override — job path resolves override via `BUILD_CONFIG["job_cover_somerset"]["document_title_key"]` → that block's `"document_title"` (same string today: `SomersetCover`).
3. Keep CSS/DOM exactly as today (parent golden: `body`, `.cover-letter`, `.fromBlock`, `.toBlock`, `.letterdate`, `.lettersubject`, `.lettercontent` (+ `p` / `p:last-child`), `.letterSignoff`, `.signature-img`, `@page` / `@page :first`, print media rules). Do **not** edit selector/declaration values in this ticket unless a literal drift from the parent brief is found while reading the helper — if drift is found, align to the parent Description golden only (same as session target for AST-1139).
4. Point `build_session_cover_letter` at the renamed helper (behavior-identical call).
5. Keep `_session_cover_letter_paragraphs` name (shared paragraph split) — no rename required.

⚠️ **Decision:** Rename + thin title override beats copying the ~200-line CSS/DOM into a second job-only emitter (`astral.standards.dry-and-focused-functions`). AST-1139 can still tune session defaults without forking job CSS.

## Stage 3: Job cover-only → SomersetCover + fromBlock

**Done when:** `build_cover_letter_from_job` returns SomersetCover HTML with `fromBlock` from AST-1137 resolve; Subject/Letter/signature mapped; no resume `h1`/`.contact` chrome; resume builders untouched.

1. Add helper (private, near cover emit helpers):

   ```python
   def _job_cover_somerset_fields(cover: dict, from_block_text: str) -> dict:
       """Map normalized job cover + resolved from-block into session field keys."""
   ```

   Implementation (literal):
   - Start from `BUILD_CONFIG["job_cover_somerset"]`.
   - Build `fields: Dict[str, str]` with every key in `BUILD_CONFIG["session_cover_letter"]["fields"]` initialized to `""`.
   - For each `unset_fields` name, leave `""` (then set `from_block` from argument).
   - For each `(artifact_key, field_key)` in `artifact_to_fields.items()`, set `fields[field_key] = str(cover.get(artifact_key) or "")`.
   - `fields["from_block"] = from_block_text` (may be `""` if resolve returned empty).
   - Return `fields`.

2. Add helper to shape the coerced builder candidate blob for `resolve_cover_from_block`:

   ```python
   def _candidate_for_cover_from_block(cd: dict) -> dict:
   ```

   Map `_full`/`_first`/`_last` → `full`/`first`/`last`, pass through `contact` dict, and copy `astral_candidate_id` / `_astral_candidate_id` if present on `cd`. Do **not** change `resolve_cover_from_block` itself.

3. Rewrite `build_cover_letter_from_job` success path (after `_resolve_cover_letter` succeeds):
   - **Remove** the `_apply_contact_to_render_dict` / `_apply_resume_text_markers` / `_merge_effective_style` / `_emit_html_document(..., include_cover=True, body_section_ids=[])` path for this function.
   - `from_res = candidate_mod.resolve_cover_from_block(_candidate_for_cover_from_block(cd), debug=debug)` — import already via `candidate_mod` if present; else `from src.core import candidate as candidate_mod` (module already imports candidate for loads).
   - Resolve signature image the same way session does: `_signature_image_token_status(cover.get("signature") or "", {"contact": cd.get("contact") or {}})` (or pass a root that satisfies `tok["path"]` = `contact.cover_letter_signature_image`).
   - `fields = _job_cover_somerset_fields(cover, from_res["text"])`.
   - `html_out = _emit_somerset_cover_html_document(fields, signature_image_src=sig_src, document_title=…)` where title is loaded via `job_cover_somerset["document_title_key"]`.
   - Preserve existing `ValueError` when no cover content.
   - Do **not** change `build_cover_letter` load/orchestration except that it still returns `build_cover_letter_from_job(...)`.

4. **Do not** change `build_resume` / `_emit_html_document` / `_emit_cover_sections_html` — materials resume+cover embed and Resume Print stay on the resume stylesheet. Cover-only Print Cover Letter is the sole consumer of this rewrite (`/candidate/cover/<job_id>` → `build_cover_letter`).

5. Signature image token replace stays inside `_emit_somerset_cover_html_document` (AST-1126 session path). Do not reintroduce auto-image-above-name (`cover-signoff` job path is unused for cover-only after this change).

⚠️ **Decision:** Cover-only leaves the legacy `_emit_cover_sections_html` path for `build_resume` materials embed so Resume Print AC stays green without expanding into AST-1139/resume work. Parent AC #1 targets Print Cover Letter only.

## Stage 4: Style D debug on job cover emit

**Done when:** `debug=True` on `build_cover_letter_from_job` emits one index header + `|` details for fromBlock source and cover document path; no new debug when `debug=False`.

1. Replace/extend the existing debug block in `build_cover_letter_from_job` (keep `func="builder.build_cover_letter_from_job"`):
   - Index outcome: `success — somerset cover html` (or equivalent short success string).
   - `|` `from_block_source={from_res["source"]}` — must be one of `COVER_FROM_BLOCK_CONFIG["sources"]` values (`candidate` / `default`).
   - `|` `from_block_chars={len(from_res["text"])}`
   - `|` `document_path=somerset_cover` (literal distinguishing from old resume-shell path).
   - `|` `cover_source={cover_src!r}` (existing `_cover_letter_source_label`).
   - `|` field presence for mapped subject/letter/signature (nonempty bools).
   - Keep existing signature image token/image status lines and `html_chars` / preview block.
2. `resolve_cover_from_block(..., debug=debug)` may also emit its own index when debug — that is acceptable (AST-1137). Job emit must still log the fromBlock source on the **builder** index so cover-path debugging is scannable without reading candidate logs alone.
3. No React/UI debug.

## Contract check (manual — builder notes only)

- Print Cover Letter HTML contains `<div class="fromBlock">` with `<br>` between identity lines when defaults resolve to two lines; no centered resume `h1` / `.contact` strip as the cover header.
- Embedded `<style>` includes `.fromBlock`, `.toBlock`, `.letterdate`, `.lettersubject`, `.lettercontent`, `.letterSignoff`, `.signature-img` matching the shared golden helper.
- `build_resume` / `build_base_resume` HTML still uses resume header/contact (spot-check unchanged).
- Custom `contact.cover_letter_from_block` → `from_block_source=candidate`; empty → `default`.

## Self-Assessment

**Scope:** `Single-Component` — config map + `builder.py` cover-only emit rewrite reusing session SomersetCover helper; no UI.

**Conf:** `high` — AST-1137 resolve + AST-1024 SomersetCover emit already exist; this ticket is wiring and field mapping.

**Risk:** `Medium` — Print Cover Letter is user-visible; wrong mapping could drop Letter body or keep resume chrome. Mitigated by reusing the battle-tested session emitter and leaving resume paths untouched.

## Code Rules check

- §1.1 in-scope-only / no-cross-contamination: job cover-only only; no resume golden reopen; no session Admin defaults (AST-1139).
- §1.3 DRY: one SomersetCover document helper for session + job.
- §1.5.1 debug-contract-gated: Style D only when `debug=True`.
- §2.1 / §1.4: field map + unset keys in `BUILD_CONFIG["job_cover_somerset"]`.
- §3.3 import direction: builder → candidate resolve + utils config; no UI import.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1124/AST-1138-job-cover-html-somersetcover-fromblock-golden-css`

| Stage | Summary |
|-------|---------|
| 1 | `BUILD_CONFIG["job_cover_somerset"]` artifact→Somerset field map |
| 2 | Shared `_emit_somerset_cover_html_document` (session call sites updated) |
| 3 | `build_cover_letter_from_job` → resolve fromBlock + SomersetCover (no resume shell) |
| 4 | Style D debug: fromBlock source + `document_path=somerset_cover` |

**Build:** `code(AST-1138)` on `sub/AST-1124/AST-1138-job-cover-html-somersetcover-fromblock-golden-css` — `c86c8be587a10c29e1476a18e85a53bd6523f227`.

## Radia review (code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1138
**Publish ref:** `70b1f775a1f675c828d1fd6d493126bc6b7c6141` (`origin/sub/AST-1124/AST-1138-job-cover-html-somersetcover-fromblock-golden-css`)
**Overall:** DISCUSS

### What's solid

- Stages 1–4 match the plan: `job_cover_somerset` config map; `_emit_somerset_cover_html_document` rename + title override; `_candidate_for_cover_from_block` / `_job_cover_somerset_fields`; `build_cover_letter_from_job` uses `resolve_cover_from_block` + SomersetCover (no resume `_emit_html_document` shell); Style D with `set_debug_flag`, `from_block_source`, `document_path=somerset_cover`.
- Golden selectors present on shared helper; `build_resume` / `_emit_html_document` path retained for resume.
- Session call site updated to renamed helper; no second CSS fork.
- One `merge-tests(AST-1138)`; helpers landed in follow-up `code(AST-1138)` before tests.

### Issues

**discuss (C4 straggler):** Joan excluded `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, and `astral.debug.spikes-under-debug-dir` at plan time; three-dot vs `origin/dev` puts them in-scope. Sweep scores all three **conforms**.

**advisory:** Intermediate commit `a2eabbc7` briefly called helpers before they were defined; tip `c86c8be5`+ completes the rename/defs before `merge-tests` — no tip defect.

### Recommended actions

1. Hedy: no product fix required for AST-1138 AC; acknowledge discuss via resolve-child (or no-op).

### Pattern conformance

Ticket-cited: `pattern.layers.import-discipline` / `in-scope-only` / `no-cross-contamination` / `debug-contract-gated` / `import-direction` / `dry-and-focused-functions` / `config-source-of-truth` — conforms (table). Invented catalog: none.

### Plan adherence

Self-Assessment Single-Component matches config + builder cover-only rewrite. Resume/session Admin boundaries held. CSS stays in shared helper per Joan discuss.

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | conforms | not touched by this ticket’s behavior |
| astral.agent.do-task-delegation | scoped | conforms | not touched by this ticket’s behavior |
| astral.agent.grade-vector-validation | scoped | conforms | not touched by this ticket’s behavior |
| astral.batch.batch-id-first | scoped | conforms | not touched by this ticket’s behavior |
| astral.batch.batch-id-format | scoped | conforms | not touched by this ticket’s behavior |
| astral.batch.claim-process-release | scoped | conforms | not touched by this ticket’s behavior |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | not touched by this ticket’s behavior |
| astral.config.config-source-of-truth | scoped | conforms | BUILD_CONFIG[job_cover_somerset] artifact→field map |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | not touched by this ticket’s behavior |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | not touched by this ticket’s behavior |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths match none of ['artifacts/**', 'scripts/spikes/**'] |
| astral.debug.spikes-under-debug-dir | scoped | conforms | feature plans under docs/features/; not spike dumps |
| astral.dispatch.run-next-is-chain-authority | scoped | conforms | not touched by this ticket’s behavior |
| astral.dispatch.seed-auto-false | scoped | conforms | not touched by this ticket’s behavior |
| astral.docs.features-single-file-per-ticket | scoped | conforms | ast-1138 plan file present (sibling plans also on tip lineage) |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty commits touch tests/bible only |
| astral.git.engineer-test-tree-ban | scoped | conforms | test-tree on Betty test/merge-tests SHAs only |
| astral.layers.core-vs-external-bright-line | scoped | conforms | no external I/O |
| astral.layers.import-direction | scoped | conforms | builder→candidate resolve + utils |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers ['scripts'] ∩ diff ['core', 'docs', 'utils'] empty |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | config map only; no UI files |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | not touched by this ticket’s behavior |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | not touched by this ticket’s behavior |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | layers ['ui'] ∩ diff ['core', 'docs', 'utils'] empty |
| astral.seed.agent-tables-in-repo-json | scoped | conforms | not touched by this ticket’s behavior |
| astral.seed.archie-catalog-wins | scoped | conforms | not touched by this ticket’s behavior |
| astral.seed.boot-only-not-hot-path | scoped | conforms | not touched by this ticket’s behavior |
| astral.seed.define-approved | scoped | conforms | not touched by this ticket’s behavior |
| astral.seed.operator-rows-stay-deleted | scoped | conforms | not touched by this ticket’s behavior |
| astral.seed.other-via-coverage-join | scoped | conforms | not touched by this ticket’s behavior |
| astral.standards.data-raises-caller-logs | scoped | conforms | not touched by this ticket’s behavior |
| astral.standards.database-header-inventory | scoped | not-applicable | layers ['data'] ∩ diff ['core', 'docs', 'utils'] empty |
| astral.standards.debug-contract-gated | scoped | conforms | set_debug_flag + Style D only when debug=True |
| astral.standards.dry-and-focused-functions | scoped | conforms | shared _emit_somerset_cover_html_document; no CSS fork |
| astral.standards.in-scope-only | scoped | conforms | cover-only job path; resume emit untouched |
| astral.standards.logging-via-utils | scoped | conforms | builder _log debug helpers |
| astral.standards.names-not-ticket-ids | scoped | conforms | domain helper/API names; ticket only in comments/docs |
| astral.standards.no-cross-contamination | scoped | conforms | no resume header/contact shell on cover-only |
| astral.standards.no-hardcoded-sets | scoped | conforms | artifact_to_fields / unset_fields in config |
| astral.standards.public-then-helpers | scoped | conforms | private mappers beside cover emit helpers |
| astral.standards.utils-data-late-import-only | scoped | conforms | config literals only; no utils→data |
| astral.state.core-decides-transitions | scoped | conforms | not touched by this ticket’s behavior |
| astral.state.job-prior-states-enforced | scoped | conforms | not touched by this ticket’s behavior |
| astral.state.no-daisy-chain-in-run | scoped | conforms | not touched by this ticket’s behavior |
| astral.ui.frontend-file-placement | scoped | not-applicable | layers ['ui'] ∩ diff ['core', 'docs', 'utils'] empty |
| astral.ui.naming-conventions | scoped | not-applicable | layers ['ui'] ∩ diff ['core', 'docs', 'utils'] empty |
| astral.ui.single-gunicorn-worker | scoped | conforms | config touch unrelated to gunicorn |
| orch.git.betty-merge-tests-one-sha | universal | conforms | one merge-tests(AST-1138) @ 70b1f775 pinning tests 5427c279 |
| orch.git.commit-vocabulary | universal | conforms | docs/code/test/merge-tests vocabulary on sub |
| orch.git.flow-direction-inviolable | universal | conforms | publish on origin/sub/AST-1124/AST-1138-… |
| orch.git.ftr-sub-topology | universal | conforms | child sub under parent ftr/AST-1124-… |
| orch.git.merge-on-checkout | universal | conforms | no illegal merge recipe in commits |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | no cherry-pick/rebase/force on tip |
| orch.git.no-dev-agent-branches | universal | conforms | sub publish-ref only |
| orch.git.one-epic-worktree-per-parent | universal | conforms | astral-AST-1124 epic worktree |
| orch.git.three-permanent-branches | universal | conforms | no permanent-branch invention |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | no open product decisions in diff |
| orch.pipeline.plan-is-bible | universal | conforms | stages 1–4 match plan Files Changed |
| orch.pipeline.project-scoped-queues | universal | conforms | Artifacts child scope only |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | no canon/statutes edits |
| orch.roles.betty-owns-test-tree | universal | conforms | test/bible via Betty test+merge-tests commits |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee remains Hedy |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Hedy stays assignee through Tests Passed |
| orch.roles.pre-commit-path-bans | universal | conforms | no banned-path product edits |

## Notes

Joan plan-rubric APPROVED attached. §5f applied; §5g N/A. Three-dot includes AST-1137 lineage + sibling plan docs vs `origin/dev`.

context_tokens≈22000

## Resolution

**Date:** 2026-08-02  
**Review:** Radia `[code-rubric] revision=1` — Overall **DISCUSS** (no fix-now). Publish tip at review: `ef7e0776`.

| Finding | Action |
|---------|--------|
| discuss — C4 stragglers (`features-single-file-per-ticket`, `engineer-test-tree-ban`, `spikes-under-debug-dir`) now in-scope vs `origin/dev`; sweep **conforms** | No product change — acknowledged; tip already conforms |
| advisory — intermediate helper-order SHA | No tip defect; no change |

Merged `origin/dev` + `origin/ftr/AST-1124-cover-letter-header-is-incorrect` + `origin/<publish-ref>` before User Testing. No product edits required for this resolve pass.
