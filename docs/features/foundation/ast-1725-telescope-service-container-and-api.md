# Telescope service container and API

**Linear:** [AST-1725](https://linear.app/astralcareermatch/issue/AST-1725)
**Parent:** [AST-1721](https://linear.app/astralcareermatch/issue/AST-1721) — Astral Telescope — stateless headless-scraping microservice (per-URL)
**Publish ref:** `sub/AST-1721/AST-1725-telescope-service-container-and-api`

Stand up a process-isolated FastAPI Telescope under `service/telescope/`: one Firefox per replica, fresh browser context per URL, RAM semaphore + hard request timeout + recycle-after-N, bearer auth from env, console-only logs, and contract endpoints `POST /telescope`, `POST /telescope/html`, `GET /healthz`. Browser interaction only — no Surfer-shared post-render helpers (`_cull_html`, delimiter splits, vendor fingerprint). Does not own the platform drop-in ([AST-1726](https://linear.app/astralcareermatch/issue/AST-1726)) or Railway/CI wiring ([AST-1727](https://linear.app/astralcareermatch/issue/AST-1727)).

## Explicit scope gate

Ticket **## Scope** names exactly:

- `service/telescope/` — **new** — FastAPI app package: lifespan browser session, `/telescope`, `/telescope/html`, `/healthz`, browser-interaction helpers only (navigate / capture / load-all / cookie-dismiss / readiness); console-only logging; no fork of post-render cull/split helpers that Surfer must share.
- `service/telescope/requirements.txt` — **new** — Telescope-only deps (Playwright pin matching the image, FastAPI, uvicorn, etc.).
- `service/telescope/Dockerfile` — **new** — Official Playwright Python image, Firefox, single uvicorn worker, non-root, `--init`, memory/`/dev/shm` sizing.

Every row in **Files Changed** is under those paths. Technical kinds covered: FastAPI routes + lifespan one-Firefox session; per-request fresh context + semaphore + `wait_for` timeout + recycle-after-N; cookie dismiss always; expand default on; wait_ready default off as generic stability/min-chars only; rendered capture artifacts (no cull); console-only logging; env bearer; Dockerfile + Telescope requirements. No `railway.toml`, no `src/**`, no platform client, no CI import fence (those are AST-1726 / AST-1727).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `service/telescope/__init__.py` | Empty package marker | service |
| `service/telescope/settings.py` | Env + service-local constants (bearer, concurrency, timeouts, recycle N, cookie selectors, firefox prefs, wait_ready knobs) — **no** `src` imports | service |
| `service/telescope/logging_util.py` | Stdlib logging → stdout/stderr only; configure root logger at process start | service |
| `service/telescope/auth.py` | FastAPI dependency: require `Authorization: Bearer <TELESCOPE_BEARER_TOKEN>` | service |
| `service/telescope/browser.py` | One-Firefox lifespan pool: launch, fresh context per acquire, semaphore, recycle-after-N, `recover`, health poke | service |
| `service/telescope/interact.py` | Navigate, cookie dismiss (selector + fuzzy), expand/`load_all`, generic `wait_ready` | service |
| `service/telescope/capture.py` | Visible text (single vs multi-match), links `[{href, text}]`, raw scoped HTML (**no** cull) | service |
| `service/telescope/app.py` | FastAPI app, lifespan, `POST /telescope`, `POST /telescope/html`, `GET /healthz` | service |
| `service/telescope/requirements.txt` | Pin `playwright==1.49.1`, `fastapi`, `uvicorn[standard]`, `pydantic` | service |
| `service/telescope/Dockerfile` | `FROM mcr.microsoft.com/playwright/python:v1.49.1-jammy`; copy only this package; non-root; `--init`; single uvicorn worker | service |

**Out of this ticket (do not touch):** `service/telescope/railway.toml` / Railway deploy (AST-1727); `.github/workflows/**` import fence (AST-1727); `src/external/telescope.py` / delete `playwright.py` / core import rewires / `src/utils/config.py` / root `requirements.txt` (AST-1726); any `src/**` import from service or vice versa; Surfer extension; `_cull_html` / vendor / `request_urls` / `frame_urls` on the service; `tests/` / `docs/test-bible/**` (Betty).

## Canon notes (planner)

- **Patterns (pending):** `patt.external.web-scraping-via-telescope` — flagged pending Archie; **not** scoring law this pass. Id-only.
- **Statute amendment (pending):** `stat.layers.import-rules` bidirectional `service/*`↔`src/` ban is requested, not amended. This ticket still **implements** the fence on the service side (zero `src` imports; image copies only `service/telescope/`). CI enforcement is AST-1727.
- **Logging statutes** (`stat.logging.error` / `.warning` / `.info` / `.debug`): paths in those files are `src/**` and channel is `src.utils.logging.get_logger`. Telescope has **no DB / no `app_log`**. Apply the **semantic** (error once at handler with facts + traceback; warning for soft-fails; succinct info progress; debug at joints) via **stdlib logging to console** — do not import `src.utils.logging`.

## Stage 1: Package skeleton, settings, console logging, auth

**Done when:** `service/telescope/` exists with settings readable from env, stdout logging configured, and a FastAPI dependency that rejects missing/wrong bearer with 401. No browser code yet. `uvicorn` can import `app:app` (routes may be stubs).

1. Create `service/telescope/__init__.py` (empty).

2. Create `service/telescope/settings.py` with a `Settings` dataclass (or plain module constants) loaded once at import from env:

| Name | Env | Default | Role |
|------|-----|---------|------|
| `bearer_token` | `TELESCOPE_BEARER_TOKEN` | **required** (raise on missing at app startup) | Auth |
| `max_concurrent_pages` | `TELESCOPE_MAX_CONCURRENT_PAGES` | `3` | RAM semaphore |
| `request_timeout_seconds` | `TELESCOPE_REQUEST_TIMEOUT_SECONDS` | `60` | Per-request `asyncio.wait_for` |
| `recycle_after_n` | `TELESCOPE_RECYCLE_AFTER_N` | `50` | Browser recycle count |
| `port` | `TELESCOPE_PORT` | `8080` | Documented for local/Docker; uvicorn binds in Dockerfile CMD |
| `page_goto_timeout_ms` | `TELESCOPE_PAGE_GOTO_TIMEOUT_MS` | `30000` | `page.goto` |
| `launch_timeout_ms` | `TELESCOPE_LAUNCH_TIMEOUT_MS` | `60000` | Firefox launch |
| `launch_max_attempts` | — | `3` | Launch retries |
| `launch_retry_delay_seconds` | — | `2.0` | Between launch attempts |
| `viewport` | — | `{"width": 1280, "height": 2000}` | Context viewport |
| `firefox_user_prefs` | — | `{"security.sandbox.content.level": 0}` | Match platform `PLAYWRIGHT_CONFIG` |
| `cookie_dismiss_selectors` | — | Copy the list from platform `ASTRAL_CONFIG["cookie_dismiss_selectors"]` in `src/utils/config.py` (same strings, service-owned) | Cookie dismiss |
| `cookie_fuzzy_accept_keywords` | — | `["accept", "allow", "agree", "confirm", "ok", "got it"]` | Fuzzy dismiss |
| `wait_ready_max_ms` | — | `20000` | Generic wait_ready |
| `wait_ready_poll_ms` | — | `500` | Poll interval |
| `wait_ready_stability_polls` | — | `2` | Stable length polls |
| `wait_ready_min_chars` | — | `400` | Min visible chars |

⚠️ **Decision:** Cookie selectors and firefox prefs are **duplicated** into `settings.py`, not imported from `src/utils/config.py`. Import fence forbids `src` imports; AST-1726 owns the platform copy. Drift is acceptable until a later shared-config epic (out of scope).

3. Create `service/telescope/logging_util.py`:
   - `configure_logging()` → stdlib `logging.basicConfig` to **stdout**, level from env `TELESCOPE_LOG_LEVEL` default `INFO`, format including level + logger name + message.
   - `get_logger(name)` → `logging.getLogger(name)` (stdlib only).
   - Call `configure_logging()` at the top of `app.py` module load (before routes).

4. Create `service/telescope/auth.py`:
   - FastAPI dependency `require_bearer(authorization: Annotated[str | None, Header()] = None)` (or `HTTPBearer`).
   - Compare token to `settings.bearer_token` with constant-time compare (`hmac.compare_digest`).
   - Missing/invalid → HTTP 401 `{"detail": "unauthorized"}`.
   - Apply this dependency to `/telescope` and `/telescope/html` **and** `/healthz` (private service — no public health without bearer).

⚠️ **Decision:** `/healthz` also requires bearer. Parent says private networking + bearer; an unauthenticated health check would be an SSRF-adjacent probe surface. AST-1727 Railway probes must send the same secret (document in a one-line comment above the dependency).

5. Create stub `service/telescope/app.py`:
   - `app = FastAPI(title="Astral Telescope", lifespan=...)` — lifespan may be a no-op stub that yields until Stage 2.
   - Register three routes with `dependencies=[Depends(require_bearer)]` returning placeholder 501 or empty bodies is **not** allowed past Stage 3 — for Stage 1, routes may raise `HTTPException(501)` only if Stage 2/3 are not yet committed; prefer leaving route bodies for Stage 3 and only proving import + auth in Stage 1 via a minimal `GET /healthz` that returns `{"status": "starting"}` **without** browser until Stage 2 replaces it.

⚠️ **Decision (Stage 1 `/healthz`):** Stage 1 may return `{"status": "starting"}` with 200 **only** until Stage 2 wires the real browser poke. Stage 2 **must** replace this with a live browser poke before Stage 3 lands contract endpoints. Do not ship Stage 3 while `/healthz` is still the stub.

**Stage 1 commit message:** `code(AST-1725): telescope package skeleton auth logging`

## Stage 2: One Firefox per replica — pool, semaphore, recycle, health poke

**Done when:** App lifespan launches exactly one Firefox; `GET /healthz` (with bearer) opens a fresh context, confirms the browser is connected (e.g. `about:blank` + `browser.is_connected()`), closes the context in `finally`, and returns `{"status": "ok"}`. On browser-down, return 503 with a warning/error log. Semaphore and recycle counters exist and are used by a public `async with pool.page() as page` API even if no scrape routes call it yet.

1. Create `service/telescope/browser.py` with class `BrowserPool`:

   - Fields: `_playwright`, `_browser`, `_lock` (`asyncio.Lock`), `_semaphore` (`asyncio.Semaphore(settings.max_concurrent_pages)`), `_request_count` (int), `_recycle_after_n`.
   - `async def start(self)` — `async_playwright()` → launch Firefox with `settings.firefox_user_prefs`, `timeout=settings.launch_timeout_ms`, retry loop matching platform `_launch_browser` (max attempts / sleep). Log launch failures at **warning** per attempt; final failure → **exception** log then raise.
   - `async def stop(self)` — close browser + stop playwright (best-effort).
   - `async def recover(self, reason: str)` — under lock: warning log with reason; close browser; relaunch (same as platform `BatchBrowserSession.recover` intent).
   - `@asynccontextmanager async def page(self)`:
     1. `async with self._semaphore`
     2. Under lock, if `_request_count >= recycle_after_n` or browser disconnected → `recover("recycle" | "disconnected")` and reset `_request_count` to 0
     3. `context = await self._browser.new_context(viewport=settings.viewport)`
     4. `page = await context.new_page()`
     5. `try: yield page` / `finally: await context.close()` (always — never reuse context across requests)
     6. Increment `_request_count` after successful acquire (or at end of request — either is fine; pick **after** context close so a hung request still counts toward recycle)
   - `async def health_poke(self) -> bool` — `async with self.page() as page: await page.goto("about:blank", timeout=…). return self._browser.is_connected()`

⚠️ **Decision:** Do **not** copy `BatchBrowserSession` verbatim. Platform session reuses one shared context across companies; Telescope **must** use a fresh context per URL (parent FS §6). One browser + fresh contexts is intentional.

2. Wire lifespan in `app.py`:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    if not settings.bearer_token:
        raise RuntimeError("TELESCOPE_BEARER_TOKEN is required")
    pool = BrowserPool()
    await pool.start()
    app.state.pool = pool
    try:
        yield
    finally:
        await pool.stop()
```

3. Replace Stage 1 `/healthz` stub: call `await request.app.state.pool.health_poke()`; success → 200 `{"status": "ok"}`; failure → 503 `{"status": "unhealthy"}` and log once at exception/warning with live facts (no stack spam on expected soft disconnect — use `logger.exception` only for unexpected throws).

**Stage 2 commit message:** `code(AST-1725): one-firefox pool healthz`

## Stage 3: Interact + capture helpers and contract endpoints

**Done when:** With bearer auth, `POST /telescope` and `POST /telescope/html` navigate a URL under the pool, always dismiss cookies, honor `expand` (default **true**) and `wait_ready` (default **false**, generic only), return the JSON shapes below, enforce `settings.request_timeout_seconds` via `asyncio.wait_for`, and never import `src` or call `_cull_html`.

### Request / response contracts

**`POST /telescope`** body (Pydantic):

| Field | Type | Default |
|-------|------|---------|
| `url` | `str` (required, non-empty) | — |
| `selector` | `str \| null` | `null` (= body / page visible text) |
| `expand` | `bool` | `true` |
| `wait_ready` | `bool` | `false` |
| `links` | `bool` | `true` |

Response:

```json
{
  "final_url": "<page.url after redirects>",
  "text": "<string>" | ["<blob>", "..."],
  "links": [{"href": "...", "text": "..."}]
}
```

- When `links` is `false`, **omit** the `links` key (or set to `[]` — **pick omit**; document in OpenAPI `response_model` with optional field).
- `text` is a **string** when the resolved selector yields 0 or 1 node; a **list of strings** when `querySelectorAll` returns 2+ nodes (parent AC 5 / Notes).

**`POST /telescope/html`** body:

| Field | Type | Default |
|-------|------|---------|
| `url` | `str` (required) | — |
| `selector` | `str \| null` | `null` (= `body` outerHTML) |
| `expand` | `bool` | `true` |
| `wait_ready` | `bool` | `false` |

Response:

```json
{ "final_url": "...", "html": "<raw rendered HTML — NOT culled>" }
```

No `cull` field on the service (platform AST-1726 applies cull in `src/external/telescope.py`).

### Helpers

4. Create `service/telescope/interact.py`:

   - `async def navigate(page, url: str) -> None` — `page.goto(url, wait_until="domcontentloaded", timeout=settings.page_goto_timeout_ms)` then a short settle `wait_for_timeout(500)` (mirror platform `navigate_and_wait_for_ready` / `wait_for_page_ready_after_navigation` spirit without careers selectors).
   - `async def dismiss_cookies(page) -> None` — port `_try_dismiss_cookie_banner` then `_try_dismiss_cookie_banner_fuzzy` from `src/external/playwright.py` using **settings** selectors/keywords (copy logic; do not import playwright.py). Soft-fail: log debug if none clicked; never raise.
   - `async def expand_page(page) -> None` — port `load_all_jobs` scroll + "Load More" loop from `playwright.py` (~lines 2290–2334) without the unused `short_name` logging dependency.
   - `async def wait_ready_generic(page) -> dict` — port the **stability / min_chars** half of `wait_for_careers_list_readiness` only: poll visible-text length until `wait_ready_min_chars` + `wait_ready_stability_polls` consecutive equal lengths, or `wait_ready_max_ms` elapses. **Do not** use `listing_selectors` / careers hits. Do not call `expand_page` from inside wait_ready (expand is a separate request flag, already applied before wait_ready in the route).

5. Create `service/telescope/capture.py`:

   - `async def capture_text(page, selector: str | None) -> str | list[str]`:
     - If `selector` is `None`, `""`, `"page"`, or `"body"` (case-insensitive): run the same JS as platform `extract_visible_text` (clone body, strip header/footer/nav/hidden) → return that **string**.
     - Else: `querySelectorAll(selector)`; for each element, take `innerText` (trimmed). 0 matches → `""`; 1 → that string; 2+ → `list[str]`.
   - `async def capture_links(page) -> list[dict]`:
     - Evaluate JS collecting `a[href]` where `href` starts with `http`; each item `{"href": a.href, "text": (a.innerText || "").trim()}`.
   - `async def capture_html(page, selector: str | None) -> str`:
     - `None` / `""` / `"body"` → `document.body.outerHTML` (or `""` if no body).
     - `"page"` → `document.documentElement.outerHTML`.
     - Else → `querySelector(selector)?.outerHTML || ""` (single first match for HTML endpoint — multi-match array is text-endpoint only).
     - **Do not** call any cull/strip of tags beyond what the browser already rendered.

6. Shared scrape pipeline in `app.py` (private async helper `_run_browser_job(pool, url, expand, wait_ready, work)`):

   1. `async with pool.page() as page:`
   2. `await navigate(page, url)`
   3. `await dismiss_cookies(page)` — always
   4. If `expand`: `await expand_page(page)`
   5. If `wait_ready`: `await wait_ready_generic(page)`
   6. `return await work(page)`  # capture_*
   - Wrap the whole job in `asyncio.wait_for(..., timeout=settings.request_timeout_seconds)`.
   - On `TimeoutError`: warning log with url + timeout; HTTP 504 `{"detail": "timeout"}`.
   - On other exceptions: `logger.exception` once with url + exc type/message; HTTP 502 `{"detail": "scrape_failed"}`. Do not log-and-re-raise.

7. Wire routes:

   - `POST /telescope` → pipeline then `text = await capture_text(...)`; `final_url = page.url` (capture inside `work` before context closes — read `page.url` inside `work`); if `links`: include `capture_links`; build response dict.
   - `POST /telescope/html` → pipeline then `html = await capture_html(...)`.
   - Missing/empty `url` → 400 `{"detail": "url required"}`.

8. Info logs (succinct): one line per successful scrape — `telescope ok method=/telescope final_url=... chars=N` (or `html_len=N`). Debug at joints: navigate start/end, expand start/end, wait_ready outcome, cookie dismiss result.

**Stage 3 commit message:** `code(AST-1725): telescope scrape endpoints`

## Stage 4: requirements.txt + Dockerfile

**Done when:** `docker build -f service/telescope/Dockerfile .` produces an image that runs one uvicorn worker as non-root, with Playwright/Firefox matching the base image pin, and the container filesystem has **no** `src/` tree.

1. Write `service/telescope/requirements.txt`:

```
playwright==1.49.1
fastapi>=0.115.0,<1
uvicorn[standard]>=0.30.0,<1
pydantic>=2,<3
```

⚠️ **Decision:** Pin Playwright **1.49.1** to match `mcr.microsoft.com/playwright/python:v1.49.1-jammy`. If build discovers that tag missing on MCR, stop and comment on parent AST-1721 with the 404 — do not silently float to another major without a plan revision.

2. Write `service/telescope/Dockerfile`:

```dockerfile
# syntax=docker/dockerfile:1
FROM mcr.microsoft.com/playwright/python:v1.49.1-jammy

ENV PYTHONUNBUFFERED=1 \
    TELESCOPE_PORT=8080 \
    TELESCOPE_MAX_CONCURRENT_PAGES=3 \
    TELESCOPE_REQUEST_TIMEOUT_SECONDS=60 \
    TELESCOPE_RECYCLE_AFTER_N=50

WORKDIR /app

# Copy only the Telescope package — src/ must not exist in this image.
COPY service/telescope/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY service/telescope/ /app/

# Non-root (image may already define pwuser — use it if present, else create telescope)
USER pwuser

EXPOSE 8080

# --init is expected via docker run / Railway (reap zombies). Single worker = one Firefox.
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
```

3. Add a short comment block at the top of the Dockerfile noting: memory limit and `/dev/shm` sizing are **deploy** concerns (AST-1727 / Railway); local `docker run` should pass `--init --shm-size=1g` (document in comment only — do not add README).

4. Verify by inspection (no need to push an image in this ticket): every `.py` file under `service/telescope/` has **zero** imports matching `src` / `astral` package paths (`rg -n '^(from|import) src' service/telescope` must be empty).

**Stage 4 commit message:** `code(AST-1725): telescope Dockerfile and requirements`

## Execution contract

The plan is binding. The builder:

- Executes steps in order within a stage, and stages in order.
- Does not add files outside **Files Changed**.
- Does not implement AST-1726 / AST-1727 scope.
- On ambiguity or codebase drift → stop, comment on **parent** AST-1721 with the Stage blocked format from plan-child, wait.

## Estimate

Confirm Chuckles estimate: 5 — agree
