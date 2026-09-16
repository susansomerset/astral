# AST-1690 — Retention skip for job-linked meteorites

**Linear:** [AST-1690](https://linear.app/astralcareermatch/issue/AST-1690/retention-skip-for-job-linked-meteorites-view-related-meteorite-record)  
**Parent:** [AST-1685](https://linear.app/astralcareermatch/issue/AST-1685/view-related-meteorite-record-data-on-recommended-job-modal) — View related meteorite record data on recommended job modal  
**Publish ref:** `sub/AST-1685/AST-1690-retention-skip-job-linked-meteorites`

Exempt LANDED meteorite rows that still reference an existing job from age-based purge so Recommended provenance can stay on the live row. Does not own report API/UI (siblings AST-1691 / AST-1692). Criteria tweak on the existing AST-1562 retention runner — not a new claim arc.

## UAT fitness

- **AC restored:** Parent AC7 — “Given a LANDED meteorite older than `landed_purge_days` whose `astral_job_id` still resolves to a job row, one retention run does **not** delete that meteorite id.” Parent AC8 — “Given a LANDED meteorite older than `landed_purge_days` with null `astral_job_id` or a missing job, retention may still purge it under existing age rules.” Parent AC9 — “Stage/scrape/land/qualify runners and Manage Email are unchanged except the retention skip above.”
- **Correct outcome:** A Recommended job whose staging meteorite is still linked via `astral_job_id` keeps that live meteorite row after retention runs past `landed_purge_days`, so later Meteorite-tab lookup can read timestamps / link / AI fields from the row (no job-side snapshot).
- **Sibling check:** AST-1691 (`related_meteorite` on job GET) and AST-1692 (Meteorite pane) both read the live reverse-link row — they still hold if this skip keeps job-linked LANDED ids; verified by not editing stage/scrape/land/qualify/Manage Email and by AC8 still purging unlinked / orphan-job LANDED rows.
- **Not sufficient:** Removing a stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Widening purge exemption to all LANDED (or lengthening `landed_purge_days` globally) would make unlinked rows immortal and fail AC8; snapshotting meteorite fields onto `job_data` is out of epic design (live row only). Filter in the runner (or SQL EXISTS) against `get_job` / job existence is the AC-matched fix.

## Scope gate

Ticket **## Scope** (only files this plan may touch):

- `src/core/meteorite.py` — `run_meteorite_retention` skip
- `src/data/database.py` — retention helper adjustment **only if** SQL-side EXISTS is used
- `src/utils/config.py` — **only if** a new retention literal/assert is required

**Citations:** `stat.logging.info.entity`, `stat.logging.debug`, `stat.logging.error` (id-only for error — no new throw path expected).

**Out of scope:** report API/UI (AST-1691 / AST-1692); stage/scrape/land/qualify runners; Manage Email; `tests/` / bible.

⚠️ **Decision:** Implement the skip in `run_meteorite_retention` with existing `get_job` (already imported from `src.data.database` in `meteorite.py`). Do **not** edit `database.py` or `config.py` — no new SQL helper, no new retention literal/assert. Prefer behavior change without new magic numbers (parent Component scope).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/meteorite.py` | In `run_meteorite_retention` LANDED purge path: exclude rows whose non-blank `astral_job_id` still resolves via `get_job`; keep age purge for the rest; entity-info + debug for skip/purge | core |

**Verified no touch:** `src/data/database.py`, `src/utils/config.py`, `src/core/dispatcher.py`, stage/scrape/land/qualify/notify runners, Manage Email / UI, `tests/**`, `docs/test-bible/**`.

## Stage 1: Retention skip for job-linked LANDED

**Done when:** One call to `run_meteorite_retention` does not delete a LANDED row older than `landed_purge_days` when `astral_job_id` is non-blank and `get_job(astral_job_id)` returns a row; the same run may still delete age-eligible LANDED rows with null/blank `astral_job_id` or a missing job; stale-list path unchanged; no edits outside `src/core/meteorite.py`; `python3 -m py_compile src/core/meteorite.py` succeeds.

1. In `src/core/meteorite.py`, locate `run_meteorite_retention` (AST-1562). Keep cutoffs, `list_meteorites_for_retention` for purge states, stale-list loop, and summary shape exactly as today except the LANDED purge selection below.

2. After `landed_rows = list_meteorites_for_retention(...)` and before `delete_meteorites_by_ids`, partition rows:

   - For each `row` in `landed_rows`:
     - `jid = str(row.get("astral_job_id") or "").strip()`
     - If `jid` is non-empty **and** `get_job(jid)` is not `None` → **skip** (do not add to purge ids).
     - Else → add `int(row["id"])` to the purge id list (null/blank `astral_job_id` or missing job → still purge-eligible under age rules).
   - Debug joints (ContextVar-gated via existing logger; do not wrap in `if debug`):
     - Before the partition loop: `logger.debug("Beginning landed retention filter loop on %s items", len(landed_rows))`
     - For each skip: `logger.debug("Calling get_job: [astral_job_id=%s]", jid)` then `logger.debug("Response from get_job: retention skip meteorite id=%s (job exists)", row["id"])` (or equivalent callee in/out pair using the actual `get_job` return).
     - After the loop: `logger.debug("End landed retention filter loop after %s purge ids (%s skipped)", len(purge_ids), skipped_count)` with `skipped_count` = number of job-linked skips.
   - Entity info for each skipped id (always-on): reuse `_meteorite_state_info(row_id, "retention_kept", from_state="LANDED")` so operators can grep id-pipe keep vs purge (`stat.logging.info.entity`). Do **not** invent a second logging style.

3. If the purge id list is non-empty: call `delete_meteorites_by_ids(purge_ids)` exactly as today; bump `summary["total_processed"]` / `summary["total_passed"]` by the delete return count; emit existing `_meteorite_state_info(row_id, "purged", from_state="LANDED")` for each purged id. If the purge id list is empty, skip the delete call (no-op).

4. Do **not** count skipped rows as purged. Optional: leave skipped rows out of `total_processed` for this path (purge-only accounting stays delete-count based, matching today’s landed path). Stale-list accounting unchanged.

5. Do **not** change `landed_purge_days`, `METEORITE_RETENTION_CONFIG`, `list_meteorites_for_retention`, or `delete_meteorites_by_ids`. Do **not** edit `run_stage_meteorite` / `run_scrape_meteorite` / `run_land_meteorite` / `run_notify_meteorite_bot_blocked` / Manage Email paths.

6. No new try/except in the retention runner for this skip — `get_job` returning `None` is the soft miss. If an unexpected exception escapes, leave it to the existing dispatcher handler (`stat.logging.error`); do not add a local `logger.exception` that would double-log.

7. Compile check: `python3 -m py_compile src/core/meteorite.py`.

⚠️ **Decision:** Runner-side `get_job` filter rather than SQL `EXISTS` — stays inside the ticket’s primary Scope file, reuses the already-imported helper, and keeps `list_meteorites_for_retention` shared with the stale-list path untouched. Batch may delete fewer than `batch_size` when many age-eligible rows are job-linked; next scheduled run continues — acceptable for AC7/8.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-1690
**Overall:** APPROVED
**Corpus:** fc0c368e5927a57f1561c057ce9a0ff4abe1fb13
**Publish ref:** `sub/AST-1685/AST-1690-retention-skip-job-linked-meteorites` @ `3f93d3583a30a4e1302df908a04cd6fe58107c36`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| stat.logging.info.entity | A | | |
| stat.logging.debug | C | 1 | Stage 1 §2 omits callee-out debug when `get_job` returns `None` on purge-eligible rows |
| stat.logging.error | A | | |

## Traceability

AC7→Stage 1 §2–3 (job-linked LANDED skip); AC8→Stage 1 §2 else-branch (null/blank `astral_job_id` or missing job still purge-eligible); AC9→Stage 1 §5 + Files Changed verified-no-touch (runners/Manage Email/UI untouched).

## Findings

### discuss

- **Severity:** discuss  
- **Location:** Stage 1 §2 debug joints  
- **Finding:** `stat.logging.debug` requires callee in/out for every `get_job` invocation. Plan logs Calling/Response only for skip (job exists); when `jid` is non-empty and `get_job` returns `None` (orphan job → purge), no Response line is specified.  
- **Recommendation:** Add `logger.debug("Response from get_job: %s", row_or_none)` (or equivalent) on that branch before adding the id to the purge list.

- **Severity:** discuss  
- **Location:** Canon Scope (parent child #1 Citations)  
- **Finding:** `astral.standards.in-scope-only` plainly governs this single-file retention tweak but is absent from the frozen list. Plan itself is tight (one file, explicit verified-no-touch table).  
- **Recommendation:** No plan change required; Archie may add at Discussion if the parent Canon Scope should carry scope discipline for all core children.

### acceptable

- **Severity:** acceptable  
- **Location:** Stage 1 §2 entity info  
- **Finding:** `retention_kept` as `_meteorite_state_info` to_state parallels existing `purged` retention outcome in the same function — not a real DB state, but consistent id-pipe precedent.  
- **Recommendation:** None.

- **Severity:** acceptable  
- **Location:** Scope gate decision  
- **Finding:** Runner-side `get_job` filter vs optional SQL EXISTS — justified; reuses existing import; `database.py`/`config.py` omission is within ticket Scope (“only if”).  
- **Recommendation:** None.

context_tokens≈28000

---

[plan-rubric] PROCEED (Commit: 3f93d358) retention skip plan clean

## Review

**Publish ref:** `sub/AST-1685/AST-1690-retention-skip-job-linked-meteorites`
**Build tip:** `4dccbcbb03751d6234b993fe51412f5942a21cb0`
**Status:** Code Complete pending Betty
