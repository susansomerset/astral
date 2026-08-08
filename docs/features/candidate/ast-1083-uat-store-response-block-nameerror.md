<!-- linear-archive: AST-1083 archived 2026-08-07 -->

## Linear archive (AST-1083)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1083/uat-nameerror-in-store-response-block-response-debug-log  
**Status at archive:** Archive  
**Project:** Astral Candidate  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-952 — Candidate Profile Preamble to Intake  
**Blocked by / blocks / related:** parent: AST-952

### Description

<!-- uat-validate: stacktrace -->

## What failed

While UAT-testing Candidate Intake (candidate `mcevoy`), after Estelle `intake_initiate_candidate` returned a successful assistant message, backend logged:

```
[ ~ ] _store_response_block failed
Traceback (most recent call last):
  File ".../src/core/agent.py", line 2593, in do_task
    resp_id = _store_response_block(...)
  File ".../src/core/agent.py", line 1549, in _store_response_block
    f"agent_data_write block_type=RESPONSE outcome={result.get('outcome')} "
NameError: name 'result' is not defined
```

`do_task` still printed completed successfully, but RESPONSE `agent_data_write` debug path crashed.

## Expected

`_store_response_block` persists the RESPONSE block and (when `debug=True`) emits the found/recorded-style `agent_data_write` detail line without raising. Intake initiate continues without a stacktrace in the server log.

## Repro

1. Open Candidate Intake for candidate `mcevoy` on local/staging with debug logging on.
2. Start a new intake so Estelle runs `intake_initiate_candidate` (after preamble / into chat as applicable).
3. Observe server log: LLM success, then `_store_response_block failed` NameError on `result`.

## Parent AC (quoted inline)

> 8. Touched backend `debug=True` validation/write paths emit per-step found/recorded debug lines per the contract above.
> 9. Candidate can complete the mechanical preamble UI driven by PREAMBLE_CONFIG; Valid answers persist to the correct columns/blobs; UI calls Ruth validation rather than inlining a checker.

## Diagnosis

* **Hypothesis:** In `_store_response_block`, `save_agent_data(...)` return value is not bound to `result`, but the `debug=True` detail log still calls `result.get(...)` — NameError on every RESPONSE store under debug.
* **Correct outcome:** RESPONSE block write returns cleanly; debug detail logs the write outcome; intake open message path does not dump a traceback.
* **Wrong fix to avoid:** bare `try/except` swallow around the debug line; deleting RESPONSE storage; turning off debug to hide the error; returning empty success without persisting agent_data.
* **Related siblings / contracts:** AST-1015 (Ruth/agent_task), AST-1017 (mechanical intake UI) — intake still must call validation/UI contracts; this fix is [agent.py](<http://agent.py>) RESPONSE store/debug only.

## Boundaries

- [X] This bug does **not** change: PREAMBLE_CONFIG copy, Ruth Valid/Try Again/Escalate semantics, contact/context/artifacts schema, or Estelle prompt content.
- [X] "No more stacktrace / no more error" alone is **not** done — Parent AC + Correct outcome must hold.

## Acceptance criteria

- [X] With `debug=True`, `_store_response_block` / RESPONSE `do_task` path persists agent_data and emits `agent_data_write block_type=RESPONSE` detail without NameError.
- [X] Intake initiate for a candidate (e.g. mcevoy) does not log `_store_response_block failed` traceback after a successful Estelle reply.

## In scope

- [X] `src/core/agent.py` — `_store_response_block` bind `result = save_agent_data(...)` (mirror sibling store debug path).

## Considered but excluded

- [X] PREAMBLE_CONFIG / AST-1015 Ruth outcomes / AST-1017 intake UI — wrong layer for this NameError.
- [X] Swallowing the debug log in try/except — hides AC 8 found/recorded contract.
- [X] Turning off debug — does not restore the write-path debug line.

## Git branch (authoritative)

`sub/AST-952/AST-1083-uat-store-response-block-nameerror`. Publish to `origin/<publish-ref>` only.

### Comments

#### hedy — 2026-07-30T18:52:17.662Z
`origin/sub/AST-952/AST-1083-uat-store-response-block-nameerror` @ `ec24b22f` · §9a clean · ftr dry-run clean

#### radia — 2026-07-30T18:49:27.992Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1083
**Publish ref:** `sub/AST-952/AST-1083-uat-store-response-block-nameerror` @ `d7a1b971b2d72e4871b10d4c402adaa50fa1f87f` (product tip `51de0897`; docs append `d7a1b971`)
**Overall:** CLEAN

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| orch.git.betty-merge-tests-one-sha | universal | conforms | Single `merge-tests(AST-1083)` from Betty tip `0a635933` |
| orch.git.commit-vocabulary | universal | conforms | docs/code/test/merge-tests vocab on publish-ref |
| orch.git.flow-direction-inviolable | universal | conforms | Publish to origin/sub only; no reverse-flow |
| orch.git.ftr-sub-topology | universal | conforms | Child on `sub/AST-952/AST-1083-uat-store-response-block-nameerror` |
| orch.git.merge-on-checkout | universal | conforms | Tip includes merge(ftr) ancestry; origin/dev is ancestor |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | Linear history; no force/rebase on publish-ref |
| orch.git.no-dev-agent-branches | universal | conforms | No agent-named epic branch; sub under parent |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Review in astral-AST-952 worktree |
| orch.git.three-permanent-branches | universal | conforms | Touches sub only; not inventing fourth permanent |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | No product-decision open questions in scope |
| orch.pipeline.plan-is-bible | universal | conforms | Stage 1 one-line bind matches plan exactly |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Candidate / Team Chuckles gates held |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Review entered from Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No statute edits in diff |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty bible + merge-tests; reuse AST-1076 cases |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee remains Hedy through review |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Hedy stays assignee at Review Posted |
| orch.roles.pre-commit-path-bans | universal | conforms | Docs-only Radia commit; no src/tests in docs() |
| astral.agent.confidence-bounds | scoped | conforms | No confidence fields touched |
| astral.agent.do-task-delegation | scoped | conforms | No do_task routing change; store helper only |
| astral.agent.grade-vector-validation | scoped | conforms | No grade-vector path touched |
| astral.batch.batch-id-first | scoped | conforms | batch_id usage unchanged in store helper |
| astral.batch.batch-id-format | scoped | conforms | No batch_id format change |
| astral.batch.claim-process-release | scoped | conforms | No claim/release path touched |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | RESPONSE store id/hash logic unchanged |
| astral.config.config-source-of-truth | scoped | conforms | No config edits |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | No threshold/score edits |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No secrets/env edits |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths predicate — no artifacts/** or scripts/spikes/** |
| astral.debug.spikes-under-debug-dir | scoped | conforms | No spike/debug-dir artifacts added |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Single plan file `ast-1083-uat-store-response-block-nameerror.md` |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty tip is bible/tests; no engineer features smuggle |
| astral.git.engineer-test-tree-ban | scoped | conforms | AST-1083 code commit is agent.py only; tests via Betty reuse |
| astral.layers.core-vs-external-bright-line | scoped | conforms | Core-only bind; no external touch |
| astral.layers.import-direction | scoped | conforms | No import changes |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers/paths — no scripts/** |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | layers/paths — no ui/utils config |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | Still persists RESPONSE block_data; no empty-store bypass |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | No consult/verdict path touched |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | layers/paths — no src/ui/** |
| astral.standards.data-raises-caller-logs | scoped | conforms | No data-layer logging added |
| astral.standards.database-header-inventory | scoped | not-applicable | layers/paths — no src/data/** |
| astral.standards.debug-contract-gated | scoped | conforms | Debug detail still behind `debug=True`; bind restores outcome line |
| astral.standards.dry-and-focused-functions | scoped | conforms | Mirrors sibling `_save` bind; no rewrite |
| astral.standards.in-scope-only | scoped | conforms | agent.py bind only; boundaries held |
| astral.standards.logging-via-utils | scoped | conforms | Existing get_logger/debug_detail path unchanged |
| astral.standards.no-cross-contamination | scoped | conforms | No sibling PREAMBLE/Ruth/UI edits |
| astral.standards.no-hardcoded-sets | scoped | conforms | No new hardcoded sets |
| astral.standards.public-then-helpers | scoped | conforms | Helper-only change; signature unchanged |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | layers/paths — no src/utils/** |
| astral.state.core-decides-transitions | scoped | conforms | No state-transition logic touched |
| astral.state.job-prior-states-enforced | scoped | conforms | No job-state edits |
| astral.state.no-daisy-chain-in-run | scoped | conforms | No run daisy-chain touched |
| astral.ui.frontend-file-placement | scoped | not-applicable | layers/paths — no src/ui/frontend/** |
| astral.ui.naming-conventions | scoped | not-applicable | layers/paths — no src/ui/** |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | layers/paths — no ui/scripts/config worker touch |

## Pattern conformance

none cited

## Plan adherence

Stage 1 delivered exactly: `result = save_agent_data(...)` in `_store_response_block`, debug block and return left intact. Wrong fixes (try/except swallow, delete RESPONSE storage, disable debug, empty success) absent. Scope remains minor / high conf / low risk. Joan uat-thin APPROVED (no Excluded statute list → C4 straggler N/A).

## Findings

none

## What’s solid

- One-line bind identical to `_store_prompt_blocks` `_save` pattern
- Restores AC 8 found/recorded `agent_data_write block_type=RESPONSE` under `debug=True` without hiding failures
- Betty reuse of `TestAst1076StoreResponseDebugResult` + existing write-outcome case

## Notes

Joan artifact is `[validate-plan uat-thin]` APPROVED — not a full plan-rubric Excluded list; no C4 straggler pass required.

context_tokens≈22000

— Radia

#### betty — 2026-07-30T18:44:52.589Z
## QA test manifest

`origin/sub/AST-952/AST-1083-uat-store-response-block-nameerror` @ `cbbdfc91` (`merge-tests(AST-1083): origin/tests 0a635933`).

Same RESPONSE debug `result` bind as AST-1076 — reuse existing coverage (no new cases).

1. `tests/component/core/test_agent.py::TestAst1076StoreResponseDebugResult` — `debug=True` does not NameError on `result`
2. `tests/component/core/test_agent.py::TestAst977AgentDataDedupeDebug::test_store_response_debug_emits_write_outcome` — `agent_data_write` outcome detail

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst1076StoreResponseDebugResult \
  tests/component/core/test_agent.py::TestAst977AgentDataDedupeDebug::test_store_response_debug_emits_write_outcome \
  -q
```

**Bible sha256** (`git show origin/sub/AST-952/AST-1083-uat-store-response-block-nameerror:docs/test-bible/core/agent.md`):
- `docs/test-bible/core/agent.md` `a9099bb1cc6580a4299702f5bcaef2a1e032657820d68a2a716e099c9ebd14eb`

— Betty

#### joan — 2026-07-30T18:27:08.029Z
[validate-plan uat-thin]
**Ticket:** AST-1083
**Overall:** APPROVED

## UAT-thin checklist

- [x] Plan cites Parent AC (quoted AC 8 + AC 9 in ## UAT fitness), not symptom-only
- [x] Stage 1 achieves Correct outcome: bind `result = save_agent_data(...)`, persist RESPONSE, emit `agent_data_write block_type=RESPONSE` under `debug=True`, return `agent_data_id` — not merely silence the NameError
- [x] Wrong fixes rejected (try/except swallow, delete RESPONSE storage, disable debug, empty success without persist) — plan implements sibling-style bind only
- [x] No catch-and-ignore / delete-log-path / empty-success / bypass
- [x] Sibling check: AST-1015 / AST-1017 unchanged; scope `src/core/agent.py` only
- [x] Boundaries respected: no PREAMBLE_CONFIG / Ruth semantics / library / Estelle prompt edits

## Notes

## UAT fitness present. Conf high / Risk low honest for a one-line bind mirroring ~L1208.

context_tokens≈18000

— Joan

#### hedy — 2026-07-30T18:20:22.556Z
Plan: [docs/features/candidate/ast-1083-uat-store-response-block-nameerror.md](https://github.com/susansomerset/astral/blob/sub/AST-952/AST-1083-uat-store-response-block-nameerror/docs/features/candidate/ast-1083-uat-store-response-block-nameerror.md) @ `8c759a5c`.

**Scope:** minor — single `result = save_agent_data(...)` bind in `_store_response_block`.
**Conf:** high — Diagnosis matches source; sibling store ~L1208 already shows the pattern.
**Risk:** low — restores debug detail on an already-successful RESPONSE write; no schema/UI/config change.

## UAT fitness present — AC 8/9, Correct outcome, sibling AST-1015/1017 check, wrong-fix rejects listed.

---

# UAT: NameError in `_store_response_block` RESPONSE debug log

**Linear:** [AST-1083](https://linear.app/astralcareermatch/issue/AST-1083/uat-nameerror-in-store-response-block-response-debug-log)
**Parent:** [AST-952](https://linear.app/astralcareermatch/issue/AST-952)
**Publish ref:** `sub/AST-952/AST-1083-uat-store-response-block-nameerror`

After Estelle `intake_initiate_candidate` succeeds, `_store_response_block` persists the RESPONSE `agent_data` row but crashes under `debug=True` because the `save_agent_data(...)` return is never bound to `result`, yet the found/recorded-style detail log calls `result.get(...)`. Bind the return like the sibling non-RESPONSE store path already does so the write completes and the debug line emits without a NameError.

## UAT fitness

- **AC restored:** Parent AC 8 — “Touched backend `debug=True` validation/write paths emit per-step found/recorded debug lines per the contract above.” Parent AC 9 — “Candidate can complete the mechanical preamble UI driven by PREAMBLE_CONFIG; Valid answers persist to the correct columns/blobs; UI calls Ruth validation rather than inlining a checker.” (intake open / Estelle initiate must not dump a RESPONSE-store traceback that breaks the debug contract on the write path.)
- **Correct outcome:** RESPONSE block write returns cleanly; when `debug=True`, the `agent_data_write block_type=RESPONSE …` detail line logs the write outcome; intake open-message path does not dump a `_store_response_block failed` traceback.
- **Sibling check:** AST-1015 (Ruth / `preamble_validate_response`) and AST-1017 (mechanical intake UI) contracts unchanged — this ticket only fixes `src/core/agent.py` RESPONSE store/debug binding. No PREAMBLE_CONFIG, Ruth outcomes, or intake UI edits. Verified by plan file scope + Files Changed table.
- **Not sufficient:** Removing the stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Bare `try/except` swallow around the debug line; deleting RESPONSE storage; turning off debug to hide the error; returning empty success without persisting `agent_data` — all rejected by Diagnosis. Correct fix is bind `result = save_agent_data(...)` (mirror sibling store at ~L1208).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/agent.py` | In `_store_response_block`, bind `result = save_agent_data(...)` so the existing `debug=True` `agent_data_write` detail line can read `outcome` / `agent_data_id` / `ref_agent_data_id` without NameError | core |

## Stage 1: Bind `save_agent_data` return in `_store_response_block`

**Done when:** With `debug=True`, calling `_store_response_block` (or completing a `do_task` that stores a RESPONSE) persists the RESPONSE row and emits the `agent_data_write block_type=RESPONSE outcome=…` detail line without raising `NameError: name 'result' is not defined`. Function still returns `agent_data_id`.

1. In `src/core/agent.py`, locate `_store_response_block` (currently ~L1520–1553). The call:

   ```python
   save_agent_data(
       agent_data_id=agent_data_id,
       ...
       entity_id=index if index else None,
   )
   ```

   is followed by a `if debug:` block that interpolates `result.get('outcome')`, `result.get('agent_data_id')`, and `result.get('ref_agent_data_id')`.

2. Change that call to bind the return value, matching the sibling store path immediately above (~L1208–1224):

   ```python
   result = save_agent_data(
       agent_data_id=agent_data_id,
       entity_type=entity_type,
       task_key=task_key,
       batch_id=batch_id,
       block_type="RESPONSE",
       block_data=response_text,
       token_size=len(response_text) // CHARS_PER_TOKEN,
       created_at=created_at,
       entity_id=index if index else None,
   )
   ```

3. Leave the existing `if debug:` `dbg.debug_detail(...)` block and the `return agent_data_id` unchanged — do not wrap the debug line in `try/except`, do not delete RESPONSE storage, do not alter `save_agent_data` kwargs beyond the binding.

⚠️ **Decision:** One-line bind to `result` rather than rewriting the debug line to use local `agent_data_id` only — preserves the found/recorded-style contract that logs `outcome` / `ref_agent_data_id` from the write result, identical to the non-RESPONSE store path.

## Self-Assessment

**Scope:** minor — single binding in `src/core/agent.py` `_store_response_block`.

**Conf:** high — Diagnosis matches the source; sibling pattern at ~L1208 already shows the correct bind.

**Risk:** low — restores debug logging on an already-successful write; no schema, config, or intake UI change. Wrong bind would still NameError or log incomplete detail only in this helper.

## Code Rules self-review

| Rule | Check |
|------|--------|
| §1.3 DRY | Reuse the existing `result = save_agent_data(...)` + `agent_data_write` detail pattern from the sibling store in the same file |
| §1.5.1 | Debug detail remains gated on `debug=True`; no new unconditional logs |
| §2.2 | Core-only change; no UI→external |
| §3.3 | No new imports |
| Boundaries | No PREAMBLE_CONFIG / Ruth / library / Estelle prompt edits |

## Review

**Publish ref:** `sub/AST-952/AST-1083-uat-store-response-block-nameerror`
**Build tip:** `51de0897`
**code-rubric:** revision=1 — **Overall: CLEAN** (tip after this docs append)

### Stages delivered

1. `_store_response_block` — bind `result = save_agent_data(...)` so `debug=True` `agent_data_write` detail line no longer NameErrors.

### Radia — code-rubric.v1 @ tip (post-docs)

Three-dot `origin/dev...origin/sub/AST-952/AST-1083-uat-store-response-block-nameerror`: product delta is the one-line `result =` bind in `_store_response_block`; mirrors `_store_prompt_blocks` `_save`. Debug detail remains gated on `debug=True`. Plan Stage 1 + wrong-fix rejects held. Betty reused AST-1076 RESPONSE NameError coverage (no new cases). No fix-now / discuss.

## Resolution

**2026-07-30** — `resolve(AST-1083): — clean`

- **fix-now:** none (Radia Overall CLEAN).
- **discuss:** none.
- Tip after resolve publish: `origin/sub/AST-952/AST-1083-uat-store-response-block-nameerror` (this commit).
