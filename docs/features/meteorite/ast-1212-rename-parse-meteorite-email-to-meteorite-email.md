# AST-1212 — Rename parse_meteorite_email to meteorite_email

**Linear:** [AST-1212](https://linear.app/astralcareermatch/issue/AST-1212/rename-parse-meteorite-email-to-meteorite-email-rename-task-to)
**Parent:** [AST-1182](https://linear.app/astralcareermatch/issue/AST-1182/rename-task-to-meteorite-email-ai-payload-as-visible-textlinks) — Rename task to meteorite_email + AI payload as visible text/links
**Publish ref:** `origin/sub/AST-1182/AST-1212-rename-parse-meteorite-email-to-meteorite-email`

Domain rename only: product config task key, `agent_task` seed identity, and live callers resolve to `meteorite_email`. Parse modes (`html_links` / `subject_body`), response schema, and prompt wording stay intact under the new key. Does **not** change the AI live-payload shape (**AST-1213**), review groupings (**AST-1183**), or task aliases (**AST-1184**).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Rename `TASK_CONFIG` key + `METEORITE_EMAIL_PARSE_CONFIG["task_key"]` + `context_format` / `agent_task` literals to `meteorite_email`; refresh inventory/comments that still name the old live key | utils |
| `data/admin/agent_task.json` | Rename the current Ruth row `task_key` / `task_name` to `meteorite_email` (prompts/grouping/`task_key_uuid` unchanged) | data/admin |
| `docs/uat-fixtures/AST-756/expected-agent_task.json` | Surgical sync of that same row’s `task_key` / `task_name` (and `updated_at` if bumped) — **no** whole-file `cp` | docs |

**No changes expected:** `src/core/gaze_email.py` (already calls `do_task` with `METEORITE_EMAIL_PARSE_CONFIG["task_key"]`), `src/core/agent.py`, `src/core/consult.py`, `src/core/gazer.py`, dispatcher, Gmail external, frontend, `METEORITE_DISPATCH_TASKS`, `tests/` / bible (Betty after Code Complete). Do **not** add a compat alias or dual old/new key list.

## Stage 1: Config — live task key `meteorite_email`

**Done when:** `METEORITE_EMAIL_PARSE_CONFIG["task_key"] == "meteorite_email"`; that key exists in `TASK_CONFIG` with the same response schema / meta as today (including `requires_candidate_key is True`, `entity_type is None`, `trigger_state is None`); `parse_meteorite_email` is absent from `TASK_CONFIG` and from `METEORITE_EMAIL_PARSE_CONFIG`; `python3 -m py_compile src/utils/config.py` succeeds (use repo venv if needed: `~/astral/.venv/bin/python`).

1. In `src/utils/config.py`, locate the inventory comment line for `METEORITE_EMAIL_PARSE_CONFIG` (near other meteorite / email ingest bullets). Update wording so it describes the Ruth meteorite-email parse task key as `meteorite_email` (may still cite AST-1089 origin + AST-1212 rename). Do **not** invent a second config block name.

2. In `TASK_CONFIG`, rename the dict key `"parse_meteorite_email"` → `"meteorite_email"` (same position: immediately after `"qualify_meteorite"`). Inside that block, set:
   - `"context_format": "meteorite_email_{index}"`
   - `"agent_task": "meteorite_email"`
   - Leave `response_format`, `output_type`, `scored`, `response_schema` (including `parse_mode`, `jobs` / `metadata` dict, `jd_link`, `content_text`), `entity_type`, `requires_candidate_key`, and `trigger_state` **byte-identical** to the pre-rename values (types and required flags unchanged).

3. Update the block’s leading comments so they name `meteorite_email` as the live key (keep AST-1089 / AST-1090 historical pointers; note AST-1212 rename). Do **not** change call-site guidance: AST-1090 / `gaze_email` still uses `METEORITE_EMAIL_PARSE_CONFIG["task_key"]`.

4. In `METEORITE_EMAIL_PARSE_CONFIG`, set `"task_key": "meteorite_email"`. Leave `"parse_modes": ("html_links", "subject_body")` unchanged. Keep the existing asserts:

```python
assert METEORITE_EMAIL_PARSE_CONFIG["task_key"] in TASK_CONFIG
assert set(METEORITE_EMAIL_PARSE_CONFIG["parse_modes"]) == {"html_links", "subject_body"}
```

5. Grep `src/utils/config.py` for `parse_meteorite_email`. Remove or rewrite any remaining **live** identity string (dict keys, `task_key` / `agent_task` / `context_format` values). Historical “formerly …” prose in comments is allowed; a live `"parse_meteorite_email"` string value or `TASK_CONFIG` key is not.

6. Do **not** add `meteorite_email` to `METEORITE_DISPATCH_TASKS`, `_DISPATCH_BATCH_CALL_MODE_ONE`, or `_dispatch_trigger_state_for_task_key`. Do **not** leave a shim key `parse_meteorite_email` alongside the new one.

⚠️ **Decision — no compat alias:** Parent AC requires `parse_meteorite_email` absent as a live product key. Callers already read `METEORITE_EMAIL_PARSE_CONFIG["task_key"]`; a dual-key list would violate `astral.standards.no-hardcoded-sets` and the rename AC.

⚠️ **Decision — leave `gaze_email.py` untouched:** `_ruth_parse` already passes `task_key=METEORITE_EMAIL_PARSE_CONFIG["task_key"]`. Renaming the config value flips the live call path without a core edit (config source of truth).

**Done when (recheck):**

```bash
~/astral/.venv/bin/python -c "
from src.utils import config as c
assert c.METEORITE_EMAIL_PARSE_CONFIG['task_key'] == 'meteorite_email'
assert 'parse_meteorite_email' not in c.TASK_CONFIG
t = c.TASK_CONFIG['meteorite_email']
assert t['agent_task'] == 'meteorite_email'
assert t['context_format'] == 'meteorite_email_{index}'
assert t['requires_candidate_key'] is True
assert t['entity_type'] is None
assert t['trigger_state'] is None
assert set(c.METEORITE_EMAIL_PARSE_CONFIG['parse_modes']) == {'html_links', 'subject_body'}
assert all(e.get('task_key') != 'meteorite_email' for e in c.METEORITE_DISPATCH_TASKS)
"
~/astral/.venv/bin/python -m py_compile src/utils/config.py
```

**Ritual:** `code(AST-1212): config task key meteorite_email`

## Stage 2: Repo `agent_task` identity + surgical AST-756 fixture sync

**Done when:** `data/admin/agent_task.json` has exactly one `current: 1` row with `task_key == "meteorite_email"` and `task_name == "meteorite_email"` (`college_intern_ruth`); no current row still uses `parse_meteorite_email`; prompts / grouping / `task_key_uuid` / `task_seq` / `agent_id` match the pre-rename row except identity fields (+ `updated_at` if bumped); the AST-756 fixture’s matching row has the same `task_key` / `task_name` (/`updated_at`); catalog vs fixture still differ only by the pre-existing missing `evaluate_meteorite` + `craft_evaluate_meteorite_rubric` rows (53 vs 51) — this stage does not absorb that drift.

1. Snapshot before edit (local `/tmp` only — do not commit):

```bash
cp data/admin/agent_task.json /tmp/agent_task.pre-ast-1212.json
cp docs/uat-fixtures/AST-756/expected-agent_task.json /tmp/expected-agent_task.pre-ast-1212.json
```

2. In `data/admin/agent_task.json`, locate the single object with `task_key == "parse_meteorite_email"` and `current == 1`. Set:
   - `task_key` → `"meteorite_email"`
   - `task_name` → `"meteorite_email"` (AST-1107 law: `task_name == task_key`)
   - Optionally bump `updated_at` to current UTC matching neighboring row format (`YYYY-MM-DD HH:MM:SS`)
   - Do **not** change `task_key_uuid`, `agent_id`, `task_group_order`, `task_group_name`, `task_seq`, `cache_prompt`, `user_prompt`, or empty prompt slots (`system_prompt`, `cache_prompt_b/c/d`, `nocache_prompt`, `run_next`).
   - Do **not** edit any other row.

3. **Surgical fixture sync (no whole-file `cp`):** in `docs/uat-fixtures/AST-756/expected-agent_task.json`, find the object with `task_key == "parse_meteorite_email"` and `current == 1` and set its `task_key`, `task_name`, and `updated_at` to the **exact same strings** as the catalog row just edited. Do **not** `cp` the whole catalog over the fixture. Do **not** add missing fixture rows (`evaluate_meteorite`, `craft_evaluate_meteorite_rubric`) or rewrite other tasks.

⚠️ **Decision — leave inherited fixture drift alone:** Catalog has 53 current rows; AST-756 fixture has 51 (missing `evaluate_meteorite` + `craft_evaluate_meteorite_rubric`) plus unrelated shared-row drift. Blind `cp` would absorb that under this ticket. Same stance as AST-1196.

⚠️ **Decision — prompts unchanged:** Prompt body still says “meteorite email parse” in prose; that is fine. Rewriting prompts / live payload for visible text+links is **AST-1213**.

4. Verify only identity fields moved on the target row; no other catalog/fixture rows changed:

```bash
~/astral/.venv/bin/python - <<'PY'
import json
from pathlib import Path

def load(p):
    return json.loads(Path(p).read_text())

def by_uuid(rows):
    return {r["task_key_uuid"]: r for r in rows}

for label, pre, post in (
    ("catalog", "/tmp/agent_task.pre-ast-1212.json", "data/admin/agent_task.json"),
    ("fixture", "/tmp/expected-agent_task.pre-ast-1212.json", "docs/uat-fixtures/AST-756/expected-agent_task.json"),
):
    a, b = by_uuid(load(pre)), by_uuid(load(post))
    assert set(a) == set(b), label
    changed = [u for u in a if a[u] != b[u]]
    assert len(changed) == 1, (label, changed)
    old, new = a[changed[0]], b[changed[0]]
    assert old["task_key"] == "parse_meteorite_email"
    assert new["task_key"] == new["task_name"] == "meteorite_email"
    # prompts / grouping / uuid / seq / agent unchanged
    for k in (
        "task_key_uuid", "agent_id", "task_group_order", "task_group_name",
        "task_seq", "cache_prompt", "user_prompt", "system_prompt",
        "cache_prompt_b", "cache_prompt_c", "cache_prompt_d",
        "nocache_prompt", "run_next", "current",
    ):
        assert old.get(k) == new.get(k), (label, k)

cat = load("data/admin/agent_task.json")
fix = load("docs/uat-fixtures/AST-756/expected-agent_task.json")
assert len(cat) == 53 and len(fix) == 51
assert not any(r.get("task_key") == "parse_meteorite_email" for r in cat)
assert not any(r.get("task_key") == "parse_meteorite_email" for r in fix)
cm = next(r for r in cat if r["task_key"] == "meteorite_email" and r.get("current") == 1)
fm = next(r for r in fix if r["task_key"] == "meteorite_email" and r.get("current") == 1)
assert cm["task_name"] == fm["task_name"] == "meteorite_email"
assert cm["updated_at"] == fm["updated_at"]
assert cm["cache_prompt"] == fm["cache_prompt"]
print("OK")
PY
```

5. Confirm product `src/` has no live old key (comments in historical feature docs / tests are out of scope):

```bash
rg -n 'parse_meteorite_email' src/ data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json
# expect: zero matches (or only historical comment prose if any remain — fix those if they are string literals used as keys)
~/astral/.venv/bin/python -c "
from src.utils import config as c
assert c.METEORITE_EMAIL_PARSE_CONFIG['task_key'] == 'meteorite_email'
# known call path: gaze_email resolves via config (no hardcoded old key)
import ast, pathlib
src = pathlib.Path('src/core/gaze_email.py').read_text()
assert 'parse_meteorite_email' not in src
assert 'METEORITE_EMAIL_PARSE_CONFIG' in src
print('caller path OK')
"
```

**Ritual:** `code(AST-1212): agent_task identity meteorite_email`

## Self-Assessment

**Scope:** `Single-Component` — utils config identity + one Ruth `agent_task` seed row (+ surgical AST-756 fixture sync); core caller already config-driven and stays untouched.

**Conf:** `high` — mechanical rename with an established config→`do_task` path (`gaze_email._ruth_parse`); parse modes / schema / prompts frozen for sibling AST-1213.

**Risk:** `Medium` — a missed live string would break Ruth lookup on the gaze_email hop; blast radius is that parse path, not dispatch claim / qualify / evaluate meteorite GDL.

## ASTRAL_CODE_RULES self-review

- **§1.1 / in-scope-only:** Stages touch only the rename files; payload, groupings, aliases, and `tests/` excluded.
- **§1.4 / no-hardcoded-sets:** No dual old/new key lists; single config `task_key`.
- **§2.1 / config-source-of-truth:** Live key lives in `TASK_CONFIG` + `METEORITE_EMAIL_PARSE_CONFIG`; callers keep reading config.
- **§2.2 / do-task-delegation:** `gaze_email` continues to call `do_task` with the config task key — no new Anthropic assembly in core.
- **§3.5 / names-not-ticket-ids:** Domain key `meteorite_email`, not ticket-scoped names.
- **Seed / agent tables in repo JSON:** Catalog row identity renames with the product key; fixture surgically synced without absorbing 53↔51 drift.
- **§3.3 imports / layers:** No new imports or layer crossings.
- **Betty test-tree ban:** No edits under `tests/` or `docs/test-bible/**` — expected component asserts on the old key are Betty’s post–Code Complete work.
