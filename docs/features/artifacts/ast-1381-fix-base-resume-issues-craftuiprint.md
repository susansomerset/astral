# AST-1381 — fix: Base Resume Issues (craft/UI/print)

<!-- linear-archive: AST-1381 archived 2026-08-31 -->

## Linear archive (AST-1381)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1381/fix-base-resume-issues-craftuiprint  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** katherine  
**Priority / estimate:** None / 5  
**Parent:** AST-1362 — Base Resume Issues  
**Blocked by / blocks / related:** parent: AST-1362

### Description

## What this fixes

Orphaned Bug AST-1362 (approved as-is/to-be). Ancestor context: AST-1345 (Done) experience-array epic — related-linked, not re-parented.

1. Craft/experience detail double-bullets → request `string[]` for accomplishments/detail; parse + render once.
2. `|` → `•` on Contact header and Core Competencies resume emit.
3. Collapsible experience roles on Base Resume Content with `<company>, <title> / <from> - <to>` collapsed header.
4. Prior Experience format Save `word_cloud`→`free_prose` must print as free_prose.

## Make-fix checklist

- [X] Schema + prompts: `accomplishments` is `string[]` (config, craft/parse/draft/finalize prompts, AST-756 twin)
- [X] Candidate validate: job accomplishments must be list of strings; Style D lists elements
- [X] Emit: list (or legacy str coerce) → one `<li>` per item; strip residual bullet glyphs
- [X] Resume markers: authoring `|` → emit `•` (contact + competencies + all marker leaves)
- [X] ExperienceJobsEditor: collapsible roles with `{company}, {title} / {dates}` header; accomplishments textarea ↔ `string[]`
- [X] Content Save persists `resume_structure.sections` (formats) with base_resume when structure authoring is on

## Notes for plan-fix

* Parent Description has ## As-is / ## To-be / ## Proposed steps (authoritative for this bug).
* Seed feature docs from AST-1345 family under docs/features/artifacts/ (ast-1349, ast-1351, and related format docs as needed).
* Publish to origin/sub/AST-1362/<this-child-segment> only; parent ftr is AST-1362's own fresh branch off origin/dev.

### Comments

#### betty — 2026-08-15T01:15:36.233Z
`origin/sub/AST-1362/AST-1381-fix-base-resume-issues` @ `5e5b5e7c1b5ba487513db4267688a21ff9578f90` · stripped orphan AST-1383 agent test/bible (ftr restore)

#### katherine — 2026-08-15T01:14:07.586Z
[qa-handoff]
@Betty White — Radia review-fix fix-now on AST-1381 (resolve-child): strip orphan AST-1383 test/bible from this publish ref.

**Why:** tip has `TestAst1380CraftRubricThinkingOffAndFailureBanner` + `docs/test-bible/core/agent.md` AST-1380/1383 section (`test(AST-1383):` / merge-tests ancestry) but **no matching AST-1380 craft-thinking product delta vs `origin/ftr/AST-1362-base-resume-issues`**. The only `src/core/agent.py` tip↔ftr delta is rename `is_rubric_backed_task` → `is_vector_feedback_task` (from synced origin/dev / AST-1378 family), not craft thinking-off.

**Please restore alien paths only** (do not revert AST-1381/AST-1382 product or their repros):

```bash
git checkout origin/ftr/AST-1362-base-resume-issues -- \
  tests/component/core/test_agent.py \
  docs/test-bible/core/agent.md
```

Publish: `origin/sub/AST-1362/AST-1381-fix-base-resume-issues`
Worktree: `/home/susan/astral-AST-1362`

After you land + reassign Katherine, she resumes resolve-child → User Testing.

#### radia — 2026-08-15T01:12:45.856Z
[code-rubric] REVIEW (Commit: a57be15f) product clean; orphan AST-1383 tests

fix-now: strip AST-1383 `test_agent.py` / agent.md additions from this publish ref (no matching agent.py product on tip) — or restore AST-1380 product. Discuss: multi-ticket frame on sub (AST-1382 expected).

#### katherine — 2026-08-15T01:11:15.031Z
`origin/sub/AST-1362/AST-1381-fix-base-resume-issues` @ `3cb8426ee82d9c6e0d78bd27ca43811dd4fe859c` · suites green, Tests Passed

#### betty — 2026-08-15T01:10:28.189Z
`origin/sub/AST-1362/AST-1381-fix-base-resume-issues` @ `a57be15fcf31ec310e5cc2b9c55a97f86ab06204` · AST-1007 markers assert → accomplishments string[] (clean merge-tests; no product src)

#### betty — 2026-08-15T01:09:49.442Z
`origin/sub/AST-1362/AST-1381-fix-base-resume-issues` @ `5be4c135499d236c54226cfee3f9e320c8d047a6` · AST-1007 markers assert → accomplishments string[]

#### katherine — 2026-08-15T01:08:31.367Z
[qa-handoff]
@Betty White — incomplete AST-1382 fixture retarget (not a product bug). Markers deep-walk correctly on list elements; assert still expects a str.

Command (tip `origin/sub/AST-1362/AST-1381-fix-base-resume-issues` @ `7ea7e8ac0f57c5c081da6f4275cc1d9ecb7989ea`):

```
.venv/bin/python -m pytest -q \
  tests/component/core/test_builder.py::TestAst1007NestedTypographyMarkers::test_apply_markers_deep_walks_job_array_and_list_leaves
```

→ red: `job0["accomplishments"]` is `['Achieved sprint\u2011level clarity across delivery.']` (markers applied) but assert compares to a bare str. Fixture `_JOBS` already uses `accomplishments: […]` — flip the assert to the list shape (e.g. `== ["Achieved sprint\u2011level clarity across delivery."]`).

Already green on this tip: prior [qa-handoff] accomplishments:str fixtures, AST-1382 bug-repro + UI retargets, and the rest of the experience touched-area suite (51 passed beside this one).

#### katherine — 2026-08-15T00:55:35.732Z
[qa-handoff]
@Betty White — existing component fixtures assert pre-AST-1381 `accomplishments: str`; product tip is `string[]`. Gap sibling AST-1382 already owns bible/fixture retarget + repro coverage — please land there (or revise these asserts) and reassign me when green.

Commands (epic worktree tip `origin/sub/AST-1362/AST-1381-fix-base-resume-issues` @ `0d8fed5b114768562080768fd1bcf3707c2711aa`):

```
.venv/bin/python -m pytest -q \
  tests/component/core/test_candidate.py::TestAst1349ExperienceArrayContract::test_validate_accepts_five_key_job_array \
  tests/component/utils/test_config.py::TestAst996ExperienceJobArrayConfig::test_craft_resume_base_experience_is_job_array_field
```
→ both fail: validate expects string accomplishments list; config assert expects items_schema accomplishments type str.

```
cd src/ui/frontend && ./node_modules/.bin/vitest run \
  ../../../tests/component/frontend/components/test_ExperienceJobsEditor.test.tsx \
  ../../../tests/component/frontend/components/test_ArtifactEditor.test.tsx \
  --testNamePattern="AST-1351|AST-996"
```
→ 2 failed (e.g. `getByText("Role 1")` — collapsible header is now `{company}, {title} / {dates}`); 2 passed / 22 skipped.

Compile/sanity on product tip: py_compile + tsc clean. 46 other experience/builder pytest nodes green. Not a product revert — fixtures obsolete vs plan-fix to-be / make-fix wire.

#### joan — 2026-08-15T00:50:19.727Z
[board-joan] CANON: OK

Accomplishments string[], `_resume_site_markers` `|`→`•`, collapsible experience chrome, and content-Save persisting `resume_structure` stay inside existing canon (config SoT, seed JSON, UI-config-driven UI, import discipline). No statute/pattern update required. Legacy accomplishments coerce-vs-refuse stays blast-radius scoped, not ESCALATE.

#### betty — 2026-08-15T00:49:56.798Z
[board-betty] TESTS: REVISE
What: docs/test-bible/frontend/components.md (+ core/builder.md, core/candidate.md) — AST-1351/996 fixtures assert accomplishments:str (will break); no repro coverage for string[] single-bullet emit, contact/competencies |→•, or content-Save persisting prior_experience format

#### katherine — 2026-08-15T00:48:51.420Z
`origin/sub/AST-1362/AST-1381-fix-base-resume-issues` @ `c739b652126e9a2a30d0879d175730a587d0af11` · base resume plan-fix

---

_Implementation detail may live in git history on `origin/dev`._
