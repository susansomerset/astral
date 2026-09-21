# AST-1019 — Take 2: Resume Render Format discrepancies
**Component:** artifacts  
**Children:** AST-1020, AST-1021, AST-1027, AST-1028, AST-1029, AST-1030, AST-1035, AST-1039  
**Linear archived:** AST-1019 2026-08-05; AST-1020 2026-08-05; AST-1021 2026-08-05; AST-1027 2026-08-05; AST-1028 2026-08-05; AST-1029 2026-08-05; AST-1030 2026-08-05; AST-1035 2026-08-05; AST-1039 2026-08-05

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-07-28 12:58 | AST-1020 | docs | `a0b70b477` | docs(AST-1020): plan — embedded stylesheet golden parity |
| 2026-07-28 13:21 | AST-1020 | code | `6104b15b0` | code(AST-1020): Stage 1 — golden text/border color tokens |
| 2026-07-28 13:21 | AST-1020 | code | `89c3f44ce` | code(AST-1020): Stage 2 — embedded stylesheet golden parity |
| 2026-07-28 13:21 | AST-1020 | docs | `fd6757eb9` | docs(AST-1020): review stub after build |
| 2026-07-28 13:23 | AST-1020 | test | `4c04e20fa` | test(AST-1020): golden stylesheet parity + color tokens |
| 2026-07-28 13:24 | AST-1020 | merge-tests | `24a466ce4` | merge-tests(AST-1020): origin/tests 4c04e20fa |
| 2026-07-28 13:27 | AST-1020 | docs | `bbb8eb4b5` | docs(AST-1020): Radia review — findings |
| 2026-07-28 13:29 | AST-1020 | resolve | `1cf1878ba` | resolve(AST-1020): — clean |
| 2026-07-28 19:12 | AST-1021 | docs | `37527f56b` | docs(AST-1021): plan — residual emit chrome tweaks |
| 2026-07-28 19:18 | AST-1021 | docs | `66f9f63b4` | docs(AST-1021): review stub after build |
| 2026-07-28 19:18 | AST-1021 | code | `712bd3246` | code(AST-1021): Stage 1 — document title {name} Resume |
| 2026-07-28 19:20 | AST-1021 | merge-tests | `517faa964` | merge-tests(AST-1021): origin/tests bcb2d83aa |
| 2026-07-28 19:20 | AST-1021 | test | `bcb2d83aa` | test(AST-1021): document title chrome + meta lock |
| 2026-07-28 19:23 | AST-1021 | docs | `73ab77f9a` | docs(AST-1021): Radia review — findings |
| 2026-07-28 19:25 | AST-1021 | resolve | `8dd054923` | resolve(AST-1021): — clean |
| 2026-07-28 19:29 | AST-1019 | prep-uat | `b81bc968a` | prep-uat(AST-1019): rebuild merge ticket log |
| 2026-07-28 20:28 | AST-1027 | docs | `f28d8dbf0` | docs(AST-1027): plan — UAT markers nbsp preserve |
| 2026-07-28 20:31 | AST-1027 | code | `eedc91e48` | code(AST-1027): Stage 1 — preserve __/~~ in craft_resume_base |
| 2026-07-28 20:35 | AST-1027 | merge-tests | `b16675cd6` | merge-tests(AST-1027): origin/tests b264fd619 |
| 2026-07-28 20:35 | AST-1027 | test | `b264fd619` | test(AST-1027): craft_resume_base marker preserve + UAT expand |
| 2026-07-28 20:38 | AST-1027 | docs | `f8f0f3247` | docs(AST-1027): Radia review — clean |
| 2026-07-28 20:40 | AST-1027 | resolve | `e1f678e80` | resolve(AST-1027): — clean |
| 2026-07-28 20:46 | AST-1028 | docs | `a475761b1` | docs(AST-1028): plan — UAT keywords meta vs header |
| 2026-07-28 20:48 | AST-1028 | code | `d83b486bf` | code(AST-1028): Stage 1 — title vs tagline in craft_resume_base |
| 2026-07-28 20:51 | AST-1028 | test | `99df7288e` | test(AST-1028): title/tagline split prompt + keywords-in-meta emit |
| 2026-07-28 20:51 | AST-1028 | merge-tests | `efec1f04a` | merge-tests(AST-1028): origin/tests 99df7288e |
| 2026-07-28 20:54 | AST-1028 | docs | `d749c1015` | docs(AST-1028): Radia review — clean |
| 2026-07-28 20:56 | AST-1028 | resolve | `672b2eea5` | resolve(AST-1028): — clean |
| 2026-07-28 21:06 | AST-1029 | docs | `400145cca` | docs(AST-1029): plan — UAT competencies pipes to bullets |
| 2026-07-28 21:08 | AST-1029 | code | `c24f2aabb` | code(AST-1029): Stage 1 — competencies • not pipe separators |
| 2026-07-28 21:11 | AST-1029 | test | `5fc85d9a1` | test(AST-1029): competencies • separators prompt + emit lock |
| 2026-07-28 21:14 | AST-1029 | docs | `38bcbc165` | docs(AST-1029): Radia review — clean |
| 2026-07-28 21:15 | AST-1029 | resolve | `644ded32f` | resolve(AST-1029): — clean |
| 2026-07-28 21:17 | AST-1029 | merge-tests | `c6149e4d1` | merge-tests(AST-1029): origin/tests 5fc85d9a1 |
| 2026-07-28 21:21 | AST-1030 | docs | `f04c20800` | docs(AST-1030): plan — UAT no-bullet lead preserve |
| 2026-07-28 21:25 | AST-1030 | code | `f54d3519a` | code(AST-1030): Stage 1 — preserve <no bullet> in accomplishments |
| 2026-07-28 21:27 | AST-1030 | test | `133c5cde2` | test(AST-1030): craft_resume_base <no bullet> preserve + emit lock |
| 2026-07-28 21:27 | AST-1030 | merge-tests | `67718600c` | merge-tests(AST-1030): origin/tests 133c5cde2 |
| 2026-07-28 21:30 | AST-1030 | docs | `b35e68bbb` | docs(AST-1030): Radia review — clean |
| 2026-07-28 21:33 | AST-1030 | resolve | `7da1695d7` | resolve(AST-1030): — clean |
| 2026-07-28 21:35 | AST-1019 | prep-uat | `ddc438db4` | prep-uat(ast-1019): rebuild merge ticket log |
| 2026-07-29 07:50 | AST-1035 | docs | `951569095` | docs(AST-1035): plan — View Parsed JSON on Session Resume Paste |
| 2026-07-29 07:52 | AST-1035 | code | `5f920814a` | code(AST-1035): View Parsed JSON modal on Session Resume Paste |
| 2026-07-29 07:54 | AST-1035 | test | `3538ee6eb` | test(AST-1035): View Parsed JSON modal on Session Resume Paste |
| 2026-07-29 07:54 | AST-1035 | merge-tests | `91d25515c` | merge-tests(AST-1035): origin/tests 3538ee6eb |
| 2026-07-29 07:57 | AST-1035 | docs | `c0be4044e` | docs(AST-1035): Radia review — clean |
| 2026-07-29 07:58 | AST-1035 | resolve | `fc1bd6707` | resolve(AST-1035): — clean |
| 2026-07-29 08:00 | AST-1019 | prep-uat | `4e46e29cb` | prep-uat(ast-1019): rebuild merge ticket log |
| 2026-07-29 09:53 | AST-1039 | docs | `fc49b3323` | docs(AST-1039): plan — Summary newlines → summary-intro paragraphs |
| 2026-07-29 09:54 | AST-1039 | code | `b76345ad0` | code(AST-1039): Summary single-\n → multiple summary-intro paragraphs |
| 2026-07-29 09:56 | AST-1039 | test | `98103cee6` | test(AST-1039): summary single-\n → multiple .summary-intro |
| 2026-07-29 09:56 | AST-1039 | merge-tests | `c213ed4b1` | merge-tests(AST-1039): origin/tests 98103cee6 |
| 2026-07-29 09:59 | AST-1039 | docs | `558b86f56` | docs(AST-1039): Radia review — clean |
| 2026-07-29 10:01 | AST-1039 | resolve | `9666ee2b2` | resolve(AST-1039): — clean |
| 2026-07-29 10:02 | AST-1019 | prep-uat | `05ff6b273` | prep-uat(ast-1019): rebuild merge ticket log |
| 2026-08-05 14:54–14:55 | AST-1020/1021/1027/1028/1029/1030/1035/1039 | docs | `64c5495f4` `b679b806e` `897151098` `2a6be5c4c` `e35e52841` `762b25602` `07a7c55cb` `a924359aa` | docs(AST-NNNN): archive Linear issue content |
| 2026-08-05 14:58 | AST-1019 | docs | `f02b0e06f` | docs(AST-1019): archive Linear issue content |

_Three `Merge remote-tracking branch 'origin/dev' into tmp-refresh-…` commits (`ec37d5810`, `59c2fb722`, `4f5ba7b51`) accompany the `prep-uat(ast-1019)` merge-log rebuilds — routine refreshes, no product change._

## Epic — AST-1019
_Archived: 2026-08-05 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1019/take-2-resume-render-format-discrepancies · Status at archive: Archive · Project: Astral Artifacts · Assignee: chuckles · Priority / estimate: Urgent / — · Blocked by / blocks / related: —_

### Purpose

AST-993 closed structure for resume HTML (markers, role layout, education/skills/prior, header/meta) but UAT used incomplete desired HTML and guessed styles without the real legacy stylesheet. This epic is the corrected Take 2 fixture: close every remaining **style, format, font, structure, alignment, and cosmetic** gap so Session Resume Paste → Open HTML (and the shared builder family) matches the input paste + desired HTML in this ticket's Original brief — including the full embedded `<style>` block Susan provided.

### Functional scope

#### Formatting requirements (laundry list — authoritative)

These are the remaining changes the render software must make. If it is not listed here, it is out of scope for this epic.

**Document chrome**

1. Document `<title>` is `{candidate_name} Resume` (single space; **no** em/en dashes) — not `SomersetResume` and not `{name} — Resume`.
2. ATS `<meta name="description">` is **candidate-specific** from paste name / title / tagline using the AST-993 field-derived template `Resume of <name>, <title>, specializing in <tagline>`. The literal meta string in the desired HTML is an **example of structure only** — do not force that fixed Product Manager / Cloud Platforms text when the paste carries different title/tagline.

**Embedded stylesheet (match desired `<style>` block)**
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

**Structure already owned by AST-993 (must remain correct under the new styles)**
13. Header `Name • Title` with markers; contact one line with markers; Professional Summary as multiple `.summary-intro` paragraphs; Core Competencies one competencies list; Experience role articles (compact title/location, optional lead paragraph, bullets); Prior Experience competencies-list style; Education per-line emphasized credentials; Technical Skills category grid markup; nested `__` / `~~` markers end-to-end.

**Surfaces**
14. Same cosmetics on session paste HTML, candidate base-resume HTML, and job-tailored resume HTML that share the builder family.
15. Fixture-driven UAT: Original-brief input paste → Open HTML matches desired structure + cosmetics (eye + HTML source). No "close enough."

### Boundaries

* Does **not** re-litigate AST-993 / AST-1007–1010 structural contracts except where corrected CSS or residual emit needs a cosmetic tweak.
* Does **not** rewrite resume *content* (paste/parse supplies copy).
* Does **not** redesign Manage Tasks prompts, invent new resume sections, or change cover-letter HTML.
* Does **not** add server-side PDF generation; Print → PDF from the HTML tab remains the path.
* Does **not** persist session paste to the candidate database (AST-985).
* Does **not** switch to an external `styles07.css` — embedded styles only.
* Must **not** break AST-985/986/987 Session Resume Paste → Open HTML, AST-994 job-array experience render, or AST-993 marker/layout behavior already correct.
* Code Rules: config-driven style tokens stay in config; no new top-level artifacts dump directory.
* Existing children AST-1020 / AST-1021 already map to the proposed slices below (created on a prior Todo pass; parent returned to Discussion for this redraft). Re-dispatch must not duplicate them.

### Acceptance criteria

1. Pasting the Original-brief input fixture through Session Resume Paste Parse → Open HTML yields an embedded `<style>` that carries the golden rules for items 3–12 above (fonts, colors, decorative `h2`, contact flex, role/education/skills spacing and type, skills grid, mobile, print) — verifiable in HTML source and print/preview.
2. Experience roles, education indent/credentials, and Technical Skills category grid match golden spacing/typography (items 7–9).
3. Contact is the golden centered flex line; header remains `Name • Title` with markers — fixture shows `Susan Somerset • Senior Technical Program Manager` with non-breaking spaces from `__`.
4. No external stylesheet link; styles are embedded.
5. Document `<title>` is `{candidate_name} Resume` (item 1).
6. Meta description is candidate-specific from paste name/title/tagline (item 2) — not the stale Product Manager / Cloud Platforms example string when paste differs.
7. Shared builders (session, base, job-tailored) show the same cosmetics for equivalent structured content.
8. Susan can verify by eye against the desired HTML for every laundry-list item; no judgment call on "close enough."

### Dependencies and blockers

* AST-993 — structural stack (AST-1007–1010). Prefer landed on `origin/dev` or work atop its `ftr`.
* AST-985 / AST-986 / AST-987 — Session Resume Paste UAT surface.
* none otherwise.

### Open questions

none.

### Proposed child tickets

**1[*]: Embedded stylesheet golden parity — Katherine** *(Linear AST-1020)* — Owns laundry-list items **3–12** (and shared-surface stylesheet application for **14**): bring the embedded resume stylesheet to the ticket's full `<style>` block — contact flex, role/education/skills spacing and type, skills CSS grid, all-caps treatments, mobile and print, config-driven font/color tokens as needed. Does **not** own document title / meta emit (**2** / Ada).

**2: Residual emit / chrome tweaks — Ada** *(Linear AST-1021)* — Owns laundry-list items **1–2** plus any emit/`white-space`/class leftovers CSS cannot fix. Document title `{name} Resume`; candidate-specific field-derived meta (example string in desired HTML is structure-only). Does **not** rework AST-993 structural contracts or the stylesheet slice. After #1; thin/skip if UAT shows CSS-only is enough.

**New pattern:** Corrected golden HTML+CSS fixture (Take 2) with explicit formatting laundry list — introduced across #1–#2.

**Monolith check:** Laundry list has 15 scoped items; 2 children split stylesheet vs emit/chrome (CSS-first). Existing AST-1020/AST-1021 stay the implementers.

_(UAT bugs AST-1027–AST-1030, AST-1035, AST-1039 were filed later as children during the fix-uat wave.)_

### Original brief

AST-993 had the wrong html content and did not include the style details (it was in a separate css file I did not provide.)

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
    <h1>Susan Somerset • Senior Technical Program Manager</h1>
    <div class="contact">
      <span>hire@susansomerset.com • 415-745-5238 • linkedin.com/in/susansomerset • California, USA (PST)</span>
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
      <p class="competencies-list">Enterprise Implementation Management • Service Delivery • Customer Onboarding and Adoption • Go‑Live Readiness • Risk and Dependency Management • Stakeholder Alignment • Program Governance • Agile/Scrum Delivery • Executive Reporting • Requirements and Scope Definition • Systems Thinking</p>
    </section>

    <section aria-labelledby="experience">
      <h2 id="experience">Experience</h2>
      <article class="role">
        <div class="role-header">
          <p class="compact-title"><strong>Principal Technical Program Manager • Somerset Consulting</strong></p>
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
      <p class="competencies-list">Project Manager (4 yrs) • Systems Analyst (6 yrs) • ETL Migration Specialist (2 yrs) • Database Engineer (2 yrs) • VBA Software Developer (3 yrs)</p>
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
          <p>Jira • Confluence • Linear • Jira Align • Azure DevOps • Asana • Trello • JAMA • Pivotal Tracker</p>
        </div>
        <div class="skill-category">
          <h4>Design & Documentation</h4>
          <p>Lucidchart • Figma • ERD Tools • Miro • Mural • Confluence (Wiki)</p>
        </div>
        <div class="skill-category">
          <h4>Development & APIs</h4>
          <p>Python • Next.js • Google Apps Script • GraphQL • REST • JSON</p>
        </div>
        <div class="skill-category">
          <h4>Cloud & DevOps</h4>
          <p>AWS • Vercel • GitHub • CI/CD Pipelines</p>
        </div>
        <div class="skill-category">
          <h4>Data & Analytics</h4>
          <p>PostgreSQL • MySQL • Prisma • Airtable • Tableau • QlikView • Talend (ETL)</p>
        </div>
        <div class="skill-category">
          <h4>Integration & Automation</h4>
          <p>Zapier • Google Workspace • GitHub Actions • Make • Microsoft 365 • Power Automate</p>
        </div>
        <div class="skill-category">
          <h4>AI Development & Orchestration</h4>
          <p>Claude API • GPT‑4 • Multi‑agent workflows • Prompt engineering • Cursor • Copilot • Structured AI outputs</p>
        </div>
        <div class="skill-category">
          <h4>Collaboration</h4>
          <p>Slack • Discord • Teams • Zoom • Google Meet</p>
        </div>

      </div>
    </section>
  </main>
</body>
</html>
```

#### Comments

##### chuckles — 2026-07-28T18:06:41.932Z (open questions)
1. The input paste fence in the brief is empty — please paste the marker-laden input that should produce this desired HTML (or confirm reverse-engineer from the golden body using AST-993 `__` / `~~` conventions).
2. Desired HTML uses document `<title>SomersetResume</title>`. AST-993 left `{name} — Resume`. Keep that, or switch to the golden title?
3. Golden meta description uses title text `Senior Technical Product Manager / Program Manager` while the h1 uses `Senior Technical Program Manager` — intentional (meta title ≠ header title), or fix toward one string?

_(Resolved into the laundry list above: title becomes `{candidate_name} Resume` (item 1); the golden meta string is an example of structure only — meta stays candidate-specific / field-derived (item 2). Susan supplied the marker-laden input paste, now the Original brief fixture.)_

##### susan — 2026-07-28T19:45:53.294Z
@chuckles I think this description needs a redraft to include the new formatting requirements. _(→ redraft to the laundry list above)_

##### susan — 2026-07-29T03:06:57.637Z — UAT: missing non-breaking space (→ AST-1027)
Missing non-breaking space throughout content where specified in the input text. Input `Program & Delivery: Jira__•__Confluence__•__Linear__• Jira__Align__• …`; HTML output `<p>Jira&nbsp;• Confluence&nbsp;• Linear&nbsp;• Jira Align&nbsp;• …</p>`. Expected 1:1 replace for every occurrence of `__` with `&nbsp;`.

##### susan — 2026-07-29T03:11:15.710Z — UAT: keywords in body not meta (→ AST-1028)
Keywords printing on the resume content instead of in meta content: `Susan Somerset&nbsp;• Fractional TPM — Program Delivery, Cross-Functional Alignment, Cloud SaaS, AI-Assisted Engineering`. Expected `<meta name="description" content="<keywords>" />` in `<head>`.

##### susan — 2026-07-29T03:13:30.939Z — UAT: competencies pipes (→ AST-1029)
Core competencies printing with `|` instead of bullet characters: `<p class="competencies-list">AI-Assisted Delivery | Cross-Functional Execution | Risk and Dependency Management | …</p>`.

##### susan — 2026-07-29T03:14:39.187Z — UAT: `<no bullet>` not honored (→ AST-1030)
`<no bullet>` not honored — the Somerset Consulting role's `<no bullet>` lead line is emitted as the first `<li>` inside `<ul>` instead of a `<p class="role-description">` lead paragraph.

##### susan — 2026-07-29T04:47:47.644Z — request: View Parsed JSON (→ AST-1035)
@chuckles For debugging purposes, please display the parsed json resume (add a button for "view parsed json" between Parse and Open HTML. I need to see if the issue is with the json structure or with the renderer.

##### chuckles — 2026-07-29T04:48:42.369Z / susan — 2026-07-29T14:33:09.483Z
Chuckles flagged the View Parsed JSON button as untied to any AC (would invent scope) and asked Susan to pick: in scope for AST-1019, separate Task, or a different render bug. **Susan: "In scope for 1019, just under-defined original specification. You know how end users can be…"** — so AST-1035 ships under this epic and Susan's call is quoted as the AC for that wave.

##### susan — 2026-07-29T16:48:03.800Z — UAT: summary newlines collapse (→ AST-1039)
@chuckles While `\n` registers as new bullets/paragraphs in the experience section, they are converted to regular spaces in the Summary text in the resume render.

##### chuckles — 2026-07-29 [fix-uat] waves
Wave 1 (`2026-07-29T04:35`): AST-1027 / AST-1028 / AST-1029 / AST-1030 landed. Wave 2 (`15:00`): AST-1035. Wave 3 (`17:02`): AST-1039. Local `dev` merged via prep-uat each time.

_(`[thread-missing]` cursor-chats store.db rebuild notes and "why is this blocked" orchestration-pause narration omitted.)_

### Files changed (plan vs actual)

_No product commit trail on the parent — `prep-uat(ast-1019)` commits rebuild the merge ticket log (each paired with a routine `Merge remote-tracking branch 'origin/dev'` refresh). Implementation landed via the eight sub-issues below._

_Implementation detail may live in git history on `origin/dev`._

## Sub-issues

### AST-1020 — Embedded stylesheet golden parity
_Archived: 2026-08-05 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1020/embedded-stylesheet-golden-parity-take-2-resume-render-format · Status at archive: Archive · Project: Astral Artifacts · Assignee: katherine · Priority / estimate: None / — · Blocked by / blocks / related: parent: AST-1019; blocks: AST-1021_

#### What this implements

Align the shared resume embedded stylesheet with the AST-1019 golden `<style>` block: contact flex, role/education/skills spacing and type, skills CSS grid, all-caps skills/competencies treatment, mobile and print rules, and config-driven token updates needed for fonts/colors already partially correct. Does not own DOM emit changes beyond what CSS alone can fix.

#### Acceptance criteria

Parent AC 1–4, 7, 8 for the stylesheet slice — embedded `<style>` carries golden rules for laundry items 3–12; experience/education/skills match golden spacing/typography; contact golden centered flex line; no external stylesheet link; shared-builder parity; eye-verify no "close enough". Document title / meta (AC 5–6) are sibling AST-1021.

#### Boundaries

Does not own residual DOM emit / document title / meta string tweaks (sibling Ada). Does not rework AST-993 structural contracts. Does not change cover-letter HTML.

#### Golden CSS contract (stylesheet only)

Authoritative source: parent AST-1019 Original-brief desired HTML `<style>` block (laundry-list items **3–12**). After this ticket, the embedded `<style>` in HTML from `build_session_base_resume` / `build_base_resume` / `build_resume_from_job` must carry (selectors and declarations must match; token values may interpolate from `style` / `BUILD_CONFIG["default_style"]`):

- `:root` — `--max-width: 800px`; accent/header from style; `--text-primary`/`--text-secondary`/`--text-tertiary`; `--border-light`/`--border-medium`; three font stacks.
- Typography alignment — `h1,h2,h3,.title,.specialties` header font + center; `.contact,.competencies-list,.skill-category p` list font + center; `.skill-category h4` header font + center; `p,.role-description,ul,li` body font + left + `line-height: 1.25`; `p { margin-bottom: 12px }`; unused-but-present `.job-title` / `.dates` rules.
- All-caps — `.competencies-list` and `.skill-category p`: uppercase, `letter-spacing: 0.2px`, `font-size: 13.5px`.
- Contact — `.contact`: flex, wrap, `gap: 8px 16px`, `justify-content: center`; `.contact span { white-space: nowrap }`.
- Decorative `h2` — flex + `::before`/`::after` hairlines (keep exact golden sizes/margins).
- Experience — `.role` `margin-bottom: 12px` + `page-break-inside: avoid`; `.role-header` `margin-top: 20px; margin-bottom: 8px`; `.compact-title` / `.compact-location` (14.5px tertiary body font; `em` italic 14.5px); `.role ul` `padding-left: 20px`; bullet `margin-bottom: 6px`.
- Education — `.education-list` `margin-left: 0.5in`; `line-height: 1.1`; `strong` on header font.
- Skills — `.skills-grid` CSS grid `repeat(auto-fit, minmax(280px, 1fr))` + gap; category `h4` centered uppercase accent-colored.
- Mobile — full `@media (max-width: 600px)` block from golden.
- Print — full `@media print` from golden **including** `#prior-experience { page-break-before: always }` always (not gated on `emit_prior_experience`).

Astral-only appendages that must **remain** after the golden resume rules (not in the desired HTML fixture, but required by existing builder surfaces): `.cover-block` / `.cover-signoff` rules; `.ats-keywords` rules from `ats_keyword_block` config; `.prose-block { white-space: pre-wrap; }` so the legacy string-`experience` emit path does not collapse newlines when golden general `p` rules drop `white-space: pre-wrap`. Do **not** emit `<link rel="stylesheet" …>`.

#### Stage 1: Config — golden text/border color tokens

**Done when:** `BUILD_CONFIG["default_style"]["colors"]` exposes the golden text and border literals below; fonts / accent / header / page_background remain as today (`#3c2c6e`, `#f5f5f5`, Helvetica Neue / Palatino stacks). No other `BUILD_CONFIG` keys change.

Inside `BUILD_CONFIG["default_style"]["colors"]`, **add** (do not rename existing `ink` / `muted` / `rule` / `surface`): `text_primary: "#1a1a1a"`, `text_secondary: "#444"`, `text_tertiary: "#666"`, `border_light: "#e0e0e0"`, `border_medium: "#ccc"`. Correct any drift in `default_accent` / `default_header` / `page_background` / font stacks vs `#3c2c6e` / `#f5f5f5` / Helvetica Neue / Palatino in the same edit.
⚠️ **Decision:** Promote only the CSS custom-property colors that the golden `:root` defines and that Stage 2 interpolates. Do **not** move spacing/type-scale px values into config for this ticket — those stay as literal declarations in the CSS string copied from the golden block (same pattern as AST-1010).

#### Stage 2: Replace resume embedded CSS with golden parity

**Done when:** The `css` f-string inside `_emit_html_document` produces a `<style>` body whose resume rules match the golden contract above (selectors + declarations), interpolating `accent` / `header_c` / `page_bg` / font stacks / the five new color tokens; contact flex-centered; skills CSS grid; education `0.5in` indent; mobile and print blocks present; `#prior-experience { page-break-before: always }` always in the print block; cover + ATS + `.prose-block` appendages remain; no external stylesheet link; title/meta/header/contact emit code paths unchanged.

1. In `_emit_html_document`, after reading `fonts` / `colors` / `ak`, also read `text_primary`/`text_secondary`/`text_tertiary`/`border_light`/`border_medium` from `colors` with the Stage 1 defaults.
2. **Delete** the conditional `prior_rule` construction (`if emit_prior_experience: prior_rule = …`). Keep the `emit_prior_experience` parameter on the function signature (callers still pass it for body-section inclusion) — it must no longer affect CSS.
3. **Replace** the resume portion of the `css = f"""…"""` string (`:root` through the skills / competencies rules, before cover/ATS) with the golden stylesheet as an f-string — interpolate `{accent}`, `{header_c}`, `{page_bg}`, `{hstack}`, `{bstack}`, `{lstack}` and the five color tokens; copy every golden rule **verbatim** (including unused `.title` / `.specialties` / `.job-title` / `.dates`); use `.role-description` (not `.prose-block`) in the body typography group; do **not** put `white-space: pre-wrap` on the general `p, .role-description, ul, li` rule (golden does not).
4. **After** the golden skills rules and **before** the mobile block, append Astral-only `.prose-block { white-space: pre-wrap; }` + `.cover-block` / `.cover-signoff` / `.ats-keywords` (existing interpolations unchanged).
5. Append the golden Mobile block exactly; append the golden Print block exactly (including `#prior-experience { page-break-before: always }` and `#competencies { page-break-after: avoid }`) — no `{prior_rule}` splice.
6. Remove obsolete/divergent declarations that conflict with golden (`.contact` without flex; `.compact-location` on list font / 13px / secondary; `.role ul { padding-left: 1.25em }`; `.skills-grid` without `display: grid`; `.skill-category h4` left-aligned primary color; `.education-list` without `margin-left: 0.5in`; duplicate `article.role` margin rule).
7. Do **not** change the HTML template below the CSS. Title/meta remain AST-1021.
⚠️ **Decision:** One wholesale CSS replacement against the parent golden `<style>` block, plus the three Astral appendages — rather than piecemeal patches — avoids leaving half-updated AST-1010/1008 spacing values that fail UAT "no close enough."

#### Stage 3: Three-surface stylesheet proof (build verification)

**Done when:** For fixture-shaped content matching the AST-1019 paste, each of the three public builders yields HTML whose embedded `<style>` contains the Stage 2 selectors/declarations (spot-check: `.contact{` flex + gap; `.skills-grid` `minmax(280px`; `.education-list` `0.5in`; `.compact-location` `14.5px`; `@media (max-width: 600px)`; `#prior-experience { page-break-before: always }`); no `<link rel="stylesheet"`; header still `Name • Title` with markers; cover HTML path untouched when not requested. Spike dumps only under `debug/spikes/AST-1020/`.

**Self-Assessment:** Single-Component — `BUILD_CONFIG["default_style"]["colors"]` tokens plus the embedded CSS string inside `_emit_html_document`; no emit markup or UI layer changes. Conf high — golden `<style>` is pasted in the parent Original brief; builder already interpolates fonts/accent into one CSS f-string. Risk Medium — wrong stylesheet would visually regress all three resume surfaces, including print pagination for Prior Experience.

##### Comments

###### katherine — 2026-07-28T19:58:22.064Z
Plan @ `a0b70b47`. Single-Component — `BUILD_CONFIG["default_style"]["colors"]` text/border tokens + the embedded CSS string in `builder._emit_html_document` only (no emit markup). Conf high; Risk Medium.

###### joan — 2026-07-28T20:14:24.273Z (plan-rubric.v1)
**Overall: APPROVED.** Stages 1–3 map to laundry items 3–12 + AC7. All in-scope statutes **conforms**. **acceptable:** Astral-only `.cover-block` / `.ats-keywords` / `.prose-block` rules appended between golden skills and mobile — `<style>` won't be byte-identical to the parent fixture; Stage 3 correctly gates on golden selectors/declarations. No `fix-now`.

###### betty — 2026-07-28T20:24:25.336Z
QA manifest AST-1020: golden stylesheet parity + color tokens (`test_builder.py::TestAst1020GoldenStylesheet`, `test_config.py::TestAst1020DefaultStyleColorTokens`, + AST-1010/998/1008/1009 regressions). Obsolete: `TestAst1010HeaderContactMetaStyles` pre–Take-2 negative assert that contact flex was absent — removed. Publish `@ 24a466ce` (`merge-tests(AST-1020): origin/tests 4c04e20f`).

###### radia — 2026-07-28T20:27:36.766Z (code-rubric.v1)
**Overall: DISCUSS** (procedural stragglers only). Stages 1–2 match: five color tokens + golden embedded CSS with cover/ATS/`.prose-block` appendages; `#prior-experience` print break always emitted; no emit/markup/title/meta scope creep into AST-1021. All in-scope statutes **conforms**. **discuss (straggler):** three Joan plan-time exclusions (`spikes-under-debug-dir`, `features-single-file-per-ticket`, `engineer-test-tree-ban`) in-scope on the three-dot diff — each **conforms**. No **fix-now**.

#### Resolution (2026-07-28)

Clean — no product code changes. Radia discuss (straggler) items acknowledged (Joan-excluded at plan time; **conforms** in substance). No **fix-now**.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/utils/config.py` | Add golden text/border color tokens under `BUILD_CONFIG["default_style"]["colors"]` | `6104b15b0` |
| ✓ | `src/core/builder.py` | Replace the resume-body CSS string inside `_emit_html_document` with the golden stylesheet (interpolating config tokens); keep Astral-only cover + ATS CSS appendages; always emit golden print `#prior-experience` rule | `89c3f44ce` |
| | _tests_ | golden stylesheet parity (three surfaces) + `BUILD_CONFIG` color tokens | `4c04e20fa` — `test_builder.py` / `test_config.py` + test-bible (Betty) |

### AST-1021 — Residual emit / chrome tweaks
_Archived: 2026-08-05 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1021/residual-emit-chrome-tweaks-take-2-resume-render-format-discrepancies · Status at archive: Archive · Project: Astral Artifacts · Assignee: ada · Priority / estimate: None / — · Blocked by / blocks / related: parent: AST-1019; blockedBy: AST-1020_

#### What this implements

Cosmetic emit adjustments the stylesheet cannot fix: document `<title>` → `{name} Resume` (no dashes); keep field-derived candidate-specific meta (do not force the golden HTML's example meta string); plus any `white-space` / class alignment leftovers vs golden body. Does not rework AST-993 structural contracts. After stylesheet sibling; skip or thin if UAT shows CSS-only is enough.

#### Acceptance criteria

Document `<title>` is `{candidate_name} Resume` (space, no em/en dashes); ATS `<meta name="description">` is candidate-specific from paste name/title/tagline via the AST-993 field-derived template (`Resume of <name>, <title>, specializing in <tagline>`), the literal example string in the desired HTML being structure-only; shared-builder parity; eye-verify no "close enough".

#### Boundaries

Does not own embedded stylesheet golden parity (sibling Katherine). Does not rewrite resume content. Does not force literal golden meta example string.

#### Current baseline (post–AST-1020 on ftr)

1. **Document `<title>` (must change):** `_emit_html_document` builds `html.escape(f"{render.get('candidate_name', '')} — Resume".strip() or "Resume")` — em dash between name and `Resume`; empty name also fails the `or "Resume"` fallback because `"— Resume"` is truthy after strip.
2. **Meta description (must keep):** when name/title/tagline are all non-empty, emit already uses `Resume of {name}, {title}, specializing in {tagline}` with `html.escape` and omit-on-partial. Do **not** replace with the golden example string.
3. **Stylesheet / structural emit:** golden CSS + class names already land via AST-1020 / AST-993. This ticket does not re-open those contracts.

#### Stage 1: Document `<title>` → `{name} Resume`

**Done when:** For any render dict (via the three public builders), the HTML `<title>` text is `{candidate_name} Resume` when `candidate_name` is non-empty after strip, and exactly `Resume` when name is empty/missing — with no em dash, en dash, or `SomersetResume`-style concatenation; value HTML-escaped.

Replace the current `title_esc = …` line (`f"{render.get('candidate_name', '')} — Resume".strip() or "Resume"`) with construction from the already-computed `name_raw`:
```python
title_esc = html.escape(f"{name_raw} Resume" if name_raw else "Resume")
```
Do **not** invent a camelCase title; do **not** put the title suffix into `BUILD_CONFIG`; do **not** change `<title>…</title>` placement in the head template.
⚠️ **Decision:** Keep the title string inline next to the existing meta template. Parent AC states the exact shape `{candidate_name} Resume`; `BUILD_CONFIG["default_style"]["type_scale"]["document_title"]` is CSS sizing metadata, not the HTML `<title>` text — do not overload it.

#### Stage 2: Meta description — lock field-derived template (no golden-literal force)

**Done when:** Meta emit still matches the AST-1010 / laundry-list item 2 contract: content `Resume of {name}, {title}, specializing in {tagline}` only when all three of `name_raw` / `title_raw` / `tagline_raw` are non-empty; otherwise no `<meta name="description">`; values from the paste/render fields; the golden HTML's example meta string is **never** hardcoded.

**Do not change** the existing `meta_tag` block, the omit-when-partial rule, escape order, or meta tag placement unless Stage 1's edit disturbed them. **Do not** assign the golden fixture's literal `content="Resume of Susan Somerset, Senior Technical Product Manager / Program Manager specializing in Cloud Platforms, Agile Delivery, SaaS, and Healthcare."`.
⚠️ **Decision:** Meta work is a **lock / no-force** pass, not a rewrite. AST-1010 already shipped the correct field-derived template; child AC exists to prevent Take 2 from "matching" the desired HTML by hardcoding its example meta. If the inspected baseline already matches, Stage 2 produces **no code diff** beyond Stage 1's title line.

#### Stage 3: Residual white-space / class emit leftovers (CSS cannot fix)

**Done when:** Against the shared `_emit_html_document` head + header chrome (only emit attributes CSS cannot supply), either (a) no residual gaps remain beyond Stage 1 title, or (b) any concrete leftover in the disposition table (`<title>` em-dash → fix in Stage 1; meta forced to golden example → forbidden Stage 2 lock; contact single-span → no change; header emit → untouched) is fixed in `builder.py` only. Any **new** residual not in the table → **stop**, comment on parent AST-1019, wait. As built: residual inventory produced no further edits.

**Self-Assessment:** `minor` — one-line product footprint (the `<title>` construction). Meta is a lock. Residual inventory found nothing else.

##### Comments

###### ada — 2026-07-29T02:12:14.384Z (plan)
Files Changed: `src/core/builder.py` only — fix `<title>` to `{name} Resume`; leave meta template field-derived; apply only concrete residual emit chrome fixes found in Stage 3 (if any).

###### joan — 2026-07-29T02:15:28.790Z (plan-rubric.v1)
**Overall: APPROVED.** Stage 1 title fix maps to AC5; Stage 2 meta lock to AC6; Stage 3/4 residual + three-surface verification. All in-scope statutes **conforms**. **acceptable:** Stage 2 is intentionally a no-diff lock when baseline already matches — correct adversarial guard against hardcoding the golden example meta string.

###### betty — 2026-07-29T02:20:46.773Z
QA manifest AST-1021: document title chrome + meta lock (`test_builder.py`). Publish `@ 517faa964` (`merge-tests(AST-1021): origin/tests bcb2d83a`).

###### radia — 2026-07-29T02:23:43.814Z (code-rubric.v1)
**Overall: DISCUSS** (procedural stragglers only). Stage 1: `<title>` is `{name_raw} Resume` / empty → `Resume`; em-dash + broken empty-name fallback gone. Stage 2–3: meta field-derived template unchanged (lock); residual inventory no further edits. Scope `minor` matches. All in-scope statutes **conforms**. No **fix-now**.

#### Resolution (2026-07-28)

Clean — Stage 1 title fix only; meta lock produced no diff; no residual chrome edits.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/core/builder.py` | Fix `_emit_html_document` document `<title>` to `{name} Resume`; leave meta template field-derived; apply only concrete residual emit chrome fixes found in Stage 3 (none found) | `712bd3246` |
| | _tests_ | document title chrome + meta lock | `bcb2d83aa` — `test_builder.py` + test-bible (Betty) |

### AST-1027 — UAT: `__` markers not 1:1 `&nbsp;` in HTML emit
_Archived: 2026-08-05 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1027/uat-markers-not-11-andnbsp-in-html-emit · Status at archive: Archive · Project: Astral Artifacts · Assignee: (fix-uat) · Priority / estimate: None / — · Blocked by / blocks / related: parent: AST-1019 · UAT bug_

#### What failed

Session Resume Paste → Open HTML emits skill / separator lines where `__` markers are not replaced 1:1 with `&nbsp;`. Input `Program & Delivery: Jira__•__Confluence__•__Linear__• Jira__Align__• …`; actual HTML `Jira&nbsp;• Confluence&nbsp;• Linear&nbsp;• Jira Align&nbsp;• …` — after each `•` a normal space remains; word-joins like `Jira__Align` become ordinary spaces instead of `&nbsp;`. Expected: every `__` → `&nbsp;` (1:1) — `Jira&nbsp;•&nbsp;Confluence&nbsp;•&nbsp;…` and `Jira&nbsp;Align`.

#### Root cause (plan-time)

Marker expand looks "incomplete" only because **parse destroyed the digraphs first** — the `craft_resume_base` prompt tells the model to replace `__` with space / `~~` with hyphen and demands "formatting codes stripped clean", so the shared builder expand (`_resume_site_markers`) has nothing left to expand. `_resume_site_markers` itself is correct.

#### Stage 1: Preserve `__` / `~~` in `craft_resume_base` cache_prompt

**Done when:** The repo `craft_resume_base` `cache_prompt` no longer tells the model to replace `__` with space or `~~` with hyphen; it explicitly requires those digraphs to be copied into section string values (and experience job string fields) when present in the resume/paste; the checklist no longer demands "formatting codes stripped clean" for `__`/`~~`; skills/contact/prior instructions do not force rewriting marked `•` separators into `|`. File is valid JSON; only the `craft_resume_base` entry's `cache_prompt` string changes.
⚠️ **Decision:** Prompt preserve + existing shared builder expand (not a builder rewrite). Parent epic forbids Manage Tasks *redesign*; this is a one-rule + checklist + separator-faithfulness patch on `craft_resume_base` only. Startup `apply_repo_admin_json_at_startup` publishes the JSON into DB — no new migration function.

#### Stage 2: Builder contract lock + three-surface proof (build verification)

**Done when:** With in-memory content that still contains `__` / `~~` (as after a correct parse), the three public builders produce HTML showing NBSP for every `__` and non-breaking hyphen for every `~~` on skills/contact/competencies-style strings. Confirm `_resume_site_markers` source is unchanged from pre-ticket tip.

##### Comments

Radia code-rubric **Overall: CLEAN** — prompt preserve only; `_resume_site_markers` untouched; Betty coverage for `craft_resume_base` marker preserve + UAT expand across three surfaces (`merge-tests(AST-1027): origin/tests b264fd61`).

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `data/admin/agent_task.json` | `craft_resume_base` `cache_prompt` — preserve `__`/`~~` digraphs; drop "strip formatting codes clean"; don't force `•`→`|` | `eedc91e48` |
| | _tests_ | marker preserve prompt + expand proof | `b264fd619` — `test_builder.py` / `test_candidate.py` + test-bible (Betty) |

### AST-1028 — UAT: keywords emit in resume body instead of meta
_Archived: 2026-08-05 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1028/uat-keywords-emit-in-resume-body-instead-of-meta · Status at archive: Archive · Project: Astral Artifacts · Assignee: (fix-uat) · Priority / estimate: None / — · Blocked by / blocks / related: parent: AST-1019 · UAT bug_

#### What failed

Keywords / specialty line rendered in the resume body header instead of only in ATS meta: `Susan Somerset&nbsp;• Fractional TPM — Program Delivery, Cross-Functional Alignment, Cloud SaaS, AI-Assisted Engineering`. Expected: header stays `Name • Title` (markers applied); candidate-specific keywords/tagline feed `meta name="description"` (field-derived template), not an extra visible header line.

#### Root cause (plan-time)

Parse is folding the specialty/keyword line into `candidate_title` rather than a separate `candidate_tagline` field. Builder header/meta contracts are already correct when the fields are separate.

#### Stage 1: Teach `craft_resume_base` to split title vs tagline

**Done when:** The repo `craft_resume_base` `cache_prompt` has an explicit `### candidate_tagline` segment between `candidate_title` and `candidate_contact_detail`; `candidate_title` instructions forbid folding specialty / keyword / "specializing in …" lines into the title; when the paste has a title line and a separate specialty/keyword line (parent fixture: line after title, before contact), those map to `candidate_title` and `candidate_tagline` respectively; file is valid JSON; only the `craft_resume_base` entry's `cache_prompt` string changes.
⚠️ **Decision:** Prompt-only split (not builder post-processing of mashed titles). Changing emit to guess "everything after — is tagline" would fight paste fidelity and AST-1010 tests. Parent epic forbids Manage Tasks *redesign*; surgical segment-instruction patch on `craft_resume_base` only.

#### Stage 2: Builder emit lock + three-surface proof (build verification)

**Done when:** With in-memory content where `candidate_title` is title-only and `candidate_tagline` holds the specialty line, the three public builders show `<h1>` with `Name • Title` only (no specialty text in header/main) and `<meta name="description">` matching `Resume of {name}, {title}, specializing in {tagline}`. Confirm `_emit_html_document` header/meta source is unchanged from pre-ticket tip.

##### Comments

Radia code-rubric **Overall: CLEAN** — prompt-only split; builder header/meta unchanged. Betty coverage for title/tagline split prompt + keywords-in-meta emit (`merge-tests(AST-1028): origin/tests 99df7288`).

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `data/admin/agent_task.json` | `craft_resume_base` `cache_prompt` — `### candidate_tagline` segment; forbid folding specialty/keyword lines into `candidate_title` | `d83b486bf` |
| | _tests_ | title/tagline split prompt + keywords-in-meta emit | `99df7288e` — `test_builder.py` / `test_candidate.py` + test-bible (Betty) |

### AST-1029 — UAT: competencies separators print as pipes
_Archived: 2026-08-05 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1029/uat-competencies-separators-print-as-pipes · Status at archive: Archive · Project: Astral Artifacts · Assignee: (fix-uat) · Priority / estimate: None / — · Blocked by / blocks / related: parent: AST-1019 · UAT bug_

#### What failed

Core Competencies list prints `|` separators instead of bullet characters: `<p class="competencies-list">AI-Assisted Delivery | Cross-Functional Execution | Risk and Dependency Management | …</p>`. Expected: `•` bullet separators (with nbsp where markers require), matching golden / fixture.

#### Root cause (plan-time)

Emit is already faithful; a soft "prefer" from AST-1027's prompt left a `|` default for enrichment/synthesis. Deterministic DOM fidelity for already-piped JSON would need a builder normalize.

#### Stage 1: Harden competencies / prior separator rules in `craft_resume_base`

**Done when:** The repo `craft_resume_base` `cache_prompt` requires Core Competencies (and Prior Experience when present) to use `•` item separators — never `|` — whether copying from paste or synthesizing/enriching; paste `__` / `~~` / marked `•` forms are still preserved (AST-1027); file is valid JSON; only the `craft_resume_base` entry's `cache_prompt` string changes.
⚠️ **Decision:** Prompt harden only (not a builder `|`→`•` rewrite, not CSS fake bullets). If UAT still shows pipes after deploy + re-parse, escalate rather than silently adding an emit rewrite mid-build. Startup applies repo JSON — no new migration.

#### Stage 2: Builder emit lock + three-surface proof (build verification)

**Done when:** With in-memory content whose `core_competencies` string already uses `•` separators, session / base / job-tailored HTML shows those bullets inside `.competencies-list` (escaped); builder does not introduce `|`. Negative note: in-memory content that still contains `|` will still render pipes (documents that parse harden is required).

##### Comments

Radia code-rubric **Overall: CLEAN** — prompt harden only; emit lock. Betty coverage for competencies `•` separators prompt + emit lock (`merge-tests(AST-1029): origin/tests 5fc85d9a`). Chuckles `[merge-child] blocked` on a forbidden `Merge remote-tracking branch` subject on the sub-branch — resolved by re-merging with a proper message.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `data/admin/agent_task.json` | `craft_resume_base` `cache_prompt` — Core Competencies / Prior Experience `•` separators, never `|` | `c24f2aabb` |
| | _tests_ | competencies `•` separators prompt + emit lock | `5fc85d9a1` — `test_builder.py` / `test_candidate.py` + test-bible (Betty) |

### AST-1030 — UAT: `<no bullet>` lead emitted as list item
_Archived: 2026-08-05 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1030/uat-no-bullet-lead-emitted-as-list-item · Status at archive: Archive · Project: Astral Artifacts · Assignee: (fix-uat) · Priority / estimate: None / — · Blocked by / blocks / related: parent: AST-1019 · UAT bug_

#### What failed

`<no bullet>` lead copy under a role is emitted as the first `<li>` inside `<ul>` instead of a `<p class="role-description">` lead paragraph (Somerset Consulting role — no preceding `.role-description`). Expected: `<no bullet>` lines render as `.role-description`; following true bullets remain `<li>`.

#### Root cause (plan-time)

The `<no bullet>` prefix is being stripped/lost at parse — `craft_resume_base` does not preserve it inside the job's `accomplishments` string, so AST-1008's already-correct `_split_role_accomplishments` sees no lead marker.

#### Stage 1: Preserve `<no bullet>` in `craft_resume_base` experience accomplishments

**Done when:** The repo `craft_resume_base` `cache_prompt` `### experience` section requires that when the resume/paste marks a role lead with `<no bullet>`, that exact prefix remains on the corresponding line(s) inside that job's `accomplishments` string (newline-separated from following bullets); ordinary bullet lines have no such prefix; file is valid JSON; only the `craft_resume_base` entry's `cache_prompt` string changes.
⚠️ **Decision:** Prompt preserve only (not builder heuristics that treat the first accomplishments line as a lead without the marker, not CSS first-`<li>` restyle). Inventing "first line is always lead" would mis-classify roles that have only bullets. Startup applies repo JSON — no new migration.

#### Stage 2: Builder emit lock + three-surface proof (build verification)

**Done when:** With in-memory experience job array whose Somerset-style `accomplishments` starts with `<no bullet>Solo practice…` then bullet lines, the three public builders show `.role-description` for the lead and `<li>` only for bullets; `<no bullet>` absent from HTML. Confirm builder split/emit source unchanged from pre-ticket tip.

##### Comments

Radia code-rubric **Overall: CLEAN** — prompt preserve only; `_split_role_accomplishments` untouched. Betty coverage for `<no bullet>` preserve + emit lock (`merge-tests(AST-1030): origin/tests 133c5cde`).

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `data/admin/agent_task.json` | `craft_resume_base` `cache_prompt` `### experience` — preserve `<no bullet>` prefix inside `accomplishments` | `f54d3519a` |
| | _tests_ | `<no bullet>` preserve + emit lock | `133c5cde2` — `test_builder.py` / `test_candidate.py` + test-bible (Betty) |

### AST-1035 — UAT: View Parsed JSON button on Session Resume Paste
_Archived: 2026-08-05 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1035/uat-view-parsed-json-button-on-session-resume-paste · Status at archive: Archive · Project: Astral Artifacts · Assignee: (fix-uat) · Priority / estimate: None / — · Blocked by / blocks / related: parent: AST-1019 · Susan confirmed in scope for AST-1019 (under-defined original spec)_

#### What failed

Session Resume Paste has Parse and Open HTML, but no way to inspect the parsed resume JSON between those steps. Susan cannot tell whether a remaining UAT gap is in the parse/JSON structure or in the HTML renderer. Expected: a **View Parsed JSON** control between Parse and Open HTML showing the current parsed resume JSON (post-Parse). Susan confirmed this debug affordance is in scope for AST-1019.

#### Stage 1: View Parsed JSON control + read-only display

**Done when:** On Session Resume Paste, after a successful Parse, a **View Parsed JSON** button sits between **Parse** and **Open HTML**; it is disabled when `lastParse` is null (and while parsing/opening); activating it shows a read-only pretty-printed JSON of the **exact** `lastParse` object (`resume_structure` + `base_resume`) that Open HTML would POST; closing returns to the page without clearing `lastParse` or changing paste text. No new API routes; no changes to parse/html backend handlers.
⚠️ **Decision:** Modal + `JSON.stringify(lastParse)` (not a new-tab blob and not an inline always-visible dump). Modal matches existing admin "view JSON" UX (`AdminManageCandidates`); showing `lastParse` guarantees identity with the Open HTML POST body without a second fetch. New-tab would work but adds popup-blocker noise next to Open HTML.

#### Stage 2: Compile check + manual smoke (build verification)

**Done when:** `npx tsc -b --noEmit` under `src/ui/frontend` passes; with mocked or live session, Parse success → View Parsed JSON enabled → modal shows both `resume_structure` and `base_resume` keys; Open HTML still posts the same object; before Parse, View Parsed JSON is disabled.

##### Comments

Radia code-rubric **Overall: CLEAN** — modal + `JSON.stringify(lastParse)`; no API/backend changes. Betty coverage for the View Parsed JSON modal on Session Resume Paste (`merge-tests(AST-1035): origin/tests 3538ee6e`).

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/ui/frontend/src/pages/AdminSessionResumePaste.tsx` | View Parsed JSON button between Parse and Open HTML; read-only modal of the `lastParse` object | `5f920814a` |
| | _tests_ | View Parsed JSON modal (§6c page test) | `3538ee6eb` — `test_AdminSessionResumePaste.test.tsx` + test-bible (Betty) |

### AST-1039 — UAT: Summary newlines collapse to spaces (Experience ok)
_Archived: 2026-08-05 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1039/uat-summary-newlines-collapse-to-spaces-experience-ok · Status at archive: Archive · Project: Astral Artifacts · Assignee: (fix-uat) · Priority / estimate: None / — · Blocked by / blocks / related: parent: AST-1019 · UAT bug_

#### What failed

In Session Resume Paste → Open HTML, `\n` correctly becomes new bullets/paragraphs in Experience, but in Professional Summary the same newlines become regular spaces — the summary collapses into a single paragraph instead of splitting into multiple `.summary-intro` `<p>` elements. Expected: summary newlines → separate `.summary-intro` paragraphs, consistent with Experience and the desired HTML's multi-paragraph summary.

#### Root cause (plan-time)

Asymmetric newline handling: Experience's bullet/paragraph splitter treats `\n` as a break, but the summary emit/join path collapses whitespace/newlines into a single string / single paragraph.

#### Stage 1: Summary paragraph split honors single `\n`

**Done when:** Given `professional_summary` text with single `\n` between paragraphs (no blank line), `_emit_body_sections_html` / session Open HTML emits **two or more** `<p class="summary-intro">` elements (one per non-empty line/paragraph chunk). Blank-line-separated input (`Para one\n\nPara two`) still emits multiple paragraphs (existing behavior preserved). Experience emit path and `_split_role_accomplishments` are untouched. No CSS or prompt edits.
⚠️ **Decision:** Builder emit fix only (reuse the cover-letter paragraph helper). Prompt-only "emit `\n\n`" is **not** sufficient — Session Resume Paste fixtures and model output commonly use single `\n`, and Experience already treats `\n` as structural; Summary must match that contract in HTML structure. Default to the helper's proven order (blank lines first, then `\n` fallback) so intentional multi-sentence paragraphs separated by `\n\n` stay intact.

#### Stage 2: Compile check (build verification)

**Done when:** `python3 -m py_compile src/core/builder.py` succeeds; feeding `build_session_base_resume` a structure-enabled summary `"First para\nSecond para"` → two `.summary-intro` tags; `"First\n\nSecond"` still two; Experience job array with `\n` accomplishments unchanged.

##### Comments

Radia code-rubric **Overall: CLEAN** — builder emit fix only; Experience path untouched. Betty coverage for summary single-`\n` → multiple `.summary-intro` (`merge-tests(AST-1039): origin/tests 98103cee`).

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/core/builder.py` | Summary emit — single `\n` between paragraphs → multiple `<p class="summary-intro">` (reuse cover-letter paragraph helper); Experience path untouched | `b76345ad0` |
| | _tests_ | summary single-`\n` → multiple `.summary-intro` | `98103cee6` — `test_builder.py` + test-bible (Betty) |
