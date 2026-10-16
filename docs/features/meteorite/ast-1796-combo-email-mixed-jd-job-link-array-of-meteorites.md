# AST-1796 — Combo email: mixed JD + job-link array of meteorites

<!-- linear-archive: AST-1796 archived 2026-10-07 -->

## Linear archive (AST-1796)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1796/combo-email-mixed-jd-job-link-array-of-meteorites  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1783 — Parsing emails with linked job titles  
**Blocked by / blocks / related:** parent: AST-1783

### Description

## Report (verbatim)

\[bug\] See the attached sample message of a combo of job description and separate job links.  We need instruction to accommodate for this type in the response as an array of meteorites, some with job links, some with full job description contents (and link if available).

## As-is

Combo emails that mix an inline job description with separate job links are not classified into an array of mixed meteorites (some link-only, some with full JD content — and a link when available).

## To-be

Stage classify instructions accommodate that combo shape and return an array of meteorites covering both kinds: jobs with links, and jobs with full JD contents (plus link when present).

## Suggested engineer

Ada Lovelace (sibling [AST-1784](https://linear.app/astralcareermatch/issue/AST-1784/stage-meteorite-linked-title-prompts-parsing-emails-with-linked-job) — `stage_meteorite` prompts / classify instruction ownership)

### Comments

#### radia — 2026-09-25T18:59:49.418Z
AST-1796 REVIEW — CLEAN. Combo prompts + mapper blank-jd_text+http skip landed; [bug-repro] OK; What must still hold OK. No fix-now.

#### betty — 2026-09-25T18:54:53.646Z
[bug-repro]
`origin/sub/AST-1783/AST-1796-combo-email-mixed-jd-job-link-array` @ `b27fb038` · repro lands red, awaits fix

#### joan — 2026-09-25T18:52:20.656Z
[board-joan]  CANON: OK

#### betty — 2026-09-25T18:51:50.866Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/repo_admin_json.md + core/meteorite.md — no combo-prompt or blank-jd_text+http-job_link map coverage; blast radius touches AST-1784 lockstep + AST-1756 ingress fallback

#### ada — 2026-09-25T18:50:37.311Z
`origin/sub/AST-1783/AST-1796-combo-email-mixed-jd-job-link-array` @ `9b336492f5d2c98e53989ccbd24f2dc97650962a` · combo plan ready

---

_Implementation detail may live in git history on `origin/dev`._
