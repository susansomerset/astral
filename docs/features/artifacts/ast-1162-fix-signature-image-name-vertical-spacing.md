<!-- linear-archive: AST-1162 archived 2026-08-11 -->

## Linear archive (AST-1162)

**Archived:** 2026-08-11  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1162/fix-signature-image-name-vertical-spacing-signature-image-now-overlaps  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** Urgent / —  
**Parent:** AST-1161 — Signature Image now overlaps Name text in signature  
**Blocked by / blocks / related:** parent: AST-1161

### Description

## What this implements

Correct SomersetCover `.signature-img` (and only related signoff spacing if required) so an image above typed name text no longer overlaps or bottom-aligns with that text; same stylesheet covers session and job SomersetCover surfaces. Does **not** own token resolve, profile image storage, or from-block work.

## In scope

- [X] `astral.standards.in-scope-only` — touch only `.signature-img` (and related signoff spacing if still required) inside shared SomersetCover golden CSS in `src/core/builder.py` `_emit_somerset_cover_html_document`
- [X] `astral.standards.no-cross-contamination` — do not pull resume stylesheet, token resolve, profile upload, or unrelated emit paths
- [X] `astral.docs.features-single-file-per-ticket` — one plan doc for this child

## Considered but excluded

- [X] `{$SIGNATURE_IMAGE}` token contract / omit policies / `COVER_LETTER_RENDER_TOKENS` — AST-1125 / AST-1126; consume only
- [X] Candidate profile signature image upload / storage — out of slice
- [X] From-block / to-block / letter body layout — out of slice
- [X] Resume HTML emit (`_emit_html_document`) — out of slice
- [X] Reopen AST-1124 / AST-1123 scope — supersede prior `.signature-img` vertical margin only

## Acceptance criteria

- [X] With signature content shaped like closing + image token + name, rendered cover HTML shows the image above the name with no overlap and no shared bottom alignment of image and name glyphs.
- [X] Session cover letter HTML and job SomersetCover cover HTML that use `.signature-img` both show the corrected stacking.
- [X] Signoff without an image (token absent / image omitted) still renders closing + name text without stray empty image space from this change.
- [X] Archie can verify on a printed/PDF or browser print preview of a real candidate signature image + name line.

## Boundaries

Does **not** change `{$SIGNATURE_IMAGE}` token contract, omit policies, or profile upload. Does **not** redesign from-block / to-block / letter body. Does **not** change resume HTML emit. Does **not** reopen AST-1124 / AST-1123 except to supersede the prior golden `.signature-img` vertical margin that causes overlap under token-below-name signoff.

## Notes for planning

Shared SomersetCover golden CSS — one CSS fix ships both session and job surfaces. Root cause: `.signature-img { margin: 8px 0 -25px 0 }` (negative bottom margin). Shipped: `margin: 8px 0 8px 0`.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1161-signature-image-now-overlaps-name-text-in-signature`, child `sub/AST-1161/AST-1162-fix-signature-image-name-vertical-spacing`. Created at dispatch-parent.

### Comments

#### radia — 2026-08-03T07:06:24.092Z
[code-rubric] revision=1

**Rubric:** code-rubric.v1
**Ticket:** AST-1162
**Publish ref:** `581f39b8a99e1e960827d8c8126c1dd3e7c1b574`
**Overall:** CLEAN

**Full-set sweep:** all 64 active statutes scored in-session (22 universal, 42 scoped). Zero `violates`, zero `needs-discussion`. Scoped statutes outside `src/core/**` / `docs/features/**` / test-tree paths (`ui/**`, `data/**`, `dispatcher.py`, `config.py`, seed/agent-table paths, spikes/artifacts-dir) are `not-applicable`. No Joan plan-rubric verdict attached — noted, not a block.

## Pattern conformance

none cited (description checkboxes are statute ids already covered by the full sweep, not `canon/patterns/*` ids).

## Plan adherence

- Diff is exactly Stage 1: one `.signature-img` margin literal changed (`8px 0 -25px 0` → `8px 0 8px 0`) in `_emit_somerset_cover_html_document`; no markup/token/from-block/resume drift.
- Self-Assessment (Single-Component / high / low) holds — shared helper edit covers both session and job SomersetCover surfaces with one line.
- Per-commit boundaries clean: `code(AST-1162)` touches only `src/core/builder.py`; `test(AST-1162)` touches only `tests/` + `docs/test-bible/`; `merge-tests(AST-1162)` is the sole test-corpus merge onto the sub. No engineer→test-tree or Betty→src/features crossover.

**What's solid:** New margin value keeps the same literal-px convention already used throughout this embedded stylesheet (`.letterdate`, `.lettersubject`, etc.) — not a new hardcoded-set pattern. New test class asserts non-negative margin, DOM stacking order, and the no-image path stays unaffected.

**Notes:** Local pytest re-run blocked in this shell (no Python 3.10+ available); relying on Betty's `merge-tests(AST-1162)` SHA and the Tests Passed gate for green confirmation.

## Frame diff

(none)

context_tokens≈14000
— Radia

#### betty — 2026-08-03T06:59:13.640Z
## QA test manifest

`origin/sub/AST-1161/AST-1162-fix-signature-image-name-vertical-spacing` @ `581f39b8` (`merge-tests(AST-1162): origin/tests 9abc1c8ddca66bcc5ab183ca1cece20c6604ea05`)

1. **Existing coverage** — token placement / omit / selector presence (still apply; not rewritten):
   - `tests/component/core/test_builder.py::TestAst1024BuildSessionCoverLetter::test_token_replaces_with_contact_image`
   - `tests/component/core/test_builder.py::TestAst1024BuildSessionCoverLetter::test_no_image_without_token_even_with_contact_image`
   - `tests/component/core/test_builder.py::TestAst1024BuildSessionCoverLetter::test_name_only_when_contact_image_absent_or_rejected`
2. **Broken / obsolete** — none (prior suites never asserted `-25px`).
3. **Gaps (new this pass)** — `TestAst1162SignatureImgVerticalSpacing`:
   - `…::test_session_signature_img_margin_non_negative` — session CSS `margin: 8px 0 8px 0`, no `-25px`, closing → img → name order
   - `…::test_job_somerset_signature_img_margin_non_negative` — job SomersetCover shares the same rule
   - `…::test_session_no_image_keeps_closing_and_name` — no empty `<img>` when token absent

**Integration:** none to revise.

**Run:**
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_builder.py::TestAst1162SignatureImgVerticalSpacing \
  tests/component/core/test_builder.py::TestAst1024BuildSessionCoverLetter::test_token_replaces_with_contact_image \
  tests/component/core/test_builder.py::TestAst1024BuildSessionCoverLetter::test_no_image_without_token_even_with_contact_image \
  -q
```

**Bible:** `docs/test-bible/core/builder.md` shasum `b30b3751bf4d52c8c5c78d4aa3cb325c7f0de19c`

— Betty

#### joan — 2026-08-03T06:52:28.906Z
[plan-rubric] revision=1

**Rubric:** plan-rubric.v1
**Ticket:** AST-1162
**Overall:** APPROVED
**Publish ref tip:** `origin/sub/AST-1161/AST-1162-fix-signature-image-name-vertical-spacing` @ `78be3c61`

## Traceability

AC1→S1 (steps 1–2, 5); AC2→S1 (step 4, shared `_emit_somerset_cover_html_document`); AC3→S1 (step 3 + Done-when); AC4→S1 (step 5 + UAT Decision). No unmapped AC, no orphan stage; S1 maps to parent Purpose + Functional scope bullets 1–3.

**Considered:** full active corpus swept (18 universal + 25 scoped considered, 22 scoped excluded on layer/path predicates); all considered statutes score `conforms`. Recorded in-session per R7.

## Findings

- `acceptable` — Stage 1 step 5 contingency (`adjust only .letterSignoff / .signature-img spacing in this same helper`). Read against `orch.pipeline.plan-is-bible` this is a pre-authorized, bounded branch rather than improvisation: it names the two selectors, forbids markup/token changes, and stops-and-comments if a non-CSS fix appears necessary. Engineer must not treat it as license to pixel-tune — the Decision note already reserves exact gap for Archie UAT (`orch.pipeline.call-susan-for-product-decisions`).
- `acceptable` — Removing `margin-bottom: -25px` makes the signoff block ~25px taller, so print pagination shifts slightly. That is inherent to the AC ("clear gap") and is Archie-visible at UAT, not a plan defect.

## Verification notes

- Root cause claim confirmed in tree: `src/core/builder.py` golden CSS `.signature-img { display: block; height: 61px; margin: 8px 0 -25px 0; }`. With `display: block`, the negative bottom margin pulls the following anonymous text block up into the 61px image — this is the overlap / apparent bottom-alignment. A non-negative bottom margin resolves it without new layout machinery.
- AC2 confirmed structurally: `build_session_cover_letter` and the job SomersetCover path both call `_emit_somerset_cover_html_document`; `.signature-img` appears exactly once in `src/`, so one edit ships both surfaces and there is no DRY duplication risk.
- AC3 confirmed: `img_html` is emitted only when `token_status == "present"` and a safe src exists, so the no-image signoff never renders the element the rule targets.
- `@media print` does not override `.signature-img`, so the corrected gap holds in print preview / PDF.
- The other signoff emitter (`_emit_cover_signoff_html`) uses inline `max-width` styling and does not use `.signature-img`. Parent Boundaries explicitly permit leaving non-SomersetCover img families alone, so its absence from the plan is correct, not an omission.
- Self-assessment (`Single-Component` / `high` / `low`) is honest and specifically justified against the literal declaration in tree.

context_tokens≈62000

— Joan

#### ada — 2026-08-03T06:48:48.174Z
Plan published on `origin/sub/AST-1161/AST-1162-fix-signature-image-name-vertical-spacing` @ `78be3c61`.

https://github.com/susansomerset/astral/blob/sub/AST-1161/AST-1162-fix-signature-image-name-vertical-spacing/docs/features/artifacts/ast-1162-fix-signature-image-name-vertical-spacing.md

**Scope:** Single-Component — one embedded CSS rule in `src/core/builder.py` SomersetCover helper; session + job cover surfaces inherit via shared emit.

**Conf:** high — overlap is explained by the literal negative bottom margin (`margin: 8px 0 -25px 0`) already in tree; fix is a one-declaration supersede.

**Risk:** low — scoped to `.signature-img` spacing; no-image omit paths do not emit the img; wrong margin only regresses signoff gap (Archie-visible).

---

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

## Radia review

[code-rubric] revision=1

**Rubric:** code-rubric.v1
**Ticket:** AST-1162
**Publish ref:** `581f39b8a99e1e960827d8c8126c1dd3e7c1b574`
**Overall:** CLEAN

**Full-set sweep:** all 64 active statutes scored in-session (22 universal, 42 scoped). Zero `violates`, zero `needs-discussion`. Scoped statutes outside `src/core/**` / `docs/features/**` / test-tree paths (`ui/**`, `data/**`, `dispatcher.py`, `config.py`, seed/agent-table paths, spikes/artifacts-dir) are `not-applicable`. No Joan plan-rubric verdict attached — noted, not a block.

**Pattern conformance:** none cited (description checkboxes are statute ids already covered by the full sweep, not `canon/patterns/*` ids).

**Plan adherence:**
- Diff is exactly Stage 1: one `.signature-img` margin literal changed (`8px 0 -25px 0` → `8px 0 8px 0`) in `_emit_somerset_cover_html_document`; no markup/token/from-block/resume drift.
- Self-Assessment (Single-Component / high / low) holds — shared helper edit covers both session and job SomersetCover surfaces with one line.
- Per-commit boundaries clean: `code(AST-1162)` touches only `src/core/builder.py`; `test(AST-1162)` touches only `tests/` + `docs/test-bible/`; `merge-tests(AST-1162)` is the sole test-corpus merge onto the sub. No engineer→test-tree or Betty→src/features crossover (orch.roles.pre-commit-path-bans, orch.roles.betty-owns-test-tree conform).

**What's solid:** New margin value keeps the same literal-px convention already used throughout this embedded stylesheet (`.letterdate`, `.lettersubject`, etc.) — not a new hardcoded-set pattern. New test class asserts non-negative margin, DOM stacking order, and the no-image path stays unaffected.

**Notes:** Local pytest re-run blocked in this shell (no Python 3.10+ available); relying on Betty's `merge-tests(AST-1162)` SHA and the Tests Passed gate for green confirmation.

## Frame diff

(none)

context_tokens≈14000
— Radia

## Resolution

**Date:** 2026-08-03  
**Review tip:** `732f01c2` (`docs(AST-1162): Radia review — clean; full sweep zero findings`)  
**Outcome:** clean — no fix-now / discuss / advisory product changes.

Radia Overall CLEAN; Frame diff none. Product remains Stage 1 margin supersede (`ab131524`); Betty tests + bible via `merge-tests(AST-1162)` @ `581f39b8`. No code or test-tree edits this resolve pass.
