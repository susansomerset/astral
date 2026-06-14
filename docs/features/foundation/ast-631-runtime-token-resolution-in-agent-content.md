# AST-631 — Runtime token resolution in agent content (Support tokens in Agent prompts)

- **Linear (this ticket):** [AST-631](https://linear.app/astralcareermatch/issue/AST-631/runtime-token-resolution-in-agent-content-support-tokens-in-agent)
- **Parent:** [AST-574](https://linear.app/astralcareermatch/issue/AST-574/support-tokens-in-agent-prompts)
- **Publish ref:** `origin/sub/AST-574/AST-631-runtime-token-resolution-in-agent-content`
- **Blocks:** [AST-632](https://linear.app/astralcareermatch/issue/AST-632/manage-agents-token-autocomplete-and-preview-support-tokens-in-agent) (Katherine — Manage Agents UI only; out of scope here)

## Summary

Agent `content` already resolves candidate/config/output-type/job tokens when it is the **direct** system block (`system_prompt` empty). When a task's `system_prompt` is `{$SELECTED_AGENT}`, `chain_context_selected_agent` injects **raw** `agent.content` into `SELECTED_AGENT`, so tokens like `{$FIRST_NAME}` survive into the assembled system text. This ticket resolves agent body tokens **before** `SELECTED_AGENT` is populated, using the same `resolve_tokens` registry and call context as task prompt segments — across `do_task`, chain hops, `preview_prompt`, and admin paths that already resolve task prompts.

## Root cause (current code)

1. `_chain_context` in `src/core/agent.py` calls `chain_context_selected_agent(agent_row.get("content"))` with **unresolved** text.
2. `resolved_task_system` picks `system_prompt` when non-empty; for `{$SELECTED_AGENT}` it runs `resolve_tokens` once on the outer template, substituting the raw agent body from `chain_context`.
3. Direct-system path (`system_prompt` empty) runs `resolve_tokens` on agent `content` itself — tokens resolve correctly today.

AST-304 intentionally shipped raw `SELECTED_AGENT` injection; AST-631 reverses that for **non-chain** tokens inside agent bodies while keeping chain tokens (`{$CALLER_*}`) task-prompt-only per parent boundaries.

## Out of scope (this ticket)

| Item | Owner |
|------|--------|
| New tokens or `TOKEN_SOURCES` entries | — |
| Chain tokens in agent rows (`{$CALLER_*}`, `{$SELECTED_AGENT}` in agent `content`) | Not expected; no picker |
| Nested agent indirection | — |
| Manage Agents autocomplete / candidate-scoped preview UI | **AST-632** (Katherine) |
| Changes to task-only prompt fields beyond agent-body resolution | — |
| Betty test manifest / `tests/` edits | Betty (`qa-child`) |

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/agent.py` | `resolved_agent_content` helper; expand `_chain_context` signature; reorder `do_task` so `job_context` is available before `_chain_context`; update `preview_prompt` / `simulated_chain_context_for_preview` call sites | core |
| `src/ui/api/api_admin.py` | Replace direct `chain_context_selected_agent(agent.get("content"))` with agent-module chain builder; use `resolved_task_system` / shared `_chain_context` for system token counts | ui |

No changes to `src/utils/config.py` (`chain_context_selected_agent` stays a thin dict builder; resolution lives in `agent.py`).

## Stage 1: Resolve agent body before `SELECTED_AGENT` injection

**Done when:** `resolved_agent_content` exists; `_chain_context` puts **token-resolved** agent text into `SELECTED_AGENT`; all production and preview assembly paths that build `_cc` via `_chain_context` use the new signature; agent rows with no merge tokens behave identically; agent rows with `{$FIRST_NAME}` (etc.) resolve on both direct-system and `{$SELECTED_AGENT}` paths.

1. In `src/core/agent.py`, immediately **above** `_chain_context` (~line 343), add:

```python
def resolved_agent_content(
    agent_row: Dict[str, Any],
    candidate_data: dict,
    task_key: str,
    job_context: Optional[Dict[str, str]] = None,
    *,
    chain_entry: bool = False,
    parent_task_key: Optional[str] = None,
    parent_caller_summary: Optional[Dict[str, str]] = None,
) -> str:
    """Resolve non-chain tokens in agent.content before SELECTED_AGENT injection (AST-631)."""
    return resolve_tokens(
        agent_row.get("content") or "",
        candidate_data,
        task_key,
        None,  # chain tokens not expected in agent rows
        job_context,
        chain_entry=chain_entry,
        parent_task_key=parent_task_key,
        parent_caller_summary=parent_caller_summary,
    )
```

2. Replace `_chain_context` with:

```python
def _chain_context(
    agent_row: Dict[str, Any],
    candidate_data: dict,
    task_key: str,
    job_context: Optional[Dict[str, str]] = None,
    extra: Optional[Dict[str, str]] = None,
    *,
    chain_entry: bool = False,
    parent_task_key: Optional[str] = None,
    parent_caller_summary: Optional[Dict[str, str]] = None,
) -> Dict[str, str]:
    """Chain/runtime tokens for resolve_tokens (AST-304). SELECTED_AGENT = resolved agent body (AST-631)."""
    resolved_body = resolved_agent_content(
        agent_row,
        candidate_data,
        task_key,
        job_context,
        chain_entry=chain_entry,
        parent_task_key=parent_task_key,
        parent_caller_summary=parent_caller_summary,
    )
    base = chain_context_selected_agent(resolved_body)
    if not extra:
        return base
    out = dict(base)
    for k, v in extra.items():
        if not k.startswith("_"):
            out[k] = v
    return out
```

3. In `do_task` (~line 1293), **move** `_jc = _job_context_for_call(ctx, index, cd)` to **before** `_cc = _chain_context(...)` so job-scoped tokens in agent content resolve when a job is in scope. Pass hop kwargs into `_chain_context`:

```python
_cc = _chain_context(
    agent_row,
    cd,
    task_key,
    _jc,
    chain_context,
    chain_entry=chain_entry,
    parent_task_key=parent_task_key or None,
    parent_caller_summary=parent_caller_summary or None,
)
```

Remove the duplicate `_jc` assignment at the old line (~1307) — only one `_jc` assignment remains, before `_cc`.

4. In `simulated_chain_context_for_preview` (~2080), replace `_cc = _chain_context(agent_row)` with:

```python
_cc = _chain_context(agent_row, cd, parent_task_key, job_context)
```

5. In `preview_prompt` (~2113), replace `_cc = _chain_context(agent_row, chain_context)` with:

```python
_cc = _chain_context(
    agent_row,
    cd,
    task_key,
    job_context,
    chain_context,
)
```

6. In `src/ui/api/api_admin.py`:
   - Add `_chain_context` to the existing import from `src.core.agent` (same line as `resolved_task_system`).
   - In `_enrich_tasks` (~242), replace:

     ```python
     _cc = chain_context_selected_agent(agent.get("content")) if agent else None
     ```

     with:

     ```python
     _cc = _chain_context(agent, cd, task_key, None) if agent else None
     ```

     (List view has no job entity id — job tokens in agent content stay unresolved here, same as cache blocks without `astral_job_id`; acceptable for token **estimates**.)

   - In `_resolve_adhoc` (~886), replace:

     ```python
     _cc = chain_context_selected_agent(agent.get("content"))
     ```

     with:

     ```python
     _cc = _chain_context(agent, cd, task_key, jc)
     ```

     and replace the adhoc `system` line:

     ```python
     "system": resolve_tokens(agent.get("content") or "", cd, task_key, _cc, jc),
     ```

     with:

     ```python
     "system": resolved_task_system(agent, agent_task_row or {}, cd, task_key, _cc, jc),
     ```

     when `agent_task_row` is `{}` for pure adhoc, `resolved_task_system` still falls back to agent `content` (empty `system_prompt`) — same as today but through one code path.

     ⚠️ **Decision:** For adhoc when `task_key == "adhoc"` and `agent_task_row` is `None`, pass `agent_task_row = {"system_prompt": ""}` (empty dict with no system_prompt) so `resolved_task_system` uses agent content without requiring a DB row.

7. Remove unused `chain_context_selected_agent` import from `api_admin.py` if no remaining references.

⚠️ **Decision:** Agent-body resolution uses `chain_context=None` inside `resolved_agent_content` — agent templates must not contain chain tokens per AST-574 boundaries; avoids recursive `{$SELECTED_AGENT}` inside agent body.

⚠️ **Decision:** No second pass over assembled system text — fixing `_chain_context` is sufficient because direct-system path already resolves via `resolved_task_system` → `resolve_tokens(base, ..., _cc)` where `base` is agent content and `_cc["SELECTED_AGENT"]` is the same resolved body (unused for that path).

## Stage 2: Betty verification targets (manifest — not implemented in this ticket)

**Done when:** Betty's `qa-child` manifest covers the four parent AC items; engineer does not edit `tests/`.

Betty should add or extend component tests (suggested locations):

| AC | Suggested coverage |
|----|-------------------|
| AC1 — direct system block | `resolved_task_system` / `preview_prompt` with empty `system_prompt`, agent `content` containing `{$FIRST_NAME}` |
| AC2 — `{$SELECTED_AGENT}` path | Same agent body, `system_prompt` = `{$SELECTED_AGENT}`; assert no literal `{$FIRST_NAME}` in output |
| AC3 — Manage Tasks preview | `preview_task_prompt` / admin preview route mirrors production for `{$SELECTED_AGENT}` task |
| AC6 — no tokens unchanged | Agent with plain text; before/after strings equal on both paths |

Update `TestChainContext.test_merges_extra_chain_tokens` in `tests/component/core/test_agent.py` for new `_chain_context` signature (`cd`, `task_key` positional args).

## Self-Assessment

**Scope — Single-Component:** Touches `_chain_context` / `resolved_agent_content` in `agent.py` and two admin call sites in `api_admin.py` — no config registry, DB, or frontend changes.

**Conf — high:** Bug and fix are localized; reuses existing `resolve_tokens` and AST-304 chain wiring; AST-304 raw-SELECTED_AGENT decision is explicitly superseded for non-chain tokens only.

**Risk — Medium:** Every LLM call uses assembled prompts; mis-resolution would affect all tasks using `{$SELECTED_AGENT}` or agent-body tokens, but behavior for token-free agent content must remain byte-identical and chain hop semantics are unchanged.

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Status |
|------|--------|
| §1.3 DRY | Centralizes agent-body resolution in `resolved_agent_content`; admin reuses `_chain_context` instead of duplicating `chain_context_selected_agent` |
| §2.1 config | No new config keys; `TOKEN_SOURCES` unchanged |
| §3.3 imports | `api_admin` → `core.agent` (existing pattern for `resolved_task_system`) |
| §3.5 naming | `resolved_agent_content` parallels `resolved_task_system` |

No conflicts requiring `conf-!!-NONE`.

## Review (build-child)

**Built:** `origin/sub/AST-574/AST-631-runtime-token-resolution-in-agent-content` @ `25359fc1`

| Commit | Summary |
|--------|---------|
| `25359fc1` | Stage 1: `resolved_agent_content`, `_chain_context` signature, `do_task` / preview paths, admin `_enrich_tasks` + `_resolve_adhoc` |

**Verification:** `python3 -m py_compile src/core/agent.py src/ui/api/api_admin.py`

---

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-574/AST-631-runtime-token-resolution-in-agent-content` @ `b8345d3f`

### What's solid

| Area | Notes |
|------|-------|
| **Plan fidelity** | `resolved_agent_content`, expanded `_chain_context`, `do_task` `_jc` before `_cc` with hop kwargs, `preview_prompt` / `simulated_chain_context_for_preview`, admin `_enrich_tasks` + `_resolve_adhoc` match Stage 1 spec. |
| **AC coverage (Betty)** | `TestAst631AgentContentTokens` (direct + `{$SELECTED_AGENT}` + plain body + `preview_prompt`); `TestPreviewTaskPrompt::test_preview_resolves_agent_body_when_system_is_selected_agent`; bible §7.13zzm manifest. |
| **Rules §1.3 / §3.3** | DRY: single resolution helper; admin reuses `_chain_context` instead of raw `chain_context_selected_agent`. `api_admin` → `core.agent` matches existing `resolved_task_system` import pattern. No layer bends, silent failures, or debug-contract drift in touched product files. |
| **Boundaries (§5d)** | No AST-632 UI, no registry/DB changes, no chain tokens in agent rows. Product diff limited to `agent.py` + `api_admin.py`. |

### Issues

| Severity | Location | Issue |
|----------|----------|-------|
| — | — | No **fix-now** or **discuss** items on product code. |

### Advisory

| Location | Note |
|----------|------|
| `agent.py` direct-system path | `_chain_context` resolves agent body for `SELECTED_AGENT` while `resolved_task_system` (empty `system_prompt`) resolves the same `content` again — redundant but idempotent; plan documents this as acceptable. |
| `api_admin._enrich_tasks` | `job_context=None` — job-scoped tokens in agent body stay literal in list token **estimates** only; production `do_task` / adhoc preview pass `_jc`. Plan decision stands. |
| Publish ref test merge | `merge-tests` commit includes Betty bible + large `test_agent.py` churn (AST-603 rubric harness alignment). Product scope clean; test tree is Betty-owned. |

### Recommended actions (resolve-child)

| Action | Owner |
|--------|-------|
| No product code changes required — proceed to **User Testing** after optional read of advisory | Ada |
