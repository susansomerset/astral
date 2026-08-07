# AST-994 — Parse resume json output is incomplete

<!-- linear-archive: AST-994 archived 2026-08-05 -->

## Linear archive (AST-994)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-994/parse-resume-json-output-is-incomplete  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Session Resume Paste and candidate base-resume flows still treat **Experience** as incomplete structured output: Judith returns (or the product coerces) flat prose instead of a clear list of jobs. Susan needs each role parsed into company, title, dates, location, and one faithful accomplishments block — no rewriting or inventing facts — and the shared resume HTML builders must render that job array with consistent role subheaders and metadata. This unblocks readable experience layout on the Admin paste path and the same builder family used for base and job-tailored resume HTML, and must land before [AST-993](https://linear.app/astralcareermatch/issue/AST-993/resume-render-format-discrepancies) can proceed (gap found while testing 993).

## Functional scope

* **Structured experience jobs from Judith (craft-base):** When resume text is parsed through the craft-base (Judith) path, Experience is an ordered array of jobs. Each job carries company name, title, dates (freeform as in the source — e.g. `2023`, `Jan 2023 to Dec 2023`, or similar), location (as present in the source), and one accomplishments text block taken from what the source actually says for that role.
* **No fabrication / no rewrite of facts:** Parse extracts and organizes content that is present; it does not invent employers, titles, dates, locations, or accomplishments, and does not paraphrase or “improve” factual job metadata.
* **Job-tailored experience on the same shape:** Job-tailored resume hops use the same experience job-array contract. Judith may tailor **accomplishments / highlights** to the target job; company, title, dates, and location remain factual and are not rewritten for the posting.
* **Shared HTML recognition of the job array:** Resume HTML builders for candidate base resume and job-tailored resume recognize Experience as that job array and render each job with consistent subheaders and metadata (company, title, dates, location) plus the accomplishments block — not a single undifferentiated experience dump.
* **Session resume builder parity:** The session / Admin Session Resume Paste HTML path uses the same experience job-array render logic so paste → Parse → Open HTML shows the same role structure as base-resume HTML for equivalent content.
* **Contract alignment:** Task response contracts / structure expectations for craft-base and job-tailored Experience match the job-array shape so validation and downstream split/persist paths accept the new form without silently flattening it back to a single string.

## Boundaries

* Ships **job-array + consistent subheaders** with a **single accomplishments text block** per job. Richer golden-fixture role layout (lead paragraph vs achievement bullets, exact `Title • Company` / dates:place phrasing chrome) remains [AST-993](https://linear.app/astralcareermatch/issue/AST-993/resume-render-format-discrepancies) after this epic — AST-994 does not absorb that laundry list.
* Does **not** own golden-fixture typography markers, education lines, skills category grid, prior-experience list style, header/contact/tagline, or full HTML chrome parity — that remains AST-993.
* Does **not** add server-side PDF generation; Print → PDF from the HTML tab stays the path ([AST-985](https://linear.app/astralcareermatch/issue/AST-985/save-resume-pdf)).
* Does **not** persist session paste into the candidate database (AST-985 detached-session boundary stands).
* Does **not** redesign the full resume section catalog or invent new top-level sections beyond Experience’s job-array shape.
* Does **not** change cover-letter HTML or graded consult tasks.
* Must **not** break Session Resume Paste parse → Open HTML ([AST-986](https://linear.app/astralcareermatch/issue/AST-986/session-parse-api-no-persist-no-candidate-bind-save-resume-pdf) / [AST-987](https://linear.app/astralcareermatch/issue/AST-987/admin-session-resume-paste-page-html-new-tab-save-resume-pdf)), Base Resume Content editing, or existing flat-section print for non-experience sections.
* Code Rules: behavior-driving schema/contract literals stay config-driven; backend `debug=` surfaces touched for parse hops follow the AST-538 depth / index / detail contract.

## Acceptance criteria

1. After craft-base parse of a multi-job resume paste, Experience is an ordered list of jobs; each job exposes company, title, dates, location, and one accomplishments text block observable in the parse JSON (session parse response and/or Base Resume Content equivalent).
2. Company, title, dates, and location for each job match source content for that role — no invented employers, titles, dates, or locations.
3. Accomplishments for craft-base match source content for that role (same facts and wording intent) — no added bullet claims that were not in the paste.
4. Opening HTML from Session Resume Paste (or equivalent session HTML) for that parse shows each experience job with consistent role subheaders/metadata (company, title, dates, location) and the accomplishments body — not one merged experience blob.
5. Candidate base-resume HTML built from the same structured experience job array shows the same role subheader/metadata pattern (parity with the session builder path).
6. Job-tailored resume hops accept and emit the same experience job-array shape; tailored output may change accomplishments/highlights for the target job while leaving company, title, dates, and location unchanged from the base facts.
7. Job-tailored resume HTML recognizes the job array and renders the same consistent subheader/metadata pattern as base/session.
8. Dates remain freeform strings as supplied by the source (year-only and range forms both acceptable); the product does not require a rigid start/end date schema for this epic.
9. When `debug=True` on touched parse/tailor hops, debug output shows what was found/recorded for the experience jobs (Style D index + detail), not only a pass/fail summary.

## Dependencies and blockers

* [AST-985](https://linear.app/astralcareermatch/issue/AST-985/save-resume-pdf) / [AST-986](https://linear.app/astralcareermatch/issue/AST-986/session-parse-api-no-persist-no-candidate-bind-save-resume-pdf) / [AST-987](https://linear.app/astralcareermatch/issue/AST-987/admin-session-resume-paste-page-html-new-tab-save-resume-pdf) — Session Resume Paste is the primary UAT surface; assume that path remains available on staging/`dev`.
* This epic **blocks** [AST-993](https://linear.app/astralcareermatch/issue/AST-993/resume-render-format-discrepancies) — 993 cannot proceed until the experience job-array contract and render recognition land.
* none otherwise.

## Open questions

none.

## Proposed child tickets

| # | Working title | What it delivers | Agent | Sequencing |
| -- | -- | -- | -- | -- |
| 1 | Judith craft-base: experience job array | Updates Judith’s craft-base prompt and response contract so Experience is an ordered array of jobs (company, title, dates, location, one accomplishments block) with no fabrication/rewrite of facts. Owns parse JSON shape for session and candidate craft-base paths. Does **not** own HTML emit or job-tailored highlight rewriting. | Ada | — |
| 2 | Job-tailored experience on job-array shape | Job-tailored resume hop(s) use the same experience job-array contract; may tailor accomplishments/highlights for the target job while preserving company, title, dates, location. Does **not** own craft-base parse (#1) or HTML emit (#3). | Ada | after #1 |
| 3 | Base + session + job builders: experience job render | Resume HTML builders (candidate base, session/Admin paste, and job-tailored) recognize the experience job array and render consistent role subheaders/metadata (including location) plus the accomplishments block. Does **not** own Judith prompt/schema (#1/#2) or AST-993 education/skills/header chrome. | Hedy | after #1 |

**New pattern:** Experience as a structured **job array** (company / title / dates / location / accomplishments) — introduced in #1; job-tailored (#2) and all resume HTML builders (#3) reuse the same shape.

**Monolith check:** Functional scope has 6 capabilities; 3 children split craft-base parse, job-tailored highlight policy, and shared HTML recognition (Susan confirmed job-tailored is in scope).

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-994 (parent) | ftr/ast-994-parse-resume-json-output-is-incomplete |
| AST-996 | sub/AST-994/AST-996-judith-craft-base-experience-job-array |
| AST-997 | sub/AST-994/AST-997-job-tailored-experience-on-job-array-shape |
| AST-998 | sub/AST-994/AST-998-base-session-job-builders-experience-job-render |
| AST-1005 | sub/AST-994/AST-1005-uat-parse-validation-false-missing-candidate-name |

**Epic worktree:** `astral-AST-994/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during **do-all-the-things** / **fix-uat**. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | 6c7a6c75-6bfa-47fb-83be-a3519597d732 |
| Hedy | engineer | bc99c93c-9b9d-40b2-87c4-7d763b47c50a |
| Betty | qa | 3de127aa-4322-4682-8fda-5b957d8ccdf9 |
| Radia | review | 5ee8b1db-3c24-4756-b6d5-9777d0f3480e |

---

## Original brief

For the experience section of the resume, I want the AI (Judith) to parse each job with the company name, title, dates (could be just "2023" or "Jan 2023 to Dec 2023" or whatever), and then one block of text for the accomplishments in that role, whatever is detailed on the text provided, to not change or fabricate content.

Then, update the resume renderer to recognize the array of jobs in experience and display their subheaders and metadata consistently.

This issue will cover both the update to Judith's prompt as well as the update to the resume builder logic and the session resume builder to use the new logic.

### Comments

#### chuckles — 2026-07-28T15:39:39.166Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-1005** | parse validation false-missing candidate_name after job-array |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-1005** — _parse validation false-missing candidate_name after job-array_
- **Issue reported:** On Session Resume Paste / craft-base parse UAT, experience jobs return correctly as an array, but the UI validation popup claims the response is missing `candidate_name` — even though the returned JSON includes `agent_payload.resume_structure.candidate_name` (e.g. `"Susan Somerse
- **Should now:** A successful craft-base parse whose `resume_structure` includes `candidate_name` and the experience job array must pass response validation and not show a false “missing candidate_name” failure.
- **Quick check (this fix only):**
  1. Open Session Resume Paste (Admin) on staging/`dev`.
  2. Paste a multi-job resume and run Parse (craft-base).
  3. Observe experience jobs look correct in the payload.
  4. Note validation popup claiming missing `candidate_name` while the JSON body still contains `resume_structure.candidate_name`.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-07-28T15:14:27.204Z
The experience blocks come back well, but the response doesn't pass validation because the popup claimed it's missing the candidate_name:

```
{
  "agent_performance": {
    "status": "success",
    "failure_note": ""
  },
  "agent_payload": {
    "resume_structure": {
      "candidate_name": "Susan Somerset",
      "candidate_title": "Fractional TPM",
      "candidate_contact_detail": "hire@susansomerset.com • 415-745-5238 • linkedin.com/in/susansomerset • California, USA (PST)",
      "professional_summary": "A technical program manager who embeds in programs already in flight, where technical commitments are slipping, stakeholders are losing confidence, or priorities are in flux: I redirect efforts back to delivery. Up to speed in days, not weeks, from the codebase to the roadmap, working autonomously to establish canonical priorities, concrete success criteria, and the risks that actually threaten the date.\n\nAcross over 30 engagements spanning healthtech startups, FDA-regulated medical devices, and enterprise cloud platforms, I discern the real blockers in a room full of competing priorities and get everyone moving the same direction—cutting iteration cycles by as much as 80% through concise scope definition and hands-on technical deliberation. I draw alignment from segmented stakeholders and speak truth to power with diplomacy.\n\nI know when and how to use AI to make real progress, not just create a different problem. I understand the codebase and the commitments, and I have personally built and deployed full-stack, AI-assisted software, so I can facilitate the whole board and triage where to focus next without waiting on someone to translate.",
      "core_competencies": "AI-Assisted Delivery | Cross-Functional Execution | Risk and Dependency Management | Stakeholder Alignment | Program Governance | Delivery Turnaround | Agile/Scrum Delivery | Executive Reporting | Roadmapping | Requirements and Scope Definition | Systems Thinking",
      "experience": [
        {
          "company": "Somerset Consulting",
          "title": "Principal Technical Program Manager",
          "dates": "2011 to Present",
          "location": "United States / Full-time Remote",
          "accomplishments": "Solo practice delivering embedded technical program management across 30+ SaaS engagements over 15 years—brought into troubled or fast-moving programs in healthcare, enterprise cloud, and workflow automation to restore delivery, rebuild stakeholder trust, and ship.\nDiagnosed and mitigated blockers and bottlenecks across distributed teams, implementing lightweight frameworks that reduced iteration cycles from 5 to 10 rounds per feature to only 1 or 2, tuned to team size and culture.\nEmbedded in programs mid-flight to establish canonical priorities, concrete success criteria, and risk mitigation—drawing alignment from segmented stakeholders and driving progress through uncertainty.\nLed technical program delivery across globally distributed teams of as many as 40 people, applying Agile cadence and CI/CD guardrails to achieve sprint-level clarity and measurable delivery rhythm.\nPartnered with founders, executives, and engineering leads to translate complex goals into executable roadmaps and measurable OKRs, embedding Agile/Scrum delivery and metrics-driven accountability.\nArchitected a multi-agent AI recruiting pipeline integrating web scraping, LLM-based analysis, and document generation—reducing manual job-matching time by 90% while maintaining quality through staged human review.\nWorked with lead architects to optimize cloud infrastructure—reducing AWS spend by 70% and saving $23K annually in one instance—while increasing CI/CD deployment velocity."
        },
        {
          "company": "PTown.tech",
          "title": "Technical Program Manager",
          "dates": "2022 to 2024",
          "location": "United States / Full-time Remote",
          "accomplishments": "Repaired a deeply fractured relationship between decision makers and engineering by defining feature-level use cases and prioritizing them through stakeholder interviews, helping non-technical partners understand trade-offs and user impact of their choices.\nDrove an aggressive compliance effort with an uncooperative third-party security auditor, cutting through red tape to achieve full GDPR certification for global deployment in less than four months.\nBuilt an enrollment funnel tracking system for a B2B2C wellness platform serving enterprise clients and employees, increasing completion rates 50% by visualizing stages and working hands-on with engineering to optimize each step.\nDelivered a production-ready MVP that unlocked a global partnership with Manpower's Talent Solutions division, positioning the client for rapid, multinational expansion."
        },
        {
          "company": "EMIDS Technologies",
          "title": "Technical Program Manager",
          "dates": "2021 to 2022",
          "location": "United States / Full-time Remote",
          "accomplishments": "Championed platform adoption by reluctant engineering teams, securing buy-in from key system owners and aligning resources, timelines, and data access to enable full integration of patient services.\nEstablished the first end-to-end onboarding framework for engineering teams integrating into the centralized platform, personally managing 12 onboardings through security, legal, and compliance gates to ensure HIPAA- and FHIR-compliant production deployment.\nNegotiated with solution architects to reconcile legacy design patterns with modern, scalable architectures that fully supported microservice performance and security requirements.\nLed user story mapping sessions and strengthened delivery rhythm across product and platform groups through SAFe Program Increment planning and transparent Agile Release Train coordination."
        },
        {
          "company": "Green Mars Consulting",
          "title": "Founder & Delivery Lead",
          "dates": "2018 to 2020",
          "location": "United States / Full-time Remote",
          "accomplishments": "Built delivery frameworks orchestrating up to 7 concurrent client projects with a 25-employee remote engineering team, driving consistency, accountability, and measurable quality across every delivery.\nDesigned and built an internal operational-intelligence platform unifying five source systems—CRM, finance, project management, QA, and code repositories—into a single MySQL data layer driving automated reporting, proactive monitoring, and Slack alerting; caught 90% of delivery issues before escalation and saved ~10 hours per week in manual reconciliation.\nDesigned API integration strategies for medical-device clients, enabling data exchange between cloud platforms and clinical systems while supporting 2 successful FDA submissions with traceable, testable systems."
        },
        {
          "company": "Tellme Networks / Microsoft",
          "title": "Sr. Operations IT Program Manager",
          "dates": "2006 to 2011",
          "location": "Mountain View, CA / Full-time Onsite",
          "accomplishments": "Drove cross-functional programs integrating business operations, IT systems, and analytics through Tellme's acquisition and transition into Microsoft, preventing deployment delays of up to 6 weeks through proactive stakeholder alignment.\nDesigned and deployed business-intelligence tools with KPI-driven dashboards that improved cost management, resource planning, and operational transparency across multiple departments.\nLed requirements definition, data-model design, and automation efforts that increased reporting accuracy and decision velocity for executive and engineering stakeholders."
        }
      ],
      "prior_experience": "Project Manager (4 yrs) • Systems Analyst (6 yrs) • ETL Migration Specialist (2 yrs) • Database Engineer (2 yrs) • VBA Software Developer (3 yrs)",
      "education_certifications": "Certified ScrumMaster (CSM) • Scrum Alliance, 2024 to 2026\nCertified Scrum Product Owner (CSPO) • Scrum Alliance, 2024 to 2026\nUW Milwaukee • Completed coursework in Computer Science and Business Administration",
      "technical_skills": "Program & Delivery: Jira | Confluence | Linear | Jira Align | Azure DevOps | Asana | Trello | JAMA | Pivotal Tracker\nAI Development & Orchestration: Claude API | GPT-4 | Multi-agent workflows | Prompt engineering | Cursor | Copilot | Structured AI outputs\nDesign & Documentation: Lucidchart | Figma | ERD Tools | Miro | Mural | Confluence (Wiki)\nDevelopment & APIs: Python | Next.js | Google Apps Script | GraphQL | REST | JSON\nData & Analytics: PostgreSQL | MySQL | Prisma | Airtable | Tableau | QlikView | Talend (ETL)\nIntegration & Automation: Zapier | Google Workspace | GitHub Actions | Make | Microsoft 365 | Power Automate\nCloud & DevOps: AWS | Vercel | GitHub | CI/CD Pipelines\nCollaboration: Slack | Discord | Teams | Zoom | Google Meet"
    }
  }
}
```

Did we miss updating the response validation logic?

#### chuckles — 2026-07-28T03:04:18.028Z
[check-linear] In Progress — not finished (AST-998 still Tests Passed; AST-996/997 User Testing)

— Chuckles

#### susan — 2026-07-28T02:48:52.219Z
@chuckles is this ticket finished?

#### chuckles — 2026-07-28T00:13:26.669Z
@susan

1. [AST-993](https://linear.app/astralcareermatch/issue/AST-993/resume-render-format-discrepancies) already scopes Experience role HTML toward `Title • Company`, dates/location phrasing, optional lead paragraph, then achievement bullets. This epic scopes one accomplishments text block per job. Confirm: AST-994 ships the job-array + consistent subheaders with a single accomplishments block first, and AST-993 later refines display — or should AST-994 absorb the richer role layout now and AST-993 drop its experience child?
2. Should the job-array Experience contract also apply to job-tailored resume hops (draft / structure-keyed job resume), or only craft-base + base/session builders for this epic?
3. For fields present in many pastes but not named in your brief (location, remote/onsite arrangement): omit from the job object for this epic, stash inside the dates/accomplishments freeform text as Judith finds them, or add optional fields now?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
