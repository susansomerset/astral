# AST-1551 — Discussion pane on Recommended Job Report

**Linear:** [AST-1551](https://linear.app/astralcareermatch/issue/AST-1551/discussion-pane-on-recommended-job-report-add-discussion-tab-to)  
**Parent:** [AST-1541 — Add "Discussion" tab to Recommended Job modal](https://linear.app/astralcareermatch/issue/AST-1541/add-discussion-tab-to-recommended-job-modal)  
**Publish ref (origin):** `sub/AST-1541/AST-1551-discussion-pane-recommended-job-report`

After AST-1550: render the Discussion top-tab pane in `JobAnalysisReportModal` via a new `JobDiscussionPane` using `ReportSectionList` / `CollapsiblePanel` — RESPONSE-only, readable formatting (same approach as Agent Story), nine collapsed slots from `jobs.recommended.report_discussion_sections` + job `agent_story`. Does **not** change Job Detail / Company Detail Agent Story.

---

## Explicit scope gate

Ticket **## Scope** (only surfaces this plan may touch):

- `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` — Discussion pane wire-up + `agent_story` on job type
- `src/ui/frontend/src/components/JobDiscussionPane.tsx` — **new**
- `src/ui/frontend/src/App.css` — only if report-local chrome is required beyond existing classes

Every **Files Changed** row and every Stage step names only those files / that kind of change. No config, no `api_system`, no `agent.py`, no `AgentStoryTab.tsx` edits, no Job Detail Agent Story behavior, no Artifacts / Summary / Analysis body changes.

**Depends on (already on `origin/ftr/AST-1541-discussion-tab-recommended-job-modal`, User Testing):** AST-1550 — `report_top_tabs` includes Discussion; `report_discussion_sections` length 9; `agent_story[].task_name` optional.

**Sibling consume contract (from AST-1550 — consume only):**

| Manifest / API field | Shape | UI use |
|----------------------|-------|--------|
| `jobs.recommended.report_top_tabs` | includes `{tab_id: "discussion", nav_label: "Discussion"}` after Artifacts | existing `topTabs` / `TabBar` (no hardcode) |
| `jobs.recommended.report_discussion_sections` | `[{section_id, nav_label, default_expanded}, …]` length 9 | Discussion section list |
| `GET /api/jobs/<id>` → `agent_story` | entries with `task_key`, `blocks[]`, optional `task_name` | RESPONSE body per hop |

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/JobDiscussionPane.tsx` | **New** — nine-section RESPONSE-only stack via `ReportSectionList` | ui |
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | Add `agent_story` on `JobDetail`; when `activeTopTab === "discussion"`, render `JobDiscussionPane` with manifest sections + story | ui |

**Out of scope / do not touch:** `AgentStoryTab.tsx` (import its types only); `StateUiContext.tsx` (see Decision — local typed read); `App.css` (Decision — reuse existing classes; if chrome is insufficient, stop and comment — do not silently add CSS); config / api_system / agent.py (AST-1550); `tests/` / bible (Betty).

⚠️ **Decision:** Omit `App.css` from this plan. Bodies use existing `entity-story-content` (read-only textarea) inside `recommended-report-section-list` / `CollapsiblePanel`. If UAT shows a real visual gap that existing classes cannot cover, escalate — do not invent CSS in build.

⚠️ **Decision:** Do **not** edit `StateUiContext.tsx` (not in ticket Scope). In the modal, read `report_discussion_sections` with a local cast/type narrowing on `manifest.jobs.recommended`. Do **not** hardcode the nine hop keys in TSX.

⚠️ **Decision:** Section **order and labels** come from `report_discussion_sections` (AST-1550 hop walk + `task_name`/`task_key` labels). Do **not** re-sort the nine slots by `created_at` — parent’s timestamp note is satisfied by latest-per-task story refs already; reordering slots would fight the config-driven manifest. Match story → section by `task_key === section_id`.

---

## Stage 1: `JobDiscussionPane` — RESPONSE-only nine-section stack

**Done when:** A new `JobDiscussionPane` component renders `ReportSectionList` for the passed section defs (all `default_expanded: false` from the caller/manifest). Expanding a section shows only that hop’s RESPONSE body in a read-only monospace textarea (class `entity-story-content`), pretty-printed when JSON-parseable, otherwise raw text (same `formatContent` rules as `AgentStoryTab`). Hops with no matching story entry or no non-empty RESPONSE show an empty body (still a collapsed panel). No prompt/cache/system blocks appear. No edits to the modal yet.

1. Create `src/ui/frontend/src/components/JobDiscussionPane.tsx`.

2. Imports (exact intent):
   - `ReportSectionList`, `type ReportSectionDef` from `./ReportSectionList`
   - `type AgentStoryEntry`, `type AgentBlock` from `./AgentStoryTab` (types only — do **not** modify `AgentStoryTab.tsx`)

3. Props:

   ```tsx
   type Props = {
     sections: readonly ReportSectionDef[]
     agentStory: readonly AgentStoryEntry[]
   }
   ```

4. Helpers inside the module (public component first, then helpers — or keep helpers above the default export if the file is small; either is fine if focused):

   - `formatDiscussionContent(raw: string): string` — copy `AgentStoryTab`’s `formatContent` logic literally:
     - `try { return JSON.stringify(JSON.parse(raw), null, 2) } catch { return raw }`
   - `responseBodyForTask(story: readonly AgentStoryEntry[], taskKey: string): string`:
     - Find the first entry where `(entry.task_key || "") === taskKey`.
     - From `entry.blocks ?? []`, find the first block where `block.type === "RESPONSE"` **or** `block.type.startsWith("RESPONSE")` (Agent Story may label duplicates as `RESPONSE (2)` — Discussion should still treat those as RESPONSE; prefer the first block whose type equals `"RESPONSE"` or starts with `"RESPONSE"`).
     - Skip when `content === ""` (same empty-RESPONSE filter as Agent Story).
     - Return `formatDiscussionContent(block.content)` when found; else `""`.

5. Default export `JobDiscussionPane({ sections, agentStory })`:
   - Render:

     ```tsx
     <ReportSectionList
       sections={sections}
       renderSection={(sectionId) => {
         const body = responseBodyForTask(agentStory, sectionId)
         if (!body) return null
         return (
           <textarea
             className="entity-story-content"
             readOnly
             value={body}
           />
         )
       }}
     />
     ```

   - Do **not** pass `leading` or `renderMetadata`.
   - Do **not** add Expand-All chrome beyond what `ReportSectionList` already provides.
   - Do **not** hardcode hop keys, hop count, or section labels in this file.

6. Do **not** change `App.css` in this stage.

⚠️ **Decision:** Reuse `AgentStoryTab` formatting exactly (JSON pretty-print try/catch; else raw string). No markdown renderer, no extra `\n` unescape pass — matches parent “existing Agent Story formatting approach.”

⚠️ **Decision:** Empty RESPONSE → `null` body (collapsed empty section still present via `ReportSectionList`). Do not show “No prompt blocks” / Agent Story chrome.

---

## Stage 2: Wire Discussion into `JobAnalysisReportModal`

**Done when:** Opening a Recommended job whose manifest includes Discussion shows top tabs … | Artifacts | **Discussion**. Selecting Discussion renders `JobDiscussionPane` with nine collapsed sections from `report_discussion_sections` and RESPONSE bodies from `job.agent_story` (already returned by `GET /api/jobs/<id>`). Summary / Analysis / Artifacts panes and their actions are unchanged. Job Detail Agent Story is untouched.

1. In `src/ui/frontend/src/components/JobAnalysisReportModal.tsx`:
   - Import `JobDiscussionPane` from `./JobDiscussionPane`.
   - Import `type AgentStoryEntry` from `./AgentStoryTab` (types only).

2. Extend the local `JobDetail` interface with:

   ```tsx
   agent_story?: AgentStoryEntry[]
   ```

   Do **not** invent other new job fields.

3. Build Discussion sections from the manifest (near the existing `summarySections` / `analysisSections` memos):

   ```tsx
   const discussionSections = useMemo((): ReportSectionDef[] => {
     const recommended = manifest?.jobs.recommended as
       | {
           report_discussion_sections?: Array<{
             section_id: string
             nav_label: string
             default_expanded: boolean
           }>
         }
       | undefined
     const rows = recommended?.report_discussion_sections ?? []
     return rows.map(s => ({
       section_id: s.section_id,
       nav_label: s.nav_label,
       default_expanded: s.default_expanded,
     }))
   }, [manifest])
   ```

   - Do **not** override `default_expanded` to `true` for any section (content-aware expand is Summary-only).
   - Do **not** hardcode nine keys. Empty manifest list → empty `ReportSectionList` (acceptable soft-fail from AST-1550).

4. In the tab-pane switch (after the `artifacts` branch, same `recommended-report-tab-pane` container), add:

   ```tsx
   {activeTopTab === "discussion" && (
     <JobDiscussionPane
       sections={discussionSections}
       agentStory={job?.agent_story ?? []}
     />
   )}
   ```

5. Do **not** change `topTabs` construction — Discussion already arrives via `report_top_tabs` from AST-1550. Do **not** add a React-literal fourth tab.

6. Do **not** change Artifacts generate/cancel, Summary/Analysis renderers, header actions, or close behavior.

7. Do **not** edit `App.css` unless Stage 1’s Done-when cannot be met with existing classes (then stop + parent comment — this plan assumes no CSS).

⚠️ **Decision:** Labels displayed in headers are manifest `nav_label` values (already `task_name` or `task_key` from AST-1550). Do not re-derive headers from `agent_story[].task_name` — keeps empty hops labeled correctly when story is missing.

---

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; publish each to `origin/sub/AST-1541/AST-1551-discussion-pane-recommended-job-report`.
- Do not add files, modules, or CSS not listed above.
- Ambiguity / drift → comment on **parent** AST-1541 with the Stage blocked template; stop.

---

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

```
[plan-rubric]
**Rubric:** plan-rubric.v1
**Ticket:** AST-1551
**Overall:** APPROVED
**Publish ref:** `sub/AST-1541/AST-1551-discussion-pane-recommended-job-report` @ `313778b1e6574bc034bf9b6856c324b3b2a43021`

## Traceability
AC1→Stage 2 (manifest `report_top_tabs` + Discussion pane branch); AC2–AC6→Stages 1–2 (`JobDiscussionPane` + `report_discussion_sections` / `agent_story` RESPONSE-only formatting); AC7→explicit out-of-scope (no `AgentStoryTab` / Job Detail / Artifacts edits).

## Findings

### acceptable — `formatDiscussionContent` duplicated from `AgentStoryTab`
**Location:** Stage 1 (`JobDiscussionPane.tsx`)
**Finding:** Plan copies `formatContent` inline rather than extracting a shared helper; parent allowed a tiny extract in `AgentStoryTab` but ticket Scope excludes editing that file.
**Recommendation:** Proceed as planned; duplication is bounded (4 lines) and scope-correct.

### acceptable — parent timestamp-order vs manifest hop-order
**Location:** Files Changed ⚠️ Decision (no `created_at` re-sort)
**Finding:** Parent Functional scope mentions timestamp ordering when runs differ; child AC2 and stable nine-hop slots require manifest hop order from AST-1550.
**Recommendation:** Manifest-driven `section_id` order is the correct reading for this child; no plan change needed.

context_tokens≈68000
```

---

## Review

**Built:** `origin/sub/AST-1541/AST-1551-discussion-pane-recommended-job-report` @ `00c10b63edcb19b578b7fd50af8077fbd729c4ce`

Stages 1–2: `JobDiscussionPane` RESPONSE-only stack; Discussion tab wired in `JobAnalysisReportModal` from `report_discussion_sections` + `agent_story`. Tests deferred to Betty.

## Radia review

```
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1551
**Publish ref:** `sub/AST-1541/AST-1551-discussion-pane-recommended-job-report` @ `9fab6df296e63a2f64c008bf174a3af7e01ddef2`
**Overall:** DISCUSS

**Diff baseline:** `origin/dev...origin/sub/AST-1541/AST-1551-discussion-pane-recommended-job-report` (11 files). **AST-1551 product surface:** `JobDiscussionPane.tsx` (new), `JobAnalysisReportModal.tsx` (wire-up). Diff also carries **AST-1550 backend** (`config.py`, `api_system.py`, `agent.py`) and both issue docs — sibling rollup on sub before `origin/dev` merge (commits `e9b5c46b` sync from AST-1550 sub, `3326b92f resolve(AST-1550)`); not Katherine product scope.

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–2 match plan |
| orch.roles.archie-approves-statutes | universal | conforms | N/A |
| orch.git.betty-merge-tests-one-sha | universal | conforms | Single `merge-tests(AST-1551)` @ `253b780f`; AST-1552 bleed dropped @ `38a0b42d` |
| orch.git.commit-vocabulary | universal | conforms | `code`/`docs`/`test`/`merge-tests`/`sync` |
| orch.git.flow-direction-inviolable | universal | conforms | Sub publish ref |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1541/AST-1551-…` |
| orch.git.merge-on-checkout | universal | conforms | N/A |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No evidence |
| orch.git.no-dev-agent-branches | universal | conforms | Sub only |
| orch.git.one-epic-worktree-per-parent | universal | conforms | AST-1541 epic |
| orch.git.three-permanent-branches | universal | conforms | Sub topology |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | No product-policy drift |
| orch.pipeline.project-scoped-queues | universal | conforms | N/A |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed; empty-RESPONSE gap fixed @ `9fab6df2` |
| orch.roles.betty-owns-test-tree | universal | conforms | Tests/bible/fixture on Betty path |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | N/A |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Katherine assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | No hook violations visible |
| astral.agent.confidence-bounds | scoped | not-applicable | No agent confidence paths |
| astral.agent.do-task-delegation | scoped | not-applicable | No do_task changes in 1551 product |
| astral.agent.grade-vector-validation | scoped | not-applicable | No grade logic |
| astral.batch.batch-id-first | scoped | not-applicable | No batch paths |
| astral.batch.batch-id-format | scoped | not-applicable | No batch paths |
| astral.batch.claim-process-release | scoped | not-applicable | No dispatcher |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | No batch reads |
| astral.config.config-source-of-truth | scoped | conforms | Sections/tabs from manifest; no TSX hardcode |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | No secrets |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | No debug artifacts |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | No spikes |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | Frontend-only product diff |
| astral.dispatch.seed-auto-false | scoped | not-applicable | No seed |
| astral.docs.features-single-file-per-ticket | scoped | conforms | AST-1551 plan doc present |
| astral.git.betty-no-src-or-features | scoped | not-applicable | Engineer frontend only |
| astral.git.engineer-test-tree-ban | scoped | not-applicable | Engineer did not land tests |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | No coat-check |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | No consult |
| astral.idioms.require-auth-on-protected-endpoints | scoped | not-applicable | No new API routes |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | No core/external product edits |
| astral.layers.import-direction | scoped | conforms | Frontend imports components only |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | No scripts |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | `report_top_tabs` / `report_discussion_sections` from manifest; local cast per plan |
| astral.seed.* | scoped | not-applicable | No seed JSON (5 statutes) |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | No data layer |
| astral.standards.database-header-inventory | scoped | not-applicable | No SQL |
| astral.standards.debug-contract-gated | scoped | not-applicable | No debug emission |
| astral.standards.dry-and-focused-functions | scoped | conforms | Small focused pane; Joan-approved `formatContent` duplication |
| astral.standards.in-scope-only | scoped | conforms | Product TSX limited to plan files; no `App.css` / `AgentStoryTab` / `StateUiContext` |
| astral.standards.logging-via-utils | scoped | not-applicable | No logging in frontend diff |
| astral.standards.names-not-ticket-ids | scoped | conforms | `JobDiscussionPane`, `responseBodyForTask` |
| astral.standards.no-cross-contamination | scoped | conforms | No out-of-layer frontend deps |
| astral.standards.no-hardcoded-sets | scoped | conforms | Component TSX manifest-driven; test constants only in tests |
| astral.standards.public-then-helpers | scoped | conforms | Default export first, helpers below |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | No utils product changes (1550 carryover pre-reviewed) |
| astral.state.core-decides-transitions | scoped | not-applicable | No transitions |
| astral.state.job-prior-states-enforced | scoped | not-applicable | No job state enforcement |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | UI render only |
| astral.ui.frontend-file-placement | scoped | conforms | New pane under `components/` |
| astral.ui.naming-conventions | scoped | conforms | PascalCase component, camelCase helpers |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | No server config |

**Active set scored:** 64 statute ids (registry rows excluding namespace paths). **0 violates** on AST-1551 product `src/ui/frontend/**`.

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| none cited | — | Plan/parent cite no `canon/patterns/**` ids; reuses `ReportSectionList` / `CollapsiblePanel` / `entity-story-content` by convention |

## Plan adherence

**Stage 1 — `JobDiscussionPane`:** New component renders `ReportSectionList`; RESPONSE-only via `responseBodyForTask`; JSON pretty-print / raw text (`formatDiscussionContent`); skips empty RESPONSE before selecting body (`9fab6df2`); handles `RESPONSE (2)` via `startsWith("RESPONSE")`; no prompt blocks; no hardcoded hop keys in component.

**Stage 2 — `JobAnalysisReportModal`:** `agent_story?: AgentStoryEntry[]` on `JobDetail`; `discussionSections` memo from manifest local cast (no `StateUiContext` edit); Discussion pane branch after Artifacts; `topTabs` unchanged (manifest-driven); Summary/Analysis/Artifacts untouched; no `App.css`.

**Dependency:** AST-1550 backend on same sub ref supplies `report_top_tabs`, `report_discussion_sections`, `agent_story[].task_name` — present in diff vs `origin/dev` via sibling sync; matches blockedBy AST-1550 @ User Testing.

**Estimate 3:** Fits (two TSX files + wiring).

Joan **APPROVED** @ `313778b1`; acceptable findings (duplicated `formatContent`, manifest hop-order vs timestamp) honored. No straggler excluded statute scored in-scope.

## Findings

### discuss — Manifest fixture hop keys drift from AST-1550 consume contract

**Location:** `tests/component/frontend/fixtures/stateUiManifestFixture.ts` (`report_discussion_sections`); mirrored in `test_JobDiscussionPane.test.tsx` `NINE` constant

**Finding:** Fixture/test constants use nine section_ids including `advise_job_resume`, `finalize_job_resume`, `finalize_cover_letter`. AST-1550’s documented live walk (and `test_api_system.py` `TestAst1550ReportDiscussionSections._NINE` on this branch) is:

`contemplate_job` → `draft_job_resume` → `check_job_resume` → `draft_cover_letter` → `check_cover_letter` → `draft_application_responses` → `check_application_responses` → `polish_application_package` → `propose_application_responses`

Fixture comment says “AST-1550: nine hop slots” but keys differ. Product TSX is manifest-driven and will render production keys correctly; component tests nonetheless assert labels (“Advise Job Resume”, etc.) that staging will not show.

**Recommendation:** Betty align fixture + pane unit `NINE` with AST-1550 `_NINE` before UAT sign-off — not an engineer `resolve-child` item.

### advisory — AST-1550 backend in three-dot diff vs `origin/dev`

**Location:** `src/utils/config.py`, `src/ui/api/api_system.py`, `src/core/agent.py` in diff

**Finding:** Expected sibling rollup on sub (`sync(publish-ref)` / `resolve(AST-1550)`). AST-1551 plan scope excludes these files; Katherine’s product commits are frontend-only (`cebb4f47`, `00c10b63`). No additional 1551-authored backend drift.

### advisory — `formatDiscussionContent` duplication

**Location:** `JobDiscussionPane.tsx` vs `AgentStoryTab.formatContent`

**Finding:** Four-line duplicate per Joan acceptable finding; scope-correct (plan excludes `AgentStoryTab` edits).

## What’s solid

- Discussion pane wiring matches sibling consume contract in production code (manifest sections + `job.agent_story`).
- RESPONSE-only filtering; PROMPT hidden; read-only `entity-story-content` textarea.
- Empty RESPONSE no longer masks later non-empty body (Agent Story parity test green).
- No hardcoded fourth tab; Discussion from `report_top_tabs`.
- `default_expanded` preserved from manifest (all collapsed).
- AST-1552 builder bleed removed from merge-tests; Toast not re-bled on this ref.
- Modal integration tests cover nine collapsed slots, partial story, RESPONSE expand.

## Frame diff

- **New:** `JobDiscussionPane` — nine-slot RESPONSE-only collapsible stack
- **`JobAnalysisReportModal`:** `agent_story` on `JobDetail`; Discussion tab pane when `activeTopTab === "discussion"`
- **Tests/fixture:** Discussion tab + sections in manifest fixture; pane + modal component tests
- **Out of 1551 frame (on diff):** AST-1550 backend + docs (sibling dependency)

## Recommended actions (downstream — not Radia)

1. **Betty:** Update `stateUiManifestFixture.ts` and `test_JobDiscussionPane` `NINE` to match AST-1550 `_NINE` hop keys/labels.
2. **Ada/Katherine / resolve-child:** No product `src/ui/frontend/**` fixes required for AST-1551 scope.
3. **Chuckles:** On merge-child, expect AST-1550 backend already on this sub; dedupe vs ftr if needed.

**Notes:** AST-1550 blockedBy satisfied on branch tip. Product code alone: **CLEAN**.

context_tokens≈58000

---
```

## Resolution

**2026-08-31 — resolve-child (Katherine)**

- **Overall DISCUSS** @ `bd5e0fb3` (Radia docs intake via sync-child).
- **fix-now:** none (Radia: no product `src/ui/frontend/**` fixes required).
- **discuss — fixture hop keys:** test-tree only (`stateUiManifestFixture.ts` + `test_JobDiscussionPane` `NINE`). Routed **`[qa-handoff]`** @Betty White; assignee Betty; status stays **Review Posted**. Resume resolve → User Testing after Betty lands AST-1550 `_NINE` alignment and reassigns Katherine.
- **advisory:** AST-1550 backend rollup + `formatDiscussionContent` duplication — no action.
