# AST-1363 — Clean up agent_task so that only the right meteorite email intake task is run

<!-- linear-archive: AST-1363 archived 2026-09-09 -->

## Linear archive (AST-1363)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1363/clean-up-agent-task-so-that-only-the-right-meteorite-email-intake-task  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Low / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Actually, the scope of this ticket is JUST to remove all things gaze_email, including task and component file.

Clean up `agent_task` so that only the right meteorite email intake task is run.

Also delete old `dispatch_task` where the `task_key` is no longer in the `agent_task` table.

**Approved ancestor:** AST-1128 (gaze_email candidate-bound dispatch redesign) — retire that epic's shipped `gaze_email` stack; preserve mailbox intake under `meteorite_email`.

## As-is

AST-1128 landed a full candidate-bound `gaze_email` dispatch architecture (AST-1134 provision + schema, AST-1135 bind-filtered Avail/due, AST-1136 runner in `src/core/gaze_email.py`) that is still live: `gaze_email` `agent_task` seed row, per-candidate `dispatch_task` rows from `GAZE_EMAIL_CONFIG`, dispatcher hooks (`run_gaze_email`, `_gaze_email_due_tasks`, `provision_gaze_email_dispatch_tasks`), Admin Scheduled Actions special-casing, and Land Meteorite selected-ids via `run_gaze_email_selected_ids`. That legacy identity duplicates the meteorite-email intake surface now consolidated under `meteorite_email` (Ruth parse + dispatcher mailbox fold). Orphan `dispatch_task` rows can also remain for retired `task_key` values no longer present as current `agent_task` rows.

## To-be

The AST-1128 `gaze_email` product identity is fully retired: no `gaze_email` `agent_task` row, no `gaze_email` `dispatch_task` rows, no `GAZE_EMAIL_CONFIG` / `TASK_CONFIG["gaze_email"]`, no `src/core/gaze_email.py`, and no dispatcher/admin/inbox imports of that module. Candidate-bound mailbox intake, bind-filtered Avail, unbound Trash hygiene, `last_email_check` stamping, and Land Meteorite selected-ids run under the `meteorite_email` dispatch/config path only (reusing the same AST-1128 behavioral contracts on the surviving key). Any `dispatch_task` whose `task_key` is absent from current `agent_task` is removed (migration and/or provision cleanup).

## Proposed steps

1. Map every AST-1128 touch surface still keyed `gaze_email` (1134 provision in `dispatcher.py`/`database.py`, 1135 Avail/due in `database.py`/`api_admin.py`, 1136 runner in `gaze_email.py`, 1140 selected-ids in `api_inbox.py`) against the existing `meteorite_email` mailbox fold in config/dispatcher.
2. Rehome candidate-bound mailbox runner + selected-ids entrypoints from `gaze_email.py` onto `meteorite_email` (new thin module or `gazer.py` wrapper — plan-fix picks the split); wire dispatcher `_dispatch_one` and due/provision to `meteorite_email` only.
3. Move `GAZE_EMAIL_CONFIG` literals (`account_address`, `unbound_retention_days`, debug func names, dispatch seed) into `METEORITE_EMAIL_PARSE_CONFIG` (or a sibling meteorite-mailbox config block); update `INBOX_BIND_CONFIG` to stop aliasing `GAZE_EMAIL_CONFIG`.
4. Remove `gaze_email` from `data/admin/agent_task.json` and sync `docs/uat-fixtures/AST-756/expected-agent_task.json`; add idempotent migration to drop live DB `gaze_email` agent/dispatch rows and re-provision `meteorite_email` per-candidate rows via coverage join (AST-1134 pattern, new key).
5. Delete all `gaze_email` `dispatch_task` rows; run general orphan sweep deleting `dispatch_task` rows whose `task_key` is not in current `agent_task`.
6. Retire `tests/component/core/test_gaze_email.py` and bible `docs/test-bible/core/gaze_email.md`; retarget dispatcher/admin/inbox tests to `meteorite_email` only.

## Component scope

* `src/core/gaze_email.py` — delete after AST-1136 runner and AST-1140 selected-ids paths are rehomed under `meteorite_email`.
* `src/core/dispatcher.py` — remove AST-1134/1135 `gaze_email` provision, due merge, and dispatch branch; wire `meteorite_email` candidate-bound provision and runner call instead.
* `src/utils/config.py` — delete `GAZE_EMAIL_CONFIG` and `TASK_CONFIG["gaze_email"]`; consolidate mailbox literals into meteorite-email config; keep `INBOX_BIND_CONFIG` and admin enrichment coherent on `meteorite_email` only.
* `src/data/database.py` — migration to delete `gaze_email` dispatch rows, purge orphan `dispatch_task` rows, and (if needed) retarget AST-1135 bind-filtered Avail count queries from `gaze_email` to `meteorite_email`.
* `src/ui/api/api_inbox.py` — replace `run_gaze_email_selected_ids` with rehomed Land Meteorite selected-ids entrypoint on `meteorite_email`.
* `src/ui/api/api_admin.py` — remove `GAZE_EMAIL_CONFIG` Scheduled Actions special cases; rely on existing `is_meteorite_email_mailbox_task_key` enrichment only.
* `data/admin/agent_task.json` — remove `gaze_email` catalog row; `meteorite_email` remains the sole intake identity.
* `docs/uat-fixtures/AST-756/expected-agent_task.json` — byte-identical lockstep after gaze row removal.
* `tests/component/core/test_gaze_email.py` — delete; retarget `test_dispatcher.py`, `test_api_inbox.py`, `test_api_admin.py`, `test_config.py`, and frontend Scheduled Actions tests.
* `docs/test-bible/core/gaze_email.md` — retire or fold into meteorite-mailbox bible (Betty at Code Complete).

## Technical scope

* `src/core/gaze_email.py` — module deletion once `run_gaze_email`, `_handle_bound`, `run_gaze_email_selected_ids`, and helpers move to the `meteorite_email` home.
* `src/core/dispatcher.py` — delete `ensure_gaze_email_dispatch_task`, `provision_gaze_email_dispatch_tasks`, `_gaze_email_due_tasks`; add/rename equivalent provision+due for `meteorite_email`; modify `_dispatch_one` mailbox branch to import/call the rehomed runner.
* `src/utils/config.py` — delete `GAZE_EMAIL_CONFIG` block and asserts; extend `METEORITE_EMAIL_PARSE_CONFIG` (or sibling block) with mailbox runner literals formerly on gaze; modify `INBOX_BIND_CONFIG` and `_admin_dispatch_row_enrichment` to drop gaze branches.
* `src/data/database.py` — new idempotent migration(s): DELETE `dispatch_task` WHERE `task_key='gaze_email'`; DELETE orphan `dispatch_task` WHERE `task_key` NOT IN current `agent_task`; retarget any count/claim SQL still filtering on `gaze_email`.
* `src/ui/api/api_inbox.py` — modified land-meteorite handler calling the rehomed selected-ids async entrypoint.
* `src/ui/api/api_admin.py` — modified enrichment/filter helpers with gaze branches removed.
* Seed JSON + fixture — remove `gaze_email` object from array; no second intake row added.
* Tests / bible — delete or retarget gaze-specific coverage to `meteorite_email` dispatch runner behavior.

## Ancestor candidates

- [X] AST-1128 — gaze_email candidate-bound dispatch redesign (approved — parent epic whose shipped 1134/1135/1136 stack this ticket retires)
- [ ] AST-1134 — AST-1128 child: null-shell retirement + per-candidate `gaze_email` provision (subsumed by approved parent)
- [ ] AST-1135 — AST-1128 child: bind-filtered Avail/dispatch eligibility for `gaze_email` rows (subsumed by approved parent)
- [ ] AST-1136 — AST-1128 child: candidate-bound runner in `gaze_email.py` (subsumed by approved parent)
- [ ] AST-1140 — Land Meteorite selected-ids ingest (`run_gaze_email_selected_ids`)
- [ ] AST-1182 — Rename task to meteorite_email + AI payload epic (identity path for surviving `meteorite_email` key)
- [ ] AST-1212 — Shipped `parse_meteorite_email` → `meteorite_email` seed/config rename
- [ ] AST-1088 — Original gaze_email dispatch shell provision
- [ ] AST-1089 — Original Ruth `parse_meteorite_email` agent_task authoring
- [ ] AST-1087 — Original add-gaze_email-as-dispatch-task epic
- [ ] AST-1269 — Seed-integrity precedent for catalog rows not surviving startup apply
- [ ] AST-1282 — Dispatcher meteorite-mailbox fold (`meteorite_email` vs `gaze_email` path)

### Comments

#### chuckles — 2026-08-27T01:46:55.184Z
[check-linear] answered — **meteorite_email** is the final/canonical task key (AST-1212 rename). **parse_meteorite_email** is the legacy key; remove that one.

#### chuckles — 2026-08-27T01:45:23.010Z
[thread-missing] Cursor chat `6643d586-671d-496b-901f-08f3a095e396` has no local `store.db` on **chuckles** (expected `/home/susan/.cursor/chats/40f37617870e538aada0246cb9f8c346/6643d586-671d-496b-901f-08f3a095e396/store.db`; blob-search also empty).

Minting a **new** conversation on this host and continuing (history from the old UUID is not recovered).

Replacement UUID: `d1c247dd-f284-465b-860d-d69408e775f2`.

Watcher rule `check` on `AST-1363` (Thread owner `AST-1363`).

#### susan — 2026-08-27T01:44:42.133Z
@chuckles There are two tasks I see when I revert to the json file:

"parse_meteorite_email" and "meteorite_email".  Which one is the FINAL one, and which one needs to be removed?

#### chuckles — 2026-08-14T21:02:37.767Z
Ancestor candidates (ranked — pick one, ask about one, or reject the set):

1. **AST-1182** — Rename task to `meteorite_email` + AI payload epic. Owns the gaze→meteorite-email identity path; AST-1244 already routes related `catch_meteorite_email` / mailbox naming fixes here as a fix, not a new epic.
2. **AST-1212** — Child of AST-1182 that renamed `parse_meteorite_email` → `meteorite_email` in seed/config. Closest shipped tip for “only the right intake key is live.”
3. **AST-1128** — `gaze_email` candidate-bound dispatch redesign. Owns the mailbox `dispatch_task` shape this cleanup would prune against.
4. **AST-1089** — Original Ruth `parse_meteorite_email` `agent_task` authoring (intake catalog row).
5. **AST-1088** — Original `gaze_email` dispatch shell + `dispatch_task` provision (where orphan schedule rows often come from).
6. **AST-1269** — UAT: alias `agent_task` rows not seeded / catalog wipe that dropped meteorite identities — related seed-integrity precedent.
7. **AST-1134** — Retire null-shell candidate-bound config; prior pattern for deleting residual `gaze_email` `dispatch_task` rows.

No git seed / no plan-fix until you move this to Todo (or name a different ancestor).

#### chuckles — 2026-08-14T18:28:39.617Z
[thread-missing] Cursor chat `bc56df68-6b98-48cc-9bea-5681ad166adc` has no local `store.db` on **chuckles** (expected `/home/susan/.cursor/chats/40f37617870e538aada0246cb9f8c346/bc56df68-6b98-48cc-9bea-5681ad166adc/store.db`; blob-search also empty).

Minting a **new** conversation on this host and continuing (history from the old UUID is not recovered).

Replacement UUID: `a6c6022c-5249-4965-9d9d-1bfa378c2e93`.

Watcher rule `bug-find` on `AST-1363` (Thread owner `AST-1363`).

#### chuckles — 2026-08-14T18:17:52.353Z
[thread-missing] Cursor chat `be3e4e9d-4728-4ce3-9548-4395ea1fb7c4` has no local `store.db` on **chuckles** (expected `/home/susan/.cursor/chats/40f37617870e538aada0246cb9f8c346/be3e4e9d-4728-4ce3-9548-4395ea1fb7c4/store.db`; blob-search also empty).

Minting a **new** conversation on this host and continuing (history from the old UUID is not recovered).

Replacement UUID: `b223a02f-1f2d-4afe-b187-26292d1fc707`.

Watcher rule `bug-find` on `AST-1363` (Thread owner `AST-1363`).

---

_Implementation detail may live in git history on `origin/dev`._
