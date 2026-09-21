# AST-1119 — Fallback for company job id

<!-- linear-archive: AST-1119 archived 2026-08-11 -->

## Linear archive (AST-1119)

**Archived:** 2026-08-11  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1119/fallback-for-company-job-id  
**Status at archive:** Archive  
**Project:** Astral Tracker  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-497

### Description

## Purpose

When Ruth’s qualify parse omits an external job id, Astral fails the qualify content gate even though a UUID already sits in the job URL path. This epic (Astral Tracker) makes apply-time fallback explicit: prefer AI `company_job_id`, else a UUID-shaped path segment from `job_link`, so meteorite qualify can record a stable external id used by string-match dedupe and continue.

## Functional scope

* Prefer a non-empty AI-returned `company_job_id` (job external id — not company `short_name`); never overwrite a real AI value with a URL-derived fallback.
* When AI omits or returns empty `company_job_id`, derive fallback from `job_link` **only** (not company `job_site`) by extracting a **UUID-shaped** path segment from that URL — so the stored id stays safe for existing substring / pattern-match dedupe (no query junk, no arbitrary non-UUID path tails).
* Apply the resolve step **immediately before the** `qualify_meteorite` **empty-**`company_job_id` **content gate only** (Archie-confirmed quick fix — no other apply surfaces in this epic), so empty-AI + UUID-in-`job_link` jobs stop failing solely for missing id.
* When `debug=True` on that touched apply path: per job index, log what was **found** (AI vs UUID-from-`job_link` vs neither), the `job_link` used when falling back, and what was **recorded** — Style D headers and `|` detail per AST-538 / Code Rules.
* If neither AI nor a UUID path segment in `job_link` yields a usable id, keep failing that job the same way empty `company_job_id` fails today.

## Architectural definition

* **Patterns to reuse**
  * `pattern.batch.entity-claim-process-release` — fallback inside existing qualify claim/process/release apply, not a parallel ingest path.
  * `pattern.batch.entity-agent-responses` — AI value from latest RESPONSE decode; fallback is post-decode apply logic only.
  * `pattern.layers.import-discipline` — UUID-from-URL helper stays in allowed layers.
* **New patterns proposed**
  * `pattern.identity.url-uuid-path-external-id-fallback` (proposed) — when agent-omitted external job id may be recovered as a UUID path segment from `job_link`, prefer AI, else UUID segment, else fail. Archie approval before other tasks copy it. Child #1 introduces.
* **Applicable statutes**
  * `astral.standards.in-scope-only` — agreed apply surface + resolve helper only.
  * `astral.standards.no-hardcoded-sets` — UUID shape / path rules via config or shared helper constants, not ad-hoc Dice host lists unless Susan later requires host gates.
  * `astral.standards.debug-contract-gated` — found/recorded on touched `debug=` apply path.
  * `astral.standards.dry-and-focused-functions` / `astral.standards.public-then-helpers` — one resolve helper.
  * `astral.layers.import-direction` — layer law on helper placement.
  * `astral.batch.claim-process-release` / `astral.batch.entity-agent-responses-latest-only` — no reinvent claim or RESPONSE storage.

## Boundaries

* Does **not** change meteorite **create** paths that intentionally leave `company_job_id` empty until qualify ([AST-1061](https://linear.app/astralcareermatch/issue/AST-1061/gazer-email-meteorite-jobs-playwright-dedupe-qualify-meteorite) / [AST-1090](https://linear.app/astralcareermatch/issue/AST-1090/gaze-email-runner-bind-route-scrape-dedupe-create-mailbox-outcomes-add)).
* Does **not** use company `job_site` or any non-`job_link` URL for fallback (id must stay unique to the job).
* Does **not** store arbitrary last path segments or URL-decoded junk that would break `company_job_id` substring dedupe — UUID-shaped path token only.
* Does **not** retarget company PK / `short_name` ([AST-497](https://linear.app/astralcareermatch/issue/AST-497/company-pk-surrogate-key-instead-of-global-short-name-multi-candidate)).
* Does **not** add UI or prompt rewrites as the primary fix.
* Does **not** weaken identity collision rules once an id is recorded.
* Does **not** expand into `qualify_job_listings` unless Susan names it — that path has no empty-`company_job_id` content fail gate today.

## Acceptance criteria

1. Non-empty AI `company_job_id` is recorded unchanged even when `job_link` contains a different UUID path segment.
2. Empty/missing AI `company_job_id` + `job_link` containing a UUID path segment (e.g. Dice `…/company-profile/<uuid>` or a job URL with a UUID segment) records that UUID as `company_job_id` and does not hit the empty-id fail gate.
3. Empty/missing AI id + `job_link` with no UUID path segment still fails the empty-id gate (same fail kind as today).
4. With `debug=True` on the touched apply run, each job index shows found source (AI vs UUID-from-`job_link` vs neither) and recorded `company_job_id` under Style D / `|` detail.
5. Meteorite create-without-`company_job_id` behavior outside the agreed qualify apply surface is unchanged.

## Dependencies and blockers

none.

## Open questions

none.

## Proposed child tickets

#### 1!: **UUID-from-job_link company_job_id fallback before qualify empty-id gate - Ada**

Owns resolve rule (AI wins; else UUID path segment from `job_link`; else empty) and wires it immediately before the `qualify_meteorite` empty-`company_job_id` content gate only. Does **not** own create-time meteorite ingest that leaves id empty; does **not** use `job_site`. **Citations:** `pattern.batch.entity-claim-process-release`, `pattern.batch.entity-agent-responses`, proposed `pattern.identity.url-uuid-path-external-id-fallback`, `astral.standards.no-hardcoded-sets`, `astral.standards.in-scope-only`, `astral.layers.import-direction`.

#### 2: **Debug found/recorded for company_job_id resolve - Hedy**

After #1: on the touched `debug=` qualify apply path, Style D index + `|` detail for found source (AI vs UUID-from-`job_link` vs neither), `job_link` used when falling back, and recorded `company_job_id`. **Citations:** `astral.standards.debug-contract-gated`.

**New patterns:** Child #1 introduces proposed `pattern.identity.url-uuid-path-external-id-fallback` for Archie approval before reuse.

**Monolith check:** Functional scope has 5 capabilities; 2 children (resolve+wire vs debug) — intentional.

---

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| [AST-1119](https://linear.app/astralcareermatch/issue/AST-1119/fallback-for-company-job-id) (parent) | ftr/AST-1119-fallback-for-company-job-id |
| [AST-1120](https://linear.app/astralcareermatch/issue/AST-1120/uuid-from-job-link-company-job-id-fallback-before-qualify-empty-id) | sub/AST-1119/AST-1120-uuid-from-job-link-company-job-id-fallback |
| [AST-1121](https://linear.app/astralcareermatch/issue/AST-1121/debug-foundrecorded-for-company-job-id-resolve-fallback-for-company) | sub/AST-1119/AST-1121-debug-found-recorded-company-job-id-resolve |
| [AST-1127](https://linear.app/astralcareermatch/issue/AST-1127/uat-qualify-meteorite-still-fails-schema-when-company-job-id-omitted) | sub/AST-1119/AST-1127-uat-qualify-meteorite-schema-company-job-id-omitted |

**Epic worktree:** `astral-AST-1119/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **Thread** column is the fully-qualified `store.db` path (UUID is the directory name — extract for `agent --resume`). **datt resume:** read this table — not chat memory. One UUID per agent; never the parent Chuckles Thread UUID.

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | `/home/susan/.cursor/chats/3b42c17f1227be2507eadeb09fad46b8/d21f66a2-0d74-4041-97bc-0d2a9dd924d5/store.db` |
| Hedy | engineer | `/home/susan/.cursor/chats/3b42c17f1227be2507eadeb09fad46b8/f90eab36-8b3b-480e-a162-70c579942b2e/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/e1f3f94b-fd6f-486b-b65c-9c5334ff3184/store.db` |
| Radia | review | `/home/susan/.cursor/chats/3b42c17f1227be2507eadeb09fad46b8/09ef0342-01ce-41a0-aa9b-be709fb11638/store.db` |

## Original brief

Sometimes, the AI can parse a company job id, sometimes not.  If not, then use the job page name (e.g. [https://www.dice.com/company-profile/9f704ad3-7a18-506a-bd5e-6a84e73b7c00](<https://www.dice.com/company-profile/9f704ad3-7a18-506a-bd5e-6a84e73b7c00>) uses `9f704ad3-7a18-506a-bd5e-6a84e73b7c00` as the external company id if the ai agent does not return a different one.

### Comments

#### susan — 2026-08-02T22:28:31.849Z
Per-job isolation.  As long as the agent_performance was a success, you can error on individual jobs no problem.  Only when the agent_performance is failure do we want to error the whole batch.

#### chuckles — 2026-08-02T21:32:27.996Z
[fix-uat] blocked: open question — batch fail-all vs schema

@susan

**Why all 3 errored (your log):** not because jobs 001/002 lacked `job_title` / `company_job_id`. Ruth returned good titles for those two. Job `000` had `job_title: null` (bogus `https://www.w3.org/2000/svg`). `do_task` → `_validate_response_schema` still has `job_title` **required**, so `jobs[0]: Missing required field 'job_title'` fails the **entire** RESPONSE. Consult then does `do_task failed — batch error transition` and marks **every claimed job** in that batch `METEORITE_ERROR_QUALIFY` → `errors=3`. Company_job_id omit is no longer the stopper here (AST-1127 path held); this is the next required field + batch atomicity.

**Parent AC gap:** AST-1119 ACs only cover `company_job_id` resolve/debug. None say “one bad peer must not fail siblings” or “`job_title` may be null through schema.”

Which do you want as the UAT bug?

1. **Per-job isolation** — schema/`do_task` fail for one index must not error the other claimed jobs in the batch (keep good Dice rows).
2. **Schema soften** — `job_title` `required: False` (like AST-1127) so null reaches consult, and consult fails **only** the empty-title job.
3. **Both**, or **out of this epic** (file elsewhere / leave as known batch behavior).

Won’t file until you pick — filing without an AC would invent scope.

— Chuckles

#### susan — 2026-08-02T21:30:59.537Z
Okay, I get that there are issues with the bogus link, but the other two links returned job_title, so why did the whole job get 3 errors?

```
[2026-08-02 20:34:59] DEBUG src.external.deepseek:  |         "job_link": "https://www.dice.com/job-detail/3628bf85-8915-4525-93ff-2f05e09f9e39",
[2026-08-02 20:34:59] DEBUG src.external.deepseek:  |         "jd_text": "Role: Health Data Services Operations & Strategy Director\nLocation: San Francisco, CA (Hybrid – Minimum 6 days/month onsite)\nDuration: 6 Months\nSummary: The Client is seeking a Health Data Services Operations & Strategy Director to lead enterprise healthcare analytics, digital health initiatives, and data-driven transformation. The Director will oversee analytics strategy, enterprise reporting, dashboards, data governance, EHR integration, and digital health programs while managing a multidisciplinary team supporting clinical, operational, and regulatory reporting.\nMust Have: Healthcare Data Analytics, Epic EHR & Data Integration, Enterprise Reporting & Dashboard Development, Data Governance & Healthcare Compliance, Digital Health Strategy, Leadership & Team Management\nKey Responsibilities:\nLead enterprise healthcare analytics and digital transformation initiatives.\nDevelop and execute analytics strategy aligned with organizational goals.\nOversee enterprise dashboards, KPIs, reporting, and performance metrics.\nDrive data governance, data quality, and reporting standardization.\nManage EHR data integration with enterprise data warehouses.\nSupport regulatory reporting (CMS, DHCS, HCAI, California Public Hospital reporting, audits).\nCollaborate with clinical and executive leadership on quality improvement and health equity initiatives.\nManage budgets, staff, and cross-functional healthcare analytics teams.\nProvide leadership for digital health, patient engagement, and telehealth analytics.\nRequired Skills:\n7+ years of healthcare analytics, healthcare IT, or digital health experience.\n3+ years of leadership/supervisory experience managing analytics or technical teams.\nStrong healthcare analytics, enterprise reporting, and dashboard development experience.\nExperience with Epic EHR (preferred) and healthcare data interoperability.\nKnowledge of healthcare data warehousing, data governance, and privacy regulations.\nExperience with regulatory reporting (CMS, DHCS, HCAI, cost reports, audits).\nStrong understanding of healthcare quality measures and performance reporting.\nBachelor's degree in Healthcare Administration, Public Health, Data Science, Information Systems, Statistics, Business Administration, or related field (Master's preferred).\nPreferred:\nGovernment healthcare or public sector experience.\nExperience leading enterprise digital health and analytics transformation initiatives.\nExpertise in Epic HB, PB, Retail Pharmacy reporting architecture and enterprise data warehouses."
[2026-08-02 20:34:59] DEBUG src.external.deepseek:  |       },
[2026-08-02 20:34:59] DEBUG src.external.deepseek:  |       {
[2026-08-02 20:34:59] DEBUG src.external.deepseek:  |         "astral_job_id": "002",
[2026-08-02 20:34:59] DEBUG src.external.deepseek:  |         "company_job_id": "484516",
[2026-08-02 20:34:59] DEBUG src.external.deepseek:  |         "job_title": "Data Strategy / Business Analyst Consultant",
[2026-08-02 20:34:59] DEBUG src.external.deepseek:  |         "job_link": "https://www.dice.com/job-detail/eaba0d1b-5258-4843-9ddc-5487b7985338",
[2026-08-02 20:34:59] DEBUG src.external.deepseek:  |         "jd_text": "Data Strategy / Business Analyst Consultant\nDETAILS\nLocation: Remote\nPosition Type: 6-week+ Contract\nHourly / Salary: to $85W2+ (based on experience level)\nJOB SUMMARY\nVaco is currently seeking a Data Strategy / Business Analysis Consultant for an enterprise Data and AI strategy engagement. The BA will facilitate stakeholder discovery, capture business requirements, and translate workshop discussions into structured deliverables supporting enterprise data governance and Data / AI product strategies. Partnering with Data Architects, Engagement Leadership, and business stakeholders, the BA will document current-state challenges, prioritize data and AI product opportunities, and help develop a data governance framework. The role operates at the intersection of Business Analysis, Data Governance, Data Architecture, Technical Writing, and AI Enablement, requiring strong workshop facilitation, real-time documentation, business-to-technical translation, and the ability to communicate complex data concepts clearly.\nWorkshop Facilitation Support – Capturing requirements, use cases, decisions, and action items during stakeholder workshops while producing structured documentation in real time.\nBusiness Analysis / Requirements Elicitation – Conducting stakeholder interviews, documenting current-state processes, identifying pain points, and translating business needs into actionable requirements.\nTechnical Documentation – Developing business and technical deliverables including workshop summaries, use case documentation, governance artifacts, and prioritized Data / AI product recommendations.\nData Governance Support – Assisting with the development of ownership models, stewardship processes, metadata standards, and governance documentation supporting enterprise data initiatives.\nData / AI Product Definition – Helping define reusable data products and AI use cases by documenting business capabilities, data requirements, and expected outcomes.\nBusiness / Technical Translation – Bridging communication between business stakeholders and technical teams to ensure requirements, priorities, and deliverables are clearly understood and documented.\nJOB REQUIREMENTS\nBusiness Analysis – Stakeholder Interviews / Current- & Future-State Analysis / Process Mapping / Gap Analysis / Use Case Development\nWorkshop Facilitation – Facilitating Stakeholder Workshops / Real-Time Documentation / Decision Capture / Action Item Tracking\nTechnical Documentation – Business Requirements / Functional Specifications / Governance Artifacts / Executive Deliverables & Documentation\nData Governance – Data Ownership / Data Stewardship / Metadata Management / Data Quality / Governance Frameworks\nModern Data Platforms (working knowledge) – SQL / ETL / ELT / Data Modeling / Snowflake / Databricks / Cloud Platforms (AWS / Azure / Google Cloud Platform)\nData Engineering Concepts (working knowledge) – Python / dbt / Apache Airflow / Data Pipelines / Analytics Workflows\nData / AI Enablement – Data Products / AI Use Cases / Reusable Data Product Concepts / Feature Stores\nStakeholder Management / Engagement – Executive Communication / Cross-Functional Collaboration / Business-to-Technical Translation / Analytical Problem Solving"
[2026-08-02 20:34:59] DEBUG src.external.deepseek:  |       }
[2026-08-02 20:34:59] DEBUG src.external.deepseek:  |     ]
[2026-08-02 20:34:59] DEBUG src.external.deepseek:  |   }
[2026-08-02 20:34:59] DEBUG src.external.deepseek:  | }
[2026-08-02 20:34:59] DEBUG src.core.agent:  | agent_data_write block_type=SYSTEM outcome=ref_existing agent_data_id=qualify_meteorite-a59ea7fc-6bba-45d9-b74b-cd62e7cdae21-system-6115c254577f3e5f ref_agent_data_id='qualify_job_listings-b19b0d3b-c73b-4e4b-99d8-c282a16eb4e6-system-cbfb0bb55a6614f7'
[2026-08-02 20:34:59] DEBUG src.core.agent:  | agent_data_write block_type=CACHE_A outcome=ref_existing agent_data_id=qualify_meteorite-a59ea7fc-6bba-45d9-b74b-cd62e7cdae21-cache_a-b57147451be4faaf ref_agent_data_id='qualify_meteorite-d782d09b-6a43-4668-b90c-f2a9da05aa8b-cache_a-e43941a12c97756c'
[2026-08-02 20:34:59] DEBUG src.core.agent:  | agent_data_write block_type=NO_CACHE outcome=ref_existing agent_data_id=qualify_meteorite-a59ea7fc-6bba-45d9-b74b-cd62e7cdae21-no_cache-9e689b6afcd9d9e8 ref_agent_data_id='qualify_meteorite-fbc8d617-99bd-4e81-896f-4cd0df2db757-no_cache-fbc6c3482e7db267'
[2026-08-02 20:34:59] DEBUG src.core.agent:  | agent_data_write block_type=TASK outcome=ref_existing agent_data_id=qualify_meteorite-a59ea7fc-6bba-45d9-b74b-cd62e7cdae21-task-a974c9998275959c ref_agent_data_id='qualify_meteorite-d782d09b-6a43-4668-b90c-f2a9da05aa8b-task-2f07e0975a79d12b'
[2026-08-02 20:34:59] DEBUG src.core.agent:  | raw_response task_key=qualify_meteorite lines=30 chars=6620
[2026-08-02 20:34:59] DEBUG src.core.agent:  | {
[2026-08-02 20:34:59] DEBUG src.core.agent:  |   "agent_performance": {
[2026-08-02 20:34:59] DEBUG src.core.agent:  |     "status": "success"
[2026-08-02 20:34:59] DEBUG src.core.agent:  |   },
[2026-08-02 20:34:59] DEBUG src.core.agent:  |   "agent_payload": {
[2026-08-02 20:34:59] DEBUG src.core.agent:  |     "jobs": [
[2026-08-02 20:34:59] DEBUG src.core.agent:  |       {
[2026-08-02 20:34:59] DEBUG src.core.agent:  |         "astral_job_id": "000",
[2026-08-02 20:34:59] DEBUG src.core.agent:  |         "company_job_id": null,
[2026-08-02 20:34:59] DEBUG src.core.agent:  |         "job_title": null,
[2026-08-02 20:34:59] DEBUG src.core.agent:  |         "job_link": "https://www.w3.org/2000/svg",
[2026-08-02 20:34:59] DEBUG src.core.agent:  |         "jd_text": null
[2026-08-02 20:34:59] DEBUG src.core.agent:  |       },
[2026-08-02 20:34:59] DEBUG src.core.agent:  |       {
[2026-08-02 20:34:59] DEBUG src.core.agent:  |         "astral_job_id": "001",
[2026-08-02 20:34:59] DEBUG src.core.agent:  |         "company_job_id": "9039489",
[2026-08-02 20:34:59] DEBUG src.core.agent:  |         "job_title": "Health Data Services Operations & Strategy Director",
[2026-08-02 20:34:59] DEBUG src.core.agent:  |         "job_link": "https://www.dice.com/job-detail/3628bf85-8915-4525-93ff-2f05e09f9e39",
[2026-08-02 20:34:59] DEBUG src.core.agent:  |         "jd_text": "Role: Health Data Services Operations & Strategy Director\nLocation: San Francisco, CA (Hybrid – Minimum 6 days/month onsite)\nDuration: 6 Months\nSummary: The Client is seeking a Health Data Services Operations & Strategy Director to lead enterprise healthcare analytics, digital health initiatives, and data-driven transformation. The Director will oversee analytics strategy, enterprise reporting, dashboards, data governance, EHR integration, and digital health programs while managing a multidisciplinary team supporting clinical, operational, and regulatory reporting.\nMust Have: Healthcare Data Analytics, Epic EHR & Data Integration, Enterprise Reporting & Dashboard Development, Data Governance & Healthcare Compliance, Digital Health Strategy, Leadership & Team Management\nKey Responsibilities:\nLead enterprise healthcare analytics and digital transformation initiatives.\nDevelop and execute analytics strategy aligned with organizational goals.\nOversee enterprise dashboards, KPIs, reporting, and performance metrics.\nDrive data governance, data quality, and reporting standardization.\nManage EHR data integration with enterprise data warehouses.\nSupport regulatory reporting (CMS, DHCS, HCAI, California Public Hospital reporting, audits).\nCollaborate with clinical and executive leadership on quality improvement and health equity initiatives.\nManage budgets, staff, and cross-functional healthcare analytics teams.\nProvide leadership for digital health, patient engagement, and telehealth analytics.\nRequired Skills:\n7+ years of healthcare analytics, healthcare IT, or digital health experience.\n3+ years of leadership/supervisory experience managing analytics or technical teams.\nStrong healthcare analytics, enterprise reporting, and dashboard development experience.\nExperience with Epic EHR (preferred) and healthcare data interoperability.\nKnowledge of healthcare data warehousing, data governance, and privacy regulations.\nExperience with regulatory reporting (CMS, DHCS, HCAI, cost reports, audits).\nStrong understanding of healthcare quality measures and performance reporting.\nBachelor's degree in Healthcare Administration, Public Health, Data Science, Information Systems, Statistics, Business Administration, or related field (Master's preferred).\nPreferred:\nGovernment healthcare or public sector experience.\nExperience leading enterprise digital health and analytics transformation initiatives.\nExpertise in Epic HB, PB, Retail Pharmacy reporting architecture and enterprise data warehouses."
[2026-08-02 20:34:59] DEBUG src.core.agent:  |       },
[2026-08-02 20:34:59] DEBUG src.core.agent:  |       {
[2026-08-02 20:34:59] DEBUG src.core.agent:  |         "astral_job_id": "002",
[2026-08-02 20:34:59] DEBUG src.core.agent:  |         "company_job_id": "484516",
[2026-08-02 20:34:59] DEBUG src.core.agent:  |         "job_title": "Data Strategy / Business Analyst Consultant",
[2026-08-02 20:34:59] DEBUG src.core.agent:  |         "job_link": "https://www.dice.com/job-detail/eaba0d1b-5258-4843-9ddc-5487b7985338",
[2026-08-02 20:34:59] DEBUG src.core.agent:  |         "jd_text": "Data Strategy / Business Analyst Consultant\nDETAILS\nLocation: Remote\nPosition Type: 6-week+ Contract\nHourly / Salary: to $85W2+ (based on experience level)\nJOB SUMMARY\nVaco is currently seeking a Data Strategy / Business Analysis Consultant for an enterprise Data and AI strategy engagement. The BA will facilitate stakeholder discovery, capture business requirements, and translate workshop discussions into structured deliverables supporting enterprise data governance and Data / AI product strategies. Partnering with Data Architects, Engagement Leadership, and business stakeholders, the BA will document current-state challenges, prioritize data and AI product opportunities, and help develop a data governance framework. The role operates at the intersection of Business Analysis, Data Governance, Data Architecture, Technical Writing, and AI Enablement, requiring strong workshop facilitation, real-time documentation, business-to-technical translation, and the ability to communicate complex data concepts clearly.\nWorkshop Facilitation Support – Capturing requirements, use cases, decisions, and action items during stakeholder workshops while producing structured documentation in real time.\nBusiness Analysis / Requirements Elicitation – Conducting stakeholder interviews, documenting current-state processes, identifying pain points, and translating business needs into actionable requirements.\nTechnical Documentation – Developing business and technical deliverables including workshop summaries, use case documentation, governance artifacts, and prioritized Data / AI product recommendations.\nData Governance Support – Assisting with the development of ownership models, stewardship processes, metadata standards, and governance documentation supporting enterprise data initiatives.\nData / AI Product Definition – Helping define reusable data products and AI use cases by documenting business capabilities, data requirements, and expected outcomes.\nBusiness / Technical Translation – Bridging communication between business stakeholders and technical teams to ensure requirements, priorities, and deliverables are clearly understood and documented.\nJOB REQUIREMENTS\nBusiness Analysis – Stakeholder Interviews / Current- & Future-State Analysis / Process Mapping / Gap Analysis / Use Case Development\nWorkshop Facilitation – Facilitating Stakeholder Workshops / Real-Time Documentation / Decision Capture / Action Item Tracking\nTechnical Documentation – Business Requirements / Functional Specifications / Governance Artifacts / Executive Deliverables & Documentation\nData Governance – Data Ownership / Data Stewardship / Metadata Management / Data Quality / Governance Frameworks\nModern Data Platforms (working knowledge) – SQL / ETL / ELT / Data Modeling / Snowflake / Databricks / Cloud Platforms (AWS / Azure / Google Cloud Platform)\nData Engineering Concepts (working knowledge) – Python / dbt / Apache Airflow / Data Pipelines / Analytics Workflows\nData / AI Enablement – Data Products / AI Use Cases / Reusable Data Product Concepts / Feature Stores\nStakeholder Management / Engagement – Executive Communication / Cross-Functional Collaboration / Business-to-Technical Translation / Analytical Problem Solving"
[2026-08-02 20:34:59] DEBUG src.core.agent:  |       }
[2026-08-02 20:34:59] DEBUG src.core.agent:  |     ]
[2026-08-02 20:34:59] DEBUG src.core.agent:  |   }
[2026-08-02 20:34:59] DEBUG src.core.agent:  | }
[2026-08-02 20:34:59] ERROR src.core.agent: do_task validation failed. task_key='qualify_meteorite' error=jobs[0]: Missing required field 'job_title'
[2026-08-02 20:34:59] DEBUG src.core.agent:  | agent_data_write block_type=RESPONSE outcome=new_content agent_data_id=qualify_meteorite-a59ea7fc-6bba-45d9-b74b-cd62e7cdae21-response-ca02eaeefd9589d0 ref_agent_data_id=None
[2026-08-02 20:34:59] DEBUG src.core.consult: consult._run_batch_consult(qualify_meteorite) index 1/1 qualify_meteorite -> do_task failed — batch error transition
[2026-08-02 20:34:59] DEBUG src.core.consult:  | error="jobs[0]: Missing required field 'job_title'" error_state='METEORITE_ERROR_QUALIFY'
[2026-08-02 20:34:59] DEBUG src.core.dispatcher:  | batch end summary={'total_processed': 3, 'total_passed': 0, 'total_failed': 0, 'total_errors': 3}
[2026-08-02 20:34:59] DEBUG src.core.dispatcher:  | runner returned summary={'total_processed': 3, 'total_passed': 0, 'total_failed': 0, 'total_errors': 3}
[2026-08-02 20:34:59] DEBUG src.core.dispatcher:  | iteration 1 summary processed=3 passed=0 failed=0 errors=3 accumulated={'total_processed': 3, 'total_passed': 0, 'total_failed': 0, 'total_errors': 3}
[2026-08-02 20:34:59] DEBUG src.core.dispatcher:  | loop stop: max_runs reached max_runs=1 run_count=1
[2026-08-02 20:34:59] WARNING src.core.dispatcher: [qualify_meteorite/qualify_meteorite-a59ea7fc-6bba-45d9-b74b-cd62e7cdae21] batch finished COMPLETED with errors — processed=3 passed=0 failed=0 errors=3
[2026-08-02 20:34:58] DEBUG src.core.dispatcher: dispatcher._run_task index 1/1 qualify_meteorite -> running batch
[2026-08-02 20:34:58] DEBUG src.core.dispatcher:  | batch_size=30 batch_id=qualify_meteorite-a59ea7fc-6bba-45d9-b74b-cd62e7cdae21 entity_type='job' trigger_state='METEORITE_NEW'
[2026-08-02 20:34:58] DEBUG src.core.dispatcher: dispatcher._run_unified index 1/1 job/METEORITE_NEW -> claimed 3 entity/entities
[2026-08-02 20:34:58] DEBUG src.core.dispatcher:  | task_key=qualify_meteorite batch_id=qualify_meteorite-a59ea7fc-6bba-45d9-b74b-cd62e7cdae21 batch_call_mode=True dispatch batch_size=30 claim_cap=3 claim_states=['METEORITE_NEW']
[2026-08-02 20:34:58] DEBUG src.core.dispatcher: dispatcher._run_unified index 1/3 db9d1e10-51a2-42a2-b67d-c9878fc826dc -> claimed
[2026-08-02 20:34:58] DEBUG src.core.dispatcher:  | entity_type=job trigger_state=METEORITE_NEW state='METEORITE_NEW'
[2026-08-02 20:34:58] DEBUG src.core.dispatcher: dispatcher._run_unified index 2/3 b5c0af45-eac6-4c7f-8219-63b439edf3c3 -> claimed
[2026-08-02 20:34:58] DEBUG src.core.dispatcher:  | entity_type=job trigger_state=METEORITE_NEW state='METEORITE_NEW'
[2026-08-02 20:34:58] DEBUG src.core.dispatcher: dispatcher._run_unified index 3/3 925f25fc-3f89-440b-975a-3cf37610ec53 -> claimed
[2026-08-02 20:34:58] DEBUG src.core.dispatcher:  | entity_type=job trigger_state=METEORITE_NEW state='METEORITE_NEW'
[2026-08-02 20:34:58] DEBUG src.core.consult:  | qualify_meteorite batch_id=qualify_meteorite-a59ea7fc-6bba-45d9-b74b-cd62e7cdae21 job_count=3
[2026-08-02 20:34:58] DEBUG src.core.consult: consult.qualify_meteorite index 1/3 db9d1e10-51a2-42a2-b67d-c9878fc826dc -> input job
[2026-08-02 20:34:58] DEBUG src.core.consult:  | job_link='https://www.w3.org/2000/svg' job_description_chars=737
[2026-08-02 20:34:58] DEBUG src.core.consult: consult.qualify_meteorite index 2/3 b5c0af45-eac6-4c7f-8219-63b439edf3c3 -> input job
[2026-08-02 20:34:58] DEBUG src.core.consult:  | job_link='https://www.dice.com/job-detail/3628bf85-8915-4525-93ff-2f05e09f9e39' job_description_chars=4329
[2026-08-02 20:34:58] DEBUG src.core.consult: consult.qualify_meteorite index 3/3 925f25fc-3f89-440b-975a-3cf37610ec53 -> input job
[2026-08-02 20:34:58] DEBUG src.core.consult:  | job_link='https://www.dice.com/job-detail/eaba0d1b-5258-4843-9ddc-5487b7985338' job_description_chars=5165
[2026-08-02 20:34:58] DEBUG src.core.consult: consult._run_batch_consult(qualify_meteorite) index 1/1 qualify_meteorite -> batch start n=3
[2026-08-02 20:34:58] DEBUG src.core.consult:  | batch_id=qualify_meteorite-a59ea7fc-6bba-45d9-b74b-cd62e7cdae21 batch_states=['METEORITE_NEW'] batch_chunk_index=None astral_ids=['db9d1e10-51a2-42a2-b67d-c9878fc826dc', 'b5c0af45-eac6-4c7f-8219-63b439edf3c3', '925f25fc-3f89-440b-975a-3cf37610ec53']
[2026-08-02 20:34:58] INFO src.core.agent: run_next chain entry: task=qualify_meteorite batch_id=qualify_meteorite-a59ea7fc-6bba-45d9-b74b-cd62e7cdae21
[2026-08-02 20:34:58] DEBUG src.core.agent: do_task index 1/1 qualify_meteorite_batch_qualify_meteorite-a59ea7fc-6bba-45d9-b74b-cd62e7cdae21 -> task start
[2026-08-02 20:34:58] DEBUG src.core.agent:  | task_key=qualify_meteorite batch_id=qualify_meteorite-a59ea7fc-6bba-45d9-b74b-cd62e7cdae21 index=qualify_meteorite_batch_qualify_meteorite-a59ea7fc-6bba-45d9-b74b-cd62e7cdae21 in_run_next_chain=False
[2026-08-02 20:34:58] INFO src.core.agent: [DEBUG] do_task('qualify_meteorite'): brain_setting=Little provider=deepseek model=deepseek-v4-flash max_tokens=8192 temp=0.3 skip_cache=False candidate=somerset
[2026-08-02 20:34:58] DEBUG src.core.agent:  | llm_params provider=deepseek brain_setting=Little model=deepseek-v4-flash max_tokens=8192 temp=0.3 skip_cache=False candidate_id=somerset
[2026-08-02 20:34:58] DEBUG src.core.agent:  | blocks system=2 user=2 runtime_prompt_segments=4
[2026-08-02 20:34:58] INFO src.external.deepseek: LLM deepseek task=qualify_meteorite 7.7s stop=end_turn tokens in=1255 out=1268
[2026-08-02 20:34:58] DEBUG src.external.deepseek: send_to_deepseek index 1/1 qualify_meteorite -> success
[2026-08-02 20:34:58] DEBUG src.external.deepseek:  | provider=deepseek model=deepseek-v4-flash task=qualify_meteorite duration=7.7s stop_reason=end_turn
[2026-08-02 20:34:58] DEBUG src.external.deepseek:  | vendor=deepseek-v4-flash tokens fresh=1255 cache_read=1280 cache_write=0 output=1268
[2026-08-02 20:34:58] DEBUG src.external.deepseek:  | response_preview:
[2026-08-02 20:34:58] DEBUG src.external.deepseek:  | {
[2026-08-02 20:34:58] DEBUG src.external.deepseek:  |   "agent_performance": {
[2026-08-02 20:34:58] DEBUG src.external.deepseek:  |     "status": "success"
[2026-08-02 20:34:58] DEBUG src.external.deepseek:  |   },
[2026-08-02 20:34:58] DEBUG src.external.deepseek:  |   "agent_payload": {
[2026-08-02 20:34:58] DEBUG src.external.deepseek:  |     "jobs": [
[2026-08-02 20:34:58] DEBUG src.external.deepseek:  |       {
[2026-08-02 20:34:58] DEBUG src.external.deepseek:  |         "astral_job_id": "000",
[2026-08-02 20:34:58] DEBUG src.external.deepseek:  |         "company_job_id": null,
[2026-08-02 20:34:58] DEBUG src.external.deepseek:  |         "job_title": null,
[2026-08-02 20:34:58] DEBUG src.external.deepseek:  |         "job_link": "https://www.w3.org/2000/svg",
[2026-08-02 20:34:58] DEBUG src.external.deepseek:  |         "jd_text": null
[2026-08-02 20:34:58] DEBUG src.external.deepseek:  |       },
[2026-08-02 20:34:58] DEBUG src.external.deepseek:  |       {
[2026-08-02 20:34:58] DEBUG src.external.deepseek:  |         "astral_job_id": "001",
[2026-08-02 20:34:58] DEBUG src.external.deepseek:  |         "company_job_id": "9039489",
[2026-08-02 20:34:58] DEBUG src.external.deepseek:  |         "job_title": "Health Data Services Operations & Strategy Director",
[2026-08-02 20:34:50] INFO dispatch.scheduler: Dispatching qualify_meteorite — 3 available, batch qualify_meteorite-a59ea7fc-6bba-45d9-b74b-cd62e7cdae21
[2026-08-02 20:34:50] DEBUG src.core.dispatcher: dispatcher._run_dispatch_loop index 1/1 qualify_meteorite -> loop iteration 1 starting
[2026-08-02 20:34:50] DEBUG src.core.dispatcher:  | available=3 effective_min=1 max_runs=1 draining=False entity_batch_id=qualify_meteorite-a59ea7fc-6bba-45d9-b74b-cd62e7cdae21
```

#### chuckles — 2026-08-02T19:00:40.247Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-1127** | qualify_meteorite still fails schema when company_job_id omitted |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-1127** — _qualify_meteorite still fails schema when company_job_id omitted_
- **Issue reported:** `qualify_meteorite` still dies in agent RESPONSE validation when Ruth omits `company_job_id`:
- **Should now:** When AI omits or returns empty/`null` `company_job_id` and `job_link` has a UUID path segment, qualify records that UUID as `company_job_id` and continues (does not fail with Missing required field / empty-id solely for missing AI id).
- **Quick check (this fix only):**
  1. Run `qualify_meteorite` on a meteorite job whose Ruth RESPONSE omits `company_job_id` (or sets it null) but includes an http `job_link` with a UUID path segment (e.g. Dice-style `…/<uuid>`).
  2. Observe `do_task validation failed … Missing required field 'company_job_id'` — task never reaches consult resolve.
  3. Confirm a RESPONSE with `company_job_id: ""` would have reached consult fallback, but omit/`null` does not.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-08-02T18:46:34.288Z
Okay, please issue the CORRECT UAT issue for this, let's get it fixed up.

#### chuckles — 2026-08-02T18:24:18.613Z
[check-linear] answered — yes, wrong gate prioritized

Honest: when you asked where validation fails, I found **two** stops and still shipped the wrong one.

1. **Consult content gate** (`qualify_meteorite` process: empty/`""` → fail_state) — what we wired.
2. **Agent RESPONSE schema** — `do_task` → `_validate_response_schema` against `TASK_CONFIG["qualify_meteorite"]["response_schema"]` where `company_job_id` is `required: True`. Absent/`null` → `Missing required field` and the task dies **before** consult runs. Your log line is this path.

I called out schema vs empty-string in the define comment, then asked you to confirm the content-gate wire as the “quick fix,” and we treated that as enough. That was the miss: for Ruth **omitting** the key, the schema gate is the one that matters; content-gate fallback is only useful after the object already passes schema (e.g. `""`).

**What we should have done instead:** make schema allow omit/`null` for `company_job_id` (`required: False`) **and** keep (or add) resolve from `job_link` in consult — or fill from `job_link` **before** `_validate_response_schema`. Content-gate-only was never going to catch this failure mode.

No code changed this pass — say the word when you want a Bug/child filed.

— Chuckles

#### susan — 2026-08-02T18:22:57.060Z
@chuckles So we put the code where it would be pointless.  When I asked where the validation was happening, did you only find one (in qualify_meteorite) and assume that was the only one?  Where does the validator run?  In short, what should we have done instead, because we just wasted an hour of processing time to NOT fix a bug.\\

#### chuckles — 2026-08-02T18:14:20.995Z
[check-linear] answered — schema fails before consult fallback

The ERROR is from **agent RESPONSE schema validation** (`do_task validation failed … Missing required field 'company_job_id'`), not from the consult empty-id content gate we fixed.

What shipped: fallback runs in `qualify_meteorite` **process** after decode — AI wins, else UUID from `job_link`, else `empty company_job_id` fail. That only runs when the job object already got past schema.

What we missed: `qualify_meteorite` schema still has `company_job_id` **required: True**. Validator treats **absent/`null`** as missing and aborts the whole task **before** consult apply. Empty string `""` would reach the fallback; omitted key does not.

So Ruth returning no `company_job_id` key never hits UUID-from-`job_link`. Next fix (when you want code) is earlier than the content gate — allow omit/`null` through schema (or fill from `job_link` before validate) so process can resolve.

— Chuckles

#### susan — 2026-08-02T18:13:18.612Z
The validation is still failing:

\[2026-08-02 18:11:23\] ERROR src.core.agent: do_task validation failed. task_key='qualify_meteorite' error=jobs\[0\]: Missing required field 'company_job_id'

@chuckles Do NOT change the codebase yet, but explain to me why the original fix did not resolve this issue.  What did we miss?

#### chuckles — 2026-08-02T17:30:46.062Z
[thread-missing] Cursor chat for **Hedy** · engineer had no local `store.db` on **chuckles** (prior Team UUID `549eab88-ef9a-4277-8310-757c423442e5`). Bound to existing epic-workspace chat `cf012818-64f1-43ca-903a-197d60c2b8d9` and continuing.

— Chuckles

#### chuckles — 2026-08-02T17:04:33.225Z
@susan

1. Validation today: consult `qualify_meteorite` process content gate — empty `company_job_id` → fail_state. Schema requires the field key, but `""` still reaches that gate (`null`/absent fails schema earlier). `qualify_job_listings` has no empty-id content gate.
2. Confirm wire UUID-from-`job_link` fallback immediately before that `qualify_meteorite` gate only?

— Chuckles

#### chuckles — 2026-08-02T16:55:04.575Z
@susan

1. Which Linear project owns AST-1119 (none set today): Astral Meteorite, Astral Tracker, Astral Roster, or other?
2. Confirm stored field is job.`company_job_id` (not a company-row identifier) despite the Dice company-profile example / “external company id” wording.
3. Fallback URL source: `job_link`, company `job_site`, or both (which wins)?
4. Which apply surfaces in this epic: `qualify_meteorite` only, `parse_job_list` / listing ingest, all `initialize_job` agent-meta paths, or a named subset?
5. Host scope: any http(s) job URL last path segment, or only configured hosts/path prefixes?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
