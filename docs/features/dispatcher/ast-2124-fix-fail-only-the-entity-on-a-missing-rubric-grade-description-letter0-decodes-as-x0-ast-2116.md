# AST-2124 — fix: fail only the entity on a missing rubric grade description; letter0 decodes as X0 (AST-2116)

<!-- linear-archive: AST-2124 archived 2026-10-16 -->

## Linear archive (AST-2124)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2124/fix-fail-only-the-entity-on-a-missing-rubric-grade-description-letter0  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / 5  
**Parent:** AST-2116 — [✅/Somerset] meteorite_grade_do COMPLETED: 1 error(s) / 2 processed | meteorite_grade_do-8c5dd940-9dac-4833-a057-43ac09c2091d  
**Blocked by / blocks / related:** parent: AST-2116; blocks: AST-2125

### Description

## What this implements

A rubric grade that can't be hydrated no longer sinks a whole batch. For every rubric-graded hydrate site (job consult and company prefilter), an entity whose letter grade (confidence > 0) has no description in that vector's rubric gets a warning log line and goes to its task's `fail_state`. It is not an error and not a retry, and the rest of the batch applies normally. A letter grade with confidence 0 decodes as X0, replacing AST-2053's letter0 → letter1 rewrite. X is always "no signal": it never fails hydrate, and it uses the rubric's X text when present, otherwise a fixed no-signal reason. Statute `astral.agent.confidence-bounds` is amended to match.

## Scope

## Component scope

* `src/core/consult.py`: modified. X hydrate never raises. The job batch consult path and the single-row apply path fail only the affected entity (with a warning) on a missing letter-grade description, instead of erroring or retrying the batch.
* `src/core/roster.py`: modified. The company prefilter batch path and the single-company apply path get the same per-entity fail routing. The prefilter notes builder (which already returns `None` on a hydrate `ValueError`) is checked for consistency.
* `src/core/agent.py`: modified. `_decode_payload` maps letter grades with confidence 0 to X0 instead of letter-with-confidence-1.
* `canon/directives/draft/stat.agent.confidence-bounds.md`: modified. This is the live statute text AST-2053 amended. Letter0 → X0 replaces the letter0 → letter1 sanctioned slip, and X is stated as always no-signal.
* `canon/statutes/astral/agent/astral.agent.confidence-bounds.md`: modified. This harvest copy of the same statute id gets the same statement, so the two copies don't disagree.
* `tests/component/core/test_consult.py`, `tests/component/core/test_agent.py`, `docs/test-bible/core/agent.md`, plus roster prefilter tests (Betty's tree): modified. Coverage for:
  * per-entity fail on a missing description, with batch siblings still applying;
  * X hydrating with no X row;
  * letter0 → X0.

## Technical scope

* `src/core/consult.py`:
  * **Lookup:** `_lookup_rubric_reason_for_grade` gets an X fallback reason.
  * **Hydrate helpers:** they report which entities have a missing description instead of raising once for the batch.
  * **Batch consult caller:** routes those entities to `fail_state` through the existing state-transition helper, with one warning log per entity, and lets the rest apply.
  * **Single-row apply:** `_apply_render_verdict_decoded_job` routes the same condition to fail instead of raising.
  * **Why:** today one missing row errors and retries every job in the batch, and a retry can't fix missing rubric text.
* `src/core/roster.py`: modified functions at the company prefilter batch hydrate site and in `_apply_prefilter_decoded_company_outcome`. Same per-entity routing to the prefilter `fail_state`, because the rule covers all rubric grades.
* `src/core/agent.py`: one-branch change in the non-vet encoded loop of `_decode_payload`, so confidence 0 on a letter becomes X0, per Susan's rule.
* `canon/directives/draft/stat.agent.confidence-bounds.md` and `canon/statutes/astral/agent/astral.agent.confidence-bounds.md`: the same text amendment to the sanctioned-slip rule in both copies of `astral.agent.confidence-bounds`. No code.

## Acceptance criteria

1. A batch where one job's grade has no rubric description (confidence > 0) sends that job to its `fail_state` with one warning log line naming the vector and letter. Every other job in the batch applies normally. Nothing goes to `error_state` or a `_RETRY` state for this cause.
2. The single-row job apply path and both company prefilter paths (batch and single-company) behave the same way, with prefilter using `PREFILTER_FAILED`.
3. A letter grade with confidence 0 in an encoded line decodes as `X0`. The vet branch (`grades_encoded_vet_meta`) is unchanged.
4. An X grade hydrates on a vector with no X row, using a fixed no-signal reason. With an X row present, it uses that row's text.
5. `astral.agent.confidence-bounds` states the new letter0 → X0 rule and "X is always no signal".

## Boundaries

* No save-time or dispatch-preflight rubric validation (Susan chose grade-time handling instead; AST-2091 is untouched).
* No change to scoring math for grades that hydrate fine.
* Somerset's Process & Systems Design F row is an ops data fix, not this ticket.

## Notes for planning

Bug: [AST-2116](https://linear.app/astralcareermatch/issue/AST-2116). Read its As-is / To-be (Susan's rule and decisions) / Proposed steps. Checked ancestor: [AST-2053](https://linear.app/astralcareermatch/issue/AST-2053) (letter0 → letter1 decode, Hedy), whose rewrite this fix replaces.

## Git branch (authoritative)

Parent `ftr/AST-2116-missing-grade-fail`, child `sub/AST-2116/AST-2124-missing-grade-fail`. Created at bug-fix dispatch.

### Comments

#### radia — 2026-10-10T03:56:16.382Z
[code-rubric] PROCEED (Commit: 350dd6ca0) Entity hydrate; X0 canon

#### radia — 2026-10-10T03:55:38.795Z
[code-rubric] REVIEW (Commit: 0d01e20d2) Stacked siblings on sub

#### hedy — 2026-10-10T03:53:41.123Z
`origin/sub/AST-2116/AST-2124-missing-grade-fail` @ `0d01e20d2` · Tests Passed (lighter check, no qa-fix manifest)

`pytest tests/component/core/test_{consult,roster,agent}.py`, pre-fix tree (`f4bc1bdd4` src) vs fix tree, failure sets diffed:
- New with fix: exactly the 3 AST-2053 decode tests owned by AST-2125 (`test_ast2053_letter_conf0_normalised_to_conf1`, `test_ast2053_normalisation_boundaries`, `test_skips_non_dict_payload_rows_and_invalid_confidence`).
- Newly passing: none. 129 other failures are identical on the pre-fix tree (pre-existing, not this ticket).
- Hydrate/all-X/AST-1846 tests: green except 4 roster tests already red on baseline.

#### hedy — 2026-10-10T03:49:18.676Z
`origin/sub/AST-2116/AST-2124-missing-grade-fail` @ `0d01e20d2` · Code Complete

Expected red until AST-2125 lands (tests/bible are AST-2125's, untouched here) — `tests/component/core/test_agent.py` AST-2053 asserts on `{letter}0 → {letter}1`, now `X0`:
- `TestDecodePayload::test_ast2053_letter_conf0_normalised_to_conf1`
- `TestDecodePayload::test_ast2053_normalisation_boundaries`
- `TestDecodeAndAuditBranches::test_skips_non_dict_payload_rows_and_invalid_confidence`

Canon (Joan REVISE): plan §9 wording landed verbatim in both `astral.agent.confidence-bounds` copies; frontmatter untouched.

#### joan — 2026-10-10T02:46:10.898Z
[board-joan]  CANON: REVISE
What: astral.agent.confidence-bounds — Statement + Conforming/Violating must record letter0→X0 and X always no-signal at hydrate — per plan-fix §9 in both statute copies

#### betty — 2026-10-10T02:45:28.116Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/agent.md (AST-2057 block) + core/consult.md + core/roster.md — 3 existing decode tests break (plan names 1) and the repro has no coverage — rewrite letter0 asserts to X0; add per-entity hydrate-miss / X-no-row coverage

Breaks (tests/component/core/test_agent.py, all assert AST-2053 `{letter}0 → {letter}1`):
- `TestDecodePayload::test_ast2053_letter_conf0_normalised_to_conf1` (~L281) — named by plan.
- `TestDecodePayload::test_ast2053_normalisation_boundaries` (~L300) — `_notes` `CRF0` expects `F/1`. **Not named in Blast radius.**
- `TestDecodeAndAuditBranches::test_skips_non_dict_payload_rows_and_invalid_confidence` (~L2673) — `0|CRA0` expects `A/1`. **Not named.**
- Bible: `core/agent.md` L1925 summary line + `### AST-2057` table rows L1942–1943 ("decodes as conf 1", "`CRF0` → `F/1`").

Stay green (checked): `test_treats_parse_errors_as_empty_rows` (same message, subclass of ValueError); the `_hydrate_response_jobs_grade_reasons` / `_hydrate_grade_reasons_from_rubric` plain-`ValueError` stubs in test_consult.py (~L1258, 2694, 3600, 8001) and test_roster.py `TestAst1846…` (~L6797) stay on the structural path; `MagicMock()` stubs return a mock whose `in` check is False, so no false hydrate-miss. Nothing in the tree asserts X raises on a vector with no X row.

No coverage for the repro: nothing tests one entity's missing description failing only that entity while its sibling applies (consult batch to `fail_state`, prefilter to `PREFILTER_FAILED`); `render_verdict` single-row and `_apply_prefilter_decoded_company_outcome` miss branches; X hydrate falling back to `_X_NO_SIGNAL_REASON`. consult.py, roster.py and agent.py are all `LOCKED_AT_100`, so the new branches need tests anyway. qa-fix [bug-repro] = the plan's `## Repro` fixture (red today on the `ValueError`).
context_tokens≈38000

#### hedy — 2026-10-10T02:44:17.612Z
`origin/sub/AST-2116/AST-2124-missing-grade-fail` @ `bf0473254` · per-entity fail; letter0 → X0

---

_Implementation detail may live in git history on `origin/dev`._
