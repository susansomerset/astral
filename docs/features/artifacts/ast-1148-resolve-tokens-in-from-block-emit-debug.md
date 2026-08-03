# AST-1148 — Resolve tokens in from-block + emit debug

**Linear:** https://linear.app/astralcareermatch/issue/AST-1148/resolve-tokens-in-from-block-emit-debug-allow-contact-info-tokens-and  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1145/allow-contact-info-tokens-and-or-chars-in-fromblock  
**Publish ref:** `sub/AST-1145/AST-1148-resolve-tokens-in-from-block-emit-debug`

Owns expanding allowlisted contact tokens, `|`→`•`, and empty-segment drop inside the shared from-block path used by job Print Cover Letter emit, session empty→candidate resolve, **and** non-empty session-typed From. Consumes AST-1147 `COVER_FROM_BLOCK_CONFIG` keys (`default_template`, `allowed_token_ids`, `authoring_separator`, `emit_separator`, `empty_segment_policy`). Style D debug on the touched `debug=` expand/resolve path. Does **not** change SomersetCover CSS/DOM, signature-image tokens, profile/session help chrome (AST-1149), or register brief aliases.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/candidate.py` | Add shared `expand_cover_from_block_text`; rewrite `resolve_cover_from_block` to select authoring text (saved custom or `default_template`) then expand via that helper; Style D token/source/rewrite details when `debug=True`. Stop using AST-1137 `line_*_contact_paths` composition for the default path (keys remain in config; do not delete). | core |
| `src/core/builder.py` | In `build_session_cover_letter`, when form `from_block` is non-empty (`source=session`), run the same expand helper before emit (pass candidate blob when loaded, else empty contact shape). Job path already consumes `resolve_cover_from_block` text — no second expand. Keep existing Style D `from_block_source` / `from_block_chars` lines. | core |

**Out of files (siblings / boundaries):**

| File / area | Owner |
|-------------|-------|
| `COVER_FROM_BLOCK_CONFIG` key declarations | AST-1147 (already on ftr) |
| Profile/session help copy, placeholders, labels | AST-1149 |
| SomersetCover CSS/DOM, `{$SIGNATURE_IMAGE}` | out of epic |
| Brief aliases `RESUME_LOCATION` / `RESUME_EMAIL` / `CANDIDATE_MOBLE` | never |
| `tests/`, `docs/test-bible/**` | Betty |

## Stage 1: Shared expand helper + resolve migration

**Done when:** `expand_cover_from_block_text` expands allowlisted tokens, rewrites `|`→`emit_separator`, drops empty segments per config policy; `resolve_cover_from_block` returns expanded text for both custom and default paths using `default_template` (no more path-based default composition); Style D details fire only when `debug=True`.

1. In `src/core/candidate.py`, add imports to the existing config import block:
   - `TOKEN_SOURCES` from `src.utils.config`
   - Keep `COVER_FROM_BLOCK_CONFIG` (already imported)
   - Import `value_to_str` from `src.utils.formatting` (same helper `resolve_tokens` uses)

2. Add a module-level token regex matching config’s pattern (do **not** import private `_TOKEN_RE`):
   ```python
   _FROM_BLOCK_TOKEN_RE = re.compile(r"\{\$([A-Z_]+)\}")
   ```

3. After `recompute_full_name` (public section), add public:

   ```python
   def expand_cover_from_block_text(
       text: str,
       candidate: dict,
       *,
       source: str,
       debug: bool = False,
   ) -> str:
       """Expand from-block authoring text for emit (AST-1148).

       Allowlisted ``{$TOKEN}`` → candidate values; ``|`` → emit separator;
       empty segments dropped per COVER_FROM_BLOCK_CONFIG. Unrecognized
       ``{$…}`` left as-is. ``source`` is a debug label only (candidate/default/session).
       """
   ```

4. Implementation of `expand_cover_from_block_text` (literal behavior):

   a. `logger.set_debug_flag(debug)`.

   b. Read config (no hardcoded literals for separators/policy/allowlist/template):
      - `auth_sep = COVER_FROM_BLOCK_CONFIG["authoring_separator"]`  # `"|"`
      - `emit_sep = COVER_FROM_BLOCK_CONFIG["emit_separator"]`  # `" • "`
      - `line_sep = COVER_FROM_BLOCK_CONFIG["line_separator"]`  # `"\n"`
      - `policy = COVER_FROM_BLOCK_CONFIG["empty_segment_policy"]`
      - `allowed = COVER_FROM_BLOCK_CONFIG["allowed_token_ids"]`
      - If `policy != "drop_with_adjacent_separator"`: raise `ValueError` naming the unexpected policy (only this policy is implemented).

   c. Build a walkable token view from `candidate` (same dual-shape acceptance as today’s `resolve_cover_from_block`):
      - If `candidate` has dict `candidate_data`: start from `build_candidate_token_view(candidate)`.
      - Else treat as token-view / builder shape:  
        `view = {"first": …, "last": …, "full": …, "contact": top-level contact dict or {}, "_astral_candidate_id": …}`.
      - If `str(view.get("full") or "").strip()` is empty, set `view["full"] = recompute_full_name(first, last)` so `{$FULL_NAME}` matches AST-1137 name fallback.

   d. Define inner `_lookup_allowed(name: str) -> Optional[str]`:
      - If `name` not in `allowed`: return `None` (caller leaves `{$name}` as-is).
      - `spec = TOKEN_SOURCES.get(name)`; if missing or `spec.get("source") != "candidate"`: return `None` (leave as-is — do not invent values; brief aliases are absent from allowlist and TOKEN_SOURCES).
      - Walk `spec["path"]` on `view` with a tiny local dotted-path walker (do **not** call `resolve_tokens` — that would expand non-allowlisted registry tokens like `{$GITHUB}`).
      - Return `value_to_str(raw).strip()` when raw is present/non-empty; return `""` when empty/missing.

   e. Define inner `_expand_segment(segment: str) -> tuple[str, dict]` that replaces tokens via `_FROM_BLOCK_TOKEN_RE`:
      - For each match: if `_lookup_allowed(name) is None` → keep literal `match.group(0)` and count `left_as_is`; else substitute the looked-up string (may be `""`) and count `resolved` or `empty`.
      - Return `(expanded_segment, counts)`.

   f. Normalize newlines: `raw = (text or "").replace("\r\n", "\n")`.

   g. Per-line empty-segment drop (policy `drop_with_adjacent_separator`):
      - Split `raw` on `line_sep`.
      - For each line: split on `auth_sep` (`"|"`) into segments; for each segment run `_expand_segment`, then `.strip()`; **keep** only segments whose stripped expanded text is non-empty; join keepers with `emit_sep`.
      - Drop lines that become empty after join.
      - Join surviving lines with `line_sep`.
      - Result is the returned emit text (may be `""`).

   h. Do **not** mutate `candidate` / contact. Do **not** persist. Do **not** touch HTML.

   i. When `debug=True`, emit Style D:
      - One `debug_index`: `func="candidate.expand_cover_from_block_text"`, `index=1`, `total=1`, `identifier` = `view.get("_astral_candidate_id")` or `candidate.get("astral_candidate_id")` or `""`, `outcome=f"success — from_block {source}"`.
      - `debug_detail` lines (prefix contract via existing helper):
        - `source={source}`
        - `tokens_found={total {$TOKEN} matches in authoring text}`
        - `tokens_resolved={allowlisted non-empty substitutions}`
        - `tokens_empty={allowlisted empty substitutions}`
        - `tokens_left_as_is={non-allowlisted / unknown left as placeholders}`
        - `separator_rewrite={"yes" if auth_sep in raw else "no"}`
        - `text_chars={len(result)}`
      - No debug-contract lines when `debug=False`.

⚠️ **Decision:** Expand lives in `candidate.py` (not `builder.py`) so job resolve, session empty→resolve, and session-typed From share one path without pulling HTML into the library layer — same placement as AST-1137 resolve.

⚠️ **Decision:** Do **not** call `resolve_tokens()` for from-block text. Parent allowlist is a surface subset of `TOKEN_SOURCES`; `resolve_tokens` would expand every registry token (e.g. `{$GITHUB}`) and warn on empties. Walk `TOKEN_SOURCES` paths only for ids in `allowed_token_ids`.

⚠️ **Decision:** Segment-first algorithm (split lines → split on `authoring_separator` → expand tokens per segment → drop empty → join with `emit_separator`) implements `drop_with_adjacent_separator` literally. Do not regex-scrub dangling bullets after a blind global replace.

5. Rewrite `resolve_cover_from_block` body:

   a. Keep signature `resolve_cover_from_block(candidate: dict, *, debug: bool = False) -> dict` and return shape `{"text": str, "source": "candidate"|"default"}`.

   b. `logger.set_debug_flag(debug)`.

   c. Resolve contact + custom raw exactly as today (DB row `candidate_data.contact` **or** top-level `contact`; `contact_key` from config; custom wins when `isinstance(raw, str) and raw.strip()`).

   d. If custom: `authoring = raw.strip()` (outer strip only; preserve internal newlines), `source = COVER_FROM_BLOCK_CONFIG["sources"]` candidate entry (index 0 / `"candidate"`).

   e. Else: `authoring = COVER_FROM_BLOCK_CONFIG["default_template"]`, `source =` default entry (`"default"`). **Delete** the AST-1137 path-based `line_1_contact_paths` / `line_2_contact_paths` / `segment_separator` composition block — default emit now comes from expanding the template.

   f. `text = expand_cover_from_block_text(authoring, candidate, source=source, debug=debug)`.

   g. Return `{"text": text, "source": source}`.

   h. Style D on resolve: when `debug=True`, keep one index on `func="candidate.resolve_cover_from_block"` with outcome `success — from_block {source}` plus details `source={source}` and `text_chars={len(text)}` (expand emits the token/rewrite details under its own index). No debug when `debug=False`.

⚠️ **Decision:** Leave AST-1137 `line_*_contact_paths` / `segment_separator` / `name_column` keys in `COVER_FROM_BLOCK_CONFIG` untouched (AST-1147 contract). Resolve stops reading them; do not delete keys in this ticket.

## Stage 2: Session-typed From uses the same expand

**Done when:** Non-empty Admin Session Cover Letter `from_block` is expanded with the same token / `|`→`•` / empty-segment rules before SomersetCover emit; empty→`resolve_cover_from_block` path already expands via Stage 1; job Print Cover Letter unchanged beyond consuming expanded resolve text.

1. In `src/core/builder.py`, inside `build_session_cover_letter`, locate the `from_block` special case (non-empty form → `source=session`).

2. When `raw.strip()` is non-empty:
   - Set `from_block_source = cfg["from_block_sources"][0]` (`"session"`) as today.
   - Shape candidate for expand:
     - If `candidate_root` is non-empty: `shaped = _candidate_for_cover_from_block(candidate_root)`.
     - Else: `shaped = {"full": "", "first": "", "last": "", "contact": {}}` (tokens resolve empty and drop; free text / unrecognized placeholders still emit).
   - `normalized["from_block"] = candidate_mod.expand_cover_from_block_text(raw, shaped, source=from_block_source, debug=debug)`.
   - Do **not** strip `raw` before expand (preserve internal newlines; expand normalizes `\r\n` itself). Pass `raw` as authored (same string previously assigned to `normalized[key]`).

3. Empty form + `empty_uses_candidate_resolve` + candidate: keep calling `resolve_cover_from_block` (Stage 1 already expands). Do **not** double-expand the returned text.

4. Job `build_cover_letter_from_job`: keep single call to `resolve_cover_from_block(...); fields from from_res["text"]`. Do **not** call expand again on that text.

5. Do **not** change `_emit_somerset_cover_html_document`, SomersetCover CSS, signature-image token handling, resume builders, or profile persistence APIs.

6. Existing builder Style D success details (`from_block_source=…`, `from_block_chars=…`, `document_path=somerset_cover`) stay. Expand’s own Style D index/details cover token outcomes when `debug=True`.

⚠️ **Decision:** Session-typed From does not write through to `contact.cover_letter_from_block` (AST-1139 contract unchanged). Expand is emit-only.

## Contract for siblings (non-goals)

- **AST-1147** already declared config keys — this ticket only consumes them.
- **AST-1149** owns authoring help chrome so Susan can discover tokens / `|`→`•` / default template.
- Persistence of authoring text (tokens + `|`) on Candidate Profile remains the existing PUT path; this ticket only changes emit-time expansion.
- Betty owns test/bible updates for golden strings that previously assumed raw custom text or path-composed defaults.

## Self-Assessment

**Scope:** `Single-Component` — core candidate expand/resolve + one builder session call-site; no config key invention, no UI/CSS.

**Conf:** `high` — AST-1147 keys are on ftr; dual-shape contact handling and Style D patterns already exist in `resolve_cover_from_block` / session builder; allowlist-gated walk of `TOKEN_SOURCES` is a narrow, known pattern.

**Risk:** `Medium` — cover emit is user-visible; a wrong empty-segment or allowlist rule would print dangling `•` / unresolved tokens / expand non-allowlisted registry tokens. Mitigated by config-driven policy and shared helper for all three sources.

## Code Rules check

- §1.1 / `in-scope-only`: no CSS, signature-image, help chrome, alias registration, resume header.
- §1.3 / `dry-and-focused-functions` + `public-then-helpers`: one public expand; resolve + session call it; local lookup/segment helpers below public section.
- §1.4 / `no-hardcoded-sets`: separators, allowlist, template, policy from `COVER_FROM_BLOCK_CONFIG`; token paths from `TOKEN_SOURCES`.
- §1.5.1 / `debug-contract-gated`: Style D index + ` | ` details only when `debug=True`.
- §2.1 / config source of truth: no new config block; consume AST-1147 keys.
- §3.3 import direction: core → utils only; UI unchanged.
- No cross-contamination into consult/rubric `|` parsers or resume HTML.
