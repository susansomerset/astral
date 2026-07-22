# AST-717 — Store only the latest rubric results in <entity>_data

<!-- linear-archive: AST-717 archived 2026-07-22 -->

## Linear archive (AST-717)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-717/store-only-the-latest-rubric-results-in-entity-data  
**Status at archive:** Archive  
**Project:** Astral Roster  
**Assignee:** susan  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-378

### Description

## Purpose

Repeated rubric-backed consult runs (joblist qualify, JD evaluate, DO/GET/LIKE, company prefilter, and the same class of scored steps) have been leaving prior outcomes on the entity row. That clutters entity modals and the Recommended Job Report consult tabs with duplicate-looking results for the same phase. Susan needs each entity's working snapshot to reflect only the latest rubric outcome while full per-run audit remains in agent_data for history and debugging.

## Functional scope

* When a rubric-backed consult or prefilter step runs again for the same entity, replace — do not accumulate — that step's outcome fields on the entity data blob (grades, associated score, associated notes for that phase).
* Apply to job and company entities for every scored consult phase in the standard pipeline (joblist, JD, DO, GET, LIKE) and company prefilter; include any sibling scored steps that persist rubric outcomes into entity data the same way.
* Preserve complete per-run prompt/response blocks in agent_data; this epic does not reduce agent_data retention or block storage.
* Entity modals (job detail, company detail) and Recommended Job Report consult phase panes show one current rubric result per consult phase — not multiple tabs or sections for reruns of the same phase. Dedup key: one latest entry per task_key for modal navigation.
* Job dispatch gating that reads consult scores (e.g. score floor on PASSED_* states) uses the score from the latest run for that phase.
* Manual reruns (dispatch, admin ad hoc, retry/holding states) follow the same latest-only rule on the entity row.
* Ship a one-time backfill script that cleans existing job and company entity rows: collapse accumulated rubric outcome data and duplicate agent_responses entries to latest-only per task_key, without deleting agent_data history.

## Boundaries

* Does not change how rubric criteria are authored or stored on the candidate (artifact definitions stay as-is).
* Does not implement runtime rubric validation or per-vector feedback storage (AST-378 — adjacent, out of scope).
* Does not remove admin or agent_data access to historical runs; only the entity working snapshot and consumer-facing entity navigation are latest-only.
* Does not change debug logging contracts (AST-538).
* Does not alter batch locking, state-machine rules, or dispatch ledger behavior beyond reading the updated latest scores/grades.

## Acceptance criteria

* Running the same scored consult phase twice on one job leaves a single current grades payload for that phase on the job's data blob, matching the second run; associated score and notes fields for that phase match the second run only.
* agent_data still contains distinct blocks for both runs after the scenario above.
* The job entity modal shows one navigable result for that consult phase (e.g. one consult_get entry), not multiple tabs for reruns of the same phase.
* Recommended Job Report JD / DO / GET / LIKE tabs display grades from the latest run only.
* Re-running company prefilter replaces prefilter grades/score/notes on company_data without accumulation; the company entity modal shows one current prefilter result.
* Dispatch eligibility that depends on latest consult score reflects the most recent scored run after a rerun.
* No regression: first-time runs still persist outcomes and populate entity modals as they do today.
* Backfill script: after running against the current database, entities that previously had duplicate rubric outcomes or duplicate agent_responses entries per task_key show latest-only data on the entity row; agent_data rows are untouched.

## Dependencies and blockers

none.

## Open questions

none.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-717 (parent) | ftr/AST-717-store-only-latest-rubric-results-in-entity-data |
| AST-726 | sub/AST-717/AST-726-latest-only-rubric-writes-and-modal-dedup |
| AST-727 | sub/AST-717/AST-727-backfill-latest-only-rubric-entity-data |

## Team (authoritative — headless `--resume` thread ids)

| Agent | Role | Thread |
| -- | -- | -- |
| Hedy | engineer | ad4b0364-f60b-47f1-a8ac-640c513a5ec0 |
| Betty | qa | a3530942-ab01-46f8-aec0-d81a493aaa6b |
| Radia | review | 2d2de752-9ebf-4055-8395-dccf97c17f4b |

---

## Original brief

We have been appending to the rubric content for repeated runs of get/do/like/evaluate, etc.  While we want to keep that data in the agent_data table for historical reference, the actual entity record (candidate/job/company) should store only the latest results, so that the navigation of the entity modal doesn't show multiple results for consult_get, etc.

### Comments

#### chuckles — 2026-06-25T02:00:55.353Z
[check-linear] answered (@susan) — prep-uat §9 handoff posts UAT steps on the parent Description; AST-717 is Done on the integration line

#### chuckles — 2026-06-18T04:17:19.442Z
[check-linear] User Testing — UAT tick-list posted (@susan)

**Re: prep-uat skill** — `prep-uat` lands `ftr` on `dev`, pushes staging, and hands the parent to you. It does **not** auto-post a browser UAT tick-list anymore. When you need setup + test steps, `@chuckles` on the parent (here) or ask during prep — I'll post the checklist in-thread like **AST-512**.

**Prereq:** `origin/dev` deployed to Railway staging (prep-uat landed **`c7bf216d`**). Local optional: `cd astral && git checkout dev && git pull origin dev`.

---

### Slice A — Runtime latest-only writes (**AST-726**, staging UAT)

Pick one job already past a scored consult phase (GET/DO/LIKE/JD) and one company past prefilter.

- [ ] **Job rerun:** Re-dispatch the **same** scored consult phase (Scheduled Actions or ad hoc). Entity modal side tabs show **one** navigable entry for that phase (`task_key`), not duplicate tabs for the rerun.
- [ ] **Latest grades:** Recommended Job Report consult tabs (JD / DO / GET / LIKE) show grades/scores from the **second** run only.
- [ ] **History preserved:** Execution History / agent_data still shows **both** runs (distinct blocks) after the rerun.
- [ ] **Company prefilter rerun:** Re-run prefilter on a company; company modal shows one current prefilter result; `prefilter_grades` / score / notes match latest run only (no accumulation).
- [ ] **No regression:** First-time consult/prefilter on a fresh entity still persists and displays normally.

**Known cosmetic (Radia discuss — not a fail):** rerunning one phase can reorder modal tab order among keys; still one entry per key.

---

### Slice B — Backfill script (**AST-727**, **local DB only** — staging not required)

Run against a **copy** of your SQLite (backup first). Script docstring in `scripts/migrations/backfill_latest_only_rubric_entity_data.py`.

- [ ] **Backup:** `cp data/astral.db data/astral.db.pre-AST-727-$(date +%Y%m%d)`
- [ ] **Dry-run full scan:** `python scripts/migrations/backfill_latest_only_rubric_entity_data.py --dry-run` — review counts; spot entities with duplicate refs.
- [ ] **Spot-check:** `--dry-run --job <astral_job_id>` and/or `--company <short_name>` on a row you know had duplicate `agent_responses` tabs.
- [ ] **Live run (after OK):** same command without `--dry-run` — re-open those entities; one ref per `task_key` in modal navigation.
- [ ] **agent_data untouched:** optional `SELECT COUNT(*) FROM agent_data` before/after — unchanged.

Candidates excluded by design.

---

### Out of scope for this pass

- Tab-order stability across reruns (discuss item — defer unless you want it in this epic).
- Clearing stale `joblist_score` on qualify fail path (advisory — separate if needed).

— Chuckles

#### chuckles — 2026-06-18T04:16:49.721Z
[check-linear] User Testing — UAT instructions (origin/dev @ c7bf216, Railway staging)

**Runtime (AST-726) — pick one job that already ran a consult phase twice, or rerun from admin/dispatch:**
1. Run the same scored phase twice (e.g. consult_get) on one job.
2. Job entity modal: exactly **one** side tab for that phase (not two consult_get tabs); grades/score/notes match the **second** run.
3. Recommended Job Report JD/DO/GET/LIKE tabs: grade dots reflect **latest** run only.
4. Re-run company prefilter on a company with prior prefilter: one prefilter tab; `prefilter_grades`/notes match second run.
5. Optional sanity: confirm `agent_data` still has blocks from both runs (admin/agent story RESPONSE blocks) — history not deleted.

**Backfill (AST-727) — production DB only when ready; not required for browser UAT of runtime behavior:**
1. Backup DB.
2. `python scripts/migrations/backfill_latest_only_rubric_entity_data.py --dry-run`
3. Spot-check a noisy entity id from dry-run output.
4. Live run without `--dry-run`; re-open entity modals — duplicate tabs per `task_key` should collapse to latest.

Pass → move parent to **PR Ready**. Fail → comment on parent with repro; assignee Chuckles.

— Chuckles

#### susan — 2026-06-18T04:14:49.041Z
@chuckles I need testing instructions, please.  That's still included in the prep-uat skill, right?

#### chuckles — 2026-06-18T00:06:14.313Z
@susan

1. Should we backfill existing entity rows that already have accumulated/duplicate rubric outcome data, or only enforce latest-only behavior on new runs going forward?

— Chuckles

#### chuckles — 2026-06-18T00:05:53.349Z
@susan — open questions before dispatch:

1. **Backfill:** One-time dedupe of existing duplicate `agent_responses` / rubric blobs, or forward-only (re-run entities as needed)?
2. **Dedup key:** One latest entry per `task_key` for modal navigation — or separate slots per trigger state?
3. **Project home:** Keep parent under **Astral Roster**, or move to a cross-cutting Agent/Consult epic?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
