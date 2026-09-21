# AST-1462 — Create and position page break
**Component:** artifacts  
**Children:** AST-1474, AST-1475, AST-1476  
**Linear archived:** AST-1462 2026-09-09; AST-1474 2026-09-09; AST-1475 2026-09-09; AST-1476 2026-09-09

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-08-24 15:54 | AST-1474 | docs | `56eecd88c` | plan — page-break policy config and resume_structure schema |
| 2026-08-24 16:10 | AST-1474 | docs | `4fc40a85e` | Joan validate — plan approved |
| 2026-08-24 16:46 | AST-1474 | code | `7c53225ac` | page-break policy config and resume_structure schema |
| 2026-08-24 16:48 | AST-1462/1474 | sync | `67c214b31` | sync(publish-ref): origin/sub/AST-1462/AST-1474-… |
| 2026-08-24 16:53 | AST-1474 | test | `5f1051cf2` | page-break policy schema coverage |
| 2026-08-24 16:54 | AST-1474 | merge-tests | `f150166d2` | origin/tests 5f1051cf |
| 2026-08-24 16:59 | AST-1462/1474 | sync | `b8a665139` | sync(publish-ref) — wrong-parent contamination introduced here |
| 2026-08-24 17:07 | AST-1474 | docs | `cd8a24e92` | Radia review — wrong-parent sync on publish ref |
| 2026-08-24 17:16 | AST-1474 | resolve | `4aef54ffc` | strip wrong-parent sync contamination |
| 2026-08-24 17:27 | AST-1475 | docs | `740acbe2e` | plan — builder print CSS from structure page-break policies |
| 2026-08-24 17:37 | AST-1475 | docs | `f1a06a3f5` | Joan validate — APPROVED builder print CSS |
| 2026-08-24 17:48 | AST-1462 | sync | `f47d5d29d` | sync(ftr): origin/ftr/AST-1462-create-and-position-page-break |
| 2026-08-24 17:49 | AST-1475 | code | `7fb201ea5` | map structure page-break policies to print CSS |
| 2026-08-24 17:55 | AST-1462/1475 | sync | `01340dfaf` | sync(publish-ref) / sync(ftr) resolve into tests |
| 2026-08-24 17:58 | AST-1475 | test | `f32da2684` | page-break print CSS coverage |
| 2026-08-24 18:00 | AST-1475 | merge-tests | `b9307d4a8` | origin/tests f32da268 |
| 2026-08-24 18:08 | AST-1475 | docs | `9282b6a0d` | Radia review — CLEAN structure policy print CSS |
| 2026-08-24 18:35 | AST-1476 | docs | `4fbd80d1e` | plan — structure editor page-break dropdown base and job |
| 2026-08-24 20:15 | AST-1476 | docs | `a915b6bf6` | Joan validate — APPROVED structure dropdown UI |
| 2026-08-24 20:17 | AST-1476 | merge-resume | `c3d956403` | resolve origin/dev into sub (bible both-sides) |
| 2026-08-24 20:18 | AST-1476 | code | `7c09aced3` | page-break dropdown types and ArtifactEditor header |
| 2026-08-24 20:18 | AST-1476 | code | `94201a851` | base Save sections includes page_break_policy |
| 2026-08-24 20:19 | AST-1476 | code | `8161bc1f7` | JAR structure authoring shares page-break policies |
| 2026-08-25 09:44 | AST-1462 | sync | `acb2669b9` | sync(ftr): resolve AST-1462 ftr merge into tests |
| 2026-08-25 09:45 | AST-1476 | sync | `b73572a3d` | sync(publish-ref): resolve AST-1476 tip into tests |
| 2026-08-25 09:49 | AST-1476 | test | `318c62d4c` | structure page-break dropdown coverage |
| 2026-08-25 09:49 | AST-1476 | merge-tests | `1dc2a87e3` | origin/tests 318c62d4 |
| 2026-08-25 09:52 | AST-1462/1476 | sync | `9a1e1d110` | sync(publish-ref) — **regresses `origin/dev` product** (see AST-1476 below) |
| 2026-08-25 09:52 | AST-1476 | merge-resume | `191de65ae` | resolve origin/dev (keep api_jobs bible both sections) — clean, immediately undone by the sync above |
| 2026-08-25 09:55 | AST-1476 | docs | `8e7dee841` | Radia review — sync regressed origin/dev product (FIX-NOW) |
| 2026-08-25 09:58 | AST-1476 | resolve | `9b0f01212` | restore origin/dev product; keep page-break slice (17 files, meteorite/inbox/tracker/dispatcher/database/JobDetailModal) |
| 2026-08-25 10:15 | AST-1462 | fix | `bba008b6a` | restore sibling UAT docs/tests dropped during page-break land¹ |
| 2026-08-25 21:58 | AST-1475 | test | `f3aed2648` | test(AST-1487) bug-repro — restore AST-1475 page-break print CSS coverage² |
| 2026-09-09 17:56 | AST-1474/1475/1476 | docs | `418e10025`/`6770385ed`/`f5f5dc909` | archive Linear issue content |
| 2026-09-09 18:06 | AST-1462 | docs | `cc245ea59` | archive Linear issue content |

¹ `bba008b6a` restores files belonging to unrelated **meteorite-family** tickets (AST-1453, AST-1454, AST-1469, AST-1470, AST-1471, AST-1472 docs + `test_meteorite.py` + `test_api_meteorite.py` + `test_JobDetailModal.test.tsx`) that the AST-1476 sync regression (see below) had collaterally deleted. It is collateral repair, not AST-1462 family product — those tickets belong to other families' own archives, not this one.
² This is AST-1487's own bug-repro test commit — AST-1487's real parent is **AST-1483** (a later family in this archival pass), not AST-1462. It is footnoted here only because it body-matches "AST-1475" in the grep; its full build narrative (embedded in the AST-1475 source doc under a `## Bug: AST-1487` heading, sourced from AST-1475's builder.py regression) is preserved separately for that family, not reproduced in this archive.

## Epic — AST-1462
_Archived: 2026-09-09 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1462/create-and-position-page-break · Status at archive: Archive · Project: Astral Artifacts · Assignee: chuckles · Priority / estimate: None / 5 · Blocked by / blocks / related: —_

### Purpose

Resume print layout today hard-codes a few page-break rules in the builder (notably `#prior-experience { page-break-before: always }` and role/section avoid rules) while `BUILD_CONFIG["supported_sections"][*]["page_break_policy"]` literals exist but are not read at render time. Operators cannot choose where a new printed page starts or whether a section should flow naturally versus stay intact on one page. This epic adds per-candidate **page-break control on structure sections** — persisted in `artifacts.resume_structure`, editable on **Base Resume Content** and the **JAR Job Resume** structure headers (job UI seeded from base policies), honored when printing **base** and **job** resumes — so Susan can place explicit breaks before sections and keep content blocks together without editing HTML or CSS by hand.

### Functional scope

* **Per-section page-break policy on structure.** Each enabled resume section carries an operator-set policy via a header dropdown: flow uninterrupted, force a new page before the section, or keep the section block together. Policies persist on `artifacts.resume_structure.sections[*]` and round-trip through existing structure Save paths.
* **Default = keep block together.** New and existing candidates with no explicit override get **keep block together** (`avoid_split` or equivalent) for every section — not the old hard-coded prior-experience always-break. The operator changes a section only when they want flow or a forced break.
* **Experience roles always stay together.** Each experience job/role chunk must never split across pages (no orphaned title or bullet). That keep-together is mandatory in the builder for experience roles — not an optional per-role control in the Experience job-array editor. Section-level dropdown remains for the Experience section as a whole (e.g. new page before Experience).
* **Print honors policies for base and job resumes.** Saved base resume HTML/print and job-tailored resume HTML/print reflect the candidate's structure policies; legacy hard-coded `#prior-experience { page-break-before: always }` no longer wins over operator/default policy.
* **Structure editor control on base and job.** The same per-section header dropdown appears on Base Resume Content and on JAR Job Resume structure authoring. Job Resume layout uses page-break settings from base (`artifacts.resume_structure`) as the defaults shown/applied — shared candidate structure, not a second job-only policy store in this epic.
* **No regression to section content editing or ordering.** AST-1323/AST-1410 structure header authoring, section reorder, and body Save on base/job paths remain intact; this epic adds one more persisted structure field, UI on both surfaces, and print wiring only.

### Component scope

* `src/utils/config.py` — **modified** — canonical allowed page-break policy tokens; default for every known section id = keep block together; catalog fields exposed to UI.
* `src/core/candidate.py` — **modified** — validate/normalize/default the new per-section page-break field in `normalize_resume_structure` / `RESUME_STRUCTURE_DEFAULT`.
* `src/core/builder.py` — **modified** — generate print `@media` page-break CSS from resolved structure policies; always emit experience `.role` keep-together; gate/remove hard-coded `#prior-experience` always-break so structure policy wins; apply on base, session-base, and job resume emit paths.
* `src/ui/api/api_candidate.py` — **modified** — include page-break policy options and defaults in `/resume_structure` catalog payload.
* `src/ui/frontend/src/components/ResumeStructureEditor.tsx` — **modified** — extend `SectionRow` / catalog types with page-break policy when shared outside ArtifactEditor.
* `src/ui/frontend/src/components/ArtifactEditor.tsx` — **modified** — structure header dropdown + Save payload for per-section page-break policy (shared by base and job structure mode).
* `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx` — **modified** — pass through page-break field on structure Save if not wholly owned by ArtifactEditor.
* `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` — **modified** — ensure JAR Job Resume structure mode surfaces the same page-break dropdown (candidate structure as defaults).
* `tests/component/core/test_builder.py` — **modified** — assert print CSS reflects structure policies; experience roles always `page-break-inside: avoid`; no forced prior-experience break unless policy says so.
* `tests/component/frontend/components/test_ArtifactEditor.test.tsx` — **modified** — structure-mode Save includes page-break policy; dropdown on header for base and job persistence paths.
* `docs/test-bible/core/builder.md` — **modified** — manifest rows for new/changed builder assertions (Betty at qa-child).

### Technical scope

* **config.py** — config-owned allowed page-break policy string tokens (e.g. flow / page_break_before / avoid_split — exact names are plan-child's call); default policy for every `RESUME_STRUCTURE_KNOWN_SECTION_IDS` entry is keep-block-together; expose for catalog/UI.
* **candidate.py** — on each section spec, accept optional page-break policy with keep-together default when absent; reject unknown tokens; preserve through prepare/hydrate/save paths.
* **builder.py** — map each enabled section's resolved policy to print CSS via existing DOM ids (`_html_section_dom_id`); **always** keep `.role` blocks together regardless of section dropdown; remove or gate hard-coded `#prior-experience { page-break-before: always }` so operator/default policy wins; session-base and job resume entry points pass structure through unchanged.
* **api_candidate.py** — extend GET `/resume_structure` catalog with allowed policies list and default map for the structure editor dropdown.
* **ArtifactEditor.tsx / ResumeStructureEditor.tsx / ArtifactsBaseResumeContent.tsx / JobAnalysisReportModal.tsx** — compact per-section header dropdown on base and job structure authoring; include policy in structure Save; job path shows/uses candidate `resume_structure` policies as defaults (same persistence).
* **test_builder.py** — assert keep-together default CSS; forced break only when policy set; experience roles always avoid split; prior-experience not always-broken unless policy says so.
* **test_ArtifactEditor.test.tsx** — change policy → Save → PUT includes page-break field; control present in structure mode for candidate and job persistence.

### Architectural definition

* **Patterns to reuse** — `pattern.config.config-block`; `pattern.ui.admin-endpoint`.
* **New patterns proposed** — `pattern.artifacts.resume-section-print-policy` — structure-persisted per-section print policy resolved at builder emit (config keep-together defaults + candidate override → embedded print CSS; experience roles always avoid split). Introduced by AST-1475 (behavior + citation only; no `canon/patterns/**` file minted in this epic — deferred to epic close per binding Decision).
* **Applicable statutes** — `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `astral.layers.ui-config-driven-business-logic`; `astral.standards.in-scope-only`; `astral.git.engineer-test-tree-ban`.

### Acceptance criteria

1. **Defaults** — a candidate with no explicit page-break overrides gets keep-block-together for every section in print CSS; prior experience does **not** force a new page unless the operator set that policy.
2. **Explicit break** — setting "new page before" on a section causes that section to start on a new printed page in base and job resume print HTML; reverting to flow or keep-together removes the forced break.
3. **Keep together** — keep-block-together on a prose section prevents the section block from splitting across pages; every experience role chunk always has `page-break-inside: avoid` (or equivalent) even without an operator toggle per role.
4. **Persistence** — changing policies on Base Resume Content structure Save survives reload; JAR Job Resume shows the same structure policies (base as defaults) and print for that candidate/job reflects them without a separate job-only policy store.
5. **UI** — each structure section header on **Base Resume Content** and **JAR Job Resume** exposes the page-break dropdown; Save persists without requiring a separate body edit.
6. **Tests** — builder component tests and ArtifactEditor structure-mode tests (base + job paths) pass on publish ref for the scenarios above.

### Open questions

none

### Proposed child tickets

**Monolith check:** schema, builder emit, and dual-surface UI — three children by layer; builder blocked on schema.

**1!!!: Page-break policy config and resume_structure schema — Ada** — Adds config-owned policy tokens with keep-together as the default for all known sections; extends `normalize_resume_structure` / defaults / GET catalog so structure sections persist a page-break policy. Does **not** emit print CSS or build React controls.
**Citations:** `pattern.config.config-block`, `astral.config.config-source-of-truth`, `astral.standards.no-hardcoded-sets`.
**Scope:** `src/utils/config.py`; `src/core/candidate.py`; `src/ui/api/api_candidate.py`.
**Estimate: 2**

**2!: Builder print CSS from structure page-break policies — Hedy** — Maps resolved per-section policies to embedded print `@media` rules on base, session-base, and job resume builders; always keeps experience `.role` chunks together; gates legacy hard-coded `#prior-experience` always-break so structure policy wins. Does **not** own React editor controls.
**Citations:** `pattern.config.config-block`, new `pattern.artifacts.resume-section-print-policy` (introduce), `astral.standards.in-scope-only`.
**Scope:** `src/core/builder.py`; `tests/component/core/test_builder.py`; `docs/test-bible/core/builder.md` manifest touch at qa-child.
**Estimate: 3**

**3: Structure editor page-break dropdown on base and job — Katherine** — Exposes the per-section page-break dropdown on Base Resume Content and JAR Job Resume structure headers; persists via existing structure Save (job uses base/`resume_structure` as defaults). Does **not** change builder emit or config token lists.
**Citations:** `pattern.ui.admin-endpoint`, `astral.layers.ui-config-driven-business-logic`, `astral.standards.no-hardcoded-sets`.
**Scope:** `src/ui/frontend/src/components/ArtifactEditor.tsx`; conditional touch `ResumeStructureEditor.tsx`, `ArtifactsBaseResumeContent.tsx`, `JobAnalysisReportModal.tsx`; `tests/component/frontend/components/test_ArtifactEditor.test.tsx`.
**Estimate: 3**

### Original brief

Where candidate can explicitly create a page break or let the content flow uninterrupted across pages, keeping blocks of content together. This is for both base and job resumes.

#### Comments

##### chuckles — 2026-08-24T22:01:55.601Z
@susan
1. **Control shape:** Do you want a per-section header dropdown (e.g. *Flow / New page before / Keep block together*) or the ability to insert explicit page-break-only rows between sections (or both)?
2. **Default migration:** Should existing candidates inherit today's hard-coded golden rules as their initial per-section defaults, or should the new default be uninterrupted flow until the operator opts into breaks?
3. **Experience granularity:** Is section-level control enough, or do you also need per-role page-break control inside the Experience job-array editor?

##### chuckles — 2026-08-24T22:18:10.079Z
@susan
Missing for dispatch:
* Linear **project** is unset on this parent — every child must inherit the parent project. Set project (likely **Astral Artifacts**) and reassign Chuckles on **Todo** when ready.

##### susan — 2026-08-25T00:09:11.063Z (via chuckles AST-1474 review note)
AST-1474 REVIEW — Radia fix-now: publish ref has AST-1464 sibling syncs; recalling Ada for branch cleanup.

##### susan — 2026-08-25T14:49:58.778Z
@chuckles What's next here?

##### chuckles — 2026-08-25T14:52:06.491Z
[check-linear] In Progress — AST-1474/1475 User Testing; AST-1476 Code Complete (last child). Next: finish AST-1476 → UT + merge, then prep-uat.

##### chuckles — 2026-08-25T16:55:41.694Z
AST-1476 REVIEW — Radia: publish-ref tip sync regressed origin/dev; Katherine to repair tip then resolve.

### Files changed (plan vs actual)

_No direct product commit trail on the parent beyond the collateral-repair commit `bba008b6a` (restoring unrelated meteorite-family sibling docs/tests dropped by the AST-1476 sync regression — see ledger footnote ¹) and the archive-docs commit. Implementation landed via the three sub-issues below._

## Sub-issues

### AST-1474 — Page-break policy config and resume_structure schema
_Archived: 2026-09-09 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1474/page-break-policy-config-and-resume-structure-schema-create-and · Status at archive: Archive · Project: Astral Artifacts · Assignee: ada · Priority / estimate: None / 2 · Blocked by / blocks / related: parent: AST-1462; blocks: AST-1475_

#### What this implements

Adds config-owned policy tokens with keep-together as the default for all known sections; extends `normalize_resume_structure` / defaults / GET catalog so structure sections persist a page-break policy. Does **not** emit print CSS or build React controls.

#### Wire contract / QA manifest

Allowed tokens: `normal` / `page_break_before` / `avoid_split`, default `avoid_split` (keep-together) for every known section including `prior_experience`. Normalize: missing/blank → `avoid_split`; valid value kept; unknown rejected; hydrate soft-fills; ingest stamps. GET catalog / `all_sections` expose the page-break fields; soft-default invalid stored values; PUT persists `page_break_before` / rejects unknown.

QA manifest: `tests/component/utils/test_config.py::TestAst1474PageBreakPolicyCatalog`; `tests/component/core/test_candidate.py::TestAst1474PageBreakPolicyNormalize`; `tests/component/ui/api/test_api_candidate.py::TestAst1474PageBreakPolicyCatalogApi`.

#### Build and review

Plan published (`56eecd88c`), Joan validate approved (`4fc40a85e`), product landed (`7c53225ac`). A wrong-parent sync contaminated the publish ref (`b8a665139`); Radia flagged it (`cd8a24e92`: "[code-rubric] REVIEW — wrong-parent sync on publish ref"); Ada resolved by stripping the contamination (`4aef54ffc`, "§9a clean").

#### Resolution

No fix-now on the schema slice itself; the wrong-parent sync was cleanly stripped. Betty's schema tests (bible shasums for `core/candidate.md`, `utils/config.md`, `ui/api/api_candidate.md`) landed green.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/utils/config.py` | Allowed tokens, keep-together default map, catalog literals | `7c53225ac` — +27 |
| ✓ | `src/core/candidate.py` | Validate/normalize/default new field | `7c53225ac` — +30 |
| ✓ | `src/ui/api/api_candidate.py` | Catalog payload for policies | `7c53225ac` — +14 |
| | _tests_ | schema coverage manifest above | `5f1051cf2`; bible per Betty manifest |

### AST-1475 — Builder print CSS from structure page-break policies
_Archived: 2026-09-09 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1475/builder-print-css-from-structure-page-break-policies-create-and · Status at archive: Archive · Project: Astral Artifacts · Assignee: hedy · Priority / estimate: None / 3 · Blocked by / blocks / related: parent: AST-1462; blocks: AST-1476_

#### What this implements

Maps each enabled body section's resolved `page_break_policy` (from `artifacts.resume_structure`, tokens owned by AST-1474) into the shared resume embedded `@media print` block so base, session-base, and job resume HTML honor flow / new-page-before / keep-together. Always keeps experience `.role` chunks together. Removes the legacy hard-coded `#prior-experience { page-break-before: always }` so structure policy wins. Does **not** own React editor controls (AST-1476) or config/schema (AST-1474).

#### Wire contract

Token → CSS mapping: `avoid_split` → `page-break-inside: avoid;`; `page_break_before` → `page-break-before: always;`; `normal` → no rule (flow uninterrupted). Missing/blank/unknown policy soft-defaults to `RESUME_STRUCTURE_PAGE_BREAK_POLICY_DEFAULT` (`avoid_split`) rather than raising. Rules emitted only for enabled **body** section ids (`_structure_ordered_body_ids`); contact/header trio skipped. `.role { page-break-inside: avoid; }` is always present in print, mandatory regardless of dropdown. Single injection point — `_emit_html_document` — so `build_base_resume`, `build_session_base_resume`, and `build_resume_from_job` all pick up policies via the `resume_structure=` they already pass.

⚠️ **Decision:** Consume only AST-1474's `RESUME_STRUCTURE_PAGE_BREAK_POLICIES` / `_DEFAULT` constants — not the legacy `BUILD_CONFIG["supported_sections"][*]["page_break_policy"]` (mixed `keep_with_next` values, not the operator contract). ⚠️ **Decision:** delete the hard-coded `#prior-experience { page-break-before: always; }` line outright — prior experience only breaks when its structure policy says `page_break_before`. ⚠️ **Decision:** introduce pattern `pattern.artifacts.resume-section-print-policy` by implementation + docstring citation only; no `canon/patterns/**` file in this ticket.

#### Plan review — Joan (APPROVED)

**discuss** — assignee was Hedy, not Joan, at validate time (normal handoff artifact, not a defect). **discuss** — ticket AC4 still named "ArtifactEditor structure-mode tests" though this slice correctly scoped builder tests to Betty and deferred ArtifactEditor to AST-1476 — optional ticket-description trim only. **discuss** — the CSS helper emits rules for all enabled body ids even when a section's HTML body is empty (harmless extra selectors, tightening to `emitted_ids` optional follow-up). **acceptable** — AST-1474 prerequisite wasn't on the epic worktree yet at plan time; plan's stop-and-escalate-if-missing rule was correct, not a defect. **acceptable** — golden `TestAst1020GoldenStylesheet` flip deferred to Betty at qa-child (engineer test-tree ban).

#### Radia review — code-rubric.v2, CLEAN

Full statute sweep conforms/not-applicable throughout. Product commit `7fb201ea` (+26/-3, `builder.py` only) confirmed to implement Stage 1 completely: imports the AST-1474 constants, `_print_section_page_break_css` maps tokens per the binding table, `_emit_html_document` f-string injects dynamic rules and removes the hard prior-experience break, golden companions (`h2`, `#competencies`, `.role`, `p, li`) retained, cover-letter print CSS untouched, all three resume emit paths already threaded `resume_structure=`. Branch tip vs `origin/dev`: 4 `src/**` files (AST-1475 + AST-1474 prerequisite) — clean epic-stack shape, no cross-epic contamination (unlike AST-1474's prior wrong-parent-sync review).

**discuss** — `pattern.artifacts.resume-section-print-policy` cited/implemented but no `canon/patterns/**` entry yet; Joan APPROVED intro-by-behavior, deferred to epic close (Archie/Chuckles). **advisory** — harmless extra print selectors for enabled-but-empty body sections, matches plan. **advisory** — prior Joan discuss items all addressed or accepted.

#### Resolution

No fix-now. `TestAst1475PageBreakPrintCss` (default avoid_split/no forced prior; explicit page_break_before/normal; missing-policy soft-default + job path) and revised `TestAst1020GoldenStylesheet` landed green via Betty.

**Note — later regression:** this ticket's product (`7fb201ea`) shipped clean and reviewed CLEAN, but never survived onto `origin/dev`'s first-parent line for `builder.py` — it was overwritten by the AST-1476 sync regression (see AST-1476 below) and had to be restored as its own bug ticket, **AST-1487** (real parent AST-1483, archived in a later family of this pass — not reproduced here; see that family's archive for the full bug narrative, sourced from this ticket's doc).

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/core/builder.py` | Print CSS from structure + mandatory role keep-together | `7fb201ea5` — +26/-3 |
| | _tests_ | `TestAst1475PageBreakPrintCss` + revised `TestAst1020GoldenStylesheet` | `f32da2684`; bible per Betty manifest |

### AST-1476 — Structure editor page-break dropdown on base and job
_Archived: 2026-09-09 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1476/structure-editor-page-break-dropdown-on-base-and-job-create-and · Status at archive: Archive · Project: Astral Artifacts · Assignee: katherine · Priority / estimate: None / 3 · Blocked by / blocks / related: parent: AST-1462_

#### What this implements

Exposes a per-section page-break policy dropdown on structure section headers for **Base Resume Content** and **JAR Job Resume**; options and labels come from the GET `/resume_structure` catalog (AST-1474); values persist on `artifacts.resume_structure.sections[*].page_break_policy` via existing structure Save paths (job UI uses the same candidate structure — no job-only policy store). Does **not** change builder emit or config token lists (AST-1474 / AST-1475).

#### Wire contract

Compact `<select>` in the existing `.structure-authoring-header` row, after the format select, reusing class `structure-authoring-style`; options/labels entirely catalog-driven (`page_break_policies`, `page_break_policy_labels`, `page_break_policy_default`) — never hardcoded in React; select omitted entirely if the catalog has no policies. Persisted wherever structure sections are already written (`ArtifactsBaseResumeContent.saveStructure`, `ArtifactEditor.doSave` structure bundle, `addStructureSection` defaults) — always send the explicit token, never omit on default match. JAR Job Resume enables the **same** full `structureAuthoring` gate as Base (not an isolated dropdown mode); `onStructureSave` PUTs `{ artifacts: { resume_structure: { sections } } }` to the candidate data route — job body content Save stays separate and does not bundle `resume_structure`.

#### Stages 1–3 (as built)

Stage 1: `Catalog`/`SectionRow` types extended in `ResumeStructureEditor.tsx`; `ArtifactEditor.tsx` gets the catalog-driven `<select>`, `addStructureSection` default, and `doSave` always-set `page_break_policy`. Stage 2: `ArtifactsBaseResumeContent.saveStructure` includes the field on every spec. Stage 3: `JobAnalysisReportModal.tsx` loads `all_sections` + `catalog`, adds `persistStructureRows`-style `saveStructure` PUTing to the candidate route, wires full `structureAuthoring` props onto the Job Resume `ArtifactEditor`.

#### Plan review — Joan (APPROVED)

**discuss** — no `## Self-assessment` block (sibling AST-1475 had one) — optional add. **discuss** — ticket AC6 still named "builder component tests" though this child's scope correctly limited Betty work to `test_ArtifactEditor.test.tsx` — optional trim. **discuss** — the dropdown may appear on contact-header rows with no print body section — accepted, no explicit skip rule in parent AC. **acceptable** — JAR enables full structure authoring (not a dropdown-only mode) — matches AC5. **acceptable** — `jobPersistence` Save keeps its early return, does not bundle structure — policies persist via Save sections instead, satisfying the "no separate body edit" AC.

#### Radia review — code-rubric.v2, FIX-NOW → resolved

First review of publish-ref tip `9a1e1d11` found a serious problem, **not in the AST-1476 product slice itself**: the final `sync(publish-ref)` commit (`9a1e1d11`, merging `191de65a merge-resume` with `1dc2a87e merge-tests`) took the wrong conflict side and **regressed 17 files of already-shipped `origin/dev` product** — `inbox.py`, `meteorite.py`, `tracker.py`, `dispatcher.py`, `consult.py`, `contact.py`, `database.py`, `api_inbox.py`, `api_meteorite.py`, `api_jobs.py`, `JobDetailModal.tsx`, `config.py` and more, −1666/+424 lines, reverting AST-1457/AST-1472 meteorite work back toward its AST-1032 gazer-ingest era shape. Three fix-now findings: (1) the sync regression itself; (2) a scope-gate violation (22 `src/**` files touched vs the plan's 4-file frontend scope); (3) cross-epic contamination — `sub/AST-1457/*` meteorite commits had been synced onto the AST-1462 child ref before `merge-resume` cleaned it, and the final sync re-broke it. Radia's advisory: the AST-1476 product slice itself (`7c09aced` → `8161bc1f`, +108 lines, 4 files) was sound and matched all three plan stages and binding Decisions — the pre-sync tip `191de65a` showed a clean 7-file diff vs `origin/dev` (4 scoped + 3 AST-1474 prerequisite).

**Resolution (2026-08-25):** Katherine restored the regressed `src/**` paths from `origin/dev` and re-applied the clean epic slice (`9b0f01212`, "restore origin/dev product; keep page-break slice"). Post-fix diff vs `origin/dev` returned to 7 files/+179 — the same clean shape Radia had marked at `191de65a`. §9a dry-run confirmed clean; ticket proceeded to User Testing.

**Cross-family consequence:** this regression (before repair) had wiped a shipped vertical slice from an unrelated ticket, **AST-1479** (Jobs → Applied nav/list), whose component tests remained on `origin/dev` after the product was deleted. That gap required its own re-land ticket, **AST-1488** (`docs/features/interface/ast-1488-applied-jobs-list-home-re-land.md`, out of scope for this artifacts-folder archive), which explicitly cites "re-land after AST-1476 conflict resolution wiped product while tests remained." Reported here as a cross-folder consequence of this family's work; not edited.

**Note — later bug:** even after this fix-now was resolved, AST-1476's dropdown itself surfaced a follow-on gap — Print Resume ignored **unsaved** dropdown edits (only picked up policies already persisted via Save sections). That gap became its own bug ticket, **AST-1489** (real parent AST-1483, archived in a later family of this pass — not reproduced here; see that family's archive for the full bug narrative, sourced from this ticket's doc).

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/ui/frontend/src/components/ResumeStructureEditor.tsx` + `ArtifactEditor.tsx` | Catalog/SectionRow types; header select; Save/add payloads | `7c09aced3` — +29 across 2 files |
| ✓ | `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx` | Base Save sections includes policy | `94201a851` — +1 |
| ✓ | `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | JAR structure authoring + shared persistence | `8161bc1f7` — +78/-1 |
| ✓ | (repair) 17 `src/**` files | Restore `origin/dev` product regressed by sync | `9b0f01212` — +1685/-245 |
| | _tests_ | ArtifactEditor / JAR / Base structure-mode page-break coverage | `318c62d4c`; bible per Betty manifest |
