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

### Fix board — AST-1839

#### Betty

[board-betty] TESTS: REVISE
What: docs/test-bible/core/roster.md § AST-882 + utils/config.md + core/consult.md + utils/logging + core/agent.md + core/candidate.md — broken tests + missing repro coverage — `test_roster.py` hard-asserts HR→`WEBSITE_FOUND_RETRY` first strike (`_prefilter_batch_fail_dest` L2254, `TestAst882PrefilterOneRetryThenError` L2272, plus L6031/L6292) and `COMPANY_STATES`/transition asserts for HOMEPAGE_READY; no existing node covers the repro (HR→`HOMEPAGE_READY_RETRY`→`ERROR_PREFILTER`, envelope WFR-once via history, `retried` excluded from `total_errors`, WARNING-vs-ERROR by `retry_base(dest)`, `do_task` `agent_failure` flag, `parse_job_list_batch` retry/terminal counting, candidate `error_state` → `total_errors: 1`, `log_llm_batch_summary` WARNING level).

#### Joan

[board-joan]  CANON: REVISE
What: stat.logging.error + stat.logging.warning — destination-based batch/LLM severity (retry holding → warning + debug traceback; terminal → error); amend Resolution §2–3 and log_llm_batch_summary level.

**Findings (Joan pass — AST-1839, plan-fix on `origin/sub/AST-1828/AST-1839-auto-retry-warn-then-error`, Bug section in `docs/features/roster/ast-882-prefilter-one-retry-error.md`)**

**Read:** As-is / To-be / Repro / Root cause / Proposed change / Blast radius / What must still hold. No frozen **Canon Scope** on AST-1839 (same process gap as other fix children; triage via directive roster overlap only, not R1–R7).

**Aligns (no canon edit for F3 on these):**
- **`patt.task.dispatch-retry` / AST-641 shape:** Moving prefilter parsing first-strike to `retry_of("HOMEPAGE_READY")` (`HOMEPAGE_READY_RETRY`) matches the `{trigger}_RETRY` claim rule the parent already cited; implicit registration via `retry_state` + transitions (AST-1805-style, no literal `HOMEPAGE_READY_RETRY` row) matches pattern arc 1–2. Envelope path via `envelope_retry_state` → `WEBSITE_FOUND_RETRY` reuses the existing cross-task holding with history-gated second strike — bounded in plan; not an unbounded loop ESCALATE.
- **`stat.general.registry-not-literals` / config SSOT:** Routing and `retry_base`/`retry_of` stay in `config.py`; no new dispatch seed rows (AST-745-safe).
- **`patt.entity.batch-processing` / claim-process-release:** `retried` counting and consult `total_errors` math do not change batch lock/release; monitor formatting explicitly out of scope.
- **`stat.agent` / `do_task`:** Rubric envelope `agent_failure` flag is caller routing input, not a new I/O path — within delegation.

**Requires canon update (REVISE → spawn `validate-plan` fix mode F3):**
- **`stat.logging.warning`:** Statement scopes warning to happy-path misses **without an exception**; Resolution §2 sends any `except` path to **`stat.logging.error`**. Proposed change deliberately does the opposite on retry holdings: caught hydrate/decode/process failures → **`logger.debug(..., exc_info=True)`** plus **`_log_fail_dest` → WARNING** when `retry_base(dest)`. That is the core product fix but is not readable as compliant with in-force text without a carve-out (retry-routed batch catch: per-item warning who/why; stack on debug, not `logger.exception` at error).
- **`stat.logging.error`:** Same batch handlers today use `logger.exception`; plan removes error-level traceback for retry destinations. Resolution §3 still treats **`log_llm_batch_summary(..., error=...)`** as **the** hop error line; plan §7 downgrades provider summary to **WARNING** and defers ERROR to callers when dest is terminal — needs an explicit amendment so F7/Radia do not read the shipped fix as violating §3.

**Not ESCALATE:** Susan answered open questions on AST-1828/1839; dual first-strike holdings and counting approach are specified in plan-fix with blast radius and “What must still hold” (AST-882 AC restated, AST-1810/1155/641 preserved). No Archie-only precedent gap beyond logging statute wording.

#### Chuckles disposition

Both REVISE. Orphaned-bug rule: both verdicts go to one sibling gap child (tests + bible from Betty, and the `stat.logging.*` carve-out that Joan authors in validate-plan fix mode and Chuckles applies verbatim), not to qa-fix / F3 inline on AST-1839. AST-1839 → Plan Approved → make-fix now.

### Radia review-fix — AST-1839

[code-rubric] PROCEED (Commit: 36f385a2) destination logging + retry counts

**Ticket:** AST-1839  
**Publish ref:** `36f385a2` (`origin/sub/AST-1828/AST-1839-auto-retry-warn-then-error`)  
**Diff reviewed:** `origin/ftr/AST-1828-auto-retry-warn-then-error...origin/sub/AST-1828/AST-1839-auto-retry-warn-then-error` (tip = single product commit `36f385a2` for `src/**`; wider three-dot includes `sync(dev)` @ `eaf40dda` and other landed history — see advisory)  
**Corpus:** `canon/docs/DIRECTIVES-DIRECTORY.md` + active `canon/directives/**` on tip (no `docs/canon-index.md` on ref)  
**Overall:** CLEAN  

#### Canon scores

Frozen **Canon Scope** on AST-1839 is empty (Linear Description + fix-board Joan). No directive rows to score; roll-up from canon grades is vacuously clean.

**Board overlap (informational only — not on frozen list):**

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| `patt.task.dispatch-retry` / AST-641 shape | A | | `HOMEPAGE_READY.retry_state` → `retry_of("HOMEPAGE_READY")`, transitions + `envelope_retry_state`; history-gated envelope WFR |
| `stat.general.registry-not-literals` | A | | routing/`retry_base` in `config.py`; no new dispatch rows |
| `patt.entity.batch-processing` | A | | `retried` keys; consult `total_errors` math; claim/process/release unchanged |
| `stat.agent` / `do_task` | A | | rubric `agent_failure` envelope branch in `agent.py` only |
| `stat.logging.warning` | B | | matches Susan To-be + Joan’s **destination-based** carve-out (per-item who/why at WARNING on retry holdings); in-force Resolution §2 (except → error) not amended until **AST-1846** — **not fix-now here** |
| `stat.logging.error` | B | | terminal/out-of-holding via `_log_fail_dest` → ERROR; `log_llm_batch_summary` WARNING + caller ERROR; §3 LLM hop wording pending **AST-1846** — **not fix-now here** |

#### Column diff vs plan stage

`no plan-stage validate-plan scores attached` — fix-board Joan REVISE on logging is explicitly deferred to **AST-1846** carve-out; Radia aligns with that disposition, not re-litigating F3.

#### Frame diff

(none)

#### Fix-specific checks

- **`[bug-repro]`:** not applicable — clean board opt-out (Betty TESTS: REVISE → sibling **AST-1846**; no qa-fix / no `[bug-repro]` on this tip per spawn).
- **`## What must still hold`:** OK — traced on `36f385a2` product diff:
  - AST-882 AC restated: parsing first strike → `HOMEPAGE_READY_RETRY`; envelope first strike → `WEBSITE_FOUND_RETRY` with history gate; any failure not from primary `HOMEPAGE_READY` → `ERROR_PREFILTER`; evaluate pass/fail/no-PJL paths untouched.
  - Hard non-retryable `_prefilter_fail` still → `error_state`.
  - AST-1810: no `gazer.py` change; not-ready skip uses `envelope_retry_state` (WFR left for fetch).
  - Consult grade/upshot/candidate paths: holding vs terminal severity and counting via `retry_base` / `retried`.
  - Balance refusal / `state_held` paths unchanged.
  - Terminal failures still increment `total_errors` (prefilter `retried` excluded; candidate `error_state` → `total_errors: 1`; parse_job_list terminal out of holding → `errors`).

#### Findings

**fix-now:** none  

**discuss:** none  

**advisory:**
- Three-dot `ftr...sub` includes non–AST-1839 product from `sync(dev)` and prior merges (e.g. `dispatcher.py` AST-1829, telescope/formatting/admin). **AST-1839 product footprint** is commit `36f385a2` only: `agent.py`, `candidate.py`, `consult.py`, `roster.py`, `config.py`, `logging.py`.
- In-force `stat.logging.*` text still reads strict on `except` + `log_llm_batch_summary`; canon amendment tracked on **AST-1846** (Joan board REVISE). Shipped code follows approved plan-fix / Susan To-be.
- Betty’s broken/missing test nodes (incl. Ada’s 19-node list) remain **AST-1846**; not gated on this review.

#### What’s solid

- `_log_fail_dest` + `retry_base(dest)` applied consistently on consult batch/upshot and prefilter transitions.
- `run_consult_task` prefilter branch: `errors = max(0, total - passed - failed - skipped - r.get("retried", 0))`; single-entity grade respects `retry_base(to_state)`.
- `do_task` rubric envelope `agent_failure` before unwrap enables WFR vs HR_RETRY routing.
- `parse_job_list_batch` separates `retried` vs terminal `errors`; `log_llm_batch_summary` provider line downgraded to WARNING per plan §7.

#### Recommended actions

| Action | Item |
|--------|------|
| none (ship product) | 0 fix-now · 0 discuss · 0 advisory blocking |

#### Chuckles disposition

Clean PROCEED → Review Posted → User Testing (resolve-child skipped). Orphaned mini-parent: merge-child into `ftr/AST-1828-auto-retry-warn-then-error`. The statute carve-out and the 19 test nodes stay on gap AST-1846.

### docs-acceptance (AST-1839)

Test and bible coverage for this fix is owned by sibling gap **AST-1846** (Betty board `[board-betty] TESTS: REVISE`; orphaned mini-parent, so no qa-fix / `[bug-repro]` on this ref). That includes the 19 broken or missing test nodes (the `test_roster.py` AST-882 first-strike asserts, `COMPANY_STATES` / HOMEPAGE_READY transition asserts, and the uncovered repro paths listed under Fix board → Betty) plus the `docs/test-bible/**` updates. No test-tree delivery on this ref, so no `merge-tests(AST-1839)` and no fabricated `test(AST-1839)` noop.

---

## AST-1846 plan-fix

- **Linear:** [AST-1846](https://linear.app/astralcareermatch/issue/AST-1846) — gap: tests + logging statute carve-out for AUTO retry WARNING (sibling of AST-1839, parent AST-1828)
- **Publish ref:** `origin/sub/AST-1828/AST-1846-auto-retry-warn-then-error-gap`
- **Refs:** ftr base (pre-fix) `31846c28`; ftr tip (AST-1839 merged) `2eac54b5`.
- **No product `src/` change.** make-fix is an empty `code(AST-1846)` commit after sync.

### As-is

- AST-1839's product fix is merged on `origin/ftr/AST-1828-auto-retry-warn-then-error` @ `2eac54b5`. On that tip, 19 existing component nodes still assert the old contract: HR → `WEBSITE_FOUND_RETRY` first strike, result dicts without `retried`, retries counted as errors or passes, provider errors at ERROR, and the old `HOMEPAGE_READY` config/prior snapshot. They are red there and green at `31846c28`. The list comes from AST-1839 test-fix: a touched-area run of roster, consult, agent, `agent_ast1448`, candidate, config, and `logging_batch` compared against the pre-fix tree. It had 267 failures in common (env/dev drift) and exactly these 19 new ones.
- No node covers the new behavior (fix board, Betty).
- The in-force `stat.logging.warning` Resolution §2 sends every `except` path to `stat.logging.error`, and `stat.logging.error` Resolution §3 names `log_llm_batch_summary(..., error=...)` as the hop error line. The shipped fix contradicts both on retry-routed paths (fix board, Joan; Radia B on both, deferred here).

### To-be

- The 19 nodes assert the AST-1839 contract (§ Bug: AST-1839 → Proposed change), and they are green at `2eac54b5`.
- New repro nodes pin that contract. They are **red at `31846c28`** and **green at `2eac54b5`**.
- The bible pages list both.
- `stat.logging.warning` / `stat.logging.error` read as compliant with destination-based severity. A caught exception routed to a retry holding logs WARNING per item (who/why), with the traceback at debug only. Only an error/terminal destination logs ERROR. `log_llm_batch_summary` provider errors log WARNING, and the caller logs ERROR when the entity lands terminal.

### Repro

The new nodes below (Proposed change §2) are the repro set. Gate for qa-fix: each new node is **RED** against a `git archive 31846c28` export and **GREEN** at `2eac54b5`, run with the repo's own `pytest.ini` addopts (`--import-mode=importlib`; don't clear addopts). Fixture shape is § Bug: AST-1839 → Repro (`acme_com`, `HOMEPAGE_READY`, hydrate `ValueError`, envelope variant with a `HOMEPAGE_READY → WEBSITE_FOUND_RETRY` history row). Every new node must fail at base on an **assertion** about the behavior (wrong state, wrong count, wrong level, missing key), not on an import or attribute error. Import- or attribute-errors at base (`envelope_retry_state`, `retry_base` on roster) don't count as red. Assert through `run_consult_task` / batch functions and `caplog` levels, not by referencing new symbols.

The 19 flipped nodes follow the opposite direction: green at base, red at tip before Betty's edit, green at tip after.

### Root cause

Fix board on AST-1839 routed both REVISE verdicts to one gap child (orphaned mini-parent rule), so AST-1839 shipped with no test-tree delivery and no statute amendment. The test tree and canon still encode the pre-AST-1839 contract.

### Proposed change

#### 1. Betty (qa-fix) — flip the 19 existing nodes to the new contract

Edit assertions only; keep each node's intent where it still holds. Target behavior per node:

| Node | New assertion |
|------|---------------|
| `tests/component/core/test_roster.py::TestAst702PrefilterBatchHelpers::test_prefilter_batch_fail_dest_from_homepage_ready` | `_prefilter_batch_fail_dest("HOMEPAGE_READY", cfg)` → `HOMEPAGE_READY_RETRY` |
| `…test_roster.py::TestAst882PrefilterOneRetryThenError::test_prefilter_fail_first_strike_retries` | first strike → `HOMEPAGE_READY_RETRY`, `decision == "RETRY"` |
| `…test_roster.py::TestAst882PrefilterOneRetryThenError::test_batch_do_task_failure_second_strike_to_error` | from `HOMEPAGE_READY_RETRY` → `ERROR_PREFILTER`; result dict includes `"retried": 0` |
| `…test_roster.py::TestAst882PrefilterOneRetryThenError::test_not_ready_wfr_left_alone_for_fetch_website` | WFR not-ready still skipped; result dict includes `"retried": 0` |
| `…test_roster.py::TestAst702PrefilterCompanyBatch::test_do_task_failure_transitions_batch` | HR rows → `HOMEPAGE_READY_RETRY`; dict includes `"retried": <n>` |
| `…test_roster.py::TestAst702PrefilterCompanyBatch::test_skips_not_ready_without_do_task` | dict includes `"retried": 0` |
| `…test_roster.py::TestAst1155PrefilterIncompleteRetry::test_prefilter_company_incomplete_routes_to_website_found_retry` | incomplete grades → `HOMEPAGE_READY_RETRY` (rename optional; Betty's call) |
| `…test_roster.py::TestAst897HoldStateOnBalanceRefusal::test_prefilter_fail_ordinary_api_still_retries` | ordinary API failure → `HOMEPAGE_READY_RETRY` (balance hold unchanged) |
| `…test_roster.py::TestAst891ParseJobListBatch::test_passes_batch_session_and_counts_definite_outcomes` | `JOBLIST_IDENTIFIED_RETRY` → `retried`, not `passed`; `COULD_NOT_PARSE_JOBLIST` → `errors` |
| `tests/component/core/test_consult.py::TestAnalysisUpshotPrepAndBatch480::test_batch_company_missing_moves_to_retry` | dest `PASSED_LIKE_RETRY`, `total_errors == 0` |
| `…test_consult.py::TestAnalysisUpshotPrepAndBatch480ExtraBranches::test_batch_do_task_failure_transitions_error` | from primary → holding, `total_errors == 0`; (add or keep a from-holding case → `FAILED_TECHNICAL`, `total_errors == 1`) |
| `…test_consult.py::TestAnalysisUpshotPrepAndBatch480ExtraBranches::test_batch_missing_company_transitions_and_counts_error` | same split: holding → 0, terminal → 1 |
| `…test_consult.py::TestAst642PerEntityBatchRetry::test_analysis_upshot_primary_failure_to_retry_holding` | holding dest, `total_errors == 0` |
| `tests/component/core/test_candidate.py::TestAst972RequestedStageDispatch::test_artifacts_dispatch_retry_failure_errors` | from `REQUESTED_ARTIFACTS_RETRY` → `REQUESTED_ARTIFACTS_ERROR`, `total_errors == 1`, `total_failed == 0` |
| `tests/component/utils/test_config.py::TestAst702PrefilterBatchConfig::test_prefilter_input_state_and_retry_on_homepage_ready` | `retry_state == "HOMEPAGE_READY_RETRY"`, `envelope_retry_state == "WEBSITE_FOUND_RETRY"` |
| `…test_config.py::TestAst507EncodedPrefilterConfig::test_company_states_and_transitions` | `COMPANY_STATES["HOMEPAGE_READY"]["retry_state"] == "HOMEPAGE_READY_RETRY"`; new HR / HR_RETRY transition edges present; `("HOMEPAGE_READY", "WEBSITE_FOUND_RETRY")` still present |
| `…test_config.py::TestAst1807ImplicitRetryHelpers::test_state_prior_states_cross_base_feeders` | `state_prior_states(COMPANY_STATES, "WEBSITE_FOUND_RETRY")` has no `HOMEPAGE_READY` feeder; `…("HOMEPAGE_READY_RETRY")` includes `HOMEPAGE_READY` |
| `…test_config.py::TestAst1808RetryRegistryPurge::test_prior_snapshot_pinned` | re-pin `tests/component/utils/fixtures/ast1806_prior_snapshot.json` `COMPANY_STATES` entries for `WEBSITE_FOUND_RETRY` / `HOMEPAGE_READY_RETRY` to the derived values |
| `tests/component/utils/test_logging_batch.py::TestLogLlmBatchSummary::test_empty_error_string_uses_error_path_not_healthy_summary` | `error="(empty error)"` line at **WARNING**, not ERROR; still no healthy `stop=?` INFO |

(Betty's board note cited `test_roster.py` L6292. That line doesn't exist at tip: the file has 6251 lines. The late first-strike asserts are L6031 and L6250, which are the `TestAst897…` and `TestAst1155…` rows above.)

#### 2. Betty (qa-fix) — new repro nodes (red at `31846c28`, green at `2eac54b5`)

Class and file placement is Betty's call. Suggested: one `TestAst1846*` class per file. Each bullet is one node:

- **`test_roster.py`**
  1. HR hydrate failure through `run_consult_task(…, dispatch_task_key="prefilter_company")` → `HOMEPAGE_READY_RETRY`, `total_errors == 0`, one WARNING record `acme_com -> HOMEPAGE_READY_RETRY [hydrate: …]`, no ERROR record.
  2. Same company from `HOMEPAGE_READY_RETRY` → `ERROR_PREFILTER`, `total_errors == 1`, one ERROR record.
  3. Envelope (`do_task` → `{"success": False, "agent_failure": True, …}`) from HR with empty history → `WEBSITE_FOUND_RETRY`, WARNING, `total_errors == 0`.
  4. Envelope from HR with a `HOMEPAGE_READY → WEBSITE_FOUND_RETRY` history row → `ERROR_PREFILTER`, ERROR, `total_errors == 1` (loop bound).
  5. Mixed batch (one per-company decode failure from HR, one missing id from `HOMEPAGE_READY_RETRY`, one clean pass) → `prefilter_company_batch` returns `retried == 1`, `passed == 1`; summary `total_errors == 1`.
  6. `parse_job_list_batch`: one `JOBLIST_IDENTIFIED` fail (→ retry) and one `JOBLIST_IDENTIFIED_RETRY` fail (→ `COULD_NOT_PARSE_JOBLIST`) → `retried == 1`, `errors == 1`, `passed == 0`; WARNING for the first, ERROR for the second.
- **`test_consult.py`**
  7. `_run_batch_consult` hydrate failure on primary-state jobs → dests `*_RETRY`, `run_consult_task` `total_errors == 0`, WARNING records only.
  8. Same from `*_RETRY` states → `error_state`, `total_errors == N`, ERROR records.
  9. Single-entity grade, incomplete grades → `*_RETRY`: `total_errors == 0`. Balance-held result (`state_held=True`) still `total_errors == 1`.
- **`test_agent.py`**
  10. Rubric-encoded task (`prefilter_company`) whose envelope is `{"agent_performance": {"status": "failure", "failure_note": "parked domain"}, "agent_payload": "…"}` → `success is False`, `agent_failure is True`, `error == "Agent failure: parked domain"`. A non-rubric task with the same envelope does **not** set `agent_failure` (existing schema path).
- **`test_candidate.py`**
  11. Primary `REQUESTED_ARTIFACTS` failure → `REQUESTED_ARTIFACTS_RETRY`, `total_failed == 1`, `total_errors == 0`, WARNING (no ERROR record).
- **`test_logging_batch.py`**
  12. `log_llm_batch_summary(..., error="400 Content Exists Risk")` → one WARNING record, zero ERROR records.
- **`test_roster.py`** (fetch_website severity)
  13. `scrape_company_homepage_content` scrape exception → WARNING record, zero ERROR records; `out["error"]` set as before.

#### 3. Betty — bible

Add or modify entries for every node in §1–§2 in `docs/test-bible/core/roster.md` (AST-882 section + new AST-1846 entries), `core/consult.md`, `core/agent.md`, `core/candidate.md`, `utils/config.md`, and `utils/logging_batch.md`. Include a `## QA test manifest` listing all §1 and §2 nodes with the run command:

```bash
./scripts/testing/run_component_tests.sh <node ids…>
```

#### 4. Joan (validate-plan fix mode) — canon carve-out, intent only

Joan authors the literal patch; Chuckles applies it verbatim. No new directive ids; no other `stat.logging.*` directive touched.

- **`canon/directives/active/stat.logging.warning.md`:** Statement + Resolution §2. A caught exception on a dispatch batch path whose entity is routed to a **retry holding** (`retry_base(dest)` not `None`) logs **WARNING per item** (who → dest [why]), with the traceback at **debug** (`exc_info=True`), not `logger.exception`. §2's "thrown → error" stays true for everything else.
- **`canon/directives/active/stat.logging.error.md`:** Statement/Do + Resolution §3. ERROR (with traceback where useful) is for a **terminal/error destination** or an unrouted exception. `log_llm_batch_summary(..., error=...)` is the per-call provider line at **WARNING**, and the caller logs ERROR only when the entity lands in an error/terminal state. The §3 wording changes from "the hop error line" accordingly.

### Blast radius

- Test tree and bible only (Betty), plus two canon files (Joan → Chuckles). No `src/**`.
- The fixture `tests/component/utils/fixtures/ast1806_prior_snapshot.json` is shared by the AST-1806/1808 snapshot tests. Re-pin only the two `COMPANY_STATES` retry targets.
- The 267 touched-area failures common to base and tip are environment/dev drift (missing scratch-DB tables, dev's required candidate id for agent prompts, Python 3.14 venv). They are out of scope, so don't "fix" them here. The qa-fix run should use the component venv (`scripts/testing/ensure_component_venv.sh`) where they may not reproduce.
- Radia's B grades on `stat.logging.warning` / `stat.logging.error` for AST-1839 clear once §4 lands.

### What must still hold

- No `src/**` change on this ref (make-fix = empty `code(AST-1846)`).
- The AST-1839 contract as shipped (§ Bug: AST-1839 → Proposed change / What must still hold). Tests pin it and don't re-shape it.
- Pre-existing, non-AST-1839 assertions in the touched classes (balance-refusal hold, clean evaluate outcomes, AST-1810 fetch_website re-scrape of every WFR row, AST-1155/1760 holding → `FAILED_TECHNICAL_*`) stay asserted.
- The canon carve-out stays scoped to retry-routed dispatch batch failures and the `log_llm_batch_summary` level. It doesn't loosen ERROR for terminal or unrouted exceptions.

### Fix board — AST-1846

#### Betty

[board-betty] TESTS: REVISE
What: docs/test-bible/README.md §6a/§7.12 (`LOCKED_AT_100`) — missing coverage — the plan's manifest is narrowed node ids only, so `check_per_file_coverage.py` never runs on the five locked files AST-1839 touched (`roster.py`, `consult.py`, `agent.py`, `candidate.py`, `config.py`), and the 13 repro nodes leave new 36f385a2 branches unexercised. Add to §2/§3: a branch-lock check on those five files at `2eac54b5`, plus a node for each uncovered AST-1839 branch it reports. Likely uncovered: `agent.py` `failure_note` fallbacks (non-dict perf / top-level note / no note) and `_should_store` store-exception; `candidate.py` hop-label hold + unregistered-trigger WARNING returns; `consult.py` process_fn-exception `_log_fail_dest`, upshot no-company / no-live-content / non-dict-parse holding-vs-terminal branches, `if error_state else 0` false branch. The rest of the test plan (19 flips verified present at tip, 13 repro nodes, red-at-base-on-assertion gate, bible pages) is right as written.

#### Joan

```text
[board-joan]  CANON: REVISE
What: stat.logging.warning + stat.logging.error — AST-1839 destination carve-out (§4 intent) — F3 literal patch
```

**Findings (fix-board Joan — AST-1846 only)**

**Read:** `## AST-1846 plan-fix` on `origin/sub/AST-1828/AST-1846-auto-retry-warn-then-error-gap` (As-is / To-be / Repro / Root cause / Proposed change §1–§4 / Blast radius / What must still hold). No product `src/**`; Joan scope is **§4 only** (Betty §1–§3 is Betty’s board, not re-scored here).

**Confirm REVISE intent (correct):** On this gap child, **`CANON: REVISE` is the expected board outcome**, not a plan defect. It matches AST-1839 fix-board Joan (“logging Resolution §2/§3 pending **AST-1846**”) and records that **in-force canon still contradicts shipped AST-1839** until F3 lands. **`validate-plan` fix mode** is where you **author the literal** `stat.logging.warning` / `stat.logging.error` text; Chuckles applies it verbatim per plan §4 and ticket Boundaries. **`make-fix`** on this ref stays empty product + canon commit after F3. Do **not** read REVISE as ESCALATE or as “replan the carve-out”—§4 intent already matches Susan To-be and `_log_fail_dest` / `retry_base(dest)`.

**Directives touched (canon):** Only these two, as scoped in plan §4 and Linear Boundaries:

| Id | Plan §4 intent |
|----|----------------|
| `stat.logging.warning` | Statement + Resolution §2: **carve-out** — caught batch failure routed to a **retry holding** (`retry_base(dest)` not `None`) → **WARNING** per item (`who → dest [why]`); traceback **`logger.debug(..., exc_info=True)`**, not `logger.exception`. §2 “thrown → error” **unchanged** for all other paths (terminal dest, unrouted throw, dispatcher crash). |
| `stat.logging.error` | Statement/Do + Resolution §3: ERROR + traceback for **terminal/error destination** or **unrouted** exception; **`log_llm_batch_summary(..., error=...)`** at **WARNING**; caller **ERROR** only when the entity lands terminal/error. Replace “the hop error line” wording accordingly. |

**No other directive ids in scope:** Plan explicitly excludes new ids and other `stat.logging.*` files. **No `patt.*` or config statute amend** on this ticket—`patt.task.dispatch-retry` alignment is product/tests (Betty §1–§2), not canon text here.

**Advisory for F3 (not separate board REVISE ids):** After §3 moves provider summary to WARNING, skim **`stat.logging.info`** Resolution §3 (“exception → error”) and **`stat.logging.debug`** Notes on `log_llm_batch_summary` for stale “error-only hop” implications. If a one-line **cross-reference** in Notes avoids reader confusion, add it in F3 **only if** it stays inside the two-file boundary; otherwise leave them untouched per Boundaries.

**ESCALATE:** No. Carve-out is bounded (retry-routed dispatch batch + provider summary level); Susan/AST-1839 product already shipped; no new precedent beyond amending the two logging statutes.

**Chuckles branch (Joan half):** REVISE → Plan Discuss optional only if F3 finds wording gaps; then **`validate-plan` fix mode (F3)** before **`make-fix`** on AST-1846. Parallel **Betty `qa-fix` (F4)** for §1–§3 is independent; board matrix REVISE|REVISE runs both F3 and F4 (F3 before F4 per fix-lane table).

#### Chuckles disposition

Both REVISE. AST-1846 is the gap child, so both run inline (no gap-of-a-gap): F3 validate-plan fix mode (Joan writes the literal `stat.logging.warning` / `stat.logging.error` patch, Chuckles applies it verbatim), then F4 qa-fix (Betty), with her branch-lock addendum (a `check_per_file_coverage.py` run on the five locked files at `2eac54b5`, plus a node for each uncovered AST-1839 branch) added to §2/§3 scope. make-fix = empty `code(AST-1846)` after sync.

### Radia review-fix — AST-1846

[code-rubric] PROCEED (Commit: 2b515163) tests, bible, canon carve-out

**Ticket:** AST-1846  
**Publish ref:** `2b515163` (`origin/sub/AST-1828/AST-1846-auto-retry-warn-then-error-gap`)  
**Diff:** `origin/ftr/AST-1828-auto-retry-warn-then-error...origin/sub/AST-1828/AST-1846-auto-retry-warn-then-error-gap` — 16 files, **0** `src/**` lines (canon + plan doc + test-bible + component tests + `ast1806_prior_snapshot.json` re-pin)  
**Corpus:** active `canon/directives/**` on tip (`e1f2699f` canon commit)  
**Overall:** CLEAN  

#### Canon scores

No frozen **Canon Scope** id list on the ticket (gap child; boundaries name the two statutes only). Scored per plan §4 / Joan F3 scope:

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| `stat.logging.warning` | A | | Statement/Resolution §2 carve-out matches `_log_fail_dest` + consult/roster hydrate/decode (`debug` + `exc_info`, per-item WARNING on `retry_base(dest)`) |
| `stat.logging.error` | A | | Statement/Resolution §3: terminal/unrouted → ERROR; `log_llm_batch_summary(..., error=...)` → WARNING; caller ERROR on terminal landings |

#### Column diff vs plan stage

Joan F3 comment on Linear documents the §4 intent; no separate validate-plan grade table in the issue doc → `no plan-stage scores attached` (aligned with F3 delivery in `e1f2699f`).

#### Frame diff

(none)

#### Fix-specific checks

### `[bug-repro]` — OK

Betty’s `[bug-repro]` on Linear (`b6207dc6`) matches the plan gate and the test bodies are substantive (not tautologies):

- **New repro (`TestAst1846*`):** Pin concrete To-be values — e.g. `transition…("HOMEPAGE_READY_RETRY")`, `total_errors == 0`, `caplog` level vectors like `["WARNING"]` / `["ERROR"]`, `retried` / `errors` splits, `agent_failure` + `error` strings, `log_llm_batch_summary` WARNING-only (`TestAst1846ProviderErrorLevel`).
- **Red @ `31846c28` / green @ `2eac54b5`:** Documented on Linear (28/29 repro runs failed on **assertions** at base; guard `test_non_rubric_task_does_not_set_agent_failure` green both shas by design). I could not re-run pytest here (host lacks component Python); Betty’s archive export method is acceptable for gap sequencing.
- **19 flips:** Present per manifest in `docs/test-bible/core/roster.md` § AST-1846; assertions updated to HR_RETRY / `retried` / upshot holding `total_errors == 0` (e.g. `test_batch_missing_company_transitions_and_counts_error`, `test_analysis_upshot_primary_failure_to_retry_holding`).
- **Board addendum:** Extra nodes cover agent `failure_note` fallbacks + store swallow, candidate hop-label / unregistered trigger, parse batch error/exception paths, upshot terminal/no-dest ERROR sites — consistent with Betty’s branch-lock comment.

### `## What must still hold` — OK

| Item | Verdict |
|------|---------|
| No `src/**` on this ref | Diff has zero product lines; tip includes empty `code(AST-1846)` after ftr sync. |
| Tests pin AST-1839 contract, don’t reshape it | Repro + flips assert routing, counts, and levels per § Bug: AST-1839; no product edits. |
| AST-882 / AST-1810 / balance / grade holdings preserved | Flipped nodes retain balance hold, WFR leave-alone, incomplete-grade → HR_RETRY, upshot `FAILED_TECHNICAL` second strike, etc. |
| Canon carve-out scoped | Only `stat.logging.warning` + `stat.logging.error` touched; no other `stat.logging.*`. |

### Canon text vs shipped AST-1839 code (`2eac54b5` on ftr)

- **`_log_fail_dest` / `retry_base(dest)`:** Canon Do block mirrors `(logger.warning if retry_base(dest) else logger.error)(...)`.
- **Batch hydrate/decode:** Code uses `logger.debug(..., exc_info=True)` + `_log_fail_dest`; canon carve-out matches.
- **`log_llm_batch_summary`:** Code logs WARNING on `error=`; canon §3 amended accordingly.
- **Advisory (not fix-now, no re-wording):** `scrape_company_homepage_content` still uses `logger.warning(..., exc_info=True)` on scrape exceptions (AST-1839 product). Joan’s carve-out text targets **dispatch batch handlers** with traceback on **debug**, not `warning`+`exc_info`. Tests only require WARNING and no ERROR (`test_fetch_website_scrape_failure_logs_warning`). Statute does not explicitly bless that single-entity path; it also does not contradict it if read as outside the batch carve-out.

#### Findings

**fix-now:** none  

**discuss:** none  

**advisory:**
- **sibling test carry:** N/A — this ticket *is* the test/bible delivery; diff is expected test-tree only.
- **Host manifest:** Component venv unavailable in this session; rely on Betty’s 50/50 manifest + red/green archive proof for gate sign-off.
- **Pre-existing reds:** Documented in bible (AST-891 timeout, AST-882 WFR claim, AST-507 inflow pair) — out of scope.

#### What’s solid

- Canon patch at `e1f2699f` closes the AST-1839 deferral Radia noted as **B** on AST-1839.
- Primary manifest in `roster.md` § AST-1846 lists all 19 flips + five `TestAst1846*` classes; sibling bible sections cross-link.
- Fixture re-pin drops stale `HOMEPAGE_READY` feeder on `WEBSITE_FOUND_RETRY` per plan.

#### Recommended actions

| Action | Item |
|--------|------|
| none (ship) | 0 fix-now · 0 discuss · 0 advisory blocking |

#### Chuckles disposition

Clean PROCEED → Review Posted → User Testing (resolve-child skipped). merge-child into `ftr/AST-1828-auto-retry-warn-then-error`; all children done → prep-uat.

## Threads (generated — epic_registry mirror)

_(generated from epic registry — do not hand-edit; edits are overwritten)_

### Team

| Agent | Role | Thread |
|--------|-------|--------|
| Ada | engineer | `/home/susan/.cursor/chats/e000ddc7f242b6e9b47d3df58312fbe7/9c2624eb-57b6-4ed2-8b65-6cf9ff6fb038/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/12212c79-09cc-4799-95c9-0bcd19cfa8c6/store.db` |
| Radia | review | `/home/susan/.cursor/chats/e000ddc7f242b6e9b47d3df58312fbe7/ea56a33b-0ef9-403f-946b-2939a8646b2f/store.db` |

### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-1828 (parent) | ftr/AST-1828-auto-retry-warn-then-error |
| AST-1839 | sub/AST-1828/AST-1839-auto-retry-warn-then-error |
| AST-1846 | sub/AST-1828/AST-1846-auto-retry-warn-then-error-gap |

**Epic worktree:** `astral-AST-1828/` — one active sub checked out at a time.
