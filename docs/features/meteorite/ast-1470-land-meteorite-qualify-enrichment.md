# AST-1470 — land_meteorite + qualify_meteorite enrichment

**Linear:** [AST-1470](https://linear.app/astralcareermatch/issue/AST-1470/land-meteorite-qualify-meteorite-enrichment-meteorite-component)  
**Parent:** [AST-1457](https://linear.app/astralcareermatch/issue/AST-1457/meteorite-component) — Meteorite component  
**Publish ref:** `sub/AST-1457/AST-1470-land-meteorite-qualify-enrichment`

Public `land_meteorite`: candidate-bound scraps (link-only, text-only, or both) → optional Playwright visible-text fetch → packet enrichment via repurposed `qualify_meteorite` (`do_task`) → Tracker `save_meteorite_job` (AST-1469) under `meteorite-{candidate_id}` with known-employer metadata. Explicit created / duplicate_skip / superseded / error outcomes — never a silent no-op. No Gmail/mailbox I/O in meteorite. Style D when `debug=True`.

## Scope gate

Ticket **## Scope** (verbatim partition):

- `src/core/meteorite.py` (`land_meteorite`, no Gmail)
- `src/core/agent.py` / `src/core/consult.py` (invoke repurposed `qualify_meteorite`)
- `tests/component/core/test_meteorite.py` — Betty owns the test-tree; engineer does not edit (pre-commit ban). Listed so qa-child knows the contract surface.

All Files Changed / Stages stay inside that set. **Out of scope (siblings):** `config.py` / `database.py` / Tracker save (AST-1469 — already on `origin/ftr/AST-1457-meteorite-component`); intake API + Contact (AST-1471); inbox `fetch_email` / `gaze_email` / gazer email ingest retarget / dispatcher / `api_inbox` (AST-1472). Do **not** retarget existing `create_meteorite_job` callers in this ticket — leave them for #3/#4.

**Depends on:** AST-1469 `tracker.save_meteorite_job`, `METEORITE_CONFIG` land outcome keys, `JOB_SOURCE_*`, `employer_name_job_data_key`, and `qualify_meteorite` items_schema with optional `astral_job_id` + `employer_name` (present after sync with `origin/ftr/AST-1457-meteorite-component`).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/consult.py` | Add `enrich_meteorite_land_packet` — assemble scrap packet → `do_task(qualify_meteorite)` → return field rows; no claim, no `initialize_job`, no state transition | core |
| `src/core/agent.py` | Module-header note + any minimal invoke-path support required so land `do_task(qualify_meteorite)` persists RESPONSE with packet `index` (no new Anthropic client paths; no `config.py` SEED edits) | core |
| `src/core/meteorite.py` | Public async `land_meteorite`; scrap normalize; optional link visible-text via `external.playwright.get_visible_text`; call consult enrich + `tracker.save_meteorite_job`; Style D; keep `create_meteorite_job` / `ensure_meteorite_company` | core |
| `tests/component/core/test_meteorite.py` | Betty / qa-child — `land_meteorite` outcome + no-Gmail + employer metadata contracts | tests (Betty only) |

## Stage 1: Consult — packet enrich via repurposed `qualify_meteorite`

**Done when:** Callers can `await enrich_meteorite_land_packet(...)` with one or more scrap rows and get a list of Ruth field dicts (or a structured error) without writing jobs or transitioning state. Existing dispatch `qualify_meteorite` / `_run_batch_consult` path is unchanged.

1. In `src/core/consult.py` module docstring, add one line: land packet enrichment uses the same `qualify_meteorite` task_key via `enrich_meteorite_land_packet` (no claim/transition).

2. Add public **`async def enrich_meteorite_land_packet`**:

```python
async def enrich_meteorite_land_packet(
    candidate_id: str,
    scraps: List[Dict[str, Any]],
    *,
    ctx: Optional[Dict[str, Any]] = None,
    debug: bool = False,
) -> Dict[str, Any]:
```

   **Preconditions:** non-empty stripped `candidate_id`; `scraps` a non-empty list. Else return  
   `{ "success": False, "error": "<reason>", "jobs": [] }`  
   (do not raise for empty scraps — `land_meteorite` maps this to `land_outcome_error`).

3. **Scrap row shape** (each dict; unknown keys ignored):

   | Key | Meaning |
   |-----|---------|
   | `job_link` | Optional URL string |
   | `content` / `text` / `html_body` | Optional scrap body (prefer first non-empty among these, in that order) |
   | `employer_name` | Optional known employer hint (passthrough when Ruth omits) |

   At least one of link or body text must be non-empty after strip per row; drop blank rows. If every row drops, return `success=False` as above.

4. **Assemble live_content** — reuse the same format as `qualify_meteorite`’s inner `assemble` (lockstep with existing Ruth prompt):

```text
METEORITE JOBS:
000: job_link: <link or empty>
CONTENT:
<body text>
001: ...
```

   Use 0-based zero-padded index (`f"{i:03d}"`). Do **not** put `astral_job_id` in live content (matches current assemble).

5. **Invoke agent** — `from src.core.agent import do_task` then:

```python
result = await do_task(
    task_key="qualify_meteorite",
    live_content=live_content,
    index=candidate_id,          # packet-level index; no job id yet
    ctx=task_ctx,                # must include candidate raft when available
    debug=debug,
)
```

   Build `task_ctx` from `ctx` or load candidate via existing consult/candidate helpers so `requires_candidate_key` is satisfied (same pattern as other consult entry points that pass `ctx` with `astral_candidate_id` / `candidate_data` / `candidate_api_key`). Set `batch_entities` to a list of stub dicts `{ "job_link": ..., "job_data": { jd_key: content } }` parallel to scraps so any decode helpers that peek batch_entities do not crash — stubs have **no** `astral_job_id`.

6. **On `do_task` failure:** return `{ "success": False, "error": result.get("error") or "do_task failed", "jobs": [], "raw": result }`. No state writes.

7. **On success:** read `parsed_response["jobs"]` (list). Map by list order to input scraps (AST-1469 made `astral_job_id` optional). For each output row `i`:

   - Prefer Ruth fields: `company_job_id`, `job_title`, `job_link`, `jd_text`, `employer_name`.
   - If Ruth `job_link` empty, fall back to scrap `job_link`.
   - If Ruth `employer_name` empty, fall back to scrap `employer_name`.
   - Resolve `company_job_id` with existing `_resolve_company_job_id(ai_id, job_link)` (same as qualify process).
   - Append `{ "company_job_id", "job_title", "job_link", "jd_text", "employer_name", "scrap_index": i }`.

   Return `{ "success": True, "jobs": <list>, "error": None }`.

8. **Style D** (only `debug=True`): one `debug_index` per scrap row under `func="consult.enrich_meteorite_land_packet"` with outcome `enriched` or `enrich_failed`; `|` detail: link, content chars in, jd_chars out, employer_name present/absent. No new contract lines when `debug=False`.

9. **Do not** call `tracker.initialize_job`, `_transition_job_state_for_task`, or `_run_batch_consult` from this function. Dispatch `qualify_meteorite` remains the post-create METEORITE_NEW → METEORITE_QUALIFIED path (no daisy-chain in land).

⚠️ **Decision:** Packet enrichment is a **separate consult entry** that shares `task_key="qualify_meteorite"` + assemble shape + field resolution helpers, not a fork of `_run_batch_consult` process(). That preserves claim/transition law for the dispatch path while satisfying parent “repurpose qualify_meteorite” for pre-create land.

⚠️ **Decision:** Land does **not** transition to `METEORITE_QUALIFIED` in this run (`astral.state.no-daisy-chain-in-run`). Tracker save lands `METEORITE_NEW` via AST-1469; later dispatch qualify still owns qualification.

## Stage 2: Agent — land invoke support (minimal)

**Done when:** `do_task(qualify_meteorite, …)` from Stage 1 persists prompt/RESPONSE under the packet `index` without requiring a pre-existing job row; `agent.py` documents the land call shape. No Anthropic client changes. No `config.py` / SEED edits (out of Scope).

1. In `src/core/agent.py` module docstring (or the `do_task` docstring), add a short note: land packet enrichment may call `do_task(task_key="qualify_meteorite", index=<candidate_id>, …)` before a job row exists; `entity_id` / RESPONSE tagging uses that index string.

2. Verify (read-only at build time) that `do_task` already tolerates `index` that is not an `astral_job_id` UUID for fields tasks — existing path stores by `index` / batch_id. **If** a hard assumption rejects non-job indexes (raises or skips store), fix **only** the minimal guard in `agent.py` so land’s candidate_id index is accepted for `qualify_meteorite` when no job row exists. Do **not** broaden unrelated tasks.

3. **Prompt delta:** Do **not** edit `config.py` SEED. Prefer scrap `employer_name` passthrough (Stage 1 step 7) so Ruth need not invent employer. If build discovers the live `agent_task` prompt for `qualify_meteorite` cannot accept packet content without an `astral_job_id` in the user prompt (runtime failure with a clear prompt mismatch), stop and comment on **parent AST-1457** with the Stage blocked template — do not invent a config SEED change inside this ticket’s Scope.

⚠️ **Decision:** Employer metadata primarily from scrap hint / Ruth optional field already in AST-1469 schema — avoids a Scope-breaking `config.py` prompt seed edit unless proven necessary at build.

## Stage 3: Meteorite — public `land_meteorite`

**Done when:** Contact/inbox/API callers (siblings) can `await land_meteorite(candidate_id, scraps=…, debug=…)` and receive per-job outcomes `created` | `duplicate_skip` | `superseded` | `error` from `METEORITE_CONFIG` land keys; jobs attach under `meteorite-{candidate_id}`; known employer lands in `job_data[employer_name_job_data_key]`; `meteorite.py` has zero Gmail/mailbox imports; `debug=True` emits Style D found→recorded; `debug=False` emits none from this path.

1. Update `src/core/meteorite.py` module docstring: public entry is `land_meteorite`; `create_meteorite_job` remains for legacy callers until AST-1471/1472 retarget; no email I/O in this module.

2. Imports (allowed): `get_candidate`, `ensure` helpers already in file, `tracker.save_meteorite_job`, `TRACKER_CONFIG`, `METEORITE_CONFIG`, logging, `enrich_meteorite_land_packet` from consult, and **`get_visible_text` from `src.external.playwright`** for link flesh-out.  
   **Forbidden:** any `gmail`, `mailbox`, `inbox`, or `meteorite_email` imports in this file.

3. Add helper **`async def _land_fetch_link_text(url: str, *, debug: bool = False) -> tuple[str, str]`**  
   Wrap `get_visible_text(url=url, return_final_url=True)` the same way gazer’s private helper does (normalize tuple vs str). On failure return `("", url)` and let enrich/save decide — do not raise for a single bad link when other scraps remain. Do **not** edit `gazer.py` (out of Scope).

4. Add public **`async def land_meteorite`**:

```python
async def land_meteorite(
    candidate_id: str,
    *,
    scraps: Optional[List[Dict[str, Any]]] = None,
    text: Optional[str] = None,
    job_link: Optional[str] = None,
    employer_name: Optional[str] = None,
    debug: bool = False,
) -> Dict[str, Any]:
```

   **Normalize inputs:**  
   - If `scraps` is None, build a one-row list from `text` / `job_link` / `employer_name`.  
   - If `scraps` provided, ignore top-level text/link only when scraps non-empty; if scraps empty/None and top-level also empty → error outcome (never silent).  
   - Strip candidate_id; missing candidate → `{ "outcome": land_outcome_error, "error": "candidate not found: …", "outcomes": [] }` (or raise `ValueError` — **pick return-with-error** so HTTP siblings can map without try/except for not-found vs validation; use `ValueError` only for programmer misuse like wrong types).

5. **Candidate + company:** `get_candidate`; if missing, return error shape. `ensure_meteorite_company(candidate_id, debug=debug)` → `short_name`, `company_inserted`.

6. **Optional link scrape before enrich:** For each scrap row with a non-empty `job_link` whose body text is empty or shorter than `TASK_CONFIG["qualify_meteorite"]["min_jd_chars"]`, call `_land_fetch_link_text` and set scrap content to visible text when non-empty; if final_url differs, prefer it as `job_link`. Read the min from `TASK_CONFIG` (existing config — do not add new literals to `config.py`).

7. **Enrich:** `enrich = await enrich_meteorite_land_packet(candidate_id, scraps, ctx=…, debug=debug)`.  
   Build `ctx` with `astral_candidate_id=candidate_id` and candidate raft fields needed for `do_task` (mirror other core callers — e.g. load via `get_candidate` / existing ctx builders; if a shared helper already exists in candidate/consult, reuse it).  
   If `enrich["success"]` is False or `jobs` empty → return top-level  
   `{ "outcome": METEORITE_CONFIG["land_outcome_error"], "error": enrich.get("error") or "enrichment produced no jobs", "outcomes": [], "company": short_name, "company_inserted": … }`.

8. **Save each enriched job** via `tracker.save_meteorite_job`:

```python
save = tracker.save_meteorite_job(
    candidate_id,
    company=short_name,
    company_job_id=row.get("company_job_id") or None,
    job_title=row.get("job_title") or None,
    job_link=row.get("job_link") or None,
    job_data={ TRACKER_CONFIG["job_data_keys"]["job_description"]: row.get("jd_text") or "" },
    employer_name=row.get("employer_name") or None,
    debug=debug,
)
```

   Append each save return dict into `outcomes` (already has `outcome` / `astral_job_id` / `job` / `source`). On unexpected `ValueError`/`RuntimeError` from Tracker, append  
   `{ "outcome": land_outcome_error, "error": str(e), "astral_job_id": None }` for that row and continue remaining rows (partial success allowed).

9. **Top-level return:**

```python
{
  "company": short_name,
  "company_inserted": bool,
  "outcomes": [ ... ],           # one entry per enriched job save attempt
  "outcome": <rollup>,           # see Decision below
  "error": Optional[str],        # set when rollup is error and no row succeeded
}
```

   ⚠️ **Decision — rollup `outcome`:**  
   - If every row is `duplicate_skip` → `duplicate_skip`.  
   - Else if any row is `created` or `superseded` → prefer `created` if any created, else `superseded`.  
   - Else if any row is `error` and none created/superseded/skip → `error`.  
   - Else if mix of skip + error only → `duplicate_skip` when any skip else `error`.  
   Callers that need full fidelity always read `outcomes[]`.

10. **Style D** (`debug=True` only): for each scrap/save, `debug_index(func="meteorite.land_meteorite", index=i, total=n, identifier=<astral_job_id or candidate_id>, outcome=<created|duplicate_skip|superseded|error>)` plus `|` detail lines: found link/title/jd_chars/employer → recorded counterparts from `save["job"]` when present. No new contract lines when `debug=False`.

11. Keep **`create_meteorite_job`** and **`ensure_meteorite_company`** behavior unchanged (siblings still call create until retarget).

12. **Import ban check:** after edits, `meteorite.py` must not import gmail/mailbox/inbox/meteorite_email (AC3).

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; publish to `origin/sub/AST-1457/AST-1470-land-meteorite-qualify-enrichment`.
- Do not add files outside the Files Changed table.
- Do not edit `tests/`, bible, `config.py`, `database.py`, `tracker.py`, `gazer.py`, `inbox.py`, `contact.py`, API modules.
- On ambiguity or codebase drift: stop and comment on **parent** AST-1457 with the Stage blocked template from plan-child.

## Estimate

Confirm Chuckles estimate: 5 — agree

New public orchestration + consult packet enrich path + Playwright link flesh-out + Tracker integration is a real multi-file core slice (new land pattern) without schema work (Ada already landed that). Matches Bang !! / estimate 5. No revise.

## Joan validate

[plan-discuss] round=1 concern
[plan-rubric]
**Rubric:** plan-rubric.v1
**Ticket:** AST-1470
**Overall:** REVISE
**Publish ref:** `sub/AST-1457/AST-1470-land-meteorite-qualify-enrichment` @ `b1bc8382799129fb4342d2641a99904cdac3f196`

## Traceability
AC1→Stage 3 `land_meteorite` explicit outcomes + `outcomes[]` (callable API only; Contact/inbox wiring→N/A AST-1471/1472 per Boundaries); AC2→Stage 1 scrap/`employer_name` passthrough + Stage 3 `save_meteorite_job(..., employer_name=…)` under `meteorite-{candidate_id}`; AC3→Stage 3 import ban + module docstring (no Gmail in meteorite; Contact/inbox call→N/A siblings); AC4→Stage 1 `do_task(task_key="qualify_meteorite")` separate entry, no `_run_batch_consult` transition; AC5→Stages 1/3 Style D gated on `debug=True`. Parent AC6–10→N/A (ingress retarget/API/inbox). Stages 1–3→child Scope + parent Functional #1/#5/#6/#9/#10 slice.

## Findings

### fix-now — Stage 1 missing `batch_id` / `log_batch_id` before `do_task`
**Location:** Stage 1 step 5; Stage 2 done-when (“persists prompt/RESPONSE”)  
**Finding:** `do_task` only stores agent_data when `store_agent_data and batch_id and entity_type` (`batch_id = hop_ledger_batch_id or log_batch_id.get()`). Land enrich calls `do_task` outside dispatch with no `log_batch_id` set — `_should_store` is false, so no prompt/RESPONSE rows despite Stage 2 requiring persistence. Dispatch `qualify_meteorite` uses `do_index = f"{task_key}_batch_{batch_id}"` under an active batch context; land cannot reuse that shape without generating its own id.  
**Recommendation:** Stage 1 step 5 must mint a land batch id (e.g. `f"qualify_meteorite-land-{uuid4()}"`), `log_batch_id.set(...)` for the call (clear in `finally`), and document the `index` string used — mirror `_run_batch_consult` audit trail.

### fix-now — Top-level `meteorite` → `consult` import will cycle
**Location:** Stage 3 step 2 (`enrich_meteorite_land_packet` from consult)  
**Finding:** `consult.py` already imports `is_meteorite_company` from `meteorite` at module load. A module-level `from src.core.consult import enrich_meteorite_land_packet` in `meteorite.py` creates a consult↔meteorite import cycle.  
**Recommendation:** Late-import `enrich_meteorite_land_packet` inside `land_meteorite` only (same carve-out family as AST-1469 tracker/meteorite note).

### discuss — AC1 / AC3 caller wiring deferred (acceptable partition)
**Location:** Child AC1 + AC3 vs Boundaries / Execution contract  
**Finding:** Ticket AC text says Contact/inbox “can call” `land_meteorite`; plan correctly implements the core entry only and defers retarget to AST-1471/1472.  
**Recommendation:** Add one traceability note in plan Scope gate: AC1/AC3 “callable” half = this ticket; “wired” half = siblings — no scope change needed once batch_id fix lands.

### discuss — `entity_id` tagging with `entity_type=job` + `index=candidate_id`
**Location:** Stage 1 step 5 / Stage 2 step 2  
**Finding:** `qualify_meteorite` TASK_CONFIG `entity_type` is `job`; land uses candidate id as index. RESPONSE rows would tag `entity_id=candidate_id` under job entity type — not a valid job row for `list_entity_latest_agent_refs`. May be acceptable for packet-level audit only.  
**Recommendation:** At build, either document “audit-only, no latest-ref consumers” or tag under candidate entity for land calls — engineer choice once batch_id exists.

### discuss — Cited pattern still `proposed`
**Location:** Ticket ## Citations — `pattern.agent.prompt-persist-before-provider`  
**Finding:** Catalog entry is `status: proposed`, not `approved`. Plan relies on existing `do_task` pre-provider `_store_prompt_blocks` (already conforming); no new sequencing work staged.  
**Recommendation:** Citation hygiene only — implementation path is fine via `do_task`.

### acceptable — Dependency on AST-1469 / ftr
**Location:** Scope gate **Depends on**  
**Finding:** `save_meteorite_job` and land outcome keys are on `origin/ftr/AST-1457-meteorite-component`; plan assumes epic sync before build — correct.

### acceptable — Tests row Betty-only
**Location:** Files Changed `test_meteorite.py`  
**Finding:** Engineer pre-commit ban honored; qa-child owns contract tests for AC1–5 — consistent with Betty statute and AST-1469 pattern.

## R6 checklist (summary)
Layer discipline (core→external Playwright, no Gmail in meteorite), config-as-read-only (`TASK_CONFIG` read, no `config.py` edits), no-daisy-chain (enrich without qualify transition), and `do_task` delegation all pass once batch_id + late-import fixes land. Self-assessment (estimate 5, !! orchestration) is honest.

context_tokens≈78000
