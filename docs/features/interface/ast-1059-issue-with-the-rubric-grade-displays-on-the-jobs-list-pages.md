# AST-1059 — Issue with the rubric grade displays on the Jobs List pages

<!-- linear-archive: AST-1059 archived 2026-08-07 -->

## Linear archive (AST-1059)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1059/issue-with-the-rubric-grade-displays-on-the-jobs-list-pages  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

On Jobs list pages (observed on Skipped during Meteorite UAT), rows can show mostly empty rubric grade cells even when the job already holds a complete graded response — because columns today come from the **live** candidate rubric while cells join by name to **stored** job grades. Operators cannot see what was actually graded. This epic makes list tables (headers, tooltips, grade-dots, and Score) reflect the **job’s own analysis-time rubric and score**, never the live rubric artifact.

## Functional scope

* Do **not** use the live candidate rubric to choose Jobs list grade columns or tooltips. Columns, header codes, and tooltips come from the **fully hydrated rubric carried with the job’s analysis data** (the same epoch as the stored grades).
* Within a list section, **group jobs by aligned rubric**. Jobs that share the same rubric shape share one table. When the rubric shape differs, start a **separate table** with that group’s correct headers and tooltips.
* Every stored grade vector for that section’s grade field paints as a grade-dot + confidence under the matching job-aligned column (no sea of dashes from a renamed live rubric).
* The **Score** column shows the score recorded on the job at analysis time (from job data) — not a live recomputation that disagrees with the stored grades shown in the row.
* Same rules on every Jobs list surface that shows per-vector grade-dot columns (at least Skipped and In Review). Recommended phase-score layout stays out of scope unless Susan expands later.

## Architectural definition

* **Patterns to reuse**
  * `pattern.layers.import-discipline` — UI renders API-shaped job data; list tables do not invent rubric criteria from live candidate artifacts.
  * `pattern.config.config-block` — section → grade-field mapping stays config-driven; column *content* comes from job-carried hydration.
* **New patterns proposed**
  * **Job-list tables keyed by job-carried rubric fingerprint** — within a section, split tables when stored rubric shape differs; headers/tooltips from job hydration, not live `rubric_artifact`. Flag for Archie approval before plans treat it as catalog law.
* **Applicable statutes**
  * `astral.layers.ui-config-driven-business-logic` — grouping / grade-field selection remains config/API-resolved; React paints resolved shapes.
  * `astral.layers.import-direction` — UI over API; no UI→data shortcuts.
  * `astral.config.config-source-of-truth` — which grade field belongs to which section stays in config.
  * `astral.agent.grade-vector-validation` — only if write-path investigation shows grades were accepted without matching hydration (secondary; not the primary list bug).
  * universal set — product UI (and API shaping if hydration must be surfaced more explicitly for lists).

## Boundaries

* Does **not** re-grade jobs or rewrite historical grades / scores.
* Does **not** update or version live candidate rubrics ([AST-1050](https://linear.app/astralcareermatch/issue/AST-1050/bulk-update-candidate-rubric) stays separate).
* Does **not** change Recommended phase-score columns or Recommended Job Modal analysis chrome.
* Does **not** own meteorite GDL processing ([AST-1052](https://linear.app/astralcareermatch/issue/AST-1052/processing-meteorites)); this is an Interface list-display bug (related discovery only).
* Must not break sections where every job already shares one rubric shape (single table as today, with job-aligned headers).

## Acceptance criteria

1. List grade columns for a section are derived from each job group’s **job-carried hydrated rubric**, not from the live candidate rubric artifact. Changing the live rubric without re-analyzing jobs does not retitle empty columns over old grades.
2. Jobs in the same section with **different** rubric shapes appear in **separate tables**, each with headers and tooltips matching that group’s rubric; grades fill those columns for every stored vector.
3. Jobs sharing an aligned rubric share one table; every stored vector for the section grade field shows grade-dot + confidence (regression: the brief’s meteorite-somerset style rows show full grades, not mostly dashes).
4. Score on those rows is the **analysis-time score from job data**, consistent with the grades shown for that analysis.
5. In Review sections that use the same per-vector grade-dot pattern follow the same job-aligned / group-by-rubric rules.
6. Happy path: a section of jobs that all share one rubric still renders one coherent table with correct grades and Score.

## Dependencies and blockers

* Related: [AST-1052](https://linear.app/astralcareermatch/issue/AST-1052/processing-meteorites) — discovery during Meteorite UAT; not blockedBy.
* none otherwise.

## Open questions

none

## Proposed child tickets

#### 1!: **Job-carried rubric hydration for list columns - Ada**

Owns surfacing (API / job payload) the fully hydrated rubric that already lives with job analysis data so list pages can build headers and tooltips without the live candidate rubric. Does **not** own table grouping UI or score column paint.
**Citations:** `pattern.layers.import-discipline`; `astral.layers.import-direction`; `astral.config.config-source-of-truth`; `astral.layers.ui-config-driven-business-logic`.

#### 2: **Group-by-aligned-rubric Jobs list tables - Katherine**

Owns Skipped + In Review list rendering: drop live-rubric columns; group jobs by aligned job-carried rubric into separate tables with matching headers/tooltips; paint grade-dots from stored grades; paint Score from analysis-time job data. After #1. Does **not** own hydration payload shape beyond consuming it; does not own Recommended phase-score UI.
**Citations:** job-list tables keyed by job-carried rubric fingerprint (new-pattern flag); `astral.layers.ui-config-driven-business-logic`; `astral.layers.import-direction`; `pattern.layers.import-discipline`.

**New patterns:** Child 2 introduces job-list tables keyed by job-carried rubric fingerprint (Archie-approved new pattern above).

**Monolith check:** Functional scope has 5 capabilities; **M = 2** — hydration/API surface vs list grouping UI split intentionally.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-1059 (parent) | ftr/AST-1059-rubric-grade-displays-jobs-list |
| AST-1063 | sub/AST-1059/AST-1063-job-carried-rubric-hydration-for-list-columns |
| AST-1064 | sub/AST-1059/AST-1064-group-by-aligned-rubric-jobs-list-tables |

**Epic worktree:** `astral-AST-1059/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **Thread** column is the fully-qualified `store.db` path (UUID is the directory name — extract for `agent --resume`). **datt resume:** read this table — not chat memory. One UUID per agent; never the parent Chuckles Thread UUID.

| Agent | Role | Thread |
| -- | -- | -- |
| Katherine | engineer | `/home/susan/.cursor/chats/845cf1b3ae7cc5921673592f13d91e09/796b52dd-2830-43c6-a8aa-cf6897426e99/store.db` |
| Ada | engineer | `/home/susan/.cursor/chats/845cf1b3ae7cc5921673592f13d91e09/1223ef33-6442-4b3f-a048-7a7c8d1a7715/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/1435db58-ae87-4b74-8a59-a276592304c5/store.db` |
| Radia | review | `/home/susan/.cursor/chats/845cf1b3ae7cc5921673592f13d91e09/32a0c6c0-2099-4b97-baa8-e48095b506b3/store.db` |

---

## Original brief

We have incomplete rubric data appearing for jobs that had full rubric responses.

```html
<div class="list-page-table-wrap"><table class="list-page-table"><thead><tr><th style="width: 1px; white-space: nowrap;">Actions</th><th style="width: 32px;"></th><th class="sortable">Job Title</th><th class="sortable">Company</th><th class="sortable" title="Company Stage &amp; Product Maturity (5)" style="text-align: center; white-space: nowrap; width: 1px;">CS</th><th class="sortable" title="Domain &amp; Technology Fit (5)" style="text-align: center; white-space: nowrap; width: 1px;">DT</th><th class="sortable" title="Employment Type (5)" style="text-align: center; white-space: nowrap; width: 1px;">ET</th><th class="sortable" title="Gut Check (5)" style="text-align: center; white-space: nowrap; width: 1px;">GC</th><th class="sortable" title="JD Readability &amp; Coherence (5)" style="text-align: center; white-space: nowrap; width: 1px;">JD</th><th class="sortable" title="Remote Status (5)" style="text-align: center; white-space: nowrap; width: 1px;">RS</th><th class="sortable" title="Role Type &amp; Technical Involvement (5)" style="text-align: center; white-space: nowrap; width: 1px;">RT</th><th class="sortable" title="Seniority &amp; Scope Alignment (5)" style="text-align: center; white-space: nowrap; width: 1px;">SA</th><th class="sortable" style="text-align: center; min-width: 60px;">Score</th><th class="sortable">Failed At</th></tr></thead><tbody><tr class="clickable"><td></td><td><input type="checkbox"></td><td>—</td><td>meteorite-somerset</td><td style="text-align: center; white-space: nowrap; width: 1px;">—</td><td style="text-align: center; white-space: nowrap; width: 1px;">—</td><td style="text-align: center; white-space: nowrap; width: 1px;"><div class="analysis-grade-block"><span class="grade-dot dot-x" title="No information about employment type">X</span><div class="confidence-bullets" aria-hidden="true"><span class="confidence-bullet"></span><span class="confidence-bullet"></span><span class="confidence-bullet"></span><span class="confidence-bullet"></span><span class="confidence-bullet"></span></div></div></td><td style="text-align: center; white-space: nowrap; width: 1px;">—</td><td style="text-align: center; white-space: nowrap; width: 1px;">—</td><td style="text-align: center; white-space: nowrap; width: 1px;">—</td><td style="text-align: center; white-space: nowrap; width: 1px;">—</td><td style="text-align: center; white-space: nowrap; width: 1px;">—</td><td style="text-align: center;">10.00</td><td>7/29/26, 3:59:49 PM</td></tr><tr class="clickable"><td></td><td><input type="checkbox"></td><td>—</td><td>meteorite-somerset</td><td style="text-align: center; white-space: nowrap; width: 1px;">—</td><td style="text-align: center; white-space: nowrap; width: 1px;">—</td><td style="text-align: center; white-space: nowrap; width: 1px;"><div class="analysis-grade-block"><span class="grade-dot dot-x" title="No information about employment type">X</span><div class="confidence-bullets" aria-hidden="true"><span class="confidence-bullet"></span><span class="confidence-bullet"></span><span class="confidence-bullet"></span><span class="confidence-bullet"></span><span class="confidence-bullet"></span></div></div></td><td style="text-align: center; white-space: nowrap; width: 1px;">—</td><td style="text-align: center; white-space: nowrap; width: 1px;">—</td><td style="text-align: center; white-space: nowrap; width: 1px;">—</td><td style="text-align: center; white-space: nowrap; width: 1px;">—</td><td style="text-align: center; white-space: nowrap; width: 1px;">—</td><td style="text-align: center;">10.00</td><td>7/29/26, 3:57:54 PM</td></tr></tbody></table></div>
```

```
--- [1/2] ---
{
  "jobs": [
    {
      "astral_job_id": "a40b85a6-e7a3-4835-b5d2-9d604031d74e",
      "grades": [
        {
          "vector": "Compensation",
          "grade": "X",
          "confidence": 0
        },
        {
          "vector": "Domain & Role Type Exclusions",
          "grade": "F",
          "confidence": 2
        },
        {
          "vector": "Employment Type",
          "grade": "X",
          "confidence": 0
        },
        {
          "vector": "Program Scope",
          "grade": "X",
          "confidence": 0
        },
        {
          "vector": "Remote/Location Policy",
          "grade": "F",
          "confidence": 2
        },
        {
          "vector": "Technical Scope",
          "grade": "F",
          "confidence": 2
        }
      ]
    }
  ]
}

--- [2/2] ---
{
  "jobs": [
    {
      "astral_job_id": "a40b85a6-e7a3-4835-b5d2-9d604031d74e",
      "grades": [
        {
          "vector": "Compensation",
          "grade": "X",
          "confidence": 0
        },
        {
          "vector": "Domain & Role Type Exclusions",
          "grade": "F",
          "confidence": 2
        },
        {
          "vector": "Employment Type",
          "grade": "X",
          "confidence": 0
        },
        {
          "vector": "Program Scope",
          "grade": "X",
          "confidence": 0
        },
        {
          "vector": "Remote/Location Policy",
          "grade": "F",
          "confidence": 2
        },
        {
          "vector": "Technical Scope",
          "grade": "F",
          "confidence": 2
        }
      ]
    }
  ]
}
```

### Comments

#### chuckles — 2026-07-29T23:14:14.364Z
@susan open questions (definition is in the Description):

1. Column strategy when live rubric ≠ stored job vectors — **A** (columns from job grades when join would be mostly blank), **B** (keep live columns + surface unmatched grades), **C** (dashes OK after rubric rewrite; only fix write-path bugs), or **D** (other)?
2. Home project / attachment — keep **Astral Interface**, move to **Astral Meteorite**, or Bug child under AST-1052?
3. Is Score `10.00` with empty grade cells also in scope, or grade-dots only?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
