# AST-2112 — [✅/Somerset] meteorite_grade_do COMPLETED: 1 error(s) / 1 processed | meteorite_grade_do-3f837cd7-89e5-47f6-9ae1-e8aae7ee4284

<!-- linear-archive: AST-2112 archived 2026-10-16 -->

## Linear archive (AST-2112)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2112/somerset-meteorite-grade-do-completed-1-errors-1-processed-meteorite  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Prior occurrences

* `meteorite_grade_do · IncompleteGradeSetError · _render_score: missing vectors [<every current Do vector>]` — **novel** — diagnosed below. Closest earlier `meteorite_grade_do` reports carry different evidence and are not this failure: [AST-2013](https://linear.app/astralcareermatch/issue/AST-2013) / [AST-2011](https://linear.app/astralcareermatch/issue/AST-2011) (all literal X, 12 vectors, duplicate `TP`), [AST-2007](https://linear.app/astralcareermatch/issue/AST-2007) (600s call timeout), [AST-1984](https://linear.app/astralcareermatch/issue/AST-1984) (max_tokens truncation). (3 searches)
* Recurrences since filing, duplicated into this ticket: [AST-2113](https://linear.app/astralcareermatch/issue/AST-2113) (Parasail, 4.7s, out=81) and [AST-2118](https://linear.app/astralcareermatch/issue/AST-2118) (**Nebius**, 3.2s, out=83). The same failure on the parent task `grade_do`, [AST-2119](https://linear.app/astralcareermatch/issue/AST-2119) (Nebius, out=74), was marked Duplicate of this ticket on 2026-10-10. This ticket now owns both task keys.
* Not covered by any unlanded fix (checked 2026-10-10): the related rubric/grade fixes (AST-2011, AST-2013/AST-2091, AST-2019, AST-2020, AST-2073) are already on `dev` and the failure recurs after them. The only in-flight grade fix, [AST-2108](https://linear.app/astralcareermatch/issue/AST-2108), is a `qualify_job_listings` prompt change for a different failure. No unmerged branch touches `_GRADE_SEG`, the `V{idx}` fallback, `_require_complete_grade_set`, or `_decode_payload`.

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

## Component scope

* `src/data/database.py` — modified — `sync_rubric_vectors_from_criteria` assigns the `V{idx:02d}` fallback code that `_GRADE_SEG` can never match.
* `src/core/candidate.py` — modified — the pre-save rubric code helper (AST-2008's uptick) is where a blank or invalid code should become a valid 2-letter code, and `rubric_dispatch_error` is where an undecodable code should make the task Invalid.
* `src/core/consult.py` — modified — `_require_complete_grade_set` hides the `unknown vectors` half whenever `missing` is non-empty, and `_normalize_rubric_task_response` turns a 1-job zero-segment reply into a silent `grades: []` row (scope amended per AST-2126 \[scope-gate\]).
* `src/core/agent.py` — modified — `_decode_payload`'s `grades_encoded_notes` branch folds a line with no grade segments into `notes` instead of recording a decode failure.
* Staging Somerset `rubric_vector` rows and job `cfcccdcb-…` — read, then one rubric re-save — evidence for step 1 and the data repair in step 2. No repo change.

## Technical scope

* `src/data/database.py`: **modified function** `sync_rubric_vectors_from_criteria`. It no longer invents a non-decodable code. It either receives a guaranteed 2-letter code from the save helper or rejects the criterion, so stored codes always fit the encoded-grade contract.
* `src/core/candidate.py`: **modified function** — the pre-save code dedupe helper also fills blank or invalid codes with a 2-letter code derived from the label (collision-safe via the existing uptick). **Modified function** `rubric_dispatch_error` adds an "invalid vector code" reason beside duplicate and empty.
* `src/core/consult.py`: **modified function** `_require_complete_grade_set` returns one reason carrying both the missing labels and the unexpected decoded vectors. It keeps the same exception class and routing. **Modified function** `_normalize_rubric_task_response`: for `grades_encoded_notes` jobs, a letter-pipe fallback row with zero grades becomes one `decode_failures` entry per batch entity (raw reply as reason) instead of a silent `grades: []` row.
* `src/core/agent.py`: **modified function** `_decode_payload`. In the notes-tolerant job path, a line with empty `grade_segs` appends a `decode_failures` entry (id, pos, reason) and skips the line, matching the existing [AST-1996](https://linear.app/astralcareermatch/issue/AST-1996/isolate-malformed-encoded-grade-lines-per-entity-retry-not-hop-error) handling. No new states or config keys.

## Ancestor candidates

- [X] [AST-1155](<https://linear.app/astralcareermatch/issue/AST-1155>) / [AST-1150](<https://linear.app/astralcareermatch/issue/AST-1150>) — Incomplete grades → retry holding, never technical fail (`docs/features/consult/ast-1155-incomplete-grades-retry-holding-never-technical-fail.md`, `ast-1150-technical-fail-for-do-prompt.md`). Owns `_require_complete_grade_set`, the `missing` / `unknown vectors` messages, and the retry → error route this failure took.
- [ ] [AST-2007](https://linear.app/astralcareermatch/issue/AST-2007) / [AST-2008](https://linear.app/astralcareermatch/issue/AST-2008) — rubric code uptick + sync duplicate retire (`docs/features/consult/ast-1513-reject-duplicate-do-rubric-codes-meteorite-grade-do-is-failing.md` § AST-2008). Owns the pre-save code helper and `sync_rubric_vectors_from_criteria`, where the `V{idx}` fallback lives. This is the lead candidate if step 1 confirms `V01`-style codes.
- [ ] [AST-723](<https://linear.app/astralcareermatch/issue/AST-723>) — rubric vector read/write cutover (`docs/features/auditor/ast-723-rubric-vector-read-write-cutover.md`). Introduced `rubric_vector` sync and `{$RUBRIC_VECTORS}` from those rows, the origin of the code-assignment contract.
- [ ] [AST-1510](<https://linear.app/astralcareermatch/issue/AST-1510>) / [AST-1513](<https://linear.app/astralcareermatch/issue/AST-1513>) — meteorite_grade_do is failing / duplicate Do rubric codes (`docs/features/consult/ast-1510-meteorite-grade-do-is-failing.md`, `ast-1513-…`). Same task and the same Somerset rubric, with an earlier `missing vectors` caused by code→label mapping.
- [ ] [AST-1154](<https://linear.app/astralcareermatch/issue/AST-1154>) — Rubric completeness contracts, all graded tasks (`docs/features/consult/ast-1154-rubric-completeness-contracts-all-graded-tasks.md`). The prompt-side "every vector gets a segment" contract; relevant only if step 1 shows the model replied in prose.
- [ ] [AST-483](<https://linear.app/astralcareermatch/issue/AST-483>) — Normalize grades segment whitespace in agent decode (`docs/features/boards/ast-483-normalize-grades-segment-whitespace-in-agent-decode.md`). Owns the `_GRADE_SEG` / notes classification loop and the "do not widen `_GRADE_SEG`" decision.
- [ ] [AST-1193](<https://linear.app/astralcareermatch/issue/AST-1193>) — Analysis token vector/rubric match parity (`docs/features/artifacts/ast-1193-analysis-token-vector-rubric-match-parity.md`). Label-or-code matching rules shared by scoring. Context only.

## Original report

```
2026-10-09 15:12:19  [INFO]  somerset | dispatch job starting
meteorite_grade_do — 1 available (batch:
meteorite_grade_do-3f837cd7-89e5-47f6-9ae1-e8aae7ee4284)
2026-10-09 15:12:27  [INFO]  somerset | dispatch job task completed:
meteorite_grade_do pass:0 fail:0 error:1 (batch:
meteorite_grade_do-3f837cd7-89e5-47f6-9ae1-e8aae7ee4284)
2026-10-09 15:12:27  [ERROR]  cfcccdcb-1c07-4b23-9a46-834382f2ef42 ->
METEORITE_FAILED_TECHNICAL_DO [_render_score: missing vectors
['AI-Assisted Delivery Rigor', 'Autonomous Scope Ownership', 'Clean
Handoff & Documentation', 'Delivering Under Regulatory Weight',
'Distributed Team Cadence', 'Hands-On Technical Partnership', 'Process
& Systems Design', 'Rapid Value Ramp', 'Scope Discipline & Iteration
Efficiency', 'Stakeholder De-escalation', 'Turnaround of Slipping
Programs']]
2026-10-09 15:12:27  [INFO]  LLM openrouter host=Parasail
task=meteorite_grade_do 5.2s stop=end_turn tokens in=8992 out=73
```

### Comments

#### chuckles — 2026-10-10T02:54:44.408Z
[check-linear] answered — the missing piece is the status. Move this ticket to **Todo** and assign it to Chuckles. That starts the fix with your checked candidate (AST-1155 / AST-1150). Assigning to Chuckles while it's still in Discussion only re-runs the diagnosis pass, which is why it came back to you. My earlier note should have said Todo.

#### susan — 2026-10-10T02:54:05.880Z
@chuckles What am I missing? I chose a candidate ticket.

#### chuckles — 2026-10-10T02:40:13.681Z
[check-linear] answered — not a duplicate of an unlanded fix. I checked every unmerged `ftr/*` and `sub/*` branch against `origin/dev`.

- The rubric and grade fixes that look related ([AST-2011](https://linear.app/astralcareermatch/issue/AST-2011) all-X, [AST-2013](https://linear.app/astralcareermatch/issue/AST-2013)/[AST-2091](https://linear.app/astralcareermatch/issue/AST-2091) duplicate-code gate, [AST-2019](https://linear.app/astralcareermatch/issue/AST-2019) / [AST-2020](https://linear.app/astralcareermatch/issue/AST-2020) rubric gates, [AST-2073](https://linear.app/astralcareermatch/issue/AST-2073) terminal states) are **already on dev**, and this failure keeps recurring after them ([AST-2113](https://linear.app/astralcareermatch/issue/AST-2113), [AST-2118](https://linear.app/astralcareermatch/issue/AST-2118)).
- The only in-flight grade fix is [AST-2108](https://linear.app/astralcareermatch/issue/AST-2108). It changes the `qualify_job_listings` prompt, where the model drops two specific codes. Here all 11 Do vectors come back missing on `grade_do`, so that's a different task and a different failure.
- No unmerged branch touches the parts of the code where this breaks: `_GRADE_SEG`, the `V{idx}` code fallback in `sync_rubric_vectors_from_criteria`, `_require_complete_grade_set`, or `_decode_payload`.
- The same failure on `grade_do` is [AST-2119](https://linear.app/astralcareermatch/issue/AST-2119). It's still in Discussion with no fix branch. That's the duplicate pair, and the two should be folded together.

Discussion (@susan): to continue, check a candidate and assign to Chuckles. If you meant a specific ticket, name it and I'll compare it directly.

#### susan — 2026-10-10T02:38:51.735Z
@chuckles I think this is a duplicate of a fix that just hasn't landed yet.  Can you verify?

#### chuckles — 2026-10-09T22:49:13.174Z
Recurred: [AST-2118](https://linear.app/astralcareermatch/issue/AST-2118) — meteorite_grade_do-5ade3129-88e5-4b0e-be38-9d0eaf2e4e89, 2026-10-09 22:47:38. Host Nebius (not Parasail), 83 tokens out.

#### chuckles — 2026-10-09T21:33:43.508Z
Recurred: [AST-2113](https://linear.app/astralcareermatch/issue/AST-2113) — meteorite_grade_do-02b93b95-af21-4f65-8583-1f969707a559, 2026-10-09 21:32:42.

---

_Implementation detail may live in git history on `origin/dev`._
