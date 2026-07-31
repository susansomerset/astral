# UAT: Admin task_name should equal task_key for now

**Linear:** [AST-1107](https://linear.app/astralcareermatch/issue/AST-1107/uat-admin-task-name-should-equal-task-key-for-now)

**Parent:** [AST-1087](https://linear.app/astralcareermatch/issue/AST-1087/add-gaze-email-as-a-dispatch-task)

**Publish ref:** `sub/AST-1087/AST-1107-uat-admin-task-name-should-equal-task-key-for-now`

Admin Task Prompts now displays `task_name` (falling back to `task_key` only when empty). Friendly labels in `data/admin/agent_task.json` make meteorite / gaze_email UAT unreadable. This ticket rewrites every current catalog row so `task_name == task_key` (temporary clarity), keeps section grouping (`task_group_*`) unchanged, and syncs the AST-756 seed fixture. Does **not** hardcode display strings in React or rename any `task_key`.

## UAT fitness

- **AC restored:** Parent AC1 — “With a `gaze_email` `dispatch_task` row (`candidate_id` null, `auto_mode` true) running under normal dispatch…” — Parent UAT requires Susan to identify and operate dispatcher / Task Prompts catalog entries for this epic; labels currently come from `agent_task.task_name`.
- **Correct outcome:** Every in-catalog `agent_task.task_name` equals that row’s `task_key` so Admin labels match keys; section grouping (`task_group_order` / `task_group_name` / `task_seq`) remains usable. Keys used by this epic (`gaze_email`, `parse_meteorite_email`) are included.
- **Sibling check:** AST-1088/1089/1090 product contracts unchanged (no TASK_CONFIG prompt edits, no dispatch claim/runner/Gmail changes). AST-1106 already set `gaze_email`’s `task_name` to `gaze_email` — this pass normalizes the rest of the catalog the same way.
- **Not sufficient:** Changing one React label string alone is **not** done. Catalog data must make every Task Prompts row show its key.
- **Wrong fix rejected:** Do **not** hardcode display strings in React; do **not** invent a second naming system; do **not** rename `task_key` values; do **not** change long-term product naming strategy beyond temporary `task_name := task_key`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `data/admin/agent_task.json` | Set every current row’s `task_name` to equal that row’s `task_key` (leave grouping/prompts/agent_id untouched) | data/admin |
| `docs/uat-fixtures/AST-756/expected-agent_task.json` | Byte-identical copy after the rewrite (AST-786 seed gate) | docs |

## Stage 1: Rewrite catalog `task_name` := `task_key`

**Done when:** For every object in `data/admin/agent_task.json` with `current == 1`, `task_name == task_key` (string equality). No other fields change. JSON remains a flat-row array of scalars.

1. In the epic worktree on `sub/AST-1087/AST-1107-uat-admin-task-name-should-equal-task-key-for-now`, load `data/admin/agent_task.json`.
2. For each row, set `task_name` to the exact string value of `task_key` (including rows that already match, e.g. `gaze_email`).
3. Do **not** edit `task_group_order`, `task_group_name`, `task_seq`, prompts, `agent_id`, or UUIDs.
4. Write the file back with the same pretty-print style as the repo (2-space indent + trailing newline). Prefer a small mechanical Python rewrite over hand-editing 47 rows.

⚠️ **Decision — data source, not React:** Task Prompts already renders `{row.task_name || row.task_key}` (`AdminTaskPrompts.tsx`). Scheduled Actions Task column already shows `task_key`. Fixing the catalog makes labels match keys without hardcoding display strings in the frontend (Code Rules UI business-logic / Diagnosis wrong fix).

⚠️ **Decision — temporary UAT clarity only:** Do not invent a permanent naming framework or change `task_key` identifiers. Sibling AST-1106 already aligned `gaze_email`; this ticket finishes the catalog.

**Verify:**

```bash
python3 -c "
import json
rows=json.load(open('data/admin/agent_task.json'))
bad=[(r.get('task_key'), r.get('task_name')) for r in rows if (r.get('task_name') or '') != (r.get('task_key') or '')]
assert not bad, bad
assert any(r.get('task_key')=='gaze_email' and r.get('task_name')=='gaze_email' for r in rows)
assert any(r.get('task_key')=='parse_meteorite_email' and r.get('task_name')=='parse_meteorite_email' for r in rows)
print('OK', len(rows))
"
```

**Ritual:** `code(AST-1107): agent_task task_name equals task_key`

## Stage 2: AST-756 fixture sync

**Done when:** `docs/uat-fixtures/AST-756/expected-agent_task.json` is byte-identical to `data/admin/agent_task.json`.

1. Copy and verify:

```bash
cp data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json
cmp -s data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json && echo OK
```

2. Do **not** hand-edit the live DB — startup `apply_repo_admin_json` ships the repo file (same path as AST-1089 / AST-1106).

**Ritual:** `code(AST-1107): AST-756 fixture sync after task_name rewrite`

## Execution contract

- Stages in order; one commit per stage on the epic worktree sub branch; publish to `origin/<publish-ref>` after each stage per build-child.
- No files outside the Files Changed table.
- Ambiguity or codebase drift → stop and comment on **parent** AST-1087 with the Stage N blocked template.
- Leave TASK_CONFIG prompts, dispatch runners, Gmail I/O, and React display logic untouched.

## Self-Assessment

**Scope:** `Single-Component` — repo `agent_task.json` catalog labels + AST-756 fixture sync; no `src/` product logic.

**Conf:** `high` — mechanical field rewrite; UI already prefers `task_name` with `task_key` fallback; grouping columns untouched; mirrors AST-1106’s `gaze_email` naming choice.

**Risk:** `low` — Admin Task Prompts labels change site-wide to keys (intentional temporary clarity); section headers still use `task_group_name`; fixture drift fails AST-786 gate if Stage 2 is skipped.

## Self-review vs ASTRAL_CODE_RULES

- **§2.1 / config-source-of-truth:** Display labels for Manage Tasks live in repo-owned `agent_task` JSON (AST-782), not React literals.
- **§1.4 / no-hardcoded-sets:** No new React name maps.
- **§3 UI:** No frontend business-rule change; data already drives the label.
- **in-scope-only:** No runner / Gmail / TASK_CONFIG prompt / `task_key` renames.
- **No conflict requiring conf-!!-NONE.**

## Review

**Publish ref:** `origin/sub/AST-1087/AST-1107-uat-admin-task-name-should-equal-task-key-for-now`
**Tip:** `adb30fc1`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `3356309c` | agent_task task_name equals task_key (47 rows rewritten) |
| 2 | `adb30fc1` | AST-756 fixture sync after task_name rewrite |

