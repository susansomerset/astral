<!-- linear-archive: AST-1014 archived 2026-08-07 -->

## Linear archive (AST-1014)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1014/contact-context-artifacts-library-name-columns-candidate-profile  
**Status at archive:** Archive  
**Project:** Astral Candidate  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-952 — Candidate Profile Preamble to Intake  
**Blocked by / blocks / related:** parent: AST-952; blocks: AST-1065; blocks: AST-1017; blocks: AST-1016; blocks: AST-1015

### Description

## What this implements

Persist three candidate blobs (**contact**, **context**, **artifacts**) and **first / last / full / pronouns** as individual candidate-table text columns (not in a blob). Contact blob holds emails, phone, LinkedIn/GitHub URL-or-username, websites; context holds prose + raw_resume / raw_profile / raw_sample (and remaps); artifacts stay structured resume/rubrics. Readable by Profile/Admin and intake.

## Acceptance criteria

1. Candidate has three blobs (contact / context / artifacts) plus first, last, full, and pronouns as table columns; contact identity/comms are not stored as freeform context prose; raw resume / LinkedIn / sample live in context; structured resume/rubrics remain artifacts.
2. Profile/Admin identity and pronoun editing still work against the new columns/contact home — no divergent copies.

## Boundaries

Does **not** own validation (#2), PREAMBLE_CONFIG (#3), or mechanical UI (#4). Does **not** own Estelle confirm (AST-953).

## Notes for planning

Config as source of truth (§2.1). Remap existing profile/context keys into the three-blob + column shape without shadow copies.

## Git branch (authoritative)

Parent `ftr/AST-952-candidate-profile-preamble-to-intake`; this child `sub/AST-952/<this-id>-contact-context-artifacts-library`. Publish to `origin/<publish-ref>` only — never Linear `gitBranchName` when it disagrees.

### Comments

#### chuckles — 2026-07-28T19:19:20.065Z
[check-linear] User Testing — sub tip cleaned; merge-child via [datt]

— Chuckles

#### ada — 2026-07-28T18:55:03.550Z
[check-linear] User Testing — tip cleaned earlier; `origin/sub/AST-952/AST-1014-contact-context-artifacts-library` @ `494f0fb9` (no `Merge remote-tracking`); validate-sub-log empty-range (already on ftr).

@Chuckles Cursor

#### chuckles — 2026-07-28T18:03:32.166Z
[merge-child] blocked: git pull merge on sub — use: git fetch && git merge origin/ftr/<parent-segment>

Bad commits on `origin/sub/AST-952/AST-1014-contact-context-artifacts-library`:
- `13c8789d` Merge remote-tracking branch `origin/dev` into sub/…
- `95faf77a` Merge remote-tracking branch `origin/sub/…` into sub/…

@Ada Lovelace — rewrite/republish a clean sub tip (no `Merge remote-tracking branch`), keep User Testing, then Chuckles will re-run merge-child.

— Chuckles

#### radia — 2026-07-28T18:01:45.079Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1014
**Publish ref:** `sub/AST-952/AST-1014-contact-context-artifacts-library` @ `7bf485576ac980eb478e28745b23fa9b48b31784` (product tip reviewed `95faf77a`; docs append `7bf48557`)
**Overall:** FIX-NOW

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| orch.git.betty-merge-tests-one-sha | universal | conforms | Single `merge-tests(AST-1014)` SHA `7ecac69d` from Betty tip |
| orch.git.commit-vocabulary | universal | conforms | `docs`/`code`/`test`/`merge-tests` vocab on publish-ref |
| orch.git.flow-direction-inviolable | universal | conforms | Sub tip advanced vs origin/dev; no reverse-flow |
| orch.git.ftr-sub-topology | universal | conforms | Child on `sub/AST-952/AST-1014-…` under parent ftr |
| orch.git.merge-on-checkout | universal | conforms | Tip includes merge of origin/dev onto sub |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No cherry-pick/rebase/force in tip history |
| orch.git.no-dev-agent-branches | universal | conforms | Publish stays on named sub/ |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Review in astral-AST-952 only |
| orch.git.three-permanent-branches | universal | conforms | No fourth permanent branch |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | No new open product decision in diff |
| orch.pipeline.plan-is-bible | universal | violates | Stage 3.1 full-row resolve_tokens + Stage 3 debug honor incomplete (api_admin; PUT debug) |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Candidate child only |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Review entered from Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No statute authoring |
| orch.roles.betty-owns-test-tree | universal | conforms | tests/bible only in Betty `test`/`merge-tests` commits |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee remains Ada |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada stays assignee through Review Posted |
| orch.roles.pre-commit-path-bans | universal | conforms | Engineer code commits exclude test-tree; Betty owns tests |
| astral.agent.confidence-bounds | scoped | conforms | No confidence math changes |
| astral.agent.do-task-delegation | scoped | conforms | Still AI via do_task; only token-view wiring |
| astral.agent.grade-vector-validation | scoped | conforms | No graded-task schema changes |
| astral.batch.batch-id-first | scoped | conforms | No claim API signature changes |
| astral.batch.batch-id-format | scoped | conforms | No batch_id format work |
| astral.batch.claim-process-release | scoped | conforms | No claim/process/release changes |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | No agent_responses / latest-ref changes |
| astral.config.config-source-of-truth | scoped | conforms | `CANDIDATE_LIBRARY_CONFIG` owns keys/remaps/URL bases/join |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | Consult scoring untouched |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | Library block literals; no os.environ |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths artifacts/** / scripts/spikes/** miss diff |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Production plan under docs/features/; not a spike dump |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Single plan file ast-1014-…md |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty commits touch tests/bible only |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer `code` commits have no tests/bible |
| astral.layers.core-vs-external-bright-line | scoped | conforms | No external I/O added |
| astral.layers.import-direction | scoped | conforms | ui→core/utils; data→utils; core owns normalize/token view |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers scripts / paths scripts/** miss diff |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | Profile stays shapes-driven; Admin pronouns from shapes |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | No coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | Consult orchestrator untouched |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | api_candidate auth decorators retained |
| astral.standards.database-header-inventory | scoped | conforms | candidate header lists state_history + name columns + library blobs |
| astral.standards.data-raises-caller-logs | scoped | conforms | Data silent; UI maps ValueError→400; refuse-profile raises |
| astral.standards.debug-contract-gated | scoped | violates | save_candidate_data has gated debug, but PUT /data never passes ui_llm_debug() |
| astral.standards.dry-and-focused-functions | scoped | conforms | One config remap/URL/join; migration uses config join (data≠core) |
| astral.standards.in-scope-only | scoped | conforms | state_history wire stays schema/upsert parity only |
| astral.standards.logging-via-utils | scoped | conforms | get_logger / debug_* only; no print/import logging |
| astral.standards.no-cross-contamination | scoped | conforms | Stays in layered src/ + candidate docs |
| astral.standards.no-hardcoded-sets | scoped | conforms | Key sets/remaps/pronoun options from config |
| astral.standards.public-then-helpers | scoped | conforms | New library helpers grouped at candidate.py top |
| astral.standards.utils-data-late-import-only | scoped | conforms | No new utils→data import |
| astral.state.core-decides-transitions | scoped | conforms | No new transition decisions; vocabulary unchanged |
| astral.state.job-prior-states-enforced | scoped | conforms | Job prior_states untouched |
| astral.state.no-daisy-chain-in-run | scoped | conforms | No batch daisy-chain |
| astral.ui.frontend-file-placement | scoped | conforms | Edits existing pages/components/contexts/lib only |
| astral.ui.naming-conventions | scoped | conforms | No new naming violations |
| astral.ui.single-gunicorn-worker | scoped | conforms | Worker count untouched |

## Pattern conformance

none cited

## Plan adherence

Stages 1–2 and most of 3–5 land: library config, migration (incl. missing-def fix), refuse-`profile`, Profile/Admin one-home, builder/intake remaps, data-model doc. Gaps vs Stage 3 bible: (1) not every full-row `resolve_tokens` site updated — `api_admin` still passes raw `candidate_data`; (2) library-write `debug=True` contract not reachable from primary PUT. Self-Assessment Scope MAJOR-CHANGE matches footprint; Conf high; Risk HIGH materialized as the missed admin token readers.

## Findings

### fix-now
1. **`src/ui/api/api_admin.py`** — `_resolve_agent_preview_candidate`, `_enrich_tasks`, `_resolve_adhoc` (and any peer full-row path) still pass raw `candidate.get("candidate_data")` into `resolve_tokens`. After TOKEN_SOURCES → columns + `contact.*`, Admin task/adhoc name+contact tokens blank. Plan Stage 3.1: use `build_candidate_token_view(candidate)` (or equivalent merge).
2. **`src/ui/api/api_candidate.py` `update_candidate_data`** — calls `save_candidate_data(...)` without `debug=ui_llm_debug()`; Stage 3 / parent AC8 debug contract dead on primary PUT.
3. **`src/core/agent.py`** — function-scoped `from src.core.candidate import build_candidate_token_view` lacks cycle-break/lazy-load comment (B1; sibling import below has one).

### discuss
1. **straggler** — Joan excluded `astral.git.engineer-test-tree-ban` at plan time; diff includes `tests/**` + `docs/test-bible/**`. Statute score **conforms** (Betty-only commits).

### advisory
- Intake keeps legacy Python/API param names with documented call-boundary remap to `raw_*` — allowed by plan.
- Migration inlines `full_name_join` (cannot import core `recompute_full_name`) — acceptable layer bend.

## What’s solid

Config contract + migration + refuse-profile + Profile/Admin/builder remaps are coherent; Betty coverage landed cleanly after the missing-migration NameError fix.

## Recommended actions

Wire token view in `api_admin`; pass `debug=ui_llm_debug()` on PUT save; add lazy-import comment in `agent.py`.

## Notes

Joan plan-rubric verdict attached (APPROVED). Excluded at plan: `astral.debug.no-repo-root-artifacts-dir`, `astral.git.engineer-test-tree-ban`, `astral.layers.scripts-exempt-from-layer-rules`.

Docs append: `docs/features/candidate/ast-1014-contact-context-artifacts-library.md` @ `7bf48557`.

context_tokens≈95000

#### betty — 2026-07-28T17:56:30.016Z
## QA test manifest — AST-1014

`origin/sub/AST-952/AST-1014-contact-context-artifacts-library` @ `7ecac69d` (`merge-tests(AST-1014): origin/tests 3159d8aa34b601af17a31ed9c0889d9d4b6916c3`)

### Manifest

1. `tests/component/core/test_candidate.py::TestAst1014CandidateLibrary`
2. `tests/component/utils/test_config.py::TestAst1014CandidateLibraryConfig`
3. `tests/component/utils/test_config.py::TestAst510MiddleNameConfig` (revised — middle retired)
4. `tests/component/utils/test_config.py::TestAst575PronounTokens`
5. `tests/component/core/test_builder.py::TestAst1014BuilderContact`
6. `tests/component/core/test_builder.py::TestBuilderHelpers`
7. `tests/component/data/database/test_candidate_migrations.py` (incl. `TestAst1014CandidateLibraryMigration` + revised AST-575 end-state)
8. `tests/component/ui/api/test_api_candidate.py::TestCandidateRoutes::test_update_rejects_legacy_profile_body`
9. `tests/component/core/test_gazer.py::TestCompiledTitlePatterns`
10. `tests/component/core/test_intake.py::TestIntakeSessionFlow::test_create_session_persists_source_materials`
11. Vitest (§6c):
    - `tests/component/frontend/pages/test_CandidateProfile.test.tsx`
    - `tests/component/frontend/pages/test_AdminManageCandidates.test.tsx`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst1014CandidateLibrary \
  tests/component/utils/test_config.py::TestAst1014CandidateLibraryConfig \
  tests/component/utils/test_config.py::TestAst510MiddleNameConfig \
  tests/component/utils/test_config.py::TestAst575PronounTokens \
  tests/component/core/test_builder.py::TestAst1014BuilderContact \
  tests/component/core/test_builder.py::TestBuilderHelpers \
  tests/component/data/database/test_candidate_migrations.py \
  tests/component/ui/api/test_api_candidate.py::TestCandidateRoutes::test_update_rejects_legacy_profile_body \
  tests/component/core/test_gazer.py::TestCompiledTitlePatterns \
  tests/component/core/test_intake.py::TestIntakeSessionFlow::test_create_session_persists_source_materials \
  -q

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_CandidateProfile.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminManageCandidates.test.tsx
```

### Bible shasums on publish tip

- `46bdd2c443a6b5e195816c1f1d3964fba099e5475d2e061ea3edd0cc7f5e7f3a` `docs/test-bible/core/candidate.md`
- `706f498d4d58005d6c30de9d752d9f56f01fd25afb2624ec7c8650b93d8386a2` `docs/test-bible/utils/config.md`
- `63e611ce90f0d00f9835a2c8b0f84b1b798d002342ae83b14a84085777183271` `docs/test-bible/core/builder.md`
- `6e03230058ae3d2dba02d7c891362871943a238d14867cd67b926e5cd98a4e77` `docs/test-bible/ui/api/api_candidate.md`
- `20bc45ac1bb5a34a025ff1edcc1a515eda68332134ab70cdf011638b9ca92139` `docs/test-bible/frontend/pages.md`
- `a2037d9756039e34419335c14c0a29911bf6258fb270bcc58571ee0f17032665` `docs/test-bible/data/database/candidate_migrations.md`
- `640243eef394a75057f5d88ae86581c2b6dc29a9135ba46fed91fbcb55f51ad0` `docs/test-bible/core/gazer.md`
- `60b56a337b20bf3ef60739f8cced76e011a8d7bb33de47fa27e10b810f47ddb5` `docs/test-bible/core/intake.md`

— Betty

#### ada — 2026-07-28T17:47:52.597Z
origin/sub/AST-952/AST-1014-contact-context-artifacts-library @ `72fbb410` — defined `_migrate_candidate_library_ast1014` (was called from `_ensure_candidate_schema` but missing).

#### betty — 2026-07-28T17:46:05.796Z
Product bug — holding Tests Ready.

`_ensure_candidate_schema` calls `_migrate_candidate_library_ast1014(conn)` (database.py ~L2440) but **no `def _migrate_candidate_library_ast1014` exists** on `origin/sub/AST-952/AST-1014-contact-context-artifacts-library` @ `612e7671` (also missing in the epic worktree). Any `save_candidate` / schema ensure raises:

```
NameError: name '_migrate_candidate_library_ast1014' is not defined
```

Plan Stage 2 §5 requires this idempotent migration (profile→contact, name/pronoun columns, context remaps, hopes/interests/concerns seed, no dual keys).

**Needed:** implement `_migrate_candidate_library_ast1014` per plan (or remove the call if migration was intentionally inlined — it was not). Re-push `code(AST-1014)` to the publish ref and leave **Code Complete** for Betty to resume qa-child.

Status stays **Code Complete**; assignee remains Ada.

— Betty

#### joan — 2026-07-28T17:27:00.315Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1014
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 three blobs + name/pronoun columns; contact ≠ context prose; raw sources in context; structured in artifacts | Stages 1–3 (config, migration, core readers/writers) |
| AC2 Ruth Valid/Try Again/Escalate | N/A — boundary (AST-1015); plan excludes Ruth |
| AC3 PREAMBLE_CONFIG | N/A — boundary (AST-1016); plan forbids adding it |
| AC4 mechanical preamble UI | N/A — boundary (AST-1017) |
| AC5 hopes/interests/concerns as context; Estelle confirm not in epic | Stage 1 seeds empty context keys; Estelle confirm N/A (AST-953) |
| AC6 contact+context ready for AST-953 after Valid mechanical | N/A — boundary (requires siblings 1015–1017); this child only supplies library homes |
| AC7 Profile/Admin one home, no divergent copies | Stage 4 (+ Stage 3 refuse `profile` writes) |
| AC8 backend `debug=True` found/recorded lines on touched write paths | Stage 3 library-write `debug=` contract |

### Child AC → plan stages

| Child AC | Stages |
|----------|--------|
| Three blobs + columns; contact/context/artifacts split | 1–3, 5 |
| Profile/Admin against new homes; no divergent copies | 3–4 |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| 1 Config `CANDIDATE_LIBRARY_CONFIG` + shapes/tokens | Purpose library homes; Functional scope contact/context/artifacts vocabulary; §2.1 |
| 2 Columns + idempotent migration | AC1; no shadow copies; header inventory |
| 3 Core token view / writers / URL normalize / debug | Functional scope contact coercion; AC8; builder/intake remap |
| 4 API + Profile/Admin | AC7 / child AC2; surfaces stay coherent |
| 5 `CANDIDATE_DATA_MODEL.md` | Docs fidelity to shipped library |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | Plan is engineer library work; no Betty test-merge path |
| orch.git.commit-vocabulary | conforms | Plan commits stay docs/code vocab on publish-ref (no forbidden ops in plan) |
| orch.git.flow-direction-inviolable | conforms | Publish ref is `sub/AST-952/…`; no reverse-flow steps |
| orch.git.ftr-sub-topology | conforms | Child `sub/` under parent `ftr/` named correctly |
| orch.git.merge-on-checkout | conforms | No plan step that skips merge-on-checkout discipline |
| orch.git.no-cherry-pick-rebase-force | conforms | No cherry-pick/rebase/force in plan |
| orch.git.no-dev-agent-branches | conforms | Work stays on named `sub/` publish-ref |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree AST-952 only |
| orch.git.three-permanent-branches | conforms | Does not invent fourth permanent branch |
| orch.pipeline.call-susan-for-product-decisions | conforms | Blob-nesting / contact-field decisions documented; no open product blocker |
| orch.pipeline.plan-is-bible | conforms | Stages are build-ready bible for this child |
| orch.pipeline.project-scoped-queues | conforms | Astral Candidate child only |
| orch.pipeline.status-gates-skill-entry | conforms | Validating at Plan Ready gate |
| orch.roles.archie-approves-statutes | conforms | Plan does not author statutes |
| orch.roles.betty-owns-test-tree | conforms | No test-tree edits in Files Changed |
| orch.roles.chuckles-never-ticket-assignee | conforms | N/A to plan content; assignee law external |
| orch.roles.engineer-assignee-through-resolve | conforms | Implementer path after approve; Joan does not reassign |
| orch.roles.pre-commit-path-bans | conforms | No banned-path commits prescribed |
| astral.config.config-source-of-truth | conforms | `CANDIDATE_LIBRARY_CONFIG` owns keys/remaps/URL bases/join |
| astral.config.secrets-and-env-specific-from-environ | conforms | Library block is literals; no `os.environ` |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched consult scoring paths |
| astral.standards.in-scope-only | needs-discussion | Stage 2 wires `state_history` on same upsert — adjacent to library columns; keep strictly schema/upsert parity |
| astral.standards.database-header-inventory | conforms | Header bullet update listed for new columns |
| astral.standards.no-cross-contamination | conforms | Stays in layered `src/` + candidate docs |
| astral.standards.dry-and-focused-functions | conforms | One remap table, one URL normalizer, one full-name helper |
| astral.standards.public-then-helpers | conforms | No conflicting file organization mandate |
| astral.standards.no-hardcoded-sets | conforms | Key sets/remaps in config |
| astral.standards.logging-via-utils | conforms | Debug via `get_logger`; data still silent |
| astral.standards.data-raises-caller-logs | conforms | Data raises; UI maps `ValueError` → 400 |
| astral.standards.utils-data-late-import-only | conforms | No new utils→data import path |
| astral.standards.debug-contract-gated | conforms | Library write emits §1.5.1 only when `debug=True` |
| astral.layers.import-direction | conforms | ui→core/utils; data→utils; core owns normalize/token view |
| astral.layers.core-vs-external-bright-line | conforms | No external I/O added |
| astral.layers.ui-config-driven-business-logic | conforms | Profile stays shapes-driven; no new React business rules |
| astral.ui.frontend-file-placement | conforms | Edits existing flat pages/components/contexts/lib only |
| astral.ui.naming-conventions | conforms | No new naming violations prescribed |
| astral.ui.single-gunicorn-worker | conforms | Touches config/ui but does not change worker count |
| astral.docs.features-single-file-per-ticket | conforms | Single plan file under `docs/features/candidate/` |
| astral.debug.spikes-under-debug-dir | conforms | Production plan in `docs/features/`; not a spike dump |
| astral.git.betty-no-src-or-features | conforms | Engineer owns these paths; Betty not assigned this plan |
| astral.state.core-decides-transitions | conforms | No new transition decisions; vocabulary unchanged |
| astral.state.no-daisy-chain-in-run | conforms | No batch daisy-chain introduced |
| astral.state.job-prior-states-enforced | conforms | Job prior_states untouched |
| astral.agent.do-task-delegation | conforms | No new AI task / do_task path |
| astral.agent.grade-vector-validation | conforms | No graded task changes |
| astral.agent.confidence-bounds | conforms | Confidence math untouched |
| astral.batch.claim-process-release | conforms | No batch claim/process/release changes |
| astral.batch.batch-id-format | conforms | No batch_id work |
| astral.batch.batch-id-first | conforms | No claim signature changes |
| astral.batch.entity-agent-responses-latest-only | conforms | No agent_responses / latest-ref changes |
| astral.patterns.coat-check-never-store-empty | conforms | No coat-check keys added |
| astral.patterns.render-verdict-orchestrates-consult | conforms | Consult orchestrator untouched |
| astral.patterns.require-auth-on-protected-endpoints | conforms | `api_candidate` edits do not remove `@require_auth` |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.config.config-source-of-truth, astral.config.secrets-and-env-specific-from-environ, astral.config.pass-threshold-vs-score-floor, astral.standards.in-scope-only, astral.standards.database-header-inventory, astral.standards.no-cross-contamination, astral.standards.dry-and-focused-functions, astral.standards.public-then-helpers, astral.standards.no-hardcoded-sets, astral.standards.logging-via-utils, astral.standards.data-raises-caller-logs, astral.standards.utils-data-late-import-only, astral.standards.debug-contract-gated, astral.layers.import-direction, astral.layers.core-vs-external-bright-line, astral.layers.ui-config-driven-business-logic, astral.ui.frontend-file-placement, astral.ui.naming-conventions, astral.ui.single-gunicorn-worker, astral.docs.features-single-file-per-ticket, astral.debug.spikes-under-debug-dir, astral.git.betty-no-src-or-features, astral.state.core-decides-transitions, astral.state.no-daisy-chain-in-run, astral.state.job-prior-states-enforced, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.agent.confidence-bounds, astral.batch.claim-process-release, astral.batch.batch-id-format, astral.batch.batch-id-first, astral.batch.entity-agent-responses-latest-only, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.patterns.require-auth-on-protected-endpoints

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths `artifacts/**`, `scripts/spikes/**` miss plan paths
- astral.git.engineer-test-tree-ban — paths `tests/**`, `docs/test-bible/**`, … miss plan paths
- astral.layers.scripts-exempt-from-layer-rules — layers `scripts` miss plan layers; paths `scripts/**` miss plan paths

## Findings

### discuss
1. **Stage 2 `state_history` wire** — Same-upsert schema parity with what core already passes is plausible, but it is adjacent to the library+columns charter. Keep strictly to column + parse/persist (no Progress UI, no vocabulary/transition changes); drop from this ticket if it grows.
2. **HIGH-risk missed readers** — Frontend Stage 4.7 greps `profile.`; extend the same smoke-check to all of `src/` (`profile.`, `starting_resume_text`, `linkedin_profile_text`, `sample_cover_text`, `pronoun_preference`) as a Stage 3 done-when so builder/intake/admin helpers cannot leave a blank-name path.

### acceptable
- Nesting contact/context/artifacts under `candidate_data` (vs three SQL JSON columns) matches parent “blobs on the candidate” + existing persistence; name/pronoun table columns remain the only required SQL lifts.
- Non-comms Profile fields (`timezone`, signatures, `title_patterns`, `reason_codes`) on contact are justified; not context prose.

**Self-assessment:** Scope MAJOR-CHANGE / Conf high / Risk HIGH — honest; Risk HIGH does not escalate because migration, refuse-`profile`, and remap steps are concrete.

— Joan
context_tokens≈62000

#### ada — 2026-07-28T17:24:14.142Z
Plan: `docs/features/candidate/ast-1014-contact-context-artifacts-library.md`

https://github.com/susansomerset/astral/blob/sub/AST-952/AST-1014-contact-context-artifacts-library/docs/features/candidate/ast-1014-contact-context-artifacts-library.md

**Self-Assessment**
- **Scope:** `MAJOR-CHANGE` — schema + migration, config contract, core readers/writers (candidate/builder/intake), API, and Profile/Admin frontend all move from `profile` + nested names to columns + `contact` library.
- **Conf:** `high` — remap and column lift follow existing `_migrate_candidate_*` / DATA_SHAPES / TOKEN_SOURCES patterns; boundaries with AST-1015/1016/1017 are explicit.
- **Risk:** `HIGH` — nearly every candidate identity/token path changes; a missed `profile` reader would blank names or break resume render / Admin create. Migration must be idempotent and shadow-copy-free.

Five stages: (1) `CANDIDATE_LIBRARY_CONFIG` + shapes/tokens, (2) columns + idempotent library migration (+ wire `state_history` on the same upsert), (3) core token view / URL normalize / writers, (4) API + Profile/Admin one-home UI, (5) `CANDIDATE_DATA_MODEL.md`.

Publish ref `sub/AST-952/AST-1014-contact-context-artifacts-library` @ `3b2eb05b`.

---

# AST-1014 — Contact / context / artifacts library + name columns

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1014/contact-context-artifacts-library-name-columns-candidate-profile  
**Parent:** https://linear.app/astralcareermatch/issue/AST-952/candidate-profile-preamble-to-intake  

**Publish ref (origin):** `sub/AST-952/AST-1014-contact-context-artifacts-library`  
**Parent integration ref:** `ftr/AST-952-candidate-profile-preamble-to-intake`

Give the candidate a durable **contact / context / artifacts** library (three JSON blobs under `candidate_data`) plus **first / last / full / pronouns** as individual `candidate` table text columns, so Profile/Admin and later preamble / Topic Menu (AST-953) read and write one home each — no shadow copies of identity or contact in context prose.

Boundaries (do **not** implement): Ruth Valid/Try Again/Escalate (AST-1015), `PREAMBLE_CONFIG` (AST-1016), mechanical intake UI (AST-1017), Estelle confirm (AST-953), candidate state-machine vocabulary changes (AST-871).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `CANDIDATE_LIBRARY_CONFIG` (blob keys, context remaps, URL bases, full-name join rule); rename DATA_SHAPES `profile.*` → columns + `contact.*`; update TOKEN_SOURCES paths; add `FULL_NAME`; point pronoun resolution at `pronouns` column via token view; update intake/bootstrap required field paths that still say `profile.` / old context raw keys | utils |
| `src/data/database.py` | Add columns `first`, `last`, `full`, `pronouns` (+ wire missing `state_history` persist/parse that core already calls); header inventory; `_migrate_candidate_library_ast1014`; extend `save_candidate` / `_parse_candidate_row` | data |
| `src/core/candidate.py` | Library-aware save/get helpers; `build_candidate_token_view`; `check_context_complete` + resume parse paths use remapped context keys; optional `debug=` library-write contract lines; Admin/create paths write columns + contact | core |
| `src/core/builder.py` | `_apply_profile_to_render_dict` reads contact blob + name columns (no `profile`) | core |
| `src/core/intake.py` | Persist/read remapped context raw keys (`raw_resume` / `raw_profile` / `raw_sample`) where it currently uses `starting_resume_text` / `linkedin_profile_text` / `sample_cover_text` | core |
| `src/ui/api/api_candidate.py` | PUT `/data` routes column fields vs `contact`/`context`/`artifacts`; signature-image validation under `contact`; GET returns columns + migrated `candidate_data`; create/admin no longer write `profile` | ui |
| `src/ui/frontend/src/pages/CandidateProfile.tsx` | Load/save columns + `contact`/`context` (shapes-driven); signature image path `contact.cover_letter_signature_image` | ui |
| `src/ui/frontend/src/pages/AdminManageCandidates.tsx` | Create/edit first/last/email/pronouns against columns + contact; drop `profile.*` | ui |
| `src/ui/frontend/src/contexts/CandidateContext.tsx` | Display name / timezone from columns + `contact` | ui |
| `src/ui/frontend/src/lib/candidateLabel.ts` | Prefer table `first`/`last` | ui |
| `src/ui/frontend/src/components/Time.tsx` | Timezone from `contact.timezone` | ui |
| `src/ui/frontend/src/components/ProfileTextPage.tsx` | Edit under `contact` (not `profile`) | ui |
| `src/ui/frontend/src/components/NavigationShell.tsx` | Any `candidate_data.profile` reads → columns/contact | ui |
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | Profile/contact reads → new homes | ui |
| `src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx` | Timezone from `contact` | ui |
| `src/ui/frontend/src/pages/CandidateIntake.tsx` | Context raw key names if referenced | ui |
| `docs/features/candidate/CANDIDATE_DATA_MODEL.md` | Rewrite table + blob sections for library + columns | docs |

---

## Stage 1: Config contract — library vocabulary + shapes + tokens

**Done when:** `CANDIDATE_LIBRARY_CONFIG` is the sole source for blob key lists and context remaps; DATA_SHAPES Profile detail uses column keys + `contact.*` / remapped `context.*`; TOKEN_SOURCES resolve names from columns and contact/context from the new paths; no remaining `profile.` keys in DATA_SHAPES or TOKEN_SOURCES.

1. In `src/utils/config.py`, add `CANDIDATE_LIBRARY_CONFIG` immediately after `CANDIDATE_CONFIG` with these literal keys (no `os.environ`):

```python
CANDIDATE_LIBRARY_CONFIG = {
    "contact_keys": (
        "contact_email", "reply_email", "phone", "location",
        "github", "linkedin_url", "websites", "timezone",
        "cover_letter_signature", "cover_letter_signature_image",
        "title_patterns", "reason_codes",
    ),
    "context_keys": (
        "bio_summary", "backstory", "strengths", "priorities", "deal_breakers",
        "writing_preferences", "hopes", "interests", "concerns",
        "raw_resume", "raw_profile", "raw_sample",
    ),
    "context_key_remap": {
        "starting_resume_text": "raw_resume",
        "linkedin_profile_text": "raw_profile",
        "sample_cover_text": "raw_sample",
    },
    "name_columns": ("first", "last", "full", "pronouns"),
    "linkedin_url_base": "https://www.linkedin.com/in/",
    "github_url_base": "https://github.com/",
    "full_name_join": " ",  # join non-empty first + last when recomputing `full`
}
```

⚠️ **Decision:** Keep the three library blobs **inside** `candidate_data` (`contact` / `context` / `artifacts`) rather than three new SQL JSON columns. Parent AC requires three blobs **and** name/pronoun **table columns**; nesting the blobs under the existing JSON column matches today’s persistence pattern and avoids dual homes. Meta keys (`lifecycle`, `pending_craft_generations`, `intakes_old`) stay as **siblings** of the three blobs under `candidate_data` — not inside contact/context/artifacts.

⚠️ **Decision:** Rename `profile` → `contact`. Identity/comms leave freeform context; high-frequency name/pronoun tokens leave the blob for columns. Non-comms fields that Profile already edits (`timezone`, signatures, `title_patterns`, `reason_codes`) stay on **contact** so Profile keeps one blob home (they are not context prose and not rubric artifacts).

⚠️ **Decision:** Add empty `hopes` / `interests` / `concerns` to the context vocabulary now (Topic Menu inputs per parent); do not populate them in this ticket.

2. Update `DATA_SHAPES["candidates"]["detail"]["profile"]` Contact Information fields:

| Old key | New key |
|---------|---------|
| `profile.first` | `first` (top-level on the edit values object) |
| `profile.last` | `last` |
| `profile.pronoun_preference` | `pronouns` |
| `profile.contact_email` | `contact.contact_email` |
| `profile.reply_email` | `contact.reply_email` |
| `profile.phone` | `contact.phone` |
| `profile.location` | `contact.location` |
| `profile.github` | `contact.github` |
| `profile.linkedin_url` | `contact.linkedin_url` |
| `profile.timezone` | `contact.timezone` |
| `profile.cover_letter_signature` | `contact.cover_letter_signature` |
| `profile.cover_letter_signature_image` | `contact.cover_letter_signature_image` |
| `profile.title_patterns` | `contact.title_patterns` |
| `context.sample_cover_text` | `context.raw_sample` |
| `context.linkedin_profile_text` | `context.raw_profile` |
| `context.starting_resume_text` | `context.raw_resume` |
| `context.bio_summary` | unchanged |

Pronoun select `options` must continue to mirror `PRONOUN_PREFERENCE_OPTIONS` (same five values + empty “(not set)”); do not invent a second option list.

3. Update `TOKEN_SOURCES`:

| Token | New path / behavior |
|-------|---------------------|
| `FIRST_NAME` | `first` (column; see Stage 3 token view) |
| `LAST_NAME` | `last` |
| `FULL_NAME` | **new** token → `full` |
| `CONTACT_EMAIL` … `LINKEDIN_URL`, `LOCATION`, `GITHUB` | `contact.<key>` |
| `TITLE_PATTERNS`, `REASON_CODES`, `COVER_LETTER_SIGNATURE` | `contact.<key>` |
| `STARTING_RESUME_TEXT` | `context.raw_resume` (token **name** unchanged for prompt authors) |
| `LINKEDIN_PROFILE_TEXT` | `context.raw_profile` |
| `SAMPLE_COVER_TEXT` | `context.raw_sample` |
| other context / artifact tokens | same keys under `context.` / `artifacts.` |

4. Change `_pronoun_preference_key` to read preference from the token-view key `pronouns` (string column value), still defaulting invalid/empty to `PRONOUN_PREFERENCE_DEFAULT` via `PRONOUN_FORMS`.

5. Update every config path that still references `profile.title_patterns` or old context raw keys for intake/bootstrap required-field lists (search `profile.` and `starting_resume_text` / `linkedin_profile_text` / `sample_cover_text` in `config.py`) to the new homes. Do not add `PREAMBLE_CONFIG`.

---

## Stage 2: Data layer — columns + idempotent library migration

**Done when:** Fresh and existing DBs expose `first`/`last`/`full`/`pronouns` on `get_candidate`; one-time migration remaps `profile`→`contact`, lifts names/pronouns to columns, remaps context raw keys, seeds empty hopes/interests/concerns, and leaves **no** `profile` key and **no** old context raw keys on migrated rows; `save_candidate` can set columns and deep-merge library blobs; header inventory lists the new columns.

1. In `_ensure_candidate_schema`, extend CREATE TABLE and the idempotent ALTER loop with:

| Column | Def |
|--------|-----|
| `first` | `TEXT` |
| `last` | `TEXT` |
| `full` | `TEXT` |
| `pronouns` | `TEXT` |
| `state_history` | `TEXT DEFAULT '[]'` |

⚠️ **Decision:** While touching `save_candidate` / `_parse_candidate_row` / schema ensure, **wire `state_history`** (column + JSON parse + optional kwarg, preserve-when-omitted on update) to match what `src/core/candidate.py` already passes (`initiate_candidate` / `transition_candidate_state`) and what `CANDIDATE_DATA_MODEL.md` / AST-971 already document. This is unblock for the same upsert path — not Progress UI and not a new product feature.

2. Update the module header inventory `candidate — …` bullet to list: `state`, `state_history`, `candidate_data` (contact/context/artifacts + meta), `first`, `last`, `full`, `pronouns`, `candidate_api_key`, timestamps.

3. In `_parse_candidate_row`: keep parsing `candidate_data`; parse `state_history` to list (invalid/missing → `[]`); leave `first`/`last`/`full`/`pronouns` as plain strings (NULL → `""` or `None` consistently — use `""` for missing so UI selects work).

4. Extend `save_candidate` keyword-only args: `first`, `last`, `full`, `pronouns`, `state_history` (optional). On INSERT/UPDATE, set only provided name/pronoun columns. `candidate_data` merge behavior unchanged (deep-merge when `merge=True`).

5. Add `_migrate_candidate_library_ast1014(conn)` called from `_ensure_candidate_schema` **after** existing `_migrate_candidate_data_structure` / pronoun / context-array migrations. Idempotent probe: skip a row when `candidate_data` has `contact` and lacks `profile`, and context lacks old remap source keys, and name columns are already populated when profile had names. For each row that still needs work:

   - Parse `candidate_data`.
   - If `profile` dict present: copy contact-eligible keys into `contact` (from `CANDIDATE_LIBRARY_CONFIG["contact_keys"]`); copy `first`/`last` into columns if column empty; set `pronouns` from `profile.pronoun_preference` if column empty; **delete** `profile`.
   - Ensure `contact` / `context` / `artifacts` dicts exist.
   - Apply `context_key_remap`: for each old→new, if old in context and new absent, move value; always `pop` old key.
   - For each of `hopes`, `interests`, `concerns`: if missing, set `""`.
   - Recompute `full` when empty: join non-empty `first` and `last` with `full_name_join`.
   - If `pronouns` empty/invalid, set `PRONOUN_PREFERENCE_DEFAULT`.
   - Write columns + `candidate_data` JSON; commit.

6. Do **not** keep dual keys (`profile` alongside `contact`, or `starting_resume_text` alongside `raw_resume`) after migration — that would be a shadow copy (parent AC).

---

## Stage 3: Core library helpers + readers/writers

**Done when:** All core paths that read/write identity, contact, or context raw sources use columns + `contact`/`context`/`artifacts`; `build_candidate_token_view` feeds `resolve_tokens`; LinkedIn/GitHub URL-or-username normalization runs on contact save; library writes honor `debug=True` contract lines; builder/intake use remapped keys.

1. In `src/core/candidate.py`, add:

```python
def build_candidate_token_view(candidate: dict) -> dict:
    """Walkable dict for resolve_tokens: name columns + library blobs (no meta)."""
```

   Shape:

```python
{
  "first": candidate.get("first") or "",
  "last": candidate.get("last") or "",
  "full": candidate.get("full") or "",
  "pronouns": candidate.get("pronouns") or "",
  "contact": (candidate.get("candidate_data") or {}).get("contact") or {},
  "context": (candidate.get("candidate_data") or {}).get("context") or {},
  "artifacts": (candidate.get("candidate_data") or {}).get("artifacts") or {},
  "_astral_candidate_id": candidate.get("astral_candidate_id") or "",
}
```

   Every `resolve_tokens(..., candidate_data=cd)` call site that today passes raw `candidate_data` for name/contact/context tokens must pass this view (or an equivalent merge). Prefer updating the call sites that load a full candidate row; do not invent a second resolver.

2. Add `normalize_contact_urls(contact: dict) -> None` (mutates in place): for `linkedin_url` and `github`, if value is non-empty and has no `://`, prepend `CANDIDATE_LIBRARY_CONFIG` URL bases (strip leading `@`). This is library coercion, **not** Ruth validation (AST-1015).

3. Add `recompute_full_name(first: str, last: str) -> str` using `full_name_join`.

4. Extend `save_candidate_data` (or add `save_candidate_library`) so PUT-shaped bodies may include top-level `first`/`last`/`full`/`pronouns` plus `contact`/`context`/`artifacts` (+ meta). Implementation:

   - Pop column keys → `database.save_candidate(..., first=..., last=..., full=..., pronouns=...)`.
   - When `first` or `last` provided and `full` omitted, set `full=recompute_full_name(...)`.
   - On `contact` dict: run `normalize_contact_urls`; deep-merge via existing save.
   - Reject body key `profile` with `ValueError("profile was renamed to contact; refuse shadow write")` so divergent copies cannot land.
   - Accept optional `debug: bool = False`. When `debug=True`, emit §1.5.1 lines via `get_logger(..., debug_flag=debug)`: one `debug_index` header per logical write step (e.g. columns, contact, context, artifacts) with primary id = `astral_candidate_id` and outcome found/recorded; long blobs through `truncate_debug_content`. No new debug lines when `debug=False`.

5. Update `check_context_complete` to read remapped context keys if it references old names (keep gate field set from config — do not invent new completeness rules beyond key renames).

6. Update `parse_candidate_resume` / any reader of `starting_resume_text` to `context.raw_resume`; write structured output only to `artifacts` as today.

7. Update `initiate_candidate` / `save_candidate_admin` / Manage-Candidates create path helpers: accept names + pronouns as columns; contact email into `contact`; never write `profile`.

8. In `src/core/builder.py`, change `_apply_profile_to_render_dict` callers to pass **contact** plus inject `first`/`last`/`full` from columns into the render dict (rename helper to `_apply_contact_to_render_dict` if that keeps the file clearer — one rename, update all call sites in this file).

9. In `src/core/intake.py`, replace persistence/read of `starting_resume_text` / `linkedin_profile_text` / `sample_cover_text` with `raw_resume` / `raw_profile` / `raw_sample`. Parameter names on Python functions may keep the old names only if that avoids a wide churn **and** the plan step documents the mapping at the call boundary; prefer renaming parameters to the new keys when the function is already being edited.

---

## Stage 4: API + Profile/Admin UI — one home, no divergent copies

**Done when:** GET `/api/candidates/<id>` returns columns at top level and `candidate_data` without `profile`; PUT `/data` saves columns + contact/context/artifacts; Candidate Profile and Admin Manage Candidates edit first/last/pronouns/contact against the new homes and round-trip; timezone/signature/title-pattern pages that used `profile` use `contact`.

1. In `src/ui/api/api_candidate.py` `update_candidate_data`:

   - Treat top-level `first`/`last`/`full`/`pronouns` as column updates (via Stage 3 saver).
   - Validate signature image under `contact.cover_letter_signature_image` (same rules as today’s `profile` path).
   - Artifact / rubric / company_search_terms handling stays on `artifacts` (unchanged logic, new blob name already `artifacts`).
   - Do not accept `profile` in the body (propagate Stage 3 `ValueError` as 400).

2. `get_candidate_detail` / list sanitization: after hydrate, ensure response includes `first`/`last`/`full`/`pronouns` from columns; `candidate_data` has `contact` not `profile`.

3. `create_candidate`: map POST body so Admin can send `candidate_data.contact` + top-level names, or nested create payload documented in this step — Admin UI (step 5) must match.

4. `CandidateProfile.tsx`: build edit `values` as `{ first, last, pronouns, contact, context, ... }` from GET (columns + `candidate_data` sections). Save PUTs that object. Update signature image path to `contact.cover_letter_signature_image`. Keep FormFields/shapes-driven — no hardcoded field lists beyond signature/base-resume special cases already present.

5. `AdminManageCandidates.tsx`: add/edit forms read/write `first`/`last`/`pronouns` columns and `contact.contact_email` (and any other contact fields already in the modal). Remove `profile` / `pronoun_preference` nested under `candidate_data` on create/save. Pronoun field still driven from shapes (find field by key `pronouns`).

6. Update the remaining frontend files in the Files Changed table that read `candidate_data.profile` so they use columns and/or `contact` (timezone → `contact.timezone`; display name → `first`/`last`/`full`).

7. Smoke-check by inspection: no `profile.` string left in `src/ui/frontend/src` for candidate data paths (grep). Allow comments/history only if unavoidable — prefer zero.

---

## Stage 5: Data model doc

**Done when:** `CANDIDATE_DATA_MODEL.md` matches the shipped library + columns; no stale `profile` section as the identity home.

1. Rewrite `docs/features/candidate/CANDIDATE_DATA_MODEL.md`:

   - Document table columns `first`, `last`, `full`, `pronouns`, `state_history`.
   - Document `candidate_data` top-level: `contact`, `context`, `artifacts`, plus meta (`lifecycle`, `pending_craft_generations`, `intakes_old`).
   - Contact / context / artifacts key tables per Stages 1–2 (including remaps and hopes/interests/concerns).
   - Token table: column-backed name/pronoun tokens; contact/context paths; `FULL_NAME`.
   - Explicit rule: do **not** store first/last/full/pronouns inside contact/context/artifacts; do **not** store contact handles as context prose.

---

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — data schema + migration, config contract, core readers/writers (candidate/builder/intake), API, and Profile/Admin frontend all move from `profile` + nested names to columns + `contact` library.

**Conf:** `high` — remap and column lift follow existing `_migrate_candidate_*` / DATA_SHAPES / TOKEN_SOURCES patterns; boundaries with AST-1015/1016/1017 are explicit.

**Risk:** `HIGH` — nearly every candidate identity/token path changes; a missed `profile` reader would show blank names or break resume render / Admin create. Migration must be idempotent and shadow-copy-free.

---

## Code rules self-review

- **§2.1:** Library vocabulary and remaps live in `CANDIDATE_LIBRARY_CONFIG`; no inline key sets in migration/UI.
- **§1.3:** One remap table, one URL normalizer, one full-name join helper — no duplicated remap dicts in data vs core.
- **§1.5.1:** Library write path accepts `debug=` and emits contract lines only when true; data layer still does not log.
- **§2.4 / §2.6:** No new batch primitives; no candidate state vocabulary changes.
- **§3.3:** UI → core/utils only; data migration imports config options already used by pronoun backfill.
- **§3.5:** Frontend keeps shapes-driven Profile fields; PascalCase components / snake_case API unchanged.
- **Out of scope enforced:** no Ruth agent_task, no `PREAMBLE_CONFIG`, no mechanical preamble UI.

---

## Review

**Publish ref:** `sub/AST-952/AST-1014-contact-context-artifacts-library`
**Build tip:** `c907a7c40d9c5eedc30abf985ec4f72b56bc5626`

### Radia — code-rubric.v1 (`[code-rubric] revision=1`)

**Tip reviewed:** `95faf77a50cdfce39366fb957df151ecd8f7b74a` (`origin/sub/AST-952/AST-1014-contact-context-artifacts-library` vs `origin/dev`)
**Overall:** FIX-NOW

#### What’s solid
- `CANDIDATE_LIBRARY_CONFIG` owns keys/remaps/URL bases; DATA_SHAPES + TOKEN_SOURCES moved off `profile.*`.
- Idempotent `_migrate_candidate_library_ast1014` (profile→contact, column lift, context remaps, hopes/interests/concerns seed); refuses `profile` writes in core.
- Profile/Admin UI + builder/gazer/monitor/intake persistence remapped; Betty test split clean (`test` / `merge-tests` vs engineer `code`).

#### Issues
1. **fix-now** — `src/ui/api/api_admin.py` still feeds raw `candidate_data` into `resolve_tokens` / preview helpers (`_resolve_agent_preview_candidate`, `_enrich_tasks`, `_resolve_adhoc`). After TOKEN_SOURCES → columns + `contact.*`, Admin task/adhoc name+contact tokens blank. Plan Stage 3.1: every full-row `resolve_tokens` site must use `build_candidate_token_view`.
2. **fix-now** — `update_candidate_data` calls `save_candidate_data(...)` without `debug=ui_llm_debug()`; Stage 3 / parent AC8 debug contract is dead on the primary PUT path.
3. **fix-now** — `src/core/agent.py` function-scoped `from src.core.candidate import build_candidate_token_view` lacks an in-code cycle-break / lazy-load comment (B1; sibling import two lines below has one).
4. **discuss** — straggler: Joan excluded `astral.git.engineer-test-tree-ban` at plan time; diff includes `tests/**` + `docs/test-bible/**`. Statute itself **conforms** (Betty `test`/`merge-tests` only).

#### Recommended actions
- Wire `build_candidate_token_view(candidate)` (or equivalent merge) at all `api_admin` full-row token sites.
- Pass `debug=ui_llm_debug()` into `save_candidate_data` from `update_candidate_data`.
- Add the lazy-import cycle comment on the new `agent.py` import.

#### Notes
Joan plan-rubric verdict attached (APPROVED). Excluded set: `astral.debug.no-repo-root-artifacts-dir`, `astral.git.engineer-test-tree-ban`, `astral.layers.scripts-exempt-from-layer-rules`.

## Resolution

**2026-07-28** — resolve-child vs `[code-rubric] revision=1` (FIX-NOW)

1. **fix-now / api_admin** — `_resolve_agent_preview_candidate`, `_enrich_tasks`, and `_resolve_adhoc` now pass `build_candidate_token_view(candidate)` into `resolve_tokens` / preview helpers (name columns + `contact.*`).
2. **fix-now / api_candidate** — `update_candidate_data` calls `save_candidate_data(..., debug=ui_llm_debug())` so Stage 3 / AC8 gated debug lines fire on primary PUT.
3. **fix-now / agent.py** — lazy-import comment added on `build_candidate_token_view` (same cycle-break note as sibling import).
4. **discuss** — engineer-test-tree-ban straggler: acknowledged; statute already conforms (Betty-only test/bible commits). No product change.

---

## Bug: AST-1904 — Keep full saved contact line on resume render

Fix child of mini-parent AST-1902 (*Candidate Contact Detail is truncated after email*, project Astral Artifacts). Publish ref `sub/AST-1902/AST-1904-keep-full-saved-contact-line`, parent `ftr/AST-1902-candidate-contact-detail-truncated`. This block covers only the contact-line overwrite that Stage 3 step 8 above re-sourced. It does not bring in any other AST-1014 scope.

### As-is

`build_resume_from_job` and `build_base_resume` call `_apply_contact_to_render_dict` after content loads. Whenever at least one contact-blob field is non-empty, it replaces `render["candidate_contact_detail"]`, even when the blob has fewer parts than the saved line. A `job_resume` saved with `hire@susansomerset.com • 415-745-5238 • linkedin.com/in/susansomerset • California, USA (PST)` renders as `<div class="contact"><span>hire@susansomerset.com</span></div>` when the blob holds only the email.

### To-be

A non-empty saved `candidate_contact_detail` renders exactly as saved. The line built from the contact blob is used only when the saved content has no contact line (missing, empty, or whitespace-only).

### Repro

Fixture (persistence is JSON, so this is a literal dict, not a seeded DB row). Run against `origin/ftr/AST-1902-candidate-contact-detail-truncated` @ `777c04a81`:

```python
from src.core.builder import _apply_contact_to_render_dict as f
r = {"candidate_name": "Susan Somerset",
     "candidate_contact_detail": "hire@susansomerset.com • 415-745-5238 • linkedin.com/in/susansomerset • California, USA (PST)"}
f(r, {"contact_email": "hire@susansomerset.com"}, full="Susan Somerset")
r["candidate_contact_detail"]   # -> 'hire@susansomerset.com'   (BUG: phone / LinkedIn / location dropped)

r = {"candidate_contact_detail": ""}
f(r, {"contact_email": "a@b.c", "phone": "555"})
r["candidate_contact_detail"]   # -> 'a@b.c\xa0• 555'           (fallback path, must keep working)
```

End to end, the same happens through `build_resume_from_job` (L255) and `build_base_resume` (L447). `_emit_html_document` (L1242) escapes and emits whatever `render["candidate_contact_detail"]` holds by then.

### Root cause

`src/core/builder.py` `_apply_contact_to_render_dict` (L1028–1050) ends with `if parts: render["candidate_contact_detail"] = "\u00a0• ".join(parts)`. It never checks whether the render already holds a contact line. This unconditional overwrite came over from the pre-AST-1014 `_apply_profile_to_render_dict`. Stage 3 step 8 only re-pointed it at the contact blob plus the name columns. The bug shows up when the blob is sparser than the saved artifact line.

### Proposed change

**Choice: option (a). A saved artifact `candidate_contact_detail` wins, and the contact blob is only a fallback.**

Why (a) and not (b), "blob stays authoritative but never emits fewer parts than the saved line":

- **Smaller change.** (a) changes one condition in one function. Neither the signature nor the two call sites change, and `src/utils/config.py` is untouched.
- **No heuristic.** `candidate_contact_detail` is freeform text. To count its "parts", (b) would have to split on an assumed `•` separator, and nothing in config declares that separator. A line saved with `|`, `,` or line breaks would count as one part, so the bug would come back. Doing (b) properly would need a new config field for separator and precedence. That is a bigger change and a heuristic that has not been approved.
- **Meets AC 1–3 directly.** AC1: the saved line is kept. AC2: both builders go through this one helper. AC3: an empty or missing saved line still falls back to the blob.

Edit to `src/core/builder.py` `_apply_contact_to_render_dict`:

1. Update the docstring to say that `candidate_name` is still overwritten from the name columns, and that `candidate_contact_detail` is filled from the contact blob only when the render has no non-empty saved line (AST-1904).
2. Before building `parts`, return early when a saved line already exists. Normalize the value the same way `_emit_html_document` does at L1242:

```python
    # AST-1904: a saved artifact contact line wins; the blob is only a fallback.
    if str(render.get("candidate_contact_detail") or "").strip():
        return
```

   Place this **after** the `candidate_name` block (L1030–1032), so the name-column overwrite still runs whatever the contact line holds. Leave the rest of the function (the part list, `if parts:` assignment and NBSP-bullet join) unchanged. A whitespace-only saved value counts as empty and falls back to the blob.

3. Do not change `build_resume_from_job`, `build_base_resume`, `build_resume_from_paste`, `_emit_html_document`, or `src/utils/config.py`.

⚠️ **Decision (consequence of (a)):** if a job resume or base resume already has a saved contact line, later edits to the Profile contact blob will not change that resume's header. To change it, edit the saved `candidate_contact_detail`. This is the trade-off built into (a), which AST-1902 offered as acceptable, and the blob still covers resumes with no saved line.

### Blast radius

- **Callers:** `build_resume_from_job` (L255) and `build_base_resume` (L447) only. `build_resume_from_paste` already skips this helper (L528). Session builders (`build_session_base_resume`, etc.) do not call it.
- **Tests that rely on the current overwrite.** `tests/component/core/test_builder.py`: the `_resume_blob()` fixture (L17–23) always sets `candidate_contact_detail: "ada@example.com"`, so under (a) these asserts change outcome:
  - `TestBuilderHelpers::test_applies_profile_contact_and_markers`: `assert "555" in render["candidate_contact_detail"]` (L366) will fail, because the saved `ada@example.com` now wins.
  - `TestBuilderHelpers::test_profile_uses_reply_email_and_skips_empty_name`: `assert "reply@example.com" in ...` (L382) will fail for the same reason.
  - `TestAst1014BuilderContact::test_apply_contact_uses_full_column_over_first_last` (L2965) still passes, but only because the saved value and the blob value are both `ada@example.com`.
  - For Betty (fix-board / qa-fix): these blob-fallback asserts need `_resume_blob(candidate_contact_detail="")`, or an equivalent, to keep testing the fallback path. The new AST-1904 regression goes in `TestAst1014BuilderContact`, as the scope lists. This plan does not touch `tests/`.
- **Other suites** with `candidate_contact_detail` mentions (`test_candidate`, `test_config`, `test_tracker`, `test_agent`, `test_api_candidate`) do not call `_apply_contact_to_render_dict`, so they are not expected to change. test-fix confirms this.
- **Data / UI:** no schema, contact-library, Profile UI, `.contact` CSS, or `draft_job_resume` change (AST-1904 Boundaries).

### What must still hold

- AST-1014 Stage 3 step 8: `candidate_name` is still taken from `full`, else `first last`, and is left alone when both are blank.
- If there is no saved line, the header contact line is still built from the blob in this order: `contact_email`/`reply_email`, `phone`, `linkedin_url`, `github`, `location`, joined with `"\u00a0• "` (AST-1904 AC3).
- The saved line is emitted exactly as saved, only HTML-escaped at L1242. The builder does not rewrite, merge, or reorder it (AC1).
- Both `build_resume_from_job` and `build_base_resume` behave the same way, because both go through this one helper (AC2).
- The paste path (`build_resume_from_paste`) is unchanged.

### Joan fix-board — AST-1904

```text
[board-joan]  CANON: OK

Overlap skim (no `docs/canon-index.md` on publish ref; `canon/docs/DIRECTIVES-DIRECTORY.md` + `canon/statutes/**` on tip): `src/core/builder.py` `_apply_contact_to_render_dict` only. Frozen Canon Scope on AST-1902 / AST-1904: none cited (mini-parent bug; triage via roster overlap, not R1–R7).

`astral.config.config-source-of-truth` / `patt.config.block`: plan keeps join order and `CANDIDATE_LIBRARY_CONFIG` untouched; early-return when a non-empty saved `candidate_contact_detail` is present does not add literals or move precedence into `config.py`. Fallback path unchanged (AC3).

`patt.core.logical-scope` (builder): one conditional guard; no layer/import/signature churn. `patt.artifact.parse-validate-persist` / build lifecycle: persisted resume JSON is still emitted HTML-escaped at render; fix stops sparser contact blob from overwriting a richer saved artifact line — no statute requires unconditional blob overwrite.

Option (a) vs (b) and Profile-blob staleness when a saved line exists are product trade-offs already accepted in the AST-1902 / plan-fix patch, not an in-force statute conflict or new architectural precedent (`orch.pipeline.call-susan-for-product-decisions` scope is plan-fix, not F2 canon landing).

No directive id needs amendment or a one-line carve-out for F3.

context_tokens≈12000
```

### Radia review-fix — AST-1904

```
[code-rubric]
**Ticket:** AST-1904
**Publish ref:** 7479f320aaa372f734fa192769487e8473dafb1e (`origin/sub/AST-1902/AST-1904-keep-full-saved-contact-line`)
**Diff base:** `origin/ftr/AST-1902-candidate-contact-detail-truncated...origin/sub/AST-1902/AST-1904-keep-full-saved-contact-line` (2 files: `src/core/builder.py` + plan-fix doc block)
**Corpus:** `bd68954dc854ca80fca1fc391821dff9ff288a7a` (canon tree at publish tip; no `docs/canon-index.md` on ref — same shape Joan used at fix-board)
**Overall:** CLEAN

## Canon scores

(no rows) — AST-1904 Linear Description has no locked `## Canon Scope` / frozen directive ids; Joan `[board-joan] CANON: OK` on AST-1904 explicitly records *Frozen Canon Scope on AST-1902 / AST-1904: none cited* (mini-parent bug; roster overlap at F2, not R1–R7). Nothing on the frozen list to score; no off-list statute scored as a grade.

## Column diff vs plan stage

no plan-stage scores attached (`validate-plan` fix-mode did not run; fix-board only)

## Frame diff

(none)

### Fix-specific checks

- **[bug-repro]** not applicable — clean board opt-out: `qa-fix` did not run on this ticket; Betty’s `TESTS: REVISE` test work was gap-split to **AST-1905**. No `[bug-repro]` on this tip by design; not scored as missing here.
- **`## What must still hold`** — OK. Traced against `src/core/builder.py` `_apply_contact_to_render_dict` @ publish tip:
  - `candidate_name` still overwritten from `full` / `first last` **before** the AST-1904 guard (L1031–1033).
  - Fallback path unchanged: same field order and `"\u00a0• ".join(parts)` (L1037–1054).
  - Non-empty saved line preserved via early `return` after `.strip()` (L1035–1036); matches plan normalization intent vs `_emit_html_document` contact escape at L1246 (`str(... or "").strip()` on read path).
  - `build_resume_from_job` / `build_base_resume` still call the helper only (L255, L447); `build_resume_from_paste` still skips it (L528) — untouched in diff.

## Findings

**advisory**

- **Sibling test carry / split scope:** Diff is product-only (`builder.py` + `## Bug: AST-1904` plan patch). Two `TestBuilderHelpers` failures on tip vs ftr are expected per plan **Blast radius** and Ada’s test-fix comment; owned by **AST-1905**, not a defect on this publish ref.
- **AC proof on tip:** Behavioral AC 1–3 are implemented by the guard; automated regression + helper fixture repoint land on AST-1905. Acceptable given explicit gap split; UAT should use plan **Repro** or wait for AST-1905 green manifest for full test lock.

**fix-now:** (none)

**discuss:** (none)

## Notes

- **Canon Scope:** Empty frozen list is consistent with fix-board; overlapping draft/statute skim (config SoT, logical-scope, artifact lifecycle) was already litigated at F2 with **CANON: OK**. No Canon Scope gap requiring **ESCALATE** for unstated ids on this micro-diff.
- **Plan fidelity:** Matches plan-fix **Proposed change** option (a) — docstring update + early return after name block; no `config.py`, call-site, or paste-path edits.
- **Estimate footprint:** Estimate **2** vs ~5-line product change + doc — fits.
- **Parent shape (Chuckles §8):** Mini-parent **AST-1902** with live `ftr/AST-1902-candidate-contact-detail-truncated` — **not** the orphaned-parent → straight-`dev` merge path. Clean review → **Review Posted** → `do-all-the-things` §3h shortcut → **User Testing** (`resolve-child` skipped). Product fix may ride with AST-1905 test work on the same ftr stack; no `merge-child`/`prep-uat` epic semantics.

## What’s solid

- Minimal, plan-faithful guard; fallback and name precedence unchanged; boundaries respected (no schema/UI/config/test tree on this ticket).

context_tokens≈9500
```

```
[code-rubric] PROCEED (Commit: 7479f320a) saved line wins guard
```

### Resolution — AST-1904

docs-acceptance: product-only fix. The regression test and the two `TestBuilderHelpers` fixture repoints (Betty `[board-betty] TESTS: REVISE`) land on gap sibling AST-1905, stacked after this ticket on `ftr/AST-1902-candidate-contact-detail-truncated`.

---

## Bug: AST-1905 — Cover saved contact line vs sparse contact blob on resume render

Test-gap sibling of AST-1904, filed from Betty's `[board-betty] TESTS: REVISE` on AST-1904. Mini-parent AST-1902. Publish ref `sub/AST-1902/AST-1905-cover-saved-contact-line-tests`. **Tests and bible only.** Betty lands them via qa-fix, and nothing in `src/` changes. The product fix is AST-1904's early return, already on `ftr/AST-1902-candidate-contact-detail-truncated` @ `7479f320a` and brought onto this sub by sync-child.

### As-is

Now that AST-1904's early return is on the tip, two existing tests fail. `_resume_blob()` (`tests/component/core/test_builder.py` L17–23) always saves `candidate_contact_detail: "ada@example.com"`, and that saved line now wins over the blob:

- `TestBuilderHelpers::test_applies_profile_contact_and_markers`: `assert "555" in render["candidate_contact_detail"]` (L366)
- `TestBuilderHelpers::test_profile_uses_reply_email_and_skips_empty_name`: `assert "reply@example.com" in render["candidate_contact_detail"]` (L382)

No test covers the AST-1904 bug itself (a multi-part saved line replaced by a sparser blob).

### To-be

- Both `TestBuilderHelpers` tests pass on the post-fix tip and still exercise the blob-built line.
- A new regression test in `TestAst1014BuilderContact` fails on `origin/dev`'s pre-fix `src/core/builder.py` and passes on this tip.
- The bible records the new and revised coverage.

### Repro

Checked with a standalone script that calls `_apply_contact_to_render_dict` with the exact inputs planned below. No `tests/` file was touched. It ran against `origin/dev`'s `src/core/builder.py` (pre-fix) and against this tip (`3fcc8388c`, which carries AST-1904's fix):

| Scenario (inputs as in Proposed change) | `origin/dev` | tip |
|---|---|---|
| New regression: multi-part saved line + email-only blob keeps the saved line, and `candidate_name` is overwritten | **fails** | passes |
| New guard: whitespace-only saved line falls back to the blob | passes | passes |
| Repointed L366 (`candidate_contact_detail=""` + full blob → contains `"555"`) | passes | passes |
| Repointed L382 (`candidate_contact_detail=""` + `reply_email` blob → contains `reply@example.com`) | passes | passes |

The first row is the red→green bug-repro gate (AST-1905 AC1). The other rows guard AST-1904's "What must still hold" and are meant to pass on both trees.

### Root cause

The test gap: the only fixture feeding `_apply_contact_to_render_dict` always carries a non-empty saved contact line, so the helper tests only ever exercised blob-over-saved, never an empty saved line. When AST-1014 re-sourced the helper, no case paired a rich saved line with a sparse blob. That is why the bug shipped untested.

### Proposed change

All edits are in `tests/component/core/test_builder.py` and `docs/test-bible/core/{builder,candidate}.md`, and Betty makes them (qa-fix). Do not change `_resume_blob()` itself. Other suites rely on its saved `ada@example.com`, including `TestAst1014BuilderContact::test_apply_contact_uses_full_column_over_first_last` (L2955).

1. **Repoint `TestBuilderHelpers::test_applies_profile_contact_and_markers` (L349).** Change the fixture call at L350 to `_resume_blob(candidate_contact_detail="", professional_summary="__keep~~dash", experience={"role": "lead"})`. Leave everything else as-is, including the five-field contact blob, the marker asserts, and `assert "555" in render["candidate_contact_detail"]`.

2. **Repoint `TestBuilderHelpers::test_profile_uses_reply_email_and_skips_empty_name` (L379).** Change the first fixture call only (L380) to `_resume_blob(candidate_contact_detail="")`. Leave the second half (`_resume_blob(candidate_name="Keep")` with `{}` contact and blank names → `candidate_name == "Keep"`) unchanged. With an empty blob it produces no parts, so the saved line doesn't matter there.

3. **Add `TestAst1014BuilderContact::test_saved_multi_part_contact_line_survives_email_only_blob`** (the AST-1904 bug-repro, which must fail on `origin/dev`):

```python
    def test_saved_multi_part_contact_line_survives_email_only_blob(self) -> None:
        # AST-1904: a saved line with more parts than the blob must not be replaced.
        saved = "hire@example.com\u00a0• 415-555-0100\u00a0• linkedin.com/in/ada\u00a0• London, UK"
        render = _resume_blob(candidate_name="Old", candidate_contact_detail=saved)
        builder_mod._apply_contact_to_render_dict(
            render, {"contact_email": "hire@example.com"}, full="Ada Lovelace"
        )
        assert render["candidate_contact_detail"] == saved
        assert render["candidate_name"] == "Ada Lovelace"
```

   Assert exact equality on `candidate_contact_detail`, not a substring check. On `origin/dev` the value becomes `"hire@example.com"`, and a substring check on the email would wrongly pass. The `candidate_name` assert locks AST-1904's rule that the name-column overwrite still runs.

4. **Add `TestAst1014BuilderContact::test_whitespace_saved_contact_line_falls_back_to_blob`** (fallback guard, passes on both trees):

```python
    def test_whitespace_saved_contact_line_falls_back_to_blob(self) -> None:
        # AST-1904: whitespace-only saved line counts as empty; blob line is built.
        render = _resume_blob(candidate_contact_detail="   ")
        builder_mod._apply_contact_to_render_dict(
            render, {"contact_email": "ada@example.com", "phone": "555"}
        )
        assert render["candidate_contact_detail"] == "ada@example.com\u00a0• 555"
```

5. **Bible, `docs/test-bible/core/builder.md` § AST-1014 · AST-952 (L415).** Under the existing paragraph, add one line: AST-1904 revision (AST-1905): the saved `candidate_contact_detail` wins and the blob is the fallback. It names `TestAst1014BuilderContact::test_saved_multi_part_contact_line_survives_email_only_blob` (bug-repro, red on pre-fix builder) and `::test_whitespace_saved_contact_line_falls_back_to_blob`, and says the `TestBuilderHelpers` contact tests now pass `candidate_contact_detail=""` to exercise the blob-built line.

6. **Bible cross-ref, `docs/test-bible/core/candidate.md` § AST-1014 · AST-952 (L667, the primary home).** Add a one-line cross-reference to `builder.md` § AST-1014 for the AST-1904/AST-1905 revision. No manifest change: that section's manifest (L694–695) already runs `TestAst1014BuilderContact` and `TestBuilderHelpers` whole-class, so the new functions are picked up automatically.

**Verification command** (Betty, and test-fix after her):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_builder.py::TestAst1014BuilderContact \
  tests/component/core/test_builder.py::TestBuilderHelpers -q
```

On this host set `ASTRAL_PYTHON` to a 3.10+ venv python. `ensure_component_venv.sh` only looks for `python3.10`–`3.12`, and the only interpreter here is `python3.14`. For the red gate, run the same command with `src/core/builder.py` temporarily checked out from `origin/dev`. Only `test_saved_multi_part_contact_line_survives_email_only_blob` may fail there.

### Blast radius

- **`tests/component/core/test_builder.py` only.** Two fixture-call edits in `TestBuilderHelpers` and two new functions in `TestAst1014BuilderContact`. `_resume_blob()` stays unchanged, so the other ~30 `candidate_contact_detail` references in the file are unaffected.
- Betty's board read found no other resume-render test that asserts a blob-built line over a saved one. The cover from-block suites (`TestAst1139…`, `TestAst1148…`) do not call this helper.
- **Bible:** `builder.md` and `candidate.md` § AST-1014 only. No other sections and no manifest edits.
- **No `src/` change.** The helper's callers (`build_resume_from_job`, `build_base_resume`) aren't tested end to end here because both go through this one helper. AST-1904 AC2 holds through that single code path.

### What must still hold

- AST-1905 AC3: no product code change on this ticket.
- The full `tests/component/core/test_builder.py` suite is green on this tip. On `origin/dev`'s builder only the new bug-repro test fails, and the rest matches the 190-pass ftr baseline.
- The repointed `TestBuilderHelpers` tests still assert blob-built content (`"555"`, `reply@example.com`) and the NBSP marker behavior. They are repointed, not weakened.
- `TestAst1014BuilderContact::test_apply_contact_uses_full_column_over_first_last` and `test_coerce_row_injects_name_columns_for_render` are left untouched.

### Joan fix-board — AST-1905

```text
[board-joan]  CANON: OK

Scope: **tests + `docs/test-bible/**` only** (AST-1905); no `src/**` on this publish ref. Product behavior is AST-1904 on ftr @ `7479f320a`. Frozen Canon Scope on AST-1902 / AST-1905: none cited.

Overlap skim (no `docs/canon-index.md` on ref; `canon/docs/DIRECTIVES-DIRECTORY.md` + in-force `canon/statutes/**`): `orch.roles.betty-owns-test-tree`, `astral.git.betty-no-src-or-features`, `astral.git.engineer-test-tree-ban` — delivery matches Betty/qa-fix; no engineer product landing. `astral.docs.features-single-file-per-ticket` applies to `docs/features/**`; bible rows in `docs/test-bible/core/{builder,candidate}.md` are test-tree documentation, not statute/pattern corpus.

No active directive requires amending canon to record AST-1904 precedence or test names; fixing fixture calls and adding `TestAst1014BuilderContact` regressions does not contradict `astral.config.config-source-of-truth` or any builder/contact statute (no product diff to score). Same fix-board pattern as other test-gap siblings (e.g. AST-1848): not F3 material.

context_tokens≈14000
```
