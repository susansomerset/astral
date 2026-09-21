# AST-1046 — Contact Estelle conversational envelope

<!-- linear-archive: AST-1046 archived 2026-08-14 -->

## Linear archive (AST-1046)

**Archived:** 2026-08-14  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1046/contact-estelle-conversational-envelope  
**Status at archive:** Archive  
**Project:** Astral Contact  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Contact Estelle needs a conversational turn loop with a structured agent envelope (rubric-like), spun out of **AST-1043** so Slack Contact infrastructure can ship without owning dialogue orchestration. Each turn returns **success**, **failure**, or **concern** — where **concern** is an admin-facing aside that the user is struggling or having a negative experience, plus a short note.

## Functional scope

Wire Contact resolve + Slack-sourced context + ACL skills (from **AST-1043**) into Estelle conversational turns via `do_task` at config brain tier (default medium / non-thinking).

Agent responses use a conversational envelope with outcomes **success** | **failure** | **concern**. A **concern** outcome carries a short admin aside for Astral operators about user struggle / negative experience.

Honor Manage Slack listen gate and non-production `[<environment>]` prefix from **AST-1043**.

Debug-contract on touched backend paths when `debug=True`.

## Architectural definition

* **Patterns to reuse** — Contact/Slack patterns from **AST-1043** once approved; `pattern.config.config-block`; `astral.agent.do-task-delegation`.
* **New patterns proposed** — `pattern.agent.conversational-envelope` — structured turn outcome success|failure|concern (+ admin aside on concern).
* **Applicable statutes** — `astral.agent.do-task-delegation`; `astral.standards.debug-contract-gated`; `astral.layers.core-vs-external-bright-line`; universal product-code set.

## Boundaries

Does **not** re-implement Slack Events ingress, Manage Slack switch, resolve-util, Slack context cache, or Contact ACL skill catalog (**AST-1043**). Does **not** include astral-faq Q&A or activity-summary.

## Acceptance criteria

1. Estelle can complete a multi-turn Slack conversation using **AST-1043** Contact plumbing.
2. Each agent turn yields a structured envelope outcome of success, failure, or concern.
3. A concern outcome records an admin-visible aside (short note) about user struggle / negative experience.
4. Default brain tier remains medium / non-thinking unless config says otherwise.
5. Debug=True paths emit contract index + `|` detail for turn outcomes.

## Dependencies and blockers

**Blocked by AST-1043** (Contact Slack foundation). Related: **AST-1044** (shared resolve util).

## Open questions

none yet — run define-parent when Archie is ready to refine children.

## Proposed child tickets

#### 1!: **Conversational agent envelope (success / failure / concern) - Ada**

Schema + `do_task` contract for conversational envelope; concern → admin aside + note. Does not own Slack wiring.
**Citations:** `pattern.agent.conversational-envelope` (proposed), `astral.agent.do-task-delegation`

#### 2: **Contact Estelle turn loop over AST-1043 Contact - Hedy**

Wire resolve + Slack context + ACL + listen gate into turns consuming the envelope. After #1; after **AST-1043**.
**Citations:** `pattern.core.contact-agent` (proposed), `astral.standards.debug-contract-gated`

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-1046 (parent) | ftr/AST-1046-contact-estelle-conversational-envelope |
| AST-1072 | sub/AST-1046/AST-1072-conversational-agent-envelope |
| AST-1073 | sub/AST-1046/AST-1073-contact-estelle-turn-loop |

**Epic worktree:** `astral-AST-1046/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **Thread** column is the fully-qualified `store.db` path (UUID is the directory name — extract for `agent --resume`). **datt resume:** read this table — not chat memory. One UUID per agent; never the parent Chuckles Thread UUID.

| Agent | Role | Thread |
| -- | -- | -- |
| Hedy | engineer | `/home/susan/.cursor/chats/1881949f6913c56102302a1096e88bcb/afd2a1f0-a51a-4617-b76c-f88b76e63c22/store.db` |
| Ada | engineer | `/home/susan/.cursor/chats/1881949f6913c56102302a1096e88bcb/234777dd-eefd-4660-99e5-1594c1a07725/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/62019fcc-f4d8-4fe4-bf19-23b0696bc2a9/store.db` |
| Radia | review | `/home/susan/.cursor/chats/1881949f6913c56102302a1096e88bcb/d43e3f1b-44e4-41f5-bcc4-ce9b68995b16/store.db` |

---

## Original brief

Moved from AST-1043 proposed child #7: Contact Estelle turn loop was too much for that parent. New ticket should support an agent envelope like we do for rubrics, but because it's conversational, the agent should respond with "success", "failure", "concern", where "concern" would give the agent an opportunity to express an aside to the Astral admins that the user is struggling or having a negative experience, with a sentence of notes.

### Comments

#### chuckles — 2026-08-06T02:49:26.397Z
[fix-uat] open questions — need your call before filing a UAT bug

**Symptom (your comment):** production Contact logs show `RuntimeError: users.info failed: invalid_auth` twice — once in `resolve_slack_user` / `fetch_user_profile`, then again on the activity-identity fallback fetch. You noted resolve should have worked for your userdata and there was no further useful log trail.

**Parent AC this hits:**
> 1. Estelle can complete a multi-turn Slack conversation using **AST-1043** Contact plumbing.

**Why I’m not filing yet (ambiguity):**
Slack `invalid_auth` on `users.info` means the **bot token Slack received is rejected** (revoked, wrong workspace, wrong/missing env value, truncated secret). The same `CONTACT_CONFIG["bot_token_env"]` token is used for `chat.postMessage`, so a bad token also blocks outbound Estelle replies — this is not an envelope schema / turn-loop outcome bug by itself.

AST-1046 **Boundaries** say we do **not** re-own resolve / Slack token plumbing (**AST-1043**). I cannot pick a single AC-tied product hypothesis on this parent without knowing whether production’s Contact bot token is actually valid.

**Need from you:**
1. Confirm production Contact bot token env (the one `CONTACT_CONFIG` names) is set and valid for the Estelle app in that workspace — or say it’s known-good and we should treat this as a code path bug on **AST-1043** / wrong token source.
2. Was this **production** only, or does staging Railway (`origin/dev` prep-uat host) resolve you cleanly?
3. If token is good: should the UAT bug live on **AST-1046** (turn loop after resolve miss) or **AST-1043** (resolve / Slack I/O)?

@susan — once you pick, I’ll file the Bug child and run plan→qa→merge.

— Chuckles

#### susan — 2026-08-06T02:47:35.370Z
```
[
  {
    "batch_id": null,
    "created_at": "2026-08-05 16:48:16",
    "id": "67ea67e5-cbab-4fa3-b1aa-f9af8291cab2",
    "level": "ERROR",
    "logger_name": "src.core.contact",
    "message": "contact resolve_slack_user failed: users.info failed: invalid_auth\nTraceback (most recent call last):\n  File \"/app/src/core/contact.py\", line 963, in handle_slack_event\n    resolved = resolve_slack_user(user, estelle_in_play=True, debug=debug)\n               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/app/src/core/contact.py\", line 594, in resolve_slack_user\n    profile = fetch_user_profile(sid)\n              ^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/app/src/external/slack.py\", line 145, in fetch_user_profile\n    raise RuntimeError(f\"users.info failed: {payload.get('error')}\")\nRuntimeError: users.info failed: invalid_auth"
  },
  {
    "batch_id": null,
    "created_at": "2026-08-05 16:48:16",
    "id": "5646e3bf-9b2b-4969-b7e5-fe14df091979",
    "level": "ERROR",
    "logger_name": "src.core.contact",
    "message": "contact activity identity fetch failed: users.info failed: invalid_auth\nTraceback (most recent call last):\n  File \"/app/src/core/contact.py\", line 963, in handle_slack_event\n    resolved = resolve_slack_user(user, estelle_in_play=True, debug=debug)\n               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/app/src/core/contact.py\", line 594, in resolve_slack_user\n    profile = fetch_user_profile(sid)\n              ^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/app/src/external/slack.py\", line 145, in fetch_user_profile\n    raise RuntimeError(f\"users.info failed: {payload.get('error')}\")\nRuntimeError: users.info failed: invalid_auth\n\nDuring handling of the above exception, another exception occurred:\n\nTraceback (most recent call last):\n  File \"/app/src/core/contact.py\", line 983, in handle_slack_event\n    profile = fetch_user_profile(user.strip())\n              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/app/src/external/slack.py\", line 145, in fetch_user_profile\n    raise RuntimeError(f\"users.info failed: {payload.get('error')}\")\nRuntimeError: users.info failed: invalid_auth"
  }
]
```

From the production log.  It should have been able to resolve my userdata, but there's no more log content about it.

#### chuckles — 2026-08-04T18:24:37.598Z
[check-linear] User Testing — how to exercise Estelle conversational envelope

Code is on Railway staging via `origin/dev` (prep-uat landed).

**Prereqs (AST-1043 foundation)**
1. Estelle Slack app + Events Request URL pointed at Astral Contact webhook.
2. Admin **Manage Slack** listen **on** for the env you are testing (non-prod replies get `[<environment>]` prefix).
3. You can DM Estelle or `@` her in a channel she has joined.

**Happy path (multi-turn)**
1. DM / `@` Estelle as a Slack user (first unknown user should resolve/create PROSPECT via Contact).
2. Hold a short back-and-forth (2+ turns). Confirm she answers in-thread and keeps Slack context.
3. Each turn should complete (not hang). Outcomes are structured **success** / **failure** / **concern** on the agent envelope (not free-form only).

**Concern path**
1. Message something that signals struggle / negative experience (confused, stuck, frustrated).
2. Confirm a **concern** outcome with a short admin aside (operator-visible note), not only a user-facing reply.

**Gates / debug**
1. With Manage Slack listen **off**, Estelle must not respond.
2. On non-production with listen on, outbound replies prefixed `[<environment>]`.
3. Optional: run touched Contact/Estelle paths with `debug=True` and confirm Style D index + `|` detail for turn outcomes.

Plans: `docs/features/contact/ast-1072-conversational-agent-envelope.md`, `docs/features/contact/ast-1073-contact-estelle-turn-loop.md`.

— Chuckles

#### susan — 2026-08-04T18:23:10.816Z
@chuckles How do I test this ticket?

#### chuckles — 2026-07-30T18:16:35.591Z
@susan linear-chuckles MCP dead after restart (session still has no linear-chuckles). AST-1072 UT; AST-1073 Plan Ready. Hard ban — will not use persona MCPs. — Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
