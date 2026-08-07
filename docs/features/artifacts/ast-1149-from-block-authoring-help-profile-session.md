# AST-1149 — From-block authoring help on profile / session

**Linear:** https://linear.app/astralcareermatch/issue/AST-1149/from-block-authoring-help-on-profile-session-allow-contact-info-tokens  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1145/allow-contact-info-tokens-and-or-chars-in-fromblock  
**Publish ref:** `sub/AST-1145/AST-1149-from-block-authoring-help-profile-session`

Owns user-visible authoring help (and config-driven placeholder/label copy) so Susan can see that Cover From supports `{$FULL_NAME}` / `{$LOCATION}` / `{$CONTACT_EMAIL}` / `{$PHONE}`, that `|` authors as `•` in print, and what the default template looks like when unset — on Candidate Profile and Admin Session Cover Letter. Consumes AST-1147 `COVER_FROM_BLOCK_CONFIG` keys (`default_template`, `allowed_token_ids`, separators). Does **not** implement resolve/emit math or SomersetCover CSS (AST-1148 / out of epic). Does **not** invent a new save route (existing candidate data PUT).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `authoring_help` + `session_authoring_help` to `COVER_FROM_BLOCK_CONFIG`. Move `contact.cover_letter_from_block` into its own `DATA_SHAPES` profile section with `placeholder` (= `default_template`) and `help` (= `authoring_help`). | utils |
| `src/ui/api/api_system.py` | Expose a small `cover_from_block` slice on `GET /api/ui_config` from `COVER_FROM_BLOCK_CONFIG` (help + default template) for Session Cover Letter. | ui |
| `src/ui/frontend/src/components/FormFields.tsx` | Extend `Field` with optional `placeholder?: string` and `help?: string` so shapes JSON is typed. | ui |
| `src/ui/frontend/src/components/TabbedTextArea.tsx` | Extend `TextTab` with optional `help?: string`; render muted help text above the textarea when present; pass `placeholder` through (already supported). | ui |
| `src/ui/frontend/src/pages/CandidateProfile.tsx` | When building `textTabs`, pass `placeholder` and `help` from the section’s first field (shapes). Do not hardcode token names in the page. | ui |
| `src/ui/frontend/src/pages/AdminSessionCoverLetter.tsx` | Load `/api/ui_config`, replace the intro help `<p>` with `cover_from_block.session_authoring_help`, and show `cover_from_block.authoring_help` under the From block field. Optional: From textarea `placeholder` = `default_template`. | ui |

**Out of files (siblings / boundaries):**

| File / area | Owner |
|-------------|-------|
| `COVER_FROM_BLOCK_CONFIG` token template / allowlist / rewrite / empty policy keys | AST-1147 (already on ftr; consume only) |
| `resolve_cover_from_block` / builder emit / Style D | AST-1148 |
| SomersetCover CSS/DOM, `{$SIGNATURE_IMAGE}` | out of epic |
| New admin/candidate routes | not in scope — existing `PUT /api/candidates/<id>/data` |
| `tests/`, `docs/test-bible/**` | Betty |

## Stage 1: Config authoring chrome + profile shape visibility

**Done when:** `COVER_FROM_BLOCK_CONFIG` carries profile + session help strings; `DATA_SHAPES` exposes from-block as its own profile tab section with `placeholder`/`help` bound to those strings; `/api/ui_config` returns a `cover_from_block` object Session can read. No resolve/emit code changes.

1. In `src/utils/config.py`, inside `COVER_FROM_BLOCK_CONFIG` (after the AST-1147 keys), add exactly these keys with these values:

   | Key | Value |
   |-----|-------|
   | `"authoring_help"` | `"Allowed tokens: {$FULL_NAME}, {$LOCATION}, {$CONTACT_EMAIL}, {$PHONE}. Type \| between segments; cover print shows •. Leave empty to use the default template (see placeholder)."` |
   | `"session_authoring_help"` | `"Enter cover-letter field values, then Open HTML to Print → PDF. Letter fields come from this form. From block supports {$FULL_NAME}, {$LOCATION}, {$CONTACT_EMAIL}, {$PHONE}; type \| for • in print. When a candidate is selected, leave From empty to use that candidate’s saved from-block or the default token template. Without a candidate, From is required. If a candidate is selected and has a profile signature image, the server may include it in the sign-off; otherwise name-only. This tool does not save to the database."` |

   Update the block comment to mention AST-1149 for authoring chrome (keep AST-1137 / AST-1147 attributions).

2. In `DATA_SHAPES["candidates"]["detail"]["profile"]`, **remove** the `contact.cover_letter_from_block` field from the **"Cover Letter Signature"** group (leave `contact.cover_letter_signature` there alone).

3. Immediately after the **"Cover Letter Signature"** group (before **"Signature Image"**), insert a new section:

   ```python
   {
       "label": "Cover Letter From",
       "fields": [
           {
               "key": "contact.cover_letter_from_block",
               "label": "Cover letter From block",
               "type": "textarea",
               "placeholder": COVER_FROM_BLOCK_CONFIG["default_template"],
               "help": COVER_FROM_BLOCK_CONFIG["authoring_help"],
           },
       ],
   },
   ```

   Do **not** mark required. Empty / whitespace remains “unset → default template” at resolve time (AST-1148).

4. In `src/ui/api/api_system.py`:
   - Import `COVER_FROM_BLOCK_CONFIG` alongside existing config imports.
   - In `ui_config()`, add to the jsonify payload:

     ```python
     "cover_from_block": {
         "default_template": COVER_FROM_BLOCK_CONFIG["default_template"],
         "authoring_help": COVER_FROM_BLOCK_CONFIG["authoring_help"],
         "session_authoring_help": COVER_FROM_BLOCK_CONFIG["session_authoring_help"],
     },
     ```

5. **Do not** change `allowed_token_ids`, `default_template`, `authoring_separator`, `emit_separator`, or `empty_segment_policy` values from AST-1147. **Do not** touch `src/core/candidate.py` or `src/core/builder.py`.

⚠️ **Decision:** Own `DATA_SHAPES` section (“Cover Letter From”) instead of sharing “Cover Letter Signature”. `CandidateProfile` maps each tab section to `sec.fields[0]` only — today from-block is `fields[1]` and never renders. A dedicated one-field section makes the textarea visible without rewriting TabbedTextArea into multi-field panels.

⚠️ **Decision:** Help copy lives in `COVER_FROM_BLOCK_CONFIG` (not hardcoded in TSX). Token names appear in those strings so the UI only renders config text — no React assembly of allowlists (import-direction / ui-config-driven). Slight string overlap with `allowed_token_ids` is intentional for a single user-facing sentence.

⚠️ **Decision:** Profile `placeholder` reuses `COVER_FROM_BLOCK_CONFIG["default_template"]` by reference so the unset default is not duplicated as a second literal.

## Stage 2: Profile tab shows help + placeholder

**Done when:** Candidate Profile “Cover Letter From” tab shows the from-block textarea with placeholder = default template and muted help listing tokens + `|`→`•` + empty→default. Save path unchanged (existing PUT).

1. In `src/ui/frontend/src/components/FormFields.tsx`, extend `Field`:

   ```ts
   placeholder?: string
   help?: string
   ```

2. In `src/ui/frontend/src/components/TabbedTextArea.tsx`:
   - Add optional `help?: string` to `TextTab`.
   - When `tab.help` is a non-empty string, render a muted paragraph (reuse the muted style pattern from `CandidateProfile` signature-image blurb: `color: "#8b949e"`, `marginBottom: 8`, `fontSize: 13`, `lineHeight: 1.5`) **above** `LabeledTextArea` / custom panel.
   - Keep passing `placeholder={tab.placeholder}` into `LabeledTextArea`.

3. In `src/ui/frontend/src/pages/CandidateProfile.tsx`, in the `textTabs` map, after resolving `const f = sec.fields[0]`, set:

   - `placeholder: f.placeholder ?? (isResume && hasBaseResume ? "Locked — base resume has been generated from this text" : undefined)`  
     (prefer shapes `placeholder` when present; keep the resume-lock override when `isResume && hasBaseResume`)
   - `help: typeof f.help === "string" && f.help.trim() ? f.help : undefined`

4. **Do not** add token names, `|`, or `•` as string literals in `CandidateProfile.tsx` / `TabbedTextArea.tsx` beyond rendering `f.help` / `f.placeholder` from shapes.

5. Manual check (builder note only; no product test tree edits): with a candidate selected, open Profile → “Cover Letter From” tab → see placeholder template and help; type `{$FULL_NAME} | {$LOCATION}` → Save → GET candidate shows `candidate_data.contact.cover_letter_from_block` with that authoring text.

## Stage 3: Session Cover Letter help parity

**Done when:** Admin Session Cover Letter intro and From-field help document the same token + `|`→`•` + empty→default authoring rules from config (not hardcoded page copy).

1. In `src/ui/frontend/src/pages/AdminSessionCoverLetter.tsx`:
   - On mount, `api("/api/ui_config")` → JSON; read `cover_from_block` object into state (default empty strings if missing so the page still renders).
   - Replace the static intro `<p>` body with `cover_from_block.session_authoring_help` when non-empty; if empty (config missing), keep the current AST-1139 intro text as fallback only.
   - For the `from_block` field label block, under the label span (or under the textarea), render muted `cover_from_block.authoring_help` when non-empty.
   - Set the From `textarea` `placeholder` to `cover_from_block.default_template` when non-empty.

2. **Do not** change Open HTML gating (`from_block` optional when candidate selected — AST-1139). **Do not** compose defaults in React. **Do not** call resolve helpers from the page.

3. Manual check: Session Cover Letter page shows updated intro + From help/placeholder matching config; Open HTML still works with empty From + candidate selected.

## Contract for siblings (non-goals)

- **AST-1148** still owns expand of allowlisted tokens, `|`→`•`, empty-segment drop, and Style D on emit. This ticket only makes the authoring contract visible.
- **AST-1147** already owns template/allowlist/rewrite keys; do not redefine them.
- Persist path remains AST-1137’s `contact.cover_letter_from_block` via existing candidate data PUT.

## Self-Assessment

**Scope:** `Single-Component` — utils config + shapes + thin ui_config exposure + profile/session help wiring; no resolve/emit.

**Conf:** `high` — AST-1147 keys are on ftr and merged into this publish tip; TabbedTextArea already supports placeholder; visibility fix is a one-field section split that matches Signature Image’s own-section pattern.

**Risk:** `low` — additive help chrome; save/emit paths untouched; wrong help text would confuse authoring but cannot break HTML emit.

## Code Rules check

- §1.1 / `in-scope-only`: help chrome only; no resolve/emit/CSS.
- §1.4 / `no-hardcoded-sets`: token/separator story rendered from config strings; React does not invent allowlists.
- §2.1 / `astral.config.config-source-of-truth`: `authoring_help` / `session_authoring_help` / placeholder live in or reference `COVER_FROM_BLOCK_CONFIG`.
- §3.2 / `astral.layers.ui-config-driven-business-logic` + §3.3 `import-direction`: UI renders config; no from-block expansion in the page.
- §3.5 `frontend-file-placement` / naming: edits stay in existing page/component files under `src/ui/frontend/src/pages|components`.
- `pattern.ui.admin-endpoint`: no new route; reuse `/api/ui_config` + existing candidate data PUT.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1145/AST-1149-from-block-authoring-help-profile-session`
**Tip:** `e61c58b9`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `2c3dc706` | `COVER_FROM_BLOCK_CONFIG` authoring help + own DATA_SHAPES section + `/api/ui_config` slice |
| 2 | `727a1ecb` | Profile TabbedTextArea help/placeholder wiring |
| 3 | `e61c58b9` | Session Cover Letter config-driven intro + From help/placeholder |

## Radia review — findings (rev 1)

**Overall: DISCUSS** — no fix-now. Diff matches the plan almost line-for-line: help/placeholder stay in `COVER_FROM_BLOCK_CONFIG`, no token/`|`/`•` literals invented in TSX, no new routes, no resolve/emit touched.

**What's solid:**
- `COVER_FROM_BLOCK_CONFIG["authoring_help"]` / `["session_authoring_help"]` are the only source of the token/`|`→`•` prose; `CandidateProfile.tsx` / `TabbedTextArea.tsx` render `f.help` / `f.placeholder` without re-deriving it.
- `AdminSessionCoverLetter.tsx` keeps `SESSION_INTRO_FALLBACK` as a fetch-failure-only fallback (matches plan §3.1) — does not compose config in React.
- New "Cover Letter From" `DATA_SHAPES` section fixes the real `sec.fields[0]`-only bug (from-block was `fields[1]`, invisible) exactly per the plan's ⚠️ Decision.

**Discuss:**
1. **Git topology** — `sub/AST-1145/AST-1149-...` merged `origin/sub/AST-1145/AST-1148-...` directly (`2f56ef35`) in addition to `origin/ftr/AST-1145-...` (`38caf363`). Traced the merge parent: it landed only AST-1148's plan-stage commit (`d2d39504`), before AST-1148's own code commits existed, so no AST-1148 production code (`candidate.py` / `builder.py`) crossed into this diff — verified via `git diff origin/dev...<tip> -- src/core/candidate.py src/core/builder.py` (empty). No functional impact; flagging only so future siblings sync via `merge-child` → `ftr` rather than a direct sub-to-sub merge (`orch.git.merge-on-checkout` describes merging `ftr`, not a sibling's sub).
2. **Straggler (C4)** — plan-time Considered-but-excluded lists `astral.standards.debug-contract-gated` and `astral.standards.dry-and-focused-functions` (deferred to AST-1148). Full-set sweep's `applies_when` (ui/utils layer, `src/**`) technically matches this diff too, so both score `conforms` rather than `not-applicable` — no `debug=` surface and no function-complexity growth in the touched lines, so substance-wise there's nothing to fix; noting per rubric C4 belt-and-suspenders, not blocking.

**Pattern conformance:** `pattern.ui.admin-endpoint` — conforms (no new route; reuses `/api/ui_config` + existing candidate data `PUT`).

— Radia

## Resolution

**Date:** 2026-08-03  
**Review tip ingested:** `5aaa5c75` (`docs(AST-1149): Radia review — findings`)  
**Overall:** clean — Radia **DISCUSS** with **no fix-now**; Frame diff none.

| Item | Action |
|------|--------|
| Discuss 1 — sub↔sub merge of AST-1148 plan tip | Accepted; no product change. Confirmed tip still has empty `git diff origin/dev...HEAD -- src/core/candidate.py src/core/builder.py`. Future sibling sync via `merge-child` → `ftr`. |
| Discuss 2 — C4 stragglers (`debug-contract-gated`, `dry-and-focused-functions`) | Accepted; already `conforms` on substance — no `debug=` / no complexity growth. No src change. |

**§9a:** `origin/sub/AST-1145/AST-1149-from-block-authoring-help-profile-session` dry-runs clean into `origin/dev` and `origin/ftr/AST-1145-allow-contact-info-tokens-and-chars-in-fromblock`.
