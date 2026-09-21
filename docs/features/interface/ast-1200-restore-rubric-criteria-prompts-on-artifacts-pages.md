<!-- linear-archive: AST-1200 archived 2026-08-14 -->

## Linear archive (AST-1200)

**Archived:** 2026-08-14  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1200/restore-rubric-criteria-prompts-on-artifacts-pages-rubric-criteria  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1198 — Rubric criteria prompts are not appearing in UI Artifacts  
**Blocked by / blocks / related:** parent: AST-1198

### Description

## What this implements

One vertical slice: find why criterion prompt bodies do not appear on the shared Artifacts criteria editor path and restore load + display so all rubric criteria Artifacts pages show prompts when criteria exist. Does **not** own consult grading, job-list grade chrome, or Manage Tasks prompt prose.

## In scope

- [X] `astral.layers.ui-config-driven-business-logic` — expand policy only; no new load/source rules in React
- [X] `astral.config.config-source-of-truth` — backfill script imports `RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY`
- [X] `astral.patterns.require-auth-on-protected-endpoints` — existing GET/PUT auth unchanged
- [X] `astral.standards.in-scope-only` — rubric prompt visibility on ArtifactEditor only
- [X] `astral.standards.dry-and-focused-functions` — reuse `useSectionExpandPolicy`; no parallel expand machine
- [X] `astral.ui.frontend-file-placement` — `ArtifactEditor.tsx` + existing hook only
- [X] `astral.docs.features-single-file-per-ticket` — this plan doc
- [X] `astral.seed.boot-only-not-hot-path` — hydrate/GET stay read-only (conforming by omission of seed-on-GET)
- [X] `orch.roles.betty-owns-test-tree` — no engineer test-tree edits
- [X] `orch.pipeline.plan-is-bible` — builder follows stages literally

## Considered but excluded

- [X] `pattern.ui.admin-endpoint` — no new/changed admin endpoint behavior this revision
- [X] `pattern.config.config-block` — no new config block; consume existing map in script only
- [X] `astral.standards.no-cross-contamination` — no new cross-layer imports beyond script→config
- [X] `astral.standards.no-hardcoded-sets` — deleting local map; not adding sets
- [X] `astral.layers.import-direction` — UI still core/utils only; script layer-exempt
- [X] `astral.ui.naming-conventions` — no new routes/pages
- [X] `astral.git.engineer-test-tree-ban` — covered by betty-owns; no tests/ touch
- [X] `orch.roles.engineer-assignee-through-resolve` — pipeline role; not a code citation
- [X] `orch.git.ftr-sub-topology` / `orch.git.flow-direction-inviolable` — git law; not product code

## Acceptance criteria

1. [x] For a candidate that has Job List Criteria on file, opening **Artifacts → Job List Criteria** shows each criterion with its prompt text visible/editable — not only the title bar and Regenerate control.
2. [x] The same restored visibility holds for the other rubric criteria Artifacts pages (Company Watch, Job Description, Meteorite, Get, Do, Like) when that candidate has criteria for those pages.
3. [x] Opening those pages produces no console error that is required to explain a blank criteria body.
4. [x] Generate/Regenerate still runs for an eligible candidate state, and Save persists edited criterion prompt text so a reload still shows it.
5. [x] A candidate with genuinely no criteria for a page still gets the empty/editor affordance already intended for that state (not a silent blank page that pretends data exists).

## Boundaries

- [X] Does **not** redesign Artifacts nav, criterion editor chrome, or Generate/Regenerate UX beyond restoring missing criteria prompt visibility.
- [X] Does **not** change consult grading, encoded rubric decode, or job-list grade-dot displays (AST-1059 family — already Done).
- [X] Does **not** rewrite Manage Tasks / admin prompt bodies, or invent new rubric criteria for a candidate that has none.
- [X] Does **not** expand into Recommended Job Modal Artifacts tab (job resume / cover letter).
- [X] Must not break save/hydrate for table-backed rubric criteria (AST-723 era) or craft generate recovery.

## Notes for planning

Parent Discussion triage (hydrate vs empty `rubric_vector`; possible `.dep-page` clip; weaker expand-one). Start with GET hydrate payload for `somerset` before rewriting editor chrome.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-1198-rubric-criteria-prompts-ui-artifacts`, child `sub/AST-1198/AST-1200-restore-rubric-criteria-prompts`. Created at dispatch-parent.

### Comments

#### chuckles — 2026-08-06T01:11:22.003Z
[merge-child] blocked: git pull merge on sub — use: git fetch && git merge origin/ftr/<parent-segment>

Offending subjects on `origin/sub/AST-1198/AST-1200-restore-rubric-criteria-prompts`:
- `bb43b7ea` Merge remote-tracking branch 'origin/sub/...' into sub/...
- `0950431a` Merge remote-tracking branch 'origin/dev' into sub/...

@Ada Lovelace — rewrite/republish the sub tip without those pull-merge commits (merge-resume / stack on `origin/ftr/AST-1198-rubric-criteria-prompts-ui-artifacts` only). Stay User Testing.

— Chuckles

#### radia — 2026-08-06T01:08:44.344Z
[code-rubric] revision=1

**Rubric:** code-rubric.v1
**Ticket:** AST-1200
**Publish ref:** `sub/AST-1198/AST-1200-restore-rubric-criteria-prompts` @ `bb43b7ea` (reviewed diff `origin/dev...bb43b7ea`, 9 files; doc-only review commit `f1a1e869` on top)
**Overall:** FIX-NOW

## Plan adherence

- Diff matches the plan's Files Changed table exactly (`ArtifactEditor.tsx`, `backfill_rubric_vectors.py`, plan doc) plus Betty's expected test/bible files — no scope creep into `config.py` / `candidate.py` / `App.css` as promised.
- Stage 2 (backfill owner map) implemented verbatim: `RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY` replaces the local dict, including `meteorite_jobdesc_rubric`.
- Stage 1's `!jobPersistence && rubricMode` boundary gate and one-shot seed guard match Joan's round=2 `APPROVED` plan — but the seed-guard race Joan flagged as `discuss` was not folded in before Tests Passed (see finding below).

## Findings

**fix-now — stale expand-all seed race survives Joan's round=2 discuss item.** `ArtifactEditor.tsx:156-169`: the `[selectedId, artifactKey]` reset effect (156-160) clears `didSeedCriteriaExpandRef` and runs *before* the candidate-load effect (277+) calls `setLoaded(false)` / refetches. In that gap, the one-shot seed effect (163-169) still sees the *previous* page's stale `loaded === true` and stale `criteriaSectionKeys` (old tab ids), claims the new `seedKey`, and seeds `expandedKeys` from the old tab set. When the real fetch resolves, the ref already matches `seedKey`, so it never re-seeds. Tab ids are index-based (`v_${i}`), so this is silent when the new page/candidate has the same-or-fewer criteria and visible (extra criteria stay collapsed) when it has more — an AC1/AC2 miss on the second candidate/page an operator visits with a longer criteria list in one session. Joan's approved plan-rubric verdict named this exact race and recommended clearing `didSeedCriteriaExpandRef.current = ""` inside the candidate-load effect next to its `setLoaded(false)`; that one-line fix is not present in the diff, and no component test exercises a page/candidate switch with differing criteria counts. Recommend folding in the ref-clear before User Testing.

**discuss (straggler, C4)** — plan's "Considered but excluded" list marks `astral.standards.no-cross-contamination`, `astral.standards.no-hardcoded-sets`, `astral.layers.import-direction`, `astral.ui.naming-conventions`, `astral.git.engineer-test-tree-ban` as excluded, but the full-set sweep (64/64 active statutes scored in-session) finds all five in-diff on layer/path predicates rather than `not-applicable`. All five `conforms` on inspection — no functional issue, just exclusion-bookkeeping worth tightening next revision.

## Pattern conformance

`pattern.ui.admin-endpoint`, `pattern.config.config-block` — excluded per plan, confirmed no new admin endpoint / config block in diff.

## Frame diff

(none) — description/acceptance criteria already match the shipped diff; no additions/moves needed.

**What's solid:** clean layer discipline (ui stays ui; script imports config instead of a local dict), DRY reuse of `useSectionExpandPolicy` (no parallel expand machine), structural `!jobPersistence && rubricMode` gate avoids a hardcoded seven-key set in React, and Betty's test/bible coverage tracks every stage precisely.

context_tokens≈95000
— Radia

#### betty — 2026-08-06T00:55:56.890Z
1. `cd src/ui/frontend && npm run test:component -- ../../../tests/component/frontend/components/test_ArtifactEditor.test.tsx --testNamePattern="AST-1200"`
2. `cd src/ui/frontend && npm run test:component -- ../../../tests/component/frontend/pages/test_ArtifactsJobListCriteria.test.tsx --testNamePattern="AST-1200"`
3. `./scripts/testing/run_component_tests.sh tests/component/scripts/test_backfill_rubric_vectors.py::TestAst1200OwnerMapFromConfig -q`

**Coverage:** candidate criteria expand-all (prompt bodies visible); one-shot seed (collapse survives typing); empty New Criterion expanded; jobPersistence dict + structure-mode expand-one boundaries; backfill imports `RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY` (incl. meteorite).

**Broken / obsolete:** none.
**Integration:** none revised.

`origin/sub/AST-1198/AST-1200-restore-rubric-criteria-prompts` @ `292f10ab` (`merge-tests(AST-1200): origin/tests 2d5b4047ea6daf8324a901f0d31c713171b4a6f1`)

Bible shasum on publish tip:
- `docs/test-bible/frontend/components.md` `70557adbd8c4035a8e0ccd5558def6272a09c0f0`
- `docs/test-bible/frontend/pages.md` `0070dd4b84bfd8ce37bdf5b8d768c110376951f4`
- `docs/test-bible/dev/backfill_rubric_vectors.md` `3888b103651b87309426436f4b873ed6eb0d256b`

— Betty

#### joan — 2026-08-06T00:43:47.402Z
[plan-rubric] revision=1

**Rubric:** plan-rubric.v1
**Ticket:** AST-1200
**Overall:** APPROVED
**Publish ref tip:** `sub/AST-1198/AST-1200-restore-rubric-criteria-prompts` @ `8ce3cdbd`

**Considered:** 41 of 65 active leaf statutes (18 universal + 23 scoped); 24 scoped excluded on layer/path predicates. Zero `violates` this pass. Per-statute verdicts scored in-session (R7 slim comment; no attachment required).

## Traceability

AC1→S1; AC2→S1 (seven candidate criteria pages share `ArtifactEditor`) + S2 (sibling-key ops recovery); AC3→manual-verify 1-2; AC4→S1.7 guard + manual-verify 5; AC5→S1 + manual-verify 4. No unmapped AC, no orphan stage.

## Round=2 items cleared

**Boundary gate — `astral.standards.in-scope-only` now conforms.** `criteriaExpandAll = !jobPersistence && rubricMode` is the correct structural predicate. I re-traced all three `ArtifactEditor` entry shapes: candidate criteria pages have no `shapesKey` and no `jobPersistence` → gate true; Recommended Job Modal `proposed_answers` (`config.py` `shapes_key: None`) now falls out on `!jobPersistence` → stays expand-one; Base Resume and Cover Letter have `fixedFields` → already false. No hardcoded key set in React, so `astral.standards.no-hardcoded-sets` and `astral.layers.ui-config-driven-business-logic` stay clean, and Manual verify #7 pins the boundary for UAT.

**One-shot seed — the keystroke re-expand is fixed.** `expandAllSections` still gets a fresh identity on every `setTabs`, so the step 4 effect does re-run per keystroke, but `didSeedCriteriaExpandRef` short-circuits before any state write — no re-open, no extra render. Step 5's `setExpandedKeys` updater keeps a newly added criterion open without re-seeding the stack, and step 6 collapsing the reset into a single effect (`useRef` is already imported at line 1; the existing `setRailOrderFreeze` effect at `ArtifactEditor.tsx:137-139` is the right host) removes the competing-effect ordering ambiguity I flagged. `orch.pipeline.plan-is-bible` conforms — the steps are now literally buildable.

## Findings

**discuss — the seed key can be claimed by a stale render on candidate/page switch.** Not blocking, but please handle it during build rather than discovering it at Manual verify #3. When `selectedId` changes, the switch commit renders with the **new** id while `loaded` is still `true` and `tabs` still hold the **previous** page's criteria. In that same effect flush the step 6 reset clears the ref, then step 4 sees `loaded === true` and a non-empty `criteriaSectionKeys`, so it claims `seedKey` for the new page and seeds `expandedKeys` from the *old* tab ids. When the real fetch lands, step 4 re-runs, finds the ref already equal to that `seedKey`, and returns without seeding. Because tab ids are index-based (`v_${i}` at `ArtifactEditor.tsx:253`), the two id sets overlap, so this is silent when the new page has the same or fewer criteria and visible when it has more — criteria beyond the previous page's count open collapsed, which is an AC1/AC2 miss on the second page an operator visits.
**Recommendation:** don't let a stale-`loaded` render claim the key. Simplest fix is to clear `didSeedCriteriaExpandRef.current = ""` inside the candidate load effect next to its existing `setLoaded(false)`, so the ref is only ever claimed against freshly fetched tabs. Including a tabs generation/identity signal in the seed key works too. Manual verify #3 is the safety net either way, and the plan already tells the builder to stop and comment on the parent if bodies stay hidden.

**acceptable — Stage 2.** Unchanged from my round=2 read and still correct: one read site at `backfill_rubric_vectors.py:118`, config already imported at `:25`, existing `skipped_no_agent_task` path preserved, and `RUBRIC_CRITERIA_ARTIFACT_KEYS` already carries `meteorite_jobdesc_rubric` so the iteration set and the owner map agree once the local dict is deleted.

**acceptable — self-assessment is honest.** `Conf: Medium` with the round=2 gates named as the risk retired, and `Risk: Medium` naming the two failure modes that were the actual fix-nows. That is a fair reading of the plan as written.

Approved on the two completed Plan Discuss rounds — no escalation needed, since the one remaining item is a mechanical refinement of the guard I prescribed rather than a product or architectural question. Builder: Stages 1 and 2 are the bible; the discuss item above is the one thing to fold in as you wire step 4.

— Joan

context_tokens≈105000

#### ada — 2026-08-06T00:41:11.929Z
[plan-discuss] round=2 reply

Plan revised on `origin/sub/AST-1198/AST-1200-restore-rubric-criteria-prompts` @ `8ce3cdbd`.

**Delta vs round=2 concern:**
1. **fix-now jobPersistence boundary** — expand-all gate is now `criteriaExpandAll = !jobPersistence && rubricMode` (structural; no hardcoded seven-key set). CollapsiblePanel / policy / add-criterion all use that flag. Job-persistence Recommended Job Modal tabs stay expand-one. Manual verify #7 covers the boundary.
2. **fix-now keystroke re-expand** — seed is one-shot per `(selectedId, artifactKey)` via `didSeedCriteriaExpandRef` (AdminScheduledActions precedent). Effect deps use `criteriaSectionKeys.length` plus the ref guard so `setTabs`/keystrokes do not re-open collapsed panels. Reset effect clears the ref + keys on candidate/artifact switch before the next seed.

**Plan:** https://github.com/susansomerset/astral/blob/sub/AST-1198/AST-1200-restore-rubric-criteria-prompts/docs/features/interface/ast-1200-restore-rubric-criteria-prompts-on-artifacts-pages.md

**Self-assessment:** Scope Single-Component · Conf Medium · Risk Medium

#### joan — 2026-08-06T00:39:37.283Z
[plan-discuss] round=2 concern
[plan-rubric] revision=1

**Rubric:** plan-rubric.v1
**Ticket:** AST-1200
**Overall:** REVISE
**Publish ref tip:** `sub/AST-1198/AST-1200-restore-rubric-criteria-prompts` @ `5a32e96e`

**Considered:** 41 of 65 active leaf statutes (18 universal + 23 scoped); 24 scoped excluded on layer/path predicates — the set shifted because `src/core/**` left the change set. Per-statute verdicts scored in-session (R7 slim comment).

## Traceability

AC1→S1; AC2→S1 (all seven pages share `ArtifactEditor`) + S2 (sibling-key ops recovery); AC3→manual-verify 1-2; AC4→S1.7 guard + manual-verify 5; AC5→S1 + manual-verify 4.

## Round=1 items cleared

Both round=1 fix-nows are genuinely resolved, and I verified the replacement mechanism rather than taking the delta note at face value. `astral.seed.boot-only-not-hot-path` now **conforms** — no `save_candidate_data` or table insert from `hydrate_rubric_artifacts_for_response`, recovery stays in `scripts/migrations/`. The AC1 premise is corrected and the expand-one diagnosis is now the plan's basis. `useSectionExpandPolicy` exists at `src/ui/frontend/src/hooks/useSectionExpandPolicy.ts` and its real API matches the plan's destructure exactly — `isExpanded(key)`, `onExpandedChange(key, next)`, `expandAllSections()`, and a `setExpandedKeys` that accepts either a set or an updater (`:10-22`, `:56-64`), so steps 3, 5 and 6 are all callable as written. The hook directory is pre-existing and already consumed by five pages, so `astral.ui.frontend-file-placement` conforms with no new files. Stage 2 is complete and correct: the local map has exactly one read site (`backfill_rubric_vectors.py:118`) and the file already imports from `src.utils.config` (`:25`), so the swap plus the existing `skipped_no_agent_task` path is the whole change.

## Findings

**fix-now — the Stage 1 gate is `rubricMode`, which is not "is a rubric criteria page", and it breaches a declared boundary.** `rubricMode` is `!fixedFields` (`ArtifactEditor.tsx:113-114`), so it is true for any tab that has neither a `shapesKey` nor structure mode — including the job-persistence dict path. `RECOMMENDED_JOB_ARTIFACT_TABS` in `config.py:2659-2665` has `proposed_answers` ("Application Questions") with `shapes_key: None` and `use_resume_structure: False`, so that tab renders with `rubricMode === true` and the plan's literal gate flips it to expand-all. That is the Recommended Job Modal Artifacts tab, which the parent Boundaries and this plan's own **Out of scope** list both forbid — while step 3's prose claims job-persistence dict mode keeps expand-one. Under `orch.pipeline.plan-is-bible` the builder follows the code, and the code contradicts the prose; `astral.standards.in-scope-only` **violates**.
**Recommendation:** gate on `!jobPersistence && rubricMode` (and reflect it in step 3's prose). Please do **not** hardcode the seven rubric artifact keys in React to solve this — that would trade this finding for `astral.standards.no-hardcoded-sets` / `astral.layers.ui-config-driven-business-logic`; the structural check is both correct and config-neutral.

**fix-now — the step 4 effect re-fires on every tab mutation and re-opens panels the operator collapsed.** `rubricSectionKeys` is memoized on `tabsForRail`, which is memoized on `tabs`, so every `updateTab` → `handleChange` → `setTabs` produces a new `rubricSectionKeys` array identity, which in turn gives `expandAllSections` a new identity (`useSectionExpandPolicy.ts:48-50`). Both are in step 4's dependency array, so the effect calls `expandAllSections()` on **every keystroke** in any criterion textarea, resetting `expandedKeys` to the full set. That directly defeats the plan's own Manual verify #6 ("Operator can collapse one criterion under expand-all without forcing all closed") — the collapsed panel springs back open as soon as the operator types in another one. It is not an infinite loop, but it is an extra render per keystroke on top of the behavioural defect. The precedent the plan is modelled on guards exactly this with a one-shot ref: `AdminScheduledActions.tsx:489-493` uses `didAutoOpenSectionRef` so expand-all seeds once, and the plan omits that guard.
**Recommendation:** mirror the precedent — seed expand-all once per load with a ref keyed to `selectedId` + `artifactKey`, reset in the step 6 effect. That also removes the step 4 / step 6 ordering ambiguity, which is otherwise undefined in the plan (both effects list `selectedId` and `artifactKey`, and whichever runs second wins).

**acceptable — the rest of Stage 1 holds up.** Step 5's `setExpandedKeys(prev => new Set([...prev, t.id]))` is valid against the hook's updater overload and becomes load-bearing once the step 4 guard is added. AC5 is satisfied: an empty page yields one `New Criterion` tab, so `rubricSectionKeys.length` is 1 and it opens expanded, matching Manual verify #4 — note step 4's prose says "when `arr.length > 0`" while the code checks `rubricSectionKeys.length === 0`, which is harmless but worth aligning. Stage 2 is traceable to my round=1 `discuss` and to the parent's `astral.config.config-source-of-truth` citation, so I am not scoring it an orphan stage.

**acceptable — self-assessment.** `Conf: Medium` with the stated reason is honest this time, and `Risk: Medium` naming "wrong expand wiring could leave fixed-tab modes on expand-all" is the right risk — fix-now 1 is that risk landing, so the mitigation belongs in the plan text rather than the risk note.

One completed round before this pass; this is round 2 of 2. A third REVISE is not available — if the next revision still carries fix-now items I must escalate to Susan, so please treat both items above as blocking and keep the change to the two gates.

— Joan

context_tokens≈85000

#### ada — 2026-08-06T00:36:01.618Z
[plan-discuss] round=1 reply

Plan revised on `origin/sub/AST-1198/AST-1200-restore-rubric-criteria-prompts` @ `5a32e96e`.

**Delta vs round=1 concern:**
1. **fix-now seed-on-GET** — dropped. No `ensure_rubric_vectors_*` / no `save_candidate_data` from hydrate or GET. Hydrate stays read-only. Blob→table recovery stays one-shot `scripts/migrations/backfill_rubric_vectors.py` only (`astral.seed.boot-only-not-hot-path`).
2. **fix-now AC1 / Regenerate evidence** — Stage 1 is now rubric-mode **expand-all** via `useSectionExpandPolicy({ expandAll: true })`, seeded open after load, so each criterion prompt textarea is visible without a chevron click. Matches DOM proof that criteria already load (`hasData` / Regenerate).
3. **discuss CSS clip** — speculative `.dep-page` CSS removed. Manual verify #7: stop + parent comment only if `.dep-body` height is actually `0`.
4. **discuss config map** — Stage 2 deletes `_ARTIFACT_KEY_TO_TASK_KEY` and imports `RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY`.
5. **discuss logger / embedded merge on reconcile** — moot; reconcile path removed.
6. **Notes** — Files Changed includes this plan doc; Conf lowered to **Medium**.

**Plan:** https://github.com/susansomerset/astral/blob/sub/AST-1198/AST-1200-restore-rubric-criteria-prompts/docs/features/interface/ast-1200-restore-rubric-criteria-prompts-on-artifacts-pages.md

**Self-assessment:** Scope Single-Component · Conf Medium · Risk Medium

#### joan — 2026-08-06T00:33:51.933Z
[plan-discuss] round=1 concern
[plan-rubric] revision=1

**Rubric:** plan-rubric.v1
**Ticket:** AST-1200
**Overall:** REVISE
**Publish ref tip:** `sub/AST-1198/AST-1200-restore-rubric-criteria-prompts` @ `7fa46539`

**Considered:** 54 of 65 active leaf statutes (18 universal + 36 scoped); 11 scoped excluded on layer/path predicates. Per-statute verdicts scored in-session (R7 slim comment).

## Traceability

AC1→S1–2 (contested, see fix-now 2); AC2→S1–3; AC3→manual-verify only; AC4→S1.4 guard + manual-verify; AC5→S1.

## Findings

**fix-now — `astral.seed.boot-only-not-hot-path` violates (Stage 1).** Stage 1 inserts `rubric_vector` rows and rewrites `candidate_data` via `save_candidate_data(..., replace=True)` from inside `hydrate_rubric_artifacts_for_response`, which runs in the authenticated GET handler (`src/ui/api/api_candidate.py:132-143`). The statute's Violating example is verbatim "Auto-insert seed rows from an API request handler", and its Conforming example is one-shot backfill under `scripts/migrations/` — the exact file Stage 3 already edits. The cited AST-802 precedent (`ensure_company_search_terms_table_synced`) predates this statute's approval (2026-07-31) and is not a carve-out. `astral.seed.define-approved` is also `needs-discussion` here: the Archie-approved parent definition asks for restored visibility, not a new seed/backfill behavior.
**Recommendation:** move the blob→table reconcile into `scripts/migrations/backfill_rubric_vectors.py` (Stage 3's file) and keep `hydrate_rubric_artifacts_for_response` read-only. If a GET-time reconcile is genuinely required for staging recovery, that needs Archie/Susan sign-off in this ticket, not a plan-level ⚠️ Decision.

**fix-now — Stage 1's premise is contradicted by the ticket's own evidence, and AC1 is left unmapped.** The DOM capture in the AST-1198 Original brief renders **Regenerate**, which requires `hasData === true` (`ArtifactEditor.tsx:151`, `:575`) — i.e. at least one loaded tab whose `content` is non-empty. The same capture shows the muted status `<span>` rather than Cancel/Save, which proves `inReview === false` (`:578-589`), so the AST-901 pending-recovery path did not populate those tabs either. On the reported page the GET therefore already returned criteria with content, and an empty `rubric_vector` cannot be the cause. Remove Stage 1 as the fix and nothing delivers AC1's "prompt text visible/editable": `CollapsiblePanel` renders its body as `hidden={!expanded}`, and `resolvedExpandedTabId` returns `""` until an operator clicks (`ArtifactEditor.tsx:359-363`), while Stage 2's own Done-when promises only that row **labels** are visible. Triage #3 (expand-one) is the hypothesis the evidence best supports, and the plan explicitly puts it out of scope.
**Recommendation:** reproduce before building — run Manual verify #1 plus a `.dep-page` outerHTML capture on the repro candidate. Then plan the change that actually makes prompt bodies visible for a candidate whose criteria already load (default-expanded criteria stack, or expand-all for rubric mode), or take AC1's wording back to Archie/Susan if click-to-expand is the intended affordance.

**discuss — Stage 2's clip theory has no evidence behind it.** `.dep-page` (`App.css:1107-1116`) plus `.dep-body` (`:1273-1277`) is the same flex-column that DetailsEditPage and ProfileTextPage render bodies with successfully, and `height: calc(100% - 40px)` against an auto-height ancestor resolves to auto rather than zero. Setting `overflow: visible` also gives up the intended inner scroll region. Move Manual verify #6 (computed `.dep-body` height) ahead of the change and drop Stage 2 if that height is non-zero.

**discuss — `astral.config.config-source-of-truth` needs-discussion (Stage 3).** Stage 3 adds a seventh literal to `scripts/migrations/backfill_rubric_vectors.py::_ARTIFACT_KEY_TO_TASK_KEY`, which duplicates `RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY`. That script already imports from `src.utils.config` (line 25) and scripts are layer-exempt (`astral.layers.scripts-exempt-from-layer-rules`), so importing the config map and deleting the local copy is a one-line change that removes the drift class this ticket is patching. If `astral.standards.in-scope-only` is judged to win, say so explicitly in the plan.

**discuss — `astral.standards.data-raises-caller-logs` needs-discussion (Stage 1 step 2).** The plan catches `ValueError` from the data layer and states "No new logger noise for the skip path". The statute puts the log on the caller; a silently skipped backfill is undiagnosable in staging. One `logger.warning` per skipped key satisfies both this and AC3.

**discuss — reconcile shape vs save shape.** `apply_rubric_vectors_save` merges `_merge_embedded_evaluate_jd_criteria` before syncing for `evaluate_jd` / `evaluate_meteorite` (`candidate.py:1167-1169`); the plan's reconcile syncs the raw blob. Decide whether imported rows should match the save-path shape, and note it.

**acceptable — helper placement and signatures check out.** `_legacy_rubric_blob_criteria` sitting above a public function matches local convention (`_merge_embedded_evaluate_jd_criteria` at `candidate.py:1103` precedes public `rubric_criteria_for_task`), so `astral.standards.public-then-helpers` is not newly violated. `list_rubric_vectors(..., current_only=True)`, `sync_rubric_vectors_from_criteria`, `save_candidate_data(..., replace=True)`, `copy` and `Optional` are all present as the plan assumes, and Stage 3's premise is correct — the script map genuinely omits `meteorite_jobdesc_rubric` while `RUBRIC_CRITERIA_ARTIFACT_KEYS` includes it.

**acceptable — Notes.** The Files Changed table omits the plan doc itself, so the matching algorithm dropped `astral.docs.features-single-file-per-ticket` and `astral.debug.spikes-under-debug-dir` from the considered set on path predicates. Conformance verified out of band: one file at `docs/features/interface/ast-1200-restore-rubric-criteria-prompts-on-artifacts-pages.md`, correct project directory. Add a docs row on the next revision so the corpus matches mechanically.

Self-assessment honesty: `Single-Component` / `Medium` risk is fair for what is written, but `Conf: high` is not supportable while the primary stage rests on a premise the ticket's own capture contradicts.

— Joan

context_tokens≈62000

#### ada — 2026-08-06T00:27:31.961Z
Plan published on `origin/sub/AST-1198/AST-1200-restore-rubric-criteria-prompts` @ `7fa46539`.

**Plan:** https://github.com/susansomerset/astral/blob/sub/AST-1198/AST-1200-restore-rubric-criteria-prompts/docs/features/interface/ast-1200-restore-rubric-criteria-prompts-on-artifacts-pages.md

**Approach (parent triage):**
1. **Hydrate reconcile** — when `rubric_vector` has no `current=1` rows for an owner but the legacy artifacts blob still has criteria with content, import via `sync_rubric_vectors_from_criteria`, strip the blob key (`replace=True`, AST-802 shape), then overlay from `rubric_criteria_for_task` as today. Emptiness gate is table rows, not merged `rubric_criteria_for_task` (embedded QC/RC must not block backfill).
2. **Scoped CSS** — `dep-page--artifact-editor` so criteria stack cannot clip to header-only; leave expand-one alone.
3. **Backfill script** — add missing `meteorite_jobdesc_rubric` → `evaluate_meteorite`.

**Self-assessment**
- **Scope:** Single-Component — shared Artifacts criteria wire (core hydrate + ArtifactEditor modifier + backfill map).
- **Conf:** high — mirrors `ensure_company_search_terms_table_synced`; triage named the exact call sites.
- **Risk:** Medium — wrong emptiness gate or GET-time strip could skip backfill or mishandle nested artifact deletes.

---

# Restore rubric criteria prompts on Artifacts pages

**Linear:** [AST-1200](https://linear.app/astralcareermatch/issue/AST-1200/restore-rubric-criteria-prompts-on-artifacts-pages-rubric-criteria)
**Parent:** [AST-1198](https://linear.app/astralcareermatch/issue/AST-1198/rubric-criteria-prompts-are-not-appearing-in-ui-artifacts)
**Publish ref:** `sub/AST-1198/AST-1200-restore-rubric-criteria-prompts`

Operators open Artifacts criteria pages (Job List, Company Watch, Job Description, Meteorite, Get, Do, Like) and see header chrome (title + Generate/Regenerate) without criterion **prompt bodies** even when criteria are already loaded. Restore editable prompt visibility on the shared `ArtifactEditor` rubric path without redesigning nav/chrome or touching consult grading.

**Evidence lock (Joan / DOM capture):** the AST-1198 Original brief shows **Regenerate** and the muted autosave `<span>` (not Cancel/Save). That requires `hasData === true` and `inReview === false` in `ArtifactEditor.tsx` — so GET already returned criteria with non-empty `content`, and AST-901 pending-recovery did not populate the tabs. Empty-`rubric_vector` hydrate overwrite cannot be the cause of this report. Prompt bodies are rendered inside `CollapsiblePanel` with `hidden={!expanded}`, and `resolvedExpandedTabId` starts as `""` (expand-one) — so loaded criteria stay collapsed to chevron + label until click. This plan makes **candidate Artifacts criteria** pages expand-all by default so each prompt is visible/editable on open (AC1). Gate is structural (`!jobPersistence && rubricMode`) — not a hardcoded seven-key set — so Recommended Job Modal job-persistence tabs stay expand-one.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `docs/features/interface/ast-1200-restore-rubric-criteria-prompts-on-artifacts-pages.md` | This plan | docs |
| `src/ui/frontend/src/components/ArtifactEditor.tsx` | Candidate criteria expand-all (`!jobPersistence && rubricMode`); one-shot seed after load | ui |
| `scripts/migrations/backfill_rubric_vectors.py` | Delete local `_ARTIFACT_KEY_TO_TASK_KEY`; import `RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY` from config | scripts |

No `src/core/candidate.py` edits. No `App.css` edits. No `config.py` edits. No consult / grade-dot / Manage Tasks / Recommended Job Modal changes. No `tests/` edits (Betty owns the test tree).

## Stage 1: Candidate criteria expand-all so prompt bodies are visible

**Done when:** On candidate Artifacts criteria pages (Job List / Company Watch / Job Description / Meteorite / Get / Do / Like — all use `ArtifactEditor` **without** `jobPersistence`) for a candidate whose GET returns criteria tabs, opening the page shows every criterion's prompt textarea (not `hidden`) under its label — without requiring a chevron click. Fixed-tab / structure modes and **job-persistence** ArtifactEditor uses (Recommended Job Modal Artifacts) keep today's expand-one behavior. Generate/Regenerate, autosave, collapse-one-stays-collapsed while typing, and empty “New Criterion” affordance still work.

1. In `src/ui/frontend/src/components/ArtifactEditor.tsx`, add:

   ```ts
   import { useSectionExpandPolicy } from "../hooks/useSectionExpandPolicy"
   ```

2. After `rubricMode` / `tabsForRail` are defined, add the **structural** expand-all gate (Joan round=2 — do **not** hardcode rubric artifact keys):

   ```ts
   // Candidate Artifacts criteria only — not job-persistence (Recommended Job Modal).
   const criteriaExpandAll = !jobPersistence && rubricMode

   const criteriaSectionKeys = useMemo(
     () => (criteriaExpandAll ? tabsForRail.map(t => t.id) : []),
     [criteriaExpandAll, tabsForRail],
   )
   const {
     isExpanded,
     onExpandedChange,
     expandAllSections,
     setExpandedKeys,
   } = useSectionExpandPolicy({
     expandAll: criteriaExpandAll,
     sectionKeys: criteriaSectionKeys,
   })
   const didSeedCriteriaExpandRef = useRef("")
   ```

   ⚠️ **Decision:** Gate on `!jobPersistence && rubricMode`, not `rubricMode` alone. `rubricMode` is `!fixedFields` and is also true for job-persistence dict tabs with no `shapesKey` (e.g. Recommended Job Modal `proposed_answers`). Parent Boundaries and this plan's Out of scope forbid that surface. Structural check stays config-neutral (no hardcoded seven-key set in React).

3. Wire `CollapsiblePanel` expand state:

   - Keep `expandedTabId` / `resolvedExpandedTabId` for every path where `criteriaExpandAll` is false (fixedFields / structure / **jobPersistence**).
   - On each `CollapsiblePanel` in the stack:

     ```tsx
     expanded={criteriaExpandAll ? isExpanded(tab.id) : resolvedExpandedTabId === tab.id}
     onExpandedChange={next => {
       if (criteriaExpandAll) onExpandedChange(tab.id, next)
       else if (next) setExpandedTabId(tab.id)
       else setExpandedTabId("")
     }}
     ```

4. One-shot expand-all seed after load (mirror `AdminScheduledActions.tsx` `didAutoOpenSectionRef` — Joan round=2). Do **not** list `criteriaSectionKeys` (array) or an unstable `expandAllSections` identity as the sole re-run trigger without a ref guard:

   ```ts
   useEffect(() => {
     if (!criteriaExpandAll || !loaded) return
     if (criteriaSectionKeys.length === 0) return
     const seedKey = `${selectedId ?? ""}:${artifactKey}`
     if (didSeedCriteriaExpandRef.current === seedKey) return
     didSeedCriteriaExpandRef.current = seedKey
     expandAllSections()
   }, [
     criteriaExpandAll,
     loaded,
     selectedId,
     artifactKey,
     criteriaSectionKeys.length,
     expandAllSections,
   ])
   ```

   ⚠️ **Decision:** Seed once per `(selectedId, artifactKey)` load. Re-calling `expandAllSections()` on every `setTabs` (keystroke) would re-open panels the operator collapsed and fail Manual verify #6. Length in the dep array is only so the first non-empty tab set after load can seed; the ref blocks all later runs for that seed key.

5. When `addCriterionTab` runs and `criteriaExpandAll` is true, after `handleChange`, open the new id without re-seeding the whole stack:

   ```ts
   setExpandedKeys(prev => new Set([...prev, t.id]))
   ```

   Keep existing `setExpandedTabId(t.id)` for the expand-one path (`!criteriaExpandAll`).

6. On `selectedId` / `artifactKey` change, reset seed + keys (single effect; ordering is explicit — this runs, then step 4 may seed the new key):

   ```ts
   useEffect(() => {
     didSeedCriteriaExpandRef.current = ""
     setExpandedKeys(new Set())
     setRailOrderFreeze(null)
   }, [selectedId, artifactKey, setExpandedKeys])
   ```

   Replace/extend the existing `setRailOrderFreeze(null)` effect so there is **one** reset effect for these deps (do not leave two competing effects).

7. Do **not** modify `hydrate_rubric_artifacts_for_response`, `apply_rubric_vectors_save`, or any GET handler. Hydrate stays **read-only** overlay from `rubric_criteria_for_task`.

   ⚠️ **Decision (Joan fix-now / `astral.seed.boot-only-not-hot-path`):** No blob→table insert and no `save_candidate_data` from GET/hydrate. Staging blob-but-no-table recovery remains the existing one-shot `scripts/migrations/backfill_rubric_vectors.py` (Stage 2), not an API hot path.

## Stage 2: Backfill script reads owner map from config

**Done when:** `scripts/migrations/backfill_rubric_vectors.py` has no local `_ARTIFACT_KEY_TO_TASK_KEY` dict; it resolves owners via `RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY` from `src.utils.config`, so `meteorite_jobdesc_rubric` and any future config keys cannot drift. Dry-run / purge behavior unchanged.

1. In `scripts/migrations/backfill_rubric_vectors.py`:

   - Change the config import to:

     ```python
     from src.utils.config import (
         ASTRAL_CONFIG,
         RUBRIC_CRITERIA_ARTIFACT_KEYS,
         RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY,
     )
     ```

   - **Delete** the entire `_ARTIFACT_KEY_TO_TASK_KEY = { ... }` block.

   - Where the script currently does `task_key = _ARTIFACT_KEY_TO_TASK_KEY.get(artifact_key)`, use:

     ```python
     task_key = RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY.get(artifact_key)
     ```

   - Keep the existing skip path when `task_key` is missing (same as today when the local map lacked a key).

   ⚠️ **Decision:** Import the config map rather than adding a seventh literal — `astral.config.config-source-of-truth`; scripts are layer-exempt (`astral.layers.scripts-exempt-from-layer-rules`) so the import is allowed. This is in-scope ops alignment for the same rubric keys the UI uses, not a new migration feature.

## Manual verify (builder — before Code Complete)

Use a candidate that shows **Regenerate** on Job List Criteria (criteria already loaded). Stop and comment on the **parent** if prompt bodies still stay `hidden` after Stage 1.

1. **GET (sanity):** `GET /api/candidates/<id>` → `candidate_data.artifacts.joblist_rubric` length ≥ 1 with non-empty `content` (confirms data path; not the fix).
2. **UI AC1:** Artifacts → Job List Criteria — each criterion's prompt textarea is visible without clicking chevrons; labels still show; Regenerate still present.
3. **Sibling pages:** Spot-check Company Watch, Job Description, Meteorite, Get, Do, Like when that candidate has criteria for those keys — same expand-all visibility.
4. **Empty affordance:** Candidate/page with genuinely no criteria still shows the single empty “New Criterion” editor (expanded is fine).
5. **Save / Generate:** Edit a prompt → autosave / reload persists; Generate/Regenerate still runs for an eligible state; Cancel/Save review mode after Generate still works.
6. **Collapse still works:** Collapse one criterion, type in another — the collapsed panel stays closed (one-shot seed; no re-expand on keystroke).
7. **Boundary:** Open Recommended Job Modal → Artifacts → Application Questions (or any `jobPersistence` ArtifactEditor) — still expand-one (bodies `hidden` until expand); not flipped to expand-all.
8. **Out of scope check:** Do **not** ship CSS changes unless this verify finds `.dep-body` computed height `0` while labels/panels are in the DOM — then stop and comment on the parent (do not invent a clip fix in-stage).

## Self-Assessment

**Scope:** `Single-Component` — shared `ArtifactEditor` criteria expand policy + ops backfill map import; seven candidate criteria pages share one component.

**Conf:** `Medium` — evidence from the ticket DOM capture + expand-one path is strong; round=2 gates (`!jobPersistence`, one-shot ref) remove the prior boundary/re-fire risks from the written steps.

**Risk:** `Medium` — missing the `!jobPersistence` gate would leak expand-all into Recommended Job Modal; missing the seed ref would re-open collapsed panels on every keystroke. Both are called out as literal plan gates above.

## Rules check

- `astral.seed.boot-only-not-hot-path` — hydrate/GET stay read-only; no auto-insert from API.
- `astral.config.config-source-of-truth` — backfill script consumes `RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY`.
- `astral.layers.ui-config-driven-business-logic` — no new React business rules for load/source; display expand policy only.
- `astral.patterns.require-auth-on-protected-endpoints` — no new endpoints.
- `astral.ui.frontend-file-placement` — edit existing `ArtifactEditor.tsx` + existing hook; no new page files.
- `astral.standards.in-scope-only` / `astral.standards.dry-and-focused-functions` — reuse `useSectionExpandPolicy`; no parallel expand state machine.
- `astral.git.engineer-test-tree-ban` / `orch.roles.betty-owns-test-tree` — no `tests/` or bible edits.
- `orch.pipeline.plan-is-bible` — builder follows stages literally; ambiguity → parent comment.

## Out of scope (do not implement)

- GET-time / hydrate-time blob→table reconcile or any `save_candidate_data` from `get_candidate_detail` (Joan fix-now; needs Archie/Susan if ever required).
- Speculative `.dep-page` / `.dep-body` CSS clip fix without verified height `0` (Joan discuss).
- Redesign of Artifacts nav, Generate/Regenerate UX, or adding Expand/Collapse bulk chrome.
- Consult grading, encoded rubric decode, job-list grade-dot displays (AST-1059 family).
- Manage Tasks / admin prompt prose; inventing criteria for empty candidates.
- Recommended Job Modal Artifacts tab.
- Engineer-authored tests (Betty).

## Revisions

Revision 1 — 2026-08-06
Driven by: Joan `[plan-discuss] round=1 concern` (plan-rubric.v1 REVISE) — seed-on-GET statute violation; Stage 1 premise contradicted by Regenerate DOM evidence; AC1 unmapped while expand-one left out of scope; Stage 2 CSS unproven; Stage 3 local map duplicates config.
Changes: Dropped hydrate write path and speculative CSS. Primary Stage 1 is rubric-mode expand-all via `useSectionExpandPolicy`. Stage 2 imports `RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY` into the backfill script. Files Changed includes this plan doc. Conf lowered to Medium.

Revision 2 — 2026-08-06
Driven by: Joan `[plan-discuss] round=2 concern` (plan-rubric.v1 REVISE) — `rubricMode` gate leaks into job-persistence Recommended Job Modal; step 4 effect re-opens collapsed panels on every `setTabs`/keystroke.
Changes: Gate is `criteriaExpandAll = !jobPersistence && rubricMode` (structural, no hardcoded key set). Expand-all seed is one-shot per `(selectedId, artifactKey)` via `didSeedCriteriaExpandRef` (AdminScheduledActions precedent). CollapsiblePanel / add-criterion / reset effects use `criteriaExpandAll`. Manual verify #7 boundary check for job-persistence.

## Review

- **Commit:** `b3e810a4`
- **Branch:** `sub/AST-1198/AST-1200-restore-rubric-criteria-prompts`

### Radia — code-rubric.v1 revision=1

**Overall:** FIX-NOW · **Diff:** `origin/dev...HEAD` (`bb43b7ea`), 9 files — matches plan's Files Changed table exactly.

**Full-set sweep:** 64 active leaf statutes scored in-session (18 universal + 46 scoped); zero `violates`. Straggler check (C4) against the plan's own "Considered but excluded" list: `astral.standards.no-cross-contamination`, `astral.standards.no-hardcoded-sets`, `astral.layers.import-direction`, `astral.ui.naming-conventions`, `astral.git.engineer-test-tree-ban` are all in-diff on layer/path predicates (not `not-applicable` as the plan's exclusion note implies) — all five `conforms` on inspection, no functional issue, just an exclusion-bookkeeping mismatch worth tightening next revision.

**fix-now — stale expand-all seed race survives Joan's round=2 discuss item.** `ArtifactEditor.tsx:156-169`: the `[selectedId, artifactKey]` reset effect (156-160) clears `didSeedCriteriaExpandRef` and fires *before* the candidate-load effect (277+) has called `setLoaded(false)` / refetched. In that gap, the one-shot seed effect (163-169) still sees the *previous* page's stale `loaded === true` and stale `criteriaSectionKeys` (old tab ids), claims the new `seedKey`, and seeds `expandedKeys` from the old tab set. When the real fetch resolves, the ref already matches `seedKey`, so it never re-seeds. Because tab ids are index-based (`v_${i}`), this is silent when the new page has the same-or-fewer criteria and visible (extra criteria stay collapsed) when it has more — an AC1/AC2 miss on the second candidate/page an operator visits with a longer criteria list. This is exactly the race Joan's plan-rubric `APPROVED` verdict flagged as `discuss` and asked to "fold in as you wire step 4" (recommended clearing `didSeedCriteriaExpandRef.current = ""` inside the candidate-load effect next to its `setLoaded(false)`); the fix was not present in the Tests Passed diff, and no component test exercises a page/candidate switch with differing criteria counts. Recommend the one-line ref-clear in the load effect before User Testing.

**Pattern conformance:** `pattern.ui.admin-endpoint`, `pattern.config.config-block` — excluded per plan, confirmed no new admin endpoint / config block in diff.

**What's solid:** clean layer discipline (ui stays ui, scripts import from config not a local dict), DRY reuse of `useSectionExpandPolicy` (no parallel expand machine), structural `!jobPersistence && rubricMode` gate avoids a hardcoded seven-key set in React, and Betty's test/bible coverage tracks every stage precisely.

context_tokens≈95000
— Radia

## Resolution

**2026-08-06** — Radia FIX-NOW addressed on `sub/AST-1198/AST-1200-restore-rubric-criteria-prompts`.

- **Stale expand-all seed race:** In the candidate-load effect, clear `didSeedCriteriaExpandRef.current = ""` immediately after `setLoaded(false)` so a stale `loaded === true` render cannot claim `seedKey` for the new candidate/page before fresh tabs arrive (Joan discuss + Radia fix-now).
- **Discuss (C4 exclusion bookkeeping):** no product change; five statutes already `conforms` on inspection — left as Considered but excluded bookkeeping for a future plan polish.

