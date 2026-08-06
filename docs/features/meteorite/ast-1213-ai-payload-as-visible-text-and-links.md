# AST-1213 — AI payload as visible text and links

**Linear:** [AST-1213](https://linear.app/astralcareermatch/issue/AST-1213/ai-payload-as-visible-text-and-links-rename-task-to-meteorite-email-ai)
**Parent:** [AST-1182](https://linear.app/astralcareermatch/issue/AST-1182/rename-task-to-meteorite-email-ai-payload-as-visible-textlinks) — Rename task to meteorite_email + AI payload as visible text/links
**Publish ref:** `origin/sub/AST-1182/AST-1213-ai-payload-as-visible-text-and-links`

After the AST-1212 rename, assemble the `meteorite_email` live payload as **visible text plus links** (same content shape as JD-scrape / `select_job_page` page sections — not raw HTML markup), and rewrite Ruth’s `agent_task` prompts so she expects that shape. Parse modes, response schema, task key, and post-parse ingest/archive behavior stay as they are today.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `METEORITE_EMAIL_INGEST_CONFIG["ruth_payload_link_exclude_substrings"]` — AI-visibility noise only (not Playwright’s full exclude list) | utils |
| `src/core/gaze_email.py` | Assemble Ruth `live_content` as visible text + enumerated links (gazer body-text helper + local link walk using the Ruth exclude key); Style D detail when `debug=True` | core |
| `data/admin/agent_task.json` | Rewrite `meteorite_email` `cache_prompt` / `user_prompt` so CONTENT is visible text + links, not raw HTML | data/admin |
| `docs/uat-fixtures/AST-756/expected-agent_task.json` | Surgical sync of that same row’s prompt fields (+ `updated_at` if bumped) — **no** whole-file `cp` | docs |

**No changes expected:** `src/core/agent.py`, `src/core/gazer.py` (reuse `_meteorite_email_body_text` + `_meteorite_fetch_link_visible_text` only — **do not** edit gazer; **do not** call `_meteorite_email_candidate_links` for Ruth), dispatcher, Gmail external, frontend, evaluate_meteorite / UI grouping siblings, `tests/` / bible (Betty after Code Complete). Do **not** Playwright-scrape the inbox; extraction is from the message HTML already fetched via `get_message_html`.

## Stage 1: Config + `gaze_email` — Ruth live payload = visible text + links

**Done when:** `METEORITE_EMAIL_INGEST_CONFIG` exposes a Ruth-only exclude tuple that keeps click-tracking hosts (e.g. `list-manage.com`) visible to Ruth; for both `html_links` and `subject_body` branches in `_handle_bound`, `live_content` starts with the existing `PARSE_MODE:` (and `SUBJECT:` for subject_body) header lines, then visible text plus an optional `--- LINKS ---` enumerated URL list with **no raw HTML tags as the primary content**; a Mailchimp-style `list-manage.com/track/click` href appears in that list while unsubscribe / preferences / w3.org / svg noise does not; `subject_url` / ignore shapes are unchanged. `python3 -m py_compile` succeeds for touched modules (repo venv: `~/astral/.venv/bin/python`).

1. In `src/utils/config.py`, inside `METEORITE_EMAIL_INGEST_CONFIG` (after `link_exclude_substrings` / near the Playwright allow comment), add:

```python
    # AST-1213: href fragments excluded from Ruth's --- LINKS --- payload only.
    # Deliberately narrower than link_exclude_substrings — click-tracking wrappers
    # (e.g. list-manage.com) stay visible; _ingest_link Playwright resolves final_url.
    # Do not reuse this key for Playwright candidate filtering.
    "ruth_payload_link_exclude_substrings": (
        "unsubscribe",
        "mailto:",
        "/preferences",
        "/email-settings",
        "w3.org",
        "/2000/svg",
        "schemas.xmlsoap.org",
        "xmlns=",
    ),
```

Do **not** remove or alter `link_exclude_substrings` (Playwright ingest hygiene stays as today). Do **not** add `list-manage.com` to the Ruth tuple.

⚠️ **Decision — Ruth AI-visibility excludes ≠ Playwright candidate excludes (Joan round=1 option a):** Reusing `_meteorite_email_candidate_links` / `link_exclude_substrings` would strip Mailchimp-style click wrappers from `--- LINKS ---` while leaving the job title in visible text; Ruth’s “do not invent URLs absent from CONTENT” rule then silently drops those postings. Parent AC requires the same class of job-link outcomes. Tracking wrappers stay in Ruth’s list; `_ingest_link` already Playwright-fetches and records `final_url`. Genuine noise (unsubscribe / prefs / namespace/svg markers) stays excluded. Config comment must state the two keys have different consumers so operators do not “narrow Playwright” and accidentally blind Ruth.

2. In `src/core/gaze_email.py`, keep importing `_meteorite_fetch_link_visible_text` from gazer; **also** import `_meteorite_email_body_text`. Do **not** import or call `_meteorite_email_candidate_links`. Import `METEORITE_EMAIL_INGEST_CONFIG` (already imported) and `urlparse` (already imported).

3. Add these private helpers (place with the other module privates above `_ruth_parse`) — **this is the binding final shape** (no superseded `_ruth_live_body(html) -> str` contract):

```python
def _ruth_candidate_links(html: str) -> list[str]:
    """Ordered unique http(s) hrefs for Ruth --- LINKS --- (ruth_payload excludes)."""
    # B1 lazy import: bs4 only on Ruth payload assembly (same pattern as gazer).
    from bs4 import BeautifulSoup

    cfg = METEORITE_EMAIL_INGEST_CONFIG
    schemes = {s.casefold() for s in cfg["link_schemes"]}
    excludes = tuple(s.casefold() for s in cfg["ruth_payload_link_exclude_substrings"])
    allows = tuple(s.casefold() for s in cfg["link_allow_substrings"])
    soup = BeautifulSoup(html or "", "html.parser")
    seen: set[str] = set()
    out: list[str] = []
    for tag in soup.find_all("a", href=True):
        href = (tag.get("href") or "").strip()
        if not href or href in seen:
            continue
        parsed = urlparse(href)
        scheme = (parsed.scheme or "").casefold()
        if scheme not in schemes:
            continue
        low = href.casefold()
        if any(frag in low for frag in excludes):
            continue
        if allows and not any(frag in low for frag in allows):
            continue
        seen.add(href)
        out.append(href)
    return out


def _ruth_live_parts(html: str) -> tuple[str, list[str]]:
    """Return (visible_text, ruth_candidate_links) from email HTML."""
    return _meteorite_email_body_text(html), _ruth_candidate_links(html)


def _format_ruth_live_body(text: str, links: list[str]) -> str:
    """Visible text + optional --- LINKS --- enumeration (JD-scrape payload shape)."""
    parts = [text] if (text or "").strip() else ["(no visible text)"]
    if links:
        parts.append("--- LINKS ---")
        for i, lnk in enumerate(links, 1):
            parts.append(f"{i}. {lnk}")
    return "\n".join(parts)
```

⚠️ **Decision — local `_ruth_candidate_links`, not a gazer edit:** Joan required “do not edit `gazer.py`.” Playwright continue to use `_meteorite_email_candidate_links` + `link_exclude_substrings`. Ruth’s walk is the same algorithm with a different exclude key — intentional dual policy, documented in config.

⚠️ **Decision — section marker `--- LINKS ---` (not `--- NEW LINKS ---`):** Email has no “nav vs new” split; one link list is enough. Keep the triple-dash header style so the shape stays recognizable next to roster PJL live content.

⚠️ **Decision — keep local `_body_text` for emptiness + create-path JD suffix:** `_body_is_empty` and the subject_body `jd_suffix` / no-link create path continue to use existing `_body_text(html)`. This ticket only changes what Ruth sees in `live_content`, not the text appended to scraped JDs or the empty-body gate.

4. In `_handle_bound`, replace the two raw-HTML live assemblies:

- **html_links** (today: `live = f"PARSE_MODE: {html_mode}\n\n{html}"`):

```python
text, links = _ruth_live_parts(html)
body = _format_ruth_live_body(text, links)
live = f"PARSE_MODE: {html_mode}\n\n{body}"
_detail(debug, f"ruth_payload visible_chars={len(text)} links={len(links)}")
for line in truncate_debug_content(live):
    _detail(debug, line)
parsed = await _ruth_parse(...)
```

- **subject_body** (today: `live = f"PARSE_MODE: {subject_mode}\nSUBJECT: {subject}\n\n{html}"`):

```python
text, links = _ruth_live_parts(html)
body = _format_ruth_live_body(text, links)
live = f"PARSE_MODE: {subject_mode}\nSUBJECT: {subject}\n\n{body}"
_detail(debug, f"ruth_payload visible_chars={len(text)} links={len(links)}")
for line in truncate_debug_content(live):
    _detail(debug, line)
parsed = await _ruth_parse(...)
```

Do **not** change shape routing, `_ruth_parse` args other than `live`, ingest loop, archive finalize, or `subject_url`.

⚠️ **Decision — emit truncated live payload under Style D detail:** Parent AC requires found/recorded visibility when this hop’s `debug=True` paths are touched. Summary line = found; `truncate_debug_content(live)` lines = recorded payload (50-line contract). Do **not** add new `logger.info("[DEBUG] …")` lines. `_detail` already no-ops when `debug=False`.

5. Update the module docstring one line to note AST-1213: Ruth live payload is visible text + links (not raw HTML); link list uses `ruth_payload_link_exclude_substrings`.

**Done when (recheck):**

```bash
~/astral/.venv/bin/python - <<'PY'
from src.core import gaze_email as ge
from src.utils.config import METEORITE_EMAIL_INGEST_CONFIG as cfg

assert "list-manage.com" in cfg["link_exclude_substrings"]
assert "list-manage.com" not in cfg["ruth_payload_link_exclude_substrings"]
assert "unsubscribe" in cfg["ruth_payload_link_exclude_substrings"]

html = (
    '<p>New jobs</p>'
    '<a href="https://jobs.example.com/apply/123">Senior Engineer at Acme</a>'
    '<a href="https://example.list-manage.com/track/click?u=1">Staff Engineer at Globex</a>'
    '<a href="https://example.com/unsubscribe">Unsubscribe</a>'
    '<a href="mailto:x@y.z">x</a>'
)
text, links = ge._ruth_live_parts(html)
assert "Staff Engineer at Globex" in text
assert "https://jobs.example.com/apply/123" in links
assert any("list-manage.com" in u for u in links), links  # tracking wrapper kept for Ruth
assert not any("unsubscribe" in u.casefold() for u in links)
body = ge._format_ruth_live_body(text, links)
assert "--- LINKS ---" in body
assert "<a" not in body and "<p>" not in body
assert ge._format_ruth_live_body("", []).startswith("(no visible text)")
print("ok")
PY
~/astral/.venv/bin/python -m py_compile src/utils/config.py src/core/gaze_email.py
```

**Ritual:** `code(AST-1213): Ruth live payload visible text + links`

## Stage 2: Ruth prompts expect visible text + links

**Done when:** Current `meteorite_email` row in `data/admin/agent_task.json` describes CONTENT as visible text plus a `--- LINKS ---` list (not HTML / email HTML as the payload); `user_prompt` no longer says “absent from the HTML”; catalog and fixture `cache_prompt` / `user_prompt` (/`updated_at`) are **byte-equal to each other**; catalog vs fixture drift outside this row is untouched.

1. Snapshot before edit (local `/tmp` only — do not commit):

```bash
cp data/admin/agent_task.json /tmp/agent_task.pre-ast-1213.json
cp docs/uat-fixtures/AST-756/expected-agent_task.json /tmp/expected-agent_task.pre-ast-1213.json
```

2. In `data/admin/agent_task.json`, locate the single `current == 1` object with `task_key == "meteorite_email"`. Rewrite **`cache_prompt`** and **`user_prompt`** only (optionally bump `updated_at` to current UTC `YYYY-MM-DD HH:MM:SS`). Do **not** change `task_key`, `task_name`, `task_key_uuid`, grouping, `task_seq`, `agent_id`, empty prompt slots, or any other row.

**`cache_prompt` binding content** (keep `## INSTRUCTIONS` header style; exact wording may be tightened for clarity but must include every bullet below):

- Still: mechanical meteorite email parse; `PARSE_MODE: html_links` | `subject_body` on the first CONTENT line; echo into response `parse_mode`.
- **Replace** every phrase that treats the body as markup: “HTML body”, “email HTML”, “HTML/body”, “absent from the email HTML”, “links absent from the HTML”.
- State that after the header line(s), CONTENT is **visible text** extracted from the message, optionally followed by a `--- LINKS ---` section of numbered `http(s)` URLs (same shape as JD-scrape visible text + links — not markup). Click-tracking redirect URLs in LINKS are valid job sources (downstream resolves the final URL).
- **html_links:** Use visible text + `--- LINKS ---` to extract every distinct meteorite **job** link worth scraping; skip obvious non-job noise when clearly not a posting; return `{job_link, job_title?, metadata?}` in `jobs` with optional `metadata` object `company` / `location`; prefer empty `jd_link` / `content_text`.
- **subject_body:** CONTENT includes `SUBJECT:` then visible text (+ optional links). Return `content_text` = usable subject + body text; set `jd_link` when one likely JD URL is present; prefer `jobs: []`.
- Always valid JSON only; do **not** invent links absent from CONTENT (visible text or LINKS list); do **not** copy qualify_meteorite’s astral_job_id contract.

**`user_prompt` binding** (one string): ask Ruth to parse CONTENT per `PARSE_MODE` and return JSON with `parse_mode`, `jobs`, optional `jd_link` / `content_text`; do not scrape or invent URLs absent from the CONTENT; do not emit grade vectors. Must **not** say “absent from the HTML” or “email HTML”.

3. **Surgical fixture sync (no whole-file `cp`):** in `docs/uat-fixtures/AST-756/expected-agent_task.json`, find the `current == 1` / `task_key == "meteorite_email"` object and set `cache_prompt`, `user_prompt`, and `updated_at` to the **exact same strings** as the catalog row. Do **not** add missing fixture rows or rewrite other tasks.

⚠️ **Decision — prompts ship with payload, not as a drive-by later:** Parent AC requires Ruth to expect the new shape; leaving HTML-oriented prompts would fight Stage 1.

4. Verify only the target row’s prompt fields (and optional `updated_at`) moved, catalog↔fixture prompts match, and HTML-as-payload wording is gone:

```bash
~/astral/.venv/bin/python - <<'PY'
import json
from pathlib import Path

def load(p):
    return json.loads(Path(p).read_text())

def by_uuid(rows):
    return {r["task_key_uuid"]: r for r in rows}

def by_key(rows, key="meteorite_email"):
    for r in rows:
        if r.get("task_key") == key and r.get("current") == 1:
            return r
    raise AssertionError(key)

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
    cp, up = new.get("cache_prompt") or "", new.get("user_prompt") or ""
    for banned in ("HTML body", "email HTML", "absent from the HTML", "absent from the email HTML"):
        assert banned not in cp, (label, banned, "cache_prompt")
        assert banned not in up, (label, banned, "user_prompt")
    assert "--- LINKS ---" in cp or "visible text" in cp.lower()
    for k in ("task_key_uuid", "agent_id", "task_group_order", "task_group_name", "task_seq", "task_name"):
        assert old[k] == new[k], (label, k)

# Surgical sync: catalog and fixture prompts must be byte-equal
cat = by_key(load("data/admin/agent_task.json"))
fix = by_key(load("docs/uat-fixtures/AST-756/expected-agent_task.json"))
assert cat["cache_prompt"] == fix["cache_prompt"]
assert cat["user_prompt"] == fix["user_prompt"]
assert cat.get("updated_at") == fix.get("updated_at")
print("ok")
PY
```

**Ritual:** `code(AST-1213): meteorite_email prompts visible text + links`

## Self-Assessment

**Scope:** `Single-Component` — Ruth live-content assembly in `gaze_email` + one ingest-config exclude key + matching `meteorite_email` agent_task prompt/fixture row; no rename, no ingest/archive redesign, no sibling UI/evaluate work.

**Conf:** `high` — call sites are two known string assemblies; payload shape copies roster PJL enumeration; Joan round=1 locked the link-visibility decision (option a); helpers and gates are now single-contract.

**Risk:** `Medium` — wrong extraction still degrades Ruth parse → create counts, but the known Mailchimp click-wrapper blind spot is closed by keeping tracking hosts in Ruth’s list while Playwright hygiene stays separate; archive/ingest control flow itself is unchanged.

## Code-rules check

- **§1.3 DRY:** Reuse `_meteorite_email_body_text`; Ruth link walk shares algorithm shape with gazer but must **not** share `link_exclude_substrings` (different consumer — Decision above).
- **§2.1 config:** New Ruth exclude tuple lives in `METEORITE_EMAIL_INGEST_CONFIG`; Playwright key unchanged; parse modes stay in `METEORITE_EMAIL_PARSE_CONFIG`.
- **§2.2 / `astral.agent.do-task-delegation`:** Still `do_task` with config `task_key`; only `live_content` body changes.
- **§1.5.1 debug:** Style D detail + `truncate_debug_content` only when `debug=True`.
- **§3.3 imports:** core → core/utils; no gazer edit; no utils→data or layer violations.
- **§1.1 in-scope:** No rename, no evaluate_meteorite, no UI grouping, no Playwright inbox scrape.
- **Engineer test-tree ban:** No `tests/` / bible edits.

## Revisions

Revision 1 — 2026-08-06
Driven by: Joan `[plan-discuss] round=1 concern` (plan-rubric.v1 REVISE @ `a7959c45`)
Changes:
- **fix-now #1:** Stop reusing `_meteorite_email_candidate_links` / `link_exclude_substrings` for Ruth. Add `ruth_payload_link_exclude_substrings` (option a) so click-tracking wrappers stay in `--- LINKS ---`; implement `_ruth_candidate_links` in `gaze_email`; keep gazer untouched.
- **discuss #2:** Strengthen Stage 2 gate — catalog↔fixture prompt byte-equality; ban leftover “email HTML” / “absent from the email HTML” phrases in both prompts.
- **discuss #3:** Collapse S1 helper contract to final `_ruth_live_parts` + `_format_ruth_live_body` (+ `_ruth_candidate_links`); remove superseded `_ruth_live_body(html) -> str` / exploratory alternate signatures.
- Files Changed / Self-Assessment / code-rules updated for the config + local link-walk delta.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1182/AST-1213-ai-payload-as-visible-text-and-links`
**Plan path:** `docs/features/meteorite/ast-1213-ai-payload-as-visible-text-and-links.md`

**Built tip:** `38a2cecd269ac07390eab9ceb5bf06ade7863e66` (`38a2cecd`) — tip moves after this stub commit.

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `aef00995` | Ruth live payload visible text + links |
| 2 | `38a2cecd` | meteorite_email prompts visible text + links (+ surgical AST-756 fixture) |
