<!-- linear-archive: AST-1222 archived 2026-08-17 -->

## Linear archive (AST-1222)

**Archived:** 2026-08-17  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1222/meteorite-doget-alias-seed-retarget-dispatch-task-config-aliases-via  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1184 — Task config aliases via master_task_key  
**Blocked by / blocks / related:** parent: AST-1184

### Description

## What this implements

After #2: add alias `agent_task` identities (grouping under Meteorite Review / live section; prompts from master — no override), retarget `METEORITE_DISPATCH_TASKS` Do/Get rows to `meteorite_grade_do` / `meteorite_grade_get`, and keep fixtures/seed consistent. Does **not** invent the resolve helpers (siblings #1–#2) or own the UI hardcode audit (**AST-1185**).

## In scope

- [X] `astral.seed.agent-tables-in-repo-json` — grouping-only alias rows in `data/admin/agent_task.json` (+ AST-756 fixture surgical sync)
- [X] `astral.standards.no-hardcoded-sets` — retarget via `METEORITE_DISPATCH_TASKS` / `SEED_CONFIG` catalog; no new meteorite-only alias map
- [X] `astral.standards.in-scope-only` — seed + dispatch retarget + stale shared-key retirement only
- [X] `astral.standards.names-not-ticket-ids` — domain keys `meteorite_grade_do` / `meteorite_grade_get`
- [X] `astral.git.engineer-test-tree-ban` — no `tests/` / bible edits on this ticket
- [X] `pattern.layers.import-discipline` / `astral.layers.import-direction` — dispatcher continues to consume catalog from utils; no reverse imports

## Considered but excluded

- [X] `pattern.config.config-block` / proposed `pattern.config.task-alias` / resolve helpers + alias `TASK_CONFIG` literals — **AST-1220** (`src/utils/config.py`)
- [X] Runtime prompt resolve / consult overlay retirement / exhaust keys — **AST-1221** (`src/core/agent.py`, `consult.py`, `dispatcher.py` exhaust set)
- [X] UI hardcode audit / alphabetical dropdowns — **AST-1185**
- [X] Gaze/Meteorite Review section rename — **AST-1183** (live section already Meteorite Review; this child only seeds into it)

## Acceptance criteria

- [X] Meteorite dispatch rows for Do/Get use the alias task keys with meteorite trigger states; classic Gaze rows continue to use `grade_do` / `grade_get`.
- [X] Alias identities have `agent_task` grouping metadata that can place them under Meteorite Review (or the live meteorite section name) independently of the master's Gaze Review grouping.
- [X] Admin task-key listings that are config/DB-driven include the new alias keys (alphabetical / catalog behavior refinements remain **AST-1185**).
- [X] Editing the master's prompts changes what the alias runs; the alias has no divergent prompt row.

## Boundaries

Does **not** invent resolve helpers (siblings #1–#2). Does **not** own UI hardcode audit (AST-1185). Does **not** rename Gaze/Meteorite Review sections (AST-1183).

## Notes for planning

After AST-1221. Grouping section name = live seed at land time (Meteorite Review on tip after AST-1183/AST-1219).

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1184-task-config-aliases-via-master-task-key`, child `sub/AST-1184/<this-id>-meteorite-do-get-alias-seed-retarget-dispatch`. Created at dispatch-parent.

### Comments

#### chuckles — 2026-08-06T09:49:38.603Z
[merge-child] blocked: validate-sub-log — missing plan/code/merge-tests/test in ftr..sub range

Product for AST-1222 is already on `origin/ftr/AST-1184-task-config-aliases-via-master-task-key` (through prior resolve `0562a37d` + `merge-resume` `cea4222d`). Residual `ftr..sub` is only:
- `docs(AST-1222): Radia review — clean (post-restack re-verify)`
- `resolve(AST-1222): — clean`

`validate-sub-log` scopes the canonical sequence to that residual range, so it fails even though plan/code/merge-tests/test are ancestors of ftr tip.

@Katherine Johnson — on `origin/sub/AST-1184/AST-1222-meteorite-do-get-alias-seed-retarget-dispatch`, add empty tip-marker commits (see `plan(AST-1189): — tip marker for merge-child validate-sub-log`) for the missing labels in order: `plan(AST-1222):`, `code(AST-1222):`, `merge-tests(AST-1222):`, `test(AST-1222):` (docs+resolve already present), force-with-lease push, stay User Testing. Chuckles will re-run merge-child after.

— Chuckles

#### radia — 2026-08-06T09:46:33.538Z
[code-rubric] revision=1

**Rubric:** code-rubric.v1
**Ticket:** AST-1222
**Publish ref:** `bbbe983c` (`origin/sub/AST-1184/AST-1222-meteorite-do-get-alias-seed-retarget-dispatch`)
**Overall:** CLEAN

## Plan adherence

- Re-review after `merge-child` bounced this ticket `Review Posted` → `User Testing` → `Tests Ready` → `Tests Passed` for a git-history restack — `validate-sub-log.sh` had flagged bad `Merge remote-tracking branch` subjects in the `ftr..sub` range, not a content problem. Katherine restacked cleanly onto `origin/ftr/AST-1184-...` and force-pushed; Betty re-ran `merge-tests`; engineer `resolve` was clean (no fix needed).
- Verified `git diff <prior-reviewed-tip>..cea4222d -- src/utils/config.py src/core/dispatcher.py data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json` is **empty** — byte-identical to the content I already reviewed clean this session. The only non-empty diff anywhere in the tree is this plan doc's own carried-forward review/resolution history from the rebase.
- `ftr..sub` range is now clean (zero commits, `origin/ftr/AST-1184-task-config-aliases-via-master-task-key` == this tip — already fast-forwarded by `merge-child`). No `Merge remote-tracking branch` subjects remain.
- `python3 -m py_compile src/utils/config.py src/core/dispatcher.py src/core/agent.py src/core/consult.py` clean at tip. Prior full active-set sweep (65 active statutes, zero `violates`/`needs-discussion`) still applies unchanged since the diff content did not move.

**Note:** this three-dot diff still carries AST-1220's and AST-1221's already-reviewed changes (merged via `origin/ftr/AST-1184-...`, neither sibling has landed `dev` yet) — both independently Review Posted clean.

**Pattern conformance:** `pattern.layers.import-discipline` — conforms (no new imports; no content change this pass).

## Frame diff

(none — ticket description/AC unchanged; no findings to fold in)

context_tokens≈45000

— Radia

#### betty — 2026-08-06T09:22:24.090Z
## QA test manifesto

`origin/sub/AST-1184/AST-1222-meteorite-do-get-alias-seed-retarget-dispatch` @ `e459d368` (`merge-tests(AST-1222): origin/tests f51cd0546eb70c514879430d197e9c0581afdb3c`)

1. `tests/component/utils/test_config.py::TestAst1222MeteoriteAliasDispatchAndSeed` — dispatch catalog + SEED_CONFIG SQL + grouping catalog key
2. `tests/component/utils/test_config.py::TestAst1054MeteoriteGdlDispatch` + `TestAst1220TaskAliasConfigContract` — revised to alias Do/Get pairs
3. `tests/component/core/test_dispatcher.py::TestAst1054MeteoriteDispatchProvision` — alias insert lookups + `test_ensure_retires_shared_key_meteorite_do_get_when_aliases_present`
4. `tests/component/core/test_repo_admin_json.py::TestAst1222MeteoriteGradeAliasCatalogRows` — grouping-only seed + fixture lockstep
5. Revised catalog count/seq: `TestAst786AgentTaskRepoJsonSeed` (55), `TestAst1211EvaluateCraftFixtureLockstep`, `TestAst1218GazeReviewClassicGroupLabel`, `TestAst1219MeteoriteReviewGroupMembership`, `TestAst1055MeteoriteCatalogRows` (like/upshot 7/8)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1222MeteoriteAliasDispatchAndSeed \
  tests/component/utils/test_config.py::TestAst1054MeteoriteGdlDispatch \
  tests/component/utils/test_config.py::TestAst1220TaskAliasConfigContract \
  tests/component/core/test_dispatcher.py::TestAst1054MeteoriteDispatchProvision \
  tests/component/core/test_repo_admin_json.py::TestAst1222MeteoriteGradeAliasCatalogRows \
  tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed \
  tests/component/core/test_repo_admin_json.py::TestAst1219MeteoriteReviewGroupMembership \
  tests/component/core/test_repo_admin_json.py::TestAst1218GazeReviewClassicGroupLabel \
  tests/component/core/test_repo_admin_json.py::TestAst1055MeteoriteCatalogRows \
  tests/component/core/test_repo_admin_json.py::TestAst1211EvaluateCraftFixtureLockstep \
  -q
```

**Broken / obsolete revised:** shared-key meteorite Do/Get dispatch pins; catalog 53→55; Meteorite Review six-key exclusivity → eight keys; like/upshot seq 5/6 → 7/8.

**Bible shasum** (`origin/sub/...` tip):
- `docs/test-bible/utils/config.md` `0fdf85c781af4b85f5e7feffcdf019f0a9ade394`
- `docs/test-bible/core/dispatcher.md` `65b6a61d2cb08d0c033e6fd1bb5aa15f1d1f81cc`
- `docs/test-bible/core/repo_admin_json.md` `4958ac2489064aa45f6d6688e4d685a224f7e4da`

— Betty

#### betty — 2026-08-06T09:21:56.639Z
## QA test manifesto

`origin/sub/AST-1184/AST-1222-meteorite-do-get-alias-seed-retarget-dispatch` @ `e459d368` (`merge-tests(AST-1222): origin/tests f51cd0546eb70c514879430d197e9c0581afdb3c`)

1. `tests/component/utils/test_config.py::TestAst1222MeteoriteAliasDispatchAndSeed` — dispatch catalog + SEED_CONFIG SQL + grouping catalog key
2. `tests/component/utils/test_config.py::TestAst1054MeteoriteGdlDispatch` + `TestAst1220TaskAliasConfigContract` — revised to alias Do/Get pairs
3. `tests/component/core/test_dispatcher.py::TestAst1054MeteoriteDispatchProvision` — alias insert lookups + `test_ensure_retires_shared_key_meteorite_do_get_when_aliases_present`
4. `tests/component/core/test_repo_admin_json.py::TestAst1222MeteoriteGradeAliasCatalogRows` — grouping-only seed + fixture lockstep
5. Revised catalog count/seq: `TestAst786AgentTaskRepoJsonSeed` (55), `TestAst1211EvaluateCraftFixtureLockstep`, `TestAst1218GazeReviewClassicGroupLabel`, `TestAst1219MeteoriteReviewGroupMembership`, `TestAst1055MeteoriteCatalogRows` (like/upshot 7/8)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1222MeteoriteAliasDispatchAndSeed \
  tests/component/utils/test_config.py::TestAst1054MeteoriteGdlDispatch \
  tests/component/utils/test_config.py::TestAst1220TaskAliasConfigContract \
  tests/component/core/test_dispatcher.py::TestAst1054MeteoriteDispatchProvision \
  tests/component/core/test_repo_admin_json.py::TestAst1222MeteoriteGradeAliasCatalogRows \
  tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed \
  tests/component/core/test_repo_admin_json.py::TestAst1219MeteoriteReviewGroupMembership \
  tests/component/core/test_repo_admin_json.py::TestAst1218GazeReviewClassicGroupLabel \
  tests/component/core/test_repo_admin_json.py::TestAst1055MeteoriteCatalogRows \
  tests/component/core/test_repo_admin_json.py::TestAst1211EvaluateCraftFixtureLockstep \
  -q
```

**Broken / obsolete revised:** shared-key meteorite Do/Get dispatch pins; catalog 53→55; Meteorite Review six-key exclusivity → eight keys; like/upshot seq 5/6 → 7/8.

**Bible shasum** (`origin/sub/...` tip):
- `docs/test-bible/utils/config.md` `0fdf85c781af4b85f5e7feffcdf019f0a9ade394`
- `docs/test-bible/core/dispatcher.md` `65b6a61d2cb08d0c033e6fd1bb5aa15f1d1f81cc`
- `docs/test-bible/core/repo_admin_json.md` `4958ac2489064aa45f6d6688e4d685a224f7e4da`

— Betty

#### betty — 2026-08-06T09:21:06.440Z
## QA test manifest

`origin/sub/AST-1184/AST-1222-meteorite-do-get-alias-seed-retarget-dispatch` @ `e459d368` (`merge-tests(AST-1222): origin/tests f51cd0546eb70c514879430d197e9c0581afdb3c`)

1. `tests/component/utils/test_config.py::TestAst1222MeteoriteAliasDispatchAndSeed` — dispatch catalog + SEED_CONFIG SQL + grouping catalog key
2. `tests/component/utils/test_config.py::TestAst1054MeteoriteGdlDispatch` + `TestAst1220TaskAliasConfigContract` — revised to alias Do/Get pairs
3. `tests/component/core/test_dispatcher.py::TestAst1054MeteoriteDispatchProvision` — alias insert lookups + `test_ensure_retires_shared_key_meteorite_do_get_when_aliases_present`
4. `tests/component/core/test_repo_admin_json.py::TestAst1222MeteoriteGradeAliasCatalogRows` — grouping-only seed + fixture lockstep
5. Revised catalog count/seq: `TestAst786AgentTaskRepoJsonSeed` (55), `TestAst1211EvaluateCraftFixtureLockstep`, `TestAst1218GazeReviewClassicGroupLabel`, `TestAst1219MeteoriteReviewGroupMembership`, `TestAst1055MeteoriteCatalogRows` (like/upshot 7/8)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1222MeteoriteAliasDispatchAndSeed \
  tests/component/utils/test_config.py::TestAst1054MeteoriteGdlDispatch \
  tests/component/utils/test_config.py::TestAst1220TaskAliasConfigContract \
  tests/component/core/test_dispatcher.py::TestAst1054MeteoriteDispatchProvision \
  tests/component/core/test_repo_admin_json.py::TestAst1222MeteoriteGradeAliasCatalogRows \
  tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed \
  tests/component/core/test_repo_admin_json.py::TestAst1219MeteoriteReviewGroupMembership \
  tests/component/core/test_repo_admin_json.py::TestAst1218GazeReviewClassicGroupLabel \
  tests/component/core/test_repo_admin_json.py::TestAst1055MeteoriteCatalogRows \
  tests/component/core/test_repo_admin_json.py::TestAst1211EvaluateCraftFixtureLockstep \
  -q
```

**Broken / obsolete revised:** shared-key meteorite Do/Get dispatch pins; catalog 53→55; Meteorite Review six-key exclusivity → eight keys; like/upshot seq 5/6 → 7/8.

**Bible shasum** (`origin/sub/...` tip):
- `docs/test-bible/utils/config.md` `0fdf85c781af4b85f5e7feffcdf019f0a9ade394`
- `docs/test-bible/core/dispatcher.md` `65b6a61d2cb08d0c033e6fd1bb5aa15f1d1f81cc`
- `docs/test-bible/core/repo_admin_json.md` `4958ac2489064aa45f6d6688e4d685a224f7e4da`

— Betty

#### katherine — 2026-08-06T09:16:07.892Z
Restacked onto `origin/ftr/AST-1184-task-config-aliases-via-master-task-key` — no `Merge remote-tracking branch` subjects in `ftr..sub`. `validate-sub-log` ok @ `0562a37d`.

#### chuckles — 2026-08-06T09:13:30.227Z
[merge-child] blocked: git pull merge on sub — use: git fetch && git merge origin/ftr/<parent-segment>

`validate-sub-log.sh` failed on `origin/sub/AST-1184/AST-1222-meteorite-do-get-alias-seed-retarget-dispatch`:
- Bad commit in range vs `origin/ftr/AST-1184-task-config-aliases-via-master-task-key`: `210ad052` — `Merge remote-tracking branch 'origin/ftr/AST-1184-…' into sub/AST-1184/AST-1222-…`
- Also in range (inherited): `5a3243ec` — `Merge remote-tracking branch 'origin/dev' into ftr/AST-1183-…`
- Tip `9f3469d4` resolve sits on that merge history.

@Katherine Johnson — drop the merge commits from the sub log, restack AST-1222 commits (plan→…→resolve + Betty merge-tests) cleanly on `origin/ftr/AST-1184-task-config-aliases-via-master-task-key` (fetch + merge/rebase onto ftr; never leave `Merge remote-tracking branch` subjects on sub), keep tip clean, force-with-lease push `origin/sub/AST-1184/AST-1222-meteorite-do-get-alias-seed-retarget-dispatch`. Chuckles will re-run merge-child after.

— Chuckles

#### radia — 2026-08-06T09:11:09.049Z
[code-rubric] revision=1

**Rubric:** code-rubric.v1
**Ticket:** AST-1222
**Publish ref:** `72c321d5` (`origin/sub/AST-1184/AST-1222-meteorite-do-get-alias-seed-retarget-dispatch`)
**Overall:** CLEAN

## Plan adherence

- Stage 1 retarget is exact: `METEORITE_DISPATCH_TASKS` + `SEED_CONFIG["dispatch_task-meteorite"]` SQL retarget in lockstep to `meteorite_grade_do`/`meteorite_grade_get`; classic `grade_do`/`grade_get` untouched. Retirement in `ensure_meteorite_dispatch_tasks` re-lists rows after insert, gates on **both** alias pairs present, deletes only the two exact shared-key pairs — classic Gaze `grade_do`@`PASSED_JD` / `grade_get`@`PASSED_DO` untouched.
- Stage 2 seed rows are byte-exact against the plan's field tables in both `data/admin/agent_task.json` and the AST-756 fixture (true surgical sync, not `cp`) — verified UUIDs, `Meteorite Review`/`"4500"`, seq 5/6, `agent_id: "n/a"`, empty prompts/`run_next`, and `meteorite_like`/`meteorite_upshot` bumped to 7/8 identically in both files.
- Ran every assertion from the plan's own Stage 1 + Stage 2 verify blocks live at tip — all pass, including `dispatch_task_grouping_catalog_key` returning the alias unchanged (AC3) and `get_task_keys()` membership.
- Commit hygiene holds: `code(AST-1222)` touches only `src/utils/config.py`, `src/core/dispatcher.py`, `data/admin/agent_task.json`, `docs/uat-fixtures/AST-756/expected-agent_task.json`; `test(AST-1222)`/`merge-tests(AST-1222)` touch only Betty's test-tree paths.

**Note:** this three-dot diff also carries AST-1220's and AST-1221's already-reviewed changes (merged onto this branch via `origin/ftr/AST-1184-...`, since neither sibling has landed `dev` yet). Both were independently reviewed clean (Review Posted); this review's findings focus on AST-1222's own commits.

**Pattern conformance:** `pattern.layers.import-discipline` — conforms (no new imports in this ticket's own commits).

Full active-set sweep scored in-session: 65 active statutes (18 universal + 41 scoped-applicable against this diff's `{core, utils, docs}` layers / `src/utils/config.py`, `src/core/dispatcher.py`, `data/admin/agent_task.json`, `docs/uat-fixtures/**`, `docs/features/**`, `docs/test-bible/**`, `tests/**` paths) — zero `violates`, zero `needs-discussion`. `python3 -m py_compile` clean on all touched product modules at tip.

## Frame diff

(none — ticket description/AC unchanged; no findings to fold in)

context_tokens≈95000

— Radia

#### betty — 2026-08-06T09:06:56.213Z
## QA test manifest

`origin/sub/AST-1184/AST-1222-meteorite-do-get-alias-seed-retarget-dispatch` @ `e459d368` (`merge-tests(AST-1222): origin/tests f51cd0546eb70c514879430d197e9c0581afdb3c`)

1. `tests/component/utils/test_config.py::TestAst1222MeteoriteAliasDispatchAndSeed` — dispatch catalog + SEED_CONFIG SQL + grouping catalog key
2. `tests/component/utils/test_config.py::TestAst1054MeteoriteGdlDispatch` + `TestAst1220TaskAliasConfigContract` — revised to alias Do/Get pairs
3. `tests/component/core/test_dispatcher.py::TestAst1054MeteoriteDispatchProvision` — alias insert lookups + `test_ensure_retires_shared_key_meteorite_do_get_when_aliases_present`
4. `tests/component/core/test_repo_admin_json.py::TestAst1222MeteoriteGradeAliasCatalogRows` — grouping-only seed + fixture lockstep
5. Revised catalog count/seq: `TestAst786AgentTaskRepoJsonSeed` (55), `TestAst1211EvaluateCraftFixtureLockstep`, `TestAst1218GazeReviewClassicGroupLabel`, `TestAst1219MeteoriteReviewGroupMembership`, `TestAst1055MeteoriteCatalogRows` (like/upshot 7/8)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1222MeteoriteAliasDispatchAndSeed \
  tests/component/utils/test_config.py::TestAst1054MeteoriteGdlDispatch \
  tests/component/utils/test_config.py::TestAst1220TaskAliasConfigContract \
  tests/component/core/test_dispatcher.py::TestAst1054MeteoriteDispatchProvision \
  tests/component/core/test_repo_admin_json.py::TestAst1222MeteoriteGradeAliasCatalogRows \
  tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed \
  tests/component/core/test_repo_admin_json.py::TestAst1219MeteoriteReviewGroupMembership \
  tests/component/core/test_repo_admin_json.py::TestAst1218GazeReviewClassicGroupLabel \
  tests/component/core/test_repo_admin_json.py::TestAst1055MeteoriteCatalogRows \
  tests/component/core/test_repo_admin_json.py::TestAst1211EvaluateCraftFixtureLockstep \
  -q
```

**Broken / obsolete revised:** shared-key meteorite Do/Get dispatch pins; catalog 53→55; Meteorite Review six-key exclusivity → eight keys; like/upshot seq 5/6 → 7/8.

**Bible shasum** (`origin/sub/...` tip):
- `docs/test-bible/utils/config.md` `0fdf85c781af4b85f5e7feffcdf019f0a9ade394`
- `docs/test-bible/core/dispatcher.md` `65b6a61d2cb08d0c033e6fd1bb5aa15f1d1f81cc`
- `docs/test-bible/core/repo_admin_json.md` `4958ac2489064aa45f6d6688e4d685a224f7e4da`

— Betty

#### joan — 2026-08-06T08:58:25.356Z
[plan-rubric] revision=1

**Rubric:** plan-rubric.v1
**Ticket:** AST-1222
**Overall:** APPROVED
**Publish-ref tip:** `d768cf82` (`origin/sub/AST-1184/AST-1222-meteorite-do-get-alias-seed-retarget-dispatch`)
**Validated against:** the same composite tree as round 1 — the sub still merges `origin/ftr/AST-1184-…` @ `7a7d90fc`, and the only new commit is the plan patch, so every anchor I checked in round 1 still stands.

**Considered:** 56 active statutes (18 universal + 38 scoped), 9 scoped excluded — unchanged from round 1; the Files Changed table did not move, so the matching set is identical. Scored in-session.

## Traceability

AC1→S1.1–S1.3 (catalog + SQL retarget, shared-key retirement); AC2→S2.2–S2.3; AC3→S2 (now mapped explicitly, with the grouping-key assertion); AC4→S2.3 + AST-1221 resolve. No orphan stages.

## Round 1 items — both cleared

**fix-now → resolved, and the enumeration is complete.** The QA note names all three files and every pinned value I found, with the right dispositions: alias keys at the same triggers for the two `AST-1054` classes, 53→55 on both catalog and fixture, `AST786_EXPECTED_TASK_KEYS` +2, like/upshot 5→7 and 6→8, and `_METEORITE_SEQ` gaining the aliases at 5/6. It also carries forward the two things that do **not** break in `test_dispatcher.py` (row count stays 6, `retired == 0` still expected on the mocked-catalog path), which is exactly the kind of detail that stops Betty from "fixing" something that is already correct.

I went back over the file for classes the note might have missed and found none: `TestAst787AgentRepoJsonSeed`'s `len(rows) == 6` is the `agent.json` persona count, `TestAst1060` pins `qualify_meteorite` at seq 3 (which you keep), and `TestAst878` / the other seq assertions are all Gaze Review rows this plan does not touch. One correction to my own round-1 wording: the affected total is **seven** classes, five of them in `test_repo_admin_json.py` — not eight and six. Your table lists the right classes, so only the count label in the note is off; worth a one-word fix so it does not read as a missing entry on Betty's checklist.

**The eight-key decision is the right call and correctly framed.** Declaring the Meteorite Review expansion as an intentional coverage revision — with the full eight-key list spelled out — turns AST-1219's exclusivity assert from a mystery failure into a contract Betty revises deliberately. That was the part of this ticket most likely to be mishandled at Tests Ready.

**discuss → resolved.** Stage 2 now maps AC2/AC3/AC4 and names the actual mechanism, and the verify block asserts the load-bearing piece: `dispatch_task_grouping_catalog_key` returning the alias unchanged, `get_task_keys()` membership, and the seeded `Meteorite Review` / `"4500"` grouping. I confirmed the new assertions will run — `dispatch_task_grouping_catalog_key` and `get_task_keys` are both public in `config.py`, and `check()` already returns the current-row dict that `cat` now captures. The Done-when picked up the grouping-key clause too, so the AC is gated, not just described.

**nit → resolved.** One `rows_after` snapshot now feeds both the membership test and the delete loop.

## Findings

No `fix-now`. The round-1 `acceptable` items carry forward unchanged and I am not re-litigating them: surgical-not-`cp` is the blessed precedent, the seed shape matches the shipped `gaze_email` pattern (`fetch_culture_pages` is a second `agent_id: "n/a"` precedent I noticed while sweeping the tests), retirement stays gated on both aliases and scoped to the two replaced pairs, the SQL substring assertions are safe, and provision plus startup apply mean no manual operator step.

**Self-assessment:** Now fully honest. `Risk: Medium` explicitly states that the existing component pins fail until Betty revises per the QA note — that is the correct disclosure for a seed ticket that renumbers pinned values, and it is what was missing in round 1. `Conf: high` holds on mechanics I verified.

Good plan. One catalog drives provision, the retirement window is bounded and reasoned, grouping-only rows with empty `run_next` honor the constraint AST-1221 handed you, classic Gaze is untouched, and the coverage consequences are now on the record for Betty instead of waiting to ambush her.

context_tokens≈142000

— Joan

#### katherine — 2026-08-06T08:56:31.506Z
[plan-discuss] round=1 reply

Patched plan @ `d768cf82` on `origin/sub/AST-1184/AST-1222-meteorite-do-get-alias-seed-retarget-dispatch`.

https://github.com/susansomerset/astral/blob/sub/AST-1184/AST-1222-meteorite-do-get-alias-seed-retarget-dispatch/docs/features/meteorite/ast-1222-meteorite-do-get-alias-seed-retarget-dispatch.md

**fix-now:** Added Betty QA note (three files / eight classes) naming the pins Stage 1–2 invalidate — catalog/fixture 53→55, `AST786_EXPECTED_TASK_KEYS` +2, like/upshot seq 5→7 / 6→8, `_METEORITE_SEQ` maps, Meteorite Review exclusivity, AST-1054 shared-key dispatch lookups. Declared eight-key Meteorite Review membership as intentional coverage revision (not accidental leakage). Engineers still do not touch `tests/`.

**discuss:** Stage 2 now maps AC2/AC3/AC4 explicitly; verify asserts `dispatch_task_grouping_catalog_key(alias) == alias`, `get_task_keys()` membership, and seeded Meteorite Review / `"4500"` so Admin grouping cannot silently fall through to the master's Gaze Review.

**nit:** Stage 1 retirement reuses one `rows_after` list for membership + delete.

Status left at Plan Discuss for Joan re-validation.

#### joan — 2026-08-06T08:53:51.431Z
[plan-discuss] round=1 concern
[plan-rubric] revision=1

**Rubric:** plan-rubric.v1
**Ticket:** AST-1222
**Overall:** REVISE
**Publish-ref tip:** `a88fbf63` (`origin/sub/AST-1184/AST-1222-meteorite-do-get-alias-seed-retarget-dispatch`)
**Validated against:** the sub itself — it already merges `origin/ftr/AST-1184-…` @ `7a7d90fc` (`210ad052`), so I read every anchor from the composite tree the build will actually sit on. AST-1221 is at User Testing with its code on `ftr`, so the dependency claim in your header is true, not aspirational.

**Considered:** 56 active statutes (18 universal + 38 scoped), 9 scoped excluded — plan layers `{utils, core, data, docs}`, paths `src/utils/config.py`, `src/core/dispatcher.py`, `data/admin/agent_task.json`, `docs/uat-fixtures/AST-756/expected-agent_task.json`, change_types `{modify, add, delete}`. Scored in-session. Notes: the `data/admin` layer cell is matched as `data` (it is repo seed data, not `src/data/`), and the fixture cell as `docs`.

## Traceability

AC1→S1.1–S1.3 (catalog + SQL retarget, shared-key retirement); AC2→S2.2–S2.3 (grouping rows under Meteorite Review); AC3→S2 only implicitly (see discuss below); AC4→S2.3 + AST-1221 resolve (empty prompts, verified in S2.6). No orphan stages.

## Findings

**fix-now — the plan invalidates ~15 assertions across 8 existing component test classes and says nothing about it.** `orch.pipeline.plan-is-bible`.

The statute's own rationale is that binding the plan keeps Joan validation, **Betty manifests**, and Radia review on one script. This plan hands Betty no script for the largest consequence of its own Done-when. Everything below is a direct, foreseeable result of "count is 55" and "like/upshot seqs become 7/8" — I ran these against the tree rather than guessing:

`tests/component/utils/test_config.py` — `TestAst1054MeteoriteGdlDispatch.test_dispatch_row_specs_and_job_states`: `rows[("grade_do", "METEORITE_PASSED_JD")]` and `rows[("grade_get", "METEORITE_PASSED_DO")]` become `KeyError` the moment Stage 1 lands.

`tests/component/core/test_dispatcher.py` — `TestAst1054MeteoriteDispatchProvision`: `by_key["grade_do"]["score_floor"]` / `by_key["grade_get"]["score_floor"]` break, since those keys are no longer saved. (Worth noting what does *not* break: `added` counts stay at 6 because two aliases replace two shared keys and both are in `TASK_CONFIG`, and `retired == 0` still holds because the mocked catalog never inserts a shared-key meteorite row for your loop to delete. Your retirement code is invisible to that test.)

`tests/component/core/test_repo_admin_json.py` — six classes: `TestAst786…` (`len(rows) == 53` **and** the `AST786_EXPECTED_TASK_KEYS` frozenset, plus `count == 53` after startup apply), `TestAst1211…` (`len(fix) == 53`), `TestAst1055MeteoriteCatalogRows` (`meteorite_like task_seq == 5`, `meteorite_upshot task_seq == 6`), `TestAst1218…` and `TestAst1219…` (each: `len(by) == 53`, `len(fix) == 53`, and a `_METEORITE_SEQ` map pinning like=5 / upshot=6).

One of those is not a bookkeeping bump and deserves its own decision line in the plan: `TestAst1219MeteoriteReviewGroupMembership` asserts `for key, row in by.items(): if key not in _METEORITE_SEQ: assert row.get("task_group_name") != "Meteorite Review"`. That encodes a contract — *only these six keys may live in Meteorite Review*. You are deliberately making it eight. That is a coverage **revision**, not a fix, and it should be Katherine's declared intent in the plan rather than Betty's guess at Tests Ready.

**Recommendation:** add a QA note (the shape AST-1221 used) listing the three files, the eight classes, and the specific pinned values — catalog/fixture count 53→55, `AST786_EXPECTED_TASK_KEYS` +2, `meteorite_like` 5→7, `meteorite_upshot` 6→8, the `_METEORITE_SEQ` maps, the Meteorite Review exclusivity assertion, and the `grade_do` / `grade_get` meteorite-trigger lookups in the two `AST-1054` classes — plus a line that Meteorite Review now legitimately holds eight keys. Keep `astral.git.engineer-test-tree-ban` exactly as you have it: you do **not** touch `tests/`; you hand Betty the list.

**discuss — AC3 is satisfied by machinery the plan never names, so nothing verifies it.** `astral.seed.agent-tables-in-repo-json`.

AC3 ("Admin task-key listings that are config/DB-driven include the new alias keys") has no stage line and no assertion. It does hold — I checked rather than assuming: `/dispatch_tasks/task_keys` iterates `get_task_keys()`, so aliases are already selectable from `TASK_CONFIG`; grouping comes from `_catalog_task_grouping_meta` → `database.get_agent_task(catalog_key)`; and critically `dispatch_task_grouping_catalog_key` special-cases only `prefilter` and returns the alias **unchanged**, so it reads the alias's own row and shows Meteorite Review rather than resolving to the master's Gaze Review. That last one is the entire reason your grouping-only row is the right mechanism, and it is one function away from silently defeating the epic.

**Recommendation:** one Stage 2 verify line asserting `dispatch_task_grouping_catalog_key('meteorite_grade_do') == 'meteorite_grade_do'` and that the seeded row resolves to `Meteorite Review` / `"4500"`, plus a sentence mapping AC3 to Stage 2. Cheap insurance on the AC most likely to go quietly wrong.

**acceptable — surgical-not-`cp` is right, and I confirmed it is the blessed precedent rather than a shortcut.** The older plans that call the fixture "byte-identical" are superseded: AST-1196 established surgical sync, AST-1211 followed it, and the live tests say so out loud ("do not require whole-file catalog↔fixture byte identity"). The two files are already not byte-identical on this tree — `grade_do` `user_prompt` is 134 chars in the catalog vs 324 in the fixture — so a `cp` would smuggle unrelated prompt drift in under this ticket's name. Your "do not reconcile pre-existing drift" instruction and the deliberately weak non-empty assertion on classic prompts are both correct.

**acceptable — the seed shape is precedent-backed and the numbers check out.** Both files currently hold 53 current rows (→55), `meteorite_like`/`meteorite_upshot` are at seq 5/6 as you state, classic `grade_do`/`grade_get` sit in Gaze Review `"4000"` with prompts intact, neither proposed `task_key_uuid` collides with any existing row, the alias keys are absent today, and the field set in your row tables matches the catalog's 17 columns exactly. `agent_id: "n/a"` with empty prompts is not a guess — `gaze_email` already ships that exact shape, which also answers whether an `agent_id` with no row in `agent.json` is tolerated.

**acceptable — retirement placement and the dual-claim reasoning hold.** Re-listing after the insert loop is necessary (the pre-loop `existing` snapshot is stale) and you say why; `database.list_dispatch_tasks_for_candidate` / bare `delete_dispatch_task` / `cid` / `retired` all match the conventions already in that function; 4-space indentation correctly places your block outside `if twin_present:`. The transient window where both the alias and shared-key rows exist is harmless because every meteorite row is `auto_mode=False` (the AST-1098 assert guarantees it), so no scheduler tick can claim either. Nit, not blocking: you call `list_dispatch_tasks_for_candidate` twice — one snapshot reused for both the membership test and the delete loop would be tidier.

**acceptable — the Stage 1 SQL assertions are substring-safe.** I checked the trap: after retargeting, `"'grade_do', 'job',"` is genuinely absent because the SELECT literal reads `'meteorite_grade_do', 'job',` (no quote immediately before `grade_do`), and `task_key = 'meteorite_grade_do'` matches the `WHERE` clause shape exactly. `SEED_CONFIG` has only two keys and the classic Gaze rows are not in the meteorite tuple, so step 2 cannot over-reach.

**acceptable — no operator step is missing.** I went looking for one and found the opposite: `provision_meteorite_dispatch_tasks()` runs from `start_scheduler()`, and `agent_task.json` is applied by `apply_agent_task_repo_json_startup`, so both halves take effect on deploy without a manual provision click.

**Self-assessment:** Scope and Risk are honest — dual-claim really is the failure mode, and empty prompts really are the fork mitigation. `Conf: high` is defensible on the product mechanics, all of which I verified. It is high partly because the plan does not account for the coverage it invalidates, which is the fix-now.

The product substance here is good: one catalog drives provision, retirement is gated on both aliases and scoped to exactly the two pairs being replaced, grouping-only rows with no `run_next` honor the constraint AST-1221 handed you, and classic Gaze is untouched throughout. Add the QA disclosure and the AC3 line and this approves.

context_tokens≈112000

— Joan

#### katherine — 2026-08-06T08:45:39.689Z
Plan published on `origin/sub/AST-1184/AST-1222-meteorite-do-get-alias-seed-retarget-dispatch` @ `a88fbf63`.

https://github.com/susansomerset/astral/blob/sub/AST-1184/AST-1222-meteorite-do-get-alias-seed-retarget-dispatch/docs/features/meteorite/ast-1222-meteorite-do-get-alias-seed-retarget-dispatch.md

**Scope:** Single-Component — retarget `METEORITE_DISPATCH_TASKS` / `SEED_CONFIG`, retire stale shared-key meteorite Do/Get on provision, seed grouping-only `agent_task` + AST-756 fixture under live Meteorite Review.

**Conf:** high — AST-1221 already shipped resolve + alias `TASK_CONFIG`; retirement mirrors AST-1209 twin-before-retire; empty-prompt seed matches gaze_email shape.

**Risk:** Medium — without retirement, dual claim rows (shared key + alias) would mis-route outcomes; empty prompts mitigate fork risk vs master.

---

# AST-1222 — Meteorite Do/Get alias seed + retarget dispatch

**Linear:** [AST-1222](https://linear.app/astralcareermatch/issue/AST-1222/meteorite-doget-alias-seed-retarget-dispatch-task-config-aliases-via)
**Parent:** [AST-1184](https://linear.app/astralcareermatch/issue/AST-1184/task-config-aliases-via-master-task-key) — Task config aliases via master_task_key
**Publish ref:** `origin/sub/AST-1184/AST-1222-meteorite-do-get-alias-seed-retarget-dispatch`

After **AST-1221** (User Testing): retarget meteorite Do/Get dispatch catalog rows from shared `grade_do` / `grade_get` to alias keys `meteorite_grade_do` / `meteorite_grade_get`; retire stale shared-key meteorite trigger rows on provision; seed grouping-only `agent_task` identities under the live **Meteorite Review** section (empty prompts — master's prompts via `resolve_task_key_for_content`); keep AST-756 fixture lockstep. Does **not** invent resolve helpers (**AST-1220** / **AST-1221**), own UI hardcode audit (**AST-1185**), or rename Gaze/Meteorite Review sections (**AST-1183** — already live as Meteorite Review on this tree).

**Depends on AST-1221 (User Testing):** alias `TASK_CONFIG` entries, runtime resolve, overlay deleted. Build expects those on the epic tree via `sync-child` (already merges `origin/dev`; attach `origin/ftr/AST-1184-…` when Chuckles publishes it). If `meteorite_grade_do` / `is_task_alias` are missing at Stage 1 start → stop, comment on parent, wait — do not re-implement the contract.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Retarget `METEORITE_DISPATCH_TASKS` Do/Get `task_key`s; retarget matching `SEED_CONFIG["dispatch_task-meteorite"]` INSERT SQL | utils |
| `src/core/dispatcher.py` | In `ensure_meteorite_dispatch_tasks`, retire `grade_do`@`METEORITE_PASSED_JD` / `grade_get`@`METEORITE_PASSED_DO` once alias rows are present (classic Gaze `PASSED_JD` / `PASSED_DO` untouched) | core |
| `data/admin/agent_task.json` | Add current grouping-only `meteorite_grade_do` / `meteorite_grade_get` rows; bump `meteorite_like` / `meteorite_upshot` `task_seq` | data/admin |
| `docs/uat-fixtures/AST-756/expected-agent_task.json` | Surgical sync of the same new rows + seq bumps — **no** whole-file `cp` | docs |

**No changes expected:** `src/core/agent.py`, `src/core/consult.py`, `TASK_CONFIG` alias literals / resolve helpers, frontend, classic Gaze `agent_task` / Gaze dispatch keys, `tests/` / bible (Betty after Code Complete).

**QA note (Betty after Code Complete):** this ticket deliberately invalidates pinned asserts in existing component tests — engineers do **not** edit `tests/` / bible (`astral.git.engineer-test-tree-ban`). Manifest must revise coverage for:

| File | Classes / asserts to revise |
|------|-----------------------------|
| `tests/component/utils/test_config.py` | `TestAst1054MeteoriteGdlDispatch.test_dispatch_row_specs_and_job_states` — `rows[("grade_do", "METEORITE_PASSED_JD")]` / `rows[("grade_get", "METEORITE_PASSED_DO")]` → alias keys `meteorite_grade_do` / `meteorite_grade_get` at the same triggers |
| `tests/component/core/test_dispatcher.py` | `TestAst1054MeteoriteDispatchProvision` — `by_key["grade_do"]` / `by_key["grade_get"]` score_floor lookups → alias keys (row **count** stays 6; `retired == 0` on the mocked-catalog path is still expected because that fixture never inserts a shared-key meteorite row for the new retire loop) |
| `tests/component/core/test_repo_admin_json.py` | `TestAst786…` — `len(rows) == 53` / `count == 53` after startup apply, and `AST786_EXPECTED_TASK_KEYS` frozenset (+2 alias keys); `TestAst1211…` — `len(fix) == 53` → **55**; `TestAst1055MeteoriteCatalogRows` — `meteorite_like` `task_seq` 5→**7**, `meteorite_upshot` 6→**8**; `TestAst1218…` / `TestAst1219…` — catalog+fixture `len(by) == 53` → **55**, and each `_METEORITE_SEQ` map must add `meteorite_grade_do: 5` / `meteorite_grade_get: 6` and bump like/upshot |

⚠️ **Decision — Meteorite Review membership becomes eight keys (coverage revision, not a fix):** AST-1219's exclusivity assert (`key not in _METEORITE_SEQ` ⇒ not Meteorite Review) encoded a six-key contract. This ticket **intentionally** expands that set to eight (`gaze_email`, `meteorite_email`, `qualify_meteorite`, `evaluate_meteorite`, `meteorite_grade_do`, `meteorite_grade_get`, `meteorite_like`, `meteorite_upshot`). Betty revises `_METEORITE_SEQ` / exclusivity to match Stage 2's table — do not treat the new alias rows as accidental leakage.

## Stage 1: Retarget dispatch catalog + retire stale shared-key rows

**Done when:** `METEORITE_DISPATCH_TASKS` Do/Get entries use `meteorite_grade_do` @ `METEORITE_PASSED_JD` and `meteorite_grade_get` @ `METEORITE_PASSED_DO` (other meteorite rows unchanged); `SEED_CONFIG["dispatch_task-meteorite"]` INSERT pairs match those alias keys; `ensure_meteorite_dispatch_tasks` inserts alias rows and, when both alias pairs are present, deletes only `grade_do`@`METEORITE_PASSED_JD` and `grade_get`@`METEORITE_PASSED_DO` (never `grade_do`@`PASSED_JD` / `grade_get`@`PASSED_DO`); classic Gaze dispatch keys remain untouched; `python3 -m py_compile` on the two files succeeds (repo venv: `~/astral/.venv/bin/python`).

1. In `src/utils/config.py`, in `METEORITE_DISPATCH_TASKS`, change only the two Do/Get entry `task_key` strings:

```python
    {
        "task_key": "meteorite_grade_do",
        "trigger_state": "METEORITE_PASSED_JD",
        "score_floor": 0.0,
        "auto_mode": False,
        "batch_size": 10,
        "min_count": 1,
        "freq_hrs": 0,
    },
    {
        "task_key": "meteorite_grade_get",
        "trigger_state": "METEORITE_PASSED_DO",
        "score_floor": 0.0,
        "auto_mode": False,
        "batch_size": 10,
        "min_count": 1,
        "freq_hrs": 0,
    },
```

Keep `score_floor` / `batch_size` / `auto_mode` / `min_count` / `freq_hrs` and the surrounding qualify / evaluate / like / upshot entries exactly as they are. Update the block comment above `METEORITE_DISPATCH_TASKS` so it no longer implies Do/Get share classic keys — note aliases + **AST-1222**.

2. In the same file, in `SEED_CONFIG["dispatch_task-meteorite"]`, retarget the two INSERT statements that currently seed `'grade_do'` / `'METEORITE_PASSED_JD'` and `'grade_get'` / `'METEORITE_PASSED_DO'`:

- SELECT / WHERE clauses: `'grade_do'` → `'meteorite_grade_do'`, `'grade_get'` → `'meteorite_grade_get'`.
- Leave trigger states, `score_floor` `0.0`, `batch_size` `10`, `batch_call_mode` `1`, `sort_by` `'latest_score'`, and all other meteorite INSERT strings unchanged.

⚠️ **Decision — catalog + SQL lockstep in one stage:** `METEORITE_DISPATCH_TASKS` is the live provision source; `SEED_CONFIG` is the SQL-first register (AST-1108, not executed yet). Both must name the same alias keys so they cannot drift. Do **not** invent a third alias map.

3. In `src/core/dispatcher.py`, after the existing `evaluate_jd`@`METEORITE_*` retirement block inside `ensure_meteorite_dispatch_tasks`, append alias Do/Get retirement. Re-list rows after inserts (the pre-loop `existing` snapshot is stale once new alias rows are saved):

```python
    # AST-1222: once alias Do/Get rows exist, drop shared-key meteorite triggers
    # (classic Gaze grade_do@PASSED_JD / grade_get@PASSED_DO stay).
    rows_after = database.list_dispatch_tasks_for_candidate(cid)
    existing_after = {
        ((r.get("task_key") or "").strip(), (r.get("trigger_state") or "").strip())
        for r in rows_after
    }
    alias_do = ("meteorite_grade_do", "METEORITE_PASSED_JD")
    alias_get = ("meteorite_grade_get", "METEORITE_PASSED_DO")
    if alias_do in existing_after and alias_get in existing_after:
        for row in rows_after:
            tk = (row.get("task_key") or "").strip()
            ts = (row.get("trigger_state") or "").strip()
            if (tk, ts) in {
                ("grade_do", "METEORITE_PASSED_JD"),
                ("grade_get", "METEORITE_PASSED_DO"),
            }:
                delete_dispatch_task(int(row["id"]))
                retired += 1
```

`retired` continues to accumulate with the evaluate_jd count. Update the function docstring to mention AST-1222 alias Do/Get retirement (keep the evaluate_jd / twin language).

⚠️ **Decision — retire only the two meteorite shared-key pairs, gated on both aliases present:** Mirrors AST-1209 twin-before-retire. Leaving orphan `grade_do`@`METEORITE_PASSED_JD` would dual-claim with the alias and still use Gaze `TASK_CONFIG` outcomes (broken after overlay deletion). Do **not** delete `grade_do`@`PASSED_JD` or `grade_get`@`PASSED_DO`. Do **not** rewrite existing row `task_key` in place — delete + insert (idempotent catalog insert already handles the alias side).

⚠️ **Decision — no new hardcoded frozenset of “meteorite shared keys” outside this function:** The retire set is the two literal pairs that this ticket replaces. Catalog authority remains `METEORITE_DISPATCH_TASKS`.

4. Verify:

```bash
~/astral/.venv/bin/python -c "
from src.utils import config as c
by = {(e['task_key'], e['trigger_state']): e for e in c.METEORITE_DISPATCH_TASKS}
assert ('meteorite_grade_do', 'METEORITE_PASSED_JD') in by
assert ('meteorite_grade_get', 'METEORITE_PASSED_DO') in by
assert ('grade_do', 'METEORITE_PASSED_JD') not in by
assert ('grade_get', 'METEORITE_PASSED_DO') not in by
assert ('meteorite_like', 'METEORITE_PASSED_GET') in by
assert ('evaluate_meteorite', 'METEORITE_QUALIFIED') in by
# Classic Gaze still uses shared keys at Gaze triggers (not in METEORITE_DISPATCH_TASKS)
assert c.TASK_CONFIG['grade_do']['pass_state'] == 'PASSED_DO'
assert c.is_task_alias('meteorite_grade_do')
sql = '\n'.join(c.SEED_CONFIG['dispatch_task-meteorite'])
assert \"'meteorite_grade_do', 'job',\" in sql
assert \"'meteorite_grade_get', 'job',\" in sql
assert \"'grade_do', 'job',\" not in sql
assert \"'grade_get', 'job',\" not in sql
assert \"task_key = 'meteorite_grade_do'\" in sql
assert \"task_key = 'meteorite_grade_get'\" in sql
"
~/astral/.venv/bin/python -m py_compile src/utils/config.py src/core/dispatcher.py
```

**Ritual:** `code(AST-1222): retarget meteorite Do/Get dispatch to alias keys`

## Stage 2: Grouping-only alias `agent_task` seed + AST-756 fixture

**AC mapping:** AC2 (alias grouping under Meteorite Review) and AC3 (config/DB-driven Admin task-key listings include the alias keys) are both satisfied by this stage — aliases already appear in `get_task_keys()` via **AST-1220** `TASK_CONFIG`; Stage 2 supplies the alias's own `agent_task` row so Admin grouping (`dispatch_task_grouping_catalog_key` → `_catalog_task_grouping_meta` → `get_agent_task`) reads **Meteorite Review**, not the master's Gaze Review. AC4 (no divergent prompt row) is the empty-prompt seed + **AST-1221** resolve.

**Done when:** `data/admin/agent_task.json` and `docs/uat-fixtures/AST-756/expected-agent_task.json` each have current rows for `meteorite_grade_do` / `meteorite_grade_get` under **Meteorite Review** / `"4500"` with empty prompts and empty `run_next`; `meteorite_like` / `meteorite_upshot` seqs are `7` / `8`; classic Gaze `grade_do` / `grade_get` rows still **Gaze Review** / `"4000"` with prompts intact; current catalog count is **55**; `dispatch_task_grouping_catalog_key` returns the alias key unchanged (so grouping uses the alias row, not the master); JSON keeps `ensure_ascii=False` (literal em-dashes, no `\u2014` re-escape storm).

**Meteorite Review seq after this stage:**

| `task_key` | `task_group_name` | `task_group_order` | `task_seq` |
|------------|-------------------|--------------------|------------|
| `gaze_email` | `Meteorite Review` | `"4500"` | `1` (unchanged) |
| `meteorite_email` | `Meteorite Review` | `"4500"` | `2` (unchanged) |
| `qualify_meteorite` | `Meteorite Review` | `"4500"` | `3` (unchanged) |
| `evaluate_meteorite` | `Meteorite Review` | `"4500"` | `4` (unchanged) |
| `meteorite_grade_do` | `Meteorite Review` | `"4500"` | `5` (**new**) |
| `meteorite_grade_get` | `Meteorite Review` | `"4500"` | `6` (**new**) |
| `meteorite_like` | `Meteorite Review` | `"4500"` | `7` (was `5`) |
| `meteorite_upshot` | `Meteorite Review` | `"4500"` | `8` (was `6`) |

⚠️ **Decision — live section name is Meteorite Review:** Ticket notes said Job Review until AST-1183; on this tree AST-1219 already moved meteorite membership to **Meteorite Review** / `"4500"`. Seed aliases into that live section — do **not** invent Job Review rows.

⚠️ **Decision — renumber like/upshot seq only:** Inserting Do/Get at `5`/`6` mirrors classic Gaze GDL order (evaluate → do → get → like → upshot). Touch only `task_seq` on those two existing rows (no prompt / uuid / agent_id edits).

⚠️ **Decision — grouping-only rows (empty prompts, empty `run_next`, `agent_id` = `n/a`):** Parent AC: alias has no divergent prompt row; runtime loads master via **AST-1221** `resolve_task_key_for_content`. Match `gaze_email`-style non-prompt seed shape so Admin grouping works without a second prompt body. Do **not** copy `grade_do` / `grade_get` prompt text onto the alias.

1. Snapshot before edit (local `/tmp` only — do not commit):

```bash
cp data/admin/agent_task.json /tmp/agent_task.pre-ast-1222.json
cp docs/uat-fixtures/AST-756/expected-agent_task.json /tmp/expected-agent_task.pre-ast-1222.json
```

2. In `data/admin/agent_task.json`, for current `meteorite_like` / `meteorite_upshot` rows only, set `task_seq` to `7` and `8` respectively. Do not change any other field on those rows (prefer leaving `updated_at` untouched).

3. Append two new objects to the array (same field set as other rows). Use these exact identities:

**`meteorite_grade_do`:**

| Field | Value |
|-------|-------|
| `task_key_uuid` | `47e47cc0-26b8-4af6-81d6-f9e080b2b712` |
| `task_key` | `meteorite_grade_do` |
| `task_name` | `meteorite_grade_do` |
| `agent_id` | `n/a` |
| `task_group_name` | `Meteorite Review` |
| `task_group_order` | `"4500"` |
| `task_seq` | `5` |
| `current` | `1` |
| `run_next` | `""` |
| `system_prompt` | `""` |
| `cache_prompt` | `""` |
| `cache_prompt_b` | `""` |
| `cache_prompt_c` | `""` |
| `cache_prompt_d` | `""` |
| `nocache_prompt` | `""` |
| `user_prompt` | `""` |
| `updated_at` | `2026-08-06 08:00:00` |

**`meteorite_grade_get`:**

| Field | Value |
|-------|-------|
| `task_key_uuid` | `357b56de-20a6-4360-a98e-d4527db40b7f` |
| `task_key` | `meteorite_grade_get` |
| `task_name` | `meteorite_grade_get` |
| `agent_id` | `n/a` |
| `task_group_name` | `Meteorite Review` |
| `task_group_order` | `"4500"` |
| `task_seq` | `6` |
| `current` | `1` |
| `run_next` | `""` |
| all prompt fields | `""` |
| `updated_at` | `2026-08-06 08:00:00` |

Do **not** add `master_task_key` to the JSON row (that field lives on `TASK_CONFIG` only). Do **not** edit classic Gaze `grade_do` / `grade_get` rows.

4. Rewrite the file with `json.dump(..., indent=2, ensure_ascii=False)` + trailing newline (same convention as the current seed — literal Unicode in prompts elsewhere). Prefer a surgical Python edit that loads, mutates by `task_key`, and dumps — do **not** hand-edit megabytes of prompts.

5. In `docs/uat-fixtures/AST-756/expected-agent_task.json`, apply the **same** two new rows and the same `task_seq` bumps. Surgical only — **no** `cp` from catalog. Do not reconcile unrelated pre-existing catalog↔fixture prompt drift.

6. Verify:

```bash
~/astral/.venv/bin/python - <<'PY'
import json
from pathlib import Path

CLASSIC_DO_GET = {"grade_do", "grade_get"}
METEORITE_SEQ = {
    "gaze_email": 1,
    "meteorite_email": 2,
    "qualify_meteorite": 3,
    "evaluate_meteorite": 4,
    "meteorite_grade_do": 5,
    "meteorite_grade_get": 6,
    "meteorite_like": 7,
    "meteorite_upshot": 8,
}
ALIAS_UUID = {
    "meteorite_grade_do": "47e47cc0-26b8-4af6-81d6-f9e080b2b712",
    "meteorite_grade_get": "357b56de-20a6-4360-a98e-d4527db40b7f",
}
PROMPT_FIELDS = (
    "system_prompt", "cache_prompt", "cache_prompt_b", "cache_prompt_c",
    "cache_prompt_d", "nocache_prompt", "user_prompt",
)

def check(path: str) -> dict:
    text = Path(path).read_text(encoding="utf-8")
    assert "\\u2014" not in text[:8000] or "—" in text  # prefer literal emdash preserved
    rows = json.loads(text)
    by = {r["task_key"]: r for r in rows if r.get("current") == 1}
    assert len(by) == 55, (path, len(by))
    for k in CLASSIC_DO_GET:
        assert by[k]["task_group_name"] == "Gaze Review", (path, k)
        assert by[k]["task_group_order"] == "4000", (path, k)
        assert (by[k].get("cache_prompt") or "").strip() or (by[k].get("user_prompt") or "").strip(), (
            path, k, "classic prompts must remain non-empty"
        )
    for k, seq in METEORITE_SEQ.items():
        assert k in by, (path, k)
        assert by[k]["task_group_name"] == "Meteorite Review", (path, k, by[k]["task_group_name"])
        assert by[k]["task_group_order"] == "4500", (path, k)
        assert by[k]["task_seq"] == seq, (path, k, by[k]["task_seq"], seq)
    for k, uid in ALIAS_UUID.items():
        r = by[k]
        assert r["task_key_uuid"] == uid, (path, k, r["task_key_uuid"])
        assert r["task_name"] == k
        assert r["agent_id"] == "n/a"
        assert (r.get("run_next") or "") == ""
        for f in PROMPT_FIELDS:
            assert (r.get(f) or "") == "", (path, k, f)
    print("ok", path)
    return by

cat = check("data/admin/agent_task.json")
check("docs/uat-fixtures/AST-756/expected-agent_task.json")
from src.utils import config as c
assert c.resolve_task_key_for_content("meteorite_grade_do") == "grade_do"
assert c.resolve_task_key_for_content("meteorite_grade_get") == "grade_get"
# AC3: grouping catalog key stays the alias (not master) so Admin reads Meteorite Review.
assert c.dispatch_task_grouping_catalog_key("meteorite_grade_do") == "meteorite_grade_do"
assert c.dispatch_task_grouping_catalog_key("meteorite_grade_get") == "meteorite_grade_get"
assert "meteorite_grade_do" in c.get_task_keys()
assert "meteorite_grade_get" in c.get_task_keys()
assert cat["meteorite_grade_do"]["task_group_name"] == "Meteorite Review"
assert cat["meteorite_grade_do"]["task_group_order"] == "4500"
assert cat["meteorite_grade_get"]["task_group_name"] == "Meteorite Review"
assert cat["meteorite_grade_get"]["task_group_order"] == "4500"
print("resolve still master-only; grouping stays on alias: ok")
PY
```

**Ritual:** `code(AST-1222): seed meteorite_grade_do/get agent_task grouping rows`

## Self-Assessment

**Scope:** Single-Component — dispatch catalog + provision retirement + admin seed/fixture grouping; no runtime resolve rewrite.

**Conf:** high — siblings already shipped alias `TASK_CONFIG` + resolve; retarget/retire mirrors AST-1209 `evaluate_jd` pattern; grouping-only seed matches gaze_email empty-prompt shape; live section name is already Meteorite Review on tip; Joan round-1 coverage / AC3 gaps closed in-plan (QA note + grouping verify).

**Risk:** Medium — missing retirement would leave dual meteorite Do/Get claim rows (shared key + alias); wrong seed prompts would fork content from the master (mitigated by empty prompts + resolve). Classic Gaze Do/Get must keep working at `PASSED_JD` / `PASSED_DO`. Existing component pins (53-count / six-key Meteorite Review / shared-key dispatch lookups) fail until Betty revises per the QA note.

## Code rules check

- §1.3 DRY — one catalog (`METEORITE_DISPATCH_TASKS`) drives provision; retire pairs are the two replaced keys only; one `rows_after` list for membership + delete.
- §1.4 / `astral.standards.no-hardcoded-sets` — no new meteorite-only alias map; aliases already in `TASK_CONFIG` via `master_task_key`.
- `astral.seed.agent-tables-in-repo-json` — alias identities land in `data/admin/agent_task.json`; AC3 grouping via alias catalog key (not master resolve).
- `astral.standards.in-scope-only` — no UI audit (**AST-1185**), no section rename (**AST-1183**), no resolve helpers (**AST-1220/1221**).
- `astral.standards.names-not-ticket-ids` — domain keys `meteorite_grade_do` / `meteorite_grade_get`.
- `astral.git.engineer-test-tree-ban` — no `tests/` / bible edits on this ticket; broken pins listed for Betty in the QA note.
- `orch.pipeline.plan-is-bible` — coverage consequences of Done-when are declared for Betty manifests.
- §3.3 imports — dispatcher already imports `METEORITE_DISPATCH_TASKS` / `TASK_CONFIG`; no new reverse imports.

## Revisions

### Revision 1 — 2026-08-06

Driven by: Joan `[plan-discuss] round=1 concern` (plan-rubric.v1 REVISE @ tip `a88fbf63`).

Changes:

- **fix-now:** QA note listing the three test files / eight classes and pinned values that Stage 1–2 invalidate (53→55, `AST786_EXPECTED_TASK_KEYS` +2, like/upshot seq 5→7 / 6→8, `_METEORITE_SEQ` maps, Meteorite Review exclusivity, AST-1054 shared-key lookups); Decision that Meteorite Review membership expanding to eight keys is intentional coverage revision.
- **discuss:** Stage 2 AC mapping (AC2/AC3/AC4); Done-when + verify asserts `dispatch_task_grouping_catalog_key(alias) == alias`, `get_task_keys()` membership, and seeded Meteorite Review / `"4500"` grouping.
- **acceptable (carried):** surgical-not-`cp`; empty-prompt / `n/a` seed shape; retirement gated on both aliases; SQL substring asserts; no manual provision step.
- **nit:** Stage 1 retirement reuses one `rows_after` list for membership + delete loop.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1184/AST-1222-meteorite-do-get-alias-seed-retarget-dispatch`
**Plan path:** `docs/features/meteorite/ast-1222-meteorite-do-get-alias-seed-retarget-dispatch.md`

**Built tip:** `22450fa2c3c79390819694070d2c5d5de8cb497f` (`22450fa2`)

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `320ac917` | retarget meteorite Do/Get dispatch to alias keys |
| 2 | `22450fa2` | seed meteorite_grade_do/get agent_task grouping rows |

## Radia review — [code-rubric] revision=1

**Rubric:** code-rubric.v1 · **Publish ref tip:** `e459d368`

**Overall: CLEAN**

**What's solid:**

- Stage 1 retarget is exact: `METEORITE_DISPATCH_TASKS` Do/Get entries now read `meteorite_grade_do`@`METEORITE_PASSED_JD` / `meteorite_grade_get`@`METEORITE_PASSED_DO`; `SEED_CONFIG["dispatch_task-meteorite"]` SELECT/WHERE literals retarget in lockstep (verified both files' substrings live at tip — no drift between the two seed sources). Classic `grade_do`/`grade_get` `TASK_CONFIG` pass_state stays `PASSED_DO`/untouched.
- Stage 1 retirement in `ensure_meteorite_dispatch_tasks` re-lists rows after the insert loop (stale pre-loop snapshot correctly avoided), gates deletion on **both** alias pairs being present, and deletes only the exact two shared-key pairs — never touches classic Gaze `grade_do`@`PASSED_JD` / `grade_get`@`PASSED_DO`. Matches the AST-1209 twin-before-retire precedent already in the same function.
- Stage 2 seed rows are byte-exact against the plan's field tables in both `data/admin/agent_task.json` and `docs/uat-fixtures/AST-756/expected-agent_task.json` — verified `task_key_uuid`, `Meteorite Review`/`"4500"`, `task_seq` 5/6, `agent_id: "n/a"`, all prompt fields empty, `run_next` empty, and `meteorite_like`/`meteorite_upshot` bumped to 7/8 — identically in both files (true surgical sync, not a `cp`; classic `grade_do`/`grade_get` Gaze Review rows with non-empty prompts left untouched).
- Ran every assertion from the plan's own Stage 1 + Stage 2 verify blocks live against the tip (dispatch catalog membership, SQL substrings, `resolve_task_key_for_content`, `dispatch_task_grouping_catalog_key` returning the alias unchanged, `get_task_keys()` membership, seeded grouping) — all pass.
- JSON convention preserved: literal em-dashes intact, no `\u2014` re-escape storm, trailing newline kept on both files.
- No new hardcoded state/allow-lists: the Stage 1 retirement tuple set is a narrow, function-scoped migration literal (same shape as the pre-existing `evaluate_jd`@`METEORITE_*` retirement two lines above it in the same function), not a parallel meteorite-key catalog — Joan's plan-rubric precedent check on this exact pattern concurred.
- Commit hygiene: `code(AST-1222)` commits touch only `src/utils/config.py`, `src/core/dispatcher.py`, `data/admin/agent_task.json`, `docs/uat-fixtures/AST-756/expected-agent_task.json`; `docs(AST-1222)` touches only the plan doc; `test(AST-1222)`/`merge-tests(AST-1222)` touch only `tests/`/`docs/test-bible/**` — `astral.git.engineer-test-tree-ban` and `astral.git.betty-no-src-or-features` both hold.
- `python3 -m py_compile src/utils/config.py src/core/dispatcher.py src/core/agent.py src/core/consult.py` clean at tip.
- Full active-set sweep (65 active statutes: 18 universal + 41 scoped-applicable against this diff's `{core, utils, docs}` layers / `src/utils/config.py`, `src/core/dispatcher.py`, `data/admin/agent_task.json`, `docs/uat-fixtures/**`, `docs/features/**`, `docs/test-bible/**`, `tests/**` paths) — zero `violates`, zero `needs-discussion`.

**Note:** this three-dot diff also carries AST-1220's and AST-1221's already-reviewed changes (merged onto this branch via `origin/ftr/AST-1184-...` per `orch.git.merge-on-checkout`, since neither sibling has landed `dev` yet). Both were independently reviewed clean (Review Posted); this review's findings focus on AST-1222's own commits.

**Pattern conformance:** `pattern.layers.import-discipline` — conforms (no new imports at all in this ticket's own commits). None else cited beyond the active `astral.*` statutes already covered by the full sweep.

**Plan adherence:** Both stages match the plan's binding tables/code blocks exactly, including the Revision 1 fix-now (QA note enumerating the seven test classes/pins this seed change invalidates, and the intentional eight-key Meteorite Review membership decision) and the Revision 1 discuss item (AC3 grouping-key verify).

## Frame diff

(none — ticket description/AC unchanged; no findings to fold in)

context_tokens≈92000

— Radia

## Resolution — 2026-08-06

**Review tip:** `72c321d5` (`docs(AST-1222): Radia review — clean`) — Overall **CLEAN**.

- **fix-now:** none.
- **Discuss:** none requiring product change.
- **Advisory:** none.
- **Product / plan code:** unchanged this pass (resolve clean).

## Radia re-review — [code-rubric] revision=1 (post-restack)

**Rubric:** code-rubric.v1 · **Publish ref tip:** `cea4222d`

**Overall: CLEAN**

Ticket bounced `Review Posted` → `User Testing` → `Tests Ready` → `Tests Passed` for a `merge-child`-flagged git-history restack (bad `Merge remote-tracking branch` subjects in the `ftr..sub` range) — not a content change. Verified `git diff <prior-tip>..cea4222d -- src/utils/config.py src/core/dispatcher.py data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json` is empty; the only content delta anywhere in the tree is this doc's own review/resolution history carried forward by the rebase. `ftr..sub` range is now clean (no merge-commit subjects), and `origin/ftr/AST-1184-...` == this tip (already fast-forwarded by `merge-child`). `python3 -m py_compile` clean on all touched product modules at tip. Prior CLEAN verdict stands unchanged; no new findings.

## Frame diff

(none — ticket description/AC unchanged; no findings to fold in)

context_tokens≈45000

— Radia

## Resolution — 2026-08-06 (post-restack re-review)

**Review tip:** `bbbe983c` (`docs(AST-1222): Radia review — clean (post-restack re-verify)`) — Overall **CLEAN**.

- **fix-now:** none.
- **Discuss:** none requiring product change.
- **Advisory:** none.
- **Product / plan code:** unchanged this pass (resolve clean after restack re-verify).
