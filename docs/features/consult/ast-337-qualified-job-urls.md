<!-- linear-archive: AST-337 archived 2026-06-03 -->

## Linear archive (AST-337)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-337/include-company-job-site-when-calling-qualify-job-listings  
**Status at archive:** Done  
**Project:** Astral Consult  
**Assignee:** susan  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Sometimes job_links are relative, and the agent needs to make a best effort to deduce the fully qualified job_link path.

### Comments

_No comments._

---

# AST-337 Include company job_site when calling qualify job listings

## Plan

### Context

When `qualify_job_listings` sends job listings to the Agent for evaluation, some job links are relative URLs (e.g., `/careers/job-123`). The Agent needs context to construct fully qualified URLs. Currently, only the relative job_link is provided; the Agent has no way to determine the base domain.

By appending the company's `job_site` URL (joined from the company table), the Agent can make a best-effort attempt to deduce the fully qualified job_link path. If the Agent cannot parse or construct a valid URL, that is reflected in the grade on the quality check vector.

### Design Decisions

**D1 — job_site only, not company_website.** Include only the job_site URL (where job listings are hosted), not the broader company website. This is more directly relevant to URL construction.

**D2 — Per-job data element in raw_job_listings.** Add `job_site` as a flat field in each job object in the raw_job_listings array sent to the Agent, similar to job_title, job_link, etc.

**D3 — Inner join on company.short_name.** Join the job record with the company table using `job.company = company.short_name`. Per requirements, this join will always succeed (no error handling needed).

**D4 — Database layer handles company lookup.** Add a database.py function to fetch the company.job_site column by short_name. This is a direct column lookup, not a coat-check pattern (job_site is a concrete entity field, not lazy-loaded data). Per ASTRAL_CODE_RULES 1.1 (exception), we allow this direct data layer → core layer interaction for simple field retrieval.

**D5 — No schema changes.** The response_schema for qualify_job_listings remains unchanged; job_site is input data only, not part of the Agent's response.

---

### Step 1: Job data already enriched with job_site via get_job_batch

**File:** `src/data/database.py`

**Status:** ✅ COMPLETE — Susan updated `get_job_batch()` to include job_site from the company table via inner join on company.short_name. Jobs returned from `get_job_batch()` now include the `job_site` field.

**No additional database changes needed.**

---

### Step 2: Update qualify_job_listings in consult.py to pass enriched jobs to Agent

**File:** `src/core/consult.py`

**Function:** `qualify_job_listings(batch_id, jobs, ctx, debug)`

**Change:** Updated the `assemble()` function to format job_site and raw_job_listing together for each job:

```python
def assemble(jobs):
    raw_htmls = [
        f"job_site: {j.get('job_site', '')}\nraw_job_listing: {j.get('job_data', {}).get('raw_job_listing', '')}"
        for j in jobs
    ]
    astral_ids = [j["astral_job_id"] for j in jobs]
    return enumerate_array("JOB LISTINGS", raw_htmls, index_key="astral_job_id", index_values=astral_ids)
```

This ensures each job listing includes the job_site URL, allowing the Agent to construct fully qualified URLs from relative links.

**Commit:** `dde4e77`

---

### Step 3: Verify Agent receives job_site in raw_job_listings

**File:** Agent prompt (task database / agent_task table)

**Change:** No code change needed; verify that the prompt for qualify_job_listings can access and use the job_site field when constructing URLs.

**Instruction template:** The existing prompt should already instruct the Agent on URL construction. If not, the prompt can be updated separately to explain how to use job_site with relative links.

---

## Files Changed

| File | Changes |
|------|---------|
| `src/data/database.py` | ✅ COMPLETE — `get_job_batch()` updated to include job_site from company table via inner join |
| `src/core/consult.py` | ✅ COMPLETE — Updated `assemble()` function to format job_site with each raw_job_listing for Agent |

---

## Implementation Notes

- **Inner join confidence:** Per requirements, the join always succeeds (company records exist for all jobs).
- **Grade reflection:** If the Agent cannot parse job_site or construct a URL, the grade on the quality vector should reflect that.
- **No prompt changes:** The Agent's prompt instructions should already guide URL construction; this change just provides the data.
- **Backward compatible:** Existing jobs without job_site will gracefully skip enrichment; Agent receives what's available.
- **ASTRAL_CODE_RULES 1.1 exception:** Direct column lookup from database layer (job_site is a concrete entity field, not lazy-loaded data). This is allowed per code rules exception for simple field retrieval.

---

## Testing

- Verify that jobs in qualify_job_listings include job_site field
- Confirm Agent receives job_site in raw_job_listings data
- Spot-check that Agent can construct qualified URLs from relative links + job_site

---

## Review

**Commits:** `1241d41`, `dde4e77` (fix applied)
**Branch:** `dev`
**Reviewed:** 2026-03-22

---

## What's Solid

- The approach of enriching via JOIN in `get_job_batch` is the right call — it's a single query change, no new functions, no new imports, zero ceremony. The plan identified that the data was already available and avoided over-engineering.
- Inner join is correct here: every job has a company, every company has a `short_name`. The join condition `j.company = c.short_name` matches the existing FK pattern used throughout `roster.py` and `gazer.py`.
- `_job_row_to_dict` uses `row.keys()` from `sqlite3.Row`, so the extra `c.job_site` column is picked up automatically — no schema or dict-building changes needed.
- D5 (no schema changes) is correct — `job_site` is input-only, not part of the Agent's response.

---

## Issues Resolved

### Issue 1 — job_site not in live_content ✅ FIXED

**Resolution:** Updated `assemble()` function in `qualify_job_listings` to prepend job_site to each raw_job_listing:

```python
raw_htmls = [
    f"job_site: {j.get('job_site', '')}\nraw_job_listing: {j.get('job_data', {}).get('raw_job_listing', '')}"
    for j in jobs
]
```

Agent now receives job_site for each job listing and can construct fully qualified URLs from relative links.

**Commit:** `dde4e77`

### Issue 2 — get_job_batch JOIN affects all callers ℹ️

**Status:** Advisory only. No action taken. The JOIN is benign — extra `job_site` column is harmless, and every job batch caller works correctly. Performance impact is negligible (indexed join on `short_name`).

If orphan jobs ever appear in production, recommend switching to LEFT JOIN for safety.

### Issue 3 — Plan/doc inaccuracies ✅ UPDATED

**Resolution:** Updated plan text to reflect actual implementation:
- D4: Now correctly states that `get_job_batch()` was updated with a JOIN, not that a new function was added
- Files Changed: Updated to reflect that consult.py now includes the job_site formatting change
- Step 2: Updated to describe the actual assemble() function fix

---

## Recommended Actions

| # | Severity | Status |
|---|----------|--------|
| 1 | Fix now | ✅ FIXED — job_site now included in live_content via assemble() function |
| 2 | Advisory | OK — LEFT JOIN can be considered for orphan jobs in future |
| 3 | Advisory | ✅ FIXED — Plan text updated to match implementation |

---

## Bug: AST-1893 — Restore InvalidJobLinkError class + _run_batch_consult decorator

> Housed here only because this doc owns the `qualify_job_listings` `job_link` path. The regression came from unticketed commit `c86d8b5ce` (2026-09-28), not from AST-337. None of AST-337's scope is pulled in. Mini-parent: AST-1888.

### As-is

When `qualify_job_listings` gets a passing response job with an empty or relative `job_link`, the job goes to its fail/retry destination with the reason `process_fn ValueError: no signature found for builtin type <class 'src.core.consult.InvalidJobLinkError'>`. Separately, `_run_batch_consult(..., debug=True)` no longer turns on `log_debug` for its frame.

### To-be

The same input goes to the same fail/retry destination, and the logged reason is `process_fn InvalidJobLinkError: empty job_link: ` or `process_fn InvalidJobLinkError: relative job_link: /…`. `InvalidJobLinkError` is a real `ValueError` subclass. `_run_batch_consult` is wrapped by `@_with_log_debug` again, so `debug=` scoping works the way it did before `c86d8b5ce`.

### Repro

Fixture (no DB; `_run_batch_consult` with a stubbed agent response, same shape as the existing `tests/component/core/test_consult.py` `_run_batch_consult` tests):

```python
input_job    = {"id": "e04cbf01-...", "company": "Abrams", "state": "<qualify_job_listings from_state>"}
response_job = {"id": "e04cbf01-...", "grades": [<passing>], "job_title": "Senior Engineer", "job_link": ""}
# relative variant: "job_link": "/careers/123"
```

Run the batch through the `qualify_job_listings` `process_fn`, which reaches `raise InvalidJobLinkError(f"{kind} job_link: {job_link}")` in `src/core/consult.py`.
- **Observed:** `_log_fail_dest(aid, <fail dest>, "process_fn ValueError: no signature found for builtin type <class 'src.core.consult.InvalidJobLinkError'>")`.
- **Expected:** `"process_fn InvalidJobLinkError: empty job_link: "` (or `relative job_link: /careers/123`).

Production log (2026-09-29 21:00:14, batch `qualify_job_listings-35ef8081-…`): `e04cbf01-… -> ERROR_QUALIFY_JOB_LISTINGS [process_fn ValueError: no signature found for builtin type <class 'src.core.consult.InvalidJobLinkError'>]`.

### Root cause

`c86d8b5ce` put the new class between an existing decorator and the function that decorator belonged to:

```python
@_with_log_debug                      # was _run_batch_consult's decorator
class InvalidJobLinkError(ValueError):
    """Model returned an empty or non-absolute job_link for a listing."""


async def _run_batch_consult(         # now undecorated
```

Before that commit, `c86d8b5ce^:src/core/consult.py` had `@_with_log_debug` directly above `async def _run_batch_consult` (line 1550). That misplacement causes two defects:

1. `_with_log_debug(InvalidJobLinkError)` goes down the sync branch and returns `wrapper`, a plain function. After that, the module name `InvalidJobLinkError` refers to that function, not the class. `raise InvalidJobLinkError(...)` calls `wrapper`, which runs `inspect.signature(<class>)`. That call raises `ValueError: no signature found for builtin type …` before the exception object is ever built. The `except Exception` in `_run_batch_consult` (around lines 1740–1776) still catches it, so routing is correct, but `type(e).__name__` and `e` in the fail reason are wrong.
2. `_run_batch_consult` lost its decorator, so `debug=True` passed by `qualify_job_listings`, `grade_*_batch`, and the other callers no longer sets `log_debug` for the batch frame.

### Proposed change

The fix is limited to `src/core/consult.py`, which is inside this ticket's `## Scope`:

1. Remove the `@_with_log_debug` line immediately above `class InvalidJobLinkError(ValueError):` (currently line 1567). The class definition and docstring stay exactly as they are.
2. Add `@_with_log_debug` on the line immediately above `async def _run_batch_consult(` (currently line 1572), with no blank line between them. That restores the pre-`c86d8b5ce` layout.
3. Leave everything else alone: the `raise InvalidJobLinkError(...)` site (around line 1977), the `_log_fail_dest(... f"process_fn {type(e).__name__}: {e}")` reason format, `_consult_batch_fail_dest`, the `job_link` `startswith("http")` rule, and the `_run_batch_consult` signature.

End state:

```python
class InvalidJobLinkError(ValueError):
    """Model returned an empty or non-absolute job_link for a listing."""


@_with_log_debug
async def _run_batch_consult(
```

Before commit, run compile and lint: `python -m py_compile src/core/consult.py` plus the repo linter on the file. Then run the existing `tests/component/core/test_consult.py` `_run_batch_consult` tests.

Tests: the regression test described in `## Scope` (empty/relative `job_link` → fail/retry destination and a fail reason containing `InvalidJobLinkError`, never `no signature found`) belongs to Betty (placement is her call). The engineer does not edit `tests/`.

Canon: neither AST-1893 nor AST-1888 has a Canon Scope list, so there are no canon ids to resolve for this pass.

### Blast radius

- **`_run_batch_consult` callers** (`src/core/consult.py` around lines 1986, 2148, 2264, 2375: `qualify_job_listings` and the `grade_*_batch` Pattern-A tasks). With the decorator back, `debug=True` sets `log_debug` again for the batch frame, and nested `_with_log_debug` frames restore it on exit (set/reset token). More `logger.debug` output shows up only when `debug=True`. Routing and return values do not change.
- **Wrapper overhead:** each `_run_batch_consult` call runs `inspect.signature(fn).bind_partial(...)` once. That was already the case before `c86d8b5ce`.
- **`tests/component/core/test_consult.py`:** tests that call `consult_mod._run_batch_consult(...)` directly (around lines 958, 998, 2321) go through `async_wrapper`, which uses `functools.wraps` and binds the same arguments. Tests that monkeypatch `consult_mod._run_batch_consult` (around lines 2071, 2088) swap the module attribute, so the decorator doesn't affect them. No test currently references `InvalidJobLinkError` or `no signature found`.
- **Other modules:** `_with_log_debug` has separate module-local definitions in `meteorite.py`, `contact.py`, `agent.py`, and `inbox.py`. They are not touched.

### What must still hold

- An empty or relative `job_link` on a passing `qualify_job_listings` response still goes to `_consult_batch_fail_dest(input_job["state"], error_state)`, the same fail/retry destination as today. It still produces one `_log_fail_dest` line (WARNING on retry, ERROR if terminal), and the traceback stays debug-only.
- AST-337's behavior is unchanged: `job_site` enrichment in `assemble()` and the absolute `http…` `job_link` requirement before `tracker.initialize_job`.
- `InvalidJobLinkError` subclasses `ValueError`, and `isinstance(e, InvalidJobLinkError)` is true for the raised exception.
- `_run_batch_consult` keeps its signature and return shape, and `debug=False` callers behave exactly as they do today.
- No other `@_with_log_debug` use in `src/` changes, and no decorator in `src/` sits on a class.


### Joan fix-board (AST-1893)

`[board-joan]  CANON: OK` — context_tokens≈12000

The plan-fix patch only moves `@_with_log_debug` off `InvalidJobLinkError` and back onto `_run_batch_consult` in `src/core/consult.py`. No behavior change to `job_link` rules, fail/retry routing, or `_log_fail_dest` formatting — only restoration of a real `ValueError` subclass and `debug=True` → `log_debug` scoping. Aligns with `stat.logging.debug` (run entry sets the ContextVar; batch frame was wrongly undecorated) and `stat.logging.warning`'s consult `_log_fail_dest` pattern (per-item who/why, including `process_fn {ExceptionName}: …`). Overlap checks: `patt.entity.batch-processing`, `patt.task.dispatch-retry` — claim/process/release and dest logic unchanged. AST-1893 / AST-1888 carry no Canon Scope ids; nothing in the directive roster implies a statute or pattern amendment or a new "no decorator on classes" carve-out for this mechanical regression fix. No architectural ESCALATE.

### Radia review-fix (AST-1893)

[code-rubric]
**Ticket:** AST-1893  
**Publish ref:** `b516e8764d088b3e0cb2b6860ae950b79076b7ff` (`origin/sub/AST-1888/AST-1893-restore-invalid-job-link-error-class`)  
**Diff base:** `42b6ecf527ee04dfad6bb959a71494a631da9a7a` (`origin/ftr/AST-1888-invalid-job-link-error-decorator`) — fix-lane isolated diff (2 files: `src/core/consult.py` + plan-fix patch in `docs/features/consult/ast-337-qualified-job-urls.md`)  
**Corpus:** `e1f2699fad44e4083e39a9a066cc87cae494ad51`  
**Overall:** CLEAN  

## Canon scores

**Omitted** — AST-1893 Linear description has **no frozen Canon Scope id list** (plan-fix patch states the same). Per fix-lane precedent (e.g. AST-1882 / AST-1881 in consult docs), do **not** treat `[board-joan] CANON: OK` as per-directive plan-stage grades or substitute an inferred roster.

## Column diff vs plan stage

`no plan-stage scores attached` — Joan **fix-board** `CANON: OK` only; no `validate-plan` fix-mode per-id column on this bug.

## Frame diff

- [ ] **Acceptance criteria #1–#3 (product):** Empty/relative `job_link` fail reason names `InvalidJobLinkError` (not `no signature found`); class is a `ValueError` subclass; `_run_batch_consult(debug=True)` restores `log_debug` scoping — verify in UAT or via engineer’s import/`__wrapped__` checks on tip.
- [ ] **Regression tests** called out in ticket **Component scope** / AC: owned by sibling **AST-1895** (board `TESTS: REVISE` split); not required on this sub tip.

## Fix-specific checks

- **[bug-repro]** not applicable — clean board opt-out: `qa-fix` did not run on AST-1893; Betty’s `TESTS: REVISE` coverage work was split to **AST-1895**. No `[bug-repro]` on this tip by design; not scored as missing.
- **## What must still hold — OK** — Traced against tip `src/core/consult.py`:
  - Fail path unchanged: `process_fn` still `raise InvalidJobLinkError(...)` when `job_link` fails `startswith("http")`; `_run_batch_consult` still catches `Exception`, routes via `_consult_batch_fail_dest(input_job["state"], error_state)`, single `_log_fail_dest(..., f"process_fn {type(e).__name__}: {e}")` (lines ~1742–1770, ~1973–1977). With the class restored, `type(e).__name__` is `InvalidJobLinkError` instead of the stray `ValueError`.
  - AST-337 path untouched in diff: no changes to `assemble()` / `job_site` enrichment or the `http` gate before `tracker.initialize_job`.
  - `class InvalidJobLinkError(ValueError)` undecorated; `@_with_log_debug` only on `async def _run_batch_consult` (lines 1567–1572). No `@_with_log_debug` on any class in `src/` (repo grep clean).
  - `_run_batch_consult` signature and return contract unchanged; decorator move only restores pre-`c86d8b5ce` layout.

### Findings

**fix-now:** (none)

**discuss:** (none)

**advisory:**

- **Sibling test gap (AST-1895):** Ticket description still lists `tests/` in component scope; plan-fix and board explicitly park regression assertions (fail reason string, `debug=True` `log_debug`) on **AST-1895**. Product fix on this tip is complete; UAT should not expect new tests here.
- **Pre-existing pytest drift on dev:** Hedy’s test-fix comment documents **7 failures** in `tests/component/core/test_consult.py` (rubric hydration / AST-1062 / debug detail expectations), **identical** on pre-fix `consult.py` and on this branch — outside AST-1893 blast radius; Betty flagged for AST-1895 / bible context.
- **Canon Scope process:** No F7 per-id table this pass; intake explicitly waived ids for AST-1893/AST-1888 — not an ESCALATE unless Archie later freezes a list for this cluster.

### What’s solid

- Diff is exactly the mechanical **Proposed change** (move one `@_with_log_debug` line off the exception class onto `_run_batch_consult`); no collateral edits in `consult.py`.
- Root cause analysis in plan-fix matches the failure mode (`_with_log_debug` on a class → name binding / `inspect.signature` on builtin).
- Estimate **1** matches footprint (two-line product fix + plan-fix doc).

### Chuckles branching (read-only)

| Gate | Parent shape | Next action |
|------|----------------|-------------|
| **PROCEED** (clean, artifact complete) | AST-1888 **mini-parent** with dedicated `origin/ftr/AST-1888-invalid-job-link-error-decorator` (diff **not** vs `origin/dev`) | → **Review Posted** → fix-lane **§3h** clean-review shortcut → **User Testing** (`resolve-child` skipped). Merge/stack policy for the mini-parent cluster stays on **ftr**, not the “parent Done → straight to `origin/dev`” orphaned finish-up path unless intake later flags `ORPHANED — target dev`. |

context_tokens≈14000

---

[code-rubric] PROCEED (Commit: b516e8764) Decorator restore clean

### Resolution — AST-1893

**2026-09-29** — Radia PROCEED (`b516e8764`), clean-review shortcut → User Testing (no resolve-child). Docs-Acceptance for this product-only sub: no test-tree delivery here — regression tests and bible land on gap sibling **AST-1895** (from `[board-betty] TESTS: REVISE`). Targeted `test_consult.py` run: same 7 pre-existing failures as `origin/dev`, none from this change.

---

## Bug: AST-1895 — Cover InvalidJobLinkError fail reason + _run_batch_consult debug scope

> Test-gap sibling of AST-1893, filed from `[board-betty] TESTS: REVISE`. It covers **tests and bible only** (`tests/component/core/test_consult.py`, `docs/test-bible/core/consult.md`). Betty lands it through qa-fix. There is no product change; AST-1893's decorator move (`b516e8764`) reaches this sub through `origin/ftr/AST-1888-invalid-job-link-error-decorator`.

### As-is

No test catches the `c86d8b5ce` decorator regression. `TestQualifyJobListings::test_fails_short_title_and_relative_link` sends `job_link: "/relative"`, but it only asserts `out["passed"] == 1` and `out["bad_grades"] == ["job-2"]`. Routing was correct even on the broken tree, so the test passes on `origin/dev`. Nothing asserts the `_log_fail_dest` reason, that `InvalidJobLinkError` is a `ValueError` subclass, or that `_run_batch_consult(debug=True)` sets `log_debug`. `docs/test-bible/core/consult.md` has no entry for any of these.

### To-be

A new bug-repro test class fails on `origin/dev`, where `consult.py` still has the decorator on the class, and passes on this sub's tip, where AST-1893's fix is present. The bible has a matching section and manifest.

### Repro

This was verified with a throwaway probe outside `tests/` that mirrors the tests in **Proposed change**, run with `/home/susan/astral/.venv` (system `python3` lacks `asyncpg`):

| Tree | Result |
| --- | --- |
| This sub tip (`658b7123e`, includes `b516e8764`) | 4 passed |
| `origin/dev` `src/core/consult.py` swapped in | 3 failed: the reason was `process_fn ValueError: no signature found for builtin type <class 'src.core.consult.InvalidJobLinkError'>`, `isinstance(InvalidJobLinkError, type)` was `False` (it's a function), and `log_debug` inside the frame was `[False]` instead of `[True]`. The `debug=False` guard passes on both trees, by design. |

### Root cause

The coverage gap is that the only relative-link test asserts routing, and routing survives the bug because the stray `ValueError` is caught by the same `except Exception` in `_run_batch_consult`. The reason string (`f"process_fn {type(e).__name__}: {e}"`) and the decorator's `log_debug` scoping were never asserted.

### Proposed change

All of this is Betty's (qa-fix) work. The engineer does not touch `tests/` or the bible.

**1. `tests/component/core/test_consult.py`: add a new class `TestAst1895InvalidJobLinkError`.** Place it after `TestQualifyJobListings`, or wherever Betty's placement convention says. Reuse the module's existing `_pass_grade()` / `_rubric_item()` helpers, `consult_mod`, `MagicMock` / `AsyncMock`, and `pytest.mark.asyncio`. Do not modify `test_fails_short_title_and_relative_link`; it stays as the routing check.

- **`test_empty_and_relative_job_link_fail_reason_names_error`** (**bug-repro**), async:
  - Monkeypatch these on `consult_mod`: `_log_fail_dest` → `MagicMock()` (captures `(entity, dest, reason)`; it is resolved as a module global inside `_run_batch_consult`); `_transition_job_state_for_task` → `MagicMock()`; `tracker.initialize_job` and `tracker.save_job_data` → `MagicMock()`; `_rubric_criteria_for_cfg` → `lambda _cid, _cfg: [_rubric_item()]`. The rubric patch is required: without criteria, hydration raises `rubric criteria missing or empty`, which is the cause of the 7 existing failures on dev.
  - `do_task` → `AsyncMock` returning `{"success": True, "parsed_response": {"jobs": [...]}, "timesheet": {}}` with two passing jobs: `{"astral_job_id": "job-e", "grades": [_pass_grade()], "job_title": "Engineer", "job_link": ""}` and `{"astral_job_id": "job-r", ..., "job_link": "/relative"}`.
  - Input jobs: `{"astral_job_id": "job-e"|"job-r", "state": "VALID_TITLE", "company": "co", "job_data": {"raw_job_listing": "a"|"b"}}`. Call `await consult_mod.qualify_job_listings("batch-x", jobs, {}, debug=False)`.
  - Assert `out["bad_grades"] == ["job-e", "job-r"]`.
  - Key the `_log_fail_dest` calls by `args[0]`. Both jobs' `args[1]` must equal `consult_mod._consult_batch_fail_dest("VALID_TITLE", consult_mod.TASK_CONFIG["qualify_job_listings"].get("error_state"))`, meaning the same destination.
  - Assert `args[2] == "process_fn InvalidJobLinkError: empty job_link: "` for `job-e` (trailing space included) and `args[2] == "process_fn InvalidJobLinkError: relative job_link: /relative"` for `job-r`. An exact match also rules out `no signature found`.
- **`test_invalid_job_link_error_is_value_error_class`** (**bug-repro**), sync: `assert isinstance(consult_mod.InvalidJobLinkError, type)` and `assert issubclass(consult_mod.InvalidJobLinkError, ValueError)`.
- **`test_run_batch_consult_debug_scope`**, async, `@pytest.mark.parametrize("debug", [True, False])`. `True` is the **bug-repro** case; `False` guards that nothing is forced on.
  - Monkeypatch `_transition_job_state_for_task` → `MagicMock()` and `do_task` → `AsyncMock(return_value={"success": False, "error": "bad"})`. The envelope-failure path returns early and needs no rubric.
  - Use an `assemble_fn` that appends `consult_mod.log_debug.get()` to a list and returns `"content"`. It is called inside the frame before `do_task`.
  - Record `before = consult_mod.log_debug.get()`, then call `await consult_mod._run_batch_consult("qualify_job_listings", "batch-d", [{"astral_job_id": "job-1", "state": "VALID_TITLE"}], assemble, lambda i, r, c: c["pass_state"], {}, debug)`.
  - Assert `seen == [debug]`, and `consult_mod.log_debug.get() is before` after the call, meaning the token was reset.

**2. `docs/test-bible/core/consult.md`: append a section `### AST-1895 · AST-1888 (bug-repro — InvalidJobLinkError reason + _run_batch_consult debug scope)`.** Follow the shape of the AST-1846 block: a one-line contract, then an `Area | Source | Component tests` table with one row per test above (tag the bug-repro ones), `**Integration:** none.`, and a manifest:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_consult.py::TestAst1895InvalidJobLinkError \
  -q
```

**Pass criterion:** that class is green on this sub's tip, and the three bug-repro cases (reason, class, `debug=True`) are red against `origin/dev` `src/core/consult.py`.

Canon: AST-1895 lists no Canon Scope, so there are no ids to resolve.

### Blast radius

- The work is new test code plus one bible section. No product file changes, and no existing test is edited.
- The monkeypatches are scoped by the `monkeypatch` fixture per test. `log_debug` is a `ContextVar`, and the decorator resets its token, so it does not leak into sibling tests. The `before` assertion checks exactly this.
- The 7 failures that already exist in `test_consult.py` on dev (rubric/debug-detail drift) are untouched and out of scope. The new tests avoid them by patching `_rubric_criteria_for_cfg` and by using the envelope-failure path.

### What must still hold

- There are no changes under `src/` on this ticket (AC2).
- The bug-repro cases fail on `origin/dev` and pass on the tip (AC1).
- `test_fails_short_title_and_relative_link` and every other existing test stay unchanged.
- AST-1893's invariants hold: the same fail/retry destination, one `_log_fail_dest` line per job, and a `_run_batch_consult` signature and return shape that don't change.

### Joan fix-board (AST-1895)

`[board-joan]  CANON: OK`

AST-1895's plan-fix patch is qa-fix scope only — new `TestAst1895InvalidJobLinkError` in `test_consult.py` and a bible block in `docs/test-bible/core/consult.md`. No `src/` edits (AC2). The bug-repro assertions pin behavior that already matches in-force logging statutes (`stat.logging.warning` / consult `_log_fail_dest` who→dest [why], `stat.logging.debug` / `log_debug` via `_with_log_debug` on `_run_batch_consult`) once AST-1893's product fix is on the tree; they do not introduce a new product rule or contradict `patt.entity.batch-processing` / dispatch-retry routing. No Canon Scope ids on AST-1895; nothing in the roster calls for a statute or pattern amendment to land test+bible coverage.

### Radia review-fix (AST-1895)

[code-rubric]  
**Ticket:** AST-1895  
**Publish ref:** `e393232179af4d491f7d3901a5ab650abf892533` (`origin/sub/AST-1888/AST-1895-cover-invalid-job-link-error-tests-v2`)  
**Diff base (fix-lane):** `658b7123e4b31a35e1e417130c0ce5b44392e094` (`origin/ftr/AST-1888-invalid-job-link-error-decorator`)  
**Scored delta (ticket-owned, `ftr...v2` three-dot):** `tests/component/core/test_consult.py` (+`TestAst1895InvalidJobLinkError` only), `docs/test-bible/core/consult.md` (§ AST-1895), `docs/features/consult/ast-337-qualified-job-urls.md` (plan-fix patch). Full `ftr...v2` also carries **merge-tests** + **`sync(dev)`** (106 files) — dev/tests forward; **not** scored as AST-1895 product scope per spawn.  
**Corpus:** `e1f2699fad44e4083e39a9a066cc87cae494ad51`  
**Overall:** CLEAN  

## Canon scores

**Omitted** — AST-1895 has **no frozen Canon Scope id list** (plan-fix + Linear). Do not infer a roster from Joan **fix-board** `CANON: OK`.

## Column diff vs plan stage

`no plan-stage scores attached` — Joan fix-board only; no `validate-plan` per-id column.

## Frame diff

- [ ] Run bible manifest: `./scripts/testing/run_component_tests.sh tests/component/core/test_consult.py::TestAst1895InvalidJobLinkError -q` (4 passed on tip per Hedy/Betty).
- [ ] Confirm **AST-1893** decorator fix remains on tree (`src/core/consult.py` on v2 tip **matches** `origin/ftr/...`; vs `origin/dev` only the two-line decorator move).

## Fix-specific checks

### [bug-repro] — OK (substance); advisory on tag shape

**Present and meaningful** (qa-fix on v2; Betty/Hedy threads document repro-first):

| Test | Tied to **To-be**? | Pre-fix plausibility |
|------|-------------------|----------------------|
| `test_empty_and_relative_job_link_fail_reason_names_error` | Yes — exact `_log_fail_dest` reasons `process_fn InvalidJobLinkError: empty job_link: ` and `relative job_link: /relative`; same `dest` via `_consult_batch_fail_dest`; `bad_grades` | Yes — pre-fix yields `no signature found` / wrong type (Hedy swap `origin/dev` `consult.py`: 3/4 red) |
| `test_invalid_job_link_error_is_value_error_class` | Yes — `isinstance(..., type)` + `issubclass(..., ValueError)` | Yes — pre-fix name is decorator wrapper, not class |
| `test_run_batch_consult_debug_scope[True]` | Yes — in-frame `log_debug` via `assemble_fn` capture | Yes — undecorated `_run_batch_consult` leaves `[False]` |
| `test_run_batch_consult_debug_scope[False]` | Guard — `seen == [debug or before]` per Betty board tweak (ambient inherit, not forced off) | Passes on both trees by design |

Assertions are **concrete**, not tautological (they pin strings, dest helper, and ContextVar behavior — not “no exception” alone).

**Advisory:** Individual methods lack a **first-line** `# [bug-repro]` comment (class docstring + Betty’s Linear `[bug-repro]` carry the intent). Not fix-now given qa-fix thread + passing repro contract.

### ## What must still hold — OK (with branch-shape notes)

| Item | Verdict |
|------|---------|
| No **AST-1895-authored** `src/` product fix | **OK** — `git diff ftr v2 -- src/core/consult.py` empty; v2 vs `origin/dev` differs **only** `src/core/consult.py` (AST-1893 decorator). Tip commit documents test-gap-only intent. |
| Bug-repro red on dev / green on tip | **OK** — documented in plan **Repro**, Betty qa-fix, Hedy test-fix (swap + restore). |
| Existing tests unchanged | **OK** — `ftr...v2` diff in `test_consult.py` is **+84 lines** (`TestAst1895InvalidJobLinkError` only); `test_fails_short_title_and_relative_link` untouched. |
| AST-1893 invariants (routing, one fail line, signature) | **OK** — new tests assert dest + reason format; no `src/` edits on this ticket’s owned delta. |

**Advisory (branch topology, not test defect):** Tip includes `merge-tests(AST-1895)` + `sync(dev)` so **28** `src/**` files differ **ftr → v2** (dev parity). That is **not** in the three-file ticket delta; Chuckles retired the evil `merge-tests` parent on the old sub (`96d7ba059`) and replaced the publish ref with **v2** per `[bug-fix]`. Rollup should use **v2 only**; do not merge the retired sub.

## Findings

**fix-now:** (none)

**discuss:** (none)

**advisory:**

- **merge-tests carry:** `ftr...v2` also changes **35** other `tests/**` paths (and many `docs/test-bible/**` entries) from `origin/tests` / `sync(dev)` — expected; **sibling test carry**; AST-1895 review scope stays the three paths above.
- **Plan vs board:** Proposed change still says `assert seen == [debug]`; implemented `seen == [debug or before]` matches Betty **TESTS: REVISE** tweak — plan text slightly stale, implementation correct.
- **Retired ref:** `sub/.../AST-1895-cover-invalid-job-link-error-tests` (pre-v2) must stay out of merge-child (history hazard documented by Hedy/Chuckles).

### What’s solid

- `TestAst1895InvalidJobLinkError` matches plan-fix **Proposed change** (fixtures, patches, exact reason strings, dest equality).
- Bible § **AST-1895 · AST-1888** mirrors tests, tags bug-repro rows, manifest matches plan.
- v2 repair path aligns tip with **dev** except AST-1893 fix on `consult.py` — correct stack for test-gap sibling.

### Chuckles branching (read-only)

| Gate | Parent shape | Next action |
|------|----------------|-------------|
| **PROCEED** (clean) | AST-1888 mini-parent + `origin/ftr/AST-1888-invalid-job-link-error-decorator` | → **Review Posted** → §3h clean shortcut → **User Testing** (`resolve-child` skipped). Merge **v2** only when rolling the cluster; old `...-tests` sub is retired. |

context_tokens≈15000

---

[code-rubric] PROCEED (Commit: e39323217) Bug-repro tests+bible OK
