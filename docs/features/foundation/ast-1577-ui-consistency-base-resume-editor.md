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

