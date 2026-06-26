# AST-599 — Rebuild 581 (git casualty)

<!-- linear-archive: AST-599 archived 2026-06-23 -->

## Linear archive (AST-599)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-599/rebuild-581-git-casualty  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-581

### Description

We lost the functionality we built for [AST-581](https://linear.app/astralcareermatch/issue/AST-581/uat-preview-materials-button-resumecover-html-preview-tabs-in-jar) in the git merges.  Please use this ticket to recreate the code and merge it.

### Comments

#### chuckles — 2026-06-12T18:36:43.972Z
Betty land preflight: CLEAN (origin/dev @ `9cf9e2e4` = origin/ftr/AST-599-rebuild-581-git-casualty).

— Chuckles

#### chuckles — 2026-06-12T00:22:28.545Z
## Manual test steps

1. Restart the app from local `dev` if it is already running (`e63651ec`).
2. Open a job in **CANDIDATE_REVIEW** (or with `resume_content` / `cover_letter` artifacts populated).
3. Open the Recommended Job Report (JAR) — confirm **Preview Materials** appears in the header.
4. Click **Preview Materials** — modal opens with **Resume** tab; iframe loads `/candidate/resume/<job_id>` HTML.
5. When cover letter content exists, switch to **Cover Letter** tab — iframe loads `/candidate/cover/<job_id>`.
6. Confirm job resume route no longer bundles cover inline (resume-only HTML on resume tab).

`origin/ftr/AST-599-rebuild-581-git-casualty` @ `6dd9baaf` · local `dev` merged (`e63651ec`). Reset: `git reset --hard origin/dev`

— Chuckles

#### chuckles — 2026-06-12T00:19:18.037Z
**[prep-uat] blocked:** `land-ftr` merge conflict in `docs/ASTRAL_TEST_BIBLE.md` (local `dev` ← `origin/ftr/AST-599-rebuild-581-git-casualty`).

@Betty White — resolve bible hunk; keep **§7.13zx** (AST-605) from ftr alongside existing dev § blocks.

Chuckles will re-run `land-ftr AST-599` after fix lands on `origin/ftr/AST-599-rebuild-581-git-casualty`.

— Chuckles

#### chuckles — 2026-06-12T00:06:33.078Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-599 (parent) | ftr/AST-599-rebuild-581-git-casualty |
| AST-605 | sub/AST-599/AST-605-preview-materials-jar-tabs-rebuild-581 |

## Epic sessions (headless — Chuckles injects in every spawn; agents do not read Linear)

| Agent | Session id | Ticket | Role |
|-------|------------|--------|------|
| Joan | `901e123a-d527-4183-b7af-39f8241a31a3` | AST-599 (parent) | git |
| Katherine | see manifest | AST-605 | engineer |
| Betty | see manifest | AST-605 | qa |
| Radia | see manifest | AST-605 | review |

**Parent:** AST-599

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
