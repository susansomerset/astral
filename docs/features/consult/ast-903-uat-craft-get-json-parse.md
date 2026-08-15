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

---

## Bug: AST-1380 — craft_get_rubric RESPONSE truncation (289-token cut)

**Parent:** AST-1379 (orphaned mini-parent; `ftr/AST-1379-response-truncated-after-289-tokens` off `origin/dev`).  
**Publish ref:** `origin/sub/AST-1379/AST-1380-fix-craft-get-rubric-truncation`  
**Ancestor:** this doc (AST-903) — prior craft_get truncate + `CRAFT_RUBRIC_MAX_TOKENS=32000` + JSON `stop_reason==max_tokens` hard-fail. Archived; no related-issue link.

### As-is

`craft_get_rubric` for candidate `abrams` (batch `craft_get_rubric-ff19fa20-5f6d-469c-a1bf-5c09b4574948`) stores a RESPONSE whose `block_data` cuts mid-criteria after ~289 tokens (`token_size: 289`). The model envelope shows `agent_performance.status=success` with a full `vector_reviews` list, but `agent_payload.criteria` is incomplete (first criterion `content` ends mid-grade-row at `…even though no title`; remaining criteria never written). Downstream parse/use treats that truncated payload like a finished hop.

### To-be

A successful `craft_get_rubric` RESPONSE is complete, parseable JSON with every crafted criterion fully written — **or** the hop fails loudly under the existing `max_tokens` / unusable-response failure class. Never `agent_performance.status=success` (or hop success) with a partial truncated payload.

### Repro

1. Candidate `abrams` → generate `craft_get_rubric` (UI generate or REQUESTED_ARTIFACTS chain entry — both call `do_task`).
2. Inspect RESPONSE for batch `craft_get_rubric-ff19fa20-5f6d-469c-a1bf-5c09b4574948` (or a fresh re-run with `debug=True`).
3. Observe `token_size ≈ 289` and mid-`criteria[].content` cut while the envelope still claims `agent_performance.status=success`.

### Root cause

AST-903’s controls are still present on this tree:

- `CRAFT_RUBRIC_MAX_TOKENS = 32000` in `src/utils/config.py`
- `do_task` floors `max_tokens` for every `task_key in CRAFT_RUBRIC_UI_TASK_KEYS` (`src/core/agent.py`)
- DeepSeek + Anthropic hard-fail JSON when `stop_reason == "max_tokens"` before heal/parse (`failure_class: max_tokens`)

The abrams cut is the same truncation *signature* as AST-903 (`karfo`), so one of these holes is still open (confirm which on the live hop before coding):

1. **Budget starvation under thinking** — `craft_get_rubric` uses agent `ats_expert_atlas` (`brain_setting=Big`). On DeepSeek, Big enables thinking (`reasoning_effort=max`). Thinking tokens share the same `max_tokens` budget as the visible JSON answer, so the text block can stop mid-`criteria[].content` after a few hundred estimated tokens even when the floor sent `32000`.
2. **Hard-fail miss** — truncation lands without `stop_reason == "max_tokens"` (or the gate is skipped), and heal/parse still yields a success-shaped path; or raw truncated envelope is stored as the RESPONSE audit body with no failure marker so operators/downstream read `status=success` inside the blob.
3. **Floor bypass** — unlikely for current `do_task` (UI generate and REQUESTED_ARTIFACTS both call it with `task_key=craft_get_rubric`); only reopen if debug shows `max_tokens < 32000` on the hop.

`heal_json` does **not** recover unterminated mid-string craft criteria (same as AST-903). A true `success=True` persist unwraps to `agent_payload` only; a RESPONSE that still contains `agent_performance` is usually the failure-audit raw body (`_audit_response_body` stores raw text with no `Validation failed:` prefix on the provider-failure path).

### Proposed change

Execute in order; stop when the confirmed hole is closed. Do not invent new token caps or “close enough to max_tokens” heuristics without an explicit Decision below.

1. **Confirm the hop (make-fix first action)** — Re-run `craft_get_rubric` for `abrams` (or equivalent) with `debug=True`, or read timesheet + RESPONSE for batch `…ff19fa20…` if still available. Record: `provider`, `brain_setting` / DeepSeek `thinking`, `max_tokens` actually passed to the provider, `stop_reason`, `usage.output_tokens`, whether `do_task` returned `success` / `failure_class`.

2. **If `max_tokens` sent `< CRAFT_RUBRIC_MAX_TOKENS`** — restore the AST-903 floor on that entry path in `src/core/agent.py` (only if a real bypass is found; do not duplicate the existing floor).

3. **If `stop_reason == "max_tokens"` but provider result is still `success=True`** — fix the Stage-3 gate regression in `src/external/deepseek.py` and/or `src/external/anthropic.py`: JSON + `stop_reason == "max_tokens"` must return `success=False`, `failure_class: "max_tokens"`, error `"Generation truncated (max_tokens) before complete JSON"` **before** heal/parse (same return shape as AST-903).

4. **If DeepSeek Big thinking starved the visible JSON** (floor applied, truncation mid-criteria) — apply **Decision A** below so craft rubric hops keep enough output budget for a full `criteria` array.

5. **Fail closed on truncated craft JSON even when heal would run** — In both provider clients, for `response_format == "json"`: if raw text fails `json.loads` with a truncation-class decode error (`Unterminated string` / incomplete JSON) **and** `stop_reason == "max_tokens"`, keep the existing hard-fail (no heal). If diagnose shows truncation with a different `stop_reason` string that still means output-length stop, map that provider value to the same hard-fail **only when observed** (do not invent aliases without evidence — same rule as AST-903 execution contract).

6. **Never surface truncated envelope as a successful craft result** — On provider `success=False` for craft rubric tasks, ensure `run_candidate_artifact_generation` / REQUESTED_ARTIFACTS persist paths do not stash or write criteria; ledger `FAILED` (AST-903 Stage 4 already forwards `error` — verify still true). Prefix provider-failure RESPONSE audit bodies the same way validation failures do (`Validation failed:` / explicit failure banner) so a raw `agent_performance.status=success` envelope cannot be mistaken for a finished hop when browsing `agent_data`.

7. **Verify** — Re-run `craft_get_rubric` for `abrams` (or fixture): either full parseable `criteria` with RESPONSE `token_size` well above a mid-vector cut, or loud `failure_class: max_tokens` (or unusable-response) with no success persist.

⚠️ **Decision A (thinking vs floor):** Prefer **force DeepSeek `thinking=False` for `CRAFT_RUBRIC_UI_TASK_KEYS` only** inside `do_task` when resolving `tier_meta` (structured JSON emit; thinking burns the shared output budget). Alternative if board rejects: raise `CRAFT_RUBRIC_MAX_TOKENS` to a single new config literal large enough for thinking+full criteria — do not add a second ad-hoc number in `agent.py`. Pick one; do not do both.

⚠️ **Decision B (scope):** Same six `CRAFT_RUBRIC_UI_TASK_KEYS` as AST-903 (includes `craft_get_rubric`). No prompt/schema redesign, no `grade_*` / ArtifactEditor, no AST-1190 hollow classification ownership beyond consuming existing failure classes.

### Blast radius

- All six craft rubric UI tasks share the floor / thinking Decision A.
- DeepSeek Big thinking change (if chosen) affects only those task keys’ hops, not other Big-brain tasks.
- Provider hard-fail path already used by AST-903 tests; any gate fix must keep text-format `max_tokens` succeeding.
- Failure-RESPONSE banner change touches every provider-failure audit row shape operators see in Admin agent_data.
- Neighbor AST-1377 parked `craft_do_rubric max_tokens / truncated JSON` as out of epic — this bug owns that symptom family for Get (and shared craft keys if Decision A/B apply).

### What must still hold

- AST-903 AC: craft rubric generate returns complete parseable criteria **or** a clear truncation/unusable failure — never heal-into-partial-success on `max_tokens`.
- `CRAFT_RUBRIC_MAX_TOKENS` remains a floor (`max(agent, floor)`), not a downward override of a higher admin `max_tokens`.
- UI generate and REQUESTED_ARTIFACTS both keep using `do_task` with `task_key=craft_get_rubric` (no parallel provider call path).
- Empty-criteria / pending-stash failure behavior from AST-901 unchanged except that truncated runs must not look like COMPLETED success.
- No changes to rubric grading semantics, consult batches, or craft prompt prose except as required for token/budget correctness (ticket boundaries).

## Radia review-fix (AST-1380)

**Overall:** DISCUSS (no fix-now). Decision A + failure banner solid; AST-903 floor/gates retained.

**discuss (process):**
1. Plan step 1 hop-confirm evidence not recorded in issue doc (code implies thinking starvation).
2. Board TESTS:REVISE deferred to sibling gap **AST-1383** (Todo) — no merge-tests on this sub; expected orphaned-path shape.

**advisory:** unrelated AST-1352 Threads mirror noise in three-dot diff; residual truncate risk if future stop_reason ≠ max_tokens.

**Chuckles:** clean-review shortcut → User Testing; drive AST-1383 for bible/repro coverage before parent finish-up.

## Docs-acceptance (AST-1380)

No test-tree delivery on this sub — Betty TESTS:REVISE filed as sibling gap **AST-1383**.

---

## Bug: AST-1383 — Gap: craft rubric truncated-success RESPONSE coverage (agent bible/tests)

**Parent:** AST-1379 (orphaned mini-parent).  
**Publish ref:** `origin/sub/AST-1379/AST-1383-gap-craft-get-truncation-tests`  
**Sibling product:** AST-1380 (`code(AST-1380)` Decision A thinking-off + provider-failure RESPONSE banner — already on `ftr` / this epic).  
**Source verdict:** AST-1380 `[board-betty] TESTS: REVISE` — `docs/test-bible/core/agent.md` missing Decision A / truncated-success RESPONSE coverage.

### As-is

`docs/test-bible/core/agent.md` § AST-903 and `TestAst903CraftRubricMaxTokensFloor` / provider `TestAst903JsonMaxTokensHardFail` lock the 32000 floor and JSON `stop_reason==max_tokens` hard-fail. They do **not** cover AST-1380 Decision A (DeepSeek Big craft rubrics force `thinking=False`) or the provider-failure RESPONSE audit banner (`Provider failed …`) that prevents a truncated success-shaped envelope from looking like a finished hop (abrams-shaped path).

### To-be

Bible + component tests document and assert: (1) `craft_get_rubric` (and craft rubric UI keys) on DeepSeek with Big brain still floors `max_tokens` and passes `tier_meta.thinking is False` into `send_to_deepseek`; (2) when the provider returns `success=False` with a success-shaped raw JSON body, the stored RESPONSE `block_data` is prefixed with `Provider failed` (optionally `(failure_class)`) so operators/recovery cannot treat it as a completed craft payload.

### Repro

Fixture-shaped (no live LLM / no DB seed):

1. **Thinking-off:** Monkeypatch `get_active_llm_provider` → `"deepseek"`, `_resolve_task_prompts` → `_agent_rows(brain_setting="Big")`, stub `resolve_brain_setting_to_deepseek_tier_meta` to return Big meta with `thinking=True` / `reasoning_effort="max"` (as production Big does). Mock `send_to_deepseek` success with a full craft criteria envelope. Call `do_task("craft_get_rubric", …)`.
2. **Pre-fix vs post-fix (repro gate):** Against a tree **without** AST-1380’s `tier_meta = {**tier_meta, "thinking": False, …}` line, assert would see `send_to_deepseek` kwargs `tier_meta["thinking"] is True`. Against current product tip (AST-1380 landed), assert `tier_meta["thinking"] is False` and `reasoning_effort is None`, and `max_tokens == CRAFT_RUBRIC_MAX_TOKENS`.
3. **Failure banner:** Monkeypatch provider to return `success=False`, `failure_class="max_tokens"`, `error="Generation truncated (max_tokens) before complete JSON"`, `api_response` whose text is truncated abrams-shaped JSON still containing `"agent_performance":{"status":"success"}`. With `store_agent_data`/batch so RESPONSE is written, capture `save_agent_data` kwargs for `block_type=="RESPONSE"`: body must start with `Provider failed` (and include `max_tokens` when `failure_class` set) and must still contain the raw model snippet after `--- model response ---`.

### Root cause

Coverage gap only — product fix is on AST-1380. Board correctly flagged that AST-903’s existing suite does not lock Decision A or the failure-RESPONSE banner, so a future regression could re-enable thinking on craft Big hops or store bare success-shaped failure bodies without a bible/test tripwire.

### Proposed change

**No product code.** Lands **test-tree + bible only** (Betty / `astral-tests` → `merge-tests` onto this `sub/*`). Ada does not edit `tests/` or `docs/test-bible/**` on the epic worktree.

1. **Bible** — In `docs/test-bible/core/agent.md`, immediately after the existing **### AST-903 · AST-900 (UAT fix)** block, add **### AST-1380 / AST-1383 · AST-1379 (fix + gap)**:
   - One paragraph: Decision A forces DeepSeek `thinking=False` / `reasoning_effort=None` for `CRAFT_RUBRIC_UI_TASK_KEYS` in `do_task` while keeping the AST-903 `max_tokens` floor; provider-failure RESPONSE rows use `_provider_failure_audit_body` (`Provider failed …` / optional `(failure_class)` + `--- model response ---`).
   - Table rows pointing at the new test class(es) below.
   - Narrowed run command listing those node ids (plus keep AST-903 ids as regression neighbors if useful).

2. **Tests** — In `tests/component/core/test_agent.py`, add class **`TestAst1380CraftRubricThinkingOffAndFailureBanner`** (or `TestAst1383…` — prefer **1380** in the name since it locks the product behavior; bible cites AST-1383 as the gap that landed coverage):

   - **`test_craft_get_rubric_deepseek_big_forces_thinking_false`**
     - Provider deepseek; agent rows `brain_setting="Big"`.
     - Real or stubbed Big tier meta initially `thinking=True` (must exercise the override path — if stubbing `resolve_brain_setting_to_deepseek_tier_meta`, return thinking True so the assertion proves `do_task` cleared it).
     - Assert `send_to_deepseek` awaited with `tier_meta["thinking"] is False`, `tier_meta.get("reasoning_effort") in (None,)` / falsy, and `max_tokens == cfg.CRAFT_RUBRIC_MAX_TOKENS`.
     - Non-goal: do not assert Anthropic path thinking (N/A).

   - **`test_non_craft_deepseek_big_keeps_thinking`** (optional but preferred — blast control)
     - Same Big deepseek setup for a **non**-`CRAFT_RUBRIC_UI_TASK_KEYS` task that still runs on deepseek in this suite (pick an existing deepseek-covered task key already used in `test_agent.py`).
     - Assert thinking remains True when tier meta says so — Decision A must not blanket-disable Big thinking.

   - **`test_provider_failure_response_banner_prefixes_success_shaped_envelope`**
     - `do_task("craft_get_rubric", …)` with provider mock `success=False`, `failure_class="max_tokens"`, truncated raw body containing `agent_performance.status=success` mid-criteria cut (literal fixture string ending at `even though no title` without closing the content string is fine — banner path uses raw text, not parse).
     - Ensure agent_data store path runs (`batch_id` / `store_agent_data` fixtures as in neighboring store tests).
     - Assert saved RESPONSE `block_data` contains `Provider failed` and `max_tokens`, contains `--- model response ---`, and still embeds the success-status substring so the banner is visibly guarding the abrams-shaped blob.

3. **Publish** — Betty commits on `astral-tests`, `merge-tests(AST-1383)` onto `origin/sub/AST-1379/AST-1383-gap-craft-get-truncation-tests`. No `origin/dev` / `ftr` push from this gap alone.

⚠️ **Decision:** Gap ownership is **Betty test-tree** (bible + component tests). Product remains AST-1380 only — do not re-touch `src/core/agent.py` here unless a new product defect appears (then file a separate bug, do not expand this gap).

### Blast radius

- Extends `docs/test-bible/core/agent.md` and `tests/component/core/test_agent.py` only.
- Neighbor AST-903 tests must stay green (floor + provider hard-fail unchanged).
- Optional non-craft thinking-keep test protects other Big deepseek hops from accidental Decision A bleed.
- Does not change canon (Joan CANON: OK on AST-1380).

### What must still hold

- AST-903 floor + JSON `max_tokens` hard-fail tests and bible wording remain accurate.
- AST-1380 product behavior (thinking-off for craft rubrics; failure RESPONSE banner) is not weakened.
- No prompt/schema/`grade_*`/ArtifactEditor changes.
- Gap does not re-implement or amend AST-1380’s Decision A / banner code.

## Radia review-fix (AST-1383)

**Overall:** CLEAN. Gap bible + three Decision A / failure-banner tests lock AST-1380; [bug-repro] OK; no product delta.

