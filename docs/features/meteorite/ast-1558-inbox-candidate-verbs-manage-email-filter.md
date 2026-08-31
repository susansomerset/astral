# AST-1558 — inbox candidate verbs + Manage Email filter

**Linear:** [AST-1558](https://linear.app/astralcareermatch/issue/AST-1558/inbox-candidate-verbs-manage-email-filter)  
**Parent:** [AST-1555](https://linear.app/astralcareermatch/issue/AST-1555/meteorite-ingress-staging-table-inboxmeteorite-consolidation) — Meteorite ingress: staging table + inbox/meteorite consolidation  
**Publish ref:** `sub/AST-1555/AST-1558-inbox-candidate-verbs-manage-email-filter`

Shrink `inbox.py` to candidate-scoped Gmail fetch/archive verbs (plus keep HTML get + strip/extract), retire `fetch_email` / From-then-To bind / land-bound helpers and their config+dispatcher wiring, and rewrite Manage Email so listing is All-or-candidate-filter (aliases → `fetch_candidate_email`) with Land calling meteorite ingress under an explicit candidate id. Does **not** implement `check_inbox`, staging-table transitions, Estelle, retention, or delete `meteorite_email.py`.

## Scope gate

Linear child **## Scope** / **## Citations** headings are empty on every AST-1555 child (dispatch template gap). Authoritative partition for this ticket is parent **Proposed child tickets → #2** (mirrored in this ticket’s **What this implements**):

- `src/core/inbox.py` — candidate verbs; delete fetch/land-bound/bind
- `src/utils/config.py` — `FETCH_EMAIL_CONFIG` + `INBOX_BIND_CONFIG` retire (and the tied `TASK_CONFIG` / `SEED_CONFIG` fetch_email entries)
- `src/core/dispatcher.py` — `fetch_email` branch remove
- `data/admin/` seed JSON for `fetch_email` removal — **verified empty** (no `fetch_email` rows in `data/admin/*.json`); no file touch
- `src/ui/api/api_inbox.py` — All vs candidate list; Land → meteorite
- `src/ui/frontend/src/pages/AdminManageEmail.tsx` — filter + drop Matched column

**Citations (parent #2):** `pattern.layers.import-discipline`, `pattern.ui.admin-endpoint`, `astral.layers.import-direction`, `astral.layers.core-vs-external-bright-line`, `astral.layers.ui-config-driven-business-logic`, `astral.dispatch.seed-auto-false`

**Out of scope (siblings):** AST-1557 table/helpers; AST-1559 `check_inbox` + monitoring; AST-1560 stage/scrape/land transitions; AST-1561 Estelle/`apply_paste`; AST-1562 retention + delete `meteorite_email.py`. Parent AC6’s “`meteorite_email.py` is gone” is owned by AST-1562 — this ticket only clears inbox bind/fetch_email surfaces that AC6 also names.

**Depends on:** none for this slice (parallel with AST-1557). After this lands, `meteorite_email.py` still imports `list_inbox_messages` and expects `candidate_match` — that path will see unbound/empty matches until AST-1559 rehomes the runner onto `fetch_candidate_email`. Expected temporary mailbox Avail/runner degradation; do not patch `meteorite_email.py` here.

All Files Changed / Stages stay inside the Scope file set above.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/inbox.py` | Add `fetch_candidate_email` / `archive_candidate_email`; thin unenriched `list_inbox_messages`; keep `get_message_html` / `get_message_with_assembled_html` / `strip_extract_email_html`; delete bind helpers, `run_fetch_email`, `_land_bound_inbox_message`, `land_inbox_message_ids`, `create_meteorite_job_from_inbox_message`; stub bind-count helpers for import compat | core |
| `src/utils/config.py` | Delete `FETCH_EMAIL_CONFIG`, `INBOX_BIND_CONFIG`, `TASK_CONFIG["fetch_email"]`, `SEED_CONFIG["dispatch_task-fetch-email"]` + header inventory / asserts that name them | utils |
| `src/core/dispatcher.py` | Delete `ensure_fetch_email_dispatch_task`; remove `_dispatch_one` / `run_task` `fetch_email` branches and `FETCH_EMAIL_CONFIG` import | core |
| `src/ui/api/api_inbox.py` | `GET /messages` All vs `candidate_id` → aliases → `fetch_candidate_email`; `POST /land-meteorite` requires `candidate_id` + ids → strip via inbox → `stage_meteorite`; delete create-job route | ui |
| `src/ui/frontend/src/pages/AdminManageEmail.tsx` | Candidate filter default All; drop Matched/Candidate column + modal match line; list/Land use new API shape | ui |

## Stage 1: Config — retire fetch_email + bind blocks

**Done when:** `FETCH_EMAIL_CONFIG` and `INBOX_BIND_CONFIG` are gone from `config.py` (no imports can resolve them); `TASK_CONFIG` has no `"fetch_email"` key; `SEED_CONFIG` has no `"dispatch_task-fetch-email"` entry; module header inventory lines that named those blocks are removed or rewritten so they no longer claim the blocks exist; `python3 -c "from src.utils import config"` still imports (remaining asserts green).

1. In `src/utils/config.py` module header inventory, remove the `INBOX_BIND_CONFIG` and `FETCH_EMAIL_CONFIG` one-liners (today ~lines naming AST-1313 / AST-1469).
2. Delete the entire `TASK_CONFIG["fetch_email"]` entry (the small `entity_type`/`requires_candidate_key`/`trigger_state` shell after `contact_estelle_turn`).
3. Delete the entire `FETCH_EMAIL_CONFIG = {…}` block and its four `assert`s.
4. Delete the entire `INBOX_BIND_CONFIG = {…}` block and its four `assert`s (including the comment block that describes From-then-To bind).
5. Delete `SEED_CONFIG["dispatch_task-fetch-email"]` (the `INSERT … fetch_email` SQL stub and its AST-1469/1496 comment).
6. Do **not** edit `data/admin/agent.json` or `data/admin/agent_task.json` — neither contains `fetch_email`. Do **not** add a live-DB purge of existing `dispatch_task` rows with `task_key='fetch_email'` (orphans may remain until operator/#6 cleanup; this ticket only stops seeding/ensuring/running them).

⚠️ **Decision:** Retire tied `TASK_CONFIG` / `SEED_CONFIG` fetch_email entries in the same config pass as `FETCH_EMAIL_CONFIG` — they are the same seed surface parent Scope named under config + admin seed, and leaving them would reintroduce a catalog key with no runner.

## Stage 2: inbox.py — candidate verbs; delete bind / fetch_email / land-bound

**Done when:** `inbox.py` exposes `fetch_candidate_email(aliases)`, `archive_candidate_email(message_id)`, unenriched `list_inbox_messages`, and the existing HTML/strip helpers; it has **no** `_bind_inbox_message` / `_remaining_to_addresses` / `_inbox_addr_folded` / `run_fetch_email` / `_land_bound_inbox_message` / `land_inbox_message_ids` / `create_meteorite_job_from_inbox_message`; `count_inbox_bound_by_candidate` / `count_inbox_messages_bound_to_candidate` remain importable but return `{}` / `0`; `python3 -m py_compile src/core/inbox.py` succeeds; module no longer imports `FETCH_EMAIL_CONFIG`, `INBOX_BIND_CONFIG`, `get_candidate_id_for_query`, `STAGE_METEORITE_CONFIG`, or `METEORITE_CONFIG` (unless a kept helper still needs one of those — strip unused imports).

1. Replace the module docstring with: candidate-scoped Gmail list/filter (`fetch_candidate_email`) + archive (`archive_candidate_email`); thin unenriched `list_inbox_messages` for Manage Email All; keep `get_message_html` / assembled HTML / `strip_extract_email_html`. No From-then-To bind, no `fetch_email` runner, no land-bound stage entrypoints (AST-1558). Land for admin is owned by `api_inbox` → meteorite.
2. Delete helpers and runners in full: `_inbox_addr_folded`, `_remaining_to_addresses`, `_bind_inbox_message`, `run_fetch_email`, `_land_bound_inbox_message`, `land_inbox_message_ids`, `create_meteorite_job_from_inbox_message`.
3. Rewrite `list_inbox_messages(debug: bool = False) -> list[dict]`:
   - Call `external_list_inbox_messages()`; on failure log warning and re-raise (same as today).
   - Return the external rows as `list[dict]` **without** attaching `candidate_match` or any bind fields.
   - Optional Style D when `debug=True`: one index header per message under `func="inbox.list"` with outcome `"listed"` and mid identifier — no bind detail lines. No new lines when `debug=False`.
4. Add `fetch_candidate_email(aliases: list[str] | tuple[str, …], *, debug: bool = False) -> list[dict]`:
   - Normalize aliases: for each raw string, `parseaddr` → bare address if `@` present else strip; drop empties; build a casefold set `alias_set`.
   - If `alias_set` is empty, return `[]` (do not fall through to full inbox).
   - `messages = list_inbox_messages(debug=debug)`.
   - Keep a message when **any** address token from `from_address` **or** `to_address` (use `email.utils.getaddresses` on each header) has `token.casefold()` in `alias_set`.
   - Return matching rows in list order (no `candidate_match` field).
   - Style D when `debug=True`: per kept message, `func="inbox.fetch_candidate_email"`, outcome `"matched"`; detail one line `aliases_n={len(alias_set)}`. No ungated info spam.
5. Add `archive_candidate_email(message_id: str) -> None`:
   - `mid = (message_id or "").strip()`; if empty raise `ValueError("message_id is required")`.
   - Late-import or top-import `archive_message` from `src.external.gmail` and call it; on failure log warning and re-raise.
6. Replace `count_inbox_bound_by_candidate` body with `return {}` and docstring: retired with From-then-To bind (AST-1558); empty until AST-1559 eligibility. Replace `count_inbox_messages_bound_to_candidate` body with `return 0` (same note). Keep signatures so `dispatcher` / `api_admin` imports do not break.
7. Keep `get_message_html`, `get_message_with_assembled_html`, `strip_extract_email_html` behavior unchanged (still read `INBOX_CREATE_JOB_CONFIG` only).
8. Drop unused imports (`get_candidate_id_for_query`, `FETCH_EMAIL_CONFIG`, `INBOX_BIND_CONFIG`, `METEORITE_CONFIG`, `METEORITE_EMAIL_MAILBOX_CONFIG`, `STAGE_METEORITE_CONFIG`, `asyncio` if no longer needed).

⚠️ **Decision — match From or To against aliases:** Parent replaces From-then-To *bind identity* with caller-supplied aliases. Filtering keeps a message if either header carries an alias address so To-only candidate mail still appears when the filter is that candidate.

⚠️ **Decision — bind-count stubs stay:** `api_admin` is out of Scope; deleting the symbols would force an out-of-scope edit. Empty stubs preserve imports; mailbox Avail goes to 0 until AST-1559.

## Stage 3: dispatcher — remove fetch_email runner + ensure

**Done when:** `dispatcher.py` has no `FETCH_EMAIL_CONFIG` import, no `ensure_fetch_email_dispatch_task`, no `_dispatch_one` branch that calls `run_fetch_email`, and no `run_task` special-case that sets `available_count` via fetch_email bind sum; `python3 -m py_compile src/core/dispatcher.py` succeeds.

1. Remove `FETCH_EMAIL_CONFIG` from the `src.utils.config` import list in `src/core/dispatcher.py`.
2. Delete the entire `ensure_fetch_email_dispatch_task` function.
3. Delete the full `_dispatch_one` block gated on `FETCH_EMAIL_CONFIG["task_key"]` (the null-candidate runner that imports `run_fetch_email` and writes ledger) — including its early `return`.
4. In `run_task`, delete the `if … == FETCH_EMAIL_CONFIG["task_key"]:` available_count branch. Leave the existing `_is_inbox_mailbox_task_key` branch intact (it still calls `count_inbox_messages_bound_to_candidate`, which now returns 0).
5. Do **not** change `provision_meteorite_email_dispatch_tasks` / meteorite_email runner wiring (AST-1559/1562).

## Stage 4: api_inbox — All vs candidate list; Land → stage_meteorite

**Done when:** `GET /api/admin/inbox/messages` with no/`""` `candidate_id` returns unenriched full inbox; with a non-empty `candidate_id` resolves that candidate’s email aliases and returns `fetch_candidate_email` rows; `POST /api/admin/inbox/land-meteorite` requires `candidate_id` + non-empty `message_ids`, strips via inbox helpers, late-imports `stage_meteorite`, and returns a per-id results rollup; create-job route is gone; `python3 -m py_compile src/ui/api/api_inbox.py` succeeds.

1. Update the module docstring: Manage Email list is All (`list_inbox_messages`) or candidate-scoped (`aliases → fetch_candidate_email`); Land requires `candidate_id` and calls `stage_meteorite` (meteorite ingress). No bind enrichment; no create-job (AST-1558).
2. Replace inbox imports with: `fetch_candidate_email`, `get_message_html`, `get_message_with_assembled_html`, `list_inbox_messages`, `strip_extract_email_html`. Drop `create_meteorite_job_from_inbox_message` and `land_inbox_message_ids`.
3. Add a **local** helper `_email_aliases_for_candidate(candidate_id: str) -> list[str]` in `api_inbox.py` (do **not** edit `candidate.py`):
   - `from src.core.candidate import get_candidate`
   - `from src.utils.config import CANDIDATE_LOOKUP_CONFIG`
   - Load `get_candidate(cid)`; if missing return `[]`.
   - Walk `CANDIDATE_LOOKUP_CONFIG["email_paths"]` then `["email_list_paths"]` against the candidate row the same way bind lookup did: scalar dotted paths under `candidate_data` (and top-level if present); list paths yield each non-empty string in the list.
   - For each value, `parseaddr` → bare address; keep unique casefold order-stable list of addresses containing `@`.
4. Rewrite `inbox_list_messages`:
   - Read `candidate_id = (request.args.get("candidate_id") or "").strip()`.
   - If empty: `messages = list_inbox_messages(debug=debug)`.
   - Else: `aliases = _email_aliases_for_candidate(candidate_id)`; `messages = fetch_candidate_email(aliases, debug=debug)`.
   - Same 502-on-exception / `{"messages": …}` 200 contract as today.
5. Delete the entire `POST …/messages/<message_id>/create-job` route and its METEORITE_CONFIG outcome mapping.
6. Rewrite `inbox_land_meteorite`:
   - Body must include `candidate_id` (non-empty string) and `message_ids` (non-empty list after strip) — else 400 with clear error strings (`candidate_id is required` / existing message_ids errors).
   - For each mid, build one result row:
     - Try `get_message_html(mid)` + `strip_extract_email_html(...)`; on failure append `{message_id, outcome: "error", astral_candidate_id: cid, error: str}`.
     - If stripped HTML empty → outcome `METEORITE_CONFIG["land_outcome_error"]` with error `stripped email HTML is empty`.
     - Else late-import `from src.core.meteorite import stage_meteorite` and `asyncio.run` is wrong inside an already-sync handler that used `asyncio.run(land_inbox…)` — keep **one** `asyncio.run` around an inner async helper that loops `await stage_meteorite(cid, html, source_kind="email", source_id=mid, debug=debug)` per id (same pattern as today’s single `asyncio.run(land_inbox_message_ids(...))`).
     - Map each stage dict to a result row: `message_id`, `outcome` from `stage.get("outcome")` or error key, `astral_candidate_id=cid`, optional nested `stage`/`land` if useful for toast parity — at minimum match today’s top-level counters: `results`, `total_processed`, `total_passed`, `total_failed`, `total_errors`, `total_skipped`.
   - Pass counting rule: treat `stage.get("skipped")` or outcome in `STAGE_METEORITE_CONFIG["skip_outcomes"]` or land-created/duplicate/supersede keys as passed (import `STAGE_METEORITE_CONFIG` / `METEORITE_CONFIG` from config). Missing Gmail message → skip outcome string from `METEORITE_EMAIL_MAILBOX_CONFIG["selected_outcome_skipped_not_in_inbox"]` (still valid config; not bind).

⚠️ **Decision — Land requires filter candidate_id:** With bind gone there is no per-message matched candidate. Manage Email All is list-only; Land is only valid when a candidate filter is selected. API enforces that; UI disables the button when filter is All.

⚠️ **Decision — interim ingress is `stage_meteorite`:** AST-1560 will replace table-driven land transitions; this ticket’s Scope says Land → meteorite without implementing those transitions. Calling existing `stage_meteorite` from the API (not resurrecting inbox land-bound helpers) satisfies “meteorite ingress” inside Scope.

## Stage 5: AdminManageEmail — filter default All; drop Matched

**Done when:** Manage Email shows a Candidate filter control whose default value is All (`""`); changing the filter reloads messages via `GET /api/admin/inbox/messages` with optional `candidate_id`; the table has no Candidate/Matched column and the modal has no Matched line; Land Meteorite is disabled when filter is All or selection is empty, and POST body includes `candidate_id`; frontend typecheck/build for the page file is clean enough that `npm`/Vite compile of the touched module does not error on removed `candidate_match` fields.

1. Import `AdminCandidateFilterControl` and `useCandidate` (for `candidates` list). Use **local** state `const [candidateFilter, setCandidateFilter] = useState<AdminCandidateFilterValue>("")` — default **All**, do **not** sync to nav selected candidate (parent AC: default All).
2. Place `AdminCandidateFilterControl` in the toolbar (before Select all).
3. Change `loadMessages` to call  
   `api(candidateFilter ? `/api/admin/inbox/messages?candidate_id=${encodeURIComponent(candidateFilter)}` : `/api/admin/inbox/messages`)`.  
   Re-run load when `candidateFilter` changes (`useEffect` deps include `candidateFilter`); clear selection on filter change.
4. Remove `CandidateMatch` type, `candidate_match` from `InboxMessage`, `matchCell`, table header `Candidate`, `{matchCell(row)}` cell, modal `selectedMatchId` block, and any `manage-email-match` usage in this file.
5. Set table `colSpan` for empty row to the new column count (5: checkbox, Subject, From, Date, Status).
6. `onLandMeteorite`: if `!candidateFilter` return early; POST JSON `{ message_ids: ids, candidate_id: candidateFilter }`. Disable Land button when `!candidateFilter || selectionCount === 0 || landBusy`.

⚠️ **Decision — default All overrides nav sync:** Other admin pages pin to nav candidate via `useAdminCandidateFilter`; parent AC7 explicitly defaults Manage Email to All, so local `""` state is intentional.

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; publish each to `origin/sub/AST-1555/AST-1558-inbox-candidate-verbs-manage-email-filter`.
- Do not edit `meteorite_email.py`, `meteorite.py` (beyond late-import call sites from api), `candidate.py`, `api_admin.py`, or `tests/` / bible.
- If `stage_meteorite` signature differs after sync, stop and comment on **parent AST-1555** with the blocking format from plan-child.

## Estimate

Confirm Chuckles estimate: 5 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1558
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1555/AST-1558-inbox-candidate-verbs-manage-email-filter` @ `81c44eb91a13ff71c363e609643e4eac65251ca5`

## Traceability

AC6 (child slice): Stages 1–3 retire `run_fetch_email` / `fetch_email` / From-then-To bind + dispatcher/config surfaces; AC6 remainder (`meteorite_email.py` delete, meteorite→gmail ban, unbound Trash hygiene) explicitly N/A here → AST-1559/1562 per Boundaries. AC7: Stages 2+4+5 — All default list, candidate filter → aliases → `fetch_candidate_email`, Matched column removed, Land → `stage_meteorite` with required `candidate_id`.

## Findings

### acceptable
- **Location:** Scope gate / Boundaries  
  **Finding:** Parent AC6 is split across siblings; plan documents AST-1562 for file delete and AST-1559 for runner rehome.  
  **Recommendation:** Keep boundary comments during build; do not expand into `meteorite_email.py` or `meteorite.py` beyond Stage 4 late-import.

- **Location:** Stage 1 step 6  
  **Finding:** Live-DB `dispatch_task` rows with `task_key='fetch_email'` may linger; plan correctly limits scope to stopping seed/ensure/run.  
  **Recommendation:** Accept orphans until operator/#6 cleanup.

- **Location:** Stage 2 step 6  
  **Finding:** `archive_candidate_email` is added but unused in this slice — required by parent Functional scope #2 for AST-1559.  
  **Recommendation:** Land as specified; no API wiring needed here.

### discuss
- **Location:** Stage 4 step 3 (`_email_aliases_for_candidate`)  
  **Finding:** Reimplements `CANDIDATE_LOOKUP_CONFIG` path walking that `_lookup_path_value` / `_iter_uniqueness_path_values` already own in `candidate.py`. Scope gate forbids `candidate.py` touch.  
  **Recommendation:** Accept for this ticket; consider a shared `core` helper in a follow-up if duplication bites.

- **Location:** Stage 4 step 6 vs current `land_inbox_message_ids` in `inbox.py`  
  **Finding:** Land orchestration (strip loop + `asyncio.run` + `stage_meteorite`) moves from core to `api_inbox.py` because inbox land-bound helpers are deleted and `meteorite.py` is out of scope.  
  **Recommendation:** Proceed as planned; heavier than thin-wrapper ideal but scope-consistent.

- **Location:** Stage 2 step 4 (`fetch_candidate_email`)  
  **Finding:** Candidate filter loads full inbox then filters in memory — fine for admin scale today, not Gmail-query-optimal.  
  **Recommendation:** No plan change unless Susan wants query-shaped fetch in this slice.

## R6 checklist (summary)

Definition fidelity: passes — Files Changed ⊆ parent #2 Scope; sibling work explicitly excluded.  
Layer/config/placement: passes — ui→core only; config retirements in `config.py`; `AdminManageEmail.tsx` stays flat under `pages/`.  
Pattern compliance: cited patterns (`import-discipline`, `admin-endpoint`, layer statutes, `seed-auto-false`) match plan shape; `stage_meteorite` signature on tree matches Stage 4 call (`candidate_id`, `blob`, `source_kind`, `source_id`, `debug`).  
DRY/scope: no scope creep; bind-count stubs documented for AST-1559.  
Self-assessment: absent — not blocking (no `!!-NONE` conf gap).

**Considered (in-session):** universal orch.* statutes — conform (orchestration/process, not product plan content). Scoped product statutes on `core`/`utils`/`ui` paths — conform except `astral.standards.dry-and-focused-functions` → needs-discussion (alias helper duplication), not fix-now.

context_tokens≈38000

## Review

- **Publish ref:** `origin/sub/AST-1555/AST-1558-inbox-candidate-verbs-manage-email-filter`
- **Tip:** `9121d03acabc923e0c1cfd3024a157a1022f99e3`
- **Stages:** 1 config retire · 2 inbox verbs · 3 dispatcher · 4 api_inbox · 5 AdminManageEmail

## Radia review

# Radia review — AST-1558

`[code-rubric] revision=2`  
**Rubric:** code-rubric.v2  
**Ticket:** AST-1558  
**Publish ref:** `sub/AST-1555/AST-1558-inbox-candidate-verbs-manage-email-filter` @ `158e73aa7ae28da5ba78a251d52256268b562f14`  
**Overall:** DISCUSS  
**Internal grade:** DISCUSS (product faithful; branch hygiene + off-manifest test debt)

**Baseline:** `git diff origin/dev...origin/sub/AST-1555/AST-1558-inbox-candidate-verbs-manage-email-filter`  
**Status gate:** Tests Passed (spawn prompt — trusted)

---

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | no agent paths |
| astral.agent.do-task-delegation | scoped | not-applicable | no do_task changes |
| astral.agent.grade-vector-validation | scoped | not-applicable | no grade-vector paths |
| astral.batch.batch-id-first | scoped | not-applicable | no batch claim paths |
| astral.batch.batch-id-format | scoped | not-applicable | no batch ids |
| astral.batch.claim-process-release | scoped | not-applicable | bind/claim queue retired |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | no agent_responses |
| astral.config.config-source-of-truth | scoped | conforms | land/skip outcomes read `METEORITE_CONFIG` / `STAGE_METEORITE_CONFIG` / mailbox config |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | no new env reads |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no artifacts dir |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | no spikes |
| astral.dispatch.seed-auto-false | scoped | conforms | `FETCH_EMAIL_CONFIG` + `SEED_CONFIG["dispatch_task-fetch-email"]` removed; no new auto seeds |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | no run_next edits |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single `ast-1558-*.md` plan doc |
| astral.git.betty-no-src-or-features | scoped | not-applicable | Betty test/bible commits |
| astral.git.engineer-test-tree-ban | scoped | not-applicable | engineer `src/` only per plan contract |
| astral.layers.core-vs-external-bright-line | scoped | conforms | Gmail I/O in `src/external`; core orchestrates |
| astral.layers.import-direction | scoped | conforms | ui→core; core→external; no ui→data/external |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no scripts |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | filter/Land rules server-side; React thin |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | no coat-check paths |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | no consult |
| astral.idioms.require-auth-on-protected-endpoints | scoped | conforms | all inbox routes `@require_admin` + auth tests |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | no admin JSON edits (verified empty) |
| astral.seed.archie-catalog-wins | scoped | not-applicable | no seed catalog |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | no boot seed |
| astral.seed.define-approved | scoped | not-applicable | implement ticket |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | no operator row purge |
| astral.seed.other-via-coverage-join | scoped | not-applicable | no coverage join |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | no data layer changes |
| astral.standards.database-header-inventory | scoped | not-applicable | no database.py |
| astral.standards.debug-contract-gated | scoped | conforms | `list_inbox_messages` / `fetch_candidate_email` emit Style D only when `debug=True` |
| astral.standards.dry-and-focused-functions | scoped | needs-discussion | `_email_aliases_for_candidate` duplicates candidate lookup walking (Joan flagged; scope forbids `candidate.py` touch) |
| astral.standards.in-scope-only | scoped | needs-discussion | `METEORITE_STATES` block (AST-1557) landed on this sub via `6a9a046f` — outside AST-1558 plan Files Changed |
| astral.standards.logging-via-utils | scoped | conforms | `get_logger` in inbox/api; warnings + re-raise |
| astral.standards.names-not-ticket-ids | scoped | conforms | domain function/route names |
| astral.standards.no-cross-contamination | scoped | conforms | inbox/dispatcher/api_inbox changes cohesive; retired symbols removed from `src/` |
| astral.standards.no-hardcoded-sets | scoped | conforms | outcomes/aliases from config; no inline state sets |
| astral.standards.public-then-helpers | scoped | conforms | public verbs before local lookup helpers |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | config-only utils edits |
| astral.state.core-decides-transitions | scoped | conforms | Land delegates to `stage_meteorite`; no inbox transition map |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no job transition edits |
| astral.state.no-daisy-chain-in-run | scoped | conforms | per-id `stage_meteorite` loop; no inbox daisy-chain |
| astral.ui.frontend-file-placement | scoped | conforms | `AdminManageEmail.tsx` under `pages/` |
| astral.ui.naming-conventions | scoped | conforms | no naming violations |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no server config |
| orch.git.betty-merge-tests-one-sha | universal | conforms | `merge-tests(AST-1558)` on tip |
| orch.git.commit-vocabulary | universal | conforms | staged `code`/`test`/`docs`/`merge-tests` |
| orch.git.flow-direction-inviolable | universal | conforms | sub under AST-1555 |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1555/AST-1558-…` |
| orch.git.merge-on-checkout | universal | conforms | no rebase violation observed |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | clean history |
| orch.git.no-dev-agent-branches | universal | conforms | engineer sub branch |
| orch.git.one-epic-worktree-per-parent | universal | conforms | AST-1555 worktree |
| orch.git.three-permanent-branches | universal | conforms | diff vs `origin/dev` |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | no product-policy invention |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–5 implemented |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Meteorite child |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review |
| orch.roles.archie-approves-statutes | universal | conforms | no new statutes |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty manifest + tests |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Hedy assignee |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | implementer still assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | no hook bypass |

**Active set scored:** 64 rows (registry lists 65; all corpus ids covered).

---

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.layers.import-discipline | conforms | Gmail in external; bind/filter/archive in core; ui calls core only |
| pattern.ui.admin-endpoint | needs-discussion | `@require_admin` (pre-existing on this blueprint) vs catalog canonical `@require_auth` — Joan precedent on peer inbox routes |

---

## Plan adherence

**Stages 1–5:** Matches plan.

| Stage | Verdict |
|-------|---------|
| **1 Config** | `FETCH_EMAIL_CONFIG`, `INBOX_BIND_CONFIG`, `TASK_CONFIG["fetch_email"]`, `SEED_CONFIG["dispatch_task-fetch-email"]` deleted; header inventory updated |
| **2 inbox.py** | `fetch_candidate_email`, `archive_candidate_email`, unenriched `list_inbox_messages`, bind/fetch/land-bound symbols removed, count stubs `{}`/`0`, HTML/strip keepers retained, Style D when `debug=True` |
| **3 dispatcher** | `ensure_fetch_email_dispatch_task`, `_dispatch_one` fetch_email branch, `run_task` available_count branch removed |
| **4 api_inbox** | All vs `candidate_id` list; `_email_aliases_for_candidate` local; create-job route gone; Land requires `candidate_id`, loops `stage_meteorite` via `asyncio.run` |
| **5 AdminManageEmail** | Default All filter; Matched column removed; Land disabled when All; POST includes `candidate_id` |

**Boundaries respected in `src/`:** No `meteorite_email.py`, `candidate.py`, `api_admin.py` edits. `archive_candidate_email` present but unwired (plan-acceptable for AST-1559).

**Estimate 5:** Honest for ~350 LOC net shrink + API/UI rewrite + Betty test pass.

**Sibling degradation:** Documented — `meteorite_email` still expects bind enrichment until AST-1559; bind-count stubs return 0.

---

## Findings

### discuss — AST-1557 `METEORITE_STATES` on AST-1558 publish ref

- **Location:** `src/utils/config.py` (commit `6a9a046f` on same sub)
- **Finding:** Three-dot diff adds full `METEORITE_STATES` / `METEORITE_STATES_RETENTION` block — AST-1557 scope, not listed in AST-1558 Files Changed. No `database.py` helpers on this branch.
- **Recommendation:** Not a functional defect for this ticket. **Chuckles/datt:** confirm parallel-child stacking on shared ftr/sub ancestry is intentional; avoid double-landing config on ftr merge if AST-1557 lands separately first.

### discuss — sibling test/bible bleed on publish ref

- **Location:** `tests/component/data/database/test_meteorites.py`, `tests/component/core/test_tracker.py`, `tests/component/ui/api/test_api_jobs.py`, related bible blocks (AST-1557 / AST-1556 ancestry via `origin/tests`)
- **Finding:** Present in diff vs `origin/dev` but outside AST-1558 manifest; Betty manifest correctly scopes green runs.
- **Recommendation:** **Chuckles:** strip or document parallel-track carry before ftr merge; not resolve-child product work.

### discuss — off-manifest legacy test references deleted `INBOX_BIND_CONFIG`

- **Location:** `tests/component/core/test_ast1467_gaze_email_retire.py::test_mailbox_config_is_meteorite_email_only`
- **Finding:** Asserts `cfg.INBOX_BIND_CONFIG["inbox_address"]` — AttributeError if that module is run; not in AST-1558 manifest.
- **Recommendation:** **Betty** revise on next sweep (assert mailbox address via `METEORITE_EMAIL_MAILBOX_CONFIG` only, or drop bind coupling). Manifest green does not prove zero-arg harness safety.

### discuss — `_email_aliases_for_candidate` duplication (Joan carry-forward)

- **Location:** `src/ui/api/api_inbox.py`
- **Finding:** Reimplements `CANDIDATE_LOOKUP_CONFIG` path walking because plan forbids `candidate.py` touch.
- **Recommendation:** Accept for this ticket; optional shared core helper follow-up.

### discuss — Land orchestration in UI API layer

- **Location:** `src/ui/api/api_inbox.py::inbox_land_meteorite`
- **Finding:** Strip loop + `asyncio.run` + `stage_meteorite` moved from deleted inbox land-bound helpers into API — heavier than ideal thin-wrapper.
- **Recommendation:** Plan- and Joan-approved; proceed to UT; AST-1560 may rehome when table transitions land.

### advisory — `get_message_html` failures map to skip-missing outcome

- **Location:** `inbox_land_meteorite` exception handler
- **Finding:** All `get_message_html` failures use `selected_outcome_skipped_not_in_inbox`, not generic `"error"` — plan bullets slightly tensioned; matches prior mailbox skip semantics.
- **Recommendation:** No change unless Susan wants stricter error vs skip distinction.

### advisory — `fetch_candidate_email` loads full inbox then filters in memory

- **Location:** `src/core/inbox.py`
- **Finding:** Joan flagged; acceptable at admin scale per plan Decision.
- **Recommendation:** No plan change in this slice.

### advisory — `@require_admin` vs pattern `require_auth`

- **Location:** `src/ui/api/api_inbox.py`
- **Finding:** Pre-existing on dev; auth + non-admin forbidden tests present.
- **Recommendation:** Citation hygiene only.

---

## What's solid

- Clean retirement of bind/fetch_email surfaces: config, dispatcher, inbox, API, and UI aligned.
- `list_inbox_messages` no longer attaches `candidate_match`; filter uses explicit aliases From **or** To.
- Manage Email AC: default All, Matched column gone, Land gated on candidate filter + required `candidate_id`.
- Layer discipline maintained; debug contract gated on inbox paths.
- Betty manifest covers inbox core, config retirements, API, and Vitest page tests.

---

## Frame diff

| Area | Paths | Verdict |
|------|-------|---------|
| AST-1558 product | `src/core/inbox.py`, `dispatcher.py`, `api_inbox.py`, `AdminManageEmail.tsx`, `config.py` retirements | In-scope; plan-faithful |
| AST-1558 tests/bible | `test_inbox.py`, `test_api_inbox.py`, `test_AdminManageEmail.test.tsx`, `TestAst1558FetchEmailBindRetired`, inbox/api/pages bible | In-scope |
| AST-1557 bleed | `METEORITE_STATES` in `config.py`; `test_meteorites.py` + bible | Discuss — sibling |
| AST-1556 bleed | `test_tracker.py`, `api_jobs` bible/tests | Discuss — sibling |
| Off-manifest debt | `test_ast1467_gaze_email_retire.py` | Discuss — Betty |

---

## Notes

- Joan plan-rubric APPROVED @ `81c44eb9`; no Excluded-statute attachment for straggler sweep.
- C6 lenses (imports, layers, silent failure, fallbacks, logging, batch §5f, external §5g): no fix-now violations in AST-1558 `src/` footprint.
- `grep` confirms no remaining `FETCH_EMAIL_CONFIG` / `INBOX_BIND_CONFIG` / `run_fetch_email` in `src/`.
- No fix-now product findings on AST-1558 scope.

---

## Recommended actions (downstream — not Radia)

1. **Chuckles:** Append verdict; post slim upshot; → Review Posted.
2. **Chuckles/datt:** Resolve AST-1557 config + sibling test bleed on sub tip before ftr merge.
3. **Betty (follow-up):** Fix `test_ast1467` `INBOX_BIND_CONFIG` assertion off-manifest.
4. **resolve-child:** No AST-1558 product changes required; proceed to UT after discuss acknowledged.

context_tokens≈62000

## Resolution

**Date:** 2026-08-31  
**Review tip:** `158e73aa` (Radia DISCUSS — no fix-now product items)  
**Resolve tip:** (this commit)

### Outcome

**Clean resolve — no AST-1558 product changes.** Radia recommended proceeding to User Testing after discuss items are acknowledged; all fix-now slots empty.

### Discuss items (acknowledged, no action this ticket)

| Item | Disposition |
|------|-------------|
| AST-1557 `METEORITE_STATES` + sibling test/bible bleed on publish ref | Sibling stacking on parallel `sub/*` tracks — Chuckles `merge-child` / ftr rollup hygiene, not AST-1558 defect |
| `test_ast1467_gaze_email_retire.py` still references deleted `INBOX_BIND_CONFIG` | Off-manifest — Betty follow-up on next sweep |
| `_email_aliases_for_candidate` duplication in `api_inbox.py` | Scope-accepted (plan forbids `candidate.py` touch) |
| Land orchestration in API layer | Plan- and Joan-approved; AST-1560 may rehome |
| Advisory: skip-missing vs error mapping, in-memory filter, `@require_admin` | No change unless Susan directs |

### Rollup alignment

Merged `origin/ftr/AST-1555-meteorite-ingress-staging-table-inbox-meteorite-consolidation` (AST-1557 resolve @ `5408b867`) into this publish ref so §9a ftr dry-run is clean before User Testing. Plan doc retained (modify/delete conflict — ftr had no per-child plan files).

### §9a dry-run

- `origin/dev`: clean
- `origin/ftr/AST-1555-meteorite-ingress-staging-table-inbox-meteorite-consolidation`: clean after ftr merge
