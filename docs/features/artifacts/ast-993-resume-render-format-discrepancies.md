# AST-993 — Resume Render Format discrepancies

<!-- linear-archive: AST-993 archived 2026-08-05 -->

## Linear archive (AST-993)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-993/resume-render-format-discrepancies  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Session Resume Paste and the shared resume HTML builders still diverge from the legacy ResumeSite golden HTML Susan supplied. **AST-994** landed the experience job-array contract and basic role subheaders; this epic closes the remaining golden-fixture gaps — typography markers, richer role layout (lead paragraph vs bullets, compact title/location phrasing), education lines, skills category grid, prior-experience list style, header/contact composition, ATS meta description from the paste tagline, and embedded stylesheet coverage — so the known paste fixture produces the known HTML structure and typography across all shared builder surfaces.

## Functional scope

* **Golden fixture parity:** Using the input text and desired HTML in this ticket as the reference fixture, rendered resume HTML must match the desired document’s section structure, role/education/skills markup patterns, and typography conventions (observable in the HTML source and print view).
* **Legacy typography markers end-to-end:** Double-underscore becomes non-breaking space; double-tilde becomes non-breaking hyphen; bullet separators get the legacy non-breaking spacing. Markers apply through nested strings (experience bullets/accomplishments, skills lines, contact, competencies, prior experience) — not only top-level flat fields.
* **Header and contact composition:** Name and title render on one heading as `Name • Title` (with markers applied). Contact renders as one centered line with markers. The paste tagline line after the title is **not** shown in the body; it feeds the HTML `<meta name="description">` in the form `Resume of <Candidate>, <title>, specializing in <tagline>` for ATS/PDF metadata.
* **Experience role layout (on AST-994 job array):** Each experience job renders as a role article: compact title `Title • Company`, compact location line in the desired phrasing (`dates: place (arrangement)`), optional lead paragraph when the source marks a non-bullet line, then a bullet list for remaining achievements. Builds on the AST-994 job array (company, title, dates, location, accomplishments) — does not re-litigate that contract.
* **Education & certifications lines:** Each education/certification line renders as its own paragraph with the credential name emphasized and the issuer/dates after a bullet separator — not one undifferentiated prose blob.
* **Technical skills category grid:** Each `Category: items` line becomes a skill category with a category heading and an items line (markers applied) — not a single dumped paragraph.
* **Prior experience list:** Prior experience renders in the competencies-list style with markers applied.
* **Embedded stylesheet coverage:** Update Astral’s embedded resume stylesheet so it carries the styles, fonts, and structural rules needed for the above layout (no external legacy CSS file swap).
* **All shared builder surfaces:** Fixes apply to session paste HTML, candidate base-resume HTML, and job-tailored resume HTML that share the builder family.

## Boundaries

* Does **not** re-implement AST-994’s experience job-array parse/contract or basic job-array recognition — that epic is Done; this epic consumes it.
* Does **not** redesign Manage Tasks prompts or invent a new resume section catalog beyond layout/emit refinements against the golden fixture.
* Does **not** add server-side PDF generation; Print → PDF from the HTML tab remains the path.
* Does **not** persist session paste to the candidate database (AST-985 boundary stands).
* Does **not** switch to an external `styles07.css` link or chase legacy document title chrome as a separate asset pipeline — embedded stylesheet + structure/classes + meta description is the contract.
* Does **not** change cover-letter HTML.
* Must **not** break AST-985 Session Resume Paste parse → Open HTML, AST-994 job-array experience render, Base Resume Content editing, or existing print routes for sections already correct.
* Code Rules: config-driven style values stay in config; no new top-level artifacts dump directory.

## Acceptance criteria

1. Pasting the ticket’s input fixture through Session Resume Paste Parse → Open HTML yields HTML whose body sections match the desired fixture’s structure: header (`Name • Title` + contact), Professional Summary as multiple summary paragraphs, Core Competencies as one competencies list, Experience as role articles with compact title/location, optional lead paragraph, and bullet lists, Prior Experience as competencies list, Education as per-line emphasized credentials, Technical Skills as a category grid.
2. In that rendered HTML, legacy markers from the input are visible as non-breaking spaces and non-breaking hyphens in header/title, contact, competencies, experience text, prior experience, and skills — not left as literal `__` / `~~`.
3. The Somerset Consulting role’s marked non-bullet lead line appears as a paragraph under the role header, not as a list item; subsequent lines are list items.
4. Education lines and skill categories are not a single escaped dump; they show the per-line / per-category markup described above.
5. The document `<head>` includes a meta description of the form `Resume of <Candidate>, <title>, specializing in <tagline>` derived from paste/name/title/tagline fields (tagline not duplicated as a visible body line under the header).
6. Candidate base-resume HTML and job-tailored resume HTML that share the builder produce matching structure/typography for equivalent structured content (parity is not session-only).
7. Embedded stylesheet supports the role/education/skills/header layout without requiring an external legacy CSS file.
8. Susan can verify by eye against the desired HTML in this ticket (structure and typography); no judgment call on “close enough” for the listed discrepancies.

## Dependencies and blockers

* **AST-994** (Parse resume json output is incomplete) — **Done.** Experience job-array contract and basic role subheader recognition are prerequisites; this epic builds the remaining golden-fixture layout on top.
* **AST-985** / **AST-986** / **AST-987** — Session Resume Paste parse + HTML tab remain the primary UAT surface.
* none otherwise.

## Open questions

none.

## Proposed child tickets

| # | Working title | What it delivers | Agent | Sequencing |
| -- | -- | -- | -- | -- |
| 1 | Nested typography markers on render | Markers (`__` / `~~` / bullet spacing) apply through nested strings on all shared resume HTML emits. Owns fixture-driven proof markers are not left literal. Does **not** own role/education/skills layout chrome. | Ada | — |
| 2 | Experience golden layout (lead vs bullets, compact phrasing) | On the AST-994 job array, emit role articles with `Title • Company`, desired dates/location phrasing, optional non-bullet lead paragraph, then achievement bullets. Does **not** own education/skills grid or meta description. | Hedy | after #1 |
| 3 | Education lines + skills category grid + prior list | Education as per-line emphasized credentials; technical skills as category grid; prior experience as competencies list with markers. Does **not** rework experience roles (#2). | Katherine | after #1 |
| 4 | Header/contact + ATS meta description + embedded styles | Header/contact match desired composition; tagline feeds meta description (not body); expand embedded stylesheet for fonts/structure needed by #2/#3. Does **not** own experience/education/skills emit logic. | Katherine | after #1 (parallel #2/#3 once styles needed by those land or stubbed) |

**New pattern:** Golden paste→HTML fixture for resume render parity (input markers + desired HTML structure + ATS meta description from tagline) — introduced across #1–#4; later CSS tweaks reuse the same fixture.

**Monolith check:** Functional scope has 9 capabilities; 4 children split markers, experience golden layout, remaining body sections, and header/meta/styles (laundry list without one mega-ticket). AST-994 already owns parse job-array; not duplicated here.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-993 (parent) | ftr/ast-993-resume-render-format-discrepancies |
| AST-1007 | sub/AST-993/AST-1007-nested-typography-markers-on-render |
| AST-1008 | sub/AST-993/AST-1008-experience-golden-layout |
| AST-1009 | sub/AST-993/AST-1009-education-skills-prior |
| AST-1010 | sub/AST-993/AST-1010-header-contact-meta-styles |

**Epic worktree:** `astral-AST-993/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | e82e63be-414c-4934-a5f8-72f39256eb74 |
| Katherine | engineer | d7b2c0ca-a840-4315-9d06-96ad57141367 |
| Hedy | engineer | 2c15a9ae-86be-456a-9070-805790a09574 |
| Betty | qa | 177ea30f-73fa-4528-a853-d4eba6a2eff6 |
| Radia | review | 86cb03dd-fbe2-4b2a-8fcb-d81277c2d53a |

---

## Original brief

When we first wrote the resume rendering logic, I provided some content from the old javascript application with the original files.

There are numerous inconsistencies between what is rendered for a parsed resume and what the actual output should look like.  In this discussion phase, please compare the input text and the desired output, and propose the laundry list of changes to be made as subissues.

```
input:
Susan Somerset
Fractional__TPM
Program Delivery • Cross-Functional Alignment • Cloud SaaS • AI-Assisted Engineering
hire@susansomerset.com__•__415-745-5238__• linkedin.com/in/susansomerset__•__California,__USA__(PST)
Professional Summary
A technical program manager who embeds in programs already in flight, where technical commitments are slipping, stakeholders are losing confidence, or priorities are in flux: I redirect efforts back to delivery. Up to speed in days, not weeks, from the codebase to the roadmap, working autonomously to establish canonical priorities, concrete success criteria, and the risks that actually threaten the date.
Across over 30 engagements spanning healthtech startups, FDA-regulated medical devices, and enterprise cloud platforms, I discern the real blockers in a room full of competing priorities and get everyone moving the same direction—cutting iteration cycles by as much as 80% through concise scope definition and hands-on technical deliberation. I draw alignment from segmented stakeholders and speak truth to power with diplomacy.
I know when and how to use AI to make real progress, not just create a different problem. I understand the codebase and the commitments, and I have personally built and deployed full-stack, AI-assisted software, so I can facilitate the whole board and triage where to focus next without waiting on someone to translate.
Core Competencies
AI~~Assisted__Delivery • Cross~~Functional__Execution • Risk__and__Dependency__Management • Stakeholder__Alignment • Program__Governance • Delivery__Turnaround • Agile/Scrum__Delivery • Executive__Reporting • Roadmapping • Requirements__and__Scope__Definition • Systems__Thinking
Experience
Somerset__Consulting
Principal Technical Program Manager | 2011 to Present | United States / Full-time Remote
<no bullet>Solo practice delivering embedded technical program management across 30+ SaaS engagements over 15 years—brought into troubled or fast-moving programs in healthcare, enterprise cloud, and workflow automation to restore delivery, rebuild stakeholder trust, and ship.
Diagnosed and mitigated blockers and bottlenecks across distributed teams, implementing lightweight frameworks that reduced iteration cycles from 5 to 10 rounds per feature to only 1 or 2, tuned to team size and culture.
Embedded in programs mid-flight to establish canonical priorities, concrete success criteria, and risk mitigation—drawing alignment from segmented stakeholders and driving progress through uncertainty.
Led technical program delivery across globally distributed teams of as many as 40 people, applying Agile cadence and CI/CD guardrails to achieve sprint~~level clarity and measurable delivery rhythm.
Partnered with founders, executives, and engineering leads to translate complex goals into executable roadmaps and measurable OKRs, embedding Agile/Scrum delivery and metrics~~driven accountability.
Architected a multi-agent AI recruiting pipeline integrating web scraping, LLM-based analysis, and document generation—reducing manual job-matching time by 90% while maintaining quality through staged human review.
Worked with lead architects to optimize cloud infrastructure—reducing AWS spend by 70% and saving $23K annually in one instance—while increasing CI/CD deployment velocity.
PTown.tech
Technical Program Manager | 2022 to 2024 | United States / Full-time Remote
Repaired a deeply fractured relationship between decision makers and engineering by defining feature-level use cases and prioritizing them through stakeholder interviews, helping non-technical partners understand trade-offs and user impact of their choices.
Drove an aggressive compliance effort with an uncooperative third-party security auditor, cutting through red tape to achieve full GDPR certification for global deployment in less than four months.
Built an enrollment funnel tracking system for a B2B2C wellness platform serving enterprise clients and employees, increasing completion rates 50% by visualizing stages and working hands-on with engineering to optimize each step.
Delivered a production-ready MVP that unlocked a global partnership with Manpower's Talent Solutions division, positioning the client for rapid, multinational expansion.
EMIDS Technologies
Technical Program Manager | 2021 to 2022 | United States / Full-time Remote
Championed platform adoption by reluctant engineering teams, securing buy-in from key system owners and aligning resources, timelines, and data access to enable full integration of patient services.
Established the first end-to-end onboarding framework for engineering teams integrating into the centralized platform, personally managing 12 onboardings through security, legal, and compliance gates to ensure HIPAA- and FHIR-compliant production deployment.
Negotiated with solution architects to reconcile legacy design patterns with modern, scalable architectures that fully supported microservice performance and security requirements.
Led user story mapping sessions and strengthened delivery rhythm across product and platform groups through SAFe Program Increment planning and transparent Agile Release Train coordination.
Green Mars Consulting
Founder & Delivery Lead | 2018 to 2020 | United States / Full-time Remote
Built delivery frameworks orchestrating up to 7 concurrent client projects with a 25~~employee remote engineering team, driving consistency, accountability, and measurable quality across every delivery.
Designed and built an internal operational-intelligence platform unifying five source systems—CRM, finance, project management, QA, and code repositories—into a single MySQL data layer driving automated reporting, proactive monitoring, and Slack alerting; caught 90% of delivery issues before escalation and saved ~10 hours per week in manual reconciliation.
Designed API integration strategies for medical-device clients, enabling data exchange between cloud platforms and clinical systems while supporting 2 successful FDA submissions with traceable, testable systems.
Tellme Networks / Microsoft
Sr. Operations IT Program Manager | 2006 to 2011 | Mountain View, CA / Full-time Onsite
Drove cross~~functional programs integrating business operations, IT systems, and analytics through Tellme's acquisition and transition into Microsoft, preventing deployment delays of up to 6 weeks through proactive stakeholder alignment.
Designed and deployed business~~intelligence tools with KPI~~driven dashboards that improved cost management, resource planning, and operational transparency across multiple departments.
Led requirements definition, data~~model design, and automation efforts that increased reporting accuracy and decision velocity for executive and engineering stakeholders.
Prior Experience
Project__Manager__(4__yrs) • Systems__Analyst__(6__yrs) • ETL__Migration__Specialist__(2__yrs) • Database__Engineer__(2__yrs) • VBA__Software__Developer__(3__yrs)
Education & Certifications
Certified ScrumMaster (CSM) • Scrum Alliance, 2024 to 2026
Certified Scrum Product Owner (CSPO) • Scrum Alliance, 2024 to 2026
UW Milwaukee • Completed coursework in Computer Science and Business Administration
Technical Skills
Program & Delivery: Jira__•__Confluence__•__Linear__• Jira__Align__•__Azure__DevOps__•__Asana__• Trello__•__JAMA__•__Pivotal__Tracker
AI Development & Orchestration: Claude__API__•__GPT~~4__• Multi~~agent__workflows__• Prompt__engineering__• Cursor__• Copilot__• Structured__AI__outputs
Design & Documentation: Lucidchart__•__Figma__•__ERD__Tools__• Miro__•__Mural__•__Confluence__(Wiki)
Development & APIs: Python__•__Next.js__•__Google__Apps__Script__• GraphQL__•__REST__•__JSON
Data & Analytics: PostgreSQL__•__MySQL__•__Prisma__•__Airtable__• Tableau__•__QlikView__•__Talend__(ETL)
Integration & Automation: Zapier__•__Google__Workspace__•__GitHub__Actions__• Make__•__Microsoft__365__•__Power__Automate
Cloud & DevOps: AWS • Vercel • GitHub • CI/CD__Pipelines
Collaboration: Slack__•__Discord__•__Teams__• Zoom__•__Google__Meet
```

Desired output:

```
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>SomersetResume</title>
  <link rel="stylesheet" href="styles07.css" />
  <meta name="description" content="Resume of Susan Somerset, Senior Technical Product Manager / Program Manager specializing in Cloud Platforms, Agile Delivery, SaaS, and Healthcare." />
</head>
<body>
  <header class="header">
    <h1>Susan Somerset • Fractional TPM</h1>
    <div class="contact">
      <span>hire@susansomerset.com • 415-745-5238 • linkedin.com/in/susansomerset • California, USA (PST)</span>
    </div>
  </header>

  <main class="content">
    <section aria-labelledby="summary">
      <h2 id="summary">Professional Summary</h2>
      <p class="summary-intro">A technical program manager who embeds in programs already in flight, where technical commitments are slipping, stakeholders are losing confidence, or priorities are in flux: I redirect efforts back to delivery. Up to speed in days, not weeks, from the codebase to the roadmap, working autonomously to establish canonical priorities, concrete success criteria, and the risks that actually threaten the date.</p>
      <p class="summary-intro">Across over 30 engagements spanning healthtech startups, FDA-regulated medical devices, and enterprise cloud platforms, I discern the real blockers in a room full of competing priorities and get everyone moving the same direction—cutting iteration cycles by as much as 80% through concise scope definition and hands-on technical deliberation. I draw alignment from segmented stakeholders and speak truth to power with diplomacy.</p>
      <p class="summary-intro">I know when and how to use AI to make real progress, not just create a different problem. I understand the codebase and the commitments, and I have personally built and deployed full-stack, AI-assisted software, so I can facilitate the whole board and triage where to focus next without waiting on someone to translate.</p>
    </section>

    <section aria-labelledby="competencies">
      <h2 id="competencies">Core Competencies</h2>
      <p class="competencies-list">AI‑Assisted Delivery • Cross‑Functional Execution • Risk and Dependency Management • Stakeholder Alignment • Program Governance • Delivery Turnaround • Agile/Scrum Delivery • Executive Reporting • Roadmapping • Requirements and Scope Definition • Systems Thinking</p>
    </section>

    <section aria-labelledby="experience">
      <h2 id="experience">Experience</h2>
      <article class="role">
        <div class="role-header">
          <p class="compact-title"><strong>Principal Technical Program Manager • Somerset Consulting</strong></p>
          <p class="compact-location"><em>2011 to Present: United States (Full-time Remote)</em></p>
        </div>
        <p class="role-description">Solo practice delivering embedded technical program management across 30+ SaaS engagements over 15 years—brought into troubled or fast-moving programs in healthcare, enterprise cloud, and workflow automation to restore delivery, rebuild stakeholder trust, and ship.</p>
        <ul>
          <li>Diagnosed and mitigated blockers and bottlenecks across distributed teams, implementing lightweight frameworks that reduced iteration cycles from 5 to 10 rounds per feature to only 1 or 2, tuned to team size and culture.</li>
          <li>Embedded in programs mid-flight to establish canonical priorities, concrete success criteria, and risk mitigation—drawing alignment from segmented stakeholders and driving progress through uncertainty.</li>
          <li>Led technical program delivery across globally distributed teams of as many as 40 people, applying Agile cadence and CI/CD guardrails to achieve sprint‑level clarity and measurable delivery rhythm.</li>
          <li>Partnered with founders, executives, and engineering leads to translate complex goals into executable roadmaps and measurable OKRs, embedding Agile/Scrum delivery and metrics‑driven accountability.</li>
          <li>Architected a multi-agent AI recruiting pipeline integrating web scraping, LLM-based analysis, and document generation—reducing manual job-matching time by 90% while maintaining quality through staged human review.</li>
          <li>Worked with lead architects to optimize cloud infrastructure—reducing AWS spend by 70% and saving $23K annually in one instance—while increasing CI/CD deployment velocity.</li>
        </ul>
      </article>

      <article class="role">
        <div class="role-header">
          <p class="compact-title"><strong>Technical Program Manager • PTown.tech</strong></p>
          <p class="compact-location"><em>2022 to 2024: United States (Full-time Remote)</em></p>
        </div>
        <ul>
          <li>Repaired a deeply fractured relationship between decision makers and engineering by defining feature-level use cases and prioritizing them through stakeholder interviews, helping non-technical partners understand trade-offs and user impact of their choices.</li>
          <li>Drove an aggressive compliance effort with an uncooperative third-party security auditor, cutting through red tape to achieve full GDPR certification for global deployment in less than four months.</li>
          <li>Built an enrollment funnel tracking system for a B2B2C wellness platform serving enterprise clients and employees, increasing completion rates 50% by visualizing stages and working hands-on with engineering to optimize each step.</li>
          <li>Delivered a production-ready MVP that unlocked a global partnership with Manpower's Talent Solutions division, positioning the client for rapid, multinational expansion.</li>
        </ul>
      </article>

      <article class="role">
        <div class="role-header">
          <p class="compact-title"><strong>Technical Program Manager • EMIDS Technologies</strong></p>
          <p class="compact-location"><em>2021 to 2022: United States (Full-time Remote)</em></p>
        </div>
        <ul>
          <li>Championed platform adoption by reluctant engineering teams, securing buy-in from key system owners and aligning resources, timelines, and data access to enable full integration of patient services.</li>
          <li>Established the first end-to-end onboarding framework for engineering teams integrating into the centralized platform, personally managing 12 onboardings through security, legal, and compliance gates to ensure HIPAA- and FHIR-compliant production deployment.</li>
          <li>Negotiated with solution architects to reconcile legacy design patterns with modern, scalable architectures that fully supported microservice performance and security requirements.</li>
          <li>Led user story mapping sessions and strengthened delivery rhythm across product and platform groups through SAFe Program Increment planning and transparent Agile Release Train coordination.</li>
        </ul>
      </article>

      <article class="role">
        <div class="role-header">
          <p class="compact-title"><strong>Founder & Delivery Lead • Green Mars Consulting</strong></p>
          <p class="compact-location"><em>2018 to 2020: United States (Full-time Remote)</em></p>
        </div>
        <ul>
          <li>Built delivery frameworks orchestrating up to 7 concurrent client projects with a 25‑employee remote engineering team, driving consistency, accountability, and measurable quality across every delivery.</li>
          <li>Designed and built an internal operational-intelligence platform unifying five source systems—CRM, finance, project management, QA, and code repositories—into a single MySQL data layer driving automated reporting, proactive monitoring, and Slack alerting; caught 90% of delivery issues before escalation and saved ~10 hours per week in manual reconciliation.</li>
          <li>Designed API integration strategies for medical-device clients, enabling data exchange between cloud platforms and clinical systems while supporting 2 successful FDA submissions with traceable, testable systems.</li>
        </ul>
      </article>

      <article class="role">
        <div class="role-header">
          <p class="compact-title"><strong>Sr. Operations IT Program Manager • Tellme Networks / Microsoft</strong></p>
          <p class="compact-location"><em>2006 to 2011: Mountain View, CA (Full-time Onsite)</em></p>
        </div>
        <ul>
          <li>Drove cross‑functional programs integrating business operations, IT systems, and analytics through Tellme's acquisition and transition into Microsoft, preventing deployment delays of up to 6 weeks through proactive stakeholder alignment.</li>
          <li>Designed and deployed business‑intelligence tools with KPI‑driven dashboards that improved cost management, resource planning, and operational transparency across multiple departments.</li>
          <li>Led requirements definition, data‑model design, and automation efforts that increased reporting accuracy and decision velocity for executive and engineering stakeholders.</li>
        </ul>
      </article>

    </section>

    <section aria-labelledby="prior-experience">
      <h2 id="prior-experience">Prior Experience</h2>
      <p class="competencies-list">Project Manager (4 yrs) • Systems Analyst (6 yrs) • ETL Migration Specialist (2 yrs) • Database Engineer (2 yrs) • VBA Software Developer (3 yrs)</p>
    </section>

    <section aria-labelledby="education">
      <h2 id="education">Education &amp; Certifications</h2>
      <div class="education-list">
        <p><strong>Certified ScrumMaster (CSM)</strong> • Scrum Alliance, 2024 to 2026</p>
        <p><strong>Certified Scrum Product Owner (CSPO)</strong> • Scrum Alliance, 2024 to 2026</p>
        <p><strong>UW Milwaukee</strong> • Completed coursework in Computer Science and Business Administration</p>

      </div>
    </section>

    <section aria-labelledby="skills">
      <h2 id="skills">Technical Skills</h2>
      <div class="skills-grid">
        <div class="skill-category">
          <h4>Program & Delivery</h4>
          <p>Jira • Confluence • Linear • Jira Align • Azure DevOps • Asana • Trello • JAMA • Pivotal Tracker</p>
        </div>
        <div class="skill-category">
          <h4>AI Development & Orchestration</h4>
          <p>Claude API • GPT‑4 • Multi‑agent workflows • Prompt engineering • Cursor • Copilot • Structured AI outputs</p>
        </div>
        <div class="skill-category">
          <h4>Design & Documentation</h4>
          <p>Lucidchart • Figma • ERD Tools • Miro • Mural • Confluence (Wiki)</p>
        </div>
        <div class="skill-category">
          <h4>Development & APIs</h4>
          <p>Python • Next.js • Google Apps Script • GraphQL • REST • JSON</p>
        </div>
        <div class="skill-category">
          <h4>Data & Analytics</h4>
          <p>PostgreSQL • MySQL • Prisma • Airtable • Tableau • QlikView • Talend (ETL)</p>
        </div>
        <div class="skill-category">
          <h4>Integration & Automation</h4>
          <p>Zapier • Google Workspace • GitHub Actions • Make • Microsoft 365 • Power Automate</p>
        </div>
        <div class="skill-category">
          <h4>Cloud & DevOps</h4>
          <p>AWS • Vercel • GitHub • CI/CD Pipelines</p>
        </div>
        <div class="skill-category">
          <h4>Collaboration</h4>
          <p>Slack • Discord • Teams • Zoom • Google Meet</p>
        </div>

      </div>
    </section>
  </main>
</body>
</html>
```

### Comments

#### chuckles — 2026-07-28T16:01:58.504Z
[check-linear] Todo — definition updated post-AST-994; OQs cleared

#### susan — 2026-07-28T15:59:01.650Z
@chuckles Let's update the definition of this ticket now that [AST-994](https://linear.app/astralcareermatch/issue/AST-994/parse-resume-json-output-is-incomplete) is complete.

#### chuckles — 2026-07-27T23:55:46.666Z
@susan — open questions on the definition:

1. Tagline line after title is in the paste but missing from desired HTML — omit on render, or add it to the fixture?
2. Apply render fixes to all shared builder surfaces (session + base + job-tailored), or only session + base this epic?
3. Keep Astral embedded stylesheet and match structure/classes only, or also chase legacy doc chrome (external CSS link, `SomersetResume` title, meta description)?
4. Prefer structured objects from parse for experience/skills/education (builder walks them), or builder interprets marker/prose conventions from flat strings?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
