# AST-1721 — Astral Telescope — stateless headless-scraping microservice (per-URL)

<!-- linear-archive: AST-1721 archived 2026-10-02 -->

## Linear archive (AST-1721)

**Archived:** 2026-10-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1721/astral-telescope-stateless-headless-scraping-microservice-per-url  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** High / 8  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Firefox and the platform share one Railway process today, so a browser OOM kills orchestration, DB pools, and business logic with it. Astral Telescope isolates headless rendering into a dumb, horizontally scalable, domain-agnostic microservice: give it a URL, get back text/links or HTML. The platform keeps crawl orchestration, parse, vendor, and entity logic; scraping capacity scales (and fails) independently of the stateful tier.

**Surfer adjacency (design lock, not Surfer build):** Astral Surfer will later scrape via a browser extension (human-authenticated sessions). Post-render helpers — "that's what the page rendered, now what?" (HTML delimiter splits, cull, visible-text-from-HTML, link extraction from HTML, and similar) — must live in `src/external/telescope.py` (or other `src/` modules) so headless Telescope and Surfer share one processing path. That keeps the extension thin and keeps web-content processing source-agnostic.

## Functional scope

 1. **Per-URL Telescope service** — A monorepo service under `service/telescope/` that accepts one URL per request, navigates with Firefox, and returns page artifacts. No company/entity/job awareness, no database, no job queue, no webhook/poll loop. Telescope logging is **console only** (no `app_log` / `astral.db` inserts — there is no DB on Telescope). Service owns **browser interaction** only (navigate, cookie dismiss, expand/load-all, wait_ready, capture rendered DOM/text/links).
 2. **Shared post-render processing on the platform** — Helpers that operate on already-rendered HTML/text (cull, delimiter splits, extract-from-HTML, normalize, vendor fingerprint from artifacts, and other former `playwright.py` non-browser utilities) live in `src/external/telescope.py` so Surfer and headless callers reuse them. They are **not** implemented only inside `service/telescope/` (service cannot import `src/`, and duplicating them would fork Surfer).
 3. **Text endpoint (links optional)** — `POST /telescope` returns `final_url` and text (or an array of text blobs when the selector matches multiple nodes). Request flag `links` defaults **true** and may be set **false** to return visible text only (omit or empty `links` in the response when false). Cookie dismissal always runs. `expand` defaults **on** (load-all scroll / Load More). `wait_ready` defaults **off** (opt-in generic content-stability wait only — no careers listing selectors on the service). Platform `telescope.py` may further process returned text/links via shared helpers when callers need it.
 4. **HTML endpoint** — `POST /telescope/html` returns `final_url` and rendered scoped-element HTML from the browser. Same expand/wait_ready semantics on the service. `cull` **defaults on in the platform drop-in API** (applied in `src/external/telescope.py` via the shared helper), not as a service-only fork. Callers that need text and HTML use separate calls (confirmed — no single-load dual payload required this epic).
 5. **Live health check** — `GET /healthz` actually launches or pokes a browser; a process-up 200 alone is not healthy.
 6. **One Firefox per Telescope replica** — Each Telescope **replica** (one Docker/Railway container running one Telescope process) launches **exactly one** Firefox browser in FastAPI lifespan and reuses it. Every request opens a **fresh browser context** (isolated cookies/storage), always closed in `finally` — never reuse a context across URLs. A process-local semaphore caps concurrent pages to what that replica's RAM holds; each request has a hard timeout; after N requests the single browser is recycled (`recover`) to fight Firefox memory creep.
    *Why not the alternatives:* (a) **new browser per request** — launch cost dominates latency and churns RAM; (b) **many browsers per replica** — multiplies Firefox RSS and recreates today's OOM; (c) **shared context across URLs** — cookie/session bleed and unreliable cleanup. One browser + fresh contexts is the durability/performance tradeoff that keeps a hard memory ceiling without paying full launch cost every URL.
 7. **Private auth** — Telescope is reachable only on Railway private networking (and locally only via its own host/port — never co-hosted with the platform process). Auth is an **environment-specific bearer token** from env vars on Telescope and the platform client — **not** candidate/Stytch/user auth.
 8. **Drop-in platform client; decommission [playwright.py](<http://playwright.py>)** — All headless browser I/O runs on Telescope. New `src/external/telescope.py` is the **full port** of today's `playwright.py` public surface: same function names and parameter lists for every symbol core already imports — calling components change **only** the import module path (`playwright` → `telescope`); no reworked call-site logic. Scrape-backed entrypoints call the Telescope pool over HTTP (round-robin, then least-in-flight; retry same URL on another node on timeout/failure), then apply shared post-render helpers locally. `src/external/playwright.py` is **deleted**. No sibling `page_parse.py`. No new platform code may re-introduce in-process headless Playwright; further **browser** scrape capability is added in the Telescope service; further **post-render** capability is added in `src/external/telescope.py` (Surfer-ready).
 9. **True process isolation** — Platform talks to Telescope **only over HTTP to a separate host/IP (or separate local port/process)**. Not an in-process import, not "call a function from another directory on the same host." Telescope never runs in the same OS process or same Railway/local server instance as the platform — including local dev (second process/container required). `service/*` and `src/` **never import in either direction** (CI-enforced; law lives on the import-rules statute amendment below, not a new pattern).
10. **Telescope admin operator page** — An admin-authenticated platform screen to exercise Telescope: URL input, response type (html vs text), toggles for each optional Telescope request parameter, and a display of the raw response including string content plus scrape metadata (bot-block, cookies, or other issues that prevented a clean scrape). Platform admin API proxies to Telescope with the env bearer (candidate/Stytch auth on the admin route only). Contract may extend service and/or `src/external/telescope.py` responses with that metadata beyond today's `final_url` + text|html|links.
11. **Explicit non-goals** — No Phase 2 batch-aware autoscaler / Judoscale. No separate Telescope git repo. No Redis/job system. No returning `request_urls` / `frame_urls` / vendor signals from the service (metadata for scrape health/bot-block/cookies for the admin surface is in-scope under #10). No depth/output limits or perf shortcuts without Susan sign-off. No mirroring the full platform into N browser boxes. No Telescope writes to `app_log` / `astral.db`. No split of former `playwright.py` into a second platform module. **No Surfer extension build in this epic** — only the shared-helper placement that Surfer will need.

## Component scope

* `service/telescope/` — **new** — FastAPI app package: lifespan browser session, `/telescope`, `/telescope/html`, `/healthz`, browser-interaction helpers only (navigate / capture / load-all / cookie-dismiss / readiness); console-only logging; no fork of post-render cull/split helpers that Surfer must share.
* `service/telescope/requirements.txt` — **new** — Telescope-only deps (Playwright pin matching the image, FastAPI, uvicorn, etc.).
* `service/telescope/Dockerfile` — **new** — Official Playwright Python image, Firefox, single uvicorn worker, non-root, `--init`, memory/`/dev/shm` sizing.
* `service/telescope/railway.toml` (or equivalent Railway service config colocated with the service) — **new** — subdirectory deploy for the Telescope service.
* `src/external/telescope.py` — **new** — full drop-in replacement for `playwright.py`: same public names/params; HTTP client for headless scrape surfaces; **all** former non-browser / post-render helpers live in this same file (Surfer-ready shared processing); no in-process Firefox.
* `src/external/playwright.py` — **deleted** — fully decommissioned; no thin-client leftover under this name.
* `src/core/roster.py` — **modified** — import module path `playwright` → `telescope` only; no call-site shape changes.
* `src/core/gazer.py` — **modified** — same import-path-only rewire.
* `src/core/meteorite.py` — **modified** — same import-path-only rewire; also allow scrape-batch counter classification so genuine technical ERROR / `SCRAPE_ERROR` paths increment `total_errors` only (not also `total_failed`) (AST-1751; complements AST-1742 inbox path). **Exception (AST-1752):** content verdicts `closed` / `missing` are not technical faults — write new terminal state `LINK_EXPIRED` and increment `total_failed` (not `total_errors`); not a bot-notify trigger. Soft non-throw rows stay `logger.warning`; the warning text must name the bucket (`LINK_EXPIRED` / `BOT_BLOCKED` / `SCRAPE_ERROR`) and must not say "This row is ERROR". Thrown faults stay `logger.exception`.
* `src/utils/config.py` — **modified** — Telescope base URL(s), env bearer token key, client timeout, platform in-flight pool semaphore / per-node caps, and Telescope-facing defaults that must not live as literals in callers. **Also (AST-1752):** `METEORITE_STATES` gains terminal `LINK_EXPIRED` (`prior_states: ["SCRAPE_LINK"]`); `METEORITE_INGRESS_DISPATCH_CONFIG["scrape_page_status_states"]` maps `closed` and `missing` to `LINK_EXPIRED` instead of `SCRAPE_ERROR` (allowed-values assert updated).
* `requirements.txt` — **modified** — add direct `httpx` (or confirm/pin the async HTTP client the facade uses) for the platform Telescope client; drop platform Playwright browser runtime needs once no process launches Firefox.
* `.github/workflows/` (or a tracked lint script invoked by CI) — **modified/new** — fail the build if `service/telescope/` imports from `src/` **or** `src/` imports from `service/`.
* `src/ui/frontend/` (admin Telescope page + route/nav wiring under existing admin patterns) — **new/modified** — URL, html|text, optional-parameter toggles, raw response + scrape-metadata display.
* `src/ui/api/` (admin Telescope proxy blueprint under `/api/admin/…`) — **new/modified** — admin-authenticated route that calls Telescope (via `src/external/telescope.py` / HTTP) and returns content + scrape metadata to the admin page.
* Telescope request/`id` filter + admin control — **new/modified** — optional `id` secondary filter (`id="…"`) alongside tag/selector and class.

## Technical scope

* `service/telescope/` — New FastAPI routes for `POST /telescope` (optional `links` default true), `POST /telescope/html`, `GET /healthz`; lifespan owns one Firefox per replica; per-request fresh context + RAM semaphore + `wait_for` timeout + recycle-after-N; cookie dismiss always; expand default on; wait_ready default off as generic stability/min-chars only; returns rendered capture artifacts; does **not** own Surfer-shared post-render helpers (those stay in `src/external/telescope.py`); logs to console only (no DB).
* `service/telescope/requirements.txt` — New pin set; Playwright version must match the base image browsers.
* `service/telescope/Dockerfile` — New image build for the Telescope process only.
* `service/telescope/railway.toml` — New Railway subdirectory service definition for Phase 1 fixed replicas (start at 1, then fan out), private networking, bearer secret from env.
* `src/external/telescope.py` — New single module replacing `playwright.py`: pool dispatch (round-robin → least-in-flight), retry other node on timeout/failure, bearer from env; public scrape entrypoints keep today's names and parameters, call Telescope over HTTP, then apply shared post-render helpers (cull default-on for HTML paths, delimiter splits, extract-from-HTML, etc.) locally so Surfer can reuse the same functions later.
* `src/external/playwright.py` — Delete file; purge imports repo-wide on the product tree for this epic's callers.
* `src/core/roster.py` / `gazer.py` / `meteorite.py` — Change import module to `telescope` only; leave call shapes untouched; multi-page discovery becomes repeated Telescope HTTP calls inside the drop-in helpers, not new core logic. **Exception (AST-1751):** in `meteorite.py` scrape runners (`run_scrape_meteorite` and any sibling dispatch runners that double-bump), genuine technical ERROR outcomes must not also increment fail counters. **Exception (AST-1752):** `closed` / `missing` content verdicts are fails via `LINK_EXPIRED` (`total_failed`, not `total_errors`) — alongside `BOT_BLOCKED` and `NOT_A_JOB`. `_classify_jd` stays shared; no gazer rename. Soft outcomes stay warning-level; do not log a non-throw as `logger.error`.
* `src/utils/config.py` — New/modified config keys for Telescope pool URLs, env bearer token, client timeout, and dispatch concurrency aligned to replica × per-node cap. **Also (AST-1752):** add `LINK_EXPIRED` to `METEORITE_STATES` and point `scrape_page_status_states` `closed` / `missing` at it.
* `requirements.txt` — Add/pin the platform HTTP client dependency; remove platform dependency on launching Playwright browsers once deleted.
* CI lint — Bidirectional fence: no `src`↔`service` imports either direction.
* Optional `id` filter parameter — **new** across Telescope service capture, platform client, and admin UI — select by `id="…"` like class as a secondary filter alongside tag/selector.
* `service/telescope/` and/or `src/external/telescope.py` — **modified as needed** — scrape-metadata fields on text/html responses (bot-block, cookies, other scrape failures) so the admin surface can show why a scrape was unclean; keep browser I/O on the service and post-render helpers on the platform client.
* `src/ui/frontend/` — **new/modified** — Admin Telescope page: URL, response type html|text, toggles for optional Telescope parameters, raw response pane including content + metadata.
* `src/ui/api/` — **new/modified** — Admin-auth proxy to Telescope returning the same payload the page displays; uses env bearer toward Telescope, not candidate credentials on the service.

## Architectural definition

**Patterns to reuse**

* `patt.entity.batch-processing` — platform `parse_job_list_batch` still claims/processes/releases under one batch id; only the per-URL scrape I/O moves behind HTTP to Telescope. [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.entity.batch-processing.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.entity.batch-processing.md>)
* `patt.entity.batch-criteria` — batch claim shape stays criteria-driven from dispatch_task; Telescope itself is not a claim surface. [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.entity.batch-criteria.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.entity.batch-criteria.md>)

**New patterns proposed**

* `patt.external.web-scraping-via-telescope` — all headless browser I/O goes through the Telescope service; **no new code may re-introduce in-process headless Playwright**; additional **browser** capability lands in the service; **post-render** ("page rendered, now what?") helpers land in `src/external/telescope.py` so Surfer and headless share them. Needs Archie approval before children treat it as scoring law.

**Statute change requested** (not a new pattern):

* `stat.layers.import-rules` — amend so `service/*` and `src/` **never import in either direction** (runtime is always separate host/process; CI enforces the fence). Not treated as already amended. [https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/stat.layers.import-rules.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/stat.layers.import-rules.md>)
* Related current layer file (same intent family): [https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.import-direction.md](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.import-direction.md>)

**Applicable statutes**

* `stat.logging.error` — transport and browser failures logged once at the handler with live facts (Telescope: console only). [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.error.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.error.md>)
* `stat.logging.warning` — per-item / per-node scrape warnings (Telescope: console only). [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.warning.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.warning.md>)
* `stat.logging.info` — succinct operator-readable progress on Telescope and client paths that emit info (Telescope: console only). [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.md>)
* `stat.logging.debug` — debug backstop on scrape paths that already use it (Telescope: console only). [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md>)

## Acceptance criteria

 1. **Service tree exists** — `test -d service/telescope && test -f service/telescope/Dockerfile` exits 0. Fail: Telescope lives under `src/` or has no Dockerfile.
 2. **Bidirectional import fence** — `rg -n "from src\\.|import src" service/telescope/` and `rg -n "from service\\.|import service" src/` both return no matches (CI fails on either). Fail: any cross-import either direction.
 3. **Contract endpoints** — Against a running Telescope node with valid env bearer token: `POST /telescope` with a known URL returns JSON including `final_url` and either `text` (string) or `text` (array of strings); with `links: true` (default) also `links` as `[{href, text}, …]`; with `links: false` response has no link list (or empty); `POST /telescope/html` returns `final_url` and rendered `html`; `GET /healthz` returns success only when a browser poke succeeds. Fail: 200 with empty browser poke on `/healthz`, missing fields, links always forced on, or success without auth on a token-required route.
 4. **Defaults** — Default `/telescope` request runs expand behavior without `expand: true` in the body; `wait_ready` omitted does not run the readiness poll; `links` omitted includes links; platform HTML drop-in applies cull by default via `src/external/telescope.py` (not a service-only cull fork). Fail: expand/links off by default, wait_ready on by default, or cull only exists under `service/telescope/` with no platform helper.
 5. **Multi-match text** — A selector that matches multiple nodes on a fixture page returns an **array** of text blobs, not one concatenated string. Fail: single string for multi-match.
 6. **[playwright.py](<http://playwright.py>) gone; no platform Firefox; no page_parse split** — `test ! -f src/external/playwright.py && test ! -f src/external/page_parse.py` exits 0; `rg -n "async_playwright|firefox\\.launch|BatchBrowserSession" src/` returns no matches; Firefox launch lives only under `service/telescope/`. Fail: `playwright.py` or `page_parse.py` present, or platform process still launches Firefox.
 7. **Drop-in telescope API; callers untouched in shape** — `rg -n "from src.external.playwright import|import src.external.playwright" src/core/roster.py src/core/gazer.py src/core/meteorite.py` returns nothing; those modules import `src.external.telescope` instead; **every function name and parameter list they used from today's** `playwright.py` **exists identically on** `telescope.py` (no reworked logic in calling components). Core does not embed Telescope URLs/tokens (`rg -n "TELESCOPE_|/telescope" src/core/roster.py src/core/gazer.py src/core/meteorite.py` is empty — config owns them). Fail: leftover playwright imports, renamed/reparametrized call sites, or core hardcoding Telescope endpoints.
 8. **Shared post-render helpers in src** — Post-render helpers used by today's HTML/text pipeline (at least cull and extract-from-HTML / delimiter-split style utilities that lived in `playwright.py`) are defined under `src/external/telescope.py` and callable without a browser. Fail: those helpers exist only under `service/telescope/` or require Firefox to run.
 9. **Separate host even locally** — Platform config points at a Telescope base URL whose host/port is not the platform process; local smoke requires a second Telescope process/container. Fail: platform scrapes by importing `service.telescope` or sharing one process with Firefox.
10. **Bearer is env, not candidate auth** — Telescope auth checks only the shared env bearer; grepping Telescope auth code finds no candidate/Stytch session validation. Fail: Telescope gated on user/candidate credentials.
11. **Console-only Telescope logs** — `rg -n "app_log|astral\\.db|add_log_entry|database\\." service/telescope/` returns no matches. Fail: Telescope writes to the platform DB or app_log path.
12. **OOM isolation** — With Phase 1 fixed replicas ≥1 and per-node semaphore documented in config, a Telescope replica OOM/restart does not require restarting the platform Railway service to resume scrapes. Fail: platform service dies when Telescope OOMs, or only one fused process remains.
13. **Phase 2 out; Surfer not built** — `rg -n "serviceInstanceUpdate|Judoscale|numReplicas" service/ src/` returns no autoscaler implementation shipped by this epic; no Surfer extension package is added by this epic. Fail: Phase 2 autoscaler or Surfer extension lands here.
14. **Telescope admin page** — An admin-authenticated operator can open the Telescope admin screen, submit a URL with html|text and optional-parameter toggles, and see the raw response body plus scrape metadata (bot-block / cookies / other scrape failures when present). Fail: no admin route/page, or response omits content/metadata the operator needs to judge scrape health.

## Open questions

none

## Proposed child tickets

#### 1!!!: **Telescope service container and API - Ada**

Stand up `service/telescope/` with FastAPI `/telescope` (optional `links` default true), `/telescope/html`, `/healthz`, one Firefox per replica with fresh per-request contexts, RAM semaphore, timeouts, recycle, cookie dismiss, expand default on, wait_ready default off (generic only), browser capture only (no Surfer-shared post-render fork), Dockerfile + Telescope requirements, env bearer auth, console-only logging (no DB). Does not own the platform HTTP facade (#2) or Railway replica/CI wiring (#3).
**Citations:** `stat.logging.error`; `stat.logging.warning`; `stat.logging.info`; `stat.logging.debug`; new-pattern flag `patt.external.web-scraping-via-telescope` (pending Archie); import-rules amendment request (service↔src bidirectional ban)
**Scope:** `service/telescope/` — **new** — FastAPI app package: lifespan browser session, `/telescope`, `/telescope/html`, `/healthz`, browser-interaction helpers only (navigate / capture / load-all / cookie-dismiss / readiness); console-only logging; no fork of post-render cull/split helpers that Surfer must share. `service/telescope/requirements.txt` — **new** — Telescope-only deps (Playwright pin matching the image, FastAPI, uvicorn, etc.). `service/telescope/Dockerfile` — **new** — Official Playwright Python image, Firefox, single uvicorn worker, non-root, `--init`, memory/`/dev/shm` sizing.
**Estimate: 5**

#### 2!: **Platform [telescope.py](<http://telescope.py>) drop-in and playwright decommission - Hedy**

Add `src/external/telescope.py` as the **full** drop-in port of today's `playwright.py` (same public names/params for core's import surface; HTTP pool dispatch + retry + env bearer for headless scrape paths; **all** former non-browser / post-render helpers — cull, delimiter splits, extract-from-HTML, etc. — live in this same file for Surfer reuse; no `page_parse.py`); delete `src/external/playwright.py`; change `roster.py` / `gazer.py` / `meteorite.py` import module path only; add Telescope pool/auth/timeout/concurrency keys in config; pin platform HTTP client in root requirements and drop platform Firefox launch deps. After #1. Does not own Railway service deploy or CI import fence (#3). Does not build Surfer.
**Citations:** `patt.entity.batch-processing`; `patt.entity.batch-criteria`; `stat.logging.error`; `stat.logging.warning`; `stat.logging.info`; `stat.logging.debug`; new-pattern flag `patt.external.web-scraping-via-telescope` (pending Archie)
**Scope:** `src/external/telescope.py` — **new** — full drop-in replacement for `playwright.py`: same public names/params; HTTP client for headless scrape surfaces; **all** former non-browser / post-render helpers live in this same file (Surfer-ready shared processing); no in-process Firefox. `src/external/playwright.py` — **deleted** — fully decommissioned; no thin-client leftover under this name. `src/core/roster.py` — **modified** — import module path `playwright` → `telescope` only; no call-site shape changes. `src/core/gazer.py` — **modified** — same import-path-only rewire. `src/core/meteorite.py` — **modified** — same import-path-only rewire. `src/utils/config.py` — **modified** — Telescope base URL(s), env bearer token key, client timeout, platform in-flight pool semaphore / per-node caps, and Telescope-facing defaults that must not live as literals in callers. `requirements.txt` — **modified** — add direct `httpx` (or confirm/pin the async HTTP client the facade uses) for the platform Telescope client; drop platform Playwright browser runtime needs once no process launches Firefox.
**Estimate: 5**

#### 3: **Railway Phase 1 deploy and import-boundary CI - Katherine**

Wire the Railway Telescope service from `service/telescope/` (private networking, env bearer secret, memory limits, start at 1 replica then fixed fan-out), and land the CI/lint rule that fails on `service/`↔`src/` imports in **either** direction. After #2 so end-to-end client+node can be validated on separate hosts/processes. No Phase 2 autoscaler. No Surfer extension.
**Citations:** import-rules amendment request (service↔src bidirectional ban); `stat.logging.info`
**Scope:** `service/telescope/railway.toml` (or equivalent Railway service config colocated with the service) — **new** — subdirectory deploy for the Telescope service. `.github/workflows/` (or a tracked lint script invoked by CI) — **modified/new** — fail the build if `service/telescope/` imports from `src/` **or** `src/` imports from `service/`.
**Estimate: 3**

**Monolith check:** Functional scope has 10 ship capabilities (+ non-goals); children #1–#3 partition service / platform drop-in+shared helpers / deploy+CI; UAT Bug [AST-1728](https://linear.app/astralcareermatch/issue/AST-1728/telescope-admin-page) owns the Telescope admin operator page + metadata contract (#10 / AC14) — not a single mega-ticket.

**Scope partition check:** `service/telescope/` + requirements + Dockerfile → #1; `telescope.py` + delete `playwright.py` + core import-path rewires + `config.py` + root `requirements.txt` → #2; `service/telescope/railway.toml` + CI lint → #3; `src/ui/frontend/` + `src/ui/api/` admin Telescope surface (+ metadata fields on service/client as needed) → [AST-1728](https://linear.app/astralcareermatch/issue/AST-1728/telescope-admin-page). No file claimed twice. No `page_parse.py`.

---

## Original brief

# Astral Scope

*(as in tele**scope**, and "**scope** out a website")*

Extract Playwright browser work out of the main platform process into a dedicated, horizontally-scalable microservice. The main platform's `src/external/playwright.py` becomes a thin HTTP client that dispatches scrape requests to a pool of Scope nodes.

> This ticket is a **complete spec**, not a define-parent stub. It intentionally states the design we've already converged on. It does **not** need a separate definition pass.

## Problem

Today the whole platform and Firefox run in one Railway service. `parse_job_list_batch` ([roster.py:1294](<http://roster.py:1294>)) drives a single shared `BatchBrowserSession` ([playwright.py:153](<http://playwright.py:153>)) with `asyncio.Semaphore(max_concurrent=3)`. When too many pages open at once, Firefox's memory balloons and OOMs the **entire service** — orchestration, DB connections, and business logic die with the browser. Scraping capacity and platform logic are fused; they can't scale independently.

## Goal

A **dumb, stateless, domain-agnostic** rendering primitive: give it a URL, it navigates, scrapes, and returns what's on the page. It knows nothing about companies, entities, jobs, or our data model. All orchestration, crawl logic, parsing, and state stay on the platform.

The scaling win isn't "more scrapers" — it's **isolating the crash-prone, memory-heavy tier from the stateful orchestration tier**, so a browser OOM kills one replica (Railway restarts it) instead of the platform.

---

## What we WANT

* **Per-URL, not per-entity.** The unit of work is a single link. A site's N pages fan out across N nodes. No session affinity, no cross-call state.
* **Stateless service, no database.** Every request is fully independent → round-robin, failover, retry, and autoscaling are all trivial.
* **Coarse-enough-to-be-useful, thin-enough-to-be-generic.** All the *interaction smarts* (cookie dismissal, readiness wait, load-all scroll/click) happen **inside a single call** as options — but nothing domain-specific.
* **Thin client on the platform.** Keep `src/external/playwright.py` as the client facade (or `scope_client.py`) so callers (`roster.py`, `gazer.py`) barely change — they still `await scrape(url)`, they just don't know a browser moved to another box.
* **Hard per-container concurrency cap sized to RAM.** This is the actual OOM fix: a container physically cannot open more browsers than its RAM holds.
* **Private networking + bearer token.** A service that fetches arbitrary URLs is an SSRF surface; keep it internal to Railway's private network with an auth token.

## What we DON'T want

* **No mirroring the whole platform N times.** That replicates DB pools, cron, and dispatch loops just to get browsers, and creates a multi-writer hazard (double-dispatch, races) against the shared DB.
* **No business/domain logic on the service.** No company/entity/job awareness. No **job-listing parsing** (`extract_raw_job_listings`, `extract_page_clickables` stay platform-side). No **vendor/ATS routing** — see note below.
* **No database / no persisted state on the service.**
* **No submit-then-poll / webhook / job-queue system.** Per-*link* scrapes are seconds, not the old 120s-per-company. Hold the connection and `await` synchronously. A job system would force state back onto the service and kill the statelessness. (Redis-pull workers are a *later* evolution only if we outgrow HTTP.)
* **No separate repository (yet).** Monorepo-first, built extraction-ready (its own deps + Dockerfile, a lint/CI rule that it never imports from `src/`). Extraction to its own repo is a `git filter-repo` away once the contract stops churning — cheap in that direction, expensive to walk back.
* **No premature autoscaler.** Ship fixed replicas first; add scaling only after the fixed fleet is boringly stable.
* **No depth/output limits or perf shortcuts** added without explicit sign-off.

---

## API contract

Stateless. Selector semantics + which fields are default-on vs opt-in to be finalized in implementation.

`POST /scope` — text + links (both come free from one page load, so bundle them)

```
req:  { url, selector?: "page"|"body"|"div"|<css>, expand?: bool, wait_ready?: bool }
resp: { final_url, text, links: [{ href, text }] }
```

`POST /scope/html` — rendered HTML of the scoped element (separate endpoint per Susan; job-list parsing needs DOM, not flattened text)

```
req:  { url, selector?, expand?, wait_ready?, cull?: bool }
resp: { final_url, html }
```

`GET /healthz` — actually launches/pokes a browser, not just a 200.

* `expand` = run the load-all scroll + "Load More" click loop (`load_all_jobs`, [playwright.py:2290](<http://playwright.py:2290>)) before capture.
* `wait_ready` = the dynamic-content readiness poll (`wait_for_careers_list_readiness`).
* Cookie-banner dismissal always runs.
* **Redirects:** always return `final_url`.
* **Tradeoff to confirm:** two endpoints = two navigations if a single flow needs *both* text and HTML off the same load. Current flows look clean (prefilter/recheck → text, parse-job-list → HTML, discovery → links), so this is likely fine — verify no caller needs both from one load.

### Note on vendor detection (why the payload is just text/links/html)

`detect_vendor` / `recommend_routing` ([playwright.py:870](<http://playwright.py:870>), 1041) fingerprint the ATS (Greenhouse, Lever, Workday, iCIMS, Ashby, …) from network-request URLs + iframe URLs. **They are currently only called by tests — dead in the live pipeline.** So we do NOT need to return `request_urls` / `frame_urls` now. If vendor routing is ever wired into production, add those artifacts to the response then.

---

## Async / concurrency model (platform side)

The platform is already async — **we just** `await` **the HTTP call.** `parse_job_list_batch` already fires N concurrent scrapes via `asyncio.gather` under `asyncio.Semaphore` ([roster.py:1294](<http://roster.py:1294>)–1343). The only change: inside the loop, instead of driving a local browser, `await http_client.post(scope_url, ...)` (httpx.AsyncClient). While one request is parked on the socket, the event loop runs the others — waiting is free.

* The **semaphore now caps in-flight requests to the pool** (e.g. 5 nodes × 3 = don't fire >\~15 at once) — that's the backpressure knob.
* Client timeout \~30–60s; on timeout, **retry the same URL against a different node**.

---

## Implementation recommendations

### The container (this is the real OOM fix)

* Base on the **official Playwright Python image, pinned to the exact version** matching the pip `playwright` package (browsers must match the driver).
* **Keep Firefox** — the `firefox_user_prefs` and vendor patterns are Firefox-tuned.
* **FastAPI + a single uvicorn worker** (one event loop; multiple workers each spawn a browser = memory multiplied).
* **One browser per container**, launched in FastAPI `lifespan`; reuse `BatchBrowserSession` ([playwright.py:153](<http://playwright.py:153>)) nearly verbatim.
* **Fresh context per request, always closed in** `finally`**.** No context reuse across URLs.
* `asyncio.Semaphore` **cap sized to container RAM** (\~2–4 pages in a 2GB container). Match this to the platform-side dispatch cap.
* `asyncio.wait_for` **timeout on every request** — one hung `networkidle` page pins a slot and cascades into a fleet outage.
* **Recycle the browser after N requests** (`recover()`, [playwright.py:189](<http://playwright.py:189>) is the seam) to counter Firefox memory creep.
* Ops: `--init` (reap zombies), explicit memory limit, `/dev/shm` sized (or disable dev-shm), **non-root user** (untrusted URLs), Debian/Ubuntu base (not Alpine).

### Deployment & scaling (Railway specifics — verified)

Railway has **no native load-based horizontal autoscaling**. It does vertical autoscaling automatically and manual replica counts; horizontal scaling means either fixed replicas or a small autoscaler you run against the GraphQL API. Railway can deploy a **subdirectory of a monorepo** as its own service — so a separate repo is NOT required for a separate service.

* **Phase 1 — fixed replicas + hard per-node cap.** e.g. 5 replicas × 3 pages = 15 concurrent, cannot exceed. Kills the OOM today with zero autoscaler code. **Ship this first.**
* **Phase 2 — batch-aware autoscaler.** Load is batchy (`parse_job_list_batch`), not a smooth stream. At batch claim, size desired replicas from batch size and call `serviceInstanceUpdate(numReplicas)`; scale back to a floor of 1 **only when the pool is fully idle**. This dodges Railway's sharp edge — the API can only set a desired count, it **cannot pick which replica to kill**, so scaling down mid-flight would murder an in-flight scrape. Batch-boundary scaling sidesteps that entirely.
* Buy-vs-build shortcut: **Judoscale** does queue/latency-based autoscaling on Railway.

### Dispatch (platform side)

* Start **round-robin**; upgrade to **least-in-flight** over the pool (the platform is the single dispatcher, so it knows in-flight counts — no DB needed).
* **Retry-to-another-node** on failure/timeout. Idempotent per-URL scrapes make this painless.

---

## Rollout / phasing

1. Stand up the Scope container with `/scope`, `/scope/html`, `/healthz`; move the generic browser code (navigate, visible-text, links, load-all, cookie dismiss, cull) into it. Leave parsing/vendor/crawl on the platform.
2. Rewrite `src/external/playwright.py` into the thin async client; keep the public function signatures so `roster.py`/`gazer.py` barely change.
3. Deploy **1 node**, validate the contract + memory ceiling end-to-end.
4. Fan out to fixed replicas (Phase 1).
5. Add the batch-aware autoscaler (Phase 2) once the fixed fleet is stable.

## Open questions (confirm during implementation)

* **Service home:** top-level `astral-scope/` (sibling to `src/`, cleanest deploy boundary — lean) vs `src/scope/`.
  * create "service" as a sibling to src, then create scope within that folder.
* **Selector semantics:** single container vs multiple matches → one text blob or a list per match.
  * Multiple matches returns an array of text blobs.
* **Defaults:** is `expand` / `wait_ready` on or off by default? Is `cull` default-on for `/scope/html`?
  * Expand is default ON, I don't know what wait_ready is, but use your judgment.  Cull is default-on for html.
* Confirm no single caller needs text **and** HTML from one page load (else that URL double-loads across two endpoints).
  * Confirmed.  HTML is asked for for specific purposes.

### Comments

#### chuckles — 2026-09-21T06:27:34.015Z
[fix-intake] No new `[bug]`/`[fix]` — not filing.

Respawning Ada on AST-1752 plan-fix. Parent scope already covers `LINK_EXPIRED`. Parent stays User Testing / Chuckles.

#### susan — 2026-09-21T06:24:33.234Z
Please respawn Ada to continue the work, please.

#### chuckles — 2026-09-21T06:21:16.741Z
[check-linear] answered — Component and Technical scope already include AST-1752: `closed`/`missing` → `LINK_EXPIRED` and `total_failed` (not `total_errors`); warning text names the bucket and must not say "This row is ERROR". Ada can re-run plan-fix.

#### chuckles — 2026-09-21T06:20:34.632Z
[fix-intake] No new `[bug]`/`[fix]` — not filing.

Parent Component/Technical scope now covers AST-1752: `LINK_EXPIRED` for `closed`/`missing` (fail counter, not `total_errors`), config state + status map, and warning text that names the bucket instead of "This row is ERROR". AST-1751 still holds for genuine technical errors. Parent stays User Testing / Chuckles.

#### susan — 2026-09-21T06:16:42.587Z
@chuckles Please expand the description of this ticket to accommodate the requirement in 1752 so that Ada may be unblocked.

#### chuckles — 2026-09-21T06:02:07.596Z
[fix-intake] Marked comment points at existing AST-1752 (already a Bug child) — not filing a duplicate. Moved AST-1752 Backlog → Discussion, assignee Susan. Parent stays User Testing / Chuckles.

#### susan — 2026-09-21T06:00:05.911Z
\[bug\] see new [AST-1752](https://linear.app/astralcareermatch/issue/AST-1752/meteorite-scrape-closedmissing-content-verdicts-must-be-fail-link) ticket for new bug.

#### chuckles — 2026-09-21T01:39:40.164Z
[fix-intake] Filed 2 Bug children at Discussion (assignee Susan): AST-1750, AST-1751. Parent stays User Testing / Chuckles.

#### susan — 2026-09-21T01:38:28.456Z
\[bug\] errors are not ALSO fails.  They are only errors.  Fails are only for BOT_BLOCKED and NOT_A_JOB.

#### susan — 2026-09-21T01:37:58.339Z
\[bug\] When scraping 5 urls, I get re-produceable errors back, but no detail.  Logging statutes for telescope fails for error and debug logging.

```
[2026-09-21 01:34:46] INFO src.external.telescope: telescope ok path=/telescope final_url=https://www.dice.com/job-detail/c5a9ffeb-c9c9-44a2-b0e4-59668a8d18b3
[2026-09-21 01:34:46] WARNING src.core.meteorite: meteorite 92 for somerset — scrape_closed
  This row is ERROR
[2026-09-21 01:34:46] INFO src.external.telescope: telescope ok path=/telescope final_url=https://www.dice.com/job-detail/b3573283-846b-4863-a592-ab8e6ec18e27
[2026-09-21 01:34:46] WARNING src.core.meteorite: meteorite 96 for somerset — scrape_closed
  This row is ERROR
[2026-09-21 01:34:46] INFO src.external.telescope: telescope ok path=/telescope final_url=https://www.dice.com/job-detail/029332ea-1e6a-44ab-9372-8c74805becd9
[2026-09-21 01:34:46] WARNING src.core.meteorite: meteorite 97 for somerset — scrape_closed
  This row is ERROR
[2026-09-21 01:34:46] INFO src.external.telescope: telescope ok path=/telescope final_url=https://www.dice.com/job-detail/9404cd49-0dc1-42dd-84c0-eee19b48fbb7
[2026-09-21 01:34:46] WARNING src.core.meteorite: meteorite 98 for somerset — scrape_closed
  This row is ERROR
[2026-09-21 01:34:46] INFO src.external.telescope: telescope ok path=/telescope final_url=https://www.dice.com/job-detail/9940908d-3e9b-4111-94ce-7a6d0102baea
[2026-09-21 01:34:46] WARNING src.core.meteorite: meteorite 99 for somerset — scrape_closed
  This row is ERROR
[2026-09-21 01:34:46] INFO src.core.dispatcher: somerset | dispatch meteorite stopping scrape_meteorite — 0 remaining after 1 run(s)
[2026-09-21 01:34:46] INFO src.core.dispatcher: somerset | dispatch meteorite task completed: scrape_meteorite pass:0 fail:5 error:5 (batch: scrape_meteorite-f3d275db-cdb9-4378-8276-f84137831192)
```

#### chuckles — 2026-09-21T01:13:28.443Z
[fix-intake] Filed 4 Bug children at Discussion (assignee Susan): AST-1744, AST-1745, AST-1746, AST-1747. Parent Description amended for optional `id` filter scope. Parent stays User Testing / Chuckles.

#### susan — 2026-09-21T01:10:18.156Z
\[bug\] the link array must be deduped.  Multiple cases of the same link with different text should support an array of text per link.

#### susan — 2026-09-21T01:06:20.978Z
\[bug\] Please add "id" as an optional parameter. This would be similar to class, but would look for `id="<idstring>"` Update the description of the parent ticket to include the scope, and issue a bug ticket.

#### susan — 2026-09-21T01:02:19.877Z
\[bug\] when I specify a class name, e.g. `logo`, it should return the outer HTML for the element(s) of that class:

```
<svg id="bLogo" role="img" class="logo" viewBox="0 0 24 24" aria-label="Microsoft Logo Image" filter="none" tabindex="0"><g class="squares"><path fill="#f26522" d="M11.4 0H0v11.4h11.4z"></path><path fill="#8dc63f" d="M23.9 0H12.5v11.4H24z"></path><path fill="#00aeef" d="M11.4 12.5H0V24h11.4z"></path><path fill="#ffc20e" d="M23.9 12.5H12.5V24H24z"></path></g></svg>
```

#### susan — 2026-09-21T00:59:45.649Z
\[bug\] Tag and Selector should be the same thing (html, div, span, body, head, ul). class name should be secondary filter (elements within the tag with `class="<classname>"`

#### chuckles — 2026-09-20T23:57:28.710Z
[fix-intake] Filed 5 Bug children at Discussion (assignee Susan): AST-1733, AST-1734, AST-1735, AST-1736, AST-1737. Parent stays User Testing / Chuckles.

#### susan — 2026-09-20T23:55:22.277Z
\[bug\] Is expand the same as pagination? Did we lose the pagination scrape feature with this migration?  If I go to a url and I have 1500 results across 15 screens, will telescope capture all 15 sets of 100?

#### susan — 2026-09-20T23:52:29.957Z
\[bug\] when I put a class name in the filter (`shaders`) the html scrape does not recognize that I'm talking about a class name and returns an empty string.  Perhaps this should be a separate parameter?  Like, filter by element tag and then filter by class name?

#### susan — 2026-09-20T23:50:02.418Z
\[bug\] when I scraped the text for the head element with links and then scraped the text for the body element with links, the links were identical, and I would have expected them to be different.

#### susan — 2026-09-20T23:47:12.529Z
\[bug\] the actual Telescope page isn't scrollable, so when we view the full JSON, In can see only one line of it at a time.

#### susan — 2026-09-20T23:45:54.880Z
\[bug\] selecting text from the head section of the url returns style content and other non-visible text, such as:

```
div[data-rewards-widget].medallion .firework,
.firework::before,
.firework::after {
  position: absolute;
  top: 16px;
  left: 16px;
  transform: translate(-50%, -50%);
  width: 0vmin;
  aspect-ratio: 1;
  background: radial-gradient(circle, #7fdbff 0.4vmin, rgba(245, 245, 245, 0) 0 0) 50% 0%,
    radial-gradient(circle, #39cccc 0.4vmin, rgba(245, 245, 245, 0) 0 0) 0% 50%,
```

#### chuckles — 2026-09-20T19:08:40.115Z
[fix-intake] Filed 4 Bug children at Discussion (assignee Susan): AST-1729, AST-1730, AST-1731, AST-1732. Parent stays User Testing / Chuckles.

#### susan — 2026-09-20T19:06:01.534Z
\[bug\] when a class name is specified, the links array includes links on the whole page, not just within the class name

#### susan — 2026-09-20T19:04:03.965Z
\[bug\] scraping HTML, Specifying a class name \``points-container`\` from [https://www.bing.com](<https://www.bing.com>) returns an empty HTML string, though I know the container exists because it was explicitly seen in the body element.

#### susan — 2026-09-20T18:59:35.940Z
\[bug\] The output is not in a scrollable/wrapping text field, I can't select all or scroll to see the full response.

#### susan — 2026-09-20T18:59:30.840Z
\[bug\] The html does not return the full html (only body) where no selector is set.

#### chuckles — 2026-09-20T16:17:14.983Z
[fix-intake] No new `[bug]`/`[fix]` — not filing. Spawning Katherine on AST-1728 for plan-fix (scope already amended on AST-1721). Parent stays User Testing / Chuckles.

#### susan — 2026-09-20T16:16:06.919Z
Chuckles, Katherine is NOT ACTIVELY WORKING on the now-unblocked child ticket.  YOU MUST SPAWN HER to do the work.

#### chuckles — 2026-09-20T16:13:07.874Z
[fix-intake] No new `[bug]`/`[fix]` in this batch — not filing another child.

AST-1728 (Telescope Admin page) is already the child: Plan Discuss, Katherine. Parent Component/Technical scope was amended for the admin UI/API. Next for that ticket is Katherine re-running plan-fix (fix lane F1), not another UAT-batch file. Parent stays User Testing / Chuckles.

#### susan — 2026-09-20T16:12:24.786Z
Please proceed with the child bug issue in progress!

#### chuckles — 2026-09-20T14:39:32.849Z
Already filed as **AST-1728** (Telescope Admin page) — not filing a duplicate.

Reassigning AST-1728 → Chuckles so `bug-fix` drives it through the fix lane to User Testing. Parent stays User Testing / Chuckles (no In Progress move here).

#### susan — 2026-09-20T14:38:11.238Z
I need you to run that ticket through to user testing, please.  \[bug\]

#### chuckles — 2026-09-20T14:37:06.010Z
No `[bug]` / `[fix]` marker on that comment, so this UAT-batch pass does not file a new child.

That ask is already tracked as **AST-1728** (Telescope Admin page) — Todo, Katherine. If that ticket is the one you meant, nothing else to file here. If you have a different or additional UAT break, reply with `[bug]` or `[fix]` on it.

#### susan — 2026-09-20T13:51:01.175Z
we need to add an admin screen for using telescope.  A screen with a url and response type (html vs text) and toggles for each optional parameter, and a display window to show the raw response from the telescope service.  I expect the response to include the string contents, as well as Meta data about the scrape, such as if it was bot blocked or cookies, or some other issue that prevented it from properly scraping the page as expected.

#### chuckles — 2026-09-20T05:29:36.911Z
AST-1726 scope-gate cleared — added scripts/build_railway.sh, scripts/setup_dev.sh, scripts/start_server.py (+ config playwright_browsers_path drop) to ## Scope; re-spawning plan-child.

---

_Implementation detail may live in git history on `origin/dev`._
