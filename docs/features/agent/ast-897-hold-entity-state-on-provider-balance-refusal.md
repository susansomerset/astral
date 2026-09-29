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
