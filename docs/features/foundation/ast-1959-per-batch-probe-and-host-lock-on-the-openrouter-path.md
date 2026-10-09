<!-- linear-archive: AST-1959 archived 2026-10-08 -->

## Linear archive (AST-1959)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1959/per-batch-probe-and-host-lock-on-the-openrouter-path-add-host  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** hedy  
**Priority / estimate:** None / 3  
**Parent:** AST-1954 — Add host-discovery probe ahead of warm/gather; pin the batch to one provider  
**Blocked by / blocks / related:** parent: AST-1954; blocks: AST-1960

### Description

## What this implements

The first OpenRouter call of each dispatch batch sends one probe first, and the batch's real calls are locked to the probe's host with `only`. A failed probe fails the batch's calls with no fallback. Every `llm_compat` result returns the host that served it, and the per-call INFO line names it. This child does **not** write the ledger (#2). Requires AST-1953 on `dev`. Hedy built AST-1953's wire child in `llm_compat`.

## Citations

`patt.entity.batch-processing` (host map keyed on the claim's batch id); `patt.task.dispatch-retry` (probe failure is an ordinary failed call); `stat.logging.debug`; `stat.logging.info`.

## Scope

* `src/utils/config.py` (**modified**):
  * **New server field:** a boolean probe flag on every `LLM_SERVER_CONFIG` entry, true on `openrouter` only, checked by the server validator. No server name is hard-coded outside config.
  * **New constant:** the probe message text.
* `src/external/openrouter.py` (**new**):
  * **New probe function:** takes the real call's fully assembled request arguments, swaps the content for the probe message, drops the system block, sends it through the same client and returns the response's `provider`. It records the probe on the timesheet through the caller's `record_timesheet` callback, so its cost shows in the ledger.
  * **New host-map function:** keyed on (batch id, the request arguments minus content and system), it returns the batch's host or the remembered probe failure. Exactly one probe runs per key, even when first calls arrive at the same time. Entries are never evicted; a restart clears them, and no cap or TTL is added.
* `src/external/llm_compat.py` (**modified**):
  * **Modified request assembly in** `send_to_llm_compat`: when the server's probe flag is on and a batch id is set, gets the host from the map. On success it sets `provider.only = [host]`. On a remembered failure it returns a failure result with no request sent. Otherwise the request is exactly as today.
  * **Modified result:** carries `host`, which is the response's `provider` or, when that is absent, the server's label. The served host goes into the per-call summary.
* `src/utils/logging.py` (**modified**): `log_llm_batch_summary`'s INFO line adds the served host and stays one line per call.
* Tests and bibles (Betty in `qa-child`):
  * `tests/component/utils/test_config.py`
  * `tests/component/external/test_openrouter.py` (**new**)
  * `tests/component/external/test_llm_compat.py`
  * `tests/component/utils/test_logging_batch.py`
  * `docs/test-bible/utils/config.md`
  * `docs/test-bible/external/openrouter.md` (**new**)
  * `docs/test-bible/external/llm_compat.md`
  * `docs/test-bible/utils/logging_batch.md`

## Acceptance criteria

"Stubbed client" means the component-test stub of the Anthropic SDK client used by `test_llm_compat.py`. All checks run on the shipped tree, after AST-1953.

1. **One probe per batch key, before the first real call.**
   * **Check (component test, stubbed client, batch id set, server** `openrouter`**):** one awaited `send_to_llm_compat` call, then three concurrent calls for the same model and settings. The stub records exactly **5** requests, and the first has the probe message as its only content.
   * **Fails if:** there are 0 or more than 1 probes, or the probe is not first.
2. **The probe matches the real call and carries no cache.**
   * **Check (same test):** the probe's request arguments equal the first real call's, except the content and the missing `system`. `max_tokens`, temperature/effort and `provider` are identical. No `cache_control` appears in the probe, and the probe has no `provider.only` beyond what the agent set.
   * **Fails if:** any of those fields differs, a `cache_control` block is present, or the probe carries a host lock.
3. **Warm and gather are locked to the probe's host.**
   * **Check (component test):** the stubbed probe response has `provider: "DeepInfra"`. Every later request in the batch carries `provider.only == ["DeepInfra"]`, and AST-1953's other provider keys (for example `quantizations: ["bf16"]`) are unchanged.
   * **Fails if:** `only` is missing or different, or another provider key is dropped or altered.
4. **A failed probe fails the batch's calls with no fallback.**
   * **Check (component test):** the stubbed probe raises a 429. The stub records exactly **1** request (the probe) across one awaited call and three concurrent calls in that batch, and every call returns `success: False`.
   * **Fails if:** any real request is sent, a second probe is sent, or any call reports success.
5. **No probe outside scope.**
   * **Check (component test):** with server `kimi` or `deepseek`, or with `openrouter` and no batch id, the stub records zero probes and no request gets a host lock.
   * **Check:** `rg -n '"openrouter"' src/external/` returns nothing.
   * **Check:** `git diff origin/dev...HEAD --stat -- src/core/dispatcher.py` is empty.
   * **Fails if:** there is a probe or lock in those cases, a hit for `"openrouter"`, or a dispatcher change.
6. **The host comes back (this child's part).**
   * **Check (component test):** an `llm_compat` result for a stubbed response with `provider: "DeepInfra"` has `host == "DeepInfra"`, and the per-call INFO line contains `DeepInfra`.
   * **Fails if:** the host is missing from the result or the line.

## Boundaries

* Does **not** write `dispatch_ledger` or touch `agent.py` / `database.py`: that is #2 (Record the serving host on the dispatch ledger - Katherine).
* Does **not** change `dispatcher.py`.
* Uses the response's `provider` value as-is in `only`, with no slug mapping (Susan's decision; parent UAT AC 7 is the tripwire).

## Notes for planning

* Cite `patt.entity.batch-processing`, `patt.task.dispatch-retry`, `stat.logging.debug` and `stat.logging.info` (parent Architectural definition has the links).
* AST-1953 (agent settings → provider object in `llm_compat`) must be on `dev` before this child plans. A gate ticket on the parent holds it.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at dispatch-parent.

### Comments

#### radia — 2026-10-04T00:36:29.916Z
[code-rubric] PROCEED (Commit: 67b54753) canon clean probe lock

#### betty — 2026-10-04T00:33:55.801Z
`origin/sub/AST-1954/AST-1959-probe-host-lock` @ `67b54753f` · probe/lock tests, 157 manifest

#### hedy — 2026-10-04T00:28:52.473Z
`origin/sub/AST-1954/AST-1959-probe-host-lock` @ `10377b6e3`

#### joan — 2026-10-04T00:26:27.051Z
[plan-rubric] PROCEED (Commit: 059f2a444) probe lock plan solid

#### hedy — 2026-10-04T00:25:03.179Z
`origin/sub/AST-1954/AST-1959-probe-host-lock` @ `059f2a444` · plan ready, three stages

---

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
