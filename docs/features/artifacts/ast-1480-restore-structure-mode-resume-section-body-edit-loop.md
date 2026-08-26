# AST-1480 — Restore structure-mode resume section body edit loop

**Linear:** [AST-1480](https://linear.app/astralcareermatch/issue/AST-1480/restore-structure-mode-resume-section-body-edit-loop-resume-editor-is) (child of [AST-1459](https://linear.app/astralcareermatch/issue/AST-1459/resume-editor-is-not-working-properly))

**Publish ref:** `sub/AST-1459/AST-1480-restore-structure-mode-resume-section-body-edit-loop`

**Summary:** Operators see structure chrome (collapsible headers / AST-1323 authoring controls) on Base Resume Content and JAR Job Resume, but persisted section bodies are missing, empty, or not usable for edit→Save. This ticket restores the shared `ArtifactEditor` structure-mode load → body edit → Save loop for both candidate `artifacts.base_resume` and job `job_data.artifacts.resume_content`, without regressing structure header authoring, Experience job-array editing, or Cancel in-place reload (AST-1410).

---

## Explicit scope gate

Ticket **## Scope** (and parent Component/Technical scope partitioned onto this child) names:

- **Required:** `ArtifactEditor.tsx` — structure-mode load through `tabs[].content`, body edit gating, Save payload.
- **Conditional (only if repro needs them):** `LabeledTextArea.tsx`, `ExperienceJobsEditor.tsx`, `ArtifactsBaseResumeContent.tsx`, `JobAnalysisReportModal.tsx`, `App.css`.
- **Tests (Betty owns tree):** `test_ArtifactEditor.test.tsx`, `test_ArtifactsBaseResumeContent.test.tsx` if page wiring touched — engineer does **not** edit `tests/` or bible at build-child; note expected repro in Code Complete for Betty.

Every Files Changed row below is named in Scope. Stages must not invent `src/core/` or `src/ui/api/` work unless Stage 1 proves an API hydration bug — then **stop** and comment on the parent (AC 6 / `no-cross-contamination`).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/ArtifactEditor.tsx` | Split structure-mode **tab chrome** vs **section body** editability; fix structure-mode load guards/races so `tabs[].content` hydrates from candidate/job artifact blobs; keep Save for `fixedFields` / `jobPersistence`; preserve Experience unsupported path | ui |
| `src/ui/frontend/src/components/LabeledTextArea.tsx` | **Only if** bodies hydrate but stay non-interactive for a reason owned by this component (explicit `disabled` / missing `onChange` wiring). Prefer ArtifactEditor fix first | ui |
| `src/ui/frontend/src/components/ExperienceJobsEditor.tsx` | **Only if** Experience panels share the same empty/read-only failure after prose sections are fixed | ui |
| `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx` | **Only if** `structureSections` vs `allSections` / `handleStructureRowsChange` contributes to empty or non-editable bodies (e.g. tab key list diverges from `base_resume` keys incorrectly) | ui |
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | **Only if** JAR-only timing (`structureSections` fetch vs `jobPersistence` mount) blocks hydration after ArtifactEditor fix | ui |
| `src/ui/frontend/src/App.css` | **Only if** a rule blocks interaction or hides `.side-tab-textarea` / `.collapsible-panel-body` content in structure mode (no drive-by restyle) | ui |
| `tests/component/frontend/components/test_ArtifactEditor.test.tsx` | Betty at qa-child — structure-mode body display + edit + save; engineer must not edit | tests |
| `tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx` | Betty at qa-child — only if page wiring touched | tests |

**Out of scope:** craft-base generation, Print HTML, builder emit, `resume_structure` catalog schema, new API routes, tab add/remove/rename chrome in structure mode.

---

## Stage 1: ArtifactEditor — hydrate bodies + body editability (not tab chrome)

**Done when:** On a structure-mode mount with non-empty mocked/persisted section values, expanding a prose panel shows that text in `LabeledTextArea` and typing updates `tabs[].content`; Save still appears and PUTs the artifact dict; structure header controls remain; `editable`-gated tab rename / add / remove / rubric chrome stay **off** in structure mode; Experience valid arrays still use `ExperienceJobsEditor`, legacy non-array still shows the unsupported message + disabled textarea.

### 1.1 Diagnose against current code (read-only, then fix in this file)

Trace these paths in `ArtifactEditor.tsx` before changing behavior; the build agent must confirm which failure mode is live, then apply the matching fix below (do not skip diagnosis):

1. **Structure → fields:** `useCandidateResumeStructure` → `structureMode`; parent `structureSections` effect (~L413–430) and internal `resume_structure` fetch (~L433–446) → `shapeFields` / `fixedFields`.
2. **Load gates:** candidate load (~L531–543) and job load (~L517–528) both early-return when `(shapesKey \|\| structureMode) && !fixedFields`. Confirm they re-run once `fixedFields` is set and call `applyCandidateArtifactResponse` / `applyJobArtifactResponse` → `mapFixedFieldsFromRaw` → `tabs[].content` via `sectionValueToTabContent`.
3. **Edit gate:** `const editable = !shapesKey && !structureMode` (~L193). Today this correctly disables tab chrome and autosave, and prose `LabeledTextArea` still receives `onChange={v => updateTab(...)}` (~L1146). Confirm whether the live bug is (A) empty `tabs[].content` after load, (B) body controls non-interactive, (C) Save missing/broken, or (D) page/CSS outside this file — then fix (A)–(C) here; for (D) proceed to Stage 2.

⚠️ **Decision:** Prefer fixing shared gating/hydration inside `ArtifactEditor.tsx`. Do not add a new prop from pages for body editability unless Stage 1 cannot restore both Base and JAR surfaces.

### 1.2 Split chrome editability from body editability

In `ArtifactEditor.tsx`:

1. Keep structure mode disabling **tab chrome** (rename, add criterion, remove, reorder controls, rubric code/importance) via a clearly named flag derived from the current `editable` meaning, e.g. `tabChromeEditable = !shapesKey && !structureMode` (name is the implementer’s call; meaning is mandatory).
2. Introduce an explicit **body** affordance for structure / shapes / job fixed-field modes, e.g. `bodiesEditable = !!(fixedFields \|\| jobPersistence) && !inReview` (or equivalent that stays true in structure mode whenever fixed-field tabs are mounted and not in Generate review). Wire prose `LabeledTextArea` `onChange` and Experience `ExperienceJobsEditor` `onChange` through `bodiesEditable` (when false, use no-op / `disabled` only for the existing unsupported-experience path — do not disable happy-path bodies in structure mode).
3. Leave autosave gated on tab-chrome/`editable` semantics (`if (editable && !inReview)` ~L666) — structure mode continues to use **explicit Save**, not autosave (`pattern.ui.dirty-leave-save-then-navigate`).
4. Keep the Save/Cancel header branch that already shows when `fixedFields \|\| inReview \|\| jobPersistence` (~L943). Do not hide Save in structure mode.

### 1.3 Fix hydration races / guards that leave empty bodies

Still in `ArtifactEditor.tsx`, apply only what diagnosis requires:

1. If `mapFixedFieldsFromRaw` / `sectionValueToTabContent` drops persisted values for structure keys (dict or legacy `{label,content}[]`), fix mapping so each `fixedFields` key gets the matching artifact value into `tabs[].content`.
2. If structure-mode load returns early forever or remounts with empty tabs after `structureSections` updates, fix the effect dependencies / guards so a successful candidate GET or job GET always remaps once `fixedFields` is non-null. Do **not** clear `tabs` to empty placeholders after a successful hydrate when only structure header metadata changed.
3. Preserve AST-1410 Cancel: `handleCancel` must still re-GET and re-apply artifact response without full page reload on job and candidate paths.
4. Preserve Experience: `type: "experience_jobs"` on `experience` in structure `shapeFields`; valid arrays → `ExperienceJobsEditor`; `parseExperienceJobs` failure → unsupported message + disabled raw textarea; Save still aborts with that message.

### 1.4 Regression checklist (manual / existing component expectations)

After the edit, structure mode must still:

- Not call `/api/shapes/candidates` when `useCandidateResumeStructure` is set (existing AST structure tests).
- Show AST-1323 header controls when `structureCatalog` + `structureRows` + change/save callbacks are passed; **Save sections** remains separate from content Save.
- Expand-one policy for non-rubric rails (bodies may stay `hidden` until Expand — content must still be present in the DOM / appear after expand).

**Out of this stage:** edits under `ArtifactsBaseResumeContent.tsx`, `JobAnalysisReportModal.tsx`, `App.css`, `LabeledTextArea.tsx`, `ExperienceJobsEditor.tsx` unless diagnosis proved they are required — those are Stage 2.

---

## Stage 2: Conditional page / CSS / child-component wiring (skip if Stage 1 restores both ACs)

**Done when:** Either (a) Stage 1 alone satisfies Base Resume Content and JAR Job Resume ACs and this stage is a no-op commit skipped with a Linear stage comment stating “Stage 2 skipped — ArtifactEditor-only”, or (b) the minimal extra file(s) named below are patched and both surfaces hydrate + edit + Save.

⚠️ **Decision:** Skip entire Stage 2 when Stage 1 verification shows both surfaces working. Do not touch conditional files “for cleanliness.”

If Stage 1 leaves a gap, apply **only** the matching branch:

1. **`ArtifactsBaseResumeContent.tsx`** — If `handleStructureRowsChange` remapping `structureSections` to **all** rows (including disabled) blanks or desyncs body tabs relative to `artifacts.base_resume`, keep tab field keys aligned with enabled (or hydrated) section ids for body load while `structureRows` / `allSections` remain the authoring list. Do not change Print, accent bar, or structure PUT shape.
2. **`JobAnalysisReportModal.tsx`** — If JAR alone fails because `ArtifactEditor` mounts before `structureSections` is ready or remounts wipe job hydrate, align fetch/mount so `useCandidateResumeStructure` + `structureSections` + `jobPersistence` are present together for `use_resume_structure` artifact tabs. Do not change Generate/Cancel artifact strip or non-structure artifact tabs.
3. **`LabeledTextArea.tsx` / `ExperienceJobsEditor.tsx`** — Only if ArtifactEditor already passes interactive handlers but the child forces `disabled` or drops `onChange` in the structure-mode happy path.
4. **`App.css`** — Only if a rule sets `pointer-events: none`, zero height, or `visibility`/`display` that hides `.collapsible-panel-body .side-tab-textarea` (or experience editor) in structure mode. Narrow the fix; do not restyle the stack.

If the gap is server-side (candidate/job GET omits `base_resume` / `resume_content` that exists in DB), **stop** — comment on parent AST-1459 with the 🛑 Stage blocked format; do not invent API changes under this ticket.

---

## Stage 3: Compile and lint (product only)

**Done when:** Frontend TypeScript build and lint for touched UI files succeed on the epic worktree; no `tests/` or bible edits in the engineer commit(s).

1. From `src/ui/frontend`, run the repo’s usual compile/lint for the touched TS/TSX (and CSS if Stage 2 touched it).
2. Fix any type/lint errors introduced by this ticket only.
3. In the Code Complete / stage comment trail, name the failure mode found in §1.1 (A/B/C/D) and which files landed, so Betty can target `test_ArtifactEditor.test.tsx` (and page test if Base wiring changed) for structure-mode body display + edit + Save on both persistence paths.

---

## Estimate

Confirm Chuckles estimate: 3 — agree

Single shared component vertical slice (load/edit/save) with known patterns; conditional page/CSS only if needed; no schema/API by default.

---

## Review

**Publish ref:** `origin/sub/AST-1459/AST-1480-restore-structure-mode-resume-section-body-edit-loop` @ `b16a93d3`

**Built:** Stage 1 only in `ArtifactEditor.tsx` — diagnosis **(A)** empty/stale bodies from label-churn re-GET + weak dict coerce, plus **(B)** chrome vs body edit split. Stage 2 skipped (no page/CSS/LabeledTextArea/ExperienceJobsEditor edits). Frontend-only (AC6).

**Betty:** Lock `test_ArtifactEditor.test.tsx` structure-mode + jobPersistence body display/edit/Save; include `job_resume` key with `resume_content` sibling if covering JAR pin overlay.

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1480
**Overall:** APPROVED
**Publish ref:** `sub/AST-1459/AST-1480-restore-structure-mode-resume-section-body-edit-loop` @ `9ca35357`

## Traceability
AC1–AC2 → Stage 1 (ArtifactEditor hydrate + body/chrome split) + Stage 2 conditional page/modal/CSS only if diagnosis proves (D); AC3 → Stage 1 §1.4 regression (AST-1323 headers + Save sections); AC4 → Stage 1 §1.3.4 Experience path + Stage 2 branch 3 if needed; AC5 → Stage 3 compile/lint + Code Complete handoff to Betty (engineer defers `tests/` per scope gate); AC6 → Explicit scope gate + Stage 2 🛑 stop (no `src/core/` / `src/ui/api/` without Susan).

## Findings

### discuss
- **Location:** Child Citations / parent Architectural definition — `pattern.ui.in-place-live-refresh`
- **Finding:** Catalog entry is still `status: proposed`, not `approved`, yet cited under “Patterns to reuse.”
- **Recommendation:** Not blocking — Stage 1.3 explicitly preserves AST-1410 Cancel re-GET (matches the pattern’s solution shape); plan does not invent new refresh semantics. Archie may approve the pattern id separately; optional hygiene swap to AST-1410 canonical refs only.

### acceptable
- **Location:** Files Changed — `tests/component/...` rows
- **Finding:** Test files listed as modified while engineer is barred from touching `tests/` at build-child.
- **Recommendation:** Correct for this workflow — Betty owns test-tree at qa-child; Stage 3 names failure mode (A/B/C/D) for targeting.

**Considered (in-session):** Universal orch.* statutes — conforms (plan doc only, no git/test-tree violations). Scoped ui-layer statutes (`astral.layers.import-direction`, `astral.ui.frontend-file-placement`, `astral.standards.in-scope-only`, `astral.standards.no-cross-contamination`, `astral.layers.ui-config-driven-business-logic`, `astral.git.engineer-test-tree-ban`) — conforms. `pattern.ui.admin-endpoint` — conforms (existing GET/PUT, no new routes). Proposed patterns (`in-place-live-refresh`, `dirty-leave-save-then-navigate`) — behavior described inline; see discuss above.

context_tokens≈42000

## Radia review

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1480
**Publish ref:** `origin/sub/AST-1459/AST-1480-restore-structure-mode-resume-section-body-edit-loop` @ `bcc05032`
**Overall:** FIX-NOW

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | no agent/LLM paths in diff |
| astral.agent.do-task-delegation | scoped | not-applicable | no dispatcher/do_task changes |
| astral.agent.grade-vector-validation | scoped | not-applicable | no grade-vector paths |
| astral.batch.batch-id-first | scoped | not-applicable | no batch layer |
| astral.batch.batch-id-format | scoped | not-applicable | no batch layer |
| astral.batch.claim-process-release | scoped | not-applicable | no batch layer |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | no batch layer |
| astral.config.config-source-of-truth | scoped | not-applicable | no config.py changes |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | no secrets/env wiring |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no debug/artifacts dir |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | no debug/ spikes |
| astral.dispatch.seed-auto-false | scoped | not-applicable | no dispatch/seed paths |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | no run_next changes |
| astral.docs.features-single-file-per-ticket | scoped | conforms | issue doc at planned path |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty test/bible commits; engineer `code()` is `src/ui` only |
| astral.git.engineer-test-tree-ban | scoped | conforms | engineer commit `b16a93d3` did not touch `tests/` |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | ui-only diff |
| astral.layers.import-direction | scoped | conforms | `ArtifactEditor.tsx` stays frontend; no `src.data` / `src.external` imports |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no scripts layer |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | structure formats/catalog still server-driven; no new inline allowlists |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | no coat-check paths |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | no render_verdict/consult |
| astral.idioms.require-auth-on-protected-endpoints | scoped | conforms | reuses existing authenticated GET/PUT; no new routes |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | no seed tables |
| astral.seed.archie-catalog-wins | scoped | not-applicable | no seed/catalog edits |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | no seed boot paths |
| astral.seed.define-approved | scoped | not-applicable | no define/seed |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | no seed rows |
| astral.seed.other-via-coverage-join | scoped | not-applicable | no seed coverage |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | no data layer |
| astral.standards.database-header-inventory | scoped | not-applicable | no database/migrations |
| astral.standards.debug-contract-gated | scoped | not-applicable | no backend debug emission |
| astral.standards.dry-and-focused-functions | scoped | conforms | focused vertical slice; label-sync effect is ticket-scoped |
| astral.standards.in-scope-only | scoped | conforms | `ArtifactEditor.tsx` + Betty tests/bible; Stage 2 skipped as planned |
| astral.standards.logging-via-utils | scoped | not-applicable | no logging added |
| astral.standards.names-not-ticket-ids | scoped | conforms | no ticket-id symbols in product code |
| astral.standards.no-cross-contamination | scoped | conforms | no `src/core/` or `src/ui/api/` creep |
| astral.standards.no-hardcoded-sets | scoped | conforms | structure field keys from props/catalog, not new TSX sets |
| astral.standards.public-then-helpers | scoped | conforms | helpers unchanged; new effect is local |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | no utils layer |
| astral.state.core-decides-transitions | scoped | not-applicable | no state transitions |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no job state machine |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no run/daisy-chain |
| astral.ui.frontend-file-placement | scoped | conforms | component edit under `components/` |
| astral.ui.naming-conventions | scoped | conforms | `tabChromeEditable` / `bodiesEditable` naming is clear |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no server/worker config |
| orch.git.betty-merge-tests-one-sha | universal | conforms | `merge-tests(AST-1480)` at tip |
| orch.git.commit-vocabulary | universal | conforms | `code` / `test` / `docs` / `merge-tests` vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | child `sub/` off epic parent |
| orch.git.ftr-sub-topology | universal | conforms | publish ref matches child topology |
| orch.git.merge-on-checkout | universal | conforms | no rebase; merge-tests pattern |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | no forbidden git ops in diff |
| orch.git.no-dev-agent-branches | universal | conforms | `sub/AST-1459/...` publish ref |
| orch.git.one-epic-worktree-per-parent | universal | conforms | review in `astral-AST-1459/` |
| orch.git.three-permanent-branches | universal | conforms | diff vs `origin/dev` only |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | no product-policy invention |
| orch.pipeline.plan-is-bible | universal | conforms | implementation tracks Stage 1 plan; Stage 2 correctly skipped |
| orch.pipeline.project-scoped-queues | universal | conforms | scoped child review |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | no statute edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty landed tests + bible manifest |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | n/a to code diff |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada assignee; review is read-only |
| orch.roles.pre-commit-path-bans | universal | conforms | no banned-path commits observed |

**Active set scored:** 65 / 65 (per `canon/statutes/README.md` harvested corpus).

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.ui.dirty-leave-save-then-navigate | needs-discussion | cited in plan; catalog `status: proposed` — behavior matches (explicit Save, autosave gated on `tabChromeEditable`) |
| pattern.ui.in-place-live-refresh | needs-discussion | Joan carry-forward — proposed; Cancel re-GET preserved, no new refresh hook |
| pattern.ui.admin-endbound | not cited | — |
| none other cited | — | Joan noted `pattern.ui.admin-endpoint` intent only |

## Plan adherence

- **Stage 1 delivered:** `ArtifactEditor.tsx` only — chrome/body split (`tabChromeEditable` / `bodiesEditable`), `fixedFieldKeys` load guards, label-only label sync effect, dict coerce hardening, `job_resume` → `resume_content` sibling overlay (JAR). Diagnosis **(A)+(B)** documented in issue doc matches diff.
- **Stage 2 skipped:** no page/CSS/LabeledTextArea/ExperienceJobsEditor edits — correct per plan.
- **Estimate 3:** footprint matches (single shared component + Betty tests).
- **Betty manifest:** three `AST-1480` repro tests + bible block align with Code Complete handoff; regression pointers to AST-553 / AST-1410 reasonable.
- **Joan:** APPROVED @ `9ca35357`; no Excluded-statute straggler. Proposed-pattern discuss carries forward.

## Findings

### fix-now

- **Location:** `src/ui/frontend/src/components/ArtifactEditor.tsx` ~L298, ~L1204–L1216 (`bodiesEditable`, `LabeledTextArea` / `ExperienceJobsEditor` wiring)
- **Finding:** `bodiesEditable = !!(fixedFields || jobPersistence) && !inReview` **does not include rubric/free-form mode**. When `fixedFields` is null and `jobPersistence` is absent (e.g. `artifactKey="rubric"`, `joblist_rubric`, criteria pages), `bodiesEditable` is `false` while `tabChromeEditable` is `true`. Prose bodies get `disabled={!bodiesEditable}` and no-op `onChange` — **criterion body editing is locked** outside structure/shapes/job-fixed-field paths. Pre-change code used the same `editable` flag for bodies and chrome, so rubric bodies stayed interactive.
- **Severity:** B — functional regression on a major shared editor surface; manifest does not assert rubric body edit persistence (existing `joblist_rubric` expand-one test types into a field but does not assert content change).
- **Recommendation:** Extend the gate, e.g. `const bodiesEditable = !inReview && (tabChromeEditable || !!fixedFields || !!jobPersistence)` (or equivalent that preserves structure-mode chrome lock while restoring rubric/shapes-adjacent free-form bodies). Add/extend a component test that types into a rubric body and asserts PUT payload.

### discuss

- **Location:** Plan / Joan verdict — `pattern.ui.in-place-live-refresh`, `pattern.ui.dirty-leave-save-then-navigate`
- **Finding:** Both remain `status: proposed` in catalog while cited under patterns to reuse.
- **Recommendation:** Joan already accepted behavior inline; optional Archie approval or swap to AST-1410 canonical refs. Not blocking once `bodiesEditable` is fixed.

### advisory

- **Location:** `ArtifactEditor.tsx` load effects ~L578, ~L595 — `eslint-disable-next-line react-hooks/exhaustive-deps`
- **Finding:** Intentional omission of `fixedFields` from deps in favor of `fixedFieldKeys`; comment explains label-churn rationale. Acceptable if `resolve-child` keeps the comment.
- **Location:** Betty manifest — `tests/component/frontend/components/test_ArtifactEditor.test.tsx`
- **Finding:** AST-1480 coverage is strong for structure/job paths; no rubric-body regression guard for the chrome/body split. Recommend one line in manifest after fix.

## Frame diff

vs issue doc **Review** stub @ `b16a93d3` (engineer `code()` only):

| Path | Δ since stub |
|------|----------------|
| `src/ui/frontend/src/components/ArtifactEditor.tsx` | unchanged since `b16a93d3` |
| `tests/component/frontend/components/test_ArtifactEditor.test.tsx` | +186 lines — 3 `AST-1480` tests (label-churn, JAR sibling overlay, chrome off / bodies on) |
| `docs/test-bible/frontend/components.md` | +32 lines — AST-1480 manifest block |
| `docs/features/artifacts/ast-1480-…md` | plan/review sections (docs trail) |
| tip | `bcc05032` merge-tests(AST-1480) |

## What's solid

- Structure-mode fix logic is sound: `fixedFieldKeys` prevents label-only re-GET wipes; label-sync effect preserves `tabs[].content`; dict coerce rejects pin strings; JAR `job_resume`/`resume_content` overlay matches Betty handoff.
- Scope discipline: ArtifactEditor-only product change; no API/core creep.
- AST-1480 tests directly exercise the reported failure modes (A)/(B).

## Recommended actions (downstream — not executed here)

1. **resolve-child:** fix `bodiesEditable` formula + rubric regression test.
2. **Chuckles:** append this artifact to issue doc; post slim upshot; → **Review Posted** after writeback (C7 complete).
3. **Optional:** Archie pattern-id hygiene per Joan discuss.

## Notes

- Joan plan-rubric verdict attached (APPROVED). No excluded-statute straggler.
- §5f / §5g not triggered (frontend-only; no `debug=` or LLM external changes).
- Trust spawn prompt: Tests Passed @ Ada assignee.

context_tokens≈55000

---

## Resolution

**Date:** 2026-08-25  
**vs Radia review** @ `f899a95d` (`FIX-NOW bodiesEditable`)

### fix-now — addressed (product)

- **`bodiesEditable`** in `ArtifactEditor.tsx` now:  
  `!inReview && (tabChromeEditable || !!fixedFields || !!jobPersistence)`  
  Restores rubric/free-form body editing while keeping structure-mode chrome locked and bodies on when `fixedFields` / `jobPersistence` are set.

### fix-now — test-tree (Betty)

- Rubric body type → PUT regression: Betty landed `AST-1480: rubric free-form body edit PUTs edited content` + bible line; `merge-tests` @ `c109a45d`. Ada re-ran full AST-1480 manifest — **6 green** (4× AST-1480 + AST-553 job persistence + AST-1410 Cancel).

### discuss / advisory

- Proposed-pattern citations — no change (Joan already non-blocking).  
- `eslint-disable` on load deps — kept with existing comment.

## Threads (generated — epic_registry mirror)

_(generated from epic registry — do not hand-edit; edits are overwritten)_

### Team

| Agent | Role | Thread |
|--------|-------|--------|
| Ada | engineer | `/home/susan/.cursor/chats/8988639e5c4a792e44df3cc01f98d553/c257fbde-dbf6-48b7-b2b6-5dc1ccc0cec1/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/3d4b688a-ff4c-4d02-a06a-f2593def0f9d/store.db` |
| Radia | review | `/home/susan/.cursor/chats/8988639e5c4a792e44df3cc01f98d553/8aaddc49-079d-4ab7-ba91-3e3305120e43/store.db` |

### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-1459 (parent) | ftr/AST-1459-resume-editor-is-not-working-properly |
| AST-1480 | sub/AST-1459/AST-1480-restore-structure-mode-resume-section-body-edit-loop |

**Epic worktree:** `astral-AST-1459/` — one active sub checked out at a time.
