# AST-348 — scrape_jd: classify bad JD captures into typed error states

<!-- linear-archive: AST-348 archived 2026-06-03 -->

## Linear archive (AST-348)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-348/scrape-jd-classify-bad-jd-captures-into-typed-error-states  
**Status at archive:** Done  
**Project:** Astral Gazer  
**Assignee:** susan  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## **Problem**

`scrape_jd_batch` currently sends scraped content to `JD_READY` if the text clears `jd_min_chars`, with no awareness of *what* was actually captured. This means jobs whose scrape hit a cookie wall, bot block, job board page, or "no longer available" page land in `JD_READY` and burn `evaluate_jd` tokens on content that will never produce a useful grade.

We have a working classifier (from `debug/classify_jd.py`) that correctly identifies the failure modes across 26 bad entries in a sample of 185.

## **Goal**

After `get_visible_text` returns, classify the content before saving it. Route each outcome to a typed state instead of collapsing all failures into `FAILED_JD_SCRAPE`.

| **Outcome** | **New state** |
| -- | -- |
| Real job description | `JD_READY` (unchanged) |
| Cookie / consent wall | `JD_ERROR_COOKIE` |
| Bot block / auth wall | `JD_ERROR_BOT` |
| Wrong page / 404 / job board | `JD_ERROR_MISSING` |
| "No longer available" | `JD_ERROR_CLOSED` |
| Network error / empty / too short | `FAILED_JD_SCRAPE` (unchanged) |

## **Scope**

### **1.** `src/utils/config.py`

`JOB_STATES` — add four new states (no `batch_criteria`; these are terminal/skipped):

"JD_ERROR_COOKIE": {},

"JD_ERROR_BOT": {},

"JD_ERROR_MISSING": {},

"JD_ERROR_CLOSED": {},

`SKIPPED_STATES` — append the four new states.

`TRACKER_CONFIG["job_state_transitions"]` — add four new valid transitions from `PASSED_JOBLIST`:

("PASSED_JOBLIST", "JD_ERROR_COOKIE"),

("PASSED_JOBLIST", "JD_ERROR_BOT"),

("PASSED_JOBLIST", "JD_ERROR_MISSING"),

("PASSED_JOBLIST", "JD_ERROR_CLOSED"),

`TRACKER_CONFIG` — add a `jd_classifier` block holding the signal lists (keeps magic strings out of `gazer.py`):

"jd_classifier": {

"closed_signals": \[...\], *# "no longer available", etc.*

"bot_signals": \[...\], *# "New to LinkedIn? Join now", "Access Denied", etc.*

"cookie_signals": \[...\], *# "We value your privacy", "Customize Consent Preferences", etc.*

"min_meaningful_chars": 500, *# below this → JD_ERROR_MISSING*

"cookie_threshold": 3, *# hits needed for full cookie-wall classification*

"cookie_short_threshold": 1, *# hits + len < cookie_short_max → classify as cookie*

"cookie_short_max": 400,

"bot_threshold": 2,

"date_pattern_threshold": 5, *# many dates → it's a job board listing*

},

`CONSULT_CONFIG["scrape_jd"]` — add `error_states` list for documentation/introspection (no functional change needed here since routing is done in gazer):

"error_states": \["JD_ERROR_COOKIE", "JD_ERROR_BOT", "JD_ERROR_MISSING", "JD_ERROR_CLOSED"\],

### **2.** `src/core/gazer.py`

Add private helper `_classify_jd(text: str) -> str`:

* Reads signals and thresholds from `TRACKER_CONFIG["jd_classifier"]`
* Returns one of: `"ok"`, `"cookie"`, `"bot"`, `"missing"`, `"closed"`
* Logic order: closed → bot → cookie → missing → ok (exact order matters; see classify_jd.py)

Update `_scrape_one` inside `scrape_jd_batch`:

* After pruning and the `min_chars` gate, call `_classify_jd(text)`
* If classification is not `"ok"`: save the text to `job_data` (for debugging), transition to the appropriate `JD_ERROR_*` state, increment `failed`, return
* If `"ok"`: proceed exactly as today → `JD_READY`

The `evaluate_jd` task is **unchanged** — it already only picks up `JD_READY`.

### **3.** `debug/classify_jd.py`

Delete (logic migrated into gazer + config). The 5 output JSON files in `debug/` can also be cleaned up.

## **Out of scope**

* Remediating existing `JD_READY` records that contain bad content (that's a separate one-off cleanup query + state reset ticket)
* UI display changes for the new states (they'll appear in SKIPPED count automatically)
* Retry logic for `JD_ERROR_COOKIE` / `JD_ERROR_BOT` (future ticket)

## **Files changed**

| **File** | **Change** |
| -- | -- |
| `src/utils/config.py` | Add 4 states, 4 transitions, `jd_classifier` config block, update SKIPPED_STATES |
| `src/core/gazer.py` | Add `_classify_jd()` helper, update `_scrape_one` routing |
| `debug/classify_jd.py` | Delete |

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
