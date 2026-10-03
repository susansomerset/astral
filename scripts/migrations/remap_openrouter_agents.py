#!/usr/bin/env python3
"""Remap agent rows onto the AST-1946 catalog: starting modes, new OpenRouter sizes, Kimi fold.

Run once per environment, right after the AST-1946 deploy (needs the agent `mode` column
from AST-1948). Default is a dry run that prints every planned change and every row on a
removed model; --apply writes. Idempotent: a second run finds nothing to change.

  1. mode: every row with no mode gets Big -> Creative, else Deterministic, judged on the
     row's brain_setting before remap.
  2. OpenRouter rows: brain_setting moves to the slug's one new size; kimi-k2.6-openrouter
     rows move to moonshotai/kimi-k2.6 / Little.
Rows on removed models and direct-model rows keep their model and size.

Usage:
  python scripts/migrations/remap_openrouter_agents.py
  python scripts/migrations/remap_openrouter_agents.py --apply
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.data.database import _get_connection
from src.utils.config import AGENT_MODE_CREATIVE, AGENT_MODE_DETERMINISTIC, BRAIN_BIG

# Snapshot 2026-10-03: pre-epic OpenRouter model id -> (AST-1946 model id, its one brain size).
# Literal on purpose: later catalog edits must not change what this one-time remap does.
REMAP = {
    "bytedance-seed/seed-1.6": ("bytedance-seed/seed-1.6", "Medium"),
    "bytedance-seed/seed-1.6-flash": ("bytedance-seed/seed-1.6-flash", "Medium"),
    "bytedance-seed/seed-2-1-turbo": ("bytedance-seed/seed-2-1-turbo", "Medium"),
    "bytedance-seed/seed-2.0-code": ("bytedance-seed/seed-2.0-code", "Medium"),
    "bytedance-seed/seed-2.0-lite": ("bytedance-seed/seed-2.0-lite", "Medium"),
    "bytedance-seed/seed-2.0-mini": ("bytedance-seed/seed-2.0-mini", "Medium"),
    "deepseek/deepseek-chat-v3-0324": ("deepseek/deepseek-chat-v3-0324", "Medium"),
    "deepseek/deepseek-chat-v3.1": ("deepseek/deepseek-chat-v3.1", "Little"),
    "deepseek/deepseek-r1-0528": ("deepseek/deepseek-r1-0528", "Medium"),
    "deepseek/deepseek-v3.1-terminus": ("deepseek/deepseek-v3.1-terminus", "Medium"),
    "deepseek/deepseek-v3.2": ("deepseek/deepseek-v3.2", "Medium"),
    "deepseek/deepseek-v3.2-exp": ("deepseek/deepseek-v3.2-exp", "Medium"),
    "deepseek/deepseek-v4-flash": ("deepseek/deepseek-v4-flash", "Medium"),
    "deepseek/deepseek-v4-flash-0731": ("deepseek/deepseek-v4-flash-0731", "Medium"),
    "deepseek/deepseek-v4-flash-vision-exp": ("deepseek/deepseek-v4-flash-vision-exp", "Medium"),
    "deepseek/deepseek-v4.1-flash": ("deepseek/deepseek-v4.1-flash", "Little"),
    "google/gemma-3-27b-it": ("google/gemma-3-27b-it", "Medium"),
    "google/gemma-4-26b-a4b-it": ("google/gemma-4-26b-a4b-it", "Medium"),
    "google/gemma-4-31b-it": ("google/gemma-4-31b-it", "Little"),
    "gryphe/mythomax-l2-13b": ("gryphe/mythomax-l2-13b", "Big"),
    "meta-llama/llama-3.1-70b-instruct": ("meta-llama/llama-3.1-70b-instruct", "Medium"),
    "meta-llama/llama-3.3-70b-instruct": ("meta-llama/llama-3.3-70b-instruct", "Medium"),
    "meta-llama/llama-4-maverick": ("meta-llama/llama-4-maverick", "Medium"),
    "meta-llama/llama-4-scout": ("meta-llama/llama-4-scout", "Medium"),
    "mistralai/mistral-nemo": ("mistralai/mistral-nemo", "Medium"),
    "mistralai/mistral-small-24b-instruct-2501": ("mistralai/mistral-small-24b-instruct-2501", "Medium"),
    "mistralai/mistral-small-3.2-24b-instruct": ("mistralai/mistral-small-3.2-24b-instruct", "Medium"),
    "moonshotai/kimi-k2-0905": ("moonshotai/kimi-k2-0905", "Medium"),
    "nousresearch/hermes-3-llama-3.1-70b": ("nousresearch/hermes-3-llama-3.1-70b", "Medium"),
    "nvidia/nemotron-3-nano-30b-a3b": ("nvidia/nemotron-3-nano-30b-a3b", "Medium"),
    "nvidia/nemotron-3-super-120b-a12b": ("nvidia/nemotron-3-super-120b-a12b", "Medium"),
    "openai/gpt-oss-120b": ("openai/gpt-oss-120b", "Big"),
    "openai/gpt-oss-20b": ("openai/gpt-oss-20b", "Little"),
    "qwen/qwen-2.5-72b-instruct": ("qwen/qwen-2.5-72b-instruct", "Medium"),
    "qwen/qwen3-14b": ("qwen/qwen3-14b", "Little"),
    "qwen/qwen3-235b-a22b-2507": ("qwen/qwen3-235b-a22b-2507", "Medium"),
    "qwen/qwen3-30b-a3b": ("qwen/qwen3-30b-a3b", "Medium"),
    "qwen/qwen3-30b-a3b-instruct-2507": ("qwen/qwen3-30b-a3b-instruct-2507", "Medium"),
    "qwen/qwen3-32b": ("qwen/qwen3-32b", "Medium"),
    "qwen/qwen3-coder-30b-a3b-instruct": ("qwen/qwen3-coder-30b-a3b-instruct", "Medium"),
    "qwen/qwen3-next-80b-a3b-instruct": ("qwen/qwen3-next-80b-a3b-instruct", "Medium"),
    "qwen/qwen3-vl-235b-a22b-instruct": ("qwen/qwen3-vl-235b-a22b-instruct", "Medium"),
    "qwen/qwen3-vl-30b-a3b-instruct": ("qwen/qwen3-vl-30b-a3b-instruct", "Medium"),
    "qwen/qwen3.5-27b": ("qwen/qwen3.5-27b", "Medium"),
    "qwen/qwen3.5-35b-a3b": ("qwen/qwen3.5-35b-a3b", "Medium"),
    "qwen/qwen3.5-397b-a17b": ("qwen/qwen3.5-397b-a17b", "Medium"),
    "qwen/qwen3.5-9b": ("qwen/qwen3.5-9b", "Big"),
    "qwen/qwen3.6-27b": ("qwen/qwen3.6-27b", "Medium"),
    "qwen/qwen3.6-35b-a3b": ("qwen/qwen3.6-35b-a3b", "Medium"),
    "qwen/qwen3.8-27b": ("qwen/qwen3.8-27b", "Medium"),
    "stepfun/step-3.7-flash": ("stepfun/step-3.7-flash", "Medium"),
    "tencent/hunyuan-a13b-instruct": ("tencent/hunyuan-a13b-instruct", "Medium"),
    "tencent/hy-mt2-30b-a3b": ("tencent/hy-mt2-30b-a3b", "Medium"),
    "tencent/hy-mt2-7b": ("tencent/hy-mt2-7b", "Medium"),
    "thedrummer/skyfall-36b-v2": ("thedrummer/skyfall-36b-v2", "Medium"),
    "undi95/remm-slerp-l2-13b": ("undi95/remm-slerp-l2-13b", "Medium"),
    "xiaomi/mimo-v2.5": ("xiaomi/mimo-v2.5", "Medium"),
    "xiaomi/mimo-v2.6-flash": ("xiaomi/mimo-v2.6-flash", "Medium"),
    "xiaomi/mimo-v2.6-pro": ("xiaomi/mimo-v2.6-pro", "Medium"),
    "z-ai/glm-4.7-flash": ("z-ai/glm-4.7-flash", "Medium"),
    "z-ai/glm-5.2": ("z-ai/glm-5.2", "Medium"),
    "z-ai/glm-5.3": ("z-ai/glm-5.3", "Medium"),
    "z-ai/glm-5.3-flash": ("z-ai/glm-5.3-flash", "Little"),
    "kimi-k2.6-openrouter": ("moonshotai/kimi-k2.6", "Little"),
}
# Pre-epic OpenRouter models with no AST-1946 row: listed for the operator, never rewritten.
REMOVED = (
    "anthracite-org/magnum-v4-72b",
    "deepseek/deepseek-v4-pro",
    "deepseek/deepseek-v4-pro-0813",
    "moonshotai/kimi-k3",
    "morph/morph-v3-large",
    "nousresearch/hermes-3-llama-3.1-405b",
    "qwen/qwen2.5-vl-72b-instruct",
    "qwen/qwen3.8-2.4t-a95b",
    "sao10k/l3.1-euryale-70b",
    "tencent/hy4-preview",
    "z-ai/glm-5",
    "z-ai/glm-5.1",
)


def main(argv=None) -> int:
    apply = "--apply" in (sys.argv[1:] if argv is None else argv)
    conn = _get_connection()
    rows = conn.execute(
        "SELECT agent_id, model_id, brain_setting, mode FROM agent ORDER BY agent_id"
    ).fetchall()
    changes = []
    for agent_id, model_id, brain_setting, mode in rows:
        # Starting mode is judged on the size the row had before the remap below.
        new_mode = mode or (AGENT_MODE_CREATIVE if brain_setting == BRAIN_BIG else AGENT_MODE_DETERMINISTIC)
        # Removed / direct / post-deploy rows are not in REMAP, so they keep model and size.
        new_model_id, new_brain = REMAP.get(model_id, (model_id, brain_setting))
        if model_id in REMOVED:
            print(f"  removed model: {agent_id} on {model_id} ({brain_setting}), left as-is")
        if (new_model_id, new_brain, new_mode) != (model_id, brain_setting, mode):
            print(f"  {agent_id}: {model_id}/{brain_setting}/{mode} -> {new_model_id}/{new_brain}/{new_mode}")
            changes.append((new_model_id, new_brain, new_mode, agent_id))

    if not changes:
        print("No agent rows to change.")
    elif not apply:
        print(f"\n{len(changes)} row(s) would change. Re-run with --apply to commit.")
    else:
        conn.executemany(
            """UPDATE agent SET model_id = ?, brain_setting = ?, mode = ?, updated_at = CURRENT_TIMESTAMP
               WHERE agent_id = ?""",
            changes,
        )
        conn.commit()
        print(f"\nUpdated {len(changes)} row(s).")
    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
