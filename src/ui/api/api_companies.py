"""API endpoints for Companies screens: list, detail, bulk state, import, scan history."""

from flask import Blueprint, jsonify, request

from ui.auth import require_auth
from src.core.agent import get_entity_agent_story
from src.core.roster import (
    add_company_for_test_watch,
    count_companies,
    enrich_watch_list_company,
    get_active_trigger_states,
    get_companies_job_state_stats,
    get_companies_scan_counts,
    get_company,
    get_company_job_state_counts,
    list_companies,
    list_company_job_scans,
    list_company_jobs_for_bucket,
    save_company,
    transition_company_state,
    update_company,
)
from src.utils.config import ASTRAL_CONFIG, METEORITE_CONFIG, WATCH_LIST_JOB_BUCKETS
from src.utils.logging import get_logger
from ui.api.api_jobs import _flatten_grades

companies_bp = Blueprint("companies", __name__, url_prefix="/api/companies")
logger = get_logger(__name__)

# Match api_jobs list payloads — drop bulky blobs from bucket job lists (AST-2320).
_WATCH_JOB_LIST_DROP_KEYS = ("job_data", "state_history")


def _flatten_for_view(company: dict) -> dict:
    """Lift prefilter_company_notes and company_upshot from company_data to top-level for display."""
    cd = company.get("company_data") or {}
    company["prefilter_company_notes"] = cd.get("prefilter_company_notes", "")
    company["company_upshot"] = cd.get("company_upshot", "")
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
        short_names = [r["short_name"] for r in rows if r.get("short_name")]
        stats_by_company = get_companies_job_state_stats(short_names)
        scan_by_company = get_companies_scan_counts(short_names)
        enriched = []
        for r in rows:
            sn = r.get("short_name")
            enrich_watch_list_company(
                r,
                stats_by_company.get(sn, {}) if sn else {},
                scan_by_company.get(sn, 0) if sn else 0,
            )
            enriched.append(_flatten_for_view(r))
        return jsonify(enriched)
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
    elif view == "meteorite_list":
        rows = list_companies(
            states=[METEORITE_CONFIG["company_state"]],
            candidate_id=candidate_id,
        )
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
        "/companies/meteorite_list": count_companies(
            states=[METEORITE_CONFIG["company_state"]],
            candidate_id=candidate_id,
        ),
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


@companies_bp.route("/<short_name>/jobs")
@require_auth
def company_jobs_by_bucket(short_name):
    """Jobs for one company filtered to a Watch List count bucket (AST-2320).

    bucket=all returns every job for the company (no state IN filter) with grades
    flattened like jobs list slim rows (AST-2326).
    """
    bucket = (request.args.get("bucket") or "").strip()
    candidate_id = (request.args.get("candidate_id") or "").strip()
    if bucket != "all" and bucket not in WATCH_LIST_JOB_BUCKETS:
        return jsonify({"error": "invalid bucket"}), 400
    if not candidate_id:
        return jsonify({"error": "candidate_id required"}), 400
    if not get_company(short_name):
        return jsonify({"error": "Not found"}), 404
    states = None if bucket == "all" else list(WATCH_LIST_JOB_BUCKETS[bucket]["states"])
    rows = list_company_jobs_for_bucket(short_name, states, candidate_id=candidate_id)
    slim = []
    for job in rows:
        row = _flatten_grades(dict(job))
        for key in _WATCH_JOB_LIST_DROP_KEYS:
            row.pop(key, None)
        slim.append(row)
    return jsonify(slim)


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
    transitions = ASTRAL_CONFIG["company_state_transitions"]
    # Validate every found row before any write (no partial apply on illegal pair).
    to_apply = []
    for sn in short_names:
        company = get_company(sn)
        if not company:
            continue
        from_state = str(company.get("state") or "")
        if (from_state, to_state) not in transitions:
            return jsonify({"error": f"transition not allowed: {from_state} -> {to_state}"}), 400
        to_apply.append(sn)
    updated = 0
    for sn in to_apply:
        transition_company_state(sn, to_state)
        updated += 1
    logger.info("%s | api %s completed: POST %s", "-", "/api/companies/bulk_state", 200)
    return jsonify({"updated": updated})


@companies_bp.route("/add", methods=["POST"])
@require_auth
def add_company():
    """Create candidate-owned company in TEST_WATCH. Body: name/website/job_site + candidate_id."""
    data = request.get_json(force=True) or {}
    candidate_id = (data.get("candidate_id") or "").strip()
    company_name = (data.get("company_name") or "").strip()
    company_website = (data.get("company_website") or "").strip()
    job_site = (data.get("job_site") or "").strip()
    if not candidate_id:
        return jsonify({"error": "candidate_id required"}), 400
    if not company_name:
        return jsonify({"error": "company_name required"}), 400
    if not company_website:
        return jsonify({"error": "company_website required"}), 400
    if not job_site:
        return jsonify({"error": "job_site required"}), 400
    try:
        sn = add_company_for_test_watch(
            candidate_id, company_name, company_website, job_site,
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    logger.info("%s | api %s completed: POST %s", candidate_id, "/api/companies/add", 201)
    return jsonify({"short_name": sn, "state": "TEST_WATCH"}), 201


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
