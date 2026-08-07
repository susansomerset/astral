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
| `src/data/database.py` | Neuter `_apply_ast1113_craft_run_next_chain_migration` (bare `return`, same species as AST-1108 / AST-469 / AST-834) so schema-ensure cannot rewrite craft `run_next` away from repo JSON | data |
| `src/core/agent.py` | Candidate-craft path: pass live `CALLER_*` into recurse **and** skip/fail-open hydration when those live tokens are already present; Style D debug when a successful candidate-craft persist hop has empty / invalid `effective_next` | core |

**Out of this ticket’s file list (do not touch):** `config.py` hop lists, Generate/Regenerate UI (AST-1253), `tests/` / bible (Betty), resume daisy-chain, vector-feedback owner-code taxonomy, `data/admin/agent_task.json` craft topology (already correct on tip: `craft_get_rubric` → `craft_do_rubric`).

## Diagnosis (planner)

1. **Fossil migration stomps succession (root cause for skipped `craft_do_rubric`).** `_apply_ast1113_craft_run_next_chain_migration` (`database.py`) hard-codes a near-reversed topology vs live seed — notably `craft_get_rubric` → `craft_like_rubric` (skips do) and `craft_do_rubric` → `craft_get_rubric`. It is **corrective** (re-`UPDATE`s whenever live differs), called from `_ensure_agent_task_schema` (per-process hot path, many call sites), and writes via raw `conn.execute` + `conn.commit()` that **bypass `_validate_run_next_graph_acyclic`**. That is exactly the **Violating** shape of `astral.seed.boot-only-not-hot-path` (“prompt-seed helper inside schema ensure on every connection open”). Closest precedent is **AST-1108** (three migrations directly above this one already neutered for the same forever-overwrite failure); AST-1113 was missed in that sweep. Repo JSON usually re-applies at bootstrap afterward, but ordering varies by process — neuter regardless. Matches Susan’s symptom that **`craft_do_rubric` did not run**.
2. **Hydration abort on the child hop (same-invocation succession).** After a successful hop, `do_task` strips `CALLER_*` from `merged_ctx`, sets `_hop_parent_task_key`, and recurses. `craft_do_rubric` references `CALLER_RESPONSE`; the child always enters `_hydrate_caller_chain_context` when that parent key is set. On `hydr_err` (`agent.py` ~2014–2021) the child returns `success=False` **before** LLM / hop ledger — chain stops after get with little hop noise. **Re-injecting CALLER onto `merged_ctx` alone does not fix this:** the hydration gate does not check whether CALLER is already populated, and on `hydr_err` the function returns before `_merge_hydrated_caller_context`. Fix must land at the hydration abort (skip when live CALLER already present, and/or fall back to live tokens on `hydr_err`), scoped to `persist_candidate_craft_hops`. Note: `_merge_hydrated_caller_context` overwrites incoming CALLER with hydrated values (hydrated wins on overlap) — do not claim the opposite.

Vector-feedback `unknown_code` / `unparseable` on get is adjacent noise only — `_capture_rubric_vector_feedback` returns without failing the hop.

**AC6:** Terminal `ARTIFACTS_READY` + full rubric visibility is existing AST-1252 graduation/persist behavior. This plan restores succession so a full chain can complete; **AC6 verification belongs to the UAT re-test** after Code Complete / Tests Passed (not a compile-time Done when on these stages).

## Stage 1: Neuter AST-1113 craft run_next migration

**Done when:** `_apply_ast1113_craft_run_next_chain_migration` is a no-op (`return` only, docstring notes superseded by repo JSON / live seed headed by `craft_get_rubric`, cites AST-1108 / `astral.seed.boot-only-not-hot-path`); `rg '_apply_ast1113_craft_run_next_chain_migration' src/data/database.py` still shows the call site in `_ensure_agent_task_schema` (keep the hook, empty body); no new hop-order list in `config.py`; `python3 -m py_compile src/data/database.py` succeeds.

1. In `src/data/database.py`, replace the body of `_apply_ast1113_craft_run_next_chain_migration` with an immediate `return` (mirror AST-1108 / `_apply_ast469_select_job_page_run_next_migration`). Update the docstring: AST-1113’s hardcoded craft succession is retired — `data/admin/agent_task.json` applied at bootstrap is the sole craft `run_next` authority (`astral.dispatch.run-next-is-chain-authority`); schema-ensure must not rewrite prompt/chain edges (`astral.seed.boot-only-not-hot-path`).
2. Do **not** delete the call from `_ensure_agent_task_schema` (keeps the migration slot visible). Do **not** add a replacement hardcoded chain. Do **not** edit `data/admin/agent_task.json` in this ticket.

⚠️ **Decision:** Neuter rather than rewrite the migration to the current seed chain — a second hardcoded list would drift again and still violate boot-only-not-hot-path. Repo JSON already encodes `craft_get_rubric` → `craft_do_rubric` → ….

## Stage 2: Live CALLER on candidate-craft recurse + hydration fail-open + debug

**Done when:** With `(ctx or {}).get("persist_candidate_craft_hops")` truthy, a successful `craft_get_rubric` hop that has non-empty live CALLER tokens from `_chain_tokens_for_next_hop` can recurse into `craft_do_rubric` **even when upstream agent_data for that hop is absent or empty** (hydration skipped or `hydr_err` falls back to live tokens — child does **not** return `success=False` solely for hydration miss); job / non-persist paths keep today’s hydrate-or-fail semantics; when persist_candidate_craft just recorded success and `effective_next` is empty or not in `TASK_CONFIG`, `debug=True` emits a Style D detail naming `task_key` and `planned_next` / reason; UI `suppress_run_next` path unchanged; `python3 -m py_compile src/core/agent.py` succeeds.

1. In `src/core/agent.py`, in the `run_next` dispatch block (after `hop_ctx = _chain_tokens_for_next_hop(...)` and the existing `caller_only_hop` / `non_caller_hop` split, before `await do_task(effective_next, …)`):
   - If `(ctx or {}).get("persist_candidate_craft_hops")` and `effective_next`: after the existing loop that `pop`s `CALLER_HOP_TOKEN_NAMES` from `merged_ctx`, **re-apply** each non-empty value from `caller_only_hop` whose key is in `CALLER_HOP_TOKEN_NAMES` onto `merged_ctx` (so the child invocation actually receives live CALLER — matches the existing `caller_hydration=live_llm` debug claim).
2. In the **child** hydration block near the top of `do_task` (where `parent_for_hydration` + `_hydrate_caller_chain_context` run, ~2004–2024), when `(ctx or {}).get("persist_candidate_craft_hops")` is truthy:
   - If incoming `chain_context` already has any non-empty `CALLER_HOP_TOKEN_NAMES` value (same shape `_caller_key_status` inspects): **skip** `_hydrate_caller_chain_context` and keep `effective_chain_context = chain_context`.
   - Else run hydrate as today; on `hydr_err`, if incoming `chain_context` still has any non-empty CALLER token, **fall back** to `effective_chain_context = chain_context` and continue (do not return `success=False`); only return the hard failure when there are no live CALLER tokens to fall back to.
   - Do **not** change hydrate-or-fail for callers that omit `persist_candidate_craft_hops`.
3. When persist_candidate_craft just succeeded and later `not effective_next` or `effective_next not in TASK_CONFIG`, if `debug=True`, emit `debug_detail` explaining succession stopped (`planned_next=…`, `suppress_run_next=…`, or `invalid_child=…`).
4. Do **not** set `suppress_run_next` on the dispatch worker. Do **not** add hop sequencing in config. Do **not** change vector-feedback capture.

⚠️ **Decision:** Fix at the hydration abort (skip / fail-open), not only at the parent recurse setup. Re-inject remains necessary so live tokens exist for the child to skip/fall back on. Scoped to `persist_candidate_craft_hops` so job `BUILD_ARTIFACTS` hydration semantics stay unchanged.

## Execution contract

- Stages in order; one commit per stage on the epic worktree sub; publish to `origin/sub/AST-1243/AST-1264-uat-craft-get-run-next` after each stage per build-child.
- No files outside the Files Changed table.
- Ambiguity or drift → stop and comment on **parent** AST-1243 with the Stage N blocked template.
- Betty owns test/bible updates after Code Complete — engineer does not patch `tests/`.

## Revisions

### Revision 1 — 2026-08-07
Driven by: Joan `[plan-discuss] round=1 concern` (plan-rubric.v1 REVISE @ `3bf470c5`).
Changes:
- **fix-now:** Stage 2 now fixes the child hydration abort (skip when live CALLER present; fall back on `hydr_err`) — re-inject alone was insufficient because hydrate still runs and returns before merge.
- **Stage 1:** Strengthened diagnosis — `astral.seed.boot-only-not-hot-path`, AST-1108 precedent, raw UPDATE bypasses acyclic validate; neuter rationale unchanged.
- **discuss AC6:** Explicitly UAT re-test owns terminal `ARTIFACTS_READY` / full rubric visibility after succession is restored.
- Corrected token-precedence note: hydrated overwrites incoming on merge.

## Self-Assessment

**Scope:** `Single-Component` — data-layer migration neuter plus a narrow `do_task` succession/hydration hardening for the candidate craft persist flag; no new modules or UI.

**Conf:** `high` — fossil migration edges and the hydration early-return are both readable in source; Joan confirmed the Stage 2 abort site; AST-1252 worker already omits `suppress_run_next`.

**Risk:** `HIGH` — wrong succession leaves REQUESTED_ARTIFACTS after a single hop or skips Do; hydration fail-open must stay gated on `persist_candidate_craft_hops` so job chains do not change; empty CALLER + hydr_err must still hard-fail.

## Rules check

- **§2.6.0 / `astral.dispatch.run-next-is-chain-authority`:** Neuter hardcoded migration; succession stays `agent_task.run_next` / repo JSON — no config hop list.
- **`astral.seed.boot-only-not-hot-path`:** Stage 1 removes prompt/chain rewrite from schema-ensure hot path.
- **`astral.state.no-daisy-chain-in-run`:** Still uses the documented `do_task` `run_next` carve-out only.
- **§1.3 DRY / in-scope-only:** No second chain walker; no AST-1253 UI; vector-feedback taxonomy out of scope.
- **Betty test-tree ban:** No `tests/` / bible edits in this plan.
- **No conflict requiring conf-!!-NONE.**
