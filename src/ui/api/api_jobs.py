"""API endpoints for Jobs screens: list, detail, bulk state."""

from datetime import datetime, timezone
from typing import Optional

from flask import Blueprint, jsonify, request

from ui.auth import require_auth
from ui.api_errors import server_error_from_exception
from src.core.consult import _phase_score_breakdown
from src.core.agent import get_entity_agent_story
from src.core.roster import get_company, update_company
from src.core.candidate import resume_structure_editor_payload
from src.core.tracker import (
    assemble_job_copy_snapshot,
    cancel_artifact_build,
    candidate_skip_job,
    count_jobs,
    get_job,
    get_job_artifacts,
    get_job_effective_resume_structure,
    hydrate_job_artifacts_for_display,
    job_state_admits_transition,
    job_misses_dispatch_score_floor,
    legal_job_successor_states,
    list_jobs,
    list_jobs_below_dispatch_score_floor,
    list_job_artifact_versions,
    persist_skipped_job_edits,
    save_job_artifact,
    save_job_data,
    score_floor_by_trigger_for_candidate,
    set_candidate_result,
    set_job_artifact_current,
    start_artifact_build,
    transition_job_state,
)
from src.data.database import (
    get_meteorite,
    get_meteorite_by_astral_job_id,
    get_meteorite_link_by_astral_job_id,
)
from src.utils.config import (
    APPLIED_JOB_STATES,
    JOBS_PROCESSING_EXCLUDED_STATES,
    PHASE_SCORE_BREAKDOWN_KEY_SUFFIX,
    READY_JOB_STATES,
    REVIEW_JOB_STATES,
    SKIPPED_STATES,
    SOURCE_ENTITY_TYPE_METEORITE,
)
from src.utils.deploy_status import ui_llm_debug
from src.utils.logging import get_logger

jobs_bp = Blueprint("jobs", __name__, url_prefix="/api/jobs")
logger = get_logger(__name__)


def _http_listing_url(raw) -> Optional[str]:
    """Return stripped http(s) URL, else None. Non-http breadcrumbs → None."""
    if raw is None:
        return None
    s = str(raw).strip()
    if s.startswith("http://") or s.startswith("https://"):
        return s
    return None


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


@jobs_bp.route("")
@require_auth
def list_view():
    """List jobs filtered by view.

    Query params:
      view: ready | review | applied | processing | skipped
      candidate_id: scope to one candidate
    """
    view = request.args.get("view", "ready")
    candidate_id = request.args.get("candidate_id")

    if view == "ready":
        rows = list_jobs(states=list(READY_JOB_STATES), candidate_id=candidate_id, order_by="state_changed_at")
        return jsonify([_flatten_grades(r) for r in rows])
    elif view == "review":
        rows = list_jobs(states=list(REVIEW_JOB_STATES), candidate_id=candidate_id, order_by="state_changed_at")
        return jsonify([_flatten_grades(r) for r in rows])
    elif view == "applied":
        # job.candidate_id scoping (AST-1598) covers every Applied row; no company-linkage repair.
        rows = list_jobs(states=list(APPLIED_JOB_STATES), candidate_id=candidate_id, order_by="state_changed_at")
        return jsonify([_flatten_grades(r) for r in rows])
    elif view == "processing":
        # Complement of the four explicit lists — never an include-list (AST-1974).
        rows = list_jobs(
            exclude_states=list(JOBS_PROCESSING_EXCLUDED_STATES),
            candidate_id=candidate_id,
            order_by="state_changed_at",
        )
        if candidate_id:
            # Below-floor rows are virtual skips — they show on Skipped only.
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
    # AST-1872: server-resolved Skip legality for the Recommended report (core owns the prior-state rule)
    job["can_skip"] = job_state_admits_transition(job.get("state") or "", "CANDIDATE_SKIPPED")
    # AST-1100/1592: pin-resolve proposed_answers; re-hydrate with job id for catalog current-read.
    jd = job.get("job_data") if isinstance(job.get("job_data"), dict) else {}
    art = hydrate_job_artifacts_for_display(
        get_job_artifacts(job) or jd.get("artifacts"),
        astral_job_id=astral_job_id,
    )
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
    # AST-1704: parent/track fields + employer for Job Detail consumers
    job["company_id"] = job.get("company_id")
    job["source"] = job.get("source")
    job["source_entity_id"] = job.get("source_entity_id")
    # AST-1691: reverse-link meteorite provenance for Recommended report pane.
    # AST-1769: if reverse link misses, fall back via job.source / source_entity_id.
    try:
        logger.debug(
            "Calling get_meteorite_by_astral_job_id: [astral_job_id=%s]",
            astral_job_id,
        )
        row = get_meteorite_by_astral_job_id(astral_job_id)
        # Full row — stat.logging.debug: no truncation of callee response.
        logger.debug("Response from get_meteorite_by_astral_job_id: %s", row)
        if row is None:
            src = (job.get("source") or "").strip()
            sid = str(job.get("source_entity_id") or "").strip()
            if src == SOURCE_ENTITY_TYPE_METEORITE and sid and sid.isdigit():
                logger.debug("Calling get_meteorite: [meteorite_id=%s]", sid)
                row = get_meteorite(int(sid))
                logger.debug("Response from get_meteorite: %s", row)
        if row is None:
            job["related_meteorite"] = None
        else:
            job["related_meteorite"] = {
                "id": row.get("id"),
                "created_at": row.get("created_at"),
                "updated_at": row.get("updated_at"),
                "state_changed_at": row.get("state_changed_at"),
                "estelle_notified_at": row.get("estelle_notified_at"),
                "link": row.get("link"),
                "classify_outcome": row.get("classify_outcome"),
                "content": row.get("content"),
                "state": row.get("state"),
                "source_kind": row.get("source_kind"),
                "source_id": row.get("source_id"),
                "error": row.get("error"),
            }
    except Exception as exc:
        logger.exception(
            "%s | api %s related_meteorite lookup failed\n  %s: %s\n  Returning related_meteorite=null",
            job.get("candidate_id") or "-",
            f"/api/jobs/{astral_job_id}",
            type(exc).__name__,
            exc,
        )
        job["related_meteorite"] = None
    # AST-1694: resolved http(s) listing href (job.job_link else meteorite.link).
    listing = _http_listing_url(job.get("job_link"))
    if listing is None:
        try:
            logger.debug(
                "Calling get_meteorite_link_by_astral_job_id: [astral_job_id=%s]",
                astral_job_id,
            )
            meta_link = get_meteorite_link_by_astral_job_id(astral_job_id)
            logger.debug(
                "Response from get_meteorite_link_by_astral_job_id: %s",
                meta_link,
            )
            listing = _http_listing_url(meta_link)
        except Exception as exc:
            logger.exception(
                "%s | api %s listing_href meteorite lookup failed\n  %s: %s\n"
                "  Continuing with listing_href from job.job_link only",
                job.get("candidate_id") or "-",
                f"/api/jobs/{astral_job_id}",
                type(exc).__name__,
                exc,
            )
            listing = None
    job["listing_href"] = listing
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
    """AST-1556/1592: legacy URL → catalog job_resume write."""
    job = get_job(astral_job_id)
    if not job:
        return jsonify({"error": "Not found"}), 404
    data = request.get_json(force=True) or {}
    body = data.get("resume_content")
    if not isinstance(body, dict):
        return jsonify({"error": "resume_content must be a dict"}), 400
    save_job_artifact(astral_job_id, "job.artifacts.job_resume", body)
    return jsonify({"ok": True})


@jobs_bp.route("/<astral_job_id>/artifacts/job_resume", methods=["PUT"])
@require_auth
def put_job_resume_pin_key(astral_job_id):
    """AST-1556/1592: ArtifactEditor PUTs job_resume via catalog write."""
    job = get_job(astral_job_id)
    if not job:
        return jsonify({"error": "Not found"}), 404
    data = request.get_json(force=True) or {}
    body = data.get("job_resume")
    if not isinstance(body, dict):
        return jsonify({"error": "job_resume must be a dict"}), 400
    save_job_artifact(astral_job_id, "job.artifacts.job_resume", body)
    return jsonify({"ok": True})


@jobs_bp.route("/<astral_job_id>/artifacts/cover_letter", methods=["PUT"])
@require_auth
def put_job_cover_letter(astral_job_id):
    """AST-1556/1592: persist cover letter via catalog write."""
    job = get_job(astral_job_id)
    if not job:
        return jsonify({"error": "Not found"}), 404
    data = request.get_json(force=True) or {}
    body = data.get("cover_letter")
    if not isinstance(body, dict):
        return jsonify({"error": "cover_letter must be a dict"}), 400
    save_job_artifact(astral_job_id, "job.artifacts.cover_letter", body)
    return jsonify({"ok": True})


@jobs_bp.route("/<astral_job_id>/resume_structure")
@require_auth
def get_job_resume_structure(astral_job_id):
    """AST-2081: structure-editor payload for the job's effective resume structure (read-only)."""
    job = get_job(astral_job_id)
    if not job:
        return jsonify({"error": "Not found"}), 404
    cid = job.get("candidate_id") or "-"
    route = f"/api/jobs/{astral_job_id}/resume_structure"
    try:
        payload = resume_structure_editor_payload(
            get_job_effective_resume_structure(astral_job_id, hydrate_from_base=True)
        )
    except Exception as exc:
        logger.exception(
            "%s | api %s failed\n  %s: %s\n  Returning 500; the job resume editor shows no sections",
            cid,
            route,
            type(exc).__name__,
            exc,
        )
        return server_error_from_exception(exc)
    return jsonify(payload)


@jobs_bp.route("/<astral_job_id>/artifacts/job_resume_structure", methods=["PUT"])
@require_auth
def put_job_resume_structure(astral_job_id):
    """AST-2081: write the job's own resume structure via catalog write (candidate structure untouched)."""
    job = get_job(astral_job_id)
    if not job:
        return jsonify({"error": "Not found"}), 404
    data = request.get_json(silent=True)
    body = data.get("job_resume_structure") if isinstance(data, dict) else None
    if not isinstance(body, dict):
        return jsonify({"error": "job_resume_structure must be a dict"}), 400
    cid = job.get("candidate_id") or "-"
    route = f"/api/jobs/{astral_job_id}/artifacts/job_resume_structure"
    try:
        save_job_artifact(astral_job_id, "job.artifacts.job_resume_structure", body)
    except ValueError as exc:
        # Invalid structure (normalize / slug reject) — routed 400, no log.
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        logger.exception(
            "%s | api %s failed\n  %s: %s\n  Returning 500; the job resume structure is unchanged",
            cid,
            route,
            type(exc).__name__,
            exc,
        )
        return server_error_from_exception(exc)
    logger.info("%s | api %s completed: PUT %s", cid, route, 200)
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


@jobs_bp.route("/<astral_job_id>/artifacts/<artifact_key>/versions", methods=["GET"])
@require_auth
def get_job_artifact_versions_api(astral_job_id, artifact_key):
    """AST-2067: chronological version map for a job catalog key (oldest first)."""
    job = get_job(astral_job_id)
    if not job:
        return jsonify({"error": "Not found"}), 404
    try:
        versions = list_job_artifact_versions(astral_job_id, artifact_key)
    except ValueError as exc:
        # Unknown / non-job catalog key — routed reject, no log.
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        logger.exception(
            "%s | api %s failed\n  %s: %s\n  Returning 500; the editor shows no version arrows",
            job.get("candidate_id") or "-",
            f"/api/jobs/{astral_job_id}/artifacts/{artifact_key}/versions",
            type(exc).__name__,
            exc,
        )
        return server_error_from_exception(exc)
    return jsonify({"versions": versions})


@jobs_bp.route("/<astral_job_id>/artifacts/<artifact_key>/current", methods=["PUT"])
@require_auth
def put_job_artifact_current_api(astral_job_id, artifact_key):
    """AST-2067: move current to a named version of a job catalog key; body untouched."""
    job = get_job(astral_job_id)
    if not job:
        return jsonify({"error": "Not found"}), 404
    body = request.get_json(silent=True)
    uid = body.get("artifact_uuid") if isinstance(body, dict) else None
    if not isinstance(uid, str) or not uid.strip():
        return jsonify({"error": "artifact_uuid required"}), 400
    cid = job.get("candidate_id") or "-"
    route = f"/api/jobs/{astral_job_id}/artifacts/{artifact_key}/current"
    try:
        current = set_job_artifact_current(astral_job_id, artifact_key, uid)
        versions = list_job_artifact_versions(astral_job_id, artifact_key)
    except ValueError as exc:
        # Bad key, or uuid outside this job/key (cross-key guard) — data layer rolled back.
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        logger.exception(
            "%s | api %s failed\n  %s: %s\n  Returning 500; the editor keeps its loaded version",
            cid,
            route,
            type(exc).__name__,
            exc,
        )
        return server_error_from_exception(exc)
    logger.info("%s | api %s completed: PUT %s", cid, route, 200)
    return jsonify({"current": current, "versions": versions})


@jobs_bp.route("/<astral_job_id>/skip", methods=["POST"])
@require_auth
def skip_job(astral_job_id):
    """Candidate Skip from any non-Applied, non-Skipped state → CANDIDATE_SKIPPED; core releases a held batch claim."""
    job = get_job(astral_job_id)
    if not job:
        return jsonify({"error": "Not found"}), 404
    try:
        candidate_skip_job(astral_job_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 409
    logger.info(
        "%s | api %s completed: POST %s",
        job.get("candidate_id") or "-",
        f"/api/jobs/{astral_job_id}/skip",
        200,
    )
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
