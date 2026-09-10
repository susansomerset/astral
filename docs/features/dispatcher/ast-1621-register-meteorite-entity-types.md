# AST-1621 — Register meteorite in ENTITY_TYPES and dispatch registries

- **Linear:** https://linear.app/astralcareermatch/issue/AST-1621
- **Parent:** AST-1620 — Treat meteorite as a first-class dispatch entity_type
- **Publish ref:** `sub/AST-1620/AST-1621-register-meteorite-entity-types`

Register `meteorite` as a first-class member of `ENTITY_TYPES` and wire the shared dispatch state/claim/sort helpers to `METEORITE_STATES`, then flip ingress + BOT_BLOCKED notify seed SQL to store `entity_type='meteorite'` instead of NULL. Leaves count/due/Available runtime and ledger/live-row backfill to siblings AST-1622 / AST-1623.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Append `meteorite` to `ENTITY_TYPES`; map it in `dispatch_entity_state_registry`, `dispatch_claim_states`, and `_dispatch_sort_by_for`; set ingress + bot-blocked `SEED_CONFIG` SQL `entity_type` to `'meteorite'` | utils |
| `docs/ASTRAL_CODE_RULES.md` | ENTITY_TYPES bullet and §2.4 claim-queue member list include `meteorite` | docs |

## Stage 1: ENTITY_TYPES + dispatch registries + sort default

**Done when:** `from src.utils.config import ENTITY_TYPES, METEORITE_STATES, dispatch_entity_state_registry, dispatch_claim_states, _dispatch_sort_by_for` works; `'meteorite' in ENTITY_TYPES`; `set(dispatch_entity_state_registry("meteorite")) == set(METEORITE_STATES)`; `_dispatch_sort_by_for("meteorite", "NEW") == "updated_at"`; `dispatch_claim_states("NEW", "meteorite")` returns a non-empty list whose first element is `"NEW"` (companion `*_RETRY` only if present in `METEORITE_STATES` — today none are).

1. In `src/utils/config.py`, change `ENTITY_TYPES = ["candidate", "company", "job"]` to `ENTITY_TYPES = ["candidate", "company", "job", "meteorite"]`. Keep the existing header comment above the list; do not invent a second entity-type constant elsewhere.
2. In `dispatch_entity_state_registry`, add `"meteorite": METEORITE_STATES` to the local `registries` dict alongside `job` / `company` / `candidate`. Keep the existing `KeyError` for unknown types.
3. In `dispatch_claim_states`, extend the registry resolution so `entity_type == "meteorite"` selects `METEORITE_STATES` (same nested-if / ternary shape already used for job/company/candidate). Leave the retry / companion-`*_RETRY` logic unchanged — it already operates on whichever registry was selected. Do not call `dispatch_entity_state_registry` from this function unless the surrounding code already does (it does not today).
4. In `_dispatch_sort_by_for`, before the final `raise KeyError(f"dispatch sort_by: unknown entity_type …")`, add:

   ```python
   if entity_type == "meteorite":
       return "updated_at"
   ```

   Do not validate `trigger_state` against `METEORITE_STATES` here (job validates; company/candidate do not require a successful registry hit for every trigger before returning a default — meteorite matches the ingress seed default).

⚠️ **Decision:** Meteorite sort default is the literal `"updated_at"`, matching the existing `SEED_CONFIG` ingress / bot-blocked `sort_by` values and the parent technical scope. Do not invent a `batch_criteria.sort_by` block on `METEORITE_STATES` in this ticket.

## Stage 2: SEED_CONFIG entity_type literals for ingress + bot-blocked notify

**Done when:** `grep` of `SEED_CONFIG["dispatch_task-meteorite-ingress"]` and `SEED_CONFIG["dispatch_task-meteorite-bot-blocked-notify"]` string values shows `'meteorite'` in the `entity_type` column position for `stage_meteorite` / `scrape_meteorite` / `land_meteorite` / `meteorite_bot_blocked_notify`, and no longer shows `, NULL, 'NEW'` / `, NULL, 'SCRAPE_LINK'` / `, NULL, 'READY'` / `, NULL, 'BOT_BLOCKED'` in those four INSERT SELECT lists. `dispatch_task-meteorite-retention` still inserts `entity_type` as NULL with `trigger_state` NULL. Job-track `dispatch_task-meteorite` seeds remain `entity_type='job'`.

1. In `SEED_CONFIG["dispatch_task-meteorite-ingress"]`, in each of the three INSERT SELECT clauses, replace the third SELECT value `NULL` (the `entity_type` column after `task_key`) with the string literal `'meteorite'`:
   - `stage_meteorite`: `) SELECT NULL, 'stage_meteorite', 'meteorite', 'NEW', 'updated_at', …`
   - `scrape_meteorite`: `) SELECT NULL, 'scrape_meteorite', 'meteorite', 'SCRAPE_LINK', 'updated_at', …`
   - `land_meteorite`: `) SELECT NULL, 'land_meteorite', 'meteorite', 'READY', 'updated_at', …`
2. In `SEED_CONFIG["dispatch_task-meteorite-bot-blocked-notify"]`, same replacement: `) SELECT NULL, 'meteorite_bot_blocked_notify', 'meteorite', 'BOT_BLOCKED', 'updated_at', …`
3. Leave `SEED_CONFIG["dispatch_task-meteorite-retention"]` unchanged (`entity_type` NULL, `trigger_state` NULL). Leave `SEED_CONFIG["dispatch_task-meteorite"]` (job-lifecycle qualify/evaluate/grade seeds) unchanged (`entity_type` `'job'`). Do not change `auto_mode` (stays `0` / false per `astral.dispatch.seed-auto-false`).

⚠️ **Decision:** Seed SQL only — no live-row `UPDATE` of existing NULL `dispatch_task.entity_type` values. That backfill is AST-1623. `INSERT … WHERE NOT EXISTS` will not rewrite rows already present with NULL.

## Stage 3: Code Rules ENTITY_TYPES + §2.4 claim-queue wording

**Done when:** `docs/ASTRAL_CODE_RULES.md` §2.1 ENTITY_TYPES bullet lists `meteorite` with the other members, and the §2.4 sentence that names claim-queue members includes `meteorite`.

1. In `docs/ASTRAL_CODE_RULES.md` §2.1 Config blocks, update the **ENTITY_TYPES** bullet from `(candidate, company, job)` to `(candidate, company, job, meteorite)`. Keep the rest of that bullet's wording (agent_data / dispatch_ledger / retired agent_responses notes) intact.
2. In §2.4 Batch Processing Pattern, update the claim-queue member parenthetical from ``(`candidate`, `company`, `job`)`` to ``(`candidate`, `company`, `job`, `meteorite`)`` in the sentence that begins "Every `ENTITY_TYPES` member used as a dispatch claim queue". Do not rewrite the rest of §2.4 (claim → process → release narrative, batch_id format, dispatcher pseudocode).

## Out of scope (siblings — do not touch)

- `src/data/database.py` `count_eligible_for_dispatch_task` / `get_due_tasks` (AST-1622)
- `src/ui/api/api_admin.py` state_options / Available / validation (AST-1623)
- `src/core/dispatcher.py` ledger `entity_type='meteorite'` and live-row NULL→meteorite UPDATE (AST-1623)
- Rewriting custom meteorite runners into consult / `_run_unified`
- Forcing retention or `meteorite_email` mailbox onto ENTITY_TYPES claim semantics

## Estimate

Confirm Chuckles estimate: 2 — agree
