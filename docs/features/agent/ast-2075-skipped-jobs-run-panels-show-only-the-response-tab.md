# AST-2075 — Skipped job's run panels show only the RESPONSE tab

<!-- linear-archive: AST-2075 archived 2026-10-16 -->

## Linear archive (AST-2075)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2075/skipped-jobs-run-panels-show-only-the-response-tab  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-2028 — Technical fail modals must filter by entity_id  
**Blocked by / blocks / related:** parent: AST-2028

### Description

## Report (verbatim)

> \[fix\] I'm still only seeing the RESPONSE tab for the Skipped job's task history panels.

## As-is

On staging (after [PR #258](<https://github.com/susansomerset/astral/pull/258>) and the [AST-2052](https://linear.app/astralcareermatch/issue/AST-2052/job-run-modal-should-read-like-a-single-each-mode-call) Each-mode fix landed), opening a run from a **Skipped** job's State History shows only the RESPONSE tab — SYSTEM, CACHE, TASK and NO_CACHE are missing.

## To-be

A Skipped job's run panels read like a single Each-mode call, same as any other job after AST-2052: SYSTEM, non-empty CACHE, TASK, the job's NO_CACHE, and its RESPONSE.

If for some reason the agent_data cannot be found for the call (because it aged out), indicate as much in the various tabs that are missing the content.

## Suggested engineer

Hedy Lamarr ([AST-2030](https://linear.app/astralcareermatch/issue/AST-2030/slice-agent-data-reads-and-agent-story-by-entity-technical-fail-modals) / [AST-2052](https://linear.app/astralcareermatch/issue/AST-2052/job-run-modal-should-read-like-a-single-each-mode-call) — entity-sliced agent-data read path in `src/core/agent.py`).

### Comments

#### radia — 2026-10-10T05:47:59.605Z
[code-rubric] PROCEED (Commit: 2e80369af) entity placeholder tabs OK

#### chuckles — 2026-10-09T01:25:05.155Z
@susan — AST-2075 is fixed and green (Tests Passed, `38e9c5b50`), but held before review: Betty's tests publish (`merge-tests(AST-2075)`) also carried three in-flight **AST-2054** test commits from the shared tests branch (`d239600c9` AST-2069, `8598b335c` / `e6e47125b` AST-2070 — upshot / `GET_UPSHOT` asserts). That product isn't on `dev` yet ([PR #272](https://github.com/susansomerset/astral/pull/272) open), so on this branch `test_roster` / `test_config` / `test_consult` / `test_gazer` fail ~35 more tests than on `dev`. Merged into AST-2028's ftr, they'd ride to `dev` red.

Options:
1. **Hold** until PR #272 merges to `dev` — then those commits are already on `dev` and the branch is clean (default; move this back to Chuckles once it's merged).
2. **Proceed now** — Radia → User Testing → merge into AST-2028 ftr; just merge PR #272 before AST-2028's next PR.
3. **Rebuild** a clean AST-2075 branch without the foreign commits (fresh sub ref + Betty/Hedy re-publish).

Reply with 1/2/3 (or move to Chuckles to resume).

#### hedy — 2026-10-09T01:23:05.205Z
`origin/sub/AST-2028/AST-2075-skipped-job-run-panels` @ `38e9c5b50` · [bug-repro] RESPONSE-only entity run placeholder test red on f7ea56566, green on fix; manifest 59 passed / 1 skipped (filtered); tsc clean; scope gate empty.

#### betty — 2026-10-09T01:20:43.085Z
[bug-repro]
`origin/sub/AST-2028/AST-2075-skipped-job-run-panels` @ `f7ea56566` · repro lands red, awaits fix

#### joan — 2026-10-09T01:18:39.584Z
[board-joan]  CANON: OK

Frontend-only display change in `BatchAgentDataModal.tsx`; storage, join keys and backend logging untouched — no canon impact.

#### betty — 2026-10-09T01:18:24.656Z
[board-betty] TESTS: REVISE
What: docs/test-bible/frontend/components.md § AST-2031 — broken tests + missing coverage — entity-mode active tab now defaults to SYSTEM (placeholder when absent), so test_BatchAgentDataModal.test.tsx "BatchAgentDataPanes — AST-2031" cases "entityId → encoded entity_id on agent data only" and "changing entityId refetches the scoped agent data" (single NO_CACHE row, read via active-pane display value) break; no node covers the Repro (placeholder SYSTEM/CACHE/NO_CACHE/TASK tabs + missing-row text, CACHE only when SYSTEM also missing, batch-wide tabs/empty state unchanged).

#### hedy — 2026-10-09T01:17:42.621Z
`origin/sub/AST-2028/AST-2075-skipped-job-run-panels` @ `faf502439` · missing tabs say so

#### hedy — 2026-10-09T00:59:40.274Z
@susan — plan-fix paused: I need one look at staging data before I can name a root cause. Local `data/astral.db` has no jobs and only 7 test `agent_data` rows.

**What the code says:** both the run modal (`get_agent_data`) and the story (`list_entity_latest_agent_refs`) return every SYSTEM / CACHE / TASK row in the run's `batch_id`, whichever job is open. The AST-2052 blank-row skip only drops rows whose content is empty. So "RESPONSE only" means that run has **no prompt rows stored** under its `batch_id`.

`do_task` writes prompt rows before calling the provider. If that write fails, the error is swallowed (`Continuing without that agent_data row` in app_log) and the RESPONSE is still saved afterwards. Failed (Skipped) jobs would show exactly this.

**For one affected Skipped job, could you send (or let me pull from staging):**
1. The job's `astral_job_id` and the `run_id` on the State History row you opened.
2. `GET /api/agent_data/<run_id>` **without** `entity_id`. Which `block_type`s come back?
3. Any staging app_log lines containing `Continuing without that agent_data row` for that run's task around that time.

If (2) shows SYSTEM / TASK rows, the bug is in the read and I plan it in the AST-2030 doc. If it shows only RESPONSE, the bug is in storage and I plan it from whatever (3) says.

---

_Implementation detail may live in git history on `origin/dev`._
