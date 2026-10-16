# AST-2126 — fix: Do rubric codes always decodable; name the empty-grade case (AST-2112)

<!-- linear-archive: AST-2126 archived 2026-10-16 -->

## Linear archive (AST-2126)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2126/fix-do-rubric-codes-always-decodable-name-the-empty-grade-case-ast  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / 3  
**Parent:** AST-2112 — [✅/Somerset] meteorite_grade_do COMPLETED: 1 error(s) / 1 processed | meteorite_grade_do-3f837cd7-89e5-47f6-9ae1-e8aae7ee4284  
**Blocked by / blocks / related:** parent: AST-2112

### Description

## What this implements

Fix for [AST-2112](https://linear.app/astralcareermatch/issue/AST-2112): Somerset's Do grading (`grade_do` and its alias `meteorite_grade_do`) fails every run with `_render_score: missing vectors [...]` listing **all 11** Do vectors, sending each job to `METEORITE_FAILED_TECHNICAL_DO` / `FAILED_TECHNICAL_DO`. It recurred as [AST-2113](https://linear.app/astralcareermatch/issue/AST-2113), [AST-2118](https://linear.app/astralcareermatch/issue/AST-2118), and [AST-2119](https://linear.app/astralcareermatch/issue/AST-2119), all now duplicates of AST-2112.

## Ancestor (Susan-approved)

AST-1155 / AST-1150 — incomplete grades → retry holding, never technical fail (`docs/features/consult/ast-1155-incomplete-grades-retry-holding-never-technical-fail.md`). That doc owns `_require_complete_grade_set`, the `missing` / `unknown vectors` messages, the retry → error route, and the AST-1996 per-line decode-failure block this fix extends. Both Linear tickets are archived, so there is no live ticket to link. Patch that doc.

## As-is

Every Somerset Do grading run since 2026-10-09 15:12 fails the same way. Four batches so far (`3f837cd7`, `02b93b95`, `5ade3129`, and `grade_do` `fae00574`) each sent **one** job to the grader. Each reply came back in 3–7s with **73–83 output tokens**, on two different hosts (Parasail and Nebius). Scoring then raised `IncompleteGradeSetError: _render_score: missing vectors [...]` listing **all 11** current Do vectors, and the job went to `METEORITE_FAILED_TECHNICAL_DO` / `FAILED_TECHNICAL_DO`. Because it is deterministic across hosts, the host is ruled out (round 1's Parasail theory is dropped). The common factor is Somerset's Do rubric, which was re-saved after [AST-2008](https://linear.app/astralcareermatch/issue/AST-2008): the `duplicate rubric codes: TP` warning is gone, there are 11 vectors, and labels are reworded (e.g. "Hands-On Technical Partnership").

**Code paths on** `origin/dev` **are consistent.** The prompt's `{$RUBRIC_VECTORS}` (`src/utils/config.py` token resolver → `rubric_criteria_for_token`), the decode map (`_vector_labels_map`), and the scorer's rubric (`_render_score`) all come from `rubric_criteria_for_task` (`src/core/candidate.py`) over the current `rubric_vector` rows. So AST-2119's "prompt and decoder read different sources" theory does not hold in code.

**Most likely mechanism (unverified against data):** `sync_rubric_vectors_from_criteria` (`src/data/database.py`) gives any criterion saved with a blank `code` the fallback code `V{idx:02d}`, i.e. `V01`…`V11`. The prompt shows the model those codes. `_GRADE_SEG` in `_decode_payload` (`src/core/agent.py`) only accepts `[A-Z]{2}` + grade letter + digit, so a correct reply like `000|V01A3|V02B4|…` matches **no** segment. Under `output_type: grades_encoded_notes`, the unmatched fields are folded into `notes` and the row decodes to `grades: []`. Nothing records a `decode_failure`, and scoring reports every label as missing. Eleven `V01A3`-style segments are about the 73–83 tokens observed. `rubric_dispatch_error` (AST-2091's Scheduled Actions gate) checks only duplicate and empty rubrics, so it can't catch a code the decoder can never match.

Fallback mechanism if the stored codes turn out to be proper 2-letter codes: the model is replying with something other than encoded segments (prose, labels), which reaches the same `grades: []` through the same notes fold.

Either way, two diagnostic gaps hide the cause. `_require_complete_grade_set` (`src/core/consult.py`) raises on `missing` before it reports `unknown vectors`, and the raw reply / zero-segment condition is never logged.

Routing ([AST-1155](<https://linear.app/astralcareermatch/issue/AST-1155>), checked): an incomplete set's first strike should go to retry holding (`METEORITE_PASSED_JD_RETRY`) and only the second to `error_state`. Each run here was a 1-job batch landing straight in technical fail. That fits a second strike on a job already in `_RETRY`, but it hasn't been confirmed against state history.

## To-be

Somerset's Do rubric grades normally: every criterion carries a code the encoded-grade decoder can match, so a well-formed reply scores. A rubric whose codes can't be decoded is caught at save time (repaired or rejected) and shown as Invalid on Scheduled Actions, so a broken rubric doesn't burn grading calls. When a reply still yields no usable grade, the failure text names the case (no grade segments vs. unknown codes, with the decoded codes listed), and a zero-segment line is a per-entity decode failure (AST-1996 route), not a silently empty grade row. The AST-1155 retry-then-error contract is unchanged.

## Proposed steps

1. **Data first (staging, no code):** read Somerset's current `rubric_vector` rows for owner `grade_do` (codes and labels), the stored raw reply for job `cfcccdcb-1c07-4b23-9a46-834382f2ef42` (batch `3f837cd7`), and that job's state history. This confirms or kills the `V01` theory and the second-strike reading.
2. **If codes are** `V01`**-style (or otherwise not 2 letters):** make the rubric save path guarantee a 2-letter `[A-Z]{2}` code for every criterion. Derive it from the label, with AST-2008's last-letter uptick on collision, instead of the `V{idx}` fallback. Then re-save Somerset's Do rubric once so the stored rows get real codes.
3. Extend `rubric_dispatch_error` so a rubric with any code that isn't `[A-Z]{2}` is Invalid, using the same message plumbing as duplicate and empty codes.
4. `_require_complete_grade_set` reports `missing` **and** `unknown` together, and `_decode_payload` records a `grades_encoded_notes` line with zero grade segments as a `decode_failure` (AST-1996 route). This holds whichever mechanism step 1 confirms.
5. Fix both task keys in one pass: `grade_do` (folded in from [AST-2119](https://linear.app/astralcareermatch/issue/AST-2119)) and its alias `meteorite_grade_do` share the `do_rubric`, the decode, and the scoring path, so nothing here is alias-specific.

## Citations

none. `plan-fix` resolves Canon Scope from the touched files.

## Scope

### Component scope

* `src/data/database.py` — modified — `sync_rubric_vectors_from_criteria` assigns the `V{idx:02d}` fallback code that `_GRADE_SEG` can never match.
* `src/core/candidate.py` — modified — the pre-save rubric code helper (AST-2008's uptick) is where a blank or invalid code should become a valid 2-letter code, and `rubric_dispatch_error` is where an undecodable code should make the task Invalid.
* `src/core/consult.py` — modified — `_require_complete_grade_set` hides the `unknown vectors` half whenever `missing` is non-empty, and `_normalize_rubric_task_response` turns a 1-job zero-segment reply into a silent `grades: []` row (scope amended per AST-2126 \[scope-gate\]).
* `src/core/agent.py` — modified — `_decode_payload`'s `grades_encoded_notes` branch folds a line with no grade segments into `notes` instead of recording a decode failure.
* Staging Somerset `rubric_vector` rows and job `cfcccdcb-…` — read, then one rubric re-save — evidence for step 1 and the data repair in step 2. No repo change.

### Technical scope

* `src/data/database.py`: **modified function** `sync_rubric_vectors_from_criteria`. It no longer invents a non-decodable code. It either receives a guaranteed 2-letter code from the save helper or rejects the criterion, so stored codes always fit the encoded-grade contract.
* `src/core/candidate.py`: **modified function** — the pre-save code dedupe helper also fills blank or invalid codes with a 2-letter code derived from the label (collision-safe via the existing uptick). **Modified function** `rubric_dispatch_error` adds an "invalid vector code" reason beside duplicate and empty.
* `src/core/consult.py`: **modified function** `_require_complete_grade_set` returns one reason carrying both the missing labels and the unexpected decoded vectors. It keeps the same exception class and routing. **Modified function** `_normalize_rubric_task_response`: for `grades_encoded_notes` jobs, a letter-pipe fallback row with zero grades becomes one `decode_failures` entry per batch entity (raw reply as reason) instead of a silent `grades: []` row.
* `src/core/agent.py`: **modified function** `_decode_payload`. In the notes-tolerant job path, a line with empty `grade_segs` appends a `decode_failures` entry (id, pos, reason) and skips the line, matching the existing [AST-1996](https://linear.app/astralcareermatch/issue/AST-1996/isolate-malformed-encoded-grade-lines-per-entity-retry-not-hop-error) handling. No new states or config keys.

## Git branch (authoritative)

Bug mini-parent `ftr/AST-2112-do-rubric-undecodable-codes`, child `sub/AST-2112/<this-ticket>-do-rubric-undecodable-codes`. Registry: `epic_registry.py show AST-2112`.

### Comments

#### radia — 2026-10-10T04:02:07.738Z
[code-rubric] PROCEED (Commit: 4e9731267) Rubric decode + diagnostics

Clean. `patt.task.dispatch-retry`, `patt.entity.batch-processing`, and `stat.logging.warning` got an A. `stat.logging.debug` is not applicable. `## What must still hold` is OK: AST-1155, AST-1996, AST-2008, and AST-2091 behaviour is preserved and `_GRADE_SEG` is unchanged. `[bug-repro]` is not applicable because that coverage is on [AST-2127](https://linear.app/astralcareermatch/issue/AST-2127). Full artifact: AST-1155 doc § Radia review — AST-2126 (F7).

#### hedy — 2026-10-10T03:59:52.093Z
`origin/sub/AST-2112/AST-2126-do-rubric-undecodable-codes` @ `4e9731267` · steps 1–5 per plan; step 6 is the operator staging step.

**Test note for AST-2127 (Betty):** sanity run of `test_agent`, `test_candidate`, `test_consult`, `test_rubric_vectors`, and `test_backfill_rubric_vectors` in `~/astral/.venv` showed 29 new failures compared with the pre-change tree. The 93 baseline failures are environment-only, e.g. `no such table: job`.
- 2 are the expected candidate tests: `TestAst2008RubricCodeUptick::test_uptick_is_pure_and_passes_non_dict_and_blank_codes` and `TestAst2091RubricDispatchError::test_duplicates_case_insensitive_sorted_and_blank_codes_ignored`.
- **27 more** come from fixtures that call `sync_rubric_vectors_from_criteria` directly with codes plan step 2 now rejects (`G1` ×20, `V01` ×4, `CLR` ×2, `A` ×1). They are in `test_rubric_vectors.py` (`TestAst723SyncRubricVectors`, `TestAst724/725/808/809`, `TestAst2066RubricCriterionVersions`) and `test_agent.py` (`TestAst724/809/816/820/862` vector-feedback, `TestAst1486FeedbackEntityIdStamp`). These fixtures need two-letter codes. This is wider than the plan's Blast radius predicted. No tests were edited.

#### joan — 2026-10-10T03:56:23.289Z
[board-joan] CANON: OK

No statute or pattern needs to change. Routing zero-segment and empty letter-pipe replies through the existing `decode_failures` per-entity path follows `patt.task.dispatch-retry`. No claim or batch-size changes, so `patt.entity.batch-processing` holds. The new code-repair warning is a use of `stat.logging.warning`, not an amendment. `_GRADE_SEG` stays as it is, so no wire-contract canon is touched. Full findings: AST-1155 doc § Fix board — Joan (F2), commit `a5f16db39`.

#### betty — 2026-10-10T03:55:45.014Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/candidate.md + core/consult.md + core/agent.md — 2 broken tests + no repro coverage — `test_candidate.py::…::test_uptick_is_pure_and_passes_non_dict_and_blank_codes` (blank now filled) and `…::test_duplicates_case_insensitive_sorted_and_blank_codes_ignored` (invalid-code check now fires before duplicates on ` tp`/`sa`/blank rows) break; no existing node covers the zero-grade letter-pipe → `decode_failures` path (§5, the production repro), the zero-segment `_decode_payload` notes line (§4), sync rejecting non-`[A-Z]{2}` codes (§2), `rubric_dispatch_error` invalid-code message (§1), or the combined missing+unknown reason (§3).

Notes for qa-fix (not part of the verdict):
- Guard tests that stay green, by plan: `test_agent.py::…::test_ast1996_notes_type_tail_is_not_a_decode_failure` (line has a segment), `test_consult.py` `missing vectors` / `unknown vectors` single-side matches (byte-identical), `test_api_candidate.py` V01 rubric-route tests (explicit stored codes, never via a blank-code fallback through sync — keep an eye on these if sync's raise is reached in any fixture path).
- [bug-repro] candidate: the plan's Repro (`_normalize_rubric_task_response("grade_do", …)` with `V01A3` segments and with prose) → today returns `grades: []`; to-be returns `jobs: []` plus one `decode_failures` entry per entity carrying the raw reply.
- Bible: `scripts/ci/ftr-merge-ready.sh` in the diff is outside the fix scope; no test impact.

#### hedy — 2026-10-10T03:54:45.261Z
`origin/sub/AST-2112/AST-2126-do-rubric-undecodable-codes` @ `cfd59ab62` · step 5 now in scope

#### chuckles — 2026-10-10T03:51:23.728Z
[scope-gate] answered — `src/core/consult.py` `_normalize_rubric_task_response` (a `grades_encoded_notes` letter-pipe fallback row with zero grades becomes one `decode_failures` entry per batch entity, carrying the raw reply) is now in Component/Technical scope on AST-2126 and AST-2112. Step 5 is in scope.

#### hedy — 2026-10-10T03:50:41.198Z
[scope-gate] `origin/sub/AST-2112/AST-2126-do-rubric-undecodable-codes` @ `7027c28cb` · plan written, step 5 out of scope

**File / change kind needed:** `src/core/consult.py` — **modified function** `_normalize_rubric_task_response`: for `grades_encoded_notes` jobs, a letter-pipe fallback row with zero grades becomes one `decode_failures` entry per batch entity (raw reply as reason) instead of a silent `grades: []` row.

**Scope lines that don't cover it:**
> `src/core/consult.py` — modified — `_require_complete_grade_set` hides the `unknown vectors` half whenever `missing` is non-empty.
> `src/core/agent.py`: **modified function** `_decode_payload`. In the notes-tolerant job path, a line with empty `grade_segs` appends a `decode_failures` entry …

**Why the in-scope change can't do it alone:** on a 1-job batch (every Somerset run), neither a `V01A3`-style reply nor prose ever reaches `_decode_payload`. `_should_decode_as_encoded_line` finds no `_GRADE_SEG` match, so `_normalize_rubric_task_response` falls to `_job_from_letter_pipe`, which returns `grades: []`. Verified by the no-DB repro in the doc (`## Bug: AST-2126` → Repro). The ticket's "notes fold" wording only applies when some line has a valid segment. Without step 5, To-be's "zero-segment line is a per-entity decode failure" does not hold for the production case. Steps 1–4 (the 2-letter code guarantee, dispatch Invalid gate, and combined missing/unknown message) are all in scope and still close the `V01` hypothesis.

Same approach, one more function in an already-scoped file, so no Archie widening is needed. If declined, make-fix drops step 5 and nothing else changes.

Staging evidence (Somerset `rubric_vector` codes, the raw reply for `cfcccdcb-…`) was unreachable from this environment because the local DB is empty. It's listed as operator step 6.

After amending, assign this bug to Chuckles.

---

_Implementation detail may live in git history on `origin/dev`._
