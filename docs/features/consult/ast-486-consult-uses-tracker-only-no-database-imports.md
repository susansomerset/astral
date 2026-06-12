# AST-486 — Consult uses tracker only, no database imports

**Parent:** [AST-372 — Consult fetch job by ID through tracker, not database](https://linear.app/astralcareermatch/issue/AST-372/consult-fetch-job-by-id-through-tracker-not-database)  
**Branches (origin):** parent integration `origin/ftr/AST-372-consult-fetch-job-by-id-through-tracker-not-database`; child publish **`origin/sub/AST-372/AST-486-consult-uses-tracker-only-no-database-imports`** (dispatch).

Susan’s goal: **`src/core/consult.py` must never import `src.data.database`.** Job-by-ID and other reads/writes used by consult go through **`src/core/tracker.py`**, which already wraps the data layer for jobs and exposes UI-oriented facades. This keeps batch-scoped consult logic on the tracker boundary and simplifies layer hygiene (consult → tracker → database, not consult → database).

## Files Changed (planned)

Spike/investigation output (if ever needed): **`debug/spikes/AST-486/…`** only — not repo plans.

| File | Change | Layer |
|------|--------|-------|
| `src/core/tracker.py` | Add thin delegates `get_company`, `append_agent_response`, `list_timesheets` next to existing “UI API facades” block (same style as `list_jobs`) | core |
| `src/core/consult.py` | Remove database import entirely; route all former call sites through `tracker` | core |
| `src/core/agent.py` | In `run_resume_artifact_chain_for_job` and `run_cover_letter_artifact_chain_for_job`, replace lazy `database` imports of `get_job`/`get_company` with `tracker.get_job` / `tracker.get_company` | core |

---

## Stage 1: Tracker delegates for consult

**Done when:** `tracker.py` exposes `get_company`, `append_agent_response`, and `list_timesheets`, each documented as a one-line delegate following the pattern of `tracker.list_jobs` / `tracker.get_job`; `python -m compileall` for edited module passes (executor runs fuller checks at end of pipeline).

1. Open `src/core/tracker.py`. Scroll to section `# ---- UI API facades (AST-321)...` (~line 384). Immediately after `get_job` (lines 276–279) **or** at the end of that facades cluster (preferred: **group consult-facing reads with existing facades**, after `score_floor_by_trigger_for_candidate` / before `job_misses_dispatch_score_floor` is fine — keep “facade” functions together).

2. Add **`get_company(short_name: str) -> Optional[Dict[str, Any]]`** containing only: `return database.get_company(short_name)`. Match the **`database.get_company`** name and semantics (already used by consult): single `short_name`, returns `Optional[dict]`.

3. Add **`append_agent_response(entity_type: str, entity_id: str, entry: Dict[str, Any]) -> None`** containing only: `database.append_agent_response(entity_type, entity_id, entry)` — same arity and types as **`database.append_agent_response`** (see `database.py` ~3564).

4. Add **`list_timesheets`** as a **`**kwargs` forwarder**: `return database.list_timesheets(**kwargs)` — mirror today’s **`consult.list_timesheets`** passthrough so `api_admin.py` callers keep working unchanged (`consult.list_timesheets` will call into tracker in Stage 2). Add a one-line docstring: thin delegate for layering (UI/core must not reach database for timesheets reads).

5. Update the **`tracker.py` module docstring** top bullets to mention these three entry points alongside existing batch/job APIs **only if** missing; otherwise a short comment above the new trio is enough: `# Consult / API facades — delegate reads-writes AST-486`.

⚠️ **Decision:** Delegates live on `tracker`, not `roster`, because `get_company`/`append_agent_response`/timesheets are already job-orchestration-adjacent and `tracker.py` owns the documented “thin wrapper” corridor for Flask imports; avoids splitting consult across two façade modules.

---

## Stage 2: Purge database imports from `consult.py`

**Done when:** `rg 'src\.data\.database' src/core/consult.py` returns no matches; all former `get_job` / `get_company` / `append_agent_response` / timesheet forwarding use `tracker`.

1. **Remove** the import line  
   `from src.data.database import get_job, get_company, list_timesheets as _db_list_timesheets, append_agent_response`  
   Keep `from src.core import tracker, roster` unchanged.

2. **`render_verdict`** (~lines 327–335): Replace `job = get_job(astral_job_id)` with **`job = tracker.get_job(astral_job_id)`**. Replace `company = get_company(job["company"])` with **`company = tracker.get_company(job["company"])`** when `cfg.get("requires_company")` is true.

3. **`_run_batch_consult`** (~lines 532–533): Replace `append_agent_response(entity_type, aid, agent_ref)` with **`tracker.append_agent_response(entity_type, aid, agent_ref)`** inside the `try` block. Leave exception handling and logging unchanged.

4. **`_run_cover_letter_for_job`** (~line 740): Replace `row = get_job(astral_job_id) or job` with **`row = tracker.get_job(astral_job_id) or job`** (same semantics: optional refresh when caller already passed `job`).

5. **`_run_craft_job_cover_letter_batch`** (~line 788): Replace `row = get_job(aid) or job` with **`row = tracker.get_job(aid) or job`**.

6. **`list_timesheets`** (~lines 881–883): Replace body `return _db_list_timesheets(**kwargs)` with **`return tracker.list_timesheets(**kwargs)`**. Preserve the public function signature and docstring intent (Admin API imports `consult.list_timesheets` — **do not change `api_admin.py`** in this ticket).

⚠️ **Decision:** Optional dedupe/double-fetch: where `entities[0]` in `render_verdict` call path already carries a full job row, **leave** **`render_verdict(task_type, astral_job_id, …)`** behavior as **`tracker.get_job(astral_job_id)`** everywhere it appears today unless a later ticket threads `job` through the dispatcher contract; correctness first, perf micro-opt out of AST-486 scope unless Susan adds it.

---

## Stage 3: `agent.py` lazy imports — `get_job` / `get_company` via tracker only

**Done when:** `rg 'from src\.data\.database import get_job' src/core` returns no hits; consult + agent chain resolve jobs/companies via `tracker`.

1. **`run_resume_artifact_chain_for_job`** (inner block starting ~647): Replace  
   `from src.data.database import get_job, get_company`  
   with **`from src.core import tracker`** (keep `from src.core import consult as _consult` as-is). Replace **`get_job(astral_job_id)`** with **`tracker.get_job(astral_job_id)`** and **`get_company(cid)`** with **`tracker.get_company(cid)`**.

2. **`run_cover_letter_artifact_chain_for_job`** (~725): Same replacement block as step 1 for the lazy-import line and both call sites (`get_job`, `get_company` → **`tracker`**).

⚠️ **Decision:** Leave all **other** `agent.py` top-level **`src.data.database` imports untouched** (`append_agent_response` for agent internals, `save_agent_data`, etc.). AST-486 scope is **eliminating trivial `get_job`** from **`src/core/*`** alongside consult layer hygiene — not re-homing all of `agent.py`.

---

## Execution contract

Binding per **plan-astral**: execute stages 1→2→3 in order; one commit per stage on **`dev-hedy`** during **build-astral**, then cherry-pick to **`origin/sub/AST-372/AST-486-consult-uses-tracker-only-no-database-imports`** per Chuckles workflow. Do not edit **`builder.py`**, **`analysis_upshot`**, **`AST-478`** feature blobs, batch router semantics beyond imports, or `api_admin` import paths.

**Verification checklist (executor / test-astral):**

1. `rg 'src\.data\.database' src/core/consult.py` → empty.
2. `rg 'from src\.data\.database import .*get_job' src/core` → empty.
3. `rg 'tracker\.get_job|tracker\.get_company|tracker\.append_agent_response|tracker\.list_timesheets' src/core/consult.py` → hits at all migrated call sites.
4. `GET /api/admin/timesheets` still exercises **`consult.list_timesheets`** → **`tracker.list_timesheets`** chain (manual or existing tests).

---

## Self-Assessment

**Scope:** `Single-Component` — Touches tracker facades plus consult orchestration plus two agent chain helpers; limited to core layer import wiring.  

**Conf:** `conf-high` — Matches existing **`tracker`** delegate pattern (`get_job`, `list_jobs`) and deterministic call-site renames with no behavioral spec change intended.  

**Risk:** `risk-Medium` — A wrong **`get_job`/`get_company`** call or typo in delegated kwargs would break **`render_verdict`**, artifact chains, or **`agent_responses` appends`; batch consult paths are sensitive but localized.

---

## Self-review vs ASTRAL_CODE_RULES

- **§1.3 DRY:** One delegation site per primitive in `tracker`; consult does not reimplement reads.
- **§2.1 config:** No changes.
- **§2.4 batch processing:** Claim/clear pattern unchanged — only façade indirection for single-row lookups and `append_agent_response`.
- **§2.6 state machine:** **`transition_job_state`** still owned by **`tracker`**; consult still calls **`tracker.transition_job_state`** / **`tracker.save_job_data`** as today.
- **§3.3 imports:** **`consult`** goes **core → tracker** (and existing **roster/agent/utils**); **`agent`** inner block uses **`tracker`** for **`get_job`/`get_company`** only; aligns with Bright Line (**core orchestrates**, data reached via façade).
- **§3.5 naming:** Preserve **`database`** function names on **`tracker`** (`get_company`, **`list_timesheets`**, **`append_agent_response`**).

No conflicts flagged; plan is implementation-ready.

---

## Review

**Baseline:** three-dot **`origin/dev…origin/sub/AST-372/AST-486-consult-uses-tracker-only-no-database-imports`** (product + plan already on publish ref).

### What's solid

- **`consult.py`:** **`src.data.database`** import removed; **`render_verdict`**, cover-letter refresh paths, **`list_timesheets`**, and batch **`append_agent_response`** all call **`tracker`** — matches AST-486 AC and parent AST-372 intent.
- **`tracker.py`:** One-line **`get_company`**, **`append_agent_response`**, **`list_timesheets`** delegates next to existing facades; no duplicate semantics (§1.3 DRY).
- **`agent.py`:** Cycle-breaking lazy imports kept; **`get_job` / `get_company`** in **`run_resume_artifact_chain_for_job`** and **`run_cover_letter_artifact_chain_for_job`** routed through **`tracker`** only — matches plan Stage 3 without re-homing unrelated **`database`** imports.
- **Verification:** **`git grep`** shows no **`from src.data.database import …get_job`** under **`src/core`** on reviewed tip; component tests monkeypatch **`consult_mod.tracker.*`**; **`TestTrackerFacades.test_ast486_consult_layer_facades_delegate_to_database`** documents the delegate contract; **`ASTRAL_TEST_BIBLE`** cites that test.

### Issues

| Severity | Where | Detail |
|:--|:--|:--|
| advisory | Plan introduction | Fixed 2026-05-24: space after comma before “which”. |
| advisory | Header “Feature ref” | Fixed 2026-05-24: intro names parent **`ftr/AST-372-…`** and child **`sub/AST-372/AST-486-…`**. |

### Recommended actions

- Nothing blocking **`resolve-astral`**. Optional markdown cleanup of the advisory items if someone edits this plan again.

---

## Resolution

**2026-05-24 (Hedy, `resolve-astral`):** Radia **`review-astral`** recorded no blocking product fixes; publish ref already included product, Betty’s **`test(AST-486):`** / bible alignment, and **`docs(AST-486): Radia review`** (`49330cbf` lineage).

- Addressed advisory: comma spacing before “which”; header lists parent **`ftr/AST-372-…`** and authoritative **`origin/sub/…`** child; Issues table reflects closure above.
---

## Revisions

*(None — initial plan.)*
