# AST-602 — Prefilter Company Failing

<!-- linear-archive: AST-602 archived 2026-06-23 -->

## Linear archive (AST-602)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-602/prefilter-company-failing  
**Status at archive:** Done  
**Project:** Astral Auditor  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Roster inflow depends on **prefilter company** to grade each **WEBSITE_FOUND** employer against the candidate's **company_prefilter** rubric and advance the company to **PREFILTER_PASSED**, **PREFILTER_FAILED**, or a retryable unknown state. Susan's production batch of 20 companies returned **20 failures** even though the model reported **agent_performance.status = success** — every company landed in **PREFILTER_UNKNOWN** because **prefilter_company** is not receiving **hydrated, decoded rubric responses** the way consult tasks do. This ticket restores prefilter by reusing the **consult rubric response-processing pattern** (decode → hydrate grades from artifact → verdict/score), not by inventing parallel parse logic for raw **agent_payload** shapes.

## Functional scope

* **Consult-parity hydration:** **prefilter_company** is a rubric-type prompt. After the model call, response processing must follow the same path consult uses: the agent layer returns a **decoded, hydrated** rubric result (grades with vector labels and reasons, plus optional link indices where applicable) — not roster-specific re-parsing of legacy pipe lines, JSON blobs, or ad-hoc field names from the Original brief.
* **End-to-end prefilter on hydrated input:** Once the hydrated decoded shape is available, apply existing **AST-507** prefilter semantics: dealbreaker **F** (confidence ≥ 2) → fail state; otherwise pass with **prefilter_score**; persist **prefilter_company_notes**, **possible_job_links**, and **culture_links_to_explore**; transition inflow companies to **PREFILTER_PASSED** / **PREFILTER_FAILED** (legacy manual path → **TO_WATCH** / **IGNORE**).
* **Successful model envelope → completed prefilter:** When **agent_performance.status** is **success**, a company must not remain in **PREFILTER_UNKNOWN** solely because decode/hydration failed — the consult-aligned pipeline must handle the response the model actually returns for this rubric task configuration.
* **Coat-check parity:** Manual prefilter (coat-check / notes fetch) uses the same hydrated response path as dispatch batch prefilter.

## Boundaries

* Does **not** change rubric vector definitions, pass thresholds, or dealbreaker rules from **AST-507**.
* Does **not** alter **AST-508** locate/parse dispatch beyond reading persisted prefilter fields.
* Does **not** add a second, prefilter-only decode matrix alongside consult — one rubric response pattern for both.
* Does **not** fix website scrape timeouts (e.g. [olo.com](<http://olo.com>) in the log) — those remain **CANNOT_READ_WEBSITE** behavior.
* Must not break existing **AST-507** component tests; extend coverage to prove consult-parity hydration on the repro payload shapes in the Original brief.

Per **ASTRAL_CODE_RULES** §2.1, behavior stays config-driven; alignment belongs in the shared agent/consult response path, not roster one-offs.

## Acceptance criteria

1. Re-run dispatch prefilter (or fixture replay of each **agent_payload** shape in the Original brief): **zero** companies stuck in **PREFILTER_UNKNOWN** solely because of decode/hydration errors when **agent_performance.status** is **success**.
2. Each successful run produces **hydrated grades** (vector + grade + confidence + reason) consistent with consult rubric processing before roster applies pass/fail and score.
3. Companies reach **PREFILTER_PASSED**, **PREFILTER_FAILED**, **TO_WATCH**, or **IGNORE** per inflow vs legacy path — not parse exceptions surfaced as **PREFILTER_UNKNOWN**.
4. **possible_job_links** and **culture_links_to_explore** persist when present in the decoded response; empty lists when absent.
5. Betty's **prefilter_company** / **AST-507** manifest tests pass; new tests cover at least one repro category using the consult hydration path.
6. Susan confirms a fresh prefilter batch advances companies out of **WEBSITE_FOUND** at a rate consistent with model success (not 0/N).

## Dependencies and blockers

* **AST-507** (Done) — prefilter state/score semantics this fix must preserve.
* **Consult encoded rubric pipeline** (incl. **AST-500** / **AST-351** hydration behavior) — pattern to reuse, not reimplement.
* **AST-491** (Done) — multi-provider routing; repro used DeepSeek.
* No open blockers; work can start once Susan approves this definition.

## Open questions

none.

---

## Original brief

I ran prefilter company on 20 companies and received 20 errors.

Responses:

```
--- [1/20] ---
[flex]
{
  "agent_performance": {
    "status": "success"
  },
  "agent_payload": "A|B|A|59,60|51,46,53,50,45"
}
--- agent_payload ---
A|B|A|59,60|51,46,53,50,45

--- [2/20] ---
[kodiakrobotics]
{
  "agent_performance": {
    "status": "success"
  },
  "agent_payload": "A|B|B|5|3,4,18"
}
--- agent_payload ---
A|B|B|5|3,4,18

--- [3/20] ---
[magic]
{
  "agent_performance": {
    "status": "success"
  },
  "agent_payload": "{\"RealityCheck\":\"A\",\"MissionProductOrientation\":\"C\",\"USPresenceTimeZone\":\"A\",\"PossibleJobLinks\":[46],\"CultureLinksToExplore\":[45,25,26,27,31]}"
}
--- agent_payload ---
{"RealityCheck":"A","MissionProductOrientation":"C","USPresenceTimeZone":"A","PossibleJobLinks":[46],"CultureLinksToExplore":[45,25,26,27,31]}

--- [4/20] ---
[karbon]
Validation failed: Missing required field 'jobs'

--- model response ---
{
  "agent_performance": {
    "status": "success",
    "failure_note": null
  },
  "agent_payload": {
    "reality_check": "A",
    "mission_product_orientation": "B",
    "us_presence": "A",
    "possible_job_links": [77],
    "culture_links_to_explore": [75, 76, 40, 72, 42]
  }
}

--- [5/20] ---
[berry]
{
  "agent_performance": {
    "status": "success",
    "failure_note": null
  },
  "agent_payload": "{\"Reality_Check\":\"A\",\"Mission_Product_Orientation\":\"B\",\"US_Presence\":\"A\",\"POSSIBLE_JOB_LINKS\":[7],\"CULTURE_LINKS_TO_EXPLORE\":[10,5,3,7]}"
}
--- agent_payload ---
{"Reality_Check":"A","Mission_Product_Orientation":"B","US_Presence":"A","POSSIBLE_JOB_LINKS":[7],"CULTURE_LINKS_TO_EXPLORE":[10,5,3,7]}

--- [6/20] ---
[follettsoftware]
{
  "agent_performance": {
    "status": "success",
    "failure_note": ""
  },
  "agent_payload": "A|B|A|82,76,80|76,80,81,66,67"
}
--- agent_payload ---
A|B|A|82,76,80|76,80,81,66,67

--- [7/20] ---
[archesys]
{
  "agent_performance": {
    "status": "success",
    "failure_note": null
  },
  "agent_payload": "A|D|B|5,8,10|1,3,9,10,11"
}
--- agent_payload ---
A|D|B|5,8,10|1,3,9,10,11

--- [8/20] ---
[moonvalley]
Validation failed: Missing required field 'jobs'

--- model response ---
{
  "agent_performance": {
    "status": "success",
    "failure_note": null
  },
  "agent_payload": {
    "reality_check": "A",
    "mission_product_orientation": "B",
    "us_presence_time_zone": "A",
    "possible_job_links": [8],
    "culture_links_to_explore": [7, 3, 6, 20, 8]
  }
}

--- [9/20] ---
[lovable]
{
  "agent_performance": {
    "status": "success"
  },
  "agent_payload": "000|ERCA|MEAC|PGAA|JOB:16|CULT:38,3,27,37,34"
}
--- agent_payload ---
000|ERCA|MEAC|PGAA|JOB:16|CULT:38,3,27,37,34

--- [10/20] ---
[apolloio]
{
  "agent_performance": {
    "status": "success"
  },
  "agent_payload": "A|C|B|37,71|39,40,38,41,30"
}
--- agent_payload ---
A|C|B|37,71|39,40,38,41,30

--- [11/20] ---
[firstignite]
{
  "agent_performance": {
    "status": "success"
  },
  "agent_payload": "A|B|A|15|13,16,14"
}
--- agent_payload ---
A|B|A|15|13,16,14

--- [12/20] ---
[sardine]
{
  "agent_performance": {
    "status": "success"
  },
  "agent_payload": "A|B|B|52,36,51,32,33|51,36,3,1,52"
}
--- agent_payload ---
A|B|B|52,36,51,32,33|51,36,3,1,52

--- [13/20] ---
[educatoai]
{
  "agent_performance": {
    "status": "success"
  },
  "agent_payload": "A|B|A|14|12"
}
--- agent_payload ---
A|B|A|14|12

--- [14/20] ---
[leadbank]
{
  "agent_performance": {
    "status": "success",
    "failure_note": ""
  },
  "agent_payload": "A|B|A|12,11,30,13|12,13,11,30"
}
--- agent_payload ---
A|B|A|12,11,30,13|12,13,11,30

--- [15/20] ---
[cais]
{
  "agent_performance": {
    "status": "success",
    "failure_note": null
  },
  "agent_payload": "{\"reality_check\": \"A\", \"mission_product\": \"B\", \"us_presence\": \"A\", \"possible_job_links\": [17], \"culture_links\": [13, 16, 14, 15, 20]}"
}
--- agent_payload ---
{"reality_check": "A", "mission_product": "B", "us_presence": "A", "possible_job_links": [17], "culture_links": [13, 16, 14, 15, 20]}

--- [16/20] ---
[outreach]
Validation failed: Missing required field 'jobs'

--- model response ---
{
  "agent_performance": {
    "status": "success",
    "failure_note": null
  },
  "agent_payload": {
    "reality_check": "A",
    "mission_product": "C",
    "us_presence": "A",
    "possible_job_links": [74, 73, 72],
    "culture_links_to_explore": [76, 74, 77, 78, 75]
  }
}

--- [17/20] ---
[humanagency]
{
  "agent_performance": {
    "status": "success",
    "failure_note": null
  },
  "agent_payload": "A|B|A|35|35,4,3,38,2"
}
--- agent_payload ---
A|B|A|35|35,4,3,38,2

--- [18/20] ---
[fictiv]
Validation failed: Missing required field 'jobs'

--- model response ---
{
  "agent_performance": {
    "status": "success",
    "failure_note": null
  },
  "agent_payload": {
    "reality_check": "A",
    "mission_product_orientation": "B",
    "us_presence": "A",
    "possible_job_links": [54],
    "culture_links_to_explore": [49, 51, 52, 53, 40]
  }
}

--- [19/20] ---
[1mind]
{
  "agent_performance": {
    "status": "success"
  },
  "agent_payload": "A|C|A|[7]|[2,7]"
}
--- agent_payload ---
A|C|A|[7]|[2,7]

--- [20/20] ---
[olo]
{
  "agent_performance": {
    "status": "success"
  },
  "agent_payload": "A|B|A|30,29,48|30,48,49,29"
}
--- agent_payload ---
A|B|A|30,29,48|30,48,49,29
```

Log:

\[2026-06-10 16:59:55\] INFO src.core.roster: \[outreach\] company state WEBSITE_FOUND -> PREFILTER_UNKNOWN (batch_id=prefilter-762456bc-771f-4bfc-a4c5-b4e1a0400c6d)

\[2026-06-10 16:59:55\] ERROR src.core.roster: \[outreach\] prefilter error: Missing required field 'jobs'

\[2026-06-10 16:59:55\] INFO src.external.deepseek: LLM deepseek task=prefilter_company 36.2s stop=end_turn tokens in=1258 out=2880

\[2026-06-10 16:59:55\] ERROR src.core.agent: do_task decode failed. task_key='prefilter_company' error=\[prefilter_company\] bad position field in line: 'A|B|A|35|35,4,3,38,2'
\[2026-06-10 16:59:55\] INFO src.core.roster: \[humanagency\] company state WEBSITE_FOUND -> PREFILTER_UNKNOWN (batch_id=prefilter-762456bc-771f-4bfc-a4c5-b4e1a0400c6d)

\[2026-06-10 16:59:55\] ERROR src.core.roster: \[humanagency\] prefilter error: \[prefilter_company\] bad position field in line: 'A|B|A|35|35,4,3,38,2'
\[2026-06-10 16:59:55\] INFO src.external.deepseek: LLM deepseek task=prefilter_company 26.1s stop=end_turn tokens in=5579 out=1424

\[2026-06-10 16:59:55\] ERROR src.core.agent: do_task validation failed. task_key='prefilter_company' error=Missing required field 'jobs'

\[2026-06-10 16:59:53\] INFO src.core.roster: \[moonvalley\] company state WEBSITE_FOUND -> PREFILTER_UNKNOWN (batch_id=prefilter-762456bc-771f-4bfc-a4c5-b4e1a0400c6d)

\[2026-06-10 16:59:53\] ERROR src.core.roster: \[moonvalley\] prefilter error: Missing required field 'jobs'

\[2026-06-10 16:59:53\] INFO src.external.deepseek: LLM deepseek task=prefilter_company 29.0s stop=end_turn tokens in=1353 out=2369

\[2026-06-10 16:59:53\] ERROR src.core.agent: do_task decode failed. task_key='prefilter_company' error=\[prefilter_company\] unexpected trailing content in grades-only line: '000|ERCA|MEAC|PGAA|JOB:16|CULT:38,3,27,37,34'
\[2026-06-10 16:59:53\] INFO src.core.roster: \[lovable\] company state WEBSITE_FOUND -> PREFILTER_UNKNOWN (batch_id=prefilter-762456bc-771f-4bfc-a4c5-b4e1a0400c6d)

\[2026-06-10 16:59:53\] ERROR src.core.roster: \[lovable\] prefilter error: \[prefilter_company\] unexpected trailing content in grades-only line: '000|ERCA|MEAC|PGAA|JOB:16|CULT:38,3,27,37,34'
\[2026-06-10 16:59:53\] INFO src.external.deepseek: LLM deepseek task=prefilter_company 31.8s stop=end_turn tokens in=3577 out=2707

\[2026-06-10 16:59:53\] ERROR src.core.agent: do_task decode failed. task_key='prefilter_company' error=\[prefilter_company\] bad position field in line: 'A|C|B|37,71|39,40,38,41,30'
\[2026-06-10 16:59:53\] INFO src.core.roster: \[apolloio\] company state WEBSITE_FOUND -> PREFILTER_UNKNOWN (batch_id=prefilter-762456bc-771f-4bfc-a4c5-b4e1a0400c6d)

\[2026-06-10 16:59:53\] ERROR src.core.roster: \[apolloio\] prefilter error: \[prefilter_company\] bad position field in line: 'A|C|B|37,71|39,40,38,41,30'
\[2026-06-10 16:59:53\] INFO src.external.deepseek: LLM deepseek task=prefilter_company 22.1s stop=end_turn tokens in=2652 out=1766

\[2026-06-10 16:59:53\] ERROR src.core.agent: do_task decode failed. task_key='prefilter_company' error=\[prefilter_company\] bad position field in line: 'A|B|A|15|13,16,14'
\[2026-06-10 16:59:53\] INFO src.core.roster: \[firstignite\] company state WEBSITE_FOUND -> PREFILTER_UNKNOWN (batch_id=prefilter-762456bc-771f-4bfc-a4c5-b4e1a0400c6d)

\[2026-06-10 16:59:53\] ERROR src.core.roster: \[firstignite\] prefilter error: \[prefilter_company\] bad position field in line: 'A|B|A|15|13,16,14'
\[2026-06-10 16:59:53\] INFO src.external.deepseek: LLM deepseek task=prefilter_company 23.8s stop=end_turn tokens in=2949 out=1957

\[2026-06-10 16:59:53\] ERROR src.core.agent: do_task decode failed. task_key='prefilter_company' error=\[prefilter_company\] bad position field in line: 'A|B|B|52,36,51,32,33|51,36,3,1,52'
\[2026-06-10 16:59:53\] INFO src.core.roster: \[sardine\] company state WEBSITE_FOUND -> PREFILTER_UNKNOWN (batch_id=prefilter-762456bc-771f-4bfc-a4c5-b4e1a0400c6d)

\[2026-06-10 16:59:53\] ERROR src.core.roster: \[sardine\] prefilter error: \[prefilter_company\] bad position field in line: 'A|B|B|52,36,51,32,33|51,36,3,1,52'
\[2026-06-10 16:59:53\] INFO src.external.deepseek: LLM deepseek task=prefilter_company 34.5s stop=end_turn tokens in=2128 out=2588

\[2026-06-10 16:59:53\] ERROR src.core.agent: do_task decode failed. task_key='prefilter_company' error=\[prefilter_company\] bad position field in line: 'A|B|A|14|12'
\[2026-06-10 16:59:53\] INFO src.core.roster: \[educatoai\] company state WEBSITE_FOUND -> PREFILTER_UNKNOWN (batch_id=prefilter-762456bc-771f-4bfc-a4c5-b4e1a0400c6d)

\[2026-06-10 16:59:53\] ERROR src.core.roster: \[educatoai\] prefilter error: \[prefilter_company\] bad position field in line: 'A|B|A|14|12'
\[2026-06-10 16:59:53\] INFO src.external.deepseek: LLM deepseek task=prefilter_company 32.0s stop=end_turn tokens in=1735 out=2655

\[2026-06-10 16:59:53\] ERROR src.core.agent: do_task decode failed. task_key='prefilter_company' error=\[prefilter_company\] bad position field in line: 'A|B|A|12,11,30,13|12,13,11,30'
\[2026-06-10 16:59:53\] INFO src.core.roster: \[leadbank\] company state WEBSITE_FOUND -> PREFILTER_UNKNOWN (batch_id=prefilter-762456bc-771f-4bfc-a4c5-b4e1a0400c6d)

\[2026-06-10 16:59:53\] ERROR src.core.roster: \[leadbank\] prefilter error: \[prefilter_company\] bad position field in line: 'A|B|A|12,11,30,13|12,13,11,30'
\[2026-06-10 16:59:53\] INFO src.external.deepseek: LLM deepseek task=prefilter_company 28.7s stop=end_turn tokens in=1752 out=1775

\[2026-06-10 16:59:53\] ERROR src.core.agent: do_task decode failed. task_key='prefilter_company' error=\[prefilter_company\] bad position field in line: '{"reality_check": "A", "mission_product": "B", "us_presence": "A", "possible_job_links": \[17\], "culture_links": \[13, 16, 14, 15, 20\]}'

\[2026-06-10 16:59:53\] INFO src.core.roster: \[cais\] company state WEBSITE_FOUND -> PREFILTER_UNKNOWN (batch_id=prefilter-762456bc-771f-4bfc-a4c5-b4e1a0400c6d)

\[2026-06-10 16:59:53\] ERROR src.core.roster: \[cais\] prefilter error: \[prefilter_company\] bad position field in line: '{"reality_check": "A", "mission_product": "B", "us_presence": "A", "possible_job_links": \[17\], "culture_links": \[13, 16, 14, 15, 20\]}'

\[2026-06-10 16:59:53\] INFO src.external.deepseek: LLM deepseek task=prefilter_company 27.6s stop=end_turn tokens in=2674 out=1305

\[2026-06-10 16:59:53\] ERROR src.core.agent: do_task validation failed. task_key='prefilter_company' error=Missing required field 'jobs'

\[2026-06-10 16:59:41\] INFO src.core.roster: \[karbon\] company state WEBSITE_FOUND -> PREFILTER_UNKNOWN (batch_id=prefilter-762456bc-771f-4bfc-a4c5-b4e1a0400c6d)

\[2026-06-10 16:59:41\] ERROR src.core.roster: \[karbon\] prefilter error: Missing required field 'jobs'

\[2026-06-10 16:59:41\] INFO src.external.deepseek: LLM deepseek task=prefilter_company 27.5s stop=end_turn tokens in=1474 out=2405

\[2026-06-10 16:59:41\] ERROR src.core.agent: do_task decode failed. task_key='prefilter_company' error=\[prefilter_company\] bad position field in line: '{"Reality_Check":"A","Mission_Product_Orientation":"B","US_Presence":"A","POSSIBLE_JOB_LINKS":\[7\],"CULTURE_LINKS_TO_EXPLORE":\[10,5,3,7\]}'

\[2026-06-10 16:59:41\] INFO src.core.roster: \[berry\] company state WEBSITE_FOUND -> PREFILTER_UNKNOWN (batch_id=prefilter-762456bc-771f-4bfc-a4c5-b4e1a0400c6d)

\[2026-06-10 16:59:41\] ERROR src.core.roster: \[berry\] prefilter error: \[prefilter_company\] bad position field in line: '{"Reality_Check":"A","Mission_Product_Orientation":"B","US_Presence":"A","POSSIBLE_JOB_LINKS":\[7\],"CULTURE_LINKS_TO_EXPLORE":\[10,5,3,7\]}'

\[2026-06-10 16:59:41\] INFO src.external.deepseek: LLM deepseek task=prefilter_company 25.1s stop=end_turn tokens in=3145 out=1982

\[2026-06-10 16:59:41\] ERROR src.core.agent: do_task decode failed. task_key='prefilter_company' error=\[prefilter_company\] bad position field in line: 'A|B|A|82,76,80|76,80,81,66,67'
\[2026-06-10 16:59:41\] INFO src.core.roster: \[follettsoftware\] company state WEBSITE_FOUND -> PREFILTER_UNKNOWN (batch_id=prefilter-762456bc-771f-4bfc-a4c5-b4e1a0400c6d)

\[2026-06-10 16:59:41\] ERROR src.core.roster: \[follettsoftware\] prefilter error: \[prefilter_company\] bad position field in line: 'A|B|A|82,76,80|76,80,81,66,67'
\[2026-06-10 16:59:41\] INFO src.external.deepseek: LLM deepseek task=prefilter_company 32.1s stop=end_turn tokens in=2311 out=2716

\[2026-06-10 16:59:41\] ERROR src.core.agent: do_task decode failed. task_key='prefilter_company' error=\[prefilter_company\] bad position field in line: 'A|D|B|5,8,10|1,3,9,10,11'
\[2026-06-10 16:59:41\] INFO src.core.roster: \[archesys\] company state WEBSITE_FOUND -> PREFILTER_UNKNOWN (batch_id=prefilter-762456bc-771f-4bfc-a4c5-b4e1a0400c6d)

\[2026-06-10 16:59:41\] ERROR src.core.roster: \[archesys\] prefilter error: \[prefilter_company\] bad position field in line: 'A|D|B|5,8,10|1,3,9,10,11'
\[2026-06-10 16:59:41\] INFO src.core.agent: run_next chain entry: task=prefilter_company batch_id=prefilter-762456bc-771f-4bfc-a4c5-b4e1a0400c6d

\[2026-06-10 16:59:41\] INFO src.external.deepseek: LLM deepseek task=prefilter_company 27.7s stop=end_turn tokens in=1639 out=2338

\[2026-06-10 16:59:41\] ERROR src.core.agent: do_task validation failed. task_key='prefilter_company' error=Missing required field 'jobs'

\[2026-06-10 16:59:37\] INFO src.core.agent: run_next chain entry: task=prefilter_company batch_id=prefilter-762456bc-771f-4bfc-a4c5-b4e1a0400c6d

\[2026-06-10 16:59:37\] INFO src.core.agent: run_next chain entry: task=prefilter_company batch_id=prefilter-762456bc-771f-4bfc-a4c5-b4e1a0400c6d

\[2026-06-10 16:59:37\] INFO src.core.agent: run_next chain entry: task=prefilter_company batch_id=prefilter-762456bc-771f-4bfc-a4c5-b4e1a0400c6d

\[2026-06-10 16:59:37\] INFO src.core.agent: run_next chain entry: task=prefilter_company batch_id=prefilter-762456bc-771f-4bfc-a4c5-b4e1a0400c6d

\[2026-06-10 16:59:37\] INFO src.core.agent: run_next chain entry: task=prefilter_company batch_id=prefilter-762456bc-771f-4bfc-a4c5-b4e1a0400c6d

\[2026-06-10 16:59:37\] INFO src.core.agent: run_next chain entry: task=prefilter_company batch_id=prefilter-762456bc-771f-4bfc-a4c5-b4e1a0400c6d

\[2026-06-10 16:59:37\] INFO src.core.agent: run_next chain entry: task=prefilter_company batch_id=prefilter-762456bc-771f-4bfc-a4c5-b4e1a0400c6d

\[2026-06-10 16:59:37\] INFO src.core.agent: run_next chain entry: task=prefilter_company batch_id=prefilter-762456bc-771f-4bfc-a4c5-b4e1a0400c6d

\[2026-06-10 16:59:37\] INFO src.core.agent: run_next chain entry: task=prefilter_company batch_id=prefilter-762456bc-771f-4bfc-a4c5-b4e1a0400c6d

\[2026-06-10 16:59:37\] INFO src.core.agent: run_next chain entry: task=prefilter_company batch_id=prefilter-762456bc-771f-4bfc-a4c5-b4e1a0400c6d

\[2026-06-10 16:59:37\] INFO src.core.agent: run_next chain entry: task=prefilter_company batch_id=prefilter-762456bc-771f-4bfc-a4c5-b4e1a0400c6d

\[2026-06-10 16:59:37\] INFO src.core.agent: run_next chain entry: task=prefilter_company batch_id=prefilter-762456bc-771f-4bfc-a4c5-b4e1a0400c6d

\[2026-06-10 16:59:37\] INFO src.core.agent: run_next chain entry: task=prefilter_company batch_id=prefilter-762456bc-771f-4bfc-a4c5-b4e1a0400c6d

\[2026-06-10 16:59:37\] INFO src.core.agent: run_next chain entry: task=prefilter_company batch_id=prefilter-762456bc-771f-4bfc-a4c5-b4e1a0400c6d

\[2026-06-10 16:59:37\] WARNING src.external.playwright: get_visible_text: attempt 1 failed: TimeoutError: Page.goto: Timeout 30000ms exceeded.

Call log:

* navigating to "[https://www.olo.com/](<https://www.olo.com/>)", waiting until "load"

\[2026-06-10 16:59:37\] INFO src.core.agent: run_next chain entry: task=prefilter_company batch_id=prefilter-762456bc-771f-4bfc-a4c5-b4e1a0400c6d

\[2026-06-10 16:59:37\] INFO src.core.agent: run_next chain entry: task=prefilter_company batch_id=prefilter-762456bc-771f-4bfc-a4c5-b4e1a0400c6d

\[2026-06-10 16:59:37\] INFO src.core.agent: run_next chain entry: task=prefilter_company batch_id=prefilter-762456bc-771f-4bfc-a4c5-b4e1a0400c6d

\[2026-06-10 16:59:37\] INFO src.core.agent: run_next chain entry: task=prefilter_company batch_id=prefilter-762456bc-771f-4bfc-a4c5-b4e1a0400c6d

\[2026-06-10 16:59:37\] INFO src.external.deepseek: LLM deepseek task=prefilter_company 14.8s stop=end_turn tokens in=1309 out=1108

\[2026-06-10 16:59:37\] ERROR src.core.agent: do_task decode failed. task_key='prefilter_company' error=\[prefilter_company\] bad position field in line: 'A|B|B|5|3,4,18'
\[2026-06-10 16:59:37\] INFO src.core.roster: \[kodiakrobotics\] company state WEBSITE_FOUND -> PREFILTER_UNKNOWN (batch_id=prefilter-762456bc-771f-4bfc-a4c5-b4e1a0400c6d)

\[2026-06-10 16:59:37\] ERROR src.core.roster: \[kodiakrobotics\] prefilter error: \[prefilter_company\] bad position field in line: 'A|B|B|5|3,4,18'
\[2026-06-10 16:59:37\] INFO src.external.deepseek: LLM deepseek task=prefilter_company 19.6s stop=end_turn tokens in=4966 out=1647

\[2026-06-10 16:59:37\] ERROR src.core.agent: do_task decode failed. task_key='prefilter_company' error=\[prefilter_company\] bad position field in line: '{"RealityCheck":"A","MissionProductOrientation":"C","USPresenceTimeZone":"A","PossibleJobLinks":\[46\],"CultureLinksToExplore":\[45,25,26,27,31\]}'

\[2026-06-10 16:59:37\] INFO src.core.roster: \[magic\] company state WEBSITE_FOUND -> PREFILTER_UNKNOWN (batch_id=prefilter-762456bc-771f-4bfc-a4c5-b4e1a0400c6d)

\[2026-06-10 16:59:37\] ERROR src.core.roster: \[magic\] prefilter error: \[prefilter_company\] bad position field in line: '{"RealityCheck":"A","MissionProductOrientation":"C","USPresenceTimeZone":"A","PossibleJobLinks":\[46\],"CultureLinksToExplore":\[45,25,26,27,31\]}'

\[2026-06-10 16:59:37\] INFO src.external.deepseek: LLM deepseek task=prefilter_company 22.9s stop=end_turn tokens in=3038 out=1923

\[2026-06-10 16:59:37\] ERROR src.core.agent: do_task validation failed. task_key='prefilter_company' error=Missing required field 'jobs'

\[2026-06-10 16:58:40\] INFO dispatch.scheduler: Dispatching prefilter — 123 available, batch prefilter-762456bc-771f-4bfc-a4c5-b4e1a0400c6d

\[2026-06-10 16:58:40\] INFO src.core.agent: run_next chain entry: task=prefilter_company batch_id=prefilter-762456bc-771f-4bfc-a4c5-b4e1a0400c6d

\[2026-06-10 16:58:40\] INFO src.external.deepseek: LLM deepseek task=prefilter_company 30.9s stop=end_turn tokens in=5613 out=2557

\[2026-06-10 16:58:40\] ERROR src.core.agent: do_task decode failed. task_key='prefilter_company' error=\[prefilter_company\] bad position field in line: 'A|B|A|59,60|51,46,53,50,45'
\[2026-06-10 16:58:40\] INFO src.core.roster: \[flex\] company state WEBSITE_FOUND -> PREFILTER_UNKNOWN (batch_id=prefilter-762456bc-771f-4bfc-a4c5-b4e1a0400c6d)

\[2026-06-10 16:58:40\] ERROR src.core.roster: \[flex\] prefilter error: \[prefilter_company\] bad position field in line: 'A|B|A|59,60|51,46,53,50,45'

### Comments

#### chuckles — 2026-06-12T00:24:58.300Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-606** | Prefilter no longer routes retryable failures to **PREFILTER_UNKNOWN**. Added **WEBSITE_FOUND_RETRY** company state with dispatch retry seed; **ROSTER_CONFIG["prefilter"]** now uses `retry_state` / `error_state`. `_prefilter_fail` sends dec |

Local `dev` merged via prep-uat. Re-run the **Manual test steps** from the latest prep-uat comment on this ticket; pay extra attention to the bugs above.

— Chuckles

#### chuckles — 2026-06-12T00:18:20.074Z
## Git dispatch (UAT bug wave)

| Ticket | Publish ref |
|--------|-------------|
| AST-606 | `sub/AST-602/AST-606-prefilter-retry-states` |

**Joan session:** `dd7666a7-4335-4d30-96b1-d067f5e0ffd1`  
**Seed:** `origin/ftr/ast-602-prefilter-company-failing` @ `001a7589`

#### susan — 2026-06-12T00:15:58.460Z
It appears that we are not using "WEBSITE_FOUND_RETRY" for the prefilter company task.  We need to add that so that error cases where the rubric is incomplete should get a retry, in case it was an incidental error from the agent.  "PREFILTER_UNKNOWN" should not be a state at all, it breaks the pattern.  Either it's "ERROR_PREFILTER" or it's "WEBSITE_FOUND_RETRY", right?

#### chuckles — 2026-06-12T00:04:29.106Z
## Manual test steps

1. Restart the app if it is running (`src/ui/server.py`).
2. Pick a candidate with **company_prefilter** rubric data loaded.
3. Queue **prefilter company** on 5–10 **WEBSITE_FOUND** companies (dispatch or manual coat-check).
4. Confirm companies with `agent_performance.status = success` leave **PREFILTER_UNKNOWN** — they should reach **PREFILTER_PASSED**, **PREFILTER_FAILED**, **TO_WATCH**, or **IGNORE** per inflow vs legacy path.
5. Spot-check one pass: **prefilter_company_notes** show hydrated grade reasons (vector + grade + confidence + reason text); **prefilter_score** persisted on pass.
6. Spot-check link fields: **possible_job_links** and **culture_links_to_explore** present when model returned them; empty lists when absent.
7. Replay at least one repro shape from the Original brief (letter-pipe `A|B|A|15|13,16,14`, dict JSON karbon-style, or encoded `000|ERCA|…|JOB:16|CULT:…`) via fixture/component test or live batch — no decode/hydration exception when model succeeded.

`origin/ftr/ast-602-prefilter-company-failing` @ `001a7589` · local `dev` merged (`d9417d24`). Restart app if running.

**Radia audit (via Chuckles):** Parent AC 1–5 **PASS** on composite ftr; AC 6 (Susan production batch rate) awaits this UAT. Discuss items from AST-603 review: sparse partial rubric rows fail closed; letter-pipe default confidence=3 — watch pass/fail rates.

— Chuckles

#### chuckles — 2026-06-12T00:03:10.139Z
**[land-ftr] blocked:** merge conflict in `docs/ASTRAL_TEST_BIBLE.md` merging `origin/ftr/ast-602-prefilter-company-failing` into local `dev`.

@Betty White — resolve bible conflict on `dev-betty`, reconcile with ftr tip, then Chuckles re-runs `land-ftr AST-602`.

— Chuckles

#### susan — 2026-06-11T23:30:58.791Z
@chuckles Sorry for the disconnection, try now?

#### chuckles — 2026-06-10T18:29:15.940Z
@susan **Blocked:** `git.sh session-open` could not push `origin/ftr/ast-602-prefilter-company-failing` or `origin/sub/AST-602/AST-603-consult-parity-prefilter-hydration` — SSH to github.com:22 times out; HTTPS push has no credentials. Child **AST-603** dispatched (Hedy, Todo). Joan session `dd7666a7-4335-4d30-96b1-d067f5e0ffd1` opened locally only. Re-run session-open when GitHub is reachable, then reassign parent to Chuckles to resume pipeline.

— Chuckles

#### chuckles — 2026-06-10T18:28:46.817Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-602 (parent) | ftr/ast-602-prefilter-company-failing |
| AST-603 | sub/AST-602/AST-603-consult-parity-prefilter-hydration |

**Note:** `git.sh session-open` ref seed blocked (GitHub SSH timeout / HTTPS push auth). Joan ledger + epic sessions opened locally; re-run `session-open` when network/auth available to seed `origin/ftr/*` and `origin/sub/*`.

## Epic sessions (headless — Chuckles injects in every spawn; agents do not read Linear)

| Agent | Session id | Ticket | Role |
|-------|------------|--------|------|
| Joan | `dd7666a7-4335-4d30-96b1-d067f5e0ffd1` | AST-602 (parent) | git |
| Hedy | `5a67c075-1109-436c-9a89-3bd93f41e25f` | AST-603 | engineer |
| Betty | `1f8f23cd-c4f1-4d00-a55d-2763107e899a` | AST-603 | qa |
| Radia | `92c116c3-8426-4150-ac17-11a4dc61669d` | AST-603 | review |

Chuckles authoritative copy: `debug/AST-602-agents.txt`.

#### susan — 2026-06-10T18:21:14.981Z
Are we storing a score for the prefilter company based on our rubric quantification model?  If not, please add that before proceeding.

#### susan — 2026-06-10T17:22:17.815Z
@chuckles I'm concerned about how you are framing this ticket.  It should simply reuse the parsing pattern we use for consult rubrics, because prefilter is now a rubric type prompt.

Can you rewrite the plan to make the prefilter_company response processing to use the "hydrated" responses, just like consult gets the decoded responses from agent?

#### chuckles — 2026-06-10T17:07:50.494Z
@susan

1. After fix, should **prefilter company** prompt/instructions be tightened so models prefer one canonical encoded line format, or is long-term tolerance for multiple shapes (pipe letters, JSON) the desired steady state?

---

_Implementation detail may live in git history on `origin/dev`._
