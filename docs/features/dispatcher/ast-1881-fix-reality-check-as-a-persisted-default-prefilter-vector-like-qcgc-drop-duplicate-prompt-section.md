# AST-1881 — fix: Reality Check as a persisted default prefilter vector (like QC/GC); drop duplicate prompt section

<!-- linear-archive: AST-1881 archived 2026-10-07 -->

## Linear archive (AST-1881)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1881/fix-reality-check-as-a-persisted-default-prefilter-vector-like-qcgc  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / 3  
**Parent:** AST-1876 — [✅/Johnson] prefilter_company COMPLETED: 50 error(s) / 50 processed | prefilter_company-6e5f321d-aa8d-4a68-94eb-3efa041a59bd  
**Blocked by / blocks / related:** parent: AST-1876

### Description

## What this implements

Reality Check (`RC`) for `prefilter_company` is defined in exactly one place: a default rubric vector maintained the same way as the job-description default vectors `QC` / `GC`. It's a constant in `config.py`, merged into the candidate's `prefilter_company` rubric on save, craft persist, and craft generate, and stored in `rubric_vector`. Its content is the company-site grade scale. The duplicate hand-written Reality Check section in the `prefilter_company` prompt is removed, so the model grades RC once per line and batches stop failing on `duplicate vector code RC`.

## Scope

## Component scope

* `data/admin/agent_task.json` — modified: remove the duplicate Reality Check section from the `prefilter_company` `cache_prompt`.
* `src/utils/config.py` — modified: the `RC` entry in `EMBEDDED_COMPANY_PREFILTER_CRITERIA` gets the company-site grade scale.
* `src/core/candidate.py` — modified: RC is merged and saved on the same code paths as the job-description QC/GC vectors, not just added at read time.

## Technical scope

* `data/admin/agent_task.json`: data-only edit to the `prefilter_company` row's `cache_prompt` field. No schema change.
* `src/utils/config.py`: edit the existing `EMBEDDED_COMPANY_PREFILTER_CRITERIA` constant (`content` and `grade_descriptions` of the `RC` dict). No new constant.
* `src/core/candidate.py`: a new merge helper for the embedded prefilter criteria, parallel to `_merge_embedded_evaluate_jd_criteria`. Modify `rubric_criteria_for_task` to use it, and modify `normalize_rubric_artifacts_on_save`, the craft persist path, and the craft generate response to call it for `prefilter_company` / `company_prefilter` / `craft_prefilter_rubric`, so RC is saved to `rubric_vector` like QC/GC. No new table or field.

## Boundaries

Product code and prompt data only. Tests and the test bible belong to Betty (a gap sibling gets filed if fix-board asks for one). Do not weaken the AST-1513 duplicate-code decode guard in `_decode_payload` or `_require_complete_grade_set`. Do not change the QC/GC merge behavior. No new limits, caps, or retries.

## Notes for planning

Parent bug AST-1876's Description (As-is / To-be / Proposed steps) is authoritative. Susan approved it by reassigning, after asking in-thread for RC to be "maintained the same way" as the two job-description default vectors (persisted in the DB), with content "about company sites". Ancestor Susan checked: AST-707 / AST-708 (`docs/features/consult/ast-707-uat-batch-prefilter-embedded-rc-vector-hydration.md`, `docs/features/consult/ast-708-uat-batch-prefilter-fails-rc-embedded-vector-hydration.md`), both archived, so there's no related link. Pattern to mirror: AST-1085 / AST-1077 (`_merge_embedded_evaluate_jd_criteria`, `docs/features/interface/ast-1085-wire-constants-evaluate-jd.md`). Hot-file note: in-flight `ftr/AST-1862-recommended-job-modal-changes` also touches `src/utils/config.py`, in a different block.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1876-prefilter-rc-default-vector`, child `sub/AST-1876/AST-1881-prefilter-rc-default-vector`. Created at bug-fix.

### Comments

#### radia — 2026-09-29T20:01:04.536Z
[code-rubric] PROCEED (Commit: 2b1f6e1a) RC persist + prompt dedupe OK

#### hedy — 2026-09-29T19:58:15.718Z
`origin/sub/AST-1876/AST-1881-prefilter-rc-default-vector` @ `2b1f6e1a` · light check (no qa-fix manifest)

Ran `test_config.py`, `test_candidate.py`, and `-k "Ast707 or Rubric or prefilter"` over `test_consult.py` / `test_roster.py`, one tree at a time with an isolated `ASTRAL_DB_DIR`, against `origin/dev`. The only new failure is the expected one: `test_config.py::TestAst707EmbeddedPrefilterConfig::test_embedded_rc_registry`, which still expects the old "real vs fraudulent" RC text. AST-1882 updates it. All other failures (61) are identical on `origin/dev` and predate this change.

#### joan — 2026-09-29T19:54:40.026Z
[board-joan]  CANON: OK

#### betty — 2026-09-29T19:53:56.020Z
[board-betty] TESTS: REVISE
What: docs/test-bible/utils/config.md + core/candidate.md — broken test + missing coverage — `tests/component/utils/test_config.py::TestAst707EmbeddedPrefilterConfig::test_embedded_rc_registry` asserts the old "real vs fraudulent" RC prose and the A–F+E/X grade list, so the new company-site scale (A/B/C/D/F/X, no E) breaks it. No bible entry covers the repro (the `prefilter_company` `cache_prompt` in `data/admin/agent_task.json` must have no hand-written `Reality Check` block while keeping `{$RUBRIC_VECTORS}`) or the new RC merge on `apply_rubric_vectors_save` (owner `prefilter_company`), `_persist_craft_dispatch_success` (`company_prefilter`), and craft generate (`craft_prefilter_rubric`). The AST-1085 QC/GC tests in `test_candidate.py` (~3745–3833) are the pattern to follow.

Not affected (checked): `test_consult.py::TestRubricLookup::test_matches_criterion_by_code` (index 3 is still D), `test_roster.py::TestAst707EmbeddedRcBatchHydration` (only needs a non-empty reason), `test_candidate.py::TestAst723RubricVectorsCutover::test_prefilter_merges_embedded_rc_from_table` (RC still first).

— Betty

#### hedy — 2026-09-29T19:52:41.642Z
`origin/sub/AST-1876/AST-1881-prefilter-rc-default-vector` @ `944af3b8` · RC persisted like QC/GC

---

_Implementation detail may live in git history on `origin/dev`._
