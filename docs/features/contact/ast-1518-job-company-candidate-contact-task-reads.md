# AST-1518 — Job / company / candidate contact-task reads

**Linear:** [AST-1518](https://linear.app/astralcareermatch/issue/AST-1518/job-company-candidate-contact-task-reads-estelle-needs-to-be-able-to)  
**Parent:** [AST-1414](https://linear.app/astralcareermatch/issue/AST-1414/estelle-needs-to-be-able-to-use-our-endpoints) — Estelle needs to be able to use our endpoints  
**Publish ref:** `sub/AST-1414/AST-1518-job-company-candidate-contact-task-reads`

Child #4 of AST-1414: implement the four read handlers registered by sibling AST-1515 in `CONTACT_TASK_CONFIG` — `contact_task_get_job_by_pattern`, `contact_task_get_job_data`, `contact_task_get_company_data`, `contact_task_get_candidate_data` — in `src/core/tracker.py`. Thin wrappers over extant getters + `agent.get_entity_agent_story` hydration; candidate-scoped; refuse cross-candidate / unmatched patterns. Does **not** own markup/dispatch (AST-1515), gazer scrape, or meteorite create. Does **not** create jobs or run new analysis.

## Scope gate

Ticket **## Scope** (verbatim partition):

- `src/core/tracker.py` (modified — `get_job_by_pattern` + contact-task read wrappers). Technical: candidate-scoped pattern match; read helpers delegating to existing `get_job_data`, `roster.get_company_data`, `candidate.get_candidate`, and `agent.get_entity_agent_story`; refuse cross-candidate or unmatched patterns.

**Out of scope:** `config.py` / `contact.py` / `agent_task.json` (AST-1515); `gazer.py` (AST-1516); `meteorite.py` (AST-1517). Do **not** rename or rewrite extant coat-check `get_job_data(job, key)` / `roster.get_company_data(company, key)` — contact-task entrypoints are **new** `contact_task_*` names matching AST-1515 handler dotted paths.

**Depends on:** AST-1515 tip on epic worktree (`CONTACT_TASK_CONFIG` handlers already point at `src.core.tracker.contact_task_*`). Stack via merge of `origin/ftr/AST-1414-estelle-endpoints` (or AST-1515 publish tip) before product commits.

**Handler contract (AST-1515 Stage 2):** sync or async  
`handler(astral_candidate_id: str, param: str, *, debug: bool = False) -> dict`  
Return a `dict` with `ok` and `task_key`; on success put payload under `result`. Contact dispatch already Style-D bookends the call — handlers emit their own Style D found/recorded when `debug=True` (ticket AC7 / parent AC8).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/tracker.py` | New public `get_job_by_pattern`; four `contact_task_*` read wrappers; private hydrate helper; Style D on read paths | core |

## Stage 1: Pattern resolve + hydrate helpers

**Done when:** `get_job_by_pattern(astral_candidate_id, pattern)` returns one candidate-scoped job row or raises/`None` per contract below; a private hydrate helper attaches `agent_story` via late-imported `get_entity_agent_story`. No contact-task entrypoints yet.

1. In `src/core/tracker.py` module docstring, note AST-1518: contact-task read wrappers + `get_job_by_pattern`.

2. Add private **`_contact_task_hydrate_job(job: Dict[str, Any]) -> Dict[str, Any]`**:

   - Shallow-copy the job dict.
   - Late-import `from src.core.agent import get_entity_agent_story` (avoid load cycles).
   - Set `out["agent_story"] = get_entity_agent_story(out)` (list; empty list on soft-fail — story already soft-fails internally).
   - Return `out`. Do **not** call async coat-check `get_job_data` / gazer self-heal — parent boundary: no new analysis / no scrape from this ticket.

3. Add public **`get_job_by_pattern(astral_candidate_id: str, pattern: str) -> Optional[Dict[str, Any]]`**:

   a. `cid = (astral_candidate_id or "").strip()`; `pat = (pattern or "").strip()`. If either empty → return `None`.  
   b. `jobs = list_jobs(candidate_id=cid)` (existing tracker facade).  
   c. Casefold `pat_cf = pat.casefold()`. Match a job when **any** of these fields, as string, casefold-contains `pat_cf` **or** equals `pat` / `pat_cf` for id:

   - `astral_job_id`
   - `job_title`
   - `company` (short_name column)
   - `job_link`

   d. Collect all matches. If **zero** → `None`. If **more than one** → return `None` (caller maps to `ambiguous_pattern` — refuse rather than guess). If **exactly one** → return that job dict (raw row, not yet hydrated).

   ⚠️ **Decision — ambiguous → refuse:** Parent AC5 requires refuse on unresolved pattern; multiple hits are unresolved for Estelle purposes. Single exact id match still wins when the pattern equals `astral_job_id`.

4. Do **not** add contact_task_* wrappers in this stage.

## Stage 2: Four `contact_task_*` read wrappers

**Done when:** All four handlers exist with the AST-1515 signatures, candidate-scope checks, hydrate where applicable, Style D when `debug=True`, and return shapes Contact dispatch can normalize. Extant coat-check `get_job_data` / `roster.get_company_data` remain unchanged.

1. Add private Style D helper used by all four (keeps DRY):

```python
def _contact_task_style_d(
    log, *, func: str, identifier: str, found_detail: str, recorded_detail: str, debug: bool
) -> None:
    if not debug:
        return
    log.set_debug_flag(True)
    log.debug_index(func=func, index=1, total=2, identifier=identifier, outcome="found")
    for line in truncate_debug_content(found_detail):
        log.debug_detail(line)
    log.debug_index(func=func, index=2, total=2, identifier=identifier, outcome="recorded")
    for line in truncate_debug_content(recorded_detail):
        log.debug_detail(line)
```

   Import `truncate_debug_content` from `src.utils.logging` if not already imported; use existing `logger` / `get_logger(__name__)`.

2. **`contact_task_get_job_by_pattern(astral_candidate_id, param, *, debug=False) -> dict`**

   - Empty cid → `{"ok": False, "error": "no_candidate", "task_key": "get_job_by_pattern"}`.  
   - Empty param → `{"ok": False, "error": "unmatched_pattern", "task_key": "get_job_by_pattern"}`.  
   - `job = get_job_by_pattern(cid, param)`.  
   - If `None`: distinguish via a second list pass — if ≥2 matches would have hit → `ambiguous_pattern`; else `unmatched_pattern`. (Implement by having `get_job_by_pattern` return `None` and a small private `_match_jobs_by_pattern(cid, pat) -> List[Dict]` used by both, so counts are exact.)  
   - If job's `candidate_id` (when present) is a non-empty string and ≠ cid → `refused_cross_candidate` (defense in depth; `list_jobs` already scoped).  
   - Else hydrate → `{"ok": True, "task_key": "get_job_by_pattern", "result": hydrated}`.  
   - Style D: identifier=`get_job_by_pattern`; found=`param=…`; recorded=`ok=… error=…` or `astral_job_id=…`.

3. **`contact_task_get_job_data(astral_candidate_id, param, *, debug=False) -> dict`**

   - Empty cid → `no_candidate`. Empty param → `not_found`.  
   - `job = get_job(param.strip())`. If missing → `not_found`.  
   - If `job.get("candidate_id")` is a non-empty str and ≠ cid → `refused_cross_candidate`.  
   - ⚠️ **Decision — do not call async coat-check `get_job_data(job, key)`:** that path self-heals JD via gazer (out of Boundaries). This handler returns the stored job row + `agent_story` hydration only. Parent Technical scope's "delegating to existing `get_job_data`" is satisfied by composing **`get_job`** (tracker job read) + hydration; the coat-check function keeps its existing name/signature for gazer/consult callers.  
   - Hydrate → success result. Style D as above (`task_key` / identifier `get_job_data`).

4. **`contact_task_get_company_data(astral_candidate_id, param, *, debug=False) -> dict`**

   - Empty cid → `no_candidate`. Empty param → `not_found`.  
   - Late-import `from src.core.roster import get_company as roster_get_company` **or** use tracker `get_company(param.strip())` (already a thin database delegate in tracker — prefer **tracker `get_company`** to stay inside Files Changed without inventing a roster import unless needed).  
   - If company missing → `not_found`.  
   - Scope check: company `candidate_id` when present must equal cid; **or** if company has no `candidate_id`, require at least one `list_jobs(candidate_id=cid)` row whose `company` equals the company's `short_name`. Else → `refused_cross_candidate`.  
   - Build result: shallow copy of company row; late-import `get_entity_agent_story` and set `agent_story` from the company entity dict (story keys off `short_name`).  
   - ⚠️ **Decision — do not invoke async `roster.get_company_data(company, key)` coat-check:** same boundary as job (no on-demand website fetch). Wrapper returns stored company + agent story.  
   - Style D with identifier `get_company_data`.

5. **`contact_task_get_candidate_data(astral_candidate_id, param, *, debug=False) -> dict`**

   - Empty cid → `no_candidate`.  
   - Load via existing `candidate_mod.get_candidate(cid)` (module already imported as `candidate_mod` in tracker). Missing → `not_found`.  
   - Optional `param`: if non-empty after strip, treat as a dotted path under `candidate_data` (e.g. `profile.first`). Walk dict keys; if any segment missing → `not_found`. Success `result` is the leaf value (or full candidate row + `agent_story` when param empty).  
   - When param empty: shallow-copy candidate row; attach `agent_story` via `get_entity_agent_story` (entity uses `astral_candidate_id`).  
   - Never write / never invent fields. Style D with identifier `get_candidate_data`.

6. Error strings (exact literals for Betty / Contact follow-up):  
   `no_candidate` | `not_found` | `unmatched_pattern` | `ambiguous_pattern` | `refused_cross_candidate`.

7. Confirm AST-1515 config paths resolve: after this stage, `importlib` of  
   `src.core.tracker.contact_task_get_job_by_pattern` (and the other three) must succeed — no config.py edits.

## Execution contract

- Stages in order; one commit per stage on epic worktree; push  
  `git push origin HEAD:sub/AST-1414/AST-1518-job-company-candidate-contact-task-reads` after each.
- No files outside Files Changed.
- Before Stage 1 product work: ensure AST-1515 / `origin/ftr/AST-1414-estelle-endpoints` is merged into the sub (CONTACT_TASK_CONFIG present).
- Ambiguity or missing `list_jobs` / `get_job` / `get_candidate` → stop, comment on **AST-1518** with Stage blocked format, wait.
- Test tree / bible: Betty only.

## Estimate

Confirm Chuckles estimate: 3 — agree
