# Cost Calculator

**Test module:** `tests/component/utils/test_cost_calculator.py`

_(Coverage map and manifest blocks appended by Betty `qa-child`.)_

### AST-1877 · AST-1851 (pricing via model catalog)

**Primary manifest:** **`docs/test-bible/utils/config.md`** § AST-1877.

| Area | Source | Component tests |
| --- | --- | --- |
| Catalog pricing (`get_sku_pricing`), generic buckets + cost-from-counts, legacy DeepSeek name delegates, unpriced SKU raises | `src/utils/cost_calculator.py` | `TestAst1877CatalogPricing` |
| Legacy DeepSeek / Anthropic numbers unchanged | `src/utils/cost_calculator.py` | `tests/component/utils/test_cost_calculator_deepseek.py` (unchanged) |
