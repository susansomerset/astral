# AST-1312 — Mailbox To on list and get payloads

**Linear:** [AST-1312](https://linear.app/astralcareermatch/issue/AST-1312/mailbox-to-on-list-and-get-payloads-email-bind-where-email-is-in-the)
**Parent:** [AST-1308](https://linear.app/astralcareermatch/issue/AST-1308/email-bind-where-email-is-in-the-to-field-alone) — Email bind where email is in the To: field (alone)
**Publish ref:** `origin/sub/AST-1308/AST-1312-mailbox-to-on-list-and-get-payloads`

Inbox list and get payloads already carry the raw **From** header as `from_address`. This ticket adds the raw **To** header the same way so sibling **AST-1313** (From-then-To bind) can see it. This ticket does **not** decide bind order, ignore the Astral inbox address, emit bind-source debug, or change Manage Email chrome.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/external/gmail.py` | Add `to_address` on `GmailInboxMessage` and `GmailMessageHtml`; request `To` on list metadata; copy the raw To header on list and get (empty string if missing) | external |

**No changes expected:** `src/core/inbox.py` (`list_inbox_messages` already does `row = dict(msg)` so `to_address` passes through; `get_message_html` already returns the external TypedDict as-is), `src/ui/api/api_inbox.py` (jsonify already forwards those dicts), `src/core/gaze_email.py`, `src/core/candidate.py`, `src/utils/config.py`, `src/ui/frontend/src/pages/AdminManageEmail.tsx` (extra JSON keys are ignored; chrome is out of scope), `tests/` / `docs/test-bible/**` (Betty after Code Complete).

**Do not add files.** If a step below cannot be executed in `src/external/gmail.py` alone, stop and comment on **AST-1308** with the stage-blocked template.

## Stage 1: Raw To on Gmail list and get shapes

**Done when:** `list_inbox_messages()` rows and `get_message_html()` payloads include `to_address` as the raw `To` header string (empty string when the header is missing or unreadable), using the same `_header_map` path as `from_address`; list metadata get requests include `"To"` so the header is actually present on `format="metadata"` responses; From bind / `candidate_match` / create rematch / archive / trash / Manage Email chrome are unchanged. `python3 -m py_compile src/external/gmail.py` succeeds (repo venv: `~/astral/.venv/bin/python` if present, else `python3`).

1. In `src/external/gmail.py`, extend `GmailInboxMessage` — insert `to_address: str` immediately after `from_address` (keep `date` / `unread` / `internal_date_ms` where they are):

```python
class GmailInboxMessage(TypedDict):
    id: str
    thread_id: str
    subject: str
    from_address: str
    to_address: str
    date: str
    unread: bool
    internal_date_ms: int
```

2. In the same file, extend `GmailMessageHtml` — insert `to_address: str` immediately after `from_address`:

```python
class GmailMessageHtml(TypedDict):
    id: str
    html_body: str
    subject: str
    from_address: str
    to_address: str
```

3. In `list_inbox_messages`, change the metadata get to request To as well:

```python
                metadataHeaders=["Subject", "From", "Date", "To"],
```

Add a one-line comment on that list: list `format="metadata"` only returns named headers — without `"To"`, `to_address` would always be empty on list rows.

4. In `_message_metadata`, after the existing `from_address` line, set:

```python
        "to_address": headers.get("to", ""),
```

Do **not** parse, split, lowercase, or strip display names. Do **not** drop the Astral inbox address. The value is the raw header string Gmail returned (same contract as `from_address`, which today can be `"Ada <ada@ex.com>"`).

5. In `get_message_html`, add `"to_address": headers.get("to", "")` to the returned dict (after `from_address`). Update the function docstring from “HTML body + Subject/From” to “HTML body + Subject/From/To”. `format="full"` already returns all headers; do **not** add a second Gmail get.

⚠️ **Decision — raw `to_address` string, not a parsed address list:** Ticket notes say this child only exposes the raw To field. Parent AC 2 (single remaining address after ignoring the Astral inbox) and bind-source debug belong to **AST-1313**. Parsing here would invent the sibling’s contract and risk two To-normalizers.

⚠️ **Decision — external-only; no core/API/React edits:** Core list already copies every external key; core get already returns `GmailMessageHtml`; the admin API already jsonifies those dicts. A core wrapper that re-sets `to_address` would be duplicate. Changing `_candidate_match_for_from`, `create_meteorite_job_from_inbox_message` rematch, or Manage Email columns would absorb **AST-1313** / chrome that this ticket forbids.

6. Do **not** change `_candidate_match_for_from`, `count_inbox_bound_by_candidate`, `create_meteorite_job_from_inbox_message`, gaze_email bind consumers, or any `debug=` Style D lines. Existing From-only bind must keep behaving exactly as today.

7. Compile: `python3 -m py_compile src/external/gmail.py`.

### Betty will need (not this ticket’s commit)

Exact-equality fixtures in `tests/component/external/test_gmail.py` (`TestListInboxMessages.test_paginates_and_preserves_order`, `test_non_dict_metadata_payload_yields_empty_fields`, `TestGetMessageHtml` exact dicts) will fail until they include `"to_address"`. `test_includes_subject_and_from_headers` should also assert a To header when Betty adds one to that fixture. Engineer does **not** edit `tests/` or `docs/test-bible/**`.

## Execution contract

The plan is binding. The agent:

- Executes steps in order within the stage.
- Does not skip, reorder, combine, or expand steps.
- Does not add files, modules, configs, or dependencies that aren't in the plan.
- When a step is ambiguous, contradicts another step, references something that doesn't exist, or fails when executed literally — **stops, comments on the Linear parent issue, and waits.**
- When the codebase has drifted from what the plan assumes — **stops and comments.** Does not adapt silently.
- Completes the stage on the epic worktree, commits, and publishes to `origin/sub/AST-1308/AST-1312-mailbox-to-on-list-and-get-payloads`.

Blocking comment format (parent **AST-1308**):

```
🛑 Stage N blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

## Self-Assessment

**Scope:** Single-Component — one external module (`src/external/gmail.py`); TypedDict + header copy only; core/UI/bind untouched.

**Conf:** high — identical to the existing `from_address` / `_header_map` / `metadataHeaders` pattern from AST-1032 / AST-1049.

**Risk:** low — additive field with empty-string missing behavior; From bind and ingest consumers keep reading `from_address` / `candidate_match` as they do today. Wrong header name on `metadataHeaders` would leave list `to_address` empty and stall AST-1313, which is why step 3 is explicit.

## Self-review vs ASTRAL_CODE_RULES

| Rule | Verdict |
|------|---------|
| §1.3 DRY | Reuse `_header_map` and the From empty-string missing path; no second To parser. |
| §2.1 config | No new config. Inbox identity / bind-header order are AST-1313. Header name `"To"` sits next to existing `"From"` in the Gmail API call, not a behavior set. |
| §2.4 batch | N/A — no claim/process/release. |
| §2.6 state | N/A — no entity state. |
| §3.3 imports | No new imports; external still imports utils only. |
| §3.5 naming | `to_address` matches `from_address`; snake_case. |

No conflicts. Conf remains **high**.

## Joan validate

[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1312
**Publish ref:** `sub/AST-1308/AST-1312-mailbox-to-on-list-and-get-payloads` @ `a8aa15f`
**Overall:** APPROVED

### Traceability

| Child AC | Plan stage(s) | Definition anchor |
|----------|---------------|-------------------|
| 1 — `list_inbox_messages()` rows include `to_address` = raw `To` header (empty if missing) | Stage 1 steps 1, 3–4 | Child scope: expose To on mailbox rows for sibling bind |
| 2 — `get_message_html()` payloads include `to_address` the same way | Stage 1 steps 2, 5 | Same |
| 3 — From-only `candidate_match` / create rematch unchanged | Stage 1 step 6; “No changes expected” for core | Parent boundary: From-first bind stays; this child does not decide bind |
| 4 — Manage Email chrome unchanged | Stage 1 step 6; no React/API edits | Parent boundary: no new column/chrome |
| 5 — This slice does **not** complete parent AC 2–5 | Explicit boundary + ⚠️ decisions | Parent AC 2–5 owned by **AST-1313** |

| Plan stage | Child AC / boundary |
|------------|---------------------|
| Stage 1 (gmail TypedDict + metadata + get) | AC 1–2 |
| Stage 1 step 6 (no bind/core/UI edits) | AC 3–4 |
| Out of scope / sibling | AC 5; parent AC 2–5 → AST-1313 |

No orphan stages. Parent AC 1–6 correctly deferred to AST-1313 except raw-field prerequisite for AC 2.

### Statute verdicts

| Statute / pattern | Verdict | Rationale |
|-------------------|---------|-----------|
| `pattern.layers.import-discipline` | conforms | To read stays in `src/external/gmail.py`; bind decision untouched in core |
| `astral.layers.import-direction` | conforms | No new imports; external → utils only |
| `astral.layers.core-vs-external-bright-line` | conforms | Header I/O external; `_candidate_match_for_from` unchanged |
| `astral.standards.in-scope-only` | conforms | Single additive field on existing list/get shapes |
| `astral.standards.dry-and-focused-functions` | conforms | Reuses `_header_map` / `_message_metadata`; no parallel To parser |

### Considered and excluded

**Considered:** child **In scope** statutes (above).

**Excluded (boundary / sibling):**
- `pattern.config.config-block` / `astral.config.config-source-of-truth` / `astral.standards.no-hardcoded-sets` — AST-1313 (bind order, inbox identity)
- `astral.standards.debug-contract-gated` — bind-source Style D is AST-1313
- `astral.layers.ui-config-driven-business-logic` — no React To rules
- `pattern.ui.admin-endpoint` / `astral.patterns.require-auth-on-protected-endpoints` — no route changes; existing admin jsonify pass-through
- From-then-To bind, inbox-address filter, To parse/split — AST-1313
- ingest / scrape / create / archive / gaze_email bind consumers — out of slice
- `tests/`, `docs/test-bible/**` — Betty (plan documents expected fixture updates)

### Findings

| Sev | Location | Finding | Recommendation |
|-----|----------|---------|----------------|
| **acceptable** | “Betty will need” | Component tests in `test_gmail.py` use exact dict equality without `to_address`; plan correctly assigns fixture updates to Betty post–Code Complete. | None — already documented. |

**Tip verification:** On worktree @ `a8aa15f`, `metadataHeaders` is `["Subject", "From", "Date"]` (no `"To"`), TypedDicts lack `to_address`, `_message_metadata` / `get_message_html` return only `from_address`. Core `list_inbox_messages` does `row = dict(msg)` and passes external keys through; `get_message_html` returns external TypedDict as-is — plan’s “no core/API/React edits” claim is accurate.

**Self-assessment:** Single-Component / high conf / low risk — honest; mirrors AST-1032/AST-1049 `from_address` pattern; step 3 explicitly guards the list-empty-To failure mode.

context_tokens≈42000
— Joan

## Review (build stub)

**Publish ref:** `origin/sub/AST-1308/AST-1312-mailbox-to-on-list-and-get-payloads`
**Plan path:** `docs/features/meteorite/ast-1312-mailbox-to-on-list-and-get-payloads.md`

**Built tip:** `40612c891d3e7b1a26301dd0faad05366933e15b` (`40612c89`)

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `40612c89` | Raw `to_address` on Gmail list + get shapes |

## Radia review

[code-rubric] revision=2
**Rubric:** code-rubric.v2
**Ticket:** AST-1312
**Publish ref:** `origin/sub/AST-1308/AST-1312-mailbox-to-on-list-and-get-payloads` @ `eb63c656`

**Overall:** CLEAN

**Diff baseline:** `origin/dev...origin/sub/AST-1308/AST-1312-mailbox-to-on-list-and-get-payloads` (4 paths: issue doc, test-bible, `src/external/gmail.py`, `tests/component/external/test_gmail.py`). Engineer code commit `40612c89` touches `gmail.py` only; Betty `2f4d1ad0` + `merge-tests` landed tests/bible per pipeline.

### Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | not-applicable | no agent/grade paths in diff |
| `astral.agent.do-task-delegation` | scoped | not-applicable | no do_task/dispatch changes |
| `astral.agent.grade-vector-validation` | scoped | not-applicable | no grade vector changes |
| `astral.batch.batch-id-first` | scoped | not-applicable | no batch_id usage |
| `astral.batch.batch-id-format` | scoped | not-applicable | no batch_id strings |
| `astral.batch.claim-process-release` | scoped | not-applicable | no claim/process/release |
| `astral.batch.entity-agent-responses-latest-only` | scoped | not-applicable | no entity-agent-response paths |
| `astral.config.config-source-of-truth` | scoped | not-applicable | no config/TASK_CONFIG edits (Joan excluded; diff confirms) |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | not-applicable | no env/secret surface changes |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | no artifacts dir |
| `astral.debug.spikes-under-debug-dir` | scoped | not-applicable | no debug spikes |
| `astral.dispatch.seed-auto-false` | scoped | not-applicable | no dispatch/seed paths |
| `astral.dispatch.run-next-is-chain-authority` | scoped | not-applicable | no run_next/dispatcher changes |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | single issue doc `docs/features/meteorite/ast-1312-…md` |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty commits limited to tests + test-bible |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | engineer `code()` commit is `src/external/gmail.py` only |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | Gmail header I/O stays external; `_candidate_match_for_from` untouched |
| `astral.layers.import-direction` | scoped | conforms | no new imports; external still utils-only |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | no scripts layer |
| `astral.layers.ui-config-driven-business-logic` | scoped | not-applicable | no UI/React (Joan excluded) |
| `astral.idioms.coat-check-never-store-empty` | scoped | not-applicable | no coat-check storage |
| `astral.idioms.render-verdict-orchestrates-consult` | scoped | not-applicable | no render/consult paths |
| `astral.idioms.require-auth-on-protected-endpoints` | scoped | not-applicable | no API route changes (Joan excluded) |
| `astral.seed.agent-tables-in-repo-json` | scoped | not-applicable | no seed tables |
| `astral.seed.archie-catalog-wins` | scoped | not-applicable | no seed catalog |
| `astral.seed.boot-only-not-hot-path` | scoped | not-applicable | no boot/seed hot path |
| `astral.seed.define-approved` | scoped | not-applicable | no define/seed flow |
| `astral.seed.operator-rows-stay-deleted` | scoped | not-applicable | no seed rows |
| `astral.seed.other-via-coverage-join` | scoped | not-applicable | no coverage join |
| `astral.standards.data-raises-caller-logs` | scoped | not-applicable | no data layer |
| `astral.standards.database-header-inventory` | scoped | not-applicable | no DB/migrations |
| `astral.standards.debug-contract-gated` | scoped | not-applicable | no `debug=` emission added (Joan excluded for AST-1313) |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | reuses `_header_map` + same empty-string missing path as `from_address` |
| `astral.standards.in-scope-only` | scoped | conforms | single additive field; bind/core/UI deferred to AST-1313 |
| `astral.standards.logging-via-utils` | scoped | conforms | no new logging/print |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | `to_address` mirrors `from_address` naming |
| `astral.standards.no-cross-contamination` | scoped | conforms | no cross-layer smuggling |
| `astral.standards.no-hardcoded-sets` | scoped | not-applicable | no behavior sets added (Joan excluded for AST-1313) |
| `astral.standards.public-then-helpers` | scoped | conforms | public shapes extended; helpers unchanged in role |
| `astral.standards.utils-data-late-import-only` | scoped | not-applicable | no utils edits |
| `astral.state.core-decides-transitions` | scoped | not-applicable | no state transitions |
| `astral.state.job-prior-states-enforced` | scoped | not-applicable | no job state |
| `astral.state.no-daisy-chain-in-run` | scoped | not-applicable | no run chain |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | no frontend files |
| `astral.ui.naming-conventions` | scoped | not-applicable | no UI naming |
| `astral.ui.single-gunicorn-worker` | scoped | not-applicable | no server worker config |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | `merge-tests(AST-1312)` present on publish tip |
| `orch.git.commit-vocabulary` | universal | conforms | `code` / `test` / `docs` / `merge-tests` vocabulary |
| `orch.git.flow-direction-inviolable` | universal | conforms | sub branch off ftr parent topology |
| `orch.git.ftr-sub-topology` | universal | conforms | publish ref `sub/AST-1308/AST-1312-…` |
| `orch.git.merge-on-checkout` | universal | conforms | no checkout violations observed |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | linear commit stack |
| `orch.git.no-dev-agent-branches` | universal | conforms | no agent-named branches |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | AST-1308 epic worktree |
| `orch.git.three-permanent-branches` | universal | conforms | sub publish, not main/dev direct |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | raw-To vs parse/bind correctly deferred to AST-1313 in plan |
| `orch.pipeline.plan-is-bible` | universal | conforms | Stage 1 steps 1–7 executed literally in `40612c89` |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Meteorite child scoped correctly |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Tests Passed → review gate satisfied |
| `orch.roles.archie-approves-statutes` | universal | conforms | no statute edits |
| `orch.roles.betty-owns-test-tree` | universal | conforms | test/bible commits by Betty pipeline |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | assignee Katherine through Tests Passed |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | engineer assignee retained |
| `orch.roles.pre-commit-path-bans` | universal | conforms | no banned-path commits observed |

**Sweep count:** 64 active statutes scored (per `canon/statutes/README.md` harvested corpus).

### Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| *(none cited)* | — | plan/parent cite no `canon/patterns/**` ids |

### Plan adherence

Stage 1 implemented exactly in engineer commit `40612c89`:

- `GmailInboxMessage` / `GmailMessageHtml` gain `to_address: str` immediately after `from_address`.
- `metadataHeaders` includes `"To"` with the required one-line comment guarding the list-empty failure mode.
- `_message_metadata` and `get_message_html` copy raw `headers.get("to", "")` — no parse/split/filter.
- Docstring updated; `_candidate_match_for_from` and bind consumers unchanged.
- Core pass-through (`row = dict(msg)` in `inbox.py`) confirmed on worktree — `to_address` reaches list payloads without core edits.

Self-Assessment (**Single-Component / high conf / low risk**) matches the diff footprint. Betty manifest (`TestAst1312ToAddress`) asserts both raw header copy and `metadataHeaders` contract; existing exact dicts revised. Joan plan-rubric APPROVED attached — **no stragglers** (Joan-excluded statutes remain `not-applicable` on this diff).

### C6 judgment aids (§5a–§5g)

| Lens | Verdict |
|------|---------|
| Imports (B1) | conforms — no new imports |
| Layer compliance (B2) | conforms — external-only product change |
| Silent failure (D2) | conforms — no new swallow paths |
| Fallbacks (D3) | conforms — `headers.get("to", "")` matches existing `from_address` contract |
| Logging (E1) | conforms — no logging added |
| Config/state in UI (G1) | not-applicable |
| Batch/transitions (H*) | not-applicable |
| Debug contract (§5f) | not-applicable — no `debug=` paths touched |
| External cleanliness (§5g) | not-applicable — gmail is not an LLM provider peer |

### Findings

*(none)*

### What's solid

- Mirrors AST-1032/AST-1049 `from_address` pattern with minimal, reviewable diff (+7/−2 in product code).
- The `metadataHeaders` comment + `TestAst1312ToAddress::test_list_requests_to_and_copies_raw_header` guard the highest-risk failure mode (list rows always empty To).
- Scope boundary to AST-1313 held: no bind logic, no inbox-address filter, no Manage Email chrome.

### Frame diff

- **`GmailInboxMessage`:** `+to_address: str` (after `from_address`)
- **`GmailMessageHtml`:** `+to_address: str` (after `from_address`)
- **Runtime JSON:** list/get/admin API payloads gain additive `to_address` key (empty string when header absent); clients ignoring unknown keys unaffected.

### Notes

- Joan plan-rubric verdict attached (`revision=1`, APPROVED). No straggler callouts.
- Downstream AST-1313 will consume `to_address`; parsing/bind-source debug correctly out of scope here.

context_tokens≈38000
— Radia

## Resolution — 2026-08-11

**Review tip:** `d1a3026d` (`docs(AST-1312): Radia review — CLEAN`) — Overall **CLEAN**.

- **fix-now:** none.
- **Discuss:** none.
- **Advisory:** none.
- **Product / plan code:** unchanged this pass (resolve clean).

