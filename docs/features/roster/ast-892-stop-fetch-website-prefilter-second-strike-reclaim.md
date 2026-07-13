# AST-892 — Stop fetch_website reclaim of prefilter second-strike companies

- **Linear:** [AST-892 — Stop fetch_website reclaim of prefilter second-strike companies (fetch_website infinite loop)](https://linear.app/astralcareermatch/issue/AST-892/stop-fetch-website-reclaim-of-prefilter-second-strike-companies-fetch)
- **Parent:** [AST-889 — fetch_website infinite loop](https://linear.app/astralcareermatch/issue/AST-889/fetch-website-infinite-loop)
- **Publish ref:** `origin/sub/AST-889/AST-892-stop-fetch-website-prefilter-second-strike-reclaim`

`fetch_website` and `prefilter` both companion-claim `WEBSITE_FOUND_RETRY`, but they own different subsets: scrape-retry (no usable `homepage_text`) vs prefilter second strike (homepage already scraped). AST-882 correctly **skips** the second-strike subset inside `fetch_website_batch` without state change; the dispatcher still **claims and counts** those rows every iteration (`available` never drains, `total_processed` keeps climbing with zero pass/fail). This ticket closes that ownership hole at claim/count time so second-strike companies stay eligible for prefilter only, real scrape-retry work still runs under `fetch_website`, and a batch composed solely of already-scraped second-strike companies finishes in a finite number of iterations.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Helper returning `(retry_state, homepage_text_key)` used by claim/count exclusion; brief comment on dual ownership of `WEBSITE_FOUND_RETRY` | utils |
| `src/data/database.py` | Optional claim/count filter excluding `retry_state` rows with non-empty `homepage_text`; wire into `set_company_batch` / `claim_company_batch` / `count_eligible_for_dispatch_task` | data |
| `src/core/roster.py` | Pass-through kwarg on `get_new_company_batch` → `claim_company_batch` | core |
| `src/core/dispatcher.py` | When `task_key == "fetch_website"`, pass the exclude flag into `get_new_company_batch` (mirrors `require_empty_website` for resolve) | core |
| `src/core/gazer.py` | Keep AST-882 skip as defense-in-depth; count skips separately; return `total` that does **not** treat skips as processed work (so even a race cannot inflate loop counters unboundedly); keep §1.5.1 skip vs scrape `debug_index` outcomes | core |
| `src/core/consult.py` | Map `fetch_website_batch` return so `total_processed` excludes intentional second-strike skips (use returned `total`, which will already exclude skips after gazer change) | core |

**Verify only (Betty / qa-child — engineer does not edit in build-child):**

| File | Change |
|------|--------|
| `tests/component/data/database/…` (or existing company-batch claim tests) | Claim + count for a `fetch_website` / `WEBSITE_FOUND` row do **not** include `WEBSITE_FOUND_RETRY` + non-empty `homepage_text`; bare `WEBSITE_FOUND_RETRY` without homepage text still counts/claims; `prefilter` / `HOMEPAGE_READY` claim of the same second-strike row is unchanged |
| `tests/component/core/test_gazer.py` | Existing AST-882 skip test still holds; assert skip does not increment `passed`/`failed`/`errors` and returned `total` equals work actually attempted (passed+failed+errors), not skip count |
| `tests/component/core/test_consult.py` (or dispatcher loop coverage if present) | A company-only second-strike claim set does not keep accumulating `total_processed` across infinite iterations — finite stop |

**Out of scope:** new company states; redesign of prefilter grading / evaluate destinations; AST-850/854 infra-vs-site fail classification; job gazer paths; dispatch admin UI; one-time migration of historically stuck rows beyond making them claimable by prefilter again (eligibility fix is sufficient).

---

## Stage 1: Config helper — dual ownership of `WEBSITE_FOUND_RETRY`

**Done when:** Callers can read `(retry_state, homepage_text_key)` from one config helper without hardcoding those strings in `database.py` / `dispatcher.py`. A short comment near `COMPANY_STATES["WEBSITE_FOUND_RETRY"]` or `GAZER_CONFIG["fetch_website"]` documents that the same state is shared: empty/missing `homepage_text` → `fetch_website` scrape retry; non-empty `homepage_text` → prefilter second strike.

1. In `src/utils/config.py`, add:

   ```python
   def fetch_website_prefilter_second_strike_filter() -> tuple[str, str]:
       """(retry_state, homepage_text_company_data_key) for AST-892 claim/count exclusion.

       ``WEBSITE_FOUND_RETRY`` is shared: rows with non-empty homepage_text are owned by
       prefilter second strike; rows without are owned by fetch_website infra retry.
       """
       return (
           GAZER_CONFIG["fetch_website"]["retry_state"],
           ROSTER_CONFIG["company_data_keys"]["homepage_text"],
       )
   ```

   Place it next to `dispatch_claim_states` (same dispatch-eligibility family). Do **not** change `dispatch_claim_states` itself — both tasks still list `WEBSITE_FOUND_RETRY` in claim states; exclusion is data-key based, not state-list based.

2. Add a one-line comment on `GAZER_CONFIG["fetch_website"]["retry_state"]` (or the `WEBSITE_FOUND_RETRY` company state entry) pointing at AST-892 dual ownership. No new config keys, no new states.

⚠️ **Decision:** Do not remove `WEBSITE_FOUND_RETRY` from `dispatch_claim_states("WEBSITE_FOUND", "company")`. Bare WFR without homepage_text must stay claimable by `fetch_website` for AST-854 infra retry. Subset ownership is enforced with a `company_data.homepage_text` filter (same pattern as `score_floor` / inflow blurb JSON filters), not by inventing a parallel holding state.

---

## Stage 2: Claim + count exclude second-strike rows for `fetch_website`

**Done when:** With `exclude_prefilter_second_strike=True`, `set_company_batch` / `claim_company_batch` never lock a company whose `state` equals the fetch_website `retry_state` and whose `company_data.homepage_text` is non-empty after trim. `count_eligible_for_dispatch_task` for a `fetch_website` row uses the **same** predicate so `available` drains when only second-strike rows remain. `prefilter` counts/claims are unchanged (no flag).

1. In `src/data/database.py`, extend `set_company_batch` and `claim_company_batch` with keyword-only:

   ```python
   exclude_prefilter_second_strike: bool = False,
   ```

   When `clear=False` and `exclude_prefilter_second_strike` is True, after the existing `score_floor` clause, append:

   ```sql
   AND NOT (
     state = ?
     AND json_extract(company_data, '$.<homepage_text_key>') IS NOT NULL
     AND TRIM(json_extract(company_data, '$.<homepage_text_key>')) != ''
   )
   ```

   Bind `retry_state` and resolve `<homepage_text_key>` via `fetch_website_prefilter_second_strike_filter()` from config (import at use site in the claim path — same style as `ROSTER_CONFIG["company_data_keys"]["prefilter_score"]` for `score_floor`). Do not log from the data layer.

2. Update `claim_company_batch` to pass the new kwarg through to `set_company_batch`.

3. In `count_eligible_for_dispatch_task`, in the `entity_type == "company"` branch, after the existing resolve/vet/score_floor special cases and **before** the generic `count_entities_in_state` path:

   - If `(task.get("task_key") or "").strip() == "fetch_website"`: count unclaimed companies for `candidate_id` in `claim_states` **with the same NOT homepage_text predicate** as step 1.
   - Implement as a small private helper next to the other company count helpers (e.g. `count_companies_eligible_for_fetch_website(candidate_id, states)`) so claim SQL and count SQL stay visually twin — copy the exclusion fragment, do not invent a different emptiness rule.

⚠️ **Decision:** Apply the exclude flag only for `task_key == "fetch_website"` at the dispatcher/count call sites — not for every company claim globally. Prefilter must continue claiming `WEBSITE_FOUND_RETRY` + homepage_text for the second strike (AST-881 / AST-882).

4. Do not change `require_empty_website` or score_floor behavior.

---

## Stage 3: Wire dispatcher + core claim pass-through

**Done when:** A `fetch_website` dispatch run claims zero second-strike companies; `available` for that task drops to 0 when the pool is only second-strike rows (loop stops on `available < effective_min`). Companies that still need a scrape (`WEBSITE_FOUND`, or `WEBSITE_FOUND_RETRY` without homepage_text) still claim and run.

1. In `src/core/roster.py` `get_new_company_batch`, add `exclude_prefilter_second_strike: bool = False` and pass it to `claim_company_batch`.

2. In `src/core/dispatcher.py` `_run_unified` company branch, when calling `get_new_company_batch`, set:

   ```python
   exclude_prefilter_second_strike=(dispatch_task_key == "fetch_website"),
   ```

   Keep `require_empty_website=(task.get("task_key") == resolve_key)` as today. Do not special-case other task keys.

3. No change to `dispatch_claim_states` call — still `["WEBSITE_FOUND", "WEBSITE_FOUND_RETRY"]` for the fetch_website primary row.

---

## Stage 4: Gazer skip accounting + debug contract (defense in depth)

**Done when:** If a second-strike company is somehow still in the claimed batch (race / stale row), `fetch_website_batch` still skips without state change (AST-882), emits the existing §1.5.1 skip `debug_index` when `debug=True`, and the batch return does **not** count that skip toward `total` / loop `total_processed`. Scrape / fail / retry paths and their debug outcomes are unchanged.

1. In `src/core/gazer.py` `fetch_website_batch`, keep the AST-882 early return when `company_state == cfg["retry_state"]` and trimmed `homepage_text` is non-empty. Introduce a `skipped` counter incremented on that path (and any future intentional no-op leave-alone paths you do **not** invent here — only this one).

2. Change the return dict so:

   ```python
   work_total = passed + failed + errors  # excludes skipped
   return {
       "passed": passed,
       "failed": failed,
       "errors": errors,
       "skipped": skipped,
       "total": work_total,
   }
   ```

   ⚠️ **Decision:** `consult.run_batch` already does `total = r.get("total", len(entities))` then `total_processed: total`. Returning work-only `total` stops the dispatch loop after a pure-skip iteration (`total_processed == 0` → loop break at `dispatcher._run_dispatch_loop`) even if claim ever races. Primary fix remains Stage 2–3 eligibility; this is the safety belt for AC4.

3. Keep skip `debug_index` outcome string exactly:
   `skip — homepage_text present; leave for prefilter second strike`
   (already matches production repro logs). For scrape pass/fail paths keep existing outcome shapes. Do not emit new debug lines when `debug=False`.

4. In `src/core/consult.py` `fetch_website` branch: keep using `r.get("total", …)` for `total_processed`. No need to special-case `skipped` unless `total` is missing — Stage 4 step 2 makes `total` authoritative. Do not change other task_key branches.

5. Docstring on `fetch_website_batch`: note that `total` is work attempted (excludes intentional second-strike skips) and that claim-time exclusion (AST-892) is the primary ownership fix.

---

## Execution contract

The plan is binding. Execute stages in order; one commit per stage on the epic worktree; publish each stage to `origin/sub/AST-889/AST-892-stop-fetch-website-prefilter-second-strike-reclaim`. Do not add files outside the table. If claim SQL emptiness rules conflict with another in-flight filter, or if `count_eligible` and `set_company_batch` diverge on the predicate, stop and comment on the **parent** (AST-889) with the Stage N blocked template.

Linear blocker format:

```
🛑 Stage N blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

---

## Self-Assessment

**Scope:** Single-Component — claim/count eligibility for one company gazer task (`fetch_website`) plus a small defense-in-depth tally in `fetch_website_batch`; no new states, no UI, no prefilter grade redesign.

**Conf:** high — production logs already name the skip path; AST-882 left claim ownership wrong by design note; existing `score_floor` / `require_empty_website` / inflow JSON filters show the exact data-layer pattern to copy.

**Risk:** Medium — a wrong emptiness predicate could hide real infra-retry companies from `fetch_website` or (if mis-wired onto prefilter) starve second strike; mitigated by task_key-scoped flag and twin claim/count SQL.

---

## Self-review vs ASTRAL_CODE_RULES

| Rule | Check |
|------|--------|
| §1.3 DRY | Single helper for `(retry_state, homepage_text_key)`; one SQL fragment shape shared by claim + count |
| §1.4 / §2.1 config | No hardcoded state/key strings in data/core — read via helper + existing `GAZER_CONFIG` / `ROSTER_CONFIG` |
| §2.4 batch | Claim still batch_id-first via existing `claim_company_batch` / `get_new_company_batch`; no select-by-state without claim |
| §2.6 state machine | No new states; second-strike rows stay in `WEBSITE_FOUND_RETRY` for prefilter |
| §1.5.1 debug | Skip vs scrape outcomes only when `debug=True`; style D index headers retained |
| §3.3 imports | Data reads config only; core still owns transitions; no UI |
| §3.5 naming | `exclude_prefilter_second_strike` names the product subset, not a vague `filter_ready` |

---

## Review (build stub)

**Publish ref:** `origin/sub/AST-889/AST-892-stop-fetch-website-prefilter-second-strike-reclaim`

| Stage | Commit | Summary |
|-------|--------|---------|
| plan | `95e25f4` | Plan doc |
| 1 | `0e47c62` | Config helper + dual-ownership comments |
| 2 | `11388d0` | Claim/count exclude WFR + homepage_text |
| 3 | `3c8ccec` | Dispatcher + roster wire for fetch_website |
| 4 | `fa119e7` | Skip tally; work-only `total` from fetch_website_batch |

**Tip:** `fa119e7`
