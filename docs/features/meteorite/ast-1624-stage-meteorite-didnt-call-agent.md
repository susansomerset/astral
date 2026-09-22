# AST-1624 — Stage_meteorite didn’t call agent

<!-- linear-archive: AST-1624 archived 2026-09-22 -->

## Linear archive (AST-1624)

**Archived:** 2026-09-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1624/stage-meteorite-didnt-call-agent  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** susan  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## As-is

The dump in this ticket shows `meteorite` rows already at `READY` with a valid Ruth classify literal (`classify_outcome=single_jd_no_link`) and full JD `content`. That is the **intended** post-classify transition path (AST-1560): dispatch `stage_meteorite` / `run_stage_meteorite` only moves NEW → READY|SCRAPE_LINK from an **already-written** `classify_outcome` — it never calls Ruth, so Scheduled Actions / dispatch logs for that task_key have no agent prompt by design. Looking there for `stage_meteorite` agent content will always look empty; that emptiness alone does not prove classify never ran. The dump itself is consistent with classify having already succeeded earlier on the inbox ingest path (`invoke_stage_meteorite` → `do_task`).

## To-be

No product change for “make dispatch `stage_meteorite` call the agent.” Operators (and this ticket’s diagnosis) treat Ruth classify and the dispatch transition as two different hops: audit classify via agent_data / inbox classify monitoring for the ingest batch; expect the dispatch runner to stay agent-silent. Only if agent_data for the Ruth hop is **verified empty** while these rows still carry `classify_outcome` would that become a separate persist/audit bug — the row dump here does not show that.

## Proposed steps

1. Treat the stated symptom (“dispatch / stage_meteorite didn’t call agent, but rows are READY”) as **not a bug** — matches AST-1527/1530/1560 split-by-design.
2. Optional sanity only if still worried: look up agent_data for `task_key=stage_meteorite` around the ingest/`state_changed_at` window for these `source_id`s. Empty there → file a **new** persist/audit bug (not “dispatch should call Ruth”). Present there → close this ticket.
3. Cancel or Archive AST-1624 once Susan agrees (no fix child, no git seed).

## Component scope

* none — no product files for the stated symptom; this is diagnosis/ops clarification only. If a follow-on persist bug is confirmed, scope that ticket separately (likely `src/core/consult.py` / `src/core/agent.py` / `data/admin/agent_task.json`), not this one.

## Technical scope

* none — no function/table changes for AST-1624 under the current reading. A confirmed missing agent_data trail would be a different ticket’s technical scope.

## Ancestor candidates

- [ ] no ancestor candidate found
- [ ] AST-1559 — check_inbox + monitoring log (only if a follow-on confirms Ruth classify ran without durable agent_data / monitoring)
- [ ] AST-1448 — Persist prompt before provider (same follow-on: agent ran, prompts missing)
- [ ] AST-1560 — stage/scrape/land transitions (reference only — explains why dispatch stage is agent-silent by design; not a fix ancestor for “make it call Ruth”)
- [ ] AST-1555 — Meteorite ingress staging table parent (reference)
- [ ] AST-1530 — Core stage scrap land / `invoke_stage_meteorite` (reference)
- [ ] AST-1527 — Generalize Meteorite Ingress Point (reference)
- [ ] AST-1529 — stage_meteorite catalog (reference)

## Original report

There are no logs or agent prompt content for stage_meteorite, but all the new states are now ready.

```
[
  {
    "astral_job_id": null,
    "batch_created_at": null,
    "batch_id": null,
    "candidate_id": "somerset",
    "classify_outcome": "single_jd_no_link",
    "content": "Job Title: BEST Program Technical Operations Lead\nLocation: Boston, MA (4 Days in a Month)\nDuration: 6 Months (Possible Extension)\n\nPosition Summary\nThe BEST Program Technical Operations Lead will work for the BEST Solution Technical Lead and Deputy Program Manager to oversee and coordinate the adoption of the future state operational protocols. Together with the PMO and Phase 2 Technical Lead, Product Vendor Systems Integrator (SI), Office of the Comptroller and Executive Office of Technology Services and Security (EOTSS) staff, the BEST Program Technical Operations Lead will be responsible for tasks related to planning, approach, align, and oversee the implementation of the operational solution across the Commonwealth and product vendor areas of responsibility.\n\nThe BEST Program Technical Operations Lead will join the BEST technical leadership team which includes: BEST Solution Technical Lead, BEST Phase 2 Technical Lead, BEST Technical Testing and Quality Assurance Lead, BEST Technical Security Lead, and BEST Technical Reporting Lead. Furthermore, this position will partner with and work across BEST PMO, SI, Product Vendor, EOTSS, CTR, HRD, ANF, and Departments to ensure deliverable quality and identify the necessary and optimal operational business solution.\n\nThe BEST Program Technical Operations Lead will:\n- Align with Comptroller Technical Group (CTG) leadership, CTR Organizational leadership, Sponsor Organization technical leadership, BEST Architecture Review Board (ARB), and BEST Phase 2 Technical Lead to establish a future operations framework and operational model and define future state solution operational roles and responsibilities for the technical adoption and operational execution of the Phase 2 business solution.\n- Engage Commonwealth Department Information Technology (IT) organizations or IT representatives that support approximately 160 departments to ensure the future operational solution will be implemented within departments, operate as desired as defined by the business, and will support local department operational and compliance needs. This position will be accountable to communicate and facilitate with the IT department representatives on their local technology needs, track and manage local department IT needs / issues, facilitate overall department testing of business solution, verify department users have necessary access, manage approvals for department implementations, align with security and risk teams to ensure appropriate and proper access levels are enabled, and be the BEST contact to oversee the local resolution to department operational issues.\n  - Where departments have an existing system today that performs a similar business function, these existing systems may or may not continue after implementation of the Phase 2 BEST solution. This role will coordinate with departments to establish necessary technical plans, such as (but not limited to):\n    - For local full adoption of the BEST new solution:\n      - existing system shutdown and retirement plans, existing system data conversion plans, user security migration plans, and other\n    - For local retention of existing system (full or part) aligned with the BEST new solution:\n      - data integration plans, compliance plans, or other.\n  - Coordinate testing and approval of department IT solution with the new HR/Payroll solution including user access, local IT operations plans and staffing, local IT compliance needs, and other needs.\n- Work side by side with Comptroller Technical Group (CTG) leadership, Commonwealth staff, solution SI, and solution SaaS vendor to establish the overall operational solution model, to identify and recommend future state operational needs, recommend future state roles and responsibilities, and will be responsible for oversight of specific operational deliverables provided by the SI and Product vendors during the project period with transition planning to CMW staff post go-live and warranty period.\n- These include upgrades, defect fixes by the product vendor, implementation of penalties for Service Level Agreement ( SLA) failures or breaches, m onitoring SLA metrics for software, support, and maintenance services, and implementation of on-going configuration changes.\n- Work with BEST and CTR security and risk teams to communicate local IT department security and compliance requirements, as well as review local department implementation plans for security and compliance.\n- Work with BEST Quality Assurance and Testing team to define, communicate, and oversee testing within Departments.\n- Align with BEST Program business contacts to ensure the most current and appropriate business solution is understood and identity potential needs / issues with department operational needs and operational metrics.\n- Develop implementation plans with BEST program leadership to ensure department IT adoption, communications, coordination, and testing to support departments' implementation of the Phase 2 business solution.\n- Support BEST Solution Technical Lead to engage the BEST Architecture Review Board (ARB) as requested, providing information on department technical needs / issues. BEST Phase 2 Operational lead will communicate ARB decisions to departments.\n- Be responsible for additional BEST program delivery tasks including:\n  - BEST technical environment management\n  - Assist in the technical implementation of Help Desk to enable Hypercare Support Delivery during initial states of operations.\n  - Determine the timing and procedures for adopting SaaS solution upgrades and required system maintenance\n  - Establish appropriate monitoring functions and operational SLAs to ensure a quality operational environment, including operational support tasks, local IT operational support tasks, alignment of data backups, and other related tools.\n  - Assist BEST Compliance team in implementing the procedures to meet risk mitigation requirements and to monitor vendor compliance with security protocols.\n  - Maintain awareness and communicate status of data within each environment\n- Exhibit excellent verbal and written communication and interpersonal skills, including an excellent customer service attitude.\n- Communicate progress, risks, and potential changes in scope to the BEST Solution Technical Lead, BEST Program Director, and BEST Phase 2 Technical Lead.\n- Work closely with BEST Phase 2 Technical Lead to engage EOTSS operational solution to clarify existing roles and responsibilities, operational details, and identification of known department needs and issues.\n- Act as a liaison between incident response leads and subject matter experts and monitor daily or weekly reports and operational logs for unusual events\n\nThe BEST Program Technical Operations Lead will partner with the product vendor and SI vendor who will also provide staff and have significant responsibilities per the vendor and Commonwealth's Statement of Work to:\n- Support the generation and approval of technical operational artifacts and deliverables.\n- Assist coordination in the transition of legacy data contained within local IT system(s) or department server(s) into the new solution, as necessary.\n\nSpecific Duties\n- Manage the planning, delivery, and implementation of work products, as defined in the SOW, that will be provided by the product vendor and SI vendor to ensure a successful outcome of operational execution. This will include resource planning and management; maintenance of vendor performance metrics and progress, tracking of issues and risk; and review of deliverables by product vendor and SI vendor.\n- Conduct regular meetings with Department Local IT representatives to communicate BEST Phase 2 plans, decisions, and information needs, as well as capture local IT specific needs and issues.\n- Communicate progress, risks, and potential changes in scope to the BEST Solution Technical Lead and Phase 2 Technical Lead.\n- Work with business owners, BEST program resources, and departments to understand the changing business needs served by the new system and the change management needed to arrive at the future state for operating the new solution.\n- Participate in testing, including quality assurance testing, business process solution testing, integrated system test (IST), user acceptance testing (UAT) and end to end testing activities and deliverables throughout the project period.\n- Participate in Product vendor testing, such as performance, penetration, disaster recovery and integration testing to meet requirements for volume, performance, and security.\n- Ensure that appropriate deliverables fulfill the business requirements of the project and recommend procedures and tools for troubleshooting software issues, applying patches, dealing with exceptions, and escalating problems.\n- Where needed, provide recommend software support needs that could be met by a third-party vendor or by the SI or product vendor if such tasks cannot be supported by Commonwealth in-house staff.\n- Support BEST Phase 2 Technical lead as needed to assess the results of product vendor audits or audits performed by third parties to produce recommendations of acceptable risks and risk mitigation strategies. Provide recommendations regarding audit finding remediation, including providing feedback and suggestions on managerial responses to findings, tracking progress and providing status and updates.\n\nRequired Skills\n- Extensive technical knowledge and experiences that operated in various operational settings, including but not limited to: Software as a Services (SaaS), relational database structures, Structured Query Language (SQL), and others.\n- Experience in Technical Leadership roles and decision making.\n- Extensive experience with system administration and monitoring for various application platforms particularly SaaS delivery models and all phases of testing including unit, system, integration, parallel and user acceptance.\n- Experienced with LAN/WAN/VPN and remote network technologies and protocols (such as, but not limited to, TCP/IP, HTTP, FTP, Ethernet, token ring, ARCNET, HTML CGI, ATM, CDPD), as well as experience with network infrastructure, including routers, switches, firewalls, and the associated network protocols and concepts.\n- Experience with common information security management frameworks, such as International Organization for Standardization (ISO) 2700x, ITIL, National Institute of Standards and Technology (NIST), and others.\n- Ability to analyze and communicate project risks and challenges and drive resolution.\n- Problem-solving, negotiation and decision-making skills.\n- Leadership and effectiveness in matrix management and team building.\n- Understanding of the relationship between systems architecture and business use cases.\n\nPreferred Qualifications\nExperience with Software as a Service (SaaS) cloud implementations particularly those in which legacy on premise applications have been migrated to cloud delivery options.\n- In depth experience and exposure to multiple, diverse technical configurations, technologies, and processing environments in at least one project of similar size and complexity to the BEST Program in which the candidate led data integration, system operations, and security protocols to a successful conclusion.\n- Extensive experience in Project Plan development, delivery oversight, and status reporting.\n- Demonstrated experience in development and delivery of Executive status reports and communications.\n- Experience in implementation of Data Quality programs\n- Experience in performing or supporting a system audit within a state government.\n- Experience with state government implementation and operations, preference given to individuals with Commonwealth of Mass specific experience.\n\nMinimum Entrance Requirements\n- Bachelor's degree in computer science, system analysis or a related study/equivalent experience.\n- Minimum of ten years of design and implementation experience in IT, with a deep knowledge in the following technical disciplines: application development, application programming interfaces (APIs), audit compliance, database management, infrastructure and network design, middleware, security risk and compliance management, and servers and storage.",
    "created_at": "2026-09-09 23:27:58",
    "error": null,
    "estelle_notified_at": null,
    "estelle_thread_ts": null,
    "id": 1,
    "link": null,
    "nag_count": 0,
    "source_id": "1a0883ac62715a20",
    "source_kind": "email",
    "source_ref": null,
    "state": "READY",
    "state_changed_at": "2026-09-10 03:02:40",
    "updated_at": "2026-09-10 03:02:40"
  },
  {
    "astral_job_id": null,
    "batch_created_at": null,
    "batch_id": null,
    "candidate_id": "somerset",
    "classify_outcome": "single_jd_no_link",
    "content": "Program Manager opportunity in Rancho Cordova, CA. This role focuses on driving program governance, talent acquisition initiatives, and ensuring clarity of responsibilities through RACI frameworks. Key Skills: Program Governance & Oversight; Talent Acquisition Strategy; RACI Matrix Implementation.",
    "created_at": "2026-09-09 23:28:04",
    "error": null,
    "estelle_notified_at": null,
    "estelle_thread_ts": null,
    "id": 2,
    "link": null,
    "nag_count": 0,
    "source_id": "1a0879ac5378fab4",
    "source_kind": "email",
    "source_ref": null,
    "state": "READY",
    "state_changed_at": "2026-09-10 03:02:40",
    "updated_at": "2026-09-10 03:02:40"
  },
  {
    "astral_job_id": null,
    "batch_created_at": null,
    "batch_id": null,
    "candidate_id": "somerset",
    "classify_outcome": "single_jd_no_link",
    "content": "Job Title: Technical Project Manager (Development Background)\nWork Location : Philadelphia, PA  (Onsite)\nContract duration: 12+ months Contract\nUSC and GC Only\nJob Summary:\nSeeking a Technical Project Manager with a strong software/application development background to manage end-to-end technology projects. Candidates who have transitioned from a Software Developer/Engineer or Technical Lead role into Project Management are highly preferred.",
    "created_at": "2026-09-09 23:28:08",
    "error": null,
    "estelle_notified_at": null,
    "estelle_thread_ts": null,
    "id": 3,
    "link": null,
    "nag_count": 0,
    "source_id": "1a08790aa9b8f1bf",
    "source_kind": "email",
    "source_ref": null,
    "state": "READY",
    "state_changed_at": "2026-09-10 03:02:40",
    "updated_at": "2026-09-10 03:02:40"
  },
  {
    "astral_job_id": null,
    "batch_created_at": null,
    "batch_id": null,
    "candidate_id": "somerset",
    "classify_outcome": "single_jd_no_link",
    "content": "Job Title: Technical Project Manager (Development Background)\nWork Location : Philadelphia, PA (Onsite)\nContract duration: 12+ months Contract\nVisa: US Citizens or GC\n\nJob Summary:\nSeeking a Technical Project Manager with a strong software/application development background to manage end-to-end technology projects. Candidates who have transitioned from a Software Developer/Engineer or Technical Lead role into Project Management are highly preferred.",
    "created_at": "2026-09-09 23:28:11",
    "error": null,
    "estelle_notified_at": null,
    "estelle_thread_ts": null,
    "id": 4,
    "link": null,
    "nag_count": 0,
    "source_id": "1a0877b2ac11e45a",
    "source_kind": "email",
    "source_ref": null,
    "state": "READY",
    "state_changed_at": "2026-09-10 03:02:40",
    "updated_at": "2026-09-10 03:02:40"
  },
  {
    "astral_job_id": null,
    "batch_created_at": null,
    "batch_id": null,
    "candidate_id": "somerset",
    "classify_outcome": "single_jd_no_link",
    "content": "Job Title: Technical Project Manager (Development Background)\nWork Location : Philadelphia, PA (Onsite)\nContract duration: 12+ months Contract\nVisa: US Citizens or GC\n\nJob Summary:\nSeeking a Technical Project Manager with a strong software/application development background to manage end-to-end technology projects. Candidates who have transitioned from a Software Developer/Engineer or Technical Lead role into Project Management are highly preferred.",
    "created_at": "2026-09-09 23:28:15",
    "error": null,
    "estelle_notified_at": null,
    "estelle_thread_ts": null,
    "id": 5,
    "link": null,
    "nag_count": 0,
    "source_id": "1a087507808545d6",
    "source_kind": "email",
    "source_ref": null,
    "state": "READY",
    "state_changed_at": "2026-09-10 03:02:40",
    "updated_at": "2026-09-10 03:02:40"
  },
  {
    "astral_job_id": null,
    "batch_created_at": null,
    "batch_id": null,
    "candidate_id": "somerset",
    "classify_outcome": "single_jd_no_link",
    "content": "Job Description:- \nJob Title:- Senior Principal Program Manager\nLocation:- Rancho Cordova, CA (Hybrid)\nContract\nPosition Summary\nWe are seeking a highly experienced Senior Principal Program Manager to report to and directly support the Head of Talent Acquisition in leading the HR workstream for a confidential, large-scale strategic initiative. This person will serve as the operational backbone of the HR workstream, establishing governance, creating structure, driving accountability, and enabling disciplined execution across multiple concurrent priorities.\nThe successful candidate must be able to plug in immediately with minimal onboarding. This role requires a senior practitioner who genuinely loves project and program management, can create order from ambiguity, and is comfortable operating with executives and cross-functional leaders in a fast-paced, highly confidential environment.\nProject governance (RACI) / PM\nWorking across teams / external partners / IT\nTracking deadlines / meetings / managing groups\nRequired Qualifications\n•           12+ years of progressive project and program management experience, including leadership of highly complex, cross-functional initiatives.\n•            Demonstrated experience supporting senior executives and serving as a trusted program management partner in a highly visible environment.\n•            Direct semiconductor and manufacturing industry experience. Candidates without both relevant industry contexts should not be advanced.\n•            Proven ability to establish governance, integrated plans, RACIs, milestone tracking, decision logs, action tracking, risk management, and executive reporting from the ground up.\n•            PMP certification in active good standing.\n•            Practical experience applying Agile and Scrum methods in complex programs.\n•            Advanced proficiency in Microsoft Teams, PowerPoint, Excel, and spreadsheet management, with the ability to produce polished executive deliverables independently.\n•            Demonstrated, responsible use of AI productivity tools to accelerate program management work while protecting confidential information.\n•            Ability to work primarily in Pacific Time and collaborate effectively with geographically distributed stakeholders.\n•            Exceptional judgment, discretion, written communication, facilitation, organizational discipline, and attention to detail.\n•            Support development of the HR workstream budget, resource plan, assumptions, and supporting business cases.\n•            Monitor planned versus actual spend, commitments, forecast changes, and emerging budget risks.\n•            Partner with Finance, Procurement, and workstream owners to maintain accurate budget reporting and supporting documentation.\n•            Prepare leadership-ready financial summaries and clearly flag decisions, tradeoffs, and corrective actions.\nPreferred Qualifications\n•            West Coast-based candidate with established availability during Pacific Time business hours.\n•            Advanced certification such as Certified ScrumMaster, PMI-ACP, SAFe, or PgMP.\n•            Experience supporting organizational readiness, workforce planning, business expansion, or large-scale transformation programs.\n•            Experience managing budgets, consulting or contractor spend, resource forecasts, and leadership-level financial reporting.\n•            Experience partnering across Talent Acquisition, HR, Finance, IT, Legal, Procurement, and Operations.\n•            Experience with Microsoft Project, Smartsheet, SharePoint, and dashboard/reporting solutions.\nKey Responsibilities\n• Strategic Partnership to the Head of Talent Acquisition\n• Program Governance and Operating Rhythm\n• Integrated Planning, Milestones, and Execution\n• Decision, Action, Risk, and Issue Management\n• Budget Development and Monitoring Support\n• Tools, Reporting, and AI Enablement",
    "created_at": "2026-09-09 23:28:21",
    "error": null,
    "estelle_notified_at": null,
    "estelle_thread_ts": null,
    "id": 6,
    "link": null,
    "nag_count": 0,
    "source_id": "1a082474ca8a689f",
    "source_kind": "email",
    "source_ref": null,
    "state": "READY",
    "state_changed_at": "2026-09-10 03:02:40",
    "updated_at": "2026-09-10 03:02:40"
  },
  {
    "astral_job_id": null,
    "batch_created_at": null,
    "batch_id": null,
    "candidate_id": "somerset",
    "classify_outcome": "single_jd_no_link",
    "content": "Job Title: Technical Project Manager\nJob Location: South San Francisco, CA 94080\nJob Duration: 6 months on W2 (Contract Full Time)\nMust be US Citizens or Permanent Resident (Green Card holder)\n\nOverview\nClient is seeking a Technical Project Manager to support the Director of GenAI Applications through delivery coordination, documentation, and business systems analysis activities across internal engineering teams and external partners.\nThis role focuses on maintaining visibility, alignment, and execution across multiple workstreams. The Technical Project Manager will help organize delivery efforts, manage documentation, support planning and tracking activities, and ensure technical requirements, decisions, and progress are clearly documented and communicated.\n\nCore Responsibilities\n• Maintain delivery plans, milestones, dependencies, action items, risks, and decisions across multiple workstreams.\n• Coordinate follow-ups, handoffs, and open items among internal engineering teams and external partners.\n• Partner closely with the Director of GenAI Applications to document priorities, ownership, timelines, and blockers.\n• Collaborate with the Technical Program Manager to provide accurate delivery updates and escalate issues requiring leadership attention.\n• Create and maintain Confluence documentation for technical solutions, workflows, architecture decisions, interfaces, dependencies, and operational processes.\n• Translate approved requirements and technical discussions into clear Jira stories, subtasks, and testable acceptance criteria with appropriate technical owners.\n• Ensure Jira and Confluence remain aligned so that scope, ownership, decisions, current status, and completion evidence are easily accessible.\n• Support backlog refinement, planning activities, demonstrations, release readiness efforts, and acceptance tracking while identifying and escalating gaps as needed.\n\nEssential Qualifications, Skills, and Technologies\n• Experience coordinating software delivery across multiple engineering teams and external partners.\n• Strong Jira and Confluence expertise, including story creation, backlog management, technical documentation, dashboards, and traceability.\n• Ability to create clear technical documentation and write testable acceptance criteria.\n• Working knowledge of software architecture, APIs, data flows, cloud services, environments, testing practices, and release processes.\n• Strong organizational skills, written communication skills, attention to detail, and follow-through.\n• Ability to collaborate effectively across business, product, engineering, data and AI, platform, security, and vendor teams, including globally distributed teams and multiple time zones.\n\nPreferred Skills or Experience\n• Experience with enterprise software environments.\n• Experience supporting AI or machine learning applications.\n• Experience working with distributed systems.\n• Experience with cloud platforms.\n\nWork Details\n• Reports to the Director of GenAI Applications.\n• Supports delivery coordination and technical documentation activities across internal engineering teams and external partners.\n• This role supports delivery coordination and documentation functions and is not accountable for writing or approving implementation code.",
    "created_at": "2026-09-09 23:28:27",
    "error": null,
    "estelle_notified_at": null,
    "estelle_thread_ts": null,
    "id": 7,
    "link": null,
    "nag_count": 0,
    "source_id": "1a06dda7a4459f80",
    "source_kind": "email",
    "source_ref": null,
    "state": "READY",
    "state_changed_at": "2026-09-10 03:02:40",
    "updated_at": "2026-09-10 03:02:40"
  },
  {
    "astral_job_id": null,
    "batch_created_at": null,
    "batch_id": null,
    "candidate_id": "somerset",
    "classify_outcome": "single_jd_no_link",
    "content": "The work model will be hybrid, with an expectation of working a minimum of every other week, Tuesday through Thursday at OGO (300 Lakeside Dr, Oakland). There may be some periods where working each week from OGO Tuesday through Thursday will be required. Mondays & Fridays are almost always remote.\n\nFor supporting resume screening, I'd look for:\nGovernance & Reporting Leadership\nAnalytical Problem Solving\nStakeholder Influence\n\nTop 3 Qualifications / Attributes to Prioritize\nPMO Governance & Executive Reporting; Experience building program governance, reporting rhythms, dashboards, KPIs, and executive-ready status communications.\nAnalytical & Systems Thinking; Ability to turn complex program data into meaningful insights, metrics, readiness indicators, and improvement actions.\nInfluence Without Authority; Proven success driving alignment, accountability, and results across multiple teams and stakeholders.\n\nTop 5 Skill Sets to Look For\nKPI, Metrics, and Dashboard Development\nExecutive Communication and Storytelling\nProgram Governance and PMO Operations\nProcess Improvement and Problem Solving\nStakeholder Management and Cross-Functional Leadership\n\nProgram Manager, Senior\n• Completes moderate to complex problems and takes a new perspective on existing solutions, plans, and goals.\n• Works independently on most issues.\n• Provides direction on overall program plan and goals.\n• Responsible for most/all deliverables within the program implementation plan.\n• Communicates findings and recommendations to various levels of management.\n• Develops budget forecasts, conducts analysis in support of identifying budget variances, and develops solutions to address.\n• Develops new and ad-hoc reports, summarizes findings and recommendations, and provides business insight.\n\nEducation:\n• Bachelor's degree or equivalent experience\n\nExperience:\n6 years of related experience or equivalent\n\nKnowledge, Skills, and Abilities\nDesired\n• Advanced knowledge of Program Management\n• Ability to communicate findings and recommendations to various levels of management.\n• Ability to effectively manage multiple projects with demanding time constraints.\n• Knowledge and understanding of business drivers.\n• Demonstrated ability to manage or direct teams\n• Ability to work within a Regulatory environment\n• Ability to assess and recommend solutions for assigned projects\nKnowledge of energy industry applications to local-level customers, including energy issues, customer energy efficiency applications, and general customer information.\n\nDesired\n• Primarily office environment with extensive use of personal computers, telephone conversations, conference calls, and in-person meetings.\nTravel may be required.",
    "created_at": "2026-09-09 23:28:33",
    "error": null,
    "estelle_notified_at": null,
    "estelle_thread_ts": null,
    "id": 8,
    "link": null,
    "nag_count": 0,
    "source_id": "1a06daf869d4049e",
    "source_kind": "email",
    "source_ref": null,
    "state": "READY",
    "state_changed_at": "2026-09-10 03:02:40",
    "updated_at": "2026-09-10 03:02:40"
  },
  {
    "astral_job_id": null,
    "batch_created_at": null,
    "batch_id": null,
    "candidate_id": "somerset",
    "classify_outcome": "single_jd_no_link",
    "content": "Job Title: Technical Project Manager\nReporting To: Director of GenAI Applications\nFunction: Engineering / AI Delivery Operations\nLocation: South San Francisco, CA \n12+ Months Contract \nRole Summary:\nThe Technical Project Manager (Delivery Coordination & BSA) is responsible for driving operational alignment, structured delivery, and technical documentation across Generative AI application workstreams. Partnering directly with the Director of GenAI Applications, Technical Program Managers (TPMs), and engineering leads, you will bridge the gap between technical design and execution. This role ensures roadmaps, cross-team dependencies, vendor integrations, and system documentation remain transparent, organized, and measurable—enabling software and machine learning engineers to focus on architecture, coding, and deployment.\nKey Responsibilities:\n- Delivery & Governance: Build and maintain cross-functional delivery schedules, milestones, dependencies, risks/issues (RAID logs), action items, and decision logs across multiple concurrent AI workstreams.\n- Stakeholder & Vendor Coordination: Drive regular alignment, handoffs, and clear communication across internal engineering, data/platform, security, product, and external technology partners.\n- Status & Escalations: Collaborate with the Director and TPM to synthesize delivery health metrics, identify blockers early, and escalate cross-team bottlenecks needing leadership intervention.\n- Systems Analysis & Documentation: Author and curate comprehensive Confluence pages covering architecture decision records (ADRs), system integration points, API data flows, interface definitions, and standard operating procedures (SOPs).\n- Backlog & Agile Operations: Translate technical specifications and business requirements into groomed Jira epics, user stories, subtasks, and testable acceptance criteria with assigned technical owners.\n- Traceability & Releases: Maintain synchronization between Jira tickets and Confluence artifacts to ensure clear scope boundaries, auditability, acceptance sign-offs, and release readiness.\nRequired Qualifications:\n- 4+ years of experience in technical project management, delivery coordination, or technical systems analysis within software engineering environments.\n- Proven track record managing multi-team software deliveries and third-party vendor/partner workstreams.\n- Advanced proficiency in Atlassian Jira and Confluence (creating technical epics/stories, managing backlogs, building status dashboards, and tracking end-to-end traceability).\n- Practical understanding of modern software systems: REST/gRPC APIs, cloud-native services (AWS/GCP/Azure), CI/CD pipelines, system environments, and automated testing frameworks.\n- Ability to break down ambiguous engineering concepts into structured, testable acceptance criteria and operational documentation.\n- Strong written and verbal communication skills with demonstrated success coordinating distributed or global technical teams across time zones.\nPreferred Qualifications:\n- Experience working on teams delivering Generative AI, Large Language Model (LLM) workflows, ML pipelines, or enterprise data platforms.\n- Hands-on familiarity with Agile/Scrum/Kanban delivery frameworks.\nRole Boundaries:\nFocuses on delivery enablement, dependency management, process tracking, and technical documentation. This role does not write application code, act as the final solution architect, or replace technical lead ownership of system design.",
    "created_at": "2026-09-09 23:28:38",
    "error": null,
    "estelle_notified_at": null,
    "estelle_thread_ts": null,
    "id": 9,
    "link": null,
    "nag_count": 0,
    "source_id": "1a06d92c6e750895",
    "source_kind": "email",
    "source_ref": null,
    "state": "READY",
    "state_changed_at": "2026-09-10 03:02:40",
    "updated_at": "2026-09-10 03:02:40"
  },
  {
    "astral_job_id": null,
    "batch_created_at": null,
    "batch_id": null,
    "candidate_id": "somerset",
    "classify_outcome": "single_jd_no_link",
    "content": "Role- Compliance Project Manager\nLocation- Cupertino, CA(Remote is also fine)\nMode- Full-Time\nProject management with individual planning and execution capabilities\nSummary\nThe Tax Product team is responsible for researching, defining, and delivering tax capabilities that support seamless commerce experiences for customers worldwide. This work ensures customers can access our digital products and services securely , privately , and without friction.\nAs a Compliance Program Manager, you will drive end-to-end execution of tax compliance programs — from due diligence to launch readiness — coordinating cross-functional efforts across client engineering, product, finance, tax, and business teams.\nDescription\nWe are seeking an experienced, highly organized, and motivated problem-solver to drive critical compliance initiatives across our ecosystem. In this role, you will manage complex, global programs that sit at the intersection of tax policy , tax product development, developer operations, and cross-functional execution.\nYou will coordinate end-to-end lifecycle management of tax compliance requirements — from due diligence and requirement gathering through system implementation and launch readiness. As part of launch readiness activities, you will identify impacted developer populations for outreach programs that communicate tax obligations clearly and at scale. You will draft developer-facing communications, enforcement strategies, help guides, and helpline support responses, and own the project management required to move these deliverables through cross-functional review and leadership sign-off.\nThis role requires comfort operating in ambiguous regulatory environments across the globe. You must be equally comfortable analyzing large datasets, writing crisp developer-facing copy , and presenting compliance status to leadership.\nMinimum Qualifications:\n3+ years of experience in end-to-end program management, with expertise leading large, global, complex projects\nStrong project management skills, with a track record of driving cross-functional teams — spanning legal, finance/tax, engineering, product, and operations — to decisions and formal approvals on tight deadlines\nProficient in managing launch readiness and operational activities, including communications and prepared responses to developer inquiries\nAbility to identify process efficiencies and improvements using existing and new methodologies; manage technical and non-technical dependencies to ensure solutions meet regulatory , customer, partner, and A requirements\nExperience spanning business operations, project management, finance, and/or tax, legal, and system design, with a track record of driving impactful outcomes\nPreferred Qualifications\nUnderstanding of general tax principles, with the ability to translate complex regulatory requirements into clear, partner-facing language\nAbility to navigate ambiguity in response to regulatory change, solving problems with sound judgment and innovative techniques\nOutstanding written and verbal communication skills, leveraging emotional intelligence to build strong partnerships with stakeholders in a matrix organization; ability to bring structure to all aspects of work and influence cross-functional teams\nHighly motivated and results-oriented problem-solver who thrives in a fast-paced environment delivering value to customers and partners\n7–10 years of relevant work experience in Tax/Commerce Product and Program Management\nHighly organized, with exceptional multitasking skills, attention to detail, and the ability to thrive in time-sensitive, constantly changing environment",
    "created_at": "2026-09-09 23:28:54",
    "error": null,
    "estelle_notified_at": null,
    "estelle_thread_ts": null,
    "id": 10,
    "link": null,
    "nag_count": 0,
    "source_id": "1a06ce4255deaa5e",
    "source_kind": "email",
    "source_ref": null,
    "state": "READY",
    "state_changed_at": "2026-09-10 03:02:40",
    "updated_at": "2026-09-10 03:02:40"
  },
  {
    "astral_job_id": null,
    "batch_created_at": null,
    "batch_id": null,
    "candidate_id": "somerset",
    "classify_outcome": "single_jd_no_link",
    "content": "Client: PG&E - Agile1\nTitle: Program Manager, Senior\nJob ID: PCGJP00005049\nLocation: 300 Lakeside Dr Oakland, CA 94612 - The work model will be hybrid, with an expectation of working a minimum of every other week Tuesday through Thursday at OGO (300 Lakeside Dr, Oakland). There may be some periods where working each week from OGO Tuesday through Thursday will be required. Monday’s & Friday’s are almost always remote.\nPay Rate - $98 to $100hr w2\nDuration: 3 Months (2026-09-14 to 2026-12-11)\n\nWHAT THE CLIENT DOES?\nA major utility company that provides electricity and natural gas services to millions of customers. It operates a vast energy infrastructure, including power plants, transmission lines, and gas pipelines.\n\nDescription:\nONLY SUBMIT CANDIDATES WHO RESIDE LOCALLY IN PG&E SERVICE TERRITORY AND NEAR WORK LOCATION-OAKLAND GO.\n\nThe work model will be hybrid, with an expectation of working a minimum of every other week Tuesday through Thursday at OGO (300 Lakeside Dr, Oakland). There may be some periods where working each week from OGO Tuesday through Thursday will be required. Monday’s & Friday’s are almost always remote.\n\nA PG&E LAPTOP WILL BE PROVIDED AND A PERSONAL/SUPPLIER LAPTOP CAN'T BE USED. ANY ADDITIONAL EQUIPMENT NEEDED WILL BE PROVIDED BY THE SUPPLIER. PERSONAL PHONE REQUIRED(W/NO REIMBURSEMENT) MILEAGE REIMBURSEMENT WILL BE APPROVED IF CANDIDATE IS ASKED TO GO TO ANY OTHER LOCATION BESIDES THE OAKLAND GO, NORMAL COMMUTE TO OGO NOT INCLUDED.\n\nFor supporting resumes screening, I'd look for:\nGovernance & Reporting Leadership\nAnalytical Problem Solving\nStakeholder Influence\n\nTop 3 Qualifications / Attributes to Prioritize\nPMO Governance & Executive Reporting; Experience building program governance, reporting rhythms, dashboards, KPIs, and executive-ready status communications.\nAnalytical & Systems Thinking; Ability to turn complex program data into meaningful insights, metrics, readiness indicators, and improvement actions.\nInfluence Without Authority; Proven success driving alignment, accountability, and results across multiple teams and stakeholders.\n\nTop 5 Skill Sets to Look For\nKPI, Metrics, and Dashboard Development\nExecutive Communication and Storytelling\nProgram Governance and PMO Operations\nProcess Improvement and Problem Solving\nStakeholder Management and Cross-Functional Leadership\n\nProgram Manager, Senior\n• Completes moderate to complex problems and takes a new perspective on existing solutions plan and goals.\n• Works independently on most issues.\n• Provides direction on overall program plan and goals.\n• Responsible for most/all deliverables within the program implementation plan.\n• Communicates findings and recommendations to various levels of management.\n• Develops budget forecasts, conducts analysis in support of identifying budget variances and develops solutions to address.\n• Develops new and ad-hoc reports, summarizes findings and recommendations and provides business insight.\n\nEducation:\nBachelor degree or equivalent experience\n\nExperience:\n6 years of related experience or equivalent\n\nKnowledge, Skills, and Abilities\nDesired\n• Advanced knowledge of Program Management\n• Ability to communicate findings and recommendations to various levels of management.\n• Ability to effectively manage multiple projects with demanding time constraints.\n• Knowledge and understanding of business drivers.\n• Demonstrated ability to manage or direct teams\n• Ability to work within a Regulatory environment\n• Ability to assess and recommend solutions for assigned projects\nKnowledge of energy industry applications to local level customers, including energy issues, customer energy efficiency applications, and general customer information.\n\nDesired\n• Primarily office environment with extensive use of personal computers, telephone conversations, conference calls and in person meetings.\nTravel may be required.",
    "created_at": "2026-09-09 23:29:04",
    "error": null,
    "estelle_notified_at": null,
    "estelle_thread_ts": null,
    "id": 11,
    "link": null,
    "nag_count": 0,
    "source_id": "1a0699b99551c9b2",
    "source_kind": "email",
    "source_ref": null,
    "state": "READY",
    "state_changed_at": "2026-09-10 03:02:45",
    "updated_at": "2026-09-10 03:02:45"
  },
  {
    "astral_job_id": null,
    "batch_created_at": null,
    "batch_id": null,
    "candidate_id": "somerset",
    "classify_outcome": "single_jd_no_link",
    "content": "Job Title: Oracle Technical Program Manager\nLocation: Phoenix, AZ\nEmployment Type: Full Time\nExperience: 8+ years\n• Strong experience managing Oracle Platform operations, Governance, Change Management and Delivery.\n• Manage end-to-end Oracle platform programs, including planning, execution, delivery tracking, risk management, and stakeholder communication.\n• Lead Oracle implementation, upgrade, migration, and support initiatives across cross-functional technical and business teams.\n• Drive governance for Oracle programs by maintaining project plans, status reporting, issue escalation, change management, and delivery compliance.\n• Coordinate with Oracle technical teams, vendors, business users, and leadership to ensure timely delivery of milestones and resolution of dependencies.\n• Ensure Oracle solutions meet business requirements, operational standards, security guidelines, and quality expectations while supporting continuous improvement.",
    "created_at": "2026-09-09 23:29:09",
    "error": null,
    "estelle_notified_at": null,
    "estelle_thread_ts": null,
    "id": 12,
    "link": null,
    "nag_count": 0,
    "source_id": "1a06976e691e2900",
    "source_kind": "email",
    "source_ref": null,
    "state": "READY",
    "state_changed_at": "2026-09-10 03:02:45",
    "updated_at": "2026-09-10 03:02:45"
  },
  {
    "astral_job_id": null,
    "batch_created_at": null,
    "batch_id": null,
    "candidate_id": "somerset",
    "classify_outcome": "single_jd_no_link",
    "content": "Position: Project Manager\nLocation: Woodland Hills CA/Mason, OH(Onsite)\nFulltime\nJob Description:\n10–15 years of IT experience with strong exposure to Healthcare domain\n• Proven experience as Project Manager / Program Manager with Technical Delivery ownership\n• Experience in Payer/Provider / Medicare / Medicaid environments preferred\nRole Overview\nWe are seeking an experienced Project/Program Manager with strong healthcare domain expertise who can lead complex programs and drive end-to-end technical delivery. The role demands a blend of delivery leadership, program governance, and technical oversight to ensure successful execution of healthcare solutions in compliance with regulatory requirements.\nKey Responsibilities\n• Lead end-to-end delivery of projects/programs, ensuring alignment with business objectives and regulatory standards\n• Act as a Technical Delivery Lead, guiding architecture, solution design, and implementation across systems\n• Manage program/project planning, including scope, schedule, cost, and resource allocation\n• Drive cross-functional collaboration across business, engineering, QA, and operations teams\n• Ensure compliance with healthcare regulations and standards (e.g., claims processing, payer/provider workflows, data compliance) \n• Oversee risk management, issue resolution, and escalation handling for delivery assurance\n• Manage stakeholder communication, including executive leadership and client interactions\n• Drive Agile/Scrum delivery practices, ensuring continuous improvement and timely delivery\n• Support solutioning, estimations, and pre-sales activities where applicable\n• Ensure quality, release management, and production stability across applications\nRequired Skills & Competencies\n• Strong expertise in Project Management / Program Management / Delivery Management\n• Proven experience as Technical Delivery Lead for enterprise applications\n• Deep understanding of Healthcare processes (Enrollment, Eligibility, Benefits, Claims Adjudication, Billing, Provider Management, compliance) \n• Experience with Agile/Scrum methodologies and tools (JIRA, MS Project, etc.) [ \n• Strong stakeholder management and communication skills\n• Ability to manage cross-functional and distributed teams\n• Strong analytical, problem-solving, and decision-making skills\n• Familiarity with healthcare IT systems, integrations, and data standards\nPreferred Qualifications\n• Exposure to US Healthcare (Medicare / Medicaid programs)\n• Experience handling large-scale transformation programs / AMS engagements\nKey Traits\n• Strong ownership and accountability mindset\n• Ability to operate at both strategic (program level) and technical (delivery level)\n• Excellent collaboration and leadership skills\n• High attention to detail and structured execution (aligned to delivery excellence)",
    "created_at": "2026-09-09 23:29:14",
    "error": null,
    "estelle_notified_at": null,
    "estelle_thread_ts": null,
    "id": 13,
    "link": null,
    "nag_count": 0,
    "source_id": "1a064038ed227945",
    "source_kind": "email",
    "source_ref": null,
    "state": "READY",
    "state_changed_at": "2026-09-10 03:02:45",
    "updated_at": "2026-09-10 03:02:45"
  },
  {
    "astral_job_id": null,
    "batch_created_at": null,
    "batch_id": null,
    "candidate_id": "somerset",
    "classify_outcome": "single_jd_no_link",
    "content": "Job Title: Senior Technical Project Manager\nWork Location: San Jose, CA USA (Hybrid)\nContract duration: Long term contract\nVisa: GC/USC/ Only\n\nJob Description:\nProject Manager – Level III\nResponsibilities\nThe role includes responsibility for:\n- Developing, planning, scheduling, introducing, communicating, and maintaining projects.\n- Organizing and controlling activities, assigning personnel to projects, and directing their work.\n- Managing high-complexity, cross-functional system implementation, maintenance, and integration projects.\n- Monitoring progress to ensure objectives are delivered on time, within budget, and that business results are realized.\n- Monitoring and controlling quality, risks, issues, and project changes.\n- Supporting and contributing to the development and enhancement of ServiceNow project management standards and processes.\n- Determining the impact of changes on the business case and reforecasting value creation.\n- Developing executive-level sponsorship and support, and establishing governance structures.\n- Resolving issues escalated by the management team.\n- Escalating unresolved issues through the governance framework.\n\nQualifications\nThe qualifications listed include:\n- Bachelor’s degree (BA/BS) or equivalent combination of education and experience.\n- 5+ years managing large-scale initiatives in an engineering or technology environment and 7+ years of project management experience.\n- Experience and training in Scrum Master and DevSecOps methodologies.\n- Expert knowledge in the assigned business discipline such as engineering or information technology.\n- PMP certification strongly preferred.\n- Advanced proficiency in project management tools such as Microsoft Project, including financial and schedule performance reporting.\n- Strong analytical, organizational, project management, interpersonal, and communication skills.\n- ServiceNow and relationship-focused mindset; process-driven, metric-focused, results-oriented, organized, and self-directed.\n- Ability to multitask and solve problems innovatively.\n- Consulting Perspective\n\nFor a client such as ServiceNow, this role aligns with a Senior Project Manager / Program Manager profile responsible for:\n- Leading enterprise technology implementations.\n- Managing cross-functional delivery teams.\n- Driving governance, risk management, and executive stakeholder alignment.\n- Overseeing budget, schedule, value realization, and business outcomes.\n- Working within Agile, Scrum, and DevSecOps environments.",
    "created_at": "2026-09-09 23:29:23",
    "error": null,
    "estelle_notified_at": null,
    "estelle_thread_ts": null,
    "id": 14,
    "link": null,
    "nag_count": 0,
    "source_id": "1a062f205610ca9d",
    "source_kind": "email",
    "source_ref": null,
    "state": "READY",
    "state_changed_at": "2026-09-10 03:02:45",
    "updated_at": "2026-09-10 03:02:45"
  },
  {
    "astral_job_id": null,
    "batch_created_at": null,
    "batch_id": null,
    "candidate_id": "somerset",
    "classify_outcome": "single_jd_no_link",
    "content": "Job Title: Technical Product Owner\nWork Location: Houston, TX 77002\nContract duration: 6 months\nMinimum years of experience: 10+ years\nVisa: GC/USC\nW2 Only\nMust Have Skills\nScrum\nAWS\nProduct Owner\nNice to have skills\nScrum\nAWS\nDetailed Job Description\nPOManaging and prioritizing the product backlogServing as a liaison between product and developmentDefine Sprint GoalAttend workshops and understand WM expectations in detailDevelop user storiesParticipate in Scrum events",
    "created_at": "2026-09-09 23:29:31",
    "error": null,
    "estelle_notified_at": null,
    "estelle_thread_ts": null,
    "id": 15,
    "link": null,
    "nag_count": 0,
    "source_id": "1a05e06866bd7a59",
    "source_kind": "email",
    "source_ref": null,
    "state": "READY",
    "state_changed_at": "2026-09-10 03:02:45",
    "updated_at": "2026-09-10 03:02:45"
  },
  {
    "astral_job_id": null,
    "batch_created_at": null,
    "batch_id": null,
    "candidate_id": "somerset",
    "classify_outcome": "single_jd_no_link",
    "content": "Job Title: Product Owner\nLocation: Houston, TX 77002 (Hybrid)\nDuration: 6 Months\n\nJob Details:\nMust Have Skills\nScrum\nAWS\nProduct Owner\n\nNice to have skills\nScrum\nAWS\n\nDetailed Job Description\nPOManaging and prioritizing the product backlogServing as a liaison between product and developmentDefine Sprint GoalAttend workshops and understand WM expectations in detailDevelop user storiesParticipate in Scrum events\n\nMinimum years of experience\n>10 years",
    "created_at": "2026-09-09 23:29:34",
    "error": null,
    "estelle_notified_at": null,
    "estelle_thread_ts": null,
    "id": 16,
    "link": null,
    "nag_count": 0,
    "source_id": "1a05def4eb618ba9",
    "source_kind": "email",
    "source_ref": null,
    "state": "READY",
    "state_changed_at": "2026-09-10 03:02:45",
    "updated_at": "2026-09-10 03:02:45"
  },
  {
    "astral_job_id": null,
    "batch_created_at": null,
    "batch_id": null,
    "candidate_id": "somerset",
    "classify_outcome": "single_jd_no_link",
    "content": "Title: SR STAFF ENTERPRISE PROGRAM MANAGER\nLocation: REMOTE BUT PREFERENCE FOR MA/EAST COAST FROM TIMEZONE POV\nDuration: 6+ Months Contract\nClient: Insulet\nInterview Mode: Video\n*Must get two references*\n\nPosition Overview:\nThis position is responsible for the Global Website Redesign program which covers multiple workstreams including development, content and UX and will be launched in countries throughout the world.\n\nOverall, the program manager is responsible for the delivery of enterprise-wide programs through a methodical approach of planning, executing, and controlling projects from start to finish. The Senior Staff Enterprise Program Manager (Sr Staff EPM) demonstrates enterprise solution ownership and guides teams through the program execution process to realize strategic objectives of the Franchise. The Sr Staff EPM uses professional program management concepts and frameworks in accordance with company objectives to solve complex problems in a creative and effective way, and exercises a balance of independent judgment and group organization in developing methods, techniques, and evaluation criteria for obtaining results.\n\nResponsibilities\n· Responsible for planning, program management, and on-time delivery of major enterprise-wide strategic priorities such as product and country launches, and complex large-scale systems releases, across multiple Agile Solution Delivery trains\n· Build and maintain overall detailed program plan, Gantt chart, status updates, and RAIDE Register (Risks, Assumptions, Issues, Dependencies and Escalations) integrating all cross-functional workstreams.\n· Maintain and update program schedule and dependencies integrated with Agile teams, ARTs, and Solutions PI Plans\n· Lead release-based program core team for assigned program(s)\n· Lead program-related activities of project team members, providing guidance on conformance to established design control procedures.\n· Identify and assess mitigation options for program risks and issues and escalate as needed to ensure program success.\n· Assist Product Managers and core teams in problem solving and scenario analysis to assess impact of change requests.\n· Provide input to Agile teams and ARTs review during PI planning and assess impact of PI Planning output to overall plan.\n· Adhere to all regulatory agency standards, company quality standards, and corporate policies.\n· Perform other duties as required.\n\nKey Decision Rights\n· Develops and maintains 24-month program schedule & supporting detailed integrated program plan, identification and communication of programs risks, issues, and blockers impacting overall program delivery.\n· Influences program timelines, budget, and priorities, change management of any changes impacting overall program timeline.\n· Vetoes unapproved schedule or resource changes that will impact overall program timeline and unapproved communication of program status, scenario analysis, timelines/roadmaps, risks, or issues.\n\nRequired Leadership/Interpersonal Skills & Behaviors\n· Strong influence management skills – track record of influencing behaviors.\n· Excellent communication, collaboration, problem solving, and people skills.\n· Desire to learn and to help teams continuously improve.\n· Courage to challenge & advise various stakeholders, including senior leaders.\n· Strategic Orientation - Understand the business context in which the technology solutions are being developed and designed to ensure alignment with business and technology strategies.\n· Results Orientation - Deliver technology solutions focused on business outcome value with metrics of on time, within budget and ROI. Maintain a sense of urgency, delivering high-quality work in a highly dynamic environment.\n· Collaboration and Influencing - Build meaningful relationships across the enterprise, functions, levels and geographies. Skilled in communicating complex ideas and open to ideas from others. Proven sound decision-making process and ability to influence through strong interpersonal skills, underlined by superior judgment.\n· Business Strategic Planning - Work with senior business leaders to better understand business challenges, strategic goals, and process improvement opportunities. Assist in the business planning and multi-year strategic planning process for the company.\n· Team Leadership - Demonstrated strong leadership skills, signifying a passion for guiding and developing others and challenging his/her team to discover an improved way of delivering value. Attract and develop a highly skilled program team. Acquire resources, set direction, and coordinate the efforts of team members and third-party contractors or consultants to deliver program results. Flexibility in style to bring out the best in people with different backgrounds and working styles, while unifying them in purpose, role clarity, and expectations related to deliverables.\n\nRequired Skills and Competencies\n· Medical Device Program Management experience\n· Agile certification and transformation experience\n· Project management certification preferred.\n· Experience leading development, testing, and commercial launch of complex innovative hardware, software, and cloud connected medical devices.\n· Experience working with Agile teams to develop and launch products against concreate deadlines.\n· Demonstrated flexibility and ability to function in a fast-paced, growth industry and work environment.\n· Proficient in the following computer software applications: MS 365 Suite (Word, Excel, PowerPoint Project, Outlook, Teams), Miro, Smartsheet, SharePoint, Timeline Pro.\n· Helpful to have working knowledge or familiarity with: - Agile applications (Jira & Confluence), - CRM Environments (SalesForce, Marketing Cloud), - ERP system (SAP), - Identity Management (Okta, .Net) - Integration (Mulesoft) - PLM & QMS applications (Arena), - PPM tools (Clarity), - Validated test management tool - Requirements, Test Cases, Defects (Polarion) - Web (Drupal)\n\nEducation and Experience\n· Bachelor's Degree\n· At least 10 years of overall work experience in a technical discipline and 10-12 years of demonstrated experience in a program management role\n· Minimum of 5-7 years’ experience managing and developing people (directly or indirectly)",
    "created_at": "2026-09-09 23:29:56",
    "error": null,
    "estelle_notified_at": null,
    "estelle_thread_ts": null,
    "id": 17,
    "link": null,
    "nag_count": 0,
    "source_id": "1a059b5085a9c734",
    "source_kind": "email",
    "source_ref": null,
    "state": "READY",
    "state_changed_at": "2026-09-10 03:02:45",
    "updated_at": "2026-09-10 03:02:45"
  },
  {
    "astral_job_id": null,
    "batch_created_at": null,
    "batch_id": null,
    "candidate_id": "somerset",
    "classify_outcome": "single_jd_no_link",
    "content": "Title: SR STAFF ENTERPRISE PROGRAM MANAGER\nLocation: REMOTE BUT PREFERENCE FOR MA/EAST COAST FROM TIMEZONE POV\nDuration: 6+ Months Contract\nInterview Mode: Video\n\n*Must get two references\n\nPosition Overview:\nThis position is responsible for the Global Website Redesign program which covers multiple workstreams including development, content and UX and will be launched in countries throughout the world. Overall, the program manager is responsible for the delivery of enterprise-wide programs through a methodical approach of planning, executing, and controlling projects from start to finish. The Senior Staff Enterprise Program Manager (Sr Staff EPM) demonstrates enterprise solution ownership and guides teams through the program execution process to realize strategic objectives of the Franchise. The Sr Staff EPM uses professional program management concepts and frameworks in accordance with company objectives to solve complex problems in a creative and effective way, and exercises a balance of independent judgment and group organization in developing methods, techniques, and evaluation criteria for obtaining results.\n\nResponsibilities\n· Responsible for planning, program management, and on-time delivery of major enterprise-wide strategic priorities such as product and country launches, and complex large-scale systems releases, across multiple Agile Solution Delivery trains\n· Build and maintain overall detailed program plan, Gantt chart, status updates, and RAIDE Register (Risks, Assumptions, Issues, Dependencies and Escalations) integrating all cross-functional workstreams.\n· Maintain and update program schedule and dependencies integrated with Agile teams, ARTs, and Solutions PI Plans\n· Lead release-based program core team for assigned program(s)\n· Lead program-related activities of project team members, providing guidance on conformance to established design control procedures.\n· Identify and assess mitigation options for program risks and issues and escalate as needed to ensure program success.\n· Assist Product Managers and core teams in problem solving and scenario analysis to assess impact of change requests.\n· Provide input to Agile teams and ARTs review during PI planning and assess impact of PI Planning output to overall plan.\n· Adhere to all regulatory agency standards, company quality standards, and corporate policies.\n· Perform other duties as required.\n\nKey Decision Rights\n· Develops and maintains 24-month program schedule & supporting detailed integrated program plan, identification and communication of programs risks, issues, and blockers impacting overall program delivery.\n· Influences program timelines, budget, and priorities, change management of any changes impacting overall program timeline.\n· Vetoes unapproved schedule or resource changes that will impact overall program timeline and unapproved communication of program status, scenario analysis, timelines/roadmaps, risks, or issues.\n\nRequired Leadership/Interpersonal Skills & Behaviors\n· Strong influence management skills – track record of influencing behaviors.\n· Excellent communication, collaboration, problem solving, and people skills.\n· Desire to learn and to help teams continuously improve.\n· Courage to challenge & advise various stakeholders, including senior leaders.\n· Strategic Orientation - Understand the business context in which the technology solutions are being developed and designed to ensure alignment with business and technology strategies.\n· Results Orientation - Deliver technology solutions focused on business outcome value with metrics of on time, within budget and ROI. Maintain a sense of urgency, delivering high-quality work in a highly dynamic environment.\n· Collaboration and Influencing - Build meaningful relationships across the enterprise, functions, levels and geographies. Skilled in communicating complex ideas and open to ideas from others. Proven sound decision-making process and ability to influence through strong interpersonal skills, underlined by superior judgment.\n· Business Strategic Planning - Work with senior business leaders to better understand business challenges, strategic goals, and process improvement opportunities. Assist in the business planning and multi-year strategic planning process for the company.\n· Team Leadership - Demonstrated strong leadership skills, signifying a passion for guiding and developing others and challenging his/her team to discover an improved way of delivering value. Attract and develop a highly skilled program team. Acquire resources, set direction, and coordinate the efforts of team members and third-party contractors or consultants to deliver program results. Flexibility in style to bring out the best in people with different backgrounds and working styles, while unifying them in purpose, role clarity, and expectations related to deliverables.\n\nRequired Skills and Competencies\n· Medical Device Program Management experience\n· Agile certification and transformation experience\n· Project management certification preferred.\n· Experience leading development, testing, and commercial launch of complex innovative hardware, software, and cloud connected medical devices.\n· Experience working with Agile teams to develop and launch products against concreate deadlines.\n· Demonstrated flexibility and ability to function in a fast-paced, growth industry and work environment.\n· Proficient in the following computer software applications: MS 365 Suite (Word, Excel, PowerPoint Project, Outlook, Teams), Miro, Smartsheet, SharePoint, Timeline Pro.\n· Helpful to have working knowledge or familiarity with: - Agile applications (Jira & Confluence), - CRM Environments (SalesForce, Marketing Cloud), - ERP system (SAP), - Identity Management (Okta, .Net) - Integration (Mulesoft) - PLM & QMS applications (Arena), - PPM tools (Clarity), - Validated test management tool - Requirements, Test Cases, Defects (Polarion) - Web (Drupal)\n\nEducation and Experience\n· Bachelor's Degree\n· At least 10 years of overall work experience in a technical discipline and 10-12 years of demonstrated experience in a program management role\n· Minimum of 5-7 years’ experience managing and developing people (directly or indirectly)",
    "created_at": "2026-09-09 23:30:04",
    "error": null,
    "estelle_notified_at": null,
    "estelle_thread_ts": null,
    "id": 18,
    "link": null,
    "nag_count": 0,
    "source_id": "1a0599ae5adfd0c6",
    "source_kind": "email",
    "source_ref": null,
    "state": "READY",
    "state_changed_at": "2026-09-10 03:02:45",
    "updated_at": "2026-09-10 03:02:45"
  }
]
```

### Comments

#### chuckles — 2026-09-10T11:49:43.272Z
[check-linear] answered — confirmed not a bug (from this ticket’s description)

Yes. The As-is / To-be / Proposed steps already say the dump is consistent with intended design: classify already wrote `classify_outcome` earlier on the inbox path; dispatch `stage_meteorite` is transition-only and correctly has no agent call. Treat the stated symptom as **not a bug** unless agent_data for the Ruth hop is verified empty while rows still carry `classify_outcome` (that would be a separate persist/audit issue — this dump does not show that).

#### susan — 2026-09-10T03:21:45.590Z
So this is not a bug? You can confirm from the content in the description. @chuckles

#### chuckles — 2026-09-10T03:19:46.082Z
[check-linear] answered — intended flow was split on purpose (not a broken qualify twin)

Original design (AST-1527 / AST-1530 / AST-1560) was **not** “dispatch `stage_meteorite` ≈ `qualify_job_listings`.” Two different things share the name:

1. **Ruth classify** — `TASK_CONFIG["stage_meteorite"]` / `invoke_stage_meteorite` → `do_task`. Runs **inline** on inbox ingest (`check_inbox` / `ingest_candidate_email_message`). Writes `classify_outcome` (+ jobs) onto new `meteorite` rows. That is the agent hop. Audit = agent_data for that classify batch, not the Scheduled Actions runner.

2. **Dispatch `stage_meteorite`** — `run_stage_meteorite` (AST-1560). **Table transition only**: claim NEW rows → SCRAPE_LINK | READY from the **already-persisted** `classify_outcome`. Explicitly **not** a consult hop — no `do_task`, by design.

The Pattern-A twin of `qualify_job_listings` is **`qualify_meteorite`** (post-land job enrich), not dispatch stage.

Meteorite-not-in-`ENTITY_TYPES` did leave transition runners on a NULL-entity shell (Avail/AUTO blind) — that is a real gap (AST-1620) — but it is **not** why the dispatch runner has no Ruth logs. Looking at dispatch `stage_meteorite` for agent prompts will always look empty; the classify call was meant to happen earlier on the inbox path.

#### susan — 2026-09-10T03:17:56.381Z
@chuckles what was the original intended flow for stage_meteorite? I thought it was a path much like qualify_job_listing, no? Or did we build it differently because meteorite wasn't considered an entity at the time so the batch processing isn't working as expected?

---

_Implementation detail may live in git history on `origin/dev`._
