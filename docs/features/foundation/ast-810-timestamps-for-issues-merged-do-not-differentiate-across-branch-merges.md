# AST-810 — timestamps for issues merged do not differentiate across branch merges

<!-- linear-archive: AST-810 archived 2026-07-22 -->

## Linear archive (AST-810)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-810/timestamps-for-issues-merged-do-not-differentiate-across-branch-merges  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

The admin deploy footer merge-ticket tooltip (AST-675 / AST-691 / AST-791) lists parent epics awaiting Susan's UAT on the current deploy. After AST-800 introduced full log rebuild at prep-uat time, multiple parents can appear in the list — but Susan observes they often share the same timestamp in the tooltip. That makes it impossible to tell which feature branch actually landed most recently or whether a specific UAT fix has reached dev. This epic corrects per-parent timestamp semantics so each listed parent reflects when its own ftr work merged onto the integration line, not a shared rebuild moment or unrelated dev tip.

## Functional scope

* **Per-parent land timestamp:** Each entry in the persisted merge ticket log carries a `recorded_at` value that reflects when that parent epic's feature branch (`ftr/*`) was merged onto `origin/dev` — i.e. the commit timestamp of the merge that brought that parent's code onto dev, not the timestamp of an unrelated dev commit or a bulk rebuild triggered by a different parent.
* **Distinct timestamps across siblings:** When two or more parent epics are listed simultaneously and their ftr branches landed on dev at different times, their tooltip timestamps differ accordingly. Parents that genuinely landed in the same merge commit may legitimately share a timestamp.
* **Rebuild correctness:** Running the prep-uat merge-ticket log rebuild (`record-landed-parent.sh` / rebuild CLI) on `origin/dev` rewrites `recorded_at` for every qualifying parent using the per-parent resolution above — not one shared timestamp applied to all entries missing a dedicated prep-uat commit message.
* **Tooltip read path unchanged:** The admin env-label tooltip continues to display ticket id plus formatted timestamp (AST-691 UX: hover, up to 20 lines, most recent first). No change to which parents qualify for the list (AST-800 User Testing + ftr-on-dev gate, AST-805 landing-parent union).

## Boundaries

* Does not change tooltip interaction, styling, line cap, or poll interval (AST-691 / AST-798).
* Does not change eligibility rules for which parent ids appear in the log (AST-791 / AST-800 / AST-805).
* Does not add ticket titles, child ids, or SHA display to the tooltip.
* Does not add runtime Linear filtering on deploy-status poll (log remains authoritative after rebuild).
* Does not backfill or alter Linear issue state — dev git history and the persisted log only.

## Acceptance criteria

1. On a deploy built from `origin/dev` where `data/merge_ticket_log.json` lists at least two parent epics whose ftr branches merged onto dev at different times, hovering the admin env label shows **different** formatted timestamps for those parents (not all identical).
2. For a given parent epic AST-NNN in the log, `recorded_at` corresponds to the commit timestamp of the merge that brought that parent's `ftr/*` onto `origin/dev` — verifiable by inspecting dev git history for that parent — rather than the timestamp of an unrelated commit that merely touched the log file or refreshed the list for another parent.
3. Susan can identify the most recently landed parent in the tooltip by timestamp alone when multiple parents are listed.
4. After a prep-uat rebuild on dev, parents that previously shared an incorrect identical timestamp receive corrected distinct values where their actual land times differ.
5. Existing deploy-status payload shape and AST-691 tooltip behavior (empty list, non-admin, missing env) remain unchanged.

## Dependencies and blockers

* **AST-791** (Done) — deploy env tooltip and merge ticket log infrastructure.
* **AST-800** (Done) — full rebuild at prep-uat; established ftr-on-dev gate and timestamp resolution intent.
* **AST-805** / **AST-806** (Done) — `--landing-parent` union during prep-uat rebuild.
* None blocking start — fix applies to rebuild timestamp resolution and resulting log data on dev.

## Open questions

none.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-810 (parent) | ftr/ast-810-timestamps-for-issues-merged-do-not-differentiate-across-branch-merges |
| AST-811 | sub/AST-810/AST-811-per-parent-merge-ticket-timestamp-resolution |

**Epic worktree:** `astral-AST-810/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |

---

## Original brief

All timestamps are identical in the tool tip, when they should be the create date of the SHA that was merged into dev from the ftr branch.

I need to see the latest merge timestamp to know if UAT fixes have been successfully merged.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
