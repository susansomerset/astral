# AST-1222 — Meteorite Do/Get alias seed + retarget dispatch

**Linear:** [AST-1222](https://linear.app/astralcareermatch/issue/AST-1222/meteorite-doget-alias-seed-retarget-dispatch-task-config-aliases-via)
**Parent:** [AST-1184](https://linear.app/astralcareermatch/issue/AST-1184/task-config-aliases-via-master-task-key) — Task config aliases via master_task_key
**Publish ref:** `origin/sub/AST-1184/AST-1222-meteorite-do-get-alias-seed-retarget-dispatch`

After **AST-1221** (User Testing): retarget meteorite Do/Get dispatch catalog rows from shared `grade_do` / `grade_get` to alias keys `meteorite_grade_do` / `meteorite_grade_get`; retire stale shared-key meteorite trigger rows on provision; seed grouping-only `agent_task` identities under the live **Meteorite Review** section (empty prompts — master's prompts via `resolve_task_key_for_content`); keep AST-756 fixture lockstep. Does **not** invent resolve helpers (**AST-1220** / **AST-1221**), own UI hardcode audit (**AST-1185**), or rename Gaze/Meteorite Review sections (**AST-1183** — already live as Meteorite Review on this tree).

**Depends on AST-1221 (User Testing):** alias `TASK_CONFIG` entries, runtime resolve, overlay deleted. Build expects those on the epic tree via `sync-child` (already merges `origin/dev`; attach `origin/ftr/AST-1184-…` when Chuckles publishes it). If `meteorite_grade_do` / `is_task_alias` are missing at Stage 1 start → stop, comment on parent, wait — do not re-implement the contract.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Retarget `METEORITE_DISPATCH_TASKS` Do/Get `task_key`s; retarget matching `SEED_CONFIG["dispatch_task-meteorite"]` INSERT SQL | utils |
| `src/core/dispatcher.py` | In `ensure_meteorite_dispatch_tasks`, retire `grade_do`@`METEORITE_PASSED_JD` / `grade_get`@`METEORITE_PASSED_DO` once alias rows are present (classic Gaze `PASSED_JD` / `PASSED_DO` untouched) | core |
| `data/admin/agent_task.json` | Add current grouping-only `meteorite_grade_do` / `meteorite_grade_get` rows; bump `meteorite_like` / `meteorite_upshot` `task_seq` | data/admin |
| `docs/uat-fixtures/AST-756/expected-agent_task.json` | Surgical sync of the same new rows + seq bumps — **no** whole-file `cp` | docs |

**No changes expected:** `src/core/agent.py`, `src/core/consult.py`, `TASK_CONFIG` alias literals / resolve helpers, frontend, classic Gaze `agent_task` / Gaze dispatch keys, `tests/` / bible (Betty after Code Complete).

## Stage 1: Retarget dispatch catalog + retire stale shared-key rows

**Done when:** `METEORITE_DISPATCH_TASKS` Do/Get entries use `meteorite_grade_do` @ `METEORITE_PASSED_JD` and `meteorite_grade_get` @ `METEORITE_PASSED_DO` (other meteorite rows unchanged); `SEED_CONFIG["dispatch_task-meteorite"]` INSERT pairs match those alias keys; `ensure_meteorite_dispatch_tasks` inserts alias rows and, when both alias pairs are present, deletes only `grade_do`@`METEORITE_PASSED_JD` and `grade_get`@`METEORITE_PASSED_DO` (never `grade_do`@`PASSED_JD` / `grade_get`@`PASSED_DO`); classic Gaze dispatch keys remain untouched; `python3 -m py_compile` on the two files succeeds (repo venv: `~/astral/.venv/bin/python`).

1. In `src/utils/config.py`, in `METEORITE_DISPATCH_TASKS`, change only the two Do/Get entry `task_key` strings:

```python
    {
        "task_key": "meteorite_grade_do",
        "trigger_state": "METEORITE_PASSED_JD",
        "score_floor": 0.0,
        "auto_mode": False,
        "batch_size": 10,
        "min_count": 1,
        "freq_hrs": 0,
    },
    {
        "task_key": "meteorite_grade_get",
        "trigger_state": "METEORITE_PASSED_DO",
        "score_floor": 0.0,
        "auto_mode": False,
        "batch_size": 10,
        "min_count": 1,
        "freq_hrs": 0,
    },
```

Keep `score_floor` / `batch_size` / `auto_mode` / `min_count` / `freq_hrs` and the surrounding qualify / evaluate / like / upshot entries exactly as they are. Update the block comment above `METEORITE_DISPATCH_TASKS` so it no longer implies Do/Get share classic keys — note aliases + **AST-1222**.

2. In the same file, in `SEED_CONFIG["dispatch_task-meteorite"]`, retarget the two INSERT statements that currently seed `'grade_do'` / `'METEORITE_PASSED_JD'` and `'grade_get'` / `'METEORITE_PASSED_DO'`:

- SELECT / WHERE clauses: `'grade_do'` → `'meteorite_grade_do'`, `'grade_get'` → `'meteorite_grade_get'`.
- Leave trigger states, `score_floor` `0.0`, `batch_size` `10`, `batch_call_mode` `1`, `sort_by` `'latest_score'`, and all other meteorite INSERT strings unchanged.

⚠️ **Decision — catalog + SQL lockstep in one stage:** `METEORITE_DISPATCH_TASKS` is the live provision source; `SEED_CONFIG` is the SQL-first register (AST-1108, not executed yet). Both must name the same alias keys so they cannot drift. Do **not** invent a third alias map.

3. In `src/core/dispatcher.py`, after the existing `evaluate_jd`@`METEORITE_*` retirement block inside `ensure_meteorite_dispatch_tasks`, append alias Do/Get retirement. Re-list rows after inserts (the pre-loop `existing` snapshot is stale once new alias rows are saved):

```python
    # AST-1222: once alias Do/Get rows exist, drop shared-key meteorite triggers
    # (classic Gaze grade_do@PASSED_JD / grade_get@PASSED_DO stay).
    existing_after = {
        ((r.get("task_key") or "").strip(), (r.get("trigger_state") or "").strip())
        for r in database.list_dispatch_tasks_for_candidate(cid)
    }
    alias_do = ("meteorite_grade_do", "METEORITE_PASSED_JD")
    alias_get = ("meteorite_grade_get", "METEORITE_PASSED_DO")
    if alias_do in existing_after and alias_get in existing_after:
        for row in database.list_dispatch_tasks_for_candidate(cid):
            tk = (row.get("task_key") or "").strip()
            ts = (row.get("trigger_state") or "").strip()
            if (tk, ts) in {
                ("grade_do", "METEORITE_PASSED_JD"),
                ("grade_get", "METEORITE_PASSED_DO"),
            }:
                delete_dispatch_task(int(row["id"]))
                retired += 1
```

`retired` continues to accumulate with the evaluate_jd count. Update the function docstring to mention AST-1222 alias Do/Get retirement (keep the evaluate_jd / twin language).

⚠️ **Decision — retire only the two meteorite shared-key pairs, gated on both aliases present:** Mirrors AST-1209 twin-before-retire. Leaving orphan `grade_do`@`METEORITE_PASSED_JD` would dual-claim with the alias and still use Gaze `TASK_CONFIG` outcomes (broken after overlay deletion). Do **not** delete `grade_do`@`PASSED_JD` or `grade_get`@`PASSED_DO`. Do **not** rewrite existing row `task_key` in place — delete + insert (idempotent catalog insert already handles the alias side).

⚠️ **Decision — no new hardcoded frozenset of “meteorite shared keys” outside this function:** The retire set is the two literal pairs that this ticket replaces. Catalog authority remains `METEORITE_DISPATCH_TASKS`.

4. Verify:

```bash
~/astral/.venv/bin/python -c "
from src.utils import config as c
by = {(e['task_key'], e['trigger_state']): e for e in c.METEORITE_DISPATCH_TASKS}
assert ('meteorite_grade_do', 'METEORITE_PASSED_JD') in by
assert ('meteorite_grade_get', 'METEORITE_PASSED_DO') in by
assert ('grade_do', 'METEORITE_PASSED_JD') not in by
assert ('grade_get', 'METEORITE_PASSED_DO') not in by
assert ('meteorite_like', 'METEORITE_PASSED_GET') in by
assert ('evaluate_meteorite', 'METEORITE_QUALIFIED') in by
# Classic Gaze still uses shared keys at Gaze triggers (not in METEORITE_DISPATCH_TASKS)
assert c.TASK_CONFIG['grade_do']['pass_state'] == 'PASSED_DO'
assert c.is_task_alias('meteorite_grade_do')
sql = '\n'.join(c.SEED_CONFIG['dispatch_task-meteorite'])
assert \"'meteorite_grade_do', 'job',\" in sql
assert \"'meteorite_grade_get', 'job',\" in sql
assert \"'grade_do', 'job',\" not in sql
assert \"'grade_get', 'job',\" not in sql
assert \"task_key = 'meteorite_grade_do'\" in sql
assert \"task_key = 'meteorite_grade_get'\" in sql
"
~/astral/.venv/bin/python -m py_compile src/utils/config.py src/core/dispatcher.py
```

**Ritual:** `code(AST-1222): retarget meteorite Do/Get dispatch to alias keys`

## Stage 2: Grouping-only alias `agent_task` seed + AST-756 fixture

**Done when:** `data/admin/agent_task.json` and `docs/uat-fixtures/AST-756/expected-agent_task.json` each have current rows for `meteorite_grade_do` / `meteorite_grade_get` under **Meteorite Review** / `"4500"` with empty prompts and empty `run_next`; `meteorite_like` / `meteorite_upshot` seqs are `7` / `8`; classic Gaze `grade_do` / `grade_get` rows still **Gaze Review** / `"4000"` with prompts intact; current catalog count is **55**; JSON keeps `ensure_ascii=False` (literal em-dashes, no `\u2014` re-escape storm).

**Meteorite Review seq after this stage:**

| `task_key` | `task_group_name` | `task_group_order` | `task_seq` |
|------------|-------------------|--------------------|------------|
| `gaze_email` | `Meteorite Review` | `"4500"` | `1` (unchanged) |
| `meteorite_email` | `Meteorite Review` | `"4500"` | `2` (unchanged) |
| `qualify_meteorite` | `Meteorite Review` | `"4500"` | `3` (unchanged) |
| `evaluate_meteorite` | `Meteorite Review` | `"4500"` | `4` (unchanged) |
| `meteorite_grade_do` | `Meteorite Review` | `"4500"` | `5` (**new**) |
| `meteorite_grade_get` | `Meteorite Review` | `"4500"` | `6` (**new**) |
| `meteorite_like` | `Meteorite Review` | `"4500"` | `7` (was `5`) |
| `meteorite_upshot` | `Meteorite Review` | `"4500"` | `8` (was `6`) |

⚠️ **Decision — live section name is Meteorite Review:** Ticket notes said Job Review until AST-1183; on this tree AST-1219 already moved meteorite membership to **Meteorite Review** / `"4500"`. Seed aliases into that live section — do **not** invent Job Review rows.

⚠️ **Decision — renumber like/upshot seq only:** Inserting Do/Get at `5`/`6` mirrors classic Gaze GDL order (evaluate → do → get → like → upshot). Touch only `task_seq` on those two existing rows (no prompt / uuid / agent_id edits).

⚠️ **Decision — grouping-only rows (empty prompts, empty `run_next`, `agent_id` = `n/a`):** Parent AC: alias has no divergent prompt row; runtime loads master via **AST-1221** `resolve_task_key_for_content`. Match `gaze_email`-style non-prompt seed shape so Admin grouping works without a second prompt body. Do **not** copy `grade_do` / `grade_get` prompt text onto the alias.

1. Snapshot before edit (local `/tmp` only — do not commit):

```bash
cp data/admin/agent_task.json /tmp/agent_task.pre-ast-1222.json
cp docs/uat-fixtures/AST-756/expected-agent_task.json /tmp/expected-agent_task.pre-ast-1222.json
```

2. In `data/admin/agent_task.json`, for current `meteorite_like` / `meteorite_upshot` rows only, set `task_seq` to `7` and `8` respectively. Do not change any other field on those rows (prefer leaving `updated_at` untouched).

3. Append two new objects to the array (same field set as other rows). Use these exact identities:

**`meteorite_grade_do`:**

| Field | Value |
|-------|-------|
| `task_key_uuid` | `47e47cc0-26b8-4af6-81d6-f9e080b2b712` |
| `task_key` | `meteorite_grade_do` |
| `task_name` | `meteorite_grade_do` |
| `agent_id` | `n/a` |
| `task_group_name` | `Meteorite Review` |
| `task_group_order` | `"4500"` |
| `task_seq` | `5` |
| `current` | `1` |
| `run_next` | `""` |
| `system_prompt` | `""` |
| `cache_prompt` | `""` |
| `cache_prompt_b` | `""` |
| `cache_prompt_c` | `""` |
| `cache_prompt_d` | `""` |
| `nocache_prompt` | `""` |
| `user_prompt` | `""` |
| `updated_at` | `2026-08-06 08:00:00` |

**`meteorite_grade_get`:**

| Field | Value |
|-------|-------|
| `task_key_uuid` | `357b56de-20a6-4360-a98e-d4527db40b7f` |
| `task_key` | `meteorite_grade_get` |
| `task_name` | `meteorite_grade_get` |
| `agent_id` | `n/a` |
| `task_group_name` | `Meteorite Review` |
| `task_group_order` | `"4500"` |
| `task_seq` | `6` |
| `current` | `1` |
| `run_next` | `""` |
| all prompt fields | `""` |
| `updated_at` | `2026-08-06 08:00:00` |

Do **not** add `master_task_key` to the JSON row (that field lives on `TASK_CONFIG` only). Do **not** edit classic Gaze `grade_do` / `grade_get` rows.

4. Rewrite the file with `json.dump(..., indent=2, ensure_ascii=False)` + trailing newline (same convention as the current seed — literal Unicode in prompts elsewhere). Prefer a surgical Python edit that loads, mutates by `task_key`, and dumps — do **not** hand-edit megabytes of prompts.

5. In `docs/uat-fixtures/AST-756/expected-agent_task.json`, apply the **same** two new rows and the same `task_seq` bumps. Surgical only — **no** `cp` from catalog. Do not reconcile unrelated pre-existing catalog↔fixture prompt drift.

6. Verify:

```bash
~/astral/.venv/bin/python - <<'PY'
import json
from pathlib import Path

CLASSIC_DO_GET = {"grade_do", "grade_get"}
METEORITE_SEQ = {
    "gaze_email": 1,
    "meteorite_email": 2,
    "qualify_meteorite": 3,
    "evaluate_meteorite": 4,
    "meteorite_grade_do": 5,
    "meteorite_grade_get": 6,
    "meteorite_like": 7,
    "meteorite_upshot": 8,
}
ALIAS_UUID = {
    "meteorite_grade_do": "47e47cc0-26b8-4af6-81d6-f9e080b2b712",
    "meteorite_grade_get": "357b56de-20a6-4360-a98e-d4527db40b7f",
}
PROMPT_FIELDS = (
    "system_prompt", "cache_prompt", "cache_prompt_b", "cache_prompt_c",
    "cache_prompt_d", "nocache_prompt", "user_prompt",
)

def check(path: str) -> dict:
    text = Path(path).read_text(encoding="utf-8")
    assert "\\u2014" not in text[:8000] or "—" in text  # prefer literal emdash preserved
    rows = json.loads(text)
    by = {r["task_key"]: r for r in rows if r.get("current") == 1}
    assert len(by) == 55, (path, len(by))
    for k in CLASSIC_DO_GET:
        assert by[k]["task_group_name"] == "Gaze Review", (path, k)
        assert by[k]["task_group_order"] == "4000", (path, k)
        assert (by[k].get("cache_prompt") or "").strip() or (by[k].get("user_prompt") or "").strip(), (
            path, k, "classic prompts must remain non-empty"
        )
    for k, seq in METEORITE_SEQ.items():
        assert k in by, (path, k)
        assert by[k]["task_group_name"] == "Meteorite Review", (path, k, by[k]["task_group_name"])
        assert by[k]["task_group_order"] == "4500", (path, k)
        assert by[k]["task_seq"] == seq, (path, k, by[k]["task_seq"], seq)
    for k, uid in ALIAS_UUID.items():
        r = by[k]
        assert r["task_key_uuid"] == uid, (path, k, r["task_key_uuid"])
        assert r["task_name"] == k
        assert r["agent_id"] == "n/a"
        assert (r.get("run_next") or "") == ""
        for f in PROMPT_FIELDS:
            assert (r.get(f) or "") == "", (path, k, f)
    print("ok", path)
    return by

check("data/admin/agent_task.json")
check("docs/uat-fixtures/AST-756/expected-agent_task.json")
from src.utils import config as c
assert c.resolve_task_key_for_content("meteorite_grade_do") == "grade_do"
assert c.resolve_task_key_for_content("meteorite_grade_get") == "grade_get"
print("resolve still master-only: ok")
PY
```

**Ritual:** `code(AST-1222): seed meteorite_grade_do/get agent_task grouping rows`

## Self-Assessment

**Scope:** Single-Component — dispatch catalog + provision retirement + admin seed/fixture grouping; no runtime resolve rewrite.

**Conf:** high — siblings already shipped alias `TASK_CONFIG` + resolve; retarget/retire mirrors AST-1209 `evaluate_jd` pattern; grouping-only seed matches gaze_email empty-prompt shape; live section name is already Meteorite Review on tip.

**Risk:** Medium — missing retirement would leave dual meteorite Do/Get claim rows (shared key + alias); wrong seed prompts would fork content from the master (mitigated by empty prompts + resolve). Classic Gaze Do/Get must keep working at `PASSED_JD` / `PASSED_DO`.

## Code rules check

- §1.3 DRY — one catalog (`METEORITE_DISPATCH_TASKS`) drives provision; retire pairs are the two replaced keys only.
- §1.4 / `astral.standards.no-hardcoded-sets` — no new meteorite-only alias map; aliases already in `TASK_CONFIG` via `master_task_key`.
- `astral.seed.agent-tables-in-repo-json` — alias identities land in `data/admin/agent_task.json`.
- `astral.standards.in-scope-only` — no UI audit (**AST-1185**), no section rename (**AST-1183**), no resolve helpers (**AST-1220/1221**).
- `astral.standards.names-not-ticket-ids` — domain keys `meteorite_grade_do` / `meteorite_grade_get`.
- `astral.git.engineer-test-tree-ban` — no `tests/` / bible edits on this ticket.
- §3.3 imports — dispatcher already imports `METEORITE_DISPATCH_TASKS` / `TASK_CONFIG`; no new reverse imports.
