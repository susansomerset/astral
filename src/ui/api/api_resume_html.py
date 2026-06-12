"""AST-298: authenticated HTML resume routes for print/PDF."""

from flask import Blueprint, Response, jsonify, request

from ui.auth import require_auth
from src.core.builder import build_base_resume, build_cover_letter, build_resume

resume_html_bp = Blueprint("resume_html", __name__, url_prefix="/candidate")


@resume_html_bp.route("/resume/base")
@require_auth
def resume_base():
    candidate_id = (request.args.get("candidate_id") or "").strip()
    if not candidate_id:
        return jsonify({"error": "candidate_id query parameter is required"}), 400
    try:
        html = build_base_resume(candidate_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404
    return Response(html, mimetype="text/html; charset=utf-8")


@resume_html_bp.route("/resume/<job_id>")
@require_auth
def resume_for_job(job_id: str):
    try:
        html = build_resume(job_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404
    return Response(html, mimetype="text/html; charset=utf-8")


@resume_html_bp.route("/cover/<job_id>")
@require_auth
def cover_for_job(job_id: str):
    try:
        html = build_cover_letter(job_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404
    return Response(html, mimetype="text/html; charset=utf-8")
