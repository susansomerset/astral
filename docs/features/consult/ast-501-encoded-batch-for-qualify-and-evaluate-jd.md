<!-- linear-archive: AST-501 archived 2026-06-15 -->

## Linear archive (AST-501)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-501/encoded-batch-for-qualify-and-evaluate-jd-high-volume-encoded-batch  
**Status at archive:** Done  
**Project:** Astral Consult  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-500 — High-volume encoded batch consult: migrate all stages, cache-first exhaustion runs  
**Blocked by / blocks / related:** parent: AST-500; blocks: AST-502

### Description

## What this implements

Restore the intended **single-call batch** behavior for **job-listing qualification** and **JD evaluation**: many items in one assessment, one response with a multi-line encoded payload inside the standard agent performance envelope. Fix the runtime path that today often issues **one assessment per job** despite encoded wire format and seed `batch_call_mode` for these steps. Tighten provider-facing instructions so models return the **outer envelope** plus compact lines (not bare pipe text or expanded JSON job arrays).

## Acceptance criteria

1. With batch size **N > 1** and **N** eligible jobs for JD evaluation, a single dispatch pass produces **one** assessment call for that chunk and a payload with **N** encoded lines (or explicit agent failure in the envelope); each job lands in pass, fail, retry, or error state per today’s rules—not left stuck in the trigger state.
2. The same single-call / multi-line behavior holds for **job-listing qualification** on a multi-listing batch.
3. Model responses respect the **outer envelope**; compact lines live inside `agent_payload`, not as a substitute for the envelope or as unrelated expanded JSON, for all providers in production use.

## Boundaries

* Does not implement multi-chunk parallel exhaustion (sibling ticket).
* Does not migrate DO / GET / LIKE (sibling ticket).
* Does not change rubric vectors, pass/fail rules, or grade letters.

## Notes for planning

* `dispatch_task` **batch_size** and **batch_call_mode** are authoritative (no hard-coded default batch sizes in code).
* Partial line omissions in an otherwise valid envelope → **per-job retry states**, not whole-batch error.

## Git branch (authoritative)

Parent `ftr/AST-500-high-volume-encoded-batch-consult-migrate-all-stages-cache-first-exhaustion-runs`, child `sub/AST-500/…` per orientation-astral § Branch law.

### Comments

#### radia — 2026-05-27T03:47:44.946Z
**Diff:** `origin/dev...origin/sub/AST-500/AST-501-encoded-batch-for-qualify-and-evaluate-jd` @ `ed193fa1`.

- **Plan / code — OK:** `_strict_encoded_batch_consult_envelope_err` limited to `qualify_job_listings` + `evaluate_jd` matches ticket + `ASTRAL_CODE_RULES` batch consult intent; `grades_encoded*` / `grades_encoded_notes` `output_types` mandate the outer envelope and drop the contradictory “lines only / RESPOND ONLY…” tail; dispatcher component test locks a single `run_consult_task` await with full claimed entity list for `batch_call_mode=1`; agent tests cover bare pipe text and structured `agent_payload` object cases.
- **Advisory (D2):** Strict-envelope branch wraps `_store_response_block` in bare `except`; same broad pattern exists elsewhere in `do_task` — fine if intentional parity; tie to rubric tradeoff in a one-line comment only if you want clearer audit rationale.

**Radia doc cherry-pick:** `04445e0e1ad00ac3a635ff3d50bc1b7095dd842c` — `git cherry-pick 04445e0e1ad00ac3a635ff3d50bc1b7095dd842c` onto engineer branch, then re-publish if needed. Findings also in `docs/features/consult/ast-501-encoded-batch-for-qualify-and-evaluate-jd.md` **`## Review`** on the publish ref tip.

#### betty — 2026-05-27T03:24:39.990Z
1. `tests/component/core/test_dispatcher.py::TestRunUnified::test_ast501_job_batch_call_mode_single_run_consult_with_all_claimed_entities` — `batch_call_mode=1` invokes `consult.run_consult_task` once with the full claimed job list (`len==2`).
2. `tests/component/core/test_agent.py::TestDoTask::test_ast501_rejects_evaluate_jd_when_api_returns_bare_encoded_lines_without_envelope` — bare multi-line encoded text without `{ agent_performance, agent_payload }` fails `do_task`.
3. `tests/component/core/test_agent.py::TestDoTask::test_ast501_rejects_evaluate_jd_when_agent_payload_is_structured_json_object` — structured JSON object inner `agent_payload` rejected for `evaluate_jd`.

Existing coverage retained: `tests/component/core/test_consult.py`, `evaluate_jd` / `qualify_job_listings` `_run_batch_consult` paths; `./scripts/testing/run_component_tests.sh` wholesale per harness when widening.

**Publish:** `origin/sub/AST-500/AST-501-encoded-batch-for-qualify-and-evaluate-jd` @ **`ed193fa1`** — `origin/ftr/AST-500-high-volume-encoded-batch-consult-migrate-all-stages-cache-first-exhaustion-runs` advanced with the same tip (fast-forward); bible blob `sha1 a9de57321a8c8ba275791dcbb90ca30c3240325c` matches on both refs.

§ `docs/ASTRAL_TEST_BIBLE.md` **§7.13zf** (AST-502/503 rows TBD).

— Betty

#### hedy — 2026-05-27T03:03:44.164Z
**Published plan:** [docs/features/consult/ast-501-encoded-batch-for-qualify-and-evaluate-jd.md](https://github.com/susansomerset/astral/blob/sub/AST-500/AST-501-encoded-batch-for-qualify-and-evaluate-jd/docs/features/consult/ast-501-encoded-batch-for-qualify-and-evaluate-jd.md)

**Self-assessment (with justifications)**

- **Scope — scope-Single-Component:** Dispatcher, consult routing, tight `agent` envelope path, `output_types`/seed prompts, targeted tests—all scoped to qualify + `evaluate_jd`; explicitly defers chunk fan-out (AST-502) and DO/GET/LIKE (AST-503).
- **Conf — conf-high:** Failure mode traced against `_warm_then_gather` vs `batch_call_mode`, `_run_batch_consult`, and contradictory `grades_encoded_notes` tails; residual unknown is only if Susan’s reproduction implies different `dispatch_tasks` shaping than repo code.
- **Risk — risk-HIGH:** Incorrect tightening could strand jobs, double-handle retries, or mis-parse valid provider output—shows up immediately in JOB_STATES / dispatcher ledger.

---

# AST-501 — Encoded batch for qualify_job_listings and evaluate_jd

**Linear:** [AST-501](https://linear.app/astralcareermatch/issue/AST-501/encoded-batch-for-qualify-and-evaluate-jd-high-volume-encoded-batch)  
**Parent epic:** [AST-500](https://linear.app/astralcareermatch/issue/AST-500/high-volume-encoded-batch-consult-migrate-all-stages-cache-first)  
**Project:** Astral Consult  
**Publish ref:** `origin/sub/AST-500/AST-501-encoded-batch-for-qualify-and-evaluate-jd` (canonical ticket work — not a local checkout)

Restore **one `do_task` per claimed batch** for **`qualify_job_listings`** and **`evaluate_jd`**: assembled live content carries **all N jobs**, `agent_payload` delivers **N newline-separated encoded lines**, outer JSON envelope (**`agent_performance` + `agent_payload`**) is always present when the agent succeeds. Eliminate silent regression to **`_warm_then_gather` per job** where **`dispatch_tasks.batch_call_mode = 1`**. Align provider-facing instructions (`TASK_CONFIG`-driven **`output_types`**, DB-managed prompts via agent_task rows where applicable) so models do **not** return bare pipe-lines, unstructured expanded JSON blobs, or “inner lines only.” **Leave multi-chunk parallel exhaustion to AST-502** — this ticket fixes **single-call multi-line correctness** inside one consult batch invocation.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/dispatcher.py` | Confirm and, if necessary, tighten comments or guards around `batch_call_mode` branching so qualifying/evaluate never fall through to per-job gather when DB says batch; optional debug log citing `batch_call_mode`, `batch_size`, and `len(entities)` once per `_run_unified` consult batch (no heuristic caps). | core |
| `src/core/consult.py` | Confirm `qualify_job_listings` / `evaluate_jd_batch` always receive the **full** claimed entity list passed from `run_consult_task` (already thin wrappers around `_run_batch_consult`). If any edge path slices to one entity, remove it (only explicitly single-job tools like admin paths may diverge — not dispatched AUTO/CLICK runners). Document in-code that **one** `_run_batch_consult` ⇒ **one** API round-trip. | core |
| `src/utils/config.py` | **`ASTRAL_CONFIG["output_types"]`**: revise `grades_encoded`, `grades_encoded_meta` (**qualify**) instructions to **require** the standard envelope; inner `agent_payload` is the multi-line encoded string (**no JSON arrays of jobs inside `agent_payload`**). Fix **`grades_encoded_notes`** (**do/get/like**) example tail if it contradicts envelope + inner-string contract — scoped here only because the broken tail lives beside qualify/evaluate instructions in the same registry (**AST-351 alignment**); **leave DO/GET/LIKE batch routing to AST-503**. | utils |
| `src/core/agent.py` | Narrow or gate any “bare string / coerce to lines” workaround paths so they **never** bypass envelope validation for production consult tasks (**qualify_job_listings**, **`evaluate_jd`**). If coexistence with legacy adhoc tasks is needed, gate on `task_key` or explicit `output_type`; **consult batch keys must enforce envelope-first** parsing. Optionally extend structured logging where decode fails after API success (**include first ~N chars only in debug path** existing pattern). Document decision inline. | core |
| `src/data/database.py` | Verification-only pass: **`_DISPATCH_TASK_SEED`** (or equivalent seed) confirms **`batch_call_mode`** seed intent matches product for qualify/evaluate; **no runtime hard-coded default** replacing DB `batch_size`. If seed rows are wrong for dev/test DBs used in CI, align seed text only — orchestration stays DB-driven (**ASTRAL_CODE_RULES §2.1**). | data |
| `tests/component/core/test_dispatcher.py` (or adjacent) | **Component test:** when `batch_call_mode` truthy stub path, `_run_unified` invokes **`run_consult_task` once with `entities` length > 1** (mock `consult`). | tests |
| `tests/component/core/test_agent.py` or `tests/component/core/test_consult.py` | Regression: encoded multi-job envelope survives validation + `_decode_payload` producing **`len(parsed["jobs"]) == N`** for N-line payload (reuse existing harness patterns). | tests |

---

## Stage 1: Trace and lock the dispatched path

**Done when:** You can cite the exact branch from **`dispatcher._run_unified`** through **`consult.run_consult_task`** → **`evaluate_jd_batch` / `qualify_job_listings`** for **`batch_call_mode=1`** and show it issues **exactly one** `asyncio`-await chain to **`_run_batch_consult`** per dispatcher batch (**not one per entity via `_warm_then_gather`**).

1. In `src/core/dispatcher.py`, read `_run_unified` (`batch_call_mode` branch vs `_warm_then_gather`). Confirm `bool(task.get("batch_call_mode", 0))` is the sole switch; **document** inline if anything else can force per-job mode.
2. In `src/core/consult.py`, read `run_consult_task`: confirm **`evaluate_jd`** / **`VALID_TITLE`** (qualify mapping in `_INPUT_STATE_TO_TASK`) pass **the full `entities` list** into `evaluate_jd_batch` / `qualify_job_listings` without truncating.
3. Grep **`_warm_then_gather`** call sites — assert only **`batch_call_mode=0`** consult paths remain on it (**consult_do/get/like** today — out of scope to migrate here).

⚠️ **Decision:** Root cause assumption for Susan’s “one assessment per job” UAT symptom: **`dispatch_tasks.batch_call_mode`** was **`0`** in the exercised environment **and/or** models returned non-envelope payloads that forced fallback decode paths — **confirm on failing repro** before narrowing code; if **`batch_call_mode=1`** in DB yet per-job persists, escalate with ledger + `dispatch_task.id` snippet in Linear.

---

## Stage 2: Envelope-first instructions and coercion policy

**Done when:** `grades_encoded*` `payload_instructions` and consult agent_task prompts (**DB**, sync’d from repo seed where applicable) **all** instruct: respond with **`{ "agent_performance": …, "agent_payload": "<multi-line-string>" }`**, where inner payload is newline-separated **`000|…`** lines (**no nested `jobs` JSON inside `agent_payload`**). Contradictory “lines only” or “RESPOND ONLY WITH THIS JSON…” tails that confuse inner vs outer shape are removed or rewritten.

1. In `src/utils/config.py`, under **`ASTRAL_CONFIG["output_types"]`**, rewrite **`grades_encoded`**, **`grades_encoded_meta`** `payload_instructions` to add an explicit bullet: outer object keys **`agent_performance`** + **`agent_payload`** (reuse wording from **`response-schema-envelope-plan.md`** / existing consult docs if present in repo — **prefer copy-paste from working `grades_encoded`** block patterns).
2. Fix **`grades_encoded_notes`** (**do/get/like**) tail used in **`TASK_CONFIG`** for **`grade_*`**: remove **`OUTPUT FORMAT: ** RESPOND ONLY WITH THIS JSON FORMAT…`** (contradicts inner compact lines). Replace with envelope + **`agent_payload`** string wording consistent with **`grades_encoded`** (**do not** tell the model inner payload is unstructured JSON).

3. If **`agent_task` `user_prompt` / `system_prompt` DB rows** mirror obsolete text, update **`database.py` seed definitions** (`agent_task`-related seed) **only where this repo owns them**, so fresh environments match **`TASK_CONFIG`** token behavior — **Susan may own production DB deltas**; call that out if seed is bypassed.

---

## Stage 3: Strict envelope handling for batch consult decode path

**Done when:** For **`task_key IN ("qualify_job_listings", "evaluate_jd")`**, a response that parses as bare multi-line pipe text **without** the envelope fails early with the same **`do_task`** error surface as broken JSON — **never** silently coerced into **`parsed_response`** that bypasses **`agent_performance`**.

1. In `src/core/agent.py`, trace **`do_task`** after API success (`parsed` extraction through `_decode_payload`). Identify branches that stringify / wrap non-dict payloads.
2. Restrict coercion: **consult batch keys listed above must require dict envelope before treating `agent_payload` as encoded string.** If other tasks relied on coercion, whitelist them **explicitly by `task_key`** — default strict for **`qualify_job_listings`** and **`evaluate_jd`**.
3. Preserve **`_validate_response_schema`** behavior: encoded inner string exits early (**no dict field validation**) until **`agent_payload`** is promoted — **already correct** — ensure coercion does not replace `parsed` dict before `_validate_response_schema` runs envelope checks.

⚠️ **Decision:** Prefer **narrow whitelist** (`if task_key in (...): strict`) over heuristics (string length / pipe count). Avoid new global limits (**Susan rule**).

---

## Stage 4: Partial-line omission behavior (ticket notes)

**Done when:** Code matches **`_run_batch_consult`** contract already in `consult.py`: missing job IDs vs sent batch → **`retry_state`** when configured else **`error_state`**; **`process_fn` exceptions** accumulate **`bad_grades`** → **`retry_state`**. Acceptance: **omit line** ⇒ **retry** not whole-batch **`error_state`** unless envelope/`do_task` failed.

1. Read `_run_batch_consult` (**missing**, **fabricated**, **bad_grades** transitions). Align any agent-side skips (e.g. `_decode_payload` pos out-of-range **skip line**) with **overall job accounting**: skipped line must correlate with **retry** (**same as missing ID**) — `_decode_payload` **warning + skip** already documented; **`_run_batch_consult`** treats missing **`astral_job_id`** in **`response_jobs`** — confirm end-to-end: if model omits **`pos`** line entirely, **`response_jobs`** shorter → **retry** (**existing `missing set`** logic). Do **not** invent new truncation limits.

---

## Stage 5: Tests + manual verification checklist

**Done when:** New/updated automated tests green; checklist below reproducible locally.

1. Component test mocking **`consult.run_consult_task`**: `_run_unified` + **`batch_call_mode=1`** + **job** **`entity_type`**, claimed **two** stubs → mocked coroutine awaited **once** with **`len(entities)==2`**.
2. Fixture or mocked Anthropic reply: envelope JSON → **`agent_payload`** with **two** newline lines → **`_decode_payload`** → **`parsed["jobs"]` length == 2** for **`evaluate_jd`** (**`grades_encoded`**) path.
3. Negative: bare two-line pipe payload **without** envelope → **`do_task` success False** (**strict whitelist path**).

**Manual (Susan / UAT scripting):**

- ADMIN: confirm **`dispatch_tasks`** rows for **`qualify_job_listings`**, **`evaluate_jd`** → **`batch_call_mode = 1`**, **`batch_size > 1`**.
- Run one CLICK dispatch with **N≥2** eligible jobs; verify **exactly one** timesheet/request per batch (not **N**) and **`agent_payload` line count**.

---

## Self-Assessment

### Scope — **scope-Single-Component**

Touches **dispatcher**, **consult** routing, **`agent`** validation edge, **`config` output_types**, optional **seed** rows, and targeted **tests** — all constrained to qualifying + JD-evaluate orchestration (**no AST-502 chunk splitter, no AST-503 DO/GET/LIKE**).

### Conf — **conf-high**

Concrete failure mode was traced in codebase: **`_warm_then_gather` vs `batch_call_mode`**, **`_run_batch_consult` already batches**, and **`grades_encoded_notes` contradictory instruction block** identified for removal; residual risk only if **`dispatch_tasks` drift** contradicts Susan’s reproduction.

### Risk — **risk-HIGH**

Wrong fix could **suppress valid provider responses**, **strand jobs** in trigger states, or **double-transition** retries — regressions surface in **dispatcher ledger** / **JOB_STATES**.

---

## Plan vs ASTRAL_CODE_RULES cross-check

- **§2.4 batch_id:** Preserve existing **`batch_id`** from **`log_batch_id`** throughout one batch consult (**no redesign** unless AST-502 lands).
- **§2.1 config:** **`batch_size` / `batch_call_mode`** authoritative from **`dispatch_tasks` DB** — no invented defaults in Python.
- **§2.6 state machine:** Existing **`retry_state`** / **`error_state`** semantics from **`JOB_STATES`** — **reuse** **`_transition_job_state_for_task`**.
- **§3.3 imports:** No **`ui` → core** crossings; **`data` edits** confined to documented seed/header if touched.

---

## Review

**Diff:** `origin/dev...origin/sub/AST-500/AST-501-encoded-batch-for-qualify-and-evaluate-jd` @ `ed193fa1a865bffe3d88e0e1fcc34aa20050ac9b`

### What's solid
- Narrow envelope gate `_strict_encoded_batch_consult_envelope_err` keyed to **`qualify_job_listings`** and **`evaluate_jd`** matches AST-351 + plan Stage 3; regression tests reject bare compact lines and a structured **`agent_payload`** object masquerading as inner text.
- **`ASTRAL_CONFIG["output_types"]`** now mandate the **`agent_performance` + `agent_payload`** envelope across **`grades_encoded` / `grades_encoded_meta` / `grades_encoded_notes`**, removes the contradictory "RESPOND ONLY WITH THIS JSON…" tail on **`grades_encoded_notes`** (plan Stage 2).
- Dispatcher debug line records **`batch_call_mode`**, dispatch **`batch_size`**, and **`len(entities)`** alongside **`bid`** — useful corroboration for single-call **`run_consult_task`** UAT.
- **`tests/component/core/test_dispatcher.py`** locks one **`await run_consult_task`** with **`len(entities)==2`** for **`evaluate_jd`** **`batch_call_mode=1`** path.

### Issues / follow-ups

| Severity | Bucket | Topic | Notes |
| -------- | ------ | ----- | ----- |
| Advisory | D2 parity | Bare `except` around `_store_response_block` after strict-envelope rejection | Mirrors other **`do_task`** storage swallow patterns; acceptable if parity is deliberate — add a tying comment (**`ASTRAL_CODE_RULES`** §1.5 / AST-388) only if you want sharper audit rationale. |

### Recommended actions

No **fix-now** items for **`resolve-astral`**; optional comment-only hardening above.

---

## Resolution (`resolve-astral`)

**Date:** 2026-05-26  

**Against:** Radia `review-astral` § **Review** on `origin/sub/AST-500/AST-501-encoded-batch-for-qualify-and-evaluate-jd` @ **`ed193fa1`**.

**Product / plan**

- **`fix-now`:** None — envelope gate, **`output_types`**, dispatcher single-call assertion, and regression tests landed as-reviewed; **`dev-hedy`** was aligned to the canonical publish tip (Radia **`docs(AST-501): …`** merge) before this appendix.
- **Advisory — bare `except` around `_store_response_block`:** Accepted as **`do_task` parity** with existing swallow patterns; **no** one-line rationale comment unless a future readability pass asks for it (**AST-501** scope unchanged).
