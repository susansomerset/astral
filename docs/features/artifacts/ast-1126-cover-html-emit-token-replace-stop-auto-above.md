# AST-1126 — Cover HTML emit — token replace and stop auto-above

**Linear:** [AST-1126](https://linear.app/astralcareermatch/issue/AST-1126/cover-html-emit-token-replace-and-stop-auto-above-support-signature)  
**Parent:** [AST-1123](https://linear.app/astralcareermatch/issue/AST-1123/support-signature-image-as-a-token-in-the-cover-letter) — Support Signature_Image as a token in the cover letter  
**Publish ref:** `origin/sub/AST-1123/AST-1126-cover-html-emit-token-replace-stop-auto-above`  
**Blocked by (done):** [AST-1125](https://linear.app/astralcareermatch/issue/AST-1125/cover-letter-signature-image-token-contract-support-signature-image-as) — config contract already on `ftr` / this sub tip

After AST-1125’s `BUILD_CONFIG["cover_letter_render_tokens"]["SIGNATURE_IMAGE"]` contract: job and session cover HTML emit stop unconditional signature-image placement; replace `{$SIGNATURE_IMAGE}` at the token position only (safe `<img>` via existing `_safe_image_src`); if the token is absent, omit the image (no fallback insert); Style D debug on touched cover paths reports token presence and image accepted / absent / rejected. Does **not** own profile upload UI, resume emit, or the config contract.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/builder.py` | Shared SIGNATURE_IMAGE resolve/replace helpers; rewrite job `_emit_cover_signoff_html` (stop auto-prepend); rewrite session signoff emit (stop auto-inject); Style D debug lines on job + session cover success paths; import `get_cover_letter_render_token` | core |

**Out of scope (do not touch):**

| Item | Owner / reason |
|------|----------------|
| `BUILD_CONFIG["cover_letter_render_tokens"]` / `get_cover_letter_render_token` | AST-1125 (already shipped) |
| Resume base / job / session HTML emit (`build_base_resume`, `build_resume*`, `build_session_base_resume`, resume branches of `_emit_html_document`) | excluded — must not resolve `{$SIGNATURE_IMAGE}` |
| Candidate Profile upload/validation (`api_candidate`, UI signature_image field) | excluded |
| `TOKEN_SOURCES` / `resolve_tokens` | excluded — binary image must not enter LLM prompts |
| Admin React Session Cover Letter page | AST-1025 — no UI change; API continues to pass `signature` text (may now contain the literal) |
| `tests/` / `docs/test-bible/**` | Betty |

## Stage 1: Shared token helpers + job cover signoff

**Done when:** Job cover HTML from `build_cover_letter` / `build_cover_letter_from_job` never prepends a signature `<img>` above the signature text; when `cover["signature"]` contains `tok["literal"]` and the image at `tok["path"]` passes `_safe_image_src`, the `<img>` appears at the token position inside the signoff; when the token is absent, no signature image is emitted even if a valid image exists; when the token is present but image missing/rejected, the literal is removed and no broken `<img>` is emitted; `debug=True` on `build_cover_letter_from_job` logs token + three-way image status; `python3 -m py_compile src/core/builder.py` passes.

1. In `src/core/builder.py`, update the config import to include `get_cover_letter_render_token`:
   ```python
   from src.utils.config import (
       BUILD_CONFIG,
       RESUME_STRUCTURE_CONTACT_SECTION_IDS,
       get_cover_letter_render_token,
   )
   ```

2. Add two private helpers near `_safe_image_src` (before `_emit_cover_signoff_html`):

   ```python
   def _lookup_dotted_path(root: Any, dotted: str) -> Any:
       """Walk ``a.b.c`` on nested dicts; return ``None`` if any segment missing/non-dict."""
       cur: Any = root
       for part in (dotted or "").split("."):
           if not part or not isinstance(cur, dict):
               return None
           cur = cur.get(part)
       return cur


   def _signature_image_token_status(
       signature_text: str,
       candidate_root: dict,
   ) -> tuple[str, Optional[str], str]:
       """Return ``(token_status, safe_src_or_None, image_status)``.

       ``token_status``: ``present`` | ``absent``
       ``image_status``: ``accepted`` | ``absent`` | ``rejected``
         - ``absent``: path value missing / empty / non-string
         - ``rejected``: non-empty raw failed ``_safe_image_src``
         - ``accepted``: ``_safe_image_src`` returned a usable src
       """
       tok = get_cover_letter_render_token("SIGNATURE_IMAGE")
       literal = tok["literal"]
       token_status = "present" if literal in (signature_text or "") else "absent"
       raw = _lookup_dotted_path(candidate_root, tok["path"])
       if not isinstance(raw, str) or not raw.strip():
           return token_status, None, "absent"
       safe = _safe_image_src(raw)
       if safe is None:
           return token_status, None, "rejected"
       return token_status, safe, "accepted"
   ```

3. Add a private HTML fragment builder that applies AST-1125 policies (do **not** hardcode the literal — always `tok["literal"]`):

   ```python
   def _html_with_signature_image_token(
       signature_text: str,
       *,
       safe_src: Optional[str],
       token_status: str,
       img_html: str,
   ) -> str:
       """Escape signature text; replace or omit ``SIGNATURE_IMAGE`` literal per contract.

       - token absent → escape full text only (caller must not inject ``img_html``).
       - token present + ``safe_src`` → escape segments around literal; insert ``img_html`` once
         at the first occurrence (replace that occurrence; if literal appears more than once,
         replace **all** occurrences with the same ``img_html`` / empty per policy — no leftover
         literal text).
       - token present + no ``safe_src`` → omit literal (empty string at each occurrence).
       Newlines in text segments stay as escaped text (same as today's single-``<p>`` job path);
       do not invent new ``<br>`` rules on this ticket.
       """
   ```

   Implementation requirements for step 3:
   - Load `tok = get_cover_letter_render_token("SIGNATURE_IMAGE")` and use `tok["literal"]` only.
   - If `token_status == "absent"`: return `html.escape(signature_text or "")`.
   - If `token_status == "present"`: `parts = (signature_text or "").split(tok["literal"])`; join `html.escape(part)` with separator `img_html if safe_src else ""`.
   - Honor `tok["absent_token_policy"]` / `tok["missing_or_rejected_image_policy"]` as already set to `"omit"` — do not invent a fallback insert path. If either policy key is ever not `"omit"`, **stop and comment on the parent** (do not improvise).

4. Rewrite `_emit_cover_signoff_html(cover: dict, profile: dict) -> str`:
   - Treat `profile` as today’s **contact** dict (call sites already pass `cd.get("contact")`). Build `candidate_root = {"contact": profile or {}}` so `tok["path"]` (`contact.cover_letter_signature_image`) resolves.
   - `sig = (cover.get("signature") or "")` — keep raw (including whitespace) for token search; strip only when deciding emptiness for the early return.
   - `token_status, safe_src, _image_status = _signature_image_token_status(sig, candidate_root)`.
   - **Stop** the current unconditional prepend:
     ```python
     # DELETE this shape:
     if safe_src:
         inner_lines.append('<img ...>')
     if sig:
         inner_lines.append(f'<p>{html.escape(sig)}</p>')
     ```
   - Replacement shape:
     - If `not (sig or "").strip()` and token absent: return `""` (same empty-signoff behavior as today when no text and no image — but image alone must **not** create a signoff).
     - If signature text is non-empty (or was only the token): build
       `img_html = f'<img src="{html.escape(safe_src, quote=True)}" alt="Cover letter signature" style="max-width:240px;height:auto;" />'` when `safe_src` else `""`.
       - `body = _html_with_signature_image_token(sig, safe_src=safe_src, token_status=token_status, img_html=img_html)`.
       - If `body` is empty after omit: return `""`.
       - Else emit the existing section wrapper with **one** inner `<p>{body}</p>` when the result has no raw `<img>`, **or** when it contains an `<img>`, emit the section with the fragment directly inside the section (img + escaped text) **without** wrapping the `<img>` in a way that re-escapes it. Concrete rule: if `safe_src` and `token_status == "present"`, use:
         ```html
         <section class="cover-block cover-signoff" aria-label="Cover sign-off">
         {fragment}
         </section>
         ```
         where `fragment` is the joined escaped-parts + img (no extra outer `<p>` around the img). If there is escaped text before/after the img, keep those text nodes as `<p>…</p>` **or** plain escaped text separated by the img — pick **this exact shape** to match visual order closing→image→name when the signature string is e.g. `Sincerely,\n\n{$SIGNATURE_IMAGE}\nJane Doe\nTitle`:
         ```html
         <section class="cover-block cover-signoff" aria-label="Cover sign-off">
               <p>{escaped_before}</p>
               {img_html}
               <p>{escaped_after}</p>
         </section>
         ```
         Omit empty `<p></p>` nodes when a side is empty/whitespace-only after strip. When token absent: single `<p>{escaped full signature}</p>` as today (no img). When token present and image omitted: single `<p>` with literal removed (join escaped parts with `""`), or two `<p>`s only if you split on the literal and both sides are non-empty — prefer **one** `<p>` with concatenated escaped parts when `safe_src` is None.
   - Do **not** change `_emit_cover_sections_html` beyond what `_emit_cover_signoff_html` already feeds.
   - Do **not** touch resume emit branches.

5. Update `build_cover_letter_from_job` debug block (`debug=True` success path only):
   - After HTML is built, compute status from the same cover signature + contact:
     ```python
     contact = cd.get("contact") or {}
     cover_sig = (cover.get("signature") or "")
     token_status, _safe, image_status = _signature_image_token_status(
         cover_sig, {"contact": contact}
     )
     ```
   - Keep existing `debug_index` header.
   - Replace the current single `signature_image=accepted|absent_or_rejected` detail with:
     ```python
     _log.debug_detail(f"signature_image_token={token_status}")
     _log.debug_detail(f"signature_image={image_status}")
     ```
   - Keep `cover_source`, fields nonempty, `html_chars`, and `html_preview` details as they are today.

⚠️ **Decision:** Job signoff keeps existing img attributes (`alt="Cover letter signature"`, inline max-width style). Session keeps its own `class="signature-img"` markup in Stage 2 — do not unify CSS across the two DOM families.

⚠️ **Decision:** Image alone (valid src, no signature text, no token) must not emit a signoff section. Parent OQ1/OQ2: image only where the token resolves.

## Stage 2: Session cover — stop auto-inject + token replace + debug

**Done when:** `build_session_cover_letter` no longer inserts a signature `<img>` between `signoff_closing` and `signature` unless `fields["signature"]` contains the config literal; image bytes are read from `contact.cover_letter_signature_image` via `tok["path"]` (not `profile`); `debug=True` reports `signature_image_token` + three-way `signature_image`; resume builders unchanged; `python3 -m py_compile src/core/builder.py` passes.

1. In `build_session_cover_letter`, replace the profile-based image read:
   ```python
   # DELETE / replace:
   profile = _coerce_candidate_blob(row).get("profile") or {}
   sig_src = _safe_image_src(profile.get("cover_letter_signature_image"))
   ```
   With:
   - `cd = _coerce_candidate_blob(row)`.
   - `token_status, sig_src, image_status = _signature_image_token_status(
         fields.get("signature") or "", cd
     )` — note full candidate blob so `tok["path"]` (`contact.cover_letter_signature_image`) resolves after AST-1014 contact migration.
   - Keep `sig_image_status` variable name only if useful; prefer storing `token_status` and `image_status` for debug. When `candidate_id` is empty: `token_status, sig_src, image_status` from the signature text against `candidate_root={}` (image will be `absent`; token may still be `present` → omit literal / no img).

2. Change the call to `_emit_session_cover_html_document` so the emitter receives enough to apply token policy — either:
   - **Preferred:** pass `signature_image_src=sig_src` **and** let the emitter read token presence from `fields["signature"]`, **or**
   - Pass `token_status` as an extra kw-only arg.
   - Do **not** keep today’s behavior of “if `signature_image_src`: always inject between closing and name”.

3. Rewrite the signoff assembly inside `_emit_session_cover_html_document`:
   - Keep `signoff_closing` escaped + `<br>` as today.
   - **Delete** the unconditional block:
     ```python
     if signature_image_src:
         signoff_parts.append('<img ...>')
         signoff_parts.append("<br>")
     signoff_parts.append(html.escape(sig_name))
     ```
   - Replacement:
     - `tok = get_cover_letter_render_token("SIGNATURE_IMAGE")`.
     - `raw_sig = fields.get("signature") or ""`.
     - `token_status = "present" if tok["literal"] in raw_sig else "absent"`.
     - `img_html = f'<img src="{html.escape(signature_image_src, quote=True)}" class="signature-img" alt="Signature">'` when `signature_image_src` and `token_status == "present"`, else `""`.
     - Build signature fragment via `_html_with_signature_image_token(raw_sig, safe_src=signature_image_src, token_status=token_status, img_html=img_html)`.
     - Append that fragment to `signoff_parts` (session historically appends the name as a text node after `<br>` — keep closing + `<br>` + fragment; if fragment contains an `<img>`, do not wrap the whole fragment in `html.escape`).
     - If after omit the signature fragment is empty, still emit closing (required field) — do not invent a placeholder image.

4. Update session `debug=True` success details:
   - Replace `signature_image={sig_image_status}` with:
     ```python
     _log.debug_detail(f"signature_image_token={token_status}")
     _log.debug_detail(f"signature_image={image_status}")
     ```
   - When no `candidate_id`, `image_status` is `absent` (unless you only looked at token — still `absent` for image). Keep other existing detail lines (`to_block`, `subject`, `candidate_id`, `html_chars`, preview).

5. Confirm `"cover_letter" in get_cover_letter_render_token("SIGNATURE_IMAGE")["surfaces"]` before emitting a replacement on both job and session paths. If missing, **stop and comment on the parent** — do not emit the image.

6. Do **not** edit `src/ui/api/api_admin.py`, resume builders, or `src/utils/config.py` on this ticket.

⚠️ **Decision:** Session signature field is the token host (e.g. `{$SIGNATURE_IMAGE}\nSusan Somerset`). `signoff_closing` stays closing-only. That matches parent “token in cover letter signature content” and AST-1024’s `signature` ↔ artifact `signature` spine without a new field.

⚠️ **Decision:** Switch session image source from legacy `profile.cover_letter_signature_image` to `tok["path"]` (`contact.cover_letter_signature_image`). Required by AST-1125; profile path would silently omit images after contact migration.

## Self-Assessment

**Scope — `Single-Component`**  
One core module (`builder.py`) on cover emit helpers and two cover entrypoints’ debug lines; no utils/ui/resume edits.

**Conf — `high`**  
AST-1125 contract + integration note spell the algorithm; job and session currently show the exact auto-above/auto-inject code to delete; `_safe_image_src` is reused.

**Risk — `Medium`**  
Wrong omit/replace would hide signatures or leave literals in print HTML; session contact-path switch could blank images if a row still only had profile-era data — mitigated by AST-1014 contact ownership and AC coverage in Betty’s pass.

## Self-review vs ASTRAL_CODE_RULES

| Rule | Check |
|------|--------|
| `astral.standards.in-scope-only` | Cover job + session emit only; resume/profile/config contract excluded. |
| `astral.standards.no-cross-contamination` | Resume emit paths listed do-not-touch; no `cover_letter_render_tokens` import on resume builders. |
| `astral.standards.debug-contract-gated` | New/changed detail lines only under existing `debug=True` gates; Style D index headers already present — extend details only. |
| `astral.layers.import-direction` / `pattern.layers.import-discipline` | core → utils accessor only; no ui/external imports added. |
| `astral.standards.dry-and-focused-functions` | Reuse `_safe_image_src`; shared token helpers; no second validator. |
| `astral.config.config-source-of-truth` / `astral.standards.no-hardcoded-sets` | Literal + path + policies from `get_cover_letter_render_token` only. |
| §1.3 DRY | One replace helper shared by job + session. |

## Review (stub — build-child)

| Field | Value |
|-------|-------|
| Branch | `sub/AST-1123/AST-1126-cover-html-emit-token-replace-stop-auto-above` |
| Tip | `678bc856` |
| Notes | Job + session cover emit: token-only `{$SIGNATURE_IMAGE}` replace via `get_cover_letter_render_token`; stop auto-prepend/inject; Style D `signature_image_token` + three-way `signature_image`. |
