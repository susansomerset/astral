---
id: patt.artifacts.ui-consistency
kind: pattern
scope: [src/ui/frontend/src/components/ArtifactEditor.tsx, src/ui/frontend/src/pages]
point: >
  Parameterize artifact editors by catalog body_shape so same-typed bodies share one UI path.
---

# Abstract

UI editors for versioned artifact bodies select their layout and payload shape from the catalog entry’s `body_shape` (into `BUILD_CONFIG["artifact_shapes"]`), not from one-off per-key forks. Artifacts that share a `body_shape` reuse the same editor component path. Persist and reload go through the entity’s existing candidate/job data API contracts for that leaf slot; the client does not invent parallel storage keys.

**Status:** draft — Archie approval required before active.

# Arc

1. **Before** — Catalog registers `body_shape` on the key (SoT in config; not this pattern’s register step).
2. **During** — Page passes `bodyShape` (and leaf `artifactKey` for the API slot) into the shared editor; editor renders the shape’s field/structure UI; Save PUTs the body under the leaf artifacts key; GET reloads the current body for that leaf.
3. **After** — Another key with the same `body_shape` can reuse the same editor props pattern without a new component fork.

# Applications

1. Candidate Base Resume Content page — pilot `body_shape` `resume_content`, leaf `base_resume`.
2. Future same-shape candidate or job editors (reuse the shared component; out of this ticket’s product edits).

# Exceptions

1. **Rubric / criteria chrome** — criteria arrays with add/remove/importance are not `resume_content`; they keep the existing rubric editor mode until a separate shape registers them.
2. **Job Analysis Report Modal / other job tabs** — may keep legacy props until a job-editor ticket adopts `bodyShape`; this pattern does not require rewriting them in the pilot ticket.
3. **Non-artifact forms** (session paste, admin tools) — out of scope.

# Implementation

1. **Select shape** — Page reads the catalog key’s `body_shape` (pilot hardcodes the known literal `resume_content` matching `ARTIFACT_CONFIG["candidate.artifacts.base_resume"]["body_shape"]` — do not add frontend catalog fetch this ticket).
2. **Pass props** — Shared `ArtifactEditor` receives `bodyShape` plus the API leaf `artifactKey` (pilot: `base_resume`) and craft `taskKey` when Generate applies.
3. **Render** — For `resume_content`: structure-driven section tabs + dict payload (experience as `experience_jobs` when section id/type says so). Do not fork a second base-resume-only component.
4. **Load** — GET entity detail; map `candidate_data.artifacts[artifactKey]` (or job equivalent) into tabs. Empty/missing → empty sections, not a client-side blob invent.
5. **Save** — PUT entity data with `{ artifacts: { [artifactKey]: dictPayload } }` via existing candidate/job API. Do not add a one-off `artifact_id` field on the client.
6. **Verify** — Save then reload (or use PUT response body) shows the same section bodies the operator just saved.

# OPEN QUESTIONS / DECISIONS

1. Whether the frontend later fetches `ARTIFACT_CONFIG` / shapes via a system endpoint instead of page-level literals — default no until a catalog-UI ticket; pilot pages may hardcode `bodyShape="resume_content"` matching config.
2. Job editors adopting the same prop — separate tickets; pattern only requires reuse readiness on `ArtifactEditor`.
