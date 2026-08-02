# AST-1132 — Job-link hygiene + non-job create skip

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1132/job-link-hygiene-non-job-create-skip-manage-email-create-button-for  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1130/manage-email-create-button-for-job-lists-isnt-working  

**Publish ref (origin):** `sub/AST-1130/AST-1132-job-link-hygiene-non-job-create-skip`  
**Parent integration ref:** `ftr/AST-1130-manage-email-create-button-for-job-lists-isnt-working`

After AST-1131 normalize, owns tightening which http(s) candidates may Playwright-fetch and create: config-driven exclude/allow substring rules for non-job hosts/paths, post-fetch skip when the final URL or visible text is clearly not a job posting (so `min_jd_chars` alone cannot admit SVG/spec pages), and candidate-scoped dedupe for Manage Email Create (same link/id on another candidate must not block create). Preserves created/skipped reporting and Style D debug. Does **not** own HTML unescape (AST-1131) or `qualify_meteorite` apply (AST-1133). Does not redesign `gaze_email`.

**Current gap (tip after AST-1131 merge):** `_meteorite_email_candidate_links` only excludes unsubscribe/tracking fragments — not `w3.org` / SVG / schema hosts. `ingest_meteorite_jobs_from_email_html` uses global `job_link_exists` + global `text_matches_known_company_job_id`, which bounces cross-candidate duplicates contrary to parent AC. Post-fetch gate is length-only.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Extend `METEORITE_EMAIL_INGEST_CONFIG` with expanded excludes, optional allow substrings, and non-job visible-text markers | utils |
| `src/data/database.py` | Widen `job_link_exists_for_candidate` to all companies for the candidate; add `text_matches_known_company_job_id_for_candidate` | data |
| `src/core/gazer.py` | Apply allow filter in link discovery; post-fetch URL/content non-job skip; switch ingest dedupe to candidate-scoped helpers; Style D for new skip reasons | core |

No UI, API, Playwright, inbox strip, qualify, `gaze_email` redesign, or `tests/` / bible changes (Betty after Code Complete).

---

## Stage 1: Config knobs for hygiene + non-job skip

**Done when:** `METEORITE_EMAIL_INGEST_CONFIG` exposes the keys below as importable literals; no data/gazer behavior changes yet.

1. In `src/utils/config.py`, inside `METEORITE_EMAIL_INGEST_CONFIG`, **replace** the existing `link_exclude_substrings` tuple with:

```python
    # Lowercased path/host fragments that disqualify an href (unsubscribe, tracking,
    # namespace/spec/asset URLs — AST-1132 hygiene).
    "link_exclude_substrings": (
        "unsubscribe",
        "mailto:",
        "list-manage.com",
        "/preferences",
        "/email-settings",
        "w3.org",
        "/2000/svg",
        "schemas.xmlsoap.org",
        "xmlns=",
    ),
```

2. Immediately after `link_exclude_substrings`, add:

```python
    # When non-empty: after exclude check, href must contain ≥1 allow substring (casefold)
    # to remain a Playwright candidate. Empty = no allow filter (newline pastes of any
    # ATS URL still work — not Dice-exclusive).
    "link_allow_substrings": (),
    # After Playwright: if any marker appears in visible text (casefold), skip create
    # even when len(text) >= min_jd_chars (SVG/spec docs that are "long enough").
    "non_job_visible_substrings": (
        "www.w3.org/2000/svg",
        "w3.org/2000/svg",
        "schemas.xmlsoap.org",
        "xml schema",
        "svg namespace",
    ),
```

3. Update the top-of-file config inventory one-liner for `METEORITE_EMAIL_INGEST_CONFIG` to mention AST-1132 hygiene / non-job skip (keep AST-1061 + AST-1131 mentions).

⚠️ **Decision — extend ingest config, not a new block:** Parent architectural definition says extend `METEORITE_EMAIL_INGEST_CONFIG`. Thresholds stay next to link discovery / min_jd.

⚠️ **Decision — empty allow by default:** Parent forbids Dice-only coding and requires `\n`-delimited arbitrary job-link pastes. An empty `link_allow_substrings` keeps allow as a real config knob without locking create to `/job-detail/`. Operators can tighten later without a code change.

⚠️ **Decision — exclude `xmlns=` as substring:** Catches rare residual attribute-shaped hrefs if normalize missed a case; casefold match on the full href string.

---

## Stage 2: Candidate-scoped dedupe helpers

**Done when:** `job_link_exists_for_candidate` scopes to all companies owned by the candidate; `text_matches_known_company_job_id_for_candidate` is importable and mirrors the global inverted match with the same company scope; global helpers remain for any non-ingest callers; no gazer wiring yet.

1. In `src/data/database.py`, update `job_link_exists_for_candidate` docstring to:  
   `True when any job under a company owned by this candidate has this exact job_link.`  
   Replace the meteorite-`short_name_template` company equality with the same candidate company subquery used by `claim_job_batch`:

```sql
SELECT 1 FROM job
 WHERE job_link = ?
   AND job_link IS NOT NULL AND TRIM(job_link) != ''
   AND company IN (SELECT short_name FROM company WHERE candidate_id = ?)
 LIMIT 1
```

Bind order: `(link, cid)`. Remove the `METEORITE_CONFIG["short_name_template"]` local if it becomes unused in this function (do not remove unrelated METEORITE_CONFIG imports used elsewhere in the file).

⚠️ **Decision — all candidate companies, not meteorite-only:** Parent AC: “dedupe is keyed by the candidate's companies only.” `claim_job_batch` already uses `company IN (SELECT short_name FROM company WHERE candidate_id = ?)`. Widening this helper also aligns `gaze_email` (existing caller) with the same AC without a second fork.

2. Immediately after `job_link_exists_for_candidate`, add:

```python
def text_matches_known_company_job_id_for_candidate(
    candidate_id: str, text: str
) -> Optional[str]:
    """Inverted company_job_id match scoped to this candidate's companies.

    Returns the matched company_job_id when any non-empty company_job_id on a job
    under the candidate's companies appears as a substring of text; else None.
    """
```

Empty/`None` `text` or empty `candidate_id` → return `None` without querying.

SQL:

```sql
SELECT company_job_id FROM job
 WHERE company_job_id IS NOT NULL AND TRIM(company_job_id) != ''
   AND company IN (SELECT short_name FROM company WHERE candidate_id = ?)
   AND ? LIKE '%' || company_job_id || '%'
 LIMIT 1
```

Bind order: `(cid, text)`.

3. Keep `job_link_exists` and `text_matches_known_company_job_id` unchanged (global). Do not delete them.

**Done when (recheck):** Helpers importable; `python3 -m py_compile src/data/database.py` succeeds.

---

## Stage 3: Gazer link filter + ingest gates + candidate dedupe

**Done when:** Link discovery applies exclude then allow; links mode re-checks final URL against excludes, skips non-job visible markers, and dedupes with candidate-scoped helpers; body mode uses candidate-scoped id match; new skip reasons appear in `skipped` and Style D when `debug=True`; single-link / body create path still creates when gates pass.

1. In `src/core/gazer.py` imports from `src.data.database`:  
   - Remove `job_link_exists` and `text_matches_known_company_job_id` if unused after this stage.  
   - Add `job_link_exists_for_candidate` and `text_matches_known_company_job_id_for_candidate`.

2. In `_meteorite_email_candidate_links`, after the existing exclude check (`if any(frag in low for frag in excludes): continue`), apply allow:

```python
    allows = tuple(s.casefold() for s in cfg["link_allow_substrings"])
    ...
        if allows and not any(frag in low for frag in allows):
            continue
```

Do not Playwright-fetch excluded or non-allowed hrefs (they do not enter `links` and do not need `skipped` rows — same silent drop as today's unsubscribe excludes).

3. In `ingest_meteorite_jobs_from_email_html` **links** branch, inside `_one`, after successful Playwright fetch and `link = (final_url or url).strip() or url`, **before** dedupe / min_chars / create, add two gates (use `cfg` already loaded; casefold helpers inline):

**Gate A — final URL exclude (redirect hygiene):**  
- `low_link = link.casefold()`  
- `excludes = tuple(s.casefold() for s in cfg["link_exclude_substrings"])`  
- If `any(frag in low_link for frag in excludes)`: append skipped `{reason: "excluded_link", url: link, matched_company_job_id: None}`; if `debug`, Style D `debug_index` with `outcome="skipped-excluded"` and `debug_detail("reason=excluded_link")`; `return`.

**Gate B — non-job visible text:**  
- `markers = tuple(s.casefold() for s in cfg["non_job_visible_substrings"])`  
- `hay_vis = (text or "").casefold()`  
- If `markers` and `any(m in hay_vis for m in markers)`: append skipped `{reason: "non_job_page", url: link, matched_company_job_id: None}`; if `debug`, Style D `outcome="skipped-non-job"` and `debug_detail("reason=non_job_page")`; `return`.

4. Replace dedupe calls in the **links** branch:  
   - `if job_link_exists(link):` → `if job_link_exists_for_candidate(candidate_id, link):` (same skipped reason `known_job_link`, same Style D).  
   - `matched = text_matches_known_company_job_id(haystack)` → `matched = text_matches_known_company_job_id_for_candidate(candidate_id, haystack)` (same skipped reason `known_company_job_id`).

5. In the **body** branch, replace  
   `matched = text_matches_known_company_job_id(text)`  
   with  
   `matched = text_matches_known_company_job_id_for_candidate(candidate_id, text)`  
   (same skipped shape / Style D). Body mode has no job_link; leave that path without a link-exists check.

6. Keep existing `min_jd_chars` gate, `create_meteorite_job`, concurrency, return shape, and AST-1131 normalize call unchanged. Do not edit `inbox.py`, `api_inbox.py`, or Manage Email UI — they already surface `created` / `skipped`.

7. Style D contract: every new skip path above emits `debug_index` + `debug_detail` only when `debug=True` (same `func="gazer.meteorite_email_ingest"`, `index`/`total`/`identifier` pattern as existing skips). No summary-only replacement for per-link headers.

⚠️ **Decision — silent drop at discovery vs skipped row:** Pre-fetch exclude/allow continue to omit URLs from `links` (no Playwright cost). Post-fetch exclude/non-job use explicit `skipped` reasons so Create toasts can show hygiene skips when a redirect or fat SVG page slips past discovery.

⚠️ **Decision — do not touch qualify or gaze_email orchestration:** AST-1133 owns qualify ERROR bind. `gaze_email` already uses `job_link_exists_for_candidate`; Stage 2 widening is the only intentional shared-helper effect.

**Done when (recheck):**  
- A Dice Saved-jobs HTML (post-1131 normalize) with residual `w3.org` / SVG hrefs yields **zero** created rows with those `job_link`s (filtered or `excluded_link` / `non_job_page`).  
- Re-Create on the same candidate skips known links/ids; a second candidate can still create the same ATS URL.  
- `debug=True` shows per-link Style D for found / skipped / recorded including new skip outcomes.  
- Single-link / body Create that passed before still creates when gates pass.

---

## Self-Assessment

**Scope:** `Single-Component` — config + one data helper pair + gazer ingest path only; no UI/API/qualify.

**Conf:** `high` — reuses existing `METEORITE_EMAIL_INGEST_CONFIG` / Style D / `job_link_exists_for_candidate` patterns; concrete SQL and gate order already established by AST-1061/1131.

**Risk:** `Medium` — wrong exclude/marker lists could over-skip real postings, and widening candidate-scoped link exists affects `gaze_email` callers; empty allow + conservative markers keep the blast radius small.

---

## Rules check (ASTRAL_CODE_RULES)

- §1.3 DRY: shared candidate company subquery pattern from `claim_job_batch`; no duplicated exclude lists in gazer — read config.
- §1.4 / §2.1: all fragments and markers in `METEORITE_EMAIL_INGEST_CONFIG`; no inline magic sets in core.
- §1.5.1: new debug lines gated on `debug=True` Style D only.
- §2.5 / §3.3: Playwright stays in external via existing `_meteorite_fetch_link_visible_text`; decisions stay in core; data helpers have no business branching beyond SQL scope.
- §2.6: create still lands **METEORITE_NEW** via unchanged `create_meteorite_job`; no new job states.
- Out of scope honored: no AST-1131 normalize edits, no AST-1133 qualify, no `tests/` / bible.
