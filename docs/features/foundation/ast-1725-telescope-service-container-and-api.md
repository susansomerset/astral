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
| `selector` | `str \| null` | `null` (= full document / `documentElement` outerHTML; `"body"` for body-only) |
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
     - `None` / `""` / `"page"` → `document.documentElement.outerHTML` (AST-1729).
     - `"body"` → `document.body.outerHTML` (or `""` if no body).
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

## Joan validate

[plan-rubric]
**Ticket:** AST-1725
**Overall:** APPROVED
**Corpus:** 751624d7ebdf9bc441fc3d08a51ae751ea8026af
**Publish ref tip:** 18412e4794d31d71351f622883d9f9027a6c79a3 (`origin/sub/AST-1721/AST-1725-telescope-service-container-and-api`)

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| stat.logging.error | B | | |
| stat.logging.warning | B | | |
| stat.logging.info | B | | |
| stat.logging.debug | B | | |
| patt.external.web-scraping-via-telescope | X | | pending Archie — id-only; not scoring law this pass |
| stat.layers.import-rules (amendment request) | B | | |

## Traceability

AC1→S1+S4; AC2→Explicit scope gate + S4§4 + Canon notes (service-side zero `src` imports; CI bidirectional fence AST-1727); AC3→S2 `/healthz` poke + S3 contract routes; AC4→S3 request defaults + no service cull (platform cull AST-1726); AC5→S3 `capture_text` multi-match; AC9→S4 Dockerfile/uvicorn separate process (platform base URL AST-1726); AC10→S1 `settings` + `auth.py`; AC11→S1 `logging_util.py` stdlib stdout only; AC12→S2 semaphore/recycle/timeout + S4 single-worker image.

## Findings

### discuss — Canon Scope gap (do not score)

- **Severity:** discuss
- **Location:** Parent Canon Scope vs frozen Citations
- **Finding:** `astral.config.config-source-of-truth` plainly governs duplicated cookie selectors / firefox prefs in `settings.py` but is absent from the frozen list.
- **Recommendation:** Archie may amend Canon Scope at Discussion for Radia comparability; plan’s duplicate-not-import Decision is explicit and fence-correct.

### discuss — Canon Scope gap (do not score)

- **Severity:** discuss
- **Location:** Citations / `patt.external.web-scraping-via-telescope`
- **Finding:** Pattern is pending Archie approval; plan correctly defers scoring and keeps browser I/O in `service/telescope/` only with no post-render fork.
- **Recommendation:** No plan change; treat as id-only until Archie approves.

### acceptable

- **Severity:** acceptable
- **Location:** Canon notes / logging statutes
- **Finding:** Logging directives’ `applies_when.paths` are `src/**`; Telescope applies **semantic** via stdlib console logging (no `src.utils.logging` import). Intentional channel variance for process isolation.
- **Recommendation:** None — B grades reflect documented variance, not violation.

### acceptable

- **Severity:** acceptable
- **Location:** Out-of-scope table; AST-1726 / AST-1727
- **Finding:** `railway.toml`, CI import fence, platform `telescope.py`, and config pool wiring correctly deferred to siblings; no scope creep in Files Changed.
- **Recommendation:** None.

### acceptable

- **Severity:** acceptable
- **Location:** Stage 1 `/healthz` stub → Stage 2 replacement
- **Finding:** Transient `{"status":"starting"}` before Stage 2 is bounded by sequential stage contract; Stage 2 gate prevents shipping contract endpoints atop a stub health poke.
- **Recommendation:** None.

### acceptable — R6 definition fidelity

- **Severity:** acceptable
- **Location:** Explicit scope gate; Stages 1–4; `## Estimate`
- **Finding:** Plan matches child Scope and parent slice for service container/API only. All Files Changed rows sit under ticket Scope. Self-assessment (`Confirm Chuckles estimate: 5 — agree`) is honest for four staged commits. No `!!-NONE` conf gaps.
- **Recommendation:** None.

### acceptable — Plan Discuss

- **Severity:** acceptable
- **Location:** Linear comments
- **Finding:** Plan Discuss rounds completed: **0** (status Plan Ready; assignee Joan).
- **Recommendation:** N/A.

context_tokens≈52000

[plan-rubric] PROCEED (Commit: 18412e4794d31d71351f622883d9f9027a6c79a3) Service container plan sound

## Review (build stub)

**Built:** `origin/sub/AST-1721/AST-1725-telescope-service-container-and-api` @ `c00550bb`.

**Stages delivered:**
- Stage 1: package skeleton, settings, console logging, bearer auth — `4ddd4af6`.
- Stage 2: one-Firefox `BrowserPool` + live `/healthz` poke — `7628e1a7`.
- Stage 3: `/telescope` + `/telescope/html` (interact + capture, no cull) — `e544249b`.
- Stage 4: `requirements.txt` + Dockerfile (Playwright `1.49.1-jammy`) — `c00550bb`.

**Betty:** new service surface — contract defaults (expand/links/wait_ready), multi-match text, bearer 401, healthz browser poke, no-`src` import fence under `service/telescope/`, timeout/504 paths.

## Radia review

[code-rubric]
**Ticket:** AST-1725
**Publish ref:** `3a1cce4b7bf91d73776616c50678082c8679ebcc` (`origin/sub/AST-1721/AST-1725-telescope-service-container-and-api`)
**Corpus:** `751624d7ebdf9bc441fc3d08a51ae751ea8026af`
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| stat.logging.error | B | | |
| stat.logging.warning | B | | |
| stat.logging.info | B | | |
| stat.logging.debug | B | | |
| patt.external.web-scraping-via-telescope | X | | pending Archie — id-only; not scoring law this pass |
| stat.layers.import-rules (amendment request) | B | | |

## Column diff vs plan stage

(aligned)

## Frame diff

(none)

## Findings

### discuss — Canon Scope gap (do not score)

- **Severity:** discuss
- **Location:** Parent Canon Scope vs frozen Citations; `service/telescope/settings.py` duplicated cookie selectors / firefox prefs
- **Finding:** `stat.config.config-source-of-truth` plainly governs duplicated platform config in `settings.py` but is absent from the frozen list. Implementation matches the plan’s explicit duplicate-not-import Decision and service-side import fence.
- **Recommendation:** Archie may amend Canon Scope at Discussion for future comparability; no code change required on this tip.

### discuss — pending pattern (do not score)

- **Severity:** discuss
- **Location:** Citations / `patt.external.web-scraping-via-telescope`
- **Finding:** Pattern id does not resolve in active corpus (`canon_clerk expand` → unknown). Diff keeps browser I/O under `service/telescope/` with no post-render cull fork — consistent with plan deferral.
- **Recommendation:** Remains id-only until Archie approves the pattern.

### advisory — logging semantic variance (channel)

- **Severity:** advisory
- **Location:** `service/telescope/logging_util.py`; all `_log.*` call sites
- **Finding:** Logging statutes’ `applies_when.paths` are `src/**` and channel is `src.utils.logging.get_logger`. Telescope applies semantics via stdlib `logging` to stdout — intentional process isolation per plan Canon notes. Exception bodies omit an explicit product next-step line (e.g. “returning 502”) though handlers do return structured HTTP errors.
- **Recommendation:** Acceptable B variance; optional polish in a later logging pass if Telescope gets its own surface statute.

### advisory — silent soft-fail in expand

- **Severity:** advisory
- **Location:** `service/telescope/interact.py` — `expand_page` load-more loop
- **Finding:** `except Exception: break` swallows load-more click failures with no warning/debug line.
- **Recommendation:** Optional `debug` on break for operability; not a canon violation given expand is best-effort.

### advisory — recover duplication

- **Severity:** advisory
- **Location:** `service/telescope/browser.py` — `page()` vs `recover()`
- **Finding:** Recycle/disconnect path inlines close+relaunch; `recover()` exists but is unused from `page()`.
- **Recommendation:** Mechanical refactor only; behavior matches plan.

### advisory — branch diff carry

- **Severity:** advisory
- **Location:** `origin/dev...origin/sub/AST-1721/AST-1725-telescope-service-container-and-api` (full three-dot diff)
- **Finding:** Ticket-scoped product surface is 18 files (~1.5k LOC: `service/telescope/`, `tests/component/service/`, bible row, harness tweak, plan doc). Full branch diff also carries large `canon/` migration and unrelated test-bible reshuffles from epic line — outside AST-1725 Files Changed.
- **Recommendation:** No action on AST-1725 product; parent merge hygiene only.

## What's solid

- All four plan stages landed on publish ref (`4ddd4af6` → `c00550bb`) plus Betty `test` + `merge-tests` at tip.
- Contract endpoints match plan: bearer on `/healthz`, `/telescope`, `/telescope/html`; defaults `expand=true`, `links=true`, `wait_ready=false`; links key omitted when `links=false`; empty url → 400; timeout → 504 warning + 502 exception-once paths.
- `BrowserPool`: one Firefox, fresh context per URL, semaphore, recycle-after-N, authenticated health poke.
- Zero `src` imports under `service/telescope/`; Dockerfile pins Playwright `1.49.1-jammy`, `USER pwuser`, single uvicorn worker, copies package only.
- Component tests + `docs/test-bible/service/telescope.md` align with Betty manifest; estimate **5** footprint is honest.

## Recommended actions (downstream only — not executed here)

- Chuckles: append this artifact to the issue doc, commit `docs(AST-1725): Radia review — clean`, push, post slim upshot `--as radia`, move to Review Posted.
- datt: PROCEED → User Testing (no `resolve-child` round needed).

context_tokens≈38000

## Resolution

**Date:** 2026-09-20  
**Radia:** CLEAN / PROCEED — no fix-now; discuss + advisory only (config duplication Canon Scope gap, pending pattern id, logging channel variance, expand soft-fail debug, recover duplication). No product changes.

**§9a:** Restacked publish ref onto `origin/dev` via `sync-child.sh` (no `origin/ftr/AST-1721` yet). Dry-run `merge-tree` vs `origin/dev` clean after publish.

## Bug: AST-1729 — Telescope HTML returns body-only when no selector set

### As-is

`POST /telescope/html` with `selector` omitted / `null` / `""` returns `document.body.outerHTML` only (no `<html>` / `<head>`).

### To-be

With no selector set (and with explicit `"page"`), Telescope HTML returns the full document (`document.documentElement.outerHTML`). Explicit `"body"` still returns body-only.

### Repro

1. Start Telescope with `TELESCOPE_BEARER_TOKEN` set; `POST /telescope/html` with bearer auth and body `{"url": "https://example.com"}` (no `selector`).
2. Observe response `html` starts with `<body` (or body fragment) and lacks the outer `<html>` document wrapper / `<head>`.
3. Same URL with `"selector": "page"` already returns full document HTML today — omitted selector should match that.

Component-level (no live browser): call `capture_html(page, None)` / `capture_html(page, "")` and assert the evaluate script is the documentElement path (same as `"page"`), not the body path.

### Root cause

AST-1725 Stage 3 `capture_html` (and the plan contract table) treated omitted selector as equivalent to `"body"`:

```python
if not sel or sel.lower() == "body":
    return … document.body.outerHTML …
if sel.lower() == "page":
    return … document.documentElement.outerHTML …
```

UAT expects the default (no selector) to be the full page, not the body fragment. The defect is the default branch grouping, not navigation or auth.

### Proposed change

In `service/telescope/capture.py`, change `capture_html` so:

1. `selector` is `None`, `""`, or case-insensitive `"page"` → evaluate `document.documentElement ? document.documentElement.outerHTML : ''`.
2. Case-insensitive `"body"` → keep `document.body ? document.body.outerHTML : ''`.
3. Any other CSS selector → keep first-match `querySelector(…).outerHTML` (unchanged).

Do **not** change `capture_text` defaults (visible text from body remains correct for `/telescope`). Do **not** touch `src/external/telescope.py`, Railway/CI, or Dockerfile.

Update the Stage 3 contract note in this doc's table row for `/telescope/html` `selector` default from `null` (= `body` outerHTML) to `null` (= full document / `documentElement` outerHTML); `"body"` remains an explicit opt-in for body-only.

### Blast radius

- Callers of `POST /telescope/html` with no `selector` (or `null`/`""`) will start receiving a larger payload including `<head>` / doctype-level markup via `documentElement` — intentional UAT fix.
- Callers that already pass `"selector": "body"` or a CSS selector are unchanged.
- `tests/component/service/test_telescope_capture.py::test_capture_html_page_vs_body_vs_selector` covers `"page"` / `"body"` / CSS but does **not** assert the omitted-selector default; Betty may need a repro assertion that `None`/`""` use the documentElement path (fix-board TESTS signal).
- Platform drop-in (`src/external/telescope.py`, AST-1726) if it assumes body-only HTML from the service default — verify during make-fix; out of this bug's file edit unless it hardcodes the old default locally.

### What must still hold

- Parent / AST-1725 AC: `/telescope/html` returns `final_url` + raw rendered HTML (no service-side cull); expand default on; wait_ready default off; bearer auth; console-only logs; zero `src` imports under `service/telescope/`.
- Explicit `"body"` still returns body outerHTML only.
- Explicit CSS selectors still return the first matching element's outerHTML.
- `/telescope` text endpoint and multi-match text behavior unchanged.
- Boundaries: no Railway/CI (#3), no Surfer-shared post-render helpers, no new service endpoints.

## Radia review-fix (AST-1729)

Overall: CLEAN. [bug-repro] OK; What must still hold OK. Clean-review shortcut → User Testing (resolve skipped).

## Bug: AST-1731 — Telescope HTML class selector returns empty string

### As-is

`POST /telescope/html` with a bare class name (e.g. selector `points-container` against https://www.bing.com) returns `"html": ""` even though an element with that class is present in the rendered body.

### To-be

A class selector that matches rendered content returns that element’s outer HTML — and when multiple nodes share the class, an **array** of outer-HTML strings (any tag: `div`, `span`, `td`, …), mirroring multi-match `capture_text` shape (0 → `""`, 1 → `str`, 2+ → `list[str]`).

### Repro

Against a running Telescope node (bearer required), with expand off to keep the call short:

```http
POST /telescope/html
Authorization: Bearer <TELESCOPE_BEARER_TOKEN>
Content-Type: application/json

{"url":"https://www.bing.com","selector":"points-container","expand":false}
```

**As-is:** `200` with `"html":""` (node exists under `document.body` with `class` containing `points-container`).

**To-be:** `200` with `"html"` a non-empty string (single match) or a non-empty `list[str]` (multiple matches) of those elements’ `outerHTML`.

Equivalent via Admin Telescope: response type html, selector `points-container`, URL bing.com — body pane must show the matched markup (not blank).

### Root cause

In `service/telescope/capture.py`, `capture_html` passes the caller’s selector straight into `document.querySelector(selector)`. A bare token like `points-container` is a **tag-name** selector in CSS (`<points-container>`), not a class selector (`.points-container`). Zero tag matches → `''`. Separately, HTML capture uses `querySelector` (first match only) and always returns a single string — Stage 3 of this plan explicitly kept multi-match arrays on the text endpoint only, which this bug’s to-be overturns for HTML class/CSS matches.

### Proposed change

All edits stay inside parent AST-1721 Component/Technical scope (`service/telescope/` capture + route wiring; platform HTML post-process / admin display as needed for the new `html` shape).

1. **`service/telescope/capture.py` — normalize bare class tokens; multi-match HTML**
   - Add a private helper, e.g. `_css_selector_for_query(sel: str) -> str` (or inline the same rules once):
     - If `sel` is a single bare CSS identifier (`^[A-Za-z_][\w-]*$`) **and** `document.querySelectorAll(sel)` returns **zero** nodes, retry the query with `.{sel}` (class). Do **not** rewrite tokens that already look like CSS (leading `.` / `#` / `[`, combinators, spaces, `tag.class`, etc.), and do **not** rewrite when the bare token already matched as a tag (`div`, `span`, …).
     - Prefer one `page.evaluate` that tries the raw selector then the dotted class form when the raw form is a bare identifier with zero hits (avoids a tag-list hardcode and keeps custom elements that exist as tags working).
   - Change `capture_html` return type to `str | list[str]`, parallel to `capture_text`:
     - Keep existing `None` / `""` / `"body"` / `"page"` branches unchanged (AST-1729 owns empty-selector full-document semantics — do not absorb that bug here).
     - Else: `querySelectorAll` (after the bare→class retry above); map each node to `outerHTML`; 0 → `""`; 1 → that string; 2+ → `list[str]`.
   - Apply the **same** bare-identifier → class retry inside `capture_text`’s non-page/body path so text and HTML agree on class-name inputs (same root cause).
   - Still no cull / Surfer helpers in the service.

2. **`service/telescope/app.py` — HTML success log when `html` is a list**
   - In `post_telescope_html`, `html_len=` must not call `len(result.get("html") or "")` on a list (that counts elements, not chars, and `or ""` is wrong). Mirror `/telescope` text: if list, sum of lengths; else `len(str)`.
   - `build_scrape_meta` already accepts `str | list[str]` — no meta.py change required unless a type hint is stale.

3. **`src/external/telescope.py` — platform consumers of `html`**
   - `_post_telescope_html` info log: same list-safe length as (2).
   - `admin_telescope_scrape`: when `cull` and `html` is a `list`, map `_cull_html` over each string; when `html` is a `str`, keep today’s single `_cull_html` call. Do not join list items into one string before cull.
   - `_ensure_html` (drop-in path that feeds parsers expecting one DOM string): if service returns a `list`, unwrap `html[0]` when non-empty else `""` (preserves historical first-match behavior for roster/gazer helpers). Admin continues to receive the raw service payload (full array) via `admin_telescope_scrape`.

4. **`src/ui/frontend/src/pages/AdminTelescope.tsx` — display multi-match HTML**
   - Widen `ScrapeResult.html` to `string | string[]`.
   - In `formatBody`, when `html` is an array, join with the same `\n---\n` separator used for multi-match `text` (so a class that hits N nodes is visible in the pane, not coerced to `""`).

### Blast radius

- **AST-1725 Stage 3 decision** (“HTML endpoint = first match string only”) is superseded for non-`body`/`page` selectors by this bug’s to-be.
- **AST-1729** (empty selector → full document): touches the same `capture_html` special-case branches — keep those branches out of this fix; merge order must not reintroduce body-only default for empty selector if 1729 lands first/second.
- **AST-1726 / AST-1728** admin + platform cull path: list-shaped `html` breaks today’s `len(html)` / `_cull_html(str)` / Admin `typeof html === "string"` assumptions — covered in Proposed change (3)(4).
- Betty tests/bible that assert `html` is always a string for CSS selectors will need qa-fix attention if fix-board flags TESTS: REVISE; do not edit `tests/` here.
- Callers that pass a full CSS class selector already (`.points-container`) get correct matches today for the **first** node; after this fix they also get multi-match arrays when N≥2.

### What must still hold

- Parent AC 3 / AST-1725: `/telescope/html` still returns `final_url` + `html`; bearer required; no service-side cull.
- Parent AC 5: multi-match **text** still `""` / `str` / `list[str]` — unchanged except bare class names now resolve.
- `body` / `page` / empty-selector specials remain explicit branches (empty-selector document vs body owned by AST-1729, not this ticket).
- Zero `src` imports under `service/telescope/`; capture stays browser-only.
- Drop-in helpers that need a single HTML string via `_ensure_html` still get a string (first match when the service returns a list).
- Cookie dismiss / expand / wait_ready defaults and pipeline order unchanged.

## Resolution (AST-1731 resolve-child)

**Date:** 2026-09-20  
**Radia fix-now (review-fix):** AST-1729+1730 regressions on tip `67fd3bf5` — restack onto `origin/ftr/AST-1721-astral-telescope-stateless-headless-scraping`; restore omitted/`page` → `documentElement` and explicit `body` → body-only; keep AST-1731 bare-class retry + multi-match html list on the CSS path only; keep AST-1730 scrollable selectable AdminTelescope textareas.

**Landed:**
- Merged `origin/ftr/AST-1721-astral-telescope-stateless-headless-scraping` into this sub (sync-child `--ftr AST-1721` alone skips the slug-suffixed ftr ref).
- `capture_html`: AST-1729 specials restored; AST-1731 `_QUERY_HTML_JS` / `_fold_blobs` only after those branches.
- `AdminTelescope.tsx`: AST-1730 `RESPONSE_PANE_STYLE` textareas + AST-1731 multi-match `html` formatting both present.

## Radia review-fix (AST-1731)

Overall: FIX-NOW addressed via resolve-child — restacked on ftr, AST-1729 empty-selector restored, AST-1730 UI panes kept, bare-class + multi-match html kept.

## Bug: AST-1732 — Telescope links not scoped to class selector

### As-is

When `POST /telescope` includes a filtering `selector` (e.g. a class CSS selector) and `links` is true (default), the `links` array still contains every `a[href]` on the whole page.

### To-be

When any filtering selector is set, `links` only includes http(s) anchors found **inside** matching element(s). If the selector matches multiple nodes, return the **deduped** union of links found under any match. When no filtering selector is set (`null` / `""` / `"page"` / `"body"`), whole-page link collection stays as today.

### Repro

1. Page with links both inside and outside `.job-list` (e.g. nav + listing cards).
2. `POST /telescope` with `{"url": "…", "selector": ".job-list", "links": true}` (bearer auth).
3. As-is: `links` includes nav / footer URLs outside `.job-list`.
4. To-be: every `links[].href` is an anchor under at least one `.job-list` match; duplicates across multiple matches appear once.

Component (no live browser): `capture_links(page, ".job-list")` must evaluate a scoped script (not bare `document.querySelectorAll('a[href]')`); assert dedupe when two matches share an href.

### Root cause

AST-1725 Stage 3 implemented `capture_links(page)` as whole-document only:

```python
const links = Array.from(document.querySelectorAll('a[href]'));
```

`app.py` `POST /telescope` calls `await capture_links(page)` and never passes `body.selector`. Text capture is selector-aware; links are not — so a class/CSS filter scopes text but not links.

### Proposed change

1. In `service/telescope/capture.py`, change signature to `async def capture_links(page, selector: str | None = None) -> list[dict]`.
2. Normalize `sel = (selector or "").strip()`.
3. **Whole-page path** (unchanged collect shape): when `not sel` or `sel.lower() in ("page", "body")` — keep today’s evaluate that gathers `a[href]` with `href.startswith('http')` → `[{href, text}, …]` from the document.
4. **Scoped path**: otherwise evaluate JS that:
   - `querySelectorAll(sel)` for match roots;
   - under each root, collect `a[href]` with http(s) `href` and trimmed `innerText`;
   - **dedupe by `href`** (first occurrence wins for `text`);
   - return the deduped list.
5. In `service/telescope/app.py` `post_telescope` `work()`, change to `out["links"] = await capture_links(page, body.selector)` when `body.links` is true.

Do **not** change `/telescope/html`, `capture_text`, auth, pool, Dockerfile, or `src/**`.

### Blast radius

- Clients that relied on whole-page links while also passing a text-scoping selector will see a smaller `links` array — intentional UAT fix.
- `links: false` path unchanged (still omits the key / does not call capture).
- `tests/component/service/test_telescope_capture.py::test_capture_links_filters_http` calls `capture_links(page)` with no selector — must keep passing (whole-page path). Betty may need a new assertion for scoped + multi-match dedupe (fix-board TESTS signal).
- App route tests that monkeypatch `capture_links` keep working if the mock accepts an optional second arg.

### What must still hold

- AST-1725 AC: `links` defaults true; when false, omit `links`; http(s) filter; bearer; expand/wait_ready defaults; no service cull; zero `src` imports under `service/telescope/`.
- Multi-match **text** behavior unchanged (string vs list).
- Explicit `"page"` / `"body"` / omitted selector still return whole-page links.
- Boundaries: no Railway/CI, no platform `telescope.py` drop-in edits unless it reimplements service link capture (it must not for this bug).

## Resolution (AST-1732)

**Date:** 2026-09-20  
**Radia fix-now:** Restacked onto `origin/ftr/AST-1721-astral-telescope-stateless-headless-scraping` so AST-1729 `capture_html` (documentElement default) and sibling ftr product are present; kept AST-1732 scoped `capture_links` + `app.py` selector wiring. Full `test_telescope_capture.py` verified green.

## Radia review-fix (AST-1732)

Restacked onto ftr after REVIEW; link-scoping + sibling capture_html/class fixes held. → User Testing.

## Bug: AST-1735 — Telescope head vs body text+links return identical links

### As-is

`POST /telescope` with `links: true` and `selector: "head"`, then the same URL with `selector: "body"`, returns the **same** `links` array (document-wide), even when head and body contain different anchors.

### To-be

Links are scoped to the selected element: `"head"` → http(s) `a[href]` under `<head>` only; `"body"` → under `<body>` only. When the DOM differs by section, the two responses’ `links` arrays differ. Omitted selector / `"page"` still mean whole-document link collection.

### Repro

1. Page with at least one http(s) anchor in `<body>` and a different set in (or absent from) `<head>` (any public site with nav links in body is enough).
2. `POST /telescope` `{"url": "…", "selector": "head", "links": true}` (bearer) → note `links`.
3. Same URL with `"selector": "body"` → note `links`.
4. As-is: the two `links` arrays are equal (full-page set both times, or body alias still document-wide matching a non-scoped head path on the tip under test).
5. To-be: every `links[].href` for `head` is under `<head>`; every href for `body` is under `<body>`; the arrays are not equal when the sections’ anchors differ.

Component (no live browser): `capture_links(page, "head")` and `capture_links(page, "body")` must evaluate scoped scripts (not the document-wide branch); assert the evaluate selector / root differs (`head` vs `body`) and that omit/`"page"` still use the document-wide script.

### Root cause

AST-1732 wired `capture_links(page, selector)` and scoped CSS class selectors, but left this whole-page gate:

```python
if not sel or sel.lower() in ("page", "body"):
    # document.querySelectorAll('a[href]')
```

So explicit `"body"` is still an alias for **document-wide** links (same set as omit / `"page"`). UAT expects `"body"` / `"head"` to mean the HTML elements. Explicit `"head"` already falls through to the scoped `querySelectorAll` path after AST-1732; pairing it with body-as-document still yields a wrong body set and made pre-1732 tips return identical full-page arrays for both selectors. AST-1732’s “What must still hold” line that `"body"` returns whole-page links is **superseded** by this bug.

Platform admin / `src/external/telescope.py` already forward `selector` on `POST /telescope` — no client re-extraction bug.

### Proposed change

1. In `service/telescope/capture.py` `capture_links` only:
   - Whole-document path: when `not sel` **or** `sel.lower() == "page"` (drop `"body"` from this gate).
   - All other selectors — including explicit `"head"` and `"body"` — use the existing scoped evaluate (roots via `querySelectorAll(sel)`, http(s) `a[href]` under each root, dedupe by `href`). No new JS shape required unless make-fix prefers `document.head` / `document.body` specials equivalent to that query.
2. Do **not** change `capture_text` (body/page visible-text chrome strip stays), `capture_html`, `app.py` (already passes `body.selector`), auth, pool, Dockerfile, or `src/**`.
3. Do not re-assert AST-1732’s “body = whole-page links” invariant; update any comment in `capture_links` that still says omit/page/body share the document path.

### Blast radius

- Callers that passed `"selector": "body"` expecting **document-wide** links (including anchors under `<head>`) will get body-only links — intentional UAT correction; use omit or `"page"` for whole-document.
- `"head"` already scoped after AST-1732; behavior stays element-scoped; new coverage should lock head≠body when fixtures differ.
- `links: false` and class/CSS scoping from AST-1732 unchanged.
- Betty may need a head-vs-body (and body≠page) assertion on `capture_links` (fix-board TESTS signal). Do not edit `tests/` here.

### What must still hold

- AST-1725 AC: `links` defaults true; when false, omit `links`; http(s) filter; bearer; expand/wait_ready defaults; no service cull; zero `src` imports under `service/telescope/`.
- AST-1732: non-`page` CSS/class selectors still scope links; multi-match union + href dedupe.
- Omitted selector and explicit `"page"` still return **whole-document** links.
- Explicit `"body"` scopes to `<body>` (this ticket); explicit `"head"` scopes to `<head>`.
- Multi-match **text** behavior and HTML specials (AST-1729/1731) unchanged.
- Boundaries: no Railway/CI; no platform `telescope.py` / admin proxy edits for this bug.

## Resolution (AST-1735)

**Date:** 2026-09-21  
**Radia fix-now:** Restacked onto `origin/ftr/AST-1721-astral-telescope-stateless-headless-scraping` (AST-1733 style/script strip + sibling tips). Kept AST-1735 `capture_links`: omit/`page` = document-wide; explicit `head`/`body` = element-scoped. Full `test_telescope_capture.py` green (incl. AST-1733 repro).

## Radia review-fix (AST-1735)

Overall: FIX-NOW — restack onto current ftr (include AST-1733 text strip); keep capture_links head/body scoping. Then User Testing.

## Bug: AST-1736 — Telescope HTML class filter (shaders) returns empty string

### As-is

Putting a bare class token like `shaders` in the Admin / request filter (`selector`) is not treated as a class name: the HTML scrape returns an empty string (same class-vs-tag confusion Susan hit on AST-1731 with `points-container`).

### To-be

Class-name filters match elements that have that class and return their HTML when nodes exist — **or** the request surface exposes an explicit tag vs class split so “I mean a class” does not depend on CSS-selector heuristics.

### Repro

Component fixture (no live URL required — ticket names the token `shaders`, not a host):

1. DOM with no `<shaders>` element and at least one node `class="shaders"` (any tag).
2. `POST /telescope/html` with `{"url":"…","selector":"shaders","expand":false}` (bearer) **or** Admin Telescope html + selector `shaders`.
3. **As-is (pre-explicit-class / incomplete paths):** `"html":""` when the caller’s intent is class, not tag — and/or bare `shaders` fails to scope links on `POST /telescope` even when html/text would match after AST-1731.
4. **To-be:** non-empty `html` for matching nodes; with explicit params, `class_name: "shaders"` (optional `tag`) matches without relying on bare-`selector` retry.

### Root cause

AST-1731 already landed a silent bare-CSS-ident → `.{ident}` retry inside `capture_html` / `capture_text` (`service/telescope/capture.py` `_BARE_CLASS_RETRY`). On this tip that path treats `shaders` the same as `points-container` for html/text. Two gaps remain vs this bug’s to-be:

1. **Intent is still only a CSS `selector`.** A bare token is always “query as tag, then maybe as class.” There is no first-class “this is a class name” (and optional element tag) field — the design Susan asked for on the ticket.
2. **`capture_links` never received the bare→class retry** (AST-1732 scoped roots with raw `querySelectorAll(selector)` only). Bare class filters are inconsistent across html/text vs links on the same request.

So this is not “re-do AST-1731’s heuristic for another token”; it is the missing **tag / class parameter split** (plus shared selector resolution so links agree).

### Proposed change

All edits stay inside parent AST-1721 Component/Technical scope (`service/telescope/` contract + capture; platform admin client pass-through; Admin Telescope UI). Do **not** re-open AST-1729 `page`/`body` branches or remove AST-1731 bare-retry on `selector` (back-compat).

1. **`service/telescope/capture.py` — resolve class/tag → CSS; share across capture paths**
   - Add a pure helper, e.g. `resolve_capture_query(*, selector: str | None, tag: str | None, class_name: str | None) -> str | None`:
     - Strip all three inputs.
     - If `selector` is non-empty **and** (`tag` or `class_name` non-empty) → raise a small domain error the route maps to **HTTP 400** (ambiguous filter).
     - If `class_name` set: must match `^[A-Za-z_][\w-]*$` else 400; build CSS `.{class_name}` or `{tag}.{class_name}` when `tag` is also set (`tag` must match `^[A-Za-z][\w-]*$`). **Do not** run tag-first then class-retry for this path — class intent is explicit.
     - If only `tag` set: return that tag name as the CSS selector.
     - If only `selector` set: return it unchanged (existing `page`/`body`/empty handling stays in each `capture_*`).
     - If none set: return `None` / `""` so today’s whole-document branches run.
   - Route `capture_html` / `capture_text` / `capture_links` through that resolved CSS string (app calls the helper once per request and passes the result as today’s `selector` arg, **or** capture accepts the optional kwargs and resolves internally — one place only).
   - Apply **`_BARE_CLASS_RETRY` to `capture_links`’ scoped path** the same way html/text do, so bare `selector: "shaders"` scopes link roots after zero tag hits (closes the AST-1732 omission without requiring callers to learn `class_name` immediately).

2. **`service/telescope/app.py` — request fields**
   - On `TelescopeRequest` and `TelescopeHtmlRequest`, add optional `tag: str | None = None` and `class_name: str | None = None` (JSON name `class_name`, not `class`).
   - Before capture: resolve via the helper; on validation/ambiguity error → `400` with a clear `detail`.
   - Pass the resolved selector into `capture_text` / `capture_links` / `capture_html` as today.
   - Log which filter mode was used at info/debug (selector vs tag/class) without dumping page HTML.

3. **`src/external/telescope.py` + `src/ui/api/api_admin.py` — pass-through**
   - `_post_telescope`, `_post_telescope_html`, and `admin_telescope_scrape` accept optional `tag` / `class_name` and include them in the JSON body when set (same rules as service).
   - Admin proxy reads `tag` / `class_name` from the request body and forwards them.

4. **`src/ui/frontend/src/pages/AdminTelescope.tsx` — explicit filters**
   - Add optional **Tag** and **Class name** inputs beside the existing Selector field.
   - Submit rules: if Class name and/or Tag is filled, send `tag` / `class_name` and **omit** `selector` (and disable or clear Selector in the UI to match the 400 rule). If only Selector is filled, keep today’s `selector` body field (AST-1731 bare-retry still applies).
   - Placeholder/help: Selector = full CSS / `page` / `body`; Class name = class token without a leading dot.

### Blast radius

- AST-1731 bare-retry on `selector` remains for callers that already send bare tokens; new Admin path should prefer `class_name` so UAT does not depend on the heuristic.
- AST-1732 scoped links: bare class tokens start scoping roots once `_BARE_CLASS_RETRY` is shared — link arrays may shrink vs today’s empty-root → empty list when `<shaders>` tags are absent (correct).
- Contract JSON grows two optional keys; omit-when-unset keeps old clients working.
- Betty / qa-fix may need asserts for `class_name: "shaders"` → non-empty html and for ambiguous `selector`+`class_name` → 400; do not edit `tests/` here.

### What must still hold

- Parent AC 3: `/telescope` + `/telescope/html` still return `final_url` + text|html|links; bearer required; no service-side cull.
- AST-1731: bare `selector` class retry + multi-match html `""` / `str` / `list[str]` unchanged when only `selector` is used.
- AST-1729: empty / `page` / `body` specials unchanged.
- AST-1732: when a filter matches, links stay scoped under match roots (dedupe by href).
- Zero `src` imports under `service/telescope/`; capture stays browser-only.
- Drop-in `_ensure_html` first-match unwrap for list html unchanged.

## Radia review-fix (AST-1736)

Overall: CLEAN. PROCEED — tag/class_name filter fix. Resolve skipped.

## Bug: AST-1737 — Telescope expand vs multi-page pagination

### As-is

`expand` (default on) runs `expand_page` in `service/telescope/interact.py`: infinite-scroll height growth (capped) then clicks `Load More` / `Show More` on the **same URL**. It does **not** follow numbered pagination, “Next” page controls, or `?page=N` URL changes. A listing split across 15 discrete result screens therefore yields only the first screen’s DOM/text after expand. OpenAPI / admin toggle label only say `expand` with no semantics, so UAT cannot tell load-more from multi-page. Pre-migration `playwright.load_all_jobs` was the same scroll + Load More loop — numbered multi-page was never part of that helper.

### To-be

Contract documents that **expand = load-more / infinite-scroll on the current URL only**. Discrete paginated screens (page 2…N / Next) stay out of expand; callers must request each page URL separately (platform already fans out multi-URL scrapes). No new numbered-pagination browser loop in this bug — that would be a new product capability beyond parent FS §3 / API contract (`expand` = load-all scroll + Load More).

### Repro

1. Admin Telescope (or `POST /telescope` with bearer): any URL whose results use **numbered pages** or Next (not a Load More button), `expand=true`, no selector.
2. Observe: response covers only the first page’s listings, not all N pages × page size.
3. Contrast: a URL that appends rows via infinite scroll / “Load More” — expand keeps scrolling/clicking until height/button stall (existing caps: 10 scrolls / 20 clicks, unchanged by this bug).

### Root cause

Ambiguous naming, not a migration regression. Parent and AST-1725 Stage 3 already defined expand as the port of `load_all_jobs` (scroll + Load More). Multi-page **URL** fan-out lives on the platform (`roster` page maps), not inside one Telescope request. UAT treated “pagination” as expand’s job; the shipped flag never meant that.

### Proposed change

Document-only — **do not** extend `expand_page` to click Next / page numbers.

1. **`service/telescope/app.py`** — On `TelescopeRequest.expand` and `TelescopeHtmlRequest.expand`, use `pydantic.Field(default=True, description=...)` with description text that states expand runs infinite-scroll + Load More/Show More on the current document and does **not** navigate numbered pagination or Next-page URLs. Keep default `True`.
2. **`service/telescope/interact.py`** — Replace/extend the `expand_page` docstring to the same contract (scroll then Load More/Show More; no Next / page-index navigation; soft-fail loop unchanged). No logic change to the scroll/click loops or their existing caps.
3. **`src/ui/frontend/src/pages/AdminTelescope.tsx`** — On the expand checkbox label (or adjacent hint), surface the same wording so UAT sees e.g. `expand (scroll / Load More — not numbered pages)`. Do not add a separate pagination toggle.

Out of this bug: implementing Next/page-N capture; changing scroll/click caps; platform roster multi-URL fan-out; `src/external/telescope.py` flag plumbing beyond what already passes `expand` through.

### Blast radius

- Admin + OpenAPI readers see clearer expand semantics; request/response JSON shape unchanged.
- Call sites that assumed expand fetched every numbered page keep seeing first-page-only — that was always true; documentation makes it intentional.
- Sibling bugs touching `capture_*` / selectors are orthogonal.
- Betty: no behavior flip expected; optional assertion that Field description / admin copy exists is board’s call (TESTS), not a product change.

### What must still hold

- Parent FS §3 / Technical scope: expand default **on** = load-all scroll / Load More; cookie dismiss always; wait_ready default off; per-URL single navigation + capture.
- AST-1725 AC: `expand_page` port of `load_all_jobs` behavior; bearer; no service cull; zero `src` imports under `service/telescope/`.
- Platform drop-in still maps `load_all_jobs` → `page.expand = True` (AST-1726) without inventing a second pagination flag.
- Parent non-goal: no depth/output limits **added** without Susan sign-off — this bug does not tighten or raise the existing scroll/click caps.

## Radia review-fix (AST-1737)

Overall: CLEAN. Expand contract documented. Clean-review shortcut → User Testing.

## Bug: AST-1746 — Telescope add optional id filter parameter

UAT-batch fix against amended AST-1721 Component/Technical scope (optional `id` secondary filter + admin control, alongside tag/selector/class). Lives on this plan doc because AST-1736’s tag/`class_name` contract + capture resolver are the sibling surface. Does not rewrite Stages 1–4 or other bug blocks.

### As-is

Telescope requests and Admin Telescope expose optional `tag` / `class_name` (and CSS `selector`) but have no optional `id` parameter to filter elements by `id="<idstring>"`.

### To-be

An optional `id` request field (same role as `class_name`) resolves to a CSS id selector so capture matches `id="<idstring>"`; Admin Telescope exposes an Id control and forwards it; platform admin proxy / `_post_telescope*` pass it through.

### Repro

1. DOM with at least one node whose attribute is `id="hero"` (any tag), and no reliance on a bare CSS `selector` of `#hero`.
2. `POST /telescope/html` with bearer and body `{"url":"…","id":"hero","expand":false}` — **as-is:** `id` is ignored (Pydantic drops unknown fields or field absent) → whole-document / default HTML, not the `#hero` node.
3. Admin Telescope: Tag / Class name / Selector present; **no** Id input — operator cannot express id intent without typing `#hero` into Selector.
4. **To-be:** `id: "hero"` (optional `tag`) returns that node’s html/text/links scope; Admin Id field sends `id` and omits `selector` when secondary filters are active.

### Root cause

AST-1736 added explicit `tag` / `class_name` → CSS in `resolve_capture_query` and wired them through service models, platform client, admin proxy, and AdminTelescope UI. The parallel **id** secondary filter was never added — only class got a first-class field. Parent scope has since been amended to include it; product still lacks the field and control.

### Proposed change

All edits stay inside parent AST-1721 Component/Technical scope (`service/telescope/` capture + request models; `src/external/telescope.py` / `src/ui/api/` pass-through; `src/ui/frontend/` Admin Telescope). Do **not** remove AST-1736 tag/`class_name` behavior, AST-1731 bare-class retry on `selector`, or AST-1729 `page`/`body` branches.

1. **`service/telescope/capture.py` — extend `resolve_capture_query`**
   - Add optional kwarg `id: str | None = None` (strip like the others). Reuse `_CLASS_NAME_RE` (same `^[A-Za-z_][\w-]*$`) for the id token, or an identically shaped `_ID_RE` alias — invalid → `CaptureQueryError("invalid id")`.
   - Ambiguity: if `selector` is non-empty **and** any of `tag` / `class_name` / `id` is non-empty → `CaptureQueryError` (message names all three secondary fields).
   - When `id` is set (alone or with tag/class), build CSS **without** attribute-selector fallback and **without** a bare→`#id` retry on the `selector` path:
     - `id` only → `#{id}`
     - `tag` + `id` → `{tag}#{id}`
     - `class_name` + `id` → `.{class_name}#{id}`
     - `tag` + `class_name` + `id` → `{tag}.{class_name}#{id}`
   - When `id` is unset, keep today’s tag/`class_name` / selector-only branches unchanged.
   - `capture_html` / `capture_text` / `capture_links` stay selector-string consumers; app still resolves once per request.

2. **`service/telescope/app.py` — request field + resolve wiring**
   - On `TelescopeRequest` and `TelescopeHtmlRequest`, add optional `id: str | None = None`.
   - `_resolve_body_selector` passes `id=body.id` into `resolve_capture_query`; log mode when `id` (and/or tag/class) is set, e.g. `telescope filter mode=tag/class/id … resolved=…`, without dumping page HTML.
   - Invalid/ambiguous → existing HTTP 400 `detail` path.

3. **`src/external/telescope.py` + `src/ui/api/api_admin.py` — pass-through**
   - `_post_telescope`, `_post_telescope_html`, and `admin_telescope_scrape` accept optional `id` and include `"id"` in the JSON body when set (same omit-when-unset pattern as `class_name`).
   - Admin proxy reads `id` from the request body (strip empty → `None`) and forwards it.

4. **`src/ui/frontend/src/pages/AdminTelescope.tsx` — Id control**
   - Add optional **Id** text input beside Tag / Class name (placeholder e.g. `hero` — no leading `#`).
   - Treat Id as part of the secondary-filter group with Tag/Class: if any of tag / class_name / id is filled, send those fields and **omit** `selector` (disable Selector when the group is active; disable the group when Selector is filled) — same mutual exclusion as AST-1736, now including `id`.
   - Help copy: Id = HTML `id` token without a leading `#`.

**Out of this bug:** inventing bare-`selector` → `#ident` retry; changing multi-match fold rules; service cull; expand/pagination; unrelated admin scroll bugs.

### Blast radius

- Contract JSON gains one optional key (`id`); omit-when-unset keeps existing clients working.
- Admin operators who previously typed `#foo` into Selector keep that path; new Id field is the preferred explicit path (mirrors Class name vs bare class token).
- Combining `id` with `class_name` / `tag` can narrow matches vs class-only (correct).
- Betty / qa-fix may assert `id: "…"` → scoped html/text/links and `selector`+`id` → 400; do not edit `tests/` here.

### What must still hold

- Parent AC 3 / AC 14: endpoints and admin still return `final_url` + text|html|links (+ scrape_meta on admin); bearer required; no service-side cull.
- AST-1736: `tag` / `class_name` resolution and Admin Tag/Class controls unchanged when `id` is omitted.
- AST-1731: bare `selector` class retry + multi-match html `""` / `str` / `list[str]` unchanged when only `selector` is used.
- AST-1729: empty / `page` / `body` specials unchanged.
- AST-1732: when a filter matches, links stay scoped under match roots (dedupe by href).
- Zero `src` imports under `service/telescope/`; capture stays browser-only.
- Drop-in `_ensure_html` first-match unwrap for list html unchanged.
