<!-- linear-archive: AST-1259 archived 2026-08-17 -->

## Linear archive (AST-1259)

**Archived:** 2026-08-17  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1259/dispatcher-and-core-candidate-pool-claim-parity-candidate-table-does  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1257 — candidate table does not have batch_id  
**Blocked by / blocks / related:** parent: AST-1257; blocks: AST-1260

### Description

## What this implements

Add core `get_new_candidate_batch` / clear wrappers and replace the unlocked single-ctx candidate branch in unified dispatch with claim → process → release using the same batch_size / claim-state pool mechanics as job/company (finally clears; debug contract on touched path). After AST-1258. Does not own statute text.

## In scope

- [X] `pattern.batch.entity-claim-process-release` — core wrappers + dispatcher claim → process → release for `entity_type=candidate`
- [X] `astral.batch.claim-process-release` — no unlocked single-ctx candidate carve-out in `_run_unified`
- [X] `astral.batch.batch-id-first` — `get_new_candidate_batch` / data claim order
- [X] `astral.batch.batch-id-format` — reuse dispatcher-minted `f"{task_key}-{uuid}"` golden ticket
- [X] `astral.standards.debug-contract-gated` — Style D on touched candidate claim/dispatch path when `debug=True`
- [X] `astral.layers.import-direction` — late core→core import in `_run_unified`; wrappers call data only
- [X] `astral.state.core-decides-transitions` — claim/clear lock columns only; state transitions stay in existing runners
- [X] `astral.standards.dry-and-focused-functions` — Batch API grouping in `candidate.py` (Radia C4; was excluded as “universal”)
- [X] `astral.standards.public-then-helpers` — claim wrappers public, grouped under Batch API (Radia C4; was excluded as “universal”)

## Considered but excluded

- [X] `astral.standards.database-header-inventory` — candidate schema/inventory owned by AST-1258 (`src/data/database.py`)
- [X] `orch.roles.archie-approves-statutes` — statute/pattern/`CANDIDATE_DATA_MODEL` amend/retire is AST-1260
- [X] `pattern.state.entity-state-transitions` — no state-machine redesign; craft/inflow runners unchanged
- [X] gaze_email mailbox path — non-`ENTITY_TYPES` claim exception (parent boundary)
- [X] `consult.run_consult_task` multi-entity candidate rewrite — force per-entity process in dispatcher instead

## Acceptance criteria

- [X] 3. Dispatcher `entity_type=candidate` scheduled runs claim via those helpers (respecting `batch_size` / claim states) and clear the lock in `finally` (including empty-batch / early-exit paths that today clear job but `pass` for candidate).
- [X] 4. With `debug=True` on the touched candidate claim/dispatch path, logs show per-step found/recorded detail with Style D index headers and Style D detail-prefix working lines (backend only).

## Boundaries

Does not own schema/data claim APIs (AST-1258). Does not own statute/pattern/docs text (sibling). Does not redefine CANDIDATE_STATES or craft/`run_next` graphs except as required for shared batch APIs.

## Notes for planning

After #1 (AST-1258). Full job/company pool claim parity in dispatcher.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at dispatch-parent.

**Publish ref:** `sub/AST-1257/AST-1259-dispatcher-and-core-candidate-pool-claim-parity`

### Comments

#### betty — 2026-08-07T19:16:03.311Z
[check-linear]
Moved `@pytest.mark.skipif(retire_candidate_requested_wrapper_dispatch_tasks)` back onto `TestAst972CandidateStageDispatch`; `TestAst1259CandidatePoolClaim` unguarded.

`origin/sub/AST-1257/AST-1259-dispatcher-and-core-candidate-pool-claim-parity` @ `a4f94240` (`test(AST-1259): restore skipif…` from `origin/tests` `b3af62dd`). Assignee → Ada for resolve-child.

— Betty

#### ada — 2026-08-07T19:14:10.250Z
[qa-handoff]
@Betty White

Radia **fix-now** (test-tree): misplaced `@pytest.mark.skipif` in `tests/component/core/test_dispatcher.py`.

**What:** The decorator that guards `retire_candidate_requested_wrapper_dispatch_tasks` now sits above `class TestAst1259CandidatePoolClaim` (inserted between the decorator and `class TestAst972CandidateStageDispatch`). Move the decorator back immediately above `TestAst972CandidateStageDispatch`; leave `TestAst1259CandidatePoolClaim` unguarded.

**Why test/manifest:** Product claim path is fine; only Betty’s `test(AST-1259)` layout broke the skip attachment. Benign today (`hasattr` True) but wrong when that symbol retires.

**Tip:** `origin/sub/AST-1257/AST-1259-dispatcher-and-core-candidate-pool-claim-parity` — resolve doc @ upcoming push; product still `e0d18dab` / merge-tests `d950de10`. Stay Review Posted.

#### radia — 2026-08-07T19:11:32.341Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1259
**Publish ref:** `sub/AST-1257/AST-1259-dispatcher-and-core-candidate-pool-claim-parity` @ `d950de10`
**Overall:** DISCUSS

Full active-set sweep run in-session (65 active statutes: 18 universal + 47 scoped — 39 scoped matched the diff and scored, 8 scoped `not-applicable` with layer/path reasons). Note: this branch has not merged onto `dev` yet, so the three-dot diff also carries AST-1258's already-`Review Posted` data-layer content (`src/data/database.py`, its tests/bible) — that surface is not re-litigated here; this review's substantive findings are scoped to what's new in AST-1259: `src/core/candidate.py`, `src/core/dispatcher.py`, and their tests/bible.

## Plan adherence

- Stage 1 (`35265641`) and Stage 2 (`e0d18dab`) land exactly as planned: `get_new_candidate_batch` / `clear_candidate_batch` in `candidate.py` mirror `get_new_job_batch` / `get_new_company_batch` (state-first signature, `CANDIDATE_STATES` validation per entry, `context`-or-`batch_id` guard); `_run_unified`'s candidate arm replaces the unlocked `entities = [ctx] if … else []` gate with the pool claim, adds the empty-batch `clear_candidate_batch(bid)` early exit, and swaps the `finally` `pass` for a real clear — all at the exact insertion sites Joan verified against the tip.
- `use_full_batch = False` is forced for `entity_type == "candidate"` before the branch dispatch, which is required (confirmed `run_consult_task`'s candidate/inflow arms read `entities[0]` only) and correctly scoped — job/company `use_full_batch` behavior is untouched.
- Joan's round-1 fix-now (undisclosed test invalidation) and both discuss items (AC4 release-logging parity, cross-candidate inflow `ctx` cadence) are closed in Revision 1 and verified again in her Plan Approved pass.
- Scope held: only `src/core/candidate.py` and `src/core/dispatcher.py` touched by the two `code()` commits; `test()`/`merge-tests()` commits touch only `tests/` + `docs/test-bible/`; `docs()` commits touch only the plan file — clean role separation across all five AST-1259 commits.

## Pattern conformance

`pattern.batch.entity-claim-process-release` — conforms. This ticket closes the gap AST-1258 opened: the candidate branch of `_run_unified` now does a real claim → process → release cycle instead of the unlocked single-ctx `[ctx]` arm, matching the job/company shape end to end.

## Findings

**discuss — misplaced `@pytest.mark.skipif` decorator in `test_dispatcher.py` (Betty tree, not engineer scope).** The `test(AST-1259)` commit inserts the new `class TestAst1259CandidatePoolClaim` directly between the pre-existing `@pytest.mark.skipif(not hasattr(dispatcher_mod, "retire_candidate_requested_wrapper_dispatch_tasks"), …)` decorator and its intended target, `class TestAst972CandidateStageDispatch`. On this tip the attribute exists, so the skip condition is `False` either way and nothing currently fails — but the decorator now silently guards the wrong class, and `TestAst972CandidateStageDispatch` (whose own tests call `retire_candidate_requested_wrapper_dispatch_tasks`) runs unconditionally. Confirmed by diffing `origin/dev`'s file at the same lines: the decorator sat directly above `TestAst972CandidateStageDispatch` before this insertion. Not a block — tests pass today — but worth a bible/test-tree fix so the guard tracks its original target (`orch.roles.betty-owns-test-tree` territory, not engineer fix-now).

**discuss — straggler: `astral.standards.dry-and-focused-functions` and `astral.standards.public-then-helpers` excluded at plan time but in-scope on this sweep.** The plan's "Considered but excluded" list drops both with the reasoning "universal; no new statute work beyond existing Batch API grouping." Both are actually `tier: scoped` (not universal), and their `applies_when` (`layers` includes `core`, `paths` includes `src/core/**`) mechanically matches this diff's new `src/core/candidate.py` / `src/core/dispatcher.py` content, so this sweep scores both `conforms`, not `not-applicable`. Content-wise the exclusion reasoning holds up on inspection — the new `get_new_candidate_batch` / `clear_candidate_batch` pair is grouped under one `# ---- Batch API ----` section, no duplicated claim SQL, no oversized function — so no code change needed. Flagging per C4 so the plan-exclusion tier/label and the mechanical sweep predicate stay reconciled.

## Frame diff

(none)

## What's solid

- Claimed-row shape flows cleanly through every downstream reader: `_dispatch_entity_identifier` and `consult.run_consult_task`'s `entities[0].get("astral_candidate_id")` both work unchanged against real DB rows instead of the old raw `ctx`.
- The existing Style D post-claim debug block (found/recorded per index, batch-end summary) is entity-agnostic and now fires correctly for candidate with zero new debug code — exactly the AC4 answer Stage 3 commits to (release stays silent, parity with job/company clear).
- `limit_val = limit if limit is not None else 10` in the new wrapper is character-for-character the existing `get_new_job_batch` fallback — landed-code parity, not a new magic number.
- Test/bible delta precisely revises the two tests Stage 2 invalidates (`test_ast505_candidate_entity_routes_ctx_without_company_clear` → `…_claims_without_company_clear`; `test_run_unified_candidate_claim_gate`) and adds direct multi-row / empty-batch / finally-clear coverage matching the plan's Betty-contract list item-for-item.

context_tokens≈158000

— Radia

#### betty — 2026-08-07T19:04:20.423Z
## QA test manifest

`origin/sub/AST-1257/AST-1259-dispatcher-and-core-candidate-pool-claim-parity` @ `d950de10` (`merge-tests(AST-1259): origin/tests 79aa4374`)

1. `tests/component/core/test_candidate.py::TestAst1259CandidateBatchApi` — `get_new_candidate_batch` / `clear_candidate_batch` wrappers (batch_id/context, state validation, claim kwargs, clear delegate).
2. `tests/component/core/test_dispatcher.py::TestRunUnified::test_ast505_candidate_entity_claims_without_company_clear` — revised: pool claim → per-entity consult; `clear_candidate_batch` in finally; no job/company clear.
3. `tests/component/core/test_dispatcher.py::TestAst972CandidateStageDispatch::test_run_unified_candidate_claim_gate` — revised: empty claim → no consult + clear; claimed row → consult with claimed entity.
4. `tests/component/core/test_dispatcher.py::TestAst1259CandidatePoolClaim` — `batch_size` + `dispatch_claim_states`; multi-row → one consult per row; empty clears; finally clear skips job/company.

**Broken / obsolete (this pass):** unlocked-`[ctx]` asserts in `test_ast505_candidate_entity_routes_ctx_without_company_clear` and ctx-state-only claim gate.

**Integration:** none revised.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst1259CandidateBatchApi \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_ast505_candidate_entity_claims_without_company_clear \
  tests/component/core/test_dispatcher.py::TestAst972CandidateStageDispatch::test_run_unified_candidate_claim_gate \
  tests/component/core/test_dispatcher.py::TestAst1259CandidatePoolClaim \
  -q
```

**Bible (on publish-ref):**
- `docs/test-bible/core/dispatcher.md` `4ce9495753b61a9a3674fe877612370ffa35cb3382f4a784faba7cc87471745f`
- `docs/test-bible/core/candidate.md` `f521b5805e75c360e45f6bf3ed5a34fa99fb6922c77199324ba56ed2ea1c4d5f`

— Betty

#### joan — 2026-08-07T18:59:36.293Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1259
**Overall:** APPROVED
**Publish ref tip:** `sub/AST-1257/AST-1259-dispatcher-and-core-candidate-pool-claim-parity` @ `c8aff1a8` (Revision 1; round=1 concern was scored @ `ded4e05e`)

## Traceability

AC3→S2; AC4→S3; S1 (core wrappers) → parent Functional scope 2 ("Data **and core** expose claim → get → clear helpers"). No orphan stages; no unmapped AC. R5 pass.

**Considered:** 52 active statutes scored in-session (18 universal + 34 scoped considered, 13 scoped excluded). No `violates`, no `needs-discussion`.

## Round=1 items — all closed

**fix-now (Tests invalidated) → resolved.** The new **Tests invalidated (Betty contract)** section names both node ids with today's vs after-Stage-2 expectations plus the five coverage items Betty owns. I re-checked that those two are the *complete* set: `TestDispatchOne::test_skips_without_candidate_context` exercises `_dispatch_one`, not the claim arm, and no other test in the tree asserts the `entities = [ctx] if …` gate. `orch.pipeline.plan-is-bible` / `orch.roles.betty-owns-test-tree` → conforms.

**discuss (AC4 release logging) → decided.** Stage 3 Done-when plus step 2 now state release stays silent at job/company parity, so AC4 rests on the shared claim-side Style D block rather than new clear-side lines. That is the answer I offered and it is defensible — Radia will not read AC4 as unmet. `astral.standards.debug-contract-gated` → conforms.

**discuss (cross-candidate inflow ctx) → decided.** The Stage 2 inflow Decision now records the accepted cadence mismatch (A's `inflow_discovery_freq_hrs` against B's search terms) and explicitly declines a row-scoped inflow claim this ticket. Decided in the plan rather than discovered at review, which is what I asked for.

## Verified against the tip this round (no change needed)

- **Claimed-row shape matches every downstream reader.** `get_candidate_batch` returns `SELECT *` rows keyed on `astral_candidate_id`; `_dispatch_entity_identifier` reads `astral_candidate_id` first (line 61) and `consult.run_consult_task` builds `cid` from `entities[0].get("astral_candidate_id")` (line 2474). Swapping `[ctx]` for claimed DB rows does not break the identifier or the artifacts dispatch.
- **The new wrapper validation cannot raise where the old gate silently skipped.** Stage 1 mirrors `get_new_company_batch` by validating every entry of `states` against `CANDIDATE_STATES`. I resolved both live candidate trigger states: `REQUESTED_ARTIFACTS` → `['REQUESTED_ARTIFACTS', 'REQUESTED_ARTIFACTS_RETRY']` and `ACTIVE_SEARCH` → `['ACTIVE_SEARCH']`, all registry keys. The old code turned a non-member into `entities = []`; the new code would have raised. No candidate row reaches that path.
- **Stage 2 step 5 ordering holds.** `use_full_batch` is computed at line 467, before the entity branch, and `entity_type` is bound at 457 — the forced `use_full_batch = False` slots in cleanly.
- **Insertion sites are exactly where the plan says.** Empty-batch `if entity_type == "job" and bid: clear_job_batch(bid)` at 537, `elif entity_type == "candidate": pass` in `finally` at 651, late job/company imports at 453–455 (function-scope, so visible in `finally`), and the `return s` at 551 sits outside the `try` — the added empty-batch clear cannot double-clear.
- **`limit_val = limit if limit is not None else 10`** is character-for-character `get_new_job_batch` line 718, so the fallback literal is landed-code parity, not a new magic number (`astral.standards.no-hardcoded-sets` → conforms).
- **Boundary respected:** `gaze_email` is handled in `_dispatch_one` at line 738 and never reaches the candidate claim arm, so the parent's non-`ENTITY_TYPES` mailbox exception is untouched.

## Findings

None at `fix-now` or `discuss`.

### acceptable

- `bid` falsiness: `bid = ctx.get("entity_batch_id") or log_batch_id.get()` (line 465) and the wrapper raises if neither `batch_id` nor `context` is given. Identical exposure to the job arm, which passes `batch_id=bid` the same way — parity is the right call.
- The `finally` clear passes `bid` unguarded, matching job (line 649–650) rather than the guarded empty-batch site. Consistent with the arm it mirrors.

Status → Plan Approved.

— Joan

context_tokens≈62000

#### ada — 2026-08-07T18:53:31.953Z
[plan-discuss] round=1 reply

Patched plan on `origin/sub/AST-1257/AST-1259-dispatcher-and-core-candidate-pool-claim-parity` (Revision 1).

**fix-now — Tests invalidated:** added **Tests invalidated (Betty contract)** with both node ids (`test_ast505_candidate_entity_routes_ctx_without_company_clear`, `test_run_unified_candidate_claim_gate`), today vs after-Stage-2 expectations, and Betty coverage list (batch_size/claim_states, empty clear, finally clear, per-row consult, no job/company clear).

**discuss — AC4 release:** Stage 3 Done-when + step 2 — release stays silent at job/company parity; no clear-side `debug_detail`.

**discuss — inflow ctx:** Stage 2 inflow Decision now records accepted cross-candidate cadence (`A`’s `inflow_discovery_freq_hrs` with `B`’s terms); no row-scoped inflow claim this ticket.

#### joan — 2026-08-07T18:52:01.645Z
[plan-discuss] round=1 concern
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1259
**Overall:** REVISE
**Publish ref tip:** `sub/AST-1257/AST-1259-dispatcher-and-core-candidate-pool-claim-parity` @ `ded4e05e` (AST-1258 product code is already on this branch, so I verified against the real claim APIs, not the plan's description of them)

## Traceability

AC3→S2; AC4→S3; S1 (core wrappers) → parent Functional scope 2 ("Data **and core** expose claim → get → clear helpers"). No orphan stages; no unmapped AC. R5 pass.

**Considered:** 53 active statutes scored in-session (18 universal + 35 scoped considered, 12 scoped excluded).

## Findings

### fix-now — Stage 2 breaks two passing dispatcher tests the plan does not disclose

Both pass on this tip (I ran them by exact node id) and both assert the unlocked `[ctx]` behavior Stage 2 deletes:

1. `tests/component/core/test_dispatcher.py::TestRunUnified::test_ast505_candidate_entity_routes_ctx_without_company_clear` (line 332) — asserts `run_consult_task` is awaited with `[ctx]` as the entity list. After Stage 2 the entity list comes from `get_new_candidate_batch`, so the awaited args change (and with no claim stub in that test, nothing is claimed and the await never happens).
2. `tests/component/core/test_dispatcher.py::TestAst972CandidateStageDispatch::test_run_unified_candidate_claim_gate` (line 1562) — asserts the gate itself: `bad` ctx state → `run.assert_not_called()`, `good` → `run.await_args.args[2] == [good]`. That is precisely the `entities = [ctx] if ctx and cur in claim_states else []` arm Stage 2 replaces.

The plan says "Engineer does **not** edit `tests/` or bible" but discloses no invalidation, so build-child lands on a red suite with nothing sanctioned to do about it (`orch.roles.betty-owns-test-tree`, `astral.git.engineer-test-tree-ban`, `orch.pipeline.plan-is-bible` → violates).

**Recommendation:** add a **Tests invalidated (Betty contract)** section in the same shape AST-1258 landed — both node ids, today's expectation vs after-Stage-2 expectation — plus the coverage Betty owns here: claim through the wrapper honoring `batch_size` / `dispatch_claim_states`, empty-batch clear, `finally` clear (no more `pass`), one `run_consult_task` call per claimed row for a multi-row pool (the forced `use_full_batch=False`), and no job/company clear on the candidate path.

### discuss — AC4 covers the release step, and Stage 2 introduces two new release sites

Stage 3 only confirms the pre-existing post-claim block. That block is genuinely entity-agnostic and `_dispatch_entity_identifier` already handles `candidate`, so the claim side is fine as written. But Stage 2 adds two candidate clear calls (empty-batch early exit and `finally`) and neither emits anything, so "what was **recorded** per step" (parent Functional scope 6, child AC4) has no line on the step this ticket introduces. Job and company log nothing on clear either, so parity is a defensible answer — it just needs to be the stated one.

**Recommendation:** either add one gated `debug_detail` on the candidate release (both sites), or state in Stage 3 that release logging stays at job/company parity, so Radia does not read AC4 as unmet. `astral.standards.debug-contract-gated` → needs-discussion (mechanism conforms — reusing the shared Style D block and explicitly banning a parallel `logger.info("[DEBUG] …")` is right).

### discuss — cross-candidate claim changes what the dispatch row's `ctx` means, and the inflow arm still reads it

This is the first claim in the system that crosses candidates (job scopes through `company.candidate_id`, company scopes on `candidate_id`), so a row owned by candidate A can now claim and process candidate B. I checked the half that would have been a real defect and it is safe: `run_requested_artifacts_dispatch(cid)` re-reads the claimed candidate by id and builds its own `task_ctx`, so `do_task` picks up **B's** `candidate_api_key`, not A's.

The inflow arm is the loose end. `consult.run_consult_task` passes the dispatch row's `ctx` alongside the claimed entity, and `roster.run_inflow_discovery_batch` takes `freq_hrs` from `(ctx or {}).get("inflow_discovery_freq_hrs")` — so B's search terms get evaluated against A's staleness window, and the ledger attributes B's work to A's row.

**Recommendation:** one line in the Stage 2 inflow Decision recording this as accepted (it is small — cadence only, and the no-stale-terms no-op you already cite limits the blast radius), or scope the inflow claim to the row's candidate. Either is fine; I want it decided in the plan rather than discovered at review.

### acceptable

- `get_new_candidate_batch(batch_id=bid)` with no `context`: the job arm does exactly this and the company arm passes both. If `bid` were ever empty the wrapper would raise, but that exposure already exists for job, so parity is the right call.

## Verified against the tip (no change needed)

- Stage 2 step 2 quotes the current candidate arm verbatim; the empty-batch `if entity_type == "job" and bid: clear_job_batch(bid)` and the `elif entity_type == "candidate": pass` in `finally` are exactly where the plan says they are.
- The empty-batch `return s` sits **outside** the `try`, so the plan's added clear there cannot double-clear against `finally`.
- Forcing `use_full_batch = False` is not defensive — the candidate arm of `run_consult_task` really does read `entities[0]` only (`cid = entities[0]…`, `run_inflow_discovery_batch(entities[0], …)`), so without it a pool claim >1 would silently drop rows. `use_full_batch = batch_call_mode or (dispatch_task_key == "parse_job_list")` is where the plan says it is.
- Stage 1 preconditions all hold: `candidate.py` imports `uuid`, imports `CANDIDATE_STATES`, uses `from src.data import database` (so the wrapper name does not shadow the data function), has `typing` as `Any, Dict, Optional, Tuple` (so adding `List` is required), and imports `dispatcher` at module top — which is exactly why the dispatcher side must late-import. `list_candidates` is at line 1443.
- The wrapper's call shape matches the landed AST-1258 signature `claim_candidate_batch(batch_id, state, limit, sort_by=None, *, states=None)`, and the dispatcher's default `sort_by="updated_at"` is in `_CANDIDATE_BATCH_SORT_COLUMNS`.
- `get_new_company_batch` validates each entry of `states` the way Stage 1 describes, so the mirror is accurate.

Status → Plan Discuss. One fix-now; the two discuss items are one or two sentences each.

— Joan

context_tokens≈132000

#### ada — 2026-08-07T18:46:02.992Z
Plan published on `origin/sub/AST-1257/AST-1259-dispatcher-and-core-candidate-pool-claim-parity` @ `ded4e05e`.

https://github.com/susansomerset/astral/blob/sub/AST-1257/AST-1259-dispatcher-and-core-candidate-pool-claim-parity/docs/features/dispatcher/ast-1259-dispatcher-and-core-candidate-pool-claim-parity.md

**Scope:** Single-Component — core wrappers in `candidate.py` + `_run_unified` claim/release in `dispatcher.py` only.

**Conf:** high — mirrors job/company `get_new_*_batch` and replaces the named unlocked `[ctx]` candidate arm; AST-1258 claim APIs already on tip.

**Risk:** Medium — bad claim/clear leaves locks or races; forcing per-entity process for candidate avoids dropping pool rows on `entities[0]`-only consult without expanding consult scope.

---

# AST-1259 — Dispatcher and core candidate pool claim parity

**Linear:** [AST-1259](https://linear.app/astralcareermatch/issue/AST-1259/dispatcher-and-core-candidate-pool-claim-parity-candidate-table-does)
**Parent:** [AST-1257](https://linear.app/astralcareermatch/issue/AST-1257/candidate-table-does-not-have-batch-id) — candidate table does not have batch_id
**Publish ref:** `origin/sub/AST-1257/AST-1259-dispatcher-and-core-candidate-pool-claim-parity`

After AST-1258’s data-layer claim / get / clear, add core `get_new_candidate_batch` / `clear_candidate_batch` wrappers and replace the unlocked single-ctx candidate branch in `dispatcher._run_unified` with claim → process → release using the same `batch_size` / `dispatch_claim_states` pool mechanics as job/company (always clear in `finally` and on empty-batch early exit; Style D debug on the touched claim path). Does **not** own schema/data APIs (AST-1258) or statute/pattern/docs text (AST-1260).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/candidate.py` | Add `get_new_candidate_batch` / `clear_candidate_batch` (batch_id-first wrappers over AST-1258 data APIs); extend module docstring | core |
| `src/core/dispatcher.py` | Candidate branch of `_run_unified`: claim via those wrappers; empty-batch clear; `finally` clear; force per-entity process for candidate so pool claims are not dropped by `batch_call_mode=1` + `entities[0]`-only consult | core |

No `src/data/database.py`, `src/utils/config.py`, consult runners, gaze_email mailbox path, statute/canon, or `CANDIDATE_DATA_MODEL.md`. Engineer does **not** edit `tests/` or bible (`orch.roles.betty-owns-test-tree`); see **Tests invalidated (Betty contract)** below for the suite delta Stage 2 causes.

## Tests invalidated (Betty contract)

Stage 2 deletes the unlocked `[ctx]` candidate arm in `_run_unified`. These two component tests pass on tip `ded4e05e` and assert that arm; after Stage 2 they fail. Builder does not touch `tests/` or bible — Betty owns the revision (`qa-child` after Code Complete).

| Item | Detail |
|------|--------|
| **Broken by tip (after Stage 2)** | `tests/component/core/test_dispatcher.py::TestRunUnified::test_ast505_candidate_entity_routes_ctx_without_company_clear` |
| **Today (pre-Stage 2)** | `run_consult_task` awaited with entity list `[ctx]` (unlocked single-ctx path) |
| **After Stage 2** | Entity list comes from `get_new_candidate_batch`; without a claim stub the await may not happen / args are claimed rows, not raw `ctx` |
| **Broken by tip (after Stage 2)** | `tests/component/core/test_dispatcher.py::TestAst972CandidateStageDispatch::test_run_unified_candidate_claim_gate` |
| **Today (pre-Stage 2)** | `bad` ctx state → `run.assert_not_called()`; `good` → `run.await_args.args[2] == [good]` (exact `entities = [ctx] if … else []` gate) |
| **After Stage 2** | Gate is pool claim via wrappers + `dispatch_claim_states` / `batch_size`; stub `get_new_candidate_batch` (or DB claim) instead of mutating ctx state alone |

**Coverage Betty must add or extend for this ticket** (component / bible for dispatcher claim path):

1. Claim through `get_new_candidate_batch` honors `batch_size` and `dispatch_claim_states` (multi-row unclaimed pool → claimed under one `batch_id`).
2. Empty-batch path calls `clear_candidate_batch(bid)` (same early-exit site as job clear).
3. `finally` calls `clear_candidate_batch` (no more `pass`); locks released after process.
4. Multi-row claim → one `run_consult_task` call per claimed row (`use_full_batch=False`).
5. Candidate path does **not** call `clear_job_batch` / `clear_company_batch`.

## Stage 1: Core claim wrappers

**Done when:** `src/core/candidate.py` exposes `get_new_candidate_batch` and `clear_candidate_batch` with the same call shape as `tracker.get_new_job_batch` / `clear_job_batch` (minus job-only score_floor / candidate_id / claim_cap), calling `database.claim_candidate_batch` / `get_candidate_batch` / `clear_candidate_batch`. No dispatcher wiring yet.

1. In `src/core/candidate.py`, add `List` to the existing `typing` import (`Any, Dict, List, Optional, Tuple`).
2. Update the module docstring so the in-scope list names `get_new_candidate_batch` and `clear_candidate_batch` (batch claim wrappers; AST-1259).
3. After `list_candidates` (before state-transition helpers), add a `# ---- Batch API ----` section with:
   - `get_new_candidate_batch(state: str, limit: Optional[int] = None, sort_by: Optional[str] = None, batch_id: Optional[str] = None, context: Optional[str] = None, *, states: Optional[List[str]] = None) -> Tuple[str, List[Dict[str, Any]]]`:
     - Allowed states = `list(CANDIDATE_STATES.keys())`. If `states is None`, require `state in allowed` else raise `ValueError` naming the allowed list. If `states` is provided, validate **each** entry the same way (mirror `get_new_company_batch`).
     - `limit_val = limit if limit is not None else 10`.
     - If not `batch_id` and not `context`: raise `ValueError("batch_id or context is required for batch_id generation")`.
     - `bid = batch_id or f"{context}-{uuid.uuid4()}"` (uuid already imported).
     - Call `database.claim_candidate_batch(bid, state, limit_val, sort_by=sort_by, states=states)`.
     - Return `(bid, database.get_candidate_batch(bid))`.
   - `clear_candidate_batch(batch_id: str) -> int`: return `database.clear_candidate_batch(batch_id)`.
4. Do **not** add `candidate_id` / `score_floor` / `claim_cap` parameters — AST-1258 pool claim is cross-candidate; job/company scoping knobs do not apply.
5. Do **not** import these from `dispatcher.py` at module top (candidate already imports dispatcher; keep wrappers callable via late import from `_run_unified`).

⚠️ **Decision:** Wrappers live in `candidate.py` (entity owner), parallel to job→`tracker` and company→`roster`, not a new module and not inside `dispatcher.py`.

## Stage 2: Dispatcher claim → process → release

**Done when:** `_run_unified` for `entity_type=candidate` claims via `get_new_candidate_batch` (using `dispatch_claim_states` + `batch_size`), processes claimed rows, clears the lock on empty early-exit (like job) and in `finally` (no more `pass`), and never uses the unlocked `entities = [ctx] if ctx and cur in claim_states` branch.

1. In `src/core/dispatcher.py` `_run_unified`, keep the existing late imports of job/company helpers. Add a late import: `from src.core.candidate import get_new_candidate_batch, clear_candidate_batch` (same block / adjacent lines — late, not module-top).
2. Replace the candidate claim arm:
   ```python
   if entity_type == "candidate":
       claim_states = dispatch_claim_states(input_state, "candidate")
       cur = (ctx.get("state") or "").strip() if ctx else ""
       entities = [ctx] if ctx and cur in claim_states else []
   ```
   with:
   ```python
   if entity_type == "candidate":
       claim_states = dispatch_claim_states(input_state, "candidate")
       bid, entities = get_new_candidate_batch(
           input_state,
           limit=limit,
           sort_by=sort_by,
           batch_id=bid,
           states=claim_states,
       )
   ```
   Keep the job / company arms unchanged.
3. Empty-batch early exit (today clears job only): extend so candidate also clears when `bid` is set:
   ```python
   if not entities:
       if entity_type == "job" and bid:
           clear_job_batch(bid)
       elif entity_type == "candidate" and bid:
           clear_candidate_batch(bid)
       ...
   ```
   Leave company empty-path behavior unchanged (still no clear on empty).
4. In the existing `finally` block, replace `elif entity_type == "candidate": pass` with `clear_candidate_batch(bid)` (same position — after job, before company).
5. After `use_full_batch` is computed (`batch_call_mode or dispatch_task_key == "parse_job_list"`), force per-entity processing for candidate so pool claims are not silently reduced to `entities[0]` inside `consult.run_consult_task`:
   ```python
   if entity_type == "candidate":
       use_full_batch = False
   ```
   Do **not** edit `consult.py` / inflow / `run_requested_artifacts_dispatch` in this ticket.
6. Do **not** change `_dispatch_one` ledger mint (`f"{task_key}-{uuid4()}"`), gaze_email mailbox early-return, network skip, or AUTO eligibility / `count_eligible_for_dispatch_task` (AST-1258 already flipped stage Avail to the unclaimed pool).

⚠️ **Decision:** `inflow_discovery` uses the same pool claim path (ACTIVE_SEARCH via `dispatch_claim_states`). Avail still uses the inflow eligibility helper (AST-1258). Claimed ACTIVE_SEARCH rows without stale terms already no-op inside `run_inflow_discovery_batch` (“no stale search terms”) and still release in `finally` — do not invent an inflow-only claim filter here. **Accepted cross-candidate ctx:** a dispatch row owned by candidate A may claim/process candidate B; `run_inflow_discovery_batch` still reads `inflow_discovery_freq_hrs` from the row’s `ctx` (A’s cadence) while search terms come from B — cadence-only mismatch; no-stale no-op limits blast radius. Do **not** scope inflow claim to the row’s `candidate_id` in this ticket.

⚠️ **Decision:** Force `use_full_batch = False` for candidate so `_warm_then_gather` runs `run_consult_task` once per claimed row. Expanding consult to multi-entity candidate batches is out of scope; this keeps pool claim correct without touching consult.

## Stage 3: Debug contract on the claim path + smoke

**Done when:** With `debug=True`, the existing `_run_unified` Style D claim headers/details fire for candidate the same way they do after a job/company claim (found/recorded: claimed count, per-entity identifiers via `_dispatch_entity_identifier`, batch end summary). Manual smoke confirms claim → clear without editing tests. **Release logging:** Stage 2’s empty-batch and `finally` `clear_candidate_batch` sites emit nothing — same as job/company clear (AC4 / parent “recorded per step” is satisfied by the shared claim-side Style D block, not by new clear-side lines).

1. Confirm (do not duplicate) the existing post-claim debug block in `_run_unified` (claimed N / per-entity `debug_index` + `debug_detail` with Style D ` | ` prefix) runs for candidate after Stage 2 — it already keys off `entities` / `entity_type` and does not special-case candidate away. If Stage 2 somehow skips it, restore the shared path; do not add a parallel `logger.info("[DEBUG] …")` style.
2. Do **not** add gated `debug_detail` on `clear_candidate_batch` at the empty-batch or `finally` sites — release stays at job/company parity (silent clear).
3. Empty-batch debug already emits `outcome="no entities claimed"` with `batch_id={bid}` — leave it; after Stage 2 `bid` is the golden ticket used for claim.
4. Manual smoke under `debug/spikes/AST-1259/` (gitignored; do not commit) or equivalent local check:
   - ≥2 unclaimed candidates in `REQUESTED_ARTIFACTS`; run a candidate `entity_type` dispatch path (or call `get_new_candidate_batch` + `clear_candidate_batch` then a thin `_run_unified` exercise) with `batch_size=2` and `debug=True`.
   - Assert rows locked under one `batch_id`, then unlocked after clear / `finally`.
   - Empty claim (`limit` with no matching unclaimed rows) still calls `clear_candidate_batch` and does not leave locks.
5. No product commit required for smoke-only if Stages 1–2 already committed; smoke findings that need code fixes stay in Stage 2’s files.

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; publish each to `origin/sub/AST-1257/AST-1259-dispatcher-and-core-candidate-pool-claim-parity`.
- Do not add files outside **Files Changed**.
- Do not edit `src/data/database.py`, statutes, pattern catalog, CODE_RULES §2.4 wording, or `CANDIDATE_DATA_MODEL.md`.
- On ambiguity or drift: stop and comment on **parent** AST-1257 with the 🛑 Stage N blocked template.

## Self-Assessment

**Scope:** Single-Component — core only (`candidate.py` wrappers + `dispatcher.py` claim/release parity); no data/UI/config.

**Conf:** high — mirrors `get_new_job_batch` / `get_new_company_batch` and replaces a named unlocked branch; AST-1258 APIs and empty/finally clear sites are already visible in `_run_unified`.

**Risk:** Medium — wrong claim wiring can double-process or leave locks; forcing per-entity process avoids silent drop of pool rows but changes behavior vs a theoretical `batch_call_mode=1` full-batch consult path for candidate (consult was never multi-entity-aware).

## Rules check (plan vs ASTRAL_CODE_RULES)

| Rule | Plan stance |
|------|-------------|
| §2.4 claim-process-release / batch-id-first / batch-id-format | Core wrappers call data claim with batch_id first; dispatcher mints `f"{task_key}-{uuid}"` already; finally + empty clear |
| §1.5.1 debug-contract-gated | Reuse existing `_run_unified` Style D index/detail; emit only when `debug=True` |
| §3.3 import-direction | Late import core→core inside `_run_unified`; candidate wrappers call data only |
| §1.3 DRY / public-then-helpers | Wrappers grouped under Batch API; no duplicated claim SQL |
| §2.1 config SSoT | `dispatch_claim_states` + `CANDIDATE_STATES` validation; no new state lists |
| §2.6 core-decides-transitions | Claim/clear touch lock columns only; state transitions stay in existing craft/inflow runners |
| Out of scope | Data schema/eligibility (AST-1258); statute/pattern/`CANDIDATE_DATA_MODEL` (AST-1260); gaze_email non-ENTITY_TYPES mailbox; consult multi-entity rewrite |
| Betty contract / engineer test-tree ban | Stage 2 invalidates two dispatcher component tests; plan discloses node ids + after-expectation; engineer does not patch `tests/` |
| `astral.standards.dry-and-focused-functions` / `astral.standards.public-then-helpers` | **In scope / conforms** (resolve): scoped statutes; Batch API grouping + no duplicated claim SQL — plan had excluded as “universal”; Radia C4 discuss |

## Revisions

**Revision 1 — 2026-08-07**  
Driven by: Joan `[plan-discuss] round=1 concern` (REVISE @ `ded4e05e`)  
Changes: added **Tests invalidated (Betty contract)** (fix-now — both unlocked-`[ctx]` node ids + Betty coverage list); Stage 3 states release logging stays at job/company parity / no clear-side `debug_detail` (discuss); Stage 2 inflow Decision records accepted cross-candidate `ctx` cadence for inflow (discuss).

## Review (build stub)

**Publish ref:** `origin/sub/AST-1257/AST-1259-dispatcher-and-core-candidate-pool-claim-parity`
**Tip:** `e0d18dab`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `35265641` | `get_new_candidate_batch` / `clear_candidate_batch` in `candidate.py` |
| 2 | `e0d18dab` | `_run_unified` pool claim; empty + finally clear; force per-entity process |
| 3 | (smoke) | Temp-DB claim → clear + empty clear; Style D claim path unchanged (no product delta) |

## Radia review — [code-rubric] revision=1

**Publish ref:** `sub/AST-1257/AST-1259-dispatcher-and-core-candidate-pool-claim-parity` @ `d950de10`
**Overall:** DISCUSS

Full active-set sweep run in-session (65 active statutes: 18 universal + 47 scoped — 39 scoped matched and scored, 8 scoped `not-applicable`). Branch not yet merged onto `dev`, so the three-dot diff also carries AST-1258's already-`Review Posted` data-layer content — not re-litigated here; findings below are scoped to what's new: `src/core/candidate.py`, `src/core/dispatcher.py`, and their tests/bible.

**Plan adherence:** Stage 1 (`35265641`) / Stage 2 (`e0d18dab`) land exactly as planned — `get_new_candidate_batch` / `clear_candidate_batch` mirror `get_new_job_batch` / `get_new_company_batch`; `_run_unified`'s candidate arm swaps the unlocked `[ctx]` gate for a real pool claim, adds empty-batch clear, and replaces the `finally` `pass` with `clear_candidate_batch(bid)`. `use_full_batch = False` forced for candidate is required and correctly scoped. Joan's round-1 items (undisclosed test invalidation; AC4 release-logging parity; cross-candidate inflow `ctx` cadence) are all closed by Revision 1. Scope held — `code()` commits touch only the two core files; `test()`/`merge-tests()` touch only tests/bible; clean role separation across all five commits.

**Pattern conformance:** `pattern.batch.entity-claim-process-release` — conforms; closes the gap AST-1258 opened (candidate now does real claim → process → release, matching job/company).

**Findings:**
- **discuss** — misplaced `@pytest.mark.skipif` decorator in `test_dispatcher.py`: the new `TestAst1259CandidatePoolClaim` class landed between the pre-existing skip decorator and its intended target `TestAst972CandidateStageDispatch` (confirmed against `origin/dev`'s file at the same lines). Condition is `False` either way on this tip so nothing fails today, but the guard now tracks the wrong class. Betty/test-tree fix, not engineer fix-now.
- **discuss** — straggler: `astral.standards.dry-and-focused-functions` and `astral.standards.public-then-helpers` were excluded at plan time ("universal; no new statute work") but both are `tier: scoped` and mechanically match this diff's `core` layer / `src/core/**` paths, so this sweep scores both `conforms` (not `not-applicable`). Content genuinely conforms — flagged per C4 to reconcile the plan-exclusion label with the sweep predicate.

**What's solid:** claimed-row shape flows unchanged through `_dispatch_entity_identifier` / `run_consult_task`; the existing entity-agnostic Style D debug block now fires correctly for candidate with zero new debug code; `limit_val` fallback is character-for-character the `get_new_job_batch` precedent; test/bible delta precisely revises the two Stage-2-invalidated tests and adds direct multi-row/empty/finally-clear coverage.

context_tokens≈158000

— Radia


## Resolution

**Date:** 2026-08-07  
**Tip before resolve:** `d79cd9a0` (Radia `docs(AST-1259): Radia review — findings`)

| Finding | Action |
|---------|--------|
| **fix-now** — misplaced `@pytest.mark.skipif` above `TestAst1259CandidatePoolClaim` instead of `TestAst972CandidateStageDispatch` | No product change. **`[qa-handoff]`** → Betty; cleared @ `a4f94240` (`test(AST-1259): restore skipif on TestAst972CandidateStageDispatch`). Manifest re-run: 10 passed. |
| **discuss** — `dry-and-focused-functions` / `public-then-helpers` plan-excluded vs mechanical `conforms` | No product change. Linear **In scope** + plan Rules check now list both (Batch API grouping; no duplicated claim SQL). |

**fix-now (product):** none.

