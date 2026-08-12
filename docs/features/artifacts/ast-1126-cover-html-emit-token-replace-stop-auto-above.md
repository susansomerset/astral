<!-- linear-archive: AST-1126 archived 2026-08-07 -->

## Linear archive (AST-1126)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1126/cover-html-emit-token-replace-and-stop-auto-above-support-signature  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-1123 — Support Signature_Image as a token in the cover letter  
**Blocked by / blocks / related:** parent: AST-1123

### Description

## What this implements

After AST-1125: cover HTML emit (job + session) stops unconditional/default image placement; replaces `{$SIGNATURE_IMAGE}` with a safe image at the token position only; if the token is absent, omit the image (no fallback insert); Style D debug on touched cover paths. Does **not** own profile upload UI or resume emit.

## In scope

- [X] `astral.standards.in-scope-only` — job + session cover HTML emit only (`builder.py` cover paths)
- [X] `astral.standards.no-cross-contamination` — do not teach resume emit to read `cover_letter_render_tokens`
- [X] `astral.standards.debug-contract-gated` — Style D token/image details only when `debug=True` on touched cover paths
- [X] `astral.layers.import-direction` / `pattern.layers.import-discipline` — core consumes `get_cover_letter_render_token`; no layer inversion
- [X] `astral.standards.dry-and-focused-functions` — reuse `_safe_image_src`; shared replace helper; no second image validator
- [X] `astral.config.config-source-of-truth` / `astral.standards.no-hardcoded-sets` — literal, path, and omit policies from AST-1125 accessor only

## Considered but excluded

- [X] `pattern.config.config-block` / config contract registration — AST-1125 owns `BUILD_CONFIG["cover_letter_render_tokens"]`
- [X] Candidate Profile upload/validation UI — out of boundaries
- [X] Resume (base / job / session) HTML emit — must not resolve `{$SIGNATURE_IMAGE}`
- [X] `TOKEN_SOURCES` / `resolve_tokens` — binary image must not enter LLM prompts
- [X] Admin React Session Cover Letter page — AST-1025; no UI change this ticket

## Acceptance criteria

1. [x] Rendering a job cover letter whose signature text contains `{$SIGNATURE_IMAGE}` between the closing and the name/title shows the signature image in that position — not above the closing.
2. [x] The literal token string `{$SIGNATURE_IMAGE}` does not appear in the rendered cover HTML when a valid image is available.
3. [x] When the candidate has no usable signature image, cover render does not emit a signature `<img>`, and the layout does not leave a broken image placeholder.
4. [x] Cover letter HTML no longer places the signature image above the full signature text block as an unconditional prepend.
5. [x] Resume (base / job / session) HTML render paths do not resolve or display `{$SIGNATURE_IMAGE}` as an image.
6. [x] With `debug=True` on a touched cover render path, debug output includes an index header and `|` detail for token presence and image accepted / absent / rejected.

## Boundaries

* Does **not** own the config token contract (sibling AST-1125).
* Does **not** change Candidate Profile upload/validation UI.
* Does **not** touch resume emit paths.
* Does **not** edit Admin React Session Cover Letter page (AST-1025).

## Notes for planning

Blocked by AST-1125. Token-only placement — no default image inject on job or session cover.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1123-support-signature-image-as-a-token-in-the-cover-letter`, child `sub/AST-1123/AST-1126-cover-html-emit-token-replace-stop-auto-above`. Created at dispatch-parent.

### Comments

#### radia — 2026-08-02T18:16:20.585Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1126
**Publish ref:** `origin/sub/AST-1123/AST-1126-cover-html-emit-token-replace-stop-auto-above` tip `0364b533844f2f1d45549b00be7404924f3853b5` (product/tests through `6570adbd` + docs review append)
**Overall:** DISCUSS

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | conforms | no graded-task / confidence edits |
| `astral.agent.do-task-delegation` | scoped | conforms | builder emit only; no do_task changes |
| `astral.agent.grade-vector-validation` | scoped | conforms | no grade-vector changes |
| `astral.batch.batch-id-first` | scoped | conforms | no batch claim work |
| `astral.batch.batch-id-format` | scoped | conforms | untouched |
| `astral.batch.claim-process-release` | scoped | conforms | untouched |
| `astral.batch.entity-agent-responses-latest-only` | scoped | conforms | untouched |
| `astral.config.config-source-of-truth` | scoped | conforms | literal/path/policies via get_cover_letter_render_token only |
| `astral.config.pass-threshold-vs-score-floor` | scoped | conforms | thresholds untouched |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | conforms | no secrets/env keys |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | paths miss vs core+utils+docs diff |
| `astral.debug.spikes-under-debug-dir` | scoped | conforms | feature docs under docs/features/artifacts/; not spikes |
| `astral.dispatch.run-next-is-chain-authority` | scoped | conforms | no run_next edits |
| `astral.dispatch.seed-auto-false` | scoped | conforms | no seed/dispatch_task edits |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | one ast-1126 features file (+ sibling 1125 on tip) |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty owns tests/bible; engineer owns builder+plan |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | Hedy code() touched builder.py (+docs stub); Betty owns tests |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | core emit; no external I/O added |
| `astral.layers.import-direction` | scoped | conforms | core → utils accessor; no layer inversion |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | layers+paths miss vs core+utils+docs diff |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | no React rules; emit consumes config |
| `astral.patterns.coat-check-never-store-empty` | scoped | conforms | not coat-check work |
| `astral.patterns.render-verdict-orchestrates-consult` | scoped | conforms | not consult work |
| `astral.patterns.require-auth-on-protected-endpoints` | scoped | not-applicable | layers+paths miss vs core+utils+docs diff |
| `astral.seed.agent-tables-in-repo-json` | scoped | conforms | no seed JSON |
| `astral.seed.archie-catalog-wins` | scoped | conforms | no catalog edits |
| `astral.seed.boot-only-not-hot-path` | scoped | conforms | not seed/boot |
| `astral.seed.define-approved` | scoped | conforms | not seed work |
| `astral.seed.operator-rows-stay-deleted` | scoped | conforms | not seed/dispatch |
| `astral.seed.other-via-coverage-join` | scoped | conforms | not seed work |
| `astral.standards.data-raises-caller-logs` | scoped | conforms | no data-layer write/log changes |
| `astral.standards.database-header-inventory` | scoped | not-applicable | layers+paths miss vs core+utils+docs diff |
| `astral.standards.debug-contract-gated` | scoped | conforms | Style D token/image details only under debug=True |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | shared helpers + reuse _safe_image_src |
| `astral.standards.in-scope-only` | scoped | conforms | job+session cover emit only; resume/profile untouched |
| `astral.standards.logging-via-utils` | scoped | conforms | uses existing _log debug helpers |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | helpers/debug keys use domain names |
| `astral.standards.no-cross-contamination` | scoped | conforms | resume builders do not call cover render-token helpers |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | literal/path from accessor; no parallel hardcoded set |
| `astral.standards.public-then-helpers` | scoped | conforms | private helpers colocated near _safe_image_src |
| `astral.standards.utils-data-late-import-only` | scoped | conforms | no new utils→data import |
| `astral.state.core-decides-transitions` | scoped | conforms | no state transitions |
| `astral.state.job-prior-states-enforced` | scoped | conforms | JOB_STATES untouched |
| `astral.state.no-daisy-chain-in-run` | scoped | conforms | untouched |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | layers+paths miss vs core+utils+docs diff |
| `astral.ui.naming-conventions` | scoped | not-applicable | layers+paths miss vs core+utils+docs diff |
| `astral.ui.single-gunicorn-worker` | scoped | conforms | no worker/RAILWAY_CONFIG changes |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | one merge-tests(AST-1126) SHA |
| `orch.git.commit-vocabulary` | universal | conforms | plan/code/docs/test/merge-tests vocabulary |
| `orch.git.flow-direction-inviolable` | universal | conforms | publish on origin/sub/AST-1123/AST-1126-… |
| `orch.git.ftr-sub-topology` | universal | conforms | matches parent Git table |
| `orch.git.merge-on-checkout` | universal | conforms | merge-resume(AST-1126) origin/dev present |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | no force/rebase/cherry-pick |
| `orch.git.no-dev-agent-branches` | universal | conforms | sub/ topology only |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | epic worktree astral-AST-1123 |
| `orch.git.three-permanent-branches` | universal | conforms | no new permanent branches |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | non-omit policy raises; no improvised product rule |
| `orch.pipeline.plan-is-bible` | universal | conforms | Stages 1–2 match plan helpers + stop auto-above |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Artifacts child scope |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Tests Passed → review-child |
| `orch.roles.archie-approves-statutes` | universal | conforms | no statute corpus edits |
| `orch.roles.betty-owns-test-tree` | universal | conforms | Betty test()+merge-tests own tests/bible |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | assignee remains Hedy |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Hedy stays assignee through Tests Passed |
| `orch.roles.pre-commit-path-bans` | universal | conforms | no banned path smuggling in code() |

## Pattern conformance

- `pattern.layers.import-discipline` — **conforms** (core → `get_cover_letter_render_token`; no ui/external added)
- `pattern.config.config-block` — **not-cited for this ticket** (AST-1125 owns registration; emit consumes accessor)

## Plan adherence

Stages 1–2 match the plan: shared helpers beside `_safe_image_src`; job signoff stops auto-prepend and uses Joan’s concrete `<p>before</p>{img}<p>after</p>` shape; session stops auto-inject, resolves image via `tok["path"]` on full candidate blob, replaces via `_html_with_signature_image_token`; Style D details gated on existing `debug=True` success paths. Surfaces + omit-policy guards raise instead of improvising. Resume builders untouched. Self-Assessment Single-Component / Conf high / Risk Medium matches the builder-only footprint (session contact-path switch noted).

## Findings

**discuss (C4 straggler):** Joan excluded at plan time (Files Changed = core): `astral.debug.spikes-under-debug-dir`, `astral.dispatch.seed-auto-false`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, `astral.layers.ui-config-driven-business-logic`, `astral.seed.agent-tables-in-repo-json`, `astral.seed.archie-catalog-wins`, `astral.seed.operator-rows-stay-deleted`, `astral.seed.other-via-coverage-join`, `astral.standards.utils-data-late-import-only`, `astral.ui.single-gunicorn-worker`. Code-time three-dot includes plan docs, Betty tests, and AST-1125 `config.py` on tip — those statutes score in-scope and **conform**. No product action.

No **fix-now**. Debug contract (§5f) satisfied on touched cover paths. External cleanliness (§5g) N/A.

## What’s solid

- Token-only placement; no image when token absent even if a valid src exists.
- Shared resolve helper + reused `_safe_image_src`; no second validator.
- One `merge-tests(AST-1126)`; Hedy assignee retained.

## Notes

- Joan plan-rubric APPROVED; prior non-blocking HTML-shape discuss is implemented in `_emit_cover_signoff_html`.
- Three-dot includes AST-1125 contract files (expected blocker land) — not AST-1126 scope creep.

## Recommended actions

- Hedy / resolve-child: acknowledge C4 stragglers; no product patch → User Testing.

context_tokens≈48000

#### betty — 2026-08-02T18:12:44.558Z
**QA test manifest — AST-1126**

`origin/sub/AST-1123/AST-1126-cover-html-emit-token-replace-stop-auto-above` @ `6570adbd` (`merge-tests(AST-1126): origin/tests f50640e6b086f097d0f5f8b7a7cd50d05736aae2`)

**Classification**
1. **Gaps (new):** `TestAst1126CoverSignatureImageToken` — job signoff image between closing and name; no img without token; omit literal on rejected image; token/image status matrix; job debug `signature_image_token=` / `signature_image=`; resume HTML does not resolve token as image.
2. **Broken / obsolete (revised):** `TestBuilderHelpers::test_emits_cover_signoff_and_ats_tokens` (image-only no longer creates signoff); `TestAst1024BuildSessionCoverLetter` image cases (token-gated + `contact.cover_letter_signature_image`, no auto-inject).
3. **Existing coverage (re-run):** `TestBuildCoverLetterFromJobDebugPaths` (debug paths still green after Style D detail rename).
4. **Integration:** none.

**Run (test-child):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_builder.py::TestAst1126CoverSignatureImageToken \
  tests/component/core/test_builder.py::TestAst1024BuildSessionCoverLetter \
  tests/component/core/test_builder.py::TestBuilderHelpers::test_emits_cover_signoff_and_ats_tokens \
  tests/component/core/test_builder.py::TestBuildCoverLetterFromJobDebugPaths \
  -q
```

**Bible (publish tip):**
`docs/test-bible/core/builder.md` shasum `b80d191ce7ad439e4c951ff0998a6fe6d9d228f2`

— Betty

#### joan — 2026-08-02T18:05:37.819Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1126
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 image between closing and name/title | Stage 1 job signoff rewrite + Stage 2 session fragment (token position) |
| AC2 literal absent when valid image available | Stages 1–2 `_html_with_signature_image_token` replace-all with img |
| AC3 no img / no broken placeholder when unusable | Stages 1–2 omit literal when no `safe_src`; reuse `_safe_image_src` |
| AC4 stop unconditional prepend above signature | Stage 1 delete auto-prepend; Stage 2 delete auto-inject |
| AC5 resume paths do not resolve token as image | Out-of-scope table — resume builders not edited |
| AC6 Style D debug token + image status | Stages 1.5 + 2.4 `signature_image_token` + three-way `signature_image` |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 shared helpers + job cover signoff | Purpose token placement; Functional scope 1–5; child #2 job path |
| Stage 2 session cover stop-inject + token + debug | Functional scope 1–5 + OQ2 session; child #2 session path |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work |
| orch.git.commit-vocabulary | conforms | Publish on sub; build uses plan()/code() |
| orch.git.flow-direction-inviolable | conforms | origin/sub/AST-1123/AST-1126-… only |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | No illegal merge recipe |
| orch.git.no-cherry-pick-rebase-force | conforms | Not proposed |
| orch.git.no-dev-agent-branches | conforms | sub/ topology only |
| orch.git.one-epic-worktree-per-parent | conforms | astral-AST-1123 |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | OQ1/OQ2 encoded as omit; stop+parent if policy ≠ omit |
| orch.pipeline.plan-is-bible | conforms | Binding Files Changed + staged steps |
| orch.pipeline.project-scoped-queues | conforms | Single-child Artifacts scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate-plan only |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | tests/ excluded |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Hedy) owns build |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer path after approve |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | No graded-task changes |
| astral.agent.do-task-delegation | conforms | No do_task / agent changes |
| astral.agent.grade-vector-validation | conforms | Untouched |
| astral.batch.batch-id-first | conforms | No batch claim work |
| astral.batch.batch-id-format | conforms | Untouched |
| astral.batch.claim-process-release | conforms | Untouched |
| astral.batch.entity-agent-responses-latest-only | conforms | Untouched |
| astral.config.config-source-of-truth | conforms | Literal/path/policies via get_cover_letter_render_token only |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env |
| astral.dispatch.run-next-is-chain-authority | conforms | No dispatch edits |
| astral.git.betty-no-src-or-features | conforms | Engineer owns builder.py |
| astral.layers.core-vs-external-bright-line | conforms | Core emit only; no external I/O added |
| astral.layers.import-direction | conforms | core → utils accessor; no ui/data/external |
| astral.patterns.coat-check-never-store-empty | conforms | Not coat-check work |
| astral.patterns.render-verdict-orchestrates-consult | conforms | Not consult work |
| astral.seed.boot-only-not-hot-path | conforms | Not seed work |
| astral.seed.define-approved | conforms | Not seed work |
| astral.standards.data-raises-caller-logs | conforms | No data-layer writes |
| astral.standards.debug-contract-gated | conforms | Detail lines only under existing debug=True gates |
| astral.standards.dry-and-focused-functions | conforms | Reuse _safe_image_src; shared helpers job+session |
| astral.standards.in-scope-only | conforms | Cover job+session emit only; resume/profile/config out |
| astral.standards.logging-via-utils | conforms | Uses existing _log debug helpers |
| astral.standards.names-not-ticket-ids | conforms | Helper/debug keys use domain names |
| astral.standards.no-cross-contamination | conforms | Resume paths do-not-touch; surfaces gate before emit |
| astral.standards.no-hardcoded-sets | conforms | No parallel {$SIGNATURE_IMAGE} set; config accessor only |
| astral.standards.public-then-helpers | conforms | Private helpers near _safe_image_src |
| astral.state.core-decides-transitions | conforms | No state transitions |
| astral.state.job-prior-states-enforced | conforms | Untouched |
| astral.state.no-daisy-chain-in-run | conforms | Untouched |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.dispatch.run-next-is-chain-authority, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.seed.boot-only-not-hot-path, astral.seed.define-approved, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.names-not-ticket-ids, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths match none of plan paths
- astral.debug.spikes-under-debug-dir — paths match none of plan paths
- astral.dispatch.seed-auto-false — paths match none of plan paths
- astral.docs.features-single-file-per-ticket — layers {docs} ∩ plan {core} empty
- astral.git.engineer-test-tree-ban — paths match none of plan paths
- astral.layers.scripts-exempt-from-layer-rules — layers ∩ plan {core} empty
- astral.layers.ui-config-driven-business-logic — layers ∩ plan {core} empty
- astral.patterns.require-auth-on-protected-endpoints — layers ∩ plan {core} empty
- astral.seed.agent-tables-in-repo-json — paths match none of plan paths
- astral.seed.archie-catalog-wins — paths match none of plan paths
- astral.seed.operator-rows-stay-deleted — paths match none of plan paths
- astral.seed.other-via-coverage-join — paths match none of plan paths
- astral.standards.database-header-inventory — layers ∩ plan {core} empty
- astral.standards.utils-data-late-import-only — layers ∩ plan {core} empty
- astral.ui.frontend-file-placement — layers ∩ plan {core} empty
- astral.ui.naming-conventions — layers ∩ plan {core} empty
- astral.ui.single-gunicorn-worker — layers ∩ plan {core} empty

## Findings

None fix-now.

**discuss (non-blocking):** Stage 1 step 4 narrates several HTML wrapper options before settling on the `<p>before</p>{img}<p>after</p>` exact shape for present+safe. Engineer should implement that concrete rule (and the omit/absent variants stated immediately after), not invent a third wrapper. Multi-literal signatures are edge-case only.

**acceptable:** Self-assessment Single-Component / Conf high / Risk Medium is honest (session contact-path switch + omit/replace visibility). Surfaces gate + stop-on-non-omit policy are good execution brakes. Resume non-touch satisfies AC5 by isolation.

**R6:** Definition fidelity pass (child #2 emit). Config consumed not authored. Layer core→utils pass. DRY via shared helpers + `_safe_image_src`. No profile UI / TOKEN_SOURCES / resume creep.

context_tokens≈42000

— Joan

#### hedy — 2026-08-02T18:03:54.706Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-1123/AST-1126-cover-html-emit-token-replace-stop-auto-above/docs/features/artifacts/ast-1126-cover-html-emit-token-replace-stop-auto-above.md

**Scope — Single-Component:** `src/core/builder.py` only — shared token helpers, job `_emit_cover_signoff_html` stop-prepend + token replace, session stop-auto-inject + token replace, Style D debug on both cover success paths.

**Conf — high:** AST-1125 contract + integration note define the algorithm; auto-above/auto-inject call sites are already localized; reuse `_safe_image_src`.

**Risk — Medium:** omit/replace mistakes show in print HTML; session switches image read from legacy `profile` to `contact.cover_letter_signature_image` per `tok["path"]`.

— Hedy

#### chuckles — 2026-08-02T17:58:55.676Z
[thread-missing] Hedy Team thread `1d68e436-64e5-4b76-8275-2bed4edff2c5` store.db nowhere on host; minted `a6352234-7f4f-4839-9ec1-ccfcc027d135` → `/home/susan/.cursor/chats/c949585722c8f009c0bb68bfaec8882f/a6352234-7f4f-4839-9ec1-ccfcc027d135/store.db`.

— Chuckles

---

# AST-1126 — Cover HTML emit — token replace and stop auto-above

**Linear:** [AST-1126](https://linear.app/astralcareermatch/issue/AST-1126/cover-html-emit-token-replace-and-stop-auto-above-support-signature)  
**Parent:** [AST-1123](https://linear.app/astralcareermatch/issue/AST-1123/support-signature-image-as-a-token-in-the-cover-letter) — Support Signature_Image as a token in the cover letter  
**Publish ref:** `origin/sub/AST-1123/AST-1126-cover-html-emit-token-replace-stop-auto-above`  
**Blocked by (done):** [AST-1125](https://linear.app/astralcareermatch/issue/AST-1125/cover-letter-signature-image-token-contract-support-signature-image-as) — config contract already on `ftr` / this sub tip

After AST-1125’s `BUILD_CONFIG["cover_letter_render_tokens"]["SIGNATURE_IMAGE"]` contract: job and session cover HTML emit stop unconditional signature-image placement; replace `{$SIGNATURE_IMAGE}` at the token position only (safe `<img>` via existing `_safe_image_src`); if the token is absent, omit the image (no fallback insert); Style D debug on touched cover paths reports token presence and image accepted / absent / rejected. Does **not** own profile upload UI, resume emit, or the config contract.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/builder.py` | Shared SIGNATURE_IMAGE resolve/replace helpers; rewrite job `_emit_cover_signoff_html` (stop auto-prepend); rewrite session signoff emit (stop auto-inject); Style D debug lines on job + session cover success paths; import `get_cover_letter_render_token` | core |

**Out of scope (do not touch):**

| Item | Owner / reason |
|------|----------------|
| `BUILD_CONFIG["cover_letter_render_tokens"]` / `get_cover_letter_render_token` | AST-1125 (already shipped) |
| Resume base / job / session HTML emit (`build_base_resume`, `build_resume*`, `build_session_base_resume`, resume branches of `_emit_html_document`) | excluded — must not resolve `{$SIGNATURE_IMAGE}` |
| Candidate Profile upload/validation (`api_candidate`, UI signature_image field) | excluded |
| `TOKEN_SOURCES` / `resolve_tokens` | excluded — binary image must not enter LLM prompts |
| Admin React Session Cover Letter page | AST-1025 — no UI change; API continues to pass `signature` text (may now contain the literal) |
| `tests/` / `docs/test-bible/**` | Betty |

## Stage 1: Shared token helpers + job cover signoff

**Done when:** Job cover HTML from `build_cover_letter` / `build_cover_letter_from_job` never prepends a signature `<img>` above the signature text; when `cover["signature"]` contains `tok["literal"]` and the image at `tok["path"]` passes `_safe_image_src`, the `<img>` appears at the token position inside the signoff; when the token is absent, no signature image is emitted even if a valid image exists; when the token is present but image missing/rejected, the literal is removed and no broken `<img>` is emitted; `debug=True` on `build_cover_letter_from_job` logs token + three-way image status; `python3 -m py_compile src/core/builder.py` passes.

1. In `src/core/builder.py`, update the config import to include `get_cover_letter_render_token`:
   ```python
   from src.utils.config import (
       BUILD_CONFIG,
       RESUME_STRUCTURE_CONTACT_SECTION_IDS,
       get_cover_letter_render_token,
   )
   ```

2. Add two private helpers near `_safe_image_src` (before `_emit_cover_signoff_html`):

   ```python
   def _lookup_dotted_path(root: Any, dotted: str) -> Any:
       """Walk ``a.b.c`` on nested dicts; return ``None`` if any segment missing/non-dict."""
       cur: Any = root
       for part in (dotted or "").split("."):
           if not part or not isinstance(cur, dict):
               return None
           cur = cur.get(part)
       return cur


   def _signature_image_token_status(
       signature_text: str,
       candidate_root: dict,
   ) -> tuple[str, Optional[str], str]:
       """Return ``(token_status, safe_src_or_None, image_status)``.

       ``token_status``: ``present`` | ``absent``
       ``image_status``: ``accepted`` | ``absent`` | ``rejected``
         - ``absent``: path value missing / empty / non-string
         - ``rejected``: non-empty raw failed ``_safe_image_src``
         - ``accepted``: ``_safe_image_src`` returned a usable src
       """
       tok = get_cover_letter_render_token("SIGNATURE_IMAGE")
       literal = tok["literal"]
       token_status = "present" if literal in (signature_text or "") else "absent"
       raw = _lookup_dotted_path(candidate_root, tok["path"])
       if not isinstance(raw, str) or not raw.strip():
           return token_status, None, "absent"
       safe = _safe_image_src(raw)
       if safe is None:
           return token_status, None, "rejected"
       return token_status, safe, "accepted"
   ```

3. Add a private HTML fragment builder that applies AST-1125 policies (do **not** hardcode the literal — always `tok["literal"]`):

   ```python
   def _html_with_signature_image_token(
       signature_text: str,
       *,
       safe_src: Optional[str],
       token_status: str,
       img_html: str,
   ) -> str:
       """Escape signature text; replace or omit ``SIGNATURE_IMAGE`` literal per contract.

       - token absent → escape full text only (caller must not inject ``img_html``).
       - token present + ``safe_src`` → escape segments around literal; insert ``img_html`` once
         at the first occurrence (replace that occurrence; if literal appears more than once,
         replace **all** occurrences with the same ``img_html`` / empty per policy — no leftover
         literal text).
       - token present + no ``safe_src`` → omit literal (empty string at each occurrence).
       Newlines in text segments stay as escaped text (same as today's single-``<p>`` job path);
       do not invent new ``<br>`` rules on this ticket.
       """
   ```

   Implementation requirements for step 3:
   - Load `tok = get_cover_letter_render_token("SIGNATURE_IMAGE")` and use `tok["literal"]` only.
   - If `token_status == "absent"`: return `html.escape(signature_text or "")`.
   - If `token_status == "present"`: `parts = (signature_text or "").split(tok["literal"])`; join `html.escape(part)` with separator `img_html if safe_src else ""`.
   - Honor `tok["absent_token_policy"]` / `tok["missing_or_rejected_image_policy"]` as already set to `"omit"` — do not invent a fallback insert path. If either policy key is ever not `"omit"`, **stop and comment on the parent** (do not improvise).

4. Rewrite `_emit_cover_signoff_html(cover: dict, profile: dict) -> str`:
   - Treat `profile` as today’s **contact** dict (call sites already pass `cd.get("contact")`). Build `candidate_root = {"contact": profile or {}}` so `tok["path"]` (`contact.cover_letter_signature_image`) resolves.
   - `sig = (cover.get("signature") or "")` — keep raw (including whitespace) for token search; strip only when deciding emptiness for the early return.
   - `token_status, safe_src, _image_status = _signature_image_token_status(sig, candidate_root)`.
   - **Stop** the current unconditional prepend:
     ```python
     # DELETE this shape:
     if safe_src:
         inner_lines.append('<img ...>')
     if sig:
         inner_lines.append(f'<p>{html.escape(sig)}</p>')
     ```
   - Replacement shape:
     - If `not (sig or "").strip()` and token absent: return `""` (same empty-signoff behavior as today when no text and no image — but image alone must **not** create a signoff).
     - If signature text is non-empty (or was only the token): build
       `img_html = f'<img src="{html.escape(safe_src, quote=True)}" alt="Cover letter signature" style="max-width:240px;height:auto;" />'` when `safe_src` else `""`.
       - `body = _html_with_signature_image_token(sig, safe_src=safe_src, token_status=token_status, img_html=img_html)`.
       - If `body` is empty after omit: return `""`.
       - Else emit the existing section wrapper with **one** inner `<p>{body}</p>` when the result has no raw `<img>`, **or** when it contains an `<img>`, emit the section with the fragment directly inside the section (img + escaped text) **without** wrapping the `<img>` in a way that re-escapes it. Concrete rule: if `safe_src` and `token_status == "present"`, use:
         ```html
         <section class="cover-block cover-signoff" aria-label="Cover sign-off">
         {fragment}
         </section>
         ```
         where `fragment` is the joined escaped-parts + img (no extra outer `<p>` around the img). If there is escaped text before/after the img, keep those text nodes as `<p>…</p>` **or** plain escaped text separated by the img — pick **this exact shape** to match visual order closing→image→name when the signature string is e.g. `Sincerely,\n\n{$SIGNATURE_IMAGE}\nJane Doe\nTitle`:
         ```html
         <section class="cover-block cover-signoff" aria-label="Cover sign-off">
               <p>{escaped_before}</p>
               {img_html}
               <p>{escaped_after}</p>
         </section>
         ```
         Omit empty `<p></p>` nodes when a side is empty/whitespace-only after strip. When token absent: single `<p>{escaped full signature}</p>` as today (no img). When token present and image omitted: single `<p>` with literal removed (join escaped parts with `""`), or two `<p>`s only if you split on the literal and both sides are non-empty — prefer **one** `<p>` with concatenated escaped parts when `safe_src` is None.
   - Do **not** change `_emit_cover_sections_html` beyond what `_emit_cover_signoff_html` already feeds.
   - Do **not** touch resume emit branches.

5. Update `build_cover_letter_from_job` debug block (`debug=True` success path only):
   - After HTML is built, compute status from the same cover signature + contact:
     ```python
     contact = cd.get("contact") or {}
     cover_sig = (cover.get("signature") or "")
     token_status, _safe, image_status = _signature_image_token_status(
         cover_sig, {"contact": contact}
     )
     ```
   - Keep existing `debug_index` header.
   - Replace the current single `signature_image=accepted|absent_or_rejected` detail with:
     ```python
     _log.debug_detail(f"signature_image_token={token_status}")
     _log.debug_detail(f"signature_image={image_status}")
     ```
   - Keep `cover_source`, fields nonempty, `html_chars`, and `html_preview` details as they are today.

⚠️ **Decision:** Job signoff keeps existing img attributes (`alt="Cover letter signature"`, inline max-width style). Session keeps its own `class="signature-img"` markup in Stage 2 — do not unify CSS across the two DOM families.

⚠️ **Decision:** Image alone (valid src, no signature text, no token) must not emit a signoff section. Parent OQ1/OQ2: image only where the token resolves.

## Stage 2: Session cover — stop auto-inject + token replace + debug

**Done when:** `build_session_cover_letter` no longer inserts a signature `<img>` between `signoff_closing` and `signature` unless `fields["signature"]` contains the config literal; image bytes are read from `contact.cover_letter_signature_image` via `tok["path"]` (not `profile`); `debug=True` reports `signature_image_token` + three-way `signature_image`; resume builders unchanged; `python3 -m py_compile src/core/builder.py` passes.

1. In `build_session_cover_letter`, replace the profile-based image read:
   ```python
   # DELETE / replace:
   profile = _coerce_candidate_blob(row).get("profile") or {}
   sig_src = _safe_image_src(profile.get("cover_letter_signature_image"))
   ```
   With:
   - `cd = _coerce_candidate_blob(row)`.
   - `token_status, sig_src, image_status = _signature_image_token_status(
         fields.get("signature") or "", cd
     )` — note full candidate blob so `tok["path"]` (`contact.cover_letter_signature_image`) resolves after AST-1014 contact migration.
   - Keep `sig_image_status` variable name only if useful; prefer storing `token_status` and `image_status` for debug. When `candidate_id` is empty: `token_status, sig_src, image_status` from the signature text against `candidate_root={}` (image will be `absent`; token may still be `present` → omit literal / no img).

2. Change the call to `_emit_session_cover_html_document` so the emitter receives enough to apply token policy — either:
   - **Preferred:** pass `signature_image_src=sig_src` **and** let the emitter read token presence from `fields["signature"]`, **or**
   - Pass `token_status` as an extra kw-only arg.
   - Do **not** keep today’s behavior of “if `signature_image_src`: always inject between closing and name”.

3. Rewrite the signoff assembly inside `_emit_session_cover_html_document`:
   - Keep `signoff_closing` escaped + `<br>` as today.
   - **Delete** the unconditional block:
     ```python
     if signature_image_src:
         signoff_parts.append('<img ...>')
         signoff_parts.append("<br>")
     signoff_parts.append(html.escape(sig_name))
     ```
   - Replacement:
     - `tok = get_cover_letter_render_token("SIGNATURE_IMAGE")`.
     - `raw_sig = fields.get("signature") or ""`.
     - `token_status = "present" if tok["literal"] in raw_sig else "absent"`.
     - `img_html = f'<img src="{html.escape(signature_image_src, quote=True)}" class="signature-img" alt="Signature">'` when `signature_image_src` and `token_status == "present"`, else `""`.
     - Build signature fragment via `_html_with_signature_image_token(raw_sig, safe_src=signature_image_src, token_status=token_status, img_html=img_html)`.
     - Append that fragment to `signoff_parts` (session historically appends the name as a text node after `<br>` — keep closing + `<br>` + fragment; if fragment contains an `<img>`, do not wrap the whole fragment in `html.escape`).
     - If after omit the signature fragment is empty, still emit closing (required field) — do not invent a placeholder image.

4. Update session `debug=True` success details:
   - Replace `signature_image={sig_image_status}` with:
     ```python
     _log.debug_detail(f"signature_image_token={token_status}")
     _log.debug_detail(f"signature_image={image_status}")
     ```
   - When no `candidate_id`, `image_status` is `absent` (unless you only looked at token — still `absent` for image). Keep other existing detail lines (`to_block`, `subject`, `candidate_id`, `html_chars`, preview).

5. Confirm `"cover_letter" in get_cover_letter_render_token("SIGNATURE_IMAGE")["surfaces"]` before emitting a replacement on both job and session paths. If missing, **stop and comment on the parent** — do not emit the image.

6. Do **not** edit `src/ui/api/api_admin.py`, resume builders, or `src/utils/config.py` on this ticket.

⚠️ **Decision:** Session signature field is the token host (e.g. `{$SIGNATURE_IMAGE}\nSusan Somerset`). `signoff_closing` stays closing-only. That matches parent “token in cover letter signature content” and AST-1024’s `signature` ↔ artifact `signature` spine without a new field.

⚠️ **Decision:** Switch session image source from legacy `profile.cover_letter_signature_image` to `tok["path"]` (`contact.cover_letter_signature_image`). Required by AST-1125; profile path would silently omit images after contact migration.

## Self-Assessment

**Scope — `Single-Component`**  
One core module (`builder.py`) on cover emit helpers and two cover entrypoints’ debug lines; no utils/ui/resume edits.

**Conf — `high`**  
AST-1125 contract + integration note spell the algorithm; job and session currently show the exact auto-above/auto-inject code to delete; `_safe_image_src` is reused.

**Risk — `Medium`**  
Wrong omit/replace would hide signatures or leave literals in print HTML; session contact-path switch could blank images if a row still only had profile-era data — mitigated by AST-1014 contact ownership and AC coverage in Betty’s pass.

## Self-review vs ASTRAL_CODE_RULES

| Rule | Check |
|------|--------|
| `astral.standards.in-scope-only` | Cover job + session emit only; resume/profile/config contract excluded. |
| `astral.standards.no-cross-contamination` | Resume emit paths listed do-not-touch; no `cover_letter_render_tokens` import on resume builders. |
| `astral.standards.debug-contract-gated` | New/changed detail lines only under existing `debug=True` gates; Style D index headers already present — extend details only. |
| `astral.layers.import-direction` / `pattern.layers.import-discipline` | core → utils accessor only; no ui/external imports added. |
| `astral.standards.dry-and-focused-functions` | Reuse `_safe_image_src`; shared token helpers; no second validator. |
| `astral.config.config-source-of-truth` / `astral.standards.no-hardcoded-sets` | Literal + path + policies from `get_cover_letter_render_token` only. |
| §1.3 DRY | One replace helper shared by job + session. |

## Review (stub — build-child)

| Field | Value |
|-------|-------|
| Branch | `sub/AST-1123/AST-1126-cover-html-emit-token-replace-stop-auto-above` |
| Tip | `33d143fd` |
| Notes | Job + session cover emit: token-only `{$SIGNATURE_IMAGE}` replace via `get_cover_letter_render_token`; stop auto-prepend/inject; Style D `signature_image_token` + three-way `signature_image`. |

## Radia review — code-rubric.v1

`[code-rubric] revision=1`  
**Overall:** DISCUSS (C4 stragglers only — no product fix-now)  
**Publish tip reviewed:** `6570adbd` product/tests tip + this docs append  
**Baseline:** `origin/dev`

### What’s solid

- Stages 1–2 match: shared `_lookup_dotted_path` / `_signature_image_token_status` / `_html_with_signature_image_token`; job `_emit_cover_signoff_html` uses concrete `<p>before</p>{img}<p>after</p>`; session stops auto-inject and replaces via token helper.
- Image source via `tok["path"]` (`contact.…`); surfaces + omit-policy guards raise instead of improvising.
- Style D: `signature_image_token` + three-way `signature_image` only under existing `debug=True` gates on job + session cover success paths.
- Resume builders do not call cover render-token helpers. One `merge-tests(AST-1126)`.

### Findings

**discuss (C4 straggler):** Joan excluded several statutes at plan time (Files Changed = core only). Code-time three-dot diff includes plan docs, Betty test tree, and AST-1125 `config.py` on the tip, so those statutes score in-scope and **conform**. No product action — acknowledge and continue.

### Recommended actions

- Hedy: no `fix-now` product work. On resolve-child, acknowledge C4 stragglers → User Testing.

## Resolution

**Date:** 2026-08-02  
**Engineer:** Hedy  
**Publish tip:** `0364b533` → resolve commit on `origin/sub/AST-1123/AST-1126-cover-html-emit-token-replace-stop-auto-above`

### Radia findings

| Finding | Action |
|---------|--------|
| **fix-now** | None |
| **discuss (C4 stragglers)** | Acknowledged — plan-time excludes that scored in-scope at code-time all **conform**; no product patch |
| Joan HTML-shape discuss (plan-time) | Already implemented in `_emit_cover_signoff_html` (`<p>before</p>{img}<p>after</p>`) |

### Outcome

No product changes on resolve. Tip advances with this Resolution append only → **User Testing**.
