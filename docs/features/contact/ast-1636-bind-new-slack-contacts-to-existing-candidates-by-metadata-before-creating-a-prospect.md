# AST-1636 — Bind new Slack contacts to existing candidates by metadata before creating a prospect

<!-- linear-archive: AST-1636 archived 2026-09-24 -->

## Linear archive (AST-1636)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1636/bind-new-slack-contacts-to-existing-candidates-by-metadata-before  
**Status at archive:** Archive  
**Project:** Astral Contact  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / 8  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Contact must stop guessing who a Slack speaker is. Admins bind Slack identities to candidates on Manage Candidates (from a pool of workspace users who have posted somewhere). When someone talks to Estelle, resolve only answers "I know who that is" (already bound) or "I don't recognize you" (not bound) — no metadata auto-bind and no create-on-miss PROSPECT.

## Functional scope

* Fetch Slack users who have ever posted a message anywhere in the workspace via a new Slack Web API path from the external layer (workspace-wide posters — not a single channel's membership, and not "every workspace account" via raw `users.list` alone).
* Exclude posters whose Slack user id is already stored on any non-deleted candidate's contact fields; the remainder is the unbound pool.
* On the admin Manage Candidates page (add and edit), offer that unbound pool as a dropdown labeled by Slack username; selecting one binds that Slack user id and username onto the candidate being set up.
* Binding is admin-explicit only — no automatic metadata match inside `resolve_slack_user`.
* Change `resolve_slack_user` / the Estelle accept path so inbound Slack traffic only looks up an existing bind: known → Contact continues as that candidate and can acknowledge recognition; unknown → Contact does **not** create a PROSPECT and responds that it does not recognize the user.
* Out of scope: Manage Slack listen/debug/activity UI beyond what's needed for the above, Candidate Profile free-text Slack fields (remain unless a later ticket replaces them), and inbox email binding.

## Component scope

* `src/external/slack.py` — **modified** — new helper that derives Slack user ids (plus usernames) who have posted a message somewhere in the workspace; no outcome logging in external.
* `src/core/contact.py` — **modified** — unbound-pool orchestration for admin; `resolve_slack_user` lookup-only (retire create-on-miss PROSPECT); Estelle accept path posts known vs unknown recognition replies.
* `src/utils/config.py` — **modified** — `CONTACT_CONFIG` (or sibling) homes for known/unknown reply text templates; no bind-pool channel id.
* `src/ui/api/api_contact.py` — **modified** — admin-gated GET for unbound Slack users (bind via existing candidate write path preferred).
* `src/ui/frontend/src/pages/AdminManageCandidates.tsx` — **modified** — Slack username dropdown on add and edit; persists selected Slack user id + username.
* `src/core/candidate.py` — **unchanged** unless bind must reuse an existing public save entry (prefer `save_candidate_data` — no new candidate-table scanner).

## Technical scope

* `src/external/slack.py`: new function building the workspace poster pool (unique user id + username), gated by `require_controlled_external_io`; exact Slack method mix is `plan-child`'s call — must not use `conversations.members` on a configured channel as the pool, and must not treat raw `users.list` alone as "has posted"; bots/deleted excluded by default.
* `src/core/contact.py`: unbound list = external posters minus candidates' `contact.slack_user_id`; `resolve_slack_user` returns matched candidate or unbound with `created=False` and never calls `initiate_prospect_candidate`; handle/accept path posts recognition reply for known vs unknown (config templates).
* `src/utils/config.py`: add reply-text keys for known and unknown recognition (defaults matching Susan's wording: "I know who that is" / "I don't recognize you"); keep existing Slack env-name contracts.
* `src/ui/api/api_contact.py`: `@require_admin` GET returning the unbound list JSON.
* `src/ui/frontend/src/pages/AdminManageCandidates.tsx`: load unbound list on add/edit; dropdown by username; save stamps `contact.slack_user_id` + `contact.slack_username`.

## Architectural definition

* **Patterns to reuse** — `no established pattern applies` (in-force patterns are batch/daisy-chain/dispatch-retry only; admin Contact routes already follow the local `@require_admin` thin-wrapper shape without a harvested pattern id).
* **New patterns proposed** — none.
* **Applicable statutes**
  * [`stat.logging.info.contact`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.contact.md>) — Contact progress stays listen + Estelle action notes; recognition replies must not invent a parallel info dialect.
  * [`stat.logging.info.api`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.api.md>) — admin route progress logs once at the completing route.
  * [`stat.logging.debug`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md>) — debug-gated detail when debug is on.
  * [`stat.logging.error`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.error.md>) — Slack list / bind / reply failures log once at the handler with live facts + traceback.

## Acceptance criteria

 1. `rg -n "initiate_prospect_candidate" src/core/contact.py` shows no call from `resolve_slack_user` (create-on-miss retired). Fail if resolve still creates a PROSPECT on Slack user id miss.
 2. With a Slack user id already on a candidate: Estelle inbound resolve returns that candidate, `created=False`, and Contact posts the known-recognition reply (config default: "I know who that is"). Fail if unknown-reply is posted or a new candidate appears.
 3. With a Slack user id not on any candidate: resolve returns no candidate, `created=False`, Contact posts the unknown-recognition reply (config default: "I don't recognize you"), and no PROSPECT row is created. Fail if a prospect is minted or Estelle continues as if bound.
 4. Admin GET unbound Slack users returns only workspace posters whose id is not on any non-deleted candidate's `contact.slack_user_id`. Fail if an already-bound id appears.
 5. Manage Candidates add/edit: unbound usernames in a dropdown; save with a selection persists `contact.slack_user_id` and `contact.slack_username`. Fail if already-bound usernames appear or selection does not stamp both fields.
 6. After bind, unbound list omits that Slack user. Fail if they remain selectable for another candidate.
 7. External poster pool lives in `src/external/slack.py`, invoked from core/API — not from React. Fail if `AdminManageCandidates.tsx` hardcodes Slack Web API URLs/tokens.
 8. New admin routes use `@require_admin`. Fail if unbound-list is reachable without admin auth.
 9. Bots and deleted Slack users are absent from the dropdown. Fail if `is_bot` or deleted users appear.
10. Pool source is workspace posters — not `conversations.members` on a configured channel, and not raw `users.list` alone. Fail if channel-membership is the pool or "all accounts" equals "has posted" without a poster-derived set.

## Open questions

none

## Proposed child tickets

#### 1!: **Workspace poster pool (external) - Ada**

Owns the Slack external helper that derives workspace users who have posted a message (id + username), excluding bots/deleted. Does not own Contact unbound filtering, resolve, admin GET, or Manage Candidates UI.
**Citations:** `stat.logging.debug`, `stat.logging.error`.
**Scope:** `src/external/slack.py` — new workspace-poster helper only.
**Estimate: 3**

#### 2!: **Contact unbound list + known/unknown resolve - Hedy**

Owns Contact orchestration: unbound pool (external posters minus bound ids), admin GET, retiring create-on-miss in `resolve_slack_user`, and known/unknown recognition replies (config templates). Does not own the external poster fetch implementation or Manage Candidates UI. After #1.
**Citations:** `stat.logging.info.contact`, `stat.logging.info.api`, `stat.logging.debug`, `stat.logging.error`.
**Scope:** `src/core/contact.py` — unbound orchestration + `resolve_slack_user` lookup-only + recognition reply wiring; `src/utils/config.py` — known/unknown reply text keys; `src/ui/api/api_contact.py` — admin GET unbound users. `src/core/candidate.py` unchanged unless existing save entry must accept bind fields.
**Estimate: 5**

#### 3: **Manage Candidates Slack bind dropdown - Katherine**

Owns the Manage Candidates add/edit Slack username dropdown and persisting selected Slack id + username via the existing candidate write path. Consumes sibling #2's GET. Does not own resolve recognition or the poster helper.
**Citations:** `stat.logging.info.api`, `stat.logging.error`.
**Scope:** `src/ui/frontend/src/pages/AdminManageCandidates.tsx` — dropdown on add/edit; `src/ui/api/api_candidate.py` / existing candidate create+data PUT — only if bind payload must be accepted there. Candidate Profile Slack text fields unchanged.
**Estimate: 2**

**Monolith check:** Functional scope has 6 capabilities; 3 children (external poster pool, contact resolve+unbound API, Manage Candidates UI) — intentional across layers.
**Scope partition check:** `slack.py` → #1; `contact.py` + reply config + `api_contact.py` → #2; `AdminManageCandidates.tsx` (+ candidate write if needed) → #3. Each file in exactly one child.

---

## Original brief

Today, `resolve_slack_user` in `src/core/contact.py` only checks whether the incoming Slack user ID is already stored on a candidate's contact fields. If there's no match, it immediately calls `fetch_user_profile` and creates a brand new PROSPECT candidate, stamping the Slack user ID onto it.

This skips a step: before creating a new candidate, we should try to bind this Slack user to an *existing* candidate using the metadata Slack gives us (first name, last name, display name, username), in case that person already exists in the candidate table under a different identity.

Proposed direction: add a "get candidate by metadata" lookup function, likely belonging on the candidate core/service layer, that attempts to match an existing candidate by name (and any other available metadata) before falling back to creating a new prospect. When a match is found, bind the Slack user ID onto that existing candidate's contact fields instead of creating a duplicate.

Note: `fetch_user_profile` currently returns first, last, display name, and username — no email is available from this Slack call, so matching will need to work with name-based metadata unless another data source is added.

### Comments

#### chuckles — 2026-09-21T00:16:50.431Z
[fix-intake] filed AST-1739 at Discussion (assignee Susan) — empty Slack username dropdown on Manage Candidates

#### susan — 2026-09-21T00:15:24.512Z
\[bug\] When I open the Manage Candidate modal, when I click on the Slack username dropdown, I expect to see a list of all users on the astral slack workspace, but I don't see any. Thus, I am unable to assign known users to their candidate records.

#### chuckles — 2026-09-16T01:34:38.074Z
[check-linear] Todo — confirmed: resolve is lookup-only (known: "I know who that is" / unknown: "I don't recognize you"); no create-on-miss PROSPECT; admin Manage Candidates bind remains

#### susan — 2026-09-15T23:58:42.707Z
This issue has been through a lot of discussion but I would love to get confirmation that we are updating the binding function to just say "this slack user is talking to us" and for contact to respond with "I know who that is" or "I don't recognize you." @chuckles

#### chuckles — 2026-09-15T22:34:25.229Z
[check-linear] Discussion — definition revised to workspace poster pool; Open questions none (@susan)

#### fable — 2026-09-15T22:32:24.406Z
@chuckles Susan has changed the approach: drop the channel-membership pool entirely. The bind pool should be every Slack workspace user who has ever posted a message anywhere in the workspace, minus anyone already bound to a candidate — not `conversations.members` on a configured channel.

Please revise Component scope, Technical scope, and Acceptance criteria (including the "conversations.members, not workspace users.list" line in Acceptance criterion 8, which now inverts) to fetch/derive that workspace-wide posted-message pool instead, and drop Open question 1 about the channel id/env key since it no longer applies.

#### chuckles — 2026-09-15T12:09:44.132Z
@susan
1. Which Slack channel id is the bind pool, and where does it live — e.g. environ name on `CONTACT_CONFIG` (like `bot_token_env`), or a literal? Please name the env key and/or the channel id.

#### chuckles — 2026-09-15T12:06:50.897Z
@susan
1. Slack source of the pool: workspace-wide (`users.list`), or members of a specific channel (`conversations.members`)? If channel — which channel id, and where does it live in config/env?

#### susan — 2026-09-15T12:03:20.598Z
actually no.  Let's not have an ai assert a bind with the candidate.  Instead, let's just have an admin screen in the ui that can bind slack users to candidates. It should be part of the initial user setup. 

Create an api call to slack that will fetch all the users on the slack channel, then for all the users found, remove those who are already matched with candidates and offer that list by slack username in a dropdown select on the manage candidate page.

#### chuckles — 2026-09-15T01:39:01.997Z
@susan
1. Which Slack profile fields, in which order, may bind? Candidates: constructed `first`+`last` / `full`, `display_name`, `username`. May a lone `first` or lone `last` ever bind, or are single-token name hits forbidden?
2. On ambiguous metadata (2+ candidates): treat as miss and create PROSPECT (when Estelle in play), or refuse create and return unbound?
3. Should `contact.slack_username` be added to `CANDIDATE_LOOKUP_CONFIG` so username can bind against previously stamped Slack handles, or is username matching out of scope for this epic?

#### chuckles — 2026-09-15T01:38:27.197Z
No dedicated "get candidate by metadata" function exists today.

Closest reuse: `get_candidate_id_for_query` in `src/core/candidate.py`, driven by `CANDIDATE_LOOKUP_CONFIG` (`email_paths` / `email_list_paths` / `name_paths` = `first`/`last`/`full` (+ transitional profile name paths) / `slack_user_id_paths`). It takes one string needle and returns an id only on a unique hit (ambiguous or none → `None`).

`resolve_slack_user` already uses that helper for the Slack user id; on miss it goes straight to `fetch_user_profile` + `initiate_prospect_candidate`. There is no structured multi-field metadata matcher, and `contact.slack_username` is not on the lookup vocabulary.

Recommendation for the definition: reuse/extend that lookup + config surface rather than a parallel matcher — exact match-field policy called out in Open questions.

#### fable — 2026-09-15T01:38:15.221Z
Scope note: if this function doesn't already exist, it should be built as a general-purpose "get candidate by metadata" function on the candidate core, not something specific to the Slack path. It needs to support matching by whatever metadata is available at the call site — for Slack that's name-based fields (first, last, display, username), but the email inbox parsing flow (separate scope from Contact) will need to bind candidates by email through this same function/endpoint. One shared lookup, not separate one-off matching logic per integration.

#### fable — 2026-09-15T01:36:24.849Z
Before scoping this further: is there already a "get candidate by metadata" (or similarly-purposed) function exposed on the candidate core file? If so, can we reuse or extend it here rather than building a new one from scratch? You can see the full candidate service code, so wanted your read on what already exists before we lock in the approach.

---

_Implementation detail may live in git history on `origin/dev`._
