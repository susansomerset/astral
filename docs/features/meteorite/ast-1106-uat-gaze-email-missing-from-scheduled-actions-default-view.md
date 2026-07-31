# UAT: gaze_email missing from Scheduled Actions default view

**Linear:** [AST-1106](https://linear.app/astralcareermatch/issue/AST-1106/uat-gaze-email-missing-from-scheduled-actions-default-view)

**Parent:** [AST-1087](https://linear.app/astralcareermatch/issue/AST-1087/add-gaze-email-as-a-dispatch-task)

**Publish ref:** `sub/AST-1087/AST-1106-uat-gaze-email-missing-from-scheduled-actions-default-view`

After AST-1087 UAT, the shared null-`candidate_id` `gaze_email` dispatch row is invisible under Scheduled Actions’ default Avail **> 0** filter because list enrichment correctly sets `available_count=0` when `entity_type` / `trigger_state` / `candidate_id` are absent. This ticket adds a config-driven, API-resolved “always visible under Avail gt0” carve-out for that mailbox shell (without faking a positive avail count) and ships a repo `agent_task` catalog row so the task groups under Job Review like its meteorite siblings.

## UAT fitness

- **AC restored:** Parent AC1 — “With a `gaze_email` `dispatch_task` row (`candidate_id` null, `auto_mode` true) running under normal dispatch…” — and Parent AC9 — “The `dispatch_task` schema/provision path allows `candidate_id` null for `gaze_email`…” — require Susan to find and operate that shared row in Task Dispatcher / Scheduled Actions during UAT.
- **Correct outcome:** Susan can see and run/flip AUTO on the shared `gaze_email` row under default Scheduled Actions filters (Avail **> 0**, Candidate All) without clearing obscure filters; catalog meta exists so it groups under Job Review.
- **Sibling check:** AST-1088 provision/ensure null-candidate row unchanged; AST-1090 runner / due wiring unchanged; AST-1089 Ruth `parse_meteorite_email` prompts/contracts unchanged. AST-1107 (`task_name := task_key`) is a separate display pass — this plan sets `task_name` to `gaze_email` on the new catalog row so it already matches that temporary clarity rule.
- **Not sufficient:** Removing a stacktrace / 5xx alone is **not** done. Row must be visible + operable under normal admin use.
- **Wrong fix rejected:** Do **not** fake a non-zero `available_count` for mailbox tasks; do **not** delete the Avail gt0 default without a mailbox carve-out; do **not** invent a fake `candidate_id` just to pass enrichment; do **not** hardcode `gaze_email` visibility sets in React (UI business rules resolve in API from config).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `ADMIN_CONFIG` always-visible-under-avail-gt0 task-key tuple (seeded from `GAZE_EMAIL_CONFIG["task_key"]`) + helper frozenset accessor | utils |
| `src/ui/api/api_admin.py` | Stamp `always_visible_under_avail_gt0` on each `list_dtasks` row from that helper | ui |
| `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | Avail gt0 filter keeps rows where the API flag is true; extend `DispatchTask` type | ui |
| `data/admin/agent_task.json` | Add current `gaze_email` catalog row (empty prompts, Job Review grouping) | data/admin |
| `docs/uat-fixtures/AST-756/expected-agent_task.json` | Byte-identical copy after the new row (AST-786 seed gate) | docs |

## Stage 1: Config — always-visible under Avail gt0 keys

**Done when:** `admin_always_visible_under_avail_gt0_dispatch_task_keys()` returns a frozenset containing `GAZE_EMAIL_CONFIG["task_key"]` (`"gaze_email"`) and no other product literals are invented in React for this rule.

1. In `src/utils/config.py`, on `ADMIN_CONFIG` (near `hidden_dispatch_task_keys` usage / the existing `ADMIN_CONFIG` dict), add:

   ```python
   "always_visible_under_avail_gt0_dispatch_task_keys": (
       GAZE_EMAIL_CONFIG["task_key"],
   ),
   ```

   `GAZE_EMAIL_CONFIG` is already defined above `ADMIN_CONFIG` on this tip — do **not** duplicate the string `"gaze_email"` as a bare literal in this tuple.

2. Immediately after `admin_hidden_dispatch_task_keys()`, add:

   ```python
   def admin_always_visible_under_avail_gt0_dispatch_task_keys() -> frozenset:
       """task_key values kept visible under Scheduled Actions Avail > 0 (mailbox shells)."""
       raw = ADMIN_CONFIG.get("always_visible_under_avail_gt0_dispatch_task_keys") or ()
       return frozenset(raw)
   ```

3. Mirror the module header inventory comment style if `ADMIN_CONFIG` / helpers are listed there — one line noting the Avail-gt0 always-visible set (AST-1106).

⚠️ **Decision — config frozenset, not fake avail:** Visibility exception is an admin-UI policy for mailbox shells with intentional zero entity eligibility. Keep `available_count` computation unchanged (`0` when entity/trigger/candidate missing).

**Ritual:** `code(AST-1106): admin always-visible under avail gt0 config`

## Stage 2: API stamps the visibility flag on dispatch_task rows

**Done when:** `GET /api/admin/dispatch_tasks` JSON rows include boolean `always_visible_under_avail_gt0` true iff `task_key` is in the Stage 1 frozenset; other rows false. Enrichment still sets `available_count` via the existing `et and ts and cid` gate (gaze_email stays `0`).

1. In `src/ui/api/api_admin.py`, import `admin_always_visible_under_avail_gt0_dispatch_task_keys` from `src.utils.config` (same import cluster as `admin_hidden_dispatch_task_keys`).

2. In `list_dtasks()`, after computing `available_count` for each row (and before/alongside the hidden-key filter is fine), set:

   ```python
   row["always_visible_under_avail_gt0"] = (
       row.get("task_key") in admin_always_visible_under_avail_gt0_dispatch_task_keys()
   )
   ```

3. Do **not** change `count_eligible_for_dispatch_task` / the `et and ts and cid else 0` gate. Do **not** add this flag by inventing a positive `available_count`.

⚠️ **Decision — resolve in API:** Code Rules §3 UI — frontend must not own the business set; it only honors the boolean the API already resolved from config.

**Ritual:** `code(AST-1106): stamp always_visible_under_avail_gt0 on list_dtasks`

## Stage 3: Scheduled Actions Avail gt0 carve-out (flag only)

**Done when:** With default `availGtZeroFilter === "gt0"`, a row with `available_count === 0` and `always_visible_under_avail_gt0 === true` remains in `filteredRows`; other zero-avail rows stay omitted. Default Avail remains `"gt0"` (AST-894). No React literal `"gaze_email"` for this filter.

1. In `src/ui/frontend/src/pages/AdminScheduledActions.tsx`, extend the `DispatchTask` interface with:

   ```typescript
   always_visible_under_avail_gt0?: boolean
   ```

2. Replace the Avail gt0 predicate only — keep Candidate / section / AUTO / other filters unchanged:

   ```typescript
   if (availGtZeroFilter === "gt0") {
     filtered = filtered.filter(
       r => (r.available_count ?? 0) > 0 || !!r.always_visible_under_avail_gt0,
     )
   }
   ```

3. Do **not** change `formatAvailableCount` (gaze_email continues to show Avail as `—` when count is 0). Do **not** change default `useState("gt0")`. Do **not** widen Candidate All semantics (null `candidate_id` still only appears when Candidate filter is empty / All).

**Ritual:** `code(AST-1106): SA Avail gt0 keeps API always-visible rows`

## Stage 4: Repo `agent_task` catalog row + AST-756 fixture

**Done when:** `data/admin/agent_task.json` has a `current: 1` row for `task_key == "gaze_email"` with Job Review grouping; `docs/uat-fixtures/AST-756/expected-agent_task.json` is byte-identical; JSON remains a flat-row array. Startup `apply_repo_admin_json` will ship the row (same path as AST-1089).

1. Append one object to `data/admin/agent_task.json` (flat scalars only), modeled on the existing non-Ruth dispatch shells (`gaze`, `fetch_jd`) — **not** on Ruth prompt rows:

   | Field | Value |
   |-------|--------|
   | `task_key_uuid` | `519eba14-091c-45d2-9fa7-ff94b42bf9cf` |
   | `task_key` | `gaze_email` |
   | `current` | `1` |
   | `agent_id` | `n/a` |
   | `user_prompt` / `cache_prompt` / `cache_prompt_b`–`d` / `nocache_prompt` / `system_prompt` / `run_next` | `""` |
   | `task_group_order` | `"4000"` |
   | `task_group_name` | `Job Review` |
   | `task_seq` | `2.3` (before `parse_meteorite_email` ~`2.4`, before `qualify_meteorite` `2.5`) |
   | `task_name` | `gaze_email` (equals `task_key` — temporary clarity; aligns with AST-1107) |
   | `updated_at` | ISO-ish UTC timestamp string consistent with neighboring rows |

2. Sync the AST-786 gate fixture:

   ```bash
   cp data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json
   cmp -s data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json && echo OK
   ```

3. Verify parse + presence:

   ```bash
   python3 -c "import json; rows=json.load(open('data/admin/agent_task.json')); assert any(r.get('task_key')=='gaze_email' and r.get('task_group_name')=='Job Review' for r in rows)"
   ```

⚠️ **Decision — repo JSON is source of truth for grouping:** Same as AST-1089; do **not** hand-edit live DB. Empty prompts because `gaze_email` is a mailbox dispatch shell (Ruth parse stays on `parse_meteorite_email`).

⚠️ **Decision — out of scope for this ticket:** Do **not** rewrite every existing friendly `task_name` to equal `task_key` (that is AST-1107). Do **not** change Gmail scopes, runner, or Ruth prompts.

**Ritual:** `code(AST-1106): gaze_email agent_task catalog + AST-756 fixture`

## Execution contract

- Stages in order; one commit per stage on the epic worktree sub branch; publish to `origin/<publish-ref>` after each stage per build-child.
- No files outside the Files Changed table.
- Ambiguity or codebase drift → stop and comment on **parent** AST-1087 with the Stage N blocked template.
- Leave AST-1088/1089/1090 product contracts and AST-1107 bulk rename untouched except the new `gaze_email` catalog row named above.

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — utils admin config, admin API enrichment, Scheduled Actions React filter, and repo `agent_task` + AST-756 fixture.

**Conf:** `high` — diagnosis matches `list_dtasks` (`et and ts and cid else 0`) + default `availGtZeroFilter="gt0"`; carve-out pattern is a boolean flag from config; catalog seed mirrors AST-1089 / empty-prompt shells like `gaze`.

**Risk:** `Medium` — wrong Avail predicate could re-hide mailbox shells or accidentally show unrelated zero-avail rows if the config set is widened carelessly; fixture drift fails AST-786 gate. Scoped to `GAZE_EMAIL_CONFIG["task_key"]` only.

## Self-review vs ASTRAL_CODE_RULES

- **§2.1 / config-source-of-truth:** Always-visible task keys live in `ADMIN_CONFIG`, seeded from `GAZE_EMAIL_CONFIG["task_key"]`.
- **§1.4 / no-hardcoded-sets:** No React `"gaze_email"` visibility set; API boolean only.
- **§3 UI business logic:** Visibility exception resolved in `api_admin.list_dtasks` from config; frontend renders the flag.
- **§3.3 imports:** ui←utils only for the helper; no new data/external imports in UI.
- **in-scope-only:** No Gmail / Ruth / runner / fake candidate_id / removing Avail default.
- **No conflict requiring conf-!!-NONE.**

## Review

**Publish ref:** `origin/sub/AST-1087/AST-1106-uat-gaze-email-missing-from-scheduled-actions-default-view`
**Tip:** `64431acd`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `ea8c8665` | ADMIN_CONFIG always-visible under Avail gt0 |
| 2 | `31f34265` | list_dtasks stamps `always_visible_under_avail_gt0` |
| 3 | `7c32fd19` | SA Avail gt0 keeps API always-visible rows |
| 4 | `ee05c771` | gaze_email agent_task catalog + AST-756 fixture |
| 4b | `64431acd` | null-safe Candidate cell (Betty product return) |

**Betty product return (`64431acd`):** the Stage 3 carve-out surfaced the shared mailbox row, and `ListTableTruncatedCell text={row.candidate_id}` crashed `truncateForDisplay` on the null `candidate_id` (AST-1088). `DispatchTask.candidate_id` is now typed `string | null` to match the API, the Candidate cell renders `"—"` like its sibling cells, and `openEdit` coerces to `""` (the edit PUT never sends `candidate_id`). Avail carve-out and `available_count` computation unchanged; no invented candidate id.
