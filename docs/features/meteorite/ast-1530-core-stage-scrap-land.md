# AST-1530 — Core stage → scrap map → land_meteorite

**Linear:** [AST-1530](https://linear.app/astralcareermatch/issue/AST-1530/core-stage-scrap-map-land-meteorite-generalize-meteorite-ingress)  
**Parent:** [AST-1527](https://linear.app/astralcareermatch/issue/AST-1527/generalize-meteorite-ingress-point) — Generalize Meteorite Ingress Point  
**Publish ref:** `sub/AST-1527/AST-1530-core-stage-scrap-land`

Public ingress stage entry: candidate-bound blob + source handle → Ruth `stage_meteorite` → map closed outcomes to scrap array → call existing `land_meteorite` for landable outcomes (or structured skip for ignore/fail). Reuses land’s URL scrape for types 2/4; no second Playwright stack; Style D when `debug=True`. Does **not** retarget mailbox / inbox / Contact (**AST-1531**). Consumes catalog/config from **AST-1529** (`STAGE_METEORITE_CONFIG` + `TASK_CONFIG["stage_meteorite"]` + live `agent_task` row) — already on `origin/ftr/AST-1527-generalize-meteorite-ingress-point` / this worktree after sync-child.

## Scope gate

Ticket **## Scope** (verbatim partition):

- `src/core/meteorite.py` — **modified** — public stage entry: blob + source handle → `do_task(stage_meteorite)` → map closed outcomes to scrap array → call existing `land_meteorite`; ignore/fail outcomes create no jobs; Style D when `debug=True`.
- `src/core/consult.py` — **modified** — thin stage invoke helper only if needed so meteorite does not duplicate `do_task` batch-id / live_content assembly (same shape as land enrich helper).
- `src/core/agent.py` — **modified** — only if stage needs a minimal invoke-path note or validation hook; no new provider client.
- `src/core/meteorite.py` — **new** public async stage function (name per plan-child under `stage_meteorite` contract): accept candidate id, blob, source kind/id, debug; call agent; map outcomes 1/3 → text+source-ref scraps, 2/4 → URL scraps for existing `land_meteorite` scrape path, 5/6 → structured skip/fail with no land; **no** second Playwright stack.
- `src/core/consult.py` — **new** optional `stage_meteorite` invoke helper (assemble live_content, mint batch id, `do_task`) mirroring land enrich discipline.
- `src/core/agent.py` — **modified** only if schema validation or context_format for `stage_meteorite` needs a one-line wire; else untouched.

All Files Changed / Stages stay inside that set.

**Out of scope (siblings / keep):**

- Catalog / `STAGE_METEORITE_CONFIG` / `agent_task` row — **AST-1529** (already shipped to UT; do not re-edit config or catalog here).
- Mailbox `_handle_bound`, inbox Land / `fetch_email`, `contact_land_meteorite` cutover — **AST-1531**.
- Rewrites of `land_meteorite` scrape/enrich/save path or `qualify_meteorite` claim/dispatch.
- New Playwright / gazer scrape stack in stage.

**Depends on:** AST-1529 catalog present on the epic worktree after `sync-child.sh` (merge `origin/ftr/AST-1527-generalize-meteorite-ingress-point`). If `STAGE_METEORITE_CONFIG` / `TASK_CONFIG["stage_meteorite"]` are missing after sync — **stop**, comment on parent AST-1527 with Stage blocked format; do not invent config.

**AC partition (this ticket):** Parent AC1–AC6 + AC7 Style D for the stage path (AC7 catalog half is AST-1529).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/consult.py` | Add `invoke_stage_meteorite` — live_content + batch id + `do_task("stage_meteorite")`; header inventory line | core |
| `src/core/meteorite.py` | Add public `stage_meteorite` + scrap-map helpers; call invoke → map → `land_meteorite` or skip; Style D; header inventory | core |

⚠️ **Decision — `agent.py` untouched:** `do_task` already accepts `entity_type=None` + `requires_candidate_key` (same audit-index pattern as `enrich_meteorite_land_packet`). No Files Changed row for `agent.py`. If Stage 1/2 runtime proves a one-line schema/context wire is required, **stop** and comment on parent — do not silently expand Files Changed.

## Stage 1: Consult invoke helper — `invoke_stage_meteorite`

**Done when:** `consult.invoke_stage_meteorite` assembles live_content (source handle + blob), mints a batch id, calls `do_task(task_key="stage_meteorite", …)`, and returns `{success, outcome, jobs, error, batch_id, raw}` with outcome validated against `STAGE_METEORITE_CONFIG["outcomes"]` when present; header lists the helper next to `enrich_meteorite_land_packet`; `python3 -m py_compile src/core/consult.py` succeeds. No meteorite public stage yet.

1. In `src/core/consult.py` module docstring inventory (near the `enrich_meteorite_land_packet` line), add:  
   `invoke_stage_meteorite: ingress classify via stage_meteorite do_task (blob + source handle; no claim/land) (AST-1530).`

2. Import `STAGE_METEORITE_CONFIG` from `src.utils.config` alongside existing `TASK_CONFIG` imports (same import block; do not duplicate).

3. Immediately **after** `enrich_meteorite_land_packet` (before `qualify_meteorite`), add:

```python
async def invoke_stage_meteorite(
    candidate_id: str,
    blob: str,
    *,
    source_kind: str,
    source_id: str,
    ctx: Optional[Dict[str, Any]] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """Ingress classify via stage_meteorite do_task (AST-1530). No claim, no land."""
```

4. Validate inputs inside the helper:
   - `cid = (candidate_id or "").strip()` — if empty → `{"success": False, "error": "candidate_id is required", "outcome": None, "jobs": [], "batch_id": None}`.
   - `kind = (source_kind or "").strip()` — must be a key of `STAGE_METEORITE_CONFIG["source_ref_prefixes"]`; else → `{"success": False, "error": "invalid source_kind", …}` (same empty shape).
   - `sid = (source_id or "").strip()` — if empty → `{"success": False, "error": "source_id is required", …}`.
   - `body = blob if isinstance(blob, str) else ""` — if `not body.strip()` → `{"success": False, "error": "blob is required", …}`.

5. Assemble `live_content` exactly (Ruth user prompt says “Read CONTENT”; source handle is caller-supplied identity for core + debug — not Gmail header parsing):

```text
SOURCE_KIND: {kind}
SOURCE_ID: {sid}
CONTENT:
{body}
```

6. Mint batch id / do_index mirroring enrich discipline:
   - `task_key = STAGE_METEORITE_CONFIG["task_key"]` (must equal `"stage_meteorite"`).
   - `batch_id = f"{task_key}-stage-{uuid4()}"`.
   - `do_index = f"{task_key}_batch_{batch_id}"`.
   - Build `task_ctx` from `ctx` (or `{}`) with `astral_candidate_id=cid`; preserve `candidate_data` / `candidate_api_key` when present on `ctx`. Do **not** set job `batch_entities` (no job claim; `entity_type` is `None`).

7. `log_batch_id.set(batch_id)` around the `do_task` call (same try/finally clear as enrich). Call:

```python
result = await do_task(
    task_key=task_key,
    live_content=live_content,
    index=do_index,
    ctx=task_ctx,
    debug=debug,
)
```

8. On `not result.get("success")`: return `{"success": False, "error": result.get("error") or "do_task failed", "outcome": None, "jobs": [], "batch_id": batch_id, "raw": result}`. When `debug=True`, emit one Style D index (`func="consult.invoke_stage_meteorite"`, identifier=`cid`, outcome=`"stage_failed"`) + detail with `batch_id` and error — gated only.

9. Parse `parsed_response = result.get("parsed_response")` if dict else `{}`. Read `outcome` (str strip) and `jobs` (list of dicts; non-dicts skipped).  
   - If `outcome` not in `STAGE_METEORITE_CONFIG["outcomes"]`: return failure `error="invalid stage outcome"` with `outcome` set to the raw string (or `None` if empty), `jobs=[]`.  
   - If `outcome` in `STAGE_METEORITE_CONFIG["skip_outcomes"]`: coerce `jobs` to `[]` (ignore any agent scraps).  
   - Else keep `jobs` as the filtered list (may be empty — caller/map decides landability).

10. Success return: `{"success": True, "outcome": outcome, "jobs": jobs, "error": None, "batch_id": batch_id, "raw": result}`. When `debug=True`, one Style D index (`outcome=outcome`) + detail `batch_id=… job_count=… source_kind=…`.

⚠️ **Decision — helper owns do_task, meteorite owns map+land:** Matches ticket Scope (“thin stage invoke helper … mirroring land enrich discipline”) and keeps scrap/land policy in `meteorite.py` next to `land_meteorite`.

⚠️ **Decision — live_content shape:** Explicit `SOURCE_KIND` / `SOURCE_ID` / `CONTENT` blocks so core can synthesize source-refs without trusting prompt-invented ids, and Style D can echo the handle. Agent still classifies from CONTENT; prompts (AST-1529) already say caller synthesizes source-refs.

## Stage 2: Public `stage_meteorite` — scrap map → land or skip

**Done when:** `meteorite.stage_meteorite(candidate_id, blob, *, source_kind, source_id, debug=False)` is the public async entry; landable outcomes call existing `land_meteorite(scraps=…)`; skip outcomes create **no** jobs and return a structured skip; URL outcomes leave scrape to `land_meteorite` (no new Playwright in stage); Style D found-vs-recorded lines appear only when `debug=True`; header documents the entry; `python3 -m py_compile src/core/meteorite.py src/core/consult.py` succeeds.

1. In `src/core/meteorite.py` module docstring, extend the public-entry sentence: stage classifies blob+source handle then maps scraps → `land_meteorite` (AST-1530); skip outcomes do not land. Add import of `STAGE_METEORITE_CONFIG` from `src.utils.config` (keep existing `METEORITE_CONFIG` / `TASK_CONFIG` imports).

2. Place public `stage_meteorite` **immediately before** `land_meteorite` (public-then-helpers: stage and land are both public; scrap-map helpers below land helpers or grouped under a `# --- stage_meteorite helpers ---` section after the public functions — prefer helpers **after** both public functions if that matches current file layout; do not scatter).

3. Signature and docstring:

```python
async def stage_meteorite(
    candidate_id: str,
    blob: str,
    *,
    source_kind: str,
    source_id: str,
    debug: bool = False,
) -> Dict[str, Any]:
    """Public ingress stage: classify blob → scrap map → land_meteorite or skip (AST-1530).

    Does not claim METEORITE_NEW or run qualify_meteorite dispatch. Callers (AST-1531)
    own mailbox/inbox/Contact hygiene after this return.
    """
```

4. Candidate gate (same spirit as `land_meteorite`): empty `candidate_id` → structured error return (see return contract below) with `error="candidate_id is required"`. Missing candidate row via `get_candidate` → `error=f"candidate not found: {cid}"`. Do **not** call the agent when candidate is missing.

5. Late-import consult (cycle-safe, same pattern as land → enrich):

```python
from src.core.consult import invoke_stage_meteorite
```

Build `ctx` from the candidate dict with `astral_candidate_id=cid`. Call `invoke = await invoke_stage_meteorite(cid, blob, source_kind=source_kind, source_id=source_id, ctx=ctx, debug=debug)`.

6. If `not invoke.get("success")`: return stage error (no land). Top-level `outcome` = `METEORITE_CONFIG["land_outcome_error"]`; include `stage_outcome=None`, `skipped=False`, `scraps=[]`, `land=None`, `error=invoke.get("error")`, `batch_id=invoke.get("batch_id")`. Style D when debug: index outcome `"stage_invoke_failed"`.

7. `stage_outcome = invoke["outcome"]` (already config-validated by the helper).

8. **Skip path** — if `stage_outcome in STAGE_METEORITE_CONFIG["skip_outcomes"]`:
   - Do **not** call `land_meteorite`.
   - Return: `outcome=stage_outcome`, `stage_outcome=stage_outcome`, `skipped=True`, `scraps=[]`, `land=None`, `error=None`, `batch_id=…`.
   - Style D when debug: index header `func="meteorite.stage_meteorite"`, identifier=`cid`, outcome=`stage_outcome`; detail `source_kind=… source_id=… scrap_count=0 land=skip`.

9. **Scrap map** — call helper `_map_stage_jobs_to_scraps(stage_outcome, invoke.get("jobs") or [], source_kind=…, source_id=…)` (implement in step 11). If the map returns an error string (invalid URL for scrape outcomes, empty landable scraps): return stage error with `land_outcome_error`, no land; Style D detail the reason.

10. **Land path** — `land = await land_meteorite(cid, scraps=scraps, debug=debug)`. Return: `outcome=land.get("outcome")` (Tracker rollup), `stage_outcome=stage_outcome`, `skipped=False`, `scraps=scraps`, `land=land` (full land dict), `error=land.get("error")`, `batch_id=…`, plus pass through `company` / `company_inserted` / `outcomes` from `land` at the top level for caller convenience (`company=land.get("company")`, etc.). Style D when debug: index outcome=`stage_outcome` → recorded land rollup; detail `scrap_count=N` + truncated scrap link/body summary via `truncate_debug_content` when bodies are long; **no** new contract lines when `debug=False`.

11. Implement `_map_stage_jobs_to_scraps(outcome, jobs, *, source_kind, source_id) -> tuple[list[dict], Optional[str]]` returning `(scraps, error)`:

    - Resolve `prefix = STAGE_METEORITE_CONFIG["source_ref_prefixes"][source_kind]` (caller already validated kind via invoke; if missing key → `([], "invalid source_kind")`).
    - `sid = (source_id or "").strip()`.
    - Helper `_source_ref(index: Optional[int] = None) -> str`: if `index is None` → `f"{prefix}{sid}"`; else → `f"{prefix}{sid}-{index}"` (1-based index for multi-row individuation).

    - **`outcome in text_source_ref_outcomes`** (`single_jd_no_link`, `multi_jd_inline`):
      - Require `len(jobs) >= 1`; else `([], "text outcome produced no jobs")`.
      - For each job at 1-based `i`:  
        `ref = _source_ref(None if len(jobs) == 1 else i)`  
        scrap keys for `land_meteorite`:  
        - `job_link` = `ref`  
        - `company_job_id` = `ref`  
        - `text` = `(job.get("jd_text") or "").strip()` (also acceptable to set `content` to the same string — `_land_scrap_body` reads `content`/`text`/`html_body`)  
        - `employer_name` = strip of job’s `employer_name` if str else `""`  
        - optional pass-through: do **not** require agent `job_link`; **overwrite** any agent homepage/URL with `ref` (AC1 / source-ref rule).
      - Reject inventing empty text rows: if `not scrap text/body` after map → `([], "text scrap missing jd_text")` for that outcome (fail the whole map — do not land partial empties).

    - **`outcome in url_scrape_outcomes`** (`single_jd_with_more`, `link_list`):
      - Require `len(jobs) >= 1`; else `([], "url outcome produced no jobs")`.
      - For each job at 1-based `i`:  
        `link = (job.get("job_link") or "").strip()`  
        - Must start with `http://` or `https://`; else `([], "url scrap missing http(s) job_link")`.  
        - `company_job_id` = `_source_ref(None if len(jobs) == 1 else i)` (source-ref until scrape/qualify extracts ATS id — AC2).  
        - `job_link` = `link` (agent posting URL — land scrapes when body thin).  
        - `text`/`content` = strip of `jd_text` if present (may be empty; land scrapes).  
        - `employer_name` as above.

    - **`outcome in skip_outcomes`**: should not reach the mapper (caller returns earlier); if called → `([], None)` with empty scraps.

    - **Any other outcome**: `([], "unhandled stage outcome")`.

⚠️ **Decision — source-ref individuation:** Single-row landable → `{prefix}{source_id}`; multi-row → `{prefix}{source_id}-{n}` (1-based). Keeps dedupe identity stable without inventing UUIDs or using company homepages.

⚠️ **Decision — no second Playwright:** URL thin-body scrape stays inside existing `land_meteorite` → `_land_fetch_link_text`. Stage never imports `get_visible_text` / gazer scrape for this path.

⚠️ **Decision — return contract (for AST-1531):** Always a dict with keys:  
`outcome`, `stage_outcome`, `skipped`, `scraps`, `land`, `error`, `batch_id`, and when land ran also top-level `company`, `company_inserted`, `outcomes` copied from `land`. Skip uses `outcome == stage_outcome` (config literal). Agent/map failures use `METEORITE_CONFIG["land_outcome_error"]` for `outcome` and `skipped=False`.

12. Compile gate: `python3 -m py_compile src/core/meteorite.py src/core/consult.py` (repo venv if needed: `~/astral/.venv/bin/python`).

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; publish to `origin/sub/AST-1527/AST-1530-core-stage-scrap-land` after each stage (build-child).
- No files outside the Files Changed table.
- Ambiguity / drift → stop, comment on **parent** AST-1527 with the Stage blocked format from plan-child, wait.
- Do not implement AST-1531 caller cutover or re-edit AST-1529 catalog/config.
- Do not claim `METEORITE_NEW` or invoke `qualify_meteorite` dispatch from stage (land’s enrich packet may still call `do_task(qualify_meteorite)` as today — that is land’s existing path, not a stage claim).

## Estimate

Confirm Chuckles estimate: 5 — agree

New public core entry + consult invoke helper on a known enrich/`do_task` pattern; scrap map is careful but bounded to config partitions; no caller cutover in this child.

## Joan validate

```text
[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1530
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1527/AST-1530-core-stage-scrap-land` @ `c29d47d88413facb675cffa2d4d9e40cfb4ac951`

## Traceability
AC1–AC4 → Stage 2 (`_map_stage_jobs_to_scraps` partitions + `land_meteorite`); AC5 → Stage 2 skip path (no `land_meteorite`); AC6 → Stage 2 docstring/contract (no METEORITE_NEW / qualify dispatch from stage; land remains write API); AC7 → Stage 1 + Stage 2 Style D gated on `debug=True` only. Stage 1 → `invoke_stage_meteorite` / `do_task("stage_meteorite")`.

## Findings

### discuss — `pattern.agent.prompt-persist-before-provider` citation
Ticket/parent cite this pattern; catalog entry is `status: proposed` (not `approved`). Plan conforms by delegating through existing `do_task` (same as `enrich_meteorite_land_packet`) — no new provider/persist sequencing in stages. Epic-level canon status, not a missing implementation step; no plan rewrite required for AST-1530 build.

### acceptable — Dual Style D on `debug=True` success path
`invoke_stage_meteorite` and `stage_meteorite` each emit gated index/detail. Slightly redundant but both respect `debug=False` silence and match enrich+land layering.

### acceptable — `invoke_stage_meteorite` success detail omits `source_id`
Stage path detail includes `source_id`; invoke helper logs `source_kind` only. AC7 “source handle” is still recoverable from live_content assembly; minor observability gap, not a functional AC miss.

context_tokens≈38000
```

## Review (build stub)

**Publish ref:** `origin/sub/AST-1527/AST-1530-core-stage-scrap-land`
**Plan path:** `docs/features/meteorite/ast-1530-core-stage-scrap-land.md`

**Built tip:** `4df72aa8675e4926f31c2cc918ac29c92a5c0311` (`4df72aa8`)

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `61d940e7` | `consult.invoke_stage_meteorite` — live_content + `do_task(stage_meteorite)` |
| 2 | `4df72aa8` | public `meteorite.stage_meteorite` + `_map_stage_jobs_to_scraps` → land/skip; Style D |

**agent.py:** untouched (plan Decision).
