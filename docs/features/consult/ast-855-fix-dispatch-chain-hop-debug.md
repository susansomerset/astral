# Fix dispatch chain hop debug index on multi-hop success

**Linear:** [AST-855 — Fix dispatch chain hop debug index on multi-hop success (Contemplate Job fails on local dev)](https://linear.app/astralcareermatch/issue/AST-855/fix-dispatch-chain-hop-debug-index-on-multi-hop-success-contemplate)  
**Parent:** [AST-852 — Contemplate Job fails on local dev](https://linear.app/astralcareermatch/issue/AST-852/contemplate-job-fails-on-local-dev) (AC reference only — do not expand epic scope)  
**Publish ref:** `origin/sub/AST-852/AST-855-fix-dispatch-chain-hop-debug`

When Susan runs a multi-hop BUILD_ARTIFACTS dispatch chain with `debug=True` (e.g. `anticipate_scan` → `contemplate_job`), the second hop completes the LLM call successfully but crashes in `_write_dispatch_hop_label_on_success` because the hop debug header uses `index=2` with `total=1`. The job hop label write never finishes and the batch aborts. This ticket aligns the success-path hop debug total with the entry-path contract already used in `_resume_hop_debug_index`: when `_dispatch_chain_hop_total` is unset on context, total must be at least the current hop index (never `index > total`).

**Out of scope:** `contemplate_job` prompts/model/content; dispatcher entity batch indexing; dispatch claim/eligibility (AST-849); precomputing full chain hop counts from the `run_next` graph; relaxing AST-538 validation when callers pass explicit index and total; `tests/` edits (Betty at Code Complete).

**Related (context only):** [AST-848](./ast-848-do-task-run-next-chain.md) (dispatch chain in `do_task`), parent AST-852 crash log.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/agent.py` | Shared hop debug index/total helper; fix `_write_dispatch_hop_label_on_success` total fallback | core |

**Verify only (no product change expected):**

| File | Role |
|------|------|
| `src/utils/logging.py` | `format_debug_index_header` validation unchanged — callers must pass valid index/total |
| `src/core/consult.py` | Passes `dispatch_trigger_state` on chain entry; no change expected |

---

## Stage 1: Align dispatch-chain hop debug total on success path

**Done when:** `_write_dispatch_hop_label_on_success` emits a valid Style D header for hop 2+ when `_dispatch_chain_hop_total` is unset; `_resume_hop_debug_index` and the success path share one helper for index/total derivation; repro scenario (`anticipate_scan` → `contemplate_job`, `debug=True`) no longer raises `ValueError: index must be 1..1, got 2/1`; `python3 -m py_compile src/core/agent.py` passes.

1. In `src/core/agent.py`, immediately above `_resume_hop_debug_index` (~line 821), add a module-level helper:

   ```python
   def _dispatch_chain_hop_debug_counts(
       ctx: Optional[Dict[str, Any]],
       *,
       hop_index: Optional[int] = None,
   ) -> tuple[int, int]:
       """Style D index/total for dispatch-chain hop debug when total may be unset on ctx."""
       idx = hop_index
       if idx is None:
           idx = int((ctx or {}).get("_dispatch_chain_hop_index") or 1)
       total = int((ctx or {}).get("_dispatch_chain_hop_total") or 0) if ctx else 0
       # Match entry-path contract: unset/zero total → use current hop index (AST-855).
       effective_total = total if total >= idx else idx
       return idx, effective_total
   ```

2. In `_resume_hop_debug_index`, inside the `if trigger:` branch (~lines 833–844), replace inline `hop_idx` / `total or hop_idx` with:

   ```python
   hop_idx, hop_total = _dispatch_chain_hop_debug_counts(ctx)
   ```

   and pass `index=hop_idx, total=hop_total` to `dbg.debug_index`.

3. In `_write_dispatch_hop_label_on_success` (~lines 895–908), after incrementing `_dispatch_chain_hop_index` on `ctx`, compute debug counts once:

   ```python
   hop_idx = int((ctx or {}).get("_dispatch_chain_hop_index") or 1)
   hop_idx, hop_total = _dispatch_chain_hop_debug_counts(ctx, hop_index=hop_idx)
   ```

   Replace the `dbg.debug_index(...)` call to use `index=hop_idx, total=hop_total` (not `total=... or 1`).

4. Do **not** change `format_debug_index_header` in `src/utils/logging.py` — AST-538 validation stays strict; callers must supply valid pairs.

5. Do **not** set `_dispatch_chain_hop_total` from the `run_next` graph or `resume_artifact_hop_task_keys()` length — parent AST-852 explicitly excludes precomputed chain totals.

6. Run `python3 -m py_compile src/core/agent.py`.

⚠️ **Decision:** Use `effective_total = total if total >= idx else idx` rather than `total or idx` so an explicit total larger than the current hop (e.g. future batch metadata) is preserved, while unset/zero total still expands to the current hop index. This matches `_resume_hop_debug_index`'s prior `total or hop_idx` behavior for the common unset case and fixes the `2/1` crash.

---

## Stage 2: Manual smoke verification

**Done when:** Local multi-hop BUILD_ARTIFACTS chain with `debug=True` completes `contemplate_job` without crash; hop label write debug shows `index ≤ total` (e.g. `2/2`, not `2/1`); job state after successful `contemplate_job` is `BUILD_ARTIFACTS.contemplate_job`.

1. With app running via `launch.sh`, dispatch a job through `anticipate_scan` @ `BUILD_ARTIFACTS` where `run_next` reaches `contemplate_job` (Susan's wired chain).

2. Confirm server log contains a hop-ok Style D line for `contemplate_job` with valid index/total (no `ValueError` from `format_debug_index_header`).

3. Confirm job row state is `BUILD_ARTIFACTS.contemplate_job` (or the runtime label from `dispatch_hop_label(BUILD_ARTIFACTS, "contemplate_job")`).

4. Confirm no regression on first-hop success: `anticipate_scan` hop-ok header remains valid (e.g. `1/1` when total unset).

---

## Test coverage (Betty — Code Complete)

Engineer does **not** edit `tests/`. Betty's manifest for AST-855 must include a component test that reproduces the bug without relying on manual UAT:

- **Scenario:** `do_task("contemplate_job", ...)` with `ctx` carrying `dispatch_trigger_state=BUILD_ARTIFACTS`, `_dispatch_chain_hop_index=2`, `_dispatch_chain_hop_total` **absent or 0**, `debug=True`, mocked successful LLM response, and `write_job_dispatch_hop_label` mocked or stubbed.
- **Assert:** call completes with `success=True`; `debug_index` / log capture shows hop-ok header with `index=2` and `total >= 2` (not `2/1`); no exception from `format_debug_index_header`.
- **Regression:** existing `TestAst848DispatchChainDoTask` cases remain green.

Suggested node (Betty names exact path): extend `tests/component/core/test_agent.py::TestAst848DispatchChainDoTask` or add `TestAst855DispatchChainHopDebug`.

---

## Self-Assessment

**Scope:** `minor` — One helper and two call sites in `src/core/agent.py`; no config, consult, dispatcher, or logging contract changes.

**Conf:** `high` — Root cause is identified in Susan's stack trace and the asymmetry between `_resume_hop_debug_index` (`total or hop_idx`) and `_write_dispatch_hop_label_on_success` (`total or 1`); fix is a one-line semantic alignment behind a small DRY helper.

**Risk:** `low` — Change affects debug-only emission on dispatch-chain hop label success; production paths (`debug=False`) skip `debug_index`; explicit `_dispatch_chain_hop_total` values still honored when `>= hop_index`.

---

## ASTRAL_CODE_RULES self-review

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Helper deduplicates index/total logic shared by entry and success hop debug paths. |
| §1.5 / §1.5.1 | Debug contract unchanged — only fixes invalid index/total pair; no new debug lines when `debug=False`. |
| §2.1 config | No new config keys; does not precompute chain totals (per parent boundary). |
| §2.6.0 | Dispatch chain hop labels and graduation behavior untouched — debug header only. |
| §3.3 imports | Helper stays in `agent.py`; no new cross-layer imports. |
| §3.5 naming | `_dispatch_chain_hop_debug_counts` matches existing `_dispatch_chain_*` prefix. |

No conflicts requiring escalation.

---

## Built

**Publish ref:** `origin/sub/AST-852/AST-855-fix-dispatch-chain-hop-debug`

| Stage | Summary |
|-------|---------|
| 1 | `_dispatch_chain_hop_debug_counts` helper; entry + success hop debug use shared index/total |

**Verify:** `python3 -m py_compile src/core/agent.py` — pass.

---

## Radia review (2026-07-10)

**Diff:** `origin/dev...origin/sub/AST-852/AST-855-fix-dispatch-chain-hop-debug` @ `6ba63c7`  
**AST-855 product commits:** `282119f` helper + success-path alignment · `fc346cd` component tests · `6ba63c7` merge-tests rollup  
**Tests:** manifest green per **Tests Passed** (Betty `TestAst855DispatchChainHopDebug` + **AST-848** regression class)

### What's solid

| Area | Notes |
|------|-------|
| Plan fidelity | Stage 1 delivered exactly: `_dispatch_chain_hop_debug_counts` above `_resume_hop_debug_index`; entry + success paths share helper; `format_debug_index_header` untouched. |
| Root cause | Success path no longer uses `total or 1` — aligns with entry-path contract (`total if total >= idx else idx`); fixes `index 2/1` crash on multi-hop BUILD_ARTIFACTS chains. |
| §1.3 DRY | Single helper replaces duplicated index/total derivation; `_dispatch_chain_*` naming consistent. |
| §1.5.1 / §5f | Debug emission remains gated on `debug=True`; `debug_index` uses valid Style D pairs; existing `debug_detail` on hop-ok path preserved; no new anti-patterns. |
| §2.6.0 boundary | Hop label write + graduation logic unchanged — debug header only; no precomputed chain totals (per plan + parent AST-852). |
| Layering | Helper stays in `src/core/agent.py`; no new cross-layer imports. |
| Self-Assessment | `minor` / `high` / `low` matches actual footprint. |
| Tests + bible | `TestAst855DispatchChainHopDebug` covers helper edge cases + second-hop `contemplate_job` hop-ok log (`2/2`); bible manifest matches. |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| **advisory** | Plan Stage 2 | Manual multi-hop smoke (`anticipate_scan` → `contemplate_job`, `debug=True`) remains parent **AST-852** UAT — not blocking this child. |

### Recommended actions

| Item | Action |
|------|--------|
| fix-now | None — ready for `resolve-child`. |
| discuss | None. |
| advisory | Parent **AST-852** UAT: confirm Stage 2 smoke when Susan exercises the wired chain locally. |

**Counts:** 0 fix-now · 0 discuss · 1 advisory

**Outcome:** Clean — ship.

— Radia

---

## Resolution (2026-07-10)

**Driven by:** Radia review @ `09475f7` on `origin/sub/AST-852/AST-855-fix-dispatch-chain-hop-debug`.

| Item | Change |
|------|--------|
| fix-now | None — review clean. |
| discuss | None. |
| advisory | Stage 2 manual smoke (`anticipate_scan` → `contemplate_job`, `debug=True`) deferred to parent **AST-852** UAT. |

**Verify:** §9a dry-run — publish ref merges cleanly into `origin/dev` and `origin/ftr/AST-852-contemplate-job-hop-debug-crash`.
