# Cost Calculator Deepseek

**Test module:** `tests/component/utils/test_cost_calculator_deepseek.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/utils/cost_calculator.py` (DeepSeek catalog SKUs) | `tests/component/utils/test_cost_calculator_deepseek.py` | no |

### AST-1880 · AST-1851

The DeepSeek-named wrappers (`deepseek_usage_to_token_counts`, `calculate_cost_components_deepseek_from_counts`, `calculate_cost_components_deepseek`) are deleted. The AST-570 pricing snapshots now run through `calculate_cost_components_from_counts(..., sku=, server_id="deepseek")` (**`TestDeepseekCatalogCostSnapshots`**), and `test_deepseek_named_wrappers_are_gone` asserts that the symbols are absent. Bucket mapping lives in `test_cost_calculator.py::TestAst1877CatalogPricing` (`usage_to_token_counts`); `test_legacy_deepseek_name_delegates_to_catalog` has been retired. Manifest: [`../ui/api/api_admin.md`](../ui/api/api_admin.md) § AST-1880.
