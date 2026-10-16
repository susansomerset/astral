# AST-2052 — Job run modal should read like a single Each-mode call

<!-- linear-archive: AST-2052 archived 2026-10-16 -->

## Linear archive (AST-2052)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2052/job-run-modal-should-read-like-a-single-each-mode-call  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-2028 — Technical fail modals must filter by entity_id  
**Blocked by / blocks / related:** parent: AST-2028

### Description

## Report (verbatim)

> \[bug\]
>
> Please show the original system, cache and user prompts and the no_cache for the selected entity as well as the response (layout should look like a single "each-mode" call)

## As-is

A job's run modal (State History → run) for a batched (`batch_call_mode` Full) run does not read like one call: it shows the batch's agent data with only NO_CACHE / TASK / RESPONSE cut down to fragments, not the call's full system, cache and user prompts plus this entity's no_cache and response laid out as one coherent call.

## To-be

The run modal shows the run's original SYSTEM, CACHE A–D and user (TASK) prompts, the NO_CACHE for the selected entity only, and that entity's RESPONSE — laid out exactly as an Each-mode (one entity per call) run would show.

* Skip empty prompt content, so if Cache C was empty, drop it.

## Suggested engineer

Hedy Lamarr (sibling [AST-2030](https://linear.app/astralcareermatch/issue/AST-2030/slice-agent-data-reads-and-agent-story-by-entity-technical-fail-modals) — entity-sliced agent-data read); Katherine Johnson owns the modal wiring ([AST-2031](https://linear.app/astralcareermatch/issue/AST-2031/job-run-modal-requests-entity-scoped-agent-data-technical-fail-modals)) if the change is frontend-only.

### Comments

#### radia — 2026-10-08T19:48:43.829Z
[code-rubric] PROCEED (Commit: 3bf8bd513) Each-mode entity read OK

#### radia — 2026-10-08T19:47:50.704Z
[code-rubric] REVIEW (Commit: 2c7b93bf4) branch carries foreign diffs

#### hedy — 2026-10-08T19:46:17.548Z
`origin/sub/AST-2028/AST-2052-run-modal-each-mode-layout` @ `2c7b93bf4` · [bug-repro] `test_bug_repro_entity_read_is_one_each_mode_call` red on dc16b33c0, green on fix; manifest 22 passed; scope gate empty.

#### betty — 2026-10-08T19:36:56.463Z
[bug-repro]
`origin/sub/AST-2028/AST-2052-run-modal-each-mode-layout` @ `dc16b33c0` · repro lands red, awaits fix

#### joan — 2026-10-08T19:33:32.613Z
[board-joan]  CANON: OK

No canon impact — `batch_id` stays the join key (`patt.entity.batch-processing`); the new `_entity_call_view` read shape and debug line need no statute carve-out.

#### betty — 2026-10-08T19:33:10.729Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/agent.md § AST-2030 — missing coverage + broken test — no node exercises the Repro (tagged preamble kept, JSON jobs[]/companies[] envelope filtered to one item, blank CACHE/TASK rows omitted); blank-row skip breaks test_agent_ast2030.py::TestAst2030GetAgentDataSlice::test_ac4_ac5_ac7_entity_read (pins ("TASK", "") row).

#### hedy — 2026-10-08T19:32:12.856Z
`origin/sub/AST-2028/AST-2052-run-modal-each-mode-layout` @ `a1bc56eb6` · Each-mode view, blanks dropped

---

_Implementation detail may live in git history on `origin/dev`._
