# AST-744 — Remove column gap in scheduled_actions

<!-- linear-archive: AST-744 archived 2026-06-23 -->

## Linear archive (AST-744)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-744/remove-column-gap-in-scheduled-actions  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

There is a gap of whitespace between the Candidate and Task columns, and task and entity are shifted to the right, overlaying (and blocking) the State column value.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-744 (parent) | ftr/AST-744-remove-column-gap-in-scheduled-actions |
| AST-746 | sub/AST-744/AST-746-fix-scheduled-actions-table-column-gap |

| AST-758 | sub/AST-744/AST-758-uat-local-dev-not-showing-scheduled-actions-ui-fix |

| AST-760 | sub/AST-744/AST-760-uat-entity-header-overlays-state-in-scheduled-actions |

**Epic worktree:** `astral-AST-744/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Katherine | engineer | b6e50b66-2b15-441a-811a-266077a1538c |
| Betty | qa | 96041421-f4b0-4e15-baaf-026fcba38c35 |
| Radia | review | 43e30371-fd7e-4798-ab6b-794f2737d577 |

### Comments

#### susan — 2026-06-23T19:37:54.461Z
My bad! I forgot you guys are working on a different server and I had to pull from origin dev to get the fresh code.  Looks great!

#### chuckles — 2026-06-23T19:35:34.427Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-760** | Entity header overlays State in scheduled actions table (Remove column gap in scheduled_actions) |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-760** — _Entity header overlays State in scheduled actions table (Remove column gap in scheduled_actions)_
- **Issue reported:** After AST-758 local-dev delivery fix, Susan re-tested on local dev (2026-06-23). The Scheduled Actions phase table still mis-renders frozen headers: **Entity** `th` overlays **State** `th` (State appears behind Entity). Screenshots attached on parent comment.
- **Should now:** Frozen column headers align left-to-right: Candidate, Task, Entity, State — each visible and clickable; Entity must not cover State.
- **Quick check (this fix only):**
  1. Local `dev` after pull; `zsh launch.sh --flask`
  2. Admin → Scheduled Actions
  3. Expand a phase section with rows
  4. Observe header row — State th hidden behind Entity th (see parent screenshots)

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-06-23T19:27:44.845Z
The problem persists.  Confirm if you can parse these two screen shots to see that the State th is rendered behind the frozen Entity th.

![Screenshot 2026-06-23 at 12.24.53 PM.png](https://uploads.linear.app/6d08b154-c90f-497b-8dae-9a0bb7b7b5cd/15135a15-f50e-4a91-87f1-b742241c90f8/b5734286-e1b3-4897-b1f1-b5ea55af470d)

![Screenshot 2026-06-23 at 12.26.21 PM.png](https://uploads.linear.app/6d08b154-c90f-497b-8dae-9a0bb7b7b5cd/e17b4496-b679-48b5-b9f1-0cd506c796f4/32cc44e7-a37f-4f2a-b8a0-e8a6963a4c04)

#### chuckles — 2026-06-23T19:24:00.957Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-758** | local dev branch not showing scheduled actions UI fix (Remove column gap in scheduled_actions) |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-758** — _local dev branch not showing scheduled actions UI fix (Remove column gap in scheduled_actions)_
- **Issue reported:** Susan cannot see the AST-746 scheduled-actions column-gap fix when running the app on her local **dev** branch during UAT (parent comment 2026-06-23).
- **Should now:** After prep-uat landed the epic on `origin/dev`, pulling local dev and running the app should show **Scheduled Actions** with corrected frozen-column layout: no whitespace gap between Candidate and Task; Entity must not overlay State.
- **Quick check (this fix only):**
  1. On local `astral` worktree: `git fetch origin && git checkout dev && git pull origin dev`
  2. Start local dev (`./launch.sh` or project-standard local run)
  3. Open Admin → Scheduled Actions; expand a phase section with rows
  4. Compare column layout to the fix described in AST-746

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-06-23T19:13:11.895Z
@chuckles I'm not seeing the updated UI on the local dev branch.

#### chuckles — 2026-06-23T19:01:55.106Z
[merge-child] blocked: `validate-sub-log.sh` rejected `sub/AST-744/AST-746-fix-scheduled-actions-table-column-gap` — git pull merges on sub (`Merge remote-tracking branch 'origin/sub/...'`). @Katherine republish from `origin/ftr/AST-744-remove-column-gap-in-scheduled-actions` with canonical log (plan|code|merge-tests|test|docs|resolve only).

— Chuckles

#### chuckles — 2026-06-18T23:01:03.095Z
@susan — Cursor agent usage limit hit during Betty qa-child (stage 7) for AST-746. Katherine build landed Code Complete on `origin/sub/AST-744/AST-746-fix-scheduled-actions-table-column-gap`. Resume after spend limit reset (6/24) or model override: reassign parent to Chuckles and re-run datt.

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
