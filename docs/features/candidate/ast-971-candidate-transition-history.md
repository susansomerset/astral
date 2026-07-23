# AST-971 — Candidate transition history

**Linear:** [AST-971](https://linear.app/astralcareermatch/issue/AST-971/candidate-transition-history-candidate-state-machine)  
**Parent:** [AST-871](https://linear.app/astralcareermatch/issue/AST-871/candidate-state-machine)  
**Publish ref:** `origin/sub/AST-871/AST-971-candidate-transition-history`

Persist enter/exit history on every successful candidate state change with parity to job/company history so prior state, new state, and timestamps support time-in-state reporting (AST-869 State Progress later). This ticket does **not** own the state vocabulary or transition allow-list (AST-970) and does **not** build the Progress UI (AST-869).

**Dependency:** blockedBy AST-970. Build against the sole validated transition API AST-970 leaves in `src/core/candidate.py` (`transition_candidate_state`, `prior_states` enforcement). Do not invent a parallel transition path. If AST-970 renames/moves that API, stop and comment on AST-871 — do not improvise.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Add `candidate.state_history` column (CREATE + idempotent ALTER); update module **header inventory** candidate bullet to include `state_history`; parse JSON in `_parse_candidate_row`; accept optional `state_history` on `save_candidate` (caller-managed overwrite, preserve when omitted) | data |
| `src/core/candidate.py` | Seed history on create; append company-shaped history **once** inside `transition_candidate_state` on success (AST-970 routes delete + admin state overrides through that sole path) | core |
| `docs/features/candidate/CANDIDATE_DATA_MODEL.md` | Document `state_history` column + entry shape | docs |

## Stage 1: Data layer — `state_history` on candidate

**Done when:** Fresh and existing candidate DBs expose a parsed `state_history` list on `get_candidate` / `list_candidates`; `save_candidate(..., state_history=[...])` persists the list; omitting `state_history` on update leaves the existing column unchanged; the `database.py` header inventory candidate line lists `state_history`.

1. In `src/data/database.py`, extend `_ensure_candidate_schema`:
   - On **CREATE TABLE candidate**, add column `state_history TEXT DEFAULT '[]'` after `state` (or after `state_changed_at` — either is fine; keep column order consistent with the ALTER list).
   - On existing DBs, add to the idempotent migration loop: `("state_history", "TEXT DEFAULT '[]'")` alongside `candidate_api_key` / `agent_responses`.
2. In the same change, update the module **header inventory** (top-of-file `Tables used (inventory):` block). Extend the `candidate — …` bullet so it includes `state_history` (JSON array), same style as the `job` / `company` bullets that already list `state_history`. Statute: `astral.standards.database-header-inventory`.
3. In `_parse_candidate_row`, parse `state_history` the same way company/job rows do: `json.loads` → `list`; on missing/invalid → `[]`.
4. In `save_candidate`, add keyword-only arg `state_history: Optional[List[Dict[str, Any]]] = None`:
   - **INSERT (new PK):** persist `json.dumps(state_history if state_history is not None else [])` into the new column (include column in the INSERT column list).
   - **UPDATE:** if `state_history is not None`, set `state_history = ?` with `json.dumps(state_history)`; if `None`, do **not** touch the column (preserve existing), matching `save_job` caller-managed overwrite semantics.
   - Do **not** auto-append inside the data layer — core owns append (rules §2.6: data accepts state from caller; history recording stays in core next to transition).
5. Keep existing auto-`state_changed_at` behavior when `state` changes (already present). History append does not replace `state_changed_at`.

⚠️ **Decision:** Column on `candidate`, not a separate history table — mirrors job/company `state_history` JSON arrays so AST-869 can reuse the same read pattern.

## Stage 2: Core — append history once on the sole transition path

**Done when:** Creating a candidate seeds one history entry for the initial state; every successful `transition_candidate_state` appends exactly one entry with prior + new state + timestamp; delete/admin state changes that go through that function do not double-append; illegal transitions still raise and write nothing.

### Entry shape (binding)

Every history entry is a dict:

```json
{
  "from_state": "<prior state string, empty string on create seed>",
  "to_state": "<new state>",
  "timestamp": "<UTC 'YYYY-MM-DD HH:MM:SS' via same clock as other candidate writes>",
  "batch_id": null
}
```

- Use **company** parity (`from_state` + `to_state` + `timestamp` + `batch_id`), not job-only `to_state`. Parent AC requires prior/new for time-in-state; consecutive timestamps give duration in the exited state (`from_state` of entry N = time from entry N-1 `timestamp` to entry N `timestamp`).
- `batch_id`: always include the key. Read `candidate.get("batch_id")` if present; otherwise `null`. **Do not** add a `batch_id` column in this ticket (dispatch claim is AST-972). AST-869 / other readers must treat `null` as “no batch” (not an error). Forward-compatible with later batch anchoring (AST-769 noted candidates lack history today).
- Timestamp format: same UTC string style already used in `transition_job_state` / `transition_company_state` / `_utc_now()` for candidates — pick the existing helper used by `save_candidate` / nearby candidate core code and use it consistently in this module (do not invent a second clock format).

⚠️ **Decision:** Prefer company-shaped entries over job-only `to_state` so prior state is explicit without scanning the previous row. AST-869 can still compute time-in-state from consecutive timestamps.

### Helpers and call sites

6. In `src/core/candidate.py`, add a small private helper (name e.g. `_append_candidate_state_history`) that:
   - Takes `candidate: dict`, `from_state: str`, `to_state: str`, `timestamp: str`.
   - Returns a **new** list = `list(candidate.get("state_history") or [])` + one entry shaped as above.
   - Does not write to the DB itself.
7. **`initiate_candidate`:** seed history for the initial state AST-970 defines (`CANDIDATE_CONFIG["initial_state"]` / `NEW_CANDIDATE`). Prefer a single INSERT that includes both `state` and `state_history` with one seed entry: `from_state=""`, `to_state=<initial>`, `timestamp=now`, `batch_id=null`. Create-then-update is fine if INSERT shape is awkward. Do not double-seed on re-call (if initiate always inserts fresh, keep that).
8. **`transition_candidate_state`:** keep AST-970’s validation (`to_state in CANDIDATE_STATES` + `prior_states` / `_candidate_state_allowed` — not the retired `candidate_state_transitions` tuple list). On success only:
   - `history = _append_candidate_state_history(candidate, from_state, to_state, now)`
   - Pass `state_history=history` on the same `database.save_candidate` call that writes `state=to_state` (AST-970’s plan writes state here; this ticket adds the history kwarg to that write — do not add a second save solely for history).
   - Preserve AST-970 side effects already in that function (e.g. DELETED reap timer start) — history append does not replace them.
   - Do not change validation rules, allow-lists, or vocabulary in this ticket.
9. **`delete_candidate` / admin state overrides (post-AST-970):** AST-970 routes both through `transition_candidate_state` (`delete_candidate` → `transition_candidate_state(..., "DELETED")`; admin API calls `transition_candidate_state` instead of `save_candidate_admin(..., state=...)`). **Do not** append history again in `delete_candidate` or `save_candidate_admin`. History for those hops is recorded exactly once inside `transition_candidate_state` (step 8).
10. **Residual direct state writes:** After merging AST-970, if any call site still does `database.save_candidate(..., state=...)` without going through `transition_candidate_state` (should be none for product state changes), add a single guarded append at that residual site only — or stop and comment on AST-871 if a surprising bypass remains. Do not sprinkle appends “just in case” on every wrapper.
11. Do **not** append history for `candidate_data`-only or `candidate_api_key`-only saves.
12. Do **not** build AST-869 UI, reports, or API endpoints that aggregate time-in-state.

⚠️ **Decision:** Exactly one history append per successful state change, on the sole AST-970 transition write path. Matches job/company (`transition_*_state` appends; wrappers that call transition do not re-append). Soft-delete is **not** a validation bypass after AST-970 (`DELETED.prior_states is None` allows entry via transition).

## Stage 3: Data model doc

**Done when:** `CANDIDATE_DATA_MODEL.md` documents the column and entry shape so AST-869 / future readers do not reverse-engineer from code.

13. In `docs/features/candidate/CANDIDATE_DATA_MODEL.md`, under **Candidate table (columns)**, add:
    - **state_history** — JSON array of `{from_state, to_state, timestamp, batch_id}`; appended by core on successful `transition_candidate_state` (and create seed) (AST-971). `batch_id` may be null until candidate batch claim exists; readers treat null as no batch.
14. In the **State machine** section, add one sentence: successful transitions append `state_history` (prior/new + timestamp) for time-in-state; Progress UI remains AST-869.

## Out of scope (do not do)

- AST-970 vocabulary / `prior_states` / transition allow-list changes
- AST-972 dispatch claim / stale aging / `batch_id` column
- AST-973 legacy row remaps
- AST-869 Progress UI
- Changing company or job history shapes
- Writing or editing `tests/` (Betty owns tests)

## Self-Assessment

**Scope:** `Single-Component` — candidate data column (+ header inventory) + core append inside the sole transition path; no UI, no dispatch, no sibling vocabulary work.

**Conf:** `high` — mirrors existing `transition_company_state` / `transition_job_state` history append; AST-970 already designates `transition_candidate_state` as the sole state-write path for delete/admin; gap is the missing column and core append.

**Risk:** `Medium` — wrong or double appends break future AST-869 time-in-state and agent batch anchoring; illegal transitions must still fail closed with no partial history write. Vocabulary drift from AST-970 is a merge-order risk, not a design unknown.

## Code rules check

- §2.1 / §2.6: no new hardcoded state lists; validation stays on AST-970’s config-backed `prior_states` API.
- §2.6: core decides/records transitions; data layer only persists caller-supplied `state` + `state_history`.
- §1.3 DRY: one append helper; reuse existing UTC timestamp helper; do not fork a second history format.
- §3.3 / §3.5: no new modules; names follow `state_history` / `from_state` / `to_state` already used for company.
- `astral.standards.database-header-inventory`: Stage 1 step 2 updates the candidate header bullet with `state_history`.

## Revisions

### Revision 1 — 2026-07-23

Driven by: Joan `[plan-discuss] round=1 concern` REVISE — (1) missing `database.py` header-inventory update for `candidate.state_history`; (2) Stage 2 double-append risk because AST-970 routes `delete_candidate` + admin state overrides through `transition_candidate_state`.

Changes:
- Stage 1: explicit header-inventory step; Files Changed row mentions it.
- Stage 2: history appends exactly once inside `transition_candidate_state`; create seed on initiate; delete/admin do not re-append when they call transition; residual direct `save_candidate(..., state=)` only if still present post-970.
- Dropped hard claim that soft-delete bypasses validation (false after AST-970).
- Step 8 validation language points at AST-970 `prior_states` (not retired tuple list); Dependency stop-rule unchanged.
- Noted `batch_id: null` means “no batch” for AST-869 readers.
