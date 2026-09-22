# AST-1608 — fix: meteorite_email bound messages / Manage Email land error

<!-- linear-archive: AST-1608 archived 2026-09-22 -->

## Linear archive (AST-1608)

**Archived:** 2026-09-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1608/fix-meteorite-email-bound-messages-manage-email-land-error  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** katherine  
**Priority / estimate:** None / 3  
**Parent:** AST-1606 — meteorite_email is not recognizing bound messages  
**Blocked by / blocks / related:** parent: AST-1606

### Description

## What this implements

Fix: meteorite_email not recognizing bound messages; Manage Email Land error with no execution log.

## Scope

### Component scope

* `src/core/inbox.py` — modified: `fetch_candidate_email` (and related list/filter) is what both mailbox and Manage Email use to decide which messages exist for a candidate.
* `src/core/candidate.py` — modified if alias lookup is wrong: `email_aliases_for_candidate` feeds the fetch.
* `src/core/meteorite.py` — modified: `check_inbox` (mailbox runner behind task_key `meteorite_email`) and/or `stage_meteorite` (Manage Email Land entry).
* `src/core/dispatcher.py` — modified only if Avail / `available_count` for the `meteorite_email` mailbox shell is wrong or never computed for this task shape.
* `src/ui/api/api_inbox.py` — modified: Manage Email list + Land endpoints; error payload and any missing failure recording.
* `src/ui/frontend/src/pages/AdminManageEmail.tsx` — modified: how Land errors are shown when the API returns failure without an execution-history row.

### Technical scope

* `src/core/inbox.py` — modified function(s) on the candidate-scoped fetch/filter path so bound messages are not dropped before mailbox or Manage Email can act on them.
* `src/core/candidate.py` — modified function for alias resolution if the candidate's From/To addresses are incomplete or mismatched against the live message.
* `src/core/meteorite.py` — modified `check_inbox` and/or `stage_meteorite` so empty-fetch vs classify/land failure is distinguishable and Land failures carry a usable error string.
* `src/core/dispatcher.py` — modified Avail/eligibility path for `meteorite_email` only if the shell still reports zero when fetch would return messages (or if Click is blocked by a stale count).
* `src/ui/api/api_inbox.py` — modified Land handler to return and optionally persist a clear error when `stage_meteorite` fails, instead of a bare UI "error" with no ledger trail.
* `src/ui/frontend/src/pages/AdminManageEmail.tsx` — modified Land error handling to surface the API error (and/or deep-link to whatever log row exists).

## Boundaries

Does not reopen AST-1555 epic children. Orphaned mini-parent is AST-1606.

## Proposed change

- [X] A1 — `_filter_messages_by_aliases` / alias-set helper on already-fetched inbox list
- [X] A2 — `count_inbox_messages_bound_to_candidate` live via aliases → fetch/filter
- [X] A3 — `count_inbox_bound_by_candidate` one inbox list + mailbox-task candidate ids
- [X] A4 — Avail helper docstrings describe live alias eligibility
- [X] A5 — no dispatcher/api_admin Avail rewrite (callers unchanged)
- [X] B1 — `ingest_candidate_email_message` extracted from check_inbox per-message path
- [X] B2 — `check_inbox` loops ingest helper; same summary counters + last_email_check stamp
- [X] B3 — `inbox_land_meteorite` uses ingest (not classify-only `stage_meteorite`); error on results
- [X] B4 — AdminManageEmail shows `row.error`; toast error when failed/errors > 0
- [X] C — [candidate.py](<http://candidate.py>) untouched; no dispatcher ledger for Land; no meteorite_email.py delete

### Comments

#### radia — 2026-09-09T22:42:51.834Z
[code-rubric] REVIEW (Commit: 8ea85dd7) Avail+Land ingress — discuss only, no fix-now

Overall DISCUSS/REVIEW: plan-faithful Avail live counts + Land→ingest. No fix-now product defects. Discuss: per-candidate Avail may re-list Gmail; Land pre-check outcome strings changed for check_inbox parity; `test(AST-1608)` commit was product scoring fallback. Sibling AST-1611 holds [bug-repro].

#### betty — 2026-09-09T22:36:36.590Z
[check-linear]
Cleared [qa-handoff]: Land bug-repro setup fixed on `origin/sub/AST-1606/AST-1611-gap-tests-avail-land` @ `144e0ca5` (ingest-only mocks; dropped get_html/strip). Avail repro already green. Retry test-fix vs product tip `8ea85dd7`.

#### katherine — 2026-09-09T22:33:24.460Z
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

#### joan — 2026-09-09T22:23:05.475Z
[board-joan]  CANON: OK

#### betty — 2026-09-09T22:22:50.045Z
[board-betty] TESTS: REVISE
What: docs/test-bible/ui/api/api_inbox.md § AST-1558 + docs/test-bible/core/inbox.md § AST-1558 — TestAst1558InboxLandMeteoriteApi (Land→stage_meteorite) and TestAst1558CandidateInboxVerbs (count stubs {}/0) break under Proposed A/B; repro live Avail/ingest Land uncovered.

#### katherine — 2026-09-09T22:21:28.569Z
`origin/sub/AST-1606/AST-1608-fix-meteorite-email-bound-messages` @ `a260be05444775cb6ccff2ec25ae0629f0345b79` · Avail stubs + Land ingress

@chuckles Land half is AST-1558 surface (`api_inbox` / `AdminManageEmail`); full bug plan lives on `docs/features/meteorite/ast-1559-check-inbox-monitoring-log.md` per intake preference — add a pointer on `ast-1558-*.md` if you want cross-link, no new plan doc.

---

_Implementation detail may live in git history on `origin/dev`._
