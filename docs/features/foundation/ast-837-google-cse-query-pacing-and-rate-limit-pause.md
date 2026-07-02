# AST-837 — Google CSE query pacing and rate-limit pause

- **Linear (this ticket):** [AST-837 — Google CSE query pacing and rate-limit pause](https://linear.app/astralcareermatch/issue/AST-837/google-cse-query-pacing-and-rate-limit-pause-rate-limit-queries-for-a)
- **Parent (reference only):** [AST-835 — Rate limit queries for a config-driven pause](https://linear.app/astralcareermatch/issue/AST-835/rate-limit-queries-for-a-config-driven-pause)
- **Publish ref:** `origin/sub/AST-835/AST-837-google-cse-query-pacing-and-rate-limit-pause`

## Summary

Google Custom Search requests from roster inflow discovery and website resolution can fire many paginated HTTP calls in seconds; when Google returns HTTP 429 or a rate-limit API envelope, the product today fails immediately and burns the rest of the batch. This ticket adds **config literals** for minimum spacing between successive CSE HTTP requests and for **pause-and-retry** on rate-limit responses, implemented once in **`src/external/google_cse.py`** so every caller shares the same behavior. Roster call sites only wire an optional **`pace_detail`** callback when **`debug=True`** so pacing and retry sleeps appear as **` | `** detail lines under the existing Style D index headers (AST-538 / AST-557). After retries are exhausted, discovery and resolve keep today's failure semantics unchanged.

## Out of scope (explicit)

| Item | Reason |
|------|--------|
| Search term selection, `freq_hrs`, `max_results_per_query`, date-restrict | Ticket boundaries |
| Admin UI knobs for delay/pause | Config literals only (§2.1) |
| Anthropic, Playwright, or other external I/O pacing | CSE only |
| Job-table UNIQUE constraint crash | Separate ticket (parent open question #3) |
| Dispatch scheduler active/paused toggle | Unrelated |
| Betty test manifest / bible edits | **qa-child** owns tests |
| Logging inside **`google_cse.py`** | External layer §2.5 — use **`pace_detail`** callback |

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add **`GOOGLE_CSE_CONFIG`** block with inter-query delay, rate-limit pause, max retries (documented units) | utils |
| `src/external/google_cse.py` | Inter-query pacing, rate-limit detection + pause-and-retry loop, optional **`pace_detail`** callback; refactor HTTP into internal helper | external |
| `src/core/roster.py` | Pass **`pace_detail`** buffer at **`run_inflow_discovery_batch`** and **`resolve_company_website`** call sites; flush buffered lines under existing **`debug_index`** headers when **`debug=True`** | core |

## Stage 1: `GOOGLE_CSE_CONFIG` literals

**Done when:** `from src.utils.config import GOOGLE_CSE_CONFIG` returns a dict with three keys and documented units; no `os.environ` reads for these values; defaults are plain literals Susan can tune at UAT.

1. In **`src/utils/config.py`**, immediately **after** the **`INFLOW_CONFIG`** block (before **`GAZER_CONFIG`**), add:

```python
# Google Custom Search HTTP pacing (AST-837). Units: seconds (float/int) and count (int).
GOOGLE_CSE_CONFIG = {
    # Minimum spacing between successive CSE HTTP requests (including pagination pages
    # within one search_google_cse call). 0 disables pacing delay.
    "inter_query_delay_sec": 1.2,
    # Sleep duration after a rate-limit response before retrying the same HTTP request.
    "rate_limit_pause_sec": 65,
    # Number of pause-and-retry cycles after a rate-limit response (0 = no retries;
    # 2 means up to 3 HTTP attempts total for that request).
    "rate_limit_max_retries": 2,
}
```

2. Do **not** add environment-variable overrides for these keys (ticket AC5 / §2.1).

⚠️ **Decision:** **`1.2` s inter-query delay** targets ~50 requests/min with headroom under Google's documented **100 queries/min/user** ceiling observed in production logs. **`65` s pause** exceeds the per-minute quota window so a retry after 429 has a fresh minute bucket. Susan confirms or adjusts at UAT (parent open question #2).

---

## Stage 2: Shared pacing and rate-limit retry in `google_cse.py`

**Done when:** Any caller of **`search_google_cse`** automatically spaces HTTP requests per config, retries rate-limit responses up to **`rate_limit_max_retries`**, and raises the same **`RuntimeError`** shapes as today when retries are exhausted or the failure is not rate-limit-related; optional **`pace_detail`** receives human-readable strings for debug wiring in Stage 3.

1. At top of **`src/external/google_cse.py`**, add imports:

```python
import time
from collections.abc import Callable

from src.utils.config import GOOGLE_CSE_CONFIG
```

Keep existing imports; add **`Callable`** to typing import line if you collapse imports.

2. Add module-level pacing state **after** existing module constants:

```python
_last_cse_request_at: float | None = None
```

This is process-global (acceptable — Gunicorn **`RAILWAY_CONFIG`** uses single worker; all CSE calls share one pacing clock).

3. Add private helpers (place after **`_next_start_index`**, before **`search_google_cse`**):

```python
def _pace_detail_emit(pace_detail: Callable[[str], None] | None, message: str) -> None:
    if pace_detail is not None:
        pace_detail(message)


def _is_rate_limit_response(status_code: int, parsed: dict | None) -> bool:
    if status_code == 429:
        return True
    if not isinstance(parsed, dict):
        return False
    err_obj = parsed.get("error")
    if not isinstance(err_obj, dict):
        return False
    code = err_obj.get("code")
    if code == 429 or code == "429":
        return True
    errors = err_obj.get("errors")
    if isinstance(errors, list):
        for row in errors:
            if isinstance(row, dict) and row.get("reason") == "rateLimitExceeded":
                return True
    return False


def _apply_inter_query_delay(pace_detail: Callable[[str], None] | None) -> None:
    global _last_cse_request_at
    delay = float(GOOGLE_CSE_CONFIG["inter_query_delay_sec"])
    if delay <= 0:
        return
    if _last_cse_request_at is None:
        return
    elapsed = time.monotonic() - _last_cse_request_at
    wait = delay - elapsed
    if wait > 0:
        _pace_detail_emit(
            pace_detail,
            f"pacing: sleeping {wait:.2f}s before CSE HTTP request",
        )
        time.sleep(wait)


def _parse_cse_json(response) -> dict | None:
    try:
        parsed = response.json()
    except ValueError:
        return None
    return parsed if isinstance(parsed, dict) else None


def _http_get_with_pacing_and_retry(
    params: dict[str, str | int],
    *,
    pace_detail: Callable[[str], None] | None,
):
    """Return (response, parsed_dict|None). Raises RuntimeError on exhausted rate limit or non-retryable HTTP/API failure."""
    global _last_cse_request_at
    max_retries = int(GOOGLE_CSE_CONFIG["rate_limit_max_retries"])
    pause_sec = float(GOOGLE_CSE_CONFIG["rate_limit_pause_sec"])
    if max_retries < 0:
        max_retries = 0

    last_response = None
    last_parsed: dict | None = None

    for attempt in range(max_retries + 1):
        _apply_inter_query_delay(pace_detail)
        last_response = requests.get(
            GOOGLE_CSE_API_URL,
            params=params,
            timeout=_DEFAULT_REQUEST_TIMEOUT_SEC,
        )
        _last_cse_request_at = time.monotonic()
        last_parsed = _parse_cse_json(last_response)

        if _is_rate_limit_response(last_response.status_code, last_parsed):
            if attempt < max_retries:
                _pace_detail_emit(
                    pace_detail,
                    f"rate limit: HTTP {last_response.status_code}; pausing {pause_sec:.0f}s "
                    f"before retry {attempt + 1}/{max_retries}",
                )
                time.sleep(pause_sec)
                continue
            break  # exhausted — fall through to existing error raise paths below

        # Not rate-limited: return immediately (success or other error handled by caller)
        return last_response, last_parsed

    # Rate limit retries exhausted — reuse existing HTTP error formatting
    assert last_response is not None
    raise RuntimeError(
        f"Google CSE HTTP {last_response.status_code}: "
        f"{_truncate_body(last_response.text)}"
    )
```

4. Extend **`search_google_cse`** signature — add optional keyword-only parameter **after** **`days`**:

```python
pace_detail: Callable[[str], None] | None = None,
```

Add **`pace_detail`** to the docstring: when provided, the function invokes it with pacing/retry status strings; external layer does not log (§2.5).

5. Inside the pagination **`while True:`** loop, **replace** the inline **`requests.get(...)`** block (lines that build params through **`response = requests.get`**) with:

```python
response, parsed = _http_get_with_pacing_and_retry(params, pace_detail=pace_detail)
```

6. **Remove** the duplicate **`response.json()`** / root-type check block that followed the old **`requests.get`** — **`parsed`** is already returned by the helper when JSON parses. Keep the existing logic flow:

   - If **`not response.ok`** and we did not already raise from exhausted rate limit inside helper: raise **`RuntimeError(f"Google CSE HTTP {response.status_code}: …")`** as today.
   - If **`parsed is None`** (invalid JSON on non-rate-limit response): raise **`RuntimeError("Google CSE returned a response body that is not valid JSON")`** as today.
   - If **`not isinstance(parsed, dict)`**: raise **`RuntimeError("Google CSE returned JSON root that is not an object")`** as today.
   - Continue with **`err_obj = parsed.get("error")`** handling unchanged for **non-rate-limit** API errors (e.g. 403 quota in JSON on HTTP 200 still raises immediately without retry — preserves **`test_api_error_object_raises`** behavior when code ≠ 429 and reason ≠ rateLimitExceeded).

7. **Rate-limit on HTTP 200 with error envelope:** If **`response.ok`** and **`_is_rate_limit_response(response.status_code, parsed)`** is true but helper returned without retry (should not happen — helper handles 429 before return). If helper returns **`response.ok`** with parsed error object indicating rate limit (edge case: HTTP 200 + error code 429): treat like today’s error path **after** retries inside helper — helper must not return success for rate-limit shapes. Ensure helper loops on **`_is_rate_limit_response`** regardless of **`response.ok`**.

   ⚠️ **Decision:** Rate-limit detection runs on **both** non-2xx and 2xx bodies **before** the caller treats the response as success. Non-rate-limit **`error`** objects still raise immediately on first attempt (no behavior change for **`code: 403` quota** test).

8. Do **not** export new private helpers via **`__all__`** — only **`search_google_cse`** remains public.

---

## Stage 3: Roster debug wiring for pacing trace (AC2)

**Done when:** With **`debug=True`**, discovery and resolve emit **`pace_detail`** lines as **`log.debug_detail(...)`** immediately **after** the existing per-term (or per-company) **`debug_index`** header and **before** hit-level detail lines; with **`debug=False`**, no new log lines and no callback passed.

### 3a. `run_inflow_discovery_batch` term loop

1. In **`src/core/roster.py`**, inside **`for term_i, term in enumerate(terms, start=1):`**, **before** the **`try:`** that calls **`search_google_cse`**:

```python
pace_lines: list[str] = []
pace_detail = pace_lines.append if debug else None
```

2. Change the **`search_google_cse(...)`** call to pass **`pace_detail=pace_detail`** as the last keyword argument. Leave all other arguments unchanged.

3. In the **`except (RuntimeError, ValueError) as exc:`** block, **after** the existing **`log.debug_index(...)`** call and **before** **`logger.warning(...)`**:

```python
for line in pace_lines:
    log.debug_detail(line)
```

4. In the **`try`** success path, **after** the existing **`log.debug_index(...)`** with **`outcome=f"{len(hits)} hit(s)"`** and **before** **`log.debug_detail(f"search_term=...")`**:

```python
for line in pace_lines:
    log.debug_detail(line)
```

Do **not** bump **`last_scan_at`** in the except path (unchanged). Do **not** stop the term loop on exhausted retries (parent open question #1 — continue remaining terms).

### 3b. `resolve_company_website`

1. At the start of the CSE block (after building **`query`**, before **`try:`**):

```python
pace_lines: list[str] = []
pace_detail = pace_lines.append if debug else None
```

2. Pass **`pace_detail=pace_detail`** into **`search_google_cse(...)`**.

3. In **`except (RuntimeError, ValueError) as exc:`**, after **`log.debug_index(...)`**, flush **`pace_lines`** via **`log.debug_detail`** (same loop as 3a).

4. In the success path, after **`log.debug_index(...)`** with **`outcome=f"{len(hits)} CSE hit(s)"`**, flush **`pace_lines`** before hit listing detail lines.

5. Confirm exhausted-retry **`RuntimeError`** still returns **`{"success": False, "state": None, "error": str(exc)}`** with **no** **`transition_company_state`** call (unchanged semantics — AC4).

---

## Self-Assessment

**Scope:** `Single-Component` — Touches **`GOOGLE_CSE_CONFIG`**, the CSE external client, and two roster call sites for debug callback wiring only; no dispatcher, UI, or test corpus changes.

**Conf:** `Medium` — Rate-limit detection covers HTTP 429 and Google's `rateLimitExceeded` envelope, but live API edge shapes may need UAT tuning of delay/pause literals rather than code changes.

**Risk:** `Medium` — Incorrect pacing slows all inflow batches globally; incorrect retry logic could mask non-rate-limit failures or still exhaust quota — mitigated by keeping existing `RuntimeError` raise paths for non-rate-limit errors.

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Plan compliance |
|------|-----------------|
| §1.3 DRY | Pacing/retry centralized in **`google_cse.py`**; roster only buffers callback lines |
| §1.4 / §2.1 config | All behavior literals in **`GOOGLE_CSE_CONFIG`**; secrets remain env-only |
| §1.5.1 debug | Pacing/retry trace via roster **`debug_detail`** under existing **`debug_index`** headers; no emission when **`debug=False`** |
| §2.5 external | No logging in external layer; **`pace_detail`** callback only |
| §2.6 state machine | No new transitions; discovery/resolve failure paths unchanged after exhausted retries |
| §3.3 imports | External may import **`src.utils.config`**; roster continues calling **`search_google_cse`** only |
| §3.5 naming | Config block name **`GOOGLE_CSE_CONFIG`** matches module/domain |

No conflicts requiring **`Conf: !!-NONE`**.

---

## Review (build)

**Built:** `origin/sub/AST-835/AST-837-google-cse-query-pacing-and-rate-limit-pause` @ `48ee9b1`

**Stages delivered:**
- Stage 1: `GOOGLE_CSE_CONFIG` literals — `6c424cb`
- Stage 2: inter-query pacing + rate-limit pause/retry in `google_cse.py` — `e4af754`
- Stage 3: `pace_detail` debug callback wiring in `run_inflow_discovery_batch` and `resolve_company_website` — `48ee9b1`

**Betty / qa-child:** Component tests for pacing delay spacing and 429 retry behavior per ticket AC1–AC2; existing `test_google_cse.py` regression gate.
