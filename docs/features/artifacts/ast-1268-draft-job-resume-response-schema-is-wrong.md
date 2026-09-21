# AST-1268 — draft_job_resume response schema is wrong

<!-- linear-archive: AST-1268 archived 2026-08-19 -->

## Linear archive (AST-1268)

**Archived:** 2026-08-19  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1268/draft-job-resume-response-schema-is-wrong  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-1201; related: AST-1205

### Description

## Purpose

`draft_job_resume` is rejecting a well-formed nested model response because the Manage Tasks prompt and the runtime validator disagree on the JSON envelope. The hop must accept `agent_payload.resume` (section bodies) plus sibling `agent_payload.deviations`, validate resume keys against the candidate’s current base resume sections, and keep deviations out of resume render/persist paths so artifact drafting can land without schema folklore fights.

## Functional scope

* Adopt a nested hop contract: `agent_payload.resume` holds section bodies; `agent_payload.deviations` is a sibling metadata list (decision-drift notes for the artifacts cycle).
* Normalize must unwrap `agent_payload.resume` before section whitelist checks so `resume` is never treated as a catalog section id.
* Validate section keys inside `resume` against the candidate’s **current** `artifacts.base_resume` **section keys** (the content the hop is tailoring). Do not require a persisted `artifacts.resume_structure` blob for this whitelist.
* Align Manage Tasks / task prompt guidance with that nested contract (same keys and nesting the hop validates).
* Persist and render job resume content from the nested resume object only (e.g. paths that mean “the resume body under `.resume`”); never feed `deviations` into resume HTML/content parsers.
* Persist or retain `deviations` as hop/artifact metadata separate from resume section content so operators can see decision drift across the artifacts cycle.
* Accept experience as either a prose string or a job array for this hop (both are valid today); this epic does not force a base-resume experience migration to job arrays.
* When `debug=True`, log whitelist source (base_resume keys), envelope unwrap outcome, and accepted/rejected keys with Style D headers and `|` detail lines (AST-538).

## Architectural definition

* **Patterns to reuse** — `pattern.config.config-block`: draft metadata keys, nest unwrap names, and task flags stay in config / TASK_CONFIG rather than new inline sets in core.
* **New patterns proposed** — none.
* **Applicable statutes** — `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `astral.standards.in-scope-only`; `astral.standards.debug-contract-gated`; `astral.agent.do-task-delegation`; universal product set as applicable to core/utils changes.

## Boundaries

* Does not backfill or invent `artifacts.resume_structure` on candidates that lack it (other features may still resolve a default catalog via `resolve_resume_structure`; this epic’s draft whitelist is base_resume keys).
* Does not redesign craft-base / session parse, HTML builders beyond excluding deviations from resume body paths, or cover-letter hops.
* Does not own [AST-1201](https://linear.app/astralcareermatch/issue/AST-1201/we-need-a-daisy-chain-to-generate-the-base-resume-content) (base-resume daisy chain) or [AST-1205](https://linear.app/astralcareermatch/issue/AST-1205/approve-artifacts-task) (approve artifacts), though nested deviations support the broader artifacts cycle.
* Does not convert existing prose `experience` strings into job arrays as a migration; both shapes remain acceptable on draft.
* Must not break AST-594 / AST-997 section typing rules once the outer envelope is nested correctly.

## Acceptance criteria

* A response shaped like `{ agent_performance, agent_payload: { resume: {…section keys…}, deviations: […] } }` validates when `resume` keys are a subset of that candidate’s `artifacts.base_resume` keys and values are well-typed.
* The Manage Tasks prompt for `draft_job_resume` instructs that same nested shape (no contradictory flat-only example).
* `resume` is never reported as an unknown section key after normalize; true unknown keys inside `resume` still fail clearly.
* Job resume render/persist uses only the resume body (`.resume` / equivalent); including `deviations` in that body path does not occur.
* `deviations` is retained as metadata for the artifacts cycle (not dropped silently on a successful hop).
* Candidates without a persisted `artifacts.resume_structure` can still pass draft validation when `base_resume` section keys match.
* With `debug=True`, whitelist keys and unwrap/accept/reject outcomes are visible under Style D headers.

## Dependencies and blockers

none.

## Open questions

none.

## Proposed child tickets

#### 1!: **Nested draft_job_resume contract (prompt + normalize/validate) - Ada**

Owns unwrap of `agent_payload.resume`, whitelist from candidate `base_resume` keys, allow `deviations` as sibling metadata, and Manage Tasks prompt alignment to the nested contract. Observable: the failing nested sample shape validates when section keys/types are good; resume parsers never see `deviations` as section content. Does not own HTML chrome or other hops.
**Citations:** `pattern.config.config-block`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `astral.agent.do-task-delegation`.

#### 2: **Deviations metadata retention on draft hop - Hedy**

After #1: ensure successful draft responses retain `deviations` as hop/artifact metadata separate from resume body for the artifacts cycle (decision-drift visibility). Does not invent a full approve-artifacts UI ([AST-1205](https://linear.app/astralcareermatch/issue/AST-1205/approve-artifacts-task)).
**Citations:** `astral.config.config-source-of-truth`; `astral.standards.in-scope-only`.

#### 3: **Draft hop debug whitelist trail - Katherine**

After #1: when `debug=True`, emit Style D found/recorded detail for base_resume whitelist, unwrap, and accepted/rejected keys. Does not change allowlist rules.
**Citations:** `astral.standards.debug-contract-gated`.

---

## Original brief

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
      "candidate_tagline": "Cloud Platforms \u2022 Agile Delivery \u2022 SaaS \u2022 Healthcare",
      "candidate_contact_detail": "hire@susansomerset.com \u2022 415-745-5238 \u2022 linkedin.com/in/susansomerset \u2022 Oakland, CA (PST)",
      "professional_summary": "Founded on six years as a Systems Analyst, I approach every engagement with rigorous requirements discipline. I build structure where none exists. Sometimes that means a roadmap, sometimes a delivery framework, occasionally an entire ecosystem that wasn't supposed to be possible. Over 20 years and more than 30 engagements spanning healthtech startups, FDA-regulated medical devices, and enterprise cloud platforms, I have walked into complexity and left behind systems that work, teams that ship, and a delivery rhythm that sticks.\n\nI am equally comfortable defining product vision, shaping roadmaps, and working alongside engineers at the whiteboard. I discern patterns from ambiguity and translate them into modular, extensible scopes that drive consensus across cross-functional teams. That hands-on technical partnership has reduced iteration cycles by 80% through concise scope definition and deliberate collaboration, not process for its own sake. I apply just enough structure to ease friction using the tools already in place.\n\nI create documentation that outlasts engagements\u2014plans, decisions, and reviews\u2014ensuring clean handoff and reusable assets. I also employ AI to its best advantage, providing guardrails and support structures that manifest the analytical power of the tool while maintaining quality control and human oversight. I have designed and built several partner-tools for education, recruiting, and highly-tuned research and analysis. What drives me is coherence with the value proposition, the place where messy ideas, creative engineers, and impossible deadlines align into something elegant and often simple.",
      "core_competencies": "Business & Systems Analysis | Requirements Gathering & Documentation | Process Documentation & Mapping | Agile/Scrum Delivery | Cross-Functional Alignment | Systems Thinking | Technical Partnership | Delivery Management | Roadmapping | Operational Scaling | Regulatory Compliance (HIPAA, GDPR, FDA) | AI Product Management | Analytics",
      "experience": "Somerset Consulting\nFounder, Principal Consultant | 2011 to Present | United States / Full-time Remote\n\nOwner/operator of a boutique consultancy serving dozens of clients over 14 years, providing both business and technical leadership, often installed in teams of 5 to 30 people in healthcare, SaaS, and cloud platform operations from startups to enterprise divisions.\n\nConducted as-is process analysis across distributed teams, implemented to-be improvements that reduced feature iteration cycles from 5\u201310 rounds to 1\u20132 through lightweight delivery frameworks, and developed sustainable systems to suit team size and culture.\n\nPartnered with founders, executives, and engineering leads to translate complex goals into clear, executable roadmaps and measurable OKRs, embedding Agile/Scrum delivery principles and metrics-driven accountability.\n\nLed technical product delivery across globally distributed teams of as many as 40 people, applying Agile cadence CI/CD guardrails to achieve sprint-level clarity and measurable delivery rhythm.\n\nCoordinated go-to-market readiness and product launch strategies for client MVPs across engineering, sales, and customer success teams.\n\nArchitected multi-agent AI recruiting pipeline integrating web scraping, LLM-based analysis, and document generation, reducing manual job-matching time by 90% while maintaining quality through staged human review.\n\nWorked with lead architects to optimize for modern cloud infrastructure, reducing AWS spend by 70%, saving $23K annually in one instance, and increasing CI/CD deployment velocity to allow for more frequent and cost-effective iterations.\n\nPTown.tech\nTechnical Product Manager | 2022 to 2024 | United States / Full-time Remote\n\nBuilt enrollment funnel tracking system for B2B2C wellness platform serving enterprise clients and employees, increasing completion rates 50% by visualizing stages and working hands-on with engineering to optimize each step.\n\nGathered and documented business requirements through stakeholder interviews and use-case definition, translating them into a prioritized feature backlog that repaired a fractured relationship between decision makers and engineering by making trade-offs and user impact visible to non-technical partners.\n\nDrove an aggressive compliance effort with an uncooperative third-party security auditor, cutting through red tape to achieve full GDPR certification for global deployment in less than four months.\n\nDelivered a production-ready MVP that unlocked a global partnership with Manpower's Talent Solutions division, granting access to its worldwide enterprise network and positioning the client for rapid, multinational expansion.\n\nEMIDS Technologies\nTechnical Product Owner | 2021 to 2022 | United States / Full-time Remote\n\nChampioned platform adoption by reluctant engineering teams, securing buy-in from key system owners and aligning resources, timelines, and data access to enable full integration of patient services.\n\nConducted business process mapping of existing onboarding workflows, identified bottlenecks, and established the first end-to-end onboarding framework for engineering teams integrating into the centralized platform. Personally managed 12 onboardings through security, legal, and compliance gates to ensure HIPAA- and FHIR-compliant production deployment.\n\nNegotiated with solution architects to reconcile legacy design patterns with modern, scalable architectures that fully supported microservice performance and security requirements.\n\nLed user story mapping sessions and strengthened delivery rhythm across product and platform groups through SAFe Program Increment planning and transparent Agile Release Train coordination.\n\nGreen Mars Consulting\nCEO | 2018 to 2020 | United States / Full-time Remote\n\nBuilt innovative delivery frameworks orchestrating up to 7 concurrent client projects from around the world with a 25-employee remote engineering team, driving consistency, accountability, and measurable quality for each and every delivery.\n\nDesigned API integration strategies for medical-device clients, enabling seamless data exchange between cloud platforms and clinical systems, observing regulatory standards and supporting 2 successful FDA submissions with traceable, testable systems, while preserving agility for iterative design and cross-team innovation.\n\nAuthored functional and technical requirements in JAMA for a Point-of-Care Ultrasound (POCUS) platform, including verification protocols and data-exchange specifications (DICOM, HL7), which enabled rigorous system testing and secure integration with hospital PACS systems and cloud architecture.\n\nTellme Networks / Microsoft\nSr. Operations IT Program Manager | 2006 to 2011 | Mountain View, CA / Full-time Onsite\n\nDrove cross-functional programs integrating business operations, IT systems, and analytics through Tellme's acquisition and transition into Microsoft, preventing deployment delays of up to 6 weeks through proactive stakeholder alignment.\n\nDesigned and deployed business-intelligence tools with KPI-driven dashboards that improved cost management, resource planning, and operational transparency across multiple departments.\n\nLed requirements definition, data-model design, and automation efforts that increased reporting accuracy and decision velocity for executive and engineering stakeholders.",
      "prior_experience": "Project Manager (4 yrs) \u2022 Systems Analyst (6 yrs) \u2022 ETL Migration Specialist (2 yrs) \u2022 Database Engineer (2 yrs) \u2022 VBA Software Developer (3 yrs)",
      "education_certifications": "Certified ScrumMaster (CSM) \u2022 Scrum Alliance, 2024 to 2026\nCertified Scrum Product Owner (CSPO) \u2022 Scrum Alliance, 2024 to 2026\nUW Milwaukee \u2022 Completed coursework in Computer Science and Business Administration",
      "technical_skills": "Project Management: Linear | Jira | Trello | Azure DevOps | Jira Align | Asana | JAMA | Pivotal Tracker\nDesign & Documentation: Figma | Lucidchart | ERD Tools | Miro | Mural | Confluence (Wiki)\nDevelopment & APIs: Python | Next.js | Google Apps Script | GraphQL | REST | JSON\nCloud & DevOps: AWS | Vercel | GitHub | CI/CD Pipelines\nData & Analytics: PostgreSQL | MySQL | Prisma | Airtable | Tableau | QlikView | Talend (ETL)\nIntegration & Automation: Zapier | Google Workspace | GitHub Actions | Make | Microsoft 365 | Power Automate\nAI Development & Orchestration: Claude API | GPT-4 | Multi-agent workflows | Prompt engineering | Cursor | Copilot | Structured AI outputs | Self-healing code\nCollaboration: Slack | Discord | Teams | Zoom | Google Meet"
    },
    "deviations": [
      "Skipped adding a separate 'Systems Analysis & Process Expertise' section because the output schema does not permit new keys; the required content was instead woven into the professional summary and core competencies.",
      "Skipped UAT-specific language in the resume because Susan has not confirmed recent hands-on UAT experience; the brief's instruction to claim UAT was deferred per gap-handling guidance."
    ]
  }
}
```

first question: are we setting the expected response based on the candidate's base_resume content, specifically, or is the list "['candidate_contact_detail', 'candidate_name', 'candidate_tagline', 'candidate_title', 'core_competencies', 'education_certifications', 'experience', 'prior_experience', 'professional_summary', 'technical_skills']" hard-coded anywhere (including [config.py](<http://config.py>)) in the codebase?

The Response_schema should give the JSON elements of the candidate's current base_resume sections and validate against those.

Please confirm current behavior before we change anything.

## Git (authoritative — ignore Linear `gitBranchName`)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Ticket | `origin/…` |
| -- | -- |
| [AST-1268](https://linear.app/astralcareermatch/issue/AST-1268/draft-job-resume-response-schema-is-wrong) (parent) | ftr/AST-1268-draft-job-resume-response-schema-is-wrong |
| [AST-1270](https://linear.app/astralcareermatch/issue/AST-1270/nested-draft-job-resume-contract-prompt-normalizevalidate-draft-job) | sub/AST-1268/AST-1270-nested-draft-job-resume-contract |
| [AST-1271](https://linear.app/astralcareermatch/issue/AST-1271/deviations-metadata-retention-on-draft-hop-draft-job-resume-response) | sub/AST-1268/AST-1271-deviations-metadata-retention-on-draft-hop |
| [AST-1272](https://linear.app/astralcareermatch/issue/AST-1272/draft-hop-debug-whitelist-trail-draft-job-resume-response-schema-is) | sub/AST-1268/AST-1272-draft-hop-debug-whitelist-trail |

**Epic worktree:** `astral-AST-1268/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | `/home/susan/.cursor/chats/ba0b8fd4e41dce68bad4ce49b257d487/2f7cf194-d36b-4aa9-953d-d66649e98fb2/store.db` |
| Hedy | engineer | `/home/susan/.cursor/chats/ba0b8fd4e41dce68bad4ce49b257d487/acf51cc0-977c-4631-b0a4-fb80b2c28fe0/store.db` |
| Katherine | engineer | `/home/susan/.cursor/chats/ba0b8fd4e41dce68bad4ce49b257d487/ddae4d06-b7a0-4839-bd17-76c977b8df2d/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/b938911e-2991-45e0-859f-ed62ea393da0/store.db` |
| Radia | review | `/home/susan/.cursor/chats/ba0b8fd4e41dce68bad4ce49b257d487/ed148395-1ccd-45c2-b419-e3d43edc031d/store.db` |

### Comments

#### susan — 2026-08-08T01:59:42.196Z
I guess I can't test this until the ref_agent_data_id issue is resolved.

#### chuckles — 2026-08-08T01:57:29.007Z
[fix-uat] blocked: open questions on parent

@susan Two separate UAT signals — I still cannot file an AC-tied bug under AST-1268 without your call:

1. **`draft_job_resume` `total_errors=1` with no further log** — We still have no `Validation failed:` / exception text for batch `draft_job_resume-365a4168-…`. Without that, I cannot tell whether the nested-`resume` contract (this epic) still fails vs a non-schema runner fault. Please re-run once on current `origin/dev` with the local process restarted and `debug=True` on that dispatch task, then paste the ERROR / Style D / Validation lines.

2. **`ValueError: agent_data ref target missing: 'check_job_resume-c9fa00ec-…'`** (during `[contemplate_job]`) — That is pin/ref resolution (`database._resolve_agent_data_block_data`), not the draft nest/whitelist ACs on this parent. Boundaries already push pin write/resolve to the AST-1099 / AST-1100 family. **Do you want a new parent for dangling `ref_agent_data_id` targets, or should we expand AST-1268 AC to cover agent_data ref integrity on the artifacts chain?** I will not invent that scope here.

Assign Chuckles again when you answer.

— Chuckles

#### susan — 2026-08-08T01:56:26.708Z
There was no further log about it.

#### susan — 2026-08-08T01:56:04.277Z
```
  File "/Users/susan/chuckles/astral/src/data/database.py", line 265, in _run_with_retry
    return fn()
           ^^^^
  File "/Users/susan/chuckles/astral/src/data/database.py", line 5898, in _with_conn
    d["block_data"] = _resolve_agent_data_block_data(conn, d)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/src/data/database.py", line 5867, in _resolve_agent_data_block_data
    raise ValueError(f"agent_data ref target missing: {current_id!r}")
ValueError: agent_data ref target missing: 'check_job_resume-c9fa00ec-9520-48db-9d07-e74a58f6c11f-task-ac21267ced673803'
[contemplate_job] thread exited and cleared from registry
127.0.0.1 - - [07/Aug/2026 18:45:06] "GET /api/admin/scheduler/thread_status HTTP/1.1" 200 -
127.0.0.1 - - [07/Aug/2026 18:45:06] "GET /api/admin/scheduler/thread_status HTTP/1.1" 200 -
127.0.0.1 - - [07/Aug/2026 18:45:11] "GET /api/admin/scheduler/thread_status HTTP/1.1" 200 -
127.0.0.1 - - [07/Aug/2026 18:45:16] "GET /api/admin/scheduler/thread_status HTTP/1.1" 200 -
127.0.0.1 - - [07/Aug/2026 18:45:21] "GET /api/admin/scheduler/thread_status HTTP/1.1" 200 -
127.0.0.1 - - [07/Aug/2026 18:45:26] "GET /api/admin/scheduler/thread_status HTTP/1.1" 200 -
```

#### chuckles — 2026-08-08T01:40:31.266Z
[fix-uat] blocked: open questions — need the actual hop error

@susan Your paste shows `draft_job_resume` claimed job `6f25f71f-…` and finished with `total_errors=1`, but the log cuts off before any `Validation failed:` / `do_task validation failed` / traceback line. That summary alone is not enough to file a UAT bug against parent AC (could still be nested-`resume` schema, a *new* whitelist/typing reject after AST-1270, or a non-schema runner error — and I cannot tell which).

Please paste the ERROR / `Validation failed:` block for that run (same batch `draft_job_resume-365a4168-…` if you still have it), and note whether the local process was restarted on current `origin/dev` (AST-1270 unwrap is on `dev`) before the click. Then assign Chuckles again and I’ll file + pipeline.

— Chuckles

#### susan — 2026-08-08T01:38:10.267Z
```
127.0.0.1 - - [07/Aug/2026 18:34:20] "GET /api/deploy_status HTTP/1.1" 200 -
127.0.0.1 - - [07/Aug/2026 18:34:20] "GET /api/nav_config?candidate_id=somerset HTTP/1.1" 200 -
127.0.0.1 - - [07/Aug/2026 18:34:22] "POST /api/admin/dispatch_tasks/11174/run HTTP/1.1" 200 -
dispatcher._dispatch_one index 1/1 draft_job_resume -> task start
 | candidate_id=somerset available_count=1 entity_batch_id=draft_job_resume-365a4168-bc46-4bdd-bd4a-ce55d554e46f mode=CLICK run_next_chain=True entity_type='job' trigger_state='BUILD_ARTIFACTS.advise_job_resume'
Dispatching draft_job_resume — 1 available, batch draft_job_resume-365a4168-bc46-4bdd-bd4a-ce55d554e46f
dispatcher._run_dispatch_loop index 1/1 draft_job_resume -> loop iteration 1 starting
 | available=1 effective_min=1 max_runs=1 draining=False entity_batch_id=draft_job_resume-365a4168-bc46-4bdd-bd4a-ce55d554e46f
dispatcher._run_task index 1/1 draft_job_resume -> running batch
 | batch_size=1 batch_id=None entity_type='job' trigger_state='BUILD_ARTIFACTS.advise_job_resume'
dispatcher._run_unified index 1/1 job/BUILD_ARTIFACTS.advise_job_resume -> claimed 1 entity/entities
 | task_key=draft_job_resume batch_id=draft_job_resume-365a4168-bc46-4bdd-bd4a-ce55d554e46f batch_call_mode=False dispatch batch_size=1 claim_cap=None claim_states=['BUILD_ARTIFACTS.advise_job_resume']
dispatcher._run_unified index 1/1 6f25f71f-b2a0-4b23-ad43-434c245af0fb -> claimed
 | entity_type=job trigger_state=BUILD_ARTIFACTS.advise_job_resume state='BUILD_ARTIFACTS.advise_job_resume'
 | batch end summary={'total_processed': 1, 'total_passed': 0, 'total_failed': 0, 'total_errors': 1}
 | runner returned summary={'total_processed': 1, 'total_passed': 0, 'total_failed': 0, 'total_errors': 1}
 | iteration 1 summary processed=1 passed=0 failed=0 errors=1 accumulated={'total_processed': 1, 'total_passed': 0, 'total_failed': 0, 'total_errors': 1}
 | loop stop: max_runs reached max_runs=1 run_count=1
[draft_job_resume] thread exited and cleared from registry
127.0.0.1 - - [07/Aug/2026 18:34:22] "GET /api/admin/scheduler/thread_status HTTP/1.1" 200 -
127.0.0.1 - - [07/Aug/2026 18:34:23] "GET /api/admin/scheduler/thread_status HTTP/1.1" 200 -
127.0.0.
```

I don't know why this is failing.

#### chuckles — 2026-08-08T01:36:55.796Z
[fix-uat] UAT fixes landed — ready for re-test

_No UAT bug children listed — prep-uat merge only._

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-08-08T01:27:30.554Z
You're right. I was commenting on the wrong ticket.  lol

#### chuckles — 2026-08-08T01:27:08.327Z
[check-linear] answered — not the pin/fetch gap. The UAT fail was `Unknown resume section key 'resume'`: Manage Tasks nested `agent_payload.resume` while validate treated `resume` as a section id (AST-1270 unwrap + base_resume whitelist). `ref_agent_data_id` / AST-1099 pin only runs after a successful RESPONSE store — related as a downstream consequence of a failed hop, not this schema mismatch.

— Chuckles

#### susan — 2026-08-08T01:15:29.538Z
@chuckles I bet this is related to the issue of the ref_agent_data_id not being fully implemented from the fetch side.

#### chuckles — 2026-08-08T00:01:25.539Z
@susan On your structure / experience check:

1. Missing `artifacts.resume_structure` on the candidate is real and allowed today. Draft validation does **not** read the blob you see in the DB row — `resolve_resume_structure` falls back to `RESUME_STRUCTURE_DEFAULT` in config when structure is absent/invalid. That is why the error listed those ten section ids even though your candidate has no persisted structure. Structure gets written when craft-base / parse persistence succeeds (post AST-517/650); older base_resume-only records can still lack it.
2. Prose `experience` (one long string) is still valid on draft — AST-997 accepts job array **or** string. Job-array shape was added for craft-base; it is not a forced migration of existing candidates. Out of scope for this epic to convert your string to jobs.

Definition updated from your calls: nested `resume` + sibling `deviations`; whitelist = `base_resume` keys; render/persist only `.resume`; deviations retained as metadata. Open questions cleared — ready for your Todo + assign Chuckles when you approve.

— Chuckles

#### chuckles — 2026-08-07T23:49:52.131Z
@susan Current behavior (no code changes yet):

1. Whitelist is **not** taken from `artifacts.base_resume` content keys. Runtime `validate_draft_job_resume_payload` allows keys from the candidate’s **enabled** `artifacts.resume_structure` section ids.
2. That error list is that candidate’s enabled catalog (sorted for the message). It matches the default known set in `config.py` (`RESUME_STRUCTURE_KNOWN_SECTION_IDS` / `RESUME_STRUCTURE_DEFAULT`) when the candidate still uses the default enabled sections — but draft validation reads the per-candidate structure, not a hard-coded ten-name list inside the validator.
3. `TASK_CONFIG["draft_job_resume"].response_schema` only has optional hop metadata (`astral_job_id` / `company` / `title`). Section bodies are gated by `resume_section_payload: True` + the runtime catalog check above — not by a static section schema in that TASK_CONFIG block.
4. Normalize unwraps nests named `content` / `section_content` / `base_resume` — **not** `resume`. So `agent_payload.resume` fails as unknown section key `resume`. `deviations` is also not in draft metadata allowlist today.

Open questions (need your call before Todo):
1. Whitelist source: keep enabled `resume_structure`, switch to keys on `base_resume`, or intersection?
2. Envelope: flat section keys on `agent_payload` (validator today) vs nested `resume` + `deviations` (prompt today)?
3. Keep / drop / relocate `deviations`?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
