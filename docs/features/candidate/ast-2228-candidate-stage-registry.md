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
