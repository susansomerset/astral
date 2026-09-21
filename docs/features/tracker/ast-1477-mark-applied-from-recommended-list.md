<!-- linear-archive: AST-1477 archived 2026-09-09 -->

## Linear archive (AST-1477)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1477/mark-applied-from-recommended-list-add-means-to-mark-job-as-applied  
**Status at archive:** Archive  
**Project:** Astral Tracker  
**Assignee:** katherine  
**Priority / estimate:** None / 2  
**Parent:** AST-1464 — Add means to mark job as applied for  
**Blocked by / blocks / related:** parent: AST-1464

### Description

## What this implements

Add the Applied icon-control on Recommended list rows for legal `CANDIDATE_APPLIED` priors; wire through existing `useCandidateJobActions` / `CandidateActionNotesModal` / `candidate_action`. Does not own report Applied/Skip (sibling Report Applied and Skip) or the Applied list page (sibling Applied jobs list home).

## Citations

`pattern.ui.icon-control`; `astral.state.core-decides-transitions`; `astral.state.job-prior-states-enforced`; `astral.ui.naming-conventions`

## Scope

`src/ui/frontend/src/components/CandidateJobRowActions.tsx` (modified — Applied icon on legal pre-applied states); `src/ui/frontend/src/pages/JobsRecommended.tsx` (modified — list Applied via shared requestAction/notes path and list refresh; may pass action handlers through to the report modal for sibling Report Applied and Skip)

## Acceptance criteria

1. On Recommended, a job in a legal prior for `CANDIDATE_APPLIED` shows an Applied list-row icon-control; confirming with optional notes transitions to `CANDIDATE_APPLIED` and writes `candidate_results.applied`.
2. After mark-applied, the job no longer appears on Recommended and does appear on `/jobs/applied` for that candidate. (list home is sibling — this child owns the mark control that starts the transition)
3. Illegal transitions still fail with a visible error (no silent no-op).

## Boundaries

Does not add Applied/Skip on Job Analysis Report. Does not implement Applied list API/page/nav.

## Notes for planning

Reuse existing `onAction("applied")` / notes modal; legal priors only per `CANDIDATE_APPLIED.prior_states`.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at dispatch-parent.

## QA test manifest

1. Row Applied icon-control: `tests/component/frontend/components/test_CandidateJobRowActions.test.tsx` — `--testNamePattern="AST-1477"`
2. Recommended list Applied path (§6c): `tests/component/frontend/pages/test_JobsRecommended.test.tsx` — `--testNamePattern="AST-1477"`
3. Regression: AST-1302 + AST-1410 only — **do not** use bare `Skip` in the Vitest pattern (matches sibling AST-1478 report cases)

**Narrowed run** (from `src/ui/frontend/`):

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_CandidateJobRowActions.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsRecommended.test.tsx \
  --testNamePattern="AST-1477|AST-1302|AST-1410"
```

**Publish:** `origin/sub/AST-1464/AST-1477-mark-applied-from-recommended-list` @ `44fa5b67` · `merge-tests(AST-1477): origin/tests 4d9f85ba`

### Comments

#### betty — 2026-08-25T02:36:43.826Z
[check-linear] ftr merge clean — AST-1477+1478 bible/nests; PRE_APPLIED restored @ 37350c11

#### chuckles — 2026-08-25T02:32:41.953Z
[merge-child] blocked: docs/test-bible/frontend/components.md; tests/component/frontend/pages/test_JobsRecommended.test.tsx — @Betty White (keep AST-1477 + AST-1478 manifests/nests).

#### chuckles — 2026-08-25T02:20:50.808Z
[merge-child] blocked: `validate-sub-log.sh` — missing `plan(AST-1477):` `code(AST-1477):` in `origin/ftr/AST-1464-add-means-to-mark-job-as-applied-for..origin/sub/AST-1464/AST-1477-mark-applied-from-recommended-list` range.

Those commits are already ancestors of ftr (via AST-1478 `sync(publish-ref)` of this sub) and of this tip (`docs(AST-1477): plan —` @ `06a60cc2`, `code(AST-1477):` @ `d47122f2`). Residual range still has resolve / merge-tests / test / docs; merge-tree into ftr is clean @ `f150463f`.

@Katherine Johnson — same tip-marker pattern as AST-1222: empty tip commits `plan(AST-1477): — tip marker for merge-child validate-sub-log` and `code(AST-1477): — tip marker for merge-child validate-sub-log` on `origin/sub/AST-1464/AST-1477-mark-applied-from-recommended-list`, force-with-lease push, stay **User Testing**. Chuckles will re-run merge-child after.

#### betty — 2026-08-25T01:39:10.759Z
[check-linear] Cleared ftr dry-run block: merged origin/ftr into sub; kept both plans; components.md has AST-1477 + AST-1478 manifests; JobsRecommended nests AST-1478 + AST-1057 + AST-1477. `origin/sub/AST-1464/AST-1477-mark-applied-from-recommended-list` @ `f150463f` · assignee Katherine for resolve-child §9a.

#### katherine — 2026-08-25T01:30:24.797Z
[check-linear] blocked: §9a ftr dry-run conflicts

@Betty White @Chuckles Cursor

`origin/sub/AST-1464/AST-1477-mark-applied-from-recommended-list` @ `5cfa9cd8` merges cleanly into `origin/dev`, but **not** into `origin/ftr/AST-1464-add-means-to-mark-job-as-applied-for`.

Attempted `git merge origin/ftr/AST-1464-add-means-to-mark-job-as-applied-for` on this sub — aborted. Conflict files:

- `docs/features/tracker/ast-1477-mark-applied-from-recommended-list.md` (modify/delete — keep on sub)
- `docs/features/tracker/ast-1478-report-applied-and-skip.md` (modify/delete — sibling plan on ftr)
- `docs/test-bible/frontend/components.md` (AST-1477 vs AST-1478 QA manifest patterns)
- `tests/component/frontend/pages/test_JobsRecommended.test.tsx` (AST-1477 nesting vs AST-1478 report describe)

Radia FIX-NOW nesting is cleared (Betty `0fc2059d`); resolve doc pushed. Staying **Review Posted** until ftr↔sub test/bible merge is reconciled (Betty test-tree / Chuckles epic orchestration). Cannot advance to User Testing while §9a ftr dry-run is blocked.

#### betty — 2026-08-25T00:51:29.352Z
[check-linear] Cleared [qa-handoff]: nested AST-1057 + AST-1477 inside `describe("JobsRecommended")` so suite `beforeEach` applies. `origin/sub/AST-1464/AST-1477-mark-applied-from-recommended-list` @ `0fc2059d` · assignee Katherine for resolve-child.

#### katherine — 2026-08-25T00:44:12.660Z
[qa-handoff]
@Betty White

Radia **FIX-NOW** (`docs(AST-1477): Radia review — FIX-NOW describe nesting` @ `fbdb4432`):

**`tests/component/frontend/pages/test_JobsRecommended.test.tsx`** — `describe("JobsRecommended")` closes at line 229; AST-1057 `it` blocks (and the AST-1477 describe) sit outside the suite and lose shared `beforeEach` (`localStorage.clear` / `mockedApi.mockReset()`).

**Fix (test-tree only):** move the closing `})` to after AST-1057 + AST-1477 (or nest those describes inside the main suite). Engineer cannot patch `tests/` — please land on this publish ref and reassign Katherine.

No product delta for this finding. Discuss/advisory items need no engineer code change.

`origin/sub/AST-1464/AST-1477-mark-applied-from-recommended-list` @ `fbdb4432`

#### radia — 2026-08-25T00:39:27.474Z
[code-rubric] REVIEW (Commit: 44fa5b67)

#### chuckles — 2026-08-25T00:37:39.449Z
[agent-busy-timeout] blocked: Cursor conversation still busy after 20m call-wait (spawn=`79e2a573`, attempts=12).
- parent: `AST-1464`
- agent: **Radia** role=review `review-child` on `AST-1477`
- AGENT_SESSION: `c1844f96-104a-48a9-9d58-26432f33d87d`

Do **not** `agent create-chat` and do **not** treat this as `[thread-missing]` — the Thread UUID is fine; another run held it.

#### betty — 2026-08-25T00:06:29.792Z
[check-linear] Cleared [qa-handoff]: narrowed AST-1477 Vitest pattern to `AST-1477|AST-1302|AST-1410` (dropped bare `Skip` so sibling AST-1478 report cases are not selected); stripped AST-1478 page describe from this tip’s JobsRecommended tests. `origin/sub/AST-1464/AST-1477-mark-applied-from-recommended-list` @ `44fa5b67` · assignee Katherine for test-child.

#### katherine — 2026-08-24T23:57:40.916Z
[qa-handoff]
@Betty White

Manifest command from `docs/test-bible/frontend/components.md` (AST-1477):

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_CandidateJobRowActions.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsRecommended.test.tsx \
  --testNamePattern="AST-1477|AST-1302|AST-1410|Skip"
```

**Product / this ticket:** all `AST-1477` cases pass (narrow `--testNamePattern="AST-1477"` is green). Applied mark + notes → `candidate_action` + 409 toast behave as planned.

**Manifest defect:** `|Skip` also matches sibling describe **`AST-1478 report Applied and Skip`** in the same `test_JobsRecommended.test.tsx`. Those three tests fail here (`reportStrip()` null) because report Applied/Skip is **out of scope** for AST-1477 (AST-1478 owns `JobAnalysisReportModal` props).

Please narrow the Vitest pattern (e.g. drop bare `Skip`, or exclude `AST-1478`) so the AST-1477 run does not require sibling report controls. Stay Tests Ready after you republish.

`origin/sub/AST-1464/AST-1477-mark-applied-from-recommended-list` @ `151a8ef2` (Betty merge-tests `3c065946` is ancestor)

#### betty — 2026-08-24T23:52:05.584Z
`origin/sub/AST-1464/AST-1477-mark-applied-from-recommended-list` @ `3c065946` · Applied mark ready

#### katherine — 2026-08-24T23:08:40.299Z
`origin/sub/AST-1464/AST-1477-mark-applied-from-recommended-list` @ `06a60cc2023dea7c92a9b34e045db976ccaa2f0d` · plan ready

---

# AST-1477 — Mark applied from Recommended list

**Linear:** [AST-1477](https://linear.app/astral-tracker/issue/AST-1477)
**Parent:** [AST-1464](https://linear.app/astral-tracker/issue/AST-1464) — Add means to mark job as applied for
**Publish ref:** `sub/AST-1464/AST-1477-mark-applied-from-recommended-list`

Operators on Recommended can mark a job Applied via a list-row icon-control when the job is in a legal prior for `CANDIDATE_APPLIED`. Confirmation uses the existing notes modal and `POST …/candidate_action` (`action=applied`); list refresh drops the row from Recommended. This child does **not** add report Applied/Skip (AST-1478) or the Applied list home (AST-1479).

## Explicit scope gate

Ticket **## Scope** names only:

- `src/ui/frontend/src/components/CandidateJobRowActions.tsx` — Applied icon on legal pre-applied states
- `src/ui/frontend/src/pages/JobsRecommended.tsx` — list Applied via shared `requestAction` / notes path and list refresh; may pass action handlers through to the report modal for sibling AST-1478

No other files. Do **not** edit `JobAnalysisReportModal.tsx`, `api_jobs.py`, `config.py`, or `JobsApplied.tsx`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/CandidateJobRowActions.tsx` | On the review-like / pre-applied branch, add an Applied `icon-control` for states that are legal `CANDIDATE_APPLIED` priors appearing on Recommended; call `onAction("applied")` | ui |
| `src/ui/frontend/src/pages/JobsRecommended.tsx` | Confirm list Applied uses existing `useCandidateJobActions` → `requestAction` / `CandidateActionNotesModal` / error toast / `load` refresh; only edit if that wiring is incomplete. Do **not** add report-modal Applied/Skip props here (AST-1478 owns `JobAnalysisReportModal`) | ui |

## Stages

### Stage 1: Applied icon on legal Recommended priors

**Done when:** On Recommended, rows in `RECOMMENDED` / `BUILD_ARTIFACTS` / `CANDIDATE_REVIEW` show an Applied icon-control next to Skip; clicking it opens the existing notes modal with title “Applied”; confirming POSTs `candidate_action` with `action=applied` (via existing `onAction` → `requestAction` → `confirmPending`). Illegal / failed transitions still surface via the existing error toast (no silent no-op).

1. In `CandidateJobRowActions.tsx`, keep the existing `REVIEW_LIKE` branch that renders Skip (and optional View Analysis). Do not remove Skip or change post-applied R/I/X/G behavior.
2. Add a module-level set of states that may show the **Applied** mark-control on this list. Exact members:

   ```ts
   const PRE_APPLIED_MARK = new Set([
     "CANDIDATE_REVIEW",
     "BUILD_ARTIFACTS",
     "RECOMMENDED",
   ])
   ```

   These are the intersection of Recommended-list states (`RECOMMENDED_JOB_STATES` in config) and `JOB_STATES["CANDIDATE_APPLIED"]["prior_states"]`. Do **not** add `PASSED_LIKE` (it is in `REVIEW_LIKE` for Skip/view legacy, but is **not** a `CANDIDATE_APPLIED` prior — showing Applied there would invite illegal hops).

   ⚠️ **Decision:** Keep this set as a module-level `Set` next to `REVIEW_LIKE` / `POST_APPLIED`. Ticket Scope does not include `config.py` or a state-UI manifest field; the component already hardcodes review/post-applied sets the same way. Do not invent a config/API surface for this child.

3. Inside the `REVIEW_LIKE.has(state) && onSkip` branch (same `job-list-actions` div as Skip), when `onAction` is defined **and** `PRE_APPLIED_MARK.has(state)`, render:

   ```tsx
   <button type="button" className="icon-control" title="Applied" aria-label="Applied"
     onClick={() => onAction("applied")}>A</button>
   ```

   Place Applied after Skip (and before View Analysis when that button is shown). Glyph `A`, labels `Applied` — matches `CandidateActionNotesModal` `LABELS.applied` and `pattern.ui.icon-control` (class `icon-control`, not a labeled `.btn`).

4. Do not call the API from this component. Only `onAction("applied")`. Backend `candidate_action` + `transition_job_state` + `candidate_results.applied` already exist (AST-311); do not duplicate POST logic.

### Stage 2: Recommended list wiring (verify / minimal edit)

**Done when:** After Stage 1, marking Applied from a Recommended row opens notes, confirms, refreshes the list (row leaves Recommended when the API succeeds), and failed/409 responses still toast via `actions.error`. No report Applied/Skip controls are added.

1. Read `JobsRecommended.tsx`. Today it already:

   - mounts `useCandidateJobActions(load)`
   - passes `onAction={a => actions.requestAction(job.astral_job_id, a)}` into `CandidateJobRowActions`
   - mounts `CandidateActionNotesModal` on `actions.pending` / `confirmPending`
   - toasts `actions.error`

   `CandidateActionKey` already includes `"applied"`; `postCandidateAction` already POSTs it. **If that wiring is still present, make no functional change** (optional: one short comment above the `CandidateJobRowActions` usage stating that `onAction` covers list Applied via notes + `candidate_action`).

2. If `onAction` / notes modal / error toast / refresh path is missing or broken for Applied, restore only the list path to match the pattern above — still inside `JobsRecommended.tsx` only.

3. ⚠️ **Decision:** Do **not** pass Applied/Skip handlers into `JobAnalysisReportModal` in this ticket. Ticket Scope’s “may pass … for sibling” would require accepting props on `JobAnalysisReportModal.tsx`, which is AST-1478’s Scope file. Leave the modal mount as `jobId` / `onClose` / `onRefresh` only. Sibling AST-1478 owns report labeled Applied/Skip.

4. Do not implement `/jobs/applied` visibility, nav enablement, or `view=applied` — AST-1479. Acceptance criterion 2’s “appear on `/jobs/applied`” is satisfied for this child by completing the mark-applied transition; list home is sibling ownership per Boundaries.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric.v1
**Ticket:** AST-1477
**Overall:** APPROVED
**Publish ref:** `sub/AST-1464/AST-1477-mark-applied-from-recommended-list` @ `06a60cc2023dea7c92a9b34e045db976ccaa2f0d`

## Traceability
AC1→Stage 1+2 (Applied `icon-control` → `onAction("applied")` → notes modal → `candidate_action` applied); AC2→Stage 2 (row leaves Recommended on success; `/jobs/applied` list home→AST-1479 per Boundaries); AC3→Stage 1 Done-when + Stage 2 (`actions.error` toast, no silent no-op)

## Findings
None (`fix-now`).

**acceptable** — `PRE_APPLIED_MARK` module-level `Set` in `CandidateJobRowActions.tsx`: extends existing `REVIEW_LIKE` / `POST_APPLIED` pattern; intersection (`RECOMMENDED`, `BUILD_ARTIFACTS`, `CANDIDATE_REVIEW`) matches config; `PASSED_LIKE` excluded; API enforces illegal hops (409). Child scope excludes `config.py`.

**R6 checklist (summary):** Scope gate honored (two in-scope files; AST-1478/1479 exclusions explicit). Ui-only, layer-clean. `pattern.ui.icon-control` conforms. Reuses `useCandidateJobActions` / notes modal — no parallel POST. Stage 2 verify-first on existing `JobsRecommended` wiring. No `JobAnalysisReportModal` props.

**Considered (in-session):** Universal `orch.*` (20) — conforms. Scoped: `astral.ui.frontend-file-placement`, `astral.ui.naming-conventions`, `astral.standards.dry-and-focused-functions`, `astral.standards.in-scope-only`, `astral.standards.no-hardcoded-sets` — conforms or acceptable; `astral.layers.ui-config-driven-business-logic` — acceptable. Excluded: `astral.state.*` (no core/data/config touch).

context_tokens≈35000

## Review

**Publish ref:** `origin/sub/AST-1464/AST-1477-mark-applied-from-recommended-list`
**Tip (pre-review):** `d47122f23a79`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1–2 | `d47122f23a79` | Applied icon on legal Recommended priors; JobsRecommended onAction comment |

## Radia review

**Rubric:** code-rubric.v1
**Ticket:** AST-1477
**Publish ref:** `origin/sub/AST-1464/AST-1477-mark-applied-from-recommended-list` @ `44fa5b67ebc3c95e8e60e14b95fe8e82d1eabec4`
**Overall:** FIX-NOW

## Statutes checked

65 active statutes scored in-session (per `canon/statutes/README.md` harvested corpus). No **violates**.

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | ui/docs diff only |
| astral.agent.do-task-delegation | scoped | not-applicable | no agent paths |
| astral.agent.grade-vector-validation | scoped | not-applicable | no agent paths |
| astral.batch.batch-id-first | scoped | not-applicable | no batch paths |
| astral.batch.batch-id-format | scoped | not-applicable | no batch paths |
| astral.batch.claim-process-release | scoped | not-applicable | no batch paths |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | no batch paths |
| astral.config.config-source-of-truth | scoped | not-applicable | no config.py in AST-1477 delta |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | no secrets paths |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no debug paths |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | no debug paths |
| astral.dispatch.seed-auto-false | scoped | not-applicable | no dispatch paths |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | no dispatch paths |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single AST-1477 issue doc |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty: bible + tests only |
| astral.git.engineer-test-tree-ban | scoped | conforms | product `d47122f2` → `src/ui` only |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | ui-only |
| astral.layers.import-direction | scoped | conforms | no layer violations |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no scripts |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | `PRE_APPLIED_MARK` extends existing module-level set pattern; plan-documented |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | no coat-check |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | no consult |
| astral.idioms.require-auth-on-protected-endpoints | scoped | not-applicable | no new routes |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | no seed |
| astral.seed.archie-catalog-wins | scoped | not-applicable | no seed |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | no seed |
| astral.seed.define-approved | scoped | not-applicable | no seed |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | no seed |
| astral.seed.other-via-coverage-join | scoped | not-applicable | no seed |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | no data layer |
| astral.standards.database-header-inventory | scoped | not-applicable | no database.py |
| astral.standards.debug-contract-gated | scoped | not-applicable | no debug= |
| astral.standards.dry-and-focused-functions | scoped | conforms | reuses `onAction` → shared hook |
| astral.standards.in-scope-only | scoped | conforms | product delta = two scoped files |
| astral.standards.logging-via-utils | scoped | not-applicable | no logging |
| astral.standards.names-not-ticket-ids | scoped | conforms | domain state names |
| astral.standards.no-cross-contamination | scoped | not-applicable | single feature |
| astral.standards.no-hardcoded-sets | scoped | conforms | `PRE_APPLIED_MARK` mirrors `REVIEW_LIKE`/`POST_APPLIED`; plan-acceptable (Joan straggler — discuss) |
| astral.standards.public-then-helpers | scoped | not-applicable | no new surface |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | no utils |
| astral.state.core-decides-transitions | scoped | not-applicable | transitions via existing API (Joan excluded) |
| astral.state.job-prior-states-enforced | scoped | not-applicable | API enforces; no core touch (Joan excluded) |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no run paths |
| astral.ui.frontend-file-placement | scoped | conforms | correct tree |
| astral.ui.naming-conventions | scoped | conforms | consistent naming |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no server |
| orch.git.betty-merge-tests-one-sha | universal | conforms | merge-tests at tip |
| orch.git.commit-vocabulary | universal | conforms | standard prefixes |
| orch.git.flow-direction-inviolable | universal | conforms | sub topology |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1464/AST-1477-…` |
| orch.git.merge-on-checkout | universal | conforms | no rebase issues |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | merge only |
| orch.git.no-dev-agent-branches | universal | conforms | branch naming |
| orch.git.one-epic-worktree-per-parent | universal | conforms | AST-1464 worktree |
| orch.git.three-permanent-branches | universal | conforms | vs origin/dev |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | no policy invention |
| orch.pipeline.plan-is-bible | universal | conforms | matches plan |
| orch.pipeline.project-scoped-queues | universal | conforms | n/a |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | approved pattern |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty manifest |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Katherine assignee |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Katherine assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | no bypass |

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.ui.icon-control | conforms | glyph `A`; `title`/`aria-label` Applied; `icon-control` class; after Skip |
| pattern.ui.shared-button-roles | not cited | plan uses icon-control for list-row Applied (correct) |

## Plan adherence

Product code (`d47122f2`) matches approved plan:

- **`CandidateJobRowActions.tsx`:** `PRE_APPLIED_MARK` set (`RECOMMENDED`, `BUILD_ARTIFACTS`, `CANDIDATE_REVIEW`; excludes `PASSED_LIKE`); Applied `icon-control` after Skip; `onAction("applied")` only — no API calls in component.
- **`JobsRecommended.tsx`:** existing `useCandidateJobActions` / notes modal / error toast wiring verified; comment only — no `JobAnalysisReportModal` props (AST-1478 boundary honored).

Estimate 2 fits. Betty tests cover icon visibility, success path, and 409 toast.

## Frame diff

(none)

## Findings

### fix-now

**`tests/component/frontend/pages/test_JobsRecommended.test.tsx` — `describe("JobsRecommended")` closes at line 229; AST-1057 cases stranded**

`describe("JobsRecommended")` ends at line 229. AST-1057 `it` blocks (lines 231–284) sit outside the suite and lose `beforeEach` (`localStorage.clear`, `mockedApi.mockReset()`). Vitest still runs them today, but structure regressed vs `origin/dev` (where AST-1057 lived inside the suite). Likely from epic-branch sync / `merge-tests` resolution — same class of issue as AST-1478.

**Fix:** move the closing `})` to after AST-1057 (and optionally nest `describe("AST-1477 …")` inside the main suite for shared `beforeEach`).

### discuss

- **Straggler — `astral.standards.no-hardcoded-sets`:** Joan scored acceptable at plan; sweep scores **conforms** (`PRE_APPLIED_MARK` follows existing `REVIEW_LIKE`/`POST_APPLIED` module pattern). No product fix.
- **`docs/test-bible/frontend/pages.md`:** no dedicated AST-1477 §6c block — coverage documented in `components.md` only. Minor bible completeness gap; Betty may mirror to `pages.md` if convention requires.

### advisory

- Publish ref carries sibling sync noise (AST-1474 `config.py`, AST-1106 bible drift, etc.) unrelated to AST-1477 product delta. Two-dot scoped `src/ui` diff ≡ `d47122f2` only.
- Betty’s `test(AST-1477)` commit initially included AST-1478 report tests inside `JobsRecommended` describe; `merge-tests` dropped them — correct sibling boundary, but contributed to describe nesting drift.

## What's solid

- Applied icon on legal priors only; `PASSED_LIKE` excluded.
- Reuses shared hook / notes modal — no parallel POSTs.
- AST-1478 boundary clean (no report modal changes on this branch).
- Component + page tests pass on manifest (`AST-1477` pattern): 5 green.
- 409 error path covered on list Applied.

## Recommended actions (downstream)

1. **resolve-child:** fix `test_JobsRecommended.test.tsx` describe nesting.
2. **Optional:** add AST-1477 block to `pages.md` for bible parity.
3. **merge-child:** reconcile sibling sync drift on epic integration.

## Notes

Joan APPROVED @ `06a60cc2`. Product anchor: `d47122f2` + `080604f2` → tip `44fa5b67`. Spawn **Tests Passed** — trusted.

context_tokens≈48000

## Resolution

**Date:** 2026-08-25
**Vs Radia review** (`docs(AST-1477): Radia review — FIX-NOW describe nesting`):

| Finding | Disposition |
|---------|-------------|
| FIX-NOW — `test_JobsRecommended.test.tsx` describe nesting (AST-1057 / AST-1477 outside suite) | Cleared by Betty `test(AST-1477): nest AST-1057 + Applied mark inside JobsRecommended suite` → `merge-tests` @ `0fc2059d` (engineer `[qa-handoff]`; no product change) |
| discuss — `no-hardcoded-sets` / `PRE_APPLIED_MARK` | No product change (conforms / Joan-acceptable) |
| discuss — `pages.md` AST-1477 §6c mirror | Optional Betty bible; not blocking UT |
| advisory — sibling sync noise | No action on this child |

Manifest re-run after Betty nesting: green (`AST-1477|AST-1302|AST-1410`).
