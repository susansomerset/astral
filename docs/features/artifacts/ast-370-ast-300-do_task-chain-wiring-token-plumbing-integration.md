# AST-370 — [AST-300] do_task chain wiring + token plumbing integration

**Linear:** [AST-370](https://linear.app/astralcareermatch/issue/AST-370/ast-300-do-task-chain-wiring-token-plumbing-integration)  
**Parent epic:** [AST-300](https://linear.app/astralcareermatch/issue/AST-300/build-resume-artifact) — Build Resume Artifact  
**Feature branch:** `<agent>/ast-370-ast-300-do_task-chain-wiring-token-plumbing-integration`

This ticket is **Ada-owned integration**: ensure the **resume artifact pipeline** (parent **AST-300**) can drive **`do_task`** through **`run_next` chains** ( **AST-303** ) with **chain tokens** ( **AST-304** ) so each hop’s prompts resolve correctly and **§2.4** `batch_id` continuity holds. **AST-300** owns product wiring (when a job hits `RECOMMENDED`, which `task_key` starts the chain, where `job_data.artifacts.resume_content` is written). **AST-370** owns **core** behavior so that orchestration does not re-fetch data the caller already has and does not drop `chain_context` between hops.

⚠️ **Decision:** Linear **blockedBy** **AST-296** — do not merge implementation until **AST-296** is **Done** on `dev` (or the plan explicitly lists any substitute contract). **AST-303** and **AST-304** must also be merged to `dev` before this branch merges, or this branch must merge/rebase them in the integration PR and call that out in the PR body.

---

## Files changed (planned)

| File | Change | Layer |
|------|--------|--------|
| `src/core/agent.py` | Ensure recursive `do_task` hop builds **merged** `chain_context` for `resolve_tokens` per **AST-304** (caller response + cache block strings); keep same outer `ctx` / kwargs per **AST-303** Revision 1; avoid new `get_*` solely to re-fetch caller-owned blobs. | core |
| `src/utils/config.py` | **Only if** new chain token names or `TOKEN_SOURCES` entries are required for resume-specific tokens not already covered by **AST-304** / **AST-365** — otherwise unchanged. | utils |
| `src/core/tracker.py` or `src/core/dispatcher.py` | **Only** the minimal hook **AST-300** specifies for “first `do_task` call into resume chain” — if parent plan places the trigger elsewhere, follow **AST-300** execution doc instead and **do not** duplicate orchestration here. | core |

---

## Stage 1 — Dependency gate + inventory

**Done when:** Branch rebases on `dev` with **AST-303**, **AST-304**, and **AST-296** present; grep confirms `run_next` on `get_agent_task` rows and `resolve_tokens(..., chain_context=...)` signature; any gap is documented in a PR comment (not silent).

1. `git fetch origin && git merge origin/dev` (or rebase) on this feature branch until `origin/dev` includes merged **AST-303** + **AST-304** + **AST-296**.
2. In `src/core/agent.py`, read the **post-AST-303** success-path tail: confirm where the next hop’s `chain_context` dict is built (or missing).
3. List every **`TOKEN_SOURCES`** entry with `"source": "chain"` used by **TASK_CONFIG** keys that participate in the resume pipeline (per parent **AST-300** / **BUILD_CONFIG** when documented). Confirm each key is populated on **hop ≥ 2** after **AST-304**’s contract.

---

## Stage 2 — `chain_context` merge for chained hops

**Done when:** For a two-hop `run_next` chain in a local test or minimal harness, **hop 2** resolves `{$CALLER_RESPONSE}` (and any required `{$CACHE_BLOCK_*}`) using **hop 1**’s assembled content; no duplicate Anthropic round-trip beyond the chain itself.

1. In `src/core/agent.py`, in the code path that invokes `await do_task(...)` for the **next** `task_key` after a successful hop, construct `chain_context_next` by **starting from** the same base as the current hop’s `_chain_context(agent_row)` / `chain_context_selected_agent` output, then **overlay** string values required by **AST-304** for:
   - prior structured or raw response text appropriate for `{$CALLER_RESPONSE}` (match **AST-304** field names in `TOKEN_SOURCES`);
   - `{$CACHE_BLOCK_A}` … `{$CACHE_BLOCK_D}` derived from the **completed** hop’s cached system/user assembly (use the same string sources the audit `runtime_prompt` uses — **do not** invent parallel block assembly).
2. Thread `chain_context_next` into the recursive `do_task` call in the shape **AST-303** + **AST-304** standardized (if **AST-303** passes `ctx` only, extend **only** the agreed kwargs — **stop and comment** if the merged code path has no hook for `chain_context` and **AST-303** did not add one).
3. Preserve **same** `live_content`, `index`, `ctx`, `debug`, `store_agent_data` across hops unless **AST-300**’s execution doc documents a narrowed shape for a named hop.

---

## Stage 3 — Resume pipeline entry (minimal, parent-aligned)

**Done when:** A single **exported** async function (name from **AST-300** plan; if unspecified, use `run_resume_artifact_chain_for_job`) exists in the module **AST-300** names, callable with `(astral_job_id: str, ctx: Dict[str, Any])`, returns the **final** `do_task` result dict from the chain. No dispatcher subscription unless **AST-300** Stage explicitly assigns it here.

1. Implement the function body as: resolve **first** `task_key` from **AST-300** / **BUILD_CONFIG** (when present); if not yet in config, **stop** with 🛑 Linear comment — do not hardcode a full pipeline list in **agent.py**.
2. Inside the function, build the **minimal** `ctx` / `candidate_data` slice the first hop needs (orchestrate objects already loaded for the job — **no** new `get_job` if the caller passed `job` dict).
3. `return await do_task(first_task_key, live_content=..., index=astral_job_id, ctx=ctx, ...)` relying on **`run_next`** for further hops.

---

## Self-review vs ASTRAL_CODE_RULES

| Rule | Check |
|------|--------|
| §1.3 DRY | One merge helper for chain_context; no second copy in `anthropic.py`. |
| §2.1 config | New literals for pipeline ordering live under **BUILD_CONFIG** / parent plan — not scattered in core. |
| §2.4 batch | Same `log_batch_id` / entity index across hops in one chain. |
| §2.6 state machine | Resume chain does not auto-transition **job** states; **AST-300** owns transitions. |
| §3.3 imports | Core → data, utils, external only. |
| §3.5 naming | snake_case; align with `run_next`, `chain_context` naming from **AST-303**/**AST-304**. |

**Conflicts:** If **AST-303** lands without a `chain_context` parameter on the recursive `do_task` call, **Stage 2** blocks — resolve in **AST-303** or extend in this PR with a single agreed kwargs shape.

---

## Self-Assessment

**Scope — `scope-MAJOR-CHANGE`**  
Touches `do_task` chain handoff in **`src/core/agent.py`** and possibly a thin job entry in **core**; behavior affects every multi-hop resume run once **AST-300** connects.

**Conf — `Medium`**  
Depends on **AST-303**/**AST-304**/**AST-296** merge order and on **AST-300**’s orchestration contract; chain_context merge details must match token registry.

**Risk — `HIGH`**  
Wrong merge drops tokens or doubles spend; bad `batch_id` handling breaks §2.4 audit trails for artifact jobs.

---

## Review stub (build)

Built by Ada.

- **Branch:** `chuckles/ast-370-ast-300-do_task-chain-wiring-token-plumbing-integration`
- **Implementation commit:** `b134ee13`
