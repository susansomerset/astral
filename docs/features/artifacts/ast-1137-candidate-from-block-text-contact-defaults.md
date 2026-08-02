# AST-1137 — Candidate from-block text + contact defaults

**Linear:** https://linear.app/astralcareermatch/issue/AST-1137/candidate-from-block-text-contact-defaults-cover-letter-header-is  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1124/cover-letter-header-is-incorrect  
**Publish ref:** `sub/AST-1124/AST-1137-candidate-from-block-text-contact-defaults`

Owns the candidate-controlled cover from-block: config field contract, persist + edit on Candidate Profile beside cover signature fields, and a shared resolve helper that returns custom text or the default `Name • City, ST` / `email • phone` composition when unset. Does **not** change job Print Cover Letter HTML emit or session Admin Cover Letter golden CSS (siblings AST-1138 / AST-1139 consume this contract).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `cover_letter_from_block` to `CANDIDATE_LIBRARY_CONFIG["contact_keys"]`; add `COVER_FROM_BLOCK_CONFIG` (field path, separators, contact segment paths, name source); add Candidate Profile textarea beside Cover Letter Signature; optional `TOKEN_SOURCES` entry only if an existing cover token map already documents sibling keys — **do not** invent a new resolve_tokens surface unless a current consumer requires it (none in this ticket). | utils |
| `src/core/candidate.py` | Add `resolve_cover_from_block(candidate: dict, *, debug: bool = False) -> dict` returning `{"text": str, "source": "candidate"\|"default"}` using `COVER_FROM_BLOCK_CONFIG` + name columns + `contact`. Optional Style D index/detail when `debug=True` (found custom vs recorded default). No builder / HTML emit. | core |
| `src/ui/frontend/src/pages/CandidateProfile.tsx` | No custom panel required — config-driven textarea via existing profile field renderer (same path as `contact.cover_letter_signature`). Touch only if the page hardcodes a field allowlist that would hide the new key; otherwise leave unchanged. | ui |

**Out of files (siblings):** `src/core/builder.py` job/session cover HTML, `AdminSessionCoverLetter.tsx`, job cover CSS golden — AST-1138 / AST-1139.

## Stage 1: Config contract

**Done when:** `COVER_FROM_BLOCK_CONFIG` and library/`UI_CONFIG` profile field declare the from-block key and composition rules; no business logic yet.

1. In `src/utils/config.py`, add `cover_letter_from_block` to `CANDIDATE_LIBRARY_CONFIG["contact_keys"]` (after `cover_letter_signature_image`, before `title_patterns`).
2. In `src/utils/config.py`, add module-level `COVER_FROM_BLOCK_CONFIG` (near `CANDIDATE_LIBRARY_CONFIG` / cover signature config) with exactly these keys:
   - `"contact_key": "cover_letter_from_block"`
   - `"segment_separator": " • "` (bullet with surrounding spaces, matching parent brief)
   - `"line_separator": "\n"`
   - `"name_column": "full"` — primary display name; when empty after strip, builder of the default line uses `recompute_full_name(first, last)` from name columns (same join as library)
   - `"line_1_contact_paths": ("location",)` — after name, join non-empty stripped segments with `segment_separator`
   - `"line_2_contact_paths": ("contact_email", "phone")` — join non-empty stripped segments with `segment_separator`
   - `"sources": ("candidate", "default")` — allowed `source` values returned by resolve (no hardcoded sets in core)
3. In `UI_CONFIG["detail"]["profile"]`, in the existing **"Cover Letter Signature"** group (immediately before or after the `contact.cover_letter_signature` textarea field), add:
   ```python
   {
       "key": "contact.cover_letter_from_block",
       "label": "Cover letter from-block",
       "type": "textarea",
   }
   ```
   Do **not** mark required. Empty / whitespace = unset (defaults apply at resolve time).
4. Do **not** add `cover_letter_from_block` to `TOPIC_MENU_GEN_CONFIG["packet_contact_keys"]` unless that tuple already lists signature keys (it does not today) — keep Estelle packet scope unchanged.
5. Do **not** change `BUILD_CONFIG["session_cover_letter"]` required `from_block` (session form field stays AST-1139).

⚠️ **Decision:** Field key is `contact.cover_letter_from_block` (not bare `from_block`) so it sits beside `cover_letter_signature*` and cannot be confused with session Admin `from_block` payload keys.

## Stage 2: Resolve helper (core)

**Done when:** `resolve_cover_from_block` returns custom text or default two-line composition; empty segments/lines omitted; `source` is always one of `COVER_FROM_BLOCK_CONFIG["sources"]`.

1. In `src/core/candidate.py`, after `recompute_full_name` (public section), add:

   ```python
   def resolve_cover_from_block(candidate: dict, *, debug: bool = False) -> dict:
       """Return cover from-block text + source for emit consumers (AST-1137).

       Returns ``{"text": str, "source": "candidate"|"default"}``.
       Custom wins when ``contact.cover_letter_from_block`` strips non-empty;
       otherwise compose defaults from name + contact per COVER_FROM_BLOCK_CONFIG.
       """
   ```

2. Implementation rules (literal):
   - Import `COVER_FROM_BLOCK_CONFIG` from `src.utils.config` (add to existing config import block).
   - Read `contact = (candidate.get("candidate_data") or {}).get("contact")` — if not a dict, treat as `{}`. Also accept a pre-built token view: if `candidate` already has top-level `"contact"` dict and no `"candidate_data"`, use that contact + top-level `first`/`last`/`full` (same shape as `build_candidate_token_view` output) so AST-1138 can pass either a DB row or a token view without a second adapter.
   - Custom path: `raw = contact.get(COVER_FROM_BLOCK_CONFIG["contact_key"])`; if `isinstance(raw, str)` and `raw.strip()` → return `{"text": raw.strip(), "source": "candidate"}` (strip outer whitespace only; preserve internal newlines).
   - Default path:
     - Name: `full = str(candidate.get("full") or "").strip()`; if empty, `full = recompute_full_name(str(candidate.get("first") or ""), str(candidate.get("last") or ""))`.
     - Build line 1: start with `[full]` if non-empty, then for each path in `line_1_contact_paths` append `str(contact.get(path) or "").strip()` when non-empty; join with `segment_separator`.
     - Build line 2: for each path in `line_2_contact_paths` append stripped non-empty values; join with `segment_separator`.
     - Join non-empty lines with `line_separator`.
     - Return `{"text": composed, "source": "default"}` (composed may be `""` if all contact/name empty).
   - `source` must be taken from / validated against `COVER_FROM_BLOCK_CONFIG["sources"]` (e.g. assign literals that appear in that tuple — do not invent a third source string).
3. When `debug=True`, emit one Style D index header (`func="candidate.resolve_cover_from_block"`, `identifier` = `candidate.get("astral_candidate_id")` or `candidate.get("_astral_candidate_id")` or `""`) with outcome `success — from_block {source}`, then `|` detail lines: `source=…`, `text_chars=N`, and for default path which line segments were non-empty (`line1_segments=…`, `line2_segments=…`). Use existing `logger` / `debug_index` / `debug_detail` patterns already in this module.
4. Do **not** call builder, do **not** write HTML, do **not** mutate `contact`.

⚠️ **Decision:** Resolve lives in `candidate.py` (not `builder.py`) so job/session emit siblings import one contract without pulling cover HTML into the candidate library layer.

## Stage 3: Profile edit path (UI)

**Done when:** Candidate Profile shows the from-block textarea and `PUT /api/candidates/<id>/data` persists `contact.cover_letter_from_block` via existing merge save (no new endpoint).

1. Confirm `CandidateProfile.tsx` renders `UI_CONFIG` profile fields generically (including textareas under `contact.*`). If it does, **no frontend code change** — Stage 1 config is sufficient.
2. If the page has a hardcoded skip-list / custom panel map that would omit unknown keys, extend it only as needed so `contact.cover_letter_from_block` renders as a normal textarea (no custom panel like signature image).
3. API: no new validation in `api_candidate.py` for this field (plain optional string). Do **not** add JPEG-style validation. Existing `save_candidate_data` merge already persists arbitrary contact keys.
4. Manual check (builder notes in Linear comment is enough; no product test tree edits): save a non-empty from-block → GET candidate shows it under `candidate_data.contact.cover_letter_from_block`; clear to empty → resolve returns `source=default` with composed lines from name/email/phone/location.

## Contract for siblings (non-goals for this ticket)

AST-1138 / AST-1139 **must** call `resolve_cover_from_block` (or equivalent import) when filling SomersetCover `fromBlock` / empty session from-block defaults. This ticket only guarantees the field + helper. Print Cover Letter AC 2–3 on the parent are satisfied when those siblings consume `text` / `source`.

## Self-Assessment

**Scope:** `Single-Component` — utils config + one core resolve helper + config-driven profile field; no builder/HTML emit.

**Conf:** `high` — mirrors `cover_letter_signature` profile + library key pattern; composition rules are fully specified in config.

**Risk:** `low` — additive optional contact field; empty default is backward-compatible; job/session render unchanged until siblings wire the helper.

## Code Rules check

- §1.1 in-scope-only: no job/session HTML, no AST-1123 token work.
- §1.4 / `no-hardcoded-sets`: separators and contact paths live in `COVER_FROM_BLOCK_CONFIG`.
- §2.1 config source of truth: field key + UI label in config.
- §3.2 / §3.3: UI stays config-driven; core imports utils only; ui does not grow business composition logic.
- §3.2 ui-config-driven: profile textarea from `UI_CONFIG`, not a React-only field.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1124/AST-1137-candidate-from-block-text-contact-defaults`

| Stage | Summary |
|-------|---------|
| 1 | `COVER_FROM_BLOCK_CONFIG` + `contact.cover_letter_from_block` library/UI field |
| 2 | `resolve_cover_from_block` — custom text or `Name • City, ST` / `email • phone` defaults |
| 3 | Profile: config-driven textarea (no `CandidateProfile.tsx` change) |
