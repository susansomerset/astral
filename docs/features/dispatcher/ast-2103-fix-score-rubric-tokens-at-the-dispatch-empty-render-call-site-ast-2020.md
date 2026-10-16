# AST-2103 — fix: score rubric tokens at the dispatch empty-render call site (AST-2020)

<!-- linear-archive: AST-2103 archived 2026-10-16 -->

## Linear archive (AST-2103)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2103/fix-score-rubric-tokens-at-the-dispatch-empty-render-call-site-ast  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** ada  
**Priority / estimate:** None / 2  
**Parent:** AST-2020 — [✅/Abrams] qualify_job_listings COMPLETED: 2 error(s) / 2 processed | qualify_job_listings-3e0aa3ec-a853-42fa-ad37-63aea7c24a02  
**Blocked by / blocks / related:** parent: AST-2020; related: AST-2019

### Description

## What this implements

Fix for [AST-2020](https://linear.app/astralcareermatch/issue/AST-2020): dispatch validation must treat an empty `source: rubric` token (`RUBRIC_VECTORS` and the AST-1405 named pins) as non-executable. Then the row is flagged Invalid, AUTO is forced off, and Run/AUTO-on are refused before any jobs are claimed.

## Overlap — read before planning

[AST-2019](https://linear.app/astralcareermatch/issue/AST-2019) is the same production symptom. Its fix [AST-2092](https://linear.app/astralcareermatch/issue/AST-2092) (User Testing, on `origin/ftr/AST-2019-rubric-empty-render-gate`, commit `5ff29d792`) changes `empty_render_for_prompts` in `src/utils/config.py` to score `source: rubric` by default. That change is **not on** `origin/dev` **yet**. Susan approved this ticket going ahead anyway. Plan the call-site change so it is correct both with and without AST-2092 landed, and so the two compose with no conflict or double-scoring. Flag in the plan if the call-site change becomes a no-op once AST-2092 ships.

## As-is

The pre-dispatch empty-render validation (`_evaluate_dispatch_empty_render` in `src/ui/api/api_admin.py`) calls AST-1779's `empty_render_for_prompts` with `entity_contexts=None`. That helper scores only `source: candidate` tokens. `{$RUBRIC_VECTORS}` (and the AST-1405 named rubric pins) are `source: rubric`, meaning per-candidate `rubric_vector` rows for the task's rubric owner. For `qualify_job_listings` the owner is `qualify_job_listings` / artifact `joblist_rubric`. So a candidate with no current joblist rubric still validates `empty_render: false`, AUTO stays on, and Run is allowed. The dispatch then claims jobs, `agent.do_task` refuses the call ("Empty tokens: RUBRIC_VECTORS"), and every claimed job is routed to `ERROR_QUALIFY_JOB_LISTINGS`. In this report that was abrams: 2 jobs claimed, 2 errored.

## To-be

Dispatch validation treats an empty rubric token as non-executable. When `{$RUBRIC_VECTORS}` or any `source: rubric` token in the task's prompts resolves empty for the row's candidate, the row validates `empty_render: true` with that token in `empty_tokens`. Then AST-1780's list enrichment forces AUTO off, the Invalid tooltip names the token (AST-1819), and Run/AUTO-on return the existing 400 "Prompt tokens resolve empty for this candidate". No jobs are claimed or errored because a rubric was never crafted.

## Proposed steps

1. In `_evaluate_dispatch_empty_render`, pass an `entity_contexts` entry keyed `rubric` to `empty_render_for_prompts`. That's AST-1779's documented extension seam, and its manifest test 7 (`test_rubric_scored_only_via_entity_contexts`) already proves rubric tokens score through it. The candidate token view already carries `_astral_candidate_id`, so the `rubric` resolver branch reads the candidate's `rubric_vector` rows exactly as the runtime does.
2. Leave `empty_render_for_prompts`' default (candidate-only, chain ignored, job only via the seam) unchanged so AST-1779's contract and tests still hold.
3. Every existing gate caller picks this up with no further changes, because they all go through `_evaluate_dispatch_empty_render` / `_candidate_dispatch_empty_render_error`: list enrichment with AUTO force-off, save, AUTO-on, and `POST …/run`.

## Citations

none — `plan-fix` resolves Canon Scope from the touched files.

## Scope

### Component scope

`src/ui/api/api_admin.py` — modified. `_evaluate_dispatch_empty_render` is the single dispatch-validation gate behind list enrichment (AUTO force-off), save, AUTO-on, and Run. Today it passes `entity_contexts=None`, which hides rubric emptiness.

### Technical scope

`src/ui/api/api_admin.py` — modified function `_evaluate_dispatch_empty_render`: supply the `rubric` entity-context key to `empty_render_for_prompts` so empty `source: rubric` tokens flip `empty_render` true for that candidate and task. No new functions, tables, or fields.

## Git branch (authoritative)

Bug mini-parent `ftr/AST-2020-rubric-gate-call-site`, child `sub/AST-2020/<this-ticket>-rubric-gate-call-site`. Registry: `epic_registry.py show AST-2020`.

### Comments

#### radia — 2026-10-09T03:02:36.487Z
[code-rubric] PROCEED (Commit: ad073ede) Call-site rubric seam explicit

#### joan — 2026-10-09T02:59:40.721Z
[board-joan]  CANON: OK

#### betty — 2026-10-09T02:59:20.539Z
[board-betty] TESTS: OK

Repro is already covered at the helper: `tests/component/utils/test_config.py` AST-2092 `[bug-repro]` (`test_empty_rubric_vectors_sets_empty_render` + filled control) uses the same abrams/`qualify_job_listings` shape, and the existing `entity_contexts={"rubric": {}}` helper case pins the exact kwarg this fix passes. The call-site edit is a no-op on this tip, so no new `[bug-repro]` could go red.

Blast radius is clean against existing tests: nothing in `tests/` asserts `entity_contexts=None` at `_evaluate_dispatch_empty_render`. AST-1780/1792/1795 classes monkeypatch the evaluator or stub prompt texts with candidate-only tokens. AST-1854's real-loader evaluator tests carry no rubric tokens, so they're unaffected. `database/test_dispatch_tasks.py:1917` is the AST-1781 revalidation path, which this fix doesn't touch. The `api_admin.py` `LOCKED_AT_100` lock is unaffected because the edit is one line with no new branch.

#### ada — 2026-10-09T02:58:16.631Z
`origin/sub/AST-2020/AST-2103-rubric-gate-call-site` @ `fd31c854b` · No-op: AST-2092 already on dev

---

_Implementation detail may live in git history on `origin/dev`._
