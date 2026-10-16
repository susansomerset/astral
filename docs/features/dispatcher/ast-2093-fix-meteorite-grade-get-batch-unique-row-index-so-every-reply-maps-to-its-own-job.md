# AST-2093 — fix: meteorite_grade_get — batch-unique row index so every reply maps to its own job

<!-- linear-archive: AST-2093 archived 2026-10-16 -->

## Linear archive (AST-2093)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2093/fix-meteorite-grade-get-batch-unique-row-index-so-every-reply-maps-to  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / 3  
**Parent:** AST-2012 — [✅/Somerset] meteorite_grade_get COMPLETED: 23 error(s) / 52 processed | meteorite_grade_get-a4ec9af6-55e0-4bb6-92a9-2c4754009971  
**Blocked by / blocks / related:** parent: AST-2012; blocks: AST-2095; related: AST-2015

### Description

## What this implements

Batch-unique per-entity row indexes for the encoded grade path (`meteorite_grade_get` and the other Do/Get/Like grade tasks routed through `_consult_scored_dispatch_batch_encoded`). Each claimed entity gets its own index across the whole claimed batch, not chunk-local `000…` restarting per chunk or call. That index is the single row label in the assembled content. `_decode_payload` maps each reply line back through an explicit index → entity map instead of list position, so parallel/async chunk replies always land on the right entity. A duplicate or unknown index becomes a per-entity decode failure instead of every line collapsing onto `batch_entities[0]`. Also fixes the batch-complete "N processed" double count across retry runs.

## Scope

## Component scope

`src/core/consult.py`: modified. `_prep_live_content` and the `assemble` inside `_consult_scored_dispatch_batch_encoded` build the chunk-local `000…` labels, and `_run_batch_consult` builds the decode context (`batch_entities`) that maps replies back to entities.
`src/core/agent.py`: modified. `_decode_payload` maps reply lines by list position (`batch_entities[pos]`) with no uniqueness check, which is what collapses every `000` line onto one entity.
`src/core/dispatcher.py`: modified. It splits claims into parallel chunks (each restarting its numbering) and builds the Somerset `COMPLETED: N error(s) / M processed` summary that overcounts.
`data/admin/agent_task.json`: modified. The `grade_do` / `grade_get` prompts tell the model to use a zero-based row index like `000:`, which invites the same label on every line.

## Technical scope

`src/core/consult.py`: modified functions `_prep_live_content` and the encoded-dispatch `assemble`, to stamp the entity's batch-unique index once per row. Modified function `_run_batch_consult`, to put an index → entity map into the `do_task` context so the reply can be mapped back by identity rather than position.
`src/core/agent.py`: modified function `_decode_payload`, to resolve each line's index through the index → entity map (falling back to position only where no map is supplied, so other tasks keep working). Duplicate or unknown indexes are recorded as per-entity `decode_failures`.
`src/core/dispatcher.py`: modified chunking path, so each chunk keeps its batch-global indexes. Modified batch-complete summary, so each entity is counted once across retry runs.
`data/admin/agent_task.json`: modified prompt text fields on `grade_do` / `grade_get`, to tell the model to echo each row's own index.

## Acceptance criteria

- [X] A batch where the model labels every line `000` no longer grades only the first entity and marks the rest "omitted". Every line is resolved by its index, and collisions route only the affected entities to retry.
- [X] Parallel chunks of one claimed batch never share an index.
- [X] Each assembled row carries exactly one index label (no `NNN: [index=NNN]:` double label).
- [X] Tasks that don't supply an index map keep today's positional decode.
- [X] The batch-complete summary counts each entity once.

## Boundaries

Does not change rubric/grade semantics, pass/fail rendering, or retry-holding routing (AST-642 / AST-1839). The only change is which entity a reply line maps to. Does not touch `qualify_meteorite`'s link/order binds. Does not reset jobs already stranded in `METEORITE_FAILED_TECHNICAL_GET` by the reported run. Tests and bible belong to Betty (fix-board decides whether a gap child is needed).

## Notes for planning

AST-2012 Description (As-is / To-be / Proposed steps) is authoritative, including Susan's direction at the top: send a real, unique index for each entity on every call so async replies map back affirmatively. No ancestor box was checked. Patch `docs/features/agent/response-validation-layers.md` (the canonical Pattern A decode/bind doc) with a `## Bug: <this id>` block. Hot-file overlap: [AST-2015](https://linear.app/astralcareermatch/issue/AST-2015) / AST-2089 (in flight, also Hedy) changes `do_task` envelope salvage and `_run_batch_consult` in the same files. Keep this diff local to index assembly and decode so the refresh-ftr merge stays small.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-2012-grade-batch-unique-index`, child `sub/AST-2012/AST-2093-grade-batch-unique-index`. Created at bug-fix.

### Comments

#### radia — 2026-10-09T02:42:03.744Z
[code-rubric] PROCEED (Commit: 2856ad263) Batch-unique grade indexes clean

#### betty — 2026-10-09T02:38:49.949Z
[check-linear] Code Complete — [qa-handoff] cleared (@Hedy Lamarr, test-fix)
Tests updated for [qa-handoff]: the 5 `tests/component/core/test_dispatcher.py` nodes now follow the approved plan, no product change.
- `test_ast505_candidate_entity_claims_without_company_clear`: expects `repeat_processed: 0` on the return, and `batch_index_offset=0` on the `run_consult_task` await. That second assert was hidden behind the first failure.
- `test_ast502_chunked_evaluate_await_chunk0_sleep_once_then_gather_tails`: the `run_capture` stub accepts `batch_index_offset`.
- `test_run_unified_per_entity_skips_after_refusal` / `test_run_unified_per_entity_skips_after_rate_limit`: expected dicts include `repeat_processed: 0`.
- `test_run_unified_candidate_claim_gate`: expects `{**_SUMMARY_ZERO, "repeat_processed": 0}`.
Manifest delta: none. New coverage for the fix stays with AST-2095.
Publish: carry `6a2bc960f` (on ftr base `823d376`) → `origin/sub/AST-2012/AST-2093-grade-batch-unique-index` @ `2856ad263` (`merge-tests(AST-2093)`); `origin/tests` @ `3b7bb8984`.
Verify: `/home/susan/astral/.venv/bin/python -m pytest tests/component/core/test_dispatcher.py -q -rf` → 12 failed / 170 passed at the tip. The 12 match the base `823d376` reds exactly, and all 5 handoff nodes pass.

#### hedy — 2026-10-09T02:36:14.733Z
[qa-handoff]
@Betty White: test-fix lighter check on `origin/sub/AST-2012/AST-2093-grade-batch-unique-index` @ `01d49f2`. I ran `test_agent.py`, `test_consult.py` and `test_dispatcher.py` (`tests/component/core/`) at base `origin/ftr/AST-2012-grade-batch-unique-index` (`823d376`) and at the tip.

Base had 80 failed / 836 passed. Tip had 85 failed / 831 passed. All 80 base failures are identical at the tip. There are 5 new reds, all in `test_dispatcher.py` and all test-side under the approved plan (`response-validation-layers.md` § Bug: AST-2093, Proposed change steps 1–5):

1. Exact-dict equality on `_run_unified`'s return. The plan adds `s["repeat_processed"]` to that return as a non-`_SUMMARY_ZERO` key, and `_run_dispatch_loop` subtracts it so retry runs aren't double-counted. These tests need to compare only the `_SUMMARY_ZERO` keys, or expect `repeat_processed` (`0` here):
   - `TestRunUnified::test_ast505_candidate_entity_claims_without_company_clear` (line 433)
   - `TestAst1867ProviderBalanceOutage::test_run_unified_per_entity_skips_after_refusal` (line 1791)
   - `TestAst2010ProviderRateLimitOutage::test_run_unified_per_entity_skips_after_rate_limit` (line 1947)
   - `TestAst972CandidateStageDispatch::test_run_unified_candidate_claim_gate` (`out == _SUMMARY_ZERO`)
2. A stub signature mismatch. The chunk path now passes `batch_index_offset=ci * chunk_sz` to `consult.run_consult_task` (plan step 1). The local `run_capture` stub needs to accept it (`**kwargs`, or the new kwarg):
   - `TestRunUnified::test_ast502_chunked_evaluate_await_chunk0_sleep_once_then_gather_tails`: `TypeError: run_capture() got an unexpected keyword argument 'batch_index_offset'`

Command:

`/home/susan/astral/.venv/bin/python -m pytest tests/component/core/test_agent.py tests/component/core/test_consult.py tests/component/core/test_dispatcher.py -q -rf`

These likely fold into the AST-2095 test gap.

There is a product-side alternative for group 1, but it deviates from the plan text. `_run_unified` could hand the repeat count back through `ctx` (the same in-place channel as `dispatch_partial`) instead of the summary dict. That would keep the return shape exact. Group 2 would still need the stub fix. If Chuckles/Susan prefer that route, say so and I'll amend the plan.

Status stays Code Complete. Reassign to me when the tests are updated.

#### joan — 2026-10-09T02:28:14.320Z
[board-joan]  CANON: OK

#### betty — 2026-10-09T02:27:52.566Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/agent.md + core/consult.md + core/dispatcher.md — missing coverage — no test exercises batch_index_map / batch_index_offset / dispatch_seen_ids (rg finds zero hits), so the Repro (chunk-1 `000` echo collapses onto entity 0) is uncaptured; need [bug-repro] tests for _decode_payload map path (unknown index skipped, duplicate index → one decode_failures row, correct 020–039 maps), _consult_scored_dispatch_batch_encoded assemble (`[index=020]: …`, no `000: ` double prefix), render_verdict batch_index, _run_unified chunk/per-entity offsets, and _run_dispatch_loop repeat_processed dedupe. All three modules are LOCKED_AT_100, so every new branch needs a node. Existing nodes reviewed (test_consult `[index=000]: jd text` default-position, dispatcher mocked _run_task summaries) stay valid as written.

#### hedy — 2026-10-09T02:26:42.627Z
`origin/sub/AST-2012/AST-2093-grade-batch-unique-index` @ `f9523f6d8` · global index, map-based decode

---

_Implementation detail may live in git history on `origin/dev`._
