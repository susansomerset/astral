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
