# AST-882 — Prefilter one-retry then ERROR_PREFILTER

- **Linear:** [AST-882 — Prefilter one-retry then ERROR_PREFILTER](https://linear.app/astralcareermatch/issue/AST-882/prefilter-one-retry-then-error-prefilter-failed-prefiter-companies-are)
- **Parent:** [AST-881 — failed prefiter companies are not getting transitioned to an error state](https://linear.app/astralcareermatch/issue/AST-881/failed-prefiter-companies-are-not-getting-transitioned-to-an-error)
- **Publish ref:** `origin/sub/AST-881/AST-882-prefilter-one-retry-error`

Prefilter technical failures already have the right *dest* map for a second strike (`HOMEPAGE_READY` → `WEBSITE_FOUND_RETRY`, `WEBSITE_FOUND_RETRY` → `ERROR_PREFILTER`), but companies that land in `WEBSITE_FOUND_RETRY` are never re-claimed by the prefilter primary dispatch row. `dispatch_claim_states("HOMEPAGE_READY", "company")` looks for a name-convention companion `HOMEPAGE_READY_RETRY`, which does not exist; the configured holding state is `COMPANY_STATES["HOMEPAGE_READY"]["retry_state"]` = `WEBSITE_FOUND_RETRY`. Meanwhile `fetch_website` on `WEBSITE_FOUND` *does* claim `WEBSITE_FOUND_RETRY` via naming, re-scrapes, promotes back to `HOMEPAGE_READY`, and the same companies loop forever under monitor alerts. This ticket closes that loop: one automatic prefilter retry, then terminal `ERROR_PREFILTER`, without changing clean evaluate outcomes or redesigning fetch_website infra-vs-site fail routing.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Honor registry `retry_state` in `dispatch_claim_states` so `HOMEPAGE_READY` claims `WEBSITE_FOUND_RETRY` | utils |
| `src/core/roster.py` | Align `_prefilter_fail` with batch second-strike dest; leave not-ready `WEBSITE_FOUND_RETRY` alone for fetch_website; debug_index for retry vs error | core |
| `src/core/gazer.py` | In `fetch_website_batch`, skip (no state change) companies already in `WEBSITE_FOUND_RETRY` that have `homepage_text` — leave them for prefilter second strike | core |

**Verify only (Betty / qa-child — engineer does not edit in build-child):**

| File | Change |
|------|--------|
| `tests/component/utils/test_config.py` | Assert `dispatch_claim_states("HOMEPAGE_READY", "company") == ["HOMEPAGE_READY", "WEBSITE_FOUND_RETRY"]`; existing `WEBSITE_FOUND` companion claim unchanged |
| `tests/component/core/test_roster.py` | Second-strike from `WEBSITE_FOUND_RETRY` → `ERROR_PREFILTER` via batch fail path; `_prefilter_fail` respects current state; not-ready WFR does not → `CANNOT_READ_WEBSITE` |
| `tests/component/core/test_gazer.py` | Homepage-ready WFR skipped (state unchanged); infra retry without homepage_text still → retry/fail per AST-854 |
| `tests/component/data/database/test_dispatch_tasks.py` | Primary `prefilter`/`HOMEPAGE_READY` row claims WFR entities without a separate WFR dispatch row (AST-745 companion pattern) |

**Out of scope:** new company states; one-time migration of companies already stuck in retry; LLM grade quality; fetch_website infra-vs-site classification (`_fetch_website_fail_destination`); successful evaluate routing (`PREFILTER_PASSED` / `PREFILTER_FAILED` / `NO_PREFILTER_JOBLISTS`); monitor email formatting; UI.

---

## Stage 1: Companion claim via registry `retry_state`

**Done when:** A primary `prefilter` dispatch row with `trigger_state=HOMEPAGE_READY` claims companies in both `HOMEPAGE_READY` and `WEBSITE_FOUND_RETRY`. `fetch_website` on `WEBSITE_FOUND` still claims `WEBSITE_FOUND` + `WEBSITE_FOUND_RETRY`. Job claim companions (`VALID_TITLE` / `VALID_TITLE_RETRY`, etc.) are unchanged.

1. In `src/utils/config.py`, replace the body of `dispatch_claim_states` (currently ~lines 1289–1303) with logic that:

   - Returns `[]` when `trigger_state` is `None` or blank (unchanged).
   - Returns `[ts]` when `ts.endswith("_RETRY")` (unchanged — retry holding rows claim only themselves).
   - Otherwise, for `entity_type == "job"`: if `(JOB_STATES.get(ts) or {}).get("retry_state")` is a non-empty string present in `JOB_STATES`, return `[ts, that_retry]`. Else fall back to existing name-convention `f"{ts}_RETRY"` when that key exists in `JOB_STATES`. Else `[ts]`.
   - For `entity_type == "company"`: same pattern against `COMPANY_STATES` (prefer `retry_state`, else `f"{ts}_RETRY"` name convention, else `[ts]`).
   - Any other `entity_type`: return `[ts]`.

   ⚠️ **Decision:** Prefer registry `retry_state` over name convention when both could apply. Jobs today set `retry_state` to the same `*_RETRY` name, so behavior is identical. Companies on `HOMEPAGE_READY` set `retry_state` to `WEBSITE_FOUND_RETRY` (not `HOMEPAGE_READY_RETRY`) — that is the prefilter gap this stage closes. Do **not** re-introduce a separate `dispatch_task` row for `prefilter`/`WEBSITE_FOUND_RETRY` (AST-702 deleted it; AST-745 forbids auto-seeding companions).

2. Do not change `COMPANY_STATES`, `ROSTER_CONFIG["prefilter"]`, or `company_state_transitions` in this stage — dest strings and edges already exist (`HOMEPAGE_READY`→`WEBSITE_FOUND_RETRY`, `WEBSITE_FOUND_RETRY`→`ERROR_PREFILTER`, `ERROR_PREFILTER` has no `batch_criteria`).

---

## Stage 2: Prefilter fail routing and readiness split

**Done when:** A company claimed while `state=HOMEPAGE_READY` that hits a retryable technical failure lands in `WEBSITE_FOUND_RETRY`. The same company claimed while `state=WEBSITE_FOUND_RETRY` that fails again (retryable or hard) lands in `ERROR_PREFILTER`. Single-company `_prefilter_fail` matches that dest map. Not-ready rows already in `WEBSITE_FOUND_RETRY` are left untouched for `fetch_website`. With `debug=True`, each fail path emits a `debug_index` header naming the destination.

1. In `src/core/roster.py`, change `_prefilter_fail` so destination uses the company's **current** state, not "always retry if retryable":

   ```python
   def _prefilter_fail(
       short_name: str,
       cfg: Dict[str, Any],
       result: Dict[str, Any],
       error: str,
       *,
       api_result: Optional[Dict[str, Any]] = None,
   ) -> Dict[str, Any]:
       company = get_company(short_name) or {}
       current_state = (company.get("state") or "").strip()
       retryable = api_result is None or (
           not api_result.get("success") and _prefilter_api_failure_is_retryable(api_result)
       )
       if not retryable:
           dest = cfg["error_state"]
       else:
           dest = _prefilter_batch_fail_dest(current_state, cfg) or cfg["error_state"]
       transition_company_state(short_name, dest)
       result["error"] = error
       result["state"] = dest
       result["decision"] = "RETRY" if dest == cfg["retry_state"] else "ERROR"
       return result
   ```

   ⚠️ **Decision:** Hard/system failures (non-retryable API body absence) still go straight to `ERROR_PREFILTER` even from `HOMEPAGE_READY` — same as today's `_prefilter_fail` when `retryable` is false. Parent contract: further failure **from the retry holding state** always errors; first-strike hard errors may still terminal without consuming the retry. Keep that asymmetry.

2. Keep `_prefilter_batch_fail_dest` semantics as today (already correct):

   - State with `COMPANY_STATES[st].retry_state` (e.g. `HOMEPAGE_READY`) → `cfg["retry_state"]` (`WEBSITE_FOUND_RETRY`).
   - State equal to `cfg["retry_state"]` (`WEBSITE_FOUND_RETRY`) → `cfg["error_state"]` (`ERROR_PREFILTER`).
   - Empty / other → `cfg["error_state"]`.

   Do not rewrite this helper unless a literal bug is found while wiring step 1; call it from `_prefilter_fail` instead of duplicating the branch table.

3. In `prefilter_company_batch`, change the not-ready loop so:

   - If `company.get("state") == cfg["retry_state"]` (`WEBSITE_FOUND_RETRY`) and not homepage-ready: **do not** call `transition_company_state(..., "CANNOT_READ_WEBSITE")`. Leave the row in `WEBSITE_FOUND_RETRY` (fetch_website owns scrape retry). Optionally emit `debug_index` outcome `readiness skip — leave WEBSITE_FOUND_RETRY for fetch_website`. Count these toward `skipped` (or a distinct tally merged into return `skipped`) so consult error math does not treat them as silent drops.
   - If state is `HOMEPAGE_READY` (or other non-retry) and not homepage-ready: keep today's behavior — `CANNOT_READ_WEBSITE` + notes `"No homepage_text in company_data"`.

4. In `_run_batch_company_prefilter` / `_transition_prefilter_batch_failures` paths that already call `_prefilter_batch_fail_dest`, when `debug=True`, emit `debug_index` per company with:

   - `func="roster._run_batch_company_prefilter"` (or the existing func name already used on that path — stay consistent with current headers in that function).
   - `identifier=short_name`
   - `outcome` including the destination state string, e.g. `technical fail -> WEBSITE_FOUND_RETRY` or `technical fail -> ERROR_PREFILTER`
   - working detail line with ` | ` prefix naming the failure class (`do_task` / hydrate / missing id / process exception) — §1.5.1 style D. Only when `debug=True`.

5. Do not change `_apply_prefilter_decoded_company_outcome` pass/fail/no-pjl routing.

---

## Stage 3: Stop fetch_website from recycling prefilter retries

**Done when:** A company in `WEBSITE_FOUND_RETRY` that already has non-empty `homepage_text` is not promoted to `HOMEPAGE_READY` by `fetch_website_batch`. Companies in `WEBSITE_FOUND_RETRY` without homepage_text still follow AST-854 infra/site routing unchanged.

1. In `src/core/gazer.py` `fetch_website_batch`, at the start of `_fetch_one_inner` (after reading `short_name` / `company_state`), add:

   ```python
   cd = company.get("company_data") or {}
   if (
       company_state == cfg["retry_state"]
       and len((cd.get("homepage_text") or "").strip()) > 0
   ):
       if debug:
           _log.debug_index(
               func="gazer.fetch_website_batch",
               index=company_index,
               total=company_total,
               identifier=_gazer_company_identifier(company),
               outcome="skip — homepage_text present; leave for prefilter second strike",
           )
       return  # no transition; dispatcher clear_company_batch releases the claim
   ```

   Use `cfg["retry_state"]` (already on `GAZER_CONFIG["fetch_website"]`) — do not hardcode the string in the condition beyond what config already holds.

   ⚠️ **Decision:** This is not a redesign of `_fetch_website_fail_destination` / infra-vs-site classification (AST-854 stays). Prefilter failures leave `homepage_text` in place when moving `HOMEPAGE_READY` → `WEBSITE_FOUND_RETRY`; scrape infra failures typically do not. Skipping the homepage-ready subset prevents fetch_website from winning the shared-state race and re-opening the prefilter loop. Parent boundary forbids redesigning infra retry — this only declines to re-scrape rows that already have homepage content.

2. Do not remove `WEBSITE_FOUND` → companion `WEBSITE_FOUND_RETRY` claim behavior. Infra retries without text must still be claimable by fetch_website.

---

## Stage 4: Compile / smoke (no product expansion)

**Done when:** Touched modules compile; a one-shot in-process check shows first-strike dest `WEBSITE_FOUND_RETRY` and second-strike dest `ERROR_PREFILTER` for the batch fail helper + claim-states list.

1. From repo root:

   ```bash
   .venv/bin/python -m compileall -q src/utils/config.py src/core/roster.py src/core/gazer.py
   ```

2. Smoke (do not commit the smoke script; use a REPL or `debug/spikes/AST-882/` if needed):

   ```python
   from src.utils.config import dispatch_claim_states, ROSTER_CONFIG
   from src.core import roster as r
   cfg = ROSTER_CONFIG["prefilter"]
   assert dispatch_claim_states("HOMEPAGE_READY", "company") == [
       "HOMEPAGE_READY", "WEBSITE_FOUND_RETRY",
   ]
   assert dispatch_claim_states("WEBSITE_FOUND", "company") == [
       "WEBSITE_FOUND", "WEBSITE_FOUND_RETRY",
   ]
   assert r._prefilter_batch_fail_dest("HOMEPAGE_READY", cfg) == "WEBSITE_FOUND_RETRY"
   assert r._prefilter_batch_fail_dest("WEBSITE_FOUND_RETRY", cfg) == "ERROR_PREFILTER"
   ```

3. Stop. Betty owns tests; do not edit `tests/` or `docs/test-bible/**`.

---

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree line; publish each to `origin/sub/AST-881/AST-882-prefilter-one-retry-error` per build-child.
- Do not add files, states, or dispatch seed rows not listed above.
- Ambiguity or codebase drift → stop and comment on **AST-881** with the Stage N blocked template from plan-child.

---

## Self-Assessment

**Scope:** Single-Component — claim-state helper in config plus prefilter fail/readiness paths in roster and a one-branch skip in gazer; no UI, no schema, no new states.

**Conf:** high — dest helper and transitions already encode one-retry-then-error; the bug is companion claim naming + fetch_website recycling homepage-ready WFR; both have clear existing patterns (AST-745 companion claim, AST-854 fail dest).

**Risk:** Medium — shared `WEBSITE_FOUND_RETRY` between prefilter and fetch_website means a mistake in the homepage_text skip or not-ready leave-alone could strand scrape infra retries or re-open the loop; success evaluate paths are untouched.

## Rules check (§8)

- **§1.3 DRY:** `_prefilter_fail` calls `_prefilter_batch_fail_dest` — no second dest table.
- **§2.1 config:** dest and retry strings stay in `ROSTER_CONFIG` / `COMPANY_STATES` / `GAZER_CONFIG`; claim companion reads registry `retry_state`.
- **§2.4 / §2.6:** still claim → process → clear; no daisy-chain inside one run beyond existing batch helper; `ERROR_PREFILTER` remains terminal (no batch_criteria).
- **§3.3:** utils change stays pure; core-only roster/gazer edits.
- **§1.5.1:** debug lines gated on `debug=True` with index headers + ` | ` detail.
- **§3.6:** no spike artifacts committed under `docs/features/`.
