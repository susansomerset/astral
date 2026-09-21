# AST-1467 — gap: gaze_email test coverage for retire (AST-1466)

<!-- linear-archive: AST-1467 archived 2026-09-09 -->

## Linear archive (AST-1467)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1467/gap-gaze-email-test-coverage-for-retire-ast-1466  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** katherine  
**Priority / estimate:** None / 2  
**Parent:** AST-1363 — Clean up agent_task so that only the right meteorite email intake task is run  
**Blocked by / blocks / related:** parent: AST-1363

### Description

## What this implements

Fix-lane test gap for parent fix AST-1466 (retire gaze_email stack). Betty board REVISE: retarget/delete gaze_email test coverage before make-fix lands.

## Scope

### Component scope

* `tests/component/core/test_gaze_email.py` — delete or retarget to meteorite_email mailbox runner.
* `docs/test-bible/core/gaze_email.md` — retire or fold into meteorite-mailbox bible.
* `tests/component/core/test_dispatcher.py`, `test_api_inbox.py`, `test_api_admin.py`, `test_config.py`, `test_repo_admin_json.py`, frontend Scheduled Actions tests — update gaze_email asserts for meteorite_email rehome.

### Technical scope

* Delete `test_gaze_email.py` or retarget imports/entrypoints to rehomed `meteorite_email` module.
* Revise bible nodes and component asserts that reference `gaze_email` task_key, `GAZE_EMAIL_CONFIG`, or `run_gaze_email*` symbols.

## Board verdict (from AST-1466)

[board-betty] TESTS: REVISE
What: docs/test-bible/core/gaze_email.md — broken test retarget — test_gaze_email.py delete + dispatcher/inbox/admin/config/repo_admin_json gaze_email asserts break on meteorite_email rehome

## Git branch (authoritative)

sub/AST-1363/<child-segment> off ftr/AST-1363-clean-up-agent-task-so-that-only-the-right-meteorite-email-intake-task-is-run

## QA test manifest

**\[bug-repro\]** `tests/component/core/test_ast1467_gaze_email_retire.py::TestAst1467GazeEmailRetired` — inventory gate (no `gaze_email` seed/config/module/dispatcher symbols; `METEORITE_EMAIL_MAILBOX_CONFIG` + `meteorite_email` module present). Green with AST-1466 on tip.

**Retarget / delete (board scope):**

* Deleted `tests/component/core/test_gaze_email.py` → `tests/component/core/test_meteorite_email.py`
* Retargeted: `test_config.py`, `test_dispatcher.py`, `test_api_inbox.py`, `test_api_admin.py`, `test_repo_admin_json.py`, `test_dispatch_tasks.py`
* Bible: `docs/test-bible/core/gaze_email.md` → `docs/test-bible/core/meteorite_email.md`

**Return pass (Review Posted + \[qa-handoff\] — Radia FIX-NOW):**

1. Rewrote all `run_component_tests` blocks in `docs/test-bible/core/meteorite_email.md` to `tests/component/core/test_meteorite_email.py` (+ matching node ids).
2. Retired `tests/component/frontend/pages/test_AdminScheduledActions_AST1106.test.tsx` (gaze Avail-gt0 carve-out obsolete post–AST-1134/1466); bible § AST-1106 + `repo_admin_json.md` AST-1219 Vitest pointer retargeted to AST-887/AST-894.

**Bible shasums** (`origin/sub/AST-1363/AST-1467-gap-gaze-email-test-coverage-for-retire` @ `31bffc80`):

* `docs/test-bible/core/meteorite_email.md` — `a87ca3631be71e884947c21cad532587f300057c`
* `docs/test-bible/frontend/pages.md` — `a8332f5b31203df8eea74bbb0d633655669196c8`
* `docs/test-bible/core/repo_admin_json.md` — `cbf7d9fd8c4da6e72fdc0ae3ac9d0c37e5c16b55`

**Publish:** `origin/sub/AST-1363/AST-1467-gap-gaze-email-test-coverage-for-retire` @ `31bffc80` (`merge-tests(AST-1467): origin/tests 0fa5bc81`)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_ast1467_gaze_email_retire.py::TestAst1467GazeEmailRetired \
  -q
```

### Comments

#### betty — 2026-08-24T23:46:07.198Z
`origin/sub/AST-1363/AST-1467-gap-gaze-email-test-coverage-for-retire` @ `31bffc80` · FIX-NOW bible+AST1106

#### katherine — 2026-08-24T23:26:03.626Z
[qa-handoff]
@Betty White

Radia FIX-NOW on AST-1467 (Review Posted) — both items are test-tree / bible only; Katherine cannot land them (resolve-child test-tree ban). Staying **Review Posted**; please revise and reassign Katherine.

1. **`docs/test-bible/core/meteorite_email.md`** — header correctly names `test_meteorite_email.py`, but every `./scripts/testing/run_component_tests.sh` block still points at deleted `tests/component/core/test_gaze_email.py` (and `::TestAst…` paths under that file). Rewrite those commands to `tests/component/core/test_meteorite_email.py` (+ matching node ids).

2. **`tests/component/frontend/pages/test_AdminScheduledActions_AST1106.test.tsx`** (+ bible node in `docs/test-bible/frontend/pages.md` § AST-1106 if needed) — still seeds `gaze_email` task_key / Avail-gt0 always-visible carve-out. Post–AST-1134 / AST-1466 that carve-out is retired; mailbox identity is `meteorite_email` with real bind-filtered Avail. Retarget asserts to `meteorite_email` (or retire the file if the carve-out scenario is obsolete).

Tip when reassigned: `origin/sub/AST-1363/AST-1467-gap-gaze-email-test-coverage-for-retire` @ `05b26a9f` (post-sync).

#### radia — 2026-08-24T23:06:31.169Z
[code-rubric] REVIEW (Commit: 33c0bf3e) Bible manifests + frontend gap

#### katherine — 2026-08-24T22:45:00.547Z
`origin/sub/AST-1363/AST-1467-gap-gaze-email-test-coverage-for-retire` @ `33c0bf3e3eba8306605de3f35d3cc56ffd2eaf25`

[bug-repro] `TestAst1467GazeEmailRetired` green (6 passed) with AST-1466 product on tip. Manifest command satisfied. Board-scoped mailbox suite green; merge conflict on `test_repo_admin_json.py` resolved to Betty’s 54-count catalog asserts.

#### betty — 2026-08-24T22:14:25.626Z
[bug-repro]
`origin/sub/AST-1363/AST-1467-gap-gaze-email-test-coverage-for-retire` @ `bb619d55` · repro lands red, awaits fix

#### betty — 2026-08-24T22:03:53.006Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/gaze_email.md — broken test retarget — test_gaze_email.py delete + dispatcher/inbox/admin/config/repo_admin_json gaze_email asserts break on meteorite_email rehome

---

_Implementation detail may live in git history on `origin/dev`._
