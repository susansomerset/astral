<!-- linear-archive: AST-826 archived 2026-07-22 -->

## Linear archive (AST-826)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-826/uat-select-job-page-live-content-duplicates-nav-links  
**Status at archive:** Archive  
**Project:** Astral Roster  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-753 — fetch_job_pages does not fetch nav links  
**Blocked by / blocks / related:** parent: AST-753

### Description

## What failed

After AST-759 shipped, **select_job_page** agent live content at **PJL_READY** includes navigation links **twice** — per-page `--- NAV LINKS ---` sections inside assembled PJL page text **and** a trailing global `=== NAV LINKS ===` block from merged `pjl_nav_links`. Susan UAT: "it's adding nav links TWICE."

## Expected

Nav links appear **once** in the material sent to **select_job_page** (token-efficient). Links must still be available for TRY_LINKS index resolution.

## Repro

1. Run **fetch_job_pages** on a **PREFILTER_PASSED** company with **possible_joblist_links** where Playwright finds nav links (e.g. Mitratech careers).
2. Confirm company reaches **PJL_READY** with non-empty `pjl_nav_links` and assembled PJL content.
3. Inspect **select_job_page** live content (Admin ad-hoc preview or debug) — nav enumeration appears twice (per-page block + global block).

## Parent AC (quoted inline)

> **select_job_page** at **PJL_READY** receives link material aligned with criterion 2 before the agent call when links were scraped.

## Boundaries

* This bug does **not** change: **select_job_page** routing, TRY_LINKS retry logic, or state transitions (AST-720).
* Does **not** remove nav links entirely — dedupe presentation only.
* Does **not** change **fetch_website** / homepage prefilter nav assembly unless the same double-append pattern exists there.

### Comments

#### radia — 2026-06-26T18:22:58.809Z
**Review:** `origin/dev...origin/sub/AST-753/AST-826-dedupe-select-job-page-nav-links` @ `21aa550`

**Plan fidelity:** Stage 1 matches plan — `_assembled_has_embedded_nav_links` guards on `--- NAV LINKS ---`; `_build_select_job_page_live_content` skips trailing `=== NAV LINKS ===` when per-page nav is already embedded; global append + exact-substring idempotency preserved when no embedded marker; `run_select_job_page_dispatch` still passes `nav_links=` separately for TRY_LINKS (unchanged wiring).

**Rules (§1.3, §2.6, §3.3):** roster-only presentation fix; no scrape/persistence/routing/state changes.

**Tests:** Betty manifest green — `TestAst826DedupeSelectJobPageNav` (both helper paths); `TestAst720PjlReadySelectDispatch` dispatch cases for dedupe vs global append.

**fix-now:** none

**Advisory:** Marker string must stay aligned with `_assemble_pjl_content` section header (both in `roster.py` today).

**Doc:** [ast-826-dedupe-select-job-page-nav-links.md](https://github.com/susansomerset/astral/blob/21aa550cc1577e5c384acd7f66284f798437279c/docs/features/roster/ast-826-dedupe-select-job-page-nav-links.md#review-radia) — clean; `resolve-child` may proceed.

#### betty — 2026-06-26T18:21:39.157Z
## QA test manifest (AST-826)

**Publish ref:** `origin/sub/AST-753/AST-826-dedupe-select-job-page-nav-links` @ `aabee46` (`merge-tests(AST-826): origin/tests 4dfc3b2`)

**Bible shasums (publish ref):**
- `docs/test-bible/core/roster.md` → `86a9614d3d5a70ebe963c514f1a5c06c5a9eae1b`

1. **Live content dedupe helper (required):** `tests/component/core/test_roster.py::TestAst826DedupeSelectJobPageNav` — skips global `=== NAV LINKS ===` when assembled has `--- NAV LINKS ---`; retains global append when no embedded marker.

2. **PJL_READY dispatch embedded path (required):** `tests/component/core/test_roster.py::TestAst720PjlReadySelectDispatch::test_select_dispatch_dedupes_nav_when_per_page_embedded` — agent live content has nav once; `nav_links=` unchanged for TRY_LINKS.

3. **PJL_READY dispatch legacy path (required):** `tests/component/core/test_roster.py::TestAst720PjlReadySelectDispatch::test_select_dispatch_appends_global_nav_when_no_embedded_per_page` — global block still appended when assembled lacks per-page nav marker.

**Narrowed run:**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_roster.py::TestAst826DedupeSelectJobPageNav \
  tests/component/core/test_roster.py::TestAst720PjlReadySelectDispatch::test_select_dispatch_dedupes_nav_when_per_page_embedded \
  tests/component/core/test_roster.py::TestAst720PjlReadySelectDispatch::test_select_dispatch_appends_global_nav_when_no_embedded_per_page \
  -q
```

**Broken / obsolete (Betty revision):** `TestAst720PjlReadySelectDispatch::test_select_dispatch_passes_live_content_with_nav_links` — replaced by dedupe + legacy global-append cases (AST-759 global append no longer expected when per-page nav embedded).

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

— Betty

#### chuckles — 2026-06-26T18:18:17.729Z
## validate-plan — APPROVED

**Verdict:** APPROVED → Plan Approved

**Definition fidelity:** Bug targets duplicate nav in select_job_page live content only; presentation dedupe matches UAT AC (nav once for tokens). Boundaries respected — no fetch_job_pages / state machine changes.

**Layer compliance:** `roster.py` only — OK.

**Findings:** None (fix-now).

— Chuckles

#### hedy — 2026-06-26T18:18:01.735Z
Plan doc: https://github.com/susansomerset/astral/blob/sub/AST-753/AST-826-dedupe-select-job-page-nav-links/docs/features/roster/ast-826-dedupe-select-job-page-nav-links.md

**Scope:** `minor` — guard in `_build_select_job_page_live_content` skips global `=== NAV LINKS ===` when assembled PJL already has per-page `--- NAV LINKS ---`; `pjl_nav_links` unchanged for TRY_LINKS `nav_links=` arg.

**Conf:** `high` — UAT root cause is AST-759 global append firing alongside per-page assembly; one-function dedupe.

**Risk:** `low` — legacy rows with global-only nav still get global append when no embedded marker present.

---

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

---

## Resolution (Hedy)

**Date:** 2026-06-26  
**Review ref:** Radia @ `21aa550` — **fix-now:** none

No product changes required. Presentation dedupe shipped in `2ff200b`; Betty manifest green on publish ref @ `aabee46`. §9a dry-run into `origin/dev` clean; ftr merge-tree clean (no file conflicts).

**Verdict:** Ready for **User Testing** — Susan re-run Mitratech careers repro: **select_job_page** live content should show nav links once (per-page `--- NAV LINKS ---` only, no trailing global block).
