# AST-1630 — Update your check-linear watcher/skill to respond to fable and cursorapp

<!-- linear-archive: AST-1630 archived 2026-09-22 -->

## Linear archive (AST-1630)

**Archived:** 2026-09-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1630/update-your-check-linear-watcherskill-to-respond-to-fable-and  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Execution plan

1. Scope is **Linear user identity**, not email channels / inbound mail. Actions taken in the Linear workspace as **fable** or **cursorapp** (MCP or UI) must be treated like Susan’s for watcher gating. Match on those Linear users’ ids/emails only as API author keys — do **not** add email-ingestion support.
2. `[check]` **/** `check-linear`: today the mention inbox filters unreplied `@Chuckles` to Susan alone. Extend the Susan-equivalent author allow-set to include **fable** (`susan+fable@susansomerset.com`) and **cursorapp** (`susan+cursor@susansomerset.com`) alongside `susan@susansomerset.com`. Leave agent personas out.
3. `watch_linear.py`: replace single-email Susan checks with that allow-set (config + defaults) for mention-inbox fetch, unreplied-@Chuckles author match, and any `require_susan_last_comment` / last-commenter helpers that would otherwise ignore fable/cursorapp.
4. `watch_rules` **+ related rollcall helpers**: share the same allow-set so other Susan-authorship gates stay consistent; keep string `susanEmail` backward-compatible if needed.
5. Refresh `check-linear` **skill prose** so “FROM Susan” explicitly means Susan **or** fable **or** cursorapp as Linear comment authors.
6. Land in `team-chuckles`, run `install.sh` on the watcher host so the next poll cycle picks it up.

## Done when

* A fable or cursorapp `@Chuckles` comment (authored as that Linear user) in the lookback window triggers `[check]` the same way Susan’s does.
* No new email-channel / mail support is added.
* `install.sh` has been run on the server.

## Risks / open questions

* GraphQL comment `user.email` filter: prefer `in` over three fetches if the API supports it.
* Keep `susan+cursor@` out of Chuckles identity; only on the Susan allow-set.
* none else if fable + cursorapp are the full extra set.

---

## Original brief

I am working through the fable user so please update the watchers and skills to respond to updates made by fable and cursorapp as you would from me.

Then install the changes on your server so that the polls catch those new updates.

### Comments

#### chuckles — 2026-09-14T20:45:41.361Z
[check-linear] answered — pushed to origin/main

Yes — `team-chuckles` `origin/main` has `87b9446` (Susan allow-set for fable/cursorapp) and `63bb8d0` (docstring). `install.sh` ran; check watcher restarted at 20:45 and already picks up fable `@Chuckles` (e.g. AST-1629).

#### chuckles — 2026-09-14T20:45:34.296Z
[check-linear] answered — origin/main has the push (@susan)

Yes — `team-chuckles` `origin/main` tip is `63bb8d0` (allow-set + docstring); prior commit `87b9446` is the Susan/fable/cursorapp gate change. Local `main` matches remote.

#### susan — 2026-09-14T20:45:01.545Z
@chuckles did you push your changes to the main origin branch for team chuckles?

#### chuckles — 2026-09-14T20:32:22.745Z
[check-linear] answered — plan ready for Todo (@susan)

Yes. Scope is Linear users **fable** / **cursorapp** as comment authors (not email channels); the Description plan already matches that. Move AST-1630 to **Todo** and assign Chuckles when you want implement — `[task]` will pick it up.

#### susan — 2026-09-14T20:30:38.377Z
@chuckles see my comment above. I think this ready this ticket is ready to move to the to-do status?

#### susan — 2026-09-14T20:28:38.056Z
This isn't from email. This would be using an MCP to take actions within the linear workspace for our project. We don't need to support email from those sources. Just from the users themselves. Right now I believe the watcher is only watching for comments in check Linear for comments made by Susan and I need to extend that to include the users of fable and cursor app.

---

_Implementation detail may live in git history on `origin/dev`._
