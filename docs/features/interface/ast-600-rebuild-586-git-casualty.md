# AST-600 — Rebuild 586 (git casualty)

<!-- linear-archive: AST-600 archived 2026-06-23 -->

## Linear archive (AST-600)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-600/rebuild-586-git-casualty  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

[AST-586](https://linear.app/astralcareermatch/issue/AST-586) fixed a dispatch bug: **qualify_job_listings** on trigger **VALID_TITLE** incorrectly applied **score_floor** gating, so jobs with no **latest_score** were never claimed and the pipeline stalled. That fix shipped and passed review, but the product behavior was lost in later git merges (plan docs and component tests partially remain on **dev**; runtime claim behavior reverted). This ticket restores that capability on **origin/dev** so dispatch can advance **VALID_TITLE** jobs through qualify and downstream consult steps — unblocking verification of JD scores on the Recommended list ([AST-547](https://linear.app/astralcareermatch/issue/AST-547) lineage). Same rebuild pattern as [AST-599](https://linear.app/astralcareermatch/issue/AST-599).

## Functional scope

* Separate **dispatch claim score-floor gating** from **task grading metadata** so input-state triggers (including **VALID_TITLE**) do not filter batch claims on **latest_score**, while post-score outcome triggers still honor **score_floor** when configured.
* **qualify_job_listings** manual or scheduled dispatch on **VALID_TITLE** claims eligible jobs that lack **latest_score**.
* Scheduled Actions admin presentation matches claim semantics: input-trigger rows are not score-gated for claim; post-score trigger rows retain floor behavior and defaults.
* Eligible-job counts shown for dispatch tasks align with the same claim rules (input triggers must not require **latest_score** to count as eligible).

## Boundaries

* Does not change **jd_score** persistence or Recommended list rendering ([AST-560](https://linear.app/astralcareermatch/issue/AST-560) scope).
* Does not remove **score_floor** for consult dispatch steps that legitimately gate on prior scores (**PASSED_JD**, **PASSED_DO**, **PASSED_GET**, **PASSED_LIKE**, and related post-score triggers).
* Does not alter **pass_threshold** grading math, consult verdict logic, or job state transitions.
* Does not change React UI beyond what the admin API returns for dispatch task metadata.
* Does not reopen [AST-547](https://linear.app/astralcareermatch/issue/AST-547) parent scope — only restores the dispatch fix that unblocked it.

## Acceptance criteria

1. With a dispatch task configured for **qualify_job_listings** + trigger **VALID_TITLE**, running dispatch claims at least one eligible **VALID_TITLE** job that has no **latest_score**.
2. The same configuration does not claim zero jobs solely because **latest_score** is null when jobs are otherwise eligible at **VALID_TITLE**.
3. Dispatch on **PASSED_JD** (and other post-score outcome triggers) still applies **score_floor** — jobs below floor are not claimed.
4. Scheduled Actions list shows **VALID_TITLE** / **qualify_job_listings** rows as not score-gated for claim; post-score rows still show scored/floor semantics consistent with claim behavior.
5. Component tests covering the AST-586 claim-floor contract pass on the merged branch.
6. Change lands on **origin/dev** via normal team git workflow.

## Dependencies and blockers

* **Reference spec:** [AST-586](https://linear.app/astralcareermatch/issue/AST-586) (Done — behavior to recreate).
* **Planning artifact:** `docs/features/interface/ast-586-qualify-no-score-floor-valid-title.md` (approved plan from original ship; dev agent may use as **plan-child** starting point).
* None blocking start.

## Open questions

None.

### Comments

#### ada — 2026-06-14T21:36:55.117Z
@Susan — **finish-up blocked:** `finish-up-land.sh` needs `gh` authenticated on this machine (`gh auth login`). `create-dev-pr.py --create` fails before PR/land. Parent reassigned to you; wrap lock cleared. Re-run wrap after `gh auth login`, or land manually: `./scripts/git/finish-up-land.sh AST-600-rebuild-586-git-casualty`.

— Chuckles

#### chuckles — 2026-06-14T03:58:15.254Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-600 (parent) | ftr/AST-600-rebuild-586-git-casualty |
| AST-617 | sub/AST-600/AST-617-qualify-no-score-floor-valid-title-rebuild-586 |

## Epic sessions (headless — Chuckles injects in every spawn; agents do not read Linear)

| Agent | Session id | Ticket | Role |
|-------|------------|--------|------|
| Joan | `88a60b4f-6c72-4bc2-94d8-cd3d119d34a7` | AST-600 (parent) | git |
| Hedy | `22fe020e-f6c1-49a8-8a50-17a7794d55c4` | AST-617 | engineer |
| Betty | `d270a62e-47b6-4c1d-bf55-f22f9b2ee9ab` | AST-617 | qa |
| Radia | `0a6c9017-3b31-4fa7-b1e3-3a7f891f3a1d` | AST-617 | review |

**Epic worktree:** `astral-AST-600/`

**Parent:** AST-600

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
