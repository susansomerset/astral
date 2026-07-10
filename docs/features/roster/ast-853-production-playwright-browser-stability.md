# AST-853 — Production Playwright browser stability (fetch_website didn't finish in production)

**Linear:** [AST-853 — Production Playwright browser stability](https://linear.app/astralcareermatch/issue/AST-853/production-playwright-browser-stability-fetch-website-didnt-finish-in-production)

**Parent (reference only — orchestration AC):** [AST-850 — fetch_website didn't finish in production](https://linear.app/astralcareermatch/issue/AST-850/fetch-website-didnt-finish-in-production)

**Publish ref:** `origin/sub/AST-850/AST-853-production-playwright-browser-stability` (origin only)

## Summary

Production **fetch_website** batches on Railway share one Firefox session across concurrent company scrapes (`Semaphore(3)`). Mid-batch browser crashes (`Exiting due to channel error`, `Target page, context or browser has been closed`) poison the shared context: every subsequent company hits the same opaque error, logs repeat identical launch/context failures without naming the failure class, and work crawls for hours. This ticket hardens Playwright **launch**, **session lifecycle**, and **failure classification** in the external layer, adds a **recoverable batch browser session** for **fetch_website**, and ensures each company scrape fails fast with a labeled infra error — without changing per-company state routing (**AST-854** owns **WEBSITE_FOUND_RETRY**, claim release, and batch completion AC).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add top-level `PLAYWRIGHT_CONFIG` block (launch timeouts, retry counts, page goto timeout, recovery cap) | utils |
| `src/external/playwright.py` | Failure classification, `PlaywrightInfraError`, launch retries, `BatchBrowserSession` + `create_batch_browser_session()`, `get_page` recovery hook, `check_connectivity` uses hardened launch | external |
| `src/core/roster.py` | `scrape_company_homepage_content` accepts optional `batch_session`; prefix infra errors with `[playwright:<failure_class>]`; non-debug WARNING log per company on infra failure | core |
| `src/core/gazer.py` | `fetch_website_batch` uses `create_batch_browser_session()` instead of `create_browser_context()`; pass `batch_session` into scrape helper | core |

**Out of scope (sibling AST-854):** `fail_state` / **WEBSITE_FOUND_RETRY** routing, dispatcher claim release, batch summary reconciliation, AST-538 debug additions beyond existing gazer `debug_index` paths.

**Out of scope (explicit):** `fetch_job_pages_batch`, `process_gazer_batch`, `scrape_jd_batch`, gaze, local dev browser install path changes.

---

## Stage 1: Config and failure taxonomy

**Done when:** `PLAYWRIGHT_CONFIG` is importable from `config.py`, and `classify_playwright_failure()` returns a stable failure class string for the production log signatures listed in AST-850 Original brief.

1. In `src/utils/config.py`, after the `RAILWAY_CONFIG` block (~line 2200), add:

```python
PLAYWRIGHT_CONFIG = {
    "launch_timeout_ms": 60_000,
    "launch_max_attempts": 3,
    "launch_retry_delay_seconds": 2.0,
    "page_goto_timeout_ms": 30_000,
    "connectivity_timeout_ms": 10_000,
    "context_recovery_max_attempts": 2,
    "company_scrape_timeout_seconds": 120,
    "firefox_user_prefs": {
        "security.sandbox.content.level": 0,
    },
}
```

   Plain literals only — no new env lookups (Railway path stays in `RAILWAY_CONFIG` / `start_server.py`).

2. In `src/external/playwright.py`, immediately after module logger setup (~line 22), add:

   - **`PLAYWRIGHT_INFRA_FAILURE_CLASSES`** — frozenset of strings:
     `launch_failure`, `launch_timeout`, `channel_error`, `context_closed`, `connectivity_failure`
   - **`def classify_playwright_failure(exc: BaseException) -> str`** — inspect `type(exc).__name__` and `str(exc).lower()`; map substrings in this order:
     - `"channel error"` → `channel_error`
     - `"target page, context or browser has been closed"`, `"browser has been closed"`, `"browser closed"` → `context_closed`
     - `"timeout"` + (`"launch"` in msg or `"firefox.launch"` in msg) → `launch_timeout`
     - `"could not launch firefox"` → `launch_failure`
     - `"timeout"` + (`"goto"` in msg or `"navigation"` in msg) → `navigation_timeout` (not infra — return as-is but not in infra frozenset)
     - default → `unknown`
   - **`def is_playwright_infra_failure(failure_class: str) -> bool`** — membership in `PLAYWRIGHT_INFRA_FAILURE_CLASSES`.
   - **`class PlaywrightInfraError(Exception)`** with attributes **`failure_class: str`**, **`detail: str`**; message format: `"[{failure_class}] {detail}"`.

⚠️ **Decision:** Infra vs site failure is classified in **external** only. Core may prefix error strings for logs; **AST-854** interprets `[playwright:…]` prefix for state routing — this ticket does not branch on it in gazer.

---

## Stage 2: Launch retries and batch browser session

**Done when:** `_launch_browser` retries per config; `create_batch_browser_session()` yields a session whose context can be recreated after a simulated `context_closed` error; `get_page(..., batch_session=session)` succeeds on the retry attempt.

1. In `_launch_browser` (`src/external/playwright.py` ~line 59):
   - Read **`cfg = PLAYWRIGHT_CONFIG`** (import from `src.utils.config`).
   - Replace single `pw.firefox.launch(...)` with a loop **`for attempt in range(1, cfg["launch_max_attempts"] + 1)`**:
     - Pass **`timeout=cfg["launch_timeout_ms"]`** to `launch`.
     - Pass **`firefox_user_prefs=cfg["firefox_user_prefs"]`** (drop inline dict).
     - On success: `_log.debug("Firefox launched successfully (attempt %d)", attempt)` and return browser.
     - On exception: `_log.warning("Firefox launch attempt %d/%d failed: %s: %s", attempt, max, type(e).__name__, e)`; if attempt < max, **`await asyncio.sleep(cfg["launch_retry_delay_seconds"])`**; else raise **`PlaywrightInfraError(classify_playwright_failure(e), str(e))`** from e.
   - Add **`import asyncio`** at module top if not present.

2. Add **`class BatchBrowserSession`** in the same file (before `create_browser_context`):

   - State: **`_pw`**, **`_browser`**, **`_context`**, **`_lock: asyncio.Lock`**, **`_headless: bool`**, **`_viewport: dict`**.
   - **`async def ensure_context(self) -> BrowserContext`**: if **`_context`** exists and **`_browser.is_connected()`** (guard with try/except — treat disconnected as dead), return **`_context`**; else call **`await self._open_fresh()`** under lock.
   - **`async def _open_fresh(self)`**: start **`async_playwright()`** if **`_pw`** is None; launch via **`_launch_browser`**, **`new_context(viewport=...)`**, assign **`_browser`/`_context`**.
   - **`async def recover(self, failure_class: str, reason: str)`**: under **`_lock`**, `_log.warning("playwright batch session recover failure_class=%s reason=%s", failure_class, reason)`; close **`_context`** and **`_browser`** best-effort; null handles; call **`_open_fresh()`**.
   - **`async def aclose(self)`**: close context, browser, stop playwright; null handles.

3. Add context manager:

```python
@asynccontextmanager
async def create_batch_browser_session(headless=True, viewport=None):
    session = BatchBrowserSession(headless=headless, viewport=viewport or {"width": 1280, "height": 2000})
    try:
        await session.ensure_context()
        yield session
    finally:
        await session.aclose()
```

4. Extend **`get_page`** signature: add **`batch_session: Optional[BatchBrowserSession] = None`**.

   - Read **`goto_timeout = PLAYWRIGHT_CONFIG["page_goto_timeout_ms"]`** and **`recovery_max = PLAYWRIGHT_CONFIG["context_recovery_max_attempts"]`**.
   - When **`batch_session`** is set, resolve context via **`await batch_session.ensure_context()`** instead of the **`context`** parameter for page creation ( **`context`** param still used when **`batch_session`** is None).
   - Wrap **`context.new_page()`** + optional **`page.goto(...)`** in a loop **`for recovery in range(recovery_max + 1)`**:
     - On exception: **`fc = classify_playwright_failure(e)`**; if **`batch_session`** and **`is_playwright_infra_failure(fc)`** and **`recovery < recovery_max`**: **`await batch_session.recover(fc, str(e))`** and continue; else if infra: raise **`PlaywrightInfraError(fc, str(e))`**; else re-raise original.
   - Replace hardcoded **`timeout=30000`** on **`page.goto`** with **`goto_timeout`**.

5. Leave **`create_browser_context()`** calling **`_launch_browser`** (inherits retries) — no batch recovery in that path (single-company callers unchanged).

---

## Stage 3: fetch_website wiring and observability

**Done when:** `fetch_website_batch` uses one recoverable session for the whole batch; a scrape failure from dead browser context produces a log line containing **`[short_name]`**, **`failure_class=`** or **`[playwright:context_closed]`**, and the batch **`gather`** completes without an unhandled exception (individual companies still fail — state unchanged from today).

1. In **`scrape_company_homepage_content`** (`src/core/roster.py` ~line 1537):
   - Add optional kwarg **`batch_session=None`**.
   - Import **`PlaywrightInfraError`**, **`classify_playwright_failure`**, **`is_playwright_infra_failure`** from `src.external.playwright`.
   - When **`batch_session`** is not None: call **`get_page(batch_session= batch_session, url=company_website)`** (do not pass **`browser_context`**).
   - In **`except Exception as scrape_err`** block:
     - If **`isinstance(scrape_err, PlaywrightInfraError)`**: set **`fc = scrape_err.failure_class`**, **`msg = scrape_err.detail`**.
     - Else: **`fc = classify_playwright_failure(scrape_err)`**, **`msg = str(scrape_err)`**.
     - If **`is_playwright_infra_failure(fc)`**: set **`out["error"] = f"[playwright:{fc}] {msg}"`** and **`logger.warning("[%s] playwright infra failure failure_class=%s %s", short_name, fc, msg)`** (always — not debug-gated).
     - Else: keep **`out["error"] = str(scrape_err)`** (site/navigation failures unchanged).

2. In **`fetch_website_batch`** (`src/core/gazer.py` ~line 299):
   - Replace import/use of **`create_browser_context`** with **`create_batch_browser_session`** for this function only.
   - Change:

```python
async with create_batch_browser_session() as batch_session:
```

   - Pass **`batch_session=batch_session`** into **`scrape_company_homepage_content(...)`** (remove **`browser_context=browser_context`**).
   - Wrap the body of **`_fetch_one`** (scrape + persist path only, not semaphore acquire) with:

```python
await asyncio.wait_for(
    _fetch_one_inner(...),
    timeout=PLAYWRIGHT_CONFIG["company_scrape_timeout_seconds"],
)
```

     where **`_fetch_one_inner`** holds the current scrape logic; on **`asyncio.TimeoutError`**: log **`logger.warning("[%s] playwright infra failure failure_class=scrape_timeout batch_id=%s", short_name, batch_id)`**, set scrape error equivalent **`[playwright:scrape_timeout] company scrape exceeded Ns`** — treat as infra for logging only; call existing fail path (**`fail_state`**, **`save_company_data`**) **unchanged** (still **`CANNOT_READ_WEBSITE`** until AST-854).

   - Import **`PLAYWRIGHT_CONFIG`** from config in gazer.

3. In **`check_connectivity`** (`src/external/playwright.py` ~line 433):
   - Use **`timeout=PLAYWRIGHT_CONFIG["connectivity_timeout_ms"]`** on goto.
   - On exception, log **`check_connectivity failed failure_class=%s: %s`** with **`classify_playwright_failure(e)`** before returning **`False`**.

⚠️ **Decision:** Per-company **`wait_for`** wall clock prevents silent hang when Playwright wedged; **`scrape_timeout`** is logged as infra but is **not** added to **`PLAYWRIGHT_INFRA_FAILURE_CLASSES`** — AST-854 may treat it like other infra retries.

---

## Self-Assessment

**Scope:** `Single-Component` — primary work in `playwright.py` and `config.py`; two small core touch points (`scrape_company_homepage_content`, `fetch_website_batch` only) to wire the batch session and labeled logs.

**Conf:** `Medium` — AST-317 and existing launch sandbox prefs establish the pattern; Railway channel-error recovery is new but bounded by explicit retry caps and lock-serialized session recreate.

**Risk:** `Medium` — `fetch_website` hot path changes session lifecycle; mitigated by limiting gazer wiring to this one batch, keeping state transitions identical, and capping launch/recovery/scrape timeouts in config.

---

## ASTRAL_CODE_RULES self-review

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Single `BatchBrowserSession`, one classifier, one launch retry loop — no duplicate recovery in gazer/roster. |
| §2.1 config | All limits in `PLAYWRIGHT_CONFIG`; no magic numbers in loops. |
| §2.5 bright line | Browser I/O stays external; gazer orchestrates; roster scrape helper only formats errors/logs. |
| §3.3 imports | Core imports external + utils only; no new cross-layer violations. |
| §1.5 logging | Infra WARNING lines are operational (not debug-contract); existing AST-538 `debug_index` paths in gazer unchanged. |

No conflicts requiring plan revision.

---

## Execution contract (developer agent)

- Execute stages **1 → 2 → 3** in order; one commit per stage on **`epic worktree`**, then publish to **`origin/sub/AST-850/AST-853-production-playwright-browser-stability`**.
- Do **not** change **`fail_state`** / **`pass_state`**, dispatcher claim logic, or **`fetch_job_pages_batch`** in this ticket.
- Do **not** add or edit files under **`tests/`** — Betty owns manifest after **Code Complete**.
- If production log signatures do not match classifier substrings during build, **stop** and comment on **AST-850** with proposed substring additions — do not guess new failure classes silently.

---

## Review (build stub)

**Publish ref:** `origin/sub/AST-850/AST-853-production-playwright-browser-stability`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `842e922` | `PLAYWRIGHT_CONFIG` + failure taxonomy |
| 2 | `7eea584` | Launch retries, `BatchBrowserSession`, `get_page` recovery |
| 3 | `aa8cfad` | `fetch_website_batch` wiring, scrape timeout, labeled infra logs |
