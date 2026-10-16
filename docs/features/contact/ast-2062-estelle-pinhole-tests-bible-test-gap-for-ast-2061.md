# AST-2062 — Estelle pinhole tests + bible (test gap for AST-2061)

<!-- linear-archive: AST-2062 archived 2026-10-16 -->

## Linear archive (AST-2062)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2062/estelle-pinhole-tests-bible-test-gap-for-ast-2061  
**Status at archive:** Archive  
**Project:** Astral Contact  
**Assignee:** katherine  
**Priority / estimate:** None / 3  
**Parent:** AST-2055 — Contact Estelle can currently add a meteorite directly to the job table  
**Blocked by / blocks / related:** parent: AST-2055

### Description

## What this implements

Test-tree and bible coverage for [AST-2061](https://linear.app/astralcareermatch/issue/AST-2061)'s Estelle pinhole fix: no Contact path writes `job` or `candidate`, Contact meteorite writes go through the `nh3` sanitize helper, public-channel `app_mention` events are refused, and the import-time pinhole assert is in place. This child was routed here from Betty's fix-board `[board-betty] TESTS: REVISE` on AST-2061 (same shape as AST-2060 for AST-2059). No product source change.

## Scope

## Component scope

* `tests/component/core/test_contact.py` (modified): retire the `create_contact_meteorite` / `save_candidate_*` / `skill_calls` cases. Patch `fetch_channel_type` in the roughly 20 `C…` `app_mention` cases. Add repros for the candidate-write path being gone, the public-channel refusal (no command, no turn, no save), the private/DM passthrough, and fail-closed on lookup error.
* `tests/component/core/test_meteorite.py` (modified): retire the `create_contact_meteorite` cases. Add repros showing no Contact path reaches `create_meteorite_job`, and that `insert_slack_meteorite` / `apply_paste` / the `contact_land_meteorite` blob are sanitized through the `nh3` helper, including Slack link unwrap before sanitizing and URL query strings surviving.
* `tests/component/utils/test_config.py` (modified): retire the `create_contact_meteorite` / skills / `allowed_paths` subset assertions. Cover the allowed-channel-types field and the pinhole assert.
* `tests/component/ui/api/test_api_contact.py` (modified): admin skills endpoint behavior with an empty skills registry.
* `tests/component/core/test_repo_admin_json.py` (modified): `skill_calls` references, per Betty's blast-radius list.
* `tests/component/external/test_slack.py` (modified): the new `conversations.info` channel-type helper (im / mpim / group / channel mapping, error path).
* `docs/test-bible/core/contact.md`, `docs/test-bible/core/meteorite.md`, `docs/test-bible/utils/config.md`, `docs/test-bible/external/slack.md` (modified): bible rows matching the tests above.

## Technical scope

* `test_contact.py`, `test_meteorite.py`, `test_config.py`, `test_api_contact.py`, `test_repo_admin_json.py`: modified and deleted test functions for the retired surfaces, and new test functions for each repro, so the suite asserts the pinhole rather than the old access.
* `test_slack.py`: new test functions for the channel-type helper.
* The four bible files: modified and new rows, so the bible matches the tests.

## Acceptance criteria

- [X] Each repro (job leak, candidate write, unsanitized write, public-channel `app_mention`) fails on the pre-fix tree and passes on the AST-2061 tip.
- [X] The existing tests that Betty named as broken by the fix pass against the shipped fix. No test still references `create_contact_meteorite` or the `save_candidate_*` skills.
- [X] The bible matches the tests.

## Boundaries

- [X] No `src/` change: AST-2061 owns the product fix.
- [X] Estelle's system prompt in `data/admin/agent_task.json` still mentions skills (Katherine's plan-fix follow-up). That is out of scope here.

## Notes for planning

Betty's verdict comment on AST-2061 (`[board-betty] TESTS: REVISE`) names the exact gaps. Doc to patch: `docs/features/contact/ast-1517-create-contact-meteorite.md`, with a `## Bug: <this id>` block alongside AST-2061's. This child is blocked by AST-2061 so the tests run against the shipped fix on `ftr`.

## Git branch (authoritative)

Parent `ftr/AST-2055-estelle-pinhole`; this child `sub/AST-2055/AST-2062-estelle-pinhole-tests`. Registry is authoritative.

### Comments

#### chuckles — 2026-10-08T23:07:33.029Z
Radia fix-now (`data/admin/*`) adjudicated: those are Susan's commits already on `origin/dev`, pulled in by `sync(dev)`; the sub matches `dev` byte-for-byte there, so reverting would undo dev work. No resolve-child. Details in the plan doc § Radia review — AST-2062.

#### radia — 2026-10-08T23:07:32.054Z
[code-rubric] REVIEW (Commit: 20fc3341) drop data/admin churn

#### katherine — 2026-10-08T23:05:56.413Z
`origin/sub/AST-2055/AST-2062-estelle-pinhole-tests` @ `20fc3341` · [bug-repro] 8/8 red on pre-fix src `2fd5c63e7` (assertion failures), 8/8 green on tip; full manifest 120 passed, 5 deselected.

#### betty — 2026-10-08T23:03:43.141Z
[bug-repro]
`origin/sub/AST-2055/AST-2062-estelle-pinhole-tests` @ `91220f994` · repro lands red, awaits fix

#### joan — 2026-10-08T22:55:19.162Z
[board-joan]  CANON: OK

#### betty — 2026-10-08T22:55:01.986Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/{contact,meteorite}.md + utils/config.md + external/slack.md — broken tests + missing repro coverage — the whole fix is test-tree work: 33 AST-2061 reds (TestAst1517CreateContactMeteorite, 18 C… app_mention cases, AST-1515 sample key, TestAst1071 skill runners/config, skill_calls loop) to revise, plus four [bug-repro] groups and fetch_channel_type / sanitize_contact_text / pinhole-assert cases to land via qa-fix per the plan (no src/ change).

#### katherine — 2026-10-08T22:54:05.857Z
`origin/sub/AST-2055/AST-2062-estelle-pinhole-tests` @ `9b41c749` · pinhole tests plan ready

---

_Implementation detail may live in git history on `origin/dev`._
