# AST-791 — List of UAT issues in environment tooltip is not updating

<!-- linear-archive: AST-791 archived 2026-07-22 -->

## Linear archive (AST-791)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-791/list-of-uat-issues-in-environment-tooltip-is-not-updating  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** susan  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

The admin deploy footer environment tooltip ([AST-675](https://linear.app/astralcareermatch/issue/AST-675/create-a-ticket-log-in-utils) / [AST-691](https://linear.app/astralcareermatch/issue/AST-691/uat-env-label-hover-tooltip-pointer-cursor-05s-delay)) was built to surface recently landed parent epics. Susan UAT shows the list is stale: tickets that have finished UAT and moved to **Done** (e.g. **AST-741**) still appear after a fresh staging deploy. The tooltip should answer "which parent epics are on this deploy awaiting my UAT?" — not "everything ever prep-uat'd." That requires keeping the log in sync with Linear **User Testing** state and restoring Chuckles workflow docs so prep-uat and ship paths maintain the list correctly.

## Functional scope

* **User Testing filter:** The deploy-status ticket list exposed to the admin env-label tooltip includes only parent epic ids that are currently in Linear state **User Testing**. Parents in **Done**, **PR Ready**, or any other state are excluded. Most recent prep-uat first; up to **20** lines in the tooltip (unchanged UX from AST-691).
* **Stale entry cleanup:** One-time cleanup removes from the persisted merge ticket log any parent ids that are no longer **User Testing**, so a fresh deploy from `origin/dev` does not show finished epics (including **AST-741** and other **Done** parents currently in the log).
* **Ongoing lifecycle:** When **prep-uat** lands a parent on `dev`, that parent id is recorded (existing behavior). When a parent leaves **User Testing** (Susan moves to **PR Ready** or **finish-up** moves to **Done**), its id is removed from the active tooltip set so the list stays current without manual log edits.
* **Chuckles skills (team-chuckles):** Update **prep-uat** and any symmetric ship/finish path so the documented workflow matches the User Testing–only semantics Susan expects; publish to the **team-chuckles** repository.
* **Deploy status contract:** `GET /api/deploy_status` continues to expose the ticket array the footer consumes; the payload reflects the filtered **User Testing** set. Admin-only visibility, hover delay, line format (`AST-NNN` + timestamp), and non-admin behavior unchanged.

## Boundaries

* Does **not** change tooltip UX (500 ms hover, 20-line cap, pointer cursor, line format) beyond which tickets appear.
* Does **not** add ticket titles, assignees, or other Linear fields to the tooltip — id + timestamp only.
* Does **not** list child ticket ids — parent epic ids only.
* Does **not** show parents in **User Testing** on Linear that were never prep-uat'd to this deploy (no "global UAT inbox" — list is deploy-scoped via the merge ticket log, filtered by state).
* Must **not** break existing admin deploy footer fields (environment label, uptime, error handling).
* Supersedes [AST-675](https://linear.app/astralcareermatch/issue/AST-675/create-a-ticket-log-in-utils) acceptance that the tooltip shows all landed merge history regardless of Linear state; full historical audit trail in the log file is subject to open question #1 below.

## Acceptance criteria

1. After deploy from current `origin/dev`, hovering the admin environment label on staging shows **no** parent ids that are **Done** in Linear (including **AST-741** and other previously logged finished epics).
2. Every parent id shown in the tooltip is in Linear state **User Testing** at the time of the deploy-status request.
3. A parent prep-uat'd to staging while in **User Testing** appears in the tooltip with an updated timestamp; re-prep-uat of the same parent updates timestamp only (no duplicate lines).
4. When Susan moves a parent from **User Testing** to **PR Ready**, that parent disappears from the tooltip on the next deploy-status refresh without requiring a new deploy.
5. After **finish-up** moves a parent to **Done**, that parent does not appear in the tooltip.
6. When no logged parents are in **User Testing**, the env label is non-interactive (same as AST-691 empty-list behavior).
7. **prep-uat** and related Chuckles skill docs in **team-chuckles** describe User Testing–only maintenance; changes are pushed to that repo.
8. Non-admin navigation and deploy footer behavior outside the ticket list are unchanged.

## Dependencies and blockers

* [AST-675](https://linear.app/astralcareermatch/issue/AST-675/create-a-ticket-log-in-utils) (merge ticket log + deploy status) — shipped; this fix corrects semantics and lifecycle.
* [AST-691](https://linear.app/astralcareermatch/issue/AST-691/uat-env-label-hover-tooltip-pointer-cursor-05s-delay) (hover tooltip UX) — shipped; display layer unchanged.
* **prep-uat** / **finish-up** Chuckles skills — workflow updates ship with or immediately after product fix.
* none blocking start once open questions are answered.

## Open questions

none.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-791 (parent) | ftr/ast-791-list-of-uat-issues-in-environment-tooltip-is-not-updating |
| AST-792 | sub/AST-791/ast-792-user-testing-only-merge-ticket-log-and-deploy-status-filter |
| AST-798 | sub/AST-791/ast-798-uat-env-label-i-beam-cursor-and-no-tooltip-on-staging |
| AST-800 | sub/AST-791/ast-800-uat-tooltip-shows-only-ast-791-not-all-user-testing-parents-on-dev |

**Epic worktree:** `astral-AST-791/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | aad60062-bbcc-4b2c-91b7-07bdad351355 |
| Betty | qa | f0652ae2-aace-478d-bcb8-b7be89df951a |
| Radia | review | 386e70b3-a33f-44d2-8b3b-bf051e8daeb4 |

---

## Original brief

A fresh deploy from origin dev still shows 741 as the most recent update, as well as many other tickets that have since been set to Done.  This list should only include tickets in User Testing state.  If this got lost in the skill for prep-uat, please fix it and push it to the team-chuckles repository.

### Comments

#### chuckles — 2026-06-25T02:01:55.514Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-800** | tooltip shows only AST-791 not all User Testing parents on dev |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-800** — _tooltip shows only AST-791 not all User Testing parents on dev_
- **Issue reported:** On staging after AST-798 fix-uat, hovering the admin deploy footer environment label tooltip shows **only AST-791**, not every parent epic that has been landed on `origin/dev` and is in Linear **User Testing**.
- **Should now:** The tooltip lists **all** parent issue ids that (a) are in Linear **User Testing** at prep-uat time and (b) have their `ftr/*` branch merged into `origin/dev`, each with the timestamp of the latest dev commit for that feature. Parents whose `ftr` has **not** been merged to `origi
- **Quick check (this fix only):**
  1. Log in as admin on staging (deploy from current `origin/dev`).
  2. Hover the deploy footer environment label for ≥0.5s.
  3. **Observed:** tooltip shows only **AST-791** (one line).
  4. **Expected:** every User Testing parent whose feature is on `origin/dev` (e.g. other active UAT epics), not just this epic.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-06-25T01:43:26.791Z
Now it is only showing 791, instead of all the issues that have been committed to origin dev that are in User Testing status in linear.  Rethink the logging approach as part of prep-uat:

1. pull JUST the file containing the log list from origin dev.
2. get a fresh list of all the PARENT issue id's from Linear in "User Testing" status.
3. use the list issue ID's to verify that each one has been merged to origin/dev, and the timestamp of the latest commit for that feature.
4. Remove from the list any ID's where the ftr branch has NOT been merged into origin/dev
5. Make the log include JUST THAT LIST, and commit the log list file and merge it directly back to origin dev.

#### chuckles — 2026-06-25T01:37:30.694Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-798** | env label I-beam cursor and no tooltip on staging |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-798** — _env label I-beam cursor and no tooltip on staging_
- **Issue reported:** On staging after the AST-792 merge, hovering the admin deploy footer **environment label** shows an **I-beam (text) cursor** over the environment text and **no tooltip** appears. Susan reports this worked on **localhost** before the latest merge.
- **Should now:** With `ASTRAL_DEPLOY_ENV` set and admin session, hovering the environment label shows **pointer** cursor and, after **0.5 seconds**, a tooltip with up to **20** ticket lines (`AST-NNN` + timestamp) for parents currently in **User Testing** — same AST-691 UX as before this epic.
- **Quick check (this fix only):**
  1. Log in as admin on **staging** (fresh deploy from current `origin/dev` after AST-791 prep-uat).
  2. Open left nav deploy footer; locate the environment label (e.g. `staging`).
  3. Hover the environment text for ≥0.5s.
  4. **Observed:** I-beam cursor; no tooltip.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-06-25T01:25:13.696Z
The pointer is an ibar over the environment text, no tooltip appears, now.  This was working on localhost before the latest merge.

#### chuckles — 2026-06-24T22:47:02.556Z
@susan

1. **Log retention:** [AST-675](https://linear.app/astralcareermatch/issue/AST-675/create-a-ticket-log-in-utils) promised the persisted log would never truncate. For this fix, may entries be **removed** when parents leave **User Testing**, or must the full log be preserved with filtering applied only when building the deploy-status payload?

2. **Enforcement mechanism:** Is a runtime Linear state check on deploy-status reads acceptable, or must User Testing filtering be enforced solely by log add/remove in **prep-uat** / **finish-up** (no Linear API on each admin page poll)?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
