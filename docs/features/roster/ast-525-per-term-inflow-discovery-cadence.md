<!-- linear-archive: AST-525 archived 2026-06-15 -->

## Linear archive (AST-525)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-525/per-term-inflow-discovery-cadence-company-search-terms-table-with-per  
**Status at archive:** Done  
**Project:** Astral Roster  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-523 — Company search terms table with per-term last_scan_at (Roster inflow)  
**Blocked by / blocks / related:** parent: AST-523

### Description

## What this implements

Wire roster inflow Phase 1 to the **company_search_terms** table: per-term staleness for dispatch eligibility, CSE only for stale terms, **last_scan_at** bump on successful search, and **COMPANY_SEARCH_TERMS** token resolution from the table.

## Acceptance criteria

4. **COMPANY_SEARCH_TERMS** in prompts matches the table content (newline-joined), not a stale artifact field.
5. **inflow_discovery** runs CSE only for terms whose **last_scan_at** is null or past the configured scan interval; terms searched recently are skipped.
6. After a successful CSE for a term, that term's **last_scan_at** is set; dispatch-task **last_run_at** is not used to decide term staleness.
7. Dispatch shows **inflow_discovery** as available when at least one term is stale (and candidate preconditions pass), even if the dispatch row was run recently for other reasons.

## Boundaries

* No change to vet/ingest beyond term source and timestamps.
* No Artifacts UI changes — **AST-526**.
* No table schema work beyond calling **AST-524** helpers.
* Scan interval from product config (**INFLOW_CONFIG**), not **dispatch_task.freq_hrs** / **last_run_at**.

## Notes for planning

* [**roster.py**](<http://roster.py>) **run_inflow_discovery_batch**, [**database.py**](<http://database.py>) **count_candidate_inflow_discovery_eligible**.
* Remove candidate-level **last_run_at** gating for discovery cadence.

## Git branch (authoritative)

**sub/AST-523/AST-525-per-term-inflow-discovery-cadence**

### Comments

#### chuckles — 2026-06-02T19:34:50.394Z
[check-linear]

Confirmed merged to **`origin/dev`** via **AST-523** / **AST-490** composite merges (**`0cc15621`**, **`803aaa1f`**). Per-term **`last_scan_at`** discovery cadence + **`COMPANY_SEARCH_TERMS`** token overlay on dev. Publish sub branch deleted post-rollup.

**Done** — engineer assignee unchanged (Hedy).

— Chuckles

#### susan — 2026-06-02T17:39:55.693Z
@chuckles Please confirm this ticket is actually done and merged to dev origin, and then set it to Done?

#### chuckles — 2026-05-29T03:40:13.910Z
## prep-uat blocker — fix-now (Hedy)

**prep-uat AST-523** failed at §6 collection on `origin/ftr/AST-523-company-search-terms-table-with-per-term-last-scan-at-roster-inflow`:

```
ImportError: partially initialized module 'src.core.consult' (consult ↔ roster cycle)
```

On ftr, **`roster.py`** still top-level-imports **`consult`** helpers and **`consult.py`** top-level-imports **`roster`**. Same fix as AST-490 UAT hotfix:

- **`roster.py`:** lazy-import consult helpers inside the functions that need them.
- **`consult.py`:** drop top-level `roster`; single lazy `from src.core import roster` at start of `run_consult_task` / `_prep_live_content`.

**Owner:** Hedy — fix on **`dev-hedy`**, publish to **`origin/sub/AST-523/AST-525-per-term-inflow-discovery-cadence`**, then **`resolve-astral AST-525`** → User Testing. Chuckles will re-rollup 525 → ftr after.

**AST-524** stays User Testing — no action on 524.

— Chuckles

#### radia — 2026-05-29T03:11:42.833Z
**Review (Radia)** — `origin/dev...origin/sub/AST-523/AST-525-per-term-inflow-discovery-cadence` (includes AST-524 stack)

### What's solid
- **§2.1:** `INFLOW_CONFIG["discovery"]["scan_interval_hours"]` = 168; eligibility uses `count_stale_company_search_terms`, not `last_run_at` / `freq_hrs`.
- **Discovery batch:** `list_stale_company_search_terms` → CSE per term → `update_company_search_term_last_scan_at` after successful `search_google_cse` (before hit aggregation) — matches parent AC #6.
- **Tokens:** `do_task` + `preview_task_prompt` overlay table-joined `artifacts.company_search_terms`.
- **`company_search_terms_lines(candidate_id)`** retargeted to table (artifact path removed).

### fix-now
- **`src/core/agent.py` (~873):** Function-scoped `from src.core.candidate import company_search_terms_joined_text` with **no** in-code comment. **§1.2 / B1** — add a one-line cycle/lazy-load rationale (same bar as `consult` / `tracker` imports in `do_task`).

### discuss
- **Stack size:** Branch carries full Phase 1 inflow module (`run_inflow_discovery_batch`, `INFLOW_CONFIG`, ingest helpers) if not yet on `origin/dev`. Confirm this is expected carry-forward from **AST-505** rather than accidental sibling scope on the publish ref.

### advisory
(none)

— Radia

#### betty — 2026-05-29T02:41:59.901Z
## QA test manifest (AST-525)

Publish tip: `origin/sub/AST-523/AST-525-per-term-inflow-discovery-cadence` @ `d9aab2ae`

`docs/ASTRAL_TEST_BIBLE.md` shasum on publish ref: `b78c25f7b59b8a00c4f3a64421d16e2f32e23237`

Cumulative publish: merged blocker **AST-524** bible/tests (`38b99081`) before **AST-525** test commit — engineer branch had dropped **AST-524** test tree.

1. `./scripts/testing/run_component_tests.sh tests/component/utils/test_config.py::TestAst525InflowDiscoveryConfig`
2. `./scripts/testing/run_component_tests.sh tests/component/data/database/test_company_search_terms.py::TestAst524CompanySearchTermsTable::test_list_stale_company_search_terms_ordered`
3. `./scripts/testing/run_component_tests.sh tests/component/data/database/test_dispatch_tasks.py::TestAst525InflowDiscoveryEligible`
4. `./scripts/testing/run_component_tests.sh tests/component/core/test_roster.py::TestAst505InflowDiscovery::test_run_batch_no_stale_terms_returns_zero_errors`
5. `./scripts/testing/run_component_tests.sh tests/component/core/test_roster.py::TestAst505InflowDiscovery::test_run_batch_happy_path`
6. `./scripts/testing/run_component_tests.sh tests/component/core/test_roster.py::TestAst505InflowDiscovery::test_run_batch_cse_failure_continues`
7. `./scripts/testing/run_component_tests.sh tests/component/core/test_roster.py::TestAst505InflowDiscovery::test_run_batch_searches_only_stale_terms`
8. `./scripts/testing/run_component_tests.sh tests/component/core/test_candidate.py::TestCompanySearchTermsLines`
9. `./scripts/testing/run_component_tests.sh tests/component/core/test_candidate.py::TestAst525CompanySearchTermsTokenOverlay`

**Blocker smoke (AST-524):** items 2 plus full **AST-524** manifest in bible §7.13zi if any table helper regressions appear during `test-astral`.

**Revised from AST-505:** `TestAst505InflowDiscoveryEligible` removed — eligibility is per-term `last_scan_at` (items 3). Roster batch tests updated for stale-only CSE and `last_scan_at` bump (items 4–7).

— Betty

#### chuckles — 2026-05-29T02:14:23.033Z
## Plan validation — APPROVED

**Verdict:** APPROVED → **Plan Approved**

Per-term staleness, removal of dispatch **last_run_at** gating, and CSE bump only on success match AST-523.

— Chuckles

#### hedy — 2026-05-29T02:12:34.160Z
Plan: [`docs/features/roster/ast-525-per-term-inflow-discovery-cadence.md`](https://github.com/susansomerset/astral/blob/sub/AST-523/AST-525-per-term-inflow-discovery-cadence/docs/features/roster/ast-525-per-term-inflow-discovery-cadence.md)

**Self-Assessment**
- **Scope:** Single-Component — `config`, `database`, `roster`, `candidate`, and `agent` only; retargets inflow discovery eligibility and CSE loop to per-term staleness.
- **Conf:** Medium — staleness SQL copied from `claim_board_search_batch`; token overlay is a small `do_task` hook; build gate on AST-524 table helpers.
- **Risk:** Medium — wrong eligibility could starve or flood discovery; contained to `inflow_discovery` dispatch path.

---

# AST-525 — Per-term inflow discovery cadence

- **Linear:** [AST-525](https://linear.app/astralcareermatch/issue/AST-525/per-term-inflow-discovery-cadence-company-search-terms-table-with-per)
- **Parent (coordination only):** [AST-523](https://linear.app/astralcareermatch/issue/AST-523/company-search-terms-table-with-per-term-last-scan-at-roster-inflow)
- **Publish ref:** `origin/sub/AST-523/AST-525-per-term-inflow-discovery-cadence`
- **Blocked by (build gate):** [AST-524](https://linear.app/astralcareermatch/issue/AST-524/company-search-terms-table-and-sync-company-search-terms-table-with) — table + **`company_search_terms_lines_for_candidate`** / **`sync_*`** / **`update_company_search_term_last_scan_at`** must exist on integration line before build/test.

## Summary

Retarget Phase 1 **`inflow_discovery`** from candidate-level **`dispatch_task.last_run_at`** / **`freq_hrs`** gating to **per-term **`last_scan_at`** staleness** on the **`company_search_terms`** table (AST-524). Discovery runs Google CSE **only for stale terms**, bumps **`last_scan_at`** after each **successful** CSE call, and resolves **`{$COMPANY_SEARCH_TERMS}`** from the table (newline-joined). Dispatch shows **`inflow_discovery`** available when **≥1 stale term** exists (plus existing **`LIVE_PROMPTS`** precondition). Vet/ingest behavior unchanged except term source and timestamps.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | **`INFLOW_CONFIG["discovery"]["scan_interval_hours"]`**; comment on **`COMPANY_SEARCH_TERMS`** token | utils |
| `src/data/database.py` | Rewrite **`count_candidate_inflow_discovery_eligible`**; add **`list_stale_company_search_terms`**; replace **`_candidate_search_term_lines`** with table reads | data |
| `src/core/roster.py` | **`run_inflow_discovery_batch`**: stale terms only + per-term **`last_scan_at`** bump | core |
| `src/core/candidate.py` | Switch **`company_search_terms_lines`** to delegate to table (deprecate artifact path) | core |
| `src/core/agent.py` | Overlay table-joined terms into token-resolution dict before **`resolve_tokens`** | core |
| `src/core/candidate.py` | **`preview_task_prompt`**: same overlay when **`candidate_id`** known | core |

**Tests:** Betty owns **`tests/`** — engineer does **not** edit **`tests/component/data/database/test_dispatch_tasks.py`** or roster tests; post **`[qa-handoff]`** if manifest breaks on intentional behavior change.

## Stage 1: Config — scan interval literal

**Done when:** **`INFLOW_CONFIG["discovery"]["scan_interval_hours"]`** exists (default **168** = 7 days); discovery cadence reads this key, not **`dispatch_task.freq_hrs`**.

1. In **`src/utils/config.py`**, inside **`INFLOW_CONFIG["discovery"]`**, after **`dispatch_freq_hrs`**, add:

   ```python
   "scan_interval_hours": 168,  # per-term last_scan_at staleness (AST-525); not dispatch_task.last_run_at
   ```

2. **Leave **`dispatch_freq_hrs`** in place** for documentation parity with AST-505 plan text but **do not** use it for inflow eligibility after this ticket.

⚠️ **Decision:** **`scan_interval_hours`** matches **`dispatch_freq_hrs` (168)** — same weekly intent, but enforced per **term row**, independent of **`dispatch_task.last_run_at`**.

### Self-review (Stage 1)

| Rule | OK? |
|------|-----|
| §2.1 config | Literal in **`INFLOW_CONFIG`** only |
| §1.4 magic numbers | No inline **168** elsewhere |

---

## Stage 2: Dispatch eligibility — stale term count

**Done when:** **`count_candidate_inflow_discovery_eligible`** returns **1** iff candidate is **`LIVE_PROMPTS`** and **`count_stale_company_search_terms(candidate_id, scan_interval_hours) > 0`**; **`last_run_at`** and **`freq_hrs`** arguments ignored for eligibility (signature may remain for call-site compatibility).

1. In **`src/data/database.py`**, add **`list_stale_company_search_terms(candidate_id: str, scan_interval_hours: float) -> List[str]`**:
   - Return **`search_term`** strings for stale rows (same SQL predicate as **`count_stale_company_search_terms`** from AST-524), ordered **`search_term ASC`**.

2. Replace **`count_candidate_inflow_discovery_eligible`** implementation:

   ```python
   def count_candidate_inflow_discovery_eligible(
       candidate_id: str,
       freq_hrs: float,  # unused — kept for caller compatibility
       last_run_at: Optional[str],  # unused — AST-525
   ) -> int:
   ```

   - Return **0** if **`candidate_id`** blank.
   - Load candidate; **0** if missing or **`state != INFLOW_CONFIG["discovery"]["dispatch_trigger_state"]`**.
   - **`scan_h = float(INFLOW_CONFIG["discovery"]["scan_interval_hours"])`**
   - Return **1** if **`count_stale_company_search_terms(candidate_id, scan_h) > 0`**, else **0**.

3. In **`count_eligible_for_dispatch_task`**, **candidate** branch: stop computing **`eff_freq`** from **`freq_hrs`** / **`dispatch_freq_hrs`** for **`inflow_discovery`** — call **`count_candidate_inflow_discovery_eligible(candidate_id, 0, None)`** (or pass through args; function ignores them).

4. Delete **`_candidate_search_term_lines(candidate_data)`** (artifact mirror). No replacement — eligibility uses **`count_stale_company_search_terms`** directly; no other callers should remain after step 2.

### Self-review (Stage 2)

| Rule | OK? |
|------|-----|
| §2.4 batch | Eligibility mirrors **`claim_board_search_batch`** staleness predicate |
| §3.3 imports | **`database → config`** only |

---

## Stage 3: Discovery batch — CSE per stale term + timestamp bump

**Done when:** **`run_inflow_discovery_batch`** searches only stale terms; after **`search_google_cse`** succeeds for a term (no exception), **`update_company_search_term_last_scan_at(candidate_id, term)`** runs; failed CSE does **not** bump; vet/ingest aggregate unchanged.

1. In **`src/core/roster.py`** **`run_inflow_discovery_batch`**:
   - Import **`list_stale_company_search_terms`**, **`update_company_search_term_last_scan_at`** from **`database`**.
   - Import **`company_search_terms_lines_for_candidate`** from **`candidate`** (AST-524).
   - Replace **`terms = company_search_terms_lines(...)`** with:

     ```python
     scan_h = float(INFLOW_CONFIG["discovery"]["scan_interval_hours"])
     terms = list_stale_company_search_terms(candidate_id, scan_h)
     ```

   - If **`not terms`**: log warning **`no stale search terms`**; return **`{**zero, "total_errors": 0}`** (not an error — nothing to do).

2. Inside **`for term in terms:`** loop, **after** successful **`search_google_cse`** (after **`hits = search_google_cse(...)`** returns, before iterating hits):

   ```python
   update_company_search_term_last_scan_at(candidate_id, term)
   ```

   - On **`except (RuntimeError, ValueError)`** for CSE: **do not** bump; increment **`errors`** (existing behavior).

3. **Do not** change vet task aggregation (still one vet call per batch over combined hits from all **stale** terms searched this run).

⚠️ **Decision:** **`last_scan_at`** advances on **successful CSE HTTP/search**, not after vet/ingest — matches parent AC #6 wording (“After a successful CSE for a term”).

### Self-review (Stage 3)

| Rule | OK? |
|------|-----|
| §2.5 bright line | CSE stays **`external`**; roster orchestrates |
| §1.3 DRY | Reuses AST-524 bump helper |

---

## Stage 4: Term list helpers + token overlay

**Done when:** **`company_search_terms_lines(candidate_data)`** reads table via **`candidate_id`** from caller context; **`{$COMPANY_SEARCH_TERMS}`** resolves to newline-joined **table** text in **`do_task`** and **`preview_task_prompt`**.

1. In **`src/core/candidate.py`**, change **`company_search_terms_lines(candidate_data: dict) -> list[str]`**:
   - **Remove** artifact read path.
   - **Cannot** get **`candidate_id`** from **`candidate_data`** alone reliably — add required param:

     **`company_search_terms_lines(candidate_id: str) -> list[str]`** returning **`company_search_terms_lines_for_candidate(candidate_id)`** (AST-524 function).

   - Update **`src/core/roster.py`** call at line ~304 to pass **`candidate_id`**.

2. **`company_search_terms_joined_text(candidate_id)`** — use for token overlay (AST-524).

3. In **`src/core/agent.py`** **`do_task`**, immediately after **`cd = (ctx.get("candidate_data") or {}) if ctx else ...`** and **`candidate_id = ctx.get("astral_candidate_id") if ctx else None`**:

   ```python
   if candidate_id:
       from src.core.candidate import company_search_terms_joined_text
       joined = company_search_terms_joined_text(candidate_id)
       cd = dict(cd)
       arts = dict(cd.get("artifacts") or {})
       arts["company_search_terms"] = joined
       cd["artifacts"] = arts
   ```

   - Overlay applies to all **`resolve_tokens(..., cd, ...)`** calls in **`do_task`** (read-through for **`TOKEN_SOURCES`** path — no **`config.py`** change required).

4. In **`src/core/candidate.py`** **`preview_task_prompt`**, after loading **`candidate`** dict and building **`cd = candidate.get("candidate_data") or {}`**:

   ```python
   joined = company_search_terms_joined_text(candidate_id)
   cd = dict(cd)
   arts = dict(cd.get("artifacts") or {})
   arts["company_search_terms"] = joined
   cd["artifacts"] = arts
   ```

5. In **`src/utils/config.py`**, update comment on **`COMPANY_SEARCH_TERMS`**: `# Resolved from company_search_terms table via agent overlay (AST-525); path kept for registry.`

### Self-review (Stage 4)

| Rule | OK? |
|------|-----|
| §3.3 imports | Overlay in **`core/agent`** and **`core/candidate`** — not **`utils → data`** |
| §2.1 config | Token registry unchanged structurally |

---

## Execution contract (developer agent)

Execute stages **1 → 4** in order. **Requires AST-524 merged on `dev-hedy`** (or cherry-picked) before Stage 2. One commit per stage on **`dev-hedy`**; cherry-pick to **`origin/sub/AST-523/AST-525-per-term-inflow-discovery-cadence`**. Do **not** change Artifacts UI (**AST-526**). If tests assert artifact-based eligibility or **`last_run_at`** gating, **`[qa-handoff]`** to Betty — do **not** patch tests locally.

## Self-Assessment

**Scope:** `Single-Component` — **`config`**, **`database`**, **`roster`**, **`candidate`**, **`agent`** only; no UI or new tables.

**Conf:** `Medium` — Staleness predicate copied from **`board_search`** / **`claim_board_search_batch`**; token overlay is a small **`do_task`** hook; signature change on **`company_search_terms_lines`** needs call-site grep.

**Risk:** `Medium` — Wrong eligibility logic starves or floods discovery runs; mitigated by mirroring proven **`last_scan_at`** SQL and scoped to **`inflow_discovery`** task only.

## Self-review vs ASTRAL_CODE_RULES

| Section | Assessment |
|---------|------------|
| §1.3 DRY | Reuses AST-524 table helpers; no duplicate staleness SQL |
| §2.1 config | **`scan_interval_hours`** in **`INFLOW_CONFIG`** |
| §2.4 batch | Candidate dispatch still one entity per run; term cadence inside batch |
| §2.6 state machine | No new transitions |
| §3.3 imports | Respected |
| §3.5 naming | Existing function names extended, not renamed gratuitously |

## Review

- **Branch:** `origin/sub/AST-523/AST-525-per-term-inflow-discovery-cadence`
- **Built:** 2026-05-28 — stages 1–4 on `dev-hedy`; Betty manifest pending.

## Resolution

- **2026-05-28 (Radia review):** **fix-now:** Added lazy-import rationale comment on `company_search_terms_joined_text` in `do_task` (`src/core/agent.py`) per §1.2 / B1 (matches `persist_job_artifact_from_parsed` / tracker pattern).
- **Discuss:** Publish ref carries full Phase 1 inflow module (`run_inflow_discovery_batch`, `INFLOW_CONFIG`, ingest helpers) — expected carry-forward from **AST-505** build on this epic stack, not accidental sibling scope.
- **Outcome:** One product commit + this Resolution section on publish ref `origin/sub/AST-523/AST-525-per-term-inflow-discovery-cadence`.
