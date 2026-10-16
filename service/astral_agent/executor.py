"""Stub provider executor — request jsonb in, result dict out (no HTTP).

AST-2239 replaces this with OpenRouter / Anthropic / llm-compat wrappers.
Keep ``async def execute(request: dict) -> dict`` so worker.py stays stable.
"""

from __future__ import annotations

from typing import Any, Dict


async def execute(request: dict) -> Dict[str, Any]:
    if not isinstance(request, dict):
        raise ValueError("request must be a dict")
    return {
        "stub": True,
        "echo": request,
        "usage": {"input_tokens": 0, "output_tokens": 0},
    }
