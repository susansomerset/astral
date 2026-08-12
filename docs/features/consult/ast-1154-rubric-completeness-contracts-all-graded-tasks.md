<!-- linear-archive: AST-1154 archived 2026-08-07 -->

## Linear archive (AST-1154)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1154/rubric-completeness-contracts-all-graded-tasks-technical-fail-for-do  
**Status at archive:** Archive  
**Project:** Astral Consult  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1150 — Technical fail for Do prompt  
**Blocked by / blocks / related:** parent: AST-1150; blocks: AST-1156

### Description

## What this implements

Harden model-facing instructions and encoded/JSON payload contracts for every rubric grading task (Do/Get/Like, JD, qualify, prefilter, meteorite twins) so each item must emit all expected rubric codes (`X`/`0` allowed; omission forbidden). Does **not** own retry-state routing (sibling Incomplete grades → retry holding) or Skipped Retry.

## Acceptance criteria

- [X] 3. Model-facing contracts for those tasks state that every rubric code must appear; UAT can show a formerly omitting run landing on retry (or completing after a complete response) — never first-touch technical fail for omission.

## Boundaries

Does **not** own retry-state routing or Skipped Retry landing. Does **not** change scoring math for complete grade sets.

## In scope

- [X] `astral.agent.grade-vector-validation` — model-facing contracts require the full live-rubric code set on every graded encoded line (`payload_instructions` + graded `agent_task` cache prompts)
- [X] `astral.agent.confidence-bounds` — silence → `{code}X0`; do not invent letter grades to fill omitted vectors

## Considered but excluded

* `astral.standards.debug-contract-gated` — no new debug emission; expected-vs-decoded Style D logging is AST-1155
* `astral.patterns.render-verdict-orchestrates-consult` / incomplete → retry holding — AST-1155 (`src/core/consult.py` apply path)
* `astral.state.core-decides-transitions` / Skipped Retry hop landing — AST-1156
* `qualify_meteorite` — fields extract, not multi-vector rubric grading
* `grades_encoded_vet_meta` / `vet_inflow_discovery` — single fixed `LT` segment, not a rubric set
* Scoring math for complete grade sets — unchanged
* `src/data/database.py` prompt migrations — AST-1108 repo JSON authority; edit `data/admin/agent_task.json` only
* `tests/` / `docs/test-bible/**` — Betty

## Notes for planning

Parent decisions: completeness + retry for all rubric paths. This child owns contracts only.

## Git branch (authoritative)

`sub/AST-1150/AST-1154-rubric-completeness-contracts-all-graded-tasks`

### Comments

#### radia — 2026-08-03T01:24:27.386Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1154
**Publish ref:** 7c3ec573 (doc-only append on 5842580113fbc6f228d7cb56b073d47ed54e08e1)
**Overall:** DISCUSS

## Plan adherence
- Stage 1 (`src/utils/config.py`): shared `_ENCODED_GRADE_SET_COMPLETENESS` constant appended to exactly the 4 planned multi-vector keys (`grades_encoded`, `_notes`, `_meta`, `_prefilter_links`); confirmed absent from `grades_encoded_vet_meta` / `grades_json` — matches plan verbatim.
- Stage 2 (`data/admin/agent_task.json`): all 7 planned task_keys (`prefilter_company`, `qualify_job_listings`, `evaluate_jd`, `grade_do`, `grade_get`, `grade_like`, `meteorite_like`) carry the `## GRADE SET COMPLETENESS (AST-1154)` block immediately before `## PAYLOAD INSTRUCTIONS`, plus the VALIDATE/Rules tighteners. Tightener insertion lands at end-of-sentence rather than literally mid-sentence after the exact quoted plan phrase in a few rows — same intent, no functional difference.
- `docs/uat-fixtures/AST-756/expected-agent_task.json` verified byte-identical to `data/admin/agent_task.json` on the publish tip (`cmp` clean).
- Full active statute set (65) scored in-session per §5.0 — 0 fix-now, 1 discuss carried from Joan's plan-rubric verdict (below), 3 trivially-clean C4 stragglers (see Notes; structural diff-vs-Files-Changed-table artifacts, not scope creep).

## Pattern conformance
none cited (ticket/plan cite statute ids, not `canon/patterns/*`)

## Findings

**discuss — `astral.standards.names-not-ticket-ids`.** Carried from Joan's plan-rubric verdict: the literal `GRADE SET COMPLETENESS (AST-1154)` doubles as the Stage 2 idempotency sentinel and ships in production `cache_prompt` text / Manage Tasks. Joan already called this non-blocking (precedent: `<!-- AST-723_RUBRIC_VECTORS_TOKEN -->` already lives in the same rows) and left it as engineer's call — engineer kept the ticket-id sentinel. No fix required; flagging only so it doesn't read as an oversight if a later ticket cleans up the heading.

## Frame diff
(none) — description already reflects the shipped diff via the plan doc's Files Changed table and Review stub section; no adds/moves applied to the Linear description itself. Doc-only `docs(AST-1154): Radia review — discuss` append landed on `docs/features/consult/ast-1154-rubric-completeness-contracts-all-graded-tasks.md` at commit `7c3ec573`.

## Notes
- C4 straggler check: 3 statutes Joan's plan-rubric verdict scored not-applicable/excluded (`astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`) score `conforms` on this diff-based sweep, purely because the actual diff includes the plan doc file itself and the pipeline's later test/test-bible additions — neither appears in the plan's Files-Changed table by convention. Both clean: plan doc correctly placed under `docs/features/consult/`; test/test-bible work stays on `test()`/`merge-tests()` SHAs, never touched by the engineer's `code()` commits. Not scope creep.
- Per-commit role separation verified clean: `code()` commits (`0c07b966`, `e62fb471`, `867ea994`) touch only `src/utils/config.py`, `data/admin/agent_task.json`, `docs/uat-fixtures/AST-756/expected-agent_task.json`, `docs/features/consult/*.md`; `test()`/`merge-tests()` commits (`f0d2c9bf`, `58425801`) touch only `tests/**` and `docs/test-bible/**`.
- `origin/ftr/AST-1150-technical-fail-for-do-prompt` confirmed ancestor of this sub tip (merge-on-checkout satisfied).
- `docs/test-bible/{core/candidate,core/consult,utils/config}.md` also carry unrelated AST-1147 / AST-1152 entries — bleed-in from the shared `origin/tests` branch via `merge-tests`, not authored by this ticket; no `src/` or `docs/features/` touch under those ids.
- Shared epic worktree note: mid-review, a concurrent AST-1155 session had this worktree checked out to its own branch with a stray unpushed sub-to-sub merge commit on this branch's local ref. Reset local ref to origin's tip (no force-push, nothing lost — the stray commit was never on origin) before making the doc-only commit below.

## What's solid
- DRY: one shared constant, one identical insertion block reused across 4 config keys and 7 prompt rows — zero drift risk.
- Confidence-bounds / grade-vector-validation contract language is precise: explicit `{code}X0` for silence, explicit ban on inventing letter grades — matches `astral.agent.confidence-bounds` almost verbatim.
- Fixture identity gate (`cmp`) is real and passing on the publish tip, not just asserted in prose.
- Clean boundary discipline: no `src/core/consult.py`, `agent.py`, `database.py`, or scoring-math touch — AST-1155/1156 boundaries fully respected.

context_tokens≈160000

— Radia

#### betty — 2026-08-03T01:10:29.522Z
## QA test manifest — AST-1154

**Publish:** `origin/sub/AST-1150/AST-1154-rubric-completeness-contracts-all-graded-tasks` @ `58425801`
**tests SHA:** `f0d2c9bf` (`test(AST-1154): rubric completeness contracts for encoded grades`)
**merge-tests:** `merge-tests(AST-1154): origin/tests f0d2c9bfee01dbb57f8cb000971065ee21d35313`

### Classification

1. **Existing coverage (bible-backed)**
   - `tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed::test_repo_json_matches_uat_fixture_byte_for_byte` — AST-756 fixture identity still holds after Stage 2 prompt edits.

2. **Broken / obsolete:** none — additive contract text; catalog count unchanged; no scoring/retry path edits.

3. **Gaps (new this pass)**
   1. `tests/component/utils/test_config.py::TestAst1154EncodedGradeSetCompleteness` — shared `_ENCODED_GRADE_SET_COMPLETENESS` on the four multi-vector encoded `payload_instructions`; absent from `grades_encoded_vet_meta` / `grades_json`.
   2. `tests/component/core/test_repo_admin_json.py::TestAst1154GradedTaskCompletenessPrompts` — AST-1154 marker + VALIDATE/Rules tighteners on the seven graded `cache_prompt`s; fixture byte-lock.

**Integration:** none — prompt/config contract only; no existing integration scenario asserts these strings.

### Run

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1154EncodedGradeSetCompleteness \
  tests/component/core/test_repo_admin_json.py::TestAst1154GradedTaskCompletenessPrompts \
  tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed::test_repo_json_matches_uat_fixture_byte_for_byte \
  -q
```

### Bible (on publish-ref)

- `docs/test-bible/utils/config.md` shasum `ca83ff60d3121ea3cfdf0077f8212cf4c21a0003`

— Betty

#### joan — 2026-08-03T01:03:03.775Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1154
**Overall:** APPROVED

Publish ref confirmed against parent Git table: `sub/AST-1150/AST-1154-rubric-completeness-contracts-all-graded-tasks` @ `ae56ef5f`.

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 incomplete vectors → retry holding, never `*_FAILED_TECHNICAL_*` | N/A — boundary (AST-1155); plan Non-goals name it |
| AC2 complete grade sets behave as today | Preserved by omission — Files Changed touches no scoring path; Decision 4 forbids `_validate_grades` / `_render_score` edits |
| AC3 model-facing contracts require every rubric code | Stage 1 (shared `payload_instructions` clause) + Stage 2 (seven graded `cache_prompt`s) |
| AC4 Skipped Retry hop-correct dispatchable state | N/A — boundary (AST-1156) |
| AC5 `debug=True` expected-vs-decoded vector detail | N/A — boundary (AST-1155); plan adds no debug emission |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 `_ENCODED_GRADE_SET_COMPLETENESS` on four encoded output types | Functional scope 3 "Prompt / output-contract hardening (all rubric tasks)"; Architectural definition "DRY shared completeness helper across tasks; no one-off Do-only fork"; child AC3 |
| Stage 2 marker + VALIDATE/Rules on seven graded `agent_task` rows, fixture synced | Functional scope 1 "Complete grade lines everywhere" (model-facing half) + Functional scope 3; child AC3 |

No orphan stages. Fixture sync is a sub-step of Stage 2, not independent scope.

## Adversarial verification (plan claims checked against the worktree)

| Plan claim | Result |
|------------|--------|
| Seven graded rows exist at `current: 1` | Verified — all seven present, exactly one current row each |
| "today all seven have `## PAYLOAD INSTRUCTIONS`" | Verified — true for all seven |
| Inserted text references `{$RUBRIC_VECTORS}` | Verified — real token (`config.py` token registry, `source: rubric`) and already present in all seven `cache_prompt`s, so it resolves rather than emitting the "resolved to empty" warning seen in the parent brief |
| Meteorite Do/Get reuse `grade_do` / `grade_get`; only `meteorite_like` is a separate twin | Verified — meteorite task keys are `meteorite_like`, `meteorite_upshot`, `parse_meteorite_email`, `qualify_meteorite`; no `meteorite_do` / `meteorite_get` rows |
| `qualify_meteorite` is a separate extract task, correctly excluded | Verified — distinct task key, not in the seven |
| `expected-agent_task.json` twin is byte-identical today | Verified — `cmp` clean now, so the Stage 2 gate is meaningful |
| Output types `grades_encoded{,_notes,_meta,_prefilter_links}`, `grades_encoded_vet_meta`, `grades_json` exist | Verified in `ASTRAL_CONFIG["output_types"]` |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work in this plan |
| orch.git.commit-vocabulary | conforms | One `code()` commit per stage, published to the sub ref |
| orch.git.flow-direction-inviolable | conforms | Publishes to `origin/sub/...` only |
| orch.git.ftr-sub-topology | conforms | Publish ref matches the parent Git table row exactly |
| orch.git.merge-on-checkout | conforms | No merge recipe proposed |
| orch.git.no-cherry-pick-rebase-force | conforms | No cherry-pick / rebase / force |
| orch.git.no-dev-agent-branches | conforms | Sub branch only |
| orch.git.one-epic-worktree-per-parent | conforms | Executes on `astral-AST-1150` |
| orch.git.three-permanent-branches | conforms | Invents no permanent branch |
| orch.pipeline.call-susan-for-product-decisions | conforms | Stage-blocked template escalates to parent AST-1150; no improvisation |
| orch.pipeline.plan-is-bible | conforms | Binding execution contract + Files Changed table present |
| orch.pipeline.project-scoped-queues | conforms | Single child, Astral Consult |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready entry only |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | `tests/` and `docs/test-bible/**` explicitly out of scope |
| orch.roles.chuckles-never-ticket-assignee | conforms | Ada implements; Chuckles orchestrates |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer path after Plan Approved |
| orch.roles.pre-commit-path-bans | conforms | No banned-path edits |
| astral.agent.confidence-bounds | conforms | Clause mandates `{code}X0` for silence and forbids inventing letter grades to fill gaps |
| astral.config.config-source-of-truth | conforms | Contract text lives in `ASTRAL_CONFIG["output_types"]`, not in core |
| astral.config.pass-threshold-vs-score-floor | conforms | Neither value touched |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets or env lookups added |
| astral.dispatch.run-next-is-chain-authority | conforms | Adds no config hop-membership or succession set; twin reuse is an observation about existing rows, not a new shadow list |
| astral.dispatch.seed-auto-false | conforms | No `dispatch_task` rows touched |
| astral.git.betty-no-src-or-features | conforms | Engineer owns `src/` and `data/admin/`; Betty excluded |
| astral.layers.import-direction | conforms | No new imports in any layer |
| astral.layers.ui-config-driven-business-logic | conforms | No UI change; config stays the source of the contract |
| astral.seed.agent-tables-in-repo-json | conforms | Edits repo `data/admin/agent_task.json`; Decision 3 forbids a `database.py` prompt migration; fixture twin treated as mirror, not second source |
| astral.seed.archie-catalog-wins | conforms | Lasting change is a committed catalog edit, not a live DB edit |
| astral.seed.boot-only-not-hot-path | conforms | Relies on the existing startup repo-JSON apply; adds no hot-path seed |
| astral.seed.define-approved | conforms | Edits prompt copy on existing rows; invents no table, catalog, coverage rule, or AUTO/CLICK seed |
| astral.seed.operator-rows-stay-deleted | conforms | No dispatch-row re-insertion |
| astral.seed.other-via-coverage-join | conforms | No non-JSON seed inserts; no hardcoded candidate ids |
| astral.standards.data-raises-caller-logs | conforms | No data-layer code change (JSON catalog only) |
| astral.standards.debug-contract-gated | conforms | No new debug emission; Style D expected-vs-decoded is AST-1155 |
| astral.standards.dry-and-focused-functions | conforms | One shared constant across four output types; one identical insert across seven rows |
| astral.standards.in-scope-only | conforms | Explicit out-of-scope list covers `agent.py`, `consult.py`, `database.py`, `src/ui/**`, craft rubrics |
| astral.standards.logging-via-utils | conforms | No logging change |
| astral.standards.names-not-ticket-ids | needs-discussion | Constant name `_ENCODED_GRADE_SET_COMPLETENESS` is clean domain language, but the literal `GRADE SET COMPLETENESS (AST-1154)` doubles as the idempotency sentinel — see discuss finding |
| astral.standards.no-cross-contamination | conforms | Stays inside config + repo catalog + fixture |
| astral.standards.no-hardcoded-sets | conforms | Contract prose is a named config constant; the seven-key list appears only in a throwaway verify script, not shipped code |
| astral.standards.public-then-helpers | conforms | Single module-level constant; no function reorganization |
| astral.standards.utils-data-late-import-only | conforms | No `utils → data` import added |
| astral.state.job-prior-states-enforced | conforms | No state transitions touched |
| astral.ui.single-gunicorn-worker | conforms | No gunicorn or worker change |

## Considered and excluded

**Considered (45):** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.dispatch.run-next-is-chain-authority, astral.dispatch.seed-auto-false, astral.git.betty-no-src-or-features, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.seed.agent-tables-in-repo-json, astral.seed.archie-catalog-wins, astral.seed.boot-only-not-hot-path, astral.seed.define-approved, astral.seed.operator-rows-stay-deleted, astral.seed.other-via-coverage-join, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.names-not-ticket-ids, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.job-prior-states-enforced, astral.ui.single-gunicorn-worker

**Excluded (20):**
- astral.agent.do-task-delegation — layers [core] does not intersect plan layers [data, docs, utils]
- astral.agent.grade-vector-validation — layers [core] does not intersect plan layers [data, docs, utils] (see Notes)
- astral.batch.batch-id-first — paths [src/data/**, src/core/**] match no plan path
- astral.batch.batch-id-format — paths [src/core/**, src/data/**] match no plan path
- astral.batch.claim-process-release — paths [src/core/**, src/data/**] match no plan path
- astral.batch.entity-agent-responses-latest-only — paths [src/core/**, src/data/**] match no plan path
- astral.debug.no-repo-root-artifacts-dir — paths [artifacts/**, scripts/spikes/**] match no plan path
- astral.debug.spikes-under-debug-dir — paths [debug/**, docs/features/**, scripts/spikes/**] match no plan path
- astral.docs.features-single-file-per-ticket — paths [docs/features/**] match no plan path (plan doc itself is not in Files Changed)
- astral.git.engineer-test-tree-ban — paths [tests/**, docs/test-bible/**, ...] match no plan path
- astral.layers.core-vs-external-bright-line — layers [core, external] does not intersect plan layers
- astral.layers.scripts-exempt-from-layer-rules — layers [scripts] does not intersect plan layers
- astral.patterns.coat-check-never-store-empty — layers [core] does not intersect plan layers
- astral.patterns.render-verdict-orchestrates-consult — layers [core] does not intersect plan layers
- astral.patterns.require-auth-on-protected-endpoints — layers [ui] does not intersect plan layers
- astral.standards.database-header-inventory — paths [src/data/**] match no plan path
- astral.state.core-decides-transitions — paths [src/core/**, src/data/**] match no plan path
- astral.state.no-daisy-chain-in-run — layers [core] does not intersect plan layers
- astral.ui.frontend-file-placement — layers [ui] does not intersect plan layers
- astral.ui.naming-conventions — layers [ui] does not intersect plan layers

## Findings

**No fix-now findings.**

**discuss — `astral.standards.names-not-ticket-ids`, Stage 2 step 1a and Stage 1 constant body.** The literal `GRADE SET COMPLETENESS (AST-1154)` is not just prose: Stage 2 step 1a uses it as the idempotency key for skipping already-edited rows, and both verify scripts assert on it, so it becomes a durable sentinel shipped in product prompts and visible in Manage Tasks. The statute governs identifiers rather than string values, and there is in-file precedent (`<!-- AST-723_RUBRIC_VECTORS_TOKEN -->` already lives in these `user_prompt`s), so this does not block. Flagging it because a ticket-id sentinel reads as noise once AST-1154 closes; a ticket-free heading such as `## GRADE SET COMPLETENESS` with the ticket reference confined to the config comment would carry the same idempotency guarantee. Engineer's call.

**acceptable — self-assessment honesty.** Scope `Single-Component`, Conf `high`, Risk `Medium` all match what the plan actually does. The Medium justification is specific rather than generic: prompt wording can move model output, and a bad `agent_task.json` edit would break AST-756 fixture identity — which the plan gates with a `cmp` check that I confirmed passes on the current tree.

**Notes — headline statute mechanically excluded.** The ticket's In-scope list names `astral.agent.grade-vector-validation` as the primary statute, but its `applies_when.layers` is `[core]`, so the matching algorithm excludes it for a utils/data/docs change set. Recording this so the exclusion does not read as an oversight: the plan strengthens the model-facing half of that statute, while its enforcement path (`_validate_grades` / `_render_score`) is deliberately AST-1155's. No action needed on this plan.

**R6 checklist.** Definition fidelity pass — implements Functional scope 3 and the "DRY shared completeness helper, no one-off Do-only fork" instruction, nothing more. Boundaries pass — no `_render_score` math, no retry routing, no Skipped landing. Layer and import pass. Config-as-source-of-truth pass. File placement pass against paths that exist. No batch, state-machine, or `do_task` changes. DRY pass. No sibling scope creep into AST-1155 or AST-1156.

context_tokens≈95000

— Joan

#### ada — 2026-08-03T00:57:37.342Z
Plan published: https://github.com/susansomerset/astral/blob/sub/AST-1150/AST-1154-rubric-completeness-contracts-all-graded-tasks/docs/features/consult/ast-1154-rubric-completeness-contracts-all-graded-tasks.md

`origin/sub/AST-1150/AST-1154-rubric-completeness-contracts-all-graded-tasks` @ `ae56ef5f`

**Scope:** Single-Component — shared encoded `payload_instructions` completeness clause in `config.py` plus the seven multi-vector graded `agent_task` cache prompts in repo JSON (fixture twin); no consult retry / Skipped Retry code.

**Conf:** high — `{$OUTPUT_INSTRUCTIONS}` injection + AST-786/1108 repo-JSON prompt authority already established; Do/Get/Like already say “every vector,” but the shared output-type contract did not; evaluate/qualify VALIDATE language was weaker.

**Risk:** Medium — prompt wording can change model output completeness, but scoring/retry paths are untouched so complete-grade math stays stable; bad `agent_task.json` edits would break AST-756 fixture identity (plan gates `cmp`).

---

# AST-1154 — Rubric completeness contracts (all graded tasks)

**Linear:** [AST-1154](https://linear.app/astralcareermatch/issue/AST-1154/rubric-completeness-contracts-all-graded-tasks-technical-fail-for-do)  
**Parent:** [AST-1150](https://linear.app/astralcareermatch/issue/AST-1150/technical-fail-for-do-prompt) — Technical fail for Do prompt  
**Project:** Astral Consult  
**Publish ref:** `sub/AST-1150/AST-1154-rubric-completeness-contracts-all-graded-tasks`

Harden model-facing instructions so every rubric grading task (Do/Get/Like, JD, qualify, prefilter, meteorite twins) requires a grade segment for **every** expected rubric code. `X`/`0` is the correct no-signal answer; omitting a code is forbidden. This ticket owns the **prompt / `{$OUTPUT_INSTRUCTIONS}` contract** only — retry-state routing and Skipped Retry stay with siblings.

**Non-goals:** Incomplete-grade → retry holding (AST-1155). Skipped Retry landing (AST-1156). Scoring math for complete grade sets. Live-rubric enforcement / `_render_score` missing-vector handling. New debug emission. `qualify_meteorite` (fields extract, not rubric-graded). `vet_inflow_discovery` (single fixed `LT` segment, not a multi-vector rubric set).

---

## Decisions (locked for build)

1. **Shared contract lives in `payload_instructions`.** Completeness language is added once to the four multi-vector `ASTRAL_CONFIG["output_types"]` entries that graded tasks inject via `{$OUTPUT_INSTRUCTIONS}` — not duplicated as four independent rewrites with drift risk.
2. **Task cache prompts reinforce the same rule.** Repo-owned `data/admin/agent_task.json` (and the AST-756 fixture twin) get an identical marker + VALIDATE/Rules line on every multi-vector graded task so Manage Tasks / UAT can see the contract without reading config source.
3. **No `database.py` prompt migration.** AST-1108 made `_apply_ast776/822/880_*` no-ops; startup `apply_agent_task_repo_json_startup` applies repo JSON. Edit the JSON catalog only.
4. **No product validation / retry changes here.** `do_task` / `consult` incomplete-set routing remains AST-1155. This plan must not alter `_validate_grades`, `_render_score`, or error-state maps.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Shared completeness clause on multi-vector encoded `payload_instructions` | utils |
| `data/admin/agent_task.json` | Completeness marker + VALIDATE/Rules lines on graded task `cache_prompt`s | data |
| `docs/uat-fixtures/AST-756/expected-agent_task.json` | Byte-identical to updated `agent_task.json` (AST-786 identity) | docs |

**Out of scope:** `src/core/agent.py`, `src/core/consult.py`, `src/data/database.py`, `src/ui/**`, `tests/**`, `docs/test-bible/**`, craft-rubric tasks, `qualify_meteorite`, `grades_encoded_vet_meta`.

---

## Stage 1: Shared `{$OUTPUT_INSTRUCTIONS}` completeness clause

**Done when:** All four multi-vector encoded output types include the same completeness paragraph; `grades_encoded_vet_meta` and unused `grades_json` are unchanged; a one-liner import check prints `ok`.

1. In `src/utils/config.py`, immediately above the `ASTRAL_CONFIG["output_types"]` dict (near the existing output-type registry comment ~line 3476), add a module-level string constant:

   ```python
   # AST-1154: injected into multi-vector grades_encoded* payload_instructions (not vet / grades_json).
   _ENCODED_GRADE_SET_COMPLETENESS = (
       "GRADE SET COMPLETENESS (AST-1154) — mandatory:\n"
       "Emit exactly one grade segment for every rubric vector code listed in the grading "
       "instructions for this run. Omitting a code is invalid.\n"
       "When there is no signal for a vector, emit {code}X0 — never skip that segment.\n"
       "Do not invent extra codes beyond the rubric. Do not invent letter grades to fill gaps — "
       "use X with confidence 0 when the source is silent."
   )
   ```

2. Append `"\n\n" + _ENCODED_GRADE_SET_COMPLETENESS` to the end of `payload_instructions` for exactly these keys (leave examples and existing format rules intact; append after the example block):

   - `grades_encoded`
   - `grades_encoded_notes`
   - `grades_encoded_meta`
   - `grades_encoded_prefilter_links`

3. Do **not** append to `grades_encoded_vet_meta` (single `LT` segment) or `grades_json` (unused / not multi-vector encoded).

4. Verify:

   ```bash
   python3 -c "
   from src.utils import config as c
   marker = 'GRADE SET COMPLETENESS (AST-1154)'
   ots = c.ASTRAL_CONFIG['output_types']
   for k in ('grades_encoded', 'grades_encoded_notes', 'grades_encoded_meta', 'grades_encoded_prefilter_links'):
       assert marker in ots[k]['payload_instructions'], k
   assert marker not in ots['grades_encoded_vet_meta']['payload_instructions']
   assert marker not in ots['grades_json']['payload_instructions']
   print('ok')
   "
   ```

⚠️ **Decision:** Append (do not rewrite) existing format prose — token/confidence digit tables stay; completeness is an additive mandatory rule. DRY via one constant so the four types cannot drift.

---

## Stage 2: Repo `agent_task` prompts for all multi-vector graded tasks

**Done when:** Every listed task’s current `cache_prompt` contains the AST-1154 marker and an explicit “every code / X0 / omission forbidden” line; `expected-agent_task.json` is byte-identical to `data/admin/agent_task.json`.

1. In `data/admin/agent_task.json`, for each current (`"current": 1`) row with `task_key` in:

   - `prefilter_company`
   - `qualify_job_listings`
   - `evaluate_jd`
   - `grade_do`
   - `grade_get`
   - `grade_like`
   - `meteorite_like`

   edit **only** `cache_prompt` as follows (leave `user_prompt`, agent_id, grouping, `run_next`, uuids, `updated_at` unchanged):

   a. If the string `GRADE SET COMPLETENESS (AST-1154)` is already present, skip that row (idempotent hand-edit).

   b. Otherwise insert the following block **immediately before** the `## PAYLOAD INSTRUCTIONS` heading (or before `{$OUTPUT_INSTRUCTIONS}` if a task lacks that heading — today all seven have `## PAYLOAD INSTRUCTIONS`):

   ```text
   ## GRADE SET COMPLETENESS (AST-1154)
   Every rubric vector code in {$RUBRIC_VECTORS} (or the rubric listed above) MUST appear as exactly one encoded grade segment on that job's line. Omitting a code is invalid. When the source is silent, emit {code}X0 — never skip the segment. Do not add codes that are not in the rubric.
   ```

   c. Additionally tighten the existing VALIDATE / Rules language on these weaker rows (exact edits — do not rewrite surrounding steps):

   - **`evaluate_jd`** — in STEP 3, after “Check that the codes and grades you used are valid.”, append: ` Confirm every rubric vector code appears exactly once; use X0 when silent — never omit a code.`
   - **`qualify_job_listings`** — after STEP 4’s example line, append a new sentence on its own line: `Every rubric vector code must appear exactly once per job line; use X0 when silent — never omit a code.`
   - **`grade_do` / `grade_get` / `grade_like` / `meteorite_like`** — in STEP 3, after “**every** rubric vector present”, append: ` Omitting a code is invalid; silent vectors must be {code}X0.`
   - **`prefilter_company`** — after Rules item 1 (“Grade every vector in the rubric…”), append: ` Omitting a code is invalid; silent vectors must be X0.`

2. Sync the UAT fixture (AST-786 identity contract):

   ```bash
   cp data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json
   cmp -s data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json && echo identical
   ```

3. Verify marker coverage:

   ```bash
   python3 -c "
   import json
   from pathlib import Path
   keys = {
       'prefilter_company','qualify_job_listings','evaluate_jd',
       'grade_do','grade_get','grade_like','meteorite_like',
   }
   marker = 'GRADE SET COMPLETENESS (AST-1154)'
   for path in (
       Path('data/admin/agent_task.json'),
       Path('docs/uat-fixtures/AST-756/expected-agent_task.json'),
   ):
       rows = json.loads(path.read_text())
       for k in keys:
           r = next(x for x in rows if x.get('task_key')==k and x.get('current')==1)
           assert marker in (r.get('cache_prompt') or ''), f'{path}:{k}'
   print('ok')
   "
   ```

⚠️ **Decision:** Meteorite Do/Get reuse `grade_do` / `grade_get` agent_task rows (dispatch twins share prompts); only `meteorite_like` is a separate twin key — all three meteorite graded hops are covered by the seven-key list. Do **not** invent a new `database.py` migration; repo JSON is authoritative at startup.

---

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; publish each tip to `origin/sub/AST-1150/AST-1154-rubric-completeness-contracts-all-graded-tasks`.
- Do not edit files outside the Files Changed table.
- If a step is ambiguous, contradicts the codebase, or fails when followed literally — stop and comment on **parent AST-1150** with the Stage N blocked template. No improvisation.
- After both stages: hand-confirm Manage Tasks (or a local DB after app start / repo-json apply) shows the AST-1154 marker on `grade_do` `cache_prompt` and that `{$OUTPUT_INSTRUCTIONS}` resolution for `grade_do` includes the completeness paragraph (Ad Hoc prompt preview or debug assemble — optional; config assert in Stage 1 is sufficient for build gate).

---

## Self-Assessment

**Scope:** `Single-Component` — utils `payload_instructions` plus repo-owned graded-task prompt catalog; no core apply/retry path.

**Conf:** `high` — pattern matches AST-880/AST-786 repo-JSON prompt authority and existing `{$OUTPUT_INSTRUCTIONS}` injection; scope excludes the harder retry routing sibling.

**Risk:** `Medium` — prompt wording can change model behavior and token shape; a bad edit to `agent_task.json` would diverge Manage Tasks / fixture identity, but scoring/retry paths are untouched so complete-grade math stays stable.

---

## Self-review vs `ASTRAL_CODE_RULES.md`

| Section | Check |
|---------|--------|
| §1.3 DRY | Completeness prose is one `_ENCODED_GRADE_SET_COMPLETENESS` constant shared by four output types; agent_task block is one identical insert across seven keys |
| §2.1 config | Contract text lives in `ASTRAL_CONFIG["output_types"]`; no hard-coded completeness set in core |
| §2.3.1 grade-vector-validation | Model contract requires full code set; enforcement/retry remains AST-1155 — this plan does not weaken or relocate `_validate_grades` |
| §2.3.2 confidence-bounds | Explicitly requires `X0` for silence; forbids inventing letter grades to fill gaps |
| §1.5.1 debug-contract-gated | No new debug lines |
| §3.3 imports | No new cross-layer imports |
| §3.5 naming | Constant `_ENCODED_GRADE_SET_COMPLETENESS` + marker `AST-1154` |

**Conflicts:** None.

---

## Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-1150/AST-1154-rubric-completeness-contracts-all-graded-tasks`  
**Product commits:**
- `0c07b966` — Stage 1: `_ENCODED_GRADE_SET_COMPLETENESS` on four multi-vector `payload_instructions`
- `e62fb471` — Stage 2: AST-1154 completeness marker + VALIDATE/Rules on seven graded `agent_task` cache prompts; AST-756 fixture byte-identical

**Local verification:** Stage 1 import assert on marker presence/absence; Stage 2 marker coverage + `cmp` fixture identity.

---

## Radia review

**[code-rubric] revision=1** · **Publish ref:** `5842580113fbc6f228d7cb56b073d47ed54e08e1` · **Overall:** DISCUSS

Full active statute set (65) scored in-session — 0 fix-now. Stage 1 / Stage 2 diffs match the plan verbatim (constant on exactly the 4 planned keys, absent from `grades_encoded_vet_meta` / `grades_json`; all 7 planned `agent_task` rows carry the marker + tighteners; fixture byte-identical on the publish tip).

**discuss — `astral.standards.names-not-ticket-ids`.** Carried from Joan's plan-rubric verdict: `GRADE SET COMPLETENESS (AST-1154)` doubles as the Stage 2 idempotency sentinel and ships in production `cache_prompt` text. Non-blocking (in-file precedent: `AST-723_RUBRIC_VECTORS_TOKEN`); engineer's call, exercised — kept the ticket-id sentinel.

**Notes:** 3 statutes Joan excluded at plan time (`astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`) score `conforms` on the diff-based sweep — the actual diff includes this plan doc and the pipeline's later test/test-bible commits, neither of which sit in the plan's Files-Changed table by convention. Both clean; not scope creep. Per-commit role separation verified: `code()` commits never touch `tests/**` / `docs/test-bible/**`; `test()` / `merge-tests()` commits never touch `src/**` / `docs/features/**`.

— Radia

---

## Resolution

**2026-08-03** — Radia **0 fix-now**. Discuss on `astral.standards.names-not-ticket-ids` (ticket-id in `GRADE SET COMPLETENESS (AST-1154)` sentinel): **kept as shipped**. Renaming would churn Betty’s marker assertions and Manage Tasks copy for a non-blocking, already-precedented pattern; no product code change this pass.

**Publish tip after resolve:** see `resolve(AST-1154): — clean` commit on `origin/sub/AST-1150/AST-1154-rubric-completeness-contracts-all-graded-tasks`.
