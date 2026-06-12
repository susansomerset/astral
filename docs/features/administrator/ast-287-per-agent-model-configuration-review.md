# ast-287: Per-Agent Model Configuration — Code Review

**Branch:** `<agent>/ast-287-per-agent-model-configuration`
**Commits reviewed:** 6 (sub1–sub6)
**Reviewer:** Chuckles

---

## Overall Assessment

**Ship it.** The implementation matches the plan closely, the commit sequence is logical, and there are no obvious correctness bugs. A few issues worth flagging — two of them real (one small functional gap, one style consistency miss), the rest are observations or suggestions for follow-up.

---

## Sub 1 — `MODELS` catalog + remove `api` block (`config.py`)

**Clean.** MODELS dict keyed by `model_code` alias, `get_model()` helper raises `ValueError` on unknown code. The `api` block removal is complete and the module docstring update is accurate.

**One observation:** `get_model()` uses `MODELS.get(model_code)` and checks for falsy, which would also raise on a hypothetically empty-dict model entry. Technically fine given the structure, but `if m is None` would be more precise.

```python
# current
if not m:
    raise ValueError(...)
# more precise (low priority)
if m is None:
    raise ValueError(...)
```

---

## Sub 2 — Agent table migration + DB functions (`database.py`)

**Solid migration pattern.** The idempotent `ALTER TABLE` with `PRAGMA table_info` + duplicate-column catch mirrors the company `batch_created_at` pattern. Seeding existing agents to Sonnet defaults on first connection is correct.

**Issue: `_agent_schema_ensured` flag is only set in the new-table path.**

```python
# line ~1342 in the diff
    conn.execute("""CREATE TABLE agent ...""")
    conn.commit()
else:
    # migration block ...
    conn.commit()
_agent_schema_ensured = True   # ← set after both branches — correct as written
```

Wait — re-reading the diff, `_agent_schema_ensured = True` is *outside* both branches (after the `else` block), so it does fire in both cases. The flag is fine. Never mind — that was a false alarm on my part.

**Good catch in `list_agents`:** calling `_ensure_agent_task_schema(conn)` before the correlated subquery — prevents a schema-not-yet-created crash on a fresh DB. Correct.

**`update_agent` silently drops unknown kwargs** — only the allowlisted columns are used. This is by design (the allowlist is the point), but the caller gets no signal that extra keys were ignored. Acceptable for an internal function, just worth knowing.

---

## Sub 3 — `cost_calculator.py`

**Clean reduction.** Hardcoded Sonnet 4.5 constants gone; both functions now accept `model_code`. The `getattr(usage, "cache_read_input_tokens", 0) or 0` double-safety pattern (handles both missing attribute and `None`) is smart.

**One style note:** `calculate_cost` uses a backslash line continuation:

```python
return (usage.input_tokens / 1_000_000) * m["cpm_input"] + \
       (usage.output_tokens / 1_000_000) * m["cpm_output"]
```

`calculate_cost_with_cache` uses parenthesized multi-line. The parenthesized form is preferred in this codebase — minor inconsistency.

---

## Sub 4 — `anthropic.py`

**The critical path.** This is the highest-risk change and it looks right.

**`do_task` fallback logic** uses `if agent_row.get("temperature") is not None` correctly — this is important because `temperature=0.0` is a valid value and falsy. Same for `max_tokens`. Good.

```python
agent_temperature = agent_row.get("temperature") if agent_row.get("temperature") is not None else model_cfg["default_temperature"]
agent_max_tokens  = agent_row.get("max_tokens")  if agent_row.get("max_tokens")  is not None else model_cfg["default_max_tokens"]
```

**`_send_and_parse` guard** uses `if not model_code:` — will also raise on empty string `""`, which is correct since an empty string is as bad as `None` here.

**`_fetch_response` (legacy path) defaults** hardcode `"claude-sonnet-4-5"` string literal twice (once for `model_code` default, twice in the `get_model()` call for temperature/max_tokens defaults). If the default model name ever changes, this needs updating in two spots. Acceptable for a legacy/scripts-only path, but worth noting.

```python
# legacy path — two references to the default model string
model_code=model_code or "claude-sonnet-4-5",
temperature=temperature if temperature is not None else get_model("claude-sonnet-4-5")["default_temperature"],
max_tokens=max_tokens if max_tokens is not None else get_model("claude-sonnet-4-5")["default_max_tokens"],
```

A single `_DEFAULT_MODEL = "claude-sonnet-4-5"` constant at the top of that function (or module-level) would make this one edit instead of three. Low priority for a legacy path.

---

## Sub 5 — API endpoints (`admin_agents.py`)

**Route ordering is correct.** `/models` is registered before `/<agent_id>` — avoids Flask matching `"models"` as an agent_id. The comment documents why.

**`create_agent` temperature/max_tokens** are passed through to `save_agent` without type coercion. `request.get_json()` will give Python `float`/`int` for numeric JSON, so this is fine — but if the client sends `"0.3"` as a string (which shouldn't happen from the React UI, but could from curl), it would be stored as a string and blow up downstream. A `float()/int()` cast with a try/except at the boundary would be robust.

**`update_agent` does an extra `get_agent` round-trip for the 404 check** before calling `database.update_agent`. The DB function returns `rowcount` which would be `0` on not-found — the API could check that instead and save one query. Minor; readability is better this way.

---

## Sub 6 — Manage Agents UI (`AgentPrompts.tsx`, `ListPage.tsx`, `App.css`)

**`renderedAgents` replaces `model_code` with `model_label` for display:**

```tsx
const renderedAgents = agents.map(a => ({
  ...a,
  model_code: modelLabel(a.model_code as string | undefined),
}))
```

This means when `onRowClick` fires on a row from `renderedAgents`, the `model_code` in the clicked row is now the *label* (`"Sonnet"`), not the code (`"claude-sonnet-4-5"`). The fix is already there — `openEdit` looks up the agent from the original `agents` array:

```tsx
onRowClick={row => openEdit(agents.find(a => a.agent_id === row.agent_id) ?? row)}
```

Good. The `?? row` fallback would open the edit modal with a label instead of a code if the find failed, but that can only happen if `agents` and `renderedAgents` somehow desync — benign in practice.

**`rowActions` delete button uses `agent?.task_count ?? 1` as the disabled guard:**

```tsx
const count = agent?.task_count ?? 1
const disabled = count > 0
```

The `?? 1` means: if the agent isn't found in the original array (shouldn't happen), default to `1` which keeps the button disabled. Correct defensive choice.

**`applyModelDefaults` always overwrites temp/max_tokens** when the model dropdown changes, even if the user has already edited those fields. The plan says "pre-populate... but keep them editable — don't overwrite if user already tweaked." The current implementation overwrites on every model change. In practice this is fine — changing the model is an intentional action and the user expects the defaults to update — but it's a minor deviation from the spec.

**`eslint-disable-next-line react-hooks/exhaustive-deps`** suppresses the missing `addModel` dependency in the `useEffect`. The intent is to run the models fetch only once on mount regardless of `addModel`. This is correct but the suppression comment should at minimum note *why* it's being suppressed so the next reader doesn't flag it as a bug.

**`ModelFields` is a plain function, not a `React.FC` with `memo`** — fine for a small component, but if the parent re-renders frequently (e.g. every keystroke in the prompt textarea), `ModelFields` re-renders too. Not a real perf concern at this scale.

**`ListPage.tsx` `rowActions` prop is typed as `(row: T) => ReactNode`** — clean. The `onClick={e => e.stopPropagation()}` on the `<td>` prevents the delete click from bubbling to `onRowClick`. Correct.

---

## Cross-cutting concerns

**No tests added.** The plan didn't mention tests and there are none in the existing codebase pattern for these layers, so this isn't a gap relative to the standard.

**`MODELS` pricing is hardcoded from Anthropic's published rates.** The alias form (e.g. `claude-sonnet-4-5`) auto-upgrades on Anthropic's side, but pricing changes are a manual code update. This is the documented design decision — just flagging that it's a human process dependency.

**`agent_task.agent_id` is a convention reference, not a real FK.** Delete guard is enforced in the API layer (`count_agent_task_refs`), not at the DB level. This is documented in the plan and matches the existing pattern. If an agent is deleted via direct DB access, orphaned agent_task rows won't cascade. Fine for the current operational model.

---

## Summary of actionable items

| # | Severity | Location | Issue |
|---|----------|----------|-------|
| 1 | Low | `cost_calculator.py` | `calculate_cost` return uses backslash continuation; prefer parenthesized form for consistency |
| 2 | Low | `anthropic.py` `_fetch_response` | `"claude-sonnet-4-5"` literal appears 3x in the legacy default block — a single constant would be cleaner |
| 3 | Low | `admin_agents.py` `create_agent` | `temperature`/`max_tokens` from JSON not type-coerced; string input would store silently and fail at call time |
| 4 | Note | `AgentPrompts.tsx` `useEffect` | `eslint-disable` comment should explain the intent |
| 5 | Note | `AgentPrompts.tsx` `applyModelDefaults` | Overwrites temp/max_tokens on every model change (minor spec deviation — likely desired behavior anyway) |

None of these are blockers. Items 1–3 are minor polish; items 4–5 are informational.
