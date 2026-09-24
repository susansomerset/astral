# AST-1683 — Cover Contact-shaped BASE_RESUME current-read (test gap for AST-1682)

<!-- linear-archive: AST-1683 archived 2026-09-24 -->

## Linear archive (AST-1683)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1683/cover-contact-shaped-base-resume-current-read-test-gap-for-ast-1682  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** hedy  
**Priority / estimate:** None / 2  
**Parent:** AST-1681 — {$BASE_RESUME} does not read current base_resume artifact  
**Blocked by / blocks / related:** parent: AST-1681

### Description

## What this implements

Land bible + test coverage for Contact-shaped `do_task(index=cid, ctx=None)` / library blob without `_astral_candidate_id` so `{$BASE_RESUME}` current-read after the AST-1682 cid-threading fix is exercised (Betty board REVISE on AST-1682).

## Citations

Copied from sibling AST-1682 `[board-betty] TESTS: REVISE`:
What: docs/test-bible/core/agent.md — missing coverage — Contact-shaped do_task(index=cid, ctx=None) / library blob without \_astral_candidate_id → {$BASE_RESUME} current-read not exercised (AST-1587/607/1192 only cover pre-stamped cid or name tokens)

## Scope

### Component scope

* `docs/test-bible/core/agent.md` — modified: add coverage note for Contact-shaped do_task / BASE_RESUME current-read after cid threading.
* astral-tests component tests under agent/token resolve (Betty-owned) — new or extended case for index=cid, ctx=None → non-empty `{$BASE_RESUME}` when operative current exists.

### Technical scope

* Bible row / scenario describing the Contact-shaped resolve path.
* New or revised test asserting `{$BASE_RESUME}` resolves via current-read when cid is only on the do_task index (no pre-stamped `_astral_candidate_id` on the blob).

## Acceptance criteria

1. A test fails against pre-fix product (or pre-cid-threading) and passes once AST-1682’s cid threading lands — tagged `[bug-repro]` if qa-fix lands it.
2. Bible `docs/test-bible/core/agent.md` names the Contact-shaped BASE_RESUME path Betty flagged.

## Boundaries

Does not implement the product cid-threading fix (sibling AST-1682 / make-fix). Does not change canon.

## Notes for planning

Test-gap sibling for AST-1682 board REVISE. Assignee Betty.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1681-base-resume-does-not-read-current-artifact`, child `sub/AST-1681/AST-1683-cover-contact-base-resume-current-read`. Created at bug-fix gap dispatch.

## QA test manifest

1. Bug-repro (red pre AST-1682 cid threading; green after): `tests/component/core/test_agent.py::TestAst1683ContactBaseResumeCurrentRead::test_do_task_index_cid_ctx_none_resolves_base_resume`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst1683ContactBaseResumeCurrentRead::test_do_task_index_cid_ctx_none_resolves_base_resume \
  -q
```

**Pass criterion:** pytest green on the repro node once AST-1682 make-fix lands.

**Publish:** `origin/sub/AST-1681/AST-1683-cover-contact-base-resume-current-read` @ `af453c56` (`merge-tests(AST-1683): origin/tests eec6f443…`).

**Bible shasum (publish tip):**

* `docs/test-bible/core/agent.md` — `4a829085a25a8c8de288e947ab05995500ba8b60`

### Comments

#### betty — 2026-09-16T19:36:15.937Z
[bug-repro]
`origin/sub/AST-1681/AST-1683-cover-contact-base-resume-current-read` @ `af453c56` · repro lands red, awaits fix

#### chuckles — 2026-09-16T19:28:55.582Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/agent.md — missing coverage — Contact-shaped do_task(index=cid, ctx=None) / library blob without _astral_candidate_id → {$BASE_RESUME} current-read not exercised (AST-1587/607/1192 only cover pre-stamped cid or name tokens)
Copied from sibling AST-1682 board; this gap child is the test-hole slice.

---

_Implementation detail may live in git history on `origin/dev`._
