# AST-1483 — Resume page break settings don't work
**Component:** artifacts  
**Children:** AST-1487, AST-1489, AST-1490  
**Linear archived:** AST-1483 2026-09-09; AST-1487 2026-09-09; AST-1489 2026-09-09; AST-1490 2026-09-09

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-08-25 21:51 | AST-1487 | docs | `a510ed3f2` | plan-fix — restore builder print CSS regression |
| 2026-08-25 21:58 | AST-1487 | test | `f3aed2648` | bug-repro — restore AST-1475 page-break print CSS coverage |
| 2026-08-25 21:59 | AST-1487 | merge-tests | `4092da2ee` | origin/tests f3aed264 |
| 2026-08-25 22:01 | AST-1487 | code | `f2d3a0d00` | restore structure page-break print CSS mapping |
| 2026-08-25 22:06 | AST-1487 | docs | `e8e229a7a` | Radia review — clean proceed |
| 2026-08-26 11:07 | AST-1489 | docs | `d06191896` | plan-fix — auto-save structure before Print Resume |
| 2026-08-26 11:20 | AST-1489 | test | `4f45f24d8`/`c1776c654` | bug-repro — print-before-PUT page-break auto-persist |
| 2026-08-26 11:24 | AST-1489 | code | `dcc93b885` | auto-persist structure rows before Print Resume |
| 2026-08-26 11:27 | AST-1489 | docs | `b4e4bb08a` | Radia review — clean proceed |
| 2026-08-26 11:28 | AST-1489 | merge-tests | `0ac4574b3` | origin/tests 4f45f24d |
| 2026-08-26 11:30 | AST-1490 | docs | `529f2bd5d` | plan-fix — order-insensitive fixedFieldKeys for reorder |
| 2026-08-26 11:33 | AST-1490 | test | `64fc383db`/`7c630a753` | bug-repro — reorder+Print full body, no re-GET guard |
| 2026-08-26 11:35 | AST-1490 | code | `20d4b7e3a` | order-insensitive fixedFieldKeys; stable job load deps |
| 2026-08-26 11:39 | AST-1490 | docs | `47ac98ccd` | Radia review — clean proceed |
| 2026-08-26 11:39 | AST-1490 | merge-tests | `f9301ccb0` | origin/tests 7c630a75 |
| 2026-08-26 11:40 | AST-1483 | merge | `279126b21` | Merge origin/ftr/AST-1483-resume-page-break-settings-dont-work into dev |
| 2026-09-09 17:57 | AST-1487 | docs | `1886ccf59` | archive Linear issue content |
| 2026-09-09 17:58 | AST-1489 | docs | `699be68e8` | archive Linear issue content |
| 2026-09-09 17:58 | AST-1490 | docs | `e0db69d73` | archive Linear issue content |
| 2026-09-09 18:06 | AST-1483 | docs | `2cd03e418` | archive Linear issue content |

_This family is the immediate aftermath of the AST-1462 page-break epic ([[artifacts-ast-1462-create-and-position-page-break]]): three successive bugs, each closing a gap the previous one uncovered. AST-1487 restores a builder regression (AST-1475's emit logic never survived onto `origin/dev` — see that archive's AST-1476 section for how the sync regression happened). AST-1489 then found the deeper design gap the restore exposed: Print Resume only ever reflected **saved** structure, never live/unsaved dropdown edits — Susan explicitly widened scope to UI (Option 1) to fix it. AST-1490, filed by Susan in the same bug report as AST-1489, is unrelated in cause (a structure-reorder re-GET race, not a page-break issue) but shares the parent. None of AST-1487/1489/1490's rich build narrative lived in their own thin ticket docs — each was embedded as a `## Bug: AST-NNNN` section inside a sibling ancestor ticket's doc from the AST-1462 epic (AST-1487 in `ast-1475-...md`, AST-1489 in `ast-1476-...md`) or a distant AST-1459 family doc (AST-1490 in `ast-1480-...md`, part of [[artifacts-ast-1459-resume-editor-is-not-working-properly]]); that richer content is reproduced here, sourced and cited to its host doc, per this session's embedded-bug convention."_

## Epic — AST-1483
_Archived: 2026-09-09 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1483/resume-page-break-settings-dont-work · Status at archive: Archive · Project: Astral Artifacts · Assignee: chuckles · Priority / estimate: High / — · Blocked by / blocks / related: —_

### Report (Susan)

When everything is set to "Keep block together", there is still a page break above the Prior Experience section. When I add "New Page Before" to the section Education and Certifications, it does not page break as expected.

### As-is

Structure authoring exposes per-section page-break policies (`Keep block together` / `New page before` / `Flow uninterrupted`). After AST-1487, builder emit honors **persisted** `page_break_policy`, but Base/JAR Print Resume always rebuilds from saved structure via `GET /candidate/resume/...` — unsaved page-break dropdown edits in the structure editor never reach print, so operators still see "settings ignored" when they Print without Save sections first.

### To-be

Print Resume reflects the operator's current page-break choices when they click Print (auto-save structure before print, or print from live structure rows), including Keep block together and New page before on Education and Certifications / Prior Experience. Experience `.role` chunks still always stay together. Builder emit for already-saved policies remains correct (AST-1487).

### Proposed steps

1. Keep AST-1487 builder mapping as landed (no re-do of emit).
2. On Base + JAR Print Resume, either auto-persist structure (including `page_break_policy`) before the resume GET/build, or pass live structure rows into the print path so unsaved dropdown changes affect the printed HTML.
3. Optionally surface that Print uses the structure about to be printed (saved or live) so operators are not surprised.
4. Cover with frontend tests for Print after page-break change without a separate Save click (Betty).

### Component scope

* `src/core/builder.py` — **modified** (AST-1487 done) — structure→print page-break CSS helper; hard-coded Prior Experience always-break removed.
* `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx` — **modified** — Print Resume path must apply current structure page-break policies (auto-save before print and/or print from live `structureRows`), not only a prior DB snapshot after an explicit Save.
* `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` — **modified** — same Print Resume behavior for JAR Job Resume structure authoring.
* `src/ui/frontend/src/components/ArtifactEditor.tsx` — **modified** only if shared print/structure helpers need to expose live `page_break_policy` rows to the Print path.
* `tests/component/core/test_builder.py` — **modified** (Betty, AST-1487) — page-break print CSS coverage.
* `docs/test-bible/core/builder.md` — **modified** (Betty, AST-1487).
* Frontend component/page tests + bible rows (Betty) — Print after page-break edit without separate Save.

### Technical scope

* `src/core/builder.py` — `_print_section_page_break_css` + `_emit_html_document` print injection (AST-1487) — leave as landed unless Print gains a new structure payload shape.
* `ArtifactsBaseResumeContent.tsx` — modified function `handlePrint` (or equivalent): before `GET /candidate/resume/base`, persist current structure including `page_break_policy`, or supply live structure to the build path so print matches the editor.
* `JobAnalysisReportModal.tsx` — modified function Print Resume handler: same persist-or-live-structure behavior for job resume print.
* `ArtifactEditor.tsx` — modified only if needed to share live structure rows / save helper with Print callers.
* No new config tokens expected — AST-1474/1476 catalog and dropdown remain.

### Ancestor candidates

- [X] AST-1475 — Builder print CSS from structure page-break policies (Done child of AST-1462; landed the mapping that tip is missing after a later merge-resume)
- [ ] AST-1462 — Create and position page break (Done parent epic for operator page-break control)
- [ ] AST-1476 — Structure editor page-break dropdown on base and job (Done UI/persist slice; merge-resume onto this line reintroduced the golden hard-coded prior break)
- [ ] AST-1474 — Page-break policy config and resume_structure schema (Done catalog/normalize; still present on tip — weaker fit unless schema/default drift is found)

#### Comments

##### susan — 2026-08-26T14:44:21.354Z
[bug]

Still isn't working. It is rendering on the fly, correct? A change to the text or a change to the page break setting is incorporated every time I click "Print Resume", right?

Separate bug, if I move a section up or down, the print render only includes the contact information and no other content appears.

##### chuckles — 2026-08-26T14:50:43.580Z
Yes — Print Resume builds HTML from the candidate's current saved `base_resume` content and `resume_structure` (including each section's page-break policy) at click time. A text or page-break change only shows up after that change is saved; then the next Print Resume should pick it up.

Filed from your [bug] comment:
- AST-1489 — page-break settings still ignored
- AST-1490 — Print Resume only contact after section reorder

Both at Discussion assigned to you for diagnosis confirm before the fix lane runs.

### Files changed (plan vs actual)

_No direct product commit trail on the parent beyond the dev-merge of the `ftr/AST-1483-…` epic branch (`279126b21`) and the archive-docs commit. Implementation landed via the three sub-issues below._

## Sub-issues

### AST-1487 — Restore builder page-break print CSS from structure
_Archived: 2026-09-09 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1487/restore-builder-page-break-print-css-from-structure · Status at archive: Archive · Project: Astral Artifacts · Assignee: hedy · Priority / estimate: None / 3 · Blocked by / blocks / related: parent: AST-1483_

#### What this implements (own ticket doc)

Restore builder print CSS mapping from `artifacts.resume_structure.sections[*].page_break_policy` so operator page-break settings affect printed base and job resumes. Regression fix for AST-1462 / AST-1475 work dropped from `origin/dev` tip. Does not change config catalog, API, or React structure editor.

**Notes for planning:** Ancestor context AST-1475 (Done); prior implementation commit `7fb201ea`. Susan symptom: all `Keep block together` still forces break before Prior Experience; `New page before` on Education and Certifications has no effect. Board: Joan `[board-joan] CANON: OK`; Betty `[board-betty] TESTS: REVISE` — "no AST-1475 page-break coverage; `TestAst1020GoldenStylesheet` breaks — restore `TestAst1475PageBreakPrintCss` + flip AST-1020 prior-break assert." Orphaned handling: "parent Done, no origin/ftr — lands straight to dev after review-fix clears, not via merge-child/prep-uat."

#### As-is / To-be / Repro _(embedded build narrative, sourced from `ast-1475-builder-print-css-structure-page-break-policies.md` § "Bug: AST-1487")_

**As-is:** `origin/dev` tip embeds `@media print { #prior-experience { page-break-before: always; } }` unconditionally in `_emit_html_document` and has no `_print_section_page_break_css`. Operator page-break policies persist on `artifacts.resume_structure.sections[*].page_break_policy` (AST-1474/1476 on dev) but print HTML ignores them: all-`avoid_split` still forces a new page before Prior Experience; `page_break_before` on Education & Certifications (`education_certifications` → `#education`) emits no break.

**To-be:** Same as AST-1475 Stage 1 (already shipped on `sub/AST-1462/AST-1475-…` @ `7fb201ea`): resume print CSS derives from structure `page_break_policy` on every enabled body section; hard-coded prior always-break removed; `.role { page-break-inside: avoid; }` stays mandatory.

**Repro:**
1. On dev tip, call `build_session_base_resume(candidate_mod.default_resume_structure(), blob)` where `blob` includes non-empty `prior_experience` and `education_certifications` strings (minimal fixture from `TestAst1475PageBreakPrintCss._blob()` plus `"education_certifications": "MBA — Example U"`).
2. Inspect embedded `<style>`: `#prior-experience { page-break-before: always; }` is present even though every section policy is default `avoid_split`.
3. Set `structure["sections"]["education_certifications"]["page_break_policy"] = "page_break_before"`, re-emit: `#education { page-break-before: always; }` is absent.

#### Root cause

AST-1475 product commit `7fb201ea` landed and passed review on `sub/AST-1462/AST-1475-builder-print-css-structure-page-break-policies` but never merged into `origin/dev`'s first-parent line for `src/core/builder.py`. Dev absorbed AST-1474 config/catalog and AST-1476 UI persistence; the builder emit half regressed to AST-1020's golden hard-coded `#prior-experience` always-break — this is the AST-1476 sync-regression fallout documented in [[artifacts-ast-1462-create-and-position-page-break]] (the repair commit `9b0f01212` restored 17 other regressed files but never touched `builder.py`). `TestAst1475PageBreakPrintCss` and the revised `TestAst1020GoldenStylesheet` assertion from `f32da268` were also absent on dev tip.

#### Proposed change (as built)

**Product (`src/core/builder.py`):**
1. Extend the existing `src.utils.config` import block with `RESUME_STRUCTURE_PAGE_BREAK_POLICIES` and `RESUME_STRUCTURE_PAGE_BREAK_POLICY_DEFAULT` (constants already on dev).
2. Re-add `_print_section_page_break_css(resume_structure: Optional[dict]) -> str` immediately above `_emit_html_document`, matching AST-1475 Stage 1 / commit `7fb201ea`: docstring cites `pattern.artifacts.resume-section-print-policy`; non-dict structure → empty string; for each `sid` in `_structure_ordered_body_ids(resume_structure)`, read `sections[sid].page_break_policy`, soft-default invalid/missing to the config default, map via `_html_section_dom_id(sid)` (`page_break_before` → `page-break-before: always;`, `avoid_split` → `page-break-inside: avoid;`, `normal` → nothing).
3. In `_emit_html_document`'s `@media print` f-string: delete `#prior-experience {{ page-break-before: always; }}`; insert `{_print_section_page_break_css(resume_structure)}` after `#competencies` and before `.role`; keep `body`, `h2`, `#competencies`, `.role`, `p, li` lines unchanged.
4. Update the stale comment claiming an unconditional golden prior-experience break.
5. No changes to cover-letter print CSS, config, API, React, or caller threading.

**Tests (Betty):** Restored `TestAst1475PageBreakPrintCss` (three tests: default avoid_split + no forced prior; explicit `page_break_before`/`normal`; missing-policy soft-default + job path); revised `TestAst1020GoldenStylesheet._assert_golden_style` to assert **absence** of the unconditional prior break; updated `docs/test-bible/core/builder.md` manifest.

#### Blast radius / what must still hold

Shared emit path `_emit_html_document` feeds base, session-base, and job resume HTML — all three pick up the fix via existing `resume_structure=` threading. AST-1020 golden stylesheet tests flip to require the prior break be **absent** by default. AST-1476 plan referenced AST-1475 print mapping as prerequisite — no React/config changes needed. Binding decisions carried forward unchanged: token mapping table; soft-default to config default; rules only for `_structure_ordered_body_ids`; mandatory `.role` avoid; keep `h2`/`#competencies` golden companions; no `BUILD_CONFIG["supported_sections"][*]["page_break_policy"]` reads; cover-letter print CSS untouched; body HTML emit order and DOM ids unchanged.

#### Review

Radia review-fix @ `f2d3a0d0` — CLEAN, PROCEED. §3h shortcut: no resolve-child; structure print CSS restore matches plan-fix patch; [bug-repro] substantive.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/core/builder.py` | Restore `_print_section_page_break_css` + `_emit_html_document` injection; drop hard-coded prior-experience break | `f2d3a0d00` — +26/-3 |
| | _tests_ | Restore `TestAst1475PageBreakPrintCss`; flip `TestAst1020GoldenStylesheet` prior-break assertion; bible manifest | `f3aed2648` — 125 insertions/4 deletions across `test_builder.py` + `docs/test-bible/core/builder.md` |

### AST-1489 — Page break settings still ignored on Print Resume
_Archived: 2026-09-09 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1489/page-break-settings-still-ignored-on-print-resume · Status at archive: Archive · Project: Astral Artifacts · Assignee: hedy · Priority / estimate: None / — · Blocked by / blocks / related: parent: AST-1483_

#### Susan's report (verbatim, filed as this ticket's Description)

Still isn't working. It is rendering on the fly, correct? A change to the text or a change to the page break setting is incorporated every time I click "Print Resume", right?

#### As-is / To-be (own ticket doc)

**As-is:** After AST-1487, builder emit honors **saved** `page_break_policy`, but Base/JAR Print Resume always `GET`s persisted structure and ignores unsaved page-break dropdown edits in the structure editor — so Print still looks like settings "don't work" unless Save sections ran first.

**To-be:** Clicking Print Resume applies the operator's current page-break dropdown choices (Keep block together / New page before / Flow uninterrupted), including when they have not clicked Save sections since the last edit — via auto-save before print and/or printing from live structure rows. **Susan approved widen-to-UI (Option 1) on 2026-08-26.**

#### Scope-gate escalation (Susan's product direction — kept in full per the never-skip rule)

##### hedy — 2026-08-26T15:49:50.802Z
[scope-gate]

After AST-1487, `_print_section_page_break_css` on tip maps saved `page_break_policy` correctly (verified: `build_base_resume` / session emit — no hard `#prior-experience` always-break; `page_break_before` on `education_certifications` → `#education { page-break-before: always; }`).

Residual UAT failure is the Print wire path, not emit:

- Base Print (`ArtifactsBaseResumeContent.handlePrint`) always `GET /candidate/resume/base` → `build_base_resume` → **persisted** `artifacts.resume_structure` only (comment in code: "not editor buffer").
- JAR Print Resume same pattern: `GET /candidate/resume/<job_id>` → candidate structure from DB.
- Page-break dropdown edits live in `structureRows` until **Save sections** (or content Save with structure authoring). Unsaved policy changes never reach `_print_section_page_break_css`.
- Susan's question on the parent ("rendering on the fly… every time I click Print Resume?") matches this gap.

**Proposed fix kind (needs scope amend):** frontend — e.g. auto-save structure before Print, or print from live `structureRows` (session-style), and/or clear operator signal that Print uses saved structure only. Possibly touch `ArtifactsBaseResumeContent.tsx` / `JobAnalysisReportModal.tsx` (and only builder if a new print payload is required).

**Parent AST-1483 scope that does not cover this:**

> Component: `src/core/builder.py` — restore structure→print page-break CSS helper…
> Technical: `_print_section_page_break_css` + `_emit_html_document` print-block injection only.
> "No config/API/UI changes expected"

Cannot Plan Ready a builder-only re-do of AST-1487 — emit already honors **saved** policies. Need Component/Technical scope widened to the Print/structure-authoring UI (or Chuckles/Archie confirm operator-must-Save is intended and this bug should close as works-as-designed).

##### chuckles — 2026-08-26T16:00:36.836Z
@susan — scope gate on AST-1489 (Hedy plan-fix).

AST-1487 emit is correct for **saved** `page_break_policy`. Print Resume always builds from persisted structure (`GET /candidate/resume/base`), not the live page-break dropdown. Unsaved dropdown changes never reach print — that matches your "on the fly?" question.

Parent AST-1483 Component/Technical scope is builder-only ("no UI changes"). Fixing the residual UAT fail needs UI work (auto-save before Print, or print from live `structureRows`, and/or an operator signal that Print uses saved structure only).

Need your call:
1. **Widen scope** — amend AST-1489 / parent to include Base + JAR Print/structure-authoring UI, then Hedy re-plans Plan Ready, or
2. **Works as designed** — operators must Save sections before Print; close AST-1489 (and keep the prior answer on the parent).

Holding at Plan Discuss, assignee → you.

##### susan — 2026-08-26T16:04:25.048Z
Option 1

#### As-is / To-be / Repro _(embedded build narrative, sourced from `ast-1476-structure-editor-page-break-dropdown-base-and-job.md` § "Bug: AST-1489", written after Susan's Option 1 answer)_

**As-is:** After AST-1487, builder emit honors **saved** `page_break_policy` on `artifacts.resume_structure.sections[*]`, but Base Resume Content and JAR Job Resume **Print Resume** handlers only `GET` resume HTML built from the persisted candidate snapshot. Unsaved page-break dropdown edits live in page state (`allSections` / structure rows from `ArtifactEditor`) and never reach print until the operator clicks **Save sections**.

**To-be:** Clicking **Print Resume** applies the operator's current page-break dropdown choices even when **Save sections** has not been clicked since the last edit — by auto-persisting the current structure rows (including `page_break_policy`) immediately before the existing validate-then-blob print `GET`. Susan approved widen-to-UI Option 1 on 2026-08-26.

**Repro:**
1. Open Artifacts → Base Resume Content for a candidate with printable saved base resume content and at least one enabled body section (e.g. Prior Experience).
2. Expand structure authoring; on a section header, change **Page break** from default to **New page before** (`page_break_before`). Do **not** click **Save sections**.
3. Click **Print Resume** (validate-then-blob opens HTML tab).
4. Inspect embedded `@media print` CSS in the returned HTML: section still uses prior persisted policy (e.g. `#prior-experience { page-break-inside: avoid; }` for default `avoid_split`) — not `#prior-experience { page-break-before: always; }`.
5. Repeat on JAR → Job Resume artifact tab: change page-break dropdown without Save sections → **Print Resume** → same mismatch.

Fixture-level check (no browser): with `allSections` holding `page_break_policy: "page_break_before"` for `prior_experience`, `handlePrint` issues `GET /candidate/resume/base?…` without a preceding `PUT /api/candidates/{id}/data` whose body includes that policy.

#### Root cause

AST-1337 deliberately wired Print to **saved** server content only (`handlePrint` comment: "saved base via GET … (not editor buffer)"). AST-1476 added catalog-driven dropdown + **Save sections** PUT persistence but did not connect live structure rows to Print. `handlePrint` / `handlePrintResume` never read `allSections` and never PUT `resume_structure` before the resume HTML `GET`, so AST-1487's builder fix was invisible until explicit Save sections.

#### Proposed change (as built)

**Approach:** auto-save structure before print (no new API route, no builder change). Reuse the existing PUT shape from `saveStructure`; refactor to a shared async persist step both Save and Print can await.

**`ArtifactsBaseResumeContent.tsx`:**
1. Extract page-local `persistStructureRows(rows: SectionRow[]): Promise<void>` from `saveStructure` — guards `selectedId`, builds the `sections` map exactly as today (including `page_break_policy`), PUTs `/api/candidates/${selectedId}/data`, re-GETs `resume_structure` and reapplies via `applyStructurePayload`, manages `structureSaving`/`structureError`, no success toast inside the helper.
2. Rewrite `saveStructure(rows)` to call `persistStructureRows` then show the existing success toast — preserves error-toast behavior.
3. In `handlePrint`, after `selectedId`/`printing` guards and before the resume `GET`: `await persistStructureRows(allSections)`; on failure set `printError`, error toast, return (no blob tab); on success proceed with the existing validate-then-blob `GET` flow unchanged.
4. Update the stale comment: print **content** still comes from saved `base_resume`; **structure page-break policies** are auto-persisted from current editor rows immediately before the GET.

**`JobAnalysisReportModal.tsx` — same pattern:** extract `persistStructureRows` mirroring Base; rewrite `saveStructure` to wrap persist + success toast; in `handlePrintResume`, before the resume `GET`, `await persistStructureRows(allSections)` when `selectedId` is set (skip persist when missing — print uses server structure as today); add `selectedId`/`allSections` to the `useCallback` dependency array.

**`ArtifactEditor.tsx`:** no change required — both pages keep duplicate `persistStructureRows` (preferred, minimal diff).

**Out of scope:** `src/core/builder.py`, `api_resume_html.py`, `config.py`, `candidate.py`, new routes, passing live structure in the print GET query/body.

**Tests (Betty):** Base — change page-break combobox, click Print Resume without Save sections, assert a structure `PUT` occurred with the new policy before the resume `GET`; JAR — parallel case. Bible rows updated where manifest text referenced AST-1337 "saved only" for structure (content-only invariant remains).

#### Blast radius / what must still hold

Extra PUT on every Print is a lightweight structure-only write (also persists other unsaved row fields — title/order/enabled/format — acceptable). AST-1337 content invariant holds: Print still uses saved **body** content, only structure policies are auto-persisted pre-print. Explicit Save sections unchanged UX; Save-then-Print now issues two harmless idempotent PUTs. AST-1487 builder mapping already correct; this bug completes the operator-facing loop. Session/Cover Letter print paths untouched.

#### Review

Radia review-fix @ `d119eb2c` — CLEAN, PROCEED. Auto-persist structure before Print on Base + JAR; [bug-repro] substantive; "What must still hold" intact.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx` + `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | Extract `persistStructureRows`; auto-persist before Print Resume on both surfaces | `dcc93b885` — +100/-78 across 2 files |
| | _tests_ | Base + JAR print-before-PUT bug-repro; bible rows (`frontend/pages.md` + `components.md`) | `4f45f24d8`/`c1776c654` |

### AST-1490 — Print Resume contact-only after section reorder
_Archived: 2026-09-09 · Linear URL: n/a — no standalone Linear-archive doc; ticket exists only as a `## Bug: AST-1490` section embedded in `ast-1480-restore-structure-mode-resume-section-body-edit-loop.md` (part of [[artifacts-ast-1459-resume-editor-is-not-working-properly]]) · Status at archive: (inferred Archive, per commit trail) · Project: Astral Artifacts (inferred) · Assignee: hedy (inferred from commits) · Blocked by / blocks / related: parent: AST-1483 (per Susan's/Chuckles's 2026-08-26 comments on the parent, which filed both AST-1489 and AST-1490 from the same [bug] report)_

_No standalone ticket file for AST-1490 exists anywhere in this repo's `docs/features/**` tree — its only written record is the embedded section below, reproduced here in full since this is its real family._

#### As-is

On Base Resume Content and JAR Job Resume structure authoring, moving a section **Up** or **Down** then clicking **Print Resume** (with or without **Save sections**) produces HTML with the contact/header block only — enabled body sections are missing from the printed output. The on-screen editor may flash **Loading…** after reorder because the shared artifact loader re-runs.

#### To-be

After a structure Up/Down reorder, **Print Resume** still emits the full resume body (contact plus every enabled content section) in the new section order. Reorder alone must not trigger a spurious candidate/job artifact re-GET or wipe hydrated section bodies.

#### Repro

1. Open Artifacts → Base Resume Content for a candidate with printable saved `base_resume` (non-empty prose in at least two body sections, e.g. Professional Summary and Prior Experience).
2. Expand structure authoring; click **Up** or **Down** on any movable body section header. Observe brief **Loading…** (optional).
3. Do **not** click **Save sections** (AST-1489 auto-persist on Print is sufficient).
4. Click **Print** / **Print Resume**; open the blob HTML tab.
5. **Actual:** contact/header renders; body `<section>` blocks for summary/experience/etc. are absent or empty.
6. **Expected:** full body sections present in the reordered structure order.
7. Repeat on JAR → Artifacts → Job Resume tab with the same reorder → **Print Resume** pattern.

Component repro (mock): after hydrate, fire `onStructureRowsChange` with two rows swapped (`order` reindexed); assert `GET /api/candidates/{id}` count does **not** increment; click Print; assert structure `PUT` (AST-1489) precedes resume `GET` and returned HTML includes body section ids.

#### Root cause

AST-1480 added `fixedFieldKeys = fixedFields.map(f => f.key).join("\0")` (~L300) so **label-only** structure header edits would not re-trigger candidate/job load effects. The signature is **order-sensitive**: Up/Down reorder changes `structureRows` → `setShapeFields(structureRows.map…)` (~L424) → same id **set** but different join string → candidate load `useEffect` (~L583–596) and job load effect (~L567–580) fire again (`setLoaded(false)` → re-GET).

The companion label-sync effect (~L486–505) also compares **ordered** `prev.map(t => t.id).join("\0")` vs `fixedFields.map(f => f.key).join("\0")`. On reorder-only, those strings differ even though the id set is unchanged, so the effect returns stale `prev` tabs instead of reordering them to match structure chrome order — editor structure panels and `tabs[]` diverge.

Builder emit with a correctly saved reordered structure still produces full body HTML on the server (`build_base_resume` / `_structure_ordered_body_ids` verified on tip) — this is **not** a `builder.py` regression. The operator-visible Print failure is the UI reload / structure-vs-content desync path above, compounded by AST-1489's print-time structure auto-persist firing after reorder while the loader signature treats order as a content-key change.

#### Proposed change (as built)

**Product (`src/ui/frontend/src/components/ArtifactEditor.tsx`):**

1. **Order-insensitive load signature:** replace order-sensitive `fixedFieldKeys` with a stable id-set signature (sort keys before join), keeping the existing comment intent ("label-only structure header edits do not re-GET") extended to cover reorder-only churn. Candidate/job load effects and Cancel guards keep depending on this variable — no new deps.
2. **Reorder tabs without re-GET:** in the label-sync effect, detect reorder vs add/remove using sorted-id-array comparisons: if the **set** of ids differs, return `prev` (add/remove still handled by the load effect); if the set is the same but order differs, return `fixedFields.map(...)` reordered from `byId[f.key]` so `tabs[]` order matches structure row order without clearing `content`.
3. Do **not** change structure Up/Down handlers (`moveStructureRow` / `reindexStructureRows`) — they already emit correct `order` indices.

**Print surfaces — verify only, no code change:** `ArtifactsBaseResumeContent.tsx` `handlePrint`/`persistStructureRows` (AST-1489) already auto-persists `allSections` before the resume `GET`; after the fix, confirmed reorder → Print sends the full structure dict and print HTML includes body sections. Same verification on `JobAnalysisReportModal.tsx` `handlePrintResume`.

**Out of scope:** `src/core/builder.py`, `api_resume_html.py`, `candidate.py` normalize/emit, new API routes, structure Save button UX.

**Tests (Betty):** bug-repro — reorder structure row → Print without Save sections → resume `GET` HTML includes body sections; structure `PUT` precedes `GET` (extends AST-1489 pattern). Regression — `AST-1480: structure title rename keeps hydrated body` still holds (sorted-key signature preserves label-churn guard); reorder alone still does not increment candidate/job artifact `GET` count after initial hydrate. Bible: `docs/test-bible/frontend/components.md` AST-1490 manifest row.

#### Blast radius / what must still hold

Shared editor: Base Resume Content and JAR Job Resume both use `ArtifactEditor` structure mode — one fix covers both Print paths. AST-1480's label-only rename remains a no-re-GET path. AST-1489's print-time structure auto-persist stays; this fix makes reorder + Print reliable. Add/remove section still legitimately triggers reload (id-set change unchanged). Explicit content Save (`buildPayload`/`doSave`) unchanged. AST-1480 AC (structure-mode hydrate/edit/Save, tab chrome off, label rename no re-GET, JAR overlay, Experience unsupported path), AST-1489 (print auto-persist), AST-1487/1476 (print CSS + dropdown behavior), and AST-1323/1306 (Up/Down / Save sections UX) all confirmed unchanged.

#### Review

Radia review-fix @ `0338900a` — CLEAN, PROCEED. Sorted `fixedFieldKeys` + tab reorder sync; [bug-repro] substantive; "What must still hold" intact.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/ui/frontend/src/components/ArtifactEditor.tsx` | Order-insensitive `fixedFieldKeys`; reorder-aware tab sync; stable job load deps | `20d4b7e3a` — +13/-8 |
| | _tests_ | Reorder+Print full-body bug-repro; no-re-GET regression guard; bible manifest row | `64fc383db`/`7c630a753` |
