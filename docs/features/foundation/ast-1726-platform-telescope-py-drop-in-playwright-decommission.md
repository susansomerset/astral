# Platform telescope.py drop-in and playwright decommission

**Linear:** [AST-1726](https://linear.app/astralcareermatch/issue/AST-1726)
**Parent:** [AST-1721](https://linear.app/astralcareermatch/issue/AST-1721) — Astral Telescope — stateless headless-scraping microservice (per-URL)
**Publish ref:** `sub/AST-1721/AST-1726-platform-telescope-py-drop-in-playwright-decommission`

Replace in-process Firefox scraping with an HTTP client to the Telescope service ([AST-1725](https://linear.app/astralcareermatch/issue/AST-1725)): add `src/external/telescope.py` as a **full drop-in** of today's `playwright.py` public surface (same names/params; core changes **import module path only**), keep all post-render helpers in that same file (Surfer-ready), delete `src/external/playwright.py`, wire Telescope pool/auth/timeout/concurrency in config, pin `httpx` and remove platform Firefox install from requirements + build/dev/start scripts. Does not own Telescope service deploy or CI import fence ([AST-1727](https://linear.app/astralcareermatch/issue/AST-1727)). Does not build Surfer.

## Explicit scope gate

Ticket **## Scope** names exactly:

- `src/external/telescope.py` — **new** — full drop-in; HTTP for headless scrape; all former non-browser / post-render helpers in this file; no in-process Firefox
- `src/external/playwright.py` — **deleted**
- `src/core/roster.py` / `gazer.py` / `meteorite.py` — **modified** — import path `playwright` → `telescope` only; no call-site shape changes
- `src/utils/config.py` — **modified** — Telescope base URL(s), env bearer, client timeout, in-flight pool / per-node caps, Telescope-facing defaults; drop `RAILWAY_CONFIG["playwright_browsers_path"]`
- `requirements.txt` — **modified** — pin `httpx`; drop platform `playwright`
- `scripts/build_railway.sh` — **modified** — remove Firefox install / `PLAYWRIGHT_BROWSERS_PATH`
- `scripts/setup_dev.sh` — **modified** — remove `playwright install firefox`
- `scripts/start_server.py` — **modified** — remove browsers-path env seed

Every **Files Changed** row is one of those paths. No `service/**`, no Railway Telescope deploy, no CI import fence, no Surfer, no `tests/` / bible, no `page_parse.py`, no call-site logic rewrites in core beyond the import module string.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `TELESCOPE_CONFIG`; trim `PLAYWRIGHT_CONFIG` / drop `RAILWAY_CONFIG["playwright_browsers_path"]` | utils |
| `src/external/telescope.py` | **New** — full drop-in port of `playwright.py` + HTTP pool client | external |
| `src/external/playwright.py` | **Delete** | external |
| `src/core/roster.py` | `from src.external.telescope import (...)` — same symbol list | core |
| `src/core/gazer.py` | Same import-path-only rewire | core |
| `src/core/meteorite.py` | Same import-path-only rewire | core |
| `requirements.txt` | Add `httpx`; remove `playwright` | deps |
| `scripts/build_railway.sh` | Remove Firefox install + browsers path | scripts |
| `scripts/setup_dev.sh` | Remove `playwright install firefox` | scripts |
| `scripts/start_server.py` | Remove `PLAYWRIGHT_BROWSERS_PATH` seed | scripts |

**Out of this ticket:** `service/telescope/**` (AST-1725); `service/telescope/railway.toml` / CI import fence (AST-1727); Surfer; `scripts/` spikes that still import `playwright` (leave broken or for a later cleanup — not in Scope); `tests/` / `docs/test-bible/**` (Betty).

## Canon notes (planner)

- **Patterns (full):** `patt.entity.batch-processing`, `patt.entity.batch-criteria` — this ticket does **not** invent claim/clear or criteria literals. Batch scrape concurrency stays caller-owned (`roster`/`gazer` semaphores + `PLAYWRIGHT_CONFIG["company_scrape_timeout_seconds"]` / meteorite `playwright_concurrency` keys unchanged at call sites). Platform `TELESCOPE_CONFIG` only adds the **HTTP in-flight** backpressure knob so the facade does not open unbounded sockets to the pool. Corpus sha at plan: `751624d7ebdf9bc441fc3d08a51ae751ea8026af`.
- **Logging statutes** (`stat.logging.error` / `.warning` / `.info` / `.debug`): **id-only** at plan; expand at build. Use `src.utils.logging.get_logger` (platform has DB).
- **Pending:** `patt.external.web-scraping-via-telescope` — flagged pending Archie; **not** scoring law this pass. Id-only.

## Stage 1: Config + deps + Firefox uninstall scripts

**Done when:** `TELESCOPE_CONFIG` is importable from `config.py` with the keys below; root `requirements.txt` lists `httpx` and does not list `playwright`; the three scripts no longer install or seed Firefox browsers; `RAILWAY_CONFIG` has no `playwright_browsers_path`. No `telescope.py` yet.

1. In `src/utils/config.py`, immediately **after** the existing `PLAYWRIGHT_CONFIG` block (~line 4703), add:

```python
# TELESCOPE_CONFIG: platform HTTP client to Astral Telescope (AST-1726).
# Bearer is env-only (never a code default secret).
TELESCOPE_CONFIG = {
    "base_urls": [],  # filled from TELESCOPE_BASE_URLS (comma-separated) or TELESCOPE_BASE_URL
    "bearer_env": "TELESCOPE_BEARER_TOKEN",
    "client_timeout_seconds": 60,
    "max_in_flight": 15,           # platform-wide concurrent HTTP scrapes
    "per_node_max_in_flight": 3,   # soft cap tracking per base_url
    "retry_other_node": True,
    "max_node_attempts": 2,        # try primary + one other node on timeout/5xx
    "healthz_path": "/healthz",
    "telescope_path": "/telescope",
    "telescope_html_path": "/telescope/html",
    "cull_html_default": True,     # platform drop-in applies _cull_html after /telescope/html
    "default_expand": True,
    "default_wait_ready": False,
}
```

2. At module load (same area as other env-derived config), populate `TELESCOPE_CONFIG["base_urls"]` from env:
   - Prefer `TELESCOPE_BASE_URLS` (comma-separated, strip whitespace, drop empties).
   - Else if `TELESCOPE_BASE_URL` set → single-element list.
   - Else leave `[]` (client fails closed at first scrape with a clear error — do not invent `localhost` as a silent default).

3. Keep `PLAYWRIGHT_CONFIG` keys that **callers already read** without import changes: at minimum `company_scrape_timeout_seconds`, and any other keys still referenced from `roster.py` / `gazer.py` / `meteorite` config dicts. Remove **only** keys that become dead after Firefox leave **if** nothing outside `playwright.py` reads them after this ticket's import rewires. Safe to remove from `PLAYWRIGHT_CONFIG` when unused by core: `launch_timeout_ms`, `launch_max_attempts`, `launch_retry_delay_seconds`, `firefox_user_prefs` — **verify with ripgrep** before deleting; if any non-playwright module still imports them, leave the key.

4. In `RAILWAY_CONFIG`, **delete** the `"playwright_browsers_path"` entry entirely.

5. In `requirements.txt`:
   - Under `# Web scraping & automation`, **remove** the `playwright>=1.40.0` line.
   - **Add** `httpx>=0.27.0,<1` (direct pin; anthropic already pulls httpx transitively — still declare it for the Telescope client).
   - Keep `beautifulsoup4` (needed by `_cull_html` / HTML helpers).

6. In `scripts/build_railway.sh`, delete the two Firefox lines:

```bash
export PLAYWRIGHT_BROWSERS_PATH="$PWD/.browsers"
playwright install --with-deps firefox
```

Leave `pip install -r requirements.txt` and the frontend build as-is.

7. In `scripts/setup_dev.sh`, delete the line `"$VENV/bin/python" -m playwright install firefox` (and any comment that only exists for that install).

8. In `scripts/start_server.py`, delete the block that reads `RAILWAY_CONFIG["playwright_browsers_path"]` and sets `os.environ["PLAYWRIGHT_BROWSERS_PATH"]`.

⚠️ **Decision:** Env var names match the service (`TELESCOPE_BEARER_TOKEN`, base URL(s)). Local multi-process: platform points at `http://127.0.0.1:<TELESCOPE_PORT>` via `TELESCOPE_BASE_URL` — never import `service.telescope`.

**Stage 1 commit message:** `code(AST-1726): telescope config httpx drop firefox scripts`

## Stage 2: `telescope.py` HTTP pool + handle types (no full port yet)

**Done when:** `src/external/telescope.py` exists with HTTP pool helpers, `BrowserSession` / `PageHandle` / `BatchBrowserSession` client-side types (no `playwright` import), and `PlaywrightInfraError` / classify helpers under the **same public names**. Core still imports `playwright` until Stage 4. Module may not yet re-export every scrape helper.

1. Create `src/external/telescope.py`. Module docstring: platform Telescope client + Surfer-ready post-render helpers; **no** in-process browser.

2. Imports allowed: `asyncio`, `hmac`/`hashlib` as needed, `httpx`, stdlib HTML/`bs4`, `src.utils.config` (`ASTRAL_CONFIG`, `PLAYWRIGHT_CONFIG`, `TELESCOPE_CONFIG`), `src.utils.integration_io.require_controlled_external_io`, `src.utils.logging.get_logger`. **Forbidden:** `playwright`, `service.*`, any `src`→`service` import.

3. Copy these symbols **verbatim in name and behavior intent** from `playwright.py` (adjust only what must change for HTTP later):

   - `PLAYWRIGHT_INFRA_FAILURE_CLASSES`, `classify_playwright_failure`, `is_playwright_infra_failure`, `PlaywrightInfraError` — extend `classify_playwright_failure` to map httpx timeouts / connect errors / 5xx to stable classes (`connectivity_failure`, existing timeout-ish classes, or add `"telescope_timeout"` / `"telescope_http_error"` **and** include them in `PLAYWRIGHT_INFRA_FAILURE_CLASSES` so roster infra routing still treats them as infra). Prefer reusing existing class strings when the message matches; for HTTP 504/timeout use a class that `is_playwright_infra_failure` returns True for.

4. Replace Playwright type aliases with client handles:

```python
class BrowserSession:
    """Client-side session handle (no Firefox). Drop-in for former BrowserContext."""
    ...

class PageHandle:
    """Bound URL + scrape flags + optional cached artifacts. Drop-in for former Page."""
    url: str
    expand: bool
    wait_ready: bool
    _html: Optional[str]
    _text: Optional[Any]  # str | list[str]
    _links: Optional[list]
    _final_url: Optional[str]
    _closed: bool
    async def close(self) -> None: ...
```

5. Implement `_TelescopePool` (module-private) with:
   - Round-robin index + per-URL in-flight counters.
   - Platform `asyncio.Semaphore(TELESCOPE_CONFIG["max_in_flight"])`.
   - `async def request(method, path, *, json_body=None) -> httpx.Response`:
     1. `require_controlled_external_io("telescope.request")`
     2. If `base_urls` empty → raise `PlaywrightInfraError("connectivity_failure", "TELESCOPE_BASE_URL(S) not configured")`
     3. Pick next URL (round-robin); on failure/timeout with `retry_other_node` and ≥2 bases, retry another base up to `max_node_attempts`
     4. Headers: `Authorization: Bearer <os.environ[TELESCOPE_CONFIG["bearer_env"]]>` — missing token → `PlaywrightInfraError("connectivity_failure", "TELESCOPE_BEARER_TOKEN not set")`
     5. `httpx.AsyncClient(timeout=TELESCOPE_CONFIG["client_timeout_seconds"])` — prefer one shared client created lazily, closed on process shutdown not required for v1
     6. On httpx timeout / connect error: warning log once with base_url + path; raise `PlaywrightInfraError` with infra class
     7. On HTTP 401/403: error log; raise infra error
     8. On HTTP 504/502/5xx: warning; retry other node if configured; else raise

6. Implement:
   - `async def _post_telescope(url, *, selector=None, expand=None, wait_ready=None, links=True) -> dict` → `POST {base}{telescope_path}` body matching AST-1725 contract.
   - `async def _post_telescope_html(url, *, selector=None, expand=None, wait_ready=None) -> dict` → `POST .../telescope/html`.
   - `async def _get_healthz() -> bool` → `GET .../healthz` with bearer; True iff 200 and body status ok.

7. Implement session factories with **identical signatures** to today:

   - `create_browser_context(headless: bool = True, viewport: Optional[Dict] = None)` — async contextmanager yielding `BrowserSession` (ignore headless/viewport for HTTP; accept params for drop-in).
   - `BatchBrowserSession` — no Firefox; `ensure_context` returns self or an inner `BrowserSession`; `recover(failure_class, reason)` logs warning (no browser relaunch); `aclose` clears state.
   - `create_batch_browser_session(headless=True, viewport=None)` — same CM shape as today.
   - `get_page(context=None, url=None, *, batch_session=None) -> PageHandle` — requires context or batch_session; creates `PageHandle` with `url` set; **does not** call Telescope yet (lazy fetch on first extract). If `url` empty, return blank handle (mirrors today's allow empty).
   - `new_page(session) -> PageHandle` — blank handle bound to session.
   - `close_page(page)` → `await page.close()`.
   - `get_page_url(page) -> str` → `page.url` or `page._final_url or page.url`.
   - `check_connectivity(timeout=None) -> bool` → `_get_healthz()` (ignore local Firefox). Soft-fail False + warning on error (same return contract as today).

⚠️ **Decision:** Lazy fetch on extract (not on `get_page`) so `load_all_jobs` / `wait_for_careers_list_readiness` can flip `expand` / `wait_ready` on the handle **before** the single Telescope round-trip. That preserves the gazer/roster sequence without double-loading when callers set flags then extract.

⚠️ **Decision:** Keep public names `PlaywrightInfraError` / `classify_playwright_failure` / `PLAYWRIGHT_*` — drop-in law is **same public names**, not rename-for-taste.

**Stage 2 commit message:** `code(AST-1726): telescope http pool and handles`

## Stage 3: Port all public helpers — scrape via HTTP, post-render local

**Done when:** Every public symbol core (and the former `playwright.py` public surface) exists on `telescope.py` with the **same names and parameter lists**; scrape-backed paths use Telescope HTTP; `_cull_html` and HTML/text post-processors run **locally** in this file; `import playwright` / `from playwright` appear **nowhere** in `telescope.py`.

### Port method

1. Copy the remainder of `src/external/playwright.py` into `telescope.py` (post-render helpers, TypedDicts, vendor/clickables, `extract_raw_job_listings`, `normalize_url`, `_cull_html`, parsers, etc.).
2. **Delete** all in-process browser machinery: `_launch_browser`, `_create_page_context`, `_log_browser_env`, cookie dismiss that drives a live page, `page.goto` / `page.evaluate` / `page.locator` / `async_playwright` usages.
3. Rewrite scrape-backed functions as specified below. Pure HTML/string helpers stay logic-equivalent (BeautifulSoup / HTMLParser).

### Scrape-backed mapping (binding)

| Symbol | Behavior in `telescope.py` |
|--------|----------------------------|
| `get_visible_text(url=..., context=, page=, return_final_url=)` | If `page` with cached text → use it. Else resolve URL from `page.url` or `url`; `POST /telescope` with `links=False`, `expand=page.expand if page else TELESCOPE_CONFIG["default_expand"]`, `wait_ready=...`; return text or `(text, final_url)`. On failure: same raise/retry spirit as today (2 attempts over pool nodes already in `_TelescopePool`). |
| `extract_visible_text(page)` | Ensure page artifacts via `_ensure_text(page)`; return `{"text", "url"}` shape callers expect. |
| `extract_page_scrape_contract(page)` | Text + nav link hrefs from `/telescope` with `links=True`; shape matches today's keys (`visible_text` / `nav_urls` / `final_url` — **read current return dict keys in `playwright.py` and preserve them exactly**). |
| `extract_page_dom(page, element=None)` | `_ensure_html(page, selector=element)`; then if `TELESCOPE_CONFIG["cull_html_default"]`: return `_cull_html(raw)` else raw. **Cull defaults on in the platform drop-in** (parent AC 4). |
| `get_page_dom(url=..., element=, context=, page=)` | Same lifecycle as today but using handles + HTTP. |
| `load_all_jobs(page, short_name)` | Set `page.expand = True`; invalidate cached artifacts; log debug with short_name. **Do not** scroll locally. |
| `wait_for_careers_list_readiness(page, cfg)` | Set `page.wait_ready = True`; if `cfg.get("run_load_all_jobs", True)`: `page.expand = True`; invalidate cache; optionally one `_ensure_text(page)` so readiness reflects service `wait_ready`; return a meta dict with the **same keys** as today (`outcome`, `wait_ms`, `visible_chars`, `listing_hits`, `load_all_jobs_ran`, …). Set `listing_hits=0` (service has no listing selectors — parent design). Do not call `page.locator`. |
| `extract_site_page_list(...)` | Single-page: links from `/telescope` `links=True`. Recursive `max_depth`: additional HTTP navigations per discovered same-domain URL (preserve today's filter/verify behavior using HTTP GET-via-telescope, not Firefox). Honor existing `max_depth` / `verify` / `debug` params — do not invent new caps. |
| `get_page_with_artifacts` / `extract_page_clickables` / `extract_page_content` / `extract_with_javascript` | Prefer HTML-first paths: fetch html via `/telescope/html`, then existing `_parse_html_for_internal_clickables` / JS-equivalent **on HTML string** where possible. If a helper truly cannot work without live `page.evaluate`, implement evaluate against **cached HTML is impossible** — then: fetch html, and for clickables use the HTML parser path only; `request_urls` / `frame_urls` stay empty lists (parent: vendor artifacts not required from service). |
| `navigate_and_wait_for_ready` / `wait_for_page_ready_after_navigation` / `wait_for_timeout` / `evaluate` / `get_link_urls_from_page` / `get_frame_urls` | Keep signatures. `wait_for_timeout` → `asyncio.sleep(ms/1000)`. `evaluate` → raise `PlaywrightInfraError("unknown", "evaluate unsupported on Telescope client")` **unless** you can satisfy the call from cached artifacts without a browser. Core does not call `evaluate` today — fail loud for scripts. `get_frame_urls` → `[]`. `get_link_urls_from_page` → from cached links or `_ensure_text` with links. |
| `detect_vendor` / `recommend_routing` / `normalize_url` / `extract_tags_in_order` / `extract_raw_job_listings` / `_cull_html` / `_parse_html_for_internal_clickables` | Stay local; no HTTP. |

4. Internal helpers `_ensure_html(page, selector=None)` / `_ensure_text(page, links=False)`:
   - If cache valid for requested mode, return.
   - Else POST appropriate endpoint with `page.url`, `page.expand`, `page.wait_ready`, selector; store `_html` / `_text` / `_links` / `_final_url` (`final_url` also updates `page.url` when present).
   - Closed page → raise clear error.

5. Logging: info one-liner per successful HTTP scrape (`telescope ok path=... final_url=...`); warning on retry/failover; `logger.exception` once on unexpected errors (statutes expanded at build).

6. Confirm **no** `from playwright` / `import playwright` in this file. Confirm **no** second module (`page_parse.py`).

**Stage 3 commit message:** `code(AST-1726): telescope drop-in scrape and helpers`

## Stage 4: Rewire core imports + delete `playwright.py`

**Done when:** `roster.py`, `gazer.py`, and `meteorite.py` import from `src.external.telescope` with the **identical** symbol lists they have today; `src/external/playwright.py` is deleted; `rg 'src\.external\.playwright|external\.playwright' src/` returns no matches under `src/` (scripts/spikes may still mention it — out of Scope, leave them).

1. In `src/core/roster.py`, change only:

```python
from src.external.telescope import (
    # same names, same order as current playwright import
)
```

2. Same one-line module path change in `src/core/gazer.py` and `src/core/meteorite.py`.

3. **Do not** change call-site argument shapes, symbol names, or `PLAYWRIGHT_CONFIG` usages in those files.

4. Delete `src/external/playwright.py`.

5. Compile check (builder will re-run): `python -m compileall src/external/telescope.py src/core/roster.py src/core/gazer.py src/core/meteorite.py src/utils/config.py`.

⚠️ **Decision:** Scripts under `scripts/` that still import `playwright` are **out of Scope** — do not edit them in this ticket. If compileall of `src/` is green, stop.

**Stage 4 commit message:** `code(AST-1726): rewire core imports delete playwright`

## Estimate

Confirm Chuckles estimate: 5 — agree

Full drop-in of a ~2.5k-LOC scrape module onto HTTP handles + pool + Firefox uninstall is multi-component and not a known tiny pattern; 5 is the child max and matches the port risk.

## Joan validate

[plan-rubric]
**Ticket:** AST-1726
**Overall:** APPROVED
**Corpus:** 751624d7ebdf9bc441fc3d08a51ae751ea8026af
**Publish ref tip:** 0ee051dec110ebb320b024df35912f61af7c1290 (`origin/sub/AST-1721/AST-1726-platform-telescope-py-drop-in-playwright-decommission`)

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.entity.batch-processing | A | | |
| patt.entity.batch-criteria | A | | |
| stat.logging.error | B | | |
| stat.logging.warning | B | | |
| stat.logging.info | B | | |
| stat.logging.debug | B | | |
| patt.external.web-scraping-via-telescope | X | | pending Archie — id-only; not scoring law this pass |

## Traceability

AC4→S1 `cull_html_default` + S3 `extract_page_dom` local `_cull_html`; AC6→S1 Firefox uninstall scripts + drop `playwright` dep + S3 no `async_playwright`/`firefox.launch` + S4 delete `playwright.py` (see discuss: `BatchBrowserSession` name retained); AC7→S3 full public-surface port + S4 core import-path-only rewire; AC8→S3 post-render helpers local in `telescope.py`; AC9→S1 `TELESCOPE_CONFIG` env base URLs, no `service.*` import; AC13→Explicit scope gate (no Surfer).

## Findings

### discuss — Parent AC 6 literal grep vs drop-in class name

- **Severity:** discuss
- **Location:** Stage 2 `BatchBrowserSession`; parent AC 6
- **Finding:** Plan keeps `class BatchBrowserSession` and `create_batch_browser_session` for drop-in parity (AC 7). Parent AC 6 also requires `rg BatchBrowserSession src/` → no matches. Intent is satisfied (no in-process Firefox); literal grep text conflicts with retained public batch-session API name.
- **Recommendation:** Add a one-line ⚠️ Decision in Stage 2 naming the conflict and stating builder verifies **no** `async_playwright` / `firefox.launch` / Playwright package import — the AC 6 bar for this child. Archie may narrow parent AC 6 grep to launch patterns only if UAT will run the literal `BatchBrowserSession` check.

### discuss — Canon Scope gap (do not score)

- **Severity:** discuss
- **Location:** Citations vs `astral.layers.import-direction`
- **Finding:** `service/*`↔`src/` bidirectional fence plainly governs `telescope.py` imports but is not on this child’s frozen list (owned by AST-1727 CI + AST-1725 service side). Plan forbids `service.*` and `playwright` imports in Stage 2.
- **Recommendation:** No plan change; AST-1727 lands CI enforcement.

### acceptable — Scope gate resolved

- **Severity:** acceptable
- **Location:** `[scope-gate]` comment; Explicit scope gate; ticket ## Scope
- **Finding:** Hedy’s scope-gate for `scripts/build_railway.sh`, `scripts/setup_dev.sh`, `scripts/start_server.py`, and `playwright_browsers_path` removal is reflected in ticket Scope, Files Changed, and Stage 1. Plan returned to Plan Ready.
- **Recommendation:** None.

### acceptable — Batch patterns

- **Severity:** acceptable
- **Location:** Canon notes; Stage 2 `_TelescopePool`
- **Finding:** Plan does not invent claim/clear or criteria literals. Caller semaphores (`roster`/`gazer` `max_concurrent`, meteorite `playwright_concurrency`) stay untouched. `TELESCOPE_CONFIG.max_in_flight` is HTTP socket backpressure only — correct partition.
- **Recommendation:** None.

### acceptable — Lazy-fetch decision

- **Severity:** acceptable
- **Location:** Stage 2 lazy fetch; Stage 3 `load_all_jobs` / `wait_for_careers_list_readiness`
- **Finding:** Deferred Telescope round-trip until extract, after `expand`/`wait_ready` flags are set, preserves gazer/roster call order without double-load. Aligns with AST-1725 service semantics.
- **Recommendation:** None.

### acceptable — Scripts / tests out of scope

- **Severity:** acceptable
- **Location:** Out-of-scope table; Stage 4 step 5
- **Finding:** `scripts/` spikes and component tests still importing `playwright` are explicitly out of Scope; Betty owns test-tree updates. Core `src/` rewires are in Scope.
- **Recommendation:** None.

### acceptable — R6 definition fidelity

- **Severity:** acceptable
- **Location:** Explicit scope gate; Stages 1–4; `## Estimate`
- **Finding:** Plan matches child Scope and parent platform drop-in slice. No `service/**`, Railway, or Surfer creep. Self-assessment (`Confirm Chuckles estimate: 5 — agree`) is honest for a ~2.5k-LOC HTTP port. No `!!-NONE` conf gaps.
- **Recommendation:** None.

### acceptable — Plan Discuss

- **Severity:** acceptable
- **Location:** Linear comments
- **Finding:** Plan Discuss rounds completed: **0** (scope-gate was pre–Plan Ready resolution, not a `[plan-discuss] round=N` pair).
- **Recommendation:** N/A.

context_tokens≈78000

## Review (build stub)

**Built:** `origin/sub/AST-1721/AST-1726-platform-telescope-py-drop-in-playwright-decommission` @ `52a77415`.

**Stages delivered:**
- Stage 1: `TELESCOPE_CONFIG` + httpx pin + Firefox uninstall scripts — `c177bea8`.
- Stage 2: HTTP pool + client `BrowserSession`/`PageHandle`/`BatchBrowserSession` — `f2e942fa`.
- Stage 3: scrape via Telescope HTTP + local post-render helpers (cull default on) — `b8e6c3d8`.
- Stage 4: core import rewires + delete `playwright.py` — `52a77415`.

**Betty:** drop-in surface parity (same public names), cull-default-on HTML path, pool failover/timeout → infra classes, no `src.external.playwright`, no platform Firefox install in build/dev/start scripts, `TELESCOPE_BASE_URL(S)` + bearer required for live scrapes.

## Radia review

[code-rubric]
**Ticket:** AST-1726
**Publish ref:** `8fcb5cc6e4e085cec7955b7e9a0cb999009e7730` (`origin/sub/AST-1721/AST-1726-platform-telescope-py-drop-in-playwright-decommission`)
**Corpus:** `751624d7ebdf9bc441fc3d08a51ae751ea8026af`
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.entity.batch-processing | A | | |
| patt.entity.batch-criteria | A | | |
| stat.logging.error | B | | |
| stat.logging.warning | B | | |
| stat.logging.info | B | | |
| stat.logging.debug | B | | |
| patt.external.web-scraping-via-telescope | X | | pending Archie — id-only; not scoring law this pass |

## Column diff vs plan stage

(aligned)

## Frame diff

(none)

## Findings

### discuss — Parent AC 6 vs retained `BatchBrowserSession` name

- **Severity:** discuss
- **Location:** `src/external/telescope.py` (`BatchBrowserSession`, `create_batch_browser_session`); parent AC 6
- **Finding:** Plan retains public batch-session names for drop-in parity (AC 7). `rg BatchBrowserSession src/` will still match. No `async_playwright`, `firefox.launch`, or `playwright` package import anywhere under `src/`; platform Firefox is fully decommissioned.
- **Recommendation:** UAT should verify launch-pattern grep, not class-name grep alone. Archie may narrow parent AC 6 if the literal `BatchBrowserSession` check is still in the parent checklist.

### discuss — Canon Scope gap (do not score)

- **Severity:** discuss
- **Location:** Citations vs `stat.layers.import-rules` / service↔`src` fence
- **Finding:** Bidirectional import fence plainly governs `telescope.py` but is not on this child’s frozen list. Implementation forbids `service.*` imports; no `service` import in `telescope.py`. CI enforcement remains AST-1727.
- **Recommendation:** No code change on this tip.

### discuss — pending pattern (do not score)

- **Severity:** discuss
- **Location:** Citations / `patt.external.web-scraping-via-telescope`
- **Finding:** Id does not resolve in active corpus. Diff routes headless I/O through HTTP to the Telescope service and keeps post-render helpers local in `src/external/telescope.py` — consistent with plan deferral.
- **Recommendation:** Remains id-only until Archie approves.

### advisory — `per_node_max_in_flight` config unused

- **Severity:** advisory
- **Location:** `src/utils/config.py` `TELESCOPE_CONFIG["per_node_max_in_flight"]`; `src/external/telescope.py` `_TelescopePool`
- **Finding:** Config key is present (plan Stage 1 table: “soft cap tracking per base_url”). Pool tracks `_in_flight` per base for retry sort preference but does not enforce the per-node cap value.
- **Recommendation:** Optional follow-up to wire soft-cap rejection or document that sort-only is intentional; not a drop-in blocker.

### advisory — out-of-scope scripts still reference deleted module

- **Severity:** advisory
- **Location:** `scripts/test_getVisibleText.py`, `scripts/spikes/*`, etc.
- **Finding:** Multiple `scripts/` files still `from src.external.playwright import …`. Plan Stage 4 explicitly excludes scripts from Scope; `src/` compile path is clean.
- **Recommendation:** Separate script-retarget ticket or spike cleanup; not AST-1726 fix-now.

### advisory — `extract_site_page_list` progress gated on `debug` param

- **Severity:** advisory
- **Location:** `src/external/telescope.py` — `extract_site_page_list`
- **Finding:** Crawl-depth `info` lines emit only when caller passes `debug=True` (ported from former module). Main scrape success paths log ungated `info` via `_post_telescope` / `_post_telescope_html`.
- **Recommendation:** Acceptable B variance on deep-crawl diagnostics; optional ungate in a later logging pass.

## What's solid

- Full four-stage delivery on publish ref (`c177bea8` → `52a77415`) plus Betty `test` + `merge-tests` at tip `8fcb5cc6`.
- `src/external/playwright.py` deleted; core rewires in `roster.py` / `gazer.py` / `meteorite.py` are import-path-only (verified diff).
- `telescope.py` is HTTP client + local post-render port: `require_controlled_external_io`, bearer auth, round-robin pool with 5xx/timeout failover, `cull_html_default=True` on `extract_page_dom`, lazy fetch preserves expand/wait_ready ordering.
- `requirements.txt`: `playwright` removed, `httpx` added; `build_railway.sh` / `setup_dev.sh` / `start_server.py` no longer install or seed Firefox.
- `TELESCOPE_CONFIG` + trimmed `PLAYWRIGHT_CONFIG`; `playwright_browsers_path` gone from `RAILWAY_CONFIG`.
- Component tests cover drop-in handles, pool failover/timeout/bearer, cull default, classifier + `telescope_timeout`, module-gone assertion; roster tests retargeted to `telescope`.

## Recommended actions (downstream only — not executed here)

- Chuckles: append this artifact to the issue doc, commit `docs(AST-1726): Radia review — clean`, push, post slim upshot `--as radia`, move to Review Posted.
- datt: PROCEED → User Testing (no `resolve-child` round needed).
- Optional later: script retarget sweep; wire or document `per_node_max_in_flight`; parent AC 6 grep clarification with Archie.

context_tokens≈42000

## Bug: AST-1728 — Telescope Admin page

UAT-batch fix against amended AST-1721 Component/Technical scope (admin UI/API + scrape metadata). Lives on this plan doc because the admin proxy calls Telescope through `src/external/telescope.py` (platform seam). Does not rewrite Stages 1–4 above.

### As-is

No admin screen exists to call Telescope with a URL, response type (html vs text), and optional-parameter toggles, or to inspect the raw scrape payload and scrape health metadata.

### To-be

An admin-authenticated operator opens a Telescope admin page, submits a URL with html|text and toggles for optional Telescope parameters, and sees the raw response body plus scrape metadata (bot-block / cookies / other scrape failures when present) — parent AC 14.

### Repro

1. Sign in as admin on the platform SPA.
2. Look for any Admin/Tools nav entry named Telescope (or route `/admin/telescope`) — absent.
3. Confirm `rg -n "admin/telescope|/api/admin/telescope" src/ui/` returns no matches.
4. Confirm `POST /telescope` / `/telescope/html` JSON has no `scrape_meta` (only `final_url` + `text`/`html`/`links`).

### Root cause

Epic ships service + platform client + CI, but no operator workbench. Responses also lack structured scrape-health metadata, so even a raw curl cannot show bot-block / cookie / unclean-scrape signals Susan asked for.

### Proposed change

⚠️ **Decision — metadata on the service, pass-through on the client:** Browser-visible facts (`bot_blocked`, cookie dismiss outcome, empty/short content) are computed in `service/telescope/` during the scrape. `src/external/telescope.py` forwards `scrape_meta` unchanged. Admin API does not invent heuristics that need a live page.

⚠️ **Decision — admin shows service raw by default:** HTML `cull` is an optional admin toggle defaulting **off** so the pane shows service HTML; when on, apply platform `_cull_html` after the HTTP call (same helper as the drop-in). Core drop-in callers keep `cull_html_default=True` unchanged.

⚠️ **Decision — additive JSON only:** Existing `/telescope` and `/telescope/html` fields stay; add sibling key `scrape_meta`. Drop-in callers that ignore unknown keys keep working.

1. **`service/telescope/interact.py`** — Change `dismiss_cookies(page)` to return `bool` (`True` if any selector/fuzzy click succeeded; `False` otherwise). Keep always-run behavior.

2. **`service/telescope/capture.py` (or new small helper in same package, e.g. `meta.py`)** — Add `build_scrape_meta(*, requested_url: str, final_url: str, text_or_html: str | list, cookies_dismissed: bool) -> dict` returning:

```python
{
  "bot_blocked": bool,
  "cookies_dismissed": bool,
  "issues": list[str],  # subset of: "bot_blocked", "empty_content", "short_content"
  "content_chars": int,  # sum of lengths for list text; len for str
}
```

   - `bot_blocked`: case-insensitive substring match on concatenated visible text (or HTML) against this fixed list (service-owned constants, not imported from `src`): `cloudflare`, `attention required`, `just a moment`, `captcha`, `are you a robot`, `verify you are human`, `access denied`, `unusual traffic`, `enable javascript and cookies`.
   - `empty_content`: content_chars == 0.
   - `short_content`: 0 < content_chars < 80 (and not already empty).
   - `issues` lists only the true flags (include `"bot_blocked"` when that bool is true).

3. **`service/telescope/app.py`** — In both `post_telescope` and `post_telescope_html` work functions: capture `cookies_dismissed = await dismiss_cookies(page)` (today dismiss is inside `_run_browser_job` — **move** cookie dismiss into each route’s `work` closure **or** thread the bool out of `_run_browser_job` so meta can see it; prefer extending `_run_browser_job` to return `(result, cookies_dismissed)` so navigate/expand/wait_ready stay shared). Attach `result["scrape_meta"] = build_scrape_meta(...)`. Do not remove existing keys.

4. **`src/external/telescope.py`** — `_post_telescope` / `_post_telescope_html` already `return data` from `resp.json()` — keep that (meta passes through). Add:

```python
async def admin_telescope_scrape(
    url: str,
    *,
    response_type: str,  # "text" | "html"
    expand: Optional[bool] = None,
    wait_ready: Optional[bool] = None,
    links: bool = True,
    selector: Optional[str] = None,
    cull: bool = False,
) -> dict:
```

   - `response_type == "text"` → `_post_telescope(...)`; `"html"` → `_post_telescope_html(...)`.
   - Invalid `response_type` → raise `ValueError("response_type must be text or html")`.
   - If `response_type == "html"` and `cull` and `"html" in data`: `data = {**data, "html": _cull_html(data["html"])}` (copy dict; do not mutate shared state).
   - Return the full JSON dict (content + `scrape_meta` + top-level fields).
   - Log one succinct `info` on success: `telescope admin scrape type=%s final_url=%s` (stat.logging.info semantic via `get_logger`).

5. **`src/ui/api/api_admin.py`** — Add `@admin_bp.route("/telescope", methods=["POST"])` + `@require_admin`:

   - Body JSON keys: `url` (required non-empty str), `response_type` (`"text"`|`"html"`, required), `expand` (bool, default `True`), `wait_ready` (bool, default `False`), `links` (bool, default `True`, text only), `selector` (optional str), `cull` (bool, default `False`, html only).
   - Call `asyncio.run(admin_telescope_scrape(...))` — same bridge as `adhoc` test in this file (`asyncio.run(run_adhoc_workbench_test(...))`).
   - Success: `200` + JSON body = scrape dict.
   - `PlaywrightInfraError` / connect failures: `502` `{"error": "<failure_class>", "detail": "<message>"}`.
   - Validation errors: `400` `{"error": "..."}`.
   - Never send candidate/Stytch credentials to Telescope; bearer stays env-only inside `telescope.py`.

6. **`src/ui/frontend/src/pages/AdminTelescope.tsx`** — New page (AdminRoute child):
   - Controls: URL text input; response type radio/select `text` | `html`; toggles `expand` (default on), `wait_ready` (default off), `links` (default on, disabled when html), `cull` (default off, disabled when text); optional selector text input; Submit button.
   - On submit: `api("/api/admin/telescope", { method: "POST", body: JSON.stringify(...) })`.
   - Display: (a) scrape metadata panel showing `scrape_meta` fields + HTTP/error state; (b) raw body pane — `text` (join list with `\n---\n` if array) or `html` string, plus a collapsible full JSON dump of the response.
   - Loading + error toast/inline error; no cards beyond what’s needed for the form/result interaction.

7. **`src/ui/frontend/src/routes.tsx`** — Import page; add `{ path: "admin/telescope", element: <AdminRoute><AdminTelescope /></AdminRoute> }` next to other admin tool routes.

8. **`src/utils/config.py`** — In `NAV_CONFIG` Tools `admin_only` group, add `{"label": "Telescope", "path": "/admin/telescope"}` after Agent Ad Hoc (or at end of Tools items).

**Out of this bug:** Phase 2 autoscaler, Surfer extension, changing core roster/gazer/meteorite call shapes, amending CI fence, rewriting Stages 1–4 of this doc.

### Blast radius

- Service JSON grows `scrape_meta` — Betty’s AST-1725 contract tests may need additive asserts (Betty owns tests).
- Platform `_post_telescope*` return dicts may now include `scrape_meta`; drop-in helpers that only read `text`/`html`/`links`/`final_url` stay fine.
- Admin nav / routes / `api_admin` surface — admin-only; candidates unaffected.
- `dismiss_cookies` return-type change — only service callers (app.py).

### What must still hold

- Parent AC 2–13 unchanged (import fence, drop-in shapes, no platform Firefox, bearer env-only, no Phase 2 / Surfer).
- Parent AC 3 field set remains; `scrape_meta` is additive.
- Cookie dismiss still always runs; expand default on; wait_ready default off; links default on for text.
- Platform cull default-on for **drop-in** HTML helpers (`cull_html_default`); admin cull toggle is separate and defaults off.
- `service/*` ↔ `src/` never import either direction.
- Telescope still console-only (no `app_log` / DB).
