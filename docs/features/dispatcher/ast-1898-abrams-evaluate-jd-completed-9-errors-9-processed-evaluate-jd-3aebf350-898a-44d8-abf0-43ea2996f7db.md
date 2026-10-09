# AST-1898 — [✅/Abrams] evaluate_jd COMPLETED: 9 error(s) / 9 processed | evaluate_jd-3aebf350-898a-44d8-abf0-43ea2996f7db

<!-- linear-archive: AST-1898 archived 2026-10-08 -->

## Linear archive (AST-1898)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1898/abrams-evaluate-jd-completed-9-errors-9-processed-evaluate-jd-3aebf350  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## As-is

The Abrams `evaluate_jd` batch `evaluate_jd-3aebf350-…` finished 9/9 as `ERROR_EVALUATE_JD`, each with `hydrate: No rubric description for vector 'Quality Check' grade X`. The model returned grade `X` for the embedded **QC / Quality Check** vector. `_lookup_rubric_reason_for_grade` in `src/core/consult.py` raises because QC's `grade_descriptions` in `EMBEDDED_EVALUATE_JD_CRITERIA` (`src/utils/config.py`) deliberately has rows for **A/B/C/F only**. But every instruction the model sees says `X` is always valid: the evaluate_jd task prompt (`data/admin/agent_task.json`, `task_key: evaluate_jd`) says "use X0 when silent", and the shared `_ENCODED_GRADE_SET_COMPLETENESS` block in `config.py` says the same. Nothing tells it QC is an exception. One missing grade row fails every job in the batch.

## To-be

**Decision (Susan, 2026-09-30): option (b), forbid** `X` **for Quality Check.** The model never emits `X` for QC. When a JD is too thin to analyze, it grades QC **F**, which already means "not enough information to perform job fit analysis". QC keeps its A/B/C/F-only table, and hydrate stays strict: no silent X→F mapping in code.

## Proposed steps

1. Add an explicit rule line to QC's `content` in `EMBEDDED_EVALUATE_JD_CRITERIA`: `X` is not a valid grade for Quality Check, and if there isn't enough to analyze, the grade is F. The model sees rubric content, so this puts the exception right next to the vector.
2. Change the evaluate_jd task prompt row in `data/admin/agent_task.json`, where it says "use X0 when silent", so it adds that **QC must never be X** (use F). Leave every other vector's X0 rule unchanged.
3. Leave the shared `_ENCODED_GRADE_SET_COMPLETENESS` text alone unless plan-fix finds that the per-vector rule loses to it in practice. It's shared by every encoded task, so changing it has a wide blast radius.
4. Tests: extend the QC config assertions for the new content line. Keep A/B/C/F as the pinned grade set.
5. Re-run an evaluate_jd batch and confirm 0 hydrate errors. If QC now comes back **F on all jobs**, JD content is probably arriving empty upstream. That would be a separate bug, not part of this fix.

## Component scope

* `src/utils/config.py`: modified. QC's `content` in `EMBEDDED_EVALUATE_JD_CRITERIA` gains a "no X, use F" rule line.
* `data/admin/agent_task.json`: modified. The `evaluate_jd` row's prompt text gets a QC exception to the "use X0 when silent" rule.
* `docs/uat-fixtures/AST-756/expected-agent_task.json`: modified. Byte-twin of `data/admin/agent_task.json` (AST-756/AST-1773 lockstep); the `evaluate_jd` row's prompt edit is mirrored here so the twin does not drift further. Added at fix-board (Betty note on AST-1910).
* `tests/component/utils/test_config.py`: modified (Betty's tree). `TestAst1084EvaluateJdCriteria` QC assertions should cover the new rule line while still pinning grades to A/B/C/F.

## Technical scope

* `src/utils/config.py`: data change to a module-level constant. One added line in QC's `content` string; `grade_descriptions` unchanged. No function changes, and hydrate in `consult.py` stays strict by design.
* `data/admin/agent_task.json`: modified prompt string on one existing row (`task_key: evaluate_jd`). No schema change. plan-fix confirms how repo admin JSON is applied to the live `agent_task` table (`REPO_ADMIN_JSON_CONFIG`) so the prompt change actually reaches runtime.
* `docs/uat-fixtures/AST-756/expected-agent_task.json`: same one-row prompt-string edit as `data/admin/agent_task.json`, mirrored byte-for-byte. No other rows touched (four rows already drifted on dev; not this fix).
* `tests/component/utils/test_config.py`: modified test, adding one assertion that QC content forbids X.

## Ancestor candidates

- [X] AST-1084 — config constant JD vectors (`docs/features/interface/ast-1084-config-constant-jd-vectors.md`): defined QC with A/B/C/F only (best fit)
- [ ] AST-1085 — wire constants into evaluate_jd (`docs/features/interface/ast-1085-wire-constants-evaluate-jd.md`): merged QC into evaluate_jd, but not the prompt's X rule
- [ ] AST-1077 — add a constant set of rubric vectors to generated JD evaluate vectors (`docs/features/interface/ast-1077-add-a-constant-set-of-rubric-vectors-to-generated-jd-evaluate-vectors.md`): parent feature for QC/GC
- [ ] AST-1063 — job-carried rubric hydration for list columns (`docs/features/interface/ast-1063-job-carried-rubric-hydration-for-list-columns.md`): the hydrate path that raises (behaving correctly)

---

## Original report

```
2026-09-30 20:11:12  [INFO]  abrams | dispatch job task completed:
evaluate_jd pass:0 fail:0 error:9 (batch:
evaluate_jd-3aebf350-898a-44d8-abf0-43ea2996f7db)
2026-09-30 20:11:12  [ERROR]  a08e3fe1-ed9c-4e2c-9f1b-23dbb3edcf03 ->
ERROR_EVALUATE_JD [hydrate: No rubric description for vector 'Quality
Check' grade X]
2026-09-30 20:11:12  [ERROR]  6a9e53b1-9ecd-45fb-bad9-eb8814b0fa65 ->
ERROR_EVALUATE_JD [hydrate: No rubric description for vector 'Quality
Check' grade X]
2026-09-30 20:11:12  [ERROR]  8b089c46-d1ab-4ff2-9f24-7fe025b63488 ->
ERROR_EVALUATE_JD [hydrate: No rubric description for vector 'Quality
Check' grade X]
2026-09-30 20:11:12  [ERROR]  6a05c43c-aed8-42e5-90eb-9a0715100333 ->
ERROR_EVALUATE_JD [hydrate: No rubric description for vector 'Quality
Check' grade X]
2026-09-30 20:11:12  [ERROR]  1448101c-0fb1-4342-8384-a7838ae2c519 ->
ERROR_EVALUATE_JD [hydrate: No rubric description for vector 'Quality
Check' grade X]
2026-09-30 20:11:12  [ERROR]  5713f821-0056-4f51-97ed-9e7d2f53c5f6 ->
ERROR_EVALUATE_JD [hydrate: No rubric description for vector 'Quality
Check' grade X]
2026-09-30 20:11:12  [ERROR]  3a6a201a-5b1d-41c1-88cf-a06cc91ace78 ->
ERROR_EVALUATE_JD [hydrate: No rubric description for vector 'Quality
Check' grade X]
2026-09-30 20:11:12  [ERROR]  7cb19af4-bebe-4fbf-bb15-0bf81254425b ->
ERROR_EVALUATE_JD [hydrate: No rubric description for vector 'Quality
Check' grade X]
2026-09-30 20:11:12  [ERROR]  14a9daa1-fa97-426f-83cd-f5b44fcc01d0 ->
ERROR_EVALUATE_JD [hydrate: No rubric description for vector 'Quality
Check' grade X]
2026-09-30 20:11:12  [INFO]  LLM deepseek task=evaluate_jd 4.0s
stop=end_turn tokens in=666 out=746
2026-09-30 20:11:12  [INFO]  abrams | dispatch job starting
evaluate_jd — 9 available (batch:
evaluate_jd-3aebf350-898a-44d8-abf0-43ea2996f7db)
```

### Comments

#### chuckles — 2026-10-02T04:29:59.597Z
PR #203 (ftr → dev) is open. The product change is two files: the QC "never X, grade F" line in `src/utils/config.py`, and the evaluate_jd prompt exception in `data/admin/agent_task.json` (mirrored into the AST-756 fixture). AST-1911 adds the tests pinning both.

Before you merge:
- **Test carry:** through `origin/tests`, #203 also brings AST-1895's tests (`test_consult.py`; product AST-1893 is on `ftr/AST-1888`) and AST-1920's tests (`test_AdminManageCandidates`; product on `ftr/AST-1851`). If #203 lands first, those tests fail on dev until AST-1888 and AST-1851 land. Either land those first and have me refresh this ftr, or merge knowing they'll be red for a while.
- **Deploy step:** the prompt change only reaches runtime after an admin runs **Revert to file** for `agent_task`, which rewrites every row from the file, so check the compare view first. The QC rubric line needs no extra step.

finish-up runs once you move this to PR Ready.

#### chuckles — 2026-10-01T01:15:26.646Z
Recreated origin/tests-clean-base at 82423d73b (AST-1912). The gate still fails on three AST-1902 sync merges above it, so AST-1911 is gated on AST-1919 (grandfather, scrub, or waive).

#### chuckles — 2026-10-01T00:29:49.021Z
AST-1911 gated on AST-1912: Betty's tests are proven locally (`f0000cf10`), but origin/tests can't pass the tests gate (missing tests-clean-base plus three sync merges from the AST-1902 run). AST-1910 is fixed and merged on ftr/AST-1898-evaluate-jd-qc-forbid-x.

#### susan — 2026-09-30T23:19:49.952Z
I answer "b", forbid X for Quality Check

---

_Implementation detail may live in git history on `origin/dev`._
