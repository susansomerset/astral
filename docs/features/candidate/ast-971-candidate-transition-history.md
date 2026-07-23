# AST-971 — Candidate transition history

**Linear:** [AST-971](https://linear.app/astralcareermatch/issue/AST-971/candidate-transition-history-candidate-state-machine)  
**Parent:** [AST-871](https://linear.app/astralcareermatch/issue/AST-871/candidate-state-machine)  
**Publish ref:** `origin/sub/AST-871/AST-971-candidate-transition-history`

Persist enter/exit history on every successful candidate state change with parity to job/company history so prior state, new state, and timestamps support time-in-state reporting (AST-869 State Progress later). This ticket does **not** own the state vocabulary or transition allow-list (AST-970) and does **not** build the Progress UI (AST-869).

**Dependency:** blockedBy AST-970. Build against whatever sole validated transition API AST-970 leaves in `src/core/candidate.py` (today: `transition_candidate_state`). Do not invent a parallel transition path. If AST-970 renames/moves that API, stop and comment on AST-871 — do not improvise.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Add `candidate.state_history` column (CREATE + idempotent ALTER); parse JSON in `_parse_candidate_row`; accept optional `state_history` on `save_candidate` (caller-managed overwrite, preserve when omitted) | data |
| `src/core/candidate.py` | Seed history on create; append company-shaped history on every successful state write through `transition_candidate_state`, `delete_candidate`, and `save_candidate_admin` when `state` changes | core |
| `docs/features/candidate/CANDIDATE_DATA_MODEL.md` | Document `state_history` column + entry shape | docs |

## Stage 1: Data layer — `state_history` on candidate

**Done when:** Fresh and existing candidate DBs expose a parsed `state_history` list on `get_candidate` / `list_candidates`; `save_candidate(..., state_history=[...])` persists the list; omitting `state_history` on update leaves the existing column unchanged.

1. In `src/data/database.py`, extend `_ensure_candidate_schema`:
   - On **CREATE TABLE candidate**, add column `state_history TEXT DEFAULT '[]'` after `state` (or after `state_changed_at` — either is fine; keep column order consistent with the ALTER list).
   - On existing DBs, add to the idempotent migration loop: `("state_history", "TEXT DEFAULT '[]'")` alongside `candidate_api_key` / `agent_responses`.
2. In `_parse_candidate_row`, parse `state_history` the same way company/job rows do: `json.loads` → `list`; on missing/invalid → `[]`.
3. In `save_candidate`, add keyword-only arg `state_history: Optional[List[Dict[str, Any]]] = None`:
   - **INSERT (new PK):** persist `json.dumps(state_history if state_history is not None else [])` into the new column (include column in the INSERT column list).
   - **UPDATE:** if `state_history is not None`, set `state_history = ?` with `json.dumps(state_history)`; if `None`, do **not** touch the column (preserve existing), matching `save_job` caller-managed overwrite semantics.
   - Do **not** auto-append inside the data layer — core owns append (rules §2.6: data accepts state from caller; history recording stays in core next to transition).
4. Keep existing auto-`state_changed_at` behavior when `state` changes (already present). History append does not replace `state_changed_at`.

⚠️ **Decision:** Column on `candidate`, not a separate history table — mirrors job/company `state_history` JSON arrays so AST-869 can reuse the same read pattern.

## Stage 2: Core — append history on every successful state change

**Done when:** Creating a candidate seeds one history entry for the initial state; every successful `transition_candidate_state` appends one entry with prior + new state + timestamp; soft-delete and admin state overrides that actually change `state` also append; illegal transitions still raise and write nothing.

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
- `batch_id`: always include the key. Read `candidate.get("batch_id")` if present; otherwise `null`. **Do not** add a `batch_id` column in this ticket (dispatch claim is AST-972). Forward-compatible with later batch anchoring (AST-769 noted candidates lack history today).
- Timestamp format: same UTC string style already used in `transition_job_state` / `transition_company_state` / `_utc_now()` for candidates — pick the existing helper used by `save_candidate` / nearby candidate core code and use it consistently in this module (do not invent a second clock format).

⚠️ **Decision:** Prefer company-shaped entries over job-only `to_state` so prior state is explicit without scanning the previous row. AST-869 can still compute time-in-state from consecutive timestamps.

### Helpers and call sites

5. In `src/core/candidate.py`, add a small private helper (name e.g. `_append_candidate_state_history`) that:
   - Takes `candidate: dict`, `from_state: str`, `to_state: str`, `timestamp: str`.
   - Returns a **new** list = `list(candidate.get("state_history") or [])` + one entry shaped as above.
   - Does not write to the DB itself.
6. **`initiate_candidate`:** after the successful `save_candidate(..., state=<initial>)` create (today `"NEW"`; post-AST-970 whatever initial runtime state AST-970 defines, e.g. `NEW_CANDIDATE`), immediately `save_candidate` again **or** pass `state_history` on the create call with a single seed entry: `from_state=""`, `to_state=<that initial state>`, `timestamp=now`, `batch_id=null`. Prefer a single INSERT that includes both `state` and `state_history` when easy; otherwise create-then-update is fine. No second seed if the row already existed (initiate must not double-seed on re-call — if current initiate always inserts fresh, keep that behavior).
7. **`transition_candidate_state`:** keep AST-970’s validation (today: `(from_state, to_state) in candidate_state_transitions`). On success only:
   - `history = _append_candidate_state_history(candidate, from_state, to_state, now)`
   - `database.save_candidate(candidate_id, state=to_state, state_history=history)`
   - Do not change validation rules, allow-lists, or vocabulary in this ticket.
8. **`delete_candidate`:** before/with the DELETED write, append history `from_state=<current>`, `to_state="DELETED"` (or AST-970’s deleted label if renamed — use the same string this function already writes). Soft-delete remains validation-bypass; history still records the hop (parent AC #7: every successful state change).
9. **`save_candidate_admin`:** when kwargs include `state` and the loaded candidate’s current `state` differs from the requested state, append history then pass `state_history` through to `database.save_candidate` with the other kwargs. If `state` omitted or unchanged, do not append.
10. Do **not** append history for `candidate_data`-only or `candidate_api_key`-only saves.
11. Do **not** build AST-869 UI, reports, or API endpoints that aggregate time-in-state.

⚠️ **Decision:** History is owned by core write paths that change `state`, not by silent auto-append inside `database.save_candidate`. Matches job/company (`transition_*_state` appends; raw data updates do not invent history). Admin/delete are included because parent AC #7 requires every successful state change, not only allow-listed transitions.

## Stage 3: Data model doc

**Done when:** `CANDIDATE_DATA_MODEL.md` documents the column and entry shape so AST-869 / future readers do not reverse-engineer from code.

12. In `docs/features/candidate/CANDIDATE_DATA_MODEL.md`, under **Candidate table (columns)**, add:
    - **state_history** — JSON array of `{from_state, to_state, timestamp, batch_id}`; appended by core on successful state changes (AST-971). `batch_id` may be null until candidate batch claim exists.
13. In the **State machine** section, add one sentence: successful state changes append `state_history` (prior/new + timestamp) for time-in-state; Progress UI remains AST-869.

## Out of scope (do not do)

- AST-970 vocabulary / `prior_states` / transition allow-list changes
- AST-972 dispatch claim / stale aging / `batch_id` column
- AST-973 legacy row remaps
- AST-869 Progress UI
- Changing company or job history shapes
- Writing or editing `tests/` (Betty owns tests)

## Self-Assessment

**Scope:** `Single-Component` — candidate data column + core transition/delete/admin write paths that already own candidate state; no UI, no dispatch, no sibling vocabulary work.

**Conf:** `high` — mirrors existing `transition_company_state` / `transition_job_state` history append; candidate `save_candidate` already auto-bumps `state_changed_at`; gap is the missing column and core append.

**Risk:** `Medium` — wrong or missing appends break future AST-869 time-in-state and agent batch anchoring; illegal transitions must still fail closed with no partial history write. Vocabulary drift from AST-970 is a merge-order risk, not a design unknown.

## Code rules check

- §2.1 / §2.6: no new hardcoded state lists; validation stays on AST-970’s config-backed transition API.
- §2.6: core decides/records transitions; data layer only persists caller-supplied `state` + `state_history`.
- §1.3 DRY: one append helper; reuse existing UTC timestamp helper; do not fork a second history format.
- §3.3 / §3.5: no new modules; names follow `state_history` / `from_state` / `to_state` already used for company.
