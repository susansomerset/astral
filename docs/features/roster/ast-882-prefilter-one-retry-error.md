<!-- linear-archive: AST-882 archived 2026-07-29 -->

## Linear archive (AST-882)

**Archived:** 2026-07-29  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-882/prefilter-one-retry-then-error-prefilter-failed-prefiter-companies-are  
**Status at archive:** Archive  
**Project:** Astral Roster  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-881 — failed prefiter companies are not getting transitioned to an error state  
**Blocked by / blocks / related:** parent: AST-881

### Description

## What this implements

When a company fails prefilter for a retryable technical reason, it must move to the established prefilter retry holding state once; when it fails again while already in that retry state, it must move to the established prefilter error state and leave the automatic prefilter claim pool. Batch summaries and monitor auto-run error reporting must reflect exhausted retries rather than an unbounded retry pool of the same companies. With debug enabled, each company outcome must record what was found and what state was written (retry vs error) per the backend debug contract.

## Acceptance criteria

1. A company that fails prefilter for a retryable technical reason while in the primary prefilter-eligible state is observable in `WEBSITE_FOUND_RETRY` afterward.
2. The same company, claimed again from `WEBSITE_FOUND_RETRY` and failing prefilter again, is observable in `ERROR_PREFILTER` afterward — not still in `WEBSITE_FOUND_RETRY`.
3. Companies in `ERROR_PREFILTER` are not re-claimed by automatic prefilter dispatch on later scheduler loops.
4. Re-running prefilter against a set that previously produced repeated monitor alerts for the same technical failures no longer leaves those companies cycling forever in `WEBSITE_FOUND_RETRY`; after one retry they are in `ERROR_PREFILTER`.
5. Companies that evaluate cleanly still reach the same pass / fail / no-joblists outcomes as today.

## Boundaries

* Does not change successful evaluate outcomes: `PREFILTER_PASSED`, `PREFILTER_FAILED`, or `NO_PREFILTER_JOBLISTS`.
* Does not redesign `fetch_website` infra retry or other roster stages’ retry/error maps.
* Does not require fixing LLM grade quality or malformed vector labels as a deliverable.
* Does not add new company states beyond the established prefilter retry and error states.
* Does not require a one-time production data migration unless Susan later asks for cleanup of companies already stuck in retry.

## Notes for planning

* Product contract was established in AST-606 / AST-702: first-strike retryable technical failure → `WEBSITE_FOUND_RETRY`; second strike from retry → `ERROR_PREFILTER`.
* Primary domain: roster prefilter failure routing and any batch path that currently re-applies retry instead of error on second strike. Config/dispatch seeds for the legitimate single retry must keep working.
* Parent definition lives on [AST-881](https://linear.app/astralcareermatch/issue/AST-881/failed-prefiter-companies-are-not-getting-transitioned-to-an-error) Description (Chuckles block above Original brief).

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at dispatch-parent. Engineers publish to `origin/<sub-ref>` — never Linear `gitBranchName` when it disagrees.

### Comments

#### radia — 2026-07-13T17:04:14.899Z
**Diff:** `origin/dev...origin/sub/AST-881/AST-882-prefilter-one-retry-error` @ `e8f0414`

### What’s solid
- Stages 1–3 match plan: registry `retry_state` claim companion (HOMEPAGE_READY → WEBSITE_FOUND_RETRY), `_prefilter_fail` → `_prefilter_batch_fail_dest` (one retry then ERROR_PREFILTER), not-ready WFR left alone, `fetch_website_batch` skips homepage-ready WFR.
- Boundaries held — no new states, no evaluate routing / infra-fail redesign; ERROR_PREFILTER has no `batch_criteria`.
- §1.3 / §2.1 / §2.6 / §1.5.1 satisfied; Self-Assessment Scope matches footprint.

### Issues
None.

### Recommended actions
| Action | Item |
|--------|------|
| none (ship) | 0 fix-now · 0 discuss · 0 advisory |

**Doc:** `docs/features/roster/ast-882-prefilter-one-retry-error.md` — `docs(AST-882): Radia review — clean` → `origin/sub/AST-881/AST-882-prefilter-one-retry-error` @ `e8f0414`

#### betty — 2026-07-13T16:58:04.029Z
1. `tests/component/utils/test_config.py::TestAst882DispatchClaimStates` — `HOMEPAGE_READY` claims `WEBSITE_FOUND_RETRY`; `WEBSITE_FOUND` companion unchanged
2. `tests/component/core/test_roster.py::TestAst882PrefilterOneRetryThenError` — `_prefilter_fail` first/second strike; batch do_task fail from WFR → `ERROR_PREFILTER`; not-ready WFR leave-alone
3. `tests/component/core/test_roster.py::TestPrefilterCompany::test_api_failure_and_missing_parsed_response` — revised scrape + `HOMEPAGE_READY` get_company mock
4. `tests/component/core/test_gazer.py::TestAst882HomepageReadyWfrSkip` — homepage-ready WFR skip; bare WFR infra still terminals
5. `tests/component/data/database/test_dispatch_tasks.py::TestAst882HomepageReadyClaimsWfr` — primary `prefilter`/`HOMEPAGE_READY` count+claim unions WFR

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst882DispatchClaimStates \
  tests/component/core/test_roster.py::TestAst882PrefilterOneRetryThenError \
  tests/component/core/test_roster.py::TestPrefilterCompany::test_api_failure_and_missing_parsed_response \
  tests/component/core/test_gazer.py::TestAst882HomepageReadyWfrSkip \
  tests/component/data/database/test_dispatch_tasks.py::TestAst882HomepageReadyClaimsWfr \
  -q
```

`origin/sub/AST-881/AST-882-prefilter-one-retry-error` @ `cdcd3296d2af575ad83e63f375663d6a4556d1f6` (`merge-tests(AST-882): origin/tests c65ac459cbbd4427d2c631ca40abd6fd367aca20`)

Bible shasums on publish ref:
- `docs/test-bible/core/roster.md` `34481ed926819673e7ca55184f05d97923673b9f`
- `docs/test-bible/core/gazer.md` `e1e7bd25ea88e698ec7469005455341a012b94c0`
- `docs/test-bible/utils/config.md` `108a996d02c12c4ad54f2985e1b99f02ba2f8eab`
- `docs/test-bible/data/database/dispatch_tasks.md` `a43455d862a46a6888fcd7196dec3b017afd2d82`

#### hedy — 2026-07-13T16:49:53.821Z
Plan: [`docs/features/roster/ast-882-prefilter-one-retry-error.md`](https://github.com/susansomerset/astral/blob/sub/AST-881/AST-882-prefilter-one-retry-error/docs/features/roster/ast-882-prefilter-one-retry-error.md)

`origin/sub/AST-881/AST-882-prefilter-one-retry-error` @ `01c1f201af8a4180b8bd145dbec77abb30c521c2`

**Self-assessment**
- **Scope:** Single-Component — `dispatch_claim_states` retry_state companion for `HOMEPAGE_READY`, roster fail/readiness alignment, and a homepage_text skip in `fetch_website_batch` so prefilter can take the second strike.
- **Conf:** high — dest map already encodes one-retry-then-error; bug is companion claim naming (`HOMEPAGE_READY_RETRY` vs configured `WEBSITE_FOUND_RETRY`) plus fetch_website recycling homepage-ready WFR.
- **Risk:** Medium — shared `WEBSITE_FOUND_RETRY` between prefilter and fetch_website; wrong skip/leave-alone could strand scrape infra retries or re-open the loop.

---

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

---

## Review (build stub)

**Publish ref:** `origin/sub/AST-881/AST-882-prefilter-one-retry-error`

| Stage | Commit | Summary |
|-------|--------|---------|
| plan | `01c1f20` | Plan doc |
| 1 | `df3f516` | `dispatch_claim_states` honors registry `retry_state` |
| 2 | `7b00291` | `_prefilter_fail` second-strike; WFR not-ready leave-alone; fail debug |
| 3 | `dcb8fd1` | `fetch_website_batch` skips homepage-ready WFR |

**Tip:** `dcb8fd1`

---

## Radia review

**Diff:** `origin/dev...origin/sub/AST-881/AST-882-prefilter-one-retry-error` @ `cdcd329`

### What’s solid

- Stages 1–3 match the plan: `dispatch_claim_states` prefers registry `retry_state` (HOMEPAGE_READY → WEBSITE_FOUND_RETRY) with name-convention fallback for WEBSITE_FOUND; `_prefilter_fail` routes via `_prefilter_batch_fail_dest` (one retry then ERROR_PREFILTER); not-ready WFR left for fetch_website; `fetch_website_batch` skips homepage-ready WFR.
- Boundaries held: no new states, no evaluate routing changes, no `_fetch_website_fail_destination` redesign; ERROR_PREFILTER stays without `batch_criteria`.
- §1.3 / §2.1 / §2.6: single dest helper, config-owned strings, transitions via existing helpers; claim → process → clear unchanged.
- §1.5.1 / §5f: batch fail paths emit `debug_index` + `debug_detail` only when `debug=True`; gazer skip header gated the same way.
- Self-Assessment Scope Single-Component matches footprint; Conf high still fits. Betty tests + bible on publish-ref are expected post-qa.

### Issues

None.

### Recommended actions

| Action | Item |
|--------|------|
| none (ship) | 0 fix-now · 0 discuss · 0 advisory |

**Outcome:** Clean — ready for `resolve-child`.

---

## Resolution (2026-07-13)

**Driven by:** Radia review @ `e8f0414` — 0 fix-now, 0 discuss, 0 advisory.

| Item | Action |
|------|--------|
| **fix-now** | None — no product changes. |
| **discuss** | None. |
| **advisory** | None. |

**§9a dry-run:** `origin/sub/AST-881/AST-882-prefilter-one-retry-error` @ `1cdabf8` merges cleanly into `origin/dev` and `origin/ftr/AST-881-prefilter-retry-to-error`.

---

## Bug: AST-1839 — AUTO retries log WARNING and skip error count; error only after retry fails

- **Linear:** [AST-1839](https://linear.app/astralcareermatch/issue/AST-1839) (fix child of orphaned bug [AST-1828](https://linear.app/astralcareermatch/issue/AST-1828))
- **Publish ref:** `origin/sub/AST-1828/AST-1839-auto-retry-warn-then-error`
- **Scope (Susan, 2026-09-28):** prefilter + the AUTO tasks that **already** have a retry holding — job consult/grade/upshot, `fetch_website`, `parse_job_list`, candidate craft chain. No new holdings for any other task. `src/core/agent.py` only for the envelope-failure flag. The `JO`/`JOB:<n>` decode bug is out.

### As-is

- A Somerset `prefilter_company` AUTO run reported "100 error(s) / 500 processed" and emailed (`monitor.auto_run_error`). Nearly every "error" was a company routed to a retry holding. `consult.run_consult_task` computes prefilter `total_errors = total − passed − failed − skipped`, so every retry-routed company counts, and `dispatcher.py:1443` alerts when `total_errors > 0`. The job-batch branch (`total − passed − failed`), the upshot `errors` counter, and the single-entity grade path (`total_errors: 1` whenever `success` is false) count their retries the same way.
- Retry-routed failures log ERROR: prefilter hydrate/decode use `logger.exception` (`roster.py:1986`, `:2032`), consult hydrate/bad-grades use `logger.exception` (`consult.py:1644`, `:1741`), `parse_job_list` scrape failures use `logger.exception` (`roster.py:1249`, `:1261`), the homepage scrape uses `logger.exception` (`roster.py:1608`), the candidate craft chain uses `logger.error` on every failure (`candidate.py:3668`), and `log_llm_batch_summary` always logs provider errors at ERROR (`logging.py:262`).
- Prefilter never reaches `ERROR_PREFILTER` on a repeat failure. `_prefilter_batch_fail_dest` sends every `HOMEPAGE_READY` failure to `COMPANY_STATES["HOMEPAGE_READY"]["retry_state"]` = `WEBSITE_FOUND_RETRY`. Since AST-1810, `fetch_website` re-scrapes every WFR row back to `HOMEPAGE_READY` and `dispatch_claim_states("HOMEPAGE_READY")` claims `HOMEPAGE_READY_RETRY` (which nothing writes), not WFR. So the company loops HR → WFR → HR indefinitely.
- Rubric-encoded `do_task` (prefilter's `grades_encoded_prefilter_links`) unwraps `agent_payload` at `agent.py:2421` and drops `agent_performance.status`, so a model-reported "source content is the problem" failure can't be told apart from a decode failure.

### To-be

Susan: "Downgrade errors that result in retry to warning, only error in true error case … the whole batch needs a retry: warning. Then, if retry didn't fix it: error."

- **Retry-routed** (destination is a `*_RETRY` holding): log WARNING, not counted in `total_errors`, so no alert email.
- **Out of the holding** (destination is the task's error/terminal state): log ERROR, counted in `total_errors`, emails.
- **Prefilter parsing failures** (do_task failure, hydrate, missing id, per-company decode): first strike goes to a new `HOMEPAGE_READY_RETRY` holding (no re-scrape). Any failure out of `HOMEPAGE_READY_RETRY` goes to `ERROR_PREFILTER`.
- **Prefilter agent-envelope failures** (`agent_performance.status == "failure"`): first strike goes to `WEBSITE_FOUND_RETRY` so `fetch_website` re-scrapes. A second envelope failure after that re-scrape goes to `ERROR_PREFILTER`.

### Repro

Fixture (no DB seed; mock `do_task` + `get_company` / `transition_company_state` as `TestAst882PrefilterOneRetryThenError` already does):

```python
company = {
    "short_name": "acme_com", "state": "HOMEPAGE_READY",
    "company_data": {"homepage_text": "Acme builds rockets.", "nav_links": "[001] https://acme.com/careers"},
    "state_history": [{"from_state": "WEBSITE_FOUND", "to_state": "HOMEPAGE_READY"}],
}
# do_task → {"success": True, "parsed_response": {"companies": [{"company_id": "acme_com", "grades": [{"vector": "JO", ...}]}]}}
# _hydrate_response_jobs_grade_reasons raises ValueError("No rubric criterion matching vector 'JO'")
await consult.run_consult_task("company", "HOMEPAGE_READY", [company], "b1", dispatch_task_key="prefilter_company")
```

- **As-is:** `acme_com` → `WEBSITE_FOUND_RETRY`; summary `total_errors == 1`; ERROR log `company prefilter hydrate`. After `fetch_website` succeeds it returns to `HOMEPAGE_READY` and the same failure repeats with no terminal.
- **To-be:** `acme_com` → `HOMEPAGE_READY_RETRY`; `total_errors == 0`; one WARNING `acme_com -> HOMEPAGE_READY_RETRY [hydrate: …]`. Re-run with `state="HOMEPAGE_READY_RETRY"` → `ERROR_PREFILTER`, `total_errors == 1`, ERROR `acme_com -> ERROR_PREFILTER [hydrate: …]`.
- **Envelope variant:** `do_task` returns `{"success": False, "agent_failure": True, "error": "Agent failure: page is a parked domain"}` → `WEBSITE_FOUND_RETRY`, WARNING, `total_errors == 0`. The same company back at `HOMEPAGE_READY` with a history entry `HOMEPAGE_READY → WEBSITE_FOUND_RETRY` → `ERROR_PREFILTER`, ERROR, `total_errors == 1`.

### Root cause

1. Summary conversion treats "not passed and not failed" as an error, and retry holdings fall into that remainder.
2. Failure-log severity is fixed per call site (`logger.exception` / `logger.error`) instead of following the destination.
3. Prefilter's first-strike holding is the cross-named, fetch-owned `WEBSITE_FOUND_RETRY`. After AST-1810 re-scrapes all of WFR, the second-strike input (`WEBSITE_FOUND_RETRY` → `ERROR_PREFILTER`) is never claimed by prefilter, so a strike is never remembered.
4. `do_task` discards the rubric-encoded envelope status, so prefilter can't route bad-source-content failures on their own.

### Proposed change

**Severity rule used everywhere below:** a destination `d` is a retry holding iff `retry_base(d)` (`src/utils/config.py:206`) is not `None`. Holding → WARNING and not counted. Anything else (error state, terminal fail, `None`) → ERROR and counted. This holds for upshot too, whose TASK_CONFIG `error_state` *is* `PASSED_LIKE_RETRY`, and whose second strike (`FAILED_TECHNICAL`) is not a holding.

⚠️ **Decision — counting:** per-function `retried` key (not a central post-run state re-read). This matches the Technical scope's roster instruction, adds no DB reads, and counts only this run's retry transitions (rows that were merely skipped while sitting in a holding aren't miscounted). No new summary key: dispatcher accumulates only the four `total_*` keys and is out of scope, so retries are simply excluded from `total_errors`.

⚠️ **Decision — log helper per module:** `utils/logging.py` scope is `log_llm_batch_summary` only, so each module gets a two-line helper on its own logger (the module logger name stays correct in app_log):

```python
def _log_fail_dest(entity: Any, dest: Any, reason: str) -> None:
    """Retry holding → WARNING; error/terminal → ERROR (AST-1839)."""
    (logger.warning if retry_base(dest) else logger.error)("%s -> %s [%s]", entity, dest or "-", reason)
```

This is added to `src/core/roster.py` (next to `_warn_company`) and `src/core/consult.py` (next to `_warn_job`). Import `retry_base` from `src.utils.config` in both.

#### 1. `src/utils/config.py`

1. `COMPANY_STATES["HOMEPAGE_READY"]["retry_state"]` → `retry_of("HOMEPAGE_READY")`. Replace the comment above it with `# retry_of("HOMEPAGE_READY"): prefilter parsing-failure holding (AST-1839); prefilter claims it via dispatch_claim_states.`
2. `ROSTER_CONFIG["prefilter"]`: `"retry_state": retry_of("HOMEPAGE_READY")`, and add `"envelope_retry_state": retry_of("WEBSITE_FOUND")`.
3. `company_state_transitions`: add `("HOMEPAGE_READY", retry_of("HOMEPAGE_READY"))` and, from `retry_of("HOMEPAGE_READY")`, edges to `PREFILTER_PASSED`, `PREFILTER_FAILED`, `NO_PREFILTER_JOBLISTS`, `TO_WATCH`, `IGNORE`, `ERROR_PREFILTER`, `CANNOT_READ_WEBSITE`. Keep `("HOMEPAGE_READY", retry_of("WEBSITE_FOUND"))` for the envelope path.

⚠️ **Decision:** no literal `"HOMEPAGE_READY_RETRY": {}` key. Per AST-1805, `{base}_RETRY` registers implicitly through its base (`is_registered_state` / `transition_company_state`), and `WEBSITE_FOUND_RETRY` has no literal key either. The Component scope's "new `COMPANY_STATES` entry" is satisfied by `retry_state` + transitions. No `batch_criteria` is needed: prefilter's `HOMEPAGE_READY` row already claims `HOMEPAGE_READY_RETRY` (`dispatch_claim_states`, `config.py:3592`).

#### 2. `src/core/agent.py` — `do_task`

At the `if isinstance(parsed, dict) and "agent_payload" in parsed:` block (~line 2414), before unwrapping, when `rubric_encoded` and `_agent_performance_status(parsed.get("agent_performance")) == "failure"`:

- `note` = `perf.get("failure_note")` if `perf` is a dict, else `parsed.get("failure_note")`, else `"Agent returned status=failure with no note"`. `err = f"Agent failure: {note}"`.
- Same failure tail as the `envelope_err` branch (~2297–2313): `_warn_hop_no_success(task_key, err)`, store the failure response block (`_audit_response_body(raw_text, parsed, err)`) when `_should_store`, `_close_hop_ledger(success=False, clear_log=True, failure_error=err)`.
- Return `_with_harvest({"success": False, "agent_failure": True, "api_response": …, "parsed_response": None, "error": err, "raw_response": parsed, "timesheet": …})`.

Non-rubric tasks are unchanged (they already fail through `_validate_response_schema`). No other `agent.py` edits.

#### 3. `src/core/roster.py` — prefilter

1. Replace `_prefilter_batch_fail_dest` with:

   ```python
   def _prefilter_batch_fail_dest(
       entity_state: Optional[str], cfg: Dict[str, Any], *,
       short_name: str = "", agent_failure: bool = False,
   ) -> str:
       """HR parsing fail → HR_RETRY; HR envelope fail → WFR once; anything out of a holding → error (AST-1839)."""
       if (entity_state or "").strip() != cfg["input_state"]:
           return cfg["error_state"]
       if not agent_failure:
           return cfg["retry_state"]
       history = (get_company(short_name) or {}).get("state_history") or []
       rescraped = any(
           h.get("from_state") == cfg["input_state"] and h.get("to_state") == cfg["envelope_retry_state"]
           for h in history
       )
       return cfg["error_state"] if rescraped else cfg["envelope_retry_state"]
   ```

2. `_prefilter_fail` (single-company path): pass `short_name=short_name, agent_failure=bool((api_result or {}).get("agent_failure"))` to the helper. `decision` = `"RETRY"` when `retry_base(dest)`, else `"ERROR"`. Log with `_log_fail_dest(short_name, dest, error)`. The hard (non-retryable) branch keeps going straight to `error_state` (AST-882 decision).
3. `_transition_prefilter_batch_failures(companies, cfg, *, debug=False, fail_class="technical fail", agent_failure=False, reason=None) -> int`: compute `dest` via the new helper (passing `short_name` and `agent_failure`), transition, `_log_fail_dest(short_name, dest, f"{fail_class}: {reason}")` when `reason` is not `None`, and **return the count of companies whose `dest` is a retry holding**.
4. `_run_batch_company_prefilter`: accumulate `retried` and return it in every non-balance return dict (`{"passed", "failed", "total", "retried"}`).
   - do_task failure (non-balance): `retried = _transition_prefilter_batch_failures(companies, cfg, fail_class="do_task", agent_failure=bool(result.get("agent_failure")), reason=result.get("error") or "do_task failed")`.
   - hydrate: `logger.exception` → `logger.debug("%s | company prefilter hydrate: %s", batch_id, hydrate_err, exc_info=True)`. Then `retried = _transition_…(companies, cfg, fail_class="hydrate", reason=str(hydrate_err))`.
   - missing id: drop the `_warn_company(mid, "-", …)` loop. `retried += _transition_…(missing_rows, cfg, fail_class="missing id", reason="prefilter batch omitted this id")`.
   - per-company decode: `logger.exception` → `_log_fail_dest(cid, _prefilter_batch_fail_dest(input_company.get("state"), cfg), f"decode: {type(e).__name__}: {e}")` plus `logger.debug(…, exc_info=True)`. Then `retried += _transition_prefilter_batch_failures(bad_rows, cfg)` (no `reason`, so already logged).
   - Balance-refusal return is unchanged (state held; out of scope).
5. `prefilter_company_batch`: the not-ready skip compares against `cfg["envelope_retry_state"]` (was `cfg["retry_state"]`), keeping its meaning ("WFR belongs to fetch_website"). `HOMEPAGE_READY_RETRY` rows keep `homepage_text`; if one ever lacks it, it takes the existing `CANNOT_READ_WEBSITE` path (edge added in §1). `batch_result` already carries `retried` through. The `if not ready:` return adds `"retried": 0`.
6. `_apply_prefilter_decoded_company_outcome`: no change (`cfg.get("retry_state")` in its debug line now names `HOMEPAGE_READY_RETRY`, which is correct).

**No-loop proof (HR → WFR → HR):** HR → WFR happens only on an envelope failure *and* only when history has no prior `HOMEPAGE_READY → WEBSITE_FOUND_RETRY` edge. That edge is written by that same transition, so each company takes it at most once. After the one re-scrape, a second envelope failure from HR goes to `ERROR_PREFILTER`. A parsing failure from HR goes to `HOMEPAGE_READY_RETRY`, and every failure from `HOMEPAGE_READY_RETRY` (parsing or envelope) goes to `ERROR_PREFILTER` (helper first branch). A company therefore reaches at most HR → WFR → HR → HR_RETRY → `ERROR_PREFILTER`, a bounded chain. Legacy rows that already looped under the old routing have that history edge, so their next envelope failure errors immediately.

#### 4. `src/core/roster.py` — `fetch_website` and `parse_job_list`

1. `scrape_company_homepage_content` (~1608): `logger.exception` → `logger.warning` (same message and args, add `exc_info=True`). Every fetch_website scrape failure lands in `WEBSITE_FOUND_RETRY` or its `fail_state` `CANNOT_READ_WEBSITE`; the task has no `error_state`. fetch_website counts are unchanged: retries already count as `failed`, not errors (`gazer.py:557`).
2. `_save_parse_dispatch_failure`: after computing `fail_state`, `_log_fail_dest(short_name, fail_state, notes or response_type)`.
3. `run_parse_job_list_dispatch` except blocks (~1249, ~1261): `logger.exception` → `logger.debug(…, exc_info=True)` (the helper above now logs the outcome at the right level).
4. `parse_job_list_batch`: drop `retry_state` and `terminal_fail_state` from `ok_states` (→ `{pass_state}`). In `_one`: `result.get("state") == parse_cfg["retry_state"]` and no `error` → `retried += 1`. Pass state → `passed += 1`. Anything else (incl. `COULD_NOT_PARSE_JOBLIST`, reached only out of the holding) → `errors += 1`. Return `{"passed", "failed": 0, "total", "errors", "retried"}`. The `run_consult_task` branch keeps reading the explicit `errors`.

#### 5. `src/core/consult.py`

1. `_transition_batch_consult_failures(task_key, job_rows, error_state, reason: Optional[str] = None) -> int`: per row compute `dest`, `_log_fail_dest(aid, dest, reason)` when `reason` is not `None`, transition as today, **return the count with `retry_base(dest)`**.
2. `_run_batch_consult`:
   - Envelope failure (non-balance): drop the `_warn_job` loop. `retried = _transition_batch_consult_failures(task_key, jobs, error_state, reason=result.get("error") or "do_task failed") if error_state else 0`. Add `"retried": retried` to the return.
   - Hydrate: `logger.exception` → `logger.debug(…, exc_info=True)`. Drop the `_warn_job` loop, use `reason=f"hydrate: {e}"`, and return `"retried"`.
   - Missing: keep `missing_dest_counts`, drop `_warn_job(…, "omitted from response")`, `retried = _transition_…(task_key, missing_rows, error_state, reason="omitted from response")`.
   - process_fn exception: `logger.exception` → `_log_fail_dest(aid, _consult_batch_fail_dest(input_job.get("state"), error_state), f"process_fn {type(e).__name__}: {e}")` + `logger.debug(…, exc_info=True)`. Then `retried += _transition_…(task_key, bad_rows, error_state)` (no reason).
   - Final return adds `"retried": retried`. Wrappers (`qualify_job_listings`, `qualify_meteorite`, `evaluate_jd_batch`, `evaluate_meteorite_batch`, `_consult_scored_dispatch_batch_encoded`) already return or spread the dict unchanged.
3. `_run_analysis_upshot_batch`: at the four `_consult_batch_fail_dest` sites (no company, no live content, do_task fail, non-dict parse), replace `_warn_job(aid, dest or "-", …)` with `_log_fail_dest(aid, dest, …)` and `errors += 1` with `if not retry_base(dest): errors += 1`. The `NEED_WEBSITE_CONTENT` and balance-hold sites are unchanged.
4. `render_verdict` `IncompleteGradeSetError` branch: `_warn_job(astral_job_id, dest or "-", str(e))` → `_log_fail_dest(astral_job_id, dest, str(e))`. `_fail` (straight to `error_state`, no holding on that path) is unchanged.
5. `run_consult_task`:
   - `prefilter_company` branch: `errors = max(0, total - passed - failed - skipped - r.get("retried", 0))`.
   - single-entity grade (`rv` not success): `"total_errors": 0 if (not rv.get("state_held") and retry_base(rv.get("to_state"))) else 1`.
   - final job normalize (~2861): `errors = max(0, total - passed - failed - r.get("retried", 0))`.
   - `parse_job_list` / `fetch_website` / upshot branches: unchanged (explicit `errors`).

#### 6. `src/core/candidate.py` — `run_requested_artifacts_dispatch`

Move the `logger.error(...)` at ~3668 so severity follows the outcome:
- Hop-label hold and unregistered-trigger returns: `logger.warning` with the same message (state stays claimable, not an error).
- After `target = _requested_stage_failure_target(...)`: `(logger.warning if retry_base(target) else logger.error)(same message + " -> %s", ..., target)`.
- `target` is the `error_state` (not a holding): return `{"total_processed": 1, "total_passed": 0, "total_failed": 0, "total_errors": 1}`. The retry case keeps today's `total_failed: 1`.

Import `retry_base` (already importing from `src.utils.config`).

#### 7. `src/utils/logging.py` — `log_llm_batch_summary`

`logger.error(` → `logger.warning(` in the `error is not None` branch. Update the docstring to `"One INFO/WARNING per LLM call …"`. The provider call is followed by caller routing: ERROR is logged by the caller only when the entity lands in an error state.

#### 8. Compile

```bash
.venv/bin/python -m compileall -q src/utils/config.py src/utils/logging.py src/core/agent.py src/core/roster.py src/core/consult.py src/core/candidate.py
```

Betty owns tests; do not edit `tests/` or `docs/test-bible/**`.

**Out of scope (explicit):** new retry holdings for tasks without one (vet_inflow_discovery, the resolve tasks, recheck_no_openings, fetch_job_pages, fetch_jd, fetch_culture_pages, select_job_page, gaze, build-artifact/cover-letter chains, inbox), `dispatcher.py` catch/count sites, `monitor.py` formatting, balance-refusal holds, `render_verdict._fail` and grade prep straight-to-error paths, `evaluate_jd` not-ready counting, the `JO` decode bug.

### Blast radius

- **Tests assuming old behavior (Betty):** `TestAst882PrefilterOneRetryThenError` / `TestPrefilterCompany` (first strike now `HOMEPAGE_READY_RETRY`, not WFR), `test_config` transition/claim assertions for `HOMEPAGE_READY`, consult batch tests asserting `total_errors` for retry-routed rows or `logger.exception` calls, `parse_job_list_batch` tests counting retry/terminal as `passed`, candidate dispatch tests expecting `total_failed: 1` on `error_state` and `logger.error`, `log_llm_batch_summary` tests asserting ERROR level, and `do_task` rubric-encoded tests with an `agent_performance.status == "failure"` envelope.
- **Monitor emails:** fewer. Retry-only runs stop alerting. `parse_job_list` terminal (`COULD_NOT_PARSE_JOBLIST`) and candidate `REQUESTED_ARTIFACTS_ERROR` now count as errors. Candidate run_next chains still don't alert (no `dispatch_ledger_id`, dispatcher unchanged).
- **Existing WFR companies** from the old loop: still re-scraped by `fetch_website` and back to HR. Their prior HR → WFR history means an envelope failure now errors on first sight, and a parsing failure takes one `HOMEPAGE_READY_RETRY` strike. No migration.
- **`agent_failure` flag:** new key on the failed `do_task` result for rubric-encoded tasks (prefilter, grade/consult encoded tasks). Consult callers ignore it and route as any do_task failure, so behavior there is unchanged.
- **Admin/UI state lists** that enumerate `COMPANY_STATES` keys won't list `HOMEPAGE_READY_RETRY` (same as `WEBSITE_FOUND_RETRY` today).

### What must still hold

- AST-882 AC 1–5, restated for the new holding. A retryable prefilter failure from the primary state is observable in a retry holding (`HOMEPAGE_READY_RETRY`, or `WEBSITE_FOUND_RETRY` for envelope failures). A failure out of the holding is observable in `ERROR_PREFILTER`. `ERROR_PREFILTER` is never re-claimed (no `batch_criteria`). No company cycles forever. Clean evaluate outcomes (`PREFILTER_PASSED` / `PREFILTER_FAILED` / `NO_PREFILTER_JOBLISTS`) are unchanged.
- Hard (non-retryable) single-company prefilter failures still go straight to `ERROR_PREFILTER`.
- AST-1810: `fetch_website` still claims and re-scrapes every `WEBSITE_FOUND_RETRY` row; infra vs site routing (`_fetch_website_fail_destination`) is unchanged.
- AST-641 / AST-1155 / AST-1760: `{trigger}_RETRY` claim rule, incomplete/all-X grades → holding → `FAILED_TECHNICAL_*` second strike are unchanged. Only severity and counting move.
- Provider balance refusal still holds state (AST-897).
- Every out-of-holding failure still counts toward `total_errors` and still triggers `auto_run_error` on AUTO runs.

