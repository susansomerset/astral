<!-- linear-archive: AST-389 archived 2026-06-15 -->

## Linear archive (AST-389)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-389/save-valid-titles-to-new  
**Status at archive:** Done  
**Project:** Astral Tracker  
**Assignee:** susan  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

before we upsert new job descriptions, run the pattern match for the candidate's valid titles against the string, and if it passes, count it as a "title_mismatch" as a sibling statistic to "duplicate".  We're wasting disk space on jobs no one will ever want to look at.  If the candidate does not have title regex strings in its candidate data (that is, nothing to filter on), then pass it through and title_mismatch = 0.

### Comments

#### chuckles — 2026-05-18T19:46:16.907Z
## Landed on origin/dev — Chuckles

- Merged prep-uat rollup (`65862be6`) → pushed **`origin/dev`** @ `65862be6`
- Adds test fix + review/resolution docs on top of existing product (`ca5e7953`)
- Deleted `origin/ftr/AST-389-save-valid-titles-to-new`

— Chuckles

#### chuckles — 2026-05-18T19:36:53.675Z
## UAT Ready — Chuckles

**AST-389** is standalone (no children). **Product** (`title_mismatch` at ingest) is already on **`origin/dev`** (PR merge `ca5e7953`).

**Local `dev`:** Merged `origin/ftr/AST-389-save-valid-titles-to-new` for remaining ftr-only commits (test fix + review docs):

- Merge: prep-uat rollup on `dev`
- Includes `f0c45e07` — compiled regex in title_mismatch ingest test

**Feature branch kept on origin** for finish-up after UAT.

Restart the app if running; exercise ingest with/without candidate title patterns and confirm `title_mismatch` counts.

If testing fails on `dev`:
```
git reset --hard origin/dev
```

— Chuckles

#### katherine — 2026-05-17T17:49:59.393Z
[check-linear]

**resolve-astral:** Review Posted → **User Testing** (assignee Susan).
- Radia: 0 fix-now · 0 discuss · 1 advisory (acknowledged).
- Published: `origin/ftr/AST-389` (resolve doc on feature branch; product on `origin/dev`).

— Katherine

#### radia — 2026-05-16T23:44:47.991Z
## review-astral (Radia)

**Diff:** `origin/dev...origin/ftr/AST-389` — **test-only** on feature tip (`f0c45e07`); full **AST-389** product already on `origin/dev` (`ingest_jobs` + `title_mismatch`).

**Summary:** Correct test fix. **0 fix-now** · **0 discuss** · **1 advisory**

- **Solid:** `re.compile(r"Engineer")` in `title_matchers` — required (`.search()` on matchers; plain strings would break).
- **Advisory:** Feature branch publish is test-only; product landed on `dev` earlier per plan `ca5e7953`.

**Doc commit:** `2b6be298` on `origin/ftr/AST-389`

— Radia

#### katherine — 2026-05-16T23:40:02.372Z
Tests passed by Katherine (test-astral).

**Integration:** `origin/dev` (product) + `origin/ftr/AST-389` @ `f0c45e07` (Betty test fix), merged onto `dev-kath`.

**Command (Betty manifest):**
`python -m pytest tests/component/core/test_tracker.py::TestIngestJobs::test_counts_title_mismatch_when_regex_filters_listing -q` → **1 passed**

**Product fixes:** none required.

**Published:** no new commits (feature tip unchanged @ `f0c45e07`).

— Katherine

#### betty — 2026-05-16T23:38:28.866Z
QA manifest by Betty (return pass — `[qa-handoff]`).

**Fix:** Manifest test now passes compiled matchers (`re.compile(r"Engineer")`), matching plan + `gazer._compiled_title_patterns` contract (`.search` on pattern objects, not raw strings).

**Branch:** `origin/ftr/AST-389` @ `f0c45e07` (test fix; product on `origin/dev` via `ca5e7953`)

**Manifest (Katherine — test-astral):**
1. `tests/component/core/test_tracker.py::TestIngestJobs::test_counts_title_mismatch_when_regex_filters_listing`

**Verified locally:** 1 passed.

— Betty

#### katherine — 2026-05-16T20:25:35.778Z
[qa-handoff]

**Ticket:** AST-389 — manifest item 1 fails on `dev-kath` @ `origin/dev` (post dev-betty merge).

**Command:** `/Users/susan/chuckles/astral/.venv/bin/python -m pytest tests/component/core/test_tracker.py::TestIngestJobs::test_counts_title_mismatch_when_regex_filters_listing`

**Failure:** `AttributeError: 'str' object has no attribute 'search'` at `tracker.py:61` — test passes `title_matchers=[r"Engineer"]` (raw strings).

**Why test/manifest, not product:** Plan (`docs/features/tracker/ast-389-save-valid-titles-to-new.md`) specifies `title_matchers` are **compiled** regex objects (`.search`); `gazer.py` passes `_compiled_title_patterns`. Test should use `re.compile(r"Engineer")` (or compile in fixture), not bare strings.

**Ask:** Update manifest test (or note compile step) and re-handoff; status stays **Tests Ready**.

#### betty — 2026-05-16T16:02:51.102Z
QA manifest by Betty.

**Integration:** `origin/dev` + test commits on `origin/dev-betty`.

**Manifest:**
1. `tests/component/core/test_tracker.py::TestIngestJobs::test_counts_title_mismatch_when_regex_filters_listing`

**Commits (dev-betty):** `3afe4c30` — title_mismatch ingest count

— Betty

#### chuckles — 2026-05-16T15:44:43.619Z
## [retroactive-pipeline] — Chuckles

Implementation is **already on `origin/dev`** from the emergency integration merge. **Do not re-implement.**

Next step: **`astral-qa-plan`** (Betty) from **Code Complete** — manifest + test bible only, then hand off to the implementing engineer for **`astral-test`**.

Susan board cleanup 2026-05-16.

— Chuckles

#### katherine — 2026-05-14T02:55:25.628Z
Built by Katherine.

Branch: `katherine/ast-389-save-valid-titles-to-new`
Commit: `ca5e7953` — title prefilter at ingest, `title_mismatch` on scan history.

#### katherine — 2026-05-14T02:54:43.152Z
Label review: agree on all three (conf-high, risk-Medium, scope-Single-Component).

#### susan — 2026-05-09T00:49:39.264Z
Decision: I'm saying that if there is a list to filter by (a list of regex defined for the candidate). But if the candidate doesn't have a list, we don't want all the jobs to be skipped. Does that make sense?

#### katherine — 2026-05-08T21:48:52.864Z
**Plan (execution doc):** `docs/features/tracker/ast-389-save-valid-titles-to-new.md` on branch `katherine/ast-389-save-valid-titles-to-new` (GitHub attachment below).

**Self-assessment (binding for build/review):**
- **Scope:** Single-Component — tracker ingest + Gazer/Roster handoff + `company_job_scan` + Watch History shape.
- **Conf:** conf-high — reuses `_compiled_title_patterns` / same string and flags as `validate_title_batch`.
- **Risk:** Medium — wrong filtering drops real jobs; schema mistakes break scan inserts.

**Note:** Plan flags a wording vs intent decision on “if it passes” vs disk savings; implementation follows non-match → skip insert + `title_mismatch`.

---

# Save Valid Titles to NEW

**Linear:** [AST-389 — Save Valid Titles to NEW](https://linear.app/astralcareermatch/issue/AST-389/save-valid-titles-to-new)

**Feature branch:** `katherine/ast-389-save-valid-titles-to-new` (Linear `gitBranchName`; use exactly this for plan push and attachments.)

**Summary:** Gazer ingest currently inserts every non-duplicate raw listing into `job` as `NEW`, then `validate_title` later moves non-matching rows to `INVALID_TITLE`. That stores HTML the candidate will never use. This plan filters **at ingest**: when the active candidate has one or more compiled title regexes (same source as `validate_title_batch`), only insert listings where **at least one** pattern matches the **full** `raw_job_listing` string (same match semantics as `src/core/gazer.py` `validate_title_batch`). Listings that fail that check are **not** inserted; they increment a new counter **`title_mismatch`**, sibling to **`duplicates`** in the ingest return dict and in `company_job_scan`. When there are **no** usable patterns (missing/empty `profile.title_patterns` or only invalid lines), behavior matches today: no title filtering, `title_mismatch` stays `0` for that ingest.

⚠️ **Decision (Linear wording vs intent):** The issue says “if it passes … count as title_mismatch.” The disk-space sentence implies **non-matching** listings should be dropped. This plan implements **no regex match → `title_mismatch`++ and skip `save_job`** (aligned with `validate_title_batch` where no match → fail state). If product intent was the opposite, stop and re-plan.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Extend `company_job_scan` with nullable `title_mismatch` (idempotent migration); add param to `record_to_company_job_scan`; extend INSERT; add column to `list_company_job_scans` SELECT list | data |
| `src/core/tracker.py` | Extend `ingest_jobs` with optional title matchers; filter before `save_job`; extend return dict; docstring | core |
| `src/core/gazer.py` | Add optional `ctx` to `process_gazer_batch`; compile patterns via existing `_compiled_title_patterns`; pass matchers into `ingest_jobs`; thread `title_mismatch` into `record_to_company_job_scan` and outcome `message` | core |
| `src/core/roster.py` | `process_gazer_batch(batch_id, [entity], debug=debug, ctx=ctx)` in `WATCH` branch | core |
| `src/utils/config.py` | Add `title_mismatch` column to `DATA_SHAPES` → `companies` → `list` → `watch_history` (after `duplicates` or next logical column) | utils |
| `ui/frontend/src/pages/CompaniesWatchHistory.tsx` | Add `title_mismatch: number \| null` to `ScanRow` | ui |
| `docs/features/tracker/TRACKER_DATA_MODEL.md` | Update ingest output and `company_job_scan` row description | docs |

---

## Stage 1: Data layer and ingest contract

**Done when:** `company_job_scan` persists `title_mismatch` on success rows; `list_company_job_scans` returns it; `ingest_jobs` accepts optional matchers, skips insert on non-match, returns `title_mismatch` count; `process_gazer_batch` + `run_company_task` pass `ctx` and record the new field.

1. **`database.py` — schema**
   - In `_ensure_company_job_scan_schema` (or a small helper it calls): after ensuring the table exists, read `PRAGMA table_info(company_job_scan)`. If `title_mismatch` is missing, `ALTER TABLE company_job_scan ADD COLUMN title_mismatch INTEGER`.
   - For **brand-new** DBs created from scratch in the same function: if you inline `CREATE TABLE`, include `title_mismatch INTEGER` in the column list so new installs match migrated ones.
2. **`database.py` — `record_to_company_job_scan`**
   - Add parameter `title_mismatch: Optional[int] = None` after `duplicates` (or grouped with other counters).
   - Extend the `INSERT` column list and `VALUES` tuple to write `title_mismatch`.
3. **`database.py` — `list_company_job_scans`**
   - Add `s.title_mismatch` to the `SELECT` list (same order as shapes will expose).
4. **`tracker.py` — `ingest_jobs`**
   - Add optional parameter `title_matchers: Optional[List[Any]] = None` (objects with `.search(str) -> Optional[Match]` — compiled regexes from `re.compile`; use `typing.Any` to avoid importing `re` types if unnecessary).
   - Signature order: keep existing `(company, batch_id, raw_job_listings)` first; append `title_matchers=None` at the end so call sites stay stable.
   - Loop body after duplicate check:
     - If `title_matchers` is **None** or **empty**: unchanged — `save_job` as today.
     - Else: if `any(m.search(raw_job_listing) for m in title_matchers)` then `save_job` and `new_count += 1`; else **`title_mismatch_count += 1`** and **do not** call `save_job`.
   - Return `{"new": new_count, "duplicates": dup_count, "title_mismatch": title_mismatch_count}` always (third key `0` when no filtering applied).
   - Update the module docstring / `ingest_jobs` docstring to describe the third counter.
5. **`gazer.py` — `process_gazer_batch`**
   - Add `ctx: Optional[Dict[str, Any]] = None` as the last parameter (after `debug`).
   - Before the ingest `try`: `patterns = _compiled_title_patterns(ctx or {})` — reuse existing helper (same `IGNORECASE | DOTALL`, skip invalid lines).
   - Call `ingest_jobs(short_name, batch_id, raw_job_listings, title_matchers=patterns or None)` — pass `None` when `patterns` is empty so `ingest_jobs` treats it as “no filter” (do not pass empty list if your `ingest_jobs` distinguishes `None` vs `[]`; **pick one convention in code** and document it in the plan execution: recommended **`title_matchers=None` when no patterns** so “no patterns” is explicit).
   - On success: read `title_mismatch` from result; pass to `record_to_company_job_scan(..., title_mismatch=...)`.
   - Append counts to `outcomes` message, e.g. `ingest: new=… duplicates=… title_mismatch=…`.
6. **`roster.py`**
   - In `input_state == "WATCH"`, change to `await process_gazer_batch(batch_id, [entity], debug=debug, ctx=ctx)`.

---

## Stage 2: Watch History UI and tracker doc

**Done when:** Watch History table shows `title_mismatch`; `TRACKER_DATA_MODEL.md` ingest section matches behavior; `py_compile` on changed `.py` files passes; `npx tsc -b --noEmit` in `ui/frontend` passes if TS changed.

1. **`config.py`** — under `DATA_SHAPES` → `companies` → `list` → `watch_history`, add a column entry `{"key": "title_mismatch", "label": "Title mismatch", "sortable": True}` immediately after `duplicates` (or after `new` if you prefer grouping “loss” columns — **pick one and keep shapes order aligned with API field order**).
2. **`CompaniesWatchHistory.tsx`** — extend `ScanRow` with `title_mismatch: number | null`.
3. **`TRACKER_DATA_MODEL.md`** — In **Ingest contract**, document: optional title prefilter; return shape `{"new", "duplicates", "title_mismatch"}`; and that `company_job_scan.title_mismatch` stores per-scan aggregate.

---

## Self-Assessment

**Scope:** `Single-Component` — Touches tracker ingest, one Gazer/Roster call chain, one scan table, and the existing Watch History list shape; no dispatcher or consult task changes.

**Conf:** `conf-high` — Title regex source and match semantics are already defined in `_compiled_title_patterns` / `validate_title_batch`; this plan reuses them verbatim for the string under test (`raw_job_listing`).

**Risk:** `Medium` — Over-aggressive filtering would drop jobs the candidate should see; under-filtering only wastes disk (status quo). Wrong `INSERT`/`ALTER` shape would break scan recording — mitigated by auditing tuple length vs column list per ASTRAL_CODE_RULES.

---

## Plan vs ASTRAL_CODE_RULES (§8 self-review)

- **§1.3 DRY:** Reuse `_compiled_title_patterns`; do not fork regex parsing into `tracker.py`.
- **§2.1 config:** New UI column only via existing `DATA_SHAPES` / companies list pattern; no new behavior flags in `config.py` unless a constant is truly needed (none planned).
- **§2.4 batch processing:** Ingest remains synchronous inside Gazer batch; `batch_id` unchanged.
- **§2.6 state machine:** No new job states; fewer rows reach `NEW` / `validate_title`.
- **§3.3 imports:** `tracker` must not import `gazer` (would cycle). Callers pass compiled matchers **into** `ingest_jobs` only.
- **§3.5 naming:** snake_case `title_mismatch` everywhere (DB, JSON keys, Python).

No conflicts identified.

## Review

**Status:** Review resolved 2026-05-16.

**Branch:** `ftr/AST-389`

**Product:** `origin/dev` (`ca5e7953` / retroactive merge) · **Tests:** `f0c45e07` on `ftr/AST-389`

---

## Radia review (review-astral 2026-05-16)

**Diff:** `origin/dev...origin/ftr/AST-389` (test-only on feature tip; product on `origin/dev`)

### What's solid

- Feature implementation on `origin/dev`: `ingest_jobs` title prefilter + `title_mismatch` counter matches plan (reuse compiled matchers from gazer; no `tracker`→`gazer` import).
- **ftr publish:** `test_counts_title_mismatch_when_regex_filters_listing` now passes `title_matchers=[re.compile(r"Engineer")]` — required because `ingest_jobs` calls `.search()` on matcher objects (plain strings would not work).

### Issues

| Severity | Item |
|----------|------|
| **advisory** | Plan cites `ca5e7953` on Katherine branch; review diff is test-only on `ftr/AST-389` — expected publish split. |

### Recommended actions

| Action | Owner |
|--------|-------|
| None blocking | — |

**Counts:** 0 fix-now · 0 discuss · 1 advisory

— Radia

---

## Resolution (resolve-astral 2026-05-16)

- **Fix-now / discuss:** none.
- **Advisory:** Acknowledged test-only `ftr` tip vs product on `dev` — no change required.
- **Branch:** `origin/ftr/AST-389` @ `f0c45e07` (+ Radia doc `2b6be298`) ready for UAT.

— Katherine
