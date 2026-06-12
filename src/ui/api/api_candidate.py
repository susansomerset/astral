"""Candidate API endpoints: list, get, create, update candidate data, generate artifacts."""

import base64
import binascii
import struct

from flask import Blueprint, jsonify, request

from ui.auth import require_auth
from src.core.candidate import (
    apply_company_search_terms_save,
    clear_candidate_api_key,
    company_search_terms_joined_text,
    company_search_terms_lines_for_candidate,
    delete_candidate as core_delete_candidate,
    get_candidate,
    initiate_candidate,
    list_candidates as core_list_candidates,
    company_search_terms_joined_text,
    company_search_terms_lines_for_candidate,
    normalize_rubric_artifacts_on_save,
    run_candidate_artifact_generation,
    save_candidate_admin,
    save_candidate_data,
)
from src.utils.config import CANDIDATE_STATES, TASK_CONFIG, UI_CONFIG

candidate_bp = Blueprint("candidate", __name__, url_prefix="/api/candidates")

_SENTINEL_CLEAR = ""

_SIG_IMG_LIMITS = UI_CONFIG["cover_letter_signature_image"]
_MAX_COVER_SIG_W = _SIG_IMG_LIMITS["max_width_px"]
_MAX_COVER_SIG_H = _SIG_IMG_LIMITS["max_height_px"]


def _jpeg_dimensions(raw: bytes):
    """Read width/height from JPEG SOF marker; None if not a JPEG."""
    if len(raw) < 4 or raw[0:2] != b"\xff\xd8":
        return None
    i = 2
    while i + 9 < len(raw):
        if raw[i] != 0xFF:
            return None
        marker = raw[i + 1]
        if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            height = struct.unpack(">H", raw[i + 5 : i + 7])[0]
            width = struct.unpack(">H", raw[i + 7 : i + 9])[0]
            return width, height
        seg_len = struct.unpack(">H", raw[i + 2 : i + 4])[0]
        if seg_len < 2:
            return None
        i += 2 + seg_len
    return None


def _validate_cover_letter_signature_image(value) -> None:
    """AST-366: profile.cover_letter_signature_image must be empty or a bounded JPEG data URL."""
    if value is None or value == "":
        return
    if not isinstance(value, str):
        raise ValueError("cover_letter_signature_image must be a string")
    low = value.strip().lower()
    if not low.startswith("data:image/jpeg;base64,"):
        raise ValueError("cover_letter_signature_image must be a JPEG data URL")
    try:
        raw = base64.b64decode(value.split(",", 1)[1], validate=True)
    except (binascii.Error, IndexError, ValueError) as exc:
        raise ValueError("cover_letter_signature_image is not valid base64") from exc
    dims = _jpeg_dimensions(raw)
    if not dims:
        raise ValueError("cover_letter_signature_image is not a valid JPEG")
    width, height = dims
    if width > _MAX_COVER_SIG_W or height > _MAX_COVER_SIG_H:
        raise ValueError(
            f"cover_letter_signature_image must be at most {_MAX_COVER_SIG_W}x{_MAX_COVER_SIG_H} pixels"
        )


def _sanitize_candidate(c: dict) -> dict:
    """Strip ciphertext, inject has_api_key boolean. Applied to every outbound candidate."""
    c["has_api_key"] = bool(c.get("candidate_api_key"))
    c.pop("candidate_api_key", None)
    return c


@candidate_bp.route("")
@require_auth
def list_candidates():
    include_deleted = request.args.get("include_deleted", "").lower() == "true"
    return jsonify([_sanitize_candidate(c) for c in core_list_candidates(include_deleted=include_deleted)])


# Must be registered before the /<candidate_id> catch-all
@candidate_bp.route("/states")
@require_auth
def get_candidate_states():
    return jsonify(list(CANDIDATE_STATES.keys()))


@candidate_bp.route("/<candidate_id>")
@require_auth
def get_candidate_detail(candidate_id):
    candidate = get_candidate(candidate_id)
    if not candidate:
        return jsonify({"error": f"Candidate not found: {candidate_id}"}), 404
    # AST-526: table-backed field for Artifacts textarea (not artifacts blob).
    candidate["company_search_terms"] = company_search_terms_joined_text(candidate_id)
    return jsonify(_sanitize_candidate(candidate))


@candidate_bp.route("", methods=["POST"])
@require_auth
def create_candidate():
    body = request.get_json(silent=True) or {}
    candidate_id = body.get("astral_candidate_id", "").strip().lower()
    if not candidate_id:
        return jsonify({"error": "astral_candidate_id is required"}), 400
    candidate_data = body.get("candidate_data", {})
    try:
        initiate_candidate(candidate_id, candidate_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"created": candidate_id}), 201


@candidate_bp.route("/<candidate_id>/data", methods=["PUT"])
@require_auth
def update_candidate_data(candidate_id):
    """Update candidate_data fields (merge=True). If 'state' is in the body,
    applies it as a direct admin override (bypasses transition validation).
    api_key handling: non-empty string = set/replace, empty string = clear to NULL."""
    body = request.get_json(silent=True) or {}
    if not body:
        return jsonify({"error": "No data provided"}), 400
    try:
        state_override = body.pop("state", None)
        api_key = body.pop("api_key", None)
        if body:
            arts = body.get("artifacts")
            if isinstance(arts, dict):
                apply_company_search_terms_save(candidate_id, arts)
                candidate = get_candidate(candidate_id)
                cd = (candidate.get("candidate_data") or {}) if candidate else {}
                resolved = resolve_resume_structure(cd)
                section_ids = {s["id"] for s in enabled_resume_structure_sections(resolved)}
                if "base_resume" in arts and isinstance(arts["base_resume"], dict):
                    arts["base_resume"] = filter_base_resume_to_structure(
                        arts["base_resume"], section_ids
                    )
                if "resume_structure" in arts and isinstance(arts["resume_structure"], dict):
                    rs_in = arts["resume_structure"]
                    merged = dict(resolved)
                    if isinstance(rs_in.get("sections"), dict):
                        merged["sections"] = {**resolved.get("sections", {}), **rs_in["sections"]}
                    if "accent_color" in rs_in:
                        merged["accent_color"] = rs_in["accent_color"]
                    try:
                        arts["resume_structure"] = normalize_resume_structure(merged)
                    except ValueError as e:
                        msg = str(e)
                        if "accent" in msg.lower():
                            return jsonify({"error": "invalid accent_color"}), 400
                        return jsonify({"error": "invalid resume_structure"}), 400
                if not arts:
                    body.pop("artifacts", None)
                else:
                    normalize_rubric_artifacts_on_save(arts)
            prof = body.get("profile")
            if isinstance(prof, dict) and "cover_letter_signature_image" in prof:
                _validate_cover_letter_signature_image(prof.get("cover_letter_signature_image"))
            if body:
                save_candidate_data(candidate_id, body, replace=False)
        if state_override is not None:
            save_candidate_admin(candidate_id, state=state_override)
        if api_key is not None:
            if api_key.strip():
                save_candidate_admin(candidate_id, candidate_api_key=api_key.strip())
            else:
                clear_candidate_api_key(candidate_id)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    updated = get_candidate(candidate_id)
    return jsonify(_sanitize_candidate(updated) if updated else {})


@candidate_bp.route("/<candidate_id>/company_search_terms/sync", methods=["PUT"])
@require_auth
def sync_company_search_terms(candidate_id):
    """Sync company_search_terms table from multiline textarea content."""
    body = request.get_json(silent=True) or {}
    if "search_terms" not in body:
        return jsonify({"error": "search_terms is required"}), 400
    candidate = get_candidate(candidate_id)
    if not candidate:
        return jsonify({"error": f"Candidate not found: {candidate_id}"}), 404
    try:
        apply_company_search_terms_save(
            candidate_id,
            {"company_search_terms": body["search_terms"]},
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({
        "search_terms": company_search_terms_joined_text(candidate_id),
        "terms": company_search_terms_lines_for_candidate(candidate_id),
    })


@candidate_bp.route("/<candidate_id>", methods=["DELETE"])
@require_auth
def delete_candidate(candidate_id):
    try:
        core_delete_candidate(candidate_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"deleted": candidate_id})


@candidate_bp.route("/<candidate_id>/generate/<task_key>", methods=["POST"])
@require_auth
def generate_artifact(candidate_id, task_key):
    """Run do_task for a craft_* task, tracking through the dispatch pattern.
    Creates a ledger entry, sets log_batch_id, stores agent_data blocks.
    The frontend decides whether to display and let the user Save or Cancel."""
    if task_key not in TASK_CONFIG:
        return jsonify({"error": f"Unknown task: {task_key}"}), 400

    candidate = get_candidate(candidate_id)
    if not candidate:
        return jsonify({"error": f"Candidate not found: {candidate_id}"}), 404

    cd = candidate.get("candidate_data") or {}
    live = None
    if task_key == "craft_resume_base":
        live = (cd.get("context") or {}).get("starting_resume_text", "")

    body, status = run_candidate_artifact_generation(candidate_id, task_key, live)
    return jsonify(body), status
