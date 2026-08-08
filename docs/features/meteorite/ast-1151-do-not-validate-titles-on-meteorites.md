# AST-1151 — Do not validate titles on meteorites

<!-- linear-archive: AST-1151 archived 2026-08-07 -->

## Linear archive (AST-1151)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1151/do-not-validate-titles-on-meteorites  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Candidates send meteorite jobs they already chose for analysis. Roster title-pattern screening exists to filter board scrapes against a candidate’s title preferences; that gate must not apply on the meteorite track. Candidate submission is the title qualification — meteorites should proceed into analysis without being rejected for title-pattern fitness. A usable title string extracted from content remains required (short/blank title still fails content trust).

## Functional scope

Meteorite jobs never run through roster title-pattern validation and never land in a title-screen fail outcome because a listing title did not match candidate title patterns.
A candidate-submitted meteorite that is otherwise ready for the meteorite qualify → GDL path continues into analysis without a title-pattern reject.
The `qualify_meteorite` short/blank title content gate stays: if a usable job title cannot be taken from the content, the job fails content trust (METEORITE_FAILED_QUALIFY) — that is not title-pattern validation.
Non-meteorite (roster) jobs keep today’s NEW title-screen behavior unchanged.

## Architectural definition

* **Patterns to reuse** — `pattern.batch.entity-claim-process-release` (meteorite qualify stays claim→process→release; no separate title-screen hop); `pattern.state.entity-state-transitions` (meteorite states stay on the METEORITE_* track; no INVALID_TITLE / VALID_TITLE diversion); `pattern.config.config-block` (title content-gate literals stay in TASK_CONFIG; no hardcoded apply thresholds).
* **New patterns proposed** — none.
* **Applicable statutes** — `astral.state.job-prior-states-enforced` (meteorite transitions must honor METEORITE_* priors); `astral.state.core-decides-transitions` (core owns any state change that removes a title-pattern reject); `astral.config.config-source-of-truth` (content-gate mins and orchestration from config blocks); `astral.standards.no-cross-contamination` (do not change roster qualify_job_listings title screen while fixing meteorites); `astral.standards.in-scope-only` (no GDL / email-ingest drive-by).

## Boundaries

Does not change roster `qualify_job_listings` inline title-pattern screening for NEW jobs.
Does not remove or relax the `qualify_meteorite` short/blank title content gate (Archie: only the title-pattern screen is forbidden; missing/unusable title means content cannot be trusted).
Does not change meteorite GDL scoring (evaluate_jd / grade_do / grade_get / grade_like) or Recommended UI.
Does not widen `gaze_email` / Manage Email create / Playwright ingest ([AST-1130](https://linear.app/astralcareermatch/issue/AST-1130/manage-email-create-button-for-job-lists-isnt-working) children stay owners of those paths).
Does not invent new METEORITE_* states.
Does not retire or redesign `validate_title` for the roster track.

## Acceptance criteria

A meteorite job that would fail candidate title-pattern matching on the roster path is not rejected for that reason and remains eligible for meteorite qualify → analysis when it has a usable title and other content gates pass.
No meteorite job is transitioned to INVALID_TITLE (or any roster title-screen fail state) by title-pattern screening.
A meteorite whose extract has a short or blank title still fails the existing content gate to METEORITE_FAILED_QUALIFY (unchanged policy).
Roster NEW jobs still receive the existing title-pattern screen (pass → continue qualify; fail → INVALID_TITLE) with no behavioral change from this epic.
UAT can show a candidate-submitted meteorite with a title outside the candidate’s title patterns still progressing past the pre-analysis gate into meteorite analysis when title/link/JD content gates pass.

## Dependencies and blockers

none.

## Open questions

none.

## Proposed child tickets

#### 1!: **Stop title-pattern screening on meteorite track - Ada**

Owns ensuring meteorite jobs never run roster title-pattern validation and never divert to INVALID_TITLE / title-screen fail for pattern mismatch; candidate submission is the title qualification. Leaves the `qualify_meteorite` short/blank title content gate unchanged. Does not own GDL grading or email ingest.
**Citations:** `pattern.batch.entity-claim-process-release`, `pattern.state.entity-state-transitions`, `pattern.config.config-block`; `astral.state.job-prior-states-enforced`, `astral.state.core-decides-transitions`, `astral.config.config-source-of-truth`, `astral.standards.no-cross-contamination`, `astral.standards.in-scope-only`.

#### 2: **Prove meteorite analysis without title-pattern reject - Hedy**

After #1: observable coverage that a meteorite whose title would fail roster title patterns still reaches meteorite qualify/analysis eligibility when content gates pass, that short/blank title still content-fails, and that roster NEW title screening is unchanged. Does not invent new ingest paths.
**Citations:** `pattern.state.entity-state-transitions`; `astral.standards.no-cross-contamination`, `astral.standards.in-scope-only`.

Monolith check: two functional capabilities (meteorite skip title-pattern + roster unchanged / content gate preserved) → two children; child #2 locks the Archie decision so Ada’s path change cannot silently regress roster or drop the title content gate.

---

## Original brief

Candidates send in jobs they want us to analyze, which means they have already qualified it for analysis.

## Git (authoritative — ignore Linear `gitBranchName`)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Ticket | `origin/…` |
| -- | -- |
| AST-1151 (parent) | ftr/AST-1151-do-not-validate-titles-on-meteorites |
| AST-1152 | sub/AST-1151/AST-1152-stop-title-pattern-screening-on-meteorite-track |
| AST-1153 | sub/AST-1151/AST-1153-prove-meteorite-analysis-without-title-pattern-reject |

**Epic worktree:** `astral-AST-1151/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | `/home/susan/.cursor/chats/7531f67927a1691184a40cb2f7e0e9d5/47e1b9ce-6643-425a-8bd5-065b52411a98/store.db` |
| Hedy | engineer | `/home/susan/.cursor/chats/7531f67927a1691184a40cb2f7e0e9d5/b333e07c-b468-4634-8422-d7fff041923f/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/a6771dc5-dac5-4ca9-9323-260f47ea20a8/store.db` |
| Radia | review | `/home/susan/.cursor/chats/7531f67927a1691184a40cb2f7e0e9d5/a6b5b5f1-cf20-4d09-afae-8dd99577c05e/store.db` |

### Comments

#### chuckles — 2026-08-03T00:35:17.270Z
@susan

1. Does “do not validate titles” also remove or relax the `qualify_meteorite` short/blank title content gate (today: title shorter than the configured minimum → METEORITE_FAILED_QUALIFY), or is that gate still required for having a usable title string while only the roster title-pattern screen is forbidden?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
