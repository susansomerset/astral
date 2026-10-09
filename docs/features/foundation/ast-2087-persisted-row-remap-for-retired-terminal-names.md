# AST-2087 — Persisted-row remap for retired terminal names

- **Parent:** [AST-2073 — Revise terminal states](https://linear.app/astralcareermatch/issue/AST-2073)
- **Ticket:** [AST-2087](https://linear.app/astralcareermatch/issue/AST-2087)
- **Publish ref:** `origin/sub/AST-2073/AST-2087-terminal-state-remap` (off `ftr/AST-2073-revise-terminal-states`)
- **Depends on:** [AST-2086](https://linear.app/astralcareermatch/issue/AST-2086) (merged into ftr at `b41a8f17f`). Its `RETIRED_TERMINAL_STATE_MAP` in `src/utils/config.py` is the only input this ticket reads.
- **Canon scope:** `stat.dispatch.entity-state-bound` (read in full). There is no `docs/canon-index.md` in this tree or on `origin/dev`, so the id was resolved directly to `canon/directives/active/stat.dispatch.entity-state-bound.md`.

After AST-2086, existing job, company, candidate and meteorite rows, plus live `dispatch_task` rows, can still sit on retired terminal names. This ticket adds a conn-bound remap in `src/data/database.py` and an operator CLI, `scripts/migrations/migrate_terminal_state_names.py`, which is a dry run by default and applies changes only with `--execute`. The remap reads `RETIRED_TERMINAL_STATE_MAP`. A single-target retired name maps directly. A multi-target name is resolved either from the row's last `state_history` predecessor (a trigger state, or a `<TRIGGER>.<hop>` label resolved to a task_key) or, for the meteorite expired link, from the `scrape_closed` / `scrape_missing` prefix in `error`. Unresolvable rows are left untouched and counted. Dead-state rows are left untouched and counted under `unregistered`. The remap only ever writes `state` and `dispatch_task.trigger_state`. It never writes `state_history`, `state_changed_at` or `updated_at`, and it is never called from schema-ensure.

---

## Scope gate

Checked against this ticket's `## Scope` (verbatim from parent).

| Need | Covered by Scope? |
|------|-------------------|
| `src/data/database.py`: new conn-bound remap of entity `state` + `dispatch_task.trigger_state` from the retired-name map; public wrapper | Yes ("new conn-bound remap function") |
| `src/data/database.py`: the one comment naming `NEW_EMAIL_ERROR` (line 4165) | Yes ("one comment naming `NEW_EMAIL_ERROR`") |
| `src/data/database.py`: add config names to the existing `from src.utils.config import (...)` block | Yes (part of the same function change) |
| `scripts/migrations/migrate_terminal_state_names.py`: new CLI | Yes |

No config, core, seed, or test file is touched. `RETIRED_TERMINAL_STATE_MAP` is consumed exactly as AST-2086 shipped it.

---

## Facts the plan relies on (verified on `b41a8f17f`)

1. **Map shape.** `RETIRED_TERMINAL_STATE_MAP[entity][old_name] = {key: new_name}`. Here `key` is the writing task_key, except for meteorite `LINK_EXPIRED`, whose keys are the page statuses `closed` / `missing`. Config asserts already guarantee that every `new_name` is registered and that no `old_name` is. The map never lists the dead states.
2. **Single vs multi target.** Single-target entries need no row data. Multi-target entries are: job `FAILED_TECHNICAL`, `JD_SCRAPE_FAIL`, `JD_SCRAPE_FAIL_COOKIE`, `BOT_BLOCKED`, `NEED_WEBSITE_CONTENT`, `ERROR_BUILD_ARTIFACTS`; company `NO_WEBSITE`, `CANNOT_READ_WEBSITE`, `JOBSITE_SCRAPE_ISSUE`; candidate `REQUESTED_RESUME_ERROR`, `REQUESTED_ARTIFACTS_ERROR`; meteorite `LINK_EXPIRED`, `SCRAPE_ERROR`.
3. **Catalog trigger per task_key.** `dispatch_task_admin_defaults(k)["trigger_state"]` (already imported in `database.py`) returned the same value as `_dispatch_trigger_state_for_task_key` for every map key and every `TASK_CONFIG` key, and raised `KeyError` in the same cases. Those cases are the chain hops after the entry hop, plus `closed` / `missing`. Within each multi-target entry, the triggers are distinct, with one exception: `ERROR_BUILD_ARTIFACTS`, where all ten artifact hops resolve to `BUILD_ARTIFACTS`.
4. **History entry shapes.** Job and meteorite entries are `{to_state, timestamp, …}` with no `from_state`. Company and candidate entries also carry `from_state`. Meteorite insert-time history is a single entry, so `NEW_EMAIL_ERROR` rows have no predecessor. That is fine, because `NEW_EMAIL_ERROR` is a single-target entry.
5. **Hop labels name the completed hop.** `write_job_dispatch_hop_label` and `write_candidate_dispatch_hop_label` write `<TRIGGER>.<completed_task_key>` after a hop succeeds. `dispatch_chain_row_matches_job` claims label `T.x` for the row whose task_key is `agent_task(x).run_next`. A failure recorded right after label `T.x` therefore belongs to the hop `run_next(x)`.
6. **Live `run_next` is the chain truth, not the config tuples.** In `agent_task` (`current = 1`) the craft chain runs `craft_company_search_terms → craft_joblist_rubric → craft_jobdesc_rubric → craft_do_rubric → craft_get_rubric → craft_like_rubric → craft_prefilter_rubric`. That is not the order of `CANDIDATE_CRAFT_CHAIN_TASK_KEYS`.
7. **Meteorite expired-link error.** Pre-AST-2086 `run_scrape_meteorite` wrote `error = f"scrape_{page_status} signal=… text_len=… final_url=…"` on `LINK_EXPIRED`. Its first whitespace token is `scrape_closed` or `scrape_missing`.
8. **No SQLite triggers** on any table, so `UPDATE … SET state` touches nothing else.
9. **dispatch_task.** The only unique index is `idx_dispatch_task_null_candidate_task_key ON dispatch_task(task_key) WHERE candidate_id IS NULL`. Rewriting `trigger_state` in place on the same row cannot collide with it.
10. **AC 2 grep constraint.** AC 2 greps `src` (excluding `config.py`) for every retired and dead name. The new code must therefore type none of them, and must type neither `BOT_BLOCKED` nor `LINK_EXPIRED`. Everything is derived from the map and from config. Today the only hit is the line 4165 comment, which Stage 1 fixes.

---

## Resolution rules (what the code below implements)

For a row on retired `old` with map entry `by_key = MAP[entity][old]`:

1. **Single target.** If `len(by_key) == 1`, the row gets that value.
2. **Page-status keys.** If every key of `by_key` is a key of `METEORITE_INGRESS_DISPATCH_CONFIG["scrape_page_status_states"]`, the row gets `by_key[status]` where the first token of `error` is `scrape_<status>`. Otherwise the row is unresolved.
3. **Bare-error families widen.** If every value in `by_key` equals `error_state_for(key)`, the entry is a bare per-task family (`FAILED_TECHNICAL`, `ERROR_BUILD_ARTIFACTS`, `REQUESTED_*_ERROR`). The candidate targets then also include `{k: error_state_for(k)}` for every `TASK_CONFIG` key `k` whose bare error is a key of the entity's registry. This implements the config comment "A FAILED_TECHNICAL row whose history names any other task_key resolves to error_state_for(task_key)" without typing the retired name.
4. **Predecessor.** Find the last history entry whose `to_state == old`. The predecessor is that entry's `from_state` when it is non-empty, else the previous entry's `to_state`. With no such entry, or no predecessor, the row is unresolved. A `_RETRY` suffix is stripped (`retry_base`).
5. **Hop label predecessor.** If `parse_dispatch_hop_label(pred)` gives `(trigger, completed)`, the failing task is `run_next[completed]` from live `agent_task`. The row gets `targets[failing]`. If that task has no target, the row is unresolved.
6. **Trigger predecessor.** Otherwise, the matches are the targets whose catalog trigger equals `pred`. If there is more than one match (artifact chain on bare `BUILD_ARTIFACTS`), intersect with the task_keys of `dispatch_task` rows whose `trigger_state == pred` and whose `candidate_id` is the row's candidate or NULL. The row resolves only when exactly one match remains.

**`dispatch_task` rows** whose `trigger_state` is any retired `old` (in any entity) get the task_key's catalog trigger (`dispatch_task_admin_defaults`), but only when that trigger is one of `old`'s map targets. Otherwise they are skipped and counted. This follows `stat.dispatch.entity-state-bound`: the catalog default wins, and the result must be a real registry state that the runner claims by. For `meteorite_bot_blocked_notify` the result is `BOT_BLOCKED → BOT_BLOCKED_SCRAPE_METEORITE`.

⚠️ **Decision: hop labels are completed hops, including legacy `BUILD_ARTIFACTS.<hop>`.** Legacy AST-803 compounds and current labels share the `BUILD_ARTIFACTS.` prefix and cannot be told apart. The live claim path (`dispatch_chain_row_matches_job`) reads every such label as "completed hop", so the remap does the same. A legacy row whose label actually meant "hop in progress" would resolve to the following hop's error. That error is in the same chain and carries the same Skipped label and bulk-retry target (`RECOMMENDED`), so the Skipped retry behaves identically.

⚠️ **Decision: rule 3 widens all bare-error families, not only `FAILED_TECHNICAL`.** `database.py` cannot type `FAILED_TECHNICAL` (AC 2), so the family is recognised by shape. For `ERROR_BUILD_ARTIFACTS` and the candidate chains, the widening only adds tasks whose bare error is already registered on that entity. That is exactly the parent's "ERROR_<HOP TASK_KEY> per hop" intent (e.g. resume-chain hops for `REQUESTED_RESUME_ERROR`). An unregistered target is never produced.

⚠️ **Decision: the shared-trigger tie-break reads `dispatch_task`, not a hard-coded chain head.** `BUILD_CONFIG.resume_artifact_chain.first_task_key` is `contemplate_job`, while live `run_next` starts the chain at `anticipate_scan`. Which hop claims a bare `BUILD_ARTIFACTS` job depends on that candidate's dispatch rows, so the row's own candidate decides. If the result is ambiguous or empty, the row is unresolved and counted.

⚠️ **Decision: no schema-ensure inside the remap.** `_ensure_*` functions can seed or alter rows (`_ensure_dispatch_task_schema` seeds), and a dry run must write nothing. The operator runs the remap against an app-initialised DB. A missing table surfaces as `sqlite3.OperationalError`.

⚠️ **Decision: `updated_at` is not touched.** Scope says the remap "rewrites `state`". The legacy candidate migrate bumped `updated_at`, but nothing here asks for it, so leaving it alone keeps the write surface to `state` / `trigger_state` only.

**Dead states** (`PREFILTER_UNKNOWN`, `HARD_PARSE`, `BUILD_FAILED`) are not in the map, so no UPDATE can touch them. They are counted, keyed by the state name read from the data, under `unregistered[entity][state]`: any state that is not registered (`registered_base`), not a hop label (after `retry_base`), and not a retired map key. No dead name is typed.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Add 6 config imports; add `_TERMINAL_REMAP_ENTITIES`, `_terminal_predecessor`, `_resolve_retired_terminal_state`, `_terminal_state_remap_conn`, `migrate_terminal_state_names` after `migrate_legacy_candidate_states`; reword the line-4165 comment | data |
| `scripts/migrations/migrate_terminal_state_names.py` | New operator CLI (dry run default, `--execute`) | scripts |

**Build-agent note:** `.cursorignore` lists an unanchored `data/` that also matches `src/data/`, so the IDE Read/Grep tools refuse `src/data/database.py`. Read it with `sed -n` / `rg` in the shell, and edit with exact-string replacement. Do **not** change `.cursorignore` (out of scope).

---

## Stage 1: Conn-bound remap in `src/data/database.py`

**Done when:** `python3 -c "from src.data import database as d; import json; print(json.dumps(d.migrate_terminal_state_names(dry_run=True), indent=2))"` prints the result dict with keys `dry_run`, `remapped`, `skipped`, `unregistered`, `dispatch_task`. The AC 2 `git grep` from the parent prints nothing for `src/data/database.py`.

1. In `src/data/database.py`, in the `from src.utils.config import (` block (line 72), add these names directly after `ENTITY_TYPES,`:
   ```python
       JOB_STATES,
       METEORITE_INGRESS_DISPATCH_CONFIG,
       RETIRED_TERMINAL_STATE_MAP,
       error_state_for,
       parse_dispatch_hop_label,
       retry_base,
   ```
   `registered_base`, `TASK_CONFIG`, `COMPANY_STATES`, `CANDIDATE_STATES`, `METEORITE_STATES` and `dispatch_task_admin_defaults` are already imported. Do not duplicate them.

2. At line 4164–4165, replace the comment
   ```python
                   # state defaults to NEW when omitted, but a caller-supplied state (e.g.
                   # NEW_EMAIL_ERROR from _new_email_error_row) is respected, not overridden.
   ```
   with
   ```python
                   # state defaults to NEW when omitted, but a caller-supplied state (e.g. the
                   # stage_error_state from _new_email_error_row) is respected, not overridden.
   ```

3. Directly after the end of `migrate_legacy_candidate_states` (the `return _run_with_retry(_with_conn)` line before `def _ensure_company_candidate_fk`), insert this block verbatim:
   ```python
   # AST-2087: entity -> (registry, primary key, candidate_id column) for the retired terminal-state remap.
   _TERMINAL_REMAP_ENTITIES: Dict[str, Tuple[Dict[str, Any], str, str]] = {
       "job": (JOB_STATES, "astral_job_id", "candidate_id"),
       "company": (COMPANY_STATES, "short_name", "candidate_id"),
       "candidate": (CANDIDATE_STATES, "astral_candidate_id", "astral_candidate_id"),
       "meteorite": (METEORITE_STATES, "id", "candidate_id"),
   }
   assert set(_TERMINAL_REMAP_ENTITIES) == set(RETIRED_TERMINAL_STATE_MAP)


   def _terminal_predecessor(raw_history: Optional[str], state: str) -> Optional[str]:
       """State the row left to land on `state`: the last such entry's from_state, else the prior to_state."""
       try:
           hist = json.loads(raw_history or "[]")
       except (TypeError, ValueError):
           return None
       for i in range(len(hist) - 1, -1, -1):
           entry = hist[i] if isinstance(hist[i], dict) else {}
           if entry.get("to_state") != state:
               continue
           # job/meteorite entries carry no from_state; company/candidate do
           prev = hist[i - 1] if i and isinstance(hist[i - 1], dict) else {}
           return entry.get("from_state") or prev.get("to_state")
       return None


   def _resolve_retired_terminal_state(
       old: str,
       by_key: Dict[str, str],
       registry: Dict[str, Any],
       row: sqlite3.Row,
       cid: Optional[str],
       triggers: Dict[str, Optional[str]],
       run_next: Dict[str, str],
       dispatch: Dict[Tuple[Optional[str], str], set],
   ) -> Optional[str]:
       """New name for a row on retired `old`, or None when its data can't decide (row left as-is)."""
       if len(by_key) == 1:
           return next(iter(by_key.values()))
       # Keys are scrape page statuses (meteorite expired link): run_scrape_meteorite wrote
       # error = "scrape_<status> signal=… text_len=… final_url=…".
       if set(by_key) <= set(METEORITE_INGRESS_DISPATCH_CONFIG["scrape_page_status_states"]):
           head = (row["error"] or "").split(" ", 1)[0]
           return next((new for status, new in by_key.items() if head == f"scrape_{status}"), None)
       targets = dict(by_key)
       # Bare per-task family (every value is error_state_for(key)): any task whose bare error
       # is registered on this entity resolves to it (config RETIRED_TERMINAL_STATE_MAP comment).
       if all(new == error_state_for(k) for k, new in by_key.items()):
           for k in TASK_CONFIG:
               if k not in targets and error_state_for(k) in registry:
                   targets[k] = error_state_for(k)
       pred = _terminal_predecessor(row["state_history"], old)
       if not pred:
           return None
       pred = retry_base(pred) or pred
       hop = parse_dispatch_hop_label(pred)
       if hop is not None:
           # <TRIGGER>.<hop> names the completed hop; the one that failed is its live run_next.
           return targets.get(run_next.get(hop[1], ""))
       matches = {k for k in targets if triggers.get(k) == pred}
       if len(matches) > 1:
           # Shared trigger (artifact chain on bare BUILD_ARTIFACTS): the row's own dispatch rows name the claimant.
           matches &= dispatch.get((cid, pred), set()) | dispatch.get((None, pred), set())
       return targets[matches.pop()] if len(matches) == 1 else None


   def _terminal_state_remap_conn(conn: sqlite3.Connection, *, dry_run: bool) -> Dict[str, Any]:
       """Conn-bound retired terminal-state remap (AST-2087).

       Writes only entity `state` and dispatch_task.trigger_state — never state_history,
       state_changed_at, or updated_at. Explicit op: never called from schema-ensure.
       """
       out: Dict[str, Any] = {
           "dry_run": dry_run,
           "remapped": {},      # entity -> old -> new -> count
           "skipped": {},       # entity -> old -> count (retired rows left as-is)
           "unregistered": {},  # entity -> state -> count (dead / unknown states, untouched)
           "dispatch_task": {"remapped": {}, "skipped": {}},
       }

       def _catalog_trigger(k: str) -> Optional[str]:
           try:
               return dispatch_task_admin_defaults(k)["trigger_state"]
           except KeyError:
               return None

       task_keys = set(TASK_CONFIG) | {k for olds in RETIRED_TERMINAL_STATE_MAP.values() for m in olds.values() for k in m}
       triggers = {k: _catalog_trigger(k) for k in task_keys}
       # Live chain order (agent_task.run_next) — the config chain tuples are not run_next order.
       run_next = {
           r["task_key"]: (r["run_next"] or "").strip()
           for r in conn.execute("SELECT task_key, run_next FROM agent_task WHERE current = 1")
       }
       # (candidate_id, trigger_state) -> task_keys; NULL candidate_id rows apply to every candidate.
       dispatch: Dict[Tuple[Optional[str], str], set] = {}
       for r in conn.execute("SELECT candidate_id, task_key, trigger_state FROM dispatch_task"):
           dispatch.setdefault((r["candidate_id"], r["trigger_state"] or ""), set()).add(r["task_key"])

       for entity, olds in RETIRED_TERMINAL_STATE_MAP.items():
           registry, pk, cid_col = _TERMINAL_REMAP_ENTITIES[entity]
           remapped = out["remapped"].setdefault(entity, {})
           skipped = out["skipped"].setdefault(entity, {})
           error_col = ", error" if entity == "meteorite" else ""
           marks = ",".join("?" * len(olds))
           rows = conn.execute(
               f"SELECT {pk}, {cid_col}, state, state_history{error_col} FROM {entity} WHERE state IN ({marks})",
               tuple(olds),
           ).fetchall()
           for row in rows:
               old = row["state"]
               new = _resolve_retired_terminal_state(
                   old, olds[old], registry, row, row[cid_col], triggers, run_next, dispatch,
               )
               if new is None:
                   skipped[old] = skipped.get(old, 0) + 1
                   continue
               by_new = remapped.setdefault(old, {})
               by_new[new] = by_new.get(new, 0) + 1
               if not dry_run:
                   conn.execute(f"UPDATE {entity} SET state = ? WHERE {pk} = ? AND state = ?", (new, row[pk], old))
           # Dead / unknown states: not registered, not a hop label, not retired — counted, never written.
           unregistered = out["unregistered"].setdefault(entity, {})
           for r in conn.execute(f"SELECT state, COUNT(*) AS n FROM {entity} GROUP BY state"):
               s = r["state"] or ""
               if s not in olds and registered_base(registry, s) is None and parse_dispatch_hop_label(retry_base(s) or s) is None:
                   unregistered[s] = r["n"]

       # dispatch_task: catalog trigger wins, and must be one of the retired name's map targets
       # (stat.dispatch.entity-state-bound).
       targets_of: Dict[str, set] = {}
       for olds in RETIRED_TERMINAL_STATE_MAP.values():
           for old, by_key in olds.items():
               targets_of.setdefault(old, set()).update(by_key.values())
       marks = ",".join("?" * len(targets_of))
       for r in conn.execute(
           f"SELECT id, task_key, trigger_state FROM dispatch_task WHERE trigger_state IN ({marks})",
           tuple(targets_of),
       ).fetchall():
           old = r["trigger_state"]
           new = triggers.get(r["task_key"]) or _catalog_trigger(r["task_key"])
           if new not in targets_of[old]:
               d_skipped = out["dispatch_task"]["skipped"]
               d_skipped[old] = d_skipped.get(old, 0) + 1
               continue
           by_new = out["dispatch_task"]["remapped"].setdefault(old, {})
           by_new[new] = by_new.get(new, 0) + 1
           if not dry_run:
               conn.execute("UPDATE dispatch_task SET trigger_state = ? WHERE id = ?", (new, r["id"]))

       if not dry_run:
           conn.commit()
       return out


   def migrate_terminal_state_names(*, dry_run: bool = True) -> Dict[str, Any]:
       """Retired terminal-state remap (AST-2087) — operator CLI only; dry run unless dry_run=False."""

       def _with_conn() -> Dict[str, Any]:
           conn = _get_connection()
           try:
               return _terminal_state_remap_conn(conn, dry_run=dry_run)
           finally:
               conn.close()

       return _run_with_retry(_with_conn)
   ```

   ⚠️ **Decision:** each `UPDATE` keeps `AND state = ?` (the old name). A row that a live worker moves between the read and the write is left alone rather than overwritten. Counts still reflect the read snapshot. Retries are safe because `_run_with_retry` re-runs on a fresh connection, and the closed uncommitted connection rolls back.

4. Compile and lint: `python3 -m py_compile src/data/database.py` and `ruff check src/data/database.py --extend-ignore UP,I --statistics`. Compare against the same command before the edit. The total must not rise. `UP` / `I` are ignored because the file's house style is `Dict` / `Optional` (683 baseline findings, mostly `UP`), and the new code matches it. The plan code was pre-checked this way and is clean.

5. Run the AC 2 grep from the parent for `src/data/database.py` only and confirm there is no output.

6. Commit `code(AST-2087): conn-bound retired terminal-state remap` and publish to `origin/sub/AST-2073/AST-2087-terminal-state-remap`.

---

## Stage 2: Operator CLI `scripts/migrations/migrate_terminal_state_names.py`

**Done when:** `python scripts/migrations/migrate_terminal_state_names.py` (no flags) prints the JSON result with `"dry_run": true` and `select sum(length(state)) from job` is unchanged. `--execute` prints `"dry_run": false`.

1. Create `scripts/migrations/migrate_terminal_state_names.py` with exactly:
   ```python
   #!/usr/bin/env python3
   """
   Retired terminal-state remap (AST-2087).

   Moves job / company / candidate / meteorite `state` and live dispatch_task.trigger_state
   off retired names using config RETIRED_TERMINAL_STATE_MAP (AST-2086). Rows it can't
   resolve, and dead-state rows, are left as-is and counted. Never rewrites state_history
   or state_changed_at; never runs from schema-ensure.

   Recommended:
     1. cp data/astral.db data/astral.db.pre-AST-2087-$(date +%Y%m%d)
     2. python scripts/migrations/migrate_terminal_state_names.py
     3. After Susan OK: python scripts/migrations/migrate_terminal_state_names.py --execute
   """

   from __future__ import annotations

   import argparse
   import json
   import sys
   from pathlib import Path

   sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

   from src.data.database import migrate_terminal_state_names


   def main() -> int:
       ap = argparse.ArgumentParser(description=__doc__)
       ap.add_argument(
           "--execute",
           action="store_true",
           help="Apply changes (default is dry-run)",
       )
       args = ap.parse_args()
       result = migrate_terminal_state_names(dry_run=not args.execute)
       print(json.dumps(result, indent=2, default=str))
       return 0


   if __name__ == "__main__":
       raise SystemExit(main())
   ```

2. `chmod +x scripts/migrations/migrate_terminal_state_names.py`. The template script is mode `100755`, and ruff `EXE001` flags a shebang on a non-executable file.
3. Compile and lint: `python3 -m py_compile scripts/migrations/migrate_terminal_state_names.py` and `ruff check scripts/migrations/migrate_terminal_state_names.py --extend-ignore UP,I`. Both must be clean.

4. Verify against a **copy** only. In the epic worktree, `data/astral.db` is a symlink to `~/astral/data/astral.db`, Susan's main DB. **Never** run `--execute` against it.
   ```bash
   mkdir -p /tmp/ast2087 && cp ~/astral/data/astral.db /tmp/ast2087/astral.db
   ASTRAL_DB_DIR=/tmp/ast2087 python scripts/migrations/migrate_terminal_state_names.py
   ASTRAL_DB_DIR=/tmp/ast2087 python scripts/migrations/migrate_terminal_state_names.py --execute
   rm -rf /tmp/ast2087
   ```
   The first run must print `"dry_run": true`, and the second `"dry_run": false`. AC 8's live half and AC 9 on real data are run by Betty or the operator on a copy or staging.

5. Commit `code(AST-2087): migrate_terminal_state_names operator CLI` and publish to `origin/sub/AST-2073/AST-2087-terminal-state-remap`.

---

## Test impact (for Betty)

- Component tests can seed rows through a temp DB and call `_terminal_state_remap_conn(conn, dry_run=…)` directly. Cases worth covering:
  - each resolution rule: single target, page-status error prefix, trigger predecessor, `_RETRY` predecessor, hop-label predecessor with `agent_task.run_next`, shared-trigger tie-break via `dispatch_task`, and the bare-family widening for a `FAILED_TECHNICAL` row whose predecessor is `PASSED_JD`
  - unresolved rows land in `skipped`
  - dead states land in `unregistered` and are untouched
  - the dry run writes nothing
  - `state_history` / `state_changed_at` / `updated_at` are byte-identical after execute
  - dispatch rows: `meteorite_bot_blocked_notify` `BOT_BLOCKED → BOT_BLOCKED_SCRAPE_METEORITE`
- Note that AC 9 says "equal to the dry run's skipped count for that table". That is `sum(out["skipped"][entity].values())`.

## Out of scope, noted

- `.cursorignore` `data/` also hides `src/data/` from agent tools. That's a repo-hygiene fix for Chuckles/Susan, not this ticket.
- `docs/canon-index.md` is referenced by AGENTS.md and the skills but does not exist in the tree or on `origin/dev`.
- Meteorite `SCRAPE_ERROR` rows written by `land_meteorite` from the old `BOT_BLOCKED` claim state stay unresolved: `BOT_BLOCKED` is not land's catalog trigger (`READY`). They are counted in `skipped`, per the ticket's unresolvable-row rule.

## Execution contract (for the developer agent)

Execute the stages in order and the steps literally. Do not add files, imports, helpers, logging, or schema-ensure calls beyond the ones listed. If a referenced line, name, or behaviour has drifted from this plan, stop and post the 🛑 stage-blocked comment on the parent:

```
🛑 Stage N blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

## Estimate

Confirm Chuckles estimate: 3 — agree
