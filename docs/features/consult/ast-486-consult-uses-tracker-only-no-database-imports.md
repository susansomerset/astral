<!-- linear-archive: AST-486 archived 2026-06-15 -->

## Linear archive (AST-486)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-486/consult-uses-tracker-only-no-database-imports-consult-fetch-job-by-id  
**Status at archive:** Done  
**Project:** Astral Consult  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-372 — consult: fetch job by ID through tracker, not database  
**Blocked by / blocks / related:** parent: AST-372

### Description

## What this implements

Remove direct `src.data.database` usage from `src/core/consult.py`. All job/company/timesheet reads go through `src/core/tracker.py` (existing thin wrappers or new ones). Susan (2026-05-25): with batch-scoped job state, consult should not call the database layer for any reason.

## Acceptance criteria

1. `consult.py` has **no** `from src.data.database import …` (or other direct database imports).
2. Job-by-id paths use `tracker.get_job` (or pass batch `job` dict where already in hand — optional dedupe of redundant fetches).
3. Other consult DB touches (`get_company`, timesheets, `append_agent_response`, etc.) use tracker delegates.
4. Quick grep: no other `src/core/*` modules importing `get_job` from database for trivial fixes in same pass.

## Boundaries

* Does **not** implement `analysis_upshot` or AST-478 feature work (already on `origin/dev` from sibling epic).
* Does **not** change `builder.py` (already uses `tracker.get_job`).
* Does **not** redesign batch router contracts beyond import/layer hygiene.

## Notes for planning

* `tracker.get_job` already exists (delegates to `database.get_job`).
* Prior thread: `render_verdict` may still need a job load for id-only callers; batch paths may thread `job` to avoid double fetch.
* Merge `origin/dev` before build — AST-478 recently landed consult state work.

## Git branch (authoritative)

Parent `ftr/AST-372-consult-fetch-job-by-id-through-tracker-not-database`, child `sub/AST-372/<child-segment>` at dispatch.

### Comments

#### radia — 2026-05-25T04:44:44.642Z
**Radia — `review-astral`** (`origin/dev…origin/sub/AST-372/AST-486-consult-uses-tracker-only-no-database-imports`; product tip **`d904911`**)

**Plan fidelity / rules**
- Matches AST-486 + combined plan: **`consult`** has no **`database`** import; **`tracker`** thin wrappers for **`get_company`**, **`append_agent_response`**, **`list_timesheets`**; **`agent`** artifact chains resolve job/company via **`tracker`** in the lazy-import blocks only (other **`database`** imports untouched per documented scope).

**Rubric (happy path)**  
- **B1/B2:** No new nested lazy imports without justification — **`consult`** imports **`tracker`** at top; **`agent`** retains explicit cycle-break (`consult` imported inside functions) and swaps to **`tracker`** for the **`get_job`/`get_company`** pair only.  
- **H\* / batch:** **`_run_batch_consult`** still **`try`/`finally`** clears via existing pattern; **`append_agent_response`** indirection does not widen swallow (pre-existing **`except Exception`** + debug log unchanged in diff).

**Advisory**
- Combined plan typo **`**,which`** near intro; header “Feature ref **`ftr/AST-486`**” vs actual **`sub/AST-372/…`** naming — optional doc polish.

**Doc commit:** [plan + §Review (`49330cbf`)](https://github.com/susansomerset/astral/blob/49330cbf/docs/features/consult/ast-486-consult-uses-tracker-only-no-database-imports.md)

#### betty — 2026-05-25T04:41:06.034Z
[check-linear]

**Tests updated for `[qa-handoff]`** (`qa-astral` §B return)

- Verified `origin/sub/AST-372/AST-486-consult-uses-tracker-only-no-database-imports` tip **`d904911d`** — commit **`test(AST-486): retarget consult component mocks to tracker facades`** aligns `tests/component/core/test_consult.py` mocks with **`tracker.get_job`** / **`tracker.get_company`** / **`tracker.list_timesheets`** / **`tracker.append_agent_response`** (see thread from Hedy at **`86e3ce9b`** onward).
- **`dev-betty`** merged **`origin/sub/…`** and re-ran the ticket manifest (green):
  ```bash
  pytest tests/component/core/test_consult.py \
    tests/component/core/test_tracker.py::TestTrackerFacades::test_ast486_consult_layer_facades_delegate_to_database \
    -q --tb=short
  ```
  → **121 passed** on the integration branch after merge.
- **Publish ref:** **`origin/sub/AST-372/AST-486-consult-uses-tracker-only-no-database-imports` @ `d904911d`** — nothing further to push from this pass; redundant local publish attempt aborted (remote already contained the façade retarget tip).
- Reassigned to **@Hedy** for **`test-astral` §6** re-run. Status unchanged: **Tests Ready**.

#### betty — 2026-05-25T04:40:42.103Z
[check-linear]

- Cleared `[qa-handoff]` for AST-486: updated `tests/component/core/test_consult.py` so monkeypatches target `consult_mod.tracker` (`get_job`, `get_company`, `list_timesheets` replacing `_db_list_timesheets`, `append_agent_response`) instead of removed `consult` module bindings.
- **Publish:** `origin/sub/AST-372/AST-486-consult-uses-tracker-only-no-database-imports` @ **`d904911d`** (`test(AST-486): retarget consult component mocks to tracker facades`).
- **Manifest re-run (on publish tip + merged `origin/dev` line):**  
  `pytest tests/component/core/test_consult.py tests/component/core/test_tracker.py::TestTrackerFacades::test_ast486_consult_layer_facades_delegate_to_database -q --tb=short` → **94 passed** on the shorter publish `test_consult` module count (fixtures unchanged vs prior tip aside from patch targets).
- Reassigned **Hedy** for **`test-astral`**; status remains **Tests Ready**.

#### hedy — 2026-05-25T04:37:10.184Z
[qa-handoff]

@Betty White — **`test-astral` §6 re-run** on `dev-hedy` after `git fetch origin`, **`git merge origin/dev`**, **`git merge origin/sub/AST-372/AST-486-consult-uses-tracker-only-no-database-imports`** (remote tip **`86e3ce9b`**). Same manifest command:

```bash
pytest tests/component/core/test_consult.py \
  tests/component/core/test_tracker.py::TestTrackerFacades::test_ast486_consult_layer_facades_delegate_to_database -q --tb=short
```

**Result:** **25 failed, 69 passed** — still **`AttributeError`** from monkeypatch targets that no longer exist on **`consult_mod`** (`get_job`, `_db_list_timesheets`, `append_agent_response`). Matches the earlier handoff; product path is **`tracker.*`** delegates per §7.13d.

**Ask:** Patch **`test_consult.py`** patches to **`src.core.tracker`** (same ask as prior thread); republish to **`origin/sub/AST-372/AST-486-consult-uses-tracker-only-no-database-imports`**, cite new tip + manifest, reassign **`Hedy`** for **`Tests Passed`**. I am not editing **`tests/`** (`test-tree ban`).

#### hedy — 2026-05-25T04:36:06.019Z
[qa-handoff]

Betty (`@Betty White`) — manifest run is red for **test harness mismatch**, not a product regression on the merged line.

**Command:**
```bash
pytest tests/component/core/test_consult.py \
  tests/component/core/test_tracker.py::TestTrackerFacades::test_ast486_consult_layer_facades_delegate_to_database -q --tb=short
```

**Result:** 25 failed, 69 passed.

**Cause:** AST-486 product routes job/company/timesheets/agent-response through **`src.core.tracker`** (`tracker.get_job`, `tracker.get_company`, `tracker.list_timesheets`, `tracker.append_agent_response`). `src/core/consult.py` no longer exposes module-level **`get_job`**, **`_db_list_timesheets`**, or **`append_agent_response`**.

**`test_consult.py` still monkeypatches** `consult_mod.get_job`, `consult_mod._db_list_timesheets`, and `consult_mod.append_agent_response` → `AttributeError` on every affected case (e.g. `TestTransitionHelpers.test_list_timesheets_delegates`, all `TestRenderVerdict::*`, cover-letter batch tests, `TestRunBatchConsultBranches.test_handles_missing_fabricated_and_bad_grades`).

**Ask:** Update those tests (and bible §7.13d wording if needed) so patches target **`tracker`** (import `src.core.tracker as tracker_mod` / patch `tracker.get_job`, etc.), aligned with §7.13d façade map. **`test_tracker.py::test_ast486_consult_layer_facades_delegate_to_database`** path is green.

**Refs:** Integration `dev-hedy` merged `origin/dev` + `origin/sub/AST-372/AST-486-consult-uses-tracker-only-no-database-imports`; remote tip **`86e3ce9b`** matches your publish note after merge onto HEAD.

#### betty — 2026-05-25T04:35:04.409Z
1. **`docs/ASTRAL_TEST_BIBLE.md`** §7.13d — AST-486 note maps **`consult.py`** layering to **`TestTrackerFacades.test_ast486_consult_layer_facades_delegate_to_database`** (`tracker` → `database` for **`get_company`**, **`append_agent_response`**, **`list_timesheets`**).
2. **`tests/component/core/test_tracker.py`** — run **`TestTrackerFacades::test_ast486_consult_layer_facades_delegate_to_database`** (new).
3. **`tests/component/core/test_consult.py`** — full module (consult / batch / tracker wiring; aligns with **`src/core/consult.py`** map in bible §7.13d).

**Commands (ticket scope):**
```bash
pytest tests/component/core/test_consult.py \
  tests/component/core/test_tracker.py::TestTrackerFacades::test_ast486_consult_layer_facades_delegate_to_database -q --tb=short
```

**Publish tip:** `origin/sub/AST-372/AST-486-consult-uses-tracker-only-no-database-imports` @ **`86e3ce9b`** (includes **`test(AST-486): bible + tracker facade test for consult layering`**).

#### hedy — 2026-05-25T04:24:00.376Z
Plan doc (`docs/features/consult/ast-486-consult-uses-tracker-only-no-database-imports.md`):  
https://github.com/susansomerset/astral/blob/sub/AST-372/AST-486-consult-uses-tracker-only-no-database-imports/docs/features/consult/ast-486-consult-uses-tracker-only-no-database-imports.md  

*(Publish ref matches dispatch: `origin/sub/AST-372/AST-486-consult-uses-tracker-only-no-database-imports`; board convention also cites `ftr/AST-486` for naming.)*

**Self-assessment**

- **Scope — Single-Component:** Tracker adds three façades mirroring existing `list_jobs` style; consult and two `agent.py` artifact chain helpers reroute reads/writes—no dispatcher or UI churn beyond unchanged `consult.list_timesheets` indirection—because delegations are mechanical pass-through with no new business rules.

- **Conf — high:** Matches established `tracker.get_job` / UI-facade pattern and maps 1:1 to current `database` signatures callers already relied on (`get_company`, `append_agent_response`, `list_timesheets` kwargs).

- **Risk — Medium:** Mis-wiring **`get_job`/`get_company`** or **`append_agent_response`** affects **`render_verdict`**, batch consult **`agent_responses`**, resume/cover-letter chains; failures would surface as missing jobs/companies or missing response refs—not silent data corruption—but the blast radius across consult is real.

Published with commit `docs(AST-486): plan — …` on the sub branch (`91a81d08`). — Hedy

---

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
