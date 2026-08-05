# AST-1031 — Receive email on gmail account for astral

<!-- linear-archive: AST-1031 archived 2026-08-05 -->

## Linear archive (AST-1031)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1031/receive-email-on-gmail-account-for-astral  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** chuckles  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Susan needs an authenticated admin surface to prove Astral can **read** the product Gmail inbox via the Gmail API (send already exists for monitor alerts), and to leave that path in place as the **seed** for a later Meteorite ingest epic. The near-term outcome is: open a **Read email** nav item, see every inbox message (read and unread), click one, and inspect its HTML body in a scrollable modal.

## Functional scope

* Authenticated admins see a **Read email** nav item and can open a dedicated admin screen for inbox browsing.
* The screen lists every message currently in the Gmail inbox for `astral.career.match@gmail.com` (`GMAIL_USER`), including both read and unread messages, with enough identifying fields to choose one (at minimum subject, from, date, and read/unread).
* Selecting a listed message opens a scrollable modal that renders that message’s HTML body.
* Inbox access uses one OAuth client + **one refresh token** that covers **both** send and read scopes (`gmail.send` and `gmail.readonly`), via the existing env names `GMAIL_USER`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN` (optional `GOOGLE_TOKEN_URI`). Monitor send and inbox read share that single token.
* Live Gmail read (and send) calls honor the product controlled-external-I/O gate the same way other external network I/O does.

## Architectural definition

* **Patterns to reuse**
  * `pattern.ui.admin-endpoint` — auth-gated admin HTTP + thin API; React renders resolved payloads.
  * `pattern.layers.import-discipline` — UI must not call Gmail; external owns Gmail I/O; core orchestrates.
* **New patterns proposed** — none (extend the existing Gmail external module for read helpers under one dual-scope credential set).
* **Applicable statutes**
  * `astral.layers.core-vs-external-bright-line` — Gmail list/get stay in external; core orchestrates.
  * `astral.layers.import-direction` — ui → core; core → external; no ui→external.
  * `astral.patterns.require-auth-on-protected-endpoints` — Read email APIs and screen are protected admin surfaces.
  * `astral.config.secrets-and-env-specific-from-environ` — OAuth secrets and mailbox identity from environ only.
  * `astral.layers.ui-config-driven-business-logic` — admin UI stays thin; no inbox rules invented in React.
  * `universal` set applies to product code changes on this epic.
* **Env ownership (closed):** CSE uses `GOOGLE_CSE_API_KEY` and `GOOGLE_CSE_ID` only. Gmail OAuth uses `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN` (plus `GMAIL_USER`). Those OAuth `GOOGLE_*` names are **not** the CSE credentials — same Google Cloud project may host both, but the env keys and auth styles differ (API key + cx vs OAuth refresh).

## Boundaries

* Does **not** change the monitor alert **send** contract beyond sharing the dual-scope token; send must keep working.
* Does **not** ingest, classify, reply to, label, delete, archive, or otherwise mutate mailbox state beyond what is required to **display** messages (read-only preference for this epic).
* Does **not** build the full Meteorite ingest/routing product in this epic — **Read email** is the seed UI/API surface for that later work, not the ingest pipeline itself.
* Does **not** use IMAP/SMTP alternatives; Gmail API only.
* Does **not** persist email bodies into Astral data tables as part of this epic.
* Must not break existing external import-time Gmail env validation or controlled-I/O behavior for send.
* Must not repurpose or overwrite CSE env vars (`GOOGLE_CSE_API_KEY`, `GOOGLE_CSE_ID`) for Gmail OAuth.

## Acceptance criteria

1. An authenticated admin can open **Read email** from admin nav and see a list of inbox messages for `astral.career.match@gmail.com` (read and unread).
2. Clicking a listed message opens a scrollable modal showing that message’s HTML body as returned by Gmail.
3. Unauthenticated callers cannot access the list or message-body endpoints/screens.
4. Monitor alert email send still succeeds using the same single dual-scope `GOOGLE_REFRESH_TOKEN` after read ships.
5. With controlled external I/O disabled (integration/harness posture), live Gmail read is blocked the same way other gated external calls are — no silent live inbox hits from tests.

## Dependencies and blockers

* **Ops (before live UAT):** mint and install one `GOOGLE_REFRESH_TOKEN` whose scopes include both `https://www.googleapis.com/auth/gmail.send` and `https://www.googleapis.com/auth/gmail.readonly` (single token, not two). No sibling Linear blockers on Astral Meteorite.

## Open questions

none

## Proposed child tickets

#### 1!: **Gmail inbox read (external + core) - Ada**

Owns Gmail API list/get for `astral.career.match@gmail.com` (read + unread), returns message metadata and HTML body to callers, honors controlled-external-I/O, and uses **one** dual-scope OAuth token so existing send keeps working. Does **not** own admin nav or the React modal (child 2).
**Citations:** `pattern.layers.import-discipline`; `astral.layers.core-vs-external-bright-line`; `astral.config.secrets-and-env-specific-from-environ`.

#### 2: **Read email admin screen (ingest seed) - Hedy**

Owns authenticated admin API + **Read email** nav/screen: inbox list, click-through scrollable HTML body modal. Leaves this surface as the seed for a later Meteorite ingest epic (no ingest logic here). Does **not** own Gmail credential/scope plumbing (child 1). After #1.
**Citations:** `pattern.ui.admin-endpoint`; `astral.patterns.require-auth-on-protected-endpoints`; `astral.layers.ui-config-driven-business-logic`; `astral.layers.import-direction`.

## Git (authoritative — ignore Linear `gitBranchName`)

* [AST-1031](https://linear.app/astralcareermatch/issue/AST-1031/receive-email-on-gmail-account-for-astral) (parent): `ftr/AST-1031-receive-email-on-gmail-account-for-astral`
* [AST-1032](https://linear.app/astralcareermatch/issue/AST-1032/gmail-inbox-read-external-core-receive-email-on-gmail-account-for): `sub/AST-1031/AST-1032-gmail-inbox-read`
* [AST-1033](https://linear.app/astralcareermatch/issue/AST-1033/read-email-admin-screen-ingest-seed-receive-email-on-gmail-account-for): `sub/AST-1031/AST-1033-read-email-admin-screen`
* [AST-1040](https://linear.app/astralcareermatch/issue/AST-1040/uat-read-email-modal-shows-raw-html-source-not-rendered-preview): `sub/AST-1031/AST-1040-uat-read-email-modal-raw-html`

**Epic worktree:** `astral-AST-1031/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. Each entry is agent · role, then the fully-qualified `store.db` path (UUID is the directory name — extract for `agent --resume`). **datt resume:** read this list — not chat memory.

* **Ada** · engineer
  `/home/susan/.cursor/chats/a57e1c9a84f917887255ccc5aa4fdc54/a841fe6c-0779-484e-bf98-36da4ba4dc9a/store.db`
* **Hedy** · engineer
  `/home/susan/.cursor/chats/a57e1c9a84f917887255ccc5aa4fdc54/1435db58-ae87-4b74-8a59-a276592304c5/store.db`
* **Betty** · qa
  `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/1223ef33-6442-4b3f-a048-7a7c8d1a7715/store.db`
* **Radia** · review
  `/home/susan/.cursor/chats/a57e1c9a84f917887255ccc5aa4fdc54/e662e9ef-014e-40f7-be4d-6dc3efcb7417/store.db`

---

## Original brief

Using the gmail api (which I believe we already have set up), access the inbox, get each message, and display them on a temporary admin screen (nav item: 'read email').

Let me know what is already set up for environment variables and gmail account addresses (I think I registered [astralcareermatch@gmail.com](<mailto:astralcareermatch@gmail.com>)?)

I want the main screen to list the messages found in the inbox (read or unread), and when I click on one, I want a scrollable modal to display the HTML body of the selected email.

### Comments

#### chuckles — 2026-07-29T17:10:12.828Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-1040** | Read email modal shows raw HTML source not rendered preview |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-1040** — _Read email modal shows raw HTML source not rendered preview_
- **Issue reported:** On **Read email**, opening a message shows the HTML body as a **rendered browser view** inside the scrollable modal. Susan wants to see the **raw HTML source** in that panel instead.
- **Should now:** The scrollable modal shows the message’s HTML body **as raw source text** (as returned by Gmail), not as a live rendered email preview.
- **Quick check (this fix only):**
  1. Open admin **Read email**.
  2. Click any inbox message that has an HTML body.
  3. Observe the modal — content renders like a browser email view rather than raw markup.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### chuckles — 2026-07-29T16:59:51.987Z
@susan Filing **AST-1040** for the Read email modal: show **raw HTML source** instead of the iframe-rendered preview. That’s the remaining UAT product work on this epic (ops dual-scope OAuth token still needed for live inbox if not minted yet).

— Chuckles

#### susan — 2026-07-29T16:09:12.264Z
@chuckles This looks great, but I'm keen to see the raw html in the modal panel.  It's automatically rendering as a browser view.

#### susan — 2026-07-29T14:47:14.312Z
@chuckles What's left on this ticket?

#### chuckles — 2026-07-29T04:33:19.698Z
[thread-orphan] Joan session 2f96bb3a-9e52-4b2a-80a0-b832afadc55f relocated: /home/susan/.cursor/chats/0ab2adc851c7f84d4ce4bb00f485d83d/2f96bb3a-9e52-4b2a-80a0-b832afadc55f/store.db → /home/susan/.cursor/chats/a57e1c9a84f917887255ccc5aa4fdc54/2f96bb3a-9e52-4b2a-80a0-b832afadc55f/store.db

— Chuckles

#### chuckles — 2026-07-29T04:20:03.647Z
@susan

1. Confirm mailbox: `GMAIL_USER` is `astral.career.match@gmail.com` (not `astralcareermatch@gmail.com`) — read that inbox?
2. Approve minting a new OAuth refresh token with inbox read (`gmail.readonly` recommended) while keeping monitor send working? Current token/scope is `gmail.send` only.
3. Runtime env names already in use: `GMAIL_USER`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN` (optional `GOOGLE_TOKEN_URI`). Legacy `GMAIL_CLIENT_*` / `GMAIL_TOKEN_FILE` are unused by the module.
4. After UAT: remove **Read email**, leave it auth-gated, or seed a later Meteorite ingest epic?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
