<!-- linear-archive: AST-1726 archived 2026-10-02 -->

## Linear archive (AST-1726)

**Archived:** 2026-10-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1726/platform-telescopepy-drop-in-and-playwright-decommission-astral  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** None / 5  
**Parent:** AST-1721 — Astral Telescope — stateless headless-scraping microservice (per-URL)  
**Blocked by / blocks / related:** parent: AST-1721; blocks: AST-1727

### Description

## What this implements

Add `src/external/telescope.py` as the **full** drop-in port of today's `playwright.py` (same public names/params for core's import surface; HTTP pool dispatch + retry + env bearer for headless scrape paths; **all** former non-browser / post-render helpers — cull, delimiter splits, extract-from-HTML, etc. — live in this same file for Surfer reuse; no `page_parse.py`); delete `src/external/playwright.py`; change `roster.py` / `gazer.py` / `meteorite.py` import module path only; add Telescope pool/auth/timeout/concurrency keys in config; pin platform HTTP client in root requirements and drop platform Firefox launch deps. After #1. Does not own Railway service deploy or CI import fence (#3). Does not build Surfer.

## Citations

`patt.entity.batch-processing`; `patt.entity.batch-criteria`; `stat.logging.error`; `stat.logging.warning`; `stat.logging.info`; `stat.logging.debug`; new-pattern flag `patt.external.web-scraping-via-telescope` (pending Archie)

## Scope

- [X] `src/external/telescope.py` — **new** — full drop-in replacement for `playwright.py`: same public names/params; HTTP client for headless scrape surfaces; **all** former non-browser / post-render helpers live in this same file (Surfer-ready shared processing); no in-process Firefox.
- [X] `src/external/playwright.py` — **deleted** — fully decommissioned; no thin-client leftover under this name.
- [X] `src/core/roster.py` — **modified** — import module path `playwright` → `telescope` only; no call-site shape changes.
- [X] `src/core/gazer.py` — **modified** — same import-path-only rewire.
- [X] `src/core/meteorite.py` — **modified** — same import-path-only rewire.
- [X] `src/utils/config.py` — **modified** — Telescope base URL(s), env bearer token key, client timeout, platform in-flight pool semaphore / per-node caps, and Telescope-facing defaults that must not live as literals in callers; drop or stop using `RAILWAY_CONFIG["playwright_browsers_path"]` once platform Firefox is gone.
- [X] `requirements.txt` — **modified** — add direct `httpx` for the platform Telescope client; drop platform Playwright browser runtime needs once no process launches Firefox.
- [X] `scripts/build_railway.sh` — **modified** — remove `PLAYWRIGHT_BROWSERS_PATH` export and `playwright install --with-deps firefox`.
- [X] `scripts/setup_dev.sh` — **modified** — remove `"$VENV/bin/python" -m playwright install firefox`.
- [X] `scripts/start_server.py` — **modified** — remove the `RAILWAY_CONFIG["playwright_browsers_path"]` → `PLAYWRIGHT_BROWSERS_PATH` env seed.

## Acceptance criteria

- [X] Parent AC 4 (cull default via platform helper)
- [X] Parent AC 6 (playwright gone / no platform Firefox)
- [X] Parent AC 7 (drop-in API)
- [X] Parent AC 8 (shared post-render helpers in src)
- [X] Parent AC 9 (platform points at separate host)
- [X] Parent AC 13 (no Surfer build)

## Boundaries

- [X] Does not own Telescope service (#1) or Railway/CI (#3). Does not build Surfer extension.

## Notes for planning

`patt.entity.batch-processing`; `patt.entity.batch-criteria`; `stat.logging.error`; `stat.logging.warning`; `stat.logging.info`; `stat.logging.debug`; new-pattern flag `patt.external.web-scraping-via-telescope` (pending Archie)

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at dispatch-parent.

## QA test manifest

**Classification:** Broken/obsolete (playwright → telescope retarget) + Gaps (HTTP pool / cull / TELESCOPE_CONFIG). Existing: roster infra prefix + readiness wiring (revised). Integration drift: none.

1. `tests/component/external/test_telescope.py` — drop-in helpers, classifier (+ telescope_timeout), get_page PageHandle, HTTP pool failover/timeout/bearer, cull default, playwright module gone
2. `tests/component/utils/test_config.py::TestAst853PlaywrightConfig` — trimmed PLAYWRIGHT_CONFIG (no Firefox launch keys)
3. `tests/component/utils/test_config.py::TestAst1726TelescopeConfig` — TELESCOPE_CONFIG + no playwright_browsers_path
4. `tests/component/core/test_roster.py::TestAst689ScrapeReadiness` — wait_ready ready / empty (Telescope client)
5. `tests/component/core/test_roster.py::TestAst701ScrapeCompanyHomepageContent::test_playwright_infra_error_prefixes_failure_class` — import telescope; `[playwright:…]` prefix unchanged

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/external/test_telescope.py \
  tests/component/utils/test_config.py::TestAst853PlaywrightConfig \
  tests/component/utils/test_config.py::TestAst1726TelescopeConfig \
  tests/component/core/test_roster.py::TestAst689ScrapeReadiness \
  tests/component/core/test_roster.py::TestAst701ScrapeCompanyHomepageContent::test_playwright_infra_error_prefixes_failure_class \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

**Bible:** `docs/test-bible/external/telescope.md` (canonical); `playwright.md` retired pointer; AST-1726 notes on roster/config; `LOCKED_AT_100` → `src/external/telescope.py`

**Bible shasum** (`origin/sub/AST-1721/AST-1726-platform-telescope-py-drop-in-playwright-decommission`):

* `docs/test-bible/external/telescope.md` — `0f24d59952b849feff44380f85e8b564add29acf`
* `docs/test-bible/external/playwright.md` — `b4061f181354d7d9577f18dc06984653bf0fda95`
* `docs/test-bible/core/roster.md` — `701e1ad703bc68961b5d03b1da0de8f4b1554c65`
* `docs/test-bible/utils/config.md` — `6966d6014a1847bda00c8a130b0f41e1ddcf127a`
* `docs/test-bible/README.md` — `e0865243163eaf72b311e9d0e85f996a06f372bd`

### Comments

#### radia — 2026-09-20T05:44:27.318Z
[code-rubric] PROCEED (Commit: 8fcb5cc6e4e085cec7955b7e9a0cb999009e7730) Platform drop-in canon-clean

#### betty — 2026-09-20T05:41:44.877Z
`origin/sub/AST-1721/AST-1726-platform-telescope-py-drop-in-playwright-decommission` @ `8fcb5cc6` · telescope drop-in tests

#### joan — 2026-09-20T05:33:02.291Z
[plan-rubric] PROCEED (Commit: 0ee051dec110ebb320b024df35912f61af7c1290) Drop-in port plan sound

#### hedy — 2026-09-20T05:31:08.680Z
`origin/sub/AST-1721/AST-1726-platform-telescope-py-drop-in-playwright-decommission` @ `0ee051dec110ebb320b024df35912f61af7c1290` · plan ready drop-in

#### hedy — 2026-09-20T05:29:11.160Z
[scope-gate] Cannot finish Plan Ready without Scope rows for platform Firefox uninstall scripts.

Needed files / change kinds (not in ticket ## Scope today):
1. `scripts/build_railway.sh` — remove `PLAYWRIGHT_BROWSERS_PATH` export + `playwright install --with-deps firefox` (platform image must stop launching/installing Firefox once root `requirements.txt` drops `playwright`).
2. `scripts/setup_dev.sh` — remove `"$VENV/bin/python" -m playwright install firefox`.
3. `scripts/start_server.py` — remove the `RAILWAY_CONFIG["playwright_browsers_path"]` → `PLAYWRIGHT_BROWSERS_PATH` env seed (no platform browser runtime).

Quoted Scope covering deps today:
> `requirements.txt` — **modified** — add direct `httpx` …; drop platform Playwright browser runtime needs once no process launches Firefox.

That covers the pip pin only. Leaving the install/env scripts in place after removing the package makes platform Railway/`setup_dev` fail on `playwright` not found — so the drop-in cannot ship inside declared Scope.

Also in `src/utils/config.py` (already in Scope): drop or stop using `RAILWAY_CONFIG["playwright_browsers_path"]` once `start_server.py` is allowed to drop the env seed.

Please amend ## Scope with those three script paths (and confirm config may remove `playwright_browsers_path`). Re-spawn plan-child after. Not tagging @susan — Chuckles can add the rows if the approach stays "uninstall platform Firefox + httpx client" as already defined.

---

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

## Radia review-fix (AST-1728)

Overall: CLEAN. [bug-repro] OK; What must still hold OK. Advisories only. Clean-review shortcut → User Testing (resolve skipped).

## Bug: AST-1730 — Telescope admin response not scrollable / selectable

UAT-batch fix against AST-1721 Component/Technical scope (`src/ui/frontend/` admin Telescope raw response pane). Sibling of AST-1728 on this doc; does not rewrite Stages 1–4 or the AST-1728 block.

### As-is

After a successful admin Telescope scrape, the raw response (and optional full JSON dump) render in an unbounded `<pre className="admin-telescope-pre">` with no wrap, no max-height, and no overflow scroll. The operator cannot scroll the full payload or treat it as a text field for select-all.

### To-be

The admin raw response (and the optional full JSON dump) each appear in a read-only, wrapping, scrollable text field so the operator can scroll the full payload and select-all / copy it.

### Repro

1. Sign in as admin; open `/admin/telescope`.
2. Submit any URL that returns a multi-screen body (or toggle Show full JSON on a large scrape).
3. Observe the Raw text|html pane: content expands the page with no inner scroll; long lines do not wrap; Ctrl/Cmd+A does not select the payload as a focused text field.

### Root cause

AST-1728 step 6 rendered results with bare `<pre>` elements and never defined `.admin-telescope-pre` styles (no `white-space` wrap, no `max-height` / `overflow`). A `<pre>` is also not a form text control, so select-all behavior is awkward for operators.

### Proposed change

⚠️ **Decision — read-only `<textarea>`, not styled `<pre>`:** Match existing admin read-only payload panes (`JobMeteoritePane`, `BatchAgentDataModal`): a focused text control gives native select-all / copy. Both the raw body pane and the optional full-JSON pane get the same control (both are response display).

⚠️ **Decision — scroll viewport `maxHeight: "60vh"`:** Same bound as `AdminSessionResumePaste` / `AdminManageCandidates` JSON panes. Required for “scrollable”; not a content truncation — overflow is `auto`.

1. **`src/ui/frontend/src/pages/AdminTelescope.tsx`** only:
   - Replace the Raw `{responseType}` `<pre className="admin-telescope-pre">…</pre>` with:

     ```tsx
     <textarea
       className="admin-telescope-pre"
       readOnly
       value={formatBody(result, responseType)}
       spellCheck={false}
       style={{
         display: "block",
         width: "100%",
         boxSizing: "border-box",
         minHeight: 200,
         maxHeight: "60vh",
         overflow: "auto",
         whiteSpace: "pre-wrap",
         wordBreak: "break-word",
         fontFamily: "monospace",
         fontSize: 12,
         lineHeight: 1.5,
         resize: "vertical",
       }}
     />
     ```

   - Replace the Show-full-JSON `<pre className="admin-telescope-pre">…</pre>` with the same `<textarea readOnly>` shape, `value={JSON.stringify(result, null, 2)}`.
   - Keep `formatBody`, metadata list, form controls, and API call unchanged.
   - No new CSS file required (inline styles, same as sibling admin tools); keep `className="admin-telescope-pre"` for a stable hook.

**Out of this bug:** service / `telescope.py` / `api_admin` contract, scrape_meta shape, nav/routes, AST-1728 metadata behavior.

### Blast radius

- Admin Telescope UI only — candidates and core scrape callers untouched.
- Existing AST-1728 vitest only asserts the page module exports a component; no `<pre>` DOM assert to break.
- Optional: Betty may add a shallow assert that the raw pane is a `textarea[readonly]` — Betty owns tests.

### What must still hold

- Parent AC 14 / AST-1728 to-be: admin can submit URL + toggles and see raw body + scrape_meta (metadata list stays; only the body/JSON display widget changes).
- No change to `/api/admin/telescope` request/response shape.
- `service/*` ↔ `src/` import fence unchanged.
- No depth/output limits on scrape content itself — only a scroll viewport on the display control.

## Radia review-fix (AST-1730)

Overall: CLEAN. [bug-repro] OK; What must still hold OK. Clean-review shortcut → User Testing.

## Bug: AST-1734 — Telescope admin page / full JSON not scrollable

UAT-batch fix against AST-1721 Component/Technical scope (`src/ui/frontend/` admin Telescope page). Sibling of AST-1728 / AST-1730 on this doc; does not rewrite Stages 1–4 or those bug blocks. **Distinct from AST-1730:** that ticket made the response *textareas* scrollable; this ticket makes the *page* scrollable so those panes (especially full JSON below the form) are reachable.

### As-is

The Telescope admin page itself does not scroll. With form + metadata + raw pane already filling the viewport, opening **Show full JSON** leaves only a one-line-high strip of the JSON textarea visible; the operator cannot scroll the page to reach the rest of the payload.

### To-be

The Telescope admin page scrolls (via the existing shell `.content` scroller) so the operator can navigate the full form + metadata + raw + full-JSON stack. AST-1730 textarea inner-scroll / select-all behavior remains.

### Repro

1. Sign in as admin; open `/admin/telescope`.
2. Submit a URL that returns a non-trivial body (enough that raw pane + form consume most of the viewport).
3. Click **Show full JSON**.
4. Observe: the page/document does not scroll; only a thin (≈one-line) band of the JSON textarea is visible below the toggle; wheel/trackpad on the page background does not reveal more content.

### Root cause

`AdminTelescope` roots in `<div className="list-page">`. Global `.list-page` (App.css) is built for table tools:

```css
.list-page {
  height: calc(100% - 40px);
  overflow: hidden;
  /* + flex column */
}
```

That locks the card to the viewport and clips overflow. List tables recover via an *inner* `.list-page-table-wrap--scroll`; AdminTelescope has no such inner page scroller — AST-1730 only capped the textareas (`maxHeight: 60vh`). Form + meta + raw pane consume the fixed card height, so the full-JSON textarea is clipped to a sliver. Sibling form tools (e.g. Agent Ad Hoc) avoid `.list-page` height/overflow lock so `.content { overflow-y: auto }` scrolls the page.

### Proposed change

⚠️ **Decision — fix page flow on AdminTelescope only; do not change global `.list-page`:** Table pages still need the fixed-height + `overflow: hidden` + inner table scroll contract. Touched file stays inside parent scope `src/ui/frontend/`.

⚠️ **Decision — keep AST-1730 `RESPONSE_PANE_STYLE` textareas:** Inner pane scroll/select-all stays; this bug only unlocks the outer page so both panes remain reachable when stacked.

1. **`src/ui/frontend/src/pages/AdminTelescope.tsx` only:**
   - On the root wrapper that currently is `<div className="list-page">`, override the two clipping properties so the card grows with content and participates in `.content` page scroll. Prefer the smallest override that matches existing admin form tools:

     ```tsx
     <div className="list-page" style={{ height: "auto", overflow: "visible" }}>
     ```

     Equivalent acceptable alternative (same outcome): drop `list-page` and use the Agent Ad Hoc free-flow shell (`style={{ padding: 24, maxWidth: 1100 }}`) with the same title/subtitle children — pick one; do not do both.

   - Leave `RESPONSE_PANE_STYLE`, form controls, metadata list, API call, and show/hide full JSON toggle unchanged.
   - Do **not** edit `App.css` `.list-page` globally.
   - Do **not** change `/api/admin/telescope`, `telescope.py`, or the service.

**Out of this bug:** AST-1730 textarea widget choice; scrape contract / scrape_meta; nav/routes; service.

### Blast radius

- Admin Telescope UI layout only — candidates and core scrape callers untouched.
- Other `.list-page` consumers (ListPage tables, Execution History, etc.) unchanged if the override stays page-local.
- AST-1730 vitest / shallow asserts on `textarea[readonly]` stay valid.

### What must still hold

- Parent AC 14 / AST-1728 to-be: submit URL + toggles; see raw body + scrape_meta.
- AST-1730 to-be: raw + full-JSON panes remain read-only wrapping scrollable textareas with native select-all (no regression to bare `<pre>`).
- No change to `/api/admin/telescope` request/response shape.
- `service/*` ↔ `src/` import fence unchanged.
- No depth/output limits on scrape content — only layout scroll so the existing panes are reachable.

## Resolution (AST-1734) — 2026-09-21

Radia `review-fix` overall FIX-NOW (`880d96ef`): drop/revert `data/admin/agent_task.json` (AST-1722 Land Meteorite stubs) from this publish ref before merge-child; keep AdminTelescope page-scroll fix.

**fix-now — `agent_task.json`:** No tree edit. At resolve time the file is **byte-identical** to both `origin/ftr/AST-1721-astral-telescope-stateless-headless-scraping` (`b756e235`) and `origin/dev` (`cmp` clean). Two-dot `git diff` vs ftr/dev is empty; `origin/ftr…HEAD` for this path has no commits. Radia's 38-line three-dot delta was against an older ftr tip / multi-merge-base phantom — deleting or reverting the catalog now would *create* a stray deletion vs current ftr/dev. AdminTelescope scroll override unchanged (`height: auto` / `overflow: visible`).

**Discuss — sibling merge-tests:** Left as-is (Betty shared `astral-tests` delivery); not product scope for this bug.

**Advisory — plan match:** Confirmed; no further change.

## Radia review-fix (AST-1734)

Overall: REVIEW addressed — page-scroll fix kept; agent_task.json clear vs ftr/dev. Clean → User Testing.

## Bug: AST-1751 — Errors must not count as fails; fails only BOT_BLOCKED and NOT_A_JOB

UAT-batch fix against amended AST-1721 Component/Technical scope (`meteorite.py` scrape-batch counter exception). Lives on this plan doc because AST-1726 owns `src/core/meteorite.py` in the epic. Complements [AST-1742](https://linear.app/astralcareermatch/issue/AST-1742) (inbox / ingest `NOT_A_JOB` → fail); does not rewrite Stages 1–4 or other bug blocks above.

### As-is

`run_scrape_meteorite` (and sibling meteorite dispatch runners) treat ERROR / `SCRAPE_ERROR` / `scrape_closed` rows as **both** fail and error: each such row does `total_failed += 1` and `total_errors += 1`. Dispatcher logs then show both buckets moving together (UAT: `scrape_meteorite pass:0 fail:5 error:5` for five ERROR rows). Separately, scrape `BOT_BLOCKED` currently increments `total_passed`.

### To-be

Errors are errors only. `total_failed` is reserved for `BOT_BLOCKED` and `NOT_A_JOB` (meteorite-domain outcomes — classify/`stage_meteorite` for `NOT_A_JOB`, scrape page-status for `BOT_BLOCKED`), not for Telescope HTTP itself and not for ERROR / `SCRAPE_ERROR` / `scrape_closed`. A batch of five scrape ERROR rows must report `fail:0 error:5` (with `pass` unchanged aside from real READY successes).

### Repro

1. Candidate with ≥5 meteorite rows in `SCRAPE_LINK` whose Telescope scrape returns visible text that `_classify_jd` maps to a non-ok / non-blocked page status (e.g. `scrape_closed` → `SCRAPE_ERROR`), as in the AST-1750 UAT log.
2. Run dispatch task `scrape_meteorite` for that candidate.
3. Observe dispatcher completion line: `scrape_meteorite pass:0 fail:N error:N` with the same N (broken). Post-fix: `fail:0 error:N`.

### Root cause

Meteorite dispatch runners (AST-1560 era) hard-coded ERROR-family branches as `total_failed += 1` **and** `total_errors += 1` in the same arm. That made ERROR also look like a fail in operator rollups. AST-1742 fixed the inbox/`stage_meteorite` skip → fail contract and **explicitly deferred** scrape runners; this ticket is that deferred half. Telescope is a red herring for the counter bug — the double-bump is entirely in `meteorite.py` summary arithmetic after the fetch returns.

### Proposed change

**In scope (amended parent):** `src/core/meteorite.py` only — batch summary counters on scrape / sibling dispatch runners. No Telescope service, no `telescope.py`, no config, no UI.

1. **`run_scrape_meteorite`** (observed UAT path)

   - On every ERROR / `SCRAPE_ERROR` arm (missing link; empty / `scrape_*` closed path; bare `except` continuing to next row): increment **`total_errors` only** — remove the paired `total_failed += 1`.
   - On `page_status == "blocked"` → `BOT_BLOCKED`: increment **`total_failed` only** (replace today's `total_passed += 1`). Do not increment `total_errors`. State transition / `_row_miss` / AST-1689 contact-column rules stay unchanged.
   - `READY` success path stays `total_passed += 1`.

2. **Sibling dispatch runners that still double-bump ERROR** — same ERROR→errors-only rule (remove the paired `total_failed += 1` on SCRAPE_ERROR / exception arms):

   - `run_stage_meteorite` — missing classify_outcome, skip-outcome-on-row, missing link/content/breadcrumb, unhandled outcome, exception.
   - `run_land_meteorite` — missing-content ERROR arm (non–empty-BOT_BLOCKED skip), land exception / SCRAPE_ERROR arms that currently double-bump.
   - `run_notify_bot_blocked` (or current notify runner name) — only arms that today do **both** fail and error on an ERROR/exception path; leave pure-`total_failed` “staying BOT_BLOCKED” arms as fail-only.

3. **Do not edit**

   - `stage_meteorite` classify / insert / `NOT_A_JOB` row creation (AST-1742 already counts skip → fail on inbox/ingest).
   - `inbox.check_email` / `ingest_candidate_email_message` / `api_inbox._land_all` (AST-1742).
   - `src/external/telescope.py`, `service/telescope/**`, config keys, admin UI.
   - Row state vocabulary (`SCRAPE_ERROR`, `BOT_BLOCKED`, `READY`, …) and transition guards — counters only.

**Decision — scrape `BOT_BLOCKED`:** count as fail (not pass, not error). Parent Component reserves `total_failed` for `BOT_BLOCKED` / `NOT_A_JOB`; scrape is where `BOT_BLOCKED` is actually set today (`stage_meteorite` does not produce it).

### Blast radius

- Dispatcher / ledger / Performance Monitor rollups for `scrape_meteorite` (and stage/land/notify) will stop showing fail≈error on ERROR batches; ERROR-only batches drop `total_failed` to 0.
- Scrape `BOT_BLOCKED` will start moving `total_failed` instead of `total_passed` — any operator habit or test that treated bot-block as pass must flip (Betty / fix-board).
- AST-1742 inbox fail contract unchanged; AST-1750 (error detail logging) is a sibling, not this ticket.
- Four-key summary shape `{total_processed, total_passed, total_failed, total_errors}` unchanged.

### What must still hold

- Return shape of dispatch runners remains the four int keys above.
- `SCRAPE_LINK` → `READY` | `BOT_BLOCKED` | `SCRAPE_ERROR` state transitions and `_row_miss` / info logging strings unchanged aside from which counter increments.
- AST-1689: bot-block is state-only (do not clear `electronic_contact`).
- AST-1742: inbox / ingest `NOT_A_JOB` / skip → fail; ERROR-family → error — do not regress.
- Telescope HTTP contract and import-path-only rewires for roster/gazer stay out of this bug.
- No depth/output limits or new fail classes invented in Telescope responses.

## Radia review (AST-1751)

**Overall:** CLEAN — `[code-rubric] PROCEED` @ `d892d7e3`.

- **[bug-repro] OK** — ERROR-only batch + BOT_BLOCKED→fail; qa-handoff fixture fixes included.
- **What must still hold — OK** — four-key summary; AST-1689/1742 holds; meteorite.py only.
- **§3h:** resolve-child skipped (clean review).

## Bug: AST-1752 — Closed/missing content is LINK_EXPIRED fail, not SCRAPE_ERROR

UAT-batch fix against amended AST-1721 Component/Technical scope (AST-1752 exception on `meteorite.py` + `config.py`). Lives on this plan doc because AST-1726 owns `src/core/meteorite.py` in the epic (same home as the AST-1751 block above). Does not rewrite Stages 1–4 or the AST-1751 block above. Diagnostic `why` strings from [AST-1750](ast-1725-telescope-service-container-and-api.md) stay; only state, counter, and next-step change for `closed` / `missing`.

### As-is

`_classify_jd` verdicts `closed` and `missing` go through `METEORITE_INGRESS_DISPATCH_CONFIG["scrape_page_status_states"]` to `SCRAPE_ERROR`. `run_scrape_meteorite` then increments `total_errors` and warns via `_row_miss` → `logger.warning` with next step `This row is ERROR`. UAT (`meteorite 92`, Dice): `scrape_closed signal='no longer available' …` then `This row is ERROR`, dispatcher `scrape_meteorite pass:0 fail:0 error:5`. Nothing threw. The same next step `This row is ERROR` is passed for every other soft `SCRAPE_ERROR` arm in `run_stage_meteorite`, `run_scrape_meteorite` (missing link), and `run_land_meteorite`. Thrown faults already use `logger.exception`. `BOT_BLOCKED` already warns `This row is BOT_BLOCKED` and increments `total_failed` only. There is no `LINK_EXPIRED` state.

### To-be

`closed` and `missing` write terminal state `LINK_EXPIRED` and increment `total_failed` only. Five closed rows report `pass:0 fail:5 error:0`. The warning stays `logger.warning`; the next step is `This row is LINK_EXPIRED`. The AST-1750 `why` / row `error` string (`signal=`, `text_len=`, `final_url=`) stays on that warning. A row with no usable link stays `SCRAPE_ERROR`, `total_errors` only, next step `This row is SCRAPE_ERROR`. No soft arm's warning text is `This row is ERROR`. Exceptions stay `logger.exception` and `total_errors` only. `LINK_EXPIRED` does not trigger Estelle bot-block notify.

### Repro

No SQL seed. Fixture text returned as Telescope visible text for a meteorite row already in `SCRAPE_LINK` with an `http://` or `https://` `link`:

1. **Closed.** `visible_text` = `Sorry, this job is no longer available.` (`TRACKER_CONFIG["jd_classifier"]["closed_signals"]` contains `no longer available`). After `run_scrape_meteorite`: row `state` is `LINK_EXPIRED`; `error` still contains `signal='no longer available'`, `text_len=`, and `final_url=`; warning next step is `This row is LINK_EXPIRED`; summary `total_failed=1`, `total_errors=0`. Live shape: the AST-1752 UAT line for meteorite 92 (`final_url=https://www.dice.com/job-detail/c5a9ffeb-c9c9-44a2-b0e4-59668a8d18b3`).
2. **Missing.** `visible_text` = `not a posting` (shorter than `jd_classifier.min_meaningful_chars`, default 500; no closed/bot/cookie hit, so `_classify_jd` returns `missing`). Same outcomes as (1) with `page_status` `missing` and `signal=None` in the `why` string: `LINK_EXPIRED`, `total_failed` only, next step `This row is LINK_EXPIRED`.
3. **Still an error.** `link` empty or not `http://` / `https://` (no fetch). State stays `SCRAPE_ERROR`, `total_errors=1`, `total_failed=0`, warning next step `This row is SCRAPE_ERROR`.

### Root cause

`scrape_page_status_states` maps `closed` and `missing` to `SCRAPE_ERROR`, and the scrape soft-fail tail always does `total_errors += 1` plus next step `This row is ERROR`. Those two verdicts are `_classify_jd` content judgments after Telescope already returned text. They are not a throw, a timeout, an HTTP 5xx, or a missing link. The next-step string says `ERROR` on a `logger.warning`, which names a log level instead of the meteorite state that was written.

### Proposed change

Files: `src/utils/config.py`, `src/core/meteorite.py` only. Do not edit `src/core/gazer.py` (`_classify_jd` / `_CONTACT_PAGE_STATUS` stay shared), `src/external/telescope.py`, `service/telescope/**`, `tests/`, or `docs/test-bible/**`.

1. **`METEORITE_STATES` in `src/utils/config.py`** — add:

   ```python
   "LINK_EXPIRED": {
       "prior_states": ["SCRAPE_LINK"],
   },
   ```

   Add `"LINK_EXPIRED"` to the `assert set(METEORITE_STATES) == {…}` set. Do **not** add `LINK_EXPIRED` to `SCRAPE_LINK["prior_states"]` (no retry onto the scrape queue). Do **not** add `LINK_EXPIRED` to `ABANDONED["prior_states"]` (nag/stale cleanup stays `BOT_BLOCKED` and `SCRAPE_ERROR` only — not in this bug's scope).

2. **`METEORITE_INGRESS_DISPATCH_CONFIG["scrape_page_status_states"]`** — set `"closed"` and `"missing"` to `"LINK_EXPIRED"`. Leave `"blocked": "BOT_BLOCKED"` and `"ok": "READY"`. Widen the values assert from `{"READY", "BOT_BLOCKED", "SCRAPE_ERROR"}` to also include `"LINK_EXPIRED"`.

3. **`METEORITE_BOT_BLOCKED_NOTIFY_CONFIG`** — do not edit. Leave `trigger_state` `BOT_BLOCKED` and the existing `assert _mid_notify["trigger_state"] == "BOT_BLOCKED"`. That already excludes `LINK_EXPIRED`.

4. **`run_scrape_meteorite` in `src/core/meteorite.py`**

   - Missing-link arm (no `http://` / `https://` link): keep `state="SCRAPE_ERROR"`, `error="missing link"`, `total_errors += 1` only. Change the `_row_miss` next step from `This row is ERROR` to `This row is SCRAPE_ERROR`.
   - `page_status == "blocked"`: unchanged (`BOT_BLOCKED`, `total_failed` only, next step `This row is BOT_BLOCKED`, do not clear `electronic_contact`).
   - `page_status == "ok"` and non-empty stripped text: unchanged (`READY`, `total_passed`).
   - **Before** the shared soft-fail `update_meteorite`, if `page_status` is `closed` or `missing`: keep today's AST-1750 `err` build (closed-signal scan, `text_len`, `final_url`; `missing` keeps `signal=None`) and the ungated `logger.debug` of full `visible_text`. Then `update_meteorite(row_id, state=status_map[page_status], error=err)`, `_row_miss(row_id, cid, err, "This row is LINK_EXPIRED")`, `summary["total_failed"] += 1`, `continue`. Do not increment `total_errors`.
   - Any remaining soft-fail fall-through (not closed/missing): keep `state=status_map.get(page_status, "SCRAPE_ERROR")` and `total_errors += 1`. Next step is `f"This row is {state}"`, not `This row is ERROR`. Do not send this arm to `LINK_EXPIRED`. (`_classify_jd("")` is `missing`, so this fall-through is not the closed/missing UAT path.)
   - `except Exception`: unchanged — `logger.exception` with candidate, row id, exception type/message, and `Continuing to the next row`; `total_errors += 1` only. Do not add `_row_miss`. Do not call `logger.error` for a non-throw.
   - Docstring: `SCRAPE_LINK → READY | BOT_BLOCKED | LINK_EXPIRED | SCRAPE_ERROR`.

5. **Other soft `SCRAPE_ERROR` warnings** — where `_row_miss` is called with next step exactly `This row is ERROR` and the row is written `SCRAPE_ERROR`, change only that string to `This row is SCRAPE_ERROR`. Do not change those states or counters:

   - `run_stage_meteorite`: missing classify_outcome, skip outcome on row, missing link, missing content, missing breadcrumb link, unhandled classify_outcome.
   - `run_land_meteorite`: missing content (non-empty `BOT_BLOCKED` skip stays), land-failed `error` arm.

   Leave `This row is BOT_BLOCKED`, `This row is ABANDONED`, and `This row is staying BOT_BLOCKED` as they are. Do not switch any of these `logger.warning` calls to `logger.error` (`stat.logging.error`: soft-fail with no throw is warning; error level is `logger.exception` on a throw).

### Blast radius

- Closed/missing batches that AST-1751 made `fail:0 error:N` become `fail:N error:0`. Genuine `SCRAPE_ERROR` and exception arms stay `total_errors` only.
- AST-1750's `signal=` / `text_len=` / `final_url=` why-string and Telescope debug dump stay. Operators will see `LINK_EXPIRED` instead of `This row is ERROR` on that warning.
- `meteorite_bot_blocked_notify` does not claim `LINK_EXPIRED` (trigger stays `BOT_BLOCKED`). `SCRAPE_LINK` retry priors stay `NEW` and `SCRAPE_ERROR` only, so an expired link is not scraped again. `ABANDONED` does not list `LINK_EXPIRED`.
- Stage/land warning next steps that said `This row is ERROR` will say `This row is SCRAPE_ERROR`. Counters on those arms do not move.
- Tests or bible rows that expect `closed`/`missing` → `SCRAPE_ERROR`, the phrase `This row is ERROR`, or `fail:0` on a closed batch will fail. Betty owns `tests/` and `docs/test-bible/**`. This ticket does not edit them.
- Dispatcher summary stays four ints: `total_processed`, `total_passed`, `total_failed`, `total_errors`.

### What must still hold

- AST-1751: `SCRAPE_ERROR` and exception arms increment `total_errors` only, never also `total_failed`. `BOT_BLOCKED` increments `total_failed` only. AST-1742 inbox `NOT_A_JOB` / skip → fail is untouched.
- AST-1750: closed/missing warning `why` and row `error` still include `signal=`, `text_len=`, and `final_url=`; `logger.debug` still logs full `visible_text`; no page HTML on the warning; no truncation and no `if debug` gate.
- `stat.logging.warning`: one per-item warning for a soft miss. `stat.logging.error`: throws stay a single `logger.exception` (facts + next step + traceback). No `logger.error` on a non-throw. No pass/fail/error rollup at error level.
- AST-1689: bot-block remains state-only (do not clear `electronic_contact`). Notify `trigger_state` stays `BOT_BLOCKED`.
- `_classify_jd` is not renamed or forked. Telescope HTTP helpers and roster/gazer import paths stay as AST-1726 left them.
- No depth or output limits.

## Radia review (AST-1752)

**Overall:** CLEAN — `[code-rubric] PROCEED` @ `37becf57`.

- **[bug-repro] OK** — closed/missing → LINK_EXPIRED, total_failed, not total_errors.
- **What must still hold — OK.**
- **§3h:** resolve-child skipped (clean review).

## Bug: AST-1849 — asyncio.run callers leak Telescope per-loop state at loop close

Orphaned-bug `fix` child of mini-parent AST-1841. Lives on this plan doc because AST-1726 introduced `_TelescopeQueue` and its per-loop `_LoopState` (Stage 2). Does not rewrite Stages 1–4 or any earlier bug block. Scope: AST-1849 `## Scope`, amended after its `[scope-gate]` to add the `contact.py` contact-task dispatch site. `dispatcher._task_thread_target` is already fixed on dev (`c86d8b5c`) and is not touched. The 2h loop stall (AST-1840) is out of scope.

### As-is

Five one-shot `asyncio.run(...)` call sites can reach Telescope. When their loop closes, that loop's `_LoopState` is still open: the asyncpg pool (`st.db`), the LISTEN connection (`st.listener`), the `telescope-result-poller` task, and any `_ping_wake` tasks in `st.wake_tasks`. `asyncio.run` cancels leftover tasks before it closes the loop, but it never closes the pool or listener. `_TelescopeQueue._state()` later drops the closed loop's entry from `_states` without closing anything (it can't, because the loop is gone). The result is `Event loop is closed` / `Task was destroyed but it is pending!` teardown noise (AST-1841 `parse_job_list` log, 12:40:33) and one leaked Telescope DB pool plus listener per request.

The five sites:

| Site | Call | Telescope reach |
|------|------|-----------------|
| `src/ui/api/api_admin.py` `admin_telescope` | `asyncio.run(admin_telescope_scrape(...))` | direct |
| `src/ui/api/api_meteorite.py` `_run_land` | `asyncio.run(land_meteorite(candidate_id, **kwargs))` | `land_meteorite` → `_land_link_check_append` / `enrich_meteorite_land_packet` → `_land_fetch_link_text` → `get_visible_text` |
| `src/ui/api/api_inbox.py` `inbox_land_meteorite` | `asyncio.run(_land_all())` | `ingest_candidate_email_message` → meteorite land path |
| `src/core/gazer.py` `ingest_meteorite_jobs_from_email_html_sync` | `asyncio.run(ingest_meteorite_jobs_from_email_html(...))` | `_meteorite_fetch_link_visible_text` → `get_visible_text` |
| `src/core/contact.py` contact-task dispatch loop | `asyncio.run(handler(cid, param, debug=debug))` | handlers `gazer.contact_task_gazer_scrape` / `meteorite.create_contact_meteorite` → `check_connectivity` → `_pool.healthy()` → `_get_db()` |

### To-be

Each of the five sites calls one sync runner in `src/external/telescope.py`, `run_one_shot(coro)`. It runs `coro` under `asyncio.run` and awaits `close_loop_resources()` in a `finally` inside that same loop, before `asyncio.run` cancels leftovers and closes it. After any of the five calls returns or raises, `_pool._states` has no entry for that loop, its pool and listener are closed, and its poller and wake tasks are cancelled. Return values and raised exceptions reach the caller unchanged. A loop that never touched Telescope is a no-op (`aclose_current_loop` returns when the loop has no state).

### Repro

No SQL seed. Fixture-level, against `src/external/telescope.py` with `asyncpg.create_pool` and `asyncpg.connect` patched to fakes whose `close()` is an `AsyncMock`:

1. **Leak (today).** `asyncio.run(coro)` where `coro` does `await telescope._pool._get_db()` (the first Telescope touch of every path above, e.g. via `check_connectivity()`). After it returns: `telescope._pool._states` still holds an entry for the now-closed loop, `st.db.close` was never awaited, and `st.poller` was cancelled only by `asyncio.run`'s leftover-task sweep.
2. **Fixed.** `telescope.run_one_shot(coro)` with the same `coro`. After it returns: `_pool._states` has no entry for that loop, the fake pool's `close` was awaited once, and the poller is `done()`.
3. **Exception path.** `coro` does `await _pool._get_db()` then raises `ValueError("x")`. `run_one_shot` re-raises the same `ValueError`, and (2)'s cleanup assertions still hold.
4. **No Telescope touch.** `run_one_shot` on a coroutine that returns `42` without touching Telescope returns `42`. `_pool._states` is unchanged and no pool is created.

Live shape: `POST /api/admin/telescope` once, then a later request that creates a new loop. Today, `_state()` silently drops the first loop's entry with its pool still open, and interpreter/GC teardown logs `Event loop is closed` / `Task was destroyed but it is pending!`. After the fix there is no leaked entry and no noise.

### Root cause

`close_loop_resources()` → `_TelescopeQueue.aclose_current_loop()` has to run on the loop that owns the state, before that loop closes. Only the dispatcher's long-lived task threads call it (`_task_thread_target`, `c86d8b5c`). The one-shot `asyncio.run` callers never do, and `asyncio.run` itself doesn't know about asyncpg pools or listeners. So nothing releases per-loop Telescope state on those loops.

### Proposed change

Files: `src/external/telescope.py`, `src/ui/api/api_admin.py`, `src/ui/api/api_meteorite.py`, `src/ui/api/api_inbox.py`, `src/core/gazer.py`, `src/core/contact.py` only. Do not edit `src/core/dispatcher.py`, `_TelescopeQueue` / `_LoopState` / `aclose_current_loop` / `close_loop_resources`, any other `asyncio.run` site, `tests/`, or `docs/test-bible/**`.

1. **`src/external/telescope.py` — new `run_one_shot`**, placed directly after `close_loop_resources()`. Add `Awaitable` to the existing `from typing import ...` line.

   ```python
   def run_one_shot(coro: Awaitable[Any]) -> Any:
       """asyncio.run for one-shot callers: releases this loop's Telescope state before the loop closes."""
       async def _main() -> Any:
           try:
               return await coro
           finally:
               # Must run on the owning loop, before asyncio.run closes it.
               await close_loop_resources()
       return asyncio.run(_main())
   ```

   Do not add a try/except or logging around `close_loop_resources()`. `aclose_current_loop` already swallows listener/pool close errors and gathers the poller with `return_exceptions=True`, so it can't mask the caller's result or exception. Do not call dispatcher's `_cancel_pending_tasks`, because `asyncio.run` already cancels and drains leftover tasks.

2. **`src/ui/api/api_admin.py` `admin_telescope`** — `data = asyncio.run(admin_telescope_scrape(...))` → `data = run_one_shot(admin_telescope_scrape(...))`, same arguments. Import: extend line 29 to `from src.external.telescope import PlaywrightInfraError, admin_telescope_scrape, run_one_shot`. Keep `import asyncio` because the workbench `asyncio.run` at `:1679` stays, out of scope.

3. **`src/ui/api/api_meteorite.py` `_run_land`** — `result = asyncio.run(land_meteorite(candidate_id, **kwargs))` → `result = run_one_shot(land_meteorite(candidate_id, **kwargs))`. Add `from src.external.telescope import run_one_shot` next to the `src.core.meteorite` import. Remove `import asyncio` (this was its only use).

4. **`src/ui/api/api_inbox.py` `inbox_land_meteorite`** — `result = asyncio.run(_land_all())` → `result = run_one_shot(_land_all())`. Add `from src.external.telescope import run_one_shot` with the other `src.*` imports. Remove `import asyncio` (this was its only use).

5. **`src/core/gazer.py` `ingest_meteorite_jobs_from_email_html_sync`** — `return asyncio.run(ingest_meteorite_jobs_from_email_html(...))` → `return run_one_shot(ingest_meteorite_jobs_from_email_html(...))`. Add `run_one_shot` to the existing `from src.external.telescope import (...)` block. Docstring: `"""Sync wrapper for Flask/inbox callers (run_one_shot)."""`. Keep `import asyncio` (other uses remain).

6. **`src/core/contact.py` contact-task dispatch loop** — only the `asyncio.iscoroutinefunction(handler)` branch: `raw_result = asyncio.run(handler(cid, param, debug=debug))` → `raw_result = run_one_shot(handler(cid, param, debug=debug))`. The sync-handler `else` branch is unchanged. Add a module-top `from src.external.telescope import run_one_shot` (telescope imports only `src.utils.*`, so there's no cycle). Keep `import asyncio`. Leave the `:572` `stage_meteorite` call and the `:1153` / `:1202` `do_task` `asyncio.run` calls as they are.

### Blast radius

- Every request through the five sites now closes its Telescope pool/listener before returning. That adds one `pool.close()` round-trip per Telescope-touching request and removes the per-request leak. Paths that never touch Telescope (e.g. `land_meteorite` with text only, non-scrape contact tasks) pay nothing.
- Each request still gets a fresh pool, the same as today. No cross-request pooling is introduced.
- `api_meteorite.py` / `api_inbox.py` drop `import asyncio`. No `tests/` file patches `asyncio.run` in any of the five modules (checked at plan time), so no existing mock target moves. Tests that mock `asyncpg.create_pool` on these paths will now also see `close()` awaited. Betty owns `tests/` and `docs/test-bible/**`, and this ticket does not edit them.
- `dispatcher._task_thread_target` teardown is unchanged, and the long-lived dispatch loops are unaffected.
- Out-of-scope `asyncio.run` sites (`candidate.py`, `contact.py:572/1153/1202`, `intake.py`, `api_intake.py`, `api_admin.py:1679`) keep bare `asyncio.run`. None of them reaches Telescope (verified at plan time).

### What must still hold

- AST-1726 Stage 2: state stays per event loop. asyncpg connections, Events, and Futures never cross loops, and `_state()` still forgets closed loops as a fallback.
- `c86d8b5c`: `dispatcher._task_thread_target` still runs `close_loop_resources()` → `_cancel_pending_tasks` → `loop.close()`, unchanged.
- Each of the five sites returns the same value and raises the same exception types as before. HTTP handlers keep their `ValueError` → 400, `PlaywrightInfraError` → 502, and other → 502/`telescope_error` mappings. The contact loop's per-task `try/except` behavior is unchanged.
- The AST-1728 admin Telescope workbench response shape is unchanged.
- No depth, output, or timeout limits added. No new logging.



### Joan fix-board — AST-1849

**Joan fix-board (AST-1849)** — Read the `## Bug: AST-1849` plan-fix patch on `origin/sub/AST-1841/AST-1849-asyncio-run-telescope-loop-teardown` and overlapped roster rows via `canon/docs/DIRECTIVES-DIRECTORY.md` / harvested statutes (no `docs/canon-index.md` on this ref). The change adds `run_one_shot` beside existing `close_loop_resources()` and routes five known Telescope-touching `asyncio.run` call sites through it; it does not alter `_TelescopeQueue` / `aclose_current_loop` semantics and explicitly preserves AST-1726 per-loop state and dispatcher `c86d8b5c` teardown. That matches the existing `aclose_current_loop` docstring (“before the loop closes”) and layer rules (`astral.layers.import-direction`, `astral.layers.core-vs-external-bright-line`); no in-force statute or pattern text contradicts the wrapper or requires a carve-out. Pending `patt.external.web-scraping-via-telescope` remains id-only (AST-1726 planner note). No F3 canon landing indicated.

BEGIN-VERDICT
```
[board-joan]  CANON: OK
```
END-VERDICT

```text
AST-1849 board-joan done — CANON: OK.
```


### Radia review — AST-1849

**Diff reviewed:** `origin/ftr/AST-1841-asyncio-run-telescope-loop-teardown...origin/sub/AST-1841/AST-1849-asyncio-run-telescope-loop-teardown` — commits through `bf470756` (plan-fix, Joan board, product); product delta `src/external/telescope.py`, `src/ui/api/api_admin.py`, `api_meteorite.py`, `api_inbox.py`, `src/core/gazer.py`, `src/core/contact.py` (+ plan-fix doc block, unrelated doc carry below).

## Canon scores

*(Frozen Canon Scope on Linear description: **none** — same as sibling orphaned fixes; no directive ids to score. Joan fix-board overlap skim in issue doc records `[board-joan] CANON: OK` including `astral.layers.import-direction` / `astral.layers.core-vs-external-bright-line`. Off-list statutes not graded per §5.3.)*

| (no frozen ids) | — | — | — |

## Column diff vs plan stage

`no plan-stage scores attached` (Joan **fix-board** `[board-joan] CANON: OK` only; no `validate-plan` fix-mode score table for AST-1849).

## Frame diff

- [ ] **Description · What this implements:** still says “four confirmed … call sites” while Component/Technical scope and plan-fix list **five** (post `[scope-gate]` `contact.py`). Tick after aligning Linear text to five sites.

## Fix-specific checks

**`[bug-repro]`** — **not applicable — board REVISE owned by sibling AST-1850.** Betty `[board-betty] TESTS: REVISE` on AST-1849; repro nodes and `[bug-repro]` live on **AST-1850** per issue doc and spawn prompt. No `[bug-repro]` on this tip — expected, not fix-now.

**`## What must still hold`** — **OK**

| Item | Verdict |
|------|---------|
| AST-1726 Stage 2: per-loop state; no cross-loop asyncpg/Events/Futures; `_state()` forgets closed loops as fallback | OK — `_TelescopeQueue` / `aclose_current_loop` untouched; `run_one_shot` only calls existing `close_loop_resources()` on the owning loop before `asyncio.run` exits |
| `c86d8b5c`: `dispatcher._task_thread_target` teardown unchanged | OK — zero diff on `src/core/dispatcher.py`; sub tip still `close_loop_resources()` → `_cancel_pending_tasks` → `loop.close()` |
| Five sites: same return values and exception types; HTTP mappings unchanged; contact per-task `try/except` unchanged | OK — thin `asyncio.run` → `run_one_shot` swap; handlers/wrappers unchanged; `run_one_shot` re-raises after `finally` |
| AST-1728 admin Telescope **response shape** unchanged | OK — only execution wrapper in `admin_telescope()`; workbench `asyncio.run` at ~1679 untouched |
| No new depth/output/timeout limits; no new logging | OK — diff adds no limits or log lines |

## Findings

**fix-now:** (none)

**discuss:** (none)

**advisory:**

- **Sibling test gap:** AST-1850 owns Betty’s REVISE manifest (`run_one_shot` / Repro 1–4); this tip is product-only by design — merge order per plan (tests red on ftr until AST-1849 lands).
- **Stray doc carry:** commit `3998536e` appends **AST-1845** epic-registry **Threads** to `docs/features/roster/ast-891-parse-job-list-browser-and-batch.md` — unrelated to AST-1849. Harmless to product; Chuckles may omit from dev merge narrative or strip on doc commit.
- **Linear copy drift:** “four confirmed sites” in **What this implements** vs five in scope/plan — cosmetic; frame diff above.
- **UI → external imports:** `api_inbox.py` / `api_meteorite.py` gain first `src.external.telescope` import (runner only); follows existing `api_admin` Telescope import pattern named in plan.
- **Test baseline noise:** Hedy Tests Passed comment — 28 component failures identical with fix reverted; not introduced here.

## What’s solid

- `run_one_shot` matches plan-fix verbatim (placement, `try`/`finally`, no extra logging, no `_cancel_pending_tasks`).
- All **five** binding sites switched; `contact.py` only the `iscoroutinefunction(handler)` branch; `:572` / `:1153` / `:1202` `asyncio.run` left bare.
- Plan fidelity to **To-be** and **Proposed change** (six files, dispatcher/queue internals out) satisfied on the product diff.
- Estimate **2** footprint still fits (wrapper + five call-site swaps).

## Recommended actions (Chuckles)

| Gate | Parent shape | Next action |
|------|----------------|-------------|
| **PROCEED** (C7 complete) | **Orphaned mini-parent AST-1841** (spawn: finish-up-style **`origin/dev`**, not `merge-child`/`prep-uat`) | **Review Posted** → clean-review shortcut → **User Testing** (`resolve-child` skipped). When Susan accepts UT, merge **`sub/AST-1841/AST-1849-…`** straight to **`origin/dev`** (single bug), not via parent UAT rollup. |

context_tokens≈0
```

**Docs-acceptance (AST-1849):** no test-tree delivery on this tip. Betty's [board-betty] TESTS: REVISE is owned by sibling gap AST-1850.

## Bug: AST-1850 — tests for one-shot Telescope loop teardown runner

Test-gap sibling of AST-1849 under mini-parent AST-1841. It answers AST-1849's `[board-betty] TESTS: REVISE`. Tests and bible only: Betty lands them at qa-fix, and product code stays on AST-1849 (`run_one_shot` in `src/external/telescope.py`, `bf470756`). Case numbers below refer to the `## Bug: AST-1849` block's `### Repro` list in this doc. Does not rewrite Stages 1–4 or any other bug block.

### As-is

No test references `close_loop_resources`, `aclose_current_loop`, `_LoopState`, `_pool._states`, or `run_one_shot`. AST-1849's Repro cases 1–4 have no node, so a regression back to a bare `asyncio.run` (or a runner that stops awaiting `close_loop_resources`) would pass the suite. `docs/test-bible/external/telescope.md` has no loop-teardown entry.

### To-be

`tests/component/external/test_telescope.py` gains one class, `TestAst1849OneShotLoopTeardown`, with four nodes that cover AST-1849 Repro cases 1–4. The `[bug-repro]` node is red against the pre-fix product and green on `bf470756`. `docs/test-bible/external/telescope.md` gains an `AST-1849 · AST-1850` section mapping those nodes.

### Repro

Red/green proof, prototyped at plan time from a scratch copy outside the repo, with the real `tests/conftest.py` chain and the fixture below:

- On `bf470756` (AST-1849 fix): all 4 nodes pass.
- On pre-fix `3998536e` (this sub's base, which is `origin/dev` = `origin/ftr/AST-1841-…` product): nodes 1–3 fail with `AttributeError: module 'src.external.telescope' has no attribute 'run_one_shot'`, and node 4 (control) passes.

### Root cause

AST-1726's per-loop queue (Stage 2) shipped without teardown coverage, and AST-1849 added `run_one_shot` with no node. `TestTelescopePoolHttp` exercises the retired HTTP `_TelescopePool`, not `_TelescopeQueue`.

### Proposed change

Files: `tests/component/external/test_telescope.py`, `docs/test-bible/external/telescope.md` only. No product code, no other test file.

1. **`tests/component/external/test_telescope.py` — new class `TestAst1849OneShotLoopTeardown`**, appended after `TestAst1750PostTelescopeDebugDump` with a `# Branches:` header comment matching the file's style: `# Branches: run_one_shot releases per-loop Telescope state (AST-1849 / AST-1850).` Add `import asyncio` to the file's imports. Nodes are plain `def` (not `async def` / `@pytest.mark.asyncio`), because `asyncio.run` cannot start inside a running loop.

   **Fixture** (class-local `@pytest.fixture` named `fresh_queue`, returns `(q, fake_db, create_pool)`):
   - `monkeypatch.setenv(pw_mod.TELESCOPE_CONFIG["database_url_env"], "postgresql://fake/db")` so `_dsn()` passes.
   - `q = pw_mod._TelescopeQueue()` and `monkeypatch.setattr(pw_mod, "_pool", q)`. `close_loop_resources` reads module-global `_pool` at call time, so it sees `q`.
   - `fake_db = MagicMock()`, `fake_db.close = AsyncMock()`, `fake_db.fetch = AsyncMock(return_value=[])`.
   - `create_pool = AsyncMock(return_value=fake_db)` and `monkeypatch.setattr(pw_mod.asyncpg, "create_pool", create_pool)`.

   **Shared coroutine** (class-local helper `_touch(q, seen)` returning an `async def`): `await q._get_db()` (starts the real `telescope-result-poller`). Then record `loop = asyncio.get_running_loop()` and `st = q._states[loop]`. Attach a fake listener `st.listener = MagicMock(is_closed=MagicMock(return_value=False), close=AsyncMock())`. Store `loop`, `st`, `listener` in `seen` and return `"ok"`.

   **Shared release asserts** (helper `_assert_released(q, fake_db, seen)`):
   - `seen["st"].db is fake_db`: state really existed, so the green isn't vacuous.
   - `seen["loop"] not in q._states` and `q._states == {}`.
   - `fake_db.close.await_count == 1` and `seen["listener"].close.await_count == 1`.
   - `seen["st"].poller.done()`.
   - `seen["loop"].is_closed()`.

   **Nodes:**

   | Node | AST-1849 Repro | Body | Pre-fix | `bf470756` |
   |------|----------------|------|---------|------------|
   | `test_run_one_shot_releases_loop_state` (**bug-repro**) | 2 (+1 via red) | `assert pw_mod.run_one_shot(_touch(q, seen)()) == "ok"`, then `_assert_released` | red (`AttributeError`) | green |
   | `test_run_one_shot_reraises_and_still_releases` | 3 | `async def _boom(): await touch(); raise ValueError("boom")`; `with pytest.raises(ValueError, match="boom"): pw_mod.run_one_shot(_boom())`, then `_assert_released` | red | green |
   | `test_run_one_shot_passthrough_without_telescope` | 4 | `async def _plain(): return 42`; `assert pw_mod.run_one_shot(_plain()) == 42`; `assert q._states == {}`; `create_pool.assert_not_awaited()` | red | green |
   | `test_bare_asyncio_run_leaves_loop_state_control` | 1 | `asyncio.run(_touch(q, seen)())`; `assert seen["loop"] in q._states`; `assert fake_db.close.await_count == 0` | green | green |

   Node 4 is a control, not a bug-repro. It proves the fixture creates the exact state a bare `asyncio.run` leaves behind, which is AST-1849's as-is. Its docstring must say so: `"""Control: bare asyncio.run leaves per-loop Telescope state open (AST-1849 as-is); proves the fixture is not vacuous."""`. No `time.sleep`, wall-clock asserts, or timeouts.

2. **`docs/test-bible/external/telescope.md` — new section** appended after the AST-1840 · AST-1844 section, same shape as that section:

   ~~~markdown
   ---

   ### AST-1849 · AST-1850 (qa-fix bug-repro — one-shot loop teardown)

   **Board REVISE:** no test referenced `close_loop_resources` / `aclose_current_loop` / `_LoopState` / `_pool._states`; one-shot `asyncio.run` callers leaked the per-loop asyncpg pool, LISTEN connection and `telescope-result-poller`. Product: **AST-1849** (`run_one_shot`); tests on gap sibling **AST-1850**. `[bug-repro]` node red on pre-fix `3998536e` (`AttributeError`: no `run_one_shot`), green on AST-1849 (`bf470756`).

   | Area | Component tests |
   | --- | --- |
   | `run_one_shot` releases loop state (pool + listener closed once, poller done, `_states` empty) | `test_telescope.py::TestAst1849OneShotLoopTeardown::test_run_one_shot_releases_loop_state` (**bug-repro**) |
   | Exception re-raised unchanged, cleanup still done | `test_telescope.py::TestAst1849OneShotLoopTeardown::test_run_one_shot_reraises_and_still_releases` |
   | No Telescope touch → value returned, no pool, `_states` unchanged | `test_telescope.py::TestAst1849OneShotLoopTeardown::test_run_one_shot_passthrough_without_telescope` |
   | Control: bare `asyncio.run` leaves loop state open | `test_telescope.py::TestAst1849OneShotLoopTeardown::test_bare_asyncio_run_leaves_loop_state_control` |

   **Broken / obsolete:** none. Call-site swaps (`api_admin`, `api_meteorite`, `api_inbox`, `gazer`, `contact`) need no new nodes; no test patches `asyncio.run` on those modules.

   ```bash
   ./scripts/testing/run_component_tests.sh \
     tests/component/external/test_telescope.py::TestAst1849OneShotLoopTeardown -q
   ```
   ~~~

### Blast radius

- Test tree and bible only. No product file changes, and no existing node is edited.
- The nodes monkeypatch `pw_mod._pool` and `asyncpg.create_pool` via `monkeypatch`, which restores them after each node, so other telescope nodes are unaffected.
- **Merge order:** AST-1850's own sub has no `run_one_shot` (the base is pre-fix). Nodes 1–3 stay red on `origin/sub/AST-1841/AST-1850-…` until AST-1849 merges into `origin/ftr/AST-1841-…`, so AST-1850 test-fix runs after that merge. The red/green gate is red on the current ftr base, green on `bf470756` / post-merge ftr.
- Four pre-existing `test_telescope.py` failures (`TestTelescopePoolHttp` ×3 and `TestAst1750PostTelescopeDebugDump`) target the retired `_TelescopePool` / `_pool.request` and also fail on `origin/dev`. They are out of this gap's scope, noted and not fixed here.
- `LOCKED_AT_100` for `telescope.py`: this gap adds coverage of `run_one_shot` and `aclose_current_loop`. It does not make the branch lock whole (the bible's pass criterion is manifest-green, not the lock gate).

### What must still hold

- AST-1849 `### What must still hold`: nodes assert return value and exception pass-through unchanged, and a no-op on loops that never touched Telescope.
- AST-1726 Stage 2: per-loop state. The fixture uses a fresh `_TelescopeQueue` per node and never shares a loop or Future across nodes.
- Engineers don't edit `tests/` or `docs/test-bible/**`. Betty lands both at qa-fix.
- No depth, output, or timing limits in the nodes.



### Joan fix-board — AST-1850

**Findings (Joan fix-board, AST-1850)**

Read `## Bug: AST-1850` on `origin/sub/AST-1841/AST-1850-asyncio-run-telescope-loop-teardown-tests`. Scope is **tests + bible only** (`test_telescope.py`, `docs/test-bible/external/telescope.md`); product stays on AST-1849 (`run_one_shot` @ `bf470756`). Overlap triage via `canon/docs/DIRECTIVES-DIRECTORY.md` / harvested statutes (no `docs/canon-index.md` on ref)—same resolution as AST-1849 and gap siblings like AST-1848.

The plan adds four component nodes that lock AST-1849 Repro 1–4 (including `[bug-repro]` on `run_one_shot` teardown) and a bible block pointing at those nodes. It does **not** amend any `canon/statutes/**`, `canon/directives/active/**`, or pattern text, and does not introduce a new product rule beyond what AST-1849 already implements. `astral.layers.*` and pending `patt.external.web-scraping-via-telescope` are unchanged; monkeypatching `_pool` / `asyncpg.create_pool` is test-tree practice, not a corpus edit. `orch.roles.betty-owns-test-tree` / engineer test-tree ban are satisfied by Betty-only landing.

**Verdict:** no in-force statute or pattern needs an update or carve-out; F3 (`validate-plan` fix mode) not indicated.

`[board-joan]  CANON: OK`


### Radia review — AST-1850

**Diff scope check:** three-dot diff touches **only**  
`tests/component/external/test_telescope.py`,  
`docs/test-bible/external/telescope.md`,  
`docs/features/foundation/ast-1726-platform-telescope-py-drop-in-playwright-decommission.md` (AST-1850 plan-fix block). **Zero bytes under `src/**`.** Tip commit `code(AST-1850): no product src — test gap; product fix AST-1849 on tip via ftr` is a publish marker, not a product delta.

---

```
[code-rubric]
**Ticket:** AST-1850
**Publish ref:** `06d68e26` (`origin/sub/AST-1841/AST-1850-asyncio-run-telescope-loop-teardown-tests`)
**Corpus:** `bd68954dc854ca80fca1fc391821dff9ff288a7a` (tree `canon/` at publish tip; no `docs/canon-index.md` on this ref)
**Overall:** CLEAN

**Diff reviewed:** `origin/ftr/AST-1841-asyncio-run-telescope-loop-teardown...origin/sub/AST-1841/AST-1850-asyncio-run-telescope-loop-teardown-tests` — plan-fix + Joan board + qa-fix test/bible + merge-tests/sync/marker commits; **net delta:** 211 lines across the three paths above only. Sub stacked on ftr with AST-1849 (`run_one_shot`) already merged.

## Canon scores

*(Frozen Canon Scope on Linear description: **none** — gap test sibling pattern (cf. AST-1848). Joan fix-board `[board-joan] CANON: OK` for tests/bible-only; Betty post-qa `[board-betty] TESTS: OK`. Off-list statutes not graded per §5.3.)*

| (no frozen ids) | — | — | — |

## Column diff vs plan stage

`no plan-stage scores attached` (fix-board Joan + Betty only; no `validate-plan` fix-mode score table).

## Frame diff

(none)

## Fix-specific checks

**`[bug-repro]`** — **OK**

Primary repro: `TestAst1849OneShotLoopTeardown::test_run_one_shot_releases_loop_state` (docstring opens with `[bug-repro]`; Betty’s Linear `[bug-repro]` @ `41a1c634` names this node).

- **Not tautological:** asserts AST-1849 **To-be** teardown — return `"ok"`, then `_assert_released`: `seen["st"].db is fake_db`, `seen["loop"] not in q._states` and `q._states == {}`, `fake_db.close.await_count == 1`, `seen["listener"].close.await_count == 1`, `seen["st"].poller.done()`, `seen["loop"].is_closed()`. These are concrete post-conditions, not “no exception.”
- **Repro-first plausible:** pre-fix product @ `83a0c352` (ftr before AST-1849 merge) → nodes 1–3 fail `AttributeError: no run_one_shot`; control green (Hedy attestation @ tip). On ftr `0877d286` all four green — matches plan **Repro** / qa-fix contract.
- **Would catch a fake-green runner:** a `run_one_shot` that only `asyncio.run(coro)` without awaiting `close_loop_resources()` would still fail `_assert_released` (open `_states`, `close` not awaited, poller not `done()`). Betty board reached the same conclusion; control node `test_bare_asyncio_run_leaves_loop_state_control` pins the as-is leak shape (`loop in q._states`, `fake_db.close.await_count == 0`) so green on the bug-repro is not vacuous setup.

**Companion nodes (plan Repro 3–4 + control 1):**

| Node | Verdict |
|------|---------|
| `test_run_one_shot_reraises_and_still_releases` | OK — `pytest.raises(ValueError, match="boom")` then same `_assert_released` |
| `test_run_one_shot_passthrough_without_telescope` | OK — `== 42`, `q._states == {}`, `create_pool.assert_not_awaited()` |
| `test_bare_asyncio_run_leaves_loop_state_control` | OK — required docstring; proves fixture models AST-1849 as-is |

**`## What must still hold` (AST-1850 plan-fix + AST-1849 cross-refs)** — **OK**

| Item | Verdict |
|------|---------|
| AST-1849: return/exception pass-through unchanged | OK — nodes 1–3 |
| No-op when loop never touches Telescope | OK — passthrough node |
| AST-1726 per-loop isolation in tests | OK — class `fresh_queue` fixture; new `_TelescopeQueue` per node; plain `def` + outer `asyncio.run` / `run_one_shot` |
| No timing/wall-clock asserts | OK |
| Plan files only (`test_telescope.py`, `telescope.md`) | OK — no other test file edits in diff |

## Findings

**fix-now:** (none)

**discuss:** (none)

**advisory:**

- **Known residual (documented):** bible + Betty **TESTS: OK** — reverting a **call site** to bare `asyncio.run` would not fail this class; plan and bible state that explicitly. Product decision already flagged for Susan; not a blocker for this gap ticket.
- **`[bug-repro]` tag shape:** tag lives in the test **docstring** first line, not a `# [bug-repro]` comment (same minor convention drift as AST-1848); Betty thread + bible manifest still key the node — not fix-now.
- **Betty qa-fix ops:** `[bug-repro]` comment notes `origin/tests-clean-base` missing, cherry-pick to `origin/tests` @ `b3c7f256`, and **marker still needs restoring** — Chuckles/process, not a defect in the published sub diff vs ftr.
- **Pre-existing suite noise:** four failing `test_telescope.py` nodes (`TestTelescopePoolHttp` ×3, `TestAst1750PostTelescopeDebugDump`) on retired `_TelescopePool`; Hedy documented identical on `origin/dev` — out of gap scope per plan **Blast radius**.

## What’s solid

- Strict gap-child footprint: tests + test-bible + plan-fix doc only; no product smuggle.
- Implementation matches plan-fix **Proposed change** (fixture, `_touch`, `_assert_released`, four nodes, bible section + manifest command).
- Repro class would go red if `run_one_shot` existed but skipped `close_loop_resources`, not only on missing symbol.
- ftr now carries AST-1849; engineer red→green gate (`83a0c352` → tip on ftr) satisfied per thread.

## Recommended actions (Chuckles)

| Gate | Parent shape | Next action |
|------|----------------|-------------|
| **PROCEED** (C7 complete) | **Orphaned mini-parent AST-1841** | **Review Posted** → clean-review shortcut → **User Testing** (`resolve-child` skipped). After UT: merge gap sub into **`origin/ftr/AST-1841-…`** (tests green on ftr without scratch overlay), then finish-up-style **`origin/dev`** for the orphaned mini-parent per fix-lane §8 — not `prep-uat` rollup. Restore **`origin/tests`** marker per Betty if still open. |

context_tokens≈0
```

## Threads (generated — epic_registry mirror)

_(generated from epic registry — do not hand-edit; edits are overwritten)_

### Team

| Agent | Role | Thread |
|--------|-------|--------|
| Hedy | engineer | `/home/susan/.cursor/chats/470bcda677679f613fe0681dc1fbdda1/730ab1c2-eb2e-4750-81a2-264acd3db387/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/b4c452ea-b55d-4951-8bdf-19484427361c/store.db` |
| Radia | review | `/home/susan/.cursor/chats/470bcda677679f613fe0681dc1fbdda1/d490759b-7e7d-4554-99d9-972eb9e0fee3/store.db` |

### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-1841 (parent) | ftr/AST-1841-asyncio-run-telescope-loop-teardown |
| AST-1849 | sub/AST-1841/AST-1849-asyncio-run-telescope-loop-teardown |
| AST-1850 | sub/AST-1841/AST-1850-asyncio-run-telescope-loop-teardown-tests |

**Epic worktree:** `astral-AST-1841/` — one active sub checked out at a time.
