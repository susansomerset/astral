<!-- linear-archive: AST-1024 archived 2026-08-05 -->

## Linear archive (AST-1024)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1024/session-cover-letter-html-builder-admin-html-api-session-cover-letter  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1023 — Session Cover Letter  
**Blocked by / blocks / related:** parent: AST-1023; blocks: AST-1025

### Description

## What this implements

Core session cover emit from in-memory field payload (no job load; no artifact persist) producing golden SomersetCover HTML; Admin `POST` HTML route under existing admin auth. Optional signature-image read from the **selected** candidate profile when present — otherwise name-only sign-off. Owns debug contract on touched backend paths. Does **not** own Admin React page or localStorage. After this child unblocks the Admin Session Cover Letter page sibling.

## Citations

`pattern.ui.admin-endpoint`, `pattern.layers.import-discipline`, `astral.standards.debug-contract-gated`, `astral.patterns.require-auth-on-protected-endpoints`, `astral.standards.in-scope-only`

## Acceptance criteria

1. From in-memory session field payload, Admin can obtain styled cover-letter HTML consistent with the Original-brief SomersetCover layout (from block, date, letter body, sign-off).
2. Render succeeds without a job id; letter fields come from the request body. With no candidate selected, HTML still renders (name-only sign-off). With a selected candidate that has a profile signature image, that image appears in the sign-off.
3. No server-generated PDF file is required (HTML for Print → PDF).
4. Failed validation/render returns a clear error (no success HTML).
5. When `debug=True` on touched backend cover emit/API paths, logs show Style D per-index headers and `|` working detail for what was found/recorded (not counts-only).

## Boundaries

Does **not** own Admin React page, localStorage, or session retention. Does **not** upgrade job `build_cover_letter` / materials cover tabs. Does **not** write candidate or job artifacts. Does **not** change Manage Tasks / dispatch chains.

## Notes for planning

Fields-only (no LLM parse). Session-only golden cover CSS/DOM. Optional selected-candidate signature image read only.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/ast-1023-session-cover-letter`, child `sub/AST-1023/AST-1024-session-cover-letter-html-builder-admin-html-api`. Created at dispatch-parent.

### Comments

#### radia — 2026-07-29T03:34:10.245Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1024
**Publish ref:** `origin/sub/AST-1023/AST-1024-session-cover-letter-html-builder-admin-html-api` @ `d5813c67` (product tip reviewed `053830d3`; this SHA is docs-only)
**Overall:** DISCUSS

**Diff:** `origin/dev...origin/sub/AST-1023/AST-1024-session-cover-letter-html-builder-admin-html-api`
**Layers:** core, ui, utils, docs (+ Betty tests/bible)
**Notes:** Joan plan-rubric APPROVED attached. C4 stragglers below (Excluded at plan time; in-scope on code diff). No product fix-now.

## Statutes checked

| id | tier | verdict | one-line |
| -- | -- | -- | -- |
| astral.agent.confidence-bounds | scoped | conforms | No confidence / agent scoring touched |
| astral.agent.do-task-delegation | scoped | conforms | No do_task / LLM parse; fields-only emit |
| astral.agent.grade-vector-validation | scoped | conforms | Untouched |
| astral.batch.batch-id-first | scoped | conforms | Untouched |
| astral.batch.batch-id-format | scoped | conforms | Untouched |
| astral.batch.claim-process-release | scoped | conforms | Untouched |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | Untouched |
| astral.config.config-source-of-truth | scoped | conforms | Field keys from `BUILD_CONFIG["session_cover_letter"]["fields"]` |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No secrets/env additions |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | No repo-root `artifacts/**` or `scripts/spikes/**` |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Plan under `docs/features/` — not a misplaced spike (C4 straggler) |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Single `ast-1024-…` features file (C4 straggler) |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty `test`/`merge-tests` only bible+tests; src/features from engineer/docs |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer `code()` = src only; tests/bible via Betty (C4 straggler) |
| astral.layers.core-vs-external-bright-line | scoped | conforms | Emit in core; no external LLM layer |
| astral.layers.import-direction | scoped | conforms | ui → core + utils; core candidate read for optional image |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers/paths miss — no `scripts/**` |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | API maps keys from config; validation in core |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | Untouched |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | Untouched |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | `@require_admin` on new Admin POST |
| astral.standards.data-raises-caller-logs | scoped | conforms | Core `ValueError`; UI JSON 400 |
| astral.standards.database-header-inventory | scoped | not-applicable | layers/paths miss — no `src/data/**` |
| astral.standards.debug-contract-gated | scoped | conforms | Style D only when `debug=True` / `ui_llm_debug()` |
| astral.standards.dry-and-focused-functions | scoped | conforms | Session emit helpers; no duplicate field-key list |
| astral.standards.in-scope-only | scoped | conforms | No React/nav, job cover, or artifact writes |
| astral.standards.logging-via-utils | scoped | conforms | Builder `_log` Style D helpers; no `print`/`logging` |
| astral.standards.no-cross-contamination | scoped | conforms | No job load / no `save_*` / no job cover emit |
| astral.standards.no-hardcoded-sets | scoped | conforms | Session field set owned by config |
| astral.standards.public-then-helpers | scoped | conforms | Public `build_session_cover_letter` then private helpers |
| astral.standards.utils-data-late-import-only | scoped | conforms | `config.py` add only — no utils→data |
| astral.state.core-decides-transitions | scoped | conforms | Untouched |
| astral.state.job-prior-states-enforced | scoped | conforms | Untouched |
| astral.state.no-daisy-chain-in-run | scoped | conforms | Untouched |
| astral.ui.frontend-file-placement | scoped | not-applicable | paths miss — no `src/ui/frontend/**` |
| astral.ui.naming-conventions | scoped | conforms | snake_case `/session_cover_letter/html` |
| astral.ui.single-gunicorn-worker | scoped | conforms | Untouched |
| orch.git.betty-merge-tests-one-sha | universal | conforms | Single `merge-tests(AST-1024)` @ `053830d3` |
| orch.git.commit-vocabulary | universal | conforms | `docs`/`code`/`test`/`merge-tests` vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | Child publish on `sub/AST-1023/…` only |
| orch.git.ftr-sub-topology | universal | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | universal | conforms | `origin/ftr` ancestor of tip |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | Linear history; no rewrite ops in range |
| orch.git.no-dev-agent-branches | universal | conforms | Ticket `sub/*` publish-ref |
| orch.git.one-epic-worktree-per-parent | universal | conforms | `astral-AST-1023` |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Session-only golden cover already Archie-decided |
| orch.pipeline.plan-is-bible | universal | conforms | Diff matches Stages 1–3; boundaries held |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Artifacts child |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Review from Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty owns tests/bible on tip |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee Ada |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Assignee remains Ada |
| orch.roles.pre-commit-path-bans | universal | conforms | No banned path commits in engineer SHA |

## Pattern conformance

| cited | verdict |
| -- | -- |
| `pattern.ui.admin-endpoint` | conforms — Admin POST + `@require_admin`, mirrors session resume HTML |
| `pattern.layers.import-discipline` | conforms — ui → core + utils |
| `astral.standards.debug-contract-gated` | conforms — covered in statutes |
| `astral.patterns.require-auth-on-protected-endpoints` | conforms — covered in statutes |
| `astral.standards.in-scope-only` | conforms — covered in statutes |

## Plan adherence

Self-Assessment Scope `Single-Component` matches footprint (config + builder session emit + one Admin route). No React/localStorage (AST-1025). No job `build_cover_letter` / `_emit_cover_sections_html`. Revision 1 config-iterated field map implemented. Cross-ticket: unblocks AST-1025 only via API contract.

## Findings

### fix-now
(none)

### discuss
1. **C4 straggler** — `astral.debug.spikes-under-debug-dir` excluded by Joan; in-scope via `docs/features/**`. Substance **conforms** (plan doc, not a spike).
2. **C4 straggler** — `astral.docs.features-single-file-per-ticket` excluded by Joan; in-scope via features file. Substance **conforms**.
3. **C4 straggler** — `astral.git.engineer-test-tree-ban` excluded by Joan; in-scope via Betty tests/bible. Substance **conforms** (`code()` src-only).

### advisory
(none)

## What’s solid

Config spine + session-only SomersetCover + Admin HTML route; Style D gated; unknown `candidate_id` → 400; omit candidate → name-only sign-off.

## Recommended actions

Ada: acknowledge C4 stragglers in resolve (no product change) → User Testing.

context_tokens≈72000

#### betty — 2026-07-29T03:23:23.630Z
1. `tests/component/utils/test_config.py::TestAst1024SessionCoverLetterConfig` — `BUILD_CONFIG["session_cover_letter"]` document title + required/optional field map (job `artifact_shapes["cover_letter"]` untouched).
2. `tests/component/core/test_builder.py::TestAst1024BuildSessionCoverLetter` — `build_session_cover_letter`: validation; SomersetCover DOM (`fromBlock` / `letterdate` / `lettercontent` / `letterSignoff`); optional `toBlock`/`lettersubject`; paragraph split; HTML escape; no candidate bind; optional `profile.cover_letter_signature_image` accept/absent/reject; candidate miss; Style D `debug=True` paths (no log-string asserts).
3. `tests/component/ui/api/test_api_admin.py::TestAst1024SessionCoverLetterHtmlApi` — `POST /api/admin/session_cover_letter/html`: `@require_admin`; non-object body 400; builder `ValueError` → JSON error; 200 `text/html`; fields keyed from config only; `candidate_id` strip/None/forward/non-str.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1024SessionCoverLetterConfig \
  tests/component/core/test_builder.py::TestAst1024BuildSessionCoverLetter \
  tests/component/ui/api/test_api_admin.py::TestAst1024SessionCoverLetterHtmlApi \
  -q
```

Broken / obsolete: none (additive session path).
Integration: no existing scenario asserts session cover HTML — no revision.

`origin/sub/AST-1023/AST-1024-session-cover-letter-html-builder-admin-html-api` @ `053830d3` (`merge-tests(AST-1024): origin/tests 055e81c6`).

Bible shasums on publish tip:
- `docs/test-bible/core/builder.md` `c4fa69c1c08b3aef707085243c0eb2fda55b7c8c5912674ba25be9344c2c3607`
- `docs/test-bible/ui/api/api_admin.md` `ba9fbdb9a1085a484450009f70d37379e511febdc52d9e1559543ad588a95914`
- `docs/test-bible/utils/config.md` `6c0e32892fd41583f882b7203341a0d04c9cd5220e2132c366648ecaa4375caf`

— Betty

#### betty — 2026-07-29T03:23:15.152Z
## QA test manifest

**Publish:** `origin/sub/AST-1023/AST-1024-session-cover-letter-html-builder-admin-html-api` @ `053830d3`
**merge-tests:** `merge-tests(AST-1024): origin/tests 055e81c6fe52b1d1be43259d9abe37cb4c307e07`

### Classification
1. **Existing coverage:** none for session SomersetCover (job cover emit / AST-987 session resume stay separate).
2. **Broken / obsolete:** none.
3. **Gaps (this pass):** new builder + admin HTML API + config spine tests.

### Manifest (test-child — narrowed)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_builder.py::TestAst1024BuildSessionCoverLetter \
  tests/component/ui/api/test_api_admin.py::TestAst1024SessionCoverLetterHtmlApi \
  tests/component/utils/test_config.py::TestAst1024SessionCoverLetterConfig \
  -q
```

1. `TestAst1024BuildSessionCoverLetter` — validation; SomersetCover DOM; optional to/subject; paragraph split; HTML escape; optional `candidate_id` signature image / miss / reject / blank skip; debug True/False (no log-string asserts).
2. `TestAst1024SessionCoverLetterHtmlApi` — `@require_admin`; 400 on builder `ValueError`; 200 `text/html`; fields from `BUILD_CONFIG["session_cover_letter"]["fields"]` keys; `candidate_id` strip/None/forward.
3. `TestAst1024SessionCoverLetterConfig` — document title + required flags; job `artifact_shapes["cover_letter"]` untouched.

**Integration:** no existing scenario asserts this path — no revision; no new integration coverage.

### Bible shasums (`origin/<publish-ref>`)
- `docs/test-bible/core/builder.md` `c4fa69c1c08b3aef707085243c0eb2fda55b7c8c5912674ba25be9344c2c3607`
- `docs/test-bible/ui/api/api_admin.md` `ba9fbdb9a1085a484450009f70d37379e511febdc52d9e1559543ad588a95914`
- `docs/test-bible/utils/config.md` `6c0e32892fd41583f882b7203341a0d04c9cd5220e2132c366648ecaa4375caf`

— Betty

#### joan — 2026-07-29T03:10:44.703Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1024
**Overall:** APPROVED

**Notes:** Plan Discuss round=1 completed (concern + reply). Tip `0dde7c97`. Prior fix-now (Stage 3 hardcoded field keys vs config spine) addressed in Revision 1.
**Implementer:** Ada (parent Team table).

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
| -- | -- |
| 1 Admin screen + SomersetCover HTML | Stages 2–3 HTML API; screen/new-tab N/A — AST-1025 |
| 2 No job id; form fields; optional signature image | Stages 2–3 |
| 3 Print → PDF; no server PDF | Inherent (HTML only) |
| 4 Browser session retention | N/A — AST-1025 |
| 5 No durable artifact write | Stages 2–3 detached rules |
| 6 Clear error; no success broken tab | Stage 3 API 400; screen gating N/A — AST-1025 |
| 7 Style D debug on touched backend paths | Stage 2 |

### Child AC → plan stages

| Child AC | Stages |
| -- | -- |
| 1 In-memory payload → SomersetCover HTML via Admin | 1–3 |
| 2 No job id; name-only vs signature image | 2–3 |
| 3 No server PDF | 2–3 |
| 4 Validation failure → clear error, no success HTML | 2–3 |
| 5 Style D debug | 2 |

### Plan stages → definition

| Stage | Maps to |
| -- | -- |
| 1 Config field contract | Config source of truth; API/form spine |
| 2 Session SomersetCover emit | Golden HTML; signature rules; no persist |
| 3 Admin POST HTML route | Admin endpoint; unblocks AST-1025 |

## Statute verdicts

| id | verdict | one-line |
| -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests |
| orch.git.commit-vocabulary | conforms | Plan `docs(AST-1024):` path |
| orch.git.flow-direction-inviolable | conforms | Child `sub/*` only |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | No skip of ftr merge |
| orch.git.no-cherry-pick-rebase-force | conforms | No rewrite ops |
| orch.git.no-dev-agent-branches | conforms | Ticket sub only |
| orch.git.one-epic-worktree-per-parent | conforms | `astral-AST-1023` |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Session-only golden cover Archie-decided |
| orch.pipeline.plan-is-bible | conforms | Stages binding; React/job cover excluded |
| orch.pipeline.project-scoped-queues | conforms | Single-child Astral Artifacts |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Discuss follow-up after round=1 reply |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | tests/bible out of scope |
| orch.roles.chuckles-never-ticket-assignee | conforms | Implementer Ada |
| orch.roles.engineer-assignee-through-resolve | conforms | Reassign Ada on approve |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | Untouched |
| astral.agent.do-task-delegation | conforms | No LLM parse |
| astral.agent.grade-vector-validation | conforms | Untouched |
| astral.batch.batch-id-first | conforms | Untouched |
| astral.batch.batch-id-format | conforms | Untouched |
| astral.batch.claim-process-release | conforms | Untouched |
| astral.batch.entity-agent-responses-latest-only | conforms | Untouched |
| astral.config.config-source-of-truth | conforms | Stage 3 iterates `BUILD_CONFIG["session_cover_letter"]["fields"]` |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env |
| astral.git.betty-no-src-or-features | conforms | Engineer-owned src |
| astral.layers.core-vs-external-bright-line | conforms | Emit in core; API thin |
| astral.layers.import-direction | conforms | ui → core + utils |
| astral.layers.ui-config-driven-business-logic | conforms | Field keys from config; validation in core |
| astral.patterns.coat-check-never-store-empty | conforms | Untouched |
| astral.patterns.render-verdict-orchestrates-consult | conforms | Untouched |
| astral.patterns.require-auth-on-protected-endpoints | conforms | `@require_admin` |
| astral.standards.data-raises-caller-logs | conforms | ValueError → JSON 400 |
| astral.standards.debug-contract-gated | conforms | Style D only when debug |
| astral.standards.dry-and-focused-functions | conforms | No duplicate field-key list after Revision 1 |
| astral.standards.in-scope-only | conforms | Excludes React/nav, job cover, writes |
| astral.standards.logging-via-utils | conforms | Style D helpers |
| astral.standards.no-cross-contamination | conforms | No job load / no save_* |
| astral.standards.no-hardcoded-sets | conforms | Field keys from config only |
| astral.standards.public-then-helpers | conforms | Public session emit + helpers |
| astral.standards.utils-data-late-import-only | conforms | No new utils→data |
| astral.state.core-decides-transitions | conforms | Untouched |
| astral.state.job-prior-states-enforced | conforms | Untouched |
| astral.state.no-daisy-chain-in-run | conforms | Untouched |
| astral.ui.naming-conventions | conforms | snake_case Admin route |
| astral.ui.single-gunicorn-worker | conforms | Untouched |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.patterns.require-auth-on-protected-endpoints, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.naming-conventions, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths miss
- astral.debug.spikes-under-debug-dir — paths miss
- astral.docs.features-single-file-per-ticket — layers/paths miss
- astral.git.engineer-test-tree-ban — paths miss
- astral.layers.scripts-exempt-from-layer-rules — layers/paths miss
- astral.standards.database-header-inventory — layers/paths miss
- astral.ui.frontend-file-placement — paths miss

## Findings

### fix-now
(none)

### discuss
(none)

### acceptable
1. Session-only SomersetCover CSS/DOM — matches Archie/parent Boundaries.
2. Mirrors AST-987 session HTML auth/response pattern.
3. Unknown `candidate_id` → 400; omit candidate still works.
4. Self-assessment Single-Component / high / Medium — honest.
5. Parent screen/retention/new-tab deferred to AST-1025.

— Joan
context_tokens≈52000

#### ada — 2026-07-29T03:09:29.101Z
[plan-discuss] round=1 reply

**Delta:** Stage 3 no longer hardcodes the seven field keys. Route builds `fields = {k: body.get(k, "") for k in BUILD_CONFIG["session_cover_letter"]["fields"]}` (ui→utils `BUILD_CONFIG` import). `candidate_id` stays outside that map; required/type checks remain in core Stage 2. Added Stage 3 Decision + Revisions § + Code rules check notes for config-source-of-truth / DRY / no-hardcoded-sets.

Plan tip: `0dde7c97` on `origin/sub/AST-1023/AST-1024-session-cover-letter-html-builder-admin-html-api`.
Blob: https://github.com/susansomerset/astral/blob/sub/AST-1023/AST-1024-session-cover-letter-html-builder-admin-html-api/docs/features/artifacts/ast-1024-session-cover-letter-html-builder-admin-html-api.md

#### joan — 2026-07-29T03:07:20.538Z
[plan-discuss] round=1 concern
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1024
**Overall:** REVISE

**Notes:** First Plan Ready pass. Tip `b386eebb`. Unblocks AST-1025 correctly; job cover / React left out of scope.
**Implementer:** Ada (plan author / parent Team table).

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
| -- | -- |
| 1 Admin screen enter fields + open SomersetCover HTML | Stages 2–3 supply HTML API; **Admin screen / new-tab UX N/A — AST-1025** |
| 2 No job id; form fields; optional selected-candidate signature image | Stages 2–3 |
| 3 Print → PDF; no server PDF | Inherent (HTML-only response) |
| 4 Browser session retention | N/A — boundary: AST-1025 |
| 5 No durable candidate/job artifact write | Stages 2–3 hard detached rules |
| 6 Clear error on Admin screen; no success broken tab | Stage 3 API 400 JSON; **screen/tab gating N/A — AST-1025** |
| 7 `debug=True` Style D on touched backend paths | Stage 2 |

### Child AC → plan stages

| Child AC | Stages |
| -- | -- |
| 1 In-memory payload → SomersetCover HTML via Admin | 1–3 |
| 2 No job id; name-only vs signature image | 2–3 |
| 3 No server PDF | 2–3 (HTML only) |
| 4 Validation/render failure → clear error, no success HTML | 2–3 |
| 5 Style D debug on touched backend paths | 2 |

### Plan stages → definition

| Stage | Maps to |
| -- | -- |
| 1 `BUILD_CONFIG["session_cover_letter"]` field contract | Config source of truth; API/form spine |
| 2 `build_session_cover_letter` SomersetCover emit | Purpose / Functional golden HTML; AC2 signature rules; AC5/7; Boundaries |
| 3 Admin POST HTML route | pattern.ui.admin-endpoint; child AC1/4; unblocks AST-1025 |

## Statute verdicts

| id | verdict | one-line |
| -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests |
| orch.git.commit-vocabulary | conforms | Plan `docs(AST-1024):` path |
| orch.git.flow-direction-inviolable | conforms | Child `sub/*` only |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | No skip of ftr merge |
| orch.git.no-cherry-pick-rebase-force | conforms | No rewrite ops |
| orch.git.no-dev-agent-branches | conforms | Ticket sub only |
| orch.git.one-epic-worktree-per-parent | conforms | `astral-AST-1023` |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Session-only golden cover already Archie-decided on parent |
| orch.pipeline.plan-is-bible | conforms | Stages binding; React/job cover excluded |
| orch.pipeline.project-scoped-queues | conforms | Single-child Astral Artifacts |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | tests/bible out of scope |
| orch.roles.chuckles-never-ticket-assignee | conforms | Implementer Ada |
| orch.roles.engineer-assignee-through-resolve | conforms | Reassign Ada after this pass |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | Untouched |
| astral.agent.do-task-delegation | conforms | No new do_task / LLM parse |
| astral.agent.grade-vector-validation | conforms | Untouched |
| astral.batch.batch-id-first | conforms | Untouched |
| astral.batch.batch-id-format | conforms | Untouched |
| astral.batch.claim-process-release | conforms | Untouched |
| astral.batch.entity-agent-responses-latest-only | conforms | Untouched |
| astral.config.config-source-of-truth | violates | Stage 1 Decision says config owns field keys for API+form spine; Stage 3 hardcodes the same key list in Flask |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env |
| astral.git.betty-no-src-or-features | conforms | Engineer-owned src |
| astral.layers.core-vs-external-bright-line | conforms | Emit in core; API thin |
| astral.layers.import-direction | conforms | ui → core; core may read candidate for optional image |
| astral.layers.ui-config-driven-business-logic | needs-discussion | Required-field policy correctly in core/config; API still duplicates field key list (see fix-now) |
| astral.patterns.coat-check-never-store-empty | conforms | Untouched |
| astral.patterns.render-verdict-orchestrates-consult | conforms | Untouched |
| astral.patterns.require-auth-on-protected-endpoints | conforms | `@require_admin` on new Admin route |
| astral.standards.data-raises-caller-logs | conforms | Core raises ValueError; UI returns JSON |
| astral.standards.debug-contract-gated | conforms | Style D only when `debug=True` / `ui_llm_debug()` |
| astral.standards.dry-and-focused-functions | violates | Duplicate field-key list across Stage 1 config and Stage 3 handler |
| astral.standards.in-scope-only | conforms | Explicitly excludes React/nav, job cover, artifact writes |
| astral.standards.logging-via-utils | conforms | Style D helpers |
| astral.standards.no-cross-contamination | conforms | Hard no job load / no save_* / no artifact write |
| astral.standards.no-hardcoded-sets | violates | Session field key set hardcoded in Stage 3 despite config contract |
| astral.standards.public-then-helpers | conforms | Public `build_session_cover_letter` + helpers |
| astral.standards.utils-data-late-import-only | conforms | No new utils→data |
| astral.state.core-decides-transitions | conforms | Untouched |
| astral.state.job-prior-states-enforced | conforms | Untouched |
| astral.state.no-daisy-chain-in-run | conforms | Untouched |
| astral.ui.naming-conventions | conforms | snake_case Admin route |
| astral.ui.single-gunicorn-worker | conforms | Untouched |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.patterns.require-auth-on-protected-endpoints, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.naming-conventions, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths miss
- astral.debug.spikes-under-debug-dir — paths miss
- astral.docs.features-single-file-per-ticket — layers/paths miss
- astral.git.engineer-test-tree-ban — paths miss
- astral.layers.scripts-exempt-from-layer-rules — layers/paths miss
- astral.standards.database-header-inventory — layers/paths miss
- astral.ui.frontend-file-placement — paths miss

## Findings

### fix-now
1. **Location:** Stage 1 Decision vs Stage 3 request mapping
   **Finding:** Stage 1 ⚠️ Decision: “Config owns the session field keys so AST-1025 form + this API share one spine **without hardcoding duplicate required lists in React and Flask**.” Stage 3 then builds `fields` with an explicit seven-key `body.get(...)` dict that duplicates `BUILD_CONFIG["session_cover_letter"]["fields"]`. That reintroduces the drift the Decision forbids (config adds a key → API silently drops it; core never sees it).
   **Recommendation:** In Stage 3, build `fields` from config, e.g. `fields = {k: body.get(k, "") for k in BUILD_CONFIG["session_cover_letter"]["fields"]}` (import `BUILD_CONFIG` from utils — ui→utils allowed). Keep `candidate_id` handling outside that map. Leave required/type checks in core (already Stage 2).

### discuss
(none blocking)

### acceptable
1. Session-only SomersetCover CSS/DOM (no job cover backfill) — matches Archie/parent Boundaries.
2. Mirrors AST-987 `session_resume_html` auth/response pattern — sound.
3. Unknown `candidate_id` → 400 (not silent empty) — clear error; no-candidate omit still works.
4. Self-assessment Single-Component / high / Medium — honest about contamination risk.
5. Parent screen/retention/new-tab ACs correctly deferred to AST-1025.

— Joan
context_tokens≈45000

#### chuckles — 2026-07-29T03:04:55.887Z
[thread-orphan] Joan session relocated for epic workspace.
found: `/home/susan/.cursor/chats/0ab2adc851c7f84d4ce4bb00f485d83d/2f96bb3a-9e52-4b2a-80a0-b832afadc55f/store.db`
expected: `/home/susan/.cursor/chats/241bb01e7f0660c1b4999e1300653d55/2f96bb3a-9e52-4b2a-80a0-b832afadc55f/store.db`
— Chuckles

#### ada — 2026-07-29T03:02:19.062Z
Plan: [`docs/features/artifacts/ast-1024-session-cover-letter-html-builder-admin-html-api.md`](https://github.com/susansomerset/astral/blob/sub/AST-1023/AST-1024-session-cover-letter-html-builder-admin-html-api/docs/features/artifacts/ast-1024-session-cover-letter-html-builder-admin-html-api.md) on `origin/sub/AST-1023/AST-1024-session-cover-letter-html-builder-admin-html-api` @ `b386eebb`.

**Scope:** `Single-Component` — config field contract, session SomersetCover emit in `builder.py`, one Admin POST HTML route; job cover emit and React left to siblings/out of scope.

**Conf:** `high` — mirrors AST-987 session HTML (`build_session_base_resume` + admin POST); SomersetCover DOM/CSS specified in parent Original brief; signature image reuses `_safe_image_src`.

**Risk:** `Medium` — mistaken job-cover reuse or a write path would contaminate artifacts / materials preview; plan isolates session CSS/DOM and forbids persist/job load.

---

# Session cover letter HTML builder + admin HTML API (Session Cover Letter)

**Linear:** [AST-1024](https://linear.app/astralcareermatch/issue/AST-1024/session-cover-letter-html-builder-admin-html-api-session-cover-letter)
**Parent:** [AST-1023](https://linear.app/astralcareermatch/issue/AST-1023/session-cover-letter) — Session Cover Letter
**Publish ref:** `origin/sub/AST-1023/AST-1024-session-cover-letter-html-builder-admin-html-api`
**Unblocks:** [AST-1025](https://linear.app/astralcareermatch/issue/AST-1025/admin-session-cover-letter-page-session-retention) — Admin page + localStorage (consume this API only; do not implement React here)

Core session cover emit from an in-memory field payload (no job load; no artifact persist) producing golden SomersetCover HTML, plus an Admin `POST` HTML route under existing admin auth. Optional signature-image read from the **selected** candidate profile when a `candidate_id` is supplied — otherwise name-only sign-off. Owns Style D debug on touched backend paths. Does **not** own Admin React page, nav, or session retention.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `BUILD_CONFIG["session_cover_letter"]` field contract (keys + required flags + document title) | utils |
| `src/core/builder.py` | Add `build_session_cover_letter` + session-only SomersetCover emit helpers; update module public list | core |
| `src/ui/api/api_admin.py` | Add `POST /api/admin/session_cover_letter/html` (`@require_admin`) — validate JSON, return `text/html` or JSON error | ui |

**Out of scope (do not touch):** React pages / `NAV_CONFIG` / routes / localStorage (AST-1025), job `build_cover_letter` / `build_cover_letter_from_job` / `_emit_cover_sections_html` / materials cover tabs, `TASK_CONFIG` / Manage Tasks / dispatch chains, candidate or job artifact writers, Session Resume Paste routes, `tests/`, bible, repo-root `artifacts/`.

## API contract (for AST-1025)

**`POST /api/admin/session_cover_letter/html`**
- Auth: `@require_admin` (same as Session Resume Paste admin tools).
- Request JSON:
  ```json
  {
    "from_block": "Susan Somerset • Oakland, CA\nhire@susansomerset.com • 415-745-5238",
    "letter_date": "July 27, 2026",
    "to_block": "",
    "subject": "",
    "letter": "Dear Hiring Team,\n\nParagraph two…",
    "signoff_closing": "Best,",
    "signature": "Susan Somerset",
    "candidate_id": null
  }
  ```
  - Field keys and required flags come from `BUILD_CONFIG["session_cover_letter"]["fields"]` (Stage 1).
  - `candidate_id`: optional. Omit, `null`, or `""` → no candidate read (name-only sign-off). Non-empty string → optional profile signature-image read only.
  - Aligns with cover artifact naming spine: `subject` ↔ `Subject`, `letter` ↔ `Letter`, `signature` ↔ `signature`. Session also carries layout fields (`from_block`, `letter_date`, `to_block`, `signoff_closing`) that job artifacts do not store today.
- Success **200**: raw HTML body, `Content-Type: text/html; charset=utf-8` (same pattern as `POST /api/admin/session_resume/html`).
- Client / validation failures **400**: `{ "success": false, "error": "<clear message>" }` — never return success HTML on failure.
- Unknown / missing candidate when `candidate_id` is non-empty: **400** with clear error (do not silently pretend no candidate).

**Detached rules (hard):**
- Do **not** load a job or read `job_data.artifacts.cover_letter`.
- Do **not** call `save_candidate`, job artifact writers, or any cover-letter chain task.
- Letter field values come **only** from the request body. Candidate row (when id provided) is used **only** for `profile.cover_letter_signature_image` via existing `_safe_image_src`.
- Do **not** change `/candidate/cover/<job_id>` or job cover emit DOM/CSS.

## Stage 1: Config field contract

**Done when:** `BUILD_CONFIG["session_cover_letter"]` exists with document title and the field map below; no other config blocks changed for this ticket.

1. In `src/utils/config.py`, inside `BUILD_CONFIG` (after `artifact_shapes` / near cover-related keys is fine), add:
   ```python
   "session_cover_letter": {
       "document_title": "SomersetCover",
       "fields": {
           "from_block": {"required": True},
           "letter_date": {"required": True},
           "to_block": {"required": False},
           "subject": {"required": False},
           "letter": {"required": True},
           "signoff_closing": {"required": True},
           "signature": {"required": True},
       },
   },
   ```
2. Do **not** add `NAV_CONFIG` entries (AST-1025).
3. Do **not** change `artifact_shapes["cover_letter"]` (Subject/Letter/signature stays the job artifact shape).

⚠️ **Decision:** Config owns the session field keys so AST-1025 form + this API share one spine without hardcoding duplicate required lists in React and Flask.

## Stage 2: Session SomersetCover builder (core)

**Done when:** `build_session_cover_letter` returns a standalone print-oriented HTML document whose DOM matches Original-brief SomersetCover blocks (`fromBlock`, optional `toBlock` / `lettersubject`, `letterdate`, `lettercontent`, `letterSignoff`); no job load; optional signature image only from selected candidate profile; empty/invalid required fields raise `ValueError` with clear messages; `debug=True` emits Style D headers + `|` detail.

1. In `src/core/builder.py` module docstring public list, append ``build_session_cover_letter``.
2. Add public function immediately after `build_session_base_resume`:
   ```python
   def build_session_cover_letter(
       fields: dict,
       *,
       candidate_id: Optional[str] = None,
       debug: bool = False,
   ) -> str:
   ```
3. When `debug=True`, call `_log.set_debug_flag(True)` before other work.
4. Validate `fields`:
   - If `fields` is not a `dict`, raise `ValueError("session cover letter fields object is required")`.
   - Read `cfg = BUILD_CONFIG["session_cover_letter"]` and `field_defs = cfg["fields"]`.
   - For each key in `field_defs`: coerce missing → `""`; require `isinstance(..., str)` else raise `ValueError(f"{key} must be a string")`; if `field_defs[key]["required"]` and not `value.strip()`, raise `ValueError(f"{key} is required")`.
   - Ignore unknown extra keys in `fields` (do not error).
5. Resolve optional signature image (read-only):
   - `sig_src = None`.
   - If `candidate_id` is a non-empty string after strip:
     - `row = candidate_mod.get_candidate(candidate_id.strip())`.
     - If not `row`, raise `ValueError(f"Candidate not found: {candidate_id.strip()}")`.
     - `cd = _coerce_candidate_blob(row)`; `profile = cd.get("profile") or {}`.
     - `sig_src = _safe_image_src(profile.get("cover_letter_signature_image"))` (may remain `None` → name-only sign-off).
   - If `candidate_id` is `None` / non-str / blank: do **not** call `get_candidate`.
6. Emit HTML via new helper `_emit_session_cover_html_document(fields, signature_image_src=sig_src) -> str` (see step 7). Do **not** call `_emit_html_document`, `_emit_cover_sections_html`, or job cover builders.
7. Implement `_emit_session_cover_html_document`:
   - Pull colors/fonts from `BUILD_CONFIG["default_style"]` the same way `_emit_html_document` reads accent / header / text / border / font stacks (literal defaults only as fallbacks matching today’s builder).
   - Document `<title>` and meta description use `BUILD_CONFIG["session_cover_letter"]["document_title"]` (and signature name when present for meta).
   - CSS: session-only SomersetCover rules from parent Original brief — `:root` tokens; `body` / `.cover-letter` / `.fromBlock` / `.toBlock` / `.letterdate` / `.lettersubject` / `.lettercontent` / `.lettercontent p` / `.letterSignoff` / `.signature-img` (`height: 61px`, `margin: 8px 0 -25px 0`); `@page` / `@media print` rules from the brief’s second `<style>` block. Do **not** copy the full resume body stylesheet (experience/skills/h2 chrome). Do **not** modify the CSS string inside `_emit_html_document`.
   - Body structure (escape all text with `html.escape`; image `src` via `_safe_image_src` only — already validated):
     ```html
     <main>
       <div class="cover-letter">
         <div class="fromBlock">…</div>          <!-- required; newlines → <br> between escaped lines -->
         <!-- optional .toBlock if to_block.strip() -->
         <div class="letterdate">…</div>
         <!-- optional .lettersubject if subject.strip() -->
         <div class="lettercontent">…</div>     <!-- paragraphs: see step 8 -->
         <div class="letterSignoff">…</div>     <!-- see step 9 -->
       </div>
     </main>
     ```
8. Paragraphize `letter`:
   - Normalize `\r\n` → `\n`, strip.
   - Split on blank lines: `re.split(r"\n\s*\n", text)`; keep non-empty stripped chunks as `<p>` bodies (escape each chunk; preserve single newlines inside a chunk as spaces, or as `<br>` — pick **`<br>`** after escape so pasted single-newline breaks survive).
   - If the split yields a single chunk that still contains `\n`, split that chunk on `\n` into separate `<p>` tags (form textarea UX).
9. Sign-off block (class `letterSignoff`):
   - Emit `html.escape(signoff_closing)` then `<br>`.
   - If `signature_image_src`: emit `<img src="..." class="signature-img" alt="Signature">` then `<br>` (`src` attribute-escaped with `html.escape(..., quote=True)`).
   - Emit `html.escape(signature)` (typed name — always, including when image present).
10. When `debug=True`, Style D:
    - Header: `func="builder.build_session_cover_letter"`, `index=1`, `total=1`, `identifier=candidate_id.strip() if candidate_id else "session"`, outcome `"success — session cover html"`.
    - Detail lines (`|`): which required fields were non-empty; `to_block`/`subject` present or omitted; `candidate_id` used or not; `signature_image=accepted|absent_or_rejected|skipped_no_candidate`; `html_chars=…`; optional truncated `html_preview` via `debug_detail_block`.
    - On validation failure before emit, use `_emit_builder_failure` with the same `func` name (mirror `build_session_base_resume`).
11. Return the HTML string. Forbidden: any `save_*` / artifact write / job fetch.

⚠️ **Decision:** Session-only golden cover DOM/CSS (Original brief), not a backfill of job `build_cover_letter`. Archie: no job cover upgrade this epic.

⚠️ **Decision:** Optional `candidate_id` is explicit in the request (Katherine passes selected id or omits). Server does not invent candidate context from Flask cookies/session beyond what the JSON body provides.

## Stage 3: Admin HTML route

**Done when:** `POST /api/admin/session_cover_letter/html` is registered on `admin_bp`, requires admin auth, returns `text/html` on valid body and JSON `{success:false,error}` on bad input / `ValueError`; `py_compile` clean on touched Python files.

1. In `src/ui/api/api_admin.py`, import `build_session_cover_letter` from `src.core.builder` (keep existing `build_session_base_resume` import; extend that import line). Import `BUILD_CONFIG` from `src.utils.config` if not already imported in this module.
2. Add route immediately after `session_resume_html` (leave comment `# AST-1024 session cover letter HTML`):
   ```python
   @admin_bp.route("/session_cover_letter/html", methods=["POST"])
   @require_admin
   def session_cover_letter_html():
       body = request.get_json(silent=True) or {}
       if not isinstance(body, dict):
           return jsonify({"success": False, "error": "JSON object body is required"}), 400
       # Field keys from config only — do not hardcode the key list here (Joan plan-discuss round=1).
       field_defs = BUILD_CONFIG["session_cover_letter"]["fields"]
       fields = {k: body.get(k, "") for k in field_defs}
       raw_cid = body.get("candidate_id")
       candidate_id = raw_cid.strip() if isinstance(raw_cid, str) else None
       if candidate_id == "":
           candidate_id = None
       try:
           html_out = build_session_cover_letter(
               fields,
               candidate_id=candidate_id,
               debug=ui_llm_debug(),
           )
       except ValueError as exc:
           return jsonify({"success": False, "error": str(exc)}), 400
       return Response(html_out, mimetype="text/html; charset=utf-8")
   ```
3. Do **not** register a new blueprint or change `server.py`.
4. Do **not** alter `/api/admin/session_resume/*` or `/candidate/cover/<job_id>`.
5. Compile: `python3 -m py_compile src/utils/config.py src/core/builder.py src/ui/api/api_admin.py`.

⚠️ **Decision:** API builds `fields` by iterating `BUILD_CONFIG["session_cover_letter"]["fields"]` so config remains the single key spine (AST-1025 form + Flask + core). `candidate_id` stays outside that map. Required/type validation stays in core (Stage 2).

## Self-Assessment

**Scope:** `Single-Component` — config field contract, one core session emit path beside `build_session_base_resume`, and one Admin POST HTML route; job cover emit and React left untouched.

**Conf:** `high` — mirrors AST-987 session HTML pattern (`build_session_base_resume` + admin POST); SomersetCover DOM/CSS is specified in the parent Original brief; signature-image reuse of `_safe_image_src` is known.

**Risk:** `Medium` — mistaken reuse of job cover emit or a write path would contaminate job/candidate artifacts or change materials preview; the plan forbids those paths and keeps session CSS/DOM isolated.

## Code rules check

- §1.1 / `in-scope-only`: no job cover backfill, no React/nav, no artifact writes.
- §1.3 DRY: new session emit helper; reuse `_safe_image_src` / `_coerce_candidate_blob` / `_emit_builder_failure`; do not fork job `_emit_cover_sections_html`. Stage 3 field keys iterated from config (no duplicate hardcoded list).
- §1.5.1: Style D only when `debug=True` via `ui_llm_debug()` / `debug=` pass-through.
- §2.1 / `no-hardcoded-sets`: field keys + title in `BUILD_CONFIG["session_cover_letter"]`; API maps body via those keys; style tokens from `default_style`.
- §2.9 / require-auth: `@require_admin` on the new Admin route.
- §3.3: ui → core + utils; core may call `candidate_mod.get_candidate` for optional image read.
- §3.6: no repo-root `artifacts/` directory.

## Revisions

Revision 1 — 2026-07-29
Driven by: Joan `[plan-discuss] round=1 concern` — Stage 3 hardcoded seven-key `body.get` dict duplicated `BUILD_CONFIG["session_cover_letter"]["fields"]` (violates config-source-of-truth / DRY / no-hardcoded-sets).
Changes: Stage 3 builds `fields = {k: body.get(k, "") for k in BUILD_CONFIG["session_cover_letter"]["fields"]}`; `candidate_id` remains outside the map; Decision + Code rules check updated.

## Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-1023/AST-1024-session-cover-letter-html-builder-admin-html-api`
**Tip:** `db3915d4`

**Stages delivered:**
- Stage 1 — `BUILD_CONFIG["session_cover_letter"]` field contract + document title
- Stage 2 — `build_session_cover_letter` + `_emit_session_cover_html_document` (SomersetCover; optional candidate signature image read-only)
- Stage 3 — `POST /api/admin/session_cover_letter/html` (`@require_admin`, fields from config keys)

## Radia review (code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1024
**Publish ref tip (pre-docs):** `053830d3`
**Overall:** DISCUSS

### What’s solid
- Stages 1–3 match the plan bible: config field spine, session-only SomersetCover emit, Admin POST under `@require_admin`.
- Stage 3 iterates `BUILD_CONFIG["session_cover_letter"]["fields"]` (Joan Revision 1).
- No job cover reuse, no artifact writes, optional candidate signature via `_safe_image_src` only.
- Style D gated on `debug=True` / `ui_llm_debug()` with index + `|` detail + `debug_detail_block`.

### Issues
**discuss (C4 stragglers — Joan Excluded, in-scope on code diff):**
1. `astral.debug.spikes-under-debug-dir` — `docs/features/**` present (plan/review doc); substance conforms (not a misplaced spike).
2. `astral.docs.features-single-file-per-ticket` — single features file; substance conforms.
3. `astral.git.engineer-test-tree-ban` — `tests/**` + bible via Betty `test`/`merge-tests`; engineer `code()` touched only `src/`; substance conforms.

**fix-now:** none

### Recommended actions
- Ada: acknowledge C4 stragglers in resolve (no product change required) → User Testing.

## Resolution

**2026-07-29** — Radia `[code-rubric] revision=1` Overall DISCUSS; tip intake `d5813c67` (docs-only) after product `053830d3`.

- **fix-now:** none — no product changes.
- **discuss (C4 stragglers):** acknowledged — Joan Excluded statutes became in-scope via features/test-tree on the tip; substance already **conforms** (plan under `docs/features/`, single ticket file, Betty owns tests/bible; engineer `code()` was src-only). No product or plan-stage change.
- **advisory:** none.
