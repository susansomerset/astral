# AST-1769 — Meteorite tab missing on Recommended job modal (prod)

<!-- linear-archive: AST-1769 archived 2026-10-02 -->

## Linear archive (AST-1769)

**Archived:** 2026-10-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1769/meteorite-tab-missing-on-recommended-job-modal-prod  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1685 — View related meteorite record data on recommended job modal  
**Blocked by / blocks / related:** parent: AST-1685

### Description

## Report (verbatim)

\[bug\] I saw this working earlier, but it doesn't seem to be working in the latest deployment to main/production.  The meteorite tab does not appear in the job modal.

## As-is

On main/production, opening a Recommended job modal does not show the Meteorite top tab.

## To-be

When a related `meteorite` row exists for the open job, the Recommended Job Report modal shows the Meteorite top tab (alongside Summary / Analysis / Artifacts / Discussion).

## Suggested engineer

Katherine Johnson (AST-1692 Meteorite pane; tab visibility gates on `related_meteorite` from AST-1691).

## Proposed change

- [X] Import `get_meteorite` in `api_jobs.py`; after reverse-link miss, resolve via `job.source == meteorite` + digit `source_entity_id` → `get_meteorite(sid)`; project same `related_meteorite` fields; read-only (no write of `astral_job_id`).

## QA test manifest

1. **\[bug-repro\]** `tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_detail_related_meteorite_source_entity_fallback`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_detail_related_meteorite_source_entity_fallback \
  -q
```

**Pass criterion:** that node green after make-fix — red against pre-fix product.

**Bible shasum (publish tip):**

* `docs/test-bible/ui/api/api_jobs.md` — `b5376712d4f0fdd1d1990e3aa35a7f6d466e195d`

### Comments

#### radia — 2026-09-23T01:30:15.387Z
[code-rubric] PROCEED (Commit: 2f990d20) source_entity fallback clean

#### betty — 2026-09-23T01:25:04.790Z
[bug-repro]
origin/sub/AST-1685/AST-1769-meteorite-tab-missing-prod @ 05cc0b3b · repro lands red, awaits fix

#### joan — 2026-09-23T01:22:20.568Z
[board-joan] CANON: OK

#### betty — 2026-09-23T01:20:48.017Z
[board-betty] TESTS: REVISE
What: docs/test-bible/ui/api/api_jobs.md § AST-1691 — missing coverage — no test for related_meteorite via job source/source_entity_id when reverse astral_job_id link is null (prod repro)

#### katherine — 2026-09-23T01:18:56.075Z
`origin/sub/AST-1685/AST-1769-meteorite-tab-missing-prod` @ `0d57074f76dbefab5a12472a18f8f57faacd64f6` · plan-fix ready

---

_Implementation detail may live in git history on `origin/dev`._
