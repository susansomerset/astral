<!-- linear-archive: AST-2004 archived 2026-10-13 -->

## Linear archive (AST-2004)

**Archived:** 2026-10-13  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2004/route-bot-walled-job-pages-to-bot-blocked-with-job-site-distinguish  
**Status at archive:** Archive  
**Project:** Astral Roster  
**Assignee:** ada  
**Priority / estimate:** None / 2  
**Parent:** AST-1998 — Distinguish between BOT_BLOCKED and NO_JOBSITE  
**Blocked by / blocks / related:** parent: AST-1998; related: AST-1994

### Description

## What this implements

Renames the company bot state to `BOT_BLOCKED`, makes the existing bot-signal check reusable, and reroutes the `select_job_page` `NO_JOBLIST` fall-through to `BOT_BLOCKED` with the blocked URL on `job_site`, counted as a fail. Does not touch prompts, the legacy locate paths' early exits, `NO_PJL_SELECTED`, recovery, or UI.

## Citations

`stat.logging.debug`, `stat.logging.info.entity`.

## Scope

* `src/utils/config.py` — **modified** — rename company state `BOT_BLOCK` → `BOT_BLOCKED` in `COMPANY_STATES` and `company_state_transitions`; add the `PJL_READY → BOT_BLOCKED` transition. Modified `COMPANY_STATES` entry (rename key `BOT_BLOCK` → `BOT_BLOCKED`, still `{}` — terminal); modified `company_state_transitions` (rename the three existing `BOT_BLOCK` tuples; add one tuple for `PJL_READY` → `BOT_BLOCKED`). No new config block — detection reads the existing `TRACKER_CONFIG["jd_classifier"]` bot signals/threshold.
* `src/core/gazer.py` — **modified** — make the existing bot-signal check reusable by roster (behavior of JD classification unchanged). New public helper (or promoted function) that answers "is this page text a bot wall?" using the same `bot_signals` / `bot_threshold` logic `_classify_jd` uses today; `_classify_jd` delegates to it so the two can never drift.
* `src/core/roster.py` — **modified** — reroute the select step's `NO_JOBLIST` fall-through to `BOT_BLOCKED` when a shown page is a bot wall; persist `job_site` for `BOT_BLOCKED`. Modified `_find_job_page_from_assembled` / `_check_parse_results` so the final `NO_JOBLIST` fall-through has the shown pages' URL + visible text available and, when the first bot-walled page is found, saves `BOT_BLOCKED` with that page's URL as `page_option_url`; modified `_PERSIST_PAGE_OPTION_URL_STATES` to include `BOT_BLOCKED` so `job_site` is written; modified the `PJL_READY` branch of `run_company_task` so `BOT_BLOCKED` is not in the `terminal_ok` set (reports `total_failed`).

## Acceptance criteria

1. **Rename is complete.** `rg -n '"BOT_BLOCK"' src/` returns nothing, and `python -c "from src.utils.config import COMPANY_STATES as C; assert 'BOT_BLOCKED' in C and 'BOT_BLOCK' not in C"` exits 0. Fail: any hit, or the assert raises.
2. **Bot wall →** `BOT_BLOCKED` **+ URL.** Component test: company in `PJL_READY` whose `pjl_scrape_pages` holds page 1 = careers-less homepage text and page 2 = `https://www.linkedin.com/company/acme/jobs` with LinkedIn auth-wall text ("New to LinkedIn? Join now" … "Sign in with Email"); `select_job_page` mocked to `{"response_type": "NO_JOBLIST_FOUND", "selected_page": 0}`. After `run_select_job_page_dispatch`: `company.state == "BOT_BLOCKED"` and `company.job_site == "https://www.linkedin.com/company/acme/jobs"`. Fail: state `NO_JOBLIST`, or `job_site` empty / the company website.
3. **No bot wall → unchanged** `NO_JOBLIST`**.** Same test with no page reaching the bot threshold: `state == "NO_JOBLIST"` and `job_site` equals its pre-run value. Fail: `BOT_BLOCKED`, or `job_site` changed.
4. **Found job list wins.** Same pages, `select_job_page` mocked to `JOBLIST_TITLES` on page 1: `state == "JOBLIST_IDENTIFIED"`. Fail: `BOT_BLOCKED`.
5. **First walled page wins.** Two walled pages (2 and 3): `job_site` is page 2's URL. Fail: page 3's URL or empty.
6. **Rollup counts it as a fail.** `run_company_task` on the AC2 fixture returns `total_failed == 1`, `total_passed == 0`, `total_errors == 0`. Fail: any other split.
7. **One bot detector, not two.** `_classify_jd` and the roster check both go through the same gazer helper: `rg -n "bot_signals" src/core/` returns exactly one hit (in that helper). Fail: a second copy of the signal loop (e.g. inlined in `roster.py`).
8. **No host-list shim.** `rg -in "linkedin" src/core/roster.py` returns nothing. Fail: any hit — detection must be content-based, not a hard-coded domain list (Susan chose option (a)).

## Boundaries

Single child — owns all of the parent's scope. No backfill of existing `NO_JOBLIST` rows (Susan: new rows only). No `select_job_page` prompt change, no domain list, no UI, no recovery path for `BOT_BLOCKED` companies. Note: in-flight [AST-1994](https://linear.app/astralcareermatch/issue/AST-1994) touches `gazer.fetch_job_pages_batch` and `roster._merge_pjl_scrape_record` — different functions; merge `origin/dev` if it lands first.

## Notes for planning

Citations: `stat.logging.debug`, `stat.logging.info.entity`. Susan's resolved decisions: detection = existing JD bot-signal check (option a); rename `BOT_BLOCK` → `BOT_BLOCKED`, no data migration; new rows only. Estimate: 2.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1998-bot-blocked-vs-no-joblist`, child `sub/AST-1998/<child-segment>`. Created at dispatch-parent.

### Comments

#### radia — 2026-10-06T05:36:07.412Z
[code-rubric] PROCEED (Commit: 0e59c7a7) logging + reroute match plan

#### betty — 2026-10-06T05:33:45.516Z
`origin/sub/AST-1998/AST-2004-route-bot-walled-job-pages` @ `0e59c7a71` · bot-wall tests + snapshot revised

#### joan — 2026-10-06T05:26:35.283Z
[plan-rubric] PROCEED (Commit: ecc3bd6c2) logging + reroute plan solid

#### ada — 2026-10-06T05:24:58.681Z
`origin/sub/AST-1998/AST-2004-route-bot-walled-job-pages` @ `ecc3bd6c2` · plan ready, two stages

---

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

## Joan validate

[plan-rubric]
**Ticket:** AST-2004
**Overall:** APPROVED
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51
**Publish ref:** `ecc3bd6c24529fa04e68edc0063a5c047513c15c` (`sub/AST-1998/AST-2004-route-bot-walled-job-pages`)

## Canon scores

stat.logging.debug | A | | Loop begin/end plus Calling/Response around `is_bot_wall` in `_first_bot_walled_page`; no call-site gating.
stat.logging.info.entity | A | | Explicitly defers `PJL_READY → BOT_BLOCKED` to `transition_company_state` / `_entity_info`; no new `logger.info`.

## Traceability

AC1→Stage1; AC2–AC3, AC5–AC6→Stage2; AC4→unchanged `JOBLIST_TITLES` path; AC7→Stage1 helper+delegate; AC8→Stage2 content-only helper — parent Purpose/Functional 1–6 and child `## Scope` (three files only) fully covered; no orphan stages.

## Findings

(none — no `fix-now`; no `discuss` blocking)

**R6 (spot-check):** Plan matches parent/child definition (rename, shared detector, decomposed-only reroute, `job_site` persist, fail rollup, boundaries). `decomposed=False` legacy fall-through left on `NO_JOBLIST` is an explicit, scoped decision aligned with child scope and parent out-of-scope on legacy locate paths.

**Gates:** AST-2004 `Plan Ready`, assignee Joan; no `[plan-discuss]` rounds (0/2).

context_tokens≈42000

[plan-rubric] PROCEED (Commit: ecc3bd6c2) logging + reroute plan solid

## Review

- **Branch:** `sub/AST-1998/AST-2004-route-bot-walled-job-pages`
- **Stage 1:** `6d13bce65` — `BOT_BLOCKED` rename + shared `is_bot_wall`
- **Stage 2:** `f7680ff89` — reroute bot-walled `NO_JOBLIST` to `BOT_BLOCKED`
- **Build notes:** executed as planned, no deviations. Repo has no configured linter; checks were `py_compile`, `git diff --check`, and the AC1/AC7/AC8 greps (all pass). In-memory mock smoke (not committed) matched AC2–AC6.

## Radia review

[code-rubric]
**Ticket:** AST-2004
**Publish ref:** `0e59c7a7163135acaa1c3b216104925d8c095af6` (`origin/sub/AST-1998/AST-2004-route-bot-walled-job-pages`)
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| stat.logging.debug | A | | |
| stat.logging.info.entity | A | | |

## Column diff vs plan stage

(aligned) — Joan: `stat.logging.debug` A, `stat.logging.info.entity` A; code review matches.

## Frame diff

(none)

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **sibling test carry:** `docs/test-bible/core/agent.md`, `docs/test-bible/core/consult.md`, `tests/component/core/test_agent.py`, `tests/component/core/test_consult.py` — AST-2001 / AST-1996 decode-line isolation (merge-tests from `origin/tests`); not AST-2004 product scope.
- **sibling test carry:** Tip commit is `merge-tests(AST-2004): origin/tests bb791a2bd` — expected Betty publish shape; product delta remains the three planned `src/` files.
- **qa manifest note:** `docs/test-bible/core/roster.md` documents 74 pre-existing component reds unchanged with/without this pass — out of AST-2004 scope; UAT / broader harness should not treat them as regressions from this child.

## What's solid

- Stage 1–2 match the plan: `BOT_BLOCK` → `BOT_BLOCKED`, `is_bot_wall` single detector, decomposed-only `_first_bot_walled_page` + `_check_parse_results` branch, `BOT_BLOCKED` in `_PERSIST_PAGE_OPTION_URL_STATES`, guard comment on `terminal_ok`.
- `_first_bot_walled_page` implements the frozen debug contract (loop begin/end, per-page Calling/Response around `is_bot_wall`) without call-site `if debug` gating.
- `BOT_BLOCKED` persistence uses `_save_company` → `transition_company_state` → `_entity_info(..., "company", "state", "<from> -> BOT_BLOCKED")`; no new `logger.info` in the diff.
- Component tests in the diff cover AC1–AC8 intent (including legacy `decomposed=False` guard).

## Recommended actions (downstream only — not executed here)

- Chuckles: append this artifact to `docs/features/roster/ast-2004-route-bot-walled-job-pages.md`, commit `docs(AST-2004): Radia review — clean`, push sub branch, post slim upshot `--as radia`, move to **Review Posted**; datt **§3h** PROCEED → **User Testing** (no fix-now).
- If Susan wants legacy locate paths (`decomposed=False`) to also route bot walls to `BOT_BLOCKED`, that is a **new** product decision (explicitly excluded in plan); no action on this ticket.

context_tokens≈28000

[code-rubric] PROCEED (Commit: 0e59c7a7) logging + reroute match plan
