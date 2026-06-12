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
