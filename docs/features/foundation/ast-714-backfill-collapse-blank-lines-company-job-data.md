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
