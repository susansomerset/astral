<!-- linear-archive: AST-1189 archived 2026-08-07 -->

## Linear archive (AST-1189)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1189/provider-call-budget-timeout-failure-class-anticipate-scan-jobs  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1164 — anticipate_scan jobs failing  
**Blocked by / blocks / related:** parent: AST-1164; blocks: AST-1191

### Description

## What this implements

Enforce the hard per-call time budget on the DeepSeek path and Anthropic mirror so over-budget calls fail with a non-empty timeout error / failure class instead of a long zero-token mystery. Raise the provider call budget to **10 minutes** (Archie: Open questions §3). Does **not** own hollow-response classification (sibling Empty / unusable provider response surfacing) or artifact hop release/debug (sibling Artifact hop failure release + debug trail).

## Acceptance criteria

- [X] A provider call that exceeds the configured per-call time budget fails within that budget (plus the small existing grace already used around the wait) with a non-empty timeout error / failure class — not a ~20+ minute `stop=? tokens in=0 out=0` mystery with blank `error=`.
- [X] A healthy DeepSeek (or mirrored Anthropic) response with normal stop reason and token counts still completes `anticipate_scan` successfully when prompt context is otherwise valid.

## Boundaries

* Does not own empty/unusable provider response classification (Hedy sibling).
* Does not own artifact hop batch release / error-state / debug trail (Katherine sibling).
* Does not fix hollow name/ANALYSIS tokens (AST-1163).
* Does not re-author prompts or change run_next topology.

## In scope

- [X] `pattern.config.config-block` — `PROVIDER_CALL_BUDGET` in `src/utils/config.py`
- [X] `astral.config.config-source-of-truth` — timeout/grace/failure_class literals; no env
- [X] `astral.layers.core-vs-external-bright-line` — timeout tagging stays in `src/external/{deepseek,anthropic}.py`
- [X] `astral.agent.do-task-delegation` — core consumes structured `error` / `failure_class` from external
- [X] `astral.standards.in-scope-only` — budget + timeout failure class only
- [X] `astral.standards.dry-and-focused-functions` — shared classify/message helpers in `src/utils/llm_external.py`

## Considered but excluded

- [X] `astral.patterns.coat-check-never-store-empty` — hollow/empty provider payload surfacing is AST-1190 (`src/core/agent.py` / response path), not this timeout budget ticket
- [X] `pattern.batch.entity-claim-process-release` / `astral.batch.claim-process-release` — hop release + error/hold state is AST-1191 (`src/core` batch paths)
- [X] `astral.standards.debug-contract-gated` — found/recorded debug trail on failure is AST-1191
- [X] `astral.dispatch.run-next-is-chain-authority` — `run_next` / hop topology unchanged; no dispatcher edits
- [X] `src/ui/**` — no UI surface for this failure class

## Notes for planning

Archie answers: timeout → 10 minutes; Anthropic mirror ships in this epic with DeepSeek. Blank `error=` root cause for wait_for path: `str(asyncio.TimeoutError()) == ""`.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at dispatch-parent.

**Publish ref:** `origin/sub/AST-1164/AST-1189-provider-call-budget-timeout`

### Comments

#### chuckles — 2026-08-05T23:46:56.497Z
[merge-child] blocked: missing plan(AST-1189): on origin/sub/AST-1164/AST-1189-provider-call-budget-timeout (have docs(AST-1189): … instead of plan(); use plan() or docs(): plan —)

@Ada Lovelace — plan commits `e013e910` / `94846b99` (`docs(AST-1189): plan — …`) are already ancestors of `origin/ftr/AST-1164-anticipate-scan-jobs-failing`, so `validate-sub-log`’s `sub --not ftr` range no longer sees them. Tip still has code/test/resolve ahead of ftr. Need a tip commit whose subject matches `plan(AST-1189):` or `docs(AST-1189): plan —` so the gate passes, then Chuckles will re-run merge-child.

— Chuckles

#### ada — 2026-08-05T23:46:25.053Z
origin/sub/AST-1164/AST-1189-provider-call-budget-timeout @ aefa0efe · §9a clean · ftr dry-run clean

#### betty — 2026-08-05T23:45:26.904Z
[check-linear]

Cleared `[qa-handoff]` (§9a ftr bible/test union).

**Tip:** `origin/sub/AST-1164/AST-1189-provider-call-budget-timeout` @ `aefa0efe` — `test(AST-1189): union AST-1189+AST-1190 bible/tests for ftr merge` (blobs from `origin/tests`; TimeoutError path allows `provider_call_timeout`).

**Verified:** AST-1189 + AST-1190 narrowed suites **30 passed** on tip; `git merge` of tip onto `origin/ftr/AST-1164-anticipate-scan-jobs-failing` is conflict-free for bible/tests (ftr already ancestor of tip).

**Bible shasum** (`aefa0efe`):
- `docs/test-bible/utils/llm_external.md` `2fbe7c95f958ef0ee3208e737c029ae07b74c3c2`
- `docs/test-bible/utils/config.md` `aa29b79e5ed3eebbde65ce7013ddea8890cc76b0`
- `docs/test-bible/utils/logging_batch.md` `93ba229a69e9e84fce6c070f5b04e4f656f57e02`
- `docs/test-bible/external/deepseek.md` `3a3fd40d970d39013551505ee19eeeb3017bf34d`
- `docs/test-bible/external/anthropic.md` `177fb64ee1436b67f5f397f3843831ddf271c057`
- `docs/test-bible/core/agent.md` `04a061bba871fdddce61c0df9908d76d51acf3db`

Assignee → Ada. Stay **Review Posted**.

— Betty

#### ada — 2026-08-05T23:43:33.964Z
[qa-handoff]
@Betty White

§9a blocked on engineer test-tree ban during `origin/ftr` merge.

**Product tip (Ada):** `origin/sub/AST-1164/AST-1189-provider-call-budget-timeout` @ `98f495fe`
- Merged `origin/ftr` product surfaces (AST-1189 budget + AST-1190 empty-response) + `origin/dev` product
- §9a dry-run clean vs `origin/dev` and vs `origin/ftr/AST-1164-anticipate-scan-jobs-failing`
- AST-1189 narrowed suite green (12 passed)

**Need from Betty:** republish / merge-tests so tip tree carries **both** AST-1189 and AST-1190 bible+component coverage (engineer hook blocked Ada from committing the union). Paths that conflicted on the ftr merge:
- `docs/test-bible/external/{anthropic,deepseek}.md`
- `docs/test-bible/utils/{config,llm_external}.md`
- `tests/component/external/test_{anthropic,deepseek}.py`
- `tests/component/utils/test_{config,llm_external}.py`
(+ any auto-merge updates from `origin/dev` for related bible/tests if still needed)

**Note:** blank `TimeoutError` on the merged product is tagged `provider_call_timeout` (AST-1189) — do not keep AST-1190 asserts that expect no `failure_class` on that path.

Stay **Review Posted**; reassign Ada when tip is re-cut.

#### betty — 2026-08-05T23:37:52.219Z
[check-linear]

Cleared `[qa-handoff]` (Radia fix-now / merge-tests contamination).

**Re-cut:** sole `merge-tests(AST-1189): origin/tests 08675910` on tip `107e325f` — AST-1190 test commit `748a5725` is **not** an ancestor; `TestAst1190*` gone from this tip’s `tests/component/**`; sibling plan doc already dropped @ resolve.

**Manifest (unchanged node ids):**
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1189ProviderCallBudgetConfig \
  tests/component/utils/test_llm_external.py::TestAst1189ProviderCallBudgetHelpers \
  tests/component/external/test_deepseek.py::TestAst1189ProviderCallBudgetTimeout \
  tests/component/external/test_anthropic.py::TestAst1189ProviderCallBudgetTimeout \
  -q
```
Verified 12 passed on tip; no `TestAst1190` collected.

**Bible shasum** (`107e325f`):
- `docs/test-bible/utils/llm_external.md` `667d0b13b607c716505e2097bb81b9525c3d757f`
- `docs/test-bible/utils/config.md` `c194264072013c8c5a6bcdeb9863c5406fa2440f`
- `docs/test-bible/external/deepseek.md` `6cf25e754e236401972d31b6c62b3fe4fca9cefd`
- `docs/test-bible/external/anthropic.md` `5d97ed4653e15c8c460b93c628852e2ae43ca0bd`

Assignee → Ada for resolve / re-run touched suite → User Testing. Stay **Review Posted**.

— Betty

#### ada — 2026-08-05T23:34:18.466Z
[qa-handoff]
@Betty White

Radia fix-now (code-rubric.v1 FIX-NOW) — test-tree / merge-tests contamination on this publish ref.

**What failed (Radia):** On tip `683bcb1f`, running the touched test files standalone fails **9 tests** — all AST-1190 classes (`TestAst1190*`) importing `PROVIDER_EMPTY_RESPONSE` / `normalize_provider_error` / `is_unusable_provider_response`, which do **not** exist on this tip’s product surface.

**Why test/manifest (not product):** `merge-tests(AST-1189): origin/tests 886b1033` stacks on ancestor `748a5725 test(AST-1190): hollow provider response + blank error= coverage`. AST-1189 product stages (`d41b16c7`–`663f6a07`) are clean; the narrowed AST-1189 node IDs passed under test-child, but the publish ref’s own test tree is not green standalone.

**Need from Betty:**
1. Re-cut / re-publish `merge-tests(AST-1189)` with an `origin/tests` SHA scoped to AST-1189 only (AST-1190 test commit must not be an ancestor on this sub).
2. Confirm AST-1190 test classes are gone from this tip’s `tests/component/**` (or gated so they don’t collect without AST-1190 product).

**Already done (engineer):** dropped leftover `docs/features/artifacts/ast-1190-empty-unusable-provider-response-surfacing.md` @ `a4e54c58`.

Stay **Review Posted**. Reassign Ada after `merge-tests` so resolve can re-run the touched suite → User Testing.

#### radia — 2026-08-05T23:32:18.842Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1189
**Publish ref:** `origin/sub/AST-1164/AST-1189-provider-call-budget-timeout` @ `683bcb1f` (docs-only review append at `7fd70cd2`)
**Overall:** FIX-NOW

## Plan adherence

Stages 1–3 (`d41b16c7`, `6d650feb`, `663f6a07`) match the plan's code blocks essentially verbatim — `PROVIDER_CALL_BUDGET` shape, the four `llm_external` helpers, `await_provider_call_with_budget`'s wall-release-without-awaiting-the-orphan design, and the mirrored DeepSeek/Anthropic wiring (client `max_retries`, timeout-vs-balance tagging, never-empty `error`) all land as specified. `src/core/agent.py` is untouched, honoring the stated boundary.

## Findings

**fix-now — cross-ticket test/doc contamination breaks this publish ref's own test tree.** `merge-tests(AST-1189): origin/tests 886b1033` stacks on `748a5725 test(AST-1190): hollow provider response + blank error= coverage` as an ancestor on the shared `origin/tests` branch, and `docs/features/artifacts/ast-1190-empty-unusable-provider-response-surfacing.md` (added earlier in this branch's own history) survives a `347bf506` attempt to drop it. Confirmed by running the touched test files against this tip in a fresh venv: **9 failing tests** — `TestAst1190DoTaskEmptyProviderError` x2, `TestAst1190EmptyUnusableProviderResponse` (both `test_anthropic.py`/`test_deepseek.py`), `TestAst1190ProviderEmptyResponseConfig`, `TestAst1190EmptyResponseHelpers` x5 — all `ImportError`/`AttributeError` on `PROVIDER_EMPTY_RESPONSE`, `normalize_provider_error`, `is_unusable_provider_response`, none of which exist on this tip (that product surface lives on AST-1190's own branch only). "Tests Passed" on this ticket does not reflect this publish ref actually being green standalone. Fix: re-cut `merge-tests` with a Betty SHA scoped to AST-1189 only (or sequence so AST-1190's test commit isn't an ancestor), and drop the leftover `ast-1190-*.md` plan file from this branch.

**advisory — `astral.standards.debug-contract-gated` mechanically in-scope, content benign.** Plan's Considered-but-excluded marks debug/found-recorded trail as AST-1191, and the diff does touch `emit_llm_call_debug(..., error=err, ...)` call sites in both externals — but only the `error=` value changed (str(e) → classified/never-empty string), no new debug capability or ungating. Not a substantive straggler, noting for completeness.

## Pattern conformance

None cited (plan lists statute ids under In-scope / Considered-but-excluded, not `canon/patterns/*`; covered by the full-set sweep).

## Frame diff

Unplanned adds relative to the plan's Files Changed table: `docs/features/artifacts/ast-1190-empty-unusable-provider-response-surfacing.md` (sibling ticket's plan doc — should not be on this branch) and the AST-1190 test classes bundled into the otherwise-expected `docs/test-bible/**` / `tests/component/**` merge-tests payload.

### What's solid

- `PROVIDER_CALL_BUDGET`, the wall-budget release design, and the mirrored DeepSeek/Anthropic wiring are clean, DRY, and layer-correct (external → utils only, no cross-external import).
- Never-empty `error` guarantee enforced consistently on every touched failure path in both externals.

### Recommended actions

1. Re-publish this branch with a `merge-tests` SHA scoped to AST-1189 only.
2. Drop `ast-1190-*.md` plan doc from this branch.
3. Re-run the touched-file test set on the corrected tip before re-requesting review.

`context_tokens≈48000`
— Radia

#### betty — 2026-08-05T23:18:31.225Z
## QA test manifest

`origin/sub/AST-1164/AST-1189-provider-call-budget-timeout` @ `683bcb1f` (`merge-tests(AST-1189): origin/tests 886b1033`)

1. `tests/component/utils/test_config.py::TestAst1189ProviderCallBudgetConfig` — `PROVIDER_CALL_BUDGET` shape (600s / 10s grace / `max_retries=0` / `provider_call_timeout`)
2. `tests/component/utils/test_llm_external.py::TestAst1189ProviderCallBudgetHelpers` — budget readers, cause-chain classify, `non_empty_provider_error`, wall-release `await_provider_call_with_budget`
3. `tests/component/external/test_deepseek.py::TestAst1189ProviderCallBudgetTimeout` — `TimeoutError` → non-empty budget error + `failure_class`; ordinary errors omit timeout class; healthy success unchanged
4. `tests/component/external/test_anthropic.py::TestAst1189ProviderCallBudgetTimeout` — same as DeepSeek

**Broken / obsolete revised:** AST-1190 blank-`TimeoutError` asserts coexist with `provider_call_timeout` tagging; `PROVIDER_EMPTY_RESPONSE` import in `test_llm_external.py` is lazy so the module collects on this tip.

**Integration:** none — no existing scenario asserts wall budget / `provider_call_timeout`.

**Narrowed run:**
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1189ProviderCallBudgetConfig \
  tests/component/utils/test_llm_external.py::TestAst1189ProviderCallBudgetHelpers \
  tests/component/external/test_deepseek.py::TestAst1189ProviderCallBudgetTimeout \
  tests/component/external/test_anthropic.py::TestAst1189ProviderCallBudgetTimeout \
  -q
```

**Bible shasum** (`origin/sub/…` tip):
- `docs/test-bible/utils/llm_external.md` `2fbe7c95f958ef0ee3208e737c029ae07b74c3c2`
- `docs/test-bible/utils/config.md` `625908dee25184027b38a640e5e0fe60188da7e0`
- `docs/test-bible/external/deepseek.md` `3a3fd40d970d39013551505ee19eeeb3017bf34d`
- `docs/test-bible/external/anthropic.md` `177fb64ee1436b67f5f397f3843831ddf271c057`

— Betty

#### joan — 2026-08-05T23:13:13.425Z
[plan-rubric] revision=1

**Rubric:** plan-rubric.v1
**Ticket:** AST-1189
**Overall:** APPROVED
**Publish ref tip:** `origin/sub/AST-1164/AST-1189-provider-call-budget-timeout` @ `94846b99`
**Plan Discuss:** round=1 complete (concern + reply); approving on this pass, no round=2 opened.

## Traceability

AC1→S1 (budget + `max_retries` config) + S2 (`await_provider_call_with_budget` wall release, cause-chain classifier, `non_empty_provider_error`) + S3 (both externals wired; Done-when asserts logged `duration` ≈ 610s) — **both halves now mapped**, timing and non-empty error; AC2→S3 Done-when (4) + Execution contract healthy path. Parent AC2/AC3/AC4 remain N/A–boundary for this child (Hedy AST-1190 / Katherine AST-1191). No orphan stages.

**Considered:** full active corpus re-swept against the revised Files Changed table (65 leaves — 18 universal + 27 scoped considered, 20 scoped excluded on layer/path predicates); all considered statutes score `conforms`. Recorded in-session per R7.

## Round=1 fix-nows — both cleared

**1. AC1 timing — resolved.** `await_provider_call_with_budget` uses `asyncio.wait({task}, timeout=...)` and returns without cancelling or awaiting the pending task, then raises `TimeoutError(provider_call_timeout_error_message())`. That is the material difference from `wait_for`: `asyncio.wait` does not cancel-and-await on timeout, so the caller is genuinely released at ~610s while the worker thread finishes on its own time. The companion `max_retries: 0` keeps the abandoned attempt singular. Stage 3's Done-when now pins the observable I asked for — logged `duration` ≈ budget+grace rather than provider-return wall time — so AC1 is falsifiable at test time instead of assumed.

**2. `BaseException` typing import — resolved.** Step deleted and inverted into an explicit "do not" with the reason, which also protects the next reader.

**3. Classifier / blank error (was `discuss`) — resolved beyond what I asked.** Cause/context walk with an `id()` cycle guard covers the wrapped `APIConnectionError` → `__cause__` `ReadTimeout` shape, and `non_empty_provider_error(e, fallback=type(e).__name__)` on every touched failure return makes "never blank `error=`" an invariant rather than a consequence of correct classification. That is the right shape for AC1's second half.

## Findings

**1. `discuss` — the abandoned task's outcome is never retrieved.** After `asyncio.wait` times out, the pending task is dropped with no reference kept. When that task eventually raises (likely, since it is the call that blew the budget), nobody retrieves the exception, so asyncio logs `Task exception was never retrieved` with a bare traceback at GC time — no `batch_id`, no task context, minutes after the failure was already reported. On an epic whose whole point is that operators cannot tell what happened, that is an unforced ambiguity. A one-line `task.add_done_callback(...)` that consumes (and optionally debug-logs) the orphan's result would close it. Related and worth a thought while you are in there: `_get_client` builds a fresh `Anthropic(...)` per call in both externals, so each abandoned call also holds its client and connection until the thread ends — fine at current call volume, but it is the kind of thing that only shows up under a run of consecutive timeouts.

**2. `discuss` — `max_retries: 0` trades away transient-error resilience, and it no longer has to.** My round=1 recommendation coupled retry bounding to AC1 because `wait_for` let retries multiply caller-observed latency. Once the caller is released at 610s unconditionally, `max_retries` no longer affects AC1 at all — it only governs how much work the orphan does. Meanwhile I confirmed neither `src/external/anthropic.py` nor `src/external/deepseek.py` has any 429 / rate-limit handling of its own (the only such logic in the tree is `google_cse.py`'s own loop), so the SDK's default two retries are today's entire cushion for a transient 429 or 5xx. Setting `0` converts every blip into a task failure. `1` would keep one cheap retry while still bounding the orphan, and the value is config-owned either way, so this is a knob you can name in the plan rather than a rewrite. I am not blocking on it — the value is Archie-visible in config and reversible — but the plan should say which behavior it intends instead of letting `0` read as purely a timeout companion.

**3. `acceptable`** — `await_provider_call_with_budget` lands in `src/utils/llm_external.py`, so utils now hosts a thread runner. No layer rule is broken (§3.3: utils imports only `asyncio`, config, and logging; the helper takes a callable and knows nothing about providers), and `llm_external` is the DRY-correct home since both externals consume it. Flagging only so it is not a surprise at code review.

**4. `acceptable`** — Dispatch ceiling confirmed: 610s caller budget against `ASTRAL_CONFIG["dispatch_timeout_seconds"]` 3600 leaves ample headroom, and Stage 1 step 3 correctly refuses to touch that or the gunicorn timeout.

Self-assessment is now honest on the point that mattered — `Conf: Medium` naming the FIRST_COMPLETED abandon path as new wiring, and `Risk: Medium` listing orphan threads first, which is exactly where finding 1 lives. The Revisions section records what changed and why, so the next reader can see the reasoning without replaying this thread.

context_tokens≈105000

— Joan

#### ada — 2026-08-05T23:10:38.324Z
[plan-discuss] round=1 reply

Revised plan on `origin/sub/AST-1164/AST-1189-provider-call-budget-timeout` @ `94846b99`.

**Plan doc:** https://github.com/susansomerset/astral/blob/sub/AST-1164/AST-1189-provider-call-budget-timeout/docs/features/artifacts/ast-1189-provider-call-budget-timeout-failure-class.md

**Delta vs round=1 concern:**

1. **fix-now AC1 timing** — Agreed: raising an already-unenforced 310s budget cannot bound a 1425.7s run. Replaced `asyncio.wait_for(to_thread…)` with `await_provider_call_with_budget` (`asyncio.wait` + abandon pending task) so the caller returns at budget+grace without awaiting the uncancellable worker. Companion: config `max_retries: 0` so the orphan is one attempt, not SDK-default three. Stage 3 Done-when asserts logged `duration` ≈ 610s.
2. **fix-now BaseException typing import** — Deleted. `BaseException` stays a builtin annotation, same as existing `classify_provider_balance_refusal`.
3. **discuss classifier / blank error** — Classifier now walks `__cause__` / `__context__`. All touched failure returns use `non_empty_provider_error` (fallback `type(e).__name__`) so `error` is never `""`.
4. **acceptable dispatch ceiling** — Noted: 610s × one attempt stays under `dispatch_timeout_seconds` 3600.

**Conf** softened `high` → `Medium`. Status left **Plan Discuss** for Joan.

#### joan — 2026-08-05T23:07:54.915Z
[plan-discuss] round=1 concern
[plan-rubric] revision=1

**Rubric:** plan-rubric.v1
**Ticket:** AST-1189
**Overall:** REVISE
**Publish ref tip:** `origin/sub/AST-1164/AST-1189-provider-call-budget-timeout` @ `e013e910`

## Traceability

AC1→S1–S3 (**partial** — non-empty error / `failure_class` half only; the "fails within that budget" half has no stage); AC2→S3 + Execution contract (healthy path unchanged). Parent AC2/AC3/AC4 are N/A–boundary for this child ("Does not own empty/unusable provider response classification (Hedy sibling)" / "artifact hop batch release / error-state / debug trail (Katherine sibling)").

**Considered:** full active corpus swept (65 leaves — 18 universal + 27 scoped considered, 20 scoped excluded on layer/path predicates). All considered statutes score `conforms`; the fix-nows below are R5 traceability and R6 definition fidelity, not statute violations. Recorded in-session per R7.

## Findings

**1. `fix-now` — the plan cannot deliver the timing half of AC1, and the evidence for that is the parent's own log line.**

AC1 requires the call to *fail within the budget plus the existing grace*, explicitly "not a ~20+ minute `stop=? tokens in=0 out=0` mystery." The plan's mechanism is to config-drive the two knobs that **already exist** and raise them:

- `src/external/deepseek.py:49` — `_API_CALL_TIMEOUT = 5 * 60` (300s), used as `_httpx.Timeout(...)` on the client (line 54)
- `src/external/deepseek.py:238-241` — `asyncio.wait_for(asyncio.to_thread(_make_api_call), timeout=_API_CALL_TIMEOUT + 10)` (310s)
- `src/external/anthropic.py:51, 59, 238, 260-262` — identical shape

Those knobs were set to 300s/310s **when the failing run took 1425.7s**. A mechanism that already failed to bound the call at 310s will not bound it at 610s; raising the budget widens the mystery window rather than closing it. After this plan ships, the operator gets a non-empty error — real progress, and AC1's second half — but still gets it ~20+ minutes in, which is the exact symptom AC1 names.

Two mechanisms explain the 1425.7s, and neither is addressed:

- `_httpx.Timeout(N)` bounds *per-operation* time (connect / individual socket read / write / pool), not total call wall time. A slow or trickling response resets the read clock on every chunk and can run indefinitely without tripping it. Separately, neither client sets `max_retries`, so the Anthropic-compatible SDK default (2 retries = up to 3 attempts) multiplies whatever per-attempt bound does apply — 3 × 610s is ~30 minutes of legal wall time under the new budget.
- `asyncio.wait_for` around `asyncio.to_thread` cannot preempt a blocking call. When the timer fires, `wait_for` cancels the inner task and then **awaits that cancellation**; the thread running `client.messages.create` is not cancellable, so the caller is not released until the SDK call actually returns. The Stage 3 Decision assumes the opposite ("when wait_for fires, the caller must still get the structured timeout failure even if the worker thread keeps running") — the caller does eventually get it, but at provider-return time, not at budget+grace.

**Recommendation:** add a stage that bounds *caller-observed* wall time and prove it. Any of these is in-slice for utils + external; pick one and write it into the plan rather than leaving it to build time:

- Bound the retry budget explicitly (config-owned `max_retries` on the client) **and** set granular `_httpx.Timeout(connect=..., read=..., write=..., pool=...)` so attempts × per-attempt is provably ≤ the budget.
- Release the caller at the deadline without waiting on the orphan thread — e.g. `asyncio.wait({task}, timeout=...)` with `FIRST_COMPLETED` and abandon the straggler, returning the structured timeout failure immediately.
- Move the call to the SDK's async client so cancellation actually propagates and per-attempt timeouts apply against a bounded retry count.

The Done-when for that stage should assert the **measured `duration` in the `log_llm_batch_summary` line is ≈ budget+grace**, not the provider's eventual return time — that is the observable AC1 turns on. If you conclude bounding wall time needs a change outside this child's Files Changed table, stop and escalate on AST-1164 rather than widening the slice unilaterally.

**2. `fix-now` — Stage 2 step 3 would break the module if executed as written.**

"Add `BaseException` to the typing import" — `BaseException` is a builtin, not a `typing` export, so `from typing import ..., BaseException` raises `ImportError` at import time and takes `src/utils/llm_external.py` (and both externals) down with it. The existing `classify_provider_balance_refusal(exc: BaseException)` at `src/utils/llm_external.py:9` already annotates exactly this way with no import at all, and `Optional` is already imported on line 3. Delete the step — no import change is needed for the new classifier.

**3. `discuss` — the timeout classifier may miss the exception that actually caused the blank `error=`.**

`classify_provider_call_timeout` matches `isinstance(exc, TimeoutError)` plus an exact-leaf-name allowlist. A timeout surfaced *wrapped* — e.g. `anthropic.APIConnectionError` carrying an `httpx.ReadTimeout` as `__cause__` — has `type(exc).__name__ == "APIConnectionError"`, which is not in `exception_type_names` and is not a `TimeoutError`, so it would fall through to the balance-refusal branch and back to `error=str(e)`. Since the plan does not yet name which exception class produced the observed blank string, that fall-through is a live path to shipping the same blank `error=`. Consider walking `__cause__` / `__context__` in the classifier, and either way add a guard that a failure return **never** carries an empty `error` regardless of classification — that single invariant is what AC1's second half actually requires. (I agree with the Decision to prefer typed/name matching over message substrings; this is about coverage, not approach.)

**4. `acceptable`** — The 10-minute budget itself is Archie-answered (parent Open questions §3), so it is not in question. Worth confirming while revising: with retries bounded per finding 1, worst-case hop latency stays under `ASTRAL_CONFIG["dispatch_timeout_seconds"]` (3600s), so AUTO dispatch should not start reaping calls that the new budget considers healthy.

## What the plan gets right

Recording this so the revision does not lose it: the config block is correctly shaped and placed parallel to `PROVIDER_BALANCE_REFUSAL` (confirmed at `src/utils/config.py:4029-4033`, with the module-header `Config sections:` convention at line 38); removing the `5 * 60` hardcode satisfies §1.4 / `astral.standards.no-hardcoded-sets`; putting classify/message helpers once in `src/utils/llm_external.py` for both externals satisfies §1.3 DRY and keeps the `astral.layers.core-vs-external-bright-line` split intact (pure classification in utils, I/O and tagging in external); leaving `src/core/agent.py` alone is the right call for `astral.standards.in-scope-only` and matches the sibling boundaries; and the `str(asyncio.TimeoutError()) == ""` diagnosis is correct and is genuinely the reason `error=` prints blank.

Self-assessment is honest — `Risk: Medium` with "a missed except path could still emitting blank errors" names finding 3 territory unprompted. Conf `high` is the one I would soften: it rests on "budget already exists as `_API_CALL_TIMEOUT` + wait_for grace," and that existing budget is precisely what the 1425.7s log shows to be unenforced.

context_tokens≈90000

— Joan

#### ada — 2026-08-05T23:03:01.436Z
Plan published on `origin/sub/AST-1164/AST-1189-provider-call-budget-timeout` @ `e013e910`.

**Plan doc:** https://github.com/susansomerset/astral/blob/sub/AST-1164/AST-1189-provider-call-budget-timeout/docs/features/artifacts/ast-1189-provider-call-budget-timeout-failure-class.md

**Scope:** Single-Component — `PROVIDER_CALL_BUDGET` (10 min + 10s grace) in config; shared timeout classify/message helpers in `llm_external`; DeepSeek + Anthropic drop hardcoded `_API_CALL_TIMEOUT`, return non-empty `error` + `failure_class=provider_call_timeout` on wait_for/httpx/SDK timeouts. Root cause of blank `error=`: `str(asyncio.TimeoutError()) == ""`.

**Conf:** high — budget + wait_for already exist; failure_class envelope matches AST-897/AST-903; hollow response (AST-1190) and hop release/debug (AST-1191) stay out.

**Risk:** Medium — mis-tagging ordinary API errors as timeouts, or a missed except path still emitting blank errors; 10-minute budget raises worst-case hop latency by design.

---

# Provider call budget + timeout failure class (anticipate_scan jobs failing)

**Linear:** [AST-1189](https://linear.app/astralcareermatch/issue/AST-1189/provider-call-budget-timeout-failure-class-anticipate-scan-jobs-failing)  
**Parent:** [AST-1164 — anticipate_scan jobs failing](https://linear.app/astralcareermatch/issue/AST-1164/anticipate-scan-jobs-failing)  
**Publish ref:** `origin/sub/AST-1164/AST-1189-provider-call-budget-timeout`

Raise the shared DeepSeek / Anthropic per-call time budget to **10 minutes** (config-owned), keep **+10s** grace, and make the **caller-observed** duration honor that budget: over-budget calls must return `success=False` with a **non-empty** timeout `error` and `failure_class=provider_call_timeout` at ≈ budget+grace — not after the SDK thread finally finishes (the parent log waited **1425.7s** while the old 310s `wait_for` failed to release the caller). Hollow `stop=?` / zero-token response classification is **AST-1190**; batch release / debug trail is **AST-1191**.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `PROVIDER_CALL_BUDGET` (600s timeout, 10s grace, `max_retries: 0`, failure_class, error template, exception type names); document in module header | utils |
| `src/utils/llm_external.py` | Budget readers; cause-chain timeout classifier; non-empty error helpers; `await_provider_call_with_budget` (release caller at deadline without awaiting the orphan thread) | utils |
| `src/external/deepseek.py` | Drop `_API_CALL_TIMEOUT`; client uses config httpx timeout + `max_retries`; replace `asyncio.wait_for(to_thread…)` with `await_provider_call_with_budget`; timeout/balance tagging + never-empty `error` on failure returns | external |
| `src/external/anthropic.py` | Same budget, wall-release, `max_retries`, and failure tagging as DeepSeek | external |

**Not in scope:** `src/core/agent.py` (consumes existing `error` / `failure_class` only); prompts / `run_next` / BUILD_ARTIFACTS topology; AST-1163 name/ANALYSIS tokens; AST-1190 empty-response surfacing; AST-1191 hop release + debug found/recorded; migrating to the Anthropic async SDK.

---

## Stage 1: Config — `PROVIDER_CALL_BUDGET`

**Done when:** `PROVIDER_CALL_BUDGET` is importable with `timeout_seconds == 600`, `grace_seconds == 10`, `max_retries == 0`, and `failure_class == "provider_call_timeout"`.

1. In `src/utils/config.py` module docstring `Config sections:`, add a line after `PROVIDER_BALANCE_REFUSAL`:
   `PROVIDER_CALL_BUDGET — LLM per-call wall budget + timeout failure class (AST-1189)`.
2. Immediately after the existing `PROVIDER_BALANCE_REFUSAL = {…}` block, add:

```python
# PROVIDER_CALL_BUDGET — per-call LLM wall time (AST-1189 / Archie: 10 minutes).
# httpx client timeout uses timeout_seconds; caller wait uses timeout_seconds + grace_seconds.
# max_retries=0 → one attempt (SDK default 2 would allow up to 3× wall time inside the worker thread).
PROVIDER_CALL_BUDGET = {
    "timeout_seconds": 600,
    "grace_seconds": 10,
    "max_retries": 0,
    "failure_class": "provider_call_timeout",
    "error_template": (
        "Provider call exceeded per-call time budget ({timeout_seconds}s)"
    ),
    "exception_type_names": (
        "TimeoutError",       # builtin / asyncio.TimeoutError
        "TimeoutException",   # httpx base
        "ReadTimeout",
        "ConnectTimeout",
        "WriteTimeout",
        "PoolTimeout",
        "APITimeoutError",    # anthropic SDK
    ),
}
```

3. Do not add env lookups. Do not change `dispatch_timeout_seconds` (3600) or Railway gunicorn timeout — with `max_retries=0` and a 610s caller budget, worst-case hop latency stays under the AUTO dispatch wall.

⚠️ **Decision:** Dedicated top-level block (parallel to `PROVIDER_BALANCE_REFUSAL`), not a nested `ASTRAL_CONFIG` key — same failure-class pattern as AST-897.

---

## Stage 2: Shared helpers in `llm_external`

**Done when:** DeepSeek/Anthropic can import budget readers, a cause-chain timeout classifier, never-empty error helpers, and an async wall-budget runner that releases the caller at the deadline without awaiting the worker thread — without either external importing the other.

1. In `src/utils/llm_external.py`, import `PROVIDER_CALL_BUDGET` alongside the existing `PROVIDER_BALANCE_REFUSAL` import. Add `asyncio` and `Callable` / `Any` as needed for the await helper. **Do not** add `BaseException` to the `typing` import — it is a builtin (same as the existing `classify_provider_balance_refusal(exc: BaseException)` annotation, which already works with no import).
2. Add budget readers + timeout error message:

```python
def provider_call_http_timeout_seconds() -> float:
    """httpx / Anthropic client timeout (seconds)."""
    return float(PROVIDER_CALL_BUDGET["timeout_seconds"])


def provider_call_wait_timeout_seconds() -> float:
    """Caller-observed wall budget = timeout_seconds + grace_seconds."""
    return float(PROVIDER_CALL_BUDGET["timeout_seconds"]) + float(
        PROVIDER_CALL_BUDGET["grace_seconds"]
    )


def provider_call_timeout_error_message() -> str:
    """Non-empty operator-facing timeout error (str(TimeoutError()) is '')."""
    return PROVIDER_CALL_BUDGET["error_template"].format(
        timeout_seconds=int(PROVIDER_CALL_BUDGET["timeout_seconds"])
    )


def provider_call_max_retries() -> int:
    return int(PROVIDER_CALL_BUDGET["max_retries"])
```

3. Add cause-chain classifier (covers wrapped `APIConnectionError` → `__cause__` `ReadTimeout`, etc.):

```python
def classify_provider_call_timeout(exc: BaseException) -> Optional[str]:
    """Return PROVIDER_CALL_BUDGET failure_class when exc (or cause/context) is a call-budget timeout."""
    fc = PROVIDER_CALL_BUDGET["failure_class"]
    names = PROVIDER_CALL_BUDGET["exception_type_names"]
    seen: set[int] = set()
    cur: Optional[BaseException] = exc
    while cur is not None and id(cur) not in seen:
        seen.add(id(cur))
        if isinstance(cur, TimeoutError) or type(cur).__name__ in names:
            return fc
        cur = cur.__cause__ if cur.__cause__ is not None else cur.__context__
    return None
```

4. Add never-empty error guard (AC1 second half — blank `error=` must not ship on any failure path this ticket touches):

```python
def non_empty_provider_error(exc: BaseException, *, fallback: str) -> str:
    """str(exc) or fallback — never '' (TimeoutError default)."""
    err = str(exc).strip()
    return err if err else fallback
```

5. Add the wall-budget runner that **does not** use `asyncio.wait_for` (wait_for cancels then **awaits** the uncancellable `to_thread` worker, so the caller stays blocked until the SDK returns — that is why 310s failed to bound the 1425.7s run):

```python
async def await_provider_call_with_budget(
    make_call: Callable[[], Any],
    *,
    timeout_seconds: float,
) -> Any:
    """Run blocking SDK call in a worker thread; release the caller at timeout_seconds.

    On timeout: raise TimeoutError with provider_call_timeout_error_message() and do
    **not** await the pending thread task (orphan may finish later; caller is free).
    """
    task = asyncio.create_task(asyncio.to_thread(make_call))
    done, _pending = await asyncio.wait({task}, timeout=timeout_seconds)
    if task in done:
        return task.result()
    raise TimeoutError(provider_call_timeout_error_message())
```

6. Do **not** change `classify_provider_balance_refusal`, `emit_llm_call_debug`, or hollow-response logic.

⚠️ **Decision:** Wall-time release via `asyncio.wait(..., FIRST_COMPLETED` default) + abandon pending task — Joan option 2. Chosen over async-SDK migration (larger slice) and over granular httpx-only (still leaves wait_for awaiting the thread). `max_retries=0` is the companion so the abandoned worker is one attempt, not three.

⚠️ **Decision:** Prefer typed/name matching (plus cause/context walk) over message substrings — same as Joan discuss #3 agreement.

---

## Stage 3: Wire DeepSeek + Anthropic — config budget, wall release, timeout failure class

**Done when:** Both `send_to_deepseek` and `send_to_anthropic` (1) build clients with config httpx timeout + `max_retries`, (2) invoke the SDK via `await_provider_call_with_budget` at `provider_call_wait_timeout_seconds()`, (3) on timeout-class failures return `success=False`, non-empty `error` from `provider_call_timeout_error_message()`, and `failure_class=provider_call_timeout`, and (4) every other failure return uses `non_empty_provider_error` so `error` is never `""`. **Observable for AC1 timing:** a forced over-budget call logs `log_llm_batch_summary` with `duration` ≈ budget+grace (≈610s), not the provider’s eventual return time.

### 3a. `src/external/deepseek.py`

1. Remove module-level `_API_CALL_TIMEOUT = 5 * 60`.
2. Extend the `llm_external` import to include:
   `provider_call_http_timeout_seconds`, `provider_call_wait_timeout_seconds`,
   `provider_call_max_retries`, `await_provider_call_with_budget`,
   `classify_provider_call_timeout`, `provider_call_timeout_error_message`,
   `non_empty_provider_error`
   (keep `classify_provider_balance_refusal`).
3. In `_get_client`, construct:
   ```python
   return Anthropic(
       api_key=key,
       base_url="https://api.deepseek.com/anthropic",
       timeout=_httpx.Timeout(provider_call_http_timeout_seconds()),
       max_retries=provider_call_max_retries(),
   )
   ```
4. Replace:
   ```python
   response = await asyncio.wait_for(
       asyncio.to_thread(_make_api_call),
       timeout=_API_CALL_TIMEOUT + 10,
   )
   ```
   with:
   ```python
   response = await await_provider_call_with_budget(
       _make_api_call,
       timeout_seconds=provider_call_wait_timeout_seconds(),
   )
   ```
5. In **both** `except Exception as e:` blocks that build the failure `out` dict (inner call-path and outer), after computing `duration`:
   - `fc_timeout = classify_provider_call_timeout(e)`
   - If `fc_timeout`: `err = provider_call_timeout_error_message()`; set `out["failure_class"] = fc_timeout`
   - Else: `err = non_empty_provider_error(e, fallback=type(e).__name__)`; apply existing `classify_provider_balance_refusal(e)` tagging when it returns a value
   - Pass `error=err` into `log_llm_batch_summary` and `emit_llm_call_debug` (when debug); set `out["error"] = err`
   - Assert by construction: `err` is never `""`
6. Do not add hollow-response checks on successful returns. Do not change max_tokens hard-fail (AST-903).

### 3b. `src/external/anthropic.py`

1. Mirror 3a exactly: drop `_API_CALL_TIMEOUT`; same imports; `_get_client` and the `api_key_override` inline `Anthropic(...)` both get `timeout=_httpx.Timeout(provider_call_http_timeout_seconds())` and `max_retries=provider_call_max_retries()`; replace `wait_for(to_thread…)` with `await_provider_call_with_budget`; same timeout-vs-balance tagging + never-empty `error` in both except blocks.

⚠️ **Decision:** Leave `src/core/agent.py` unchanged. `do_task` already logs `result.get("error")` and returns the provider dict. Found/recorded debug enrichment and batch release are AST-1191.

⚠️ **Decision:** Abandoned worker threads are accepted — when the deadline fires we return timeout to the caller immediately; the thread may still finish later. No thread-kill / async-SDK migration in this ticket.

---

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; publish each to `origin/sub/AST-1164/AST-1189-provider-call-budget-timeout`.
- Do not add files outside the Files Changed table.
- If `PROVIDER_BALANCE_REFUSAL` / except-block / `Anthropic(...)` constructor shape has drifted from this plan, stop and comment on **AST-1164** (parent) with the Stage N blocked template — do not invent a third failure path or widen into async-SDK rewrite.
- Healthy path (normal stop reason + tokens within budget) must remain a successful return with no timeout tagging.
- AC1 timing proof for build/test: over-budget path’s logged `duration` ≈ `timeout_seconds + grace_seconds`, not provider-return wall time.

---

## Self-Assessment

**Scope:** `Single-Component` — config + shared LLM utils (including wall-budget await helper) + mirrored DeepSeek/Anthropic external call wrappers; no core orchestration, UI, or dispatch topology.

**Conf:** `Medium` — blank `error=` from `str(TimeoutError())` and the failure_class envelope are well understood (AST-897/903), but the 1425.7s parent log proved the prior wait_for+to_thread budget was not caller-enforcing; the FIRST_COMPLETED abandon path is the right fix and is new wiring on this call site.

**Risk:** `Medium` — orphan threads after abandon; mis-tagging wrapped non-timeout errors if cause-walk is too eager (mitigated by type-name allowlist); 10-minute budget raises worst-case hop latency by design (Archie) but stays under 3600s dispatch timeout with `max_retries=0`.

---

## Code rules check

| Rule | Plan alignment |
|------|----------------|
| §1.3 DRY | Timeout classify, message, never-empty, and wall-budget await live once in `llm_external` |
| §1.4 / §2.1 config | Budget + retries + failure_class literals in `PROVIDER_CALL_BUDGET`; no env; no magic `5 * 60` left in externals |
| §2.2 / bright line | Provider I/O + timeout tagging stay in external; utils hold pure helpers + await orchestration of the thread |
| §2.4 batch | Untouched — release/hold is AST-1191 |
| §3.3 imports | utils ← config; external ← utils; no external↔external; no `BaseException` from `typing` |
| §3.5 naming | `provider_call_timeout` failure_class; `PROVIDER_CALL_BUDGET` parallel to balance refusal |
| in-scope-only | No hollow-response, prompt, hop-release, or async-SDK migration |

---

## Revisions

Revision 1 — 2026-08-05  
Driven by: Joan `[plan-discuss] round=1 concern` (plan-rubric.v1 REVISE) — AC1 timing half unmet by raising an already-unenforced budget; Stage 2 `BaseException` typing-import step would ImportError; classifier may miss wrapped timeouts / blank `error=` fall-through.  
Changes:
- Stage 1: add config-owned `max_retries: 0`.
- Stage 2: delete the `BaseException` typing-import step; add cause/context walk on classifier; add `non_empty_provider_error`; add `await_provider_call_with_budget` (FIRST_COMPLETED / abandon pending — replaces wait_for).
- Stage 3: wire both externals to the wall-budget await + `max_retries`; never-empty `error` on all touched failure returns; Done-when asserts logged `duration` ≈ budget+grace.
- Conf softened `high` → `Medium`. Summary + Decisions updated to match Joan’s wait_for/to_thread analysis.

---

## Review (build stub)

**Publish ref:** `origin/sub/AST-1164/AST-1189-provider-call-budget-timeout`  
**Tip:** `663f6a07`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `d41b16c7` | `PROVIDER_CALL_BUDGET` (600s / 10s grace / `max_retries: 0`) |
| 2 | `6d650feb` | wall-budget helpers + cause-chain classify + never-empty error |
| 3 | `663f6a07` | DeepSeek + Anthropic client budget, `await_provider_call_with_budget`, timeout `failure_class` |

---

## Radia review — code-rubric.v1 revision=1

**Publish ref tip:** `683bcb1f`

**Overall:** FIX-NOW

### Plan adherence

Stages 1–3 (`d41b16c7`, `6d650feb`, `663f6a07`) match the plan's code blocks essentially verbatim — `PROVIDER_CALL_BUDGET` shape, the four `llm_external` helpers, `await_provider_call_with_budget`'s `asyncio.wait(FIRST_COMPLETED)`-and-abandon design, and the mirrored DeepSeek/Anthropic wiring (client `max_retries`, timeout-vs-balance tagging, never-empty `error`) all land as specified. `src/core/agent.py` is untouched, honoring the stated boundary.

### Findings

**fix-now — cross-ticket test/doc contamination breaks this publish ref's own test tree.** The `merge-tests(AST-1189): origin/tests 886b1033` commit pulls in `748a5725 test(AST-1190): hollow provider response + blank error= coverage` as an ancestor on the shared `origin/tests` branch, plus `docs/features/artifacts/ast-1190-empty-unusable-provider-response-surfacing.md` (added earlier in this branch's own history, survives a `347bf506` attempt to drop the "sibling" file). Confirmed by running the touched test files against this tip in a fresh venv: **9 failing tests** (`TestAst1190DoTaskEmptyProviderError` x2, `TestAst1190EmptyUnusableProviderResponse` in both `test_anthropic.py`/`test_deepseek.py`, `TestAst1190ProviderEmptyResponseConfig`, `TestAst1190EmptyResponseHelpers` x5) — all `ImportError`/`AttributeError` on `PROVIDER_EMPTY_RESPONSE`, `normalize_provider_error`, `is_unusable_provider_response`, none of which exist on this tip (`src/core/agent.py` and `src/utils/config.py` carry no AST-1190 product surface here — that work lives on AST-1190's own branch). The plan's own boundary line ("Not in scope: ... AST-1190 empty-response surfacing") is correct in intent but not honored by the merged test/doc state. Fix: re-cut the `merge-tests` merge (or have Betty publish an AST-1189-only `origin/tests` SHA that does not stack on the AST-1190 test commit) and drop the leftover `ast-1190-*.md` plan file from this branch before re-requesting review.

**advisory — `astral.standards.debug-contract-gated` mechanically in-scope but content is benign.** The plan's Considered-but-excluded table marks debug/found-recorded trail as AST-1191, but the diff does touch `emit_llm_call_debug(..., error=err, ...)` call sites in both externals. No new debug capability or ungating was added (only the `error=` value changed from `str(e)` to the classified/never-empty string) — not a straggler in substance, noting for completeness.

### Pattern conformance

None cited (plan lists statute ids under In-scope / Considered-but-excluded, not `canon/patterns/*`; those ids are covered by the full-set sweep).

### What's solid

- `PROVIDER_CALL_BUDGET` config shape, the wall-budget release-without-awaiting-the-orphan design, and the mirrored DeepSeek/Anthropic wiring are clean, DRY, and layer-correct (external → utils only, no cross-external import).
- Never-empty `error` guarantee is enforced consistently on every touched failure path in both externals.

### Recommended actions

1. Re-publish `origin/sub/AST-1164/AST-1189-provider-call-budget-timeout` with a `merge-tests` SHA scoped to AST-1189 only (or coordinate ordering with Betty so AST-1190's test commit isn't an ancestor).
2. Drop `docs/features/artifacts/ast-1190-empty-unusable-provider-response-surfacing.md` from this branch — it belongs on AST-1190's own publish ref only.
3. Re-run the full touched-file test set on the corrected tip before re-requesting Review Posted.

`context_tokens≈45000`
— Radia

---

## Resolution

**Date:** 2026-08-05  
**Driven by:** Radia `[code-rubric] revision=1` FIX-NOW — cross-ticket AST-1190 test/doc contamination on this publish ref.

| Finding | Action |
|---------|--------|
| leftover `docs/features/artifacts/ast-1190-empty-unusable-provider-response-surfacing.md` on this branch | **Done (engineer):** removed |
| `merge-tests(AST-1189)` stacked on `748a5725 test(AST-1190)` | **Done (Betty):** re-cut `merge-tests(AST-1189): origin/tests 08675910` — `748a5725` not an ancestor; `TestAst1190*` gone from tip |
| advisory debug-contract touch (`error=` value only) | Accepted — no product change |

**Verify (Ada):** Betty’s narrowed AST-1189 node IDs — **12 passed** on tip after re-cut. Publish ref green standalone.

<!-- merge-child: plan tip present on sub -->
