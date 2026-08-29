# AST-1537 — Email header+body HTML for land/qualify

**Linear:** [AST-1537](https://linear.app/astralcareermatch/issue/AST-1537/email-headerbody-html-for-landqualify-manage-email-gives-html-for-the)  
**Parent:** [AST-1533](https://linear.app/astralcareermatch/issue/AST-1533/manage-email-gives-html-for-the-body-of-the-message-not-for-the-header) — Manage Email gives HTML for the body of the message, not for the header, and it must include both.  
**Publish ref:** `sub/AST-1533/AST-1537-email-header-body-html-land-qualify`

Owns the shared header+body HTML assembly and wires every email land path that feeds `stage_meteorite` / qualify so Ruth sees From/To/Subject/(Date) with the body. Does not own Manage Email React chrome or the copy button (sibling AST-1538).

## Scope gate

Ticket **## Scope** (verbatim partition):

- `src/utils/config.py` (extend inbox email HTML wrapper literals for From/To/Subject/(Date)+body)
- `src/core/inbox.py` (shared assemble/strip path for land + message get)
- `src/core/meteorite_email.py` (bound blob uses shared assembly)
- `src/external/gmail.py` (Date on full-message HTML payload when available)
- `src/ui/api/api_inbox.py` (expose assembled header+body HTML on message get)

All Files Changed / Stages stay inside that set.

**Out of scope (siblings / keep):**

- `AdminManageEmail.tsx` / `App.css` — **AST-1538** (render/copy/dark purple).
- Non-email meteorite ingress (paste / scrap / Contact / Slack) — unchanged.
- `consult.py` `_qualify_meteorite_email_subject` — do **not** edit; keep template markup that scraper already matches (see Stage 1 decision).
- New strip tag/attr sets beyond the existing AST-1049 cull lists.

**Depends on:** none (bang! for AST-1538). Parent ftr may be unpublished; `sync-child.sh` already skips missing `origin/ftr/AST-1533`.

**AC partition (this ticket):** Parent AC4 + AC5 only — email land → qualify input includes headers+body; non-email ingress unchanged. Parent AC1–3 / AC6 are AST-1538 (or shared UI).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Extend `INBOX_CREATE_JOB_CONFIG` wrapper to From/To/Subject/(Date)+body; refresh header comment | utils |
| `src/external/gmail.py` | Add `date` on `GmailMessageHtml`; copy Date header on `get_message_html` | external |
| `src/core/inbox.py` | Expand `strip_extract_email_html` headers; land/create call sites; `get_message_with_assembled_html` for admin get | core |
| `src/core/meteorite_email.py` | `_handle_bound` uses shared strip/assemble instead of plain subject prepend | core |
| `src/ui/api/api_inbox.py` | Message GET returns core assembled payload (thin) | ui |

## Stage 1: Config — header+body wrapper literal

**Done when:** `INBOX_CREATE_JOB_CONFIG` owns a single format template with placeholders `{from_address}`, `{to_address}`, `{subject}`, `{date}`, `{body}`; file header comment for that block mentions AST-1537 header fields; `python3 -m py_compile src/utils/config.py` succeeds.

1. In `src/utils/config.py`, update the inventory line for `INBOX_CREATE_JOB_CONFIG` (near the other config block comments) from “subject wrapper (AST-1049)” to note strip/extract + **header+body** wrapper (AST-1049 / AST-1537).

2. In `INBOX_CREATE_JOB_CONFIG`, **replace** the `subject_html_template` value (keep the **key name** `subject_html_template` — Betty’s config tests and bible already key on it; renaming is out of scope / would invent a second key). New value exactly:

```python
    "subject_html_template": (
        '<header class="email-headers">'
        '<p class="email-from"><span class="email-label">From:</span> {from_address}</p>'
        '<p class="email-to"><span class="email-label">To:</span> {to_address}</p>'
        '<div class="email-subject"><h1>{subject}</h1></div>'
        '<p class="email-date"><span class="email-label">Date:</span> {date}</p>'
        '</header>\n'
        '<section class="email-body">{body}</section>'
    ),
```

Update the inline comment above that key from “Format with subject= … and body=” to: Format with HTML-escaped `from_address` / `to_address` / `subject` / `date` and already-stripped `body`.

⚠️ **Decision — keep key name `subject_html_template`:** Parent asked to *extend* the existing wrapper literal, not invent a parallel config key. Renaming would force Betty-side bible/test key churn without product value.

⚠️ **Decision — preserve `class="email-subject"` + inner `<h1>`:** `consult._qualify_meteorite_email_subject` scrapes `class="email-subject"…<h1>…</h1>` (AST-1197). Consult is out of this ticket’s Scope; changing that selector would break title-source Style D. From/To/Date live as sibling elements under `email-headers`.

⚠️ **Decision — always emit the Date row:** Template always includes `{date}`. When Gmail omits Date, core passes `""` and the label still appears with an empty value. Avoids a second template or conditional markup in config.

## Stage 2: Gmail — Date on full-message HTML payload

**Done when:** `GmailMessageHtml` includes `date: str`; `get_message_html` sets it from the raw `Date` header via existing `_header_map` (empty string when missing); list metadata path unchanged; `python3 -m py_compile src/external/gmail.py` succeeds.

1. In `src/external/gmail.py`, extend `GmailMessageHtml` — insert `date: str` immediately after `to_address`:

```python
class GmailMessageHtml(TypedDict):
    id: str
    html_body: str
    subject: str
    from_address: str
    to_address: str
    date: str
```

2. In `get_message_html`, after reading headers with `_header_map`, add `"date": headers.get("date", "")` to the returned dict (same empty-string convention as list `_message_metadata`). Do **not** change `format=` / part extraction / other keys.

3. Update the `get_message_html` docstring to mention Subject/From/To/**Date**.

⚠️ **Decision — external-only Date read:** Full-message `format="full"` already returns all headers; `_header_map` already lowercases names. No new Gmail API knobs. List path already exposes `date` — do not touch list.

## Stage 3: Inbox — shared strip/assemble + land/create callers + get helper

**Done when:** `strip_extract_email_html` escapes and embeds From/To/Subject/Date into the config template; `_land_bound_inbox_message` and `create_meteorite_job_from_inbox_message` pass those fields from the Gmail payload; a public core helper returns the get payload plus `assembled_html` for the admin API; empty-strip guards unchanged; `python3 -m py_compile src/core/inbox.py` succeeds.

1. Change `strip_extract_email_html` signature to:

```python
def strip_extract_email_html(
    subject: str,
    html_body: str,
    *,
    from_address: str = "",
    to_address: str = "",
    date: str = "",
) -> str:
```

Keep the existing BeautifulSoup strip/cull + `normalize_pasted_list_email_html(body)` path unchanged.

2. After cull/normalize, HTML-escape **all four** header fields with `html_module.escape(..., quote=True)` (same as today’s subject). Return:

```python
return INBOX_CREATE_JOB_CONFIG["subject_html_template"].format(
    from_address=escaped_from,
    to_address=escaped_to,
    subject=escaped_subject,
    date=escaped_date,
    body=body,
)
```

Update the function docstring to say header+body wrap per `INBOX_CREATE_JOB_CONFIG`, not subject-only.

3. In `_land_bound_inbox_message`, after `payload = get_message_html(mid)`, replace the subject-only strip call with:

```python
html = strip_extract_email_html(
    payload.get("subject") or "",
    payload.get("html_body") or "",
    from_address=payload.get("from_address") or "",
    to_address=payload.get("to_address") or "",
    date=payload.get("date") or "",
)
```

Leave empty-html error return and `stage_meteorite(..., source_kind="email", ...)` unchanged.

4. In `create_meteorite_job_from_inbox_message`, same header kwargs on the `strip_extract_email_html` call (still rematch From-then-To before strip; still `land_meteorite` after — do not retarget that legacy path to stage).

5. Add a public helper **immediately after** `get_message_html` (public-then-helpers: this is public API for the admin get):

```python
def get_message_with_assembled_html(message_id: str) -> dict:
    """Gmail HTML payload plus assembled_html (header+body strip/wrap)."""
    payload = dict(get_message_html(message_id))
    payload["assembled_html"] = strip_extract_email_html(
        payload.get("subject") or "",
        payload.get("html_body") or "",
        from_address=payload.get("from_address") or "",
        to_address=payload.get("to_address") or "",
        date=payload.get("date") or "",
    )
    return payload
```

`html_body` remains the **raw** Gmail HTML fragment. `assembled_html` is the only field operators/sibling AST-1538 should render/copy.

6. Update the module docstring note for AST-1049 / strip ownership to mention AST-1537 header+body assembly shared by land and message get.

⚠️ **Decision — new `assembled_html` key, keep raw `html_body`:** Replacing `html_body` with assembled markup would double-wrap if any caller stripped again, and would hide the raw fragment. Sibling AST-1538 is told (by parent Scope) to render assembled HTML from the get API — that field is `assembled_html`.

## Stage 4: meteorite_email — bound blob uses shared assembly

**Done when:** `_handle_bound` no longer builds `f"{subject}\n\n{html}"`; it calls `strip_extract_email_html` with the same header kwargs as inbox land; archive / stage / debug behavior otherwise unchanged; `python3 -m py_compile src/core/meteorite_email.py` succeeds.

1. In `src/core/meteorite_email.py`, extend the existing `from src.core.inbox import …` to also import `strip_extract_email_html` (already imports `get_message_html`).

2. Inside `_handle_bound`, after a successful `payload = get_message_html(mid)`, **replace** the “Caller-owned blob (no strip_extract …)” block with:

```python
blob = strip_extract_email_html(
    payload.get("subject") or "",
    payload.get("html_body") or "",
    from_address=payload.get("from_address") or "",
    to_address=payload.get("to_address") or "",
    date=payload.get("date") or "",
)
```

Then `stage_meteorite(cid, blob, source_kind="email", source_id=mid, debug=debug)` as today.

3. If `blob` is empty/whitespace after assemble, keep current stage call behavior (do **not** add a new empty-html early-return unless one already exists — today empty still stages). Do not invent archive-policy changes.

4. Refresh the one-line comment that said inbox owns strip / no strip_extract here: mailbox bound land now uses the **same** inbox-owned strip helper (AST-1537).

⚠️ **Decision — mailbox lands through strip, not plain prepend:** Parent Technical scope requires `meteorite_email` bound blob to use shared header+body assembly. Plain `subject\n\nhtml` was the AST-1531 interim; this ticket retires it so qualify sees the same HTML shape as Manage Email Land / fetch_email.

## Stage 5: api_inbox — expose assembled HTML on message get

**Done when:** `GET /api/admin/inbox/messages/<message_id>` returns the dict from `get_message_with_assembled_html` (includes `assembled_html` + raw fields + `date`); `@require_admin` / 400 / 502 mapping unchanged; `python3 -m py_compile src/ui/api/api_inbox.py` succeeds.

1. In `src/ui/api/api_inbox.py`, change the import from `get_message_html` to `get_message_with_assembled_html` (keep other inbox imports).

2. In `inbox_get_message`, replace `payload = get_message_html(mid)` with `payload = get_message_with_assembled_html(mid)`; still `return jsonify(payload), 200` on success.

⚠️ **Decision — no React edit here:** Modal still reads `html_body` until AST-1538. Bang! means sibling waits on this API field; do not absorb modal/copy/chrome into this plan.

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; publish each to `origin/sub/AST-1533/AST-1537-email-header-body-html-land-qualify`.
- Do not edit `tests/`, `docs/test-bible/**`, React, or consult.
- If `GmailMessageHtml` / strip call sites have drifted from this plan after `sync-child.sh`, stop and comment on **AST-1533** with the stage-blocked template — do not improvise.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1537
**Overall:** APPROVED
**Publish ref:** `sub/AST-1533/AST-1537-email-header-body-html-land-qualify` @ `6a3a4260d9a4a70a015c68b4a7bb6ec026629ce9`

## Traceability
AC4 → Stages 1–5 (config header+body template, gmail `date`, inbox shared strip on land/create/get, `meteorite_email` bound blob, api `assembled_html`); AC5 → Scope gate + email-only paths (paste/scrap/consult/React explicitly untouched).

## Findings

### acceptable
- **Location:** Plan structure — no formal `## Self-assessment` block
- **Finding:** Confidence/unknowns are implicit in stage ⚠️ decisions and estimate confirm, not a labeled self-assessment section.
- **Recommendation:** Optional polish only; stages and decisions are specific enough to build.

### acceptable
- **Location:** Stage 1 — always emit Date row
- **Finding:** Template renders `Date:` even when Gmail omits the header (empty value).
- **Recommendation:** Documented tradeoff; fine for AC4 qualify input; sibling AST-1538 can handle display nuance for AC1.

context_tokens≈42000
