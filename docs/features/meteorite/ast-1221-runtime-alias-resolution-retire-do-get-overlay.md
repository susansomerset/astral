# AST-1221 — Runtime alias resolution + retire Do/Get overlay

**Linear:** [AST-1221](https://linear.app/astralcareermatch/issue/AST-1221/runtime-alias-resolution-retire-doget-overlay-task-config-aliases-via)
**Parent:** [AST-1184](https://linear.app/astralcareermatch/issue/AST-1184/task-config-aliases-via-master-task-key) — Task config aliases via master_task_key
**Publish ref:** `origin/sub/AST-1184/AST-1221-runtime-alias-resolution-retire-do-get-overlay`

After **AST-1220**: honor `master_task_key` → master resolution wherever prompts / shared agent_task content are loaded; run alias dispatch keys (`meteorite_grade_do` / `meteorite_grade_get`) with **alias-owned** `TASK_CONFIG` orchestration (pass/fail/error); remove `METEORITE_GDL_OUTCOME_BY_TASK` (symbol + consult overlay read path). Does **not** author the config contract (**AST-1220**), seed/retarget meteorite dispatch or `agent_task` rows (**AST-1222**), or own UI hardcode audit (**AST-1185**).

**Depends on AST-1220 (User Testing):** `is_task_alias` / `resolve_task_key_for_content`, alias `TASK_CONFIG` entries, empty overlay dict. Build expects those on the epic tree via `sync-child` merging `origin/ftr/AST-1184-…` once Chuckles lands AST-1220. If helpers are missing at Stage 1 start → stop, comment on parent, wait — do not re-implement the contract.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/agent.py` | Resolve prompt/`agent_task` fetch via `resolve_task_key_for_content`; keep caller `task_key` as identity; Style D detail when alias resolves; `_is_strict_encoded_batch_consult` for both strict-envelope gate sites | core |
| `src/core/consult.py` | Retire overlay read; alias-aware scored Do/Get dispatch routing; header lookup via master resolve | core |
| `src/core/dispatcher.py` | Add alias keys to `_CHUNK_EXHAUST_CONSULT_JOB_KEYS` | core |
| `src/utils/config.py` | Delete `METEORITE_GDL_OUTCOME_BY_TASK` symbol + its value∈`JOB_STATES` assert loop | utils |

**No changes expected:** `data/admin/agent_task.json`, `METEORITE_DISPATCH_TASKS` / `SEED_CONFIG` meteorite SQL (still `grade_do` / `grade_get` until **AST-1222**), frontend, `tests/` / bible (Betty after Code Complete).

## Stage 1: Agent — prompt content resolve + debug detail

**Done when:** `_resolve_task_prompts` loads `agent_task` / `agent` rows for `resolve_task_key_for_content(task_key)` while `do_task` / preview still key storage, context, and `TASK_CONFIG` orchestration off the caller `task_key`; when `debug=True` and the key is an alias, Style D detail shows alias → master; `meteorite_grade_do` / `meteorite_grade_get` participate in the strict encoded-batch envelope gate; `python3 -m py_compile src/core/agent.py` succeeds (repo venv: `~/astral/.venv/bin/python`).

1. In `src/core/agent.py`, extend the existing config import (near other `TASK_CONFIG` helpers) to include `resolve_task_key_for_content` and `is_task_alias`.

2. Replace `_resolve_task_prompts` so content lookup uses the resolved master; keep the parameter name `task_key` as the **caller identity** (alias or master) for error messages that name the requested key:

```python
def _resolve_task_prompts(task_key: str):
    """Fetch and validate agent_task + agent rows for prompt/content lookup.

    Alias keys resolve to master_task_key for DB rows (AST-1221); caller identity
    stays the original task_key at do_task / preview call sites.
    """
    content_key = resolve_task_key_for_content(task_key)
    agent_task_row = get_agent_task(content_key)
    if not agent_task_row:
        raise ValueError(
            f"No agent_task row for '{content_key}'"
            + (f" (alias '{task_key}')" if content_key != (task_key or "").strip() else "")
            + ". Run sync_agent_tasks or configure via Manage Tasks."
        )
    agent_id = (agent_task_row.get("agent_id") or "").strip()
    if not agent_id:
        raise ValueError(
            f"agent_task '{content_key}' has no agent_id assigned. Configure via Manage Tasks."
        )
    agent_row = get_agent(agent_id)
    if not agent_row:
        raise ValueError(
            f"Agent '{agent_id}' referenced by task '{content_key}' not found."
        )
    return agent_row, agent_task_row
```

⚠️ **Decision — content resolve at `_resolve_task_prompts` only (prompt fetch):** Parent requires master's prompts/content with no alias prompt override; alias remains the identity operators see. `do_task` continues `TASK_CONFIG.get(task_key)` for schema / scored flags / `requires_candidate_key` (alias entries already carry those per **AST-1220** Radia advisory — do **not** invent a field-merge from master). `preview_prompt` / `simulated_chain_context_for_preview` inherit resolve automatically via `_resolve_task_prompts`.

⚠️ **Decision — `_parent_hop_task_key_for_child` / `_current_agent_task_run_next` stay on caller identity:** These also call `get_agent_task`, but they are **not** prompt-content lookups — they read `run_next` / chain-parent identity (`astral.dispatch.run-next-is-chain-authority`). Leave them keyed on the raw `task_key`. Safe today (aliases have no `agent_task` row until **AST-1222**) and safe after **AST-1222** seeds grouping-only alias rows with no `run_next` (Do/Get have no chain; `get_agent_task(alias)` returning a grouping row with empty `run_next` yields `""`, same as today). Do **not** resolve these to master — that would silently attribute the master's `run_next` to the alias. Document only; no code change at those two sites on this ticket.

3. In `do_task`, immediately after the successful `TASK_CONFIG` lookup (and before `_resolve_task_prompts`), when `debug` is True and `is_task_alias(task_key)`:

```python
    if debug and is_task_alias(task_key):
        logger.set_debug_flag(True)
        master = resolve_task_key_for_content(task_key)
        logger.debug_index(
            func=f"do_task({task_key})",
            index=1,
            total=1,
            identifier=index or task_key,
            outcome="alias_resolve",
        )
        logger.debug_detail(
            f"alias={task_key} content_master={master} "
            f"orchestration=TASK_CONFIG[{task_key}] prompts=agent_task[{master}]"
        )
```

⚠️ **Decision — Style D only when `debug=True`:** Matches `astral.standards.debug-contract-gated`. No new ungated INFO noise. Index header uses the **alias** identity; detail names the master.

4. Strict encoded-batch gate — membership is tested in **two** places today (`do_task` ~line 2468 sets `strict_batch = task_key in _STRICT_ENCODED_BATCH_CONSULT_KEYS`, then only calls `_strict_encoded_batch_consult_envelope_err` when `strict_batch`). Resolving only inside the helper leaves aliases with `strict_batch=False` (helper never called; no `agent_performance` back-fill). Introduce one membership helper and use it in both places:

```python
def _is_strict_encoded_batch_consult(task_key: str) -> bool:
    """True when task_key (or its content master) is in the strict encoded-batch set."""
    return resolve_task_key_for_content(task_key) in _STRICT_ENCODED_BATCH_CONSULT_KEYS


def _strict_encoded_batch_consult_envelope_err(task_key: str, parsed: Any) -> Optional[str]:
    """Return error detail if encoded-batch consult response bypasses envelope rules; otherwise None."""
    if not _is_strict_encoded_batch_consult(task_key) or parsed is None:
        return None
    # ... remainder unchanged (same checks as today) ...
```

In `do_task` (~line 2468), replace the direct frozenset membership with the helper:

```python
    strict_batch = _is_strict_encoded_batch_consult(task_key)
```

Leave the subsequent `if strict_batch … agent_performance` back-fill and both `envelope_err = _strict_encoded_batch_consult_envelope_err(...)` calls unchanged — they already key off `strict_batch`.

⚠️ **Decision — one membership helper, both call sites:** `astral.standards.dry-and-focused-functions`. Do **not** add `meteorite_grade_do` / `meteorite_grade_get` literals to `_STRICT_ENCODED_BATCH_CONSULT_KEYS` — resolve covers them. Leave the frozenset body as masters + existing twins (`meteorite_like`, etc.).

5. Verify:

```bash
~/astral/.venv/bin/python -c "
from src.utils.config import resolve_task_key_for_content, is_task_alias
from src.core.agent import _is_strict_encoded_batch_consult
assert is_task_alias('meteorite_grade_do')
assert resolve_task_key_for_content('meteorite_grade_do') == 'grade_do'
assert resolve_task_key_for_content('grade_do') == 'grade_do'
assert _is_strict_encoded_batch_consult('meteorite_grade_do') is True
assert _is_strict_encoded_batch_consult('meteorite_grade_get') is True
assert _is_strict_encoded_batch_consult('grade_do') is True
assert _is_strict_encoded_batch_consult('prefilter_company') is False
"
~/astral/.venv/bin/python -m py_compile src/core/agent.py
```

**Ritual:** `code(AST-1221): agent prompt resolve via master_task_key`

## Stage 2: Consult — retire overlay + alias Do/Get dispatch routing

**Done when:** `METEORITE_GDL_OUTCOME_BY_TASK` is not imported or read in consult; `_consult_orchestration_for_entity` returns the alias/master `TASK_CONFIG` row with no entity-state overlay; `run_consult_task` / `_consult_scored_dispatch_batch_encoded` accept `meteorite_grade_do` / `meteorite_grade_get` and use alias orchestration + header via master resolve; classic `grade_do` / `grade_get` paths unchanged.

1. In `src/core/consult.py` imports from `src.utils.config`, **remove** `METEORITE_GDL_OUTCOME_BY_TASK`. Add `resolve_task_key_for_content` and `is_task_alias`.

2. Replace `_consult_orchestration_for_entity` (keep the name and `entity_state` parameter so call sites stay stable):

```python
def _consult_orchestration_for_entity(task_key: str, entity_state: Optional[str] = None) -> Dict[str, Any]:
    """TASK_CONFIG orchestration for dispatch/catalog task_key.

    AST-1221: meteorite Do/Get outcomes live on alias TASK_CONFIG entries
    (meteorite_grade_do / meteorite_grade_get). No METEORITE_GDL_OUTCOME_BY_TASK overlay.
    entity_state retained for call-site compatibility; unused.
    """
    return dict(_consult_orchestration(task_key))
```

Keep `_entity_state_is_meteorite` — still used by `_format_analysis_phase_text` (Analysis-JD meteorite override), unrelated to the Do/Get overlay.

3. Update the `evaluate_meteorite_batch` docstring to drop the “no METEORITE_GDL_OUTCOME_BY_TASK overlay needed” phrasing — say standalone twin with own `TASK_CONFIG` pass/fail/error (same pattern as `meteorite_like_batch` / alias Do/Get).

4. In `_consult_scored_dispatch_batch_encoded`, replace the header lookup:

```python
    hdr = _GRADE_DISPATCH_TO_HEADER.get(dispatch_task_key)
    if hdr is None:
        hdr = _GRADE_DISPATCH_TO_HEADER[resolve_task_key_for_content(dispatch_task_key)]
```

⚠️ **Decision — do not add alias keys to `_GRADE_DISPATCH_TO_HEADER`:** Field-driven via `resolve_task_key_for_content` → existing master entries (`grade_do`→`DO`, `grade_get`→`GET`). Avoids a parallel meteorite-only header map (`astral.standards.no-hardcoded-sets`). Leave `meteorite_like` in the map (twin, not an alias).

5. In `run_consult_task`, expand the scored grade branch so alias Do/Get keys route like masters. Replace the current `elif task_key in ("grade_do", "grade_get", "grade_like", "meteorite_like"):` block with:

```python
    elif (
        task_key in ("grade_do", "grade_get", "grade_like", "meteorite_like")
        or (
            is_task_alias(task_key)
            and resolve_task_key_for_content(task_key) in ("grade_do", "grade_get")
        )
    ):
        if len(entities) == 1:
            aid = entities[0]["astral_job_id"]
            orch = _consult_orchestration_for_entity(task_key, entities[0].get("state"))
            rv = await render_verdict(task_key, aid, ctx=ctx, debug=debug)
            if rv.get("success"):
                passed = 1 if rv.get("to_state") == orch.get("pass_state") else 0
                return {"total_processed": 1, "total_passed": passed, "total_failed": 1 - passed, "total_errors": 0}
            return {"total_processed": 1, "total_passed": 0, "total_failed": 0, "total_errors": 1}
        if task_key in ("grade_do", "grade_get", "grade_like", "meteorite_like"):
            _batch = {
                "grade_do": grade_do_batch,
                "grade_get": grade_get_batch,
                "grade_like": grade_like_batch,
                "meteorite_like": meteorite_like_batch,
            }[task_key]
            r = await _batch(batch_id, entities, ctx=ctx, debug=debug, batch_chunk_index=batch_chunk_index)
        else:
            # Alias Do/Get — same encoded path; dispatch_task_key is the alias identity.
            r = await _consult_scored_dispatch_batch_encoded(
                task_key, batch_id, entities, ctx=ctx, debug=debug, batch_chunk_index=batch_chunk_index,
            )
```

⚠️ **Decision — no thin `meteorite_grade_*_batch` wrappers:** Call `_consult_scored_dispatch_batch_encoded` directly for aliases (same pattern body as the thin wrappers would have). Masters keep existing wrappers. Do **not** retarget `METEORITE_DISPATCH_TASKS` here (**AST-1222**).

6. Verify:

```bash
~/astral/.venv/bin/python -c "
import ast, pathlib
src = pathlib.Path('src/core/consult.py').read_text()
assert 'METEORITE_GDL_OUTCOME_BY_TASK' not in src
from src.core.consult import _consult_orchestration_for_entity, _GRADE_DISPATCH_TO_HEADER
from src.utils.config import resolve_task_key_for_content
orch = _consult_orchestration_for_entity('meteorite_grade_do', 'METEORITE_PASSED_JD')
assert orch['pass_state'] == 'METEORITE_PASSED_DO'
assert orch['fail_state'] == 'METEORITE_FAILED_DO'
# classic Gaze unchanged
gaze = _consult_orchestration_for_entity('grade_do', 'PASSED_JD')
assert gaze['pass_state'] == 'PASSED_DO'
assert _GRADE_DISPATCH_TO_HEADER.get('meteorite_grade_do') is None
assert _GRADE_DISPATCH_TO_HEADER[resolve_task_key_for_content('meteorite_grade_do')] == 'DO'
"
~/astral/.venv/bin/python -m py_compile src/core/consult.py
```

**Ritual:** `code(AST-1221): consult retire Do/Get overlay + alias routing`

## Stage 3: Dispatcher exhaust set + delete overlay symbol

**Done when:** `_CHUNK_EXHAUST_CONSULT_JOB_KEYS` includes `meteorite_grade_do` / `meteorite_grade_get`; `METEORITE_GDL_OUTCOME_BY_TASK` is gone from `config.py` (no empty dict left); no remaining product imports of that name under `src/`; compile clean.

1. In `src/core/dispatcher.py`, add the two alias keys to `_CHUNK_EXHAUST_CONSULT_JOB_KEYS` next to `grade_do` / `grade_get`:

```python
_CHUNK_EXHAUST_CONSULT_JOB_KEYS = frozenset({
    "qualify_job_listings",
    "qualify_meteorite",
    "evaluate_jd",
    "grade_do",
    "grade_get",
    "grade_like",
    "meteorite_like",
    "meteorite_grade_do",
    "meteorite_grade_get",
})
```

⚠️ **Decision — explicit frozenset membership (not resolve-at-runtime):** Matches how `meteorite_like` and Ada’s `_DISPATCH_BATCH_CALL_MODE_ONE` list alias keys. Exhaust eligibility is a closed dispatch set, not prompt content.

2. In `src/utils/config.py`, **delete** the `METEORITE_GDL_OUTCOME_BY_TASK` assignment and the assert that iterates `METEORITE_GDL_OUTCOME_BY_TASK.values()`. Keep `assert all(e["trigger_state"] in JOB_STATES for e in METEORITE_DISPATCH_TASKS)`.

Rewrite any residual comments that still describe a live Do/Get overlay — point at alias `TASK_CONFIG` entries + **AST-1221** retirement. Leave **AST-1220** comments on the alias entries that say consult resolve is AST-1221 as historical context, or shorten to “consult uses alias TASK_CONFIG outcomes”.

3. Repo grep gate (product tree only):

```bash
rg -n 'METEORITE_GDL_OUTCOME_BY_TASK' src/ && echo 'FAIL: symbol still referenced' || echo 'ok: no src references'
~/astral/.venv/bin/python -c "from src.utils import config as c; assert not hasattr(c, 'METEORITE_GDL_OUTCOME_BY_TASK')"
~/astral/.venv/bin/python -m py_compile src/utils/config.py src/core/consult.py src/core/dispatcher.py src/core/agent.py
```

⚠️ **Decision — delete the symbol, do not leave `{}`:** Parent + **AST-1220** excluded list assign deletion / consult import removal to this ticket. Tests/bible that still import the name are Betty’s after Code Complete — engineers do not patch `tests/`.

**QA note (ftr-internal):** Until **AST-1222** retargets `METEORITE_DISPATCH_TASKS` to alias keys, live meteorite Do/Get rows still claim as `grade_do` / `grade_get` and therefore use classic Gaze `TASK_CONFIG` outcomes (overlay gone). Do not exercise meteorite Do/Get as operator-safe until **AST-1222** lands (or full ftr rollup). Classic Gaze Do/Get at `PASSED_JD` / `PASSED_DO` must keep working.

**Ritual:** `code(AST-1221): delete METEORITE_GDL_OUTCOME_BY_TASK + alias exhaust keys`

## Self-Assessment

**Scope:** Single-Component — core agent/consult/dispatcher plus deleting one utils overlay symbol; no seed/UI.

**Conf:** high — **AST-1220** helpers and alias entries are shipped; overlay call site is a single function; prompt-content resolve is one choke point (`_resolve_task_prompts`) with chain/`run_next` readers intentionally caller-keyed; strict-envelope membership is one helper used at both gate sites; alias dispatch routing mirrors `meteorite_like` / resolve patterns already in-tree.

**Risk:** Medium — removing the overlay before **AST-1222** retarget means in-flight shared-key meteorite Do/Get temporarily use Gaze outcomes (accepted epic sequencing); wrong resolve would pull prompts from the wrong `agent_task` row or mis-route alias pass/fail once aliases are dispatched.

## Code rules check

- §1.3 DRY — one prompt-content resolve choke point; one `_is_strict_encoded_batch_consult` membership test for both gate sites; no duplicated alias→master maps in core.
- §1.4 / `astral.standards.no-hardcoded-sets` — no new meteorite-only overlay; header via `resolve_task_key_for_content`; strict-envelope gate via resolve; exhaust frozenset lists domain keys (same pattern as existing twins).
- §1.5.1 / `astral.standards.debug-contract-gated` — alias resolve detail only when `debug=True`, Style D index + detail.
- §2.2 / `astral.agent.do-task-delegation` — alias invocation still goes through `do_task`; prompts from master’s `agent_task`.
- `astral.dispatch.run-next-is-chain-authority` — `_parent_hop_task_key_for_child` / `_current_agent_task_run_next` stay on caller identity (no master resolve for chain authority).
- §3.3 / `pattern.layers.import-discipline` — core imports resolve helpers from utils; no reverse imports; no UI edits.
- `astral.standards.in-scope-only` — no seed/dispatch retarget (**AST-1222**), no config contract authorship (**AST-1220**), no UI audit (**AST-1185**).
- `astral.git.engineer-test-tree-ban` — no `tests/` / bible edits on this ticket.

## Revisions

### Revision 1 — 2026-08-06

Driven by: Joan `[plan-discuss] round=1 concern` (plan-rubric.v1 REVISE @ tip `fd46f3e6`).

Changes:

- **fix-now:** Stage 1 step 4 — add `_is_strict_encoded_batch_consult` wrapping `resolve_task_key_for_content(task_key) in _STRICT_ENCODED_BATCH_CONSULT_KEYS`; use it at `do_task` ~2468 (`strict_batch = …`) and at the top of `_strict_encoded_batch_consult_envelope_err` so aliases get `agent_performance` back-fill and envelope checks (not dead code).
- **discuss:** Document that `_parent_hop_task_key_for_child` / `_current_agent_task_run_next` intentionally stay on caller identity (grouping-only alias rows, no `run_next`); stop claiming a single choke point for all `get_agent_task` reads.
- **Self-assessment / code-rules:** Conf justification and §1.3 / `run-next-is-chain-authority` notes updated to match.
