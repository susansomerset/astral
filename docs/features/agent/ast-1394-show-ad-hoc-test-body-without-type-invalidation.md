<!-- linear-archive: AST-1394 archived 2026-08-31 -->

## Linear archive (AST-1394)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1394/show-ad-hoc-test-body-without-type-invalidation-ad-hoc-agent-is  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** katherine  
**Priority / estimate:** None / 2  
**Parent:** AST-1392 — Ad hoc Agent is failing  
**Blocked by / blocks / related:** parent: AST-1392

### Description

## What this implements

After #1, the Admin Test response returns that same text, and the workbench displays it (pretty-printed when it is JSON). A successful provider reply must never be replaced with a type or schema error overlay. Does **not** own persist, debug contract, or production ingest.

## Citations

`pattern.ui.admin-endpoint`; `pattern.layers.import-discipline`; `astral.layers.import-direction`; `astral.standards.in-scope-only`.

## Acceptance criteria

- [X] An Agent Ad Hoc Test whose model returns a successful JSON envelope with an object payload (the `craft_company_search_terms` shape in the original brief) completes as success: the workbench shows the payload as JSON text, and no `_store_response_block failed` / `block_data must be a str` traceback appears for that run.
- [X] A successful reply that is already plain text still displays and stores as that text — no extra JSON wrapping.
- [X] A provider/API failure still surfaces as a failed Test (error shown; no fake success body).

## Boundaries

Does **not** own persist, debug contract, or production ingest (sibling #1). Does **not** change Preview, dispatch batch apply, or other Admin pages except Agent Ad Hoc Test display of the returned body. Does **not** invent a new envelope: when a payload key is present, display that payload body (JSON text if structured); when it is absent, display the raw reply text.

## Notes for planning

After sibling #1. Thin Admin Test surface returns the serialized body; React renders it. UI does not call data.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1392-ad-hoc-agent-is-failing`, child `sub/AST-1392/AST-1394-show-ad-hoc-test-body-without-type-invalidation`. Created at dispatch-parent.

## QA test manifest

1. Existing string/numeric HTTP + 500: `tests/component/ui/api/test_api_admin.py::TestAdhocRoutes::test_adhoc_preview_and_test`
2. Object/list/plain stringify + failure envelope: `tests/component/ui/api/test_api_admin.py::TestAst1394AdhocTestResponseText`
3. Routed Agent Ad Hoc page (**§6c**) + object/plain/failure chrome: `tests/component/frontend/pages/test_AdminAnthropicAdHoc.test.tsx`

**Broken / obsolete:** none.

**Integration:** none revised.

**Narrowed run:**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_admin.py::TestAdhocRoutes::test_adhoc_preview_and_test \
  tests/component/ui/api/test_api_admin.py::TestAst1394AdhocTestResponseText \
  -q
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminAnthropicAdHoc.test.tsx
```

**Pass criterion:** pytest + Vitest green on manifest lines — not zero-arg harness / branch-lock gate.

**Bible shasums** (`origin/sub/AST-1392/AST-1394-show-ad-hoc-test-body-without-type-invalidation`):

* `docs/test-bible/ui/api/api_admin.md` `8749badfc3db0fa7fe3c8b2a98ce8edf179a2631`
* `docs/test-bible/frontend/pages.md` `947b561898651125cf3cfd397fa2a2ddb29d6839`

### Comments

#### radia — 2026-08-16T02:18:41.661Z
[code-rubric] PROCEED (Commit: c4c22d2d) display overlay clean

#### betty — 2026-08-16T02:12:51.710Z
`origin/sub/AST-1392/AST-1394-show-ad-hoc-test-body-without-type-invalidation` @ `c4c22d2d` · display without type invalidation

#### joan — 2026-08-16T02:02:14.697Z
[plan-rubric] PROCEED (Commit: eed6751e) display without invalidation

#### katherine — 2026-08-16T01:59:07.504Z
`origin/sub/AST-1392/AST-1394-show-ad-hoc-test-body-without-type-invalidation` @ `eed6751e` · plan ready

---

# Show Ad Hoc Test body without type invalidation

- **Linear:** [AST-1394](https://linear.app/astralcareermatch/issue/AST-1394)
- **Parent:** [AST-1392](https://linear.app/astralcareermatch/issue/AST-1392)
- **Publish ref:** `sub/AST-1392/AST-1394-show-ad-hoc-test-body-without-type-invalidation`

After sibling #1 (`AST-1393`) the workbench success path already stringifies an object/list payload to compact JSON text via `_caller_response_blob` before the RESPONSE write, and leaves `result["parsed_response"]` as the original envelope. This ticket is the Admin Test overlay: `POST /api/admin/adhoc/test` returns that same text as `response_text` (always a `str`), and the Agent Ad Hoc workbench displays it — pretty-printed when it is JSON. A successful provider reply is never replaced with a type or schema error overlay. Provider/API failures still fail the Test.

Does **not** own persist, debug contract, or production ingest (sibling #1 / Boundaries). Does **not** edit `src/core/agent.py` beyond importing the existing stringify helper into the UI API. Does **not** change Preview, dispatch batch apply, or other Admin pages.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/api/api_admin.py` | Import `_caller_response_blob`; stringify Ad Hoc Test success body the same way #1 stores it; `response_text` is always `str` | ui |
| `src/ui/frontend/src/pages/AdminAnthropicAdHoc.tsx` | Coerce a success body to text before `setResponse`; keep existing pretty-print; never treat `success: true` as an `ERROR:` overlay | ui |

Do **not** edit: `src/core/agent.py` (no persist/debug changes), `src/data/database.py`, `do_task` schema validation / AST-1289 coerce, Preview (`/api/admin/adhoc/preview` or the Preview UI), hydrated-output section (stays commented out), `tests/`, bible.

## Stages

### Stage 1: Admin Test HTTP returns serialized body as text

**Done when:** `POST /api/admin/adhoc/test` on a successful workbench result whose `parsed_response` is a JSON envelope with an object `agent_payload` (the `craft_company_search_terms` shape) returns HTTP 200 `{"success": true, "response_text": <str>, ...}` where `response_text` is compact JSON text of that payload — the same string `_caller_response_blob` produces, not a nested JSON object, not a Python `str(dict)` dump. A successful plain-text `parsed_response` (or string `agent_payload`) is returned unchanged (no extra JSON wrapping). A numeric `parsed_response` such as `123` is still `"123"`. A provider/API failure (`success` false or raised exception) still returns HTTP 500 with `{"success": false, "error": ...}` — no fake success body. `python3 -m py_compile src/ui/api/api_admin.py` passes.

1. In `src/ui/api/api_admin.py`, add `_caller_response_blob` to the existing `src.core.agent` import (do **not** add a new import block, do **not** import from `src.data` for this ticket):

   ```python
   from src.core.agent import (
       run_adhoc_workbench_test,
       _decode_payload,
       resolved_agent_content,
       resolved_task_system,
       _chain_context,
       _caller_response_blob,
   )
   ```

2. In `adhoc_test`, after the existing `if not result.get("success"):` 500 return and **before** `timesheet = result.get("timesheet", {})`, replace **only** this success-body extraction:

   ```python
       response_text = result.get("parsed_response") or ""
       # For tasks with JSON envelope, do_task auto-extracts agent_payload into parsed_response.
       # If it's still a dict here (e.g. run_adhoc doesn't do the extraction), pull it out.
       if isinstance(response_text, dict) and "agent_payload" in response_text:
           response_text = response_text["agent_payload"] or ""
       if not isinstance(response_text, str):
           response_text = str(response_text)
   ```

   with this exact sequence:

   ```python
       parsed = result.get("parsed_response")
       if isinstance(parsed, dict) and "agent_payload" in parsed:
           body = parsed["agent_payload"]
       else:
           body = parsed
       response_text = _caller_response_blob(body)
   ```

   Leave the encoded `_decode_payload` block and the `return jsonify({"success": True, "response_text": response_text, "hydrated": hydrated, "timesheet": timesheet})` unchanged. `response_text` is always a `str` (compact JSON for dict/list via `_caller_response_blob`; otherwise `str(body)` or `""` for `None`). Flask therefore emits a JSON **string** field, not a nested object.

3. Do **not** pretty-print in the API (`indent=`). Compact JSON matches the RESPONSE text sibling #1 stored. React pretty-prints for display (Stage 2).

4. Do **not** use `parsed_response or ""` before the extract — an empty dict/list is falsy and would collapse to `""`. Empty dict/list become `"{}"` / `"[]"` (same as #1). Do **not** wrap an already-`str` body in extra JSON quotes.

5. Do **not** change the failure branches (`except Exception` → 500, `if not result.get("success")` → 500). Do **not** change `_resolve_adhoc`, Preview, `run_adhoc_workbench_test` arguments, `@require_admin`, or `hydrated`. Do **not** call `database` / `save_agent_data` from this route. Do **not** add schema validation on this overlay — a successful provider reply stays `success: True` even when the payload would fail production `do_task` ingest.

6. Do **not** edit `tests/` or `docs/test-bible/**`. Existing component cases that assert `response_text == "payload"` (string `agent_payload`) and `response_text == "123"` (numeric `parsed_response`) stay valid. Betty owns any new object-payload HTTP coverage.

⚠️ **Decision:** Import `_caller_response_blob` rather than a second `json.dumps` in `api_admin.py` or a new public helper in `agent.py`. The UI layer already imports private agent helpers (`_decode_payload`, `_chain_context`). One stringify habit means HTTP `response_text` equals the stored RESPONSE body (`astral.standards.dry-and-focused-functions`). UI still does not call data (`pattern.layers.import-discipline` / `astral.layers.import-direction`).

⚠️ **Decision:** Keep extracting `agent_payload` when that key is present, then stringify **that** body — not the full `{agent_performance, agent_payload}` envelope. Parent: when a payload key is present, display that payload body. Same extract as #1.

### Stage 2: Workbench displays the body; success is never an ERROR overlay

**Done when:** On `POST /api/admin/adhoc/test` HTTP 200 with `success: true`, the Agent Ad Hoc **Response** `<pre>` shows the payload as text. When `response_text` is compact JSON (object payload from Stage 1), the existing `formatResponse` pretty-prints it (`JSON.stringify(..., null, 2)`). When `response_text` is already plain text, it displays unchanged. If `response_text` is a nested object/list (defense — Stage 1 should not emit this), it is coerced to JSON text and shown — React does **not** throw (`response.startsWith` / “Objects are not valid as a React child”) and does **not** replace it with `ERROR: …`. HTTP `!ok` / `success: false` still set `ERROR: …` (red overlay). Preview UI is unchanged.

1. In `src/ui/frontend/src/pages/AdminAnthropicAdHoc.tsx`, immediately **above** the existing `formatResponse` helper, add this function (do **not** change `formatResponse` itself):

   ```tsx
     function responseBodyToText(body: unknown): string {
       if (typeof body === "string") return body
       if (body == null) return ""
       try { return JSON.stringify(body) } catch { return String(body) }
     }

     function formatResponse(text: string): string {
       try { return JSON.stringify(JSON.parse(text), null, 2) } catch { return text }
     }
   ```

   `JSON.stringify` without `indent` — compact text in state; `formatResponse` at render still pretty-prints JSON strings. `body == null` covers both `null` and `undefined`.

2. In `handleTest`, inside `.then(data => { ... })`, replace **only** the success assignment:

   ```tsx
           if (data.success) {
             setResponse(data.response_text)
             setTimesheet(data.timesheet || null)
           } else {
             setResponse(`ERROR: ${data.error || "Unknown error"}`)
           }
   ```

   with:

   ```tsx
           if (data.success) {
             setResponse(responseBodyToText(data.response_text))
             setTimesheet(data.timesheet || null)
           } else {
             setResponse(`ERROR: ${data.error || "Unknown error"}`)
           }
   ```

   Leave the `if (!r.ok)` throw, the `.catch(e => setResponse(\`ERROR: ${e.message}\`))`, `setTesting`, timesheet display, and the Response `<pre>` (including `response.startsWith("ERROR:")` color and `{formatResponse(response)}`) unchanged. `setResponse` always receives a `string` on the success path, so `startsWith` stays valid.

3. Do **not** set `ERROR:` when `data.success` is true, even if `response_text` is an object, list, number, or empty. Do **not** add schema / type validation in this page. Do **not** re-enable the commented hydrated-output section. Do **not** change Preview, Save As, prompt tabs, or other Admin pages. Do **not** add a display truncation / length cap on the Response `<pre>` (existing `maxHeight: 600` overflow stays).

4. Do **not** edit `tests/` or `docs/test-bible/**`. Existing frontend case that posts `response_text: "{\"ok\":true}"` and asserts pretty-printed `"ok": true` stays valid. Betty owns any new object-payload chrome coverage.

⚠️ **Decision:** Pretty-print in React, not in the API. HTTP `response_text` stays compact so it matches the stored RESPONSE; the workbench pretty-prints at render via the existing `formatResponse` (`pattern.ui.admin-endpoint`: API returns the resolved body; React renders it).

⚠️ **Decision:** Coerce-to-string on the success path even after Stage 1 always returns a `str`. That is the type-invalidation guard: a nested JSON object in `response_text` must still display as JSON text, never crash the page or become an `ERROR:` overlay. Failure overlays stay reserved for HTTP/`success: false`.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Traceability

AC1 workbench shows JSON text / no type overlay → S1 + S2 | AC2 plain-text display → S1 + S2 | AC3 provider failure still failed Test → S1 (500) + S2 (`ERROR:`)
(AC persist / debug / production ingest → sibling #1, not this plan)

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
revision: 1
**Ticket:** AST-1394
**Overall:** APPROVED
**Publish ref:** `sub/AST-1392/AST-1394-show-ad-hoc-test-body-without-type-invalidation` @ `eed6751e`

## Traceability
AC1 workbench shows JSON text / no type overlay → S1 + S2 (persist/traceback → sibling #1) | AC2 plain-text display → S1 + S2 (store → sibling #1) | AC3 provider failure still failed Test → S1 (500) + S2 (`ERROR:`)

## Findings

### acceptable — AC1 traceback / AC2 store clauses
- **Location:** Child Description AC1–AC2; plan `## Traceability` footer
- **Finding:** Ticket AC text still quotes persist/traceback language from the parent epic; this plan correctly limits scope to Admin HTTP + React display. Boundaries and traceability defer store/debug to AST-1393.
- **Recommendation:** No plan change. Full epic UAT needs #1 landed first for store/traceback; #2 UAT verifies `response_text` is always `str` and the Response `<pre>` never type-invalidates on `success: true`.

### acceptable — duplicate extract+stringify in API
- **Location:** Stage 1; sibling #1 leaves `result["parsed_response"]` as the original envelope
- **Finding:** `agent_payload` extract mirrors core workbench logic because #1 does not expose serialized text on `result`. Importing `_caller_response_blob` keeps the stringify habit aligned with stored RESPONSE text.
- **Recommendation:** Acceptable given the sibling split. Optional future refactor (out of scope): core returns a dedicated `response_text` field — not required for this ticket.

context_tokens≈17500

## Review (build stub)

**Publish ref:** `origin/sub/AST-1392/AST-1394-show-ad-hoc-test-body-without-type-invalidation`
**Tip (pre-review):** `f685256e`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `e5d49eb9` | Admin Test HTTP `response_text` via `_caller_response_blob` (compact JSON text of payload) |
| 2 | `f685256e` | Workbench coerces success body to text before `setResponse`; existing `formatResponse` pretty-prints JSON |

## Radia review — AST-1394

**Rubric:** code-rubric.v1  
**Ticket:** AST-1394  
**Publish ref:** `origin/sub/AST-1392/AST-1394-show-ad-hoc-test-body-without-type-invalidation` @ `c4c22d2d`  
**Overall:** CLEAN  
**Diff baseline:** `origin/dev...origin/sub/AST-1392/AST-1394-show-ad-hoc-test-body-without-type-invalidation` (11 files; includes stacked AST-1393 predecessor on this sub tip)

**AST-1394 product delta** (commits `e5d49eb9`, `f685256e`): `src/ui/api/api_admin.py`, `src/ui/frontend/src/pages/AdminAnthropicAdHoc.tsx` only — no `src/core/agent.py` edits in 1394 code commits (agent.py changes in the three-dot diff are AST-1393, already PROCEED @ `a45fff61`).

## Statutes checked

63 active statutes per `canon/statutes/README.md` § Harvested corpus.

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | not-applicable | no grade/confidence paths |
| `astral.agent.do-task-delegation` | scoped | not-applicable | no `do_task` changes in 1394 delta |
| `astral.agent.grade-vector-validation` | scoped | not-applicable | no schema validation added |
| `astral.batch.batch-id-first` | scoped | not-applicable | no batch claim changes |
| `astral.batch.batch-id-format` | scoped | not-applicable | no batch-id format changes |
| `astral.batch.claim-process-release` | scoped | not-applicable | not dispatcher claim/release |
| `astral.batch.entity-agent-responses-latest-only` | scoped | not-applicable | no agent_data write path in 1394 delta |
| `astral.config.config-source-of-truth` | scoped | not-applicable | no config edits |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | not-applicable | no env/secrets |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | no debug artifacts |
| `astral.debug.spikes-under-debug-dir` | scoped | not-applicable | no spikes |
| `astral.dispatch.seed-auto-false` | scoped | not-applicable | no dispatch seed |
| `astral.dispatch.run-next-is-chain-authority` | scoped | not-applicable | no `run_next` |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | single AST-1394 feature doc |
| `astral.git.betty-no-src-or-features` | scoped | not-applicable | Betty merge-tests on test paths only |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | engineer `code()` commits touch `src/ui/` only; tests via `merge-tests(AST-1394)` |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | UI overlay only; no external imports |
| `astral.layers.import-direction` | scoped | conforms | `ui → core` import of `_caller_response_blob` matches existing `_decode_payload` / `_chain_context` habit; plan-approved |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | no scripts |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | no new hardcoded job/candidate state lists |
| `astral.idioms.coat-check-never-store-empty` | scoped | not-applicable | display overlay, not coat-check |
| `astral.idioms.render-verdict-orchestrates-consult` | scoped | not-applicable | no consult/render |
| `astral.idioms.require-auth-on-protected-endpoints` | scoped | conforms | `adhoc_test` retains `@require_admin` |
| `astral.seed.agent-tables-in-repo-json` | scoped | not-applicable | no seed |
| `astral.seed.archie-catalog-wins` | scoped | not-applicable | no seed |
| `astral.seed.boot-only-not-hot-path` | scoped | not-applicable | no seed/boot |
| `astral.seed.define-approved` | scoped | not-applicable | no seed |
| `astral.seed.operator-rows-stay-deleted` | scoped | not-applicable | no seed |
| `astral.seed.other-via-coverage-join` | scoped | not-applicable | no seed |
| `astral.standards.data-raises-caller-logs` | scoped | conforms | route does not call `save_agent_data`; stringify before JSON response |
| `astral.standards.database-header-inventory` | scoped | not-applicable | no DB/schema |
| `astral.standards.debug-contract-gated` | scoped | not-applicable | no new debug-contract emission in 1394 delta |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | reuses `_caller_response_blob`; no second `json.dumps` in API |
| `astral.standards.in-scope-only` | scoped | conforms | Admin Test HTTP + React chrome only; Preview/dispatch/other pages untouched |
| `astral.standards.logging-via-utils` | scoped | not-applicable | no new logging |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | applies to `src/**`; no new ticket-id symbols in product code |
| `astral.standards.no-cross-contamination` | scoped | conforms | scoped to Ad Hoc Test overlay |
| `astral.standards.no-hardcoded-sets` | scoped | not-applicable | no hardcoded sets |
| `astral.standards.public-then-helpers` | scoped | not-applicable | no file layout churn |
| `astral.standards.utils-data-late-import-only` | scoped | not-applicable | no utils changes |
| `astral.state.core-decides-transitions` | scoped | not-applicable | no state transitions |
| `astral.state.job-prior-states-enforced` | scoped | not-applicable | no job states |
| `astral.state.no-daisy-chain-in-run` | scoped | not-applicable | no run chain |
| `astral.ui.frontend-file-placement` | scoped | conforms | change in existing `AdminAnthropicAdHoc.tsx` |
| `astral.ui.naming-conventions` | scoped | conforms | `responseBodyToText` follows page conventions |
| `astral.ui.single-gunicorn-worker` | scoped | not-applicable | no server config |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | `merge-tests(AST-1394): origin/tests 322c490` |
| `orch.git.commit-vocabulary` | universal | conforms | `code` / `docs` / `test` / `merge-tests` |
| `orch.git.flow-direction-inviolable` | universal | conforms | sub off AST-1392 ftr |
| `orch.git.ftr-sub-topology` | universal | conforms | `sub/AST-1392/AST-1394-…` |
| `orch.git.merge-on-checkout` | universal | conforms | no violations observed |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | linear commits |
| `orch.git.no-dev-agent-branches` | universal | conforms | publish ref on `sub/…` |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | AST-1392 worktree |
| `orch.git.three-permanent-branches` | universal | conforms | dev/tests/sub flow |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | no product-policy forks |
| `orch.pipeline.plan-is-bible` | universal | conforms | Stages 1–2 match Joan-approved plan |
| `orch.pipeline.project-scoped-queues` | universal | conforms | n/a to diff |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Tests Passed gate satisfied |
| `orch.roles.archie-approves-statutes` | universal | conforms | n/a |
| `orch.roles.betty-owns-test-tree` | universal | conforms | Betty tests + bible; engineer did not author test-tree in `code()` |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | assignee Katherine |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Katherine still assignee |
| `orch.roles.pre-commit-path-bans` | universal | conforms | no ban evasion |

**C4 straggler:** Joan plan-rubric APPROVED attached; no `Excluded` statute list — nothing to straggle.

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| none cited | — | plan references `pattern.layers.import-discipline` / `pattern.ui.admin-endpoint` in decisions; no `canon/patterns/**` catalog ids in Architectural definition |

## Plan adherence

**Stage 1** (`api_admin.py` `adhoc_test` ~1474–1479): `agent_payload` extract → `_caller_response_blob(body)` → always-`str` `response_text`; failure branches, `_decode_payload` / `hydrated`, Preview, and `run_adhoc_workbench_test` args unchanged. Empty `{}`/`[]` → `"{}"`/`"[]"` (not falsy collapse). Regression cases `"payload"` / `"123"` preserved in existing `TestAdhocRoutes`.

**Stage 2** (`AdminAnthropicAdHoc.tsx`): `responseBodyToText` added above `formatResponse`; success path `setResponse(responseBodyToText(data.response_text))`; `formatResponse` + `ERROR:` overlay logic unchanged. Nested-object defense tested.

**Boundaries:** No `src/core/agent.py` persist/debug edits in 1394 code commits. No Preview, `do_task` coerce, or schema overlay on success. Estimate **2** matches footprint.

**Cross-ticket (AST-1393):** Duplicate extract+stringify in API is plan-documented and acceptable — HTTP `response_text` aligns with stored RESPONSE text when both use `_caller_response_blob` + same extract. Predecessor #1 on sub tip is expected for stacked epic work.

**Betty manifest** aligns with bible: `TestAst1394AdhocTestResponseText` + `TestAdhocRoutes` (API); `test_AdminAnthropicAdHoc.test.tsx` AST-1394 cases (object/plain/nested/ERROR).

### C6 judgment aids (§5a–§5g)

| Lens | Result |
|------|--------|
| Imports (B1) | OK — one symbol added to existing `src.core.agent` import block |
| Layer compliance (B2) | OK — `ui → core`; no `ui → data` for stringify |
| Silent failure (D2) | OK — pre-existing `except` on encoded `_decode_payload` unchanged; no new swallows |
| Fallbacks (D3) | OK — intentional `{}`/`[]` JSON text; `responseBodyToText` null guard |
| Logging (E1) / §5f | n/a — no new debug emission |
| Config/state in UI (G1) | OK |
| Cross-ticket (§5d) | OK — #1 persist scope not re-smuggled; #2 display-only |
| §5g external | n/a |

## Findings

### advisory — duplicate stringify vs AST-1393 core path
- **Location:** `src/ui/api/api_admin.py` `adhoc_test` (~1474–1479); mirrors `run_adhoc_workbench_test` in AST-1393
- **Finding:** Extract + `_caller_response_blob` duplicated because #1 leaves `parsed_response` as the original envelope. Joan flagged acceptable; drift risk if one call site changes without the other.
- **Recommendation:** No fix-now. Optional future refactor (out of epic scope): core returns `response_text` on `result` for overlay consumption.

### advisory — misleading Stage 2 commit message
- **Location:** git `f685256e` message says “workbench” / implies `agent.py`; diff is `AdminAnthropicAdHoc.tsx` only
- **Finding:** Commit archaeology only; code is correct.
- **Recommendation:** None for resolve-child.

### advisory — `body` variable reuse in `adhoc_test`
- **Location:** `api_admin.py` ~1436 vs ~1476–1478
- **Finding:** Request `body` dict shadowed by payload `body` after success extract. Harmless — request fields already consumed.
- **Recommendation:** Optional rename to `payload_body` in a hygiene pass; not blocking.

## What's solid

- Fixes the type-invalidation failure mode at both layers: API always emits `response_text` as `str`; React coerces nested objects before `setResponse`, so `response.startsWith("ERROR:")` stays safe.
- Pretty-print stays in React (`formatResponse`); API returns compact JSON matching stored RESPONSE text from #1.
- Betty tests cover object/list/empty/plain/numeric HTTP cases and frontend success/failure/nested-object defense without golden log strings.
- Engineer respected test-tree ownership and plan boundaries (UI-only product commits).

## Frame diff

(none) — AST-1394 implementation matches Joan-approved Stages 1–2; no scope/frame drift.

## Notes

- Three-dot diff vs `origin/dev` includes AST-1393 files (agent.py, AST-1393 tests/docs) because sub branch stacks on #1; Radia AST-1393 verdict was PROCEED — no regression observed in combined tip.
- Joan plan-rubric: APPROVED @ `eed6751e`; no excluded-statute table.
- Epic UAT: verify object-payload Test shows pretty-printed JSON in Response `<pre>`, no `ERROR:` on `success: true`, and provider failure still red `ERROR:` overlay.

context_tokens≈22000
