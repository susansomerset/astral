# AST-1213 — AI payload as visible text and links

**Linear:** [AST-1213](https://linear.app/astralcareermatch/issue/AST-1213/ai-payload-as-visible-text-and-links-rename-task-to-meteorite-email-ai)
**Parent:** [AST-1182](https://linear.app/astralcareermatch/issue/AST-1182/rename-task-to-meteorite-email-ai-payload-as-visible-textlinks) — Rename task to meteorite_email + AI payload as visible text/links
**Publish ref:** `origin/sub/AST-1182/AST-1213-ai-payload-as-visible-text-and-links`

After the AST-1212 rename, assemble the `meteorite_email` live payload as **visible text plus links** (same content shape as JD-scrape / `select_job_page` page sections — not raw HTML markup), and rewrite Ruth’s `agent_task` prompts so she expects that shape. Parse modes, response schema, task key, and post-parse ingest/archive behavior stay as they are today.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/gaze_email.py` | Assemble Ruth `live_content` body as visible text + enumerated links (reuse gazer email helpers); Style D detail for found/recorded payload when `debug=True` | core |
| `data/admin/agent_task.json` | Rewrite `meteorite_email` `cache_prompt` / `user_prompt` so CONTENT is visible text + links, not raw HTML | data/admin |
| `docs/uat-fixtures/AST-756/expected-agent_task.json` | Surgical sync of that same row’s prompt fields (+ `updated_at` if bumped) — **no** whole-file `cp` | docs |

**No changes expected:** `src/utils/config.py` (task key / parse modes / response schema already `meteorite_email`), `src/core/agent.py`, `src/core/gazer.py` (reuse existing private helpers only — do not edit gazer), dispatcher, Gmail external, frontend, evaluate_meteorite / UI grouping siblings, `tests/` / bible (Betty after Code Complete). Do **not** Playwright-scrape the inbox; extraction is from the message HTML already fetched via `get_message_html`.

## Stage 1: `gaze_email` — Ruth live payload = visible text + links

**Done when:** For both `html_links` and `subject_body` branches in `_handle_bound`, the string passed to `_ruth_parse` / `do_task` as `live_content` starts with the existing `PARSE_MODE:` (and `SUBJECT:` for subject_body) header lines, then a body that contains **no raw HTML tags as the primary content** — visible text plus an optional `--- LINKS ---` enumerated URL list. `subject_url` / ignore shapes are unchanged. `python3 -m py_compile src/core/gaze_email.py` succeeds (repo venv: `~/astral/.venv/bin/python`).

1. In `src/core/gaze_email.py`, extend the gazer import to also pull `_meteorite_email_body_text` and `_meteorite_email_candidate_links` (same module already imports `_meteorite_fetch_link_visible_text`). Do **not** copy-paste those helpers into `gaze_email`.

2. Add a private helper (place with the other module privates above `_ruth_parse`):

```python
def _ruth_live_body(html: str) -> str:
    """Visible text + links for Ruth (JD-scrape payload shape; not raw HTML)."""
```

Implementation (literal):

- `text = _meteorite_email_body_text(html)` (newline-separated visible text from the email HTML).
- `links = _meteorite_email_candidate_links(html)` (ordered unique http(s) hrefs minus `METEORITE_EMAIL_INGEST_CONFIG` excludes/allow — same list gazer uses for ingest link discovery).
- Build parts:
  - If `text.strip()`: start with that text; else start with the literal `(no visible text)` (same sentinel style as roster PJL scrape sections).
  - If `links` non-empty: append a line `--- LINKS ---`, then one line per link as `f"{i}. {lnk}"` with `i` starting at 1 (mirror roster `_fetch_job_links_content` `--- NEW LINKS ---` enumeration).
  - If `links` empty: do **not** append a `--- LINKS ---` section.
- Return `"\n".join(parts)`.

⚠️ **Decision — reuse gazer helpers, do not reimplement link filters:** Parent requires the JD-scrape *payload shape* (visible text + links), not a new link-hygiene policy. `_meteorite_email_candidate_links` already applies `METEORITE_EMAIL_INGEST_CONFIG` scheme/exclude/allow rules; duplicating that list in `gaze_email` would violate DRY and drift from ingest.

⚠️ **Decision — section marker `--- LINKS ---` (not `--- NEW LINKS ---`):** Email has no “nav vs new” split; one link list is enough. Keep the triple-dash header style so the shape stays recognizable next to roster PJL live content.

⚠️ **Decision — keep local `_body_text` for emptiness + create-path JD suffix:** `_body_is_empty` and the subject_body `jd_suffix` / no-link create path continue to use existing `_body_text(html)`. This ticket only changes what Ruth sees in `live_content`, not the text appended to scraped JDs or the empty-body gate.

3. In `_handle_bound`, replace the two raw-HTML live assemblies:

- **html_links** (today: `live = f"PARSE_MODE: {html_mode}\n\n{html}"`):
  - `body = _ruth_live_body(html)`
  - `live = f"PARSE_MODE: {html_mode}\n\n{body}"`
- **subject_body** (today: `live = f"PARSE_MODE: {subject_mode}\nSUBJECT: {subject}\n\n{html}"`):
  - `body = _ruth_live_body(html)`
  - `live = f"PARSE_MODE: {subject_mode}\nSUBJECT: {subject}\n\n{body}"`

Do **not** change shape routing, `_ruth_parse` args other than `live`, ingest loop, archive finalize, or `subject_url`.

4. **Style D when `debug=True`:** immediately before each `_ruth_parse` call on those two branches (after `live` is built):

- `_detail(debug, f"ruth_payload visible_chars={len(_meteorite_email_body_text(html))} links={len(_meteorite_email_candidate_links(html))}")` — **or** compute `text`/`links` once inside `_ruth_live_body` and return them for detail (preferred: have `_ruth_live_body` return only the string, and call the two gazer helpers once in the branch to avoid double-parse — see next bullet).
- Prefer a single extraction: either (a) `_ruth_live_body` returns `(body, visible_chars, link_count)` or (b) a tiny `_ruth_live_parts(html) -> tuple[str, str, list[str]]` used by both assembly and debug. Pick **(b)**:

```python
def _ruth_live_parts(html: str) -> tuple[str, list[str]]:
    """Return (visible_text, candidate_links) from email HTML."""
    return _meteorite_email_body_text(html), _meteorite_email_candidate_links(html)

def _ruth_live_body(html: str) -> str:
    text, links = _ruth_live_parts(html)
    ...
```

Then in each Ruth branch:

```python
text, links = _ruth_live_parts(html)
body = _format_ruth_live_body(text, links)  # or inline format in _ruth_live_body(text, links)
live = f"PARSE_MODE: ...\n\n{body}"  # subject_body adds SUBJECT line as today
_detail(debug, f"ruth_payload visible_chars={len(text)} links={len(links)}")
for line in truncate_debug_content(live):
    _detail(debug, line)
```

Keep helper naming tight: at most two privates (`_ruth_live_parts` + `_format_ruth_live_body`, or one `_ruth_live_body` that formats and a debug-only recount is **not** preferred). Final shape: **`_ruth_live_parts` + `_format_ruth_live_body(text, links) -> str`**.

⚠️ **Decision — emit truncated live payload under Style D detail:** Parent AC requires found/recorded visibility when this hop’s `debug=True` paths are touched. Summary line = found; `truncate_debug_content(live)` lines = recorded payload (50-line contract). Do **not** add new `logger.info("[DEBUG] …")` lines.

5. Update the module docstring one line to note AST-1213: Ruth live payload is visible text + links (not raw HTML).

**Done when (recheck):**

```bash
~/astral/.venv/bin/python - <<'PY'
import asyncio
from unittest.mock import AsyncMock, patch
from src.core import gaze_email as ge

html = '<p>Hello <a href="https://jobs.example.com/j/1">Role</a></p><a href="mailto:x@y.z">x</a>'
text, links = ge._ruth_live_parts(html)
assert "Hello" in text and "Role" in text
assert "<p>" not in text and "<a" not in text
assert links == ["https://jobs.example.com/j/1"]
body = ge._format_ruth_live_body(text, links)
assert "--- LINKS ---" in body
assert "1. https://jobs.example.com/j/1" in body
assert "<p>" not in body
# live wrappers still prefix PARSE_MODE / SUBJECT
assert ge._format_ruth_live_body("", []).startswith("(no visible text)")
print("ok")
PY
~/astral/.venv/bin/python -m py_compile src/core/gaze_email.py
```

(If the plan’s helper names differ by one rename, adjust the smoke script to match the names actually committed — names above are binding.)

**Ritual:** `code(AST-1213): Ruth live payload visible text + links`

## Stage 2: Ruth prompts expect visible text + links

**Done when:** Current `meteorite_email` row in `data/admin/agent_task.json` describes CONTENT as visible text plus a `--- LINKS ---` list (not “HTML body” / “email HTML”); `user_prompt` no longer says “absent from the HTML”; AST-756 fixture row matches those prompt strings; catalog vs fixture drift outside this row is untouched.

1. Snapshot before edit (local `/tmp` only — do not commit):

```bash
cp data/admin/agent_task.json /tmp/agent_task.pre-ast-1213.json
cp docs/uat-fixtures/AST-756/expected-agent_task.json /tmp/expected-agent_task.pre-ast-1213.json
```

2. In `data/admin/agent_task.json`, locate the single `current == 1` object with `task_key == "meteorite_email"`. Rewrite **`cache_prompt`** and **`user_prompt`** only (optionally bump `updated_at` to current UTC `YYYY-MM-DD HH:MM:SS`). Do **not** change `task_key`, `task_name`, `task_key_uuid`, grouping, `task_seq`, `agent_id`, empty prompt slots, or any other row.

**`cache_prompt` binding content** (keep `## INSTRUCTIONS` header style; exact wording may be tightened for clarity but must include every bullet below):

- Still: mechanical meteorite email parse; `PARSE_MODE: html_links` | `subject_body` on the first CONTENT line; echo into response `parse_mode`.
- **Replace** any instruction that says the body is HTML / “email HTML” / “HTML body is the job source”.
- State that after the header line(s), CONTENT is **visible text** extracted from the message, optionally followed by a `--- LINKS ---` section of numbered `http(s)` URLs (same shape as JD-scrape visible text + links — not markup).
- **html_links:** Use visible text + `--- LINKS ---` to extract every distinct meteorite **job** link worth scraping; skip obvious non-job noise when clearly not a posting; return `{job_link, job_title?, metadata?}` in `jobs` with optional `metadata` object `company` / `location`; prefer empty `jd_link` / `content_text`.
- **subject_body:** CONTENT includes `SUBJECT:` then visible text (+ optional links). Return `content_text` = usable subject + body text; set `jd_link` when one likely JD URL is present; prefer `jobs: []`.
- Always valid JSON only; do **not** invent links absent from CONTENT (visible text or LINKS list); do **not** copy qualify_meteorite’s astral_job_id contract.

**`user_prompt` binding** (one string): ask Ruth to parse CONTENT per `PARSE_MODE` and return JSON with `parse_mode`, `jobs`, optional `jd_link` / `content_text`; do not scrape or invent URLs absent from the CONTENT; do not emit grade vectors. Must **not** say “absent from the HTML”.

3. **Surgical fixture sync (no whole-file `cp`):** in `docs/uat-fixtures/AST-756/expected-agent_task.json`, find the `current == 1` / `task_key == "meteorite_email"` object and set `cache_prompt`, `user_prompt`, and `updated_at` to the **exact same strings** as the catalog row. Do **not** add missing fixture rows or rewrite other tasks.

⚠️ **Decision — prompts ship with payload, not as a drive-by later:** Parent AC requires Ruth to expect the new shape; leaving HTML-oriented prompts would fight Stage 1.

4. Verify only the target row’s prompt fields (and optional `updated_at`) moved:

```bash
~/astral/.venv/bin/python - <<'PY'
import json
from pathlib import Path

def load(p):
    return json.loads(Path(p).read_text())

def by_uuid(rows):
    return {r["task_key_uuid"]: r for r in rows}

for label, pre, post in (
    ("catalog", "/tmp/agent_task.pre-ast-1213.json", "data/admin/agent_task.json"),
    ("fixture", "/tmp/expected-agent_task.pre-ast-1213.json", "docs/uat-fixtures/AST-756/expected-agent_task.json"),
):
    a, b = by_uuid(load(pre)), by_uuid(load(post))
    assert set(a) == set(b), label
    changed = [u for u in a if a[u] != b[u]]
    assert len(changed) == 1, (label, changed)
    old, new = a[changed[0]], b[changed[0]]
    assert old["task_key"] == new["task_key"] == "meteorite_email"
    assert "HTML body" not in (new.get("cache_prompt") or "")
    assert "absent from the HTML" not in (new.get("user_prompt") or "")
    assert "--- LINKS ---" in (new.get("cache_prompt") or "") or "visible text" in (new.get("cache_prompt") or "").lower()
    for k in ("task_key_uuid", "agent_id", "task_group_order", "task_group_name", "task_seq", "task_name"):
        assert old[k] == new[k], (label, k)
print("ok")
PY
```

**Ritual:** `code(AST-1213): meteorite_email prompts visible text + links`

## Self-Assessment

**Scope:** `Single-Component` — `gaze_email` Ruth live-content assembly plus the matching Ruth `agent_task` prompt/fixture row; no config key rename, no ingest/archive redesign, no sibling UI/evaluate work.

**Conf:** `high` — call sites are two known string assemblies; payload shape copies roster PJL `visible text + --- NEW LINKS ---` enumeration; gazer already owns body-text and candidate-link extraction used elsewhere on this path.

**Risk:** `Medium` — wrong extraction (dropping real job URLs or leaving markup in live_content) would degrade Ruth parse quality and downstream create counts on both gaze_email shapes; archive/ingest control flow itself is unchanged.

## Code-rules check

- **§1.3 DRY:** Reuse `_meteorite_email_body_text` / `_meteorite_email_candidate_links`; do not fork link filters.
- **§2.1 config:** No new task key; parse modes stay in `METEORITE_EMAIL_PARSE_CONFIG`; link hygiene stays in `METEORITE_EMAIL_INGEST_CONFIG` via gazer helpers.
- **§2.2 / `astral.agent.do-task-delegation`:** Still `do_task` with config `task_key`; only `live_content` body changes.
- **§1.5.1 debug:** Style D detail + `truncate_debug_content` only when `debug=True`.
- **§3.3 imports:** core → core (gazer helpers) already established; no utils→data or layer violations.
- **§1.1 in-scope:** No rename, no evaluate_meteorite, no UI grouping, no Playwright inbox scrape.
- **Engineer test-tree ban:** No `tests/` / bible edits.
