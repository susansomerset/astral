# AST-713 — Collapse blank lines in gazer visible text saves (Remove empty lines from visible text)

- **Linear (this ticket):** [AST-713](https://linear.app/astralcareermatch/issue/AST-713/collapse-blank-lines-in-gazer-visible-text-saves-remove-empty-lines)
- **Parent:** [AST-710](https://linear.app/astralcareermatch/issue/AST-710/remove-empty-lines-from-visible-text)
- **Publish ref:** `origin/sub/AST-710/AST-713-collapse-blank-lines-gazer` (child of AST-710; not Linear `gitBranchName`)
- **Sibling scope:** none — this ticket covers the full parent functional scope for gazer save paths.

## Summary

Add a shared **`collapse_consecutive_blank_lines`** helper in `src/utils/formatting.py` that collapses runs of two or more consecutive blank lines (including whitespace-only lines) to a single blank line, preserving non-empty line order and content unchanged. Wire it into **`scrape_jd_batch`** and **`fetch_website_batch`** in `src/core/gazer.py` immediately after scrape returns visible text and before empty-text gating, JD prune, classification, and save — so persisted job descriptions and homepage text no longer carry redundant empty rows.

## Out of scope (explicit)

| Item | Note |
|------|------|
| HTML extraction / Playwright scrape | Unchanged |
| `_prune_jd` boilerplate rules | Unchanged |
| Raw job listing fragments, DOM snapshots, nav link enumerations | Not normalized |
| Roster inflow prompt text outside gazer save paths | Unchanged |
| DB backfill of existing rows | Out of scope |
| UI display normalization (e.g. `JobDetailModal`) | Separate; not this ticket |

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/formatting.py` | Add `collapse_consecutive_blank_lines(text: str) -> str` | utils |
| `src/core/gazer.py` | Import helper; apply in `scrape_jd_batch` and `fetch_website_batch` on visible text after scrape | core |
| `tests/component/utils/test_formatting.py` | Unit tests for the new helper | tests (Betty manifest — engineer does not edit in build; listed for QA planning) |

## Stage 1: Shared blank-line normalizer in `formatting.py`

**Done when:** `collapse_consecutive_blank_lines` exists in `src/utils/formatting.py`, has no `config` import, and unit-test cases below pass when Betty adds them (or when engineer runs ad-hoc verification during build).

1. In `src/utils/formatting.py`, after `split_to_list` (~line 145) and before `parse_text`, add:

```python
def collapse_consecutive_blank_lines(text: str) -> str:
    """Collapse runs of blank lines to a single blank line.

    A line is blank when it is empty or contains only whitespace (spaces, tabs).
    Non-empty lines keep their original string (no strip/reformat of content).
    """
    if not text or not isinstance(text, str):
        return "" if text is None else text
    out: List[str] = []
    prev_blank = False
    for line in text.splitlines():
        if not line.strip():
            if not prev_blank:
                out.append("")
            prev_blank = True
        else:
            out.append(line)
            prev_blank = False
    return "\n".join(out)
```

2. Do **not** strip leading/trailing blank lines from the result — only collapse **consecutive** blanks. Example: `"a\n\n\n\nb"` → `"a\n\nb"`; `"  \n\t\nhello"` → `"\nhello"`.

3. Do **not** add any import from `config.py` (existing module constraint).

⚠️ **Decision:** Use line-oriented collapse via `splitlines()` / `"\n".join()` rather than regex — matches existing formatting helpers, avoids `\r\n` edge cases, and keeps whitespace-only detection explicit via `line.strip()`.

## Stage 2: Apply normalizer in `scrape_jd_batch`

**Done when:** Every JD scrape path that persists `job_description` runs visible text through `collapse_consecutive_blank_lines` after `get_visible_text` and before the empty-text gate, `_prune_jd`, min-chars check, classification, and `save_job_data`; pass/fail transitions unchanged for genuinely empty scrapes.

1. In `src/core/gazer.py`, add to imports from `src.utils.formatting`:

```python
from src.utils.formatting import collapse_consecutive_blank_lines
```

(If other symbols are already imported from formatting in this file, extend that import line instead of adding a duplicate.)

2. In `scrape_jd_batch`, inside `_scrape_one`, immediately after the successful `get_visible_text` call (~line 164) and **before** the `if not text or not text.strip():` empty check (~line 179), insert:

```python
        text = collapse_consecutive_blank_lines(text)
```

3. Do **not** move the empty check before normalization — normalization must run first per parent scope ("immediately after scrape"), but empty rejection still uses `not text.strip()` so whitespace-only or all-blank captures remain failures (AC #4).

4. Do **not** change `_prune_jd`, `_classify_jd`, min_chars gate, debug logging, or state transitions in this stage.

## Stage 3: Apply normalizer in `fetch_website_batch`

**Done when:** Homepage visible text saved to `homepage_text` is normalized; `nav_links` and other fields are untouched; batch pass/fail behavior unchanged.

1. In `fetch_website_batch`, inside `_fetch_one`, after `visible_text = scrape["visible_text"]` (~line 331) and **before** building `data_to_save`, insert:

```python
            visible_text = collapse_consecutive_blank_lines(visible_text)
```

2. Do **not** normalize `nav_links` or `enumerated_nav_links`.

3. Do **not** add a new empty-text fail gate in this ticket — `fetch_website_batch` has no empty-text rejection today; normalization must not invent content (all-blank input stays all-blank).

## Stage 4: Verification (build agent — no test file edits)

**Done when:** Engineer confirms behavior manually or via existing test run; Betty owns `tests/component/utils/test_formatting.py` additions in QA pass.

Expected test cases for Betty (reference only — do not commit from engineer):

| Input | Expected output |
|-------|-----------------|
| `"line1\n\n\nline2"` | `"line1\n\nline2"` |
| `"line1\n \n\t\nline2"` | `"line1\n\nline2"` |
| `"line1\nline2"` | `"line1\nline2"` |
| `"  content  "` | `"  content  "` |
| `""` | `""` |
| `"\n\n\n"` | `""` |
| `"only"` | `"only"` |

## Self-Assessment

**Scope:** `Single-Component` — touches one utils helper and two call sites in `gazer.py`; no config, UI, or database schema changes.

**Conf:** `high` — straightforward line-walk utility with explicit insertion points already identified in existing batch functions.

**Risk:** `low` — wrong collapse logic would only affect stored visible text formatting; empty-scrape gates remain intact via existing `text.strip()` checks on the JD path.

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Single shared helper in `formatting.py`; both gazer paths call it — no duplicate regex in core |
| §2.1 config | No new config keys; helper lives in formatting without config import |
| §2.4 batch | Normalizer applied inside existing per-item scrape handlers — no batch lifecycle change |
| §2.6 state machine | No transition or state name changes |
| §3.3 imports | `gazer.py` (core) imports `formatting.py` (utils) — allowed direction |
| §3.5 naming | `collapse_consecutive_blank_lines` describes behavior; matches ticket language |

No conflicts requiring `Conf: !!-NONE`.

## Review stub

| Field | Value |
|-------|-------|
| **Publish ref** | `origin/sub/AST-710/AST-713-collapse-blank-lines-gazer` |
| **Built tip** | `8740dead` |
| **Stages** | 1 — `collapse_consecutive_blank_lines` in `formatting.py` (`29e41c98`); 2 — `scrape_jd_batch` post-scrape normalize (`8740dead`); 3 — `fetch_website_batch` homepage normalize (`8740dead`) |
| **Stage 4** | Manual case table verified in build (`python3 -c` against plan cases — all pass) |
| **Betty next** | `tests/component/utils/test_formatting.py` per plan Stage 4 reference table |

## Radia review (2026-06-16)

**Diff:** `origin/dev...origin/sub/AST-710/AST-713-collapse-blank-lines-gazer` @ `554db853`

### What's solid

- Plan Stages 1–3 implemented exactly: `collapse_consecutive_blank_lines` in `formatting.py` (no `config` import); `scrape_jd_batch` normalizes after successful `get_visible_text` and before empty-text gate / `_prune_jd`; `fetch_website_batch` normalizes `homepage_text` only — `nav_links` untouched.
- Acceptance criteria covered: consecutive blank/whitespace-only runs collapse to one blank line; non-empty line order and content preserved; all-whitespace input still fails JD empty gate via `not text.strip()` after normalize.
- Layer compliance (§3.3): core → utils import only; utils helper is pure (no cross-layer imports).
- Tests manifest-aligned: unit cases match plan Stage 4 table; gazer integration tests assert collapsed save payloads on both batch paths.
- Self-Assessment footprint matches diff (`Single-Component`, low risk).

### Issues

| Severity | Location | Note |
|----------|----------|------|
| — | — | No fix-now or discuss items |

### Recommended actions

| Action | Owner | Note |
|--------|-------|------|
| — | — | Ready for `resolve-child` / merge when pipeline says so |

**Advisory (non-blocking):** `collapse_consecutive_blank_lines` passthrough for non-`str` inputs (`return text` when not `None`) mirrors defensive patterns in sibling formatting helpers; production scrape paths always pass `str`. Optional future tighten: return `""` for non-str or drop the branch if callers are typed.
