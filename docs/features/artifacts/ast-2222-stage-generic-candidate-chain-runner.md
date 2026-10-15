# AST-2222 — Stage-generic candidate chain runner

**Linear:** [AST-2222](https://linear.app/astralcareermatch/issue/AST-2222)
**Parent:** [AST-1201](https://linear.app/astralcareermatch/issue/AST-1201) — We need a daisy chain to generate the base resume content
**Publish ref:** `sub/AST-1201/AST-2222-stage-generic-candidate-chain-runner`

Generalizes the candidate stage runner, claim expansion, and consult routing from `requested_artifacts`-only to any `CANDIDATE_STAGE_DISPATCH` stage. After sibling [AST-2221](https://linear.app/astralcareermatch/issue/AST-2221) (registry + seed), a `shape_the_story` dispatch row at `REQUESTED_RESUME` walks the nine-hop base-resume chain in one claim: intermediate hops persist only agent_data RESPONSE, `draft_resume_base` rotates `base_resume` / `resume_structure` via the existing `artifact_key` path, `draft_title_patterns` overwrites `contact.title_patterns`, success lands `RESUME_READY`, mid-chain reclaim resumes, and first/second failure follow retry → `ERROR_<HOP>`. `REQUESTED_ARTIFACTS` behaviour stays the same.

## UAT fitness

- **AC restored:** Parent AC sentences this change satisfies (from ticket Description / parent Acceptance criteria):
  > 6. **No chain-walk special-casing.** `rg -n "shape_the_story|draft_resume_experiences|draft_supporting_sections|draft_highlights|draft_core_competencies|draft_professional_summary|draft_keywords|BASE_RESUME_CHAIN" src/core/dispatcher.py src/core/consult.py` returns nothing. Fail: dispatcher/consult hardcode hop membership or order instead of resolving through stage config + `run_next`. (`draft_title_patterns` / `draft_resume_base` may appear only in the candidate persist gate, parallel to `craft_company_search_terms`.)
  > 7. **Stage-generic resolvers (runtime consumers).** `rg -n 'CANDIDATE_STAGE_DISPATCH\["requested_artifacts"\]' src/core/dispatcher.py src/core/consult.py` returns nothing. Fail: a hit.
  > 8. **End-to-end run.** A candidate in `REQUESTED_RESUME` with a current `candidate.artifacts.base_resume`: running the `shape_the_story` dispatch row once leaves the candidate in `RESUME_READY`. The current `base_resume` artifact row has a new `artifact_uuid` (the prior row is now `current=0`). agent_data holds one RESPONSE for each of the nine task_keys under that claim's batch. Fail: state stuck on `REQUESTED_RESUME.<hop>`, same `artifact_uuid` as before, or any hop missing a RESPONSE.
  > 9. **Keywords reach the meta tag.** After the run in AC 8, the current `base_resume` has a non-empty `candidate_tagline`, and the base resume HTML (`builder.build_base_resume`) contains `<meta name="description" content="Resume of … specializing in <that tagline>">`. Fail: empty tagline, or no meta description.
  > 10. **Title patterns land on contact.** After the run in AC 8, `candidate_data.contact.title_patterns` is a non-empty string matching the terminal hop's validated output (newline-separated if multiple). Fail: field unchanged, empty, or written under an artifact key.
  > 11. **Only the assembler writes artifacts.** Across the run in AC 8, the candidate's artifact rows grow by exactly the `base_resume` + `resume_structure` versions from `draft_resume_base`. No intermediate hop raises "unsupported craft task_key". Fail: extra artifact rows (including any title-patterns artifact), or the chain erroring on an intermediate persist.
  > 12. **Resume, don't restart.** A candidate left at `REQUESTED_RESUME.draft_highlights` and claimed again by the same row continues at `draft_core_competencies`. agent_data shows no new `shape_the_story` RESPONSE for that claim. Fail: the chain reruns from hop 1.
  > 13. **Retry then error.** A forced hop failure with the candidate on `REQUESTED_RESUME` lands it on `REQUESTED_RESUME_RETRY`; the same failure on retry lands it on that hop's `ERROR_<HOP>`. Fail: any other landing state.
  > 14. **Rubric chain unbroken.** The existing component tests for the requested-artifacts runner and candidate claim expansion pass unchanged (`pytest tests/component/core/test_candidate.py tests/component/core/test_dispatcher.py tests/component/core/test_consult.py`), and a `craft_get_rubric` @ `REQUESTED_ARTIFACTS` run still ends at `ARTIFACTS_READY`. Fail: any regression.
- **Correct outcome:** Operator puts a candidate in `REQUESTED_RESUME` and runs the `shape_the_story` dispatch row once; the candidate lands in `RESUME_READY` with a new current base resume (keywords in tagline / meta description), `contact.title_patterns` updated from the terminal hop, and mid-chain reclaim / retry→error matching the existing artifacts stage. Rubric chain at `REQUESTED_ARTIFACTS` still ends at `ARTIFACTS_READY`.
- **Sibling check:** [AST-2221](https://linear.app/astralcareermatch/issue/AST-2221) (User Testing) owns `BASE_RESUME_CHAIN_TASK_KEYS`, nine `TASK_CONFIG` hops + schemas, `requested_resume` stage entry (`trigger_state=REQUESTED_RESUME`, `pass_state=RESUME_READY`, entry `shape_the_story`), stage-generic config resolvers, and seed `run_next` links. This ticket does not touch `config.py` / `agent_task.json`. Build tip must include AST-2221 product (via `origin/ftr/AST-1201-base-resume-daisy-chain` or equivalent sync) before Stages execute — verify `CANDIDATE_STAGE_DISPATCH["requested_resume"]` and `TASK_CONFIG["shape_the_story"]` exist. Config resolvers already stage-generic after AST-2221; this ticket makes **runtime consumers** (dispatcher / consult / runner) match.
- **Not sufficient:** Removing the stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Special-casing only `REQUESTED_RESUME` / hardcoding the nine hop keys in `dispatcher.py` or `consult.py` (violates AC 6–7 and `patt.task.daisy-chain`). Also wrong: writing title patterns into the artifact table, or forcing intermediate hops through `save_candidate_data` artifact paths. Persist gate may name `draft_title_patterns` / `draft_resume_base` only (parallel to `craft_company_search_terms`); everything else resolves through stage config + live `run_next`.

## Explicit scope gate

This ticket's **Scope** names only:

* `src/core/candidate.py` — generalize stage runner / claim-state builder / chain walk; per-hop persist no-op for intermediate base-resume hops; `draft_title_patterns` → `contact.title_patterns`
* `src/core/dispatcher.py` — candidate claim expansion for mid-chain hop labels for every stage trigger
* `src/core/consult.py` — candidate dispatch branch routes any stage trigger (+ hop labels) to the generalized runner; persistable gate admits base-resume chain hops

No `src/utils/config.py`. No `data/admin/agent_task.json`. No UI for Generate. No title-patterns → artifact migration.

## Prerequisite (build tip, not a product stage)

Before Stage 1 product commits: epic worktree tip must include AST-2221 registry. Prefer re-running `sync-child.sh` so `origin/ftr/AST-1201-base-resume-daisy-chain` is merged (spawn's `--ftr AST-1201` short form did not match the published ftr slug and skipped). Confirm with:

```bash
python -c "from src.utils.config import CANDIDATE_STAGE_DISPATCH, TASK_CONFIG; assert 'requested_resume' in CANDIDATE_STAGE_DISPATCH; assert TASK_CONFIG['shape_the_story']['entity_type']=='candidate'"
```

If the assert fails, stop and comment on AST-2222 — do not invent config.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/candidate.py` | Stage-from-trigger resolve; generic chain walk + claim states; generalize `run_requested_artifacts_dispatch`; persist no-op / `draft_title_patterns` contact write | core |
| `src/core/dispatcher.py` | Mid-chain claim expansion for any `CANDIDATE_STAGE_DISPATCH` trigger | core |
| `src/core/consult.py` | Stage-trigger set + resume routing; persistable gate admits base-resume hops without naming intermediate keys | core |

## Canon Scope (plan-time)

**Patterns (read in full):** `patt.task.daisy-chain`, `patt.task.dispatch-retry`, `patt.entity.batch-processing`, `patt.artifact.write-operative`.

**Statutes (id-only until build):** `stat.batch.claim-process-release` (ticket citation; clerk roster also lists `astral.batch.claim-process-release` — same claim→process→release placement), `stat.logging.debug`, `stat.logging.error`.

Corpus `@` plan: `b7ab2203048ce0beb2869a12200ab7fa696c8066` (dirty=false).

## Stage 1: Stage-generic helpers + persist + runner (`candidate.py`)

**Done when:** From a tip that includes AST-2221, `requested_artifacts_dispatch_claim_states()` still returns bare `REQUESTED_ARTIFACTS` + retry + live craft hop labels; a parallel call for `REQUESTED_RESUME` returns bare + retry + nine `REQUESTED_RESUME.<hop>` labels from the live `run_next` walk; `_persist_craft_dispatch_success` no-ops intermediate base-resume hops, writes `contact.title_patterns` for `draft_title_patterns`, and still handles craft search-terms / rubric artifacts; `run_requested_artifacts_dispatch` resolves stage (pass/entry) from the bare trigger instead of hardcoding `["requested_artifacts"]`. Existing requested-artifacts unit behaviour unchanged.

**AC map (partial — full e2e in Stage 4):** AC 10 (title-patterns contact write), AC 11 (intermediate no-op / no "unsupported craft task_key"), AC 13 machinery (`_requested_stage_failure_target` still routes bare → retry → hop `error_state` for `REQUESTED_RESUME`).

1. In `src/core/candidate.py`, add a small stage lookup used by claim walk + runner (private helpers; names are planner picks — keep them next to the existing requested-artifacts block ~2622):

   * `_candidate_stage_for_trigger(bare_trigger: str) -> dict` — loop `CANDIDATE_STAGE_DISPATCH.values()`; return the entry whose `trigger_state == bare_trigger`. If none match, raise `ValueError` naming the trigger (caller decides how to surface).
   * `_walk_candidate_stage_chain_task_keys(stage: dict) -> list[str]` — same cycle-safe walk as `_walk_requested_artifacts_chain_task_keys`, but start from `stage["task_key"]` and follow `_current_agent_task_run_next`. Refactor `_walk_requested_artifacts_chain_task_keys` to call this with `CANDIDATE_STAGE_DISPATCH["requested_artifacts"]` (behaviour identical).

2. Generalize claim-state expansion:

   * Add `candidate_stage_dispatch_claim_states(trigger_state: str) -> List[str]` — parse hop label if needed to get bare trigger; `states = list(dispatch_claim_states(bare, "candidate"))`; append `dispatch_hop_label(bare, tk)` for each key from `_walk_candidate_stage_chain_task_keys(_candidate_stage_for_trigger(bare))`; de-dupe preserving order (same pattern as today's `requested_artifacts_dispatch_claim_states`).
   * Keep **`requested_artifacts_dispatch_claim_states()`** as a one-liner that calls `candidate_stage_dispatch_claim_states(CANDIDATE_STAGE_DISPATCH["requested_artifacts"]["trigger_state"])` so existing imports/tests keep working (AC 14).

3. In `_persist_craft_dispatch_success` (~4037):

   * Keep the `craft_company_search_terms` branch unchanged.
   * **Before** the `CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY` branch, add `draft_title_patterns`:
     * `parsed` must be a `dict`.
     * Read `parsed.get("title_patterns")`. If it is a `list`, coerce to a newline-joined string of stripped non-empty items; if it is a `str`, strip it; otherwise raise `ValueError` naming the type.
     * Empty after coerce → `ValueError`.
     * Persist with `save_candidate_data(candidate_id, {"contact": {"title_patterns": text}})` (dict library merge — same field Manage Candidates / intake already use). Do **not** call `save_candidate_data` with an artifact-key string for this hop.
     * `return`.
   * Keep the existing rubric `artifact_key` branch unchanged.
   * Replace the final `raise ValueError(f"unsupported craft task_key…")` with: if `TASK_CONFIG.get(task_key)` has `entity_type == "candidate"` and no truthy `artifact_key`, **`return`** (agent_data RESPONSE already landed — intermediate base-resume hops). Otherwise keep the raise for truly unsupported keys.

   ⚠️ **Decision:** No-op is keyed off `TASK_CONFIG` entity + missing `artifact_key`, not an imported `BASE_RESUME_CHAIN_TASK_KEYS` membership list — keeps persist stage-generic when future stages add non-artifact hops, and avoids pulling chain tuples into the persist path. `draft_title_patterns` stays an explicit named branch (ticket + AC 6 allow it in the persist gate only).

4. In `run_requested_artifacts_dispatch` (~4079): **do not rename** the function (tests monkeypatch this symbol).

   * After resolving `bare_trigger` from `trigger_state` / hop label (existing logic), replace `stage = CANDIDATE_STAGE_DISPATCH["requested_artifacts"]` with `stage = _candidate_stage_for_trigger(bare_trigger)`.
   * `pass_state = stage["pass_state"]`; default `start_key` still `(task_key or "").strip() or (stage.get("task_key") or "").strip()`.
   * Keep `persist_candidate_craft_hops=True`, empty-token → hop `error_state`, success → `transition_candidate_state(..., pass_state)` when `bare_trigger == stage["trigger_state"]` and not `skip_daisy_chain`, and the existing failure / hop-label held / `_requested_stage_failure_target` paths.
   * Logging strings may keep `run_requested_artifacts_dispatch` in the message (stable for existing log asserts).

5. Do **not** edit `agent.py`. `draft_resume_base` already takes the `TASK_CONFIG["artifact_key"]` branch in `do_task` (`save_candidate_data` for `resume_structure` + `base_resume`) before `_persist_craft_dispatch_success` — that path stays the sole assembler write (AC 11 / `patt.artifact.write-operative`).

6. **Stage 1 verify (exit 0)** — persist unit checks only (no full chain); do not edit `tests/`:

```bash
python - <<'PY'
from src.core import candidate as c
from src.utils.config import CANDIDATE_STAGE_DISPATCH, dispatch_hop_label
# Claim labels for both stages
ra = c.requested_artifacts_dispatch_claim_states()
assert CANDIDATE_STAGE_DISPATCH["requested_artifacts"]["trigger_state"] in ra
rr = c.candidate_stage_dispatch_claim_states("REQUESTED_RESUME")
assert "REQUESTED_RESUME" in rr and "REQUESTED_RESUME_RETRY" in rr
assert dispatch_hop_label("REQUESTED_RESUME", "draft_highlights") in rr
# AC10 / AC11 persist shape (monkeypatch save; no DB required if patched)
calls = []
c.save_candidate_data = lambda cid, data, *a, **k: calls.append((cid, data)) or None
c._persist_craft_dispatch_success("c1", "draft_title_patterns", {"title_patterns": "Eng.*\nSr Eng"})
assert calls and calls[0][1] == {"contact": {"title_patterns": "Eng.*\nSr Eng"}}
calls.clear()
c._persist_craft_dispatch_success("c1", "shape_the_story", {"story": "x"})  # no-op, no raise
assert calls == []
print("stage1 verify ok")
PY
```

## Stage 2: Dispatcher claim expansion (`dispatcher.py`)

**Done when:** `rg -n 'CANDIDATE_STAGE_DISPATCH\["requested_artifacts"\]' src/core/dispatcher.py` is empty; a candidate claim whose `input_state` bare trigger is any stage trigger (including `REQUESTED_RESUME` and `REQUESTED_ARTIFACTS`, bare or `.<hop>`) uses `candidate_stage_dispatch_claim_states` for that bare trigger; non-stage candidate triggers still use plain `dispatch_claim_states`.

**AC map:** AC 7 (dispatcher half of stage-generic consumers).

1. In `src/core/dispatcher.py` candidate claim block (~710–719):

   * Remove the hardcode `stage = CANDIDATE_STAGE_DISPATCH["requested_artifacts"]` and the equality check against that one `stage_trigger`.
   * Build `stage_triggers = {e["trigger_state"] for e in CANDIDATE_STAGE_DISPATCH.values()}`.
   * Let `bare = parsed_in[0] if parsed_in else raw_in`.
   * If `bare in stage_triggers`, set `claim_states = candidate_stage_dispatch_claim_states(bare)` (import from `src.core.candidate` — prefer the new generic name; do not import `requested_artifacts_dispatch_claim_states` here).
   * Leave the rest of `get_new_candidate_batch(...)` wiring unchanged.

⚠️ **Decision:** Expansion is trigger-set membership, not a walked hop-name list in the dispatcher — satisfies AC 6 and `patt.task.daisy-chain` §4 (reclaim via hop labels + parent `run_next`, not a membership frozenset in dispatcher).

## Stage 3: Consult routing + persistable gate (`consult.py`)

**Done when:** `rg -n 'CANDIDATE_STAGE_DISPATCH\["requested_artifacts"\]' src/core/consult.py` is empty; the AC 6 hop-name `rg` over `dispatcher.py` + `consult.py` is empty except allowed persist-gate names; a `REQUESTED_RESUME` / `REQUESTED_RESUME.<hop>` row with a matching stage chain task_key calls `run_requested_artifacts_dispatch`; `REQUESTED_ARTIFACTS` routing unchanged; skip-daisy persistable admits base-resume hops including `draft_title_patterns`.

**AC map:** AC 6 (hop-name ban), AC 7 (consult half of stage-generic consumers). AC 14 pytest is Stage 4.

1. In `src/core/consult.py` candidate branch (~2682–2731):

   * Replace `stage_tr = CANDIDATE_STAGE_DISPATCH["requested_artifacts"]["trigger_state"]` with membership: `stage_triggers = {e["trigger_state"] for e in CANDIDATE_STAGE_DISPATCH.values()}` and `registry_tr in stage_triggers` (keep using `parse_dispatch_hop_label` for `registry_tr`).
   * Keep `dispatch_chain_row_matches_job(row_tr, tk, cand_st)` as the resume predicate (same helper as job BUILD_ARTIFACTS — do **not** add a hop membership list).
   * Expand `persistable` for the `skip_daisy and persistable` arm:
     * Keep existing `CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY` / `craft_company_search_terms` / `craft_resume_base`.
     * Admit `draft_title_patterns` and `draft_resume_base` by name (AC 6 allowlist for the persist gate).
     * Admit other stage-chain hops **without naming them** by calling a new helper on candidate, e.g. `is_candidate_stage_chain_task(tk) -> bool`: true when `tk` appears in `_walk_candidate_stage_chain_task_keys(stage)` for **any** stage in `CANDIDATE_STAGE_DISPATCH`. Implement that helper in Stage 1's candidate.py block if not already added; consult only imports and calls it.
   * Still call `run_requested_artifacts_dispatch(...)` with the same kwargs (`task_key`, `trigger_state=input_state`, `skip_daisy_chain`).

2. Verify locally before commit (exit 0) — product tree only; do not edit tests:

```bash
rg -n 'CANDIDATE_STAGE_DISPATCH\["requested_artifacts"\]' src/core/dispatcher.py src/core/consult.py
# expect: no matches  (AC 7)

rg -n "shape_the_story|draft_resume_experiences|draft_supporting_sections|draft_highlights|draft_core_competencies|draft_professional_summary|draft_keywords|BASE_RESUME_CHAIN" src/core/dispatcher.py src/core/consult.py
# expect: no matches  (AC 6; draft_title_patterns / draft_resume_base may appear only in consult persistable / candidate persist)
```

## Stage 4: Acceptance verify (AC 8–14) — no product edits

**Done when:** Every check below exits 0 / asserts pass on the publish-ref tip after Stages 1–3. No new rows in **Files Changed**. No commit unless a prior stage must be fixed (then fix in that stage's file and re-verify). Precondition: Prerequisite assert (AST-2221 registry + live `agent_task` `run_next` for the nine hops) already green.

**AC map:** AC 8–13 (runtime behaviour) + AC 14 (rubric regression pytest).

Mirror the existing mocked `run_requested_artifacts_dispatch` patterns in `tests/component/core/test_candidate.py` (AST-1252 / AST-1388 / retry cases ~2122–2291) — engineer runs these as a **local smoke** (REPL / `python -` / `debug/spikes/` only; **do not** land new pytest under `tests/`). Betty owns any new committed coverage via qa-child.

1. **AC 8 — End-to-end run.** Candidate at `REQUESTED_RESUME` with a current `candidate.artifacts.base_resume` pin. Monkeypatch `do_task` so each of the nine chain hops returns `success` with a schema-valid `parsed_response` (assembler hop includes non-empty `candidate_tagline` + full craft-resume-base shape; title-patterns hop returns `{"title_patterns": "..."}`). Call `await run_requested_artifacts_dispatch(cid, task_key="shape_the_story", trigger_state="REQUESTED_RESUME")`.
   * **Pass:** candidate state `RESUME_READY`; current `base_resume` `artifact_uuid` ≠ prior uuid (prior `current=0`); agent_data has one RESPONSE per hop task_key under that claim's batch.
   * **Fail:** stuck on `REQUESTED_RESUME.<hop>`, same uuid, or missing RESPONSE.

2. **AC 9 — Keywords → meta.** Using the candidate from AC 8: current `base_resume` body has non-empty `candidate_tagline`; `builder.build_base_resume(...)` HTML contains `<meta name="description" content="Resume of … specializing in <that tagline>">`.
   * **Fail:** empty tagline or missing meta description.

3. **AC 10 — Title patterns on contact.** After AC 8: `candidate_data.contact.title_patterns` is non-empty and equals the terminal hop's validated string (newline-separated if list was coerced). No artifact row typed as title-patterns.
   * **Fail:** field unchanged/empty, or written under an artifact key.

4. **AC 11 — Assembler-only artifacts.** Across AC 8, count of new current artifact versions for this candidate grows by exactly `base_resume` + `resume_structure` from `draft_resume_base`. Intermediate hops did not raise `unsupported craft task_key`.
   * **Fail:** extra artifact rows or intermediate persist error.

5. **AC 12 — Resume, don't restart.** Set candidate state to `REQUESTED_RESUME.draft_highlights` (via `dispatch_hop_label`). Claim/run again with the same `shape_the_story` row (`task_key` from hop resume / `dispatch_chain_row_matches_job` path — start at the hop consult would resume). Assert next hop executed is `draft_core_competencies` and agent_data for that claim has **no** new `shape_the_story` RESPONSE.
   * **Fail:** chain restarts at hop 1.

6. **AC 13 — Retry then error.** With candidate on bare `REQUESTED_RESUME`, force `do_task` failure once → state `REQUESTED_RESUME_RETRY`. Force the same failure again from retry → state equals that hop's `TASK_CONFIG[task_key]["error_state"]` (`ERROR_<HOP>`).
   * **Fail:** any other landing state. (Same shape as existing REQUESTED_ARTIFACTS tests `test_*_retry` / error at ~2160–2182.)

7. **AC 14 — Rubric chain unbroken.** Run (exit 0):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py \
  tests/component/core/test_dispatcher.py \
  tests/component/core/test_consult.py \
  -q
```

Pass criterion: pytest green. Additionally confirm (same suite or a one-line follow-up) that a `craft_get_rubric` @ `REQUESTED_ARTIFACTS` path still transitions to `ARTIFACTS_READY` — covered by existing `TestRequestedArtifactsDispatch` cases in `test_candidate.py` when the suite is green.

## Execution contract

- Stages 1–3 in order; one product commit per stage on the epic worktree; publish each to `origin/sub/AST-1201/AST-2222-stage-generic-candidate-chain-runner`.
- Stage 4 is verify-only (no Files Changed). Do not add files outside **Files Changed**. Do not touch `tests/` / bible (Betty).
- If AST-2221 registry is missing on the tip, or a step contradicts the live signatures, stop and comment on the **parent** with the Stage blocked template — do not improvise config.
- Do not publish Code Complete until Stage 4 AC 8–14 checks pass.

## Estimate

Confirm Chuckles estimate: 5 — agree

## Revisions

### Revision 1 — 2026-10-15

Driven by: Joan `[plan-discuss] round=1 concern` / `[plan-rubric] REVIEW … map AC8–14 verify steps` (fix-now: map AC 8–13 into stage Done-when/verify; name pytest for AC 14).

Changes:

* Added **AC map** lines on Stages 1–3 Done-when (partial vs full e2e).
* Stage 1 §6 persist/claim unit verify script (AC 10/11 slice).
* New **Stage 4: Acceptance verify (AC 8–14)** with explicit pass/fail for AC 8–13 (mocked chain smoke mirroring existing REQUESTED_ARTIFACTS tests) and the AC 14 `run_component_tests.sh` pytest invocation.
* Execution contract: Stage 4 verify-only; no Code Complete until AC 8–14 green.

## Joan validate

[plan-discuss] round=1 concern
[plan-rubric]
**Ticket:** AST-2222
**Overall:** REVISE
**Corpus:** b7ab2203048ce0beb2869a12200ab7fa696c8066
**Publish ref:** `sub/AST-1201/AST-2222-stage-generic-candidate-chain-runner` @ `90422686034224f64db270d2f043685c3f737fb5`

### Canon scores

patt.task.daisy-chain | A | | |
patt.task.dispatch-retry | A | | |
patt.entity.batch-processing | A | | |
patt.artifact.write-operative | A | | |
stat.batch.claim-process-release | A | | |
stat.logging.debug | A | | |
stat.logging.error | A | | |

### Traceability

AC6→Stage 3 §2 `rg` (hop-name ban); AC7→Stage 2–3 §2 `rg` (hardcoded stage); AC8–AC13→**unmapped** in stage Done-when / verify (only quoted in `## UAT fitness`); AC14→implied by narrative + “existing tests” but **no** named `pytest` step in any stage verify block

### Findings

#### fix-now

- **Location:** Stages 1–3 Done-when / Stage 3 verify
- **Finding:** Child AC 8–13 (end-to-end `REQUESTED_RESUME` run, tagline/meta, `contact.title_patterns`, assembler-only artifact growth, mid-chain resume, retry→`ERROR_<HOP>`) have no implementation verification steps—only AC 6–7 `rg` gates. `## UAT fitness` restates parent AC but does not assign them to a stage, fixture, or manual repro the engineer runs before publish.
- **Recommendation:** Add a Stage 4 (or extend Stage 3 verify) with explicit pass/fail checks for AC 8–13—e.g. documented manual repro on a seeded candidate, or pointers to existing component/integration fixtures if Betty already owns them—and name the precondition (AST-2221 registry on tip + live `agent_task` `run_next`).

#### fix-now

- **Location:** Stage 3 verify / Execution contract
- **Finding:** AC 14 requires `pytest tests/component/core/test_candidate.py tests/component/core/test_dispatcher.py tests/component/core/test_consult.py` plus rubric regression; the plan forbids editing tests but never lists running that command in a Done-when block.
- **Recommendation:** Add a final verify bullet (exit 0) for that `pytest` invocation so R5 covers AC 14 and engineers do not rely on implicit habit.

#### discuss

- **Location:** Linear Citations vs clerk ids
- **Finding:** Frozen list cites `stat.batch.claim-process-release`; corpus id is `astral.batch.claim-process-release` (`canon_clerk expand` fails on the cited slug). Plan acknowledges the pairing; scored against claim-process-release placement on the existing pool-claim path.
- **Recommendation:** Archie may normalize the frozen slug; not a product blocker once verify gaps are fixed.

#### discuss

- **Location:** Prerequisite (build tip)
- **Finding:** Runtime work depends on AST-2221 registry/seed on the epic tip; plan documents assert-and-stop—good—but notes a prior `sync-child` / ftr slug mismatch risk.
- **Recommendation:** Chuckles/engineer confirm ftr merge before Stage 1; comment on ticket if assert fails (plan already says stop).

#### acceptable

- **Location:** Explicit scope gate / Files Changed
- **Finding:** Plan limits edits to `candidate.py`, `dispatcher.py`, `consult.py`; defers config/seed to AST-2221; persist gate names `draft_title_patterns` / `draft_resume_base` only where AC 6 allows; chain walk uses `CANDIDATE_STAGE_DISPATCH` + `run_next` (no `BASE_RESUME_CHAIN` / hop frozensets in dispatcher/consult).
- **Recommendation:** None after verify additions.

#### acceptable

- **Location:** Procedure §1 — assignee
- **Finding:** Assignee is Hedy Lamarr, not Joan; spawn requested this pass.
- **Recommendation:** Chuckles restores implementer after posting.

### R6 checklist (summary)

- Definition fidelity: matches child Scope and parent runtime slice; no config/seed/UI creep.
- DRY / scope: refactors chain walk through `_walk_candidate_stage_chain_task_keys`; stage-trigger set pattern in dispatcher/consult.
- Self-assessment: Estimate `5 — agree` matches three core files + prerequisite gate.
- Plan Discuss: zero completed rounds; entering round 1 with this REVISE.

context_tokens≈42000

## Joan validate (round 2 — APPROVED)

[plan-rubric]
**Ticket:** AST-2222
**Overall:** APPROVED
**Corpus:** b7ab2203048ce0beb2869a12200ab7fa696c8066
**Publish ref:** `sub/AST-1201/AST-2222-stage-generic-candidate-chain-runner` @ `20fec2fbba55e0914d924a4801d7d11065b5fd95`

### Canon scores

patt.task.daisy-chain | A | | |
patt.task.dispatch-retry | A | | |
patt.entity.batch-processing | A | | |
patt.artifact.write-operative | A | | |
stat.batch.claim-process-release | A | | |
stat.logging.debug | A | | |
stat.logging.error | A | | |

### Traceability

AC6→Stage 3 §2 `rg`; AC7→Stage 2–3 `rg`; AC8–AC13→Stage 4 §1–6 (mocked chain smoke); AC10/AC11 slice→Stage 1 §6 persist script; AC13 machinery→Stage 1 Done-when AC map + Stage 4 §6; AC14→Stage 4 §7 `run_component_tests.sh`

### Findings

#### discuss

- **Location:** Linear Citations vs clerk ids
- **Finding:** Frozen list cites `stat.batch.claim-process-release`; corpus id is `astral.batch.claim-process-release`. Plan documents the pairing; no claim/release redesign proposed.
- **Recommendation:** Archie may normalize slug; not blocking.

#### discuss

- **Location:** Prerequisite / sibling merge
- **Finding:** Stage 4 and Stages 1–3 assume AST-2221 registry + live `run_next` on the epic tip; plan documents assert-and-stop and ftr sync caveat.
- **Recommendation:** Confirm prerequisite before Stage 1 product commits (plan already gates).

#### acceptable

- **Location:** Revision 1 / Stage 4
- **Finding:** Prior fix-now (AC 8–13 unmapped, AC 14 pytest unnamed) addressed: Stage 4 pass/fail for AC 8–13, Stage 1 §6 unit verify, AC-map lines on Stages 1–3, execution contract “no Code Complete until AC 8–14 green.”
- **Recommendation:** None.

#### acceptable

- **Location:** Explicit scope gate
- **Finding:** Three core files only; stage-generic chain via `CANDIDATE_STAGE_DISPATCH` + `run_next`; AC 6 hop-name ban satisfied by design; `draft_title_patterns` / `draft_resume_base` only in persist gates where allowed.
- **Recommendation:** None.

#### acceptable

- **Location:** Plan Discuss
- **Finding:** One completed round (`round=1` concern in issue doc + Hedy `round=1` reply @ tip `20fec2fb`); assignee Joan for this pass.
- **Recommendation:** Chuckles restores implementer on approve.

### R6 checklist (summary)

- Definition fidelity: runtime slice matches child Scope; config/seed/UI out of scope.
- DRY / scope: shared `_walk_candidate_stage_chain_task_keys`; no dispatcher hop frozensets.
- Self-assessment: Estimate `5 — agree` matches Stages 1–3 product + Stage 4 verify-only.
- Stage 4 local smoke (no new `tests/` commits) is explicit and aligned with Betty ownership.

context_tokens≈52000

## Review (build stub)

**Publish ref:** `origin/sub/AST-1201/AST-2222-stage-generic-candidate-chain-runner`

| Stage | Commit | Summary |
|-------|--------|---------|
| plan | `904226860` | Plan doc |
| Joan r1 | `cd3fbee48` | REVISE — map AC8–14 verify |
| plan discuss | `20fec2fbb` | Stage 4 + AC maps |
| Joan r2 | `f2f0a3a31` | APPROVED |
| sync | `c5c145c94` | merge `origin/ftr/AST-1201-base-resume-daisy-chain` (AST-2221) |
| 1 | `91d44a072` | Stage-generic claim walk, persist, runner |
| 2 | `48054e85a` | Dispatcher claim expansion for all stage triggers |
| 3 | `5ac19a088` | Consult routing + persistable gate |

**Tip:** `5ac19a088`

Stage 4 smoke (AC 8–13) green locally. AC 14: `TestAst972*` / consult routing / AST-2006 trigger|retry|hop green; `TestAst2006…[entry_fallback]` expects pre-stage `ERROR_CRAFT_GET_RUBRIC` for `REQUESTED_RESUME` — product now correctly lands `ERROR_SHAPE_THE_STORY` (Betty: update want). No `tests/` edits this ticket.
