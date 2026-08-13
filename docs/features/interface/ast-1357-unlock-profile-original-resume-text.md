# AST-1357 — Unlock Profile Original Resume Text

**Linear:** [AST-1357](https://linear.app/astralcareermatch/issue/AST-1357)
**Parent:** [AST-1356](https://linear.app/astralcareermatch/issue/AST-1356) — Make profile original resume text read/write
**Publish ref:** `sub/AST-1356/AST-1357-unlock-profile-original-resume-text`

Remove the Candidate Profile ad-hoc lock that disables Original Resume Text when `artifacts.base_resume` is present (including the lock placeholder). The field stays on the existing Profile `values` / PUT save path and dirty-leave wiring from AST-1336; no Artifacts regenerate redesign, no new warning/config lock.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/CandidateProfile.tsx` | Delete `hasBaseResume` and stop setting `disabled` / lock placeholder on the Original Resume Text tab | ui |

**Do not touch:** `TabbedTextArea.tsx`, `useDirtyLeaveSaveThenNavigate.ts`, `App.tsx`, shapes/`config.py` Profile sections, Artifacts generate/regenerate UI or craft-resume paths, Contact fields, other Profile text tabs, Intake preamble, Admin session resume paste, `tests/**`, `docs/test-bible/**`, canon.

## Stage 1: Remove Original Resume Text lock

**Done when:** On Candidate Profile for a candidate that already has `artifacts.base_resume`, the Original Resume Text tab textarea is enabled, accepts typed/pasted edits, participates in dirty detection the same as Bio Summary / other text tabs, Save persists `context.raw_resume` via the existing `PUT /api/candidates/:id/data` body, Cancel restores the last loaded/saved value, and candidates without a base resume behave as today. No lock placeholder copy remains.

1. In `src/ui/frontend/src/pages/CandidateProfile.tsx`, delete the line:

   ```ts
   const hasBaseResume = Boolean(getByPath(values, "artifacts.base_resume"))
   ```

   It exists only to drive the resume lock (around the signature-image helpers). After deletion, `getByPath` remains used elsewhere in this file — do not remove the import.

2. In the same file, inside the `textTabs` map that builds `TextTab[]` from `tabSections`, replace the resume-special-case block with ordinary tab props — no `isResume`, no `disabled`, no lock placeholder:

   **As-is (remove):**

   ```ts
   const textTabs: TextTab[] = tabSections.map(sec => {
     const f = sec.fields[0]
     const isResume = f.key === "context.raw_resume"
     return {
       label: sec.label,
       key: f.key,
       disabled: isResume && hasBaseResume,
       // Prefer shapes placeholder; resume-lock override when base resume exists.
       placeholder: f.placeholder ?? (isResume && hasBaseResume
         ? "Locked — base resume has been generated from this text"
         : undefined),
       help: typeof f.help === "string" && f.help.trim() ? f.help : undefined,
     }
   })
   ```

   **To-be (exact):**

   ```ts
   const textTabs: TextTab[] = tabSections.map(sec => {
     const f = sec.fields[0]
     return {
       label: sec.label,
       key: f.key,
       placeholder: f.placeholder,
       help: typeof f.help === "string" && f.help.trim() ? f.help : undefined,
     }
   })
   ```

   ⚠️ **Decision:** Drop `disabled` entirely from these tabs rather than pass `disabled: false`. `TextTab.disabled` is optional; omitting it matches other unlocked tabs and avoids keeping dead lock wiring. Rejected: shapes/config flag for editability (`astral.layers.ui-config-driven-business-logic` — remove the React lock, do not invent a parallel rule). Rejected: clearing or invalidating `artifacts.base_resume` on edit (parent Boundaries).

3. Do **not** change `persistProfile`, `handleCancel`, `isDirty`, or `useDirtyLeaveSaveThenNavigate` wiring. Once the textarea is enabled, edits to `context.raw_resume` already flow through `onChange={set}` → `values` → the same dirty stringify compare and PUT body as other Profile fields (AST-1336). AC4 (Artifacts regenerate consumes saved text) is already product-owned via `context.raw_resume` / existing craft path — verify only that Save still writes that key; do not open Artifacts UI.

4. Frontend compile/lint only for this page change: from `src/ui/frontend`, `npx tsc -b --pretty false` and eslint on the touched file (same bar as adjacent Profile work). No product commits in `tests/**`.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1357
**Overall:** APPROVED
**Publish ref:** `sub/AST-1356/AST-1357-unlock-profile-original-resume-text` @ `58dd9eccca6aebbb7be87d0f4668691acaf5dea3`

## Traceability
AC 1–6 → Stage 1 (remove `hasBaseResume` lock in `CandidateProfile.tsx`; existing `values` / PUT persist / `handleCancel` / `isDirty` / `useDirtyLeaveSaveThenNavigate` unchanged; AC4 verify-only via `context.raw_resume` save path).

## Findings

### acceptable
- **Location:** Parent Architectural definition — `pattern.ui.dirty-leave-save-then-navigate`
- **Finding:** Pattern catalog entry is `status: proposed` (not `approved`).
- **Recommendation:** Acceptable here — citation inherited from parent AST-1356; plan does not invent new dirty-leave wiring and matches the pattern’s solution shape (hook unchanged; enabling the textarea lets `context.raw_resume` participate in existing dirty/save flow).

No `fix-now` or `discuss` findings. R1–R6 pass: single-file `ui` scope; lock removal aligns with `astral.layers.ui-config-driven-business-logic`; placement and in-scope boundaries honored; DRY via deletion not parallel paths; layer/import surface untouched.

context_tokens≈15000

## Review stub (Katherine / build)

**Publish ref:** `origin/sub/AST-1356/AST-1357-unlock-profile-original-resume-text`
**Product commits:** `8e58e420` (remove hasBaseResume lock + placeholder on Original Resume Text tab)

## QA test manifest

`origin/sub/AST-1356/AST-1357-unlock-profile-original-resume-text` @ merge-tests → `origin/tests` `47c9bb12b8efad3566f58c19bf9ab1241657e092`

1. **Existing coverage (bible-backed):**
   - `tests/component/frontend/pages/test_CandidateProfile.test.tsx` — Profile §6c load/save/Cancel + AST-1336 dirty-leave (still required regression)
2. **Broken / obsolete (revised this pass):**
   - `restores values on cancel and locks resume text when base resume exists` — dropped resume `toBeDisabled()`; Cancel-only case kept as `restores values on cancel`
3. **Gaps (this pass):**
   - `CandidateProfile — AST-1357 unlock original resume text` — with base resume: enabled + no lock placeholder; Save PUT `context.raw_resume`; Cancel restores last saved; without base resume still editable

**Integration:** none (no existing scenario asserts Profile resume lock).

**Run:**
```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_CandidateProfile.test.tsx
```

**Bible:** `docs/test-bible/frontend/pages.md` shasum `85db4ed94a5602c3e9f9d3002c2f4d813c84a087`

— Betty

## Radia review

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1357
**Publish ref:** `sub/AST-1356/AST-1357-unlock-profile-original-resume-text` @ `e12a541be4af08eba8c97b63e352a0c29cda7415`
**Overall:** CLEAN

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | no `src/core/**` or agent paths in diff |
| astral.agent.do-task-delegation | scoped | not-applicable | no `src/core/**` or agent paths in diff |
| astral.agent.grade-vector-validation | scoped | not-applicable | no `src/core/**` or agent paths in diff |
| astral.batch.batch-id-first | scoped | not-applicable | no batch/dispatcher paths in diff |
| astral.batch.batch-id-format | scoped | not-applicable | no batch/dispatcher paths in diff |
| astral.batch.claim-process-release | scoped | not-applicable | no batch/dispatcher paths in diff |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | no batch/dispatcher paths in diff |
| astral.config.config-source-of-truth | scoped | not-applicable | no `src/config.py` or config paths in diff |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | no secrets/env wiring in diff |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no `debug/**` paths in diff |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | no `debug/**` paths in diff |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | no dispatch paths in diff |
| astral.dispatch.seed-auto-false | scoped | not-applicable | no dispatch paths in diff |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single `docs/features/interface/ast-1357-*.md` for ticket |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty lane: tests + bible only; no `src/` or `docs/features/` on Betty commits |
| astral.git.engineer-test-tree-ban | scoped | conforms | product commit `8e58e420` touches only `CandidateProfile.tsx` |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | no coat-check / data-store paths in diff |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | no render-verdict paths in diff |
| astral.idioms.require-auth-on-protected-endpoints | scoped | not-applicable | no API/auth handler paths in diff |
| astral.layers.core-vs-external-bright-line | scoped | conforms | ui-only change; no core/external boundary bend |
| astral.layers.import-direction | scoped | conforms | no new cross-layer imports in touched ui file |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no `scripts/**` paths in diff |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | removes React-side resume lock; defers to shapes placeholder |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | no seed/json table paths in diff |
| astral.seed.archie-catalog-wins | scoped | not-applicable | no seed paths in diff |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | no seed/boot paths in diff |
| astral.seed.define-approved | scoped | not-applicable | no seed paths in diff |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | no seed paths in diff |
| astral.seed.other-via-coverage-join | scoped | not-applicable | no seed paths in diff |
| astral.standards.database-header-inventory | scoped | not-applicable | no `src/data/database.py` or migrations in diff |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | no `src/data/**` paths in diff |
| astral.standards.debug-contract-gated | scoped | not-applicable | no `debug=` surfaces or logging contract changes |
| astral.standards.dry-and-focused-functions | scoped | conforms | deletes special-case lock branch; uniform `textTabs` map |
| astral.standards.in-scope-only | scoped | conforms | scope limited to Profile resume unlock; boundaries honored |
| astral.standards.logging-via-utils | scoped | not-applicable | no logging changes |
| astral.standards.names-not-ticket-ids | scoped | conforms | no ticket-id naming in product code |
| astral.standards.no-cross-contamination | scoped | conforms | no Artifacts UI / craft / other ticket scope smuggled in |
| astral.standards.no-hardcoded-sets | scoped | conforms | removes hardcoded lock placeholder string |
| astral.standards.public-then-helpers | scoped | not-applicable | no new public API surface in diff |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | no `src/utils/**` paths in diff |
| astral.state.core-decides-transitions | scoped | not-applicable | no state/tracker/roster paths in diff |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no job-state paths in diff |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no run/dispatcher paths in diff |
| astral.ui.frontend-file-placement | scoped | conforms | change stays in `src/ui/frontend/src/pages/` |
| astral.ui.naming-conventions | scoped | conforms | no naming violations in touched file |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no `server.py` / gunicorn config in diff |
| orch.git.betty-merge-tests-one-sha | universal | conforms | `merge-tests(AST-1357)` lands tests at single Betty SHA |
| orch.git.commit-vocabulary | universal | conforms | commits use standard `code`/`test`/`docs`/`merge-tests` prefixes |
| orch.git.flow-direction-inviolable | universal | conforms | work on `sub/AST-1356/AST-1357-*`; diff vs `origin/dev` |
| orch.git.ftr-sub-topology | universal | conforms | child publish ref under parent `sub/AST-1356/` |
| orch.git.merge-on-checkout | universal | conforms | standard epic worktree / sub-branch topology |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | no cherry-pick/rebase/force in review artifacts |
| orch.git.no-dev-agent-branches | universal | conforms | no `dev-*` agent branches |
| orch.git.one-epic-worktree-per-parent | universal | conforms | review in `astral-AST-1356` worktree |
| orch.git.three-permanent-branches | universal | conforms | sub branch off ftr/dev pattern intact |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | stale-base-resume product choice documented in plan; not reopened in code |
| orch.pipeline.plan-is-bible | universal | conforms | implementation matches Stage 1 to-be exactly |
| orch.pipeline.project-scoped-queues | universal | conforms | scoped child ticket; no queue violation |
| orch.pipeline.status-gates-skill-entry | universal | conforms | reviewed at Tests Passed per pipeline |
| orch.roles.archie-approves-statutes | universal | conforms | no new statutes introduced |
| orch.roles.betty-owns-test-tree | universal | conforms | test + bible updates via Betty merge-tests lane |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee Katherine; Radia read-only |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Katherine assignee through Tests Passed |
| orch.roles.pre-commit-path-bans | universal | conforms | no banned-path commits evident in diff |

**Active corpus count:** 64 statutes scored (README registry cites 65; one id not `status: active` at this SHA).

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.ui.dirty-leave-save-then-navigate | conforms | Inherited from parent AST-1356; `status: proposed` — hook unchanged; enabling textarea lets `context.raw_resume` use existing dirty/save path (Joan plan acceptable) |

## Plan adherence

- Product diff matches plan **to-be** verbatim: `hasBaseResume` deleted; `textTabs` map has no `isResume` / `disabled` / lock placeholder override.
- `persistProfile`, `handleCancel`, `isDirty`, `useDirtyLeaveSaveThenNavigate` untouched per plan §3.
- Do-not-touch list honored: no TabbedTextArea, hook, App, shapes/config, Artifacts UI, or craft paths.
- Estimate **2** still fits: one ui file deletion-focused change + Betty tests/bible.
- Betty manifest gaps closed: AST-1357 describe block covers enabled + Save PUT + Cancel restore + no-base-resume regression; obsolete `toBeDisabled` assertion removed.
- AC4 (Artifacts regenerate consumes saved text): verify-only per plan — new test asserts PUT body includes `context.raw_resume`; no Artifacts UI scope opened.

## Findings

### advisory

- **Location:** `docs/features/interface/ast-1357-unlock-profile-original-resume-text.md` § QA test manifest — Bible shasum
- **Finding:** Manifest cites `pages.md` shasum `85db4ed94a5602c3e9f9d3002c2f4d813c84a087`; tip `pages.md` at publish ref is `76e6fca525b7c0b2eb64b6d50249cd40c2524b0c8632ce10e7c08a4985a1756b` (AST-1357 block added post-manifest).
- **Recommendation:** Betty/trackers may refresh manifest shasum on next bible touch — not engineer fix-now.

- **Location:** Parent / Joan — `pattern.ui.dirty-leave-save-then-navigate`
- **Finding:** Catalog entry remains `status: proposed` globally (Archie approval pending AST-1315).
- **Recommendation:** No code action on AST-1357; track parent epic / AST-1315 for approval — hook wiring unchanged here.

## Frame diff

- **ui:** `CandidateProfile.tsx` — remove `artifacts.base_resume` gate (`hasBaseResume`); Original Resume Text tab no longer `disabled` or lock-placeholder when base resume exists; uniform `textTabs` props (`placeholder` from shapes only).
- **tests:** `test_CandidateProfile.test.tsx` — drop obsolete resume `toBeDisabled` assertion; add `CandidateProfile — AST-1357 unlock original resume text` (with/without base resume: enabled, Save PUT `context.raw_resume`, Cancel restore).
- **docs:** issue doc + `docs/test-bible/frontend/pages.md` AST-1357 manifest block.

## What's solid

- Minimal, plan-exact deletion — removes UI business lock without parallel config flag or base-resume invalidation (explicit plan rejection).
- Aligns with `astral.layers.ui-config-driven-business-logic` and `astral.standards.no-hardcoded-sets`.
- Tests directly assert the unlock behavior Betty flagged; dirty-leave regression path preserved via existing AST-1336 wiring.

## Notes

- Joan plan-rubric verdict attached (APPROVED); no Excluded statute list in attachment — no C4 straggler callouts.
- §5f / §5g not applicable (no backend debug or LLM external diffs).
- §5a C6 aids: imports, layers, silent failure, logging, batch — no issues on touched ui file.

context_tokens≈22000
