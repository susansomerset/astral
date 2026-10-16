# AST-2136 — Prefilter errors

<!-- linear-archive: AST-2136 archived 2026-10-16 -->

## Linear archive (AST-2136)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2136/prefilter-errors  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Prior occurrences

* none found (0 searches — not labeled `production`, §0b skipped). Note: the `JO` signature below was already diagnosed in round 1 of [AST-1828](https://linear.app/astralcareermatch/issue/AST-1828) and dropped from that ticket's scope (Susan, question 3) — this ticket is that deferred fix.

## As-is

Somerset `prefilter_company` batch `prefilter_company-1cdeac6e-…` finished pass 4 / fail 3 / **error 15** out of 22. The errors split into two signatures:

1. `prefilter_company · ValueError · No rubric criterion matching vector 'JO'` **— 13 of 15.** The model returns the documented `JOB:`/`CULT:` link-tail form (e.g. `000|RCA5|HEA5|MLA3|PFA5|SOA5|JOB:3|CULT:7,27`). `_decode_payload` in `src/core/agent.py` strips spaces, hyphens and colons from every pipe field before testing it against `_GRADE_SEG` (AST-483). So `JOB:3` becomes `JOB3`, which matches `_GRADE_SEG` as vector `JO`, grade `B`, confidence `3`. It's recorded as a grade instead of link meta. There is no `JO` code in `vector_labels`, so the raw `JO` survives. Then `_hydrate_response_jobs_grade_reasons` → `_lookup_rubric_reason_for_grade` raises `ValueError` (unknown vector), which fails the whole batch. Each company here was already in `HOMEPAGE_READY_RETRY`, so per [AST-1828](https://linear.app/astralcareermatch/issue/AST-1828)'s routing it goes to `ERROR_PREFILTER_COMPANY`. This hits any single-digit job index `JOB:0`–`JOB:5` (multi-digit `JOB:17`, `JOB:106` and lists `JOB:2,13,…` don't match and decode correctly). Side effect: the real `possible_job_links` value is lost even when it doesn't crash. Retrying doesn't help reliably, because the model keeps emitting `JOB:n` for the same homepage.
2. `prefilter_company · IncompleteGradeSetError · missing vectors ['Staffing Agency or Outsourcing Shop']` **— 2 of 15** (logicplanet_com, cloudzenia_com). The model emitted a malformed 5-char segment `SOFA5` for the `SO` vector. That fails `_GRADE_SEG` and goes to meta, so the `SO` grade is missing. This is genuine model malformation, routed by the designed retry → error path (AST-1155 / AST-1828). **Not in scope for this fix** unless Susan says otherwise.

## To-be

A `JOB:<n>` or `CULT:<n>` pipe field is always treated as link meta, never as a grade segment, whatever the value of `n`. `JOB:3|CULT:7,27` decodes to `possible_job_links == [3]` and `culture_links_to_explore == [7, 27]`, with only the real rubric vectors as grades. No `JO` vector reaches hydrate, and those companies pass or fail prefilter on their actual grades.

## Proposed steps

1. In `_decode_payload`'s field-classification loop (`src/core/agent.py`, the `for f in fields[1:]` grade/meta split), send any raw field that starts with `JOB:` or `CULT:` (case-insensitive) straight to `meta` *before* the colon-stripping `_GRADE_SEG` test. The AST-483 normalization stays as it is for real grade tokens.
2. Keep `_should_decode_as_encoded_line` in `src/core/consult.py` consistent: skip `JOB:`/`CULT:` fields there too, so a link field alone can't make a line look encoded.
3. Regression coverage (Betty's call in the fix lane): `000|RCA5|HEA5|MLA3|PFA5|SOA5|JOB:3|CULT:7,27` decodes to five grades plus `possible_job_links [3]`. Repeat for each of `JOB:0`–`JOB:5`.

## Component scope

* `src/core/agent.py` — modified: `_decode_payload` classifies `JOB:`/`CULT:` link fields as grades because of the colon strip; this is where the misparse happens.
* `src/core/consult.py` — modified (small): `_should_decode_as_encoded_line` uses the same colon-strip + `_GRADE_SEG` test and should exclude link-prefixed fields the same way.

## Technical scope

* `src/core/agent.py` — modified function `_decode_payload`: add a link-prefix guard ahead of the grade-segment match, so a prefixed link field is never normalized into a grade token. A shared prefix pattern (the one `_LINK_PREFIX_RE` in `consult.py` already expresses) is plan-fix's call.
* `src/core/consult.py` — modified function `_should_decode_as_encoded_line`: the same guard, so routing detection and decoding agree on what counts as a grade segment.

## Ancestor candidates

- [ ] AST-1828: Somerset prefilter_company 100 errors (`docs/features/dispatcher/ast-1828-somerset-prefilter-company-completed-100-errors-500-processed-prefilter-company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf.md`). Diagnosed this exact `JOB:n` → `JO` misparse and explicitly deferred it (Proposed steps item 5, "Dropped (Susan, question 3)"). It also owns the `HOMEPAGE_READY_RETRY` → `ERROR_PREFILTER_COMPANY` routing that now makes this an error.
- [ ] AST-483: normalize grades segment whitespace in agent decode (`docs/features/boards/ast-483-normalize-grades-segment-whitespace-in-agent-decode.md`). Added the colon strip in `_decode_payload` that turns `JOB:3` into a valid-looking grade token.
- [ ] AST-697: prefilter link-set schema and bracket decode (`docs/features/consult/ast-697-prefilter-link-set-schema-and-bracket-decode.md`). Owns the `JOB:`/`CULT:` link-tail contract (`_LINK_PREFIX_RE`, `_apply_prefilter_encoded_link_meta`) that the model is following here.

## Original report (excerpts — full log trimmed per Susan, option 2)

Batch `prefilter_company-1cdeac6e-daa3-48f9-b230-4b59720a4182` (Somerset, 2026-10-12 14:09:42–14:11:12).

### ERROR lines (15)

```
[2026-10-12 14:10:36] ERROR src.core.roster: jobs_thecignagroup_com -> ERROR_PREFILTER_COMPANY [hydrate: No rubric criterion matching vector 'JO']
[2026-10-12 14:10:37] ERROR src.core.roster: logicplanet_com -> ERROR_PREFILTER_COMPANY [decode: IncompleteGradeSetError: _render_score: missing vectors ['Staffing Agency or Outsourcing Shop']]
[2026-10-12 14:10:37] ERROR src.core.roster: koerber_com -> ERROR_PREFILTER_COMPANY [hydrate: No rubric criterion matching vector 'JO']
[2026-10-12 14:10:37] ERROR src.core.roster: wellspan_org -> ERROR_PREFILTER_COMPANY [hydrate: No rubric criterion matching vector 'JO']
[2026-10-12 14:10:42] ERROR src.core.roster: cloudzenia_com -> ERROR_PREFILTER_COMPANY [decode: IncompleteGradeSetError: _render_score: missing vectors ['Staffing Agency or Outsourcing Shop']]
[2026-10-12 14:10:42] ERROR src.core.roster: uchealth_org -> ERROR_PREFILTER_COMPANY [hydrate: No rubric criterion matching vector 'JO']
[2026-10-12 14:10:42] ERROR src.core.roster: withvector_io -> ERROR_PREFILTER_COMPANY [hydrate: No rubric criterion matching vector 'JO']
[2026-10-12 14:10:44] ERROR src.core.roster: publichealthjobs_aspph_org -> ERROR_PREFILTER_COMPANY [hydrate: No rubric criterion matching vector 'JO']
[2026-10-12 14:10:44] ERROR src.core.roster: jobs_lever_co_3 -> ERROR_PREFILTER_COMPANY [hydrate: No rubric criterion matching vector 'JO']
[2026-10-12 14:10:47] ERROR src.core.roster: recruiting_paylocity_com_3 -> ERROR_PREFILTER_COMPANY [hydrate: No rubric criterion matching vector 'JO']
[2026-10-12 14:10:51] ERROR src.core.roster: precisionformedicine_com -> ERROR_PREFILTER_COMPANY [hydrate: No rubric criterion matching vector 'JO']
[2026-10-12 14:10:51] ERROR src.core.roster: legendbiotech_com_2 -> ERROR_PREFILTER_COMPANY [hydrate: No rubric criterion matching vector 'JO']
[2026-10-12 14:10:51] ERROR src.core.roster: pronixhealth_com -> ERROR_PREFILTER_COMPANY [hydrate: No rubric criterion matching vector 'JO']
[2026-10-12 14:10:54] ERROR src.core.roster: jobs_massdigitalhealth_org -> ERROR_PREFILTER_COMPANY [hydrate: No rubric criterion matching vector 'JO']
[2026-10-12 14:11:12] ERROR src.core.roster: adventisthealthcare_com -> ERROR_PREFILTER_COMPANY [hydrate: No rubric criterion matching vector 'JO']
```

### Traceback — hydrate `JO` (first of 13)

```
Traceback (most recent call last):
  File "/app/src/core/roster.py", line 2179, in _run_batch_company_prefilter
    _hydrate_response_jobs_grade_reasons(response_companies, rubric_list)
  File "/app/src/core/consult.py", line 380, in _hydrate_response_jobs_grade_reasons
    _hydrate_grade_reasons_from_rubric(glist, rubric_criteria)
  File "/app/src/core/consult.py", line 340, in _hydrate_grade_reasons_from_rubric
    g["reason"] = _lookup_rubric_reason_for_grade(
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/consult.py", line 331, in _lookup_rubric_reason_for_grade
    raise ValueError(f"No rubric criterion matching vector {vector_label!r}")
ValueError: No rubric criterion matching vector 'JO'
```

### Traceback — decode `SOFA5` (first of 2)

```
Traceback (most recent call last):
  File "/app/src/core/roster.py", line 2217, in _run_batch_company_prefilter
    new_state = _apply_prefilter_decoded_company_outcome(
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/roster.py", line 1744, in _apply_prefilter_decoded_company_outcome
    _require_complete_grade_set(rubric_list, grades)
  File "/app/src/core/consult.py", line 877, in _require_complete_grade_set
    raise IncompleteGradeSetError("_render_score: " + "; ".join(parts))
src.core.consult.IncompleteGradeSetError: _render_score: missing vectors ['Staffing Agency or Outsourcing Shop']
```

### Distinct agent_payload shapes

```
000|RCA3|HEX0|MLX0|PFX0|SOA3|[6]|[60]
000|RCA5|HEA5|MLA3|PFA5|SOA5|JOB:3|CULT:7,27
000|RCA5|HEA5|MLA4|PFA4|SOA5|JOB:2|CULT:1,3,4
000|RCA5|HEA5|MLA5|PFA3|SOA4|JOB:27|CULT:24,29,54
000|RCA5|HEA5|MLA5|PFA3|SOB4|JOB:2|CULT:13,26,27
000|RCA5|HEA5|MLA5|PFA5|SOA5|JOB:106|CULT:101,46,48,110,140
000|RCA5|HEA5|MLA5|PFA5|SOFA5|[3]|[25,9,26]
000|RCA5|HEA5|MLA5|PFC3|SOFA5|JOB:17|CULT:20,19,21
000|RCA5|HEB4|MLA5|PFA4|SOA4|JOB:3|CULT:41,45,46
000|RCA5|HEX0|MLA5|PFD4|SOA5|JOB:4|CULT:5,7
000|RCA5|HEX0|MLX0|PFA4|SOA4|JOB:2|CULT:8,9,10,11,14
000|RCA5|HEX0|MLX0|PFA4|SOB4|JOB:5|CULT:133,131,134
000|RCA5|HEX0|MLX0|PFX0|SOA5|[78,80]|[79,51,27,32,50]
000|RCA5|HEX0|MLX0|PFX0|SOA5|JOB:3|CULT:51,52,53
000|RCA5|HEX0|MLX0|PFX0|SOA5|JOB:4|CULT:7,15,16
000|RCB4|HEX0|MLX0|PFX0|SOA4|JOB:3|CULT:23,51,15
000|RCB5|HEC5|MLX0|PFX0|SOA5|JOB:5|CULT:4,51,56
000|RCF5|HEX0|MLX0|PFX0|SOA5|JOB:2,13,17,21,28|CULT:5,4,54,55,58
000|RCF5|HEX0|MLX0|PFX0|SOA5|JOB:5|CULT:20,25,26,27
000|RCF5|HEX0|MLX0|PFX0|SOX0|[1]|[1]
000|RCF5|HEX0|MLX0|PFX0|SOX0|JOB:1|CULT:[]
000|RCX0|HEX0|MLX0|PFX0|SOX0|[1]|[1]
```

### Summary line

```
[2026-10-12 14:11:12] INFO src.core.dispatcher: somerset | dispatch company task completed: prefilter_company pass:4 fail:3 error:15 (batch: prefilter_company-1cdeac6e-daa3-48f9-b230-4b59720a4182)
```

### Comments

#### chuckles — 2026-10-12T14:37:42.786Z
Project was unset; assigned **Astral Dispatcher** (encoded-decode fixes AST-2126/2124/2093 live there).

#### chuckles — 2026-10-12T14:35:41.583Z
[check-linear] Todo — definition saved with log excerpts; to approve, assign to Chuckles (@susan)

#### susan — 2026-10-12T14:34:56.906Z
@chuckles option 2

#### chuckles — 2026-10-12T14:33:08.562Z
@susan Diagnosis is ready, but I can't save it. Linear caps an issue Description at 250,000 characters, and the pasted log on its own is about 655K. A full-body rewrite that keeps the log verbatim gets rejected, so I haven't changed anything.

**Read:** 13 of the 15 errors come from a decoder bug that [AST-1828](https://linear.app/astralcareermatch/issue/AST-1828) already found and deferred ("question 3"). `_decode_payload` strips colons before running the grade-segment match, so a link field `JOB:3` becomes `JOB3` and is read as vector `JO`, grade B, confidence 3. Hydrate then raises `No rubric criterion matching vector 'JO'`. The other 2 errors are the model emitting `SOFA5`, which goes through the designed retry-then-error path. The fix is a link-prefix guard ahead of the grade match in `src/core/agent.py`; I'm confident in it.

How should I handle the raw log? Reply and reassign to me:
1. Move the full log into 3 comments on this ticket, verbatim, and the Description becomes the definition plus a pointer to them.
2. Keep only the error excerpts in the Description (the 15 ERROR lines, 2 tracebacks and the payload shapes) and drop the rest of the log.
3. Something else.

---

_Implementation detail may live in git history on `origin/dev`._
