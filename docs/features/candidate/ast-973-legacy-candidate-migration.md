# Legacy candidate migration, consumers, and dispatch/task-config keys

**Linear:** [AST-973](https://linear.app/astralcareermatch/issue/AST-973/legacy-candidate-migration-consumers-and-dispatchtask-config-keys)  
**Parent:** [AST-871](https://linear.app/astralcareermatch/issue/AST-871/candidate-state-machine)  
**Publish ref:** `origin/sub/AST-871/AST-973-legacy-candidate-migration`  
**Blocked by:** AST-970 (vocabulary + transition enforcement)

Migrate persisted candidate rows and dispatch/task-config state keys off the retired four-step vocabulary onto the AST-970 registry; hard-delete existing `DELETED` candidate rows (not remap); finish consumer/nav/config string sweep so no product path still requires `NEW` / `PROFILE_READY` / `CONTEXT_READY` / `LIVE_PROMPTS` as candidate states. Does **not** invent new product flows, does **not** redefine the registry (AST-970), does **not** own transition history writes (AST-971) or dispatch claim/stale scheduling (AST-972).

**Prerequisite contract (from AST-970 plan):** runtime keys include `NEW_CANDIDATE`, `ACTIVE_SEARCH`, `DELETED`, etc.; `transition_candidate_state` enforces `prior_states`; `INFLOW_CONFIG` discovery trigger and `NAV_CONFIG` / `gen_states` already retargeted for config import coherence. This ticket owns DB remaps, hard-delete of legacy `DELETED` rows, remaining consumer literals, and a grep gate.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `CANDIDATE_LEGACY_STATE_MAP` + helper `remap_legacy_candidate_state(state)`; ensure any leftover candidate-facing literals after AST-970 are on the new vocabulary | utils |
| `src/data/database.py` | Idempotent `migrate_legacy_candidate_states()` (hard-delete `DELETED`, remap candidate.state, remap safe `dispatch_task.trigger_state`); `hard_delete_candidate(candidate_id)` cascade of candidate-scoped satellites; invoke migrate from candidate schema ensure | data |
| `src/core/candidate.py` | Thin wrappers: `hard_delete_candidate`, `purge_reap_due_candidates` (uses AST-970 `is_candidate_reap_due`); keep logical `delete_candidate` → `DELETED` | core |
| `scripts/migrations/migrate_legacy_candidate_states.py` | Operator CLI: `--dry-run` / live run wrapping the same migrate + optional `--purge-reap-due` | scripts |
| `scripts/migrations/bootstrap_candidate.py` | Stop writing retired states (`NEW` / `CONTEXT_READY`); use `CANDIDATE_CONFIG["initial_state"]` / `ACTIVE_SEARCH` as appropriate to the script’s intent | scripts |
| `src/ui/frontend/src/pages/AdminManageCandidates.tsx` | Delete confirm copy: logical delete still sets `DELETED` (reap later); no hardcoded legacy state names | ui |
| `docs/features/candidate/CANDIDATE_DATA_MODEL.md` | Document legacy remap table + hard-delete of pre-cutover `DELETED` rows | docs |

**Out of scope:** AST-970 registry shape; AST-971 history table; AST-972 claim/aging schedule wiring; deleting companies/jobs owned by a hard-deleted candidate (see Decision).

## Stage 1: Config remap table + idempotent DB migration

**Done when:** Calling migrate (dry or live) remaps `LIVE_PROMPTS` → `ACTIVE_SEARCH`, maps other legacy candidate states → `NEW_CANDIDATE`, hard-deletes rows currently in `DELETED`, remaps dispatch trigger keys per rules below, and a second run is a no-op. No candidate row remains whose `state` is outside `CANDIDATE_STATES` after live migrate.

1. In `src/utils/config.py`, add (next to `CANDIDATE_CONFIG` from AST-970):

```python
# Retired four-step names → AST-970 registry. DELETED is not remapped (hard-deleted).
CANDIDATE_LEGACY_STATE_MAP = {
    "LIVE_PROMPTS": "ACTIVE_SEARCH",
    "NEW": "NEW_CANDIDATE",
    "PROFILE_READY": "NEW_CANDIDATE",
    "CONTEXT_READY": "NEW_CANDIDATE",
}

# Candidate-only legacy labels (never job/company registry keys). Safe to remap on any
# dispatch_task.trigger_state regardless of entity_type.
CANDIDATE_LEGACY_TRIGGER_STATES = frozenset({
    "LIVE_PROMPTS", "PROFILE_READY", "CONTEXT_READY",
})

def remap_legacy_candidate_state(state: str) -> str:
    """Map a persisted candidate.state value onto CANDIDATE_STATES keys.
    Unknown non-empty values that are not already registry keys → NEW_CANDIDATE.
    Empty/None → CANDIDATE_CONFIG['initial_state']. Does not handle DELETED."""
```

   Implement `remap_legacy_candidate_state` exactly:
   - If `state` in `CANDIDATE_STATES`: return `state`.
   - If `state` in `CANDIDATE_LEGACY_STATE_MAP`: return mapped value.
   - If `state` is `DELETED`: raise `ValueError` (caller must hard-delete, not remap).
   - Otherwise return `CANDIDATE_CONFIG["initial_state"]` (`NEW_CANDIDATE`).

   Assert every map **value** is in `CANDIDATE_STATES` and `"DELETED" not in CANDIDATE_LEGACY_STATE_MAP`.

2. In `src/data/database.py`, add `hard_delete_candidate(astral_candidate_id: str) -> Dict[str, int]` that, in one transaction, deletes candidate-scoped rows then the candidate row. Counts keys at minimum: `dispatch_task`, `candidate_intake_session`, `company_search_terms`, `rubric_vector`, `vector_feedback`, `candidate`. Also delete `agent_data` / `agent_responses` rows where `entity_type='candidate'` and `entity_id=astral_candidate_id` when those tables store candidate entities that way (match existing column names in this file). Do **not** delete `job` or `company` rows.

   ⚠️ **Decision:** Hard-delete removes the candidate row and candidate-scoped satellites listed above. Companies/jobs that still point at that `candidate_id` are left in place (same posture as AST-729 leaving related agent rows for deleted jobs). Full tenant wipe is out of scope.

3. Add `migrate_legacy_candidate_states(*, dry_run: bool = False) -> Dict[str, int]` in `database.py`:

   **Phase A — hard-delete logical DELETED**
   - `SELECT astral_candidate_id FROM candidate WHERE state = 'DELETED'`.
   - For each id: if `dry_run`, count only; else `hard_delete_candidate(id)`.
   - Count `deleted_hard`.

   **Phase B — remap candidate.state**
   - Select all remaining candidates.
   - For each row, `new_state = remap_legacy_candidate_state(old_state)` (skip if equal).
   - If not dry_run: `UPDATE candidate SET state=?, state_changed_at=state_changed_at, updated_at=now` — **preserve** `state_changed_at` on remap so stale aging clocks are not reset by cutover.
   - Count `states_remapped`. Never write a state absent from `CANDIDATE_STATES`.

   **Phase C — remap dispatch_task.trigger_state**
   - For each `dispatch_task` row:
     - If `trigger_state` in `CANDIDATE_LEGACY_TRIGGER_STATES`: map via `CANDIDATE_LEGACY_STATE_MAP` (all such keys are in the map).
     - Else if `entity_type == 'candidate'` and `trigger_state == 'NEW'`: map to `NEW_CANDIDATE`.
     - Else if `entity_type == 'candidate'` and `trigger_state` not in `CANDIDATE_STATES` and not empty: map via `remap_legacy_candidate_state(trigger_state)`.
     - Do **not** remap job/company `NEW` / other job-company registry keys.
   - On unique conflicts `(candidate_id, task_key, trigger_state)` after remap: keep one row (prefer the pre-existing target-key row if present; else keep lowest `id`) and delete the duplicate. Count `dispatch_triggers_remapped`, `dispatch_trigger_dupes_removed`.

   Return counts dict; idempotent on second live run (all counts zero except possibly scanned).

4. Invoke `migrate_legacy_candidate_states(dry_run=False)` from the candidate schema-ensure path that already runs on first DB access (same file as `_ensure_*` for `candidate`), so staging/production self-heal when AST-973 code loads. Keep the function import-safe if `CANDIDATE_STATES` is already the new registry (Phase B/C no-ops when no legacy values remain).

5. Add `scripts/migrations/migrate_legacy_candidate_states.py`:
   - argparse: `--dry-run` (default True unless `--execute`), `--execute` for live, `--purge-reap-due` optional flag calling core purge (Stage 2).
   - Print counts; exit 0.
   - Docstring: backup DB first; run `--dry-run` then `--execute` after Susan OK on production.

## Stage 2: Reap-due hard delete (production timer completion)

**Done when:** Candidates in `DELETED` with due reap (AST-970 lifecycle fields) can be hard-deleted via one core entrypoint; migration of pre-cutover `DELETED` rows (no lifecycle blob) already handled in Stage 1 Phase A.

1. In `src/core/candidate.py`, add:

```python
def hard_delete_candidate(candidate_id: str) -> Dict[str, int]:
    """Physical delete — database.hard_delete_candidate. Not a state transition."""
    return database.hard_delete_candidate(candidate_id)

def purge_reap_due_candidates(*, now=None) -> int:
    """Hard-delete every candidate where is_candidate_reap_due(...). Return count."""
```

   Implementation: `list_candidates(include_deleted=True)`, filter `state=='DELETED'` and `is_candidate_reap_due`, call `hard_delete_candidate` each. No dispatcher registration here (AST-972 may call later; CLI `--purge-reap-due` is enough for this ticket).

2. Wire `scripts/migrations/migrate_legacy_candidate_states.py --purge-reap-due` to call `purge_reap_due_candidates` after (or instead of, when flag-only) the legacy migrate when `--execute` is set. Dry-run lists due ids without deleting.

## Stage 3: Consumer sweep + grep gate

**Done when:** Under `src/` and `scripts/` (product paths), no remaining required use of retired candidate state string literals as live vocabulary; admin UI still loads states from `/api/candidates/states`; Manage Candidates delete copy does not claim hard-delete.

1. After AST-970’s config-local retargets, finish any remaining product consumers this ticket owns:
   - `scripts/migrations/bootstrap_candidate.py`: replace `state="NEW"` / `state="CONTEXT_READY"` with `CANDIDATE_CONFIG["initial_state"]` and, for the “ready for prompts” bootstrap end state, `ACTIVE_SEARCH` (script intent: candidate usable for generation — document in a one-line comment).
   - `src/ui/frontend/src/pages/AdminManageCandidates.tsx`: keep confirm as logical delete to `DELETED`; do not introduce hardcoded `LIVE_PROMPTS` / `PROFILE_READY` / etc. (states already from API).
   - Grep `src/` + `scripts/` for `LIVE_PROMPTS`, `PROFILE_READY`, `CONTEXT_READY` as candidate vocabulary. Allowed leftovers: comments pointing at this migration, `CANDIDATE_LEGACY_*` map keys, and string literals inside `migrate_legacy_candidate_states` / remap helpers. Job/company uses of unrelated tokens must not be rewritten.
   - Confirm `INFLOW_CONFIG["discovery"]["dispatch_trigger_state"]` is `ACTIVE_SEARCH` (AST-970); if still `LIVE_PROMPTS` on the integration line when this builds, set it here (consumer coherence).

2. Grep gate (builder runs before stage-complete commit):

```bash
rg -n 'LIVE_PROMPTS|PROFILE_READY|CONTEXT_READY' src scripts \
  --glob '!**/migrate_legacy_candidate_states*' 
# Fail the stage if matches remain outside CANDIDATE_LEGACY_* definitions,
# remap helpers, or explicit "legacy" comments in database migrate function.
```

   Also assert no `candidate_state_transitions` key remains (AST-970 removal); if present, stop and escalate — do not reintroduce.

3. Do **not** edit `tests/` or the test bible (Betty). Do **not** expand nav beyond ensuring config gates use new names (AST-970 + this sweep).

## Stage 4: Data-model doc note

**Done when:** `CANDIDATE_DATA_MODEL.md` documents the one-time remap table and that pre-cutover `DELETED` rows are hard-deleted by `migrate_legacy_candidate_states`.

1. Append a short **Legacy cutover (AST-973)** subsection under the state machine section:
   - Map table matching `CANDIDATE_LEGACY_STATE_MAP`.
   - `DELETED` → hard delete (not remapped).
   - `dispatch_task.trigger_state`: `LIVE_PROMPTS`/`PROFILE_READY`/`CONTEXT_READY` always; `NEW` only when `entity_type='candidate'`.
   - Operator script path + schema-ensure auto-run.

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — data-layer migration + hard-delete cascade + config remap table + consumer/script sweep; depends on AST-970 registry already on the branch line at build time.

**Conf:** `high` — parent AC #8–#10 and AST-970 out-of-scope handoff are explicit; remap rules distinguish candidate-only triggers from job/company `NEW`.

**Risk:** `HIGH` — wrong dispatch remap could break scheduled actions; hard-delete is irreversible for `DELETED` rows; mitigated by `--dry-run` default on CLI, idempotent migrate, unique-constraint dupe handling, and preserving `state_changed_at` on remap.

## Code Rules self-review

| Rule | Result |
|------|--------|
| §1.3 DRY | Single map in config; database migrate is the only writer of remaps |
| §2.1 config SSOT | Legacy map + new vocabulary in config; no hardcoded remap dict in the CLI |
| §2.4 batch | No new claim APIs |
| §2.6 state machine | Remap runs before enforcement; does not invent transitions; hard-delete is not a state hop |
| §3.3 imports | CLI → database/core; core wraps data hard-delete |
| §3.5 naming | Legacy keys only inside `CANDIDATE_LEGACY_*` |

No unresolved conflicts with AST-970 boundaries.
