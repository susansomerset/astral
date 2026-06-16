"""
Core business logic for job consulting/analysis.

render_verdict(task_type, astral_job_id): single orchestrator for per-job consult tasks.
  Fetches job/company internally, preps live content, calls agent, audits, derives verdict.
  Per-job orchestration (pass/fail/error, thresholds, rubric refs) merges TASK_CONFIG[task_type] with
  agent_task when task_type wraps a grade_* row (consult_do → grade_do via _consult_orchestration).
_render_pass_fail: binary grading (PASS/F) for qualify_job_listings and evaluate_jd_batch.
_render_score: scored grading (AST-358 importance × universal grade values × confidence) for batch qualify/evaluate_jd and consult_get/do/like.
When TASK_CONFIG[task_key].scored, transitions persist latest_score only when a numeric score exists.
_run_batch_consult: shared scaffolding for batch AI tasks (ID reconciliation, audit, error handling).
qualify_job_listings: batch job list screen (Pattern A) — thin wrapper over _run_batch_consult.
evaluate_jd_batch: batch JD dealbreaker screen (Pattern A) — thin wrapper over _run_batch_consult.
consult_*_batch: scored DO/GET/LIKE Pattern A batching (AST-503) via _run_batch_consult(agent_task=*grade_*).
"""

import json
import re
from typing import Any, Dict, List, Optional, Tuple

from src.core import tracker
from src.core.agent import do_task
from src.utils import rubric_text
from src.utils.config import (
    TASK_CONFIG,
    JOB_STATES,
    ASTRAL_CONFIG,
    CONFIDENCE_MULTIPLIERS,
    MAX_GRADE_VALUE,
    RUBRIC_TOTAL,
    JOB_TOKEN_CONFIG,
    grade_value,
    importance_multiplier,
    resolve_dispatch_task_config_key,
    resume_artifact_compound_state,
    resume_artifact_hop_task_keys,
)
from src.utils.formatting import enumerate_array
from src.utils.logging import get_logger

logger = get_logger(__name__)


def _consult_job_identifier(job: Dict[str, Any]) -> str:
    """Primary debug identifier for a consult job row (§1.5.1 style D)."""
    return str(job.get("astral_job_id") or job.get("job_title") or "?")


# input_state → TASK_CONFIG orchestration lookup key (`consult_*` → grade_* prompts via _consult_orchestration).
# Legacy map — not used for dispatch routing (AST-534). Tests pass dispatch_task_key explicitly.
_INPUT_STATE_TO_TASK = {
    "NEW":                "validate_title",
    "VALID_TITLE":        "qualify_job_listings",
    "VALID_TITLE_RETRY":  "qualify_job_listings",
    "PASSED_JOBLIST":     "scrape_jd",
    "JD_READY":           "evaluate_jd",
    "JD_READY_RETRY":     "evaluate_jd",
    "PASSED_JD":          "consult_do",
    "PASSED_DO":          "consult_get",
    "PASSED_GET":         "consult_like",
    "PASSED_LIKE":        "analysis_upshot",
    "PASSED_LIKE_RETRY":  "analysis_upshot",
    "BUILD_ARTIFACTS":    "contemplate_job",
    "CANDIDATE_REVIEW":   "draft_cover_letter",
}


def _consult_orchestration(task_key: str) -> Dict[str, Any]:
    """Return pass/fail/error/rubric/pass_threshold/agent_task orch for qualify/evaluate or consult wrappers."""
    orch_key = resolve_dispatch_task_config_key(task_key)
    base = TASK_CONFIG[orch_key]
    return base if orch_key == task_key else {**base, "agent_task": orch_key}


def _render_pass_fail(task_key: str, grades: list) -> str:
    """Binary grading (AST-357): F with confidence 2–5 fails; all literal X fails; no confidence > 1 fails.
    grades: [{vector, grade, confidence, ...}, ...].
    Raises KeyError if orchestration lookup fails (missing TASK_CONFIG key)."""
    cfg = _consult_orchestration(task_key)
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


def _rubric_criteria_from_cd(cd: dict, rubric_key: Optional[str]) -> list:
    if not rubric_key:
        return []
    raw = (cd or {}).get("artifacts", {}).get(rubric_key)
    if isinstance(raw, list):
        artifact = raw
    else:
        artifact = (raw or {}).get("criteria") or []
    if rubric_key == "company_prefilter":
        from src.utils.config import EMBEDDED_COMPANY_PREFILTER_CRITERIA

        embedded_codes = {
            str(c.get("code")).strip().upper()
            for c in EMBEDDED_COMPANY_PREFILTER_CRITERIA
            if isinstance(c, dict) and c.get("code")
        }
        tail = [
            c
            for c in artifact
            if isinstance(c, dict) and str(c.get("code") or "").strip().upper() not in embedded_codes
        ]
        return list(EMBEDDED_COMPANY_PREFILTER_CRITERIA) + tail
    return artifact


def _vector_labels_map(rubric_criteria: list) -> Dict[str, str]:
    return {item["code"]: item["label"] for item in rubric_criteria if item.get("code") and item.get("label")}


def _lookup_rubric_reason_for_grade(rubric_criteria: list, vector_label: str, letter: str) -> str:
    """Rubric line description for this vector + grade letter (AST-351). Raises ValueError if missing."""
    target = _strip_code((vector_label or "").strip())
    lt = (letter or "").upper()
    for item in rubric_criteria:
        if not isinstance(item, dict):
            continue
        lab = _strip_code(str(item.get("label") or "").strip())
        code = str(item.get("code") or "").strip().upper()
        t_upper = target.upper()
        if lab != target and code != t_upper:
            continue
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
    raise ValueError(f"No rubric criterion matching vector {vector_label!r}")


def _hydrate_grade_reasons_from_rubric(grades: list, rubric_criteria: list) -> None:
    if not rubric_criteria:
        raise ValueError("rubric criteria missing or empty; cannot hydrate grade reasons")
    for g in grades:
        if not isinstance(g, dict):
            continue
        g["reason"] = _lookup_rubric_reason_for_grade(
            rubric_criteria, str(g.get("vector") or ""), str(g.get("grade") or "")
        )


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


def _job_from_rubric_json(obj: dict, task_config: dict, ctx: dict) -> dict:
    rubric = _rubric_criteria_from_cd((ctx or {}).get("candidate_data") or {}, task_config.get("rubric_artifact"))
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
    rubric = _rubric_criteria_from_cd((ctx or {}).get("candidate_data") or {}, task_config.get("rubric_artifact"))
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
    target = _strip_code((vector_label or "").strip())
    default = ASTRAL_CONFIG["consult_importance"]["default_vector_importance"]
    for item in rubric_criteria:
        if not isinstance(item, dict):
            continue
        lab = _strip_code(str(item.get("label") or "").strip())
        code = str(item.get("code") or "").strip().upper()
        t_upper = target.upper()
        if lab != target and code != t_upper:
            continue
        imp = item.get("importance")
        if imp is None:
            return importance_multiplier(int(default))
        return importance_multiplier(int(imp))
    raise ValueError(f"_render_score: no rubric criterion matching vector {vector_label!r}")


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
    expected = {
        _strip_code(str(item.get("label") or "").strip())
        for item in rubric_criteria
        if item.get("label")
    }
    actual = {_strip_code(g["vector"]) for g in grades}
    missing = expected - actual
    if missing:
        raise ValueError(f"_render_score: missing vectors {sorted(missing)}")
    extra = actual - expected
    if extra:
        raise ValueError(f"_render_score: unknown vectors {sorted(extra)}")
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


_DISPATCH_CONSULT_TO_HEADER = {
    "consult_do": "DO",
    "consult_get": "GET",
    "consult_like": "LIKE",
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


def _format_analysis_phase_text(phase_token: str, job_data: dict, candidate_data: dict) -> str:
    """Human-readable consult recap for one ANALYSIS_* token (AST-513)."""
    phase_cfg = (JOB_TOKEN_CONFIG.get("analysis_phases") or {}).get(phase_token)
    if not phase_cfg:
        return ""
    grades = job_data.get(phase_cfg.get("grades_key") or "")
    if not isinstance(grades, list) or not grades:
        return ""
    rubric_criteria = _rubric_criteria_from_cd(candidate_data, phase_cfg.get("rubric_artifact"))
    if not rubric_criteria:
        return ""
    blocks: List[str] = []
    for g in grades:
        if not isinstance(g, dict):
            continue
        vector_label = str(g.get("vector") or "").strip()
        if not vector_label:
            continue
        criterion = None
        target = _strip_code(vector_label)
        for item in rubric_criteria:
            if not isinstance(item, dict):
                continue
            if _strip_code(str(item.get("label") or "").strip()) == target:
                criterion = item
                break
        if criterion is None:
            logger.warning(
                "_format_analysis_phase_text: no rubric criterion for vector %r (phase=%s)",
                vector_label,
                phase_token,
            )
            continue
        title = str(criterion.get("label") or vector_label).strip()
        rubric_blob = str(criterion.get("content") or "").strip()
        letter = str(g.get("grade") or "").strip().upper()
        conf = g.get("confidence")
        conf_s = f"{int(conf)}/5" if isinstance(conf, (int, float)) else "0/5"
        blocks.append(
            f"CONSIDER: {title}\n{rubric_blob}\nANALYSIS RESULT: {letter} ({conf_s} confidence)"
        )
    return "\n\n".join(blocks)


def build_job_token_context(job: Dict[str, Any], candidate_data: dict) -> Dict[str, str]:
    """Precomputed job-scoped prompt tokens for artifact single-job calls (AST-513)."""
    from src.core.candidate import enabled_resume_structure_sections, resolve_resume_structure

    jd_data = job.get("job_data") if isinstance(job.get("job_data"), dict) else {}
    visible = (jd_data.get("job_description") or "").strip()
    out: Dict[str, str] = {"VISIBLE_JD": visible}
    for key in ("ANALYSIS_JD", "ANALYSIS_DO", "ANALYSIS_GET", "ANALYSIS_LIKE"):
        out[key] = _format_analysis_phase_text(key, jd_data, candidate_data)
    structure = resolve_resume_structure(candidate_data)
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
) -> Any:
    """Coat-check JD + website (same as render_verdict LIKE); add raw_job_listing + DO/GET/LIKE recap."""
    base = await _prep_live_content(job, company, scoring_task_key="analysis_upshot")
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
) -> Dict[str, int]:
    """AST-480: synthesis at PASSED_LIKE (score_floor dispatch); persist job_data.analysis_upshot → RECOMMENDED."""
    task_cfg = TASK_CONFIG["analysis_upshot"]
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
                    _transition_job_state_for_task("analysis_upshot", [aid], dest)
                errors += 1
                continue
        live_content = await _prep_analysis_upshot_live_content(row, company)
        if not live_content:
            fresh = tracker.get_job(aid) or row
            if fresh.get("state") != "NEED_WEBSITE_CONTENT":
                dest = _consult_batch_fail_dest(fresh.get("state"), task_cfg.get("error_state"))
                if dest:
                    _transition_job_state_for_task("analysis_upshot", [aid], dest)
            errors += 1
            continue
        task_ctx = {**base_ctx, "batch_entities": [row], "job": row, "batch_size": 1}
        result = await do_task(
            task_key="analysis_upshot",
            live_content=live_content,
            index=aid,
            ctx=task_ctx,
            debug=debug,
        )
        if not result.get("success"):
            dest = _consult_batch_fail_dest(row.get("state"), task_cfg.get("error_state"))
            if dest:
                _transition_job_state_for_task("analysis_upshot", [aid], dest)
            errors += 1
            continue
        parsed = result.get("parsed_response")
        if not isinstance(parsed, dict):
            dest = _consult_batch_fail_dest(row.get("state"), task_cfg.get("error_state"))
            if dest:
                _transition_job_state_for_task("analysis_upshot", [aid], dest)
            errors += 1
            continue
        tracker.save_job_data(aid, {"analysis_upshot": parsed})
        _transition_job_state_for_task("analysis_upshot", [aid], task_cfg["pass_state"])
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
    agent_task = cfg.get("agent_task") or resolve_dispatch_task_config_key(dispatch_task_key)
    grades = response_job.get("grades")
    if not isinstance(grades, list):
        raise ValueError("agent response missing grades")
    rk = cfg.get("rubric_artifact")
    rubric_criteria = _rubric_criteria_from_cd((ctx or {}).get("candidate_data") or {}, rk)
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
        to_state = _render_pass_fail(dispatch_task_key, grades)
        score = None
    elif mode == "scored":
        rubric_key = cfg.get("rubric_artifact")
        if not rubric_key:
            orch_key = resolve_dispatch_task_config_key(dispatch_task_key)
            raise ValueError(f"TASK_CONFIG[{orch_key}] missing rubric_artifact")
        if not rubric_criteria:
            raise ValueError(f"Candidate missing rubric artifact: {rubric_key}")
        artifacts = (ctx or {}).get("candidate_data", {}).get("artifacts", {})
        threshold = artifacts.get(f"{rubric_key}_threshold", cfg.get("pass_threshold", 6.0))
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
    if notes_tail:
        save_data[f"{prefix}_notes"] = notes_tail
    tracker.save_job_data(astral_job_id, save_data)
    _transition_job_state_for_task(agent_task, [astral_job_id], to_state, score)
    return to_state, score, grades


async def render_verdict(task_type: str, astral_job_id: str, ctx: Optional[Dict[str, Any]] = None, debug: bool = False) -> Dict[str, Any]:
    """Full pipeline for one job through one agent task.
    Fetches job/company internally, preps live content, calls agent, audits,
    derives verdict, saves grades+score, transitions state.
    ctx: full candidate raft, forwarded to do_task for token resolution + API key override.
    Returns result dict for CLI logging."""
    cfg = _consult_orchestration(task_type)
    agent_task = cfg["agent_task"]
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

    job = tracker.get_job(astral_job_id)
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
    rk = cfg.get("rubric_artifact")
    rubric_criteria = _rubric_criteria_from_cd(cd, rk)
    vector_labels = _vector_labels_map(rubric_criteria)
    job_row = dict(job)
    task_ctx: Dict[str, Any] = {**(ctx or {}), "batch_entities": [job_row], "vector_labels": vector_labels, "batch_size": 1}

    result = await do_task(task_key=agent_task, live_content=live_content, index=astral_job_id, ctx=task_ctx, debug=debug)

    if not result.get("success"):
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
    cfg = _consult_orchestration(task_key)
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
    rubric_key = cfg.get("rubric_artifact")
    cd = (ctx or {}).get("candidate_data", {})
    rubric_raw = cd.get("artifacts", {}).get(rubric_key) if rubric_key else None
    # Rubric stored as list (editor-saved) or {"criteria": [...]} (AI-generated)
    rubric_criteria = rubric_raw if isinstance(rubric_raw, list) else ((rubric_raw or {}).get("criteria") or [])
    vector_labels = {item["code"]: item["label"] for item in rubric_criteria if item.get("code") and item.get("label")}
    # batch_entities + vector_labels passed so do_task/_decode_payload can map pos→id and code→label
    task_ctx = {**ctx, "batch_size": len(jobs), "batch_entities": jobs, "vector_labels": vector_labels} if ctx else \
               {"batch_size": len(jobs), "batch_entities": jobs, "vector_labels": vector_labels}
    do_index = f"{task_key}_batch_{batch_id}"
    if batch_chunk_index is not None:
        do_index = f"{do_index}_c{batch_chunk_index}"
    result = await do_task(task_key=task_key, live_content=live_content, index=do_index, ctx=task_ctx, debug=debug)

    if not result.get("success"):
        # Envelope failure — whole batch to error_state
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
            if debug:
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

    # Store per-job agent_responses refs from the shared batch call
    agent_ref = result.get("agent_ref")
    if agent_ref:
        processed_ids = received_ids - fabricated - bad_grades
        entity_type = TASK_CONFIG.get(task_key, {}).get("entity_type", "job")
        for aid in processed_ids:
            try:
                tracker.append_agent_response(entity_type, aid, agent_ref)
            except Exception:
                logger.debug("append_agent_response failed for %s", aid, exc_info=True)

    # bad_grades → per-entity retry holding or terminal error
    error_ids = list(bad_grades)
    if error_ids:
        bad_rows = [input_by_id[aid] for aid in error_ids if aid in input_by_id]
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
    task_key = "qualify_job_listings"
    cfg = _consult_orchestration(task_key)

    # AST-350: same as evaluate_jd_batch — numeric score for latest_score / dispatch sort (informational).
    rubric_key = cfg.get("rubric_artifact")
    artifacts = (ctx or {}).get("candidate_data", {}).get("artifacts", {})
    rubric_raw = artifacts.get(rubric_key) if rubric_key else None
    rubric_list = rubric_raw if isinstance(rubric_raw, list) else ((rubric_raw or {}).get("criteria") or [])
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

        if to_state == cfg["fail_state"]:
            # Failing jobs carry no metadata — just save grades and transition
            tracker.save_job_data(aid, {"joblist_grades": grades})
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
                logger.debug_detail(f"title too short: {repr(raw_title)} min_len={min_len}")
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
        tracker.initialize_job(aid, input_job["company"], response_job)
        tracker.save_job_data(aid, {"joblist_grades": grades})
        _transition_job_state_for_task(task_key, [aid], to_state, score)
        if not debug:
            logger.info(f"  {input_job.get('job_title') or aid} -> {to_state}")
        return to_state

    result = await _run_batch_consult(
        task_key, batch_id, jobs, assemble, process, ctx, debug, batch_chunk_index=batch_chunk_index,
    )
    return result


def _jd_ready_for_evaluate(job: Dict[str, Any], min_chars: int) -> bool:
    jd = ((job.get("job_data") or {}).get("job_description") or "").strip()
    return len(jd) >= min_chars


async def evaluate_jd_batch(
    batch_id: str,
    jobs: List[Dict[str, Any]],
    ctx: Optional[Dict[str, Any]] = None,
    debug: bool = False,
    batch_chunk_index: Optional[int] = None,
) -> Dict[str, Any]:
    """Batch JD dealbreaker screen (Pattern A, ast-326). Thin wrapper over _run_batch_consult.

    Jobs short on JD are transitioned separately; JD-ready remainder run together in one `_run_batch_consult`
    / one `do_task` when dispatcher ``batch_call_mode=1`` (AST-501). Expects scraped JD in ``job_data``.
    """
    task_key = "evaluate_jd"
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
            f"evaluate_jd batch_id={batch_id} ready={len(ready_jobs)} "
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
                func="consult.evaluate_jd_batch",
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
                f"evaluate_jd batch_id={batch_id} all jobs not JD-ready skipped={len(not_ready_jobs)}"
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
    rubric_key = cfg.get("rubric_artifact")
    artifacts = (ctx or {}).get("candidate_data", {}).get("artifacts", {})
    rubric_raw = artifacts.get(rubric_key) if rubric_key else None
    rubric_list = rubric_raw if isinstance(rubric_raw, list) else ((rubric_raw or {}).get("criteria") or [])
    def assemble(jobs):
        jd_key = "job_description"
        jd_texts = [j.get("job_data", {}).get(jd_key, "") or "" for j in jobs]
        # Use 0-based position index so the model's input labels match its output positions
        index_values = [f"{i:03d}" for i in range(len(jobs))]
        return enumerate_array("JD LISTINGS", jd_texts, index_key="index", index_values=index_values)

    def process(input_job, response_job, cfg):
        aid = response_job["astral_job_id"]
        grades = response_job["grades"]
        to_state = _render_pass_fail(task_key, grades)
        # Validate grades against rubric vectors; invalid/incomplete payloads retry via _run_batch_consult.
        score = None
        if rubric_list:
            _, score = _render_score(cfg, rubric_list, grades, 0.0)
        save_data: Dict[str, Any] = {"jd_grades": grades}
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


async def _consult_scored_dispatch_batch_encoded(
    dispatch_task_key: str,
    batch_id: str,
    jobs: List[Dict[str, Any]],
    ctx: Optional[Dict[str, Any]] = None,
    debug: bool = False,
    batch_chunk_index: Optional[int] = None,
) -> Dict[str, Any]:
    """One encoded grade_* Pattern-A call across N sequentially pre-prepped JD rows (AST-503); mirrors evaluate_jd exclusions."""
    hdr = _DISPATCH_CONSULT_TO_HEADER[dispatch_task_key]
    cfg_dispatch = _consult_orchestration(dispatch_task_key)
    agent_tk = cfg_dispatch["agent_task"]
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


async def consult_do_batch(
    batch_id: str,
    jobs: List[Dict[str, Any]],
    ctx: Optional[Dict[str, Any]] = None,
    debug: bool = False,
    batch_chunk_index: Optional[int] = None,
) -> Dict[str, Any]:
    return await _consult_scored_dispatch_batch_encoded(
        "consult_do", batch_id, jobs, ctx=ctx, debug=debug, batch_chunk_index=batch_chunk_index,
    )


async def consult_get_batch(
    batch_id: str,
    jobs: List[Dict[str, Any]],
    ctx: Optional[Dict[str, Any]] = None,
    debug: bool = False,
    batch_chunk_index: Optional[int] = None,
) -> Dict[str, Any]:
    return await _consult_scored_dispatch_batch_encoded(
        "consult_get", batch_id, jobs, ctx=ctx, debug=debug, batch_chunk_index=batch_chunk_index,
    )


async def consult_like_batch(
    batch_id: str,
    jobs: List[Dict[str, Any]],
    ctx: Optional[Dict[str, Any]] = None,
    debug: bool = False,
    batch_chunk_index: Optional[int] = None,
) -> Dict[str, Any]:
    return await _consult_scored_dispatch_batch_encoded(
        "consult_like", batch_id, jobs, ctx=ctx, debug=debug, batch_chunk_index=batch_chunk_index,
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


_JOB_ARTIFACT_ENTRY_KEYS = frozenset(
    k for k, v in TASK_CONFIG.items()
    if str(v.get("phase") or "").startswith("E. Job Artifacts")
    and k != "draft_cover_letter"  # cover-letter chain, not resume entry batch (AST-534 review)
)


def _resume_artifact_dispatch_row_ok(entry_task_key: str, input_state: str) -> bool:
    tk = (entry_task_key or "").strip()
    if tk not in resume_artifact_hop_task_keys():
        return True
    expected = resume_artifact_compound_state(tk)
    got = (input_state or "").strip()
    if got != expected:
        logger.warning(
            "artifact entry: task_key=%s expects trigger_state=%s got %s",
            tk,
            expected,
            got,
        )
        return False
    return True


def _artifact_entry_hop_failed(aid: str) -> None:
    tracker.release_job_dispatch_claim(aid)


async def _run_job_artifact_entry_batch(
    batch_id: str,
    entities: List[Dict[str, Any]],
    ctx: Optional[Dict[str, Any]],
    debug: bool,
    entry_task_key: str,
) -> Dict[str, int]:
    """Run one Phase E artifact hop per job starting at entry_task_key (dispatch row task_key)."""
    from src.core.agent import run_resume_artifact_chain_for_job

    passed = errors = 0
    base_ctx = dict(ctx or {})
    for job in entities:
        aid = job["astral_job_id"]
        chain_ctx = {**base_ctx, "job": job, "batch_entities": [job], "batch_size": 1}
        r = await run_resume_artifact_chain_for_job(
            aid, chain_ctx, debug=debug, first_task_key=entry_task_key,
        )
        if not r.get("success"):
            _artifact_entry_hop_failed(aid)
            errors += 1
            continue
        row = tracker.get_job(aid) or job
        if not tracker.job_has_persisted_resume_body(aid, row):
            _artifact_entry_hop_failed(aid)
            errors += 1
            continue
        try:
            tracker.transition_job_state([aid], "CANDIDATE_REVIEW")
        except ValueError as exc:
            logger.warning("[%s] CANDIDATE_REVIEW transition failed: %s", aid, exc)
            _artifact_entry_hop_failed(aid)
            errors += 1
            continue
        passed += 1
        if entry_task_key == "contemplate_job":
            await _run_cover_letter_for_job(aid, row, base_ctx, debug)
    return {
        "total_processed": len(entities),
        "total_passed": passed,
        "total_failed": 0,
        "total_errors": errors,
    }


async def _run_craft_job_cover_letter_batch(
    batch_id: str,
    entities: List[Dict[str, Any]],
    ctx: Optional[Dict[str, Any]],
    debug: bool,
) -> Dict[str, int]:
    """AST-369: cover letter for jobs that already have resume_content."""
    from src.core.agent import run_cover_letter_artifact_chain_for_job

    passed = failed = errors = 0
    base_ctx = dict(ctx or {})
    for job in entities:
        aid = job["astral_job_id"]
        row = tracker.get_job(aid) or job
        if not tracker.get_job_artifacts(row).get("resume_content"):
            failed += 1
            continue
        chain_ctx = {**base_ctx, "batch_entities": [row], "job": row, "batch_size": 1}
        r = await run_cover_letter_artifact_chain_for_job(aid, chain_ctx, debug=debug)
        if r.get("success"):
            passed += 1
        else:
            errors += 1
    return {
        "total_processed": len(entities),
        "total_passed": passed,
        "total_failed": failed,
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
            errors = max(0, total - passed - failed)
            return {
                "total_processed": total,
                "total_passed": passed,
                "total_failed": failed,
                "total_errors": errors,
            }
        if task_key == "prefilter":
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
        return await roster.run_company_task(
            input_state, entities[0], batch_id, ctx, debug,
            dispatch_task_key=dispatch_task_key,
        )

    if entity_type == "board_search":
        # Lazy import: breaks circular consult/gazer imports at module load (cycle-break, ASTRAL_CODE_RULES B1).
        from src.core.gazer import process_gaze_board_batch
        outcomes = await process_gaze_board_batch(batch_id, entities, debug=debug, ctx=ctx)
        passed = sum(1 for o in outcomes if o.get("status") == "success")
        failed = len(outcomes) - passed
        return {
            "total_processed": len(outcomes),
            "total_passed": passed,
            "total_failed": failed,
            "total_errors": 0,
        }

    if entity_type == "candidate":
        return await roster.run_inflow_discovery_batch(
            entities[0], batch_id, ctx, debug,
        )

    task_key = (dispatch_task_key or "").strip()
    if not task_key:
        logger.warning(
            "run_consult_task: dispatch_task_key required for job dispatch (input_state=%s)",
            input_state,
        )
        return zero

    if task_key == "validate_title":
        from src.core.gazer import validate_title_batch
        r = await validate_title_batch(batch_id, entities, ctx, debug=debug)
    elif task_key == "scrape_jd":
        from src.core.gazer import scrape_jd_batch
        r = await scrape_jd_batch(batch_id, entities, debug=debug)
    elif task_key == "qualify_job_listings":
        r = await qualify_job_listings(
            batch_id, entities, ctx=ctx, debug=debug, batch_chunk_index=batch_chunk_index,
        )
    elif task_key == "evaluate_jd":
        r = await evaluate_jd_batch(
            batch_id, entities, ctx=ctx, debug=debug, batch_chunk_index=batch_chunk_index,
        )
    elif task_key in ("consult_do", "consult_get", "consult_like"):
        if len(entities) == 1:
            aid = entities[0]["astral_job_id"]
            orch = _consult_orchestration(task_key)
            rv = await render_verdict(task_key, aid, ctx=ctx, debug=debug)
            if rv.get("success"):
                passed = 1 if rv.get("to_state") == orch.get("pass_state") else 0
                return {"total_processed": 1, "total_passed": passed, "total_failed": 1 - passed, "total_errors": 0}
            return {"total_processed": 1, "total_passed": 0, "total_failed": 0, "total_errors": 1}
        _batch = {"consult_do": consult_do_batch, "consult_get": consult_get_batch, "consult_like": consult_like_batch}[
            task_key
        ]
        r = await _batch(batch_id, entities, ctx=ctx, debug=debug, batch_chunk_index=batch_chunk_index)
    elif task_key == "analysis_upshot":
        return await _run_analysis_upshot_batch(batch_id, entities, ctx, debug)
    elif task_key == "draft_cover_letter":
        return await _run_craft_job_cover_letter_batch(batch_id, entities, ctx, debug)
    elif task_key in _JOB_ARTIFACT_ENTRY_KEYS:
        if not _resume_artifact_dispatch_row_ok(task_key, input_state):
            return zero
        return await _run_job_artifact_entry_batch(batch_id, entities, ctx, debug, task_key)
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


