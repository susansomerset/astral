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


## Radia review

# Radia review — AST-1476

`[code-rubric] revision=2`  
**Rubric:** code-rubric.v2  
**Ticket:** AST-1476  
**Publish ref:** `sub/AST-1462/AST-1476-structure-editor-page-break-dropdown-base-and-job` @ `9a1e1d11`  
**Overall:** FIX-NOW

---

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | No agent prompt surfaces in AST-1476 slice |
| astral.agent.do-task-delegation | scoped | not-applicable | No do_task delegation changes in slice |
| astral.agent.grade-vector-validation | scoped | not-applicable | No rubric-vector validation in slice |
| astral.batch.batch-id-first | scoped | not-applicable | No batch claim paths in slice |
| astral.batch.batch-id-format | scoped | not-applicable | No batch-id format changes |
| astral.batch.claim-process-release | scoped | not-applicable | No claim/release helpers in slice |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | No entity-agent-responses changes |
| astral.config.config-source-of-truth | scoped | conforms | UI reads catalog from GET; no new config literals in React |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | No env/secret lookups |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | No debug artifact paths |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | No spike files |
| astral.dispatch.seed-auto-false | scoped | not-applicable | No dispatch seeding in slice |
| astral.dispatch.run-next-is-chain-authority | scoped | violates | Tip regresses `dispatcher.py` vs `origin/dev` (sync conflict wrong-side) |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Plan doc matches ticket slug |
| astral.git.betty-no-src-or-features | scoped | not-applicable | Radia read-only |
| astral.git.engineer-test-tree-ban | scoped | conforms | Product commits touch only planned frontend paths; Betty owns tests/bible |
| astral.layers.core-vs-external-bright-line | scoped | violates | Tip deletes core meteorite/inbox/tracker product code present on `origin/dev` |
| astral.layers.import-direction | scoped | conforms | AST-1476 slice is frontend-only; no layer violations in scoped files |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | No `scripts/**` changes |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | Dropdown options/labels from GET catalog; no hardcoded token tuple in TSX |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | No coat-check paths |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | No consult/render paths |
| astral.idioms.require-auth-on-protected-endpoints | scoped | conforms | Reuses existing authenticated `/api/candidates/...` routes |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | No seed JSON edits in slice |
| astral.seed.archie-catalog-wins | scoped | not-applicable | No seed catalog conflicts in slice |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | No boot/seed hot-path edits in slice |
| astral.seed.define-approved | scoped | not-applicable | No define/seed work |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | No seed row resurrection |
| astral.seed.other-via-coverage-join | scoped | not-applicable | No coverage-join seed logic |
| astral.standards.data-raises-caller-logs | scoped | violates | Tip regresses `database.py` vs `origin/dev` |
| astral.standards.database-header-inventory | scoped | violates | Tip regresses `database.py` header/inventory vs dev |
| astral.standards.debug-contract-gated | scoped | not-applicable | No debug emission changes |
| astral.standards.dry-and-focused-functions | scoped | conforms | `catalogFromPayload` + `saveStructure` mirror Base; dropdown logic localized |
| astral.standards.in-scope-only | scoped | violates | Tip diff: 22 `src/**` files; plan Scope gate allows 4 frontend paths |
| astral.standards.logging-via-utils | scoped | not-applicable | No logging changes in slice |
| astral.standards.names-not-ticket-ids | scoped | conforms | Uses `page_break_policy` domain field name |
| astral.standards.no-cross-contamination | scoped | conforms | AST-1476 slice stays in `src/ui/frontend/**` |
| astral.standards.no-hardcoded-sets | scoped | conforms | Select options from `catalog.page_break_policies`; labels from catalog map |
| astral.standards.public-then-helpers | scoped | conforms | `catalogFromPayload` helper colocated in JAR modal per plan |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | No utils→data late imports |
| astral.state.core-decides-transitions | scoped | violates | Tip regresses `tracker.py` state/dispatch logic vs dev |
| astral.state.job-prior-states-enforced | scoped | not-applicable | No job prior-state edits in slice |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | No dispatch runner edits in slice |
| astral.ui.frontend-file-placement | scoped | conforms | Changes in `components/` + `pages/`; no `App.css` edit |
| astral.ui.naming-conventions | scoped | conforms | Matches existing structure-authoring class names |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | No server worker config |
| orch.git.betty-merge-tests-one-sha | universal | conforms | `merge-tests(AST-1476)` present |
| orch.git.commit-vocabulary | universal | conforms | `code` / `test` / `merge-resume` / `sync` vocabulary |
| orch.git.flow-direction-inviolable | universal | violates | Final `sync(publish-ref)` reverts AST-1457/1472 product already on `origin/dev` |
| orch.git.ftr-sub-topology | universal | violates | AST-1457 meteorite subs synced onto AST-1462 child ref, then regressed at tip |
| orch.git.merge-on-checkout | universal | violates | `191de65a merge-resume` integrated dev correctly; `9a1e1d11 sync` undid it |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No cherry-pick/rebase/force evidence |
| orch.git.no-dev-agent-branches | universal | conforms | Standard `sub/AST-1462/AST-1476-*` ref |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Review from `astral-AST-1462` worktree |
| orch.git.three-permanent-branches | universal | conforms | Diff anchored to `origin/dev` |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | No unresolved product-policy fork in slice |
| orch.pipeline.plan-is-bible | universal | violates | Tip includes meteorite/inbox/tracker/config regressions outside plan Scope |
| orch.pipeline.project-scoped-queues | universal | conforms | Single-ticket review |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Spawn at Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty landed `test_ArtifactEditor` / Base / JAR coverage |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | N/A to code diff |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Katherine remains assignee at Tests Passed |
| orch.roles.pre-commit-path-bans | universal | conforms | Radia read-only |

**Notes:** Joan plan-rubric APPROVED @ `4fbd80d1`; no Excluded statute list — straggler check N/A.

---

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| `pattern.ui.admin-endpoint` | conforms | JAR/Base use existing authenticated candidate API routes; thin client, catalog from server |
| *(none other cited)* | — | Plan cites no additional catalog patterns |

---

## Plan adherence

**AST-1476 product commits (`7c09aced` → `8161bc1f`, +108 lines, 4 files)** implement Stages 1–3:

| Stage | File | Status |
|-------|------|--------|
| 1 | `ResumeStructureEditor.tsx` | `Catalog` + `SectionRow` extended with page-break fields |
| 1 | `ArtifactEditor.tsx` | Catalog-driven `<select>` after format select; `addStructureSection` default; `doSave` always sets `page_break_policy` |
| 2 | `ArtifactsBaseResumeContent.tsx` | `saveStructure` includes `page_break_policy` on every spec |
| 3 | `JobAnalysisReportModal.tsx` | Loads `all_sections` + `catalog`; `saveStructure` PUTs candidate `resume_structure`; wires full `structureAuthoring` props |

**Binding decisions satisfied in slice:**

- Options/labels from catalog only; select omitted when `page_break_policies` empty
- `jobPersistence` content Save returns early — does not bundle `resume_structure` (L583–609)
- JAR policies persist to candidate structure, not job artifacts
- `structureSaveError` separate from boolean load-failure `structureError`
- Reuses `structure-authoring-style` class; no `App.css` edit

**Pre-sync tip `191de65a` vs `origin/dev`:** 7 `src/**` files only — 4 scoped frontend + 3 AST-1474 prerequisite (`config.py`, `candidate.py`, `api_candidate.py`). **Clean epic-stack shape.**

**Publish-ref tip `9a1e1d11` vs `origin/dev`:** 22 `src/**` files, **−1666/+424 lines** — regresses meteorite/inbox/tracker/dispatcher/database/config product code and `JobDetailModal.tsx` that `origin/dev` already ships (AST-1457 / AST-1472). Caused by `sync(publish-ref)` merge of `merge-tests` taking wrong conflict side **after** `191de65a merge-resume` had integrated dev correctly.

**Tests (Betty):** `TestAst1476PageBreak*` in `test_ArtifactEditor.test.tsx`, `test_ArtifactsBaseResumeContent.test.tsx`, `test_JobAnalysisReportModal.test.tsx` — catalog-driven mocks, Save sections persistence, JAR → candidate PUT. Aligns with plan Expected Betty notes.

**Estimate 3:** Fits isolated product footprint.

---

## Findings

### fix-now — Final `sync(publish-ref)` regressed `origin/dev` product code

- **Location:** commit `9a1e1d11` (merge `191de65a` + `1dc2a87e`); affected: `src/core/inbox.py`, `meteorite.py`, `tracker.py`, `dispatcher.py`, `consult.py`, `contact.py`, `database.py`, `api_inbox.py`, `api_meteorite.py`, `api_jobs.py`, `JobDetailModal.tsx`, `utils/config.py`, etc.
- **Finding:** `191de65a merge-resume(AST-1476)` correctly merged `origin/dev` (inbox shows AST-1472 `fetch_email → land_meteorite`). Tip `9a1e1d11 sync(publish-ref)` overwrote that with pre-dev product tree from the tests merge — e.g. `inbox.py` reverts to AST-1032 gazer-ingest era. Branch tip is **behind dev on shipped meteorite work** despite dev being an ancestor of the merge-resume commit.
- **Recommendation:** Reset publish ref to `191de65a` (or re-run sync preserving product side from `merge-resume`) before Review Posted / merge-child. Do **not** land tip on `ftr` as-is.

### fix-now — Scope gate violation on publish-ref tip (`astral.standards.in-scope-only`, `orch.pipeline.plan-is-bible`)

- **Location:** `git diff origin/dev...origin/sub/AST-1462/AST-1476-* -- 'src/**'`
- **Finding:** Plan Scope = 4 frontend paths. Tip diff includes 18 additional `src/**` files with large deletions unrelated to page-break dropdown UI.
- **Recommendation:** Resolve via fix above; isolated AST-1476 commits do not require those files.

### fix-now — Cross-epic contamination on branch history

- **Location:** commits `da5ad3be`–`60afb73c` (AST-1457 meteorite subs synced onto AST-1462 child ref)
- **Finding:** Wrong-parent `sync(publish-ref)` from `sub/AST-1457/*` landed on AST-1462 child before merge-resume cleaned it; final sync re-broke product state.
- **Recommendation:** Chuckles enforce sub-branch hygiene — AST-1462 children carry only AST-1462 stack + dev integration; meteorite siblings merge via `ftr/AST-1457` → dev, not via AST-1476 publish ref.

### advisory — AST-1476 product slice is sound

- **Location:** `7c09aced`, `94201a85`, `8161bc1f`; pre-sync `191de65a`
- **Finding:** Implementation matches all three stages and binding Decisions. Catalog-driven dropdown, always-send `page_break_policy`, JAR Save sections → candidate PUT, job content Save unchanged.
- **Recommendation:** After publish-ref repair, expect **PROCEED** on statute/pattern/plan for the 4-file slice.

### discuss — Page-break control on contact header rows

- **Location:** `ArtifactEditor.tsx` structure header JSX (all `structureRow` headers)
- **Finding:** Joan flagged dropdown may appear on contact rows with no print body section; plan accepts.
- **Recommendation:** No block.

### advisory — Prior Joan discuss items

- **Location:** issue doc Joan validate (missing self-assessment; AC6 names builder tests)
- **Finding:** Unchanged; low risk.
- **Recommendation:** Optional ticket doc trim only.

---

## What's solid

- All three stages landed in focused commits with correct file footprint
- `jobPersistence` early return preserves job-artifact-only Save
- JAR wiring mirrors Base (`catalogFromPayload`, `saveStructure`, structure authoring props)
- Betty tests cover Base content Save, Save sections, and JAR candidate PUT with catalog-driven mocks
- `191de65a` demonstrates correct dev integration before the broken final sync

## Recommended actions (Chuckles — not Radia)

1. **Repair publish ref:** Point tip at `191de65a` or cherry-pick product files from `merge-resume` onto tests tip without reverting dev meteorite stack.
2. Re-run `review-child` on repaired tip (expect PROCEED for AST-1476 slice).
3. Stop syncing `sub/AST-1457/*` product onto `sub/AST-1462/*` publish refs.
4. (Optional) Add `## Self-assessment` to issue doc before close.

---

## Frame diff

| Field | Prior (issue doc stub) | This review |
|-------|------------------------|-------------|
| Tip SHA | `8161bc1f` | `9a1e1d11` |
| Scoped product files | 4 | 4 (unchanged in product commits) |
| `src/**` vs `origin/dev` at tip | — | 22 files (−1666/+424) — **regression** |
| `src/**` at `191de65a` | — | 7 files (+179) — clean (1476 + 1474 prereq) |
| Verdict | stub | FIX-NOW (sync regression); slice CLEAN |

context_tokens≈38000


```text
[code-rubric] REVIEW (Commit: 9a1e1d11) sync regressed dev product
```

## Resolution

**Date:** 2026-08-25  
**Review tip:** `9a1e1d11` (`docs(AST-1476): Radia review — sync regressed origin/dev product`)  
**Outcome:** findings addressed — publish-ref product tree restored to match `origin/dev` + AST-1476/1474 slice.

### fix-now — Final `sync(publish-ref)` regressed `origin/dev` product code

- Restored all regressed `src/**` paths from `origin/dev` (inbox/meteorite/tracker/dispatcher/database/JobDetailModal/etc.).
- Re-applied the clean epic slice from `191de65a`: four AST-1476 frontend files + AST-1474 `config.py` / `candidate.py` / `api_candidate.py` page-break catalog.
- Post-fix `git diff origin/dev -- src/` is again **7 files / +179** (same shape Radia marked clean at `191de65a`).

### fix-now — Scope gate / cross-epic contamination

- Tip no longer carries meteorite/inbox deletions vs `origin/dev`; AST-1476 footprint is the planned frontend + schema prereq only.
- Discuss (contact-row dropdown) / prior Joan advisories: no product change (accepted).

**fix-now:** all addressed.  
**Action:** §9a dry-run vs `origin/dev` and `origin/ftr/AST-1462-…`, then User Testing.

## Bug: AST-1489 — Print Resume ignores unsaved page-break dropdown

### As-is

After AST-1487, builder emit honors **saved** `page_break_policy` on `artifacts.resume_structure.sections[*]`, but Base Resume Content and JAR Job Resume **Print Resume** handlers only `GET` resume HTML built from the persisted candidate snapshot. Unsaved page-break dropdown edits live in page state (`allSections` / structure rows from `ArtifactEditor`) and never reach print until the operator clicks **Save sections**.

### To-be

Clicking **Print Resume** applies the operator’s current page-break dropdown choices (Keep block together / New page before / Flow uninterrupted) even when **Save sections** has not been clicked since the last edit — by auto-persisting the current structure rows (including `page_break_policy`) immediately before the existing validate-then-blob print `GET`. Susan approved widen-to-UI Option 1 on 2026-08-26.

### Repro

1. Open Artifacts → Base Resume Content for a candidate with printable saved base resume content and at least one enabled body section (e.g. Prior Experience).
2. Expand structure authoring; on a section header, change **Page break** from default to **New page before** (`page_break_before`). Do **not** click **Save sections**.
3. Click **Print Resume** (validate-then-blob opens HTML tab).
4. Inspect embedded `@media print` CSS in the returned HTML: section still uses prior persisted policy (e.g. `#prior-experience { page-break-inside: avoid; }` for default `avoid_split`) — not `#prior-experience { page-break-before: always; }`.
5. Repeat on JAR → Job Resume artifact tab: change page-break dropdown without Save sections → **Print Resume** → same mismatch.

Fixture-level check (no browser): with `allSections` holding `page_break_policy: "page_break_before"` for `prior_experience`, `handlePrint` issues `GET /candidate/resume/base?…` without a preceding `PUT /api/candidates/{id}/data` whose body includes that policy.

### Root cause

AST-1337 deliberately wired Print to **saved** server content only (`handlePrint` comment: “saved base via GET … (not editor buffer)”). AST-1476 added catalog-driven dropdown + **Save sections** PUT persistence but did not connect live structure rows to Print. `handlePrint` / `handlePrintResume` never read `allSections` and never PUT `resume_structure` before the resume HTML `GET`, so AST-1487’s builder fix is invisible until explicit Save sections.

### Proposed change

**Approach:** auto-save structure before print (no new API route, no builder change). Reuse the existing PUT shape from `saveStructure`; refactor to a shared async persist step both Save and Print can await.

**`src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx` — Hedy at make-fix:**

1. Extract page-local `persistStructureRows(rows: SectionRow[]): Promise<void>` from today’s `saveStructure` (~L99–136):
   - Guard: if `!selectedId`, reject with `Error("No candidate selected")`.
   - Build `sections` map exactly as today (`id`, `title`, `enabled`, `order`, `job_agent_editable`, `page_break_policy`, optional `format`).
   - `PUT /api/candidates/${selectedId}/data` with `{ artifacts: { resume_structure: { sections } } }`.
   - On `!r.ok`, parse JSON `error` and throw.
   - `GET /api/candidates/${selectedId}/resume_structure`, call existing `applyStructurePayload(data)` to refresh `allSections` / catalog from server.
   - Manage `structureSaving` / `structureError` in `.finally` / `.catch` (same as today).
   - **Do not** toast on success inside this helper.

2. Rewrite `saveStructure(rows)` to `void persistStructureRows(rows).then(() => setToast({ text: "Resume sections saved", variant: "success" })).catch(…)` — preserve today’s error toast + `structureError` behavior.

3. In `handlePrint` (~L139), after `selectedId` / `printing` guards and before the resume `GET`:
   - `await persistStructureRows(allSections)`.
   - On failure: set `printError`, error toast, `return` (no blob tab) — same failure posture as print fetch errors.
   - On success: proceed with existing validate-then-blob `GET /candidate/resume/base?candidate_id=…` flow unchanged.

4. Update the stale comment at ~L138: print **content** still comes from saved `base_resume`; **structure page-break policies** are auto-persisted from current editor rows immediately before the GET.

**`src/ui/frontend/src/components/JobAnalysisReportModal.tsx` — same pattern:**

1. Extract `persistStructureRows(rows: SectionRow[]): Promise<void>` mirroring Base (uses `selectedId`, same PUT + GET refresh, updates `allSections` / `structureSections` / `catalog` as today’s `saveStructure` ~L210–249).

2. Rewrite `saveStructure` to wrap persist + success toast.

3. In `handlePrintResume` (~L91), before `GET /candidate/resume/${jobId}`:
   - When `selectedId` is set, `await persistStructureRows(allSections)`; on failure toast and return without opening tab.
   - When `selectedId` is missing, skip persist (print uses server structure as today).

4. Add `selectedId` and `allSections` to the `useCallback` dependency array for `handlePrintResume`.

**`src/ui/frontend/src/components/ArtifactEditor.tsx` — optional:**

- **No change required** if both pages keep duplicate `persistStructureRows` (preferred — stays within minimal diff).
- Only touch if make-fix extracts a shared exported helper to avoid copy-paste; do **not** change dropdown UX, **Save sections** wiring, or content Save paths.

**Out of scope:** `src/core/builder.py`, `api_resume_html.py`, `config.py`, `candidate.py`, new routes, passing live structure in the print GET query/body.

**Tests (Betty at qa-fix / fix-board):**

- **Base:** In `test_ArtifactsBaseResumeContent.test.tsx`, add case: change page-break combobox to `page_break_before`, click **Print Resume** without **Save sections**; assert a structure `PUT` occurred with the new policy before the resume `GET`; optionally assert returned HTML print CSS reflects `page_break_before` (mock GET body).
- **JAR:** Parallel case in `test_JobAnalysisReportModal.test.tsx`.
- Update `docs/test-bible/frontend/pages.md` / component bible rows if manifest text references AST-1337 “saved only” for structure (content-only invariant remains).

### Blast radius

- **Extra PUT on every Print:** lightweight structure-only write; also persists any other unsaved structure row fields (title, order, enabled, format) — acceptable and keeps print aligned with the visible structure editor.
- **AST-1337 content invariant:** Print still uses saved **body** content (`base_resume` / job resume content), not the ArtifactEditor text buffer — only structure policies are auto-persisted pre-print.
- **Explicit Save sections:** unchanged UX + success toast; operators who Save then Print get two PUTs (harmless idempotent shape).
- **AST-1487:** builder already maps persisted policies; this bug completes the operator-facing loop.
- **Session / Cover Letter print paths:** untouched.

### What must still hold

- AST-1487 binding: structure-driven `@media print` CSS from `page_break_policy`; no hard-coded prior always-break.
- AST-1476: catalog-driven dropdown tokens/labels; invalid policy coerced to default in UI; JAR structure Save still targets candidate `resume_structure` (not job artifact).
- AST-1337 / AST-1350: validate-then-blob; no blank tab on print failure; auth `GET` routes unchanged; unsupported-experience API errors toast without tab.
- Content **Save** and JAR job-artifact body Save remain separate from structure Save.
- **Save sections** button continues to work with “Resume sections saved” success toast.
- No new config tokens or API contracts.
