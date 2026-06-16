# AST-713 — Collapse blank lines in gazer visible text saves (Remove empty lines from visible text)

- **Linear (this ticket):** [AST-713](https://linear.app/astralcareermatch/issue/AST-713/collapse-blank-lines-in-gazer-visible-text-saves-remove-empty-lines)
- **Parent:** [AST-710](https://linear.app/astralcareermatch/issue/AST-710/remove-empty-lines-from-visible-text)
- **Publish ref:** `origin/sub/AST-710/AST-713-collapse-blank-lines-gazer`

## Summary

Scraped visible page text often contains long runs of blank or whitespace-only lines between content blocks. This ticket adds a shared **`collapse_blank_lines`** helper in **`src/utils/formatting.py`** and applies it in **`src/core/gazer.py`** on the two batch paths that persist scraped visible text — **`scrape_jd_batch`** (job descriptions) and **`fetch_website_batch`** (homepage text) — immediately after scrape returns and before empty checks, JD prune/classification, and database saves.

## Out of scope (explicit)

| Item | Reason |
|------|--------|
| Playwright / HTML extraction (`extract_visible_text`, `get_visible_text`) | Parent boundary — extraction unchanged |
| `_prune_jd` boilerplate rules | Parent boundary |
| Roster inflow, raw job listing fragments, DOM snapshots, nav link enumerations | Parent boundary |
| Database backfill of existing rows | Parent boundary |
| UI or debug-logging changes | Parent boundary |
| `tests/` or test-bible edits | Betty owns via **`qa-child`** |

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/formatting.py` | Add **`collapse_blank_lines(text: str) -> str`** | utils |
| `src/core/gazer.py` | Import helper; call in **`scrape_jd_batch`** and **`fetch_website_batch`** on scraped visible text before downstream steps | core |

## Stage 1: Add `collapse_blank_lines` in formatting

**Done when:** `collapse_blank_lines` exists with documented behavior; `python3 -m py_compile src/utils/formatting.py` passes; helper is importable from core without config imports.

1. In **`src/utils/formatting.py`**, after **`split_to_list`** (~line 145) and before **`parse_text`**, add:

```python
def collapse_blank_lines(text: str) -> str:
    """Collapse consecutive blank or whitespace-only lines to a single blank line.

    Non-empty lines keep original content and order. Lines where strip() is empty
    count as blank. Returns empty string for None-ish / empty input.
    """
```

2. Implement the body (no config imports — module constraint unchanged):

   a. If `text` is falsy or not a `str`, return `""` (coerce non-str with `str(text)` only when truthy non-str is impossible from callers — callers pass str; use `if not text or not isinstance(text, str): return ""`).

   b. Split with **`text.splitlines()`** (handles `\n` and `\r\n`).

   c. Walk lines left-to-right, building **`out: List[str]`**:
      - If **`line.strip()`** is empty (blank / whitespace-only): append **`""`** to **`out`** only when **`out`** is empty or **`out[-1] != ""`** (skip consecutive blanks).
      - Else: append **`line`** unchanged (do **not** strip non-empty lines).

   d. Return **`"\n".join(out)`**.

3. Do **not** strip leading/trailing blank lines beyond what the collapse algorithm produces (a single leading/trailing blank from one blank line in source is preserved; three consecutive blanks collapse to one).

⚠️ **Decision:** Use **`splitlines` + `"\n".join`** rather than regex — matches existing formatting helpers and avoids platform-specific newline quirks in stored blobs.

⚠️ **Decision:** Function name **`collapse_blank_lines`** (not `strip_excessive_lines`) — matches ticket language and parent AC wording.

## Stage 2: Apply in gazer save paths

**Done when:** Both batch functions normalize scraped visible text before prune/classification/save; `python3 -m py_compile src/core/gazer.py` passes; empty-scrape rejection still works (whitespace-only scrape remains fail after normalize).

1. In **`src/core/gazer.py`**, add import with existing utils imports:

```python
from src.utils.formatting import collapse_blank_lines
```

2. In **`scrape_jd_batch`**, inside **`_scrape_one`**, immediately after:

```python
text = await get_visible_text(url=job_link)
```

insert:

```python
text = collapse_blank_lines(text)
```

before the existing **`if not text or not text.strip():`** empty check (~line 179). Leave **`_prune_jd`**, **`_classify_jd`**, **`save_job_data`**, and transition logic unchanged after that point.

3. In **`fetch_website_batch`**, inside **`_fetch_one`**, immediately after:

```python
visible_text = scrape["visible_text"]
```

insert:

```python
visible_text = collapse_blank_lines(visible_text)
```

before nav link counting and **`save_company_data`** (~line 333). Do **not** modify **`scrape_company_homepage_content`** in roster — normalization stays on the gazer save path only per ticket boundary.

4. Do **not** call **`collapse_blank_lines`** in **`process_gazer_batch`**, **`process_gaze_board_batch`**, **`validate_title_batch`**, or **`scrape_one`** — those paths do not persist full-page visible text blobs per parent scope.

5. Do **not** add logging for normalization (parent: no debug-logging requirements).

## Stage 3: Verification

**Done when:** Compile checks pass; manual spot-check confirms AC behavior.

1. From repo root:

```bash
python3 -m py_compile src/utils/formatting.py src/core/gazer.py
```

2. Interactive sanity (Python REPL or one-liner):

```python
from src.utils.formatting import collapse_blank_lines
assert collapse_blank_lines("a\n\n\n\nb") == "a\n\nb"
assert collapse_blank_lines("a\n   \n\t\nb") == "a\n\nb"
assert collapse_blank_lines("  \n  ") == ""  # or "\n" stripped empty — must be falsy after .strip()
assert collapse_blank_lines("keep\nmiddle\nend") == "keep\nmiddle\nend"
```

3. Confirm **`scrape_jd_batch`** still treats all-whitespace scrape as fail: input that is only blank lines must fail **`if not text or not text.strip()`** after normalization.

⚠️ **Decision:** JD classifier may produce different outcomes when excessive blank lines inflated whitespace metrics — parent AST-710 accepts this; do not add special-case classifier bypass.

## Execution contract (for the developer agent)

- Execute stages in order; one commit per stage on epic worktree, publish to **`origin/sub/AST-710/AST-713-collapse-blank-lines-gazer`** after each stage per **`build-child`** §6.
- Do **not** edit **`tests/`** — Betty adds manifest coverage in **`qa-child`**.
- Blocking ambiguity → comment on **AST-710** parent with 🛑 template from **`plan-child`** §6.

## Self-Assessment

**Scope:** `Single-Component` — One new utils helper plus two call sites in `gazer.py`; no data, UI, or Playwright layer changes.

**Conf:** `high` — Straightforward line-walk helper and two insert points; ticket and parent AC are explicit about boundaries and ordering.

**Risk:** `low` — Wrong collapse logic only affects stored visible text on new scrapes; pass/fail gates still run on normalized blob; classifier edge-case drift is explicitly accepted by parent.

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Single shared helper in formatting; gazer calls it twice — no duplicated collapse logic |
| §2.1 config | No new config keys; behavior is fixed normalization |
| §2.4 batch | No change to claim/process/release pattern |
| §2.6 state machine | Transitions unchanged; only blob content before existing gates |
| §3.3 imports | Core → utils allowed; formatting does not import config |
| §3.5 naming | `collapse_blank_lines` matches domain language |

No conflicts requiring plan revision.
