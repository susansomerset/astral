# UAT: craft_get_rubric run_next does not continue to craft_do_rubric

**Linear:** [AST-1264](https://linear.app/astralcareermatch/issue/AST-1264/uat-craft-get-rubric-run-next-does-not-continue-to-craft-do-rubric)  
**Parent:** [AST-1243](https://linear.app/astralcareermatch/issue/AST-1243/candidate-artifacts-now-daisy-chain) — Candidate Artifacts now daisy chain  
**Publish ref:** `sub/AST-1243/AST-1264-uat-craft-get-run-next`

UAT on candidate `somerset` in `REQUESTED_ARTIFACTS` completed `craft_get_rubric` (persist recorded) but never entered `craft_do_rubric`. Restore live `agent_task.run_next` succession for the candidate artifacts dispatch path so the chain continues hop-by-hop after the opening hop.

## UAT fitness

- **AC restored:** Parent AST-1243 AC5 — “With the candidate in `REQUESTED_ARTIFACTS` and dispatch running, execution history shows the daisy chain progressing hop-by-hop comparably to `BUILD_ARTIFACTS`.” Parent AC6 — “On successful completion, candidate is in `ARTIFACTS_READY` … and each chain rubric’s new content is visible and editable under Artifacts nav.” Parent AC8 — “No craft-rubric hop sequencing list is introduced in `config.py`; succession remains `agent_task.run_next` …”
- **Correct outcome:** After `craft_get_rubric` succeeds and persists, `do_task` recurses into `craft_do_rubric` (then the rest of the live seed chain) with hop-visible execution history; terminal success graduates to `ARTIFACTS_READY` with all chain rubrics populated.
- **Sibling check:** AST-1252 native `do_task` + `persist_candidate_craft_hops` (no `suppress_run_next` on dispatch) remains the entry model — this ticket does not reintroduce a manual hop walk or wrapper keys. AST-1253 Generate/Regenerate handoff still only moves the candidate to `REQUESTED_ARTIFACTS` (unchanged). Live seed topology stays `craft_get_rubric` → `craft_do_rubric` → … (repo JSON authority).
- **Not sufficient:** Removing the stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Hard-coding hop order in `config.py`; treating “get_rubric saved / no exception” as done; swallowing vector-feedback `unknown_code` noise as the fix (capture already returns without failing the hop); inventing a second chain model beside `agent_task.run_next`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Neuter `_apply_ast1113_craft_run_next_chain_migration` (bare `return`, same posture as AST-469 / AST-834 siblings) so schema-ensure cannot rewrite craft `run_next` away from repo JSON | data |
| `src/core/agent.py` | On `persist_candidate_craft_hops` succession: keep live `CALLER_*` hop tokens in `merged_ctx` when recursing; Style D debug when a successful candidate-craft persist hop has empty / invalid `effective_next` | core |

**Out of this ticket’s file list (do not touch):** `config.py` hop lists, Generate/Regenerate UI (AST-1253), `tests/` / bible (Betty), resume daisy-chain, vector-feedback owner-code taxonomy, `data/admin/agent_task.json` craft topology (already correct on tip: `craft_get_rubric` → `craft_do_rubric`).

## Diagnosis (planner)

1. **Fossil migration stomps succession.** `_apply_ast1113_craft_run_next_chain_migration` still hard-codes a pre-head topology, including `("craft_get_rubric", "craft_like_rubric")` — **skips `craft_do_rubric`**. It runs from `_ensure_agent_task_schema` (first ensure per process) and `UPDATE`s + `commit`s live rows. Repo JSON usually re-applies at bootstrap afterward, but any ensure-without-JSON path (or a DB that was last written by the migration) leaves `craft_get_rubric.run_next` pointing at `craft_like_rubric` or otherwise not at `craft_do_rubric`. That matches Susan’s observation that **`craft_do_rubric` did not run** after a successful get persist. Joan already flagged this fossil on AST-1252 plan-discuss (non-blocking then); UAT makes it fix-now.
2. **Same-invocation CALLER strip + hydrate dependency.** After a successful hop, `do_task` strips `CALLER_*` from `merged_ctx` before recurse and relies on agent_data hydration for the child. If hydration fails, `craft_do_rubric` returns `success=False` immediately (often with little hop noise), so the worker fails after get already persisted — looks like “chain stopped after get.” For the candidate craft persist path, keep the just-built live CALLER tokens across the recurse so succession does not depend solely on a round-trip read.

Vector-feedback `unknown_code` / `unparseable` on get is adjacent noise only — `_capture_rubric_vector_feedback` returns without failing the hop.

## Stage 1: Neuter AST-1113 craft run_next migration

**Done when:** `_apply_ast1113_craft_run_next_chain_migration` is a no-op (`return` only, docstring notes superseded by repo JSON / live seed headed by `craft_get_rubric`); `rg '_apply_ast1113_craft_run_next_chain_migration' src/data/database.py` still shows the call site in `_ensure_agent_task_schema` (keep the hook, empty body); no new hop-order list in `config.py`; `python3 -m py_compile src/data/database.py` succeeds.

1. In `src/data/database.py`, replace the body of `_apply_ast1113_craft_run_next_chain_migration` with an immediate `return` (mirror `_apply_ast469_select_job_page_run_next_migration`). Update the docstring to state that AST-1113’s hardcoded craft succession is retired — `data/admin/agent_task.json` applied at bootstrap is the sole craft `run_next` authority (`astral.dispatch.run-next-is-chain-authority`).
2. Do **not** delete the call from `_ensure_agent_task_schema` (keeps the migration slot visible). Do **not** add a replacement hardcoded chain. Do **not** edit `data/admin/agent_task.json` in this ticket.

⚠️ **Decision:** Neuter rather than rewrite the migration to the current seed chain — a second hardcoded list would drift again. Repo JSON already encodes `craft_get_rubric` → `craft_do_rubric` → ….

## Stage 2: Preserve live CALLER tokens on candidate-craft recurse + debug empty succession

**Done when:** When `(ctx or {}).get("persist_candidate_craft_hops")` is truthy and `do_task` is about to recurse to `effective_next`, `merged_ctx` still carries the non-empty `CALLER_*` values from `_chain_tokens_for_next_hop` for this hop (hydration may still run; live tokens win on overlap); when persist_candidate_craft just recorded success and `effective_next` is empty or not in `TASK_CONFIG`, `debug=True` emits a Style D detail naming `task_key` and `planned_next` / reason; UI `suppress_run_next` path unchanged; `python3 -m py_compile src/core/agent.py` succeeds.

1. In `src/core/agent.py`, in the `run_next` dispatch block (after `hop_ctx = _chain_tokens_for_next_hop(...)` and the existing `caller_only_hop` / `non_caller_hop` split, before `await do_task(effective_next, …)`):
   - If `(ctx or {}).get("persist_candidate_craft_hops")` and `effective_next`: after the existing loop that `pop`s `CALLER_HOP_TOKEN_NAMES` from `merged_ctx`, **re-apply** each non-empty value from `caller_only_hop` whose key is in `CALLER_HOP_TOKEN_NAMES` onto `merged_ctx` (same-invocation CALLER authority for the candidate artifacts chain).
   - Do **not** change the strip/hydrate behavior for job `BUILD_ARTIFACTS` or other callers that omit `persist_candidate_craft_hops`.
2. In the same function, when persist_candidate_craft just succeeded (same success region already gated) and later `not effective_next` or `effective_next not in TASK_CONFIG`, if `debug=True`, emit `debug_detail` explaining succession stopped (`planned_next=…`, `suppress_run_next=…`, or `invalid_child=…`) so UAT/Railway logs show why the chain did not continue.
3. Do **not** set `suppress_run_next` on the dispatch worker. Do **not** add hop sequencing in config. Do **not** change vector-feedback capture.

⚠️ **Decision:** Live CALLER re-inject is scoped to `persist_candidate_craft_hops` only — restores same-invocation succession for AST-1252’s candidate path without widening job-chain hydration semantics.

## Execution contract

- Stages in order; one commit per stage on the epic worktree sub; publish to `origin/sub/AST-1243/AST-1264-uat-craft-get-run-next` after each stage per build-child.
- No files outside the Files Changed table.
- Ambiguity or drift → stop and comment on **parent** AST-1243 with the Stage N blocked template.
- Betty owns test/bible updates after Code Complete — engineer does not patch `tests/`.

## Self-Assessment

**Scope:** `Single-Component` — data-layer migration neuter plus a narrow `do_task` succession hardening for the candidate craft persist flag; no new modules or UI.

**Conf:** `high` — fossil migration edges are visible in source and contradict live seed (`get`→`do`); CALLER strip/hydrate path is the documented recurse contract; AST-1252 worker already omits `suppress_run_next`.

**Risk:** `HIGH` — wrong succession fix leaves REQUESTED_ARTIFACTS graduating after a single hop or skipping Do; migration neuter is safe (JSON already authoritative) but CALLER re-inject must stay gated on `persist_candidate_craft_hops` so job chains do not change.

## Rules check

- **§2.6.0 / `astral.dispatch.run-next-is-chain-authority`:** Neuter hardcoded migration; succession stays `agent_task.run_next` / repo JSON — no config hop list.
- **`astral.state.no-daisy-chain-in-run`:** Still uses the documented `do_task` `run_next` carve-out only.
- **§1.3 DRY / in-scope-only:** No second chain walker; no AST-1253 UI; vector-feedback taxonomy out of scope.
- **Betty test-tree ban:** No `tests/` / bible edits in this plan.
- **No conflict requiring conf-!!-NONE.**
