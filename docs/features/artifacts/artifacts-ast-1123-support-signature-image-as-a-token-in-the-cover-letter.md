# AST-1123 — Support Signature_Image as a token in the cover letter
**Component:** artifacts  
**Children:** AST-1125, AST-1126  
**Linear archived:** AST-1123 2026-08-07; AST-1125 2026-08-07; AST-1126 2026-08-07

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-08-02 10:46 | AST-1125 | docs | `62f2bfa54` | docs(AST-1125): plan — cover-letter SIGNATURE_IMAGE token contract |
| 2026-08-02 10:49 | AST-1125 | code | `314f39e14` | code(AST-1125): BUILD_CONFIG cover SIGNATURE_IMAGE render-token contract |
| 2026-08-02 10:49 | AST-1125 | docs | `d4ae02000` | docs(AST-1125): review stub after code commit |
| 2026-08-02 10:52 | AST-1125 | test | `11703177b` | test(AST-1125): cover-letter SIGNATURE_IMAGE render-token contract coverage |
| 2026-08-02 10:52 | AST-1125 | merge-tests | `26bfa458a` | merge-tests(AST-1125): origin/tests 11703177b |
| 2026-08-02 10:56 | AST-1125 | docs | `3dd4db02e` | docs(AST-1125): Radia review — findings |
| 2026-08-02 10:57 | AST-1125 | resolve | `42c634118` | resolve(AST-1125): — clean |
| 2026-08-02 11:02 | AST-1126 | merge-resume | `4487bb724` | merge-resume(AST-1126): origin/dev |
| 2026-08-02 11:03 | AST-1126 | docs | `978618bc7` | docs(AST-1126): plan — cover HTML token replace and stop auto-above |
| 2026-08-02 11:08 | AST-1126 | code | `33d143fda` | code(AST-1126): token-only cover signature image; stop auto-above |
| 2026-08-02 11:08 | AST-1126 | docs | `83aed9330` | docs(AST-1126): fix Review stub tip after amend |
| 2026-08-02 11:12 | AST-1126 | merge-tests | `6570adbdf` | merge-tests(AST-1126): origin/tests f50640e6b |
| 2026-08-02 11:12 | AST-1126 | test | `f50640e6b` | test(AST-1126): cover SIGNATURE_IMAGE token emit + stop auto-above |
| 2026-08-02 11:15 | AST-1126 | docs | `0364b5338` | docs(AST-1126): Radia review — findings |
| 2026-08-02 11:17 | AST-1126 | resolve | `7126f9d7a` | resolve(AST-1126): — clean |
| 2026-08-02 11:18 | AST-1123 | prep-uat | `72ef6d514` | prep-uat(AST-1123): rebuild merge ticket log |
| 2026-08-07 18:24 | AST-1125 | docs | `e94c8a46a` | docs(AST-1125): archive Linear issue content |
| 2026-08-07 18:24 | AST-1126 | docs | `04e77f5d7` | docs(AST-1126): archive Linear issue content |
| 2026-08-07 18:27 | AST-1123 | docs | `3e7045036` | docs(AST-1123): archive Linear issue content |

## Epic — AST-1123
_Archived: 2026-08-07 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1123/support-signature-image-as-a-token-in-the-cover-letter · Status at archive: Archive · Project: Astral Artifacts · Assignee: chuckles · Priority / estimate: — · Blocked by / blocks / related: —_

### Purpose

Cover letters currently stack the candidate's signature image *above* the entire signature block, so the handwritten image sits before the closing ("Sincerely,") and the name/title. Susan needs cover-letter HTML render to place that image where a letter actually signs — between the closing and the candidate's name and title — by supporting a cover-only `{$SIGNATURE_IMAGE}` token that resolves to the stored signature image. Resume and other surfaces stay untouched.

### Functional scope

1. **Cover-only token.** When rendering a cover letter, `{$SIGNATURE_IMAGE}` is replaced with the candidate's validated signature image. The token is not honored on resume HTML or any non-cover render path.
2. **No auto-stack above signature text.** Cover letter HTML must not place the signature image above the signature text block as a separate unconditional prepend. Once the token path is live, the image appears only where the token is resolved (or not at all if there is no image / rejected image).
3. **Correct visual order.** With a normal signature text shape (closing, then name and title), resolving the token between those parts yields: closing → signature image → candidate name and title. The image must not sit above the closing.
4. **Safe image only.** Replacement uses the same acceptance rules already used for cover signature images (rejected or missing values produce no image element; no unsafe `src`).
5. **Debug on cover render.** When `debug=True` on touched cover-letter render paths, log what was found and what was recorded for the token/image step (token present or absent; image accepted, absent, or rejected; outcome), using Style D index headers and `|` detail lines per the AST-538 / Code Rules debug contract.

### Architectural definition

* **Patterns to reuse:** `pattern.config.config-block` (token name and cover-only resolution contract belong in config, not scattered literals); `pattern.layers.import-discipline` (config owns the contract; core cover emit performs replacement; no layer inversion).
* **New patterns proposed:** none (single cover-render token/placement fix; no new reusable catalog shape).
* **Applicable statutes:** `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `astral.standards.in-scope-only` (cover letter render only); `astral.standards.no-cross-contamination` (keep cover emit isolated from resume emit); `astral.layers.import-direction`; `astral.standards.debug-contract-gated`; `astral.standards.dry-and-focused-functions` (reuse existing safe-image validation; no second validator).

### Boundaries

* Does **not** change Candidate Profile upload/validation UI for the signature image (JPEG limits and storage stay as today).
* Does **not** add signature-image tokens to resume HTML, job resume, or session base resume.
* Does **not** redesign cover letter field shape (Subject / Letter / signature) or the cover-letter daisy chain beyond what is required for token placement at render.
* Does **not** invent a new signature-image storage field — uses the existing candidate contact signature image.
* Does **not** break existing `{$COVER_LETTER_SIGNATURE}` text injection for signature prose.
* **Resolved (was OQ1):** no `{$SIGNATURE_IMAGE}` token in cover signature content → **omit** the image (no fallback auto-insert between closing and name).
* **Resolved (was OQ2):** remove the image's current default placement on cover render paths (including Admin Session Cover Letter auto-inject) and rely **only** on `{$SIGNATURE_IMAGE}` in cover letter signature content.

### Acceptance criteria

1. Rendering a job cover letter whose signature text contains `{$SIGNATURE_IMAGE}` between the closing and the name/title shows the signature image in that position — not above the closing.
2. The literal token string `{$SIGNATURE_IMAGE}` does not appear in the rendered cover HTML when a valid image is available.
3. When the candidate has no usable signature image, cover render does not emit a signature `<img>`, and the layout does not leave a broken image placeholder.
4. Cover letter HTML no longer places the signature image above the full signature text block as an unconditional prepend.
5. Resume (base / job / session) HTML render paths do not resolve or display `{$SIGNATURE_IMAGE}` as an image.
6. With `debug=True` on a touched cover render path, debug output includes an index header and `|` detail for token presence and image accepted / absent / rejected.

### Dependencies and blockers

none.

### Open questions

none.

### Proposed child tickets

**1[!]: Cover-letter SIGNATURE_IMAGE token contract — Ada** — Owns the config-side contract: register `{$SIGNATURE_IMAGE}` for cover-letter render resolution (cover-only; not a general LLM prompt binary injection), tied to the existing candidate signature-image source. Does **not** own HTML emit placement.
**Citations:** `pattern.config.config-block`, `astral.config.config-source-of-truth`, `astral.standards.no-hardcoded-sets`.

**2: Cover HTML emit — token replace and stop auto-above — Hedy** — After #1: cover HTML emit (job + session) stops unconditional/default image placement; replaces `{$SIGNATURE_IMAGE}` with a safe image at the token position only; if the token is absent, omit the image (no fallback insert); Style D debug on touched cover paths. Does **not** own profile upload UI or resume emit.
**Citations:** `astral.standards.in-scope-only`, `astral.standards.no-cross-contamination`, `astral.standards.debug-contract-gated`, `astral.layers.import-direction`, `pattern.layers.import-discipline`.

### Original brief

Right now, we are putting the signature ABOVE the Signature text, and it should fall BETWEEN the "Sincerely," and the Candidate's name and title.

Please allow when rendering the Cover letter (nowhere else) that {$SIGNATURE_IMAGE} is replaced with the image file correctly, and it does NOT appear above the signature text anymore.

#### Comments

##### chuckles — 2026-08-02T17:37:41.571Z
@susan

1. If the candidate has a valid signature image but the cover signature text has **no** `{$SIGNATURE_IMAGE}` token — omit the image entirely, or fallback-insert between the first line (closing) and the remaining name/title lines?
2. Admin Session Cover Letter already places image between closing and name via separate fields — leave that path unchanged (no token), or require the same `{$SIGNATURE_IMAGE}` token there too?

_(Resolved as OQ1 / OQ2 in Boundaries above: omit when the token is absent; require the token on the session path too, removing its separate auto-inject.)_

### Files changed (plan vs actual)

_No product commit trail on the parent — the one `prep-uat(AST-1123)` commit rebuilds the merge ticket log. Implementation landed via AST-1125 (config contract) and AST-1126 (emit)._

_Implementation detail may live in git history on `origin/dev`._

## Sub-issues

### AST-1125 — Cover-letter SIGNATURE_IMAGE token contract
_Archived: 2026-08-07 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1125/cover-letter-signature-image-token-contract-support-signature-image-as · Status at archive: Archive · Project: Astral Artifacts · Assignee: ada · Priority / estimate: — · Blocked by / blocks / related: parent: AST-1123; unblocks AST-1126_

#### What this implements

Register a cover-only `{$SIGNATURE_IMAGE}` **render** contract in `BUILD_CONFIG` so cover HTML emit can resolve the candidate's existing signature image at the token position. This is **not** an LLM prompt token (`TOKEN_SOURCES` / `resolve_tokens`) and does **not** change HTML emit or profile upload.

#### Acceptance criteria

Parent AC1–2 (contract for image-at-token-position, literal not left in HTML when a valid image exists), AC5 (`surfaces: ["cover_letter"]` cover-only gate).

#### Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `BUILD_CONFIG["cover_letter_render_tokens"]` with `SIGNATURE_IMAGE` contract; add thin accessor `get_cover_letter_render_token` | utils |

**Out of scope:** cover HTML token replace / stop auto-above / Style D debug on emit (AST-1126); resume (base/job/session) HTML emit — must ignore this contract; `TOKEN_SOURCES` / `resolve_tokens` / Manage Tasks token pickers (binary image must not inject into prompts); Candidate Profile signature-image upload/validation UI; a new signature-image storage field (reuse `contact.cover_letter_signature_image`); `tests/` / bible (Betty).

#### Stage 1: BUILD_CONFIG cover render-token contract

**Done when:** `BUILD_CONFIG["cover_letter_render_tokens"]["SIGNATURE_IMAGE"]` exists with the fields below; `get_cover_letter_render_token("SIGNATURE_IMAGE")` returns that dict; `"SIGNATURE_IMAGE"` is **absent** from `TOKEN_SOURCES` / `get_tokens()`.

```python
# AST-1125: cover HTML render tokens (NOT TOKEN_SOURCES / resolve_tokens).
# Emit (AST-1126) reads this contract; resume builders must ignore it.
"cover_letter_render_tokens": {
    "SIGNATURE_IMAGE": {
        "literal": "{$SIGNATURE_IMAGE}",
        "surfaces": ["cover_letter"],
        "source": "candidate",
        "path": "contact.cover_letter_signature_image",
        "value_kind": "safe_image_src",
        # Parent OQ1: no token in signature content → omit image (no fallback insert).
        "absent_token_policy": "omit",
        "missing_or_rejected_image_policy": "omit",
    },
},
```

Plus a thin accessor `get_cover_letter_render_token(name) -> dict` (raises `KeyError` for unknown names) placed near the other `BUILD_CONFIG` helpers, documented as the required lookup path for emit — no hardcoded literal or candidate path in emit code. Do **not** add `SIGNATURE_IMAGE` to `TOKEN_SOURCES`, `resolve_tokens`, `get_tokens`, `get_manage_tasks_chain_tokens`, or `get_manage_agents_tokens`. Do **not** edit `builder.py`, session/job cover emit, resume emit, UI, or Candidate Profile. Storage path stays `contact.cover_letter_signature_image` (same field as today's profile signature image after the AST-1014 contact migration).

⚠️ **Decision:** Live in `BUILD_CONFIG`, not `TOKEN_SOURCES`. `TOKEN_SOURCES` feeds `resolve_tokens()` for LLM prompt text; a data-URL / image src must never be injected into prompts. `BUILD_CONFIG` already owns artifact **rendering** tokens.

⚠️ **Decision:** `surfaces: ["cover_letter"]` is the cover-only gate for AC5. Resume builders do not read `cover_letter_render_tokens`. Emit must check surface / only import this helper on cover paths.

⚠️ **Decision:** Policies `absent_token_policy` / `missing_or_rejected_image_policy` are declared here so emit does not invent product rules. Actual replacement and removal of the auto-above prepend are AST-1126.

**Integration note for AST-1126 (not this ticket):** emit should (1) `tok = get_cover_letter_render_token("SIGNATURE_IMAGE")`; (2) search cover signature text for `tok["literal"]`; (3) if present, resolve the candidate blob at `tok["path"]` through existing `_safe_image_src` — on accept replace the literal with a safe `<img>`, on reject/missing apply `missing_or_rejected_image_policy` (`omit`); (4) if absent, apply `absent_token_policy` (`omit` — no auto-insert); (5) stop the unconditional image prepend above the signature block (parent OQ2); (6) leave resume HTML paths alone.

**Self-Assessment:** Single-Component — one `BUILD_CONFIG` sub-block plus one accessor in `src/utils/config.py`; no core/ui/data changes. Conf high — mirrors the AST-365 / AST-1024 pattern of registering a contract in config ahead of emit; path already exists on contact. Risk low — config-only; wrong path would blank the image once emit lands (easy to spot); accidental `TOKEN_SOURCES` registration would be the high-risk mistake and is forbidden by Stage 1 step 3.

##### Comments

###### ada — 2026-08-02T17:46:20.129Z
Plan @ `62f2bfa5`. Single-Component — one `BUILD_CONFIG["cover_letter_render_tokens"]` block plus accessor; no core/ui/data edits. Conf high — same config-ahead-of-emit pattern as AST-365 / AST-1024; deliberately kept out of `TOKEN_SOURCES` so image bytes never hit LLM prompts. Risk low.

###### joan — 2026-08-02T17:48:20.659Z (plan-rubric.v1)
**Overall: APPROVED.** Stage 1 → parent AC1/AC2 (contract; emit owned by AST-1126), AC5 (`surfaces: ["cover_letter"]`; no resume/`TOKEN_SOURCES` edits). All in-scope statutes **conforms**.

###### betty — 2026-08-02T17:53:08.464Z
QA manifest AST-1125: cover render-token contract coverage in `test_config.py`. Publish `@ 26bfa458` (`merge-tests(AST-1125): origin/tests 11703177`).

###### radia — 2026-08-02T17:57:00.407Z (code-rubric.v1)
**Overall: DISCUSS** (C4 stragglers only — no product fix-now). Stage 1 shipped as planned: `BUILD_CONFIG["cover_letter_render_tokens"]["SIGNATURE_IMAGE"]` fields match the plan block; `get_cover_letter_render_token` returns that dict and raises `KeyError` for unknown names; `SIGNATURE_IMAGE` not in `TOKEN_SOURCES` / `get_tokens()`; `resolve_tokens` leaves the literal untouched; no emit/resume/profile/UI edits. All in-scope statutes **conforms**. **discuss (C4 straggler):** three plan-time-excluded statutes (`spikes-under-debug-dir`, `features-single-file-per-ticket`, `engineer-test-tree-ban`) in-scope on the code diff, each **conforms**. No `fix-now`.

#### Resolution (2026-08-02)

fix-now: none — product tip unchanged. discuss (C4 stragglers): acknowledged, all **conform**, no product patch.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/utils/config.py` | `BUILD_CONFIG["cover_letter_render_tokens"]["SIGNATURE_IMAGE"]` contract + `get_cover_letter_render_token` accessor | `314f39e14` |
| | _tests_ | render-token contract coverage | `11703177b` — `test_config.py` + test-bible (Betty) |

### AST-1126 — Cover HTML emit — token replace and stop auto-above
_Archived: 2026-08-07 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1126/cover-html-emit-token-replace-and-stop-auto-above-support-signature · Status at archive: Archive · Project: Astral Artifacts · Assignee: hedy · Priority / estimate: — · Blocked by / blocks / related: parent: AST-1123; blockedBy (done): AST-1125_

#### What this implements

After AST-1125's `BUILD_CONFIG["cover_letter_render_tokens"]["SIGNATURE_IMAGE"]` contract: job and session cover HTML emit stop unconditional signature-image placement; replace `{$SIGNATURE_IMAGE}` at the token position only (safe `<img>` via existing `_safe_image_src`); if the token is absent, omit the image (no fallback insert); Style D debug on touched cover paths reports token presence and image accepted / absent / rejected. Does **not** own profile upload UI, resume emit, or the config contract.

#### Acceptance criteria

Parent AC1 (image between closing and name/title), AC2 (literal absent when valid image available), AC3 (no broken placeholder when no usable image), AC4 (stop unconditional prepend), AC5 (resume paths untouched), AC6 (Style D debug on touched cover paths).

#### Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/builder.py` | Shared SIGNATURE_IMAGE resolve/replace helpers; rewrite job `_emit_cover_signoff_html` (stop auto-prepend); rewrite session signoff emit (stop auto-inject); Style D debug lines on job + session cover success paths; import `get_cover_letter_render_token` | core |

**Out of scope:** `BUILD_CONFIG["cover_letter_render_tokens"]` / `get_cover_letter_render_token` (AST-1125, already shipped); resume base/job/session HTML emit — must not resolve `{$SIGNATURE_IMAGE}`; Candidate Profile upload/validation UI; `TOKEN_SOURCES` / `resolve_tokens` (binary image must not enter LLM prompts); Admin React Session Cover Letter page (AST-1025 — no UI change; the API just passes `signature` text, which may now contain the literal); `tests/` / bible (Betty).

#### Stage 1: Shared token helpers + job cover signoff

**Done when:** Job cover HTML from `build_cover_letter` / `build_cover_letter_from_job` never prepends a signature `<img>` above the signature text; when `cover["signature"]` contains `tok["literal"]` and the image at `tok["path"]` passes `_safe_image_src`, the `<img>` appears at the token position inside the signoff; when the token is absent, no signature image is emitted even if a valid image exists; when the token is present but the image is missing/rejected, the literal is removed and no broken `<img>` is emitted; `debug=True` on `build_cover_letter_from_job` logs token + three-way image status.

1. Import `get_cover_letter_render_token` from `src.utils.config` alongside the existing `BUILD_CONFIG` / `RESUME_STRUCTURE_CONTACT_SECTION_IDS` import.
2. Add two private helpers near `_safe_image_src`: `_lookup_dotted_path(root, dotted)` (walks `a.b.c` on nested dicts, `None` on any missing/non-dict segment) and `_signature_image_token_status(signature_text, candidate_root) -> (token_status, safe_src_or_None, image_status)` — `token_status` `present`/`absent` (literal found in signature text); resolves `tok["path"]` on `candidate_root` via `_lookup_dotted_path`; non-string/blank raw → `image_status="absent"`; non-empty raw failing `_safe_image_src` → `"rejected"`; usable src → `"accepted"`.
3. Add `_html_with_signature_image_token(signature_text, *, safe_src, token_status, img_html) -> str`: token absent → escaped full text only, no `img_html`; token present + `safe_src` → split on `tok["literal"]`, join `html.escape(part)` with `img_html` at each occurrence (no leftover literal text); token present + no `safe_src` → omit literal (join with `""`). Uses `tok["literal"]` only — never a hardcoded string. Honors `absent_token_policy` / `missing_or_rejected_image_policy` as `"omit"` only — if either is ever not `"omit"`, **stop and comment on the parent**, do not improvise.
4. Rewrite `_emit_cover_signoff_html(cover, profile)`: build `candidate_root = {"contact": profile or {}}` (call sites already pass `cd.get("contact")` as `profile`) so `tok["path"]` resolves; `sig = cover.get("signature") or ""` (keep raw for token search); compute `token_status, safe_src, _image_status`. **Delete** the current unconditional prepend (`if safe_src: <img>`, then `if sig: <p>{sig}</p>`). Replacement: if signature text is blank and token absent → return `""` (image alone must not create a signoff — parent OQ1/OQ2); else build `img_html` from `safe_src` when present, run `_html_with_signature_image_token`, and if `token_status == "present"` and `safe_src` set, emit the section as `<p>{escaped_before}</p>{img_html}<p>{escaped_after}</p>` (omitting an empty side's `<p>`) so visual order is closing → image → name; when token absent, single `<p>{escaped full signature}</p>` (no img, as today); when token present but image omitted, single `<p>` with the literal removed.
5. Update the `build_cover_letter_from_job` `debug=True` success block: keep the existing `debug_index` header, `cover_source`, fields-nonempty, `html_chars`, `html_preview` details; replace the old single `signature_image=accepted|absent_or_rejected` line with two: `signature_image_token=<present|absent>` and `signature_image=<accepted|absent|rejected>`.

⚠️ **Decision:** Job signoff keeps existing img attributes (`alt="Cover letter signature"`, inline max-width style). Session keeps its own `class="signature-img"` markup in Stage 2 — do not unify CSS across the two DOM families.

⚠️ **Decision:** Image alone (valid src, no signature text, no token) must not emit a signoff section. Parent OQ1/OQ2: image only where the token resolves.

#### Stage 2: Session cover — stop auto-inject + token replace + debug

**Done when:** `build_session_cover_letter` no longer inserts a signature `<img>` between `signoff_closing` and `signature` unless `fields["signature"]` contains the config literal; image bytes are read from `contact.cover_letter_signature_image` via `tok["path"]` (not `profile`); `debug=True` reports `signature_image_token` + three-way `signature_image`; resume builders unchanged.

1. Replace the profile-based image read (`profile = _coerce_candidate_blob(row).get("profile") or {}`; `sig_src = _safe_image_src(profile.get("cover_letter_signature_image"))`) with `cd = _coerce_candidate_blob(row)`, `token_status, sig_src, image_status = _signature_image_token_status(fields.get("signature") or "", cd)` (full candidate blob so `tok["path"]` resolves post AST-1014; empty `candidate_id` → status computed against `candidate_root={}`, image `absent`, token may still be `present` → omit literal / no img).
2. `_emit_session_cover_html_document` must apply token policy rather than "always inject when `signature_image_src` is set" — pass `signature_image_src` and read token presence from `fields["signature"]` inside the emitter (or pass `token_status` as an extra kw-only arg).
3. Rewrite the signoff assembly: keep `signoff_closing` escaped + `<br>` as today; **delete** the unconditional `if signature_image_src: <img><br>` + name-append block; replace with `tok = get_cover_letter_render_token("SIGNATURE_IMAGE")`, `raw_sig = fields.get("signature") or ""`, `token_status = "present" if tok["literal"] in raw_sig else "absent"`, `img_html` built (with `class="signature-img" alt="Signature"`) only when `signature_image_src` and `token_status == "present"`, then `_html_with_signature_image_token(raw_sig, ...)` appended after closing + `<br>` (fragment not re-escaped if it contains an `<img>`). If the signature fragment is empty after omit, still emit closing (required field) — no placeholder image.
4. Update session `debug=True` success details: replace `signature_image={sig_image_status}` with the same two-line `signature_image_token` / `signature_image` pair; keep `to_block`, `subject`, `candidate_id`, `html_chars`, preview lines.
5. Confirm `"cover_letter" in get_cover_letter_render_token("SIGNATURE_IMAGE")["surfaces"]` before emitting a replacement on both job and session paths — if missing, **stop and comment on the parent**, do not emit the image. Do not edit `api_admin.py`, resume builders, or `config.py` on this ticket.

⚠️ **Decision:** Session signature field is the token host (e.g. `{$SIGNATURE_IMAGE}\nSusan Somerset`). `signoff_closing` stays closing-only. That matches parent "token in cover letter signature content" and AST-1024's `signature` ↔ artifact `signature` spine without a new field.

⚠️ **Decision:** Switch session image source from legacy `profile.cover_letter_signature_image` to `tok["path"]` (`contact.cover_letter_signature_image`). Required by AST-1125; the profile path would silently omit images after the contact migration.

**Self-Assessment:** Single-Component — one core module (`builder.py`) on cover emit helpers and two cover entrypoints' debug lines; no utils/ui/resume edits. Conf high — AST-1125's contract + integration note spell the algorithm; job and session showed the exact auto-above/auto-inject code to delete; `_safe_image_src` is reused. Risk Medium — wrong omit/replace would hide signatures or leave literals in print HTML; the session contact-path switch could blank images if a row still only had profile-era data (mitigated by AST-1014 contact ownership + Betty's AC coverage).

##### Comments

###### hedy — 2026-08-02T18:03:54.706Z
Plan. Single-Component — `src/core/builder.py` only: shared token helpers, job `_emit_cover_signoff_html` stop-prepend + token replace, session stop-auto-inject + token replace, Style D debug on both cover success paths. Conf high; Risk Medium.

###### joan — 2026-08-02T18:05:37.819Z (plan-rubric.v1)
**Overall: APPROVED.** Stage 1 job signoff rewrite + Stage 2 session fragment → AC1 (token position); Stage 1 delete auto-prepend + Stage 2 delete auto-inject → AC4. All in-scope statutes **conforms**. **discuss (non-blocking):** Stage 1 step 4 narrates several HTML wrapper options before settling on the concrete `<p>before</p>{img}<p>after</p>` shape for present+safe — engineer should implement that concrete rule (and the omit/absent variants stated immediately after), not invent a third wrapper; multi-literal signatures are edge-case only.

###### betty — 2026-08-02T18:12:44.558Z
QA manifest AST-1126: token-only signature emit + stop-auto-above coverage in `test_builder.py`. Publish `@ 6570adbd` (`merge-tests(AST-1126): origin/tests f50640e6`).

###### radia — 2026-08-02T18:16:20.585Z (code-rubric.v1)
**Overall: DISCUSS** (C4 stragglers only — no product fix-now). Stages 1–2 match: shared `_lookup_dotted_path` / `_signature_image_token_status` / `_html_with_signature_image_token`; job `_emit_cover_signoff_html` uses the concrete `<p>before</p>{img}<p>after</p>` shape; session stops auto-inject and replaces via the token helper; image source via `tok["path"]`; surfaces + omit-policy guards raise instead of improvising; Style D `signature_image_token` + three-way `signature_image` only under existing `debug=True` gates; resume builders do not call cover render-token helpers. All in-scope statutes **conforms**. **discuss (C4 straggler):** several plan-time-excluded statutes in-scope on the code diff (plan docs + Betty test tree + AST-1125 `config.py` on the tip), all **conform**. No `fix-now`.

#### Resolution (2026-08-02)

fix-now: none. discuss (C4 stragglers): acknowledged — all **conform**, no product patch. Joan's plan-time HTML-shape discuss item was already implemented as `<p>before</p>{img}<p>after</p>` in `_emit_cover_signoff_html`. No product changes on resolve — tip advances to User Testing on the Resolution append only.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/core/builder.py` | Shared SIGNATURE_IMAGE resolve/replace helpers; rewrite job `_emit_cover_signoff_html` (stop auto-prepend); rewrite session signoff emit (stop auto-inject); Style D debug lines on job + session cover success paths | `33d143fda` |
| | _tests_ | token emit + stop auto-above coverage | `f50640e6b` — `test_builder.py` + test-bible (Betty) |
