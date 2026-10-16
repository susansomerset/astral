# AST-1786 — Manage Candidates Snapshot Slack Channel + candidate mapping

<!-- linear-archive: AST-1786 archived 2026-10-07 -->

## Linear archive (AST-1786)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1786/manage-candidates-snapshot-slack-channel-candidate-mapping  
**Status at archive:** Archive  
**Project:** Astral Contact  
**Assignee:** chuckles  
**Priority / estimate:** High / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Admins need a stopgap way to see which Slack identity and channel belong to each candidate on Manage Candidates, and to pull that channel’s message history into the clipboard as JSON — until Estelle’s Slackbot can own the same job. Wrong channel assignment is expensive; the UI must warn when the bound Slack user is not a member of the chosen channel (including when no Slack user is bound yet).

## Functional scope

* Show the candidate’s currently selected Slack username as a column on Manage Candidates (from existing `contact.slack_username` / bind — display only in the list).
* Let an admin select and persist a Slack channel onto the candidate’s profile contact data; surface that association on Manage Candidates (and Candidate Profile shapes) so the stored channel is visible after save.
* When selecting a channel, warn if the candidate’s bound Slack user id is not a member of that channel, or if no Slack user is bound yet — selection may still proceed, but the warning must be unmistakable so Admin does not assign the wrong channel by accident.
* Provide an **S** icon-control on each Manage Candidates row that fetches all messages from the candidate’s stored Slack channel (date-order ascending), builds a JSON document, and copies it to the clipboard. Stopgap only — not Estelle conversational behavior.
* Out of scope: changing Estelle listen/resolve/recognition, Manage Slack activity UI, rebinding Slack username (already shipped), and inventing a parallel Slack Web API client in React.

## Component scope

* `src/external/slack.py` — **modified** — helpers to list bot-visible channels for picker, check whether a given Slack user id is a member of a channel, and fetch full channel message history ascending (paginated); no outcome `logger.info` in external.
* `src/core/contact.py` — **modified** — thin orchestration calling those external helpers for admin channel-list / membership / snapshot (ui → core → external); no Estelle turn-loop changes.
* `src/ui/api/api_contact.py` — **modified** — admin-gated routes for channel list, membership check, and channel message snapshot JSON.
* `src/utils/config.py` — **modified** — `DATA_SHAPES` Manage Candidates list column for Slack username; Candidate Profile contact fields for stored Slack channel id + name (mirror existing slack_user_id / slack_username pairing).
* `src/ui/frontend/src/pages/AdminManageCandidates.tsx` — **modified** — Slack username column, channel select with membership warning, **S** icon-control that loads snapshot via admin API and writes JSON to clipboard.
* `src/ui/frontend/src/pages/CandidateProfile.tsx` — **unchanged** unless shapes-driven profile already renders new contact fields without page edits; do not add a parallel free-text channel editor outside shapes.

## Technical scope

* `src/external/slack.py`: new (or extended) functions — list channels the bot can see (reuse / extend the existing conversations.list pagination shape already used for poster scan); membership check for one `slack_user_id` in one `channel` (Slack membership API is appropriate here — distinct from the AST-1667 ban on using `conversations.members` as the *poster pool*); full history pagination returning messages oldest→newest for clipboard dump (existing limited `fetch_conversation_history` is not sufficient alone). Gate with `require_controlled_external_io`; soft-skip / hard-fail rules follow existing Slack helper norms; `logger.debug` at loop joints only.
* `src/core/contact.py`: orchestration entry points that call the external helpers and return plain data for API (channel options; membership bool + reason when unbound; ordered message list / snapshot payload). No React tokens; no Estelle accept-path edits.
* `src/ui/api/api_contact.py`: `@require_admin` GET (or equivalent thin routes) for channel options, membership check against a candidate’s bound Slack user + chosen channel, and snapshot JSON for a candidate’s stored channel; one completing-route progress info line per statute.
* `src/utils/config.py`: add list.manage column key for Slack username (fed from flattened `contact.slack_username`); add profile contact fields `contact.slack_channel_id` + `contact.slack_channel_name` (labels suitable for admin). Persist via existing candidate create / data PUT deep-merge — no new candidate writer.
* `src/ui/frontend/src/pages/AdminManageCandidates.tsx`: render Slack username from contact; channel `<select>` on add/edit (options from admin channel list); on change / before save, call membership check and show warning when unbound or not a member; stamp both channel id + name on save like Slack bind; row **S** `icon-control` calls snapshot API then `navigator.clipboard.writeText(JSON.stringify(...))` (same family as job snapshot / other admin clipboard copies). No Slack URLs/tokens in TSX.

## Architectural definition

* **Patterns to reuse** — `no established pattern applies` (in-force harvested patterns are batch / daisy-chain / dispatch-retry / artifact; admin Contact routes already follow the local `@require_admin` thin-wrapper shape without a harvested pattern id).
* **New patterns proposed** — none.
* **Applicable statutes**
  * [`stat.logging.info.api`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.api.md>) — admin channel-list / membership / snapshot routes log once at the completing route.
  * [`stat.logging.debug`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md>) — debug-gated detail on Slack pagination / membership loops when debug is on.
  * [`stat.logging.error`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.error.md>) — Slack / handler failures log once with live facts + traceback.

## Acceptance criteria

 1. Manage Candidates list shows a Slack username column whose cell equals `candidate_data.contact.slack_username` when set, and a clear empty/placeholder when unset. Fail if the column is missing or shows a different candidate’s username.
 2. Add/edit can select a Slack channel from bot-visible channels; save persists both `contact.slack_channel_id` and `contact.slack_channel_name` on the candidate. Fail if only one field is stamped or if React calls Slack Web API directly.
 3. Selecting a channel when the candidate has no `contact.slack_user_id` shows a membership warning (selection still allowed). Fail if there is no warning in that case.
 4. Selecting a channel when the bound Slack user is not a member of that channel shows a membership warning (selection still allowed). Fail if a non-member selection is silent.
 5. Selecting a channel when the bound Slack user **is** a member does not show that warning. Fail if member selection still warns.
 6. Row **S** icon-control (shared `icon-control` class, label/aria includes Snapshot/Slack channel) fetches the stored channel’s messages via admin API and copies JSON to the clipboard with messages in ascending date order. Fail if order is descending, if messages are truncated to a single page when more exist, or if the button is a non-`icon-control` one-off.
 7. Snapshot / channel / membership admin routes require admin auth. Fail if reachable without `@require_admin`.
 8. External Slack I/O for list / membership / history lives in `src/external/slack.py` and is reached from core/API — not from `AdminManageCandidates.tsx`. Fail if TSX hardcodes Slack API URLs or bot tokens.
 9. `rg -n "conversations.members" src/external/slack.py` may match the **membership-check** helper for a known user+channel; it must not be used as a workspace poster/user pool source. Fail if membership enumeration replaces `_iter_conversations` / poster-pool logic.
10. Candidate Profile shapes expose the new Slack channel fields under Contact Information (id + name). Fail if `DATA_SHAPES["candidates"]["detail"]["profile"]` contact fields omit both keys after ship.

## Open questions

none

## Proposed child tickets

#### 1!: **Slack channel list, membership, and full history (external) - Ada**

Owns external helpers: bot-visible channel list for picker, per-user channel membership check, and paginated full-channel history ascending for snapshot. Does not own Contact orchestration, admin routes, shapes, or Manage Candidates UI.
**Citations:** `stat.logging.debug`, `stat.logging.error`.
**Scope:** `src/external/slack.py` — channel list / membership / full history ascending helpers only (extend or complement limited `fetch_conversation_history` as needed).
**Estimate: 3**

#### 2!: **Contact admin channel APIs + shapes - Hedy**

Owns Contact orchestration + admin GET routes for channel options, membership check, and message snapshot JSON; plus `DATA_SHAPES` list column for Slack username and profile contact fields for channel id/name. Persists through existing candidate write path (no new writer). Does not own external Slack method bodies or Manage Candidates React. After #1.
**Citations:** `stat.logging.info.api`, `stat.logging.debug`, `stat.logging.error`.
**Scope:** `src/core/contact.py` — channel-list / membership / snapshot orchestration; `src/ui/api/api_contact.py` — `@require_admin` routes; `src/utils/config.py` — Manage list Slack username column + profile `contact.slack_channel_id` / `contact.slack_channel_name`.
**Estimate: 3**

#### 3: **Manage Candidates channel column, select warning, S snapshot - Katherine**

Owns Manage Candidates UI: Slack username column, channel select with membership warning, **S** icon-control clipboard snapshot via sibling APIs. Does not own external helpers or admin route bodies. After #2.
**Citations:** `stat.logging.info.api`, `stat.logging.error`.
**Scope:** `src/ui/frontend/src/pages/AdminManageCandidates.tsx` — username column, channel select + warning, **S** clipboard; `src/ui/frontend/src/pages/CandidateProfile.tsx` — only if shapes-driven render needs a page touch (prefer none).
**Estimate: 2**

**Monolith check:** Functional scope has 4 capabilities; 3 children (external Slack I/O, Contact/API/shapes, Manage Candidates UI) — intentional across layers.
**Scope partition check:** `slack.py` → #1; `contact.py` + `api_contact.py` + `config.py` → #2; `AdminManageCandidates.tsx` (+ CandidateProfile only if required) → #3. Each file in exactly one child.

---

## Original brief

On the Manage Candidates page, add a column for the selected Slack username for the candidate. Then, let's add a link to their slack channel, stored in their candidate profile data, that I can select from with a warning if the user is not already a member of the selected channel.  This is okay to happen when a candidate hasn't logged in yet, but important to indicate so that Admin doesn't assign the wrong channel accidentally.

Then add an S icon button to pull Slack channel content, using the slack API, create a json of all the messages posted in that channel in date-order ascending, and copy it to the clipboard.  This is a stop-gap measure until we have the Estelle slackbot fully functioning.

### Comments

#### susan — 2026-09-27T06:03:36.182Z
Yes, they're fine, you can close the epic out.

#### chuckles — 2026-09-27T06:02:53.756Z
@susan finish-up blocked: PR #132 is already merged, but the AST-1786 refs were moved to `contact/ftr/…` and `contact/sub/…`, and finish-up-land.sh only finds `ftr/…`. Is the `contact/` prefix intentional? If yes, OK to delete those four refs and close the epic out?

#### chuckles — 2026-09-24T19:24:23.181Z
AST-1789 REVIEW — merge-child blocked; recalling Katherine to restack sub on origin/ftr/AST-1786-manage-candidates-snapshot-slack-channel (Merge remote-tracking via sync(ftr) first-parent).

#### chuckles — 2026-09-24T19:05:35.969Z
AST-1788 REVIEW — merge-child blocked; recalling Hedy for polluted sync(ftr) first-parent (Merge remote-tracking on sub).

---

_Implementation detail may live in git history on `origin/dev`._
