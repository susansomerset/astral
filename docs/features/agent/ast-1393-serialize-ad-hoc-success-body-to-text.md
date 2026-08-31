<!-- linear-archive: AST-1393 archived 2026-08-31 -->

## Linear archive (AST-1393)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1393/serialize-ad-hoc-success-body-to-text-ad-hoc-agent-is-failing  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** ada  
**Priority / estimate:** None / 2  
**Parent:** AST-1392 — Ad hoc Agent is failing  
**Blocked by / blocks / related:** parent: AST-1392; blocks: AST-1394

### Description

## What this implements

Own the workbench success path so any successful model body becomes text before RESPONSE write (JSON text for objects/lists, otherwise the raw text), using one stringify habit rather than a second store helper. Persist that text; with `debug=True` show found type/shape → recorded text; never let a non-string payload raise a storage type error as the Test outcome. Does **not** own React chrome or production `do_task` schema validation (see #2 and Boundaries).

## Citations

`pattern.batch.entity-agent-responses`; `astral.standards.data-raises-caller-logs`; `astral.batch.entity-agent-responses-latest-only`; `astral.standards.debug-contract-gated`; `astral.standards.dry-and-focused-functions`; `astral.agent.do-task-delegation`.

## Acceptance criteria

- [X] 1. An Agent Ad Hoc Test whose model returns a successful JSON envelope with an object payload (the `craft_company_search_terms` shape in the original brief) completes as success: the workbench shows the payload as JSON text, and no `_store_response_block failed` / `block_data must be a str` traceback appears for that run.
- [X] 2. Execution History inspection for that Test run includes a RESPONSE body equal to the text shown in the workbench (JSON text of the payload, not an empty or missing block).
- [X] 3. A successful reply that is already plain text still displays and stores as that text — no extra JSON wrapping.
- [X] 4. With `debug=True`, the serialized store is visible as found→recorded under Style D; with `debug=False`, this path adds no new debug lines.

## Boundaries

- [X] Does **not** own React chrome, Admin Test HTTP display overlay, or production `do_task` schema validation / AST-1289 coerce. Sibling #2 owns showing the Test body without type invalidation. Does **not** relax `save_agent_data` to accept non-text `block_data`. Does **not** treat provider/API failures as success.

## Notes for planning

Reuse the existing `do_task` habit of JSON-serializing object/list payloads before RESPONSE write. Data layer still raises on non-text; core serializes. Ad Hoc Test stays on the workbench wrapper, not routed through production `do_task` validation just to get a store.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1392-ad-hoc-agent-is-failing`, child `sub/AST-1392/AST-1393-serialize-ad-hoc-success-body-to-text`. Created at dispatch-parent.

## QA test manifest

1. Existing string-payload ledger + store: `tests/component/core/test_agent.py::TestAst515AdhocWorkbenchLedger`
2. Object/list/plain-text stringify + debug Style D: `tests/component/core/test_agent.py::TestAst1393SerializeAdhocSuccessBody`

**Broken / obsolete:** none.

**Integration:** none revised.

**Narrowed run:**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst515AdhocWorkbenchLedger \
  tests/component/core/test_agent.py::TestAst1393SerializeAdhocSuccessBody \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

**Bible shasum** (`origin/sub/AST-1392/AST-1393-serialize-ad-hoc-success-body-to-text`):

* `docs/test-bible/core/agent.md` `ef3348a750fe36f10629fa51b7b88f3510442bc4`

### Comments

#### radia — 2026-08-16T01:50:20.466Z
[code-rubric] PROCEED (Commit: a45fff61) core stringify clean

#### betty — 2026-08-16T01:46:00.211Z
`origin/sub/AST-1392/AST-1393-serialize-ad-hoc-success-body-to-text` @ `a45fff61` · object payload stringify coverage

#### joan — 2026-08-16T01:33:02.943Z
[plan-rubric] PROCEED (Commit: 2a87dcd5) stringify before store

#### ada — 2026-08-16T01:29:58.092Z
`origin/sub/AST-1392/AST-1393-serialize-ad-hoc-success-body-to-text` @ `2a87dcd5` · stringify before store

---

# Serialize Ad Hoc success body to text

- **Linear:** [AST-1393](https://linear.app/astralcareermatch/issue/AST-1393)
- **Parent:** [AST-1392](https://linear.app/astralcareermatch/issue/AST-1392)
- **Publish ref:** `sub/AST-1392/AST-1393-serialize-ad-hoc-success-body-to-text`

Agent Ad Hoc Test currently extracts `agent_payload` (or the whole `parsed_response`) and passes that value straight into `_store_response_block`. When the payload is an object — the `craft_company_search_terms` envelope in the parent brief — `save_agent_data` raises `block_data must be a str`, and logs show `_store_response_block failed`. This ticket stringifies that success body to text **before** the RESPONSE write (JSON text for dict/list, otherwise the raw text), using the existing `_caller_response_blob` habit rather than a second store helper, persists that text, and emits found type/shape → recorded text under Style D when `debug=True`.

Sibling #2 owns Admin Test HTTP overlay and React chrome. This ticket does **not** edit `src/ui/api/api_admin.py` or `AdminAnthropicAdHoc.tsx`. Production `do_task` schema validation / AST-1289 coerce is unchanged.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/agent.py` | Stringify workbench success body via `_caller_response_blob` before `_store_response_block`; Style D found→recorded when `debug=True` | core |

Do **not** edit: `src/data/database.py` (`save_agent_data` still raises on non-text), `_store_response_block` signature, `do_task` schema validation / coerce, `src/ui/api/api_admin.py`, `src/ui/frontend/src/pages/AdminAnthropicAdHoc.tsx`, `tests/`, bible.

## Stages

### Stage 1: Stringify workbench success body before RESPONSE write

**Done when:** `run_adhoc_workbench_test` on a successful result whose `parsed_response` is a JSON envelope with an object `agent_payload` (the `craft_company_search_terms` shape) passes a `str` into `_store_response_block` — compact JSON text of that payload, not a dict, not a Python `str(dict)` dump — and the Test still completes success (`dispatch_ledger` `COMPLETED`). A successful plain-text `parsed_response` is stored unchanged (no extra JSON wrapping). With `debug=True`, Style D shows found type/shape → recorded text for that serialize; with `debug=False`, this path adds no new debug-contract lines. `python3 -m py_compile src/core/agent.py` passes.

1. In `src/core/agent.py`, in `run_adhoc_workbench_test`, replace **only** the success-path body that currently reads:

   ```python
           parsed = result.get("parsed_response")
           if isinstance(parsed, dict) and "agent_payload" in parsed:
               response_text = parsed["agent_payload"] or ""
           else:
               response_text = str(parsed) if parsed is not None else ""
           try:
               _store_response_block(
                   entity_type,
                   workbench_task_key,
                   batch_id,
                   response_text,
                   index=entity_id,
                   debug=debug)
           except Exception:
               logger.debug("_store_response_block failed", exc_info=True)
   ```

   with this exact sequence (still inside the existing `else:` of `if not result.get("success"):`):

   ```python
           parsed = result.get("parsed_response")
           if isinstance(parsed, dict) and "agent_payload" in parsed:
               body = parsed["agent_payload"]
           else:
               body = parsed
           try:
               response_text = _caller_response_blob(body)
               if debug:
                   dbg = get_logger(__name__, debug_flag=True)
                   if isinstance(body, dict):
                       shape = f"keys={sorted(body.keys())}"
                   elif isinstance(body, list):
                       shape = f"len={len(body)}"
                   elif isinstance(body, str):
                       shape = f"len={len(body)}"
                   elif body is None:
                       shape = "none"
                   else:
                       shape = type(body).__name__
                   dbg.debug_index(
                       func="run_adhoc_workbench_test",
                       index=1,
                       total=1,
                       identifier=workbench_task_key,
                       outcome="serialized store",
                   )
                   dbg.debug_detail(
                       f"found type={type(body).__name__} shape={shape}"
                   )
                   dbg.debug_detail_block(response_text)
               _store_response_block(
                   entity_type,
                   workbench_task_key,
                   batch_id,
                   response_text,
                   index=entity_id,
                   debug=debug)
           except Exception:
               logger.debug("_store_response_block failed", exc_info=True)
   ```

   `get_logger` is already imported in this module. `_caller_response_blob` already lives in this file (`json.dumps(..., ensure_ascii=False, default=str)` for dict/list; `str(body)` for other non-`None`; `""` for `None`). Do **not** add a second stringify helper. Do **not** call `json.dumps` inline here.

2. Do **not** change the failure branch (`if not result.get("success"):`) — it already stores `_failure_response_block_data(...)` as text. Provider/API failures stay failed Tests.

3. Do **not** change `_store_response_block` to accept non-text. Do **not** change `save_agent_data`. Do **not** route Ad Hoc Test through production `do_task` validation to get a store. Do **not** change `do_task`'s own `store_content = json.dumps(parsed) if isinstance(parsed, (dict, list)) else (parsed or raw_text)` line.

4. Do **not** mutate `result["parsed_response"]`. Do **not** add a new key on `result`. `return result` at the end of the function stays as-is. Sibling #2 owns returning this text from `POST /api/admin/adhoc/test` and pretty-printing it in React.

5. Do **not** pretty-print the stored JSON (`indent=`). Compact JSON from `_caller_response_blob` is the stored RESPONSE body. Do **not** wrap an already-`str` body in extra JSON quotes.

6. Do **not** edit `tests/` or `docs/test-bible/**`. Existing component test `test_success_completes_ledger_and_stores_blocks` still sees `_store_response_block` arg `[3] == "ok"` for a string payload. Betty owns any new object-payload coverage.

⚠️ **Decision:** Reuse `_caller_response_blob` instead of a new workbench-only dumps helper or a second `_store_response_block` that accepts objects. That function is already the dict/list → JSON text / else `str` habit in this file (`astral.standards.dry-and-focused-functions`). Data still raises on non-text (`astral.standards.data-raises-caller-logs`).

⚠️ **Decision:** Keep extracting `agent_payload` when that key is present, then stringify **that** body — not the full `{agent_performance, agent_payload}` envelope. Parent: when a payload key is present, store that payload body. `do_task` dumps the full `parsed` envelope; workbench stays on the payload (existing extract, now JSON text). Empty dict/list become `"{}"` / `"[]"` (structured JSON text), not `""` from the old `or ""` falsy collapse.

⚠️ **Decision:** Do not change `do_task` store or Admin HTTP/React in this ticket. Production ingest and sibling #2 display are out of Boundaries. One stringify call site for the workbench success path is enough.

⚠️ **Decision:** Debug is Style D on `run_adhoc_workbench_test` (index `1/1`, identifier=`workbench_task_key`, outcome=`serialized store`), found type/shape on one `|` detail line, recorded text via `debug_detail_block` (truncation contract). Emit only when `debug=True`. Do not log the raw found object.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Traceability

AC1 persist/no-traceback → S1 | AC2 RESPONSE body → S1 | AC3 plain text → S1 | AC4 debug found→recorded → S1
(AC1 workbench **display** / pretty-print → sibling #2, not this plan)

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
revision: 1
**Ticket:** AST-1393
**Overall:** APPROVED
**Publish ref:** `sub/AST-1392/AST-1393-serialize-ad-hoc-success-body-to-text` @ `2a87dcd5`

## Traceability
AC1 persist/no-traceback → S1 (workbench display → sibling #2) | AC2 RESPONSE body → S1 | AC3 plain text → S1 | AC4 debug found→recorded → S1

## Findings

### acceptable — epic split / AC1 display clause
- **Location:** Plan Boundaries + `## Traceability` note; child Description AC1
- **Finding:** Child AC1 quotes “workbench shows … as JSON text,” but this plan correctly limits scope to core stringify + store; Admin HTTP/React display is sibling #2. Boundaries and traceability call this out explicitly.
- **Recommendation:** No plan change required. UAT for #1 should verify RESPONSE persistence and absence of `_store_response_block failed` / `block_data must be a str`; workbench display parity lands with #2.

### acceptable — Stage 1 done-when vs AC2 wording
- **Location:** Stage 1 “Done when”
- **Finding:** Done-when specifies `str` into `_store_response_block` and ledger `COMPLETED`; AC2’s “equal to text shown in the workbench” is only fully testable after #2. Store path implies AC2 for Execution History.
- **Recommendation:** Optional clarity only — Betty may assert RESPONSE row content in component tests when she adds object-payload coverage.

context_tokens≈11500

## Review (build stub)

**Publish ref:** `origin/sub/AST-1392/AST-1393-serialize-ad-hoc-success-body-to-text`
**Tip (pre-review):** `7fed10d1`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `7fed10d1` | Workbench success body via `_caller_response_blob` before RESPONSE write; Style D found→recorded when `debug=True` |

## Radia review

**Rubric:** code-rubric.v1
**Ticket:** AST-1393
**Publish ref:** `origin/sub/AST-1392/AST-1393-serialize-ad-hoc-success-body-to-text` @ `a45fff61`
**Overall:** CLEAN
**Diff baseline:** `origin/dev...origin/sub/AST-1392/AST-1393-serialize-ad-hoc-success-body-to-text` (4 files: `src/core/agent.py`, `tests/component/core/test_agent.py`, `docs/test-bible/core/agent.md`, `docs/features/agent/ast-1393-serialize-ad-hoc-success-body-to-text.md`)

## Statutes checked

63 active statutes per `canon/statutes/README.md` § Harvested corpus (registry row count; README footer “65” appears stale vs table).

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | not-applicable | no confidence/grade paths touched |
| `astral.agent.do-task-delegation` | scoped | not-applicable | workbench path only; `do_task` unchanged |
| `astral.agent.grade-vector-validation` | scoped | not-applicable | no schema/vector validation changes |
| `astral.batch.batch-id-first` | scoped | conforms | existing workbench `batch_id` flow preserved |
| `astral.batch.batch-id-format` | scoped | not-applicable | no batch-id format changes |
| `astral.batch.claim-process-release` | scoped | not-applicable | not dispatcher claim/release |
| `astral.batch.entity-agent-responses-latest-only` | scoped | not-applicable | uses existing `_store_response_block` / agent_data path |
| `astral.config.config-source-of-truth` | scoped | not-applicable | no config edits |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | not-applicable | no env/secrets |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | no debug artifacts |
| `astral.debug.spikes-under-debug-dir` | scoped | not-applicable | no spikes |
| `astral.dispatch.seed-auto-false` | scoped | not-applicable | no dispatch seed |
| `astral.dispatch.run-next-is-chain-authority` | scoped | not-applicable | no `run_next` changes |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | single feature doc for AST-1393 |
| `astral.git.betty-no-src-or-features` | scoped | not-applicable | Betty merge-tests only on test paths |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | product commit `7fed10d1` touches `src/` only; tests via `merge-tests(AST-1393)` |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | core-only product change |
| `astral.layers.import-direction` | scoped | conforms | no new imports; existing `get_logger` |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | no scripts |
| `astral.layers.ui-config-driven-business-logic` | scoped | not-applicable | no UI |
| `astral.idioms.coat-check-never-store-empty` | scoped | not-applicable | RESPONSE store, not coat-check lazy fetch |
| `astral.idioms.render-verdict-orchestrates-consult` | scoped | not-applicable | no consult/render |
| `astral.idioms.require-auth-on-protected-endpoints` | scoped | not-applicable | no API surface |
| `astral.seed.agent-tables-in-repo-json` | scoped | not-applicable | no seed |
| `astral.seed.archie-catalog-wins` | scoped | not-applicable | no seed |
| `astral.seed.boot-only-not-hot-path` | scoped | not-applicable | no seed/boot |
| `astral.seed.define-approved` | scoped | not-applicable | no seed |
| `astral.seed.operator-rows-stay-deleted` | scoped | not-applicable | no seed |
| `astral.seed.other-via-coverage-join` | scoped | not-applicable | no seed |
| `astral.standards.data-raises-caller-logs` | scoped | conforms | stringify in core before data; `save_agent_data` still text-only |
| `astral.standards.database-header-inventory` | scoped | not-applicable | no DB/schema |
| `astral.standards.debug-contract-gated` | scoped | conforms | Style D gated on `debug=True`; `debug_index` / `debug_detail` / `debug_detail_block` |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | reuses `_caller_response_blob`, no second helper |
| `astral.standards.in-scope-only` | scoped | conforms | single call site; Admin HTTP/React / `do_task` untouched |
| `astral.standards.logging-via-utils` | scoped | conforms | `get_logger(__name__, debug_flag=True)` |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | applies to `src/**` only; product symbols unchanged |
| `astral.standards.no-cross-contamination` | scoped | conforms | no unrelated subsystem edits |
| `astral.standards.no-hardcoded-sets` | scoped | not-applicable | no hardcoded sets |
| `astral.standards.public-then-helpers` | scoped | not-applicable | no new public API surface |
| `astral.standards.utils-data-late-import-only` | scoped | not-applicable | no utils changes |
| `astral.state.core-decides-transitions` | scoped | not-applicable | no state transitions |
| `astral.state.job-prior-states-enforced` | scoped | not-applicable | no job states |
| `astral.state.no-daisy-chain-in-run` | scoped | not-applicable | no run chain |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | no frontend |
| `astral.ui.naming-conventions` | scoped | not-applicable | no UI |
| `astral.ui.single-gunicorn-worker` | scoped | not-applicable | no server config |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | `merge-tests(AST-1393): origin/tests 4667aad` |
| `orch.git.commit-vocabulary` | universal | conforms | `code` / `docs` / `test` / `merge-tests` vocabulary |
| `orch.git.flow-direction-inviolable` | universal | conforms | sub branch off ftr epic topology |
| `orch.git.ftr-sub-topology` | universal | conforms | `sub/AST-1392/AST-1393-…` |
| `orch.git.merge-on-checkout` | universal | conforms | no checkout violations observed |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | linear commits |
| `orch.git.no-dev-agent-branches` | universal | conforms | publish ref on `sub/…` |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | AST-1392 worktree |
| `orch.git.three-permanent-branches` | universal | conforms | dev/tests/sub flow |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | no product-policy forks |
| `orch.pipeline.plan-is-bible` | universal | conforms | implementation matches Joan-approved Stage 1 |
| `orch.pipeline.project-scoped-queues` | universal | conforms | n/a to diff |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Tests Passed → review gate satisfied |
| `orch.roles.archie-approves-statutes` | universal | conforms | n/a |
| `orch.roles.betty-owns-test-tree` | universal | conforms | Betty landed tests + bible; engineer did not author test-tree in `code()` commit |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | assignee Ada |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Ada still assignee at Tests Passed |
| `orch.roles.pre-commit-path-bans` | universal | conforms | no ban evasion observed |

**C4 straggler:** Joan plan-rubric APPROVED attached; no `Excluded` statute list in artifact — nothing to straggle.

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| none cited | — | plan cites statutes (`dry-and-focused-functions`, `data-raises-caller-logs`), not `canon/patterns/**` catalog entries |

## Plan adherence

Stage 1 implemented verbatim in `run_adhoc_workbench_test` success path (`src/core/agent.py` ~3548–3587): extract `agent_payload` when present → `_caller_response_blob(body)` → `_store_response_block` with `str`; Style D (`debug_index` 1/1, identifier=`workbench_task_key`, found type/shape, `debug_detail_block(response_text)`) only when `debug=True`; failure branch, `do_task`, Admin API/React, and data-layer contract unchanged. Empty `{}`/`[]` now persist as `"{}"`/`"[]"` per documented plan decision (not the old `or ""` collapse). Estimate **2** matches footprint. Sibling #2 boundary respected — no `api_admin` or frontend diffs.

Betty manifest (`TestAst515AdhocWorkbenchLedger`, `TestAst1393SerializeAdhocSuccessBody`) aligns with `docs/test-bible/core/agent.md` AST-1393 rows: object/list/str/plain-text/empty cases, debug Style D, `debug=False` quiet.

### C6 judgment aids (§5a–§5g)

| Lens | Result |
|------|--------|
| Imports (B1) | OK — no new imports |
| Layer compliance (B2) | OK — core-only |
| Silent failure (D2) | Pre-existing `except Exception: logger.debug("_store_response_block failed")` retained per plan; see advisory |
| Fallbacks (D3) | OK — intentional `{}`/`[]` JSON text per plan decision |
| Logging (E1) / §5f debug | OK — gated Style D; no `[DEBUG]` hand-roll |
| Cross-ticket (§5d) | OK — sibling #2 scope not smuggled |
| §5g external | n/a — no `src/external/` diff |

## Findings

### advisory — broad `except` log label
- **Location:** `src/core/agent.py` `run_adhoc_workbench_test` success-path `try`/`except` (~3554–3587)
- **Finding:** The `try` now wraps `_caller_response_blob`, debug emission, and `_store_response_block`, but the `except` message remains `"_store_response_block failed"`. Serialize/debug failures would log under that label. Plan-mandated structure; `_caller_response_blob` is unlikely to raise on normal payloads.
- **Recommendation:** No fix-now. Optional follow-up (out of AST-1393 scope): widen message to `"adhoc success serialize/store failed"` if this path ever needs sharper ops signal.

### advisory — store failure still yields COMPLETED ledger
- **Location:** same function, post-`except` ledger update (~3591–3601)
- **Finding:** Pre-existing: swallowed store exception does not flip ledger to FAILED. Not introduced by this ticket.
- **Recommendation:** Defer; not AST-1393 scope.

## What's solid

- Root cause fix is minimal and at the right layer: stringify before the data contract, not weakening `save_agent_data`.
- Reuses `_caller_response_blob` — same JSON habit as elsewhere in `agent.py`.
- Betty tests cover the crash repro (object payload → compact JSON `str`), regression (string payload unchanged), and debug contract without log-string golden brittleness.
- Debug instrumentation matches AST-538 Style D: index 1/1, found→recorded, gated on `debug=True`.

## Frame diff

(none) — diff matches Joan-approved plan Stage 1; no scope/frame drift.

## Notes

- Joan plan-rubric: APPROVED @ `2a87dcd5`; no excluded-statute table in attachment.
- UAT note for Chuckles/Susan: AC1 “workbench shows JSON text” display parity is sibling #2; this ticket delivers store-side stringify + debug only.

context_tokens≈28000
