# AST-1109 — Hard-coded daisy chain in config.py

<!-- linear-archive: AST-1109 archived 2026-08-07 -->

## Linear archive (AST-1109)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1109/hard-coded-daisy-chain-in-configpy  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Dispatch already treats `agent_task.run_next` as the documented carve-out for multi-hop job chains (CODE_RULES §2.6.0), yet `config.py` still carries hard-coded hop/entry lists that restate chain membership — `JOB_ARTIFACT_ENTRY_TASK_KEYS`, `BUILD_CONFIG.resume_artifact_chain.hop_task_keys` / `_RESUME_ARTIFACT_HOP_TASK_KEYS`, and candidate-stage `craft_task_keys`. Those shadows are config-as-loophole: they look statute-compliant (`no-hardcoded-sets` → put the set in config) while drifting from the real database topology and inventing carve-outs (cover letter left out of the frozenset with “no sensible reason”). This epic lands law first, then remediates each anomaly end-to-end against that law — `run_next` as authority (including cover-letter hops and craft succession), with boot confirm/correct where that anomaly’s topology must be written into `agent_task`.

## Functional scope

* **Statute first.** Archie-approved statute(s) + CODE_RULES pointer forbid config from shadowing database-owned dispatch/`run_next` topology (config-as-loophole ban). Downstream children treat those statute ids as binding.
* **Anomaly: job-artifact entry frozenset.** Retire `JOB_ARTIFACT_ENTRY_TASK_KEYS` and wrappers; membership from `run_next`; no cover-letter carve-out — `draft_cover_letter` is the same flow as other hops.
* **Anomaly: resume hop-key lists.** Retire `BUILD_CONFIG.resume_artifact_chain.hop_task_keys` / `_RESUME_ARTIFACT_HOP_TASK_KEYS` as chain-membership authority; succession from `run_next`.
* **Anomaly: craft_task_keys daisy-chain stand-in.** Retire `CANDIDATE_STAGE_DISPATCH` `craft_task_keys` lists as chain authority; succession from `run_next`; include that anomaly’s boot SQL confirm/correct (e.g. `craft_company_search_terms.run_next` → `craft_joblist_rubric`, onward along former list order through terminal empty).

## Architectural definition

* **Patterns to reuse**
  * `pattern.state.entity-state-transitions` — one registered-state transition per dispatch cycle; multi-hop only via the documented `run_next` carve-out.
  * `pattern.config.config-block` — still for true config-owned catalogs; this epic clarifies when that pattern must **not** duplicate DB topology.
* **New patterns proposed**
  * `pattern.dispatch.run-next-chain-authority` — job/candidate dispatch chain membership and hop succession come from current `agent_task.run_next` rows; config may name graduation maps / trigger registries but must not restate hop sets. **Needs Archie approval before implementation depends on the catalog id.**
* **Applicable statutes**
  * `astral.state.no-daisy-chain-in-run` — run_next is the only multi-hop carve-out; membership must match that carve-out’s data.
  * `astral.config.config-source-of-truth` — config owns behavior literals that are not DB topology; this epic narrows the boundary.
  * `astral.standards.no-hardcoded-sets` — must not be satisfied by a config list that shadows `run_next`.
  * `astral.standards.in-scope-only` / `astral.standards.dry-and-focused-functions` — delete dead shadow APIs; no drive-by refactors.
  * `astral.standards.database-header-inventory` — boot SQL stays within known tables (`agent_task`).
  * `orch.roles.archie-approves-statutes` — new statute text requires Archie approval.
  * **New statute proposed:** `astral.dispatch.run-next-is-chain-authority` (working id) — config must not define parallel allowed-key / hop-order lists for dispatch chain membership when `agent_task.run_next` already encodes the chain. **Needs Archie approval** (child 1).

## Boundaries

* Does **not** own seed-data ghost-row cleanup on **AST-1108** (Foundation; related for confusion context only). That work proceeds elsewhere.
* Does **not** redesign Manage Tasks UI, invent new hop-label formats, or change `dispatch_tasks` uniqueness / AUTO/CLICK / score_floor vs pass_threshold semantics beyond what each anomaly’s remediation requires for honest routing.
* Does **not** expand into unrelated config frozensets (grades, normalize gates, etc.) unless they literally restate `run_next` topology.
* Must not break existing §2.6.0 hop-label claim/graduation behavior that already reads `run_next` for parent matching — extend that authority, do not replace it with a new config list.
* Decomposition is **vertical per anomaly** after statutes — not horizontal layers (all deletes / then boot / then law).

## Acceptance criteria

1. New Archie-approved statute under `canon/statutes/` bans config shadow of DB-owned `run_next` topology; CODE_RULES points at it — lands before anomaly remediations claim conformance.
2. `JOB_ARTIFACT_ENTRY_TASK_KEYS` is gone; no remaining import or membership check against that name; cover-letter hops follow the same run_next-driven rules (no frozenset-exclusion carve-out).
3. `BUILD_CONFIG.resume_artifact_chain.hop_task_keys` / `_RESUME_ARTIFACT_HOP_TASK_KEYS` are not authorities for chain membership; resume/artifact hop succession comes from `run_next`.
4. Candidate-stage `craft_task_keys` lists are not authorities for craft daisy-chain succession; succession comes from `run_next`.
5. For the craft anomaly, at boot a one-time SQL series confirms/corrects expected `agent_task.run_next` links (including `craft_company_search_terms` → `craft_joblist_rubric`); observable after boot.
6. Each anomaly child’s product path does not consult that child’s retired hard-coded list for chain membership; §2.6.0 claim/match helpers that already use `run_next` remain the path for hop-label eligibility.

## Dependencies and blockers

* none. **AST-1108** is related (seed confusion) but not a blocker — seed refactor is out of scope here.

## Open questions

none

## Proposed child tickets

#### 1!: **Statute — run_next is chain authority - Katherine**

Land Archie-approved statute(s) + CODE_RULES pointer + catalog note for proposed `pattern.dispatch.run-next-chain-authority` / `astral.dispatch.run-next-is-chain-authority`. No product routing changes in this child. Blocks all anomaly remediations.

**Citations:** `orch.roles.archie-approves-statutes`; proposed `astral.dispatch.run-next-is-chain-authority`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `astral.state.no-daisy-chain-in-run`.

#### 2: **Anomaly — JOB_ARTIFACT_ENTRY_TASK_KEYS + cover-letter carve-out - Ada**

End-to-end against #1: delete frozenset/wrappers; wire membership to `run_next`; eradicate cover-letter special exclusion; keep §2.6.0 claim/graduation green for this surface. Does **not** own hop_task_keys or craft_task_keys remediations (siblings 3–4). Does **not** own AST-1108.

**Citations:** proposed `pattern.dispatch.run-next-chain-authority`; `astral.dispatch.run-next-is-chain-authority` (after #1); `astral.state.no-daisy-chain-in-run`; `astral.standards.no-hardcoded-sets`; `astral.standards.in-scope-only`.

#### 3: **Anomaly — resume hop_task_keys shadow - Hedy**

End-to-end against #1: retire `hop_task_keys` / `_RESUME_ARTIFACT_HOP_TASK_KEYS` as membership authority; succession from `run_next` on this surface. Does **not** own JOB_ARTIFACT_ENTRY or craft remediations.

**Citations:** proposed `pattern.dispatch.run-next-chain-authority`; `astral.dispatch.run-next-is-chain-authority` (after #1); `astral.standards.no-hardcoded-sets`; `astral.standards.in-scope-only`.

#### 4: **Anomaly — craft_task_keys shadow + boot run_next - Ada**

End-to-end against #1: retire `craft_task_keys`-as-chain authority; succession from `run_next`; one-time at-boot SQL confirm/correct for craft succession (and only this anomaly’s topology). Does **not** own job-artifact frozenset or resume hop-list remediations.

**Citations:** proposed `pattern.dispatch.run-next-chain-authority`; `astral.dispatch.run-next-is-chain-authority` (after #1); `astral.standards.database-header-inventory`; `astral.standards.no-hardcoded-sets`; `astral.standards.in-scope-only`.

**New patterns:** Child 1 proposes/lands the statute + pattern ids; children 2–4 implement against them. Prefer catalog ids once Archie approves.

**Monolith check:** Functional scope has 4 capabilities; 4 vertical children (statute then one anomaly each) — intentional, not a single mega-ticket.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-1109 (parent) | ftr/AST-1109-hard-coded-daisy-chain-in-configpy |
| AST-1110 | sub/AST-1109/AST-1110-statute-run-next-is-chain-authority |
| AST-1111 | sub/AST-1109/AST-1111-anomaly-job-artifact-entry-task-keys |
| AST-1112 | sub/AST-1109/AST-1112-anomaly-resume-hop-task-keys |
| AST-1113 | sub/AST-1109/AST-1113-anomaly-craft-task-keys-boot-run-next |

**Epic worktree:** `astral-AST-1109/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **Thread** column is the fully-qualified `store.db` path (UUID is the directory name — extract for `agent --resume`). **datt resume:** read this table — not chat memory. One UUID per agent; never the parent Chuckles Thread UUID.

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | `/home/susan/.cursor/chats/117f212c4fcaac22ac7085f5eb813d1b/f34e66d0-95c5-4186-b340-c22d29be0b81/store.db` |
| Hedy | engineer | `/home/susan/.cursor/chats/117f212c4fcaac22ac7085f5eb813d1b/64148792-ee8a-40a7-bc76-39f09c1876c5/store.db` |
| Katherine | engineer | `/home/susan/.cursor/chats/117f212c4fcaac22ac7085f5eb813d1b/a7e3dff5-71ee-497b-9943-14de068278ea/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/89442dba-5528-46e5-bb16-0c445b61f5b2/store.db` |
| Radia | review | `/home/susan/.cursor/chats/117f212c4fcaac22ac7085f5eb813d1b/66e94f9d-7cc5-4173-ad21-68135118514f/store.db` |

---

## Original brief

@

```/Users/susan/chuckles/astral-AST-1108/src/utils/config.py:932:945
# Dispatch consult hops that enter the job-artifact chain (AST-534 / AST-740).
# Excludes draft_cover_letter — cover-letter chain uses _run_craft_job_cover_letter_batch.
JOB_ARTIFACT_ENTRY_TASK_KEYS = frozenset({
    "anticipate_scan",
    "contemplate_job",
    "advise_job_resume",
    "draft_job_resume",
    "check_job_resume",
    "finalize_job_resume",
    "check_cover_letter",
    "finalize_cover_letter",
    "propose_application_responses",
})
```

This should not be in [config.py](<http://config.py>) at all, and I am glad to see it because it explains what I have been confused about.  Job artifact entry tasks should not be config-driven but database driven using the run_next key.  I will want to make sure this gets corrected, and statutes added to prevent similar "config-as-loophole" logic in future.

### Comments

#### chuckles — 2026-07-31T18:54:56.543Z
@susan — no concerns with statute-first then vertical per-anomaly children. Restructured Proposed child tickets that way (law → each shadow end-to-end). Boot SQL lives inside the craft anomaly child rather than a horizontal boot ticket.

— Chuckles

#### susan — 2026-07-31T18:52:44.549Z
The child tickets are going horizontally, not vertically.  Start with the statutes, then create child tickets to address each specific anomaly to those new statutes, end-to-end, please.  Please let me know if you have concerns with that approach.

#### chuckles — 2026-07-31T18:36:55.807Z
@susan

1. Cover-letter carve-out: keep separate craft batch for `draft_cover_letter`, or let run_next alone decide routing?
2. Sibling shadows: also retire `BUILD_CONFIG.resume_artifact_chain.hop_task_keys` / `_RESUME_ARTIFACT_HOP_TASK_KEYS` in this epic, or keep scope to `JOB_ARTIFACT_ENTRY_TASK_KEYS` only?
3. AST-1108: leave seed-data ghosts out of scope here (recommended), or link blockedBy/blocks?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
