# AST-826 — UAT: select_job_page live content duplicates nav links

**Linear:** [AST-826 — UAT: select_job_page live content duplicates nav links](https://linear.app/astralcareermatch/issue/AST-826/uat-select-job-page-live-content-duplicates-nav-links)

**Parent (reference only):** [AST-753 — fetch_job_pages does not fetch nav links](https://linear.app/astralcareermatch/issue/AST-753/fetch-job-pages-does-not-fetch-nav-links)

**Publish ref:** `origin/sub/AST-753/AST-826-dedupe-select-job-page-nav-links`

**Summary:** Susan UAT on AST-753: after AST-759, **select_job_page** agent live content at **PJL_READY** lists navigation links twice — per-page `--- NAV LINKS ---` blocks inside `pjl_assembled_content` **and** a trailing global `=== NAV LINKS ===` block from `_build_select_job_page_live_content`. This bug dedupes agent-visible nav to **one** presentation while keeping `pjl_nav_links` in company_data for TRY_LINKS index resolution (unchanged `nav_links=` argument to `_find_job_page_from_assembled`).

**Shipped baseline:** [AST-759 plan](ast-759-shared-page-scrape-fetch-job-pages-nav-links.md) — `_assemble_pjl_content` embeds per-page nav; `_build_select_job_page_live_content` appends global block when `pjl_nav_links` is not an exact substring of assembled text (per-page numbering differs from merged global enum → append always fires).

**Out of scope:** **select_job_page** routing, TRY_LINKS retry, state transitions (AST-720); **fetch_job_pages** scrape contract; homepage/prefilter nav assembly (unless same double-append pattern is found there during build — none expected).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/roster.py` | Dedupe logic in `_build_select_job_page_live_content` (skip global append when assembled already has embedded nav); optional tiny helper `_assembled_has_embedded_nav_links` | core |

**Verify only (Betty / qa-child — engineer does not edit in build-child):**

| File | Change |
|------|--------|
| `tests/component/core/test_roster.py` | `TestAst759SharedPageScrapeContract` / `TestAst720PjlReadySelectDispatch` — assert no duplicate nav when assembled includes `--- NAV LINKS ---`; retain global-append path when assembled has no embedded nav |

---

## Stage 1: Dedupe select_job_page live content nav presentation

**Done when:** `_build_select_job_page_live_content` returns assembled PJL text unchanged (no trailing `=== NAV LINKS ===`) when any page section already contains `--- NAV LINKS ---`; still appends global block once when assembled has visible text but **no** embedded per-page nav and `pjl_nav_links` is non-empty; `run_select_job_page_dispatch` still passes `nav_links=` separately for TRY_LINKS (unchanged).

1. In `src/core/roster.py`, immediately above `_build_select_job_page_live_content`, add:

   ```python
   def _assembled_has_embedded_nav_links(assembled_content: str) -> bool:
       return "--- NAV LINKS ---" in (assembled_content or "")
   ```

2. Replace `_build_select_job_page_live_content` body with:

   - If `pjl_nav_links` blank after strip → return `assembled_content` unchanged.
   - If `_assembled_has_embedded_nav_links(assembled_content)` → return `assembled_content` unchanged (per-page nav is the single agent-visible enumeration).
   - Else if exact `pjl_nav_links` substring already in assembled → return unchanged (existing idempotency).
   - Else append global block:

     ```
     === NAV LINKS ===
     {pjl_nav_links}
     ```

     with single blank line separator when assembled is non-empty (preserve current formatting).

3. **Do not** change `run_select_job_page_dispatch` except by behavior of the helper — keep:

   ```python
   nav_links = _nav_links_for_try_links(cdata)
   live_content = _build_select_job_page_live_content(assembled_content, nav_links)
   ...
   nav_links=nav_links,
   ```

4. **Do not** change `_assemble_pjl_content`, `fetch_job_pages_batch`, or `pjl_nav_links` persistence — dedupe is presentation-only at select time.

⚠️ **Decision:** Per-page `--- NAV LINKS ---` sections (AST-759 assembly) are authoritative for agent live content when present; global `pjl_nav_links` remains stored for TRY_LINKS numeric index resolution via the separate `nav_links` argument, matching monolith inline-per-page link material without a second global list.

---

## Self-Assessment

**Scope:** `minor` — one helper + one function body in `roster.py`; no config or state machine.

**Conf:** `high` — root cause identified in UAT; fix is a narrow guard on existing AST-759 append path.

**Risk:** `low` — wrong guard would hide nav from agent when only global `pjl_nav_links` exists (legacy rows); Stage 1 step 2 preserves global append when no `--- NAV LINKS ---` marker in assembled content.

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Single marker check; no second dedupe path |
| §2.6 state machine | No transitions touched |
| §3.3 imports | roster-only change |

No unresolved conflicts.

---

## Review stub (Hedy / build)

**Publish ref:** `origin/sub/AST-753/AST-826-dedupe-select-job-page-nav-links`  
**Product commits:** `2ff200b` (Stage 1 — dedupe select_job_page live content nav)

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-753/AST-826-dedupe-select-job-page-nav-links` @ `aabee46` (product: `2ff200b`)

### What's solid

| Area | Notes |
| --- | --- |
| Plan fidelity | Stage 1 exact: `_assembled_has_embedded_nav_links` marker guard; `_build_select_job_page_live_content` skips global `=== NAV LINKS ===` when `--- NAV LINKS ---` present; retains global append + exact-substring idempotency when no embedded marker; `run_select_job_page_dispatch` wiring unchanged (`nav_links=` still passed separately for TRY_LINKS). |
| UAT root cause | Correctly targets AST-759 interaction (per-page assembly + global append) without touching scrape, persistence, or routing. |
| Rules | roster-only; no layer/import/state-machine changes. |
| Tests | Betty manifest: `TestAst826DedupeSelectJobPageNav` (helper both paths); `TestAst720PjlReadySelectDispatch` split into embedded-dedupe vs global-append dispatch cases. |

### Issues

None (**fix-now**).

### Recommended actions

| Severity | Item |
| --- | --- |
| **Advisory** | Marker `--- NAV LINKS ---` must stay aligned with `_assemble_pjl_content` output — acceptable today because both live in `roster.py`; consider a module-level constant only if the section header ever changes. |

**Verdict:** Clean — `resolve-child` may proceed.
