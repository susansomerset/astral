# AST-675 — Create a ticket log in utils

<!-- linear-archive: AST-675 archived 2026-06-23 -->

## Linear archive (AST-675)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-675/create-a-ticket-log-in-utils  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Administrators deploying Astral need to see which Linear tickets are represented in the live build, not only the current git tip. The admin deploy footer ([AST-646](https://linear.app/astralcareermatch/issue/AST-646/deploy-status-api-and-admin-nav-footer-show-environment-and-up-time-as)) already shows environment, short commit hash, and uptime; Susan wants a durable, human-readable merge history so hovering the environment label answers "what ticket work is in this deploy?" without digging through git. A utils-maintained log keeps that history in the repo and ships with each release.

## Functional scope

* **Merge ticket log (utils):** A persisted log in the utils layer records Linear parent ticket identifiers landed on `dev`, ordered by when each entry was recorded (append-only). Each entry includes the ticket id (e.g. `AST-675`) and the timestamp when the recording tool ran. The file retains **full history** (no truncation of stored entries). SHA is **not** stored per entry.
* **Utils tool to maintain the log:** A new utils-layer tool appends one entry per invocation. It is the sole writer of the log; runtime UI reads only. `finish-up` invokes this tool automatically after each successful parent land on `dev`, appending the **parent epic issue id** for that finish-up run.
* **Deploy status surfacing:** The existing admin deploy-status payload exposes the ticket list needed for the tooltip (most recent entries first). The API may return the full stored history or a bounded slice; the UI tooltip uses at most the **20 most recent** entries.
* **Admin nav tooltip:** On the left nav admin deploy footer, hovering the **environment label** (the value from `ASTRAL_DEPLOY_ENV`, when shown) displays a tooltip listing up to **20** logged tickets with timestamps and line breaks between entries. Same ticket list applies whether the running deploy is staging (`dev`) or production (`main`) — production is updated less often but shows the same accumulated history.
* **No initial backfill:** The log starts empty and accumulates from first use after ship.

## Boundaries

* **No SHA** in log entries or tooltip.
* **Admin-only** — same visibility gate as the deploy footer (`is_admin`).
* **No runtime git mining** on each page load or API call.
* **No Linear API** calls to resolve ticket titles or states; display is ticket id + timestamp only.
* **Does not replace** the existing commit-short tooltip on the commit hash.
* **Child ticket ids are not logged** — only the parent epic id passed through finish-up.
* **No debug-logging contract** ([AST-538](https://linear.app/astralcareermatch/issue/AST-538/improve-quality-of-debug-logging)) — deploy metadata only.

## Acceptance criteria

1. After finish-up lands a parent on `dev`, the persisted log contains a new entry with that parent's Linear id and the tool-run timestamp; prior entries remain in the file.
2. The log file is never truncated — all historical entries are preserved after each append.
3. `GET /api/deploy_status` for an authenticated admin includes ticket history sufficient to render the tooltip (empty when log is empty).
4. With `ASTRAL_DEPLOY_ENV` set and admin session, hovering the environment label shows up to **20** ticket lines (id + timestamp), most recent first, separated by line breaks.
5. When the environment label is absent, ticket history is still available via deploy status; no environment-hover tooltip is required.
6. Non-admin navigation is unchanged.
7. Existing deploy footer fields (commit short, commit message tooltip, uptime) behave as before [AST-675](https://linear.app/astralcareermatch/issue/AST-675/create-a-ticket-log-in-utils).
8. No backfill from git history — first entry appears only after the first post-ship finish-up that invokes the tool.

## Dependencies and blockers

* [AST-646](https://linear.app/astralcareermatch/issue/AST-646/deploy-status-api-and-admin-nav-footer-show-environment-and-up-time-as) (deploy status API and admin nav footer) — shipped; this feature extends that surface.
* **finish-up** (`finish-up-land.sh`) — must call the utils tool after successful land (wired as part of this epic).
* None blocking start.

## Open questions

none.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| [AST-675](https://linear.app/astralcareermatch/issue/AST-675/create-a-ticket-log-in-utils) (parent) | ftr/ast-675-create-a-ticket-log-in-utils |
| [AST-681](https://linear.app/astralcareermatch/issue/AST-681/merge-ticket-log-and-deploy-status-api-create-a-ticket-log-in-utils) | sub/AST-675/ast-681-merge-ticket-log-and-deploy-status-api |
| [AST-682](https://linear.app/astralcareermatch/issue/AST-682/admin-environment-ticket-tooltip-create-a-ticket-log-in-utils) | sub/AST-675/ast-682-admin-environment-ticket-tooltip |
| [AST-683](https://linear.app/astralcareermatch/issue/AST-683/finish-up-auto-record-landed-parent-create-a-ticket-log-in-utils) | sub/AST-675/ast-683-finish-up-auto-record-landed-parent |
| [AST-690](https://linear.app/astralcareermatch/issue/AST-690/uat-env-label-click-popup-for-merge-ticket-list) | sub/AST-675/ast-690-uat-env-label-click-popup-for-merge-ticket-list |
| [AST-691](https://linear.app/astralcareermatch/issue/AST-691/uat-env-label-hover-tooltip-pointer-cursor-05s-delay) | sub/AST-675/ast-691-uat-env-label-hover-tooltip-pointer-cursor-05s-delay |

| AST-693 | sub/AST-675/ast-693-uat-staging-env-label-noninteractive-merge-tickets-empty-on-deploy |

**Epic worktree:** `astral-AST-675/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Katherine | engineer | c512c160-1368-443a-880b-8cf9e5eb493f |
| Betty | qa | cc801086-a9e8-4744-8a21-f677abbb69f0 |

---

## Original brief

I want to start tracking the tickets that have been merged to main in order by their merge time, and for the last 10 tickets to be merged, with timestamps and linebreaks, in a tooltip when I over over the astral_display_env on the left nav pane so I can see which tickets have been merged into the deployed version.  This will need a new tool in utils, and I'm okay with that.

Note, we do not need to include the SHA for this, because we won't know the SHA before committing the changed utils file.

### Comments

#### chuckles — 2026-06-16T01:10:56.995Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-693** | staging env label non-interactive — merge_tickets empty on deploy |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-693** — _staging env label non-interactive — merge_tickets empty on deploy_
- **Issue reported:** After **AST-691** landed on staging (deployment notes cite `merge-tests(AST-691)`), Susan UAT on staging shows the admin deploy footer rendering **non-interactive** markup — no `nav-deploy-env-interactive` class, no pointer cursor, no hover tooltip:
- **Should now:** With `ASTRAL_DEPLOY_ENV` set and admin session on staging, hovering the environment label shows **pointer** cursor and, after **0.5 seconds**, a tooltip with up to **20** ticket lines (most recent first).
- **Quick check (this fix only):**
  1. Log in as admin on **staging** after AST-691 deploy.
  2. Open left nav deploy footer; inspect DOM for env label.
  3. **Observed:** plain `nav-deploy-env` with text `staging`; no interactive class; no tooltip on hover.
  4. **Expected:** pointer cursor; after 0.5s hover, tooltip lines as above when tickets are logged.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-06-16T00:53:51.531Z
```
<div class="nav-deploy-footer" aria-label="Deploy status"><span class="nav-deploy-env-wrap"><span class="nav-deploy-env">staging</span></span><span class="nav-deploy-sep">·</span><span class="nav-deploy-uptime">11m</span></div>
```

This is what is rendering on staging right now, and the deployment description said: `merge-tests(AST-691)…`

#### chuckles — 2026-06-16T00:35:41.871Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-691** | env label hover tooltip pointer cursor 0.5s delay |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-691** — _env label hover tooltip pointer cursor 0.5s delay_
- **Issue reported:** After AST-690 (click popup), staging still fails Susan's UAT: the deploy footer environment label shows an **I-beam (text) cursor** instead of a pointer, and Susan does not get a reliable hover tooltip. The click-popup interaction is not what she wants.
- **Should now:** * **Cursor:** `pointer` (hand) on the environment label when merge tickets exist — never I-beam/text cursor.
- **Quick check (this fix only):**
  1. Log in as admin on staging with `ASTRAL_DEPLOY_ENV` set (e.g. `dev`) and at least one entry in merge ticket log.
  2. Open left nav deploy footer; hover the environment label.
  3. **Observed:** I-beam cursor; click popup from AST-690 — not a 0.5s hover tooltip.
  4. **Expected:** pointer cursor; after 0.5s hover, tooltip shows lines like `AST-675 6/15/26, 1:23:45 PM` (up to 20).

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-06-15T20:42:58.856Z
@chuckles This still isn't working.  I don't want an I-bar, I want a pointer, and I would prefer a tooltip that pops up after 0.5 seconds to show the set of issues.  When you take another swing at this, please include EXACTLY what the text should look like in the tooltip/popup.

#### chuckles — 2026-06-15T20:32:23.239Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-690** | env label click popup for merge ticket list |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-690** — _env label click popup for merge ticket list_
- **Issue reported:** With `ASTRAL_DEPLOY_ENV` set and an admin session on staging, the deploy footer environment label shows a text (I-beam) cursor on hover and **no** merge-ticket list appears — the native `title` tooltip does not surface ticket history.
- **Should now:** Admin can see up to **20** most recent logged parent tickets (id + timestamp), most recent first, with line breaks between entries — via an obvious click interaction on the environment label (popup/list), per Susan UAT feedback.
- **Quick check (this fix only):**
  1. Log in as admin on staging with `ASTRAL_DEPLOY_ENV` set (e.g. `dev`).
  2. Open left nav; locate the deploy footer environment label.
  3. Hover the environment string — I-beam cursor; no ticket list appears.
  4. Susan expects click on the environment label to open a small popup/list of logged tickets.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-06-15T20:07:43.015Z
deploy environment has an I-bar cursor, and no tooltip appears.  Maybe just create a little list in a popup message box with the issues when the user clicks on the astral_deploy_env string?  Like a button?

#### chuckles — 2026-06-15T19:13:26.842Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-675 (parent) | ftr/ast-675-create-a-ticket-log-in-utils |
| AST-681 | sub/AST-675/ast-681-merge-ticket-log-and-deploy-status-api |
| AST-682 | sub/AST-675/ast-682-admin-environment-ticket-tooltip |
| AST-683 | sub/AST-675/ast-683-finish-up-auto-record-landed-parent |

**Epic worktree:** `astral-AST-675/` — one active sub checked out at a time.

**Parent:** AST-675

— Chuckles

#### chuckles — 2026-06-15T18:05:30.615Z
@susan — open questions (answer in thread or edit brief; I'll update the definition):

1. Which branch feeds the log — `main`, `dev`, or env-specific?
2. When should the utils tool run?
3. How is the ticket id chosen per entry?
4. What timestamp should be shown?
5. Backfill from git history or start empty?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
