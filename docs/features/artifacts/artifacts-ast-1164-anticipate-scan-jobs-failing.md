# AST-1164 — anticipate_scan jobs failing
**Component:** artifacts  
**Children:** AST-1189, AST-1190, AST-1191  
**Linear archived:** AST-1164 2026-08-07; AST-1189 2026-08-07; AST-1190 2026-08-07; AST-1191 2026-08-07

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-08-05 16:02 | AST-1189 | docs | `e013e910e` | docs(AST-1189): plan — provider call budget + timeout failure class |
| 2026-08-05 16:02 | AST-1190 | docs | `4f1b224f0` | docs(AST-1190): plan — empty/unusable provider response surfacing |
| 2026-08-05 16:03 | AST-1190 | docs | `347bf506f` | docs(AST-1190): drop sibling plan file; align timeout class vocabulary |
| 2026-08-05 16:10 | AST-1189 | docs | `94846b991` | docs(AST-1189): plan — Joan round=1 discuss reply (wall-time release) |
| 2026-08-05 16:10 | AST-1190 | code | `c3a39ddf4` | code(AST-1190): PROVIDER_EMPTY_RESPONSE helpers and summary blank-error path |
| 2026-08-05 16:11 | AST-1190 | code | `597a41d9b` | code(AST-1190): do_task non-empty provider error coerce and debug |
| 2026-08-05 16:11 | AST-1190 | code | `968a3a7cc` | code(AST-1190): hollow response fail-closed on DeepSeek and Anthropic |
| 2026-08-05 16:12 | AST-1190 | docs | `8cfeb49f9` | docs(AST-1190): review stub; drop sibling plan file again |
| 2026-08-05 16:14 | AST-1189 | code | `6d650feb1` | code(AST-1189): Stage 2 — wall-budget helpers in llm_external |
| 2026-08-05 16:14 | AST-1189 | code | `d41b16c7b` | code(AST-1189): Stage 1 — PROVIDER_CALL_BUDGET config |
| 2026-08-05 16:15 | AST-1189 | code | `663f6a07e` | code(AST-1189): Stage 3 — wall-budget wire-up DeepSeek + Anthropic |
| 2026-08-05 16:15 | AST-1189 | docs | `ce0918a13` | docs(AST-1189): review stub — Stages 1–3 published |
| 2026-08-05 16:16 | AST-1190 | test | `748a57252` | test(AST-1190): hollow provider response + blank error= coverage |
| 2026-08-05 16:16 | AST-1190 | merge-tests | `e5ca8ec9e` | merge-tests(AST-1190): origin/tests 748a57252fbd6b96daf96dd5c8e61bfb14007a0b |
| 2026-08-05 16:18 | AST-1189 | test | `886b10336` | test(AST-1189): provider call budget + timeout failure class coverage |
| 2026-08-05 16:18 | AST-1190 | test | `0f4469e17` | test(AST-1190): import hollow-response helpers in provider clients |
| 2026-08-05 16:26 | AST-1190 | docs | `2311dbca6` | docs(AST-1190): Radia review — findings |
| 2026-08-05 16:28 | AST-1190 | resolve | `56facd867` | resolve(AST-1190): — clean |
| 2026-08-05 16:31 | AST-1189 | docs | `4368078f6` | docs(AST-1189): Radia review — findings |
| 2026-08-05 16:34 | AST-1189 | resolve | `107e325f1` | resolve(AST-1189): — drop sibling plan doc; qa-handoff merge-tests |
| 2026-08-05 16:36 | AST-1189 | test | `086759101` | test(AST-1189): provider call budget coverage (AST-1190-free tip) |
| 2026-08-05 16:36 | AST-1189 | merge-tests | `0a98422e1` | merge-tests(AST-1189): origin/tests 086759101ef753ca01467e8ee510f6220bd173f3 |
| 2026-08-05 16:38 | AST-1189 | resolve | `c29d7a598` | resolve(AST-1189): — findings addressed |
| 2026-08-05 16:42 | AST-1189 | resolve | `1ec371957` | resolve(AST-1189): — merge origin/ftr product (AST-1190 surfaces) |
| 2026-08-05 16:42 | AST-1189 | resolve | `98f495fea` | resolve(AST-1189): — merge origin/dev (product only) |
| 2026-08-05 16:45 | AST-1189 | test | `aefa0efe7` | test(AST-1189): union AST-1189+AST-1190 bible/tests for ftr merge |
| 2026-08-05 16:47 | AST-1189 | plan | `ee5e760f1` | plan(AST-1189): — tip marker for merge-child validate-sub-log |
| 2026-08-05 16:51 | AST-1191 | docs | `de6893a49` | docs(AST-1191): plan — artifact hop failure release + debug trail |
| 2026-08-05 16:58 | AST-1191 | docs | `177caa818` | docs(AST-1191): plan — Joan round=1 timesheet keys + outcome return |
| 2026-08-05 17:04 | AST-1191 | docs | `ec8971de5` | docs(AST-1191): plan — Joan round=2 close_hop_ledger every-exit return |
| 2026-08-05 17:08 | AST-1191 | code | `3aa816f3e` | code(AST-1191): provider-failure found/recorded debug trail |
| 2026-08-05 17:08 | AST-1191 | code | `7f5b132e6` | code(AST-1191): hop failure error_state + claim release outcome |
| 2026-08-05 17:09 | AST-1191 | docs | `77f43af3c` | docs(AST-1191): build review stub |
| 2026-08-05 17:12 | AST-1191 | test | `aa3b3023d` | test(AST-1191): hop failure claim release + debug trail coverage |
| 2026-08-05 17:12 | AST-1191 | merge-tests | `5c6cdcda1` | merge-tests(AST-1191): origin/tests ac509b1244a47fcd3d63858e38bf4d37c11a330f |
| 2026-08-05 17:19 | AST-1191 | docs | `d8864b7af` | docs(AST-1191): Radia review — clean |
| 2026-08-05 17:21 | AST-1191 | resolve | `5739ebc1b` | resolve(AST-1191): — clean |
| 2026-08-07 18:26 | AST-1189 | docs | `3dd51319b` | docs(AST-1189): archive Linear issue content |
| 2026-08-07 18:26 | AST-1190 | docs | `5d030e270` | docs(AST-1190): archive Linear issue content |
| 2026-08-07 18:26 | AST-1191 | docs | `a6521fcb6` | docs(AST-1191): archive Linear issue content |
| 2026-08-07 18:28 | AST-1164 | docs | `7e9c62ec1` | docs(AST-1164): archive Linear issue content |

_AST-1189 and AST-1190 built on the same shared epic worktree and their histories cross-contaminated mid-build (see both children's Review sections): a `docs(AST-1189): Radia review — findings` commit lands twice above (once correctly tagged `AST-1189`, once matched to `AST-1190` by the grep because it is also an ancestor on that sub-branch), and several `test(AST-1189)` / `merge-tests(AST-1189)` rows above carry AST-1190 test coverage merged in while Betty and Ada re-cut a clean AST-1189-only test tree after Radia's fix-now (cross-ticket test/doc contamination — see AST-1189 Review). This is git-branch entanglement from parallel sibling development, not misattributed product work — each child's own Files-changed table below reflects only that ticket's actual `src/` diff. One row is unrelated cross-ticket noise from a different family: `test(AST-1210): lock evaluate_meteorite twin contract + restore AST-1193 parity` mentions AST-1189/1190/1192/1193 test lineage in its body but is AST-1210's own commit (`docs/features/interface/`) — not shown in this table._

## Epic — AST-1164
_Archived: 2026-08-07 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1164/anticipate-scan-jobs-failing · Status at archive: Archive · Project: Astral Artifacts · Assignee: chuckles · Priority / estimate: Urgent / — · Blocked by / blocks / related: related: AST-1161; related: AST-1162_

### Purpose

`anticipate_scan` is the entry hop of the resume artifact chain. A live run waited ~24 minutes on DeepSeek, then logged `stop=? tokens in=0 out=0` and `do_task(anticipate_scan) provider call failed` with an **empty** error string. Operators cannot tell timeout from hollow response from a silent provider failure, and Generate Artifacts cannot be trusted or retried with a clear reason. This epic hardens provider-call failure for that hop (and the shared LLM path it uses) so long empty waits and blank errors stop masking the real outcome.

### Functional scope

* Provider calls used by artifact hops (DeepSeek path that produced the pasted log; Anthropic mirror when it shares the same call/timeout shape) enforce a hard per-call time budget. A call that exceeds that budget fails promptly with a non-empty, classifiable timeout error — it does not sit for tens of minutes and then report zero tokens with a blank reason.
* When a provider returns without a usable stop reason, token usage, and/or content (the observed `stop=?` / `tokens in=0 out=0` shape), `do_task` fails with a **non-empty** error that names that hollowness. Logs never show a healthy-looking LLM summary followed by `provider call failed … error=` with nothing after the equals.
* On such a failure for `anticipate_scan` (and sibling artifact hops on the same provider path), the entity batch is released and the job lands on the configured artifact error/hold state so Generate Artifacts can be retried; Execution History / app_log shows the failure reason for that `batch_id`.
* With `debug=True` on the touched provider/`do_task` failure path: log what was **found** and what was **recorded** (duration, stop reason, token counts, error / failure class). Index headers use universal `index N/M` + primary identifier + outcome (Style D); working detail lines use the contract prefix (two spaces, pipe, two spaces); payloads >50 lines use first 15 / `<n lines omitted>` / last 15. Backend only.

### Architectural definition

* **Patterns to reuse** — `pattern.batch.entity-claim-process-release` (failure still claim/process/release; no orphaned claims); `pattern.dispatch.run-next-chain-authority` (`run_next` / hop order unchanged — harden call outcomes, not chain topology); `pattern.config.config-block` (timeouts / provider knobs stay config-owned when raised out of hardcodes).
* **New patterns proposed** — none.
* **Applicable statutes** — `astral.agent.do-task-delegation` (provider I/O stays in external; core consumes structured failure); `astral.batch.claim-process-release`; `astral.batch.batch-id-first`; `astral.dispatch.run-next-is-chain-authority`; `astral.layers.core-vs-external-bright-line`; `astral.layers.import-direction`; `astral.standards.debug-contract-gated`; `astral.standards.logging-via-utils`; `astral.standards.data-raises-caller-logs`; `astral.standards.in-scope-only`; `astral.standards.no-cross-contamination`; `astral.standards.dry-and-focused-functions`; `astral.config.config-source-of-truth`; `astral.patterns.coat-check-never-store-empty` (do not treat empty provider payloads as successful hop output).

### Boundaries

* Does **not** fix hollow `{$FIRST_NAME}` / `{$LAST_NAME}` or empty `{$ANALYSIS_*}` tokens — that is AST-1163 (related).
* Does **not** re-author `anticipate_scan` prompt prose in Manage Tasks.
* Does **not** change `run_next` chain membership, graduation maps, or BUILD_ARTIFACTS hop topology.
* Does **not** redesign timesheet/pricing schema beyond the failure classification needed so ops can see timeout vs hollow response vs balance refusal (AST-897) vs max_tokens (AST-903).
* Does **not** expand schedulability of `anticipate_scan`.
* Sibling UT on signature spacing (AST-1161 / AST-1162) is out of scope.

### Acceptance criteria

1. A provider call that exceeds the configured per-call time budget fails within that budget (plus the small existing grace already used around the wait) with a non-empty timeout error / failure class — not a ~20+ minute `stop=? tokens in=0 out=0` mystery with blank `error=`.
2. A provider outcome that yields `stop=?` and zero in/out tokens with no usable content causes `do_task` to return failure with a non-empty error string visible in the `provider call failed … error=` log line.
3. After such a failure on `anticipate_scan`, the job is not left batch-claimed; it is on the configured artifact error/hold state for that task, and the failure reason is visible against that `batch_id` in Execution History / app_log.
4. A debug-gated run of the fixed path shows found/recorded lines for duration, stop, tokens, and error/failure class on the failed call.
5. A healthy DeepSeek (or mirrored Anthropic) response with normal stop reason and token counts still completes `anticipate_scan` successfully when prompt context is otherwise valid.

### Dependencies and blockers

* **Related (not blocking):** AST-1163 — hollow candidate name + ANALYSIS token context for the same hop. Fixing 1163 may reduce garbage prompts; this epic still owns provider timeout / empty-error / zero-token response hardening on its own.
* Prior failure-class patterns to reuse (already shipped): AST-897 (balance refusal), AST-903 (JSON max_tokens hard-fail).
* No open Linear blockers. Parallel Artifacts UT: AST-1161 — no functional dependency.

### Open questions

1. Confirm the split: AST-1164 = provider timeout / empty-error / zero-token response hardening; AST-1163 = hollow name + ANALYSIS tokens — not a duplicate?
   1. Correct.
2. Which candidate id + job id produced batch `anticipate_scan-bc0b3279-bde7-4c7e-a895-156ca2fa7b4a` (for UAT replay)?
   1. Not applicable, just implement and I'll retest.
3. Timeout policy: keep the existing ~5 minute provider call budget but make failure/cancellation always surface cleanly, or raise/lower the budget via `ASTRAL_CONFIG` as part of this epic?
   1. Raise the timeout to 10 minutes, please.
4. Must the Anthropic mirror ship in the same epic, or DeepSeek-only until a matching Anthropic hang is seen?
   1. Both, actually, yes.

### Proposed child tickets

**1!: Provider call budget + timeout failure class — Ada** — Enforce the hard per-call time budget on the DeepSeek path (and Anthropic mirror if #4 includes it) so over-budget calls fail with a non-empty timeout error / failure class instead of a long zero-token mystery. Does **not** own hollow-response classification (#2) or artifact hop release/debug (#3).
**Citations:** `pattern.config.config-block`; `astral.config.config-source-of-truth`; `astral.layers.core-vs-external-bright-line`; `astral.agent.do-task-delegation`; `astral.standards.in-scope-only`.

**2!: Empty / unusable provider response surfacing — Hedy** — When the provider returns `stop=?` / zero tokens / no usable content, fail `do_task` with a non-empty error (never blank `error=`) and do not log that outcome as a healthy LLM summary. Does **not** own timeout budget (#1).
**Citations:** `astral.agent.do-task-delegation`; `astral.standards.logging-via-utils`; `astral.patterns.coat-check-never-store-empty`; `astral.standards.dry-and-focused-functions`.

**3: Artifact hop failure release + debug trail — Katherine** — After #1 and #2: on provider failure for `anticipate_scan` / shared artifact hops, ensure batch release + configured error/hold state, and AST-538-style debug found/recorded for UAT. Does **not** redesign LLM adapters beyond consuming their structured failures.
**Citations:** `pattern.batch.entity-claim-process-release`; `astral.batch.claim-process-release`; `astral.dispatch.run-next-is-chain-authority`; `astral.standards.debug-contract-gated`.

### Original brief

```
[2026-08-03 22:07:30] INFO src.external.deepseek: LLM deepseek task=anticipate_scan 1425.7s stop=? tokens in=0 out=0
[2026-08-03 22:07:30] ERROR src.core.agent: do_task(anticipate_scan) provider call failed batch_id=anticipate_scan-bc0b3279-bde7-4c7e-a895-156ca2fa7b4a error=
[2026-08-03 21:45:55] INFO src.core.agent: run_next chain entry: task=anticipate_scan batch_id=anticipate_scan-bc0b3279-bde7-4c7e-a895-156ca2fa7b4a
```

#### Comments

##### chuckles — 2026-08-03T22:42:38.144Z
@susan

1. Confirm the split: **AST-1164** = provider timeout / empty-error / zero-token response hardening; **AST-1163** = hollow name + ANALYSIS tokens — not a duplicate?
2. Which candidate id + job id produced batch `anticipate_scan-bc0b3279-bde7-4c7e-a895-156ca2fa7b4a` (for UAT replay)?
3. Timeout policy: keep the existing ~5 minute provider call budget but make failure/cancellation always surface cleanly, or raise/lower the budget via `ASTRAL_CONFIG` as part of this epic?
4. Must the Anthropic mirror ship in the same epic, or DeepSeek-only until a matching Anthropic hang is seen?

— Chuckles

### Files changed (plan vs actual)

_No product commit trail on the parent — the epic worktree only carries the `plan(AST-1189)` tip-marker commit and the `docs(AST-1164)` archive commit. Implementation landed entirely via the three sub-issues below._

## Sub-issues

### AST-1189 — Provider call budget + timeout failure class
_Archived: 2026-08-07 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1189/provider-call-budget-timeout-failure-class-anticipate-scan-jobs · Status at archive: Archive · Project: Astral Artifacts · Assignee: ada · Priority / estimate: None / — · Blocked by / blocks / related: parent: AST-1164; blocks: AST-1191_

#### What this implements

Enforce the hard per-call time budget on the DeepSeek path and Anthropic mirror so over-budget calls fail with a non-empty timeout error / failure class instead of a long zero-token mystery. Raise the provider call budget to **10 minutes** (Archie: Open questions §3). Does **not** own hollow-response classification (sibling AST-1190) or artifact hop release/debug (sibling AST-1191).

#### Acceptance criteria

- [X] A provider call that exceeds the configured per-call time budget fails within that budget (plus the small existing grace already used around the wait) with a non-empty timeout error / failure class — not a ~20+ minute `stop=? tokens in=0 out=0` mystery with blank `error=`.
- [X] A healthy DeepSeek (or mirrored Anthropic) response with normal stop reason and token counts still completes `anticipate_scan` successfully when prompt context is otherwise valid.

#### Boundaries

Does not own empty/unusable provider response classification (Hedy sibling). Does not own artifact hop batch release / error-state / debug trail (Katherine sibling). Does not fix hollow name/ANALYSIS tokens (AST-1163). Does not re-author prompts or change run_next topology.

#### In scope / considered but excluded

In scope: `pattern.config.config-block` (`PROVIDER_CALL_BUDGET` in `src/utils/config.py`); `astral.config.config-source-of-truth` (timeout/grace/failure_class literals; no env); `astral.layers.core-vs-external-bright-line` (timeout tagging stays in `src/external/{deepseek,anthropic}.py`); `astral.agent.do-task-delegation` (core consumes structured `error` / `failure_class` from external); `astral.standards.in-scope-only` (budget + timeout failure class only); `astral.standards.dry-and-focused-functions` (shared classify/message helpers in `src/utils/llm_external.py`).

Considered but excluded: `astral.patterns.coat-check-never-store-empty` (hollow/empty provider payload surfacing is AST-1190); `pattern.batch.entity-claim-process-release` / `astral.batch.claim-process-release` (hop release + error/hold state is AST-1191); `astral.standards.debug-contract-gated` (found/recorded debug trail on failure is AST-1191); `astral.dispatch.run-next-is-chain-authority` (`run_next` / hop topology unchanged); `src/ui/**` (no UI surface for this failure class).

#### Notes for planning

Archie answers: timeout → 10 minutes; Anthropic mirror ships in this epic with DeepSeek. Blank `error=` root cause for wait_for path: `str(asyncio.TimeoutError()) == ""`.

#### Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `PROVIDER_CALL_BUDGET` (600s timeout, 10s grace, `max_retries: 0`, failure_class, error template, exception type names); document in module header | utils |
| `src/utils/llm_external.py` | Budget readers; cause-chain timeout classifier; non-empty error helpers; `await_provider_call_with_budget` (release caller at deadline without awaiting the orphan thread) | utils |
| `src/external/deepseek.py` | Drop `_API_CALL_TIMEOUT`; client uses config httpx timeout + `max_retries`; replace `asyncio.wait_for(to_thread…)` with `await_provider_call_with_budget`; timeout/balance tagging + never-empty `error` on failure returns | external |
| `src/external/anthropic.py` | Same budget, wall-release, `max_retries`, and failure tagging as DeepSeek | external |

**Not in scope:** `src/core/agent.py` (consumes existing `error` / `failure_class` only); prompts / `run_next` / BUILD_ARTIFACTS topology; AST-1163 name/ANALYSIS tokens; AST-1190 empty-response surfacing; AST-1191 hop release + debug found/recorded; migrating to the Anthropic async SDK.

#### Plan-discuss round=1 — Joan REVISE

**AC1 timing — the plan cannot deliver the timing half of AC1, and the evidence is the parent's own log line.** AC1 requires the call to fail *within* the budget plus grace. The plan's mechanism was to config-drive the two knobs that already exist and raise them — `_API_CALL_TIMEOUT = 5 * 60` (300s) and `asyncio.wait_for(asyncio.to_thread(_make_api_call), timeout=_API_CALL_TIMEOUT + 10)` (310s), identically in `anthropic.py`. Those knobs were set to 300s/310s **when the failing run took 1425.7s** — raising the budget widens the mystery window rather than closing it. Two mechanisms explain the 1425.7s and neither was addressed: `httpx.Timeout(N)` bounds per-operation time, not total call wall time (a trickling response resets the read clock on every chunk); and neither client set `max_retries`, so the SDK default 2 retries multiply whatever per-attempt bound applies (3 × 610s ≈ 30 minutes of legal wall time under the new budget). Separately, `asyncio.wait_for` around `asyncio.to_thread` cannot preempt a blocking call — on timeout it cancels the inner task and then **awaits that cancellation**, and the thread running `client.messages.create` is not cancellable, so the caller is not released until the SDK call actually returns; the Stage 3 Decision assumed the opposite. **Recommendation:** bound *caller-observed* wall time and prove it — bound the retry budget explicitly and set granular `httpx.Timeout(connect=…, read=…, write=…, pool=…)`, or release the caller at the deadline without waiting on the orphan thread (`asyncio.wait({task}, timeout=…)` with `FIRST_COMPLETED`, abandon the straggler), or move to the SDK's async client. Done-when should assert the measured `duration` in `log_llm_batch_summary` is ≈ budget+grace, not the provider's eventual return time.

**`BaseException` typing import — would break the module if executed as written.** `BaseException` is a builtin, not a `typing` export; `from typing import ..., BaseException` raises `ImportError` at import time. `classify_provider_balance_refusal(exc: BaseException)` already annotates exactly this way with no import. Delete the step.

**discuss — the timeout classifier may miss the exception that actually caused the blank `error=`.** `classify_provider_call_timeout` matched `isinstance(exc, TimeoutError)` plus an exact-leaf-name allowlist. A timeout surfaced wrapped (e.g. `anthropic.APIConnectionError` carrying `httpx.ReadTimeout` as `__cause__`) has `type(exc).__name__ == "APIConnectionError"` — not in the allowlist, not a `TimeoutError` — so it falls through to the balance-refusal branch and back to `error=str(e)`. Consider walking `__cause__` / `__context__`, and either way guard that a failure return never carries an empty `error` regardless of classification.

**acceptable** — The 10-minute budget itself is Archie-answered, not in question; worth confirming that with retries bounded, worst-case hop latency stays under `dispatch_timeout_seconds` (3600s).

Joan's overall assessment: config block correctly shaped and placed; removing the `5 * 60` hardcode satisfies §1.4; shared classify/message helpers in `llm_external` satisfy DRY and the core-vs-external bright line; leaving `src/core/agent.py` alone is correct for in-scope-only. Conf `high` was the one point Joan flagged as needing softening — it rested on "budget already exists," and that existing budget is precisely what the 1425.7s log shows to be unenforced.

**Ada's round=1 reply (revised plan):**
1. **AC1 timing** — agreed; replaced `asyncio.wait_for(to_thread…)` with `await_provider_call_with_budget` (`asyncio.wait` + abandon pending task) so the caller returns at budget+grace without awaiting the uncancellable worker. Companion: config `max_retries: 0` so the orphan is one attempt, not SDK-default three. Stage 3 Done-when asserts logged `duration` ≈ 610s.
2. **`BaseException` typing import** — deleted.
3. **discuss classifier / blank error** — classifier now walks `__cause__` / `__context__`. All touched failure returns use `non_empty_provider_error` (fallback `type(e).__name__`) so `error` is never `""`.
4. **acceptable dispatch ceiling** — noted: 610s × one attempt stays under `dispatch_timeout_seconds` 3600.

Conf softened `high` → `Medium`.

#### Plan Approved — Joan round=1

Both round=1 fix-nows cleared: **AC1 timing** — `await_provider_call_with_budget` uses `asyncio.wait({task}, timeout=...)` and returns without cancelling or awaiting the pending task, then raises `TimeoutError(provider_call_timeout_error_message())` — genuinely releasing the caller at ~610s while the worker thread finishes on its own time, with `max_retries: 0` keeping the abandoned attempt singular. **`BaseException` import** — resolved by deleting the step. **Classifier / blank error** (was discuss) — resolved beyond what was asked: cause/context walk with an `id()` cycle guard covers the wrapped-exception shape, and `non_empty_provider_error(e, fallback=type(e).__name__)` on every touched failure return makes "never blank `error=`" an invariant.

**Findings:**
- `discuss` — the abandoned task's outcome is never retrieved. After `asyncio.wait` times out, the pending task is dropped with no reference kept; when it eventually raises, asyncio logs `Task exception was never retrieved` at GC time with no `batch_id` context, minutes after the failure was already reported — an unforced ambiguity on an epic whose whole point is operator clarity. A `task.add_done_callback(...)` that consumes (and optionally debug-logs) the orphan's result would close it. Related: `_get_client` builds a fresh `Anthropic(...)` per call in both externals, so each abandoned call also holds its client/connection until the thread ends — fine at current volume, but worth knowing under a run of consecutive timeouts.
- `discuss` — `max_retries: 0` trades away transient-error resilience, and no longer has to. Once the caller is released at 610s unconditionally, `max_retries` no longer affects AC1 at all — it only governs how much work the orphan does. Neither external has any 429/rate-limit handling of its own, so the SDK's default two retries were today's entire cushion for a transient 429/5xx; `0` converts every blip into a task failure. `1` would keep one cheap retry while still bounding the orphan — the plan should say which behavior it intends rather than letting `0` read as purely a timeout companion. Not blocking — Archie-visible in config and reversible.
- `acceptable` — `await_provider_call_with_budget` lands in `src/utils/llm_external.py`, so utils now hosts a thread runner; no layer rule is broken (utils imports only asyncio, config, logging) and `llm_external` is the DRY-correct home since both externals consume it.
- `acceptable` — Dispatch ceiling confirmed: 610s caller budget against `dispatch_timeout_seconds` 3600 leaves ample headroom.

#### QA test manifest — Betty

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1189ProviderCallBudgetConfig \
  tests/component/utils/test_llm_external.py::TestAst1189ProviderCallBudgetHelpers \
  tests/component/external/test_deepseek.py::TestAst1189ProviderCallBudgetTimeout \
  tests/component/external/test_anthropic.py::TestAst1189ProviderCallBudgetTimeout \
  -q
```

`PROVIDER_CALL_BUDGET` shape (600s / 10s grace / `max_retries=0` / `provider_call_timeout`); budget readers, cause-chain classify, `non_empty_provider_error`, wall-release `await_provider_call_with_budget`; `TimeoutError` → non-empty budget error + `failure_class` on both externals; ordinary errors omit timeout class; healthy success unchanged. Integration: none — no existing scenario asserts wall budget / `provider_call_timeout`.

#### Radia review — code-rubric.v1, FIX-NOW

**Plan adherence:** Stages 1–3 match the plan's code blocks essentially verbatim — `PROVIDER_CALL_BUDGET` shape, the four `llm_external` helpers, `await_provider_call_with_budget`'s wall-release-without-awaiting-the-orphan design, and the mirrored DeepSeek/Anthropic wiring (client `max_retries`, timeout-vs-balance tagging, never-empty `error`) all land as specified. `src/core/agent.py` is untouched, honoring the stated boundary.

**fix-now — cross-ticket test/doc contamination breaks this publish ref's own test tree.** `merge-tests(AST-1189): origin/tests 886b1033` stacks on `748a5725 test(AST-1190): hollow provider response + blank error= coverage` as an ancestor on the shared `origin/tests` branch, and `docs/features/artifacts/ast-1190-empty-unusable-provider-response-surfacing.md` (added earlier in this branch's own history) survives a `347bf506` attempt to drop it. Confirmed by running the touched test files against this tip in a fresh venv: **9 failing tests** — `TestAst1190DoTaskEmptyProviderError` x2, `TestAst1190EmptyUnusableProviderResponse` (both `test_anthropic.py`/`test_deepseek.py`), `TestAst1190ProviderEmptyResponseConfig`, `TestAst1190EmptyResponseHelpers` x5 — all `ImportError`/`AttributeError` on `PROVIDER_EMPTY_RESPONSE`, `normalize_provider_error`, `is_unusable_provider_response`, none of which exist on this tip (that product surface lives on AST-1190's own branch only). "Tests Passed" on this ticket does not reflect this publish ref actually being green standalone. Fix: re-cut `merge-tests` with a Betty SHA scoped to AST-1189 only, and drop the leftover `ast-1190-*.md` plan file from this branch.

**advisory** — `astral.standards.debug-contract-gated` mechanically in-scope, content benign: the diff touches `emit_llm_call_debug(..., error=err, ...)` call sites in both externals, but only the `error=` value changed — no new debug capability or ungating.

**What's solid:** `PROVIDER_CALL_BUDGET`, the wall-budget release design, and the mirrored DeepSeek/Anthropic wiring are clean, DRY, and layer-correct. Never-empty `error` guarantee enforced consistently on every touched failure path in both externals.

**Contamination episode and cleanup (process detail, condensed):** the shared epic worktree let AST-1190's `748a5725` test commit and its `ast-1190-*.md` plan doc land as ancestors on AST-1189's own sub-branch mid-build. Ada flagged Radia's fix-now to Betty (`[qa-handoff]`); Betty re-cut `merge-tests(AST-1189): origin/tests 08675910` scoped to AST-1189-only (`748a5725` no longer an ancestor, `TestAst1190*` gone from the tip, verified 12 passed narrowed-suite). Ada then merged `origin/ftr` product (carrying AST-1189+AST-1190 together) and `origin/dev`, and Betty republished a union bible/test commit (`aefa0efe7`) so the eventual `ftr` merge carries both siblings' coverage — the blank `TimeoutError` on that merged product is tagged `provider_call_timeout` per AST-1189, and AST-1190 asserts expecting no `failure_class` on that path were superseded accordingly.

#### Resolution (2026-08-05)

| Finding | Action |
|---------|--------|
| leftover `docs/features/artifacts/ast-1190-empty-unusable-provider-response-surfacing.md` on this branch | **Done (engineer):** removed |
| `merge-tests(AST-1189)` stacked on `748a5725 test(AST-1190)` | **Done (Betty):** re-cut `merge-tests(AST-1189): origin/tests 08675910` — `748a5725` not an ancestor; `TestAst1190*` gone from tip |
| advisory debug-contract touch (`error=` value only) | Accepted — no product change |

**Verify (Ada):** Betty's narrowed AST-1189 node IDs — **12 passed** on tip after re-cut. Publish ref green standalone.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/utils/config.py` | `PROVIDER_CALL_BUDGET` (600s/10s grace/`max_retries: 0`/failure_class/error template/exception names) | `d41b16c7b` — +23 |
| ✓ | `src/utils/llm_external.py` | Budget readers; cause-chain timeout classifier; non-empty error helpers; `await_provider_call_with_budget` | `6d650feb1` — +63/-2 |
| ✓ | `src/external/deepseek.py` | Drop `_API_CALL_TIMEOUT`; config httpx timeout + `max_retries`; `await_provider_call_with_budget`; timeout/balance tagging | `663f6a07e` — combined commit, +96/-39 net across both externals |
| ✓ | `src/external/anthropic.py` | Same as DeepSeek | `663f6a07e` — see above |
| | _tests_ | budget config / helpers / timeout classify on both externals | `886b10336` initial, re-cut scoped `086759101` after contamination fix; union with AST-1190 at `aefa0efe7` for ftr merge |

### AST-1190 — Empty / unusable provider response surfacing
_Archived: 2026-08-07 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1190/empty-unusable-provider-response-surfacing-anticipate-scan-jobs · Status at archive: Archive · Project: Astral Artifacts · Assignee: hedy · Priority / estimate: None / — · Blocked by / blocks / related: parent: AST-1164; blocks: AST-1191_

#### What this implements

When the provider returns `stop=?` / zero tokens / no usable content, fail `do_task` with a non-empty error (never blank `error=`) and do not log that outcome as a healthy LLM summary. Does **not** own timeout budget (sibling AST-1189).

#### Acceptance criteria

- [X] A provider outcome that yields `stop=?` and zero in/out tokens with no usable content causes `do_task` to return failure with a non-empty error string visible in the `provider call failed … error=` log line.
- [X] A healthy DeepSeek (or mirrored Anthropic) response with normal stop reason and token counts still completes `anticipate_scan` successfully when prompt context is otherwise valid.

#### Boundaries

Does not own provider call time budget / timeout failure class (Ada sibling AST-1189 — `provider_call_timeout`). Does not own artifact hop batch release / error-state / debug trail (Katherine sibling AST-1191). Does not fix hollow name/ANALYSIS tokens (AST-1163).

#### In scope / considered but excluded

In scope: `astral.agent.do-task-delegation` (hollow classification at external `send_to_*`; core only coerces blank `error=` for log/return); `astral.standards.logging-via-utils` (`log_llm_batch_summary` ERROR path for provided empty `error`; `do_task` provider-failed ERROR line); `astral.patterns.coat-check-never-store-empty` (do not treat empty/unusable provider payloads as successful hop output); `astral.standards.dry-and-focused-functions` (shared hollow predicate + error normalize in `llm_external`); `astral.config.config-source-of-truth` (`PROVIDER_EMPTY_RESPONSE` owns `failure_class` + canonical error string); `astral.layers.core-vs-external-bright-line` (provider I/O classification stays in external); `astral.standards.in-scope-only`; `astral.standards.no-cross-contamination` (no sibling plan files or timeout ownership on this publish ref).

Considered but excluded: `astral.batch.claim-process-release` / `astral.batch.batch-id-first` (AST-1191 hop release); `astral.dispatch.run-next-is-chain-authority` (chain topology untouched); `astral.standards.debug-contract-gated` (full found/recorded trail is AST-1191; this ticket only adds a small `do_task` debug_detail when tagged); `astral.standards.data-raises-caller-logs` (no data-layer changes); `pattern.config.config-block` for call budget (AST-1189 `PROVIDER_CALL_BUDGET`).

#### Notes for planning

Shares provider path with Ada AST-1189; vocabulary: `provider_empty_response` (this) vs `provider_call_timeout` (1189) vs shipped `provider_balance_refusal` / `max_tokens`. A sibling AST-1189 plan file accidentally landed on this ref during a shared-worktree race and was removed in a follow-up plan commit (`347bf506`).

#### Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `PROVIDER_EMPTY_RESPONSE` block (`failure_class` + canonical error string) | utils |
| `src/utils/llm_external.py` | Add hollow-response predicate + `is_provider_empty_response`; shared non-empty error normalize helper | utils |
| `src/utils/logging.py` | `log_llm_batch_summary`: never treat a provided empty/whitespace `error` as a healthy response summary | utils |
| `src/external/deepseek.py` | Detect hollow response before healthy INFO summary; normalize blank exception errors; tag `failure_class` | external |
| `src/external/anthropic.py` | Mirror DeepSeek hollow + blank-error handling | external |
| `src/core/agent.py` | Guarantee non-empty `error=` on `provider call failed` log / return; debug detail when empty-response tagged | core |

**Sibling vocabulary (coordinate, do not own):** `provider_call_timeout` (AST-1189, over per-call budget) · `provider_empty_response` (this ticket, hollow/unusable response + blank-error/fake-healthy-summary surfacing) · `provider_balance_refusal` (shipped AST-897) · `max_tokens` (shipped AST-903). Overlap note: AST-1189 already normalizes blank `TimeoutError` on the timeout path; this ticket still owns (1) hollow-response fail-closed before a healthy LLM INFO line, (2) `log_llm_batch_summary` never treating `error=""` as healthy, (3) `do_task` non-empty `error=` coerce for any remaining blank provider failure — normalize is applied to the exception, then Ada's timeout branch (if present) takes precedence when both land on ftr.

#### Diagnosis (Joan's plan-review verification)

Confirmed exactly in tree: `src/utils/logging.py:169` was `if error:` — truthiness, not `is not None`. With `str(TimeoutError()) == ""` and `response=None`, control falls to the INFO branch, where `stop` defaults to `"?"` and both token counts default to `0` — reproducing Susan's pasted `stop=? tokens in=0 out=0` line followed by blank `error=` from `agent.py:2208`. Provider token-sense asymmetry is correct in the plan: `deepseek.py` sets `input_total = cache_miss` and `input_cached = cache_read` (summing both is required, or a cache-heavy response looks zero-token), while `anthropic.py` sets `input_total = usage.input_tokens` directly (summing there would double-count) — each branch matches what its own log line's `in=` actually reports. Layer placement follows shipped precedent: `classify_provider_balance_refusal` / `is_provider_balance_refusal` / `extract_api_response_text` already live in `llm_external.py` (AST-897). Hollowness gate is narrow by construction — `stop_missing` **and** `zero_tokens` **and** `no_content`, so a real response with a genuine stop reason and content cannot be caught even on an odd token shape.

#### Plan Approved — Joan

**Findings:**
- `discuss` — merge-time DRY with sibling AST-1189. Both plans edit the same inner/outer `except Exception as e` returns in `deepseek.py` and `anthropic.py`. This plan's prose precedence ("do not overwrite a non-empty error Ada already assigned") is the right call for authorship, but the ftr rollup should converge on this ticket's single `normalize_provider_error` helper rather than carrying two blank-error normalizers on the same path. Flagging for merge-child / Radia, not blocking this plan.
- `acceptable` — Stage 2 step 2 relocates an existing call, not just adds one: in `deepseek.py` the healthy `log_llm_batch_summary` currently sits above `_timesheet_kwargs` / `timesheet`; `anthropic.py` has the same shape. The plan's stated order ("compute usage → build timesheet + kwargs → hollow check → else healthy summary") resolves this determinately — the engineer should expect to move that log call, and Betty should expect the healthy-summary line to shift position.
- `acceptable` — Child AC checkbox numbering inherits parent numbers: child checkbox 2 = parent AC2, child checkbox 3 = parent **AC5**. Downstream readers should not read child checkbox 3 as parent AC3 (that is Katherine's AST-1191 batch-release criterion).

Cross-contamination cleared and verified: commit `347bf506` removed the sibling AST-1189 plan file that raced onto this ref — this ref now carries only the `ast-1190-…md` doc, and the diff vs `origin/ftr` is that one doc file with zero `src/` changes.

#### QA test manifest — Betty

**Product bug caught pre-review:** Stage 2 uses `is_unusable_provider_response`, `normalize_provider_error`, and `PROVIDER_EMPTY_RESPONSE` in `src/external/deepseek.py` and `src/external/anthropic.py` but never imports them — manifest lines 4–5 failed with `NameError` on the publish tip (Stage 1 helpers + Stage 3 `do_task` coerce were green, 12/18). Betty asked for the three names to be imported in both external modules (mirror AST-897 balance-refusal import style); Hedy fixed it (`0f4469e1`) and the full manifest went green — **18 passed**.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1190ProviderEmptyResponseConfig \
  tests/component/utils/test_llm_external.py::TestAst1190EmptyResponseHelpers \
  tests/component/utils/test_logging_batch.py \
  tests/component/external/test_deepseek.py::TestAst1190EmptyUnusableProviderResponse \
  tests/component/external/test_anthropic.py::TestAst1190EmptyUnusableProviderResponse \
  tests/component/core/test_agent.py::TestAst1190DoTaskEmptyProviderError \
  -q
```

#### Radia review — code-rubric.v1, DISCUSS

**Plan adherence:** Stage 1–3 all landed exactly per the combined plan: `PROVIDER_EMPTY_RESPONSE` config block mirrors `PROVIDER_BALANCE_REFUSAL`; the three `llm_external.py` helpers are shared with no cross-external import; `log_llm_batch_summary` now branches on `error is not None` instead of truthiness. Hollow-response gate sits after timesheet-kwargs build and before the healthy summary call in both externals, matching Stage 2's required ordering exactly. `do_task` coercion is defense-in-depth only. Confirmed isolated from sibling AST-1189 (branch still runs pre-budget `asyncio.wait_for` timeout, no `provider_call_timeout` vocabulary) and AST-1191 (no hop/release topology touched).

**discuss:** Commit `0f4469e1` (`test(AST-1190): import hollow-response helpers in provider clients`) touches only `src/external/anthropic.py` + `src/external/deepseek.py` — a pure product-code import fixup, not a test-tree change — but carries the `test(...)` commit-vocabulary prefix instead of `code(...)`. Not fix-now: already pushed, and correcting it would need rebase/force-push (both banned). Flagging for the next post-merge-tests fixup on this lineage to use `code(...)`.

**What's solid:** blank-`TimeoutError` → fake-healthy-INFO bug is fixed at its root (`error is not None`); AC5 healthy path (`end_turn`, real tokens) verified still returns `success=True` in both provider test suites; git separation is clean (`code()` commits touch only `src/`, Betty's `test()` + `merge-tests()` touch only `tests/`+`docs/test-bible/`).

#### Resolution (2026-08-05)

DISCUSS — no fix-now; Frame diff none.

| Item | Action |
|------|--------|
| discuss — `0f4469e1` used `test(AST-1190):` for a pure product import fixup | Accepted; no rewrite (rebase/force-push banned). Future post-merge-tests product fixups on this lineage use `code(...)`. No product change this pass. |

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/utils/config.py` + `src/utils/llm_external.py` + `src/utils/logging.py` | `PROVIDER_EMPTY_RESPONSE` block; hollow-response predicate + `is_provider_empty_response`; shared error normalize; `log_llm_batch_summary` `is not None` fix | `c3a39ddf4` — +56/-3 across three files |
| ✓ | `src/external/deepseek.py` + `src/external/anthropic.py` | Hollow gate before healthy INFO summary; normalize blank exception errors; tag `failure_class` | `968a3a7cc` — +172/-63 across both files |
| ✓ | `src/core/agent.py` | Non-empty `error=` guarantee on `provider call failed`; debug detail when empty-response tagged | `597a41d9b` — +17/-2 |
| | _tests_ | hollow provider response + blank error= coverage | `748a57252`; import fixup `0f4469e17`; bible per Betty manifest |

### AST-1191 — Artifact hop failure release + debug trail
_Archived: 2026-08-07 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1191/artifact-hop-failure-release-debug-trail-anticipate-scan-jobs-failing · Status at archive: Archive · Project: Astral Artifacts · Assignee: katherine · Priority / estimate: None / — · Blocked by / blocks / related: parent: AST-1164_

#### What this implements

After siblings #1 and #2: on provider failure for `anticipate_scan` / shared artifact hops, ensure batch release + configured error/hold state, and AST-538-style debug found/recorded for UAT. Does **not** redesign LLM adapters beyond consuming their structured failures.

#### Acceptance criteria

- [X] After such a failure on `anticipate_scan`, the job is not left batch-claimed; it is on the configured artifact error/hold state for that task, and the failure reason is visible against that `batch_id` in Execution History / app_log.
- [X] A debug-gated run of the fixed path shows found/recorded lines for duration, stop, tokens, and error/failure class on the failed call.

#### Boundaries

Does not own provider call time budget / timeout failure class (Ada sibling AST-1189). Does not own empty/unusable provider response classification (Hedy sibling AST-1190). Does not fix hollow name/ANALYSIS tokens (AST-1163). Does not redesign LLM adapters beyond consuming structured failures from #1/#2.

#### In scope / considered but excluded

In scope: `pattern.batch.entity-claim-process-release` (provider failure still claim/process/release; no orphaned `batch_id` on the job); `astral.batch.claim-process-release` (transition to `error_state` then `release_job_dispatch_claim` while history can still see `batch_id`); `astral.dispatch.run-next-is-chain-authority` (consume hop failure inside existing `do_task` / dispatch-chain path; no `run_next` topology change); `astral.standards.debug-contract-gated` (found/recorded duration/stop/tokens/failure_class only when `debug=True`); `astral.agent.do-task-delegation` (core consumes structured `error`/`failure_class`/`timesheet` from external; no adapter redesign); `astral.standards.in-scope-only`; `astral.standards.logging-via-utils`; `astral.standards.dry-and-focused-functions` (one helper owns apply error_state + release).

Considered but excluded: `pattern.config.config-block` / `PROVIDER_CALL_BUDGET` (AST-1189); `astral.patterns.coat-check-never-store-empty` / hollow predicate (AST-1190); `astral.layers.core-vs-external-bright-line` edits in `src/external/**` (adapters untouched this ticket); `astral.standards.data-raises-caller-logs` (no `src/data/**` changes); `src/ui/**` (no Generate Artifacts chrome changes); AST-1163 name/ANALYSIS token context (separate epic).

#### Notes for planning

After AST-1189 and AST-1190 (both User Testing). Gap today: `_apply_dispatch_chain_hop_failure` only hard-fails on missing job/candidate strings, so provider failures leave the job in `BUILD_ARTIFACTS` after claim clear.

#### Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/agent.py` | Expand `_apply_dispatch_chain_hop_failure` for provider failures (error_state + claim release); wire provider-failed `_close_hop_ledger` with `failure_class`; add debug found/recorded lines on that path | core |

**Not in scope:** `src/external/{deepseek,anthropic}.py` / timeout budget (AST-1189); hollow-response classification (AST-1190); `run_next` / BUILD_ARTIFACTS hop topology; AST-1163 name/ANALYSIS tokens; UI; `src/data/**`.

#### Plan-discuss round=1 — Joan REVISE

**fix-now — Stage 2 reads timesheet keys that do not exist, and its fallback prints the epic's own symptom.** Stage 2 step 1 said: "prefer timesheet keys already used by externals (`input_tokens` / `output_tokens` / cache fields if present on `ts`); if absent, use `0`." The externals do not emit those keys — both providers build `{"calltime", "duration", "inputtotal", "inputcached", "outputtotal", "cache_creation_tokens"}` (including on the failure-path `_empty_timesheet`). `input_tokens` / `output_tokens` are never present, so the "if absent, use 0" clause fires every time and the found line always reads `tokens_in=0 tokens_out=0` — the exact string the parent Purpose holds up as the mystery to be eliminated, now printed by the very debug line AC4 adds to explain the failure. It is not academic on two failure classes Stage 1's Decision explicitly routes through this path: **max_tokens** returns the real timesheet with genuine counts (`outputtotal` is by definition at the cap — the whole explanation of the failure) and would report zero; **hollow response** (AST-1190) returns real counts behind an unusable payload and would also report zero. Timeout failures do carry genuine zeros, so those stay accurate either way. **Recommendation:** name the real keys and drop the silent `0` default in favour of `n/a` when a key is genuinely missing, mirroring the shape `emit_llm_call_debug` already uses (`tokens fresh=… cache_read=… cache_write=… output=…`).

**discuss — Stage 1 and Stage 2 disagree on the `_close_hop_ledger` signature.** Stage 1 step 6 wrote it as `-> None`; Stage 2 then required threading a return dict through it. Reconcile in Stage 1.

**acceptable** — the second claim release inside `_apply_dispatch_chain_hop_failure` is genuinely redundant with the existing consult release (`consult.py:2287`); both funnel to `database.clear_job_batch_lock`, so the dual clear is idempotent exactly as the plan claims — recording it as a decision rather than something Radia rediscovers.

**acceptable** — the hard-string gate (`"Job not found"` / `"Missing candidate_data"`) survives as literal substring matching; pre-existing, `in-scope-only` argues for leaving it alone.

Verification notes Joan recorded as clean: `ERROR_BUILD_ARTIFACTS` (`prior_states: [BUILD_ARTIFACTS]`) accepts runtime hop labels because `_job_state_matches_prior` normalizes them back to base state, so the transition is valid for `anticipate_scan` and sibling artifact hops; `transition_job_state` stamps `batch_id` into `state_history`, so transitioning before releasing the claim is what makes AC3's visibility claim true, not incidental; `_empty_timesheet()` computes real elapsed seconds so `duration` survives the timeout path; `is_provider_balance_refusal` is already imported and works as written.

**Katherine's round=1 reply:** Stage 2 now reads the real external keys (`inputtotal`, `inputcached`, `outputtotal`, `cache_creation_tokens`); missing keys render as `n/a`, never a silent `0`; found line uses the `tokens fresh=… cache_read=… cache_write=… output=…` vocabulary. Stage 1 now has both helpers return `{"apply_error_state", "error_state", "batch_released"}` (including early no-op) so Stage 2 only consumes — no signature rewrite across stages. Dual release left as a recorded Decision (defense in depth).

#### Plan-discuss round=2 — Joan REVISE (genuine crash bug caught before build)

**fix-now — Stage 1 step 7 leaves `_close_hop_ledger` returning `None` on its early exit, and Stage 2 subscripts that return unconditionally.** The revised Stage 1 step 7 said to run "the existing hop-ledger finalize / `clear_log` logic unchanged," then `return outcome` — but the existing logic contains a bare early return: `if hop_ledger_closed or not hop_ledger_batch_id: return`. Left unchanged, that path returns `None`. Stage 2 step 2 then does `hop_fail_outcome["apply_error_state"]` / `["error_state"]` with no guard, so a debug-gated provider failure on that path raises `TypeError: 'NoneType' object is not subscriptable` inside `do_task`. The early exit is the **common** case, not an edge — `hop_ledger_batch_id` is only assigned when `in_chain and candidate_id`, so it is `None` for every non-chain `do_task` call (out of scope, `no-cross-contamination` territory) **and** for dispatch-chain hops whose company row carries no `candidate_id` (which already logs "run_next chain hop without astral_candidate_id — no hop ledger"). That second case reproduces the epic's own bug: `_run_dispatch_chain_job_batch` awaits `do_task` with no `try` around it and releases the claim only after checking `result.get("success")` — an exception out of `do_task` skips that release and aborts the batch loop, leaving the job batch-claimed in `BUILD_ARTIFACTS`, exactly the state AC3 exists to prevent, now reachable through the debug trail AC4 adds. Same defect class as round=1 finding 2 (`_HOP_FAILURE_NOOP` returned from every exit) but not carried across to `_close_hop_ledger`. **Recommendation:** `_close_hop_ledger` returns `outcome` from every exit including the early return (mirroring `_HOP_FAILURE_NOOP`), and — belt and braces since Stage 2 is a separate commit — Stage 2 reads `(hop_fail_outcome or _HOP_FAILURE_NOOP)`.

**acceptable** — `_ts_num` uses `isinstance(v, (int, float))`, which admits `bool`; no external path puts a bool in those keys today, note only.

Round=1 items reverified closed in this pass (timesheet keys, signature contradiction, dual-release harmlessness).

**Katherine's round=2 reply:** Stage 1 step 7 now spells the full body — the `hop_ledger_closed or not hop_ledger_batch_id` path is `return outcome`, never bare `return`. Stage 2 step 2 normalizes `hop_fail_outcome = hop_fail_outcome or _HOP_FAILURE_NOOP` before any key access as a belt-and-braces second layer.

#### Plan Approved — Joan (round=2 verified closed)

Diffed the full `_close_hop_ledger` body Katherine spelled out against the real function line for line: `nonlocal hop_ledger_closed`, the `_apply_dispatch_chain_hop_failure` kwargs, the `_finalize_run_next_hop_ledger` call, the `hop_ledger_closed = True` flag, and the `clear_log` guard are all reproduced exactly — nothing dropped, nothing invented. The early exit is `return outcome` with a comment naming why, so a future reader does not "simplify" it back to a bare `return`. Stage 2's normalize line means even a slip in Stage 1 cannot `TypeError` out of `do_task` and skip consult's claim release — both halves of the recommendation landed, closing the AC3-regress path twice over.

**Findings (all acceptable):**
1. Stage 2's normalize aliases the module-level `_HOP_FAILURE_NOOP` rather than copying it; only read for display fields, never mutated — no shared-state hazard, noting so nobody later adds a mutation on top of the alias.
2. `_ts_num`'s bool-admitting `isinstance` check — carried forward, still a note only.
3. Dual claim release (helper + consult batch runner) reconfirmed idempotent this pass: `tracker.release_job_dispatch_claim` delegates straight to `database.clear_job_batch_lock`, and consult's failure branch releases without transitioning state, so the clear cannot collide with the new `ERROR_BUILD_ARTIFACTS` transition or trip `prior_states`.
4. Pre-existing hard-string gate survival — noted so its retention is not read as an endorsement.

**Closing verification:** debug contract holds Style D (found/recorded `debug_detail` lines under a real index header, no new ungated `logger.info`); AC4 field coverage confirmed (found: duration, stop, real token keys, failure_class; recorded: non-empty error, error_state applied-or-`held`, batch_released); AC3 ordering confirmed (transition before release keeps `batch_id` in `state_history`; existing ERROR line still fires before `log_batch_id` is cleared); boundaries confirmed (single core file, no external/data/UI/topology edits). No fix-now outstanding — **Plan Approved** after 2 discuss rounds.

#### QA test manifest — Betty

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst1191ArtifactHopFailureRelease \
  tests/component/core/test_agent.py::TestAst848DispatchChainDoTask::test_hard_failure_transitions_error_build_artifacts
```

Provider fail → `error_state` + `release_job_dispatch_claim`; balance hold skips transition but still releases; non-dispatch → `_HOP_FAILURE_NOOP`; `anticipate_scan` timeout → `ERROR_BUILD_ARTIFACTS` + claim release; `debug=True` found (duration/stop/tokens/`failure_class`) + recorded (error / error_state|held / batch_released), `debug=False` quiet; existing `TestAst848` hard-string path still transitions and now also asserts claim release. Smoke on publish tip: 7 passed.

#### Radia review — code-rubric.v1, CLEAN

Isolated this ticket's own contribution via `git diff ee5e760f..5c6cdcda` (the tip AST-1189 left for merge-child) rather than the full three-dot diff, since the latter also carries already-reviewed AST-1189/AST-1190 product code stacked via `ftr`. AST-1191's own footprint is exactly `src/core/agent.py` (105 lines) + plan doc + test-bible + tests — matching the Files Changed table with no scope creep. Both Joan revision rounds honored: `_apply_dispatch_chain_hop_failure` and `_close_hop_ledger` return the outcome dict from every exit (including the no-op / no-ledger early returns — no bare `return None` regression), balance-refusal still holds state while releasing the claim, transition happens before release, and Stage 2's found/recorded lines read the real timesheet keys with honest `n/a` on missing keys.

Verified `clear_job_batch_lock` is a plain `UPDATE ... SET batch_id = NULL` — confirms the plan's "dual clear is idempotent" claim. Ran the ticket's own test class plus the adjacent `TestAst848DispatchChainDoTask` regression test in a fresh venv: **11/11 pass**. The broader touched-file test run surfaces ~30 pre-existing failures (statute-count fixture drift, shared sqlite db schema state, unrelated in-flight epics) — none in `TestAst1191*` or `TestAst848*`, confirmed against an `origin/dev` baseline showing the same failure classes already present, not diff-caused.

**Findings:** none (fix-now / discuss). No repeat of AST-1189's cross-ticket merge-tests contamination — this branch's `merge-tests(AST-1191)` diff is a clean, isolated 2-file/240-line addition (own test-bible + test file only).

**What's solid:** outcome-dict threading correct on every exit path (verified against both Joan revision concerns); debug found/recorded gating correct (`found` inside the existing `if debug:` block, `recorded` gated separately after `_close_hop_ledger`, `debug=False` emits neither, test-covered); `astral.batch.claim-process-release`, `astral.state.core-decides-transitions`, `astral.state.job-prior-states-enforced` all conform.

#### Resolution (2026-08-06)

CLEAN — no fix-now / discuss. No product change this pass.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/core/agent.py` | `_apply_dispatch_chain_hop_failure` error_state + claim release, outcome dict from every exit; provider-failed `_close_hop_ledger` wiring with `failure_class`; debug found/recorded | `7f5b132e6` (Stage 1, +53/-10) + `3aa816f3e` (Stage 2, +42) |
| | _tests_ | hop failure claim release + debug trail coverage | `aa3b3023d`; bible `docs/test-bible/core/agent.md` @ `9b9501dfe578df7e9c8b5f4108ff62df2848450d` |
