"""
Core business logic for job consulting/analysis.

render_verdict(task_type, astral_job_id): single orchestrator for per-job consult tasks.
  Fetches job/company internally, preps live content, calls agent, audits, derives verdict.
  Per-job orchestration (pass/fail/error, thresholds, rubric refs) from TASK_CONFIG[task_type] — dispatch and catalog share one string (AST-736).
_render_pass_fail: binary grading (PASS/F) for qualify_job_listings and evaluate_jd_batch.
_render_score: scored grading (AST-358 importance × universal grade values × confidence) for batch qualify/evaluate_jd and grade_get/do/like.
When TASK_CONFIG[task_key].scored, transitions persist latest_score only when a numeric score exists.
_run_batch_consult: shared scaffolding for batch AI tasks (ID reconciliation, audit, error handling).
qualify_job_listings: batch job list screen (Pattern A) — thin wrapper over _run_batch_consult.
qualify_meteorite: meteorite pre-AI enrich (Pattern A, fields) — thin wrapper over _run_batch_consult.
evaluate_jd_batch: batch JD dealbreaker screen (Pattern A) — thin wrapper over _run_batch_consult.
grade_*_batch: scored DO/GET/LIKE Pattern A batching (AST-503) via _run_batch_consult(task_key=grade_*).
"""

import json
import re
from typing import Any, Dict, List, Optional, Tuple

from src.core import tracker
from src.core.agent import do_task
from src.core.meteorite import is_meteorite_company
from src.data.database import ensure_batch_response_entity_ids
from src.utils import rubric_text
from src.utils.config import (
    TASK_CONFIG,
    TRACKER_CONFIG,
    BUILD_ARTIFACTS_BASE_STATE,
    JOB_STATES,
    ASTRAL_CONFIG,
    CONFIDENCE_MULTIPLIERS,
    MAX_GRADE_VALUE,
    RUBRIC_TOTAL,
    JOB_TOKEN_CONFIG,
    RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY,
    METEORITE_CONFIG,
    METEORITE_GDL_OUTCOME_BY_TASK,
    dispatch_chain_row_matches_job,
    dispatch_chain_registry_trigger,
    grade_value,
    importance_multiplier,
    is_dispatch_chain_trigger,
)
from src.utils.formatting import enumerate_array, normalize_link, uuid_path_segment_from_url
from src.utils.logging import get_logger
from src.utils.llm_external import is_provider_balance_refusal

logger = get_logger(__name__)


def _consult_job_identifier(job: Dict[str, Any]) -> str:
    """Primary debug identifier for a consult job row (§1.5.1 style D)."""
    return str(job.get("astral_job_id") or job.get("job_title") or "?")


# input_state → TASK_CONFIG orchestration lookup key (grade_* for scored consult hops).
# Legacy map — not used for dispatch routing (AST-534). Tests pass dispatch_task_key explicitly.
_INPUT_STATE_TO_TASK = {
    "NEW":                "qualify_job_listings",
    "VALID_TITLE":        "qualify_job_listings",
    "VALID_TITLE_RETRY":  "qualify_job_listings",
    "NEW_RETRY":          "qualify_job_listings",
    "PASSED_JOBLIST":     "fetch_jd",
    "JD_READY":           "evaluate_jd",
    "JD_READY_RETRY":     "evaluate_jd",
    "PASSED_JD":          "grade_do",
    "PASSED_JD_RETRY":    "grade_do",
    "PASSED_DO":          "grade_get",
    "PASSED_DO_RETRY":    "grade_get",
    "PASSED_GET":         "grade_like",
    "PASSED_LIKE":        "analysis_upshot",
    "PASSED_LIKE_RETRY":  "analysis_upshot",
    "BUILD_ARTIFACTS":    "contemplate_job",
    "CANDIDATE_REVIEW":   "draft_cover_letter",
}


def _consult_orchestration(task_key: str) -> Dict[str, Any]:
    """Return TASK_CONFIG orchestration for dispatch/catalog task_key (same string after AST-736)."""
    tk = (task_key or "").strip()
    return TASK_CONFIG[tk]


def _entity_state_is_meteorite(state: Optional[str]) -> bool:
    return bool(state) and str(state).startswith("METEORITE_")


def _consult_orchestration_for_entity(task_key: str, entity_state: Optional[str] = None) -> Dict[str, Any]:
    """TASK_CONFIG row, with meteorite pass/fail/error overlay for shared GDL keys."""
    cfg = dict(_consult_orchestration(task_key))
    overlay = METEORITE_GDL_OUTCOME_BY_TASK.get((task_key or "").strip())
    if overlay and _entity_state_is_meteorite(entity_state):
        cfg.update(overlay)
    return cfg


def _render_pass_fail(task_key: str, grades: list, entity_state: Optional[str] = None) -> str:
    """Binary grading (AST-357): F with confidence 2–5 fails; all literal X fails; no confidence > 1 fails.
    grades: [{vector, grade, confidence, ...}, ...].
    Raises KeyError if orchestration lookup fails (missing TASK_CONFIG key)."""
    cfg = _consult_orchestration_for_entity(task_key, entity_state)
    if not grades:
        logger.debug_detail(f"pass_fail task_key={task_key} branch=empty_grades -> fail")
        return cfg["fail_state"]
    if any(
        g.get("grade") == "F"
        and isinstance(g.get("confidence"), int)
        and g["confidence"] >= 2
        for g in grades
    ):
        logger.debug_detail(f"pass_fail task_key={task_key} branch=F2_dealbreaker -> fail grades={grades!r}")
        return cfg["fail_state"]
    if all(g.get("grade") == "X" for g in grades):
        logger.debug_detail(f"pass_fail task_key={task_key} branch=all_literal_X -> fail")
        return cfg["fail_state"]
    if not any(isinstance(g.get("confidence"), int) and g["confidence"] > 1 for g in grades):
        logger.debug_detail(f"pass_fail task_key={task_key} branch=no_confidence_gt_1 -> fail grades={grades!r}")
        return cfg["fail_state"]
    logger.debug_detail(f"pass_fail task_key={task_key} branch=pass -> {cfg['pass_state']}")
    return cfg["pass_state"]


_CODE_SUFFIX = re.compile(r'\s*\([A-Z]{2}\)\s*$')

def _strip_code(name: str) -> str:
    """Strip trailing ' (XX)' code suffix the model appends to vector names, e.g. 'Foo (CR)' → 'Foo'."""
    return _CODE_SUFFIX.sub('', name).strip()


def _find_rubric_criterion(rubric_criteria: list, vector_label: str):
    """Return the criterion dict matching vector by stripped label or code (AST-707 / AST-1193)."""
    target = _strip_code((vector_label or "").strip())
    t_upper = target.upper()
    for item in rubric_criteria or []:
        if not isinstance(item, dict):
            continue
        lab = _strip_code(str(item.get("label") or "").strip())
        code = str(item.get("code") or "").strip().upper()
        if lab != target and code != t_upper:
            continue
        return item
    return None


def _candidate_id_from_ctx(ctx: Optional[Dict[str, Any]]) -> str:
    return str((ctx or {}).get("astral_candidate_id") or "")


def _rubric_criteria_for_cfg(candidate_id: str, cfg: dict) -> list:
    """Table-backed rubric criteria for a TASK_CONFIG / orchestration row (AST-723)."""
    rk = (cfg or {}).get("rubric_artifact")
    owner = RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY.get(rk) if rk else None
    if not owner or not candidate_id:
        return []
    from src.core.candidate import rubric_criteria_for_task

    return rubric_criteria_for_task(candidate_id, owner)


def _vector_labels_map(rubric_criteria: list) -> Dict[str, str]:
    return {item["code"]: item["label"] for item in rubric_criteria if item.get("code") and item.get("label")}


def _lookup_rubric_reason_for_grade(rubric_criteria: list, vector_label: str, letter: str) -> str:
    """Rubric line description for this vector + grade letter (AST-351). Raises ValueError if missing."""
    item = _find_rubric_criterion(rubric_criteria, vector_label)
    if item is None:
        raise ValueError(f"No rubric criterion matching vector {vector_label!r}")
    lt = (letter or "").upper()
    gd = item.get("grade_descriptions")
    if isinstance(gd, list):
        for row in gd:
            if str(row.get("grade", "")).upper() == lt:
                desc = row.get("description")
                if desc is not None and str(desc).strip():
                    return str(desc).strip()
    try:
        rows = rubric_text.parse_trailing_grade_table_lines(item.get("content") or "")
    except ValueError:
        rows = []
    for row in rows:
        if row["grade"].upper() == lt:
            return row["description"]
    raise ValueError(f"No rubric description for vector {vector_label!r} grade {letter}")

def _hydrate_grade_reasons_from_rubric(grades: list, rubric_criteria: list) -> None:
    if not rubric_criteria:
        raise ValueError("rubric criteria missing or empty; cannot hydrate grade reasons")
    for g in grades:
        if not isinstance(g, dict):
            continue
        g["reason"] = _lookup_rubric_reason_for_grade(
            rubric_criteria, str(g.get("vector") or ""), str(g.get("grade") or "")
        )


def _rubric_snapshot_for_job_data(rubric_criteria: list) -> list:
    """Analysis-time rubric criteria for list headers (AST-1063). Omits content."""
    if not isinstance(rubric_criteria, list) or not rubric_criteria:
        return []
    out: list = []
    for item in rubric_criteria:
        if not isinstance(item, dict):
            continue
        work = dict(item)
        gd = work.get("grade_descriptions")
        if not gd:
            try:
                rubric_text.ensure_criterion_grade_table(work)
                gd = work.get("grade_descriptions")
            except ValueError:
                gd = []
        out.append({
            "code": work.get("code"),
            "label": work.get("label"),
            "importance": work.get("importance"),
            "grade_descriptions": gd if isinstance(gd, list) else [],
        })
    return out


def _hydrate_response_jobs_grade_reasons(jobs: list, rubric_criteria: list) -> None:
    for job in jobs:
        if not isinstance(job, dict):
            continue
        glist = job.get("grades")
        if isinstance(glist, list):
            _hydrate_grade_reasons_from_rubric(glist, rubric_criteria)


# AST-603: shared rubric response normalization (prefilter + future consult reuse).
_LINK_PREFIX_RE = re.compile(r"^(?:JOB|CULT):(.+)$", re.I)
_ENCODED_LINE_RE = re.compile(r"^\d{1,3}\|")


def _should_decode_as_encoded_line(text: str) -> bool:
    """True when a pipe line has AST-357 encoded grade segments (e.g. RCA3), not letter-pipe grades."""
    from src.core.agent import _GRADE_SEG

    line = next((ln.strip() for ln in text.splitlines() if ln.strip()), text.strip())
    fields = [f.strip() for f in line.split("|")]
    if fields and re.match(r"^\d{1,3}$", fields[0]):
        fields = fields[1:]
    for f in fields:
        norm = "".join(ch for ch in f if ch not in " -:")
        if _GRADE_SEG.match(norm):
            return True
    return False


def _parse_link_index_field(field: str) -> List[int]:
    """Comma/bracket/JOB:/CULT: index lists → list[int]."""
    if field is None:
        return []
    s = str(field).strip()
    if not s:
        return []
    m = _LINK_PREFIX_RE.match(s)
    if m:
        s = m.group(1).strip()
    if s.startswith("[") and s.endswith("]"):
        s = s[1:-1]
    out: List[int] = []
    for part in re.split(r"[,;\s]+", s):
        part = part.strip()
        if not part:
            continue
        try:
            out.append(int(part))
        except ValueError:
            continue
    return out


def _apply_prefilter_encoded_link_meta(job: dict, meta: list[str]) -> None:
    """Map JOB:/CULT: prefixes and positional bracket link_set tails onto job row (AST-697)."""
    possible: List[int] = []
    culture: List[int] = []
    positional: List[str] = []
    for m in meta:
        if re.match(r"^JOB:", m, re.I):
            possible.extend(_parse_link_index_field(m))
            continue
        if re.match(r"^CULT:", m, re.I):
            culture.extend(_parse_link_index_field(m))
            continue
        positional.append(m)
    culture_pos: List[str]
    if positional and not possible:
        possible = _parse_link_index_field(positional[0])
        culture_pos = positional[1:]
    else:
        # Prefix filled job links — remaining positionals map to culture (plan: JOB:16|[51,46]).
        culture_pos = positional
    for lf in culture_pos:
        culture.extend(_parse_link_index_field(lf))
    if possible:
        job["possible_job_links"] = possible
    if culture:
        job["culture_links_to_explore"] = culture


def _extract_grade_letter(val: Any) -> Optional[str]:
    if isinstance(val, dict):
        g = val.get("grade") or val.get("Grade")
        if g is not None:
            s = str(g).strip().upper()
            return s[:1] if s else None
    if val is None:
        return None
    s = str(val).strip().upper()
    if len(s) == 1:
        return s
    return s[:1] if s else None


def _extract_grade_confidence(val: Any) -> int:
    if isinstance(val, dict):
        conf = val.get("confidence") or val.get("Confidence")
        if isinstance(conf, int):
            return conf
        if conf is not None:
            try:
                return int(conf)
            except (TypeError, ValueError):
                pass
    return 3


def _pascal_from_snake(snake: str) -> str:
    return "".join(p.capitalize() for p in re.split(r"[_\s]+", snake) if p)


def _criterion_json_keys(criterion: dict) -> List[str]:
    keys: List[str] = []
    code = (criterion.get("code") or "").strip()
    label = (criterion.get("label") or "").strip()
    if code:
        keys.extend([code, code.lower(), code.upper()])
    if label:
        snake = re.sub(r"[^\w]+", "_", label).strip("_")
        keys.extend([label, snake, snake.lower(), snake.upper(), _pascal_from_snake(snake)])
    seen = set()
    ordered: List[str] = []
    for k in keys:
        if k and k not in seen:
            seen.add(k)
            ordered.append(k)
    return ordered


def _grade_letter_for_criterion(obj: dict, criterion: dict) -> Optional[str]:
    lower_map = {str(k).lower(): k for k in obj.keys() if isinstance(k, str)}
    for ck in _criterion_json_keys(criterion):
        raw = obj.get(ck)
        if raw is None and ck.lower() in lower_map:
            raw = obj.get(lower_map[ck.lower()])
        letter = _extract_grade_letter(raw)
        if letter and letter in ASTRAL_CONFIG.get("valid_grades", []):
            return letter
    return None


def _coerce_link_list(val: Any) -> List[int]:
    if val is None:
        return []
    if isinstance(val, int):
        return [val]
    if isinstance(val, list):
        out: List[int] = []
        for item in val:
            out.extend(_coerce_link_list(item))
        return out
    return _parse_link_index_field(str(val))


def _json_link_fields(obj: dict) -> Tuple[List[int], List[int]]:
    lower_map = {str(k).lower(): k for k in obj.keys() if isinstance(k, str)}
    job_keys = ("possible_job_links", "possiblejoblinks", "possible_job_link")
    cult_keys = (
        "culture_links_to_explore",
        "culturelinkstoexplore",
        "culture_links",
    )
    possible: List[int] = []
    culture: List[int] = []
    for variants, dest in ((job_keys, possible), (cult_keys, culture)):
        for vk in variants:
            raw = obj.get(vk)
            if raw is None and vk.lower() in lower_map:
                raw = obj.get(lower_map[vk.lower()])
            if raw is not None:
                dest.extend(_coerce_link_list(raw))
                break
    return possible, culture


def _ensure_jobs_astral_ids(jobs: list, batch_entities: list) -> None:
    for i, job in enumerate(jobs):
        if not isinstance(job, dict):
            continue
        if job.get("astral_job_id"):
            continue
        if i < len(batch_entities):
            job["astral_job_id"] = batch_entities[i].get("astral_job_id")


def _bind_response_jobs_to_claimed(response_jobs: list, claimed_jobs: list) -> None:
    """Rewrite placeholder / single-job mismatched astral_job_id to claimed ids (AST-1076).

    Assemble prefixes use 000/001…; fields-output Ruth often echoes that as astral_job_id.
    """
    claimed_ids = [j["astral_job_id"] for j in claimed_jobs if j.get("astral_job_id")]
    if not response_jobs or not claimed_ids:
        return
    claimed_set = set(claimed_ids)
    # Single-job: any non-claimed echo (e.g. "000") → sole claim id.
    if len(response_jobs) == 1 and len(claimed_ids) == 1:
        if not isinstance(response_jobs[0], dict):
            return
        aid = (response_jobs[0].get("astral_job_id") or "").strip()
        if aid not in claimed_set:
            response_jobs[0]["astral_job_id"] = claimed_ids[0]
        return
    # Ordered: empty or \\d{1,3} position echoes only — leave non-digit fabricated UUIDs alone.
    if len(response_jobs) != len(claimed_ids):
        return
    for i, rj in enumerate(response_jobs):
        if not isinstance(rj, dict):
            continue
        aid = (rj.get("astral_job_id") or "").strip()
        if aid in claimed_set:
            continue
        if not aid or re.fullmatch(r"\d{1,3}", aid):
            rj["astral_job_id"] = claimed_ids[i]


def _bind_response_jobs_by_job_link(response_jobs: list, claimed_jobs: list) -> None:
    """Bind unmatched response rows to claimed jobs by normalized job_link (AST-1133).

    Used when Ruth puts a non-digit wrong value in astral_job_id on multi-job
    qualify_meteorite batches. Does not overwrite ids already in the claim set.
    """
    if not response_jobs or not claimed_jobs:
        return
    claimed_ids = [j["astral_job_id"] for j in claimed_jobs if j.get("astral_job_id")]
    claimed_set = set(claimed_ids)
    # Unique normalized link → claim id; drop keys that collide across claims.
    claimed_by_link: Dict[str, str] = {}
    ambiguous: set = set()
    for j in claimed_jobs:
        aid = j.get("astral_job_id")
        if not aid:
            continue
        norm = normalize_link(j.get("job_link") or "")
        if not norm or norm in ambiguous:
            continue
        if norm in claimed_by_link:
            claimed_by_link.pop(norm, None)
            ambiguous.add(norm)
            continue
        claimed_by_link[norm] = aid
    assigned = {
        (rj.get("astral_job_id") or "").strip()
        for rj in response_jobs
        if isinstance(rj, dict) and (rj.get("astral_job_id") or "").strip() in claimed_set
    }
    for rj in response_jobs:
        if not isinstance(rj, dict):
            continue
        aid = (rj.get("astral_job_id") or "").strip()
        if aid in claimed_set:
            continue
        norm = normalize_link(rj.get("job_link") or "")
        if not norm:
            continue
        target = claimed_by_link.get(norm)
        if not target or target in assigned:
            continue
        rj["astral_job_id"] = target
        assigned.add(target)


def _job_from_rubric_json(obj: dict, task_config: dict, ctx: dict) -> dict:
    rubric = _rubric_criteria_for_cfg(_candidate_id_from_ctx(ctx), task_config)
    grade_rows: List[Dict[str, Any]] = []
    for crit in rubric:
        letter = _grade_letter_for_criterion(obj, crit)
        if not letter:
            continue
        raw = None
        for ck in _criterion_json_keys(crit):
            if ck in obj:
                raw = obj[ck]
                break
            lower_map = {str(k).lower(): k for k in obj.keys() if isinstance(k, str)}
            if ck.lower() in lower_map:
                raw = obj.get(lower_map[ck.lower()])
                break
        conf = _extract_grade_confidence(raw) if raw is not None else 3
        grade_rows.append({"vector": crit["label"], "grade": letter, "confidence": conf})
    possible, culture = _json_link_fields(obj)
    job: Dict[str, Any] = {"grades": grade_rows}
    if possible:
        job["possible_job_links"] = possible
    if culture:
        job["culture_links_to_explore"] = culture
    return job


def _job_from_letter_pipe(text: str, task_config: dict, ctx: dict) -> dict:
    valid = set(ASTRAL_CONFIG.get("valid_grades") or [])
    rubric = _rubric_criteria_for_cfg(_candidate_id_from_ctx(ctx), task_config)
    n = len(rubric)
    line = next((ln.strip() for ln in text.splitlines() if ln.strip()), text.strip())
    fields = [f.strip() for f in line.split("|")]
    if fields and re.match(r"^\d{1,3}$", fields[0]):
        fields = fields[1:]
    grade_rows: List[Dict[str, Any]] = []
    link_fields: List[str] = []
    for f in fields:
        if len(grade_rows) < n and len(f) == 1 and f.upper() in valid:
            grade_rows.append(
                {"vector": rubric[len(grade_rows)]["label"], "grade": f.upper(), "confidence": 3}
            )
        else:
            link_fields.append(f)
    job: Dict[str, Any] = {"grades": grade_rows}
    if link_fields:
        job["possible_job_links"] = _parse_link_index_field(link_fields[0])
        culture: List[int] = []
        for lf in link_fields[1:]:
            culture.extend(_parse_link_index_field(lf))
        if culture:
            job["culture_links_to_explore"] = culture
    return job


def _normalize_rubric_task_response(task_key: str, task_config: dict, parsed: Any, ctx: dict) -> dict:
    """Turn AST-602 repro shapes into response_schema jobs[] before validation."""
    batch_entities = (ctx or {}).get("batch_entities") or []

    if isinstance(parsed, dict) and isinstance(parsed.get("jobs"), list) and parsed["jobs"]:
        out = dict(parsed)
        _ensure_jobs_astral_ids(out["jobs"], batch_entities)
        return out

    payload = parsed
    if isinstance(parsed, dict) and "agent_payload" in parsed:
        payload = parsed["agent_payload"]
        if isinstance(payload, list):
            payload = "\n".join(str(item) for item in payload)

    if isinstance(payload, dict):
        if isinstance(payload.get("jobs"), list) and payload["jobs"]:
            return _normalize_rubric_task_response(task_key, task_config, payload, ctx)
        job = _job_from_rubric_json(payload, task_config, ctx)
        if len(batch_entities) == 1 and not job.get("astral_job_id"):
            job["astral_job_id"] = batch_entities[0].get("astral_job_id")
        return {"jobs": [job]}

    if isinstance(payload, str):
        text = payload.strip()
        if not text:
            raise ValueError(f"[{task_key}] empty agent_payload")
        if text.startswith("{") or text.startswith("["):
            try:
                obj = json.loads(text)
                if isinstance(obj, dict):
                    return _normalize_rubric_task_response(task_key, task_config, obj, ctx)
            except json.JSONDecodeError:
                pass
        first_line = next((ln.strip() for ln in text.splitlines() if ln.strip()), "")
        if _ENCODED_LINE_RE.match(first_line) and _should_decode_as_encoded_line(text):
            from src.core.agent import _decode_payload

            output_type = task_config.get("output_type", "")
            decoded = _decode_payload(task_key, output_type, text, ctx or {})
            _ensure_jobs_astral_ids(decoded.get("jobs") or [], batch_entities)
            return decoded
        job = _job_from_letter_pipe(text, task_config, ctx)
        if len(batch_entities) == 1:
            job["astral_job_id"] = batch_entities[0].get("astral_job_id")
        return {"jobs": [job]}

    raise ValueError(f"[{task_key}] unrecognised rubric response shape: {type(parsed).__name__}")


def _effective_no_signal_for_score(g: dict) -> bool:
    """True when this row contributes no signal to scored numerator (literal X or confidence 1)."""
    letter = g.get("grade")
    conf = g.get("confidence")
    if letter == "X":
        return True
    if conf == 1:
        return True
    return False


def _importance_for_label(rubric_criteria: list, vector_label: str) -> float:
    default = ASTRAL_CONFIG["consult_importance"]["default_vector_importance"]
    item = _find_rubric_criterion(rubric_criteria, vector_label)
    if item is None:
        raise ValueError(f"_render_score: no rubric criterion matching vector {vector_label!r}")
    imp = item.get("importance")
    if imp is None:
        return importance_multiplier(int(default))
    return importance_multiplier(int(imp))


class IncompleteGradeSetError(ValueError):
    """Decoded grades are not an exact match to live rubric labels (AST-1155)."""


def _grade_set_vector_diff(
    rubric_criteria: list,
    grades: list,
) -> tuple:
    """Return (missing_labels, unexpected_labels) using _strip_code on rubric labels vs grade vectors."""
    expected = {
        _strip_code(str(item.get("label") or "").strip())
        for item in (rubric_criteria or [])
        if item.get("label")
    }
    actual = {
        _strip_code(str(g.get("vector") or "").strip())
        for g in (grades or [])
        if isinstance(g, dict) and g.get("vector")
    }
    return expected - actual, actual - expected


def _require_complete_grade_set(rubric_criteria: list, grades: list) -> None:
    """Raise IncompleteGradeSetError when grades are not an exact match to live rubric labels."""
    missing, extra = _grade_set_vector_diff(rubric_criteria, grades)
    if missing:
        raise IncompleteGradeSetError(f"_render_score: missing vectors {sorted(missing)}")
    if extra:
        raise IncompleteGradeSetError(f"_render_score: unknown vectors {sorted(extra)}")


def _debug_incomplete_grade_set(
    *,
    func: str,
    identifier: str,
    rubric_criteria: list,
    grades: list,
    dest: Optional[str],
    index: int = 1,
    total: int = 1,
) -> None:
    missing, extra = _grade_set_vector_diff(rubric_criteria, grades)
    logger.debug_index(
        func=func,
        index=index,
        total=total,
        identifier=identifier,
        outcome=f"incomplete grade set -> {dest or '?'}",
    )
    logger.debug_detail(
        f"missing={sorted(missing)} | unexpected={sorted(extra)} | "
        f"decoded_vectors={sorted(_strip_code(str(g.get('vector') or '')) for g in (grades or []) if isinstance(g, dict))}"
    )


def _render_score(
    consult_cfg: dict,
    rubric_criteria: list,
    grades: list,
    pass_threshold: float,
) -> Tuple[str, Optional[float]]:
    """Scored grading (AST-358): base × grade density × importance × confidence (AST-357).
    F with confidence 2–5 = instant fail. X / conf-1 / F1 excluded from V. Score normalized 0–10 vs RUBRIC_TOTAL."""
    if any(
        g.get("grade") == "F"
        and isinstance(g.get("confidence"), int)
        and g["confidence"] >= 2
        for g in grades
    ):
        logger.debug_detail(f"branch=F2_dealbreaker scored_fail grades={grades!r}")
        return (consult_cfg["fail_state"], None)
    _require_complete_grade_set(rubric_criteria, grades)
    counted = [g for g in grades if not _effective_no_signal_for_score(g)]
    v = len(counted)
    rubric_score = 0.0
    if v > 0:
        base = float(RUBRIC_TOTAL) / v
        for g in counted:
            conf = g.get("confidence")
            if not isinstance(conf, int):
                raise ValueError(f"_render_score: confidence must be int for vector {g.get('vector')!r}")
            m = CONFIDENCE_MULTIPLIERS.get(conf)
            if m is None:
                raise ValueError(f"_render_score: invalid confidence {conf!r} for vector {g.get('vector')!r}")
            gv = grade_value(g["grade"])
            density = (gv / MAX_GRADE_VALUE) * m
            imp = _importance_for_label(rubric_criteria, g["vector"])
            contrib = base * density * imp
            rubric_score += contrib
            logger.debug_detail(
                f"vec={g.get('vector')!r} grade={g.get('grade')} conf={conf} "
                f"base={base} density={density} imp={imp} contrib={contrib}"
            )
    score = (rubric_score / float(RUBRIC_TOTAL)) * 10.0
    logger.debug_detail(
        f"rubric_score={rubric_score} score={score} threshold={pass_threshold} v={v}"
    )
    if score < pass_threshold:
        logger.debug_detail(
            f"branch=below_threshold -> fail score={score} threshold={pass_threshold}"
        )
        return (consult_cfg["fail_state"], score)
    logger.debug_detail(
        f"branch=pass -> {consult_cfg['pass_state']} score={score} threshold={pass_threshold}"
    )
    return (consult_cfg["pass_state"], score)


def _latest_score_value(raw: Optional[float]) -> Optional[float]:
    """Normalize score for persistence; None means keep existing latest_score."""
    return None if raw is None else float(raw)


def _task_config_scored(task_key: str) -> bool:
    """TASK_CONFIG.scored flag for task behavior."""
    return bool((TASK_CONFIG.get(task_key) or {}).get("scored"))


_GRADE_DISPATCH_TO_HEADER = {
    "grade_do": "DO",
    "grade_get": "GET",
    "grade_like": "LIKE",
    "meteorite_like": "LIKE",
}


def _transition_job_state_for_task(task_key: str, job_ids: List[str], to_state: str, score: Optional[float] = None) -> None:
    normalized_score = _latest_score_value(score)
    if _task_config_scored(task_key) and normalized_score is not None:
        tracker.transition_job_state(job_ids, to_state, score=normalized_score)
        return
    tracker.transition_job_state(job_ids, to_state)


async def _prep_live_content(
    job: Dict,
    company: Optional[Dict] = None,
    scoring_task_key: Optional[str] = None,
    position: int = 0,
) -> Any:
    """Assemble live_content for an agent call. JD via tracker coat-check.
    If company provided, appends website_content via roster coat-check.
    Row label is [index=NNN]: … (same keyed style as evaluate_jd enumerate_array); decode maps pos via batch_entities, not IDs in the prompt.
    Returns live_content string, or False if website_content fetch failed."""
    jd_text = await tracker.get_job_data(job, "job_description")
    if not jd_text:
        return False
    content = f"[index={position:03d}]: {jd_text}"
    if not company:
        return content
    # Lazy import: roster imports consult helpers; breaks cycle at module load (AST-507 + AST-513).
    from src.core import roster

    website_content = await roster.get_company_data(company, "website_content")
    if website_content is None:
        # Website content unavailable — set retryable state, signal failure to caller
        if scoring_task_key:
            _transition_job_state_for_task(scoring_task_key, [job["astral_job_id"]], "NEED_WEBSITE_CONTENT")
        else:
            tracker.transition_job_state([job["astral_job_id"]], "NEED_WEBSITE_CONTENT")
        return False
    if isinstance(website_content, list):
        vibes = "\n\n".join(
            f"=== {p['url']} ===\n{p['content']}" for p in website_content if p.get("content")
        )
    else:
        vibes = str(website_content)
    return f"{content}\n\n=== COMPANY CONTEXT ===\n{vibes}" if vibes else content


def _analysis_phase_rubric_snapshot_key(grades_key: str) -> str:
    """Job-carried snapshot key for a grades_key (AST-1063 write: ``{save_prefix}_rubric``).

    Couples to ``grades_key == f\"{save_prefix}_grades\"`` — same stem both sides today.
    """
    if not isinstance(grades_key, str) or not grades_key.endswith("_grades"):
        return ""
    return grades_key[:-7] + "_rubric"


def _format_analysis_phase_text(
    phase_token: str,
    job_data: dict,
    candidate_data: dict,
    *,
    debug: bool = False,
    job_id: str = "",
    phase_index: int = 1,
    phase_total: int = 1,
) -> str:
    """Human-readable consult recap for one ANALYSIS_* token (AST-513 / AST-1193).

    Meteorite-sourced jobs score ANALYSIS_JD against evaluate_meteorite's own rubric, not
    evaluate_jd's — analysis_phases_meteorite_override supplies the swapped owner/artifact.
    Live label-or-code first; on miss, job-carried ``*_rubric`` snapshot identity + live content-by-code.
    """
    log = get_logger(__name__, debug_flag=debug)
    phases = dict(JOB_TOKEN_CONFIG.get("analysis_phases") or {})
    if _entity_state_is_meteorite((job_data or {}).get("state")):
        phases.update(JOB_TOKEN_CONFIG.get("analysis_phases_meteorite_override") or {})
    phase_cfg = phases.get(phase_token)
    live_criteria: list = []
    snapshot: list = []
    found = 0
    recorded = 0

    def _emit_debug(text: str) -> None:
        if not debug:
            return
        log.debug_index(
            func="_format_analysis_phase_text",
            index=phase_index,
            total=phase_total,
            identifier=f"{job_id}:{phase_token}",
            outcome="formatted" if text else "empty",
        )
        log.debug_detail(
            f"found_grades={found} recorded_vectors={recorded} "
            f"live_criteria={len(live_criteria)} snapshot_criteria={len(snapshot)}"
        )

    if not phase_cfg:
        _emit_debug("")
        return ""
    grades_key = phase_cfg.get("grades_key") or ""
    grades = job_data.get(grades_key)
    if not isinstance(grades, list) or not grades:
        _emit_debug("")
        return ""
    snap_key = _analysis_phase_rubric_snapshot_key(str(grades_key))
    raw_snap = job_data.get(snap_key) if snap_key else None
    snapshot = raw_snap if isinstance(raw_snap, list) else []
    owner = phase_cfg.get("rubric_owner_task_key")
    cid = str((candidate_data or {}).get("_astral_candidate_id") or "")
    if owner and cid:
        from src.core.candidate import rubric_criteria_for_task

        live_criteria = rubric_criteria_for_task(cid, owner)
    blocks: List[str] = []
    for g in grades:
        if not isinstance(g, dict):
            continue
        vector_label = str(g.get("vector") or "").strip()
        if not vector_label:
            continue
        found += 1
        criterion = _find_rubric_criterion(live_criteria, vector_label)
        title = ""
        rubric_blob = ""
        snapshot_hit = False
        if criterion is not None:
            title = str(criterion.get("label") or vector_label).strip()
            rubric_blob = str(criterion.get("content") or "").strip()
        else:
            snap_row = _find_rubric_criterion(snapshot, vector_label) if snapshot else None
            if snap_row is not None:
                snapshot_hit = True
                title = str(snap_row.get("label") or vector_label).strip()
                code = str(snap_row.get("code") or "").strip()
                live_by_code = _find_rubric_criterion(live_criteria, code) if code else None
                if live_by_code is not None:
                    title = str(live_by_code.get("label") or title).strip()
                    rubric_blob = str(live_by_code.get("content") or "").strip()
        if criterion is None and not snapshot_hit:
            logger.warning(
                "_format_analysis_phase_text: no rubric criterion for vector %r (phase=%s)",
                vector_label,
                phase_token,
            )
            continue
        letter = str(g.get("grade") or "").strip().upper()
        conf = g.get("confidence")
        conf_s = f"{int(conf)}/5" if isinstance(conf, (int, float)) else "0/5"
        blocks.append(
            f"CONSIDER: {title}\n{rubric_blob}\nANALYSIS RESULT: {letter} ({conf_s} confidence)"
        )
        recorded += 1
    text = "\n\n".join(blocks)
    _emit_debug(text)
    return text


def build_job_token_context(
    job: Dict[str, Any], candidate_data: dict, *, candidate_id: str = "", debug: bool = False
) -> Dict[str, str]:
    """Precomputed job-scoped prompt tokens for artifact single-job calls (AST-513 / AST-1193)."""
    from src.core.candidate import enabled_resume_structure_sections, resolve_resume_structure

    cd = dict(candidate_data or {})
    cid = candidate_id or str(cd.get("_astral_candidate_id") or "")
    if cid:
        cd["_astral_candidate_id"] = cid
    jd_data = job.get("job_data") if isinstance(job.get("job_data"), dict) else {}
    visible = (jd_data.get("job_description") or "").strip()
    out: Dict[str, str] = {"VISIBLE_JD": visible}
    phase_tokens = tuple((JOB_TOKEN_CONFIG.get("analysis_phases") or {}).keys())
    job_id = str(job.get("astral_job_id") or "")
    total = len(phase_tokens)
    for i, key in enumerate(phase_tokens, start=1):
        out[key] = _format_analysis_phase_text(
            key, jd_data, cd, debug=debug, job_id=job_id, phase_index=i, phase_total=total
        )
    structure = resolve_resume_structure(cd)
    catalog_lines: List[str] = []
    sections = (structure.get("sections") or {}) if isinstance(structure.get("sections"), dict) else {}
    for row in enabled_resume_structure_sections(structure):
        sid = row["id"]
        spec = sections.get(sid) if isinstance(sections.get(sid), dict) else {}
        title = spec.get("title") or row.get("label") or sid
        editable = spec.get("job_agent_editable", False)
        catalog_lines.append(f"{sid}: {title} (job_agent_editable={str(bool(editable)).lower()})")
    out["RESUME_SECTION_CATALOG"] = "\n".join(catalog_lines)
    return out


def _serialize_do_get_like_bundle(job_data: Dict[str, Any]) -> str:
    """Recap DO/GET/LIKE for analysis_upshot; keys match render_verdict save_prefixes (do/get/like)."""
    lines: List[str] = []
    for prefix, label in (("do", "DO"), ("get", "GET"), ("like", "LIKE")):
        grades = job_data.get(f"{prefix}_grades")
        score = job_data.get(f"{prefix}_score")
        notes = job_data.get(f"{prefix}_notes")
        if grades is None and score is None and notes is None:
            continue
        lines.append(f"--- {label} ---")
        if grades is not None:
            lines.append(json.dumps(grades, ensure_ascii=False, default=str))
        if score is not None:
            lines.append(f"score: {score!r}")
        if notes:
            lines.append(f"notes: {notes!r}")
    if not lines:
        return ""
    return "=== PRIOR CONSULT (DO / GET / LIKE) ===\n" + "\n".join(lines)


async def _prep_analysis_upshot_live_content(
    job: Dict[str, Any],
    company: Optional[Dict[str, Any]],
    scoring_task_key: str = "analysis_upshot",
) -> Any:
    """Coat-check JD + website (same as render_verdict LIKE); add raw_job_listing + DO/GET/LIKE recap."""
    base = await _prep_live_content(job, company, scoring_task_key=scoring_task_key)
    if not base:
        return False
    jd_data = job.get("job_data") if isinstance(job.get("job_data"), dict) else {}
    raw_listing = (jd_data.get("raw_job_listing") or "").strip()
    consult_recap = _serialize_do_get_like_bundle(jd_data)
    parts: List[str] = []
    if raw_listing:
        parts.append(f"=== RAW JOB LISTING (qualify context) ===\n{raw_listing}")
    parts.append(base)
    if consult_recap:
        parts.append(consult_recap)
    return "\n\n".join(parts)


async def _run_analysis_upshot_batch(
    batch_id: str,
    entities: List[Dict[str, Any]],
    ctx: Optional[Dict[str, Any]],
    debug: bool,
    task_key: str = "analysis_upshot",
) -> Dict[str, int]:
    """AST-480 / AST-1055: synthesis upshot; persist job_data.analysis_upshot → pass_state."""
    if debug:
        logger.set_debug_flag(True)
    task_cfg = TASK_CONFIG[task_key]
    processed = passed = failed = errors = 0
    base_ctx = dict(ctx or {})
    for job in entities:
        aid = job["astral_job_id"]
        processed += 1
        row = tracker.get_job(aid) or job
        company = None
        if task_cfg.get("requires_company"):
            company = tracker.get_company(row["company"])
            if not company:
                dest = _consult_batch_fail_dest(row.get("state"), task_cfg.get("error_state"))
                if dest:
                    _transition_job_state_for_task(task_key, [aid], dest)
                errors += 1
                continue
        live_content = await _prep_analysis_upshot_live_content(
            row, company, scoring_task_key=task_key,
        )
        if not live_content:
            fresh = tracker.get_job(aid) or row
            if fresh.get("state") != "NEED_WEBSITE_CONTENT":
                dest = _consult_batch_fail_dest(fresh.get("state"), task_cfg.get("error_state"))
                if dest:
                    _transition_job_state_for_task(task_key, [aid], dest)
            errors += 1
            continue
        task_ctx = {**base_ctx, "batch_entities": [row], "job": row, "batch_size": 1}
        result = await do_task(
            task_key=task_key,
            live_content=live_content,
            index=aid,
            ctx=task_ctx,
            debug=debug,
        )
        if not result.get("success"):
            if is_provider_balance_refusal(result):
                if debug:
                    logger.debug_index(
                        func="consult._run_analysis_upshot_batch",
                        index=processed,
                        total=len(entities),
                        identifier=aid,
                        outcome="provider_balance_refusal — state held",
                    )
                    logger.debug_detail(
                        f"failure_class={result.get('failure_class')!r} error={result.get('error')!r} "
                        f"current_state={row.get('state')!r}"
                    )
                errors += 1
                continue
            dest = _consult_batch_fail_dest(row.get("state"), task_cfg.get("error_state"))
            if dest:
                _transition_job_state_for_task(task_key, [aid], dest)
            errors += 1
            continue
        parsed = result.get("parsed_response")
        if not isinstance(parsed, dict):
            dest = _consult_batch_fail_dest(row.get("state"), task_cfg.get("error_state"))
            if dest:
                _transition_job_state_for_task(task_key, [aid], dest)
            errors += 1
            continue
        # Same job_data key as analysis_upshot so Recommended report consumers keep working.
        tracker.save_job_data(aid, {"analysis_upshot": parsed})
        _transition_job_state_for_task(task_key, [aid], task_cfg["pass_state"])
        passed += 1
    return {
        "total_processed": processed,
        "total_passed": passed,
        "total_failed": failed,
        "total_errors": errors,
    }


def _apply_render_verdict_decoded_job(
    dispatch_task_key: str,
    astral_job_id: str,
    response_job: Dict[str, Any],
    cfg: Dict[str, Any],
    ctx: Optional[Dict[str, Any]],
    debug: bool = False,
) -> Tuple[str, Optional[Any], List[Any]]:
    """Decode path: hydrate reasons, graded verdict, persist {prefix}_* + transition (single row or batch)."""
    if debug:
        logger.set_debug_flag(True)
    agent_task = cfg.get("agent_task") or (dispatch_task_key or "").strip()
    grades = response_job.get("grades")
    if not isinstance(grades, list):
        raise ValueError("agent response missing grades")
    rk = cfg.get("rubric_artifact")
    rubric_criteria = _rubric_criteria_for_cfg(_candidate_id_from_ctx(ctx), cfg)
    _hydrate_grade_reasons_from_rubric(grades, rubric_criteria)

    agent_cfg = TASK_CONFIG[agent_task]
    mode = agent_cfg.get("grading_mode", "binary")
    if debug:
        logger.debug_detail(
            f"apply_verdict dispatch_task_key={dispatch_task_key} mode={mode} grades={grades!r}"
        )
    nt = response_job.get("notes")
    notes_tail = nt.strip() if isinstance(nt, str) and nt.strip() else ""

    if mode == "binary":
        job_row = tracker.get_job(astral_job_id) or {}
        to_state = _render_pass_fail(
            dispatch_task_key, grades, entity_state=job_row.get("state"),
        )
        score = None
    elif mode == "scored":
        rubric_key = cfg.get("rubric_artifact")
        if not rubric_key:
            orch_key = (dispatch_task_key or "").strip()
            raise ValueError(f"TASK_CONFIG[{orch_key}] missing rubric_artifact")
        if not rubric_criteria:
            raise ValueError(f"Candidate missing rubric artifact: {rubric_key}")
        artifacts = (ctx or {}).get("candidate_data", {}).get("artifacts", {})
        threshold = artifacts.get(f"{rubric_key}_threshold", cfg.get("pass_threshold", 6.0))
        # Exact set match before score math — incompleteness retries via caller (AST-1155).
        _require_complete_grade_set(rubric_criteria, grades)
        to_state, score = _render_score(cfg, rubric_criteria, grades, float(threshold))
    else:
        raise ValueError(f"Unknown grading_mode: {mode}")

    prefix = cfg.get("save_prefix", dispatch_task_key)
    save_data: Dict[str, Any] = {f"{prefix}_grades": grades}
    normalized_score = _latest_score_value(score)
    if _task_config_scored(agent_task) and normalized_score is not None:
        save_data[f"{prefix}_score"] = normalized_score
    elif score is not None:
        save_data[f"{prefix}_score"] = score
    save_data[f"{prefix}_notes"] = notes_tail
    # AST-1063: job-carried rubric for list headers (same criteria as hydrate/score)
    save_data[f"{prefix}_rubric"] = _rubric_snapshot_for_job_data(rubric_criteria)
    tracker.save_job_data(astral_job_id, save_data)
    _transition_job_state_for_task(agent_task, [astral_job_id], to_state, score)
    return to_state, score, grades


async def render_verdict(task_type: str, astral_job_id: str, ctx: Optional[Dict[str, Any]] = None, debug: bool = False) -> Dict[str, Any]:
    """Full pipeline for one job through one agent task.
    Fetches job/company internally, preps live content, calls agent, audits,
    derives verdict, saves grades+score, transitions state.
    ctx: full candidate raft, forwarded to do_task for token resolution + API key override.
    Returns result dict for CLI logging."""
    job = tracker.get_job(astral_job_id)
    cfg = _consult_orchestration_for_entity(
        task_type, (job or {}).get("state") if job else None,
    )
    agent_task = cfg.get("agent_task") or task_type
    error_state = cfg.get("error_state")

    if debug:
        logger.set_debug_flag(True)
        logger.debug_index(
            func="consult.render_verdict",
            index=1,
            total=1,
            identifier=astral_job_id,
            outcome="single-job consult start",
        )
        logger.debug_detail(f"task_type={task_type} agent_task={agent_task}")

    def _fail(error: str) -> Dict[str, Any]:
        """Transition to error_state (if configured) and return failure dict."""
        if debug:
            logger.debug_detail(f"render_verdict failed: {error}")
        if error_state:
            _transition_job_state_for_task(agent_task, [astral_job_id], error_state)
        return {"success": False, "to_state": error_state, "error": error}

    if not job:
        return _fail(f"Job not found: {astral_job_id}")

    company = None
    if cfg.get("requires_company"):
        company = tracker.get_company(job["company"])
        if not company:
            return _fail(f"Company not found: {job['company']}")

    live_content = await _prep_live_content(job, company, scoring_task_key=agent_task)
    if not live_content:
        # _prep_live_content may have already transitioned to NEED_WEBSITE_CONTENT
        # for the LIKE case — don't clobber with error_state
        if company is not None:
            return {"success": False, "to_state": "NEED_WEBSITE_CONTENT",
                    "error": f"website_content unavailable for {astral_job_id}"}
        return _fail(f"live_content prep failed for {astral_job_id}")

    # Encoded consult tasks need batch_entities + vector_labels for decode (same as _run_batch_consult).
    cd = (ctx or {}).get("candidate_data", {})
    rubric_criteria = _rubric_criteria_for_cfg(_candidate_id_from_ctx(ctx), cfg)
    vector_labels = _vector_labels_map(rubric_criteria)
    job_row = dict(job)
    task_ctx: Dict[str, Any] = {**(ctx or {}), "batch_entities": [job_row], "vector_labels": vector_labels, "batch_size": 1}

    result = await do_task(task_key=agent_task, live_content=live_content, index=astral_job_id, ctx=task_ctx, debug=debug)

    if not result.get("success"):
        if is_provider_balance_refusal(result):
            current_state = (job.get("state") or (tracker.get_job(astral_job_id) or {}).get("state"))
            if debug:
                logger.debug_index(
                    func="consult.render_verdict",
                    index=1,
                    total=1,
                    identifier=astral_job_id,
                    outcome="provider_balance_refusal — state held",
                )
                logger.debug_detail(
                    f"failure_class={result.get('failure_class')!r} error={result.get('error')!r} "
                    f"current_state={current_state!r}"
                )
            return {
                "success": False,
                "to_state": current_state,
                "error": result.get("error"),
                "failure_class": result.get("failure_class"),
                "state_held": True,
            }
        return _fail(result.get("error", "do_task failed"))

    parsed = result["parsed_response"]
    jobs_parse = parsed.get("jobs") if isinstance(parsed, dict) else None
    j0: Optional[Dict[str, Any]] = None
    if isinstance(jobs_parse, list) and jobs_parse:
        for j in jobs_parse:
            if isinstance(j, dict) and j.get("astral_job_id") == astral_job_id:
                j0 = j
                break
        if j0 is None and len(jobs_parse) == 1:
            cand = jobs_parse[0]
            j0 = cand if isinstance(cand, dict) else None
    elif isinstance(parsed, dict) and isinstance(parsed.get("grades"), list):
        # jobs[] omitted — treat top-level grades/notes as this row
        j0 = {"astral_job_id": astral_job_id, "grades": parsed["grades"], "notes": parsed.get("notes")}

    if not isinstance(j0, dict):
        return _fail("decoded payload has no job row for this astral_job_id")

    row_for_apply = dict(j0)
    row_for_apply["astral_job_id"] = astral_job_id

    try:
        to_state, score, grades_out = _apply_render_verdict_decoded_job(
            task_type, astral_job_id, row_for_apply, cfg, ctx, debug=debug,
        )
    except IncompleteGradeSetError as e:
        # Incomplete/extra → retry holding, never first-touch technical (AST-1155).
        dest = _consult_batch_fail_dest(job.get("state"), error_state)
        if debug:
            grades_dbg = row_for_apply.get("grades") if isinstance(row_for_apply.get("grades"), list) else []
            _debug_incomplete_grade_set(
                func="consult.render_verdict",
                identifier=astral_job_id,
                rubric_criteria=rubric_criteria,
                grades=grades_dbg,
                dest=dest,
            )
        if dest:
            _transition_job_state_for_task(agent_task, [astral_job_id], dest)
        return {"success": False, "to_state": dest, "error": str(e)}
    except ValueError as e:
        # Config defect (TASK_CONFIG typo) — not a runtime job failure — matches legacy raise contract.
        es = str(e)
        if es.startswith("Unknown grading_mode:"):
            raise
        return _fail(es)

    if debug:
        logger.debug_index(
            func="consult.render_verdict",
            index=1,
            total=1,
            identifier=astral_job_id,
            outcome=str(to_state),
        )
        logger.debug_detail(f"score={score} grades_count={len(grades_out or [])}")

    return {"success": True, "to_state": to_state, "score": score, "grades": grades_out, "timesheet": result.get("timesheet", {})}


def _consult_batch_fail_dest(entity_state: Optional[str], error_state: Optional[str]) -> Optional[str]:
    """AST-642: route batch consult failure per entity — primary → retry holding, *_RETRY → terminal."""
    st = (entity_state or "").strip()
    if not st:
        return error_state
    retry = JOB_STATES.get(st, {}).get("retry_state")
    if retry:
        return retry
    if st == error_state:
        # analysis_upshot: TASK_CONFIG error_state IS the retry holding (PASSED_LIKE_RETRY)
        return "FAILED_TECHNICAL"
    return error_state


def _transition_batch_consult_failures(
    task_key: str,
    job_rows: List[Dict[str, Any]],
    error_state: Optional[str],
) -> None:
    """Group jobs by per-entity fail dest and transition once per destination."""
    by_dest: Dict[str, List[str]] = {}
    for row in job_rows:
        aid = row.get("astral_job_id")
        if not aid:
            continue
        dest = _consult_batch_fail_dest(row.get("state"), error_state)
        if dest:
            by_dest.setdefault(dest, []).append(aid)
    for dest, ids in by_dest.items():
        _transition_job_state_for_task(task_key, ids, dest)


async def _run_batch_consult(
    task_key: str,
    batch_id: str,
    jobs: List[Dict[str, Any]],
    assemble_fn,   # (jobs) -> live_content str
    process_fn,    # (input_job, response_job, cfg) -> to_state str  (also performs its own saves)
    ctx: Optional[Dict[str, Any]] = None,
    debug: bool = False,
    batch_chunk_index: Optional[int] = None,
) -> Dict[str, Any]:
    """Shared scaffolding for batch Pattern-A consult tasks (ast-326).
    Handles: live_content assembly, single do_task call, ID reconciliation,
    audit, batch error transition, per-job process_fn dispatch.
    Missing IDs and bad_grades route per entity's current state via `_consult_batch_fail_dest`.
    Fabricated IDs are silently dropped.
    batch_chunk_index: parallel dispatcher chunks append suffix for agent_data RESPONSE dedupe (AST-502).
    Returns unified summary dict."""
    entity_state = jobs[0].get("state") if jobs else None
    cfg = _consult_orchestration_for_entity(task_key, entity_state)
    astral_ids = [j["astral_job_id"] for j in jobs]
    input_by_id = {j["astral_job_id"]: j for j in jobs}
    batch_states = sorted({j.get("state") for j in jobs if j.get("state")})
    error_state = cfg.get("error_state")

    if debug:
        logger.set_debug_flag(True)
        logger.debug_index(
            func=f"consult._run_batch_consult({task_key})",
            index=1,
            total=1,
            identifier=task_key,
            outcome=f"batch start n={len(jobs)}",
        )
        logger.debug_detail(
            f"batch_id={batch_id} batch_states={batch_states!r} "
            f"batch_chunk_index={batch_chunk_index!r} astral_ids={astral_ids}"
        )

    live_content = assemble_fn(jobs)
    # Build code→label map from candidate's rubric so _decode_payload can hydrate vector names
    rubric_criteria = _rubric_criteria_for_cfg(_candidate_id_from_ctx(ctx), cfg)
    vector_labels = _vector_labels_map(rubric_criteria)
    # batch_entities + vector_labels passed so do_task/_decode_payload can map pos→id and code→label
    cid = _candidate_id_from_ctx(ctx)
    task_ctx = {**(ctx or {}), "batch_size": len(jobs), "batch_entities": jobs, "vector_labels": vector_labels}
    if cid:
        task_ctx["astral_candidate_id"] = cid
    if ctx and ctx.get("candidate_data") is not None:
        task_ctx["candidate_data"] = ctx["candidate_data"]
    do_index = f"{task_key}_batch_{batch_id}"
    if batch_chunk_index is not None:
        do_index = f"{do_index}_c{batch_chunk_index}"
    result = await do_task(task_key=task_key, live_content=live_content, index=do_index, ctx=task_ctx, debug=debug)

    if not result.get("success"):
        # Envelope failure — whole batch to error_state (unless provider balance refusal — hold)
        if is_provider_balance_refusal(result):
            if debug:
                logger.debug_index(
                    func=f"consult._run_batch_consult({task_key})",
                    index=1,
                    total=1,
                    identifier=task_key,
                    outcome="provider_balance_refusal — batch state held",
                )
                logger.debug_detail(
                    f"error={result.get('error')!r} failure_class={result.get('failure_class')!r}"
                )
            return {
                "success": False,
                "error": result.get("error"),
                "passed": 0,
                "failed": 0,
                "total": len(jobs),
                "failure_class": result.get("failure_class"),
                "state_held": True,
            }
        if debug:
            logger.debug_index(
                func=f"consult._run_batch_consult({task_key})",
                index=1,
                total=1,
                identifier=task_key,
                outcome="do_task failed — batch error transition",
            )
            logger.debug_detail(f"error={result.get('error')!r} error_state={error_state!r}")
        if error_state:
            _transition_batch_consult_failures(task_key, jobs, error_state)
        return {"success": False, "error": result.get("error"), "passed": 0, "failed": 0, "total": len(jobs)}

    parsed = result["parsed_response"]
    response_jobs = parsed["jobs"]

    try:
        _hydrate_response_jobs_grade_reasons(response_jobs, rubric_criteria)
    except ValueError as e:
        logger.error("[%s] grade reason hydration failed: %s", task_key, e)
        if error_state:
            _transition_batch_consult_failures(task_key, jobs, error_state)
        return {
            "success": False,
            "error": str(e),
            "passed": 0,
            "failed": 0,
            "total": len(jobs),
        }

    _bind_response_jobs_to_claimed(response_jobs, jobs)
    if task_key == "qualify_meteorite":
        _bind_response_jobs_by_job_link(response_jobs, jobs)
        if debug:
            bound_ids = [
                (rj.get("astral_job_id") or "").strip()
                for rj in response_jobs
                if isinstance(rj, dict)
            ]
            logger.debug_detail(f"qualify_meteorite bound astral_job_ids={bound_ids}")

    if debug:
        ts = result.get("timesheet", {})
        logger.debug_detail(
            f"do_task returned jobs={len(response_jobs)} "
            f"tokens input={ts.get('inputtotal')} cached={ts.get('inputcached')} output={ts.get('outputtotal')}"
        )

    sent_ids = set(input_by_id.keys())
    received_ids = {rj["astral_job_id"] for rj in response_jobs}
    missing = sent_ids - received_ids
    fabricated = received_ids - sent_ids
    missing_rows: List[Dict[str, Any]] = []
    missing_dest_counts: Dict[str, int] = {}

    if missing:
        missing_rows = [input_by_id[mid] for mid in missing if mid in input_by_id]
        for row in missing_rows:
            d = _consult_batch_fail_dest(row.get("state"), error_state)
            if d:
                missing_dest_counts[d] = missing_dest_counts.get(d, 0) + 1
        if len(missing_dest_counts) == 1:
            sole_dest = next(iter(missing_dest_counts))
            dest_label = f"-> {sole_dest}"
        elif missing_dest_counts:
            dest_label = f"per-entity retry/error routing {dict(sorted(missing_dest_counts.items()))}"
        else:
            dest_label = "(no dest configured)"
        logger.warning(
            "[%s] batch incomplete: %d/%d IDs omitted %s: %s",
            task_key, len(missing), len(sent_ids), dest_label, sorted(missing),
        )
        _transition_batch_consult_failures(task_key, missing_rows, error_state)
    if debug:
        if missing:
            logger.debug_detail(f"MISSING {len(missing)} IDs: {sorted(missing)}")
        if fabricated:
            logger.debug_detail(f"FABRICATED {len(fabricated)} IDs: {sorted(fabricated)}")

    passed = failed = 0
    bad_grades: set = set()

    for job_idx, response_job in enumerate(response_jobs, start=1):
        aid = response_job["astral_job_id"]
        if aid in fabricated:
            continue
        input_job = input_by_id[aid]
        try:
            to_state = process_fn(input_job, response_job, cfg)
        except Exception as e:
            bad_grades.add(aid)
            if debug and isinstance(e, IncompleteGradeSetError):
                _debug_incomplete_grade_set(
                    func=f"consult._run_batch_consult({task_key})",
                    identifier=_consult_job_identifier(input_job),
                    rubric_criteria=rubric_criteria,
                    grades=response_job.get("grades") or [],
                    dest=_consult_batch_fail_dest(input_job.get("state"), error_state),
                    index=job_idx,
                    total=len(response_jobs),
                )
            elif debug:
                logger.debug_index(
                    func=f"consult._run_batch_consult({task_key})",
                    index=job_idx,
                    total=len(response_jobs),
                    identifier=_consult_job_identifier(input_job),
                    outcome="process_fn failed",
                )
                logger.debug_detail(f"astral_job_id={aid} error={e!r} grades={response_job.get('grades')!r}")
            logger.warning(f"[{aid}] process_fn failed: {e} | grades: {response_job.get('grades')}")
            continue
        if debug:
            logger.debug_index(
                func=f"consult._run_batch_consult({task_key})",
                index=job_idx,
                total=len(response_jobs),
                identifier=_consult_job_identifier(input_job),
                outcome=str(to_state),
            )
            logger.debug_detail(
                f"astral_job_id={aid} pass_state={cfg['pass_state']!r} fail_state={cfg['fail_state']!r} "
                f"grades={response_job.get('grades')!r}"
            )
        if to_state == cfg["pass_state"]:
            passed += 1
        else:
            failed += 1

    if debug and missing:
        for mi, mid in enumerate(sorted(missing), start=1):
            row = input_by_id.get(mid)
            d = _consult_batch_fail_dest(row.get("state") if row else None, error_state)
            logger.debug_index(
                func=f"consult._run_batch_consult({task_key})",
                index=mi,
                total=len(missing),
                identifier=mid,
                outcome=f"missing from response -> {d or (row.get('state') if row else '?')}",
            )

    # Tag RESPONSE rows with each processed job entity_id (AST-984)
    agent_ref = result.get("agent_ref")
    if agent_ref:
        processed_ids = received_ids - fabricated - bad_grades
        entity_type = TASK_CONFIG.get(task_key, {}).get("entity_type", "job")
        try:
            ensure_batch_response_entity_ids(entity_type, list(processed_ids), agent_ref)
        except Exception:
            logger.debug("ensure_batch_response_entity_ids failed", exc_info=True)

    # bad_grades → per-entity retry holding or terminal error
    error_ids = list(bad_grades)
    if error_ids:
        bad_rows = [input_by_id[aid] for aid in error_ids if aid in input_by_id]
        if debug and bad_rows:
            for bi, row in enumerate(bad_rows, start=1):
                logger.debug_index(
                    func=f"consult._run_batch_consult({task_key})",
                    index=bi,
                    total=len(bad_rows),
                    identifier=_consult_job_identifier(row),
                    outcome=f"bad_grades -> {_consult_batch_fail_dest(row.get('state'), error_state)}",
                )
                logger.debug_detail(
                    f"astral_job_id={row.get('astral_job_id')!r} from_state={row.get('state')!r}"
                )
        _transition_batch_consult_failures(task_key, bad_rows, error_state)

    errors = []
    if fabricated:
        errors.append(f"fabricated {len(fabricated)} IDs: {sorted(fabricated)}")
    if bad_grades:
        errors.append(f"bad grades on {len(bad_grades)} IDs: {sorted(bad_grades)}")
    truncated_note = None
    if missing:
        missing_dests_set = {
            _consult_batch_fail_dest(r.get("state"), error_state) for r in missing_rows
        } - {None}
        if len(missing_dests_set) == 1:
            sole = next(iter(missing_dests_set))
            truncated_note = f"truncated: {len(missing)} IDs -> {sole}: {sorted(missing)}"
        elif missing_dests_set:
            truncated_note = f"truncated: {len(missing)} IDs — per-entity routing: {sorted(missing)}"
        else:
            truncated_note = f"truncated: {len(missing)} IDs (no dest): {sorted(missing)}"

    if debug:
        logger.debug_detail(
            f"batch end processed={len(jobs)} passed={passed} failed={failed} "
            f"bad_grades={len(bad_grades)} missing={len(missing)} fabricated={len(fabricated)}"
        )

    return {
        "success": not fabricated and not bad_grades,
        "passed": passed,
        "failed": failed,
        "total": len(jobs),
        "missing": sorted(missing) if missing else None,
        "fabricated": sorted(fabricated) if fabricated else None,
        "bad_grades": sorted(bad_grades) if bad_grades else None,
        "error": "; ".join(errors) if errors else None,
        "truncated_note": truncated_note,
    }


async def qualify_job_listings(
    batch_id: str,
    jobs: List[Dict[str, Any]],
    ctx: Optional[Dict[str, Any]] = None,
    debug: bool = False,
    batch_chunk_index: Optional[int] = None,
) -> Dict[str, Any]:
    """Batch job list screen (Pattern A). Thin wrapper over _run_batch_consult (ast-326).

    With ``batch_call_mode=1``, the dispatcher attaches the full backlog (within one ledger batch_id) then may
    split work into chunked parallel ``_run_batch_consult`` calls sized to dispatch_task.batch_size (AST-502);
    otherwise one ``do_task`` for the claimed slice — never per-job ``_warm_then_gather`` fan-out from dispatch.
    AST-501: each chunk invokes one `_run_batch_consult` / one `do_task` for that slice's ``jobs`` list.
    """
    claimed_total = len(jobs)
    task_key = "qualify_job_listings"
    cfg = _consult_orchestration(task_key)

    title_screen_failed = 0
    if any((j.get("state") or "") == "NEW" for j in jobs):
        from src.core.gazer import validate_title_batch

        new_jobs = [j for j in jobs if (j.get("state") or "") == "NEW"]
        meteorite_new = [j for j in new_jobs if is_meteorite_company(j.get("company"))]
        roster_new = [j for j in new_jobs if not is_meteorite_company(j.get("company"))]
        # AST-1152: candidate submission is title qualification — never pattern-screen meteorites.
        meteorite_landing = METEORITE_CONFIG["job_create_state"]
        if debug and meteorite_new:
            logger.set_debug_flag(True)
        for mi, j in enumerate(meteorite_new, start=1):
            aid = j["astral_job_id"]
            tracker.transition_job_state([aid], meteorite_landing)
            if debug:
                logger.debug_index(
                    func="consult.qualify_job_listings",
                    index=mi,
                    total=len(meteorite_new),
                    identifier=_consult_job_identifier(j),
                    outcome=f"re-home meteorite NEW -> {meteorite_landing}",
                )
        if roster_new:
            tr = await validate_title_batch(batch_id, roster_new, ctx or {}, debug=debug)
            title_screen_failed = int(tr.get("failed", 0))
        for j in jobs:
            if (j.get("state") or "") == "NEW" or is_meteorite_company(j.get("company")):
                fresh = tracker.get_job(j["astral_job_id"])
                if fresh:
                    j["state"] = fresh.get("state")
    ai_jobs = [
        j for j in jobs
        if (j.get("state") or "") in ("VALID_TITLE", "VALID_TITLE_RETRY", "NEW_RETRY")
    ]
    if not ai_jobs:
        return {
            "passed": 0,
            "failed": title_screen_failed,
            "total": claimed_total,
        }
    jobs = ai_jobs

    # AST-350: same as evaluate_jd_batch — numeric score for latest_score / dispatch sort (informational).
    rubric_list = _rubric_criteria_for_cfg(_candidate_id_from_ctx(ctx), cfg)
    if debug:
        logger.set_debug_flag(True)
        logger.debug_detail(f"qualify_job_listings batch_id={batch_id} job_count={len(jobs)}")
        for ji, j in enumerate(jobs, start=1):
            listing_len = len(j.get("job_data", {}).get("raw_job_listing", "") or "")
            logger.debug_index(
                func="consult.qualify_job_listings",
                index=ji,
                total=len(jobs),
                identifier=_consult_job_identifier(j),
                outcome="input job",
            )
            logger.debug_detail(
                f"title={j.get('job_title', 'UNKNOWN TITLE')!r} listing_chars={listing_len} "
                f"link={j.get('job_link', 'NO LINK')!r}"
            )
        total_chars = sum(len(j.get("job_data", {}).get("raw_job_listing", "") or "") for j in jobs)
        logger.debug_detail(f"total_listing_chars≈{total_chars}")

    def assemble(jobs):
        # 0-based numbered format — astral_job_id is intentionally excluded from live content
        # so the agent can't echo it back; position mapping is handled in _decode_payload.
        lines = [
            f"{i:03d}: job_site: {j.get('job_site', '')}\nraw_job_listing: {j.get('job_data', {}).get('raw_job_listing', '')}"
            for i, j in enumerate(jobs)
        ]
        return "JOB LISTINGS:\n" + "\n".join(lines)

    def process(input_job, response_job, cfg):
        aid = response_job["astral_job_id"]
        grades = response_job["grades"]
        # Incomplete/extra sets must raise into bad_grades — do not swallow (AST-1155).
        if rubric_list:
            _require_complete_grade_set(rubric_list, grades)
        to_state = _render_pass_fail(task_key, grades)

        def _score_from_grades() -> Optional[float]:
            if not rubric_list:
                return None
            try:
                _, score = _render_score(cfg, rubric_list, grades, 0.0)
                return score
            except (ValueError, KeyError):
                return None

        score = _score_from_grades()

        def _save_joblist_result() -> None:
            save_data: Dict[str, Any] = {
                "joblist_grades": grades,
                "joblist_rubric": _rubric_snapshot_for_job_data(rubric_list),
            }
            normalized_score = _latest_score_value(score)
            if _task_config_scored(task_key) and normalized_score is not None:
                save_data["joblist_score"] = normalized_score
            tracker.save_job_data(aid, save_data)

        if to_state == cfg["fail_state"]:
            # Failing jobs carry no metadata — just save grades and transition
            _save_joblist_result()
            _transition_job_state_for_task(task_key, [aid], to_state, score)
            failed_vecs = [g["vector"] for g in grades if isinstance(grades, list) and g.get("grade") == "F"]
            if not debug:
                logger.info(f"  {input_job.get('job_title') or aid} -> {to_state} [{', '.join(failed_vecs)}]")
            return to_state

        # Passing job — validate title and URL before initializing
        raw_title = (response_job.get("job_title") or "").strip()
        min_len = cfg.get("min_job_title_length", 5)
        if len(raw_title) < min_len:
            dest = _consult_batch_fail_dest(input_job.get("state"), cfg.get("error_state"))
            if debug:
                logger.debug_index(
                    func="consult.qualify_job_listings",
                    index=1,
                    total=1,
                    identifier=_consult_job_identifier(input_job),
                    outcome=f"title too short -> {dest}",
                )
                logger.debug_detail(
                    f"from_state={input_job.get('state')!r} "
                    f"title too short: {repr(raw_title)} min_len={min_len}"
                )
            logger.warning(f"  {aid} -> {dest} [title too short: {repr(raw_title)}]")
            if dest:
                _transition_job_state_for_task(task_key, [aid], dest, score)
            return dest or cfg["error_state"]
        job_link = (response_job.get("job_link") or "").strip()
        if not job_link.startswith("http"):
            if debug:
                logger.debug_detail(f"relative job_link: {job_link!r}")
            logger.warning(f"  {aid} skipped — relative job_link: {job_link}")
            raise ValueError(f"relative job_link: {job_link}")
        if not tracker.initialize_job(aid, input_job["company"], response_job):
            if not debug:
                logger.info(f"  {aid} -> deleted (identity collision)")
            return cfg["fail_state"]
        _save_joblist_result()
        _transition_job_state_for_task(task_key, [aid], to_state, score)
        if not debug:
            logger.info(f"  {input_job.get('job_title') or aid} -> {to_state}")
        return to_state

    result = await _run_batch_consult(
        task_key, batch_id, jobs, assemble, process, ctx, debug, batch_chunk_index=batch_chunk_index,
    )
    if title_screen_failed:
        result = dict(result)
        result["failed"] = int(result.get("failed", 0)) + title_screen_failed
        result["total"] = claimed_total
    return result


async def qualify_meteorite(
    batch_id: str,
    jobs: List[Dict[str, Any]],
    ctx: Optional[Dict[str, Any]] = None,
    debug: bool = False,
    batch_chunk_index: Optional[int] = None,
) -> Dict[str, Any]:
    """Meteorite pre-AI enrich (Pattern A). Same claim/process shape as qualify_job_listings;
    fields output (no grades). AST-1062."""
    task_key = "qualify_meteorite"
    cfg = _consult_orchestration(task_key)
    jd_key = TRACKER_CONFIG["job_data_keys"]["job_description"]

    if debug:
        logger.set_debug_flag(True)
        logger.debug_detail(f"qualify_meteorite batch_id={batch_id} job_count={len(jobs)}")
        for ji, j in enumerate(jobs, start=1):
            jd_len = len((j.get("job_data") or {}).get(jd_key, "") or "")
            logger.debug_index(
                func="consult.qualify_meteorite",
                index=ji,
                total=len(jobs),
                identifier=_consult_job_identifier(j),
                outcome="input job",
            )
            logger.debug_detail(
                f"job_link={(j.get('job_link') or '')!r} job_description_chars={jd_len}"
            )

    def assemble(jobs):
        # 0-based numbered format — astral_job_id excluded from live content (position map in decode/response).
        # AST-1197: CONTENT label matches qualify_meteorite agent_task (stored email HTML / scraped JD).
        lines = [
            f"{i:03d}: job_link: {j.get('job_link') or ''}\n"
            f"CONTENT:\n{(j.get('job_data') or {}).get(jd_key, '') or ''}"
            for i, j in enumerate(jobs)
        ]
        return "METEORITE JOBS:\n" + "\n".join(lines)

    def process(input_job, response_job, cfg):
        aid = response_job["astral_job_id"]
        # Pre-resolve AI strip — source labels derive from this + resolved id (debug only).
        ai_company_job_id = (response_job.get("company_job_id") or "").strip()
        job_title = (response_job.get("job_title") or "").strip()
        ruth_link = (response_job.get("job_link") or "").strip()
        input_link = (input_job.get("job_link") or "").strip()
        jd_text = (response_job.get("jd_text") or "").strip()
        # Ruth http(s) wins; else Create-time ATS URL (list ingest) for gate + UUID resolve.
        if ruth_link.startswith("http"):
            job_link = ruth_link
            link_source = "AI"
        elif input_link.startswith("http"):
            job_link = input_link
            link_source = "input"
        else:
            job_link = ruth_link
            link_source = "neither"
        company_job_id = _resolve_company_job_id(ai_company_job_id, job_link)
        if ai_company_job_id:
            id_source = "AI"
        elif company_job_id:
            id_source = "UUID-from-job_link"
        else:
            id_source = "neither"
        min_title = int(cfg.get("min_job_title_length", 5))
        min_jd = int(cfg.get("min_jd_chars", 40))

        fail_reason = None
        if not company_job_id:
            fail_reason = "empty company_job_id"
        # AST-1152: length/blank content gate only — not roster title-pattern screening.
        elif len(job_title) < min_title:
            fail_reason = f"title too short len={len(job_title)} min={min_title}"
        elif not job_link.startswith("http"):
            fail_reason = f"job_link not http: {job_link!r}"
        elif len(jd_text) < min_jd:
            fail_reason = f"jd_text too short len={len(jd_text)} min={min_jd}"

        if fail_reason:
            to_state = cfg["fail_state"]
            if debug:
                logger.debug_index(
                    func="consult.qualify_meteorite",
                    index=1,
                    total=1,
                    identifier=_consult_job_identifier(input_job),
                    outcome=f"content fail -> {to_state}",
                )
                fail_bits = [
                    f"gate={fail_reason}",
                    f"found source={id_source}",
                    f"link_source={link_source}",
                ]
                if id_source != "AI":
                    fail_bits.append(f"fallback_job_link={job_link!r}")
                fail_bits.extend(
                    [
                        f"company_job_id={company_job_id!r}",
                        f"title={job_title!r}",
                        f"link={job_link!r}",
                        f"jd_chars={len(jd_text)}",
                    ]
                )
                logger.debug_detail(" ".join(fail_bits))
            else:
                logger.info(f"  {input_job.get('job_title') or aid} -> {to_state} [{fail_reason}]")
            _transition_job_state_for_task(task_key, [aid], to_state)
            return to_state

        parsed_job = {
            "company_job_id": company_job_id,
            "job_title": job_title,
            "job_link": job_link,
            jd_key: jd_text,
        }
        if not tracker.initialize_job(aid, input_job["company"], parsed_job):
            # Identity collision deleted the row — same as listing qualify fail_state return.
            if not debug:
                logger.info(f"  {aid} -> deleted (identity collision)")
            return cfg["fail_state"]

        to_state = cfg["pass_state"]
        _transition_job_state_for_task(task_key, [aid], to_state)
        if debug:
            recorded = tracker.get_job(aid) or {}
            rec_jd = len((recorded.get("job_data") or {}).get(jd_key, "") or "")
            logger.debug_index(
                func="consult.qualify_meteorite",
                index=1,
                total=1,
                identifier=_consult_job_identifier(input_job),
                outcome=str(to_state),
            )
            found_bits = [f"found source={id_source}", f"link_source={link_source}"]
            if id_source == "UUID-from-job_link":
                found_bits.append(f"fallback_job_link={job_link!r}")
            found_bits.extend(
                [
                    f"company_job_id={company_job_id!r}",
                    f"title={job_title!r}",
                    f"link={job_link!r}",
                    f"jd_chars={len(jd_text)}",
                ]
            )
            logger.debug_detail(
                f"{' '.join(found_bits)} | "
                f"recorded company_job_id={recorded.get('company_job_id')!r} "
                f"title={recorded.get('job_title')!r} link={recorded.get('job_link')!r} "
                f"jd_chars={rec_jd}"
            )
        else:
            logger.info(f"  {input_job.get('job_title') or aid} -> {to_state}")
        return to_state

    return await _run_batch_consult(
        task_key, batch_id, jobs, assemble, process, ctx, debug, batch_chunk_index=batch_chunk_index,
    )


def _resolve_company_job_id(ai_company_job_id: str, job_link: str) -> str:
    """Prefer non-empty AI company_job_id; else UUID path segment from job_link; else ''."""
    ai = (ai_company_job_id or "").strip()
    if ai:
        return ai
    link = (job_link or "").strip()
    if not link:
        return ""
    fallback = uuid_path_segment_from_url(link, TRACKER_CONFIG["uuid_path_segment_pattern"])
    return fallback or ""


def _jd_ready_for_evaluate(job: Dict[str, Any], min_chars: int) -> bool:
    jd = ((job.get("job_data") or {}).get("job_description") or "").strip()
    return len(jd) >= min_chars


async def evaluate_jd_batch(
    batch_id: str,
    jobs: List[Dict[str, Any]],
    ctx: Optional[Dict[str, Any]] = None,
    debug: bool = False,
    batch_chunk_index: Optional[int] = None,
    task_key: str = "evaluate_jd",
) -> Dict[str, Any]:
    """Batch JD dealbreaker screen (Pattern A, ast-326). Thin wrapper over _run_batch_consult.

    Jobs short on JD are transitioned separately; JD-ready remainder run together in one `_run_batch_consult`
    / one `do_task` when dispatcher ``batch_call_mode=1`` (AST-501). Expects scraped JD in ``job_data``.

    ``task_key`` defaults to "evaluate_jd" (regular gazer-discovered jobs); pass "evaluate_meteorite"
    for candidate-submitted jobs, which score against their own meteorite_jobdesc_rubric and land on
    METEORITE_* pass/fail/error states — see evaluate_meteorite_batch.
    """
    cfg = _consult_orchestration(task_key)
    min_chars = cfg.get("min_jd_chars", 80)
    not_ready_state = cfg.get("not_ready_state", "PASSED_JOBLIST")

    ready_jobs: List[Dict[str, Any]] = []
    not_ready_jobs: List[Dict[str, Any]] = []
    for job in jobs:
        if _jd_ready_for_evaluate(job, min_chars):
            ready_jobs.append(job)
        else:
            not_ready_jobs.append(job)

    if debug:
        logger.set_debug_flag(True)
        logger.debug_detail(
            f"{task_key} batch_id={batch_id} ready={len(ready_jobs)} "
            f"not_ready={len(not_ready_jobs)} min_chars={min_chars}"
        )

    for ni, job in enumerate(not_ready_jobs, start=1):
        aid = job["astral_job_id"]
        jd = ((job.get("job_data") or {}).get("job_description") or "").strip()
        tracker.save_job_data(aid, {
            "jd_readiness_skip": {
                "reason": "empty_or_short_jd",
                "chars": len(jd),
                "batch_id": batch_id,
            },
        })
        _transition_job_state_for_task(task_key, [aid], not_ready_state, score=None)
        if debug:
            logger.debug_index(
                func=f"consult.evaluate_jd_batch[{task_key}]",
                index=ni,
                total=len(not_ready_jobs),
                identifier=_consult_job_identifier(job),
                outcome=f"jd readiness skip -> {not_ready_state}",
            )
            logger.debug_detail(f"jd_chars={len(jd)} min_chars={min_chars}")
        if not debug:
            title = job.get("job_title") or aid
            logger.info("  %s -> %s [jd readiness skip]", title, not_ready_state)

    if not ready_jobs:
        if debug:
            logger.debug_detail(
                f"{task_key} batch_id={batch_id} all jobs not JD-ready skipped={len(not_ready_jobs)}"
            )
        return {
            "success": True,
            "passed": 0,
            "failed": 0,
            "total": len(jobs),
            "skipped": len(not_ready_jobs),
        }

    # AST-350: pre-compute vector_weights from candidate rubric so process() can derive a numeric score.
    # Score is informational only — does not affect pass/fail verdict.
    rubric_list = _rubric_criteria_for_cfg(_candidate_id_from_ctx(ctx), cfg)
    def assemble(jobs):
        jd_key = "job_description"
        jd_texts = [j.get("job_data", {}).get(jd_key, "") or "" for j in jobs]
        # Use 0-based position index so the model's input labels match its output positions
        index_values = [f"{i:03d}" for i in range(len(jobs))]
        return enumerate_array("JD LISTINGS", jd_texts, index_key="index", index_values=index_values)

    def process(input_job, response_job, cfg):
        aid = response_job["astral_job_id"]
        grades = response_job["grades"]
        # Incomplete/extra before pass/fail or score — retries via _run_batch_consult (AST-1155).
        if rubric_list:
            _require_complete_grade_set(rubric_list, grades)
        to_state = _render_pass_fail(task_key, grades, entity_state=input_job.get("state"))
        score = None
        if rubric_list:
            _, score = _render_score(cfg, rubric_list, grades, 0.0)
        save_data: Dict[str, Any] = {
            "jd_grades": grades,
            "jd_rubric": _rubric_snapshot_for_job_data(rubric_list),
        }
        normalized_score = _latest_score_value(score)
        if _task_config_scored(task_key) and normalized_score is not None:
            save_data["jd_score"] = normalized_score
        tracker.save_job_data(aid, save_data)
        _transition_job_state_for_task(task_key, [aid], to_state, score)
        title = input_job.get("job_title") or aid
        if not debug:
            if to_state == cfg["pass_state"]:
                logger.info(f"  {title} -> {to_state}")
            else:
                failed_vecs = [g["vector"] for g in grades if isinstance(grades, list) and g.get("grade") == "F"]
                logger.info(f"  {title} -> {to_state} [{', '.join(failed_vecs)}]")
        return to_state

    result = await _run_batch_consult(
        task_key,
        batch_id,
        ready_jobs,
        assemble,
        process,
        ctx,
        debug,
        batch_chunk_index=batch_chunk_index,
    )
    if not_ready_jobs:
        result = {**result, "skipped": len(not_ready_jobs), "total": len(jobs)}
    return result


async def evaluate_meteorite_batch(
    batch_id: str,
    jobs: List[Dict[str, Any]],
    ctx: Optional[Dict[str, Any]] = None,
    debug: bool = False,
    batch_chunk_index: Optional[int] = None,
) -> Dict[str, Any]:
    """Meteorite JD dealbreaker screen — candidate-submitted jobs, own rubric.

    Standalone twin of evaluate_jd_batch (own TASK_CONFIG pass/fail/error states, no
    METEORITE_GDL_OUTCOME_BY_TASK overlay needed), same pattern as meteorite_like_batch.
    """
    return await evaluate_jd_batch(
        batch_id, jobs, ctx=ctx, debug=debug, batch_chunk_index=batch_chunk_index,
        task_key="evaluate_meteorite",
    )


async def _consult_scored_dispatch_batch_encoded(
    dispatch_task_key: str,
    batch_id: str,
    jobs: List[Dict[str, Any]],
    ctx: Optional[Dict[str, Any]] = None,
    debug: bool = False,
    batch_chunk_index: Optional[int] = None,
) -> Dict[str, Any]:
    """One encoded grade_* Pattern-A call across N sequentially pre-prepped JD rows (AST-503); mirrors evaluate_jd exclusions."""
    hdr = _GRADE_DISPATCH_TO_HEADER[dispatch_task_key]
    entity_state = jobs[0].get("state") if jobs else None
    cfg_dispatch = _consult_orchestration_for_entity(dispatch_task_key, entity_state)
    agent_tk = cfg_dispatch.get("agent_task") or dispatch_task_key
    error_state = cfg_dispatch.get("error_state")
    skipped = 0

    if debug:
        logger.set_debug_flag(True)
        logger.debug_detail(
            f"{dispatch_task_key} batch_id={batch_id} claimed={len(jobs)} agent_task={agent_tk}"
        )

    eligible: List[Dict[str, Any]] = []
    live_rows: List[str] = []

    for job in jobs:
        aid = job["astral_job_id"]
        row = tracker.get_job(aid) or job

        company = None
        if cfg_dispatch.get("requires_company"):
            company = tracker.get_company(row["company"])
            if not company:
                if error_state:
                    _transition_job_state_for_task(agent_tk, [aid], error_state)
                if debug:
                    logger.debug_index(
                        func=f"consult._consult_scored_dispatch_batch_encoded({dispatch_task_key})",
                        index=skipped + 1,
                        total=len(jobs),
                        identifier=aid,
                        outcome="skipped — prep failed",
                    )
                    logger.debug_detail("reason=no_company")
                skipped += 1
                continue

        lc = await _prep_live_content(row, company, scoring_task_key=agent_tk, position=len(eligible))
        if not lc:
            fresh = tracker.get_job(aid) or row
            if fresh.get("state") != "NEED_WEBSITE_CONTENT":
                if error_state:
                    _transition_job_state_for_task(agent_tk, [aid], error_state)
            if debug:
                logger.debug_index(
                    func=f"consult._consult_scored_dispatch_batch_encoded({dispatch_task_key})",
                    index=skipped + 1,
                    total=len(jobs),
                    identifier=aid,
                    outcome="skipped — prep failed",
                )
                logger.debug_detail(f"reason=no_live_content state={fresh.get('state')!r}")
            skipped += 1
            continue

        eligible.append(row)
        live_rows.append(lc)

    if not eligible:
        if debug:
            logger.debug_detail(f"no eligible rows after prep skipped={skipped}")
        return {"success": True, "passed": 0, "failed": 0, "total": len(jobs), "skipped": skipped}

    def assemble(rows: List[Dict[str, Any]]) -> str:
        body = "\n".join(f"{i:03d}: {live_rows[i]}" for i in range(len(rows)))
        return f"CONSULT {hdr} ROWS:\n{body}"

    def process(input_job, response_job, _orch_cfg):
        aid = response_job["astral_job_id"]
        to_state, _, _grades = _apply_render_verdict_decoded_job(
            dispatch_task_key, aid, response_job, cfg_dispatch, ctx, debug=debug,
        )
        return to_state

    result = await _run_batch_consult(
        agent_tk,
        batch_id,
        eligible,
        assemble,
        process,
        ctx,
        debug,
        batch_chunk_index=batch_chunk_index,
    )
    if skipped:
        result = {**result, "skipped": skipped, "total": len(jobs)}
    return result


async def grade_do_batch(
    batch_id: str,
    jobs: List[Dict[str, Any]],
    ctx: Optional[Dict[str, Any]] = None,
    debug: bool = False,
    batch_chunk_index: Optional[int] = None,
) -> Dict[str, Any]:
    return await _consult_scored_dispatch_batch_encoded(
        "grade_do", batch_id, jobs, ctx=ctx, debug=debug, batch_chunk_index=batch_chunk_index,
    )


async def grade_get_batch(
    batch_id: str,
    jobs: List[Dict[str, Any]],
    ctx: Optional[Dict[str, Any]] = None,
    debug: bool = False,
    batch_chunk_index: Optional[int] = None,
) -> Dict[str, Any]:
    return await _consult_scored_dispatch_batch_encoded(
        "grade_get", batch_id, jobs, ctx=ctx, debug=debug, batch_chunk_index=batch_chunk_index,
    )


async def grade_like_batch(
    batch_id: str,
    jobs: List[Dict[str, Any]],
    ctx: Optional[Dict[str, Any]] = None,
    debug: bool = False,
    batch_chunk_index: Optional[int] = None,
) -> Dict[str, Any]:
    return await _consult_scored_dispatch_batch_encoded(
        "grade_like", batch_id, jobs, ctx=ctx, debug=debug, batch_chunk_index=batch_chunk_index,
    )


async def meteorite_like_batch(
    batch_id: str,
    jobs: List[Dict[str, Any]],
    ctx: Optional[Dict[str, Any]] = None,
    debug: bool = False,
    batch_chunk_index: Optional[int] = None,
) -> Dict[str, Any]:
    # AST-1055: same encoded LIKE path; TASK_CONFIG.meteorite_like drives states + agent_task.
    return await _consult_scored_dispatch_batch_encoded(
        "meteorite_like", batch_id, jobs, ctx=ctx, debug=debug, batch_chunk_index=batch_chunk_index,
    )


# ---- Job artifact pipelines (AST-369 / AST-371) ----

async def _run_cover_letter_for_job(
    astral_job_id: str,
    job: Dict[str, Any],
    ctx: Optional[Dict[str, Any]],
    debug: bool,
) -> None:
    """AST-369: cover letter hop after resume_content exists (resume-first)."""
    from src.core.agent import run_cover_letter_artifact_chain_for_job

    row = tracker.get_job(astral_job_id) or job
    if not tracker.get_job_artifacts(row).get("resume_content"):
        return
    chain_ctx: Dict[str, Any] = {**(ctx or {}), "batch_entities": [row], "job": row, "batch_size": 1}
    await run_cover_letter_artifact_chain_for_job(astral_job_id, chain_ctx, debug=debug)


async def _run_dispatch_chain_job_batch(
    batch_id: str,
    entities: List[Dict[str, Any]],
    ctx: Optional[Dict[str, Any]],
    debug: bool,
    dispatch_task_key: str,
    input_state: str,
) -> Dict[str, int]:
    """Dispatch-chain jobs: one do_task per entity; graduation in do_task (AST-848/849)."""
    from src.core.agent import _current_agent_task_run_next

    passed = errors = 0
    row_trigger = (input_state or "").strip()
    registry_trigger = dispatch_chain_registry_trigger(row_trigger) or row_trigger
    for job in entities:
        aid = job["astral_job_id"]
        row = tracker.get_job(aid) or job
        if not dispatch_chain_row_matches_job(
            row_trigger, dispatch_task_key, (row.get("state") or ""),
        ):
            continue
        cd = tracker._candidate_data_for_job(aid)
        if not cd:
            tracker.release_job_dispatch_claim(aid)
            errors += 1
            continue
        task_ctx: Dict[str, Any] = {
            **(ctx or {}),
            "batch_entities": [row],
            "batch_size": 1,
            "job": row,
            "candidate_data": cd,
            "dispatch_trigger_state": registry_trigger,
            "dispatch_chain_graduate_on_terminal": bool(
                _current_agent_task_run_next(dispatch_task_key)
            ),
        }
        company_key = row.get("company")
        if isinstance(company_key, str) and company_key.strip():
            co = tracker.get_company(company_key.strip())
            if co and co.get("candidate_id"):
                task_ctx["astral_candidate_id"] = str(co["candidate_id"])
        if "vector_labels" not in task_ctx:
            task_ctx["vector_labels"] = {}
        result = await do_task(
            dispatch_task_key,
            index=aid,
            ctx=task_ctx,
            debug=debug,
        )
        if not result.get("success"):
            tracker.release_job_dispatch_claim(aid)
            errors += 1
            continue
        passed += 1
    return {
        "total_processed": len(entities),
        "total_passed": passed,
        "total_failed": 0,
        "total_errors": errors,
    }


# ---- Public entry point for dispatcher ----

async def run_consult_task(
    entity_type: str,
    input_state: str,
    entities: List[Dict[str, Any]],
    batch_id: str,
    ctx: Optional[Dict[str, Any]] = None,
    debug: bool = False,
    batch_chunk_index: Optional[int] = None,
    dispatch_task_key: Optional[str] = None,
) -> Dict[str, Any]:
    """Unified dispatcher entry point. Routes on entity_type + input_state.

    batch_chunk_index: dispatcher sets for parallel chunked qualify / evaluate_jd / consult DO·GET·LIKE (AST-502)
    so `do_task` RESPONSE rows stay dedupe-distinct across chunks sharing one dispatch batch_id.

    Returns _SUMMARY_ZERO-shaped dict: {total_processed, total_passed, total_failed, total_errors}."""
    zero = {"total_processed": 0, "total_passed": 0, "total_failed": 0, "total_errors": 0}
    if not entities:
        return zero

    from src.core import roster

    if entity_type == "company":
        task_key = (dispatch_task_key or "").strip()
        if task_key == "fetch_website":
            from src.core.gazer import fetch_website_batch
            r = await fetch_website_batch(batch_id, entities, debug=debug)
            total = r.get("total", len(entities))
            passed = r.get("passed", 0)
            failed = r.get("failed", 0)
            errors = r.get("errors", max(0, total - passed - failed))
            return {
                "total_processed": total,
                "total_passed": passed,
                "total_failed": failed,
                "total_errors": errors,
            }
        if task_key == "fetch_job_pages":
            from src.core.gazer import fetch_job_pages_batch
            r = await fetch_job_pages_batch(batch_id, entities, debug=debug)
            total = r.get("total", len(entities))
            passed = r.get("passed", 0)
            failed = r.get("failed", 0)
            errors = max(0, total - passed - failed)
            return {
                "total_processed": total,
                "total_passed": passed,
                "total_failed": failed,
                "total_errors": errors,
            }
        if task_key in ("prefilter", "prefilter_company"):
            r = await roster.prefilter_company_batch(batch_id, entities, ctx=ctx, debug=debug)
            total = r.get("total", len(entities))
            passed = r.get("passed", 0)
            failed = r.get("failed", 0)
            skipped = r.get("skipped", 0)
            errors = max(0, total - passed - failed - skipped)
            return {
                "total_processed": total,
                "total_passed": passed,
                "total_failed": failed,
                "total_errors": errors,
            }
        if task_key == "vet_inflow_discovery":
            r = await roster.vet_inflow_discovery_company_batch(
                batch_id, entities, ctx=ctx, debug=debug,
            )
            total = r.get("total", len(entities))
            passed = r.get("passed", 0)
            failed = r.get("failed", 0)
            skipped = r.get("skipped", 0)
            errors = max(0, total - passed - failed - skipped)
            return {
                "total_processed": total,
                "total_passed": passed,
                "total_failed": failed,
                "total_errors": errors,
            }
        if task_key == "parse_job_list":
            r = await roster.parse_job_list_batch(batch_id, entities, ctx=ctx, debug=debug)
            total = r.get("total", len(entities))
            passed = r.get("passed", 0)
            failed = r.get("failed", 0)
            errors = r.get("errors", max(0, total - passed - failed))
            return {
                "total_processed": total,
                "total_passed": passed,
                "total_failed": failed,
                "total_errors": errors,
            }
        return await roster.run_company_task(
            input_state, entities[0], batch_id, ctx, debug,
            dispatch_task_key=dispatch_task_key,
        )

    if entity_type == "candidate":
        from src.utils.config import CANDIDATE_STAGE_DISPATCH, INFLOW_CONFIG
        from src.core.candidate import (
            run_requested_artifacts_dispatch,
            run_requested_resume_dispatch,
        )
        tk = (dispatch_task_key or "").strip()
        cid = (entities[0].get("astral_candidate_id") or entities[0].get("candidate_id") or "")
        if tk == INFLOW_CONFIG["discovery"]["task_key"]:
            return await roster.run_inflow_discovery_batch(
                entities[0], batch_id, ctx, debug,
            )
        if tk == CANDIDATE_STAGE_DISPATCH["requested_resume"]["task_key"]:
            return await run_requested_resume_dispatch(cid, debug=debug)
        if tk == CANDIDATE_STAGE_DISPATCH["requested_artifacts"]["task_key"]:
            return await run_requested_artifacts_dispatch(cid, debug=debug)
        logger.warning(
            "run_consult_task: unhandled candidate task_key=%s",
            tk,
        )
        return zero

    task_key = (dispatch_task_key or "").strip()
    if not task_key:
        logger.warning(
            "run_consult_task: dispatch_task_key required for job dispatch (input_state=%s)",
            input_state,
        )
        return zero

    if task_key == "fetch_jd":
        from src.core.gazer import fetch_jd_batch
        r = await fetch_jd_batch(batch_id, entities, debug=debug)
    elif task_key == "fetch_culture_pages":
        from src.core.gazer import fetch_culture_pages_batch
        r = await fetch_culture_pages_batch(batch_id, entities, debug=debug)
    elif task_key == "qualify_job_listings":
        r = await qualify_job_listings(
            batch_id, entities, ctx=ctx, debug=debug, batch_chunk_index=batch_chunk_index,
        )
    elif task_key == "qualify_meteorite":
        r = await qualify_meteorite(
            batch_id, entities, ctx=ctx, debug=debug, batch_chunk_index=batch_chunk_index,
        )
    elif task_key == "evaluate_jd":
        r = await evaluate_jd_batch(
            batch_id, entities, ctx=ctx, debug=debug, batch_chunk_index=batch_chunk_index,
        )
    elif task_key == "evaluate_meteorite":
        r = await evaluate_meteorite_batch(
            batch_id, entities, ctx=ctx, debug=debug, batch_chunk_index=batch_chunk_index,
        )
    elif task_key in ("grade_do", "grade_get", "grade_like", "meteorite_like"):
        if len(entities) == 1:
            aid = entities[0]["astral_job_id"]
            orch = _consult_orchestration_for_entity(task_key, entities[0].get("state"))
            rv = await render_verdict(task_key, aid, ctx=ctx, debug=debug)
            if rv.get("success"):
                passed = 1 if rv.get("to_state") == orch.get("pass_state") else 0
                return {"total_processed": 1, "total_passed": passed, "total_failed": 1 - passed, "total_errors": 0}
            return {"total_processed": 1, "total_passed": 0, "total_failed": 0, "total_errors": 1}
        _batch = {
            "grade_do": grade_do_batch,
            "grade_get": grade_get_batch,
            "grade_like": grade_like_batch,
            "meteorite_like": meteorite_like_batch,
        }[task_key]
        r = await _batch(batch_id, entities, ctx=ctx, debug=debug, batch_chunk_index=batch_chunk_index)
    elif task_key in ("analysis_upshot", "meteorite_upshot"):
        return await _run_analysis_upshot_batch(batch_id, entities, ctx, debug, task_key=task_key)
    elif is_dispatch_chain_trigger((input_state or "").strip()) and task_key in TASK_CONFIG:
        return await _run_dispatch_chain_job_batch(
            batch_id, entities, ctx, debug, task_key, input_state,
        )
    else:
        logger.warning("run_consult_task: unhandled task_key=%s for input_state=%s", task_key, input_state)
        return zero

    # Normalize batch result shapes (passed/failed/total) to summary shape
    total = r.get("total", len(entities))
    passed = r.get("passed", 0)
    failed = r.get("failed", 0)
    errors = max(0, total - passed - failed)
    return {"total_processed": total, "total_passed": passed, "total_failed": failed, "total_errors": errors}


# ---- Timesheets (read side) ----

def list_timesheets(**kwargs) -> List[Dict[str, Any]]:
    """Thin wrapper for layering compliance — API layer imports core, not data."""
    return tracker.list_timesheets(**kwargs)


