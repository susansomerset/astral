"""API endpoints for Jobs screens: list, detail, bulk state."""

from datetime import datetime, timezone
from flask import Blueprint, jsonify, request

from ui.auth import require_auth
from src.core.roster import get_entity_agent_story
from src.core.tracker import (
    cancel_artifact_build,
    count_jobs,
    get_job,
    get_job_artifacts,
    hydrate_job_artifacts_for_display,
    job_misses_dispatch_score_floor,
    list_jobs,
    list_jobs_below_dispatch_score_floor,
    save_job,
    save_job_artifact_cover_letter,
    save_job_artifact_resume_content,
    save_job_data,
    score_floor_by_trigger_for_candidate,
    set_candidate_result,
    start_artifact_build,
    transition_job_state,
)
from src.utils.config import IN_REVIEW_STATES, RECOMMENDED_JOB_STATES, SKIPPED_STATES

jobs_bp = Blueprint("jobs", __name__, url_prefix="/api/jobs")


def _flatten_grades(job: dict) -> dict:
    """Lift grade dicts, scores, and job-carried rubrics from job_data for list/detail."""
    jd = job.get("job_data") or {}
    for key in (
        "joblist_grades", "joblist_score", "joblist_rubric",
        "jd_grades", "jd_score", "jd_rubric",
        "get_grades", "get_score", "get_rubric",
        "do_grades", "do_score", "do_rubric",
        "like_grades", "like_score", "like_rubric",
    ):
        if key in jd:
            job[key] = jd[key]
    # Prefer column latest_score; blob-only joblist_score (legacy) fills gap for list UI
    if job.get("latest_score") is None and jd.get("joblist_score") is not None:
        job["latest_score"] = jd["joblist_score"]
    return job


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
    # AST-1100: pin-slot strings → resolved bodies for JAR / ArtifactEditor (no persist).
    jd = job.get("job_data") if isinstance(job.get("job_data"), dict) else {}
    art = hydrate_job_artifacts_for_display(get_job_artifacts(job) or jd.get("artifacts"))
    job["job_data"] = {**jd, "artifacts": art}
    job["agent_story"] = get_entity_agent_story(job)
    return jsonify(job)


@jobs_bp.route("/<astral_job_id>/artifacts/resume_content", methods=["PUT"])
@require_auth
def put_job_resume_content(astral_job_id):
    """Merge section-keyed resume draft into job_data.artifacts.resume_content (AST-553)."""
    job = get_job(astral_job_id)
    if not job:
        return jsonify({"error": "Not found"}), 404
    data = request.get_json(force=True) or {}
    body = data.get("resume_content")
    if not isinstance(body, dict):
        return jsonify({"error": "resume_content must be a dict"}), 400
    save_job_artifact_resume_content(astral_job_id, body)
    return jsonify({"ok": True})


@jobs_bp.route("/<astral_job_id>/artifacts/job_resume", methods=["PUT"])
@require_auth
def put_job_resume_pin_key(astral_job_id):
    """AST-1100: ArtifactEditor saves under remapped job_resume key (body dict replaces pin)."""
    job = get_job(astral_job_id)
    if not job:
        return jsonify({"error": "Not found"}), 404
    data = request.get_json(force=True) or {}
    body = data.get("job_resume")
    if not isinstance(body, dict):
        return jsonify({"error": "job_resume must be a dict"}), 400
    save_job_data(astral_job_id, {"artifacts": {"job_resume": body}})
    return jsonify({"ok": True})


@jobs_bp.route("/<astral_job_id>/artifacts/cover_letter", methods=["PUT"])
@require_auth
def put_job_cover_letter(astral_job_id):
    """Merge cover letter artifact into job_data.artifacts.cover_letter (AST-565)."""
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
    notes = data.get("notes")
    if action != "review":
        set_candidate_result(astral_job_id, action, notes=notes)
    try:
        transition_job_state([astral_job_id], to_state)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 409
    return jsonify({"ok": True, "state": to_state})
