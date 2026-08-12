# AST-1043 — Slack Bot Agent

<!-- linear-archive: AST-1043 archived 2026-08-11 -->

## Linear archive (AST-1043)

**Archived:** 2026-08-11  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent  
**Status at archive:** Archive  
**Project:** Astral Contact  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** blocks: AST-1073; related: AST-1046

### Description

## Purpose

Astral Contact owns Estelle on the Astral Career Match Slack workspace: a named bot members can DM or @ in public and private channels she has joined. This epic ships the **Contact** Slack foundation — Events-API **webhook** ingress (Slack POSTs to Astral), Slack-user → candidate resolve by **extending the shipped** [AST-1047](https://linear.app/astralcareermatch/issue/AST-1047/reusable-get-candidate-string-lookup-from-bind-bind-email-to-candidate) `get_candidate_id_for_query` **util** (plus **PROSPECT** create + Slack user id on first @), Admin **Manage Slack** listen switch (per environment), Slack-sourced conversation context load/cache, and a **CONTACT_CONFIG**-driven internal ACL of predetermined agent skills — on production Railway by default. Full Estelle conversational turn loop + success/failure/concern envelope lives on [AST-1046](https://linear.app/astralcareermatch/issue/AST-1046/contact-estelle-conversational-envelope) (blocked by this parent).

## Functional scope

A Slack bot/user named **Estelle** can receive DMs and @-mentions in public and private channels she has joined on the Astral Career Match Slack server. Contact is the new core embodiment for Slack I/O and identity under **Astral Contact**.

**Contact vs Consult:** Contact and Consult share a shape — each coordinates externals to drive business logic for its primary role. Consult’s role is efficient job analysis; Contact’s is productive discourse with users. Contact’s allowed capabilities live in **CONTACT_CONFIG** in `src/utils/config.py`. That block may look syntactically similar to TASK_CONFIG, but it must stay distinct: Contact skills are not dispatch tasks.

**Resolve / bind user:** Reuse [AST-1047](https://linear.app/astralcareermatch/issue/AST-1047/reusable-get-candidate-string-lookup-from-bind-bind-email-to-candidate)’s core `get_candidate_id_for_query` (string → unambiguous `astral_candidate_id`). Extend lookup config/metadata so a Slack user id is a first-class match home. On @Estelle: query with the Slack user id; if no match, Contact creates a **PROSPECT** candidate, stores the Slack user id, and seeds profile fields (e.g. names) from Slack metadata. Users who never @ Estelle are not created. Subsequent routing follows the resolved candidate’s state-machine status.

Conversation context for later Estelle turns is sourced from **Slack** (thread/channel history); Astral may cache Slack content and append new inbound/outbound messages as needed, but does **not** persist full conversation exchanges as a separate DB transcript store.

Contact manages an **internal ACL** (from CONTACT_CONFIG) of predetermined agent skills that may save entity data. Contact may use external Slack I/O, DeepSeek/`do_task` (consumed by [AST-1046](https://linear.app/astralcareermatch/issue/AST-1046/contact-estelle-conversational-envelope)), Playwright where needed for fetch, and the database — within layer rules.

**Slack → Astral configuration (Events API webhook):**

1. Create/install a Slack app in the Astral Career Match workspace with a bot user named Estelle.
2. Enable **Event Subscriptions** and set the **Request URL** to the production Astral HTTPS path that receives Slack events (Contact webhook entrypoint on Railway).
3. Subscribe to the bot events needed for DMs and @-mentions (and any channel message events Contact must see).
4. Put bot token + signing secret (and any other Slack secrets) in **environment variables** per deploy; behavior flags (listen on/off, event allowlists) in config / Manage Slack — not secrets in config literals.
5. Admin **Manage Slack** listen/respond switch is set **independently per environment**. When off, Contact does not respond. When on and deploy is not production, outbound replies are prefixed with `[<environment>]`.

**Why Events API HTTP webhook (not Socket Mode listener) for production:** The Events API Request URL **is** the webhook: Slack POSTs Estelle-relevant events to Astral. That is the superior production approach on Railway because (a) Astral already runs an always-on HTTPS app — Slack pushes in, no outbound persistent socket to babysit; (b) ack-within-~3s + async process fits gunicorn; (c) signing-secret verification is straightforward; (d) horizontal scale and deploys do not break a sticky WebSocket. **Socket Mode** (Astral opens a long-lived WebSocket *to* Slack) is a listener-style alternative useful for local/dev without a public URL — not the production anatomy. Polling Slack history on a timer is worse for latency and rate limits. Estelle-specific content is filtered by which events the app subscribes to and by Contact’s @/DM routing — not by choosing a different transport.

When backend Contact/Slack paths run with `debug=True`, touched paths log what was found and recorded (index headers + `|` detail; long payloads truncated per AST-538).

## Architectural definition

* **Patterns to reuse**
  * `pattern.config.config-block` — CONTACT_CONFIG (skills/ACL, distinct from TASK_CONFIG), Manage Slack listen flag, CANDIDATE_LOOKUP_CONFIG Slack-user-id home; secrets in environ.
  * `pattern.layers.import-discipline` — Contact in core; slack external (and DeepSeek/Playwright) in external; data for persistence; thin UI for Manage Slack + Events webhook entry.
  * `pattern.state.entity-state-transitions` — add PROSPECT as a real CANDIDATE_STATES registry key; Slack user id on candidate for lookup.
  * `pattern.ui.admin-endpoint` — Manage Slack admin surface: auth + thin API.
  * [AST-1047](https://linear.app/astralcareermatch/issue/AST-1047/reusable-get-candidate-string-lookup-from-bind-bind-email-to-candidate) `get_candidate_id_for_query` — extend match homes for Slack user id; do **not** invent a second matcher.
* **New patterns proposed** (Archie approval before implementation depends on them)
  * `pattern.external.slack-events` — Slack Events API HTTP webhook verify/ack/post via external; Contact orchestrates; production = Request URL on Railway.
  * `pattern.core.contact-agent` — Contact owns Slack foundation + CONTACT_CONFIG skills; conversational envelope/turn loop on [AST-1046](https://linear.app/astralcareermatch/issue/AST-1046/contact-estelle-conversational-envelope).
* **Applicable statutes**
  * `astral.layers.core-vs-external-bright-line` / `astral.layers.import-direction`
  * `astral.config.config-source-of-truth` / `astral.config.secrets-and-env-specific-from-environ`
  * `astral.patterns.require-auth-on-protected-endpoints`
  * `astral.standards.debug-contract-gated` / `astral.standards.logging-via-utils`
  * `astral.standards.database-header-inventory` / `astral.standards.in-scope-only` / `astral.standards.no-cross-contamination` / `astral.standards.no-hardcoded-sets` / `astral.standards.dry-and-focused-functions` / `astral.standards.public-then-helpers`

## Boundaries

Does **not** own the Estelle conversational turn loop or success/failure/concern agent envelope — that is [AST-1046](https://linear.app/astralcareermatch/issue/AST-1046/contact-estelle-conversational-envelope). Does **not** re-implement [AST-1047](https://linear.app/astralcareermatch/issue/AST-1047/reusable-get-candidate-string-lookup-from-bind-bind-email-to-candidate) `get_candidate_id_for_query` — only extend match homes + Slack create-on-miss. Does **not** conflate CONTACT_CONFIG skills with TASK_CONFIG / dispatch tasks. Does **not** redesign web Candidate Intake Chat Session (**AST-539**). Does **not** subsume [AST-952](https://linear.app/astralcareermatch/issue/AST-952/candidate-profile-preamble-to-intake). Does **not** re-do Meteorite Manage Email ([AST-1044](https://linear.app/astralcareermatch/issue/AST-1044/bind-email-to-candidate) Done). Does **not** ship a general Astral ops Slack bot. Does **not** grant Contact unrestricted admin DB mutation beyond the internal skill ACL. Does **not** use Socket Mode as the production ingress. Does **not** store full Slack conversation exchanges as a first-class DB transcript. Does **not** include astral-faq Q&A (fast-follow). Does **not** include activity-summary in v1. Does **not** create candidate rows for Slack users who never @ Estelle.

## Acceptance criteria

1. Estelle exists in the Astral Career Match Slack workspace; members can DM her and @ her in public and private channels she has joined (ingress + reply plumbing ready for [AST-1046](https://linear.app/astralcareermatch/issue/AST-1046/contact-estelle-conversational-envelope)).
2. Slack Event Subscriptions Request URL points at Astral’s production Contact webhook; signed events are verified and ack’d; Estelle-relevant DMs/@-mentions reach Contact when Manage Slack listen is on.
3. Admin **Manage Slack** exposes a per-environment listen/respond switch; when off, Contact does not respond; when on for non-production, replies are prefixed with `[<environment>]`.
4. Slack @Estelle resolves via `get_candidate_id_for_query` ([AST-1047](https://linear.app/astralcareermatch/issue/AST-1047/reusable-get-candidate-string-lookup-from-bind-bind-email-to-candidate)) using Slack user id; first unknown Slack user creates **PROSPECT** with Slack user id stored and Slack-seeded profile fields; no @ means no candidate row from Slack.
5. @Estelle routing resolves to a candidate and exposes state-machine status for downstream Contact/Estelle behavior.
6. Slack conversation history can be loaded (with optional cache) without a separate full-exchange transcript table.
7. CONTACT_CONFIG defines Contact’s allowed skills/ACL; those are the only paths Contact offers for entity writes (distinct from dispatch TASK_CONFIG).
8. With `debug=True` on touched Contact/Slack backend paths, found/recorded outcomes use Style D index headers and `|` detail.
9. Admin **Manage Slack** lists Slack users who have @'ed Estelle: bind success/fail to an Astral candidate, inbound message count from that Slack user, and timestamp + channel of the last message seen.

## Dependencies and blockers

none hard-blocked. **Done and reuse:** [AST-1044](https://linear.app/astralcareermatch/issue/AST-1044/bind-email-to-candidate) / [AST-1047](https://linear.app/astralcareermatch/issue/AST-1047/reusable-get-candidate-string-lookup-from-bind-bind-email-to-candidate) (`get_candidate_id_for_query`). **Blocked child epic:** [AST-1046](https://linear.app/astralcareermatch/issue/AST-1046/contact-estelle-conversational-envelope). Adjacent: archived **AST-539**; [AST-952](https://linear.app/astralcareermatch/issue/AST-952/candidate-profile-preamble-to-intake) / [AST-1014](https://linear.app/astralcareermatch/issue/AST-1014/contact-context-artifacts-library-name-columns-candidate-profile); [AST-970](https://linear.app/astralcareermatch/issue/AST-970/candidate-state-registry-and-transitions-candidate-state-machine) (adds PROSPECT + Slack user id match home). Fast-follow: astral-faq; activity summary.

## Open questions

none.

## Proposed child tickets

#### 1!!: **Contact core module and CONTACT_CONFIG - Ada**

Stand up Contact in core plus CONTACT_CONFIG (skills/ACL distinct from TASK_CONFIG), listen flag, Slack-user-id on CANDIDATE_LOOKUP_CONFIG, and environ secrets contracts. Does not own Slack HTTP Events plumbing (#2), Manage Slack UI (#3), Slack resolve/PROSPECT create (#4), context load (#5), or skill endpoint bodies (#6).
**Citations:** `pattern.core.contact-agent` (proposed), `pattern.config.config-block`, `astral.layers.import-direction`, `astral.config.secrets-and-env-specific-from-environ`

#### 2!: **Slack Events API webhook ingress (external slack) - Hedy**

External slack Events API HTTP webhook: verify signing secret, URL challenge, ack-within-3s, dedupe `event_id`, post replies via Web API. Document Request URL wiring for Railway. Does not own Manage Slack switch UX (#3). After #1.
**Citations:** `pattern.external.slack-events` (proposed), `astral.layers.core-vs-external-bright-line`, `astral.config.secrets-and-env-specific-from-environ`

#### 3: **Manage Slack admin listen switch - Katherine**

Admin Manage Slack per-environment listen/respond switch and non-production `[<environment>]` reply prefix. Does not own Events verify/post (#2) or resolve-user (#4). After #2.
**Citations:** `pattern.ui.admin-endpoint`, `pattern.config.config-block`, `astral.patterns.require-auth-on-protected-endpoints`

#### 4: **Slack resolve via get_candidate_id_for_query + PROSPECT create - Ada**

Extend [AST-1047](https://linear.app/astralcareermatch/issue/AST-1047/reusable-get-candidate-string-lookup-from-bind-bind-email-to-candidate) lookup homes for Slack user id; on @Estelle call `get_candidate_id_for_query`; on miss create PROSPECT, persist Slack user id, seed names/profile from Slack metadata. Adds PROSPECT to CANDIDATE_STATES. After #2.
**Citations:** [AST-1047](https://linear.app/astralcareermatch/issue/AST-1047/reusable-get-candidate-string-lookup-from-bind-bind-email-to-candidate) `get_candidate_id_for_query`; `pattern.state.entity-state-transitions`; `pattern.core.contact-agent` (proposed); `astral.standards.no-hardcoded-sets`; `astral.standards.database-header-inventory`

#### 5: **Slack-sourced conversation context load and cache - Hedy**

Load conversation context from Slack thread/channel history; optional cache and append of new in/out messages; **no** full-exchange DB transcript store. After #2.
**Citations:** `pattern.core.contact-agent` (proposed), `pattern.external.slack-events` (proposed), `astral.layers.core-vs-external-bright-line`, `astral.standards.in-scope-only`

#### 6: **CONTACT_CONFIG ACL / predetermined entity-save skills - Katherine**

Implement Contact skill runners allowlisted by CONTACT_CONFIG (entity-save paths only as configured). Does not own Slack history load (#5) or conversational envelope ([AST-1046](https://linear.app/astralcareermatch/issue/AST-1046/contact-estelle-conversational-envelope)). After #1.
**Citations:** `pattern.core.contact-agent` (proposed), `pattern.config.config-block`, `astral.patterns.require-auth-on-protected-endpoints`, `astral.standards.in-scope-only`

**New patterns:** #1 → `pattern.core.contact-agent`; #2 → `pattern.external.slack-events`. Resolve = reuse [AST-1047](https://linear.app/astralcareermatch/issue/AST-1047/reusable-get-candidate-string-lookup-from-bind-bind-email-to-candidate).

**Moved out:** Estelle turn loop + envelope → [AST-1046](https://linear.app/astralcareermatch/issue/AST-1046/contact-estelle-conversational-envelope).

**Dropped:** astral-faq Q&A; activity-summary.

**Monolith check:** Six foundation children; dialogue on [AST-1046](https://linear.app/astralcareermatch/issue/AST-1046/contact-estelle-conversational-envelope).

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| [AST-1043](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent) (parent) | ftr/AST-1043-slack-bot-agent |
| [AST-1066](https://linear.app/astralcareermatch/issue/AST-1066/contact-core-module-and-contact-config-slack-bot-agent) | sub/AST-1043/AST-1066-contact-core-module-and-contact-config |
| [AST-1069](https://linear.app/astralcareermatch/issue/AST-1069/slack-events-api-webhook-ingress-external-slack-contact) | sub/AST-1043/AST-1069-slack-events-api-webhook-ingress |
| [AST-1067](https://linear.app/astralcareermatch/issue/AST-1067/manage-slack-admin-listen-switch-per-environment-non-prod-reply-tag) | sub/AST-1043/AST-1067-manage-slack-admin-listen-switch |
| [AST-1068](https://linear.app/astralcareermatch/issue/AST-1068/slack-resolve-via-get-candidate-id-for-query-prospect-create) | sub/AST-1043/AST-1068-slack-resolve-via-get-candidate-id |
| [AST-1070](https://linear.app/astralcareermatch/issue/AST-1070/slack-sourced-conversation-context-load-and-cache) | sub/AST-1043/AST-1070-slack-sourced-conversation-context |
| [AST-1071](https://linear.app/astralcareermatch/issue/AST-1071/contact-config-acl-predetermined-entity-save-skills) | sub/AST-1043/AST-1071-contact-config-acl-entity-save-skills |
| [AST-1094](https://linear.app/astralcareermatch/issue/AST-1094/uat-manage-slack-list-of-estelle-users-bind-status-msg-count-last) | sub/AST-1043/AST-1094-uat-manage-slack-estelle-activity-list |
| [AST-1101](https://linear.app/astralcareermatch/issue/AST-1101/uat-channel-estelle-no-contact-hear-evidence-activity-reply) | sub/AST-1043/AST-1101-uat-channel-at-estelle-no-hear-evidence |
| [AST-1105](https://linear.app/astralcareermatch/issue/AST-1105/uat-slack-usernamedisplay-on-manage-slack-activity-profile) | sub/AST-1043/AST-1105-uat-slack-username-display-activity-profile |

**Epic worktree:** `astral-AST-1043/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **Thread** column is the fully-qualified `store.db` path (UUID is the directory name — extract for `agent --resume`). **datt resume:** read this table — not chat memory. One UUID per agent; never the parent Chuckles Thread UUID.

| Agent | Role | Thread |
| -- | -- | -- |
| Katherine | engineer | `/home/susan/.cursor/chats/dc8b9f956372ceed188a68a2d2f8f217/a841fe6c-0779-484e-bf98-36da4ba4dc9a/store.db` |
| Hedy | engineer | `/home/susan/.cursor/chats/dc8b9f956372ceed188a68a2d2f8f217/dfb49f98-08ec-4552-a640-3c0c319edde8/store.db` |
| Ada | engineer | `/home/susan/.cursor/chats/dc8b9f956372ceed188a68a2d2f8f217/a6c5b2b2-f473-4e03-8ab5-e68378b75acd/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/76c6db7e-d67f-401a-a1a0-6f5096f9b9b9/store.db` |
| Radia | review | `/home/susan/.cursor/chats/dc8b9f956372ceed188a68a2d2f8f217/643a4613-9f42-428e-bd24-61eebbf8c9a5/store.db` |

---

## Original brief

I have a new slack server for Astral, and I want there to be a user/bot that can be spoken to directly and added to private channels so that intake can happen in a slack channel.  Naturally, we should name this user/bot "Estelle"

I want the production platform to allow Estelle to be available 24/7 to respond to users content.  I would like Estelle to be able to choose which and how much context she needs to respond to the request, which I think means opening an ACL to some public endpoints to provide her secure access to the data as a skill she can run.  I also want her conversations to be "stateful" so that she can get into details with the user and return back to topics previously mentioned.

This would be a medium/middle brain agent so that responses don't take 45 seconds each.

### Comments

#### chuckles — 2026-07-31T17:34:06.134Z
[fix-uat] open question — ops before filing a product UAT bug.

Your log is `users.info failed: invalid_auth` inside `resolve_slack_user` / activity identity fetch. Events are reaching Contact (signing secret path works); Slack is rejecting the **bot token** Contact uses for Web API (`CONTACT_CONFIG["bot_token_env"]` → **`SLACK_BOT_TOKEN`**).

That usually means staging Railway has a missing, revoked, truncated, or non-bot token (needs `xoxb-…` Bot User OAuth Token), not a code path inventing a second auth scheme.

@susan — please confirm on staging:
1. **`SLACK_BOT_TOKEN`** is set to the Estelle app’s **Bot User OAuth Token** (`xoxb-…`), redeploy/restart after set.
2. App has **`users:read`** (needed for `users.info`).
3. Then `@Estelle` again and say whether the traceback is gone / PROSPECT + username show up.

If the token is already correct and `invalid_auth` persists, reply here and I’ll file a `UAT:` (stacktrace-shaped) for product — e.g. wrong env contract or create-on-miss must not abort when profile fetch fails.

— Chuckles

#### susan — 2026-07-31T17:31:43.490Z
```
2026-07-31T17:28:14.441561371Z [err]    warnings.warn("Test version of Stytch not intended for production use")
2026-07-31T17:28:44.729364942Z [err]      profile = fetch_user_profile(sid)
2026-07-31T17:28:44.729371882Z [err]                ^^^^^^^^^^^^^^^^^^^^^^^
2026-07-31T17:28:44.729375922Z [err]    File "/app/src/external/slack.py", line 145, in fetch_user_profile
2026-07-31T17:28:44.729402242Z [err]  contact resolve_slack_user failed: users.info failed: invalid_auth
2026-07-31T17:28:44.729406762Z [err]  Traceback (most recent call last):
2026-07-31T17:28:44.729411582Z [err]    File "/app/src/core/contact.py", line 963, in handle_slack_event
2026-07-31T17:28:44.729416362Z [err]      resolved = resolve_slack_user(user, estelle_in_play=True, debug=debug)
2026-07-31T17:28:44.729420982Z [err]                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2026-07-31T17:28:44.729425322Z [err]    File "/app/src/core/contact.py", line 594, in resolve_slack_user
2026-07-31T17:28:44.729434802Z [err]      profile = fetch_user_profile(sid)
2026-07-31T17:28:44.729440632Z [err]                ^^^^^^^^^^^^^^^^^^^^^^^
2026-07-31T17:28:44.729444341Z [err]    File "/app/src/external/slack.py", line 145, in fetch_user_profile
2026-07-31T17:28:44.729448331Z [err]      raise RuntimeError(f"users.info failed: {payload.get('error')}")
2026-07-31T17:28:44.729451831Z [err]  RuntimeError: users.info failed: invalid_auth
2026-07-31T17:28:44.729455251Z [err]  contact activity identity fetch failed: users.info failed: invalid_auth
2026-07-31T17:28:44.729458681Z [err]  Traceback (most recent call last):
2026-07-31T17:28:44.729461961Z [err]    File "/app/src/core/contact.py", line 963, in handle_slack_event
2026-07-31T17:28:44.729465411Z [err]      resolved = resolve_slack_user(user, estelle_in_play=True, debug=debug)
2026-07-31T17:28:44.729468931Z [err]                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2026-07-31T17:28:44.729473061Z [err]    File "/app/src/core/contact.py", line 594, in resolve_slack_user
2026-07-31T17:28:44.730052045Z [err]      raise RuntimeError(f"users.info failed: {payload.get('error')}")
2026-07-31T17:28:44.730058055Z [err]  RuntimeError: users.info failed: invalid_auth
2026-07-31T17:28:44.730062895Z [err]  
2026-07-31T17:28:44.730067055Z [err]  During handling of the above exception, another exception occurred:
2026-07-31T17:28:44.730071545Z [err]  
2026-07-31T17:28:44.730076235Z [err]  Traceback (most recent call last):
2026-07-31T17:28:44.730082955Z [err]    File "/app/src/core/contact.py", line 983, in handle_slack_event
2026-07-31T17:28:44.730087375Z [err]      profile = fetch_user_profile(user.strip())
2026-07-31T17:28:44.730092535Z [err]                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2026-07-31T17:28:44.730096804Z [err]    File "/app/src/external/slack.py", line 145, in fetch_user_profile
2026-07-31T17:28:44.730101344Z [err]      raise RuntimeError(f"users.info failed: {payload.get('error')}")
2026-07-31T17:28:44.730106004Z [err]  RuntimeError: users.info failed: invalid_auth
2026-07-31T17:28:44.730109894Z [err]  run_next chain entry: task=contact_estelle_turn batch_id=
```

#### chuckles — 2026-07-31T06:09:57.464Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-1105** | Slack username/display on Manage Slack activity + Profile |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-1105** — _Slack username/display on Manage Slack activity + Profile_
- **Issue reported:** Manage Slack @Estelle activity list shows only the opaque Slack user id (e.g. `U0BLSRFG1UL`) — no username / profile display metadata. Candidate Profile UI also does not show the Slack user id or Slack username for Slack-bound candidates (resolve already calls `users.info` for fi
- **Should now:** 1. Manage Slack activity rows show human-readable Slack identity (username and/or display name) in addition to Slack user id, bind status, message count, last channel/ts.
- **Quick check (this fix only):**
  1. Staging: listen on; Estelle in channel; Events API (not Socket Mode).
  2. `@Estelle` from a Slack user so an activity row exists.
  3. Admin → Manage Slack — row shows only `U…` id, no username/display name.
  4. Open the bound candidate’s Profile — no Slack user id / Slack username field visible.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-07-31T05:20:34.680Z
There we go!  I disabled socket mode and now it is working properly. Whew!

Okay, now the next problem is the metadata we're showing on the new screen just has `U0BLSRFG1UL` for the Slack user.  Can you get more metadata (like username and profile info) about the user?  Also, did we forget to put the user's slack username in the profile UI?

#### chuckles — 2026-07-31T04:47:45.826Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-1101** | Channel @Estelle — no Contact hear evidence (activity / reply) |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-1101** — _Channel @Estelle — no Contact hear evidence (activity / reply)_
- **Issue reported:** Staging Slack Event Subscriptions Request URL verifies (challenge OK). Manage Slack listen is on. @Estelle in a Slack channel produces no UAT-visible evidence that Contact accepted the event (no Manage Slack @Estelle-users activity row, no non-prod reply / hear signal).
- **Should now:** With listen **on** and Estelle in the channel: channel `@Estelle` reaches Contact (`app_mention`). Manage Slack lists the Slack user (bind status, msg count, last channel/ts). Non-production replies use the `[<environment>]` prefix when Contact posts a reply.
- **Quick check (this fix only):**
  1. Staging: Request URL verified; Admin → Manage Slack listen **on**.
  2. Confirm Estelle is a **member** of the test channel; Event Subscriptions include bot event `app_mention`.
  3. In that channel, `@Estelle` with a short message.
  4. Open Admin → Manage Slack — activity list does not show the Slack user / last message.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-07-31T04:33:03.537Z
Okay.  I believe I have set up Estelle to be listening on both ends in staging, the url works in the slack browser admin page, but when I @ Estelle in the slack channel, I can't see any evidence that Astral hears it.

#### chuckles — 2026-07-31T04:11:39.997Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-1094** | Manage Slack list of @Estelle users (bind status, msg count, last channel/ts) |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-1094** — _Manage Slack list of @Estelle users (bind status, msg count, last channel/ts)_
- **Issue reported:** UAT cannot verify Slack → Contact resolve/bind without an admin view of who @'ed Estelle. Manage Slack today only exposes the listen switch — no list of Slack users who @'ed Estelle, bind outcome, message counts, or last-seen channel/timestamp.
- **Should now:** Admin **Manage Slack** shows a list of Slack users who have @'ed Estelle, each with: whether they bound successfully to an Astral candidate, inbound message count from that Slack user, and the timestamp + channel of the last message seen.
- **Quick check (this fix only):**
  1. Deploy with Slack Events Request URL + secrets configured; Manage Slack listen **on**.
  2. From Slack, @Estelle (and optionally a second user / second channel).
  3. Open Admin → Manage Slack.
  4. Observe: no list of @Estelle Slack users / bind status / counts / last message metadata — cannot confirm AC #4–#5 from the admin UI.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-07-31T03:50:02.587Z
In this epic, please.  I can't really test it without this feature.

#### chuckles — 2026-07-31T03:46:16.521Z
[fix-uat] open question — need Archie call before filing a UAT bug.

Your ask (list of Slack users who @'ed Estelle, bind success/fail, message count, last message timestamp + channel) is **not** covered by any current parent Acceptance Criterion. Manage Slack AC is listen on/off + non-prod `[<environment>]` reply tag only.

@susan — pick one:
1. **In this epic** — expand AC / file as `UAT:` (new Manage Slack / Contact admin surface this wave), or
2. **Out of scope** — spin a follow-on ticket (e.g. under Astral Contact / AST-1046)

Staging Events challenge: still ops — set `SLACK_SIGNING_SECRET` (+ bot token) on Railway staging; URL `…/api/slack/events` is correct (already answered in-thread).

— Chuckles

#### susan — 2026-07-31T03:42:19.631Z
Can you add a list of the candidates that have @'ed Estelle that we've receieved and whether or not they were bound to a candidate successfully?  Show a count of messages from the slack user, and the timestamp of the last message seen and which channel.

#### chuckles — 2026-07-31T01:43:19.075Z
[check-linear] answered — yes, Request URL is `https://astral-staging.up.railway.app/api/slack/events` (POST).

Staging is not completing Slack’s challenge today: the route is live, but Contact reads `SLACK_SIGNING_SECRET` before returning the challenge, and Railway staging currently 500s with `KeyError: 'SLACK_SIGNING_SECRET'`. Set **`SLACK_SIGNING_SECRET`** (and the bot token env Contact expects) on the staging deploy, redeploy/restart, then re-save the Request URL in Slack so it retries the challenge.

— Chuckles

#### susan — 2026-07-31T01:41:23.085Z
@chuckles I'm trying to test in staging, but [https://astral-staging.up.railway.app/api/slack/events](<https://astral-staging.up.railway.app/api/slack/events>) isn't responding with the challenge parameter.

```
We’ll send HTTP POST requests to this URL when events occur. As soon as you enter a URL, we’ll send a request with a challenge parameter, and your endpoint must respond with the challenge value.
```

Is that the URL I should use?

#### chuckles — 2026-07-31T00:13:05.666Z
[check-linear] User Testing — smoke path for Contact foundation on staging (`origin/dev`).

**Prereqs:** Estelle Slack app Event Subscriptions Request URL → staging Contact webhook; bot token + signing secret in that env; Admin → **Manage Slack** listen **on**.

**Smoke:** (1) listen off → DM/@ gets no reply; (2) listen on (non-prod) → reply with `[<environment>]` prefix; (3) first @ from unknown Slack user → PROSPECT + Slack user id; second @ same candidate; (4) never @ → no Slack-created candidate; (5) follow-up in same thread loads Slack history (cache OK, no full DB transcript SoT).

Estelle conversational turn loop / envelope is a follow-on epic — not this parent.

— Chuckles

#### chuckles — 2026-07-30T17:53:24.932Z
@susan — UAT how-to for **AST-1043** (Slack Bot Agent / Contact foundation). No product failures in your last comment — this is the smoke path against staging (`origin/dev` already landed).

**Prereqs**
1. Slack app **Estelle** in Astral Career Match workspace; Event Subscriptions **Request URL** → staging Astral Contact webhook; bot token + signing secret in that env.
2. Admin → **Manage Slack**: turn listen **on** for the staging environment.

**Smoke (map to AC)**
1. **Listen off:** DM or @Estelle — no Contact reply.
2. **Listen on (non-prod):** DM / @ in a channel she joined — reply comes back with `[<environment>]` prefix.
3. **First @ from unknown Slack user:** creates **PROSPECT**, stores Slack user id, seeds name from Slack metadata; second @ resolves same candidate (no duplicate).
4. **Never @:** no candidate row from Slack alone.
5. **Thread context:** follow-up in the same Slack thread — Contact can load recent Slack history (cache OK; no full DB transcript SoT).
6. **Manage Slack** only toggles listen/prefix — does not replace Events webhook wiring.

**Out of this epic:** Estelle conversational turn loop / success-failure-concern envelope → **AST-1046**.

If something fails, reply on this parent with what you did + what you saw (UI/API/Slack) — I’ll file `UAT:` bugs from that.

— Chuckles

#### susan — 2026-07-30T16:49:18.555Z
@chuckles How do I test this?

#### chuckles — 2026-07-30T16:06:49.740Z
@susan — next step is finishing the wave loop: AST-1066 / AST-1069 / AST-1071 are already User Testing. Overnight the wave-3 drones for AST-1067 / AST-1068 / AST-1070 died mid-pipeline (Code Complete / Plan Approved). Re-spawning those three now → UT → refresh-ftr → prep-uat.

— Chuckles

#### susan — 2026-07-30T05:11:07.145Z
@chuckles what is the next step for this ticket?

#### chuckles — 2026-07-30T02:05:15.435Z
@susan — short answer (full detail is in the Description under **Slack → Astral configuration**):

**How Slack posts to Astral:** Slack app Event Subscriptions **Request URL** = our production HTTPS Contact webhook. Slack POSTs events there; we verify the signing secret, ack fast, process async. Bot token + signing secret live in env vars; Manage Slack listen is per-environment.

**Why that beats a "listener":** Events API Request URL **is** the webhook. Socket Mode (outbound WebSocket listener) is fine for local/dev without a public URL — worse on Railway (sticky socket, reconnect, deploys). Polling is worse still. Estelle-specific traffic comes from event subscriptions + @/DM routing, not from a different transport.

— Chuckles

#### susan — 2026-07-30T01:15:06.404Z
@chuckles how do we configure the slack to post to astral?? Why is this the superior approach to a listener or webhook for Estelle-specific content?

#### susan — 2026-07-30T00:58:45.640Z
@chuckles lets revise based on recent tickets please

#### susan — 2026-07-29T18:33:21.832Z
@chuckles See my comments inline.

#### chuckles — 2026-07-29T18:11:44.981Z
@susan — open questions before Todo/dispatch:

1. Preliminary Slack-linked candidate state: add a new `CANDIDATE_STATES` key (e.g. `PROSPECT_USER` / your preferred name) with defined `prior_states` / `progress_rank`, or start Slack-linked users at existing `NEW_CANDIDATE`? (Today config asserts `PROSPECT` is not a registry key.)
2. Is **astral-faq** process Q&A in **v1** of this epic, or a fast-follow after Contact+ingress+bind ship?
3. Is "summarize recent work / outstanding activities" explicitly **out of v1** (recommended), or must it ship in this parent?

Slack anatomy answer is in the Description Architectural note: production = Events API HTTPS request URL (webhook); Socket Mode = local/dev only; replies via Web API bot token.

— Chuckles

#### chuckles — 2026-07-29T17:39:37.281Z
@susan — open questions before Todo/dispatch:

1. Who is allowed to talk to Slack Estelle in v1 — Astral internal users only, candidates, or both?
2. Is Slack Estelle the same agent/task surface as web intake Estelle (shared session/task keys where it makes sense), or a Slack-first conversational agent that can also do intake?
3. Which data domains must the v1 skill ACL expose (candidate profile/intake fields, jobs/analysis, roster, artifacts, something else)?
4. How should a Slack DM or private channel bind to an Astral candidate (manual admin bind, invite deep-link, channel naming convention, other)?
5. Confirm all Slack Estelle turns use BRAIN_MEDIUM only for v1 (no per-channel or per-intent override)?
6. Is "24/7" production-Railway-only for v1, or must test/staging also keep Estelle always-on?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
