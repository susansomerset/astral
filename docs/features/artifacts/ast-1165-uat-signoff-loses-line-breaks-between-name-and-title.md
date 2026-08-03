# AST-1165 — UAT: signoff loses line breaks between name and title

**Linear:** https://linear.app/astralcareermatch/issue/AST-1165/uat-signoff-loses-line-breaks-between-name-and-title  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1161/signature-image-now-overlaps-name-text-in-signature  
**Publish ref:** `sub/AST-1161/AST-1165-uat-signoff-loses-line-breaks-between-name-and-title`

After AST-1162's image/name overlap fix, SomersetCover signoff still collapses authored newlines in signature text (e.g. name then title) because `_html_with_signature_image_token` HTML-escapes segments around `{$SIGNATURE_IMAGE}` without turning `\n` into `<br>`. This ticket restores visible line breaks for non-image signoff text segments on the shared SomersetCover emit path (session + job), without regressing AST-1162 margin stacking or AST-1126 token omit.

## UAT fitness

- **AC restored:** "Closing lines and other signoff text that are not the image remain readable and in the same relative order as the authored signature content." Also keep: "With signature content shaped like closing + image token + name, rendered cover HTML shows the image above the name with no overlap and no shared bottom alignment of image and name glyphs."
- **Correct outcome:** Best, then signature image, then name on its own line, then title on its own line (matching authored newlines), with no image/name overlap regression.
- **Sibling check:** AST-1162 — `.signature-img` stays `margin: 8px 0 8px 0` (no return to `-25px`); AST-1126 — token-at-position emit still omits image when token/image absent. Verify by leaving CSS margin and omit branches untouched; emit HTML still has corrected margin string and no `<img>` when token absent.
- **Not sufficient:** Removing the stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** `white-space: pre` (or `pre-wrap`) on all of `.letterSignoff` that fights other layout; inventing separate name/title fields; swallowing the bug by only changing CSS margin again; changing the `SIGNATURE_IMAGE` token contract. Correct fix matches letter-body newline→`<br>` after escape.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/builder.py` | In `_html_with_signature_image_token`, after `html.escape` on signature text segments (token-present join path **and** token-absent full-text path), convert authored newlines to `<br>` the same way letter body does (`replace(chr(10), '<br>')`, after normalizing `\r\n` → `\n` on the raw segment if needed). Do not change img markup, token omit, or `.signature-img` CSS. | core |

**Out of files (boundaries):** `COVER_LETTER_RENDER_TOKENS` / omit policies; profile upload; from-block / letter body paragraph splitting; resume `_emit_cover_signoff_html` / `_emit_html_document` (non-SomersetCover family — leave alone per parent Boundaries); React UI; `tests/`, bible (Betty).

## Stage 1: Newline → `<br>` in SomersetCover signature fragment

**Done when:** Signature content with authored newlines around / after `{$SIGNATURE_IMAGE}` (e.g. image then name line then title line) emits those newlines as `<br>` inside `.letterSignoff`; AST-1162 non-negative `.signature-img` margin still present; token-absent / image-omitted signoff still has no empty `<img>` and still preserves newlines in remaining text.

1. In `src/core/builder.py`, open `_html_with_signature_image_token`.
2. Introduce a tiny local helper **inside this function** (or a one-line private helper next to it if DRY with both return paths) that:
   - Takes a raw text segment.
   - Normalizes `\r\n` → `\n` (same as from-block / letter paths in this module).
   - Returns `html.escape(segment).replace(chr(10), "<br>")`.
3. **Token-absent path** (today `return html.escape(signature_text or "")`): return the helper result for `signature_text or ""` instead of bare escape.
4. **Token-present path** (today `sep.join(html.escape(part) for part in parts)`): join with `img_html` / `""` as today, but map each `part` through the helper instead of bare `html.escape`.
5. Do **not** change:
   - `img_html` assembly / `class="signature-img"`
   - omit policies / `get_cover_letter_render_token` contract checks
   - `_emit_somerset_cover_html_document` CSS (keep AST-1162 `margin: 8px 0 8px 0`)
   - `signoff_parts` assembly that already appends closing + `"<br>"` before the fragment
   - `_emit_cover_signoff_html` (resume cover family — out of scope)
6. Smoke-check (builder emit or HTML string inspect): for fields shaped like closing `Best,` + signature `{$SIGNATURE_IMAGE}\nSusan Somerset\nSenior Product Manager` with an image src, the `.letterSignoff` inner HTML contains the img then `Susan Somerset<br>Senior Product Manager` (or equivalent escaped text with `<br>` between name and title), and `.signature-img` CSS still has non-negative bottom margin.

⚠️ **Decision:** Fix in `_html_with_signature_image_token` (shared by session + job SomersetCover) via post-escape newline→`<br>`, mirroring `.lettercontent p` — not CSS `white-space` on `.letterSignoff`. That keeps relative authored order without inventing fields or reopening token/CSS margin scope.

## Execution contract

- Execute Stage 1 in order; one `code(AST-1165):` commit on the epic worktree, then `git push origin HEAD:sub/AST-1161/AST-1165-uat-signoff-loses-line-breaks-between-name-and-title`.
- Do not add files or edit `tests/` / bible.
- If `_html_with_signature_image_token` has moved or signature emit no longer calls it — stop and comment on the **parent** with the stage-blocked format.

## Self-Assessment

**Scope:** `Single-Component` — one helper in `src/core/builder.py` used by shared SomersetCover signoff emit.

**Conf:** `high` — Diagnosis matches the code: escape-only join; letter body already shows the newline→`<br>` pattern to copy.

**Risk:** `low` — limited to signature fragment HTML; wrong `<br>` placement is Archie-visible at UAT; AST-1162 CSS and token omit paths left untouched.

## Rules check (ASTRAL_CODE_RULES)

- §1.1 in-scope-only / no-cross-contamination: SomersetCover signature fragment only; no resume signoff / token contract / CSS margin reopen.
- §1.3 DRY: reuse the same escape+`<br>` pattern already used for letter paragraphs in this file.
- §2.1 / §2.4 / §2.6: N/A.
- §3.3 / §3.5: no new public modules; local helper only.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1161/AST-1165-uat-signoff-loses-line-breaks-between-name-and-title`
**Tip:** `75b56978`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `75b56978` | `_html_with_signature_image_token`: escape + newline→`<br>` (token present + absent) |

## Radia review

[code-rubric] revision=1

**Rubric:** code-rubric.v1
**Ticket:** AST-1165
**Publish ref:** `31ebb768a7ba3eb8d685932c058839e9f63882cd`
**Overall:** CLEAN

**Full-set sweep:** all 65 active statutes scored in-session (22 universal, 43 scoped). Zero `violates`, zero `needs-discussion`. Scoped statutes outside `src/core/**` / `docs/features/**` / test-tree paths (`ui/**`, `data/**`, `dispatcher.py`, `config.py`, seed/agent-table paths, spikes/artifacts-dir) are `not-applicable`. No Joan plan-rubric verdict attached — noted, not a block.

**Pattern conformance:** none cited (description checkboxes are statute ids already covered by the full sweep, not `canon/patterns/*` ids).

**Plan adherence:**
- Diff is exactly Stage 1: local `_esc_br` helper added inside `_html_with_signature_image_token`, used on both the token-present join path and the token-absent full-text path — no img markup / omit-policy / `.signature-img` CSS changes.
- `_esc_br` is DRY with the module's existing `\r\n`→`\n` normalization + `html.escape(...).replace(chr(10), "<br>")` pattern already used verbatim for letter-body paragraphs (`src/core/builder.py:724`) and `from_block`/`to_block` (`:703-704`, `:711-712`) — not a new hardcoded literal, it mirrors established precedent in the same file.
- Sibling checks hold: AST-1162 `.signature-img { margin: 8px 0 8px 0 }` untouched (new test asserts `-25px` absent); AST-1126 token-absent/omit path still emits no `<img>`. Per-commit boundaries clean: `code(AST-1165)` touches only `src/core/builder.py`; `test(AST-1165)` touches only `tests/` + `docs/test-bible/`; single `merge-tests(AST-1165)` merge onto the sub.

**What's solid:** Fix matches the plan's explicit "wrong fix to avoid" guardrails — no `white-space: pre`, no invented name/title fields, no CSS-only patch, no token-contract change. New test class covers session + job SomersetCover paths and the token-absent no-`<img>` case.

**Notes:** Local pytest re-run blocked in this shell (no Python 3.10+ available); relying on Betty's `merge-tests(AST-1165)` SHA and the Tests Passed gate for green confirmation.

## Frame diff

(none)

context_tokens≈12000
— Radia
