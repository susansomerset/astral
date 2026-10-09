# AST-1904 — Keep full saved contact line on resume render (Candidate Contact Detail is truncated after email)

<!-- linear-archive: AST-1904 archived 2026-10-08 -->

## Linear archive (AST-1904)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1904/keep-full-saved-contact-line-on-resume-render-candidate-contact-detail  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** None / 2  
**Parent:** AST-1902 — Candidate Contact Detail is truncated after email  
**Blocked by / blocks / related:** parent: AST-1902; blocks: AST-1905

### Description

## What this implements

Stop the resume builder from replacing a complete saved `candidate_contact_detail` with a shorter line rebuilt from the candidate's `contact` library blob. Today `_apply_contact_to_render_dict` in `src/core/builder.py` (introduced by AST-1014) overwrites `render["candidate_contact_detail"]` whenever at least one blob field is non-empty. So a `job_resume` saved as `hire@susansomerset.com • 415-745-5238 • linkedin.com/in/susansomerset • California, USA (PST)` renders as `<div class="contact"><span>hire@susansomerset.com</span></div>`.

## Scope

### Component scope

`src/core/builder.py` — modified. `_apply_contact_to_render_dict` is where the saved contact line gets overwritten. Its callers `build_resume_from_job` and `build_base_resume` are in the same file.
`src/utils/config.py` — possibly modified, only if option (b) needs a config-declared contact-part order or precedence flag instead of the hard-coded field list.
`tests/component/core/test_builder.py` — modified, through Betty (test tree): extend `TestAst1014BuilderContact` with the partial-blob regression.

### Technical scope

`src/core/builder.py`: modify the `_apply_contact_to_render_dict` function so it no longer unconditionally replaces a non-empty `render["candidate_contact_detail"]` with a string built from fewer parts. Either keep the artifact value when present (a), or merge blob parts with the saved value (b). This is the single point where the header contact line is decided for both job and base resume renders.
`src/utils/config.py` (option b only): possibly a new config field declaring contact-part order/precedence, so the builder isn't hard-coding which blob keys make up the line (config-source-of-truth).
`tests/component/core/test_builder.py`: a new test in the existing AST-1014 builder-contact class, locking the regression.

## Acceptance criteria

1. With a saved `candidate_contact_detail` of email • phone • LinkedIn • location and a contact blob holding only the email, the rendered resume header `.contact` span shows the full saved line, not just the email.
2. A partially filled contact blob never silently replaces a more complete saved `candidate_contact_detail`, for both `build_resume_from_job` and `build_base_resume`.
3. When the saved artifact has no `candidate_contact_detail`, the header still falls back to the line built from the contact blob (existing AST-1014 behavior).

## Boundaries

Does not change the contact library schema, the Profile/contact UI, the `.contact` CSS, or the paste-page path (`build_resume_from_paste` already skips `_apply_contact_to_render_dict`). Does not change how `draft_job_resume` produces `candidate_contact_detail`.

## Notes for planning

Ancestor checked by Susan: AST-1014 (contact/context/artifacts library). That ticket is gone from Linear, but its doc is at `docs/features/candidate/ast-1014-contact-context-artifacts-library.md`; plan step 8 is where the blob-overwrites-render behavior came from. **Open product call:** bug-find offered (a) "saved artifact wins, blob is fallback" vs (b) "blob stays authoritative but never emits fewer parts than the saved line", and Susan approved without picking one. Pick the option that satisfies AC 1–3 with the smaller change and say why in the plan. If the choice really needs Susan, stop at Plan Discuss. Full as-is/to-be is in the mini-parent AST-1902 Description.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1902-candidate-contact-detail-truncated`, child `sub/AST-1902/<child-segment>`. Created at bug-fix dispatch.

### Comments

#### radia — 2026-09-30T23:38:51.667Z
[code-rubric] PROCEED (Commit: 7479f320a) saved line wins guard

#### ada — 2026-09-30T23:37:14.753Z
`origin/sub/AST-1902/AST-1904-keep-full-saved-contact-line` @ `7479f320a` · lighter check (no qa-fix manifest; test work split to AST-1905)

- `python3 -m py_compile src/core/builder.py` — OK
- `./scripts/testing/run_component_tests.sh tests/component/core/test_builder.py` (ASTRAL_PYTHON = 3.14 venv)
  - ftr baseline (`origin/ftr/AST-1902-candidate-contact-detail-truncated` builder.py): 190 passed
  - AST-1904 tip: 188 passed, 2 failed — both expected, **owned by AST-1905** (fixture `_resume_blob()` saves `candidate_contact_detail`, so the saved line now wins over the blob per the plan):
    - `TestBuilderHelpers::test_applies_profile_contact_and_markers` (L366 `"555"`)
    - `TestBuilderHelpers::test_profile_uses_reply_email_and_skips_empty_name` (L382 `"reply@example.com"`)
- No other new failures vs ftr. No product changes this pass.

#### joan — 2026-09-30T23:34:31.798Z
[board-joan]  CANON: OK

Overlap skim (no `docs/canon-index.md` on publish ref; `canon/docs/DIRECTIVES-DIRECTORY.md` + `canon/statutes/**` on tip): `src/core/builder.py` `_apply_contact_to_render_dict` only. Frozen Canon Scope on AST-1902 / AST-1904: none cited (mini-parent bug; triage via roster overlap, not R1–R7).

`astral.config.config-source-of-truth` / `patt.config.block`: plan keeps join order and `CANDIDATE_LIBRARY_CONFIG` untouched; early-return when a non-empty saved `candidate_contact_detail` is present does not add literals or move precedence into `config.py`. Fallback path unchanged (AC3).

`patt.core.logical-scope` (builder): one conditional guard; no layer/import/signature churn. `patt.artifact.parse-validate-persist` / build lifecycle: persisted resume JSON is still emitted HTML-escaped at render; fix stops sparser contact blob from overwriting a richer saved artifact line — no statute requires unconditional blob overwrite.

Option (a) vs (b) and Profile-blob staleness when a saved line exists are product trade-offs already accepted in the AST-1902 / plan-fix patch, not an in-force statute conflict or new architectural precedent (`orch.pipeline.call-susan-for-product-decisions` scope is plan-fix, not F2 canon landing).

No directive id needs amendment or a one-line carve-out for F3.

context_tokens≈12000

#### betty — 2026-09-30T23:34:13.318Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/builder.md § AST-1014 (primary docs/test-bible/core/candidate.md § AST-1014) — broken tests + missing repro — `tests/component/core/test_builder.py::TestBuilderHelpers::test_applies_profile_contact_and_markers` (L366 `"555"`) and `::test_profile_uses_reply_email_and_skips_empty_name` (L382 `reply@example.com`) break under option (a) because `_resume_blob()` saves `candidate_contact_detail: "ada@example.com"`, so they need an empty saved line to keep testing the blob fallback. No test covers the repro: a multi-part saved line must survive a sparser blob (plus the whitespace-only case falling back to the blob) → new regression test in `TestAst1014BuilderContact`. No other resume-render tests assert a blob-built contact line over a saved one. The cover from-block tests (`TestAst1139…`, `TestAst1148…`) do not use this helper.

#### ada — 2026-09-30T23:32:48.505Z
`origin/sub/AST-1902/AST-1904-keep-full-saved-contact-line` @ `7ea5d3c53` · saved line wins (option a)

---

_Implementation detail may live in git history on `origin/dev`._
