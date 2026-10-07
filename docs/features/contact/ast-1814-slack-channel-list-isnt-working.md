# AST-1814 — Slack channel list isn't working

<!-- linear-archive: AST-1814 archived 2026-10-07 -->

## Linear archive (AST-1814)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1814/slack-channel-list-isnt-working  
**Status at archive:** Archive  
**Project:** Astral Contact  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## As-is

Manage Candidates (`/admin/manage_candidates`) loads the Slack channel picker via `list_bot_channels()` in `src/external/slack.py`, which calls `conversations.list` with `types=public_channel,private_channel`. Slack answers `ok:false, error:missing_scope` and the helper raises `RuntimeError("conversations.list failed: missing_scope")`, so the picker fails. Slack's response also carries `needed` / `provided` scope fields, but the helper throws them away — so the diagnostic can't say *which* scope is missing. Susan added `groups:history` (and `groups:read` is listed), yet it still fails.

Likely causes (not code-verifiable from here, Susan to confirm in the Slack app config):

1. `channels:read` (public-channel half of the `types` filter) is not on the **Bot Token Scopes** — Slack fails the whole call if any requested type lacks its scope.
2. The scopes were added under **User Token Scopes** instead of **Bot Token Scopes** (Astral uses the bot token, `CONTACT_CONFIG["bot_token_env"]`).
3. The app wasn't **reinstalled** to the workspace after adding scopes, so the deployed `xoxb-` token still carries the old scope set (new scopes only land on a reinstall-issued token; the env var may also need the refreshed token).

## To-be

The channel picker lists the bot-visible public and private channels. When Slack rejects a call with `missing_scope`, the raised error (and the Astral error diagnostic) names the scope Slack said it `needed` and the scopes the token `provided`, so a scope gap is a one-glance fix instead of a guess.

## Proposed steps

1. Susan: in the Slack app → OAuth & Permissions, confirm **Bot Token Scopes** include `channels:read` and `groups:read` (plus `groups:history` / `channels:history` for full history), reinstall the app, and update the bot token env var if Slack issued a new one. Retry the picker — this alone probably resolves the symptom.
2. Code: when a Slack Web API call returns `ok:false`, include the `needed` and `provided` fields in the raised `RuntimeError` message (at least for `conversations.list` in `list_bot_channels` and `_iter_conversations`; ideally once in a shared helper so every `ok:false` raise gets it).
3. Add/adjust the component test for `list_bot_channels` so a `missing_scope` payload with `needed`/`provided` produces an error message containing both.

## Component scope

* `src/external/slack.py` — modified: `ok:false` raises for `conversations.list` (and ideally all Web API calls going through `_slack_bot_get`) currently drop Slack's `needed`/`provided` scope detail; that detail needs to be in the error message.
* `tests/component/external/test_slack.py` — modified (Betty's tree, flagged here for fix-board): cover the `missing_scope` error message carrying `needed`/`provided`.

## Technical scope

* `src/external/slack.py` — modified function(s): the `ok:false` handling in `list_bot_channels` and `_iter_conversations` (or one new small private helper that formats the Slack error from the payload, reused by those raises) so the `RuntimeError` text includes `needed` and `provided` when present. No behavior change to pagination, `types`, sorting, or the soft-skip set.
* `tests/component/external/test_slack.py` — new test case: mocked `conversations.list` returning `missing_scope` with `needed`/`provided` asserts both appear in the raised message.

## Ancestor candidates

- [X] AST-1787 — Slack channel list / membership / full history (external): shipped `list_bot_channels()`, the exact failing call (`docs/features/contact/ast-1787-slack-channel-list-membership-full-history.md`, parent AST-1786)
- [ ] AST-1788 — Contact admin channel APIs + shapes: the admin GET that calls `list_bot_channels()` for Manage Candidates (`docs/features/contact/ast-1788-contact-admin-channel-apis-shapes.md`)
- [ ] AST-1667 — Workspace poster pool (external): `_iter_conversations`, the sibling `conversations.list` loop with the same error-drop (`docs/features/contact/ast-1667-workspace-poster-pool-external.md`)

## Original report

```
Astral error diagnostic
timestamp: 2026-09-27T01:13:10.877Z
message: conversations.list failed: missing_scope
route: /admin/manage_candidates
astral_candidate_id: abrams
```

I just added groups:history scope for the auth scope, but the job to fetch the private channel list is failing.

```
Yes

groups:history
View messages and other content in private channels that "Estelle" has been added to
Yes

groups:read
View basic information about private channels that "Estelle" has been added to
```

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
