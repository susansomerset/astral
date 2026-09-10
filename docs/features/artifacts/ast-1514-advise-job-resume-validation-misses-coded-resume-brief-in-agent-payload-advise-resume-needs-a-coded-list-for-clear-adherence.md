# AST-1514 — advise_job_resume validation misses coded resume_brief in agent_payload (Advise resume needs a coded list for clear adherence)

<!-- linear-archive: AST-1514 archived 2026-09-09 -->

## Linear archive (AST-1514)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1514/advise-job-resume-validation-misses-coded-resume-brief-in-agent  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** None / 2  
**Parent:** AST-1460 — Advise resume needs a coded list for clear adherence  
**Blocked by / blocks / related:** parent: AST-1460

### Description

## Susan's report (verbatim)

[bug]

```
"agent_payload": "{\n \"resume_brief\": \"[R1] …\",\n \"cover_letter_direction\": \"...\",\n \"ask_candidate\": \"...\"\n}"
8/26/26, 4:57:52 PM	ERROR	src.core.agent	do_task validation failed. task_key='advise_job_resume' error=RESUME BRIEF section missing or incomplete
```

Looks like she sent the section but we didn't catch it.

## As-is

When Estelle's `advise_job_resume` response includes a coded `resume_brief` string inside `agent_payload` JSON, `do_task` validation still fails with `RESUME BRIEF section missing or incomplete` — the validator does not recognize the payload Susan captured in the debug log.

## To-be

`advise_job_resume` validation should accept and parse Estelle's coded RESUME BRIEF from the response (including when it arrives nested in `agent_payload` JSON), so the hop succeeds when she delivers the brief.

## Proposed change (make-fix)

- [X] `TASK_CONFIG["advise_job_resume"]["resume_advice_json_key"]` = `"resume_brief"`
- [X] Candidate coerce: JSON-string / dict `resume_brief` → coded-list body; plain-text header path retained
- [X] `do_task` validate + persist accept `str` and `dict` post-unwrap payloads
- [X] Tracker extract/persist accept same str|dict input
- [X] `[bug-repro]` TestAst1514AdviseResumeBriefJsonPayload + TestAst1514DoTaskResumeBriefJsonPersist green

## Suggested engineer

Ada Lovelace ([AST-1507](https://linear.app/astralcareermatch/issue/AST-1507/estelle-coded-resume-advice-list-advise-resume-needs-a-coded-list-for) — Estelle coded resume-advice list)

### Comments

#### ada — 2026-08-27T01:36:50.905Z
`origin/sub/AST-1460/AST-1514-advise-resume-brief-validation` @ `aa315cda` · nested brief green

#### betty — 2026-08-27T01:34:23.037Z
[bug-repro]
`origin/sub/AST-1460/AST-1514-advise-resume-brief-validation` @ `0676c12b` · repro lands red, awaits fix

#### joan — 2026-08-27T01:30:43.043Z
[board-joan]  CANON: OK

Proposed change adds `resume_advice_json_key` to existing `TASK_CONFIG["advise_job_resume"]` and widens candidate/agent/tracker coerce paths — conforms to `pattern.config.config-block` and `astral.config.config-source-of-truth` / `astral.standards.no-hardcoded-sets`. No active statute or pattern mandates text-only advise bodies; dual JSON fallback does not contradict `astral.agent.do-task-delegation`. No canon file update required before make-fix.

context_tokens≈56000

#### betty — 2026-08-27T01:30:19.098Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/candidate.md § AST-1507 (+ agent.md/tracker.md) — missing coverage for JSON-string and dict agent_payload.resume_brief path (plain-text RESUME BRIEF only today); Blast radius requires new cases before make-fix

#### ada — 2026-08-27T01:29:17.546Z
`origin/sub/AST-1460/AST-1514-advise-resume-brief-validation` @ `5945ffabc8c0616b6557c98f87b36b7465676ca1` · nested brief plan

---

_Implementation detail may live in git history on `origin/dev`._
