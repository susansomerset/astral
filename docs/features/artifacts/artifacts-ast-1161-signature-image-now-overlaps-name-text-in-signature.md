# AST-1161 — Signature Image now overlaps Name text in signature
**Component:** artifacts  
**Children:** AST-1162, AST-1165  
**Linear archived:** AST-1161 2026-08-11; AST-1162 2026-08-11; AST-1165 2026-08-11

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-08-02 23:48 | AST-1162 | docs | `78be3c617` | docs(AST-1162): plan — fix signature image / name vertical spacing |
| 2026-08-02 23:56 | AST-1162 | code | `ab1315248` | code(AST-1162): remove signature-img negative bottom margin |
| 2026-08-02 23:56 | AST-1162 | docs | `dbdc6127a` | docs(AST-1162): review stub — Stage 1 tip |
| 2026-08-02 23:58 | AST-1162 | merge-tests | `581f39b8a` | merge-tests(AST-1162): origin/tests 9abc1c8dd |
| 2026-08-02 23:58 | AST-1162 | test | `9abc1c8dd` | test(AST-1162): SomersetCover signature-img non-negative stack margin |
| 2026-08-03 00:05 | AST-1162 | docs | `732f01c2a` | docs(AST-1162): Radia review — clean; full sweep zero findings |
| 2026-08-03 00:07 | AST-1162 | resolve | `bf9de55a1` | resolve(AST-1162): — clean |
| 2026-08-03 15:43 | AST-1165 | docs | `b14161917` | docs(AST-1165): plan — UAT signoff newline to br |
| 2026-08-03 15:45 | AST-1165 | docs | `50adb90de` | docs(AST-1165): review stub — Stage 1 tip |
| 2026-08-03 15:45 | AST-1165 | code | `75b56978c` | code(AST-1165): signoff newlines to br after escape |
| 2026-08-03 15:47 | AST-1165 | merge-tests | `31ebb768a` | merge-tests(AST-1165): origin/tests d56a7acf6 |
| 2026-08-03 15:47 | AST-1165 | test | `d56a7acf6` | test(AST-1165): SomersetCover signoff newlines to br |
| 2026-08-03 15:50 | AST-1165 | docs | `7603bdcbb` | docs(AST-1165): Radia review — clean; full sweep zero findings |
| 2026-08-03 15:51 | AST-1165 | resolve | `be9495993` | resolve(AST-1165): — clean |
| 2026-08-11 18:14 | AST-1162 | docs | `35ba8cad9` | docs(AST-1162): archive Linear issue content |
| 2026-08-11 18:14 | AST-1165 | docs | `463e8dc8c` | docs(AST-1165): archive Linear issue content |
| 2026-08-11 18:15 | AST-1161 | docs | `a8d5090a1` | docs(AST-1161): archive Linear issue content |

## Epic — AST-1161
_Archived: 2026-08-11 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1161/signature-image-now-overlaps-name-text-in-signature · Status at archive: Archive · Project: Astral Artifacts · Assignee: chuckles · Priority / estimate: Urgent / — · Blocked by / blocks / related: —_

### Purpose

Cover-letter signoff that places a handwritten signature image above the typed name (via `{$SIGNATURE_IMAGE}`) currently draws the image and the name overlapping / bottom-aligned. Operators cannot ship a readable printed cover letter. This epic restores vertical stacking so the image sits above the name with a clear gap, on both session and job SomersetCover surfaces that share the golden stylesheet.

### Functional scope

* When cover HTML signoff content has a signature image followed by name (or other) text, the image and the following text stack in document order without overlapping or sharing a bottom edge.
* The fix applies wherever SomersetCover golden CSS drives `.letterSignoff` / `.signature-img` (session cover letter and job print cover letter that share that stylesheet).
* Closing lines and other signoff text that are not the image remain readable and in the same relative order as the authored signature content.

### Architectural definition

* **Patterns to reuse:** none — this is a print/CSS spacing correction on the existing SomersetCover embedded stylesheet; the catalog has no signoff-layout pattern.
* **New patterns proposed:** none.
* **Applicable statutes:** `astral.standards.in-scope-only` (touch only signoff image spacing / related golden CSS declarations needed for the bug); `astral.standards.no-cross-contamination` (do not pull resume stylesheet or unrelated emit paths); `astral.docs.features-single-file-per-ticket`; `orch.pipeline.call-susan-for-product-decisions` (pixel spacing after remove-overlap is verified by Archie UAT, not inventing a second layout system).

### Boundaries

* Does **not** change `{$SIGNATURE_IMAGE}` token contract, omit policies, or profile upload.
* Does **not** redesign from-block / to-block / letter body layout.
* Does **not** unify job vs session *markup* families beyond the shared SomersetCover CSS already in use; if a non-SomersetCover job path still uses different img attributes, leave it unless it shares this `.signature-img` rule and shows the same overlap.
* Does **not** change resume HTML emit.
* Does **not** reopen AST-1124 / AST-1123 scope except to **supersede** the prior golden `.signature-img` vertical margin that causes overlap under token-below-name signoff.

### Acceptance criteria

* With signature content shaped like closing + image token + name, rendered cover HTML shows the image above the name with no overlap and no shared bottom alignment of image and name glyphs.
* Session cover letter HTML and job SomersetCover cover HTML that use `.signature-img` both show the corrected stacking.
* Signoff without an image (token absent / image omitted) still renders closing + name text without stray empty image space from this change.
* Archie can verify on a printed/PDF or browser print preview of a real candidate signature image + name line.

### Dependencies and blockers

none. Prior signature-token work (AST-1123 / AST-1125 / AST-1126) and SomersetCover golden CSS (AST-1124 / AST-1138 / AST-1139) are Done; this epic corrects spacing those left in place.

### Open questions

none.

### Proposed child tickets

**1: Fix signature image / name vertical spacing — Ada** — Correct SomersetCover `.signature-img` (and only related signoff spacing if required) so an image above typed name text no longer overlaps or bottom-aligns with that text; the same stylesheet covers session and job SomersetCover surfaces. Does **not** own token resolve, profile image storage, or from-block work.
**Citations:** `astral.standards.in-scope-only`, `astral.standards.no-cross-contamination`.

Monolith check: Functional scope has 3 bullets and 1 child — intentional; one inseparable vertical-slice (shared golden CSS) ships both surfaces atomically for UAT.

### Original brief

this content:

```
Best,
{$SIGNATURE_IMAGE}
Susan Somerset
```

Renders like this:

```
<div class="letterSignoff">
        
        <br>
        Best,
<img src="data:image/jpeg;base64,[…candidate's handwritten-signature JPEG, base64-encoded, elided — inert image bytes, not evidence of the bug…]" class="signature-img" alt="Signature">
Susan Somerset
      </div>
```

Where the image and the text `Susan Somerset` are bottom-aligned.

#### Comments

##### susan — 2026-08-03T22:40:25.364Z
Now the signature line doesn't recognize line breaks between name and title:

```
Best, 
{$SIGNATURE_IMAGE}
Susan Somerset
Senior Product Manager
```

```
<div class="letterSignoff">
        
        <br>
        Best, 
<img src="data:image/jpeg;base64,[…same signature JPEG, elided…]" class="signature-img" alt="Signature">
Susan Somerset
Senior Product Manager
      </div>
```

_(This second repro is what became child AST-1165, filed against the fix-uat wave below.)_

##### chuckles — 2026-08-03T22:52:22.280Z
[fix-uat] UAT fixes landed — ready for re-test. **AST-1165** — _signoff loses line breaks between name and title_: authored newlines in the signature field after the image (and in other non-image signoff text segments) should become visible line breaks in rendered cover HTML — e.g. name on one line, title on the next — while keeping the image above that text with no overlap. Local `dev` merged via prep-uat.

### Files changed (plan vs actual)

_No product commit trail on the parent. Implementation landed via AST-1162 (the overlap fix) and AST-1165 (the newline regression it surfaced)._

_Implementation detail may live in git history on `origin/dev`._

## Sub-issues

### AST-1162 — Fix signature image / name vertical spacing
_Archived: 2026-08-11 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1162/fix-signature-image-name-vertical-spacing-signature-image-now-overlaps · Status at archive: Archive · Project: Astral Artifacts · Assignee: ada · Priority / estimate: — · Blocked by / blocks / related: parent: AST-1161_

#### What this implements

SomersetCover signoff that places a handwritten signature image above typed name text (via `{$SIGNATURE_IMAGE}`) currently overlaps / bottom-aligns because the shared golden `.signature-img` rule uses a negative bottom margin. This ticket corrects that one CSS declaration (and only related signoff spacing if still required after the margin fix) so session and job SomersetCover surfaces that share `_emit_somerset_cover_html_document` both stack image above name with a clear gap. Does **not** own token resolve, profile image storage, from-block work, or resume HTML emit.

#### Acceptance criteria

Parent AC (image above name with no overlap/shared bottom edge, on both session and job surfaces; no-image signoff unaffected; Archie-verifiable).

#### Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/builder.py` | In `_emit_somerset_cover_html_document` embedded CSS, supersede `.signature-img` vertical margin so the image no longer overlaps following name text; leave markup / token replace / other selectors unchanged unless Stage 1 verification shows `.letterSignoff` alone still collapses the gap | core |

**Out of scope:** `resolve_tokens` / `{$SIGNATURE_IMAGE}` contract (AST-1125 / AST-1126); candidate profile upload; from-block resolve (AST-1137+); resume `_emit_html_document`; React Admin / Profile UI; `tests/`, bible (Betty).

#### Stage 1: Correct `.signature-img` vertical margin

**Done when:** Embedded SomersetCover CSS in `_emit_somerset_cover_html_document` no longer uses a negative bottom margin on `.signature-img`; closing + image + name signoff HTML keeps document order with a visible gap between image and following name glyphs; signoff without an image still emits closing + name text with no empty `<img>` / no new empty image box from this change.

1. Locate the embedded `.signature-img` rule (`display: block; height: 61px; margin: 8px 0 -25px 0;`).
2. Replace the `margin` declaration with `margin: 8px 0 8px 0;` (non-negative, preserves block stacking); keep `display: block` and `height: 61px` unchanged.
3. Do **not** change `_html_with_signature_image_token`, img markup (`class="signature-img"` / `alt="Signature"`), token present/absent omit policies, `signoff_parts` assembly, `.letterSignoff` rules, from/to/body CSS, or any resume stylesheet in `_emit_html_document`.
4. Do **not** add a second copy of SomersetCover CSS — session `build_session_cover_letter` and job `build_cover_letter_from_job` already share this helper; one edit ships both surfaces.
5. After the margin change, visually confirm (browser open of emitted HTML or print preview) that for signature content shaped like `Best,\n{$SIGNATURE_IMAGE}\nSusan Somerset` the image sits fully above the name with no overlap. If and only if name text still overlaps after step 2, adjust **only** `.letterSignoff` / `.signature-img` spacing declarations in this same helper — still no markup/token changes — and stop to comment on the parent if a non-CSS fix appears necessary.

⚠️ **Decision:** Root cause is the AST-1024 golden `margin-bottom: -25px`, which pulls following name text up into the 61px image under token-below-name signoff. Replacing it with `8px` bottom margin (matching the existing top margin) removes overlap without inventing a new layout system. Exact pixel gap after remove-overlap is Archie UAT (parent AC); do not tune beyond this single positive gap unless step 5 proves insufficient.

⚠️ **Decision:** Supersede the prior golden `.signature-img` vertical margin from AST-1124 / AST-1024 for this bug only — do not reopen those tickets' token, from-block, or DOM scope.

**Self-Assessment:** Single-Component — one embedded CSS rule in `src/core/builder.py`'s SomersetCover helper; session + job cover surfaces inherit via shared emit. Conf high — overlap is explained by the literal negative bottom margin already in tree. Risk low — scoped to `.signature-img` spacing; token omit and no-image paths do not emit the img, so unaffected; wrong margin would only regress the signoff gap (Archie-visible), not pipeline state.

##### Comments

###### ada — 2026-08-03T06:48:48.174Z
Plan @ `78be3c61`. Single-Component — one embedded CSS rule; session + job inherit via shared emit. Conf high; Risk low.

###### joan — 2026-08-03T06:52:28.906Z (plan-rubric.v1)
**Overall: APPROVED.** `acceptable` — Stage 1 step 5's contingency ("adjust only `.letterSignoff` / `.signature-img` spacing in this same helper") is a pre-authorized, bounded branch rather than improvisation under `orch.pipeline.plan-is-bible`: it names the two selectors, forbids markup/token changes, and stops-and-comments if a non-CSS fix appears necessary. Engineer must not treat it as license to pixel-tune — the Decision note already reserves the exact gap for Archie UAT.

###### betty — 2026-08-03T06:59:13.640Z
QA manifest AST-1162: SomersetCover signature-img non-negative stack margin coverage in `test_builder.py`. Publish `@ 581f39b8` (`merge-tests(AST-1162): origin/tests 9abc1c8d`).

###### radia — 2026-08-03T07:06:24.092Z (code-rubric.v1)
**Overall: CLEAN** — full-set sweep, zero findings. Diff is exactly Stage 1: one `.signature-img` margin literal changed (`8px 0 -25px 0` → `8px 0 8px 0`) in `_emit_somerset_cover_html_document`; no markup/token/from-block/resume drift.

#### Resolution (2026-08-03)

Radia Overall CLEAN; Frame diff none. Product remains Stage 1 margin supersede (`ab131524`); Betty tests + bible via `merge-tests(AST-1162)` @ `581f39b8`. No code or test-tree edits this resolve pass.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/core/builder.py` | `.signature-img` margin `8px 0 -25px 0` → `8px 0 8px 0` | `ab1315248` |
| | _tests_ | non-negative stack margin lock | `9abc1c8dd` — `test_builder.py` + test-bible (Betty) |

### AST-1165 — UAT: signoff loses line breaks between name and title
_Archived: 2026-08-11 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1165/uat-signoff-loses-line-breaks-between-name-and-title · Status at archive: Archive · Project: Astral Artifacts · Assignee: ada · Priority / estimate: Urgent / — · Blocked by / blocks / related: parent: AST-1161 · UAT bug_

#### What failed

After the overlap fix (AST-1162), cover signoff with authored newlines between typed name and title collapses those lines onto one visual run (HTML text nodes with no `<br>` between them inside `.letterSignoff`), so the title does not appear on its own line under the name.

#### Expected

Authored newlines in the signature field after the image (and in other non-image signoff text segments) become visible line breaks in rendered cover HTML — e.g. name on one line, title on the next — while keeping the image above that text with no overlap.

#### Repro

1. Open Session Cover Letter (or job Print Cover Letter) for a candidate with a signature image.
2. Set signature content to closing + `{$SIGNATURE_IMAGE}` + name on one line + title on the next line.
3. Emit / preview HTML (or print preview).
4. Observe name and title not stacked as separate lines under the image.

#### Diagnosis / Root cause

**Hypothesis:** SomersetCover signoff builds the signature fragment by HTML-escaping text around `{$SIGNATURE_IMAGE}` but does not turn authored newlines into `<br>` (letter body already does this; signoff does not), so browsers collapse name/title onto one visual line. **Wrong fix to avoid:** `white-space: pre` on all of `.letterSignoff` (fights other layout); inventing separate name/title fields; swallowing the bug by only changing CSS margin again; changing the `SIGNATURE_IMAGE` token contract. **Related:** AST-1162's margin fix must remain; AST-1126's token-at-position emit must still omit the image when token/image is absent.

#### Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/builder.py` | In `_html_with_signature_image_token`, after `html.escape` on signature text segments (token-present join path **and** token-absent full-text path), convert authored newlines to `<br>` the same way letter body does (normalize `\r\n`→`\n`, then `replace(chr(10), "<br>")`). Do not change img markup, token omit, or `.signature-img` CSS | core |

**Out of scope:** `COVER_LETTER_RENDER_TOKENS` / omit policies; profile upload; from-block / letter body paragraph splitting; resume `_emit_cover_signoff_html` / `_emit_html_document` (non-SomersetCover family); React UI; `tests/`, bible (Betty).

#### Stage 1: Newline → `<br>` in SomersetCover signature fragment

**Done when:** Signature content with authored newlines around / after `{$SIGNATURE_IMAGE}` (e.g. image then name line then title line) emits those newlines as `<br>` inside `.letterSignoff`; AST-1162's non-negative `.signature-img` margin still present; token-absent / image-omitted signoff still has no empty `<img>` and still preserves newlines in remaining text.

1. In `_html_with_signature_image_token`, introduce a tiny local helper (or a one-line private helper next to it) that normalizes `\r\n`→`\n` and returns `html.escape(segment).replace(chr(10), "<br>")`.
2. **Token-absent path** (today `return html.escape(signature_text or "")`): return the helper result instead of bare escape.
3. **Token-present path** (today `sep.join(html.escape(part) for part in parts)`): join with `img_html` / `""` as today, but map each `part` through the helper instead of bare `html.escape`.
4. Do **not** change `img_html` assembly / `class="signature-img"`, omit policies / `get_cover_letter_render_token` contract checks, `_emit_somerset_cover_html_document` CSS (keep AST-1162's `margin: 8px 0 8px 0`), the `signoff_parts` assembly that already appends closing + `"<br>"` before the fragment, or `_emit_cover_signoff_html` (resume cover family — out of scope).
5. Smoke-check: for fields shaped like closing `Best,` + signature `{$SIGNATURE_IMAGE}\nSusan Somerset\nSenior Product Manager` with an image src, `.letterSignoff` inner HTML contains the img then `Susan Somerset<br>Senior Product Manager`, and `.signature-img` CSS still has the non-negative bottom margin.

⚠️ **Decision:** Fix in `_html_with_signature_image_token` (shared by session + job SomersetCover) via post-escape newline→`<br>`, mirroring `.lettercontent p` — not CSS `white-space` on `.letterSignoff`. That keeps relative authored order without inventing fields or reopening token/CSS margin scope.

**Self-Assessment:** Single-Component — `_html_with_signature_image_token` in `src/core/builder.py` (shared SomersetCover session + job). Conf high — diagnosis matches code (escape-only join); letter body already has the newline→`<br>` pattern to copy. Risk low — signature fragment only; AST-1162 margin and AST-1126 omit left untouched.

##### Comments

###### ada — 2026-08-03T22:44:05.755Z
Plan @ `b1416191`. Single-Component — `_html_with_signature_image_token` in `builder.py` (shared session + job). Conf high; Risk low.

###### betty — 2026-08-03T22:47:22.009Z
QA manifest AST-1165: `TestAst1165SignoffNewlineToBr` — `Name<br>Title` after img on session and job SomersetCover paths, plus token-absent preserves newlines with no empty `<img>`; sibling `TestAst1162SignatureImgVerticalSpacing` and `TestAst1024BuildSessionCoverLetter::test_token_replaces_with_contact_image` still apply. Publish `@ 31ebb768` (`merge-tests(AST-1165): origin/tests d56a7acf`).

###### radia — 2026-08-03T22:50:51.965Z (code-rubric.v1)
**Overall: CLEAN** — full-set sweep (65 active statutes, 22 universal + 43 scoped), zero findings. Diff is exactly Stage 1: local `_esc_br` helper added inside `_html_with_signature_image_token`, used on both the token-present join path and the token-absent full-text path — no img markup / omit-policy / `.signature-img` CSS changes. `_esc_br` is DRY with the module's existing `\r\n`→`\n` normalization + escape-then-`<br>` pattern already used verbatim for letter-body paragraphs and `from_block`/`to_block` — not a new hardcoded literal, mirrors established precedent in the same file. Sibling checks hold: AST-1162's margin untouched (new test asserts `-25px` absent); AST-1126's token-absent/omit path still emits no `<img>`.

#### Resolution (2026-08-03)

Radia Overall CLEAN; Frame diff none. Product remains Stage 1 `_esc_br` in `_html_with_signature_image_token` (`75b56978`); Betty tests + bible via `merge-tests(AST-1165)` @ `31ebb768`. No code or test-tree edits this resolve pass.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/core/builder.py` | `_html_with_signature_image_token` — newline→`<br>` after escape on both join paths | `75b56978c` |
| | _tests_ | signoff newline→`<br>` coverage (session + job, token-absent) | `d56a7acf6` — `test_builder.py` + test-bible (Betty) |
