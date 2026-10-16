# AST-2053 — fix: normalise letter-grade confidence 0 to 1 in encoded grade decode

<!-- linear-archive: AST-2053 archived 2026-10-16 -->

## Linear archive (AST-2053)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2053/fix-normalise-letter-grade-confidence-0-to-1-in-encoded-grade-decode  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / 2  
**Parent:** AST-2045 — [✅/Somerset] evaluate_meteorite COMPLETED: 1 error(s) / 2 processed | evaluate_meteorite-2ec6203d-be72-40ff-9fd4-f4787cbddf6d  
**Blocked by / blocks / related:** parent: AST-2045; blocks: AST-2057

### Description

## What this implements

The encoded-grade decoder stops rejecting a letter grade written with confidence 0. A segment `{A-F}0` is normalised to `{A-F}1` (same letter, confidence 1, which already scores as no signal), so one model slip no longer costs the entity a retry strike or sends it to terminal error. The `astral.agent.confidence-bounds` statute records this as the one sanctioned exception.

## Resolved open questions (Susan approved the bug's To-be by reassigning)

* **Option B only:** decoder normalisation. No prompt change; `src/utils/config.py` and `data/admin/agent_task.json` are **out**.
* **Normal form:** `{letter}0 → {letter}1`, not `X0`. Both score as no signal, but `{letter}1` keeps the letter, never produces a forbidden QC `X` (AST-1910), and does not push a line toward `AllLiteralXGradeSetError`.

## Scope

## Component scope

* `src/core/agent.py` (modified). `_decode_payload`'s encoded grades loop holds the non-X `conf_d not in 1..5` rejection that sent this job to error. That branch becomes a normalisation for confidence 0.
* `canon/directives/draft/stat.agent.confidence-bounds.md` (modified). The statute that today says letter grades carry confidence 1–5 gains the one sanctioned `{A-F}0 → {A-F}1` decoder exception.

## Technical scope

* `src/core/agent.py`: modified function `_decode_payload`. In the per-segment confidence check, a non-X segment with confidence 0 is appended as a grade row with confidence 1 instead of setting the bad-line reason. A model writing "no signal" with a letter then costs no retry strike. Confidence 6–9 on a letter, and `X` with nonzero confidence, keep today's `decode_failures` handling.
* `canon/directives/draft/stat.agent.confidence-bounds.md`: modified statute statement plus a conforming example, so reviewers (Joan/Radia) score the coercion as compliant rather than as a breach of the 1–5 bound.

## Acceptance criteria

* A grades-only encoded line containing `{A-F}0` segments decodes to a grade row per segment with the same letter and confidence 1, and no `decode_failures` entry for that line.
* `X` with nonzero confidence and letter confidence outside 0–5 still produce `decode_failures` exactly as today.
* The vet path (`grades_encoded_vet_meta`) is unchanged.

## Boundaries

* No prompt or `agent_task.json` change.
* No change to retry/terminal routing (`_consult_batch_fail_dest`) or scoring.
* Re-dispatching the stranded job `a9112ac6-…` is an operator nudge, not part of this ticket.

## Notes for planning

Ancestor (Susan checked): [AST-1996](https://linear.app/astralcareermatch/issue/AST-1996), the per-line `decode_failures` isolation patch in `docs/features/consult/ast-1155-incomplete-grades-retry-holding-never-technical-fail.md`. Patch that existing doc (plan-fix never creates a new one).

## Git branch (authoritative)

Parent `ftr/AST-2045-letter-conf0-normalize`; this child `sub/AST-2045/AST-2053-letter-conf0-normalize`. Registry is authoritative.

### Comments

#### radia — 2026-10-08T20:41:34.128Z
[code-rubric] PROCEED (Commit: d1aa65ba4) Conf-0 decode; canon aligned

#### radia — 2026-10-08T20:40:44.570Z
[code-rubric] REVIEW (Commit: 2456e6194) ftr lag; sibling scope

#### hedy — 2026-10-08T20:38:37.124Z
`origin/sub/AST-2045/AST-2053-letter-conf0-normalize` @ `2456e6194` · test-fix (lighter path — qa-fix skipped, Betty REVISE → AST-2057)

- `py_compile src/core/agent.py` OK.
- `pytest tests/component/core/test_agent.py`: tip **47 failed / 373 passed**; pre-fix tree (`055c53c2a` agent.py) **47 failed / 373 passed** — identical failure set, **delta 0**.
- The two AST-2057 tests (`test_rejects_bad_positions_and_records_trailing_meta`, `test_skips_non_dict_payload_rows_and_invalid_confidence`) are red on both, as expected.
- The other 45 reds pre-date this fix and are unrelated to decode confidence (missing `config.CRAFT_RUBRIC_MAX_TOKENS`, `tracker.persist_advise_job_resume_coded_advice`, resume-section wording, `KeyError: 'company_id'`/`'jobs'` …) — test-tree drift vs dev, flagged for Betty, not this ticket.
- `tests/component/core/test_consult.py` cannot be collected in this env (`ModuleNotFoundError: asyncpg`) on either tree — not run.

#### joan — 2026-10-08T20:35:22.542Z
[board-joan]  CANON: REVISE
What: astral.agent.confidence-bounds — Statement + Conforming must record sanctioned non-vet `{letter}0`→`{letter}1` decode normalisation — per plan-fix wording in draft statute

#### betty — 2026-10-08T20:34:39.352Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/agent.md (AST-2001 block) + tests/component/core/test_agent.py — no coverage for {letter}0 → {letter}1 normalisation (repro `CFC0`/`SSC0`/`TCC0` line decodes, no `decode_failures`); `TestDecodeAndAuditBranches::test_skips_non_dict_payload_rows_and_invalid_confidence` (`0|CRA0` raises `confidence 1-5`) breaks under this fix; `TestDecodePayload::test_rejects_bad_positions_and_records_trailing_meta` (`0|CRX2` raise) is stale vs f8d3f9a12 and should assert an X-branch `decode_failures` entry; bible AST-2001 row still says non-X confidence bounds raise.

#### hedy — 2026-10-08T20:33:31.706Z
`origin/sub/AST-2045/AST-2053-letter-conf0-normalize` @ `c04071edb` · letter0 → letter1 planned

---

_Implementation detail may live in git history on `origin/dev`._
