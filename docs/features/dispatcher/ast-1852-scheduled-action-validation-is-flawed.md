# AST-1852 — Scheduled Action Validation is flawed

<!-- linear-archive: AST-1852 archived 2026-10-07 -->

## Linear archive (AST-1852)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1852/scheduled-action-validation-is-flawed  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## As-is

Scheduled Actions (dispatch list / AUTO-Run gate) flags `craft_do_rubric` for candidate somerset as invalid with `IDEAL_DAY` resolving empty, even though somerset has a current Ideal Day. Other candidates with Ideal Day populated pass.

Root cause (read, not guessed): `_evaluate_dispatch_empty_render` in `src/ui/api/api_admin.py` loads the candidate with raw `database.get_candidate(cid)` and passes it to `build_candidate_token_view` with no operative artifact overlay. Since the AST-1643 migration (AST-1659 blob retirement / AST-1660 Ideal Day wire-up), an Ideal Day saved through the UI goes only to the artifacts table and is popped out of `candidate_data.context`. So `{$IDEAL_DAY}` walks `context.ideal_day`, finds nothing, and the gate reports it empty. Candidates that still have the legacy `context.ideal_day` blob (never re-saved since the migration) pass, which is why only somerset fails. The real run path (`src/core/agent.py` token view) already uses the hydrated `src.core.candidate.get_candidate`, so actual runs resolve correctly. Only the admin-side validation is wrong.

The same raw-row read happens in two sibling sites in the same file: `_enrich_tasks` (Task Manager token counts) and the ad hoc run handler (around line 1580). The ad hoc one sends an empty `{$IDEAL_DAY}` (and any other migrated context token: strengths, priorities, deal breakers, bio summary, backstory, writing preferences, base resume) to the LLM for migrated candidates.

## To-be

The Scheduled Actions validation resolves artifact-typed tokens (`IDEAL_DAY` and every other `TOKEN_SOURCES` entry with `source_type: artifact`) from the operative current artifact row, with the legacy blob fallback, the same way the real run path does. Somerset's `craft_do_rubric` validates clean. A candidate with a truly empty Ideal Day still fails.

## Proposed steps

1. In `_evaluate_dispatch_empty_render`, load the candidate through the hydrated `src.core.candidate.get_candidate` (it applies all `hydrate_operative_*_for_response` overlays) instead of raw `database.get_candidate`, then build the token view as today.
2. Make the same swap in `_enrich_tasks` and the ad hoc run handler in `api_admin.py`, so every admin token resolve sees the same candidate view as runtime. (Same file, same defect class. Drop this step if you want the fix limited to the gate.)
3. Component test: a candidate with Ideal Day only in the artifacts table (no `context.ideal_day` blob) gets `empty_render: False` for a prompt containing `{$IDEAL_DAY}`. A candidate with neither is still `empty_render: True`.

## Component scope

* `src/ui/api/api_admin.py` (modified): the dispatch empty-render gate, Task Manager enrichment, and the ad hoc run all read the raw DB candidate row. They need to read the hydrated one.
* `tests/component/ui/api/test_api_admin.py` (modified; Betty's call on the exact file): repro for an artifact-only Ideal Day passing the gate.

## Technical scope

* `src/ui/api/api_admin.py`: modified functions `_evaluate_dispatch_empty_render`, `_enrich_tasks`, and the ad hoc run handler. Switch the candidate load from `database.get_candidate` to the hydrated `src.core.candidate.get_candidate` (import alongside the existing `build_candidate_token_view` import) so artifact-table values overlay `candidate_data` before token resolution. No new function, table, or field.
* Test file: new test function(s) covering artifact-only and truly empty Ideal Day through the gate.

## Ancestor candidates

- [ ] AST-1779: empty-token predicate helper (`docs/features/dispatcher/ast-1779-empty-token-predicate-helper.md`). This defined `empty_render_for_prompts`, which is the gate that's misreading.
- [ ] AST-1780: list enrich / AUTO-Run gates / force AUTO off (`docs/features/dispatcher/ast-1780-list-enrich-auto-run-gates-force-auto-off.md`). This added `_evaluate_dispatch_empty_render` with the raw candidate load.
- [ ] AST-1659 / AST-1660: Ideal Day operative save, blob retirement, and ContextTextPage wire-up (`docs/features/foundation/ast-1659-operative-save-hydrate-blob-retirement.md`, `docs/features/foundation/ast-1660-ideal-day-contexttextpage-wire-up.md`). These moved Ideal Day out of the blob, which exposed the gap.
- [ ] AST-1643: migrate `candidate_data.context.ideal_day` to the artifact table (parent migration, `docs/features/foundation/ast-1643-migrate-candidate-datacontextideal-day-to-use-the-artifact-table.md`).
- [ ] AST-1818: Scheduled Actions invalid label / zero-avail run block (`docs/features/interface/ast-1818-scheduled-actions-invalid-label-zero-avail-run-block.md`). This is the UI surface that shows the invalid flag.

---

## Original brief

craft_do_rubric for candidate somerset claims IDEAL DAY is missing for the candidate, but there is a value in the database for the candidate's ideal day.

Other candidates do not fail vaildation when their ideal day is populated.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
