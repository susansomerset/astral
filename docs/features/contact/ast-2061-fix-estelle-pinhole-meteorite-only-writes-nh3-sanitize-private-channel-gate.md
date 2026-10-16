# AST-2061 — fix: Estelle pinhole — meteorite-only writes, nh3 sanitize, private-channel gate

<!-- linear-archive: AST-2061 archived 2026-10-16 -->

## Linear archive (AST-2061)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2061/fix-estelle-pinhole-meteorite-only-writes-nh3-sanitize-private-channel  
**Status at archive:** Archive  
**Project:** Astral Contact  
**Assignee:** katherine  
**Priority / estimate:** None / 3  
**Parent:** AST-2055 — Contact Estelle can currently add a meteorite directly to the job table  
**Blocked by / blocks / related:** parent: AST-2055; blocks: AST-2062

### Description

## What this implements

Contact Estelle's platform access becomes a pinhole. She can write only to `meteorite` (insert, plus the existing BOT_BLOCKED → READY content update), never to `job` or `candidate`. Everything she saves, whether it comes from her or from a candidate paste, goes through one sanitize helper backed by the `nh3` library. She acts only in DMs and private channels. Reads of job, company, candidate and agent_data stay as they are.

## Scope

## Component scope

* `requirements.txt`: modified. Adds `nh3`, the sanitization library the To-be requires.
* `src/utils/config.py`: modified. Remove `create_contact_meteorite` from `CONTACT_TASK_CONFIG`. Remove the two Contact skills and adjust their asserts. Add the allowed channel types to `CONTACT_CONFIG`. Add the pinhole assert.
* `src/core/meteorite.py`: modified. Delete `create_contact_meteorite`. Add the shared sanitize helper, and call it in `insert_slack_meteorite` and `apply_paste`.
* `src/external/slack.py`: modified. New read-only helper wrapping Slack `conversations.info`, so the private-channel gate can tell DM / private / public apart (`app_mention` events carry no `channel_type`, and modern private channels use `C…` ids like public ones). Amended at AST-2061's `[scope-gate]`.
* `src/core/contact.py`: modified. Drop the skill ACL prompt section and `skill_calls` execution. Sanitize the `contact_land_meteorite` blob. Add the private-channel gate in `_handle_slack_event_body`.

## Technical scope

* `requirements.txt`: new dependency `nh3`, pinned like its neighbors.
* `src/utils/config.py`: removed config entries (one contact task, two skills), removed or adjusted asserts that reference the deleted skills, a new `CONTACT_CONFIG` field for the allowed Slack channel types, and a new import-time assert guarding Contact handler paths.
* `src/core/meteorite.py`: deleted function `create_contact_meteorite`. New function: a sanitize helper wrapping `nh3`, so there is one library-backed sanitize point. Modified functions `insert_slack_meteorite` and `apply_paste`, which sanitize text before the write.
* `src/external/slack.py`: new function, a read-only channel-type lookup over `conversations.info` (`is_im` / `is_mpim` / `is_private`). The `_handle_slack_event_body` gate calls it for `app_mention` events and fails closed when the lookup fails. No new Slack scopes are needed (`channels:read` / `groups:read` are already granted, AST-1814).
* `src/core/contact.py`: modified function `run_contact_estelle_turn` (no skill ACL section, no `skill_calls` loop). Modified function `contact_land_meteorite` (sanitized blob into `stage_meteorite`). Modified function `_handle_slack_event_body` (channel-type gate ahead of the command intercept and the turn). `run_contact_skill` and its helpers may become dead code to delete; plan-fix's call.

## Acceptance criteria

- [X] No Contact-reachable path (command, contact task, `land_calls`, paste recovery) calls `create_meteorite_job` or writes a `job` row. `create_contact_meteorite` is gone from `CONTACT_TASK_CONFIG`, from Estelle's prompt, and from `src/core/meteorite.py`.
- [X] Estelle cannot write `candidate`: the `save_candidate_profile` / `save_candidate_contact` skills, the ACL prompt section, and `skill_calls` execution are removed.
- [X] Every Contact-originated meteorite write (`insert_slack_meteorite` payload, `contact_land_meteorite` blob, Slack `apply_paste` text) is sanitized through one `nh3`-backed helper before saving. No homegrown sanitizer.
- [X] An `app_mention` from a public channel gets no command, no Estelle turn, and no save. DMs (`im`) and private channels (`group`) behave as today. The allowed types are read from `CONTACT_CONFIG`.
- [X] An import-time assert in `config.py` fails if a Contact command or task handler points at a non-read path outside `src.core.meteorite` (for example `create_meteorite_job`).
- [X] Read-only tasks (`get_job_by_pattern`, `get_job_data`, `get_company_data`, `get_candidate_data`) and `gazer_scrape` keep working unchanged.

## Boundaries

- [X] `create_meteorite_job` stays, because gazer's email ingress (`src/core/gazer.py`) still uses it. Email ingress is out of scope.
- [X] `resolve_slack_user`'s `contact.slack_username` stamp (AST-1105 identity binding) is untouched. It is Contact platform code, not something Estelle sends.
- [X] agent_data rows from Estelle turns are platform audit logging, untouched.
- [X] No new artifact or `rubric_vector` write path is added. Susan permits them, but none exists today and none is in scope.
- [X] No length cap on payloads (a limit needs Susan's explicit approval).

## Notes for planning

Approved ancestor: **AST-1517** (archived). Doc to patch: `docs/features/contact/ast-1517-create-contact-meteorite.md`, which introduced `create_contact_meteorite` → `create_meteorite_job`. Other context docs: `docs/features/contact/ast-1071-contact-config-acl-entity-save-skills.md` (the skills), `docs/features/contact/ast-2035-contact-add-job-intercept.md` (the `/add-job` intercept), and `docs/features/contact/ast-2034-raw-new-meteorite-stage-classify.md` (`insert_slack_meteorite`). The full As-is surface table is on the mini-parent [AST-2055](https://linear.app/astralcareermatch/issue/AST-2055).

## Git branch (authoritative)

Parent `ftr/AST-2055-estelle-pinhole`; this child `sub/AST-2055/AST-2061-estelle-pinhole`. Registry is authoritative.

### Comments

#### radia — 2026-10-08T22:50:35.506Z
[code-rubric] PROCEED (Commit: 31ccbee3) Estelle pinhole clean

#### katherine — 2026-10-08T22:48:38.106Z
Correction to the count above: test_contact has 3 create_contact_meteorite failures (not 4), so the AST-2062 total is 33 (7 meteorite + 3 + 2 + 18 contact + 3 config).

#### katherine — 2026-10-08T22:48:28.506Z
`origin/sub/AST-2055/AST-2061-estelle-pinhole` @ `31ccbee3` · lighter check green (compile + touched suites); 33 new failures all AST-2062 scope: 7 create_contact_meteorite/_contact_param_looks_like_url (test_meteorite), 4 create_contact_meteorite + 2 save_candidate_*/skill_calls (test_contact), 3 config (skills/task keys), 18 app_mention C… cases green once fetch_channel_type patched to "group"; 82 other failures pre-exist on 6b00d8c5 (not this fix).

#### chuckles — 2026-10-08T22:45:09.016Z
Board: CANON OK, TESTS REVISE → test gap routed to [AST-2062](https://linear.app/astralcareermatch/issue/AST-2062) (blocked by this ticket). qa-fix skipped here; next make-fix.

#### joan — 2026-10-08T22:44:28.381Z
[board-joan]  CANON: OK

#### betty — 2026-10-08T22:43:41.945Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/{contact,meteorite}.md + utils/config.md — broken tests + no repro coverage — Blast radius breaks existing nodes (create_contact_meteorite refs in test_meteorite.py/test_contact.py/test_config.py; save_candidate_* skills in test_config.py/test_contact.py/test_api_contact.py; skill_calls in test_contact.py/test_config.py/test_repo_admin_json.py; ~20 C… app_mention cases in test_contact.py need fetch_channel_type patched) and the four repros (job leak, candidate write, nh3 sanitize, public-channel gate) plus fetch_channel_type / sanitize_contact_text / pinhole assert have no bible entry.

#### katherine — 2026-10-08T22:42:47.384Z
`origin/sub/AST-2055/AST-2061-estelle-pinhole` @ `e1855dbc` · pinhole fix plan ready

#### chuckles — 2026-10-08T22:40:36.871Z
[scope-gate] resolved: added `src/external/slack.py` (a new read-only `conversations.info` channel-type helper) to `## Scope` on AST-2061 and to Component/Technical scope on [AST-2055](https://linear.app/astralcareermatch/issue/AST-2055). Fails closed on lookup error; no new Slack scopes. Prefix-only gating rejected, since it would block modern private channels.

#### katherine — 2026-10-08T22:40:03.419Z
[scope-gate] @chuckles — AST-2061 needs one file added to scope: `src/external/slack.py`

**Kind of change needed:** a new read-only external helper (for example `fetch_channel_type(channel) -> "im" | "mpim" | "group" | "channel"`), wrapping Slack `conversations.info` (`is_im` / `is_mpim` / `is_private`). The `_handle_slack_event_body` gate in `src/core/contact.py` calls it for `app_mention` events, skips the lookup for `D…` (DM) ids, and fails closed if the lookup fails.

**Scope lines that don't cover it:**
> `src/core/contact.py`: … Add the private-channel gate in `_handle_slack_event_body`.
> `src/core/contact.py`: modified function `_handle_slack_event_body` (channel-type gate ahead of the command intercept and the turn).

Neither `## Component scope` nor `## Technical scope` names `src/external/slack.py`.

**Why it can't be done inside current scope:**
- Slack `app_mention` payloads carry no `channel_type` (only `message.*` events do). The repo's own fixtures match: every `app_mention` in `tests/component/core/test_contact.py` is `{type, user, channel, text}`.
- Channel id prefixes can't tell private from public. `D…` is a DM, but private channels created on modern Slack get `C…` ids, the same as public channels.
- The existing `list_bot_channels()` returns only `{id, name}`, with no privacy flag. Core can't call `_slack_bot_get` directly (private helper, layer rule).

**In-scope alternative, which I don't recommend:** gate on the id prefix alone (`D` → im, `G` → group, block `C`). This blocks modern private channels, which breaks the AC "DMs (`im`) and private channels (`group`) behave as today". It would need Susan to accept that regression.

Scopes are already in place: `channels:read` and `groups:read` are on the bot token (AST-1814), and `conversations.info` needs nothing more for public or private channels.

Everything else in the fix fits the declared scope. After amending, assign this bug to Chuckles.

---

_Implementation detail may live in git history on `origin/dev`._
