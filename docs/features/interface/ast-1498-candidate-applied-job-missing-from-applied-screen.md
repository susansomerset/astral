# AST-1498 — CANDIDATE_APPLIED job missing from Applied screen

<!-- linear-archive: AST-1498 archived 2026-09-09 -->

## Linear archive (AST-1498)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1498/candidate-applied-job-missing-from-applied-screen  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1485 — Enable Applied job list in nav  
**Blocked by / blocks / related:** parent: AST-1485

### Description

## Report (verbatim)

[bug]

There is a job in state CANDIDATE_APPLIED that does not appear on the Applied screen.

## As-is

A job already in `CANDIDATE_APPLIED` does not show up on the Applied jobs screen (`/jobs/applied`).

## To-be

Every job in `CANDIDATE_APPLIED` (and the rest of the applied-view state set) for the selected candidate appears on the Applied screen.

## Suggested engineer

Ada Lovelace

### Comments

#### radia — 2026-08-26T19:45:39.470Z
[code-rubric] PROCEED (Commit: f350306285181e3af00f1707769568a8cabb7cc7) stem linkage repair clean — [bug-repro] asserts correct symptom; What must still hold intact.

#### chuckles — 2026-08-26T19:15:27.029Z
[agent-busy-timeout] blocked: Cursor conversation still busy after 20m call-wait (spawn=`8642c77e`, attempts=36).
- parent: `AST-1485`
- agent: **Radia** role=review `review-fix` on `AST-1498`
- AGENT_SESSION: `fd435942-e4c9-4db3-a324-056a745eb804`

Do **not** `agent create-chat` and do **not** treat this as `[thread-missing]` — the Thread UUID is fine; another run held it.

#### betty — 2026-08-26T18:16:26.535Z
[bug-repro]
`origin/sub/AST-1485/AST-1498-candidate-applied-missing-from-applied-screen` @ `4772a3e8` · repro lands red, awaits fix

#### joan — 2026-08-26T18:10:00.839Z
[board-joan]  CANON: OK

Proposed change stays within existing layer law: `ui` → `core.roster` (`get_company` / `update_company`) matches `api_companies.py` precedent; job transitions still via `transition_job_state`; `APPLIED_JOB_STATES` remains config-sourced. Repair-on-read for NULL `company.candidate_id` on stem/meteorite slugs is a scoped linkage fix, not seed/catalog hot-path work (`astral.seed.boot-only-not-hot-path` is boot/migration-only). No statute or approved-pattern update required before `make-fix`.

context_tokens≈38000

#### betty — 2026-08-26T18:09:35.579Z
[board-betty] TESTS: REVISE
What: docs/test-bible/ui/api/api_jobs.md § AST-1479/1488 — no repro for NULL company.candidate_id stem job missing from view=applied; need qa-fix [bug-repro]; test_list_applied_uses_applied_job_states + JobsApplied Interview POST body will break on supplement pass / candidate_id in body.

#### ada — 2026-08-26T18:02:09.312Z
`origin/sub/AST-1485/AST-1498-candidate-applied-missing-from-applied-screen` @ `523fa8672470717a2d217c268bb02d24a155a927` · company linkage repair

#### susan — 2026-08-26T17:58:19.138Z
No repro.  Just confirm it is correctly fetching the candidates jobs in the correct state.

#### ada — 2026-08-26T15:46:19.919Z
Need a concrete repro before I can write Proposed change — on `origin/dev` @ `ca860885` the AST-1488 slice looks intact (`APPLIED_JOB_STATES` includes `CANDIDATE_APPLIED`, `GET /api/jobs?view=applied` calls `list_jobs` with that set + `candidate_id`, `JobsApplied` fetches that URL). Local DBs have zero applied-state jobs, so I cannot confirm a code defect vs candidate-scope miss.

@susan please reply with:
1. `astral_job_id` of the missing job
2. Selected candidate id when on `/jobs/applied`
3. Where you see `CANDIDATE_APPLIED` (Recommended / Job Detail / admin SQL / other)
4. Optional: Network tab for `GET /api/jobs?view=applied&candidate_id=…` (status + whether that job id is in the JSON)

Note: Applied list scopes via `company.candidate_id` (jobs have no `candidate_id` column). If the job’s company is not linked to the selected candidate, the API correctly returns `[]` for that picker — knowing (1)+(2) tells us whether that is the case.

---

_Implementation detail may live in git history on `origin/dev`._
