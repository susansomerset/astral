# AST-2028 — Technical fail modals must filter by entity_id

<!-- linear-archive: AST-2028 archived 2026-10-16 -->

## Linear archive (AST-2028)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2028/technical-fail-modals-must-filter-by-entity-id  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 8  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

When an admin looks at a job's agent data — the run modal opened from a State History row, or a hop's agent-story tab — the NO_CACHE live content lists every job in the batch and the RESPONSE shows every job's answer (or the whole raw provider text when the call failed). Batch live content labels jobs by position (`000:`), never by id, so the stored blocks can't even be matched back to a job. Diagnosing why *this* job failed means hunting through an array of strangers. Agent data should be stored with real entity ids and shown sliced to the job being looked at, whatever state that job is in.

## Functional scope

1. **Stored with real ids.** Every do_task call that carries batch entities (batch of one included) stores its NO_CACHE and RESPONSE blocks with each positional label replaced by that entity's real id. What goes over the wire to the agent is unchanged — ids stay out of the prompt, positions stay in.
2. **Splittable blocks.** A stored NO_CACHE or RESPONSE block can be split into per-entity segments keyed by entity id, and the segment for one id picked out.
3. **Run modal is job-scoped.** A run opened from a job's State History (Processing and Skipped pages, any job state) shows only that job's NO_CACHE, TASK, and RESPONSE slice, and nothing from chunks that didn't carry the job. SYSTEM and CACHE_A–D are shared prompt and show as today.
4. **Agent story is job-scoped.** Hop tabs built from the agent story (Job Detail modal; the Job Analysis report's discussion pane on Recommended / Meteorites / job deeplink) show the job's NO_CACHE and RESPONSE slice for every task, not only scored ones.
5. **Failed calls too.** A failed call's raw RESPONSE in positional `NNN|` form is stored with ids and sliced the same way.
6. **Legacy fallback.** Blocks stored before this ships (positions, no ids) show in full as today — never an empty pane.
7. **Batch-wide views unchanged.** Execution History, Vector Feedback, and the Ad Hoc workbench keep showing the full batch; the Tokens & Cost line stays batch-wide. Company batches (prefilter) ride the same storage path and get ids stored; no company UI change.

## Component scope

* `src/utils/formatting.py` — **modified**. Home of `enumerate_array` and the encoded-payload helpers: gains the position→id hydrate and the id-keyed split used on both sides.
* `src/core/agent.py` — **modified**. Storage of NO_CACHE / RESPONSE hydrates positions to ids from the call's batch entities; the agent-data read (`entity_id`) and agent-story builder slice NO_CACHE / RESPONSE / TASK by id.
* `src/ui/frontend/src/components/BatchAgentDataModal.tsx` — **modified**. `BatchAgentDataPanes` takes an optional entity id and sends it as `entity_id` on the agent-data fetch.
* `src/ui/frontend/src/components/BatchExecutionModal.tsx` — **modified**. Optional entity id, forwarded to the panes.
* `src/ui/frontend/src/components/JobDetailModal.tsx` — **modified**. Passes the open job's `astral_job_id` to `BatchExecutionModal`.
* `tests/component/utils/test_formatting.py`, `docs/test-bible/utils/formatting.md` — **modified** (Betty). Hydrate + split cases.
* `tests/component/core/test_agent.py`, `docs/test-bible/core/agent.md` — **modified** (Betty). Stored-with-ids, run read, story slice, legacy fallback.
* `tests/component/frontend/components/test_BatchAgentDataModal.test.tsx`, `tests/component/frontend/components/test_JobDetailModal.test.tsx`, `docs/test-bible/frontend/pages.md` — **modified** (Betty). `entity_id` wiring.

Not in scope: `src/ui/api/api_system.py` (`GET /api/agent_data/<batch_id>` already takes `entity_id`), `src/data/database.py` (no schema change), `JobAnalysisReportModal.tsx` / `JobDiscussionPane.tsx` / `AgentStoryTab.tsx` (they render what the story builder returns), the batch `assemble` functions in `consult.py` / `roster.py` (wire prompt unchanged).

## Technical scope

* `src/utils/formatting.py` **— new function (hydrate):** given stored block text and the call's ordered entity ids, replace each positional label (`NNN:` line prefix, `[index=NNN]:` from `enumerate_array`, `NNN|` encoded response lines) with the entity id at that position; text with no positional labels is returned unchanged.
* `src/utils/formatting.py` **— new function (split):** given hydrated block text, return its per-entity segments keyed by entity id (and the JSON `jobs[]` / `companies[]` shape keyed by `astral_job_id` / `company_id`); the caller picks one id.
* `src/core/agent.py` **— modified function (prompt-block storage):** when ctx carries `batch_entities`, the stored NO_CACHE content is hydrated with their ids in order before save; wire blocks are built from the unhydrated text.
* `src/core/agent.py` **— modified function (response storage):** same hydrate on the RESPONSE row, success and failure paths alike.
* `src/core/agent.py` **— modified function (agent-data read with** `entity_id`**):** NO_CACHE / TASK / RESPONSE rows are cut to the entity's segment via the split; a row whose split yields segments but none for this id is dropped (another chunk's call); a row with no id-keyed segments is returned whole (legacy / single-entity). Replaces the ad-hoc `_extract_entity_segment` scan for these types.
* `src/core/agent.py` **— modified function (agent-story builder):** NO_CACHE and RESPONSE blocks for every task are cut to the entity's segment via the same split; the scored-only `_filter_response_block` path folds into it.
* `BatchAgentDataModal.tsx` **— modified function:** `BatchAgentDataPanes` optional entity-id prop → `entity_id` query on `/api/agent_data/…` only (timesheets / ledger fetches unchanged).
* `BatchExecutionModal.tsx` **— modified function:** optional entity-id prop, forwarded.
* `JobDetailModal.tsx` **— modified function:** passes `job.astral_job_id` into `BatchExecutionModal`.

## Architectural definition

* **Patterns to reuse**
  * [`patt.entity.batch-processing`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.entity.batch-processing.md>) — `batch_id` stays the `agent_data` join key; ids inside the stored block refine it to one entity without a new key.
* **New patterns proposed:** none.
* **Applicable statutes**
  * [`stat.logging.debug`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md>) — new hydrate / split branches log at debug only.

## Acceptance criteria

 1. **Stored with ids, wire unchanged.** A do_task call with `batch_entities` `[A,B,C]` and live content `000: …\n001: …\n002: …`: the stored NO_CACHE row contains `A`, `B`, `C` as labels and no `000:` / `001:` / `002:` prefix, while the text handed to the provider still has `000:` and no `A`. Fail = stored row still positional, or an id reaches the wire.
 2. **Enumerate form hydrated.** Same with `[index=000]:` live content → stored row carries the ids in place of `index=NNN`. Fail = `index=000` remains.
 3. **Failed RESPONSE hydrated.** A failed call's raw response `000|…\n001|…` with entities `[A,B]` stores lines labeled `A` / `B`. Fail = `000|` remains.
 4. **Run read sliced.** `GET /api/agent_data/<batch>?entity_id=B` over (1) returns a NO_CACHE row with B's segment only. Fail = A's or C's text present.
 5. **Other chunks dropped.** Same batch, second chunk call for `[D,E]`: the `entity_id=B` response returns no NO_CACHE / RESPONSE row from that call. Fail = any row from it.
 6. **Story sliced for unscored tasks.** `get_entity_agent_story` for job B, on an unscored batch task stored as in (1), returns a NO_CACHE block containing only B's segment. Fail = full batch text.
 7. **Legacy fallback.** A stored row still in `000:` form returns whole for `entity_id=B` and in B's story. Fail = empty or missing block.
 8. **Job modal sends the id.** `test_JobDetailModal.test.tsx`: admin clicks a State History row for job `J`, run `R` → fetch `/api/agent_data/R?entity_id=J`. Fail = no `entity_id`.
 9. **Batch-wide callers unchanged.** `grep -n "entity_id" src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx src/ui/frontend/src/pages/AdminVectorFeedback.tsx src/ui/frontend/src/pages/AdminAnthropicAdHoc.tsx` returns nothing, and `test_AdminPerformanceMonitor.test.tsx` passes with no assertion edits. Fail = either.
10. **No API / schema change.** `git diff origin/dev...<ftr> -- src/ui/api/ src/data/` is empty. Fail = any change.

## Open questions

none

## Proposed child tickets

#### 1!!: **Store agent data with real entity ids - Ada**

Positional labels in stored NO_CACHE and RESPONSE blocks become the call's real entity ids at save time, for every call carrying batch entities (batch of one included, failed responses included). The wire prompt is untouched. Owns the hydrate and split helpers #2 reads with. Does not change any read path (#2) or UI (#3).
**Citations:** `patt.entity.batch-processing`, `stat.logging.debug`.
**Scope:** `src/utils/formatting.py` — new function (hydrate): positional labels (`NNN:`, `[index=NNN]:`, `NNN|`) → entity ids in order; unlabeled text unchanged. New function (split): hydrated text → per-entity segments keyed by id (plus JSON `jobs[]` / `companies[]` by `astral_job_id` / `company_id`). `src/core/agent.py` — prompt-block storage hydrates stored NO_CACHE from `batch_entities`; response storage hydrates the RESPONSE row on success and failure paths; wire blocks built from unhydrated text.
Estimate: 3

#### 2!: **Slice agent-data reads and agent story by entity - Hedy**

After #1. The agent-data read with `entity_id` and the agent-story builder cut NO_CACHE / TASK / RESPONSE to one entity using #1's split, drop other chunks' rows, and fall back to the whole block for legacy rows. Story slicing covers every task, not only scored. Does not touch storage (#1) or UI (#3).
**Citations:** `patt.entity.batch-processing`, `stat.logging.debug`.
**Scope:** `src/core/agent.py` — agent-data read with `entity_id`: NO_CACHE / TASK / RESPONSE cut via the split; rows with segments but none for this id dropped; rows with no id-keyed segments returned whole; replaces the `_extract_entity_segment` scan for these types. Agent-story builder: NO_CACHE and RESPONSE for every task cut via the same split; scored-only `_filter_response_block` folds in.
Estimate: 3

#### 3: **Job run modal requests entity-scoped agent data - Katherine**

After #2. The job modal's run view passes the job id through to the agent-data panes, which request the entity-scoped data. Execution History, Vector Feedback, and Ad Hoc keep requesting the full batch.
**Citations:** none — frontend prop plumbing only; no in-force directive governs it.
**Scope:** `BatchAgentDataModal.tsx` — `BatchAgentDataPanes` optional entity-id prop → `entity_id` query on `/api/agent_data/…` only. `BatchExecutionModal.tsx` — optional entity-id prop, forwarded. `JobDetailModal.tsx` — passes `job.astral_job_id` into `BatchExecutionModal`.
Estimate: 2

**Monolith check:** Functional scope N=7, children M=3 — split by store / read / UI.
**Scope partition check:** every product file and Technical scope item appears in exactly one child (`agent.py` storage functions → #1, read + story functions → #2); test and bible rows are Betty's via qa-child.

---

## Original brief

when showing the agent data for a skipped job, filter the no_cache and the response by the entity ID, rather than showing an array of all for the batch.

### Comments

#### chuckles — 2026-10-08T23:40:18.790Z
Filed [AST-2075](https://linear.app/astralcareermatch/issue/AST-2075).

#### susan — 2026-10-08T23:39:09.068Z
\[fix\] I'm still only seeing the RESPONSE tab for the Skipped job's task history panels.

#### chuckles — 2026-10-08T19:15:15.066Z
Filed [AST-2052](https://linear.app/astralcareermatch/issue/AST-2052).

#### susan — 2026-10-08T19:13:29.593Z
\[bug\]

Please show the original system, cache and user prompts and the no_cache for the selected entity as well as the response (layout should look like a single "each-mode" call)

#### chuckles — 2026-10-08T04:43:57.191Z
@susan Betty restored the dropped test onto `origin/sub/AST-2028/AST-2031-job-run-modal-entity-scoped` (`299e6fc0b`), but `merge-child.sh` refuses the re-merge: `validate-sub-log.sh` only scopes sub commits not yet on ftr and wants `code()`/`docs()`/`resolve()(AST-2031)` again. Need your call: fast-forward ftr to that sub tip by hand (skips only the label check), or fix the validator first. prep-uat is held until then — ftr as-is would delete the test from dev.

#### chuckles — 2026-10-08T04:43:05.345Z
[prep-uat] blocked: `ftr/AST-2028-technical-fail-modals-filter-by-entity-id` would delete `tests/component/core/test_consult.py::TestAst1155IncompleteGradeRetry::test_render_verdict_bad_confidence_first_strike_to_retry` from dev — added on dev by #253, dropped by `resync(tests): merge origin/dev (non-test paths only)` (84095c453), so `origin/tests` never got it.

@Betty White — restore that test from `origin/dev` onto the tests tree and publish to `origin/sub/AST-2028/AST-2031-job-run-modal-entity-scoped`; Chuckles re-runs merge-child + prep-uat.

#### chuckles — 2026-10-08T04:30:40.200Z
@Betty White — ftr test-tree regression (pre-prep-uat): `84095c453` `resync(tests): merge origin/dev (non-test paths only)` marked dev as merged but kept the tests-branch `tests/component/core/test_consult.py`, dropping dev's `test_render_verdict_bad_confidence_first_strike_to_retry` (33 lines, from `f8d3f9a12`). `origin/ftr/AST-2028-technical-fail-modals-filter-by-entity-id` → dev would delete it; please restore it on ftr.

#### chuckles — 2026-10-08T04:17:43.852Z
AST-2029 REVIEW — Radia wants `hydrate_entity_labels` to debug-log its full return per stat.logging.debug; Ada applying via resolve-child.

#### chuckles — 2026-10-08T03:42:03.838Z
@susan

1. **Depth of the NO_CACHE filter.** Batch live content deliberately omits `astral_job_id` (positions `000:` only), and nothing today records which job sat at which position or in which chunk. A per-job NO_CACHE slice needs a new persisted per-call roster. Approve that, or stop at what's filterable today (TASK / decoded RESPONSE only — NO_CACHE stays the full batch)?
2. **Where the roster lives.** Recommended: nullable column on `agent_data` (one schema add). Alternative: stamp the job's position + chunk on its own `state_history` entry next to `run_id` (no `agent_data` change, but only works for runs that wrote a transition). Which?
3. **Scope of "technical fail modals".** I read this as the run modal opened from any job's State History (skipped or not). Confirm — or should filtering only apply when the job is in a technical-fail / skipped state?

---

_Implementation detail may live in git history on `origin/dev`._
