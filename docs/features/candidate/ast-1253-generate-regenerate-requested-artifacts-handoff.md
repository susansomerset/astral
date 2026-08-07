# Generate/Regenerate REQUESTED_ARTIFACTS handoff

**Linear:** [AST-1253](https://linear.app/astralcareermatch/issue/AST-1253/generateregenerate-requested-artifacts-handoff-candidate-artifacts-now)  
**Parent:** [AST-1243](https://linear.app/astralcareermatch/issue/AST-1243/candidate-artifacts-now-daisy-chain) — Candidate Artifacts now daisy chain  
**Publish ref:** `sub/AST-1243/AST-1253-generate-regenerate-handoff`

Empty-state **Generate** and **Regenerate** on craft-chain Artifacts pages stop calling per-artifact UI `do_task` and instead hand the candidate to `REQUESTED_ARTIFACTS` so AST-1252’s dispatch chain builds the whole rubric set. **Regenerate** alone shows a full-reset warning that names Job Description, Get, Do, Like, and the other live `run_next` hops; default control is **No**. Does **not** own dispatch/persist internals (AST-1252). Does **not** change `craft_resume_base` ad-hoc generate.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Expand `REQUESTED_ARTIFACTS.prior_states` for regenerate re-entry; expand `artifact_generate_states`; add unordered hop display-name map; expose regenerate warning hop labels via state UI manifest (order from live walk helper, not a config sequence list) | utils |
| `src/core/candidate.py` | Add `start_requested_artifacts(candidate_id)`; helpers to walk live craft chain + detect chain UI task keys; reject chain keys in `run_candidate_artifact_generation` | core |
| `src/ui/api/api_candidate.py` | `POST /<id>/generate_artifacts` → core start; keep `/generate/<task_key>` for non-chain (e.g. `craft_resume_base`) only | ui |
| `src/ui/frontend/src/components/ArtifactEditor.tsx` | Chain pages: Generate/Regenerate → handoff API; Regenerate Yes/No modal (default No); retire per-page ad-hoc generate for chain `taskKey`s | ui |
| `src/ui/frontend/src/pages/ArtifactsCompanySearchTerms.tsx` | Same handoff + Regenerate warning (search terms is a live chain hop) | ui |
| `src/ui/frontend/src/contexts/StateUiContext.tsx` | Type manifest fields for chain regenerate hop labels (if added) | ui |

**Out of this ticket’s file list (do not touch):** AST-1252 dispatch/persist/retire wrappers; `craft_resume_base` / Base Resume Content generate path; job `BUILD_ARTIFACTS`; hop-order / sequencing lists in `config.py`; Cancel-build for in-progress `REQUESTED_ARTIFACTS`; `tests/` / bible (Betty).

## Stage 1: Config + core handoff (mirror job `start_artifact_build`)

**Done when:** From a candidate in `RESUME_READY`, `ARTIFACTS_READY`, or `ACTIVE_SEARCH`, `start_requested_artifacts(id)` transitions to `REQUESTED_ARTIFACTS` and returns that state string; illegal priors raise `ValueError`; `REQUESTED_ARTIFACTS.prior_states` includes the regenerate re-entry states listed below; `python3 -m py_compile` succeeds on touched modules; no craft-hop sequencing list/frozenset is added to `config.py`.

1. In `src/utils/config.py`, expand `CANDIDATE_STATES["REQUESTED_ARTIFACTS"]["prior_states"]` to also include: `ARTIFACTS_READY`, `ARTIFACTS_READY_STALE`, `ACTIVE_SEARCH`, `PAUSE_SEARCH` (keep existing `RESUME_READY`, `RESUME_READY_STALE`, `REQUESTED_ARTIFACTS_RETRY`). Do **not** add `REQUESTED_ARTIFACTS_ERROR` (AST-970 ERROR exits stay closed).

⚠️ **Decision:** Parent Original brief requires Regenerate from “whatever state” the operator was on when Generate was available; today’s graph only allowed first entry from resume-ready. Re-entry edges reuse existing vocabulary (no new states) so AC3/AC4 work after ARTIFACTS_READY / ACTIVE_SEARCH without reopening AST-871.

2. In `build_state_ui_manifest()` (same file), set `artifact_generate_states` to:
   `["RESUME_READY", "RESUME_READY_STALE", "ARTIFACTS_READY", "ARTIFACTS_READY_STALE", "ACTIVE_SEARCH", "PAUSE_SEARCH"]`
   with the existing `assert all(s in CANDIDATE_STATES …)`. Do **not** include `REQUESTED_ARTIFACTS` / `*_RETRY` / `*_ERROR` (Generate hidden while the chain is claimed).

3. Add an **unordered** display map (dict, not a sequence list) near the craft rubric maps, e.g. `CRAFT_ARTIFACTS_CHAIN_HOP_LABELS: Dict[str, str]` covering every task_key that can appear on the live chain from `CANDIDATE_STAGE_DISPATCH["requested_artifacts"]["task_key"]`, including at least:
   - `craft_get_rubric` → `"Get"`
   - `craft_do_rubric` → `"Do"`
   - `craft_like_rubric` → `"Like"`
   - `craft_jobdesc_rubric` → `"Job Description"`
   - `craft_evaluate_meteorite_rubric` → `"Meteorite"`
   - `craft_joblist_rubric` → `"Job List"`
   - `craft_prefilter_rubric` → `"Company Watch"`
   - `craft_company_search_terms` → `"Company Search Terms"`
   Missing map entries fall back to the raw `task_key` string when building warning copy (do not invent a second ordered hop list).

4. In `src/core/candidate.py`, add `start_requested_artifacts(candidate_id: str) -> str` modeled on `tracker.start_artifact_build`:
   - Load candidate; 404-style `ValueError` if missing.
   - Target = `CANDIDATE_STAGE_DISPATCH["requested_artifacts"]["trigger_state"]` (`REQUESTED_ARTIFACTS`).
   - Call `transition_candidate_state(candidate_id, target)` (enforces priors).
   - Return `target`. Do **not** clear artifacts here — AST-1252 hop persist overwrites from head on retry/regenerate.

5. In `src/core/candidate.py`, add helpers (names may vary; keep public-then-helpers):
   - `_walk_requested_artifacts_chain_task_keys() -> list[str]`: start at stage `task_key`, follow `_current_agent_task_run_next` until empty; raise/stop on cycle the same way AST-1252 worker does.
   - `is_requested_artifacts_chain_ui_task(task_key: str) -> bool`: membership in that live walk (not a config frozenset of hops).
   - `requested_artifacts_chain_hop_labels() -> list[str]`: walk order × `CRAFT_ARTIFACTS_CHAIN_HOP_LABELS` (for warning + optional manifest).

6. In `run_candidate_artifact_generation`, if `is_requested_artifacts_chain_ui_task(task_key)`: return `({"success": False, "error": "… use generate_artifacts / REQUESTED_ARTIFACTS …"}, 409)` **before** opening a ledger / calling `do_task`. Leave `craft_resume_base` and any non-chain keys on the existing suppress_run_next path.

## Stage 2: API route

**Done when:** `POST /api/candidates/<id>/generate_artifacts` returns `{"ok": true, "state": "REQUESTED_ARTIFACTS"}` on success, 404 when missing, 409 when `ValueError` from illegal transition; `POST …/generate/craft_get_rubric` returns 409 with the Stage 1 retire message; `POST …/generate/craft_resume_base` still reaches `run_candidate_artifact_generation`.

1. In `src/ui/api/api_candidate.py`, add route `POST /<candidate_id>/generate_artifacts` (`@require_auth`), parallel to `api_jobs.generate_artifacts`:
   - `get_candidate` → 404 if missing.
   - `try: state = start_requested_artifacts(candidate_id)` except `ValueError` → 409 `{"error": str(exc)}`.
   - Return `jsonify({"ok": True, "state": state})`.
2. Keep `POST /<candidate_id>/generate/<task_key>` wired to `run_candidate_artifact_generation` (Stage 1 gate rejects chain keys).

## Stage 3: Frontend Generate / Regenerate handoff

**Done when:** On a chain Artifacts page (`ArtifactEditor` with a chain `taskKey`, or Company Search Terms), empty-state **Generate** calls `POST /api/candidates/<id>/generate_artifacts` with **no** scary modal; when any chain artifact already has content, the button reads **Regenerate**, opens a modal that lists Job Description, Get, Do, Like, and the other live hop labels, with **No** as the default/cancel control and **Yes** confirming; **Yes** calls the same POST; **No**/overlay dismiss does nothing; after success, candidate list refreshes so `state` is `REQUESTED_ARTIFACTS` and Generate is hidden for in-progress states; Base Resume Content still uses per-artifact `/generate/craft_resume_base`.

1. If Stage 1 exposes hop labels on the state UI manifest (`candidate.artifacts_chain_hop_labels: string[]`), extend `StateUiContext` types and prefer that list for warning copy. Otherwise call a tiny helper that formats labels from a prop/constant filled once from the manifest load — **do not** hardcode hop order in the React tree beyond reading the manifest array.

2. In `ArtifactEditor.tsx` (candidate mode only, not `jobPersistence`):
   - Detect chain handoff when `is_requested_artifacts_chain_ui_task` equivalent is true for `taskKey` — implement as: `taskKey !== "craft_resume_base"` **and** `taskKey` is not a job-only path; concrete rule: treat as chain when `taskKey` is in the set of keys returned via manifest (`candidate.artifacts_chain_task_keys`) **or**, if only labels are exposed, when `taskKey` starts with `craft_` and is not `craft_resume_base`. Prefer an explicit manifest `artifacts_chain_task_keys` list produced by the Stage 1 walk (order from `run_next`, membership authority live — still not a config sequencing frozenset).
   - On load of `/api/candidates/<id>`, compute `hasChainData`: any artifact key for a chain hop has non-empty content (rubric list with any criterion content, or non-empty search-terms / fixed fields). Use that — not only the current page tabs — to choose Generate vs Regenerate label and whether to show the warning.
   - Replace `doGenerate` for chain keys with `doRequestArtifacts`: `POST /api/candidates/${selectedId}/generate_artifacts`; on success toast a short “Artifacts build requested — watch Execution History” (or equivalent), `refresh()` from `useCandidate()`, clear confirm state; on 409/error show toast with server `error`.
   - Empty Generate: call `doRequestArtifacts` immediately (no modal).
   - Regenerate: open confirm modal. Copy must state that **all** chain rubrics will be reset / rebuilt, explicitly naming **Job Description, Get, Do, Like**, and the remaining labels from the live list. Buttons: **No** (cancel — `dep-btn cancel`, `autoFocus`) and **Yes** (danger/`#ff6b6b`). Default is No (autofocus + dismiss on overlay = No).
   - Remove the old per-artifact “replace current content / Save or Cancel” regenerate copy for chain keys. Keep Cancel/Save review chrome only for non-chain / job persistence paths that still use ad-hoc generate.
   - Do **not** call `/generate/${taskKey}` for chain keys anymore.

3. In `ArtifactsCompanySearchTerms.tsx`, apply the same handoff + Regenerate warning (search terms is on the live chain). Leave autosave/edit behavior for existing content intact.

4. Leave `ArtifactsBaseResumeContent` / `craft_resume_base` on the existing ad-hoc Generate path inside `ArtifactEditor`.

⚠️ **Decision:** One shared POST for Generate and Regenerate (jobs pattern). Only the confirm UX differs — matches parent Notes (“both hand off to REQUESTED_ARTIFACTS; only Regenerate shows the expensive warning”).

⚠️ **Decision:** Do not add candidate Cancel-build in this ticket. In-progress states simply hide Generate via `artifact_generate_states`.

## Execution contract

- Stages in order; one commit per stage on the epic worktree sub; publish to `origin/sub/AST-1243/AST-1253-generate-regenerate-handoff` after each stage per build-child.
- No files outside the Files Changed table.
- Ambiguity or drift → stop and comment on **parent** AST-1243 with the Stage N blocked template.
- Betty owns test/bible updates after Code Complete — engineer does not patch `tests/`.
- Depends on AST-1252 (User Testing): stage entry `craft_get_rubric`, native `run_next` persist, wrappers retired. Sync with `--ftr AST-1243-candidate-artifacts-now-daisy-chain` (full parent segment), not bare `AST-1243`.

## Self-Assessment

**Scope:** `Single-Component` — UI handoff + thin API/core start helper + prior_states / manifest wiring; no dispatch chain rewrite.

**Conf:** `high` — job `generate_artifacts` / `start_artifact_build` is the template; AST-1252 already owns the chain; Generate/Regenerate chrome already exists in `ArtifactEditor` and Company Search Terms.

**Risk:** `Medium` — wrong prior_states or generate-state list blocks Regenerate or allows double-kick while claimed; retiring ad-hoc generate for chain keys is intentional product change (Betty must update ArtifactEditor tests).

## Self-review vs ASTRAL_CODE_RULES

- **§2.6 / `astral.state.core-decides-transitions`:** UI/API call core `start_requested_artifacts` → `transition_candidate_state`; data layer does not choose the target.
- **`astral.dispatch.run-next-is-chain-authority` / §1.4:** Warning hop **order** comes from live `run_next` walk; config holds only an unordered label map, not a sequencing list.
- **§3.5 / `astral.ui.frontend-file-placement` / naming:** Changes stay under existing `ArtifactEditor` + Artifacts pages; new route named like jobs `generate_artifacts`.
- **§1.3 DRY:** Reuse job start-artifact pattern; one POST for both buttons.
- **Betty test-tree ban:** No `tests/` / bible edits in this plan.
- **No conflict requiring conf-!!-NONE.**
