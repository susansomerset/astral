<!-- linear-archive: AST-1085 archived 2026-08-11 -->

## Linear archive (AST-1085)

**Archived:** 2026-08-11  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1085/wire-constants-into-evaluate-jd-rubric-path-add-a-constant-set-of  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1077 — Add a constant set of rubric vectors to generated JD evaluate vectors  
**Blocked by / blocks / related:** parent: AST-1077

### Description

## What this implements

Always-merge QC/GC into `evaluate_jd` rubric hydration (**append** after candidate criteria); restore on generate/save if missing; dedupe by code; hard-fail via existing F-dealbreaker; do not touch other rubric owners. After AST-1084.

## In scope

- [X] `pattern.config.config-block` — consume `EMBEDDED_EVALUATE_JD_CRITERIA` from config
- [X] `astral.config.config-source-of-truth` — definitions stay in config; core only merges
- [X] `astral.standards.no-hardcoded-sets` — no inline QC/GC sets in core/UI
- [X] `astral.agent.grade-vector-validation` — grades stay in criterion `grade_descriptions` (QC A/B/C/F; GC A–D/F/X)
- [X] `astral.standards.dry-and-focused-functions` — single `_merge_embedded_evaluate_jd_criteria` for hydrate/save/generate
- [X] `astral.standards.in-scope-only` — `evaluate_jd` / `jobdesc_rubric` / `craft_jobdesc_rubric` only
- [X] `astral.layers.import-direction` — core imports utils config; no consult/UI constant copies

## Considered but excluded

- [X] Redefining `EMBEDDED_EVALUATE_JD_CRITERIA` text — AST-1084 owns the config block
- [X] DO / GET / LIKE / joblist / company-prefilter owners — parent Boundaries; other rubric paths unchanged
- [X] Scoring math / importance multipliers / dealbreaker rule changes — existing evaluate_jd F-dealbreaker only
- [X] Jobs list / Recommended Job Modal display — AST-1059 / 1063 / 1064
- [X] Admin UI to edit constant definitions — config-only until a later ticket
- [X] One-time `rubric_vector` DB backfill — parent Boundaries; pick up on next hydrate/generate/save
- [X] `consult.py` / dispatcher claim surfaces — hydrate via `rubric_criteria_for_task` is enough
- [X] `astral.debug.spikes-under-debug-dir` — no spike scripts in this ticket
- [X] `astral.docs.features-single-file-per-ticket` — plan path only; no second feature sheet
- [X] `astral.git.engineer-test-tree-ban` — Betty owns tests; engineer does not patch `tests/`

## Acceptance criteria

- [X] 2. Generating, saving, or hydrating a candidate’s job-description / `evaluate_jd` rubric results in both vectors present, **appended after** candidate-authored criteria (codes + labels + importance + grade descriptions).
- [X] 3. If an operator removes QC or GC from the editor, the next hydrate / generate / save restores them from config.
- [X] 4. Running evaluate_jd for a candidate that has a JD rubric includes grades for both constant vectors in the job’s JD grades output.
- [X] 5. An evaluate_jd run that grades Quality Check or Gut Check as **F** (with the existing dealbreaker confidence rule) moves the job to the normal JD fail path.
- [X] 6. Candidate-authored JD criteria still appear; constants do not wipe or replace them (dedupe by code if a duplicate code already exists).
- [X] 7. No other rubric owners gain these constants.

## Boundaries

Does **not** define the config block (AST-1084). Does **not** change DO/GET/LIKE/joblist/company-prefilter rubrics or Jobs list display (AST-1059/1063/1064).

## Notes for planning

Append (not prepend like RC). Always-merge + restore-on-delete. No one-time DB backfill.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1077-add-a-constant-set-of-rubric-vectors`, child `sub/AST-1077/AST-1085-wire-constants-evaluate-jd`. Created at dispatch-parent.

### Comments

#### ada — 2026-07-31T01:01:42.440Z
[check-linear] blocked: validate-sub-log after reword — @Chuckles Cursor

Rewrote `c57b123b` → `b8f19cfe` `merge(AST-1085): origin/dev` (message-only; tip tree unchanged). Force-pushed `origin/sub/AST-1077/AST-1085-wire-constants-evaluate-jd` @ `084dc713`. First-parent exclusive log is clean.

`validate-sub-log` still fails on full DAG (`sub --not ftr`): `Merge remote-tracking` commits on `origin/dev` not yet on `origin/ftr/AST-1077-add-a-constant-set-of-rubric-vectors`:
- `1c548e31` (AST-1065 tmp-refresh)
- `fc00952c` (AST-1045 tmp-refresh)

Need ftr to absorb `origin/dev` (ftr is behind) so those subjects fall out of the exclusive range. Status stays User Testing; assignee Ada.

#### chuckles — 2026-07-31T00:58:34.760Z
[merge-child] blocked: git pull merge on sub — `c57b123b` subject `Merge remote-tracking branch 'origin/dev' into sub/AST-1077/AST-1085-wire-constants-evaluate-jd` fails `validate-sub-log.sh`. Reword to `merge(AST-1085): origin/dev` (or rebuild tip without that subject) and force-with-lease push publish ref. @Ada Lovelace

— Chuckles

#### radia — 2026-07-31T00:56:52.214Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1085
**Publish ref:** `sub/AST-1077/AST-1085-wire-constants-evaluate-jd` tip `bdada8330611bd4fd36fa02b66a82e3389a4142e`
**Overall:** DISCUSS

Diff: `origin/dev...origin/sub/AST-1077/AST-1085-wire-constants-evaluate-jd` — layers `{core, docs, utils}`; change_types `{add, modify}`.

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | conforms | No confidence/dealbreaker rule edits; reuse existing F path |
| astral.agent.do-task-delegation | scoped | conforms | No new do_task; craft_jobdesc_rubric path already existed |
| astral.agent.grade-vector-validation | scoped | conforms | Grades from config grade_descriptions; no new letters |
| astral.batch.batch-id-first | scoped | conforms | No claim/get/clear signature changes |
| astral.batch.batch-id-format | scoped | conforms | No batch_id format changes |
| astral.batch.claim-process-release | scoped | conforms | No dispatch claim/process/release changes |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | No agent_data latest-ref changes |
| astral.config.config-source-of-truth | scoped | conforms | Consumes EMBEDDED_EVALUATE_JD_CRITERIA; no inline QC/GC prose |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | No threshold/floor edits |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No secrets/env values |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths predicate fails vs diff |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Feature plan under docs/features/; not spike notes |
| astral.docs.features-single-file-per-ticket | scoped | conforms | AST-1085 plan is single docs/features/interface/ast-1085-…md |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty test/merge-tests only; code() owns candidate.py |
| astral.git.engineer-test-tree-ban | scoped | conforms | code(AST-1085) touches only src/core/candidate.py |
| astral.layers.core-vs-external-bright-line | scoped | conforms | Core merge only; no external I/O |
| astral.layers.import-direction | scoped | conforms | core→utils config import; no UI/consult copies |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers predicate fails vs diff |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | No UI rule duplication; config definitions only (sibling) |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | No coat-check key changes |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | No consult.py / render_verdict edits |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | layers predicate fails vs diff |
| astral.standards.data-raises-caller-logs | scoped | conforms | No data-layer logging/behavior change beyond sync args |
| astral.standards.database-header-inventory | scoped | not-applicable | layers predicate fails vs diff |
| astral.standards.debug-contract-gated | scoped | conforms | No new debug-contract paths |
| astral.standards.dry-and-focused-functions | scoped | conforms | Single _merge_embedded_evaluate_jd_criteria for hydrate/save/generate |
| astral.standards.in-scope-only | scoped | conforms | Gates evaluate_jd / jobdesc_rubric / craft_jobdesc_rubric only |
| astral.standards.logging-via-utils | scoped | conforms | No logging changes |
| astral.standards.no-cross-contamination | scoped | conforms | Merge logic stays in candidate.py |
| astral.standards.no-hardcoded-sets | scoped | conforms | QC/GC sets remain in config constant |
| astral.standards.public-then-helpers | scoped | conforms | Private helper above rubric_criteria_for_task |
| astral.standards.utils-data-late-import-only | scoped | conforms | No utils→data imports in config constant block |
| astral.state.core-decides-transitions | scoped | conforms | No new transitions; existing evaluate_jd F-fail |
| astral.state.job-prior-states-enforced | scoped | conforms | No prior_states edits |
| astral.state.no-daisy-chain-in-run | scoped | conforms | No run_next / daisy-chain changes |
| astral.ui.frontend-file-placement | scoped | not-applicable | layers predicate fails vs diff |
| astral.ui.naming-conventions | scoped | not-applicable | layers predicate fails vs diff |
| astral.ui.single-gunicorn-worker | scoped | conforms | No gunicorn/worker changes |
| orch.git.betty-merge-tests-one-sha | universal | conforms | One merge-tests(AST-1085) pinning origin/tests bfe64f5c |
| orch.git.commit-vocabulary | universal | conforms | plan/docs/code/test/merge-tests/merge vocabulary on sub |
| orch.git.flow-direction-inviolable | universal | conforms | Publish on origin/sub/AST-1077/AST-1085-… |
| orch.git.ftr-sub-topology | universal | conforms | sub under parent AST-1077 topology |
| orch.git.merge-on-checkout | universal | conforms | merge(AST-1085): origin/dev present; no illegal recipe |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No cherry-pick/rebase/force in reviewed history |
| orch.git.no-dev-agent-branches | universal | conforms | Uses sub/AST-1077/AST-1085-wire-constants-evaluate-jd |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Epic worktree astral-AST-1077 |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Append vs prepend + pending-craft Decision documented |
| orch.pipeline.plan-is-bible | universal | conforms | Helper + three call sites match Stage 1/2 literals |
| orch.pipeline.project-scoped-queues | universal | conforms | Single-child review scope |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | universal | conforms | tests/ + test-bible via Betty |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee remains Ada |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada assignee through Tests Passed |
| orch.roles.pre-commit-path-bans | universal | conforms | No banned-path engineer commits observed |

## Pattern conformance

| id | verdict | note |
|----|---------|------|
| pattern.config.config-block | conforms | Consumes AST-1084 EMBEDDED_EVALUATE_JD_CRITERIA; no second embedding mechanism |

## Plan adherence

Stages 1–2 match: append-merge helper; hydrate on `evaluate_jd`; restore on save (`evaluate_jd` owner) + craft generate/persist (`jobdesc_rubric` / `craft_jobdesc_rubric`). Self-Assessment Single-Component matches `code(AST-1085)` footprint (`candidate.py` only). Three-dot also includes AST-1084 `config.py` + plan (blockedBy sibling not yet on `origin/dev`) — not 1085 scope creep. `evaluate_jd_batch` / consult still load criteria via `rubric_criteria_for_task` (Joan’s non-blocking AC4/AC5 note).

## Findings

**discuss:** straggler — excluded at plan time but in-scope on diff — `astral.debug.spikes-under-debug-dir` (conforms).

**discuss:** straggler — excluded at plan time but in-scope on diff — `astral.docs.features-single-file-per-ticket` (conforms).

**discuss:** straggler — excluded at plan time but in-scope on diff — `astral.git.engineer-test-tree-ban` (conforms; Betty owns tests).

**discuss:** straggler — excluded at plan time but in-scope on diff — `astral.layers.ui-config-driven-business-logic` (conforms; utils/config from sibling).

**discuss:** straggler — excluded at plan time but in-scope on diff — `astral.standards.utils-data-late-import-only` (conforms).

**discuss:** straggler — excluded at plan time but in-scope on diff — `astral.ui.single-gunicorn-worker` (conforms).

No fix-now. Advisory only: craft persist merges then `apply_rubric_vectors_save` merges again — helper is idempotent.

## What's solid

Owner-gated append-merge; DRY single helper; F-dealbreaker path unchanged; one Betty merge-tests SHA.

## Recommended actions

resolve-child: acknowledge stragglers; no src change required.

**Notes:** Joan plan-rubric verdict attached (APPROVED).

context_tokens≈48000

#### betty — 2026-07-31T00:54:08.748Z
## QA test manifest

**origin/sub/AST-1077/AST-1085-wire-constants-evaluate-jd** @ `c691c741` (`merge-tests(AST-1085): origin/tests bfe64f5cd297dc1f0a3ad151cdafb80865cfcf6a`)

### Classification

1. **Existing coverage (bible-backed, still run):** `TestAst1084EvaluateJdCriteria` (config QC/GC definitions); AST-723 prefilter prepend remains the RC mirror.
2. **Broken / obsolete:** none.
3. **Gaps (added):** `TestAst1085EvaluateJdEmbeddedMerge` — helper append/dedupe; hydrate + GET overlay; other owners untouched; save restore; craft generate stash/response; craft persist before sync.

### Manifest

1. `tests/component/core/test_candidate.py::TestAst1085EvaluateJdEmbeddedMerge`
2. `tests/component/utils/test_config.py::TestAst1084EvaluateJdCriteria` (blocker config contract)

### Run

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst1085EvaluateJdEmbeddedMerge \
  tests/component/utils/test_config.py::TestAst1084EvaluateJdCriteria \
  -q
```

### Bible (on publish tip)

- `docs/test-bible/core/candidate.md` sha1 `2bd01e91db6c953ae6ee4d0746ee6cb2a7ff5fd5`
- `docs/test-bible/utils/config.md` sha1 `ad606fd0d37b85eb34ebb6b0f4941dbb0feb6cae`

**Integration:** none revised.

— Betty

#### betty — 2026-07-31T00:44:04.594Z
[check-linear] Plan Approved — bible conflict in `docs/test-bible/utils/config.md` resolved on `merge(AST-1085): origin/dev` (`e905ce3c`); kept HEAD AST-1084 `EMBEDDED_EVALUATE_JD_CRITERIA` / `TestAst1084EvaluateJdCriteria` block; pushed `origin/sub/AST-1077/AST-1085-wire-constants-evaluate-jd`. Assignee unchanged (@Ada Lovelace).

#### ada — 2026-07-31T00:41:47.671Z
[check-linear] blocked: merge conflict — docs/test-bible/utils/config.md (@Betty White)

`git merge origin/dev` into `sub/AST-1077/AST-1085-wire-constants-evaluate-jd` conflicted; merge aborted. Ada cannot resolve `docs/test-bible/**`.

#### joan — 2026-07-31T00:41:00.087Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1085
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 Config holds QC/GC definitions | N/A — boundary (AST-1084); this child consumes `EMBEDDED_EVALUATE_JD_CRITERIA` |
| AC2 Always present / append on hydrate/generate/save | Stage 1 hydrate + Stage 2 save/generate |
| AC3 Restore on operator delete | Stage 2 — merge before sync/stash; embedded wins on code |
| AC4 evaluate_jd grades include both constants | Stage 1 `rubric_criteria_for_task("evaluate_jd")` → existing batch path; no consult rewrite |
| AC5 F on QC/GC → normal JD fail path | Stage 2 §4 — existing evaluate_jd F-dealbreaker once vectors hydrated |
| AC6 Candidate criteria preserved; dedupe by code | Stage 1 helper strips matching codes then appends embedded |
| AC7 No other rubric owners gain constants | Owner gates: `evaluate_jd` / `jobdesc_rubric` / `craft_jobdesc_rubric` only |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 Append-merge helper + hydrate | Functional scope always-present / append; parent AC2/AC6/AC7; Architectural reuse of RC merge with append |
| Stage 2 Restore on save and generate | Functional scope restore-on-delete + editor visibility; parent AC2/AC3/AC4/AC5 |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work |
| orch.git.commit-vocabulary | conforms | Publish on sub ref; no illegal commit types |
| orch.git.flow-direction-inviolable | conforms | Publish only to origin/sub/… |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | No illegal merge recipe |
| orch.git.no-cherry-pick-rebase-force | conforms | None proposed |
| orch.git.no-dev-agent-branches | conforms | Uses sub/AST-1077/AST-1085-… |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree astral-AST-1077 |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Append vs prepend + pending-craft Decision cite AST-905; no open product gap |
| orch.pipeline.plan-is-bible | conforms | Binding Files Changed + two stages with call sites |
| orch.pipeline.project-scoped-queues | conforms | Single-child scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate-plan only |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | No tests/ edits |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Ada) owns build |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer path after Plan Approved |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | No confidence rule changes; reuse existing dealbreaker |
| astral.agent.do-task-delegation | conforms | No new do_task / agent_task; craft path already exists |
| astral.agent.grade-vector-validation | conforms | No new grade letters; grades from criterion grade_descriptions (AST-1084) |
| astral.batch.batch-id-first | conforms | No claim/get/clear signature changes |
| astral.batch.batch-id-format | conforms | No batch_id format changes |
| astral.batch.claim-process-release | conforms | No dispatch claim/process/release changes |
| astral.batch.entity-agent-responses-latest-only | conforms | No agent_data latest-ref changes |
| astral.config.config-source-of-truth | conforms | Consumes EMBEDDED_EVALUATE_JD_CRITERIA; no inline QC/GC prose |
| astral.config.pass-threshold-vs-score-floor | conforms | No threshold/floor edits |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env values |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src; Betty excluded |
| astral.layers.core-vs-external-bright-line | conforms | Core merge only; no external I/O |
| astral.layers.import-direction | conforms | core → utils config; no consult/UI constant copies |
| astral.patterns.coat-check-never-store-empty | conforms | No coat-check key changes |
| astral.patterns.render-verdict-orchestrates-consult | conforms | Explicitly no consult.py / render_verdict edits |
| astral.standards.data-raises-caller-logs | conforms | No data-layer behavior change beyond existing sync call args |
| astral.standards.debug-contract-gated | conforms | No new debug-contract paths |
| astral.standards.dry-and-focused-functions | conforms | Single `_merge_embedded_evaluate_jd_criteria` for hydrate/save/generate |
| astral.standards.in-scope-only | conforms | evaluate_jd / jobdesc_rubric / craft_jobdesc_rubric only |
| astral.standards.logging-via-utils | conforms | No logging changes |
| astral.standards.no-cross-contamination | conforms | Stays in candidate.py core surface |
| astral.standards.no-hardcoded-sets | conforms | Codes/labels/grades stay in config constant |
| astral.standards.public-then-helpers | conforms | Private helper above rubric_criteria_for_task |
| astral.state.core-decides-transitions | conforms | No new transition decisions; existing F-fail path |
| astral.state.job-prior-states-enforced | conforms | No prior_states edits |
| astral.state.no-daisy-chain-in-run | conforms | No run_next / daisy-chain changes |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths match none of plan paths
- astral.debug.spikes-under-debug-dir — paths match none of plan paths
- astral.docs.features-single-file-per-ticket — layers {docs} ∩ plan {core} empty
- astral.git.engineer-test-tree-ban — paths match none of plan paths
- astral.layers.scripts-exempt-from-layer-rules — layers ∩ plan {core} empty
- astral.layers.ui-config-driven-business-logic — layers ∩ plan {core} empty
- astral.patterns.require-auth-on-protected-endpoints — layers ∩ plan {core} empty
- astral.standards.database-header-inventory — layers ∩ plan {core} empty
- astral.standards.utils-data-late-import-only — layers ∩ plan {core} empty
- astral.ui.frontend-file-placement — layers ∩ plan {core} empty
- astral.ui.naming-conventions — layers ∩ plan {core} empty
- astral.ui.single-gunicorn-worker — layers ∩ plan {core} empty

## Findings

None fix-now.

**discuss (non-blocking):** AC4/AC5 are achieved by hydrating criteria via `rubric_criteria_for_task` into the existing evaluate_jd batch / F-dealbreaker — plan correctly avoids consult edits. Build should still verify the batch reads that hydrate path (not a stale criteria snapshot).

**acceptable:** Self-assessment Scope Single-Component / Conf high / Risk Medium is honest (owner-gate / append-order risk). Append-not-prepend + no backfill + pending-craft Decision align with parent Boundaries / AST-905.

**R6 checklist:** Definition fidelity pass (wire-up only). Config consume-only pass. DRY single helper pass. In-scope owners only pass. Import direction pass. No scoring-math creep.

context_tokens≈42000

— Joan

#### ada — 2026-07-31T00:38:38.267Z
Plan published on `origin/sub/AST-1077/AST-1085-wire-constants-evaluate-jd` @ `24456b87`.

[docs/features/interface/ast-1085-wire-constants-evaluate-jd.md](https://github.com/susansomerset/astral/blob/sub/AST-1077/AST-1085-wire-constants-evaluate-jd/docs/features/interface/ast-1085-wire-constants-evaluate-jd.md)

**Scope:** Single-Component — one core module (`candidate.py`) wires AST-1084’s `EMBEDDED_EVALUATE_JD_CRITERIA` into evaluate_jd hydrate/save/generate; consult/UI untouched.

**Conf:** high — same merge pattern as `prefilter_company` + RC, with append order and three call sites named by AC (hydrate / save / generate).

**Risk:** Medium — a bad owner gate or merge order would drop QC/GC from evaluate_jd (or, if mistyped, leak constants into another rubric owner).

---

# Wire constants into evaluate_jd rubric path

**Linear:** [AST-1085](https://linear.app/astralcareermatch/issue/AST-1085/wire-constants-into-evaluate-jd-rubric-path-add-a-constant-set-of)
**Parent:** [AST-1077](https://linear.app/astralcareermatch/issue/AST-1077/add-a-constant-set-of-rubric-vectors-to-generated-jd-evaluate-vectors)
**Publish ref:** `sub/AST-1077/AST-1085-wire-constants-evaluate-jd`

Always-merge Quality Check (**QC**) and Gut Check (**GC**) from `EMBEDDED_EVALUATE_JD_CRITERIA` (AST-1084) into the `evaluate_jd` / `jobdesc_rubric` criteria path — **append** after candidate-authored rows, restore on hydrate / generate / save if missing, dedupe by code (embedded wins). Hard-fail on F uses the existing evaluate_jd dealbreaker; no other rubric owners change.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/candidate.py` | Import `EMBEDDED_EVALUATE_JD_CRITERIA`; add append-merge helper; wire hydrate / save / generate restore for `evaluate_jd` only | core |

No `config.py` edits (definitions are AST-1084). No `consult.py` / dispatcher / UI / other rubric-owner changes.

## Stage 1: Append-merge helper + hydrate

**Done when:** `rubric_criteria_for_task(candidate_id, "evaluate_jd")` returns candidate criteria with QC then GC **appended** from `EMBEDDED_EVALUATE_JD_CRITERIA`, deduped by code (embedded row wins). Other owner keys (`prefilter_company`, `grade_do`, etc.) are unchanged. GET candidate hydration (`hydrate_rubric_artifacts_for_response` → `jobdesc_rubric`) surfaces both constants after candidate rows.

1. In `src/core/candidate.py`, add `EMBEDDED_EVALUATE_JD_CRITERIA` to the existing `src.utils.config` import block (next to `EMBEDDED_COMPANY_PREFILTER_CRITERIA`).

2. Immediately above `rubric_criteria_for_task`, add a private helper:

   ```python
   def _merge_embedded_evaluate_jd_criteria(criteria: list) -> list:
       """Append EMBEDDED_EVALUATE_JD_CRITERIA; embedded wins on duplicate code (AST-1085)."""
       embedded_codes = {
           str(c.get("code")).strip().upper()
           for c in EMBEDDED_EVALUATE_JD_CRITERIA
           if isinstance(c, dict) and c.get("code")
       }
       head = [
           c
           for c in (criteria or [])
           if isinstance(c, dict)
           and str(c.get("code") or "").strip().upper() not in embedded_codes
       ]
       return head + list(EMBEDDED_EVALUATE_JD_CRITERIA)
   ```

3. In `rubric_criteria_for_task`, after the existing `prefilter_company` branch (and before the bare `return criteria`), add:

   ```python
   if owner_task_key == "evaluate_jd":
       return _merge_embedded_evaluate_jd_criteria(criteria)
   ```

   Keep the `prefilter_company` prepend branch exactly as it is today.

⚠️ **Decision:** Reuse the RC merge shape (strip matching codes from candidate rows, then place embedded rows) but **append** instead of prepend — locked by parent Architectural definition / AC#2. Embedded wins on duplicate `QC`/`GC` so restore always re-applies config text/importance, not a stale operator edit of those codes.

⚠️ **Decision:** Single helper owned by `candidate.py` (same module as `rubric_criteria_for_task`) — no second embedding mechanism in consult/agent.

## Stage 2: Restore on save and generate

**Done when:** Saving `jobdesc_rubric` without QC/GC persists them from config (appended). Generating `craft_jobdesc_rubric` returns and stashes criteria with QC/GC appended. Dispatch persist for `craft_jobdesc_rubric` also merges before `sync_rubric_vectors_from_criteria`. evaluate_jd batch grading continues to read criteria via `rubric_criteria_for_task` → constants participate in existing F-dealbreaker with no consult changes.

1. In `apply_rubric_vectors_save`, inside the loop after validating `val` is a list and `owner` is resolved, immediately before `database.sync_rubric_vectors_from_criteria(...)`:

   ```python
   if owner == "evaluate_jd":
       val = _merge_embedded_evaluate_jd_criteria(val)
   ```

   Then sync that `val` (not the pre-merge list). This covers UI candidate save (`api_candidate` → `normalize_rubric_artifacts_on_save` → `apply_rubric_vectors_save`) and any other caller of `apply_rubric_vectors_save` for `jobdesc_rubric`.

2. In `_persist_craft_dispatch_success`, in the `CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY` branch, after validating `criteria` is a non-empty list and **before** building `arts`:

   ```python
   if artifact_key == "jobdesc_rubric":
       criteria = _merge_embedded_evaluate_jd_criteria(criteria)
   ```

3. In `run_candidate_artifact_generation`, inside the `_is_craft_rubric_ui_task` success path, after the empty-criteria rejection and **before** `_stash_pending_craft_generation(...)`:

   ```python
   if task_key == "craft_jobdesc_rubric" and isinstance(parsed_response, dict):
       crit = parsed_response.get("criteria")
       if isinstance(crit, list):
           parsed_response["criteria"] = _merge_embedded_evaluate_jd_criteria(crit)
           criteria_count = len(parsed_response["criteria"])
   ```

   Ensure the mutated `parsed_response` is what gets stashed and returned in the 200 body so the Artifacts editor shows QC/GC without a separate hydrate round-trip.

4. Do **not** modify `consult.py`, `_render_pass_fail`, `_render_score`, dispatcher claim surfaces, DO/GET/LIKE/joblist/company-prefilter merge paths, or `EMBEDDED_EVALUATE_JD_CRITERIA` itself. F on QC/GC hard-fails via the existing evaluate_jd dealbreaker once those vectors are in the hydrated criteria list used by `evaluate_jd_batch`.

⚠️ **Decision:** Restore-on-save lives in `apply_rubric_vectors_save` (owner gate) rather than `normalize_rubric_artifacts_on_save` so grade-table normalization still runs on candidate-authored rows first, and merge/append is a single owner-specific step next to persist.

⚠️ **Decision:** No one-time DB backfill — existing candidates pick up QC/GC on next hydrate / generate / save (parent Boundaries).

⚠️ **Decision:** `get_pending_craft_generation` for `craft_jobdesc_rubric` will behave like company-prefilter after this change: `rubric_criteria_for_task(..., "evaluate_jd")` is never empty once embedded rows exist, so page-return recovery stays 404 when the table/hydrate path already surfaces criteria. That matches Susan’s AST-905 prefilter ruling (restore only when none already). Do not special-case “empty means no candidate rows ignoring embedded.”

## Self-Assessment

**Scope:** `Single-Component` — one core module (`candidate.py`) wires the AST-1084 config constant into evaluate_jd hydrate/save/generate; consult/UI unchanged.

**Conf:** `high` — mirror of `prefilter_company` + `EMBEDDED_COMPANY_PREFILTER_CRITERIA` with append order and three call sites named by the ticket AC.

**Risk:** `Medium` — wrong merge order or owner gate would either omit QC/GC from evaluate_jd (breaking hard-fail / editor visibility) or leak constants into another rubric owner if the `evaluate_jd` / `jobdesc_rubric` gates are mistyped.

## Rules check

- §1.3 DRY — one `_merge_embedded_evaluate_jd_criteria`; hydrate/save/generate all call it; no second embedding mechanism.
- §2.1 / `astral.config.config-source-of-truth` — consume `EMBEDDED_EVALUATE_JD_CRITERIA` only; no inline QC/GC prose in core.
- `astral.standards.no-hardcoded-sets` — codes/labels/grades stay in config.
- `astral.agent.grade-vector-validation` — no new grade letters; agent still grades from criterion `grade_descriptions` (QC A/B/C/F, GC A–D/F/X from AST-1084).
- §3.3 / `astral.layers.import-direction` — core imports utils config; no UI→core inversion; no consult import of the constant.
- `astral.standards.in-scope-only` — only `evaluate_jd` / `jobdesc_rubric` / `craft_jobdesc_rubric`; other owners untouched.
- `pattern.config.config-block` — consume the organized block from AST-1084.

## Out of scope (do not implement)

- Redefining or editing `EMBEDDED_EVALUATE_JD_CRITERIA` text (AST-1084).
- DO / GET / LIKE / joblist / company-prefilter constant vectors.
- Scoring math, importance multipliers, or dealbreaker rule changes.
- Jobs list / Recommended Job Modal display (AST-1059 / 1063 / 1064).
- Admin UI to edit constant definitions.
- One-time `rubric_vector` backfill migration.

## Review

- **Commit:** `889a68d7`
- **Branch:** `sub/AST-1077/AST-1085-wire-constants-evaluate-jd`

### Radia — code-rubric.v1 (2026-07-31)

[code-rubric] revision=1
**Overall:** DISCUSS (product CLEAN; plan-exclusion stragglers on three-dot diff)

**What's solid**
- `_merge_embedded_evaluate_jd_criteria` + hydrate/save/generate call sites match Stage 1/2 literals (append; embedded wins).
- Owner gates limited to `evaluate_jd` / `jobdesc_rubric` / `craft_jobdesc_rubric`; consult reads hydrate via `rubric_criteria_for_task`.
- `code(AST-1085)` touches only `src/core/candidate.py`; one Betty `merge-tests`.

**Issues (discuss)**
- Stragglers vs Joan Excluded (in-scope on `origin/dev...publish-ref` because plan + Betty tests + AST-1084 config landed on the sub): `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, `astral.layers.ui-config-driven-business-logic`, `astral.standards.utils-data-late-import-only`, `astral.ui.single-gunicorn-worker`. All score **conforms**; no product fix.

**Recommended actions**
- resolve-child: acknowledge stragglers; no src change required.

## Resolution

**2026-07-31 — resolve-child (Ada)**

- **fix-now:** none.
- **discuss (stragglers):** acknowledged — `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, `astral.layers.ui-config-driven-business-logic`, `astral.standards.utils-data-late-import-only`, and `astral.ui.single-gunicorn-worker` were Joan-Excluded against plan Files Changed `{core}` but appear on the three-dot diff once plan + Betty test-tree + AST-1084 config landed. All six scored **conforms** in Radia's review; no product or plan change.
- **advisory:** craft persist + `apply_rubric_vectors_save` double-merge is idempotent — left as-is (helper is safe to call twice).
- **src:** no change this pass (`889a68d7` already matches Stages 1–2).
