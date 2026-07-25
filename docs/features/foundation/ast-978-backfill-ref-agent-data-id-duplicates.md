# AST-978 — Backfill ref_agent_data_id on existing duplicates

- **Linear:** [AST-978](https://linear.app/astralcareermatch/issue/AST-978/backfill-ref-agent-data-id-on-existing-duplicates-add-a-self-reference)
- **Parent:** [AST-974 — Add a self-reference key to agent_data](https://linear.app/astralcareermatch/issue/AST-974/add-a-self-reference-key-to-agent-data)
- **Publish ref:** `origin/sub/AST-974/AST-978-backfill-ref-agent-data-id-duplicates`
- **Summary:** One-time operator-safe dry-run + live backfill that sets `ref_agent_data_id` on existing duplicate `agent_data` content rows to their earliest identical twin. Reuses AST-977’s `_find_earliest_agent_data_content_match` identity (exact logical plain text; no `block_type` filter). Never clears, nulls, or deletes any `block_data`. Does not change runtime write/read (AST-977). CLI accepts `--debug` for §1.5.1 found/recorded trails; quiet when debug is off.

## UAT fitness

- **AC restored:** Parent AST-974 AC 7–8 (this child): “Backfill dry-run + live sets refs on existing duplicates to earliest twins and leaves all `block_data` values unchanged.” / “With `debug=True` on touched backend backfill paths, a scannable per-index trail shows match-vs-new and the ids recorded/resolved; with `debug=False`, no new debug-contract noise.”
- **Correct outcome:** After live backfill, every non-earliest content duplicate has `ref_agent_data_id` pointing at the earliest canonical twin; every touched row still has the same `block_data` bytes as before; earliest/canonical rows keep `ref_agent_data_id` null; dry-run reports the same set of would-update rows without writing; `--debug` prints per-row match-vs-skip and ids; without `--debug`, no debug-contract lines.
- **Sibling check:** AST-977 (User Testing) owns schema + runtime write/read + resolve. This plan only UPDATEs `ref_agent_data_id` on legacy duplicates and reuses `_find_earliest_agent_data_content_match` / `_decompress_payload` / `_ensure_agent_data_schema` — it does not alter `save_agent_data` or getters. Verified by Boundaries and by not listing write/read files.
- **Not sufficient:** Removing an exception / making the script exit 0 without setting refs on duplicates, or “fixing” by deleting duplicate rows, is **not** done.
- **Wrong fix rejected:** Clearing or nulling `block_data` on backfill (space reclaim is Susan SQL + vacuum outside epic); matching on `(block_type, block_data)`; rewriting runtime write/read; skipping dry-run. Correct path is refs-only UPDATE via earliest twin + leave payloads intact.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Add `backfill_agent_data_refs(*, dry_run) -> Dict` (no logging) | data |
| `scripts/migrations/backfill_agent_data_refs.py` | New operator CLI: default dry-run, `--execute`, `--debug` | scripts |

**Out of scope (explicit):**

| Item | Owner |
|------|--------|
| Schema / runtime write/read / resolve | **AST-977** (already shipped) |
| Clear / null / delete / vacuum historical `block_data` | Susan SQL outside epic |
| BLOCK_TYPES, prompt assembly, Anthropic | unchanged |
| UI / admin API wiring | none — local CLI only |
| `tests/` / bible | Betty |

**Dependency:** Blocked by AST-977. Build assumes `ref_agent_data_id` column + `_find_earliest_agent_data_content_match` exist on this branch (already present after merge `origin/ftr/AST-974-…`).

---

## Stage 1: Data-layer backfill function

**Done when:** `backfill_agent_data_refs(dry_run=True)` scans all content-bearing `agent_data` rows, returns counts + per-row actions without writing; `dry_run=False` UPDATEs only `ref_agent_data_id` on duplicate rows to the earliest twin and leaves every `block_data` value unchanged; re-run is idempotent (second live pass updates 0); `python3 -m py_compile src/data/database.py` passes. No logging in `database.py`.

1. In `src/data/database.py`, immediately after `_find_earliest_agent_data_content_match` / near the other `agent_data` helpers, add:

```python
def backfill_agent_data_refs(*, dry_run: bool = True) -> Dict[str, Any]:
    """Set ref_agent_data_id on duplicate content rows to earliest twin; never clear block_data.

    Returns dict with keys:
      scanned, updated, unchanged, skipped_already_ref, errors,
      actions: list of {agent_data_id, outcome, ref_agent_data_id}
    outcome values: "would_set_ref" | "set_ref" | "canonical_or_unique" | "already_ref" | "error"
    """
```

2. Implementation (literal; all work inside `_run_with_retry` + one connection):

   1. `_ensure_agent_data_schema(conn)`.
   2. Load candidate rows:

      ```sql
      SELECT agent_data_id, block_data, ref_agent_data_id, created_at
      FROM agent_data
      WHERE block_data IS NOT NULL
      ORDER BY created_at ASC, agent_data_id ASC
      ```

      Do **not** add LIMIT / OFFSET / batch caps.
   3. For each row:
      - If `ref_agent_data_id` is not null and `str(ref).strip() != ""`: increment `skipped_already_ref`, append action `outcome="already_ref"`, `ref_agent_data_id=<existing>`, continue.
      - Decompress via `_decompress_payload(row.block_data)` to `plain`. On decompress failure: increment `errors`, append `outcome="error"`, continue (do not abort the whole pass).
      - `match_id = _find_earliest_agent_data_content_match(conn, plain, exclude_agent_data_id=agent_data_id)`.
      - If `match_id` is None: this row is canonical/unique — increment `unchanged`, append `outcome="canonical_or_unique"`, `ref_agent_data_id=None`, continue.
      - If `match_id == agent_data_id`: increment `errors`, append `outcome="error"` (should be unreachable with exclude), continue.
      - Else (duplicate of earlier twin):
        - If `dry_run`: do **not** UPDATE; increment `updated`; append `outcome="would_set_ref"`, `ref_agent_data_id=match_id`.
        - If not `dry_run`:

          ```sql
          UPDATE agent_data SET ref_agent_data_id = ? WHERE agent_data_id = ?
          ```

          with `(match_id, agent_data_id)`. Do **not** set `block_data` in the UPDATE. Increment `updated`; append `outcome="set_ref"`, `ref_agent_data_id=match_id`.
   4. Always increment `scanned` once per candidate row (including already-ref / error / unchanged).
   5. If not `dry_run`: `conn.commit()` once after the loop. If `dry_run`: never commit ref updates (no writes).
   6. Return the counts dict + full `actions` list (no truncation).
   7. Docstring must state: does not clear `block_data`; identity matches AST-977 (exact logical plain text; `block_type` ignored); data layer does not log.

⚠️ **Decision:** Logic lives in `database.py` (same home as `_find_earliest_agent_data_content_match`) so the script cannot drift from runtime match semantics. Script only orchestrates CLI + debug logging (data raises / does not log — §1.5).

⚠️ **Decision:** Only rows with `block_data IS NOT NULL` are candidates. Rows that are already audit-style (null payload + ref) are out of this pass — runtime write already created them correctly.

⚠️ **Decision:** Keep historical `block_data` on rows that gain a ref. Parent AC 7 + Boundaries forbid clearing; Susan reclaim is separate SQL + vacuum.

---

## Stage 2: Operator CLI + debug trail

**Done when:** `python scripts/migrations/backfill_agent_data_refs.py` (no flags) prints a dry-run summary and writes nothing; `--execute` applies UPDATEs; `--debug` emits §1.5.1 per-index found/recorded lines for each action; without `--debug`, no new debug-contract lines; `python3 -m py_compile scripts/migrations/backfill_agent_data_refs.py` passes.

1. Create `scripts/migrations/backfill_agent_data_refs.py` with shebang `#!/usr/bin/env python3` and module docstring covering purpose, safety (default dry-run; never clears `block_data`), and usage:

```
python scripts/migrations/backfill_agent_data_refs.py
python scripts/migrations/backfill_agent_data_refs.py --execute
python scripts/migrations/backfill_agent_data_refs.py --execute --debug
```

2. Bootstrap (mirror `migrate_legacy_candidate_states.py` / `backfill_task_grouping_metadata.py`):

```python
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.data.database import backfill_agent_data_refs
from src.utils.logging import get_logger
```

3. `argparse`:
   - `--execute` — `store_true`; when absent, `dry_run=True` (operator-safe default).
   - `--debug` — `store_true`; default `False`.

4. `main() -> int`:
   1. Print `=== DRY RUN — no DB writes ===` when not `--execute`.
   2. `result = backfill_agent_data_refs(dry_run=not args.execute)`.
   3. If `args.debug`:
      - `log = get_logger(__name__, debug_flag=True)`
      - Let `actions = result["actions"]`, `M = len(actions)`.
      - For each `i, action` in enumerate(actions, start=1): emit one `debug_index` with universal `index {i}/{M}`, primary id `action["agent_data_id"]`, outcome summarizing match-vs-new (`would_set_ref` / `set_ref` / `canonical_or_unique` / `already_ref` / `error`) and `ref_agent_data_id={action.get("ref_agent_data_id")!r}`. Prefer ids/outcome only — do not dump `block_data`. Use `truncate_debug_content` only if any payload excerpt is ever logged (not required).
   4. Always `print(json.dumps({k: result[k] for k in ("scanned", "updated", "unchanged", "skipped_already_ref", "errors")}, indent=2))` (omit full `actions` from the JSON summary unless `--debug`, in which case printing actions is optional; debug-contract lines are the AC trail).
   5. Return `0` if `errors == 0` else `1`.

5. `if __name__ == "__main__": raise SystemExit(main())`.

⚠️ **Decision:** Default dry-run + explicit `--execute` (same safety posture as `migrate_legacy_candidate_states.py`), not default-live with optional `--dry-run`. Parent calls this “operator-safe.”

⚠️ **Decision:** Debug lives only in the script behind `--debug` → `debug=True` on `get_logger`. No logging inside `database.py`. Satisfies AC 8 and “data raises; callers log.”

---

## Self-Assessment

**Scope:** `Single-Component` — one data-layer backfill function plus one migration CLI; no runtime write/read or UI.

**Conf:** `high` — match helper and schema already shipped by AST-977; pattern mirrors existing `scripts/migrations/*` dry-run CLIs; AC forbids payload clearing so the UPDATE surface is a single column.

**Risk:** `Medium` — wrong earliest-twin choice would point refs at the wrong canonical row and change what resolve returns for those ids after backfill; mitigated by reusing `_find_earliest_agent_data_content_match` unchanged and never mutating `block_data`.

## Rules self-review

- **§1.3 DRY:** Reuse `_find_earliest_agent_data_content_match` / `_decompress_payload` / `_ensure_agent_data_schema`; do not reimplement match in the script.
- **§1.5 / data-raises-caller-logs:** No logging in `database.py`; decompress failures recorded in return counts; CLI logs only when `--debug`.
- **§1.5.1:** Index headers with universal `index N/M`, primary id, outcome; quiet when `--debug` absent.
- **§2.1:** No new config keys.
- **§3.3:** Script imports `data` + `utils.logging` only; no UI → data.
- **§3.5:** Names match parent vocabulary (`ref_agent_data_id`, backfill refs).
- **Unauthorized limits:** No row/batch caps on the scan (Susan rule).
)
