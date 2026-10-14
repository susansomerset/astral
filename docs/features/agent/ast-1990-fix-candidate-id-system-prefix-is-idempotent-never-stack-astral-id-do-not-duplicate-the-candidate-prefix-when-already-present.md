# AST-1990 — fix: candidate-id system prefix is idempotent — never stack [astral-<id>] (Do not duplicate the candidate prefix when already present.)

<!-- linear-archive: AST-1990 archived 2026-10-13 -->

## Linear archive (AST-1990)

**Archived:** 2026-10-13  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1990/fix-candidate-id-system-prefix-is-idempotent-never-stack-astral-id-do  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** ada  
**Priority / estimate:** None / 1  
**Parent:** AST-1985 — Do not duplicate the candidate prefix when already present.  
**Blocked by / blocks / related:** parent: AST-1985

### Description

## What this implements

Make the AST-1639 cache-isolation marker idempotent: `_system_text_with_candidate_prefix` in `src/core/agent.py` must emit exactly one `[astral-<id>]` at byte zero no matter how many times system text passes through preview / store / assembly — today it prepends unconditionally, so re-fed text stacks copies (`[astral-somerset]` ×5 in the AST-1985 report).

## Scope

## Component scope

* `src/core/agent.py` — modified: `_system_text_with_candidate_prefix` is the only place the marker is built, so making it idempotent fixes every caller (wire, store, preview) at once.
* `tests/component/core/test_agent.py` — modified (Betty-owned, test tree): new case(s) in the AST-1639 prefix suite for already-prefixed input.

## Technical scope

* `src/core/agent.py` — modified function `_system_text_with_candidate_prefix`: normalize away existing leading `[astral-…]` marker(s) before prepending exactly one, so repeated passes cannot stack copies. No new tables or fields, and no call-site signature changes.
* `tests/component/core/test_agent.py` — new test function(s) for idempotence: one already-prefixed input and one five-times-prefixed input should each come out with a single marker.

## Acceptance criteria

* Already-prefixed system text (one or many leading `[astral-…]` markers) comes out with exactly one `[astral-<cid>]` at byte zero.
* Wire text, `preview_prompt` system text, and stored SYSTEM `agent_data` rows stay byte-identical (AST-1639 parity contract).
* Missing / blank candidate id still fails closed (`ValueError`), no send.
* Existing `TestAst1639CandidateIdSystemPrefix` stays green.

## Boundaries

Helper-only fix — no call-site signature changes, no new tables/fields. Tests / bible are Betty's (fix-board decides whether a gap child is needed). Orphaned mini-parent is AST-1985; approved ancestor AST-1639 (archived — no related link).

## Notes for planning

AST-1985 Description (As-is / To-be / Proposed steps) is authoritative. Susan approved Proposed step 1 as written — strip **any** leading run of `[astral-…]` markers, then prepend exactly one (step 2's open question was not answered separately; step 1's any-marker reading stands). Plan-doc patch target (approved ancestor): `docs/features/agent/ast-1639-candidate-id-system-prompt-prefix.md`.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1985-candidate-prefix-dedupe`, child `sub/AST-1985/AST-1990-candidate-prefix-dedupe`. Created at bug-fix.

### Comments

#### radia — 2026-10-06T04:29:36.932Z
[code-rubric] PROCEED (Commit: 2b0b74f0) idempotent prefix clean

#### ada — 2026-10-06T04:28:25.539Z
`origin/sub/AST-1985/AST-1990-candidate-prefix-dedupe` @ `2b0b74f00` · test-fix lighter path (no qa-fix on this ticket)

- `TestAst1639CandidateIdSystemPrefix` green; AST-1992's 6 new idempotence tests pass against this tip (read-only overlay, not committed).
- Full `tests/component/core/test_agent.py`: 356 passed / 40 failed — identical 40-failure set on pre-fix `5bee4129f`, none in the AST-1639 suite (resume section keys, `company_id`/`jobs` KeyErrors, missing `tracker.persist_advise_job_resume_coded_advice`). Pre-existing, outside this fix's blast radius.

#### joan — 2026-10-06T04:22:00.244Z
[board-joan]  CANON: OK

#### betty — 2026-10-06T04:21:19.549Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/agent.md § AST-1639 — missing coverage — TestAst1639CandidateIdSystemPrefix has no idempotence case; add already-prefixed + 5x-stacked (+ other-id marker) inputs collapsing to one [astral-<cid>], and blank id raising even when body carries a marker.

#### ada — 2026-10-06T04:20:09.472Z
`origin/sub/AST-1985/AST-1990-candidate-prefix-dedupe` @ `d8f4f213` · idempotent prefix plan

---

_Implementation detail may live in git history on `origin/dev`._
