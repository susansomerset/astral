# AST-570 — DeepSeek cost math, mapping, and backfill

**Parent:** [AST-569 — Timesheets for deepseek are inaccurate](https://linear.app/astralcareermatch/issue/AST-569/timesheets-for-deepseek-are-inaccurate)  
**Ticket:** [AST-570](https://linear.app/astralcareermatch/issue/AST-570/deepseek-cost-math-mapping-and-backfill-timesheets-for-deepseek-are)  
**Publish ref (origin):** `sub/AST-569/AST-570-deepseek-cost-math-mapping-backfill`

Correct DeepSeek timesheet **token buckets** and **calc_cost_*** so they match DeepSeek’s published cache-hit / cache-miss / output billing (not Anthropic cache-write semantics), fix **deepseek-v4-pro** pricing literals, recompute all historical **agent_timesheets** rows for DeepSeek SKUs, and ship a repeatable UTC-day reconciliation procedure against the vendor usage export. **Anthropic** rows and `calculate_cost_components` must remain byte-for-byte in behavior.

**Out of scope (sibling / parent):** Admin Agent Timesheets React columns (**AST-571**); brain-tier routing; schema changes.

**Pricing snapshot date (ship):** 2026-06-03 — [DeepSeek Models & Pricing](https://api-docs.deepseek.com/quick_start/pricing).

## DeepSeek → ledger mapping (authoritative for this ticket)

DeepSeek bills three input/output categories. Astral keeps the **existing** `agent_timesheets` columns (AST-494); only **semantics** for `provider=deepseek` rows change.

| DeepSeek export `type` | Stored column | Source on API usage (Anthropic-compat Messages API) | `calc_cost_*` key |
|------------------------|---------------|-----------------------------------------------------|-------------------|
| `input_cache_hit_tokens` | `cache_read_tokens` | `usage.cache_read_input_tokens` (0 if missing) | `calc_cost_cache_read` ← `cpm_cache_read` |
| `input_cache_miss_tokens` | `total_no_cache_input_tokens` | `usage.input_tokens` (must equal vendor **cache miss** count, not “fresh after breakpoint” unless docs prove identical) | `calc_cost_no_cache_input` ← `cpm_input` |
| `output_tokens` | `total_output_tokens` | `usage.output_tokens` | `calc_cost_output` ← `cpm_output` |
| *(not billed)* | `cache_write_tokens` | always **0** | `calc_cost_cache_write` always **0.0** |

**Unchanged diagnostic columns (not used in dollar reconciliation):** `no_cache_prompt_tokens`, `no_cache_live_tokens` — keep populating from char estimates in `agent.py` / `send_to_deepseek` kwargs; do **not** add them to export reconciliation sums.

⚠️ **Decision:** Reuse Anthropic-shaped column names so **AST-571** can sum `calc_cost_*` without schema work; map DeepSeek **miss** into `total_no_cache_input_tokens` and **hit** into `cache_read_tokens`, not into `cache_write_tokens`.

### UTC 2026-06-03 acceptance anchors (parent Original brief + export)

| Model | Export cache-hit tokens | Export cache-miss tokens | Export output tokens | Export $ total (price × amount sum) |
|-------|-------------------------|--------------------------|----------------------|-------------------------------------|
| `deepseek-v4-pro` | 54,400 | 39,339 | 23,547 | hit `0.1972` + miss `0.017112465` + out `0.02048589` ≈ **$0.2348** |
| `deepseek-v4-flash` | 6,656 | 3,874 | 3,102 | hit `0.0186368` + miss `0.00054236` + out `0.00086856` ≈ **$0.0200** |

Pro row sample: summed `cache_read_tokens` across the four pro rows in the parent CSV equals **54,400** — hit mapping is already correct on stored data. Dollar drift is driven mainly by **wrong `DEEPSEEK_MODEL_PRICING` for `deepseek-v4-pro`** today (`cpm_cache_read` / `cpm_input` / `cpm_output` do not match the export unit prices). After pricing fix, backfill must still prove **miss** and **output** column sums match export for the **full UTC day** (all `agent_req_id` rows in scope, not only the four-row CSV excerpt).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Correct `DEEPSEEK_MODEL_PRICING["deepseek-v4-pro"]` to official cache-hit / cache-miss / output CPM; update snapshot comment date; leave `deepseek-v4-flash` unchanged (already matches docs). | utils |
| `src/utils/cost_calculator.py` | Add `deepseek_usage_to_token_counts(usage) -> dict`; add `calculate_cost_components_deepseek_from_counts(...)` for backfill; refactor `calculate_cost_components_deepseek` to use shared math. | utils |
| `src/external/deepseek.py` | Build `_timesheet_kwargs` from `deepseek_usage_to_token_counts` + new cost helper; force `cache_write_tokens=0`. | external |
| `src/data/database.py` | Add `backfill_deepseek_agent_timesheet_costs()` — `UPDATE` all rows with `model_code` in `DEEPSEEK_MODEL_PRICING` keys; recompute four `calc_cost_*` from stored token integers. | data |
| `debug/spikes/ast-570-deepseek-export-reconcile/reconcile.py` | CLI: load DeepSeek export CSV + query `agent_timesheets` for UTC date; print per-model token and dollar deltas (Susan UAT). | spike (gitignored dir) |
| `tests/component/utils/test_cost_calculator_deepseek.py` | Golden token→cost cases for both SKUs; pro pricing matches export line math. | tests |
| `tests/component/data/database/test_timesheets.py` | Backfill updates `calc_cost_*` for seeded deepseek row; anthropic row untouched. | tests |
| `docs/ASTRAL_TEST_BIBLE.md` | §7 entry for AST-570 manifest paths (Betty adds in qa-astral). | docs |

## Stage 1: Pricing literals and shared cost math

**Done when:** `DEEPSEEK_MODEL_PRICING["deepseek-v4-pro"]` matches the pricing table (per-1M: hit `3.625`, miss `0.435`, output `0.87`); flash row unchanged; unit tests prove one pro and one flash row match export `price × amount` within `1e-9` per component.

1. In `src/utils/config.py`, inside `DEEPSEEK_MODEL_PRICING["deepseek-v4-pro"]`, set `cpm_cache_read` to `3.625`, `cpm_input` to `0.435`, `cpm_output` to `0.87`, `cpm_cache_write` to `0.0`. Update the block comment snapshot date to `2026-06-03`.
2. In `src/utils/cost_calculator.py`, add:

```python
def deepseek_usage_to_token_counts(usage) -> dict:
    """Return cache_read, cache_miss, output, cache_write ints for DeepSeek billing."""
```

   - `cache_read` = `getattr(usage, "cache_read_input_tokens", 0) or 0`
   - `cache_miss` = `usage.input_tokens` (document in docstring: DeepSeek compat reports miss here; if Stage 2 spike disproves, stop and comment on **AST-570**)
   - `output` = `usage.output_tokens`
   - `cache_write` = `0`

3. Add `calculate_cost_components_deepseek_from_counts(cache_read, cache_miss, output, cache_write, vendor_model)` returning the same four `calc_cost_*` keys using `DEEPSEEK_MODEL_PRICING`.
4. Change `calculate_cost_components_deepseek(usage, vendor_model)` to call steps 2–3 only (no duplicate formulas).

## Stage 2: Live recording path (`send_to_deepseek`)

**Done when:** A mocked `messages.create` with usage `{input_tokens: 100, cache_read_input_tokens: 50, output_tokens: 25}` produces `_timesheet_kwargs` with `cache_read_tokens=50`, `total_no_cache_input_tokens=100`, `total_output_tokens=25`, `cache_write_tokens=0`, and `calc_cost_*` matching `calculate_cost_components_deepseek_from_counts`.

1. In `src/external/deepseek.py`, after `usage = response.usage`, call `counts = deepseek_usage_to_token_counts(usage)` and `cost_parts = calculate_cost_components_deepseek_from_counts(...)` (or the usage wrapper).
2. Set `_timesheet_kwargs` fields: `cache_write_tokens=counts["cache_write"]`, `cache_read_tokens=counts["cache_read"]`, `total_no_cache_input_tokens=counts["cache_miss"]`, `total_output_tokens=counts["output"]`; keep `no_cache_prompt_tokens` / `no_cache_live_tokens` from existing kwargs unchanged.
3. Extend `tests/component/external/test_deepseek.py` (or add beside existing mocks) to assert the kwargs passed to `record_timesheet` match the table above.

## Stage 3: Historical backfill (database)

**Done when:** Running `backfill_deepseek_agent_timesheet_costs()` in a test DB updates every row with `model_code IN ('deepseek-v4-flash','deepseek-v4-pro')` and leaves rows with `model_code` like `claude-sonnet-4-6` unchanged; function is idempotent (second run identical).

1. In `src/data/database.py`, add `backfill_deepseek_agent_timesheet_costs() -> int` (returns rows updated).
2. SQL scope: `SELECT agent_req_id, model_code, cache_write_tokens, cache_read_tokens, total_no_cache_input_tokens, total_output_tokens FROM agent_timesheets WHERE model_code IN (...)` — keys from `DEEPSEEK_MODEL_PRICING`.
3. For each row, compute costs via `calculate_cost_components_deepseek_from_counts` using **stored** token integers (do not alter token columns in this stage unless Stage 4 proves miss integers wrong).
4. `UPDATE agent_timesheets SET calc_cost_cache_write=?, calc_cost_cache_read=?, calc_cost_no_cache_input=?, calc_cost_output=? WHERE agent_req_id=?`.
5. Do **not** write to `anthropic_timesheets` (DeepSeek rows are agent ledger only per AST-494).
6. Export `backfill_deepseek_agent_timesheet_costs` through `src/core/timesheets.py` as `backfill_deepseek_timesheet_costs` only if admin/script entry is needed; otherwise keep DB-only and invoke from reconciliation script step below.

⚠️ **Decision:** Backfill pass 1 recomputes **costs only** from existing token columns. If reconcile script (Stage 4) shows miss token drift, add pass 2 in a follow-up commit within this ticket — do not improvise token rewrites without a documented rule.

## Stage 4: Reconciliation script (Susan UAT)

**Done when:** Susan can run one command against a copied DeepSeek export CSV and see PASS/FAIL for UTC 2026-06-03 pro and flash token and dollar totals vs `agent_timesheets`.

1. Create `debug/spikes/ast-570-deepseek-export-reconcile/reconcile.py` (gitignored parent per **orientation-astral**).
2. CLI args: `--export-csv PATH`, `--utc-date YYYY-MM-DD`, optional `--db` (default prod path from env if present else test fixture).
3. Parse export rows: group by `model` + `type` (`input_cache_hit_tokens`, `input_cache_miss_tokens`, `output_tokens`).
4. Query SQL: `SELECT model_code, SUM(cache_read_tokens), SUM(total_no_cache_input_tokens), SUM(total_output_tokens), SUM(calc_cost_cache_write+calc_cost_cache_read+calc_cost_no_cache_input+calc_cost_output) FROM agent_timesheets WHERE date(created_at)=? AND model_code IN (...) GROUP BY model_code`.
5. Print side-by-side table; exit code `1` on any token or dollar mismatch (tolerance: costs `1e-6` per component sum, tokens exact integer match).
6. Document in plan comment on **AST-570** after first green run: exact command Susan used.

7. After backfill implementation, add a one-line admin or shell entry in script docstring only — **no** new Flask route unless Susan asks.

## Stage 5: Tests and bible handoff

**Done when:** `pytest tests/component/utils/test_cost_calculator_deepseek.py tests/component/data/database/test_timesheets.py -q` passes; existing Anthropic cost tests unchanged.

1. Add `tests/component/utils/test_cost_calculator_deepseek.py` with:
   - Pro row `840f7662-a5de-44cd-ac2e-09fade0aca81` token counts from parent CSV → costs matching stored export math at new CPMs.
   - Flash single-row sample `f778a6ce-b336-4e62-878d-7d1f82b347fa`.
   - Assert `calculate_cost_components` (Anthropic) still passes existing tests in `test_cost_calculator.py` if present, or run full utils component folder.
2. Extend `tests/component/data/database/test_timesheets.py`: insert deepseek + anthropic rows, run `backfill_deepseek_agent_timesheet_costs()`, assert deepseek costs changed and anthropic identical.
3. Do **not** weaken `TestAst492BrainSettingDoTask` or Anthropic timesheet tests.

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — Touches config pricing, pure cost math, external client recording, and data-layer backfill across the DeepSeek ledger path.

**Conf:** `high` — Official pricing page and parent export supply exact CPMs and reconciliation targets; remaining risk is confirming `usage.input_tokens` equals cache-miss on live API (Stage 2 test + optional manual smoke).

**Risk:** `HIGH` — Incorrect mapping or pro CPMs regress spend reporting and parent UAT; Anthropic path must stay isolated via separate functions and backfill SQL filter on `model_code`.

## Self-review vs ASTRAL_CODE_RULES

- **§2.1:** Pricing literals only in `config.py`; snapshot date in comment.
- **§1.3 DRY:** Single `calculate_cost_components_deepseek_from_counts`; no duplicated `/ 1_000_000` math in `deepseek.py` or `database.py`.
- **§3.3:** `cost_calculator` imports only `config`; `deepseek.py` imports `cost_calculator`, not `database`; backfill in `database.py` imports cost helper from utils (allowed: data → utils).
- **§3.6:** Reconciliation script under `debug/spikes/ast-570-deepseek-export-reconcile/`, not repo-root `artifacts/`.
- **§2.4 / state machine:** No dispatch changes.

No `conf-!!-NONE`.

## Execution contract

- Execute stages in order; one commit per stage on `dev-ada`; Joan `store-code-commit` after each stage commit (build-astral §6).
- If `usage.input_tokens` does not equal export miss for a live `agent_req_id`, stop and post on **AST-570**:

```
🛑 Stage 2 blocked: DeepSeek usage.input_tokens ≠ export cache-miss
Step: Stage 2 — map usage to total_no_cache_input_tokens
Issue: <paste usage dict and export row>
Proposed resolutions: (1) use alternate usage field <name> (2) derive miss as input_total - cache_read (3) need Susan/vendor doc
```

- Do not edit **AST-571** UI files.

## Review (build)

**Branch:** `origin/sub/AST-569/AST-570-deepseek-cost-math-mapping-backfill`  
**Tip:** `48321b2ed23c2b2f91772eae9d7e3a71226d94ea` (Joan store-code-commit after stage 3)

**Stages shipped (product):**
1. `DEEPSEEK_MODEL_PRICING` pro CPMs + `deepseek_usage_to_token_counts` / `calculate_cost_components_deepseek_from_counts`
2. `send_to_deepseek` timesheet kwargs via shared mapping (`cache_write_tokens=0`)
3. `backfill_deepseek_agent_timesheet_costs()` in `database.py`

**Susan UAT reconcile (local, gitignored):**  
`python3 debug/spikes/ast-570-deepseek-export-reconcile/reconcile.py --export-csv <path> --utc-date 2026-06-03`

**Tests:** Betty at Code Complete (`qa-astral`) per plan Stage 5.

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-569/AST-570-deepseek-cost-math-mapping-backfill` (tip `96aebe5e` after tests). **Baseline:** `origin/dev`.

### What's solid

- **§2.1 / plan Stage 1:** `DEEPSEEK_MODEL_PRICING["deepseek-v4-pro"]` CPMs (`3.625` / `0.435` / `0.87`) and snapshot comment `2026-06-03`; flash row unchanged.
- **§1.3 DRY:** `deepseek_usage_to_token_counts` + `calculate_cost_components_deepseek_from_counts` shared by `calculate_cost_components_deepseek`, `send_to_deepseek`, and `backfill_deepseek_agent_timesheet_costs`.
- **§3.3:** `cost_calculator` → `config` only; `deepseek.py` → `cost_calculator` only; `database.py` → utils helper (allowed data → utils).
- **Plan Stage 2:** `TestSendToDeepseekTimesheetMapping` pins `cache_read_tokens` / `total_no_cache_input_tokens` / `total_output_tokens` / `cache_write_tokens=0` and matching `calc_cost_*`.
- **Plan Stage 3:** Backfill updates DeepSeek SKU rows by `model_code IN DEEPSEEK_MODEL_PRICING`; anthropic row untouched in `test_recomputes_deepseek_costs_leaves_anthropic_unchanged`.
- **Anthropic isolation:** `TestAnthropicCostComponentsRegression` + `TestAst492BrainSettingDoTask` monkeypatch `get_active_llm_provider` → `anthropic` on the Big-tier regression.
- **Golden math:** `test_pro_utc_day_export_totals_match_pricing_snapshot` / flash counterpart match parent export dollar components at new CPMs.

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| **discuss** | Plan Stage 4 / UAT | `debug/spikes/ast-570-deepseek-export-reconcile/reconcile.py` is **not** on the publish ref (gitignored per orientation). Parent AC **1–3** UTC-day token + dollar checks still need Susan to run backfill + reconcile locally; document the exact `backfill_deepseek_agent_timesheet_costs()` invocation (Python one-liner or script) when reconcile is first green. |
| **discuss** | `tests/component/utils/test_cost_calculator_deepseek.py` | Plan Stage 5 asked per-row anchors (`840f7662…`, `f778a6ce…`); shipped tests use **UTC-day aggregate** token totals instead. Math is still anchored to export; weaker per-`agent_req_id` proof before UAT. |
| **discuss** | `backfill_deepseek_agent_timesheet_costs` | Pass 1 recomputes **calc_cost_* only** (per plan). If Stage 4 reconcile shows **miss/output** column drift vs export, need pass 2 within **AST-570** — do not improvise token rewrites without a documented rule. |
| **advisory** | `src/external/deepseek.py` `if debug:` block | Pre-existing `logger.info("[DEBUG] …")` left unchanged — grandfather per **§1.5.1** / **§5f** (file touched but not migrated to contract helpers). |
| **advisory** | `docs/ASTRAL_TEST_BIBLE.md` | **§7.13zz** manifest is correct for **AST-570**; large bible diff includes rollup notes for sibling tickets — expected Betty publish shape for `rollup-child`. |

### Recommended actions

| Item | Owner | Action |
|------|-------|--------|
| UAT reconcile + backfill command | Ada / Susan | After merge to UAT DB: run `backfill_deepseek_agent_timesheet_costs()`, then gitignored `reconcile.py` (or equivalent SQL) for UTC `2026-06-03` pro + flash; post exact command on **AST-570** when green. |
| Per-row golden tests (optional) | Ada via `resolve-astral` | If Susan wants stronger pre-UAT proof, add tests using parent CSV row token integers for `840f7662…` and `f778a6ce…`. |
| Token pass 2 (conditional) | Ada via `resolve-astral` | Only if reconcile FAIL on miss/output **integers** — follow plan Stage 4 escalation, not cost-only backfill. |

**Verdict:** No **fix-now** on published product code vs approved plan Stages 1–3 and Betty tests. **Review Posted** — engineer may proceed to `resolve-astral` for **discuss** UAT ops only; no code changes required for sign-off unless reconcile fails.

## Resolution (2026-06-03)

**Review tip:** `origin/sub/AST-569/AST-570-deepseek-cost-math-mapping-backfill` @ `7fc6b78d` (Radia doc + Betty tests @ `96aebe5e` product).

**Fix-now:** None — no product commits in resolve pass.

**Discuss (closed for sign-off):**

| Item | Resolution |
|------|------------|
| UAT ops | Backfill + reconcile are Susan UAT steps (gitignored spike). Commands below. |
| Per-row golden tests | Deferred — UTC-day aggregate tests in `test_cost_calculator_deepseek.py` match export dollar math; optional per-`agent_req_id` tests only if Susan requests before UAT. |
| Backfill pass 2 | Conditional — run only if reconcile FAIL on miss/output **integers**; pass 1 (cost-only from stored tokens) is shipped. |

**Susan UAT (parent AC 1–3):**

```bash
# 1. Recompute calc_cost_* for all DeepSeek rows (prod DB path from env or --db)
python3 -c "from src.data.database import backfill_deepseek_agent_timesheet_costs; print(backfill_deepseek_agent_timesheet_costs(), 'rows updated')"

# 2. UTC-day reconcile vs DeepSeek export (gitignored spike; copy export CSV locally)
python3 debug/spikes/ast-570-deepseek-export-reconcile/reconcile.py \
  --export-csv /path/to/deepseek_usage.csv \
  --utc-date 2026-06-03
```

If step 2 FAIL on token integers (not dollars only), stop and escalate per plan Stage 4 — do not rewrite token columns without a documented rule.

**§9a:** publish ref merges cleanly into `origin/dev` and `origin/ftr/ast-569-timesheets-deepseek-cost`.
