# AST-2023 — Telescope click-then-capture

- **Ticket:** [AST-2023](https://linear.app/astralcareermatch/issue/AST-2023)
- **Parent:** [AST-2022 — New Fetch task for RELATIVE_JOB_LINK](https://linear.app/astralcareermatch/issue/AST-2022)
- **Publish ref:** `sub/AST-2022/AST-2023-telescope-click-capture` (origin only)
- **Canon scope:** `stat.logging.debug`, `stat.logging.warning`, `stat.logging.error`

Telescope gets one new optional request option, `click_href`. When set, after the normal
load → cookie dismiss → expand → (optional) wait_ready on the list page, the service clicks the
first `<a>` whose `href` **attribute** exactly equals `click_href`, follows the same-tab navigation
or new-tab popup, and runs capture on the destination — so `final_url`, `text` / `links` / `html`
and `scrape_meta` all describe the destination page. A missing anchor fails the job immediately
with the distinct error class `click_target_missing`, which the worker never retries. The
platform client forwards the option and exposes one call,
`click_through_visible_text(list_url, href) -> (final_url, text)`, for the runner in AST-2022 #3.
Requests without `click_href` are unchanged (no new request key, no new response key).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `service/telescope/interact.py` | New `ClickTargetMissing` exception + new `click_and_follow(page, href)` | service |
| `service/telescope/scrape.py` | `TelescopeRequest.click_href` field; `CLICK_TARGET_MISSING` constant; `run_scrape` click step + error mapping | service |
| `service/telescope/worker.py` | `Worker._retry_delay`: `CLICK_TARGET_MISSING` non-retried alongside `bad_request` | service |
| `src/external/telescope.py` | `_post_telescope` forwards `click_href`; `_TelescopeQueue.submit` maps the new class; new constant `TELESCOPE_CLICK_TARGET_MISSING`; new public `click_through_visible_text` | external |

No config, no tests, no bible, no other files.

## Notes for every stage

- **Compile + lint before every commit (Susan's rule).**
  - Compile: `python3 -m py_compile <every file touched in the stage>` — must exit 0.
  - Lint: `ruff check <every file touched in the stage>` — must report no new findings in
    lines this stage added. `ruff` is **not** installed in the epic worktree's environment
    today (nor `flake8` / `pyflakes`). If it still isn't available, **stop** and post the
    blocked comment on AST-2022 naming the missing tool — do not skip lint and do not pick a
    different linter yourself.
- **Tests (read-only for engineers):** `python3 -m pytest tests/component/external/test_telescope.py -q`.
  Today this fails at collection with `ModuleNotFoundError: No module named 'asyncpg'` —
  an environment gap (`asyncpg` is in `requirements.txt`), not a product bug. If still
  missing at build time, stop and comment on AST-2022; do not edit tests.
  `tests/component/service/test_telescope_app.py` is module-skipped (targets a retired
  `app.TelescopeRequest` / `_run_browser_job` surface); it is not a baseline for this ticket.
- **"POST to the Telescope service" (AC 4)** means enqueueing a job on the Telescope Postgres
  queue (`_TelescopeQueue.submit` / `_post_telescope`) — the service has no HTTP scrape route
  (`service/telescope/app.py` serves only `/wake` and `/healthz`). Nothing here adds one.
- **Logging:** canon `stat.logging.*` binds `src/**`. In `src/external/telescope.py` the new
  function logs `Calling …` / `Response from …` at `logger.debug` (no gating, no truncation) and
  **does not** log warnings/errors — it raises, and the runner that chooses the job's
  destination (AST-2022 #3) logs once. Service files keep their existing `_log.debug`
  joint style; the worker's existing failure log lines are not changed.

## Stage 1: Service — click step, request option, non-retried error class

**Done when:** `service/telescope/{interact,scrape,worker}.py` compile; a request with
`click_href` runs the click step before capture; a request without it runs exactly the old
sequence; `Worker._retry_delay(job, "click_target_missing")` returns `None`.

1. In `service/telescope/interact.py`, change the import block at the top to add
   `import asyncio` above `import time` (stdlib, alphabetical). Update the module docstring
   to `"""Browser interaction — navigate, cookies, expand, click-and-follow, generic wait_ready."""`.

2. In `service/telescope/interact.py`, directly after `navigate(...)` (before
   `_try_dismiss_cookie_banner`), add exactly:

   ```python
   class ClickTargetMissing(Exception):
       """No <a> on the loaded page has this exact href attribute."""


   async def click_and_follow(page, href: str):
       """Click the first <a> whose href attribute equals `href`; return the destination page.

       Follows a same-tab navigation or a new-tab popup, whichever happens first.
       Reuses page_goto_timeout_ms for the click and the navigation — no new caps.
       """
       _log.debug("Calling click_and_follow: [href=%s url=%s]", href, page.url)
       nav_ms = settings.page_goto_timeout_ms
       # Inside a CSS "…" string only backslash and double quote need escaping.
       quoted = href.replace("\\", "\\\\").replace('"', '\\"')
       anchor = page.locator(f'a[href="{quoted}"]')
       # count() does not wait: a missing target fails now, not after a timeout.
       if await anchor.count() == 0:
           raise ClickTargetMissing(f"no <a href={href!r}> on {page.url}")
       start_url = page.url
       # Arm both waiters before the click so neither event can be missed.
       popup = asyncio.ensure_future(page.wait_for_event("popup", timeout=nav_ms))
       same_tab = asyncio.ensure_future(
           page.wait_for_url(
               lambda u: u != start_url, wait_until="domcontentloaded", timeout=nav_ms
           )
       )
       try:
           await anchor.first.click(timeout=nav_ms)
           done, _ = await asyncio.wait(
               {popup, same_tab}, return_when=asyncio.FIRST_COMPLETED
           )
       finally:
           for t in (popup, same_tab):
               if not t.done():
                   t.cancel()
           # Retrieve every outcome so no "exception never retrieved" noise is left behind.
           await asyncio.gather(popup, same_tab, return_exceptions=True)
       if popup in done and popup.exception() is None:
           dest = popup.result()
       elif same_tab in done and same_tab.exception() is None:
           dest = page
       else:
           # Plain Exception (never CancelledError) so run_scrape maps it to scrape_failed.
           raise RuntimeError(f"click on {href!r} did not navigate within {nav_ms}ms")
       await dest.wait_for_load_state("domcontentloaded", timeout=nav_ms)
       await dest.wait_for_timeout(500)
       _log.debug(
           "Response from click_and_follow: popup=%s final_url=%s",
           dest is not page,
           dest.url,
       )
       return dest
   ```

   ⚠️ **Decision:** Exact match is on the `href` **attribute** via the CSS selector
   `a[href="…"]` (not the resolved `.href` property, not substring) — the parent's "exactly
   equals the job's stored relative link, no fallback matching". Duplicate anchors with the
   same `href` (title link + "Apply" button) are common; `.first` is clicked.

   ⚠️ **Decision:** Only "anchor not on the page" is `ClickTargetMissing` (non-retried). An
   anchor that is present but not clickable within `page_goto_timeout_ms`, or a click that
   never navigates, raises an ordinary exception → `scrape_failed` → normal worker retry. Those
   can be transient (overlay, slow JS); the ticket names only a *missing* target as the
   distinct non-retried class. The runner (#3) maps any Telescope failure to
   `RELATIVE_LINK_FAIL` either way.

   ⚠️ **Decision:** The popup page belongs to the job's own browser context, which
   `Firefox.page()` closes after every job (`service/telescope/browser.py`), so the popup needs
   no separate close.

3. In `service/telescope/scrape.py`, change
   `from interact import dismiss_cookies, expand_page, navigate, wait_ready_generic` to
   `from interact import ClickTargetMissing, click_and_follow, dismiss_cookies, expand_page, navigate, wait_ready_generic`
   (wrap in parentheses one name per line if it exceeds the line length ruff reports).

4. In `service/telescope/scrape.py`, after the `_FIELDS_DESC = (...)` block, add:

   ```python
   _CLICK_DESC = (
       "Optional. After load / cookies / expand / wait_ready, click the first <a> whose href "
       "attribute exactly equals this value, follow it (same tab or new tab), and capture on "
       "the destination. No such anchor fails the job with error_class click_target_missing "
       "(never retried)."
   )
   ```

5. In `service/telescope/scrape.py`, in `class TelescopeRequest`, add after `wait_ready: bool = False`:

   ```python
   click_href: Optional[str] = Field(default=None, description=_CLICK_DESC)
   ```

   No validator. `None` or `""` means no click (step 6 checks truthiness).

6. In `service/telescope/scrape.py`, directly above `class ScrapeError`, add:

   ```python
   # Contract mirror: src/external/telescope.py maps this class — change both sides together.
   CLICK_TARGET_MISSING = "click_target_missing"
   ```

   and change the `ScrapeError` docstring to
   `"""A failed attempt. error_class drives retry: bad_request and click_target_missing never retry."""`.

7. In `service/telescope/scrape.py`, inside `run_scrape._scrape`, insert between the
   `if req.wait_ready: await wait_ready_generic(page)` lines and `out: dict = {"final_url": page.url}`:

   ```python
           if req.click_href:
               page = await click_and_follow(page, req.click_href)
               # Destination may be another site with its own banner; same dismiss as a direct load.
               cookies_dismissed = await dismiss_cookies(page) or cookies_dismissed
   ```

   Do not move or alter any existing line of `_scrape`. Update the `run_scrape` docstring to
   `"""One attempt. Raises ScrapeError("timeout" | "click_target_missing" | "scrape_failed", …) on failure."""`.

   ⚠️ **Decision:** Order is list-page load → cookies → expand → wait_ready → click → cookie
   dismiss on destination → capture. Expand / wait_ready are list-page concerns (the anchor
   may only render after scroll / Load More) and are not repeated on the destination. Cookie
   dismiss *is* repeated on the destination so the captured text matches what a direct
   `fetch_jd` load of that URL would produce — the runner (#3) feeds it into the same
   cookie-wall gate. `scrape_meta.cookies_dismissed` is true if either dismiss clicked.

8. In `service/telescope/scrape.py`, in `run_scrape`'s `try` block, add a handler between
   `except asyncio.TimeoutError:` and `except Exception as exc:`:

   ```python
       except ClickTargetMissing as exc:
           raise ScrapeError(CLICK_TARGET_MISSING, str(exc)) from None
   ```

9. In `service/telescope/worker.py`, change
   `from scrape import ScrapeError, parse_request, run_scrape` to
   `from scrape import CLICK_TARGET_MISSING, ScrapeError, parse_request, run_scrape`, and in
   `Worker._retry_delay` change `if error_class == "bad_request":` to
   `if error_class in ("bad_request", CLICK_TARGET_MISSING):`. No other line of `worker.py` changes.

10. Compile + lint the three service files (see Notes). Commit:
    `code(AST-2023): telescope click_href — click-and-follow before capture, click_target_missing non-retried`.
    Publish per build-child.

## Stage 2: Platform client — forward option, distinct failure class, public call

**Done when:** `src/external/telescope.py` compiles; `_post_telescope(url, fields=[...])` builds
the same body as before (no `click_href` key); `_post_telescope(..., click_href="/jobs/1")`
adds `"click_href": "/jobs/1"`; a queue row failing with `error_class="click_target_missing"`
raises `PlaywrightInfraError` with `failure_class == "telescope_click_target_missing"`;
`click_through_visible_text` returns `(final_url, text)`; existing
`tests/component/external/test_telescope.py` green (environment permitting — see Notes).

1. In `src/external/telescope.py`, directly after the `PLAYWRIGHT_INFRA_FAILURE_CLASSES`
   frozenset, add:

   ```python
   # Telescope found no <a> with the requested click_href. A site outcome, not infra —
   # deliberately absent from PLAYWRIGHT_INFRA_FAILURE_CLASSES.
   TELESCOPE_CLICK_TARGET_MISSING = "telescope_click_target_missing"
   ```

2. In `_TelescopeQueue.submit`, after
   `if error_class == "bad_request": raise PlaywrightInfraError("telescope_bad_request", detail)`
   and before the final `raise PlaywrightInfraError("telescope_job_failed", detail)`, add:

   ```python
           # Contract mirror: service/telescope/scrape.py CLICK_TARGET_MISSING.
           if error_class == "click_target_missing":
               raise PlaywrightInfraError(TELESCOPE_CLICK_TARGET_MISSING, detail)
   ```

   ⚠️ **Decision:** Reuse `PlaywrightInfraError` with a new `failure_class` (same as
   `telescope_bad_request`) rather than a new exception type — every existing
   `except PlaywrightInfraError` still catches it, and the runner (#3) distinguishes on
   `exc.failure_class == TELESCOPE_CLICK_TARGET_MISSING`.

3. In `_post_telescope`, add keyword parameter `click_href: Optional[str] = None` after
   `debug: Optional[bool] = None`, and after the `if id is not None: body["id"] = id` lines add:

   ```python
       if click_href is not None:
           body["click_href"] = click_href
   ```

   No other change to `_post_telescope` (existing callers' request bodies stay byte-identical).

4. Directly after `get_visible_text(...)` (before `get_page_dom`), add:

   ```python
   async def click_through_visible_text(list_url: str, href: str) -> Tuple[str, str]:
       """Load list_url, click the <a> whose href attribute equals href, return (final_url, text).

       One Telescope job, no client-side retry. Raises PlaywrightInfraError —
       failure_class TELESCOPE_CLICK_TARGET_MISSING when the anchor is absent, any other
       telescope_* class on service failure. Callers log; this function does not.
       """
       _log.debug("Calling click_through_visible_text: [list_url=%s href=%s]", list_url, href)
       data = await _post_telescope(list_url, fields=["text"], click_href=href)
       text = data.get("text")
       if isinstance(text, list):
           text = "\n\n".join(t for t in text if t)
       final_url = data.get("final_url") or ""
       _log.debug(
           "Response from click_through_visible_text: final_url=%s text=%s", final_url, text
       )
       return final_url, text or ""
   ```

   ⚠️ **Decision:** `expand` / `wait_ready` / priority use the same defaults as `fetch_jd`'s
   `get_visible_text` path (`TELESCOPE_CONFIG` `default_expand=True`,
   `default_wait_ready=False`, default priority). No client-side retry loop (unlike
   `get_visible_text`'s two attempts): a missing target must not retry, and the worker already
   retries transient service failures.

5. Compile + lint `src/external/telescope.py` (see Notes); run
   `python3 -m pytest tests/component/external/test_telescope.py -q`. Commit:
   `code(AST-2023): telescope client — forward click_href, click_through_visible_text`.
   Publish per build-child.

## Ops (after merge — not a build step)

Telescope service must be redeployed for `click_href` to take effect (ticket Boundaries).

## Estimate

Confirm Chuckles estimate: 3 — agree
