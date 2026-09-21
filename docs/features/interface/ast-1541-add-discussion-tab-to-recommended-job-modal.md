# AST-1541 — Add "Discussion" tab to Recommended Job modal

<!-- linear-archive: AST-1541 archived 2026-09-09 -->

## Linear archive (AST-1541)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1541/add-discussion-tab-to-recommended-job-modal  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Operators reviewing a Recommended job need to read the artifact daisy-chain agent responses that produced Job Resume / Cover / Application Questions without digging through Job Detail’s full Agent Story (prompts + every block). This epic adds a **Discussion** top tab on the Recommended Job Report modal so those nine hop responses are scannable, read-only, and labeled with human `task_name` values — next to the existing Artifacts tab.

## Functional scope

* Add a **Discussion** top tab on the Recommended Job Report modal, immediately to the right of **Artifacts** (Summary / Analysis / Artifacts unchanged).
* Discussion shows **nine** collapsible sections, one per live BUILD_ARTIFACTS daisy-chain hop (entry `contemplate_job` through `propose_application_responses` via `agent_task.run_next`), **not** including `anticipate_scan` and **not** the scored consult hops already covered on Analysis.
* Each section header uses that hop’s `agent_task.task_name` (fallback to `task_key` when blank). Sections default **collapsed**.
* Section bodies show **RESPONSE content only** — no prompt / cache / system blocks. Content is read-only. JSON responses render as pretty-printed JSON; text responses show real newlines (no literal `\n` runs), matching the existing Agent Story formatting approach — no new markdown editor.
* Sections appear in **timestamp order** of the underlying agent runs when timestamps differ; otherwise preserve daisy-chain hop order. Missing hops still reserve a collapsed empty section so the nine slots stay stable.
* Does **not** change Job Detail / Company Detail Agent Story tabs, artifact generation, Analysis/Summary bodies, or prompt editing.

## Component scope

* `src/utils/config.py` — **modified** — register Discussion in `JOBS_RECOMMENDED_REPORT_TOP_TABS` (after Artifacts); expose an ordered Discussion hop-key list (or walk helper) for the UI manifest so the nine slots are not hardcoded in React.
* `src/ui/api/api_system.py` — **modified** — attach Discussion hop keys / display names (from `agent_task.task_name`) on the jobs.recommended (or equivalent) manifest surface the report already consumes.
* `src/core/agent.py` — **modified** — enrich `get_entity_agent_story` entries with `task_name` from the current `agent_task` row (so headers stay DB-driven as names diverge from `task_key`).
* `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` — **modified** — wire Discussion top-tab pane; consume `agent_story` already returned by `GET /api/jobs/<id>`; filter to RESPONSE-only for the nine hops.
* `src/ui/frontend/src/components/JobDiscussionPane.tsx` — **new** — read-only nine-section stack (ReportSectionList / CollapsiblePanel) with pretty JSON / readable text bodies.
* `src/ui/frontend/src/components/AgentStoryTab.tsx` — **unchanged** unless a tiny shared format helper is extracted; Job Detail Agent Story behavior stays as-is.
* `src/ui/frontend/src/App.css` — **modified** only if Discussion needs report-local chrome beyond existing recommended-report / entity-story classes.

## Technical scope

* `config.py`: add `{tab_id: discussion, nav_label: Discussion}` to `JOBS_RECOMMENDED_REPORT_TOP_TABS`; add a single ordered hop-key list (or walk from `BUILD_CONFIG["resume_artifact_chain"]["first_task_key"]` via current `agent_task.run_next`) for the nine BUILD_ARTIFACTS hops ending at `propose_application_responses`.
* `api_system.py`: extend the recommended-report manifest payload with Discussion section defs (`section_id` / `nav_label` from `task_name`, `default_expanded: false`).
* `agent.get_entity_agent_story`: for each story entry, attach `task_name` from the active `agent_task` row for that `task_key` (empty → omit / UI falls back to `task_key`).
* `JobAnalysisReportModal`: include `agent_story` on the job detail type; when `activeTopTab === "discussion"`, render `JobDiscussionPane` with story + manifest section list.
* `JobDiscussionPane`: map nine manifest sections to RESPONSE block content; pretty-print JSON when parseable; otherwise show text with real newlines; all sections start collapsed via `default_expanded: false` / ReportSectionList seed.

## Architectural definition

* **Patterns to reuse** — `no established pattern applies` for a RESPONSE-only Discussion stack; follow the in-tree Recommended Job Report convention (config-driven `JOBS_RECOMMENDED_REPORT_TOP_TABS` + `ReportSectionList` / `CollapsiblePanel` from the AST-858 shell) rather than inventing a new catalog pattern.
* **New patterns proposed** — none.
* **Applicable statutes** —
  * [`astral.layers.ui-config-driven-business-logic`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.ui-config-driven-business-logic.md>) — top-tab list and section labels come from config/manifest, not React literals.
  * [`astral.standards.no-hardcoded-sets`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-hardcoded-sets.md>) — the nine hop keys live in config or are walked from `agent_task.run_next`, not a TSX array.
  * [`astral.config.config-source-of-truth`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/config/astral.config.config-source-of-truth.md>) — Discussion tab registration and hop order owned by config/manifest.
  * [`astral.standards.in-scope-only`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md>) — Recommended Job Report Discussion only; no Job Detail Agent Story redesign.
  * [`astral.standards.dry-and-focused-functions`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.dry-and-focused-functions.md>) — reuse ReportSectionList / existing story formatting; keep a thin Discussion pane.

## Acceptance criteria

1. Opening a Recommended job shows top tabs Summary | Analysis | Artifacts | **Discussion** (Discussion immediately after Artifacts).
2. Discussion shows exactly **nine** collapsible sections for the BUILD_ARTIFACTS daisy-chain hops from `contemplate_job` through `propose_application_responses`; all start collapsed.
3. Each header displays that hop’s `agent_task.task_name` when set; otherwise `task_key`.
4. Expanding a section shows only that hop’s **RESPONSE** body — no prompt/cache/system blocks — and the control is read-only.
5. JSON RESPONSE bodies are pretty-printed; text bodies show real line breaks (no visible `\n` escape runs).
6. Jobs with partial chain progress still show nine slots; hops without a RESPONSE are empty collapsed sections.
7. Job Detail / Company Detail Agent Story tabs and Artifacts generation / editing behavior are unchanged.

## Open questions

none

## Proposed child tickets

#### 1!: **Discussion tab config + story task_name - Ada**

Register Discussion on `JOBS_RECOMMENDED_REPORT_TOP_TABS`, expose the ordered nine-hop section list (keys + `task_name` labels, all `default_expanded: false`) on the UI manifest, and enrich `get_entity_agent_story` with `task_name`. Does not own the React Discussion pane (#2).
**Citations: **`astral.layers.ui-config-driven-business-logic`, `astral.standards.no-hardcoded-sets`, `astral.config.config-source-of-truth`.
**Scope: **`src/utils/config.py` (Discussion top tab + hop-order source); `src/ui/api/api_system.py` (manifest Discussion sections); `src/core/agent.py` (`task_name` on story entries).
**Estimate: 3**

#### 2: **Discussion pane on Recommended Job Report - Katherine**

After #1: render the Discussion top-tab pane in `JobAnalysisReportModal` via a new `JobDiscussionPane` using ReportSectionList / CollapsiblePanel — RESPONSE-only, readable formatting, nine collapsed slots from the manifest + `agent_story`. Does not change Job Detail Agent Story.
**Citations: **`astral.layers.ui-config-driven-business-logic`, `astral.standards.in-scope-only`, `astral.standards.dry-and-focused-functions`.
**Scope: **`src/ui/frontend/src/components/JobAnalysisReportModal.tsx` (Discussion pane wire-up + `agent_story` on job type); `src/ui/frontend/src/components/JobDiscussionPane.tsx` (**new**); `src/ui/frontend/src/App.css` only if report-local chrome is required beyond existing classes.
**Estimate: 3**

---

## Original brief

Create a tab that sections agent data content from the analysis prompts that generated the artifacts, in order by timestamp.  Just raw text is fine, but add the agent_task's task_name to the collapsible section headers. (right now, they're the same as task_key, but we may change that later.)

Each job that has artifacts generated should have the same Artifacts tab, then to the right the "Discussion" tab has 9 sections default all collapsed, for each of the 9 daisy-chained responses.  DO NOT include prompt content, just the responses.

Display JSON responses in a readable format, and text responses in readable (md or rtf or whatever) format, so that the user doesn't see `\n` all over the place.  All content is read-only, of course.

### Comments

#### chuckles — 2026-08-31T21:49:12.474Z
AST-1551 REVIEW — merge-child blocked; recalling @Katherine Johnson to republish sub without git-pull merge commits (sync(dev) pollution).

#### chuckles — 2026-08-31T21:49:02.344Z
AST-1551 REVIEW — merge-child blocked; recalling @Katherine Johnson to republish sub without git-pull merge commits (sync(dev) pollution).

#### chuckles — 2026-08-31T21:42:51.918Z
AST-1551 REVIEW — Radia: Betty align Discussion fixture hop keys with AST-1550 _NINE before UAT; product TSX clean.

#### chuckles — 2026-08-31T21:22:07.136Z
AST-1550 REVIEW — merge-child blocked; recalling Ada for origin/dev pull-merge on sub (need ftr merge).

#### chuckles — 2026-08-31T21:21:32.746Z
AST-1550 REVIEW — merge-child blocked; recalling Ada for origin/dev pull-merge on sub (need ftr merge).

#### chuckles — 2026-08-31T21:16:36.953Z
AST-1550 REVIEW — Radia: sibling Toast tests (AST-1553) on publish ref without Toast.tsx; recalling Betty to restore test_Toast.test.tsx to origin/dev on sub/AST-1541/AST-1550-….

---

_Implementation detail may live in git history on `origin/dev`._
