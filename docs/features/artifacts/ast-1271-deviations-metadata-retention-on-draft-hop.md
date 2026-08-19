<!-- linear-archive: AST-1271 archived 2026-08-19 -->

## Linear archive (AST-1271)

**Archived:** 2026-08-19  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1271/deviations-metadata-retention-on-draft-hop-draft-job-resume-response  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** susan  
**Priority / estimate:** None / —  
**Parent:** AST-1268 — draft_job_resume response schema is wrong  
**Blocked by / blocks / related:** parent: AST-1268

### Description

## What this implements

After #1: ensure successful draft responses retain `deviations` as hop/artifact metadata separate from resume body for the artifacts cycle (decision-drift visibility). Does not invent a full approve-artifacts UI (AST-1205).

## Acceptance criteria

- [X] Job resume render/persist uses only the resume body (`.resume` / equivalent); including `deviations` in that body path does not occur.
- [X] `deviations` is retained as metadata for the artifacts cycle (not dropped silently on a successful hop).

## Boundaries

Does not own nested contract / prompt / normalize (sibling #1). Does not own debug trail (sibling #3). Does not invent approve-artifacts UI (AST-1205).

## In scope

- [X] `astral.config.config-source-of-truth` — `deviations_artifact_key` on `TASK_CONFIG["draft_job_resume"]`; clear-key literal stays with that config source.
- [X] `astral.standards.in-scope-only` — persist sibling metadata only; no AST-1205 UI, no prompt/normalize, no debug trail.
- [X] `astral.standards.no-hardcoded-sets` — no new core frozenset of metadata names; skip keys via `payload_metadata_keys` / named artifact key from TASK_CONFIG.

## Considered but excluded

- [X] `astral.standards.debug-contract-gated` — Style D whitelist/unwrap trail is AST-1272 (`src/core` debug paths).
- [X] `astral.agent.do-task-delegation` — no new Anthropic call shape; only a post-success artifacts write on existing `draft_job_resume`.
- [X] `pattern.config.config-block` — nest/metadata keys already landed on AST-1270; this child adds only the artifact slot name.
- [X] Approve-artifacts / JAR deviations UI — AST-1205 (`src/ui`).
- [X] Nested unwrap / base_resume whitelist / Manage Tasks seed — AST-1270.

## Notes for planning

After AST-1270. Persist deviations as sibling metadata — never merge into resume section content.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1268-draft-job-resume-response-schema-is-wrong`, child `sub/AST-1268/<child-id>-<slug>`. Created at dispatch-parent.

### Comments

#### chuckles — 2026-08-08T01:23:02.649Z
[merge-child] blocked: git pull merge on sub — use: git fetch && git merge origin/ftr/<parent-segment>

`validate-sub-log` fails on `origin/sub/AST-1268/AST-1271-deviations-metadata-retention-on-draft-hop`: subjects `Merge remote-tracking branch 'origin/dev'…` / `Merge remote-tracking branch 'origin/ftr/…'` in the range ahead of `origin/ftr/AST-1268-draft-job-resume-response-schema-is-wrong` (likely from sync-child during resolve).

@Hedy Lamarr — republish a clean tip: rebuild `sub` stacked on current `origin/ftr/AST-1268-draft-job-resume-response-schema-is-wrong` with only AST-1271 plan→resolve commits (no `Merge remote-tracking branch` subjects in `sub --not ftr`). Force-with-lease push to `origin/sub/AST-1268/AST-1271-deviations-metadata-retention-on-draft-hop` is OK for this hygiene republish. Stay User Testing.

— Chuckles

#### radia — 2026-08-08T01:20:53.122Z
[code-rubric] revision=1
**Rubric:** code-rubric.v2
**Ticket:** AST-1271
**Overall:** CLEAN
**Diff:** `origin/dev...origin/sub/AST-1268/AST-1271-deviations-metadata-retention-on-draft-hop` @ `36ef32c8` (product tip `7ecf8cd5`)

## Frame diff

No frame changes from Joan's `plan-rubric.v1` verdict. Both `discuss` findings confirmed resolved in the built code:
1. `meta_key` ambiguity (Stage 2 step 1) — resolved to `deviations_artifact_key`-only lookup; no hardcoded literal in `tracker.py`.
2. `persist_job_artifact_from_parsed` `allow_resume` gate (Stage 2 step 5) — the deviations write landed unconditional, outside that gate, as Revision 1 required.

No new architectural surface beyond the plan's three files (`config.py`, `tracker.py`, `agent.py`).

## Summary

Full-set sweep: 68 active statutes (18 universal + 50 scoped) scored in-session; 17 scoped apply on touched layers (core + utils config), all conform. Zero violations, zero new findings. Pattern conformance: none cited. Plan adherence: Stages 1–3 landed in order, literal match on every instruction (config slot + clear-key, extract/save/persist helpers, `_resume_payload_body` meta skip, `do_task` success hook placement/gating/try-except style). Confirmed via `git log` that Hedy's `code()` commits touch only the three planned files — `candidate.py` in the diff is entirely AST-1270's inherited work via the `ftr` merge, not re-touched.

Full verdict appended to the plan doc: `docs/features/artifacts/ast-1271-deviations-metadata-retention-on-draft-hop.md`.

— Radia

#### betty — 2026-08-08T01:08:53.647Z
## QA test manifest — AST-1271

**Publish:** `origin/sub/AST-1268/AST-1271-deviations-metadata-retention-on-draft-hop` @ `7ecf8cd5`
**tests SHA:** `af4ec7da23f64da2d669c5664ca2da33f05a0a5d` (`merge-tests(AST-1271): origin/tests af4ec7da…`)

### Gaps (new)
1. `tests/component/core/test_tracker.py::TestAst1271DeviationsMetadataRetention` — extract/save/persist; string-typed deviations skipped from resume body; `persist_job_artifact_from_parsed` writes sibling slot; cancel clears `deviations`
2. `tests/component/utils/test_config.py::TestAst1271DeviationsArtifactConfig` — `deviations_artifact_key` + `JOB_BUILD_ARTIFACT_CLEAR_KEYS`
3. `tests/component/core/test_agent.py::TestAst1271DoTaskDeviationsPersist` — success calls persist helper; validation failure does not

### Existing (reuse)
4. `tests/component/core/test_tracker.py::TestAst1270NestedResumePayloadBody` — nested envelope still excludes deviations from body

### Broken / obsolete this pass
none — additive retention path; AST-1270 nest body prefer remains.

### Integration
None — no existing scenario for this hop; did not invent coverage.

### Run (test-child)
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_tracker.py::TestAst1271DeviationsMetadataRetention \
  tests/component/core/test_tracker.py::TestAst1270NestedResumePayloadBody \
  tests/component/utils/test_config.py::TestAst1271DeviationsArtifactConfig \
  tests/component/core/test_agent.py::TestAst1271DoTaskDeviationsPersist \
  -q
```

### Bible shasums on publish tip
- `docs/test-bible/core/tracker.md` `d30d12203ba24db228a87555592001e020bb9609`
- `docs/test-bible/utils/config.md` `ccb2d3293af71668c2b0cd68fa367ca710fffe5f`
- `docs/test-bible/core/agent.md` `a3e76ce76cc7c4819bde382bb46da512c43b71c0`

— Betty

#### hedy — 2026-08-08T01:01:59.357Z
[check-linear]
- Plan Rev 1: extract uses `TASK_CONFIG["draft_job_resume"]["deviations_artifact_key"]` only (no literal / tuple-membership ambiguity).
- `persist_job_artifact_from_parsed` deviations write ungated on `allow_resume`; documented as manual/API defense-in-depth — AC2 live path remains Stage 3 `do_task`.
- `origin/sub/AST-1268/AST-1271-deviations-metadata-retention-on-draft-hop` @ `7a8c5d40`

#### joan — 2026-08-08T01:00:13.139Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1271
**Overall:** APPROVED
**Publish ref tip:** `origin/sub/AST-1268/AST-1271-deviations-metadata-retention-on-draft-hop` @ `c9c838d7`

## Traceability

AC1→S2; AC2→S1–S3. No unmapped AC, no orphan stage.

**Considered:** 36 active statutes (18 universal + 18 scoped); 9 scoped excluded on layer/path predicates; 3 retired ignored. One `needs-discussion`, zero `violates`.

## Findings

**discuss** — Stage 2 step 1, the `meta_key` instruction (`orch.pipeline.plan-is-bible`). The bullet reads: "Read `meta_key = "deviations"` from membership in `TASK_CONFIG["draft_job_resume"]["payload_metadata_keys"]` — do **not** hardcode a second parallel set; look up the string that is already in that tuple (use the literal `"deviations"` only as the known metadata field name...)". That instructs the engineer both to look the name up and to use the literal, and there is no lookup that yields one element of a five-element tuple. The Execution contract says an ambiguous step means stop and comment, so as written this will stall the build for a question the plan can answer itself. Recommendation: read the field name from `deviations_artifact_key`, which Stage 1 already puts on the same config block — one source, no literal in `tracker.py`, and it satisfies the `no-hardcoded-sets` intent the bullet is reaching for.

**discuss** — Stage 2 step 5, `persist_job_artifact_from_parsed`. That function has no caller anywhere in `src/`; AST-1099 removed the `do_task` terminal body-copy, and `docs/test-bible/core/tracker.md` keeps it only "for manual/API callers". So the deviations write added there never fires in production, and AC2 rests entirely on the Stage 3 agent hook. Keeping the two paths in sync is defensible, but the Code rules check claims "agent and `persist_job_artifact_from_parsed` both call the wrapper" as DRY evidence, which reads as two live paths when there is one. Related: the step gates the deviations persist on `allow_resume`, a resume-content flag — a caller passing `allow_resume=False` would silently skip metadata that has nothing to do with resume bodies. Both are worth one clarifying line; neither changes the product outcome.

**acceptable** — the absent-vs-empty distinction in the extract helper is the right call and easy to get wrong. Key absent → `None` → no write, so a later hop cannot wipe a prior list; key present but empty → `[]` → written, so "the model reported no deviations" is recorded rather than indistinguishable from "never ran". That is what makes AC2's "not dropped silently" actually hold.

**acceptable** — adding a list-valued key to `job_data.artifacts` does not introduce a new class of reader risk: the dict is already heterogeneous (AST-1099 pins store bare id strings alongside `resume_content` / `cover_letter` dicts), and `resume_content` itself is untouched.

## Notes

I re-read the tree rather than trusting the plan's dependency claim, and AST-1270 has landed on `origin/ftr/AST-1268-...` @ `39913979`. Everything this plan builds on is real: `nested_resume_key` and `payload_metadata_keys` (including `deviations`) are on `TASK_CONFIG["draft_job_resume"]`, `_resume_payload_body` already prefers the nested resume dict, and `tracker.py` already imports `TASK_CONFIG`, so Stage 2 needs no new import. Stage 3's insertion point is equally concrete — the AST-1252 craft-persist block sitting right after the AST-1099 pin is the exact shape Stage 3 describes (success + truthy `index`, lazy import, try/except that logs without failing the hop), and `parsed` is in scope and post-validate there.

Stage 2 step 4 is worth a word because its value is not where it looks. With the nest present, `deviations` is already a sibling of the nest and excluded; on the flat post-normalize path it is a list and excluded by the string gate. What the skip actually catches is a string-typed `deviations`, plus `astral_job_id` / `company` / `title`, which are strings and do leak into the body dict today. That leak is currently harmless because `filter_content_to_resume_structure` drops them downstream and they are not section ids, so the match gates never saw them either — which is also why the change breaks nothing: `test_resume_payload_body_keeps_job_array`, `test_prefers_nested_resume_dict`, and `test_flat_unwrapped_payload_unchanged` all use inputs with no metadata keys.

On cancel: adding `"deviations"` to `JOB_BUILD_ARTIFACT_CLEAR_KEYS` is safe against the existing guard, and `test_clear_keys_include_pin_slots` asserts membership rather than an exact tuple, so it stays green. Merge note for `merge-child` — this child and AST-1270 both edit `_resume_payload_body`; the `blockedBy` on AST-1270 already declares the ordering.

R7 satisfied — slim comment gates the flip. Status → Plan Approved.

— Joan

context_tokens≈138000

#### hedy — 2026-08-08T00:56:14.903Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-1268/AST-1271-deviations-metadata-retention-on-draft-hop/docs/features/artifacts/ast-1271-deviations-metadata-retention-on-draft-hop.md

`origin/sub/AST-1268/AST-1271-deviations-metadata-retention-on-draft-hop` @ `c9c838d7`

**Scope:** Single-Component — config artifact slot + tracker extract/save + `_resume_payload_body` meta skip + `do_task` success hook; no UI.

**Conf:** high — AST-1270 already leaves `deviations` on the payload and out of resume body; this adds the durable `job_data.artifacts.deviations` write on successful draft.

**Risk:** Medium — writing into `resume_content` would poison render; failing the hop on metadata save would regress draft success (plan keeps resume body meta-aware and deviations persist best-effort).

---

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

## Resolution

**Date:** 2026-08-08  
**Review:** Radia `[code-rubric] revision=1` — **Overall: CLEAN** (`origin/.../AST-1271-...` @ `36ef32c8` / product tip `7ecf8cd5`).

No fix-now, discuss, or advisory items. Joan's plan-rubric discuss items were already closed in build (Revision 1 + Stages 1–3). Resolution is clean sign-off only — no product delta.

