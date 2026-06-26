# AST-434 — Production readiness: job-list rubrics UI + prompt/rubric diagnostic

<!-- linear-archive: AST-434 archived 2026-06-15 -->

## Linear archive (AST-434)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-434/production-readiness-job-list-rubrics-ui-promptrubric-diagnostic  
**Status at archive:** Done  
**Project:** Astral Agent  
**Assignee:** susan  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-448

### Description

## Purpose

Recent consult scoring and rubric-importance work ([AST-359](https://linear.app/astralcareermatch/issue/AST-359/add-importance-factor-to-rubric-vectors), [AST-428](https://linear.app/astralcareermatch/issue/AST-428/replace-per-vector-grade-scores-with-universal-grade-values-per-vector)) exposed production misalignment while the system is idle: job-list tables are hard to read, admin prompts on Railway may lag local edits, and it is unclear whether stored candidate rubrics or `craft_*` admin task definitions are wrong. Susan wants **visibility and validation first**—not blind prompt sync or rubric regeneration—so problems can be documented before any environment merge or re-craft.

[AST-434](https://linear.app/astralcareermatch/issue/AST-434/production-readiness-job-list-rubrics-ui-promptrubric-diagnostic) **is the parent coordinator.** On dispatch it splits into work in **Astral Interface** (display) and **Astral Administrator** (diagnostic). It is not an implementation home for either stream.

## Functional scope

### A. Job list rubric column presentation — *Astral Interface*

* Introduce or extend a **shared** job-list rubric column presentation used by all job-list views that show per-vector grades (at minimum **In Review**, **Skipped** as the reference behavior, and **Recommended**; others as they already use the same table pattern).
* **Visible header:** short vector code only (Skipped jobs pattern)—not long labels, importance prefixes, or raw fully qualified vector names from job grade rows.
* **Tooltip:** human-readable label and importance as `Title Match (7)`.
* **Column order:** rubric columns sorted by **descending importance** (highest leftmost among rubric columns), after fixed columns (job title, company, etc.).
* **Fallback:** when rubric artifact metadata is missing, still use compact header + best-effort tooltip—not verbose strings in the header cell.

### B. Admin prompt diagnostic — *Astral Administrator*

* Produce a **reviewable diagnostic** comparing admin-managed prompt content between environments (local vs Railway production): `agent` and `agent_task` rows for consult and craft tasks, **excluding** candidate-specific data.
* The diagnostic identifies **what differs**, **which task keys** are affected, and **whether each diff is expected or suspicious**—suitable to inform documentation about prompts and a future sync decision.
* Call out `craft_*_rubric` task prompts and instructions explicitly (admin-task level), separate from candidate-stored rubric JSON.
* **No import, export-to-production, or sync** in this effort—diagnosis only. Future sync remains [AST-373](https://linear.app/astralcareermatch/issue/AST-373/prompt-injection) / [AST-381](https://linear.app/astralcareermatch/issue/AST-381/pushing-database-content-to-github) after Susan reviews findings.

### C. Rubric and craft-task validation — *Astral Administrator (analysis); may inform Interface*

* For the candidate(s) Susan designates for investigation, document what is **actually broken** at:
  * **Candidate level:** stored rubric artifacts (missing `code`, `importance`, labels, grade tables, etc.).
  * **Admin-task level:** whether `craft_*_rubric` task definitions and prompt text match what the product now expects (codes, importance, response shape).
* Deliverable is a **validation summary** (gaps, likely root cause: data vs prompt vs schema), not regenerated rubrics and not re-run craft flows.

## Boundaries

* **No prompt sync** and **no rubric regeneration** for any candidate in this epic.
* Does **not** implement [AST-373](https://linear.app/astralcareermatch/issue/AST-373/prompt-injection) export/import UI or [AST-381](https://linear.app/astralcareermatch/issue/AST-381/pushing-database-content-to-github) repo-tracked snapshots (may reference them as follow-ups).
* Does **not** change consult scoring math, grade values, or confidence rules.
* Does **not** include Recommended page layout revamp beyond shared rubric column behavior.
* Does **not** include Boards, artifact resume/cover-letter pipelines, or `do_task` internals except as diagnostic context.

## Acceptance criteria

1. **Interface:** In Review and Recommended use the shared rubric column component; headers show short codes, tooltips show `Label (n)`, rubric columns are importance-ordered; Susan confirms parity with Skipped readability.
2. **Administrator — prompts:** A written diagnostic lists local vs production diffs for relevant admin tasks; `craft_*_rubric` tasks are covered; no production data was overwritten.
3. **Administrator — rubrics:** A written validation states what is wrong (if anything) in designated candidate rubric artifacts vs what `craft_*` tasks are specified to produce; distinguishes candidate-data issues from admin-task issues.
4. Susan has enough documentation to decide **later** whether to sync prompts ([AST-373](https://linear.app/astralcareermatch/issue/AST-373/prompt-injection)), update craft prompts, or fix candidate artifacts—without this epic performing those actions.

## Dependencies and blockers

* [AST-359](https://linear.app/astralcareermatch/issue/AST-359/add-importance-factor-to-rubric-vectors), [AST-428](https://linear.app/astralcareermatch/issue/AST-428/replace-per-vector-grade-scores-with-universal-grade-values-per-vector) — Done (importance and grade config).
* [AST-373](https://linear.app/astralcareermatch/issue/AST-373/prompt-injection) — Follow-up after diagnostic; not in scope here.
* [AST-381](https://linear.app/astralcareermatch/issue/AST-381/pushing-database-content-to-github) — Longer-term alignment; not in scope here.
* Capability A is not blocked by B or C.

## Open questions

None — Susan answered 2026-05-18. Dispatch as parent with Interface + Administrator children.

### Comments

#### chuckles — 2026-05-22T17:18:01.546Z
## Landed on origin/dev — Chuckles

- `origin/ftr/AST-434-production-readiness-job-list-rubrics-ui-promptrubric-diagnostic` was already merged into local `dev` (final prep-uat); pushed `origin/dev`
- Deleted `origin/ftr/AST-434-production-readiness-job-list-rubrics-ui-promptrubric-diagnostic`
- Moved to **Done**: **AST-434** (parent was User Testing — finish-up per Susan)
- Children **AST-437**, **AST-438** were already **Done** (assignees unchanged: Katherine, Ada)

Push range: `fa2f3650..ed7f18d0` on `origin/dev`

— Chuckles

#### chuckles — 2026-05-22T03:11:37.147Z
## UAT Ready — Chuckles (prep-uat — final rollup)

Child branches were already merged to parent on prior prep-uat runs. This run refreshes **local `dev`** from the latest **`origin/ftr/AST-434-production-readiness-job-list-rubrics-ui-promptrubric-diagnostic`** tip (includes Katherine’s post-UAT fixes).

**Parent branch:** `origin/ftr/AST-434-production-readiness-job-list-rubrics-ui-promptrubric-diagnostic`

**Children (already on ftr):**
1. **AST-437** — shared job-list rubric columns
2. **AST-438** — admin prompt/rubric diagnostic

**Latest fixes on ftr (since last UAT):**
- Grade-dot tooltips use rubric `grade_descriptions` (and job `reason` when present)
- **Recommended** — job action buttons restored (AST-312)
- **Skipped** — Resurrect action restored

Local `dev` merged (prep-uat §8). Restart the app if it is running, then test.

`ftr` tip: `aba4481a` · local `dev` merge: `ed7f18d0`

## Manual test steps

**Prerequisites:** App running from local `dev` (restart after merge). Candidate with jobs in **In Review**, **Skipped**, and **Recommended**, with rubric grades and at least one skipped job eligible for Resurrect.

### AST-437 — Job-list rubric columns (UI)

1. **In Review** — Rubric `<th>` shows **short code only** (e.g. `TE`); hover shows **`Label (n)`** (e.g. `Title Match (7)`).
2. **In Review** — Rubric columns after Company are **importance-ordered** (highest left).
3. **In Review** — Hover a **grade dot**; tooltip should show rubric text for that letter (or job `reason` if the grade row has one), not just the vector label.
4. **Recommended** — Repeat 1–3 for the Recommended table (`like_rubric`).
5. **Skipped** — Compact rubric headers + `Label (n)` tooltips; section expand/collapse and bulk-retry still work.
6. **Regression** — Artifact editor / analysis headers still use the **full** `formatRubricVectorHeader` string (not compact codes).

### Katherine fixes — job actions (UI)

7. **Recommended** — **Actions** column present; row buttons work (notes, report, state actions per AST-312). Clicking actions must not break row click-to-detail.
8. **Skipped** — **Resurrect** (or equivalent review action) visible and works on an eligible skipped job; job moves to In Review as expected.

### AST-438 — Admin diagnostic (docs)

9. Read `docs/features/administrator/ast-438-prompt-diff-local-vs-production.md` — consult + `craft_*_rubric` tasks listed; no prod writes in this epic.
10. **Rubric validation — deferred** until candidate id(s) on **AST-438** and `ast-438-rubric-validation.md` is generated.

### Parent acceptance

11. **AC1** — Interface rubric readability (steps 1–6).
12. **AC2** — Prompt diagnostic sufficient for later sync decision (step 9).
13. **AC3** — Rubric validation deferred (step 10).
14. **AC4** — No prompt sync, rubric regen, or scoring changes in this rollup.

If testing fails on `dev`:
  `git reset --hard origin/dev`

— Chuckles

#### katherine — 2026-05-22T02:39:18.730Z
**Cherry-picked to `origin/dev`** (`fa2f3650`):
- `efb3be73` — Recommended action buttons
- `d2213ba3` — Skipped Resurrect (restore)

Local UAT on `dev` should show both after pull/rebuild.

#### katherine — 2026-05-22T02:32:17.644Z
[check-linear] **Skipped — Resurrect (restore) button**

Same regression as Recommended: rubric refactor removed `CandidateJobRowActions` from `JobsSkipped.tsx`.

**Fix:** pushed on `ftr/AST-434-production-readiness-job-list-rubrics-ui-promptrubric-diagnostic` — Actions column + **Re** (Resurrect) for `CANDIDATE_SKIPPED` rows in the expanded section.

**Note:** `origin/dev` still needs this commit cherry-picked for local UAT on `dev`.

#### katherine — 2026-05-22T02:13:57.114Z
[check-linear] **UAT fix — Recommended action buttons**

**Root cause:** AST-437 `buildJobListRubricColumns` refactor rewrote `JobsRecommended.tsx` without the AST-312 `CandidateJobRowActions` column (Skip, Applied, etc.).

**Fix:** `efb3be73` on `origin/ftr/AST-434-production-readiness-job-list-rubrics-ui-promptrubric-diagnostic` — restored AST-312 UI modules from `origin/dev` and re-wired Recommended list (rubric columns + Actions column).

**Note:** `origin/dev` still has the stripped `JobsRecommended.tsx` after prep-uat merge; merge/cherry-pick this commit onto `dev` for local UAT on `dev`. Applied/Interview actions on the **ftr** line still need AST-311 API (`candidate_action`) if you exercise those buttons on the ftr build only — Skip uses existing `/skip` route.

#### susan — 2026-05-19T21:09:45.392Z
@katherine Your fix seems to have lost the action buttons on the Recommended list.  (e.g. "Skip")

#### chuckles — 2026-05-19T21:00:24.794Z
## Landed on origin/dev — Chuckles

- `origin/ftr/AST-434-production-readiness-job-list-rubrics-ui-promptrubric-diagnostic` was already integrated on local `dev` from prep-uat; merge reported **Already up to date**
- Pushed `origin/dev` (`ceec63c7` → `a5deccec`)
- Deleted `origin/ftr/AST-434-production-readiness-job-list-rubrics-ui-promptrubric-diagnostic`
- Moved to **Done** (were PR Ready): **AST-434** (parent), **AST-437**, **AST-438**

Push commit: `a5deccec`

— Chuckles

#### katherine — 2026-05-19T20:39:40.328Z
[check-linear]

Sorry — last `/check-astral` pass did not action your **@katherine** UAT note on this ticket (§0b gap on my side).

**UAT item 4 (FAILED):** grade-dot hover now shows the **rubric grade description** for that letter (e.g. C-tier text), not the vector label.
- Uses job grade row `reason` when hydrated, else artifact `grade_descriptions` on the column.
- **In Review**, **Recommended**, **Skipped** updated via shared `formatGradeDotTooltip` in `rubricDisplay.ts`.

**Branch:** `origin/ftr/AST-434-production-readiness-job-list-rubrics-ui-promptrubric-diagnostic` @ `ed226e88`

Restart app from local `dev` after pulling that ref (or merge `ftr/AST-434…` into `dev` for UAT). Status stays **User Testing** for your re-check.

#### susan — 2026-05-19T20:31:57.355Z
@katherine See the FAILED test in the comment above and resolve it with commits to the 434 branch on origin (rather than the original subissue branches).

#### susan — 2026-05-19T20:30:00.496Z
User test results:

1. Passed
2. Passed
3. WONTFIX: it's a larger issue I am addressing in [AST-448](https://linear.app/astralcareermatch/issue/AST-448/changing-importance-factors-changes-existing-scores) 
4. FAILED: I think this was misunderstood scope.  Hover over the grade icon should display human readable text relating to a C grade in that vector.
5. Same results for Recommended.
6. Same results for Skipped
7. No testing here, Applied and Responded are disabled/no-op.

I was able to synch the text across tasks, that would very helpful.

#### susan — 2026-05-19T19:49:37.012Z
@chuckles Either we never built it it or I forgot to mention here: the hover-over text/tooltip for the individual vector grade icons should be the vector-designated text for that grade, no longer the name of the vector, which we now display in the header row's tooltips.

#### chuckles — 2026-05-18T23:35:56.618Z
## UAT Ready — Chuckles (prep-uat batch)

All **2** child branches merged into parent branch and child branches deleted.

**Parent branch:** `origin/ftr/AST-434-production-readiness-job-list-rubrics-ui-promptrubric-diagnostic`

**Merged in order:**
1. **AST-437** — shared job-list rubric columns
2. **AST-438** — admin prompt/rubric diagnostic

**Deleted:** `sub/AST-434/AST-437-…`, `sub/AST-434/AST-438-…`

Local `dev` merged (prep-uat §8). Restart the app if running, then test.

`ftr` tip: `d3749908`

## Manual test steps

**Prerequisites:** App running from local `dev` (restart after merge). Use a candidate who has jobs in **In Review**, **Skipped**, and **Recommended** with rubric grades populated (e.g. one with `like_rubric` / section rubrics that include varied `importance` values).

### AST-437 — Job-list rubric columns (UI)

1. **In Review** — Open the In Review job list for your test candidate. In the table header row, confirm each rubric column shows a **short code only** (e.g. `TE`, `TM`), not a long string like `7 - Title Match (TM)`.
2. **In Review — tooltip** — Hover a rubric column header; confirm the browser tooltip is **`Label (n)`** (e.g. `Title Match (7)`), not label-only and not the old `formatRubricVectorHeader` shape.
3. **In Review — column order** — Left to right after fixed columns (title, company, …), confirm rubric columns are ordered by **descending importance** (highest-importance vector leftmost among rubric cols). Cross-check against the rubric artifact in the artifact editor if needed.
4. **In Review — grade dots** — Hover a grade dot in a rubric cell; confirm tooltip shows the **human label** (same readability as Skipped).
5. **Recommended** — Repeat steps 1–4 on the Recommended jobs table (`like_rubric` / `like_grades`). Headers and tooltips should match In Review / Skipped compact behavior.
6. **Skipped** — Open Skipped jobs. Confirm headers still show short codes with **`Label (n)`** on `<th>` tooltips (reference behavior; should be unchanged in spirit). Section expand/collapse and bulk-retry still work.
7. **Regression** — Spot-check **Applied** / **Responded** lists (no rubric columns expected). Open **Artifact editor** or an analysis header that uses `formatRubricVectorHeader`; confirm those still show the **full** header string (job-list change must not leak there).

### AST-438 — Admin prompt / rubric diagnostic (docs + script)

8. **Prompt diff report** — Read `docs/features/administrator/ast-438-prompt-diff-local-vs-production.md`. Confirm it lists compared consult + `craft_*_rubric` tasks, classifies local vs prod diffs, and explicitly notes **no production writes** were performed as part of this epic.
9. **Craft rubric tasks** — In that doc, confirm `craft_*_rubric` task keys appear (even if marked identical). Note any **CONTENT_DIFF** on consult graders (`qualify_job_listings`, `grade_*`, `evaluate_jd`) for a later sync decision (AST-373 / AST-381 — out of scope here).
10. **Optional re-run (read-only)** — From repo root, with `ASTRAL_PROD_URL` set: `python3 scripts/spikes/ast438_admin_prompt_rubric_diagnostic.py --prompt-only`. Confirm it completes without POST/upsert and refreshes snapshots under `debug/spikes/AST-438/` (gitignored).
11. **Rubric validation — deferred** — `docs/features/administrator/ast-438-rubric-validation.md` is **not** in this rollup until you name candidate id(s) on **AST-438** and Ada re-runs: `python3 scripts/spikes/ast438_admin_prompt_rubric_diagnostic.py --candidates <id>`. Skip deep rubric-data UAT for AC3 until then.

### Parent acceptance (AST-434)

12. **AC1** — Interface: Susan confirms In Review + Recommended parity with Skipped readability (steps 1–6).
13. **AC2** — Administrator prompts: written diagnostic is sufficient to decide *later* whether to sync (step 8–9); no sync performed in this epic.
14. **AC3** — Administrator rubrics: validation summary **deferred** (step 11) until candidates are designated.
15. **AC4** — No prompt sync, no rubric regeneration, no consult scoring changes in this rollup.

If testing fails on `dev`:
  `git reset --hard origin/dev`

— Chuckles

#### chuckles — 2026-05-18T17:14:15.276Z
## Dispatch — Chuckles

Dispatched **2** child tickets from the approved definition.

| Ticket | Title | Assigned to | Branch | Blocked by |
|--------|-------|-------------|--------|------------|
| [AST-437](https://linear.app/astralcareermatch/issue/AST-437) | Shared job-list rubric columns | Katherine | `sub/AST-434/AST-437-production-readiness-shared-job-list-rubric-columns` | — |
| [AST-438](https://linear.app/astralcareermatch/issue/AST-438) | Admin prompt and rubric diagnostic | Ada | `sub/AST-434/AST-438-production-readiness-admin-prompt-and-rubric-diagnostic` | — |

**Assignment rationale:**
- **Katherine:** React job-list pages (`JobsInReview`, `JobsRecommended`, `JobsSkipped`) and `rubricDisplay.ts` — frontend-only, parallel with diagnostic.
- **Ada:** `agent` / `agent_task` tables, `TASK_CONFIG` craft rubrics, read-only cross-environment comparison and written deliverables — Administrator domain.
- **Hedy:** not assigned (no tracker/dispatch work in this epic).

Susan can override any assignment by reassigning the child ticket directly.
Parent moves to **In Progress**. **prep-uat** merges child branches when all children reach **Review Posted**.

**Git (authoritative — ignore Linear `gitBranchName`):**
- Parent: `origin/ftr/AST-434-production-readiness-job-list-rubrics-ui-promptrubric-diagnostic`
- Children: `origin/sub/AST-434/AST-437-production-readiness-shared-job-list-rubric-columns`, `origin/sub/AST-434/AST-438-production-readiness-admin-prompt-and-rubric-diagnostic`

Plan attachments should use  
`https://github.com/susansomerset/astral/blob/<sub-ref-or-ftr-ref>/docs/features/...`  
after **plan-astral** lands the plan doc.

— Chuckles

#### chuckles — 2026-05-18T17:12:19.483Z
Definition updated from Susan's answers (2026-05-18):

- **Q2:** Capability B is **diagnostic only** — no sync. Findings feed docs and later AST-373/381.
- **Q3:** Fix **Recommended** too via **shared** job-list rubric column component (not a Recommended revamp).
- **Q4:** **No rubric regeneration** — validate candidate artifacts vs `craft_*` admin tasks; report only.
- **Q5:** Parent stays **AST-434**; dispatch children to **Astral Interface** (A) and **Astral Administrator** (B + C analysis).

**Open questions cleared.** Ready for your approval to dispatch.

— Chuckles

#### chuckles — 2026-05-18T17:02:42.184Z
Definition draft ready for review. Key decisions made:
- Reconstructed last night's notes into three capabilities: (A) job-list rubric headers/order, (B) local↔production admin prompt parity, (C) craft rubric output with codes + importance — with AST-373/381 called out instead of re-scoping them blindly.
- Dependencies: AST-359 and AST-428 done; prompt sync may ride AST-373 or a one-time spike per your answer.
- **5 open questions** — assignee back to you until those are answered.

**What I found in the codebase (for your review, not the definition):** In Review currently prints the full `formatRubricVectorHeader` string (`7 - Title Match (TM)`) in the column cell; Skipped shows only the two-letter `code` with `title={label}`. Recommended still uses the verbose header too. That's the "borked" behavior — fix is aligning In Review (and likely Recommended) to Skipped's compact pattern plus your tooltip format `Label (7)` and importance-desc column sort.

**Suggested resolution order after you approve (for dispatch, not committed yet):**
1. **Child — Interface (fast, unblocks UAT):** Rubric column UX on job lists (A). Katherine or similar; no backend.
2. **Child — Administrator or spike:** Prompt diff + sync (B). Either bump **AST-373** as the implementation ticket or a time-boxed Susan spike: export prod `agent`/`agent_task`, diff locally, import once.
3. **Susan + prompts — content:** Update craft_*_rubric task prompts in Manage Tasks; re-run five craft rubrics on the target candidate (C). May need a tiny schema/task-config follow-up so `importance` is in the craft response contract — dev child only if prompts alone aren't enough.

Please review the Description and comment with changes or approval.

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
