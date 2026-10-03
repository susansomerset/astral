# AST-1958 — Run-once migration of live agent rows

- **Ticket:** [AST-1958](https://linear.app/astralcareermatch/issue/AST-1958) · **Parent:** [AST-1953](https://linear.app/astralcareermatch/issue/AST-1953) Refactor agent settings and ingest per-endpoint model options
- **Publish ref:** `sub/AST-1953/AST-1958-migrate-agent-settings` (origin only)
- **Canon Scope:** none (the script is under `scripts/`, outside every directive's scope)

One operator CLI, `scripts/migrations/remap_agent_settings.py`, moves every live agent row onto AST-1955's plain settings and per-SKU model ids, then drops the retired `brain_setting` and `mode` columns. It runs once per environment, right after the AST-1953 deploy. The default is a dry run that prints each row's planned change and writes nothing; `--apply` writes the Functional scope 8 values and drops both columns in the same transaction. Everything it knows about the old world (per-SKU ids, which models could think, mode temperatures) is a literal 2026-10-03 snapshot inside the script, because AST-1955 removed those config symbols. AST-1950's superseded script (`remap_openrouter_agents.py`) is deleted; it imports `AGENT_MODE_*` / `BRAIN_BIG`, which no longer exist. No product code changes.

## Scope gate

Every file below is named in this ticket's `## Scope`. The two deletions under `tests/` and `docs/test-bible/` and the two new test/bible files are Betty's (`qa-child`): the pre-commit hook blocks engineer commits there.

| Scope line | Who | Where |
|---|---|---|
| `scripts/migrations/remap_agent_settings.py` (new) | Katherine | Stage 1 |
| `scripts/migrations/remap_openrouter_agents.py` (deleted) | Katherine | Stage 1 |
| `tests/component/scripts/test_remap_openrouter_agents.py`, `docs/test-bible/dev/remap_openrouter_agents.md` (deleted) | Betty, `qa-child` | — (it collects against a deleted script once Stage 1 lands; see **Sequencing**) |
| `tests/component/scripts/test_remap_agent_settings.py`, `docs/test-bible/dev/remap_agent_settings.md` (new) | Betty, `qa-child` | — |

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `scripts/migrations/remap_agent_settings.py` | **New.** Run-once CLI: `SKU_IDS` (6 rows), `CAN_THINK` (58 ids), `MODE_TEMPERATURE`, `main(argv=None) -> int` | scripts |
| `scripts/migrations/remap_openrouter_agents.py` | **Deleted** (AST-1950, superseded) | scripts |

## Old-world rules the script reproduces (from `origin/dev` @ AST-1947 config, not a step)

- **Thinking today:** `resolve_model_brain` set `thinking = AGENT_MODE_CONFIG[mode]["thinking"] and model["can_think"]`, so a call thought only on **Creative** and only where `can_think` was True.
- **Temperature today:** `llm_compat` sent the mode's temperature (Deterministic 0.2, Creative 0.6) only when the call was **not** thinking.
- **Thinking-off today:** when not thinking, `llm_compat` sent the server's `thinking_off_params` (`{"thinking": {"type": "disabled"}}` on kimi / openrouter / deepseek). Functional scope 8 maps that to `reasoning_effort: "none"` **only on a model that can think**. DeepSeek direct (`can_think` False) and Claude (`thinking_off_params` empty) therefore get no effort.
- **`can_think` snapshot:** `kimi-k2.6` True; `claude` and `deepseek-v4` False; each OpenRouter slug = the `reasoning-capable` column of the AST-1947 `OPENROUTER_MODEL_TABLE` (57 True of 95). Total 58 ids.
- **Output floors:** `deepseek-v4` Big had `max_tokens_floor` 384000 applied over the agent's own value → "at least 384000". `kimi-k2.6` Big defaulted to 32000; the new `kimi-k2.6` entry defaults to 16000, so only Big rows with **empty** `max_tokens` get 32000.

## Stage 1: Migration script; retire AST-1950's script

**Done when:** the new script exists and AST-1950's is gone. Against a temp DB with `brain_setting` / `mode` columns and AC 11's six rows, a dry run prints six planned changes and leaves rows **and** columns untouched (no setting columns added). `--apply` produces exactly AC 11's values, and `PRAGMA table_info(agent)` lists no `brain_setting` or `mode`. A second run prints `brain_setting / mode already dropped. Nothing to migrate.` and exits 0.

1. Create `scripts/migrations/remap_agent_settings.py` with **exactly** the content below.

```python
#!/usr/bin/env python3
"""Move live agent rows to plain settings and per-SKU model ids, then drop brain_setting and mode (AST-1958).

Run once per environment, right after the AST-1953 deploy. Default is a dry run that prints every
row's planned change; --apply writes them and drops the two retired columns in one transaction.
A second run finds the columns gone and changes nothing.

  1. Rows with no mode (AST-1950 never ran) count as Big -> Creative, else Deterministic.
  2. claude / deepseek-v4 move to their per-SKU ids; deepseek-v4 Big gets max_tokens >= 384000;
     kimi-k2.6 Big with empty max_tokens gets 32000 (today's Big default).
  3. Settings = what the call sent on 2026-10-03: temperature 0.2 (Deterministic) / 0.6 (Creative),
     empty where the call thought; reasoning_effort "none" where it sent thinking-off on a model
     that can think; provider_allow_fallbacks true; every other setting empty.

Usage:
  python scripts/migrations/remap_agent_settings.py
  python scripts/migrations/remap_agent_settings.py --apply
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.data.database import _ensure_agent_schema, _get_connection

# Snapshot 2026-10-03: (old model id, brain size) -> per-SKU model id. Literal on purpose:
# later catalog edits must not change what this one-time migration does.
SKU_IDS = {
    ("claude", "Little"): "claude-haiku-4-5",
    ("claude", "Medium"): "claude-sonnet-4-6",
    ("claude", "Big"): "claude-opus-4-6",
    ("deepseek-v4", "Little"): "deepseek-v4-flash",
    ("deepseek-v4", "Medium"): "deepseek-v4-pro",
    ("deepseek-v4", "Big"): "deepseek-v4-pro",
}
# Snapshot 2026-10-03: model ids whose catalog entry had can_think True. Every other id could not think.
CAN_THINK = frozenset({
    "apodex/apodex-1.1-mini:free",
    "bytedance-seed/seed-1.6",
    "bytedance-seed/seed-1.6-flash",
    "bytedance-seed/seed-2-1-turbo",
    "bytedance-seed/seed-2.0-code",
    "bytedance-seed/seed-2.0-lite",
    "bytedance-seed/seed-2.0-mini",
    "deepseek/deepseek-chat-v3.1",
    "deepseek/deepseek-r1-0528",
    "deepseek/deepseek-v3.1-terminus",
    "deepseek/deepseek-v3.2",
    "deepseek/deepseek-v3.2-exp",
    "deepseek/deepseek-v4-flash",
    "deepseek/deepseek-v4-flash-0731",
    "deepseek/deepseek-v4-flash-vision-exp",
    "deepseek/deepseek-v4.1-flash",
    "google/gemma-4-26b-a4b-it",
    "google/gemma-4-31b-it",
    "ibm-granite/granite-4.2-8b",
    "inclusionai/ling-3.0-flash-fin",
    "inclusionai/ling-3.0-flash-vl",
    "kimi-k2.6",
    "meta/muse-glimmer-30b",
    "minimax/minimax-m3",
    "moonshotai/kimi-k2-thinking",
    "moonshotai/kimi-k2.5",
    "moonshotai/kimi-k2.6",
    "moonshotai/kimi-k2.7-code",
    "nvidia/nemotron-3-nano-30b-a3b",
    "nvidia/nemotron-3-super-120b-a12b",
    "nvidia/nemotron-3-ultra-550b-a55b",
    "nvidia/nemotron-3.5-lightning",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "qwen/qwen3-14b",
    "qwen/qwen3-30b-a3b",
    "qwen/qwen3-32b",
    "qwen/qwen3-vl-30b-a3b-thinking",
    "qwen/qwen3.5-27b",
    "qwen/qwen3.5-35b-a3b",
    "qwen/qwen3.5-397b-a17b",
    "qwen/qwen3.5-9b",
    "qwen/qwen3.6-27b",
    "qwen/qwen3.6-35b-a3b",
    "qwen/qwen3.8-27b",
    "qwen/qwen3.8-27b:free",
    "stepfun/step-3.7-flash",
    "tencent/hunyuan-a13b-instruct",
    "tencent/hy3",
    "xiaomi/mimo-v2.5",
    "xiaomi/mimo-v2.6-flash",
    "xiaomi/mimo-v2.6-pro",
    "z-ai/glm-4.6",
    "z-ai/glm-4.7",
    "z-ai/glm-4.7-flash",
    "z-ai/glm-5.2",
    "z-ai/glm-5.3",
    "z-ai/glm-5.3-flash",
})
# Snapshot 2026-10-03: AGENT_MODE_CONFIG temperatures.
MODE_TEMPERATURE = {"Deterministic": 0.2, "Creative": 0.6}


def main(argv=None) -> int:
    apply = "--apply" in (sys.argv[1:] if argv is None else argv)
    conn = _get_connection()
    cols = {r[1] for r in conn.execute("PRAGMA table_info(agent)").fetchall()}
    if not {"brain_setting", "mode"} <= cols:
        print("brain_setting / mode already dropped. Nothing to migrate.")
        conn.close()
        return 0
    rows = conn.execute(
        "SELECT agent_id, model_id, brain_setting, mode, max_tokens FROM agent ORDER BY agent_id"
    ).fetchall()
    changes = []
    for agent_id, model_id, brain, mode, max_tokens in rows:
        mode = mode or ("Creative" if brain == "Big" else "Deterministic")
        # Today's call thinks only on Creative and only where the model can think.
        thinks = mode == "Creative" and model_id in CAN_THINK
        new_max = max_tokens
        if (model_id, brain) == ("deepseek-v4", "Big"):
            new_max = max(max_tokens or 0, 384000)
        elif (model_id, brain) == ("kimi-k2.6", "Big") and max_tokens is None:
            new_max = 32000
        new_model_id = SKU_IDS.get((model_id, brain), model_id)
        temperature = None if thinks else MODE_TEMPERATURE[mode]
        effort = "none" if model_id in CAN_THINK and not thinks else None
        print(
            f"  {agent_id}: {model_id}/{brain}/{mode} max_tokens={max_tokens} -> {new_model_id} "
            f"max_tokens={new_max} temperature={temperature} reasoning_effort={effort}"
        )
        changes.append((new_model_id, new_max, temperature, effort, agent_id))

    if not apply:
        print(f"\n{len(changes)} row(s) would change, then brain_setting and mode would be dropped. "
              "Re-run with --apply to commit.")
    else:
        # Setting columns must exist before the UPDATE (DDL only, idempotent); dry runs stay read-only.
        _ensure_agent_schema(conn)
        conn.executemany(
            """UPDATE agent SET model_id = ?, max_tokens = ?, quantization = NULL, temperature = ?,
                   reasoning_effort = ?, provider_allow_fallbacks = 1, provider_only = NULL,
                   provider_ignore = NULL, provider_sort = NULL, updated_at = CURRENT_TIMESTAMP
               WHERE agent_id = ?""",
            changes,
        )
        # Same transaction as the UPDATE: a failed drop leaves nothing half-migrated.
        for col in ("brain_setting", "mode"):
            conn.execute(f"ALTER TABLE agent DROP COLUMN {col}")
        conn.commit()
        print(f"\nUpdated {len(changes)} row(s); dropped brain_setting and mode.")
    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

   ⚠️ **Decision:** raw SQL over `_get_connection()`, like AST-1950's script, rather than `update_agent`. One `executemany` UPDATE plus two `ALTER TABLE agent DROP COLUMN` run in **one** transaction (Python's default sqlite3 transaction mode: DML opens it, DDL does not commit it), committed once. A failed drop leaves the table untouched. Both columns are plain `TEXT` with no index or CHECK, so SQLite 3.35+ `DROP COLUMN` applies (same as AST-1948's `model_code` drop).

   ⚠️ **Decision:** `_ensure_agent_schema(conn)` runs **only** on `--apply`, before the UPDATE. The script may run before the app has started once on the new code, so the setting columns may not exist yet. The dry run reads only `agent_id, model_id, brain_setting, mode, max_tokens`, so it needs no DDL and stays strictly read-only (AC 11: "a dry run writes nothing").

   ⚠️ **Decision:** every row is written with all seven settings (`quantization`, `provider_only`, `provider_ignore`, `provider_sort` explicitly NULL; `provider_allow_fallbacks` = 1). Functional scope 8 says "everything else empty". Writing them explicitly keeps the outcome fixed even if the app wrote something between deploy and run. No derived quantization (Susan).

   ⚠️ **Decision:** rows on ids outside `SKU_IDS` keep their `model_id` (OpenRouter slugs, `kimi-k2.6`, already-per-SKU ids). A `claude` / `deepseek-v4` row with an unexpected `brain_setting` also keeps its id; it's visible in the dry-run line and fails to resolve at call time like any unknown id. No catalog validation, no vocabulary checks (Susan: "code it loosely"). An unknown non-null `mode` raises `KeyError` on `MODE_TEMPERATURE`, so the dry run surfaces it before anything writes.

   ⚠️ **Decision:** idempotence is by column presence. Once `brain_setting` and `mode` are gone there is nothing left to derive from, so a second run reports and exits 0.

2. Delete `scripts/migrations/remap_openrouter_agents.py` (`git rm`).

3. Compile: `.venv/bin/python -m py_compile scripts/migrations/remap_agent_settings.py`.

4. Hand check (temp DB, not committed): with `ASTRAL_DB_DIR=$(mktemp -d)`, create `agent (agent_id TEXT PRIMARY KEY, content TEXT, model_id TEXT, brain_setting TEXT, mode TEXT, max_tokens INTEGER, updated_at TIMESTAMP)`, insert AC 11's rows, and run `main([])`, then `main(["--apply"])`, then `main(["--apply"])`. Expected after apply:

   | Seed row | `model_id` | `max_tokens` | `temperature` | `reasoning_effort` |
   |---|---|---|---|---|
   | `claude` Medium Deterministic | `claude-sonnet-4-6` | (unchanged) | 0.2 | NULL |
   | `deepseek-v4` Big Creative | `deepseek-v4-pro` | ≥ 384000 | 0.6 | NULL |
   | `kimi-k2.6` Big Creative, `max_tokens` NULL | `kimi-k2.6` | 32000 | NULL | NULL |
   | `z-ai/glm-4.6` Deterministic | `z-ai/glm-4.6` | (unchanged) | 0.2 | `none` |
   | `microsoft/phi-4` Creative | `microsoft/phi-4` | (unchanged) | 0.6 | NULL |
   | null `mode`, Big, on a thinking model (e.g. `openai/gpt-oss-120b`) | unchanged | (unchanged) | NULL (Creative + thinks) | NULL |

   Every row: `quantization` NULL, `provider_allow_fallbacks` 1, `provider_only` / `provider_ignore` / `provider_sort` NULL. Commit as `code(AST-1958): run-once agent settings migration; retire AST-1950 remap script`.

## Sequencing (for Betty / Chuckles, not a step)

- After Stage 1, `tests/component/scripts/test_remap_openrouter_agents.py` loads a missing file and fails. Betty deletes it and `docs/test-bible/dev/remap_openrouter_agents.md` in `qa-child`, per this ticket's Scope.
- The migration needs AST-1955's setting columns, which are already on `ftr/AST-1953-agent-settings` and merged into this sub. It touches no file AST-1955/1956/1957 owns.
- Operators run it after the AST-1953 deploy. Until then live agents send no temperature or effort, and rows on `claude` / `deepseek-v4` fail to resolve (parent **Sequencing**).

## Estimate

Confirm Chuckles estimate: 2 — agree

## Revisions


## Joan validate

[plan-rubric] PROCEED (Commit: eb7e78caa) Migration plan complete

**Ticket:** AST-1958  
**Overall:** APPROVED  
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51  
**Publish ref:** `sub/AST-1953/AST-1958-migrate-agent-settings` @ `eb7e78caa570a9797619ca3d659ae80991fd6300`

## Canon scores

*(Frozen Canon Scope: none — ticket **Citations** and parent **Architectural definition** place `scripts/migrations/` outside directive territory; no ids to grade.)*

## Traceability

11 → Stage 1 (verbatim script, done-when gates, hand-check table vs parent AC 11 bullets) · parent Functional scope 8 → old-world rules + script snapshot + Stage 1 apply path

## Findings

### discuss

- **Location:** Child AC 11 seed row “one row with null `mode`” vs Stage 1 hand-check table
- **Finding:** Ticket does not fix `brain_setting` / `model_id` for that row; migration outcome depends on them (`null` mode → Creative only when `brain == "Big"`). Plan documents one concrete case (Big + thinking OpenRouter slug).
- **Recommendation:** Betty’s component test should match that hand-check row (or document an alternate seed if Susan wants null-mode on Little/Medium).

### acceptable

- **Location:** Plan structure — no `## Self-assessment`
- **Finding:** Estimate confirm + staged done-when + **Sequencing** carry risk; appropriate for a single-script child.
- **Recommendation:** None blocking.

- **Location:** Stage 1 — `_ensure_agent_schema(conn)` only on `--apply`
- **Finding:** Matches AST-1955 DDL-only ensure on `ftr`; dry run stays read-only on legacy columns only, satisfying AC 11 “dry run writes nothing.”
- **Recommendation:** None.

- **Location:** **Sequencing**
- **Finding:** `test_remap_openrouter_agents.py` collection break until Betty deletes per Scope is explicit.
- **Recommendation:** None.

context_tokens≈58000

## Review

- **Branch:** `sub/AST-1953/AST-1958-migrate-agent-settings`
- **Build commits:** `1960e4902` (Stage 1 migration script; AST-1950 script deleted)
- **Build notes:** Stage 1 executed as written: script extracted verbatim from the plan block, compiled, `ruff check` clean, step 4 hand check on a temp SQLite DB matched every row of the expected table (dry run left rows and columns untouched; `--apply` dropped `brain_setting` / `mode`; second run reported nothing to migrate). No deviations. `tests/component/scripts/test_remap_openrouter_agents.py` and its bible are Betty's to delete (see **Sequencing**).
