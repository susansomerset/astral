# AST-1230 — Search-page batch creation

**Linear:** [AST-1230](https://linear.app/astralcareermatch/issue/AST-1230/search-page-batch-creation-surfer-batch-durable-worklist-state-and)
**Parent:** [AST-1169](https://linear.app/astralcareermatch/issue/AST-1169/surfer-batch-durable-worklist-state-and-batch-scoped-intake) — Surfer batch — durable worklist state and batch-scoped intake
**Publish ref:** `origin/sub/AST-1169/AST-1230-search-page-batch-creation`

When classification has already decided a page is a recognized job search page, baseline-extract target listing URLs from the submitted markup, create a Surfer batch via `create_surfer_batch` (AST-1229), and return `batch_id` + the non-empty URL list in an envelope-ready dict. Owns Style D per-URL found/recorded when `debug=True`, and the config copy / error codes for empty extraction and the one-active-batch `ValueError` hand-off from AST-1229. Does **not** own classification, the two-phase HTTP surface (AST-1226 / AST-1228), batch-scoped listing posts or remaining-work query (AST-1231), or site-aware discovery quality (AST-1171).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Extend `SURFER_BATCH_CONFIG` with baseline extract + candidate-facing message / error-code keys; document in module header | utils |
| `src/core/page_intake.py` | Add `create_batch_from_search_page` (+ private baseline extract helper); Style D per URL | core |

No new Flask routes / blueprints (AST-1228 wires this function into the fixed envelope). No changes to `src/core/surfer.py` beyond calling existing `create_surfer_batch` / relying on `database.get_surfer_batch`. No `tests/` or bible (Betty after Code Complete). No AST-1171 site heuristics.

**Build precondition:** `src/core/page_intake.py` must already exist from AST-1227 (`ingest_recognized_listing`). After `sync-child.sh`, if that file is missing, **STOP** — comment on AST-1230 naming the missing module and that AST-1168 product (at least AST-1227) must be on the epic line / `origin/dev` before build can proceed. Do **not** recreate AST-1227's ingest function and do **not** self-cherry-pick.

## Stage 1: Config — baseline extract + messages

**Done when:** `SURFER_BATCH_CONFIG` exposes the keys below; module docstring still lists the block; existing AST-1229 asserts still pass; new asserts below pass; `python3 -m py_compile src/utils/config.py` succeeds.

1. In `src/utils/config.py` module docstring `Config sections:` line for `SURFER_BATCH_CONFIG`, append that the block also holds search-page baseline link extract + envelope message/error codes (AST-1230).

2. Inside the existing `SURFER_BATCH_CONFIG` dict (after `"initial_url_outcome"`), add:

```python
    # AST-1230: baseline <a href> harvest from a classified search page (not AST-1171 quality).
    "baseline_link_schemes": ("http", "https"),
    # Drop hrefs whose casefolded absolute URL contains any of these fragments.
    "baseline_link_exclude_substrings": (
        "mailto:",
        "javascript:",
        "unsubscribe",
        "/preferences",
        "/email-settings",
    ),
    # When True, omit the search page's own absolute URL from the worklist.
    "baseline_exclude_page_url": True,
    # Candidate-facing / envelope strings (AST-1228 renders; AST-1230 owns the literals).
    "messages": {
        "search_batch_created": "Got it — here are the jobs from this search.",
        "active_batch_exists": "You already have a Surfer run in progress. Finish or cancel it before starting another.",
        "no_target_urls": "I recognized a job search page, but I couldn't find any job links on it.",
    },
    # Stable machine codes for callers (HTTP mapping / tests). Do not invent ad hoc strings at raise sites.
    "error_codes": {
        "active_batch_exists": "active_surfer_batch_exists",
        "no_target_urls": "no_target_urls",
    },
```

3. After the existing AST-1229 asserts on `SURFER_BATCH_CONFIG`, add:

```python
assert set(SURFER_BATCH_CONFIG["baseline_link_schemes"]) <= {"http", "https"}
assert isinstance(SURFER_BATCH_CONFIG["baseline_link_exclude_substrings"], tuple)
assert isinstance(SURFER_BATCH_CONFIG["baseline_exclude_page_url"], bool)
assert set(SURFER_BATCH_CONFIG["messages"]) == {
    "search_batch_created",
    "active_batch_exists",
    "no_target_urls",
}
assert set(SURFER_BATCH_CONFIG["error_codes"]) == {
    "active_batch_exists",
    "no_target_urls",
}
assert all(isinstance(v, str) and v.strip() for v in SURFER_BATCH_CONFIG["messages"].values())
assert all(isinstance(v, str) and v.strip() for v in SURFER_BATCH_CONFIG["error_codes"].values())
```

⚠️ **Decision — extend `SURFER_BATCH_CONFIG`, do not invent `PAGE_INTAKE_CONFIG`:** Classification status vocabulary and not-recognized copy are AST-1226. This ticket only needs extract filters + the three strings tied to search→batch creation. One Surfer batch block stays the single source for those literals (`pattern.config.config-block`).

⚠️ **Decision — baseline excludes are deliberately thin:** Site-aware allowlists / ATS heuristics are AST-1171. Reusing the full `METEORITE_EMAIL_INGEST_CONFIG["link_exclude_substrings"]` set would couple Surfer search harvest to email hygiene without ownership. Keep a short Surfer-owned tuple; AST-1171 may replace or wrap this later via plan change.

## Stage 2: Core — `create_batch_from_search_page`

**Done when:** Given a candidate + search-page `page_url` + HTML with at least one extractable http(s) job link, the function returns a non-empty `urls` list and a `batch_id` whose `database.get_surfer_batch(batch_id)` row carries those URLs with `initial_url_outcome`; a second create while that batch is non-terminal raises with the active-batch error code; HTML with zero surviving links raises with the no-target-urls code; `debug=True` emits Style D per URL (found then recorded); `debug=False` emits no Style D; no Flask routes added; `python3 -m py_compile src/core/page_intake.py` succeeds.

1. **Precondition check (build-time):** Confirm `src/core/page_intake.py` exists and already defines `ingest_recognized_listing` (AST-1227). If missing → STOP (see Files Changed).

2. Update the module docstring to state that the module also owns search-page → Surfer batch creation (AST-1230); classification and HTTP surface remain AST-1226 / AST-1228; discovery quality is AST-1171.

3. Add imports (keep layer rules — **no** `src.ui`, **no** `src.external`):

```python
from urllib.parse import urljoin, urlparse, urldefrag

from src.core.surfer import create_surfer_batch
from src.data import database  # only if needed for post-create get; prefer create_surfer_batch return
from src.utils.config import SURFER_BATCH_CONFIG
```

`get_logger` is already used by `ingest_recognized_listing` — reuse the same pattern (`get_logger(__name__)` inside the function or module-level; match the existing file style from AST-1227).

4. Add private helper **below** public functions (public-then-helpers), or immediately above the new public function if the file is still short — finished layout must keep public API first:

```python
def _baseline_extract_target_urls(page_url: str, html_body: str) -> list[str]:
    """Ordered unique absolute http(s) hrefs from search-page markup (baseline only)."""
```

   Behavior (literal):

   - Lazy-import `BeautifulSoup` inside the helper (same B1 pattern as `gazer._meteorite_email_candidate_links`).
   - `base = (page_url or "").strip()` — caller already validated non-empty; still tolerate and treat empty base as no resolution (absolute hrefs only survive).
   - `schemes = {s.casefold() for s in SURFER_BATCH_CONFIG["baseline_link_schemes"]}`.
   - `excludes = tuple(s.casefold() for s in SURFER_BATCH_CONFIG["baseline_link_exclude_substrings"])`.
   - Parse `html_body` with `BeautifulSoup(html_body, "html.parser")`.
   - For each `a[href]`:
     - Raw href = strip of `tag.get("href")` or `""`; skip empty.
     - Resolve: `absolute = urljoin(base, href)` when `base` else `href`.
     - Strip fragment: `absolute = urldefrag(absolute).url` (keep query string).
     - Parse with `urlparse`; scheme must be in `schemes`.
     - Skip if any exclude fragment is in `absolute.casefold()`.
     - If `SURFER_BATCH_CONFIG["baseline_exclude_page_url"]` and `base`: also skip when `urldefrag(absolute).url.casefold() == urldefrag(base).url.casefold()`.
     - Dedupe with a `seen` set of the absolute string; append first occurrence to `out`.
   - Return `out` (may be empty — caller raises).

⚠️ **Decision — resolve relative hrefs with `urljoin(page_url, …)`:** Search captures often use path-only links. Email meteorite extract keeps absolute hrefs only; Surfer search pages need resolution against the captured page URL. Do **not** call Playwright or `src.external`.

⚠️ **Decision — do not share `_meteorite_email_candidate_links`:** That helper is email-scoped and does not resolve relatives. Copy the shape, do not import gazer into page_intake (avoids core↔core coupling and email config bleed).

5. Add public function:

```python
def create_batch_from_search_page(
    candidate_id: str,
    page_url: str,
    html_body: str,
    *,
    debug: bool = False,
) -> dict[str, Any]:
    """Baseline-extract URLs from a classified search page and create a Surfer batch.

    Caller is responsible for having classified the page as a recognized job search
    page (AST-1226 / AST-1228). This function does not classify or fetch.

    Returns envelope-ready fields for the fixed page_intake shape (AST-1168 AC6):
      {
        "batch_id": str,
        "urls": list[str],          # non-empty; same order as surfer_batch worklist
        "message": str,             # SURFER_BATCH_CONFIG["messages"]["search_batch_created"]
        "surfer_batch": dict,       # create_surfer_batch / get_surfer_batch row
      }

    Raises:
      ValueError: bad input; or no extractable URLs (args: message, with .error_code);
                  or create_surfer_batch active-batch conflict (same pattern).
    """
```

6. Validation (raise `ValueError` — same bar as `ingest_recognized_listing`):

   - Strip `candidate_id`; empty → `ValueError("candidate_id is required")`.
   - Strip `page_url`; empty → `ValueError("page_url is required")`.
   - `html_body` must be a non-empty stripped string → else `ValueError("html_body is required")`.

7. Logger: `log = get_logger(__name__); log.set_debug_flag(debug)`.

8. Extract: `urls = _baseline_extract_target_urls(page_url, html_body)`. If not `urls`:

   - Build `err = ValueError(SURFER_BATCH_CONFIG["messages"]["no_target_urls"])`.
   - Set `err.error_code = SURFER_BATCH_CONFIG["error_codes"]["no_target_urls"]` (attribute on the exception instance).
   - Raise `err`.

9. Debug — **found** (per URL, Style D §1.5.1):

   - `total = len(urls)`.
   - For each `(i, url)` in `enumerate(urls, start=1)`:
     - `log.debug_index(func="page_intake.create_batch_from_search_page", index=i, total=total, identifier=url[:80], outcome="found")`
     - `log.debug_detail(f"page_url={page_url[:80]} candidate_id={candidate_id}")`

   Only when `debug=True` (gated by `set_debug_flag` + only emit inside `if debug:` blocks, matching `ingest_recognized_listing`).

10. Create batch:

```python
    try:
        batch = create_surfer_batch(candidate_id, urls, debug=debug)
    except ValueError as exc:
        msg = str(exc)
        # AST-1229: "Candidate {id} already has a non-terminal Surfer batch: {batch_id}"
        if "already has a non-terminal Surfer batch" in msg:
            err = ValueError(SURFER_BATCH_CONFIG["messages"]["active_batch_exists"])
            err.error_code = SURFER_BATCH_CONFIG["error_codes"]["active_batch_exists"]
            err.__cause__ = exc
            raise err from exc
        raise
```

⚠️ **Decision — map only the active-batch conflict to config copy:** Other `ValueError`s from `create_surfer_batch` (empty urls after its own clean — should not happen if we pass non-empty; missing candidate) propagate unchanged so callers see the real cause. HTTP status mapping for `error_code` values is AST-1228's job when it wires this function; this ticket defines the codes + messages.

11. Debug — **recorded** (per URL):

   - For each `(i, url)` in `enumerate(urls, start=1)`:
     - `log.debug_index(..., index=i, total=total, identifier=url[:80], outcome="recorded")`
     - `log.debug_detail(f"batch_id={batch['batch_id']} outcome={SURFER_BATCH_CONFIG['initial_url_outcome']}")`

12. Return:

```python
    return {
        "batch_id": batch["batch_id"],
        "urls": [entry["url"] for entry in batch["urls"]],
        "message": SURFER_BATCH_CONFIG["messages"]["search_batch_created"],
        "surfer_batch": batch,
    }
```

   Assert by construction: `urls` non-empty and equal in order to the worklist URLs on `batch`. Retrievability AC: caller (or Betty) may `database.get_surfer_batch(batch_id)` afterward — do not add a new get helper.

13. Do **not** add Flask routes, outcome-store writes, classification calls, or changes to `ingest_recognized_listing`. Do **not** mark URLs `delivered` / `success` here (AST-1231).

14. Compile: `python3 -m py_compile src/core/page_intake.py src/utils/config.py`.

**Done when (recheck):**

- Fresh candidate + HTML with two distinct `/jobs/…` links → return has `batch_id`, `urls` length 2, and `database.get_surfer_batch(batch_id)["urls"]` has those URLs with `pending` outcomes.
- Same candidate, second call while batch RUNNING → `ValueError` whose `error_code` is `active_surfer_batch_exists` and message equals config `messages.active_batch_exists`.
- HTML with only `mailto:` / self page_url links → `ValueError` with `error_code` `no_target_urls`.
- `debug=True` → per-URL found then recorded index headers; `debug=False` → no Style D lines.

## Self-Assessment

**Scope:** `Single-Component` — config keys on the existing Surfer batch block plus one new core entry on `page_intake.py` calling AST-1229 `create_surfer_batch`; no UI routes.

**Conf:** `high` — mirrors AST-1227's classify-then-call pattern and gazer's baseline href harvest shape; AST-1229 create/pointer contract is already on the epic ftr line.

**Risk:** `Medium` — empty or overly aggressive baseline extract would block a recognized search page (AC1); active-batch mapping mistakes would confuse the extension. Dispatcher claim paths and listing ingest are untouched. Site-specific miss rates are accepted until AST-1171 (explicit boundary).

## Rules check (plan-child §8)

- **§1.3 DRY:** Extract helper is local to page_intake; does not fork `create_surfer_batch`. Message/error-code literals live only in `SURFER_BATCH_CONFIG`.
- **§2.1 config:** Named block extension; no env for these literals; no hardcoded exclude sets in branches.
- **§2.4 batch:** Uses AST-1229 `surfer-{uuid}` ids via `create_surfer_batch`; batch_id returned for envelope; does not touch dispatcher `job.batch_id` claim locks.
- **§2.6 state:** No new status transitions; initial RUNNING + pending URL outcomes come from existing create path.
- **§3.3 imports:** core → surfer + utils (+ bs4 lazy); no `ui` → `data` shortcut; no `external`.
- **§3.5 naming:** `create_batch_from_search_page` / `_baseline_extract_target_urls`; snake_case.
- **§1.5.1 debug:** `debug: bool = False` threaded; Style D only when `debug=True`; per-URL index headers + working detail; no aggregate-only substitute.
- **Import direction:** Thin HTTP remains AST-1228; this ticket is core-only like AST-1227.

## Envelope contract for AST-1228 (reference only — not this ticket's stages)

When the two-phase surface resolves classification to a recognized search page, it must call `create_batch_from_search_page(...)` and place `batch_id`, `urls`, and `message` into the fixed envelope. On `ValueError` with `error_code` in `SURFER_BATCH_CONFIG["error_codes"]`, use `str(exc)` as the envelope message (already config copy). Classification **status** strings remain AST-1226. This section is documentation for the sibling, not build scope here.
