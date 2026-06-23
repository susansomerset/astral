"""Admin API endpoints: agents, tasks, timesheets, dispatch, adhoc, data management, scheduler control."""

import asyncio
import csv
import io
import re
import threading
from typing import Any, Dict, Optional

from flask import Blueprint, jsonify, request, Response, send_file

from ui.auth import require_admin, require_ip
from src.data import database
from src.data.database import (
    _get_connection,
    get_dispatch_row_or_seed_preview_meta,
    ALLOWED_CONFIG_TABLES,
    apply_config_table_upsert,
    list_vector_feedback,
    aggregate_vector_feedback_by_vector,
)

from src.core.consult import list_timesheets
from src.utils.deploy_status import ui_llm_debug
from src.utils.cost_calculator import sum_calc_cost_components
from src.core.dispatcher import (
    list_dispatch_ledger, get_dispatch_ledger, list_log_entries,
    list_dispatch_tasks, save_dispatch_task, update_dispatch_task,
    run_task, drain_task, cancel_task, cancel_all_tasks, task_status_all,
)
from src.core.candidate import preview_task_prompt
from src.core.table_copy_upsert import apply_copy_output_table_upsert
from src.utils.config import (
    ASTRAL_CONFIG,
    AGENT_CONFIG,
    DEEPSEEK_MODEL_PRICING,
    get_manage_agents_tokens,
    get_manage_tasks_chain_tokens,
    get_tokens,
    resolve_tokens,
    get_model,
    admin_brain_setting_catalog,
    brain_setting_for_anthropic_agent_key,
    TASK_CONFIG,
    JOB_STATES,
    COMPANY_STATES,
    ADMIN_CONFIG,
    admin_hidden_dispatch_task_keys,
    CHARS_PER_TOKEN,
    DISPATCH_SCHEDULABLE_TASK_KEYS,
    DISPATCH_RETIRED_TASK_KEYS,
    dispatch_task_admin_defaults,
    dispatch_task_key_is_scored,
    dispatch_task_key_retired_message,
    get_task_keys,
    dispatch_claim_uses_score_floor,
    resume_artifact_compound_state,
    resume_artifact_hop_task_keys,
    get_active_llm_provider,
    infer_brain_setting_from_legacy_model_code,
    resolve_brain_setting_to_anthropic_agent_key,
    resolve_brain_setting_to_deepseek_tier_meta,
    validate_allowed_brain_setting,
    RUBRIC_FEEDBACK_CONFIG,
    rubric_owner_task_key_choices,
)
# Direct import — AST-292-style admin helpers (`run_adhoc_workbench_test`, `_decode_payload`) plus public `resolved_task_system`
from src.core.agent import (
    run_adhoc_workbench_test,
    _decode_payload,
    resolved_agent_content,
    resolved_task_system,
    _chain_context,
)
from scripts.migrations.backfill_culture_links import run_backfill, EXCLUDE_STATES


def get_dispatch_task_by_key(task_key: str):
    """DB sample dispatch_task row else seed defaults (AST-485). Wrapper name retained for monkeypatch tests."""
    return get_dispatch_row_or_seed_preview_meta(task_key)


admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


# ---------------------------------------------------------------------------
# Admin Config
# ---------------------------------------------------------------------------

@admin_bp.route("/config")
@require_admin
def admin_config():
    return jsonify(ADMIN_CONFIG)


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

def _agent_admin_view(agent: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure brain_setting tier is visible for Manage Agents (AST-495); persisted column is canonical (AST-492)."""
    if not agent:
        return agent
    d = dict(agent)
    bs = (d.get("brain_setting") or "").strip()
    if bs:
        d["brain_setting"] = bs
        return d
    mk = d.get("model_code")
    inferred = infer_brain_setting_from_legacy_model_code(mk if isinstance(mk, str) else None)
    tier_from_key = brain_setting_for_anthropic_agent_key(mk if isinstance(mk, str) else None)
    d["brain_setting"] = tier_from_key or inferred
    return d


@admin_bp.route("/agents")
@require_admin
def list_agents():
    return jsonify([_agent_admin_view(dict(a)) for a in database.list_agents()])


@admin_bp.route("/agents/ids")
@require_admin
def list_agent_ids():
    return jsonify([a["agent_id"] for a in database.list_agents()])


@admin_bp.route("/agents/brain_settings")
@require_admin
def list_brain_settings():
    """Config-backed tier catalog for Manage Agents (AST-495)."""
    return jsonify(admin_brain_setting_catalog())


def _resolve_agent_preview_candidate(candidate_id: str):
    """Candidate row + candidate_data for agent preview (mirrors preview_task_prompt fallback)."""
    if candidate_id:
        candidate = database.get_candidate(candidate_id)
        if not candidate:
            raise ValueError(f"Candidate not found: {candidate_id}")
    else:
        candidates = database.list_candidates()
        if not candidates:
            raise ValueError("No active candidate found for preview.")
        candidate = candidates[0]
    cd = candidate.get("candidate_data") or {}
    cid = candidate.get("astral_candidate_id") or candidate_id
    return cid, cd


@admin_bp.route("/agents/meta/tokens")
@require_admin
def agent_tokens():
    """Manage Agents picker: all registry tokens except chain/hop (AST-632)."""
    return jsonify(get_manage_agents_tokens())


@admin_bp.route("/agents/preview", methods=["POST"])
@require_admin
def preview_agent():
    body = request.get_json(silent=True) or {}
    content = body.get("content")
    if content is None:
        return jsonify({"error": "content is required"}), 400
    candidate_id = (body.get("candidate_id") or "").strip()
    try:
        cid, cd = _resolve_agent_preview_candidate(candidate_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    agent_row = {"content": content}
    resolved = resolved_agent_content(agent_row, cd, "manage_agents_preview", None)
    return jsonify({"candidate_id": cid, "content": resolved})


@admin_bp.route("/agents/models")
@require_admin
def list_models():
    return jsonify([{"model_code": code, **info} for code, info in AGENT_CONFIG.items()])


@admin_bp.route("/agents/<agent_id>")
@require_admin
def get_agent(agent_id):
    agent = database.get_agent(agent_id)
    if not agent:
        return jsonify({"error": f"Agent not found: {agent_id}"}), 404
    return jsonify(_agent_admin_view(dict(agent)))


@admin_bp.route("/agents", methods=["POST"])
@require_admin
def create_agent():
    body = request.get_json(silent=True) or {}
    agent_id = (body.get("agent_id") or "").strip()
    content = body.get("content", "")
    brain_setting = (body.get("brain_setting") or "").strip() or None
    legacy_model_code = (body.get("model_code") or "").strip() or None
    temperature = body.get("temperature")
    max_tokens = body.get("max_tokens")

    if not agent_id:
        return jsonify({"error": "agent_id is required"}), 400
    if brain_setting and legacy_model_code:
        return jsonify({"error": "Specify either brain_setting or model_code, not both"}), 400
    if brain_setting:
        try:
            validate_allowed_brain_setting(brain_setting)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
    elif legacy_model_code:
        if legacy_model_code not in AGENT_CONFIG:
            return jsonify({"error": f"Unknown model_code: {legacy_model_code}"}), 400
        brain_setting = infer_brain_setting_from_legacy_model_code(legacy_model_code)
    else:
        return jsonify({"error": "brain_setting or a known model_code is required"}), 400
    if database.get_agent(agent_id):
        return jsonify({"error": f"Agent '{agent_id}' already exists"}), 409
    database.save_agent(
        agent_id, content, brain_setting=brain_setting, temperature=temperature, max_tokens=max_tokens
    )
    return jsonify({"created": agent_id}), 201


@admin_bp.route("/agents/<agent_id>", methods=["PUT"])
@require_admin
def update_agent(agent_id):
    body = request.get_json(silent=True) or {}
    if not database.get_agent(agent_id):
        return jsonify({"error": f"Agent not found: {agent_id}"}), 404

    bs_raw = body.get("brain_setting")
    mc_raw = body.get("model_code")
    has_bs_val = bs_raw not in (None, "") and str(bs_raw).strip() != ""
    has_mc_val = mc_raw not in (None, "") and str(mc_raw).strip() != ""
    if has_bs_val and has_mc_val:
        return jsonify({"error": "Specify either brain_setting or model_code, not both"}), 400

    if "brain_setting" in body and body["brain_setting"] not in (None, ""):
        try:
            validate_allowed_brain_setting(str(body["brain_setting"]).strip())
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
    if "model_code" in body and "brain_setting" not in body:
        legacy = (body.get("model_code") or "").strip()
        if legacy and legacy not in AGENT_CONFIG:
            return jsonify({"error": f"Unknown model_code: {legacy}"}), 400
        if legacy:
            body = {**body, "brain_setting": infer_brain_setting_from_legacy_model_code(legacy)}
            body.pop("model_code", None)
    kwargs = {k: body[k] for k in ("content", "brain_setting", "temperature", "max_tokens") if k in body}
    if not kwargs:
        return jsonify({"error": "No updatable fields provided"}), 400
    database.update_agent(agent_id, **kwargs)
    row = database.get_agent(agent_id)
    return jsonify(_agent_admin_view(dict(row)) if row else {})


@admin_bp.route("/agents/<agent_id>", methods=["DELETE"])
@require_admin
def delete_agent(agent_id):
    if not database.get_agent(agent_id):
        return jsonify({"error": f"Agent not found: {agent_id}"}), 404
    task_count = database.count_agent_task_refs(agent_id)
    if task_count > 0:
        return jsonify({"error": f"Agent '{agent_id}' is assigned to {task_count} task(s) — unassign first"}), 409
    database.delete_agent(agent_id)
    return jsonify({"deleted": agent_id})


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

def _grouping_from_agent_task_row(task: dict | None, task_key: str) -> dict:
    """DB grouping metadata for Manage Tasks UI."""
    if not task:
        return {
            "task_group_order": "",
            "task_group_name": "",
            "task_seq": 999.0,
            "task_name": task_key,
        }
    gn = (task.get("task_group_name") or "").strip()
    gs = float(task.get("task_seq") if task.get("task_seq") is not None else 999.0)
    return {
        "task_group_order": task.get("task_group_order") or "",
        "task_group_name": gn,
        "task_seq": gs,
        "task_name": (task.get("task_name") or "").strip() or task_key,
    }


def _enrich_tasks(candidate_id: str) -> list:
    """Assemble enriched task rows for the task manager screen.
    Resolves token counts against candidate_data, computes cache threshold status,
    and fetches timesheet averages per task version."""
    tasks = database.list_candidate_tasks()
    candidate = database.get_candidate(candidate_id) if candidate_id else None
    cd = (candidate.get("candidate_data") or {}) if candidate else {}

    conn = _get_connection()
    try:
        rows = []
        for t in tasks:
            task_key = t.get("task_key", "")
            task_key_uuid = t.get("task_key_uuid")
            agent_id = t.get("agent_id") or ""
            cfg = TASK_CONFIG.get(task_key, {})

            # Agent tiers + resolved SKU for cache threshold math (Anthropic vs DeepSeek catalog).
            full_task = database.get_agent_task(task_key) if task_key else None
            agent = database.get_agent(agent_id) if agent_id else None
            brain_setting_eff = ""
            resolved_model_key = ""
            model_cfg: Dict = {}
            _cc = _chain_context(agent, cd, task_key, None) if agent else None
            if agent:
                brain_setting_eff = (agent.get("brain_setting") or "").strip()
                if not brain_setting_eff:
                    brain_setting_eff = infer_brain_setting_from_legacy_model_code(agent.get("model_code"))
                prov_l = get_active_llm_provider()
                if prov_l == "anthropic":
                    resolved_model_key = resolve_brain_setting_to_anthropic_agent_key(brain_setting_eff)
                    model_cfg = AGENT_CONFIG.get(resolved_model_key, {})
                elif prov_l == "deepseek":
                    vm = resolve_brain_setting_to_deepseek_tier_meta(brain_setting_eff)["vendor_model"]
                    resolved_model_key = vm
                    model_cfg = DEEPSEEK_MODEL_PRICING.get(vm, {})
            if full_task and agent:
                system_content = resolved_task_system(agent, full_task, cd, task_key, _cc)
            elif agent:
                system_content = resolve_tokens(agent.get("content") or "", cd, task_key, _cc)
            else:
                system_content = ""
            system_tokens = len(system_content) // CHARS_PER_TOKEN

            # Prompt field token estimates (from DB char lengths + candidate resolution)
            len_a = int(t.get("cache_prompt_len") or 0)
            len_b = int(t.get("cache_prompt_b_len") or 0)
            len_c = int(t.get("cache_prompt_c_len") or 0)
            len_d = int(t.get("cache_prompt_d_len") or 0)
            cache_raw_total = len_a + len_b + len_c + len_d
            nocache_raw = t.get("nocache_prompt_len") or 0
            base_cache_tokens = cache_raw_total // CHARS_PER_TOKEN
            nocache_prompt_tokens = nocache_raw // CHARS_PER_TOKEN

            # Parsed cache — resolve tokens per block A–D, probe concatenation (separator not stored)
            cache_probe_parts = []
            if full_task and agent_id:
                for ck in ("cache_prompt", "cache_prompt_b", "cache_prompt_c", "cache_prompt_d"):
                    txt = resolve_tokens(full_task.get(ck) or "", cd, task_key, _cc)
                    cache_probe_parts.append(txt)
                combined_cache_probe = "\n---\n".join(cache_probe_parts)
            else:
                combined_cache_probe = ""
            task_ready = not bool(re.search(r"\{\$[^}]+\}", combined_cache_probe))
            # When tokens unresolved: parsed_cache_tokens None; approximate total_cache below uses raw lengths.
            parsed_cache_tokens = len(combined_cache_probe) // CHARS_PER_TOKEN if task_ready else None

            # Cache threshold (model_cfg populated from tier → Anthropic or DeepSeek pricing row)
            cache_min = model_cfg.get("cache_min_tokens", 0)
            total_cache = system_tokens + (
                parsed_cache_tokens if parsed_cache_tokens is not None else base_cache_tokens
            )
            cache_satisfied = total_cache >= cache_min if cache_min else False

            # Timesheet averages for this task version
            avg_live = avg_output = None
            if task_key_uuid:
                r = conn.execute(
                    "SELECT AVG(no_cache_live_tokens) AS avg_live, AVG(total_output_tokens) AS avg_output FROM agent_timesheets WHERE task_key_uuid = ?",
                    (task_key_uuid,)
                ).fetchone()
                if r and r[0] is not None:
                    avg_live = round(r[0], 1)
                    avg_output = round(r[1], 1)

            rows.append({
                "task_key":             task_key,
                "task_key_uuid":        task_key_uuid,
                "agent_id":             agent_id,
                "run_next":             t.get("run_next") or "",
                "brain_setting":        brain_setting_eff,
                "resolved_model_key":   resolved_model_key,
                "model_code":           resolved_model_key,
                "system_prompt_tokens": system_tokens,
                "base_cache_tokens":    base_cache_tokens,
                "parsed_cache_tokens":  parsed_cache_tokens,
                "cache_min_tokens":     cache_min,
                "cache_satisfied":      cache_satisfied,
                "nocache_prompt_tokens":nocache_prompt_tokens,
                "avg_live_tokens":      avg_live,
                "avg_output_tokens":    avg_output,
                "task_ready":           task_ready,
                "updated_at":           t.get("updated_at"),
                **_grouping_from_agent_task_row(t, task_key),
            })
        return rows
    finally:
        conn.close()


@admin_bp.route("/tasks")
@require_admin
def list_tasks():
    candidate_id = request.args.get("candidate_id", "")
    return jsonify(_enrich_tasks(candidate_id))


@admin_bp.route("/tasks/meta/tokens")
@require_admin
def task_tokens():
    return jsonify(get_tokens())


@admin_bp.route("/tasks/meta/chain_tokens")
@require_admin
def task_chain_tokens():  # pragma: no cover (GET mirror; registry covered in utils/component config tests)
    """Manage Tasks chain-picker: {$CALLER_*}, SELECTED_AGENT (AST-455)."""
    return jsonify(get_manage_tasks_chain_tokens())


@admin_bp.route("/tasks/<task_key>/preview")
@require_admin
def preview_task(task_key):
    try:
        candidate_id = request.args.get("candidate_id", "")
        chain_sim = request.args.get("chain_sim", "") in ("1", "true", "yes")
        parent = (request.args.get("simulate_parent") or "").strip() or None
        simulate_parsed = request.args.get("simulate_parsed")
        pfx = "chain_ctx_"
        overrides = {
            k[len(pfx) :]: v
            for k, v in request.args.items()
            if k.startswith(pfx) and len(k) > len(pfx)
        }
        astral_job_id = (request.args.get("astral_job_id") or "").strip() or None
        result = preview_task_prompt(
            task_key,
            candidate_id,
            astral_job_id=astral_job_id,
            chain_sim_enabled=chain_sim,
            chain_simulate_parent=parent,
            chain_simulate_parsed=simulate_parsed,
            chain_overrides=overrides or None,
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify(result)


@admin_bp.route("/tasks/<task_key>")
@require_admin
def get_task(task_key):
    task = database.get_agent_task(task_key)
    if not task:
        return jsonify({"error": f"Task not found: {task_key}"}), 404
    cfg = TASK_CONFIG.get(task_key, {})
    task.update(_grouping_from_agent_task_row(task, task_key))
    task["entity_type"] = cfg.get("entity_type")
    return jsonify(task)


@admin_bp.route("/tasks/<task_key>", methods=["PUT"])
@require_admin
def update_task(task_key):
    existing = database.get_agent_task(task_key)
    if not existing:
        return jsonify({"error": f"Task not found: {task_key}"}), 404
    body = request.get_json(silent=True) or {}
    rn = body["run_next"] if "run_next" in body else None
    sp = body["system_prompt"] if "system_prompt" in body else None
    tg_order = body["task_group_order"] if "task_group_order" in body else None
    tg_name = body["task_group_name"] if "task_group_name" in body else None
    tg_seq_raw = body["task_seq"] if "task_seq" in body else None
    tg_name_label = body["task_name"] if "task_name" in body else None
    tg_seq = None
    if tg_seq_raw is not None:
        try:
            tg_seq = float(tg_seq_raw)
        except (TypeError, ValueError):
            return jsonify({"error": "task_seq must be a number"}), 400
    try:
        database.save_agent_task(
            task_key,
            agent_id=body.get("agent_id"),
            user_prompt=body.get("user_prompt"),
            cache_prompt=body.get("cache_prompt"),
            cache_prompt_b=body.get("cache_prompt_b"),
            cache_prompt_c=body.get("cache_prompt_c"),
            cache_prompt_d=body.get("cache_prompt_d"),
            nocache_prompt=body.get("nocache_prompt"),
            run_next=rn,
            system_prompt=sp,
            task_group_order=tg_order,
            task_group_name=tg_name,
            task_seq=tg_seq,
            task_name=tg_name_label,
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    saved = database.get_agent_task(task_key)
    saved.update(_grouping_from_agent_task_row(saved, task_key))
    cfg = TASK_CONFIG.get(task_key, {})
    saved["entity_type"] = cfg.get("entity_type")
    return jsonify(saved)


# ---------------------------------------------------------------------------
# Timesheets
# ---------------------------------------------------------------------------

_TIMESHEET_CSV_COLUMNS = [
    "agent_req_id", "created_at", "candidate_id", "batch_id", "task_key_uuid",
    "model_code", "batch_size",
    "cache_write_tokens", "cache_read_tokens", "no_cache_prompt_tokens", "no_cache_live_tokens",
    "total_no_cache_input_tokens", "total_output_tokens",
    "calc_cost_cache_write", "calc_cost_cache_read", "calc_cost_no_cache_input", "calc_cost_output",
    "total_cost",
    "agent_performance", "failure_note",
]

_TIMESHEET_COLUMNS = [
    {"key": "created_at",                 "label": "Date",              "type": "datetime"},
    {"key": "candidate_id",               "label": "Candidate",         "type": "str"},
    {"key": "batch_id",                   "label": "Batch",             "type": "str"},
    {"key": "task_key_uuid",              "label": "Task UUID",         "type": "str"},
    {"key": "model_code",                 "label": "Model",             "type": "str"},
    {"key": "batch_size",                 "label": "Batch Size",        "type": "int"},
    {"key": "cache_write_tokens",         "label": "Cache Write Tok",   "type": "int"},
    {"key": "cache_read_tokens",          "label": "Cache Read Tok",    "type": "int"},
    {"key": "no_cache_prompt_tokens",     "label": "NoCache Prompt",    "type": "int"},
    {"key": "no_cache_live_tokens",       "label": "NoCache Live",      "type": "int"},
    {"key": "total_no_cache_input_tokens","label": "Total Input Tok",   "type": "int"},
    {"key": "total_output_tokens",        "label": "Output Tokens",     "type": "int"},
    {"key": "calc_cost_cache_write",      "label": "Cost Cache Write",  "type": "currency"},
    {"key": "calc_cost_cache_read",       "label": "Cost Cache Read",   "type": "currency"},
    {"key": "calc_cost_no_cache_input",   "label": "Cost Input",        "type": "currency"},
    {"key": "calc_cost_output",           "label": "Cost Output",       "type": "currency"},
    {"key": "total_cost",                 "label": "Total Cost",        "type": "currency"},
    {"key": "agent_performance",          "label": "Performance",       "type": "str"},
    {"key": "failure_note",               "label": "Failure",           "type": "str"},
    {"key": "agent_req_id",               "label": "Request ID",        "type": "str"},
]


def _timesheet_filters() -> dict:
    return {
        k: request.args[k]
        for k in ("date_from", "date_to", "task_key_uuid", "batch_id", "candidate_id", "model_code", "agent_performance")
        if request.args.get(k)
    }


def _enrich_timesheet_row(row: dict) -> dict:
    out = dict(row)
    out["total_cost"] = sum_calc_cost_components(row)
    return out


@admin_bp.route("/timesheets")
@require_admin
def list_timesheets_all():
    rows = [_enrich_timesheet_row(r) for r in list_timesheets(**_timesheet_filters())]
    if request.args.get("req_dict"):
        return jsonify({"columns": _TIMESHEET_COLUMNS, "rows": rows})
    return jsonify(rows)


@admin_bp.route("/timesheets/export")
@require_admin
def export_timesheets_csv():
    rows = [_enrich_timesheet_row(r) for r in list_timesheets(**_timesheet_filters())]
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=_TIMESHEET_CSV_COLUMNS, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return Response(
        buf.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=timesheets.csv"},
    )


# ---------------------------------------------------------------------------
# Vector feedback (AST-725)
# ---------------------------------------------------------------------------

def _feedback_value_label(value: str) -> str:
    return (RUBRIC_FEEDBACK_CONFIG.get("value_labels") or {}).get(value, value)


def _feedback_type_label(feedback_type: str) -> str:
    meta = (RUBRIC_FEEDBACK_CONFIG.get("feedback_types") or {}).get(feedback_type) or {}
    return meta.get("label") or feedback_type


_VECTOR_FEEDBACK_COLUMNS = [
    {"key": "created_at", "label": "Date", "type": "datetime"},
    {"key": "candidate_id", "label": "Candidate", "type": "str"},
    {"key": "task_key", "label": "Task", "type": "str"},
    {"key": "batch_id", "label": "Batch", "type": "str"},
    {"key": "vector_code", "label": "Vector", "type": "str"},
    {"key": "vector_label", "label": "Label", "type": "str"},
    {"key": "feedback_type", "label": "Type", "type": "str"},
    {"key": "value", "label": "Value", "type": "str"},
    {"key": "value_label", "label": "Value label", "type": "str"},
    {"key": "agent_data_id", "label": "Agent data", "type": "str"},
    {"key": "vector_feedback_id", "label": "Feedback ID", "type": "str"},
]

_VECTOR_FEEDBACK_SUMMARY_COLUMNS = [
    {"key": "code", "label": "Vector", "type": "str"},
    {"key": "label", "label": "Label", "type": "str"},
    {"key": "importance", "label": "Importance", "type": "int"},
    {"key": "batch_count", "label": "Batches", "type": "int"},
    {"key": "feedback_row_count", "label": "Feedback rows", "type": "int"},
    {"key": "relevance_dist", "label": "Relevance", "type": "str"},
    {"key": "clarity_dist", "label": "Clarity", "type": "str"},
    {"key": "verdict_dist", "label": "Verdict", "type": "str"},
]


def _vector_feedback_filters() -> dict:
    keys = (
        "candidate_id", "owner_task_key", "task_key", "batch_id",
        "vector_code", "feedback_type", "value", "date_from", "date_to",
    )
    out = {k: request.args[k] for k in keys if request.args.get(k)}
    if out.get("owner_task_key"):
        out.pop("task_key", None)
    return out


def _enrich_vector_feedback_row(row: dict) -> dict:
    out = dict(row)
    out["value_label"] = _feedback_value_label(str(out.get("value") or ""))
    ft = str(out.get("feedback_type") or "")
    out["feedback_type_label"] = _feedback_type_label(ft)
    return out


@admin_bp.route("/vector_feedback")
@require_admin
def list_vector_feedback_admin():
    rows = [_enrich_vector_feedback_row(r) for r in list_vector_feedback(**_vector_feedback_filters())]
    if request.args.get("req_dict"):
        return jsonify({"columns": _VECTOR_FEEDBACK_COLUMNS, "rows": rows})
    return jsonify(rows)


@admin_bp.route("/vector_feedback/summary")
@require_admin
def list_vector_feedback_summary():
    candidate_id = request.args.get("candidate_id")
    owner_task_key = request.args.get("owner_task_key") or request.args.get("task_key")
    if not candidate_id or not owner_task_key:
        return jsonify({"error": "candidate_id and owner_task_key required"}), 400
    rows = aggregate_vector_feedback_by_vector(candidate_id, owner_task_key)
    if request.args.get("req_dict"):
        return jsonify({"columns": _VECTOR_FEEDBACK_SUMMARY_COLUMNS, "rows": rows})
    return jsonify(rows)


@admin_bp.route("/vector_feedback/task_keys")
@require_admin
def list_vector_feedback_task_keys():
    return jsonify(list(rubric_owner_task_key_choices()))


# ---------------------------------------------------------------------------
# Dispatch Ledger (Execution History)
# ---------------------------------------------------------------------------

def _ledger_filters(*keys: str) -> dict:
    return {k: request.args[k] for k in keys if request.args.get(k)}


@admin_bp.route("/dispatch_ledger")
@require_admin
def list_ledger():
    params = _ledger_filters("task_key", "candidate_id", "status", "date_from", "date_to")
    return jsonify(list_dispatch_ledger(**params))


@admin_bp.route("/dispatch_ledger/<batch_id>")
@require_admin
def get_ledger(batch_id):
    record = get_dispatch_ledger(batch_id)
    if not record:
        return jsonify({"error": f"Not found: {batch_id}"}), 404
    return jsonify(record)


@admin_bp.route("/dispatch_ledger/<batch_id>/logs")
@require_admin
def get_ledger_logs(batch_id):
    return jsonify(list_log_entries(batch_id=batch_id))


# ---------------------------------------------------------------------------
# Dispatch Tasks (Task Dispatcher config)
# ---------------------------------------------------------------------------


def _trigger_state_is_scored(trigger_state: Optional[str], _task_key: str) -> bool:
    """Whether trigger_state is a scored-step outcome; task_key kept for test/API symmetry (ignored)."""
    return dispatch_claim_uses_score_floor(trigger_state)


def _task_is_scored(task_key: str) -> bool:
    return dispatch_task_key_is_scored(task_key)


_DISPATCH_TASK_COLUMNS = [
    {"key": "task_key",       "label": "Task",        "type": "str"},
    {"key": "entity_type",    "label": "Entity",      "type": "str"},
    {"key": "trigger_state",  "label": "State",       "type": "str"},
    {"key": "score_floor",    "label": "Score >= ",   "type": "float"},
    {"key": "min_count",      "label": "Min Count",   "type": "int"},
    {"key": "batch_size",     "label": "Batch Size",  "type": "int"},
    {"key": "freq_hrs",       "label": "Freq (hrs)",  "type": "float"},
    {"key": "auto_mode",      "label": "AUTO",        "type": "str"},
    {"key": "debug",          "label": "Debug",       "type": "str"},
    {"key": "available_count","label": "Available",   "type": "int"},
    {"key": "last_run_at",    "label": "Last Run",    "type": "datetime"},
]


@admin_bp.route("/dispatch_tasks")
@require_admin
def list_dtasks():
    rows = list_dispatch_tasks()
    # Enrich each row with live available entity count
    for row in rows:
        is_scored = dispatch_claim_uses_score_floor(row.get("trigger_state"))
        row["is_scored"] = is_scored
        if not is_scored:
            row["score_floor"] = None
        elif row.get("score_floor") is None:
            row["score_floor"] = 1.0
        et = row.get("entity_type")
        ts = row.get("trigger_state")
        cid = row.get("candidate_id", "")
        row["available_count"] = database.count_eligible_for_dispatch_task(row) if et and ts and cid else 0
    hidden = admin_hidden_dispatch_task_keys()
    rows = [r for r in rows if r.get("task_key") not in hidden]
    if request.args.get("req_dict"):
        return jsonify({"columns": _DISPATCH_TASK_COLUMNS, "rows": rows})
    return jsonify(rows)


def _catalog_task_grouping_meta(catalog_key: str) -> dict:
    """Grouping fields from current agent_task row; empty defaults when missing."""
    row = database.get_agent_task(catalog_key) or {}
    seq = row.get("task_seq")
    return {
        "task_group_order": (row.get("task_group_order") or ""),
        "task_group_name": (row.get("task_group_name") or ""),
        "task_seq": float(seq) if seq is not None else None,
        "task_name": (row.get("task_name") or ""),
    }


def _dispatch_task_key_form_meta(task_key: str) -> dict:
    """Scheduled Actions form defaults: schedulable keys use dispatch_task_admin_defaults;
    grouping fields from agent_task row for the dispatch task_key (AST-736 — no alias map)."""
    catalog_key = (task_key or "").strip()
    cfg = TASK_CONFIG.get(catalog_key) or TASK_CONFIG.get(task_key) or {}
    entity_type = cfg.get("entity_type") or ""
    ts = cfg.get("trigger_state")
    trigger_state = (ts or "") if ts is not None else ""
    if task_key in DISPATCH_SCHEDULABLE_TASK_KEYS:
        derived = dispatch_task_admin_defaults(task_key)
        entity_type = derived["entity_type"]
        trigger_state = derived["trigger_state"]
    return {
        "entity_type": entity_type or "",
        "trigger_state": trigger_state,
        "is_scored": dispatch_task_key_is_scored(task_key),
        **_catalog_task_grouping_meta(catalog_key),
    }


@admin_bp.route("/dispatch_tasks/task_keys")
@require_admin
def dispatch_task_keys():
    """task_key → entity_type / trigger_state for Scheduled Actions forms.

    Every TASK_CONFIG key is selectable. Schedulable keys use config-built defaults;
    other keys inherit from TASK_CONFIG. Existing dispatch_task rows may add keys."""
    seen: dict[str, dict] = {}
    for tk in get_task_keys():
        seen[tk] = _dispatch_task_key_form_meta(tk)
    for tk in DISPATCH_SCHEDULABLE_TASK_KEYS:
        if tk not in seen:
            seen[tk] = _dispatch_task_key_form_meta(tk)
    for r in list_dispatch_tasks():
        k = r.get("task_key", "")
        if not k:
            continue
        if k in DISPATCH_RETIRED_TASK_KEYS:
            continue
        if k not in seen:
            seen[k] = {
                "entity_type": (r.get("entity_type") or "") or "",
                "trigger_state": (r.get("trigger_state") or "") or "",
                "task_group_order": "",
                "task_group_name": "",
                "task_seq": None,
                "task_name": "",
                "is_scored": dispatch_claim_uses_score_floor(r.get("trigger_state")),
            }
    hidden = admin_hidden_dispatch_task_keys()
    for tk in hidden:
        seen.pop(tk, None)
    for tk in DISPATCH_RETIRED_TASK_KEYS:
        seen.pop(tk, None)
    return jsonify(seen)


@admin_bp.route("/dispatch_tasks/state_options")
@require_admin
def dispatch_task_state_options():
    return jsonify({
        "job": list(JOB_STATES.keys()),
        "company": list(COMPANY_STATES.keys()),
    })


@admin_bp.route("/dispatch_tasks", methods=["POST"])
@require_admin
def create_dtask():
    data = request.get_json(force=True)
    required = ("candidate_id", "task_key", "trigger_state", "min_count")
    missing = [k for k in required if k not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400
    retired = dispatch_task_key_retired_message(data.get("task_key", ""))
    if retired:
        return jsonify({"error": retired}), 400
    is_scored = dispatch_claim_uses_score_floor(data.get("trigger_state"))
    raw_score_floor = data.get("score_floor", None)
    score_floor = float(raw_score_floor) if (is_scored and raw_score_floor is not None) else (1.0 if is_scored else None)
    if bool(data.get("auto_mode", False)):
        err = _candidate_dispatch_api_key_error(data.get("candidate_id"))
        if err:
            return jsonify({"error": err}), 400
    try:
        task_id = save_dispatch_task(
            candidate_id=data["candidate_id"],
            task_key=data["task_key"],
            min_count=int(data["min_count"]),
            auto_mode=bool(data.get("auto_mode", False)),
            trigger_state=data.get("trigger_state"),
            batch_size=int(data["batch_size"]) if data.get("batch_size") else None,
            freq_hrs=float(data.get("freq_hrs", 0)),
            score_floor=score_floor,
        )
    except Exception as e:
        if "UNIQUE" in str(e):
            return jsonify({
                "error": (
                    f"Dispatch row already exists for candidate '{data['candidate_id']}', "
                    f"task_key '{data['task_key']}', trigger_state '{data['trigger_state']}'"
                )
            }), 409
        return jsonify({"error": str(e)}), 500
    return jsonify({"id": task_id}), 201


def _dispatch_task_key_trigger_error(task_key: str, trigger_state: str | None) -> str | None:
    tk = (task_key or "").strip()
    if not tk:
        return "task_key is required"
    retired = dispatch_task_key_retired_message(tk)
    if retired:
        return retired
    try:
        defaults = dispatch_task_admin_defaults(tk)
    except KeyError:
        return f"Unknown or non-schedulable task_key: {tk!r}"
    ts = (trigger_state or "").strip()
    if not ts:
        return "trigger_state is required"
    et = defaults["entity_type"]
    if et == "job":
        if ts not in JOB_STATES:
            return f"task_key {tk!r} (job) is not valid for trigger_state {ts!r}"
    elif et == "company":
        if ts not in COMPANY_STATES:
            return f"task_key {tk!r} (company) is not valid for trigger_state {ts!r}"
    else:
        return f"task_key {tk!r} has unsupported entity_type {et!r}"
    if tk in resume_artifact_hop_task_keys():
        expected = resume_artifact_compound_state(tk)
        if ts != expected:
            return f"task_key {tk!r} requires trigger_state {expected!r} (got {ts!r})"
    return None


@admin_bp.route("/dispatch_tasks/<int:task_id>", methods=["PUT"])
@require_admin
def update_dtask(task_id):
    data = request.get_json(force=True)
    row = database.get_dispatch_task(task_id)
    if not row:
        return jsonify({"error": f"Dispatch task not found: {task_id}"}), 404
    if row.get("auto_mode") and (set(data.keys()) - {"auto_mode"}):
        return jsonify({"error": "Turn AUTO mode off before editing this row"}), 400
    allowed = {
        "min_count", "batch_size", "auto_mode", "debug", "skip_cache", "freq_hrs",
        "max_runs", "score_floor", "trigger_state", "task_key",
    }
    updates: Dict[str, Any] = {}
    if "task_key" in data:
        effective_trigger_state = data.get("trigger_state", row.get("trigger_state"))
        tk_err = _dispatch_task_key_trigger_error(data["task_key"], effective_trigger_state)
        if tk_err:
            return jsonify({"error": tk_err}), 400
        defaults = dispatch_task_admin_defaults((data["task_key"] or "").strip())
        updates["task_key"] = (data["task_key"] or "").strip()
        updates["entity_type"] = defaults["entity_type"]
        updates["sort_by"] = defaults["sort_by"]
        updates["batch_call_mode"] = defaults["batch_call_mode"]
    trigger_state = data.get("trigger_state", row.get("trigger_state"))
    is_scored = dispatch_claim_uses_score_floor(trigger_state)
    for k in allowed:
        if k in data and k != "task_key":
            if k in ("min_count", "batch_size", "max_runs"):
                updates[k] = int(data[k]) if data[k] is not None else None
            elif k in ("auto_mode", "debug", "skip_cache"):
                updates[k] = int(bool(data[k]))
            elif k == "freq_hrs":
                updates[k] = float(data[k])
            elif k == "trigger_state":
                updates[k] = str(data[k]) if data[k] else None
            elif k == "score_floor":  # pragma: no branch
                updates[k] = float(data[k]) if (is_scored and data[k] is not None) else (1.0 if is_scored else None)
    if not updates:
        return jsonify({"error": "No valid fields to update"}), 400
    if updates.get("auto_mode") == 1:
        cid = row.get("candidate_id")
        err = _candidate_dispatch_api_key_error(cid)
        if err:
            return jsonify({"error": err}), 400
    try:
        update_dispatch_task(task_id, **updates)
    except Exception as e:
        if "UNIQUE" in str(e):
            cid = row.get("candidate_id", "")
            tk = updates.get("task_key", row.get("task_key", ""))
            ts = updates.get("trigger_state", row.get("trigger_state", ""))
            return jsonify({
                "error": (
                    f"Dispatch row already exists for candidate '{cid}', "
                    f"task_key '{tk}', trigger_state '{ts}'"
                )
            }), 409
        return jsonify({"error": str(e)}), 500
    return jsonify({"ok": True})


# ---------------------------------------------------------------------------
# Ad-hoc Prompt Workbench
# ---------------------------------------------------------------------------

def _build_adhoc_live_content(task_key: str, entity_id: str, entity_ids: Optional[list] = None) -> str:
    """Build live_content from stored DB data for adhoc preview/test.
    entity_ids: for batch-mode tasks (qualify_job_listings), pass a list of IDs.
    entity_id: for single-entity tasks, pass one ID.
    Returns empty string if entity not found or task doesn't use live_content."""
    from src.utils.formatting import enumerate_array

    cfg = get_dispatch_task_by_key(task_key) or {}
    entity_type = cfg.get("entity_type")

    if entity_type == "company":
        company = database.get_company(entity_id)
        if not company:
            return ""
        cdata = company.get("company_data", {}) or {}
        if task_key == "prefilter":
            homepage = cdata.get("homepage_text") or cdata.get("website_content") or ""
            nav_links = cdata.get("nav_links") or []
            parts = []
            if homepage:
                parts.append(f"=== HOMEPAGE ===\n{homepage}")
            if nav_links:
                parts.append(f"=== NAV LINKS ===\n{enumerate_array('', nav_links)}")
            return "\n\n".join(parts)
        # select_job_page: same nav_links enumeration as find; live PJL assembly differs — preview-only parity (AST-485).
        if task_key in ("locate_job_page", "select_job_page"):
            nav_links = cdata.get("nav_links") or []
            return enumerate_array("", nav_links) if nav_links else ""
        if task_key == "parse_job_list":
            return cdata.get("job_page_dom") or cdata.get("job_listing_html") or ""
        if task_key == "recheck_no_openings":  # pragma: no branch
            return str(company.get("job_site") or cdata.get("job_site") or "")
        # gaze / other company tasks
        wc = cdata.get("website_content") or ""
        if isinstance(wc, list):
            return "\n\n".join(f"=== {p.get('url','')} ===\n{p.get('content','')}" for p in wc if p.get("content"))
        return str(wc)

    if entity_type == "job":
        # batch mode: qualify_job_listings / validate_title assemble raw listings in one block
        if task_key in ("qualify_job_listings", "validate_title"):
            ids = entity_ids if entity_ids else ([entity_id] if entity_id else [])
            raw_htmls, astral_ids = [], []
            for jid in ids:
                job = database.get_job(jid)
                if job:
                    raw_listing = (job.get("job_data") or {}).get("raw_job_listing", "")
                    if task_key == "qualify_job_listings":
                        # Match the real assemble() in consult.py — include job_site from company
                        company = database.get_company(job.get("company", ""))
                        job_site = (company or {}).get("job_site", "") or ""
                        raw_htmls.append(f"job_site: {job_site}\nraw_job_listing: {raw_listing}")
                    else:
                        raw_htmls.append(raw_listing)
                    astral_ids.append(jid)
            return (
                "JOB LISTINGS:\n" + "\n".join(f"{i:03d}: {item}" for i, item in enumerate(raw_htmls))
            ) if astral_ids else ""
        # single-entity tasks
        job = database.get_job(entity_id)
        if not job:
            return ""
        job_data = job.get("job_data") or {}
        # evaluate_jd, grade_do/get/like — job description + optional company context
        jd = job_data.get("job_description") or job_data.get("raw_job_listing") or ""
        content = f"[astral_job_id={entity_id}]\n{jd}" if jd else ""
        # Append company website_content for LIKE (requires_company)
        task_cfg = TASK_CONFIG.get(task_key, {})
        if task_cfg.get("requires_company"):
            company = database.get_company(job.get("company", ""))
            if company:
                wc = (company.get("data") or {}).get("website_content") or ""
                if isinstance(wc, list):
                    vibes = "\n\n".join(f"=== {p.get('url','')} ===\n{p.get('content','')}" for p in wc if p.get("content"))
                else:
                    vibes = str(wc)
                if vibes:
                    content += f"\n\n=== COMPANY CONTEXT ===\n{vibes}"
        return content

    return ""


@admin_bp.route("/adhoc/entities")
@require_admin
def adhoc_entities():
    """Return entities in the trigger state for a task_key + candidate_id."""
    task_key = request.args.get("task_key", "")
    candidate_id = request.args.get("candidate_id", "")
    cfg = get_dispatch_task_by_key(task_key)
    if not cfg:
        return jsonify({"error": f"Unknown task_key: {task_key}"}), 404

    entity_type = cfg.get("entity_type")
    trigger_state = cfg.get("trigger_state")

    if entity_type == "company":
        rows = database.list_companies(states=[trigger_state], candidate_id=candidate_id or None)
        entities = [{"id": r["short_name"], "label": r.get("company_name") or r["short_name"]} for r in rows]
    elif entity_type == "job":
        rows = database.list_jobs(states=[trigger_state], candidate_id=candidate_id or None)
        entities = [{"id": r["astral_job_id"], "label": r.get("job_title") or r["astral_job_id"]} for r in rows]
    else:
        entities = []

    return jsonify({
        "entity_type": entity_type,
        "trigger_state": trigger_state,
        "batch_mode": bool(cfg.get("batch_mode")),
        "entities": entities,
    })


def _resolve_adhoc(body):
    """Load agent, resolve tokens, return resolved prompts + model params.
    Returns (dict, error_tuple). On success error_tuple is None."""
    agent_id = (body.get("agent_id") or "").strip()
    if not agent_id:
        return None, (jsonify({"error": "agent_id is required"}), 400)

    agent = database.get_agent(agent_id)
    if not agent:
        return None, (jsonify({"error": f"Agent not found: {agent_id}"}), 404)

    brain_setting = (agent.get("brain_setting") or "").strip()
    if not brain_setting:
        brain_setting = infer_brain_setting_from_legacy_model_code(agent.get("model_code"))

    provider = get_active_llm_provider()
    tier_meta = None

    if provider == "deepseek":
        tier_meta = resolve_brain_setting_to_deepseek_tier_meta(brain_setting)
        vendor_model = tier_meta["vendor_model"]
        model_cfg = DEEPSEEK_MODEL_PRICING.get(vendor_model)
        if not model_cfg:
            return None, (jsonify({"error": f"Unknown DeepSeek vendor_model: {vendor_model!r}"}), 400)
        model_code = vendor_model
    elif provider == "anthropic":
        model_code = resolve_brain_setting_to_anthropic_agent_key(brain_setting)
        model_cfg = get_model(model_code)
    else:
        return None, (jsonify({"error": f"Unknown LLM active_provider {provider!r}"}), 400)

    temperature = agent.get("temperature") if agent.get("temperature") is not None else model_cfg["default_temperature"]
    max_tokens = agent.get("max_tokens") if agent.get("max_tokens") is not None else model_cfg["default_max_tokens"]

    candidate_id = (body.get("candidate_id") or "").strip()
    cd = {}
    candidate = None
    if candidate_id:
        candidate = database.get_candidate(candidate_id)
        if candidate:
            cd = candidate.get("candidate_data") or {}

    task_key = (body.get("task_key") or "adhoc").strip()

    # Resolve task_key_uuid for timesheet attribution (None for pure adhoc)
    agent_task_row = database.get_agent_task(task_key) if task_key != "adhoc" else None
    task_key_uuid = agent_task_row.get("task_key_uuid") if agent_task_row else None

    # Candidate API key override (only if task requires it)
    task_cfg = TASK_CONFIG.get(task_key, {})
    api_key_override = None
    if candidate_id and task_cfg.get("requires_candidate_key") and candidate:
        api_key_override = candidate.get("candidate_api_key")

    jc = None
    if task_cfg.get("entity_type") == "job":
        entity_id = (body.get("entity_id") or "").strip()
        if entity_id:
            job = database.get_job(entity_id)
            if job:
                from src.core.consult import build_job_token_context

                jc = build_job_token_context(job, cd)
    _cc = _chain_context(agent, cd, task_key, jc)
    agent_task_for_system = (
        {"system_prompt": ""} if agent_task_row is None and task_key == "adhoc" else (agent_task_row or {})
    )
    return {
        "system": resolved_task_system(agent, agent_task_for_system, cd, task_key, _cc, jc),
        "user": resolve_tokens(body.get("user_prompt", ""), cd, task_key, _cc, jc),
        "cache": resolve_tokens(body.get("cache_prompt", ""), cd, task_key, _cc, jc),
        "nocache": resolve_tokens(body.get("nocache_prompt", ""), cd, task_key, _cc, jc),
        "model_code": model_code,
        "tier_meta": tier_meta,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "candidate_id": candidate_id or None,
        "task_key_uuid": task_key_uuid,
        "api_key_override": api_key_override,
    }, None


@admin_bp.route("/adhoc/preview", methods=["POST"])
@require_admin
def adhoc_preview():
    body = request.get_json(silent=True) or {}
    resolved, err = _resolve_adhoc(body)
    if err:
        return err
    entity_id = (body.get("entity_id") or "").strip()
    entity_ids = body.get("entity_ids") or None
    task_key = (body.get("task_key") or "").strip()
    live_content = _build_adhoc_live_content(task_key, entity_id, entity_ids) if (entity_id or entity_ids) and task_key else ""
    return jsonify({
        "system": resolved["system"],
        "user": resolved["user"],
        "cache": resolved["cache"],
        "nocache": resolved["nocache"],
        "live_content": live_content,
    })


@admin_bp.route("/adhoc/test", methods=["POST"])
@require_admin
def adhoc_test():
    body = request.get_json(silent=True) or {}
    resolved, err = _resolve_adhoc(body)
    if err:
        return err

    entity_id = (body.get("entity_id") or "").strip()
    entity_ids = body.get("entity_ids") or None
    task_key = (body.get("task_key") or "").strip()
    live_content = _build_adhoc_live_content(task_key, entity_id, entity_ids) if (entity_id or entity_ids) and task_key else None

    task_cfg = TASK_CONFIG.get(task_key, {})
    task_response_format = task_cfg.get("response_format") or "text"

    try:
        result = asyncio.run(run_adhoc_workbench_test(
            workbench_task_key=task_key,
            candidate_id=resolved["candidate_id"],
            entity_id=entity_id or None,
            system_content=resolved["system"],
            user_content=resolved["user"],
            cache_content=resolved["cache"] or None,
            nocache_content=resolved["nocache"] or None,
            live_content=live_content,
            response_format=task_response_format,
            model_code=resolved["model_code"],
            tier_meta=resolved.get("tier_meta"),
            temperature=resolved["temperature"],
            max_tokens=resolved["max_tokens"],
            api_key_override=resolved["api_key_override"],
            task_key_uuid=resolved["task_key_uuid"],
            debug=ui_llm_debug(),
        ))
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

    if not result.get("success"):
        return jsonify({"success": False, "error": result.get("error", "Unknown error")}), 500

    response_text = result.get("parsed_response") or ""
    # For tasks with JSON envelope, do_task auto-extracts agent_payload into parsed_response.
    # If it's still a dict here (e.g. run_adhoc doesn't do the extraction), pull it out.
    if isinstance(response_text, dict) and "agent_payload" in response_text:
        response_text = response_text["agent_payload"] or ""
    if not isinstance(response_text, str):
        response_text = str(response_text)
    timesheet = result.get("timesheet", {})

    # Decode encoded payload if the task uses a compact encoded output_type
    hydrated = None
    output_type = TASK_CONFIG.get(task_key, {}).get("output_type", "")
    if "_encoded" in output_type and response_text:
        try:
            ids = entity_ids if entity_ids else ([entity_id] if entity_id else [])
            batch_entities = [{"astral_job_id": jid} for jid in ids]
            hydrated = _decode_payload(task_key, output_type, response_text, {"batch_entities": batch_entities})
        except Exception as e:
            hydrated = {"error": str(e)}

    return jsonify({"success": True, "response_text": response_text, "hydrated": hydrated, "timesheet": timesheet})


# ---------------------------------------------------------------------------
# Data Management (ad-hoc SQL)
# ---------------------------------------------------------------------------

_SQLITE_TYPE_MAP = {
    "INTEGER": "int", "INT": "int",
    "REAL": "float", "FLOAT": "float", "DOUBLE": "float", "NUMERIC": "float",
    "TEXT": "str", "VARCHAR": "str", "CHAR": "str", "BLOB": "str",
}
# Column name suffix overrides (sqlite3 cursor.description doesn't expose declared type)
_COL_NAME_TYPE = [
    ("_at",   "datetime"),
    ("_cost", "currency"),
    ("_id",   "str"),
]

def _infer_col_type(col_name: str) -> str:
    for suffix, t in _COL_NAME_TYPE:
        if col_name.endswith(suffix):
            return t
    return "str"


def _decode_blob_values(row: dict) -> dict:
    """Decompress any zlib-compressed BLOB values so they're JSON-serializable."""
    import zlib
    for k, v in row.items():
        if isinstance(v, bytes):
            try:
                row[k] = zlib.decompress(v).decode("utf-8")
            except (zlib.error, UnicodeDecodeError):
                row[k] = f"<binary {len(v)} bytes>"
    return row


@admin_bp.route("/data/sql", methods=["POST"])
@require_admin
def run_sql():
    body = request.get_json(silent=True) or {}
    sql = (body.get("sql") or "").strip()
    if not sql:
        return jsonify({"error": "No SQL provided"}), 400

    conn = _get_connection()
    try:
        cursor = conn.execute(sql)
        if cursor.description:
            col_names = [d[0] for d in cursor.description]
            rows = [_decode_blob_values(dict(zip(col_names, row))) for row in cursor.fetchall()]
            if body.get("req_dict"):
                columns = [
                    {"key": name, "label": name.replace("_", " ").title(),
                     "type": _infer_col_type(name)}
                    for name in col_names
                ]
                return jsonify({"type": "select", "columns": columns, "rows": rows, "count": len(rows)})
            return jsonify({"type": "select", "columns": col_names, "rows": rows, "count": len(rows)})
        conn.commit()
        return jsonify({"type": "execute", "rows_affected": cursor.rowcount})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()


@admin_bp.route("/data/table_copy_upsert", methods=["POST"])
@require_admin
def admin_table_copy_upsert():
    """Paste Copy Output JSON rows → transactional upsert (generic PK or agent_task semantics)."""
    body = request.get_json(silent=True) or {}
    table = (body.get("table") or "").strip()
    json_payload = body.get("json_payload")

    if not table:
        return jsonify({"ok": False, "error": "table is required"}), 400
    if json_payload is None:
        return jsonify({"ok": False, "error": "json_payload is required"}), 400
    if not isinstance(json_payload, str):
        return jsonify({
            "ok": False,
            "error": "json_payload must be a JSON text string — paste Copy Output verbatim",
        }), 400

    try:
        result = apply_copy_output_table_upsert(table_name=table, json_payload=json_payload)
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

    if result.get("ok") is False:
        return jsonify(result), 400
    return jsonify(result)


@admin_bp.route("/data/upsert_config_table", methods=["POST"])
@require_admin
def upsert_config_table():
    """Apply config-table upsert payload (used by scripts/push_tables_to_prod.py)."""
    body = request.get_json(silent=True) or {}
    table = (body.get("table") or "").strip()
    columns = body.get("columns")
    rows = body.get("rows")

    if not table or table not in ALLOWED_CONFIG_TABLES:
        return jsonify({"error": f"Invalid or disallowed table (allowed: {sorted(ALLOWED_CONFIG_TABLES)})"}), 400
    if not isinstance(columns, list) or not columns or not all(isinstance(c, str) for c in columns):
        return jsonify({"error": "columns must be a non-empty list of strings"}), 400
    if not isinstance(rows, list):
        return jsonify({"error": "rows must be a list"}), 400

    conn = _get_connection()
    try:
        result = apply_config_table_upsert(conn, table, columns, rows)
        conn.commit()
        return jsonify(result)
    except ValueError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Scheduler / per-task thread control
# ---------------------------------------------------------------------------

def _candidate_dispatch_api_key_error(candidate_id: Optional[str]) -> Optional[str]:
    """If set, return a user-facing message; dispatch Run/Auto need a real Anthropic key on the candidate."""
    if not candidate_id:
        return "This dispatch task has no candidate; set one before Run or Auto."
    cand = database.get_candidate(candidate_id)
    if not cand:
        return f"Candidate not found: {candidate_id}"
    key = cand.get("candidate_api_key")
    if not key or not str(key).strip():
        return "Set this candidate's Anthropic API key before using Run or Auto on dispatch tasks."
    return None


@admin_bp.route("/dispatch_tasks/<int:task_id>/run", methods=["POST"])
@require_admin
def run_dtask(task_id):
    row = database.get_dispatch_task(task_id)
    if not row:
        return jsonify({"error": "Dispatch task not found", "started": False}), 404
    err = _candidate_dispatch_api_key_error(row.get("candidate_id"))
    if err:
        return jsonify({"error": err, "started": False}), 400
    started = run_task(task_id, ui_initiated=True)
    return jsonify({"started": started})


@admin_bp.route("/dispatch_tasks/<int:task_id>/stop", methods=["POST"])
@require_admin
def stop_dtask(task_id):
    """Graceful stop — finishes current batch then exits."""
    result = drain_task(task_id)
    return jsonify(result)


@admin_bp.route("/dispatch_tasks/<int:task_id>/kill", methods=["POST"])
@require_admin
def kill_dtask(task_id):
    """Immediate kill — cancels mid-batch."""
    result = cancel_task(task_id)
    return jsonify(result)


@admin_bp.route("/scheduler/thread_status")
@require_admin
def scheduler_thread_status():
    hidden = admin_hidden_dispatch_task_keys()
    status = task_status_all()
    filtered = {k: v for k, v in status.items() if v.get("task_key") not in hidden}
    return jsonify(filtered)


@admin_bp.route("/scheduler/stop_all", methods=["POST"])
@require_admin
def scheduler_stop_all():
    killed = cancel_all_tasks()
    return jsonify({"killed": killed})


# ---------------------------------------------------------------------------
# Script: backfill_culture_links
# ---------------------------------------------------------------------------

_backfill_status = {"status": "idle", "message": ""}
_backfill_thread: Optional[threading.Thread] = None


@admin_bp.route("/script/backfill_culture_links", methods=["POST"])
@require_admin
def backfill_culture_links_start():
    global _backfill_thread
    if _backfill_thread and _backfill_thread.is_alive():
        return jsonify({"error": "Backfill already running"}), 409

    data = request.get_json(force=True, silent=True) or {}
    dry_run = bool(data.get("dry_run", False))
    company = data.get("company") or None

    def _run():
        target = company or "all"
        label = f"{target} — {'dry run' if dry_run else 'run'}"
        _backfill_status.update(status="running", message=f"Backfill culture links ({label})...")
        try:
            run_backfill(dry_run=dry_run, company=company)
            _backfill_status.update(status="done", message=f"Completed ({label})")
        except Exception as e:
            _backfill_status.update(status="error", message=str(e))

    _backfill_thread = threading.Thread(target=_run, daemon=True)
    _backfill_thread.start()
    return jsonify({"started": True, "dry_run": dry_run, "company": company})


@admin_bp.route("/script/backfill_culture_links/status")
@require_admin
def backfill_culture_links_status():
    return jsonify(_backfill_status)


@admin_bp.route("/script/backfill_culture_links/companies")
@require_admin
def backfill_culture_links_companies():
    """Companies eligible for backfill that are still missing culture_links_to_explore."""
    companies = database.list_companies(exclude_states=EXCLUDE_STATES)
    eligible = sorted(
        [
            {"short_name": c["short_name"], "company_name": c.get("company_name") or c["short_name"]}
            for c in companies
            if not (c.get("company_data") or {}).get("culture_links_to_explore")
        ],
        key=lambda x: (x["company_name"] or "").lower(),
    )
    return jsonify({"companies": eligible})


# ---------------------------------------------------------------------------
# Data sync: expose table list and row data for prod-to-local sync script
# ---------------------------------------------------------------------------

@admin_bp.route("/data/tables")
@require_ip
def list_tables():
    with _get_connection() as conn:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()
    return jsonify({"tables": [r["name"] for r in rows]})


@admin_bp.route("/data/table/<table_name>")
@require_ip
def get_table_data(table_name):
    with _get_connection() as conn:
        # Validate table exists — prevents injection via untrusted table_name
        exists = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table_name,)
        ).fetchone()
        if not exists:
            return jsonify({"error": f"Table '{table_name}' not found"}), 404

        schema_only = request.args.get("schema_only", "0") == "1"
        columns = [r["name"] for r in conn.execute(f"PRAGMA table_info({table_name})").fetchall()]
        rows = [] if schema_only else [list(r) for r in conn.execute(f"SELECT * FROM {table_name}").fetchall()]

    return jsonify({"columns": columns, "rows": rows})


@admin_bp.route("/data/download")
@require_ip
def download_db():
    """Send the raw SQLite file as a binary download."""
    db_path = ASTRAL_CONFIG["db_dir"] / "astral.db"
    return send_file(str(db_path), mimetype="application/octet-stream", as_attachment=True, download_name="astral.db")
