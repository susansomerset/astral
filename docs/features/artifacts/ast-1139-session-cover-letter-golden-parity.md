# AST-1139 — Session cover letter golden parity

**Linear:** https://linear.app/astralcareermatch/issue/AST-1139/session-cover-letter-golden-parity-cover-letter-header-is-incorrect  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1124/cover-letter-header-is-incorrect  
**Publish ref:** `sub/AST-1124/AST-1139-session-cover-letter-golden-parity`

After AST-1137: Admin Session Cover Letter HTML keeps SomersetCover `fromBlock` + the golden stylesheet contract; empty form `from_block` defaults via `resolve_cover_from_block` (candidate-owned text / contact defaults); UI allows Open HTML with empty from-block when a candidate is selected; Style D debug records fromBlock source + document path. Does **not** own job Print Cover Letter emit (AST-1138), candidate from-block storage/UI (AST-1137), or AST-1123 signature-image token semantics.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | On `BUILD_CONFIG["session_cover_letter"]["fields"]["from_block"]`, add `"empty_uses_candidate_resolve": True` (keep `"required": True`). Add `"from_block_sources": ("session", "candidate", "default")` on the `session_cover_letter` block for builder debug source labels. | utils |
| `src/core/builder.py` | In `build_session_cover_letter`: load candidate before from-block required check; when form `from_block` is empty and candidate is present, fill from `resolve_cover_from_block`; track fromBlock source for Style D; call shared SomersetCover emit helper (name after ftr merge — see Stage 2); CSS drift fix only if listed golden declarations differ. Reuse `_candidate_for_cover_from_block` if present after ftr merge; otherwise add it (identical to AST-1138 contract). | core |
| `src/ui/frontend/src/pages/AdminSessionCoverLetter.tsx` | Treat `from_block` as not blocking Open HTML when a candidate is selected; update help copy for empty-from-block defaults. | ui |

**Out of files (siblings / boundaries):** `resolve_cover_from_block` / `COVER_FROM_BLOCK_CONFIG` / Candidate Profile from-block field (AST-1137 — consume only); `build_cover_letter_from_job` / job Print Cover Letter path (AST-1138); AST-1123 token policy; resume HTML / `_emit_html_document` resume header; `tests/`, bible; no new admin HTML route.

## Stage 1: Config — session from-block defaulting contract

**Done when:** `session_cover_letter` declares that empty form `from_block` may resolve from the candidate, and names the allowed builder-level fromBlock source strings. No builder/UI behavior change yet.

1. In `src/utils/config.py`, inside `BUILD_CONFIG["session_cover_letter"]`, change the `from_block` field entry to:
   ```python
   "from_block": {"required": True, "empty_uses_candidate_resolve": True},
   ```
   Keep all other `fields` entries unchanged.
2. On the same `session_cover_letter` block (sibling of `"fields"` / `"document_title"`), add:
   ```python
   "from_block_sources": ("session", "candidate", "default"),
   ```
   - `"session"` = non-empty form `from_block` used as-is  
   - `"candidate"` / `"default"` = values returned by `resolve_cover_from_block` (must match `COVER_FROM_BLOCK_CONFIG["sources"]`)
3. Do **not** change `required` on other session fields. Do **not** add job `job_cover_somerset` here (AST-1138). Do **not** invent a new API route.

⚠️ **Decision:** Keep `required: True` so emitted HTML still expects a from-block after defaulting; `empty_uses_candidate_resolve` is the explicit gate for empty form + candidate (config source of truth — no bare `if key == "from_block"` policy without this flag).

## Stage 2: Builder — empty from-block → resolve + debug + CSS parity

**Done when:** Empty session `from_block` with a valid `candidate_id` emits SomersetCover HTML using `resolve_cover_from_block` text; non-empty form text wins; no candidate + empty from-block still 400s; Style D logs fromBlock source + `document_path=somerset_cover`; listed CSS selectors match the parent golden declarations.

### 2a. Shared emit helper name (ftr-aware)

At build start, after mandatory `git merge origin/ftr/AST-1124-cover-letter-header-is-incorrect`:

1. If `_emit_somerset_cover_html_document` exists (AST-1138 landed on ftr), call that from `build_session_cover_letter` (session path already should). Do **not** reintroduce a second CSS copy.
2. If only `_emit_session_cover_html_document` exists, keep calling that name for this ticket — do **not** rename in AST-1139 (rename is AST-1138). CSS drift edits (2c) apply to whichever helper session currently calls.

### 2b. Empty from-block defaulting in `build_session_cover_letter`

Rewrite the normalize / candidate-load order in `build_session_cover_letter` as follows (literal behavior):

1. Validate `fields` is a dict (existing).
2. Read `cfg = BUILD_CONFIG["session_cover_letter"]`, `field_defs = cfg["fields"]`.
3. Resolve `cid` / load candidate **before** required checks when `candidate_id` is a non-empty stripped string (same `get_candidate` / not-found `ValueError` as today). Build `candidate_root = _coerce_candidate_blob(row)` when loaded; else `{}`.
4. Initialize `from_block_source = None` (str | None).
5. Build `normalized: Dict[str, str]` by iterating `field_defs`:
   - Coerce each value to string (same type error as today for non-str).
   - **Special case `from_block`:**  
     - If `raw.strip()` non-empty → `normalized["from_block"] = raw` (preserve internal newlines; do not strip — match current assignment of `raw` as today for other fields; for from_block use `raw` unchanged like today). Set `from_block_source = cfg["from_block_sources"][0]` (`"session"`).  
     - Else if `field_defs["from_block"].get("empty_uses_candidate_resolve")` and `candidate_root` is non-empty (candidate was loaded):  
       - Shape for resolve: if `_candidate_for_cover_from_block` exists in this module, call it; else add helper (public-helpers section near cover emit):
         ```python
         def _candidate_for_cover_from_block(cd: dict) -> dict:
             """Shape coerced builder candidate blob for ``resolve_cover_from_block``."""
             out: Dict[str, Any] = {
                 "full": cd.get("_full") or "",
                 "first": cd.get("_first") or "",
                 "last": cd.get("_last") or "",
                 "contact": cd.get("contact") or {},
             }
             if "astral_candidate_id" in cd:
                 out["astral_candidate_id"] = cd["astral_candidate_id"]
             if "_astral_candidate_id" in cd:
                 out["_astral_candidate_id"] = cd["_astral_candidate_id"]
             return out
         ```
       - `from_res = candidate_mod.resolve_cover_from_block(_candidate_for_cover_from_block(candidate_root), debug=debug)`
       - `normalized["from_block"] = from_res["text"]`
       - `from_block_source = from_res["source"]` (must be `"candidate"` or `"default"` — already constrained by AST-1137)
       - Do **not** raise required for empty resolve text (composition may be empty if contact/name blank).
     - Else (empty form, no candidate): apply existing required failure — `from_block is required`.
   - For every other key: existing `required` + `normalized[key] = raw` behavior unchanged.
6. Signature image token status / `_emit_*_cover_html_document` call unchanged aside from helper name per 2a.
7. Style D (`debug=True`) on success index `func="builder.build_session_cover_letter"`:
   - Keep existing field/candidate/signature detail lines.
   - Add `|` `from_block_source={from_block_source}` (must be one of `cfg["from_block_sources"]`).
   - Add `|` `from_block_chars={len(normalized["from_block"])}`.
   - Add `|` `document_path=somerset_cover`.
   - No new debug when `debug=False`.

⚠️ **Decision:** Form non-empty text is source `session` and does **not** write through to `contact.cover_letter_from_block` (Admin tool still does not persist). Empty form + candidate uses AST-1137 resolve only.

### 2c. Golden CSS parity (session emit helper)

Against the parent Original brief `<style>` (AST-1124 Description), verify the session SomersetCover helper’s embedded rules for: `body`, `.cover-letter`, `.fromBlock`, `.toBlock`, `.letterdate`, `.lettersubject`, `.lettercontent`, `.lettercontent p`, `.lettercontent p:last-child`, `.letterSignoff`, `.signature-img`, `@page` / `@page :first`, and `@media print` blocks.

1. For each listed selector, every golden declaration must be present with the same value (CSS variables allowed where golden uses `var(--…)`). Theme tokens may come from `BUILD_CONFIG["default_style"]` where the helper already interpolates into `:root` / `background: {page_bg}`.
2. **Known baseline (as of ftr + AST-1137):** listed SomersetCover rules already match the golden; `:root` / `*` extras may remain; body may keep extra `color` / `line-height` / `font-size` only if they do not contradict a golden declaration (golden does not set those — leave as-is unless a listed property drifts).
3. If any listed declaration differs from the golden, edit **only** that helper’s CSS string to restore parity. Do **not** touch resume `_emit_html_document` CSS.
4. Do **not** change DOM structure for AST-1123 token placement.

## Stage 3: Admin Session UI — empty from-block when candidate selected

**Done when:** With a candidate selected, Open HTML is enabled even if From block is blank; without a candidate, From block remains required in the UI; help text states empty from-block uses candidate defaults.

1. In `AdminSessionCoverLetter.tsx`, change `requiredComplete` so that for `from_block`, the field is treated as satisfied when `(fields.from_block ?? "").trim() !== ""` **or** `selectedId` is a non-empty trimmed string. All other `required` fields keep the existing nonempty check.
2. Update the intro `<p>` (help copy) to state clearly: when a candidate is selected, leaving From block empty uses that candidate’s cover from-block text or the contact default (`Name • City, ST` / `email • phone`); when no candidate is selected, From block is required. Keep “does not save to the database.”
3. Do **not** compose defaults in React (no client-side `Name • City` join). Do **not** add a new API. Do **not** change `SESSION_COVER_FIELDS` keys/labels beyond copy if needed — `required: true` on the field descriptor may stay; gating is only in `requiredComplete`.
4. No change to `api_admin.session_cover_letter_html` unless a type/error message must mention the new defaulting (prefer builder `ValueError` strings unchanged).

## Contract check (manual — builder notes only)

- Candidate selected + empty From block + filled date/letter/signoff/signature → Open HTML succeeds; HTML has `<div class="fromBlock">` with `<br>` between default lines when contact resolves to two lines.
- Candidate with custom `contact.cover_letter_from_block` → that text appears; debug `from_block_source=candidate`.
- Candidate without custom from-block → composed defaults; debug `from_block_source=default`.
- Non-empty form From block → that text wins; debug `from_block_source=session`.
- No candidate + empty From block → Open HTML stays disabled; API still 400 if called.
- Embedded `<style>` includes `.fromBlock`, `.toBlock`, `.letterdate`, `.lettersubject`, `.lettercontent`, `.letterSignoff`, `.signature-img` matching golden declarations.
- Job Print Cover Letter / resume HTML not modified by this ticket’s commits.

## Self-Assessment

**Scope:** `Single-Component` — session cover config flag + `build_session_cover_letter` defaulting/debug + Admin Session form gating; no job cover emit rewrite.

**Conf:** `high` — AST-1137 `resolve_cover_from_block` is on ftr; session SomersetCover emitter and Admin form already exist; this ticket wires empty-form defaults and documents CSS parity.

**Risk:** `Medium` — Admin Session Cover Letter is user-visible; wrong required gating could block Open HTML or emit empty headers. Mitigated by keeping no-candidate required path and reusing the shared resolve helper.

## Code Rules check

- §1.1 in-scope-only / no-cross-contamination: session Admin path only; no job cover rewrite; no resume golden reopen; no AST-1123 token work.
- §1.3 DRY: reuse `resolve_cover_from_block` and the single SomersetCover HTML helper (shared with AST-1138 when present on ftr); do not fork CSS.
- §1.4 / §2.1: `empty_uses_candidate_resolve` + `from_block_sources` live in `BUILD_CONFIG["session_cover_letter"]`.
- §1.5.1 debug-contract-gated: Style D only when `debug=True`.
- §3.2 / §3.3: UI does not compose from-block defaults; composition stays in core via AST-1137 helper.
