# AST-1876 — [✅/Johnson] prefilter_company COMPLETED: 50 error(s) / 50 processed | prefilter_company-6e5f321d-aa8d-4a68-94eb-3efa041a59bd

<!-- linear-archive: AST-1876 archived 2026-10-07 -->

## Linear archive (AST-1876)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1876/johnson-prefilter-company-completed-50-errors-50-processed-prefilter  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## As-is

`prefilter_company` batch `prefilter_company-6e5f321d-…` returned 50 errors out of 50 processed. The model graded Reality Check twice on line `000` (`000|RCA5|RCA5|…`), and the duplicate-code guard in `_decode_payload` rejected the batch.

The model saw Reality Check twice because it's defined in two places:

* The `prefilter_company` `cache_prompt` in `data/admin/agent_task.json` has a hand-written `### Reality Check - Is this the website for a company…` section, with an A/B/C/D/F scale about company sites.
* `{$RUBRIC_VECTORS}` also brings in the embedded `RC` vector from `EMBEDDED_COMPANY_PREFILTER_CRITERIA` in `src/utils/config.py`. Its content is a generic "real vs fraudulent" scale.

RC is also handled differently from the two default job-description vectors (`QC` / `GC`, `EMBEDDED_EVALUATE_JD_CRITERIA`). QC/GC get merged in on every rubric save, craft persist, and craft generate, so they're saved as real `rubric_vector` rows. RC is only added in memory by `rubric_criteria_for_task` in `src/core/candidate.py`, so it never has a `rubric_vector` row.

## To-be

Reality Check is defined in one place: a default rubric vector, maintained the same way as the job-description QC/GC vectors. It's a constant in `config.py`, merged into the candidate's `prefilter_company` rubric on save, craft persist, and craft generate, and stored in `rubric_vector`. Its content is the company-site scale (typical company site, VC or portfolio page, social media page, unexpected site, not a company site, X for couldn't read). The `prefilter_company` prompt has no hand-written Reality Check section and gets RC only through `{$RUBRIC_VECTORS}`. Each line decodes with exactly one `RC` segment.

## Proposed steps

1. Delete the hand-written `### Reality Check …` block from the `prefilter_company` `cache_prompt` in `data/admin/agent_task.json`, and push it to the live `agent_task` row through the existing repo-JSON sync path.
2. Rewrite the `RC` entry in `EMBEDDED_COMPANY_PREFILTER_CRITERIA` (`content` and `grade_descriptions`) to the company-site scale from the deleted prompt block, adding the X "could not read the page" grade.
3. Make the prefilter merge match the job-description merge: pull the inline RC merge out of `rubric_criteria_for_task` into a merge helper shaped like `_merge_embedded_evaluate_jd_criteria` (RC stays in front; embedded wins on code). Call it wherever QC/GC are merged: in `normalize_rubric_artifacts_on_save` for owner `prefilter_company`, in the craft persist path for artifact `company_prefilter`, and in the craft generate response for `craft_prefilter_rubric`.
4. Give existing candidates an RC `rubric_vector` row, the same way QC/GC rows reached candidates who predate AST-1085. plan-fix decides whether that's the next save or an explicit backfill.
5. Re-run a `prefilter_company` batch on staging and confirm one `RC` segment per line and no decode errors.

## Component scope

* `data/admin/agent_task.json` — modified: remove the duplicate Reality Check section from the `prefilter_company` `cache_prompt`.
* `src/utils/config.py` — modified: the `RC` entry in `EMBEDDED_COMPANY_PREFILTER_CRITERIA` gets the company-site grade scale.
* `src/core/candidate.py` — modified: RC is merged and saved on the same code paths as the job-description QC/GC vectors, not just added at read time.

## Technical scope

* `data/admin/agent_task.json`: data-only edit to the `prefilter_company` row's `cache_prompt` field. No schema change.
* `src/utils/config.py`: edit the existing `EMBEDDED_COMPANY_PREFILTER_CRITERIA` constant (`content` and `grade_descriptions` of the `RC` dict). No new constant.
* `src/core/candidate.py`: a new merge helper for the embedded prefilter criteria, parallel to `_merge_embedded_evaluate_jd_criteria`. Modify `rubric_criteria_for_task` to use it, and modify `normalize_rubric_artifacts_on_save`, the craft persist path, and the craft generate response to call it for `prefilter_company` / `company_prefilter` / `craft_prefilter_rubric`, so RC is saved to `rubric_vector` like QC/GC. No new table or field.

## Ancestor candidates

- [X] AST-707 / AST-708 — UAT batch prefilter embedded RC vector hydration (`docs/features/consult/ast-707-uat-batch-prefilter-embedded-rc-vector-hydration.md`, `docs/features/consult/ast-708-uat-batch-prefilter-fails-rc-embedded-vector-hydration.md`). Introduced the embedded `RC` vector (read-time merge only) and left the prompt's hand-written section in place.
- [ ] AST-1085 / AST-1077 — Constant default vectors for the job-description rubric (`docs/features/interface/ast-1085-wire-constants-evaluate-jd.md`, `docs/features/interface/ast-1077-add-a-constant-set-of-rubric-vectors-to-generated-jd-evaluate-vectors.md`). The QC/GC pattern that RC should follow.
- [ ] AST-706 — Reality check should reference the letter code of RC for re-hydration (`docs/features/agent/ast-706-reality-check-should-reference-the-letter-code-of-rc-for-re-hydration.md`). The prompt-side Reality Check / RC wiring.

## Original report

```
2026-09-29 19:16:03  [ERROR]  oxand_com -> ERROR_PREFILTER [do_task:
[prefilter_company] duplicate vector code RC in encoded line:
'000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  lacera_gov -> ERROR_PREFILTER [do_task:
[prefilter_company] duplicate vector code RC in encoded line:
'000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  tiaa_org -> ERROR_PREFILTER [do_task:
[prefilter_company] duplicate vector code RC in encoded line:
'000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  augustdebouzy_com -> ERROR_PREFILTER
[do_task: [prefilter_company] duplicate vector code RC in encoded
line: '000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  edisongroup_com_2 -> ERROR_PREFILTER
[do_task: [prefilter_company] duplicate vector code RC in encoded
line: '000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  cbs_nl -> ERROR_PREFILTER [do_task:
[prefilter_company] duplicate vector code RC in encoded line:
'000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  worcesterma_gov -> ERROR_PREFILTER
[do_task: [prefilter_company] duplicate vector code RC in encoded
line: '000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  uvcpartners_com -> ERROR_PREFILTER
[do_task: [prefilter_company] duplicate vector code RC in encoded
line: '000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  welligence_com -> ERROR_PREFILTER
[do_task: [prefilter_company] duplicate vector code RC in encoded
line: '000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  dart_deloitte_com -> ERROR_PREFILTER
[do_task: [prefilter_company] duplicate vector code RC in encoded
line: '000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  kx_com -> ERROR_PREFILTER [do_task:
[prefilter_company] duplicate vector code RC in encoded line:
'000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  facilio_com_2 -> ERROR_PREFILTER
[do_task: [prefilter_company] duplicate vector code RC in encoded
line: '000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  cisa_gov -> ERROR_PREFILTER [do_task:
[prefilter_company] duplicate vector code RC in encoded line:
'000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  ubs_com -> ERROR_PREFILTER [do_task:
[prefilter_company] duplicate vector code RC in encoded line:
'000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  ieor_berkeley_edu -> ERROR_PREFILTER
[do_task: [prefilter_company] duplicate vector code RC in encoded
line: '000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  schoenherr_eu -> ERROR_PREFILTER
[do_task: [prefilter_company] duplicate vector code RC in encoded
line: '000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  wa_gov_au -> ERROR_PREFILTER [do_task:
[prefilter_company] duplicate vector code RC in encoded line:
'000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  realinvestmentadvice_com ->
ERROR_PREFILTER [do_task: [prefilter_company] duplicate vector code RC
in encoded line: '000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  yusmpgroup_com -> ERROR_PREFILTER
[do_task: [prefilter_company] duplicate vector code RC in encoded
line: '000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  ameapower_com -> ERROR_PREFILTER
[do_task: [prefilter_company] duplicate vector code RC in encoded
line: '000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  enkiai_com -> ERROR_PREFILTER [do_task:
[prefilter_company] duplicate vector code RC in encoded line:
'000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  main_nl -> ERROR_PREFILTER [do_task:
[prefilter_company] duplicate vector code RC in encoded line:
'000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  paretosec_com -> ERROR_PREFILTER
[do_task: [prefilter_company] duplicate vector code RC in encoded
line: '000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  futuristsspeakers_com_2 ->
ERROR_PREFILTER [do_task: [prefilter_company] duplicate vector code RC
in encoded line: '000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  onehub_energy -> ERROR_PREFILTER
[do_task: [prefilter_company] duplicate vector code RC in encoded
line: '000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  jobs_empower_com -> ERROR_PREFILTER
[do_task: [prefilter_company] duplicate vector code RC in encoded
line: '000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  wsp_com -> ERROR_PREFILTER [do_task:
[prefilter_company] duplicate vector code RC in encoded line:
'000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  cmegroup_com -> ERROR_PREFILTER
[do_task: [prefilter_company] duplicate vector code RC in encoded
line: '000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  ultimatebox_cn -> ERROR_PREFILTER
[do_task: [prefilter_company] duplicate vector code RC in encoded
line: '000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  saasberry_ai -> ERROR_PREFILTER
[do_task: [prefilter_company] duplicate vector code RC in encoded
line: '000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  ridop_ri_gov -> ERROR_PREFILTER
[do_task: [prefilter_company] duplicate vector code RC in encoded
line: '000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  yesenergy_com -> ERROR_PREFILTER
[do_task: [prefilter_company] duplicate vector code RC in encoded
line: '000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  docs_omnissa_com -> ERROR_PREFILTER
[do_task: [prefilter_company] duplicate vector code RC in encoded
line: '000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  support_atlassian_com -> ERROR_PREFILTER
[do_task: [prefilter_company] duplicate vector code RC in encoded
line: '000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  developers_hubspot_com ->
ERROR_PREFILTER [do_task: [prefilter_company] duplicate vector code RC
in encoded line: '000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  help_zscaler_com -> ERROR_PREFILTER
[do_task: [prefilter_company] duplicate vector code RC in encoded
line: '000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  colburn_se -> ERROR_PREFILTER [do_task:
[prefilter_company] duplicate vector code RC in encoded line:
'000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  kahua_com -> ERROR_PREFILTER [do_task:
[prefilter_company] duplicate vector code RC in encoded line:
'000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  darwinbox_com -> ERROR_PREFILTER
[do_task: [prefilter_company] duplicate vector code RC in encoded
line: '000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  v8coredocs_rconfig_com ->
ERROR_PREFILTER [do_task: [prefilter_company] duplicate vector code RC
in encoded line: '000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  juniper_net -> ERROR_PREFILTER [do_task:
[prefilter_company] duplicate vector code RC in encoded line:
'000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  tracecat_com -> ERROR_PREFILTER
[do_task: [prefilter_company] duplicate vector code RC in encoded
line: '000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  blogs_windows_com -> ERROR_PREFILTER
[do_task: [prefilter_company] duplicate vector code RC in encoded
line: '000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  developer_box_com -> ERROR_PREFILTER
[do_task: [prefilter_company] duplicate vector code RC in encoded
line: '000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  renderdraw_com -> ERROR_PREFILTER
[do_task: [prefilter_company] duplicate vector code RC in encoded
line: '000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  nivo1_com -> ERROR_PREFILTER [do_task:
[prefilter_company] duplicate vector code RC in encoded line:
'000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]  docs_keeper_io -> ERROR_PREFILTER
[do_task: [prefilter_company] duplicate vector code RC in encoded
line: '000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:03  [ERROR]
prefilter_company_batch_prefilter_company-6e5f321d-aa8d-4a68-94eb-3efa041a59bd
| prefilter_company
  ValueError: [prefilter_company] duplicate vector code RC in encoded
line: '000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]'
  Returning this hop as failed
Traceback (most recent call last):
  File "/app/src/core/agent.py", line 2463, in do_task
    parsed = _normalize_rubric_task_response(task_key, task_config,
parsed, ctx or {})
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/consult.py", line 761, in _normalize_rubric_task_response
    decoded = _decode_payload(task_key, output_type, text, ctx or {})
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/agent.py", line 344, in _decode_payload
    raise ValueError(
ValueError: [prefilter_company] duplicate vector code RC in encoded
line: '000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]'
2026-09-29 19:16:04  [ERROR]  alphasense_com -> ERROR_PREFILTER
[do_task: [prefilter_company] duplicate vector code RC in encoded
line: '000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:04  [ERROR]  scottishenterprise_com ->
ERROR_PREFILTER [do_task: [prefilter_company] duplicate vector code RC
in encoded line: '000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
2026-09-29 19:16:04  [ERROR]  valuationresearch_com -> ERROR_PREFILTER
[do_task: [prefilter_company] duplicate vector code RC in encoded
line: '000|RCA5|RCA5|DSB5|LUX0|PCB4|POB4|[2]|[2,4,5]']
```

### Comments

#### chuckles — 2026-09-29T20:12:14.754Z
[bug-fix] Done — landed on dev (PR #192). Operator step needed for this to take effect: Manage Tasks → Revert to file on `prefilter_company` (the live DB prompt still has the duplicate Reality Check block until then). (@susan)

#### chuckles — 2026-09-29T19:47:30.158Z
[check-linear] answered — Description revised: Reality Check now follows the same pattern as the job-description `QC` / `GC` defaults. It gets merged in on save, craft persist, and craft generate, so it's stored in `rubric_vector`. It reaches the model only through `{$RUBRIC_VECTORS}`, with content about company websites, and the prompt's own Reality Check section is removed. I also dropped the decode-guard and wording options. Still Discussion. To continue, check an ancestor box and assign to Chuckles. (@susan)

#### susan — 2026-09-29T19:45:31.945Z
@chuckles We have two default vectors for job descriptions.  I believe they are persisted in the database, and the reality check for the prefilter company should be maintained the same way, except about company sites, of course.  Please revise the plan to remove extraneous references and match with the job description elements.

#### chuckles — 2026-09-29T19:27:13.672Z
[check-linear] answered: yes, RC is also in `config.py`. It's the `RC` / "Reality Check" entry in `EMBEDDED_COMPANY_PREFILTER_CRITERIA` in `src/utils/config.py`, around line 2410. `rubric_criteria_for_task` in `src/core/candidate.py` adds that entry to the front of every candidate's `prefilter_company` vectors, so `{$RUBRIC_VECTORS}` already includes RC. The hand-written block in the prompt is the second copy.

"Only as a rubric vector" could mean either of these — which one do you want?
- **Keep the `config.py` constant and delete the prompt block.** RC stays a built-in vector that every candidate gets through `{$RUBRIC_VECTORS}`.
- **Retire the `config.py` constant too.** RC would become a normal `rubric_vector` row that each candidate stores. That needs a backfill for existing candidates and touches `rubric_criteria_for_task`.

To continue, check an ancestor box and assign to Chuckles. (@susan)

#### susan — 2026-09-29T19:25:54.329Z
@chuckles I found RC in the actual task prompt string.  Is it also in config.py?  It should only live as a rubric vector.

---

_Implementation detail may live in git history on `origin/dev`._
