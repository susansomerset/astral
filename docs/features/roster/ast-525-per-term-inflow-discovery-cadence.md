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
