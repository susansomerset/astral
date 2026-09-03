# patt.artifacts.ui-consistency + shape-standardized base_resume editor

**Linear:** [AST-1577](https://linear.app/astralcareermatch/issue/AST-1577)
**Parent:** [AST-1569](https://linear.app/astralcareermatch/issue/AST-1569) — Implement patt.artifact.write-operative
**Publish ref:** `sub/AST-1569/AST-1577-ui-consistency-base-resume-editor`

Author draft `patt.artifacts.ui-consistency` and refactor the base-resume editor path so `ArtifactEditor` / `ArtifactsBaseResumeContent` are parameterized by catalog `body_shape` `resume_content`, save via the existing candidate data API, and reload the operative current body (hydrate already shipped by sibling AST-1576). Does **not** own data-layer / agent craft-persist / `artifact_catalog` deletion.

## Explicit scope gate

Ticket **## Scope** names exactly:

- `canon/directives/draft/patt.artifacts.ui-consistency.md` (**new**)
- `src/ui/frontend/src/components/ArtifactEditor.tsx`
- `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx`

Every row in **Files Changed** is one of those paths (plus this plan doc). Every Stage step is the kind of change Scope describes for that file.

**Out of this ticket (do not touch):** `src/data/**`, `src/core/**`, `src/utils/config.py` / `ARTIFACT_CONFIG`, `src/ui/api/**`, other artifact pages (rubric editors), `JobAnalysisReportModal.tsx`, job finalize / grade pin / coat-check, new catalog keys, cross-links from `patt.artifact.write-operative.md` into ui-consistency (or the reverse).

**Depends on sibling AST-1576 (done on this epic tip):** PUT `artifacts.base_resume` → operative `save_candidate_data`; GET overlays `candidate_data.artifacts.base_resume` from `get_current_artifact`. Frontend keeps the leaf slot key `base_resume` in the JSON body; do not invent a new API field.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `canon/directives/draft/patt.artifacts.ui-consistency.md` | **New** draft pattern: editors standardized on catalog `body_shape`; same shape shares editor path; pilot `resume_content` | canon |
| `src/ui/frontend/src/components/ArtifactEditor.tsx` | Add `bodyShape` prop; `resume_content` drives structure-dict editor mode; keep `useCandidateResumeStructure` for out-of-scope callers | ui |
| `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx` | Wire `bodyShape="resume_content"`; keep leaf `artifactKey="base_resume"` + candidate data save/load | ui |

## Stage 1: Draft `patt.artifacts.ui-consistency`

**Done when:** `canon/directives/draft/patt.artifacts.ui-consistency.md` exists on the publish ref with frontmatter + Abstract / Arc / Applications / Exceptions / Implementation / OPEN QUESTIONS; it mandates body_shape-driven editors; it does **not** link to or cite `patt.artifact.write-operative` by id/path; Archie approval before active is stated.

1. Create `canon/directives/draft/patt.artifacts.ui-consistency.md` using the same draft shape as sibling drafts under `canon/directives/draft/` (YAML frontmatter + numbered sections). Frontmatter:

```yaml
---
id: patt.artifacts.ui-consistency
kind: pattern
scope: [src/ui/frontend/src/components/ArtifactEditor.tsx, src/ui/frontend/src/pages]
point: >
  Parameterize artifact editors by catalog body_shape so same-typed bodies share one UI path.
---
```

2. **Abstract** (one short block): UI editors for versioned artifact bodies select their layout and payload shape from the catalog entry’s `body_shape` (into `BUILD_CONFIG["artifact_shapes"]`), not from one-off per-key forks. Artifacts that share a `body_shape` reuse the same editor component path. Persist and reload go through the entity’s existing candidate/job data API contracts for that leaf slot; the client does not invent parallel storage keys.

3. **Arc:**
   - **Before** — Catalog registers `body_shape` on the key (SoT in config; not this pattern’s register step).
   - **During** — Page passes `bodyShape` (and leaf `artifactKey` for the API slot) into the shared editor; editor renders the shape’s field/structure UI; Save PUTs the body under the leaf artifacts key; GET reloads the current body for that leaf.
   - **After** — Another key with the same `body_shape` can reuse the same editor props pattern without a new component fork.

4. **Applications:**
   1. Candidate Base Resume Content page — pilot `body_shape` `resume_content`, leaf `base_resume`.
   2. Future same-shape candidate or job editors (reuse the shared component; out of this ticket’s product edits).

5. **Exceptions:**
   1. **Rubric / criteria chrome** — criteria arrays with add/remove/importance are not `resume_content`; they keep the existing rubric editor mode until a separate shape registers them.
   2. **Job Analysis Report Modal / other job tabs** — may keep legacy props until a job-editor ticket adopts `bodyShape`; this pattern does not require rewriting them in the pilot ticket.
   3. **Non-artifact forms** (session paste, admin tools) — out of scope.

6. **Implementation** (normative for implementers of this pattern):
   1. **Select shape** — Page reads the catalog key’s `body_shape` (pilot hardcodes the known literal `resume_content` matching `ARTIFACT_CONFIG["candidate.artifacts.base_resume"]["body_shape"]` — do not add frontend catalog fetch this ticket).
   2. **Pass props** — Shared `ArtifactEditor` receives `bodyShape` plus the API leaf `artifactKey` (pilot: `base_resume`) and craft `taskKey` when Generate applies.
   3. **Render** — For `resume_content`: structure-driven section tabs + dict payload (experience as `experience_jobs` when section id/type says so). Do not fork a second base-resume-only component.
   4. **Load** — GET entity detail; map `candidate_data.artifacts[artifactKey]` (or job equivalent) into tabs. Empty/missing → empty sections, not a client-side blob invent.
   5. **Save** — PUT entity data with `{ artifacts: { [artifactKey]: dictPayload } }` via existing candidate/job API. Do not add a one-off `artifact_id` field on the client.
   6. **Verify** — Save then reload (or use PUT response body) shows the same section bodies the operator just saved.

7. **OPEN QUESTIONS / DECISIONS:**
   1. Whether the frontend later fetches `ARTIFACT_CONFIG` / shapes via a system endpoint instead of page-level literals — default no until a catalog-UI ticket; pilot pages may hardcode `bodyShape="resume_content"` matching config.
   2. Job editors adopting the same prop — separate tickets; pattern only requires reuse readiness on `ArtifactEditor`.

8. **Hard bans in the draft body:**
   - Do **not** mention or link `patt.artifact.write-operative` (id, path, or “see write-operative”).
   - Do **not** add cross-links into `patt.artifact.write-operative.md`.
   - Do **not** register new `ARTIFACT_CONFIG` keys or change config from this file.

⚠️ **Decision:** Pattern id is `patt.artifacts.ui-consistency` (plural `artifacts`) per parent / child ticket naming — not `patt.artifact.ui-consistency`.

## Stage 2: Parameterize `ArtifactEditor` + wire Base Resume page

**Done when:** Base Resume Content passes `bodyShape="resume_content"`; `ArtifactEditor` treats that as structure-dict mode equivalent to today’s `useCandidateResumeStructure`; save still PUTs `artifacts.base_resume`; load still reads that leaf (operative overlay from AST-1576); `useCandidateResumeStructure` still works for `JobAnalysisReportModal` without editing that file; no new `ARTIFACT_CONFIG` keys; TypeScript build of the frontend succeeds.

1. In `src/ui/frontend/src/components/ArtifactEditor.tsx`, extend `ArtifactEditorProps`:

```ts
/** Catalog body_shape (BUILD_CONFIG artifact_shapes / ARTIFACT_CONFIG). Pilot: resume_content. */
bodyShape?: string
```

Keep existing `useCandidateResumeStructure?: boolean` unchanged in the public props surface.

2. Replace the structure-mode derivation with:

```ts
const structureMode =
  !!useCandidateResumeStructure || bodyShape === "resume_content"
```

All existing `structureMode` call sites (tab chrome, shape fields from structure rows/sections, load gates, payload dict path) stay as they are — only the boolean source widens.

3. Replace the hard-coded leaf check for the unsupported-experience Generate escape:

```ts
// was: artifactKey === "base_resume"
&& (bodyShape === "resume_content" || artifactKey === "base_resume")
```

Keep `!jobPersistence` and the rest of `baseResumeUnsupportedEscape` / `canGenerate` logic intact. Do **not** change rubric Generate, chain handoff, or jobPersistence save paths.

4. Destructure `bodyShape` in the component signature (default `undefined`). Add a one-line comment at the prop: AST-1577 / `patt.artifacts.ui-consistency` — structure-dict mode by shape.

5. In `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx`, on the `<ArtifactEditor …>` call:

- Add `bodyShape="resume_content"`.
- Remove `useCandidateResumeStructure` from **this page only** (structure mode now comes from `bodyShape`).
- Keep `artifactKey="base_resume"`, `taskKey="craft_resume_base"`, structure authoring props, Print `headerActions`, accent bar, and structure save helpers exactly as they are (still PUT `resume_structure` / leaf body via `/api/candidates/${id}/data`).

6. Do **not** edit `JobAnalysisReportModal.tsx` or rubric artifact pages. Do **not** change API routes. Do **not** add frontend fetches of `ARTIFACT_CONFIG`.

7. From `src/ui/frontend`, run the project TypeScript check the repo already uses (`npx tsc --noEmit` or `npm run build` — whichever the frontend `package.json` scripts expose for typecheck/build). Fix only type errors introduced by the new prop in the two Scope files.

⚠️ **Decision:** Leaf API key remains `base_resume` (matches AST-1576 hydrate/save slot). `bodyShape` selects UI mode; it is not the JSON artifacts key. Catalog full key `candidate.artifacts.base_resume` stays backend/config SoT — frontend pilot does not switch PUT/GET to the dotted catalog string.

## Estimate

Confirm Chuckles estimate: 3 — agree

Pattern draft + two React files on an existing editor path; sibling already owns operative save/hydrate. Not 2 because the pattern must be detailed enough for Archie approval and the editor prop contract must preserve JAR backward compat without touching that file.


## Joan validate

```
[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1577
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1569/AST-1577-ui-consistency-base-resume-editor` @ `5cdee55b020c817921373cc4751c1ff494699bbd`

## Traceability
AC6→S2 (`bodyShape="resume_content"` + leaf `base_resume` save/load via existing candidate API; operative hydrate from merged AST-1576 on GET/reload); AC7→S1 (new draft pattern, explicit no cross-link to write-operative); AC8→S1 hard bans + explicit OOS (no new catalog keys / coat-check / grade pins / backend edits).

## Findings
(none — no fix-now; no discuss blockers)

**Considered (in-session):** Universal orch.* set + scoped statutes matching plan layers `{ui, docs}` and paths (`src/ui/frontend/**`, canon draft) — all `conforms` (scope gate matches child `## Scope` exactly; `bodyShape` prop preserves `useCandidateResumeStructure` for `JobAnalysisReportModal` without editing that file; layer imports unchanged; pilot literal `resume_content` matches parent-approved pattern shape; AST-1576 is ancestor on publish ref so operative save/hydrate dependency is satisfied).

context_tokens≈52000
```

## Review (build)

**Built @ `8f0b8a46`** — `origin/sub/AST-1569/AST-1577-ui-consistency-base-resume-editor`

Stages 1–2 landed: draft `patt.artifacts.ui-consistency.md` (no write-operative cross-link); `ArtifactEditor` `bodyShape` + Base Resume page `bodyShape="resume_content"` (leaf `base_resume` unchanged; `useCandidateResumeStructure` retained for JAR).

## Radia review

```
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1577
**Publish ref:** `origin/sub/AST-1569/AST-1577-ui-consistency-base-resume-editor` @ `07f5a248da40078a35f399e20c8338a0d9992e0d`
**Overall:** CLEAN

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| orch.git.betty-merge-tests-one-sha | universal | conforms | Tip is `merge-tests(AST-1577)` @ `4c1689b8`; Betty frontend test/bible deltas at one SHA |
| orch.git.commit-vocabulary | universal | conforms | `code` / `test` / `docs` / `merge-tests` vocabulary on branch |
| orch.git.flow-direction-inviolable | universal | conforms | Sub publish ref; no reverse-merge mechanics in product |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1569/AST-1577-ui-consistency-base-resume-editor` |
| orch.git.merge-on-checkout | universal | conforms | N/A to code content |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No cherry-pick/rebase/force in diff |
| orch.git.no-dev-agent-branches | universal | conforms | No agent-named branches |
| orch.git.one-epic-worktree-per-parent | universal | conforms | AST-1569 epic worktree |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | No unresolved product-policy forks |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–2 match AST-1577 engineer commits |
| orch.pipeline.project-scoped-queues | universal | conforms | N/A to code content |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Review at Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | Draft pattern states Archie approval required before active |
| orch.roles.betty-owns-test-tree | universal | conforms | Frontend tests/bible via Betty `test(AST-1577)` + merge-tests |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | N/A to code content |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Katherine assignee at Tests Passed |
| orch.roles.pre-commit-path-bans | universal | conforms | No hook bypass |
| astral.agent.confidence-bounds | scoped | not-applicable | No agent-layer changes in AST-1577 commits |
| astral.agent.do-task-delegation | scoped | not-applicable | No agent changes in AST-1577 commits |
| astral.agent.grade-vector-validation | scoped | not-applicable | No grade-vector paths |
| astral.batch.batch-id-first | scoped | not-applicable | No batch changes |
| astral.batch.batch-id-format | scoped | not-applicable | No batch id changes |
| astral.batch.claim-process-release | scoped | not-applicable | No claim helpers |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | No entity-response retention |
| astral.config.config-source-of-truth | scoped | conforms | Pilot `bodyShape="resume_content"` matches config `body_shape`; leaf key `base_resume` unchanged; no frontend catalog fetch |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | No secrets surface |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | No debug dir changes |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | No spike files |
| astral.dispatch.seed-auto-false | scoped | not-applicable | No dispatch seed |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | No run_next edits |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Single plan doc `ast-1577-ui-consistency-base-resume-editor.md` |
| astral.git.betty-no-src-or-features | scoped | not-applicable | Betty changes are tests/bible only |
| astral.git.engineer-test-tree-ban | scoped | conforms | AST-1577 `code()` commits touch only scoped frontend + canon draft |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | No core/external changes in AST-1577 commits |
| astral.layers.import-direction | scoped | conforms | Frontend diff adds no `src/data` / `src/core` imports |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | No scripts changes |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | Plan-approved pilot literal `resume_content`; no new state-string lists in React |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | Coat-check untouched |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | No render-verdict changes |
| astral.idioms.require-auth-on-protected-endpoints | scoped | not-applicable | No API route changes in AST-1577 commits |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | No seed JSON |
| astral.seed.archie-catalog-wins | scoped | not-applicable | No seed catalog |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | No seed boot |
| astral.seed.define-approved | scoped | not-applicable | No define work |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | No operator rows |
| astral.seed.other-via-coverage-join | scoped | not-applicable | No coverage join |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | No data-layer changes in AST-1577 commits |
| astral.standards.database-header-inventory | scoped | not-applicable | No config header edits in AST-1577 commits |
| astral.standards.debug-contract-gated | scoped | not-applicable | No backend debug surfaces in AST-1577 commits |
| astral.standards.dry-and-focused-functions | scoped | conforms | Minimal prop widening; no editor fork |
| astral.standards.in-scope-only | scoped | conforms | Engineer commits: canon draft + 2 frontend files only; backend in three-dot diff is sibling AST-1576 ancestry |
| astral.standards.logging-via-utils | scoped | not-applicable | No new runtime logging in frontend diff |
| astral.standards.names-not-ticket-ids | scoped | conforms | `bodyShape` / `resume_content` are domain names |
| astral.standards.no-cross-contamination | scoped | conforms | Rubric/jobPersistence paths unchanged; JAR keeps `useCandidateResumeStructure` |
| astral.standards.no-hardcoded-sets | scoped | conforms | Pilot literal permitted per plan OPEN QUESTIONS §1 |
| astral.standards.public-then-helpers | scoped | conforms | Public `ArtifactEditor` prop; page wires it |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | No utils changes in AST-1577 commits |
| astral.state.core-decides-transitions | scoped | not-applicable | No state transition changes |
| astral.state.job-prior-states-enforced | scoped | not-applicable | No job-state changes |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | No run-chain edits |
| astral.ui.frontend-file-placement | scoped | conforms | Changes only under `src/ui/frontend/src/components/` and `pages/` |
| astral.ui.naming-conventions | scoped | conforms | `bodyShape` camelCase prop; no new file naming violations |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | No server config |

**Sweep count:** 65 active statutes scored in-session (18 universal + 47 scoped).

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| `patt.artifacts.ui-consistency` (new draft) | conforms | Draft landed with required sections; `bodyShape` prop + Base Resume wiring; no `write-operative` cross-link |
| none cited as approved `canon/patterns/**` | — | Draft-directive citation per parent/child naming; Joan closed at plan validate |

## Plan adherence

**Stage 1** — `canon/directives/draft/patt.artifacts.ui-consistency.md` created with frontmatter (`id: patt.artifacts.ui-consistency`), Abstract/Arc/Applications/Exceptions/Implementation/OPEN QUESTIONS, Archie-approval note, and zero `write-operative` mentions (verified).

**Stage 2** — `ArtifactEditor` gains optional `bodyShape`; `structureMode = useCandidateResumeStructure || bodyShape === "resume_content"`; `baseResumeUnsupportedEscape` widened per plan; `ArtifactsBaseResumeContent` passes `bodyShape="resume_content"` and drops `useCandidateResumeStructure` on this page only; `JobAnalysisReportModal.tsx` untouched (still `useCandidateResumeStructure`). Save still PUTs `artifacts.base_resume` leaf; no new API fields or `ARTIFACT_CONFIG` frontend fetch.

**Dependency** — Sibling AST-1576 operative save/hydrate is on branch ancestry (required for Save→reload); not introduced by AST-1577 engineer commits.

**Estimate 3** — still fits (draft + two React files + Betty tests).

**Cross-ticket boundaries** — No backend/core/api/config edits in AST-1577 `code()` commits; rubric editors and JAR deferred per plan.

## Findings

(none — no fix-now; no discuss blockers)

### advisory — three-dot diff includes full AST-1576 backend stack

- **Location:** `git diff origin/dev...origin/sub/AST-1569/AST-1577-*` (25 files)
- **Finding:** Three-dot diff vs `origin/dev` includes AST-1576 product (`src/core/**`, `src/data/**`, `src/ui/api/**`, etc.) because sibling landed on the same epic tip before `dev` absorbs the parent. AST-1577 engineer commits (`93b4d953`, `8f0b8a46`) touch only canon draft + 2 frontend files.
- **Recommendation:** Not an AST-1577 scope violation. **Chuckles/merge-child:** expect diff to shrink once AST-1576 is on `origin/dev` or ftr merges in blockedBy order. Do not ask resolve-child to re-review 1576 backend here.

### advisory — dual trigger for unsupported-experience Generate escape

- **Location:** `ArtifactEditor.tsx` ~L402–405
- **Finding:** `baseResumeUnsupportedEscape` fires on `bodyShape === "resume_content" || artifactKey === "base_resume"` — intentional JAR backward compat per plan step 3.
- **Recommendation:** When job editors adopt `bodyShape`, prefer shape-driven check; `artifactKey === "base_resume"` can remain until JAR migrates.

## What's solid

- Minimal, plan-exact React diff: one prop, one boolean widening, one page wire.
- JAR backward compatibility preserved without editing `JobAnalysisReportModal.tsx`.
- Draft pattern is self-contained (no write-operative cross-link); status line calls for Archie approval.
- Betty tests cover `bodyShape` structure mode, leaf PUT contract, and draft/page source assertions.
- Operative dependency satisfied on tip — Save PUT + GET hydrate path from AST-1576 enables reload verification.

## Frame diff

| Area | Paths | Verdict |
|------|-------|---------|
| AST-1577 product (in-scope) | `canon/directives/draft/patt.artifacts.ui-consistency.md`, `ArtifactEditor.tsx`, `ArtifactsBaseResumeContent.tsx` | In-scope; plan-faithful |
| AST-1577 tests/bible | `tests/component/frontend/components/test_ArtifactEditor.test.tsx`, `pages/test_ArtifactsBaseResumeContent.test.tsx`, `docs/test-bible/frontend/components.md`, `pages.md` | In-scope via Betty merge-tests |
| Plan doc | `docs/features/foundation/ast-1577-ui-consistency-base-resume-editor.md` | Present |
| Sibling ancestry (not 1577 engineer) | `src/core/**`, `src/data/**`, `src/ui/api/**`, `src/utils/**`, AST-1576 tests/bible | Expected AST-1576 stack on epic tip — not 1577 scope creep |
| Sibling OOS | `JobAnalysisReportModal.tsx`, rubric pages, coat-check, new catalog keys | Not touched ✓ |

## Notes

- Joan plan-rubric APPROVED attached; no Excluded-statute straggler list — C4 clear.
- AST-1576 Radia CLEAN review (`12c360df`) on same branch ancestry; no regressions flagged in 1577 frontend layer.
- C7 complete: full artifact + frame diff present.

context_tokens≈22000
```
```
