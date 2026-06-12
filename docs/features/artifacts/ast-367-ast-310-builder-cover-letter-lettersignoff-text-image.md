# AST-367 — [AST-310] builder: cover letter letterSignoff (text + image)

**Linear:** [AST-367](https://linear.app/astralcareermatch/issue/AST-367/ast-310-builder-cover-letter-lettersignoff-text-image)  
**Feature branch:** `<agent>/ast-367-ast-310-builder-cover-letter-lettersignoff-text-image`  
**Parent:** [AST-310](https://linear.app/astralcareermatch/issue/AST-310/cover-letter-signature-profile-fields)

## Summary

Extend **`src/core/builder.py`** so the cover-letter **sign-off** region renders **(1)** text from **`job_data.artifacts.cover_letter.signature`** (already resolved by `_resolve_cover_letter` / pipeline) **combined with** **(2)** optional image from **`candidate_data.profile.cover_letter_signature_image`** (string URL or `data:image/...;base64,...` per **AST-310**). If the image string is missing or empty, emit **text-only** sign-off with no broken `<img>`. Apply **`html.escape`** to text; for URLs use a **strict allowlist** before emitting `src` — **only** `http:`, `https:`, or `data:image/jpeg` / `data:image/png` prefixes (reject anything else to mitigate XSS). Layout: one HTML block (e.g. `.cover-signoff`) containing optional `<img>` then pre-wrapped signature lines.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/builder.py` | New helper `_emit_cover_signoff_html(cover: dict, profile: dict) -> str`; integrate from `_emit_cover_sections_html` or replace signature-only section with combined signoff. | core |

## Stage 1: URL / data URL safety

**Done when:** Unit-level reasoning documented in module docstring: rejected schemes never reach `src`.

1. Implement `_safe_image_src(raw: str) -> Optional[str]` returning normalized string or `None`.
2. `html.escape` text portions; never concatenate raw URL into HTML without validation.

## Stage 2: HTML composition

**Done when:** Print view shows image above or below signature text per ResumeSite reference (`docs/features/artifacts/ResumeSite` if parity needed — **read** `styles07.css` for `.cover-block` spacing).

1. If `cover.get("signature")` non-empty, escape and wrap in `<p>`.
2. If safe image src, `<img src="..." alt="Cover letter signature" style="max-width:240px;height:auto;" />`.
3. If both empty, emit nothing for sign-off block.

## Stage 3: Wire `build_resume_from_job`

**Done when:** `build_resume_from_job` passes `cd.get("profile")` into cover HTML emitter (signature may need profile — adjust function signature of `_emit_cover_sections_html` to accept `profile` dict).

## Self-Assessment

**Scope — `Single-Component`**  
`builder.py` only.

**Conf — `Medium`**  
Depends on **AST-310** field names and **AST-309** `cover_letter` dict shape.

**Risk — `Medium`**  
XSS if URL validation is wrong.

## Self-review vs ASTRAL_CODE_RULES

§1.3 — small helper; §3.3 — no new imports from `ui`.

## Revisions

**Revision 1 — 2026-04-29**  
Driven by: Linear parent **AST-310** split (Hedy builder lane).  
Changes: Scoped to `builder.py` only; profile/token/prompt work stays on **AST-310**.

## Review (implementation)

Built by Hedy.

- **Branch:** `<agent>/ast-367-ast-310-builder-cover-letter-lettersignoff-text-image`
- **Commit:** `63d447db88cad8ca2cf72729bb881e591a99648a`
- **Summary:** `_safe_image_src` / `_emit_cover_signoff_html` per plan; `_emit_cover_sections_html(cover, profile)`; `build_resume_from_job` passes `cover_profile` into `_emit_html_document` for sign-off image + signature text.

## Review (Radia) — 2026-05-06

**Diff:** `origin/dev`…`<agent>/ast-367-ast-310-builder-cover-letter-lettersignoff-text-image` (`src/core/builder.py` + this doc).

### What’s solid

- **Plan fidelity:** `_safe_image_src`, `_emit_cover_signoff_html`, profile plumbed from `build_resume_from_job` → `_emit_html_document` → `_emit_cover_sections_html` matches the staged plan (Stages 1–3).
- **§1.3 / §3.3:** Small helpers; **`urllib.parse.urlparse`** stays in core; no `ui` imports.
- **XSS hardening:** `http`/`https` scheme check via `urlparse`; `data:image/jpeg` and `data:image/png` only; rejects newlines, `<`, and other schemes including `javascript:` / `data:text/html` as documented in the docstring.

### Issues

| Severity | Topic | Detail |
|----------|--------|--------|
| *Advisory* | a11y | Sign-off `<img alt="">` is empty; acceptable for print/PDF pipeline but consider a short alt if UI parity matters later. |

### Recommended actions

1. Spot-check generated HTML with **http**, **https**, valid **data:image/png**, and a rejected `data:image/svg+xml` / `javascript:` string to confirm `_safe_image_src` behavior.
2. Confirm **`cover_letter_signature_image`** field name matches **AST-310** profile UI payload end-to-end.

**Counts:** fix-now **0** · discuss **0** · advisory **1**

— Radia

## Resolution (f-resolve-linear) — 2026-05-06

**Radia review:** fix-now **0** · discuss **0**.

**Advisory — sign-off image `alt`**  
Set static **`alt="Cover letter signature"`** on the sign-off `<img>` (src remains `html.escape`’d; alt is a fixed English label, not user content).

**Verify:** `python3 -m py_compile src/core/builder.py` (clean).
