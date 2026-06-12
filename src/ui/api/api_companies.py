"""API endpoints for Companies screens: list, detail, bulk state, import, scan history."""

from flask import Blueprint, jsonify, request

from ui.auth import require_auth
from src.core.roster import (
    count_companies,
    get_active_trigger_states,
    get_company,
    get_company_job_state_counts,
    get_entity_agent_story,
    list_companies,
    list_company_job_scans,
    save_company,
    update_company,
)

companies_bp = Blueprint("companies", __name__, url_prefix="/api/companies")


def _flatten_for_view(company: dict) -> dict:
    """Lift prefilter_company_notes from company_data to top-level for column display."""
    cd = company.get("company_data") or {}
    company["prefilter_company_notes"] = cd.get("prefilter_company_notes", "")
    return company


@companies_bp.route("")
@require_auth
def list_view():
    """List companies filtered by view logic.

    Query params:
      view: watch_list | new_list | inactive_list | ignored
      candidate_id: scope to one candidate
    """
    view = request.args.get("view", "watch_list")
    candidate_id = request.args.get("candidate_id")

    if view == "watch_list":
        rows = list_companies(states=["WATCH"], candidate_id=candidate_id)
    elif view == "new_list":
        active = get_active_trigger_states(candidate_id, "company") if candidate_id else []
        pipeline_states = [s for s in active if s not in ("WATCH", "IGNORE")]
        rows = list_companies(states=pipeline_states, candidate_id=candidate_id) if pipeline_states else []
    elif view == "inactive_list":
        active = get_active_trigger_states(candidate_id, "company") if candidate_id else []
        exclude = list(set(active) | {"IGNORE"})
        rows = list_companies(exclude_states=exclude, candidate_id=candidate_id)
    elif view == "ignored":
        rows = list_companies(states=["IGNORE"], candidate_id=candidate_id)
    else:
        rows = list_companies(candidate_id=candidate_id)

    return jsonify([_flatten_for_view(r) for r in rows])


# --- Named GET routes must come before /<short_name> to avoid Flask swallowing them ---

@companies_bp.route("/scan_history")
@require_auth
def scan_history():
    """Gazer scan report from company_job_scan table."""
    candidate_id = request.args.get("candidate_id")
    rows = list_company_job_scans(candidate_id=candidate_id)
    return jsonify(rows)


@companies_bp.route("/counts")
@require_auth
def counts():
    """Return counts per view for nav badges."""
    candidate_id = request.args.get("candidate_id")
    active = get_active_trigger_states(candidate_id, "company") if candidate_id else []

    pipeline_states = [s for s in active if s not in ("WATCH", "IGNORE")]
    exclude = list(set(active) | {"IGNORE"})

    return jsonify({
        "/companies/watch_list": count_companies(states=["WATCH"], candidate_id=candidate_id),
        "/companies/new_list": count_companies(states=pipeline_states, candidate_id=candidate_id) if pipeline_states else 0,
        "/companies/inactive_list": count_companies(exclude_states=exclude, candidate_id=candidate_id),
        "/companies/ignored": count_companies(states=["IGNORE"], candidate_id=candidate_id),
        "/companies/watch_history": len(list_company_job_scans(candidate_id=candidate_id)),
    })


@companies_bp.route("/<short_name>")
@require_auth
def detail(short_name):
    company = get_company(short_name)
    if not company:
        return jsonify({"error": "Not found"}), 404
    company = _flatten_for_view(company)
    company["job_state_counts"] = get_company_job_state_counts(short_name)
    company["agent_story"] = get_entity_agent_story(company)
    return jsonify(company)


@companies_bp.route("/<short_name>", methods=["PUT"])
@require_auth
def edit(short_name):
    """Update editable company fields. Blocked when state is WATCH."""
    company = get_company(short_name)
    if not company:
        return jsonify({"error": "Not found"}), 404
    if company.get("state") == "WATCH":
        return jsonify({"error": "Cannot edit a company in WATCH state"}), 400
    data = request.get_json(force=True)
    allowed = {"company_name", "company_website", "job_site"}
    fields = {k: v for k, v in data.items() if k in allowed}
    if not fields:
        return jsonify({"error": "No valid fields to update"}), 400
    update_company(short_name, **fields)
    return jsonify({"ok": True})


@companies_bp.route("/bulk_state", methods=["POST"])
@require_auth
def bulk_state():
    """Set state for multiple companies. Body: {short_names: [...], to_state: "..."}"""
    data = request.get_json(force=True)
    short_names = data.get("short_names", [])
    to_state = data.get("to_state", "")
    if not short_names or not to_state:
        return jsonify({"error": "short_names and to_state required"}), 400
    updated = 0
    for sn in short_names:
        updated += update_company(sn, state=to_state)
    return jsonify({"updated": updated})


@companies_bp.route("/import", methods=["POST"])
@require_auth
def import_companies():
    """Import companies from CSV rows. Body: {rows: [{short_name, company_name, company_website}], candidate_id: "..."}"""
    data = request.get_json(force=True)
    rows = data.get("rows", [])
    candidate_id = data.get("candidate_id")
    if not rows:
        return jsonify({"error": "No rows to import"}), 400
    created = 0
    for row in rows:
        sn = (row.get("short_name") or "").strip()
        if not sn:
            continue
        save_company(
            short_name=sn,
            state="WEBSITE_FOUND",
            company_name=(row.get("company_name") or "").strip() or None,
            company_website=(row.get("company_website") or "").strip() or None,
        )
        if candidate_id:
            update_company(sn, candidate_id=candidate_id)
        created += 1
    return jsonify({"created": created}), 201
