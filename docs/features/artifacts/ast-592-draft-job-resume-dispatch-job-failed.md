# AST-592 — draft_job_resume dispatch job failed

<!-- linear-archive: AST-592 archived 2026-06-23 -->

## Linear archive (AST-592)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-592/draft-job-resume-dispatch-job-failed  
**Status at archive:** Done  
**Project:** Astral Artifacts  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-300; related: AST-581

### Description

## Purpose

Susan manually dispatched `draft_job_resume` and the run failed after a long, successful-looking LLM call. The model returned tailored resume prose (`candidate_name`, `experience`, etc.) with `agent_performance: success`, but runtime validation rejected the payload for `Missing required field 'grades'`. The hop is authored in [AST-313](https://linear.app/astralcareermatch/issue/AST-313/artifact-pipeline-prompt-authoring) as Judith's resume line-edits step and is expected to produce structure-keyed resume content per [AST-551](https://linear.app/astralcareermatch/issue/AST-551/structure-aligned-resume-chain-after-ast-477-build-resume-artifact) — not a graded consult response. The product still carries the legacy graded-consult contract on this task key from [AST-450](https://linear.app/astralcareermatch/issue/AST-450/register-artifact-pipeline-task-keys-dumb-chain-registry), so validation fails even when the model did what the prompt asked. Susan cannot diagnose the failure from thin logs and a response that looks correct for resume drafting.

## Functional scope

* Align the `draft_job_resume` response contract with the artifact-pipeline hop it actually performs: job-tailored resume section content keyed to the active candidate's enabled section catalog ([AST-551](https://linear.app/astralcareermatch/issue/AST-551/structure-aligned-resume-chain-after-ast-477-build-resume-artifact) / [AST-518](https://linear.app/astralcareermatch/issue/AST-518/resume-builder-and-job-artifact-keys-from-candidate-structure)), not the legacy `grades` + twelve-vector consult shape.
* Remove or replace graded-consult validation requirements (`grades`, `grading_mode`, `vectors`, `context_format: grade_like`) on this task key so they do not block resume-draft hops.
* **Susan (2026-06-06):** All section fields on this hop are **optional** at validation time. Any keys present must align to sections defined on the candidate's resume structure — the model must not invent new section headers (e.g. spurious keys outside the catalog).
* When validation still fails on any Phase E artifact hop, surface the specific schema error and which expected fields were missing or which unknown keys were rejected on the hop's Execution History row and in backend logs — not only a generic `do_task validation failed` line after an otherwise successful LLM response.
* Preserve existing daisy-chain behavior: a failed `draft_job_resume` hop must not advance `run_next`, must not persist resume content, and must leave the job in a recoverable failure state consistent with [AST-300](https://linear.app/astralcareermatch/issue/AST-300/build-resume-artifact) / [AST-552](https://linear.app/astralcareermatch/issue/AST-552/build-artifacts-gate-and-structure-keyed-persistence-build-resume) (no silent success).
* If models return nested or structure-wrapped JSON (same class as [AST-536](https://linear.app/astralcareermatch/issue/AST-536/ast-477-uat-craft-resume-base-rejects-deepseek-payload-missing) on `craft_resume_base`), normalize to the flat section-key contract before validation so DeepSeek-shaped payloads are accepted when content is present.

## Boundaries

* Does not rewrite Susan's Manage Tasks prompts for `draft_job_resume` ([AST-313](https://linear.app/astralcareermatch/issue/AST-313/artifact-pipeline-prompt-authoring) content stays Susan-owned).
* Does not change consult-path graded tasks (`grade_do`, `grade_get`, `grade_like`, etc.).
* Does not redesign Execution History UI beyond making this hop's validation failure legible on the existing per-hop row ([AST-528](https://linear.app/astralcareermatch/issue/AST-528/per-hop-execution-history-for-daisy-chained-tasks) / [AST-532](https://linear.app/astralcareermatch/issue/AST-532/execution-history-ui-per-hop-rows-and-inspection-per-hop-execution)).
* Does not fix unrelated [AST-300](https://linear.app/astralcareermatch/issue/AST-300/build-resume-artifact) UAT items ([AST-591](https://linear.app/astralcareermatch/issue/AST-591/uat-generate-artifacts-must-transition-job-to-build-artifacts-405), [AST-587](https://linear.app/astralcareermatch/issue/AST-587/uat-recommended-list-row-opens-job-detail-instead-of-job-analysis), [AST-581](https://linear.app/astralcareermatch/issue/AST-581/uat-preview-materials-button-resumecover-html-preview-tabs-in-jar)) unless they share the same schema-validation root cause.
* Must not break jobs already in **CANDIDATE_REVIEW** with persisted `resume_content`.

## Acceptance criteria

1. Re-running dispatch batch `draft_job_resume-80308ccb-087e-4100-af38-937ea9c75e01` (or an equivalent manual **Run** on `draft_job_resume` for the same job with the same prompt) succeeds when the model returns resume-section JSON like the payload in the original brief — no `Missing required field 'grades'` error.
2. `TASK_CONFIG` for `draft_job_resume` no longer requires `grades` or other consult-only graded fields; validation accepts payloads with only candidate-catalog section keys (all optional per Susan); unknown section keys fail with an explicit error.
3. On intentional validation failure (deliberately malformed test payload or invented section key), Execution History for that hop shows failed status and the exact validation message; backend logs include the same message at ERROR for the hop.
4. A successful `draft_job_resume` hop in a full resume chain still passes `{$CALLER_*}` content to `check_job_resume` per existing `run_next` wiring; no regression on [AST-530](https://linear.app/astralcareermatch/issue/AST-530/structured-run-next-hop-logging-and-empty-caller-guard-daisy-chain-hop) hop logging.
5. Component tests cover at least: valid structure-keyed resume payload accepted; legacy grades-only requirement removed; unknown section key rejected; validation failure message is observable.

## Dependencies and blockers

* [AST-551](https://linear.app/astralcareermatch/issue/AST-551/structure-aligned-resume-chain-after-ast-477-build-resume-artifact) (structure-aligned resume chain) — landed in [AST-300](https://linear.app/astralcareermatch/issue/AST-300/build-resume-artifact) UAT; defines the authoritative section-keyed output model for resume hops.
* [AST-518](https://linear.app/astralcareermatch/issue/AST-518/resume-builder-and-job-artifact-keys-from-candidate-structure) (resume builder / artifact keys from candidate structure) — defines which section ids are valid.
* [AST-450](https://linear.app/astralcareermatch/issue/AST-450/register-artifact-pipeline-task-keys-dumb-chain-registry) (task key registry) — introduced the stale graded schema this bug corrects.
* [AST-536](https://linear.app/astralcareermatch/issue/AST-536/ast-477-uat-craft-resume-base-rejects-deepseek-payload-missing) (precedent) — same validation mismatch pattern on `craft_resume_base`; normalization approach may apply here.
* Parent epic [AST-300](https://linear.app/astralcareermatch/issue/AST-300/build-resume-artifact) is in User Testing; fix should publish on the active integration path Susan is exercising.

## Open questions

none.

---

## Original brief

draft_job_resume-80308ccb-087e-4100-af38-937ea9c75e01

I can't tell why this job failed.  The logs are thin, and the response looks fine.

\[2026-06-06 04:48:16\] INFO src.external.deepseek: LLM deepseek task=draft_job_resume 223.6s stop=end_turn tokens in=5287 out=10327

\[2026-06-06 04:48:16\] INFO src.external.deepseek: \[DEBUG\] send_to_deepseek('draft_job_resume'): 223.6s | stop_reason=end_turn
\[2026-06-06 04:48:16\] INFO src.external.deepseek: \[DEBUG\]   vendor=deepseek-v4-pro tokens: fresh=5287 cache_read=20736 cache_write=0 output=10327

\[2026-06-06 04:48:16\] ERROR src.core.agent: do_task validation failed. task_key='draft_job_resume' error=Missing required field 'grades'

\[2026-06-06 04:44:33\] INFO src.core.agent: \[DEBUG\] do_task('draft_job_resume'): brain_setting=Big provider=deepseek model=deepseek-v4-pro max_tokens=16000 temp=0.3 skip_cache=False candidate=somerset

\[2026-06-06 04:44:33\] INFO src.core.agent: \[DEBUG\] do_task('draft_job_resume'): 4 system block(s) + 1 user block(s)

```
[061bdaf1-f203-4785-82b0-9dc6f70a26c4]
{
  "agent_performance": "success",
  "agent_payload": {
    "candidate_name": "Susan Somerset",
    "candidate_title": "Director of Product | AI Platforms & Enterprise SaaS | Product-Led Growth",
    "candidate_contact_detail": "hire@susansomerset.com • 415-745-5238 • linkedin.com/in/susansomerset • California, USA (PST)",
    "professional_summary": "I build the conditions for teams to ship — translating ambiguous market opportunities into product strategy, actionable roadmaps, and a delivery rhythm that sticks. Over 20 years and 30+ engagements across healthtech, SaaS, and enterprise cloud platforms, I've partnered with founders, CEOs, and engineering leads to take products from early discovery and prototyping through launch, iteration, and scaling, driving product-led growth and enterprise adoption. I'm equally comfortable shaping vision, running competitive analysis, and standing shoulder-to-shoulder with engineers at the whiteboard. That hands-on technical partnership has cut iteration cycles by 80% and unlocked global partnerships by aligning product priorities with user needs. I design systems where AI augments human judgment — not replaces it — having built multi-agent workflows and AI-assisted delivery toolchains that accelerate quality output while maintaining human oversight. What drives me is coherence: the moment when messy ideas, capable teams, and sharp priorities align into products that markets actually want.",
    "core_competencies": "Product Strategy & Vision | Product-Led Growth | Enterprise Go-to-Market | AI-Augmented Product Management | Delivery Management | Cross-Functional Alignment | Systems Thinking | Roadmapping | Operational Scaling | Stakeholder Management | Agile/Scrum | Data-Driven Decision Making",
    "product_leadership_impact": "Product engagements: 30+ | Teams led: 5–40 | Delivery cycles reduced: 80% | Cloud costs optimized: 70% ($23K/yr) | Regulatory compliance: HIPAA, GDPR, FDA",
    "ai_augmented_product_leadership": "Pioneered AI-assisted product delivery using Claude, GPT-4, Cursor, and multi-agent workflows to scaffold specifications, generate automated tests, and accelerate documentation — reducing iteration cycles by 80%. Architected a multi-agent AI recruiting pipeline integrating web scraping, LLM-based analysis, and document generation, cutting manual job-matching time by 90% while preserving quality through staged human review.",
    "experience": [
      {
        "company": "Somerset Consulting",
        "title": "Principal Product Lead (Consulting)",
        "dates": "2011 to Present",
        "location": "United States / Full-time Remote",
        "bullets": [
          "Defined product vision and go-to-market strategies for clients across healthtech, SaaS, and cloud platforms, translating complex market opportunities into executable roadmaps and measurable OKRs.",
          "Managed the full product lifecycle — from early discovery and prototyping through launch, iteration, and scaling — across 30+ engagements, creating repeatable delivery frameworks that accelerated time-to-market.",
          "Led end-to-end product delivery for globally distributed teams of up to 40, instituting Agile cadence, CI/CD guardrails, and metrics-driven accountability to achieve sprint-level clarity.",
          "Orchestrated launch coordination for client MVPs, aligning engineering, sales, and customer success to ensure coordinated product releases.",
          "Conducted competitive intelligence and market analysis to inform product positioning and roadmap prioritization across B2B sectors.",
          "Reduced AWS infrastructure costs by 70% ($23K/yr) and compressed feature iteration cycles from 5–10 rounds to 1–2 through targeted process redesign and technical oversight."
        ]
      },
      {
        "company": "PTown.tech",
        "title": "Technical Product Manager",
        "dates": "2022 to 2024",
        "location": "United States / Full-time Remote",
        "bullets": [
          "Drove product-led growth for a B2B2C wellness platform by building an enrollment funnel tracking system, increasing completion rates 50% through iterative optimization of activation and conversion touchpoints.",
          "Repaired fractured stakeholder alignment by leading feature-level use case definition and prioritization sessions, translating engineering trade-offs for non-technical decision makers and restoring cross-team trust.",
          "Delivered a production-ready MVP that unlocked a global partnership with Manpower's Talent Solutions division — a land-and-expand motion enabling enterprise adoption across multinational networks.",
          "Steered aggressive GDPR compliance effort with a third-party auditor, securing full certification in under four months to enable global deployment."
        ]
      },
      {
        "company": "EMIDS Technologies",
        "title": "Technical Product Owner",
        "dates": "2021 to 2022",
        "location": "United States / Full-time Remote",
        "bullets": [
          "Championed platform adoption across reluctant engineering teams, securing buy-in and establishing the first end-to-end onboarding framework for 12 teams integrating into a centralized healthcare platform with HIPAA- and FHIR-compliant production deployment.",
          "Led integration delivery for a large healthcare company's hosted application, driving SAFe Program Increment planning and transparent Agile Release Train coordination to strengthen delivery rhythm.",
          "Collaborated with solution architects to reconcile legacy and modern architectures, ensuring microservice performance, scalability, and security."
        ]
      },
      {
        "company": "Green Mars Consulting",
        "title": "CEO & Product Lead",
        "dates": "2018 to 2020",
        "location": "United States / Full-time Remote",
        "bullets": [
          "Designed delivery frameworks that orchestrated up to 7 concurrent client projects with a 25-person remote engineering team, ensuring consistent quality and accountability.",
          "Directed product strategy for medical device and AI/ML clients: defined MVP features, authored functional and technical requirements in JAMA, and guided a Point-of-Care Ultrasound platform through 2 successful FDA submissions.",
          "Designed API integration strategies for medical devices, enabling secure data exchange (DICOM, HL7) between cloud platforms and clinical systems while maintaining regulatory compliance and agile iteration."
        ]
      },
      {
        "company": "Tellme Networks / Microsoft",
        "title": "Sr. Operations IT Program Manager",
        "dates": "2006 to 2011",
        "location": "Mountain View, CA / Full-time Onsite",
        "bullets": [
          "Drove cross-functional programs integrating business operations, IT, and analytics through the Tellme acquisition and transition into Microsoft, preventing deployment delays of up to 6 weeks through proactive stakeholder alignment.",
          "Designed business-intelligence tools with KPI-driven dashboards that improved cost management, resource planning, and operational transparency for executive and engineering stakeholders.",
          "Led requirements definition, data-model design, and automation efforts that increased reporting accuracy and decision velocity."
        ]
      }
    ],
    "education_certifications": "Certified ScrumMaster (CSM) • Scrum Alliance, 2024 to 2026\nCertified Scrum Product Owner (CSPO) • Scrum Alliance, 2024 to 2026\nUW Milwaukee • Completed coursework in Computer Science and Business Administration",
    "technical_skills": "Project Management: Linear | Jira | Trello | Azure DevOps | Jira Align | Asana | JAMA | Pivotal Tracker\nDesign & Documentation: Figma | Lucidchart | ERD Tools | Miro | Mural | Confluence (Wiki)\nDevelopment & APIs: Python | Next.js | Google Apps Script | GraphQL | REST | JSON\nCloud & DevOps: AWS | Vercel | GitHub | CI/CD Pipelines\nData & Analytics: PostgreSQL | MySQL | Prisma | Airtable | Tableau | QlikView | Talend (ETL)\nIntegration & Automation: Zapier | Google Workspace | GitHub Actions | Make | Microsoft 365 | Power Automate\nAI Development & Orchestration: Claude API | GPT-4 | Multi-agent workflows | Prompt engineering | Cursor | Copilot | Structured AI outputs | Self-healing code\nCollaboration: Slack | Discord | Teams | Zoom | Google Meet"
  }
}
```

### Comments

#### betty — 2026-06-12T18:30:28.290Z
Betty land preflight: CLEAN @ 30b3987dea394b40500c0ccdfbc6f070a1cb2f42

#### chuckles — 2026-06-12T00:50:22.171Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-607** | `{$BASE_RESUME}` was routed through `value_to_str`, which renders legacy `{label, content}` arrays as markdown `###` sections. Added `format_base_resume_for_token` so the token always emits section-id-keyed JSON (dict passthrough via `filte |

Local `dev` merged via prep-uat. Re-run the **Manual test steps** from the latest prep-uat comment on this ticket; pay extra attention to the bugs above.

— Chuckles

#### chuckles — 2026-06-12T00:44:48.134Z
## Git (fix-uat wave)

| Ticket | `origin/…` |
|--------|------------|
| AST-592 (parent) | ftr/ast-592-draft-job-resume-dispatch-job-failed |
| AST-607 | sub/AST-592/ast-607-base-resume-token-must-inject-json-not-markdown |

— Chuckles

#### susan — 2026-06-12T00:42:47.348Z
Okay, I think I see the issue:  You're parsing the base resume content into markdown instead of rendering it as actual JSON for the agent.  It needs to be the JSON structure so that the keys can match exactly.  Always use the JSON format of the base resume content when passing it to an agent, do not add a new "BASE_RESUME_JSON" token, or whatever.

#### chuckles — 2026-06-12T00:08:03.218Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-604** | `draft_job_resume` validation rejected `candidate_contact` because the candidate catalog uses `candidate_contact_detail`. Added `_DRAFT_JOB_RESUME_SECTION_ALIASES` and `_apply_draft_job_resume_section_aliases()` in `normalize_draft_job_resu |

Local `dev` merged via prep-uat. Re-run the **Manual test steps** from the latest prep-uat comment on this ticket; pay extra attention to the bugs above.

— Chuckles

#### chuckles — 2026-06-12T00:04:51.033Z
## Git (fix-uat wave)

| Ticket | `origin/…` |
|--------|------------|
| AST-592 (parent) | ftr/ast-592-draft-job-resume-dispatch-job-failed |
| AST-604 | sub/AST-592/ast-604-draft-job-resume-rejects-candidate-contact-alias |

— Chuckles

#### susan — 2026-06-12T00:02:19.118Z
Still having issues. Here is the log from my test (@chuckles create a subissue for this, rather than resetting this ticket.):

\[2026-06-11 23:57:35\] INFO src.core.agent: \[DEBUG\] do_task('draft_job_resume'): brain_setting=Big provider=deepseek model=deepseek-v4-pro max_tokens=16000 temp=0.3 skip_cache=False candidate=somerset

\[2026-06-11 23:57:35\] INFO src.core.agent: \[DEBUG\] do_task('draft_job_resume'): 4 system block(s) + 1 user block(s)

\[2026-06-11 23:57:35\] INFO src.external.deepseek: LLM deepseek task=draft_job_resume 87.2s stop=end_turn tokens in=4108 out=10428

\[2026-06-11 23:57:35\] INFO src.external.deepseek: \[DEBUG\] send_to_deepseek('draft_job_resume'): 87.2s | stop_reason=end_turn
\[2026-06-11 23:57:35\] INFO src.external.deepseek: \[DEBUG\]   vendor=deepseek-v4-pro tokens: fresh=4108 cache_read=20480 cache_write=0 output=10428

\[2026-06-11 23:57:35\] ERROR src.core.agent: do_task validation failed. task_key='draft_job_resume' error=Unknown resume section key 'candidate_contact' (not in candidate catalog: \['candidate_contact_detail', 'candidate_name', 'candidate_title', 'core_competencies', 'education_certifications', 'experience', 'prior_experience', 'professional_summary', 'technical_skills'\])

#### chuckles — 2026-06-11T23:47:06.337Z
## Manual test steps

**Prereq:** Local `dev` @ `17f83da5` (restart app if running). Candidate `somerset` with resume structure / enabled sections configured.

1. **Susan's original failure batch** — Re-run dispatch batch `draft_job_resume-80308ccb-087e-4100-af38-937ea9c75e01` (or manual **Run** on `draft_job_resume` for the same job). Expect hop **success** when the model returns structure-keyed resume JSON (no `Missing required field 'grades'`).
2. **Valid payload** — Confirm hop accepts section keys from the candidate catalog (`candidate_name`, `professional_summary`, `experience`, etc.) without `grades` / vectors.
3. **Unknown section key** — Deliberately malformed or invented section key in a test dispatch; Execution History row shows **failed** with explicit validation message; backend log has same ERROR for the hop.
4. **Chain wiring** — On a successful `draft_job_resume` in a full resume chain, verify `{$CALLER_*}` still flows to `check_job_resume` per existing `run_next` (no regression on hop logging).
5. **CANDIDATE_REVIEW jobs** — Spot-check an existing job with persisted `resume_content` still loads normally.

`origin/ftr/ast-592-draft-job-resume-dispatch-job-failed` @ `17f83da5` · local `dev` merged (§8). Deleted `sub/AST-592/ast-594-draft-job-resume-schema-alignment`.

Reset after UAT: `git reset --hard origin/dev`

— Chuckles

#### chuckles — 2026-06-06T05:18:14.607Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-592 (parent) | ftr/ast-592-draft-job-resume-dispatch-job-failed |
| AST-594 | sub/AST-592/ast-594-draft-job-resume-schema-alignment |

## Epic sessions (headless — Chuckles injects in every spawn; agents do not read Linear)

| Agent | Session id | Ticket | Role |
|-------|------------|--------|------|
| Joan | `d3ad69df-a444-43d0-9f6d-e4418f280182` | AST-592 (parent) | git |
| Ada | `fccedd5b-8ae5-40b1-8c9f-33bb4caf80bd` | AST-594 | engineer |
| Betty | `e63bda94-3ad3-4bb2-b7f2-e85ea3e993fb` | AST-594 | qa |
| Radia | `4d9231b2-7ae8-47fd-8e49-401455a12d30` | AST-594 | review |

**Parent:** AST-592

— Chuckles

#### susan — 2026-06-06T05:08:58.979Z
They're all optional at this point, as long as they align to the sections defined and they aren't creating new section headers like "Christmas Cookie Recipes" or whatever.

#### chuckles — 2026-06-06T05:07:09.708Z
@susan Open question before dispatch:

1. For the updated `draft_job_resume` contract, should required fields be **only** the candidate’s enabled non-contact section ids (strict AST-551), or should all `finalize_job_resume`-style contact/header keys remain optional pass-through on this hop?

---

_Implementation detail may live in git history on `origin/dev`._
