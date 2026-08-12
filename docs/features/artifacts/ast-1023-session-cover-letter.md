# AST-1023 — Session Cover Letter

<!-- linear-archive: AST-1023 archived 2026-08-05 -->

## Linear archive (AST-1023)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1023/session-cover-letter  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** chuckles  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Susan needs a job-independent Session Cover Letter workbench — the cover-letter twin of [AST-985](https://linear.app/astralcareermatch/issue/AST-985/save-resume-pdf) Session Resume Paste — so she can supply cover-letter field values, see Astral’s styled cover-letter HTML in a new browser tab, and Print → PDF. Job-scoped cover-letter chains and candidate-bound profile injection stay where they are; this epic is a detached Admin convenience tool with browser session retention and no durable artifact write.

## Functional scope

* **Admin cover-letter field workbench:** A dedicated Admin screen where Susan enters the cover-letter field values (sender/from block, date, letter body, sign-off, and any subject/to fields that belong in the golden layout). Nav lives under **Admin**, parallel to Session Resume Paste — not inside Base Resume Content, JAR, or Materials Preview.
* **Session cover-letter payload (fields-only, mostly detached):** Susan enters field values (no paste → LLM parse in this epic). Values become an in-memory cover-letter payload aligned with the existing cover-letter artifact contract (Subject / Letter family and related emit fields), plus session-supplied from/contact and date blocks needed for the golden HTML. No job id required. **Signature:** when a candidate is selected and has a signature image on profile, use that image; otherwise print the typed name as on a professional electronic letter (no session upload). Letter body/from/date fields still come from the Admin form — not from candidate `artifacts.*`.
* **Golden-styled HTML + new tab:** Render a print-oriented HTML document matching the SomersetCover layout in the Original brief (cover-letter DOM + cover CSS, shared accent/font tokens as appropriate) and open it in a new browser tab for Print → PDF. No server-side PDF generation.
* **Session retention (no DB write):** Field values and last successful render payload are retained in the browser the same way Session Resume Paste / Data Management retain working state. Nothing is written to candidate or job artifacts in this epic.
* **Job-independent:** Does not enter BUILD_ARTIFACTS, job `cover_letter` persistence, or Recommended Job Report paths.

### UI inventory (new vs reused)

| Kind | Screen / component | Role in this epic |
| -- | -- | -- |
| **New** | Session Cover Letter page under **Admin** nav | Field inputs, Open HTML, status/errors, session retention |
| **New** | Session-scoped storage for this tool’s fields / last render inputs | Retain working state without DB |
| **Reused** | Cover-letter artifact field contract (Subject / Letter family) and builder cover emit family | Shape of letter content + HTML generation adapted for session/in-memory input |
| **Reused** | Admin auth + new-tab open pattern from Session Resume Paste / materials HTML | Authenticated HTML response; display outside SPA chrome |
| **Reused** | Toast / ordinary form controls | Success/error feedback |
| **Not used** | Job cover-letter daisy-chain / Manage Tasks prompts | Agent drafting stays on the job pipeline |
| **Optional read** | Selected candidate profile signature image only | When present, inject into sign-off; form fields remain source of letter content |
| **Not used** | Session Resume Paste page as the host UI | Sibling Admin tool; do not overload the resume paste screen unless Susan directs a merge |

## Architectural definition

* **Patterns to reuse**
  * `pattern.ui.admin-endpoint` — Admin HTML/API routes stay thin, authenticated, and config-nav driven.
  * `pattern.layers.import-discipline` — core owns HTML emit; UI API delegates; no ui→data.
  * `pattern.config.config-block` — Admin nav entry via `NAV_CONFIG`; cover shape remains config-owned.
* **New patterns proposed**
  * Session-scoped cover-letter workbench (Admin field entry → in-memory cover payload → golden HTML tab, browser retention, no durable write, no candidate/job bind) — mirror of the [AST-985](https://linear.app/astralcareermatch/issue/AST-985/save-resume-pdf) session-resume workbench for cover letters; catalog only after Archie approval.
* **Applicable statutes**
  * `astral.standards.in-scope-only` — do not touch resume Take 2 emit, job chains, or unrelated Admin tools.
  * `astral.standards.no-cross-contamination` — session cover path must not leak into job/candidate persistence.
  * `astral.standards.dry-and-focused-functions` / `astral.standards.public-then-helpers` — extend builder/cover emit cleanly; prefer shared helpers over a second stylesheet island when safe.
  * `astral.standards.debug-contract-gated` / `astral.standards.logging-via-utils` — any new/touched backend `debug=` cover emit/API path uses Style D index headers + `|` detail (AST-538); no React debug contract.
  * `astral.patterns.require-auth-on-protected-endpoints` — Admin session cover routes require admin auth.
  * `astral.layers.ui-config-driven-business-logic` / `astral.layers.import-direction` — nav/config and layer direction.
  * `astral.config.config-source-of-truth` — shapes, nav, style tokens from config — not hardcoded in React.

## Boundaries

* **No database persistence** of field values or HTML onto candidate or job artifacts — browser retention only.
* **No durable candidate bind** — does not write `artifacts.*` or profile. Letter fields come from the Admin form. **Exception (Archie):** optional read of the **selected** candidate’s profile signature image when present; otherwise name-only sign-off. Form render must still succeed with no candidate selected.
* **No job coupling** — does not draft via `draft_cover_letter` / check / finalize chains; does not write `job_data.artifacts.cover_letter`.
* **Does not replace** job cover-letter editing in Job Analysis Report / materials preview.
* **Does not change** Manage Tasks prompts, TASK_CONFIG registry shape, or dispatch chains.
* **No server-side PDF** — HTML tab; user Print → PDF.
* **Does not own resume Take 2 golden work** ([AST-1019](https://linear.app/astralcareermatch/issue/AST-1019/take-2-resume-render-format-discrepancies) / children) — resume stylesheet/chrome stays on that epic; this epic owns cover-letter session UX + cover golden layout from the Original brief.
* **No new top-level** `artifacts/` **directory**.
* **Must not break** Session Resume Paste ([AST-985](https://linear.app/astralcareermatch/issue/AST-985/save-resume-pdf)/**986**/**987**), job cover HTML routes, Base Resume Content, or other Admin nav items.

## Acceptance criteria

1. From the new **Admin** Session Cover Letter screen, Susan can enter cover-letter field values and open a new tab showing styled cover-letter HTML consistent with the Original-brief SomersetCover layout (from block, date, letter body, sign-off; subject/to if included in scope).
2. Render succeeds without a job id; letter fields come from the Admin form. With no candidate selected, HTML still opens (name-only sign-off). With a selected candidate that has a profile signature image, that image appears in the sign-off.
3. Susan can Print → PDF from that tab; no server-generated PDF file is required.
4. Closing and reopening the tool within the same browser session restores the last entered field values (and last successful render inputs if retained); clearing site data wipes them.
5. Completing the flow does not create or update candidate or job cover-letter artifacts or any other durable store for this session.
6. Failed validation/render surfaces a clear error on the Admin screen and does not open a blank/broken HTML tab as success.
7. When `debug=True` on touched backend cover emit/API paths, logs show Style D per-index headers and `|` working detail for what was found/recorded (not counts-only).

## Dependencies and blockers

none. Foundations on `dev`: cover-letter artifact shape (**AST-309** lineage), builder cover emit + HTML routes (**AST-294** / **AST-298** family), Admin session-resume workbench pattern ([AST-985](https://linear.app/astralcareermatch/issue/AST-985/save-resume-pdf)–**987**). Archie: session-only golden cover (no job `build_cover_letter` backfill this epic). [AST-1019](https://linear.app/astralcareermatch/issue/AST-1019/take-2-resume-render-format-discrepancies) resume Take 2 stays separate.

## Open questions

none.

## Proposed child tickets

#### 1!: **Session cover letter HTML builder + admin HTML API - Ada**

Core session cover emit from in-memory field payload (no job load; no artifact persist) producing golden SomersetCover HTML; Admin `POST` HTML route under existing admin auth. Optional signature-image read from the **selected** candidate profile when present — otherwise name-only sign-off. Owns debug contract on touched backend paths. Does **not** own Admin React page or localStorage. After #1 unblocks #2.

**Citations:** `pattern.ui.admin-endpoint`, `pattern.layers.import-discipline`, `astral.standards.debug-contract-gated`, `astral.patterns.require-auth-on-protected-endpoints`, `astral.standards.in-scope-only`

#### 2: **Admin Session Cover Letter page + session retention - Katherine**

New Admin nav page: field inputs for the cover-letter blocks, browser session retention, call #1 HTML API, open rendered HTML in a new tab (Session Resume Paste UX twin). Does **not** own core emit/CSS golden parity.

**Citations:** `pattern.ui.admin-endpoint`, `pattern.config.config-block`, `astral.layers.ui-config-driven-business-logic`, `astral.config.config-source-of-truth`

**New pattern:** Session cover-letter workbench introduced by #1+#2 (parallel to [AST-985](https://linear.app/astralcareermatch/issue/AST-985/save-resume-pdf) session resume); downstream “save to candidate/job” can reuse the same payload/HTML contract later.

**Monolith check:** Functional scope has 5 capabilities; 2 children split backend session emit/API from Admin UI/retention/new-tab (layers + agents differ). Fields-only (Archie) — no parse API child.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-1023 (parent) | ftr/ast-1023-session-cover-letter |
| AST-1024 | sub/AST-1023/AST-1024-session-cover-letter-html-builder-admin-html-api |
| AST-1025 | sub/AST-1023/AST-1025-admin-session-cover-letter-page-session-retention |

**Epic worktree:** `astral-AST-1023/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during do-all-the-things / fix-uat. Thread column is the fully-qualified store.db path (UUID is the directory name — extract for agent --resume). datt resume: read this table — not chat memory.

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | `/home/susan/.cursor/chats/241bb01e7f0660c1b4999e1300653d55/e33aca83-5df3-494d-a7b5-cd5d8efe7a11/store.db` |
| Katherine | engineer | `/home/susan/.cursor/chats/241bb01e7f0660c1b4999e1300653d55/e9328ea4-cf78-4230-b8ca-319688ad8816/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/cd413512-009f-4b73-ab8c-3ac906062c95/store.db` |
| Radia | review | `/home/susan/.cursor/chats/241bb01e7f0660c1b4999e1300653d55/49eec040-c02d-48f1-97d4-60eba293aec3/store.db` |

---

## Original brief

Like we are parsing and creating a resume, create a Session Cover Letter where the candidate can specify the values for the fields, and create a styled cover letter for the candidate as an html blob so the candidate can choose to print it to PDF.

```
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>SomersetCover</title>
  <style>
/* Susan Somerset Resume - Version 07 */
/* Compact styling with decorative headers, tighter spacing, and mixed fonts */

:root {
  --max-width: 800px;
  --accent-color: #3c2c6e;
  --header-color: #3c2c6e;
  --text-primary: #1a1a1a;
  --text-secondary: #444;
  --text-tertiary: #666;
  --border-light: #e0e0e0;
  --border-medium: #ccc;
  
  --header-font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
  --body-font-family: Palatino, "Palatino Linotype", "Book Antiqua", serif;
  --list-font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  padding: 14px 20px 20px;
  background: #f5f5f5;
  font-family: var(--body-font-family);
  color: var(--text-primary);
  line-height: 1.6;
  font-size: 15px;
}

/* Typography Alignment */
h1, h2, h3, .title, .specialties {
  font-family: var(--header-font-family);
  text-align: center;
}

.contact, .competencies-list, .skill-category p {
  font-family: var(--list-font-family);
  text-align: center;
}

.skill-category h4 {
  font-family: var(--header-font-family);
  text-align: center;
}

p, .role-description, ul, li {
  font-family: var(--body-font-family);
  text-align: left;
  line-height: 1.25;
}

p {
  margin-bottom: 12px;
}

.job-title {
  font-family: var(--header-font-family);
  text-align: left;
}

.dates {
  font-family: var(--body-font-family);
  text-align: left;
}

/* All-caps styling */
.competencies-list {
  text-transform: uppercase;
  letter-spacing: 0.2px;
  font-size: 13.5px;
}

.skill-category p {
  text-transform: uppercase;
  letter-spacing: 0.2px;
  font-size: 13.5px;
}

/* Header Section */
.header {
  max-width: var(--max-width);
  margin: 0 auto 2px;
  padding-bottom: 0;
}

h1 {
  margin: 20px 0 0;
  font-size: 33px;
  line-height: 1.1;
  font-weight: 700;
  letter-spacing: -0.5px;
  color: var(--header-color);
}

.title {
  margin: 0;
  font-size: 17px;
  font-weight: 600;
  color: var(--text-secondary);
}

.specialties {
  margin: 0;
  font-size: 14px;
  color: var(--text-tertiary);
  font-weight: 500;
}

.contact {
  margin: 6px 0 0;
  font-size: 14px;
  color: var(--text-secondary);
  display: flex;
  flex-wrap: wrap;
  gap: 8px 16px;
  justify-content: center;
}

.contact span {
  white-space: nowrap;
}

/* Main Content */
.content {
  max-width: var(--max-width);
  margin: 0 auto;
}

section {
  margin-bottom: 0;
}

/* Decorative Headers */
h2 {
  margin: 18px 0 2px;
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  color: var(--accent-color);
  display: flex;
  align-items: center;
}

h2::before,
h2::after {
  content: '';
  flex: 1;
  height: 1px;
  border-top: 1px solid var(--header-color);
}

h2::before {
  margin-right: 12px;
}

h2::after {
  margin-left: 12px;
}

/* Professional Summary */
.summary-intro {
  margin: 6px;
  line-height: 1.25;
  font-family: var(--body-font-family);
  text-align: left;
}

.summary-intro:last-child {
  margin-bottom: 0;
}


.competencies-list {
  margin: 6px 0 0;
  line-height: 1.8;
  color: var(--text-secondary);
}

/* Experience Section */
.role {
  margin-bottom: 12px;
  page-break-inside: avoid;
}

.role-header {
  margin-top: 20px;
  margin-bottom: 8px;
}

.role-description {
  margin: 8px 0;
}

.compact-title {
  margin: 5px 0 2px;
  font-size: 16px;
  font-family: var(--header-font-family);
  text-align: left;
}

.compact-title strong {
  font-weight: 700;
  color: var(--text-primary);
}

.compact-location {
  margin: 0 0 4px;
  font-size: 14.5px;
  color: var(--text-tertiary);
  font-family: var(--body-font-family);
  text-align: left;
  line-height: 1.4;
}

.compact-location em {
  font-style: italic;
  font-size: 14.5px;
}

.role ul {
  margin: 4px 0 0;
  padding-left: 20px;
}

.role li {
  margin-bottom: 6px;
}

.role li:last-child {
  margin-bottom: 0;
}

/* Education */
.education-list {
  margin: 8px 0 0;
  margin-left: 0.5in;
}

.education-list p {
  margin-bottom: 3px;
  line-height: 1.1;
}

.education-list p:last-child {
  margin-bottom: 0;
}

.education-list strong {
  font-family: var(--header-font-family);
  font-weight: 700;
}

/* Technical Skills */
.skills-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
  margin-top: 12px;
}

.skill-category {
  margin: 0;
}

.skill-category h4 {
  margin: 0 0 4px;
  font-size: 13.5px;
  font-weight: 700;
  color: var(--accent-color);
  text-transform: uppercase;
  letter-spacing: 0.2px;
}

.skill-category p {
  margin: 0;
  line-height: 1.5;
  color: var(--text-secondary);
}

/* Mobile */
@media (max-width: 600px) {
  body { padding: 12px; }
  h1 { font-size: 28px; }
  .title { font-size: 15px; }
  h2 { font-size: 18px; }
  .contact { flex-direction: column; gap: 4px; }
  .skills-grid { grid-template-columns: 1fr; gap: 12px; }
}

/* Print */
@media print {
  body { background: #fff; padding: 0; }
  h2 { page-break-after: avoid; }
  #competencies { page-break-after: avoid; } 
  #prior-experience { page-break-before: always; }
  .role { page-break-inside: avoid; }
  p, li { orphans: 3; widows: 3; } 
}
  </style>
  <style>
    body {
      margin: 0;
      padding: 40px 20px;
      background: #f5f5f5;
      font-family: var(--body-font-family);
    }
    
    .cover-letter {
      max-width: 700px;
      margin: 0 auto;
      padding: 14px 35px 35px 35px;
      background: white;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
      color: var(--text-primary);
      line-height: 1.65;
    }
    
    .fromBlock {
      margin: 0 0 32px;
      padding-bottom: 20px;
      border-bottom: 2px solid var(--accent-color);
      font-size: 17px;
      color: var(--accent-color);
      text-align: left;
      line-height: 1.5;
      font-weight: 700;
    }
    
    .toBlock {
      margin: 16px 0 16px;
      font-size: 15px;
      color: var(--text-primary);
      text-align: left;
      line-height: 1.5;
      font-weight: 400;
    }
    
    .letterdate {
      margin: 40px 0 16px;
      font-size: 14px;
      color: var(--text-secondary);
      text-align: left;
    }
    
    .lettersubject {
      margin: 0 0 24px;
      font-size: 15px;
      font-weight: 400;
      color: var(--text-primary);
      text-align: left;
    }
    
    .lettercontent {
      margin: 0 0 24px;
      text-align: left;
    }
    
    .lettercontent p {
      margin: 0 0 16px;
      font-size: 15px;
      line-height: 1.65;
      color: var(--text-primary);
    }
    
    .lettercontent p:last-child {
      margin-bottom: 0;
    }
    
    .letterSignoff {
      margin: 24px 0 0;
      font-size: 15px;
      text-align: left;
      line-height: 1.5;
    }
    
    .signature-img {
      display: block;
      height: 61px;
      margin: 8px 0 -25px 0;
    }
    
    @page {
      margin-top: 1in;
    }
    
    @page :first {
      margin-top: 0.5in;
    }
    
    @page {
      orphans: 3;
      widows: 3;
    }
    
    @media print {
      body {
        background: #fff;
        padding: 0;
      }

      .cover-letter {
        box-shadow: none;
        padding: 0.5in;
      }
      
      /* Set orphans/widows on container and paragraphs */
      .lettercontent {
        orphans: 3;
        widows: 3;
      }
      
      .lettercontent p {
        orphans: 3;
        widows: 3;
        /* Allow breaking but protect against short breaks */
        page-break-inside: auto;
        break-inside: auto;
      }
    }
  </style>
  <meta name="description" content="Cover Letter - Susan Somerset" />
</head>
<body>
  <main>
    <div class="cover-letter">
      <div class="fromBlock">
        Susan Somerset • Oakland, CA<br>
        hire@susansomerset.com • 415-745-5238
      </div>

      <div class="letterdate">July 27, 2026</div>
      <div class="lettercontent">
        <p>Dear Hiring Team,</p>
        <p>I have built numerous workflow automation and journey-orchestration solutions in my 15 years of consulting. Most recently, I used AI-development tools to design and build an agentic AI platform that inverts the job search to be candidate-forward, moving candidates through a complex staged engagement to find employment in a well-matched professional position.</p>
        <p>Each user advances as behavioral and transactional events fire over time, governed by the entry and exit criteria at each stage, the triggers that move someone forward or into a win-back track, and the suppression and frequency rules that keep email, push, and SMS from talking over each other. And no journey is more reliable than the unified profile beneath it that every segment and trigger reads from — the transition points can need more attention than the segments themselves.</p>
        <p>In my experience, when a company brings in a contract TPM mid-program, it's often because something isn't moving and the reason hasn’t made itself clear yet. The right contractor embeds in the program, meaningfully discerns the hidden blockers, builds mutual trust and respect, and drives consensus on specific solutions so delivery can accelerate.</p>
        <p>What I bring in the first month isn't a stack of new stand-up meetings, but a clear read: the real state of the program, the top risks to your milestones, and a dependency map that makes visible what everyone feels but no one has yet drawn. I am up to speed in days, not weeks, connecting with critical stakeholders, ICs and executives alike, to triage what's actually blocking delivery and quickly gain buy-in to get the team moving toward aligned objectives.</p>
        <p>I'm remote-based out of Oakland, CA, and available on your timeline. Please let me know if this sounds like a good fit.</p>
      </div>
      <div class="letterSignoff">
        Best,<br>
        <img src="SomersetSignature.png" class="signature-img" alt="Signature"><br>
        Susan Somerset
      </div>

    </div>
  </main>
</body>
</html>
```

### Comments

#### chuckles — 2026-07-29T02:44:27.704Z
@susan Open questions on AST-1023 (Session Cover Letter):

1. Input mode — fields-only for v1, or also paste → LLM parse like Session Resume Paste?
2. Signature image — omit, session upload/data-URL, or optional pull from selected candidate profile?
3. Job cover HTML backfill — golden SomersetCover CSS/DOM for job `build_cover_letter` / materials tabs in this epic, or session-only?
4. Admin IA — separate Admin nav item (recommended) or tab/mode on Session Resume Paste?

Description has the draft definition; status stays Discussion.

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
