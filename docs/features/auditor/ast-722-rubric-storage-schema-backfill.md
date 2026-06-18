# AST-722 — Rubric storage schema, backfill, and feedback config (Runtime Rubric Validation)

- **Linear:** [AST-722](https://linear.app/astralcareermatch/issue/AST-722/rubric-storage-schema-backfill-and-feedback-config-runtime-rubric)
- **Parent (context only):** [AST-378](https://linear.app/astralcareermatch/issue/AST-378/runtime-rubric-validation)
- **Publish ref:** `origin/sub/AST-378/AST-722-rubric-storage-schema-backfill`

## Summary

Introduce normalized **`rubric_vector`** and **`vector_feedback`** SQLite tables, register them in the data-layer inventory, add **`FEEDBACK`** to **`BLOCK_TYPES`**, and add product **config** for rubric feedback type/value codes. Ship a one-time backfill migration that copies legacy rubric criteria from `candidate_data.artifacts` into **`rubric_vector`** rows (`current = 1`, new UUIDs, content fingerprints). Ship an optional purge step that **deletes** legacy rubric artifact keys from `candidate_data.artifacts` after Susan verifies backfill (AC #9). **Does not** switch runtime read paths, Artifacts save paths, craft flows, or token resolution off artifact JSON — that is **AST-723**. **Does not** capture vector feedback from agent runs (**AST-724**) or build Admin UI (**AST-725**).

## Out of scope (explicit)

| Item | Owner ticket |
|------|----------------|
| Consult/roster/agent read paths from `rubric_vector` | AST-723 |
| `{$RUBRIC_VECTORS}` token; Artifacts save write to `rubric_vector` | AST-723 |
| Agent performance envelope / `vector_feedback` row creation at runtime | AST-724 |
| Admin Vector Feedback screen | AST-725 |
| Letter-grade scoring math, `TASK_CONFIG` rubric_artifact removal | AST-723+ |
| Non-rubric artifact keys (`base_resume`, `resume_structure`, etc.) | — |

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Header inventory; `_ensure_rubric_vector_table`; `_ensure_vector_feedback_table`; CRUD/list helpers; artifact purge helper | data |
| `src/utils/config.py` | Add `FEEDBACK` to `BLOCK_TYPES`; add `RUBRIC_FEEDBACK_CONFIG` block | utils |
| `src/utils/rubric_text.py` | Add pure `rubric_vector_content_fingerprint(label, content)` helper | utils |
| `scripts/migrations/backfill_rubric_vectors.py` | One-time backfill + optional artifact purge CLI | scripts |

**Tests:** Betty owns **`tests/`** at Code Complete — engineer does **not** add test files in **build-child**.

## Stage 1: Schema, config, and data-layer helpers

**Done when:** Fresh DB startup creates both tables via lazy `_ensure_*`; `BLOCK_TYPES` accepts `"FEEDBACK"`; `RUBRIC_FEEDBACK_CONFIG` is importable; manual REPL can insert/list `rubric_vector` rows; `save_agent_data(..., block_type="FEEDBACK", ...)` succeeds.

1. In **`src/utils/config.py`**, extend **`BLOCK_TYPES`** (line ~780):

   ```python
   BLOCK_TYPES = [
       "SYSTEM", "CACHE_A", "CACHE_B", "CACHE_C", "CACHE_D", "NO_CACHE",
       "TASK", "RESPONSE", "FEEDBACK",
   ]
   ```

2. In **`src/utils/config.py`**, after **`ASTRAL_CONFIG["consult_importance"]`** block (~2050), add **`RUBRIC_FEEDBACK_CONFIG`**:

   ```python
   RUBRIC_FEEDBACK_CONFIG = {
       "feedback_types": {
           "relevance": {
               "label": "Relevance",
               "value_codes": ("A", "O", "S", "R", "N"),
           },
           "clarity": {
               "label": "Clarity",
               "value_codes": ("A", "O", "S", "R", "N"),
           },
           "verdict": {
               "label": "Verdict",
               "value_codes": ("K", "E", "D"),
           },
       },
       "value_labels": {
           "A": "Always",
           "O": "Often",
           "S": "Sometimes",
           "R": "Rarely",
           "N": "Never",
           "K": "Keep",
           "E": "Edit",
           "D": "Drop",
       },
   }
   ```

   ⚠️ **Decision:** Short single-letter **value** codes match the parent envelope sketch (`R<A|O|S|R|N>C<…>V<K|E|D>`). **AST-724** validates against this config; no DB columns for relevance/clarity/verdict.

3. In **`src/utils/rubric_text.py`**, add:

   ```python
   import re
   import hashlib

   def rubric_vector_content_fingerprint(label: str, content: str) -> str:
       """Normalized label+content identity for rubric_vector versioning (AST-378).

       Strip non-alphanumeric, lowercase, concatenate label then content.
       Returns sha256 hex digest (full 64 chars) of normalized string.
       """
       combined = f"{label or ''}{content or ''}"
       normalized = re.sub(r"[^a-z0-9]", "", combined.lower())
       return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
   ```

4. In **`src/data/database.py`** header inventory (after **`company_search_terms`** bullet), add:

   ```
   - rubric_vector — Per-candidate rubric vector identity (rubric_vector_uuid TEXT PK, candidate_id,
     task_key TEXT, task_key_uuid TEXT, code, label, content, importance INTEGER, content_fingerprint TEXT,
     current INTEGER 0|1, created_at, updated_at). Active set: rows with current=1 for (candidate_id, task_key).
     Versioning follows agent_task current=1 pattern (AST-722).
   - vector_feedback — Per-run per-vector feedback grain (vector_feedback_id TEXT PK, rubric_vector_uuid,
     candidate_id, batch_id, task_key, feedback_type TEXT, value TEXT, optional agent_data_id, created_at).
     One row per feedback type per vector per run; type/value codes validated against RUBRIC_FEEDBACK_CONFIG (AST-724 writes).
   ```

5. Add module-level guards near other `_ensure_*` flags:

   ```python
   _rubric_vector_schema_ensured = False
   _vector_feedback_schema_ensured = False
   _rubric_vector_backfill_swept = False
   ```

6. Implement **`_ensure_rubric_vector_table(conn: sqlite3.Connection) -> None`**:

   ```sql
   CREATE TABLE rubric_vector (
       rubric_vector_uuid TEXT PRIMARY KEY,
       candidate_id TEXT NOT NULL,
       task_key TEXT NOT NULL,
       task_key_uuid TEXT NOT NULL,
       code TEXT NOT NULL,
       label TEXT NOT NULL,
       content TEXT NOT NULL,
       importance INTEGER NOT NULL,
       content_fingerprint TEXT NOT NULL,
       current INTEGER NOT NULL DEFAULT 1,
       created_at TIMESTAMP NOT NULL,
       updated_at TIMESTAMP NOT NULL
   );
   ```

   - Index **`idx_rubric_vector_candidate_task_current`** on **`(candidate_id, task_key, current)`**.
   - Index **`idx_rubric_vector_task_key_uuid`** on **`(task_key_uuid)`**.
   - **No** `rubric_version` table.

   ⚠️ **Decision:** Store both **`task_key`** (query path for active rubric load) and **`task_key_uuid`** (snapshot of `agent_task` row at insert/backfill time). SQLite has no enforced FK; integrity is application-level like other tables.

7. Implement **`_ensure_vector_feedback_table(conn: sqlite3.Connection) -> None`**:

   ```sql
   CREATE TABLE vector_feedback (
       vector_feedback_id TEXT PRIMARY KEY,
       rubric_vector_uuid TEXT NOT NULL,
       candidate_id TEXT NOT NULL,
       batch_id TEXT NOT NULL,
       task_key TEXT NOT NULL,
       feedback_type TEXT NOT NULL,
       value TEXT NOT NULL,
       agent_data_id TEXT,
       created_at TIMESTAMP NOT NULL
   );
   ```

   - Index **`idx_vector_feedback_rubric`** on **`(rubric_vector_uuid)`**.
   - Index **`idx_vector_feedback_batch`** on **`(batch_id)`**.
   - Index **`idx_vector_feedback_candidate_task`** on **`(candidate_id, task_key)`**.

8. Implement **`_resolve_current_agent_task_uuid(conn: sqlite3.Connection, task_key: str) -> Optional[str]`**:
   - `SELECT task_key_uuid FROM agent_task WHERE task_key = ? AND current = 1 LIMIT 1`
   - Return `None` if missing (backfill skips that artifact key for that candidate with a counted warning).

9. Implement **`insert_rubric_vector_row(conn, *, candidate_id, task_key, task_key_uuid, code, label, content, importance, content_fingerprint, current=1) -> str`**:
   - Generate `rubric_vector_uuid = str(uuid.uuid4())`.
   - `INSERT` with `_utc_now()` timestamps.
   - Return UUID string.
   - Wrap public entry points in **`_run_with_retry`**.

10. Implement **`list_rubric_vectors(candidate_id: str, task_key: str, *, current_only: bool = True) -> List[Dict[str, Any]]`**:
    - Filter `candidate_id` + `task_key`; when `current_only`, add `AND current = 1`.
    - Order by `code ASC` (display order only; runtime assembly in AST-723 does not depend on order).
    - Return dict keys: `rubric_vector_uuid`, `candidate_id`, `task_key`, `task_key_uuid`, `code`, `label`, `content`, `importance`, `content_fingerprint`, `current`, `created_at`, `updated_at`.

11. Implement **`count_rubric_vectors_for_candidate_task(candidate_id: str, task_key: str, *, current_only: bool = True) -> int`** — used by backfill idempotency.

12. Call **`_ensure_rubric_vector_table`** / **`_ensure_vector_feedback_table`** from existing schema bootstrap paths that open connections for candidate/agent_task work (mirror **`_ensure_company_search_terms_table`** — ensure on first `list_rubric_vectors` / `insert_rubric_vector_row` call).

### Self-review (Stage 1)

| Rule | OK? |
|------|-----|
| §1.1 table inventory | Header updated |
| §2.1 config | `RUBRIC_FEEDBACK_CONFIG` + `BLOCK_TYPES` in config.py |
| §3.3 imports | Data imports utils only; fingerprint in utils |
| §2.4 batch | N/A — not batch-claimed entity rows |

---

## Stage 2: Backfill migration script

**Done when:** `python scripts/migrations/backfill_rubric_vectors.py --dry-run` reports per-candidate/per-task vector counts that match legacy `candidate_data.artifacts` JSON; running without `--dry-run` inserts `rubric_vector` rows with `current=1`; re-run is idempotent (skips already-backfilled candidate+task pairs); `--candidates susan,other` limits scope; missing `agent_task` current row logs warning and skips that rubric key.

1. Create **`scripts/migrations/backfill_rubric_vectors.py`** with shebang, docstring, and usage examples (mirror **`backfill_collapse_blank_lines.py`** tone).

2. Bootstrap imports:

   ```python
   import argparse
   import json
   import sys
   from pathlib import Path
   from typing import Any, Dict, List, Optional, Tuple

   sys.path.insert(0, str(Path(__file__).parent.parent.parent))

   from src.data import database
   from src.utils.config import ASTRAL_CONFIG, RUBRIC_CRITERIA_ARTIFACT_KEYS
   from src.utils import rubric_text
   ```

3. Add migration-only artifact-key → runtime **task_key** map (lives **only** in this script — not runtime config):

   ```python
   _ARTIFACT_KEY_TO_TASK_KEY: Dict[str, str] = {
       "company_prefilter": "prefilter_company",
       "joblist_rubric": "qualify_job_listings",
       "jobdesc_rubric": "evaluate_jd",
       "do_rubric": "grade_do",
       "get_rubric": "grade_get",
       "like_rubric": "grade_like",
   }
   ```

   ⚠️ **Decision:** Map uses **runtime** task keys (`prefilter_company`, `grade_get`, …) — not `craft_*` keys — because rubric consumption and `agent_task` rows are keyed by runtime task identity per parent epic.

4. Add **`_normalize_importance(raw, ci) -> int`** in the script (duplicate small helper from `candidate.py` — data/scripts must not import core for normalization; same bounds as `ASTRAL_CONFIG["consult_importance"]`).

5. Add **`_criterion_from_artifact_item(item: dict, idx: int) -> Tuple[str, str, str, int, str]`** returning `(code, label, content, importance, fingerprint)`:
   - `code` = stripped `item["code"]` or generated `V{idx+1:02d}` if missing.
   - `label` = stripped `item.get("label")` or `code`.
   - `content` = `item.get("content") or ""` (preserve grade table text in content string).
   - `importance` = `_normalize_importance(item.get("importance"), ci)`.
   - `fingerprint` = `rubric_text.rubric_vector_content_fingerprint(label, content)`.
   - Raise **`ValueError`** with safe message if `content` empty (skip vector with error count, do not abort whole candidate).

6. Add **`backfill_candidate_rubric_vectors(candidate_id: str, *, dry_run: bool) -> Dict[str, int]`**:
   - Load candidate via **`database.get_candidate(candidate_id)`**; skip if missing or `state == "DELETED"`.
   - Parse `candidate_data.artifacts` dict.
   - For each `artifact_key` in **`RUBRIC_CRITERIA_ARTIFACT_KEYS`** present in artifacts:
     - Resolve `task_key = _ARTIFACT_KEY_TO_TASK_KEY[artifact_key]`; skip with warning if key missing from map.
     - If **`database.count_rubric_vectors_for_candidate_task(candidate_id, task_key)` > 0**, increment `skipped_existing` and continue (idempotent).
     - Resolve `task_key_uuid` via new data helper; if `None`, increment `skipped_no_agent_task` and continue.
     - For each list item in `artifacts[artifact_key]`:
       - Build row fields; on `ValueError`, increment `errors` and continue.
       - Dry-run: increment `would_insert` only.
       - Else: call **`database.insert_rubric_vector_row`** (or batch insert helper).
     - Increment `tasks_backfilled` when at least one vector inserted for that artifact key.
   - Return counts: `candidates_scanned`, `tasks_backfilled`, `vectors_inserted`, `skipped_existing`, `skipped_no_agent_task`, `errors`, `would_insert` (dry-run).

7. Add **`run_backfill(dry_run: bool, candidates: Optional[List[str]]) -> None`**:
   - If `candidates` provided, iterate that list; else **`[c["astral_candidate_id"] for c in database.list_candidates()]`** excluding `DELETED`.
   - Print summary table at end.
   - `argparse`: `--dry-run`, `--candidates` comma-separated.

8. **`if __name__ == "__main__"`** → `run_backfill(...)`.

### Self-review (Stage 2)

| Rule | OK? |
|------|-----|
| §3.6 spike output | Script only; no output under `docs/` or `artifacts/` |
| §1.3 DRY | Fingerprint in utils; map only in migration script |
| Scope gate | No consult/roster/agent edits |

---

## Stage 3: Legacy artifact purge

**Done when:** `python scripts/migrations/backfill_rubric_vectors.py --purge-artifacts --dry-run` reports which rubric keys would be removed per candidate; running `--purge-artifacts` (without dry-run) removes only keys in **`RUBRIC_CRITERIA_ARTIFACT_KEYS`** from `candidate_data.artifacts`, leaves all other artifact keys untouched; re-run reports zero keys removed.

1. In **`src/data/database.py`**, implement **`purge_legacy_rubric_artifact_keys(candidate_id: str) -> List[str]`**:
   - Load candidate `candidate_data`; if no `artifacts` dict, return `[]`.
   - For each key in **`RUBRIC_CRITERIA_ARTIFACT_KEYS`**, `pop` if present; collect removed key names.
   - If any removed, **`save_candidate(candidate_id, candidate_data=artifacts_parent_dict, merge=True)`** preserving other candidate_data fields (use same merge pattern as existing candidate updates).
   - Return list of removed keys.

2. In **`scripts/migrations/backfill_rubric_vectors.py`**, add **`purge_rubric_artifacts(candidate_ids, *, dry_run: bool) -> Dict[str, int]`**:
   - For each candidate, call data helper unless dry-run (print keys that would be removed).
   - Counts: `candidates_scanned`, `candidates_purged`, `keys_removed`.

3. Extend CLI with **`--purge-artifacts`** flag:
   - When set **without** `--dry-run`, print banner:

     ```
     WARNING: purge removes legacy rubric JSON from candidate_data.artifacts.
     Run only after AC#9 backfill verification AND AST-723 read-switch is on origin/ftr.
     ```

   - Require **`--confirm-purge`** second flag to actually execute deletes (both flags required). Without `--confirm-purge`, exit 1 with message.

   ⚠️ **Decision:** Dual-flag gate prevents accidental purge while runtime still reads artifact JSON (**AST-723** boundary). Susan runs `backfill` → verify AC#9 → merge **AST-723** → then `backfill_rubric_vectors.py --purge-artifacts --confirm-purge` before UAT.

4. Purge does **not** delete `rubric_vector` rows — only artifact JSON blobs.

### Self-review (Stage 3)

| Rule | OK? |
|------|-----|
| Scope | Purge only rubric artifact keys per ticket + Susan note |
| Risk | Gated execution; AST-723 required before production purge |

---

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — New `rubric_vector` and `vector_feedback` tables, config block, `FEEDBACK` block type, utils fingerprint helper, and migration/purge scripts in data + scripts layers only.

**Conf:** `Medium` — Table/sync patterns are established (`company_search_terms`, `agent_task` versioning); open coordination is purge timing vs **AST-723** read-switch, gated explicitly in Stage 3.

**Risk:** `Medium` — Incorrect backfill mapping or partial purge could desync rubric data from legacy JSON; mitigation is dry-run, idempotent skip, dual-flag purge, and AC#9 vector-count verification before purge.

## Self-Review vs ASTRAL_CODE_RULES

| Section | Assessment |
|---------|------------|
| §1.1 Scope / inventory | Both tables documented in `database.py` header; no other tables touched |
| §1.3 DRY | Fingerprint helper centralized in `rubric_text.py`; artifact→task map migration-only |
| §2.1 Config | `RUBRIC_FEEDBACK_CONFIG` and `BLOCK_TYPES` in `config.py`; no env lookups |
| §2.4 Batch | N/A |
| §2.6 State machine | N/A — rubric rows are not entity state machine rows |
| §3.3 Imports | data→utils; scripts→data+utils; no core/ui changes in this ticket |
| §3.5 Naming | snake_case tables/columns; script under `scripts/migrations/` |
| §3.6 Local output | Migration script stdout only; no committed spike artifacts |

No unresolved rule conflicts.
