# User Testing–only merge ticket log and deploy status filter

**Linear:** [AST-792 — User Testing–only merge ticket log and deploy status filter](https://linear.app/astralcareermatch/issue/AST-792/user-testing-only-merge-ticket-log-and-deploy-status-filter-list-of-uat)

**Parent:** [AST-791 — List of UAT issues in environment tooltip is not updating](https://linear.app/astralcareermatch/issue/AST-791/list-of-uat-issues-in-environment-tooltip-is-not-updating) (definition reference only)

**Publish ref:** `origin/sub/AST-791/ast-792-user-testing-only-merge-ticket-log-and-deploy-status-filter` (origin only)

## Summary

The admin deploy footer tooltip (AST-691) lists parent epic ids from `data/merge_ticket_log.json` via `GET /api/deploy_status`. Staging currently shows **Done** parents (e.g. **AST-741**) because the log is append-only and never filtered by Linear state. This ticket restricts the API `merge_tickets` array to parent ids that are **User Testing** in Linear at request time, adds log **remove** + **prune** utilities for lifecycle hygiene, and commits a **one-time cleanup** of stale entries on `origin/dev`. Frontend tooltip UX is unchanged.

⚠️ **Decision:** **Runtime Linear GraphQL filter** on each `get_deploy_status_payload()` call (batched by ticket id). Lifecycle-only removal (prep-uat add / finish-up remove) cannot satisfy AC 4 (parent moves to **PR Ready** without redeploy) within this ticket’s scope — Chuckles skill wiring is explicitly out of bounds. Filter is implemented in **core** orchestrating **utils** + **external/linear** (utils cannot import external per ASTRAL_CODE_RULES §3.3).

⚠️ **Decision:** On Linear API failure or missing `LINEAR_API_KEY` when the log is non-empty, return **`merge_tickets: []`** (fail closed — never show unfiltered stale ids). Uptime and environment fields are unchanged.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Extend `MERGE_TICKET_LOG_CONFIG` with `uat_state_name` literal | utils |
| `src/external/linear.py` | New: batch fetch Linear issue state names by `AST-NNN` identifier | external |
| `src/utils/merge_ticket_log.py` | Add `remove_merge_ticket_log(ticket_id)`; shared atomic `_write_entries` | utils |
| `src/utils/deploy_status.py` | Remove `merge_tickets` assembly from `get_deploy_status_payload`; add pure `filter_merge_tickets_by_state` + `merge_tickets_recent_first` helpers | utils |
| `src/core/deploy_status.py` | New: `get_deploy_status_payload()` — base fields + log read + Linear filter | core |
| `src/ui/api/api_system.py` | Import `get_deploy_status_payload` from `src.core.deploy_status` | ui |
| `scripts/remove_merge_ticket_log.py` | New CLI: remove one parent id from log | scripts |
| `scripts/prune_merge_ticket_log.py` | New CLI: rewrite log keeping only User Testing parents (one-time + maintenance) | scripts |
| `data/merge_ticket_log.json` | One-time prune: drop entries not **User Testing** in Linear (incl. **AST-741**, other **Done** ids) | data |
| `env.example` | Document `LINEAR_API_KEY` (required on staging for tooltip ticket list) | docs |
| `tests/component/external/test_linear.py` | GraphQL client tests with mocked HTTP (Betty manifest) | test |
| `tests/component/utils/test_merge_ticket_log.py` | `remove_merge_ticket_log` coverage (Betty manifest) | test |
| `tests/component/utils/test_deploy_status.py` | Pure filter/order helpers; drop full-payload tests moved to core | test |
| `tests/component/core/test_deploy_status.py` | Full payload + Linear filter integration (Betty manifest) | test |
| `tests/component/ui/api/test_api_system.py` | Monkeypatch core `get_deploy_status_payload` (import path change) | test |

**Verify only (no change expected):**

| File | Role |
|------|------|
| `src/ui/frontend/src/components/AdminDeployFooter.tsx` | AST-691 UX unchanged — consumes filtered `merge_tickets` |
| `scripts/git/record-landed-parent.sh` | Still calls append only; prep-uat add unchanged |
| `scripts/append_merge_ticket_log.py` | Append + dedupe timestamp unchanged |

**Out of scope:** AdminDeployFooter / tooltip UX; Chuckles **team-chuckles** skill updates (`prep-uat`, `finish-up`); child ticket ids; ticket titles in tooltip; global “all User Testing on Linear” inbox (log remains deploy-scoped, filtered by state).

---

## Stage 1: Linear client, log remove, config, and utils helpers

**Done when:** `fetch_parent_issue_states(["AST-741", "AST-791"])` returns a dict mapping identifier → state name via GraphQL (mocked in tests); `remove_merge_ticket_log("AST-741")` removes that row atomically; `filter_merge_tickets_by_state` and `merge_tickets_recent_first` are pure utils functions; `python3 -m py_compile` on touched modules passes.

1. In `src/utils/config.py`, extend `MERGE_TICKET_LOG_CONFIG`:

   ```python
   MERGE_TICKET_LOG_CONFIG = {
       "log_path": _PROJECT_ROOT / "data" / "merge_ticket_log.json",
       "uat_state_name": "User Testing",
   }
   ```

   Add `LINEAR_API_KEY` to the module header comment list of env vars (secret — not stored in config dict).

2. Create `src/external/linear.py` with module docstring (AST-792). Imports: `json`, `os`, `re`, `urllib.request`, `urllib.error`. No logging (external layer §2.5).

   - `_TICKET_ID_RE = re.compile(r"^AST-(\d+)$")` — same pattern as merge_ticket_log.
   - `_parse_ticket_number(ticket_id: str) -> int` — normalize to upper, match regex, return int or raise `ValueError`.
   - `_graphql(query: str, variables: dict | None) -> dict` — POST to `https://api.linear.app/graphql` with header `Authorization: os.environ["LINEAR_API_KEY"]` (no fallback). Raise `LinearApiError` (subclass of `Exception`) on HTTP error, JSON errors array, or missing `data`.
   - `fetch_parent_issue_states(ticket_ids: list[str]) -> dict[str, str | None]`:
     - Dedupe and normalize ids; empty input → `{}`.
     - Parse each to team number; build one query:

       ```graphql
       query IssueStates($teamKey: String!, $numbers: [Float!]!) {
         issues(filter: { team: { key: { eq: $teamKey } }, number: { in: $numbers } }) {
           nodes { identifier state { name } }
         }
       }
       ```

       Variables: `teamKey: "AST"`, `numbers: [<parsed ints>]`.
     - Return `{identifier: state.name for each node}`; ids requested but absent from response map to `None`.

   ⚠️ **Decision:** Single batched GraphQL query per deploy-status request (log typically ≤20 unique parent ids). No TTL cache — Susan’s rule: no unapproved performance shortcuts; 30s frontend poll is acceptable.

3. In `src/utils/merge_ticket_log.py`, refactor write path:

   - Extract `_write_entries(entries: list[dict]) -> None` from `append_merge_ticket_log` (temp file + replace — existing atomic pattern).
   - Update `append_merge_ticket_log` to call `_write_entries` after dedupe append (existing dedupe-by-`ticket_id` behavior unchanged).

4. Add `remove_merge_ticket_log(ticket_id: str) -> bool`:
   - `normalized = _normalize_ticket_id(ticket_id)`.
   - `entries = read_merge_ticket_log()`.
   - `filtered = [e for e in entries if e.get("ticket_id") != normalized]`.
   - If `len(filtered) == len(entries)`: return `False` (no-op).
   - `_write_entries(filtered)`; return `True`.

5. In `src/utils/deploy_status.py`:
   - Remove import of `read_merge_ticket_log` and remove `merge_tickets` logic from `get_deploy_status_payload()`.
   - `get_deploy_status_payload()` returns **only** uptime + optional `environment` (same as pre-AST-681 base + AST-679 shape). **Do not** include `merge_tickets` key here anymore.
   - Add pure helpers (no I/O):

     ```python
     def merge_tickets_recent_first(entries: list[dict]) -> list[dict]:
         return list(reversed(entries))

     def filter_merge_tickets_by_state(
         entries: list[dict],
         state_by_id: dict[str, str | None],
         *,
         uat_state_name: str,
     ) -> list[dict]:
         return [
             e for e in entries
             if state_by_id.get(e.get("ticket_id", "")) == uat_state_name
         ]
     ```

   - Keep `format_uptime_seconds`, `_resolve_environment`, `get_deploy_label`, `is_local_deploy_env`, `ui_llm_debug`, `_PROCESS_BOOT_TIME` unchanged.

6. `python3 -m py_compile src/external/linear.py src/utils/merge_ticket_log.py src/utils/deploy_status.py src/utils/config.py`

**Ritual:** `code(AST-792): linear client, log remove, deploy status utils helpers`

---

## Stage 2: Core payload orchestration, CLIs, env.example, and one-time log prune

**Done when:** `src.core.deploy_status.get_deploy_status_payload()` returns base fields plus `merge_tickets` filtered to **User Testing** only (most recent first); `GET /api/deploy_status` uses core module; `scripts/remove_merge_ticket_log.py` and `scripts/prune_merge_ticket_log.py` work; `data/merge_ticket_log.json` on branch contains only **User Testing** parent ids after running prune against live Linear; `python3 -m py_compile` passes.

1. Create `src/core/deploy_status.py`:

   ```python
   """Admin deploy status payload — orchestrates utils + Linear state filter (AST-792)."""
   ```

   Imports: `src.utils.deploy_status` (base payload + filter helpers), `src.utils.merge_ticket_log.read_merge_ticket_log`, `src.utils.config.MERGE_TICKET_LOG_CONFIG`, `src.external.linear` (`fetch_parent_issue_states`, `LinearApiError`).

   Implement `get_deploy_status_payload() -> dict`:

   ```python
   payload = utils_ds.get_deploy_status_payload()  # uptime, environment only
   entries = read_merge_ticket_log()
   if not entries:
       payload["merge_tickets"] = []
       return payload
   ticket_ids = list(dict.fromkeys(e.get("ticket_id", "") for e in entries if e.get("ticket_id")))
   try:
       state_by_id = linear.fetch_parent_issue_states(ticket_ids)
   except (LinearApiError, KeyError, ValueError):
       payload["merge_tickets"] = []
       return payload
   uat = MERGE_TICKET_LOG_CONFIG["uat_state_name"]
   filtered = filter_merge_tickets_by_state(entries, state_by_id, uat_state_name=uat)
   payload["merge_tickets"] = merge_tickets_recent_first(filtered)
   return payload
   ```

   Always include `merge_tickets` key (empty list when log empty, filter empty, or Linear failure).

2. In `src/ui/api/api_system.py`, change:

   ```python
   from src.core.deploy_status import get_deploy_status_payload
   ```

   Remove `from src.utils.deploy_status import get_deploy_status_payload`. Route body unchanged.

3. Create `scripts/remove_merge_ticket_log.py` (mirror `append_merge_ticket_log.py` structure):

   - Usage: `python3 scripts/remove_merge_ticket_log.py AST-741`
   - Call `remove_merge_ticket_log`; exit 0 with JSON `{"removed": true|false}` on stdout; exit 1 on `ValueError`.

4. Create `scripts/prune_merge_ticket_log.py`:

   - Docstring: one-time / maintenance — keep log entries whose parent is **User Testing** in Linear; drop all others; dedupe by `ticket_id` keeping **latest** `recorded_at` per id before write.
   - Steps: read log → unique ticket ids → `fetch_parent_issue_states` → filter entries where state == `MERGE_TICKET_LOG_CONFIG["uat_state_name"]` → for each surviving id keep entry with max `recorded_at` → `_write_entries` (import private writer via merge_ticket_log module — add `rewrite_merge_ticket_log(entries: list[dict])` public wrapper if needed instead of importing `_write_entries`).
   - Exit 0; print count removed to stdout.

   ⚠️ **Decision:** Add `rewrite_merge_ticket_log(entries: list[dict]) -> None` in `merge_ticket_log.py` — validates array shape, atomic write — for prune script and future lifecycle tooling.

5. **One-time cleanup (this stage commit):** With `LINEAR_API_KEY` set in environment, run:

   ```bash
   python3 scripts/prune_merge_ticket_log.py
   git add data/merge_ticket_log.json
   ```

   Verify `data/merge_ticket_log.json` no longer contains **AST-741** or other **Done** / **PR Ready** parents. If no ids remain in **User Testing**, file may be `[]` — valid per AC 6.

6. In `env.example`, add after Anthropic block:

   ```bash
   # Linear API (required on staging for admin deploy footer UAT ticket tooltip — AST-792)
   # Personal/API key from Linear → Settings → API
   LINEAR_API_KEY=your_linear_api_key_here
   ```

7. `python3 -m py_compile src/core/deploy_status.py src/ui/api/api_system.py scripts/remove_merge_ticket_log.py scripts/prune_merge_ticket_log.py`

**Ritual:** `code(AST-792): core deploy status filter, prune CLIs, and log cleanup`

---

## Stage 3: Component tests (Betty manifest — engineer runs in test-child)

**Done when:** Betty’s manifest tests pass; filter excludes non–User Testing ids; API route still returns `merge_tickets` key; remove/prune CLIs covered.

1. **`tests/component/external/test_linear.py`** (new):
   - Mock `urllib.request.urlopen` to return GraphQL JSON with two nodes (`AST-100` → `User Testing`, `AST-200` → `Done`).
   - `test_fetch_parent_issue_states_maps_identifiers` — assert dict shape.
   - `test_fetch_parent_issue_states_empty_input` → `{}`.
   - `test_invalid_ticket_id_raises` — `ValueError`.
   - `test_graphql_errors_raise_linear_api_error`.

2. **`tests/component/utils/test_merge_ticket_log.py`** — add class `TestRemoveMergeTicketLog`:
   - `test_remove_existing_entry` — append two ids, remove one, read confirms.
   - `test_remove_missing_returns_false` — no file mutation.
   - `test_rewrite_merge_ticket_log` — replaces contents atomically.

3. **`tests/component/utils/test_deploy_status.py`**:
   - Remove / relocate tests that call full `get_deploy_status_payload()` expecting `merge_tickets`.
   - Add `TestMergeTicketHelpers`:
     - `test_merge_tickets_recent_first`
     - `test_filter_merge_tickets_by_state_keeps_uat_only`

4. **`tests/component/core/test_deploy_status.py`** (new):
   - Monkeypatch `read_merge_ticket_log`, `fetch_parent_issue_states`, base utils payload.
   - `test_payload_includes_filtered_merge_tickets_most_recent_first`
   - `test_payload_empty_merge_tickets_when_log_empty`
   - `test_payload_empty_merge_tickets_on_linear_failure` — mock `LinearApiError`
   - `test_payload_excludes_done_parents` — states map with mixed states

5. **`tests/component/ui/api/test_api_system.py`**:
   - Change monkeypatch target to `src.core.deploy_status.get_deploy_status_payload` (or patch at `system_mod` import site after api_system imports from core).

6. Pytest gate:

   ```bash
   .venv/bin/python -m pytest \
     tests/component/external/test_linear.py \
     tests/component/utils/test_merge_ticket_log.py \
     tests/component/utils/test_deploy_status.py \
     tests/component/core/test_deploy_status.py \
     tests/component/ui/api/test_api_system.py::TestDeployStatus \
     -q
   ```

**Ritual:** `test(AST-792): User Testing merge ticket filter coverage`

---

## Execution contract (for the developer agent)

The plan is binding. Execute stages in order. Do not change AdminDeployFooter, tooltip timing/cap/format, or Chuckles skills. Do not list child ticket ids or add Linear fields beyond state name lookup.

When `read_merge_ticket_log` finds invalid top-level JSON, stop and escalate — do not silently reset the file.

Blocking questions use parent **AST-791** with:

```
🛑 Stage N blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

---

## Self-Assessment

**Scope:** `scope-Single-Component` — New external Linear client, core deploy-status orchestrator, utils log remove/prune helpers, two small CLIs, one shipped data file cleanup, and api_system import swap; no frontend or team-chuckles changes.

**Conf:** `Medium` — Runtime Linear filter is new for deploy status but follows existing external-layer HTTP patterns; layer split (core orchestrates utils + external) is required by import rules; AC 4 drove the filter decision over pure log lifecycle.

**Risk:** `risk-Medium` — Wrong filter logic would show stale **Done** ids (Susan’s reported bug) or hide active UAT parents; mitigated by fail-closed empty list on Linear errors and explicit state string match against config literal.

---

## Self-review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Atomic log write in one helper; filter/order as pure utils functions |
| §1.4 magic numbers | `uat_state_name` in config; team key `"AST"` in external module constant |
| §2.1 config | `MERGE_TICKET_LOG_CONFIG` owns path + UAT state label |
| §2.4 batch | N/A |
| §2.6 state machine | N/A — Linear state read-only |
| §3.3 imports | external → utils only; core → external + utils; ui → core; utils does not import external |
| §3.5 naming | `fetch_parent_issue_states`, `filter_merge_tickets_by_state`, `remove_merge_ticket_log` |
| §3.6 local debug | No spike output under `docs/features/` |

No conflicts requiring `conf-!!-NONE`.

---

## Acceptance criteria traceability

| AC | Plan coverage |
|----|----------------|
| 1. No **Done** ids after deploy from current dev | Stage 2 prune commit + Stage 2 runtime filter |
| 2. Every shown id is **User Testing** at request time | Stage 2 `filter_merge_tickets_by_state` + Linear fetch |
| 3. Prep-uat add + re-prep-uat timestamp dedupe | Unchanged `append_merge_ticket_log` dedupe |
| 4. **PR Ready** parent disappears on next refresh | Stage 2 runtime filter (no redeploy required) |
| 5. **Done** after finish-up excluded | Stage 2 runtime filter |
| 6. Empty filtered set → non-interactive env label | AST-691 frontend unchanged; API returns `[]` |
| 7. Non-admin / other footer fields unchanged | Only `merge_tickets` filtering; uptime/env untouched |

---

## Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-791/ast-792-user-testing-only-merge-ticket-log-and-deploy-status-filter`

**Product commits:** `6d634fd` (linear client, log remove, deploy status utils helpers), `8a3ac54` (core deploy status filter, prune CLIs, log cleanup)

**Note for Betty (Stage 3):** Component tests per plan Stage 3 — manifest at Code Complete.

---

## Radia review (2026-06-25)

**Diff:** `origin/dev...origin/sub/AST-791/ast-792-user-testing-only-merge-ticket-log-and-deploy-status-filter` @ `eb71bc4`  
**Product commits:** `6d634fd`, `8a3ac54`, `7e14cbc` (tests)

### What's solid

| Area | Notes |
|------|-------|
| Plan fidelity (Stages 1–3) | Linear client, log remove/rewrite, utils pure helpers, core orchestrator, api_system import swap, prune/remove CLIs, env.example, one-time log prune, and Betty manifest tests all match the binding plan. |
| Layer compliance (§3.3) | `ui` → `core.deploy_status`; core orchestrates `external.linear` + utils; utils has no external import; `external/linear.py` is stdlib-only with no logging. |
| Fail-closed (AC 2, 4–5) | Non-empty log + Linear failure or missing key → `merge_tickets: []`; uptime/env untouched. |
| Config (§1.4, §2.1) | `uat_state_name` in `MERGE_TICKET_LOG_CONFIG`; team key `_TEAM_KEY` constant in external module. |
| DRY / atomic writes | `_write_entries` shared by append, remove, rewrite; temp-file replace preserved. |
| Scope boundaries | No AdminDeployFooter, Chuckles skill, or child-id/title changes. Diff vs `origin/dev` is AST-792 product + tests only (sibling test manifests via `merge-tests` are expected). |
| Self-Assessment | Stated `scope-Single-Component` / `Medium` conf matches diff footprint; no `conf-!!-NONE`. |
| Tests | Manifest gate files cover Linear client, log remove/rewrite, utils helpers, core payload integration, and API route monkeypatch path. |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| **advisory** | `src/external/linear.py` `_graphql` | `urlopen` can raise `URLError` / timeout and `json.loads` can raise `JSONDecodeError` outside the `HTTPError → LinearApiError` path. Core catches `(LinearApiError, KeyError, ValueError)` per plan, so these would 500 the route instead of fail-closed `merge_tickets: []`. Low likelihood; optional hardening if Susan wants strict fail-closed on all network/parse faults. |

### Recommended actions

| Action | Owner |
|--------|-------|
| None required for resolve | — |
| Optional: wrap `URLError`, timeout, and `JSONDecodeError` as `LinearApiError` (or broaden core except) | Engineer, if Susan wants belt-and-suspenders fail-closed |
