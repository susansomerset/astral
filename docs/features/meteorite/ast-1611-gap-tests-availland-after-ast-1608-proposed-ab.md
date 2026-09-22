# AST-1611 — gap: tests Avail/Land after AST-1608 Proposed A/B

<!-- linear-archive: AST-1611 archived 2026-09-22 -->

## Linear archive (AST-1611)

**Archived:** 2026-09-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1611/gap-tests-availland-after-ast-1608-proposed-ab  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** katherine  
**Priority / estimate:** None / 2  
**Parent:** AST-1606 — meteorite_email is not recognizing bound messages  
**Blocked by / blocks / related:** parent: AST-1606

### Description

## What this implements

Test gap from [board-betty] TESTS: REVISE on AST-1608 — land/revise coverage so AST-1558 Land→stage_meteorite and Avail count stubs do not break under the AST-1608 Proposed A/B fix; add repro for live Avail/ingest Land.

## Scope

### Component scope

* `docs/test-bible/ui/api/api_inbox.md` — modified: AST-1558 Land/Avail expectations under Proposed A/B.
* `docs/test-bible/core/inbox.md` — modified: AST-1558 candidate inbox verb / count stub expectations.
* `tests/` (paths named by bible for TestAst1558InboxLandMeteoriteApi and TestAst1558CandidateInboxVerbs) — modified/new: stop asserting Land→classify-only stage_meteorite and `{}`/`0` Avail stubs; cover live alias-filtered Avail and ingest Land path.

### Technical scope

* Bible sections for AST-1558 api_inbox + inbox — revise documented contracts to match AST-1608 Proposed change A (live Avail counts) and B (Land → ingest/classify→insert_meteorite_rows→archive).
* TestAst1558InboxLandMeteoriteApi — modified assertions / setup so Land path matches ingest, not classify-only stage_meteorite.
* TestAst1558CandidateInboxVerbs — modified so count stubs `{}`/`0` are replaced by expectations for live alias-filtered counts (or removed if stubs retire).
* Add or extend a repro-first case for live Avail + ingest Land if no existing node covers it.

## Boundaries

Product code for the fix stays on AST-1608. This gap is test/bible only (Betty).

### Comments

#### chuckles — 2026-09-09T22:45:13.585Z
Tests absorbed onto AST-1608 via merge-tests(AST-1608) of this gap tip. Gap stays User Testing for rollup; product+tests land together on ftr via AST-1608 merge-child.

#### radia — 2026-09-09T22:44:09.582Z
[code-rubric] PROCEED (Commit: 144e0ca5) bug-repro+bible clean

Gap AST-1611 CLEAN: live Avail + Land ingest [bug-repro] assert the right To-be; bible honest. No fix-now. Land both siblings on the same ftr/dev line.

#### betty — 2026-09-09T22:36:37.595Z
Land [bug-repro] setup fixed @ `144e0ca5` — ingest-only mocks. AST-1608 returned to Katherine for test-fix retry.

#### katherine — 2026-09-09T22:33:23.437Z
[qa-handoff]
AST-1608 test-fix blocked on gap AST-1611 test setup — not product.

Command:
```
.venv/bin/python -m pytest \
  tests/component/ui/api/test_api_inbox.py::TestAst1558InboxLandMeteoriteApi::test_land_meteorite_happy_path \
  tests/component/core/test_inbox.py::TestAst1558CandidateInboxVerbs::test_count_inbox_messages_bound_live_alias_match \
  -q --tb=short
```

Result: Avail [bug-repro] **green**. Land [bug-repro] **red** with:
`AttributeError: <module 'ui.api.api_inbox'> has no attribute 'get_message_html'`
at `test_land_meteorite_happy_path` line ~177 (`monkeypatch.setattr(inbox_mod, "get_message_html", ...)` without `raising=False`).

Why test/manifest: post–AST-1608 Land no longer imports `get_message_html` / `strip_extract_email_html` on `api_inbox` (Proposed B → `ingest_candidate_email_message` only). Dual-mock patches for the pre-fix `stage_meteorite` path break setup before the ingest assertion runs. Same pattern in `test_land_meteorite_passes_debug` and `test_land_meteorite_upstream_502`.

Please: drop those `inbox_mod.get_message_html` / `strip_extract_email_html` setattr lines (or `raising=False`) once ingest is the Land entry; keep `ingest_candidate_email_message` mock + `stage.assert_not_awaited()`. Product tip includes public-shape pass counting so landable+`job_count` without `counter` still counts passed: `origin/sub/AST-1606/AST-1608-fix-meteorite-email-bound-messages` @ `8ea85dd777e13836f7a168019a50f51516775995`.

@Betty White

#### betty — 2026-09-09T22:30:47.068Z
[bug-repro]
`origin/sub/AST-1606/AST-1611-gap-tests-avail-land` @ `7e4ddcdb` · repro lands red, awaits fix

---

_Implementation detail may live in git history on `origin/dev`._
