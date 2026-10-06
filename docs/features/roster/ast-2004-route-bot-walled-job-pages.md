# AST-2004 — Route bot-walled job pages to BOT_BLOCKED with job_site

- **Parent:** [AST-1998 — Distinguish between BOT_BLOCKED and NO_JOBSITE](https://linear.app/astralcareermatch/issue/AST-1998)
- **Ticket:** [AST-2004](https://linear.app/astralcareermatch/issue/AST-2004)
- **Publish ref:** `sub/AST-1998/AST-2004-route-bot-walled-job-pages` (origin only)

When the decomposed `select_job_page` step (`PJL_READY`) falls through to `NO_JOBLIST`, a company whose shown job pages include a bot wall (LinkedIn sign-in wall, Cloudflare challenge, "verify you are human") is indistinguishable from one with no careers page. This ticket renames the never-written company state `BOT_BLOCK` → `BOT_BLOCKED`, promotes gazer's existing JD bot-signal check into one public helper both gazer and roster call, and reroutes that fall-through to `BOT_BLOCKED` with the first walled page's URL persisted on `company.job_site`. The select rollup counts it as a fail. Prompts, the legacy locate paths, `NO_PJL_SELECTED`, recovery, backfill, and UI are untouched.

## Canon Scope (frozen)

- `stat.logging.debug` — new bot-wall loop logs begin/end and call/response per page.
- `stat.logging.info.entity` — the `PJL_READY -> BOT_BLOCKED` progress line is the existing id-pipe line `transition_company_state` already emits via `_entity_info(short_name, "company", "state", "<from> -> <to>")`. **No new `logger.info`.**

## Verified as-is (dev @ `40d0fe70e`)

- `COMPANY_STATES["BOT_BLOCK"] = {}` (`src/utils/config.py` ~L1302); `company_state_transitions` has `("TO_WATCH", "BOT_BLOCK")`, `("JOBS_FOUND", "BOT_BLOCK")`, `("PREFILTER_PASSED", "BOT_BLOCK")` (~L4582/4591/4598). Nothing in `src/` writes `BOT_BLOCK`.
- `gazer._classify_jd` (~L137) inlines the bot check: `bot_hits = sum(... cfg.get("bot_signals", []) ...)`, `if bot_hits >= cfg.get("bot_threshold", 2): return "bot"`.
- `src/core/gazer.py` imports `src.core.roster` at module top (L20) → roster must import gazer **inside the function** (precedent: `roster.py` ~L993 `from src.core.gazer import process_gazer_batch  # lazy import avoids circular`).
- `run_select_job_page_dispatch` builds `page_url_map` / `visible_map` from `company_data.pjl_scrape_pages` (index 1..N, page order) via `_pjl_maps_from_company_data`, and calls `_find_job_page_from_assembled(..., decomposed=True)`. In decomposed mode `TRY_LINKS` never re-loops (returns retry/exhausted state), so at the final `_check_parse_results` call the maps hold exactly the pages Grace was shown.
- `_check_parse_results` final fall-through (~L2943) saves `NO_JOBLIST` with `page_option_url=company_website`; `NO_JOBLIST` ∉ `_PERSIST_PAGE_OPTION_URL_STATES` so `job_site` keeps its pre-run value.
- `run_company_task` `PJL_READY` branch: `BOT_BLOCKED` is in neither `ROSTER_CONFIG["select_job_page"]["pass_states"]` nor the local `terminal_ok` frozenset → it already reports `total_failed`. AC6 needs no logic change, only a guard comment so a future edit doesn't add it.
- `transition_company_state` validates `to_state` against `COMPANY_STATES` only (not the transitions tuple list).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Rename `BOT_BLOCK` → `BOT_BLOCKED` in `COMPANY_STATES` and the 3 `company_state_transitions` tuples; add `("PJL_READY", "BOT_BLOCKED")` | utils |
| `src/core/gazer.py` | New public `is_bot_wall(text) -> bool`; `_classify_jd` delegates to it | core |
| `src/core/roster.py` | New `_first_bot_walled_page`; `_check_parse_results` gains `page_url_map` / `visible_map` kwargs and the `BOT_BLOCKED` branch; `_find_job_page_from_assembled` passes the maps; `_PERSIST_PAGE_OPTION_URL_STATES` += `BOT_BLOCKED`; guard comment in `run_company_task` `terminal_ok` | core |

No other files. No `tests/` or bible edits (Betty owns those).

## Stage 1: State rename + shared bot detector (no routing change)

**Done when:** `rg -n '"BOT_BLOCK"' src/` returns nothing; the AC1 `python -c` assert exits 0; `rg -n "bot_signals" src/core/` returns exactly one hit (inside `is_bot_wall`); `_classify_jd` returns the same value as before for any input.

1. In `src/utils/config.py`, `COMPANY_STATES`: change the key `"BOT_BLOCK": {},` to `"BOT_BLOCKED": {},` (same position, value stays `{}` — terminal, no `batch_criteria`).
2. In `src/utils/config.py`, `company_state_transitions`: change `("TO_WATCH", "BOT_BLOCK")` → `("TO_WATCH", "BOT_BLOCKED")`, `("JOBS_FOUND", "BOT_BLOCK")` → `("JOBS_FOUND", "BOT_BLOCKED")`, `("PREFILTER_PASSED", "BOT_BLOCK")` → `("PREFILTER_PASSED", "BOT_BLOCKED")`.
3. In the same list, directly after `("PJL_READY", "NO_JOBLIST"),` add:
   ```python
           ("PJL_READY", "BOT_BLOCKED"),  # AST-2004: shown page is a bot wall at NO_JOBLIST fall-through
   ```
4. In `src/core/gazer.py`, immediately **above** `def _classify_jd`, add:
   ```python
   def is_bot_wall(text: str) -> bool:
       """True when page text trips the shared bot/challenge detector in TRACKER_CONFIG['jd_classifier'].
       Single source for JD classification and roster select_job_page (AST-2004) — do not copy the loop."""
       cfg = TRACKER_CONFIG.get("jd_classifier", {})
       text_lower = (text or "").lower()
       hits = sum(1 for s in cfg.get("bot_signals", []) if s.lower() in text_lower)
       return hits >= cfg.get("bot_threshold", 2)
   ```
   The literal `bot_signals` must appear **only** on the `hits = ...` line (AC7 greps `src/core/`). Do not write it in the docstring or any comment.
5. In `_classify_jd`, replace the two lines
   ```python
       bot_hits = sum(1 for s in cfg.get("bot_signals", []) if s.lower() in text_lower)
       if bot_hits >= cfg.get("bot_threshold", 2):
   ```
   with
   ```python
       if is_bot_wall(text):
   ```
   Keep the preceding `# --- Bot Blocked --- ...` comment and the `return "bot"` line. Check order (closed → bot → cookie → missing → ok) is unchanged.
6. Compile + lint (`python -m py_compile src/utils/config.py src/core/gazer.py` and the repo lint used by build-child §7). Run the AC1 command and `rg -n "bot_signals" src/core/`.

⚠️ **Decision:** Helper is public (`is_bot_wall`, no underscore) because a second module (roster) imports it; `_classify_jd` stays private. `text or ""` guards a `None` from a missing `visible_text`; for `str` input it is identical to the current `text.lower()`.

Commit: `code(AST-2004): stage 1 — BOT_BLOCKED rename + shared is_bot_wall`.

## Stage 2: Reroute select fall-through to BOT_BLOCKED + persist job_site

**Done when:** With `select_job_page` mocked to `NO_JOBLIST_FOUND` and a LinkedIn auth-wall page in `pjl_scrape_pages`, `run_select_job_page_dispatch` leaves the company `BOT_BLOCKED` with `job_site` = that page's URL (first walled page in page order); with no walled page it stays `NO_JOBLIST` with `job_site` unchanged; `JOBLIST_TITLES` still yields `JOBLIST_IDENTIFIED`; `run_company_task` reports `total_failed == 1` for the `BOT_BLOCKED` case; `rg -in "linkedin" src/core/roster.py` returns nothing.

1. In `src/core/roster.py`, change
   ```python
   _PERSIST_PAGE_OPTION_URL_STATES = frozenset({
       "WATCH", "NO_OPENINGS", "CANNOT_PARSE_JOB_SITE", "JOBSITE_SCRAPE_ISSUE",
   })
   ```
   to add `"BOT_BLOCKED",` after `"JOBSITE_SCRAPE_ISSUE",` (same line or next line, matching the existing style).
2. In `src/core/roster.py`, immediately **above** `async def _check_parse_results`, add:
   ```python
   def _first_bot_walled_page(page_url_map: Dict[int, str], visible_map: Dict[int, str]) -> str:
       """URL of the first shown page (page order) whose visible text is a bot wall; '' when none (AST-2004)."""
       from src.core.gazer import is_bot_wall  # lazy import avoids circular (gazer imports roster)
       pages = sorted(page_url_map)
       logger.debug("Beginning bot-wall check loop on %s items", len(pages))
       checked = 0
       for n in pages:
           checked += 1
           logger.debug("Calling is_bot_wall: page=%s url=%s", n, page_url_map[n])
           walled = is_bot_wall(visible_map.get(n, ""))
           logger.debug("Response from is_bot_wall: page=%s walled=%s", n, walled)
           if walled:
               logger.debug("End bot-wall check loop after %s items", checked)
               return page_url_map[n]
       logger.debug("End bot-wall check loop after %s items", checked)
       return ""
   ```
   No domain names, no host checks — detection is content-only (AC8).
3. In `_check_parse_results`, add two keyword parameters **after** `decomposed: bool = False,`:
   ```python
       page_url_map: Optional[Dict[int, str]] = None,
       visible_map: Optional[Dict[int, str]] = None,
   ```
   Defaults keep every existing caller (including tests calling it directly) working unchanged.
4. In `_check_parse_results`, immediately **before** the final fall-through `_save_company(... state="NO_JOBLIST", page_option_url=company_website, raw_response=result)`, insert:
   ```python
       # AST-2004: a bot-walled shown page is the real reason no job list was found (decomposed select only).
       walled_url = _first_bot_walled_page(page_url_map or {}, visible_map or {}) if decomposed else ""
       if walled_url:
           _save_company(short_name=short_name, company_website=company_website,
                         state="BOT_BLOCKED", page_option_url=walled_url, raw_response=result)
           logger.debug("Response from select_job_page: %s -> BOT_BLOCKED job_site=%s", response_type, walled_url)
           return {"short_name": short_name, "state": "BOT_BLOCKED", "job_site": walled_url, "response_type": response_type}
   ```
   Do **not** pass `suppress_job_site` here (decomposed `suppress` would blank `job_site`; this state must write it). Leave the existing `NO_JOBLIST` save/return lines below it exactly as they are. Do **not** add a `logger.info` — `transition_company_state` (called by `_save_company`) emits the id-pipe `company state: PJL_READY -> BOT_BLOCKED` line.
5. In `_find_job_page_from_assembled`, in the final `return await _check_parse_results(...)` call, add `page_url_map=page_url_map, visible_map=visible_map,` after `decomposed=decomposed,`. No other change to that function — the `JOBLIST_TITLES` branch returns before this call (AC4), and `JOBLIST_NO_JOBS` / `JOBSITE_SCRAPE_ISSUE` return inside `_check_parse_results` before the new branch.
6. In `run_company_task`, `PJL_READY` branch, add one comment line directly above `terminal_ok = frozenset({`:
   ```python
               # BOT_BLOCKED deliberately absent: bot-blocked is fail-only (AST-1751 / AST-2004).
   ```
   No logic change — `BOT_BLOCKED` already falls to `total_failed`.
7. Compile + lint (`python -m py_compile src/core/roster.py` and the repo lint per build-child §7). Run `rg -n '"BOT_BLOCK"' src/`, `rg -n "bot_signals" src/core/`, `rg -in "linkedin" src/core/roster.py`.

⚠️ **Decision:** The `BOT_BLOCKED` branch is gated on `decomposed`. Only the `PJL_READY` select step (`run_select_job_page_dispatch`, the only `decomposed=True` caller) changes. The legacy `TO_WATCH` / `JOBS_FOUND` / `PREFILTER_PASSED` locate path (`decomposed=False`) also reaches this fall-through, but the ticket scopes the reroute to "the select step" and adds only the `PJL_READY → BOT_BLOCKED` transition; leaving legacy behavior byte-identical keeps blast radius at one path.

⚠️ **Decision:** Pages are checked in ascending page index (`sorted(page_url_map)`), which is `pjl_scrape_pages` order — so the first walled page wins (AC5). A page with a URL but no visible text is checked against `""` and is never a wall.

⚠️ **Decision:** Every response_type that reaches the fall-through (`NO_JOBLIST_FOUND` or any unrecognized value) gets the bot check, matching the parent's as-is ("`NO_JOBLIST_FOUND` (or any unrecognized response_type)"). Early `NO_JOBLIST` exits in `_find_job_page_from_assembled` (`SELECT_FAILED`, invalid parse, legacy TRY_LINKS exits) are untouched.

Commit: `code(AST-2004): stage 2 — reroute bot-walled NO_JOBLIST to BOT_BLOCKED`.

## Acceptance criteria → stage map

| AC | Covered by |
|----|------------|
| 1 Rename complete | Stage 1 steps 1–2 |
| 2 Bot wall → `BOT_BLOCKED` + URL | Stage 2 steps 1, 2, 4, 5 |
| 3 No wall → `NO_JOBLIST`, `job_site` unchanged | Stage 2 step 4 (falls through to untouched code) |
| 4 Found job list wins | Unchanged `JOBLIST_TITLES` branch (Stage 2 step 5 note) |
| 5 First walled page wins | Stage 2 step 2 (sorted, return on first hit) |
| 6 Rollup counts as fail | Existing `run_company_task` logic; Stage 2 step 6 guard comment |
| 7 One bot detector | Stage 1 steps 4–5 |
| 8 No host-list shim | Stage 2 step 2 (content-only) |

## Execution contract

Execute steps in order; do not add files, helpers, or config. If any referenced code has drifted from the as-is above (signature, line content, an extra `bot_signals` hit in `src/core/`), stop and comment on the parent per build-child.

## Estimate

Confirm Chuckles estimate: 2 — agree
