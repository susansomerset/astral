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
