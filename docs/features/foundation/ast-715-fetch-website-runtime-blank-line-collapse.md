# AST-715 — UAT: fetch_website saves skip blank-line collapse at runtime (Remove empty lines from visible text)

- **Linear (this ticket):** [AST-715](https://linear.app/astralcareermatch/issue/AST-715/uat-fetch-website-saves-skip-blank-line-collapse-at-runtime-remove)
- **Parent:** [AST-710](https://linear.app/astralcareermatch/issue/AST-710/remove-empty-lines-from-visible-text)
- **Publish ref:** `origin/sub/AST-710/AST-715-fetch-website-runtime-blank-line-collapse` (child of AST-710; not Linear `gitBranchName`)

## Summary

Susan's UAT shows freshly saved `company_data.homepage_text` still contains consecutive blank lines after `fetch_website_batch`, while `backfill_collapse_blank_lines.py` reports the same row would change. **AST-713** added `collapse_consecutive_blank_lines` in `fetch_website_batch` only; the **AST-701** shared scrape helper `scrape_company_homepage_content` still returns raw Playwright visible text. Move normalization into that helper (immediately after scrape, before empty-text rejection) so every homepage scrape consumer — including `fetch_website_batch` persistence — receives collapsed text at the single DRY boundary. Simplify `fetch_website_batch` to save the helper output without a second collapse call (idempotent either way; one site is the contract).

## Out of scope (explicit)

| Item | Note |
|------|------|
| Backfill script (**AST-714**) | Unchanged |
| JD scrape path (`scrape_jd_batch`) | Already normalizes in gazer; ticket boundaries exclude unless same root cause |
| `collapse_consecutive_blank_lines` algorithm | Reuse as-is |
| UI, admin API, config, database schema | No changes |
| Historical rows | Backfill remains for pre-fix data |

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/roster.py` | Normalize visible text inside `scrape_company_homepage_content` | core |
| `src/core/gazer.py` | Remove redundant collapse in `fetch_website_batch` (helper now owns it) | core |

## Stage 1: Normalize at shared homepage scrape helper

**Done when:** `scrape_company_homepage_content` returns collapsed `visible_text` for non-empty scrapes; empty / whitespace-only scrapes still set `error` and do not persist; `fetch_website_batch` saves collapsed `homepage_text` on a fresh scrape without needing backfill.

1. In `src/core/roster.py`, add import at top with existing roster imports (utils layer allowed):

```python
from src.utils.formatting import collapse_consecutive_blank_lines
```

(If `formatting` is already imported for other symbols, extend that line.)

2. In `scrape_company_homepage_content`, after the successful `get_visible_text` call and redirect handling (`out["company_website"] = company_website` block, ~lines 1024–1027), **before** assigning `out["visible_text"]` and **before** the empty-text gate, insert:

```python
    visible_text = collapse_consecutive_blank_lines(visible_text or "")
    out["visible_text"] = visible_text
    if not visible_text.strip():
        out["error"] = "No visible text extracted"
        return out
```

3. **Remove** the old pattern that assigned raw text then checked empty separately:

```python
    out["visible_text"] = visible_text or ""
    if not out["visible_text"].strip():
        out["error"] = "No visible text extracted"
        return out
```

Replace with step 2 so collapse runs **before** empty rejection (same ordering as `scrape_jd_batch` in **AST-713**).

4. Do **not** normalize `enumerated_nav_links`. Do **not** change nav scrape error handling.

⚠️ **Decision:** Normalize in `scrape_company_homepage_content` (roster) rather than only in `fetch_website_batch` (gazer) because **AST-701** made this helper the single homepage scrape entry; `prefilter_company` and `fetch_website_batch` both call it. Collapse at the helper guarantees runtime saves and downstream live_content assembly cannot miss normalization.

## Stage 2: Simplify `fetch_website_batch` save path

**Done when:** `fetch_website_batch` persists `scrape["visible_text"]` directly without a duplicate collapse call; existing gazer integration test expectations unchanged.

1. In `src/core/gazer.py`, inside `_fetch_one` (~line 333), replace:

```python
            visible_text = collapse_consecutive_blank_lines(scrape["visible_text"])
```

with:

```python
            visible_text = scrape["visible_text"]
```

2. Keep `collapse_consecutive_blank_lines` import in `gazer.py` — still required for `scrape_jd_batch` (~line 180).

3. Do **not** change pass/fail transitions, `nav_links` handling, or debug logging.

## Stage 3: Build verification (engineer — no test file edits)

**Done when:** Manual smoke confirms collapsed save without backfill.

1. Compile: `python3 -m py_compile src/core/roster.py src/core/gazer.py`

2. Run Betty's existing manifest when available (reference):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_gazer.py::TestFetchWebsiteBatch::test_collapses_consecutive_blank_lines_in_homepage_text \
  -q
```

3. Optional local repro (`.venv/bin/python`):

```python
# Monkey-free: patch get_visible_text in a one-off or use dispatch on a WEBSITE_FOUND company
# After fetch_website_batch, inspect company_data.homepage_text — at most one blank between blocks.
# backfill --company <short_name> --dry-run should report unchanged for that row.
```

4. Do **not** edit `tests/` or `docs/test-bible/**` — Betty may add `TestAst701ScrapeCompanyHomepageContent` collapse case in QA pass.

## Self-Assessment

**Scope:** `Single-Component` — two core files; helper choke point + remove duplicate gazer line.

**Conf:** `high` — mirrors **AST-713** JD pattern (collapse immediately after scrape, before empty gate); addresses UAT gap by enforcing normalization at the shared **AST-701** scrape boundary.

**Risk:** `low` — idempotent helper; empty-text rejection unchanged; JD path untouched; backfill remains for historical rows.

## ASTRAL_CODE_RULES self-review

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Single normalize site for homepage scrape output; gazer no longer duplicates |
| §2.1 config | No new config keys |
| §2.4 batch | No batch lifecycle change |
| §2.6 state machine | No transition changes |
| §3.3 imports | roster (core) → formatting (utils); allowed |
| §3.5 naming | No new symbols |

No conflicts flagged.
