# AST-606 — UAT: prefilter retry — WEBSITE_FOUND_RETRY not PREFILTER_UNKNOWN

<!-- linear-archive: AST-606 archived 2026-06-23 -->

## Linear archive (AST-606)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-606/uat-prefilter-retry-website-found-retry-not-prefilter-unknown  
**Status at archive:** Done  
**Project:** Astral Auditor  
**Assignee:** hedy  
**Priority / estimate:** Urgent / —  
**Parent:** AST-602 — Prefilter Company Failing  
**Blocked by / blocks / related:** parent: AST-602

### Description

## What failed

After UAT prefilter batch, companies with incomplete rubric / decode-hydration failures land in **PREFILTER_UNKNOWN**. Susan: *"It appears that we are not using WEBSITE_FOUND_RETRY for the prefilter company task."* **PREFILTER_UNKNOWN** breaks the roster retry pattern.

## Expected

* Retryable prefilter failures (incomplete rubric, decode/hydration errors when model envelope succeeded but output unusable) → **WEBSITE_FOUND_RETRY**, then re-dispatch **prefilter_company** from that state.
* Hard/system prefilter errors → **ERROR_PREFILTER** (existing `error_state`).
* **PREFILTER_UNKNOWN** removed from active prefilter paths (no new transitions into it).

## Repro

1. Run dispatch **prefilter_company** on **WEBSITE_FOUND** companies where model returns success but rubric is incomplete or decode fails (see AST-602 Original brief shapes before fix).
2. Observe company state → currently **PREFILTER_UNKNOWN**.
3. Expected → **WEBSITE_FOUND_RETRY** (retryable) or **ERROR_PREFILTER** (hard error), not **PREFILTER_UNKNOWN**.

## Parent AC (quoted inline)

> Re-run dispatch prefilter (or fixture replay of each **agent_payload** shape in the Original brief): **zero** companies stuck in **PREFILTER_UNKNOWN** solely because of decode/hydration errors when **agent_performance.status** is **success**.

> Companies reach **PREFILTER_PASSED**, **PREFILTER_FAILED**, **TO_WATCH**, or **IGNORE** per inflow vs legacy path — not parse exceptions surfaced as **PREFILTER_UNKNOWN**.

## Boundaries

* Does **not** change pass/fail/score semantics from **AST-507** / **AST-603**.
* Does **not** fix **CANNOT_READ_WEBSITE** scrape timeouts.
* Does **not** re-open consult-parity normalization logic except routing to correct retry/error states.

### Comments

#### betty — 2026-06-12T00:23:43.357Z
## [fix-uat-qa] publish note

Joan cherry-pick blocked on bible base mismatch (dev-betty has **AST-605** § not on sub). QA commit pushed directly to **`origin/sub/AST-602/AST-606-prefilter-retry-states`** @ **`b383915a`** (tests + §7.13zy). **`dev-betty`** @ **`f6457a05`** (same test delta, bible includes **AST-605**).

#### betty — 2026-06-12T00:22:44.371Z
## [fix-uat-qa] tests updated

**Triage:** Dev changed prefilter failure routing from **PREFILTER_UNKNOWN** to **WEBSITE_FOUND_RETRY** / **ERROR_PREFILTER**; existing `test_api_failure_and_missing_parsed_response` still asserted **UNKNOWN** for both paths.

**Bible:** §7.13zy added
**Tests:** `tests/component/core/test_roster.py::TestPrefilterCompany::test_api_failure_and_missing_parsed_response`; `tests/component/utils/test_config.py::TestAst507EncodedPrefilterConfig::test_company_states_and_transitions`
**Publish ref:** `origin/sub/AST-602/AST-606-prefilter-retry-states` @ `3218e049`

#### hedy — 2026-06-12T00:21:05.263Z
## [fix-uat-dev] report

**Summary:** Prefilter no longer routes retryable failures to **PREFILTER_UNKNOWN**. Added **WEBSITE_FOUND_RETRY** company state with dispatch retry seed; **ROSTER_CONFIG["prefilter"]** now uses `retry_state` / `error_state`. `_prefilter_fail` sends decode/hydration/missing-parse failures (and `do_task` failures that returned an API body) to **WEBSITE_FOUND_RETRY**; bare API failures (no response body) go to **ERROR_PREFILTER**. `run_company_task` handles **WEBSITE_FOUND_RETRY** like **WEBSITE_FOUND**.

**Publish ref:** `origin/sub/AST-602/AST-606-prefilter-retry-states` @ `c2d24172`

**Files:**
- `src/core/roster.py` — `_prefilter_fail`, retry routing, dispatch input state
- `src/utils/config.py` — **WEBSITE_FOUND_RETRY** state + transitions; `retry_state` replaces `unknown_state`
- `src/data/database.py` — `_RETRY_TASK_SEED` prefilter retry row
- `docs/features/auditor/ast-603-consult-parity-hydration-for-prefilter-company.md` — patch note

**Verification:** `.venv/bin/python -m compileall` on touched modules; inline asyncio check for retry vs ERROR paths; `test_company_states_and_transitions` pass. Existing `test_api_failure_and_missing_parsed_response` now expects **ERROR** for hard API failure (Betty may update manifest).

**Open questions:** none

---

_Implementation detail may live in git history on `origin/dev`._
