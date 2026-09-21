<!-- linear-archive: AST-1131 archived 2026-08-07 -->

## Linear archive (AST-1131)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1131/normalize-pastedlist-email-html-before-link-discovery-manage-email  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1130 — Manage Email create button for job lists isn't working  
**Blocked by / blocks / related:** parent: AST-1130; blocks: AST-1133; blocks: AST-1132

### Description

## What this implements

Owns making Create see real job-detail hrefs from entity-escaped / Gmail-auto-linkified board pastes (and simple newline-delimited job-link pastes), so attribute URLs are not promoted to anchors and nested auto-link href corruption is unwrapped before candidate collection. Does **not** own exclude-list policy or qualify apply (siblings #2 / #3).

## In scope

- [X] `pattern.config.config-block` — extend `METEORITE_EMAIL_INGEST_CONFIG` with paste-normalize knobs
- [X] `astral.config.config-source-of-truth` — unescape / nested-autolink / bare-URL promote thresholds live in config
- [X] `astral.standards.no-hardcoded-sets` — no inline attr/marker sets in core
- [X] `astral.standards.debug-contract-gated` — preserve Style D per-link ingest logging; no ungated debug
- [X] `astral.layers.core-vs-external-bright-line` — pure string normalize in utils; core only wires call sites; no new I/O
- [X] `astral.layers.import-direction` — utils ← config only; core ← utils
- [X] `astral.standards.in-scope-only` — strip + ingest normalize only; no exclude-list / qualify / gaze_email redesign
- [X] `astral.standards.dry-and-focused-functions` — single `normalize_pasted_list_email_html` helper, dual call sites

## Considered but excluded

* `pattern.state.entity-state-transitions` / `astral.state.*` — create still lands **METEORITE_NEW** via existing path; no state-machine work (AST-1133 / prior)
* `pattern.batch.entity-claim-process-release` — no batch claim changes (qualify is AST-1133)
* `astral.agent.do-task-delegation` — no LLM / consult path
* `astral.ui.*` / Manage Email React — API/UI contract unchanged
* Host/path exclude lists and non-job Playwright skip — **AST-1132**
* `qualify_meteorite` ERROR/QUALIFIED apply — **AST-1133**
* `gaze_email` dispatch redesign — out of epic boundary

## Acceptance criteria

- [X] For each real posting created from that email, `job_link` is the clean ATS job URL (no nested auto-link markup inside the stored link).
- [X] With `debug=True` on Create/ingest, logs show per-link Style D `index N/M` headers and `|` detail for found / skipped / recorded outcomes (not summary-only).
- [X] A single-link or single-JD Create that already succeeded before this epic still succeeds.
- [X] Also works on a simple copy/paste of newline-delimited job links (not Dice-exclusive).
- [X] After normalize, attribute URLs (e.g. SVG `xmlns` → `w3.org/2000/svg`) are not collected as `a[href]` candidates.

## Boundaries

Does **not** own exclude-list / non-job create skip (sibling #2) or qualify ERROR bind (sibling #3). Does not redesign gaze_email.

## Notes for planning

Parent UAT shape includes Dice Saved-jobs HTML paste and newline-delimited link lists. Root cause: entity-escaped paste + Gmail nested auto-links inside `href`/`xmlns` attribute values.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1130-manage-email-create-button-for-job-lists-isnt-working`, child `sub/AST-1130/AST-1131-normalize-pasted-list-email-html`. Created at dispatch-parent.

### Comments

#### radia — 2026-08-02T20:05:54.429Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1131
**Publish ref:** `origin/sub/AST-1130/AST-1131-normalize-pasted-list-email-html` @ `4293f12c4a54c89bf45481c293b6ec329a3e4ce7`
**Overall:** DISCUSS

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | conforms | No graded consult / confidence path |
| `astral.agent.do-task-delegation` | scoped | conforms | No do_task / LLM path |
| `astral.agent.grade-vector-validation` | scoped | conforms | No grade vectors |
| `astral.batch.batch-id-first` | scoped | conforms | No batch claim helpers |
| `astral.batch.batch-id-format` | scoped | conforms | No batch_id generation |
| `astral.batch.claim-process-release` | scoped | conforms | No claim/process/release changes |
| `astral.batch.entity-agent-responses-latest-only` | scoped | conforms | No agent_data RESPONSE work |
| `astral.config.config-source-of-truth` | scoped | conforms | Paste knobs extend METEORITE_EMAIL_INGEST_CONFIG |
| `astral.config.pass-threshold-vs-score-floor` | scoped | conforms | No scoring thresholds |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | conforms | No secrets/env values |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | paths miss diff (['artifacts/**', 'scripts/spikes/**']) |
| `astral.debug.spikes-under-debug-dir` | scoped | conforms | Combined plan under docs/features — not spike notes |
| `astral.dispatch.run-next-is-chain-authority` | scoped | conforms | No dispatch/run_next changes |
| `astral.dispatch.seed-auto-false` | scoped | conforms | No seed/dispatch_task rows |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | One docs/features/meteorite/ast-1131-… plan file |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty test/bible only; merge-tests exception ok |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | code() commit is src-only; tests from Betty |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | Pure string normalize in utils; core wires only |
| `astral.layers.import-direction` | scoped | conforms | utils←config late; core←utils; no data/external |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | layers ∩ diff empty (['scripts']); paths miss diff (['scripts/**']) |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | No UI rules; config consumed by utils/core |
| `astral.patterns.coat-check-never-store-empty` | scoped | conforms | No coat-check keys |
| `astral.patterns.render-verdict-orchestrates-consult` | scoped | conforms | No consult/render_verdict |
| `astral.patterns.require-auth-on-protected-endpoints` | scoped | not-applicable | layers ∩ diff empty (['ui']); paths miss diff (['src/ui/**']) |
| `astral.seed.agent-tables-in-repo-json` | scoped | conforms | No seed JSON |
| `astral.seed.archie-catalog-wins` | scoped | conforms | No catalog seed |
| `astral.seed.boot-only-not-hot-path` | scoped | conforms | No boot seed path |
| `astral.seed.define-approved` | scoped | conforms | No seed define work |
| `astral.seed.operator-rows-stay-deleted` | scoped | conforms | No operator seed rows |
| `astral.seed.other-via-coverage-join` | scoped | conforms | No coverage-join seed |
| `astral.standards.data-raises-caller-logs` | scoped | conforms | No data-layer edits |
| `astral.standards.database-header-inventory` | scoped | not-applicable | layers ∩ diff empty (['data']); paths miss diff (['src/data/**']) |
| `astral.standards.debug-contract-gated` | scoped | conforms | Style D preserved; no ungated debug added |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | Single helper; dual thin call sites |
| `astral.standards.in-scope-only` | scoped | conforms | Normalize only; exclude/qualify untouched |
| `astral.standards.logging-via-utils` | scoped | conforms | Helper pure; gazer/inbox loggers unchanged |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | normalize_pasted_list_email_html domain-named |
| `astral.standards.no-cross-contamination` | scoped | conforms | Stays on email→meteorite ingest path |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | Attr/thresholds/promote in config; trail punct module const |
| `astral.standards.public-then-helpers` | scoped | conforms | Public helper + local regex constants colocated |
| `astral.standards.utils-data-late-import-only` | scoped | conforms | No utils→data import |
| `astral.state.core-decides-transitions` | scoped | conforms | Still METEORITE_NEW via existing create path |
| `astral.state.job-prior-states-enforced` | scoped | conforms | No JOB_STATES / transition edits |
| `astral.state.no-daisy-chain-in-run` | scoped | conforms | No run_next / daisy-chain |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | layers ∩ diff empty (['ui']); paths miss diff (['src/ui/frontend/**']) |
| `astral.ui.naming-conventions` | scoped | not-applicable | layers ∩ diff empty (['ui']); paths miss diff (['src/ui/**']) |
| `astral.ui.single-gunicorn-worker` | scoped | conforms | config.py paste knobs only; no worker changes |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | Single merge-tests(AST-1131) SHA on sub tip |
| `orch.git.commit-vocabulary` | universal | conforms | plan/code/docs/test/merge-tests vocabulary only |
| `orch.git.flow-direction-inviolable` | universal | conforms | Publish stays on origin/sub/AST-1130/AST-1131-… |
| `orch.git.ftr-sub-topology` | universal | conforms | Child sub under AST-1130 parent topology |
| `orch.git.merge-on-checkout` | universal | conforms | No illegal merge-on-checkout recipe in commits |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | No cherry-pick/rebase/force on publish ref |
| `orch.git.no-dev-agent-branches` | universal | conforms | Uses sub/AST-1130/AST-1131-… only |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | Review in astral-AST-1130 epic worktree |
| `orch.git.three-permanent-branches` | universal | conforms | No new permanent branch invented |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | No product-decision fork; plan decisions shipped |
| `orch.pipeline.plan-is-bible` | universal | conforms | Stages 1–3 match Files Changed and diff |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Astral Meteorite child only |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Entered at Tests Passed |
| `orch.roles.archie-approves-statutes` | universal | conforms | No canon/statutes edits |
| `orch.roles.betty-owns-test-tree` | universal | conforms | tests/bible via test()+merge-tests only |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | Assignee remains Ada |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Implementer stays assignee through review |
| `orch.roles.pre-commit-path-bans` | universal | conforms | No banned-path product commits |

## Pattern conformance

- `pattern.config.config-block` — **conforms** (extend `METEORITE_EMAIL_INGEST_CONFIG`)
- Other Linear In-scope citations are active statutes covered in Statutes checked

## Plan adherence

Three-dot diff vs `origin/dev` matches plan Stages 1–3 and Self-Assessment **Single-Component** (config + formatting helper + thin inbox/gazer wires). No exclude-list / qualify / gaze_email / UI smuggle from AST-1132/1133. Style D ingest logging preserved; helper is pure and idempotent for dual call sites.

## Findings

**discuss (C4 straggler):** `astral.debug.spikes-under-debug-dir` — Joan excluded; diff touches `docs/features/**`. Scores **conforms** (combined plan, not spike notes). No product action — ack only.

**discuss (C4 straggler):** `astral.docs.features-single-file-per-ticket` — Joan excluded; plan file landed. Scores **conforms**. No product action — ack only.

**discuss (C4 straggler):** `astral.git.engineer-test-tree-ban` — Joan excluded; `tests/**` + bible on tip via Betty. Scores **conforms** (`code()` src-only). No product action — ack only.

**fix-now:** none

### What’s solid

- Unescape gate / nested-autolink attrs / promote flag in `METEORITE_EMAIL_INGEST_CONFIG`; late config + BeautifulSoup imports comment-justified.
- Single `normalize_pasted_list_email_html`; strip + ingest wires only; AST-1132/1133 boundaries held.
- One `merge-tests(AST-1131)` SHA; commit vocabulary clean.

### Notes

Joan plan-rubric verdict attached (APPROVED). Trailing bare-URL punctuation remains a documented module constant (Joan plan discuss already accepted as local hygiene).

Docs append: `docs/features/meteorite/ast-1131-normalize-pasted-list-email-html.md` (`docs(AST-1131): Radia review — findings`).

context_tokens≈42000

#### betty — 2026-08-02T20:02:20.980Z
## QA test manifest

**Publish:** `origin/sub/AST-1130/AST-1131-normalize-pasted-list-email-html` @ `01efc371` (`merge-tests(AST-1131): origin/tests 3f5f1afa5e3d1ffc28d35bd81fa5ddff2012ba5a`)

### Classification

1. **Existing coverage (bible-backed):** `TestAst1061MeteoriteEmailIngest` — regression that clean single-link / body Create still works after idempotent normalize.
2. **Broken / obsolete:** none.
3. **Gaps (this pass):** paste/list normalize helper + config knobs + strip/ingest wire.

### Manifest (run these)

1. `tests/component/utils/test_formatting.py::TestNormalizePastedListEmailHtml`
2. `tests/component/utils/test_config.py::TestAst1131MeteoriteEmailIngestPasteNormalizeConfig`
3. `tests/component/core/test_inbox.py::TestAst1131StripNormalizePastedList`
4. `tests/component/core/test_gazer.py::TestAst1131NormalizePastedListEmailIngest`
5. `tests/component/core/test_gazer.py::TestAst1061MeteoriteEmailIngest`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_formatting.py::TestNormalizePastedListEmailHtml \
  tests/component/utils/test_config.py::TestAst1131MeteoriteEmailIngestPasteNormalizeConfig \
  tests/component/core/test_inbox.py::TestAst1131StripNormalizePastedList \
  tests/component/core/test_gazer.py::TestAst1131NormalizePastedListEmailIngest \
  tests/component/core/test_gazer.py::TestAst1061MeteoriteEmailIngest \
  -q
```

### Bible shasums on publish-ref

- `4c7415b2f6c73b3713ec0af6d0f53ab24fdc229f2addfb20bf4cec65c4456c7f` `docs/test-bible/utils/formatting.md`
- `d341588727fdd447188bd4f081c0931d0e66a292633e473136afa872c080beb1` `docs/test-bible/utils/config.md`
- `7496733f34849347878ef59d7a32cf3f409bb0c8788f4a5cfb360c79dc2a9988` `docs/test-bible/core/gazer.md`
- `ee11e28e9efa5ef717c484b50163afe70505137eee57b081d84c2f1419b714b6` `docs/test-bible/core/inbox.md`

— Betty

#### joan — 2026-08-02T19:56:49.831Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1131
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 Create list paste → only real job-detail jobs; zero SVG/namespace `job_link`; also newline-delimited lists | Stages 2–3 — unescape/unwrap so xmlns is not an `a[href]`; bare-URL promote for newline lists; remaining non-job host/path gates → N/A (AST-1132) |
| AC2 Clean ATS `job_link` (no nested auto-link markup) | Stages 2–3 unwrap nested Gmail auto-links in configured attrs |
| AC3 Re-Create dedupe preserved (candidate-scoped) | N/A — boundary / existing AST-1061 path; not owned here |
| AC4 `qualify_meteorite` → QUALIFIED with title + company_job_id | N/A — boundary (AST-1133) |
| AC5 `debug=True` Style D per-link found/skipped/recorded | Stage 3 — preserve existing gazer/inbox Style D; no summary-only replacement |
| AC6 Single-link / single-JD Create still succeeds | Stage 3 Done-when + promote-only-when-no-http-anchors gate |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 Config knobs | Architectural `pattern.config.config-block` / config-source-of-truth; child In scope |
| Stage 2 `normalize_pasted_list_email_html` | Purpose/Functional scope list/paste Create hygiene; child AC clean links + xmlns not candidates + newline lists |
| Stage 3 Wire strip + ingest | Functional scope Create discovers clean hrefs; AC5/AC6; dual call sites Decision |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work in this plan |
| orch.git.commit-vocabulary | conforms | Publish on sub ref with plan()/code() vocabulary |
| orch.git.flow-direction-inviolable | conforms | Publish only to origin/sub/AST-1130/AST-1131-… |
| orch.git.ftr-sub-topology | conforms | Child ref matches parent Git table |
| orch.git.merge-on-checkout | conforms | No illegal merge recipe |
| orch.git.no-cherry-pick-rebase-force | conforms | No cherry-pick/rebase/force |
| orch.git.no-dev-agent-branches | conforms | Uses sub/AST-1130/AST-1131-… only |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree astral-AST-1130 |
| orch.git.three-permanent-branches | conforms | Does not invent permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Decisions documented; no product fork needing Archie |
| orch.pipeline.plan-is-bible | conforms | Binding stages + Files Changed present |
| orch.pipeline.project-scoped-queues | conforms | Single-child Meteorite scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate-plan gate only |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | No tests/bible edits |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Ada) owns build |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer implementer path after approve |
| orch.roles.pre-commit-path-bans | conforms | No banned-path edits |
| astral.agent.confidence-bounds | conforms | No graded consult / confidence path touched |
| astral.agent.do-task-delegation | conforms | No do_task / LLM path |
| astral.agent.grade-vector-validation | conforms | No grade vectors |
| astral.batch.batch-id-first | conforms | No batch claim helpers |
| astral.batch.batch-id-format | conforms | No batch_id generation |
| astral.batch.claim-process-release | conforms | No claim/process/release changes |
| astral.batch.entity-agent-responses-latest-only | conforms | No agent_data RESPONSE work |
| astral.config.config-source-of-truth | conforms | Paste-normalize knobs extend METEORITE_EMAIL_INGEST_CONFIG |
| astral.config.pass-threshold-vs-score-floor | conforms | No scoring thresholds |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env values |
| astral.dispatch.run-next-is-chain-authority | conforms | No dispatch/run_next changes |
| astral.dispatch.seed-auto-false | conforms | No seed/dispatch_task rows |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src; Betty excluded |
| astral.layers.core-vs-external-bright-line | conforms | Pure string normalize in utils; core wires only; no new I/O |
| astral.layers.import-direction | conforms | utils←config; core←utils; no data/external from utils |
| astral.layers.ui-config-driven-business-logic | conforms | No React rules; config consumed by core/utils |
| astral.patterns.coat-check-never-store-empty | conforms | No coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | conforms | No consult/render_verdict |
| astral.seed.agent-tables-in-repo-json | conforms | No seed JSON |
| astral.seed.archie-catalog-wins | conforms | No catalog seed |
| astral.seed.boot-only-not-hot-path | conforms | No boot seed path |
| astral.seed.define-approved | conforms | No seed define work |
| astral.seed.operator-rows-stay-deleted | conforms | No operator seed rows |
| astral.seed.other-via-coverage-join | conforms | No coverage-join seed |
| astral.standards.data-raises-caller-logs | conforms | No data-layer edits |
| astral.standards.debug-contract-gated | conforms | Preserves Style D; no ungated debug |
| astral.standards.dry-and-focused-functions | conforms | Single helper; dual thin call sites |
| astral.standards.in-scope-only | conforms | Normalize only; exclude/qualify/gaze left to siblings/boundaries |
| astral.standards.logging-via-utils | conforms | Helper pure (no log); existing gazer/inbox loggers kept |
| astral.standards.names-not-ticket-ids | conforms | Helper/config names product-shaped, not ticket ids |
| astral.standards.no-cross-contamination | conforms | Stays on email→meteorite ingest path |
| astral.standards.no-hardcoded-sets | conforms | Attr names / thresholds / promote flag in config |
| astral.standards.public-then-helpers | conforms | One public normalize helper; pipeline steps internal |
| astral.standards.utils-data-late-import-only | conforms | No utils→data import |
| astral.state.core-decides-transitions | conforms | No state transition changes; still METEORITE_NEW via existing path |
| astral.state.job-prior-states-enforced | conforms | No JOB_STATES / transition_job_state edits |
| astral.state.no-daisy-chain-in-run | conforms | No run_next / daisy-chain |
| astral.ui.single-gunicorn-worker | conforms | No gunicorn/worker config changes |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.dispatch.run-next-is-chain-authority, astral.dispatch.seed-auto-false, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.seed.agent-tables-in-repo-json, astral.seed.archie-catalog-wins, astral.seed.boot-only-not-hot-path, astral.seed.define-approved, astral.seed.operator-rows-stay-deleted, astral.seed.other-via-coverage-join, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.names-not-ticket-ids, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths match none of plan paths
- astral.debug.spikes-under-debug-dir — paths match none of plan paths
- astral.docs.features-single-file-per-ticket — layers {docs} ∩ plan {core,utils} empty
- astral.git.engineer-test-tree-ban — paths match none of plan paths
- astral.layers.scripts-exempt-from-layer-rules — layers {scripts} ∩ plan {core,utils} empty
- astral.patterns.require-auth-on-protected-endpoints — layers {ui} ∩ plan {core,utils} empty
- astral.standards.database-header-inventory — layers {data} ∩ plan {core,utils} empty
- astral.ui.frontend-file-placement — layers {ui} ∩ plan {core,utils} empty
- astral.ui.naming-conventions — layers {ui} ∩ plan {core,utils} empty

## Findings

None fix-now.

**discuss (non-blocking):** Stage 2 Step C strips a small trailing-punctuation set on bare URLs in code. Acceptable as local hygiene (not a host/policy set); engineer may lift to config if Radia later prefers zero inline sets.

**acceptable:** Self-assessment Single-Component / Conf high / Risk Medium matches blast-radius of unescape+promote; gates (marker count; promote only when no http(s) anchors) are specific. BeautifulSoup lazy-import in utils for anchor presence check is string hygiene, not new I/O.

**R6 checklist:** Definition fidelity pass for child #1 only. Layers/import pass. Config knobs in `METEORITE_EMAIL_INGEST_CONFIG`. No UI/file-placement issues. No batch/state/do_task. DRY single helper. Boundaries vs AST-1132/1133 respected.

context_tokens≈58000

— Joan

#### ada — 2026-08-02T19:54:42.664Z
Plan published on `origin/sub/AST-1130/AST-1131-normalize-pasted-list-email-html` @ `8662d9d5`.

**Plan doc:** https://github.com/susansomerset/astral/blob/sub/AST-1130/AST-1131-normalize-pasted-list-email-html/docs/features/meteorite/ast-1131-normalize-pasted-list-email-html.md

**Approach:** pure `normalize_pasted_list_email_html` in `formatting.py` (gated `html.unescape` → unwrap Gmail nested auto-links in configured attrs → promote bare http(s) URLs when no anchors remain); wire from `strip_extract_email_html` and `ingest_meteorite_jobs_from_email_html` before `_meteorite_email_candidate_links`. Knobs on `METEORITE_EMAIL_INGEST_CONFIG`. Leaves exclude-list (AST-1132) and qualify (AST-1133) alone.

**Self-assessment**
- **Scope:** Single-Component — utils config + formatting hygiene; thin inbox/gazer call sites only.
- **Conf:** high — parent UAT HTML/log shows the exact entity-escape + nested-autolink failure mode; patterns already exist in inbox/formatting.
- **Risk:** Medium — over-eager unescape/bare-URL promote could affect non-list emails; marker gate + promote-only-when-no-http-anchors limit blast radius, but a bug misroutes Create link discovery.

#### chuckles — 2026-08-02T19:51:57.557Z
[thread-orphan] Joan chat `da0027e7-276d-4fe2-a6e6-65c8eb77e24d` relocated from `/home/susan/.cursor/chats/0f41bf986cfef9e06ea903e586d6d4d9/da0027e7-276d-4fe2-a6e6-65c8eb77e24d/store.db` → `/home/susan/.cursor/chats/f83db4c242138fcc700ad43e401aac8e/da0027e7-276d-4fe2-a6e6-65c8eb77e24d/store.db`. Continuing with same UUID.

— Chuckles

#### chuckles — 2026-08-02T19:50:35.354Z
[thread-missing] Cursor chat `a9fe5bae-b2ff-462b-b9a1-6ffef1961c72` has no local `store.db` on **chuckles** (expected `/home/susan/.cursor/chats/f83db4c242138fcc700ad43e401aac8e/a9fe5bae-b2ff-462b-b9a1-6ffef1961c72/store.db`; blob-search also empty).

Minting a **new** conversation on this host and continuing (history from the old UUID is not recovered).

— Chuckles

---

# AST-1131 — Normalize pasted/list email HTML before link discovery

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1131/normalize-pastedlist-email-html-before-link-discovery-manage-email  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1130/manage-email-create-button-for-job-lists-isnt-working  

**Publish ref (origin):** `sub/AST-1130/AST-1131-normalize-pasted-list-email-html`  
**Parent integration ref:** `ftr/AST-1130-manage-email-create-button-for-job-lists-isnt-working`

Owns making Manage Email **Create** discover clean http(s) job-detail URLs from entity-escaped board pastes and Gmail-auto-linkified attribute values (and from simple newline-delimited job-link pastes) **before** `_meteorite_email_candidate_links` runs. Attribute URLs such as SVG `xmlns` must not be promoted into `<a href>` candidates; nested auto-link markup must not remain inside stored `job_link` values. Does **not** own host/path exclude-list policy or non-job create skip (AST-1132) or `qualify_meteorite` apply (AST-1133). Does not redesign `gaze_email`.

**Diagnosis (from parent Original brief):** Paste is stored as entity-escaped text (`&lt;div…`). Gmail then auto-linkifies bare URL substrings inside that text, producing nested anchors inside attribute values, e.g. `href="<a href="https://www.dice.com/job-detail/…">…</a>"` and `xmlns="<a href="http://www.w3.org/2000/svg">…</a>"`. BeautifulSoup then collects those nested anchors (including `w3.org/2000/svg`) as candidate links. Fix order: unescape → unwrap nested auto-links in attributes → promote bare newline URLs when needed → existing link discovery.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Extend `METEORITE_EMAIL_INGEST_CONFIG` with paste-normalize knobs (unescape gate, nested-autolink attrs, bare-URL promote) | utils |
| `src/utils/formatting.py` | Add pure `normalize_pasted_list_email_html(html) -> str` (unescape + unwrap + bare-URL promote) | utils |
| `src/core/inbox.py` | Call normalize on the culled body inside `strip_extract_email_html` before subject wrap | core |
| `src/core/gazer.py` | Call normalize at start of `ingest_meteorite_jobs_from_email_html` before `_meteorite_email_candidate_links`; keep existing Style D per-link logging | core |

No UI, API, Playwright, qualify, exclude-list, or `tests/` / bible changes.

---

## Stage 1: Config knobs for paste normalize

**Done when:** `METEORITE_EMAIL_INGEST_CONFIG` exposes the keys below as importable literals; no formatting/core behavior changes yet.

1. In `src/utils/config.py`, inside the existing `METEORITE_EMAIL_INGEST_CONFIG` dict (after `min_jd_chars`), add:

```python
    # AST-1131: normalize entity-escaped / Gmail-auto-linkified list pastes before link discovery.
    # Unescape only when the body looks entity-escaped (count of marker ≥ threshold).
    "entity_unescape_marker": "&lt;",
    "entity_unescape_min_marker_count": 2,
    "entity_unescape_max_passes": 3,
    # Attribute names whose values may contain nested Gmail auto-link HTML; unwrap to bare URL.
    "nested_autolink_attr_names": ("href", "xmlns", "src", "cite", "data-url"),
    # When True and no http(s) <a href> remain after unwrap, wrap bare http(s) URLs as anchors
    # so newline-delimited link lists enter links mode (not Dice-exclusive).
    "promote_bare_http_urls": True,
```

2. If the top-of-file config inventory lists `METEORITE_EMAIL_INGEST_CONFIG`, extend that one-liner to mention AST-1131 paste normalize.

⚠️ **Decision — extend ingest config, not a new block:** Parent architectural definition says extend `METEORITE_EMAIL_INGEST_CONFIG`. Keeps thresholds next to link discovery knobs; no second config island.

⚠️ **Decision — marker-gated unescape:** Blind `html.unescape` on every email would rewrite legitimate `&amp;` entities. Gate on `&lt;` count so only pasted-as-text board HTML triggers multi-pass unescape.

---

## Stage 2: Pure normalize helper in formatting

**Done when:** `normalize_pasted_list_email_html` is importable from `src.utils.formatting`, is pure (no logging, no I/O), and transforms the three shapes below as specified; no inbox/gazer wiring yet.

1. In `src/utils/formatting.py`, near `normalize_link` / other URL helpers, add:

```python
def normalize_pasted_list_email_html(html: str) -> str:
    """Unescape entity-escaped board pastes, unwrap Gmail nested auto-links in attrs,
    and optionally promote bare http(s) URLs to anchors for link discovery.

    Reads METEORITE_EMAIL_INGEST_CONFIG. Idempotent for already-clean HTML.
    """
```

2. Implement exactly this pipeline (use `import html as html_module` and `import re`; import `METEORITE_EMAIL_INGEST_CONFIG` from `src.utils.config` at function top or module top — match file’s existing import style):

**Step A — entity unescape (gated):**  
- `text = html or ""`.  
- `marker = METEORITE_EMAIL_INGEST_CONFIG["entity_unescape_marker"]`.  
- `min_count = int(METEORITE_EMAIL_INGEST_CONFIG["entity_unescape_min_marker_count"])`.  
- `max_passes = int(METEORITE_EMAIL_INGEST_CONFIG["entity_unescape_max_passes"])`.  
- If `text.count(marker) >= min_count`: for `_ in range(max_passes)`, set `nxt = html_module.unescape(text)`; break when `nxt == text`; else `text = nxt`.

**Step B — unwrap nested Gmail auto-links inside attribute values:**  
For each `attr` in `METEORITE_EMAIL_INGEST_CONFIG["nested_autolink_attr_names"]`, apply a case-insensitive regex replace that turns attribute values whose entire value is a nested anchor into the bare URL.

Concrete pattern (compile once per attr, `re.IGNORECASE | re.DOTALL`):

```text
(?P<prefix>\b{attr}\s*=\s*)(?P<q>["'])\s*<a\b[^>]*\bhref\s*=\s*(?P<q2>["'])(?P<url>https?://[^"']+)(?P=q2)[^>]*>.*?</a>\s*(?P=q)
```

Replacement: `\g<prefix>\g<q>\g<url>\g<q>`  
(Use `attr` interpolated with `re.escape(attr)`.)

Also handle the UAT double-quote breakage form where the outer attribute quote is effectively broken by an inner `href="…"` — after Step A the parent brief shows:

```text
href="<a href="https://www.dice.com/job-detail/UUID">https://www.dice.com/job-detail/UUID</a>"
```

Add a second pass regex (attr-agnostic, applied once after the per-attr loop):

```text
(?P<prefix>\b(?:href|xmlns|src|cite|data-url)\s*=\s*)"\s*<a\b[^>]*\bhref\s*=\s*"(?P<url>https?://[^"]+)"[^>]*>\s*(?P=url)\s*</a>\s*"
```

Replacement: `\g<prefix>"\g<url>"`  
(Build the attr alternation from the same config tuple via `|`.join(`re.escape(a)` for a in nested_autolink_attr_names).)

Do **not** invent vendor-specific Dice path rules here.

**Step C — promote bare http(s) URLs when configured:**  
- If `METEORITE_EMAIL_INGEST_CONFIG["promote_bare_http_urls"]` is false → return `text`.  
- Lazy-import BeautifulSoup only for this check (B1). Parse `text`; if any `a[href]` has `urlparse(href).scheme.casefold()` in `METEORITE_EMAIL_INGEST_CONFIG["link_schemes"]`, return `text` unchanged (board HTML / already-linked email).  
- Otherwise find bare URLs with:

```python
_BARE_URL_RE = re.compile(r"(?P<url>https?://[^\s<>\"']+)", re.IGNORECASE)
```

For each unique URL in first-seen order, if that exact URL string is not already present as an `href="URL"` / `href='URL'` substring, append:

```html
<a href="{url}">{url}</a>
```

joined by `\n` after the original `text` (preserve original text; append promoted anchors so `_meteorite_email_candidate_links` can see them). Strip trailing punctuation commonly stuck to bare URLs (`,`, `.`, `;`, `)`, `]`) from the captured URL before wrapping — strip only from the URL used in `href` and link text, leave the original text as-is.

3. Return `text`.

⚠️ **Decision — pure utils, not core:** Unescape/unwrap/promote is string hygiene with no entity/state decisions. Core stays orchestration; matches `astral.layers.core-vs-external-bright-line` (no new I/O) and keeps the helper reusable/testable without inbox.

⚠️ **Decision — append bare anchors rather than rewrite the whole body:** Avoids destroying JD prose when a forward email has zero anchors but also has narrative URLs later filtered by AST-1132. For a pure newline list, append is equivalent to wrapping.

**Done when (recheck):** Calling the helper on (1) the parent brief’s entity-escaped + nested-autolink fragment yields clean `href="https://www.dice.com/job-detail/…"` with **no** nested `<a>` inside attributes and **no** standalone `xmlns` auto-link left as the only representation of the SVG URL; (2) `"https://example.com/a\nhttps://example.com/b"` yields those URLs as `a[href]` candidates after promote; (3) a normal single-JD HTML body with real anchors is unchanged aside from optional no-op passes.

---

## Stage 3: Wire normalize into strip + ingest

**Done when:** Manage Email Create on the UAT-shaped paste discovers clean Dice (or equivalent) job-detail hrefs; `job_link` values stored for created rows are bare http(s) URLs with no nested auto-link markup; SVG/`xmlns` URLs are not collected as `a[href]` candidates after normalize; newline-delimited link pastes enter `mode=links`; existing Style D per-link `gazer.meteorite_email_ingest` found/skipped/recorded lines still fire when `debug=True`; single-link / single-JD Create that already worked still works.

1. In `src/core/inbox.py`, import `normalize_pasted_list_email_html` from `src.utils.formatting`. Inside `strip_extract_email_html`, after computing `body` from the culled soup (`soup.body.decode_contents()` / `soup.decode_contents()`) and **before** the subject template `.format(...)`, set:

```python
body = normalize_pasted_list_email_html(body)
```

Do not change strip tag/attr cull behavior. Subject wrap stays identical.

2. In `src/core/gazer.py`, import `normalize_pasted_list_email_html` from `src.utils.formatting`. At the top of `ingest_meteorite_jobs_from_email_html`, after the empty-html `ValueError` guard and before `links = _meteorite_email_candidate_links(html)`, set:

```python
html = normalize_pasted_list_email_html(html)
```

Use the normalized `html` for both links mode and body mode (including `_meteorite_email_body_text` / JD payload). Do **not** change `_meteorite_email_candidate_links` exclude-substring logic, Playwright fetch, dedupe, or create — those remain AST-1061 / AST-1132 territory.

3. Preserve existing Style D contract on `gazer.meteorite_email_ingest` and `inbox_create_job` (found / matched / extracted / recorded). Do **not** add summary-only logging that replaces per-link headers. Optional one-line detail under `inbox_create_job` `extracted` is allowed (`normalized_html_len=…`) but not required; if added, gate with `debug=True` only.

4. Do **not** add Dice-only host allowlists, `w3.org` excludes, or “is this a job page?” Playwright heuristics — AST-1132.

⚠️ **Decision — normalize in both strip and ingest:** Strip-first makes the Manage Email debug `extracted` dump show real markup (operator-visible). Ingest-first keeps the gate at the link-discovery boundary if another caller ever feeds HTML without strip. Helper is idempotent so double-call is safe.

⚠️ **Decision — leave relative `/company/…` anchors alone:** After unescape, Dice company profile links remain relative and fail the existing `link_schemes` http(s) filter. Non-job absolute hosts that survive normalize are AST-1132’s exclude policy, not this ticket.

**Done when (recheck):**  
- Replaying the parent UAT paste shape through strip → ingest yields candidate links whose URLs equal clean `https://www.dice.com/job-detail/<uuid>` strings (no nested `<a>` markup inside the URL).  
- `http://www.w3.org/2000/svg` / `https://www.w3.org/2000/svg` does **not** appear in `_meteorite_email_candidate_links` output after normalize (attribute restored; not an anchor).  
- A body of two newline-separated https job URLs runs `mode=links` with those two URLs.  
- A single absolute job-link email and a body-only JD email still create as before.  
- `python3 -m py_compile` on the four touched files succeeds; no new lint issues in those files.

---

## Self-Assessment

**Scope:** `Single-Component` — utils config + formatting hygiene plus thin inbox/gazer call sites on the existing email→meteorite ingest path; no UI/API/qualify changes.

**Conf:** `high` — failure mode is fully diagnosed in the parent UAT HTML/log (entity-escape + nested Gmail auto-links); fix reuses BeautifulSoup/`html.unescape` patterns already in inbox/formatting.

**Risk:** `Medium` — over-eager unescape or bare-URL promote could alter non-list emails; marker gate + “promote only when no http(s) anchors” keep the blast radius small, but a bug here would mis-route Create link discovery.

---

## Rules self-review

| Rule | Status |
|------|--------|
| §1.3 DRY | Normalize once in formatting; inbox + gazer only call it |
| §1.4 / §2.1 config | Unescape thresholds, attr names, promote flag live in `METEORITE_EMAIL_INGEST_CONFIG` — no inline magic sets in core |
| §1.5.1 debug | Existing Style D on ingest preserved; no new ungated debug lines |
| §2.5 / §3.3 layers | Pure string helper in utils; core orchestrates; no external/data imports from utils beyond existing config |
| §2.4 batch / §2.6 state | Untouched — create still lands METEORITE_NEW via existing path |
| Boundaries | No exclude-list (AST-1132), no qualify (AST-1133), no gaze_email redesign |

---

## Review (build stub)

**Publish ref:** `origin/sub/AST-1130/AST-1131-normalize-pasted-list-email-html`
**Plan path:** `docs/features/meteorite/ast-1131-normalize-pasted-list-email-html.md`
**Built tip:** `3ba80bae7a2584e72ae6a10652137608f4f02443` (`3ba80bae`)

| Stage | Commit | Summary |
|-------|--------|---------|
| 1–3 | `3ba80bae` | Config knobs + `normalize_pasted_list_email_html` + strip/ingest wire |

---

## Radia review (code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1131
**Publish ref tip:** `01efc3717b06be9b44cca18a3ff5e60f12ab1a1b`
**Overall:** DISCUSS

### What’s solid

- Stages 1–3 match the three-dot diff: config knobs, pure `normalize_pasted_list_email_html`, thin strip + ingest wires.
- Unescape gate / nested-autolink attrs / promote flag live in `METEORITE_EMAIL_INGEST_CONFIG`; late config + BeautifulSoup imports are comment-justified (cycle / B1).
- Style D on `gazer.meteorite_email_ingest` preserved; no new ungated debug; AST-1132/1133 boundaries held.
- Betty `test()` + one `merge-tests` SHA; engineer `code()` is src-only.

### Issues

**discuss (C4 straggler):** `astral.debug.spikes-under-debug-dir` — Joan excluded; diff touches `docs/features/**`. Scores **conforms** (combined plan, not spike notes). No product action.

**discuss (C4 straggler):** `astral.docs.features-single-file-per-ticket` — Joan excluded; plan file landed. Scores **conforms**. No product action.

**discuss (C4 straggler):** `astral.git.engineer-test-tree-ban` — Joan excluded; `tests/**` + bible in tip via Betty. Scores **conforms** (`code()` src-only). No product action.

### Recommended actions

- Engineer: ack the three C4 stragglers (no src change required for them) via `resolve-child`, then move to User Testing.
- Trailing bare-URL punctuation stays a documented module constant (Joan plan discuss already accepted as local hygiene).

### Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | conforms | No graded consult / confidence path |
| `astral.agent.do-task-delegation` | scoped | conforms | No do_task / LLM path |
| `astral.agent.grade-vector-validation` | scoped | conforms | No grade vectors |
| `astral.batch.batch-id-first` | scoped | conforms | No batch claim helpers |
| `astral.batch.batch-id-format` | scoped | conforms | No batch_id generation |
| `astral.batch.claim-process-release` | scoped | conforms | No claim/process/release changes |
| `astral.batch.entity-agent-responses-latest-only` | scoped | conforms | No agent_data RESPONSE work |
| `astral.config.config-source-of-truth` | scoped | conforms | Paste knobs extend METEORITE_EMAIL_INGEST_CONFIG |
| `astral.config.pass-threshold-vs-score-floor` | scoped | conforms | No scoring thresholds |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | conforms | No secrets/env values |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | paths miss diff (['artifacts/**', 'scripts/spikes/**']) |
| `astral.debug.spikes-under-debug-dir` | scoped | conforms | Combined plan under docs/features — not spike notes |
| `astral.dispatch.run-next-is-chain-authority` | scoped | conforms | No dispatch/run_next changes |
| `astral.dispatch.seed-auto-false` | scoped | conforms | No seed/dispatch_task rows |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | One docs/features/meteorite/ast-1131-… plan file |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty test/bible only; merge-tests exception ok |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | code() commit is src-only; tests from Betty |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | Pure string normalize in utils; core wires only |
| `astral.layers.import-direction` | scoped | conforms | utils←config late; core←utils; no data/external |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | layers ∩ diff empty (['scripts']); paths miss diff (['scripts/**']) |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | No UI rules; config consumed by utils/core |
| `astral.patterns.coat-check-never-store-empty` | scoped | conforms | No coat-check keys |
| `astral.patterns.render-verdict-orchestrates-consult` | scoped | conforms | No consult/render_verdict |
| `astral.patterns.require-auth-on-protected-endpoints` | scoped | not-applicable | layers ∩ diff empty (['ui']); paths miss diff (['src/ui/**']) |
| `astral.seed.agent-tables-in-repo-json` | scoped | conforms | No seed JSON |
| `astral.seed.archie-catalog-wins` | scoped | conforms | No catalog seed |
| `astral.seed.boot-only-not-hot-path` | scoped | conforms | No boot seed path |
| `astral.seed.define-approved` | scoped | conforms | No seed define work |
| `astral.seed.operator-rows-stay-deleted` | scoped | conforms | No operator seed rows |
| `astral.seed.other-via-coverage-join` | scoped | conforms | No coverage-join seed |
| `astral.standards.data-raises-caller-logs` | scoped | conforms | No data-layer edits |
| `astral.standards.database-header-inventory` | scoped | not-applicable | layers ∩ diff empty (['data']); paths miss diff (['src/data/**']) |
| `astral.standards.debug-contract-gated` | scoped | conforms | Style D preserved; no ungated debug added |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | Single helper; dual thin call sites |
| `astral.standards.in-scope-only` | scoped | conforms | Normalize only; exclude/qualify untouched |
| `astral.standards.logging-via-utils` | scoped | conforms | Helper pure; gazer/inbox loggers unchanged |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | normalize_pasted_list_email_html domain-named |
| `astral.standards.no-cross-contamination` | scoped | conforms | Stays on email→meteorite ingest path |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | Attr/thresholds/promote in config; trail punct module const |
| `astral.standards.public-then-helpers` | scoped | conforms | Public helper + local regex constants colocated |
| `astral.standards.utils-data-late-import-only` | scoped | conforms | No utils→data import |
| `astral.state.core-decides-transitions` | scoped | conforms | Still METEORITE_NEW via existing create path |
| `astral.state.job-prior-states-enforced` | scoped | conforms | No JOB_STATES / transition edits |
| `astral.state.no-daisy-chain-in-run` | scoped | conforms | No run_next / daisy-chain |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | layers ∩ diff empty (['ui']); paths miss diff (['src/ui/frontend/**']) |
| `astral.ui.naming-conventions` | scoped | not-applicable | layers ∩ diff empty (['ui']); paths miss diff (['src/ui/**']) |
| `astral.ui.single-gunicorn-worker` | scoped | conforms | config.py paste knobs only; no worker changes |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | Single merge-tests(AST-1131) SHA on sub tip |
| `orch.git.commit-vocabulary` | universal | conforms | plan/code/docs/test/merge-tests vocabulary only |
| `orch.git.flow-direction-inviolable` | universal | conforms | Publish stays on origin/sub/AST-1130/AST-1131-… |
| `orch.git.ftr-sub-topology` | universal | conforms | Child sub under AST-1130 parent topology |
| `orch.git.merge-on-checkout` | universal | conforms | No illegal merge-on-checkout recipe in commits |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | No cherry-pick/rebase/force on publish ref |
| `orch.git.no-dev-agent-branches` | universal | conforms | Uses sub/AST-1130/AST-1131-… only |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | Review in astral-AST-1130 epic worktree |
| `orch.git.three-permanent-branches` | universal | conforms | No new permanent branch invented |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | No product-decision fork; plan decisions shipped |
| `orch.pipeline.plan-is-bible` | universal | conforms | Stages 1–3 match Files Changed and diff |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Astral Meteorite child only |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Entered at Tests Passed |
| `orch.roles.archie-approves-statutes` | universal | conforms | No canon/statutes edits |
| `orch.roles.betty-owns-test-tree` | universal | conforms | tests/bible via test()+merge-tests only |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | Assignee remains Ada |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Implementer stays assignee through review |
| `orch.roles.pre-commit-path-bans` | universal | conforms | No banned-path product commits |

### Pattern conformance

- `pattern.config.config-block` — **conforms** (extend `METEORITE_EMAIL_INGEST_CONFIG`)
- Other Linear In-scope citations are active statutes covered above

### Plan adherence

Diff footprint matches Self-Assessment **Single-Component** (utils config + formatting + thin inbox/gazer wires). No exclude-list / qualify / gaze_email / UI smuggle from AST-1132/1133.

context_tokens≈42000

---

## Resolution

**Date:** 2026-08-02  
**Resolve tip:** see `resolve(AST-1131): — clean` on `origin/sub/AST-1130/AST-1131-normalize-pasted-list-email-html`

| Radia item | Disposition |
|------------|-------------|
| fix-now | none |
| discuss (C4 straggler) `astral.debug.spikes-under-debug-dir` | Ack — conforms; plan doc under `docs/features/`, not spike notes. No product change. |
| discuss (C4 straggler) `astral.docs.features-single-file-per-ticket` | Ack — conforms; single combined plan file. No product change. |
| discuss (C4 straggler) `astral.git.engineer-test-tree-ban` | Ack — conforms; `code()` was src-only; tests via Betty. No product change. |
| Trailing bare-URL punctuation module constant | Leave as local hygiene (Joan plan discuss already accepted; Radia Notes concur). |

No product or test-tree edits in resolve.
