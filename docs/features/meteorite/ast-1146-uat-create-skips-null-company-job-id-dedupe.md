# AST-1146 — UAT: Create skips legitimate job via known_company_job_id matched=29

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1146/uat-create-skips-legitimate-job-via-known-company-job-id-matched29  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1130/manage-email-create-button-for-job-lists-isnt-working  

**Publish ref (origin):** `sub/AST-1130/AST-1146-uat-create-skips-null-company-job-id-dedupe`  
**Parent integration ref:** `ftr/AST-1130-manage-email-create-button-for-job-lists-isnt-working`

UAT bug: Manage Email Create on a Dice Saved-jobs email with three real job-detail links created only two; the third logged `skipped-duplicate` / `reason=known_company_job_id matched=29`. Patch candidate-scoped inverted id match so null/empty **and** too-short / non-real `company_job_id` values never participate. Exact `job_link` dedupe and true same-id skips (sufficiently long external ids under this candidate’s companies) stay. Does **not** own HTML normalize (AST-1131), qualify apply (AST-1133), or gaze_email redesign.

## UAT fitness

- **AC restored:** Parent: “Re-running Create on the same message skips already-known links/ids without duplicating rows” with “dedupe keyed by the candidate's companies only”; and Create on a Dice Saved-jobs multi-card email creates jobs for **real job-detail postings present in that list** (all three legitimate links — false duplicate skips violate that).
- **Correct outcome:** Create records all three Dice job-detail links as new meteorite jobs unless the same **non-empty, match-eligible** external id or exact `job_link` already exists under this candidate’s companies; null/empty `company_job_id` rows never participate in id dedupe; short junk values such as `29` never cause `known_company_job_id` skips.
- **Sibling check:** AST-1132 candidate-scoped helpers + Style D skip reasons remain; AST-1131 normalize and AST-1133 qualify untouched; exact `job_link` re-ingest skip still holds (AST-1061 / AST-1132 contract).
- **Not sufficient:** Removing the `skipped-duplicate` log / exception alone is **not** done.
- **Wrong fix rejected:** Disable all dedupe; swallow skip without fixing match rules; treat short numeric substrings as valid external ids; re-introduce global (cross-candidate) id matching.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `min_company_job_id_match_chars` to `METEORITE_EMAIL_INGEST_CONFIG` | utils |
| `src/data/database.py` | In `text_matches_known_company_job_id_for_candidate`, require `LENGTH(TRIM(company_job_id)) >=` that config min before `LIKE` match | data |

No gazer/UI/API/qualify changes (gazer already calls the candidate-scoped helper). No global `text_matches_known_company_job_id` change (unused by Create). No `tests/` / bible (Betty after Code Complete).

---

## Stage 1: Config min length for id-match eligibility

**Done when:** `METEORITE_EMAIL_INGEST_CONFIG["min_company_job_id_match_chars"]` is importable as `8`; no data-layer behavior change yet.

1. In `src/utils/config.py`, inside `METEORITE_EMAIL_INGEST_CONFIG` (after `min_jd_chars` is fine), add:

```python
    # AST-1146: inverted company_job_id match ignores null/empty (already) and values
    # shorter than this — short junk (e.g. "29") must not false-match JD text.
    "min_company_job_id_match_chars": 8,
```

2. Extend the top-of-file inventory one-liner for `METEORITE_EMAIL_INGEST_CONFIG` to mention AST-1146 id-match min length (keep AST-1061 / 1131 / 1132 mentions).

⚠️ **Decision — min length 8, not UUID-only:** Parent forbids Dice-exclusive coding; real ATS external ids are typically ≥8 chars while salary/year fragments like `29` are not. UUID path-segment pattern stays in `TRACKER_CONFIG` for qualify URL fallback — do not require UUID shape here (would over-skip non-UUID ATS ids). Exact `job_link` dedupe still covers re-Create of the same URL before qualify fills a long id.

---

## Stage 2: Candidate-scoped match ignores short / empty ids

**Done when:** `text_matches_known_company_job_id_for_candidate` returns `None` when the only stored ids under the candidate’s companies are null/empty/whitespace or length &lt; `min_company_job_id_match_chars`; still returns a match when a stored id of sufficient length appears as a substring of `text`; company-schema ensure from AST-1132 remains; global helper unchanged.

1. In `src/data/database.py`, inside `text_matches_known_company_job_id_for_candidate` `_do`, after the existing `_ensure_*` calls, read:

```python
        min_chars = int(METEORITE_EMAIL_INGEST_CONFIG["min_company_job_id_match_chars"])
```

Import `METEORITE_EMAIL_INGEST_CONFIG` from `src.utils.config` at module top if not already imported (file already imports `METEORITE_CONFIG` nearby — add the ingest config to that import list).

2. Replace the SELECT with:

```sql
SELECT company_job_id FROM job
 WHERE company_job_id IS NOT NULL AND TRIM(company_job_id) != ''
   AND LENGTH(TRIM(company_job_id)) >= ?
   AND company IN (SELECT short_name FROM company WHERE candidate_id = ?)
   AND ? LIKE '%' || company_job_id || '%'
 LIMIT 1
```

Bind order: `(min_chars, cid, text)`.

3. Update the docstring one line: match only non-empty ids with `LENGTH(TRIM(...)) >= METEORITE_EMAIL_INGEST_CONFIG["min_company_job_id_match_chars"]` (AST-1146).

4. Do **not** change `text_matches_known_company_job_id` (global), `job_link_exists_for_candidate`, gazer skip reason strings, or Create orchestration order.

**Done when (recheck):**  
- A haystack that only collides with a stored `company_job_id` of `"29"` (or any trimmed length &lt; 8) under the candidate’s companies → helper returns `None` → Create does not skip for `known_company_job_id`.  
- Same haystack containing a stored id of length ≥ 8 → still returns that id.  
- Re-Create of an exact existing `job_link` still skips via `job_link_exists_for_candidate`.  
- `python3 -m py_compile src/utils/config.py src/data/database.py` succeeds.

---

## Self-Assessment

**Scope:** `minor` — one config key + one SQL predicate on the existing candidate-scoped helper.

**Conf:** `high` — root cause is the unbounded `LIKE '%'||id||'%'` against short junk ids; min-length gate is the direct fix Susan’s diagnosis calls for.

**Risk:** `Medium` — too-high min could miss legitimate short ATS ids (mitigated: exact `job_link` dedupe remains; 8 is below UUID length and typical ATS tokens).

---

## Rules check (ASTRAL_CODE_RULES)

- §1.4 / §2.1: min length lives in `METEORITE_EMAIL_INGEST_CONFIG`, not an inline magic number in SQL.
- §1.3 DRY: filter in the data helper Create already calls; no duplicate length check in gazer.
- §2.5 / §3.3: data-only SQL change; no layer violations.
- Boundaries: no AST-1131 / AST-1133 / gaze_email / tests tree.

---

## Review (build stub)

**Publish ref:** `origin/sub/AST-1130/AST-1146-uat-create-skips-null-company-job-id-dedupe`  
**Plan path:** `docs/features/meteorite/ast-1146-uat-create-skips-null-company-job-id-dedupe.md`  
**Built tip:** `e98ca44fd64caeb188d5b36889d734a5579eda73` (`e98ca44f`)

| Stage | Commit | Summary |
|-------|--------|---------|
| 1–2 | `e98ca44f` | Config min_company_job_id_match_chars + LENGTH filter on candidate-scoped helper |
