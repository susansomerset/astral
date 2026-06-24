<!-- linear-archive: AST-622 archived 2026-06-23 -->

## Linear archive (AST-622)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-622/gazer-company-gaze-and-job-list-cache-debug-instrumentation-debug  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-544 — Debug logging backfill: gazer  
**Blocked by / blocks / related:** parent: AST-544

### Description

## What this implements

Backfill the **AST-538** debug logging contract across **gazer** / roster watch paths in `src/core/gazer.py` (company gaze, job list cache interactions, claim/process loops). Per **index N/M** header lines and `|` detail for URLs checked, cache hits/misses, and state transitions Susan needs during UAT.

## Acceptance criteria

1. Debug gaze batch shows per-company/job index detail.
2. `debug=False` unchanged.

## Boundaries

* No gazer business logic changes.
* **AST-542** (roster inflow) owns `roster.py` inflow paths — gazer watch/gaze only here.

## Notes for planning

* Use `src/utils/logging.py` helpers (`debug_index`, `debug_detail`, `debug_detail_block`) per **ASTRAL_CODE_RULES** §1.5.
* Align index header shape with dispatcher + roster conventions from sibling backfills.
* Grandfather untouched `[DEBUG]` lines only where file is not otherwise touched.

## Git branch (authoritative)

Per `orientation` **§ Branch law**: parent `ftr/ast-544-debug-logging-backfill-gazer`, child `sub/AST-544/<child-segment>`. Created at **dispatch-parent**.

### Comments

#### radia — 2026-06-14T05:05:06.301Z
**Review** — `origin/dev...origin/sub/AST-544/AST-622-gazer-company-gaze-job-cache-debug` @ `6b8bda45`

### Solid (plan + §1.5.1)

- All four batch paths instrumented per plan; `set_debug_flag` + `debug_index` / `debug_detail`; legacy `if debug: _log.info` and board `_log.debug` removed in touched blocks.
- `debug=False` unchanged for business logic, transitions, and warnings.
- `_log_listing_dedupe_trace` read-only via `raw_job_listing_is_duplicate`; cap 25; no tracker/roster scope bleed.

### fix-now

1. **`src/core/gazer.py` ~192–193** (`scrape_jd_batch`): `pruned_chars` `debug_detail` runs before the per-job `debug_index` on pass / too-short / classified-fail paths — §1.5.1 detail should sit under that item’s index header. Move into the terminal `debug_index` block (detail after header) or fold into `outcome`.

2. **`src/core/gazer.py` ~422–433 + ~450–458** (`process_gazer_batch`): gather `Exception` path logs an index header, then the main loop logs a second header for the same `short_name` (`scrape failed: {e}` vs `failure — scrape failed`). One header per scrape failure.

### discuss

- **`src/core/gazer.py` ~41–43`:** `_gazer_company_identifier` unused — drop or use for company `identifier=` fields.

### advisory

- Concurrent `scrape_jd_batch` may interleave lines (plan decision — OK for UAT).
- Plan doc: `docs/features/foundation/ast-622-gazer-company-gaze-job-cache-debug-instrumentation.md` § Review (Radia).

#### betty — 2026-06-14T05:01:05.889Z
## QA test manifest (AST-622)

**Publish ref:** `origin/sub/AST-544/AST-622-gazer-company-gaze-job-cache-debug` @ `6b8bda45` (`merge-tests(AST-622): origin/tests 4905191c`)

**Bible:** `docs/ASTRAL_TEST_BIBLE.md` shasum on publish ref: `2fe3efb473cbbba639c9c2408ad1cfc7f384bfc6` — see **§7.13zzi**

**Classification:** instrumentation-only (AST-538 §1.5.1 backfill in `src/core/gazer.py`). **No new log-string tests** per parent/plan. Extended **`test_gazer.py`** for **`LOCKED_AT_100`** branch pairs on new `debug=True`/`False` gates.

### Run (numbered)

1. `.venv/bin/python -m pytest tests/component/core/test_gazer.py tests/component/utils/test_debug_logging.py tests/component/utils/test_logging_batch.py -q`
2. Equivalent harness: `./scripts/testing/run_component_tests.sh tests/component/core/test_gazer.py`

### Manifest focus

| Touched path | Tests |
| --- | --- |
| `scrape_jd_batch` | **`TestScrapeJdBatch`**, **`TestScrapeJdBatchDebugPaths`**, **`TestScrapeJdBatchDebugBranchCoverage`** |
| `validate_title_batch` | **`TestValidateTitleBatch`**, **`TestValidateTitleBatchDebugPaths`** |
| `process_gazer_batch` + dedupe trace | **`TestProcessGazerBatch`**, **`TestProcessGazerBatchDebugPaths`**, **`TestProcessGazerBatchDebugBranchCoverage`**, **`TestLogListingDedupeTrace`** |
| `process_gaze_board_batch` | **`TestProcessGazeBoardBatch`**, **`TestProcessGazeBoardBatchDebugPaths`** |
| Identifier helpers | **`TestGazerIdentifierHelpers`** |
| `debug=False` unchanged | **`debug=False`** rows in classes above; full-file branch lock |

— Betty

#### hedy — 2026-06-14T04:54:58.826Z
Plan: `docs/features/foundation/ast-622-gazer-company-gaze-job-cache-debug-instrumentation.md`

https://github.com/susansomerset/astral/blob/sub/AST-544/AST-622-gazer-company-gaze-job-cache-debug/docs/features/foundation/ast-622-gazer-company-gaze-job-cache-debug-instrumentation.md

Four stages in `src/core/gazer.py` only: `scrape_jd_batch`, `validate_title_batch`, `process_gazer_batch` (company gaze + read-only per-listing dedupe trace via `raw_job_listing_is_duplicate`), `process_gaze_board_batch`. Retires legacy `if debug: _log.info` and board noise `_log.debug` in touched blocks.

**Self-assessment**
- **Scope:** `scope-Single-Component` — one core module, logging layer only across four batch entry points.
- **Conf:** `conf-high` — follows AST-615/AST-621 and consult qualify per-job index patterns; no new APIs.
- **Risk:** `risk-Medium` — critical scrape/ingest path; logging-only but volume at `debug=True` could be noisy if mis-gated.

Published: `origin/sub/AST-544/AST-622-gazer-company-gaze-job-cache-debug` @ `263cda51`.

---

# AST-622 — Gazer company gaze and job list cache debug instrumentation (Debug logging backfill: gazer)

- **Linear (this ticket):** [AST-622](https://linear.app/astralcareermatch/issue/AST-622/gazer-company-gaze-and-job-list-cache-debug-instrumentation-debug)
- **Parent:** [AST-544](https://linear.app/astralcareermatch/issue/AST-544/debug-logging-backfill-gazer)
- **Publish ref:** `origin/sub/AST-544/AST-622-gazer-company-gaze-job-cache-debug` (child of AST-544; not Linear `gitBranchName`)
- **Depends on:** [AST-538](https://linear.app/astralcareermatch/issue/AST-538/improve-quality-of-debug-logging) / [AST-554](https://linear.app/astralcareermatch/issue/AST-554/debug-logging-contract-and-shared-helper) — shared helper + §1.5.1 on integration line; sibling conventions from [AST-615](https://linear.app/astralcareermatch/issue/AST-615/dispatcher-claim-loop-and-guard-path-debug-instrumentation) and [AST-621](https://linear.app/astralcareermatch/issue/AST-621/roster-inflow-vet-ingest-and-website-path-debug-instrumentation).

## Summary

Backfill the **AST-538** debug logging contract across **all** `debug`-gated paths in `src/core/gazer.py`: company gaze (`process_gazer_batch`), job-list dedupe visibility before ingest (duplicate vs new per raw listing — “cache hit/miss”), JD scrape and title-validation job batches (`scrape_jd_batch`, `validate_title_batch`), and board gaze (`process_gaze_board_batch`). Retire hand-rolled `if debug: _log.info(...)` and the noise-only `_log.debug` board trace in touched blocks. **No** gazer business logic, ingest rules, or state-machine changes; `debug=False` emits no new contract lines.

## Out of scope (explicit)

| Item | Owner / note |
|------|----------------|
| `src/core/roster.py` WATCH dispatch wrapper | **AST-542** — calls `process_gazer_batch`; contract lives in gazer |
| `src/core/tracker.py` `ingest_jobs` internals | Log dedupe outcomes from gazer via read-only `raw_job_listing_is_duplicate` only |
| `src/core/dispatcher.py`, `consult.py` routing | **AST-540** / **AST-615** — passthrough unchanged |
| Betty log-string tests | Forbidden per parent |
| `job_list_visible` / parse_job_list roster paths | **AST-542** roster inflow |

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/gazer.py` | Contract debug across four batch functions; identifier helpers; read-only listing dedupe trace; retire legacy debug `info`/`debug` in touched blocks | core |

## Stage 1: Identifier helpers and `scrape_jd_batch` contract debug

**Done when:** With `debug=True`, each job in `scrape_jd_batch` logs one `index N/M` header per outcome path (missing link, scrape error, empty text, too short, classified failure, pass) plus ` | ` detail (job_link, pruned length, classification, target state); with `debug=False`, behavior and non-debug WARNING lines unchanged; no `if debug: _log.info` remains in `scrape_jd_batch`.

1. After `_log = get_logger(__name__)` (~line 32), add module-private helpers:

```python
def _gazer_job_identifier(job: Dict[str, Any]) -> str:
    """Primary debug identifier for a job row (§1.5.1 style D)."""
    return str(job.get("astral_job_id") or job.get("job_title") or "?")


def _gazer_company_identifier(row: Dict[str, Any]) -> str:
    """Primary debug identifier for a company row in gaze batches."""
    return str(row.get("short_name") or "?")
```

2. At `scrape_jd_batch` entry after the connectivity check (~109), before `cfg = TRACKER_CONFIG`:

```python
if debug:
    _log.set_debug_flag(True)
```

3. Capture `job_total = len(jobs)`. Change `_scrape_one` to accept `(job, job_index)` where `job_index` is 1-based position in the input list. Update `_limited` and `asyncio.gather` to pass index: `for ji, j in enumerate(jobs, start=1)`.

4. Inside `_scrape_one`, at each exit path, when `debug`, emit **before** existing `_log.warning` (warnings stay for non-debug monitoring):

   - **No job_link** (~125–128): `debug_index(func="gazer.scrape_jd_batch", index=job_index, total=job_total, identifier=_gazer_job_identifier(job), outcome=f"failed — no job_link -> {fail_state}")`
   - **get_visible_text exception** (~132–135): `outcome=f"failed — scrape error: {e!s} -> {fail_state}"` + `debug_detail(f"job_link={job_link!r}")`
   - **Empty text** (~137–140): `outcome=f"failed — empty visible text -> {fail_state}"` + `debug_detail(f"job_link={job_link!r}")`
   - **After `_prune_jd`** (~142–144): replace `if debug: _log.info("[%s] pruned JD: %d chars", ...)` with `debug_detail(f"pruned_chars={len(text)} job_link={job_link!r}")` only (no separate header — detail under eventual outcome header)
   - **Too short** (~145–148): `outcome=f"failed — JD too short ({len(text)} < {min_chars}) -> {fail_state}"`
   - **Classification != ok** (~151–157): `outcome=f"failed — classified {classification!r} -> {error_state}"` + `debug_detail(f"job_link={job_link!r} pruned_chars={len(text)}")`
   - **Pass** (~159–166): replace `if debug: _log.info(...)` with `debug_index(..., outcome=f"passed -> {pass_state} ({len(text)} chars)")` + `debug_detail(f"job_link={job_link!r} title={title!r}")`

5. When `debug` and `job_total > 0`, at batch start (after `passed = failed = 0`):

```python
_log.debug_index(
    func="gazer.scrape_jd_batch",
    index=1,
    total=1,
    identifier=batch_id,
    outcome=f"batch start {job_total} job(s)",
)
```

6. When `debug`, after `asyncio.gather` completes, before return:

```python
_log.debug_detail(
    f"summary passed={passed} failed={failed} total={job_total} pass_state={pass_state!r} fail_state={fail_state!r}"
)
```

⚠️ **Decision:** Concurrent scrapes may interleave contract lines — acceptable for UAT; each job still has a complete index header + detail on its outcome path.

## Stage 2: `validate_title_batch` contract debug

**Done when:** With `debug=True`, each job logs `index N/M` with pass/fail outcome and ` | ` detail (raw_listing length, pattern count); empty-pattern permissive path logs explicit detail; with `debug=False` unchanged; no `if debug: _log.info` in this function.

1. At `validate_title_batch` entry after orchestration locals (~212):

```python
if debug:
    _log.set_debug_flag(True)
job_total = len(jobs)
pattern_count = len(patterns)
if debug and job_total:
    _log.debug_index(
        func="gazer.validate_title_batch",
        index=1,
        total=1,
        identifier=batch_id,
        outcome=f"batch start {job_total} job(s) pattern_count={pattern_count}",
    )
```

2. Replace the `for job in jobs:` loop with `for ji, job in enumerate(jobs, start=1):`.

3. On **pass** branch (~227–231): replace `if debug: _log.info` with:

```python
if debug:
    _log.debug_index(
        func="gazer.validate_title_batch",
        index=ji,
        total=job_total,
        identifier=_gazer_job_identifier(job),
        outcome=f"passed -> {pass_state}",
    )
    _log.debug_detail(
        f"raw_listing_chars={len(raw_listing)} patterns={pattern_count} "
        f"permissive={not patterns}"
    )
```

4. On **fail** branch (~232–236): same shape with `outcome=f"failed -> {fail_state}"`.

5. After loop, when `debug`:

```python
_log.debug_detail(f"summary passed={passed} failed={failed} total={job_total}")
```

## Stage 3: `process_gazer_batch` — company gaze and job-list dedupe trace

**Done when:** With `debug=True`, each company in the batch logs scrape URL, parse/extract counts, per-listing dedupe hit/miss (up to cap), ingest counts, and scan record outcome; scrape gather failures are visible per company; with `debug=False` unchanged.

1. Add import to existing `src.data.database` import block (~22–28):

```python
from src.data.database import (
    ...
    raw_job_listing_is_duplicate,
)
```

2. Add module-private read-only helper **above** `process_gazer_batch` (no DB writes):

```python
def _log_listing_dedupe_trace(
    log: Any,
    company: str,
    raw_job_listings: List[str],
    title_matchers: Optional[List[Any]],
) -> None:
    """Debug-only: mirror ingest_jobs dedupe/title filter without inserting (AST-622)."""
    cap = 25
    for li, raw in enumerate(raw_job_listings):
        if li >= cap:
            log.debug_detail(f"... {len(raw_job_listings) - cap} more listings omitted from dedupe trace")
            break
        if raw_job_listing_is_duplicate(company, raw):
            log.debug_detail(f"listing {li + 1}: dedupe hit (duplicate)")
            continue
        if title_matchers and not any(m.search(raw) for m in title_matchers):
            log.debug_detail(f"listing {li + 1}: title filter miss (invalid_title)")
            continue
        log.debug_detail(f"listing {li + 1}: dedupe miss (would insert)")
```

⚠️ **Decision:** Read-only duplicate of `ingest_jobs` pre-checks — gives per-listing “cache hit/miss” without changing `tracker.ingest_jobs` or return types.

3. At `process_gazer_batch` entry after connectivity check (~263):

```python
if debug:
    _log.set_debug_flag(True)
company_total = len(companies)
if debug and company_total:
    _log.debug_index(
        func="gazer.process_gazer_batch",
        index=1,
        total=1,
        identifier=batch_id,
        outcome=f"batch start {company_total} company/companies",
    )
```

4. After `asyncio.gather` for scrapes (~271–280), when `debug`, for each `(i, r)` in `enumerate(results)` where `isinstance(r, Exception)`:

```python
sn, js = to_scrape[i]
_log.debug_index(
    func="gazer.process_gazer_batch",
    index=i + 1,
    total=len(to_scrape),
    identifier=sn,
    outcome=f"scrape failed: {r!s}",
)
_log.debug_detail(f"job_site={js!r}")
```

Use `to_scrape` indices — companies skipped before scrape (no job_site) are handled in the main loop below.

5. In the `for c in companies:` loop, assign `ci` via `for ci, c in enumerate(companies, start=1):` (replace existing `for c in companies:`).

6. **Missing short_name** — when `not short_name`: `continue` unchanged (no header — empty row).

7. **Scrape failure** (~290–297): when `short_name not in results_by_short_name`, before `record_to_company_job_scan`, when `debug`:

```python
_log.debug_index(
    func="gazer.process_gazer_batch",
    index=ci,
    total=company_total,
    identifier=short_name,
    outcome="failure — scrape failed",
)
_log.debug_detail(f"job_site={(c.get('job_site') or '').strip()!r}")
```

8. **Success path scrape** — when company is in `results_by_short_name`, after resolving `job_site` (~299):

```python
if debug:
    _log.debug_index(
        func="gazer.process_gazer_batch",
        index=ci,
        total=company_total,
        identifier=short_name,
        outcome="scrape ok",
    )
    _log.debug_detail(f"job_site={job_site!r}")
```

9. **No parse_instructions** (~305–312): when `debug`, before record:

```python
_log.debug_index(
    func="gazer.process_gazer_batch",
    index=ci,
    total=company_total,
    identifier=short_name,
    outcome="failure — no parse_instructions",
)
_log.debug_detail("re-run find_job_page")
```

10. After `extract_raw_job_listings` (~317), when `debug`:

```python
_log.debug_detail(
    f"extracted_listings={len(raw_job_listings)} container={container!r} job_tag={job_tag!r} "
    f"container_index={container_index}"
)
```

11. Before `ingest_jobs` (~321), when `debug` and `raw_job_listings`:

```python
_log.debug_detail(f"dedupe trace for {short_name} ({len(raw_job_listings)} listing(s))")
_log_listing_dedupe_trace(_log, short_name, raw_job_listings, title_matchers)
```

12. **Ingest success** (~328–339): after `ingest_jobs` returns, when `debug`:

```python
_log.debug_index(
    func="gazer.process_gazer_batch",
    index=ci,
    total=company_total,
    identifier=short_name,
    outcome=(
        f"success ingest new={new_count} duplicates={dup_count} "
        f"invalid_title={title_mismatch_count}"
    ),
)
_log.debug_detail(f"total_found={total_found} scan_status=success")
```

13. **Ingest exception** (~340–346): when `debug`, before record:

```python
_log.debug_index(
    func="gazer.process_gazer_batch",
    index=ci,
    total=company_total,
    identifier=short_name,
    outcome=f"failure — ingest_error: {e!s}",
)
_log.debug_detail(f"extracted_listings={len(raw_job_listings)}")
```

14. After loop completes, when `debug`:

```python
success_ct = sum(1 for o in outcomes if o.get("status") == "success")
_log.debug_detail(
    f"summary companies={company_total} success={success_ct} failure={company_total - success_ct}"
)
```

Keep existing `_log.warning` / `logger.info` in roster caller unchanged — contract detail is in gazer only.

## Stage 4: `process_gaze_board_batch` contract debug

**Done when:** With `debug=True`, each board_search row logs `index N/M`, board_key, success/failure outcome, and error detail on failure; noise-only `_log.debug` pragma block removed; with `debug=False` unchanged except ERROR on failure remains.

1. At `process_gaze_board_batch` entry (~357):

```python
if debug:
    _log.set_debug_flag(True)
search_total = len(searches)
if debug and search_total:
    _log.debug_index(
        func="gazer.process_gaze_board_batch",
        index=1,
        total=1,
        identifier=batch_id,
        outcome=f"batch start {search_total} board_search row(s)",
    )
```

2. Replace `for row in searches:` with `for si, row in enumerate(searches, start=1):`.

3. **Empty sid** — `continue` unchanged.

4. On **success** path (~367–373), after `outcomes.append(merged)`, when `debug`:

```python
_log.debug_index(
    func="gazer.process_gaze_board_batch",
    index=si,
    total=search_total,
    identifier=sid,
    outcome=f"success -> {act}",
)
_log.debug_detail(f"board_key={(row.get('board_key') or '')!r}")
```

5. On **exception** path (~374–382), when `debug`, before existing `_log.error`:

```python
_log.debug_index(
    func="gazer.process_gaze_board_batch",
    index=si,
    total=search_total,
    identifier=sid,
    outcome=f"failure -> {err_st}",
)
_log.debug_detail(f"board_key={(row.get('board_key') or '')!r} error={e!s}")
```

Keep existing `_log.error(...)` unchanged.

6. **Delete** the trailing `if debug: _log.debug(...)` block (~383–387) entirely — contract headers replace it; remove `# pragma: no cover` comment tied to that block.

7. After loop, when `debug`:

```python
passed = sum(1 for o in outcomes if o.get("status") == "success")
_log.debug_detail(f"summary processed={len(outcomes)} success={passed} failure={len(outcomes) - passed}")
```

## Self-Assessment

**Scope:** `scope-Single-Component` — one core module (`gazer.py`) at the logging layer only; four batch entry points and two small helpers.

**Conf:** `conf-high` — mirrors landed dispatcher/roster backfill plans and existing `consult.qualify_job_listings` per-job index pattern; no new patterns or APIs.

**Risk:** `risk-Medium` — gazer is on the critical scrape/ingest path; incorrect `debug` gating could add log noise or leak volume at scale, but business logic and transitions are untouched.

## Self-Review (ASTRAL_CODE_RULES)

| Section | Result |
|---------|--------|
| §1.3 DRY | Helpers centralize identifiers; dedupe trace read-only mirrors `ingest_jobs` checks once |
| §1.5.1 | All new lines gated on `debug=True` via `set_debug_flag`; index N/M + ` | ` detail; batch summaries additive |
| §2.1 config | No config changes |
| §2.4 batch | Per-entity index headers before batch-end summary |
| §2.6 state machine | No transition logic changes — only logs existing target states |
| §3.3 imports | `raw_job_listing_is_duplicate` added to existing database import block; no new cycles |
| §3.5 naming | `func=` strings use `gazer.<function>` prefix aligned with `dispatcher.*` / `roster.*` |

No conflicts requiring `conf-!!-NONE`.

## Execution contract (for build-child)

- Execute stages 1–4 in order; one commit per stage on epic worktree, publish to `origin/sub/AST-544/AST-622-gazer-company-gaze-job-cache-debug`.
- Do not modify `tests/` or tracker ingest signatures.
- If `raw_job_listing_is_duplicate` is not importable from `src.data.database` at build time, stop and comment on AST-622 — do not invent an alternate dedupe check.

## Review (build-child)

**Built:** `origin/sub/AST-544/AST-622-gazer-company-gaze-job-cache-debug` @ `d6e10380`

| Commit | Summary |
|--------|---------|
| `ad6d354f` | Stage 1: identifier helpers + `scrape_jd_batch` contract debug |
| `73d28101` | Stage 2: `validate_title_batch` contract debug |
| `d6e10380` | Stages 3–4: `process_gazer_batch` dedupe trace + `process_gaze_board_batch` contract debug |

**Verification:** `python3 -m py_compile src/core/gazer.py`

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-544/AST-622-gazer-company-gaze-job-cache-debug` @ `6b8bda45`

### What's solid

- Plan stages 1–4 landed: all four `debug`-gated batch entry points (`scrape_jd_batch`, `validate_title_batch`, `process_gazer_batch`, `process_gaze_board_batch`) use `set_debug_flag(True)` + `debug_index` / `debug_detail`; hand-rolled `if debug: _log.info` and board noise `_log.debug` retired in touched blocks.
- `debug=False` paths unchanged for transitions, warnings, and return shapes; no ingest or state-machine edits.
- Read-only `_log_listing_dedupe_trace` mirrors `ingest_jobs` pre-checks via `raw_job_listing_is_duplicate` (existing core→data import block); 25-listing cap per plan.
- Scope boundaries respected: no `roster.py` / `tracker.py` signature changes; Betty tests cover branch paths without log-string asserts.

### Issues

| Severity | Location | Issue |
|----------|----------|-------|
| fix-now | `gazer.py` ~192–193 (`scrape_jd_batch`) | `pruned_chars` `debug_detail` emits **before** the per-job `debug_index` on pass, too-short, and classified-fail paths — §1.5.1 expects working detail under the index header for that item. Move `pruned_chars` into the outcome block (detail after index, or fold into `outcome`). |
| fix-now | `gazer.py` ~422–433 + ~450–458 (`process_gazer_batch`) | Scrape `Exception` from `asyncio.gather` logs **two** index headers for the same company (`scrape failed: {e}` in gather loop, then `failure — scrape failed` in main loop). Keep one header per failure (prefer gather loop with exception text; drop duplicate in main loop when already logged). |
| discuss | `gazer.py` ~41–43 | `_gazer_company_identifier` is defined but never called; remove dead helper or use it for company `identifier=` fields. |

### Recommended actions

| Item | Action |
|------|--------|
| `pruned_chars` ordering | In `resolve-child`: emit after `debug_index` on each terminal path, or include in `debug_detail` paired with that header only. |
| Duplicate scrape-failure headers | In `resolve-child`: track gather-logged `short_name` set and skip redundant main-loop header, or remove gather-loop headers and rely on main loop only (with exception text in `debug_detail`). |
| `_gazer_company_identifier` | Remove unused helper or wire into `process_gazer_batch` identifiers for consistency with `_gazer_job_identifier`. |

## Resolution (2026-06-14)

**Publish:** `origin/sub/AST-544/AST-622-gazer-company-gaze-job-cache-debug` (resolve tip after push)

### Radia fix-now

| Item | Change |
|------|--------|
| `scrape_jd_batch` `pruned_chars` ordering | Removed standalone `debug_detail` before branch checks; `pruned_chars` now in `debug_detail` after each terminal `debug_index` (too-short, classified-fail already paired; pass path includes `pruned_chars`). |
| `process_gazer_batch` duplicate scrape-failure headers | `scrape_fail_logged` set from gather-loop exceptions; main loop skips redundant `failure — scrape failed` header when gather already logged that `short_name`. |

### Discuss

| Item | Change |
|------|--------|
| `_gazer_company_identifier` unused | Wired into all `process_gazer_batch` `identifier=` fields (gather + main loop). |

### Verification

- `python3 -m py_compile src/core/gazer.py`
- Betty manifest (no test-tree changes): `pytest tests/component/core/test_gazer.py tests/component/utils/test_debug_logging.py tests/component/utils/test_logging_batch.py -q`
