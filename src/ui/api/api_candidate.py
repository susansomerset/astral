"""Candidate API endpoints: list, get, create, update candidate data, generate artifacts."""

import base64
import binascii
import copy
import struct

from flask import Blueprint, g, jsonify, request

from ui.auth import require_auth, require_admin
from ui.api_errors import server_error_from_exception
from src.core.candidate import (
    _clear_pending_craft_generation,
    _stash_pending_craft_generation,
    apply_company_search_terms_save,
    apply_rubric_vectors_save,
    company_search_terms_joined_text,
    company_search_terms_lines_for_candidate,
    delete_candidate as core_delete_candidate,
    enabled_resume_structure_sections,
    filter_base_resume_to_structure,
    ingest_legacy_label_content_base_resume,
    get_candidate,
    get_candidate_id_for_query,
    get_pending_craft_generation,
    hydrate_operative_base_resume_for_response,
    hydrate_operative_bio_summary_for_response,
    hydrate_operative_deal_breakers_for_response,
    hydrate_operative_ideal_day_for_response,
    hydrate_operative_backstory_for_response,
    hydrate_operative_resume_structure_for_response,
    hydrate_operative_strengths_for_response,
    hydrate_operative_priorities_for_response,
    hydrate_operative_writing_preferences_for_response,
    hydrate_resume_structure_from_base_resume,
    hydrate_rubric_artifacts_for_response,
    IllegalCandidateTransition,
    initiate_candidate,
    list_candidates as core_list_candidates,
    list_candidate_artifact_versions,
    list_rubric_criterion_versions,
    normalize_resume_structure,
    normalize_rubric_artifacts_on_save,
    prepare_resume_structure_sections_for_save,
    resolve_resume_structure,
    resume_structure_editor_payload,
    run_candidate_artifact_generation,
    save_candidate_data,
    set_candidate_artifact_current,
    set_rubric_criterion_current,
    start_requested_artifacts,
    transition_candidate_state,
    update_candidate_api_keys,
)
from src.core.contact import resolve_pinned_base_resume
from src.utils.config import (
    CANDIDATE_STATES,
    CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY,
    LLM_SERVER_CONFIG,
    RUBRIC_CRITERIA_ARTIFACT_KEYS,
    TASK_CONFIG,
    UI_CONFIG,
)
from src.utils.deploy_status import ui_llm_debug
from src.utils.logging import get_logger

candidate_bp = Blueprint("candidate", __name__, url_prefix="/api/candidates")
logger = get_logger(__name__)

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
    """AST-366: contact.cover_letter_signature_image must be empty or a bounded JPEG data URL."""
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
    """Strip every key (plaintext map + legacy ciphertext); expose the api_keys array as [{server, label}]. Applied to every outbound candidate."""
    keys = c.pop("candidate_api_keys", None) or {}
    c.pop("candidate_api_key", None)
    # One entry per stored key, in array order (AST-1901) — no fixed per-server slots, never the key itself.
    c["api_keys"] = [
        {"server": sid, "label": (LLM_SERVER_CONFIG.get(sid) or {}).get("label", sid)} for sid in keys
    ]
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


# Must be registered before the /<candidate_id> catch-all
@candidate_bp.route("/by_email")
@require_auth
def get_candidate_by_email():
    """AST-1768: unique candidate id whose profile emails match ?email= (login bind)."""
    email = (request.args.get("email") or "").strip()
    if "@" not in email:
        return jsonify({"error": "email required"}), 400
    # Unique hit only; no/ambiguous match → null so the SPA keeps its stored selection.
    return jsonify({"candidate_id": get_candidate_id_for_query(email)})


@candidate_bp.route("/<candidate_id>/resume_structure")
@require_auth
def get_candidate_resume_structure(candidate_id):
    candidate = get_candidate(candidate_id)
    if not candidate:
        return jsonify({"error": f"Candidate not found: {candidate_id}"}), 404
    cd = candidate.get("candidate_data") or {}
    artifacts = cd.get("artifacts") if isinstance(cd.get("artifacts"), dict) else {}
    resolved = hydrate_resume_structure_from_base_resume(
        resolve_resume_structure(cd),
        artifacts.get("base_resume"),
    )
    return jsonify(resume_structure_editor_payload(resolved))


@candidate_bp.route("/<candidate_id>")
@require_auth
def get_candidate_detail(candidate_id):
    candidate = get_candidate(candidate_id)
    if not candidate:
        return jsonify({"error": f"Candidate not found: {candidate_id}"}), 404
    # AST-526: table-backed field for Artifacts textarea (not artifacts blob).
    candidate["company_search_terms"] = company_search_terms_joined_text(candidate_id)
    cd = candidate.get("candidate_data") or {}
    hydrate_rubric_artifacts_for_response(candidate_id, cd)
    hydrate_operative_base_resume_for_response(candidate_id, cd)
    hydrate_operative_resume_structure_for_response(candidate_id, cd)
    hydrate_operative_strengths_for_response(candidate_id, cd)
    hydrate_operative_priorities_for_response(candidate_id, cd)
    hydrate_operative_deal_breakers_for_response(candidate_id, cd)
    hydrate_operative_bio_summary_for_response(candidate_id, cd)
    hydrate_operative_ideal_day_for_response(candidate_id, cd)
    hydrate_operative_backstory_for_response(candidate_id, cd)
    hydrate_operative_writing_preferences_for_response(candidate_id, cd)
    candidate["candidate_data"] = cd
    return jsonify(_sanitize_candidate(candidate))


@candidate_bp.route("/<candidate_id>/operative/base_resume", methods=["GET"])
@require_auth
def get_operative_base_resume_api(candidate_id):
    """AST-1585: pin→body for pilot base_resume (patt.artifact.read-operative)."""
    if not get_candidate(candidate_id):
        return jsonify({"error": f"Candidate not found: {candidate_id}"}), 404
    artifact_id = (request.args.get("artifact_id") or "").strip()
    if not artifact_id:
        return jsonify({"error": "artifact_id required"}), 400
    body = resolve_pinned_base_resume(
        candidate_id, artifact_id, debug=ui_llm_debug()
    )
    if body is None:
        return jsonify({"error": "base_resume not found for pin"}), 404
    return jsonify({"base_resume": body})


@candidate_bp.route("/<candidate_id>/artifacts/<artifact_key>/versions", methods=["GET"])
@require_auth
def get_candidate_artifact_versions_api(candidate_id, artifact_key):
    """AST-2067: chronological version map for a candidate catalog key (oldest first)."""
    if not get_candidate(candidate_id):
        return jsonify({"error": f"Candidate not found: {candidate_id}"}), 404
    try:
        versions = list_candidate_artifact_versions(candidate_id, artifact_key)
    except ValueError as exc:
        # Unknown / non-candidate catalog key — routed reject, no log.
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        logger.exception(
            "%s | api %s failed\n  %s: %s\n  Returning 500; the editor shows no version arrows",
            candidate_id,
            f"/api/candidates/{candidate_id}/artifacts/{artifact_key}/versions",
            type(exc).__name__,
            exc,
        )
        return server_error_from_exception(exc)
    return jsonify({"versions": versions})


@candidate_bp.route("/<candidate_id>/artifacts/<artifact_key>/current", methods=["PUT"])
@require_auth
def put_candidate_artifact_current_api(candidate_id, artifact_key):
    """AST-2067: move current to a named version of a candidate catalog key; body untouched."""
    if not get_candidate(candidate_id):
        return jsonify({"error": f"Candidate not found: {candidate_id}"}), 404
    body = request.get_json(silent=True)
    uid = body.get("artifact_uuid") if isinstance(body, dict) else None
    if not isinstance(uid, str) or not uid.strip():
        return jsonify({"error": "artifact_uuid required"}), 400
    route = f"/api/candidates/{candidate_id}/artifacts/{artifact_key}/current"
    try:
        current = set_candidate_artifact_current(candidate_id, artifact_key, uid)
        versions = list_candidate_artifact_versions(candidate_id, artifact_key)
    except ValueError as exc:
        # Bad key, or uuid outside this key/candidate (cross-key guard) — data layer rolled back.
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        logger.exception(
            "%s | api %s failed\n  %s: %s\n  Returning 500; the editor keeps its loaded version",
            candidate_id,
            route,
            type(exc).__name__,
            exc,
        )
        return server_error_from_exception(exc)
    logger.info("%s | api %s completed: PUT %s", candidate_id, route, 200)
    return jsonify({"current": current, "versions": versions})


@candidate_bp.route("/<candidate_id>/rubric/<artifact_key>/<code>/versions", methods=["GET"])
@require_auth
def get_rubric_criterion_versions_api(candidate_id, artifact_key, code):
    """AST-2067: chronological version map for one rubric criterion (shared code, oldest first)."""
    if not get_candidate(candidate_id):
        return jsonify({"error": f"Candidate not found: {candidate_id}"}), 404
    try:
        versions = list_rubric_criterion_versions(candidate_id, artifact_key, code)
    except ValueError as exc:
        # Not a rubric criteria key — routed reject, no log.
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        logger.exception(
            "%s | api %s failed\n  %s: %s\n  Returning 500; the criterion shows no version arrows",
            candidate_id,
            f"/api/candidates/{candidate_id}/rubric/{artifact_key}/{code}/versions",
            type(exc).__name__,
            exc,
        )
        return server_error_from_exception(exc)
    return jsonify({"versions": versions})


@candidate_bp.route("/<candidate_id>/rubric/<artifact_key>/<code>/current", methods=["PUT"])
@require_auth
def put_rubric_criterion_current_api(candidate_id, artifact_key, code):
    """AST-2067: move current to a named version of one rubric criterion; other codes untouched."""
    if not get_candidate(candidate_id):
        return jsonify({"error": f"Candidate not found: {candidate_id}"}), 404
    body = request.get_json(silent=True)
    uid = body.get("rubric_vector_uuid") if isinstance(body, dict) else None
    if not isinstance(uid, str) or not uid.strip():
        return jsonify({"error": "rubric_vector_uuid required"}), 400
    route = f"/api/candidates/{candidate_id}/rubric/{artifact_key}/{code}/current"
    try:
        current = set_rubric_criterion_current(candidate_id, artifact_key, code, uid)
        versions = list_rubric_criterion_versions(candidate_id, artifact_key, code)
    except ValueError as exc:
        # Bad key, or uuid outside this candidate/task/code (cross-key guard) — data layer rolled back.
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        logger.exception(
            "%s | api %s failed\n  %s: %s\n  Returning 500; the criterion keeps its loaded version",
            candidate_id,
            route,
            type(exc).__name__,
            exc,
        )
        return server_error_from_exception(exc)
    logger.info("%s | api %s completed: PUT %s", candidate_id, route, 200)
    return jsonify({"current": current, "versions": versions})


@candidate_bp.route("", methods=["POST"])
@require_admin
def create_candidate():
    body = request.get_json(silent=True) or {}
    candidate_id = body.get("astral_candidate_id", "").strip().lower()
    if not candidate_id:
        return jsonify({"error": "astral_candidate_id is required"}), 400
    candidate_data = body.get("candidate_data", {}) or {}
    try:
        initiate_candidate(
            candidate_id,
            candidate_data,
            first=body.get("first"),
            last=body.get("last"),
            full=body.get("full"),
            pronouns=body.get("pronouns"),
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"created": candidate_id}), 201


@candidate_bp.route("/<candidate_id>/data", methods=["PUT"])
@require_auth
def update_candidate_data(candidate_id):
    """Update candidate_data fields (merge=True). If 'state' is in the body,
    applies it via transition_candidate_state (fail closed on illegal hops).
    api_keys handling ([{server, key}]): non-empty key = set/replace that server's entry, "" = remove it; duplicate servers → 400."""
    body = request.get_json(silent=True) or {}
    if not body:
        return jsonify({"error": "No data provided"}), 400
    # AST-904: capture submitted rubric before apply deletes keys; re-stash on failure
    submitted_rubric = {}
    rubric_keys_to_clear = []
    strengths_saved = False
    priorities_saved = False
    deal_breakers_saved = False
    bio_summary_saved = False
    ideal_day_saved = False
    backstory_saved = False
    writing_preferences_saved = False
    resume_structure_saved = False
    try:
        state_override = body.pop("state", None)
        api_keys = body.pop("api_keys", None)
        confirm_override = body.pop("confirm_state_override", False)
        if not g.user.get("is_admin") and (
            state_override is not None or api_keys is not None or confirm_override is True
        ):
            return jsonify({"error": "Admin access required"}), 403
        if api_keys is not None:
            if not isinstance(api_keys, list):
                return jsonify({"error": "api_keys must be an array of {server, key}"}), 400
            seen_servers: set = set()
            for e in api_keys:
                sid = e.get("server") if isinstance(e, dict) else None
                if sid not in LLM_SERVER_CONFIG or not isinstance(e.get("key"), str):
                    # Name the server only — never echo a submitted key.
                    return jsonify({"error": f"Invalid api_keys entry for server {sid!r}"}), 400
                if sid in seen_servers:
                    return jsonify({"error": f"Duplicate api_keys entry for server {sid!r}"}), 400
                seen_servers.add(sid)
        base_resume_in_save = False
        pilot_body = None
        resume_structure_body = None
        if body:
            # AST-1633 / AST-1649 / AST-1652 / AST-1655 / AST-1659 / AST-1662 / AST-1665: catalog context leaves → operative save; do not library-merge.
            strengths_body = None
            priorities_body = None
            deal_breakers_body = None
            bio_summary_body = None
            ideal_day_body = None
            backstory_body = None
            writing_preferences_body = None
            ctx = body.get("context")
            if isinstance(ctx, dict):
                if "strengths" in ctx:
                    strengths_body = ctx.pop("strengths")
                if "priorities" in ctx:
                    priorities_body = ctx.pop("priorities")
                if "deal_breakers" in ctx:
                    deal_breakers_body = ctx.pop("deal_breakers")
                if "bio_summary" in ctx:
                    bio_summary_body = ctx.pop("bio_summary")
                if "ideal_day" in ctx:
                    ideal_day_body = ctx.pop("ideal_day")
                if "backstory" in ctx:
                    backstory_body = ctx.pop("backstory")
                if "writing_preferences" in ctx:
                    writing_preferences_body = ctx.pop("writing_preferences")
                if not ctx:
                    body.pop("context", None)
            arts = body.get("artifacts")
            if isinstance(arts, dict):
                apply_company_search_terms_save(candidate_id, arts)
                candidate = get_candidate(candidate_id)
                cd = (candidate.get("candidate_data") or {}) if candidate else {}
                resolved = resolve_resume_structure(cd)
                section_ids = {s["id"] for s in enabled_resume_structure_sections(resolved)}
                if "resume_structure" in arts and isinstance(arts["resume_structure"], dict):
                    rs_in = arts["resume_structure"]
                    merged = dict(resolved)
                    if isinstance(rs_in.get("sections"), dict):
                        merged["sections"] = prepare_resume_structure_sections_for_save(rs_in["sections"])
                    if "accent_color" in rs_in:
                        merged["accent_color"] = rs_in["accent_color"]
                    try:
                        arts["resume_structure"] = normalize_resume_structure(merged)
                    except ValueError as e:
                        msg = str(e)
                        if "accent" in msg.lower():
                            return jsonify({"error": "invalid accent_color"}), 400
                        return jsonify({"error": msg}), 400
                if "base_resume" in arts and isinstance(arts["base_resume"], (list, dict)):
                    content, ingested_struct = ingest_legacy_label_content_base_resume(
                        arts["base_resume"], arts.get("resume_structure") or resolved
                    )
                    arts["base_resume"] = content
                    arts["resume_structure"] = ingested_struct
                    section_ids = {
                        s["id"] for s in enabled_resume_structure_sections(ingested_struct)
                    }
                    arts["base_resume"] = filter_base_resume_to_structure(
                        arts["base_resume"], section_ids
                    )
                    base_resume_in_save = True
                pilot_body = None
                if base_resume_in_save:
                    # Operative write — do not library-merge the pilot body.
                    pilot_body = arts.pop("base_resume", None)
                # AST-1679: catalog owns resume_structure — pop after normalize/ingest for operative save.
                if "resume_structure" in arts and isinstance(arts["resume_structure"], dict):
                    resume_structure_body = arts.pop("resume_structure")
                if not arts:
                    body.pop("artifacts", None)
                else:
                    rubric_keys_to_clear = [
                        k for k in arts if k in RUBRIC_CRITERIA_ARTIFACT_KEYS
                    ]
                    submitted_rubric = copy.deepcopy(
                        {k: arts[k] for k in rubric_keys_to_clear}
                    )
                    normalize_rubric_artifacts_on_save(arts)
                    apply_rubric_vectors_save(candidate_id, arts)
            contact = body.get("contact")
            if isinstance(contact, dict) and "cover_letter_signature_image" in contact:
                _validate_cover_letter_signature_image(contact.get("cover_letter_signature_image"))
            if body:
                # AST-1014 / AC8: gate library-write found/recorded lines on deploy debug.
                save_candidate_data(candidate_id, body, replace=False, debug=ui_llm_debug())
                # Clear pending only after persist — keys captured before apply del
                for craft_task_key, artifact_key in CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY.items():
                    if artifact_key in rubric_keys_to_clear:
                        _clear_pending_craft_generation(candidate_id, craft_task_key)
            # Leaf-only PUT may leave body empty after pop — still operative-save.
            # AST-1576 / AST-1679: pilot body outside nested if body: (leaf-only base_resume
            # pops artifacts then empties body; must still land candidate.artifacts.base_resume).
            if base_resume_in_save and pilot_body is not None:
                save_candidate_data(
                    candidate_id,
                    TASK_CONFIG["craft_resume_base"]["artifact_key"],
                    pilot_body,
                )
            if strengths_body is not None:
                save_candidate_data(
                    candidate_id,
                    "candidate.context.strengths",
                    strengths_body,
                )
                strengths_saved = True
            if priorities_body is not None:
                save_candidate_data(
                    candidate_id,
                    "candidate.context.priorities",
                    priorities_body,
                )
                priorities_saved = True
            if deal_breakers_body is not None:
                save_candidate_data(
                    candidate_id,
                    "candidate.context.deal_breakers",
                    deal_breakers_body,
                )
                deal_breakers_saved = True
            if bio_summary_body is not None:
                save_candidate_data(
                    candidate_id,
                    "candidate.context.bio_summary",
                    bio_summary_body,
                )
                bio_summary_saved = True
            if ideal_day_body is not None:
                save_candidate_data(
                    candidate_id,
                    "candidate.context.ideal_day",
                    ideal_day_body,
                )
                ideal_day_saved = True
            if backstory_body is not None:
                save_candidate_data(
                    candidate_id,
                    "candidate.context.backstory",
                    backstory_body,
                )
                backstory_saved = True
            if writing_preferences_body is not None:
                save_candidate_data(
                    candidate_id,
                    "candidate.context.writing_preferences",
                    writing_preferences_body,
                )
                writing_preferences_saved = True
            if resume_structure_body is not None:
                save_candidate_data(
                    candidate_id,
                    "candidate.artifacts.resume_structure",
                    resume_structure_body,
                )
                resume_structure_saved = True
        # AST-1287 / AST-1288: illegal hops return code=illegal_candidate_transition
        # with from_state/to_state; admin retry with confirm_state_override=true forces.
        # Same-state in the PUT body is skipped here (not a core no-op).
        if state_override is not None:
            current = get_candidate(candidate_id)
            if state_override != (current or {}).get("state"):
                try:
                    transition_candidate_state(
                        candidate_id,
                        state_override,
                        force=(confirm_override is True),
                    )
                except IllegalCandidateTransition as e:
                    return jsonify({
                        "error": str(e),
                        "code": "illegal_candidate_transition",
                        "from_state": e.from_state,
                        "to_state": e.to_state,
                    }), 400
                except ValueError as e:
                    return jsonify({"error": str(e)}), 400
        # Edits land in the candidate's api_keys array; the data layer encrypts (AST-1901).
        if api_keys:
            update_candidate_api_keys(candidate_id, [{"server": e["server"], "key": e["key"].strip()} for e in api_keys])
    except Exception as e:
        # Failed Save: keep submitted criteria recoverable via GET …/pending
        logger.exception(
            "%s | api update_candidate_data failed %s: %s — returning 400",
            candidate_id,
            type(e).__name__,
            e,
        )
        for craft_task_key, artifact_key in CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY.items():
            val = submitted_rubric.get(artifact_key)
            if isinstance(val, list) and val:
                _stash_pending_craft_generation(
                    candidate_id,
                    craft_task_key,
                    None,
                    {"criteria": val},
                )
        return jsonify({"error": str(e)}), 400
    if strengths_saved or priorities_saved or deal_breakers_saved or bio_summary_saved:
        logger.info(
            "%s | api %s completed: PUT %s",
            candidate_id,
            f"/api/candidates/{candidate_id}/data",
            200,
        )
    if ideal_day_saved:
        logger.info(
            "%s | api %s completed: PUT %s",
            candidate_id,
            f"/api/candidates/{candidate_id}/data",
            200,
        )
    if backstory_saved:
        logger.info(
            "%s | api %s completed: PUT %s",
            candidate_id,
            f"/api/candidates/{candidate_id}/data",
            200,
        )
    if writing_preferences_saved:
        logger.info(
            "%s | api %s completed: PUT %s",
            candidate_id,
            f"/api/candidates/{candidate_id}/data",
            200,
        )
    if resume_structure_saved:
        logger.info(
            "%s | api %s completed: PUT %s",
            candidate_id,
            f"/api/candidates/{candidate_id}/data",
            200,
        )
    # stat.logging.info.api: a keys-only save still completed work — one line, not doubled when an artifact line fired.
    if api_keys and not (
        strengths_saved or priorities_saved or deal_breakers_saved or bio_summary_saved
        or ideal_day_saved or backstory_saved or writing_preferences_saved or resume_structure_saved
    ):
        logger.info(
            "%s | api %s completed: PUT %s",
            candidate_id,
            f"/api/candidates/{candidate_id}/data",
            200,
        )
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
@require_admin
def delete_candidate(candidate_id):
    try:
        core_delete_candidate(candidate_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"deleted": candidate_id})


@candidate_bp.route("/<candidate_id>/generate_artifacts", methods=["POST"])
@require_auth
def generate_artifacts(candidate_id):
    """Handoff to REQUESTED_ARTIFACTS for the craft daisy chain (AST-1253)."""
    candidate = get_candidate(candidate_id)
    if not candidate:
        return jsonify({"error": f"Candidate not found: {candidate_id}"}), 404
    try:
        state = start_requested_artifacts(candidate_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 409
    return jsonify({"ok": True, "state": state})


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
        live = (cd.get("context") or {}).get("raw_resume", "")

    body, status = run_candidate_artifact_generation(
        candidate_id, task_key, live, debug=ui_llm_debug()
    )
    return jsonify(body), status


@candidate_bp.route("/<candidate_id>/generate/<task_key>/pending", methods=["GET"])
@require_auth
def get_pending_artifact_generation(candidate_id, task_key):
    """Recover a completed craft_*_rubric generate the browser missed (AST-901)."""
    body, status = get_pending_craft_generation(candidate_id, task_key)
    return jsonify(body), status
