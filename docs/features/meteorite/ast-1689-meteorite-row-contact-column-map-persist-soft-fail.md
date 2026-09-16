# AST-1689 — Meteorite-row contact column + map/persist soft-fail

**Linear:** [AST-1689](https://linear.app/astralcareermatch/issue/AST-1689/meteorite-row-contact-column-map-persist-soft-fail-reply-to-emails-in)  
**Parent:** [AST-1684](https://linear.app/astralcareermatch/issue/AST-1684/reply-to-emails-in-meteorite-when-single-jd-no-link) — Reply-to emails in meteorite when single_jd_no_link  
**Publish ref:** `sub/AST-1684/AST-1689-meteorite-row-contact-column-map-persist-soft-fail`

After AST-1688’s config literals + prompts: add the meteorite-table `electronic_contact` column (allowlist + insert), map Ruth’s `electronic_contact` from classify `jobs[]` onto fan-out row dicts for text and link outcomes, soft-fail (warn-and-continue) when contact persist fails after an otherwise good insert, keep contact on the row through BOT_BLOCKED (do not clear it), and emit Style D returned-vs-recorded debug when `debug=True`. Does **not** write contact into job `job_data` or touch Recommended UI.

## Scope gate

Ticket **## Scope** (verbatim partition):

- `src/data/database.py` — **modified** — meteorite schema + insert/update allowlist for the new contact field (header inventory / ensure path as plan chooses).
- `src/core/meteorite.py` — **modified** — classify→row map and BOT_BLOCKED / land paths carry contact onto the meteorite row; soft-fail warn on persist miss; Style D when debug.
- `src/core/consult.py` — **modified** only if stage invoke mapping must forward the new response key(s); otherwise untouched.
- `src/core/agent.py` — **modified** only if schema validation needs a one-line wire; otherwise untouched.
- `database.py` — New meteorite column + `_UPDATE_METEORITE_ALLOWED` / insert path so contact can be written at NEW fan-out and updated later.
- `meteorite.py` — Map Ruth contact into row dicts for text and link fan-out; preserve contact into BOT_BLOCKED; on persist failure log warning and continue; Style D when debug.
- `consult.py` / `agent.py` — Only if stage invoke or validator must name the new keys.

All Files Changed / Stages stay inside that set.

**Out of scope (siblings / other epics):**

- `src/utils/config.py` / `data/admin/agent_task.json` response-key / column literals / prompts — **AST-1688** (already shipped; consume its keys only)
- Writing contact onto job / `job_data` — never (parent AC5)
- Recommended / JobDetail UI — **AST-1685**
- Changing the six `STAGE_METEORITE_CONFIG["outcomes"]` literals
- Fetching new Gmail headers (Reply-To) in `gmail.py` — not in Scope (same note as AST-1688 Joan finding; From/To already in blob)

**Depends on:** AST-1688 (Bang `!`). After `sync-child.sh`, `METEORITE_CONFIG["electronic_contact_column"]` and `STAGE_METEORITE_CONFIG["electronic_contact_response_key"]` must be importable (normally via `origin/ftr/AST-1684-…` once Chuckles merges AST-1688). If either key is missing after a clean sync, **stop** — comment parent AST-1684 with Stage blocked; do not hardcode parallel string literals in this ticket.

**AC partition (this ticket):** Parent AC3, AC4, AC5, AC6, AC7, AC8 (AC1–2 = AST-1688; AC9 = AST-1685 / no UI touch).

**Canon Scope (read at plan):** `patt.entity.batch-processing` (full — contact persist must not invent a side queue; stay on claimed meteorite rows). `patt.task.daisy-chain` (full — contact rides on the row through stage→scrape→BOT_BLOCKED / land; do not re-derive by skipping stage). `stat.logging.debug`, `stat.logging.info`, `stat.logging.info.entity`, `stat.logging.warning` (full — Style D via `logger.debug`; soft-fail via `logger.warning` / `_warn_item`; no new always-on info spam unless an existing entity-state line already fires).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Add `electronic_contact` to meteorite CREATE + idempotent `ALTER` ensure; allowlist; `insert_meteorite_rows` INSERT; header inventory | data |
| `src/core/meteorite.py` | Map response key → column on classify fan-out; soft-fail contact persist after insert; Style D returned vs recorded; do not clear contact on BOT_BLOCKED / land; do not pass contact into `save_meteorite_job` | core |

⚠️ **Decision:** `consult.py` and `agent.py` are **untouched**. `invoke_stage_meteorite` already returns full `parsed_response["jobs"]` dicts; `_validate_response_schema` already walks optional `items_schema` fields. No one-line wire is required once AST-1688’s schema field exists.

## Stage 1: Meteorite column + allowlist + insert

**Done when:** `_ensure_meteorite_schema` creates or migrates column named exactly `METEORITE_CONFIG["electronic_contact_column"]` (`electronic_contact`); that name is in `_UPDATE_METEORITE_ALLOWED`; `insert_meteorite_rows` writes `row.get(column)` into the new column (NULL when absent/empty); header inventory lists the column; `python3 -m py_compile src/data/database.py` succeeds (repo venv if needed). No `meteorite.py` changes yet.

1. **Preflight (build):** After `sync-child.sh`, confirm in the epic worktree:

```python
from src.utils.config import METEORITE_CONFIG, STAGE_METEORITE_CONFIG
assert METEORITE_CONFIG["electronic_contact_column"] == "electronic_contact"
assert STAGE_METEORITE_CONFIG["electronic_contact_response_key"] == METEORITE_CONFIG["electronic_contact_column"]
```

If ImportError / KeyError: stop per Depends-on above.

2. In `src/data/database.py` header inventory line for `meteorite`, append `electronic_contact` to the column list (AST-1689; config literal from AST-1688).

3. Near other meteorite imports from `src.utils.config` in `database.py`, ensure `METEORITE_CONFIG` is imported (add if missing).

4. Extend `_UPDATE_METEORITE_ALLOWED` to include `METEORITE_CONFIG["electronic_contact_column"]` (do **not** hardcode a second spelling — build the frozenset so the config string is the member).

5. In `_ensure_meteorite_schema`:
   - Add `electronic_contact TEXT` to the `CREATE TABLE meteorite (...)` body (new DBs), placed after `link` (or immediately after `classify_outcome` — either is fine; prefer after `link` to keep scrap fields grouped).
   - After create/index path (for existing DBs), `PRAGMA table_info(meteorite)` and if `METEORITE_CONFIG["electronic_contact_column"]` is missing, `ALTER TABLE meteorite ADD COLUMN <col> TEXT` with the same duplicate-column try/except pattern used in `_ensure_job_schema`.

6. In `insert_meteorite_rows`, extend the INSERT column list and VALUES to include the config column name; bind `row.get(METEORITE_CONFIG["electronic_contact_column"])` (may be `None`). Do **not** reject rows that omit the key.

7. Do **not** change claim/get/clear/list signatures. `update_meteorite` already writes any allowlisted kwargs — once the column is allowlisted, callers can update it.

## Stage 2: Map, soft-fail persist, Style D, BOT_BLOCKED preserve

**Done when:** Text and URL branches of `_map_classify_jobs_to_meteorite_rows` copy Ruth’s optional contact onto the row dict under the config column (empty/omit → `None`); after a successful classify `insert_meteorite_rows` in `ingest_candidate_email_message`, contact is soft-persisted (warn-and-continue on failure; row not ERROR solely for contact); Style D `logger.debug` lines compare returned vs recorded when `log_debug` is on; scrape → BOT_BLOCKED does not clear the column; `run_land_meteorite` / `tracker.save_meteorite_job` still do not receive a contact key; `python3 -m py_compile src/core/meteorite.py` succeeds.

1. In `src/core/meteorite.py`, ensure `METEORITE_CONFIG` and `STAGE_METEORITE_CONFIG` are already imported (they are). Add a small helper **above** `_map_classify_jobs_to_meteorite_rows`:

```python
def _electronic_contact_from_job(job: Dict[str, Any]) -> Optional[str]:
    """Normalize Ruth jobs[] electronic_contact → meteorite column value (or None)."""
    key = STAGE_METEORITE_CONFIG["electronic_contact_response_key"]
    raw = job.get(key)
    if not isinstance(raw, str):
        return None
    text = raw.strip()
    return text or None
```

2. In `_map_classify_jobs_to_meteorite_rows`, for **both** the `text_source_ref_outcomes` loop and the `url_scrape_outcomes` loop, after building each `out.append({...})` dict, set:

```python
col = METEORITE_CONFIG["electronic_contact_column"]
contact = _electronic_contact_from_job(job)
# always set the key so insert/soft-persist see explicit None vs omitted
row_dict[col] = contact
```

Apply to the dict before append (or mutate immediately after). Do **not** treat missing contact as a map error (AC7).

3. Add soft-fail persist helper (same module, near `_warn_item` / `_row_miss`):

```python
def _soft_persist_meteorite_electronic_contact(
    meteorite_id: int,
    contact: Optional[str],
    *,
    who: Any,
) -> Optional[str]:
    """Best-effort contact write after a good insert/transition. Warns; never raises to fail the row."""
    col = METEORITE_CONFIG["electronic_contact_column"]
    try:
        update_meteorite(int(meteorite_id), **{col: contact})
        row = get_meteorite(int(meteorite_id))
        recorded = (row or {}).get(col)
        return recorded if isinstance(recorded, str) else recorded
    except Exception as exc:
        _warn_item(
            who,
            f"{col} persist failed: {type(exc).__name__}: {exc}",
            "This meteorite row continues without a contact write",
        )
        return None
```

Import `get_meteorite` if not already imported from `src.data.database`.

⚠️ **Decision:** Two-phase write for classify fan-out — `insert_meteorite_rows` may still bind contact when present (Stage 1), but ingest **always** calls `_soft_persist_meteorite_electronic_contact` after a successful insert for each new id. Soft-fail covers update failures after the insert already succeeded (AC6). Empty/`None` contact still calls soft-persist (writes NULL); that must not abort ingest (AC7).

4. In `ingest_candidate_email_message`, immediately after a successful `insert_meteorite_rows` (after the count-mismatch check passes, before archive), zip `ids` with `job_list` (same order as map/insert — already asserted equal length) and for each `(row_id, job)`:

```python
returned = _electronic_contact_from_job(job)
recorded = _soft_persist_meteorite_electronic_contact(
    row_id, returned, who=f"meteorite {row_id} for {cid}",
)
logger.debug(
    "electronic_contact returned=%r recorded=%r meteorite_id=%s",
    returned, recorded, row_id,
)
```

`logger.debug` is always called; emission is gated by `log_debug` / `@_with_log_debug` (AC8). Do **not** add `logger.info("[DEBUG] …")` or ungated Style D lines.

5. **BOT_BLOCKED preserve (AC4):** In `run_scrape_meteorite`, when `page_status == "blocked"`, keep the existing `update_meteorite(row_id, state=status_map["blocked"])` — do **not** pass `electronic_contact=None` or any other field that would clear stage-captured contact. No new scrape-time contact logic; the column already on the NEW→SCRAPE_LINK row must remain.

6. **Land / job_data (AC5):** In `run_land_meteorite` (and any other land helper in this file), do **not** add `electronic_contact` to `tracker.save_meteorite_job(... job_data=...)`. Leave land job_data as `{jd_key: content}` only. Contact stays on the meteorite row.

7. Do **not** edit Recommended / JobDetail UI files. Do **not** edit `consult.py` / `agent.py` / `config.py` / `agent_task.json` in this ticket.

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; publish each to `origin/sub/AST-1684/AST-1689-meteorite-row-contact-column-map-persist-soft-fail`.
- Do not add files outside the Files Changed table.
- Do not implement AST-1688 config/prompt work or AST-1685 UI.
- On ambiguity or codebase drift: stop, comment on **parent** AST-1684 with the Stage blocked format, wait.

## Estimate

Confirm Chuckles estimate: 5 — agree
