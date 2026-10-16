# AST-2228 — Candidate stage registry and vocabulary

- **Linear:** [AST-2228](https://linear.app/astralcareermatch/issue/AST-2228)
- **Parent:** [AST-2225](https://linear.app/astralcareermatch/issue/AST-2225) — Revise candidate ui and candidate states
- **Publish ref:** `origin/sub/AST-2225/AST-2228-candidate-stage-registry`

Adds a coarse `stage` integer on every `CANDIDATE_STATES` entry, revives `PROFILE_READY` / `CONTEXT_READY` on the happy path, retires the four topic-ready(+stale) states, remaps live topic rows onto the revived path, and exposes a stage resolver — so later siblings can gate nav and scheduled advancement off registry stage without inventing a `candidate.stage` column.

## UAT fitness

- **AC restored:** Parent AC 1–4 (this child’s partition): (1) every `CANDIDATE_STATES` value has `stage`; (2) `PROFILE_READY` / `CONTEXT_READY` registered and topic-ready(+stale) keys absent; (3) locked bands — `PAUSE_SEARCH` stage 5, `RESUME_READY` stage 4, `PROFILE_READY` stage 2, `DELETED` stage 0; (4) no new required `candidate.stage` column.
- **Correct outcome:** Runtime vocabulary is stage-honest and topic-free: candidates on retired topic states land on `PROFILE_READY` / `CONTEXT_READY`; callers resolve stage from `state` via config; dispatch still claims real `trigger_state` strings.
- **Sibling check:** #2 (readiness/advance) and #3/#4 (nav/shell) consume `stage` from the registry / resolver — they do not redefine bands. Verified by leaving `NAV_CONFIG`, dispatcher tick, and shell files untouched here; stage resolver returns the locked integers those siblings will read.
- **Not sufficient:** Removing the stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Adding a `candidate.stage` DB column (or denormalizing stage onto the row) would violate `astral.entity.required-metadata` (stage is registry metadata on `state`, not entity-table metadata) and diverge from the shared entity column set. Symptom-only: leaving topic keys registered “for compatibility” fails AC 2 and blocks the revived happy path.

## Explicit scope gate

Ticket **## Scope** names only:

- `src/utils/config.py` — `CANDIDATE_STATES` stage + revive/retire + legacy map; **not** `NAV_CONFIG` regroup
- `src/core/candidate.py` — stage resolve + topic-state migration helpers only
- `docs/features/candidate/CANDIDATE_DATA_MODEL.md`

Every Files Changed row and every stage step below stays inside that list. No `NAV_CONFIG`, `dispatcher.py`, `api_system.py`, or frontend.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `stage` on every `CANDIDATE_STATES` entry; insert `PROFILE_READY` / `CONTEXT_READY`; delete four topic states; retarget priors; locked stage bands; `ERROR_*` stage = prior waiting stage; rewrite `CANDIDATE_LEGACY_STATE_MAP` / trigger frozenset; import-time asserts for stage + AC spot checks | utils |
| `src/core/candidate.py` | `candidate_stage()` resolver; `migrate_retired_topic_candidate_states()`; heal live topic rows from existing tick path; retarget `check_context_complete` off retired `ALL_TOPICS_READY` | core |
| `docs/features/candidate/CANDIDATE_DATA_MODEL.md` | Document stage bands, revived/retired states, legacy topic remap, no `candidate.stage` column | docs |

## Canon (this ticket)

Read in full (patterns / placement statutes named on the ticket):

- `astral.entity.required-metadata` → `canon/directives/active/stat.entity.required-metadata.md` — stage is **not** a new entity-table column; keep the shared metadata set unchanged.
- `astral.dispatch.entity-state-bound` → `canon/directives/active/stat.dispatch.entity-state-bound.md` — dispatch continues to claim real registry `trigger_state` values; never invent stage-integer triggers.

All other ids: id-only.

## Stage 1: Registry vocabulary + legacy map (`config.py`)

**Done when:** `CANDIDATE_STATES` imports cleanly; every entry has `stage`; topic keys are gone; `PROFILE_READY` / `CONTEXT_READY` exist with locked bands; legacy map remaps retired topic labels onto the revived path (not forever onto bare `NEW_CANDIDATE`); AC python one-liners 1–3 succeed.

1. In `src/utils/config.py`, rewrite the `CANDIDATE_STATES` block so the happy path is:

   ```
   NEW_CANDIDATE → INTAKE_INITIATED → PROFILE_READY → CONTEXT_READY
     → REQUESTED_RESUME → RESUME_READY → REQUESTED_ARTIFACTS → ARTIFACTS_READY
     → ACTIVE_SEARCH ↔ PAUSE_SEARCH
   ```

   Keep `PROSPECT`, `INACTIVE`, `DELETED`, stale companions for resume/artifacts waiting states, `retry_state` on `REQUESTED_RESUME` / `REQUESTED_ARTIFACTS`, and the existing `CANDIDATE_CRAFT_CHAIN_ERROR_STATES` expansion.

2. **Delete** these keys entirely from `CANDIDATE_STATES`:
   - `REQUIRED_TOPICS_READY`
   - `REQUIRED_TOPICS_READY_STALE`
   - `ALL_TOPICS_READY`
   - `ALL_TOPICS_READY_STALE`

3. **Insert** (no stale companions unless already present for other waiting states — do **not** invent profile/context stale pairs):

   | State | `prior_states` | `progress_rank` | `stage` |
   |-------|----------------|-----------------|--------|
   | `PROFILE_READY` | `["INTAKE_INITIATED"]` | `2` | `2` |
   | `CONTEXT_READY` | `["PROFILE_READY"]` | `3` | `3` |

4. Retarget priors that pointed at topic states:
   - `REQUESTED_RESUME["prior_states"]` → `["CONTEXT_READY"]` only (drop `ALL_TOPICS_READY` / `ALL_TOPICS_READY_STALE`).

5. Add `"stage": <int>` to **every** remaining entry using this locked map (parent Functional scope):

   | Stage | States |
   |------:|--------|
   | 0 | `DELETED`, `INACTIVE` |
   | 1 | `PROSPECT`, `NEW_CANDIDATE`, `INTAKE_INITIATED` |
   | 2 | `PROFILE_READY` |
   | 3 | `CONTEXT_READY`, `REQUESTED_RESUME` |
   | 4 | `RESUME_READY`, `RESUME_READY_STALE`, `REQUESTED_ARTIFACTS`, `ARTIFACTS_READY`, `ARTIFACTS_READY_STALE` |
   | 5 | `ACTIVE_SEARCH`, `PAUSE_SEARCH` |

   ⚠️ **Decision:** `CANDIDATE_CRAFT_CHAIN_ERROR_STATES` entries get `"stage": 4` (artifact-craft waiting band). There is no separate resume-request `ERROR_*` key in the registry today — `REQUESTED_RESUME` failures stay on the implicit `{base}_RETRY` path, which inherits stage **3** via `registered_base`. Do not invent new `ERROR_CRAFT_RESUME_*` keys in this ticket.

6. Keep existing `progress_rank` values for states that already had them, except:
   - `PROFILE_READY` → `2`, `CONTEXT_READY` → `3` (fill the ranks vacated by topic states).
   - Craft `ERROR_*` entries may keep their current `progress_rank` (still `6`) — only `stage` is authoritative for nav/advance siblings.

7. Rewrite `CANDIDATE_LEGACY_STATE_MAP` to:

   ```python
   CANDIDATE_LEGACY_STATE_MAP = {
       "LIVE_PROMPTS": "ACTIVE_SEARCH",
       "NEW": "NEW_CANDIDATE",
       "REQUIRED_TOPICS_READY": "PROFILE_READY",
       "REQUIRED_TOPICS_READY_STALE": "PROFILE_READY",
       "ALL_TOPICS_READY": "CONTEXT_READY",
       "ALL_TOPICS_READY_STALE": "CONTEXT_READY",
   }
   ```

   ⚠️ **Decision:** Drop `PROFILE_READY` / `CONTEXT_READY` → `NEW_CANDIDATE` remaps — those names are live registry keys again (`remap_legacy_candidate_state` returns early when `state in CANDIDATE_STATES`). Topic remaps land on the revived path, not bare `NEW_CANDIDATE`.

8. Rewrite `CANDIDATE_LEGACY_TRIGGER_STATES` to the retired labels only:

   ```python
   CANDIDATE_LEGACY_TRIGGER_STATES = frozenset({
       "LIVE_PROMPTS",
       "REQUIRED_TOPICS_READY",
       "REQUIRED_TOPICS_READY_STALE",
       "ALL_TOPICS_READY",
       "ALL_TOPICS_READY_STALE",
   })
   ```

9. Extend the existing import-time asserts after `CANDIDATE_STATES` / legacy map so that:
   - `assert all("stage" in v for v in CANDIDATE_STATES.values())`
   - `assert "PROFILE_READY" in CANDIDATE_STATES and "CONTEXT_READY" in CANDIDATE_STATES`
   - `assert not ({"REQUIRED_TOPICS_READY","REQUIRED_TOPICS_READY_STALE","ALL_TOPICS_READY","ALL_TOPICS_READY_STALE"} & set(CANDIDATE_STATES))`
   - `assert CANDIDATE_STATES["PAUSE_SEARCH"]["stage"] == 5`
   - `assert CANDIDATE_STATES["RESUME_READY"]["stage"] == 4`
   - `assert CANDIDATE_STATES["PROFILE_READY"]["stage"] == 2`
   - `assert CANDIDATE_STATES["DELETED"]["stage"] == 0`
   - Keep existing `progress_rank` / `prior_states` / stale / retry / `DELETED` reap asserts; keep `assert all(v in CANDIDATE_STATES for v in CANDIDATE_LEGACY_STATE_MAP.values())`.

10. Do **not** edit `NAV_CONFIG`, `CANDIDATE_STAGE_DISPATCH` trigger keys (still `REQUESTED_ARTIFACTS`), or any `TASK_CONFIG` rows in this stage.

## Stage 2: Stage resolver + topic-row migration (`candidate.py`)

**Done when:** `candidate_stage` returns the registry integer for any registered / retry state; live rows still holding retired topic labels are rewritten onto `PROFILE_READY` / `CONTEXT_READY` via the migration helper; `check_context_complete` no longer indexes deleted `ALL_TOPICS_READY`.

1. In `src/core/candidate.py`, near the transition / stale helpers (same public-then-helpers region as `transition_candidate_state` / `age_stale_candidate_states`), add:

   ```python
   def candidate_stage(state: str) -> int:
       """Registry stage for a candidate state (incl. implicit {base}_RETRY)."""
   ```

   Implementation rules:
   - Resolve via `registered_base(CANDIDATE_STATES, state)`.
   - If base is missing / unknown → raise `ValueError` with the bad state (do not default to `0` or `1`).
   - Return `int(CANDIDATE_STATES[base]["stage"])`.

2. Add:

   ```python
   def migrate_retired_topic_candidate_states() -> int:
       """Persist remap of live topic-ready(+stale) rows onto PROFILE_READY / CONTEXT_READY.
       Returns count of rows rewritten."""
   ```

   Implementation rules:
   - Iterate `list_candidates(include_deleted=False)`.
   - For each row whose `state` is in
     `{"REQUIRED_TOPICS_READY","REQUIRED_TOPICS_READY_STALE","ALL_TOPICS_READY","ALL_TOPICS_READY_STALE"}`,
     compute `to_state = remap_legacy_candidate_state(state)` (must be `PROFILE_READY` or `CONTEXT_READY`).
   - Persist with `transition_candidate_state(candidate_id, to_state, force=True)` so history appends and priors are not a blocker for retired→revived hops.
   - Skip rows already on a live registry key; return the rewrite count.
   - Import `remap_legacy_candidate_state` from `src.utils.config` with the existing config imports in this module (add to the import list if missing).

3. At the **start** of `age_stale_candidate_states` (before the stale loop), call `migrate_retired_topic_candidate_states()` and discard/ignore its count for the return value of `age_stale_candidate_states` (stale-move count stays stale-only).

   ⚠️ **Decision:** Hook migration into the existing stale tick entrypoint so live topic rows heal without touching `dispatcher.py` or `database.py` (both out of Scope). Operator CLI / ensure-path remaps stay AST-973’s concern; this helper covers in-process rows after vocabulary cutover.

4. In `check_context_complete`, replace the `ALL_TOPICS_READY` rank look-up with `CONTEXT_READY`:

   - Docstring: “Already-advanced candidates (`progress_rank` >= `CONTEXT_READY`) count as complete.”
   - `ready_rank = int(CANDIDATE_STATES["CONTEXT_READY"]["progress_rank"])`

   Do **not** add readiness/advance or incomplete-profile signal APIs here (sibling #2).

5. Do **not** add a `candidate.stage` column, alter `database.py`, or change transition legality beyond the forced migrate path above.

## Stage 3: Data-model doc

**Done when:** `CANDIDATE_DATA_MODEL.md` describes stage-on-state, the revived happy path, topic retirement + legacy remap targets, and explicitly states there is no `candidate.stage` column.

1. In `docs/features/candidate/CANDIDATE_DATA_MODEL.md`, under **State machine**:
   - Replace the topic-ready happy-path diagram with the revived path from Stage 1 step 1.
   - Add a **Stage bands** subsection listing the locked map from Stage 1 step 5 (including craft `ERROR_*` → stage 4; `{base}_RETRY` inherits base stage).
   - State clearly: stage lives on `CANDIDATE_STATES[state]["stage"]` only — **no** `candidate.stage` (or equivalent) table column; entity metadata columns remain the shared set (`state`, `state_history`, …).
   - Update the “No `PROSPECT`” / topic-ready wording so `PROSPECT` is documented as a live registry entry (stage 1) if the file still claims it is conceptual-only.
   - In **Legacy cutover**, keep AST-973 rows for `LIVE_PROMPTS` / `NEW`; remove or strike `PROFILE_READY` / `CONTEXT_READY` → `NEW_CANDIDATE`; add the four topic → revived remaps from Stage 1 step 7 (cite AST-2228).

2. Do not invent nav/UI or scheduled-advance behavior in this doc beyond naming that siblings consume stage from the registry.

## Estimate

Confirm Chuckles estimate: 5 — agree

## Execution contract

- Follow stages in order; one commit per stage on the epic worktree; push each to `origin/sub/AST-2225/AST-2228-candidate-stage-registry`.
- Do not add files outside **Files Changed**.
- On ambiguity or codebase drift → stop and comment on parent AST-2225 with the Stage N blocked template; do not improvise.

## Joan validate

[plan-rubric]
**Ticket:** AST-2228
**Overall:** APPROVED
**Corpus:** b7ab2203048ce0beb2869a12200ab7fa696c8066
**Publish ref tip:** `51e9b203f87a78b8a49a4a1152c8ebb0581bc562` (`origin/sub/AST-2225/AST-2228-candidate-stage-registry`)

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| astral.entity.required-metadata | A | | |
| astral.dispatch.entity-state-bound | A | | |

## Traceability

AC1 → Stage 1 (every `CANDIDATE_STATES` entry gets `stage` + import asserts). AC2 → Stage 1 (delete four topic keys; insert `PROFILE_READY` / `CONTEXT_READY`). AC3 → Stage 1 step 5 + asserts (`PAUSE_SEARCH` 5, `RESUME_READY` 4, `PROFILE_READY` 2, `DELETED` 0). AC4 → Stage 2 step 5 + Stage 3 (registry-only stage; no `candidate.stage` column). Parent AC 5–13 → N/A — nav/shell/advancement owned by siblings #2–#4 per child `## Scope`.

## Findings

### acceptable
- **Location:** Linear assignee at fetch
- **Finding:** Status `Plan Ready` but assignee was Ada Lovelace, not Joan (validate-plan §1 expects Joan during the pass).
- **Recommendation:** Chuckles should assign Joan before spawn when following the strict gate; this pass proceeded per spawn instruction with recommend-only stdout.

### discuss
- **Location:** Stage 2 step 3 — `migrate_retired_topic_candidate_states()` at start of `age_stale_candidate_states`
- **Finding:** Live rows still labeled with retired topic strings are healed on the existing dispatcher stale tick, not synchronously at import. Any code path that reads `CANDIDATE_STATES[state]` for such a row before the first tick could see empty config until migration runs (dispatcher already calls `age_stale_candidate_states()` today).
- **Recommendation:** Acceptable for this child’s boundaries (no `dispatcher.py` edits). Engineer should avoid assuming instant heal on deploy; optional one-line in Stage 2 “done when” noting first-tick heal is enough unless product wants a one-shot at import (out of scope).

### acceptable
- **Location:** `## UAT fitness` block
- **Finding:** UAT-thin-shaped section on a normal feature child — redundant but correctly cites AC 1–4, sibling partition, and rejects `candidate.stage` column / topic-key compatibility sham.
- **Recommendation:** No plan change required.

**R6 (summary):** Definition fidelity holds — plan matches child partition (registry + resolver + migration + data model only; explicit exclusion of `NAV_CONFIG`, dispatcher, API, shell). Scope gate aligns with ticket `## Scope`. No sibling scope creep. Self-assessment / estimate confirm is specific. DRY: reuses `registered_base`, `remap_legacy_candidate_state`, `transition_candidate_state`, existing stale entrypoint. Craft `ERROR_*` → stage 4 matches parent banding (artifact-craft chain only; resume failures stay on `{base}_RETRY` at stage 3 via `registered_base`).

context_tokens≈42000

## Review (build stub)

**Publish ref:** `origin/sub/AST-2225/AST-2228-candidate-stage-registry`
**Plan path:** `docs/features/candidate/ast-2228-candidate-stage-registry.md`

**Built tip:** `be91a4690615cbaafa6cb715a18466ce2f5a108d` (`be91a469`)

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `0bb939db` | `stage` on every state; revive PROFILE/CONTEXT; retire topic keys; legacy topic remap |
| 2 | `ff8e235f` | `candidate_stage` + `migrate_retired_topic_candidate_states`; CONTEXT_READY completeness gate |
| 3 | `be91a469` | `CANDIDATE_DATA_MODEL.md` stage bands + topic remap doc |

**Betty note:** Registry + core helpers + data-model doc only. No test-tree edits. AC1–AC3 covered by import-time asserts; AC4 = no `candidate.stage` column.

## Radia review

[code-rubric]
**Ticket:** AST-2228
**Publish ref:** `c488aeae7a1bdc74fca6275a62be3c10fe409497` (`origin/sub/AST-2225/AST-2228-candidate-stage-registry`)
**Corpus:** b7ab2203048ce0beb2869a12200ab7fa696c8066
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| astral.entity.required-metadata | A | | |
| astral.dispatch.entity-state-bound | A | | |

## Column diff vs plan stage

(aligned)

## Frame diff

(none)

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **Location:** `src/core/candidate.py` — `migrate_retired_topic_candidate_states()` at start of `age_stale_candidate_states`
- **Finding:** Live rows still persisted as retired topic labels heal on the first stale-aging tick, not at import/deploy. Until then, `candidate_stage("REQUIRED_TOPICS_READY")` correctly raises `ValueError` (tested); any caller that indexes `CANDIDATE_STATES[row["state"]]` without `remap_legacy_candidate_state` / migration can still break on those rows.
- **Note:** Matches plan Stage 2 step 3 and Joan’s plan-stage discuss (no `dispatcher.py` in scope). No product call needed unless Susan wants synchronous heal outside this child’s boundaries.

- **Location:** `docs/test-bible/**`, `tests/component/**` in diff
- **Finding:** Betty manifest + component revisions for AST-2228 (28-node narrowed run per `docs/test-bible/utils/config.md` § QA test manifest — AST-2228). Not sibling product carry; scoped to this ticket.

## Plan fidelity (non-canon)

Diff vs `docs/features/candidate/ast-2228-candidate-stage-registry.md`: **matches** Stages 1–3 — `CANDIDATE_STATES` stage bands, topic retirement, legacy map/trigger frozenset, import asserts, `candidate_stage` / `migrate_retired_topic_candidate_states` / `check_context_complete` → `CONTEXT_READY`, `CANDIDATE_DATA_MODEL.md` updates. No `NAV_CONFIG`, `dispatcher.py`, `database.py`, or `candidate.stage` column. Ticket `## Scope` respected.

## Estimate footprint (non-canon)

Confirm estimate **5**: footprint is registry + two core helpers + data-model doc + targeted component tests — consistent with a 5-point child, not scope creep.

## What's solid

- Locked AC bands enforced in code and duplicated at import (`config.py` asserts) and in `TestAst2228CandidateStageRegistry`.
- `CANDIDATE_STAGE_DISPATCH` still claims `REQUESTED_ARTIFACTS`; no stage-integer or retired-topic keys introduced as dispatch triggers.
- Migration uses `remap_legacy_candidate_state` + `transition_candidate_state(..., force=True)` with explicit tests for rewrite count and stale-tick ordering.

## Recommended actions (downstream — not for Radia)

- Chuckles: append this artifact to `docs/features/candidate/ast-2228-candidate-stage-registry.md`, `docs(AST-2228): Radia review — clean`, push, post slim upshot `--as radia`, move **Review Posted**; datt **§3h** → **PROCEED** path toward **User Testing** (no fix-now canon items).
- Optional for `resolve-child` / UT notes only: one line in issue doc that topic-labeled rows heal on first `age_stale_candidate_states` if operators care about the window (already in plan + data model).

context_tokens≈28000

## Bug: AST-2267 — Manage Candidates state dropdown

### As-is

`GET /api/candidates/states` returns every `CANDIDATE_STATES` key (`src/ui/api/api_candidate.py` `get_candidate_states`). Manage Candidates renders each string as both option value and label (`AdminManageCandidates.tsx` state `<select>`). The list includes `ERROR_*`, `INTAKE_INITIATED`, and `*_STALE`, with no stage prefix and no alphanumeric sort.

### To-be

The dropdown omits `ERROR_*`, `INTAKE_INITIATED`, and `*_STALE`. Each remaining item’s visible text is `{stage}:{STATE}` (example `5:ACTIVE_SEARCH`). The list is sorted alphanumeric by that label. The option **value** stays the raw registry key so save still posts `ACTIVE_SEARCH`, not the label. Those omitted names stay in `CANDIDATE_STATES`.

### Repro

Open Manage Candidates, edit any candidate, open **State (admin override)**. The options include `ERROR_SHAPE_THE_STORY` (and other `ERROR_*`), `INTAKE_INITIATED`, `RESUME_READY_STALE`, `ARTIFACTS_READY_STALE`, shown as bare names in registry insertion order.

### Root cause

`get_candidate_states` dumps `list(CANDIDATE_STATES.keys())` with no picker filter. The select prints that string; it never reads `stage`.

### Proposed change

1. In `src/ui/api/api_candidate.py`, replace the body of `get_candidate_states` so the JSON is a list of objects, not bare strings. Build it only from `CANDIDATE_STATES` (do not edit the registry):

   - Skip a key when `name.startswith("ERROR_")` or `name == "INTAKE_INITIATED"` or `name.endswith("_STALE")`.
   - For each kept key, `label = f"{int(cfg['stage'])}:{name}"`.
   - Sort by `label` ascending (plain string order).
   - Return `jsonify([{"state": name, "label": label}, ...])`.

   Example head: `{"state": "DELETED", "label": "0:DELETED"}`, `{"state": "INACTIVE", "label": "0:INACTIVE"}`, then stage 1 names, through `{"state": "ACTIVE_SEARCH", "label": "5:ACTIVE_SEARCH"}`. No `ERROR_*`, no `INTAKE_INITIATED`, no `RESUME_READY_STALE`, no `ARTIFACTS_READY_STALE`.

2. In `src/ui/frontend/src/pages/AdminManageCandidates.tsx`:

   - Change `validStates` state to `{ state: string; label: string }[]`.
   - On `/api/candidates/states`, keep the array only when every element is an object with string `state` and string `label`; otherwise set `[]`.
   - Render:

     ```tsx
     {validStates.map(s => (
       <option key={s.state} value={s.state}>{s.label}</option>
     ))}
     ```

   - If `editForm.state` is non-empty and not in `validStates`, render one extra `<option value={editForm.state}>{editForm.state}</option>` **before** the mapped options so a candidate already in an omitted state stays selected. Do not invent a stage prefix for that extra option.

3. Do not change `CANDIDATE_STATES`, transition rules, or any other caller. Do not edit `tests/`.

### Blast radius

`/api/candidates/states` is only consumed by `AdminManageCandidates.tsx` in product code. Component tests that stub or assert a **string** array (`tests/component/ui/api/test_api_candidate.py`, `tests/component/frontend/pages/test_AdminManageCandidates.test.tsx`) will not match the object list — Betty owns that tree.

### What must still hold

- Every `CANDIDATE_STATES` entry still has `stage`, including omitted picker names (`ERROR_*` stage 3 or 4, `INTAKE_INITIATED` stage 1, `*_STALE` stage 4).
- No `candidate.stage` column.
- Saving the select posts the raw state key. Dispatch and stale aging still use the registry keys, not the label.
