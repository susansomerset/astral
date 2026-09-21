# AST-1521 — meteorite_email land_meteorite routing (Emailed job description parsed as HTML)

<!-- linear-archive: AST-1521 archived 2026-09-09 -->

## Linear archive (AST-1521)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1521/meteorite-email-land-meteorite-routing-emailed-job-description-parsed  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** katherine  
**Priority / estimate:** None / 5  
**Parent:** AST-1520 — Emailed job description parsed as HTML  
**Blocked by / blocks / related:** parent: AST-1520

### Description

## What this implements

Complete AST-1472's deferred retarget for `src/core/meteorite_email.py`: bound mailbox mail follows Susan's decision tree using `land_meteorite` for JD-text ingress, Playwright scrape branches, archive-on-success / error-stays-inbox. Parent bug AST-1520.

## Scope

### Component scope

* `src/core/meteorite_email.py` — complete AST-1472's deferred retarget: replace `_handle_bound` routing with Susan's tree + `land_meteorite`; keep unbound Trash / `last_email_check` stamp owned here (not in inbox `fetch_email`).
* `src/core/meteorite.py` — read-only expected (`land_meteorite` already public from AST-1470); call it, do not fork enrich.
* `src/core/inbox.py` — read-only preferred; optional shared land helper extraction only if plan-fix proves DRY without widening AST-1472 footprint.
* `src/utils/config.py` — modify only if routing literals belong in `METEORITE_EMAIL_*_CONFIG`.
* Component tests under `tests/component/core/` — Betty owns; meteorite_email land + archive regressions (AST-1472 test patterns in `test_inbox.py` are reference, not edit target unless shared helper moves).

### Technical scope

* `src/core/meteorite_email.py` — **major modified **`_handle_bound`: Susan's bind → subject → URL → links → scrape → `land_meteorite` / BOT_BLOCKED progression; **modified **`_finalize_archive`: land success → archive, error → inbox + fail (no pass-without-ingest). **Modified **`run_meteorite_email`: unchanged list/bind/filter; outcomes driven by new `_handle_bound` returns.
* `src/core/meteorite.py` — **no change expected**; consume existing `land_meteorite(text=, job_link=, scraps=)`.
* `src/utils/config.py` — **optional config keys** for shape-detection thresholds if statute requires.
* Component tests — **new cases** in meteorite_email suite: no-subject JD text, URL+body, scrape-fail BOT_BLOCKED, multi-link inspector paste.

## Proposed change

- [X] Helpers: `_land_outcome_token`, `_land_jd`, `_scrape_land_or_bot_blocked`, `_create_bot_blocked_job`, `_body_looks_like_inspector_html`, `_body_http_links`; late-import `land_meteorite` / `ensure_meteorite_company`; drop Ruth-first ingest path
- [X] Config: `inspector_structural_tags` + `inspector_min_structural_tags` on `METEORITE_EMAIL_INGEST_CONFIG`
- [X] Rewrite `_handle_bound` to Susan's subject/URL/body/inspector tree → `land_meteorite` / BOT_BLOCKED
- [X] `_finalize_archive`: empty outcomes → error (no pass-without-ingest); created/all-skip → archive
- [X] `run_meteorite_email` / selected-ids / process helpers unchanged for list/bind/filter/unbound Trash / `last_email_check`
- [X] AST-1522 `[bug-repro]` `TestAst1522NoSubjectJdLandsAndArchives::test_no_subject_jd_text_lands_and_archives` green against this tip

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1520-emailed-job-description-parsed-as-html`, child `sub/AST-1520/AST-1521-meteorite-email-land-routing`.

### Comments

#### radia — 2026-08-27T03:22:33.681Z
[code-rubric] PROCEED (Commit: 224b882b) land_meteorite routing clean

Overall CLEAN. fix-now/discuss none. [bug-repro] OK on sibling AST-1522. What must still hold OK. Advisory: drop unused do_task import after AST-1522 stops monkeypatching; unused jd_suffix param; local _body_text vs gazer helper acceptable.

Next: Review Posted → User Testing (§3h clean shortcut).

#### katherine — 2026-08-27T03:18:31.480Z
`origin/sub/AST-1520/AST-1521-meteorite-email-land-routing` @ `224b882b49552250d0a4c8ece7c6ce609aaff9ad`

[bug-repro] `TestAst1522NoSubjectJdLandsAndArchives::test_no_subject_jd_text_lands_and_archives` red→green: failed pre-fix (`land.assert_awaited` / ignored-empty @ 525fbd09); passed post-fix tip. Manifest run command green.

#### joan — 2026-08-27T03:02:52.211Z
[board-joan] CANON: OK

#### betty — 2026-08-27T03:01:28.192Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/meteorite_email.md — missing coverage + broken tests — no-subject JD→land+archive uncovered; Ruth html_links/subject_body/_ingest_link/ignored-empty expectations break

#### katherine — 2026-08-27T03:00:04.070Z
`origin/sub/AST-1520/AST-1521-meteorite-email-land-routing` @ `525fbd09086577ef437c791efffb4dded715978c` · land_meteorite routing plan

---

_Implementation detail may live in git history on `origin/dev`._
