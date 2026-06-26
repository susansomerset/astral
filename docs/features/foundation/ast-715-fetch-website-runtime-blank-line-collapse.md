<!-- linear-archive: AST-715 archived 2026-06-23 -->

## Linear archive (AST-715)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-715/uat-fetch-website-saves-skip-blank-line-collapse-at-runtime-remove  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-710 — Remove empty lines from visible text  
**Blocked by / blocks / related:** parent: AST-710

### Description

## What failed

After **AST-713** landed, Susan ran `fetch_website_batch` (and related fetch-website flows) from current code. Newly saved `company_data.homepage_text` still contained consecutive blank lines that `backfill_collapse_blank_lines.py` subsequently removed — runtime gazer normalization is not taking effect on the website-fetch save path.

## Expected

Every gazer path that persists scraped homepage visible text applies `collapse_consecutive_blank_lines` immediately after scrape and **before** save, so a fresh `fetch_website` run writes already-normalized text (at most one blank line between content blocks). No backfill needed for new scrapes.

## Repro

1. Pick a company whose homepage scrape produces multiple consecutive blank lines in raw visible text.
2. Run `fetch_website_batch` from the deployed/local app code (not the backfill script).
3. Inspect saved `company_data.homepage_text` — observe multiple consecutive blank lines remain.
4. Run `scripts/migrations/backfill_collapse_blank_lines.py --company <short_name> --dry-run` — script reports the same row would change.

## Parent AC (quoted inline)

> 3. Persisted job descriptions from JD scrape batches and homepage text from website fetch batches reflect normalized text, verifiable by inspecting saved records after a scrape run.

> 1. Given visible text with three or more consecutive blank lines (or whitespace-only lines) between content, the normalizer produces at most one blank line between those blocks.

## Boundaries

* This bug does **not** change: backfill script behavior (**AST-714**), JD scrape paths unless the same root cause applies there, HTML extraction, or UI.
* Does **not** require re-running backfill for historical rows — fix forward runtime saves only (backfill remains for existing data).
* Reuse `collapse_consecutive_blank_lines` from `src/utils/formatting.py`.

### Comments

#### betty — 2026-06-17T20:53:07.717Z
## QA test manifest (AST-715)

**Publish ref:** `origin/sub/AST-710/AST-715-fetch-website-runtime-blank-line-collapse` @ `3c10b0b`
**Tests SHA:** `2da5b59` (`merge-tests(AST-715): origin/tests 2da5b59`)

1. **Collapse at shared scrape helper (required):**
```bash
./scripts/testing/run_component_tests.sh tests/component/core/test_roster.py::TestAst701ScrapeCompanyHomepageContent::test_collapses_consecutive_blank_lines_at_scrape -q
```

2. **Gazer fetch_website passthrough (required):**
```bash
./scripts/testing/run_component_tests.sh tests/component/core/test_gazer.py::TestFetchWebsiteBatch::test_persists_normalized_visible_text_from_scrape_helper -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate unless widened.

**Bible shasums (publish ref):**
- `docs/test-bible/core/roster.md` → `1806162e0fe51819f12b0f1ae884a9197be6bcb6`
- `docs/test-bible/core/gazer.md` → `f8441ea2cde9ea8406f0df02aa4ca5a6995bcce8`

**Coverage delta:**
- `test_collapses_consecutive_blank_lines_at_scrape` — UAT fix: normalize in `scrape_company_homepage_content`
- Replaced AST-713 gazer collapse test with `test_persists_normalized_visible_text_from_scrape_helper` (helper owns normalize)
- Updated **AST-713** bible block: JD path only; homepage → **AST-715**

— Betty

#### hedy — 2026-06-17T20:49:23.160Z
Plan doc: https://github.com/susansomerset/astral/blob/sub/AST-710/AST-715-fetch-website-runtime-blank-line-collapse/docs/features/foundation/ast-715-fetch-website-runtime-blank-line-collapse.md

**Scope:** Single-Component — move `collapse_consecutive_blank_lines` into `scrape_company_homepage_content`; remove redundant call in `fetch_website_batch`.

**Conf:** high — UAT repro is explicit; fix aligns with AST-701 shared-scrape DRY and parent “immediately after scrape” AC.

**Risk:** low — idempotent helper; empty-scrape gate unchanged; JD path untouched in this bug fix.

#### hedy — 2026-06-17T20:48:29.649Z
Plan: [`docs/features/foundation/ast-715-fetch-website-runtime-blank-line-collapse.md`](https://github.com/susansomerset/astral/blob/sub/AST-710/AST-715-fetch-website-runtime-blank-line-collapse/docs/features/foundation/ast-715-fetch-website-runtime-blank-line-collapse.md) on `origin/sub/AST-710/AST-715-fetch-website-runtime-blank-line-collapse` @ `0fac0600`.

**Self-assessment**
- **Scope:** Single-Component — `scrape_company_homepage_content` in `roster.py` + remove duplicate collapse line in `gazer.fetch_website_batch`.
- **Conf:** high — move normalization to AST-701 shared scrape boundary (same post-scrape / pre-empty-gate ordering as AST-713 JD path).
- **Risk:** low — idempotent helper; no state/config changes; JD and backfill paths untouched.

---

# AST-715 — UAT: fetch_website saves skip blank-line collapse at runtime (Remove empty lines from visible text)

- **Linear (this ticket):** [AST-715](https://linear.app/astralcareermatch/issue/AST-715/uat-fetch-website-saves-skip-blank-line-collapse-at-runtime-remove)
- **Parent:** [AST-710](https://linear.app/astralcareermatch/issue/AST-710/remove-empty-lines-from-visible-text)
- **Publish ref:** `origin/sub/AST-710/AST-715-fetch-website-runtime-blank-line-collapse` (child of AST-710; not Linear `gitBranchName`)
- **Related shipped work:** [AST-713](https://linear.app/astralcareermatch/issue/AST-713) — `collapse_consecutive_blank_lines` + gazer `fetch_website_batch` wiring; [AST-714](https://linear.app/astralcareermatch/issue/AST-714) — backfill script (out of scope here)

## Summary

Susan UAT: after **AST-713**, fresh `fetch_website` dispatch runs still persist `company_data.homepage_text` with consecutive blank lines; `scripts/migrations/backfill_collapse_blank_lines.py --dry-run` reports the same rows would change. **AST-713** applied collapse only in `gazer.fetch_website_batch` on the dict returned from `roster.scrape_company_homepage_content`, but parent **AST-710** requires normalization **immediately after scrape** on the shared homepage scrape helper (the single source for `visible_text` per **AST-701**). This bug fix moves homepage blank-line collapse into `scrape_company_homepage_content` and removes the redundant gazer-layer call so every runtime consumer of scraped homepage text — including `fetch_website_batch` — persists already-normalized text.

## Out of scope (explicit)

| Item | Note |
|------|------|
| `scripts/migrations/backfill_collapse_blank_lines.py` | **AST-714** — historical rows only |
| JD scrape (`scrape_jd_batch` / `job_description`) | Susan repro is homepage-only; JD path unchanged unless Betty finds a parallel gap |
| Playwright / HTML extraction | Unchanged |
| `nav_links`, `website_content`, prefilter LLM `live_content` assembly | Unchanged |
| UI display normalization | Unchanged |

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/roster.py` | Import `collapse_consecutive_blank_lines`; normalize `visible_text` in `scrape_company_homepage_content` after `get_visible_text`, before empty-text error gate | core |
| `src/core/gazer.py` | Remove redundant `collapse_consecutive_blank_lines` call in `fetch_website_batch` (use normalized `scrape["visible_text"]` directly) | core |

**Betty (reference only — engineer does not edit in build):** extend `tests/component/core/test_roster.py::TestAst701ScrapeCompanyHomepageContent` for collapse-at-scrape; adjust `test_gazer.py::TestFetchWebsiteBatch::test_collapses_consecutive_blank_lines_in_homepage_text` if mock expectations change (helper now returns collapsed text).

## Stage 1: Normalize at shared homepage scrape helper

**Done when:** `scrape_company_homepage_content` returns collapsed `visible_text`; empty-scrape error gate unchanged; `python3 -m py_compile src/core/roster.py` passes.

1. In `src/core/roster.py`, add import (with existing utils imports):

```python
from src.utils.formatting import collapse_consecutive_blank_lines
```

2. In `scrape_company_homepage_content`, after the successful `get_visible_text` assignment block (~lines 1018–1027) and **before** `out["visible_text"] = visible_text or ""` (~line 1028), insert:

```python
    visible_text = collapse_consecutive_blank_lines(visible_text or "")
```

3. Keep the existing empty check immediately after setting `out["visible_text"]`:

```python
    out["visible_text"] = visible_text
    if not out["visible_text"].strip():
        out["error"] = "No visible text extracted"
        return out
```

(Replace `out["visible_text"] = visible_text or ""` with `out["visible_text"] = visible_text` since collapse already coerces non-str/empty.)

4. Do **not** normalize `enumerated_nav_links`.

⚠️ **Decision:** Collapse lives in **`scrape_company_homepage_content`** (roster), not only in gazer — matches parent “immediately after scrape” and **AST-701** shared-helper DRY; `prefilter_company` callers receive normalized text for LLM assembly without a second code path.

## Stage 2: Remove redundant gazer-layer collapse

**Done when:** `fetch_website_batch` persists `scrape["visible_text"]` without re-calling collapse; `python3 -m py_compile src/core/gazer.py` passes.

1. In `fetch_website_batch` `_fetch_one`, replace:

```python
            visible_text = collapse_consecutive_blank_lines(scrape["visible_text"])
```

with:

```python
            visible_text = scrape["visible_text"]
```

2. If `collapse_consecutive_blank_lines` is no longer referenced in `gazer.py`, remove it from the `src.utils.formatting` import line (keep import if `scrape_jd_batch` still uses it).

3. Do **not** change `scrape_jd_batch` normalization in this ticket.

## Stage 3: Verification (build agent — no test file edits)

**Done when:** Manual checks below pass on epic worktree; Betty owns component test updates in **qa-child**.

1. Compile:

```bash
python3 -m py_compile src/core/roster.py src/core/gazer.py
```

2. Helper unit sanity (same cases as **AST-713** Stage 4 table):

```python
from src.utils.formatting import collapse_consecutive_blank_lines
assert collapse_consecutive_blank_lines("line1\n\n\nline2") == "line1\n\nline2"
```

3. Async helper check (Python REPL or one-liner with mocks): monkeypatch `get_visible_text` to return `("intro\n\n\n\nbody", "https://acme.com")`; call `scrape_company_homepage_content("acme", "https://acme.com")`; assert `out["visible_text"] == "intro\n\nbody"` and `out["error"] is None`.

4. **Susan UAT repro (manual):** after deploy/restart of local app from this branch, run `fetch_website` dispatch for a company whose raw scrape has consecutive blank lines; inspect saved `homepage_text`; run `python scripts/migrations/backfill_collapse_blank_lines.py --company <short_name> --dry-run` — expect **unchanged** (no would-update line) for that fresh row.

## Execution contract (for the developer agent)

- Execute stages in order; one commit per stage on epic worktree; publish to **`origin/sub/AST-710/AST-715-fetch-website-runtime-blank-line-collapse`** after each stage per **build-child** §6.
- Do **not** edit `tests/` or `docs/test-bible/**` — Betty owns manifest updates.
- Blocking ambiguity → comment on **AST-710** parent with 🛑 template from **plan-child** §6.

## Self-Assessment

**Scope:** `Single-Component` — one roster helper change and one-line removal in gazer; no config, DB, or UI.

**Conf:** `high` — UAT repro is explicit; root cause is collapse applied only at gazer save wrapper instead of shared scrape helper; fix is a single move per **AST-701** architecture.

**Risk:** `low` — `collapse_consecutive_blank_lines` is idempotent; `prefilter_company` receives the same normalized blob gazer would have saved; empty-scrape gate still uses `.strip()` after normalize.

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | One collapse site for homepage scrape output; remove duplicate gazer call |
| §2.1 config | No new config |
| §2.4 batch | No batch lifecycle change |
| §2.6 state machine | No transition changes |
| §3.3 imports | `roster` → `formatting` allowed |
| §3.5 naming | Reuse existing helper name |

No conflicts requiring `Conf: !!-NONE`.

## Review stub

| Field | Value |
|-------|-------|
| **Publish ref** | `origin/sub/AST-710/AST-715-fetch-website-runtime-blank-line-collapse` |
| **Built tip** | `e8fcf9a` |
| **Stages** | 1 — `scrape_company_homepage_content` collapse (`af07653`); 2 — remove gazer duplicate (`e8fcf9a`) |
| **Betty next** | `TestAst701ScrapeCompanyHomepageContent` collapse-at-scrape; adjust gazer fetch test if needed |
