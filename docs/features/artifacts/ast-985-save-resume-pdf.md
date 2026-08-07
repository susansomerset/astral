# AST-985 — Save resume pdf

<!-- linear-archive: AST-985 archived 2026-08-05 -->

## Linear archive (AST-985)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-985/save-resume-pdf  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Susan needs a fast, job-independent way to turn pasted resume text into Astral’s structured resume JSON and see the familiar HTML layout in a new browser tab — without wiring a job, without writing the candidate database yet. This is an Admin convenience tool tightly coupled to the existing resume structure and HTML builder work already shipped in Artifacts, with a simpler paste-first input path. Session retention (same idea as Admin Data Management SQL history) keeps the working paste/parse state across navigation in the browser so UAT and iteration are not lost on every page leave. The HTML tab’s job is user Print → PDF (same as today’s resume HTML routes) — not a server-generated PDF file.

## Functional scope

* **Admin paste workbench:** A dedicated Admin screen with a text area where Susan pastes a full resume text block and triggers parse. Nav lives under **Admin** (alongside Data Management and other admin tools).
* **Parse to resume JSON (detached from candidate selector):** The pasted text is parsed into the same structure-keyed resume JSON shape Astral already uses for resume artifacts (section catalog + section content), reusing the existing craft/parse pipeline and **default** resume-structure contract. It does **not** bind to the currently selected candidate for accent, contact, profile, or stored structure — contact/header and sections come from the paste/parse result. Future job binding is out of scope for this epic.
* **Render HTML and open new tab:** Parsed JSON is rendered through the existing resume HTML builder into an HTML document (in-memory / response is fine) and opened in a new browser tab for review; Susan prints that tab to PDF herself.
* **Session retention (no DB write):** Paste text and the latest successful parse result are retained in the browser the same way Admin Data Management retains SQL command history — available after leaving and returning to the tool. Nothing is written to candidate or job artifact storage in this epic.
* **Job-independent:** Flow does not require or attach a job id; it must not enter BUILD_ARTIFACTS, job `resume_content`, or Recommended Job Report paths.

### UI inventory (new vs reused)

| Kind | Screen / component | Role in this epic |
| -- | -- | -- |
| **New** | Session Resume Paste page under **Admin** nav | Paste textarea, Parse action, status/errors, trigger “open rendered HTML” |
| **New** | Session-scoped storage for this tool’s paste + last parse (mirror Data Management SQL history pattern) | Retain working state without DB |
| **Reused** | Existing `craft_resume_base` / parse-to-structure pipeline (same JSON contract as Base Resume Content generate) | Produce structure + content JSON from pasted text |
| **Reused** | Base resume HTML builder + authenticated HTML resume response pattern (`/candidate/resume/base` family), adapted for session/in-memory JSON without selected-candidate binding | Turn JSON into the known HTML layout |
| **Reused** | New-tab open pattern already used for Print Resume / materials preview | Display rendered HTML outside the SPA chrome |
| **Reused** | Toast (and ordinary form controls) | Success/error feedback |
| **Not used** | Base Resume Content page / ArtifactEditor section tabs | Those edit persisted candidate `base_resume`; this tool is paste → parse → preview only |
| **Not used** | Candidate selector as input to parse/render | Explicitly detached this epic |
| **Not used** | Job Analysis Report, Materials Preview modal, job resume/cover HTML routes | Job-scoped; out of scope |

## Boundaries

* **No database persistence** of paste text, parsed JSON, or HTML onto the candidate or any job — browser session retention only for this epic.
* **No selected-candidate binding** — does not read or write the selected candidate’s profile, accent, or `artifacts.*` for this flow.
* **No job coupling** — does not create, select, or tailor against a job; does not write `job_data.artifacts.resume_content`. Future job binding is deferred.
* **Does not replace Base Resume Content** — persisted structure/content editing and Generate-on-candidate remain on the existing Artifacts page; this tool does not become the new system of record.
* **Does not change Manage Tasks prompts, TASK_CONFIG registry shape, or dispatch chains.**
* **No server-side PDF generation** — HTML in a new tab; user Print → PDF.
* **No cover letter** path in this epic.
* **No new top-level** `artifacts/` **directory** (Code Rules) — plans stay under `docs/features/artifacts/`.
* **Must not break** Base Resume Content, `/candidate/resume/base`, job resume/cover HTML routes, Admin Data Management session history, or other Admin nav items.

## Acceptance criteria

1. From the new **Admin** tool screen, Susan can paste resume text and run Parse; on success she receives structure-keyed resume JSON consistent with the existing base-resume parse contract (not a free-form blob).
2. Parse and HTML render succeed **without** depending on which candidate is selected in the app chrome (detached from the selector).
3. After a successful parse, a control opens a new browser tab showing HTML rendered with the existing resume HTML layout; Susan can Print → PDF from that tab; no job id is required.
4. Closing and reopening the tool screen within the same browser session restores the last pasted text and last successful parse result (Data Management–style retention); a full browser clear of site data wipes them.
5. Completing the flow does not create or update candidate `artifacts.base_resume` / `artifacts.resume_structure`, job artifacts, or any other durable store for this paste.
6. The UI inventory above is reflected in the shipped UX: new Admin paste page + session retention; reused parse pipeline, HTML builder/route family, and new-tab open — not ArtifactEditor, JAR materials preview, or selected-candidate inputs.
7. A failed parse surfaces a clear error on the paste screen and does not open a blank/broken HTML tab as if success occurred.

## Dependencies and blockers

none. Foundations already on `dev`: structure-aligned resume JSON (**AST-477** / **AST-517–519**), base resume HTML builder + `/candidate/resume/base` (**AST-298** family), Base Resume Content / craft path (**AST-519** / **AST-616**), session localStorage pattern on Admin Data Management.

## Open questions

none.

## Proposed child tickets

| # | Working title | What it delivers | Agent | Sequencing |
| -- | -- | -- | -- | -- |
| 1 | Session parse API (no persist, no candidate bind) | Backend: accept pasted resume text, run the existing parse-to-structure pipeline against the **default** structure contract, return structure-keyed JSON **without** reading/writing the selected candidate or any job artifacts; debug-capable on the parse hop per AST-538 when debug is on. Does not own UI or HTML tab. | Ada | — |
| 2 | Admin Session Resume Paste page + HTML new tab | New Admin nav page + session retention for paste + last parse; call #1; open rendered HTML in a new tab via reused builder/HTML route family fed by session/in-memory JSON (no selected-candidate bind, no DB). Does not own parse agent prompts. | Katherine | after #1 |

**New pattern:** Session-scoped resume draft (Admin paste → parse JSON → HTML preview with browser retention, no durable artifact write, no candidate selector bind) — introduced by #1+#2; later job binding or “save to candidate” can reuse the same JSON contract without redoing parse/render.

**Monolith check:** Functional scope has 5 capabilities; 2 children split backend non-persist/detached parse from Admin UI/session/HTML open (layers + agents differ).

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-985 (parent) | ftr/ast-985-save-resume-pdf |
| AST-986 | sub/AST-985/AST-986-session-parse-api-no-persist-no-candidate-bind |
| AST-987 | sub/AST-985/AST-987-admin-session-resume-paste-page-html-new-tab |

**Epic worktree:** `astral-AST-985/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | 2bd7136f-4701-481d-9be1-40c1a9521895 |
| Katherine | engineer | e29e69cc-0587-4355-b284-121fb5998b09 |
| Betty | qa | c14f5faf-edb9-479e-8e78-e8b2bf6ad33a |
| Radia | review | 845e45a7-da55-4ae8-b41d-34014611410c |

---

## Original brief

Very simple:

I want a text input screen where I can paste a resume text block.

The block is parsed into a resume json.

The resume json is then rendered into an html file (potentially just in memory)

A new tab opens to display the rendered html.

this should reuse all the work we have done already in artifacts, simplifying the input process slightly.  These resumes are not related to any job.  This is a candidate tool that is tightly coupled with our resume structure.

call out the new and reused ui screens and ui components.  The resume does not need to be saved to the database at this time, but should be retained in the user session like we do for database commands.

### Comments

#### chuckles — 2026-07-27T21:41:43.886Z
@susan

1. PDF vs HTML — title says PDF; brief is HTML new tab + no DB. Confirm UAT is browser Print → PDF from the HTML tab (same as today’s resume HTML), not a server `.pdf` download?
2. Selected candidate binding — use currently selected candidate for accent/contact/structure defaults (results still session-only), or fully detached from the selector?
3. Nav placement — Candidate or Artifacts?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
