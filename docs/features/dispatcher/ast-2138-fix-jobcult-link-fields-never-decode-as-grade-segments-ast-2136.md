# AST-2138 — fix: JOB:/CULT: link fields never decode as grade segments (AST-2136)

<!-- linear-archive: AST-2138 archived 2026-10-16 -->

## Linear archive (AST-2138)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2138/fix-jobcult-link-fields-never-decode-as-grade-segments-ast-2136  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / 1  
**Parent:** AST-2136 — Prefilter errors  
**Blocked by / blocks / related:** parent: AST-2136

### Description

## What this implements

Fix for [AST-2136](https://linear.app/astralcareermatch/issue/AST-2136): `_decode_payload` must treat a `JOB:<n>` / `CULT:<n>` pipe field as link meta, never as a grade segment. Today the colon strip turns `JOB:3` into `JOB3`, which `_GRADE_SEG` reads as vector `JO`, grade `B`, confidence `3`. Hydrate then raises `No rubric criterion matching vector 'JO'` and the company goes to `ERROR_PREFILTER_COMPANY`. That was 13 of 15 errors in Somerset batch `prefilter_company-1cdeac6e-…`. As-is, To-be, the log excerpts and payload shapes are on AST-2136.

## Citations

none at intake — plan-fix names the statutes/patterns that govern the decode change.

## Scope

### Component scope

* `src/core/agent.py` — modified: `_decode_payload` classifies `JOB:`/`CULT:` link fields as grades because of the colon strip; this is where the misparse happens.
* `src/core/consult.py` — modified (small): `_should_decode_as_encoded_line` uses the same colon-strip + `_GRADE_SEG` test and should exclude link-prefixed fields the same way.

### Technical scope

* `src/core/agent.py` — modified function `_decode_payload`: add a link-prefix guard ahead of the grade-segment match, so a prefixed link field is never normalized into a grade token. A shared prefix pattern (the one `_LINK_PREFIX_RE` in `consult.py` already expresses) is plan-fix's call.
* `src/core/consult.py` — modified function `_should_decode_as_encoded_line`: the same guard, so routing detection and decoding agree on what counts as a grade segment.

## Acceptance criteria

1. `000|RCA5|HEA5|MLA3|PFA5|SOA5|JOB:3|CULT:7,27` decodes to the five rubric grades plus `possible_job_links == [3]` and `culture_links_to_explore == [7, 27]`, with no `JO` vector. The same holds for every `JOB:0`–`JOB:5`.
2. Multi-digit / list forms (`JOB:17`, `JOB:2,13,17`) and bracket tails (`[3]|[25,9,26]`) still decode as they do today.
3. Real grade tokens that the model prettifies with spaces, hyphens or colons (AST-483) still decode as grades.

## Boundaries

* The `SOFA5` malformed-segment errors (2 of 15) are out of scope — that's model malformation on the designed retry → error path.
* No change to retry/error routing (AST-1828) or to the rubric hydrate exceptions.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-2136-job-link-prefix-decode`, child `sub/AST-2136/AST-2138-job-link-prefix-decode`. Created at bug-fix dispatch.

### Comments

#### radia — 2026-10-12T14:50:58.389Z
[code-rubric] PROCEED (Commit: 3ddbcbf7c) shared link grade guard

#### hedy — 2026-10-12T14:46:20.956Z
`origin/sub/AST-2136/AST-2138-job-link-prefix-decode` @ `3ddbcbf7c` · note for test-fix: `TestAst697PrefilterBracketLinkDecode` / `TestAst603RubricNormalize` fail identically before and after this fix (`KeyError: company_id` / `jobs` — fixtures still expect job rows for company-entity `prefilter_company`); local env also lacks `nh3`/`asyncpg`.

#### joan — 2026-10-12T14:41:25.856Z
[board-joan]  CANON: OK

#### betty — 2026-10-12T14:40:52.509Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/agent.md + core/consult.md — missing coverage — no test hits JOB:0–JOB:5 (existing JOB: tests use JOB:16 only); need [bug-repro] rows for `…|SOA5|JOB:3|CULT:7,27` → possible_job_links [3] with no JO grade, `JOB:1|CULT:[]` → [1], and `_should_decode_as_encoded_line("000|JOB:3|CULT:7") is False`.

Blast radius check: no existing test breaks. AST-483 `test_decodes_whitespace_inside_grade_tokens_preserves_meta`, `test_should_decode_as_encoded_line_routing`, the JOB:16/CULT:38,3,27 cases, and test_consult.py ~L2374 all stay valid under `_grade_segment`. No test references `consult._LINK_PREFIX_RE` or monkeypatches `_GRADE_SEG`.

#### hedy — 2026-10-12T14:40:09.133Z
`origin/sub/AST-2136/AST-2138-job-link-prefix-decode` @ `317409812` · link prefix guards grade match

---

_Implementation detail may live in git history on `origin/dev`._
