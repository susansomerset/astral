# AST-2178 — Call-time schema and hydrate

- **Linear:** [AST-2178](https://linear.app/astralcareermatch/issue/AST-2178) · parent [AST-2172](https://linear.app/astralcareermatch/issue/AST-2172) (Enforced structured output for rubric graders)
- **Publish ref:** `origin/sub/AST-2172/AST-2178-call-time-schema-hydrate`
- **Assignee:** Hedy
- **Canon Scope:** `stat.agent.grade-vector-validation`, `stat.agent.confidence-bounds`, `stat.logging.warning`, `stat.logging.debug`

This is the pure-function slice of AST-2172: one new module, `src/core/grade_schema.py`. It builds each grader call's forced-tool `input_schema` from that call's rubric codes and row ids, and it hydrates the tool input back into the exact shape `_decode_payload` produces today (`jobs[]` / `companies[]` / vet `results[]`), with per-entity `decode_failures`. The hydrate runs one light check for advisory hosts: every expected code and row present, nothing unexpected, X ⇒ confidence 0, and a letter with confidence 0 stored as X0 (AST-2124). A missing code is never defaulted to X. Nothing calls this module yet: AST-2179 (#4) sends the schema, AST-2180 (#5) wires it into `do_task` / consult / roster, and AST-2181 (#6) uses the hydrate for ad-hoc tests. No provider calls, here or in verification.

## Findings that shape this plan

1. **AST-2177 (#2) is on `origin/ftr/AST-2172-structured-output-graders`** and this branch now carries it. Every grader `ASTRAL_CONFIG["output_types"]` entry has `structured_output: True` and `extra_fields` (JSON Schema fragments). Vet also has `grade_letters` (A B C D F) and `confidence_range` (1, 5). This module reads only those keys.
2. **AC 9 of the parent bans the literal `"grades_encoded` in `src/core`.** So the module never names an output type. Vet's `results[]` shape is selected by `task_key == INFLOW_CONFIG["vet"]["task_key"]`, and company vs job ids come from `TASK_CONFIG[task_key]["entity_type"]`, the same source `_decode_payload` uses.
3. **Row ids** are the batch-unique indexes in `ctx["batch_index_map"]` (int keys, AST-2093) when present, otherwise positions in `ctx["batch_entities"]`. Prompts render them as `{i:03d}` (`consult.py` `[index={position:03d}]`, `roster.py` `{index:03d}|…`), so schema keys are those zero-padded strings.
4. **Downstream consumers read every extra field as `row.get(k) or …`** (`meteorite.py` 546/548/1171, `roster.py` 1774/1815/3560–3568). An absent key and a `None` value behave the same, so null extras are left out of the row (see the Stage 2 decision).
5. **Per-entity failures are already warned once at the dispatch handler.** `consult.py` routes `decode_failures` through `_log_fail_dest` / `_transition_batch_consult_failures` (`who -> dest [why]`). If the hydrate also warned for those, each failure would be logged twice. So the hydrate warns only for a row id it can't attach to any entity, which nobody downstream reports. That message is the one `_decode_payload` uses today.
6. **`jsonschema` is installed but isn't a declared dependency** (no `requirements*.txt` / `pyproject.toml` entry). So the light check is hand-written: about a dozen lines covering exactly the declared fragment shapes (`string`, `integer`, `object` + `additionalProperties`, `array` + `items`).
7. **Verified at plan time.** I drafted the module (Appendices A + B) outside the repo and ran the Appendix C harness with the module temporarily copied to `src/core/grade_schema.py`, then removed it (working tree clean). All four checks printed `ok`: AC 1, AC 2, AC 3 (dict-equal to `_decode_payload` for all five grader output types, including X0, notes, listing meta + `job_data`, prefilter links and vet), plus the light-check cases. `ruff check` passes on part A alone and on the assembled module.

## Contract for siblings (#4, #5, #6)

```python
grade_row_ids(ctx) -> list[str]                                   # e.g. ["000", "001"]; same ids the hydrate maps back
build_grade_tool_schema(output_type, codes, row_ids) -> dict      # the tool's input_schema only
hydrate_grade_tool_input(task_key, output_type, tool_input, codes, ctx) -> dict
```

- `codes` is the call's rubric vector codes in rubric order (multi-vector graders: the keys of the call's `vector_labels`; vet: `[INFLOW_CONFIG["vet"]["grade_vector_code"]]`). The caller passes the **same** `codes` to both functions.
- `build_grade_tool_schema` raises `ValueError` on empty `codes` (AC 2) or a non-structured-output type.
- `hydrate_grade_tool_input` returns `{array_key: [...]}`, plus `"decode_failures": [{<id_key>: …, "pos": int, "reason": str}]` only when a row fails. `<id_key>` is `astral_job_id` / `company_id` / `hit_index` (vet). It raises `TypeError` when `tool_input` isn't a dict, and `ValueError` when a vet call has other than one code. It ignores `agent_performance`; #5 reads that key from the tool input itself.
- The tool's `name` / `description` and the `tools` / `tool_choice` wrapper are not built here (#4 / #5).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/grade_schema.py` | New module: `grade_row_ids`, `build_grade_tool_schema`, `hydrate_grade_tool_input` + private helpers | core |

No other file is committed. The harness lives at `debug/spikes/AST-2178/check.py` (gitignored, `stat.debug.spikes-under-debug-dir`).

## Stage 1: Schema builder

**Done when:** `src/core/grade_schema.py` exists with Appendix A's content; `ruff check src/core/grade_schema.py` passes; and the AC 1 / AC 2 one-liner in step 3 prints `stage1 ok`.

1. Create `src/core/grade_schema.py` with the content of **Appendix A**, verbatim.
2. `python3 -m py_compile src/core/grade_schema.py && ruff check src/core/grade_schema.py`.
3. Run:
   ```bash
   python3 -c "
   from src.core.grade_schema import build_grade_tool_schema as b, grade_row_ids as r
   from src.utils.config import ASTRAL_CONFIG as A
   s = b('grades_encoded', ['CL', 'RE'], ['000', '001'])
   assert s['required'] == ['000', '001', 'agent_performance'] and s['additionalProperties'] is False
   for rid in ('000', '001'):
       row = s['properties'][rid]
       assert row['required'] == ['CL', 'RE'] and row['additionalProperties'] is False
       for c in ('CL', 'RE'):
           p = row['properties'][c]['properties']
           assert p['grade']['enum'] == A['valid_grades'] and p['confidence'] == {'type': 'integer', 'minimum': 0, 'maximum': 5}
   try:
       b('grades_encoded', [], ['000']); raise SystemExit('AC2 FAIL')
   except ValueError:
       pass
   assert r({'batch_index_map': {9: {}, 5: {}}}) == ['005', '009'] and r({'batch_entities': [{}, {}]}) == ['000', '001']
   print('stage1 ok')"
   ```
   (The output-type literal is in a shell one-liner, not under `src/`, so AC 9 is unaffected.)
4. Commit `code(AST-2178): grade_schema — call-time forced-tool schema builder` and push (Execution contract).

⚠️ **Decision (row ids helper):** `grade_row_ids(ctx)` is public so #5 builds the schema from exactly the ids the hydrate maps back. Without it, #5 would re-derive the `{i:03d}` keys from `batch_index_map` / `batch_entities` itself and the two could drift. It uses the same private `_row_entities` the hydrate uses.

⚠️ **Decision (nullable extras):** each extra field becomes `{**fragment, "type": [fragment_type, "null"]}`, which keeps `items` / `additionalProperties` on the fragment. That's the same nullable form AST-2177's spike schema used for `failure_note`. I didn't use `anyOf`, because not every host's strict mode accepts it.

⚠️ **Decision (guard):** the builder also raises on an output type without `structured_output`. That turns a mis-wired call in #5 into an immediate error rather than a schema with the wrong grade bounds. One line; Joan / Susan can strike it.

## Stage 2: Hydrate and light check

**Done when:** `ruff check src/core/grade_schema.py` passes and `python3 debug/spikes/AST-2178/check.py` prints `AC1 ok`, `AC2 ok`, `AC3 ok`, `light check ok`. The one expected WARNING line (`evaluate_jd skipped — index 007 not in this batch`) comes from the unknown-row case.

1. In `src/core/grade_schema.py`, change `from src.utils.config import ASTRAL_CONFIG` to `from src.utils.config import ASTRAL_CONFIG, INFLOW_CONFIG, TASK_CONFIG`.
2. Append **Appendix B** verbatim to the end of the file. It starts with two blank lines, then the `_PY_TYPES` comment.
3. `python3 -m py_compile src/core/grade_schema.py && ruff check src/core/grade_schema.py`.
4. Copy **Appendix C** verbatim to `debug/spikes/AST-2178/check.py` and run `python3 debug/spikes/AST-2178/check.py` from the repo root. AC 3 compares against the still-present `src.core.agent._decode_payload`, which #5 deletes later. This harness is a build-time proof only and is never committed; Betty owns the committed tests.
5. Commit `code(AST-2178): grade_schema — hydrate tool input with per-entity light check` and push.

⚠️ **Decision (missing rows are decode failures):** per the parent Technical scope, a row absent from the tool input becomes a `decode_failures` entry (`row NNN missing from tool input`). Under `_decode_payload` it fell out as "omitted from response". Consult's batch path already subtracts `decode_failures` ids from its missing set and sends both to the same retry destination (`consult.py` 1868–1883), so routing is unchanged and the reason is more precise.

⚠️ **Decision (unknown rows):** a row id that isn't in this batch is warned once (`%s skipped — index %s not in this batch`, the same text `_decode_payload` uses) and skipped. It has no entity to route; the entity it was meant for fails as missing. Under an enforcing host this can't happen, because the schema is closed.

⚠️ **Decision (null extras omitted):** a null or blank extra field (`""`, `[]`, `{}`) is left out of the row, just as `_decode_payload` leaves out an absent notes or link tail. One edge differs: an encoded line with an *empty middle* meta field (`003|…||Title|link`) used to produce `company_job_id: None`, and now the key is absent. Every consumer reads it with `.get(...) or …` (Finding 4), so behaviour is identical. `job_data` values are stripped, and blank values become `None` (old `v.strip() or None`).

⚠️ **Decision (extra-field types):** on an advisory host, an extra field of the wrong JSON type (e.g. a string where `possible_job_links` expects an int array) fails that entity rather than persisting garbage. An extra field the host left out entirely counts as null and is not a failure, because the light check's mandate is codes, rows and X ⇒ 0, and every extra is optional by parent decision.

⚠️ **Decision (vet):** vet output stays `{"results": [{hit_index, grade, website, confidence}]}`. A failed hit (bad grade, confidence outside 1–5, missing website) goes to `decode_failures` keyed `hit_index` and drops out of `results`. Today roster then warns `missing results row hit_index=i` and counts it as an error (`roster.py` 645–649); #5 decides whether roster reads the reason. Under `_decode_payload` a missing website raised for the whole batch, so this narrows a whole-batch failure to one hit, consistent with the per-entity rule. No X0 rewrite on vet: `confidence_range` starts at 1, so confidence 0 is out of range (`stat.agent.confidence-bounds`: the exception is non-vet only).

⚠️ **Decision (exact row-id keys):** row ids match as exact strings (`"001"`, not `"1"`). The schema declares the exact keys, so an enforcing host can't vary them; on an advisory host a mangled key is warned as unknown and the real row fails as missing. That is a retry, never a misattribution.

⚠️ **Decision (row order):** rows are emitted in row-id order, not the model's key order, so output is deterministic and matches `_decode_payload` for a payload whose lines are in row order.

## Canon check

- **`stat.agent.grade-vector-validation`:** `_hydrate_row` requires every expected code (`missing vector code …`), rejects any key that is neither a code nor a declared extra (`unexpected key …`), and accepts only `ASTRAL_CONFIG["valid_grades"]` (or vet's `grade_letters`). The schema's per-row `required` + `additionalProperties: false` + grade `enum` enforce the same thing on enforcing hosts. A missing code is a failure, never X.
- **`stat.agent.confidence-bounds`:** confidence is an int (not bool) in `confidence_range` (default 0–5); X requires 0; a letter with 0 becomes X0, the sanctioned exception the active statute now names (`src/core/grade_schema.py`, non-vet paths). Vet's 1–5 range means the rewrite can't fire there. No other value is coerced.
- **`stat.logging.warning`:** one warning per unattachable row (who + why). Per-entity failures are returned as `decode_failures` for the dispatch handler's single `who -> dest [why]` warning (Finding 5). There's no `print`, no tally, and no `logger.exception`.
- **`stat.logging.debug`:** the built schema is logged in full at debug (`Built grade tool schema for …`), and the hydrate loop logs begin and end with counts. No `if debug` gating and no truncation. The raw tool input is logged at its call site in #5 (`Calling` / `Response from`), not here.

## Execution contract

The plan is binding. Steps run in order and stages run in order. No added files, modules or dependencies; nothing committed from `debug/`. If a step is ambiguous, doesn't match the code, or a check fails, stop and comment on the parent [AST-2172](https://linear.app/astralcareermatch/issue/AST-2172):

```
🛑 Stage N blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

Each stage ends in one `code(AST-2178): …` commit on the epic worktree, published with `git push origin HEAD:sub/AST-2172/AST-2178-call-time-schema-hydrate`. Compile and lint before every commit. Run `sync-child.sh` with `--ftr AST-2172-structured-output-graders`; the bare `--ftr AST-2172` doesn't match the parent ref on origin, so it skips the ftr merge.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Appendix A — `src/core/grade_schema.py` (Stage 1)

```python
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
```

## Appendix B — appended to `src/core/grade_schema.py` (Stage 2)

Starts with two blank lines.

```python


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
```

## Appendix C — `debug/spikes/AST-2178/check.py` (gitignored harness)

```python
"""AST-2178 acceptance harness: AC1, AC2, AC3 (vs the still-present _decode_payload) and light-check cases."""
from src.core.agent import _decode_payload
from src.core.grade_schema import build_grade_tool_schema, grade_row_ids, hydrate_grade_tool_input
from src.utils.config import ASTRAL_CONFIG, TASK_CONFIG

AP = {"status": "success", "failure_note": None}
LABELS = {"CL": "Clarity", "RE": "Remote"}
OT = lambda k: TASK_CONFIG[k]["output_type"]  # noqa: E731


def g(letter, conf):
    return {"grade": letter, "confidence": conf}


# AC1 — complete and closed.
s = build_grade_tool_schema(OT("evaluate_jd"), ["CL", "RE"], ["000", "001"])
assert s["required"] == ["000", "001", "agent_performance"] and s["additionalProperties"] is False
for rid in ("000", "001"):
    r = s["properties"][rid]
    assert r["required"] == ["CL", "RE"] and r["additionalProperties"] is False, r
    for c in ("CL", "RE"):
        p = r["properties"][c]["properties"]
        assert p["grade"]["enum"] == ASTRAL_CONFIG["valid_grades"], p
        assert p["confidence"] == {"type": "integer", "minimum": 0, "maximum": 5}, p
n = build_grade_tool_schema(OT("grade_do"), ["CL"], ["000"])["properties"]["000"]
assert n["required"] == ["CL", "notes"] and n["properties"]["notes"]["type"] == ["string", "null"], n
print("AC1 ok")

# AC2 — empty rubric refuses.
try:
    build_grade_tool_schema(OT("evaluate_jd"), [], ["000"])
    raise SystemExit("AC2 FAIL: schema built with no codes")
except ValueError:
    print("AC2 ok")

# AC3 — same shape as the old decoder for equivalent encoded lines.
J = [{"astral_job_id": "j0"}, {"astral_job_id": "j1"}]
C = [{"company_id": "c0"}]
CASES = [
    ("evaluate_jd", {"batch_index_map": {5: J[0], 9: J[1]}}, "005|CLA5|REX0\n009|CLB3|REC0",
     {"005": {"CL": g("A", 5), "RE": g("X", 0)}, "009": {"CL": g("B", 3), "RE": g("C", 0)}}),
    ("grade_do", {"batch_entities": J}, "000|CLA5|REB2|remote but vague\n001|CLX0|RED4",
     {"000": {"CL": g("A", 5), "RE": g("B", 2), "notes": "remote but vague"},
      "001": {"CL": g("X", 0), "RE": g("D", 4), "notes": None}}),
    ("qualify_job_listings", {"batch_entities": J},
     "000|CLA4|REB3|4471|Staff Engineer|https://x.co/j/1|location: Remote|salary_range: 200k\n001|CLF5|REX0|4472",
     {"000": {"CL": g("A", 4), "RE": g("B", 3), "company_job_id": "4471", "job_title": "Staff Engineer",
              "job_link": "https://x.co/j/1", "job_data": {"location": "Remote", "salary_range": "200k"}},
      "001": {"CL": g("F", 5), "RE": g("X", 0), "company_job_id": "4472", "job_title": None,
              "job_link": None, "job_data": None}}),
    ("prefilter_company", {"batch_entities": C}, "000|CLA5|REB3|JOB:3,7|CULT:12",
     {"000": {"CL": g("A", 5), "RE": g("B", 3), "possible_job_links": [3, 7], "culture_links_to_explore": [12]}}),
    ("vet_inflow_discovery", {"batch_entities": [{"short_name": "a"}, {"short_name": "b"}]},
     "000|LTA5|https://acme.com\n001|LTF4|https://b.io",
     {"000": {"LT": g("A", 5), "website": "https://acme.com"}, "001": {"LT": g("F", 4), "website": "https://b.io"}}),
]
for key, ctx, line, tool in CASES:
    codes = ["LT"] if key == "vet_inflow_discovery" else ["CL", "RE"]
    ctx = {**ctx, "vector_labels": {} if key == "vet_inflow_discovery" else LABELS}
    old = _decode_payload(key, OT(key), line, ctx)
    new = hydrate_grade_tool_input(key, OT(key), {**tool, "agent_performance": AP}, codes, ctx)
    assert old == new, (key, old, new)
    assert set(build_grade_tool_schema(OT(key), codes, grade_row_ids(ctx))["properties"]) == {*tool, "agent_performance"}, key
print("AC3 ok")

# Light check — per-entity failures, never X for a missing code, whole batch survives.
ctx = {"batch_entities": J, "vector_labels": LABELS}
BAD = [
    ({"CL": g("A", 5)}, "missing vector code RE"),
    ({"CL": g("A", 5), "RE": g("B", 3), "ZZ": g("A", 5)}, "unexpected key ZZ"),
    ({"CL": g("A", 5), "RE": g("X", 3)}, "grade X requires confidence 0"),
    ({"CL": g("Q", 5), "RE": g("B", 3)}, "illegal grade"),
    ({"CL": g("A", 6), "RE": g("B", 3)}, "confidence must be an integer 0-5"),
    (None, "missing from tool input"),
]
for bad, why in BAD:
    tool = {"000": {"CL": g("A", 5), "RE": g("B", 3)}, "agent_performance": AP}
    if bad is not None:
        tool["001"] = bad
    out = hydrate_grade_tool_input("evaluate_jd", OT("evaluate_jd"), tool, ["CL", "RE"], ctx)
    assert [j["astral_job_id"] for j in out["jobs"]] == ["j0"], out
    (f,) = out["decode_failures"]
    assert f["astral_job_id"] == "j1" and f["pos"] == 1 and why in f["reason"], (why, f)
out = hydrate_grade_tool_input("evaluate_jd", OT("evaluate_jd"),
                               {"000": {"CL": g("A", 5), "RE": g("B", 3)}, "001": {"CL": g("A", 5), "RE": g("B", 3)},
                                "007": {"CL": g("A", 5), "RE": g("B", 3)}, "agent_performance": AP}, ["CL", "RE"], ctx)
assert "decode_failures" not in out and len(out["jobs"]) == 2, out
vctx = {"batch_entities": [{"short_name": "a"}]}
out = hydrate_grade_tool_input("vet_inflow_discovery", OT("vet_inflow_discovery"),
                               {"000": {"LT": g("A", 0), "website": "https://a.co"}, "agent_performance": AP}, ["LT"], vctx)
assert out["results"] == [] and out["decode_failures"][0]["hit_index"] == 0, out
out = hydrate_grade_tool_input("vet_inflow_discovery", OT("vet_inflow_discovery"),
                               {"000": {"LT": g("A", 5), "website": None}, "agent_performance": AP}, ["LT"], vctx)
assert "missing website" in out["decode_failures"][0]["reason"], out
print("light check ok")
```

## Joan validate

[plan-rubric]
**Ticket:** AST-2178
**Overall:** APPROVED
**Corpus:** b7ab2203048ce0beb2869a12200ab7fa696c8066
**Publish ref:** `origin/sub/AST-2172/AST-2178-call-time-schema-hydrate` @ `0206699d0`

## Canon scores

| id | grade | effort | one-line |
|----|-------|--------|----------|
| `stat.agent.grade-vector-validation` | A | | |
| `stat.agent.confidence-bounds` | A | | |
| `stat.logging.warning` | A | | |
| `stat.logging.debug` | A | | |

## Traceability

**1** → Stage 1 + Appendix A/C (`build_grade_tool_schema`, closed row/code objects, `valid_grades` enum, confidence 0–5). **2** → Stage 1 step 3 / Appendix C empty-`codes` `ValueError`. **3** → Stage 2 + Appendix B/C (`hydrate_grade_tool_input` dict-equal to `_decode_payload` for five grader types). Parent AC 4–11 / 10a–10b N/A (Boundaries: no transport, no `do_task` wire, no admin). Parent AC **5** (missing code → retry, never default X) is not on this child’s AC list but is implemented in `_hydrate_row` for AST-2180 — note only.

## Findings

### discuss

- **Location:** Stage 2 step 4 / Execution contract — `debug/spikes/AST-2178/check.py` only  
  **Finding:** AC 3 proof lives in a gitignored harness against `_decode_payload`; no committed `tests/**` in this child (Betty’s lane).  
  **Recommendation:** Accept for #3 scope; ensure `qa-child` lands durable coverage before UT.

- **Location:** Stage 1 — `build_grade_tool_schema(..., row_ids=[])`  
  **Finding:** AC 2 guards empty `codes` only; empty `row_ids` would yield a schema with only `agent_performance`. Unlikely in production batches; not forbidden by child AC.  
  **Recommendation:** Optional guard in build if Susan wants fail-fast; not required for plan approval.

- **Location:** Appendix B — vet missing website / bad grade  
  **Finding:** Per-hit `decode_failures` vs old whole-batch `ValueError` on empty website; plan defers roster double-warning to #5 (`roster.py` 645–649).  
  **Recommendation:** AST-2180 should align roster with per-entity failures (plan already flags).

- **Location:** Stage 1 — `_grader_output_type` raises on non-structured types  
  **Finding:** One-line guard beyond minimum AC; helpful for #5 mis-wiring.  
  **Recommendation:** Keep unless Susan strikes it (plan allows).

### acceptable

- **Location:** Scope / Files Changed  
  **Finding:** Single new `src/core/grade_schema.py`; no provider I/O; public contract documents siblings #4/#5/#6; parent AC 9 satisfied (no `"grades_encoded"` literal under `src/core` in module — output type passed in).

- **Location:** `stat.agent.confidence-bounds`  
  **Finding:** X ⇒ conf 0 enforced; non-vet `{letter}` + conf `0` → stored X0 (AST-2124); vet `confidence_range` (1, 5) blocks 0 before rewrite; no other coercion; bool excluded from integer.

- **Location:** `stat.agent.grade-vector-validation`  
  **Finding:** Every expected code required; unexpected keys rejected; illegal letters fail; missing code → failure reason, never inferred X; schema `required` + `additionalProperties: false` + enums mirror light check.

- **Location:** `stat.logging.warning`  
  **Finding:** Unknown row id uses same text as `_decode_payload` (`agent.py` 359); per-entity hydrate failures only in `decode_failures` (consult’s single `who -> dest [why]` — Finding 5).

- **Location:** `stat.logging.debug`  
  **Finding:** Full schema at debug (no truncation); hydrate begin/end loop counts; no `if debug` gating; uses `get_logger(__name__)`.

- **Location:** Dependencies  
  **Finding:** Hand-written light check avoids undeclared `jsonschema` dependency in product code; AST-2177 `output_types` markers/extras are sole registry inputs.

- **Location:** `grade_row_ids` / `_row_entities`  
  **Finding:** `{i:03d}` keys align with consult/roster prompts and AST-2093 `batch_index_map` ordering.

### fix-now

(none)

## R6 (condensed)

- Parent Technical scope for `grade_schema.py` (builder + hydrate + light check, nullable extras, agent_performance in schema) matches appendices and contract block.  
- After #2: reads `structured_output`, `extra_fields`, vet `grade_letters` / `confidence_range` only from config.  
- Plan Discuss: **0** rounds; **Plan Ready**, assignee Joan.  
- External dry-run claim (Finding 7): AC 3 parity with decoder is the critical bar; committed tests remain Betty’s follow-up.

context_tokens≈72000

---

[plan-rubric] PROCEED (Commit: 0206699d0) Schema + hydrate plan solid


---

## Review

Build on `origin/sub/AST-2172/AST-2178-call-time-schema-hydrate`:

- `4add8fa3f` Stage 1: `src/core/grade_schema.py` from Appendix A, verbatim. Builds the schema and exposes `grade_row_ids`.
- `b1c6796c3` Stage 2: import line widened and Appendix B appended, verbatim. Adds the hydrate and light check. The file is byte-identical to the module verified at plan time.

Checks:
- `py_compile` and `ruff check src/core/grade_schema.py` are clean after each stage.
- Stage 1's one-liner prints `stage1 ok`.
- The Appendix C harness prints `AC1 ok`, `AC2 ok`, `AC3 ok` and `light check ok`, plus the one expected `index 007` WARNING. AC 3 is dict-equal to `_decode_payload` for all five grader output types.
- `rg '"grades_encoded' src/core/grade_schema.py` returns nothing (parent AC 9).
- No provider calls.

Plan-step note: Stage 2 step 4's command `python3 debug/spikes/AST-2178/check.py` needs `PYTHONPATH=.`. Python puts the script's own folder on the import path, not the repo root. The harness is gitignored and its content is unchanged; only the invocation differs.

For qa-child: no existing test imports this module, so nothing is expected to churn. Durable coverage for AC 1–3 and the light-check cases (missing / unexpected code, X with nonzero confidence, illegal grade, out-of-range confidence, missing row, unknown row, vet website / confidence 0) can follow Appendix C.
