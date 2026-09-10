# AST-1462 — Create and position page break

<!-- linear-archive: AST-1462 archived 2026-09-09 -->

## Linear archive (AST-1462)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1462/create-and-position-page-break  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** chuckles  
**Priority / estimate:** None / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Resume print layout today hard-codes a few page-break rules in the builder (notably `#prior-experience { page-break-before: always }` and role/section avoid rules) while `BUILD_CONFIG["supported_sections"][*]["page_break_policy"]` literals exist but are not read at render time. Operators cannot choose where a new printed page starts or whether a section should flow naturally versus stay intact on one page. This epic adds per-candidate **page-break control on structure sections** — persisted in `artifacts.resume_structure`, editable on **Base Resume Content** and the **JAR Job Resume** structure headers (job UI seeded from base policies), honored when printing **base** and **job** resumes — so Susan can place explicit breaks before sections and keep content blocks together without editing HTML or CSS by hand.

## Functional scope

* **Per-section page-break policy on structure.** Each enabled resume section carries an operator-set policy via a header dropdown: flow uninterrupted, force a new page before the section, or keep the section block together. Policies persist on `artifacts.resume_structure.sections[*]` and round-trip through existing structure Save paths.
* **Default = keep block together.** New and existing candidates with no explicit override get **keep block together** (`avoid_split` or equivalent) for every section — not the old hard-coded prior-experience always-break. The operator changes a section only when they want flow or a forced break.
* **Experience roles always stay together.** Each experience job/role chunk must never split across pages (no orphaned title or bullet). That keep-together is mandatory in the builder for experience roles — not an optional per-role control in the Experience job-array editor. Section-level dropdown remains for the Experience section as a whole (e.g. new page before Experience).
* **Print honors policies for base and job resumes.** Saved base resume HTML/print and job-tailored resume HTML/print reflect the candidate's structure policies; legacy hard-coded `#prior-experience { page-break-before: always }` no longer wins over operator/default policy.
* **Structure editor control on base and job.** The same per-section header dropdown appears on Base Resume Content and on JAR Job Resume structure authoring. Job Resume layout uses page-break settings from base (`artifacts.resume_structure`) as the defaults shown/applied — shared candidate structure, not a second job-only policy store in this epic.
* **No regression to section content editing or ordering.** AST-1323/AST-1410 structure header authoring, section reorder, and body Save on base/job paths remain intact; this epic adds one more persisted structure field, UI on both surfaces, and print wiring only.

## Component scope

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

## Technical scope

* [**config.py**](<http://config.py>) — config-owned allowed page-break policy string tokens (e.g. flow / page_break_before / avoid_split — exact names are plan-child's call); default policy for every `RESUME_STRUCTURE_KNOWN_SECTION_IDS` entry is keep-block-together; expose for catalog/UI.
* [**candidate.py**](<http://candidate.py>) — on each section spec, accept optional page-break policy with keep-together default when absent; reject unknown tokens; preserve through prepare/hydrate/save paths.
* [**builder.py**](<http://builder.py>) — map each enabled section's resolved policy to print CSS via existing DOM ids (`_html_section_dom_id`); **always** keep `.role` blocks together regardless of section dropdown; remove or gate hard-coded `#prior-experience { page-break-before: always }` so operator/default policy wins; session-base and job resume entry points pass structure through unchanged.
* **api_candidate.py** — extend GET `/resume_structure` catalog with allowed policies list and default map for the structure editor dropdown.
* **ArtifactEditor.tsx / ResumeStructureEditor.tsx / ArtifactsBaseResumeContent.tsx / JobAnalysisReportModal.tsx** — compact per-section header dropdown on base and job structure authoring; include policy in structure Save; job path shows/uses candidate `resume_structure` policies as defaults (same persistence).
* **test_builder.py** — assert keep-together default CSS; forced break only when policy set; experience roles always avoid split; prior-experience not always-broken unless policy says so.
* **test_ArtifactEditor.test.tsx** — change policy → Save → PUT includes page-break field; control present in structure mode for candidate and job persistence.

## Architectural definition

* **Patterns to reuse**
  * [`pattern.config.config-block`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/config/pattern.config.config-block.md>) — allowed policy tokens and per-section defaults live in `config.py`, not React hardcodes.
  * [`pattern.ui.admin-endpoint`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/ui/pattern.ui.admin-endpoint.md>) — structure catalog continues via existing candidate GET routes; no new public surface unless catalog payload requires it.
* **New patterns proposed**
  * `pattern.artifacts.resume-section-print-policy` — structure-persisted per-section print policy resolved at builder emit (config keep-together defaults + candidate override → embedded print CSS; experience roles always avoid split). Child 2 introduces; downstream resume/print tickets reuse by catalog id once approved.
* **Applicable statutes**
  * [`astral.config.config-source-of-truth`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/config/astral.config.config-source-of-truth.md>) — policy token set and defaults in config.
  * [`astral.standards.no-hardcoded-sets`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-hardcoded-sets.md>) — UI renders allowed values from API/catalog, not inline enums.
  * [`astral.layers.ui-config-driven-business-logic`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.ui-config-driven-business-logic.md>) — structure editor reads catalog defaults/options from backend.
  * [`astral.standards.in-scope-only`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md>) — print/layout policy only; no craft-base prompt or agent schema changes.
  * [`astral.git.engineer-test-tree-ban`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/git/astral.git.engineer-test-tree-ban.md>) — Betty owns bible manifest touch at qa-child.

## Acceptance criteria

1. **Defaults** — a candidate with no explicit page-break overrides gets keep-block-together for every section in print CSS; prior experience does **not** force a new page unless the operator set that policy.
2. **Explicit break** — setting "new page before" on a section causes that section to start on a new printed page in base and job resume print HTML; reverting to flow or keep-together removes the forced break.
3. **Keep together** — keep-block-together on a prose section prevents the section block from splitting across pages; every experience role chunk always has `page-break-inside: avoid` (or equivalent) even without an operator toggle per role.
4. **Persistence** — changing policies on Base Resume Content structure Save survives reload; JAR Job Resume shows the same structure policies (base as defaults) and print for that candidate/job reflects them without a separate job-only policy store.
5. **UI** — each structure section header on **Base Resume Content** and **JAR Job Resume** exposes the page-break dropdown; Save persists without requiring a separate body edit.
6. **Tests** — builder component tests and ArtifactEditor structure-mode tests (base + job paths) pass on publish ref for the scenarios above.

## Open questions

none

## Proposed child tickets

**Monolith check:** schema, builder emit, and dual-surface UI — three children by layer; builder blocked on schema.

#### 1!!!: **Page-break policy config and resume_structure schema - Ada**

Adds config-owned policy tokens with keep-together as the default for all known sections; extends `normalize_resume_structure` / defaults / GET catalog so structure sections persist a page-break policy. Does **not** emit print CSS or build React controls.

**Citations:** `pattern.config.config-block`, `astral.config.config-source-of-truth`, `astral.standards.no-hardcoded-sets`.

**Scope:** `src/utils/config.py` (allowed tokens, keep-together default map, catalog literals); `src/core/candidate.py` (validate/normalize/default new field); `src/ui/api/api_candidate.py` (catalog payload for policies).

**Estimate: 2**

#### 2!: **Builder print CSS from structure page-break policies - Hedy**

Maps resolved per-section policies to embedded print `@media` rules on base, session-base, and job resume builders; always keeps experience `.role` chunks together; gates legacy hard-coded `#prior-experience` always-break so structure policy wins. Does **not** own React editor controls.

**Citations:** `pattern.config.config-block`, new `pattern.artifacts.resume-section-print-policy` (introduce), `astral.standards.in-scope-only`.

**Scope:** `src/core/builder.py` (print CSS from structure + mandatory role keep-together); `tests/component/core/test_builder.py`; `docs/test-bible/core/builder.md` manifest touch at qa-child.

**Estimate: 3**

#### 3: **Structure editor page-break dropdown on base and job - Katherine**

Exposes the per-section page-break dropdown on Base Resume Content and JAR Job Resume structure headers; persists via existing structure Save (job uses base/`resume_structure` as defaults). Does **not** change builder emit or config token lists.

**Citations:** `pattern.ui.admin-endpoint`, `astral.layers.ui-config-driven-business-logic`, `astral.standards.no-hardcoded-sets`.

**Scope:** `src/ui/frontend/src/components/ArtifactEditor.tsx`; conditional touch `ResumeStructureEditor.tsx`, `ArtifactsBaseResumeContent.tsx`, `JobAnalysisReportModal.tsx`; `tests/component/frontend/components/test_ArtifactEditor.test.tsx`.

**Estimate: 3**

---

## Original brief

Where candidate can explicitly create a page break or let the content flow uninterrupted across pages, keeping blocks of content together.  This is for both base and job resumes.

### Comments

#### chuckles — 2026-08-25T16:55:41.694Z
AST-1476 REVIEW — Radia: publish-ref tip sync regressed origin/dev; Katherine to repair tip then resolve.

#### chuckles — 2026-08-25T14:52:06.491Z
[check-linear] In Progress — AST-1474/1475 User Testing; AST-1476 Code Complete (last child). Next: finish AST-1476 → UT + merge, then prep-uat.

#### susan — 2026-08-25T14:49:58.778Z
@chuckles What's next here?

#### chuckles — 2026-08-25T00:09:11.063Z
AST-1474 REVIEW — Radia fix-now: publish ref has AST-1464 sibling syncs; recalling Ada for branch cleanup.

#### chuckles — 2026-08-24T22:18:10.079Z
@susan

Missing for dispatch:
* Linear **project** is unset on this parent — every child must inherit the parent project. Set project (likely **Astral Artifacts**) and reassign Chuckles on **Todo** when ready.

#### chuckles — 2026-08-24T22:01:55.601Z
@susan

1. **Control shape:** Do you want a per-section header dropdown (e.g. *Flow / New page before / Keep block together*) or the ability to insert explicit page-break-only rows between sections (or both)?
2. **Default migration:** Should existing candidates inherit today's hard-coded golden rules as their initial per-section defaults, or should the new default be uninterrupted flow until the operator opts into breaks?
3. **Experience granularity:** Is section-level control enough, or do you also need per-role page-break control inside the Experience job-array editor?

---

_Implementation detail may live in git history on `origin/dev`._
