# AST-1752 — Meteorite scrape: closed/missing content verdicts must be FAIL (LINK_EXPIRED), not ERROR

<!-- linear-archive: AST-1752 archived 2026-10-02 -->

## Linear archive (AST-1752)

**Archived:** 2026-10-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1752/meteorite-scrape-closedmissing-content-verdicts-must-be-fail-link  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** AST-1721 — Astral Telescope — stateless headless-scraping microservice (per-URL)  
**Blocked by / blocks / related:** parent: AST-1721

### Description

\[bug\] `run_scrape_meteorite()` routes gazer's content classification (`closed`, `missing`) into the same `SCRAPE_ERROR` state / `total_errors` counter as genuine Telescope technical failures (exceptions, timeouts, 5xx, connectivity, no-usable-link). Nothing actually broke when a job posting is closed — it's a normal, expected outcome — but it's logged and counted identically to a real system fault.

```
[2026-09-21 05:17:54] WARNING src.core.meteorite: meteorite 92 for somerset — scrape_closed signal='no longer available' text_len=410 final_url=https://www.dice.com/job-detail/c5a9ffeb-c9c9-44a2-b0e4-59668a8d18b3
  This row is ERROR
...
[2026-09-21 05:17:54] INFO src.core.dispatcher: somerset | dispatch meteorite task completed: scrape_meteorite pass:0 fail:0 error:5 (batch: scrape_meteorite-5f65eeaa-c325-45f0-b6ad-5413ab7b843d)
```

AST-1750 (diagnostic detail) and AST-1751 (stop double-counting error rows as also fail) both landed correctly and are visible working as-designed in the log above (`signal=`/`text_len=`/`final_url=` present; `fail:0` not leaking). Neither ticket was wrong — they exposed that `closed`/`missing` were never supposed to be in the error bucket at all.

Separately: every non-pass row in `run_scrape_meteorite` — fail-bucket (`BOT_BLOCKED`) and error-bucket (`SCRAPE_ERROR`) alike — logs through the same `_row_miss()` → `logger.warning()` path. Log level carries no signal about which bucket a row landed in; only real unhandled exceptions get true ERROR-level logging (`logger.exception`). A WARNING-level line whose own text reads "This row is ERROR" is self-contradictory and part of why this was confusing to debug from the logs alone.

## As-is

* `_classify_jd()` (`src/core/gazer.py`) content verdicts `bot`/`cookie` → `blocked` → `BOT_BLOCKED` (fail, correct).
* `_classify_jd()` content verdicts `closed`/`missing` → `SCRAPE_ERROR` (error, **wrong** — these are content judgments, not technical faults).
* Log level (`logger.warning` via `_row_miss`) is identical for fail-bucket and error-bucket soft outcomes; only real exceptions get ERROR-level logging.
* No terminal meteorite state exists for "we're confident this link will never yield a contact" that isn't `BOT_BLOCKED` (which wrongly implies bot-recovery via the Estelle DM/nag/paste flow — nothing to paste for a closed posting).

## To-be

* `_classify_jd()`'s output can only ever resolve to **pass or fail** — never error. Error is reserved exclusively for genuine Telescope-level technical faults (exception, timeout, HTTP 5xx, connectivity) and rows with no usable link to attempt at all.
* New terminal `METEORITE_STATES` entry: `LINK_EXPIRED` — covers both `closed` and `missing` content verdicts (page loaded fine-but-declared-closed, or thin/wrong/unreadable page). Not bot-recoverable; must NOT be a trigger state for `METEORITE_BOT_BLOCKED_NOTIFY_CONFIG` (no Estelle paging for a dead posting).
* `run_scrape_meteorite`: `closed`/`missing` → state `LINK_EXPIRED`, counted in `total_failed` (not `total_errors`). `BOT_BLOCKED` behavior unchanged.
* Fail-bucket and error-bucket rows should be visually distinguishable by log level, not just by counter: keep fail-bucket at WARNING (as today), but genuinely-erroring rows should not also claim "This row is ERROR" from inside a `.warning()` call — either bump those to `logger.error()`/`logger.exception()`, or otherwise make the level match the bucket it's landing in.

## Proposed change

- [X] `src/utils/config.py` — `METEORITE_STATES`: add `LINK_EXPIRED` terminal state (`prior_states: ["SCRAPE_LINK"]`); not added to `ABANDONED` prior_states (stale cleanup stays `BOT_BLOCKED` and `SCRAPE_ERROR`); update `set(METEORITE_STATES)` assertion.
- [X] `src/utils/config.py` — `METEORITE_INGRESS_DISPATCH_CONFIG["scrape_page_status_states"]`: `"closed"` and `"missing"` → `"LINK_EXPIRED"` (currently both → `"SCRAPE_ERROR"`); update the allowed-values assert to include `LINK_EXPIRED`.
- [X] `src/core/meteorite.py::run_scrape_meteorite` — soft-fail branch for `closed`/`missing`: write state `LINK_EXPIRED`, bump `total_failed` (not `total_errors`). Keep existing WARNING-level `_row_miss` logging for this branch (text should say "This row is LINK_EXPIRED", not "This row is ERROR"). True exception / no-link / no-content branches keep `SCRAPE_ERROR` + `total_errors`, Soft `SCRAPE_ERROR` warnings say `This row is SCRAPE_ERROR`. Thrown faults stay `logger.exception`.
- [X] Confirm `LINK_EXPIRED` is excluded from `METEORITE_BOT_BLOCKED_NOTIFY_CONFIG["trigger_state"]` (already scoped to `BOT_BLOCKED` only — just needs a test asserting no notify fires for `LINK_EXPIRED`).
- [X] `docs/test-bible/core/meteorite.md` — new section for `LINK_EXPIRED` fail bucket; note relationship to AST-1751's fail/error split.
- [X] Out of scope for this ticket: `_classify_jd` is intentionally shared between the JD-listing pipeline and meteorite (avoids duplicating `closed_signals`/`bot_signals`/`cookie_signals`). No rename required.

## Suggested engineer

Ada Lovelace (continuity with AST-1750/AST-1721)

### Comments

#### radia — 2026-09-21T13:42:27.354Z
[code-rubric] PROCEED (Commit: 37becf57e28bcc71945239399e71d3462a3b4ed3) LINK_EXPIRED fail bucket

#### betty — 2026-09-21T13:32:03.076Z
[bug-repro]
`origin/sub/AST-1721/AST-1752-meteorite-closed-missing-must-be-link-expired-fail` @ `96f121cb` · repro lands red, awaits fix

#### joan — 2026-09-21T13:24:33.327Z
[plan-rubric] PROCEED (Commit: 29e7800f) board CANON OK — LINK_EXPIRED is product state, not canon.

#### joan — 2026-09-21T13:24:31.788Z
[board-joan]  CANON: OK

#### betty — 2026-09-21T13:23:22.705Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/meteorite.md + utils/config.md — test_ast1750 scrape_closed asserts total_errors==1 (becomes LINK_EXPIRED fail); test_config METEORITE_STATES set and closed/missing==SCRAPE_ERROR; no LINK_EXPIRED repro

#### ada — 2026-09-21T13:18:49.866Z
`origin/sub/AST-1721/AST-1752-meteorite-closed-missing-must-be-link-expired-fail` @ `29e7800f061adf0fd51a42ef89f6468779ea25e5` · unchanged LINK_EXPIRED plan

#### chuckles — 2026-09-21T10:25:41.976Z
[check-linear] Plan Ready — plan-fix already published. Stuck because the bug-fix watcher only resumes Todo or In Progress assigned to Chuckles, and datt does not drive Bug children. Next stage is fix-board, not another plan pass.

#### susan — 2026-09-21T10:24:12.383Z
@chuckles why is this ticket stuck?  Please do the needful to get it finished.

#### ada — 2026-09-21T06:32:53.337Z
`origin/sub/AST-1721/AST-1752-meteorite-closed-missing-must-be-link-expired-fail` @ `29e7800f061adf0fd51a42ef89f6468779ea25e5` · LINK_EXPIRED fail bucket

#### ada — 2026-09-21T06:12:03.078Z
[scope-gate] AST-1752 needs a new meteorite terminal state and a fail-bucket remap. AST-1721 Component/Technical scope does not allow that. No plan doc published.

Needed, and not covered:
- `src/utils/config.py` — add `METEORITE_STATES` entry `LINK_EXPIRED` (`prior_states: ["SCRAPE_LINK"]`) and point `METEORITE_INGRESS_DISPATCH_CONFIG["scrape_page_status_states"]` `"closed"` and `"missing"` at `LINK_EXPIRED` instead of `SCRAPE_ERROR`, including the allowed-values assert. That is not a Telescope pool URL, bearer, timeout, or in-flight cap.
- `src/core/meteorite.py` `run_scrape_meteorite` — `closed` / `missing` write `LINK_EXPIRED` and increment `total_failed` (not `total_errors`). `BOT_BLOCKED` stays as it is. Genuine technical faults stay `SCRAPE_ERROR` + `total_errors`.

Scope lines that do not cover it (AST-1721):

Component:
- `src/core/meteorite.py` — **modified** — same import-path-only rewire; also allow scrape-batch counter classification so ERROR / `SCRAPE_ERROR` / `scrape_closed` paths increment `total_errors` only (not also `total_failed`); `total_failed` reserved for `BOT_BLOCKED` and `NOT_A_JOB` from `stage_meteorite` (AST-1751; complements AST-1742 inbox path).
- `src/utils/config.py` — **modified** — Telescope base URL(s), env bearer token key, client timeout, platform in-flight pool semaphore / per-node caps, and Telescope-facing defaults that must not live as literals in callers.

Technical:
- `src/core/roster.py` / `gazer.py` / `meteorite.py` — Change import module to `telescope` only; leave call shapes untouched; multi-page discovery becomes repeated Telescope HTTP calls inside the drop-in helpers, not new core logic. **Exception (AST-1751):** in `meteorite.py` scrape runners (`run_scrape_meteorite` and any sibling dispatch runners that double-bump), ERROR outcomes must not also increment fail counters — fails only for `BOT_BLOCKED` / `NOT_A_JOB`.
- `src/utils/config.py` — New/modified config keys for Telescope pool URLs, env bearer token, client timeout, and dispatch concurrency aligned to replica × per-node cap.

Why the fix cannot be done inside those lines: it adds a meteorite terminal state and counts closed/missing content verdicts as fails. That is not an import-path rewire, not Telescope client config, and it reverses the AST-1751 rule that keeps `scrape_closed` on `total_errors` and reserves `total_failed` for `BOT_BLOCKED` and `NOT_A_JOB`. `gazer.py` stays import-path-only; `_classify_jd` is not the change.

@susan this is a widening, not a missing filename. A new fail state (`LINK_EXPIRED`) is a different capability than the import rewire and the AST-1751 counter split. Please approve an epic-scope amendment before plan-fix reruns.

Logging constraint on that amendment: `stat.logging.error` says a soft-fail with no throw is `stat.logging.warning`, not `logger.error`. Non-throwing `SCRAPE_ERROR` rows cannot move to error level. The warning text has to stop saying "This row is ERROR". Thrown faults stay `logger.exception`.

---

_Implementation detail may live in git history on `origin/dev`._
