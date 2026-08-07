# Generate/Regenerate REQUESTED_ARTIFACTS handoff

**Linear:** [AST-1253](https://linear.app/astralcareermatch/issue/AST-1253/generateregenerate-requested-artifacts-handoff-candidate-artifacts-now)  
**Parent:** [AST-1243](https://linear.app/astralcareermatch/issue/AST-1243/candidate-artifacts-now-daisy-chain) — Candidate Artifacts now daisy chain  
**Publish ref:** `sub/AST-1243/AST-1253-generate-regenerate-handoff`

Empty-state **Generate** and **Regenerate** on craft-chain Artifacts pages stop calling per-artifact UI `do_task` and instead hand the candidate to `REQUESTED_ARTIFACTS` so AST-1252’s dispatch chain builds the whole rubric set. **Regenerate** alone shows a full-reset warning that names the live `run_next` hops using **Artifacts nav labels** (so Job Description / Get / Do / Like appear as “Job Description Criteria”, “Get Job Criteria”, etc.); default control is **No**. Does **not** own dispatch/persist internals (AST-1252). Does **not** change `craft_resume_base` ad-hoc generate.

⚠️ **Decision (AC5 split):** Child AC5 completion (`ARTIFACTS_READY` + hop content written) is owned by **AST-1252**. This ticket’s AC5 half is **editability**: do not clear artifacts on handoff, and do not alter Save/autosave paths on Artifacts pages — content remains editable under Artifacts nav after the chain finishes.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Expand `REQUESTED_ARTIFACTS.prior_states`; expand `artifact_generate_states`; add unordered `CRAFT_ARTIFACTS_CHAIN_TASK_TO_NAV_PATH` (`task_key` → existing `NAV_CONFIG` path string) — **no** hop sequencing list; **no** DB/`get_agent_task` calls from utils | utils |
| `src/core/candidate.py` | `start_requested_artifacts`; live `run_next` walk helpers; chain membership + NAV-label resolution; reject chain keys in `run_candidate_artifact_generation` | core |
| `src/ui/api/api_candidate.py` | `POST /<id>/generate_artifacts` → core start; keep `/generate/<task_key>` for non-chain only | ui |
| `src/ui/api/api_system.py` | `GET /state_ui_manifest`: merge core chain fields into `candidate` (utils must not walk `agent_task`) | ui |
| `src/ui/frontend/src/contexts/StateUiContext.tsx` | Type `artifacts_chain_task_keys`, `artifacts_chain_hop_labels`, `artifacts_chain_artifact_keys` on `candidate` | ui |
| `src/ui/frontend/src/components/ArtifactEditor.tsx` | Chain pages: Generate/Regenerate → handoff API; Regenerate Yes/No modal (default No); retire per-page ad-hoc generate for chain `taskKey`s | ui |
| `src/ui/frontend/src/pages/ArtifactsCompanySearchTerms.tsx` | Same handoff + Regenerate warning (search terms is a live chain hop) | ui |

**Out of this ticket’s file list (do not touch):** AST-1252 dispatch/persist/retire wrappers; `craft_resume_base` / Base Resume Content generate path; job `BUILD_ARTIFACTS`; hop-order / sequencing lists in `config.py`; Cancel-build for in-progress `REQUESTED_ARTIFACTS`; `tests/` / bible (Betty).

## Stage 1: Config + core handoff

**Done when:** From a candidate in `RESUME_READY`, `ARTIFACTS_READY`, or `ACTIVE_SEARCH`, `start_requested_artifacts(id)` transitions to `REQUESTED_ARTIFACTS` and returns that state string; illegal priors raise `ValueError`; `REQUESTED_ARTIFACTS.prior_states` includes the regenerate re-entry states listed below; walk helpers return the live eight-hop chain from `craft_get_rubric` with NAV labels; `python3 -m py_compile` succeeds on touched modules; no craft-hop sequencing list/frozenset is added to `config.py`; `config.py` does not import data/`get_agent_task`.

1. In `src/utils/config.py`, expand `CANDIDATE_STATES["REQUESTED_ARTIFACTS"]["prior_states"]` to also include: `ARTIFACTS_READY`, `ARTIFACTS_READY_STALE`, `ACTIVE_SEARCH`, `PAUSE_SEARCH` (keep existing `RESUME_READY`, `RESUME_READY_STALE`, `REQUESTED_ARTIFACTS_RETRY`). Do **not** add `REQUESTED_ARTIFACTS_ERROR` (AST-970 ERROR exits stay closed).

⚠️ **Decision:** Parent Original brief requires Regenerate from “whatever state” the operator was on when Generate was available; today’s graph only allowed first entry from resume-ready. Re-entry edges reuse existing vocabulary (no new states) so AC3/AC4 work after ARTIFACTS_READY / ACTIVE_SEARCH without reopening AST-871.

2. In `build_state_ui_manifest()` (same file), set `artifact_generate_states` to:
   `["RESUME_READY", "RESUME_READY_STALE", "ARTIFACTS_READY", "ARTIFACTS_READY_STALE", "ACTIVE_SEARCH", "PAUSE_SEARCH"]`
   with the existing `assert all(s in CANDIDATE_STATES …)`. Do **not** include `REQUESTED_ARTIFACTS` / `*_RETRY` / `*_ERROR` (Generate hidden while the chain is claimed). Do **not** add chain hop fields here — those need a live `agent_task` walk (Stage 2 / `api_system`).

3. Add an **unordered** map near the craft rubric maps: `CRAFT_ARTIFACTS_CHAIN_TASK_TO_NAV_PATH: Dict[str, str]` mapping each chain `task_key` to the existing Artifacts `NAV_CONFIG` `path` string (same paths already listed under Artifacts children), including at least:
   - `craft_get_rubric` → `"/artifacts/get_job_criteria"`
   - `craft_do_rubric` → `"/artifacts/do_job_criteria"`
   - `craft_like_rubric` → `"/artifacts/like_job_criteria"`
   - `craft_jobdesc_rubric` → `"/artifacts/job_description_criteria"`
   - `craft_evaluate_meteorite_rubric` → `"/artifacts/meteorite_criteria"`
   - `craft_joblist_rubric` → `"/artifacts/job_list_criteria"`
   - `craft_prefilter_rubric` → `"/artifacts/company_watch_criteria"`
   - `craft_company_search_terms` → `"/artifacts/company_search_terms"`
   Do **not** invent a parallel short-label vocabulary (“Get”, “Do”, …). Warning copy resolves labels by looking up that path’s `label` in `NAV_CONFIG` (e.g. `"Get Job Criteria"`). AC3’s named hops remain named because those nav strings contain Job Description / Get / Do / Like.

⚠️ **Decision (DRY labels):** One operator vocabulary — Artifacts nav labels — not a second short-name map. Path map is unordered membership plumbing only; hop **order** still comes only from live `run_next`.

⚠️ **Decision:** Do **not** reuse `CRAFT_RUBRIC_UI_TASK_KEYS` as chain membership — it omits `craft_company_search_terms` (terminal hop on the live chain).

4. In `src/core/candidate.py`, add `start_requested_artifacts(candidate_id: str) -> str`:
   - Load candidate; 404-style `ValueError` if missing.
   - Target = `CANDIDATE_STAGE_DISPATCH["requested_artifacts"]["trigger_state"]` (`REQUESTED_ARTIFACTS`).
   - Call `transition_candidate_state(candidate_id, target)` (enforces priors) — **no** extra explicit “must be in X” check before transition.
   - Return `target`. Do **not** clear artifacts here — AST-1252 hop persist overwrites from head on retry/regenerate.

⚠️ **Decision (deliberate divergence from `start_artifact_build`):** Job helper hard-checks `RECOMMENDED` then transitions; this helper lets `transition_candidate_state` + `prior_states` enforce legality and surfaces `ValueError` as HTTP 409. More config-driven; matches `astral.state.core-decides-transitions`.

5. In `src/core/candidate.py`, add helpers (public-then-helpers):
   - `_walk_requested_artifacts_chain_task_keys() -> list[str]`: start at `CANDIDATE_STAGE_DISPATCH["requested_artifacts"]["task_key"]`, follow `_current_agent_task_run_next` until empty. Keep a visited set; if a key repeats, raise `RuntimeError` (defensive only — `database._validate_run_next_graph_acyclic` already rejects cyclic graphs on write, so this should be unreachable for valid seed data). Do **not** cite AST-1252’s worker for cycle handling (that worker does not walk; it calls `do_task` once).
   - `is_requested_artifacts_chain_ui_task(task_key: str) -> bool`: membership in that live walk (not a config hop frozenset; not `CRAFT_RUBRIC_UI_TASK_KEYS`).
   - `requested_artifacts_chain_task_keys() -> list[str]`: public wrapper over the walk (stable order = live `run_next`).
   - `requested_artifacts_chain_hop_labels() -> list[str]`: same order; for each `task_key`, resolve `CRAFT_ARTIFACTS_CHAIN_TASK_TO_NAV_PATH[task_key]` → find that path’s `label` under `NAV_CONFIG` Artifacts children; missing path/label falls back to raw `task_key`.
   - `requested_artifacts_chain_artifact_keys() -> list[str]`: **rubric hops only** — for each walked `task_key` that is in `CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY`, append that artifact key (seven keys). Do **not** append `"company_search_terms"`: since AST-524/525/802 that value is **table-backed**, stripped from the artifacts blob (`ensure_company_search_terms_table_synced` deletes the nested key), and exposed on `GET /api/candidates/<id>` as top-level `company_search_terms` — never under `candidate_data.artifacts`.

6. In `run_candidate_artifact_generation`, if `is_requested_artifacts_chain_ui_task(task_key)`: return `({"success": False, "error": "… use generate_artifacts / REQUESTED_ARTIFACTS …"}, 409)` **before** opening a ledger / calling `do_task`. Leave `craft_resume_base` and any non-chain keys on the existing suppress_run_next path.

⚠️ **Note (acceptable — pending recovery):** Leave `GET …/generate/<task_key>/pending` wired. Dispatch hop persist does not feed that stash; it only serves UI-generate / failed-save recovery. Stale pre-retirement stashes on chain pages are a narrow residue, not a stage.

## Stage 2: API — handoff route + manifest merge

**Done when:** `POST /api/candidates/<id>/generate_artifacts` returns `{"ok": true, "state": "REQUESTED_ARTIFACTS"}` on success, 404 when missing, 409 when `ValueError` from illegal transition; `POST …/generate/craft_get_rubric` returns 409; `POST …/generate/craft_resume_base` still reaches `run_candidate_artifact_generation`; `GET /api/state_ui_manifest` includes the three `candidate.artifacts_chain_*` arrays from core (live walk), with hop **order** matching `run_next` and labels matching Artifacts nav; if the walk raises, those three arrays are `[]` and the rest of the manifest still returns 200.

1. In `src/ui/api/api_candidate.py`, add route `POST /<candidate_id>/generate_artifacts` (`@require_auth`), parallel to `api_jobs.generate_artifacts`:
   - `get_candidate` → 404 if missing.
   - `try: state = start_requested_artifacts(candidate_id)` except `ValueError` → 409 `{"error": str(exc)}`.
   - Return `jsonify({"ok": True, "state": state})`.
2. Keep `POST /<candidate_id>/generate/<task_key>` wired to `run_candidate_artifact_generation` (Stage 1 gate rejects chain keys).
3. In `src/ui/api/api_system.py`, change `state_ui_manifest()` so it:
   - Starts from `manifest = build_state_ui_manifest()` (utils — generate states only).
   - Import the three core helpers at **module scope** beside the existing `from src.core.candidate import get_candidate` (no function-scope late-import hedge — that import path already works).
   - Sets on `manifest["candidate"]` (exact field names — required, not optional):
     - `artifacts_chain_task_keys`: `requested_artifacts_chain_task_keys()`
     - `artifacts_chain_hop_labels`: `requested_artifacts_chain_hop_labels()`
     - `artifacts_chain_artifact_keys`: `requested_artifacts_chain_artifact_keys()`
   - Returns `jsonify(manifest)`.
   - Do **not** move the live walk into `build_state_ui_manifest()` / utils (`astral.standards.utils-data-late-import-only` / §3.3).
4. Walk failure on the manifest route: wrap the three helper calls in `try/except Exception`. On failure: log a warning via `src.utils.logging` (endpoint already has `_log`), set the three `artifacts_chain_*` fields to `[]`, and still return the rest of the manifest (jobs/company/candidate generate states). Do **not** 500 the whole app’s state vocabulary because the live walk failed. Missing/truncated seed already degrades to short arrays via `_current_agent_task_run_next` → `""` without raising.

⚠️ **Decision (fix-now — manifest ownership):** UI API merges live chain fields into the state UI manifest. Config keeps only static unordered path map + generate states. One instruction path for Stage 3 — no “if optional / otherwise heuristic” branches.

⚠️ **Decision (manifest walk failure):** Degrade to empty chain arrays + logged warning; keep the rest of `GET /state_ui_manifest` alive.

## Stage 3: Frontend Generate / Regenerate handoff

**Done when:** On a chain Artifacts page (`ArtifactEditor` with a chain `taskKey`, or Company Search Terms), empty-state **Generate** calls `POST /api/candidates/<id>/generate_artifacts` with **no** scary modal; when any chain artifact already has content, the button reads **Regenerate**, opens a modal that lists every label from `manifest.candidate.artifacts_chain_hop_labels` (nav wording; includes Job Description / Get / Do / Like criteria names), with **No** as the default/cancel control and **Yes** confirming; **Yes** calls the same POST; **No**/overlay dismiss does nothing; after success, candidate list refreshes so `state` is `REQUESTED_ARTIFACTS` and Generate is hidden for in-progress states; Base Resume Content still uses per-artifact `/generate/craft_resume_base`.

1. In `StateUiContext.tsx`, extend `candidate` typing to require:
   - `artifact_generate_states: string[]`
   - `artifacts_chain_task_keys: string[]`
   - `artifacts_chain_hop_labels: string[]`
   - `artifacts_chain_artifact_keys: string[]`

2. In `ArtifactEditor.tsx` (candidate mode only, not `jobPersistence`):
   - Chain handoff when `manifest.candidate.artifacts_chain_task_keys.includes(taskKey)`. **No** `craft_` prefix heuristic; **no** special-case only on `craft_resume_base` beyond “not in the list”.
   - On load of `/api/candidates/<id>`, compute `hasChainData` as true when **either**:
     - any key in `manifest.candidate.artifacts_chain_artifact_keys` has non-empty content in `candidate_data.artifacts` (rubric list with any criterion content / other stored rubric shape), **or**
     - the top-level response field `company_search_terms` (string from AST-526 table-backed attach — **not** `candidate_data.artifacts.company_search_terms`) has `trim() !== ""`.
     Do **not** look for search terms inside the artifacts blob (AST-802 deleted that nested key). Use this combined signal — not only the current page tabs — for Generate vs Regenerate.
   - Replace `doGenerate` for chain keys with `doRequestArtifacts`: `POST /api/candidates/${selectedId}/generate_artifacts`; on success toast “Artifacts build requested — watch Execution History” (or equivalent), `refresh()` from `useCandidate()`, clear confirm state; on 409/error show toast with server `error`.
   - Empty Generate: call `doRequestArtifacts` immediately (no modal).
   - Regenerate: open confirm modal. Copy must state that **all** chain rubrics will be reset / rebuilt, listing every string in `artifacts_chain_hop_labels` (joined readably). Buttons: **No** (`dep-btn cancel`, `autoFocus`) and **Yes** (danger/`#ff6b6b`). Default is No (autofocus + overlay dismiss = No).
   - Remove the old per-artifact “replace current content / Save or Cancel” regenerate copy for chain keys. Keep Cancel/Save review chrome only for non-chain / job persistence paths that still use ad-hoc generate.
   - Do **not** call `/generate/${taskKey}` for chain keys anymore. Leave pending GET recovery as-is (Stage 1 note).

3. In `ArtifactsCompanySearchTerms.tsx`, apply the same handoff + Regenerate warning using the same manifest fields (`taskKey` equivalent = `craft_company_search_terms` membership in `artifacts_chain_task_keys`) and the **same** `hasChainData` rule (rubric keys in artifacts blob **or** top-level `company_search_terms`). Leave autosave/edit behavior for existing content intact (page still reads/writes table-backed terms as today).

4. Leave `ArtifactsBaseResumeContent` / `craft_resume_base` on the existing ad-hoc Generate path inside `ArtifactEditor`.

⚠️ **Decision:** One shared POST for Generate and Regenerate (jobs pattern). Only the confirm UX differs — matches parent Notes (“both hand off to REQUESTED_ARTIFACTS; only Regenerate shows the expensive warning”).

⚠️ **Decision:** Do not add candidate Cancel-build in this ticket. In-progress states simply hide Generate via `artifact_generate_states`.

## Execution contract

- Stages in order; one commit per stage on the epic worktree sub; publish to `origin/sub/AST-1243/AST-1253-generate-regenerate-handoff` after each stage per build-child.
- No files outside the Files Changed table.
- Ambiguity or drift → stop and comment on **parent** AST-1243 with the Stage N blocked template.
- Betty owns test/bible updates after Code Complete — engineer does not patch `tests/`.
- Depends on AST-1252 (User Testing): stage entry `craft_get_rubric`, native `run_next` persist, wrappers retired. Sync with `--ftr AST-1243-candidate-artifacts-now-daisy-chain` (full parent segment), not bare `AST-1243`.

## Revisions

### Revision 1 — 2026-08-07
Driven by: Joan `[plan-discuss] round=1 concern` (plan-rubric.v1 REVISE @ `e98d39d0`).
Changes:
- **fix-now:** Manifest chain fields are required and merged in `api_system.state_ui_manifest` (ui may call core); `api_system.py` added to Files Changed; removed Stage 3 optional/heuristic branches; exact fields `artifacts_chain_task_keys` / `artifacts_chain_hop_labels` / `artifacts_chain_artifact_keys`.
- **discuss:** Cycle handling — cite `_validate_run_next_graph_acyclic`; defensive visited-set `RuntimeError`; drop false AST-1252-worker cross-ref.
- **discuss:** Drop short-label map; resolve warning labels via `NAV_CONFIG` paths (`CRAFT_ARTIFACTS_CHAIN_TASK_TO_NAV_PATH`).
- **discuss:** Explicit AC5 split (completion → AST-1252; editability preserved here).
- **acceptable:** Documented pending-recovery leave-as-is; documented `start_requested_artifacts` prior_states divergence from job helper.

### Revision 2 — 2026-08-07
Driven by: Joan `[plan-discuss] round=2 concern` (plan-rubric.v1 REVISE @ `06382ca7`).
Changes:
- **fix-now:** `hasChainData` reads search terms from top-level `company_search_terms` on `GET /api/candidates/<id>` (AST-526 table-backed); never from `candidate_data.artifacts`. `requested_artifacts_chain_artifact_keys()` is rubric-only (no `"company_search_terms"` blob key).
- **discuss:** Manifest walk failure → empty `artifacts_chain_*` arrays + logged warning; rest of manifest still returns.
- **acceptable:** Dropped Stage 2 late-import hedge; module-scope import beside existing `get_candidate`.

## Self-Assessment

**Scope:** `Single-Component` — UI handoff + thin API/core start helper + prior_states / manifest merge; no dispatch chain rewrite.

**Conf:** `high` — Stage 1→3 contract is decided and named; search-terms content signal now matches AST-526/802 reality.

**Risk:** `Medium` — wrong prior_states or generate-state list blocks Regenerate or allows double-kick while claimed; wrong content signal for the search-terms hop would skip the AC3 warning (mitigated by Revision 2); retiring ad-hoc generate for chain keys is intentional (Betty updates ArtifactEditor tests).

## Self-review vs ASTRAL_CODE_RULES

- **§2.6 / `astral.state.core-decides-transitions`:** UI/API call core `start_requested_artifacts` → `transition_candidate_state`; data layer does not choose the target.
- **`astral.dispatch.run-next-is-chain-authority` / §1.4:** Warning hop **order** comes from live `run_next` walk; config holds only an unordered path map, not a sequencing list.
- **`astral.standards.utils-data-late-import-only` / §3.3:** Live walk stays in core; manifest enrichment in `api_system` (ui→core). Utils does not call `get_agent_task`.
- **§3.5 / `astral.ui.frontend-file-placement` / naming:** Changes stay under existing `ArtifactEditor` + Artifacts pages; new route named like jobs `generate_artifacts`.
- **§1.3 DRY:** Reuse job start-artifact pattern + NAV labels; one POST for both buttons.
- **Betty test-tree ban:** No `tests/` / bible edits in this plan.
- **No conflict requiring conf-!!-NONE.**

## Review

**Publish ref:** `origin/sub/AST-1243/AST-1253-generate-regenerate-handoff`  
**Tip:** `7668bcf9`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `4c6fc90a` | REQUESTED_ARTIFACTS priors + start handoff helpers |
| 2 | `6f7eab54` | generate_artifacts API + manifest chain fields |
| 3 | `7668bcf9` | Generate/Regenerate UI handoff |

## Radia review

[code-rubric] revision=1

**Rubric:** code-rubric.v1
**Publish ref tip:** `1a05e566`
**Overall:** FIX-NOW

**Full-set sweep:** all 65 active statutes scored in-session (18 universal + 47 scoped) against this ticket's own contribution — `git diff 70bf6729..origin/sub/AST-1243/AST-1253-generate-regenerate-handoff` (`70bf6729` = `origin/ftr/AST-1243-candidate-artifacts-now-daisy-chain` tip = AST-1252's resolved sub tip, which this branch correctly forked from per the plan's explicit ftr-sync instruction — `git diff origin/dev...` would otherwise re-score AST-1252's already-reviewed content under this ticket). No violates beyond the finding below.

**What's solid:** Stage 1–3 match the plan closely. `start_requested_artifacts` lets `transition_candidate_state` + `prior_states` enforce legality (no UI-invented target), `REQUESTED_ARTIFACTS.prior_states` expanded exactly as specified, `CRAFT_ARTIFACTS_CHAIN_TASK_TO_NAV_PATH` is an unordered path map (hop **order** stays live-`run_next`-only, no parallel sequencing list), the manifest merge lives in `api_system.py` (ui→core, module-scope import, no late-import hedge) with a clean try/except degrade-to-`[]` + logged warning on walk failure, the chain-key 409 gate in `run_candidate_artifact_generation` fires before any DB/ledger touch, `@require_auth` is present on the new route, and the frontend reads `chainTaskKeys` / `chainHopLabels` / `chainArtifactKeys` entirely from the server manifest (no hardcoded state/business-rule sets in React, matching `astral.layers.ui-config-driven-business-logic`). `python3 -m py_compile` clean on all four touched backend modules. Engineer/Betty test-tree boundary holds (`code(AST-1253)` commits touch only `src/`; `test(AST-1253)` commit touches only `tests/` + `docs/test-bible/`). Test coverage matches every Stage 1–3 "Done when" branch (happy path, 404, 409 illegal prior, chain-key 409, manifest merge, walk-failure degrade).

**Findings**

- **fix-now — DRY / frontend-file-placement (`astral.standards.dry-and-focused-functions`, `astral.ui.frontend-file-placement`):** `artifactBlobHasContent()` is defined verbatim (identical 15-line body) in both `src/ui/frontend/src/components/ArtifactEditor.tsx` and `src/ui/frontend/src/pages/ArtifactsCompanySearchTerms.tsx`. `src/ui/frontend/src/lib/` already exists and holds exactly this kind of shared helper (`rubricDisplay.ts`, `candidateJobActions.ts`, etc.) — extract to a new `lib/` module and import from both.
- **discuss — React re-render hygiene (C6 aid, not a named table entry):** `chainArtifactKeys` (`manifest?.candidate.artifacts_chain_artifact_keys ?? []`) is used inside a `useEffect` dependency array in both files but, unlike the sibling `chainTaskKeys`, isn't wrapped in `useMemo`. While `manifest` is still loading, `?? []` produces a fresh array reference every render, which can re-fire the effect (and its `api()` fetch) repeatedly until the manifest populates — self-heals once `manifest` loads, not fatal, but worth the same memoization treatment as `chainTaskKeys` for consistency.

**Pattern conformance:** `pattern.state.entity-state-transitions` (cited, exists under `canon/patterns/`) — conforms; `start_requested_artifacts` → `transition_candidate_state` only.

**Plan adherence:** Diff matches the Files Changed table exactly. Stage 1–3 "Done when" criteria verified directly (prior_states list, unordered nav-path map, 409 gate placement, manifest merge shape + degrade path, `@require_auth`, compile). Self-Assessment `Scope: Single-Component` / `Conf: high` matches the diff's real footprint; no `!!-NONE` conflict. No Joan plan-rubric verdict attachment on the Linear issue — noting per C4 (not a block); Revisions 1–2 already fold Joan's plan-discuss fix-nows into the shipped code (manifest ownership in `api_system`, top-level `company_search_terms` signal, NAV-label resolution) with no drift from the sweep above.

**Cross-ticket boundary:** No dispatch/persist/retire internals touched (AST-1252 territory, correctly left alone); `craft_resume_base` ad-hoc generate path untouched as planned.

## Frame diff

(none — ticket description AC/scope table already accurate)

context_tokens≈34000

— Radia

## Resolution

**2026-08-07** — Radia [code-rubric] revision=1 addressed on `sub/AST-1243/AST-1253-generate-regenerate-handoff`.

| Finding | Action |
|---------|--------|
| **fix-now** — duplicate `artifactBlobHasContent` | Extracted to `src/ui/frontend/src/lib/artifactBlobHasContent.ts`; both `ArtifactEditor` and `ArtifactsCompanySearchTerms` import it. |
| **discuss** — `chainArtifactKeys` not memoized | Wrapped in `useMemo` on the same source array as `chainTaskKeys`, in both files. |
