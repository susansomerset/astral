# AST-1978 — RSC column on Manage Tasks (Indicate if {$RESPONSE_SCHEMA} is used)

- **Linear:** [AST-1978](https://linear.app/astralcareermatch/issue/AST-1978) · parent [AST-1977](https://linear.app/astralcareermatch/issue/AST-1977)
- **Publish ref:** `origin/sub/AST-1977/AST-1978-rsc-column`
- **Assignee:** Ada

`GET /api/admin/tasks` serves one new integer per task row, `response_schema_count`. It is the number
of times the literal `{$RESPONSE_SCHEMA}` token appears in the task's **raw** (pre-`resolve_tokens`)
prompt segments: the effective system block, cache A–D, no-cache, and user. Manage Tasks shows it in a
new right-aligned **RSC** column directly left of **System**. The server does the counting and React
only displays the number. The count ignores the selected candidate.

## Scope check

Every file below is named in this ticket's `## Scope`, and every change is the kind Scope describes:

- `src/ui/api/api_admin.py`: **modified function** `_enrich_tasks` adds one integer field per row.
  It also gets one module-level named token reference directly above it. Scope allows this ("the
  registry ... or one named reference").
- `src/ui/frontend/src/pages/AdminTaskPrompts.tsx`: **modified component**. It gets one row-type
  field, one `<th>`, and one `<td>`.

No scope gap. `src/utils/config.py` and `src/data/**` stay untouched. `database.get_agent_task` is
already `SELECT *`, so every raw prompt column is already loaded in `_enrich_tasks` as `full_task`.

## Canon Scope (id-only at plan)

`astral.layers.ui-config-driven-business-logic`, `astral.standards.no-hardcoded-sets`,
`astral.standards.in-scope-only`, `astral.ui.naming-conventions`.

None of the four is a pattern. They were read in full from `canon/statutes/astral/**` because they
decide placement (server-side count, named token, naming). **Clerk note:**
`python3 canon/canon_clerk.py expand <ids>` fails with `unknown directive id(s)` for all four at
`3a78a9640`. This is the same clerk-migration gap recorded on AST-1872 / AST-1678.
`docs/canon-index.md` is not present in this worktree.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/api/api_admin.py` | Add `_RESPONSE_SCHEMA_TOKEN_NAME` / `_RESPONSE_SCHEMA_TOKEN` above `_enrich_tasks`; `_enrich_tasks` computes and serves `response_schema_count` | ui |
| `src/ui/frontend/src/pages/AdminTaskPrompts.tsx` | `AgentTask.response_schema_count: number`; `RSC` header + cell between Model and System | ui |

No other files. In particular, `AdminAnthropicAdHoc.tsx` also reads `/api/admin/tasks`. It only
receives an extra field it ignores, and it stays untouched (Boundaries).

## Stage 1: Server — `response_schema_count` on every `/api/admin/tasks` row

**Done when:** `GET /api/admin/tasks` returns `response_schema_count` (int) on every row, equal to the
raw count of `{$RESPONSE_SCHEMA}` across the effective system block plus `cache_prompt`,
`cache_prompt_b`–`_d`, `nocache_prompt`, and `user_prompt`. The value is the same with and without
`?candidate_id=`. No existing row field changes value.

1. In `src/ui/api/api_admin.py`, add `get_tokens` to the existing `from src.utils.config import (...)`
   block **only if it is not already there**. It currently is (line ~62), so no import change is
   expected.
2. In `src/ui/api/api_admin.py`, directly **above** `def _enrich_tasks(` (after
   `_grouping_from_agent_task_row`, keeping two blank lines either side), add exactly:
   ```python
   # AST-1978: Manage Tasks RSC column — the TOKEN_SOURCES name counted in raw prompt text, before
   # resolve_tokens substitutes it away. Fails at import if the registry ever drops/renames it.
   _RESPONSE_SCHEMA_TOKEN_NAME = "RESPONSE_SCHEMA"
   assert _RESPONSE_SCHEMA_TOKEN_NAME in get_tokens(), "RESPONSE_SCHEMA missing from TOKEN_SOURCES"
   _RESPONSE_SCHEMA_TOKEN = "{$" + _RESPONSE_SCHEMA_TOKEN_NAME + "}"
   ```
3. In `_enrich_tasks`, immediately **after** the line `system_tokens = len(system_content) // CHARS_PER_TOKEN`
   (and before the `# Prompt field token estimates` comment), insert exactly:
   ```python

            # AST-1978: RSC = raw {$RESPONSE_SCHEMA} occurrences across every segment the task sends.
            # Counted pre-resolution (resolve_tokens replaces the token); candidate-independent.
            # System segment mirrors resolved_task_system: task system_prompt when non-blank, else agent content.
            _ft = full_task or {}
            raw_system = (_ft.get("system_prompt") or "").strip() or ((agent or {}).get("content") or "")
            response_schema_count = sum(
                seg.count(_RESPONSE_SCHEMA_TOKEN)
                for seg in (raw_system, *(_ft.get(k) or "" for k in (
                    "cache_prompt", "cache_prompt_b", "cache_prompt_c", "cache_prompt_d",
                    "nocache_prompt", "user_prompt",
                )))
            )
   ```
4. In the same function's `rows.append({...})` dict, add one entry on the line **directly after**
   `"system_prompt_tokens": system_tokens,`, aligned with its neighbours:
   ```python
                "response_schema_count": response_schema_count,
   ```
5. Change nothing else in `_enrich_tasks`. `system_content`, the cache probes, `task_ready`, the token
   math, and timesheet averages stay as they are.
6. `python3 -m py_compile src/ui/api/api_admin.py` and `python3 -c "import src.ui.api.api_admin"`
   (from the repo root with the repo env). The import must succeed, which proves the step-2 assert holds.
7. AC 7 self-check: `git diff -U0 origin/dev -- src/ui/api/api_admin.py | grep -n 'RESPONSE_SCHEMA'`.
   The only hits allowed are the three module-level lines from step 2 and the `_RESPONSE_SCHEMA_TOKEN`
   reference / comment inside the step-3 block. There must be no `"{$RESPONSE_SCHEMA}"` or
   `"RESPONSE_SCHEMA"` string literal inside `_enrich_tasks`.
8. Commit: `code(AST-1978): serve response_schema_count on /api/admin/tasks rows`. Publish per build-child §9.

⚠️ **Decision (counting approach).** I considered three options:
(a) A module-level named token tied to the registry, plus `str.count` over the raw segments.
**Chosen.** It is the smallest change, stays inside Scope's two files, and the import-time assert
gives registry tie-in (the same idiom `config.py` uses for `TOKEN_SOURCES`).
(b) Reuse `config._TOKEN_RE.finditer` and filter on the name. **Rejected.** It imports a private
symbol across layers and takes more lines for the same count.
(c) Add a `count_token_in_texts` helper to `config.py`. **Rejected.** `config.py` is not in this
ticket's Scope.

⚠️ **Decision (system segment fallback).** The `.strip()`-then-agent-content rule copies
`resolved_task_system` (`src/core/agent.py` ~504–505), so a whitespace-only `system_prompt` falls
back to the agent the same way the System column does. In the one edge where a task row has a
non-blank `system_prompt` but no agent, the System column shows 0 tokens. RSC still counts the task's
own `system_prompt`, because AC 2's manual count is defined on `system_prompt` alone. That edge cannot
run anyway, since a task without an agent is not dispatchable.

⚠️ **Decision (field name).** The field is **`response_schema_count`**: snake_case, a self-describing
row field like `system_prompt_tokens` (`astral.ui.naming-conventions`). **RSC** is only the column
label.

⚠️ **Decision (segment key tuple).** The six column names are listed inline, matching the existing
inline `("cache_prompt", …, "cache_prompt_d")` tuple a few lines below in the same function. They are
`agent_task` column names, not a business value set, so `no-hardcoded-sets` does not call for a config
constant (and `config.py` is out of Scope).

## Stage 2: Manage Tasks — RSC column left of System

**Done when:** On Manage Tasks, every section table's header reads
`Task | Run next | Agent | Model | RSC | System | Base Cache | …`. Each row's RSC cell is
right-aligned and shows the served integer, with `0` rendered as `0`.
`grep -n "RESPONSE_SCHEMA" src/ui/frontend/src/pages/AdminTaskPrompts.tsx` prints nothing.

1. In `src/ui/frontend/src/pages/AdminTaskPrompts.tsx`, in `interface AgentTask`, insert directly
   **above** `system_prompt_tokens: number`:
   ```ts
     response_schema_count: number        // RSC: raw {$…} response-schema token count, served by /api/admin/tasks
   ```
   Do not write the token name in the comment. It must stay grep-clean for AC 6, which is why the
   comment uses `{$…}`.
2. In the `<thead>` row, insert directly **between** `<th>Model</th>` and
   `<th style={{ textAlign: "right" }}>System</th>`:
   ```tsx
                         <th style={{ textAlign: "right" }}>RSC</th>
   ```
3. In the `<tbody>` row, insert directly **between** the `row.model_code` `<td>` and the
   `row.system_prompt_tokens` `<td>`:
   ```tsx
                           <td style={{ textAlign: "right" }}>{row.response_schema_count}</td>
   ```
   React renders the number `0` as `0`, so there is no fallback or `—` (AC 5).
4. Change nothing else on the page. There is no `colSpan` anywhere in the file, so no other row needs
   adjusting.
5. Verify AC 6: `grep -n "RESPONSE_SCHEMA" src/ui/frontend/src/pages/AdminTaskPrompts.tsx` must print
   nothing.
6. Compile and lint from `src/ui/frontend/`: if `node_modules/` is absent, run `npm ci` first (it is
   untracked, so no repo change). Then run `npm run build` and `npx eslint src/pages/AdminTaskPrompts.tsx`.
   Both must pass with no new errors.
7. Commit: `code(AST-1978): Manage Tasks RSC column left of System`. Publish per build-child §9.

## Test fallout (Betty, qa-child; the engineer does not touch `tests/`)

- `tests/component/ui/api/test_api_admin.py` covers `/api/admin/tasks` / `_enrich_tasks`. Any
  exact-key assertion on a row will now see `response_schema_count`. New coverage for AC 1–4 (raw
  count, agent fallback, candidate independence) belongs in Betty's manifest.
- `tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx` covers header order and the RSC
  cell (AC 5). Fixtures that build `AgentTask` rows may need the new field.
- `tests/component/frontend/pages/test_AdminAnthropicAdHoc.test.tsx` should not be affected, since
  that page is not changed.

## Execution contract

This plan is binding. Execute steps in order and stages in order. Do not add files, imports (beyond
Stage 1 step 1's conditional), constants, or routes. If a referenced line, name, or signature has
drifted from what's written here, or Stage 1 step 6's import fails, stop and comment on parent
AST-1977:

```
🛑 Stage N blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

Each stage is one commit on the epic worktree, published to `origin/sub/AST-1977/AST-1978-rsc-column`
before the next stage starts.

## Estimate

Confirm Chuckles estimate: 2 — agree
