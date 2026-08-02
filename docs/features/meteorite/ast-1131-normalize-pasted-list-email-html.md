# AST-1131 — Normalize pasted/list email HTML before link discovery

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1131/normalize-pastedlist-email-html-before-link-discovery-manage-email  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1130/manage-email-create-button-for-job-lists-isnt-working  

**Publish ref (origin):** `sub/AST-1130/AST-1131-normalize-pasted-list-email-html`  
**Parent integration ref:** `ftr/AST-1130-manage-email-create-button-for-job-lists-isnt-working`

Owns making Manage Email **Create** discover clean http(s) job-detail URLs from entity-escaped board pastes and Gmail-auto-linkified attribute values (and from simple newline-delimited job-link pastes) **before** `_meteorite_email_candidate_links` runs. Attribute URLs such as SVG `xmlns` must not be promoted into `<a href>` candidates; nested auto-link markup must not remain inside stored `job_link` values. Does **not** own host/path exclude-list policy or non-job create skip (AST-1132) or `qualify_meteorite` apply (AST-1133). Does not redesign `gaze_email`.

**Diagnosis (from parent Original brief):** Paste is stored as entity-escaped text (`&lt;div…`). Gmail then auto-linkifies bare URL substrings inside that text, producing nested anchors inside attribute values, e.g. `href="<a href="https://www.dice.com/job-detail/…">…</a>"` and `xmlns="<a href="http://www.w3.org/2000/svg">…</a>"`. BeautifulSoup then collects those nested anchors (including `w3.org/2000/svg`) as candidate links. Fix order: unescape → unwrap nested auto-links in attributes → promote bare newline URLs when needed → existing link discovery.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Extend `METEORITE_EMAIL_INGEST_CONFIG` with paste-normalize knobs (unescape gate, nested-autolink attrs, bare-URL promote) | utils |
| `src/utils/formatting.py` | Add pure `normalize_pasted_list_email_html(html) -> str` (unescape + unwrap + bare-URL promote) | utils |
| `src/core/inbox.py` | Call normalize on the culled body inside `strip_extract_email_html` before subject wrap | core |
| `src/core/gazer.py` | Call normalize at start of `ingest_meteorite_jobs_from_email_html` before `_meteorite_email_candidate_links`; keep existing Style D per-link logging | core |

No UI, API, Playwright, qualify, exclude-list, or `tests/` / bible changes.

---

## Stage 1: Config knobs for paste normalize

**Done when:** `METEORITE_EMAIL_INGEST_CONFIG` exposes the keys below as importable literals; no formatting/core behavior changes yet.

1. In `src/utils/config.py`, inside the existing `METEORITE_EMAIL_INGEST_CONFIG` dict (after `min_jd_chars`), add:

```python
    # AST-1131: normalize entity-escaped / Gmail-auto-linkified list pastes before link discovery.
    # Unescape only when the body looks entity-escaped (count of marker ≥ threshold).
    "entity_unescape_marker": "&lt;",
    "entity_unescape_min_marker_count": 2,
    "entity_unescape_max_passes": 3,
    # Attribute names whose values may contain nested Gmail auto-link HTML; unwrap to bare URL.
    "nested_autolink_attr_names": ("href", "xmlns", "src", "cite", "data-url"),
    # When True and no http(s) <a href> remain after unwrap, wrap bare http(s) URLs as anchors
    # so newline-delimited link lists enter links mode (not Dice-exclusive).
    "promote_bare_http_urls": True,
```

2. If the top-of-file config inventory lists `METEORITE_EMAIL_INGEST_CONFIG`, extend that one-liner to mention AST-1131 paste normalize.

⚠️ **Decision — extend ingest config, not a new block:** Parent architectural definition says extend `METEORITE_EMAIL_INGEST_CONFIG`. Keeps thresholds next to link discovery knobs; no second config island.

⚠️ **Decision — marker-gated unescape:** Blind `html.unescape` on every email would rewrite legitimate `&amp;` entities. Gate on `&lt;` count so only pasted-as-text board HTML triggers multi-pass unescape.

---

## Stage 2: Pure normalize helper in formatting

**Done when:** `normalize_pasted_list_email_html` is importable from `src.utils.formatting`, is pure (no logging, no I/O), and transforms the three shapes below as specified; no inbox/gazer wiring yet.

1. In `src/utils/formatting.py`, near `normalize_link` / other URL helpers, add:

```python
def normalize_pasted_list_email_html(html: str) -> str:
    """Unescape entity-escaped board pastes, unwrap Gmail nested auto-links in attrs,
    and optionally promote bare http(s) URLs to anchors for link discovery.

    Reads METEORITE_EMAIL_INGEST_CONFIG. Idempotent for already-clean HTML.
    """
```

2. Implement exactly this pipeline (use `import html as html_module` and `import re`; import `METEORITE_EMAIL_INGEST_CONFIG` from `src.utils.config` at function top or module top — match file’s existing import style):

**Step A — entity unescape (gated):**  
- `text = html or ""`.  
- `marker = METEORITE_EMAIL_INGEST_CONFIG["entity_unescape_marker"]`.  
- `min_count = int(METEORITE_EMAIL_INGEST_CONFIG["entity_unescape_min_marker_count"])`.  
- `max_passes = int(METEORITE_EMAIL_INGEST_CONFIG["entity_unescape_max_passes"])`.  
- If `text.count(marker) >= min_count`: for `_ in range(max_passes)`, set `nxt = html_module.unescape(text)`; break when `nxt == text`; else `text = nxt`.

**Step B — unwrap nested Gmail auto-links inside attribute values:**  
For each `attr` in `METEORITE_EMAIL_INGEST_CONFIG["nested_autolink_attr_names"]`, apply a case-insensitive regex replace that turns attribute values whose entire value is a nested anchor into the bare URL.

Concrete pattern (compile once per attr, `re.IGNORECASE | re.DOTALL`):

```text
(?P<prefix>\b{attr}\s*=\s*)(?P<q>["'])\s*<a\b[^>]*\bhref\s*=\s*(?P<q2>["'])(?P<url>https?://[^"']+)(?P=q2)[^>]*>.*?</a>\s*(?P=q)
```

Replacement: `\g<prefix>\g<q>\g<url>\g<q>`  
(Use `attr` interpolated with `re.escape(attr)`.)

Also handle the UAT double-quote breakage form where the outer attribute quote is effectively broken by an inner `href="…"` — after Step A the parent brief shows:

```text
href="<a href="https://www.dice.com/job-detail/UUID">https://www.dice.com/job-detail/UUID</a>"
```

Add a second pass regex (attr-agnostic, applied once after the per-attr loop):

```text
(?P<prefix>\b(?:href|xmlns|src|cite|data-url)\s*=\s*)"\s*<a\b[^>]*\bhref\s*=\s*"(?P<url>https?://[^"]+)"[^>]*>\s*(?P=url)\s*</a>\s*"
```

Replacement: `\g<prefix>"\g<url>"`  
(Build the attr alternation from the same config tuple via `|`.join(`re.escape(a)` for a in nested_autolink_attr_names).)

Do **not** invent vendor-specific Dice path rules here.

**Step C — promote bare http(s) URLs when configured:**  
- If `METEORITE_EMAIL_INGEST_CONFIG["promote_bare_http_urls"]` is false → return `text`.  
- Lazy-import BeautifulSoup only for this check (B1). Parse `text`; if any `a[href]` has `urlparse(href).scheme.casefold()` in `METEORITE_EMAIL_INGEST_CONFIG["link_schemes"]`, return `text` unchanged (board HTML / already-linked email).  
- Otherwise find bare URLs with:

```python
_BARE_URL_RE = re.compile(r"(?P<url>https?://[^\s<>\"']+)", re.IGNORECASE)
```

For each unique URL in first-seen order, if that exact URL string is not already present as an `href="URL"` / `href='URL'` substring, append:

```html
<a href="{url}">{url}</a>
```

joined by `\n` after the original `text` (preserve original text; append promoted anchors so `_meteorite_email_candidate_links` can see them). Strip trailing punctuation commonly stuck to bare URLs (`,`, `.`, `;`, `)`, `]`) from the captured URL before wrapping — strip only from the URL used in `href` and link text, leave the original text as-is.

3. Return `text`.

⚠️ **Decision — pure utils, not core:** Unescape/unwrap/promote is string hygiene with no entity/state decisions. Core stays orchestration; matches `astral.layers.core-vs-external-bright-line` (no new I/O) and keeps the helper reusable/testable without inbox.

⚠️ **Decision — append bare anchors rather than rewrite the whole body:** Avoids destroying JD prose when a forward email has zero anchors but also has narrative URLs later filtered by AST-1132. For a pure newline list, append is equivalent to wrapping.

**Done when (recheck):** Calling the helper on (1) the parent brief’s entity-escaped + nested-autolink fragment yields clean `href="https://www.dice.com/job-detail/…"` with **no** nested `<a>` inside attributes and **no** standalone `xmlns` auto-link left as the only representation of the SVG URL; (2) `"https://example.com/a\nhttps://example.com/b"` yields those URLs as `a[href]` candidates after promote; (3) a normal single-JD HTML body with real anchors is unchanged aside from optional no-op passes.

---

## Stage 3: Wire normalize into strip + ingest

**Done when:** Manage Email Create on the UAT-shaped paste discovers clean Dice (or equivalent) job-detail hrefs; `job_link` values stored for created rows are bare http(s) URLs with no nested auto-link markup; SVG/`xmlns` URLs are not collected as `a[href]` candidates after normalize; newline-delimited link pastes enter `mode=links`; existing Style D per-link `gazer.meteorite_email_ingest` found/skipped/recorded lines still fire when `debug=True`; single-link / single-JD Create that already worked still works.

1. In `src/core/inbox.py`, import `normalize_pasted_list_email_html` from `src.utils.formatting`. Inside `strip_extract_email_html`, after computing `body` from the culled soup (`soup.body.decode_contents()` / `soup.decode_contents()`) and **before** the subject template `.format(...)`, set:

```python
body = normalize_pasted_list_email_html(body)
```

Do not change strip tag/attr cull behavior. Subject wrap stays identical.

2. In `src/core/gazer.py`, import `normalize_pasted_list_email_html` from `src.utils.formatting`. At the top of `ingest_meteorite_jobs_from_email_html`, after the empty-html `ValueError` guard and before `links = _meteorite_email_candidate_links(html)`, set:

```python
html = normalize_pasted_list_email_html(html)
```

Use the normalized `html` for both links mode and body mode (including `_meteorite_email_body_text` / JD payload). Do **not** change `_meteorite_email_candidate_links` exclude-substring logic, Playwright fetch, dedupe, or create — those remain AST-1061 / AST-1132 territory.

3. Preserve existing Style D contract on `gazer.meteorite_email_ingest` and `inbox_create_job` (found / matched / extracted / recorded). Do **not** add summary-only logging that replaces per-link headers. Optional one-line detail under `inbox_create_job` `extracted` is allowed (`normalized_html_len=…`) but not required; if added, gate with `debug=True` only.

4. Do **not** add Dice-only host allowlists, `w3.org` excludes, or “is this a job page?” Playwright heuristics — AST-1132.

⚠️ **Decision — normalize in both strip and ingest:** Strip-first makes the Manage Email debug `extracted` dump show real markup (operator-visible). Ingest-first keeps the gate at the link-discovery boundary if another caller ever feeds HTML without strip. Helper is idempotent so double-call is safe.

⚠️ **Decision — leave relative `/company/…` anchors alone:** After unescape, Dice company profile links remain relative and fail the existing `link_schemes` http(s) filter. Non-job absolute hosts that survive normalize are AST-1132’s exclude policy, not this ticket.

**Done when (recheck):**  
- Replaying the parent UAT paste shape through strip → ingest yields candidate links whose URLs equal clean `https://www.dice.com/job-detail/<uuid>` strings (no nested `<a>` markup inside the URL).  
- `http://www.w3.org/2000/svg` / `https://www.w3.org/2000/svg` does **not** appear in `_meteorite_email_candidate_links` output after normalize (attribute restored; not an anchor).  
- A body of two newline-separated https job URLs runs `mode=links` with those two URLs.  
- A single absolute job-link email and a body-only JD email still create as before.  
- `python3 -m py_compile` on the four touched files succeeds; no new lint issues in those files.

---

## Self-Assessment

**Scope:** `Single-Component` — utils config + formatting hygiene plus thin inbox/gazer call sites on the existing email→meteorite ingest path; no UI/API/qualify changes.

**Conf:** `high` — failure mode is fully diagnosed in the parent UAT HTML/log (entity-escape + nested Gmail auto-links); fix reuses BeautifulSoup/`html.unescape` patterns already in inbox/formatting.

**Risk:** `Medium` — over-eager unescape or bare-URL promote could alter non-list emails; marker gate + “promote only when no http(s) anchors” keep the blast radius small, but a bug here would mis-route Create link discovery.

---

## Rules self-review

| Rule | Status |
|------|--------|
| §1.3 DRY | Normalize once in formatting; inbox + gazer only call it |
| §1.4 / §2.1 config | Unescape thresholds, attr names, promote flag live in `METEORITE_EMAIL_INGEST_CONFIG` — no inline magic sets in core |
| §1.5.1 debug | Existing Style D on ingest preserved; no new ungated debug lines |
| §2.5 / §3.3 layers | Pure string helper in utils; core orchestrates; no external/data imports from utils beyond existing config |
| §2.4 batch / §2.6 state | Untouched — create still lands METEORITE_NEW via existing path |
| Boundaries | No exclude-list (AST-1132), no qualify (AST-1133), no gaze_email redesign |

---

## Review (build stub)

**Publish ref:** `origin/sub/AST-1130/AST-1131-normalize-pasted-list-email-html`
**Plan path:** `docs/features/meteorite/ast-1131-normalize-pasted-list-email-html.md`
**Built tip:** `3ba80bae7a2584e72ae6a10652137608f4f02443` (`3ba80bae`)

| Stage | Commit | Summary |
|-------|--------|---------|
| 1–3 | `3ba80bae` | Config knobs + `normalize_pasted_list_email_html` + strip/ingest wire |
