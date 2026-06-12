export const CALC_COST_KEYS = [
  "calc_cost_cache_write",
  "calc_cost_cache_read",
  "calc_cost_no_cache_input",
  "calc_cost_output",
] as const

export function sumCalcCostComponents(row: Record<string, unknown>): number {
  return CALC_COST_KEYS.reduce((s, k) => s + (Number(row[k]) || 0), 0)
}

export function rowTotalCost(row: Record<string, unknown>): number {
  const t = row.total_cost
  return typeof t === "number" && !Number.isNaN(t) ? t : sumCalcCostComponents(row)
}
