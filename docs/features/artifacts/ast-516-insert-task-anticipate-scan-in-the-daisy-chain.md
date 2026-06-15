# AST-516 — Insert task "anticipate_scan" in the daisy chain

<!-- linear-archive: AST-516 archived 2026-06-15 -->

## Linear archive (AST-516)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-516/insert-task-anticipate-scan-in-the-daisy-chain  
**Status at archive:** Done  
**Project:** Astral Artifacts  
**Assignee:** susan  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-313; related: AST-513; related: AST-450

### Description

## Purpose

The resume artifact pipeline today moves from Judith’s job contemplation straight into Estelle’s resume-revision guidance. That skips a dedicated ATS and first-pass recruiter lens before anyone advises what to emphasize on the resume. Susan wants Atlas in that gap: after the job has been contemplated for the artifact chain, Atlas produces keyword and emphasis guidance aimed at surviving automated ATS screening and a skeptical human skim — so downstream resume steps are grounded in scan reality, not only narrative fit.

## Functional scope

* Register a new artifact-pipeline task key `anticipate_scan` in the same dumb-chain registry pattern as the existing Phase E keys — selectable in Manage Tasks, not a new dispatch entry point.
* Position `anticipate_scan` in the **resume** daisy chain **after** `contemplate_job` and **before** `advise_job_resume`, wired only via `run_next` in Manage Tasks (Susan sets `contemplate_job` **→** `anticipate_scan` **→** `advise_job_resume`).
* `BUILD_ARTIFACTS` batch entry remains `contemplate_job`; no change to which task starts the pipeline.
* `anticipate_scan` runs the **Atlas** agent persona and produces guidance for downstream resume work: keywords and themes to emphasize, what to surface loudly, and what to de-emphasize or avoid — oriented to ATS parsing and a jaded recruiter’s first pass, using job-scoped context available at artifact time (including prior hop output from `contemplate_job` via standard chain tokens).
* Output passes to later hops through the existing daisy-chain contract (`{$CALLER_RESPONSE}`, cache blocks as Susan configures). No separate job-data persistence beyond the normal per-hop `agent_responses` trail.
* When the candidate opens a **ready** job in the **Recommended** Job Analysis Report modal, `anticipate_scan` output appears alongside other artifact agent responses — same visibility pattern as existing pipeline hops.
* Susan authors Atlas prompts, agent assignment, cache layout, and `run_next` edges in Manage Tasks, consistent with [AST-313](https://linear.app/astralcareermatch/issue/AST-313/artifact-pipeline-prompt-authoring) prompt-authoring practice.
* Admin prompt preview for `anticipate_scan` resolves job-scoped tokens the same way other artifact tasks do when a job entity is selected.

## Boundaries

* Does **not** change the **cover letter** chain or any task outside the resume artifact sequence.
* Does **not** hardcode chain order, hop counts, or step lists in product code — ordering stays `agent_task.run_next` only.
* Does **not** draft or mutate resume artifact content (`draft_job_resume`, `finalize_job_resume`, builder output) — guidance only.
* Does **not** replace or re-run the consult **GET** analysis (`grade_get`) — this is a separate artifact-time Atlas pass with chain context, not a consult-state transition.
* Does **not** author prompt prose in code — Susan owns Manage Tasks content.
* Does **not** write Atlas output to dedicated `job_data` fields (e.g. `critical_keywords`, artifact blobs) — chain-only consumption downstream; UI visibility comes from stored `agent_responses` only.
* Must not break existing Phase E task keys, `BUILD_ARTIFACTS` dispatch, or downstream tasks that already consume `{$CALLER_RESPONSE}` from `contemplate_job` once Susan rewires `run_next`.
* Task keys and allowed values remain config-driven per product code rules.

## Acceptance criteria

1. `anticipate_scan` appears as a configured task key in Manage Tasks and in the authoritative task-key registry.
2. App startup sync creates a current `agent_task` row for `anticipate_scan` (blank until Susan authors prompts).
3. With Susan’s `run_next` wiring (`contemplate_job` **→** `anticipate_scan` **→** `advise_job_resume`), a full resume artifact chain run executes all three hops in order for a single job.
4. `advise_job_resume` receives `anticipate_scan` output through `{$CALLER_RESPONSE}` (or equivalent chain token Susan wires), not stale output from `contemplate_job` alone.
5. `BUILD_ARTIFACTS` dispatch still enters at `contemplate_job` only.
6. Susan can assign the Atlas agent and save all prompt segments for `anticipate_scan` in Manage Tasks without code changes.
7. Manage Tasks preview for `anticipate_scan` with a selected job entity resolves job-scoped tokens (`{$VISIBLE_JD}`, `{$ANALYSIS_*}`, etc.) the same way `contemplate_job` preview does after [AST-513](https://linear.app/astralcareermatch/issue/AST-513/token-gap-correction) lands.
8. For a job in the **ready** state, opening it in the **Recommended** Job Analysis Report modal shows the `anticipate_scan` agent response in the same agent-response section pattern as other artifact pipeline hops.

## Dependencies and blockers

* [AST-450](https://linear.app/astralcareermatch/issue/AST-450/register-artifact-pipeline-task-keys-dumb-chain-registry) (Done) — Phase E dumb-chain registry pattern.
* [AST-303](https://linear.app/astralcareermatch/issue/AST-303/daisy-chain-task-execution-in-do-task), [AST-304](https://linear.app/astralcareermatch/issue/AST-304/add-parsable-chain-tokens-to-resolve-tokens), [AST-306](https://linear.app/astralcareermatch/issue/AST-306/add-run-next-field-to-manage-tasks) (Done) — chain execution and `run_next` plumbing.
* [AST-513](https://linear.app/astralcareermatch/issue/AST-513/token-gap-correction) (User Testing) — job-scoped prompt tokens Atlas prompts will reference.
* [AST-313](https://linear.app/astralcareermatch/issue/AST-313/artifact-pipeline-prompt-authoring) (In Progress) — Susan’s prompt authoring; supersedes [AST-451](https://linear.app/astralcareermatch/issue/AST-451/configure-contemplate-job) `run_next` target (`advise_job_resume`) once this hop exists.

## Open questions

none.

---

## Original brief

Between contemplate_job and advise_job_resume in the sequence, this will go to Atlas to provide a set of keywords and input about what should be emphasized to appease the likely initial resume scan criteria (ATS and jaded recruiter)

### Comments

#### chuckles — 2026-05-29T21:11:38.256Z
finish-up blocked — AST-516 is **User Testing**, not **PR Ready**.

Move parent (and child AST-520 if applicable) to **PR Ready** after UAT, then re-run finish-up.

Git note: local `dev` already contains the AST-516 prep-uat merge (`5c42a5c8`) plus follow-on fixes (`3fadba50`, `17b70d26`); `origin/ftr/AST-516-insert-task-anticipate_scan-in-the-daisy-chain` has no commits ahead of local `dev`.

— Chuckles

#### chuckles — 2026-05-28T23:23:02.187Z
## Manual test steps

1. Restart the app so `sync_agent_tasks` runs. Open **Manage Tasks** — confirm **`anticipate_scan`** appears in the task list (tenth Phase E key, between **`contemplate_job`** and **`advise_job_resume`** in sort order).
2. Select **`anticipate_scan`** — confirm you can assign the **Atlas** agent and save all prompt segments (blank row is fine for now).
3. Wire **`run_next`**: **`contemplate_job` → `anticipate_scan` → `advise_job_resume`** (supersedes AST-451 direct link).
4. Confirm **Scheduled Actions** / dispatch still enters resume pipeline at **`contemplate_job`** only (**BUILD_ARTIFACTS** unchanged).
5. Run **`contemplate_job`** chain for a job with consult data — confirm three hops execute in order and **`advise_job_resume`** receives Atlas output via **`{$CALLER_RESPONSE}`** (not Judith output alone).
6. Open a **ready** job in **Recommended → Job Analysis Report** — confirm an **Anticipate Scan** collapsible panel appears when that hop has stored **`agent_responses`** (Phase E filter; same pattern as other artifact hops).
7. **Manage Tasks preview** for **`anticipate_scan`** with a job entity selected — confirm **`{$VISIBLE_JD}`** and **`{$ANALYSIS_*}`** tokens resolve (requires **AST-513** on your test DB).

**Susan-owned after code:** Atlas prompt prose (**AST-313**); chain acceptance **#3–4**, **#6–7** need steps 3 + prompts.

`origin/ftr/AST-516-insert-task-anticipate_scan-in-the-daisy-chain` @ **936ad90c** · local **`dev`** merged (§8) @ **5c42a5c8**. Restart app if running.

Reset: `git reset --hard origin/dev`

— Chuckles

#### hedy — 2026-05-28T23:18:23.433Z
[check-linear]

**Inbox (parent AST-516 / Astral Artifacts):**

- **§0a:** `dev-hedy` @ `/Users/susan/chuckles/astral-hedy`; `git fetch` + `merge origin/dev` — **merge-clean** (`BEHIND=0`, `origin/dev` ancestor of `HEAD`).
- **§0b:** `@hedy` issue search (Team Astral + **Astral Artifacts** project), full threads on **AST-516**, child **AST-520**, sibling **AST-513**, and other @hedy hits (**AST-514**, roster **AST-505**–**508**, done **AST-294** / **AST-310**).
- **0** actionable comments — nothing `@hedy` or directed at Hedy needing reply or small fix after this scan.

**Parent / child status (context only, no pipeline from this pass):**

- **AST-516:** **In Progress**, assignee Chuckles — Chuckles git-ref table + answered `@susan` questions in description; no `@hedy`.
- **AST-520:** **Tests Passed**, assignee **Ada** — Betty QA manifest on `origin/sub/AST-516/AST-520-register-anticipate_scan-task-key` @ `d4911f11` (not Hedy work).

**Session scope:** Assigned issue ids **(none)** — happy path; no `plan-astral` / `build-astral` / `test-astral` / `resolve-astral`.

#### hedy — 2026-05-28T23:09:58.773Z
[check-linear]

**Inbox (parent AST-516 / Astral Artifacts):** `@hedy` issue search (team + project), fallback scan (`updatedAt -P14D` on Astral Artifacts), full threads on **AST-516**, child **AST-520**, sibling **AST-513**, and other @hedy hits (**AST-514**, **AST-294**, **AST-310**, roster **AST-505**–**508**). **0** actionable comments — nothing `@hedy` or directed at Hedy needing reply or small fix after Hedy’s prior `[check-linear]` posts.

**§0a:** `dev-hedy` @ `/Users/susan/chuckles/astral-hedy`; merged `origin/dev` — **merge-clean** (`BEHIND=0`, `origin/dev` ancestor of `HEAD`). (Prior pass reported merge conflicts; not reproduced this run.)

**Session scope:** Assigned issue ids **(none)** — no `plan-astral` / `build-astral` / `test-astral` / `resolve-astral` from this pass. **AST-520** is **Plan Approved**, assignee **Ada** (`origin/sub/AST-516/AST-520-register-anticipate_scan-task-key`).

#### katherine — 2026-05-28T23:09:50.295Z
[check-linear]

**Inbox (parent AST-516 / Astral Artifacts):**

- **§0a:** `dev-kath` @ `/Users/susan/chuckles/astral-kath`; merged `origin/dev` — **merge-clean** (`BEHIND=0`, `origin/dev` ancestor of `HEAD` @ `940e58e3`).
- **§0b:** `@katherine` issue search (team + **Astral Artifacts** project), fallback scan (`updatedAt -P14D`), full threads on **AST-516**, child **AST-520**, sibling **AST-513**, and prior mention candidates (**AST-514**, **AST-308**, **AST-481**).
- **0** actionable comments — nothing `@katherine` or directed at Katherine after Katherine's latest `[check-linear]` on **AST-513** (`2026-05-28T21:10`) and **AST-514** (`2026-05-28T22:01`).
- **AST-516:** Chuckles git ref table + pre-dispatch `@susan` questions; parent description now reflects Susan's answers (candidate-visible `anticipate_scan` in Job Analysis Report; chain-only output). No `@katherine`.
- **AST-520:** **Plan Approved**, assignee **Ada** — Ada plan doc comment only (`origin/sub/AST-516/AST-520-register-anticipate_scan-task-key` @ `fe6718eb`).

**Session scope:** Assigned issue ids **(none)** — no `plan-astral` / `build-astral` / `test-astral` / `resolve-astral` from this pass (happy path).

#### chuckles — 2026-05-28T23:05:34.897Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-516 (parent) | ftr/AST-516-insert-task-anticipate_scan-in-the-daisy-chain |
| AST-520 | sub/AST-516/AST-520-register-anticipate_scan-task-key |

— Chuckles

#### chuckles — 2026-05-28T22:50:59.726Z
@susan Two open questions before dispatch:

1. Should **`anticipate_scan`** output be **visible to the candidate** anywhere (e.g. Job Analysis Report panel), or remain **internal pipeline context** consumed only by downstream agent hops?
2. Should any part of Atlas’s output **persist on the job record** (e.g. to feed the resume builder’s ATS keyword strip), or stay **chain-only** via **`{$CALLER_RESPONSE}`** / cache blocks?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
