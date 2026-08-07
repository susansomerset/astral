# AST-1019 — Take 2: Resume Render Format discrepancies

<!-- linear-archive: AST-1019 archived 2026-08-05 -->

## Linear archive (AST-1019)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1019/take-2-resume-render-format-discrepancies  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

[AST-993](https://linear.app/astralcareermatch/issue/AST-993/resume-render-format-discrepancies) closed structure for resume HTML (markers, role layout, education/skills/prior, header/meta) but UAT used incomplete desired HTML and guessed styles without the real legacy stylesheet. This epic is the corrected Take 2 fixture: close every remaining **style, format, font, structure, alignment, and cosmetic** gap so Session Resume Paste → Open HTML (and the shared builder family) matches the input paste + desired HTML in this ticket’s Original brief — including the full embedded `<style>` block Susan provided.

## Functional scope

### Formatting requirements (laundry list — authoritative)

These are the remaining changes the render software must make. If it is not listed here, it is out of scope for this epic.

**Document chrome**

1. Document `<title>` is `{candidate_name} Resume` (single space; **no** em/en dashes) — not `SomersetResume` and not `{name} — Resume`.
2. ATS `<meta name="description">` is **candidate-specific** from paste name / title / tagline using the [AST-993](https://linear.app/astralcareermatch/issue/AST-993/resume-render-format-discrepancies) field-derived template `Resume of <name>, <title>, specializing in <tagline>`. The literal meta string in the desired HTML is an **example of structure only** — do not force that fixed Product Manager / Cloud Platforms text when the paste carries different title/tagline.

**Embedded stylesheet (match desired** `<style>` **block)**
3. Font stacks and colors: header/list Helvetica Neue family; body Palatino family; accent/header `#3c2c6e`; primary/secondary/tertiary text colors as in the golden CSS.
4. Decorative section `h2` rules (flex + `::before`/`::after` hairlines), uppercase section titles, sizes/spacing matching the golden block.
5. Contact line: centered **flex** layout (wrap, gap, justify-center; spans `white-space: nowrap`) — not a sparse non-flex leftover.
6. Competencies / skill item lines: uppercase + letter-spacing + list font treatment per golden CSS.
7. Experience role chrome: role vertical rhythm (`margin-bottom`, `page-break-inside`); role-header top/bottom margins; compact-title sizing/margins; compact-location at 14.5px tertiary body font with italic `<em>`; role list `padding-left: 20px` and bullet spacing.
8. Education list: left indent `0.5in`, tight line-height (~1.1), credential `<strong>` on header font.
9. Technical skills: **CSS grid** `auto-fit` / `minmax(280px, 1fr)` with gap; category `h4` centered, uppercase, accent-colored; item lines uppercase.
10. Body paragraph rhythm (`p` margin-bottom) and body/role typography alignment rules from the golden CSS (including unused-but-present `.title` / `.specialties` / `.job-title` / `.dates` rules carried in the stylesheet).
11. **Mobile** `@media (max-width: 600px)` rules from the golden block (body padding, heading sizes, contact column, single-column skills).
12. **Print** rules from the golden block, including `#prior-experience { page-break-before: always }`, competencies/role page-break avoid, orphans/widows.

**Structure already owned by** [AST-993](https://linear.app/astralcareermatch/issue/AST-993/resume-render-format-discrepancies) **(must remain correct under the new styles)**
13. Header `Name • Title` with markers; contact one line with markers; Professional Summary as multiple `.summary-intro` paragraphs; Core Competencies one competencies list; Experience role articles (compact title/location, optional lead paragraph, bullets); Prior Experience competencies-list style; Education per-line emphasized credentials; Technical Skills category grid markup; nested `__` / `~~` markers end-to-end.

**Surfaces**
14. Same cosmetics on session paste HTML, candidate base-resume HTML, and job-tailored resume HTML that share the builder family.
15. Fixture-driven UAT: Original-brief input paste → Open HTML matches desired structure + cosmetics (eye + HTML source). No “close enough.”

## Boundaries

* Does **not** re-litigate [AST-993](https://linear.app/astralcareermatch/issue/AST-993/resume-render-format-discrepancies) / AST-1007–1010 structural contracts except where corrected CSS or residual emit needs a cosmetic tweak.
* Does **not** rewrite resume *content* (paste/parse supplies copy).
* Does **not** redesign Manage Tasks prompts, invent new resume sections, or change cover-letter HTML.
* Does **not** add server-side PDF generation; Print → PDF from the HTML tab remains the path.
* Does **not** persist session paste to the candidate database ([AST-985](https://linear.app/astralcareermatch/issue/AST-985/save-resume-pdf)).
* Does **not** switch to an external `styles07.css` — embedded styles only.
* Must **not** break AST-985/986/987 Session Resume Paste → Open HTML, [AST-994](https://linear.app/astralcareermatch/issue/AST-994/parse-resume-json-output-is-incomplete) job-array experience render, or [AST-993](https://linear.app/astralcareermatch/issue/AST-993/resume-render-format-discrepancies) marker/layout behavior already correct.
* Code Rules: config-driven style tokens stay in config; no new top-level artifacts dump directory.
* Existing children [AST-1020](https://linear.app/astralcareermatch/issue/AST-1020/embedded-stylesheet-golden-parity-take-2-resume-render-format) / [AST-1021](https://linear.app/astralcareermatch/issue/AST-1021/residual-emit-chrome-tweaks-take-2-resume-render-format-discrepancies) already map to the proposed slices below (created on a prior Todo pass; parent returned to Discussion for this redraft). Re-dispatch must not duplicate them.

## Acceptance criteria

1. Pasting the Original-brief input fixture through Session Resume Paste Parse → Open HTML yields an embedded `<style>` that carries the golden rules for items 3–12 above (fonts, colors, decorative `h2`, contact flex, role/education/skills spacing and type, skills grid, mobile, print) — verifiable in HTML source and print/preview.
2. Experience roles, education indent/credentials, and Technical Skills category grid match golden spacing/typography (items 7–9).
3. Contact is the golden centered flex line; header remains `Name • Title` with markers — fixture shows `Susan Somerset • Senior Technical Program Manager` with non-breaking spaces from `__`.
4. No external stylesheet link; styles are embedded.
5. Document `<title>` is `{candidate_name} Resume` (item 1).
6. Meta description is candidate-specific from paste name/title/tagline (item 2) — not the stale Product Manager / Cloud Platforms example string when paste differs.
7. Shared builders (session, base, job-tailored) show the same cosmetics for equivalent structured content.
8. Susan can verify by eye against the desired HTML for every laundry-list item; no judgment call on “close enough.”

## Dependencies and blockers

* [AST-993](https://linear.app/astralcareermatch/issue/AST-993/resume-render-format-discrepancies) — structural stack (AST-1007–1010). Prefer landed on `origin/dev` or work atop its `ftr`.
* [AST-985](https://linear.app/astralcareermatch/issue/AST-985/save-resume-pdf) / [AST-986](https://linear.app/astralcareermatch/issue/AST-986/session-parse-api-no-persist-no-candidate-bind-save-resume-pdf) / [AST-987](https://linear.app/astralcareermatch/issue/AST-987/admin-session-resume-paste-page-html-new-tab-save-resume-pdf) — Session Resume Paste UAT surface.
* none otherwise.

## Open questions

none.

## Proposed child tickets

#### **1\[\*\]: Embedded stylesheet golden parity - Katherine** *(Linear* [AST-1020](https://linear.app/astralcareermatch/issue/AST-1020/embedded-stylesheet-golden-parity-take-2-resume-render-format)*)*

Owns laundry-list items **3–12** (and shared-surface stylesheet application for **14**): bring the embedded resume stylesheet to the ticket’s full `<style>` block — contact flex, role/education/skills spacing and type, skills CSS grid, all-caps treatments, mobile and print, config-driven font/color tokens as needed. Does **not** own document title / meta emit (**2** / Ada).

#### **2: Residual emit / chrome tweaks - Ada** *(Linear* [AST-1021](https://linear.app/astralcareermatch/issue/AST-1021/residual-emit-chrome-tweaks-take-2-resume-render-format-discrepancies)*)*

Owns laundry-list items **1–2** plus any emit/`white-space`/class leftovers CSS cannot fix. Document title `{name} Resume`; candidate-specific field-derived meta (example string in desired HTML is structure-only). Does **not** rework [AST-993](https://linear.app/astralcareermatch/issue/AST-993/resume-render-format-discrepancies) structural contracts or the stylesheet slice. After #1; thin/skip if UAT shows CSS-only is enough.

**New pattern:** Corrected golden HTML+CSS fixture (Take 2) with explicit formatting laundry list — introduced across #1–#2.

**Monolith check:** Laundry list has 15 scoped items; 2 children split stylesheet vs emit/chrome (CSS-first). Existing AST-1020/AST-1021 stay the implementers — update their briefs on next Todo/dispatch pass if needed, do not recreate.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| [AST-1019](https://linear.app/astralcareermatch/issue/AST-1019/take-2-resume-render-format-discrepancies) (parent) | ftr/ast-1019-take-2-resume-render-format-discrepancies |
| [AST-1020](https://linear.app/astralcareermatch/issue/AST-1020/embedded-stylesheet-golden-parity-take-2-resume-render-format) | sub/AST-1019/AST-1020-embedded-stylesheet-golden-parity |
| [AST-1021](https://linear.app/astralcareermatch/issue/AST-1021/residual-emit-chrome-tweaks-take-2-resume-render-format-discrepancies) | sub/AST-1019/AST-1021-residual-emit-chrome-tweaks |
| [AST-1027](https://linear.app/astralcareermatch/issue/AST-1027/uat-markers-not-11-andnbsp-in-html-emit) | sub/AST-1019/AST-1027-uat-markers-nbsp |
| [AST-1028](https://linear.app/astralcareermatch/issue/AST-1028/uat-keywords-emit-in-resume-body-instead-of-meta) | sub/AST-1019/AST-1028-uat-keywords-meta |
| [AST-1029](https://linear.app/astralcareermatch/issue/AST-1029/uat-competencies-separators-print-as-pipes) | sub/AST-1019/AST-1029-uat-competencies-pipes |
| [AST-1030](https://linear.app/astralcareermatch/issue/AST-1030/uat-no-bullet-lead-emitted-as-list-item) | sub/AST-1019/AST-1030-uat-no-bullet-lead |
| [AST-1035](https://linear.app/astralcareermatch/issue/AST-1035/uat-view-parsed-json-button-on-session-resume-paste) | sub/AST-1019/AST-1035-uat-view-parsed-json |
| [AST-1039](https://linear.app/astralcareermatch/issue/AST-1039/uat-summary-newlines-collapse-to-spaces-experience-ok) | sub/AST-1019/AST-1039-uat-summary-newlines |

**Epic worktree:** `astral-AST-1019/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | 5b93b45b-c935-47a9-be06-ea8c4b88f968 |
| Katherine | engineer | 128c66eb-f208-4a76-8333-64ca3c5e364d |
| Betty | qa | 1ba3425a-9ce9-44db-b457-8598f1d27e0d |
| Radia | review | 8df19c6a-f1d2-4113-b3fb-33bbed56bf0d |

---

## Original brief

[AST-993](https://linear.app/astralcareermatch/issue/AST-993/resume-render-format-discrepancies) had the wrong html content and did not include the style details (it was in a separate css file I did not provide.)

In the discussion phase of this ticket, identify all remaining style, format, font, structure, alignment, or other cosmetic changes that must be updated in the render software so that this text:

```
Susan Somerset
Senior__Technical__Program__Manager
Enterprise Implementation • Service Delivery • SaaS Onboarding & Adoption • Cross-Functional Coordination
hire@susansomerset.com__•__415-745-5238__• linkedin.com/in/susansomerset__•__California,__USA__(PST)
Professional Summary
A technical program manager who runs enterprise software implementations from kickoff through go-live and adoption—keeping multiple customer-facing engagements on schedule while coordinating across Product, Customer Success, and Solutions Architecture. Up to speed in days, not weeks, from the codebase to the roadmap, establishing canonical priorities, concrete success criteria, and the risks that actually threaten the date.
Across 30+ engagements spanning healthtech startups, FDA-regulated medical devices, and enterprise cloud platforms, I have owned full delivery lifecycles: scope and schedule, dependency and risk tracking, executive reporting, and the client relationship that determines whether a rollout actually gets adopted. I cut iteration cycles by as much as 80% through concise scope definition and hands-on technical deliberation, and I draw alignment from segmented stakeholders while speaking truth to power with diplomacy.
I know when and how to use AI to make real progress, not just create a different problem. I have personally built and deployed full-stack, AI-assisted software—so I coordinate technical teams and executives without waiting on someone to translate.
Core Competencies
Enterprise__Implementation__Management • Service__Delivery • Customer__Onboarding__and__Adoption • Go~~Live__Readiness • Risk__and__Dependency__Management • Stakeholder__Alignment • Program__Governance • Agile/Scrum__Delivery • Executive__Reporting • Requirements__and__Scope__Definition • Systems__Thinking
Experience
Somerset__Consulting
Principal Technical Program Manager | 2011 to Present | United States / Full-time Remote
<no bullet>Solo practice delivering embedded technical program and implementation management across 30+ SaaS engagements over 15 years—running customer-facing enterprise deployments from kickoff through go-live and adoption in healthcare, enterprise cloud, and workflow automation.
Directed full implementation lifecycles for enterprise software deployments—scope, schedule, milestones, dependency and risk tracking—driving each engagement to on-time go-live and user adoption.
Acted as the central point of coordination between customers and internal teams—Product, Customer Success, and Solutions Architecture—aligning expectations on scope, schedules, milestones, and outcomes.
Diagnosed and mitigated blockers and bottlenecks across distributed teams, implementing lightweight frameworks that reduced iteration cycles from 5 to 10 rounds per feature to only 1 or 2, tuned to team size and culture.
Led technical program delivery across globally distributed teams of as many as 40 people, applying Agile cadence and CI/CD guardrails to achieve sprint~~level clarity and measurable delivery rhythm.
Architected a multi-agent AI recruiting pipeline integrating web scraping, LLM-based analysis, and document generation—reducing manual job-matching time by 90% while maintaining quality through staged human review.
Worked with lead architects to optimize cloud infrastructure—reducing AWS spend by 70% and saving $23K annually in one instance—while increasing CI/CD deployment velocity.
PTown.tech
Technical Program Manager | 2022 to 2024 | United States / Full-time Remote
Repaired a deeply fractured relationship between decision makers and engineering by defining feature-level use cases and prioritizing them through stakeholder interviews, helping non-technical partners understand trade-offs and user impact of their choices.
Drove an aggressive compliance effort with an uncooperative third-party security auditor, cutting through red tape to achieve full GDPR certification for global deployment in less than four months.
Built and rolled out an enrollment funnel tracking system for a B2B2C wellness platform serving enterprise clients and their employees, increasing completion rates 50% by visualizing stages and working hands-on with engineering to optimize each step.
Delivered a production-ready MVP that unlocked a global partnership with Manpower's Talent Solutions division, positioning the client for rapid, multinational expansion.
EMIDS Technologies
Technical Program Manager | 2021 to 2022 | United States / Full-time Remote
Managed enterprise implementation and onboarding for a large healthcare platform, personally driving 12 customer onboardings through security, legal, and compliance gates to HIPAA- and FHIR-compliant go-live.
Championed platform adoption by reluctant engineering teams, securing buy-in from key system owners and aligning resources, timelines, and data access to enable full integration of patient services.
Negotiated with solution architects to reconcile legacy design patterns with modern, scalable architectures that fully supported microservice performance and security requirements.
Led user story mapping sessions and strengthened delivery rhythm across product and platform groups through SAFe Program Increment planning and transparent Agile Release Train coordination.
Green Mars Consulting
Founder & Delivery Lead | 2018 to 2020 | United States / Full-time Remote
Built delivery frameworks orchestrating up to 7 concurrent client implementation projects with a 25~~employee remote engineering team, driving consistency, accountability, and measurable quality across every delivery.
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
Design & Documentation: Lucidchart__•__Figma__•__ERD__Tools__• Miro__•__Mural__•__Confluence__(Wiki)
Development & APIs: Python__•__Next.js__•__Google__Apps__Script__• GraphQL__•__REST__•__JSON
Cloud & DevOps: AWS • Vercel • GitHub • CI/CD__Pipelines
Data & Analytics: PostgreSQL__•__MySQL__•__Prisma__•__Airtable__• Tableau__•__QlikView__•__Talend__(ETL)
Integration & Automation: Zapier__•__Google__Workspace__•__GitHub__Actions__• Make__•__Microsoft__365__•__Power__Automate
AI Development & Orchestration: Claude__API__•__GPT~~4__• Multi~~agent__workflows__• Prompt__engineering__• Cursor__• Copilot__• Structured__AI__outputs
Collaboration: Slack__•__Discord__•__Teams__• Zoom__•__Google__Meet
```

will render this html:

```
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>SomersetResume</title>
  <style>
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
  <meta name="description" content="Resume of Susan Somerset, Senior Technical Product Manager / Program Manager specializing in Cloud Platforms, Agile Delivery, SaaS, and Healthcare." />
</head>
<body>
  <header class="header">
    <h1>Susan Somerset • Senior Technical Program Manager</h1>
    <div class="contact">
      <span>hire@susansomerset.com • 415-745-5238 • linkedin.com/in/susansomerset • California, USA (PST)</span>
    </div>
  </header>

  <main class="content">
    <section aria-labelledby="summary">
      <h2 id="summary">Professional Summary</h2>
      <p class="summary-intro">A technical program manager who runs enterprise software implementations from kickoff through go-live and adoption—keeping multiple customer-facing engagements on schedule while coordinating across Product, Customer Success, and Solutions Architecture. Up to speed in days, not weeks, from the codebase to the roadmap, establishing canonical priorities, concrete success criteria, and the risks that actually threaten the date.</p>
      <p class="summary-intro">Across 30+ engagements spanning healthtech startups, FDA-regulated medical devices, and enterprise cloud platforms, I have owned full delivery lifecycles: scope and schedule, dependency and risk tracking, executive reporting, and the client relationship that determines whether a rollout actually gets adopted. I cut iteration cycles by as much as 80% through concise scope definition and hands-on technical deliberation, and I draw alignment from segmented stakeholders while speaking truth to power with diplomacy.</p>
      <p class="summary-intro">I know when and how to use AI to make real progress, not just create a different problem. I have personally built and deployed full-stack, AI-assisted software—so I coordinate technical teams and executives without waiting on someone to translate.</p>
    </section>

    <section aria-labelledby="competencies">
      <h2 id="competencies">Core Competencies</h2>
      <p class="competencies-list">Enterprise Implementation Management • Service Delivery • Customer Onboarding and Adoption • Go‑Live Readiness • Risk and Dependency Management • Stakeholder Alignment • Program Governance • Agile/Scrum Delivery • Executive Reporting • Requirements and Scope Definition • Systems Thinking</p>
    </section>

    <section aria-labelledby="experience">
      <h2 id="experience">Experience</h2>
      <article class="role">
        <div class="role-header">
          <p class="compact-title"><strong>Principal Technical Program Manager • Somerset Consulting</strong></p>
          <p class="compact-location"><em>2011 to Present: United States (Full-time Remote)</em></p>
        </div>
        <p class="role-description">Solo practice delivering embedded technical program and implementation management across 30+ SaaS engagements over 15 years—running customer-facing enterprise deployments from kickoff through go-live and adoption in healthcare, enterprise cloud, and workflow automation.</p>
        <ul>
          <li>Directed full implementation lifecycles for enterprise software deployments—scope, schedule, milestones, dependency and risk tracking—driving each engagement to on-time go-live and user adoption.</li>
          <li>Acted as the central point of coordination between customers and internal teams—Product, Customer Success, and Solutions Architecture—aligning expectations on scope, schedules, milestones, and outcomes.</li>
          <li>Diagnosed and mitigated blockers and bottlenecks across distributed teams, implementing lightweight frameworks that reduced iteration cycles from 5 to 10 rounds per feature to only 1 or 2, tuned to team size and culture.</li>
          <li>Led technical program delivery across globally distributed teams of as many as 40 people, applying Agile cadence and CI/CD guardrails to achieve sprint‑level clarity and measurable delivery rhythm.</li>
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
          <li>Built and rolled out an enrollment funnel tracking system for a B2B2C wellness platform serving enterprise clients and their employees, increasing completion rates 50% by visualizing stages and working hands-on with engineering to optimize each step.</li>
          <li>Delivered a production-ready MVP that unlocked a global partnership with Manpower's Talent Solutions division, positioning the client for rapid, multinational expansion.</li>
        </ul>
      </article>

      <article class="role">
        <div class="role-header">
          <p class="compact-title"><strong>Technical Program Manager • EMIDS Technologies</strong></p>
          <p class="compact-location"><em>2021 to 2022: United States (Full-time Remote)</em></p>
        </div>
        <ul>
          <li>Managed enterprise implementation and onboarding for a large healthcare platform, personally driving 12 customer onboardings through security, legal, and compliance gates to HIPAA- and FHIR-compliant go-live.</li>
          <li>Championed platform adoption by reluctant engineering teams, securing buy-in from key system owners and aligning resources, timelines, and data access to enable full integration of patient services.</li>
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
          <li>Built delivery frameworks orchestrating up to 7 concurrent client implementation projects with a 25‑employee remote engineering team, driving consistency, accountability, and measurable quality across every delivery.</li>
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
          <h4>Design & Documentation</h4>
          <p>Lucidchart • Figma • ERD Tools • Miro • Mural • Confluence (Wiki)</p>
        </div>
        <div class="skill-category">
          <h4>Development & APIs</h4>
          <p>Python • Next.js • Google Apps Script • GraphQL • REST • JSON</p>
        </div>
        <div class="skill-category">
          <h4>Cloud & DevOps</h4>
          <p>AWS • Vercel • GitHub • CI/CD Pipelines</p>
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
          <h4>AI Development & Orchestration</h4>
          <p>Claude API • GPT‑4 • Multi‑agent workflows • Prompt engineering • Cursor • Copilot • Structured AI outputs</p>
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

#### chuckles — 2026-07-29T17:02:14.198Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-1039** | Summary newlines collapse to spaces (Experience ok) |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-1039** — _Summary newlines collapse to spaces (Experience ok)_
- **Issue reported:** In Session Resume Paste → Open HTML, newline characters (`\n`) correctly become new bullets/paragraphs in the Experience section, but in Professional Summary the same newlines are converted to regular spaces — summary text collapses instead of splitting into multiple `.summary-in
- **Should now:** Summary newlines produce separate summary paragraphs (multiple `.summary-intro` `<p>` elements), consistent with how Experience treats newlines as structural breaks, and matching the desired HTML’s multi-paragraph Professional Summary.
- **Quick check (this fix only):**
  1. Open Session Resume Paste.
  2. Paste a resume whose Professional Summary contains explicit newlines between paragraphs (and Experience lines that also use newlines).
  3. Parse → Open HTML.
  4. Confirm Experience honors newlines as new bullets/paragraphs.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-07-29T16:48:03.800Z
@chuckles While `\n` registers as new bullets/paragraphs in the experience section, they are converted to regular spaces in the Summary text in the resume render.

#### chuckles — 2026-07-29T15:00:23.196Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-1035** | View Parsed JSON button on Session Resume Paste |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-1035** — _View Parsed JSON button on Session Resume Paste_
- **Issue reported:** Session Resume Paste has Parse and Open HTML, but no way to inspect the parsed resume JSON between those steps. Susan cannot tell whether a remaining UAT gap is in the parse/JSON structure or in the HTML renderer.
- **Should now:** A **View Parsed JSON** control between Parse and Open HTML that shows the current parsed resume JSON (post-Parse) so UAT can separate structure vs render issues.
- **Quick check (this fix only):**
  1. Open Session Resume Paste.
  2. Paste a resume fixture and click Parse.
  3. Observe controls: there is no View Parsed JSON between Parse and Open HTML.
  4. Open HTML alone does not expose the intermediate JSON for debugging.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-07-29T14:33:09.483Z
In scope for 1019, just under-defined original specification. You know how end users can be…

#### chuckles — 2026-07-29T04:48:42.369Z
[fix-uat] blocked: open question — need your call before filing.

Your latest note asks for a **View Parsed JSON** button between Parse and Open HTML (debug whether the remaining gap is JSON structure vs renderer).

That is not tied to any Acceptance criteria on this epic (cosmetics / laundry list 1–15 / AC 1–8). Filing it as a UAT Bug would invent scope.

@susan — please pick one:
1. **In scope for AST-1019** — confirm I should file a Bug child and ship the button under this epic (I will quote that call as AC for the wave), or
2. **Out of scope / separate Task** — park it (e.g. Session Resume Paste tooling ticket) and keep UAT on render-format gaps only, or
3. **Different remaining render bug** — if the button was only a means to an end, paste the actual format/structure failure and I will file that instead.

— Chuckles

#### susan — 2026-07-29T04:47:47.644Z
@chuckles For debugging purposes, please display the parsed json resume (add a button for "view parsed json" between Parse and Open HTML.  I need to see if the issue is with the json structure or with the renderer.

#### chuckles — 2026-07-29T04:35:39.896Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-1027** | __ markers not 1:1 &nbsp; in HTML emit |
| **AST-1028** | keywords emit in resume body instead of meta |
| **AST-1029** | competencies separators print as pipes |
| **AST-1030** | <no bullet> lead emitted as list item |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-1027** — ___ markers not 1:1 &nbsp; in HTML emit_
- **Issue reported:** Session Resume Paste → Open HTML emits skill / separator lines where `__` markers are not replaced 1:1 with `&nbsp;`. Example input:
- **Should now:** Every `__` in the paste is replaced with `&nbsp;` (1:1). For the sample: `Jira&nbsp;•&nbsp;Confluence&nbsp;•&nbsp;…` and `Jira&nbsp;Align` (etc.).
- **Quick check (this fix only):**
  1. Open Session Resume Paste.
  2. Paste fixture text that includes `__` around bullets and inside multi-word tokens (as above).
  3. Parse → Open HTML; inspect skills / competencies / contact source for `__` → `&nbsp;` fidelity.

**AST-1028** — _keywords emit in resume body instead of meta_
- **Issue reported:** Keywords / specialty line is rendered in the resume body header instead of only in ATS meta. Observed body text:
- **Should now:** Header stays `Name • Title` (markers applied). Candidate-specific keywords/tagline feed `meta name="description"` (field-derived template), not an extra visible header line.
- **Quick check (this fix only):**
  1. Session Resume Paste with a paste that carries title + keyword/tagline fields (UAT paste showing Fractional TPM + keyword list).
  2. Parse → Open HTML.
  3. Confirm keywords are not in the visible header; confirm `<meta name="description">` carries the candidate-specific keywords string.

**AST-1029** — _competencies separators print as pipes_
- **Issue reported:** Core Competencies list prints pipe separators instead of bullet characters:
- **Should now:** Competencies separators match golden / fixture treatment — bullet/`•` characters (with nbsp where markers require), not `|`.
- **Quick check (this fix only):**
  1. Session Resume Paste with Core Competencies lines (UAT paste that currently renders pipes).
  2. Parse → Open HTML.
  3. Inspect `.competencies-list` text — separators must be bullets, not `|`.

**AST-1030** — _<no bullet> lead emitted as list item_
- **Issue reported:** `<no bullet>` lead copy under a role is emitted as a `<li>` inside `<ul>` instead of a non-list lead paragraph. Observed Somerset Consulting role HTML starts:
- **Should now:** Lines marked `<no bullet>` render as role lead paragraph (`.role-description`), not list items. Following true bullets remain `<li>`.
- **Quick check (this fix only):**
  1. Paste experience block including a `<no bullet>…` lead line under a role (as in parent Original brief / UAT paste).
  2. Parse → Open HTML.
  3. Confirm lead text is `<p class="role-description">` (or equivalent non-li), then `<ul><li>…` for real bullets only.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-07-29T03:14:39.187Z
`<no bullet>` not honored:

```
<article class="role">
        <div class="role-header">
          <p class="compact-title"><strong>Principal Technical Program Manager&nbsp;• Somerset Consulting</strong></p>
          <p class="compact-location"><em>2011 to Present: United States (Full-time Remote)</em></p>
        </div>
        <ul>
          <li>Solo practice delivering embedded technical program management across 30+ SaaS engagements over 15 years—brought into troubled or fast-moving programs in healthcare, enterprise cloud, and workflow automation to restore delivery, rebuild stakeholder trust, and ship.</li>
          <li>Diagnosed and mitigated blockers and bottlenecks across distributed teams, implementing lightweight frameworks that reduced iteration cycles from 5 to 10 rounds per feature to only 1 or 2, tuned to team size and culture.</li>
          <li>Embedded in programs mid-flight to establish canonical priorities, concrete success criteria, and risk mitigation—drawing alignment from segmented stakeholders and driving progress through uncertainty.</li>
          <li>Led technical program delivery across globally distributed teams of as many as 40 people, applying Agile cadence and CI/CD guardrails to achieve sprint-level clarity and measurable delivery rhythm.</li>
          <li>Partnered with founders, executives, and engineering leads to translate complex goals into executable roadmaps and measurable OKRs, embedding Agile/Scrum delivery and metrics-driven accountability.</li>
          <li>Architected a multi-agent AI recruiting pipeline integrating web scraping, LLM-based analysis, and document generation—reducing manual job-matching time by 90% while maintaining quality through staged human review.</li>
          <li>Worked with lead architects to optimize cloud infrastructure—reducing AWS spend by 70% and saving $23K annually in one instance—while increasing CI/CD deployment velocity.</li>
        </ul>
      </article>
```

#### susan — 2026-07-29T03:13:30.939Z
Core competencies printing with | instead of bullet characters.

```
<p class="competencies-list">AI-Assisted Delivery | Cross-Functional Execution | Risk and Dependency Management | Stakeholder Alignment | Program Governance | Delivery Turnaround | Agile/Scrum Delivery | Executive Reporting | Roadmapping | Requirements and Scope Definition | Systems Thinking</p>
```

#### susan — 2026-07-29T03:11:15.710Z
Keywords printing on the resume content instead of in meta content

```
Susan Somerset&nbsp;• Fractional TPM — Program Delivery, Cross-Functional Alignment, Cloud SaaS, AI-Assisted Engineering
```

```
<head>
  ...  
  <meta name="description" content="<keywords>" />
</head>
```

#### susan — 2026-07-29T03:06:57.637Z
Missing non-breaking space throughout content where specified in the input text:

```
Program & Delivery: Jira__•__Confluence__•__Linear__• Jira__Align__•__Azure__DevOps__•__Asana__• Trello__•__JAMA__•__Pivotal__Tracker
```

HTML output:

```
<div class="skill-category">
          <h4>Program &amp; Delivery</h4>
          <p>Jira&nbsp;• Confluence&nbsp;• Linear&nbsp;• Jira Align&nbsp;• Azure DevOps&nbsp;• Asana&nbsp;• Trello&nbsp;• JAMA&nbsp;• Pivotal Tracker</p>
        </div>
```

Expected 1:1 replace for every occurence of `__` with `&nbsp;`

#### chuckles — 2026-07-29T02:17:33.553Z
@susan It isn’t blocked on product or Archie — Linear status is In Progress and the wave is running.

- AST-1020 → User Testing (Katherine done)
- AST-1021 → Plan Approved; Ada is on build-child now

Earlier chat `blocked:` lines were orchestration pauses (MCP / rate limit / drone kills), not a Blocked ticket state. When AST-1021 hits User Testing I’ll run prep-uat.

— Chuckles

#### chuckles — 2026-07-29T02:06:02.031Z
[thread-missing] Ada engineer Team thread UUID `6f5cda06-9d75-4a08-8327-e1e31df75c3a` — look path `/home/susan/.cursor/chats/a89c0f09cff3e778df7dfaab512371d8/6f5cda06-9d75-4a08-8327-e1e31df75c3a/store.db` absent on this host. Minting replacement Ada Team thread and continuing.

— Chuckles

#### susan — 2026-07-29T02:05:04.797Z
@chuckles Why is this issue blocked?

#### chuckles — 2026-07-28T20:14:59.983Z
[thread-missing] Betty Team row store.db absent on this host.
Look path: `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/e41d52ae-7acd-460f-bd1f-bf8e3def7178/store.db`
UUID: `e41d52ae-7acd-460f-bd1f-bf8e3def7178`
Minted replacement: `f9bd91a0-0d9e-4ec6-b60b-b3d5a7fcfdde` (Betty @ astral-tests).

[thread-missing] Radia Team row store.db absent on this host.
Look path: `/home/susan/.cursor/chats/a89c0f09cff3e778df7dfaab512371d8/23fbdd2d-435c-4f75-80ef-bb9f9cf1ca5b/store.db`
UUID: `23fbdd2d-435c-4f75-80ef-bb9f9cf1ca5b`
Minted replacement: `fca4bccf-3876-4699-9a54-5207ad2100d2` (Radia @ epic).

— Chuckles

#### chuckles — 2026-07-28T19:54:38.202Z
[thread-missing] Team rows had no local `store.db` on **chuckles**. Looked for:
- Katherine `bc2b570e-4ba1-40f9-a8ca-9cb3b8925bcd` → `~/.cursor/chats/*/bc2b570e-4ba1-40f9-a8ca-9cb3b8925bcd/store.db`
- Betty `c6deaf51-bda1-472b-b2b9-e0e4eeb2b4b4` → `~/.cursor/chats/*/c6deaf51-bda1-472b-b2b9-e0e4eeb2b4b4/store.db`
- Radia `81f1fcf6-ce91-44f4-8c87-13bb47a0a273` → `~/.cursor/chats/*/81f1fcf6-ce91-44f4-8c87-13bb47a0a273/store.db`
- Ada `4ed12c60-8986-4ab4-af21-ed3e58debee9` → `~/.cursor/chats/*/4ed12c60-8986-4ab4-af21-ed3e58debee9/store.db`

Minted new conversations and updated ## Team. Continuing.

— Chuckles

#### susan — 2026-07-28T19:45:53.294Z
@chuckles I think this description needs a redraft to include the new formatting requirements.

#### chuckles — 2026-07-28T18:06:41.932Z
@susan

1. The input paste fence in the brief is empty — please paste the marker-laden input that should produce this desired HTML (or confirm reverse-engineer from the golden body using AST-993 `__` / `~~` conventions).
2. Desired HTML uses document `<title>SomersetResume</title>`. AST-993 left `{name} — Resume`. Keep that, or switch to the golden title?
3. Golden meta description uses title text `Senior Technical Product Manager / Program Manager` while the h1 uses `Senior Technical Program Manager` — intentional (meta title ≠ header title), or fix toward one string?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
