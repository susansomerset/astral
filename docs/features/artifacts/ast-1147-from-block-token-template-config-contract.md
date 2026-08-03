# AST-1147 — From-block token template + config contract

**Linear:** https://linear.app/astralcareermatch/issue/AST-1147/from-block-token-template-config-contract-allow-contact-info-tokens  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1145/allow-contact-info-tokens-and-or-chars-in-fromblock  
**Publish ref:** `sub/AST-1145/AST-1147-from-block-token-template-config-contract`

Owns the config contract for a tokenized cover from-block default: default authoring template (`{$FULL_NAME} | {$LOCATION}` / `{$CONTACT_EMAIL} | {$PHONE}`), allowlisted token ids, `|`→`•` rewrite literals, and empty-segment drop policy. Extends existing `COVER_FROM_BLOCK_CONFIG`. Does **not** implement resolve/emit (sibling AST-1148). Does **not** own profile/session help chrome (sibling AST-1149). Does **not** register brief aliases (`RESUME_LOCATION` / `RESUME_EMAIL` / `CANDIDATE_MOBLE`).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Extend `COVER_FROM_BLOCK_CONFIG` with default token template, allowlisted token ids, authoring/emit separator rewrite, and empty-segment policy. Keep AST-1137 keys intact for current resolve until AST-1148 migrates. Do not add brief aliases to `TOKEN_SOURCES` or this block. | utils |

**Out of files (siblings / boundaries):**

| File / area | Owner |
|-------------|-------|
| `src/core/candidate.py` (`resolve_cover_from_block`) | AST-1148 |
| `src/core/builder.py` job/session from-block emit + Style D | AST-1148 |
| Profile/session help copy, placeholders, labels beyond this ticket | AST-1149 |
| SomersetCover CSS/DOM, `{$SIGNATURE_IMAGE}` | out of epic |
| `tests/`, `docs/test-bible/**` | Betty |

## Stage 1: Extend `COVER_FROM_BLOCK_CONFIG`

**Done when:** `COVER_FROM_BLOCK_CONFIG` declares the default token template, allowlist, `|`→`•` rewrite, and empty-segment policy as readable keys; AST-1137 keys still present and unchanged in meaning; no resolve/emit code changes; brief aliases absent from config.

1. In `src/utils/config.py`, locate module-level `COVER_FROM_BLOCK_CONFIG` (immediately after `CANDIDATE_LIBRARY_CONFIG`, AST-1137 block). **Keep** every existing key with its current value:
   - `"contact_key": "cover_letter_from_block"`
   - `"segment_separator": " • "`
   - `"line_separator": "\n"`
   - `"name_column": "full"`
   - `"line_1_contact_paths": ("location",)`
   - `"line_2_contact_paths": ("contact_email", "phone")`
   - `"sources": ("candidate", "default")`

2. Add these new keys to the **same** dict (AST-1147). Use exactly these names and values:

   | Key | Value | Meaning for AST-1148 consumers |
   |-----|-------|--------------------------------|
   | `"default_template"` | `"{$FULL_NAME} | {$LOCATION}\n{$CONTACT_EMAIL} | {$PHONE}"` | Authoring-form default when saved from-block is empty/whitespace. Two lines joined by `line_separator` (`\n`). Tokens use `{$TOKEN}` form. Authoring separator between segments is bare `\|` (spaces around `\|` as shown). |
   | `"allowed_token_ids"` | `("FULL_NAME", "LOCATION", "CONTACT_EMAIL", "PHONE")` | Only these registry names are expanded on the from-block surface. Order is documentation order matching the default template lines — not a sort requirement for resolve. |
   | `"authoring_separator"` | `"\|"` | Character candidates type as a segment separator in from-block text. |
   | `"emit_separator"` | `" • "` | What `|` becomes at emit (spaces match AST-1137 golden / existing `segment_separator`). |
   | `"empty_segment_policy"` | `"drop_with_adjacent_separator"` | When a token resolves empty (or a free-text segment is empty after strip), omit that segment **and** its adjacent authoring/emit separator so printed output never shows dangling `•`, bare `|`, or unresolved placeholders for allowlisted empties. |

3. Update the block’s leading comment from `# AST-1137: …` to mention both tickets, e.g.  
   `# AST-1137 / AST-1147: candidate from-block field + token default template / rewrite policy.`  
   Do not delete the AST-1137 attribution.

4. **Do not** add `RESUME_LOCATION`, `RESUME_EMAIL`, `CANDIDATE_MOBLE`, or `CANDIDATE_MOBILE` to:
   - `COVER_FROM_BLOCK_CONFIG["allowed_token_ids"]`
   - `TOKEN_SOURCES`
   - any new alias map inside this block

5. **Do not** change:
   - `CANDIDATE_LIBRARY_CONFIG` / `UI_CONFIG` profile field for `contact.cover_letter_from_block` (AST-1149 owns authoring help chrome)
   - `TOKEN_SOURCES` entries for `FULL_NAME` / `LOCATION` / `CONTACT_EMAIL` / `PHONE` (already correct paths)
   - `TOPIC_MENU_GEN_CONFIG["packet_contact_keys"]`
   - `BUILD_CONFIG["session_cover_letter"]`
   - `src/core/candidate.py`, `src/core/builder.py`, or any UI/TSX file

6. **Do not** implement resolve that reads `default_template` / `allowed_token_ids` / rewrite keys — that is AST-1148. This stage is declarative config only.

⚠️ **Decision:** Keep AST-1137 `line_*_contact_paths` / `segment_separator` keys alongside the new token-template keys. Current `resolve_cover_from_block` stays green until AST-1148 switches the default path to `default_template` + allowlist + rewrite. Removing path keys here would break emit mid-epic.

⚠️ **Decision:** `emit_separator` is `" • "` (spaced bullet), not bare `"•"`, so rewrite matches the AST-1137 golden and existing `segment_separator`. Sibling resolve must substitute `|` → `emit_separator` (not invent a third literal).

⚠️ **Decision:** `empty_segment_policy` is a single string enum value (`"drop_with_adjacent_separator"`), not a nested dict — AST-1148 implements the only allowed policy; if a second policy is ever needed, extend the string set in config then.

⚠️ **Decision:** No profile `placeholder` / `help` field metadata in this ticket. Ticket boundaries hand help chrome to AST-1149; config keys above are enough for emit to satisfy parent AC1’s config half.

## Contract for siblings (non-goals)

- **AST-1148** must consume `default_template`, `allowed_token_ids`, `authoring_separator`, `emit_separator`, and `empty_segment_policy` inside the shared from-block expand path (candidate custom, default template, session-typed From). Unrecognized `{$…}` tokens stay as-is (forward-compat). Style D debug lives there.
- **AST-1149** owns user-visible help that the default template / `|`→`•` story is discoverable on profile/session.
- This ticket only guarantees the keys exist with the values above.

## Self-Assessment

**Scope:** `minor` — one utils config block extension; no core/UI behavior change.

**Conf:** `high` — parent Open questions already map tokens and rewrite; AST-1137 block is the clear extension point; allowlist matches existing `TOKEN_SOURCES` names.

**Risk:** `low` — additive keys; existing resolve ignores unknown keys; no alias registration; siblings own consumption.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1145/AST-1147-from-block-token-template-config-contract`
**Tip:** `bcc95f9a`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `bcc95f9a` | Extend `COVER_FROM_BLOCK_CONFIG` with `default_template`, `allowed_token_ids`, `authoring_separator`, `emit_separator`, `empty_segment_policy`; keep AST-1137 keys |

## Code Rules check

- §1.1 / `in-scope-only`: config only; no resolve/emit/help chrome.
- §1.4 / `no-hardcoded-sets`: token ids, separators, template, and empty policy live in `COVER_FROM_BLOCK_CONFIG` for AST-1148 to read — not inline in core/UI.
- §2.1 / `astral.config.config-source-of-truth` / `pattern.config.config-block`: extend the named block; do not invent a second from-block config dict.
- §3.3 import direction: no new imports; utils-only edit.
- No cross-contamination into resume header emit or signature-image token contract.
