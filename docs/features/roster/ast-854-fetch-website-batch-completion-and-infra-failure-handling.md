# AST-854 — fetch_website batch completion and infra failure handling

**Linear:** [AST-854 — fetch_website batch completion and infra failure handling](https://linear.app/astralcareermatch/issue/AST-854/fetch-website-batch-completion-and-infra-failure-handling-fetch-website-didnt-finish-in-production)

**Parent (reference only — orchestration AC):** [AST-850 — fetch_website didn't finish in production](https://linear.app/astralcareermatch/issue/AST-850/fetch-website-didnt-finish-in-production)

**Prerequisite (sibling):** [AST-853 — Production Playwright browser stability](https://linear.app/astralcareermatch/issue/AST-853/production-playwright-browser-stability-fetch-website-didnt-finish-in-production) — `[playwright:<failure_class>]` error prefix, `BatchBrowserSession`, launch recovery. **Build must merge `origin/ftr/AST-850-fetch-website-didnt-finish-in-production` after AST-853 `merge-child` before Stage 1.**

**Publish ref:** `origin/sub/AST-850/AST-854-fetch-website-batch-completion-and-infra-failure-handling` (origin only)

## Summary

Production **fetch_website** batches stall when browser infra failures land companies in **CANNOT_READ_WEBSITE** (terminal) instead of **WEBSITE_FOUND_RETRY**, when one unhandled exception aborts the whole concurrent scrape, or when admin-killed runs leave companies claimed. This ticket routes **Playwright infra failures** (including **`[playwright:scrape_timeout]`** from AST-853) to **WEBSITE_FOUND_RETRY** on first strike and **CANNOT_READ_WEBSITE** only after retry exhaustion or genuine site unreadability; makes **`fetch_website_batch`** complete every claimed company without **`gather`** abort; and aligns batch summary **errors** counts with observable outcomes. Susan's interrupted batch companies re-eligible automatically via existing **`clear_company_batch`** — no one-time migration.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add **`retry_state`** to **`GAZER_CONFIG["fetch_website"]`** | utils |
| `src/core/gazer.py` | Infra vs site fail routing helper; resilient **`gather`**; **`errors`** in return dict; AST-538 **`debug_index`** on timeout + retry destinations | core |
| `src/core/consult.py` | Read **`errors`** from **`fetch_website_batch`** return when present | core |

**Out of scope:** Playwright launch/session recovery (**AST-853**), **`prefilter`**, **`fetch_job_pages`**, **`gaze`**, dispatch UI, batch size defaults, dispatcher **`clear_company_batch`** mechanism (audit-only unless gap found).

---

## Stage 1: Config and fail-routing helpers

**Done when:** `GAZER_CONFIG["fetch_website"]` exposes **`retry_state`**, and **`_fetch_website_fail_destination(company_state, error_msg, cfg)`** returns **`WEBSITE_FOUND_RETRY`** for infra errors from **`WEBSITE_FOUND`**, **`CANNOT_READ_WEBSITE`** for site failures or second-strike infra from **`WEBSITE_FOUND_RETRY`**.

1. In **`src/utils/config.py`**, extend **`GAZER_CONFIG["fetch_website"]`** (~line 996):

```python
"fetch_website": {
    "fallback_batch_size": 10,
    "pass_state": "HOMEPAGE_READY",
    "fail_state": "CANNOT_READ_WEBSITE",
    "retry_state": "WEBSITE_FOUND_RETRY",
},
```

2. In **`src/core/gazer.py`**, after imports (~line 37), add:

```python
def _is_fetch_website_infra_error(error: str) -> bool:
    """True when scrape error is browser infra (AST-853 prefix or scrape_timeout label)."""
    msg = (error or "").strip()
    return msg.startswith("[playwright:")


def _fetch_website_fail_destination(company_state: str, error: str, cfg: Dict[str, Any]) -> str:
    """Route infra → retry once; site failure or retry re-fail → CANNOT_READ_WEBSITE."""
    retry_state = cfg["retry_state"]
    fail_state = cfg["fail_state"]
    if _is_fetch_website_infra_error(error):
        if (company_state or "").strip() == retry_state:
            return fail_state
        return retry_state
    return fail_state
```

   ⚠️ **Decision:** Infra detection uses **`[playwright:`** prefix only (AST-853 contract) — includes **`scrape_timeout`**. No import of **`is_playwright_infra_failure`** in gazer; prefix is the cross-layer signal AST-853 already writes to **`scrape["error"]`** and notes.

---

## Stage 2: Resilient batch loop and observability

**Done when:** A **`fetch_website_batch`** run with 3 companies where company 2 raises an unexpected exception still processes company 3; infra failure from **`WEBSITE_FOUND`** transitions to **`WEBSITE_FOUND_RETRY`**; same company failing again with infra lands **`CANNOT_READ_WEBSITE`**; empty-text / site errors land **`CANNOT_READ_WEBSITE`** immediately; return dict includes **`errors`** count; **`debug=True`** emits **`debug_index`** on scrape-timeout path with destination state.

1. In **`fetch_website_batch`** (`src/core/gazer.py`), add **`errors = 0`** beside **`passed`** / **`failed`**.

2. Replace direct **`fail_state`** usage in failure paths with routing:

   - Read **`company_state = (company.get("state") or "").strip()`** at start of **`_fetch_one_inner`**.
   - **No company_website** path: keep **`fail_state`** ( **`CANNOT_READ_WEBSITE`** ) — not infra.
   - **Scrape error** path:
     ```python
     dest = _fetch_website_fail_destination(company_state, scrape["error"], cfg)
     transition_company_state(short_name, dest)
     save_company_data(short_name, {notes_key: scrape["error"]})
     failed += 1
     ```
     Update **`debug_index`** outcome to show **`-> {dest}`** (not hardcoded **`fail_state`**).
   - **Scrape timeout** path in **`_fetch_one`**: same **`dest = _fetch_website_fail_destination(company_state, err, cfg)`**; add when **`debug`**: **`debug_index`** with outcome **`failed — {err} -> {dest}`** before transition (mirrors other fail paths).

3. Replace **`asyncio.gather(..., return_exceptions=False)`** with resilient gather:

```python
results = await asyncio.gather(
    *[_limited(c, ci) for ci, c in enumerate(companies, start=1)],
    return_exceptions=True,
)
for r in results:
    if isinstance(r, BaseException):
        errors += 1
        _log.exception(
            "fetch_website_batch unhandled error batch_id=%s: %s",
            batch_id,
            r,
            exc_info=r,
        )
```

4. Update batch-end **`debug_detail`** summary line to include **`errors={errors}`**.

5. Return **`{"passed": passed, "failed": failed, "total": len(companies), "errors": errors}`**.

6. **Do not** change **`pass_state`** transitions, semaphore cap, or **`create_batch_browser_session`** wiring (AST-853).

---

## Stage 3: Consult summary wiring

**Done when:** **`run_consult_task`** **`fetch_website`** branch reports **`total_errors`** including unhandled **`fetch_website_batch`** exceptions.

1. In **`src/core/consult.py`**, **`fetch_website`** branch (~line 1718):

```python
r = await fetch_website_batch(batch_id, entities, debug=debug)
total = r.get("total", len(entities))
passed = r.get("passed", 0)
failed = r.get("failed", 0)
errors = r.get("errors", max(0, total - passed - failed))
return {
    "total_processed": total,
    "total_passed": passed,
    "total_failed": failed,
    "total_errors": errors,
}
```

2. **Dispatcher claim release (audit — no code change unless gap found):** Read **`dispatcher._run_unified`** **`finally`** block (**`clear_company_batch(bid)`** ~line 378). Confirm **`finally`** runs on **`asyncio.CancelledError`** from admin kill (Python semantics: it should). If audit finds a path where **`bid`** is set but **`clear_company_batch`** is skipped, add minimal fix in **`dispatcher.py`** only — **stop and comment on AST-850** if the fix is not a one-line **`finally`** guarantee. Susan confirmed automatic re-eligibility — **no migration script**.

---

## Self-Assessment

**Scope:** `Single-Component` — **`GAZER_CONFIG`**, **`fetch_website_batch`**, one consult return-shape line; no dispatcher/state-machine registry changes unless audit finds a clear gap.

**Conf:** `Medium` — retry routing mirrors **`_prefilter_fail`** / **`WEBSITE_FOUND_RETRY`** transitions already in config; resilient **`gather`** is a localized pattern from **`dispatcher._warm_then_gather`**.

**Risk:** `Medium` — production **fetch_website** hot path changes fail destinations; mitigated by prefix-gated infra routing and Betty manifest updates for retry vs terminal transitions.

---

## ASTRAL_CODE_RULES self-review

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Single **`_fetch_website_fail_destination`** helper; no duplicate infra checks in roster. |
| §2.1 config | **`retry_state`** in **`GAZER_CONFIG["fetch_website"]`**; no magic state strings in loops. |
| §2.6 state machine | Uses existing **`WEBSITE_FOUND` → `WEBSITE_FOUND_RETRY` → `CANNOT_READ_WEBSITE`** transitions in **`ASTRAL_CONFIG["company_state_transitions"]`**. |
| §2.5 bright line | No new Playwright I/O; gazer orchestrates routing only. |
| §1.5 logging | **`debug_index`** extended for timeout path; operational WARNING lines unchanged (AST-853). |

No conflicts requiring plan revision.

---

## Execution contract (developer agent)

- Execute stages **1 → 2 → 3** in order; one commit per stage on **`epic worktree`**, then publish to **`origin/sub/AST-850/AST-854-fetch-website-batch-completion-and-infra-failure-handling`**.
- **Merge `origin/ftr/AST-850-fetch-website-didnt-finish-in-production`** (includes AST-853) before Stage 1 code.
- Do **not** edit **`tests/`** — Betty owns manifest at **Code Complete**.
- Do **not** change **`fetch_job_pages_batch`**, **`prefilter`**, or Playwright modules (**AST-853** scope).

---

## Review (build stub)

**Publish ref:** `origin/sub/AST-850/AST-854-fetch-website-batch-completion-and-infra-failure-handling`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `fb7be4a` | `retry_state` in `GAZER_CONFIG`; `_fetch_website_fail_destination` helpers |
| 2 | `411e212` | Resilient `gather`, infra vs site fail routing, `errors` in return dict |
| 3 | `79f366d` | Consult `total_errors` reads batch `errors` count |

**Dispatcher audit:** `dispatcher._run_unified` `finally` always calls `clear_company_batch(bid)` for company batches — no code change.

**Tip:** `79f366d`
