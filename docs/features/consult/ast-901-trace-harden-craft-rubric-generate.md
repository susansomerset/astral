# Trace and harden craft rubric generate delivery

**Parent:** [AST-900 — craft get rubric did not populate the rubric content for candidate](https://linear.app/astralcareermatch/issue/AST-900/craft-get-rubric-did-not-populate-the-rubric-content-for-candidate)

**Publish ref:** `origin/sub/AST-900/AST-901-trace-harden-craft-rubric-generate`

**Summary:** The `karfo` `craft_get_rubric` run completed on the backend (ledger `COMPLETED`, full criteria payload in `agent_data`) but the candidate never received the result in the Artifacts UI. This ticket traces that delivery gap on the **backend generate path** and hardens it so a successful `craft_*_rubric` run leaves a durable, recoverable record and AST-538 debug trace — without changing prompts, rubric semantics, auto-Save behavior, or dispatcher consult batches. **Artifact editor UX** (review banner, page-return polling) is **AST-902**.

---

## Root cause analysis (`karfo`, 2026-07-16)

End-to-end path for UI rubric Generate:

1. `ArtifactEditor.doGenerate` → `POST /api/candidates/{id}/generate/{task_key}` (`api_candidate.generate_artifact`).
2. `run_candidate_artifact_generation` creates ledger `user-{task_key}` + `batch_id`, sets `log_batch_id`, calls `do_task`.
3. `do_task` runs LLM (~178.5s for `karfo`), stores `agent_data` RESPONSE block (JSON `{criteria: [...]}`), returns `parsed_response`.
4. `run_candidate_artifact_generation` marks ledger `COMPLETED`, returns HTTP 200 `{success, parsed_response, batch_id}`.
5. **Only** `craft_resume_base` auto-persists to `candidate_data.artifacts`; all `craft_*_rubric` tasks rely on the browser receiving `parsed_response` and the user clicking **Save** (review-then-Save — correct by design).

**Where the payload was lost**

| Layer | Observation |
|-------|-------------|
| LLM / `do_task` | Succeeded; criteria payload present in logs. |
| Ledger | `COMPLETED` for `user-craft_get_rubric-364310ef-…`. |
| `agent_data` | RESPONSE block stored under `batch_id` (durable). |
| `candidate.agent_responses` | **Not written** — `craft_*_rubric` tasks have `entity_type: None` in `TASK_CONFIG`, so `append_agent_response` is skipped. |
| `candidate_data.artifacts.get_rubric` | **Not written** on generate (by design — user must Save). |
| HTTP delivery | **Only synchronous path** to the browser. No server-side pending stash. |
| Recovery API | **None** for candidate auth — admin can query ledger/`agent_data`; Artifacts UI cannot. |

**Conclusion:** Backend generation succeeded and is reconstructable from `batch_id`, but the product had **no durable user-facing delivery record** when the HTTP response never reached the browser (long wait, tab close, navigate away, or connection drop at end of a multi-minute request). The defect is **delivery hardening**, not bad criteria or failed LLM.

**Out of scope for this ticket:** Frontend handling of missed responses and page-return recovery → **AST-902**.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/candidate.py` | Pending stash, recovery helper, empty-criteria guard, AST-538 debug on generate | core |
| `src/ui/api/api_candidate.py` | `GET …/generate/<task_key>/pending` recovery endpoint; clear pending on artifact Save | ui |
| `src/utils/config.py` | `CRAFT_RUBRIC_UI_TASK_KEYS` frozenset (derived from existing `CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY`) | utils |

**Not in scope:** `ArtifactEditor.tsx`, rubric prompts/schema, `dispatcher.py` consult paths, `craft_resume_base` auto-save path.

---

## Stage 1: Config helper for craft rubric UI tasks

**Done when:** `CRAFT_RUBRIC_UI_TASK_KEYS` is importable from `config.py` and matches the six `craft_*_rubric` keys already in `CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY`.

1. In `src/utils/config.py`, immediately after `CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY`, add:
   ```python
   CRAFT_RUBRIC_UI_TASK_KEYS: frozenset[str] = frozenset(CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY.keys())
   ```
2. No other config changes.

⚠️ **Decision:** Reuse the existing artifact-key map keys as the authoritative craft-rubric UI task set — avoids a second list that could drift.

---

## Stage 2: Pending-generation stash and empty-criteria guard

**Done when:** A successful `craft_*_rubric` generate writes `candidate_data.pending_craft_generations[task_key]` before returning HTTP 200; an empty `criteria` array fails the run (ledger `FAILED`, HTTP 500).

1. In `src/core/candidate.py`, add module-level constant:
   ```python
   _PENDING_CRAFT_GENERATIONS_KEY = "pending_craft_generations"
   ```
2. Add helper `_ledger_task_key_for_ui_generate(task_key: str) -> str` returning `f"user-{task_key}"` (same prefix already used in `run_candidate_artifact_generation`).
3. Add helper `_is_craft_rubric_ui_task(task_key: str) -> bool` — `return task_key in CRAFT_RUBRIC_UI_TASK_KEYS` (import from config).
4. Add `_stash_pending_craft_generation(candidate_id, task_key, batch_id, parsed_response)`:
   - Read candidate; merge into `candidate_data[_PENDING_CRAFT_GENERATIONS_KEY][task_key]` a dict:
     `{"batch_id": batch_id, "completed_at": <UTC str>, "parsed_response": parsed_response}`.
   - Call `database.save_candidate(candidate_id, candidate_data={_PENDING_CRAFT_GENERATIONS_KEY: {...}}, merge=True)` — merge only the pending dict for this `task_key` (read-modify-write the nested dict in Python before save).
5. Add `_clear_pending_craft_generation(candidate_id, task_key)` — remove `task_key` from nested dict; delete top-level key if empty.
6. Add `_craft_rubric_criteria_count(parsed_response) -> int` — if `parsed_response` is dict, `len(parsed_response.get("criteria") or [])`; else `0`.
7. In `run_candidate_artifact_generation`, **after** `result.get("success")` is confirmed and **before** ledger `COMPLETED` update:
   - If `_is_craft_rubric_ui_task(task_key)`:
     - `count = _craft_rubric_criteria_count(parsed_response)`
     - If `count == 0`: update ledger to `FAILED` (same pattern as existing failure branch), log error `"craft rubric generate returned empty criteria"`, return HTTP 500 `{"success": False, "error": "Generation returned no criteria", "batch_id": …}`.
     - Else: call `_stash_pending_craft_generation(...)`.
8. Leave `craft_resume_base` branch unchanged (lines 913–919).

⚠️ **Decision:** Stash lives in `candidate_data.pending_craft_generations`, not in `artifacts` — satisfies “no auto-Save overwriting artifact” while giving AST-902 a server-side source for page-return recovery.

---

## Stage 3: Recovery from pending stash or ledger fallback

**Done when:** `get_pending_craft_generation(candidate_id, task_key)` returns the same `parsed_response` shape as a successful POST generate, using stash first then ledger+`agent_data` fallback.

1. In `src/core/candidate.py`, add `get_pending_craft_generation(candidate_id: str, task_key: str) -> Tuple[Dict[str, Any], int]`:
   - If not `_is_craft_rubric_ui_task(task_key)`: return `({"error": "Not a craft rubric task"}, 400)`.
   - Load candidate; if missing → 404.
   - **Primary:** read `candidate_data.pending_craft_generations[task_key]`; if present and `parsed_response` has `criteria` with `len > 0`, return 200:
     `{"success": True, "parsed_response": …, "batch_id": …, "recovered": True, "source": "pending_stash"}`.
   - **Fallback:** call `list_dispatch_ledger(task_key=_ledger_task_key_for_ui_generate(task_key), candidate_id=candidate_id, status="COMPLETED")` from `src.core.dispatcher` (core wrapper — do not import `database` from api).
   - Take first row (newest `started_at`); `batch_id = row["batch_id"]`.
   - Import `get_entity_response` from `src.core.agent`; `row = get_entity_response(batch_id, candidate_id)`.
   - Parse `row["block_data"]` as JSON; expect dict with `criteria` list.
   - If parse fails or `criteria` empty → return `({"error": "No recoverable generation"}, 404)`.
   - Return 200 with `source: "ledger_agent_data"` and same body shape as primary.
2. Export the function for API use.

⚠️ **Decision:** Fallback uses existing `dispatch_ledger` + `agent_data` so `karfo`-style runs are recoverable even before stash existed (historical rows).

---

## Stage 4: Recovery API endpoint and pending clear on Save

**Done when:** Authenticated candidate API exposes recovery; saving the matching artifact clears the pending stash.

1. In `src/ui/api/api_candidate.py`, import `get_pending_craft_generation`, `_clear_pending_craft_generation`, `CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY` from core/config.
2. Add route:
   ```python
   @candidate_bp.route("/<candidate_id>/generate/<task_key>/pending", methods=["GET"])
   @require_auth
   def get_pending_artifact_generation(candidate_id, task_key):
   ```
   - Call `get_pending_craft_generation(candidate_id, task_key)`; `return jsonify(body), status`.
3. In `update_candidate_data`, after `normalize_rubric_artifacts_on_save(arts)` and before `save_candidate_data`:
   - For each `(craft_task_key, artifact_key)` in `CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY.items()`:
     - If `artifact_key in arts`: call `_clear_pending_craft_generation(candidate_id, craft_task_key)`.
4. Do **not** add frontend calls — AST-902 consumes this endpoint.

---

## Stage 5: AST-538 debug trace on generate path

**Done when:** With `debug=True`, `run_candidate_artifact_generation` emits per-run index header + truncated criteria detail for craft rubric tasks; production INFO logs criteria count + batch_id on success.

1. In `src/core/candidate.py`, import `get_logger` and use `get_logger(__name__, debug_flag=debug)` inside `run_candidate_artifact_generation` when `debug` is True (or call `logger.set_debug_flag(debug)` at function entry).
2. For `_is_craft_rubric_ui_task(task_key)` on **success** (criteria count > 0):
   - When `debug=True`: `debug_index(func="run_candidate_artifact_generation", index=1, total=1, identifier=task_key, outcome=f"criteria_count={count}")`; `debug_detail_block` with `truncate_debug_content(json.dumps(parsed_response))`.
   - Always (debug or not): existing `UI generate completed` log line — extend with `criteria_count=%s` in the same log call (no full payload in INFO).
3. On **empty criteria** failure: when `debug=True`, `debug_index` outcome `"empty criteria"`.
4. Do not add `[DEBUG] logger.info` strings (AST-538 anti-pattern).

---

## Stage 6: Root-cause documentation on Linear

**Done when:** This ticket has a Linear comment summarizing the `karfo` trace conclusion (table above) and pointing to this plan — for Susan/Chuckles; no code in this stage.

1. Post comment on **AST-901** (not parent) with: one-paragraph root cause, link to plan blob on publish ref, note that AST-902 wires UI recovery to `GET …/pending`.

---

## Execution contract (for build-child)

- Execute stages in order; one commit per stage on epic worktree; publish each to `origin/sub/AST-900/AST-901-trace-harden-craft-rubric-generate`.
- Do **not** modify `ArtifactEditor.tsx`, `TASK_CONFIG` prompts/schemas, or dispatcher consult paths.
- Do **not** auto-write `artifacts.{artifact_key}` on generate — only `pending_craft_generations` stash.
- If `list_dispatch_ledger` or `get_entity_response` signatures differ from plan assumptions — stop and comment on parent AST-900.

---

## Self-Assessment

**Scope:** `Single-Component` — `candidate.py` generate/recovery logic plus one new API route and a small config frozenset; no UI or dispatcher changes.

**Conf:** `Medium` — root cause is clear from `karfo` evidence; pending stash + ledger fallback follow existing batch/ledger patterns, but recovery is new surface area for the candidate API.

**Risk:** `Medium` — touches the hot path for all six `craft_*_rubric` generates; empty-criteria guard could surface latent model failures as 500s (intended); must not regress `craft_resume_base`.

---

## Rules review (ASTRAL_CODE_RULES)

| Rule | Compliance |
|------|------------|
| §1.3 DRY | Reuses `CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY`, `list_dispatch_ledger`, `get_entity_response`, existing ledger prefix. |
| §2.1 config | New frozenset derived from existing map; no magic task-key lists elsewhere. |
| §2.4 batch | Same `user-{task_key}-{uuid}` batch_id; no new claim pattern. |
| §2.6 state machine | No candidate state transitions added. |
| §3.3 imports | API → core → data; core imports dispatcher + agent, not UI. |
| §3.5 naming | `pending_craft_generations`, `get_pending_craft_generation` match existing snake_case. |
| §1.5.1 debug | AST-538 helpers only when `debug=True`; truncated payloads. |

No conflicts requiring escalation.

---

## Build

- **Publish tip:** `origin/sub/AST-900/AST-901-trace-harden-craft-rubric-generate` @ `f8b9fe2eb7ab8370639a18e49580a96b4de4f841`
- Stage 1: `8b2d64c` — `CRAFT_RUBRIC_UI_TASK_KEYS` frozenset
- Stage 2: `ed23088` — pending stash + empty-criteria guard
- Stage 3: `b561ce6` — `get_pending_craft_generation` (stash / ledger fallback)
- Stage 4: `5b97833` — `GET …/generate/<task_key>/pending` + clear on Save
- Stage 5: `172ce98` — AST-538 debug on generate path
- Stage 6: root-cause Linear comment (plan-child / plan comment — no code)

## Review

**Radia** · `origin/dev`…`origin/sub/AST-900/AST-901-trace-harden-craft-rubric-generate` @ `f8be916` · product through Stage 5 + Betty tests

### What's solid

- **Plan fidelity:** Stages 1–5 match the plan: `CRAFT_RUBRIC_UI_TASK_KEYS`, pending stash + empty-criteria → ledger `FAILED` / HTTP 500, `get_pending_craft_generation` (stash then ledger+`agent_data`), `GET …/pending`, clear pending on matching artifact Save, AST-538 `debug_index` / `debug_detail_block` gated on `debug=True`. No `ArtifactEditor` / prompt / dispatcher consult scope creep (AST-902 boundary held).
- **§2.1:** UI task set derived from `CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY` — no second magic list.
- **§3.3:** API → core helpers; recovery uses `list_dispatch_ledger` + `get_entity_response` (not data from API). Ledger fallback orders `started_at DESC` (newest first) as assumed.
- **§1.5.1:** Success path emits Style D index + truncated criteria via `debug_detail_block`; empty-criteria path indexes `empty criteria`; INFO adds `criteria_count` without payload dump. No `[DEBUG]` info spam.
- **Self-Assessment:** Diff footprint matches **Single-Component** / Medium risk (hot path for six craft rubrics; `craft_resume_base` untouched).

### Issues

**fix-now:** Nested import without B1 comment — `get_pending_craft_generation` does `from src.core.dispatcher import list_dispatch_ledger` at function scope (`src/core/candidate.py` ~886). `dispatcher` does not import `candidate`, so this is not a documented cycle break. Per §1.2 / review-child §5a B1: move the import to module top, or keep it lazy with a one-line comment stating why.

**fix-now:** Silent stash skip — `_stash_pending_craft_generation` returns with no log when `get_candidate` is None (`src/core/candidate.py` ~72–74). On a multi-minute generate that is the race this ticket hardens against; success would still return HTTP 200 / ledger `COMPLETED` with no `pending_craft_generations` row and no operator signal (D2). Log at least `logger.error` (and prefer failing the craft-rubric success path if stash cannot be written).

### Recommended actions

| Action | Owner | Notes |
|--------|-------|-------|
| Module-top (or commented) `list_dispatch_ledger` import | Ada | §1.2 B1 |
| Log / fail when pending stash cannot write | Ada | D2 — delivery hardening must not go dark |
| resolve-child after fixes | Ada | Leave assignee Ada |

## Resolution

**2026-07-16** — Radia fix-now addressed (`resolve(AST-901)`).

| Finding | Change |
|---------|--------|
| Nested `list_dispatch_ledger` import | Moved to module top in `src/core/candidate.py` (no cycle; dispatcher does not import candidate). |
| Silent stash skip | `_stash_pending_craft_generation` returns `bool`; logs `logger.error` when candidate missing or save fails; craft-rubric success path returns HTTP 500 + ledger `FAILED` if stash cannot write (no COMPLETED without recovery record). |

No test-tree changes. Re-ran Betty AST-901 manifest after product fix.
