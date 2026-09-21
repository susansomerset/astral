<!-- linear-archive: AST-1253 archived 2026-08-17 -->

## Linear archive (AST-1253)

**Archived:** 2026-08-17  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1253/generateregenerate-requested-artifacts-handoff-candidate-artifacts-now  
**Status at archive:** Archive  
**Project:** Astral Candidate  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1243 — Candidate Artifacts now daisy chain  
**Blocked by / blocks / related:** parent: AST-1243

### Description

## What this implements

**Regenerate:** full-rubric-reset warning (Job Description, Get, Do, Like, and other live chain hops named; default **NO**); on **YES**, transition to `REQUESTED_ARTIFACTS`. **Generate** (empty state): same handoff to `REQUESTED_ARTIFACTS` / dispatch build path **without** the scary warning. Retire per-artifact ad-hoc generate as the build path for these craft rubrics.

## In scope

- [X] `pattern.state.entity-state-transitions` — Generate/Regenerate hand off via core transition into `REQUESTED_ARTIFACTS`
- [X] `astral.state.core-decides-transitions` — API calls `start_requested_artifacts` → `transition_candidate_state`; UI does not invent the target
- [X] `astral.ui.frontend-file-placement` — handoff UX stays in `ArtifactEditor` + Artifacts Company Search Terms page
- [X] `astral.ui.naming-conventions` — route/action naming mirrors jobs `generate_artifacts`
- [X] `astral.standards.utils-data-late-import-only` — live `run_next` walk stays in core; `api_system.state_ui_manifest` merges chain fields (utils does not call `get_agent_task`)
- [X] Expand `REQUESTED_ARTIFACTS.prior_states` for regenerate re-entry from `ARTIFACTS_READY` / `ACTIVE_SEARCH` / `PAUSE_SEARCH` (+ stale companions already named in plan)
- [X] Live `run_next` walk for warning hop **order**; unordered `task_key`→`NAV_CONFIG` path map only in config (no hop sequencing list; nav labels, not a second short vocabulary)
- [X] Retire chain-key ad-hoc UI generate (`/generate/<craft_*>` → 409 for chain keys); keep `craft_resume_base`

## Considered but excluded

- [X] Dispatch chain internals / persist / wrapper retire — AST-1252
- [X] `astral.dispatch.run-next-is-chain-authority` product ownership — succession already shipped on AST-1252; this ticket only reads live walk for warning labels / membership
- [X] Cancel-build for in-progress `REQUESTED_ARTIFACTS` — not in child AC
- [X] `craft_resume_base` / Base Resume Content ad-hoc generate — not on the artifacts daisy chain
- [X] Job `BUILD_ARTIFACTS` behavior — reference pattern only
- [X] `REQUESTED_ARTIFACTS_ERROR` → re-request prior — AST-970 ERROR exits stay closed
- [X] Putting live chain walk inside `build_state_ui_manifest()` / utils — barred by utils→data statute
- [X] `tests/` / `docs/test-bible/**` — Betty after Code Complete

## Acceptance criteria

- [X] 3. **Regenerate** shows a warning that **all** chain rubrics will be reset (explicitly includes Job Description, Get, Do, Like, and the other hops in the live chain); default control is **NO** / cancel; **YES** moves the candidate to `REQUESTED_ARTIFACTS`.
- [X] 4. Empty-state **Generate** also moves the candidate to `REQUESTED_ARTIFACTS` / starts the same dispatch build path, without the full-reset scary warning.
- [X] 5. On successful completion, candidate is in `ARTIFACTS_READY` (or the configured success state) and each chain rubric’s new content is visible and editable under Artifacts nav. (UI editability after chain — sibling #1 owns chain completion.)

## Boundaries

Does **not** own dispatch chain internals (sibling #1 / AST-1252). After AST-1252.

## Notes for planning

Generate and Regenerate both hand off to `REQUESTED_ARTIFACTS`; only Regenerate shows the expensive full-reset warning.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1243-candidate-artifacts-now-daisy-chain`, child `sub/AST-1243/<this-id>-generate-regenerate-handoff`. Created at dispatch-parent.

### Comments

#### radia — 2026-08-07T08:31:24.906Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1253
**Publish ref:** `origin/sub/AST-1243/AST-1253-generate-regenerate-handoff` @ `efb8fb9b` (docs commit) / code tip `1a05e566`
**Overall:** FIX-NOW

Full 65-statute sweep (18 universal + 47 scoped) run in-session, scoped to this ticket's own contribution: `git diff 70bf6729..origin/sub/AST-1243/AST-1253-generate-regenerate-handoff`, where `70bf6729` = `origin/ftr/AST-1243-candidate-artifacts-now-daisy-chain` tip = AST-1252's resolved sub tip. This branch correctly forked from ftr per the plan's explicit sync instruction; a raw `origin/dev...` diff would otherwise re-score AST-1252's already-reviewed content under this ticket. Full checked-list is off-ticket per C1–C4; summary below.

## Plan adherence

- Diff matches the Files Changed table exactly.
- Stage 1–3 "Done when" criteria verified directly: `REQUESTED_ARTIFACTS.prior_states` expanded exactly as specified (no `REQUESTED_ARTIFACTS_ERROR` added); `CRAFT_ARTIFACTS_CHAIN_TASK_TO_NAV_PATH` is an unordered path map (hop order stays live-`run_next`-only); the chain-key 409 gate in `run_candidate_artifact_generation` fires before any DB/ledger touch; `api_system.state_ui_manifest` merges the three chain arrays via module-scope import with a clean try/except degrade-to-`[]` + logged warning; `@require_auth` present on the new route; `python3 -m py_compile` clean on all four touched backend modules.
- Self-Assessment `Scope: Single-Component` / `Conf: high` matches the diff's real footprint; no `!!-NONE` conflict. No Joan plan-rubric verdict attached on this issue — noting per C4 (not a block); Revisions 1–2 already fold Joan's plan-discuss fix-nows into the shipped code with no drift from this sweep.

## Findings

- **fix-now — DRY / frontend-file-placement:** `artifactBlobHasContent()` is defined verbatim (identical 15-line body) in both `src/ui/frontend/src/components/ArtifactEditor.tsx` and `src/ui/frontend/src/pages/ArtifactsCompanySearchTerms.tsx`. `src/ui/frontend/src/lib/` already holds exactly this kind of shared helper (`rubricDisplay.ts`, `candidateJobActions.ts`, etc.) — extract to a new `lib/` module and import from both.
- **discuss — React re-render hygiene:** `chainArtifactKeys` (`manifest?.candidate.artifacts_chain_artifact_keys ?? []`) is used inside a `useEffect` dependency array in both files but, unlike the sibling `chainTaskKeys`, isn't wrapped in `useMemo`. While `manifest` is still loading, `?? []` produces a fresh array reference every render, which can re-fire the effect (and its fetch) repeatedly until the manifest populates — self-heals once loaded, not fatal, but worth the same memoization treatment as `chainTaskKeys` for consistency.

## Cross-ticket boundary

No dispatch/persist/retire internals touched (AST-1252 territory, correctly left alone); `craft_resume_base` ad-hoc generate path untouched as planned.

## Pattern conformance

`pattern.state.entity-state-transitions` — cited, exists under `canon/patterns/`, conforms (`start_requested_artifacts` → `transition_candidate_state` only, no UI-invented target).

## What's solid

Frontend reads `chainTaskKeys` / `chainHopLabels` / `chainArtifactKeys` entirely from the server manifest — no hardcoded state/business-rule sets in React, a clean match for `astral.layers.ui-config-driven-business-logic`. Test coverage matches every Stage 1–3 "Done when" branch (happy path, 404, 409 illegal prior, chain-key 409, manifest merge, walk-failure degrade). Engineer/Betty test-tree boundary holds cleanly.

## Frame diff

(none — ticket description AC/scope table already accurate)

context_tokens≈38000

— Radia

#### betty — 2026-08-07T08:23:11.166Z
## QA test manifest (AST-1253)

**Publish:** `origin/sub/AST-1243/AST-1253-generate-regenerate-handoff` @ `1a05e566` (`merge-tests(AST-1253): origin/tests 4e6ab98b`)

### Broken / obsolete (revised this pass)
1. AST-901 craft_get_rubric UI generate success-stash — chain keys return **409** (`TestAst901CraftRubricGenerateDelivery`)
2. `artifact_generate_states == [RESUME_READY, ACTIVE_SEARCH]` — expanded generate states (`TestAst970CandidateStateRegistry`)
3. AST-677 / Search Terms ad-hoc `POST …/generate/craft_*` — handoff via `generate_artifacts` + Yes/No modal
4. AST-904 Save-after-regen on `craft_get_rubric` — moved to non-chain `craft_rubric`

### Manifest
1. `tests/component/core/test_candidate.py::TestAst1253RequestedArtifactsHandoff`
2. `tests/component/core/test_candidate.py::TestAst901CraftRubricGenerateDelivery`
3. `tests/component/utils/test_config.py::TestAst1253GenerateRegenerateHandoffConfig`
4. `tests/component/utils/test_config.py::TestAst970CandidateStateRegistry::test_nav_and_gen_states_use_new_vocab`
5. `tests/component/ui/api/test_api_candidate.py::TestAst1253GenerateArtifactsApi`
6. `tests/component/ui/api/test_api_system.py::TestAst1253StateUiManifestChainFields`
7. Vitest `test_ArtifactEditor.test.tsx` — `AST-1253:*` + `AST-904`
8. Vitest `test_ArtifactsCompanySearchTerms.test.tsx` — `AST-1253:*` + revised AST-645
9. Vitest `test_ArtifactsCompanyWatchCriteria.test.tsx` — `AST-1253: Regenerate Yes POSTs generate_artifacts`

### Narrowed run
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst1253RequestedArtifactsHandoff \
  tests/component/core/test_candidate.py::TestAst901CraftRubricGenerateDelivery \
  tests/component/utils/test_config.py::TestAst1253GenerateRegenerateHandoffConfig \
  tests/component/utils/test_config.py::TestAst970CandidateStateRegistry::test_nav_and_gen_states_use_new_vocab \
  tests/component/ui/api/test_api_candidate.py::TestAst1253GenerateArtifactsApi \
  tests/component/ui/api/test_api_system.py::TestAst1253StateUiManifestChainFields \
  -q
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_ArtifactEditor.test.tsx \
  ../../../tests/component/frontend/pages/test_ArtifactsCompanySearchTerms.test.tsx \
  ../../../tests/component/frontend/pages/test_ArtifactsCompanyWatchCriteria.test.tsx \
  --testNamePattern='AST-1253|AST-904|AST-645|Regenerate Yes|renders company'
```

### Bible shasum (`origin/sub/…`)
- `docs/test-bible/core/candidate.md` `31635aa19f9d4595676a486985f6fd92cd1e40c1044dfadd458b8c71addce9df`
- `docs/test-bible/utils/config.md` `d27eb7a9b491e2449ddce2b730665fc0327f849a0c598906975cdc92756a2ac6`
- `docs/test-bible/ui/api/api_candidate.md` `924581d2be2234cf4f8faa55d555413e790e77718b612e57b5780872f4ba8718`
- `docs/test-bible/ui/api/api_system.md` `0a813921f3a7791bd5f34e136621bdf0210fe37761825c49066c15b8d8cdb6a4`
- `docs/test-bible/frontend/components.md` `03627e6ed2218c66dc0f494f9c6a8cc154bb51e2badac8b319ceb160bbf66500`
- `docs/test-bible/frontend/pages.md` `2f6cf9306ff8a7a06e38cf15d61a2d00b0bf3153e7302684972ff0a7e06ce82b`

**Integration:** none revised.

#### joan — 2026-08-07T08:07:30.320Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1253
**Overall:** APPROVED
**Publish ref tip:** `sub/AST-1243/AST-1253-generate-regenerate-handoff` @ `df68a988`

## Traceability

AC3→S1–3; AC4→S1–3; AC5→S3 editability half + stated boundary to AST-1252 for chain completion. No unmapped AC, no orphan stages.

**Considered:** 59 (18 universal + 41 scoped); 6 scoped excluded on layer/path predicates. Scored in-session per R7. Plan layers `{utils, core, ui}`, Files Changed unchanged since revision 1 — no `violates` remaining.

## Round 2 items — all three closed, verified against the tree

The fix-now is fixed at both ends, which is what I wanted rather than a patch at one. `requested_artifacts_chain_artifact_keys()` is now rubric-only — the seven `CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY` values, which are exactly the seven keys `hydrate_rubric_artifacts_for_response` overlays into `candidate_data.artifacts` on the GET response. And `hasChainData` became an explicit two-branch signal: rubric keys in the artifacts blob, **or** top-level `company_search_terms` with `trim() !== ""`. That second branch is the same test `ArtifactsCompanySearchTerms.tsx` already uses today (`hasData = text.trim() !== ""`, line 42, fed by `c.company_search_terms` at line 49), so the page keeps a working signal instead of trading one for a broken one. Stage 3 step 3 now applies the same combined rule rather than pointing at "the same manifest fields," which was where the regression came from. The AST-802 / AST-526 reasoning is written into the plan inline, so the next person to touch this won't reach back into the blob.

One thing I checked because the plan depends on it silently: `ArtifactEditor.tsx` already fetches `/api/candidates/${selectedId}` at line 284, so the top-level `company_search_terms` field is in a response the component loads anyway. The new branch costs no extra request. The `!jobPersistence` scoping the plan asserts also matches the existing structure — `canGenerate = !jobPersistence && generateStates.has(candidateState)` at line 188.

The manifest-failure discuss is closed better than I asked. I suggested empty arrays plus a logged warning; Stage 2 step 4 specifies that, and it turns out to be the established pattern in the very file being edited — `api_system.py` lines 59 and 77 already do `_log.debug("Failed to compute company nav counts", exc_info=True)` and degrade that section rather than failing the response. `_log` is real (line 28). So the engineer is copying a house pattern from ten lines up, not inventing error handling. The Stage 2 "Done when" now carries the degraded case explicitly, which is what makes it testable.

The late-import hedge is gone and replaced with a module-scope import beside the existing `from src.core.candidate import get_candidate`. Correct — that import path already works today.

## Findings

No `fix-now`. No `discuss`. Two notes:

### acceptable — the three `artifacts_chain_*` arrays are no longer the same length

`artifacts_chain_task_keys` and `artifacts_chain_hop_labels` are the eight live hops; `artifacts_chain_artifact_keys` is now seven. That asymmetry is correct and deliberate — the terminal hop has no artifacts-blob key — and the plan says "rubric hops only … (seven keys)" in the helper description. Worth knowing because the earlier wording promised all three in the "same order," and anything that later zips them by index will be off by one at the tail. Stage 3 consumes each independently (membership, modal copy, content check), so nothing in this ticket is exposed. A short comment on the helper at implementation time would keep it that way.

### acceptable — carried forward from round 1, unchanged and still fine

The `…/generate/<task_key>/pending` recovery stays wired for chain keys, and `start_requested_artifacts` leans on `prior_states` rather than an explicit state pre-check. Both were reviewed in round 1, both are documented in the plan as intentional, and neither changed in revisions 1 or 2.

## Notes

This converged the way the discuss loop is supposed to. Round 1 was a layer boundary — the hop order needs the database and `build_state_ui_manifest()` lives in `utils`; that closed by moving the merge into the API layer. Round 2 was a factual claim about where company search terms live, which mattered only because it sat under the one field AC3's warning depends on; that closed by splitting the content signal to match how the data is actually stored. Neither round moved the spine of the plan, which was right from the first publish: order from the live `run_next` walk, only an unordered map in config, one POST for both buttons, and Generate hidden while the chain is claimed. AC8's prohibition on hop sequencing in `config.py` is respected throughout.

Self-assessment is honest. `Conf: high` is now earned rather than asserted — the Stage 1→Stage 3 contract is named, single-path, and the content signal matches AST-526/802 reality. `Risk: Medium` is right, and revision 2 added the search-terms hazard to the named risks instead of quietly dropping it once fixed, which is the correct way to keep a risk list useful.

One thing for the build: the plan's Execution contract still says "No files outside the Files Changed table," and the table is unchanged since revision 1. It lists the seven files this needs, including `src/ui/api/api_system.py`. That should hold, but if the search-terms branch turns out to need a shape change on the candidate GET response, that is a stop-and-comment on AST-1243, not a quiet eighth file.

Status → **Plan Approved**.

context_tokens≈79000

— Joan

#### katherine — 2026-08-07T08:05:19.938Z
[plan-discuss] round=2 reply

Plan revised on `origin/sub/AST-1243/AST-1253-generate-regenerate-handoff` @ `df68a988`.

[docs/features/candidate/ast-1253-generate-regenerate-requested-artifacts-handoff.md](https://github.com/susansomerset/astral/blob/sub/AST-1243/AST-1253-generate-regenerate-handoff/docs/features/candidate/ast-1253-generate-regenerate-requested-artifacts-handoff.md)

**Delta vs round=2 concern**
1. **fix-now (search-terms signal):** `hasChainData` = non-empty rubric keys in `candidate_data.artifacts` **or** top-level `company_search_terms` on `GET /api/candidates/<id>` (AST-526). Never read search terms from the artifacts blob (AST-802). `requested_artifacts_chain_artifact_keys()` is rubric-only — no `"company_search_terms"` fallback.
2. **discuss (manifest walk failure):** empty `artifacts_chain_*` + logged warning; rest of manifest still 200.
3. **acceptable:** Dropped late-import hedge; module-scope import beside existing `get_candidate`.

Status left at **Plan Discuss** for Joan re-validate.

#### joan — 2026-08-07T08:03:35.433Z
[plan-discuss] round=2 concern
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1253
**Overall:** REVISE
**Publish ref tip:** `sub/AST-1243/AST-1253-generate-regenerate-handoff` @ `06382ca7`

## Traceability

AC3→S1–3; AC4→S1–3; AC5→S3 editability half + explicit boundary to AST-1252 for completion. No orphan stages.

**Considered:** 59 (18 universal + 41 scoped); 6 scoped excluded on layer/path predicates. Scored in-session per R7. Plan layers `{utils, core, ui}` — unchanged by the added `api_system.py` row.

## Round 1 items — all four cleared, and I checked the fix rather than the summary

The manifest fix-now is genuinely resolved, and it landed on better ground than the plan claims for itself. `src/ui/api/api_system.py` already imports `from src.core.candidate import get_candidate` at module scope (line 8), so the three chain helpers can join that same import — the plan's Stage 2 hedge "(late/import at function scope if needed for cycles)" is insurance against a cycle that demonstrably isn't there. Harmless as written; you can drop the hedge. `state_ui_manifest()` is at line 179 behind `@require_auth`, `build_state_ui_manifest()` has exactly one caller, and it is that route — so merging in the API layer reaches every consumer with no second path to keep in sync.

The DRY-labels fix is better than a compliance gesture. I checked all eight `NAV_CONFIG` path strings in your map against config lines 4487–4495 and every one resolves: `/artifacts/get_job_criteria` → "Get Job Criteria", `/artifacts/do_job_criteria` → "Do Job Criteria", `/artifacts/like_job_criteria` → "Like Job Criteria", `/artifacts/job_description_criteria` → "Job Description Criteria", plus meteorite / job list / company watch / company search terms. AC3's four named hops survive the switch to nav wording, which was the thing I was worried about when I asked for it.

The cycle cross-ref now points at `_validate_run_next_graph_acyclic` (`src/data/database.py:4707`) — real, and called on write at 4745. `_current_agent_task_run_next` is at `src/core/agent.py:3180` and already imported by `src/core/candidate.py:24`. The AC5 split is stated. And the six-state `artifact_generate_states` list still passes the `assert all(s in CANDIDATE_STATES …)` — I confirmed `PAUSE_SEARCH` (line 1263) and `ARTIFACTS_READY_STALE` (1255) exist, and today's `REQUESTED_ARTIFACTS.prior_states` is still exactly the three you say to keep.

Your `CRAFT_RUBRIC_UI_TASK_KEYS` decision is also right, and now for a second reason: the seven artifact keys in `CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY` match the seven keys of `RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY` exactly, which is what `hydrate_rubric_artifacts_for_response` overlays into the GET response. So the rubric side of your Stage 3 content check lines up perfectly.

Which is what makes the eighth member stand out.

## Findings

### fix-now — Stage 3 looks for the Company Search Terms hop in `candidate_data.artifacts`, where AST-802 guarantees it is never present

Stage 1 step 5 defines the artifact key for the terminal hop as:

> `CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY.get(task_key)` or `"company_search_terms"` for `craft_company_search_terms` (same persist key AST-1252 / company-search UI already use)

and Stage 3 step 2 consumes it as:

> compute `hasChainData`: any key in `manifest.candidate.artifacts_chain_artifact_keys` has non-empty content in `candidate_data.artifacts` (rubric list with any criterion content, or non-empty search-terms / other stored shape)

The parenthetical justification is the part that isn't true, and it's load-bearing. Company search terms have not lived in the artifacts blob since AST-524/525/802. `ensure_company_search_terms_table_synced` (`src/core/candidate.py:1385`) reconciles the legacy blob into the `company_search_terms` table and then **deletes the key** — `del updated_arts["company_search_terms"]` at line 1399, with `replace=True` specifically because "deep-merge cannot delete nested artifact keys (AST-802)." `company_search_terms_lines` at 1380 is docstringed "table-backed search term lines (AST-525); **artifact path removed**."

The UI half of the claim is wrong in the same direction. `GET /api/candidates/<id>` attaches the value as a **top-level** field, not inside `candidate_data`:

> `# AST-526: table-backed field for Artifacts textarea (not artifacts blob).`
> `candidate["company_search_terms"] = company_search_terms_joined_text(candidate_id)`

and `ArtifactsCompanySearchTerms.tsx` reads exactly that — `const raw = c.company_search_terms` (line 49), with `hasData = text.trim() !== ""` (line 42). So the page's Generate/Regenerate detection is correct **today**, and Stage 3 step 3 instructs the engineer to replace it with the manifest computation, which for this page's own artifact can only ever evaluate false.

Two consequences, and I want to be straight about the size of each. The narrow one is a genuine AC3 defeat: a candidate holding search terms but no rubric content sees **Generate**, gets no modal, and kicks a full chain reset with no warning — the exact thing AC3 exists to prevent. That combination is uncommon, since search terms and rubrics normally arrive together after a chain run. The broader one is that Stage 3 step 3 is a regression on a working surface, on the page this ticket explicitly owns. Neither is fatal, but the instruction points the engineer at an object that provably never holds the value, and your Execution contract turns that into a stop-and-comment on AST-1243.

**Recommendation:** keep `artifacts_chain_artifact_keys` as-is for the seven rubric hops — that half is verified correct — and say in Stage 3 step 2 that the search-terms member is read from the top-level `company_search_terms` field on `GET /api/candidates/<id>`, not from `candidate_data.artifacts`. One clause. Then either drop the `"company_search_terms"` fallback from `requested_artifacts_chain_artifact_keys()` or annotate it as a table-backed key so nobody later "fixes" Stage 3 by reaching back into the blob. If you would rather not special-case it, the other clean answer is to have `hasChainData` reuse each page's existing content signal, since both surfaces already compute one correctly.

### discuss — the manifest endpoint stops being infallible, and the plan doesn't say what happens when the walk fails

This one is downstream of my round 1 recommendation, so it's mine as much as yours. `build_state_ui_manifest()` is pure config — it cannot touch the database and cannot fail on data. Stage 2 step 3 adds three live `agent_task` walks to the same response, which makes `GET /api/state_ui_manifest` DB-dependent for the first time. That endpoint serves the whole app's state vocabulary — jobs, companies, candidate — so a raise inside the walk takes down every page's manifest load, not just the Artifacts surfaces.

Most of the failure surface is already benign: `_current_agent_task_run_next` returns `""` for a missing row rather than raising, so an absent or truncated seed degrades to short arrays and a thin warning, not a 500. The two paths that would propagate are a DB error inside `get_agent_task` and the new defensive `RuntimeError` you added for cycles — which, by your own (correct) citation of `_validate_run_next_graph_acyclic`, should be unreachable for valid seed data. **Recommendation:** one line in Stage 2 saying what the endpoint does if the walk raises. Empty arrays plus a logged warning keeps the rest of the manifest alive and degrades only the Regenerate warning copy; propagating is also a defensible choice, but it should be a choice rather than a side effect.

### acceptable — the Stage 2 late-import hedge is unnecessary

Noted above: `api_system.py` already imports `src.core.candidate` at module scope, so there is no cycle to work around. Leaving the hedge in costs nothing; removing it is one fewer conditional for the engineer to reason about.

## Notes

Everything I asked for in round 1 is done, and done in the stronger form each time — the manifest fields are required rather than optional, the Stage 3 conditionals are gone, the `craft_` prefix heuristic is gone, and the label vocabulary collapsed into `NAV_CONFIG` instead of a parallel map. The layer question that blocked round 1 is closed cleanly and I verified the import path rather than taking the delta note's word for it.

What blocks now is smaller and more specific than round 1: a single factual claim about where company search terms live, which happens to sit under the one manifest field that Stage 3's Generate-vs-Regenerate decision depends on. Fixing it is a clause, not a redesign, and the seven-rubric half of the same mechanism is already verified correct.

Self-assessment: `Conf: high` is now earned — the Stage 1 output Stage 3 depends on is decided and named. `Risk: Medium` remains honest and names the right hazards, though "wrong prior_states or generate-state list" could fairly be joined by "wrong content signal for the search-terms hop."

context_tokens≈58000

— Joan

#### katherine — 2026-08-07T07:58:17.109Z
[plan-discuss] round=1 reply

Plan revised on `origin/sub/AST-1243/AST-1253-generate-regenerate-handoff` @ `06382ca7`.

[docs/features/candidate/ast-1253-generate-regenerate-requested-artifacts-handoff.md](https://github.com/susansomerset/astral/blob/sub/AST-1243/AST-1253-generate-regenerate-handoff/docs/features/candidate/ast-1253-generate-regenerate-requested-artifacts-handoff.md)

**Delta vs round=1 concern**
1. **fix-now (manifest):** Decided — `api_system.state_ui_manifest` merges required `candidate.artifacts_chain_task_keys` / `artifacts_chain_hop_labels` / `artifacts_chain_artifact_keys` from core walk helpers. `api_system.py` added to Files Changed. Stage 3 conditionals / `craft_` heuristic removed. Utils does not walk `agent_task`.
2. **discuss (cycle):** Dropped false AST-1252-worker cross-ref; cite `_validate_run_next_graph_acyclic` + defensive visited-set `RuntimeError`.
3. **discuss (labels):** Dropped short-label map; resolve via `NAV_CONFIG` using unordered `CRAFT_ARTIFACTS_CHAIN_TASK_TO_NAV_PATH`.
4. **discuss (AC5):** Explicit split — completion → AST-1252; editability preserved here (no clear, save paths untouched).
5. **acceptable:** Pending recovery + prior_states-vs-job-helper divergence documented as intentional.

Status left at **Plan Discuss** for Joan re-validate.

#### joan — 2026-08-07T07:54:56.486Z
[plan-discuss] round=1 concern
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1253
**Overall:** REVISE
**Publish ref tip:** `sub/AST-1243/AST-1253-generate-regenerate-handoff` @ `e98d39d0`

## Traceability

AC3→S1–3; AC4→S1–3; AC5→S3 in part (editability preserved) + boundary to AST-1252 for chain completion. No orphan stages.

**Considered:** 59 (18 universal + 41 scoped); 6 scoped excluded on layer/path predicates. Scored in-session per R7. Plan layers `{utils, core, ui}`.

**Verified against the tree rather than assumed — all of these hold.** Every state the plan names exists (`RESUME_READY`, `RESUME_READY_STALE`, `ARTIFACTS_READY`, `ARTIFACTS_READY_STALE`, `ACTIVE_SEARCH`, `PAUSE_SEARCH`, `REQUESTED_ARTIFACTS_RETRY`), and today's `REQUESTED_ARTIFACTS.prior_states` is exactly the three the plan says to keep. `gen_states` is `["RESUME_READY", "ACTIVE_SEARCH"]` behind the `assert all(s in CANDIDATE_STATES ...)` the plan cites, and all six proposed members pass it. AST-1252 has landed on this branch: `CANDIDATE_STAGE_DISPATCH["requested_artifacts"]` exists with `task_key: craft_get_rubric` / `trigger_state: REQUESTED_ARTIFACTS`. `tracker.start_artifact_build` is a real template, `_current_agent_task_run_next` already lives in `src/core/agent.py` and is already imported by `src/core/candidate.py`, and `run_candidate_artifact_generation` is where the plan says with the `suppress_run_next` ctx flag it describes. Every frontend surface checks out — `ArtifactEditor.tsx` has `taskKey`, `jobPersistence`, `doGenerate`, `hasData ? "Regenerate" : "Generate"`, an existing confirm modal using `dep-btn cancel` and `#ff6b6b`, and `StateUiContext` already types `candidate: { artifact_generate_states: string[] }`.

**And I walked the live chain in `data/admin/agent_task.json` rather than trusting the label list.** From `craft_get_rubric`, `run_next` gives exactly eight hops: `craft_get_rubric` → `craft_do_rubric` → `craft_like_rubric` → `craft_evaluate_meteorite_rubric` → `craft_jobdesc_rubric` → `craft_joblist_rubric` → `craft_prefilter_rubric` → `craft_company_search_terms` (terminal). That is precisely the eight keys in your label map, `craft_resume_base` is the only off-chain `craft_*` key in the seed, and Company Search Terms genuinely is a live hop. So AC3's "Job Description, Get, Do, Like" are all really on the chain and your Stage 3 fallback heuristic (`craft_` prefix minus `craft_resume_base`) is correct against the current seed — I went looking for a mismatch there and there isn't one.

## Findings

### fix-now — the state-UI-manifest exposure that Stage 3 depends on is never actually specified by any step, and the one file allowed to do it is barred from doing it

Stage 3 is written against manifest fields that no Stage 1 step creates. Step 2 touches `build_state_ui_manifest()` only for `artifact_generate_states`; step 3 adds the label map to config; step 5 calls the labels helper "(for warning + **optional** manifest)". The Files Changed row for `StateUiContext.tsx` says "Type manifest fields for chain regenerate hop labels **(if added)**". Then Stage 3 branches on the outcome three separate times:

> 1. **If** Stage 1 exposes hop labels on the state UI manifest (`candidate.artifacts_chain_hop_labels: string[]`) … **Otherwise** call a tiny helper that formats labels from a prop/constant filled once from the manifest load

> Prefer an explicit manifest `artifacts_chain_task_keys` list … **or**, if only labels are exposed, when `taskKey` starts with `craft_`

Two manifest field names appear (`artifacts_chain_hop_labels`, `artifacts_chain_task_keys`), neither is created anywhere, and the "otherwise" branch is self-contradictory — it routes the no-manifest case through "filled once from the manifest load." Your own Execution contract makes ambiguity a stop-and-comment on parent AST-1243, so as written the engineer stops in Stage 3 and asks you this question.

What makes it a fix-now rather than a wording tidy is that the answer is constrained, and the plan's file list currently forbids the correct one. The hop **order** has to come from the live `run_next` walk, which needs `agent_task` from the DB. `build_state_ui_manifest()` lives in `src/utils/config.py`, and `astral.standards.utils-data-late-import-only` is unambiguous:

> The only approved runtime `utils → data` path is a late import of `add_log_entry` inside `_DatabaseLogHandler._flush_buffer` in `logging.py`. Do not copy this pattern elsewhere in utils.

Code Rules §3.3 says the same (`utils → nothing`, logging sink excepted). I do want to name the thing that will otherwise look like precedent: `config.py` already late-imports `get_agent_task` at lines 5118 and 5158 (`_agent_task_parents_with_run_next`, `dispatch_chain_row_matches_job`) and `src.core.candidate` at 5578 / 5621. That is pre-existing debt, not a license — extending it is the specific thing the statute prohibits, and a new one added by this ticket is the one Radia will land on.

The sanctioned shape is already written down in §3.2: "UI business logic lives in the API layer, driven by config." `GET /api/state_ui_manifest` is served by `api_system.state_ui_manifest()`, which is `ui` and may import `core` freely. Have the API layer merge `requested_artifacts_chain_hop_labels()` (and the task-key list, if you want membership to be authoritative rather than heuristic) into the manifest response, leaving the unordered label map in config as the static half.

**Recommendation:** decide it in the plan, one way, and add `src/ui/api/api_system.py` to the Files Changed table — the plan currently says "No files outside the Files Changed table," so the correct implementation is out of bounds until you list it. Name the exact field(s) you are adding, add them to Stage 1 (or a new step) as a real step rather than "optional," and delete the Stage 3 conditionals so there is a single instruction. If you would rather not touch the manifest at all, that is also fine — but then say so and have Stage 3 read the labels from a dedicated endpoint or from the `generate_artifacts` response, and drop the `craft_` prefix heuristic in favour of that.

### discuss — "stop on cycle the same way AST-1252 worker does" points at behavior AST-1252 does not have

Stage 1 step 5:

> follow `_current_agent_task_run_next` until empty; raise/stop on cycle the same way AST-1252 worker does.

AST-1252's worker (`run_requested_artifacts_dispatch` in `src/core/candidate.py`) does not walk the chain and has no cycle handling — it calls `do_task` once on the entry hop and lets native `run_next` recursion handle succession. There is no pattern there to copy, so this step has no resolvable referent.

The guard you actually want already exists one layer down: `_validate_run_next_graph_acyclic` in `src/data/database.py` (line 4707) validates the whole `run_next` graph as acyclic on write, so a cycle cannot be present in the data your walk reads. **Recommendation:** either cite that validator as the reason no runtime cycle check is needed, or specify a plain visited-set bail with what it does on hit. Do not leave it as a cross-reference to a sibling behavior that isn't there.

### discuss — `CRAFT_ARTIFACTS_CHAIN_HOP_LABELS` invents a second display vocabulary for artifacts that already have labels

`NAV_CONFIG` already carries operator-facing labels for exactly these artifacts (config lines 4488–4495): "Company Watch Criteria", "Company Search Terms", "Job List Criteria", "Job Description Criteria", "Meteorite Criteria", "Get Job Criteria", "Do Job Criteria", "Like Job Criteria". Your map introduces a parallel, shorter set ("Company Watch", "Job List", "Job Description", "Meteorite", "Get", "Do", "Like") for the same nine things, in the same file. Two vocabularies for one set of entities drift, and §1.3 / §2.1 both point the other way.

I am filing this as discuss rather than fix-now because there is no existing `task_key → label` map to reuse — `CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY` gets you `task_key → artifact_key` and the nav labels are keyed by route path, so either choice needs a hop of new plumbing. But the warning names things the candidate is about to go look at in the Artifacts nav, so matching the nav wording is both the DRY answer and the better product answer. Worth one line either way saying why you chose short labels if you keep them.

One related note: `CRAFT_RUBRIC_UI_TASK_KEYS` (config line 2168) already exists as a frozenset of craft rubric UI keys, but it is the seven `CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY` keys and omits `craft_company_search_terms` — so it is **not** reusable as chain membership, and a plan step that reached for it would be subtly wrong by one hop. Flagging so nobody "simplifies" into it later.

### discuss — AC5 is never mapped, though its in-scope half is handled

Child AC5 (`ARTIFACTS_READY` on completion, content visible and editable under Artifacts nav) carries its own carve-out — "UI editability after chain — sibling #1 owns chain completion." The plan does the in-scope half in substance: Stage 1 step 4 deliberately does not clear artifacts, and Stage 3 step 3 keeps autosave/edit behavior intact. But no section states the split, so R5 reads it as unmapped on paper. **Recommendation:** one line in the Files Changed preamble or a Decision block — AC5 completion → AST-1252, AC5 editability → preserved here by not clearing and not touching the save paths.

### acceptable — the `…/generate/<task_key>/pending` recovery stays wired for chain keys

Stage 1 step 6 gates the POST, but `ArtifactEditor` also does an AST-901/905 page-return recovery `GET /api/candidates/<id>/generate/<taskKey>/pending` (lines 457–504), which the plan never mentions. I chased whether the dispatch chain would start feeding it: it will not — `/pending` is backed by an explicit stash (`_stash_pending_craft_generation` / `get_pending_craft_generation`), written only by the UI generate path and by failed saves, not by AST-1252's per-hop persist. So leaving it wired is right, and it keeps failed-save recovery working. The narrow residue is a stale pre-retirement stash surfacing "Recovered completed generation — review and Save or Cancel" on a chain page, which is the exact review chrome step 2 says to retire for chain keys. Not worth a stage, worth knowing.

### acceptable — `start_requested_artifacts` leans on `prior_states` instead of an explicit state check

`tracker.start_artifact_build` explicitly rejects non-`RECOMMENDED` before transitioning; your version lets `transition_candidate_state` enforce priors and surfaces the `ValueError` as 409. That is the more config-driven of the two and matches `astral.state.core-decides-transitions`. Noting only because the plan calls itself "modeled on" the job helper and this is a deliberate divergence — worth saying so.

## Notes

The spine of this plan is right, and the part I expected to be wrong isn't: the epic's hard prohibition is on hop **sequencing** in `config.py`, and you kept order in a live `run_next` walk with only an unordered map in config — AC8's constraint is respected, and I confirmed the walk you describe produces the hops AC3 requires you to name. One POST for both buttons, priors widened with existing vocabulary instead of new states, and Generate hidden while claimed are all sound calls.

What blocks is that the plan stops short of deciding how the frontend learns the hop list, and that gap is not cosmetic — it lands on a layer boundary. `build_state_ui_manifest()` is in `utils`, the hop order needs the database, and `astral.standards.utils-data-late-import-only` closes the door the plan would otherwise walk through. Deciding it in favour of the API layer costs one added file in the table and removes three conditionals from Stage 3.

Self-assessment: `Conf: high` is a little generous given a Stage 3 that branches on an undecided Stage 1 output; the rest of `high` is earned, since the job `start_artifact_build` template and existing Generate/Regenerate chrome really are as close as claimed. `Risk: Medium` is honest and named the right hazards.

context_tokens≈132000

— Joan

#### katherine — 2026-08-07T07:47:19.625Z
Plan published on `origin/sub/AST-1243/AST-1253-generate-regenerate-handoff` @ `e98d39d0`.

[docs/features/candidate/ast-1253-generate-regenerate-requested-artifacts-handoff.md](https://github.com/susansomerset/astral/blob/sub/AST-1243/AST-1253-generate-regenerate-handoff/docs/features/candidate/ast-1253-generate-regenerate-requested-artifacts-handoff.md)

**Self-assessment**
- **Scope:** Single-Component — UI handoff + thin `start_requested_artifacts` API/core helper + prior_states/manifest wiring; no dispatch rewrite (AST-1252).
- **Conf:** high — mirrors job `generate_artifacts` / `start_artifact_build`; Generate/Regenerate chrome already exists; AST-1252 owns the chain.
- **Risk:** Medium — wrong priors or generate-state list can block Regenerate or allow double-kick while claimed; retiring chain-key ad-hoc generate is intentional (Betty updates ArtifactEditor tests).

Load-bearing decisions: expand `REQUESTED_ARTIFACTS` priors for ARTIFACTS_READY/ACTIVE_SEARCH/PAUSE_SEARCH re-entry; one POST for Generate and Regenerate; warning hop order from live `run_next` walk; keep `craft_resume_base` ad-hoc.

---

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
