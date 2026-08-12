<!-- linear-archive: AST-1191 archived 2026-08-07 -->

## Linear archive (AST-1191)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1191/artifact-hop-failure-release-debug-trail-anticipate-scan-jobs-failing  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1164 — anticipate_scan jobs failing  
**Blocked by / blocks / related:** parent: AST-1164

### Description

## What this implements

After siblings #1 and #2: on provider failure for `anticipate_scan` / shared artifact hops, ensure batch release + configured error/hold state, and AST-538-style debug found/recorded for UAT. Does **not** redesign LLM adapters beyond consuming their structured failures.

## Acceptance criteria

- [X] 3. After such a failure on `anticipate_scan`, the job is not left batch-claimed; it is on the configured artifact error/hold state for that task, and the failure reason is visible against that `batch_id` in Execution History / app_log.
- [X] 4. A debug-gated run of the fixed path shows found/recorded lines for duration, stop, tokens, and error/failure class on the failed call.

## Boundaries

* Does not own provider call time budget / timeout failure class (Ada sibling AST-1189).
* Does not own empty/unusable provider response classification (Hedy sibling AST-1190).
* Does not fix hollow name/ANALYSIS tokens (AST-1163).
* Does not redesign LLM adapters beyond consuming structured failures from #1/#2.

## In scope

- [X] `pattern.batch.entity-claim-process-release` — provider failure still claim/process/release; no orphaned `batch_id` on the job (`src/core/agent.py` `_apply_dispatch_chain_hop_failure` + existing consult clear)
- [X] `astral.batch.claim-process-release` — transition to `error_state` then `release_job_dispatch_claim` while history can still see `batch_id`
- [X] `astral.dispatch.run-next-is-chain-authority` — consume hop failure inside existing `do_task` / dispatch-chain path; no `run_next` topology change
- [X] `astral.standards.debug-contract-gated` — found/recorded duration/stop/tokens/failure_class only when `debug=True` on the provider-failed path
- [X] `astral.agent.do-task-delegation` — core consumes structured `error` / `failure_class` / `timesheet` from external; no adapter redesign
- [X] `astral.standards.in-scope-only` — hop release + debug trail only
- [X] `astral.standards.logging-via-utils` — keep `do_task(...) provider call failed … error=` ERROR; debug via `_do_task_debug_logger`
- [X] `astral.standards.dry-and-focused-functions` — one helper owns apply error_state + release

## Considered but excluded

- [X] `pattern.config.config-block` / `PROVIDER_CALL_BUDGET` — AST-1189 (`src/utils/config.py` timeout budget)
- [X] `astral.patterns.coat-check-never-store-empty` / hollow predicate — AST-1190 (`src/utils/llm_external.py` / externals)
- [X] `astral.layers.core-vs-external-bright-line` edits in `src/external/**` — adapters untouched this ticket
- [X] `astral.standards.data-raises-caller-logs` — no `src/data/**` changes
- [X] `src/ui/**` — no Generate Artifacts chrome changes
- [X] AST-1163 name/ANALYSIS token context — separate epic

## Notes for planning

After AST-1189 and AST-1190 (both User Testing). Citations as above. Gap today: `_apply_dispatch_chain_hop_failure` only hard-fails on missing job/candidate strings, so provider failures leave the job in `BUILD_ARTIFACTS` after claim clear.

## Git branch (authoritative)

**Publish ref:** `origin/sub/AST-1164/AST-1191-artifact-hop-failure-release-debug`

Per orientation § Branch law: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at dispatch-parent.

### Comments

#### radia — 2026-08-06T00:20:19.261Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1191
**Publish ref:** `origin/sub/AST-1164/AST-1191-artifact-hop-failure-release-debug` @ `5c6cdcda` (docs-only review append at `d8864b7a`)
**Overall:** CLEAN

## Plan adherence

Isolated this ticket's own contribution via `git diff ee5e760f..5c6cdcda` (the tip AST-1189 left for merge-child) rather than the full three-dot `origin/dev` diff, since the latter also carries already-reviewed AST-1189/AST-1190 product code stacked via `ftr`. AST-1191's own footprint is exactly `src/core/agent.py` (105 lines) + its plan doc + test-bible + tests — matching the Files Changed table with no scope creep. Both Joan revision rounds are honored: `_apply_dispatch_chain_hop_failure` and `_close_hop_ledger` return the outcome dict from **every** exit (including the no-op / no-ledger early returns — no bare `return None` regression), balance-refusal still holds state while releasing the claim, transition happens before release (state_history still stamps the in-flight `batch_id`), and Stage 2's found/recorded lines read the real timesheet keys (`inputtotal`/`inputcached`/`outputtotal`/`cache_creation_tokens`) with honest `n/a` on missing keys — no silent-zero regression of the parent symptom.

Verified `clear_job_batch_lock` (`src/data/database.py`) is a plain `UPDATE ... SET batch_id = NULL` — confirms the plan's "dual clear is idempotent" claim for the intentional double release (`_apply_dispatch_chain_hop_failure` + the existing consult batch runner clear).

Ran the ticket's own test class plus the adjacent `TestAst848DispatchChainDoTask` regression test in a fresh venv: **11/11 pass**. The broader touched-file test run surfaces ~30 pre-existing failures (statute-count fixture drift, shared sqlite db schema state, and unrelated in-flight epics AST-901/1054/1060/1127/1195 whose product code isn't on this branch) — none in `TestAst1191*` or `TestAst848*`, confirmed against an `origin/dev` baseline showing the same classes of failure already present. Not diff-caused.

## Findings

None (fix-now / discuss). No repeat of AST-1189's cross-ticket merge-tests contamination — this branch's `merge-tests(AST-1191)` diff is a clean, isolated 2-file/240-line addition (own test-bible + test file only).

## Pattern conformance

None cited (plan lists statute ids under In-scope / Considered-but-excluded, covered by the full-set sweep).

## Frame diff

(none) — diff matches the plan's Files Changed table exactly; no unplanned adds.

### What's solid

- `_apply_dispatch_chain_hop_failure` / `_close_hop_ledger` outcome-dict threading is correct on every exit path (verified against both Joan revision concerns).
- Debug found/recorded gating is correct — `found` sits inside the existing `if debug:` block, `recorded` is gated separately after `_close_hop_ledger`, and `debug=False` emits neither (test-covered).
- `astral.batch.claim-process-release`, `astral.state.core-decides-transitions`, `astral.state.job-prior-states-enforced` all conform — transition-then-release ordering, `ValueError` enforcement preserved via existing try/except, core (not data) decides `err_state`.

`context_tokens≈52000`
— Radia

#### betty — 2026-08-06T00:12:52.121Z
## QA test manifest

`origin/sub/AST-1164/AST-1191-artifact-hop-failure-release-debug` @ `5c6cdcda` (`merge-tests(AST-1191): origin/tests ac509b12`)

1. `tests/component/core/test_agent.py::TestAst1191ArtifactHopFailureRelease` — unit: provider fail → `error_state` + `release_job_dispatch_claim`; balance hold skips transition but still releases; non-dispatch → `_HOP_FAILURE_NOOP`
2. Same class — `do_task`/`anticipate_scan`: provider timeout → `ERROR_BUILD_ARTIFACTS` + claim release
3. Same class — `debug=True` found (duration/stop/tokens/`failure_class`) + recorded (error / error_state|held / batch_released); `debug=False` quiet
4. `TestAst848DispatchChainDoTask::test_hard_failure_transitions_error_build_artifacts` — hard-string path still transitions; now also asserts claim release

**Narrowed run:**
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst1191ArtifactHopFailureRelease \
  tests/component/core/test_agent.py::TestAst848DispatchChainDoTask::test_hard_failure_transitions_error_build_artifacts
```

**Bible:** `docs/test-bible/core/agent.md` @ `9b9501dfe578df7e9c8b5f4108ff62df2848450d  -`

Smoke on publish tip: 7 passed.

#### joan — 2026-08-06T00:06:31.876Z
[plan-rubric] revision=1

**Rubric:** plan-rubric.v1
**Ticket:** AST-1191
**Overall:** APPROVED
**Publish ref tip:** `origin/sub/AST-1164/AST-1191-artifact-hop-failure-release-debug` @ `ec8971de`

## Traceability

AC3→S1; AC4→S2. Parent AC1/AC2/AC5 are N/A–boundary for this child (Ada AST-1189 / Hedy AST-1190). No unmapped child AC, no orphan stages.

**Considered:** full active corpus re-swept (65 leaves — 18 universal + 30 scoped considered, 17 scoped excluded on layer/path predicates). Files Changed is unchanged across all three revisions (`src/core/agent.py`, modify, core), so the considered/excluded sets are identical to round=1 and every considered statute scores `conforms`. Scored in-session per R7.

## Round=2 fix-now — verified closed

Stage 1 step 7 now spells the full `_close_hop_ledger` body instead of deferring to "existing logic unchanged", and I diffed that body against the real function (`src/core/agent.py:2188-2212` on the epic ftr ref) line for line:

- `nonlocal hop_ledger_closed`, the `_apply_dispatch_chain_hop_failure` kwargs (`entity_type or ""`, `index`, `ctx`, `task_config`, `error=failure_error`, `debug`), the `_finalize_run_next_hop_ledger(hop_ledger_batch_id, success=success, batch_size=batch_size)` call, the `hop_ledger_closed = True` flag, and the `clear_log` guard are all reproduced exactly. Nothing from today's body is dropped and nothing is invented; `hop_ledger_batch_id` is read-only in the closure, so no second `nonlocal` is needed.
- The early exit is `return outcome`, with a comment naming why (no-ledger calls) so the next reader does not "simplify" it back to a bare `return`. Done-when and the Stage 1 Decision both restate the every-exit discipline, matching the `_HOP_FAILURE_NOOP` treatment on the sibling helper.
- Stage 2 step 2 normalizes `hop_fail_outcome = hop_fail_outcome or _HOP_FAILURE_NOOP` before any key access. Since the stages are separate commits, that belt-and-braces line means even a slip in Stage 1 cannot `TypeError` out of `do_task` and skip consult's claim release.

Both halves of the recommendation landed, so the AC3-regress path I raised in round=2 is closed twice over.

## Findings

**1. `acceptable`** — Stage 2's normalize aliases the module-level `_HOP_FAILURE_NOOP` rather than copying it (Stage 1 returns use `dict(...)`). The alias is only read for the recorded line's display fields, never mutated, so there is no shared-state hazard — noting it so nobody later adds a mutation on top of the alias.

**2. `acceptable`** — `_ts_num` uses `isinstance(v, (int, float))`, which admits `bool`. No external path puts a bool in those keys today. Carried forward from round=2, still a note only.

**3. `acceptable`** — Dual claim release (helper + consult batch runner) stays a recorded Decision. Re-confirmed this pass: `tracker.release_job_dispatch_claim` takes one job id and delegates straight to `database.clear_job_batch_lock` (`tracker.py:747-749`), and consult's failure branch releases without transitioning state (`consult.py:2286-2287`), so the clear is idempotent and cannot collide with the new `ERROR_BUILD_ARTIFACTS` transition or trip `prior_states`.

**4. `acceptable`** — The pre-existing hard-string gate (`"Job not found"` / `"Missing candidate_data"`) survives as literal substring matching. `astral.standards.in-scope-only` argues for leaving it alone here; noted so its retention is not read as an endorsement.

## Closing verification

- **Debug contract (§1.5.1 / `astral.standards.debug-contract-gated`):** found/recorded are `debug_detail` lines emitted only under `debug=True`, and they sit beneath a real index header — `_resume_hop_debug_index` runs early in `do_task` (`agent.py:1963`) and `dbg.debug_index` fires at `agent.py:2169` — so Style D holds, consistent with the existing `exit provider_failed` line in the same block. No new `logger.info("[DEBUG] …")`.
- **AC4 field coverage:** found carries duration, stop, tokens (real `inputtotal` / `inputcached` / `cache_creation_tokens` / `outputtotal` keys, `n/a` never silent `0`, `emit_llm_call_debug` vocabulary), and failure_class; recorded carries the non-empty error, error_state applied-or-`held`, and batch_released.
- **AC3 ordering:** transition before release keeps `batch_id` in the `state_history` entry (`tracker.py:671`), and the existing `provider call failed batch_id=… error=…` ERROR line still fires before `log_batch_id` is cleared.
- **Boundaries:** single core file, no `src/external/**`, no `src/data/**`, no UI, no `run_next` / graduation-map / `TASK_CONFIG` `error_state` edits. `provider_failed=True` is set on the one provider-return call site only, so envelope / validation / decode failures keep today's hard-string behavior.
- **Self-assessment:** `Single-Component` / `high` / `Medium` remain honest — Risk `Medium` names hard-fail breadth, contained by the `provider_failed` flag plus the explicit balance hold (`is_provider_balance_refusal` matches `failure_class == "provider_balance_refusal"`, `llm_external.py:29-33`).

No `fix-now` outstanding. Plan Discuss closes at 2 completed rounds with the plan faithful to the definition. → **Plan Approved.**

context_tokens≈78000

— Joan

#### katherine — 2026-08-06T00:04:36.928Z
[plan-discuss] round=2 reply

Patched plan on `origin/sub/AST-1164/AST-1191-artifact-hop-failure-release-debug` @ `ec8971de`.

**Delta vs round=2 concern:**

1. **fix-now (`_close_hop_ledger` early exit → `None`):** Stage 1 step 7 now spells the full body. The `hop_ledger_closed or not hop_ledger_batch_id` path is `return outcome`, never a bare `return`. Done-when + Decision restate every-exit return discipline (same as `_HOP_FAILURE_NOOP` on the sibling helper).

2. **Belt-and-braces:** Stage 2 step 2 normalizes `hop_fail_outcome = hop_fail_outcome or _HOP_FAILURE_NOOP` before any key access, so a missed bare return cannot `TypeError` out of `do_task` and skip consult’s claim release.

Round=1 items left closed (timesheet keys / signature for `_apply_dispatch_chain_hop_failure`).

Plan: [ast-1191-artifact-hop-failure-release-debug-trail.md](https://github.com/susansomerset/astral/blob/sub/AST-1164/AST-1191-artifact-hop-failure-release-debug/docs/features/artifacts/ast-1191-artifact-hop-failure-release-debug-trail.md)

**Scope / Conf / Risk:** unchanged (`Single-Component` / `high` / `Medium`).

#### joan — 2026-08-06T00:03:23.196Z
[plan-discuss] round=2 concern
[plan-rubric] revision=1

**Rubric:** plan-rubric.v1
**Ticket:** AST-1191
**Overall:** REVISE
**Publish ref tip:** `origin/sub/AST-1164/AST-1191-artifact-hop-failure-release-debug` @ `177caa81`

## Traceability

AC3→S1 (error_state transition then claim release, ordered so `state_history` keeps `batch_id`; existing `provider call failed batch_id=… error=…` ERROR line retained and still emitted before `log_batch_id` is cleared); AC4→S2 (found/recorded under `debug=True`) — **AC4 blocked by finding 1**. Parent AC1/AC2/AC5 are N/A–boundary for this child (Ada AST-1189 / Hedy AST-1190). No orphan stages.

**Considered:** full active corpus re-swept (65 leaves — 18 universal + 30 scoped considered, 17 scoped excluded on layer/path predicates). Files Changed is unchanged from revision 0 (`src/core/agent.py`, modify, core), so the considered/excluded sets are identical and all considered statutes still score `conforms`. Finding 1 is an R6 completeness gap, load-bearing because `orch.pipeline.plan-is-bible` means the stage text gets executed as written. Recorded in-session per R7.

## Findings

**1. `fix-now` — Stage 1 step 7 leaves `_close_hop_ledger` returning `None` on its early exit, and Stage 2 subscripts that return unconditionally.**

Stage 1 step 7 says: set `outcome`, "then run the existing hop-ledger finalize / `clear_log` logic unchanged", then `return outcome`. The existing logic contains a bare early return (`src/core/agent.py:2204` on the epic ftr ref):

```python
if hop_ledger_closed or not hop_ledger_batch_id:
    return
```

Left "unchanged", that path returns `None`. Stage 2 step 2 then does `hop_fail_outcome["apply_error_state"]` / `hop_fail_outcome["error_state"]` with no guard, so a debug-gated provider failure on that path raises `TypeError: 'NoneType' object is not subscriptable` inside `do_task`.

The early exit is the **common** case, not an edge: `hop_ledger_batch_id` is only assigned when `in_chain and candidate_id` (`agent.py:2118-2126`). So it is `None` for

- every non-chain `do_task` call — all consult / roster / gazer provider failures under `debug=True`, which is squarely `astral.standards.no-cross-contamination` territory since none of those paths are this ticket's business; and
- dispatch-chain hops whose company row carries no `candidate_id` — the branch that already logs `run_next chain hop without astral_candidate_id — no hop ledger` (`agent.py:2122-2125`).

That second case reproduces the epic's own bug. `_run_dispatch_chain_job_batch` awaits `do_task` with no `try` around it (`src/core/consult.py:2280`) and releases the claim only on the `not result.get("success")` line after it (`consult.py:2286-2287`). An exception out of `do_task` skips that release and aborts the batch loop — the job stays batch-claimed in `BUILD_ARTIFACTS`, which is exactly the state AC3 exists to prevent, now reachable through the debug trail AC4 adds.

This is the same defect class as round=1 finding 2, which was fixed for `_apply_dispatch_chain_hop_failure` (`_HOP_FAILURE_NOOP` returned from **every** exit) but not carried across to `_close_hop_ledger`.

**Recommendation:** state in Stage 1 step 7 that `_close_hop_ledger` returns `outcome` from **every** exit including the `hop_ledger_closed or not hop_ledger_batch_id` early return (mirroring the `_HOP_FAILURE_NOOP` treatment the sibling helper already got), and — belt and braces, since Stage 2 is a separate commit — have Stage 2 read `(hop_fail_outcome or _HOP_FAILURE_NOOP)`. Either alone closes the crash; the first is the one the plan is missing.

**2. `acceptable`** — `_ts_num` uses `isinstance(v, (int, float))`, which admits `bool`. No external path puts a bool in those keys today, so this is a note, not a change request.

## Round=1 items — verified resolved

- **fix-now (timesheet keys / silent zeros): closed.** Stage 2 now names `inputtotal` / `inputcached` / `outputtotal` / `cache_creation_tokens`, which is what both clients emit on the success dict (`deepseek.py:293-294`) and on `_empty_timesheet` (`deepseek.py:206-209`), Anthropic mirrored. Missing → `n/a`, no silent `0`, so a future rename surfaces instead of reprinting the parent's `tokens in=0 out=0` symptom. The `fresh` / `cache_read` / `cache_write` / `output` mapping is field-for-field identical to `emit_llm_call_debug` (`src/utils/llm_external.py:76-79`, whose `input_total` is the same value stored as `inputtotal`), so operators read one vocabulary across the external and core lines. max_tokens and hollow-response paths keep their real counts.
- **discuss (signature contradiction): closed for `_apply_dispatch_chain_hop_failure`.** Both helpers are declared `-> Dict[str, Any]` in Stage 1, the no-op constant covers the `_should_write_dispatch_hop_label` early return, and Stage 2 only consumes. `_apply_dispatch_chain_hop_failure` has exactly one caller (`agent.py:2196`), so the return-type change is contained. Finding 1 is the one remaining hole in that same fix.
- **acceptable (dual release): confirmed harmless, and re-verified this pass.** `_run_dispatch_chain_job_batch`'s failure branch releases the claim and does **not** transition state (`consult.py:2286-2287`), so the new `ERROR_BUILD_ARTIFACTS` transition cannot collide with a competing consult transition or trip `prior_states`. Dual clear stays idempotent through `clear_job_batch_lock`.

Everything else from round=1 still holds: `ERROR_BUILD_ARTIFACTS` accepts runtime hop labels because `_job_state_matches_prior` normalizes them (`tracker.py:603-615`); transition-before-release is what makes AC3's `batch_id` visibility true (`tracker.py:671`); `_empty_timesheet` supplies a real `duration` even when `api_response` is `None`; `is_provider_balance_refusal` matches `failure_class == "provider_balance_refusal"` on a one-key dict (`llm_external.py:29-33`), so the balance-hold branch works as written. Scope, Conf `high`, and Risk `Medium` remain honest for a single-file core change.

context_tokens≈62000

— Joan

#### katherine — 2026-08-05T23:58:47.637Z
[plan-discuss] round=1 reply

Patched plan on `origin/sub/AST-1164/AST-1191-artifact-hop-failure-release-debug` @ `177caa81`.

**Delta vs round=1 concern:**

1. **fix-now (timesheet keys / silent zeros):** Stage 2 now reads the real external keys (`inputtotal`, `inputcached`, `outputtotal`, `cache_creation_tokens`). Missing keys render as `n/a`, never a silent `0`. Found line uses the same `tokens fresh=… cache_read=… cache_write=… output=…` vocabulary as `emit_llm_call_debug`.

2. **discuss (signature contradiction):** Stage 1 now has both `_apply_dispatch_chain_hop_failure` and `_close_hop_ledger` return `{"apply_error_state", "error_state", "batch_released"}` (including early no-op). Stage 2 only consumes that return — no signature rewrite across stages.

3. **acceptable (dual release):** Left as Decision — defense in depth for non-batch `do_task` callers; idempotent with consult’s existing clear.

Plan: [ast-1191-artifact-hop-failure-release-debug-trail.md](https://github.com/susansomerset/astral/blob/sub/AST-1164/AST-1191-artifact-hop-failure-release-debug/docs/features/artifacts/ast-1191-artifact-hop-failure-release-debug-trail.md)

**Scope / Conf / Risk:** unchanged (`Single-Component` / `high` / `Medium`).

#### joan — 2026-08-05T23:57:07.264Z
[plan-discuss] round=1 concern
[plan-rubric] revision=1

**Rubric:** plan-rubric.v1
**Ticket:** AST-1191
**Overall:** REVISE
**Publish ref tip:** `origin/sub/AST-1164/AST-1191-artifact-hop-failure-release-debug` @ `de6893a4`

## Traceability

AC3→S1 (error_state transition + claim release, ordered so `state_history` keeps `batch_id`; existing `provider call failed batch_id=… error=…` ERROR line retained); AC4→S2 (found/recorded under `debug=True`) — **AC4 partially unmet, see finding 1** (the tokens field is specified against keys that do not exist). Parent AC1/AC2/AC5 are N/A–boundary for this child (Ada AST-1189 / Hedy AST-1190). No orphan stages.

**Considered:** full active corpus swept (65 leaves — 18 universal + 30 scoped considered, 17 scoped excluded on layer/path predicates); all considered statutes score `conforms`. The fix-now below is R5/R6 AC fidelity, not a statute violation. Recorded in-session per R7.

## Findings

**1. `fix-now` — Stage 2 reads timesheet keys that do not exist, and its fallback prints the epic's own symptom.**

Stage 2 step 1 says: "prefer timesheet keys already used by externals (`input_tokens` / `output_tokens` / cache fields if present on `ts`); if absent, use `0`." The externals do not emit those keys. Both providers build the same dict — `src/external/deepseek.py:291-295` and `src/external/anthropic.py:312-316`, plus the failure-path `_empty_timesheet` at `deepseek.py:206-210` / `anthropic.py:236-240`:

```
{"calltime", "duration", "inputtotal", "inputcached", "outputtotal", "cache_creation_tokens"}
```

`input_tokens` / `output_tokens` are never present, so the `if absent, use 0` clause fires every time and the found line always reads `tokens_in=0 tokens_out=0`. That is the exact string the parent Purpose holds up as the mystery to be eliminated (`stop=? tokens in=0 out=0`), now printed by the very debug line AC4 adds to explain the failure. The silent-zero fallback is what makes it dangerous: nothing fails, it just quietly lies.

It is not academic on two of the failure classes Stage 1's Decision explicitly routes through this path:

- **max_tokens** (`failure_class="max_tokens"`) returns the real `timesheet` with genuine counts — `outputtotal` is by definition at the cap, and that number is the whole explanation of the failure. The found line would report zero.
- **Hollow response** (AST-1190) returns `"timesheet": timesheet` with real counts and `api_response: response` (`deepseek.py:330-337`), so any non-zero usage behind an unusable payload would also be reported as zero.

Timeout failures do carry genuine zeros, so those stay accurate either way.

**Recommendation:** name the real keys (`inputtotal`, `inputcached`, `outputtotal`, `cache_creation_tokens`) in the plan, and drop the silent `0` default in favour of `n/a` when a key is genuinely missing — so a future rename surfaces as `n/a` instead of a plausible-looking zero. Worth mirroring the shape `emit_llm_call_debug` already uses (`tokens fresh=… cache_read=… cache_write=… output=…`, `llm_external.py:76-79`) so operators read one vocabulary across the external and core lines.

**2. `discuss` — Stage 1 and Stage 2 disagree on the `_close_hop_ledger` signature.**

Stage 1 step 6 writes it as `-> None`. Stage 2 then requires `_apply_dispatch_chain_hop_failure` to return `{"apply_error_state", "error_state", "batch_released"}` and to "thread that return value through `_close_hop_ledger`", which it cannot do while returning `None`; Stage 1's Done-when does not mention the return dict either. Under `orch.pipeline.plan-is-bible` the stages get executed as written and in order, so Stage 1 lands a signature Stage 2 has to immediately rework. Reconcile it in Stage 1 (return the dict from both helpers, including the early no-op return) or state plainly that Stage 2 amends the signature.

**3. `acceptable`** — The second claim release inside `_apply_dispatch_chain_hop_failure` is genuinely redundant with the existing one I confirmed at `src/core/consult.py:2287` (`_run_dispatch_chain_job_batch` already calls `tracker.release_job_dispatch_claim(aid)` on `not result.get("success")`). Both funnel to `database.clear_job_batch_lock`, so the dual clear is idempotent exactly as the plan claims, and keeping it means `do_task` callers outside that batch runner also release. Flagging only so the redundancy is a recorded decision rather than something Radia rediscovers.

**4. `acceptable`** — The hard-string gate (`"Job not found"` / `"Missing candidate_data"`) survives as literal substring matching. That is pre-existing and `astral.standards.in-scope-only` argues for leaving it alone here; noting it so nobody reads its retention as an endorsement.

## Verification notes (checks that came back clean)

Recording these so the revision and the later code review do not have to redo them:

- **Mid-chain hops can legally reach the error state.** `ERROR_BUILD_ARTIFACTS` declares `prior_states: [BUILD_ARTIFACTS]` (`config.py:2213`), which looked like it would reject a job sitting on a runtime hop label such as `BUILD_ARTIFACTS.anticipate_scan` and turn Stage 1 into a silent `ValueError` warning for every hop after the entry one. It does not: `_job_state_matches_prior` (`tracker.py:603-615`) normalizes both `parse_dispatch_hop_label` and `legacy_build_artifacts_hop` back to the base state before matching. So the transition is valid for `anticipate_scan` **and** for the sibling artifact hops the parent Functional scope names.
- **The ordering rationale is correct and load-bearing.** `transition_job_state` stamps `"batch_id": job.get("batch_id")` into the `state_history` entry (`tracker.py:671`), so transitioning before releasing the claim is what makes AC3's "failure reason visible against that `batch_id`" true rather than incidental. Keep that order.
- **`duration` survives the failure path.** `_empty_timesheet()` computes real elapsed seconds, so `ts.get("duration")` yields a true value even on the timeout path where `api_response` is `None` — the found line's duration field works as specified.
- **`is_provider_balance_refusal` is already imported** in `agent.py:39` and accepts a one-key dict, so the balance-hold branch works as written.

The diagnosis in the ticket and plan is accurate: today's `_apply_dispatch_chain_hop_failure` gates only on those two entity strings, so provider failures leave the job in `BUILD_ARTIFACTS` even though the claim is already cleared — state, not the claim, is the real gap. Scoping to `src/core/agent.py` with no consult/dispatcher edits is the right call for `astral.dispatch.run-next-is-chain-authority` and `astral.state.core-decides-transitions` (core decides, tracker executes). Self-assessment is honest, and `Risk: Medium` names the right hazard — hard-fail breadth — which the `provider_failed` flag plus explicit balance hold does contain.

context_tokens≈130000

— Joan

#### katherine — 2026-08-05T23:52:02.359Z
Plan: [ast-1191-artifact-hop-failure-release-debug-trail.md](https://github.com/susansomerset/astral/blob/sub/AST-1164/AST-1191-artifact-hop-failure-release-debug/docs/features/artifacts/ast-1191-artifact-hop-failure-release-debug-trail.md) on `origin/sub/AST-1164/AST-1191-artifact-hop-failure-release-debug` @ `de6893a4`.

**Scope:** `Single-Component` — only `src/core/agent.py` (dispatch-chain hop failure + debug); consumes sibling `error` / `failure_class` / `timesheet` without touching externals.

**Conf:** `high` — today’s `_apply_dispatch_chain_hop_failure` only hard-fails on missing job/candidate strings, so provider failures leave jobs in `BUILD_ARTIFACTS` after claim clear; extending that helper + provider-path `_close_hop_ledger` kwargs is the direct fix.

**Risk:** `Medium` — wrong hard-fail breadth could send balance-refusal or non-provider validation failures to `ERROR_BUILD_ARTIFACTS`; mitigated by `provider_failed=True` only on the provider return path and explicit balance hold.

---

# Artifact hop failure release + debug trail (anticipate_scan jobs failing)

**Linear:** [AST-1191](https://linear.app/astralcareermatch/issue/AST-1191/artifact-hop-failure-release-debug-trail-anticipate-scan-jobs-failing)  
**Parent:** [AST-1164 — anticipate_scan jobs failing](https://linear.app/astralcareermatch/issue/AST-1164/anticipate-scan-jobs-failing)  
**Publish ref:** `origin/sub/AST-1164/AST-1191-artifact-hop-failure-release-debug`

After AST-1189 (timeout `failure_class`) and AST-1190 (hollow/blank-error surfacing): when a provider call fails on `anticipate_scan` or any shared resume-artifact dispatch-chain hop, the job must leave the batch claim, land on the configured artifact error/hold state (`TASK_CONFIG[*].error_state` → `ERROR_BUILD_ARTIFACTS`), keep the non-empty failure reason visible against that `batch_id` in app_log / Execution History, and — when `debug=True` — emit AST-538 found/recorded detail for duration, stop, tokens, and error/failure class. Does **not** redesign LLM adapters beyond consuming their structured `error` / `failure_class` / `timesheet` returns.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/agent.py` | Expand `_apply_dispatch_chain_hop_failure` for provider failures (error_state + claim release); wire provider-failed `_close_hop_ledger` with `failure_class`; add debug found/recorded lines on that path | core |

**Not in scope:** `src/external/{deepseek,anthropic}.py` / timeout budget (AST-1189); hollow-response classification (AST-1190); `run_next` / BUILD_ARTIFACTS hop topology; AST-1163 name/ANALYSIS tokens; UI; `src/data/**`.

---

## Stage 1: Provider failure → error_state + batch claim release

**Done when:** On a dispatch-chain job hop (`ctx.dispatch_trigger_state` set, graduation target exists) whose provider call returns `success=False`, the job (1) transitions to `task_config["error_state"]` when that state is configured (for artifact hops: `ERROR_BUILD_ARTIFACTS`), (2) has its `batch_id` lock cleared, and (3) still emits the existing `do_task(...) provider call failed batch_id=… error=…` ERROR line with the non-empty error from AST-1190. Provider balance refusal (`failure_class=provider_balance_refusal`) still **holds** state (no error_state transition) but **does** release the claim. Non-provider hop failures keep today’s hard-string gate (`Job not found` / `Missing candidate_data` only). Both `_apply_dispatch_chain_hop_failure` and `_close_hop_ledger` return the outcome dict `{"apply_error_state": bool, "error_state": str, "batch_released": bool}` from **every** exit — including `_close_hop_ledger`’s `hop_ledger_closed or not hop_ledger_batch_id` path (never bare `return` / `None`). Stage 2 consumes that dict — no signature rewrite later.

1. In `src/core/agent.py`, add a module-level no-op outcome constant (near the hop-failure helper) and extend `_apply_dispatch_chain_hop_failure` to return that outcome dict from **every** exit:

```python
_HOP_FAILURE_NOOP = {
    "apply_error_state": False,
    "error_state": "",
    "batch_released": False,
}

def _apply_dispatch_chain_hop_failure(
    *,
    entity_type: str,
    index: Optional[str],
    ctx: Optional[Dict[str, Any]],
    task_config: Dict[str, Any],
    error: str,
    debug: bool,
    provider_failed: bool = False,
    failure_class: Optional[str] = None,
) -> Dict[str, Any]:
```

2. When `_should_write_dispatch_hop_label(...)` is false (not a dispatch-chain job hop — no state/claim side effects): `return dict(_HOP_FAILURE_NOOP)`.

3. Replace the hard-fail gate so error_state applies when `err_state` is non-empty **and** any of:
   - existing hard strings: `"Job not found" in error` or `"Missing candidate_data" in error`
   - `provider_failed is True` **and** not balance refusal — call the existing `is_provider_balance_refusal({"failure_class": failure_class})` already imported in this module

   Concrete:

```python
err_state = (task_config.get("error_state") or "").strip()
balance_hold = provider_failed and is_provider_balance_refusal(
    {"failure_class": failure_class}
)
hard = bool(err_state) and (
    "Job not found" in error
    or "Missing candidate_data" in error
    or (provider_failed and not balance_hold)
)
apply_error_state = False
batch_released = False
```

4. When `hard and err_state and index`:
   - `tracker_mod.transition_job_state([index], err_state)` inside the existing `try/except ValueError` (warning log unchanged).
   - On successful transition (no `ValueError`): set `apply_error_state = True`.
   - **Order:** transition **before** claim release so `state_history[].batch_id` still captures the in-flight claim (`transition_job_state` reads `job.get("batch_id")`).

5. When `provider_failed and index` (including balance_hold): call `tracker_mod.release_job_dispatch_claim(index)` after the transition attempt (or immediately when not hard); set `batch_released = True`. Idempotent with `_run_dispatch_chain_job_batch`’s existing `release_job_dispatch_claim` on `!success` — leave that consult release in place; do not remove it.

6. Before returning, when `debug=True`, emit (replace the current single `chain_hop_failed retryable=…` line):

```text
chain_hop_failed apply_error_state=<bool> error_state=<err_state or ''> batch_released=<bool> failure_class=<…> error=<…>
```

   Then always:

```python
return {
    "apply_error_state": apply_error_state,
    "error_state": err_state if apply_error_state else "",
    "batch_released": batch_released,
}
```

7. Update `_close_hop_ledger` to accept the new kwargs **and return the same outcome dict**:

```python
def _close_hop_ledger(
    *,
    success: bool,
    clear_log: bool = False,
    failure_error: Optional[str] = None,
    provider_failed: bool = False,
    failure_class: Optional[str] = None,
) -> Dict[str, Any]:
```

   - Replace the body so **every** exit returns a dict (including the existing early exit). Concrete body:

```python
nonlocal hop_ledger_closed
if not success and failure_error:
    outcome = _apply_dispatch_chain_hop_failure(
        entity_type=entity_type or "",
        index=index,
        ctx=ctx,
        task_config=task_config,
        error=failure_error,
        debug=debug,
        provider_failed=provider_failed,
        failure_class=failure_class,
    )
else:
    outcome = dict(_HOP_FAILURE_NOOP)
# Existing early exit — MUST return outcome, not bare `return` / None
# (hop_ledger_batch_id is None for non-chain calls and chain hops without candidate_id).
if hop_ledger_closed or not hop_ledger_batch_id:
    return outcome
_finalize_run_next_hop_ledger(
    hop_ledger_batch_id, success=success, batch_size=batch_size
)
hop_ledger_closed = True
if clear_log:
    log_batch_id.set(None)
return outcome
```

   - Other call sites that ignore the return value stay valid (Python allows discarding returns).
   - **Do not** leave the bare `return` at today’s `agent.py` early-exit line — that is the round=2 crash: Stage 2 would subscript `None`, abort `do_task`, and skip consult’s claim release (AC3 regress under `debug=True`).

8. On the existing provider-failure return path in `do_task` (the block after `send_to_*` where `batch_id and not result.get("success")` already normalizes `error`, and the later `if not result.get("success"):` that calls `_close_hop_ledger`):

   - Change the `_close_hop_ledger` call to capture the outcome (Stage 2 recorded line uses it):

```python
hop_fail_outcome = _close_hop_ledger(
    success=False,
    clear_log=True,
    failure_error=str(result.get("error") or "provider_failed"),
    provider_failed=True,
    failure_class=(
        str(result.get("failure_class")).strip()
        if result.get("failure_class") is not None
        else None
    ) or None,
)
```

   - Do **not** set `provider_failed=True` on other `_close_hop_ledger(success=False, …)` call sites (envelope / validation / decode failures keep the hard-string-only behavior).

⚠️ **Decision:** Apply configured `error_state` for **all** non-balance provider failures on dispatch-chain hops (timeout, empty response, max_tokens, generic provider error), not only AST-1189/1190 classes — AC3 names “such a failure” after the provider path; balance refusal keeps the existing hold semantics used elsewhere in consult.  
⚠️ **Decision:** Claim release lives in `_apply_dispatch_chain_hop_failure` (defense in depth for `do_task` callers outside `_run_dispatch_chain_job_batch`) **and** remains in that consult batch runner — dual clear is idempotent via `clear_job_batch_lock` (Joan #3: recorded, not accidental).  
⚠️ **Decision:** No consult.py / dispatcher.py edits — topology and claim/get/clear finally block stay as-is (`astral.dispatch.run-next-is-chain-authority`).  
⚠️ **Decision:** Outcome-dict return lands in Stage 1 for both helpers so Stage 2 does not amend signatures (`orch.pipeline.plan-is-bible`). `_close_hop_ledger` returns `outcome` from **every** exit (including no-ledger early return) — same discipline as `_HOP_FAILURE_NOOP` on `_apply_dispatch_chain_hop_failure`.

---

## Stage 2: Debug found/recorded trail on provider failure

**Done when:** With `debug=True`, a provider-failed `do_task` on an artifact hop emits Style D index detail under the existing hop/provider-failed path with **found** (duration, stop, token counts from real timesheet keys, failure_class) and **recorded** (non-empty error string, error_state applied or held, batch_released) lines. With `debug=False`, no new contract lines. No changes to external `send_to_*` beyond consuming fields already on `result`. Silent `tokens_*=0` fallbacks are forbidden when keys are missing.

1. In the same `if not result.get("success"):` provider-failure block in `do_task`, **after** `_store_response_block` (best-effort), when `debug` is True:

   - Read timesheet: `ts = result.get("timesheet") if isinstance(result.get("timesheet"), dict) else {}`
   - Duration: if `ts.get("duration")` is `int` or `float`, format `duration={float(ts["duration"]):.1f}s`; else `duration=n/a`.
   - Stop: `api = result.get("api_response")`; `stop = getattr(api, "stop_reason", None) if api is not None else None`; display `stop` if it is a non-empty string after strip, else `"?"`.
   - Tokens — use the **actual** external timesheet keys (both DeepSeek and Anthropic): `inputtotal`, `inputcached`, `outputtotal`, `cache_creation_tokens`. Helper for display (inline or small local lambda is fine):

```python
def _ts_num(key: str) -> str:
    v = ts.get(key)
    return str(int(v)) if isinstance(v, (int, float)) else "n/a"
```

     Do **not** invent `input_tokens` / `output_tokens`. Do **not** default missing keys to `0` — missing → `n/a` (timeout `_empty_timesheet` still supplies real zeros as ints, which print as `0` honestly).
   - `fc = result.get("failure_class")`; display `str(fc)` if non-empty after strip, else `n/a`.
   - Emit **found** line before `_close_hop_ledger`, matching `emit_llm_call_debug` vocabulary (`llm_external.py` token line: fresh / cache_read / cache_write / output):

```text
found duration=<…> stop=<…> tokens fresh=<inputtotal> cache_read=<inputcached> cache_write=<cache_creation_tokens> output=<outputtotal> failure_class=<…>
```

2. Call `_close_hop_ledger` as in Stage 1 step 8, then normalize before any subscript (belt-and-braces if Stage 1’s every-exit return is missed):

```python
hop_fail_outcome = _close_hop_ledger(...)  # same kwargs as Stage 1 step 8
hop_fail_outcome = hop_fail_outcome or _HOP_FAILURE_NOOP
```

   Then when `debug` is True, emit **recorded** from the normalized dict:

```text
recorded error=<non-empty error> error_state=<applied state or 'held'> batch_released=<true|false>
```

   - `error_state` display: `hop_fail_outcome["error_state"]` when `hop_fail_outcome["apply_error_state"]` else `'held'`.
   - `batch_released`: lowercase `true` / `false` from the bool.

3. Keep the existing debug_detail lines (`exit provider_failed…`, balance/empty class lines from AST-1190). Add found/recorded; do not delete sibling lines.

4. Do **not** edit `emit_llm_call_debug` in `llm_external.py` or either external client — ticket boundary is consume structured failures in core.

⚠️ **Decision:** Found/recorded lives in `do_task` (core), not a second pass through external debug helpers — honors “does not redesign LLM adapters” and still satisfies §1.5.1 (gated, `debug_detail`, found + recorded).  
⚠️ **Decision:** Token field names and `n/a`-not-silent-zero match Joan round=1 fix-now — operators see the same fresh/cache_read/cache_write/output vocabulary as `emit_llm_call_debug`, and max_tokens / hollow paths keep real counts.

---

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; publish each to `origin/sub/AST-1164/AST-1191-artifact-hop-failure-release-debug`.
- Do not add files outside the Files Changed table.
- If `_apply_dispatch_chain_hop_failure` / `_close_hop_ledger` / provider-failure block shape has drifted, stop and comment on **AST-1164** with the Stage N blocked template.
- Healthy provider success path unchanged (parent AC5 — owned by siblings; this ticket must not regress graduation / hop labels).
- Do not change `run_next` membership, `DISPATCH_CHAIN_TERMINAL_GRADUATION`, or TASK_CONFIG `error_state` strings (already `ERROR_BUILD_ARTIFACTS`).

---

## Self-Assessment

**Scope:** `Single-Component` — `src/core/agent.py` dispatch-chain hop failure + debug only; consumes sibling `failure_class` / `error` / `timesheet` without touching externals.

**Conf:** `high` — the gap is localized: today’s `_apply_dispatch_chain_hop_failure` only hard-fails on two missing-entity strings, so provider failures leave jobs in `BUILD_ARTIFACTS` while consult only clears the claim; extending that helper + provider-path `_close_hop_ledger` kwargs is the direct fix.

**Risk:** `Medium` — wrong hard-fail breadth could send balance-refusal or non-provider validation failures to `ERROR_BUILD_ARTIFACTS`; mitigated by `provider_failed` flag only on the provider return path and explicit balance hold.

---

## Code rules check

| Rule | Plan alignment |
|------|----------------|
| §1.3 DRY | One failure helper owns error_state + release; debug found/recorded once on the provider path |
| §1.5.1 debug-contract-gated | New found/recorded only when `debug=True`; `debug_detail` under existing hop context |
| §2.2 / do-task-delegation | Core consumes structured provider result; no adapter redesign |
| §2.4 claim-process-release | Transition then release; dual clear with consult is idempotent |
| §2.6 / run-next-is-chain-authority | No hop topology / graduation map edits |
| §3.3 imports | Core ← utils (`is_provider_balance_refusal` already present); no new upward imports |
| in-scope-only | No AST-1189 budget, AST-1190 hollow predicate, AST-1163 tokens, UI, data layer |

---

## Revisions

Revision 1 — 2026-08-05  
Driven by: Joan `[plan-discuss] round=1 concern` (plan-rubric.v1 REVISE) — Stage 2 timesheet keys wrong (`input_tokens`/`output_tokens` never emitted; silent `0` fallback reprints the parent symptom); Stage 1 `_close_hop_ledger` → `None` vs Stage 2 return-dict threading contradiction.  
Changes:
- Stage 1: both helpers return `{"apply_error_state", "error_state", "batch_released"}` from the start (including early no-op); Done-when + Decision document that Stage 2 does not amend signatures; dual claim-release recorded as intentional defense-in-depth.
- Stage 2: read real keys `inputtotal` / `inputcached` / `outputtotal` / `cache_creation_tokens`; missing → `n/a` (never silent `0`); found line mirrors `emit_llm_call_debug` token vocabulary (`fresh` / `cache_read` / `cache_write` / `output`); recorded line consumes Stage 1 `hop_fail_outcome`.

Revision 2 — 2026-08-06  
Driven by: Joan `[plan-discuss] round=2 concern` (plan-rubric.v1 REVISE) — Stage 1 step 7 left `_close_hop_ledger`’s existing `if hop_ledger_closed or not hop_ledger_batch_id: return` as a bare `return` (`None`); Stage 2 subscripted that unconditionally → `TypeError` under `debug=True`, skipping consult claim release (AC3 regress).  
Changes:
- Stage 1 step 7: full concrete body; early no-ledger exit `return outcome` (never bare `return`); Decision restates every-exit return discipline for `_close_hop_ledger`.
- Stage 2 step 2: `hop_fail_outcome = hop_fail_outcome or _HOP_FAILURE_NOOP` before any key access.

---

## Review (build stub)

**Publish ref:** `origin/sub/AST-1164/AST-1191-artifact-hop-failure-release-debug`  
**Tip:** `3aa816f3`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `7f5b132e` | hop failure → `ERROR_BUILD_ARTIFACTS` + claim release; outcome dict every exit |
| 2 | `3aa816f3` | found/recorded duration/stop/tokens/failure_class on provider fail |

---

## Radia review — code-rubric.v1 revision=1

**Publish ref tip:** `5c6cdcda`

**Overall:** CLEAN

### Plan adherence

Isolated this ticket's own contribution via `git diff ee5e760f..5c6cdcda` (the tip AST-1189 left for merge-child) rather than the full three-dot `origin/dev` diff, since the latter also carries already-reviewed AST-1189/AST-1190 product code stacked via `ftr`. AST-1191's own footprint is exactly `src/core/agent.py` (105 lines) + its plan doc + test-bible + tests — matching the Files Changed table with no scope creep. Both Joan revision rounds are honored: `_apply_dispatch_chain_hop_failure` and `_close_hop_ledger` return the outcome dict from **every** exit (including the no-op / no-ledger early returns — no bare `return None` regression), balance-refusal still holds state while releasing the claim, transition happens before release (state_history still stamps the in-flight `batch_id`), and Stage 2's found/recorded lines read the real timesheet keys (`inputtotal`/`inputcached`/`outputtotal`/`cache_creation_tokens`) with honest `n/a` on missing keys — no silent-zero regression of the parent symptom.

Verified `clear_job_batch_lock` (`src/data/database.py`) is a plain `UPDATE ... SET batch_id = NULL` — confirms the plan's "dual clear is idempotent" claim for the intentional double release (`_apply_dispatch_chain_hop_failure` + the existing consult batch runner clear).

Ran the ticket's own test class plus the adjacent `TestAst848DispatchChainDoTask` regression test in a fresh venv: **11/11 pass**. The broader touched-file test run surfaces ~30 pre-existing failures (statute-count fixture drift, shared sqlite db schema state, and unrelated in-flight epics AST-901/1054/1060/1127/1195 whose product code isn't on this branch) — none in `TestAst1191*` or `TestAst848*`, confirmed against an `origin/dev` baseline showing the same classes of failure already present. Not diff-caused.

### Findings

None (fix-now / discuss). No repeat of AST-1189's cross-ticket merge-tests contamination — this branch's `merge-tests(AST-1191)` diff is a clean, isolated 2-file/240-line addition (own test-bible + test file only).

### Pattern conformance

None cited (plan lists statute ids under In-scope / Considered-but-excluded, covered by the full-set sweep).

### Frame diff

(none) — diff matches the plan's Files Changed table exactly; no unplanned adds.

### What's solid

- `_apply_dispatch_chain_hop_failure` / `_close_hop_ledger` outcome-dict threading is correct on every exit path (verified against both Joan revision concerns).
- Debug found/recorded gating is correct — `found` sits inside the existing `if debug:` block, `recorded` is gated separately after `_close_hop_ledger`, and `debug=False` emits neither (test-covered).
- `astral.batch.claim-process-release`, `astral.state.core-decides-transitions`, `astral.state.job-prior-states-enforced` all conform — transition-then-release ordering, `ValueError` enforcement preserved via existing try/except, core (not data) decides `err_state`.

`context_tokens≈52000`
— Radia

---

## Resolution

**Date:** 2026-08-06  
**Driven by:** Radia `[code-rubric] revision=1` — **CLEAN** (no fix-now / discuss).  
**Review tip ingested:** `d8864b7a` (`docs(AST-1191): Radia review — clean`)

| Finding | Action |
|---------|--------|
| None | Accepted — no product change this pass |

**§9a:** dry-run `origin/sub/AST-1164/AST-1191-artifact-hop-failure-release-debug` → `origin/dev` (+ ftr when present).
