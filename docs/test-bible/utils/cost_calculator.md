# Cost Calculator

**Test module:** `tests/component/utils/test_cost_calculator.py`

_(Coverage map and manifest blocks appended by Betty `qa-child`.)_

### AST-1877 · AST-1851 (pricing via model catalog)

**Primary manifest:** **`docs/test-bible/utils/config.md`** § AST-1877.

| Area | Source | Component tests |
| --- | --- | --- |
| Catalog pricing (`get_sku_pricing`), generic buckets + cost-from-counts, legacy DeepSeek name delegates, unpriced SKU raises | `src/utils/cost_calculator.py` | `TestAst1877CatalogPricing` |
| Legacy DeepSeek / Anthropic numbers unchanged | `src/utils/cost_calculator.py` | `tests/component/utils/test_cost_calculator_deepseek.py` (unchanged) |

### AST-1955 · AST-1953 (per-SKU model ids)

**Primary manifest:** [`config.md`](config.md) § AST-1955. No `cost_calculator.py` change.

| Area | Source | Component tests |
| --- | --- | --- |
| Revised — Haiku pricing read from `LLM_MODEL_CONFIG["claude-haiku-4-5"]` (the `claude` model id is gone) | catalog | `TestAst1877CatalogPricing::test_anthropic_alias_costs_read_catalog_pricing` |

### AST-2098 · AST-2099 (hollow response — no usage object)

**Primary manifest:** [`../core/dispatcher.md`](../core/dispatcher.md) § AST-2098.

| Area | Source | Component tests |
| --- | --- | --- |
| New — `usage_to_token_counts(None)` → all four buckets `0`, no exception | `src/utils/cost_calculator.py` | `TestAst2098UsageNone::test_usage_none_reads_zero_tokens` |
