<!-- linear-archive: AST-1088 archived 2026-08-11 -->

## Linear archive (AST-1088)

**Archived:** 2026-08-11  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1088/gaze-email-config-null-candidate-dispatch-shell-gmail-archivetrash-add  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1087 — Add gaze_email as a dispatch task  
**Blocked by / blocks / related:** parent: AST-1087; blocks: AST-1090

### Description

## What this implements

Owns config for Astral inbox expectations + unbound retention days; allows/provisions one `gaze_email` `dispatch_task` row with **null** `candidate_id` and `auto_mode` true (schema must not require candidate; no special AUTO subtype); extends Gmail external for archive + Trash (modify-capable credential contract). Does **not** own Ruth parse prompts or the per-message decision tree (siblings #2 / #3).

## In scope

- [X] `pattern.config.config-block` — `GAZE_EMAIL_CONFIG` + `TASK_CONFIG["gaze_email"]` shell
- [X] `astral.config.config-source-of-truth` — account address, retention days, task/row seed literals in config
- [X] `astral.config.secrets-and-env-specific-from-environ` — `GMAIL_USER` + OAuth tokens remain environ; no secrets in config
- [X] `astral.layers.core-vs-external-bright-line` — archive/trash I/O in `src/external/gmail.py` only
- [X] `astral.standards.in-scope-only` — no Ruth prompts, no runner decision tree, no AUTO subtype, no permanent delete
- [X] `astral.layers.import-direction` — data←utils, core←data/utils, external←utils
- [X] `astral.standards.no-hardcoded-sets` — no inline retention/task-key/account literals outside config

## Considered but excluded

- [X] `pattern.state.entity-state-transitions` — no job landing / qualify hops on this child (AST-1090)
- [X] `astral.state.no-daisy-chain-in-run` — no create/qualify path here (AST-1090)
- [X] `astral.standards.debug-contract-gated` — no Style D runner path on this child (AST-1090)
- [X] Ruth `agent_task` / parse TASK_CONFIG body — AST-1089
- [X] `get_due_tasks` / `_dispatch_one` mailbox due wiring — AST-1090 (shell row stays non-due until then)
- [X] Manage Email UI redesign / attachments / permanent Gmail delete — parent Boundaries

## Acceptance criteria

- [X] 6. Account address and unbound retention days are read from config (defaults per Functional scope); Gmail secrets remain environ-only; Ruth invocations for bound mail use the bound candidate’s API key.
- [X] 7. The `dispatch_task` schema/provision path allows `candidate_id` null for `gaze_email` (no table-level requirement that every dispatch row have a candidate).
- [X] 8. An unbound message older than the configured retention window is moved to Gmail **Trash** and does not create a job. (Trash/archive external capability for sibling runner.)

## Boundaries

Does **not** own Ruth parse prompts or the per-message decision tree (siblings #2 / #3). Does **not** invent an AUTO task subtype.

## Notes for planning

Citations migrated into In scope / Excluded above. Normal dispatch machinery; `auto_mode` true on the row. Due-task/runner wiring deferred to AST-1090 by design.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1087-add-gaze-email-as-a-dispatch-task`, child `sub/AST-1087/AST-1088-gaze-email-config-null-candidate-dispatch-shell-gmail-archive-trash`. Created at dispatch-parent.

### Comments

#### radia — 2026-07-31T02:16:07.897Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1088
**Publish ref:** `origin/sub/AST-1087/AST-1088-gaze-email-config-null-candidate-dispatch-shell-gmail-archive-trash` tip `9abf9309550a99d1885f9658c0910d4596f2989f` (product tip reviewed `9e9f67c7`; docs() `9abf9309`)
**Overall:** CLEAN

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| orch.git.betty-merge-tests-one-sha | universal | conforms | One `merge-tests(AST-1088): origin/tests 1fc097b2…` on sub |
| orch.git.commit-vocabulary | universal | conforms | plan/code/test/docs/merge-tests/resolve vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | Published to origin/sub only |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1087/AST-1088-…` under parent ftr |
| orch.git.merge-on-checkout | universal | conforms | ftr merge keep both config blocks present |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | None in history |
| orch.git.no-dev-agent-branches | universal | conforms | No agent-named epic branch |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Review in astral-AST-1087 |
| orch.git.three-permanent-branches | universal | conforms | No permanent-branch invention |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Decisions documented; AC8 age→Trash deferred noted by Joan |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–4(+4b) match Files Changed |
| orch.pipeline.project-scoped-queues | universal | conforms | Meteorite child only |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | universal | conforms | tests/bible via Betty test + merge-tests |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee remains Ada |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Implementer stays assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | Role path bans respected |
| astral.agent.confidence-bounds | scoped | conforms | No graded consult path |
| astral.agent.do-task-delegation | scoped | conforms | No do_task / Ruth call on this child |
| astral.agent.grade-vector-validation | scoped | conforms | No grade vectors |
| astral.batch.batch-id-first | scoped | conforms | No new claim/get/clear batch helpers |
| astral.batch.batch-id-format | scoped | conforms | No batch_id minting |
| astral.batch.claim-process-release | scoped | conforms | Shell non-due; no entity claim queue |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | No agent_data RESPONSE writes |
| astral.config.config-source-of-truth | scoped | conforms | Account/retention/task seeds in GAZE_EMAIL_CONFIG |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | No scored consult / score_floor path |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | GMAIL_USER + OAuth remain environ; no secrets in config |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths {artifacts/**,scripts/spikes/**} no match |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Feature plan docs, not spike findings |
| astral.docs.features-single-file-per-ticket | scoped | conforms | AST-1088 plan file; sibling 1089 is separate ticket file |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty commits touch tests/bible only |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer commits omit tests/bible |
| astral.layers.core-vs-external-bright-line | scoped | conforms | Archive/trash I/O only in gmail.py |
| astral.layers.import-direction | scoped | conforms | data←utils, core←data/utils, external←utils |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers {scripts} ∩ diff empty |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | No React; config catalog only |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | No coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | No render_verdict / consult |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | layers {ui} ∩ diff empty |
| astral.standards.data-raises-caller-logs | scoped | conforms | save_dispatch_task raises ValueError; archive/trash raise |
| astral.standards.database-header-inventory | scoped | conforms | Header notes nullable candidate_id |
| astral.standards.debug-contract-gated | scoped | conforms | No new Style D path; provision uses normal INFO |
| astral.standards.dry-and-focused-functions | scoped | conforms | Reuses provision + schema rebuild patterns |
| astral.standards.in-scope-only | scoped | conforms | No Ruth runner / AUTO subtype / permanent delete / UI |
| astral.standards.logging-via-utils | scoped | conforms | Provision logging via existing dispatcher logger |
| astral.standards.no-cross-contamination | scoped | conforms | Stays in named layers/files |
| astral.standards.no-hardcoded-sets | scoped | conforms | Retention/task key/account in config only |
| astral.standards.public-then-helpers | scoped | conforms | Public ensure/provision + archive/trash APIs |
| astral.standards.utils-data-late-import-only | scoped | conforms | data→utils for GAZE_EMAIL_CONFIG; no new utils→data |
| astral.state.core-decides-transitions | scoped | conforms | No job state transitions |
| astral.state.job-prior-states-enforced | scoped | conforms | No job transition path |
| astral.state.no-daisy-chain-in-run | scoped | conforms | No create/qualify hop; shell non-due until AST-1090 |
| astral.ui.frontend-file-placement | scoped | not-applicable | layers {ui} ∩ diff empty |
| astral.ui.naming-conventions | scoped | not-applicable | layers {ui} ∩ diff empty |
| astral.ui.single-gunicorn-worker | scoped | conforms | No gunicorn/worker changes |

## Pattern conformance

- `pattern.config.config-block` — **conforms** (`GAZE_EMAIL_CONFIG` named block)
- Active `astral.patterns.*` — covered via statutes table

## Plan adherence

Self-Assessment Scope `MAJOR-CHANGE` matches four-layer footprint (utils/data/core/external). Stages 1–4(+4b sole `gmail.modify`) delivered. Null-candidate due/runner intentionally untouched (AST-1090). Sibling AST-1089 catalog present on tip via ftr merge — outside this ticket’s Files Changed but not a plan breach by Ada’s AST-1088 commits.

## Findings

**discuss (straggler):** Joan Excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`; tip three-dot includes `docs/features/**` + Betty test-tree so sweep scores them in-scope (all still **conforms**). Joan artifact present.

**advisory:** Three-dot vs `origin/dev` also includes sibling AST-1089 product/docs via ftr merge — expected epic lineage, not AST-1088 scope creep in Ada’s stage commits.

### What’s solid

`GAZE_EMAIL_CONFIG` + shell `TASK_CONFIG`; nullable `candidate_id` + gaze-only save gate + partial unique index; startup `provision_gaze_email_dispatch_task`; `archive_message` / `trash_message` under sole `gmail.modify` with `require_controlled_external_io` and raise-on-fail; no permanent delete.

### Recommended actions

None for fix-now.

context_tokens≈48000

#### betty — 2026-07-31T02:12:30.530Z
## QA test manifest

**Publish:** `origin/sub/AST-1087/AST-1088-gaze-email-config-null-candidate-dispatch-shell-gmail-archive-trash` @ `a291591c`
**Delivery:** `merge-tests(AST-1088): origin/tests 1fc097b26b9075ca9a3501783f490065abe71b2c`

### Gaps (new / revised this pass)

1. `tests/component/utils/test_config.py::TestAst1088GazeEmailConfig` — `GAZE_EMAIL_CONFIG` + `TASK_CONFIG["gaze_email"]` shell + null admin defaults; not company/batch/retired.
2. `tests/component/data/database/test_dispatch_tasks.py::TestAst1088NullCandidateGazeEmail` — null `candidate_id` save for gaze_email; second-shell UNIQUE; reject null for other keys; nullable schema + partial unique index.
3. `tests/component/core/test_dispatcher.py::TestAst1088GazeEmailDispatchProvision` — ensure add/skip; missing-config skip; provision wrapper; `start_scheduler` invokes gaze provision.
4. `tests/component/external/test_gmail.py` — sole `gmail.modify` scope; `TestAst1088ArchiveTrash`; controlled-I/O blocks for archive/trash.

### Broken / obsolete (revised)

5. `TestSendEmail::test_send_email_uses_dual_gmail_scopes` → `test_send_email_uses_modify_gmail_scope`.
6. `TestAst972…::test_start_scheduler_invokes_stage_provision` + `TestAst1054…::test_start_scheduler_invokes_meteorite_provision` — stub `provision_gaze_email_dispatch_task`.

### Narrowed run (required)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1088GazeEmailConfig \
  tests/component/data/database/test_dispatch_tasks.py::TestAst1088NullCandidateGazeEmail \
  tests/component/core/test_dispatcher.py::TestAst1088GazeEmailDispatchProvision \
  tests/component/core/test_dispatcher.py::TestAst1054MeteoriteDispatchProvision::test_start_scheduler_invokes_meteorite_provision \
  tests/component/core/test_dispatcher.py::TestAst972CandidateStageDispatch::test_start_scheduler_invokes_stage_provision \
  tests/component/external/test_gmail.py \
  -q
```

**Pass criterion:** pytest green on the lines above. `src/external/gmail.py` remains **LOCKED_AT_100** (covered by full `test_gmail.py` run). Do **not** use zero-arg harness / branch-lock gate for this ticket.

**Note:** `origin/tests` already had `test(AST-1089)` as an ancestor of this delivery SHA, so sibling AST-1089 catalog/config test files are present on the sub tip. They are **out of scope** for AST-1088 — do not add them to this run (catalog product for `parse_meteorite_email` is not on this tip).

### Bible shasums (`origin/<publish-ref>`)

- `docs/test-bible/utils/config.md` `4104167844c777036d36edb3a3264f0923f85d6c`
- `docs/test-bible/external/gmail.md` `cd96f39f88062693d05f57c0f81784e7b3adf782`
- `docs/test-bible/core/dispatcher.md` `dbf6ac8e24c7a2982c277e29909367b17e5672d5`
- `docs/test-bible/data/database/dispatch_tasks.md` `7d5e40a960b34259e727787e0f2e172cdb4e548a`

— Betty

#### betty — 2026-07-31T02:07:16.765Z
Product bug — holding **Code Complete** (no Tests Ready / no merge-tests this pass).

**Stage 4 incomplete on** `origin/sub/AST-1087/AST-1088-gaze-email-config-null-candidate-dispatch-shell-gmail-archive-trash` @ `e7ca75ca` (`code(AST-1088): Gmail archive + trash under gmail.modify` = `7dc42f3d`):

- Docstring + `__all__` + `archive_message` / `trash_message` landed as planned.
- `_GMAIL_SCOPES` still declares `gmail.send` + `gmail.readonly`.
- Plan Stage 4 / Done-when requires a **single** modify-capable scope:

```python
_GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
]
```

Without that, the credential contract does not match archive/trash (or the commit subject). Do **not** keep the dual-scope pair.

Stages 1–3 look aligned with the plan on tip (config shell, nullable `candidate_id` + save gate, provision + `start_scheduler` hook). No other product defects spotted in this skim.

Please land the scopes fix on the publish-ref and return to **Code Complete** — I’ll write the manifest/tests then (including revising `test_send_email_uses_dual_gmail_scopes` → modify-only).

— Betty

#### chuckles — 2026-07-31T02:05:55.024Z
[thread-missing] Betty Team chat `1251fd4e-2029-4641-bb4d-44bb5b6af320` has no local `store.db` on **chuckles**. Minted new Betty qa UUID `c2766d47-327b-42c4-95fe-7d5cf64ef7ad` and continuing.

— Chuckles

#### joan — 2026-07-31T01:58:11.591Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1088
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 bound shapes → METEORITE_NEW + archive | N/A — boundary (AST-1090 runner; AST-1089 Ruth) |
| AC2 ignore non-URL subject + empty body | N/A — boundary (AST-1090) |
| AC3 unbound newer than retention stays | N/A — boundary (AST-1090; retention literal in Stage 1 config) |
| AC4 unbound older → Gmail Trash, no job | Stage 4 supplies `trash_message` / archive external capability; age→Trash policy + no-create is AST-1090 (child AC8 parenthetical) |
| AC5 per-candidate dedupe / all-duplicate archive | N/A — boundary (AST-1090) |
| AC6 account + retention from config; secrets environ; Ruth uses bound candidate key | Stage 1 (`GAZE_EMAIL_CONFIG` + environ secrets). Ruth candidate API key — N/A — boundary (AST-1089/1090) |
| AC7 no qualify/GDL in same run | N/A — boundary (no runner; AST-1090) |
| AC8 Style D debug on touched paths | N/A — boundary (AST-1090; this child adds no Style D runner path) |
| AC9 null `candidate_id` schema/provision for `gaze_email` | Stages 2–3 (nullable column + partial unique + save gate + ensure provision) |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 GAZE_EMAIL_CONFIG + TASK_CONFIG shell | Purpose/FS §1 config-driven account + retention; parent AC6; Architectural config-block |
| Stage 2 nullable candidate_id + save gate | FS §1 / parent AC9 — table must not require candidate; gaze_email-only null gate |
| Stage 3 provision null-candidate row | FS §1 one `dispatch_task` row null candidate + auto_mode; no AUTO subtype |
| Stage 4 Gmail archive + Trash | FS §2 Trash capability; parent AC4 external I/O; Boundaries no permanent delete |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work |
| orch.git.commit-vocabulary | conforms | Execution contract uses stage commits on sub publish-ref |
| orch.git.flow-direction-inviolable | conforms | Publish only to origin/sub/… |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table sub ref |
| orch.git.merge-on-checkout | conforms | No illegal merge recipe |
| orch.git.no-cherry-pick-rebase-force | conforms | No cherry-pick/rebase/force |
| orch.git.no-dev-agent-branches | conforms | Uses sub/AST-1087/AST-1088-… only |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree astral-AST-1087 |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Decisions documented; block→parent on drift |
| orch.pipeline.plan-is-bible | conforms | Binding stages + Files Changed present |
| orch.pipeline.project-scoped-queues | conforms | Single-child Meteorite scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate-plan only |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | Explicitly no tests/bible |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Ada) owns build |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer path after Plan Approved |
| orch.roles.pre-commit-path-bans | conforms | No banned-path edits |
| astral.agent.confidence-bounds | conforms | No graded consult path in this child |
| astral.agent.do-task-delegation | conforms | No do_task / Ruth call here (AST-1089/1090) |
| astral.agent.grade-vector-validation | conforms | No grade vectors touched |
| astral.batch.batch-id-first | conforms | No new claim/get/clear batch helpers |
| astral.batch.batch-id-format | conforms | No batch_id minting in this shell |
| astral.batch.claim-process-release | conforms | No entity claim queue; mailbox runner deferred |
| astral.batch.entity-agent-responses-latest-only | conforms | No agent_data RESPONSE writes |
| astral.config.config-source-of-truth | conforms | Account, retention, task/row seeds in GAZE_EMAIL_CONFIG |
| astral.config.pass-threshold-vs-score-floor | conforms | No scored consult / score_floor path |
| astral.config.secrets-and-env-specific-from-environ | conforms | GMAIL_USER + OAuth remain environ; no secrets in config |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src; Betty excluded |
| astral.layers.core-vs-external-bright-line | conforms | Archive/trash I/O only in gmail.py; policy deferred to AST-1090 |
| astral.layers.import-direction | conforms | data←utils, core←data/utils, external←utils |
| astral.layers.ui-config-driven-business-logic | conforms | Config block only; no React business rules |
| astral.patterns.coat-check-never-store-empty | conforms | No coat-check keys added |
| astral.patterns.render-verdict-orchestrates-consult | conforms | No render_verdict / consult orchestration |
| astral.standards.data-raises-caller-logs | conforms | save_dispatch_task raises ValueError; Gmail raises after gate |
| astral.standards.database-header-inventory | conforms | Header inventory update for nullable candidate_id planned |
| astral.standards.debug-contract-gated | conforms | No new Style D path; deferred to AST-1090 |
| astral.standards.dry-and-focused-functions | conforms | Reuses provision + schema rebuild patterns |
| astral.standards.in-scope-only | conforms | No Ruth/runner/AUTO subtype/permanent delete/UI redesign |
| astral.standards.logging-via-utils | conforms | Provision logging via existing dispatcher patterns |
| astral.standards.no-cross-contamination | conforms | Stays in named layers/files |
| astral.standards.no-hardcoded-sets | conforms | Retention/task key/account in config only |
| astral.standards.public-then-helpers | conforms | Public ensure/provision + archive/trash APIs |
| astral.standards.utils-data-late-import-only | conforms | data→utils for GAZE_EMAIL_CONFIG; no new utils→data |
| astral.state.core-decides-transitions | conforms | No job state transitions on this child |
| astral.state.job-prior-states-enforced | conforms | No job transition path |
| astral.state.no-daisy-chain-in-run | conforms | No create/qualify hop; shell non-due until AST-1090 |
| astral.ui.single-gunicorn-worker | conforms | No gunicorn/worker changes |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.standards.data-raises-caller-logs, astral.standards.database-header-inventory, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths match none of plan paths
- astral.debug.spikes-under-debug-dir — paths match none of plan paths
- astral.docs.features-single-file-per-ticket — layers {docs} ∩ plan empty
- astral.git.engineer-test-tree-ban — paths match none of plan paths
- astral.layers.scripts-exempt-from-layer-rules — layers {scripts} ∩ plan empty
- astral.patterns.require-auth-on-protected-endpoints — layers {ui} ∩ plan empty
- astral.ui.frontend-file-placement — layers {ui} ∩ plan empty
- astral.ui.naming-conventions — layers {ui} ∩ plan empty

## Findings

None fix-now.

**discuss (non-blocking):** Child AC8 full wording describes unbound age→Trash behavior; plan correctly delivers external Trash/archive capability only and defers the age gate to AST-1090 — matches parent Proposed child #1 + Boundaries. Self-assessment Risk Medium (nullable migration + gmail.modify token UAT) is honest; auto_mode shell intentionally non-due until AST-1090.

**R6:** Definition fidelity pass for child #1 slice. Layer/import/config/placement/pattern/DRY/scope pass. Conf high / not !!-NONE.

context_tokens≈48000

— Joan

#### chuckles — 2026-07-31T01:56:09.036Z
[thread-orphan] Joan chat `da0027e7-276d-4fe2-a6e6-65c8eb77e24d` relocated into epic workspace hash: `/home/susan/.cursor/chats/0f41bf986cfef9e06ea903e586d6d4d9/da0027e7-276d-4fe2-a6e6-65c8eb77e24d/store.db` → `/home/susan/.cursor/chats/bd90604213fc3049015e64d030a28960/da0027e7-276d-4fe2-a6e6-65c8eb77e24d/store.db`. Same UUID; continuing with `--resume`.

— Chuckles

#### ada — 2026-07-31T01:55:43.303Z
Plan published on publish-ref.

**Plan:** https://github.com/susansomerset/astral/blob/sub/AST-1087/AST-1088-gaze-email-config-null-candidate-dispatch-shell-gmail-archive-trash/docs/features/meteorite/ast-1088-gaze-email-config-null-candidate-dispatch-shell-gmail-archive-trash.md

**Tip:** `646c059e` on `origin/sub/AST-1087/AST-1088-gaze-email-config-null-candidate-dispatch-shell-gmail-archive-trash`

**Self-assessment**
- **Scope:** `MAJOR-CHANGE` — utils config, data schema/migration + save gate, dispatcher provision, Gmail external mutate APIs.
- **Conf:** `high` — mirrors AST-1032 Gmail external + AST-1054/972 provision; null-candidate due/runner deferred to AST-1090.
- **Risk:** `Medium` — nullable `candidate_id` migration + `gmail.modify` token verification at UAT; auto_mode shell intentionally non-due until AST-1090.

#### chuckles — 2026-07-31T01:51:57.517Z
[thread-missing] Cursor chat `16374eb4-c160-400d-9e39-1beda31e8e5a` has no local `store.db` on **chuckles** (expected `/home/susan/.cursor/chats/bd90604213fc3049015e64d030a28960/16374eb4-c160-400d-9e39-1beda31e8e5a/store.db`; blob-search also empty).

Minting a **new** conversation on this host and continuing (history from the old UUID is not recovered). New Ada Team UUID: `4371df31-c8e2-466c-a424-665fd6ec867d`.

— Chuckles

---

# AST-1088 — gaze_email config + null-candidate dispatch shell + Gmail archive/trash

**Linear:** [AST-1088](https://linear.app/astralcareermatch/issue/AST-1088/gaze-email-config-null-candidate-dispatch-shell-gmail-archivetrash-add)
**Parent:** [AST-1087](https://linear.app/astralcareermatch/issue/AST-1087/add-gaze-email-as-a-dispatch-task) — Add gaze_email as a dispatch task
**Publish ref:** `origin/sub/AST-1087/AST-1088-gaze-email-config-null-candidate-dispatch-shell-gmail-archive-trash`

Owns Astral inbox expectation + unbound retention config, registers `gaze_email` as a normal dispatch task key, allows/provisions **one** `dispatch_task` row with **null** `candidate_id` and `auto_mode` true (schema must not require a candidate on every row; no AUTO subtype), and extends Gmail external with archive + Trash under a modify-capable OAuth scope contract. Does **not** own Ruth parse prompts (AST-1089) or the per-message bind/route/scrape/create decision tree (AST-1090). Does **not** invent a special AUTO dispatch path.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `GAZE_EMAIL_CONFIG`; `TASK_CONFIG["gaze_email"]` shell entry; special-case admin defaults + trigger/entity helpers for null claim queue | utils |
| `src/data/database.py` | Nullable `dispatch_task.candidate_id`; partial unique index for null-candidate rows; `save_dispatch_task` accepts `Optional` candidate_id | data |
| `src/core/dispatcher.py` | `ensure_gaze_email_dispatch_task` / `provision_gaze_email_dispatch_task`; call from `start_scheduler` | core |
| `src/external/gmail.py` | Expand scopes to modify-capable; add `archive_message` + `trash_message` | external |

No `tests/` / bible / React / Ruth agent_task / gaze_email runner body on this ticket.

## Stage 1: `GAZE_EMAIL_CONFIG` + `TASK_CONFIG` shell

**Done when:** Config exposes account address + unbound retention days + task/row seed literals; `TASK_CONFIG["gaze_email"]` exists so `dispatch_task_admin_defaults("gaze_email")` succeeds and returns null entity/trigger (no claim queue); Gmail secrets stay environ-only.

1. In `src/utils/config.py` module docstring config inventory, add one line:
   `GAZE_EMAIL_CONFIG — Astral inbox gaze_email task key, account expectation, unbound retention, dispatch row seed (AST-1088)`.

2. Immediately **after** `METEORITE_EMAIL_INGEST_CONFIG` (before `METEORITE_DISPATCH_TASKS`), add:

```python
# AST-1088: shared Astral inbox gaze_email dispatch shell (null candidate_id row).
# Live mailbox identity remains GMAIL_USER environ; account_address is the product expectation.
# Runner bind/route/create is AST-1090; Ruth parse task is AST-1089.
GAZE_EMAIL_CONFIG = {
    "task_key": "gaze_email",
    "account_address": "astral.career.match@gmail.com",
    "unbound_retention_days": 7,
    "auto_mode": True,
    "min_count": 1,
    "batch_size": 1,
    "freq_hrs": 0,
    # Mailbox poller — no entity claim queue on the dispatch_task row.
    "entity_type": None,
    "trigger_state": None,
}

assert isinstance(GAZE_EMAIL_CONFIG["unbound_retention_days"], int)
assert GAZE_EMAIL_CONFIG["unbound_retention_days"] > 0
assert GAZE_EMAIL_CONFIG["task_key"] == "gaze_email"
```

⚠️ **Decision — config owns the expected address; environ owns the live mailbox:** Parent AC requires account address from config with default `astral.career.match@gmail.com`. Existing Gmail I/O already binds to `GMAIL_USER` environ (`userId="me"`). Do **not** move `GMAIL_USER` / OAuth secrets into config. AST-1090 may compare `GAZE_EMAIL_CONFIG["account_address"]` to `GMAIL_USER` for ops diagnostics if needed — out of scope here.

3. In `TASK_CONFIG`, add a **shell** entry (no response schema / agent_task / Ruth prompts — AST-1089 owns parse):

```python
"gaze_email": {
    "entity_type": None,
    "requires_candidate_key": False,
    "trigger_state": None,
},
```

Place it near other non-consult dispatch keys if a natural neighbor exists; otherwise immediately before the closing `}` of `TASK_CONFIG` is fine.

4. In `dispatch_task_admin_defaults`, **before** the generic entity/trigger derivation, special-case:

```python
if tk == GAZE_EMAIL_CONFIG["task_key"]:
    return {
        "entity_type": None,
        "trigger_state": None,
        "sort_by": None,
        "batch_call_mode": 0,
    }
```

Do **not** call `_dispatch_entity_type_for_task_key` / `_dispatch_trigger_state_for_task_key` / `_dispatch_sort_by_for` for this key (those helpers assume ENTITY_TYPES claim queues).

5. In `_dispatch_trigger_state_for_task_key` and `_dispatch_entity_type_for_task_key`, add early returns of `None` for `GAZE_EMAIL_CONFIG["task_key"]` **only if** other callers need them — otherwise the admin-defaults special-case alone is enough. Prefer the admin-defaults special-case only to minimize blast radius; if a helper is still reached and would `raise KeyError`, add the early `None` return.

6. Do **not** add `gaze_email` to `_DISPATCH_COMPANY_ENTITY_TASK_KEYS`, `_DISPATCH_BATCH_CALL_MODE_ONE`, or `DISPATCH_RETIRED_TASK_KEYS`. Do **not** add Ruth/agent_task JSON (AST-1089). Do **not** wire due-task eligibility or a runner body (AST-1090).

**Done when (recheck):** `from src.utils.config import GAZE_EMAIL_CONFIG, TASK_CONFIG` exposes the keys above; `dispatch_task_admin_defaults("gaze_email")` returns null entity/trigger/sort_by and `batch_call_mode=0`.

## Stage 2: Nullable `candidate_id` + save path

**Done when:** `dispatch_task.candidate_id` may be NULL; at most one null-candidate row per `task_key`; `save_dispatch_task` can insert `candidate_id=None` for `gaze_email`; existing non-null rows keep `UNIQUE(candidate_id, task_key, trigger_state)` behavior.

1. In `src/data/database.py` `_ensure_dispatch_task_schema`, after existing column/unique migrations, add a migration that makes `candidate_id` nullable when the live `CREATE TABLE` SQL still has `candidate_id TEXT NOT NULL`:

   - Read `sqlite_master` SQL for `dispatch_task`.
   - If `candidate_id TEXT NOT NULL` (or equivalent NOT NULL on that column via `PRAGMA table_info` — `notnull=1` for `candidate_id`): rebuild the table with `candidate_id TEXT` (nullable), same other columns, and `UNIQUE(candidate_id, task_key, trigger_state)`.
   - Copy all rows; `DROP` old; `RENAME` new; `commit`.
   - Follow the same rebuild style already used in this function for `enabled`→`auto_mode` / unique-key migrations (do not invent a new migration framework).

⚠️ **Decision — rebuild rather than `ALTER`:** SQLite cannot drop `NOT NULL` with a simple `ALTER COLUMN`. Match existing `_ensure_dispatch_task_schema` rebuild pattern.

2. After the nullable migration (and on fresh create), ensure a **partial unique index** so SQLite’s NULL-distinct UNIQUE quirk cannot duplicate null-candidate shells:

```sql
CREATE UNIQUE INDEX IF NOT EXISTS idx_dispatch_task_null_candidate_task_key
ON dispatch_task(task_key)
WHERE candidate_id IS NULL
```

Also create this index on the fresh `CREATE TABLE` path (after create). Update the module header inventory comment for `dispatch_task` to note `candidate_id` is nullable (shared Astral inbox tasks).

3. Change `save_dispatch_task` signature to accept `candidate_id: Optional[str] = None`. Pass the value through to INSERT as SQL NULL when `candidate_id` is `None` or blank after strip **only when** `task_key == GAZE_EMAIL_CONFIG["task_key"]` (import `GAZE_EMAIL_CONFIG` from config — data may already import config). For every other task_key, blank/None `candidate_id` remains invalid: raise `ValueError("candidate_id is required")` before INSERT.

⚠️ **Decision — null candidate_id is gaze_email-only at the save gate:** Parent requires null allowed for `gaze_email`, not a free-for-all null on every task. Application gate keeps accidental null rows out; schema nullity is the table-level allowance.

4. When inserting, allow `entity_type` / `trigger_state` / `sort_by` to remain SQL NULL when defaults return `None` (gaze_email). Do not coerce `None` to empty string for these columns.

5. Do **not** change `get_due_tasks` / `count_eligible_for_dispatch_task` / `_dispatch_one` in this stage. Today those paths skip rows missing `candidate_id` / `entity_type` / `trigger_state` — that keeps the provisioned `auto_mode=1` shell from firing until AST-1090 wires mailbox due + runner. Document that contract in the Stage 3 ensure docstring.

**Done when (recheck):** Fresh DB creates nullable `candidate_id`; existing DBs migrate; partial unique index exists; `save_dispatch_task(candidate_id=None, task_key="gaze_email", ...)` inserts one row; second insert of the same null shell raises UNIQUE; `save_dispatch_task(candidate_id=None, task_key="evaluate_jd", ...)` raises `ValueError`.

## Stage 3: Provision one null-candidate `gaze_email` row

**Done when:** Scheduler startup idempotently ensures exactly one `gaze_email` dispatch row with `candidate_id` NULL, `auto_mode` true (from config), null entity/trigger, and seed sizes from `GAZE_EMAIL_CONFIG`.

1. In `src/core/dispatcher.py`, add:

```python
def ensure_gaze_email_dispatch_task() -> Dict[str, Any]:
    """Idempotent insert of the shared Astral inbox gaze_email row (null candidate_id).

    Does not wire due-task eligibility or the mailbox runner (AST-1090).
    """
```

Concrete steps:

- `tk = GAZE_EMAIL_CONFIG["task_key"]`
- Scan `database.list_dispatch_tasks()` (or a focused query if adding one is clearly smaller) for an existing row where `(row.get("task_key") or "").strip() == tk` and `row.get("candidate_id")` is None or `""`.
- If found: return `{"task_key": tk, "added": 0, "skipped": 1, "id": row["id"]}`.
- If missing: `database.save_dispatch_task(candidate_id=None, task_key=tk, min_count=int(GAZE_EMAIL_CONFIG["min_count"]), auto_mode=bool(GAZE_EMAIL_CONFIG["auto_mode"]), entity_type=GAZE_EMAIL_CONFIG["entity_type"], trigger_state=GAZE_EMAIL_CONFIG["trigger_state"], batch_size=GAZE_EMAIL_CONFIG["batch_size"], freq_hrs=float(GAZE_EMAIL_CONFIG["freq_hrs"]))` and return `{"task_key": tk, "added": 1, "skipped": 0, "id": <new id>}`.
- If `tk not in TASK_CONFIG`, return/skip with `skipped_missing_config` (same spirit as meteorite ensure) — should not happen once Stage 1 lands.

2. Add thin wrapper:

```python
def provision_gaze_email_dispatch_task() -> Dict[str, Any]:
    """Startup provision for the shared gaze_email dispatch shell (AST-1088)."""
    return ensure_gaze_email_dispatch_task()
```

3. In `start_scheduler`, after the existing meteorite provision `try`/`except` block, add another `try`/`except` that calls `provision_gaze_email_dispatch_task()` and logs template-free stats (`added` / `skipped` / `id`) at info; on failure log exception (do not crash scheduler startup) — same pattern as AST-972 / AST-1054 provisions.

4. Do **not** copy this row via `set_dispatch_tasks_from_template_rows` / per-candidate meteorite ensure. Do **not** attach the row to `template_candidate_id`. Do **not** implement `_run_unified` / consult routing for `gaze_email` here.

**Done when (recheck):** Calling `ensure_gaze_email_dispatch_task` twice yields add then skip; `start_scheduler` invokes provision; no candidate-scoped duplicate shells.

## Stage 4: Gmail archive + Trash (modify-capable)

**Done when:** `src/external/gmail.py` can archive (remove `INBOX`) and move a message to Trash; credentials declare modify-capable scopes; every new live call gates through `require_controlled_external_io`; list/get/send keep working on the same credential helper.

1. Update the module docstring to state ownership of **send, inbox read, archive, and trash** via a **modify-capable** OAuth client. Keep required env vars unchanged (`GMAIL_USER`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN`; optional `GOOGLE_TOKEN_URI`). Note that live UAT must confirm the refresh token includes modify; remint is ops-only if verification fails (parent dependency — not a code branch).

2. Replace `_GMAIL_SCOPES` with:

```python
_GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
]
```

⚠️ **Decision — single `gmail.modify` scope:** Parent asks for a modify-capable credential contract for archive/trash. `gmail.modify` subsumes the prior send+readonly pair for send/list/get/label mutate/trash (non-permanent delete). Ops remint only if the existing refresh token was minted without modify.

3. Extend `__all__` with `"archive_message"` and `"trash_message"`.

4. Add public `archive_message(message_id: str) -> None`:

   - `require_controlled_external_io("gmail.archive_message")` first.
   - `users().messages().modify(userId="me", id=message_id, body={"removeLabelIds": ["INBOX"]})`.
   - On any exception after the gate, **raise** (same contract as list/get — callers map failures).

5. Add public `trash_message(message_id: str) -> None`:

   - `require_controlled_external_io("gmail.trash_message")` first.
   - `users().messages().trash(userId="me", id=message_id)`.
   - On any exception after the gate, **raise**.
   - Do **not** call `users().messages().delete` (permanent delete is out of parent scope).

6. Do **not** add core `inbox.py` wrappers on this ticket — AST-1090’s core runner may call external directly (core→external is allowed). Do **not** implement unbound age→trash policy here (runner owns the decision; this ticket only supplies the external capability named in AC 8).

**Done when (recheck):** Module docstring + scopes reflect modify; `archive_message` / `trash_message` are public, gated, and raise on failure; no permanent delete API.

## Execution contract

- Stages in order; one commit per stage on the epic worktree sub branch; publish to `origin/<publish-ref>` after each stage per build-child.
- No files outside the Files Changed table.
- Ambiguity or codebase drift → stop and comment on **parent** AST-1087 with the Stage N blocked template.
- Leave `get_due_tasks` / `_dispatch_one` / Ruth / bind-route-create untouched — AST-1090.

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — touches utils config, data schema/migration + save gate, dispatcher provision, and Gmail external mutate APIs across four layers.

**Conf:** `high` — mirrors AST-1032 Gmail external + AST-1054/972 provision patterns; schema rebuild path already exists in `_ensure_dispatch_task_schema`; null-candidate due/runner explicitly deferred to AST-1090.

**Risk:** `Medium` — nullable `candidate_id` + unique/partial-index migration can break dispatch CRUD if wrong; expanding OAuth to `gmail.modify` requires ops token verification at UAT; leaving auto_mode shell non-due until AST-1090 is intentional (row visible, not self-firing).

## Self-review vs ASTRAL_CODE_RULES

- **§2.1 / config-source-of-truth:** Retention days, task key, account expectation, row seed literals in `GAZE_EMAIL_CONFIG`; secrets stay environ.
- **§2.1 / secrets-and-env-specific-from-environ:** `GMAIL_USER` + OAuth vars remain environ; no tokens in config.
- **§2.5 / core-vs-external:** Archive/trash I/O only in `gmail.py`; policy/age-gate stays out (AST-1090).
- **§1.4 / no-hardcoded-sets:** No inline `7` / task key / account string outside config.
- **§3.3 imports:** data←utils, core←data/utils, external←utils only.
- **in-scope-only:** No Ruth prompts, no runner decision tree, no AUTO subtype, no permanent delete, no Manage Email UI redesign.
- **No conflict requiring conf-!!-NONE.**

## Review

**Publish ref:** `origin/sub/AST-1087/AST-1088-gaze-email-config-null-candidate-dispatch-shell-gmail-archive-trash`
**Tip:** `bf172084`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `852d76cb` | GAZE_EMAIL_CONFIG + TASK_CONFIG shell |
| 2 | `d138f905` | nullable candidate_id + save gate |
| 3 | `090c0abc` | provision null-candidate gaze_email row |
| 4 | `7dc42f3d` | Gmail archive + trash under gmail.modify |
| 4b | `bf172084` | sole `_GMAIL_SCOPES` = gmail.modify (Betty hold) |

## Review (Radia — code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1088
**Publish ref tip (at review):** `9e9f67c75cce0182db8c03988a97d7402bd548ae`
**Overall:** CLEAN

### What’s solid

- Stages 1–4 (+4b sole `gmail.modify`) match plan: `GAZE_EMAIL_CONFIG` + shell `TASK_CONFIG`, nullable `candidate_id` + gaze-only save gate + partial unique index, startup provision, archive/trash gated and raise-on-fail (no permanent delete).
- Due/runner still skipped for null entity/trigger/candidate — intentional until AST-1090.
- Betty `test` + one `merge-tests(AST-1088)` SHA on the sub.

### Issues

**discuss (straggler):** Joan Excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`; three-dot tip includes `docs/features/**` + Betty test-tree so sweep scores them in-scope (all still **conforms**).

**advisory:** Three-dot vs `origin/dev` also carries sibling AST-1089 catalog/docs via ftr merge — not AST-1088 product smuggling.

### Recommended actions

None for fix-now. Straggler discuss needs no product change unless resolve wants Joan re-ack.

### Statutes checked (summary)

56 active statutes swept vs `origin/dev...origin/sub/AST-1087/AST-1088-…`. No violates. Full table in Linear review comment.

## Resolution

**Date:** 2026-07-31  
**Publish tip before resolve:** `9abf9309` (`docs(AST-1088): Radia review — CLEAN with Joan straggler discuss`)

Radia overall **CLEAN** — no fix-now product or plan-doc edits.

| Finding | Disposition |
|---------|-------------|
| discuss (Joan Excluded stragglers on three-dot tip) | Accepted as non-blocking; statutes still **conforms**; no product change |
| advisory (AST-1089 via ftr merge on three-dot) | Noted as expected epic lineage; no scope change on this child |

No product commits on this resolve pass.
