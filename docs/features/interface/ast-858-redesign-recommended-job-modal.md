# AST-858 — Redesign Recommended Job Modal

<!-- linear-archive: AST-858 archived 2026-08-05 -->

## Linear archive (AST-858)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-858/redesign-recommended-job-modal  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

The shipped Recommended Job Report modal (AST-499) proved the data and actions work, but the left-rail tab layout does not match how candidates should scan a job: summary context first, graded analysis second, editable materials third. This redesign makes the modal the centerpiece experience Susan described — three top-level horizontal tabs with collapsible sections, grade-at-a-glance (including confidence) in Analysis headers, and artifact editing grouped under one Artifacts tab — without changing consult scoring, dispatch, or artifact pipeline behavior.

## Functional scope

* **Three horizontal top tabs.** Replace the current left vertical tab rail with **Summary** (default), **Analysis**, and **Artifacts** across the top of the modal body. Tab selection persists while the modal is open.
* **Collapsible sections within each tab.** Each tab renders a vertical list of named sections with specialized headers. Sections expand and collapse independently.
* **Summary tab sections.**
  * **Job Summary** — Estelle's brief synthesis of the role from `whole_jd_upshot`. Default **expanded**.
  * **Company Upshot** — Company-level narrative from `prefilter_company_notes` on the company record. Default **expanded** unless empty.
  * **Noteworthy Caveats** — From `analysis_upshot` when present. Collapsible; default **expanded** unless empty.
  * **Questions to Ask** — From `analysis_upshot` when present. Collapsible; default **expanded** unless empty.
  * **Raw Job Description** — Full JD text when present. Default **collapsed**.
* **Analysis tab sections.** No separate Overview section — Susan confirmed Analysis is the phase drill-down only.
  * **JD Analysis** — Default **expanded**. Section header shows a **horizontal row of grade icons with confidence dots** for every graded vector (visible collapsed or expanded). Body shows `take_jd` above the hydrated per-vector rubric display.
  * **DO Analysis**, **GET Analysis**, **LIKE Analysis** — Same pattern: header grade row **with confidence dots**; body shows the matching phase upshot (`take_do`, `take_get`, `take_like`) **above** the colorful per-vector rubric content for that phase.
* **Artifacts tab — empty / in-progress state.** When the job has no artifact content yet, the tab shows **Generate Artifacts** (same server action as today). While the job is in **BUILD_ARTIFACTS** or any compound/daisy-chain variant, the generate control uses shared in-flight yellow styling, reads **Generating…**, and **Cancel** appears **immediately beside** it (same cancel behavior as today).
* **Artifacts tab — populated state.** When resume, cover letter, and/or application Q&A content exists in `job_data`, show up to three sections: **Job Resume**, **Cover Letter**, and **Application Questions**. Each section is collapsible; expanding reveals **editable** content. Job Resume uses the candidate's resume structure — stacked sections matching `candidate_resume`, each with one editable text area. Cover letter is one editable text blob. Application questions use the existing editable pattern. Saves persist to `job_data` (originals remain in `agent_data`).
* **Modal header.** Sticky or equivalent while switching tabs. Contains:
  * **Job title** — deeplinked to the job's apply URL (`job_link`) in a new tab (primary apply affordance).
  * **Company name** — deeplinked to company homepage when known.
  * **Copy Application Email** — existing plus-tag copy behavior.
  * **Copy LinkedIn Profile** — existing copy behavior from candidate profile links.
  * **Print Resume** and **Print Cover Letter** — when that artifact content exists, each opens the server-rendered HTML for that artifact in a **new browser tab** so the candidate can print to PDF. No print control for application questions. Replaces the stacked Preview Materials modal pattern.
* **List entry unchanged.** Row click on the Recommended jobs table still opens this modal; list row actions (Skip, etc.) unchanged.
* **State-aware behavior.** Tab visibility, section empty states, and workflow actions continue to follow config/API manifests — not hardcoded state machines in React.

## Boundaries

* Does **not** change the Recommended jobs **list** layout, grouping, or row actions.
* Does **not** change consult scoring, dispatch batching, graders, or artifact pipeline prompts.
* Does **not** add **Reset** or **Regenerate** artifact controls (explicitly future work).
* Does **not** remove or alter server-side artifact generation — UI wiring only re-homes existing actions.
* Does **not** require new Estelle fields or schema changes — uses existing `analysis_upshot`, company `prefilter_company_notes`, and phase grade blobs.
* Does **not** add a stacked Preview Materials modal — Print opens HTML directly in a new tab instead.
* Must **not** break existing candidate actions: Generate Artifacts, Cancel during build, artifact edit/save, and print-ready HTML rendering for resume and cover letter.

## Acceptance criteria

 1. Opening a Recommended job shows **Summary**, **Analysis**, and **Artifacts** as **horizontal** top tabs; **Summary** is selected by default.
 2. Summary tab shows **Job Summary** (`whole_jd_upshot`), **Company Upshot** (`prefilter_company_notes`), **Noteworthy Caveats**, **Questions to Ask**, and **Raw Job Description** (collapsed by default) as independent collapsible sections with clear empty states when data is missing.
 3. Analysis tab shows **JD / DO / GET / LIKE Analysis** only (no Overview section); **JD Analysis** is expanded by default.
 4. Each analysis section header displays a **horizontal grade-icon row with confidence dots for every graded vector**, visible whether the section is collapsed or expanded.
 5. Expanding a phase section shows that phase's Estelle upshot (`take_jd`, `take_do`, `take_get`, or `take_like`) **above** the per-vector rubric grades for that phase.
 6. Artifacts tab with no artifact content shows **Generate Artifacts**; clicking it starts the build using today's server action.
 7. While the job is in **BUILD_ARTIFACTS** (including compound states), the generate control is yellow/in-flight, labeled **Generating…**, with **Cancel** beside it; Cancel returns the job to **RECOMMENDED** as today.
 8. When artifact blobs exist, Artifacts tab shows **Job Resume**, **Cover Letter**, and **Application Questions** with editable content; resume sections mirror candidate resume structure; edits save to `job_data` and survive reload.
 9. Header shows deeplinked **job title** (apply URL) and **company name** (homepage when known), **Copy Application Email**, **Copy LinkedIn Profile**, and **Print Resume** / **Print Cover Letter** buttons (each only when that artifact exists) opening print-ready HTML in a new tab.
10. Jobs without `analysis_upshot` or partial data render graceful empty states — no crash.
11. Existing Recommended-list entry (row click opens modal) and Skip behavior unchanged from current shipped UX.

## Dependencies and blockers

* **AST-499** family (Recommended Job Report modal, Generate/Cancel API, `take_jd`, list entry) — **Done** on `origin/dev`; this ticket refactors presentation atop that foundation.
* **AST-645** (yellow in-flight generate buttons) — **Done**; reuse shared `.in-flight` styling for Generating…
* **AST-605** (server-rendered resume/cover HTML routes) — **Done**; Print buttons reuse those render paths in a new tab instead of the preview modal.
* Proposed Discussion children (not dispatched): **AST-948** shell/tabs/header, **AST-949** Summary tab, **AST-950** Analysis tab, **AST-951** Artifacts tab — pending Susan approval before Todo / `dispatch-parent`.
* None blocking start of definition review.

## Open questions

none.

## Proposed child tickets

| # | Working title | What it delivers | Agent | Sequencing |
| -- | -- | -- | -- | -- |
| 1 | Modal shell, horizontal tabs, sticky header | Horizontal Summary/Analysis/Artifacts tabs, collapsible section chrome, sticky header (deeplinks, copy links, Print Resume/Cover). Does not own tab section bodies. | Katherine | — |
| 2 | Summary tab sections | Job Summary, Company Upshot, Caveats, Questions to Ask, Raw JD collapsible sections. | Katherine | after #1 |
| 3 | Analysis tab grades and confidence | JD/DO/GET/LIKE sections with grade+confidence header rows and phase upshots above rubric. | Katherine | after #1 |
| 4 | Artifacts tab generate, cancel, edit | Generate/Generating…/Cancel and editable Job Resume / Cover Letter / Application Questions. | Katherine | after #1 |

**New patterns:** none — presentation refactor of the shipped Recommended Job Report.

**Monolith check:** Functional scope has multiple capabilities; four children (shell + three tabs). Shell lands first; tab bodies blocked by shell.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-858 (parent) | ftr/AST-858-redesign-recommended-job-modal |
| AST-948 | sub/AST-858/AST-948-modal-shell-horizontal-tabs-sticky-header |
| AST-949 | sub/AST-858/AST-949-summary-tab-sections |
| AST-950 | sub/AST-858/AST-950-analysis-tab-grades-confidence |
| AST-951 | sub/AST-858/AST-951-artifacts-tab-generate-cancel-edit |

**Epic worktree:** `astral-AST-858/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Katherine | engineer | 86fbe782-8fe4-416e-b5c9-df9fc1f8346a |
| Betty | qa | 9cb1a027-5b80-40a6-95c6-1ac5903b8ba5 |
| Radia | review | 18a30f3e-d922-45c8-baa9-4e8cc6ca933a |

---

## Original brief

The Recommended Job Modal is the centerpiece of the candidate user's experience.

It needs three horizontal tabs, "Summary", "Analysis" and "Artifacts"

within each horizontal tab are sectioned lists with specialized headers.
The Summary tab (default)
Will include the sections for "Job Summary" (default expanded but collapsible), "Company Upshot" (I think we have this in the company table from the prefilter task?), "Raw Job Description" (default collapsed).

The Analysis tab 
Includes "Overview" section (default expanded but collapsible), which contains Estelle's upshot analysis for the job, "JD Analysis" , "DO Analysis", "GET Analysis", "LIKE Analysis".  I believe Estelle provides upshots for DO, GET and LIKE as well, and those should appear above the colorful results.

For the Analysis tab's sections, I want a horizontal series of grade icons in the section header (visible when collapsed or expanded), so the candidate sees the full analysis in a single glimpse, and can expand the sections to see the rubric performances for each.

For the Artifacts tab, if artifacts do NOT exist, just display the "Generate Artifacts" button here.  When artifacts exist for the job, then show the three sections as described below.  In future we will add "reset" and "regenerate" buttons at the bottom of the page, but that's not in scope for this ticket.

If the job is in any permutation of "BUILD_ARTIFACTS" state (including daisy chain states, then the Generate button should be yellow and read "Generating…".

The Artifacts section headers will be "Job Resume", "Cover Letter" and "Application Questions", and expanding those sections will display EDITABLE content.  Job Resume will have its own stacked sections of resume content (identical to the candidate's candidate_resume sections), and each section will have a single editable text box that the user can change, and the changes are saved to the job_data blob in the database (We always have the original in agent_data, so no need to worry about undo actions, etc.). The cover letter will be just a single blob of text with the full content ready to be rendered.

The header of the job modal will include:
deeplinked Job Title (where the user will click to open on a new tab to apply for the job)
deeplinked company name (to homepage)
"Copy Application Email" link (existing)
"Copy LinkedIn Profile" link (existing)

### Comments

#### chuckles — 2026-07-22T21:39:26.328Z
[check-linear] Discussion — proposed subissues AST-948, AST-949, AST-950, AST-951 (@susan)

#### susan — 2026-07-22T21:37:59.148Z
@chuckles Please propose subissues for this ticket by creating the issues, setting them to "Discussion" and assigning them to me.

#### chuckles — 2026-07-10T17:33:06.684Z
@susan

1. **Company Upshot source:** Confirm the company field — is **`prefilter_company_notes`** on the company record the intended content and "Company Upshot" label, or a different field?
2. **Overview vs Job Summary:** Are Summary → Job Summary and Analysis → Overview the **same** Estelle text (`whole_jd_upshot`), or should Overview be a distinct synthesis? If distinct, where does it live today?
3. **Noteworthy Caveats / Questions to Ask:** The current summary tab surfaces these from `analysis_upshot`. In the three-tab layout, do they belong in Analysis → Overview, as extra Summary sections, or elsewhere?
4. **Header workflow actions:** Besides the four links named in the brief, should **Apply**, **Cancel artifact build**, and **Preview Materials** stay in the sticky header as today, or move (e.g. Cancel/Apply in Artifacts tab)?
5. **Cancel during BUILD_ARTIFACTS:** Where should Cancel live in the redesigned layout?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
