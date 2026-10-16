# AST-1816 — Gap: cover Slack needed/provided on conversations.list errors (Slack channel list isn't working)

<!-- linear-archive: AST-1816 archived 2026-10-07 -->

## Linear archive (AST-1816)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1816/gap-cover-slack-neededprovided-on-conversationslist-errors-slack  
**Status at archive:** Archive  
**Project:** Astral Contact  
**Assignee:** ada  
**Priority / estimate:** None / 1  
**Parent:** AST-1814 — Slack channel list isn't working  
**Blocked by / blocks / related:** parent: AST-1814

### Description

## What this implements

Test gap from `[board-betty] TESTS: REVISE` on sibling AST-1815: land component coverage (a `[bug-repro]` that is red on the pre-fix tree) for Slack `conversations.list` `ok:false` errors carrying `needed`/`provided`, plus the bible entry. Product change lives only on sibling AST-1815.

## Scope

### Component scope

* `tests/component/external/test_slack.py` — modified: no test feeds `missing_scope` + `needed`/`provided` through `list_bot_channels` or `_iter_conversations`, and none pins the exact plain message when those fields are absent.
* `docs/test-bible/external/slack.md` — modified: no AST-1815 entry for the enriched `conversations.list` error message.

### Technical scope

* `tests/component/external/test_slack.py` — new test cases: mocked `conversations.list` returning `missing_scope` with `needed`/`provided` asserts the error code and both values appear in the raised message, for `list_bot_channels` and `_iter_conversations`; a payload without those fields raises exactly `conversations.list failed: missing_scope`.
* `docs/test-bible/external/slack.md` — new coverage-map entry for AST-1815 naming the new cases.

## Acceptance criteria

1. The new `[bug-repro]` case fails against the pre-fix product tree (`origin/dev` / `ftr` before AST-1815 merges) and passes once AST-1815's `src/external/slack.py` change is on the tip.
2. Existing `TestAst1787ChannelListMembershipFullHistory::test_list_bot_channels_ok_false_raises` and `TestAst1667WorkspacePosterPool::test_hard_failures_raise` stay green.
3. Bible entry present for AST-1815.

## Boundaries

Tests and bible only. Does **not** touch `src/` — the product fix is sibling AST-1815; never cherry-pick or stack AST-1815's product commits onto this sub (it arrives via `ftr` once AST-1815 merges).

## Notes for planning

Gap sibling of AST-1815 under orphaned mini-parent AST-1814. Approved ancestor: AST-1787 (`docs/features/contact/ast-1787-slack-channel-list-membership-full-history.md`).

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at bug-fix dispatch.

### Comments

#### radia — 2026-09-27T03:23:54.296Z
[code-rubric] PROCEED (Commit: 8e27202f) Bug-repro slack scope tests

#### ada — 2026-09-27T03:22:55.322Z
`origin/sub/AST-1814/AST-1816-gap-slack-scope-error-tests` @ `8e27202f` · [bug-repro] red→green confirmed

- Pre-fix (`origin/dev` @ `cd7ca619` + tip tests): manifest 2 failed / 3 passed — both `TestAst1815SlackScopeErrorDetail` bug-repro cases red (`'channels:read' not in 'conversations.list failed: missing_scope'`); AC3 plain pin + both existing regressions green.
- Tip: `TestAst1815SlackScopeErrorDetail` 3/3; full manifest 5/5 (`run_component_tests.sh` with `ASTRAL_PYTHON` = 3.14 venv — harness rejects 3.14 without it).

#### betty — 2026-09-27T03:16:05.267Z
[bug-repro]
`origin/sub/AST-1814/AST-1816-gap-slack-scope-error-tests` @ `e52c39d7` · repro lands red, awaits fix

#### joan — 2026-09-27T03:13:32.216Z
[board-joan]  CANON: OK

#### betty — 2026-09-27T03:13:16.357Z
[board-betty] TESTS: REVISE
What: docs/test-bible/external/slack.md (no AST-1815 block yet) — missing coverage — `TestAst1815SlackScopeErrorDetail` (2× [bug-repro] needed/provided for `list_bot_channels` + `_iter_conversations`, 1× exact-text pin) absent from `tests/component/external/test_slack.py` on the sub tip; test tree is Betty-only, so qa-fix lands it as planned (design checks out: `_iter_conversations` returns a list and raises directly, no gate of its own; existing `match="conversations.list"` tests unaffected; no src/ on this sub).

#### ada — 2026-09-27T03:12:38.857Z
`origin/sub/AST-1814/AST-1816-gap-slack-scope-error-tests` @ `e202bfa8c722fc05e23f3ba0907f33f917045b7f` · scope-error tests + bible

---

_Implementation detail may live in git history on `origin/dev`._
