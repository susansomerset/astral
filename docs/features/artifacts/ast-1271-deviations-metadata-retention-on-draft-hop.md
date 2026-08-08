# AST-1271 — Deviations metadata retention on draft hop

**Linear:** https://linear.app/astralcareermatch/issue/AST-1271/deviations-metadata-retention-on-draft-hop-draft-job-resume-response  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1268/draft-job-resume-response-schema-is-wrong  
**Publish ref:** `sub/AST-1268/AST-1271-deviations-metadata-retention-on-draft-hop`

After **AST-1270**, nested `agent_payload.resume` unwraps and `deviations` is allowlisted as sibling metadata — but a successful `draft_job_resume` hop still drops that list for the artifacts cycle: `_resume_payload_body` / `resume_content` never copy it (correct for render), and nothing writes it to durable job artifact metadata. This ticket persists `deviations` under `job_data.artifacts` as a sibling of `resume_content`, keeps resume body paths free of envelope metadata, and clears the slot on cancel-build with the other build artifacts. Does **not** own nested contract / prompt / normalize (**AST-1270**), debug whitelist trail (**AST-1272**), or approve-artifacts UI (**AST-1205**).

⚠️ **Decision:** Persist as `job_data.artifacts.deviations` (string list), not as an agent_data pin and not inside `resume_content`. Pinning the whole RESPONSE (AST-1099 style) would retain the envelope only opaquely; operators need first-class decision-drift notes for the artifacts cycle without inventing AST-1205 UI. Same key name as the payload metadata field so inspectable job_data matches the model contract.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `deviations_artifact_key` on `TASK_CONFIG["draft_job_resume"]`; include that key in `JOB_BUILD_ARTIFACT_CLEAR_KEYS` | utils |
| `src/core/tracker.py` | Extract + save deviations helpers; skip metadata keys in `_resume_payload_body`; persist beside resume in `persist_job_artifact_from_parsed` | core |
| `src/core/agent.py` | On successful `draft_job_resume`, persist deviations to job artifacts after RESPONSE store | core |

**Out of files (siblings / boundaries):**

| File / area | Owner |
|-------------|-------|
| Nested unwrap / base_resume whitelist / Manage Tasks seed | AST-1270 (done) |
| Style D debug whitelist / unwrap / accept-reject trail | AST-1272 |
| Approve-artifacts UI / JAR panels for deviations | AST-1205 (out) |
| HTML builders / cover-letter hops | out of epic |
| `tests/`, `docs/test-bible/**` | Betty |

## Stage 1: Config — artifact slot + clear-key

**Done when:** `TASK_CONFIG["draft_job_resume"]` names the job-artifact slot for deviations, and cancel-build’s clear tuple includes that same key. No behavior change until Stages 2–3 read them.

1. In `src/utils/config.py`, inside `TASK_CONFIG["draft_job_resume"]` (keep AST-1270 `nested_resume_key` / `payload_metadata_keys`), add:

   ```python
   "deviations_artifact_key": "deviations",
   ```

2. In `JOB_BUILD_ARTIFACT_CLEAR_KEYS`, add `"deviations"` (same literal as `deviations_artifact_key` / the `payload_metadata_keys` entry). Do **not** invent a parallel module frozenset for the key name.

3. Do **not** add BUILD_CONFIG `artifact_shapes` for deviations (not a resume/cover shape; list metadata only). Do **not** add UI/DATA_SHAPES entries (AST-1205).

## Stage 2: Tracker — extract, save, keep resume body clean

**Done when:** A parsed draft envelope with `deviations: ["…"]` (nested or already-unwrapped) yields a string list via the extract helper; `save_job_artifact_deviations` merges that list under `job_data.artifacts[deviations_artifact_key]`; `_resume_payload_body` never returns metadata keys (including `deviations`) even if a value is a string; `persist_job_artifact_from_parsed` still writes only section bodies to `resume_content` and also persists deviations when present on the same parsed object.

1. In `src/core/tracker.py`, next to the other job-artifact save helpers (`save_job_artifact_resume_content` / `save_job_artifact_cover_letter`), add:

   ```python
   def extract_draft_job_resume_deviations(parsed: Any) -> Optional[List[str]]:
       """Normalize deviations from nested or flat draft payload; None if key absent."""
   ```

   Implementation rules:
   - Resolve `body` the same way `_resume_payload_body` does (`agent_payload` dict or `parsed`).
   - If `body` is not a dict, return `None`.
   - Resolve the payload field name from config only:
     `meta_key = TASK_CONFIG["draft_job_resume"]["deviations_artifact_key"]`
     (Stage 1 sets this to the same string as the model’s sibling metadata field; do **not** hardcode `"deviations"` in `tracker.py`).
   - Prefer nested envelope when present: if `body.get(nest_key)` is a dict, read `body.get(meta_key)` from the **outer** `body` (sibling of nest), not from inside the nest.
   - If `meta_key not in body`: return `None` (caller must not wipe a prior value).
   - If present: coerce to `list[str]`:
     - `None` → `[]`
     - `str` → `[that string]` if non-empty after strip else `[]`
     - `list` → `[str(item) for item in list if str(item).strip()]` (drop blank strings)
     - any other type → `[str(value)]` if `str(value).strip()` else `[]`
   - Return the coerced list (including empty).

2. Add:

   ```python
   def save_job_artifact_deviations(astral_job_id: str, deviations: List[str]) -> None:
       """Merge deviations list into job_data.artifacts (AST-1271)."""
   ```

   - `key = TASK_CONFIG["draft_job_resume"]["deviations_artifact_key"]`
   - `save_job_data(astral_job_id, {"artifacts": {key: list(deviations)}})` — same merge pattern as `save_job_artifact_cover_letter`.
   - No-op / early return if `astral_job_id` is empty (match pin helper’s missing-id skip style without debug noise unless an existing helper already logs — prefer silent return).

3. Add a thin public wrapper used by agent + persist:

   ```python
   def persist_draft_job_resume_deviations(astral_job_id: str, parsed: Any) -> bool:
       """Extract deviations from parsed draft response and save when the key is present."""
   ```

   - Call `extract_draft_job_resume_deviations(parsed)`.
   - If return is `None`, return `False` (key absent — leave prior artifacts untouched).
   - Else call `save_job_artifact_deviations(astral_job_id, extracted)` and return `True`.

4. Update `_resume_payload_body(parsed)`:
   - After resolving `body` (and after preferring nested resume dict when present), build `out` as today **but skip**:
     - `nest_key`
     - every key in `TASK_CONFIG["draft_job_resume"]["payload_metadata_keys"]`
   - Keep existing string / experience-job-array inclusion rules for remaining keys.
   - This hardens the flat-unwrapped path so a string-typed `deviations` can never enter resume body.

5. Update `persist_job_artifact_from_parsed` (defense-in-depth for manual/API callers only — AST-1099 removed the live `do_task` terminal body-copy; **AC2’s production path is Stage 3**):
   - After the existing resume / cover branches (regardless of `allow_resume` / whether resume matched), call `persist_draft_job_resume_deviations(astral_job_id, parsed)`.
   - Do **not** gate this call on `allow_resume` (that flag is resume-body only; deviations are sibling metadata).
   - Do **not** put deviations into `filtered` / `save_job_artifact_resume_content`.
   - If deviations persist returns True, count that as `wrote = True` (same as cover/resume writes).

6. Do **not** change HTML builders, API PUT handlers, or pin maps in this stage.

## Stage 3: Agent — retain on successful draft hop

**Done when:** A successful `do_task("draft_job_resume", …)` with `deviations` on the validated payload writes `job_data.artifacts.deviations` for that job id; failed validation / failed hop does not write; missing `deviations` key leaves any prior value alone.

1. In `src/core/agent.py`, immediately after the AST-1099 pin block (`pin_job_artifact_agent_data_id` / skipped-pin debug), add an AST-1271 block:

   - Condition: `task_key == "draft_job_resume"` and `result.get("success")` and truthy `index`.
   - Lazy-import `persist_draft_job_resume_deviations` from `src.core.tracker` (same cycle-break style as the pin / craft-persist lazy imports).
   - Call `persist_draft_job_resume_deviations(index, parsed)` where `parsed` is the post-validate dict still in scope (envelope or payload — extract helper accepts both).
   - Do **not** require `resp_id` / `_should_store` (metadata retention is independent of agent_data pin; draft is not in `JOB_ARTIFACT_AGENT_DATA_PIN_BY_TASK`).
   - Do **not** add Style D debug lines here (AST-1272 owns debug trail).
   - On exception: log with existing `logger.debug` / `logger.error` pattern used by neighboring persist blocks; do **not** fail the hop solely because deviations save failed (resume chain must still succeed — log and continue). Prefer: try/except around the persist call, `logger.error("persist_draft_job_resume_deviations failed …")`, no ledger failure.

2. Do **not** add `draft_job_resume` to `JOB_ARTIFACT_AGENT_DATA_PIN_BY_TASK`.
3. Do **not** reintroduce terminal `persist_job_artifact_from_parsed` body-copy for draft (AST-1099 removed that for finalize; draft never owned it).

## Execution contract

The plan is binding. The agent:

- Executes steps in order within a stage, and stages in order.
- Does not skip, reorder, combine, or expand steps.
- Does not add files, modules, configs, or dependencies that aren't in the plan.
- When a step is ambiguous, contradicts another step, references something that doesn't exist, or fails when executed literally — **stops, comments on the Linear parent issue, and waits.**
- Completes each stage on the epic worktree, commits, publishes to `origin/sub/AST-1268/AST-1271-deviations-metadata-retention-on-draft-hop`, then continues.

## Self-Assessment

**Scope:** `Single-Component` — config slot + tracker artifact helpers (resume-body harden) + one `do_task` success hook; no UI.

**Conf:** `high` — AST-1270 already leaves `deviations` on the payload and keeps it out of `_resume_payload_body`; this ticket only adds the missing durable write path using the existing `save_job_data` artifacts merge pattern.

**Risk:** `Medium` — wrong slot / writing into `resume_content` would poison render; failing the hop on a metadata save error would regress draft success. Plan keeps resume body extraction meta-aware and treats deviations persist as best-effort on the hop.

## Code rules check

- §1.3 DRY: one extract + one save helper; Stage 3 `do_task` is the live caller; `persist_job_artifact_from_parsed` reuses the same wrapper for manual/API defense-in-depth only.
- §1.4 / §2.1 / `astral.config.config-source-of-truth`: artifact key on `TASK_CONFIG["draft_job_resume"]`; extract reads `deviations_artifact_key` (no literal field name in core); clear-keys tuple updated with the same literal as Stage 1.
- §1.5.1 / `astral.standards.debug-contract-gated`: no new Style D lines (AST-1272).
- `astral.standards.in-scope-only`: no AST-1205 UI, no prompt/normalize changes, no test-tree edits.
- §3.3 imports: agent → tracker via lazy import only (existing cycle-break pattern).
- Boundaries: siblings AST-1270 / AST-1272 untouched beyond reading their contracts.

## Revisions

Revision 1 — 2026-08-08  
Driven by: Joan `[plan-rubric] revision=1` discuss (APPROVED) — Stage 2 step 1 meta_key ambiguity; Stage 2 step 5 `allow_resume` gate / dual-path DRY claim.  
Changes: extract reads `deviations_artifact_key` only; `persist_job_artifact_from_parsed` deviations write is ungated on `allow_resume` and documented as non-production path; Code rules DRY line corrected.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1268/AST-1271-deviations-metadata-retention-on-draft-hop`
**Tip:** `a7d2d38e`

Stages landed: config artifact slot + clear-keys → tracker extract/save + resume-body meta skip → `do_task` success persist.

## Radia review — code-rubric.v2

**[code-rubric] revision=1**
**Rubric:** code-rubric.v2
**Ticket:** AST-1271
**Overall:** CLEAN
**Diff:** `origin/dev...origin/sub/AST-1268/AST-1271-deviations-metadata-retention-on-draft-hop` @ `7ecf8cd5`

### Full-set sweep

68 active statutes considered (18 universal + 50 scoped). 17 scoped statutes apply on the touched layers/paths (core: `agent.py`, `tracker.py`; utils: `config.py`) and all conform. 33 scoped excluded on layer/path predicate (batch, seed, ui, state, agent-grade, debug-contract-gated — no new debug lines, correctly deferred to AST-1272 per plan). Zero `violates`, zero new `discuss`.

Notable conformances:
- `astral.config.config-source-of-truth` — `deviations_artifact_key` lives once on `TASK_CONFIG["draft_job_resume"]`; `extract_draft_job_resume_deviations` reads only that key (no hardcoded `"deviations"` literal in `tracker.py`).
- `astral.standards.no-hardcoded-sets` — the `"deviations"` literal in `JOB_BUILD_ARTIFACT_CLEAR_KEYS` is the same config-module tuple pattern already used for `job_resume` / `cover_letter` / `application_responses`; no parallel core frozenset invented.
- `astral.idioms.coat-check-never-store-empty` — extract helper's absent→`None` (no write, prior value untouched) vs present-but-empty→`[]` (written, "model said none" recorded) distinction is exactly this idiom.
- `astral.standards.data-raises-caller-logs` — `save_job_data` raises on unknown job id; the Stage 3 `do_task` call wraps it in try/except + `logger.error`, matching the plan's explicit "best-effort, do not fail the hop" instruction.
- `astral.standards.no-cross-contamination` — `git log origin/dev..origin/sub/.../AST-1271` confirms Hedy's `code()` commits touch only `src/utils/config.py`, `src/core/tracker.py`, `src/core/agent.py`; `candidate.py` in the diff is entirely AST-1270's own inherited commits via the `ftr` merge, not re-touched here.
- `astral.git.engineer-test-tree-ban` — Hedy's `code()` commits (`749160d0`, `3aecabd4`, `199f09c5`) touch no `tests/` or `docs/test-bible/` paths.

### Pattern conformance

None cited in the plan's Self-Assessment; none found unintentionally matched.

### Plan adherence

Stages 1–3 landed in order, no scope expansion:
- Stage 1: `deviations_artifact_key` on `TASK_CONFIG["draft_job_resume"]` + `"deviations"` added to `JOB_BUILD_ARTIFACT_CLEAR_KEYS`, literal match.
- Stage 2: `extract_draft_job_resume_deviations` / `save_job_artifact_deviations` / `persist_draft_job_resume_deviations` added next to the sibling artifact-save helpers; `_resume_payload_body` now skips `nest_key` and every `payload_metadata_keys` entry, matching the plan's literal skip list; `persist_job_artifact_from_parsed`'s deviations call sits outside the `allow_resume` gate, ungated as Revision 1 requires.
- Stage 3: `do_task` hook placed immediately after the AST-1099 pin block, gated on `task_key == "draft_job_resume" and result.get("success") and index`, lazy-imports `persist_draft_job_resume_deviations`, try/except logs and continues without failing the hop — matches literally.

Both `discuss` findings from Joan's `plan-rubric.v1` (Revision 1) verified resolved in the built code:
1. `meta_key` ambiguity — resolved to `deviations_artifact_key`-only lookup, no literal in `tracker.py`.
2. `persist_job_artifact_from_parsed` `allow_resume` gate — the deviations write is unconditional, outside that gate, as landed.

### Findings

None. Zero fix-now, zero discuss, zero advisory.

### Frame diff

No frame changes from Joan's plan-rubric verdict — both discuss items were resolved in code exactly as recommended, no new architectural surface introduced beyond the plan's three files.

— Radia
