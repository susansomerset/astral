# AST-871 — Candidate state machine

<!-- linear-archive: AST-871 archived 2026-08-05 -->

## Linear archive (AST-871)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-871/candidate-state-machine  
**Status at archive:** Archive  
**Project:** Astral Candidate  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-952; related: AST-953

### Description

## Purpose

Replace the coarse four-step candidate lifecycle (NEW → PROFILE_READY → CONTEXT_READY → LIVE_PROMPTS) with a fuller onboarding-to-search state machine that mirrors how jobs and companies already work: named stages, stale/retry/error companions where Susan called them out, and transition history. Operators and future Candidate Progress reporting need to know where each person is in intake, resume, artifacts, and active search — not just a single "live" flag.

## Functional scope

* **Lifecycle vocabulary (runtime).** Persist and enforce: NEW_CANDIDATE, INTAKE_INITIATED, REQUIRED_TOPICS_READY, ALL_TOPICS_READY, REQUESTED_RESUME, RESUME_READY, REQUESTED_ARTIFACTS, ARTIFACTS_READY, ACTIVE_SEARCH, PAUSE_SEARCH, INACTIVE, and DELETED — plus the stale / retry / error companions named for waiting and dispatch-triggering stages. **PROSPECT is conceptual only** (not a persisted runtime state).
* **INACTIVE and DELETED coexist.** INACTIVE = no longer enrolled. DELETED starts a config-driven reap timer that hard-deletes candidate data in production after the configured window.
* **Transition rules.** Only allowed hops succeed; illegal transitions fail closed. Happy path and side paths (stale aging, retry, error, pause, inactive, deleted→reap) are explicit in config, not scattered in call sites.
* **Topic-ready stages ship with manual transitions.** REQUIRED_TOPICS_READY / ALL_TOPICS_READY may be set manually (same posture as today) until Topic Menu ([AST-953](https://linear.app/astralcareermatch/issue/AST-953/topic-menu-generation)) wires satisfaction-driven transitions — deferred obligation recorded under Dependencies ([AST-953](https://linear.app/astralcareermatch/issue/AST-953/topic-menu-generation) is still Backlog; note lives here until that ticket is opened for define).
* **Waiting vs dispatch-triggering stages.** Some stages only wait and may go stale after config-driven hours; REQUESTED_RESUME and REQUESTED_ARTIFACTS are claimable by dispatch and resolve to ready, retry, or error. **ACTIVE_SEARCH is the sole gate** that replaces LIVE_PROMPTS for company/job search dispatch eligibility.
* **Transition history.** Every successful state change records history with prior state, new state, and timestamps for time-in-state (Candidate Progress [AST-869](https://linear.app/astralcareermatch/issue/AST-869/candidate-progress) consumes later).
* **Legacy migration.** LIVE_PROMPTS → ACTIVE_SEARCH. Existing DELETED rows are hard-deleted now (not remapped). Legacy NEW, PROFILE_READY, CONTEXT_READY, and any other non-LIVE_PROMPTS / non-DELETED state → NEW_CANDIDATE.
* **Dispatch and task-config foreign-key / state-key migration.** Migrate dispatch-table foreign keys and task-config entries that still point at retired candidate state names (or otherwise break under the new vocabulary) so scheduled/dispatch work stays coherent after the cutover — including rows that keyed off LIVE_PROMPTS or other legacy candidate states.
* **State consumers stay coherent.** Nav visibility, completeness gates, and other state-gated surfaces work against the new vocabulary — remapped or updated so retired names are gone. Daisy-chained resume→artifacts generation is **out of scope** (no separate epic; existing chain machinery may apply later outside this definition).

## Boundaries

* Does **not** treat PROSPECT as a runtime candidate state.
* Does **not** build Topic Menu generation ([AST-953](https://linear.app/astralcareermatch/issue/AST-953/topic-menu-generation)) or Candidate Profile Fields redesign ([AST-952](https://linear.app/astralcareermatch/issue/AST-952/candidate-profile-fields)) — only the state names and transitions those features will eventually drive.
* Does **not** build the Candidate Progress admin report UI ([AST-869](https://linear.app/astralcareermatch/issue/AST-869/candidate-progress)) — only the machine and history that report will read.
* Does **not** implement resume/artifact craft prompts, review UIs, or daisy-chained generation pipelines beyond wiring which states dispatch claims and how success / failure / stale resolve.
* Does **not** change company or job state machines.
* Does **not** break Manage Candidates dispatch-task provisioning already shipped ([AST-873](https://linear.app/astralcareermatch/issue/AST-873/add-set-dispatch-tasks-button)).
* Code Rules: state lists, transitions, stale hours, and DELETED reap window live in config as the single source of truth (§2.1 / §2.6); no parallel hardcoded candidate state sets.

## Acceptance criteria

 1. Product config exposes the runtime candidate state vocabulary (no PROSPECT) and allowed transitions; disallowed hops are rejected.
 2. INACTIVE and DELETED both exist; entering DELETED starts the configured reap timer toward hard delete of candidate data in production.
 3. A candidate can move through the documented happy path from NEW_CANDIDATE through intake topic-ready stages (manual transitions acceptable), resume request/ready, artifacts request/ready, to ACTIVE_SEARCH, and into PAUSE_SEARCH / INACTIVE / DELETED as defined.
 4. Waiting stages Susan marked for stale age into their stale companion after the configured hours.
 5. REQUESTED_RESUME and REQUESTED_ARTIFACTS are claimable by dispatch and can move to ready, retry, or error companions as appropriate.
 6. ACTIVE_SEARCH is the only candidate state that qualifies a candidate for company/job search dispatch (replacing LIVE_PROMPTS).
 7. Every successful state change appends candidate transition history usable for prior/new state and time-in-state (feeds [AST-869](https://linear.app/astralcareermatch/issue/AST-869/candidate-progress) State Progress later).
 8. Migration: LIVE_PROMPTS → ACTIVE_SEARCH; existing DELETED rows hard-deleted; all other legacy states → NEW_CANDIDATE; no silent data loss for remapped live rows.
 9. Dispatch-table foreign keys and task-config entries that referenced retired candidate states are remapped (or rewritten) so they resolve correctly under the new vocabulary — no orphaned LIVE_PROMPTS (or other legacy) dispatch/task-config keys left behind.
10. Nav and other state-gated candidate UI still resolve correctly for candidates on the new states.

## Dependencies and blockers

* Related (consumer, not a start blocker): [AST-869](https://linear.app/astralcareermatch/issue/AST-869/candidate-progress) Candidate Progress — needs this machine + history for State Progress.
* Deferred (do not block Todo): [AST-953](https://linear.app/astralcareermatch/issue/AST-953/topic-menu-generation) Topic Menu Generation — when defined/built, wire REQUIRED_TOPICS_READY / ALL_TOPICS_READY transitions from topic satisfaction (this epic ships manual transitions only). *Note kept here because* [AST-953](https://linear.app/astralcareermatch/issue/AST-953/topic-menu-generation) *is still Backlog; Chuckles does not edit Backlog tickets.*
* Soft adjacency: [AST-952](https://linear.app/astralcareermatch/issue/AST-952/candidate-profile-fields) Candidate Profile Fields — intake content, not required for the machine itself.
* Soft adjacency: [AST-873](https://linear.app/astralcareermatch/issue/AST-873/add-set-dispatch-tasks-button) Done — dispatch-task set tooling must keep working under new states.
* none blocking start.

## Open questions

none.

## Proposed child tickets

| # | Working title | What it delivers | Agent | Sequencing |
| -- | -- | -- | -- | -- |
| 1 | Candidate state registry and transitions | Config-backed runtime vocabulary (no PROSPECT), allowed transitions, stale/retry/error companions, INACTIVE + DELETED (DELETED starts reap timer), enforced transition behavior replacing the old four-step machine. Manual topic-ready transitions allowed. Does **not** own history storage (#2), dispatch claim wiring (#3), or legacy row / FK migration (#4). | Ada | — |
| 2 | Candidate transition history | Persist enter/exit history on each candidate transition with parity to job/company history for time-in-state. Does **not** own state vocabulary (#1) or the Progress UI ([AST-869](https://linear.app/astralcareermatch/issue/AST-869/candidate-progress)). | Hedy | after #1 |
| 3 | Dispatch and stale eligibility for candidate stages | Wire REQUESTED_RESUME / REQUESTED_ARTIFACTS (and stale aging) so dispatch can claim and resolve to ready/retry/error; ACTIVE_SEARCH as the sole company/job search-ready gate. Does **not** own craft prompts, daisy-chain generation, Topic Menu, or bulk FK remaps (#4). | Katherine | after #1 |
| 4 | Legacy candidate migration, consumers, and dispatch/task-config keys | Migrate LIVE_PROMPTS → ACTIVE_SEARCH; hard-delete existing DELETED rows; map remaining legacy states → NEW_CANDIDATE; remap dispatch-table foreign keys and task-config entries off retired candidate states; update nav/gates and other consumers so retired names are gone. Does **not** invent new product flows. | Ada | after #1 |

**Monolith check:** Functional scope has 9 capabilities; 4 proposed children (not a single mega-ticket).

**New patterns:** (1) Candidate state registry with enforced prior/allowed transitions aligned to the job-style machine — introduced by child #1 (includes DELETED reap timer). (2) Candidate transition history — introduced by child #2; reusable by [AST-869](https://linear.app/astralcareermatch/issue/AST-869/candidate-progress) and any future candidate batch anchoring.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| [AST-871](https://linear.app/astralcareermatch/issue/AST-871/candidate-state-machine) (parent) | ftr/AST-871-candidate-state-machine |
| [AST-970](https://linear.app/astralcareermatch/issue/AST-970/candidate-state-registry-and-transitions-candidate-state-machine) | sub/AST-871/AST-970-candidate-state-registry |
| [AST-971](https://linear.app/astralcareermatch/issue/AST-971/candidate-transition-history-candidate-state-machine) | sub/AST-871/AST-971-candidate-transition-history |
| [AST-972](https://linear.app/astralcareermatch/issue/AST-972/dispatch-and-stale-eligibility-for-candidate-stages-candidate-state) | sub/AST-871/AST-972-dispatch-stale-eligibility |
| [AST-973](https://linear.app/astralcareermatch/issue/AST-973/legacy-candidate-migration-consumers-and-dispatchtask-config-keys) | sub/AST-871/AST-973-legacy-candidate-migration |

**Epic worktree:** `astral-AST-871/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | c05fff57-115d-46a4-9cbc-e30190df6f7b |
| Hedy | engineer | 5023f010-7335-406b-a093-a24ed26e1c20 |
| Katherine | engineer | 35cd1aa1-1d7c-405a-9eee-41b0e0780417 |
| Betty | qa | 6fdc6c78-4dd8-461c-96f8-77e5ed68ff9b |
| Radia | review | c633fe23-eea5-47fb-a2b7-2669fc37c260 |

---

## Original brief

PROSPECT (unknown user, no data). This may not ever be a runtime state, but we may want to capture data about prospect users over time.

NEW_CANDIDATE (user created in stytch)

INTAKE_INITIATED (intake conversation thread begun, requires resume, cover letter and linkedin profile to get started, plus hopes, concerns and interests, and urgency/state of job search)

REQUIRED_TOPICS_READY (→ *_STALE after config-driven hours)

This state is internally set when all required topics are considered satisfied, but it does not trigger a dispatch event.

ALL_TOPICS_READY (→ *_STALE after config-driven hours)

when all topics have been satisfied and there's nothing left for the candidate to do but request the resume.  The distinction between this state and the previous state is that the previous state suggests that there is more to talk about, so the candidate may wish to continue discussions before requesting a resume draft.

(Resume & linkedin content & topics reviewed to generate Strengths, priorities, dealbreakers, backstory) - Review with Candidate to validate context sections before base resume draft, candidate manually clicks "generate new resume"

REQUESTED_RESUME - dispatch - ( → *_RETRY | *_ERROR)

RESUME_READY (→ *_STALE after config-driven hours)

(base resume with Sections defined and reviewed, Experience, skills, competencies, education, Highlights, Summary), where the candidate can review and refine the content of the resume and clarify anything in the context before requesting the artifacts.

REQUESTED_ARTIFACTS - dispatch - ( → *_RETRY | *_ERROR)

the job title patterns, search terms and rubrics.

Job Title patterns (What shape is the candidate looking for?)

Search terms drafted (What does the right company look like on the internet? Candidate experience, interests, specializations)

Rubrics drafted (Listing, Description, DO, GET, LIKE)

ARTIFACTS_READY (→ *_STALE after config-driven hours)

ACTIVE_SEARCH <THIS IS WHEN THE CANDIDATE IS READY FOR DISPATCH> (no next state)

PAUSE_SEARCH - Nothing is wrong with the candidate account, it's ready for active search, but it has been paused. (no next state)

INACTIVE - Candidate is no longer enrolled. (no next state)

Now, the difference between candidate states and company/job states is that for some of them, all they can do is go stale, but others trigger a dispatch task to process candidates in that state.  We may daisy-chain the generation of candidate artifacts similar to how we daisy-chain the job artifacts.

Candidates will need state transition history as job and company have.

### Comments

#### chuckles — 2026-07-28T01:09:33.245Z
[check-linear] blocked: refresh-ftr — docs/test-bible/README.md on ftr/AST-871-candidate-state-machine (@Betty White)

#### betty — 2026-07-24T01:15:33.625Z
[refresh-ftr] blocked: merge origin/dev into origin/ftr/AST-871-candidate-state-machine — CONFLICT files:
- docs/test-bible/README.md (@Betty White)

Resolve on ftr tip, push origin/ftr/AST-871-candidate-state-machine, then Chuckles will re-run refresh-ftr.

— Chuckles

#### chuckles — 2026-07-24T01:07:20.670Z
[datt-trace] **end** spawn=`84660100` — **DONE** **Hedy** role=engineer `resolve-child` on `AST-971`
- parent: `AST-871`
- exit: `0` · elapsed: `196s`

— Chuckles

#### chuckles — 2026-07-24T01:06:09.101Z
[datt-trace] **end** spawn=`a6c2b271` — **DONE** **Katherine** role=engineer `resolve-child` on `AST-972`
- parent: `AST-871`
- exit: `0` · elapsed: `123s`

— Chuckles

#### chuckles — 2026-07-24T01:05:15.344Z
[datt-trace] **end** spawn=`3030e727` — **DONE** **Ada** role=engineer `resolve-child` on `AST-973`
- parent: `AST-871`
- exit: `0` · elapsed: `69s`

— Chuckles

#### chuckles — 2026-07-24T01:04:05.919Z
[datt-trace] **start** spawn=`3030e727` — **IN FLIGHT** spawning **Ada** role=engineer `resolve-child` on `AST-973`
- parent: `AST-871`
- AGENT_SESSION: `c05fff57-115d-46a4-9cbc-e30190df6f7b`

— Chuckles

#### chuckles — 2026-07-24T01:04:04.771Z
[datt-trace] **start** spawn=`a6c2b271` — **IN FLIGHT** spawning **Katherine** role=engineer `resolve-child` on `AST-972`
- parent: `AST-871`
- AGENT_SESSION: `35cd1aa1-1d7c-405a-9eee-41b0e0780417`

— Chuckles

#### chuckles — 2026-07-24T01:04:03.957Z
[datt-trace] **start** spawn=`84660100` — **IN FLIGHT** spawning **Hedy** role=engineer `resolve-child` on `AST-971`
- parent: `AST-871`
- AGENT_SESSION: `5023f010-7335-406b-a093-a24ed26e1c20`

— Chuckles

#### chuckles — 2026-07-24T01:03:21.496Z
[datt-trace] **end** spawn=`7d6a18e7` — **DONE** **Hedy** role=engineer `resolve-child` on `AST-971`
- parent: `AST-871`
- exit: `0` · elapsed: `212s`

— Chuckles

#### chuckles — 2026-07-24T01:03:10.279Z
[datt-trace] **end** spawn=`85bdf56a` — **DONE** **Ada** role=engineer `resolve-child` on `AST-973`
- parent: `AST-871`
- exit: `0` · elapsed: `50s`

— Chuckles

#### chuckles — 2026-07-24T01:02:19.665Z
[datt-trace] **start** spawn=`85bdf56a` — **IN FLIGHT** spawning **Ada** role=engineer `resolve-child` on `AST-973`
- parent: `AST-871`
- AGENT_SESSION: `c05fff57-115d-46a4-9cbc-e30190df6f7b`

— Chuckles

#### chuckles — 2026-07-24T01:02:17.311Z
[datt-trace] **end** spawn=`0236e355` — **DONE** **Ada** role=engineer `resolve-child` on `AST-970`
- parent: `AST-871`
- exit: `0` · elapsed: `147s`

— Chuckles

#### chuckles — 2026-07-24T01:01:55.255Z
[datt-trace] **end** spawn=`5bfd13c2` — **DONE** **Katherine** role=engineer `resolve-child` on `AST-972`
- parent: `AST-871`
- exit: `0` · elapsed: `125s`

— Chuckles

#### chuckles — 2026-07-24T00:59:49.645Z
[datt-trace] **start** spawn=`0236e355` — **IN FLIGHT** spawning **Ada** role=engineer `resolve-child` on `AST-970`
- parent: `AST-871`
- AGENT_SESSION: `c05fff57-115d-46a4-9cbc-e30190df6f7b`

— Chuckles

#### chuckles — 2026-07-24T00:59:49.084Z
[datt-trace] **start** spawn=`5bfd13c2` — **IN FLIGHT** spawning **Katherine** role=engineer `resolve-child` on `AST-972`
- parent: `AST-871`
- AGENT_SESSION: `35cd1aa1-1d7c-405a-9eee-41b0e0780417`

— Chuckles

#### chuckles — 2026-07-24T00:59:48.315Z
[datt-trace] **start** spawn=`7d6a18e7` — **IN FLIGHT** spawning **Hedy** role=engineer `resolve-child` on `AST-971`
- parent: `AST-871`
- AGENT_SESSION: `5023f010-7335-406b-a093-a24ed26e1c20`

— Chuckles

#### chuckles — 2026-07-24T00:22:58.896Z
[datt-trace] **end** spawn=`611bd09f` — **DONE** **Radia** role=review `review-child` on `AST-971`
- parent: `AST-871`
- exit: `0` · elapsed: `145s`
- Active: clear each child after wait

— Chuckles

#### chuckles — 2026-07-24T00:22:01.958Z
[datt-trace] **end** spawn=`3f4aec94` — **DONE** **Ada** role=engineer `resolve-child` on `AST-970`
- parent: `AST-871`
- exit: `0` · elapsed: `89s`
- Active: clear each child after wait

— Chuckles

#### chuckles — 2026-07-24T00:20:32.706Z
[datt-trace] **start** spawn=`611bd09f` — **IN FLIGHT** spawning **Radia** role=review `review-child` on `AST-971`
- parent: `AST-871`
- AGENT_SESSION: `c633fe23-eea5-47fb-a2b7-2669fc37c260`
- status: agent process starting now (waiting on subprocess)
- Active: set `Radia` on each child, then `agent` + `wait`

— Chuckles

#### chuckles — 2026-07-24T00:20:32.236Z
[datt-trace] **start** spawn=`3f4aec94` — **IN FLIGHT** spawning **Ada** role=engineer `resolve-child` on `AST-970`
- parent: `AST-871`
- AGENT_SESSION: `c05fff57-115d-46a4-9cbc-e30190df6f7b`
- status: agent process starting now (waiting on subprocess)
- Active: set `Ada` on each child, then `agent` + `wait`

— Chuckles

#### chuckles — 2026-07-24T00:20:30.265Z
[datt-trace] **end** spawn=`2531e3cf` — **DONE** **Radia** role=review `review-child` on `AST-970`
- parent: `AST-871`
- exit: `0` · elapsed: `146s`
- Active: clear each child after wait

— Chuckles

#### chuckles — 2026-07-24T00:17:40.387Z
[datt-trace] **end** spawn=`39e97af0` — **DONE** **Hedy** role=engineer `check-linear` on `AST-970, AST-971, AST-972, AST-973`
- parent: `AST-871`
- exit: `0` · elapsed: `120s`
- Active: clear each child after wait

— Chuckles

#### chuckles — 2026-07-24T00:16:18.739Z
[datt-trace] **end** spawn=`1898c9af` — **DONE** **Ada** role=engineer `check-linear` on `AST-970, AST-971, AST-972, AST-973`
- parent: `AST-871`
- exit: `0` · elapsed: `41s`
- Active: clear each child after wait

— Chuckles

#### chuckles — 2026-07-24T00:15:34.184Z
[datt-trace] **end** spawn=`5dabe267` — **DONE** **Betty** role=qa `check-linear` on `AST-970, AST-971, AST-972, AST-973`
- parent: `AST-871`
- exit: `0` · elapsed: `129s`
- Active: clear each child after wait

— Chuckles

#### chuckles — 2026-07-24T00:13:24.180Z
[datt-trace] **start** spawn=`5dabe267` — **IN FLIGHT** spawning **Betty** role=qa `check-linear` on `AST-970, AST-971, AST-972, AST-973`
- parent: `AST-871`
- AGENT_SESSION: `6fdc6c78-4dd8-461c-96f8-77e5ed68ff9b`
- status: agent process starting now (waiting on subprocess)
- Active: set `Betty` on each child, then `agent` + `wait`

— Chuckles

#### chuckles — 2026-07-24T00:12:41.682Z
[datt-trace] **end** spawn=`8a41806b` — **DONE** **Ada** role=engineer `test-child` on `AST-973`
- parent: `AST-871`
- exit: `0` · elapsed: `101s`
- Active: clear each child after wait

— Chuckles

#### chuckles — 2026-07-24T00:03:28.614Z
[datt-trace] **end** — **Ada** role=engineer `test-child` on `AST-970`
- parent: `AST-871`
- exit: `0` · elapsed: `243s`
- Active: clear each child after wait

— Chuckles

#### chuckles — 2026-07-24T00:02:27.767Z
[datt-trace] **end** — **Hedy** role=engineer `test-child` on `AST-971`
- parent: `AST-871`
- exit: `0` · elapsed: `181s`
- Active: clear each child after wait

— Chuckles

#### chuckles — 2026-07-24T00:01:55.487Z
[datt-trace] **end** — **Katherine** role=engineer `test-child` on `AST-972`
- parent: `AST-871`
- exit: `0` · elapsed: `146s`
- Active: clear each child after wait

— Chuckles

#### chuckles — 2026-07-24T00:00:31.408Z
[datt-trace] **end** — **Betty** role=qa `qa-child` on `AST-973`
- parent: `AST-871`
- exit: `0` · elapsed: `321s`
- Active: clear each child after wait

— Chuckles

#### chuckles — 2026-07-23T23:55:09.043Z
[datt-trace] **end** — **Betty** role=qa `qa-child` on `AST-972`
- parent: `AST-871`
- exit: `0` · elapsed: `516s`
- Active: clear each child after wait

— Chuckles

#### chuckles — 2026-07-23T23:46:35.051Z
[datt-trace] **start** — spawning **Betty** role=qa `qa-child` on `AST-972`
- parent: `AST-871`
- AGENT_SESSION: `6fdc6c78-4dd8-461c-96f8-77e5ed68ff9b`
- Active: set `Betty` on each child, then `agent` + `wait`

— Chuckles

#### chuckles — 2026-07-23T23:46:31.707Z
[datt-trace] **end** — **Betty** role=qa `qa-child` on `AST-971`
- parent: `AST-871`
- exit: `0` · elapsed: `223s`
- Active: clear each child after wait

— Chuckles

#### chuckles — 2026-07-23T22:50:27.273Z
[check-linear] Discussion — dispatch/task-config FK migration added to definition (@susan)

#### susan — 2026-07-23T22:48:07.630Z
@chuckles Let's add the migration of foreign keys on the dispatch table and the task_config.

#### chuckles — 2026-07-23T22:32:02.648Z
@susan

1. Is **PROSPECT** a real persisted runtime state, or conceptual only (capture data about unknown users with no candidate row)?
2. How should existing **NEW / PROFILE_READY / CONTEXT_READY / LIVE_PROMPTS / DELETED** candidates map onto the new vocabulary?
3. Can **REQUIRED_TOPICS_READY / ALL_TOPICS_READY** ship with stub or manual transitions until **AST-953** Topic Menu lands, or must topic satisfaction be live before this goes Todo?
4. Is daisy-chained resume → artifacts generation in this epic, or only the states and dispatch hooks (generation epics later)?
5. Does **INACTIVE** replace **DELETED**, or do both coexist?
6. Is **ACTIVE_SEARCH** the sole gate that replaces **LIVE_PROMPTS** for company/job search dispatch eligibility?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
