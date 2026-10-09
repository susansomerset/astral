# AST-1959 — Per-batch probe and host lock on the OpenRouter path

- **Parent:** [AST-1954 — Add host-discovery probe ahead of warm/gather; pin the batch to one provider](https://linear.app/astralcareermatch/issue/AST-1954)
- **Ticket:** [AST-1959](https://linear.app/astralcareermatch/issue/AST-1959)
- **Publish ref:** `sub/AST-1954/AST-1959-probe-host-lock` (origin only)
- **Built on:** `origin/dev` @ `66d98fa7b` (AST-1953 landed: agent provider object merged in `llm_compat`)

On a server whose `LLM_SERVER_CONFIG` probe flag is on (OpenRouter only), when `log_batch_id` is set, the
first `send_to_llm_compat` call for a given (batch id, request arguments minus content and system) key sends
one cheap **probe** first. The probe is the real call's request with the content swapped for a fixed probe
message and the system block dropped, so OpenRouter filters eligible hosts on the same `max_tokens`,
temperature/effort and provider object. The response's `provider` becomes the batch's host, and every real
call for that key, the warm call included, sends `provider.only = [host]`. Concurrent first callers wait on
the one probe. A failed probe is remembered for the key: every call for it returns an ordinary failure with
no request sent, which puts the entity on `patt.task.dispatch-retry`. Every `llm_compat` result also carries
`host` (the response's `provider`, else the server label), and the per-call INFO line names it. The ledger
write is AST-1960 (Katherine), and `dispatcher.py` does not change.

## Canon (this ticket's Citations)

| Id | How this plan honours it |
|----|--------------------------|
| `patt.entity.batch-processing` | The host map key is the claim's own `batch_id`, read from the `log_batch_id` contextvar that the dispatcher already sets. No new batch identity is minted, and the map does not touch claim or release. |
| `patt.task.dispatch-retry` | A failed probe (exception or no `provider`), and any later call for that key, returns the ordinary `{"success": False, ...}` result. The caller's existing retry → error routing handles it, and no bespoke retry is added here. |
| `stat.logging.debug` | Ungated `logger.debug` call-in/response-out on the probe, plus one line per host-map decision (hit, probe owner, waiter, remembered failure). Nothing is truncated. |
| `stat.logging.info` | The served host extends the existing `log_llm_batch_summary` INFO line, which stays one line per call. No second INFO line. |

## Files Changed (planned)

Every row is named in this ticket's `## Scope`. Tests and bibles are Betty's (`qa-child`); the engineer does not touch `tests/` or `docs/test-bible/`.

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `probe` bool on every `LLM_SERVER_CONFIG` entry (true on `openrouter` only); new `LLM_PROBE_MESSAGE` constant; validator checks `probe` is a bool | utils |
| `src/utils/logging.py` | `log_llm_batch_summary` gains an optional `host` kwarg; when it is given, the INFO line carries `host=<host>` | utils |
| `src/external/openrouter.py` | **New.** `probe_host` (the probe request) and `get_batch_host` (the per-batch single-flight host map) | external |
| `src/external/llm_compat.py` | `send_to_llm_compat`: probe/lock before the real call, early failure on a remembered probe failure, `host` on every result, host passed to the INFO summary | external |

## Stage 1: Config probe flag, probe message, and host on the INFO line

**Done when:** `LLM_SERVER_CONFIG["openrouter"]["probe"] is True`, every other server has `"probe": False`, `validate_llm_provider_environment()` raises when an entry's `probe` is missing or not a bool, and `log_llm_batch_summary(..., response=r, host="DeepInfra")` emits one INFO line containing `host=DeepInfra`. With no `host` argument the line is byte-for-byte what it is today.

1. In `src/utils/config.py`, in the `LLM_SERVER_CONFIG` header comment block (the `#   concurrency …` line is the last field line), add this field line directly after the `#   concurrency` line:
   ```python
   #   probe              — True: one host-discovery probe per batch, then the batch is pinned to the
   #                        probe's host (src.external.openrouter, AST-1959). Only OpenRouter routes per call.
   ```
2. In `src/utils/config.py`, add `"probe": False,` as the last key of the `"anthropic"`, `"kimi"` and `"deepseek"` entries (after `"concurrency"`), and `"probe": True,` as the last key of the `"openrouter"` entry (after `"concurrency": None,`).
3. In `src/utils/config.py`, directly after the `LLM_SERVER_AUTH_STYLES = (...)` line, add:
   ```python
   # Probe request content (AST-1959): replaces the real call's content; system block dropped, no cache_control.
   LLM_PROBE_MESSAGE = "Respond with 1."
   ```
   ⚠️ **Decision:** The probe content is the constant alone, with no entity index. The ticket's Scope says "the probe message text" constant, and AC 1 checks for "the probe message as its only content". The parent's "(the index plus 'respond with 1')" is not in this child's Scope. A per-entity index would also make the probe differ per first caller, which buys nothing because one probe serves the whole key.
4. In `src/utils/config.py`, in `validate_llm_provider_environment()`, inside the `for sid, s in LLM_SERVER_CONFIG.items():` loop, after the `anthropic_compat requires base_url` check, add:
   ```python
        if not isinstance(s.get("probe"), bool):
            raise ValueError(f"LLM server {sid!r}: probe must be True or False")
   ```
5. In `src/utils/logging.py`, change `log_llm_batch_summary`:
   - Add a keyword-only parameter `host: Optional[str] = None` after `error: Optional[str] = None`.
   - Leave the `error is not None` WARNING branch exactly as it is.
   - Replace the final `logger.info(...)` call with:
     ```python
     # Served host (AST-1959) rides the same line, never a second one; omitted when the caller has none.
     host_part = f" host={host}" if host else ""
     logger.info(
         "LLM %s%s task=%s %.1fs stop=%s tokens in=%s out=%s",
         provider,
         host_part,
         prompt_label,
         duration,
         stop,
         in_tok,
         out_tok,
     )
     ```
   - Update the docstring to: `"""One INFO/WARNING per LLM call when log_batch_id is set (Execution History / app_log); INFO names the served host when given."""`

   ⚠️ **Decision:** `host` is optional and the segment is omitted when it is absent, so `src/external/anthropic.py`'s six calls (outside this ticket's Scope) keep today's line unchanged. `"LLM <provider>"` stays contiguous, which keeps the existing substring assertions in `test_logging_batch.py` valid.
6. Verify: `python3 -m py_compile src/utils/config.py src/utils/logging.py` and `python3 -c "from src.utils.config import validate_llm_provider_environment as v; v()"` both exit 0.

Commit: `code(AST-1959): stage 1 — server probe flag, probe message, host on INFO line`

## Stage 2: `src/external/openrouter.py` — probe and per-batch host map

**Done when:** `src/external/openrouter.py` imports cleanly and exposes `probe_host` and `get_batch_host`. For one key, N concurrent `get_batch_host` calls run `send` exactly once and all receive the same `(host, None)`. When the probe raises or returns no `provider`, all N receive `(None, <error>)` and a later call with the same key does not call `send` again. `rg -n '"openrouter"' src/external/` returns nothing.

1. Create `src/external/openrouter.py` with exactly this content:

```python
"""OpenRouter host discovery (AST-1959): one probe per batch key, then the batch is pinned to that host.

OpenRouter routes every call on its own and prompt caches live on one host, so a batch whose warm call
and gather calls land on different hosts pays full input on every call. Servers opt in via the
LLM_SERVER_CONFIG `probe` flag; send_to_llm_compat calls get_batch_host only when that flag is on and
log_batch_id is set.
"""

import asyncio
import json
import threading
from concurrent.futures import Future
from typing import Any, Awaitable, Callable, Dict, Optional, Tuple

from src.utils.config import LLM_PROBE_MESSAGE
from src.utils.llm_external import normalize_provider_error
from src.utils.logging import get_logger

__all__ = ["probe_host", "get_batch_host"]

logger = get_logger(__name__)

# (batch_id, request-args json) → Future[(host, error)]. Never evicted: a restart clears it, no cap / TTL.
# concurrent.futures.Future + threading.Lock (not asyncio primitives) because callers may run on
# different event loops / worker threads; asyncio.wrap_future bridges each waiter to its own loop.
_hosts: Dict[Tuple[str, str], Future] = {}
_hosts_lock = threading.Lock()


def _batch_key(batch_id: str, api_kwargs: Dict[str, Any]) -> Tuple[str, str]:
    """Batch id + every request argument except content and system — same settings, same host."""
    rest = {k: v for k, v in api_kwargs.items() if k not in ("messages", "system")}
    return batch_id, json.dumps(rest, sort_keys=True, default=str)


async def probe_host(
    api_kwargs: Dict[str, Any],
    send: Callable[[Dict[str, Any]], Awaitable[Any]],
    record_probe: Callable[[Any], None],
) -> str:
    """Send the real call's request with the probe message as its only content and no system block;
    return the response's `provider`. Raises when the call fails or names no provider."""
    # Content swapped wholesale and system dropped → no cache_control can ride along. Everything else
    # (max_tokens, temperature, effort, agent provider object) is the real call's, so OpenRouter
    # filters eligible hosts exactly as it will for the batch.
    probe_kwargs = {k: v for k, v in api_kwargs.items() if k not in ("messages", "system")}
    probe_kwargs["messages"] = [{"role": "user", "content": [{"type": "text", "text": LLM_PROBE_MESSAGE}]}]
    logger.debug("Calling messages.create (probe): %s", probe_kwargs)
    response = await send(probe_kwargs)
    logger.debug("Response from messages.create (probe): %s", response)
    record_probe(response)
    host = getattr(response, "provider", None)
    if not host:
        raise ValueError("Probe response named no provider")
    return host


async def get_batch_host(
    batch_id: str,
    api_kwargs: Dict[str, Any],
    send: Callable[[Dict[str, Any]], Awaitable[Any]],
    record_probe: Callable[[Any], None],
) -> Tuple[Optional[str], Optional[str]]:
    """(host, None) for the batch key, or (None, error) when its probe failed. Exactly one probe per key:
    the first caller runs it, concurrent and later callers await the same result."""
    key = _batch_key(batch_id, api_kwargs)
    with _hosts_lock:
        fut = _hosts.get(key)
        owner = fut is None
        if owner:
            fut = _hosts[key] = Future()
    if not owner:
        logger.debug("Host map: awaiting probe result for batch=%s", batch_id)
        return await asyncio.wrap_future(fut)
    logger.debug("Host map: probing for batch=%s key=%s", batch_id, key[1])
    try:
        fut.set_result((await probe_host(api_kwargs, send, record_probe), None))
    except Exception as e:
        fut.set_result((None, f"Host probe failed: {normalize_provider_error(e)}"))
    finally:
        # Cancelled owner (caller timeout) must not strand the waiters on a never-resolved future.
        if not fut.done():
            fut.set_result((None, "Host probe failed: probe cancelled"))
    host, err = fut.result()
    logger.debug("Host map: batch=%s host=%s error=%s", batch_id, host, err)
    return host, err
```

   ⚠️ **Decision:** `probe_host` takes a `send` coroutine and a `record_probe(response)` callback, both built by `send_to_llm_compat` over the same client and the caller's `record_timesheet`. This satisfies "sends it through the same client" and "records the probe on the timesheet through the caller's `record_timesheet` callback" without copying `llm_compat`'s cost and timesheet assembly into a second file.

   ⚠️ **Decision:** A missing `provider` on a successful probe response counts as a probe failure (parent Functional scope 3: "errors or returns no `provider`").

   ⚠️ **Decision:** The remembered failure is the single error string `"Host probe failed: <normalized error>"`, so every affected call's WARNING summary says why without a separate tally (`stat.logging.warning`).
2. Verify: `python3 -m py_compile src/external/openrouter.py`, `python3 -c "import src.external.openrouter"` exits 0, and `rg -n '"openrouter"' src/external/` prints nothing.

Commit: `code(AST-1959): stage 2 — openrouter probe and per-batch host map`

## Stage 3: Wire the probe, lock, and host into `send_to_llm_compat`

**Done when:** On a `probe: True` server with `log_batch_id` set, the first call of a key sends the probe and then the real call, and every real call carries `extra_body["provider"]["only"] == [<probe host>]` with the agent's other provider keys unchanged. A remembered probe failure returns `success: False` with no `messages.create`. Servers with `probe: False`, or calls with no batch id, send exactly today's request. Every return dict has a `host` key, and the success INFO line names it. `git diff origin/dev...HEAD --stat -- src/core/dispatcher.py` is empty.

1. In `src/external/llm_compat.py`, add `from src.external.openrouter import get_batch_host` directly below the `from src.external.anthropic import ...` line.
2. In `send_to_llm_compat`, directly after the `if system_blocks: api_kwargs["system"] = system_blocks` lines and **replacing** the `def _make_api_call(): ...` definition, add:

```python
        async def _send(kwargs: Dict[str, Any]) -> Any:
            # One path to the wire for the probe and the real call: same client, same budget, same slots.
            return await await_provider_call_with_budget(
                lambda: _create(client, kwargs, server_id, server["concurrency"]),
                timeout_seconds=provider_call_wait_timeout_seconds(),
            )

        def _timesheet_kwargs_for(response: Any) -> Optional[Dict[str, Any]]:
            # None when cost can't be computed — callers then skip the timesheet row (unchanged behaviour).
            counts = usage_to_token_counts(response.usage)
            try:
                cost_parts = calculate_cost_components_from_counts(
                    counts["cache_read"],
                    counts["cache_miss"],
                    counts["output"],
                    counts["cache_write"],
                    sku=sku,
                    server_id=server_id,
                )
            except Exception:
                return None
            return dict(
                agent_req_id=getattr(response, "id", None),
                task_key_uuid=task_key_uuid,
                model_code=sku,
                candidate_id=candidate_id,
                batch_id=log_batch_id.get(),
                batch_size=batch_size,
                cache_write_tokens=counts["cache_write"],
                cache_read_tokens=counts["cache_read"],
                no_cache_prompt_tokens=no_cache_prompt_tokens,
                no_cache_live_tokens=no_cache_live_tokens,
                total_no_cache_input_tokens=counts["cache_miss"],
                total_output_tokens=counts["output"],
                calc_cost_cache_write=cost_parts["calc_cost_cache_write"],
                calc_cost_cache_read=cost_parts["calc_cost_cache_read"],
                calc_cost_no_cache_input=cost_parts["calc_cost_no_cache_input"],
                calc_cost_output=cost_parts["calc_cost_output"],
                provider=server_id,
            )

        def _record_probe(response: Any) -> None:
            # Probe cost lands on the timesheet like any call; a recording failure never fails the probe.
            if record_timesheet is None:
                return
            try:
                kw = _timesheet_kwargs_for(response)
                if kw is not None:
                    record_timesheet(**kw, agent_performance="success", failure_note=None)
            except Exception:
                pass

        # Host lock (AST-1959): flagged servers only, and only inside a batch (adhoc/workbench never probe).
        batch_id = log_batch_id.get()
        if server["probe"] and batch_id:
            host, probe_err = await get_batch_host(batch_id, api_kwargs, _send, _record_probe)
            if probe_err is not None:
                # No fallback: nothing is sent; the entity takes the ordinary retry → error path.
                duration = (datetime.now() - start_time).total_seconds()
                log_llm_batch_summary(logger, server_id, prompt_label, duration, error=probe_err)
                return {
                    "success": False,
                    "api_response": None,
                    "timesheet": _empty_timesheet(),
                    "error": probe_err,
                    "host": server["label"],
                }
            # New dicts, not in-place edits: the agent's provider keys kept, only `only` replaced.
            extra_body = api_kwargs["extra_body"]
            api_kwargs["extra_body"] = {**extra_body, "provider": {**(extra_body.get("provider") or {}), "only": [host]}}
```

   ⚠️ **Decision:** The host-map key is computed from `api_kwargs` **before** the lock is merged, so the probe and every real call of the batch share one key. The probe therefore carries only the agent's own `only`, if any (AC 2).

   ⚠️ **Decision:** The probe's timesheet row is `agent_performance="success"` with no `failure_note`. The Scope asks only that its cost reach the ledger, and the timesheet has no "probe" column in this ticket's Scope.
3. In the inner `try:` block, replace:
   ```python
            response = await await_provider_call_with_budget(
                _make_api_call,
                timeout_seconds=provider_call_wait_timeout_seconds(),
            )
   ```
   with:
   ```python
            response = await _send(api_kwargs)
   ```
   Keep the `logger.debug("Calling messages.create: ...")` and `logger.debug("Response from messages.create: ...")` lines on either side as they are.
4. Directly after `logger.debug("Response from messages.create: %s", response)`, add:
   ```python
            # Served host: the router's `provider` when present, else this server's own label (AST-1959).
            host = getattr(response, "provider", None) or server["label"]
   ```
5. Replace the block from `try:` / `cost_parts = calculate_cost_components_from_counts(` through `except Exception:` / `_timesheet_kwargs = None` (current lines 149–178) with the single line:
   ```python
            _timesheet_kwargs = _timesheet_kwargs_for(response)
   ```
   Leave `counts = usage_to_token_counts(response.usage)` and the four `input_total` / `input_cached` / `output_total` / `cache_creation_tokens` lines above it unchanged.
6. Change the healthy summary call `log_llm_batch_summary(logger, server_id, prompt_label, duration, response=response)` to pass `host=host`:
   ```python
            log_llm_batch_summary(
                logger, server_id, prompt_label, duration, response=response, host=host
            )
   ```
   Leave every `error=` summary call unchanged.
7. Add `"host": host` as the last key of each of the four return dicts that have a `response`: the hollow-response return (`failure_class: PROVIDER_EMPTY_RESPONSE[...]`), the `max_tokens` truncation return, the parse-error return, and the final success return (`{"success": True, ...}`).
8. In both exception handlers (inner `except Exception as e:` and outer `except Exception as e:`), change the `out = {...}` line to include `"host": server["label"]`:
   ```python
            out = {"success": False, "api_response": None, "timesheet": _empty_timesheet(), "error": err, "host": server["label"]}
   ```
   (The outer handler sits one indentation level shallower and keeps that indentation.)
9. Update the module docstring's last line to: `Parameterized by server id + SKU; key always passed by the caller (no env fallback). Probe-flagged servers lock each batch to one host (AST-1959).`
10. Verify:
    - `python3 -m py_compile src/external/llm_compat.py src/external/openrouter.py`
    - `python3 -c "import src.external.llm_compat"` exits 0
    - `rg -n '"openrouter"' src/external/` prints nothing
    - `git diff origin/dev...HEAD --stat -- src/core/dispatcher.py` prints nothing
    - `python3 -m pytest tests/component/external/test_llm_compat.py tests/component/utils/test_logging_batch.py tests/component/utils/test_config.py -q` passes on the existing (pre-Betty) tests. A failure that comes only from the new `host` key or the `host=` segment is not fixed in `tests/`. Record it for Betty's `qa-child` and stop per the execution contract.

Commit: `code(AST-1959): stage 3 — probe, host lock and served host in send_to_llm_compat`

## Out of scope (do not touch)

- `src/core/agent.py`, `src/data/database.py`, `dispatch_ledger`: AST-1960 (Katherine).
- `src/core/dispatcher.py`: sequencing is unchanged (AC 5).
- `src/external/anthropic.py`: Anthropic-direct gets no probe and keeps its INFO line. AST-1960 uses the server label for its ledger host.
- Slug mapping of `provider` → `only` (Susan's decision; parent UAT AC 7 is the tripwire).
- `tests/**`, `docs/test-bible/**`: Betty.

## Execution contract

Run stages in order and steps in order. Do not add files, helpers or dependencies beyond this doc. If a step is ambiguous, the code has drifted from the line references above, or a verify step fails when executed literally, stop and comment on the parent AST-1954 using the `🛑 Stage N blocked:` format. Each stage ends in one `code(AST-1959): …` commit on the epic worktree, published with `git push origin HEAD:sub/AST-1954/AST-1959-probe-host-lock`.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-1959
**Overall:** APPROVED
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51
**Publish ref:** `sub/AST-1954/AST-1959-probe-host-lock` @ `059f2a44498ee6759bc257e76bd9acc39ae08527`

### Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.entity.batch-processing | A | | |
| patt.task.dispatch-retry | A | | |
| stat.logging.debug | A | | |
| stat.logging.info | A | | |

### Traceability

1 → Stages 2–3 (single-flight map + first real after probe) · 2 → Stage 2 `probe_host` / Stage 3 key before `only` merge · 3 → Stage 3 `extra_body.provider.only` · 4 → Stages 2–3 remembered failure, no wire on real call · 5 → Stage 1 `probe` flags, Stage 3 batch/server gates, verify `rg` + empty `dispatcher.py` diff · 6 → Stages 1 & 3 `host` on result + INFO segment · parent functional item 5 (ledger row) → N/A — AST-1960

### Findings

#### discuss

- **Location:** Plan Stage 1 step 3 (probe message)
- **Finding:** Parent functional scope still describes probe content as entity index plus “respond with 1”; this child’s Scope and AC 1 anchor on the config constant only. The plan documents that split explicitly and it matches the child partition.
- **Recommendation:** No plan change required for build; keep the decision visible for UAT if anyone compares against parent prose only.

#### acceptable

- **Location:** Plan structure — no `## Self-assessment`
- **Finding:** Three staged done-when blocks, inline decisions, and estimate confirm carry complexity; execution contract is explicit.
- **Recommendation:** None blocking.

- **Location:** Stage 3 verify / execution contract
- **Finding:** Pre-Betty pytest may fail on new `host` key or INFO shape; plan directs engineer to record for `qa-child`, not patch tests in build.
- **Recommendation:** None blocking.

- **Location:** Out of scope / Boundaries
- **Finding:** Ledger, `agent.py`, `database.py`, slug mapping, and `dispatcher.py` are cleanly deferred to AST-1960 or Susan’s tripwire; no scope creep into sibling files.
- **Recommendation:** None.

context_tokens≈42000

Upshot: `[plan-rubric] PROCEED (Commit: 059f2a444) probe lock plan solid`

## Review

- **Publish ref:** `sub/AST-1954/AST-1959-probe-host-lock`
- **Build commits:** `895fcb0d2` (stage 1), `8fce75966` (stage 2), `958182117` (stage 3)
- **For Betty (`qa-child`):** `tests/component/external/test_llm_compat.py::TestAst1877ResultContract::test_success_shape_and_timesheet_kwargs` fails only on the new `host` result key, which is expected per Stage 3. The 21 `tests/component/utils/test_config.py` failures were already failing and are unrelated to this diff (missing meteorite-retention / surfer / telescope config attributes). The host map `src.external.openrouter._hosts` is process-global, so tests need to clear it between cases.

## Radia review

[code-rubric]
**Ticket:** AST-1959
**Publish ref:** `67b54753f9030a58287c844bca50064e52dd514e` (`origin/sub/AST-1954/AST-1959-probe-host-lock`)
**Corpus:** `bd68954dc854ca80fca1fc391821dff9ff288a7a` (canon tree at publish tip; `docs/canon-index.md` absent on ref — ids resolved from `canon/directives/active/*.md`)
**Overall:** CLEAN

### Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.entity.batch-processing | A | | |
| patt.task.dispatch-retry | A | | |
| stat.logging.debug | A | | |
| stat.logging.info | A | | |

### Column diff vs plan stage

(aligned) — Joan graded all four **A**; code review matches.

### Frame diff

(none) — acceptance criteria 1–6 are exercised in `tests/component/external/test_llm_compat.py::TestAst1959ProbeHostLock`, `tests/component/external/test_openrouter.py`, `tests/component/utils/test_logging_batch.py`, and `tests/component/utils/test_config.py::TestAst1959ServerProbeFlag`. No Description checklist rows added.

### Findings

#### fix-now

(none)

#### discuss

(none)

#### advisory

- **Location:** `src/external/openrouter.py` — `_hosts` map
- **Finding:** Process-global, never evicted (per plan). Tests correctly clear via `monkeypatch.setattr(openrouter, "_hosts", {})` in autouse fixtures.
- **Recommendation:** No change for this ticket; long-lived workers with unbounded distinct keys are a known operational tradeoff documented in the plan.

- **Location:** Issue doc build handoff vs `test_config.py`
- **Finding:** Build noted broader `test_config.py` failures unrelated to AST-1959; the three-dot diff only adds `TestAst1959ServerProbeFlag` (probe flag / validator / constant). No product change beyond probe wiring.
- **Recommendation:** Treat any remaining `test_config` red as pre-existing hygiene, not AST-1959 scope.

- **Location:** Joan validate corpus SHA `e1f2699…` vs review corpus `bd68954…`
- **Finding:** Zero `canon/**` lines in `origin/dev...origin/sub/AST-1954/AST-1959-probe-host-lock`; directive text read at publish tip.
- **Recommendation:** None.

### What's solid

- Product footprint matches the plan: `config.py` probe flag + `LLM_PROBE_MESSAGE`, new `openrouter.py` (`probe_host` / `get_batch_host` single-flight), `llm_compat.py` probe/lock before real send, remembered failure with no wire, `host` on all result shapes, optional `host=` on the existing INFO summary line.
- `src/core/dispatcher.py` absent from diff; `rg '"openrouter"' src/external/` is clean on the reviewed tree (server choice stays config-driven via `server["probe"]`, not string literals in sibling modules).
- Probe failure path returns ordinary `success: False` and uses `log_llm_batch_summary(..., error=...)` (WARNING), consistent with `patt.task.dispatch-retry` (no bespoke retry queue in this layer).

context_tokens≈28000

Upshot: `[code-rubric] PROCEED (Commit: 67b54753) canon clean probe lock`

## Bug: AST-2098 — hold the batch on a failed host probe instead of erroring entities

- **Bug (mini-parent):** [AST-2016](https://linear.app/astralcareermatch/issue/AST-2016), orphaned bug, its own `ftr/AST-2016-probe-fail-hold`
- **Fix child:** [AST-2098](https://linear.app/astralcareermatch/issue/AST-2098)
- **Publish ref:** `sub/AST-2016/AST-2098-probe-fail-hold`
- **Amends in this doc:** Stage 2's ⚠️ decision "A missing `provider` … counts as a probe failure" (kept, but the failure is now *held*), Stage 3 step 2's `# No fallback: … ordinary retry → error path` rule (replaced), and the Canon row for `patt.task.dispatch-retry` (see the canon note below).
- **Susan's direction (AST-2016):** "if the probe fails, release the batch with no-op, let the next round catch it."

### As-is

On the OpenRouter path (`openai/gpt-oss-120b`, batch `meteorite_grade_get-1608033b…`) the per-batch probe got back a hollow response with no `usage` and no `provider`. Three things go wrong:

1. `_record_probe` → `_timesheet_kwargs_for` → `usage_to_token_counts(None)` raises `AttributeError: 'NoneType' object has no attribute 'input_tokens'`. `_timesheet_kwargs_for` catches it, logs a full ERROR traceback, and writes the row with zero tokens (AST-1966). The main call path calls `usage_to_token_counts(response.usage)` again at the top of its `try` (`llm_compat.py` ~line 240) with no guard.
2. `probe_host` finds no `provider` and raises `ValueError("Probe response named no provider")`, discarding whatever the response body carried.
3. `send_to_llm_compat` returns the probe error with no `failure_class` (only an exhausted 429 is tagged, AST-2010). Every consult/roster caller treats it as an ordinary entity failure. For `meteorite_grade_get` (a single entity, so `render_verdict`), the job is routed to `METEORITE_FAILED_TECHNICAL_GET` and the run reports `error:1`.

### To-be

A host-probe failure that is not an exhausted 429 (a hollow response, no `provider`, a probe exception, or a cancelled probe) is a **no-op for the batch**:

- Every entity keeps its current state: no `error_state` / `_RETRY` transition.
- The entity is counted **held** (`total_held`), not errored (`total_errors` stays 0).
- The dispatcher stops issuing calls for the rest of the run, and the claim is released in `_run_unified`'s existing `finally`.
- The next dispatch round mints a new `entity_batch_id` (`f"{task_key}-{uuid4()}"`), so the host-map key is new and the probe runs again. The remembered failure in `_hosts` never carries over.

Exhausted-429 probe failures keep the AST-2010 rate-limit path unchanged. When a probe response has no `provider`, the raised error includes what the response actually carried. A missing `usage` reads as zero tokens with no traceback, on both the probe and the real call.

### Repro

Fixtures only: astral has no seeded DB rows for this. The `error` payload below is illustrative. The Oct 7 incident logged only the symptoms, not the body.

1. Hollow probe response fixture, returned by the `send` coroutine `get_batch_host` receives:
   ```python
   hollow = SimpleNamespace(
       id="gen-hollow-1", provider=None, usage=None, content=[], stop_reason=None,
       error={"message": "No endpoints found matching your data policy", "code": 404},
   )
   ```
2. Call `send_to_llm_compat(server_id="openrouter", sku="openai/gpt-oss-120b", …, record_timesheet=<recorder>)` with `log_batch_id` set to `"meteorite_grade_get-<uuid>"`. Patch `_create` so the first call (the probe) returns `hollow`.
3. **Observed now:** an ERROR log record with `AttributeError … 'input_tokens'` and a traceback. The result is `{"success": False, "error": "Host probe failed: Probe response named no provider", …}` with **no** `failure_class` key. Driving it through `consult.run_consult_task("job", "METEORITE_PASSED_DO", [job], bid, ctx, dispatch_task_key="meteorite_grade_get")` transitions the job off its input state and returns `total_errors: 1`.
4. **Expected after fix:** no ERROR record. The timesheet row has zero tokens. `error` contains `"No endpoints found matching your data policy"`. `failure_class == "provider_probe_failure"`. The job's state is unchanged. `run_consult_task` returns `{"total_processed": 1, "total_passed": 0, "total_failed": 0, "total_errors": 0, "total_held": 1, "failure_class": "provider_probe_failure"}`. In `_run_unified`, `ctx["provider_probe_outage"]` is set and no further `consult.run_consult_task` calls are made that run.

### Root cause

1. `usage_to_token_counts` dereferences `usage.input_tokens` / `usage.output_tokens` unconditionally.
2. `probe_host` raises a fixed string when `provider` is missing and never reads the response.
3. **The defect itself:** this doc's Stage 3 decided "No fallback: nothing is sent; the entity takes the ordinary retry → error path". So a probe failure, which says nothing about the entity, is indistinguishable from an entity failure everywhere downstream. There is no `failure_class` for it, no hold branch accepts it, and no dispatcher outage key stops the run on it.
4. Contributing on the job paths: `run_consult_task` forwards only the rate-limit tag (`_rate_limit_tag`) and counts every non-retried failure as `total_errors`. A held job batch is therefore counted as errors and its class never reaches the dispatcher. Balance refusal on job paths has the same gap today, but the Boundaries keep that out of this fix (see ⚠️ Decision D3).

### Proposed change

Eight files, all inside AST-2098's `## Scope`. Steps run in order. No new tables, fields, alerts, retries, or caps.

**1. `src/utils/cost_calculator.py` — `usage_to_token_counts`.** Insert as the first statement of the body, before `return {`:
```python
    # Hollow response (AST-2098): no usage object reads as zero tokens, never an exception.
    if usage is None:
        return {"cache_read": 0, "cache_miss": 0, "output": 0, "cache_write": 0}
```
Leave the rest unchanged. Neither `llm_compat` caller gets its own guard. The `try/except` in `_timesheet_kwargs_for` stays for other read failures.

**2. `src/external/openrouter.py` — `probe_host`.** Replace
```python
    if not host:
        raise ValueError("Probe response named no provider")
```
with
```python
    if not host:
        # Hollow probe (AST-2098): name what came back — OpenRouter's own error object when the body has one,
        # else the whole response — so the held-batch WARNING says why.
        detail = normalize_provider_error(getattr(response, "error", None) or response, fallback="empty body")
        raise ValueError(f"Probe response named no provider: {detail}")
```
`normalize_provider_error` is already imported. `get_batch_host` is unchanged: it still wraps this as `"Host probe failed: <…>"`, and nothing is truncated (`stat.logging.debug`).

**3. `src/utils/config.py` — new `PROVIDER_PROBE_FAILURE`.** Insert directly after the `PROVIDER_RATE_LIMIT = {…}` dict:
```python
# PROVIDER_PROBE_FAILURE — per-batch host probe failed for any reason but an exhausted 429 (AST-2098).
# Entity state is held and the run stops; the next dispatch round mints a new batch id and probes again.
PROVIDER_PROBE_FAILURE = {
    "failure_class": "provider_probe_failure",
}
```

**4. `src/utils/llm_external.py` — two new predicates.** Add `PROVIDER_PROBE_FAILURE` to the `from src.utils.config import (…)` list (alphabetical, after `PROVIDER_EMPTY_RESPONSE`). Insert directly after `is_provider_rate_limit`:
```python
def is_provider_probe_failure(result: Optional[Dict[str, Any]]) -> bool:
    """True when an agent/provider result dict was tagged as a failed host probe (AST-2098)."""
    if not isinstance(result, dict):
        return False
    return result.get("failure_class") == PROVIDER_PROBE_FAILURE["failure_class"]


def is_provider_state_hold(result: Optional[Dict[str, Any]]) -> bool:
    """True when the entity keeps its state: balance refusal (AST-897) or failed host probe (AST-2098)."""
    return is_provider_balance_refusal(result) or is_provider_probe_failure(result)
```

**5. `src/external/llm_compat.py` — probe-error branch of `send_to_llm_compat`.**
- Add `PROVIDER_PROBE_FAILURE` to the `from src.utils.config import …` line, alphabetically after `PROVIDER_EMPTY_RESPONSE`.
- Replace the comment `# No fallback: nothing is sent; the entity takes the ordinary retry → error path.` with `# No fallback: nothing is sent. The tag tells the caller to hold state (AST-2098) or stop on the rate limit (AST-2010).`
- Replace
  ```python
                  if stops_batch and classify_provider_rate_limit(probe_err):
                      out["failure_class"] = PROVIDER_RATE_LIMIT["failure_class"]
  ```
  with
  ```python
                  if stops_batch and classify_provider_rate_limit(probe_err):
                      out["failure_class"] = PROVIDER_RATE_LIMIT["failure_class"]
                  else:
                      out["failure_class"] = PROVIDER_PROBE_FAILURE["failure_class"]
  ```
Nothing else in `llm_compat.py` changes. The WARNING summary line (`log_llm_batch_summary(…, error=probe_err)`) stays as the per-call signal.

**6. `src/core/consult.py`.**
- **6a. Import.** `from src.utils.llm_external import is_provider_balance_refusal, is_provider_rate_limit` → `from src.utils.llm_external import is_provider_probe_failure, is_provider_rate_limit, is_provider_state_hold`. After 6c–6e, `is_provider_balance_refusal` has no use left in consult.
- **6b. Rename `_rate_limit_tag` → `_outage_tag`** at the definition and all 7 call sites (`rg -n _rate_limit_tag src/core/consult.py` → none left). Replace the body:
  ```python
  def _outage_tag(r: Dict[str, Any]) -> Dict[str, Any]:
      """AST-2010 / AST-2098: carry an exhausted-429 or failed-probe failure_class (plus a probe hold's
      total_held) up to the dispatcher; routing unchanged. Empty for every other result."""
      if not (is_provider_rate_limit(r) or is_provider_probe_failure(r)):
          return {}
      return {k: r[k] for k in ("failure_class", "total_held") if k in r}
  ```
- **6c. `_run_analysis_upshot_batch`.** Change the counter init to `processed = passed = failed = errors = held = 0`. Replace the `if is_provider_balance_refusal(result):` block (debug, `_warn_job`, `errors += 1`, `continue`) with:
  ```python
              if is_provider_state_hold(result):
                  logger.debug(
                      "provider state hold failure_class=%r aid=%s error=%r current_state=%r",
                      result.get("failure_class"), aid, result.get("error"), row.get("state"),
                  )
                  # AST-2098: a failed probe is held, not errored; balance keeps its AST-897 error count.
                  if is_provider_probe_failure(result):
                      _warn_job(aid, row.get("state") or "-", "host probe failed — state held")
                      held += 1
                  else:
                      _warn_job(aid, row.get("state") or "-", "provider balance refusal — state held")
                      errors += 1
                  continue
  ```
  In the final return, after `**rl,` add `**({"total_held": held} if held else {}),`. The existing `rl = rl or _outage_tag(result)` line already forwards the class.
- **6d. `render_verdict`.** `if is_provider_balance_refusal(result):` → `if is_provider_state_hold(result):`. Change the debug format to `"provider state hold failure_class=%r aid=%s error=%r current_state=%r"` with `result.get("failure_class")` as the first argument. Change the `_warn_job` text to `"host probe failed — state held" if is_provider_probe_failure(result) else "provider balance refusal — state held"`. The return dict stays as is (`to_state=current_state`, `failure_class`, `state_held: True`).
- **6e. `_run_batch_consult`.** Change the comment to `# Envelope failure — whole batch to error_state (unless balance refusal or failed host probe — hold)`. Change `if is_provider_balance_refusal(result):` → `if is_provider_state_hold(result):`. Change the debug format to `"provider state hold failure_class=%r task=%s error=%r"` and pass `result.get("failure_class")` first. Set `why = "host probe failed" if is_provider_probe_failure(result) else "provider balance refusal"` before the loop and use `f"{why} — state held"` in the loop's `_warn_job`. In the return dict, after `"state_held": True,` add `**({"total_held": len(jobs)} if is_provider_probe_failure(result) else {}),`.
- **6f. `run_consult_task` rollups** (all four sites subtract the probe hold from errors; `_outage_tag` carries `total_held` and `failure_class` up):
  - `prefilter_company` branch: `errors = max(0, total - passed - failed - skipped - r.get("retried", 0) - r.get("total_held", 0))`.
  - `company_upshot` branch: `errors = max(0, total - passed - failed - r.get("retried", 0) - r.get("total_held", 0))`.
  - Single-entity grade branch (`len(entities) == 1`): directly before `retried = not rv.get("state_held") and retry_base(rv.get("to_state"))`, insert
    ```python
                if is_provider_probe_failure(rv):
                    # AST-2098: failed host probe — held, not a run error; the class stops the run upstream.
                    return {"total_processed": 1, "total_passed": 0, "total_failed": 0, "total_errors": 0,
                            "total_held": 1, **_outage_tag(rv)}
    ```
  - Final normalize: `errors = max(0, total - passed - failed - r.get("retried", 0) - r.get("total_held", 0))`.
  
  The `_rate_limit_tag(...)` → `_outage_tag(...)` spreads already on these returns (6b) attach `failure_class` + `total_held`. Results with no probe hold gain no keys.

**7. `src/core/roster.py`.**
- **7a. Import.** `from src.utils.llm_external import is_provider_balance_refusal, is_provider_rate_limit` → `from src.utils.llm_external import is_provider_balance_refusal, is_provider_probe_failure, is_provider_rate_limit, is_provider_state_hold`. `is_provider_balance_refusal` stays in use at the two `not is_provider_balance_refusal(result)` guards in the JOBS_FOUND branch, which are left unchanged (they sit after the early hold return).
- **7b. Rename `_rate_limit_tag` → `_outage_tag`** with the same body and docstring as 6b, at the definition and all 5 call sites.
- **7c. `run_company_task`.** In both the JOBS_FOUND and select_job_page held branches: `if is_provider_balance_refusal(result):` → `if is_provider_state_hold(result):`, and change the debug text `held: provider_balance_refusal error=%r` → `held: %s error=%r` with `result.get("failure_class")` before the error. The two `# AST-1867:` comments gain ` / AST-2098 failed host probe` after "provider refused for balance". The returns (`{**zero, "total_held": 1, "failure_class": …, "error": …}`) are unchanged.
- **7d. `_prefilter_fail`.** `if api_result is not None and is_provider_balance_refusal(api_result):` → `… is_provider_state_hold(api_result):`. The comment becomes `# AST-897 / AST-2098: balance refusal or failed host probe — hold current loop-eligible state`.
- **7e. `_run_batch_company_prefilter`.** `if is_provider_balance_refusal(result):` → `if is_provider_state_hold(result):`. Change the debug text to `"Response from agent.do_task: provider state hold error=%r failure_class=%r"`. In the return dict, after `"state_held": True,` add `**({"total_held": len(companies)} if is_provider_probe_failure(result) else {}),`. `prefilter_company_batch` passes the dict through and only overwrites `total` / `skipped`.
- **7f. `company_upshot_batch`.** `if is_provider_balance_refusal(result):` → `if is_provider_state_hold(result):`. The comment becomes `# Balance refusal or failed host probe: hold state; the dispatcher stops the run.`. In the return dict, after `"state_held": True,` add `**({"total_held": len(rows)} if is_provider_probe_failure(result) else {}),`.
- **7g. `_find_job_page_from_assembled`.** `if is_provider_balance_refusal(res) or res.get("failure_class") == PROVIDER_CALL_BUDGET["failure_class"]:` → `if is_provider_state_hold(res) or res.get("failure_class") == PROVIDER_CALL_BUDGET["failure_class"]:`. Add "failed host probe (AST-2098)," to the comment's list of non-verdicts.

**8. `src/core/dispatcher.py`.**
- **8a. Import.** `from src.utils.llm_external import is_provider_balance_refusal, is_provider_probe_failure, is_provider_rate_limit`.
- **8b. New note function** directly after `_note_provider_rate_limit_outage`:
  ```python
  def _note_provider_probe_outage(ctx: Dict, task: Dict, result: Dict) -> None:
      """AST-2098: first failed-host-probe result in a run sets ctx["provider_probe_outage"] and logs one
      WARNING; later results only add to the held tally. The run stops and the next round probes again."""
      outage = ctx.get("provider_probe_outage")
      if outage is None:
          outage = ctx["provider_probe_outage"] = {"error": result.get("error") or "", "held": 0}
          logger.warning(
              "%s | dispatch %s %s\n  LLM host probe failed (%s)\n  The batch is stopping; entity state is held for the next round",
              ctx.get("astral_candidate_id") or task.get("candidate_id") or "-",
              task.get("entity_type") or "-",
              task.get("task_key") or "-",
              outage["error"],
          )
      outage["held"] += int(result.get("total_held", 0) or 0)
  ```
- **8c. `_run_unified`, three result sites** (chunk `_consult_chunk`, the unchunked consult call, `_one`). After each `if is_provider_rate_limit(result): _note_provider_rate_limit_outage(ctx, task, result)` pair, add
  ```python
                      if is_provider_probe_failure(result):
                          _note_provider_probe_outage(ctx, task, result)
  ```
  at that site's indentation.
- **8d. `_run_unified`, two skip checks** (`_consult_chunk` and `_one`). Change `if ctx.get("provider_balance_outage") or ctx.get("provider_rate_limit_outage"):` → `if ctx.get("provider_balance_outage") or ctx.get("provider_rate_limit_outage") or ctx.get("provider_probe_outage"):`. Both comments gain `/ AST-2098` and `, rate limit or failed host probe`.
- **8e. `_run_dispatch_loop`.** Directly after the `provider_rate_limit_outage` break block, add
  ```python
          # AST-2098: failed host probe — stop; held entities stay eligible and the next round probes again
          if ctx.get("provider_probe_outage"):
              logger.debug("loop stop: provider host probe failed run_count=%s", run_count)
              logger.debug("End dispatch loop after %s run(s)", run_count)
              break
  ```
- **8f. `_dispatch_one_body` final status.** After the `elif ctx.get("provider_balance_outage"):` / `final_status = "INTERRUPTED"` pair, add
  ```python
          elif ctx.get("provider_probe_outage"):
              final_status = "INTERRUPTED"
  ```
  Extend the comment above with: `# AST-2098: a failed host probe is a no-op run — INTERRUPTED, so it stays out of the circuit breaker.` Leave the alert block unchanged: no probe alert (Boundary). With `total_errors == 0`, `monitor.auto_run_error` does not fire either.

**Verify:**
- `python3 -m py_compile src/utils/cost_calculator.py src/external/openrouter.py src/utils/config.py src/utils/llm_external.py src/external/llm_compat.py src/core/consult.py src/core/roster.py src/core/dispatcher.py`
- `python3 -c "from src.utils.config import validate_llm_provider_environment as v; v()"`
- `rg -n "_rate_limit_tag" src/` prints nothing
- the repo linter on the eight files
- `python3 -m pytest tests/component/utils/test_llm_external.py tests/component/external/test_openrouter.py tests/component/external/test_llm_compat.py tests/component/core/test_consult.py tests/component/core/test_roster.py tests/component/core/test_dispatcher.py -q`. A failure that only asserts the old probe behaviour (no `failure_class` on a non-429 probe error, the exact `"Probe response named no provider"` string, or an errored probe batch) goes to Betty, not `tests/`.

⚠️ **Decision D1 — one shared predicate, not a second copy of each branch.** `is_provider_state_hold` gates every hold branch. `is_provider_probe_failure` is used only where probe and balance *must* differ: held-vs-error counting on job paths (D3), the warn text, and the dispatcher outage key.

⚠️ **Decision D2 — held counts as processed.** This follows roster's existing held return (`zero` has `total_processed: 1`). A probe-held entity is `processed 1 / errors 0 / held 1`, not `processed 0`.

⚠️ **Decision D3 — balance refusal on job paths is left exactly as it is.** Today a balance hold on `render_verdict` / `_run_batch_consult` / `_run_analysis_upshot_batch` keeps state but is counted in `total_errors`, and its class never reaches the dispatcher (no stop, no AST-1867 alert). Fixing that would change AST-897 / AST-1867 balance behaviour, which the Boundaries exclude. The `total_held` key and the `_outage_tag` forwarding are therefore probe-only. Flagged for Susan as a possible follow-up, not done here.

⚠️ **Decision D4 — `_run_dispatch_chain_job_batch` is not touched.** It has no balance-refusal hold branch to widen (the Technical scope says "balance-refusal hold branches widen"). Its generic failure branch already leaves the job's state alone and releases the claim. A probe failure there is still counted as an error and does not stop the run. Adding a new branch there is a different kind of change than Scope declares, so this is noted rather than done.

⚠️ **Decision D5 — a cancelled probe and a no-`provider` probe are both probe failures.** Any `probe_err` that is not an exhausted 429 on a `stops_batch` server gets `PROVIDER_PROBE_FAILURE`. Only `openrouter` has `probe: True`, and it has `exhausted_stops_batch: True`, so AC 4 holds.

⚠️ **Canon note for fix-board (Joan): `patt.task.dispatch-retry` Arc 5.** The canon text reads: "A FAILURE DOES NOT PERSIST IN STATE … Under no circumstances does a failure remain in the same state", and "Every other failed attempt: THIS PATTERN ALWAYS APPLIES". Its only carve-out is empty runtime tokens. Susan's to-be holds state on a probe failure, as AST-897 already does for balance refusal, which has no carve-out in that directive either. This plan follows Susan's direction. Whether the directive needs a "provider-side outage, no attempt made" carve-out is canon's call (fix-board `[board-joan]`), not this fix's.

### Blast radius

- **AST-2010 (rate limit):** shares the probe-error branch and the renamed `_outage_tag`. Its 429 classification and dispatcher path are byte-for-byte the same; only the else-arm is new.
- **AST-897 / AST-1867 (balance refusal):** every balance hold branch now goes through `is_provider_state_hold`, with identical outcomes for balance (D3). Only debug-line wording changes. `_note_provider_balance_outage`, `monitor.provider_balance_outage`, and the `INTERRUPTED` status for balance are untouched.
- **AST-1966 (timesheet always a row):** the probe's row is still written with zero tokens. The ERROR traceback goes away because `usage` is `None`, not because the `except` changed.
- **AST-1190 (hollow real call):** a hollow *real* call (after a good probe) still takes `PROVIDER_EMPTY_RESPONSE` → error routing. It now gets there without a traceback, because `usage_to_token_counts(None)` returns zeros, which `is_unusable_provider_response` already treats as zero tokens.
- **AST-1960 ledger:** `llm_failure_class` on the dispatch ledger row now reads `provider_probe_failure` instead of the fallback `provider_failed` for these calls.
- **Tests that assume the old behaviour** (Betty's call): probe-failure cases in `tests/component/external/test_llm_compat.py::TestAst1959ProbeHostLock` and `tests/component/external/test_openrouter.py` that assert no `failure_class` on a non-429 probe error, or the exact `"Probe response named no provider"` string. Any consult/roster test that drives a probe-error result into an error-state transition. `tests/component/core/test_dispatcher.py` cases that enumerate outage keys.
- **Persistent probe failure (AST-2016 Proposed step 6):** if no zero-data-retention host exists for a SKU, its entities are held every round, forever. The only signals are the per-call WARNING summary and the one dispatcher WARNING per run. No alert or cap is added (Boundary; Susan's call).

### What must still hold

- AST-1959 AC 1–6: one probe per (batch id, request args) key, concurrent callers share it, `provider.only = [host]` on real calls, a remembered failure sends nothing on the wire, the `host` key on every result, and `host=` on the INFO line.
- AST-2010: an exhausted-429 probe failure on `openrouter` still yields `failure_class == "provider_rate_limit"`, `FAILED` final status, and the run stops.
- AST-1867: balance refusal still sets `provider_balance_outage`, stops the run, gets `INTERRUPTED`, and sends its one alert. The breaker is skipped. Roster's held counting is unchanged.
- AST-1189 / AST-1842: `PROVIDER_CALL_BUDGET` holds in `_find_job_page_from_assembled` are unchanged. A call-budget `state_held` result with no probe class still counts `total_errors: 1` where it did before.
- Healthy and non-probe-failure results from `run_consult_task` / roster batch functions gain **no** new keys (59 component tests assert exact summary dicts).
- The batch claim is released in `_run_unified`'s `finally` on every path, the probe-held path included.


## Joan fix-board — AST-2098


**Ticket:** AST-2098 — hold batch on failed host probe (parent AST-2016)  
**Read:** `plan-fix` § Bug: AST-2098 (As-is → What must still hold) on `origin/sub/AST-2016/AST-2098-probe-fail-hold`; `canon/directives/active/patt.task.dispatch-retry.md`; roster skim (`stat.logging.error`, `astral.dispatch.entity-state-bound` — no probe/balance hold language).

### Summary

The product change is coherent and bounded: tag non-429 probe failures as `provider_probe_failure`, hold entity state, stop the dispatch run (`provider_probe_outage` / `INTERRUPTED`, no circuit-breaker trip), and let the next round re-probe on a new batch id. That matches Susan’s AST-2016 direction and reuses the AST-897 / AST-2010 outage pattern (`is_provider_state_hold`, `_outage_tag`, dispatcher skip keys).

Canon impact is **not** “no touch.” The fix **replaces** the AST-1959 plan’s mapping of probe failure onto ordinary `patt.task.dispatch-retry` retry→error routing. Active pattern text still says failures must not persist in the trigger state (Arc 5) and that **every other** failed attempt gets the pattern (§ When this doesn’t apply — only `empty_tokens` is exempt). Holding on probe failure is the same *class* of exception as empty tokens: **no real entity attempt**, so Arc 4–5 retry semantics should not apply; the corpus should say so explicitly, as with AST-2005’s empty-token carve-out.

### Ada’s question — `patt.task.dispatch-retry` Arc 5

**Is there a conflict?**  
**Yes, at the literal-text level** if probe failure is still treated as a normal “failed attempt” under dispatch-retry. Arc 5: *“Under no circumstances does a failure remain in the same state.”* The old Stage 3 rule sent probe failure through ordinary retry→error; this fix holds state instead — that **is** a deliberate departure from that reading.

**Is it a product/canon blocker?**  
**No for implementation direction** — Susan already chose hold/no-op. **Yes for canon hygiene** — the **active** `patt.task.dispatch-retry` directive should gain a second “When this doesn’t apply” bullet (probe / provider-side pre-attempt outage), parallel to empty runtime tokens: no `_RETRY` hop, hold loop-eligible state, next dispatch round retries infrastructure (new batch id / probe), not “second strike to error_state.”

**Balance refusal (AST-897):** Same Arc 5 tension already exists in production without a pattern carve-out; this fix **widens the shared hold predicate** (`is_provider_state_hold`) but **does not** change balance counting (D3). Joan is **not** asking to fix balance in AST-2098; optional follow-up could document balance + probe under one “pre-attempt / provider gate” exemption.

**Not ESCALATE:** Precedent is AST-2005-style carve-out text, not a new architectural precedent. Susan’s call is product; F3 lands canon wording.

### Other directive overlap (skim)

| Id | Triage |
|----|--------|
| `patt.entity.batch-processing` | OK — host map still keyed by claim `batch_id`; claim released in `finally`. |
| `stat.batch.claim-process-release` | OK — no change to claim/release contract. |
| `stat.logging.error` | OK — removing the `usage=None` traceback is fixing an unintended exception on an expected hollow path, not demoting a terminal entity fault; probe path stays WARNING via `log_llm_batch_summary`. |
| `stat.logging.debug` / `stat.logging.info` | OK — plan preserves one INFO line + host. |
| `astral.dispatch.entity-state-bound` | OK — no dispatch_task row lies. |

Plan also updates the **feature doc** Canon row for `patt.task.dispatch-retry` (listed under “Amends in this doc”); that is necessary but **not sufficient** — the in-force pattern in `canon/directives/active/` should be amended in **validate-plan fix mode (F3)**.

### F3 hint (if Chuckles spawns it)

Add to `patt.task.dispatch-retry` § When this doesn’t apply something like: **failed per-batch host probe / provider routing gate** (no entity prompt sent for that task attempt) — hold current loop-eligible state, no `_RETRY` transition; dispatch may stop the run and retry on a later round. Cross-reference `provider_probe_failure` / AST-2098 in rationale only if canon style allows ticket refs in carve-outs.

---

### Machine-readable verdict (for Chuckles `linear_proxy --as joan`)

```
[board-joan]  CANON: REVISE
What: patt.task.dispatch-retry — add "When this doesn't apply" carve-out for failed host probe (no entity attempt); Arc 5 hold — provider-side gate like empty_tokens
```

### Stdout (skill § Joan)

```text
AST-2098 board-joan done — CANON: REVISE — dispatch-retry probe carve-out.
```


**Chuckles routing:** the canon change Joan names (`canon/directives/active/patt.task.dispatch-retry.md`) is outside AST-2098's approved Component scope, and Betty's `[board-betty] TESTS: REVISE` names a test gap. Both go to one sibling gap child under AST-2016 (orphaned branch: gap child instead of inline F3/F4). AST-2098 proceeds to make-fix.


## Radia review — AST-2098

```
[code-rubric]
**Ticket:** AST-2098
**Publish ref:** `19036ccf07daace568540d66f829f5cefdc0468e` (`origin/sub/AST-2016/AST-2098-probe-fail-hold`)
**Corpus:** `9b1648f5f15106be183d31aadfb04054c937378f`
**Overall:** CLEAN

## Canon scores

(no frozen directive ids in AST-2098 Linear description — no `## Citations` block; same shape as other fix-lane children with board-only canon read. Zero graded rows per review-child §5. Qualitative fix-board overlap below is **not** a second canon pass.)

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| *(frozen list empty)* | — | — | Score only ids locked at Plan Approved; none on ticket |

**Fix-board Joan overlap (qualitative, not roll-up):** `patt.entity.batch-processing`, `stat.batch.claim-process-release`, `stat.logging.error`, `stat.logging.debug`, `stat.logging.info`, `astral.dispatch.entity-state-bound` — product diff consistent with Joan’s OK triage. `patt.task.dispatch-retry` — **active** pattern text still lacks the probe carve-out; implementation deliberately holds state (Susan / plan-fix); **canon wording routed to AST-2099**, not graded as a fix-now statute violation on this sub.

## Column diff vs plan stage

`no plan-stage scores attached` — no validate-plan fix-mode (F3) artifact with per-id grades on AST-2098; Joan fix-board `[board-joan] CANON: REVISE` is qualitative + machine-readable carve-out hint only.

## Frame diff

- [ ] **Boundaries / Considered but excluded:** `_run_dispatch_chain_job_batch` still treats probe failure as a generic envelope error (plan ⚠️ D4). Confirm UAT does not expect hold/stop on chain-batch task keys.

## Fix-specific checks

- **`[bug-repro]`:** not applicable — clean board opt-out; Betty `TESTS: REVISE` and Joan canon REVISE routed to gap child **AST-2099**; qa-fix did not run on AST-2098 (per spawn brief).
- **`## What must still hold`:** OK — traced against `origin/ftr/AST-2016-probe-fail-hold...origin/sub/AST-2016/AST-2098-probe-fail-hold` product diff:
  - AST-1959 probe/lock/`host`/`log_llm_batch_summary` path intact; only non-429 probe tagging + hold routing added.
  - AST-2010: exhausted-429 probe still sets `PROVIDER_RATE_LIMIT` when `stops_batch and classify_provider_rate_limit(probe_err)`; dispatcher still sets `FAILED` on `provider_rate_limit_outage` before balance/probe `INTERRUPTED`.
  - AST-1867: balance-specific outage note/alert paths untouched; D3 preserves balance error counting on job upshot paths while probe uses `total_held`.
  - AST-1189/1842: `PROVIDER_CALL_BUDGET` branch in `_find_job_page_from_assembled` unchanged aside from `is_provider_state_hold` widening.
  - Healthy summaries: `total_held` only when probe hold; `_outage_tag` only forwards `failure_class` + optional `total_held` for rate-limit/probe.
  - Claim release: no change to `_run_unified` `finally` / release contract.

## Findings

#### fix-now

(none)

#### discuss

- **Location:** Plan ⚠️ D4 — `src/core/consult.py` `_run_dispatch_chain_job_batch`
- **Finding:** Chain-batch consult tasks still count probe failure as a run error and do not stop the dispatch run via `provider_probe_outage`; plan explicitly excluded widening here.
- **Recommendation:** @susan — Is chain-batch dispatch in scope for the same hold/stop semantics, or is meteorite single-entity grade (`render_verdict` / `run_consult_task` early return) the only UAT tripwire?
- **Default:** Leave D4 as documented; do not expand scope on resolve-child unless Susan answers yes.

#### advisory

- **Location:** Three-dot diff vs `origin/ftr/AST-2016-probe-fail-hold`
- **Finding:** Nine sibling `docs/features/**` issue-doc files ride the diff with no `src/**` changes (doc stack on sub tip). Product footprint is exactly the eight scoped files + plan-fix doc section.
- **Recommendation:** Note once for merge-child readers; not a scope violation.

- **Location:** `canon/directives/active/patt.task.dispatch-retry.md` (unchanged on this ref)
- **Finding:** Product now holds loop-eligible state on probe failure while active Arc 5 / “every other failed attempt” text still reads literally; AST-2099 owns carve-out + bible/tests per Chuckles routing.
- **Recommendation:** Do not block AST-2098 User Testing on canon file landing; track AST-2099 for corpus hygiene.

- **Location:** `tests/**`
- **Finding:** No test or test-bible diff on this publish ref; Ada notes one pre-fix-breaking assertion on probe error string (AC 5) deferred to AST-2099; remaining touched-suite failures match pre-fix tree.
- **Recommendation:** AST-2099 closes Betty’s REVISE; optional UAT uses hollow-probe repro in plan-fix § Repro.

### What's solid

- Eight-file diff matches plan-fix **Proposed change** step order and symbols (`PROVIDER_PROBE_FAILURE`, `is_provider_state_hold`, `_outage_tag`, `_note_provider_probe_outage`, loop break + `INTERRUPTED`).
- `usage_to_token_counts(None)` and enriched `probe_host` error text address the Oct 7 traceback and AC 5.
- `rg '_rate_limit_tag' src/` clean on reviewed tip.
- No `canon/**` lines in the fix diff; canon amend stays on AST-2099 by design.

### Chuckles branching (read-only)

| Gate | Parent shape | Next |
|------|----------------|------|
| **PROCEED** (C7 complete) | Normal mini-parent AST-2016 (not orphaned for merge-child) | **Review Posted** → do-all-the-things §3h clean-review shortcut → **User Testing**; **resolve-child** skipped |

context_tokens≈42000
```

```
[code-rubric] PROCEED (Commit: 19036ccf0) probe hold matches plan
```
