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
