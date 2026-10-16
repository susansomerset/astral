# AST-2088 — Upshot response should set a readable company_name

<!-- linear-archive: AST-2088 archived 2026-10-16 -->

## Linear archive (AST-2088)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2088/upshot-response-should-set-a-readable-company-name  
**Status at archive:** Archive  
**Project:** Astral Roster  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-2054 — Company Upshot - new task  
**Blocked by / blocks / related:** parent: AST-2054

### Description

## Susan's comment (verbatim)

\[fix\]

Please add to the upshot response schema to revise the company_name field (not the short_name id) with a proper, readable company name, instead of whatever was parsed by the scrapes.

## As-is / To-be

* **As-is:** after the `UPSHOT_READY` hop, `company.company_name` is still whatever the scrape or import parsed. That's often an unreadable or raw string, and Estelle's `company_upshot` response has no field to correct it.
* **To-be:** the `company_upshot` response schema also returns a proper, readable company name for each `company_id`. The upshot batch saves it to the company's `company_name` field. `short_name` (the id) is never changed.

## Suggested engineer

Hedy (AST-2070 owns the `UPSHOT_READY` Estelle batch in `src/core/roster.py`). The schema and prompt rows are AST-2069's area (Ada), in `src/utils/config.py` `TASK_CONFIG["company_upshot"]` and the `data/admin/agent_task.json` `company_upshot` row.

### Comments

#### chuckles — 2026-10-09T02:17:32.060Z
[merge-child] merged to `ftr/AST-2054-company-upshot` by hand (fast-forward to `9d7fe125c`). validate-sub-log flagged two `merge-tests(AST-2088)` commits. The second one restored AST-2085 test/bible lines that the first had reverted, and the net test tree matches `origin/tests`. Collapsing them would need a force-push, which orientation forbids.

#### radia — 2026-10-09T02:16:39.667Z
[code-rubric] PROCEED (Commit: c5de90bba272b0a81de9a3ac67cc8694c1c9671d) readable company_name fix

#### betty — 2026-10-09T02:11:30.664Z
[bug-repro]
`origin/sub/AST-2054/AST-2088-upshot-readable-company-name` @ `e6d98b862` · repro lands red, awaits fix

Manifest + repro nodes: docs/test-bible/core/roster.md § AST-2088. Note: two merge-tests on this ref — the second (6af7b33ad) restores AST-2085 test/bible hunks that origin/tests lacked and the first merge reverted.

#### joan — 2026-10-09T02:07:30.355Z
[board-joan]  CANON: OK

#### betty — 2026-10-09T02:07:03.643Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/roster.md (TestAst2070CompanyUpshotBatch) + docs/test-bible/utils/config.md (TestAst2069UpshotRegistration) — missing coverage — no node asserts that company_upshot_batch writes a stripped response company_name via update_company (and skips it when blank/missing while still moving to WATCH), or that the company_upshot items_schema/prompt carries optional company_name; no existing test breaks (live_content asserts are substring/count only).

#### hedy — 2026-10-09T02:06:08.039Z
`origin/sub/AST-2054/AST-2088-upshot-readable-company-name` @ `cc41fa509` · upshot sets readable name

---

_Implementation detail may live in git history on `origin/dev`._
