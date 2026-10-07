# AST-1815 — Surface Slack needed/provided scopes on conversations.list errors (Slack channel list isn't working)

<!-- linear-archive: AST-1815 archived 2026-10-07 -->

## Linear archive (AST-1815)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1815/surface-slack-neededprovided-scopes-on-conversationslist-errors-slack  
**Status at archive:** Archive  
**Project:** Astral Contact  
**Assignee:** ada  
**Priority / estimate:** None / 2  
**Parent:** AST-1814 — Slack channel list isn't working  
**Blocked by / blocks / related:** parent: AST-1814

### Description

## What this implements

When a Slack Web API `conversations.list` call returns `ok:false` (notably `missing_scope`), the raised `RuntimeError` — and therefore the Astral error diagnostic on Manage Candidates — names the scope Slack said it `needed` and the scopes the token `provided`, so a Slack app scope gap is a one-glance fix instead of a guess.

## Scope

### Component scope

* `src/external/slack.py` — modified: `ok:false` raises for `conversations.list` (and ideally all Web API calls going through `_slack_bot_get`) currently drop Slack's `needed`/`provided` scope detail; that detail needs to be in the error message.
* `tests/component/external/test_slack.py` — modified (Betty's tree, flagged here for fix-board): cover the `missing_scope` error message carrying `needed`/`provided`.

### Technical scope

* `src/external/slack.py` — modified function(s): the `ok:false` handling in `list_bot_channels` and `_iter_conversations` (or one new small private helper that formats the Slack error from the payload, reused by those raises) so the `RuntimeError` text includes `needed` and `provided` when present. No behavior change to pagination, `types`, sorting, or the soft-skip set.
* `tests/component/external/test_slack.py` — new test case: mocked `conversations.list` returning `missing_scope` with `needed`/`provided` asserts both appear in the raised message.

## Acceptance criteria

1. `list_bot_channels()` hitting `ok:false, error:missing_scope, needed:<x>, provided:<y>` raises a `RuntimeError` whose message contains the error code, `<x>`, and `<y>`.
2. `_iter_conversations()` gives the same detail on the same payload.
3. Payloads without `needed`/`provided` still raise with the plain error code (no crash, no empty noise).
4. No change to pagination, `types`, sorting, return shapes, or the `_SOFT_SKIP_ERRORS` set.

## Boundaries

Does **not** change Slack app configuration (bot scopes / reinstall — Susan's action from the bug's Proposed steps #1), the admin API in `src/ui/api/api_contact.py`, `src/core/contact.py`, or the Manage Candidates UI.

## Notes for planning

Approved ancestor: AST-1787 (feature doc `docs/features/contact/ast-1787-slack-channel-list-membership-full-history.md`, parent AST-1786 — merged to dev via PR #132). Mini-parent AST-1814.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at bug-fix dispatch.

### Comments

#### radia — 2026-09-27T03:19:30.119Z
[code-rubric] PROCEED (Commit: e0be3c65) Scope detail in errors

#### joan — 2026-09-27T03:10:11.110Z
[board-joan]  CANON: OK

#### betty — 2026-09-27T03:09:34.248Z
Correction to the board-betty verdict above: the poster-pool test is `TestAst1667WorkspacePosterPool::test_hard_failures_raise` (not TestListWorkspacePosters). Verdict unchanged.

#### betty — 2026-09-27T03:09:21.490Z
[board-betty] TESTS: REVISE
What: docs/test-bible/external/slack.md (no AST-1815 entry) — missing coverage — tests/component/external/test_slack.py has no missing_scope needed/provided fixture for list_bot_channels or list_workspace_posters/_iter_conversations, and no exact-equality assert on the no-extras text; existing `match="conversations.list"` asserts (test_list_bot_channels_ok_false_raises, TestListWorkspacePosters::test_hard_failures_raise) stay green, so nothing breaks.

#### ada — 2026-09-27T03:08:26.316Z
`origin/sub/AST-1814/AST-1815-surface-slack-scopes-on-conversations-list-errors` @ `10b3bab8645da1eb3023bf536ca1a7a4c49dc6c4` · needed/provided in errors

---

_Implementation detail may live in git history on `origin/dev`._
