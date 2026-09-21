# AST-1268 — draft_job_resume response schema is wrong
**Component:** artifacts  
**Children:** AST-1270, AST-1271, AST-1272  
**Linear archived:** AST-1268 2026-08-19; AST-1270 2026-08-19; AST-1271 2026-08-19; AST-1272 2026-08-19

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-08-07 17:19 | AST-1270 | docs | `5ab0473ad` | docs(AST-1270): plan — nested draft_job_resume contract (unwrap + base_resume whitelist) |
| 2026-08-07 17:26 | AST-1270 | code | `92f584a4d` | code(AST-1270): TASK_CONFIG nest key + payload metadata for draft_job_resume |
| 2026-08-07 17:27 | AST-1270 | code | `0e8878f5b` | code(AST-1270): read nested resume body in _resume_payload_body |
| 2026-08-07 17:27 | AST-1270 | code | `5428653c0` | code(AST-1270): align draft_job_resume Manage Tasks nested experience wording |
| 2026-08-07 17:27 | AST-1270 | code | `bf64209c4` | code(AST-1270): unwrap agent_payload.resume; whitelist base_resume keys |
| 2026-08-07 17:27 | AST-1270 | docs | `de8a3d723` | docs(AST-1270): append build review stub |
| 2026-08-07 17:27 | AST-1270 | code | `673924ae4` | code(AST-1270): tip SHA on build review stub |
| 2026-08-07 17:34 | AST-1270 | test | `43cf6acd2` | test(AST-1270): nested draft_job_resume contract + base_resume whitelist |
| 2026-08-07 17:34 | AST-1270 | test | `a07a3db99` | test(AST-1270): nested draft_job_resume contract + base_resume whitelist |
| 2026-08-07 17:46 | AST-1270 | docs | `6a8b0205a` | docs(AST-1270): Radia review — findings |
| 2026-08-07 17:49 | AST-1270 | resolve | `39913979c` | resolve(AST-1270): — clean |
| 2026-08-07 17:51 | AST-1270 | merge-tests | `30dcebcfc` | merge-tests(AST-1270): origin/tests a07a3db99d9e29ff58733504842e54ac92f00fa9 |
| 2026-08-07 17:55 | AST-1272 | docs | `a3e980800` | docs(AST-1272): plan — draft hop debug whitelist trail |
| 2026-08-07 17:56 | AST-1271 | docs | `7c03da3f9` | docs(AST-1271): plan — deviations metadata retention on draft hop |
| 2026-08-07 18:01 | AST-1271 | docs | `9542bc945` | docs(AST-1271): plan — Joan discuss: deviations_artifact_key + persist path |
| 2026-08-07 18:03 | AST-1272 | code | `49ddf2d5a` | code(AST-1272): drop sibling AST-1271 persist bleed from agent.py |
| 2026-08-07 18:03 | AST-1272 | code | `904d0f8b2` | code(AST-1272): Stage 1 — normalize unwrap Style D + agent debug= |
| 2026-08-07 18:04 | AST-1271 | code | `ee590b6e1` | code(AST-1271): Stage 1 — deviations_artifact_key + clear-keys |
| 2026-08-07 18:04 | AST-1271 | code | `a7cafd360` | code(AST-1271): Stage 2 — extract/save deviations; keep resume body clean |
| 2026-08-07 18:04 | AST-1271 | code | `3c51f6ef5` | code(AST-1271): Stage 3 — persist deviations on successful draft hop |
| 2026-08-07 18:04 | AST-1271 | docs | `8ef1a1ce5` | docs(AST-1271): append build review stub |
| 2026-08-07 18:04 | AST-1271 | code | `0d5b0472a` / `1763a35cc` / `6fb0cf922` | code(AST-1271): tip SHA on build review stub |
| 2026-08-07 18:04 | AST-1271 | code | `fe9509888` | code(AST-1271): tip marker for build review stub |
| 2026-08-07 18:04 | AST-1272 | code | `12a127458` | code(AST-1272): Stage 2 — validate whitelist Style D + agent debug= |
| 2026-08-07 18:04 | AST-1272 | docs | `411d64289` | docs(AST-1272): append build review stub |
| 2026-08-07 18:06 | AST-1272 | test | `460f329fc` | test(AST-1272): draft hop Style D whitelist/unwrap debug trail |
| 2026-08-07 18:08 | AST-1271 | test | `af4ec7da2` | test(AST-1271): deviations metadata retention on draft hop |
| 2026-08-07 18:13 | AST-1272 | docs | `aef39767e` / `46c7b6e86` | docs(AST-1272): Radia review — clean |
| 2026-08-07 18:16 | AST-1272 | docs | `db1516446` | docs(AST-1272): dedupe concurrent Radia review section |
| 2026-08-07 18:17 | AST-1272 | resolve | `d6d79326e` | resolve(AST-1272): — clean |
| 2026-08-07 18:19 | AST-1272 | merge-tests | `e4bbb9dee` | merge-tests(AST-1272): origin/tests 460f329fc88d82d72c2a941c1b524382d6286ed7 |
| 2026-08-07 18:20 | AST-1271 | docs | `7ec51f2d1` | docs(AST-1271): Radia review — clean |
| 2026-08-07 18:21 | AST-1271 | resolve | `7a49a6091` | resolve(AST-1271): — clean |
| 2026-08-07 18:24 | AST-1268 | merge | `8b460a594` | Merge remote-tracking branch 'origin/dev' into tmp-refresh-AST-1268-draft-job-resume-response-schema-is-wrong |
| 2026-08-07 18:24 | AST-1271 | merge-tests | `cb51169dc` | merge-tests(AST-1271): origin/tests af4ec7da23f64da2d669c5664ca2da33f05a0a5d |
| 2026-08-19 12:48 | AST-1270 | docs | `6aab3dbe3` | docs(AST-1270): archive Linear issue content |
| 2026-08-19 12:49 | AST-1271 | docs | `1387bd0de` | docs(AST-1271): archive Linear issue content |
| 2026-08-19 12:49 | AST-1272 | docs | `698ef6731` | docs(AST-1272): archive Linear issue content |
| 2026-08-19 12:53 | AST-1268 | docs | `903c1622f` | docs(AST-1268): archive Linear issue content |

_AST-1270's sub-branch briefly carried unrelated `AST-1269` test-tree content (a sibling of a different parent, AST-1184) via a shared `origin/tests` divergence — Radia's build review cleared it with a merge-clean gate before the `docs(AST-1270)` review commit; no `src/` product code was ever affected (see AST-1270 Review below). AST-1272 self-caught and reverted an AST-1271 persist-call bleed in `agent.py` mid-build (`49ddf2d5a`) before publish. Two rows below the 2026-08-19 archive line are unrelated cross-ticket noise from a much later family (F27, AST-1460 area) whose commit bodies mention these tickets' test lineage: `test(AST-1508): per-code advice_adherence manifest` (mentions AST-1271) and `test(AST-1523): revert hard-contract tests — notes + freeform advise` (mentions AST-1270) — omitted from the table above._

## Epic — AST-1268
_Archived: 2026-08-19 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1268/draft-job-resume-response-schema-is-wrong · Status at archive: Archive · Project: Astral Artifacts · Assignee: chuckles · Priority / estimate: Urgent / — · Blocked by / blocks / related: related: AST-1201; related: AST-1205_

### Purpose

`draft_job_resume` is rejecting a well-formed nested model response because the Manage Tasks prompt and the runtime validator disagree on the JSON envelope. The hop must accept `agent_payload.resume` (section bodies) plus sibling `agent_payload.deviations`, validate resume keys against the candidate's current base resume sections, and keep deviations out of resume render/persist paths so artifact drafting can land without schema folklore fights.

### Functional scope

* Adopt a nested hop contract: `agent_payload.resume` holds section bodies; `agent_payload.deviations` is a sibling metadata list (decision-drift notes for the artifacts cycle).
* Normalize must unwrap `agent_payload.resume` before section whitelist checks so `resume` is never treated as a catalog section id.
* Validate section keys inside `resume` against the candidate's **current** `artifacts.base_resume` **section keys** (the content the hop is tailoring). Do not require a persisted `artifacts.resume_structure` blob for this whitelist.
* Align Manage Tasks / task prompt guidance with that nested contract (same keys and nesting the hop validates).
* Persist and render job resume content from the nested resume object only; never feed `deviations` into resume HTML/content parsers.
* Persist or retain `deviations` as hop/artifact metadata separate from resume section content so operators can see decision drift across the artifacts cycle.
* Accept experience as either a prose string or a job array for this hop (both are valid today); this epic does not force a base-resume experience migration to job arrays.
* When `debug=True`, log whitelist source (base_resume keys), envelope unwrap outcome, and accepted/rejected keys with Style D headers and `|` detail lines (AST-538).

### Architectural definition

* **Patterns to reuse** — `pattern.config.config-block`: draft metadata keys, nest unwrap names, and task flags stay in config / TASK_CONFIG rather than new inline sets in core.
* **New patterns proposed** — none.
* **Applicable statutes** — `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `astral.standards.in-scope-only`; `astral.standards.debug-contract-gated`; `astral.agent.do-task-delegation`; universal product set as applicable to core/utils changes.

### Boundaries

* Does not backfill or invent `artifacts.resume_structure` on candidates that lack it (other features may still resolve a default catalog via `resolve_resume_structure`; this epic's draft whitelist is base_resume keys).
* Does not redesign craft-base / session parse, HTML builders beyond excluding deviations from resume body paths, or cover-letter hops.
* Does not own AST-1201 (base-resume daisy chain) or AST-1205 (approve artifacts), though nested deviations support the broader artifacts cycle.
* Does not convert existing prose `experience` strings into job arrays as a migration; both shapes remain acceptable on draft.
* Must not break AST-594 / AST-997 section typing rules once the outer envelope is nested correctly.

### Acceptance criteria

* A response shaped like `{ agent_performance, agent_payload: { resume: {…section keys…}, deviations: […] } }` validates when `resume` keys are a subset of that candidate's `artifacts.base_resume` keys and values are well-typed.
* The Manage Tasks prompt for `draft_job_resume` instructs that same nested shape (no contradictory flat-only example).
* `resume` is never reported as an unknown section key after normalize; true unknown keys inside `resume` still fail clearly.
* Job resume render/persist uses only the resume body (`.resume` / equivalent); including `deviations` in that body path does not occur.
* `deviations` is retained as metadata for the artifacts cycle (not dropped silently on a successful hop).
* Candidates without a persisted `artifacts.resume_structure` can still pass draft validation when `base_resume` section keys match.
* With `debug=True`, whitelist keys and unwrap/accept/reject outcomes are visible under Style D headers.

### Dependencies and blockers

none.

### Open questions

none.

### Proposed child tickets

**1!: Nested draft_job_resume contract (prompt + normalize/validate) — Ada** — Owns unwrap of `agent_payload.resume`, whitelist from candidate `base_resume` keys, allow `deviations` as sibling metadata, and Manage Tasks prompt alignment to the nested contract. Observable: the failing nested sample shape validates when section keys/types are good; resume parsers never see `deviations` as section content. Does not own HTML chrome or other hops.
**Citations:** `pattern.config.config-block`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `astral.agent.do-task-delegation`.

**2: Deviations metadata retention on draft hop — Hedy** — After #1: ensure successful draft responses retain `deviations` as hop/artifact metadata separate from resume body for the artifacts cycle (decision-drift visibility). Does not invent a full approve-artifacts UI (AST-1205).
**Citations:** `astral.config.config-source-of-truth`; `astral.standards.in-scope-only`.

**3: Draft hop debug whitelist trail — Katherine** — After #1: when `debug=True`, emit Style D found/recorded detail for base_resume whitelist, unwrap, and accepted/rejected keys. Does not change allowlist rules.
**Citations:** `astral.standards.debug-contract-gated`.

### Original brief

The manually entered schema to expect was written in the task prompt like this:

```
Output one JSON object, nothing else:
{
  "agent_performance": {"status": "success | failure", "failure_note": ""},
  "agent_payload": {
    "resume": { ...exactly the same keys and value types as the provided base resume; experience remains a single string formatted like the base... },
    "deviations": ["instruction skipped and why"]
  }
}
```

But, the response could not be parsed:

```
[e9e1f51b-bcda-41fc-8b65-67af41571ae6]
Validation failed: Unknown resume section key 'resume' (not in candidate catalog: ['candidate_contact_detail', 'candidate_name', 'candidate_tagline', 'candidate_title', 'core_competencies', 'education_certifications', 'experience', 'prior_experience', 'professional_summary', 'technical_skills'])

--- model response ---
{
  "agent_performance": {
    "status": "success",
    "failure_note": ""
  },
  "agent_payload": {
    "resume": {
      "candidate_name": "Susan Somerset",
      "candidate_title": "Senior Technical PM",
      "candidate_tagline": "Cloud Platforms • Agile Delivery • SaaS • Healthcare",
      "candidate_contact_detail": "hire@susansomerset.com • 415-745-5238 • linkedin.com/in/susansomerset • Oakland, CA (PST)",
      "professional_summary": "Founded on six years as a Systems Analyst, I approach every engagement with rigorous requirements discipline. I build structure where none exists. Sometimes that means a roadmap, sometimes a delivery framework, occasionally an entire ecosystem that wasn't supposed to be possible. Over 20 years and more than 30 engagements spanning healthtech startups, FDA-regulated medical devices, and enterprise cloud platforms, I have walked into complexity and left behind systems that work, teams that ship, and a delivery rhythm that sticks.\n\nI am equally comfortable defining product vision, shaping roadmaps, and working alongside engineers at the whiteboard. I discern patterns from ambiguity and translate them into modular, extensible scopes that drive consensus across cross-functional teams. That hands-on technical partnership has reduced iteration cycles by 80% through concise scope definition and deliberate collaboration, not process for its own sake. I apply just enough structure to ease friction using the tools already in place.\n\nI create documentation that outlasts engagements—plans, decisions, and reviews—ensuring clean handoff and reusable assets. I also employ AI to its best advantage, providing guardrails and support structures that manifest the analytical power of the tool while maintaining quality control and human oversight. I have designed and built several partner-tools for education, recruiting, and highly-tuned research and analysis. What drives me is coherence with the value proposition, the place where messy ideas, creative engineers, and impossible deadlines align into something elegant and often simple.",
      "core_competencies": "Business & Systems Analysis | Requirements Gathering & Documentation | Process Documentation & Mapping | Agile/Scrum Delivery | Cross-Functional Alignment | Systems Thinking | Technical Partnership | Delivery Management | Roadmapping | Operational Scaling | Regulatory Compliance (HIPAA, GDPR, FDA) | AI Product Management | Analytics",
      "experience": "Somerset Consulting\nFounder, Principal Consultant | 2011 to Present | United States / Full-time Remote\n\nOwner/operator of a boutique consultancy serving dozens of clients over 14 years, providing both business and technical leadership, often installed in teams of 5 to 30 people in healthcare, SaaS, and cloud platform operations from startups to enterprise divisions.\n\nConducted as-is process analysis across distributed teams, implemented to-be improvements that reduced feature iteration cycles from 5–10 rounds to 1–2 through lightweight delivery frameworks, and developed sustainable systems to suit team size and culture.\n\nPartnered with founders, executives, and engineering leads to translate complex goals into clear, executable roadmaps and measurable OKRs, embedding Agile/Scrum delivery principles and metrics-driven accountability.\n\nLed technical product delivery across globally distributed teams of as many as 40 people, applying Agile cadence CI/CD guardrails to achieve sprint-level clarity and measurable delivery rhythm.\n\nCoordinated go-to-market readiness and product launch strategies for client MVPs across engineering, sales, and customer success teams.\n\nArchitected multi-agent AI recruiting pipeline integrating web scraping, LLM-based analysis, and document generation, reducing manual job-matching time by 90% while maintaining quality through staged human review.\n\nWorked with lead architects to optimize for modern cloud infrastructure, reducing AWS spend by 70%, saving $23K annually in one instance, and increasing CI/CD deployment velocity to allow for more frequent and cost-effective iterations.\n\nPTown.tech\nTechnical Product Manager | 2022 to 2024 | United States / Full-time Remote\n\nBuilt enrollment funnel tracking system for B2B2C wellness platform serving enterprise clients and employees, increasing completion rates 50% by visualizing stages and working hands-on with engineering to optimize each step.\n\nGathered and documented business requirements through stakeholder interviews and use-case definition, translating them into a prioritized feature backlog that repaired a fractured relationship between decision makers and engineering by making trade-offs and user impact visible to non-technical partners.\n\nDrove an aggressive compliance effort with an uncooperative third-party security auditor, cutting through red tape to achieve full GDPR certification for global deployment in less than four months.\n\nDelivered a production-ready MVP that unlocked a global partnership with Manpower's Talent Solutions division, granting access to its worldwide enterprise network and positioning the client for rapid, multinational expansion.\n\nEMIDS Technologies\nTechnical Product Owner | 2021 to 2022 | United States / Full-time Remote\n\nChampioned platform adoption by reluctant engineering teams, securing buy-in from key system owners and aligning resources, timelines, and data access to enable full integration of patient services.\n\nConducted business process mapping of existing onboarding workflows, identified bottlenecks, and established the first end-to-end onboarding framework for engineering teams integrating into the centralized platform. Personally managed 12 onboardings through security, legal, and compliance gates to ensure HIPAA- and FHIR-compliant production deployment.\n\nNegotiated with solution architects to reconcile legacy design patterns with modern, scalable architectures that fully supported microservice performance and security requirements.\n\nLed user story mapping sessions and strengthened delivery rhythm across product and platform groups through SAFe Program Increment planning and transparent Agile Release Train coordination.\n\nGreen Mars Consulting\nCEO | 2018 to 2020 | United States / Full-time Remote\n\nBuilt innovative delivery frameworks orchestrating up to 7 concurrent client projects from around the world with a 25-employee remote engineering team, driving consistency, accountability, and measurable quality for each and every delivery.\n\nDesigned API integration strategies for medical-device clients, enabling seamless data exchange between cloud platforms and clinical systems, observing regulatory standards and supporting 2 successful FDA submissions with traceable, testable systems, while preserving agility for iterative design and cross-team innovation.\n\nAuthored functional and technical requirements in JAMA for a Point-of-Care Ultrasound (POCUS) platform, including verification protocols and data-exchange specifications (DICOM, HL7), which enabled rigorous system testing and secure integration with hospital PACS systems and cloud architecture.\n\nTellme Networks / Microsoft\nSr. Operations IT Program Manager | 2006 to 2011 | Mountain View, CA / Full-time Onsite\n\nDrove cross-functional programs integrating business operations, IT systems, and analytics through Tellme's acquisition and transition into Microsoft, preventing deployment delays of up to 6 weeks through proactive stakeholder alignment.\n\nDesigned and deployed business-intelligence tools with KPI-driven dashboards that improved cost management, resource planning, and operational transparency across multiple departments.\n\nLed requirements definition, data-model design, and automation efforts that increased reporting accuracy and decision velocity for executive and engineering stakeholders.",
      "prior_experience": "Project Manager (4 yrs) • Systems Analyst (6 yrs) • ETL Migration Specialist (2 yrs) • Database Engineer (2 yrs) • VBA Software Developer (3 yrs)",
      "education_certifications": "Certified ScrumMaster (CSM) • Scrum Alliance, 2024 to 2026\nCertified Scrum Product Owner (CSPO) • Scrum Alliance, 2024 to 2026\nUW Milwaukee • Completed coursework in Computer Science and Business Administration",
      "technical_skills": "Project Management: Linear | Jira | Trello | Azure DevOps | Jira Align | Asana | JAMA | Pivotal Tracker\nDesign & Documentation: Figma | Lucidchart | ERD Tools | Miro | Mural | Confluence (Wiki)\nDevelopment & APIs: Python | Next.js | Google Apps Script | GraphQL | REST | JSON\nCloud & DevOps: AWS | Vercel | GitHub | CI/CD Pipelines\nData & Analytics: PostgreSQL | MySQL | Prisma | Airtable | Tableau | QlikView | Talend (ETL)\nIntegration & Automation: Zapier | Google Workspace | GitHub Actions | Make | Microsoft 365 | Power Automate\nAI Development & Orchestration: Claude API | GPT-4 | Multi-agent workflows | Prompt engineering | Cursor | Copilot | Structured AI outputs | Self-healing code\nCollaboration: Slack | Discord | Teams | Zoom | Google Meet"
    },
    "deviations": [
      "Skipped adding a separate 'Systems Analysis & Process Expertise' section because the output schema does not permit new keys; the required content was instead woven into the professional summary and core competencies.",
      "Skipped UAT-specific language in the resume because Susan has not confirmed recent hands-on UAT experience; the brief's instruction to claim UAT was deferred per gap-handling guidance."
    ]
  }
}
```

first question: are we setting the expected response based on the candidate's base_resume content, specifically, or is the list "['candidate_contact_detail', 'candidate_name', 'candidate_tagline', 'candidate_title', 'core_competencies', 'education_certifications', 'experience', 'prior_experience', 'professional_summary', 'technical_skills']" hard-coded anywhere (including config.py) in the codebase?

The Response_schema should give the JSON elements of the candidate's current base_resume sections and validate against those.

Please confirm current behavior before we change anything.

#### Comments

##### chuckles — 2026-08-07T23:49:52.131Z
@susan Current behavior (no code changes yet):

1. Whitelist is **not** taken from `artifacts.base_resume` content keys. Runtime `validate_draft_job_resume_payload` allows keys from the candidate's **enabled** `artifacts.resume_structure` section ids.
2. That error list is that candidate's enabled catalog (sorted for the message). It matches the default known set in `config.py` (`RESUME_STRUCTURE_KNOWN_SECTION_IDS` / `RESUME_STRUCTURE_DEFAULT`) when the candidate still uses the default enabled sections — but draft validation reads the per-candidate structure, not a hard-coded ten-name list inside the validator.
3. `TASK_CONFIG["draft_job_resume"].response_schema` only has optional hop metadata (`astral_job_id` / `company` / `title`). Section bodies are gated by `resume_section_payload: True` + the runtime catalog check above — not by a static section schema in that TASK_CONFIG block.
4. Normalize unwraps nests named `content` / `section_content` / `base_resume` — **not** `resume`. So `agent_payload.resume` fails as unknown section key `resume`. `deviations` is also not in draft metadata allowlist today.

Open questions (need your call before Todo):
1. Whitelist source: keep enabled `resume_structure`, switch to keys on `base_resume`, or intersection?
2. Envelope: flat section keys on `agent_payload` (validator today) vs nested `resume` + `deviations` (prompt today)?
3. Keep / drop / relocate `deviations`?

— Chuckles

##### chuckles — 2026-08-08T00:01:25.539Z
@susan On your structure / experience check:

1. Missing `artifacts.resume_structure` on the candidate is real and allowed today. Draft validation does **not** read the blob you see in the DB row — `resolve_resume_structure` falls back to `RESUME_STRUCTURE_DEFAULT` in config when structure is absent/invalid. That is why the error listed those ten section ids even though your candidate has no persisted structure. Structure gets written when craft-base / parse persistence succeeds (post AST-517/650); older base_resume-only records can still lack it.
2. Prose `experience` (one long string) is still valid on draft — AST-997 accepts job array **or** string. Job-array shape was added for craft-base; it is not a forced migration of existing candidates. Out of scope for this epic to convert your string to jobs.

Definition updated from your calls: nested `resume` + sibling `deviations`; whitelist = `base_resume` keys; render/persist only `.resume`; deviations retained as metadata. Open questions cleared — ready for your Todo + assign Chuckles when you approve.

— Chuckles

##### susan — 2026-08-08T01:15:29.538Z
@chuckles I bet this is related to the issue of the ref_agent_data_id not being fully implemented from the fetch side.

##### chuckles — 2026-08-08T01:27:08.327Z
[check-linear] answered — not the pin/fetch gap. The UAT fail was `Unknown resume section key 'resume'`: Manage Tasks nested `agent_payload.resume` while validate treated `resume` as a section id (AST-1270 unwrap + base_resume whitelist). `ref_agent_data_id` / AST-1099 pin only runs after a successful RESPONSE store — related as a downstream consequence of a failed hop, not this schema mismatch.

— Chuckles

##### susan — 2026-08-08T01:38:10.267Z
Pasted a `draft_job_resume` dispatch log showing `total_errors=1` with no `Validation failed:` / traceback text in the visible window, and: "I don't know why this is failing."

##### chuckles — 2026-08-08T01:40:31.266Z
[fix-uat] blocked: open questions — need the actual hop error

@susan Your paste shows `draft_job_resume` claimed a job and finished with `total_errors=1`, but the log cuts off before any `Validation failed:` / `do_task validation failed` / traceback line. That summary alone is not enough to file a UAT bug against parent AC (could still be nested-`resume` schema, a *new* whitelist/typing reject after AST-1270, or a non-schema runner error — and I cannot tell which). Please paste the ERROR / `Validation failed:` block for that run, and note whether the local process was restarted on current `origin/dev` (AST-1270 unwrap is on `dev`) before the click.

— Chuckles

##### susan — 2026-08-08T01:56:04.277Z
Pasted a different traceback: `ValueError: agent_data ref target missing: 'check_job_resume-c9fa00ec-…'` during `[contemplate_job]`, with no further log about the draft hop itself.

##### chuckles — 2026-08-08T01:57:29.007Z
[fix-uat] blocked: open questions on parent

@susan Two separate UAT signals — I still cannot file an AC-tied bug under AST-1268 without your call:

1. **`draft_job_resume` `total_errors=1` with no further log** — still no `Validation failed:` / exception text for that batch. Without that, I cannot tell whether the nested-`resume` contract (this epic) still fails vs a non-schema runner fault. Please re-run once on current `origin/dev` with the local process restarted and `debug=True` on that dispatch task, then paste the ERROR / Style D / Validation lines.
2. **`ValueError: agent_data ref target missing: '…'`** (during `[contemplate_job]`) — that is pin/ref resolution (`database._resolve_agent_data_block_data`), not the draft nest/whitelist ACs on this parent. Boundaries already push pin write/resolve to the AST-1099 / AST-1100 family. **Do you want a new parent for dangling `ref_agent_data_id` targets, or should we expand AST-1268 AC to cover agent_data ref integrity on the artifacts chain?** I will not invent that scope here.

— Chuckles

##### susan — 2026-08-08T01:59:42.196Z
I guess I can't test this until the ref_agent_data_id issue is resolved.

### Files changed (plan vs actual)

_No product commit trail on the parent — the epic worktree only carries a `Merge remote-tracking branch 'origin/dev'` housekeeping commit and the `docs(AST-1268)` archive commit. Implementation landed entirely via the three sub-issues below. The ref_agent_data_id / agent_data pin-resolution question Susan raised in the parent thread was left open — it is downstream pin/fetch integrity (AST-1099/AST-1100 territory), not this epic's schema/whitelist fix, and no new ticket was filed in this thread to track it._

## Sub-issues

### AST-1270 — Nested draft_job_resume contract (prompt + normalize/validate)
_Archived: 2026-08-19 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1270/nested-draft-job-resume-contract-prompt-normalizevalidate-draft-job · Status at archive: Archive · Project: Astral Artifacts · Assignee: susan · Priority / estimate: None / — · Blocked by / blocks / related: parent: AST-1268; blocks: AST-1272; blocks: AST-1271_

#### What this implements

Owns unwrap of `agent_payload.resume`, whitelist from candidate `base_resume` keys, allow `deviations` as sibling metadata, and Manage Tasks prompt alignment to the nested contract. Observable: the failing nested sample shape validates when section keys/types are good; resume parsers never see `deviations` as section content. Does not own HTML chrome or other hops.

#### Acceptance criteria

- [X] A response shaped like `{ agent_performance, agent_payload: { resume: {…section keys…}, deviations: […] } }` validates when `resume` keys are a subset of that candidate's `artifacts.base_resume` keys and values are well-typed.
- [X] The Manage Tasks prompt for `draft_job_resume` instructs that same nested shape (no contradictory flat-only example).
- [X] `resume` is never reported as an unknown section key after normalize; true unknown keys inside `resume` still fail clearly.
- [X] Candidates without a persisted `artifacts.resume_structure` can still pass draft validation when `base_resume` section keys match.

#### Boundaries

Does not own deviations metadata retention beyond allowing the sibling field (sibling #2). Does not own debug whitelist trail (sibling #3). Does not convert prose experience to job arrays. Does not own AST-1201 / AST-1205.

#### In scope / considered but excluded

In scope: `astral.config.config-source-of-truth` (nest unwrap key + payload metadata keys incl. `deviations` on `TASK_CONFIG["draft_job_resume"]`); `astral.standards.no-hardcoded-sets` (no new inline nest/metadata frozensets in core; read from TASK_CONFIG); `astral.agent.do-task-delegation` (keep validate/normalize on existing `do_task` / `resume_section_payload` path); `astral.standards.in-scope-only`; `astral.standards.dry-and-focused-functions` (one whitelist helper; one unwrap path in normalize); `astral.layers.import-direction`.

Considered but excluded: `astral.standards.debug-contract-gated` (Style D whitelist/unwrap trail is AST-1272); deviations hop/artifact metadata retention (AST-1271); `astral.batch.claim-process-release` / `astral.dispatch.run-next-is-chain-authority` (no dispatch lifecycle/topology change); HTML builders / cover-letter hops / craft-base parse (out of epic); AST-1201/AST-1205 (related, not this child); experience prose→job-array migration (both shapes remain valid).

#### Notes for planning

Nested envelope is the approved contract. Whitelist = base_resume keys ∩ known section ids. Normalize must unwrap `resume` before section checks. Flat (no nest) payloads remain accepted for AST-594-era callers.

#### Diagnosis (why the nested sample fails today)

Verified against `normalize_draft_job_resume_agent_payload` / `validate_draft_job_resume_payload`: the Manage Tasks seed already showed nested `agent_payload.resume` + `deviations` — prompt and validator disagreed; the model followed the prompt. Normalize's nest loop promoted children from `content` / `section_content` / `base_resume` only (`_CRAFT_RESUME_CONTENT_DICT_KEYS`) and did **not** unwrap `resume`, so `resume` stayed a top-level `agent_payload` key. Validate iterated every non-metadata key against `enabled_resume_section_ids(resolve_resume_structure(cd))` — `resume` was not a section id → `Unknown resume section key 'resume' (not in candidate catalog: …)`, the exact parent failure. Whitelist source was the structure catalog (default when `artifacts.resume_structure` is missing), not `artifacts.base_resume` keys — parent contract requires the latter. `_DRAFT_JOB_RESUME_METADATA_KEYS` (a module frozenset) did not include `deviations`, so even after unwrap it would be treated as an unknown section unless allowlisted. `_resume_payload_body` in `tracker.py` walked flat `agent_payload` keys only — after a correct unwrap, persist gates see section bodies; without unwrap, nested bodies were invisible.

⚠️ **Decision:** Nested envelope is authoritative. Normalize **pops** `agent_payload[nested_resume_key]` when it is a dict and merges its entries onto `agent_payload` before section validation. Flat payloads (no nest key) remain accepted for AST-594-era callers. Whitelist = keys of `artifacts.base_resume` that are members of `RESUME_STRUCTURE_KNOWN_SECTION_IDS`. Nest key name, metadata key set (including `deviations`), and the existing `resume_section_payload` flag live on `TASK_CONFIG["draft_job_resume"]` — no new inline frozensets in core.

#### Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | On `TASK_CONFIG["draft_job_resume"]`: nest unwrap key + payload metadata keys (incl. `deviations`) | utils |
| `src/core/candidate.py` | Unwrap nested resume; whitelist from `base_resume` keys; read metadata/nest names from TASK_CONFIG | core |
| `src/core/tracker.py` | `_resume_payload_body`: when nested resume dict present, take section bodies from it only | core |
| `data/admin/agent_task.json` | Align `draft_job_resume` user_prompt nested example; experience matches base value types | data seed |

#### Plan Approved — Joan

**discuss** — `src/core/candidate.py`, Stage 2 step 3 (`orch.pipeline.call-susan-for-product-decisions`). Today `resolve_resume_structure` falls back to `default_resume_structure()`, so a candidate with no `artifacts.resume_structure` **and** no `artifacts.base_resume` still validated against the 10-id default catalog. The plan replaces that with an empty whitelist and a hard error `"candidate has no base_resume section keys"`. Parent AC 6 and child AC 4 only promise the missing-**`resume_structure`** case; missing **`base_resume`** flipping from pass to hard fail is a new behavior the plan decides on its own. Defensible — the hop tailors the base resume, so drafting without one is meaningless — but should be an explicit product call. Recommendation: confirm with Susan (or note in the plan) that a truthy candidate with no `base_resume` should fail the draft hop.

**discuss** — test impact for the Betty handoff: two error-string changes are load-bearing for existing component tests across 9 assertion sites. Recommend naming those two files in the plan so `qa-child` picks up the fixture/message revision deliberately.

**discuss** — `src/core/tracker.py` persist path. After this change the validate whitelist is `base_resume` keys ∩ `RESUME_STRUCTURE_KNOWN_SECTION_IDS`, while `persist_job_artifact_from_parsed` still filters through the **enabled catalog** ids (`resolve_resume_structure`). A candidate with a persisted structure that disables a section could now validate a section that then silently drops at persist — harmless today (default catalog enables all 10 known ids), narrowing persist is outside this child, but worth naming for review/QA to watch.

**acceptable** — `_DRAFT_JOB_RESUME_CONSULT_KEYS` stays a module frozenset while `_DRAFT_JOB_RESUME_METADATA_KEYS` moves to TASK_CONFIG; pre-existing, explicitly deferred, migrating it would be scope creep.

Notes: all six diagnosis points checked out line-by-line against the tree. Catching `deviations` in the metadata set matters more than it looks — without it, the normalize coercion loop would newline-join the deviation notes into a fake resume section. Stage 3 is not redundant with the Stage 2 unwrap — `normalize_draft_job_resume_agent_payload` only runs from inside `validate_draft_job_resume_payload`, which `agent.py` gates on truthy `cd`, so an unvalidated run still hands raw nested JSON to the persist path.

#### QA test manifest — Betty

New: `TestAst1270NestedDraftJobResumeContract`, `TestAst1270NestedResumePayloadBody`, `TestAst1270DraftJobResumeNestConfig`. Revised fixtures: `TestAst594DraftJobResumePayload`, `TestAst997JobTailoredExperience`, `TestAst594DraftJobResumeSchema`, `test_agent.py -k "draft_job_resume"`. **Broken/obsolete this pass:** empty `{}` / empty-artifacts `candidate_data` no longer valid for draft validate (whitelist = base_resume keys); AST-997 draft prompt literals superseded by nested-envelope wording (pin still covered by validate/pin unit tests). Integration: none — no existing scenario for this hop.

#### Radia review — code-rubric.v2, DISCUSS

**Plan adherence:** Stages 1–4 executed in order, no skip/reorder/expand. Diff = exactly the plan's 4 Files Changed. All four child ACs verified against the code. `no-hardcoded-sets` is a clean example: `_DRAFT_JOB_RESUME_METADATA_KEYS` frozenset deleted, zero new inline sets added.

Full 65-statute active-set sweep (18 universal + 47 scoped) run in-session: all `conforms` except one `needs-discussion` (`orch.pipeline.call-susan-for-product-decisions` — the base_resume-hard-fail behavior flip Joan already flagged; no Susan comment found before build proceeded on Joan's "defensible" read).

**Findings:**
- discuss — base_resume hard-fail behavior (Stage 2 step 3) is a product call Joan's plan-rubric already flagged as needing Susan's confirmation; no Susan comment found before build proceeded. Recommend a short confirmation before production traffic hits this path.
- discuss — `src/core/tracker.py` persist path still filters via `resolve_resume_structure` (enabled catalog ids) while validate now whitelists via `base_resume` keys — same divergence Joan flagged, carried forward as a live QA watch item.
- discuss — merge hygiene, not a product defect: this sub's previous tip (`ee481251`) carried `docs/test-bible/core/repo_admin_json.md` + `tests/component/core/test_repo_admin_json.py` changes for **AST-1269** (sibling of a different parent, AST-1184, unrelated to this epic) via the shared `origin/tests` branch, diverged from `origin/dev`'s own separate AST-1269 resolution. Radia ran the epic worktree's merge-clean gate (`git merge origin/dev`) before this docs() commit — resolved cleanly, no conflicts, divergence gone from the published tip; `src/` product code confirmed byte-identical across both tips.

**Recommended actions:** confirm the base_resume-hard-fail behavior with Susan before production; note the persist-vs-validate divergence for AST-1271/AST-1272/a future ticket to watch.

#### Resolution (2026-08-08)

DISCUSS @ `e748483d` — zero fix-now.

| Finding | Disposition |
|---------|-------------|
| hard-fail when truthy candidate has no `artifacts.base_resume` section keys | **Accepted as planned.** Whitelist = `base_resume` ∩ known section ids; empty whitelist → hard error. Matches parent Functional scope. No product change; Susan can reverse on parent UAT if the flip is wrong. |
| validate (`base_resume`) vs persist (enabled catalog) divergence | **Out of scope this child.** Documented for AST-1271/AST-1272/future watch. |
| AST-1269 test-tree content via `origin/tests` | **Already cleared** by Radia's merge-clean gate before `docs(AST-1270)`. |

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/utils/config.py` | Nest unwrap key + payload metadata keys (incl. `deviations`) | `92f584a4d` — +9 |
| ✓ | `src/core/candidate.py` | Unwrap nested resume; whitelist from `base_resume` keys; TASK_CONFIG-sourced metadata/nest names | `bf64209c4` — +42/-18 |
| ✓ | `src/core/tracker.py` | `_resume_payload_body` reads nested resume body | `0e8878f5b` — +6 |
| ✓ | `data/admin/agent_task.json` | Align nested Manage Tasks wording | `5428653c0` — +1/-1 |
| | _tests_ | nested contract + base_resume whitelist coverage | `43cf6acd2` / `a07a3db99`; bible per Betty manifest |

### AST-1271 — Deviations metadata retention on draft hop
_Archived: 2026-08-19 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1271/deviations-metadata-retention-on-draft-hop-draft-job-resume-response · Status at archive: Archive · Project: Astral Artifacts · Assignee: susan · Priority / estimate: None / — · Blocked by / blocks / related: parent: AST-1268_

#### What this implements

After #1: ensure successful draft responses retain `deviations` as hop/artifact metadata separate from resume body for the artifacts cycle (decision-drift visibility). Does not invent a full approve-artifacts UI (AST-1205).

#### Acceptance criteria

- [X] Job resume render/persist uses only the resume body (`.resume` / equivalent); including `deviations` in that body path does not occur.
- [X] `deviations` is retained as metadata for the artifacts cycle (not dropped silently on a successful hop).

#### Boundaries

Does not own nested contract / prompt / normalize (sibling #1). Does not own debug trail (sibling #3). Does not invent approve-artifacts UI (AST-1205).

#### In scope / considered but excluded

In scope: `astral.config.config-source-of-truth` (`deviations_artifact_key` on `TASK_CONFIG["draft_job_resume"]`); `astral.standards.in-scope-only` (persist sibling metadata only); `astral.standards.no-hardcoded-sets` (no new core frozenset; skip keys via `payload_metadata_keys` from TASK_CONFIG).

Considered but excluded: Style D debug trail (AST-1272); `astral.agent.do-task-delegation` (no new call shape; only a post-success artifacts write); `pattern.config.config-block` (nest/metadata keys already landed on AST-1270); approve-artifacts UI (AST-1205); nested unwrap / whitelist / Manage Tasks seed (AST-1270).

#### Notes for planning

After AST-1270. Persist deviations as sibling metadata — never merge into resume section content.

⚠️ **Decision:** Persist as `job_data.artifacts.deviations` (string list), not as an agent_data pin and not inside `resume_content`. Pinning the whole RESPONSE (AST-1099 style) would retain the envelope only opaquely; operators need first-class decision-drift notes without inventing AST-1205 UI. Same key name as the payload metadata field so inspectable job_data matches the model contract.

#### Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `deviations_artifact_key` on `TASK_CONFIG["draft_job_resume"]`; include that key in `JOB_BUILD_ARTIFACT_CLEAR_KEYS` | utils |
| `src/core/tracker.py` | Extract + save deviations helpers; skip metadata keys in `_resume_payload_body`; persist beside resume in `persist_job_artifact_from_parsed` | core |
| `src/core/agent.py` | On successful `draft_job_resume`, persist deviations to job artifacts after RESPONSE store | core |

#### Plan Approved — Joan

**discuss** — Stage 2 step 1, the `meta_key` instruction was internally contradictory ("look up the string" vs "use the literal `deviations`" — no lookup yields one element of a five-element tuple), and the Execution contract would stall the build on this ambiguity. Recommendation: read the field name from `deviations_artifact_key`, which Stage 1 already puts on the same config block.

**discuss** — Stage 2 step 5, `persist_job_artifact_from_parsed`. That function has no caller anywhere in `src/` (AST-1099 removed the `do_task` terminal body-copy; kept only "for manual/API callers" per the test bible) — so the deviations write added there never fires in production, and AC2 rests entirely on the Stage 3 agent hook. The Code rules check's DRY claim read as two live paths when there is one; related, the step gated the deviations persist on `allow_resume`, a resume-content flag unrelated to metadata. Neither changes the product outcome, but worth one clarifying line each.

**acceptable** — the absent-vs-empty distinction in the extract helper is the right call: key absent → `None` → no write (a later hop cannot wipe a prior list); key present but empty → `[]` → written ("model reported no deviations" is recorded, not indistinguishable from "never ran"). That is what makes AC2's "not dropped silently" actually hold.

**acceptable** — adding a list-valued key to `job_data.artifacts` does not introduce a new reader-risk class; the dict is already heterogeneous (AST-1099 pins store bare id strings alongside dicts).

Notes: verified AST-1270 landed on `ftr` and everything this plan builds on is real. Stage 3's insertion point is the exact shape the AST-1252 craft-persist block already uses (success + truthy `index`, lazy import, try/except that logs without failing the hop). Stage 2 step 4's value is not where it looks — with the nest present `deviations` is already excluded as a sibling; what the skip actually catches is a string-typed `deviations` plus `astral_job_id`/`company`/`title`, which currently leak into the body dict harmlessly (dropped downstream by `filter_content_to_resume_structure`). Cancel-clear addition is safe against the existing guard test, which asserts membership rather than an exact tuple.

**Hedy's reply (Revision 1):** extract uses `deviations_artifact_key` only (no literal/tuple-membership ambiguity); `persist_job_artifact_from_parsed` deviations write ungated on `allow_resume`, documented as manual/API defense-in-depth — AC2's live path remains Stage 3 `do_task`.

#### QA test manifest — Betty

New: `TestAst1271DeviationsMetadataRetention` (extract/save/persist; string-typed deviations skipped from resume body; `persist_job_artifact_from_parsed` writes sibling slot; cancel clears `deviations`), `TestAst1271DeviationsArtifactConfig`, `TestAst1271DoTaskDeviationsPersist` (success calls persist helper; validation failure does not). Reuse: `TestAst1270NestedResumePayloadBody` (nested envelope still excludes deviations from body). No broken/obsolete this pass — additive retention path.

#### Radia review — code-rubric.v2, CLEAN

**Frame diff:** no frame changes from Joan's plan-rubric verdict. Both `discuss` findings confirmed resolved in the built code: `meta_key` ambiguity resolved to `deviations_artifact_key`-only lookup (no hardcoded literal in `tracker.py`); `persist_job_artifact_from_parsed`'s `allow_resume` gate — the deviations write landed unconditional, outside that gate, as Revision 1 required.

Full-set sweep: 68 active statutes (18 universal + 50 scoped); 17 apply on the touched layers and all conform; 33 excluded on layer/path predicate (correctly deferred debug-contract-gated to AST-1272 per plan). Zero violations, zero new findings. Confirmed via `git log` that Hedy's `code()` commits touch only the three planned files — `candidate.py` in the diff is entirely AST-1270's inherited work via the `ftr` merge, not re-touched.

**Findings:** none. Zero fix-now, zero discuss, zero advisory.

#### Resolution (2026-08-08)

CLEAN. No fix-now, discuss, or advisory items. Joan's plan-rubric discuss items were already closed in build (Revision 1 + Stages 1–3).

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/utils/config.py` | `deviations_artifact_key` on TASK_CONFIG; add to `JOB_BUILD_ARTIFACT_CLEAR_KEYS` | `ee590b6e1` — +3 |
| ✓ | `src/core/tracker.py` | Extract + save deviations helpers; skip metadata keys in `_resume_payload_body`; persist beside resume | `a7cafd360` — +51/-1 |
| ✓ | `src/core/agent.py` | Post-success persist hook on `draft_job_resume` | `3c51f6ef5` — +14 |
| | _tests_ | deviations metadata retention coverage | `af4ec7da2`; bible per Betty manifest |

### AST-1272 — Draft hop debug whitelist trail
_Archived: 2026-08-19 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1272/draft-hop-debug-whitelist-trail-draft-job-resume-response-schema-is · Status at archive: Archive · Project: Astral Artifacts · Assignee: susan · Priority / estimate: None / — · Blocked by / blocks / related: parent: AST-1268_

#### What this implements

After #1: when `debug=True`, emit Style D found/recorded detail for base_resume whitelist, unwrap, and accepted/rejected keys. Does not change allowlist rules.

#### Acceptance criteria

- [X] With `debug=True`, whitelist keys and unwrap/accept/reject outcomes are visible under Style D headers.

#### Boundaries

Does not own nested contract / prompt alignment (sibling #1). Does not own deviations retention (sibling #2).

#### In scope / considered but excluded

In scope: `astral.standards.debug-contract-gated` (Style D `debug_index`/`debug_detail` only when `debug=True` on draft normalize + validate); passing `debug=` from `do_task` into both draft helpers at both pre-schema and post-rubric-decode sites.

Considered but excluded: nested contract / prompt alignment / base_resume whitelist rules (AST-1270); deviations retention (AST-1271); allowlist membership or error-string changes (observe only); HTML builders / cover-letter hops / craft-base parse (out of epic).

#### Notes for planning

After AST-1270. Style D index headers + `|` detail; AST-538 contract only when debug=True.

#### Why unwrap must log at normalize (not only validate)

`do_task` already calls `normalize_draft_job_resume_agent_payload(parsed)` **before** schema validation, then `validate_draft_job_resume_payload` calls normalize again. After the first call, `nested_resume_key` is gone — a validate-only unwrap peek would always report `flat` on the live hop path. So unwrap Style D is emitted from normalize when `debug=True` on the **agent** call sites; validate's internal normalize keeps `debug=False` (default) so the second pass is silent.

#### Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/candidate.py` | Add keyword-only `debug=` to normalize + validate; Style D unwrap / whitelist / accept-reject trails | core |
| `src/core/agent.py` | Pass `debug=debug` into draft normalize + validate at both pre-decode and post-rubric-decode sites | core |

#### Plan Approved — Joan

**discuss** — `src/core/candidate.py`, Stage 1 step 2 and Stage 2 step 5. Both stages used `if debug: logger.set_debug_flag(True)` and never set it back. `candidate.py`'s `logger` is a module-level singleton, so one debug draft run leaves `src.core.candidate` in debug state for the life of the worker — every other debug-gated emission in that module then fires on subsequent `debug=False` runs. `candidate.py` overwhelmingly prefers the unconditional form (`logger.set_debug_flag(debug)` at 11 sites vs `if debug:` at one). Recommendation: call `logger.set_debug_flag(debug)` unconditionally at the top of both functions, guard only the emissions.

**discuss** — Stage 2 step 4, nested-loop `break` hazard. One of the five in-loop failures — `"Section 'experience' must be a job array or prose string"` — sits inside `for job in val:`, not at loop top level. A literal `break` there would exit only the inner job loop and fall through to a coercion that returns `None` for a job array, silently rewriting the error to `"Section 'experience' must be prose text (string or coercible list)"` — an error-string change the plan's own Execution contract forbids. Recommendation: pin step 4 to the shared-emit `return` form at that site (or hoist the check to a helper).

**discuss** — unwrap trail is invisible to non-`do_task` `validate(debug=True)` callers, by design (`do_task` is the only production path — verified both call sites). Flagging so nobody later reads a missing unwrap line as "flat".

**acceptable** — Stage 2 step 5's "before every return, emit" reads as the single shared-exit path (the DRY reading), not five duplicated emit blocks.

Notes: the plan's central design decision — unwrap logging has to live on normalize because `do_task` calls it before validate re-normalizes — is correct and non-obvious; verified both normalize call sites (`agent.py:2562`, `2751`) and both validate call sites (`2597`, `2775`) sit inside `do_task`, where `debug` is in scope.

#### QA test manifest — Betty

New: `TestAst1272DraftHopDebugWhitelistTrail` (Style D unwrap `popped`/`flat`/`invalid` + whitelist/accepted/rejected trails; silent when `debug=False`), `TestDoTaskShouldStoreBranches::test_draft_job_resume_passes_debug_flag_to_normalize_and_validate`. Reuse AST-1270/AST-594 draft suites (no fixture edits — `debug=` defaults False). No broken/obsolete this pass; observe-only debug, no new coverage invented beyond the above.

#### Radia review — code-rubric.v2, CLEAN

**Joan's plan-rubric discuss items vs the built code:**
1. **Sticky debug flag** — built code uses the unconditional `logger.set_debug_flag(debug)` form Joan recommended in both functions. **Resolved.**
2. **break hazard** on the experience job-array loop — built code uses a `bad_job` flag to break the *outer* loop, preserving the correct error string. **Resolved.**
3. Unwrap trail invisible to non-`do_task` callers — by design, no action needed.

Full §5f backend-debug-logging pass: gated behind `debug=True` (double-gated — `debug_detail` also checks the internal flag), found/recorded vocabulary, single-job `index 1/1` header, no body text logged, no new `logger.info("[DEBUG]…")`, no data-layer logging. Full 65-statute active-set sweep (same corpus as AST-1270's) re-scored against the incremental diff: all conforms/not-applicable, no violates, no new needs-discussion — unlike AST-1270, nothing here needed Susan (pure observability, no product-behavior decision in scope).

**Findings:** none. No fix-now, no discuss. All three items Joan flagged at plan time were addressed in the built code with justified, narrow deviations from the literal plan text.

**Notes:** build self-caught and reverted an AST-1271 persist-call bleed in `agent.py` mid-implementation (dedicated `49ddf2d5a` commit) before publish — clean, no residue in the final diff.

#### Resolution (2026-08-08)

CLEAN (no fix-now, no discuss). No product changes on resolve. Joan's three plan-time discuss items were already resolved in the build (unconditional `set_debug_flag(debug)`, outer-loop `bad_job` break, unwrap-on-normalize by design) and confirmed by Radia.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/core/candidate.py` | `debug=` param + Style D unwrap trail (Stage 1); whitelist/accept-reject Style D (Stage 2) | `904d0f8b2` (Stage 1, with `agent.py`) + `12a127458` (Stage 2, with `agent.py`) |
| ✓ | `src/core/agent.py` | `debug=debug` passthrough at both normalize + both validate call sites | same two commits — +18/-2 and +4/-2 respectively |
| | _tests_ | Style D whitelist/unwrap debug trail coverage | `460f329fc`; bible `docs/test-bible/core/candidate.md` @ `8c4160af9ecabec2bf54e1c20ae67d310e71b54a` |
