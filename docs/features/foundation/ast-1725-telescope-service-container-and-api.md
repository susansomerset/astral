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
