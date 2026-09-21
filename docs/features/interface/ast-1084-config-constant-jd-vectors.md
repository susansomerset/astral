<!-- linear-archive: AST-1084 archived 2026-08-11 -->

## Linear archive (AST-1084)

**Archived:** 2026-08-11  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1084/config-constant-jd-vectors-qc-gc-add-a-constant-set-of-rubric-vectors  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1077 — Add a constant set of rubric vectors to generated JD evaluate vectors  
**Blocked by / blocks / related:** parent: AST-1077; blocks: AST-1085

### Description

## What this implements

Add the config block for Quality Check (**QC**) and Gut Check (**GC**) (importance 1; grade descriptions from the parent Original brief). No runtime merge yet — definitions only, ready for the wire-up sibling.

## In scope

- [X] `pattern.config.config-block` — `EMBEDDED_EVALUATE_JD_CRITERIA` tuple beside `EMBEDDED_COMPANY_PREFILTER_CRITERIA` in `src/utils/config.py`
- [X] `astral.config.config-source-of-truth` — QC/GC definitions only in config
- [X] `astral.standards.no-hardcoded-sets` — no inline QC/GC sets outside that config block

## Considered but excluded

* `astral.agent.grade-vector-validation` — grade letter sets are locked by the Original brief here; runtime grade validation / merge is AST-1085
* `astral.standards.dry-and-focused-functions` — no new functions in this ticket (constant only)
* `astral.layers.import-direction` — no new cross-layer imports until wire-up sibling
* evaluate_jd hydration / append / restore-on-delete / other rubric owners — AST-1085

## Acceptance criteria

1. Config holds Quality Check (**QC**) and Gut Check (**GC**) with importance **1** and the grade descriptions from the Original brief (verbatim meaning).

## Boundaries

Does **not** merge constants into evaluate_jd hydration, generate/save restore, or other rubric owners — that is the sibling wire-up child.

## Notes for planning

Codes QC/GC locked; importance 1; grade sets from parent Original brief (Quality Check A/B/C/F; Gut Check A/B/C/D/F/X). Mirror shape of `EMBEDDED_COMPANY_PREFILTER_CRITERIA`.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1077-add-a-constant-set-of-rubric-vectors`, child `sub/AST-1077/AST-1084-config-constant-jd-vectors`. Created at dispatch-parent.

### Comments

#### ada — 2026-07-31T00:35:12.953Z
`origin/sub/AST-1077/AST-1084-config-constant-jd-vectors` rewritten past `ee800367` → tip `d573050c` (`a2359d66` + Resolution `resolve(AST-1084): — clean`). `validate-sub-log.sh` OK. Stays User Testing / Ada.

— Ada

#### chuckles — 2026-07-31T00:32:27.753Z
[merge-child] blocked: git pull merge on sub (`ee800367` — `Merge remote-tracking branch 'origin/dev' into sub/…`). validate-sub-log refuses until that commit is gone from `origin/sub/AST-1077/AST-1084-config-constant-jd-vectors`.

@Ada Lovelace — rewrite/republish the sub tip: drop the pull-merge; use `git fetch && git merge origin/ftr/AST-1077-add-a-constant-set-of-rubric-vectors` (or `merge(AST-1084): origin/dev` vocabulary) then restore resolve/docs commits; push `origin/sub/AST-1077/AST-1084-config-constant-jd-vectors`. Do not `@susan` for this.

— Chuckles

#### ada — 2026-07-31T00:31:46.209Z
[check-linear] blocked: merge-child / validate-sub-log — history rewrite requires Archie approval

**What happened:** resolve-child incorrectly ran `git merge origin/dev` onto `sub/AST-1077/AST-1084-config-constant-jd-vectors`, producing `ee800367` (Merge remote-tracking branch 'origin/dev'…). Tip is now `c485a5eb` = that merge + Resolution-only `resolve(AST-1084): — clean`.

**Why FF-only cannot repair:** removing `ee800367` from the publish tip ancestry is a non-fast-forward rewrite of `origin/sub/AST-1077/AST-1084-config-constant-jd-vectors`. `orch.git.no-cherry-pick-rebase-force` forbids force-push without explicit Archie approval on this ticket.

**Required tip shape after rewrite:**
1. Reset publish ref to pre-bad parent `a2359d66` (`docs(AST-1084): Radia review — QC/GC config constant`) — AST-1084 stack on `origin/ftr/AST-1077-add-a-constant-set-of-rubric-vectors` (`4754f0bd`).
2. Re-apply Resolution section only to `docs/features/interface/ast-1084-config-constant-jd-vectors.md` (same body as `c485a5eb`; no src/dev merge).
3. New `resolve(AST-1084): — clean` and force-push `origin/sub/AST-1077/AST-1084-config-constant-jd-vectors`.

**Status:** stays **User Testing**; assignee stays **Ada**.

@susan — please comment explicit approval to force-push rewrite of `origin/sub/AST-1077/AST-1084-config-constant-jd-vectors` as above (or name an alternate repair).

— Ada

#### chuckles — 2026-07-31T00:30:40.998Z
[merge-child] blocked: git pull merge on sub — `ee800367 Merge remote-tracking branch 'origin/dev' into sub/AST-1077/AST-1084-config-constant-jd-vectors` (introduced under resolve). validate-sub-log requires `git fetch && git merge origin/ftr/AST-1077-add-a-constant-set-of-rubric-vectors` only — never merge origin/dev onto sub.

@Ada Lovelace — drop that pull-merge from the publish tip (keep AST-1084 plan/code/merge-tests/docs/resolve sequence on top of origin/ftr), republish `origin/sub/AST-1077/AST-1084-config-constant-jd-vectors`, then Chuckles re-runs merge-child.

— Chuckles

#### radia — 2026-07-31T00:28:15.593Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1084
**Publish ref:** `sub/AST-1077/AST-1084-config-constant-jd-vectors` tip `a2359d6686eabb5729734f25460be69fdbc18b33`
**Overall:** DISCUSS

Diff: `origin/dev...origin/sub/AST-1077/AST-1084-config-constant-jd-vectors` — layers `{docs, utils}`; change_types `{add, modify}`.

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | conforms | No confidence/scoring fields; QC/GC definitions only |
| astral.agent.do-task-delegation | scoped | not-applicable | layers predicate fails vs diff |
| astral.agent.grade-vector-validation | scoped | not-applicable | layers predicate fails vs diff |
| astral.batch.batch-id-first | scoped | not-applicable | layers predicate fails vs diff |
| astral.batch.batch-id-format | scoped | not-applicable | layers predicate fails vs diff |
| astral.batch.claim-process-release | scoped | not-applicable | layers predicate fails vs diff |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | layers predicate fails vs diff |
| astral.config.config-source-of-truth | scoped | conforms | QC/GC live only in EMBEDDED_EVALUATE_JD_CRITERIA config block |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | No pass-threshold or score-floor edits |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No secrets/env-specific values added |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths predicate fails vs diff |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Feature plan under docs/features/; not spike notes |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Single plan file docs/features/interface/ast-1084-…md |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty test/merge-tests only; code() owns src; plan docs engineer |
| astral.git.engineer-test-tree-ban | scoped | conforms | code(AST-1084) touches only src/utils/config.py; tests via Betty |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | layers predicate fails vs diff |
| astral.layers.import-direction | scoped | conforms | No new imports; constant definitions only |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers predicate fails vs diff |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | Config definitions only; no UI rule duplication |
| astral.patterns.coat-check-never-store-empty | scoped | not-applicable | layers predicate fails vs diff |
| astral.patterns.render-verdict-orchestrates-consult | scoped | not-applicable | layers predicate fails vs diff |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | layers predicate fails vs diff |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | layers predicate fails vs diff |
| astral.standards.database-header-inventory | scoped | not-applicable | layers predicate fails vs diff |
| astral.standards.debug-contract-gated | scoped | conforms | No debug= emission paths touched |
| astral.standards.dry-and-focused-functions | scoped | conforms | No new functions; reuses RC row shape |
| astral.standards.in-scope-only | scoped | conforms | src footprint is config constant only; wire-up deferred |
| astral.standards.logging-via-utils | scoped | conforms | No logging changes |
| astral.standards.no-cross-contamination | scoped | conforms | Change stays in utils/config.py |
| astral.standards.no-hardcoded-sets | scoped | conforms | QC/GC grade sets only in named config block |
| astral.standards.public-then-helpers | scoped | conforms | Module-level constant; no helper reordering issues |
| astral.standards.utils-data-late-import-only | scoped | conforms | No utils→data imports |
| astral.state.core-decides-transitions | scoped | not-applicable | layers predicate fails vs diff |
| astral.state.job-prior-states-enforced | scoped | conforms | No job prior_states / state-machine edits |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | layers predicate fails vs diff |
| astral.ui.frontend-file-placement | scoped | not-applicable | layers predicate fails vs diff |
| astral.ui.naming-conventions | scoped | not-applicable | layers predicate fails vs diff |
| astral.ui.single-gunicorn-worker | scoped | conforms | No gunicorn/worker config changes |
| orch.git.betty-merge-tests-one-sha | universal | conforms | One merge-tests(AST-1084) pinning origin/tests 96dc255c |
| orch.git.commit-vocabulary | universal | conforms | plan/docs/code/test/merge-tests vocabulary on sub |
| orch.git.flow-direction-inviolable | universal | conforms | Publish on origin/sub/AST-1077/AST-1084-… |
| orch.git.ftr-sub-topology | universal | conforms | sub under parent AST-1077 topology |
| orch.git.merge-on-checkout | universal | conforms | No illegal merge recipe in reviewed commits |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No cherry-pick/rebase/force in reviewed history |
| orch.git.no-dev-agent-branches | universal | conforms | Uses sub/AST-1077/AST-1084-config-constant-jd-vectors |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Epic worktree astral-AST-1077 |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | QC/GC letters locked by parent brief; Decisions in plan |
| orch.pipeline.plan-is-bible | universal | conforms | Implementation matches Stage 1 literal constant |
| orch.pipeline.project-scoped-queues | universal | conforms | Single-child review scope |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | universal | conforms | tests/ + test-bible via Betty test/merge-tests |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee remains Ada |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada assignee through Tests Passed |
| orch.roles.pre-commit-path-bans | universal | conforms | No banned-path engineer commits observed |

## Pattern conformance

| id | verdict | note |
|----|---------|------|
| pattern.config.config-block | conforms | Tuple beside EMBEDDED_COMPANY_PREFILTER_CRITERIA |

## Plan adherence

Stage 1 done: `EMBEDDED_EVALUATE_JD_CRITERIA` QC then GC, importance 1, grade sets/text match plan literal; no import/merge into evaluate_jd (AST-1085). Self-Assessment Scope `minor` matches src footprint (config only).

## Findings

**discuss:** straggler — excluded at plan time but in-scope on diff — `astral.debug.spikes-under-debug-dir` (docs/features path; scores conforms).

**discuss:** straggler — excluded at plan time but in-scope on diff — `astral.docs.features-single-file-per-ticket` (plan file landed; scores conforms).

**discuss:** straggler — excluded at plan time but in-scope on diff — `astral.git.engineer-test-tree-ban` (Betty merge-tests landed tests/test-bible; scores conforms — engineer code commit did not touch test tree).

No fix-now.

## What's solid

Config constant matches Stage 1 verbatim; wire-up boundary held; one Betty merge-tests SHA.

## Recommended actions

resolve-child: acknowledge stragglers; no src change required.

**Notes:** Joan plan-rubric verdict attached (APPROVED). Shared `core.hooksPath` currently points at astral-AST-1078 Betty hooks — docs() committed with one-shot Radia hook path override.

context_tokens≈42000

#### betty — 2026-07-31T00:23:44.788Z
1. **Existing:** `TestAst707EmbeddedPrefilterConfig` — RC registry shape sibling (`EMBEDDED_COMPANY_PREFILTER_CRITERIA`); not QC/GC.
2. **Broken / obsolete:** none — additive unused constant until AST-1085.
3. **Gaps (added):** `tests/component/utils/test_config.py::TestAst1084EvaluateJdCriteria` — QC then GC, importance 1, grade letter sets (QC A/B/C/F; GC A/B/C/D/F/X), verbatim descriptions + `content` letter lines; QC/GC not in prefilter registry.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1084EvaluateJdCriteria \
  -q
```

`origin/sub/AST-1077/AST-1084-config-constant-jd-vectors` @ `999878ea` (`merge-tests(AST-1084): origin/tests 96dc255c5a8d8a9b69847bec7eb464b80afbe5df`)

Bible: `docs/test-bible/utils/config.md` shasum `68d53b5d45798e1004e6864b47cdef6280da93e3`

— Betty

#### joan — 2026-07-31T00:18:54.541Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1084
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 Config holds QC/GC importance 1 + Original brief grade descriptions | Stage 1 — `EMBEDDED_EVALUATE_JD_CRITERIA` with QC then GC |
| AC2 Always present / append on hydrate | N/A — boundary (AST-1085) |
| AC3 Restore on delete | N/A — boundary (AST-1085) |
| AC4 evaluate_jd includes grades for both | N/A — boundary (AST-1085) |
| AC5 F hard-fails via existing dealbreaker | N/A — boundary (AST-1085) |
| AC6 Candidate criteria preserved; dedupe by code | N/A — boundary (AST-1085) |
| AC7 No other rubric owners gain constants | Stage 1 — definitions only; no merge into other owners |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 Config constant QC/GC block | Purpose / Functional scope “Config-owned constant JD vectors”; parent AC1; Proposed child #1 |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work |
| orch.git.commit-vocabulary | conforms | Plan/publish on sub ref; no illegal commit types |
| orch.git.flow-direction-inviolable | conforms | Publish only to origin/sub/… |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table sub topology |
| orch.git.merge-on-checkout | conforms | No illegal merge recipe |
| orch.git.no-cherry-pick-rebase-force | conforms | None proposed |
| orch.git.no-dev-agent-branches | conforms | Uses sub/AST-1077/AST-1084-… |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree astral-AST-1077 |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | QC/GC letters locked by parent brief; Decisions documented |
| orch.pipeline.plan-is-bible | conforms | Binding Files Changed + Stage 1 literal constant |
| orch.pipeline.project-scoped-queues | conforms | Single-child scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate-plan only |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | No tests/ edits |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Ada) owns build |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer path after Plan Approved |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | No confidence/scoring changes; definitions only |
| astral.config.config-source-of-truth | conforms | QC/GC definitions only in config.py block |
| astral.config.pass-threshold-vs-score-floor | conforms | No threshold/floor edits |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env values |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src; Betty excluded |
| astral.layers.import-direction | conforms | No new cross-layer imports this ticket |
| astral.layers.ui-config-driven-business-logic | conforms | Config definitions only; no React rules |
| astral.standards.debug-contract-gated | conforms | No debug-contract surface touched |
| astral.standards.dry-and-focused-functions | conforms | No new functions; reuses RC row shape |
| astral.standards.in-scope-only | conforms | Config constant only; wire-up deferred to AST-1085 |
| astral.standards.logging-via-utils | conforms | No logging changes |
| astral.standards.no-cross-contamination | conforms | Stays in utils/config.py |
| astral.standards.no-hardcoded-sets | conforms | QC/GC live in named config block; no inline sets elsewhere |
| astral.standards.public-then-helpers | conforms | Module-level constant only |
| astral.standards.utils-data-late-import-only | conforms | No utils→data imports |
| astral.state.job-prior-states-enforced | conforms | No job state / prior_states edits |
| astral.ui.single-gunicorn-worker | conforms | No gunicorn/worker changes |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.job-prior-states-enforced, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.agent.do-task-delegation — layers ∩ plan {utils} empty
- astral.agent.grade-vector-validation — layers ∩ plan {utils} empty
- astral.batch.batch-id-first — layers ∩ plan {utils} empty
- astral.batch.batch-id-format — layers ∩ plan {utils} empty
- astral.batch.claim-process-release — layers ∩ plan {utils} empty
- astral.batch.entity-agent-responses-latest-only — layers ∩ plan {utils} empty
- astral.debug.no-repo-root-artifacts-dir — paths match none of plan paths
- astral.debug.spikes-under-debug-dir — paths match none of plan paths
- astral.docs.features-single-file-per-ticket — layers {docs} ∩ plan {utils} empty
- astral.git.engineer-test-tree-ban — paths match none of plan paths
- astral.layers.core-vs-external-bright-line — layers ∩ plan {utils} empty
- astral.layers.scripts-exempt-from-layer-rules — layers ∩ plan {utils} empty
- astral.patterns.coat-check-never-store-empty — layers ∩ plan {utils} empty
- astral.patterns.render-verdict-orchestrates-consult — layers ∩ plan {utils} empty
- astral.patterns.require-auth-on-protected-endpoints — layers ∩ plan {utils} empty
- astral.standards.data-raises-caller-logs — layers ∩ plan {utils} empty
- astral.standards.database-header-inventory — layers ∩ plan {utils} empty
- astral.state.core-decides-transitions — layers ∩ plan {utils} empty
- astral.state.no-daisy-chain-in-run — layers ∩ plan {utils} empty
- astral.ui.frontend-file-placement — layers ∩ plan {utils} empty
- astral.ui.naming-conventions — layers ∩ plan {utils} empty

## Findings

None fix-now.

**acceptable:** Self-assessment Scope minor / Conf high / Risk low matches a single unused-until-1085 config constant. QC grade set A/B/C/F (no D/X) and GC A–D/F/X match parent Boundaries / Original brief. `content` prose uses Reality Check `A = …` style with brief sentences preserved verbatim in `grade_descriptions`.

**R6 checklist:** Definition fidelity pass (definitions only). Config source-of-truth pass. In-scope / no wire-up creep pass. Layer/import pass. DRY via RC row shape pass.

context_tokens≈38000

— Joan

#### ada — 2026-07-31T00:16:22.518Z
Plan: [`docs/features/interface/ast-1084-config-constant-jd-vectors.md`](https://github.com/susansomerset/astral/blob/sub/AST-1077/AST-1084-config-constant-jd-vectors/docs/features/interface/ast-1084-config-constant-jd-vectors.md) @ `14b30d55` on `sub/AST-1077/AST-1084-config-constant-jd-vectors`.

- **Scope:** minor — single `src/utils/config.py` constant (`EMBEDDED_EVALUATE_JD_CRITERIA`); no core/UI/data wiring.
- **Conf:** high — mirrors `EMBEDDED_COMPANY_PREFILTER_CRITERIA`; QC/GC codes, importance 1, and grade text locked by ticket + parent Original brief.
- **Risk:** low — unused until AST-1085 imports it; wrong copy is config-only until wire-up.

— Ada

---

# Config constant JD vectors (QC / GC)

**Linear:** [AST-1084](https://linear.app/astralcareermatch/issue/AST-1084/config-constant-jd-vectors-qc-gc-add-a-constant-set-of-rubric-vectors)
**Parent:** [AST-1077](https://linear.app/astralcareermatch/issue/AST-1077/add-a-constant-set-of-rubric-vectors-to-generated-jd-evaluate-vectors)
**Publish ref:** `sub/AST-1077/AST-1084-config-constant-jd-vectors`

Add a config-owned constant criteria block for Quality Check (**QC**) and Gut Check (**GC**) — importance **1**, grade letter → description text from the parent Original brief — shaped like `EMBEDDED_COMPANY_PREFILTER_CRITERIA`. Definitions only: no runtime merge into `evaluate_jd` hydration, generate/save restore, or other rubric owners (sibling AST-1085).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `EMBEDDED_EVALUATE_JD_CRITERIA` tuple after `EMBEDDED_COMPANY_PREFILTER_CRITERIA` | utils |

No other files. Do not import or reference the new constant from core/UI/data in this ticket.

## Stage 1: Config constant QC / GC block

**Done when:** `src/utils/config.py` defines `EMBEDDED_EVALUATE_JD_CRITERIA` as a `tuple[dict, ...]` with exactly two rows (QC then GC), each matching the RC row shape (`code`, `label`, `importance`, `content`, `grade_descriptions`). Importance is `1` on both. Grade letters and description strings match the parent Original brief (verbatim meaning). Nothing else in the repo imports or merges this constant yet.

1. In `src/utils/config.py`, immediately after the closing `)` of `EMBEDDED_COMPANY_PREFILTER_CRITERIA` (currently ends near the AST-707 Reality Check block, before the AST-803 legacy BUILD_ARTIFACTS helpers), insert a new constant:

   ```python
   # AST-1084 / AST-1077: embedded evaluate_jd vectors — definitions only;
   # merge/append into jobdesc / evaluate_jd hydration is AST-1085.
   EMBEDDED_EVALUATE_JD_CRITERIA: tuple[dict, ...] = (
       {
           "code": "QC",
           "label": "Quality Check",
           "importance": 1,
           "content": (
               "Quality Check — is this enough of a JD to analyze?\n"
               "A = This is a valid job description with full details of the role and requirements and information about the company the candidate would be working for.\n"
               "B = This is a valid job description with full details of the role and requirements, but limited information about the company the candidate would be working for.\n"
               "C = This content references a job with enough detail about the role and requirements to perform fit analysis for the candidate.\n"
               "F = This is not enough information to perform job fit analysis, either because it is not a job description, or it is too vague to determine fit for the candidate."
           ),
           "grade_descriptions": [
               {
                   "grade": "A",
                   "description": "This is a valid job description with full details of the role and requirements and information about the company the candidate would be working for.",
               },
               {
                   "grade": "B",
                   "description": "This is a valid job description with full details of the role and requirements, but limited information about the company the candidate would be working for.",
               },
               {
                   "grade": "C",
                   "description": "This content references a job with enough detail about the role and requirements to perform fit analysis for the candidate.",
               },
               {
                   "grade": "F",
                   "description": "This is not enough information to perform job fit analysis, either because it is not a job description, or it is too vague to determine fit for the candidate.",
               },
           ],
       },
       {
           "code": "GC",
           "label": "Gut Check",
           "importance": 1,
           "content": (
               "Gut Check — is this even plausible for this candidate?\n"
               "A = Based on the candidate's bio provided, this job would be a slam dunk for them.\n"
               "B = Based on the candidate's bio provided, this job could be a good fit for them.\n"
               "C = Based on the candidate's bio, this job would be doable, with caveats, for them.\n"
               "D = Based on the candidate's bio, this job would be a stretch-to-impossible for them.\n"
               "F = There's really no way this candidate could ever do this job.\n"
               "X = There's not enough information about the job to make this determination with certainty."
           ),
           "grade_descriptions": [
               {
                   "grade": "A",
                   "description": "Based on the candidate's bio provided, this job would be a slam dunk for them.",
               },
               {
                   "grade": "B",
                   "description": "Based on the candidate's bio provided, this job could be a good fit for them.",
               },
               {
                   "grade": "C",
                   "description": "Based on the candidate's bio, this job would be doable, with caveats, for them.",
               },
               {
                   "grade": "D",
                   "description": "Based on the candidate's bio, this job would be a stretch-to-impossible for them.",
               },
               {
                   "grade": "F",
                   "description": "There's really no way this candidate could ever do this job.",
               },
               {
                   "grade": "X",
                   "description": "There's not enough information about the job to make this determination with certainty.",
               },
           ],
       },
   )
   ```

2. Do **not** add QC/GC into `EMBEDDED_COMPANY_PREFILTER_CRITERIA`. Do **not** change `rubric_criteria_for_task`, `candidate.py` merge helpers, dispatcher, or UI. Do **not** add D/X grades to Quality Check or invent letters beyond the brief.

⚠️ **Decision:** Name the constant `EMBEDDED_EVALUATE_JD_CRITERIA` (parallel to `EMBEDDED_COMPANY_PREFILTER_CRITERIA`, keyed to the `evaluate_jd` owner) rather than a `jobdesc_*` alias — parent Architectural definition targets the evaluate_jd / jobdesc_rubric path; the wire-up sibling will import this exact name.

⚠️ **Decision:** Quality Check `grade_descriptions` list only A/B/C/F (no D/X); Gut Check lists A/B/C/D/F/X — locked by parent Boundaries / Original brief. Do not “complete” the QC set to the full `{A,B,C,D,F,X}` alphabet.

⚠️ **Decision:** `content` lines use `A = …` (same style as Reality Check) with the Original brief sentence text after `==` preserved verbatim; `grade_descriptions[].description` is that same sentence without the letter prefix.

## Self-Assessment

**Scope:** `minor` — single utils config constant; no core/UI/data wiring.

**Conf:** `high` — copy the existing `EMBEDDED_COMPANY_PREFILTER_CRITERIA` row shape; grade text is fixed in the parent Original brief; codes/importance locked in the ticket.

**Risk:** `low` — unused until AST-1085 imports it; wrong text would only surface when the sibling wires merge, and can be corrected in config without changing runtime paths in this ticket.

## Rules check

- §2.1 / `astral.config.config-source-of-truth` — definitions live only in `config.py`.
- `astral.standards.no-hardcoded-sets` — no inline QC/GC sets outside this config block.
- `pattern.config.config-block` — organized tuple next to the existing embedded-criteria block.
- §1.3 DRY — no second embedding mechanism; sibling reuses this constant.
- §3.3 imports — this ticket adds no new cross-layer imports.
- In-scope only — no evaluate_jd hydration, restore-on-delete, or other rubric owners.

## Review

- **Commit:** `29d55902`
- **Branch:** `sub/AST-1077/AST-1084-config-constant-jd-vectors`

### Radia — code-rubric.v1 (2026-07-31)

[code-rubric] revision=1
**Overall:** DISCUSS (product CLEAN; three plan-exclusion stragglers on the three-dot diff)

**What's solid**
- `EMBEDDED_EVALUATE_JD_CRITERIA` matches Stage 1 literally (QC then GC; importance 1; QC A/B/C/F; GC A/B/C/D/F/X).
- No runtime import/merge — boundary to AST-1085 held.
- `code(AST-1084)` touches only `src/utils/config.py`; Betty owns tests via one `merge-tests`.

**Issues (discuss)**
- Straggler vs Joan Excluded: `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban` — excluded at plan time (plan Files Changed = config only) but in-scope on `origin/dev...origin/<publish-ref>` because plan + Betty test-tree landed on the sub. All three score **conforms**; no product fix.

**Recommended actions**
- resolve-child: acknowledge stragglers; no src change required for this review.

## Resolution

**2026-07-31 — resolve-child (Ada)**

- **fix-now:** none.
- **discuss (stragglers):** acknowledged — `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, and `astral.git.engineer-test-tree-ban` were Joan-Excluded against plan Files Changed `{utils}` but appear on the three-dot diff once plan + Betty test-tree landed. All three scored **conforms** in Radia's review; no product or plan change.
- **src:** no change this pass (constant already matches Stage 1 @ `29d55902`).
