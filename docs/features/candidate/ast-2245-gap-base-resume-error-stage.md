# AST-2245 — Gap — BASE_RESUME_CHAIN_ERROR_STATES stage

- **Linear:** [AST-2245](https://linear.app/astralcareermatch/issue/AST-2245)
- **Parent:** [AST-2225](https://linear.app/astralcareermatch/issue/AST-2225) — Revise candidate ui and candidate states
- **Publish ref:** `origin/sub/AST-2225/AST-2245-gap-base-resume-error-stage`

After AST-2228 × AST-2221 merge, `BASE_RESUME_CHAIN_ERROR_STATES` entries in `CANDIDATE_STATES` still omit `"stage"`, so the import-time `assert "stage" in _cfg` fails on `ERROR_SHAPE_THE_STORY` (and siblings). This gap adds `"stage": 3` (resume-request error band per parent Functional scope) so every registry entry has `stage` again and siblings can build.

## Explicit scope gate

Ticket **## Scope** names only:

- `src/utils/config.py` — add `"stage": 3` (and matching shape) to the `BASE_RESUME_CHAIN_ERROR_STATES` dict expansion under `CANDIDATE_STATES` only; any other post-2228 ERROR keys missing `stage` in the same registry pass.

No `NAV_CONFIG`, readiness helpers, UI, or data-model doc.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `"stage": 3` to the `BASE_RESUME_CHAIN_ERROR_STATES` expansion; sweep any other `CANDIDATE_STATES` ERROR entries still missing `stage`; optional import-time assert that every `BASE_RESUME_CHAIN_ERROR_STATES` key has `stage == 3` | utils |

## Canon (this ticket)

Read in full (named on the ticket):

- `astral.entity.required-metadata` → `canon/directives/active/stat.entity.required-metadata.md` — stage stays registry metadata on `state`; no new entity-table column.
- `astral.dispatch.entity-state-bound` → `canon/directives/active/stat.dispatch.entity-state-bound.md` — do not invent stage-integer dispatch triggers; only fix registry `stage` fields.

All other ids: id-only.

## Stage 1: Base-resume ERROR stage = 3

**Done when:** `from src.utils.config import CANDIDATE_STATES` succeeds; every value has `stage`; every `BASE_RESUME_CHAIN_ERROR_STATES` key has `stage == 3`.

1. In `src/utils/config.py`, locate the `CANDIDATE_STATES` expansion (immediately after the `CANDIDATE_CRAFT_CHAIN_ERROR_STATES` block, ~AST-2221 comment):

   ```python
   **{
       s: {"prior_states": ["REQUESTED_RESUME"], "progress_rank": 4}
       for s in BASE_RESUME_CHAIN_ERROR_STATES
   },
   ```

   Change it to include stage 3 and keep the existing priors / progress_rank:

   ```python
   # AST-2221: base-resume hop failures land on ERROR_<HOP> with REQUESTED_RESUME priors only.
   # AST-2245: resume-request ERROR_* inherit stage 3 (parent locked band).
   **{
       s: {
           "prior_states": ["REQUESTED_RESUME"],
           "progress_rank": 4,
           "stage": 3,
       }
       for s in BASE_RESUME_CHAIN_ERROR_STATES
   },
   ```

   ⚠️ **Decision:** Stage **3** (not 4). Parent Functional scope: resume-request craft `ERROR_*` → stage of prior waiting state (`REQUESTED_RESUME` = 3). Artifact craft chain stays stage 4 (already set by AST-2228). Do not retarget craft-chain ERROR stages.

2. After the edit, run a one-shot check for any remaining registry keys lacking `stage` (same pass, still only `CANDIDATE_STATES` in this file):

   ```bash
   python3 -c "from src.utils.config import CANDIDATE_STATES; missing=[k for k,v in CANDIDATE_STATES.items() if 'stage' not in v]; assert not missing, missing"
   ```

   If any other ERROR (or non-ERROR) keys are still missing `stage`, add the locked-band integer for that key in the **same** `CANDIDATE_STATES` block (resume-request → 3, artifact-craft → 4, otherwise the locked map from AST-2228). Do **not** invent new states or change priors.

3. Immediately after the existing AST-2228 stage spot-check asserts (`PAUSE_SEARCH` / `RESUME_READY` / `PROFILE_READY` / `DELETED`), add:

   ```python
   assert all(
       CANDIDATE_STATES[s]["stage"] == 3 for s in BASE_RESUME_CHAIN_ERROR_STATES
   )
   ```

4. Confirm AC one-liners:

   ```bash
   python3 -c "from src.utils.config import CANDIDATE_STATES; assert all('stage' in v for v in CANDIDATE_STATES.values())"
   python3 -c "from src.utils.config import CANDIDATE_STATES, BASE_RESUME_CHAIN_ERROR_STATES; assert all(CANDIDATE_STATES[s]['stage']==3 for s in BASE_RESUME_CHAIN_ERROR_STATES)"
   ```

5. Do **not** edit `NAV_CONFIG`, `candidate.py`, dispatcher, UI, or `CANDIDATE_DATA_MODEL.md`.

## Estimate

Confirm Chuckles estimate: 1 — agree

## Execution contract

- One stage, one `code(AST-2245):` commit on the epic worktree; push to `origin/sub/AST-2225/AST-2245-gap-base-resume-error-stage`.
- Do not add files outside **Files Changed**.
- On ambiguity → stop and comment on parent AST-2225 with the Stage N blocked template.

## Joan validate

[plan-rubric]
**Ticket:** AST-2245
**Overall:** APPROVED
**Corpus:** b7ab2203048ce0beb2869a12200ab7fa696c8066
**Publish ref tip:** `f7d6d6fa03d4ff6755b47a1147a5b3998459fd50` (`origin/sub/AST-2225/AST-2245-gap-base-resume-error-stage`)

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| astral.entity.required-metadata | A | | |
| astral.dispatch.entity-state-bound | A | | |

## Traceability

AC1 → Stage 1 steps 1–2, 4 (every `CANDIDATE_STATES` value has `stage`; import succeeds). AC2 → Stage 1 steps 1, 3–4 (`BASE_RESUME_CHAIN_ERROR_STATES` keys all `stage == 3` + dedicated assert). Parent AC 1–4 / epic nav/readiness → N/A (vocabulary gap only; no NAV/readiness/UI). Sibling unblock → merge-child to ftr after land (ticket Notes; not scored as parent AC).

## Findings

### acceptable
- **Location:** Linear assignee at fetch
- **Finding:** Assignee Ada Lovelace (validate-plan §1 expects Joan during the pass).
- **Recommendation:** Chuckles handoff convention only; stdout recommendation stands.

### acceptable
- **Location:** Gap vs AST-2228 #1 slice
- **Finding:** Resume-chain `ERROR_*` from AST-2221 were omitted when AST-2228 added `stage` to craft `ERROR_*`; a dedicated gap child is the right partition vs reopening #1 scope.
- **Recommendation:** Land on `sub/AST-2245` then `merge-child` so #2/#3 import gates clear.

**R6 (summary):** Plan matches ticket Scope (`config.py` only). Publish tip confirms failure mode: `BASE_RESUME_CHAIN_ERROR_STATES` dict expansion lacks `"stage"` while the global `assert "stage" in _cfg` already runs (blocks import). Fix aligns with parent locked band (resume-request `ERROR_*` → stage **3**; craft `ERROR_*` stay **4**). No NAV, `candidate.py`, or dispatch edits. Estimate 1 — agree.

context_tokens≈86000

## Review (build stub)

**Publish ref:** `origin/sub/AST-2225/AST-2245-gap-base-resume-error-stage`
**Plan path:** `docs/features/candidate/ast-2245-gap-base-resume-error-stage.md`

**Built tip:** `88e10d497a7a8425174207b8e2e4b92d015a6449` (`88e10d497`)

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `88e10d497` | `BASE_RESUME_CHAIN_ERROR_STATES` entries get `stage: 3` + import assert |

**Betty note:** Config-only registry gap. No test-tree edits in build.
