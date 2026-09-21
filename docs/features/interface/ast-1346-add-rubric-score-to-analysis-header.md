<!-- linear-archive: AST-1346 archived 2026-08-31 -->

## Linear archive (AST-1346)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1346/add-rubric-score-to-analysis-header  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 3  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Operators reading a Recommended Job Analysis section header can see, at a glance, how strongly that phase scored — including how much capacity was lost to no-signal vectors (X / equivalent). Today grades show in the header chrome but the numeric score that already drives pass/fail stays invisible there; this epic adds that visibility without waiting for a later scoring redesign.

## Functional scope

* Each Analysis-tab phase section that has grades (JD / DO / GET / LIKE) shows a numeric score summary in the section header title area in this shape: `{Phase label} - score: {earned} out of {possible} possible ({max} max total)`. Example numbers in the brief are format-only.
* **Earned** is the sum of per-vector scoring contributions for that phase using the same contribution math the product already uses at grade time. No-signal vectors (literal X and other rows the scorer already treats as no-signal) contribute nothing to earned.
* **Possible** is the maximum attainable among only the vectors that counted (no-signal vectors removed from the denominator set).
* **Max total** is the maximum attainable if every vector on that phase’s analysis-time rubric had full signal (no-signal slots still count toward capacity).
* Persist the earned / possible / max trio on `job_data` beside that phase’s grades when scoring saves (fields are not already stored today — only the normalized 0–10 `{prefix}_score` exists). For older jobs missing the trio, derive the same three numbers at read time from stored grades plus the job-carried analysis-time rubric so headers work without re-grade.
* When a phase has no grades or no scorable result (e.g. dealbreaker path that stores no score), keep the plain phase label — do not invent a score suffix.

## Architectural definition

* **Patterns to reuse** — `pattern.layers.import-discipline` (UI over API / job payload; no core imports from React); `pattern.config.config-block` (grade/score keys and phase labels stay config/manifest-driven, not hardcoded in components).
* **New patterns proposed** — none.
* **Applicable statutes** — `astral.layers.import-direction` (API/job_data lifts score breakdown; React renders); `astral.layers.ui-config-driven-business-logic` (phase labels / grades fields from report manifest); `astral.config.config-source-of-truth` (scoring constants and phase grade fields stay in config); `astral.agent.grade-vector-validation` (X and letter set remain the graded vocabulary); `astral.standards.no-hardcoded-sets` (no ad-hoc grade/phase sets in UI); `astral.standards.in-scope-only`; `astral.standards.dry-and-focused-functions`; `astral.docs.features-single-file-per-ticket`; universal orchestration set for pipeline hygiene (`orch.pipeline.plan-is-bible`, `orch.roles.betty-owns-test-tree`, `orch.git.*` as applicable at plan/build). Honor existing job-carried rubric law from AST-1063 / AST-1321: vector set and importance for recomputes come from analysis-time job data, not the live candidate rubric.

## Boundaries

* Does **not** redesign or replace the normalized 0–10 `{prefix}_score` used by lists, dispatch floors, or Recommended phase-score columns.
* Does **not** change pass/fail / score_floor behavior, grade letters, confidence rules, or rubric criteria editing.
* Does **not** re-grade historical jobs or backfill via a batch job — display-time derive when the trio is absent.
* Does **not** change Summary / Artifacts tabs, list-table Score columns, or grade-dot header chrome (those stay as after AST-950 / AST-1321).
* Does **not** invent a new scoring formula — visibility over the existing contribution math only.

## Acceptance criteria

1. On a job with graded JD Analysis including some X vectors, the JD Analysis section header shows `JD Analysis - score: {earned} out of {possible} possible ({max} max total)` where possible excludes X/no-signal vectors and max includes full phase rubric capacity.
2. The same header shape appears for DO / GET / LIKE Analysis sections when those phases have grades.
3. Earned / possible / max for a freshly graded job are present on `job_data` with that phase’s grades (not only the existing 0–10 score).
4. An older job that has grades + job-carried rubric but no stored trio still shows the correct three numbers in the header (derived at read time).
5. A phase with no grades (or no scorable score) shows the phase label only — no fabricated score text.
6. Recommended list phase-score columns and dispatch soft-fail behavior remain unchanged.

## Dependencies and blockers

none. Adjacent Done work (AST-1321 / AST-1063 job-carried Analysis headers) is already on `dev`; this epic extends that chrome.

## Open questions

none

## Proposed child tickets

#### 1!: **Persist phase score breakdown with grades - Ada**

Owns computing earned / possible / max with existing contribution math (X/no-signal excluded from earned and possible; max = full rubric capacity) and writing that trio onto `job_data` beside phase grades at score-save time; ensures job detail/list payload can lift the fields. Does **not** own Analysis header title chrome (sibling #2). Does **not** change 0–10 `{prefix}_score` semantics.
**Citations:** `pattern.config.config-block`, `astral.config.config-source-of-truth`, `astral.agent.grade-vector-validation`, `astral.layers.import-direction`, AST-1063 job-carried rubric law.
**Estimate: 3**

#### 2: **Analysis header score title chrome - Katherine**

Owns rendering the `{Phase} - score: … out of … possible (… max total)` text on Analysis-tab section headers for JD / DO / GET / LIKE, reading stored trio when present and deriving from grades + job-carried rubric when absent; omits suffix when unscored. After #1. Does **not** own score-save writes or list phase-score columns.
**Citations:** `pattern.layers.import-discipline`, `astral.layers.ui-config-driven-business-logic`, `astral.standards.no-hardcoded-sets`, AST-950 / AST-1321 Analysis header chrome.
**Estimate: 2**

---

## Original brief

Include total of the scores for each vector, and a total possible (removing the X's)

```
JD Analysis - score: 137 out of 150 possible (320 max total)
```

I know this isn't the final, but I want to add some visibility to the score, and account for the missing vectors from X's. This can be stored in the job_data with the grades, if it isn't already.

### Comments

#### chuckles — 2026-08-12T23:48:06.816Z
AST-1348 REVIEW — Radia discuss items (branch hygiene / advisory); Katherine resolve next.

#### chuckles — 2026-08-12T23:33:17.190Z
AST-1347 REVIEW — Radia discuss: sibling Print-lane tests bundled on sub; no product fix-now.

---

## Threads (generated — epic_registry mirror)

_(generated from epic registry — do not hand-edit; edits are overwritten)_

### Team

| Agent | Role | Thread |
|--------|-------|--------|
| Ada | engineer | `/home/susan/.cursor/chats/c268073a5aaaa0851d1277e66769c721/ebbe160f-f1b9-415d-8f23-8f7e8b093dde/store.db` |
| Katherine | engineer | `/home/susan/.cursor/chats/c268073a5aaaa0851d1277e66769c721/3cb97861-1645-42e0-9a39-cbdd13285862/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/af50c568-1860-4a6d-87e7-077bd4bc01e4/store.db` |
| Radia | review | `/home/susan/.cursor/chats/c268073a5aaaa0851d1277e66769c721/7f6c0f3b-253f-4a80-ab07-c6c66bf16b0c/store.db` |

### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-1346 (parent) | ftr/AST-1346-add-rubric-score-to-analysis-header |
| AST-1347 | sub/AST-1346/AST-1347-persist-phase-score-breakdown |
| AST-1348 | sub/AST-1346/AST-1348-analysis-header-score-title-chrome |

**Epic worktree:** `astral-AST-1346/` — one active sub checked out at a time.
