# AST-1331 — Recommended list State column

- **Linear:** [AST-1331](https://linear.app/astralcareermatch/issue/AST-1331/recommended-list-state-column-add-job-state-to-recommended-job-list)
- **Parent:** [AST-1330](https://linear.app/astralcareermatch/issue/AST-1330/add-job-state-to-recommended-job-list-tables)
- **Publish ref:** `sub/AST-1330/AST-1331-recommended-list-state-column`

Add a sortable **State** column to every Recommended list table that displays each row’s existing job state string (the stored `JOB_STATES` key already on the list row, e.g. `BUILD_ARTIFACTS`). Meteorites stay one section; State makes in-progress vs ready vs untouched distinguishable without opening a job. No section regrouping, modal, API, or label-map work.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/JobsRecommended.tsx` | Add State column + `state` sort branch on every Recommended section table | ui |

**Do not touch:** `src/ui/api/**`, `src/utils/config.py`, State UI manifest / `StateUiContext`, `JobsSkipped.tsx` / `JobsInReview.tsx` / other job list pages, Recommended Job Modal / report components, `CandidateJobRowActions.tsx`, section grouping logic in `JobsRecommended.tsx`, `tests/**`, `docs/test-bible/**`.

**Do not add:** human-readable state label maps, hardcoded state allowlists, new config keys, API fields, or section membership changes.

---

## Stage 1: State column + sort on Recommended tables

**Done when:** Every visible Recommended section table (Meteorites and non-Meteorite sections) has a sortable **State** header; each row cell shows that job’s `state` string (raw key). Sorting by State toggles asc/desc like Job Title / Company / Updated. Section membership, phase score columns, Updated, row click → report, and Skip / other row actions are unchanged. No other files changed.

1. In `src/ui/frontend/src/pages/JobsRecommended.tsx`, in `sortRecommendedJobs`, after the `state_changed_at` branch and before the `phaseFields.includes(col)` branch, add a `col === "state"` branch that compares `(a.state || "").localeCompare(b.state || "")` (same string sort as `JobsSkipped.tsx` `sortJobs` for `"state"`). Do not invent a custom state order.

2. In the same file, in every section table `<thead>` row, insert a **State** column header **after Company** and **before** the `phase_score_columns` map, matching peer sortable headers:

```tsx
                      <th className="sortable" onClick={() => handleSort(sec.state, "state")}>
                        State{sortIndicator(sec.state, "state")}
                      </th>
```

Do not wrap this header in a Meteorites-only condition — AC requires State on every visible Recommended section table.

3. In the same file, in every section table `<tbody>` row, insert a State cell in the same column position (after Company `<td>`, before the phase-score `<td>` map):

```tsx
                        <td>{job.state || "\u2014"}</td>
```

Display the stored key only. Do not map through section labels, `legacyStateSectionLabel`, or any display enum. Empty/missing `state` uses the same em dash as Job Title.

4. Leave alone (verify by reading, do not edit for this ticket):
   - `sections` useMemo (Meteorite prefix split, `manifest.jobs.recommended.sections` grouping, legacy unmapped sections).
   - Default sort `{ col: "state_changed_at", asc: false }`, `handleSort` toggle behavior, phase score columns, Updated / `<Time>`, `CandidateJobRowActions`, `openJobReport` row click, modal / toast wiring.
   - API call `GET /api/jobs?view=recommended&…` — `state` is already on each row (`Job.state`); do not change the client URL or response shaping.

⚠️ **Decision:** Column placement after Company / before phase scores, matching Skipped floor State placement and keeping Meteorite triage early in the row. Raw `job.state` string only — parent/child boundaries forbid inventing human-readable labels.

⚠️ **Decision:** Single-file UI change. List rows already carry `state`; no API or config work. Peer sort pattern already exists on Skipped (`col === "state"` + localeCompare).

---

## Estimate

Confirm Chuckles estimate: 2 — agree

## Review stub (Katherine / build)

**Publish ref:** `origin/sub/AST-1330/AST-1331-recommended-list-state-column`  
**Product commits:** `a7c0738f` (sortable State column on Recommended list tables)

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1331
**Overall:** APPROVED
**Publish ref:** `sub/AST-1330/AST-1331-recommended-list-state-column` @ `68ff11567decff69ee7a7efc8793637f135e8428`

### Traceability

AC1–AC5 → Stage 1 (`JobsRecommended.tsx`: `sortRecommendedJobs` `state` branch, State header/cell after Company before phase scores, per-section sort via existing `sections.map` loop).

### Findings

(none)

context_tokens≈22000

## QA test manifest

`origin/sub/AST-1330/AST-1331-recommended-list-state-column` @ merge-tests → `origin/tests` `e581b21caaebb1174cfcc3bc157049498888dec6`

1. **Existing coverage (bible-backed):**
   - `tests/component/frontend/pages/test_JobsRecommended.test.tsx` — groups/phase scores, Company sort, row → JAR, Skip actions, AST-1057 Meteorites
2. **Broken / obsolete:** none.
3. **Gaps (this pass):**
   - `AST-1331: State column on every section; Meteorites show distinct raw state keys`
   - `AST-1331: State header sorts Meteorites by raw state asc then desc`
   - `AST-1331: empty state cell shows em dash`

**Integration:** none.

**Run:**
```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_JobsRecommended.test.tsx
```

**Bible:** `docs/test-bible/frontend/pages.md` shasum `be40c493823eb3bab344f0cfd052a543a89fe012`

— Betty

## Radia review

# Radia review — AST-1331

**Rubric:** code-rubric.v1  
**Ticket:** AST-1331  
**Publish ref:** `sub/AST-1330/AST-1331-recommended-list-state-column` @ `550aecb4040765bd7efd0507106bfcfcd209c23b`  
**Overall:** DISCUSS  
**Baseline:** `origin/dev` … `origin/sub/AST-1330/AST-1331-recommended-list-state-column` (7 files, +345 / −1)

---

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | no core/agent diff |
| astral.agent.do-task-delegation | scoped | not-applicable | no core/agent diff |
| astral.agent.grade-vector-validation | scoped | not-applicable | no core/agent diff |
| astral.batch.batch-id-first | scoped | not-applicable | no batch/dispatcher diff |
| astral.batch.batch-id-format | scoped | not-applicable | no batch diff |
| astral.batch.claim-process-release | scoped | not-applicable | no batch diff |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | no batch diff |
| astral.config.config-source-of-truth | scoped | not-applicable | no config.py diff |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | no config/secrets diff |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no debug artifact paths |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | no spikes diff |
| astral.dispatch.seed-auto-false | scoped | not-applicable | no dispatch diff |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | no dispatch diff |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single `ast-1331-*.md` plan doc added |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty touched tests/bible only |
| astral.git.engineer-test-tree-ban | scoped | conforms | product diff is `JobsRecommended.tsx` only |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | ui-only product change |
| astral.layers.import-direction | scoped | conforms | no new cross-layer imports |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no scripts diff |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | raw `job.state` display is plan-bound; no new UI business rules |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | no coat-check paths |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | no consult/render paths |
| astral.idioms.require-auth-on-protected-endpoints | scoped | not-applicable | no API/auth diff |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | no seed diff |
| astral.seed.archie-catalog-wins | scoped | not-applicable | no seed diff |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | no seed diff |
| astral.seed.define-approved | scoped | not-applicable | no seed diff |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | no seed diff |
| astral.seed.other-via-coverage-join | scoped | not-applicable | no seed diff |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | no data layer diff |
| astral.standards.database-header-inventory | scoped | not-applicable | no database/migrations diff |
| astral.standards.debug-contract-gated | scoped | not-applicable | no debug logging diff |
| astral.standards.dry-and-focused-functions | scoped | conforms | minimal sort/header/cell additions |
| astral.standards.in-scope-only | scoped | needs-discussion | AST-1334 test/bible deltas on AST-1331 ref |
| astral.standards.logging-via-utils | scoped | not-applicable | no logging diff |
| astral.standards.names-not-ticket-ids | scoped | conforms | test titles use ticket ids per bible convention |
| astral.standards.no-cross-contamination | scoped | needs-discussion | sibling AST-1334 work bundled in merge-tests SHA |
| astral.standards.no-hardcoded-sets | scoped | conforms | no state allowlists or label maps added |
| astral.standards.public-then-helpers | scoped | conforms | sort branch inline in existing helper |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | no utils diff |
| astral.state.core-decides-transitions | scoped | not-applicable | no state transition logic |
| astral.state.job-prior-states-enforced | scoped | not-applicable | display-only; no transition writes |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no run/dispatcher diff |
| astral.ui.frontend-file-placement | scoped | conforms | change in `pages/JobsRecommended.tsx` |
| astral.ui.naming-conventions | scoped | conforms | matches peer list-page patterns |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no server/worker diff |
| orch.git.betty-merge-tests-one-sha | universal | conforms | single `merge-tests(AST-1331)` commit |
| orch.git.commit-vocabulary | universal | conforms | `code`/`test`/`merge-tests`/`docs` prefixes used |
| orch.git.flow-direction-inviolable | universal | conforms | sub publish ref topology |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1330/AST-1331-…` |
| orch.git.merge-on-checkout | universal | conforms | no merge violation in diff |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | no evidence of forbidden git ops |
| orch.git.no-dev-agent-branches | universal | conforms | sub branch only |
| orch.git.one-epic-worktree-per-parent | universal | conforms | N/A to diff content |
| orch.git.three-permanent-branches | universal | conforms | N/A to diff content |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | no product-policy override in diff |
| orch.pipeline.plan-is-bible | universal | conforms | Stage 1 product matches plan |
| orch.pipeline.project-scoped-queues | universal | conforms | N/A to diff |
| orch.pipeline.status-gates-skill-entry | universal | conforms | reviewed at Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | N/A to diff |
| orch.roles.betty-owns-test-tree | universal | conforms | test/bible edits are Betty lane |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | N/A to diff |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Katherine product commit only touches planned file |
| orch.roles.pre-commit-path-bans | universal | conforms | no banned-path commits observed |

Registry reports **65** active statutes; **64** rows scored from `canon/statutes/README.md` § Harvested corpus (full active set per registry).

---

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| none cited | — | plan/parent cite peer `JobsSkipped` sort only, not a catalog pattern id |

---

## Plan adherence

**Product (Katherine / `a7c0738f`):** Matches Stage 1 and Joan traceability AC1–AC5.

- `sortRecommendedJobs`: `col === "state"` with `(a.state \|\| "").localeCompare(b.state \|\| "")` inserted after `state_changed_at`, before `phaseFields` — matches plan and `JobsSkipped.tsx` peer.
- State `<th>` / `<td>` after Company, before phase-score columns, inside `sections.map` — every visible section table gets the column (Meteorites + vetted sections).
- Cell shows raw stored key; empty → `\u2014` — matches plan; no label maps or section regrouping.
- Left alone: section grouping, default sort, row click → report, Skip/actions, API URL — no API/config/modal edits in product diff.
- **Estimate 2:** footprint fits (single product file, small delta).

**Tests (Betty / merge-tests):** AST-1331 cases in `test_JobsRecommended.test.tsx` align with manifest gaps (4 State headers, Meteorite raw keys, asc/desc sort, em dash). Describe-brace fix (AST-1057 block kept inside `describe`) is correct hygiene.

**Joan:** APPROVED; no Excluded statute list — no straggler callout required.

---

## Frame diff

| Area | Planned | Landed |
|------|---------|--------|
| Product | `JobsRecommended.tsx` State column + sort | ✓ exactly as staged |
| Tests | `test_JobsRecommended.test.tsx` AST-1331 cases | ✓ + describe structure fix |
| Bible | `pages.md` AST-1331 block | ✓ |
| **Unexpected** | — | `test_Modal.test.tsx`, `test_JobAnalysisReportModal.test.tsx`, `components.md` AST-1334 block (sibling AST-1329/1334) |

---

## Findings

### discuss — sibling AST-1334 test/bible on AST-1331 publish ref

**Locations:** commits `09363cc3`, merge-tests `550aecb4`; `tests/component/frontend/components/test_Modal.test.tsx`, `test_JobAnalysisReportModal.test.tsx`, `docs/test-bible/frontend/components.md`

**What:** Branch carries `test(AST-1334)` for `Modal` `showFooter={false}` and JAR footer omission, plus bible documentation for AST-1334. No matching product code on this ref — `showFooter` is absent from `Modal.tsx` and `JobAnalysisReportModal.tsx` on both `origin/dev` and this sub tip.

**Why it matters:** Betty’s manifest ran only `test_JobsRecommended.test.tsx`, so **Tests Passed** is valid for the manifest scope. Running the AST-1334 bible command or the Modal/JAR files on this ref would fail (tests assert props/behavior that do not exist). Cross-ticket boundary per plan “Do not touch” modal components and §5d sibling-scope rule.

**Downstream (Chuckles / Betty — not Katherine product):**

1. Remove AST-1334 commits from the AST-1331 `origin/tests` SHA **or** publish AST-1334 product on its own sub before merging those tests.
2. Re-pin `merge-tests(AST-1331)` after tests SHA is AST-1331-only.
3. Optionally run Modal/JAR component tests on the corrected ref to confirm green beyond manifest scope.

**Not fix-now for Katherine:** product delta is clean; engineer did not add AST-1334 tests.

### advisory — manifest scope vs branch integrity

Manifest-only execution masked latent red tests on the same publish ref. Worth noting in parent epic thread so merge-child / prep-uat does not assume full component tier green.

---

## What’s solid

- Peer parity with Skipped state sort (`localeCompare` on raw key, no custom order).
- Column placement and per-section sort via existing `sections.map` / `handleSort(sec.state, "state")` — minimal, readable diff.
- Raw key display respects parent/child boundary (no label-map scope creep).
- AST-1331 component tests exercise the real AC (all sections, Meteorite distinct keys, sort toggle, em dash).

---

## Notes

- Status gate: spawn prompt **Tests Passed** — trusted, no re-fetch.
- No plan-rubric Excluded table in Joan artifact.
- §5f / §5g / database / batch lenses: not applicable.
- G1 (`job.state \|\| "\u2014"`): plan-required empty display, not config-driven conditional logic.

---

## Recommended actions (downstream only — Radia does not execute)

1. Chuckles: split or revert AST-1334 test/bible from AST-1331 merge-tests lineage before **User Testing** / ftr merge.
2. Betty: fresh `origin/tests` SHA scoped to AST-1331 (+ any shared harness fixes), one `merge-tests(AST-1331)`.
3. Katherine: **no product resolve-child** needed for AST-1331 itself unless Chuckles chooses to hold UT until test SHA is clean.

context_tokens≈18500

## Resolution

**2026-08-12 — Katherine / resolve-child**

- **Mandatory stale catch-up:** `sync-child` merged `origin/dev` → tip `0b418753` (`sync(dev): origin/dev`); republished `origin/sub/AST-1330/AST-1331-recommended-list-state-column` @ `0b418753` before resolve.
- **fix-now:** none (Radia: product delta clean; no Katherine product work).
- **discuss (sibling AST-1334 test/bible on this ref):** closed on this tip by the same `origin/dev` merge — `Modal.showFooter` and JAR `showFooter={false}` are now present; optional Modal/JAR component tests + Betty’s `test_JobsRecommended` manifest all green (49 tests). No `[qa-handoff]` / no product edit.
- **advisory:** noted; no action required for UT.
- **AST-1331 product:** unchanged since `a7c0738f` (State column + sort only).
