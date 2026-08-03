# AST-1162 — Fix signature image / name vertical spacing

**Linear:** https://linear.app/astralcareermatch/issue/AST-1162/fix-signature-image-name-vertical-spacing-signature-image-now-overlaps  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1161/signature-image-now-overlaps-name-text-in-signature  
**Publish ref:** `sub/AST-1161/AST-1162-fix-signature-image-name-vertical-spacing`

SomersetCover signoff that places a handwritten signature image above typed name text (via `{$SIGNATURE_IMAGE}`) currently overlaps / bottom-aligns because the shared golden `.signature-img` rule uses a negative bottom margin. This ticket corrects that one CSS declaration (and only related signoff spacing if still required after the margin fix) so session and job SomersetCover surfaces that share `_emit_somerset_cover_html_document` both stack image above name with a clear gap. Does **not** own token resolve, profile image storage, from-block work, or resume HTML emit.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/builder.py` | In `_emit_somerset_cover_html_document` embedded CSS, supersede `.signature-img` vertical margin so the image no longer overlaps following name text; leave markup / token replace / other selectors unchanged unless Stage 1 verification shows `.letterSignoff` alone still collapses the gap. | core |

**Out of files (boundaries):** `resolve_tokens` / `COVER_LETTER_RENDER_TOKENS` / `{$SIGNATURE_IMAGE}` contract (AST-1125 / AST-1126); candidate profile upload; from-block resolve (AST-1137+); resume `_emit_html_document`; React Admin / Profile UI; `tests/`, bible (Betty).

## Stage 1: Correct `.signature-img` vertical margin

**Done when:** Embedded SomersetCover CSS in `_emit_somerset_cover_html_document` no longer uses a negative bottom margin on `.signature-img`; closing + image + name signoff HTML keeps document order with a visible gap between image and following name glyphs; signoff without an image still emits closing + name text with no empty `<img>` / no new empty image box from this change.

1. In `src/core/builder.py`, locate the embedded `.signature-img` rule inside `_emit_somerset_cover_html_document` (today approximately):
   ```css
   .signature-img {
     display: block;
     height: 61px;
     margin: 8px 0 -25px 0;
   }
   ```
2. Replace the `margin` declaration with a non-negative bottom margin that preserves block stacking:
   ```css
   .signature-img {
     display: block;
     height: 61px;
     margin: 8px 0 8px 0;
   }
   ```
   Keep `display: block` and `height: 61px` unchanged.
3. Do **not** change `_html_with_signature_image_token`, img markup (`class="signature-img"` / `alt="Signature"`), token present/absent omit policies, `signoff_parts` assembly, `.letterSignoff` rules, from/to/body CSS, or any resume stylesheet in `_emit_html_document`.
4. Do **not** add a second copy of SomersetCover CSS — session `build_session_cover_letter` and job `build_cover_letter_from_job` already share this helper; one edit ships both surfaces.
5. After the margin change, visually confirm (browser open of emitted HTML or print preview) that for signature content shaped like `Best,\n{$SIGNATURE_IMAGE}\nSusan Somerset` the image sits fully above the name with no overlap. If and only if name text still overlaps the image after step 2 (e.g. unexpected inline layout), adjust **only** `.letterSignoff` / `.signature-img` spacing declarations in this same helper — still no markup/token changes — and stop to comment on the parent if a non-CSS fix appears necessary.

⚠️ **Decision:** Root cause is the AST-1024 golden `margin-bottom: -25px`, which pulls following name text up into the 61px image under token-below-name signoff. Replacing it with `8px` bottom margin (matching the existing top margin) removes overlap without inventing a new layout system. Exact pixel gap after remove-overlap is Archie UAT (parent AC); do not tune beyond this single positive gap unless step 5 proves insufficient.

⚠️ **Decision:** Supersede the prior golden `.signature-img` vertical margin from AST-1124 / AST-1024 for this bug only — do not reopen those tickets' token, from-block, or DOM scope.

## Execution contract

- Execute Stage 1 steps in order; one commit on the epic worktree for this stage, then `git push origin HEAD:sub/AST-1161/AST-1162-fix-signature-image-name-vertical-spacing`.
- Do not add files, modules, configs, or dependencies not listed above.
- Do not edit `tests/` or `docs/test-bible/**` (Betty).
- If the codebase has drifted (helper renamed, CSS moved out of `builder.py`) — stop, comment on the **parent** Linear issue with the stage-blocked format, and wait.

## Self-Assessment

**Scope:** `Single-Component` — one embedded CSS rule in `src/core/builder.py` SomersetCover helper; session + job cover surfaces inherit via shared emit.

**Conf:** `high` — overlap is explained by the literal negative bottom margin already in tree; fix is a one-declaration supersede of known golden CSS.

**Risk:** `low` — change is scoped to `.signature-img` spacing; token omit and no-image paths do not emit the img, so they are unaffected; wrong margin would only regress signoff image/name gap (Archie-visible), not pipeline state.

## Rules check (ASTRAL_CODE_RULES)

- §1.1 / `astral.standards.in-scope-only`: only `.signature-img` (and related signoff spacing if step 5 requires) — no token/profile/from-block/resume paths.
- §1.1 / `astral.standards.no-cross-contamination`: do not pull resume stylesheet or unrelated emit helpers.
- §1.3 DRY: one shared helper already; do not duplicate CSS.
- §2.1 config: N/A — spacing is stylesheet, not a behavior-driving config set.
- §2.4 / §2.6 batch/state: N/A.
- §3.3 imports / §3.5 naming: no new symbols.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1161/AST-1162-fix-signature-image-name-vertical-spacing`
**Tip:** `ab131524`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `ab131524` | `.signature-img` margin `8px 0 -25px 0` → `8px 0 8px 0` in shared SomersetCover CSS |
