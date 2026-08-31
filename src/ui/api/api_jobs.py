"""API endpoints for Jobs screens: list, detail, bulk state."""

from datetime import datetime, timezone
from typing import Optional

from flask import Blueprint, jsonify, request

from ui.auth import require_auth
from src.core.consult import _phase_score_breakdown
from src.core.agent import get_entity_agent_story
from src.core.roster import get_company, update_company
from src.core.tracker import (
    assemble_job_copy_snapshot,
    cancel_artifact_build,
    count_jobs,
    get_job,
    get_job_artifacts,
    hydrate_job_artifacts_for_display,
    job_misses_dispatch_score_floor,
    legal_job_successor_states,
    list_jobs,
    list_jobs_below_dispatch_score_floor,
    persist_skipped_job_edits,
    save_job_artifact_cover_letter,
    save_job_artifact_job_resume_body,
    save_job_artifact_resume_content,
    save_job_data,
    score_floor_by_trigger_for_candidate,
    set_candidate_result,
    start_artifact_build,
    transition_job_state,
)
from src.utils.config import (
    APPLIED_JOB_STATES,
    IN_REVIEW_STATES,
    METEORITE_CONFIG,
    PHASE_SCORE_BREAKDOWN_KEY_SUFFIX,
    RECOMMENDED_JOB_STATES,
    SKIPPED_STATES,
)
from src.utils.deploy_status import ui_llm_debug
from src.utils.logging import get_logger

jobs_bp = Blueprint("jobs", __name__, url_prefix="/api/jobs")
logger = get_logger(__name__)


def _flatten_grades(job: dict) -> dict:
    """Lift grade dicts, scores, and job-carried rubrics from job_data for list/detail."""
    jd = job.get("job_data") or {}
    # AST-1347: {prefix}_score_breakdown for Analysis phases
    breakdown_keys = tuple(
        f"{p}_{PHASE_SCORE_BREAKDOWN_KEY_SUFFIX}" for p in ("jd", "do", "get", "like")
    )
    for key in (
        "joblist_grades", "joblist_score", "joblist_rubric",
        "jd_grades", "jd_score", "jd_rubric",
        "get_grades", "get_score", "get_rubric",
        "do_grades", "do_score", "do_rubric",
        "like_grades", "like_score", "like_rubric",
        *breakdown_keys,
    ):
        if key in jd:
            job[key] = jd[key]
    # Prefer column latest_score; blob-only joblist_score (legacy) fills gap for list UI
    if job.get("latest_score") is None and jd.get("joblist_score") is not None:
        job["latest_score"] = jd["joblist_score"]
    # AST-1348: derive missing breakdown at read (response only; never write job_data)
    for prefix in ("jd", "do", "get", "like"):
        bk = f"{prefix}_{PHASE_SCORE_BREAKDOWN_KEY_SUFFIX}"
        if bk in job:
            continue
        sk = f"{prefix}_score"
        score = job[sk] if sk in job else jd.get(sk)
        grades = job.get(f"{prefix}_grades")
        rubric = job.get(f"{prefix}_rubric")
        if score is None or not isinstance(grades, list) or not grades:
            continue
        if not isinstance(rubric, list) or not rubric:
            continue
        try:
            job[bk] = _phase_score_breakdown(rubric, grades)
        except (ValueError, TypeError, KeyError):
            pass
    return job


def _attach_skipped_edit_meta(job: dict) -> dict:
    state = job.get("state") or ""
    editable = state in SKIPPED_STATES
    job["fields_editable"] = editable
    job["legal_next_states"] = legal_job_successor_states(state) if editable else []
    return job


def _list_applied_jobs_for_candidate(candidate_id: Optional[str]) -> list[dict]:
    """Applied rows via company.candidate_id scope, plus stem/meteorite repair-on-read."""
    rows = list_jobs(
        states=list(APPLIED_JOB_STATES),
        candidate_id=candidate_id,
        order_by="state_changed_at",
    )
    cid = (candidate_id or "").strip()
    if not cid:
        return rows

    seen = {r.get("astral_job_id") for r in rows if r.get("astral_job_id")}
    default_meteorite = METEORITE_CONFIG["short_name_template"].format(candidate_id=cid)
    suffix = f"-{cid}"

    for job in list_jobs(states=list(APPLIED_JOB_STATES), candidate_id=None, order_by="state_changed_at"):
        jid = job.get("astral_job_id")
        if not jid or jid in seen:
            continue
        co_name = (job.get("company") or "").strip()
        if not co_name or (co_name != default_meteorite and not co_name.endswith(suffix)):
            continue
        company = get_company(co_name)
        if not company:
            continue
        existing = (company.get("candidate_id") or "").strip()
        if existing == cid:
            rows.append(job)
            seen.add(jid)
        elif existing == "":
            update_company(co_name, candidate_id=cid)
            rows.append(job)
            seen.add(jid)

    rows.sort(key=lambda j: (j.get("state_changed_at") or ""), reverse=True)
    return rows


@jobs_bp.route("")
@require_auth
def list_view():
    """List jobs filtered by view.

    Query params:
      view: in_review | skipped | recommended | applied | responded
      candidate_id: scope to one candidate
    """
    view = request.args.get("view", "in_review")
    candidate_id = request.args.get("candidate_id")

    if view == "in_review":
        rows = list_jobs(states=list(IN_REVIEW_STATES), candidate_id=candidate_id, order_by="state_changed_at")
        if candidate_id:
            floors = score_floor_by_trigger_for_candidate(candidate_id)
            if floors:
                rows = [r for r in rows if not job_misses_dispatch_score_floor(r, floors)]
        return jsonify([_flatten_grades(r) for r in rows])
    elif view == "skipped":
        rows = list_jobs(states=list(SKIPPED_STATES), candidate_id=candidate_id, order_by="state_changed_at")
        out = [_flatten_grades(r) for r in rows]
        if candidate_id:
            floors = score_floor_by_trigger_for_candidate(candidate_id)
            for r in list_jobs_below_dispatch_score_floor(candidate_id):
                st = r.get("state")
                fl = floors.get(st)
                ann = dict(r)
                ann["virtual_skip"] = True
                ann["dispatch_score_floor"] = float(fl) if fl is not None else None
                out.append(_flatten_grades(ann))
        out.sort(key=lambda j: (j.get("state_changed_at") or ""), reverse=True)
        return jsonify(out)
    elif view == "recommended":
        rows = list_jobs(states=list(RECOMMENDED_JOB_STATES), candidate_id=candidate_id, order_by="state_changed_at")
        return jsonify([_flatten_grades(r) for r in rows])
    elif view == "applied":
        rows = _list_applied_jobs_for_candidate(candidate_id)
        return jsonify([_flatten_grades(r) for r in rows])
    else:
        return jsonify([])


@jobs_bp.route("/bulk_state", methods=["POST"])
@require_auth
def bulk_state():
    """Set state for multiple jobs. Body: {astral_job_ids: [...], to_state: "..."}"""
    data = request.get_json(force=True)
    ids = data.get("astral_job_ids", [])
    to_state = data.get("to_state", "")
    if not ids or not to_state:
        return jsonify({"error": "astral_job_ids and to_state required"}), 400
    # AST-1156: enforce JOB_STATES priors + state_history (was save_job bypass).
    updated = 0
    for job_id in ids:
        try:
            transition_job_state([job_id], to_state)
            updated += 1
        except ValueError:
            pass
    return jsonify({"updated": updated})


@jobs_bp.route("/<astral_job_id>")
@require_auth
def detail(astral_job_id):
    """Return job detail with agent_story attached."""
    job = get_job(astral_job_id)
    if not job:
        return jsonify({"error": "Not found"}), 404
    job = _flatten_grades(job)
    _attach_skipped_edit_meta(job)
    # AST-1100: pin-resolve proposed_answers; job_resume/cover already table-overlaid via get_job.
    jd = job.get("job_data") if isinstance(job.get("job_data"), dict) else {}
    art = hydrate_job_artifacts_for_display(get_job_artifacts(job) or jd.get("artifacts"))
    job["job_data"] = {**jd, "artifacts": art}
    # AST-1274/AST-1354: secondary soft-fail — no stacktrace for expected missing pieces.
    try:
        job["agent_story"] = get_entity_agent_story(job)
    except Exception as exc:
        logger.warning(
            "detail: get_entity_agent_story failed astral_job_id=%s: %s",
            astral_job_id,
            exc,
        )
        job["agent_story"] = []
    return jsonify(job)


@jobs_bp.route("/<astral_job_id>", methods=["PUT"])
@require_auth
def persist_skipped_edits(astral_job_id):
    """Persist title/link/JD/state for a job currently in SKIPPED_STATES (AST-1453)."""
    data = request.get_json(force=True) or {}
    fields = {
        k: data[k]
        for k in ("job_title", "job_link", "job_description", "state")
        if k in data
    }
    if not fields:
        return jsonify({"error": "No valid fields to update"}), 400
    if not get_job(astral_job_id):
        return jsonify({"error": "Not found"}), 404
    try:
        persist_skipped_job_edits(astral_job_id, fields)
    except ValueError as exc:
        msg = str(exc)
        if (
            msg == "Job is not in a skipped state"
            or msg.startswith("Invalid transition")
            or msg == "job identity collision"
        ):
            return jsonify({"error": msg}), 409
        if "not in allowed list" in msg:
            return jsonify({"error": msg}), 409
        return jsonify({"error": msg}), 400
    return detail(astral_job_id)


@jobs_bp.route("/<astral_job_id>/copy")
@require_auth
def copy_snapshot(astral_job_id):
    """Diagnostic snapshot: stored job plus populated agent_data hops."""
    explicit = request.args.get("debug", "").lower() in ("1", "true", "yes")
    debug = ui_llm_debug(explicit_debug=explicit)
    try:
        snapshot = assemble_job_copy_snapshot(astral_job_id, debug=debug)
    except Exception as exc:
        logger.warning(
            "copy_snapshot failed astral_job_id=%s: %s",
            astral_job_id,
            exc,
        )
        return jsonify({"error": str(exc)}), 500
    if snapshot is None:
        return jsonify({"error": "Not found"}), 404
    return jsonify(snapshot)


@jobs_bp.route("/<astral_job_id>/artifacts/resume_content", methods=["PUT"])
@require_auth
def put_job_resume_content(astral_job_id):
    """AST-1556: legacy URL redirects to job_resume artifacts-table SoT."""
    job = get_job(astral_job_id)
    if not job:
        return jsonify({"error": "Not found"}), 404
    data = request.get_json(force=True) or {}
    body = data.get("resume_content")
    if not isinstance(body, dict):
        return jsonify({"error": "resume_content must be a dict"}), 400
    save_job_artifact_job_resume_body(astral_job_id, body)
    return jsonify({"ok": True})


@jobs_bp.route("/<astral_job_id>/artifacts/job_resume", methods=["PUT"])
@require_auth
def put_job_resume_pin_key(astral_job_id):
    """AST-1556: ArtifactEditor PUTs job_resume → artifacts-table current row."""
    job = get_job(astral_job_id)
    if not job:
        return jsonify({"error": "Not found"}), 404
    data = request.get_json(force=True) or {}
    body = data.get("job_resume")
    if not isinstance(body, dict):
        return jsonify({"error": "job_resume must be a dict"}), 400
    save_job_artifact_job_resume_body(astral_job_id, body)
    return jsonify({"ok": True})


@jobs_bp.route("/<astral_job_id>/artifacts/cover_letter", methods=["PUT"])
@require_auth
def put_job_cover_letter(astral_job_id):
    """AST-1556: persist cover letter as artifacts-table current row."""
    job = get_job(astral_job_id)
    if not job:
        return jsonify({"error": "Not found"}), 404
    data = request.get_json(force=True) or {}
    body = data.get("cover_letter")
    if not isinstance(body, dict):
        return jsonify({"error": "cover_letter must be a dict"}), 400
    save_job_artifact_cover_letter(astral_job_id, body)
    return jsonify({"ok": True})


@jobs_bp.route("/<astral_job_id>/artifacts/application_responses", methods=["PUT"])
@require_auth
def put_job_application_responses(astral_job_id):
    """Merge application Q&A blob into job_data.artifacts.application_responses (AST-565)."""
    job = get_job(astral_job_id)
    if not job:
        return jsonify({"error": "Not found"}), 404
    data = request.get_json(force=True) or {}
    body = data.get("application_responses")
    if not isinstance(body, dict):
        return jsonify({"error": "application_responses must be a dict"}), 400
    save_job_data(
        astral_job_id,
        {"artifacts": {"application_responses": body}},
    )
    return jsonify({"ok": True})


@jobs_bp.route("/<astral_job_id>/artifacts/proposed_answers", methods=["PUT"])
@require_auth
def put_job_proposed_answers(astral_job_id):
    """AST-1100: ArtifactEditor saves under remapped proposed_answers key."""
    job = get_job(astral_job_id)
    if not job:
        return jsonify({"error": "Not found"}), 404
    data = request.get_json(force=True) or {}
    body = data.get("proposed_answers")
    if not isinstance(body, dict):
        return jsonify({"error": "proposed_answers must be a dict"}), 400
    save_job_data(astral_job_id, {"artifacts": {"proposed_answers": body}})
    return jsonify({"ok": True})


@jobs_bp.route("/<astral_job_id>/skip", methods=["POST"])
@require_auth
def skip_job(astral_job_id):
    """Manually skip a job — sets state to CANDIDATE_SKIPPED with state_history entry."""
    job = get_job(astral_job_id)
    if not job:
        return jsonify({"error": "Not found"}), 404
    try:
        transition_job_state([astral_job_id], "CANDIDATE_SKIPPED")
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 409
    return jsonify({"ok": True})


@jobs_bp.route("/<astral_job_id>/generate_artifacts", methods=["POST"])
@require_auth
def generate_artifacts(astral_job_id):
    """Generate Artifacts: RECOMMENDED → BUILD_ARTIFACTS (AST-562 / AST-591)."""
    job = get_job(astral_job_id)
    if not job:
        return jsonify({"error": "Not found"}), 404
    try:
        state = start_artifact_build(astral_job_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 409
    return jsonify({"ok": True, "state": state})


@jobs_bp.route("/<astral_job_id>/cancel_artifact_build", methods=["POST"])
@require_auth
def cancel_artifact_build_route(astral_job_id):
    """Cancel in-progress artifact build: BUILD_ARTIFACTS → RECOMMENDED (AST-562 / AST-591)."""
    job = get_job(astral_job_id)
    if not job:
        return jsonify({"error": "Not found"}), 404
    try:
        state = cancel_artifact_build(astral_job_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 409
    return jsonify({"ok": True, "state": state})


@jobs_bp.route("/<astral_job_id>/approve_artifacts", methods=["POST"])
@require_auth
def approve_artifacts(astral_job_id):
    """Candidate approval: RECOMMENDED → BUILD_ARTIFACTS (AST-478 / AST-552)."""
    job = get_job(astral_job_id)
    if not job:
        return jsonify({"error": "Not found"}), 404
    if job.get("state") != "RECOMMENDED":
        return jsonify({
            "error": "Artifact approval is only allowed when the job is in RECOMMENDED",
        }), 409
    try:
        state = start_artifact_build(astral_job_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 409
    return jsonify({"ok": True, "state": state})


# AST-311: candidate action + candidate_results (UI wires in AST-312).
_CANDIDATE_ACTION_STATE = {
    "applied": "CANDIDATE_APPLIED",
    "interview": "CANDIDATE_INTERVIEW",
    "rejected": "CANDIDATE_REJECTED",
    "ghosted": "CANDIDATE_GHOSTED",
    "review": "CANDIDATE_REVIEW",
}


@jobs_bp.route("/<astral_job_id>/candidate_action", methods=["POST"])
@require_auth
def candidate_action(astral_job_id):
    """Record candidate_results.<action> and transition job state. Body: {action, notes?}."""
    job = get_job(astral_job_id)
    if not job:
        return jsonify({"error": "Not found"}), 404
    data = request.get_json(force=True) or {}
    action = (data.get("action") or "").strip().lower()
    to_state = _CANDIDATE_ACTION_STATE.get(action)
    if not to_state:
        return jsonify({"error": "invalid action"}), 400
    candidate_id = (data.get("candidate_id") or request.args.get("candidate_id") or "").strip()
    if candidate_id and action in _CANDIDATE_ACTION_STATE:
        co_name = (job.get("company") or "").strip()
        if co_name:
            co = get_company(co_name)
            if co:
                existing = (co.get("candidate_id") or "").strip()
                if existing == "":
                    update_company(co["short_name"], candidate_id=candidate_id)
                elif existing != candidate_id:
                    return jsonify({"error": "Job belongs to another candidate"}), 409
    notes = data.get("notes")
    if action != "review":
        set_candidate_result(astral_job_id, action, notes=notes)
    try:
        transition_job_state([astral_job_id], to_state)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 409
    return jsonify({"ok": True, "state": to_state})
