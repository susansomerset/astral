# AST-2085 — remove the prefix to Contact Estelle for production responses

<!-- linear-archive: AST-2085 archived 2026-10-16 -->

## Linear archive (AST-2085)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2085/remove-the-prefix-to-contact-estelle-for-production-responses  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Execution plan

**Root cause:** `format_contact_reply_text` (`src/core/contact.py`) prepends `[<ASTRAL_DEPLOY_ENV>] ` unless `contact_is_production_deploy()` is true, and that check compares the env to the literal `"production"`. Production's `ASTRAL_DEPLOY_ENV` is `✅` (same label in AUTO alert subjects, e.g. `[✅/Johnson] …`), so prod never matches and every Estelle reply gets `[✅] `.

Per the brief — deactivate the prefix code (all environments), not re-key the production check:

1. `src/core/contact.py` — `format_contact_reply_text` returns the body unchanged (keep the function so the \~7 call sites and `post_contact_reply` are untouched); delete `non_production_reply_prefix`.
2. `src/utils/config.py` — drop `CONTACT_CONFIG["non_production_reply_prefix_template"]` and fix the `production_deploy_env` comment (it no longer gates a prefix).
3. `src/ui/frontend/src/pages/AdminManageSlack.tsx` — remove the "Production — not prefixed / Non-production — prefixed with \[…\]" paragraph (no longer true anywhere).
4. Tests + bible: drop `test_non_production_reply_prefix` and the template assert in `test_config.py`; add one `format_contact_reply_text` passthrough assert (non-prod env → body unchanged); refresh `docs/test-bible/core/contact.md` AST-1067 prefix lines.
5. Compile + lint (`ruff`, frontend `tsc`/lint), run `tests/component/core/test_contact.py`, `tests/component/utils/test_config.py`, `tests/component/ui/api/test_api_contact.py`; commit + push on `dev`.

Not taken: setting `production_deploy_env` to `✅` (config-only, keeps a `[staging]` prefix) — the brief says deactivate.

## Done when

* Production @Estelle replies post exactly the reply text (no `[✅] `).
* No code path adds an environment prefix to Contact Slack replies.
* Manage Slack no longer claims replies are prefixed.
* Compile, lint, and the touched component suites are green.

## Risks / open questions

* none

---

## Original brief

Current response: 
\[✅\] Sure — send me the posting. A link is ideal; otherwise, company, title, and any description you have. I’ll get it tracked for you.
Desired response:
Sure — send me the posting. A link is ideal; otherwise, company, title, and any description you have. I’ll get it tracked for you.

Deactivate the code that adds the prefix in the current codebase.

### Comments

#### susan — 2026-10-09T01:15:57.507Z
Yes, Okay to commit --no-verify

#### chuckles — 2026-10-09T01:05:18.234Z
@susan blocked at commit — implementation is done and staged on `$ASTRAL_MAIN` (`dev`), not pushed.

The engineer pre-commit hook on `astral` rejects `tests/*` and `docs/test-bible/*`, and this change has to touch both: `test_config.py` asserted the deleted `non_production_reply_prefix_template`, and the hear-ack test in `test_contact.py` asserted the `[staging] ` prefix. Pushing product code alone would turn those two red on `dev`.

Staged: `src/core/contact.py` (`format_contact_reply_text` → passthrough, `non_production_reply_prefix` deleted), `src/utils/config.py` (template key removed), `AdminManageSlack.tsx` (prefix copy removed), the two test edits, and three bible lines. Compile and lint are clean (no new ruff findings vs `HEAD`; `tsc`/eslint clean). The touched suites show 101 failures that are identical on clean `HEAD` — pre-existing, not from this change; both edited tests pass.

1. OK to commit with `--no-verify` (Task solo path), or should the test and bible edits go through Betty on `astral-tests`?

---

_Implementation detail may live in git history on `origin/dev`._
