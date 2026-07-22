# AST-754 — vet_inflow seems to have been skipped?

<!-- linear-archive: AST-754 archived 2026-07-22 -->

## Linear archive (AST-754)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-754/vet-inflow-seems-to-have-been-skipped  
**Status at archive:** Archive  
**Project:** Astral Roster  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Roster **inflow_discovery** currently daisy-chains an inline **vet_inflow_discovery** call inside the candidate batch (logs show `run_next chain entry` under the discovery batch id). Susan does not see evidence the vet task runs with its **Admin prompt content** as a proper schedulable step — and it must not daisy-chain. Each hop is its own **dispatch_tasks** row and Scheduled Actions step; **run_next** is not used between discovery and vet.

This epic fixes discovery so it only records deduped CSE hits, then lets **vet_inflow_discovery** run as a separate company dispatch on **NEW** — with real prompt assembly — before any homepage fetch or scrape.

## Functional scope

**Authoritative discovery funnel (Scheduled Actions — not buried inline code):**

| Step | Dispatch task | Trigger → outcome |
| -- | -- | -- |
| 1 | **inflow_discovery** | candidate search terms → **NEW** company row per deduped CSE hit (blurb stored; dedupe against known company links for the candidate) |
| 2 | **vet_inflow_discovery** | **NEW** → **WEBSITE_FOUND** (pass) or **VET_FAILED** (reject) |
| 3 | **fetch_website** | **WEBSITE_FOUND** → **HOMEPAGE_READY** (navlinks captured) |
| 4 | **prefilter_company** | **HOMEPAGE_READY** → **PREFILTER_PASSED** or **PREFILTER_FAILED** (PJLs + culture links) |
| 5 | **fetch_job_pages** | **PREFILTER_PASSED** → **PJL_READY** |
| 6 | **select_job_page** | **PJL_READY** → **JOBLIST_IDENTIFIED** or **PREFILTER_PASSED_RETRY** (new PJLs merged) |
| 7 | **parse_job_list** | **JOBLIST_IDENTIFIED** → **WATCH** / **NO_OPENINGS** / **JOBLIST_PARSE_ERROR** (or equivalent terminal) |

1. **Discovery only:** **inflow_discovery** runs CSE per stale term, URL-dedupes hits against the candidate's existing company URLs, and creates **NEW** rows with the deduped CSE blurb on the company record. No inline vet LLM call; no **WEBSITE_FOUND** from discovery.
2. **Separate vet dispatch:** **vet_inflow_discovery** is a **company** dispatch on **trigger_state NEW**. It reads the stored discovery blurb, runs through the **Admin-configured agent_task prompts** for **vet_inflow_discovery** (not a hidden in-batch call), and transitions pass → **WEBSITE_FOUND** or reject → **VET_FAILED** (terminal; dedupe prevents re-recording the same bad link).
3. **Mechanical vet scope only:** **vet_inflow_discovery** rejects only link types that are not useful for downstream job-page search — e.g. news articles, Wikipedia pages, directory/listicle pages, Better Business Bureau listings, job-board posts, social profiles. It does **not** filter on the candidate's behalf (no role fit, industry preference, company quality, or "good match for this candidate" judgment). Pass/fail is literal: *does this link plausibly refer to a company we can pursue for job listings, or is it the wrong kind of page?*
4. **Vet prompt updated:** The **vet_inflow_discovery** Admin Task Prompts text is revised to state the mechanical-only scope above (including local/UAT prompt row so Susan's dev database reflects it).
5. **No daisy-chain / no run_next:** Remove hardcoded inline **do_task(vet_inflow_discovery)** from the discovery batch. Discovery completion must not invoke vet under the discovery batch id. **run_next** is not required or appropriate between these steps.
6. **Downstream unchanged in intent:** After **WEBSITE_FOUND**, the existing Scheduled Actions chain (**fetch_website** → **prefilter_company** → …) applies as today. **inflow_resolve_website** is not part of this discovery funnel.
7. **Zero-hit discovery is success:** CSE with zero URL-deduped hits after candidate dedupe completes successfully — distinct from vet rejecting candidates.
8. **Debug traceability (**`debug=True`**):** Per AST-538, logs show discovery recording into **NEW**, separate vet dispatch with prompt-backed execution, **VET_FAILED** / **WEBSITE_FOUND** transitions, and downstream eligibility — Style D index headers with `|` detail.

## Boundaries

* Does not redesign Phase 0 search-term artifacts (AST-504) or per-term staleness cadence (AST-525).
* Does not use **run_next** to link **inflow_discovery** → **vet_inflow_discovery**.
* Does not change manual **IMPORTED** import paths.
* Does not add Betty log-string tests for debug output.
* Does not rework unrelated dispatch-task seeding (AST-741) except rows/states needed for **vet_inflow_discovery** on **NEW** and **VET_FAILED**.
* **inflow_resolve_website** / legacy "Phase 2 resolve" is out of scope — Susan's chain goes **NEW** → vet → **WEBSITE_FOUND** → **fetch_website**.
* Candidate-fit filtering belongs in **prefilter_company** and later steps — not in **vet_inflow_discovery**.

## Acceptance criteria

1. **inflow_discovery** creates **NEW** rows from deduped CSE hits (candidate URL dedupe applied) and does **not** call **vet_inflow_discovery** inside that batch (no shared batch id, no inline **do_task**).
2. **vet_inflow_discovery** runs only as a company dispatch on **NEW** rows, using Admin **vet_inflow_discovery** prompts (observable as a distinct dispatch batch on the company entity).
3. Vet pass → **WEBSITE_FOUND**; vet reject → **VET_FAILED**; rejected URLs are not re-recorded on later discovery runs.
4. Susan's example class (`inflow_discovery-24004a9a-8835-4733-97ba-64cce70fde38`) cannot recur: discovery batch logs must not show **vet_inflow_discovery** LLM activity under the discovery batch id.
5. **vet_inflow_discovery** prompt text (Admin Task Prompts / local dev row) explicitly limits vetting to mechanical link-type rejection — articles, wiki, directories, BBB listings, job boards, etc. — and forbids candidate-fit filtering at this stage.
6. Zero deduped hits → **inflow_discovery** success with explicit nothing-to-record semantics.
7. After vet **WEBSITE_FOUND**, **fetch_website** dispatch can run and the downstream chain in the table above remains reachable via Scheduled Actions.
8. With `debug=True`, Susan can trace discovery record → separate vet dispatch → **WEBSITE_FOUND** / **VET_FAILED** per AST-538.

## Dependencies and blockers

* Roster inflow on the integration line (AST-490 / AST-505 — supersedes inline vet in the discovery batch).
* Admin: **vet_inflow_discovery** agent + prompts on the **agent_task** row (required for AC #2 and #5).

## Open questions

none.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-754 (parent) | ftr/AST-754-vet-inflow-discovery-split |
| AST-775 | sub/AST-754/AST-775-split-inflow-discovery-record-new-only |
| AST-776 | sub/AST-754/AST-776-vet-inflow-company-dispatch-mechanical-prompt |
| AST-785 | sub/AST-754/AST-785-dispatch-tasks-missing-from-scheduled-actions-ui |

**Epic worktree:** `astral-AST-754/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Hedy | engineer | fa288fcd-cbd1-417d-aeee-2641d617c297 |
| Katherine | engineer | 0567e1bd-18de-47bc-b65c-311fdf287705 |
| Betty | qa | 8c9d1c91-9977-4d8d-bd9b-ce31417923b3 |
| Radia | review |  |

---

## Original brief

We wanted to vet the links we have before we fetch their web pages, I thought.  That's what vet_inflow_discovery was supposed to do, right? to weed out the obvious duds from a deduped list?

### Comments

#### chuckles — 2026-06-25T02:00:52.518Z
[check-linear] User Testing — empty Scheduled Actions: verify AST-785 on staging (@susan)

#### chuckles — 2026-06-24T05:46:41.226Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-785** | dispatch_task rows missing from Scheduled Actions UI (vet inflow seems to have been skipped?) |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-785** — _dispatch_task rows missing from Scheduled Actions UI (vet inflow seems to have been skipped?)_
- **Issue reported:** Admin → **Scheduled Actions** shows no dispatch task rows (empty state / nothing usable on the page) while the `dispatch_task` table contains rows for the active candidate — Susan confirmed DB records exist; browser console shows no error.
- **Should now:** Configured `dispatch_task` rows appear on **Scheduled Actions** so Susan can run **vet_inflow_discovery**, **fetch_website**, and downstream inflow chain steps from the admin UI (grouped sections expandable with visible rows).
- **Quick check (this fix only):**
  1. On staging/local after AST-754 prep-uat (`origin/dev` includes vet split).
  2. Confirm `dispatch_task` rows exist in DB for candidate (e.g. `somerset`) including inflow/vet keys.
  3. Open Admin → **Scheduled Actions**.
  4. Observe empty UI / no visible rows despite DB records; no console error.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-06-24T05:23:14.349Z
@chuckles There are records in the dispatch_task table, but there is nothing appearing on scheduled_actions, and no error in the console.

#### chuckles — 2026-06-24T05:08:09.745Z
**[refresh-ftr] blocked:** merge `origin/dev` into `origin/ftr/AST-754-vet-inflow-discovery-split` — CONFLICT:

- `docs/test-bible/core/roster.md`, `docs/test-bible/utils/config.md`, `tests/component/core/test_roster.py` → @Betty White
- `src/core/roster.py`, `src/utils/config.py` → @Hedy Lamarr

Both children **User Testing** on ftr @ `46ad8dc`. Re-run refresh-ftr after reconcile.

— Chuckles

#### chuckles — 2026-06-24T02:59:53.489Z
[thread-missing] blocked: Cursor agent transcript for `ed6a4399-212d-4f0e-8b12-2919dbb853c5` is not on this host (petrichor). Run this job from **chuckles server (HP ProDesk)** where that conversation exists.

Do **not** `agent create-chat` or `--resume` here — that forks a new thread the other host cannot use.

Watcher rule `datt` on `AST-754`.

— Chuckles

#### chuckles — 2026-06-23T21:14:09.790Z
@susan

Pipeline resumed: **AST-775** merged to `origin/ftr/AST-754-vet-inflow-discovery-split`. **AST-776** build complete @ `3ca4eb8` — blocked spawning Betty **qa-child**: Cursor agent API usage limit (Ultra cycle resets 2026-06-24).

Reassign parent to Chuckles after limit clears to finish qa → test → review → resolve → merge-child → prep-uat.

— Chuckles

#### chuckles — 2026-06-23T21:02:58.747Z
**[merge-child] blocked:** `validate-sub-log.sh` rejects `origin/sub/AST-754/AST-775-split-inflow-discovery-record-new-only` — **Merge remote-tracking branch** subjects in sub-only range (from `merge-tests(AST-775)` pulling `origin/tests` history). Republish sub from `origin/ftr/AST-754-vet-inflow-discovery-split` with a clean single `merge-tests(AST-775)` (no pull-merge subjects in range).

@Betty White — tests/bible hygiene on **AST-775** publish ref.

— Chuckles

#### susan — 2026-06-23T18:50:48.539Z
This is great, but I would like to also add that the vet_inflow_discovery prompt should only be weeding out cases of "THIS IS AN ARTICLE/WIKIPAGE/BETTERBUSINESSBUREAULISTING, NOT A COMPANY WEBSITE."  We do not want ANY filtering on the candidate's behalf happening at this stage, just a literal, mechanical "Is this a link that talks about a company, or is it not going to useful to us for the job page search?"

Please be sure the prompt is updated to reflect that in the astral.db file.

#### chuckles — 2026-06-23T18:12:38.538Z
@susan

Definition updated from your answers + log snippet (`inflow_discovery-24004a9a-8835-4733-97ba-64cce70fde38`).

1. When vet rejects a **NEW** inflow row, should the company be deleted, moved to a terminal reject state (which name?), or left in **NEW**?
2. After vet accepts and supplies an optional homepage URL, may the company go directly to **WEBSITE_FOUND** (skipping Phase 2 resolve), or must website resolution always run as a separate dispatch step after vet pass?

— Chuckles

#### susan — 2026-06-23T18:05:21.834Z
Log output:

\[2026-06-23 18:00:09\] INFO src.external.deepseek: LLM deepseek task=vet_inflow_discovery 52.6s stop=end_turn tokens in=65110 out=8104

\[2026-06-23 18:00:09\] INFO src.core.agent: do_task(vet_inflow_discovery) completed successfully batch_id=inflow_discovery-24004a9a-8835-4733-97ba-64cce70fde38 index=somerset

\[2026-06-23 18:00:09\] INFO src.core.roster: ingest_new_companies: duplicate URL for midamerican_energy candidate somerset

\[2026-06-23 18:00:09\] WARNING src.core.roster: ingest_new_companies: slug 'aveva' owned by another candidate

\[2026-06-23 18:00:09\] INFO src.core.roster: ingest_new_companies: duplicate URL for neighborly_software candidate somerset

\[2026-06-23 18:00:09\] INFO src.core.roster: ingest_new_companies: duplicate URL for ambience_healthcare candidate somerset

\[2026-06-23 18:00:09\] INFO src.core.roster: ingest_new_companies: duplicate URL for cadence candidate somerset

\[2026-06-23 18:00:09\] INFO src.core.roster: ingest_new_companies: duplicate URL for fortive candidate somerset

\[2026-06-23 18:00:09\] INFO src.core.roster: ingest_new_companies: duplicate URL for clarium candidate somerset

\[2026-06-23 18:00:09\] INFO src.core.roster: ingest_new_companies: duplicate URL for hike_medical candidate somerset

\[2026-06-23 17:59:39\] INFO src.core.agent: run_next chain entry: task=vet_inflow_discovery batch_id=inflow_discovery-24004a9a-8835-4733-97ba-64cce70fde38

\[2026-06-23 17:58:06\] INFO dispatch.scheduler: Dispatching inflow_discovery — 1 available, batch inflow_discovery-24004a9a-8835-4733-97ba-64cce70fde38

#### chuckles — 2026-06-23T17:54:05.138Z
@susan

1. Which run showed the skip (approx date/time, candidate id, dispatch batch id if available)?
2. Did logs show CSE hits collected but no **vet_inflow_discovery** activity in the same batch?
3. Did new companies or website-resolution steps appear without a vet pass in that same batch?
4. When CSE returns hits but URL dedupe yields zero unique URLs, should **inflow_discovery** still report success, or should that be a distinct outcome from "vet rejected all duds"?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
