"""Call-time forced-tool schema and hydrate for rubric grader tasks (AST-2172).

A grader output type carries ``structured_output: True`` in ``ASTRAL_CONFIG["output_types"]``. Each call's
tool ``input_schema`` is built from that call's own rubric codes and row ids, so missing, duplicate and invented
codes are structurally impossible on enforcing hosts. The hydrate turns the tool input into the shape the
encoded-line decoder produced (``jobs[]`` / ``companies[]`` / ``results[]``) and runs one light check for
advisory hosts; a failed check is a per-entity ``decode_failures`` entry, never a whole-batch error.
"""
from typing import Any

from src.utils.config import ASTRAL_CONFIG, INFLOW_CONFIG, TASK_CONFIG
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


# JSON Schema type → Python type for the extra-field check (bool is excluded from integer separately).
_PY_TYPES = {"string": str, "integer": int, "object": dict, "array": list}


def _fits(frag: dict[str, Any], value: Any) -> bool:
    """value matches the extra field's JSON Schema fragment (type, array items, object value type)."""
    if isinstance(value, bool) or not isinstance(value, _PY_TYPES[frag["type"]]):
        return False
    if isinstance(value, list) and "items" in frag:
        return all(_fits(frag["items"], v) for v in value)
    if isinstance(value, dict) and isinstance(frag.get("additionalProperties"), dict):
        return all(_fits(frag["additionalProperties"], v) for v in value.values())
    return True


def _clean(value: Any) -> Any:
    """The old decoder's meta normalization: strip text, blank dict values → None."""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, dict):
        return {str(k).strip(): ((v.strip() or None) if isinstance(v, str) else v) for k, v in value.items()}
    return value


def _hydrate_row(
    task_key: str, rid: str, raw: Any, codes: list[str], ot: dict[str, Any], labels: dict[str, str],
) -> tuple[dict[str, Any] | None, str | None]:
    """One tool-input row → ({"grades": [...], **extras}, None), or (None, reason) when the light check fails."""
    if raw is None:
        return None, f"[{task_key}] row {rid} missing from tool input"
    if not isinstance(raw, dict):
        return None, f"[{task_key}] row {rid} must be an object, got {type(raw).__name__}"
    extras = ot.get("extra_fields") or {}
    # stat.agent.grade-vector-validation: every expected code, nothing unexpected. Never default a missing code to X.
    missing = [c for c in codes if c not in raw]
    if missing:
        return None, f"[{task_key}] row {rid} missing vector code {','.join(missing)}"
    unexpected = sorted(set(raw) - set(codes) - set(extras))
    if unexpected:
        return None, f"[{task_key}] row {rid} unexpected key {','.join(unexpected)}"
    letters, lo, hi = _grade_bounds(ot)
    grades: list[dict[str, Any]] = []
    for code in codes:
        entry = raw[code] if isinstance(raw[code], dict) else {}
        letter, conf = entry.get("grade"), entry.get("confidence")
        if letter not in letters:
            return None, f"[{task_key}] row {rid} {code}: illegal grade {letter!r}"
        if isinstance(conf, bool) or not isinstance(conf, int) or not lo <= conf <= hi:
            return None, f"[{task_key}] row {rid} {code}: confidence must be an integer {lo}-{hi}, got {conf!r}"
        if letter == "X" and conf != 0:
            return None, f"[{task_key}] row {rid} {code}: grade X requires confidence 0, got {conf}"
        # Sanctioned slip (stat.agent.confidence-bounds): a letter with confidence 0 is stored as X0 (AST-2124).
        # Vet's confidence_range starts at 1, so it never reaches this on the vet path.
        grades.append({"vector": labels.get(code, code), "grade": "X" if conf == 0 else letter, "confidence": conf})
    row: dict[str, Any] = {"grades": grades}
    for name, frag in extras.items():
        value = raw.get(name)  # a key an advisory host left out counts as null
        if value is None:
            continue
        if not _fits(frag, value):
            return None, f"[{task_key}] row {rid} {name} must be {frag['type']}, got {type(value).__name__}"
        value = _clean(value)
        if value:  # blank text and empty arrays / objects are omitted, as the old decoder did
            row[name] = value
    return row, None


def hydrate_grade_tool_input(
    task_key: str, output_type: str, tool_input: Any, codes: list[str], ctx: dict[str, Any],
) -> dict[str, Any]:
    """Tool input → the encoded decoder's shape: {jobs|companies: [...]} or vet {results: [...]}, plus
    "decode_failures" ({id, pos, reason}) only when a row fails the light check. agent_performance is ignored
    here — the caller reads it from the tool input. Raises TypeError on a non-object tool input and ValueError on a vet call
    without exactly one code."""
    ot = _grader_output_type(output_type)
    if not isinstance(tool_input, dict):
        raise TypeError(f"[{task_key}] tool input must be an object, got {type(tool_input).__name__}")
    vet = task_key == INFLOW_CONFIG["vet"]["task_key"]
    if vet and len(codes) != 1:
        raise ValueError(f"[{task_key}] vet grades exactly one vector code, got {codes!r}")
    company = (TASK_CONFIG.get(task_key) or {}).get("entity_type") == "company"
    id_key = "hit_index" if vet else ("company_id" if company else "astral_job_id")
    array_key = "results" if vet else ("companies" if company else "jobs")
    labels = ctx.get("vector_labels") or {}
    entities = _row_entities(ctx)
    for rid in tool_input:
        if rid != "agent_performance" and rid not in entities:
            # No entity to route; the row it was meant for fails below as missing.
            logger.warning("%s skipped — index %s not in this batch\n  This line is not being graded", task_key, rid)
    rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    logger.debug("Beginning hydrate loop on %s items", len(entities))
    for rid, ent in entities.items():
        pos = int(rid)
        ent_id = pos if vet else ent[id_key]
        row, reason = _hydrate_row(task_key, rid, tool_input.get(rid), codes, ot, labels)
        if row is not None and vet and not row.get("website"):
            row, reason = None, f"[{task_key}] row {rid} missing website"
        if row is None:
            # The dispatch handler warns once per entity when it routes this failure (stat.logging.warning).
            failures.append({id_key: ent_id, "pos": pos, "reason": reason})
        elif vet:
            g = row["grades"][0]
            rows.append({"hit_index": pos, "grade": g["grade"], "website": row["website"], "confidence": g["confidence"]})
        else:
            rows.append({id_key: ent_id, **row})
    logger.debug("End hydrate loop after %s items", len(rows))
    out: dict[str, Any] = {array_key: rows}
    if failures:
        out["decode_failures"] = failures
    return out
