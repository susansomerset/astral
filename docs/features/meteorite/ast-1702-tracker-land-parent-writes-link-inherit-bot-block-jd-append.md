# AST-1702 — Tracker + land parent writes, link inherit, bot-block JD append

**Linear:** [AST-1702](https://linear.app/astralcareermatch/issue/AST-1702/tracker-land-parent-writes-link-inherit-bot-block-jd-append)  
**Parent:** [AST-1640](https://linear.app/astralcareermatch/issue/AST-1640/job-source-entity-parent-meteoritecompany-candidate-facing-link) — Job source_entity parent (meteorite|company) + candidate-facing link  
**Publish ref:** `sub/AST-1640/AST-1702-tracker-land-parent-writes-link-inherit-bot-block-jd-append`

After AST-1701’s schema SSOT: tracker create/supersede parents jobs to a **meteorite row** (optional real `company_id`), same-row gazed→meteorite flip, land inherits `meteorite.link` → `job.job_link`, and land link-check bot-block no longer fails the land — non-blocked scrape JD is **appended** to existing text. Does not author email breadcrumbs (#3) or rewire qualify / jobs API / Job Detail (#4).

## Scope gate

Ticket **## Scope** (verbatim partition):

- `src/core/tracker.py` — `save_meteorite_job` / create / gazed→meteorite supersede write parent fields + optional `company_id`; stop requiring meteorite company short_name as parent; stop using old `gazed`/`meteorite` source flag as track authority once repurposed/dropped.
- `src/core/meteorite.py` — land parents to meteorite row; `job.job_link` inherits `meteorite.link`; link check does not fail land on bot-block; append non-blocked JD content to existing text; stop `ensure_meteorite_company` as job parent; optional real `company_id` (breadcrumb *format* for no-URL outcomes is #3).

Technical (same ticket): `tracker.save_meteorite_job` — create under meteorite parent; gazed match flips parent to meteorite, keeps `company_id`, state `METEORITE_NEW`, appends history; no second row; no clobber of existing meteorite-parented row. `meteorite` land — inherit `meteorite.link` → `job.job_link`; on link check, bot-block does not fail the land; if not bot-blocked, append JD text onto existing job description content; stop `ensure_meteorite_company` solely for `job.company`.

All Files Changed / Stages below stay inside that set. Out of scope (siblings): `config.py` / `database.py` schema (#1 already User Testing on `ftr`), breadcrumb authorship (#3), `consult.py` / `gazer.py` / `api_jobs.py` / `JobsJobDetail.tsx` (#4).

**Depends on:** AST-1701 merged on the epic line (`SOURCE_ENTITY_TYPES`, `save_job` requiring `source` + `source_entity_id`, nullable `company_id`). After `sync-child.sh` with registry parent segment `AST-1640-job-source-entity-parent`, if those symbols are missing on HEAD, **stop** and comment on AST-1702 (do not re-implement schema here).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/tracker.py` | Rewrite `save_meteorite_job` for meteorite-row parent + optional `company_id`; rename source helpers to source_entity SSOT; gazed/company → meteorite supersede keeps employer + history | core |
| `src/core/meteorite.py` | Land/create stop `ensure_meteorite_company` as job parent; parent via meteorite id; inherit `meteorite.link` → `job.job_link`; bot-block does not fail land; append non-blocked scraped JD; optional real `company_id` | core |

## Stage 1: Tracker — `save_meteorite_job` parent writes

**Done when:** `save_meteorite_job` creates under `source=meteorite` + non-empty `source_entity_id` (meteorite row id text) with optional `company_id`; company-parented (incl. legacy `gazed`) dedupe match supersedes in-place to meteorite parent at `METEORITE_NEW` keeping `company_id` and appending `state_history`; existing meteorite-parented match never clobbers; no required meteorite-company short_name argument. `python3 -m py_compile src/core/tracker.py` succeeds.

1. In `src/core/tracker.py` imports from `src.utils.config`, replace `JOB_SOURCE_DEFAULT` / `JOB_SOURCE_METEORITE` / `job_source_transition_allowed` / `validate_job_source` with the AST-1701 SSOT names:

   - `SOURCE_ENTITY_TYPE_COMPANY`
   - `SOURCE_ENTITY_TYPE_METEORITE`
   - `SOURCE_ENTITY_TYPE_DEFAULT`
   - `source_entity_type_transition_allowed`
   - `validate_source_entity_type`

   Keep importing `METEORITE_CONFIG` (still owns `job_create_state`, land outcomes, `source_entity_type`, dedupe order, employer_name key).

2. Rename `_assert_job_source_write` → `_assert_source_entity_type_write` (same body, call `validate_source_entity_type` + `source_entity_type_transition_allowed`). Update error text to `Invalid source_entity_type transition: … (meteorite → company forbidden)`.

3. Update `set_job_source` to call the renamed assert and keep the function name (thin admin helper). Pass `source=` through to `database.save_job` as today (physical column still `source` per #1).

4. Rewrite `save_meteorite_job` signature and docstring:

```python
def save_meteorite_job(
    candidate_id: str,
    *,
    meteorite_id: Any,  # int or str — required meteorite row id → source_entity_id
    company_id: Optional[str] = None,  # optional real employer short_name; never placeholder
    company_job_id: Optional[str] = None,
    job_title: Optional[str] = None,
    job_link: Optional[str] = None,
    job_data: Optional[Dict[str, Any]] = None,
    employer_name: Optional[str] = None,
    debug: bool = False,
) -> Dict[str, Any]:
```

   - Remove the required `company: str` parent argument.
   - Docstring: create under meteorite parent; company-parented match flips parent to meteorite, keeps `company_id`, state `METEORITE_NEW`, appends history; never clobber meteorite-parented match; no second row (AST-1702 / parent AC4–AC5 twin).

5. Validation at top of `save_meteorite_job`:

   - `cid = (candidate_id or "").strip()` — raise `ValueError("candidate_id is required")` if blank.
   - `mid = str(meteorite_id).strip() if meteorite_id is not None else ""` — raise `ValueError("meteorite_id is required")` if blank.
   - `emp = (company_id or "").strip() or None` — if `emp` is set and (`emp.startswith(METEORITE_CONFIG["short_name_prefix"])` **or** looks like `{stem}-{candidate_id}` placeholder via `METEORITE_CONFIG["stem_short_name_template"]` with default stem), treat as **not** a real employer: set `emp = None` (do not write placeholder into `company_id`).
   - Keep employer_name → `job_data[METEORITE_CONFIG["employer_name_job_data_key"]]` merge as today.

6. Dedupe: keep `database.find_meteorite_dedupe_match(cid, company_job_id=…, job_link=…)` unchanged (candidate-scoped; ignores employer column).

7. Branch A — existing **meteorite** parent (never clobber):

   - `match_source = (match.get("source") or "").strip()`
   - If `match_source == SOURCE_ENTITY_TYPE_METEORITE`: return `duplicate_skip` with existing row (same outcome keys as today: `outcome`, `astral_job_id`, `job`, plus `"source": SOURCE_ENTITY_TYPE_METEORITE`). Do **not** rewrite parent / `company_id` / JD.

8. Branch B — company / legacy gazed supersede (same `astral_job_id`):

   - Treat as supersede when `match_source` is in `{SOURCE_ENTITY_TYPE_COMPANY, SOURCE_ENTITY_TYPE_DEFAULT, "gazed", ""}` **or** any value other than `SOURCE_ENTITY_TYPE_METEORITE` that is not already handled — concrete rule: **if not Branch A, and match exists → supersede** unless `match_source == SOURCE_ENTITY_TYPE_METEORITE` (already returned). Prefer explicit: supersede when `match_source != SOURCE_ENTITY_TYPE_METEORITE`.
   - `_assert_source_entity_type_write(match.get("source"), SOURCE_ENTITY_TYPE_METEORITE)`.
   - Append history entry `{to_state: METEORITE_CONFIG["job_create_state"], timestamp, score}` onto existing `state_history` (do not wipe).
   - `database.save_job(match_id, state=…, source=SOURCE_ENTITY_TYPE_METEORITE, source_entity_id=mid, company_id=…, job_data=…, state_history=…, state_changed_at=…, latest_score=…, merge=True, …)`:
     - **Keep** existing employer: if `emp` is None, pass `company_id=(match.get("company_id") or match.get("company") or None)` so supersede does not null a known real employer. If `emp` is set, pass `emp`.
     - Always set `source` + `source_entity_id=mid`.
     - Optional title / link / company_job_id same as today when provided.
   - Return `land_outcome_superseded` with same `astral_job_id`.

9. Branch C — create:

   - New UUID `astral_job_id`.
   - `database.save_job(…, state=job_create_state, source=SOURCE_ENTITY_TYPE_METEORITE, source_entity_id=mid, company_id=emp, candidate_id=cid, company_job_id=…, job_title=…, job_link=…, job_data=…, state_history=[…], merge=False)`.
   - Do **not** pass placeholder via `company=`.
   - On identity bounce: re-find via `find_meteorite_dedupe_match`; if found return `duplicate_skip`. Drop `get_job_id_by_identity(company_key, …)` fallback that keyed on meteorite company short_name — if a second fallback is still needed, use `get_job_id_by_identity(emp, title, cid_job)` **only when** `emp` is non-None; otherwise skip that fallback.
   - Post-insert `latest_score` update + return `land_outcome_created` as today.

10. Debug helper: replace `company=` detail with `meteorite_id=` / `company_id=` / `source_entity_id=`; keep `debug_index` / `debug_detail` gated on `debug` (existing tracker pattern — do not add `logger.info("[DEBUG]")` or `print`).

⚠️ **Decision:** Physical column remains `source` (AST-1701 prefer-repurpose); Tracker talks `SOURCE_ENTITY_TYPE_*`. Legacy `"gazed"` on unread-backfill rows supersedes as company-parent (Branch B), so Susan’s operator SQL is not a hard gate for land to work on old rows.

## Stage 2: Meteorite — land parents, link inherit, bot-block, append JD

**Done when:** `run_land_meteorite` and public `land_meteorite` / `create_meteorite_job` / `create_contact_meteorite` no longer call `ensure_meteorite_company` solely to parent a job; every land→create passes a meteorite row id into `save_meteorite_job`; after successful land, `job.job_link` equals that row’s `meteorite.link` (including non-http breadcrumbs already on the row — #3 authors them); land link-check that classifies bot-block does **not** set land outcome to error solely for that reason; when the check is not bot-blocked and returns visible text, that text is **appended** to existing scrap/row JD content before save. `grep -rn "ensure_meteorite_company" src/core/meteorite.py` shows only the function **definition** (and its internal debug lines), not call sites used for job parenting. `python3 -m py_compile src/core/meteorite.py src/core/tracker.py` succeeds.

### 2a. Shared helpers (in `meteorite.py`)

1. Add `_optional_real_company_id(*, company_stem: Optional[str], candidate_id: str) -> Optional[str]`:

   - Strip `company_stem`. If blank, or equal to `METEORITE_CONFIG["default_stem"]` / `meteorite_self_stem`, return `None`.
   - `row = get_company(stem)` — if row exists and `(row.get("state") or "") != METEORITE_CONFIG["company_state"]`, return `stem`.
   - Do **not** call `ensure_meteorite_company`. Do **not** invent `{stem}-{candidate_id}` placeholders as `company_id`.

2. Add `_append_jd(existing: str, addition: str) -> str`:

   - Strip both; if `addition` empty return `existing`; if `existing` empty return `addition`; else return `existing + "\n\n" + addition`.

3. Add `_land_link_check_append(scrap: Dict[str, Any], *, debug: bool = False) -> None` (mutates scrap in place) for the **public** `land_meteorite` thin-body scrape path currently using `_land_fetch_link_text`:

   - Read current body via `_land_scrap_body(scrap)` and `link` from scrap.
   - If no http(s) link or body already meets `TASK_CONFIG["qualify_meteorite"]["min_jd_chars"]`, return (no fetch).
   - `visible, final_url = await _land_fetch_link_text(link, debug=debug)`.
   - Classify with the same gazer helpers scrape uses: `from src.core.gazer import _CONTACT_PAGE_STATUS, _classify_jd` then `page_status = _CONTACT_PAGE_STATUS.get(_classify_jd(visible), "missing")`.
   - **If `page_status == "blocked"`:** do **not** raise; do **not** set land outcome error; leave existing body unchanged; optionally `logger.warning` who+why (`stat.logging.warning` — candidate/link + bot-block, land continuing). Return.
   - **If `page_status == "ok"` and `visible.strip()`:** set `scrap["content"] = _append_jd(existing_body, visible.strip())`; if `final_url`, set `scrap["job_link"] = final_url`.
   - Else (empty / closed / missing): leave body as-is (soft miss — existing `_warn_item` only if you already warn today; do not fail the whole land solely because scrape was empty when prior text exists).

⚠️ **Decision:** Bot-block / append live on the **land** link-check path (`land_meteorite`), not by changing `run_scrape_meteorite` (scrape may still route rows to `BOT_BLOCKED` before READY — that is staging, not land failure). AC6’s “does not fail the land” targets land’s own link check.

### 2b. `run_land_meteorite` (table READY → LANDED)

1. Delete the `ensure_meteorite_company` call and `ensured["short_name"]` usage.
2. Before `save_meteorite_job`:
   - `mid = int(row["id"])` (already have `row_id`).
   - `link_text = (row.get("link") or "").strip()` — pass **full** `link_text` as `job_link` to Tracker (not only when `_is_http_url`). Empty link → `job_link=None`.
   - `company_id=_optional_real_company_id(company_stem=None, candidate_id=cid)` → `None` on table path unless a future row field supplies stem (do not invent).
3. Call:

```python
save = tracker.save_meteorite_job(
    cid,
    meteorite_id=mid,
    company_id=None,
    job_data={jd_key: content},
    job_link=link_text or None,
    company_job_id=None,
    employer_name=None,
    debug=debug,
)
```

4. On ok outcomes: after save, if `link_text` is non-empty, assert/repair inheritance — if `(save["job"] or {}).get("job_link") != link_text`, `database.save_job(job_id, job_link=link_text)` once (inherit is mandatory for AC5). Prefer getting it right on the first `save_meteorite_job` write so repair is rare.
5. Keep `update_meteorite(…, state="LANDED", astral_job_id=…)` and entity info / batch `finally: clear_meteorite_batch` unchanged (`patt.entity.batch-processing` — claim → process by batch_id → clear in finally).
6. Replace `_entity_info(…, ensured["short_name"])` detail with `meteorite_id` or job outcome detail (entity type still `job`).

### 2c. Public `land_meteorite`

1. Replace the per-row scrape loop body that calls `_land_fetch_link_text` with `_land_link_check_append` (bot-block continue / append on ok).
2. After enrich, for each enriched job row:
   - **Obtain meteorite parent id** (required for `save_meteorite_job`):
     - If `land_meteorite` gains optional kwarg `meteorite_id: Optional[Any] = None` and caller passed one, use it for every row (single-row API land).
     - Else insert one staging row via `insert_meteorite_rows([{candidate_id, source_kind: "paste", source_id: str(uuid.uuid4()), content: found_jd or None, link: (row job_link or None), classify_outcome: None}])`, take returned id, then `update_meteorite(id, state="READY")` so the row is a real parent before job write. After successful save, `update_meteorite(id, state="LANDED", astral_job_id=…)`.
   - ⚠️ **Decision:** Auto-insert `paste` staging rows when public land has no meteorite id — keeps API land inside “parent to meteorite row” without pulling `api_meteorite.py` into this ticket. Table ingress (`run_land_meteorite`) always has an id and never inserts here.
   - `job_link_for_save`: prefer `get_meteorite(mid)["link"]` after any link updates; if meteorite.link empty, fall back to enrich row’s job_link, and if that is non-empty write it onto `meteorite.link` via `update_meteorite(mid, link=…)` **before** save so inherit is `job.job_link == meteorite.link`.
   - `company_id = _optional_real_company_id(company_stem=row_stem, candidate_id=cid)`.
   - Call `tracker.save_meteorite_job(…, meteorite_id=mid, company_id=company_id, job_link=inherited_link, …)` — **no** `ensure_meteorite_company`, **no** `company=` placeholder.
3. Return payload: keep `outcomes` / rollup; set `"company": first_company_id` to the first non-None `company_id` written (or `None`); `"company_inserted": False` always (we no longer insert METEORITE companies on this path). Do not invent a fake short_name for the return key.

### 2d. `create_meteorite_job` + `create_contact_meteorite`

1. Change `create_meteorite_job` to require `meteorite_id` (or accept optional and insert a `paste` row the same way as 2c when omitted — same Decision as public land so `gazer.py` callers keep compiling until #4 without using ensure-as-parent):

```python
def create_meteorite_job(
    candidate_id: str,
    html_body: str,
    *,
    meteorite_id: Optional[Any] = None,
    job_link: Optional[str] = None,
    company_id: Optional[str] = None,
    debug: bool = False,
) -> dict[str, Any]:
```

   - Remove `stem=` and the `ensure_meteorite_company` call.
   - Resolve `mid` from arg or auto-insert paste row with `content=html_body`, `link=job_link`.
   - If `job_link` provided and meteorite.link empty, `update_meteorite(mid, link=job_link)`.
   - Write job via `database.save_job` **or** `tracker.save_meteorite_job` with `source=SOURCE_ENTITY_TYPE_METEORITE`, `source_entity_id=str(mid)`, `company_id=_optional_real_company_id` / passed-in real employer, `job_link=(get_meteorite(mid).get("link") or job_link or None)`. Prefer `tracker.save_meteorite_job` so create/supersede/dedupe stay one path — if using Tracker, pass `job_data={jd_key: html_body}`.
   - Return dict: replace `"company": short_name` with `"company_id": emp_or_none` and add `"meteorite_id": mid`; keep `astral_job_id` / `state` / `job`.

2. `create_contact_meteorite`: stop relying on ensure; after scrape-or-text resolution, call `create_meteorite_job` with `job_link=` as today (meteorite_id omitted → auto-insert). Keep warning / exception logging shapes (`stat.logging.warning` / `stat.logging.error` via existing `_warn_item` / `logger.exception`).

3. **AC3 grep gate (implementer verifies, record in stage Linear comment):**

```bash
rg -n "ensure_meteorite_company" src/core/meteorite.py
```

   Allowed: the `def ensure_meteorite_company` block and its internal debug strings. **Forbidden:** any other call site (land, create, contact create). Function may remain for out-of-tree / future non-parent uses; this ticket does not delete it.

4. Logging discipline on touched paths:
   - Success land/create: existing `_entity_info` / `_meteorite_state_info` (`stat.logging.info.entity`).
   - Soft bot-block continue: one `logger.warning` who+why (`stat.logging.warning`).
   - Unexpected exceptions in batch runners: keep `logger.exception` + continue (`stat.logging.error`).
   - Callee joints: keep `logger.debug("Calling …")` / `Response from …` / loop begin-end (`stat.logging.debug`) — no `if debug:` wrap, no `print`.

## Estimate

Confirm Chuckles estimate: 5 — agree

Tracker rewrite + two land surfaces + create cutover + bot-block/append semantics is multi-component with migration-adjacent parent writes (not a known one-file pattern) — fits 5; still bounded to two files.

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; publish each to `origin/sub/AST-1640/AST-1702-tracker-land-parent-writes-link-inherit-bot-block-jd-append`.
- Do not edit `config.py`, `database.py`, `consult.py`, `gazer.py`, or UI in this ticket.
- Do not author email breadcrumb strings (#3) — only inherit whatever is already on `meteorite.link`.
- When a step is ambiguous or the tree has drifted — stop and comment on **parent** AST-1640 with the Stage blocked template; do not improvise.

## Traceability

- AC3 → Stage 2 (no `ensure_meteorite_company` call sites for job parent on land→create; grep gate).
- AC4 → Stage 1 Branch B (same `astral_job_id`, meteorite parent, `METEORITE_NEW`, history append).
- AC5 → Stage 2b/2c (`job.job_link` inherits full `meteorite.link`).
- AC6 → Stage 2a/2c (bot-block does not fail land; non-blocked JD appended).
