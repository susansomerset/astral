# Hold entity state on provider balance refusal

**Linear:** [AST-897](https://linear.app/astralcareermatch/issue/AST-897/hold-entity-state-on-provider-balance-refusal-in-the-event-of)  
**Parent:** [AST-896](https://linear.app/astralcareermatch/issue/AST-896/in-the-event-of-insufficient-balance-do-not-transition-state)  
**Publish ref:** `origin/sub/AST-896/AST-897-hold-entity-state-balance-refusal`

When an LLM provider refuses a call for insufficient balance / credit (HTTP 402 and equivalent credit-exhausted messages), jobs and companies must stay in their current loop-eligible state so dispatch can retry after credit is restored. Failure recording (ledger, agent_data, error return) stays; only the **state transition** is withheld. Other failure classes keep today’s error/retry routing.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `PROVIDER_BALANCE_REFUSAL` config block (failure_class string, HTTP status codes, message substrings) | utils |
| `src/utils/llm_external.py` | Add classify + `is_provider_balance_refusal` helpers (shared by both providers + core) | utils |
| `src/external/anthropic.py` | On caught provider exception, set `failure_class` when balance/credit refusal | external |
| `src/external/deepseek.py` | Same tagging on caught provider exception | external |
| `src/core/agent.py` | On provider failure return path with `debug=True`, emit hold/classify detail when tagged | core |
| `src/core/consult.py` | Gate error/retry transitions after `do_task` failure when tagged (single + batch + analysis_upshot) | core |
| `src/core/roster.py` | Gate prefilter fail routing + `select_job_page` SELECT_FAILED `_save_company` path when tagged | core |

## Execution contract

The plan is binding. Execute stages in order. Do not add files outside the table. On ambiguity or codebase drift, stop and comment on **AST-896** with the 🛑 Stage format from plan-child.

---

## Stage 1: Config + shared classification helpers

**Done when:** `PROVIDER_BALANCE_REFUSAL` is readable from config; `classify_provider_balance_refusal` and `is_provider_balance_refusal` exist in `llm_external.py` and unit-callable without hitting the network.

1. In `src/utils/config.py`, near `LLM_PROVIDER_CONFIG` (after that block / before related helpers), add:

```python
# PROVIDER_BALANCE_REFUSAL — LLM billing/credit exhaustion (AST-897).
# Used by utils.llm_external classifiers and core state-hold gates.
PROVIDER_BALANCE_REFUSAL = {
    "failure_class": "provider_balance_refusal",
    "http_status_codes": (402,),
    "message_substrings": (
        "insufficient balance",
        "insufficient credit",
        "credit exhausted",
        "out of credit",
        "payment required",
    ),
}
```

Update the file header inventory comment to mention `PROVIDER_BALANCE_REFUSAL`.

⚠️ **Decision:** Match on HTTP 402 **or** case-insensitive substring in the exception/error text (Susan’s original shape is `402` + `Insufficient Balance`). Do **not** treat 429 / timeouts / schema errors as balance refusals. Substrings live in config (§1.4 / §2.1) — no inline magic sets in classifiers.

2. In `src/utils/llm_external.py`, import `PROVIDER_BALANCE_REFUSAL` from config and add:

- `classify_provider_balance_refusal(exc: BaseException) -> Optional[str]`  
  - Read `status_code` from `getattr(exc, "status_code", None)` first; if missing, try `getattr(getattr(exc, "response", None), "status_code", None)`.  
  - If status is in `PROVIDER_BALANCE_REFUSAL["http_status_codes"]`, return `PROVIDER_BALANCE_REFUSAL["failure_class"]`.  
  - Else lower-case `str(exc)` and, if any substring from `message_substrings` is present, return the same `failure_class`.  
  - Else return `None`.

- `is_provider_balance_refusal(result: Optional[Dict[str, Any]]) -> bool`  
  - `True` iff `result` is a dict and `result.get("failure_class") == PROVIDER_BALANCE_REFUSAL["failure_class"]`.

⚠️ **Decision:** Put helpers in `llm_external.py` (existing shared Anthropic/DeepSeek utils from AST-687) rather than a new module — keeps §3.3 / DRY aligned with prior provider shared-helper work. Classification strings come only from config.

---

## Stage 2: Tag balance refusals in external + debug detail in `do_task`

**Done when:** `send_to_anthropic` / `send_to_deepseek` failure returns include `failure_class` for balance refusals; `do_task` still returns `success=False` with existing audit/ledger behavior and, when `debug=True`, logs that the refusal was classified as balance/credit.

1. In `src/external/anthropic.py`, in **both** `except Exception as e` paths that return `{"success": False, ... "error": str(e)}` (inner API-call catch and outer catch), after building the error string:

```python
from src.utils.llm_external import classify_provider_balance_refusal  # top-level import preferred if no cycle

out = {"success": False, "api_response": None, "timesheet": _empty_timesheet(), "error": str(e)}
fc = classify_provider_balance_refusal(e)
if fc:
    out["failure_class"] = fc
return out
```

Do **not** change parse-failure returns (those already have `api_response` and are not balance refusals).

2. In `src/external/deepseek.py`, apply the identical tagging on both `except Exception as e` failure returns.

3. In `src/core/agent.py`, on the existing `if not result.get("success"):` provider-failure path (before `_close_hop_ledger` / `return result`), when `debug=True` and `is_provider_balance_refusal(result)`:

- Emit a `debug_detail` line:  
  `provider_balance_refusal failure_class=<…> error=<…>`  
  (use `_do_task_debug_logger(debug)`).  
- Do **not** transition state inside `do_task` for balance refusals (callers own entity transitions).  
- Leave `_apply_dispatch_chain_hop_failure` as-is: it only hard-transitions on “Job not found” / “Missing candidate_data”; provider balance refusals already stay retryable there.

⚠️ **Decision:** Tag at the external boundary (exception still available) and pass `failure_class` through the existing result dict. Do not invent a new exception type for core to catch — both providers already swallow exceptions into `success=False` dicts.

---

## Stage 3: Consult — withhold job transitions on balance refusal

**Done when:** Every consult path that today moves a job to `error_state` / retry after a failed `do_task` instead leaves the job state unchanged when `is_provider_balance_refusal(result)`; non-balance failures still transition as before; failure fields remain on the returned dict.

1. In `src/core/consult.py`, import `is_provider_balance_refusal` from `src.utils.llm_external`.

2. **`render_verdict`** — replace the bare `if not result.get("success"): return _fail(...)` after `do_task` with:

- If `is_provider_balance_refusal(result)`:  
  - Do **not** call `_transition_job_state_for_task`.  
  - Read current job state from `job` / `tracker.get_job(astral_job_id)`.  
  - If `debug=True`: `debug_index` outcome `provider_balance_refusal — state held` and `debug_detail` with `failure_class`, `error`, and `current_state`.  
  - Return `{"success": False, "to_state": <current_state>, "error": result.get("error"), "failure_class": result.get("failure_class"), "state_held": True}`.  
- Else: existing `_fail(result.get("error", "do_task failed"))`.

Prep failures (job not found, company missing, live_content) still use `_fail` unchanged — they are not balance refusals.

3. **`_run_batch_consult`** — on envelope `if not result.get("success"):` before `_transition_batch_consult_failures`:

- If `is_provider_balance_refusal(result)`: skip the batch error transition; if `debug=True`, index outcome `provider_balance_refusal — batch state held` + detail with error/failure_class; return the same failure counts shape as today (`success=False`, error, passed/failed/total) with `failure_class` / `state_held=True` on the return dict.  
- Else: existing transition.

Do **not** change missing-id / bad-grade / hydration failure transitions — those are content/validation failures, not provider balance refusals.

4. **`_run_analysis_upshot_batch`** — on `if not result.get("success"):` after `do_task`:

- If `is_provider_balance_refusal(result)`: skip `_transition_job_state_for_task`; count as `errors`; if `debug=True`, emit hold index/detail for that `aid`.  
- Else: existing dest transition.

---

## Stage 4: Roster — withhold company transitions on balance refusal

**Done when:** Prefilter single/batch API failures and `select_job_page` SELECT_FAILED no longer move company state when the agent result is a balance refusal; paths that already return without transitioning on API failure stay unchanged; debug shows hold when `debug=True`.

1. In `src/core/roster.py`, import `is_provider_balance_refusal`.

2. **`_prefilter_fail`** — at the start, when `api_result` is provided and `is_provider_balance_refusal(api_result)`:

- Do **not** call `transition_company_state`.  
- Set `result["error"] = error`, `result["state"] = current_state` (from `get_company` as today), `result["decision"] = "HOLD"`, `result["failure_class"] = api_result.get("failure_class")`, `result["state_held"] = True`.  
- Return `result`.  
- Retryable vs hard routing for non-balance failures remains unchanged.

3. **`_run_batch_company_prefilter`** — on `if not result.get("success"):` before `_transition_prefilter_batch_failures`:

- If `is_provider_balance_refusal(result)`: skip transitions; if `debug=True`, outcome `provider_balance_refusal — batch state held` + detail; return `{"passed": 0, "failed": 0, "total": len(companies), "failure_class": …, "state_held": True}`.  
- Else: existing `_transition_prefilter_batch_failures(...)`.

Hydrate / missing-id failure transitions stay as today (not balance).

4. **`_find_job_page_from_assembled`** — on `if not res.get("success"):` that currently calls `_save_company(..., state="NO_JOBLIST", ...)`:

- If `is_provider_balance_refusal(res)`:  
  - Do **not** call `_save_company`.  
  - Resolve `current_state` from `get_company(short_name)`.  
  - If `debug=True`: index outcome `provider_balance_refusal — state held` + detail with error/failure_class/current_state.  
  - Return `{"short_name": short_name, "state": current_state, "job_site": company_website, "response_type": "SELECT_FAILED", "error": res.get("error"), "failure_class": res.get("failure_class"), "state_held": True}`.  
- Else: existing `_save_company` / `NO_JOBLIST` return.

⚠️ **Decision:** Paths that already **do not** transition on `do_task` failure (`vet_inflow_discovery_company` / batch, `resolve_company_website` AI failure, coat-check `_fetch_prefilter_notes`) need **no** state-hold edits — only ensure they keep returning the error and do not newly introduce transitions. Candidate / intake / UI ad-hoc agent calls are out of scope (AC and boundaries are job/company loop state).

5. Manually verify against AC before `code()`:

| AC | Check |
|----|--------|
| 1–2 | Balance-tagged `do_task` failure leaves job/company `state` string unchanged and entity still claimable in the same trigger pool |
| 3 | Ordinary API/schema failure still routes to error/retry as before |
| 4 | Failure still visible via existing `do_task` failure storage / returned `error` (no silent drop) |
| 5 | `debug=True` shows classify + state held (index + detail) on a covered path |

---

## Self-Assessment

**Scope:** `Single-Component` — agent runtime failure classification plus consult/roster state-routing gates; config + shared utils; no JOB_STATES / COMPANY_STATES inventory changes.

**Conf:** `high` — clear AC, existing `success=False` result envelope, and known fail→transition call sites; mirrors playwright `failure_class` and AST-687 shared LLM utils patterns.

**Risk:** `Medium` — a missed transition gate would still burn loop-eligible entities into error/retry on real 402s; over-broad message matching could hold state on unrelated errors (mitigated by config substring list + 402 status).

## Self-review vs ASTRAL_CODE_RULES

- **§1.3 DRY:** One classifier in `llm_external.py`; both providers call it; callers use one `is_provider_balance_refusal` predicate.  
- **§2.1 config:** Status codes and message substrings live in `PROVIDER_BALANCE_REFUSAL`; no new JOB/COMPANY state strings.  
- **§2.4 / §2.6:** No new batch claim helpers; only gates when existing fail transitions fire.  
- **§2.2 / §2.7:** `do_task` remains the agent boundary; consult `render_verdict` / batch consult hold after that boundary.  
- **§3.3:** utils ← nothing; external ← utils; core ← utils (+ existing layers). No external↔external imports.  
- **§1.5.1:** Debug lines only when `debug=True`; index + detail for hold outcome.

---

## Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-896/AST-897-hold-entity-state-balance-refusal`  
**Product tip:** `8e6c5ff` — Stages 1–4 (`PROVIDER_BALANCE_REFUSAL` + `llm_external` classifiers; anthropic/deepseek `failure_class` tagging; `do_task` debug detail; consult + roster state-hold gates)

**Tests:** Betty at Code Complete (`qa-child`) — engineers do not land test-tree changes.
