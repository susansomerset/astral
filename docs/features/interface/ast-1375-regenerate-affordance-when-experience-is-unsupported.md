<!-- linear-archive: AST-1375 archived 2026-08-31 -->

## Linear archive (AST-1375)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1375/regenerate-affordance-when-experience-is-unsupported-regenerate-resume  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** None / 2  
**Parent:** AST-1371 — Regenerate resume button does not appear for resumes with unsupported content  
**Blocked by / blocks / related:** parent: AST-1371

### Description

## What this implements

Owns making Regenerate (or Generate when empty) appear and work on Artifacts → Base Resume Content whenever the experience section shows the unsupported resume structure message, outside daisy-chain in-flight hide states — including any config/manifest generate-state escape hatch required so that message is never unactionable on this page. Does **not** migrate data, change the unsupported message literal, or reopen Print/no-emit core gates.

## Citations

`pattern.ui.shared-button-roles`, `pattern.config.config-block`, `astral.layers.ui-config-driven-business-logic`, `astral.config.config-source-of-truth`, `astral.standards.no-hardcoded-sets`, `astral.standards.in-scope-only`

## Acceptance criteria

1. [x] With a selected candidate whose saved `artifacts.base_resume.experience` is a legacy string or other non-array shape, opening Artifacts → Base Resume Content shows the unsupported resume structure message on the experience section **and** shows Regenerate in the page header (Generate only if there is no base resume content to regenerate).
2. [x] Clicking that Regenerate control starts Base Resume craft (`craft_resume_base`) with the same confirm-when-regenerating behavior as today for eligible candidates.
3. [x] After craft succeeds with array-shaped experience, the unsupported message is gone and the experience job-array editor is usable without a reload trick.
4. [x] Candidates in artifacts-chain in-flight states that already hide Generate/Regenerate keep that hide; Print and other emit paths still toast unsupported and open no HTML tab until experience is array-shaped.
5. [x] Candidates with valid job-array experience keep current Generate/Regenerate visibility and editor behavior (no regression).

## Boundaries

- [X] Does **not** migrate data, change the unsupported message literal, or reopen Print/no-emit core gates.
- [X] Does **not** force Generate/Regenerate during REQUESTED_ARTIFACTS / chain in-flight hide states (AST-1253).
- [X] Does **not** redesign ArtifactEditor chrome or experience job-array happy-path editing.

## Notes for planning

Citations as above. Single-child epic under AST-1371.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at dispatch-parent.

## QA test manifest

1. Inflight hide membership + generate allowlist unchanged: `tests/component/utils/test_config.py::TestAst1375ArtifactGenerateInflightHideStates`
2. Manifest key on `GET /api/state_ui_manifest`: `tests/component/ui/api/test_api_system.py::TestAst1375InflightHideStatesManifest`
3. ArtifactEditor escape / hide / craft / allowlist-only: `tests/component/frontend/components/test_ArtifactEditor.test.tsx` — `--testNamePattern="AST-1375"`

**AST-1375** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1375ArtifactGenerateInflightHideStates \
  tests/component/ui/api/test_api_system.py::TestAst1375InflightHideStatesManifest \
  -q
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_ArtifactEditor.test.tsx \
  --testNamePattern="AST-1375"
```

**Bible shasums** (`origin/sub/AST-1371/AST-1375-regenerate-affordance-unsupported-experience`):

* `docs/test-bible/frontend/components.md` — `2000402346b89cd1544a7a10c3b141ae0bdb6591`
* `docs/test-bible/utils/config.md` — `1614621439682a71a3bd1311e815f01fcc0da966`
* `docs/test-bible/ui/api/api_system.md` — `39e6957b9f94d60b4823c5d615a6d7f9ace5cb49`

**Pass criterion:** pytest + Vitest green on manifest lines — not zero-arg harness / branch-lock gate.

### Comments

#### radia — 2026-08-14T21:28:55.877Z
[code-rubric] PROCEED (Commit: 3d9486eb) manifest escape hatch clean

#### betty — 2026-08-14T21:26:06.899Z
`origin/sub/AST-1371/AST-1375-regenerate-affordance-unsupported-experience` @ `3d9486eb` · regenerate affordance coverage

#### joan — 2026-08-14T21:18:05.101Z
[plan-rubric] PROCEED (Commit: 243b372d55) Config escape hatch ready

#### katherine — 2026-08-14T21:15:00.892Z
`origin/sub/AST-1371/AST-1375-regenerate-affordance-unsupported-experience` @ `243b372d55` · plan ready

---

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


## Radia review

[code-rubric] revision=2
**Rubric:** code-rubric.v2
**Ticket:** AST-1375
**Publish ref:** `origin/sub/AST-1371/AST-1375-regenerate-affordance-unsupported-experience` @ `3d9486eb`
**Overall:** CLEAN

## Statutes checked

Diff change set: `src/utils/config.py`, `src/ui/frontend/src/components/ArtifactEditor.tsx`, `src/ui/frontend/src/contexts/StateUiContext.tsx`, `docs/features/interface/ast-1375-*.md`, `docs/test-bible/**`, `tests/component/**` — layers `utils`, `ui`, `docs`; change_types `modify` + test/doc `add`. Product commit: `89fea2df`; tip includes Betty `merge-tests` @ `3d9486eb`. Corpus: **65** active per `canon/statutes/README.md`; **64** rows in harvested table (all scored below).

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | not-applicable | no `src/core/**` agent grading changes |
| `astral.agent.do-task-delegation` | scoped | not-applicable | no `do_task` / dispatch edits |
| `astral.agent.grade-vector-validation` | scoped | not-applicable | no grade-vector paths touched |
| `astral.batch.batch-id-first` | scoped | not-applicable | no batch-id paths |
| `astral.batch.batch-id-format` | scoped | not-applicable | no batch-id formatting |
| `astral.batch.claim-process-release` | scoped | not-applicable | no claim/process/release helpers |
| `astral.batch.entity-agent-responses-latest-only` | scoped | not-applicable | no entity-agent-response paths |
| `astral.config.config-source-of-truth` | scoped | conforms | `artifact_generate_inflight_hide_states` added in `build_state_ui_manifest()`; UI reads manifest only |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | not-applicable | no secrets/env surface |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | no debug artifact paths |
| `astral.debug.spikes-under-debug-dir` | scoped | not-applicable | no spike files |
| `astral.dispatch.seed-auto-false` | scoped | not-applicable | no dispatch seed flags |
| `astral.dispatch.run-next-is-chain-authority` | scoped | not-applicable | chain handoff logic unchanged |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | single plan doc for AST-1375 |
| `astral.git.betty-no-src-or-features` | scoped | not-applicable | Betty-owned test/bible diff (not Radia product bar) |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | product commit `89fea2df` touches only `src/` |
| `astral.layers.core-vs-external-bright-line` | scoped | not-applicable | no core/external layer edits |
| `astral.layers.import-direction` | scoped | conforms | utils→ui manifest consumption; no layer violations |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | no `scripts/**` |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | hide list + allowlist from manifest; React holds no state-set literals |
| `astral.idioms.coat-check-never-store-empty` | scoped | not-applicable | no coat-check paths |
| `astral.idioms.render-verdict-orchestrates-consult` | scoped | not-applicable | no render/consult paths |
| `astral.idioms.require-auth-on-protected-endpoints` | scoped | not-applicable | no API route changes in product diff |
| `astral.seed.agent-tables-in-repo-json` | scoped | not-applicable | no seed JSON |
| `astral.seed.archie-catalog-wins` | scoped | not-applicable | no seed catalog edits |
| `astral.seed.boot-only-not-hot-path` | scoped | not-applicable | manifest build is existing hot-path pattern |
| `astral.seed.define-approved` | scoped | not-applicable | no seed define |
| `astral.seed.operator-rows-stay-deleted` | scoped | not-applicable | no operator seed rows |
| `astral.seed.other-via-coverage-join` | scoped | not-applicable | no coverage join |
| `astral.standards.data-raises-caller-logs` | scoped | not-applicable | no `src/data/**` |
| `astral.standards.database-header-inventory` | scoped | not-applicable | no DB/migrations |
| `astral.standards.debug-contract-gated` | scoped | not-applicable | no `debug=` emission |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | reuses `parseExperienceJobs` for notice + affordance (single definition) |
| `astral.standards.in-scope-only` | scoped | conforms | three planned product files only; boundaries respected |
| `astral.standards.logging-via-utils` | scoped | not-applicable | no new logging |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | `artifact_generate_inflight_hide_states`, `baseResumeUnsupportedEscape` are domain-shaped |
| `astral.standards.no-cross-contamination` | scoped | conforms | Base Resume + `!jobPersistence` gate; no global allowlist expansion |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | inflight hide states in config with `CANDIDATE_STATES` assert |
| `astral.standards.public-then-helpers` | scoped | not-applicable | no new public API surface reorder |
| `astral.standards.utils-data-late-import-only` | scoped | not-applicable | no utils→data import |
| `astral.state.core-decides-transitions` | scoped | not-applicable | no state transition edits |
| `astral.state.job-prior-states-enforced` | scoped | not-applicable | no job-state enforcement changes |
| `astral.state.no-daisy-chain-in-run` | scoped | not-applicable | in-flight hide preserved; no chain logic change |
| `astral.ui.frontend-file-placement` | scoped | conforms | edits stay in `ArtifactEditor.tsx` / `StateUiContext.tsx` |
| `astral.ui.naming-conventions` | scoped | conforms | snake_case manifest key; camelCase TS locals |
| `astral.ui.single-gunicorn-worker` | scoped | not-applicable | no server worker config |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | single `merge-tests` tip `3d9486eb` |
| `orch.git.commit-vocabulary` | universal | conforms | `code(AST-1375)` / `test(AST-1375)` / `docs(AST-1375)` vocabulary |
| `orch.git.flow-direction-inviolable` | universal | conforms | sub branch off ftr parent topology |
| `orch.git.ftr-sub-topology` | universal | conforms | `sub/AST-1371/AST-1375-…` |
| `orch.git.merge-on-checkout` | universal | conforms | no checkout violations in review scope |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | none observed |
| `orch.git.no-dev-agent-branches` | universal | conforms | publish ref is `sub/…` not agent branch |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | epic worktree `astral-AST-1371` |
| `orch.git.three-permanent-branches` | universal | conforms | diff vs `origin/dev` only |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | plan decisions already Joan-approved |
| `orch.pipeline.plan-is-bible` | universal | conforms | implementation matches Stages 1–3 |
| `orch.pipeline.project-scoped-queues` | universal | conforms | n/a to code shape |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | reviewed at Tests Passed |
| `orch.roles.archie-approves-statutes` | universal | conforms | n/a |
| `orch.roles.betty-owns-test-tree` | universal | conforms | test/bible diff is Betty lane |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | n/a |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Katherine assignee at Tests Passed |
| `orch.roles.pre-commit-path-bans` | universal | conforms | no banned-path commits in product SHA |

**Straggler (C4):** Joan plan-rubric APPROVED @ `243b372d` — no Excluded statute list in attachment; no straggler rows.

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| `pattern.config.config-block` | conforms | `inflight_hide_states` lives in `build_state_ui_manifest()` beside existing `gen_states`; UI consumes manifest |
| `pattern.ui.shared-button-roles` | conforms | no button-class churn; existing `btn primary` / `in-flight` / confirm flow untouched |

(none cited in plan body; scored from Joan validate + implementation shape)

## Plan adherence

Stages 1–3 land exactly as specified:

- **Stage 1:** `artifact_generate_inflight_hide_states` = `REQUESTED_ARTIFACTS` + `REQUESTED_ARTIFACTS_RETRY` with `CANDIDATE_STATES` assert; `artifact_generate_states` unchanged; `REQUESTED_ARTIFACTS_ERROR` not in hide list.
- **Stage 2:** `StateUiManifest.candidate.artifact_generate_inflight_hide_states: string[]` added.
- **Stage 3:** `experienceUnsupported` reuses the same `parseExperienceJobs` failure as the unsupported notice render branch; `baseResumeUnsupportedEscape` gated on `artifactKey === "base_resume" && !jobPersistence`; `canGenerate` ORs escape with allowlist; `handleGenerateClick` / `doGenerate` / confirm / Print / Save-abort / chain handoff untouched.

Estimate **2** still fits footprint (config manifest key + TS typing + ~20 lines in ArtifactEditor). Betty manifest (`TestAst1375*`) covers AC spine per test-bible.

**C6 lenses (§5a):** Imports/layers/logging/batch/debug/external — no issues. **§5d cross-ticket:** product `src/` diff is AST-1375-only; `merge-tests` tip also carries **AST-1373** test classes in `test_api_system.py` / `test_config.py` — sibling Betty merge, not Katherine product scope (advisory only).

## Findings

None **fix-now**. None **discuss** blocking User Testing.

### Advisory

- **`inflightHideStates` `?? []` fallback** (`ArtifactEditor.tsx`): if an old API omits the new manifest key, hide list is empty and the escape hatch could surface Regenerate during `REQUESTED_ARTIFACTS*` until server catches up. Acceptable for co-deployed SPA+API; note only if staged rollouts are ever split.
- **Sibling tests in diff:** `TestAst1373AuthSessionPolicy*` classes ride `merge-tests` — expected; not AST-1375 product scope.

## Frame diff

(none) — implementation matches approved plan Stages 1–3 with no material deviations.

## What's solid

- Single source of “unsupported”: `experienceUnsupported` and the notice both call `parseExperienceJobs` on experience tabs — affordance cannot drift from message.
- Config-owned hide list preserves AST-1253 in-flight suppression without globally expanding `artifact_generate_states`.
- Tests exercise error-state escape (`REQUESTED_ARTIFACTS_ERROR`), both inflight hides, craft POST + array recovery, and allowlist-only when experience is valid.

## Notes

- Joan plan-rubric verdict attached (APPROVED).
- Product SHA for traceability: `89fea2df`; reviewed tip: `3d9486eb` (includes Betty test merge).

context_tokens≈52000

---

```
[code-rubric] PROCEED (Commit: 3d9486eb) manifest escape hatch clean
```

## Threads (generated — epic_registry mirror)

_(generated from epic registry — do not hand-edit; edits are overwritten)_

### Team

| Agent | Role | Thread |
|--------|-------|--------|
| Katherine | engineer | `/home/susan/.cursor/chats/cc59d8b4568ac7f6826e41af349e90f1/f39b1c0e-0837-402e-8bf5-77722901c8a4/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/503fbfa4-f5fa-46e9-a29c-c4c2efc9d4ec/store.db` |
| Radia | review | `/home/susan/.cursor/chats/cc59d8b4568ac7f6826e41af349e90f1/97322577-1301-4647-b567-7595ae916349/store.db` |

### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-1371 (parent) | ftr/AST-1371-regenerate-resume-unsupported |
| AST-1375 | sub/AST-1371/AST-1375-regenerate-affordance-unsupported-experience |

**Epic worktree:** `astral-AST-1371/` — one active sub checked out at a time.
