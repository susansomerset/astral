"""Call-time forced-tool schema and hydrate for rubric grader tasks (AST-2172).

A grader output type carries ``structured_output: True`` in ``ASTRAL_CONFIG["output_types"]``. Each call's
tool ``input_schema`` is built from that call's own rubric codes and row ids, so missing, duplicate and invented
codes are structurally impossible on enforcing hosts. The hydrate turns the tool input into the shape the
encoded-line decoder produced (``jobs[]`` / ``companies[]`` / ``results[]``) and runs one light check for
advisory hosts; a failed check is a per-entity ``decode_failures`` entry, never a whole-batch error.
"""
from typing import Any

from src.utils.config import ASTRAL_CONFIG
from src.utils.logging import get_logger

logger = get_logger(__name__)

# agent_performance rides inside the tool input: the AST-1839 agent-failure path and AST-2089 salvage read it.
_AGENT_PERFORMANCE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "status": {"type": "string", "enum": ["success", "failure"]},
        "failure_note": {"type": ["string", "null"]},
    },
    "required": ["status", "failure_note"],
    "additionalProperties": False,
}


def _grader_output_type(output_type: str) -> dict[str, Any]:
    """The output-type entry; raises when it is not a structured-output grader type."""
    ot = ASTRAL_CONFIG["output_types"].get(output_type) or {}
    if not ot.get("structured_output"):
        raise ValueError(f"{output_type!r} is not a structured-output grader type")
    return ot


def _grade_bounds(ot: dict[str, Any]) -> tuple[list[str], int, int]:
    """(grade letters, min confidence, max confidence); vet overrides both via "grade_letters" / "confidence_range"."""
    lo, hi = ot.get("confidence_range", (0, 5))
    return list(ot.get("grade_letters") or ASTRAL_CONFIG["valid_grades"]), lo, hi


def _row_entities(ctx: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Row id → entity: ctx["batch_index_map"] keys when supplied (AST-2093), else batch_entities positions."""
    index_map = ctx.get("batch_index_map") or {}
    if index_map:
        return {f"{i:03d}": index_map[i] for i in sorted(index_map)}
    return {f"{i:03d}": ent for i, ent in enumerate(ctx.get("batch_entities") or [])}


def grade_row_ids(ctx: dict[str, Any]) -> list[str]:
    """Row ids for this call's schema — the same ids hydrate_grade_tool_input maps back to entities."""
    return list(_row_entities(ctx))


def build_grade_tool_schema(output_type: str, codes: list[str], row_ids: list[str]) -> dict[str, Any]:
    """Forced-tool input_schema: one required object per row id plus agent_performance; each row requires
    every rubric code (closed object) and every extra field the output type declares (nullable)."""
    if not codes:
        raise ValueError(f"cannot build a grade schema for {output_type!r} with no rubric codes")
    ot = _grader_output_type(output_type)
    letters, lo, hi = _grade_bounds(ot)
    grade = {
        "type": "object",
        "properties": {
            "grade": {"type": "string", "enum": letters},
            "confidence": {"type": "integer", "minimum": lo, "maximum": hi},
        },
        "required": ["grade", "confidence"],
        "additionalProperties": False,
    }
    extras = ot.get("extra_fields") or {}
    row = {
        "type": "object",
        # Strict hosts require every declared key, so optional extras are required-but-nullable.
        "properties": {
            **{c: grade for c in codes},
            **{name: {**frag, "type": [frag["type"], "null"]} for name, frag in extras.items()},
        },
        "required": [*codes, *extras],
        "additionalProperties": False,
    }
    schema = {
        "type": "object",
        "properties": {**{rid: row for rid in row_ids}, "agent_performance": _AGENT_PERFORMANCE_SCHEMA},
        "required": [*row_ids, "agent_performance"],
        "additionalProperties": False,
    }
    logger.debug("Built grade tool schema for %s: %s", output_type, schema)
    return schema
