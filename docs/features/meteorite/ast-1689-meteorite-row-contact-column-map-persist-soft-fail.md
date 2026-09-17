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

## Joan validate

[plan-rubric]
**Ticket:** AST-1689
**Overall:** APPROVED
**Corpus:** fc0c368e5927a57f1561c057ce9a0ff4abe1fb13
**Publish ref tip:** `2b916c344d565a6be7e38f289c6d5884f6ec307f` (`sub/AST-1684/AST-1689-meteorite-row-contact-column-map-persist-soft-fail`)

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.entity.batch-processing | A | | Contact on meteorite row via insert/update_meteorite; no side queue; dispatch runners unchanged |
| patt.task.daisy-chain | A | | Map at classify fan-out; BOT_BLOCKED preserve explicit; no re-derive in scrape/land |
| stat.logging.debug | A | | Ungated `logger.debug` returned/recorded lines; `@_with_log_debug` gating; no `if debug` wrappers |
| stat.logging.info | A | | No new always-on progress lines; existing `_meteorite_state_info` only |
| stat.logging.info.entity | A | | Existing entity pipe on state transitions unchanged; no contact payload on info |
| stat.logging.warning | A | | Soft-fail via `_warn_item` per-item who/why/next_step pattern |

## Traceability

AC3 → Stage 1 insert + Stage 2 map + soft-persist · AC4 → Stage 2 §5 BOT_BLOCKED preserve · AC5 → Stage 2 §6 land/job_data · AC6 → Stage 2 `_soft_persist_meteorite_electronic_contact` · AC7 → map optional None + soft-persist non-aborting · AC8 → Stage 2 §4 `logger.debug` returned/recorded · AC9 N/A (no UI) · parent AC1–2 N/A (AST-1688)

## Findings

### discuss

- **Location:** Stage 2 §4 Style D; parent AC8 wording; Canon Scope “Style D via `logger.debug`”
- **Finding:** Parent AC8 says “Style D”; plan implements `logger.debug("electronic_contact returned=%r recorded=%r …")`, not `debug_index`. Meteorite test bible notes Style D on/off asserts retired under logging statutes; `stat.logging.debug` explicitly separates Style D (`debug_index`) from this statute.
- **Recommendation:** Acceptable under current canon — plan’s mapping is documented and matches `stat.logging.debug`. If Betty/UAT fixtures still grep `debug_index` func= for contact, flag at qa-child; not a plan blocker here.

- **Location:** Scope gate Reply-To note; Stage 2 ingest only (email)
- **Finding:** Reply-To not in today’s email blob (From/To only); sole `insert_meteorite_rows` / `_map_classify_jobs_to_meteorite_rows` caller is `ingest_candidate_email_message` — matches epic email focus and child partition.
- **Recommendation:** None for this ticket; epic Reply-To header ingest remains out of scope (same Joan finding on AST-1688).

- **Location:** Stage 2 `_soft_persist_meteorite_electronic_contact` exception path
- **Finding:** On `update_meteorite` failure, helper returns `None` without re-read — debug line may show `recorded=None` while Stage 1 insert already bound contact.
- **Recommendation:** Optional polish at build (read-after-insert-failure for accurate debug); does not violate AC6 warn-and-continue or row survival.

### acceptable

- **Location:** Files Changed — `consult.py` / `agent.py` omitted
- **Finding:** Plan documents decision: `invoke_stage_meteorite` returns full job dicts; optional `items_schema` validation accepts new field post-AST-1688.
- **Recommendation:** None; matches codebase (`get_meteorite` already imported in `meteorite.py`).

- **Location:** Stage 1 preflight Depends-on AST-1688
- **Finding:** Stop gate if config keys missing after sync — correct bang-first sequencing.
- **Recommendation:** None.

## R6 checklist (summary)

- Definition fidelity: DB column + map/persist + soft-fail + debug observability; no schema/prompt/UI/job_data work.
- Scope gate: two files only; AST-1688 literals consumed, not redefined.
- DRY: reuses `_warn_item`, `_meteorite_state_info`, existing lockstep/config-key patterns.
- Self-assessment: Estimate confirm line present; stages have concrete done-when gates.
- Plan Discuss rounds: 0 (Plan Ready first pass).

context_tokens≈58000

## Review (build stub)

**Publish ref:** `origin/sub/AST-1684/AST-1689-meteorite-row-contact-column-map-persist-soft-fail`
**Plan path:** `docs/features/meteorite/ast-1689-meteorite-row-contact-column-map-persist-soft-fail.md`

**Built tip:** `a0ca31ec9fcc540d616585849aaa98e97bfd0d48` (`a0ca31ec`)

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `0f58c50b` | meteorite `electronic_contact` column + allowlist + insert |
| 2 | `a0ca31ec` | classify→row map, soft-fail persist, Style D returned/recorded |

**Betty note:** consult/agent untouched; land does not write contact into job_data.

## Radia review

[code-rubric]
**Ticket:** AST-1689
**Publish ref:** `39fa655a2189fea4675508a79c1100629c258301`
**Corpus:** fc0c368e5927a57f1561c057ce9a0ff4abe1fb13
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.entity.batch-processing | A | | |
| patt.task.daisy-chain | A | | |
| stat.logging.debug | A | | |
| stat.logging.info | A | | |
| stat.logging.info.entity | A | | |
| stat.logging.warning | A | | |

## Column diff vs plan stage

(aligned) — Joan: all six directives **A**; code review matches on every row.

## Frame diff

Propose `resolve-child` §10 ticks (left unchecked for engineer validation):

- [ ] **AC3:** Text outcome (`single_jd_no_link` / `multi_jd_inline`) with Ruth `electronic_contact` → meteorite row column populated after fan-out
- [ ] **AC4:** Link outcome → **BOT_BLOCKED** preserves stage-captured contact (state-only update)
- [ ] **AC5:** Land path does not write contact into `job_data` / `save_meteorite_job`
- [ ] **AC6:** Contact persist failure warns and continues; row stays **NEW** (not **ERROR** solely for contact)
- [ ] **AC7:** Empty/omit contact still ingests successfully
- [ ] **AC8:** `debug=True` emits returned-vs-recorded `logger.debug`; `debug=False` silent for those lines
- [ ] **AC9:** No Recommended / JobDetail UI changes in this diff

## Findings

### discuss

- **Location:** Publish ref commits `a96d4617` (AST-1690), `d177cd43` (AST-1691), `1a23a972` (AST-1694); files `tests/component/data/database/test_meteorites.py` (`TestAst1694*`, `TestAst1691*`), `tests/component/ui/api/test_api_jobs_ast1694_listing_href.py`, `tests/component/ui/api/test_api_system.py` (`TestAst1691ReportMeteoriteSections`), `tests/component/core/test_meteorite.py` (`TestAst1690*`)
- **Finding:** Sibling-ticket test coverage landed on the AST-1689 sub tip without matching product on this branch (`get_meteorite_link_by_astral_job_id`, `get_meteorite_by_astral_job_id`, `listing_href`, `JOBS_RECOMMENDED_REPORT_METEORITE_SECTIONS` absent from `src/`). Betty’s narrowed manifest (AST-1689 nodes only) is green; broad file/collection runs on those classes will fail until product lands on AST-1690/1691/1694 subs.
- **Recommendation:** Not an AST-1689 product defect — relocate or `skipif` sibling tests on their own publish refs before merge-child rollup; keep AST-1689 manifest as-is.

- **Location:** `data/admin/agent_task.json` / `src/utils/config.py` / AST-1688 issue doc in three-dot diff vs `origin/dev`
- **Finding:** AST-1688 product + docs still stacked ahead of `origin/dev` (sibling #1 not merged to dev yet); expected for bang-ordered subs on one epic ftr line.
- **Recommendation:** None for this review; finish-up / merge order unchanged.

- **Location:** Parent AC8 “Style D”; `ingest_candidate_email_message` `logger.debug("electronic_contact returned=%r recorded=%r …")` (not `debug_index`)
- **Finding:** Same Joan/plan mapping as AST-1688 — parent wording says Style D; implementation follows `stat.logging.debug` (ungated call + `@_with_log_debug` ContextVar gate). Tests assert substring presence/absence correctly.
- **Recommendation:** Accept under current canon; no change required on tip.

### advisory

- **Location:** `_soft_persist_meteorite_electronic_contact` exception path (`src/core/meteorite.py`)
- **Finding:** On `update_meteorite` failure after insert, helper returns `None` — debug line may show `recorded=None` even though Stage 1 insert may have bound contact (Joan plan discuss item).
- **Recommendation:** Optional polish at resolve-child; does not violate AC6/AC7.

- **Location:** `TestAst1689ElectronicContactMapPersist`
- **Finding:** AC3 exercised for `single_jd_no_link` only; `multi_jd_inline` and URL scrape branches share `_map_classify_jobs_to_meteorite_rows` but lack dedicated cases.
- **Recommendation:** Manifest coverage is sufficient for this pass; add URL/`multi_jd_inline` cases only if Betty wants belt-and-suspenders.

## What's solid

- **Stage 1 (`database.py`):** `electronic_contact` on CREATE + idempotent ALTER; column in header inventory; `_UPDATE_METEORITE_ALLOWED` uses `METEORITE_CONFIG["electronic_contact_column"]` (no parallel spelling); `insert_meteorite_rows` column/`?`/bind tuple aligned (9 binds + `nag_count=0` + 4 trailing).
- **Stage 2 (`meteorite.py`):** `_electronic_contact_from_job` normalizes strip/empty→`None`; both text and URL map loops set config column; post-insert soft-persist + ungated `logger.debug` returned/recorded; `run_scrape_meteorite` BOT_BLOCKED is state-only (comment + no contact clear); `run_land_meteorite` `job_data={jd_key: content}` only — contact stays on meteorite row, not job.
- **Scope discipline:** `consult.py` / `agent.py` untouched (plan decision holds). No UI files. Config literals consumed from AST-1688, not redefined in AST-1689 product commits.
- **Tests (manifest):** `TestAst1689ElectronicContactColumn` (schema/alter/insert/update allowlist) + `TestAst1689ElectronicContactMapPersist` (text ingest, empty contact, soft-fail warn, BOT_BLOCKED preserve, land job_data exclusion, debug gate) map cleanly to AC3–AC8.

## Recommended actions

- Chuckles: append artifact, commit `docs(AST-1689): Radia review — clean`, post slim upshot, **Review Posted** → datt **PROCEED** to **User Testing** (no fix-now canon items).
- Downstream: peel AST-1690/1691/1694 test commits off this sub or gate with `skipif` before ftr rollup; do not block AST-1689 UT on sibling test hygiene.
- Epic follow-on: Reply-To not in today’s email blob (`From`/`To`/`Subject`/`Date` only) — same discuss as AST-1688; AC3 “Reply-To/From” satisfied via From until header ingest lands.

---

**Slim Linear upshot (Chuckles posts via `linear_proxy --as radia`):**

```
[code-rubric] PROCEED (Commit: 39fa655a) row map persist clean
```

context_tokens≈52000
