<!-- linear-archive: AST-1978 archived 2026-10-08 -->

## Linear archive (AST-1978)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1978/rsc-column-on-manage-tasks-indicate-if-dollarresponse-schema-is-used  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** ada  
**Priority / estimate:** None / 2  
**Parent:** AST-1977 — Indicate if {$RESPONSE_SCHEMA} is used  
**Blocked by / blocks / related:** parent: AST-1977

### Description

## What this implements

Serve a per-task count of `{$RESPONSE_SCHEMA}` occurrences across the raw prompt segments from `/api/admin/tasks`, and show it as an **RSC** column immediately left of **System** on Manage Tasks.

## Citations

`astral.layers.ui-config-driven-business-logic`, `astral.standards.no-hardcoded-sets`, `astral.standards.in-scope-only`, `astral.ui.naming-conventions`.

## Scope

* `src/ui/api/api_admin.py`: **modified function**. The Manage Tasks row enrichment (`_enrich_tasks`) already loads the full current task row and its agent for every task. It adds one integer field per row: the token's occurrence count summed across the raw prompt segments in Functional scope item 1. It counts the raw text before `resolve_tokens` runs, because resolution substitutes the token away. The token name comes from the existing token registry (`RESPONSE_SCHEMA` in `TOKEN_SOURCES`, `src/utils/config.py`) or one named reference, not a bare string literal copied into the function. The count is computed on the server. React only displays it.
* `src/ui/frontend/src/pages/AdminTaskPrompts.tsx`: **modified component**. Add the new field to the task row type, add a right-aligned `RSC` header between `Model` and `System`, and add the matching cell rendering the served integer. Change nothing else on the page.

Functional scope item 1 (from parent): the effective system block (the task's own system prompt when it is non-empty, otherwise the agent's content, which is the same fallback the System column already uses), cache blocks A–D, the no-cache segment, and the user prompt. The count does not depend on which candidate is selected.

## Acceptance criteria

1. **API field present.** `GET /api/admin/tasks` (as an admin) returns every row with an integer response-schema count field. **Fail:** any row lacks the field, or its value is not an integer.
2. **Count is correct.** For a task whose raw prompt segments contain `{$RESPONSE_SCHEMA}` exactly N times in total, counted on the DB row with `SELECT` + a manual count across `system_prompt` (or agent `content` when `system_prompt` is empty), `cache_prompt`, `cache_prompt_b`–`_d`, `nocache_prompt`, and `user_prompt`, the served field equals N. **Fail:** the served value differs from the manual count. This includes returning `0` because it counted resolved text after substitution.
3. **Agent fallback counted.** A task with an empty `system_prompt`, whose agent `content` contains the token once and whose other segments contain none, serves a count of `1`. **Fail:** it serves `0`.
4. **Candidate-independent.** The served count for a task is identical with and without `?candidate_id=<id>`. **Fail:** the values differ.
5. **Column placement.** On Manage Tasks, the header order reads `… Model | RSC | System | Base Cache …`, and each row's RSC cell shows the served integer, `0` included. **Fail:** RSC is missing, sits anywhere other than immediately left of System, or shows blank for `0`.
6. **No client-side counting.** `grep -n "RESPONSE_SCHEMA" src/ui/frontend/src/pages/AdminTaskPrompts.tsx` returns nothing. **Fail:** any match, which means React is deriving the count itself.
7. **No bare literal in the row builder.** In the `_enrich_tasks` diff, the token appears only through a registry lookup or a single named reference, never as an inline `"{$RESPONSE_SCHEMA}"` / `"RESPONSE_SCHEMA"` string literal inside the loop. **Fail:** a bare literal appears in the function body.

## Boundaries

Does not change any other Manage Tasks column, the token-estimate math, or the prompt editor. Only child of [AST-1977](https://linear.app/astralcareermatch/issue/AST-1977).

## Notes for planning

Single vertical slice: the served field and its column are not separately testable at UAT.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at dispatch-parent. Resolve with `epic_registry.py show AST-1977 --ref <this-id>`.

### Comments

#### radia — 2026-10-04T21:01:13.232Z
[code-rubric] PROCEED (Commit: a7ecce19c) RSC column matches plan

#### betty — 2026-10-04T20:59:07.967Z
`origin/sub/AST-1977/AST-1978-rsc-column` @ `a7ecce19c` · RSC tests + bible landed

#### joan — 2026-10-04T20:53:51.058Z
[plan-rubric] PROCEED (Commit: ea051b757) RSC server plus column

#### ada — 2026-10-04T20:52:22.113Z
`origin/sub/AST-1977/AST-1978-rsc-column` @ `ea051b757` · server count, RSC column

---

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

## Joan validate

[plan-rubric]

**Ticket:** AST-1978  
**Overall:** APPROVED  
**Corpus:** e1f2699fad  
**Publish ref:** `ea051b7575038952289c94a28e29f3cc75935bc1` (`origin/sub/AST-1977/AST-1978-rsc-column`)

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| astral.layers.ui-config-driven-business-logic | A | | |
| astral.standards.no-hardcoded-sets | A | | |
| astral.standards.in-scope-only | A | | |
| astral.ui.naming-conventions | A | | |

## Traceability

AC1–7 → Stage 1 (API field, raw-segment count, agent fallback, candidate independence, AC7 registry token) + Stage 2 (column order, display, grep-clean client).

## Findings

- **acceptable** — `## Scope check` / Files Changed: only `api_admin.py` `_enrich_tasks` and `AdminTaskPrompts.tsx`; matches child `## Scope` and parent component/technical scope.  
- **acceptable** — Stage 1 `raw_system` uses `.strip()` then agent content, aligned with `resolved_task_system` and parent functional scope; whitespace-only edge documented vs System token column.  
- **acceptable** — Inline segment key tuple in `_enrich_tasks` justified as DB column names, not a config value set; `config.py` correctly out of scope.  
- **acceptable** — Plan clerk note (`canon_clerk expand` unknown ids / no `docs/canon-index.md` in worktree): statutes read from `canon/statutes/astral/**`; index at clerk run reports `e1f2699fad` — not a plan defect.

**R6 (summary):** Definition fidelity, two-file footprint, execution contract, and adversarial decisions match parent purpose and all seven ACs. No scope creep into editor, token math, or `AdminAnthropicAdHoc.tsx`. Self-assessment and estimate (2) match slice size. No `[plan-discuss]` rounds on thread (Plan Ready, assignee Joan).

context_tokens≈22000

## Review

| Field | Value |
|-------|-------|
| Branch | `sub/AST-1977/AST-1978-rsc-column` |
| Build tip | `b89597cce7cc9956dcbf7438c23100f126f9cb21` |
| Status | Code Complete |

## Radia review

[code-rubric]
**Ticket:** AST-1978
**Publish ref:** a7ecce19cfb247b549c17af36210ce2cdf9a10ac (`origin/sub/AST-1977/AST-1978-rsc-column`)
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51
**Overall:** CLEAN

## Canon scores

astral.layers.ui-config-driven-business-logic | A | |
astral.standards.no-hardcoded-sets | A | |
astral.standards.in-scope-only | A | |
astral.ui.naming-conventions | A | |

## Column diff vs plan stage

(aligned) — Joan graded all four A at plan stage; diff confirms same.

## Frame diff

(none)

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **Clerk resolution:** `canon_clerk.py expand` still rejects all four frozen statute ids (same migration gap as plan doc / AST-1872). Scoring used `canon/statutes/astral/**` bodies directly; `canon_clerk.py index --json` reports `corpus_dirty: false` at `e1f2699fad`.
- **Plan vs System column edge:** Documented in plan — task with non-blank `system_prompt` and no agent shows `0` System tokens but RSC still counts raw task text; diff implements that intentionally (`raw_system` does not require `agent`).

## What's solid

- Product diff is exactly the two scoped files: `_RESPONSE_SCHEMA_TOKEN` + import-time `get_tokens()` assert; `_enrich_tasks` raw seven-segment sum; `response_schema_count` on the row dict; Manage Tasks **RSC** column between Model and System, grep-clean on the TSX page.
- `raw_system` matches `resolved_task_system`’s strip-then-agent fallback (`src/core/agent.py` ~504–505); count is pre-resolution and candidate-independent; tests (`TestAst1978ResponseSchemaCount`, frontend header/cell test) track AC 1–5 and bible manifest § AST-1978.
- AC7-style check: no `"RESPONSE_SCHEMA"` / `"{$RESPONSE_SCHEMA}"` string literals inside `_enrich_tasks` body; only `_RESPONSE_SCHEMA_TOKEN` and module-level registry tie-in.

## Recommended actions (downstream only — not executed here)

- Chuckles: append this artifact to `docs/features/interface/ast-1978-rsc-column-on-manage-tasks.md`, commit `docs(AST-1978): Radia review — clean`, push publish ref, post slim upshot `--as radia`, move **Review Posted**.
- datt: **PROCEED** → **User Testing** (no fix-now / discuss).

context_tokens≈18000
