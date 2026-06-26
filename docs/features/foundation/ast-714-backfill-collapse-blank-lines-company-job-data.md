<!-- linear-archive: AST-714 archived 2026-06-23 -->

## Linear archive (AST-714)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-714/uat-backfill-script-to-collapse-blank-lines-in-company-data-and-job  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-710 — Remove empty lines from visible text  
**Blocked by / blocks / related:** parent: AST-710

### Description

## What failed

Existing rows in `company_data` and `job_data` still contain runs of consecutive blank lines from scrapes saved before **AST-713** landed. New gazer saves are normalized, but Susan has no local script to clean already-persisted text blobs.

## Expected

A runnable local migration/backfill script applies `collapse_consecutive_blank_lines` to persisted visible-text fields in `company_data` and `job_data` (e.g. homepage text and job description keys), updates only rows that change, supports dry-run, and can target one company/job or run in batch — no staging deploy required.

## Repro

1. Inspect a company or job record scraped before this epic — note multiple consecutive blank lines in saved visible text.
2. Run the backfill script locally with `--dry-run` — script reports rows that would change.
3. Run without dry-run — re-inspect the same record; at most one blank line remains between content blocks.

## Parent AC (quoted inline)

> 3. Persisted job descriptions from JD scrape batches and homepage text from website fetch batches reflect normalized text, verifiable by inspecting saved records after a scrape run.

## Boundaries

* This bug does **not** change: gazer scrape paths (already shipped in **AST-713**), HTML extraction, or live scrape behavior.
* Does **not** require Railway/staging — local DB only.
* Does **not** add UI.
* Reuse `collapse_consecutive_blank_lines` from `src/utils/formatting.py`; do not duplicate normalization logic.

### Comments

#### betty — 2026-06-16T20:58:10.267Z
## QA test manifest (AST-714)

**Publish ref:** `origin/sub/AST-710/AST-714-backfill-collapse-blank-lines-company-job-data` @ `166ae132` (`merge-tests(AST-714): origin/tests 6cc67861`)

**Bible shasum:** `docs/test-bible/dev/backfill_collapse_blank_lines.md` → `40141224f3fdcc152dbd4e51b34ad6568c70d037`

### 1. Existing coverage (bible-backed — no rerun required)

| Area | Bible | Tests |
| --- | --- | --- |
| `collapse_consecutive_blank_lines` helper | `docs/test-bible/utils/formatting.md` (AST-713) | `tests/component/utils/test_formatting.py::TestCollapseConsecutiveBlankLines` |
| Gazer save-path normalization | `docs/test-bible/core/gazer.md` (AST-713) | `TestScrapeJdBatch::test_collapses_consecutive_blank_lines_before_save`, `TestFetchWebsiteBatch::test_collapses_consecutive_blank_lines_in_homepage_text` |

### 2. New tests (this ticket)

| Area | Tests |
| --- | --- |
| `_normalize_if_changed` skip/changed | `tests/component/scripts/test_backfill_collapse_blank_lines.py::TestNormalizeIfChanged` |
| Company backfill dry-run / save / unchanged / not found / error | `TestBackfillCompanies` |
| Job backfill dry-run / save / unchanged / not found | `TestBackfillJobs` |
| `--company` / `--job` / batch section selection + dry-run summary | `TestRunBackfill` |

### 3. Run command

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/scripts/test_backfill_collapse_blank_lines.py \
  -q
```

**Pass criterion:** pytest green on manifest lines.

— Betty

#### hedy — 2026-06-16T20:55:08.006Z
Plan: [`docs/features/foundation/ast-714-backfill-collapse-blank-lines-company-job-data.md`](https://github.com/susansomerset/astral/blob/sub/AST-710/AST-714-backfill-collapse-blank-lines-company-job-data/docs/features/foundation/ast-714-backfill-collapse-blank-lines-company-job-data.md) on `origin/sub/AST-710/AST-714-backfill-collapse-blank-lines-company-job-data` @ `ba2c982b`.

**Self-assessment**
- **Scope:** Single-Component — one new `scripts/migrations/backfill_collapse_blank_lines.py`; imports existing formatter + save helpers only.
- **Conf:** high — mirrors `backfill_culture_links.py` CLI pattern; reuses shipped `collapse_consecutive_blank_lines` from AST-713.
- **Risk:** low — merge-only writes on two gazer keys; dry-run + idempotent skip when unchanged; no state transitions.

---

# AST-714 — UAT: backfill script to collapse blank lines in company_data and job_data (Remove empty lines from visible text)

- **Linear (this ticket):** [AST-714](https://linear.app/astralcareermatch/issue/AST-714/uat-backfill-script-to-collapse-blank-lines-in-company-data-and-job)
- **Parent:** [AST-710](https://linear.app/astralcareermatch/issue/AST-710/remove-empty-lines-from-visible-text)
- **Publish ref:** `origin/sub/AST-710/AST-714-backfill-collapse-blank-lines-company-job-data` (child of AST-710; not Linear `gitBranchName`)

## Summary

Add a local-only migration script that backfills already-persisted visible text in `company_data.homepage_text` and `job_data.job_description` by applying the shared **`collapse_consecutive_blank_lines`** helper from `src/utils/formatting.py`. The script supports `--dry-run`, single-entity targeting (`--company`, `--job`), and full batch mode; it writes only rows whose normalized text differs from the stored value. This closes the UAT gap left when **AST-713** normalized gazer save paths but did not re-process historical DB rows.

## Out of scope (explicit)

| Item | Note |
|------|------|
| Gazer scrape paths | Shipped in **AST-713** |
| HTML extraction / live scrape | Unchanged |
| Other `company_data` / `job_data` keys (`nav_links`, `website_content`, `raw_job_listing`, etc.) | Not gazer visible-text blobs targeted by **AST-710** |
| UI or admin API wiring | Local CLI only |
| Railway / staging deploy | Susan runs against local DB |

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `scripts/migrations/backfill_collapse_blank_lines.py` | New backfill CLI | scripts |

## Stage 1: Backfill script for persisted visible text

**Done when:** `python scripts/migrations/backfill_collapse_blank_lines.py --dry-run` scans local DB rows, reports counts of would-change vs unchanged for companies and jobs; running without `--dry-run` updates only changed rows; `--company` / `--job` limit scope to one entity; re-run is idempotent (second run reports zero updates).

1. Create `scripts/migrations/backfill_collapse_blank_lines.py` with shebang `#!/usr/bin/env python3` and module docstring describing purpose, keys touched, and usage examples (mirror tone/structure of `scripts/migrations/backfill_culture_links.py`).

2. Bootstrap imports at top of file (after docstring):

```python
import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.data.database import list_companies, list_jobs
from src.core.roster import save_company_data
from src.core.tracker import save_job_data
from src.utils.formatting import collapse_consecutive_blank_lines
from src.utils.config import ROSTER_CONFIG, TRACKER_CONFIG
```

3. Resolve config keys once at module level:

```python
_HOMEPAGE_KEY = ROSTER_CONFIG["company_data_keys"]["homepage_text"]
_JD_KEY = TRACKER_CONFIG["job_data_keys"]["job_description"]
```

⚠️ **Decision:** Backfill only **`homepage_text`** and **`job_description`** — the two keys **AST-713** normalizes on gazer save. Do not walk `website_content` (structured page list, not a single visible-text blob) or other keys.

4. Add helper `_normalize_if_changed(text: Any) -> tuple[Optional[str], bool]`:

```python
def _normalize_if_changed(text: Any) -> tuple[Optional[str], bool]:
    """Return (normalized_text, changed). Non-str / empty -> (None, False) skip."""
    if not isinstance(text, str) or not text:
        return None, False
    normalized = collapse_consecutive_blank_lines(text)
    if normalized == text:
        return None, False
    return normalized, True
```

5. Add `backfill_companies(dry_run: bool, company: Optional[str]) -> Dict[str, int]`:

   - If `company` is set: `all_rows = list_companies()` then filter to `short_name == company`; if empty, print `Company '{company}' not found.` and return zero counts.
   - Else: `all_rows = list_companies()` (all companies, all states — backfill is data cleanup, not state-gated).
   - For each row:
     - `cd = company.get("company_data") or {}`
     - `text = cd.get(_HOMEPAGE_KEY)`
     - Call `_normalize_if_changed(text)`; if not changed, increment `unchanged`.
     - If changed and `dry_run`: print `[company {short_name}] DRY RUN — would update {_HOMEPAGE_KEY} ({len(text)} -> {len(normalized)} chars)`; increment `updated`.
     - If changed and not dry_run: `save_company_data(short_name, {_HOMEPAGE_KEY: normalized})`; print `[company {short_name}] updated {_HOMEPAGE_KEY}`; increment `updated`.
     - On `Exception`: print `[company {short_name}] error ({e})`; increment `errors`.
   - Return counts dict: `scanned`, `updated`, `unchanged`, `errors`.

6. Add `backfill_jobs(dry_run: bool, job_id: Optional[str]) -> Dict[str, int]`:

   - If `job_id` is set: `all_rows = list_jobs()` then filter to `astral_job_id == job_id`; if empty, print `Job '{job_id}' not found.` and return zero counts.
   - Else: `all_rows = list_jobs()` (all jobs).
   - For each row:
     - `jd = job.get("job_data") or {}`
     - `text = jd.get(_JD_KEY)`
     - Same `_normalize_if_changed` / dry-run / save / error pattern as companies, using `save_job_data(astral_job_id, {_JD_KEY: normalized})` and `[job {astral_job_id}]` log prefix.
   - Return same count keys.

7. Add `run_backfill(dry_run: bool = False, company: Optional[str] = None, job_id: Optional[str] = None) -> None` as synchronous entry point:

   - Print `=== DRY RUN — no DB writes ===` when `dry_run`.
   - If `company` is set OR (`company` is None and `job_id` is None): run `backfill_companies` (when `job_id` only, skip companies section).
   - If `job_id` is set OR (`company` is None and `job_id` is None): run `backfill_jobs` (when `company` only, skip jobs section).
   - ⚠️ **Decision:** `--company` alone processes companies only; `--job` alone processes jobs only; neither flag runs both sections in batch. This matches ticket wording ("target one company/job **or** run in batch").

   Logic:

```python
run_companies = company is not None or (company is None and job_id is None)
run_jobs = job_id is not None or (company is None and job_id is None)
```

   - Print combined summary:

```
=== SUMMARY ===
Companies: scanned=N updated=N unchanged=N errors=N
Jobs:      scanned=N updated=N unchanged=N errors=N
```

8. Add `if __name__ == "__main__":` block with `argparse`:

```python
parser = argparse.ArgumentParser(
    description="Backfill collapse_consecutive_blank_lines on persisted homepage_text and job_description."
)
parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing to DB.")
parser.add_argument("--company", metavar="SHORT_NAME", help="Single company short_name.")
parser.add_argument("--job", metavar="ASTRAL_JOB_ID", help="Single job astral_job_id.")
args = parser.parse_args()
run_backfill(dry_run=args.dry_run, company=args.company, job_id=args.job)
```

9. Do **not** add admin API routes, scheduler hooks, or tests in this ticket (Betty may manifest component coverage separately if needed; engineer does not edit `tests/`).

10. Manual verification during **build-child** (Susan repro):

```bash
python scripts/migrations/backfill_collapse_blank_lines.py --dry-run
python scripts/migrations/backfill_collapse_blank_lines.py --company <short_name> --dry-run
python scripts/migrations/backfill_collapse_blank_lines.py --job <astral_job_id> --dry-run
python scripts/migrations/backfill_collapse_blank_lines.py --company <short_name>
python scripts/migrations/backfill_collapse_blank_lines.py --job <astral_job_id>
```

## Self-Assessment

**Scope:** `Single-Component` — one new script under `scripts/migrations/`; no core/UI/utils changes beyond importing existing helpers.

**Conf:** `high` — follows established `backfill_culture_links.py` CLI pattern and reuses the shipped `collapse_consecutive_blank_lines` helper from **AST-713**.

**Risk:** `low` — script only merges changed keys via existing `save_company_data` / `save_job_data`; no state transitions; skipped rows when text already normalized; wrong-key scope limited to two known gazer fields.

## ASTRAL_CODE_RULES self-review

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Reuses `collapse_consecutive_blank_lines`; no duplicate normalization |
| §2.1 config | Keys read from `ROSTER_CONFIG` / `TRACKER_CONFIG`, not hardcoded strings |
| §3.3 imports | All imports at top; `sys.path` bootstrap matches sibling migration scripts |
| §3.5 naming | `backfill_collapse_blank_lines.py` mirrors existing `backfill_*` migration names |
| §3.6 debug/spikes | N/A — no spike output |

No conflicts flagged.

## Review stub

| Field | Value |
|-------|-------|
| **Publish ref** | `origin/sub/AST-710/AST-714-backfill-collapse-blank-lines-company-job-data` |
| **Built tip** | `76575751` |
| **Stages** | 1 — `scripts/migrations/backfill_collapse_blank_lines.py` |
| **Manual verify** | `.venv/bin/python scripts/migrations/backfill_collapse_blank_lines.py --dry-run` — local DB smoke (scanned/updated/unchanged summary) |
| **Betty next** | Optional component test for migration script if manifest warrants; engineer did not edit `tests/` |
