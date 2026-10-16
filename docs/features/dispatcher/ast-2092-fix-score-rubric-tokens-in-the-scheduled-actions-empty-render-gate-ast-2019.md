# AST-2092 — fix: score rubric tokens in the Scheduled Actions empty-render gate (AST-2019)

<!-- linear-archive: AST-2092 archived 2026-10-16 -->

## Linear archive (AST-2092)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2092/fix-score-rubric-tokens-in-the-scheduled-actions-empty-render-gate-ast  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** ada  
**Priority / estimate:** None / 2  
**Parent:** AST-2019 — [✅/Abrams] qualify_job_listings COMPLETED: 10 error(s) / 10 processed | qualify_job_listings-9f9fcf12-c163-4e88-b88f-7037ae4bc21e  
**Blocked by / blocks / related:** parent: AST-2019; blocks: AST-2094

### Description

## What this implements

Fix for [AST-2019](https://linear.app/astralcareermatch/issue/AST-2019): the Scheduled Actions empty-render gate must score `source: rubric` tokens (`RUBRIC_VECTORS` and the pinned `GET_RUBRIC` / `DO_RUBRIC` / `LIKE_RUBRIC` / `JD_RUBRIC`) the same as candidate tokens, so a candidate with an empty rubric is flagged Invalid and blocked before any jobs are claimed.

## As-is

Abrams' `qualify_job_listings` dispatch claimed 10 `NEW` jobs, passed all 10 through the inline title gate (`VALID_TITLE`), then `agent.do_task` refused to send the prompt because `{$RUBRIC_VECTORS}` resolved empty (`Empty tokens: RUBRIC_VECTORS`). All 10 jobs were routed to `ERROR_QUALIFY_JOB_LISTINGS` (batch `qualify_job_listings-9f9fcf12-c163-4e88-b88f-7037ae4bc21e`: 0 pass / 0 fail / 10 error).

Two things are wrong here:

1. **Data:** Abrams has no current `joblist_rubric` rows in `rubric_vector` (owner `qualify_job_listings`), so the token has nothing to render. (Inferred from the resolver path: the owner mapping exists and the admin token view carries `_astral_candidate_id`, so the remaining way to get `""` is "no current rows". I haven't checked this against the DB.)
2. **Gate:** Scheduled Actions should have flagged this row Invalid and blocked AUTO/Run *before* anything was claimed. It didn't, because `empty_render_for_prompts` (`src/utils/config.py`) only scores `source: candidate` tokens by default. `RUBRIC_VECTORS` (and the pinned `GET_RUBRIC` / `DO_RUBRIC` / `LIKE_RUBRIC` / `JD_RUBRIC`) are `source: rubric`, so they are skipped unless passed through `entity_contexts`. `_evaluate_dispatch_empty_render` always passes `entity_contexts=None`. This exclusion was deliberate in AST-1779 ("Do not score `pronoun`, `rubric`, `config`…"), but rubric rows are keyed per candidate (`candidate_id` + owner task), so they belong with the candidate-scoped tokens, not with the job tokens.

## To-be

A candidate whose rubric for a task is empty shows that dispatch row as **Invalid** in Scheduled Actions, with the rubric token named in the tooltip (`empty_tokens`). AUTO is forced off and Run/AUTO-on are refused (400), the same as a blank candidate token today. No jobs get claimed and dumped into `ERROR_*`. Separately, once Abrams' joblist rubric is crafted, the row validates and `qualify_job_listings` runs normally.

## Proposed steps

1. In `empty_render_for_prompts`, score `source: rubric` tokens by default, the same as `source: candidate`. They resolve from the candidate view's `_astral_candidate_id` and the task's rubric owner (or the token's pinned owner), with no entity context needed. Keep `chain` never scored and `job` scored only via the `entity_contexts` seam.
2. No change needed in `api_admin.py`: list enrich, the PUT AUTO-on gate and the POST run gate all route through `_evaluate_dispatch_empty_render` → `empty_render_for_prompts`, so they pick this up automatically.
3. Betty revises the pinned AST-1779 test `test_rubric_scored_only_via_entity_contexts`, since its contract flips, and adds a repro: a candidate with no current `rubric_vector` rows for `qualify_job_listings` gives `empty_render: True`, `empty_tokens: ["RUBRIC_VECTORS"]`.
4. Operator side, not code: craft or approve Abrams' joblist rubric (`craft_joblist_rubric`), then reset the 10 `ERROR_QUALIFY_JOB_LISTINGS` jobs back to `NEW` so they rerun.

## Citations

none — `plan-fix` resolves Canon Scope from the touched files (`src/utils/config.py` token registry / resolver).

## Scope

### Component scope

* `src/utils/config.py` — modified: `empty_render_for_prompts` is where rubric-sourced tokens are skipped by default. This is the whole product fix.
* `tests/component/utils/test_config.py` — modified (Betty-owned): the AST-1779 rubric-seam test asserts the old behaviour and must flip. Needs a new rubric-empty repro.

### Technical scope

* `src/utils/config.py` — modified function `empty_render_for_prompts`: widen the default scoring rule from "candidate only" to "candidate and rubric". Rubric tokens are candidate-scoped data (one `rubric_vector` set per candidate per owner task), and the existing `resolve_tokens` rubric branch already resolves them from the candidate view. No new resolver, no new `TOKEN_SOURCES` entries, no schema change.
* `tests/component/utils/test_config.py` — modified test plus one new test in `TestAst1779EmptyRenderForPrompts`. The pinned seam-only contract becomes default scoring, and the empty-rubric case is pinned as a repro.

## Acceptance criteria

1. For a candidate with no current `rubric_vector` rows for a task's rubric owner, `empty_render_for_prompts` over prompts containing `{$RUBRIC_VECTORS}` returns `empty_render: True` with `RUBRIC_VECTORS` in `empty_tokens`.
2. Scheduled Actions therefore shows that dispatch row Invalid (tooltip names the token), forces AUTO off, and refuses AUTO-on / Run — no jobs claimed.
3. A candidate with current rubric rows for that owner still validates (`empty_render: False`).
4. `source: chain` is still never scored; `source: job` is still scored only via `entity_contexts`.

## Boundaries

No change to `do_task`'s runtime empty-token refusal or the `ERROR_*` routing. No new resolver, `TOKEN_SOURCES` entry, or schema. Crafting Abrams' joblist rubric and resetting the 10 `ERROR_QUALIFY_JOB_LISTINGS` jobs is an operator step, not code.

## Notes for planning

No ancestor candidate was checked on AST-2019. The function being changed was introduced by AST-1779 (archived), whose plan explicitly said "Do not score `pronoun`, `rubric`, `config`…" — this fix reverses that one rule for `rubric` only.

## Git branch (authoritative)

Mini-parent `ftr/AST-2019-rubric-empty-render-gate`, child `sub/AST-2019/AST-2092-rubric-empty-render-gate`. Created at bug-fix.

### Comments

#### radia — 2026-10-09T02:24:36.535Z
[code-rubric] PROCEED (Commit: 5ff29d79) Rubric gate scoring fix

#### joan — 2026-10-09T02:21:07.075Z
[board-joan]  CANON: OK

#### betty — 2026-10-09T02:20:43.057Z
[board-betty] TESTS: REVISE
What: docs/test-bible/utils/config.md (TestAst1779EmptyRenderForPrompts) — broken test + missing repro — `test_rubric_scored_only_via_entity_contexts` default-call assertion (False) flips to True/["GET_RUBRIC"]; no existing test covers rubric-empty with `_astral_candidate_id` + stubbed `rubric_criteria_for_token` → `[]` (needs [bug-repro] for RUBRIC_VECTORS on qualify_job_listings + one-criterion AC 3 control). test_api_admin.py empty-render cases all stub prompt texts (no rubric tokens) — unaffected.

#### ada — 2026-10-09T02:19:49.680Z
`origin/sub/AST-2019/AST-2092-rubric-empty-render-gate` @ `a016336b` · rubric scored by default

---

_Implementation detail may live in git history on `origin/dev`._
