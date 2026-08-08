# AST-1272 — Draft hop debug whitelist trail

**Linear:** https://linear.app/astralcareermatch/issue/AST-1272/draft-hop-debug-whitelist-trail-draft-job-resume-response-schema-is  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1268/draft-job-resume-response-schema-is-wrong  
**Publish ref:** `sub/AST-1268/AST-1272-draft-hop-debug-whitelist-trail`

After **AST-1270**, `draft_job_resume` unwraps `agent_payload.resume` and whitelists section keys against the candidate’s `artifacts.base_resume`. This ticket adds Style D (AST-538) found/recorded debug when `debug=True`: whitelist keys, unwrap outcome, and accepted/rejected section keys. It does **not** change allowlist rules, nest key names, metadata allowlists, Manage Tasks prompts, deviations retention (**AST-1271**), or HTML/persist paths.

## Why unwrap must log at normalize (not only validate)

`do_task` already calls `normalize_draft_job_resume_agent_payload(parsed)` **before** schema validation, then `validate_draft_job_resume_payload` calls normalize again. After the first call, `nested_resume_key` is gone — a validate-only unwrap peek would always report `flat` on the live hop path. So unwrap Style D is emitted from normalize when `debug=True` on the **agent** call sites; validate’s internal normalize keeps `debug=False` (default) so the second pass is silent.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/candidate.py` | Add keyword-only `debug=` to normalize + validate; Style D unwrap / whitelist / accept-reject trails | core |
| `src/core/agent.py` | Pass `debug=debug` into draft normalize + validate at both pre-decode and post-rubric-decode sites | core |

**Out of files (siblings / boundaries):**

| File / area | Owner |
|-------------|-------|
| Nest unwrap rules, base_resume whitelist, TASK_CONFIG nest/metadata keys, Manage Tasks seed | AST-1270 (landed on ftr) |
| Persist / retain `deviations` as hop/artifact metadata | AST-1271 |
| HTML builders / cover-letter hops / craft-base parse | out of epic |
| `tests/`, `docs/test-bible/**` | Betty |

## Stage 1: Normalize unwrap Style D + agent wire

**Done when:** With `debug=True`, the first `normalize_draft_job_resume_agent_payload` call in `do_task` emits one Style D index header and `|` detail lines for unwrap outcome (`popped` / `flat` / `invalid`). With `debug=False`, no new contract lines. Allowlist / unwrap mutation behavior unchanged.

1. In `src/core/candidate.py`, change the signature to:

   ```python
   def normalize_draft_job_resume_agent_payload(parsed: dict, *, debug: bool = False) -> None:
   ```

   Keep the existing docstring intent; mention AST-1272 debug trail in the docstring one line.

2. Immediately after resolving `inner`, `nest_key`, and `meta` (and **before** the unwrap `pop`), when `debug` is True:

   - `logger.set_debug_flag(True)`
   - Compute unwrap label from `nested = inner.get(nest_key)`:
     - `isinstance(nested, dict)` → `unwrap_outcome = "popped"` and `nested_section_count = len(nested)`
     - `nest_key in inner` and not a dict → `unwrap_outcome = "invalid"` and `nested_section_count = 0`
     - else → `unwrap_outcome = "flat"` and `nested_section_count = 0`
   - Emit:

     ```python
     logger.debug_index(
         func="candidate.normalize_draft_job_resume_agent_payload",
         index=1,
         total=1,
         identifier=str(inner.get("astral_job_id") or ""),
         outcome=f"unwrap {unwrap_outcome}",
     )
     logger.debug_detail(f"found nest_key={nest_key!r} unwrap={unwrap_outcome}")
     logger.debug_detail(f"found nested_section_count={nested_section_count}")
     ```

   - Do **not** emit when `debug=False`. Do **not** log full section bodies / resume prose (keys/counts only).

3. Keep the existing unwrap + flatten + promote + alias logic **byte-for-byte in behavior** after the debug peek (still `pop` when dict, leave non-dict in place, etc.). Do **not** change meta/nest sources — still `TASK_CONFIG["draft_job_resume"]`.

4. In `src/core/agent.py`, at **both** draft normalize call sites (pre-schema path ~line where `task_key == "draft_job_resume"` before `_validate_response_schema`, and the post-rubric-decode twin), change to:

   ```python
   normalize_draft_job_resume_agent_payload(parsed, debug=debug)
   ```

5. Leave `validate_draft_job_resume_payload`’s internal `normalize_draft_job_resume_agent_payload(parsed)` call **without** `debug=` (defaults False) so the second normalize does not emit a duplicate unwrap trail.

⚠️ **Decision:** Unwrap Style D lives on normalize with `debug=` from agent’s first call only — required because `do_task` unwraps before validate; peeking nest state inside validate alone would lie on the production path.

## Stage 2: Validate whitelist + accepted/rejected Style D + agent wire

**Done when:** With `debug=True`, `validate_draft_job_resume_payload` emits one Style D index header and `|` found/recorded detail for base_resume whitelist keys, accepted section keys, rejected section keys, and the validation error string (`none` when `None`). With `debug=False`, no new contract lines. Unknown-key / typing / empty-whitelist failure strings and accept/reject rules unchanged from AST-1270.

1. In `src/core/candidate.py`, change the signature to:

   ```python
   def validate_draft_job_resume_payload(
       parsed: dict, candidate_data: dict, *, debug: bool = False
   ) -> Optional[str]:
   ```

2. Keep the first line `normalize_draft_job_resume_agent_payload(parsed)` with **no** `debug=` kwarg.

3. After resolving `payload`, `nest_key`, `meta`, and `allowed = set(draft_job_resume_allowed_section_keys(candidate_data))`, introduce accumulators used for both validation and debug:

   ```python
   accepted: list[str] = []
   rejected: list[str] = []
   ```

4. Refactor the existing validation loop **without changing rules**:

   - On early returns that happen **before** the loop (`agent_payload must be a dict`, nest non-dict error, `candidate has no base_resume section keys`): set `err` to that string; leave `accepted`/`rejected` empty; jump to the debug emit + `return err` path below (do not change the error text).
   - Inside the loop, for each non-meta / non-`resume_structure` key:
     - Consult-key / unknown-key / type failures: append `key` to `rejected`, set `err` to the **same** existing error string, break (or return via the shared emit path). Do not continue accepting after the first hard failure — same fail-fast as today.
     - Keys that pass (including empty/`None` skip and valid experience shapes): append `key` to `accepted` and continue.
   - On full success: `err = None` after `pin_experience_job_facts_from_base` as today.

5. Before every `return` from this function (success or error), when `debug` is True:

   - `logger.set_debug_flag(True)`
   - `ident = str(payload.get("astral_job_id") or "")` when `payload` is a dict, else `""`
   - `outcome = "ok" if err is None else "reject"`
   - Emit:

     ```python
     logger.debug_index(
         func="candidate.validate_draft_job_resume_payload",
         index=1,
         total=1,
         identifier=ident,
         outcome=outcome,
     )
     logger.debug_detail(
         f"found whitelist_source=base_resume keys={sorted(allowed)}"
     )
     logger.debug_detail(f"recorded accepted_keys={sorted(accepted)}")
     logger.debug_detail(f"recorded rejected_keys={sorted(rejected)}")
     logger.debug_detail(f"recorded error={err if err is not None else 'none'}")
     ```

   - When the early path never built `allowed` (e.g. payload not a dict), use `allowed = set()` for the found line.
   - Do **not** emit when `debug=False`.
   - Do **not** log section body text.

6. In `src/core/agent.py`, at **both** validate call sites (`resume_section_payload` blocks), change to:

   ```python
   cat_err = validate_draft_job_resume_payload(parsed, cd, debug=debug)
   ```

7. Do **not** edit `TASK_CONFIG`, tracker `_resume_payload_body`, agent_task seed JSON, or experience pin/debug helpers (`debug_experience_jobs` stays as-is for AST-997).

⚠️ **Decision:** Found = whitelist source + keys; recorded = accepted/rejected keys + error. Matches parent AC / AST-1191 found/recorded vocabulary without inventing a second logging API.

⚠️ **Decision:** Keyword-only `debug=` defaults False so existing Betty tests and direct callers stay valid without edits in this ticket (Betty owns any new debug assertions).

## Execution contract

The plan is binding. The agent:

- Executes steps in order within a stage, and stages in order.
- Does not skip, reorder, combine, or expand steps.
- Does not add files, modules, configs, or dependencies that aren't in the Files Changed table.
- Does not change allowlist membership, nest unwrap rules, metadata keys, or error strings except by adding debug emissions around them.
- When a step is ambiguous, contradicts another step, references something that doesn't exist, or fails when executed literally — **stops, comments on the Linear parent issue (AST-1268), and waits.**
- Completes each stage on the epic worktree, commits, publishes to `origin/sub/AST-1268/AST-1272-draft-hop-debug-whitelist-trail`, then continues.

## Self-Assessment

**Scope:** `Single-Component` — Style D debug on existing `candidate.py` draft normalize/validate plus `debug=` passthrough at the two `agent.py` call-site pairs.

**Conf:** `high` — AST-1270 already owns unwrap + whitelist; this ticket only gates observability behind `debug=True` using the same `debug_index` / `debug_detail` helpers as AST-1148 / AST-538.

**Risk:** `low` — default `debug=False` keeps production quiet; wrong detail would mislead operators but cannot change accept/reject outcomes if error strings and loop rules stay untouched.

## Code rules check

- §1.5.1 / `astral.standards.debug-contract-gated`: new lines only when `debug=True`; Style D headers + `|` detail; no `logger.info("[DEBUG] …")`; no full resume blobs.
- §1.3 DRY: one unwrap trail in normalize; one whitelist/accept trail in validate; agent only passes the flag.
- §1.4 / §2.1: no new hardcoded section sets; still reads nest/meta from `TASK_CONFIG` and whitelist via `draft_job_resume_allowed_section_keys`.
- §2.2 / `astral.agent.do-task-delegation`: no new Anthropic assembly; only `debug=` into existing helpers.
- §3.3 imports: core already imports logging helpers; no new layer violations.
- Boundaries: no AST-1270 rule changes; no AST-1271 retention; no test-tree edits.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1268/AST-1272-draft-hop-debug-whitelist-trail`  
**Tip:** `199381dd`

Stages landed: normalize unwrap Style D + agent `debug=` → validate whitelist/accepted/rejected Style D + agent `debug=`.

## Radia review — code-rubric.v2

`[code-rubric] revision=2`
**Overall:** CLEAN
**Diff:** `origin/dev...origin/sub/AST-1268/AST-1272-draft-hop-debug-whitelist-trail` (new product work: `src/core/candidate.py`, `src/core/agent.py` — matches plan Files Changed exactly; `src/utils/config.py`, `src/core/tracker.py`, `data/admin/agent_task.json` are AST-1270 ancestry via the `origin/ftr` merge, untouched by this ticket's own commits)

### Statutes checked (full active set, in-session)

`id | tier | verdict | one-line`

- `orch.roles.betty-owns-test-tree | universal | conforms | test()/merge-tests own tests/ + docs/test-bible/**; code() commits never touch them`
- `orch.roles.archie-approves-statutes | universal | conforms | no canon/statutes/** changed`
- `orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee is Katherine (engineer)`
- `orch.roles.pre-commit-path-bans | universal | conforms | each commit stayed in its role's lane (verified per-commit stat)`
- `orch.roles.engineer-assignee-through-resolve | universal | conforms | Katherine stays assignee through Tests Passed`
- `orch.git.three-permanent-branches | universal | conforms | no new permanent branch`
- `orch.git.flow-direction-inviolable | universal | conforms | tests→sub via merge-tests, ftr→sub merge only`
- `orch.git.no-cherry-pick-rebase-force | universal | conforms | no rebase/force-push/cherry-pick in the commit sequence`
- `orch.git.betty-merge-tests-one-sha | universal | conforms | exactly one merge-tests(AST-1272) commit, SHA 460f329f`
- `orch.git.merge-on-checkout | universal | conforms | explicit "Merge remote-tracking branch 'origin/ftr/...' into sub/..." commit precedes Stage 1`
- `orch.git.one-epic-worktree-per-parent | universal | conforms | single astral-AST-1268/ worktree (see Notes — concurrency observed but resolved)`
- `orch.git.ftr-sub-topology | universal | conforms | sub/AST-1268/AST-1272-… naming, Chuckles-created`
- `orch.git.commit-vocabulary | universal | conforms | docs()/code()/test()/merge-tests() only`
- `orch.git.no-dev-agent-branches | universal | conforms | no dev-<agent> branch`
- `orch.pipeline.call-susan-for-product-decisions | universal | conforms | debug-only ticket; no allowlist/behavior decision improvised`
- `orch.pipeline.status-gates-skill-entry | universal | conforms | stateHistory shows in-order Todo→…→Tests Passed`
- `orch.pipeline.project-scoped-queues | universal | conforms | explicit-id review, no queue behavior`
- `orch.pipeline.plan-is-bible | universal | conforms | Stages 1–2 executed in order, no skip/reorder/expand`
- `astral.agent.do-task-delegation | scoped | conforms | agent.py only threads debug= into existing helpers; no new call assembly`
- `astral.agent.grade-vector-validation | scoped | conforms | vector validation untouched`
- `astral.agent.confidence-bounds | scoped | conforms | confidence handling untouched`
- `astral.batch.claim-process-release | scoped | conforms | claim/process/release untouched`
- `astral.batch.batch-id-first | scoped | conforms | no new batch APIs`
- `astral.batch.entity-agent-responses-latest-only | scoped | conforms | agent_data write path untouched`
- `astral.batch.batch-id-format | scoped | conforms | batch_id construction untouched`
- `astral.config.config-source-of-truth | scoped | conforms | no new literals; reads existing TASK_CONFIG keys from AST-1270`
- `astral.config.pass-threshold-vs-score-floor | scoped | conforms | pass_threshold/score_floor untouched`
- `astral.config.secrets-and-env-specific-from-environ | scoped | conforms | no secrets/env literals added`
- `astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no artifacts/** or scripts/spikes/** paths in diff`
- `astral.debug.spikes-under-debug-dir | scoped | conforms | docs/features addition is the plan doc, not spike notes`
- `astral.dispatch.run-next-is-chain-authority | scoped | conforms | no chain-membership set touched`
- `astral.dispatch.seed-auto-false | scoped | conforms | no dispatch_task/auto_mode touched`
- `astral.docs.features-single-file-per-ticket | scoped | conforms | one file, docs/features/artifacts/ast-1272-…md`
- `astral.git.betty-no-src-or-features | scoped | conforms | Betty's test() commit touches only tests/ + docs/test-bible/**`
- `astral.git.engineer-test-tree-ban | scoped | conforms | code() commits never touch tests/ or docs/test-bible (verified per-commit)`
- `astral.idioms.coat-check-never-store-empty | scoped | conforms | no coat-check handler touched`
- `astral.idioms.render-verdict-orchestrates-consult | scoped | conforms | render_verdict/consult path untouched`
- `astral.idioms.require-auth-on-protected-endpoints | scoped | not-applicable | no src/ui/** changes`
- `astral.layers.core-vs-external-bright-line | scoped | conforms | no I/O added to core`
- `astral.layers.import-direction | scoped | conforms | no new imports; existing core→utils logger/config imports unchanged`
- `astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no scripts/** changes`
- `astral.layers.ui-config-driven-business-logic | scoped | conforms | no UI files touched`
- `astral.seed.agent-tables-in-repo-json | scoped | conforms | agent_task.json entry is AST-1270 ancestry only, untouched by this ticket`
- `astral.seed.archie-catalog-wins | scoped | conforms | no seed catalog edits by this ticket`
- `astral.seed.boot-only-not-hot-path | scoped | conforms | no seed/provision code touched`
- `astral.seed.define-approved | scoped | conforms | parent Architectural definition names the debug-contract need; cites astral.standards.debug-contract-gated`
- `astral.seed.operator-rows-stay-deleted | scoped | conforms | no dispatch_task insert/reconcile logic touched`
- `astral.seed.other-via-coverage-join | scoped | conforms | no new seed/provision path added`
- `astral.standards.database-header-inventory | scoped | not-applicable | no src/data/** changes`
- `astral.standards.data-raises-caller-logs | scoped | conforms | validate/normalize keep returning Optional[str]; debug lines are observability, not the raise/log contract`
- `astral.standards.debug-contract-gated | scoped | conforms | debug_index/debug_detail only, gated by debug=True end-to-end from do_task; no logger.info("[DEBUG]…"); no section bodies logged, keys/counts only`
- `astral.standards.dry-and-focused-functions | scoped | conforms | one unwrap trail in normalize, one whitelist/accept-reject trail in validate; agent.py only threads the flag`
- `astral.standards.in-scope-only | scoped | conforms | this ticket's own diff = exactly the plan's 2 Files Changed`
- `astral.standards.logging-via-utils | scoped | conforms | debug_index/debug_detail are src/utils/logging.py helpers`
- `astral.standards.names-not-ticket-ids | scoped | conforms | no ticket-id identifiers added; AST-1272 appears only in comments/docstrings (carve-out)`
- `astral.standards.no-cross-contamination | scoped | conforms | no out-of-layer import added`
- `astral.standards.no-hardcoded-sets | scoped | conforms | no new inline sets; accepted/rejected are plain per-call lists, not catalogs`
- `astral.standards.public-then-helpers | scoped | conforms | no structural reorg; new logic stays inside the existing public functions`
- `astral.standards.utils-data-late-import-only | scoped | conforms | no utils/config.py edits by this ticket`
- `astral.state.core-decides-transitions | scoped | conforms | no transition logic touched`
- `astral.state.job-prior-states-enforced | scoped | conforms | no job state transition touched`
- `astral.state.no-daisy-chain-in-run | scoped | conforms | no dispatch run-loop touched`
- `astral.ui.frontend-file-placement | scoped | not-applicable | no src/ui/frontend/** changes`
- `astral.ui.naming-conventions | scoped | not-applicable | no src/ui/** changes`
- `astral.ui.single-gunicorn-worker | scoped | conforms | no config.py edits by this ticket`

**Straggler (C4):** Joan's plan-rubric.v1 verdict (attached, APPROVED) reports counts only ("17 scoped excluded") without itemized ids — no itemized Excluded list to cross-check against this sweep's `not-applicable` rows. No contradiction identified.

### Pattern conformance

`none cited` — parent Architectural definition cites only `astral.standards.debug-contract-gated` (a statute, not a catalog pattern id) for this child. No catalog pattern under `canon/patterns/**` matches the diff's shape (debug instrumentation on an existing validator) closely enough to flag an uncited match.

### Findings

None. Both `discuss` items from Joan's plan-rubric verdict were verified resolved in the built code:

- **Sticky debug flag** — plan-rubric worried about `if debug: logger.set_debug_flag(True)` (never restoring INFO). The built code uses the unconditional `logger.set_debug_flag(debug)` at the top of both `normalize_draft_job_resume_agent_payload` and `validate_draft_job_resume_payload` (`candidate.py` lines ~2189, ~2634) — matching the file's prevailing idiom (11 other sites use the same form) and correctly clearing the flag on `debug=False` runs.
- **break hazard on the experience sub-loop** — plan-rubric worried a bare `break` inside `for job in val:` would only exit the inner loop and let the job-array error string get swallowed by the coercion fallback. The built code uses a `bad_job` flag plus `if bad_job or err is not None: break` at the outer-loop level, so `"Section 'experience' must be a job array or prose string"` still returns correctly — no error-string change, no plan-adherence violation.

The third plan-rubric note (unwrap trail invisible to direct `validate(..., debug=True)` callers who skip `do_task`'s own normalize-first call) is an accepted, documented design trade-off — `do_task` is the only production path, and the plan names the limitation explicitly. No action needed.

### What's solid

Precise, surgical implementation: Style D `debug_index`/`debug_detail` on both normalize (unwrap outcome: `popped`/`flat`/`invalid`) and validate (whitelist source, accepted/rejected keys, error), gated end-to-end from `do_task`'s `debug` param through all four call sites (2 normalize + 2 validate, pre-schema and post-rubric-decode). Keys/counts only — no resume prose ever logged. Both real risks flagged by Joan's plan review were fixed in the build, not just noted.

### Notes

Mid-review, this shared epic worktree briefly had another sub (`AST-1271`) checked out concurrently while this review was in progress — resolved by re-checking out `sub/AST-1268/AST-1272-draft-hop-debug-whitelist-trail` before continuing; no stale reads made it into this verdict. Separately, the build itself already caught and removed an AST-1271 code fragment that had bled into `agent.py` (commit `code(AST-1272): drop sibling AST-1271 persist bleed from agent.py`) — confirmed that fragment exists only on `origin/sub/AST-1268/AST-1271-…` (not on `origin/ftr` or `origin/dev`), so the removal is correct scope discipline, not a regression risk. Flagging the concurrency pattern for Chuckles' awareness — not a finding against this ticket, which publishes clean.

context_tokens≈95000
— Radia

## Radia review — code-rubric.v2

`[code-rubric] revision=2`
**Overall:** CLEAN
**Diff:** `origin/dev...origin/sub/AST-1268/AST-1272-draft-hop-debug-whitelist-trail` (new-to-this-child: `src/core/agent.py` (4 call sites), `src/core/candidate.py` (`debug=` params + Style D trails); `src/utils/config.py` / `src/core/tracker.py` / `data/admin/agent_task.json` diffs are inherited AST-1270 content, already reviewed under that ticket — byte-identical here)

### Joan's plan-rubric discuss items vs the built code

Joan's plan-rubric (attached, APPROVED) flagged three `discuss` items at plan time. Checked all three against the actual diff:

1. **Sticky debug flag** — plan text said `if debug: logger.set_debug_flag(True)`; Joan recommended the unconditional `logger.set_debug_flag(debug)` form instead (matches 11 other sites in the file; a `debug=False` run then actively clears any inherited sticky flag). The built code uses the unconditional form in both `normalize_draft_job_resume_agent_payload` and `validate_draft_job_resume_payload`. **Resolved** — a justified micro-deviation from the literal plan text, directly responsive to the reviewer's own recommendation (§5b justification chain satisfied).
2. **break hazard on the experience job-array loop** — Joan flagged that a bare `break` inside `for job in val` would only exit the inner loop, falling through to the coercion path and silently rewriting the error string. The built code uses a `bad_job` flag plus `if bad_job or err is not None: break` to break the **outer** key loop, preserving `"Section 'experience' must be a job array or prose string"` as the returned error. **Resolved.**
3. **Unwrap trail invisible for non-`do_task` `validate(debug=True)` callers** — by design; `do_task` is the only production path (verified both call-site pairs at `agent.py`). No action needed; carried forward as inherited context, not a new finding.

### Statutes checked (full active set, in-session)

Same 65-statute active corpus as AST-1270's sweep (unchanged since that review). Verdicts unchanged for all statutes whose relevant files are the inherited AST-1270 content (`config.py`, `tracker.py`, `agent_task.json`, universal git/pipeline/roles statutes). Re-scored fresh against the incremental `agent.py` + `candidate.py` debug diff:

- `astral.standards.debug-contract-gated | scoped | conforms | full §5f pass: gated behind debug=True (double-gated — debug_detail also checks _debug_flag internally); found/recorded vocabulary; index 1/1 (single-job hop, not a batch loop); no body text logged, only keys/counts; no logger.info("[DEBUG]…") added; no data-layer logging`
- `astral.agent.do-task-delegation | scoped | conforms | no new Anthropic call assembly; do_task only forwards debug= into existing normalize/validate hooks (cited in ticket In scope)`
- `astral.standards.dry-and-focused-functions | scoped | conforms | single shared debug-emit path at the end of validate (all early-return branches fall through to one block) rather than 4 duplicated emit blocks — matches Joan's own "acceptable" DRY read of plan step 5`
- `astral.standards.in-scope-only | scoped | conforms | diff = exactly the plan's 2 Files Changed (candidate.py, agent.py); build even self-corrected a caught AST-1271 persist-call bleed in agent.py via a dedicated d4d3d366 commit before publish`
- `astral.standards.public-then-helpers | scoped | conforms | new public draft_job_resume_allowed_section_keys stays with public draft helpers; private alias helper stays after the public validate fn (same ordering as AST-1270)`
- `astral.standards.names-not-ticket-ids | scoped | conforms | no AST-1272-style identifiers added; comments cite the ticket, not names`
- `astral.standards.no-hardcoded-sets | scoped | conforms | no new inline set; reads nest/meta from TASK_CONFIG as before`
- `astral.standards.data-raises-caller-logs | scoped | conforms | normalize/validate still return Optional[str]; debug emission is observability only, not error handling`
- `astral.standards.logging-via-utils | scoped | conforms | logger.debug_index/debug_detail via src/utils/logging.py facade`
- `astral.layers.import-direction | scoped | conforms | no new cross-layer import; core still core→utils`
- `astral.layers.core-vs-external-bright-line | scoped | conforms | no I/O added`
- `astral.standards.no-cross-contamination | scoped | conforms | no out-of-layer import; the AST-1271 bleed was caught and reverted pre-publish`
- `orch.pipeline.call-susan-for-product-decisions | universal | conforms | pure observability ticket, no product-behavior decision in scope — unlike AST-1270, nothing here needed Susan`
- `orch.pipeline.plan-is-bible | universal | conforms | Stages 1-2 executed in order; the two literal-text deviations (unconditional set_debug_flag, bad_job break) are justified fixes for reviewer-flagged risks, not improvisation — §5b chain satisfied via Joan's own recommendation text`

All other statutes (universal git/roles/pipeline set, and the scoped seed/batch/state/dispatch/ui/idioms/config set whose applicability is driven by the inherited `config.py`/`tracker.py`/`agent_task.json` content) score identically to AST-1270's sweep: conforms or not-applicable, no violates, no new needs-discussion.

**Straggler (C4):** Joan's AST-1272 plan-rubric verdict reports counts only ("17 scoped excluded") without itemized ids — no itemized Excluded list to cross-check. No contradiction identified.

### Pattern conformance

`none cited` — AST-1272's own ticket citations are statute ids only (`astral.standards.debug-contract-gated`); the parent's `pattern.config.config-block` citation was fully consumed by AST-1270 (this child reads `TASK_CONFIG["draft_job_resume"]` but does not extend it).

### Findings

No fix-now, no discuss. All three items Joan flagged at plan time were addressed in the built code with justified, narrow deviations from the literal plan text.

### What's solid

Clean single-exit refactor of `validate_draft_job_resume_payload` — every branch (three early-return failure modes plus the main loop) now funnels through one debug-emit block before `return err`, which is both the DRY reading of the plan and the only way to guarantee Style D fires on every exit path. The mid-build self-catch of the AST-1271 persist-call bleed (dedicated `d4d3d366` commit, cleanly reverted, no residue) is exactly the scope discipline `astral.standards.in-scope-only` wants.

context_tokens≈95000
— Radia
