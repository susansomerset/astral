# Regenerate affordance when experience is unsupported (Regenerate resume button does not appear for resumes with unsupported content)

**Linear:** [AST-1375](https://linear.app/astralcareermatch/issue/AST-1375/regenerate-affordance-when-experience-is-unsupported-regenerate-resume)
**Parent:** [AST-1371](https://linear.app/astralcareermatch/issue/AST-1371/regenerate-resume-button-does-not-appear-for-resumes-with-unsupported) — Regenerate resume button does not appear for resumes with unsupported content
**Publish ref:** `origin/sub/AST-1371/AST-1375-regenerate-affordance-unsupported-experience`

Owns making Regenerate (or Generate when empty) appear and work on Artifacts → Base Resume Content whenever the experience section shows the unsupported resume structure message, outside daisy-chain in-flight hide states — including a config/manifest generate-state escape hatch so that message is never unactionable on this page. Does **not** migrate data, change the unsupported message literal, or reopen Print/no-emit core gates.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | In `build_state_ui_manifest()`, add config-owned `artifact_generate_inflight_hide_states` (REQUESTED_ARTIFACTS + REQUESTED_ARTIFACTS_RETRY) next to existing `artifact_generate_states`; assert membership in `CANDIDATE_STATES` | utils |
| `src/ui/frontend/src/contexts/StateUiContext.tsx` | Extend `StateUiManifest.candidate` with `artifact_generate_inflight_hide_states: string[]` | ui |
| `src/ui/frontend/src/components/ArtifactEditor.tsx` | Base Resume Content escape hatch: when experience is unsupported (same parse failure that shows the notice), show Generate/Regenerate unless candidate state is in the inflight-hide list; keep existing craft / confirm / in-flight button behavior | ui |

**Out of scope (do not touch):** `BUILD_CONFIG["unsupported_resume_structure_message"]` literal; `ExperienceJobsEditor`; Print / Open HTML / JAR toast + no-emit (`builder` / `api_resume_html`); Admin Session Resume Paste; daisy-chain hop UX / `generate_artifacts` handoff for chain task keys; expanding `artifact_generate_states` globally to force Generate on every Artifacts page; `tests/` / bible (Betty); data migration of legacy string experience.

**As-is:** AST-1351 shows `unsupported resume structure, please regenerate` inline when `experience` is a legacy string / non-array, and blocks Save — but Generate/Regenerate visibility is only `manifest.candidate.artifact_generate_states.has(candidateState)` (`ArtifactEditor` `canGenerate`). Candidates whose state is outside that allowlist (e.g. `REQUESTED_ARTIFACTS_ERROR`, or any other non-allowlisted state where Base Resume Content is still reachable) see the message with no header affordance. AST-1253 correctly hides Generate during REQUESTED_ARTIFACTS / REQUESTED_ARTIFACTS_RETRY; that hide must remain.

**To-be:** On Base Resume Content (`artifactKey === "base_resume"`, not `jobPersistence`), if the experience tab would show the unsupported notice, `canGenerate` is also true unless the candidate state is in the new config-owned inflight-hide list. Clicking still runs existing `craft_resume_base` Generate / Regenerate confirm flow. After a successful craft that stores array-shaped experience, the notice is gone and `ExperienceJobsEditor` is usable from the updated tabs (no reload trick). Print and emit gates unchanged.

## Stage 1: Manifest — inflight hide states

**Done when:** `GET /api/state_ui_manifest` includes `candidate.artifact_generate_inflight_hide_states` listing exactly `REQUESTED_ARTIFACTS` and `REQUESTED_ARTIFACTS_RETRY`; existing `artifact_generate_states` list is unchanged; both lists assert every entry is a `CANDIDATE_STATES` key.

1. In `src/utils/config.py` `build_state_ui_manifest()`, immediately after the existing `gen_states` list / assert (AST-1253 Generate allowlist), add:

```python
# States that must keep Generate/Regenerate hidden even when Base Resume
# experience is unsupported (AST-1253 in-flight chain claim).
inflight_hide_states = [
    "REQUESTED_ARTIFACTS",
    "REQUESTED_ARTIFACTS_RETRY",
]
assert all(s in CANDIDATE_STATES for s in inflight_hide_states)
```

2. In the returned `"candidate"` object (same dict that currently has `"artifact_generate_states": gen_states`), add:
   `"artifact_generate_inflight_hide_states": inflight_hide_states`
3. Do **not** add `REQUESTED_ARTIFACTS_ERROR` to the hide list — error is not in-flight; the escape hatch must be allowed to surface Regenerate there when experience is unsupported.
4. Do **not** change the `gen_states` membership (no global expansion of Generate on other Artifacts pages).
5. `api_system.state_ui_manifest` already merges live chain arrays onto `manifest["candidate"]` — leave that merge alone; the new key rides with `build_state_ui_manifest()` output.

⚠️ **Decision:** New hide list rather than inverting Generate to “everything except hide.” Other Artifacts pages keep today’s allowlist-only visibility; only the Base Resume unsupported escape hatch consults the hide list.

## Stage 2: TypeScript manifest typing

**Done when:** `StateUiManifest.candidate` declares `artifact_generate_inflight_hide_states: string[]` so ArtifactEditor can read it without casting.

1. In `src/ui/frontend/src/contexts/StateUiContext.tsx`, under `candidate: { ... }`, add `artifact_generate_inflight_hide_states: string[]` next to `artifact_generate_states`.
2. Do not change the provider fetch path — it already stores the full JSON manifest.

## Stage 3: ArtifactEditor escape hatch + craft path unchanged

**Done when:** On Base Resume Content, unsupported experience shows the existing notice **and** a primary Generate/Regenerate control whenever the candidate is not in `artifact_generate_inflight_hide_states`; click still confirms-when-regenerating and POSTs `craft_resume_base` as today; array-shaped experience after success uses `ExperienceJobsEditor` without a forced reload; chain in-flight states still hide the control; valid job-array experience keeps current visibility (allowlist only).

1. In `src/ui/frontend/src/components/ArtifactEditor.tsx`, near the existing `generateStates` / `canGenerate` memos (~lines 348–365), add:

```ts
const inflightHideStates = useMemo(
  () => new Set(manifest?.candidate.artifact_generate_inflight_hide_states ?? []),
  [manifest?.candidate.artifact_generate_inflight_hide_states],
)
```

2. Add a `useMemo` `experienceUnsupported` that is true when any tab with `isExperienceTab(tab.id, fieldType)` fails `parseExperienceJobs(tab.content, experienceJobFields.map(f => f.key))` with `ok: false`. Use the same `fixedFields` type lookup already used in the experience render branch. Empty experience (`ok: true`, `jobs: []`) is **not** unsupported.
3. Replace the `canGenerate` assignment with (exact logic):

```ts
const baseResumeUnsupportedEscape =
  !jobPersistence
  && artifactKey === "base_resume"
  && experienceUnsupported
  && !inflightHideStates.has(candidateState)

const canGenerate =
  !jobPersistence
  && (generateStates.has(candidateState) || baseResumeUnsupportedEscape)
```

4. Do **not** change `handleGenerateClick`, `doGenerate`, `doRequestArtifacts`, confirm modal copy, `btn primary` / `in-flight` classes, Print `headerActions`, unsupported notice text sourcing (`ui_config` / `unsupportedExperienceMessage`), Save abort on unsupported experience, or chain-handoff behavior for `chainTaskKeys`.
5. `craft_resume_base` is **not** on the REQUESTED_ARTIFACTS chain — Base Resume continues to use per-artifact `POST …/generate/craft_resume_base` (existing `doGenerate`). Do not switch Base Resume to `generate_artifacts`.
6. Label rules stay as today: `showAsRegenerate = isChainHandoff ? hasChainData : hasData` — with content present (including legacy string experience), the button reads **Regenerate** and opens the confirm modal; with no tab content, **Generate** runs immediately.
7. After successful `doGenerate`, existing tab remapping via `sectionValueToTabContent` must leave array-shaped experience parseable so `ExperienceJobsEditor` renders — do not add a `window.location.reload()` or extra fetch solely for this ticket.
8. Scope gate: `artifactKey === "base_resume" && !jobPersistence` only — do not apply the escape hatch to job-persistence JAR editors or other artifact keys.

⚠️ **Decision:** Gate the escape hatch on `artifactKey === "base_resume"` inside ArtifactEditor (no new prop on `ArtifactsBaseResumeContent`) so the page file stays untouched and JAR `jobPersistence` paths remain allowlist-only.

⚠️ **Decision:** Reuse the same `parseExperienceJobs` failure that drives the unsupported notice — one definition of “unsupported” for message and affordance; do not invent a second shape check.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1375
**Overall:** APPROVED
**Publish-ref:** `origin/sub/AST-1371/AST-1375-regenerate-affordance-unsupported-experience` @ `243b372d55`

## Traceability

AC1–AC5 → Stage 1 (`artifact_generate_inflight_hide_states` in manifest), Stage 2 (TS typing), Stage 3 (`baseResumeUnsupportedEscape` + unchanged `craft_resume_base` / confirm / in-flight chrome). Stages 1–3 → parent Purpose, Functional scope, and all five AC bullets; no orphan stages; boundaries (no migration, no message literal change, no Print/no-emit reopen, AST-1253 in-flight hide preserved, `base_resume` + `!jobPersistence` only) explicit in Files Changed out-of-scope and Stage 3 gates.

## Findings

None `fix-now`. No `discuss` items that block build.

**In-session statute pass (R1–R3, not repeated in slim upshot):** Universal orchestration/git statutes — all `conforms` (plan touches only `src/utils/config.py` + two frontend files; tests/bible explicitly out of scope; no git/process violations). Scoped product statutes cited by parent — `astral.layers.ui-config-driven-business-logic`, `astral.config.config-source-of-truth`, `astral.standards.no-hardcoded-sets`, `astral.standards.in-scope-only`, `astral.ui.frontend-file-placement`, `astral.ui.naming-conventions`, `astral.standards.dry-and-focused-functions`, `astral.standards.names-not-ticket-ids` — all `conforms`: state hide list lives in `build_state_ui_manifest()` with `CANDIDATE_STATES` assert; escape hatch extends existing AST-1253 manifest-driven visibility rather than ad-hoc React state sets; `parseExperienceJobs` reuse aligns affordance with the unsupported notice; layer/placement/naming unchanged; identifiers domain-shaped (`artifact_generate_inflight_hide_states`, `baseResumeUnsupportedEscape`). Patterns `pattern.ui.shared-button-roles` and `pattern.config.config-block` — plan preserves `btn primary` / `in-flight` and config-block ownership. R6 adversarial checklist — layer/config/placement/DRY/scope gates pass; As-is/To-be matches code (`canGenerate` today is allowlist-only at ~363; `gen_states` at config ~3594–3601).

context_tokens≈42000


## Review stub (Katherine / build)

**Publish ref:** `origin/sub/AST-1371/AST-1375-regenerate-affordance-unsupported-experience`
**Product commits:** `89fea2df` (manifest inflight-hide + Base Resume unsupported escape hatch)

