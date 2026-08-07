# AST-1052 — Processing meteorites

<!-- linear-archive: AST-1052 archived 2026-08-07 -->

## Linear archive (AST-1052)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1052/processing-meteorites  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Meteorite-sourced jobs already land under a placeholder employer ([AST-1034](https://linear.app/astralcareermatch/issue/AST-1034/support-meteorite-jobs)) and can be created from matched email ([AST-1044](https://linear.app/astralcareermatch/issue/AST-1044/bind-email-to-candidate)), but they still sit on the normal GDL funnel — score-floor gated, and LIKE assumes a real hiring company with website/culture content we do not have. This epic gives meteorite jobs a **parallel GDL processing track** starting at **METEORITE_NEW**, running JD → DO → GET → LIKE → upshot with **dispatch** `score_floor` **0**, a **meteorite_like** (and meteorite upshot) agent task that keeps the same rubrics while telling Grace to use grade **X** more liberally when company signal is missing, and a **Meteorites** section on Recommended.

## Functional scope

* Register a **parallel meteorite job-state track**: entry **METEORITE_NEW**, then **METEORITE_PASSED_JD** → **METEORITE_PASSED_DO** → **METEORITE_PASSED_GET** → **METEORITE_PASSED_LIKE** (plus matching fail / technical-fail siblings needed for real step failures). Meteorite jobs move on these states only — not the vetted-company GDL trail.
* Add **new dispatch_task rows** that invoke the **same** underlying GDL tasks (`evaluate_jd`, `grade_do`, `grade_get`) with meteorite equivalent **trigger / input states**, each with `score_floor` **= 0** (always claimable by score; pass vs fail still comes from grading / real failures).
* **Skip** `fetch_culture_pages` / **CULTURE_READY** for meteorites. After **METEORITE_PASSED_GET**, LIKE is claimed via a new agent task `meteorite_like` (dispatch trigger **METEORITE_PASSED_GET**) — same like rubric as `grade_like`, prompt almost identical but states the job did not come from a known company (no vibe/culture pages), and Grace should do her best and use grade **X** (existing “not applicable / no signal”, confidence 0) more liberally when information is insufficient.
* Add a **meteorite version of the final upshot** agent task (same idea: emphasize lack of company visibility) so synthesis after **METEORITE_PASSED_LIKE** matches the meteorite context.
* Show **Meteorites as their own section** on the Recommended page (distinct from normal recommended jobs).
* Manage Email / Read Email **Create** (and the meteorite create path it calls) lands new meteorite jobs in **METEORITE_NEW** (first state of the meteorite track), not the normal **JD_READY** create default from [AST-1034](https://linear.app/astralcareermatch/issue/AST-1034/support-meteorite-jobs).
* When `debug=True` on meteorite GDL processing paths, emit Style D found→recorded detail (index headers + `|` working lines); no new contract lines when `debug=False`.

## Architectural definition

* **Patterns to reuse**
  * `pattern.state.entity-state-transitions` — **METEORITE\_*** states in `JOB_STATES` with `prior_states`; core chooses transitions.
  * `pattern.config.config-block` — state names, dispatch defaults (`score_floor` 0), `meteorite_like` / meteorite-upshot prompt literals, create landing **METEORITE_NEW** in config.
  * `pattern.batch.entity-claim-process-release` — meteorite GDL still claim → process → release.
  * `pattern.layers.import-discipline` — core orchestration; UI owns Recommended Meteorites section + Create landing behavior.
* **New patterns proposed**
  * **Parallel meteorite GDL state track** — sibling chain (**METEORITE_NEW** → **METEORITE_PASSED\_*** …) claimed by meteorite-scoped dispatch rows, distinct from the vetted-company chain. Flag for Archie approval before plans treat it as catalog law.
  * **Company-absent agent_task twin** — `meteorite_like` / meteorite upshot: same rubric, alternate task prompt (no vibe pages; liberally use grade **X**). Flag for Archie approval.
* **Applicable statutes**
  * `astral.state.core-decides-transitions` — meteorite transitions in core from registries.
  * `astral.state.job-prior-states-enforced` — legal priors for every meteorite hop (create into **METEORITE_NEW** must be a lawful entry).
  * `astral.state.no-daisy-chain-in-run` — one dispatch cycle one logical hop (existing `run_next` carve-out only).
  * `astral.config.pass-threshold-vs-score-floor` — meteorite dispatch rows use `score_floor` **0**; do not confuse with `pass_threshold` grading math.
  * `astral.config.config-source-of-truth` — states, tasks, prompts, create landing in config.
  * `astral.standards.no-hardcoded-sets` — no inline meteorite state / task sets outside config.
  * `astral.batch.claim-process-release` / `astral.batch.batch-id-first` — batch claim discipline unchanged in shape.
  * `astral.standards.debug-contract-gated` — Style D only when `debug=True`.
  * `astral.standards.database-header-inventory` — no new tables.
  * `astral.layers.import-direction` — API/dispatcher/UI → core → data.
  * `universal` set — product code changes.

## Boundaries

* Does **not** invent SEEK_COMPANY / website resolution for `meteorite-*` placeholders, and does **not** run `fetch_culture_pages` / **CULTURE_READY** for meteorites.
* Does **not** alter the normal (non-meteorite) GDL state chain, culture hop, or score-floor behavior for vetted-company jobs.
* Does **not** change Gmail ingest or From→candidate bind rules ([AST-1031](https://linear.app/astralcareermatch/issue/AST-1031/receive-email-on-gmail-account-for-astral) / [AST-1044](https://linear.app/astralcareermatch/issue/AST-1044/bind-email-to-candidate)) beyond Create landing state **METEORITE_NEW**.
* Does **not** redefine like / do / get / JD **rubric content** — rubrics stay the same; meteorite differences are **dispatch rows**, **states**, and **agent_task prompts** (`meteorite_like`, meteorite upshot).
* Does **not** scrape employer culture/vibe pages for meteorite companies.
* Must not break existing dispatch claims for normal **PASSED_JD** / **PASSED_DO** / **PASSED_GET** / **CULTURE_READY** / **PASSED_LIKE** jobs or the existing Recommended (non-meteorite) section.

## Acceptance criteria

1. Config registers **METEORITE_NEW**, **METEORITE_PASSED_JD**, **METEORITE_PASSED_DO**, **METEORITE_PASSED_GET**, **METEORITE_PASSED_LIKE** (and needed fail / technical-fail siblings) with legal `prior_states`.
2. New dispatch_task rows claim meteorite GDL hops for `evaluate_jd` / `grade_do` / `grade_get` at the meteorite input states with `score_floor` **= 0**; those hops do not exclude jobs for low `latest_score`.
3. No meteorite path requires `fetch_culture_pages` / **CULTURE_READY**; after **METEORITE_PASSED_GET**, `meteorite_like` runs (same like rubric; prompt omits vibe-page assumptions and tells Grace to use grade **X** more liberally when info is thin).
4. After meteorite LIKE, a **meteorite upshot** task runs with company-visibility caveats in the prompt.
5. Recommended UI shows a distinct **Meteorites** section for meteorite jobs that reach the post-upshot / recommended surface.
6. Manage Email **Create** (meteorite create path) inserts jobs in **METEORITE_NEW**.
7. Genuine step failures still land on meteorite fail / technical-fail states; non-meteorite GDL + Recommended behavior unchanged (smoke).
8. With `debug=True` on meteorite GDL processing, Style D index + `|` detail is present; with `debug=False`, no new debug-contract lines from those paths.

## Dependencies and blockers

* [AST-1034](https://linear.app/astralcareermatch/issue/AST-1034/support-meteorite-jobs) (Support meteorite jobs) — placeholder company + create API foundation; this epic retargets create landing to **METEORITE_NEW**.
* Related: [AST-1044](https://linear.app/astralcareermatch/issue/AST-1044/bind-email-to-candidate) — Manage Email Create wiring that this epic retargets to **METEORITE_NEW**.
* none otherwise.

## Open questions

none

## Proposed child tickets

#### 1!!!: **Meteorite GDL parallel job states - Ada**

Owns `JOB_STATES` for **METEORITE_NEW** and **METEORITE_PASSED_JD / DO / GET / LIKE** (plus fail / technical-fail siblings), priors, and UI manifests as needed. Does **not** own dispatch rows, agent_task prompt bodies, Create retarget, or Recommended section.
**Citations:** `pattern.state.entity-state-transitions`; `pattern.config.config-block`; `astral.state.job-prior-states-enforced`; `astral.state.core-decides-transitions`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`.

#### 2!: **Meteorite GDL dispatch rows (score_floor 0) - Hedy**

Owns new dispatch_task rows that call the same `evaluate_jd` / `grade_do` / `grade_get` tasks with meteorite input states and `score_floor` **= 0**, plus dispatch wiring for `meteorite_like` @ **METEORITE_PASSED_GET** and the meteorite upshot trigger. After #1. Does **not** author the agent_task prompt text (child 3).
**Citations:** `pattern.batch.entity-claim-process-release`; `astral.config.pass-threshold-vs-score-floor`; `astral.batch.claim-process-release`; `astral.standards.debug-contract-gated`; `astral.standards.no-hardcoded-sets`.

#### 3!: **meteorite_like + meteorite upshot agent tasks - Katherine**

Owns agent_task `meteorite_like` (same like rubric; no vibe-page assumptions; liberally use grade **X**) and the meteorite **upshot** twin (emphasize lack of company visibility). After #1; pairs with #2 for dispatch triggers. Does **not** own Recommended UI or Create landing.
**Citations:** `pattern.config.config-block`; company-absent agent_task twin (new-pattern flag); `astral.config.config-source-of-truth`.

#### 4: **Create lands meteorite jobs in METEORITE_NEW - Hedy**

Owns retargeting meteorite create (Manage Email **Create** / create path / `METEORITE_CONFIG` create default) so new jobs start in **METEORITE_NEW**. After #1. Does **not** own GDL processing or Recommended section.
**Citations:** `pattern.config.config-block`; `astral.state.job-prior-states-enforced`; `astral.config.config-source-of-truth`.

#### 5: **Recommended page Meteorites section - Katherine**

Owns a distinct **Meteorites** section on Recommended for meteorite-track jobs (post-upshot / recommended surface). After #1; needs #3 upshot semantics for correct membership. Does **not** own GDL states or dispatch.
**Citations:** `pattern.layers.import-discipline`; `astral.layers.import-direction`; `astral.config.config-source-of-truth`.

**New patterns:** Child 1 introduces the parallel meteorite GDL state track; child 3 introduces company-absent agent_task twins (`meteorite_like`, meteorite upshot).

**Monolith check:** Functional scope has 7 capabilities; 5 children (states / dispatch / prompts / create / Recommended) — intentional layer split.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-1052 (parent) | ftr/AST-1052-processing-meteorites |
| AST-1053 | sub/AST-1052/AST-1053-meteorite-gdl-parallel-job-states |
| AST-1054 | sub/AST-1052/AST-1054-meteorite-gdl-dispatch-rows-score-floor-0 |
| AST-1055 | sub/AST-1052/AST-1055-meteorite-like-meteorite-upshot-agent-tasks |
| AST-1056 | sub/AST-1052/AST-1056-create-lands-meteorite-jobs-in-meteorite-new |
| AST-1057 | sub/AST-1052/AST-1057-recommended-page-meteorites-section |

**Epic worktree:** `astral-AST-1052/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **Thread** column is the fully-qualified `store.db` path (UUID is the directory name — extract for `agent --resume`). **datt resume:** read this table — not chat memory. One UUID per agent; never the parent Chuckles Thread UUID.

| Agent | Role | Thread |
| -- | -- | -- |
| Katherine | engineer | `/home/susan/.cursor/chats/b36a807f3f90f0412c9849e1018d0e22/5a599caa-2ab6-4227-bcba-bb38795f62bd/store.db` |
| Hedy | engineer | `/home/susan/.cursor/chats/b36a807f3f90f0412c9849e1018d0e22/32a0c6c0-2099-4b97-baa8-e48095b506b3/store.db` |
| Ada | engineer | `/home/susan/.cursor/chats/b36a807f3f90f0412c9849e1018d0e22/1435db58-ae87-4b74-8a59-a276592304c5/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/1223ef33-6442-4b3f-a048-7a7c8d1a7715/store.db` |
| Radia | review | `/home/susan/.cursor/chats/b36a807f3f90f0412c9849e1018d0e22/796b52dd-2830-43c6-a8aa-cf6897426e99/store.db` |

---

## Original brief

I think we need a new set of job states for meteors.

Meteorites should go through all the GDL analysis without score floors, only failing on failures.

By virtue of being meteorites the jobs will have their own states that will parallel the other states but will have a slightly different like prompt because we will not have visibility to the hiring company.  We will use the same like rubric but explicitly update the task prompt for meteorites to tell Grace to use X if she doesn't have enough info.

### Comments

#### chuckles — 2026-07-29T21:49:17.974Z
[thread-missing] Katherine Team store.db for 8832dc67-b1ce-46ea-89d7-4ae2e002c6de missing on this host; minted 45967123-7867-4789-9a36-3ae19b80d6d6 and updated ## Team. — Chuckles

#### chuckles — 2026-07-29T21:03:53.407Z
@susan — open questions before this can move to Todo:

1. Insufficient-info fallback **“X”** — what should Grace use when she does not have enough info?
2. Score floors vs `pass_threshold` — disable dispatch `score_floor` only (still grade pass/fail), or also never soft-fail on score?
3. Culture hop — skip `fetch_culture_pages` / CULTURE_READY for meteorites and LIKE from a meteorite LIKE-ready state after GET?
4. Entry — stay on JD_READY from AST-1034 and branch by `meteorite-*`, or explicit meteorite entry state?
5. Post-LIKE — analysis_upshot / RECOMMENDED / artifacts in this epic, or stop at meteorite PASSED_LIKE / FAILED_LIKE?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
