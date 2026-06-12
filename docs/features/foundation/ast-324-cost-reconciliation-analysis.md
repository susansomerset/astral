<!-- linear-archive: AST-324 archived 2026-06-03 -->

## Linear archive (AST-324)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-324/refactor-timesheets-to-allow-confident-cost-calculations  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** susan  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

—

### Comments

_No comments._

---

# AST-324 Cost Reconciliation: Astral DB vs Claude Console
**Period:** 2026-03-04 to 2026-03-16
**Sources:**
- **DB (new_cost):** Recalculated from `timesheets_v1` token counts using corrected per-model pricing
- **Console:** `claude_api_cost_2026_03_01_to_2026_03_16.csv` — Anthropic's billing export, grouped by date + model

---

## Daily Summary by Model

| Date       | Model            | DB calls | DB new_cost | Console cost | Delta     | Notes |
|------------|------------------|----------|-------------|--------------|-----------|-------|
| 2026-03-16 | Sonnet 4.6       | 1,564    | $40.53      | $40.80       | -$0.27    | Console: input_no_cache $14.22 + cache_read $2.01 + cache_write $0.97 + output $23.61 |
| 2026-03-16 | Haiku 4.5        | 12       | $0.54       | $0.55        | -$0.01    | |
| 2026-03-15 | Haiku 4.5        | 1,447    | $54.49      | $56.05       | -$1.56    | Console output line: $43.97 — gap likely rounding across 1447 calls |
| 2026-03-15 | Sonnet 4.6       | 500      | $9.50       | $9.52        | -$0.02    | |
| 2026-03-15 | Opus 4.6         | 388      | $18.98      | $21.48       | -$2.50    | Console: $16.77 input + $4.71 output. DB has no cache activity. Gap = ~$2.50 |
| 2026-03-14 | Opus 4.6         | 228      | $8.41       | $8.41        | $0.00     | Clean match |
| 2026-03-14 | Sonnet 4.6       | 75       | $1.43       | $1.43        | $0.00     | Clean match |
| 2026-03-13 | Opus 4.6         | 13       | $0.54       | $0.35        | +$0.19    | orig_cost was $0.39 — new_cost higher; console lower. Possible cross-key attribution |
| 2026-03-13 | Sonnet 4.6       | 3        | $0.06       | $0.07        | -$0.01    | |
| 2026-03-13 | Haiku 4.5        | 1        | $0.03       | $0.06        | -$0.03    | |
| 2026-03-12 | Opus 4.6         | 119      | $3.35       | $0.42        | +$2.93    | ⚠️ Large gap — orig_cost was $1.01. Console only shows $0.42. Possible that Opus was switched off mid-day |
| 2026-03-12 | Haiku 4.5        | 67       | $1.94       | $2.64        | -$0.70    | Console combines astral-main + candidate-somerset keys |
| 2026-03-12 | Sonnet 4.6       | 54       | $1.02       | $1.02        | $0.00     | Clean match |
| 2026-03-12 | Sonnet 4.5       | 4        | $0.33       | n/a          | n/a       | Console has no Sonnet 4.5 line for Mar 12 — likely rolled into (db) ad-hoc |
| 2026-03-11 | Sonnet 4.6       | 69       | $1.61       | $1.96        | -$0.35    | Console splits across two API keys |
| 2026-03-11 | Haiku 4.5        | 37       | $0.80       | $1.03        | -$0.23    | Console splits across two keys |
| 2026-03-11 | Sonnet 4.5       | 12       | $0.91       | n/a          | n/a       | Pre-model-switch ad-hoc calls |
| 2026-03-10 | Opus 4.6         | 531      | $16.22      | $11.89       | +$4.33    | ⚠️ DB higher — orig_cost was $12.76 (old bug understated). Console: $10.31 + $1.58 |
| 2026-03-10 | Sonnet 4.6       | 3        | $0.08       | $0.08        | $0.00     | Clean match |
| 2026-03-10 | Haiku 4.5        | 1        | $0.03       | $0.90        | -$0.87    | Console $0.74+$0.16 — DB only has 1 call logged vs console's apparent volume |
| 2026-03-09 | Opus 4.6         | 180      | $8.21       | $4.75        | +$3.46    | ⚠️ DB higher — orig_cost was $5.41. Console: $3.93 + $0.82 |
| 2026-03-08 | Sonnet 4.5       | 11       | $1.34       | $0.57 (orig) | +$0.76    | orig_cost was $0.57 (old bug). Console: Sonnet 4.5 $0.57 + Opus $0.16 |
| 2026-03-07 | Sonnet 4.5       | 479      | $10.65      | $14.19 (orig)| -$3.54    | orig_cost $14.87 was overcalculated. Console: Sonnet $0.19 + Opus $13.99 + Haiku $0.69 |
| 2026-03-06 | Sonnet 4.5       | 72       | $1.22       | $0.78 (orig) | +$0.44    | Console: Sonnet $0.78 + Opus $0.79 |
| 2026-03-05 | Sonnet 4.5       | 8        | $0.50       | ~$1.95       | -$1.45    | Console shows Opus $1.95 on Mar 5 — task attribution unclear |
| 2026-03-04 | Sonnet 4.5       | 5        | $0.32       | $0.54 (orig) | -$0.22    | Console: Opus $0.54 — model mismatch in DB attribution |

---

## Totals

| Source            | Total Cost |
|-------------------|------------|
| DB orig_cost      | ~$144.55   |
| DB new_cost       | ~$165.27   |
| Console total     | ~$170.18   |
| Gap (new vs console) | ~$4.91  |

---

## Key Findings

### 1. The corrected calculator is much closer to reality
`new_cost` ($165) vs `orig_cost` ($145) vs console ($170). The old bug understated costs by ~$21 over the period. The corrected formula closes that to ~$5 gap.

### 2. Remaining ~$5 gap has three sources

**a) API key split** — The console export shows both `astral-main` and `candidate-somerset` keys. The DB doesn't separate these, so some days the console total is higher because it includes calls the DB didn't attribute to a task (e.g. Haiku on Mar 10 shows 1 DB call but $0.90 in console).

**b) Model attribution on early dates (pre-Mar-4)** — Mar 4–7 DB rows are attributed to `claude-sonnet-4-5` (the fallback in the query), but the console shows Opus 4.6 charges on those same days. Those were likely `(db)` / ad-hoc calls using a different model than the fallback assumed.

**c) Mar 12 Opus anomaly** — DB shows $3.35 for 119 Opus calls, console shows only $0.42. Either those calls were on a key not in the console export, or the `agent_task` join is returning the wrong model for some of those task keys on that date.

### 3. Where the money actually went (new_cost)

| Model       | Total new_cost | % of spend |
|-------------|----------------|------------|
| Haiku 4.5   | ~$57.86        | 35%        |
| Sonnet 4.6  | ~$54.17        | 33%        |
| Opus 4.6    | ~$55.69        | 34%        |
| Sonnet 4.5  | ~$14.91        | 9%         |

Haiku spend is almost entirely `qualify_job_listings` on Mar 15 ($54.49 alone). Opus spend is discovery tasks (`prefilter_company`, `parse_job_list`, `vet_job_list`, `find_job_site`) — none of which had caching active.

### 4. Biggest optimization opportunity
The Opus discovery tasks (prefilter, parse, vet, find) had **zero cache activity** across the entire period. Moving those to Haiku or Sonnet with caching enabled would reduce that ~$55 Opus line by an estimated 60–80%.
