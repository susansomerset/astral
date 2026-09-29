<!-- linear-archive: AST-897 archived 2026-08-02 -->

## Linear archive (AST-897)

**Archived:** 2026-08-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-897/hold-entity-state-on-provider-balance-refusal-in-the-event-of  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-896 — In the event of insufficient balance, do not transition state  
**Blocked by / blocks / related:** parent: AST-896

### Description

## What this implements

Recognize LLM provider balance / credit refusals (HTTP 402, Insufficient Balance, and clearly equivalent credit-exhausted refusals) on agent model calls. When such a refusal would otherwise drive a job or company state change, keep the entity in its current loop-eligible state so it stays in the same dispatch pool until credit is restored. Preserve failure recording for the attempt; only withhold the state transition. Other failure classes keep existing error/retry routing. When debug=True on touched backend paths, show that the refusal was classified as balance/credit and that state was held (AST-538 contract).

## Acceptance criteria

1. Given an agent/model call that returns HTTP 402 (or an equivalent Insufficient Balance / credit-exhausted refusal), the affected job or company **state string is unchanged** after the call completes.
2. The same entity remains eligible for the same dispatch/loop work it was eligible for before the refusal (it was not moved into an error or retry holding state solely because of the balance refusal).
3. Given a non-balance agent failure that already transitions to error or retry today, behavior is unchanged (entity still leaves the loop as before).
4. The refusal attempt is still observable in existing failure/history surfaces (not silently dropped).
5. With `debug=True` on a covered backend run, logs show that balance/credit refusal was recognized and that state was held (index outcome + working detail per AST-538).

## Boundaries

* Does not cover rate limits (e.g. 429), timeouts, malformed responses, schema/grade validation failures, missing entity data, or scrape/I/O failures.
* Does not add payment top-up, wallet UI, automatic billing repair, or a global dispatcher pause.
* Does not change pass/fail scoring for successful responses or redefine JOB_STATES / COMPANY_STATES inventories.

## Notes for planning

* Agent runtime / failure classification and any structured signal callers use to withhold transitions are in scope; follow do_task → caller state routing patterns in ASTRAL_CODE_RULES (§2.2, §2.7) and existing retryable-vs-hard hold patterns where present.
* Config remains source of truth for state names and error/retry destinations (§2.1); this feature only gates when those transitions fire after a balance refusal.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at dispatch-parent. Engineers publish to origin sub ref — never Linear gitBranchName when it disagrees.

### Comments

#### betty — 2026-07-15T05:00:38.186Z
[check-linear] Cleared `[qa-handoff]` (Radia fix-now return).

- Added `TestAst897HoldStateOnBalanceRefusal::test_run_company_task_jobs_found_balance_hold_skips_error_state` (+ `failure_class` predicate variant) so outer `run_company_task("JOBS_FOUND")` does **not** call `transition_company_state` when inner result is balance-held.
- Manifest / bible: `docs/test-bible/utils/llm_external.md` — narrowed run includes ordinary JOBS_FOUND error regression.
- Publish tip: `origin/sub/AST-896/AST-897-hold-entity-state-balance-refusal` @ `698119d` (`test(AST-897): JOBS_FOUND wrapper holds on balance refusal`; prior `merge-tests` kept singular).
- Bible shasum: `3081610b68b38b4378391e059b25bca4a5f95b78`
- Assignee → Ada; stay **Review Posted** for resolve finish → User Testing.

#### ada — 2026-07-15T04:56:54.689Z
[qa-handoff]
@Betty White

Radia fix-now (product landed on `origin/sub/AST-896/AST-897-hold-entity-state-balance-refusal` @ `4153885`):

1. `run_company_task` JOBS_FOUND now skips `error_state` when `state_held` / `is_provider_balance_refusal(result)` — hold no longer undone by the outer wrapper.
2. `_run_analysis_upshot_batch` + `_find_job_page_from_assembled` call `logger.set_debug_flag(True)` when `debug=True`.

**Need from Betty:** component coverage through the outer path — e.g. `run_company_task("JOBS_FOUND", …)` with `jobs_found_process_job_site` returning balance-hold shape (`error` + `state_held` / `failure_class=provider_balance_refusal`) asserting `transition_company_state` is **not** called, while ordinary `error` without hold still moves to locate `error_state` (existing `test_run_company_task_jobs_found_error_moves_locate_error_state`).

Existing narrowed AST-897 suite still green (22 passed including ordinary JOBS_FOUND error cases). Reassign Ada after `merge-tests` so `test-child` can re-run / we can finish resolve → User Testing.

Stay Review Posted.

#### radia — 2026-07-15T04:55:13.962Z
**fix-now:** `run_company_task` JOBS_FOUND (~1003–1007) re-transitions to `error_state` on any `result.get("error")`. `_find_job_page_from_assembled` balance hold returns `error` + `state_held=True` without `_save_company`, so the outer wrapper undoes the hold (AC1–2). Ordinary SELECT_FAILED omits `error` — only the new hold shape trips this. Skip transition when `state_held` / `is_provider_balance_refusal(result)`; cover via component test through the outer path.

**fix-now:** `_run_analysis_upshot_batch` emits hold `debug_index` / `debug_detail` under `if debug:` but never `logger.set_debug_flag(True)` — contract lines no-op (AC5 / §1.5.1). Mirror `render_verdict` / `_run_batch_consult`.

**Solid:** Config + `llm_external` classifier; Anthropic/DeepSeek tagging; consult verdict/batch holds; `_prefilter_fail` / batch prefilter holds; no cross-external imports.

Review doc: https://github.com/susansomerset/astral/blob/bd73e0d9888a6e70f74b6cffcece5895c244f86a/docs/features/agent/ast-897-hold-entity-state-on-provider-balance-refusal.md

#### betty — 2026-07-15T04:47:34.881Z
## QA test manifest (AST-897)

`origin/sub/AST-896/AST-897-hold-entity-state-balance-refusal` @ `fe6d6e3` (`merge-tests(AST-897): origin/tests 34c87cb0dcda015928ad3159861fd5bffdb65743`)

**Bible:** `docs/test-bible/utils/llm_external.md` — `ea54f034a5d637eed4e47dc8256c84c73c9b1b5e`

1. Config — `PROVIDER_BALANCE_REFUSAL` shape
2. Classifiers — `classify_provider_balance_refusal` / `is_provider_balance_refusal`
3. Anthropic tagging — 402 / substring / ordinary omit
4. DeepSeek tagging — 402 / ordinary omit
5. `do_task` debug — balance `debug_detail` when `debug=True`
6. Consult hold — `render_verdict` / `_run_batch_consult` / `_run_analysis_upshot_batch` (ordinary fail still transitions)
7. Roster hold — `_prefilter_fail` / batch prefilter / `_find_job_page_from_assembled` (ordinary still retries)

**Broken / obsolete:** none

**Narrowed run:**

```bash
./scripts/testing/run_component_tests.sh   tests/component/utils/test_config.py::TestAst897ProviderBalanceRefusalConfig   tests/component/utils/test_llm_external.py::TestAst897ProviderBalanceRefusal   tests/component/external/test_anthropic.py::TestAst897BalanceRefusalTagging   tests/component/external/test_deepseek.py::TestAst897BalanceRefusalTagging   tests/component/core/test_agent.py::TestAst897DoTaskBalanceDebug   tests/component/core/test_consult.py::TestAst897HoldStateOnBalanceRefusal   tests/component/core/test_roster.py::TestAst897HoldStateOnBalanceRefusal   -q
```

— Betty

#### ada — 2026-07-15T04:37:50.376Z
Plan published on `origin/sub/AST-896/AST-897-hold-entity-state-balance-refusal` @ `e474159`.

**Plan doc:** https://github.com/susansomerset/astral/blob/sub/AST-896/AST-897-hold-entity-state-balance-refusal/docs/features/agent/ast-897-hold-entity-state-on-provider-balance-refusal.md

**Scope:** Single-Component — tag provider balance/credit refusals (`failure_class`) in anthropic/deepseek via shared `llm_external` + config, then gate consult/roster fail→error/retry transitions so job/company state stays loop-eligible; audit/ledger failure recording unchanged.

**Conf:** high — reuses existing `success=False` envelopes and known fail-transition sites; matches AST-687 shared LLM utils + playwright `failure_class` patterns.

**Risk:** Medium — a missed gate still drains entities into error/retry on real 402s; over-broad substring matching could hold unrelated errors (mitigated by config status codes + substrings).

---

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
**Product tip:** `073bea9` — Stages 1–4 (`PROVIDER_BALANCE_REFUSAL` + `llm_external` classifiers; anthropic/deepseek `failure_class` tagging; `do_task` debug detail; consult + roster state-hold gates)

**Tests:** Betty at Code Complete (`qa-child`) — engineers do not land test-tree changes.

---

## Radia review (AST-897)

**Diff:** `origin/dev...origin/sub/AST-896/AST-897-hold-entity-state-balance-refusal` @ `fe6d6e3`

### What’s solid

- Plan Stages 1–2 match the diff: `PROVIDER_BALANCE_REFUSAL` in config; shared `classify_provider_balance_refusal` / `is_provider_balance_refusal` in `llm_external.py`; both Anthropic/DeepSeek exception returns tag `failure_class` without cross-external imports (§3.3 / §5g).
- Consult gates (`render_verdict`, `_run_batch_consult`, analysis_upshot do_task failure) and roster `_prefilter_fail` / batch prefilter skip fail→error/retry transitions and keep `error` / `failure_class` on the return (§2.1 / §2.6 / AC3–4).
- `do_task` balance detail is nested under `if debug:` via `_do_task_debug_logger` (§1.5.1). Betty bible + component coverage map to the planned call sites.

### Issues

| Sev | Location | Issue |
|-----|----------|-------|
| **fix-now** | `src/core/roster.py` `run_company_task` JOBS_FOUND branch (~1003–1007) vs `_find_job_page_from_assembled` hold return (~2353–2375) | Balance hold returns `error` + `state_held=True` without calling `_save_company`. Outer JOBS_FOUND path treats any `result.get("error")` as hard failure and calls `transition_company_state(..., error_state)`, undoing the hold (AC1–2). Ordinary SELECT_FAILED returns omit `error`, so this path only breaks the new hold shape. |
| **fix-now** | `src/core/consult.py` `_run_analysis_upshot_batch` (~775–787) | Hold path emits `debug_index` / `debug_detail` under `if debug:` but never `logger.set_debug_flag(True)`. Module logger defaults `_debug_flag=False`, so contract lines no-op on `debug=True` (AC5 / §1.5.1). Contrast `render_verdict` / `_run_batch_consult`. |

### Recommended actions

| Action | Owner |
|--------|-------|
| In `run_company_task` JOBS_FOUND (and any similar outer wrapper), skip `error_state` transition when `result.get("state_held")` or `is_provider_balance_refusal(result)`; keep logging/count as error without moving state. Add a component test through `run_company_task` or `jobs_found_process_job_site` → outer handler. | Ada (`resolve-child`) |
| At start of `_run_analysis_upshot_batch` (and preferably `_find_job_page_from_assembled` when `debug=True`), `logger.set_debug_flag(True)` before hold index/detail — same pattern as `_run_batch_consult`. | Ada (`resolve-child`) |

### Rubric notes (not fix-now)

- Scope matches Self-Assessment (`Single-Component`); no JOB_STATES / COMPANY_STATES inventory edits.
- §5f debug contract otherwise followed on consult batch / roster batch prefilter / `run_select_job_page_dispatch` (flag set before inner call).
- PJL_READY `select_job_page` dispatch path logs `error` but does not re-transition — hold is intact there.

---

## Resolution (2026-07-15 — resolve-child)

**Review ref:** Radia Linear comment + plan `## Radia review` @ `bd73e0d`.

| Item | Action |
|------|--------|
| `run_company_task` JOBS_FOUND undoes hold | Skip `transition_company_state(..., error_state)` when `result.get("state_held")` or `is_provider_balance_refusal(result)`; still log and return `total_errors: 1`. |
| `_run_analysis_upshot_batch` debug no-op | `logger.set_debug_flag(True)` at batch start when `debug=True`. |
| `_find_job_page_from_assembled` debug | Same `set_debug_flag(True)` when `debug=True` (Radia preferably). |
| Outer-path component test | Product only here — **`[qa-handoff]`** to Betty for `run_company_task` JOBS_FOUND balance-hold coverage (engineer test-tree ban). |

**Betty return (2026-07-15):** cleared `[qa-handoff]` @ `698119d` — `TestAst897HoldStateOnBalanceRefusal` outer JOBS_FOUND hold cases + ordinary error regression. Manifest green (23 passed). §9a clean vs `origin/dev` and `origin/ftr/AST-896-insufficient-balance-hold-state`.

---

## Bug: AST-1867 — report provider balance refusal as one batch-level outage

**Parent bug:** [AST-1860](https://linear.app/astralcareermatch/issue/AST-1860) (orphaned mini-parent, `ftr/AST-1860-provider-balance-outage`) · **Publish ref:** `origin/sub/AST-1860/AST-1867-provider-balance-outage`  
**Explicit scope (AST-1867 `## Scope`):** `src/core/roster.py`, `src/core/dispatcher.py`, `src/core/monitor.py`, `src/utils/config.py` (only if needed — **not needed**, see Decision D4). Product only; tests/bible are Betty's.  
**Canon Scope:** AST-1860 / AST-1867 cite no canon ids — nothing to resolve beyond ASTRAL_CODE_RULES habits already followed by this doc (§2.1 config source of truth, §3.3 layering, 3-line WARNING shape).

### As-is

DeepSeek returned HTTP 402 "Insufficient Balance" on all 24 `select_job_page` calls in batch `select_job_page-9763cb58-…`. This doc's hold worked (companies stayed `PJL_READY` via `_find_job_page_from_assembled`'s `state_held` return, AST-1842), but:

- **(a)** `run_company_task`'s `select_job_page` branch (`roster.py` ~945) sees `result["error"]`, calls `_warn_company`, returns `total_errors: 1` → run rolls up `pass:0 fail:0 error:24`. The JOBS_FOUND branch (~918–932) does the same (keeps state, still counts an error).
- **(b)** `_dispatch_one_body` calls `monitor.auto_run_error` → subject `"[✅/Somerset] select_job_page COMPLETED: 24 error(s) / 24 processed | <batch>"` with the full batch log dump as body, no headline cause.
- **(c)** Every claimed company still fires its provider call; `_run_dispatch_loop` then claims the **same** held (still-eligible) companies again on the next run until `max_runs`/drain. Each 402 is logged twice (provider-side line + `_warn_company`).
- **(d)** `_check_circuit_breaker` auto-disables after 3 consecutive COMPLETED runs with 0 passed / 0 failed — exactly the balance-refusal shape — so an unpaid provider silently turns AUTO off, and it stays off after credit is restored.

### To-be

A provider balance refusal is reported as **one provider-level outage** per dispatch run: held entities are counted as held, not errors; once a balance refusal comes back, the run issues **no further provider calls** (remaining entities in the batch are skipped and released, and the dispatch loop claims no further batches); the AUTO alert subject names the provider + "insufficient balance" with a short body (no log dump); balance-refusal runs never count toward the circuit breaker. The AST-897 / AST-1842 per-entity state hold is unchanged. No failover, no retries, no new caps.

### Repro

Fixture (no DB seed needed — astral persistence is file/SQLite rows built by test helpers; this is the data shape):

```python
task = {
    "id": 1, "task_key": "select_job_page", "candidate_id": "cand-1",
    "entity_type": "company", "trigger_state": "PJL_READY",
    "batch_call_mode": 0, "batch_size": 24, "auto_mode": 1, "max_runs": 0,
}
companies = [{"short_name": f"co{i}", "state": "PJL_READY",
              "company_data": {...assembled PJL maps...}} for i in range(24)]
# agent.do_task("select_job_page", ...) returns for every call:
balance_refusal = {
    "success": False, "api_response": None,
    "error": "Error code: 402 - {'error': {'message': 'Insufficient Balance', ...}}",
    "failure_class": "provider_balance_refusal",
}
```

Steps: `_dispatch_one_body(task, debug=False)` with `get_active_llm_provider() == "deepseek"`.  
**Today:** 24 `do_task` calls per run (and again on every subsequent loop run); ledger row `COMPLETED`, `total_errors=24`; `auto_run_error` subject `"… select_job_page COMPLETED: 24 error(s) / 24 processed | …"`; after 3 such runs `update_dispatch_task(1, enabled=False)`.  
**After fix:** exactly **1** `do_task` call (the cache-warm first entity); 23 companies skipped and released by `clear_company_batch`; loop stops after run 1; ledger row `INTERRUPTED`, `total_processed=1, total_errors=0`; one `monitor.provider_balance_outage` email, no `auto_run_error`; `_check_circuit_breaker` not called and the row is invisible to future breaker lookbacks; all 24 companies still `PJL_READY`.

### Root cause

AST-897 scoped only the per-entity **state** decision. The batch layer still treats a balance-held result as an ordinary entity error:

1. `run_company_task` maps any `result.get("error")` to `total_errors: 1` — it never consults `is_provider_balance_refusal(result)` for **counting** (only for the JOBS_FOUND state transition).
2. `_run_unified` / `_run_dispatch_loop` have no batch-level signal: nothing tells them the provider itself is refusing, so every entity and every subsequent claim still calls the provider.
3. `_dispatch_one_body` routes alerts purely on `total_errors > 0`, and `_check_circuit_breaker` reads only `total_passed`/`total_failed` of `COMPLETED` rows — a refusal run is indistinguishable from a genuinely stuck task.

### Proposed change

Signal path (task-agnostic, keyed on `failure_class`): any per-run result dict that satisfies `is_provider_balance_refusal(result)` → `_run_unified` records a **ctx-level marker** `ctx["provider_balance_outage"]` → skips remaining entities → `_run_dispatch_loop` stops → `_dispatch_one_body` ends the run `INTERRUPTED` and sends the provider-outage alert. The marker lives on `ctx` (per-run dict copied from `database.get_candidate` in `_dispatch_one_body`, same side-channel precedent as AST-1847's `ctx["dispatch_partial"]`), **not** in the summary counts, because `update_dispatch_ledger(**accumulated)` rejects keys outside `_LEDGER_UPDATE_COLS` and the ledger schema (`src/data/database.py`) is out of scope.

#### 1. `src/core/roster.py` — `run_company_task`

1a. **`select_job_page` branch** (`elif input_state == ROSTER_CONFIG["select_job_page"]["dispatch_trigger_state"]`, ~945): before the existing `if result.get("error"):` add:

```python
# AST-1867: provider refused for balance — held (AST-897 kept state), not an entity error;
# failure_class travels up so the dispatcher can stop the batch and alert once.
if is_provider_balance_refusal(result):
    logger.debug("%s | company select_job_page held: provider_balance_refusal error=%r", short_name, result.get("error"))
    return {**zero, "total_held": 1, "failure_class": result.get("failure_class"), "error": result.get("error")}
```

No `_warn_company` on this path (that is the second of the two per-call 402 log lines). Everything after it (ordinary `error` → `_warn_company` + `total_errors: 1`; terminal/pass/fail mapping) is unchanged.

1b. **JOBS_FOUND branch** (~918): identical early return (task label `jobs_found` in the debug line) placed as the first statement inside `if result.get("error"):`, **before** the `dest` / `_warn_company` / `transition_company_state` lines. Leave the existing `not result.get("state_held") and not is_provider_balance_refusal(result)` guards exactly as they are — they still protect the non-balance `state_held` case (AST-1189 call-budget).

`total_processed` stays `1` for a held company (it was attempted); `total_held` is a new informational key. It is **not** added to `_SUMMARY_ZERO` (no ledger column); the dispatcher reads it only to fill the alert body.

#### 2. `src/core/dispatcher.py`

2a. **Imports:** `from src.utils.llm_external import is_provider_balance_refusal` (core ← utils, §3.3).

2b. **New helper** directly above `_run_unified`:

```python
def _note_provider_balance_outage(ctx: Dict, task: Dict, result: Dict) -> None:
    """AST-1867: first balance refusal in a run sets ctx["provider_balance_outage"] and logs one WARNING;
    later refusals only add to the held tally."""
    outage = ctx.get("provider_balance_outage")
    if outage is None:
        outage = ctx["provider_balance_outage"] = {"error": result.get("error") or "", "held": 0}
        logger.warning(
            "%s | dispatch %s %s\n  LLM provider refused: insufficient balance (%s)\n  The batch is stopping; entity state is held",
            ctx.get("astral_candidate_id") or task.get("candidate_id") or "-",
            task.get("entity_type") or "-",
            task.get("task_key") or "-",
            outage["error"],
        )
    outage["held"] += int(result.get("total_held", 0) or 0)
```

2c. **`_run_unified`** — per-entity path (`else:` branch, `async def _one(e)`):

- First line of `_one`: `if ctx.get("provider_balance_outage"): return dict(_SUMMARY_ZERO)` — entity is not sent to the provider and not counted as processed; the existing `finally: clear_*_batch(bid)` releases it.
- After `result = await consult.run_consult_task(...)`: `if is_provider_balance_refusal(result): _note_provider_balance_outage(ctx, task, result)`.

Because `_warm_then_gather` runs entity 0 alone first, a refusal on entity 0 means every other `_one` returns immediately (no provider call). Entities already in flight when a later refusal lands finish normally — no cancellation (Decision D2).

2d. **`_run_unified`** — full-batch paths (task-agnostic; only fires where the consult return carries `failure_class`):

- Chunk split: inside `_consult_chunk`, first line `if ctx.get("provider_balance_outage"): return dict(_SUMMARY_ZERO)`; after the `consult.run_consult_task` call, `if is_provider_balance_refusal(result): _note_provider_balance_outage(ctx, task, result)`. Head chunk runs first, so a head refusal skips every tail chunk.
- Single consult call: after the call, same `is_provider_balance_refusal` → `_note_provider_balance_outage` (nothing left to skip in-run; the loop stop in 2e still applies).

2e. **`_run_dispatch_loop`** — right after the mid-run `update_dispatch_ledger(dispatch_ledger_id, **accumulated)` and **before** the `total_processed == 0` check:

```python
if ctx.get("provider_balance_outage"):
    logger.debug("loop stop: provider balance refusal run_count=%s", run_count)
    logger.debug("End dispatch loop after %s run(s)", run_count)
    break
```

(The one operator-facing WARNING was already emitted by 2b; no extra info line.)

2f. **`_dispatch_one_body`** — main (candidate/ctx) path only; meteorite / bot-blocked / mailbox branches pass `{}` or no ctx and never call `_run_unified`, so they are untouched:

- Immediately after `await _tracked()` in the `try:` (successful return), add: `if ctx.get("provider_balance_outage"): final_status = "INTERRUPTED"` — the run was cut short by a provider outage. Effects, all via existing code: the ledger row is written `INTERRUPTED`; `_log_dispatch_task_completed` (COMPLETED-only) is skipped — the 2b WARNING replaces it; `_check_circuit_breaker` (called only when `COMPLETED`) is skipped; and `get_recent_ledger_summaries` (`status = 'COMPLETED'`) never sees this row, so past outage runs can't combine with a later genuine zero-progress run to trip the breaker.
- Alert routing in `finally:` — replace the single `auto_run_error` block with:

```python
outage = ctx.get("provider_balance_outage")
if dispatch_ledger_id and not is_click and outage:
    monitor.provider_balance_outage(task_key, dispatch_ledger_id, accumulated, outage, candidate_id)
elif dispatch_ledger_id and not is_click and accumulated.get("total_errors", 0) > 0:
    monitor.auto_run_error(task_key, dispatch_ledger_id, accumulated, final_status, candidate_id)
```

Same AUTO-only / ledger-present gate as today; CLICK runs get the 2b WARNING only (unchanged policy). If a dispatch timeout or admin cancel also occurs, `final_status` is already `INTERRUPTED` and the outage alert still wins (one email per run).

2g. **`_check_circuit_breaker`** — **no code change**; exclusion is achieved by 2f (status `INTERRUPTED` is filtered out by the ledger query it reads). Scope allows "`_check_circuit_breaker` (or the ledger summary it reads)".

#### 3. `src/core/monitor.py` — new `provider_balance_outage`

Add after `auto_run_error`; import `get_active_llm_provider` from `src.utils.config`. Module docstring gains one line naming the new entry point.

```python
def provider_balance_outage(task_key: str, batch_id: str, accumulated: dict, outage: dict, candidate_id: str = "") -> None:
    """AST-1867: one alert per AUTO run stopped by an LLM provider balance refusal.
    Short body (no batch log dump). Never raises — a failed alert must not surface to the caller."""
    try:
        provider = get_active_llm_provider()
        prefix = _format_alert_subject_prefix(get_deploy_label(), _resolve_candidate_last_name(candidate_id))
        subject = f"{prefix} {provider} insufficient balance — {task_key} stopped | {batch_id}"
        lines = [
            f"Provider: {provider}",
            f"Refusal: {outage.get('error') or '-'}",
            f"Task: {task_key}   Batch: {batch_id}",
            f"Processed: {accumulated.get('total_processed', 0)}  Passed: {accumulated.get('total_passed', 0)}  "
            f"Failed: {accumulated.get('total_failed', 0)}  Errors: {accumulated.get('total_errors', 0)}",
        ]
        if outage.get("held"):
            lines.append(f"Held (state unchanged): {outage['held']}")
        lines.append("Entity state was held; the task stays enabled and resumes once provider credit is restored.")
        if not send_email(to=ASTRAL_CONFIG["support_email"], subject=subject, body="\n".join(lines)):
            logger.warning("[monitor] send_email returned False for batch %s — check Gmail credentials", batch_id)
    except Exception as e:
        logger.warning("[monitor] provider_balance_outage raised unexpectedly for %s: %s", batch_id, e)
```

Example subject for the repro: `"[✅/Somerset] deepseek insufficient balance — select_job_page stopped | select_job_page-9763cb58-…"`.

#### 4. `src/utils/config.py` — no change (Decision D4)

#### ⚠️ Decisions (for fix-board)

- **D1 — "held" keys on balance refusal only, not bare `state_held`.** AST-1867's Technical scope says "`state_held` or a balance-refusal `failure_class`". But `_find_job_page_from_assembled` also sets `state_held=True` for **AST-1189 provider-call-budget timeouts** (`roster.py` ~2233). Counting those as held would drop them out of `total_errors` → no `auto_run_error` email, while still letting all-timeout `COMPLETED` runs trip the breaker — a silent regression the bug doesn't ask for. So `run_company_task` returns `total_held` only when `is_provider_balance_refusal(result)`; call-budget holds keep today's `total_errors: 1` (narrower than scope, same file/function/kind of change).
- **D2 — "stop issuing calls" = no *new* calls.** Entities not yet started are skipped; calls already in flight (concurrent gather members started before the first refusal returned) are not cancelled. No caps/retries added.
- **D3 — breaker exclusion via `INTERRUPTED`, not a new ledger column.** A refusal run *was* cut short, so `INTERRUPTED` is truthful; it reuses an existing status the admin UI already renders (`AdminPerformanceMonitor.tsx`), needs no `database.py` change (out of scope), and excludes the run from both the current breaker check and all future lookbacks.
- **D4 — alert wording hard-coded in `monitor.py`, no config change.** Matches `auto_run_error`'s precedent (subject built in monitor); provider name comes from existing `get_active_llm_provider()` (provider is global per `LLM_PROVIDER_CONFIG`, `agent.py` ~1983). The breaker exclusion is structural (D3), so there's no switch to configure.
- **D5 — `prefilter_company` (AST-1858/1859 question) not wired end-to-end.** The dispatcher path is task-agnostic, but `consult.run_consult_task`'s `prefilter_company` branch (and the other company batch branches) rebuilds the summary dict and drops `failure_class`/`state_held`; `consult.py` is outside AST-1867's scope. Prefilter balance refusals therefore keep today's counting/alert/breaker behavior until a follow-up widens scope to `consult.py` (one-line pass-through of `failure_class`). Per-company paths (`batch_call_mode=0`, incl. `select_job_page`, JOBS_FOUND) are covered.

### Blast radius

- **`_run_unified` / `_run_dispatch_loop` / `_dispatch_one_body`** are shared by every candidate-scoped dispatch task (job consult, company, candidate). New behavior fires **only** when a returned dict carries `failure_class == "provider_balance_refusal"`; all other runs take identical code paths (the ctx key is absent).
- **Job consult batch paths** (`_run_batch_consult`, `render_verdict` holds from this doc's Stage 3) return `failure_class` only where consult passes it through; where it does, those runs now also stop/alert/skip-breaker — intended (task-agnostic). Where consult rebuilds the dict, behavior is unchanged (D5).
- **Ledger semantics:** refusal runs now show `INTERRUPTED` in execution history instead of `COMPLETED`; skipped entities are not in `total_processed`. `entity_cost` math already guards `total_processed == 0`.
- **Alerts:** refusal runs no longer send `auto_run_error`; they send `provider_balance_outage` instead. Non-refusal error runs unchanged.
- **Tests likely asserting the old behavior (Betty's call):** `tests/component/core/test_roster.py::TestAst897HoldStateOnBalanceRefusal` JOBS_FOUND outer-path cases (currently expect `total_errors: 1` on the balance hold); dispatcher tests around `auto_run_error` gating and `_check_circuit_breaker`; `_warm_then_gather` / `_run_unified` summary tests that stub `run_consult_task`. Monitor tests for the new function are new coverage.
- **AST-1839** (retry-routed → not `total_errors`) and **AST-1847** (`dispatch_partial` on timeout) are adjacent; neither code path is modified.

### What must still hold

- **AST-897 AC1–2:** balance-refused job/company **state string unchanged** and entity stays loop-eligible — no edit to any hold gate (`classify_provider_balance_refusal`, `is_provider_balance_refusal`, `_find_job_page_from_assembled` held return, `_prefilter_fail` / batch prefilter holds, consult holds). Skipped entities are released by the existing `clear_*_batch` in `_run_unified`'s `finally`, never transitioned.
- **AST-897 AC3:** non-balance failures (ordinary `error`, AST-1189 call-budget `state_held`) keep today's routing **and** counting (`total_errors: 1`, JOBS_FOUND `error_state` transition for ordinary errors).
- **AST-897 AC4:** the refusal attempt is still recorded (agent/ledger failure storage untouched) and now also surfaced once in the 2b WARNING and the outage email.
- **Circuit breaker** still trips on 3 genuine consecutive COMPLETED zero-progress runs.
- **Alert gate** stays AUTO-only with a ledger id; ordinary error runs still get `auto_run_error` with the full log body.
- No new limits, caps, retries, or failover; the only new stop is "a balance refusal came back".

## Joan fix-board — AST-1867

Read the **Bug: AST-1867** plan-fix block on `origin/sub/AST-1860/AST-1867-provider-balance-outage` (As-is through What must still hold). Overlap skim via `canon/docs/DIRECTIVES-DIRECTORY.md` and active directives on the epic worktree (`docs/canon-index.md` absent on this ref, same resolution as prior fix-board passes).

**Triage:** Ticket **Canon Scope** lists no directive ids. The change extends AST-897’s existing `failure_class` / `is_provider_balance_refusal` signal into dispatcher batch control (`ctx["provider_balance_outage"]`, same side-channel class as AST-1847’s `dispatch_partial`), roster counting (`total_held` vs `total_errors`), ledger `INTERRUPTED`, and a new `monitor.provider_balance_outage` alert. That aligns with **`stat.logging.warning`** dispatcher stops (3-line English, product next step — mirrors admin kill and circuit auto-disable) and skips the COMPLETED **`stat.logging.info.dispatcher`** task-completed line without contradicting Resolution §2 (this is not timeout `logger.exception` INTERRUPTED). **`patt.entity.batch-processing`** still claim → process → **`finally` release**; skipped entities are not double-processed. **`patt.dispatch.scheduler-loop`** / breaker unchanged in code; exclusion via non-`COMPLETED` ledger rows matches existing timeout/admin INTERRUPTED semantics. No in-force statute requires balance refusals to roll up as `total_errors` or to trip the breaker; D5 (`consult.py` pass-through gap) is scoped follow-up, not an Archie precedent call. No canon edit required before `make-fix`.

BEGIN-VERDICT

```
[board-joan]  CANON: OK
```

END-VERDICT

```text
AST-1867 board-joan done — CANON: OK.
```

## Radia review — AST-1867

[code-rubric]  
**Ticket:** AST-1867  
**Publish ref:** `144b8850c986aebb1c330035a3f82e704d04bb0c` (`origin/sub/AST-1860/AST-1867-provider-balance-outage`)  
**Diff base:** `fbe9486e` (`origin/ftr/AST-1860-provider-balance-outage`)  
**Corpus:** `docs/canon-index.md` absent on ftr and sub tips — no `corpus_sha`; Joan fix-board used `canon/docs/DIRECTIVES-DIRECTORY.md` overlap skim (same as prior passes).  
**Overall:** CLEAN  

**Status gate:** Spawn prompt + Linear brief confirm **Tests Passed** (assignee Ada). Proceed.

---

## Fix-specific checks

**[bug-repro]** not applicable — clean board opt-out on this tip: Betty **TESTS: REVISE** is owned by sibling **AST-1870** (`origin/sub/AST-AST-1860/AST-1870-provider-balance-outage` @ `d4494bc3`; repro red at ftr base, green with fix overlaid). No `[bug-repro]` on AST-1867 tip; qa-fix did not run here. Appropriate for F7.

**## What must still hold** — OK (traced against `origin/ftr/...origin/sub/...` product diff only):

| Item | Verdict |
|------|---------|
| AST-897 AC1–2 (hold gates, state, eligibility) | No edits to `classify_*`, `_find_job_page_from_assembled` hold return, prefilter holds, or consult hold paths; skip path uses existing `clear_*_batch` in `_run_unified` `finally`. |
| AST-897 AC3 (non-balance errors / AST-1189 call-budget `state_held`) | D1 honored: early return only when `is_provider_balance_refusal(result)`; JOBS_FOUND guards for bare `state_held` unchanged; ordinary errors still `_warn_company` + `total_errors: 1`. |
| AST-897 AC4 (attempt recorded + surfaced) | Agent/ledger failure storage untouched; one 3-line `logger.warning` in `_note_provider_balance_outage` + `monitor.provider_balance_outage`. |
| Circuit breaker (3× COMPLETED zero-progress) | `final_status = "INTERRUPTED"` when `ctx["provider_balance_outage"]`; `_check_circuit_breaker` only on `COMPLETED`; ledger query unchanged. |
| Alert gate (AUTO + ledger; `auto_run_error` for ordinary errors) | `not is_click` preserved; outage branch before `total_errors` branch. |
| No new limits/caps/retries/failover | Only new stop is balance refusal marker + loop `break`; D2 (no cancel in-flight) respected. |

---

## Canon scores

Frozen **Canon Scope** on AST-1867 lists **no directive ids** (issue description + plan-fix block). Nothing to resolve per id; Joan fix-board **CANON: OK** by overlap skim (`stat.logging.warning`, `patt.entity.batch-processing`, breaker via ledger status).

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| *(frozen list empty)* | — | — | Joan board CANON: OK; habits cited in plan (config SOT, layering, 3-line WARNING) observed in diff |

**Worst grade:** none scored → roll-up **CLEAN** (no off-list statute scored; no §5.3 ESCALATE).

---

## Column diff vs plan stage

`no plan-stage per-id scores attached` — Joan artifact is `[board-joan] CANON: OK` only; aligned on intent.

---

## Plan fidelity (§5.4)

Diff matches **Proposed change** §§1–3 and D4 (no `config.py`):

- **roster:** JOBS_FOUND + `select_job_page` balance early returns (`total_held`, `failure_class`, no `_warn_company` on balance path).
- **dispatcher:** `_note_provider_balance_outage`, per-entity/chunk short-circuit, loop stop, `INTERRUPTED` + alert routing.
- **monitor:** `provider_balance_outage` mirrors `auto_run_error` safety (try/except, no raise).

**D5 (`prefilter_company` / consult rebuild)** explicitly out of scope; not implemented — matches Susan-approved scope.

---

## Frame diff

(none)

---

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **Job encoded batch consult:** `consult.run_consult_task` normalizes batch results at ~2893–2898 and drops `failure_class`, so dispatcher `is_provider_balance_refusal(result)` after `run_consult_task` does **not** fire for `qualify_*` / `_run_batch_consult` balance holds even though `_run_batch_consult` can return `failure_class`. Plan blast radius says job paths stop “where consult passes it through”; at the `run_consult_task` boundary they do not — behavior for those tasks stays pre-fix. **Not a defect for the approved repro** (`select_job_page`, `batch_call_mode=0` company path passes `run_company_task` dict through with `failure_class`). Follow-up only if product wants encoded job batches on the same outage rail without touching `consult.py`.
- **Sibling test carry:** Betty’s REVISE and the two AST-897 JOBS_FOUND assertion deltas are **AST-1870**; 69 other roster/dispatcher/monitor failures match `origin/dev` per Ada’s test-fix note — do not attribute to this tip.
- **Parent shape for Chuckles:** AST-1860 is a **mini-parent with live `ftr/AST-1860-provider-balance-outage`** — **not** fix-lane “orphaned parent (Done, merge straight to dev)”. On **PROCEED**: **Review Posted** → clean-review shortcut (**User Testing**, skip `resolve-child`) → normal fix rollup on `ftr`, not finish-up-to-dev-only.

---

## What’s solid

- Side-channel `ctx["provider_balance_outage"]` follows AST-1847 `dispatch_partial` precedent; no ledger schema creep.
- Breaker exclusion is structural (`INTERRUPTED`), not a one-off hack in `_check_circuit_breaker`.
- Held tally uses `total_held` from roster summary; `is_provider_balance_refusal` on consult return works for per-company dispatch.
- Scope stays in four files (plus plan doc); no `consult.py`, no caps/limits.

---

## Recommended actions

Chuckles: append artifact, `docs(AST-1867): Radia review — clean`, post slim upshot, **Review Posted** → **User Testing** (clean shortcut). Ensure **AST-1870** lands before or with rollup so bible/tests match D1.

`context_tokens≈12000`

---

### Slim upshot (Chuckles → Linear `--as radia`)

```
[code-rubric] PROCEED (Commit: 144b8850) plan-faithful outage path
```

#### Chuckles disposition (AST-1867)

Clean review: Review Posted → User Testing via the clean-review shortcut (resolve-child skipped). Merged into the mini-parent ftr.

Docs-acceptance on this tip: no test-tree delivery here — tests and bible land on gap sibling AST-1870.

Follow-up candidates (not in this bug's approved scope): consult.py drops `failure_class` at the batch-result boundary, so prefilter_company (AST-1858/AST-1859 shape) and encoded job batch consults stay on the pre-fix counting/alert path.

---

## Bug: AST-1870 — tests for provider balance outage path (AST-1867 board)

**Parent bug:** [AST-1860](https://linear.app/astralcareermatch/issue/AST-1860) · **Gap for:** AST-1867 (`[board-betty] TESTS: REVISE`) · **Publish ref:** `origin/sub/AST-1860/AST-1870-provider-balance-outage-tests`  
**Explicit scope (AST-1870 `## Scope`):** `tests/component/core/test_roster.py`, `tests/component/core/test_dispatcher.py`, `tests/component/core/test_monitor.py`, `docs/test-bible/core/{roster,dispatcher,monitor}.md`. Test + bible only — **Betty lands them at `qa-fix`**; this block names the exact nodes. No product code.  
**Branch note:** this ref was fast-forwarded to `origin/sub/AST-1860/AST-1867-provider-balance-outage` @ `144b8850` so AST-1867's plan block precedes this one — the ref therefore **carries AST-1867's product change**. Red/green proof must compare against the pre-fix product explicitly (see Repro).

### As-is

AST-1867 (`144b8850`) changed batch behavior on a provider balance refusal, but no test covers it, and two AST-897 tests now fail on the fix:

- `test_roster.py::TestAst897HoldStateOnBalanceRefusal::test_run_company_task_jobs_found_balance_hold_skips_error_state` and `::test_run_company_task_jobs_found_balance_failure_class_skips_error_state` assert `out["total_errors"] == 1` (fix returns `total_errors: 0`, `total_held: 1`).
- Uncovered: select_job_page held counting (AST-1867 §1a), `_run_unified` skip-after-refusal (§2c/2d), `_run_dispatch_loop` stop (§2e), `_dispatch_one_body` INTERRUPTED + `provider_balance_outage` instead of `auto_run_error` + breaker skip (§2f/2g), `monitor.provider_balance_outage` (§3), and the D1 guard (AST-1189 call-budget `state_held` still `total_errors: 1`).

### To-be

The nodes below exist, the two AST-897 assertions follow the held contract, and bible entries in `docs/test-bible/core/{roster,dispatcher,monitor}.md` name every node. One dispatcher-level `[bug-repro]` is **red on the pre-fix product** and **green on `144b8850`**.

### Repro

The `[bug-repro]` (node **D1** below) was drafted as a scratch test (in `/tmp`, never committed) and run both ways against the real stack `_dispatch_one → _run_dispatch_loop → _run_task → _run_unified → consult.run_consult_task → roster.run_company_task`, stubbing only `roster.run_select_job_page_dispatch` (the AST-1842 held return) and DB/email edges:

- **RED at pre-fix product** (`origin/ftr/AST-1860-provider-balance-outage` @ `fbe9486e`, detached scratch worktree): `AssertionError: assert 9 == 1` on `run_select_job_page_dispatch.await_count` — 3 companies × 3 runs (`max_runs=3`), one `_warn_company` WARNING per company per run, exactly the incident shape.
- **GREEN at `144b8850`:** 1 passed.

Host env for the scratch run: `ASTRAL_DB_DIR` (throwaway dir) and dummy `GMAIL_USER` / `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` / `GOOGLE_REFRESH_TOKEN` (import-time checks only; both alert functions are mocked). The normal `run_component_tests.sh` env already covers this.

Roster nodes R3/R4 were scratch-checked the same way: R3 red at base (`assert 1 == 0` on `total_errors`), green at fix; R4 green on both (guard).

### Root cause

AST-1867 is a product-behavior change with no test delta: the board correctly found (a) two assertions pinned to the old "balance hold still counts as an error" contract and (b) zero coverage for the new dispatcher/monitor paths.

### Proposed change

All new classes follow existing module conventions (`monkeypatch`, `MagicMock`/`AsyncMock`, `@pytest.mark.asyncio`, `dispatcher_mod` / `roster_mod` / `monitor_mod` aliases already imported in each file). `FC = "provider_balance_refusal"`; `REFUSAL_ERR = "Error code: 402 - Insufficient Balance"`.

#### `tests/component/core/test_roster.py`

**R1 — modify** `TestAst897HoldStateOnBalanceRefusal::test_run_company_task_jobs_found_balance_hold_skips_error_state` (~6236): replace `assert out["total_errors"] == 1` with
`assert out["total_errors"] == 0`, `assert out["total_held"] == 1`, `assert out["failure_class"] == self._FC`. Keep `transition.assert_not_called()`. Docstring: add "AST-1867: counted held, not an error."

**R2 — modify** `::test_run_company_task_jobs_found_balance_failure_class_skips_error_state` (~6259): same three assertions (the predicate path — `failure_class` without `state_held`).

**New class** `TestAst1867BalanceHeldCounting` (append after `TestAst897HoldStateOnBalanceRefusal`):

**R3** `test_select_job_page_balance_hold_counts_held_not_error` (async) — patch `roster_mod.run_select_job_page_dispatch` → `AsyncMock(return_value={"short_name": "acme", "state": "PJL_READY", "response_type": "SELECT_FAILED", "error": REFUSAL_ERR, "failure_class": FC, "state_held": True})`; patch `roster_mod._warn_company` → `MagicMock()`. Call `run_company_task("PJL_READY", {"short_name": "acme", "state": "PJL_READY"}, "b1867", dispatch_task_key="select_job_page")`. Assert `total_processed == 1`, `total_errors == 0`, `total_passed == 0`, `total_failed == 0`, `total_held == 1`, `failure_class == FC`, `error == REFUSAL_ERR`; `_warn_company.assert_not_called()`.

**R4** `test_call_budget_hold_still_counts_error` (async, `@pytest.mark.parametrize("branch", ["select_job_page", "jobs_found"])`) — D1 regression guard. Inner result `{"error": "provider call budget exceeded", "failure_class": PROVIDER_CALL_BUDGET["failure_class"], "state_held": True, "state": <PJL_READY|JOBS_FOUND>}` (import `PROVIDER_CALL_BUDGET` from `src.utils.config`). Patch `transition_company_state` → `MagicMock()`. `select_job_page`: stub `run_select_job_page_dispatch`, call with `"PJL_READY"` + `dispatch_task_key="select_job_page"`. `jobs_found`: stub `jobs_found_process_job_site`, call `run_company_task("JOBS_FOUND", {"short_name": "acme", "job_site": "https://j"}, "b1189")`. Assert `total_errors == 1`, `"total_held" not in out`, `transition.assert_not_called()` (AST-897 guard still protects `state_held` on JOBS_FOUND).

#### `tests/component/core/test_dispatcher.py`

**New class** `TestAst1867ProviderBalanceOutage` (append after `TestAst1847TimeoutPartialCounts`). Shared setup helper inside the class (`_edges(monkeypatch)`) patches: `database.get_candidate` → `{"astral_candidate_id": cid, "candidate_api_key": "key"}`; `_current_agent_task_run_next` → `lambda tk: None` (otherwise a run_next chain suppresses the ledger id and the alert); `database.save_dispatch_ledger`, `database.update_dispatch_ledger`, `flush_log_buffer`, `_db_update_dispatch_task` → `MagicMock()`; `compute_batch_cost` → `MagicMock(return_value=0.0)`; `_check_circuit_breaker` → `MagicMock()` (**patch, never call** — see Blast radius, pre-existing signature drift); `check_internet_reachable` → `lambda: True`; `monkeypatch.setitem(dispatcher_mod.ASTRAL_CONFIG, "cache_warm_delay_seconds", 0)`; `monitor.auto_run_error` → `MagicMock()`; `monitor.provider_balance_outage` → `MagicMock()` with **`raising=False`** (so the repro fails on assertions, not setup, against the pre-fix product where the attribute doesn't exist).

**D1 `[bug-repro]`** `test_bug_repro_balance_refusal_one_call_interrupted_outage_alert` (async) — the incident, end to end:
- `database.count_eligible_for_dispatch_task` → `lambda task: 24` (held companies stay eligible).
- `src.core.roster.get_new_company_batch` → `MagicMock(return_value=("bid-1867", [3 companies {"short_name": f"co{i}", "state": "PJL_READY", "company_website": f"https://co{i}"}]))`; `src.core.roster.clear_company_batch` → `MagicMock()`.
- `roster_mod.run_select_job_page_dispatch` → `AsyncMock(return_value={... "state": "PJL_READY", "response_type": "SELECT_FAILED", "error": REFUSAL_ERR, "failure_class": FC, "state_held": True})`.
- Task: `{"id": 1867, "task_key": "select_job_page", "candidate_id": "cand-1", "entity_type": "company", "trigger_state": "PJL_READY", "batch_call_mode": 0, "batch_size": 3, "auto_mode": 1, "max_runs": 3}` (`max_runs=3` bounds the pre-fix run; `0` would loop forever there). `await dispatcher_mod._dispatch_one(task)`.
- Assert: `run_select_job_page_dispatch.await_count == 1`; `get_new_company_batch.call_count == 1`; `clear_company_batch.assert_called_once_with("bid-1867")`; final `update_dispatch_ledger.call_args.kwargs` has `status == "INTERRUPTED"`, `total_processed == 1`, `total_errors == 0`; `auto_run_error.assert_not_called()`; `provider_balance_outage.assert_called_once()` with `args[0] == "select_job_page"`, `args[1] == "select_job_page-…"` (startswith `"select_job_page-"`), `args[3] == {"error": REFUSAL_ERR, "held": 1}`, `args[4] == "cand-1"`; `_check_circuit_breaker.assert_not_called()`.

**D2** `test_run_unified_per_entity_skips_after_refusal` (async) — `_run_unified` directly, company task (`batch_call_mode: 0`, 3 entities, claim/clear patched as D1). `src.core.consult.run_consult_task` → `AsyncMock(return_value={"total_processed": 1, "total_passed": 0, "total_failed": 0, "total_errors": 0, "total_held": 1, "failure_class": FC, "error": REFUSAL_ERR})`. `ctx = {"astral_candidate_id": "cand-1"}`. Assert consult `await_count == 1`; `out == {"total_processed": 1, "total_passed": 0, "total_failed": 0, "total_errors": 0}` (no `total_held` / `failure_class` leak into the summary → ledger-safe); `ctx["provider_balance_outage"] == {"error": REFUSAL_ERR, "held": 1}`; clear called once.

**D3** `test_run_unified_chunk_split_skips_tail_after_head_refusal` (async) — job consult chunk path: task `{"entity_type": "job", "trigger_state": "JD_READY", "task_key": "evaluate_jd", "batch_call_mode": 1, "batch_size": 1, "score_floor": 0.5}`, `database.count_eligible_for_dispatch_task` → `3`, `src.core.tracker.get_new_job_batch` → 3 jobs, `clear_job_batch` patched; consult returns `{"total_processed": 1, "total_passed": 0, "total_failed": 0, "total_errors": 1, "failure_class": FC, "error": REFUSAL_ERR}`. Assert consult `await_count == 1` (tail chunks skipped); `ctx["provider_balance_outage"]["held"] == 0` (no `total_held` on a consult envelope).

**D4** `test_run_unified_ordinary_error_does_not_skip` (async) — same as D2 but consult returns `{"total_processed": 1, "total_errors": 1, "error": "boom"}` (no `failure_class`). Assert `await_count == 3`, `"provider_balance_outage" not in ctx`, `out["total_errors"] == 3`. Guards the task-agnostic key.

**D5** `test_run_dispatch_loop_stops_after_outage_run` (async) — `_run_dispatch_loop` directly: `count_eligible_for_dispatch_task` → `24`; `_run_task` → `AsyncMock(side_effect=_run)` where `_run(task, ctx, debug)` sets `ctx["provider_balance_outage"] = {"error": REFUSAL_ERR, "held": 1}` and returns `{"total_processed": 1, "total_passed": 0, "total_failed": 0, "total_errors": 0}`; `update_dispatch_ledger` patched. Task `{"id": 5, "task_key": "select_job_page", "entity_type": "company", "auto_mode": 1, "max_runs": 0}` (unlimited — only the outage stop can end it). Call with `(ctx, task, "select_job_page", "bid", accumulated, "bid")`. Assert `_run_task.await_count == 1`; `update_dispatch_ledger` called once with `accumulated` counts (mid-run write happens before the stop).

**D6** `test_dispatch_one_click_outage_interrupted_no_alert` (async) — `_edges`; `_run_dispatch_loop` → `AsyncMock(side_effect=_loop)` where `_loop(ctx, task, task_key, batch_id, accumulated, ledger_id)` sets `ctx["provider_balance_outage"] = {...}` and `accumulated["total_processed"] = 1`. Task `auto_mode: 0` (CLICK). Assert final ledger `status == "INTERRUPTED"`; `provider_balance_outage` and `auto_run_error` both not called (AUTO-only gate); `_check_circuit_breaker.assert_not_called()`.

**D7 — existing, unchanged:** `TestDispatchOne::test_auto_run_error_on_auto_failures` stays green (non-outage error → `auto_run_error`). Listed in the manifest as the regression half of the alert routing; see Blast radius for its pre-existing fragility.

#### `tests/component/core/test_monitor.py`

**New class** `TestAst1867ProviderBalanceOutage`. Each node patches `monitor_mod.get_active_llm_provider` → `lambda: "deepseek"`, `monitor_mod.get_deploy_label` → `lambda: "local"`, `monitor_mod._resolve_candidate_last_name` → `lambda cid: "Somerset"` (isolates from the pre-existing `TestAutoRunErrorSubjectPrefix` drift), and `send_email` via `_stub_alert` (whose `list_log_entries` stub is replaced by a `MagicMock` in M1 to prove no log dump).

**M1** `test_subject_names_provider_and_body_is_short` — call `provider_balance_outage("select_job_page", "b-1", {"total_processed": 1, "total_passed": 0, "total_failed": 0, "total_errors": 0}, {"error": REFUSAL_ERR, "held": 2}, "cand-1")`. Assert subject `== "[local/Somerset] deepseek insufficient balance — select_job_page stopped | b-1"`; body lines `== ["Provider: deepseek", f"Refusal: {REFUSAL_ERR}", "Task: select_job_page   Batch: b-1", "Processed: 1  Passed: 0  Failed: 0  Errors: 0", "Held (state unchanged): 2", "Entity state was held; the task stays enabled and resumes once provider credit is restored."]`; `to == ASTRAL_CONFIG["support_email"]`; `database.list_log_entries` not called.

**M2** `test_held_line_omitted_when_zero` — `outage={"error": REFUSAL_ERR, "held": 0}` → no line starting `"Held"`.

**M3** `test_logs_when_send_email_returns_false` — `send_email` → `False`; asserts no raise (mirror `TestAutoRunError`).

**M4** `test_swallows_unexpected_errors` — `get_active_llm_provider` raises `ValueError`; asserts no raise, `send_email` not called.

#### Bible entries (Betty's wording; content required)

- **`docs/test-bible/core/dispatcher.md`** — new `### AST-1867 · AST-1870 (qa-fix bug-repro — provider balance refusal as one batch-level outage)` in the AST-1847 section shape: parent/product/gap line (product `144b8850`), contract sentence (ctx `provider_balance_outage`; skip remaining entities/chunks; loop stop; INTERRUPTED; outage alert replaces `auto_run_error`; breaker not called and non-COMPLETED rows invisible to `get_recent_ledger_summaries`), sequencing-deviation line (product first; red at `fbe9486e`, green at `144b8850`), Area/Source/Component tests table for D1–D7 (D1 marked **bug-repro**), **Broken / obsolete:** none in dispatcher, **Integration:** none, `## QA test manifest` with the narrowed run below.
- **`docs/test-bible/core/roster.md`** — new `### AST-1867 · AST-1870` table: R3, R4; **Flipped:** R1, R2 (old `total_errors == 1` → held contract). Cross-link the AST-897 row in `docs/test-bible/utils/llm_external.md` (class-level reference there stays valid — no edit needed; that file is out of AST-1870's scope).
- **`docs/test-bible/core/monitor.md`** — new `### AST-1867 · AST-1870` table: M1–M4; note AUTO error alert (`auto_run_error`) unchanged.

**Narrowed run (manifest):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_dispatcher.py::TestAst1867ProviderBalanceOutage \
  tests/component/core/test_dispatcher.py::TestDispatchOne::test_auto_run_error_on_auto_failures \
  tests/component/core/test_roster.py::TestAst1867BalanceHeldCounting \
  tests/component/core/test_roster.py::TestAst897HoldStateOnBalanceRefusal \
  tests/component/core/test_monitor.py::TestAst1867ProviderBalanceOutage \
  tests/component/core/test_monitor.py::TestAutoRunError \
  -q
```

**`[bug-repro]`:** `tests/component/core/test_dispatcher.py::TestAst1867ProviderBalanceOutage::test_bug_repro_balance_refusal_one_call_interrupted_outage_alert`.

### Blast radius

- **Tests only.** Only R1/R2 change existing assertions; everything else is additive.
- **Pre-existing drift on this tip (not caused by AST-1867, present at ftr base `fbe9486e`; out of AST-1870 scope — flag only):** `TestCircuitBreaker::*` (3) call `_check_circuit_breaker(..., False)` with 4 args vs the 3-arg product (`TypeError`); `TestAutoRunErrorSubjectPrefix::{test_local_env_with_candidate_last_name, test_eu_west_preserves_case, test_unset_env_with_candidate_last_name}` fail on subject assertions. Also `TestDispatchOne::test_auto_run_error_on_auto_failures` passes by accident: its 5-param `_bump` raises `TypeError` against the 6-arg `_run_dispatch_loop` call, the run ends `FAILED` with `+1` error, and the alert still fires. New nodes avoid all three (patch the breaker; 6-param loop fakes; direct patches for deploy label / last name).
- **Consult batch paths** (`prefilter_company` etc.) are not covered — AST-1867 D5 leaves them unwired; do not add tests asserting outage behavior there.
- **Breaker "future lookbacks"** rely on the existing `get_recent_ledger_summaries` `status = 'COMPLETED'` filter (`src/data/database.py`); no database test is added (outside scope — D1 plus D6 prove the run is written non-COMPLETED and the breaker isn't called).

### What must still hold

- AST-897 hold assertions (`transition.assert_not_called()`, `state_held`, `_save_company` not called) stay in R1/R2 and every other `TestAst897HoldStateOnBalanceRefusal` node unchanged.
- AST-1189 call-budget holds count `total_errors: 1` (R4).
- Ordinary AUTO error runs still send `auto_run_error` (D7, `TestAutoRunError`).
- Non-refusal batches call the provider for every entity (D4).
- No test edits to `docs/test-bible/utils/llm_external.md` or any file outside AST-1870's scope.

## Joan fix-board — AST-1870

Gap child for Betty’s AST-1867 `TESTS: REVISE`: component tests + `docs/test-bible/core/{roster,dispatcher,monitor}.md` only (no `src/**`). The plan locks behavior already triaged **CANON: OK** on AST-1867 (`provider_balance_outage`, held counting, INTERRUPTED, outage alert vs `auto_run_error`, breaker skip, D1 call-budget guard). No directive or pattern amendment is proposed; bible contract text is descriptive of that product, not a new carve-out. Same shape as AST-1848 after AST-1847.

BEGIN-VERDICT

```
[board-joan]  CANON: OK
```

END-VERDICT

```text
AST-1870 board-joan done — CANON: OK.
```

## Radia review — AST-1870

[code-rubric]  
**Ticket:** AST-1870  
**Publish ref:** `8c4d2a5d25bf74ebc6d52c710655df15d7a50445` (`origin/sub/AST-1860/AST-1870-provider-balance-outage-tests`)  
**Diff base:** `727b386d88491bc623663c6af47021b454bdf3a6` (`origin/ftr/AST-1860-provider-balance-outage`, includes AST-1867 product @ merge)  
**Corpus:** `docs/canon-index.md` absent on tip; Joan fix-board **CANON: OK** (test/bible only, no new statute).  
**Overall:** CLEAN  

**Status gate:** **Tests Passed** (assignee Ada). Proceed.

---

## Fix-specific checks

### [bug-repro] — OK

**Node:** `tests/component/core/test_dispatcher.py::TestAst1867ProviderBalanceOutage::test_bug_repro_balance_refusal_one_call_interrupted_outage_alert` (first-line `[bug-repro]` in body).

**Verdict:** Asserts **concrete To-be behavior**, not presence-only:

| Pin | Assertion |
|-----|-----------|
| One provider call / no re-claim storm | `run_select_job_page_dispatch.await_count == 1`, `get_new_company_batch.call_count == 1` (vs pre-fix 3×3=9) |
| Release skipped entities | `clear_company_batch` once with `bid-1867` |
| Ledger contract | final `update_dispatch_ledger` kwargs: `status == "INTERRUPTED"`, `(total_processed, total_errors) == (1, 0)` |
| Alert routing | `auto_run_error` not called; `provider_balance_outage` once with `task_key`, batch id prefix, `args[3] == {"error": REFUSAL_ERR, "held": 1}`, `candidate_id` |
| Breaker | `_check_circuit_breaker` patched and `assert_not_called()` |

Stack is real (`_dispatch_one` → loop → `_run_unified` → `consult` → `run_company_task`); only AST-1842 held return + DB/monitor edges stubbed. `provider_balance_outage` mock uses `raising=False` so pre-fix fails on **9==1**, not missing attribute — matches Betty’s red@`fbe9486e` / green@`144b8850` thread and Ada’s test-fix red→green.

**D3 note (advisory, not repro defect):** chunk test stubs `consult.run_consult_task` to return top-level `failure_class` — exercises dispatcher chunk short-circuit; live `evaluate_jd` normalization may not pass `failure_class` until consult changes (AST-1867 D5). Plan names D3 intentionally as dispatcher unit coverage.

### ## What must still hold — OK

| Item | Check |
|------|--------|
| Other `TestAst897HoldStateOnBalanceRefusal` nodes | Diff touches only R1/R2 assertions; `transition.assert_not_called()` retained |
| AST-1189 call-budget guard | **R4** `test_call_budget_hold_still_counts_error` parametrized `select_job_page` + `jobs_found`: `total_errors == 1`, `"total_held" not in out`, `transition.assert_not_called()` |
| Ordinary errors still call every entity | **D4** `await_count == 3`, no `provider_balance_outage` in ctx |
| `auto_run_error` path | Plan **D7** unchanged; manifest includes `TestDispatchOne::test_auto_run_error_on_auto_failures` |
| No edits outside ticket test/bible scope (product) | `git diff … -- src/` empty |
| `llm_external` bible | Not in diff |

---

## Canon scores

Frozen **Canon Scope:** no directive ids (gap test ticket). Joan **CANON: OK**.

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| *(frozen list empty)* | — | — | Board CANON: OK; bible describes AST-1867 product already triaged |

**Worst grade:** none → **CLEAN**.

---

## Column diff vs plan stage

`no plan-stage per-id scores attached` — Joan `[board-joan] CANON: OK` only; plan-fix nodes R1–R4, D1–D6, M1–M4 and three bible sections match diff on tip.

---

## Plan fidelity (§5.4)

- **Roster:** R1/R2 flipped to `total_errors==0`, `total_held==1`, `failure_class`; R3 select_job_page + no `_warn_company`; R4 D1 guard with local `PROVIDER_CALL_BUDGET` import (documented merge-tree rationale).
- **Dispatcher:** Full `TestAst1867ProviderBalanceOutage` per plan; `_edges` avoids breaker arity drift and pre-fix missing `provider_balance_outage`.
- **Monitor:** M1–M4 exact subject/body lines, no `list_log_entries`, error swallow paths.
- **Bible:** `roster.md`, `dispatcher.md`, `monitor.md` gain **AST-1867 · AST-1870** sections + narrowed manifest (23 nodes per Ada).

**Cross-ticket scope:** Diff also includes `a927666d` — `TestAst1864RunIdStamp` + `docs/test-bible/core/tracker.md` (**AST-1864** on `ftr/AST-1853`, not on dev). **Not** in AST-1870 Component/Technical scope; standard **`merge-tests` / `origin/tests` carry** (Susan: Chuckles owns separation). **Not fix-now** on this ticket.

---

## Frame diff

(none)

---

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **Sibling test carry:** `tests/component/core/test_tracker.py` + `docs/test-bible/core/tracker.md` (~AST-1864) ride this publish ref; exclude from AST-1870 manifest/accounting when Chuckles splits or documents carry.
- **Pre-existing module reds:** Plan blast radius documents `TestCircuitBreaker` / `TestAutoRunErrorSubjectPrefix` / accidental D7 pass — unchanged; Ada’s 69-fail-on-full-module = `origin/dev` set.
- **Chuckles routing:** Mini-parent **AST-1860** with live `ftr` (not Done-orphaned). **PROCEED** → **Review Posted** → clean-review shortcut → **User Testing**; rollup with AST-1867 already on `ftr` @ `727b386d`.

---

## What's solid

- Repro pins the incident shape (multi-run loop bounded by `max_runs=3`) that would spam 402s pre-fix.
- R4 directly guards Susan-approved D1 (balance-only held counting).
- Bible manifest is narrowed and names `[bug-repro]` explicitly.
- Test-only diff atop merged product — appropriate gap-child shape.

---

## Recommended actions

Chuckles: append artifact, `docs(AST-1870): Radia review — clean`, post slim upshot, **Review Posted** → **User Testing** (clean shortcut). Keep AST-1864 carry visible in merge/rollup notes only.

`context_tokens≈9500`

---

### Slim upshot (Chuckles → Linear `--as radia`)

```
[code-rubric] PROCEED (Commit: 8c4d2a5d) repro pins outage contract
```

#### Chuckles disposition (AST-1870)

Clean review: Review Posted → User Testing via the clean-review shortcut (resolve-child skipped). AST-1867's product fix is on ftr @ 727b386d, so the tests run green on ftr without a scratch overlay.

origin/tests carry: Betty's merge-tests brought `a927666d` (AST-1864 TestAst1864RunIdStamp + tracker bible). AST-1864's product is on in-flight ftr/AST-1853, not dev; 3 of its 5 tests are red until AST-1853 lands. Left in place: reverting it here would make git drop those tests when AST-1853 later merges, and removing it from history would need a cherry-pick. Not part of this ticket's manifest.

## Threads (generated — epic_registry mirror)

_(generated from epic registry — do not hand-edit; edits are overwritten)_

### Team

| Agent | Role | Thread |
|--------|-------|--------|
| Ada | engineer | `/home/susan/.cursor/chats/173b1605a3fe684e671a65587ccf1ad3/7a228e39-30aa-4e4a-91c6-878710246823/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/a92930ec-b8a2-491e-a303-a327192e2ba2/store.db` |
| Radia | review | `/home/susan/.cursor/chats/173b1605a3fe684e671a65587ccf1ad3/2f1595e6-8eef-4217-95ef-356053ca7635/store.db` |

### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-1860 (parent) | ftr/AST-1860-provider-balance-outage |
| AST-1867 | sub/AST-1860/AST-1867-provider-balance-outage |
| AST-1870 | sub/AST-1860/AST-1870-provider-balance-outage-tests |

**Epic worktree:** `astral-AST-1860/` — one active sub checked out at a time.
