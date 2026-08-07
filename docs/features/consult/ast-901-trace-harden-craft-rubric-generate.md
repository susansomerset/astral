<!-- linear-archive: AST-901 archived 2026-08-02 -->

## Linear archive (AST-901)

**Archived:** 2026-08-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-901/trace-and-harden-craft-rubric-generate-delivery-craft-get-rubric-did  
**Status at archive:** Archive  
**Project:** Astral Consult  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-900 — craft get rubric did not populate the rubric content for candidate  
**Blocked by / blocks / related:** parent: AST-900; blocks: AST-902

### Description

## What this implements

Trace the `karfo` `craft_get_rubric` run end to end and document where the successful criteria payload was lost. Harden the candidate UI generate path so a successful backend COMPLETED cannot leave the user with nothing and no error — including long-running generations. When the browser never receives the result, the completed generation must be recoverable. Backend debug on the generate path must show what was produced and what was recorded when debug is on (AST-538 contract).

## Acceptance criteria

* The root cause of the `karfo` drop is documented on this ticket or a child ticket.
* A generation that completes on the backend can no longer vanish without a user-visible trace: the editor shows the result or an error, or the completed result is recoverable when the user returns to the page.
* Base resume generation still parses and saves as before.

## Boundaries

* Does not change rubric prompts, response schema, criteria content, or grading semantics.
* Does not auto-Save overwriting the candidate artifact without user confirmation after Generate.
* Does not change dispatcher batch consult paths (`grade_get` and siblings).
* Artifact editor UX for review-after-Generate and page-return recovery is the sibling Katherine ticket.

## Notes for planning

* Generate entry: candidate UI generate → `run_candidate_artifact_generation` → `do_task` for `craft_*_rubric`.
* Ledger already closed COMPLETED for `karfo` with a full criteria payload — start from that trail.
* Keep review-then-Save: Generate must not silently overwrite stored candidate artifacts.
* Fix must apply to every craft rubric generate path, not get-only.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at dispatch-parent.

### Comments

#### chuckles — 2026-07-16T21:37:19.532Z
[merge-child] blocked: missing plan(AST-901): on origin/sub/AST-900/AST-901-trace-harden-craft-rubric-generate

Plan was published as `docs(AST-901): plan — …` instead of `plan(AST-901): …`. @Ada Lovelace — republish with a `plan(AST-901):` commit in the canonical sub log (empty commit OK if the plan blob already exists), then Chuckles will re-run merge-child.

— Chuckles

#### chuckles — 2026-07-16T21:36:35.170Z
[merge-child] blocked: missing plan(AST-901): on origin/sub/AST-900/AST-901-trace-harden-craft-rubric-generate

Plan was published as `docs(AST-901): plan — …` instead of `plan(AST-901): …`. @Ada Lovelace — republish with a `plan(AST-901):` commit in the canonical sub log (empty commit OK if the plan blob already exists), then Chuckles will re-run merge-child.

— Chuckles

#### radia — 2026-07-16T21:33:42.949Z
### Radia review — findings

Diff: `origin/dev`…`origin/sub/AST-900/AST-901-trace-harden-craft-rubric-generate` @ `2dec798` (product tip was `f8be916` + this doc commit).

Plan doc: https://github.com/susansomerset/astral/blob/2dec798dd2197d1d34605a2da8e2ec2e5de4918f/docs/features/consult/ast-901-trace-harden-craft-rubric-generate.md

**fix-now:** Nested import without B1 comment — `get_pending_craft_generation` does `from src.core.dispatcher import list_dispatch_ledger` at function scope (`src/core/candidate.py` ~886). `dispatcher` does not import `candidate`, so this is not a documented cycle break. Per §1.2 / B1: move to module top, or keep lazy with a one-line why-comment.

**fix-now:** Silent stash skip — `_stash_pending_craft_generation` returns with no log when `get_candidate` is None (`src/core/candidate.py` ~72–74). On a multi-minute generate that is the race this ticket hardens against; success can still return HTTP 200 / ledger `COMPLETED` with no pending stash and no operator signal (D2). Log at least `logger.error` (prefer failing the craft-rubric success path if stash cannot be written).

**Solid:** Stages 1–5 plan fidelity; `CRAFT_RUBRIC_UI_TASK_KEYS` from existing map; API→core only; AST-538 debug gated + truncated via `debug_detail_block`; AST-902 / `craft_resume_base` boundaries held.

#### betty — 2026-07-16T21:29:30.835Z
## QA test manifest — AST-901

**Publish:** `origin/sub/AST-900/AST-901-trace-harden-craft-rubric-generate` @ `f8be916` (`merge-tests(AST-901): origin/tests 75474cf9424f15024758ce0dc78a177bc1d53966`)

### Manifest (run all)

1. `tests/component/core/test_candidate.py::TestAst901CraftRubricGenerateDelivery` — stash on craft rubric success (not artifact); empty criteria → 500 + ledger FAILED; recover from pending stash; ledger+`agent_data` fallback; reject non-rubric / missing candidate; clear pending RMW
2. `tests/component/core/test_candidate.py::TestRunCandidateArtifactGeneration` — existing; `craft_resume_base` auto-persist unchanged
3. `tests/component/ui/api/test_api_candidate.py::TestAst901PendingCraftGenerationApi` — `GET …/generate/<task_key>/pending`; PUT matching rubric artifact clears pending
4. `tests/component/utils/test_config.py::TestAst901CraftRubricUiTaskKeys` — `CRAFT_RUBRIC_UI_TASK_KEYS` == map keys (6), excludes `craft_resume_base`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst901CraftRubricGenerateDelivery \
  tests/component/core/test_candidate.py::TestRunCandidateArtifactGeneration \
  tests/component/ui/api/test_api_candidate.py::TestAst901PendingCraftGenerationApi \
  tests/component/utils/test_config.py::TestAst901CraftRubricUiTaskKeys
```

### Existing coverage (bible-backed, no rewrite)

- `TestRunCandidateArtifactGeneration` — resume-base persist / non-rubric no-artifact path still valid
- No obsolete tests found for this diff (craft rubric generate previously had no stash/recovery surface)

### Bible shasums on publish ref

- `docs/test-bible/core/candidate.md` `b13c9ee0af7f7dfa4fa296850f25d855dfa6c4da`
- `docs/test-bible/ui/api/api_candidate.md` `9c9efae379ccf0609dafc432be7acacf4176fbd8`

— Betty

#### chuckles — 2026-07-16T21:22:22.656Z
## validate-plan — APPROVED

**Verdict:** APPROVED → Plan Approved (assignee Ada)

### Findings
None blocking.

**Definition fidelity:** Matches AST-900 scope (delivery hardening vs UX recovery split). Boundaries respected (no prompt/schema/consult batch changes; review-then-Save kept).

**Layers / config:** Files-changed stay in allowed layers. Craft rubric task set derived from existing `CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY` (DRY). Pending stash outside `artifacts` is correct.

**Acceptable notes for build:** Prefer public core helpers over importing `_clear_*` into `api_candidate`; watch `candidate`↔`dispatcher` import direction when wiring ledger fallback.

— Chuckles

#### ada — 2026-07-16T21:19:19.059Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-900/AST-901-trace-harden-craft-rubric-generate/docs/features/consult/ast-901-trace-harden-craft-rubric-generate.md @ `0083732`

**Root cause (`karfo`):** Backend path succeeded end-to-end — ledger `COMPLETED`, full criteria in `agent_data` RESPONSE — but delivery was synchronous-only. `craft_*_rubric` tasks do not write `candidate.agent_responses` (`entity_type: None`) and do not auto-save artifacts (review-then-Save). When the browser missed the HTTP response after a ~3-minute wait, there was no candidate-facing recovery path. AST-901 adds `pending_craft_generations` stash, empty-criteria guard, `GET …/pending` recovery API, and AST-538 debug on the generate path. UI page-return wiring → AST-902.

**Scope:** `Single-Component` — `candidate.py` generate/recovery + one API route + config frozenset; no UI or dispatcher changes.

**Conf:** `Medium` — root cause is clear from ledger/logs; pending stash + ledger fallback are new but follow existing batch patterns.

**Risk:** `Medium` — all six `craft_*_rubric` generates touch the success path; empty-criteria guard may surface latent model failures as 500s (intended).

---

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
