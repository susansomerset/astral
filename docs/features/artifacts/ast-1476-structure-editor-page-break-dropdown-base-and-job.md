# AST-1476 — Structure editor page-break dropdown on base and job

**Linear:** [AST-1476](https://linear.app/astralcareermatch/issue/AST-1476)
**Parent:** [AST-1462](https://linear.app/astralcareermatch/issue/AST-1462) — Create and position page break
**Publish ref:** `sub/AST-1462/AST-1476-structure-editor-page-break-dropdown-base-and-job`

Exposes a per-section page-break policy dropdown on structure section headers for **Base Resume Content** and **JAR Job Resume**; options and labels come from the GET `/resume_structure` catalog (AST-1474); values persist on `artifacts.resume_structure.sections[*].page_break_policy` via existing structure Save paths (job UI uses the same candidate structure — no job-only policy store). Does **not** change builder emit or config token lists (AST-1474 / AST-1475).

## Scope gate

Ticket **## Scope** covers only:

- `src/ui/frontend/src/components/ArtifactEditor.tsx`
- conditional touch `src/ui/frontend/src/components/ResumeStructureEditor.tsx`
- conditional touch `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx`
- conditional touch `src/ui/frontend/src/components/JobAnalysisReportModal.tsx`
- `tests/component/frontend/components/test_ArtifactEditor.test.tsx` — **Betty at qa-child** (engineer test-tree ban)

Every product file and change kind below matches that Scope. Out of scope: `config.py` / `candidate.py` / `api_candidate.py` / `builder.py`, `App.css` (reuse existing structure-authoring classes), any new API route, job-artifact policy storage.

**Prerequisite (siblings #1–#2):** AST-1474 catalog fields and AST-1475 print mapping are already on `origin/ftr/AST-1462-create-and-position-page-break` (merged into this sub at plan time). Build assumes GET catalog already returns `page_break_policies`, `page_break_policy_labels`, `page_break_policy_default`, and each `all_sections[]` row includes `page_break_policy`. If those are missing after `sync-child.sh`, **stop** and comment on the parent — do not invent tokens or labels in React.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/ResumeStructureEditor.tsx` | Extend `Catalog` + `SectionRow` types with AST-1474 page-break fields | ui |
| `src/ui/frontend/src/components/ArtifactEditor.tsx` | Per-section header `<select>` from catalog; include `page_break_policy` on structure Save / content-bundled Save / new-section defaults | ui |
| `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx` | Include `page_break_policy` in `saveStructure` PUT payload | ui |
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | Load catalog + `all_sections`; wire structure authoring props; `onStructureSave` PUTs candidate `resume_structure` (shared policies) | ui |

**Betty at qa-child (not engineer commits):** `tests/component/frontend/components/test_ArtifactEditor.test.tsx` — structure-mode Save includes `page_break_policy`; dropdown present for base authoring path; catalog-driven options (no hardcoded token enum in assertions beyond what the mock catalog supplies). Extend fixtures that construct `Catalog` / `SectionRow` so TypeScript still compiles after the type widen.

**Do not touch:** `src/utils/config.py`, `src/core/candidate.py`, `src/core/builder.py`, `src/ui/api/api_candidate.py`, `src/ui/frontend/src/App.css`, bible under `docs/test-bible/**`.

## Decisions (binding)

⚠️ **Decision:** Field / catalog keys match AST-1474 exactly — `page_break_policy` on each section; catalog `page_break_policies`, `page_break_policy_labels`, `page_break_policy_default` (and optionally `page_break_policy_defaults` on the type for completeness; UI may ignore the per-id map and use the single default + row value). Tokens are only `normal` / `page_break_before` / `avoid_split` as served by the API — **never** hardcode that tuple or the display labels in React (`astral.standards.no-hardcoded-sets`).

⚠️ **Decision:** Render the control as a compact `<select>` in the existing `.structure-authoring-header` row, immediately after the format (`structure-authoring-style`) select, reusing class `structure-authoring-style` (same width behavior; header already `overflow-x: auto`). **Do not** edit `App.css` (not in Scope). Option text = `catalog.page_break_policy_labels[token]` when present, else the raw token string.

⚠️ **Decision:** Resolve the select’s `value` as: if `structureRow.page_break_policy` is a string in `catalog.page_break_policies`, use it; else use `catalog.page_break_policy_default`. On change, `patchStructureRow(id, { page_break_policy: e.target.value })`. If `page_break_policies` is missing or empty on the catalog, **omit** the select entirely (do not invent options).

⚠️ **Decision:** Persist `page_break_policy` wherever structure sections are already written:

1. `ArtifactsBaseResumeContent.saveStructure` — always set `spec.page_break_policy` from the row (string).
2. `ArtifactEditor.doSave` structure bundle (base content Save with structure authoring) — same field on each section spec.
3. `addStructureSection` — new rows get `page_break_policy: structureCatalog.page_break_policy_default` (empty string if somehow unset — Save/normalize still default server-side).

Do **not** omit the key when the value equals the default — always send the explicit string so reload matches the control.

⚠️ **Decision:** **JAR Job Resume** enables the same `structureAuthoring` gate as Base (pass `structureCatalog`, `structureRows`, `onStructureRowsChange`, `onStructureSave`, plus saving/error state). Fetch already hits `GET /api/candidates/:id/resume_structure` — expand it to apply `all_sections` + `catalog` like Base. `onStructureSave` PUTs `{ artifacts: { resume_structure: { sections } } }` to `/api/candidates/${selectedId}/data` (candidate structure only). Job body content continues via existing `jobPersistence`; do **not** store page-break policies on job artifacts. Enabling full structure authoring on JAR (title/format/flags + new page-break select) is intentional — AC requires the page-break control on that surface, and the existing authoring gate is the only in-Scope way to show header controls without inventing a parallel mode.

⚠️ **Decision:** Content Save under `jobPersistence` still returns early and does **not** bundle `resume_structure` (unchanged). Operators persist policy changes on JAR via **Save sections** (and on Base via Save sections and/or content Save when structure authoring is on). That satisfies AC “Save persists without requiring a separate body edit.”

## Stage 1: Types + ArtifactEditor dropdown and payloads

**Done when:** `Catalog` / `SectionRow` include page-break fields; with structure authoring on, each section header shows a catalog-driven page-break `<select>`; changing it updates the row; content Save (base) and new-section defaults include `page_break_policy`. No page parent changes yet.

1. In `src/ui/frontend/src/components/ResumeStructureEditor.tsx`, extend `Catalog` with:

   - `page_break_policies: string[]`
   - `page_break_policy_labels: Record<string, string>`
   - `page_break_policy_default: string`
   - `page_break_policy_defaults?: Record<string, string>` (optional; matches API; unused by UI steps below)

   Extend `SectionRow` with:

   - `page_break_policy: string`

2. In `src/ui/frontend/src/components/ArtifactEditor.tsx` → `addStructureSection`, add `page_break_policy: structureCatalog.page_break_policy_default || ""` to the new row object (alongside existing `format` / flags).

3. In `doSave`’s structure-authoring bundle (the `structureRows.forEach` that builds `arts.resume_structure.sections`), add `page_break_policy: row.page_break_policy` on each `spec` (always set; do not gate on truthiness the way `format` is gated — policy is required on every row).

4. In the structure-authoring header JSX (inside the `structureRow ? (` branch of `CollapsiblePanel` `label`), after the format `<select className="dep-input structure-authoring-style">` … `</select>`, when `structureCatalog!.page_break_policies?.length` is truthy, insert:

   - Compute `policyValue` per Decisions (row policy if in list, else `page_break_policy_default`).
   - `<select className="dep-input structure-authoring-style" aria-label="Page break" value={policyValue} onChange={e => patchStructureRow(structureRow.id, { page_break_policy: e.target.value })}>`
   - Options: `structureCatalog!.page_break_policies.map(token => <option key={token} value={token}>{structureCatalog!.page_break_policy_labels?.[token] ?? token}</option>)`

5. Do **not** change `jobPersistence` Save path, Generate, ExperienceJobsEditor, or non-structure headers.

## Stage 2: Base Resume Content Save includes policy

**Done when:** Clicking **Save sections** on Base Resume Content PUTs each section’s `page_break_policy`; after reload from GET, the dropdown shows the saved value.

1. In `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx` → `saveStructure`, inside the `rows.forEach` that builds `spec`, add `page_break_policy: row.page_break_policy` (always). Keep existing `format` conditional as-is.

2. Leave `catalogFromPayload` as a structural check on `body_formats` only — API already returns page-break catalog keys; TypeScript `Catalog` widen is enough. Do **not** invent local defaults when catalog fields are absent.

3. Do **not** change accent / Print / toast behavior.

## Stage 3: JAR Job Resume structure authoring + shared persistence

**Done when:** JAR Job Resume (`use_resume_structure` artifact tab) shows the same structure header controls including the page-break dropdown; **Save sections** persists policies to the candidate’s `resume_structure`; job artifact Save remains separate; no job-only policy fields.

1. In `src/ui/frontend/src/components/JobAnalysisReportModal.tsx`, import `Catalog` and `SectionRow` from `./ResumeStructureEditor` (same types as Base).

2. Add state mirroring Base (names may match Base for clarity):

   - `allSections: SectionRow[]` (default `[]`)
   - `catalog: Catalog | null` (default `null`)
   - `structureSaving: boolean`
   - `structureSaveError: string | null` (distinct from existing boolean `structureError` load-failure flag — do **not** overload that flag)

3. Replace the resume_structure `useEffect` body so that on success it:

   - Sets `structureSections` from `data.sections` (same map as today).
   - Sets `allSections` from `data.all_sections` when it is an array (cast/assert `SectionRow[]`); else `[]`.
   - Sets `catalog` from `data.catalog` when it is an object with `body_formats` array (inline the same minimal check Base uses, or a tiny local helper — do **not** import from the page module).
   - On failure: keep today’s `structureError` / null sections behavior; also clear `allSections` / `catalog`.

4. Add `handleStructureRowsChange` that updates `allSections` and syncs `structureSections` labels from row titles (same as Base).

5. Add `saveStructure(rows: SectionRow[])` that requires `selectedId`, builds `sections` with the **same** spec shape as Base (including `page_break_policy`), PUTs to `/api/candidates/${selectedId}/data` with `{ artifacts: { resume_structure: { sections } } }`, then re-GETs resume_structure and reapplies sections/catalog/allSections; set `structureSaving` / `structureSaveError` / optional toast via existing `setToast` on success/failure.

6. On the Job Resume `ArtifactEditor` (the `artTab.use_resume_structure` branch), pass:

   - `structureCatalog={catalog}`
   - `structureRows={allSections}`
   - `onStructureRowsChange={handleStructureRowsChange}`
   - `onStructureSave={saveStructure}`
   - `structureSaving={structureSaving}`
   - `structureError={structureSaveError}`

   Keep existing `structureSections`, `jobPersistence`, `title` / `artifactKey` / `taskKey` / `useCandidateResumeStructure`.

7. Do **not** change Print, build-artifacts actions, cover letter tabs, or non-structure artifact editors.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Execution contract

The plan is binding. Build-child executes stages in order, one commit per stage on the epic worktree, then `git push origin HEAD:sub/AST-1462/AST-1476-structure-editor-page-break-dropdown-base-and-job`. No extra files. Ambiguity or missing catalog fields after sync → stop and comment on **parent** AST-1462 with the Stage blocked template from plan-child. Engineers do **not** edit `tests/**` or `docs/test-bible/**` — wrong/missing coverage → `[qa-handoff]` to Betty.

## Joan validate

## Joan validate-plan — AST-1476

Identity: **Plan Ready**, assignee **Joan Clarke**, parent **AST-1462**. Publish ref `sub/AST-1462/AST-1476-structure-editor-page-break-dropdown-base-and-job` @ `4fbd80d1`. No `[plan-discuss]` rounds. Prerequisites (AST-1474 catalog fields, API `page_break_*` on worktree) present.

---

```text
[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1476
**Overall:** APPROVED
**Publish ref:** `sub/AST-1462/AST-1476-structure-editor-page-break-dropdown-base-and-job` @ `4fbd80d1`

## Traceability
AC4→Stages 2–3 (always send `page_break_policy` on Base `saveStructure` + JAR `saveStructure` PUT to candidate `resume_structure`; job artifact Save unchanged); AC5→Stages 1–3 (catalog-driven header `<select>` on Base + JAR when `structureAuthoring` wired); AC6 ArtifactEditor tests→Betty qa-child section; AC6 builder tests→AST-1475 Betty scope N/A; parent AC1–3 print defaults/breaks/roles→AST-1474/1475 N/A.

## Findings

### discuss — Missing `## Self-assessment`
- **Location:** plan doc (ends with Execution contract, no confidence block)
- **Finding:** No self-assessment section; sibling AST-1475 carried one.
- **Recommendation:** Optional add before build — stages and binding Decisions are already explicit.

### discuss — Child ticket AC6 names builder tests
- **Location:** ticket Description AC6 vs Betty notes
- **Finding:** Ticket AC6 still lists “builder component tests”; this child’s Scope and plan correctly limit Betty work to `test_ArtifactEditor.test.tsx`.
- **Recommendation:** Optional ticket description trim — plan is already right.

### discuss — Page-break control on contact header rows
- **Location:** Stage 1 header JSX (all `structureRow` headers)
- **Finding:** Plan does not skip contact sections; dropdown may appear on contact rows that have no print body section.
- **Recommendation:** Acceptable — AST-1474 persists policy on all section ids; omitting contact-only would need an explicit rule not in parent AC.

### acceptable — JAR enables full structure authoring, not dropdown-only
- **Location:** Stage 3 Decision + props list
- **Finding:** JAR wires full `structureAuthoring` gate (title/format/flags + page-break), not an isolated dropdown mode.
- **Recommendation:** Matches AC5 and existing ArtifactEditor gate; in Scope.

### acceptable — `jobPersistence` Save does not bundle structure
- **Location:** Decision on content Save early return
- **Finding:** Job body Save stays job-artifact-only; policies persist via **Save sections** on JAR.
- **Recommendation:** Correct; satisfies AC “Save persists without requiring a separate body edit” via Save sections.

context_tokens≈32000
```

```text
[plan-rubric] PROCEED (Commit: 4fbd80d1) structure dropdown UI
```

```text
AST-1476 plan approved.
```

---

**In-session:** `astral.standards.no-hardcoded-sets`, `astral.layers.ui-config-driven-business-logic`, `astral.standards.in-scope-only` — conform (catalog-driven options/labels, no new API routes, no config/builder edits). `astral.git.engineer-test-tree-ban` — conform (Betty owns `tests/` + bible). `pattern.ui.admin-endpoint` — conform (existing authenticated candidate routes, thin API already serves catalog). Layer/placement: `components/` + `pages/` flat, no `App.css` edit. `structureAuthoring` gate correctly requires `onStructureSave`; Stage 3 adds missing JAR wiring vs current `JobAnalysisReportModal` (labels-only fetch today).

## Review (build stub)

**Publish ref:** `origin/sub/AST-1462/AST-1476-structure-editor-page-break-dropdown-base-and-job`
**Tip (pre-review):** `8161bc1f7943483be61593daf3b8dca3e828662a`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `7c09aced` | Catalog/SectionRow page-break types; ArtifactEditor header select + Save/add payloads |
| 2 | `94201a85` | Base Save sections includes `page_break_policy` |
| 3 | `8161bc1f` | JAR structure authoring; Save sections → candidate `resume_structure` |

Tests deferred to Betty (`test_ArtifactEditor.test.tsx`).
