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

## Review

**Publish ref:** `origin/sub/AST-1243/AST-1264-uat-craft-get-run-next`  
**Tip:** `02bed622`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `6b00f250` | neuter AST-1113 craft run_next hot-path migration |
| 2 | `02bed622` | live CALLER re-inject; hydrate skip/fail-open; succession debug |

## Radia review

[code-rubric] revision=1

**Rubric:** code-rubric.v1
**Publish ref tip:** `ec8456a5`
**Overall:** FIX-NOW

**Full-set sweep:** all 65 active statutes scored in-session (18 universal + 47 scoped). `origin/dev...origin/sub/AST-1243/AST-1264-uat-craft-get-run-next` is already clean scope for this ticket — `ftr/AST-1243-candidate-artifacts-now-daisy-chain` (AST-1252 + AST-1253) landed on `origin/dev` before this branch was cut, so the two-file diff (`src/core/agent.py`, `src/data/database.py`) is this ticket's full and only contribution.

**Stage 1 — solid:** `_apply_ast1113_craft_run_next_chain_migration` neutered to a bare `return` with a docstring naming repo JSON as authority, mirroring the AST-1108/AST-469/AST-834 no-op species exactly. Call site kept in `_ensure_agent_task_schema` (migration slot stays visible). No replacement hop list added anywhere. `python3 -m py_compile` clean. Betty's tests directly assert the no-op (wrong links left untouched, no ghost rows invented, source body is `return`-only) — good regression lock on the actual root cause (hot-path stomp bypassing `_validate_run_next_graph_acyclic`).

**Stage 2 — root-cause fix confirmed, but one required sub-behavior is dead code:**

- The primary reported bug (get→do stall) is fixed correctly: the parent's re-injection of live `CALLER_*` onto `merged_ctx` (gated on `persist_candidate_craft_hops` + `effective_next`) means the child's `chain_context` (passed as `merged_ctx` into the recursive `do_task` call) already carries live CALLER tokens, so the child's `_live_caller` check is `True` and `_hydrate_caller_chain_context` is skipped entirely — no `hydr_err` early-return, chain continues. Confirmed by `test_persist_craft_reinjects_caller_on_recurse` and `test_persist_craft_skips_hydrate_when_live_caller`.

- **fix-now — dead/unreachable fallback branch (Stage 2 step 2, Revision 1's own fix-now):** The plan (and Joan's round-1 revision) explicitly require: *"on `hydr_err`, if incoming `chain_context` still has any non-empty CALLER token, fall back to `effective_chain_context = chain_context`."* As coded (`src/core/agent.py` ~2006–2036), the `else:` branch that calls `_hydrate_caller_chain_context` is only reached when `_live_caller` (`_persist_craft and any(chain_context.get(k) for k in CALLER_HOP_TOKEN_NAMES)`) was already `False`. The `hydr_err` branch re-evaluates the *identical* expression against the *same* `chain_context` — which is never mutated between the two checks (no `await`, and `_hydrate_caller_chain_context` only reads its `chain_context` argument, per `src/core/agent.py:881-907`) — so it is guaranteed to evaluate `False` again. The fallback `effective_chain_context = chain_context` at line ~2028 can never execute; that scenario always falls through to the pre-existing hard `success=False` return. Betty's own test suite reflects this gap: `test_persist_craft_hydrate_hard_fails_without_live_caller` exercises "no live caller → hydrate fails → hard fail," and `test_persist_craft_skips_hydrate_when_live_caller` exercises "live caller from the start → hydrate skipped" — there is no (and, given the current structure, cannot be a) third test for "no live caller initially, hydrate fails, tokens recovered for fallback," because that branch is unreachable. Recommend: either drop the dead fallback block (skip-hydrate already covers the real recurse path — re-scope the plan's "fail-open" language to the skip case only) or, if a genuine fallback is still wanted for hops reached via a path other than direct parent re-inject (e.g. resumed/retried hops where `chain_context` might legitimately differ from what was checked), source the fallback from the actual re-inject data (`hop_ctx`/`caller_only_hop` equivalent) rather than re-checking the same unmutated `chain_context`.

- Debug additions (`candidate_craft_persisted` gating the two new `debug_detail` succession-stopped lines) are correctly scoped and match Stage 2 step 3 — fires only after a real persist, on both the clean-terminal (`planned_next` empty) and invalid-child paths.

- Non-`persist_candidate_craft_hops` paths (jobs, etc.) are unaffected: `_persist_craft` short-circuits `_live_caller` to `False` unconditionally, so hydrate-or-fail semantics are unchanged for every caller outside this ticket's scope.

**Plan adherence:** Files Changed table matches exactly (2 files, no config.py hop list, no UI, no tests/bible from the engineer). Self-Assessment `Risk: HIGH` was earned — the dead fallback above is exactly the kind of subtlety that risk flag was warning about. No `!!-NONE` conflict.

**Cross-ticket boundary:** No AST-1253 UI touched; no resume daisy-chain; no vector-feedback taxonomy changes; `data/admin/agent_task.json` untouched as planned.

**Pattern conformance:** `pattern.dispatch.run-next-chain-authority` — conforms; succession stays on `agent_task.run_next` / repo JSON, no parallel hop list introduced anywhere (config.py untouched).

## Frame diff

(none — ticket description accurately describes the bug and fix scope)

context_tokens≈31000

— Radia
