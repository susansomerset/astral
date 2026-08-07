<!-- linear-archive: AST-903 archived 2026-08-02 -->

## Linear archive (AST-903)

**Archived:** 2026-08-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-903/uat-craft-get-rubric-json-parse-unterminated-string  
**Status at archive:** Archive  
**Project:** Astral Consult  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-900 — craft get rubric did not populate the rubric content for candidate  
**Blocked by / blocks / related:** parent: AST-900

### Description

## What failed

On `/artifacts/get_job_criteria` for candidate `karfo`, Generate for Get Job Criteria failed with an Astral error diagnostic while craft_DO succeeded on the same session.

```
message: Failed to parse JSON response: Unterminated string starting at: line 43 column 20 (char 5489)
route: /artifacts/get_job_criteria
astral_candidate_id: karfo
```

The diagnostic showed `agent_performance.status=success` with `vector_reviews` present, but `agent_payload.criteria[0].content` was truncated mid-string (`"A == The JD's target title exactly matches or is `), so JSON parse failed.

## Expected

A successful Get rubric generation returns parseable JSON with a complete `criteria` array, and the editor shows the criteria for review (or a clear recoverable error — not a truncated payload treated as success).

## Repro

1. Open candidate `karfo` → Artifacts → Get Job Criteria.
2. Click Generate (or Regenerate).
3. Observe Astral error diagnostic: Failed to parse JSON response / Unterminated string (Get fails; Do may still succeed).

## Parent AC (quoted inline)

> Generating Get Job Criteria for a candidate with an empty rubric ends with the criteria visible in the editor, and after Save they are present in the candidate's stored artifact.
> A generation that completes on the backend can no longer vanish without a user-visible trace: the editor shows the result or an error, or the completed result is recoverable when the user returns to the page.

## Boundaries

* This bug does **not** change: rubric grading semantics, dispatcher consult batches (`grade_get`), or Do/Like rubric prompt content unless required to fix Get parse/truncation.
* Artifact editor Save/recovery UX after a successful on-screen generate is the sibling UAT bug.

### Comments

#### radia — 2026-07-16T22:53:32.442Z
### Radia review — clean

Diff: `origin/dev`…`origin/sub/AST-900/AST-903-uat-craft-get-json-parse` @ `926dfca` (product tip `a3d971c` + this doc commit).

Plan doc: https://github.com/susansomerset/astral/blob/926dfcaa86387a76091b6de430ab805d985e4cc3/docs/features/consult/ast-903-uat-craft-get-json-parse.md

No fix-now / discuss.

**Solid:** Stages 1–3 match plan — `CRAFT_RUBRIC_MAX_TOKENS=32000` floor in `do_task` for `CRAFT_RUBRIC_UI_TASK_KEYS`; Anthropic + DeepSeek hard-fail JSON when `stop_reason == "max_tokens"` before heal/parse (`failure_class: max_tokens`); Stage 4 no-op confirmed (`run_candidate_artifact_generation` already forwards `error` + ledger `FAILED`). §5g clean (no cross-external imports; own logger per provider). Timesheet `except` mirrors existing parse_err pattern. Text `max_tokens` still succeeds. No ArtifactEditor / prompt / `grade_*` scope creep.

**Advisory:** Truncation path double-calls `log_llm_batch_summary` (success then error) — same as existing parse_err path; not blocking.

#### betty — 2026-07-16T22:51:14.326Z
## QA test manifest — AST-903

**Publish:** `origin/sub/AST-900/AST-903-uat-craft-get-json-parse` @ `a3d971c` (`merge-tests(AST-903): origin/tests 936aba51aaa19bfe66d2eaf36c425f6251f08521`)

### Manifest (run all)

1. `tests/component/core/test_agent.py::TestAst903CraftRubricMaxTokensFloor` — `craft_get_rubric` floors `max_tokens` to 32000; non-craft keeps agent 100
2. `tests/component/utils/test_config.py::TestAst903CraftRubricMaxTokens` — `CRAFT_RUBRIC_MAX_TOKENS == 32000`
3. `tests/component/external/test_deepseek.py::TestAst903JsonMaxTokensHardFail` — JSON + `stop_reason=max_tokens` → `failure_class`; text format still succeeds
4. `tests/component/external/test_anthropic.py::TestAst903JsonMaxTokensHardFail` — same hard-fail gate

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst903CraftRubricMaxTokensFloor \
  tests/component/utils/test_config.py::TestAst903CraftRubricMaxTokens \
  tests/component/external/test_deepseek.py::TestAst903JsonMaxTokensHardFail \
  tests/component/external/test_anthropic.py::TestAst903JsonMaxTokensHardFail
```

### Existing coverage

- No obsolete tests for this diff (new fail-closed path + config floor)
- Stage 4 (candidate generate forwards provider error) covered by existing `TestRunCandidateArtifactGeneration` failure path — no new candidate tests required

### Bible shasums on publish ref

- `docs/test-bible/core/agent.md` `f30b5bcb012057ab3a9aa61ef5ff3bb972a0a548`
- `docs/test-bible/utils/config.md` `a66570852e826a1bf95ae081a1f84ff326cd30cf`
- `docs/test-bible/external/deepseek.md` `81c14a81c98a4aae910ba4a900d792f7264a90d3`
- `docs/test-bible/external/anthropic.md` `266699e17c75cfb5db40d70f4fd4b1ce4449ed78`

— Betty

#### ada — 2026-07-16T22:46:20.233Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-900/AST-903-uat-craft-get-json-parse/docs/features/consult/ast-903-uat-craft-get-json-parse.md @ `4d706d41d04f6ab39d93c6d3e8e69a26b5aab465`

**Root cause:** LLM output truncated mid-`agent_payload.criteria[0].content` (`Unterminated string`). `heal_json` cannot recover when truncation is inside the first criterion string. Do succeeded same session because its payload fit the token budget.

**Fix:** `CRAFT_RUBRIC_MAX_TOKENS=32000` floor in `do_task` for all craft rubric UI tasks; hard-fail JSON provider calls when `stop_reason == max_tokens` (no heal-into-partial-success).

**Scope:** `Single-Component` — config + agent params + deepseek/anthropic gate; no UI / prompts / consult batches.

**Conf:** `high` — truncation signature is unambiguous.

**Risk:** `Medium` — higher cost/latency on six craft rubrics; intentional fail-closed on max_tokens.

---

# UAT: craft_get_rubric JSON parse Unterminated string

**Parent:** [AST-900 — craft get rubric did not populate the rubric content for candidate](https://linear.app/astralcareermatch/issue/AST-900/craft-get-rubric-did-not-populate-the-rubric-content-for-candidate)

**Linear:** [AST-903](https://linear.app/astralcareermatch/issue/AST-903/uat-craft-get-rubric-json-parse-unterminated-string)

**Publish ref:** `origin/sub/AST-900/AST-903-uat-craft-get-json-parse`

**Summary (FIX-UAT):** On `/artifacts/get_job_criteria` for `karfo`, Generate failed with `Failed to parse JSON response: Unterminated string` while craft_DO succeeded in the same session. The raw model body showed envelope `agent_performance.status=success` with `vector_reviews`, but `agent_payload.criteria[0].content` was cut mid-string — classic output truncation. This ticket hardens craft rubric JSON generation so truncation cannot look like a silent/ambiguous success: raise the craft-rubric token budget and fail clearly when `stop_reason == max_tokens` (or equivalent truncated JSON). Sibling editor Save/recovery UX stays out of scope.

---

## Root cause (UAT)

| Fact | Implication |
|------|-------------|
| Error: `Unterminated string` at mid-`content` in first criterion | JSON cut mid-value — not schema/prompt content wrongness |
| Envelope already had `agent_performance.status=success` | Model started a full craft envelope; output budget ran out before close |
| `craft_do_rubric` succeeded same session | Get criteria text is longer / hit limit first; Do fit |
| `heal_json` / `heal_agent_payload_envelope` | Envelope healer targets string `agent_payload` line formats (qualify/eval); craft rubrics nest `criteria[]` objects. Truncation inside the first criterion string leaves no complete array element to checkpoint → parse fails |

**Conclusion:** Delivery/hardening from AST-901 is not the bug. The LLM response was truncated (`max_tokens` / incomplete JSON). Product must (1) give craft rubrics enough output budget and (2) treat truncation as an explicit generate failure, not a heal-into-partial-success path.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `CRAFT_RUBRIC_MAX_TOKENS` literal; document use for craft rubric UI tasks | utils |
| `src/core/agent.py` | Apply craft-rubric max_tokens floor when resolving agent params for `CRAFT_RUBRIC_UI_TASK_KEYS` | core |
| `src/external/deepseek.py` | On JSON `response_format`, if `stop_reason == "max_tokens"`, return `success=False` with truncation error **before** heal/parse success | external |
| `src/external/anthropic.py` | Same `stop_reason == "max_tokens"` hard-fail for JSON `response_format` | external |

**Not in scope:** `ArtifactEditor.tsx`, rubric prompts/schemas, `grade_get` / dispatcher consult batches, Do/Like prompt bodies, AST-902 recovery UX.

---

## Stage 1: Config — craft rubric max_tokens floor

**Done when:** `CRAFT_RUBRIC_MAX_TOKENS` is importable from `config.py` next to `CRAFT_RUBRIC_UI_TASK_KEYS`.

1. In `src/utils/config.py`, immediately after `CRAFT_RUBRIC_UI_TASK_KEYS`, add:
   ```python
   # Output budget for craft_*_rubric UI generate (long per-criterion content).
   # Applied as a floor in do_task when the agent/model default is lower.
   CRAFT_RUBRIC_MAX_TOKENS = 32000
   ```
2. No other config keys.

⚠️ **Decision:** `32000` floor — Get rubrics regularly emit large `content` strings across many criteria; DeepSeek/Anthropic model defaults (8k–16k) are what truncated `karfo`. Floor (not hard override downward) so an admin-raised agent `max_tokens` still wins when higher.

---

## Stage 2: `do_task` applies craft-rubric token floor

**Done when:** For every `task_key in CRAFT_RUBRIC_UI_TASK_KEYS`, the `max_tokens` passed to the provider is `max(agent_max_tokens, CRAFT_RUBRIC_MAX_TOKENS)`.

1. In `src/core/agent.py`, import `CRAFT_RUBRIC_UI_TASK_KEYS` and `CRAFT_RUBRIC_MAX_TOKENS` from config.
2. Where `agent_max_tokens` is resolved (~1882), after computing `agent_max_tokens` from agent row / model default:
   ```python
   if task_key in CRAFT_RUBRIC_UI_TASK_KEYS:
       agent_max_tokens = max(int(agent_max_tokens), int(CRAFT_RUBRIC_MAX_TOKENS))
   ```
3. Existing debug/log lines that print `max_tokens` keep using the raised value.

---

## Stage 3: Hard-fail JSON responses truncated by `max_tokens` (DeepSeek + Anthropic)

**Done when:** Provider clients never return `success=True` with a healed/partial parse when the API `stop_reason` is `max_tokens` and `response_format == "json"`.

1. In `src/external/deepseek.py` `send_to_deepseek`, after the API response is received and `stop_reason = getattr(response, "stop_reason", None)` is available (same place debug already reads it):
   - If `response_format == "json"` and `stop_reason == "max_tokens"`:
     - Log via existing batch summary / error path.
     - Return immediately:
       ```python
       {
         "success": False,
         "api_response": response,
         "parsed_response": None,
         "timesheet": timesheet,
         "error": "Generation truncated (max_tokens) before complete JSON",
         "failure_class": "max_tokens",
       }
       ```
     - Do **not** call `_parse_json_response` / heal on this path.
2. Mirror the same gate in `src/external/anthropic.py` `send_to_anthropic` (same return shape keys the rest of `do_task` already consumes).
3. Timesheet: if timesheet kwargs are already built, record `agent_performance="failure"` with `failure_note` containing `max_tokens` (same pattern as existing parse_err failure branch).

⚠️ **Decision:** Fail-closed on `max_tokens` for JSON — heal that closes mid-`content` could invent incomplete criteria and look “successful.” Parent AC prefers complete criteria **or** a clear error.

---

## Stage 4: Craft generate surfaces truncation clearly (smoke path)

**Done when:** `run_candidate_artifact_generation` for a craft rubric task returns HTTP 500 with the truncation error string when the provider returns the Stage 3 failure (no code change required if the existing `result.get("error")` path already forwards it).

1. Verify in `src/core/candidate.py` that the existing failure branch (`not result.get("success")`) returns `error` from Stage 3 unchanged and marks ledger `FAILED`.
2. If `failure_class == "max_tokens"` is dropped before the API body: include `error` only (sufficient for UI toast). Do **not** add frontend changes.

No product edit in this stage if verification shows the existing path already forwards `error`.

---

## Execution contract (for build-child)

- Stages in order; one `code(AST-903): …` commit per stage (or Stage 4 skipped with a note in Build stub if no-op).
- Publish each to `origin/sub/AST-900/AST-903-uat-craft-get-json-parse`.
- Do not edit prompts, `response_schema`, ArtifactEditor, or consult `grade_*` paths.
- If Anthropic SDK uses a different stop-reason string than `"max_tokens"`, stop and comment on AST-903 with the observed value — do not invent aliases without evidence.

---

## Self-Assessment

**Scope:** `Single-Component` — config floor + `do_task` param + twin provider hard-fail; no UI.

**Conf:** `high` — truncation signature matches `Unterminated string` mid-`content`; Do-vs-Get same session points at output budget; fail-closed on `max_tokens` matches parent AC.

**Risk:** `Medium` — raising max_tokens increases cost/latency for all six craft rubrics; hard-fail may surface truncations that previously healed into partial (incorrect) JSON — intentional.

---

## Build

- **Publish tip:** `origin/sub/AST-900/AST-903-uat-craft-get-json-parse` @ `96b2200643a2fcb878c115058db2261f44463bd8`
- Stage 1: `6868d6f` — `CRAFT_RUBRIC_MAX_TOKENS = 32000`
- Stage 2: `721e1bf` — `do_task` floor for `CRAFT_RUBRIC_UI_TASK_KEYS`
- Stage 3: `96b2200` — DeepSeek + Anthropic hard-fail on JSON `stop_reason == max_tokens`
- Stage 4: no-op — `run_candidate_artifact_generation` already forwards `result["error"]` and marks ledger `FAILED`

## Review

**Radia** · `origin/dev`…`origin/sub/AST-900/AST-903-uat-craft-get-json-parse` @ `a3d971c` · product `6868d6f` + `721e1bf` + `96b2200` (Stage 4 no-op verified)

### What's solid

- **Plan fidelity:** Stages 1–3 match. `CRAFT_RUBRIC_MAX_TOKENS = 32000` after `CRAFT_RUBRIC_UI_TASK_KEYS`; `do_task` floors with `max(agent_max_tokens, CRAFT_RUBRIC_MAX_TOKENS)` only for craft-rubric UI keys; both providers hard-fail JSON when `stop_reason == "max_tokens"` **before** heal/parse, return `failure_class: "max_tokens"` + the planned error string, record timesheet failure. Stage 4 no-op confirmed: `run_candidate_artifact_generation` already forwards `result["error"]` and marks ledger `FAILED`.
- **§2.1 / §2.2:** Token floor is config; core raises the budget; external owns stop_reason I/O gate.
- **§5g external cleanliness:** No cross-external imports; each module emits with its own logger / provider label (`anthropic` / `deepseek`). Duplicated gate is plan-mandated mirror of the existing parse-failure return shape (not a shared helper smuggled across providers).
- **D2 timesheet:** `except Exception: pass` around `record_timesheet` on the truncation path matches the pre-existing parse_err branch — justified by plan Stage 3 (“same pattern”).
- **Boundaries:** No ArtifactEditor / prompt / schema / `grade_*` scope creep. Text `max_tokens` still succeeds (tests cover).
- **Self-Assessment:** Diff footprint matches **Single-Component** / high conf; Medium risk (cost + fail-closed) is intentional.

### Issues

None (no fix-now / discuss).

### Advisory (not fix-now)

- Truncation path calls `log_llm_batch_summary` twice (success-with-response earlier in the function, then error) — same as the existing parse_err path; operators may see a success duration line before the truncation error. Pre-existing shape; no change required for this ticket.

### Recommended actions

| Action | Owner | Notes |
|--------|-------|-------|
| _(none)_ | — | Clean — ready for resolve-child / merge-child rollup |

## Resolution

**2026-07-16** — Radia clean sign-off (`docs(AST-903): Radia review — clean` @ `926dfca`). No fix-now / discuss. No product delta this resolve pass. Advisory (double `log_llm_batch_summary`) accepted as pre-existing parse_err shape.

---

## Rules review (relevant)

| Rule | Compliance |
|------|------------|
| §2.1 config | Token floor as config literal; applied only for `CRAFT_RUBRIC_UI_TASK_KEYS`. |
| §2.2 | Core raises budget; external owns provider I/O and stop_reason gate. |
| §1.3 DRY | Same gate in anthropic + deepseek mirrors existing parse-failure return shape. |
| §3.3 | No new cross-layer imports from UI/data. |
