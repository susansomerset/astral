<!-- linear-archive: AST-650 archived 2026-06-23 -->

## Linear archive (AST-650)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-650/uat-craft-resume-base-generate-succeeds-but-does-not-persist-base  
**Status at archive:** Done  
**Project:** Astral Interface (inherited from AST-601)  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-601 — Rebuild 519 (git casualty)  
**Blocked by / blocks / related:** parent: AST-601

### Description

## What failed

After **AST-644** fix, **Generate** on candidate `karfo` for `craft_resume_base` completes without validation error (ledger batch `user-craft_resume_base-5bdeb39b-ecfb-4e76-b8d5-089cbde6c8e0`, 2026-06-14 23:04:51). UI may show success, but `candidate_data.artifacts` **is still absent** — no `base_resume` or `resume_structure` persisted. Reloading **Base Resume Content** shows empty tabs; DB row has only `profile` + `context`, no artifacts blob.

## Expected

Successful **Generate** on **Base Resume Content** persists `artifacts.resume_structure` and `artifacts.base_resume` (same as `parse_candidate_resume` after `split_craft_resume_base_payload`). Tabs show generated section content on reload without requiring a separate manual Save for the initial generate path.

## Repro

1. Admin → candidate **karfo** → **Base Resume Content**.
2. Click **Generate** (candidate in `LIVE_PROMPTS` / allowed generate state).
3. Wait for completion (no validation error).
4. Reload page or inspect candidate row — `candidate_data.artifacts.base_resume` still missing.

## Parent AC (quoted inline)

> Editor loads and saves `artifacts.base_resume` string content keyed by section ids; keys not in the candidate's structure are not shown and are not persisted (orphan keys dropped on save — self-heal, not hard error).

> **Base Resume Content** shows one tab per **enabled** section for the selected candidate, in defined order; tab labels come from that candidate's structure titles.

## Boundaries

* Does **not** change: AST-616 tab UI wiring, global `DATA_SHAPES`, or craft_resume_base prompt/schema.
* Fix: wire **Generate** POST persistence in `run_candidate_artifact_generation` (or equivalent) for `craft_resume_base` — reuse `split_craft_resume_base_payload` + `save_candidate` merge like `parse_candidate_resume`.
* May still return `parsed_response` to frontend for immediate display.

### Comments

#### betty — 2026-06-14T23:14:08.884Z
## QA test manifest (AST-650)

**Publish:** `origin/sub/AST-601/AST-650-craft-resume-base-generate-no-persist` @ `2b7f7e2f` (`merge-tests(AST-650): origin/tests 3ae3b720`)

**`docs/ASTRAL_TEST_BIBLE.md` shasum on publish ref:** `57d451eeaba1d7d79c0b44df6dc1aa683ac0391b748cd1e967260419bd644b52`

### 1. Revised this pass (product change broke harness)

1. **`test_returns_200_on_success`** — mock **`save_candidate`** (Generate success now persists for **`craft_resume_base`**)

### 2. New regression

2. **`test_persists_artifacts_on_craft_resume_base_success`** — UAT path: success → **`save_candidate`** with **`merge=True`**, **`artifacts.resume_structure`** + **`artifacts.base_resume`**
3. **`test_does_not_persist_artifacts_on_other_task_success`** — guard: **`bootstrap_candidate_context`** success does not artifact-save

### 3. Gaps

None — **§7.13zzv** narrowed run only (no UI).

### Narrowed run

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestRunCandidateArtifactGeneration
```

#### ada — 2026-06-14T23:12:04.932Z
Plan doc: [ast-650-uat-craft-resume-base-generate-succeeds-but-does-not-persist-base-resume.md](https://github.com/susansomerset/astral/blob/sub/AST-601/AST-650-craft-resume-base-generate-no-persist/docs/features/interface/ast-650-uat-craft-resume-base-generate-succeeds-but-does-not-persist-base-resume.md)

**Self-assessment**
- **Scope:** Single-Component — add split+save on `craft_resume_base` success in `run_candidate_artifact_generation` only.
- **Conf:** high — success path returns without save today; `parse_candidate_resume` is the working template; no UI/schema changes.
- **Risk:** Medium — Generate is the primary Base Resume Content path; must guard `task_key` and use `merge=True`.

**Summary:** Wire `split_craft_resume_base_payload` + `save_candidate` merge into UI Generate success path so reload shows persisted tabs.

---

# AST-650 — UAT: craft_resume_base Generate succeeds but does not persist base_resume

**Linear:** [AST-650 — UAT: craft_resume_base Generate succeeds but does not persist base_resume](https://linear.app/astralcareermatch/issue/AST-650/uat-craft-resume-base-generate-succeeds-but-does-not-persist-base-resume)  
**Parent:** [AST-601 — Rebuild 519 git casualty](https://linear.app/astralcareermatch/issue/AST-601/rebuild-519-git-casualty) (context only)  
**Publish ref:** `origin/sub/AST-601/AST-650-craft-resume-base-generate-no-persist` (origin only)

## Summary

After **AST-644**, UI **Generate** for `craft_resume_base` completes without validation error (ledger batch completes, HTTP 200), but **`candidate_data.artifacts` is never written** — no `base_resume` or `resume_structure`. Reloading **Base Resume Content** shows empty tabs.

Root cause: `run_candidate_artifact_generation` (POST **Generate** path from `api_candidate.py`) returns `parsed_response` to the frontend on success but **never** calls `split_craft_resume_base_payload` + `database.save_candidate`. That persistence exists only on `parse_candidate_resume` (CLI/script path). AST-517 deliberately deferred Generate POST persistence pending AST-519 UI; **Base Resume Content** (AST-616) now expects Generate to populate artifacts. This bug wires the same split+merge save into the UI Generate success path for `craft_resume_base` only, without changing prompt/schema or tab UI.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/candidate.py` | After successful `do_task` in `run_candidate_artifact_generation`, when `task_key == "craft_resume_base"`, persist `resume_structure` + `base_resume` via `split_craft_resume_base_payload` + `save_candidate(..., merge=True)` | core |
| `tests/component/core/test_candidate.py` | Regression: Generate success path calls `save_candidate` with artifacts (Betty manifest — engineer runs during test-child) | test |

**Verify only (no change expected):**

| File | Role |
|------|------|
| `src/ui/api/api_candidate.py` | Already routes `craft_resume_base` Generate to `run_candidate_artifact_generation` with `starting_resume_text` as `live_content` |
| `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx` | Tab UI — reload reads persisted artifacts via existing GET/structure flow (AST-616) |
| `parse_candidate_resume` | Keep existing persist block unchanged (same split+save semantics) |

**Out of scope:** AST-616 tab UI, global `DATA_SHAPES`, craft_resume_base prompt/schema, state transitions on Generate, other `craft_*` task keys.

---

## Stage 1: Persist artifacts on UI Generate success (`craft_resume_base`)

**Done when:** Successful **Generate** POST for `craft_resume_base` writes `candidate_data.artifacts.resume_structure` and `candidate_data.artifacts.base_resume` before returning HTTP 200; response body still includes `parsed_response`, `timesheet`, and `batch_id` unchanged.

1. In `src/core/candidate.py`, in `run_candidate_artifact_generation`, locate the success branch after ledger `COMPLETED` update (~lines 789–814), **before** the final `return ({ "success": True, ... }, 200)`.

2. Insert persistence block (only when `task_key == "craft_resume_base"`):

   ```python
   parsed_response = result.get("parsed_response")
   if task_key == "craft_resume_base" and parsed_response is not None:
       structure, content = split_craft_resume_base_payload(parsed_response)
       database.save_candidate(
           candidate_id,
           candidate_data={"artifacts": {"resume_structure": structure, "base_resume": content}},
           merge=True,
       )
   ```

   ⚠️ **Decision:** Mirror `parse_candidate_resume` (~lines 674–678) verbatim — same `split_craft_resume_base_payload` + merge save. Do **not** call `transition_candidate_state` here (Generate runs on `LIVE_PROMPTS` candidates; parse path only transitions `NEW` → `PROFILE_READY`).

3. Do **not** refactor `parse_candidate_resume` into a shared helper in this bug pass — inline only in `run_candidate_artifact_generation` to minimize blast radius.

4. Do **not** change failure paths, ledger bookkeeping, or return JSON shape on success.

5. `python3 -m py_compile src/core/candidate.py`

**Ritual:** `code(AST-650): persist craft_resume_base artifacts on UI Generate success`

---

## Stage 2: Regression tests (Betty manifest / test-child)

**Done when:** Component test proves `run_candidate_artifact_generation("…", "craft_resume_base", …)` on success invokes `database.save_candidate` with merged `artifacts.resume_structure` and `artifacts.base_resume`.

Betty adds to **Tests Ready** manifest. If omitted, engineer adds only:

1. In `tests/component/core/test_candidate.py`, inside `TestRunCandidateArtifactGeneration`, add **`test_persists_artifacts_on_craft_resume_base_success`**:
   - Monkeypatch `get_candidate`, `save_dispatch_ledger`, `update_dispatch_ledger`, `compute_batch_cost` as existing success test.
   - Capture `save_candidate` calls in a list.
   - Mock `asyncio.run` to return `{"success": True, "parsed_response": _craft_resume_base_payload(_three_section_structure(), {"experience": "Jobs"})}` (reuse helpers from `TestAst517ResumeStructure`).
   - Call `run_candidate_artifact_generation("karfo", "craft_resume_base", "resume text")`.
   - Assert status 200 and exactly one `save_candidate` with `candidate_data["artifacts"]["resume_structure"]` and `candidate_data["artifacts"]["base_resume"]["experience"] == "Jobs"`.
   - Assert `merge=True` on save kwargs.

2. Add **`test_does_not_persist_on_non_craft_resume_base_success`** (optional guard): same setup with `task_key="bootstrap_candidate_context"` — assert `save_candidate` not called for artifacts (only ledger paths if any).

3. Re-run `tests/component/core/test_candidate.py::TestRunCandidateArtifactGeneration`.

**Ritual:** `test(AST-650): UI Generate persists craft_resume_base artifacts`

---

## Execution contract reminders

- Response must still return `parsed_response` for immediate frontend display.
- `merge=True` must preserve other artifact keys (e.g. `profile`) — same as `parse_candidate_resume`.
- Do **not** edit `tests/` in **build-child** — Betty owns manifest.
- Blocking ambiguity → `🛑` comment on **AST-601** parent.

---

## Self-Assessment

**Scope:** `Single-Component` — One conditional block in `run_candidate_artifact_generation` in `candidate.py`; focused component tests only.

**Conf:** `high` — UAT repro matches code (`run_candidate_artifact_generation` success returns without save); `parse_candidate_resume` is the working reference implementation; no UI or schema changes.

**Risk:** `Medium` — Generate is Susan's primary Base Resume Content path; wrong task_key guard or missing `merge=True` could wipe artifacts or skip persist for other tasks.

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Reuses existing `split_craft_resume_base_payload` + save pattern from `parse_candidate_resume`; no new catalog logic |
| §2.1 config | No config changes |
| §2.4 batch | N/A — single-candidate UI generate |
| §2.6 state machine | Explicitly no new transitions on Generate |
| §3.3 imports | No new imports; functions already in `candidate.py` |
| §3.5 naming | No new public API |

No conflicts requiring `conf-!!-NONE`.

---

## Review

**Built:** `code(AST-650): persist craft_resume_base artifacts on UI Generate success`  
**Branch:** `origin/sub/AST-601/AST-650-craft-resume-base-generate-no-persist`  
**Commit:** `d4fa441e`
