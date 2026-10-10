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
    list_rubric_vectors,
    AGENT_SETTING_COLUMNS,
)

from src.core.consult import list_timesheets
from src.core.task_performance import build_task_performance
from src.core.inbox import count_inbox_bound_by_candidate
from src.utils.deploy_status import ui_llm_debug
from src.utils.logging import get_logger
from src.utils.cost_calculator import sum_calc_cost_components
from src.external.telescope import PlaywrightInfraError, admin_telescope_scrape, run_one_shot
from src.core.dispatcher import (
    list_dispatch_ledger, get_dispatch_ledger, list_log_entries,
    list_dispatch_tasks, save_dispatch_task, update_dispatch_task,
    count_dispatch_tasks_by_candidate, set_candidate_dispatch_tasks_from_template,
    run_task, drain_task, cancel_task, cancel_all_tasks, task_status_all,
    meteorite_mailbox_trigger_allows,
    get_auto_thread_cap, set_auto_thread_cap,
)
from src.core.candidate import (
    build_candidate_token_view,
    get_candidate,
    preview_task_prompt,
    rubric_dispatch_error,
    run_session_resume_parse,
)
from src.core.builder import build_session_base_resume, build_session_cover_letter
from src.core.table_copy_upsert import apply_copy_output_table_upsert
from src.core.repo_admin_json import (
    export_repo_admin_json_table_to_file,
    get_repo_admin_json_divergence_status,
    get_repo_admin_json_table_comparison,
    revert_repo_admin_json_table,
)
from src.utils.config import (
    ASTRAL_CONFIG,
    BUILD_CONFIG,
    LLM_MODEL_CONFIG,
    get_llm_server,
    resolve_agent_settings,
    get_manage_agents_tokens,
    get_manage_tasks_chain_tokens,
    get_repo_admin_json_table_keys,
    get_tokens,
    resolve_tokens,
    empty_render_for_prompts,
    TASK_CONFIG,
    TRACKER_CONFIG,
    UI_CONFIG,
    JOB_STATES,
    COMPANY_STATES,
    CANDIDATE_STATES,
    ENTITY_TYPES,
    dispatch_entity_state_registry,
    ADMIN_CONFIG,
    admin_hidden_dispatch_task_keys,
    admin_always_visible_under_avail_gt0_dispatch_task_keys,
    CHARS_PER_TOKEN,
    DISPATCH_RETIRED_TASK_KEYS,
    dispatch_task_admin_defaults,
    dispatch_task_key_is_scored,
    dispatch_task_key_retired_message,
    _dispatch_entity_type_for_task_key,
    _dispatch_sort_by_for,
    _dispatch_trigger_state_for_task_key,
    is_meteorite_email_mailbox_task_key,
    get_task_keys,
    dispatch_claim_uses_score_floor,
    dispatch_score_floor_option_labels,
    is_dispatch_chain_trigger,
    parse_dispatch_hop_label,
    is_registered_state,
    RUBRIC_FEEDBACK_CONFIG,
    rubric_owner_task_key_choices,
    rubric_owner_task_key,
)
from src.utils.rubric_feedback import hydrate_vector_review_strings
# Direct import — AST-292-style admin helpers (`run_adhoc_workbench_test`, `_decode_payload`) plus public `resolved_task_system`
from src.core.agent import (
    run_adhoc_workbench_test,
    list_agent_data_runs,
    _decode_payload,
    resolved_agent_content,
    resolved_task_system,
    _chain_context,
    _caller_response_blob,
    _resolve_task_prompts,
    task_llm_server_id,
)
from scripts.migrations.backfill_culture_links import run_backfill, EXCLUDE_STATES


def get_dispatch_task_by_key(task_key: str):
    """DB sample dispatch_task row else seed defaults (AST-485). Wrapper name retained for monkeypatch tests."""
    return get_dispatch_row_or_seed_preview_meta(task_key)


admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")
logger = get_logger(__name__)


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

def _api_completed(candidate_id: Optional[str], route: str, method: str, status: int) -> None:
    """stat.logging.info.api: one completion line at the route that did the work."""
    logger.info("%s | api %s completed: %s %s", candidate_id or "-", route, method, status)


def _agent_settings_from_body(body: Dict[str, Any]) -> Dict[str, Any]:
    """The plain agent settings present in a request body, passed as-is (AST-1957).
    Type checks live in the data layer (save_agent / update_agent raise ValueError → 400)."""
    return {k: body[k] for k in AGENT_SETTING_COLUMNS if k in body}


@admin_bp.route("/agents")
@require_admin
def list_agents():
    # database._expose_agent_public decodes the settings and exposes model_id + SKU (AST-1878, AST-1955).
    return jsonify([dict(a) for a in database.list_agents()])


@admin_bp.route("/agents/ids")
@require_admin
def list_agent_ids():
    return jsonify([a["agent_id"] for a in database.list_agents()])


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
    # AST-1014: columns + contact.* live on the row, not raw candidate_data alone.
    cd = build_candidate_token_view(candidate)
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
    """Model catalog for Manage Agents (AST-1880, AST-1957): label, server and the default output budget
    used when an agent leaves max_tokens empty. jsonify sorts keys, so `order` carries catalog order for the UI."""
    return jsonify({
        mid: {
            "order": i,
            "label": m["label"],
            "server_id": m["server"],
            "server_label": get_llm_server(m["server"])["label"],
            "default_max_tokens": m["default_max_tokens"],
        }
        for i, (mid, m) in enumerate(LLM_MODEL_CONFIG.items())
    })


@admin_bp.route("/agents/<agent_id>")
@require_admin
def get_agent(agent_id):
    agent = database.get_agent(agent_id)
    if not agent:
        return jsonify({"error": f"Agent not found: {agent_id}"}), 404
    return jsonify(dict(agent))


@admin_bp.route("/agents", methods=["POST"])
@require_admin
def create_agent():
    body = request.get_json(silent=True) or {}
    agent_id = (body.get("agent_id") or "").strip()
    model_id = (body.get("model_id") or "").strip()
    if not agent_id or not model_id:
        return jsonify({"error": "agent_id and model_id are required"}), 400
    if database.get_agent(agent_id):
        return jsonify({"error": f"Agent '{agent_id}' already exists"}), 409
    try:
        # Data layer checks model_id against the catalog and type-checks the settings (AST-1955).
        database.save_agent(
            agent_id,
            body.get("content", ""),
            model_id=model_id,
            max_tokens=body.get("max_tokens"),
            **_agent_settings_from_body(body),
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    _api_completed(None, "/api/admin/agents", "POST", 201)
    return jsonify({"created": agent_id}), 201


@admin_bp.route("/agents/<agent_id>", methods=["PUT"])
@require_admin
def update_agent(agent_id):
    body = request.get_json(silent=True) or {}
    if not database.get_agent(agent_id):
        return jsonify({"error": f"Agent not found: {agent_id}"}), 404

    kwargs = {
        k: (body[k].strip() if k == "model_id" and isinstance(body[k], str) else body[k])
        for k in ("content", "model_id", "max_tokens", *AGENT_SETTING_COLUMNS)
        if k in body
    }
    if not kwargs:
        return jsonify({"error": "No updatable fields provided"}), 400
    try:
        # update_agent checks model_id and type-checks the settings before its UPDATE (AST-1955).
        database.update_agent(agent_id, **kwargs)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    row = database.get_agent(agent_id)
    _api_completed(None, f"/api/admin/agents/{agent_id}", "PUT", 200)
    return jsonify(dict(row) if row else {})


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
# Repo admin JSON divergence (AST-783)
# ---------------------------------------------------------------------------

@admin_bp.route("/repo_json/status")
@require_admin
def repo_json_status():
    try:
        return jsonify(get_repo_admin_json_divergence_status())
    except (RuntimeError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 500


@admin_bp.route("/repo_json/revert/<table_key>", methods=["POST"])
@require_admin
def repo_json_revert(table_key: str):
    if table_key not in get_repo_admin_json_table_keys():
        return jsonify({"error": "unknown repo admin JSON table"}), 400
    try:
        count = revert_repo_admin_json_table(table_key)
    except (RuntimeError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 500
    return jsonify({"ok": True, "table_key": table_key, "row_count": count})


@admin_bp.route("/repo_json/compare/<table_key>")
@require_admin
def repo_json_compare(table_key: str):
    if table_key not in get_repo_admin_json_table_keys():
        return jsonify({"error": "unknown repo admin JSON table"}), 400
    try:
        comparison = get_repo_admin_json_table_comparison(table_key)
    except (RuntimeError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 500
    return jsonify(comparison)


@admin_bp.route("/repo_json/write/<table_key>", methods=["POST"])
@require_admin
def repo_json_write(table_key: str):
    if table_key not in get_repo_admin_json_table_keys():
        return jsonify({"error": "unknown repo admin JSON table"}), 400
    try:
        result = export_repo_admin_json_table_to_file(table_key)
    except (RuntimeError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 500
    return jsonify({"ok": True, **result})


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


# AST-1978: Manage Tasks RSC column — the TOKEN_SOURCES name counted in raw prompt text, before
# resolve_tokens substitutes it away. Fails at import if the registry ever drops/renames it.
_RESPONSE_SCHEMA_TOKEN_NAME = "RESPONSE_SCHEMA"
assert _RESPONSE_SCHEMA_TOKEN_NAME in get_tokens(), "RESPONSE_SCHEMA missing from TOKEN_SOURCES"
_RESPONSE_SCHEMA_TOKEN = "{$" + _RESPONSE_SCHEMA_TOKEN_NAME + "}"


def _enrich_tasks(candidate_id: str) -> list:
    """Assemble enriched task rows for the task manager screen.
    Resolves token counts against candidate_data, computes cache threshold status,
    and fetches timesheet averages per task version."""
    tasks = database.list_candidate_tasks()
    candidate = get_candidate(candidate_id) if candidate_id else None
    # AST-1014: token view merges name columns + library blobs for resolve_tokens.
    cd = build_candidate_token_view(candidate) if candidate else {}

    conn = _get_connection()
    try:
        rows = []
        for t in tasks:
            task_key = t.get("task_key", "")
            task_key_uuid = t.get("task_key_uuid")
            agent_id = t.get("agent_id") or ""
            cfg = TASK_CONFIG.get(task_key, {})

            # Agent model + settings → catalog SKU and pricing row for cache threshold math (AST-1880, AST-1957).
            full_task = database.get_agent_task(task_key) if task_key else None
            agent = database.get_agent(agent_id) if agent_id else None
            resolved_model_key = ""
            model_cfg: Dict = {}
            # List probe, not a hop — empty {$CALLER_*} is expected (AST-530 chain_entry).
            # AST-2000: token-count probe, not a model call — empty tokens are expected, stay quiet.
            _cc = _chain_context(agent, cd, task_key, None, chain_entry=True, warn_on_empty=False) if agent else None
            if agent:
                try:
                    route = resolve_agent_settings((agent.get("model_id") or "").strip(), agent)
                    resolved_model_key = route["sku"]
                    model_cfg = route["pricing"]
                except ValueError as e:
                    # Display row only — one misconfigured agent must not 500 the whole screen.
                    logger.warning(
                        "%s | task manager %s agent %s has no routable model: %s",
                        candidate_id or "-", task_key, agent_id, e,
                    )
            if full_task and agent:
                system_content = resolved_task_system(
                    agent, full_task, cd, task_key, _cc, chain_entry=True, warn_on_empty=False
                )
            elif agent:
                system_content = resolve_tokens(
                    agent.get("content") or "", cd, task_key, _cc, chain_entry=True, warn_on_empty=False
                )
            else:
                system_content = ""
            system_tokens = len(system_content) // CHARS_PER_TOKEN

            # AST-1978: RSC = raw {$RESPONSE_SCHEMA} occurrences across every segment the task sends.
            # Counted pre-resolution (resolve_tokens replaces the token); candidate-independent.
            # System segment mirrors resolved_task_system: task system_prompt when non-blank, else agent content.
            _ft = full_task or {}
            raw_system = (_ft.get("system_prompt") or "").strip() or ((agent or {}).get("content") or "")
            response_schema_count = sum(
                seg.count(_RESPONSE_SCHEMA_TOKEN)
                for seg in (raw_system, *(_ft.get(k) or "" for k in (
                    "cache_prompt", "cache_prompt_b", "cache_prompt_c", "cache_prompt_d",
                    "nocache_prompt", "user_prompt",
                )))
            )

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
                    txt = resolve_tokens(
                        full_task.get(ck) or "", cd, task_key, _cc, chain_entry=True, warn_on_empty=False
                    )
                    cache_probe_parts.append(txt)
                combined_cache_probe = "\n---\n".join(cache_probe_parts)
            else:
                combined_cache_probe = ""
            task_ready = not bool(re.search(r"\{\$[^}]+\}", combined_cache_probe))
            # When tokens unresolved: parsed_cache_tokens None; approximate total_cache below uses raw lengths.
            parsed_cache_tokens = len(combined_cache_probe) // CHARS_PER_TOKEN if task_ready else None

            # Cache threshold (model_cfg is the catalog pricing row for the agent's model)
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
                "resolved_model_key":   resolved_model_key,
                "model_code":           resolved_model_key,
                "system_prompt_tokens": system_tokens,
                "response_schema_count": response_schema_count,
                "base_cache_tokens":    base_cache_tokens,
                "parsed_cache_tokens":  parsed_cache_tokens,
                "cache_min_tokens":     cache_min,
                "cache_satisfied":      cache_satisfied,
                "nocache_prompt_tokens":nocache_prompt_tokens,
                "avg_live_tokens":      avg_live,
                "avg_output_tokens":    avg_output,
                "task_ready":           task_ready,
                "updated_at":           t.get("updated_at"),
                "user_prompt_len":       int(t.get("user_prompt_len") or 0),
                "cache_prompt_len":      int(t.get("cache_prompt_len") or 0),
                "cache_prompt_b_len":    int(t.get("cache_prompt_b_len") or 0),
                "cache_prompt_c_len":    int(t.get("cache_prompt_c_len") or 0),
                "cache_prompt_d_len":    int(t.get("cache_prompt_d_len") or 0),
                "nocache_prompt_len":    int(t.get("nocache_prompt_len") or 0),
                "system_prompt_len":     int(t.get("system_prompt_len") or 0),
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
    {"key": "batch_size", "label": "Batch size", "type": "int"},
    {"key": "completed_at", "label": "Completed", "type": "datetime"},
    {"key": "vector_code", "label": "Code", "type": "str"},
    {"key": "vector_label", "label": "Label", "type": "str"},
    {"key": "vector_assessment_header", "label": "Assessment", "type": "str"},
    {"key": "vector_content", "label": "Criterion", "type": "str"},
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


def _vector_assessment_header(importance: Any, label: Any, code: Any) -> str:
    imp = importance if isinstance(importance, int) and 1 <= importance <= 10 else 5
    lab = (str(label or "").strip()) or "??"
    cd = (str(code or "").strip())
    return f"{imp} - {lab} ({cd})" if cd else f"{imp} - {lab}"


def _resolve_rubric_owner_task_key(
    owner_task_key: Optional[str] = None,
    task_key: Optional[str] = None,
) -> Optional[str]:
    owner = (owner_task_key or "").strip()
    if owner:
        return owner
    tk = (task_key or "").strip()
    if not tk:
        return None
    mapped = rubric_owner_task_key(tk)
    return mapped or tk


def _rubric_lookup_by_code(candidate_id: str, owner_task_key: str) -> Dict[str, Dict[str, Any]]:
    rows = list_rubric_vectors(candidate_id, owner_task_key, current_only=True)
    out: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        code = str(row.get("code") or "").strip().upper()
        if not code:
            continue
        out[code] = {
            "label": row.get("label") or "",
            "content": row.get("content") or "",
            "importance": row.get("importance"),
        }
    return out


def _enrich_vector_feedback_row(row: dict) -> dict:
    out = dict(row)
    out["value_label"] = _feedback_value_label(str(out.get("value") or ""))
    ft = str(out.get("feedback_type") or "")
    out["feedback_type_label"] = _feedback_type_label(ft)
    out["vector_assessment_header"] = _vector_assessment_header(
        out.get("vector_importance"),
        out.get("vector_label"),
        out.get("vector_code"),
    )
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


@admin_bp.route("/vector_feedback/rubric_lookup")
@require_admin
def vector_feedback_rubric_lookup():
    candidate_id = (request.args.get("candidate_id") or "").strip()
    owner_task_key = _resolve_rubric_owner_task_key(
        request.args.get("owner_task_key"),
        request.args.get("task_key"),
    )
    if not candidate_id or not owner_task_key:
        return jsonify({"error": "candidate_id and owner_task_key required"}), 400
    return jsonify(_rubric_lookup_by_code(candidate_id, owner_task_key))


@admin_bp.route("/vector_feedback/hydrate_reviews", methods=["POST"])
@require_admin
def vector_feedback_hydrate_reviews():
    data = request.get_json(silent=True) or {}
    candidate_id = str(data.get("candidate_id") or "").strip()
    owner_task_key = _resolve_rubric_owner_task_key(
        data.get("owner_task_key"),
        data.get("task_key"),
    )
    vector_reviews = data.get("vector_reviews")
    if not candidate_id or not owner_task_key:
        return jsonify({"error": "candidate_id and owner_task_key required"}), 400
    rubric_by_code = _rubric_lookup_by_code(candidate_id, owner_task_key)
    rows = hydrate_vector_review_strings(vector_reviews, rubric_by_code)
    return jsonify({"rows": rows})


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


@admin_bp.route("/task_performance")
@require_admin
def task_performance():
    """Task Performance roster. Ledger lines are opt-in: lines=all, or line_task_key+line_version+line_candidate."""
    a = request.args
    lines = "all" if a.get("lines") == "all" else (
        (a["line_task_key"], a.get("line_version", ""), a.get("line_candidate", "")) if a.get("line_task_key") else None
    )
    return jsonify(build_task_performance(
        date_from=a.get("date_from"), date_to=a.get("date_to"),
        current_only=a.get("current_only") == "1", candidate_id=a.get("candidate_id") or None, lines=lines,
    ))


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
    {"key": "batch_call_mode","label": "Batch Mode",  "type": "int"},
    {"key": "freq_hrs",       "label": "Freq (hrs)",  "type": "float"},
    {"key": "sweep_hrs",      "label": "Sweep (hrs)", "type": "float"},
    {"key": "auto_mode",      "label": "AUTO",        "type": "str"},
    {"key": "debug",          "label": "Debug",       "type": "str"},
    {"key": "available_count","label": "Available",   "type": "int"},
    {"key": "last_run_at",    "label": "Last Run",    "type": "datetime"},
]


@admin_bp.route("/dispatch_tasks")
@require_admin
def list_dtasks():
    rows = list_dispatch_tasks()
    rows = [r for r in rows if r.get("task_key") not in DISPATCH_RETIRED_TASK_KEYS]

    def _inbox_avail_task_key(tk: str) -> bool:
        # meteorite mailbox fold — Gmail inbox ping Avail (AST-1214 / AST-1466).
        return is_meteorite_email_mailbox_task_key(tk)

    # One inbox snapshot when any candidate-bound mailbox Avail row is present.
    need_mailbox_counts = any(
        _inbox_avail_task_key((r.get("task_key") or "").strip())
        and str(r.get("candidate_id") or "").strip()
        for r in rows
    )
    bound_counts: Dict[str, int] = {}
    if need_mailbox_counts:
        try:
            bound_counts = count_inbox_bound_by_candidate()
        except Exception as exc:
            logger.warning("list_dtasks: mailbox inbox bind counts failed: %s", exc)
            bound_counts = {}
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
        if _inbox_avail_task_key((row.get("task_key") or "").strip()):
            cid_s = str(cid or "").strip()
            if cid_s and meteorite_mailbox_trigger_allows(row):
                row["available_count"] = int(bound_counts.get(cid_s, 0))
            else:
                row["available_count"] = 0
        else:
            try:
                # Meteorite claim pool is global — count without requiring candidate_id (AST-1623).
                if et and ts and (cid or et == "meteorite"):
                    row["available_count"] = database.count_eligible_for_dispatch_task(row)
                else:
                    row["available_count"] = 0
            except Exception as exc:
                logger.warning(
                    "list_dtasks: available_count failed for dispatch_task id=%s task_key=%r: %s",
                    row.get("id"),
                    row.get("task_key"),
                    exc,
                )
                row["available_count"] = 0
        row["always_visible_under_avail_gt0"] = (
            row.get("task_key") in admin_always_visible_under_avail_gt0_dispatch_task_keys()
        )
        # AST-1780: empty-render flag + force AUTO off when non-executable.
        er = _evaluate_dispatch_empty_render(row.get("candidate_id"), row.get("task_key") or "")
        key_err = _candidate_dispatch_api_key_error(row.get("candidate_id"), row.get("task_key") or "")
        # AST-2091: duplicate-code / empty rubric behind a rubric-backed task.
        rubric_err = rubric_dispatch_error(row.get("candidate_id"), row.get("task_key") or "")
        row["empty_render"] = bool(er.get("empty_render")) or bool(key_err) or bool(rubric_err)
        # AST-1819: missing prompt tokens for the Invalid tooltip ([] when valid or unvalidatable).
        row["empty_tokens"] = list(er.get("empty_tokens") or [])
        # AST-1880 / AST-2091: tooltip reason — key first, then rubric ("" when neither applies).
        row["invalid_reason"] = key_err or rubric_err or ""
        if row["empty_render"] and row.get("auto_mode"):
            update_dispatch_task(row["id"], auto_mode=0)
            row["auto_mode"] = 0
            tokens = er.get("empty_tokens") or []
            why = (
                key_err
                or rubric_err
                or (f"empty_render tokens={tokens}" if tokens else "empty_render (could not validate prompts)")
            )
            logger.warning(
                "%s | dispatch_task id=%s task_key=%r %s — AUTO forced off",
                row.get("candidate_id") or "-",
                row.get("id"),
                row.get("task_key"),
                why,
            )
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
    """Scheduled Actions form defaults: TASK_CONFIG / mailbox keys use dispatch_task_admin_defaults
    when defaults resolve; grouping fields from agent_task (identity catalog key);
    entity/trigger keyed by dispatch task_key."""
    catalog_key = (task_key or "").strip()
    grouping_key = catalog_key
    cfg = TASK_CONFIG.get(catalog_key) or {}
    entity_type = cfg.get("entity_type") or ""
    ts = cfg.get("trigger_state")
    trigger_state = (ts or "") if ts is not None else ""
    # Prefer derived admin defaults (TASK_CONFIG + meteorite mailbox fold).
    if catalog_key in TASK_CONFIG or is_meteorite_email_mailbox_task_key(catalog_key):
        try:
            derived = dispatch_task_admin_defaults(catalog_key)
            entity_type = derived["entity_type"] or ""
            trigger_state = (
                (derived["trigger_state"] or "")
                if derived["trigger_state"] is not None
                else ""
            )
        except KeyError:
            pass  # mid-chain / no default — keep prior field values
    # Helper-resolvable agent_task-only hops fill empty entity/trigger.
    if not entity_type:
        try:
            entity_type = _dispatch_entity_type_for_task_key(catalog_key) or ""
        except KeyError:
            pass
    if not trigger_state:
        try:
            trigger_state = _dispatch_trigger_state_for_task_key(catalog_key) or ""
        except KeyError:
            pass
    batch_call_mode = 0
    if catalog_key in TASK_CONFIG or is_meteorite_email_mailbox_task_key(catalog_key):
        try:
            batch_call_mode = int(
                dispatch_task_admin_defaults(catalog_key)["batch_call_mode"]
            )
        except KeyError:
            pass
    return {
        "entity_type": entity_type or "",
        "trigger_state": trigger_state,
        "is_scored": dispatch_task_key_is_scored(catalog_key),
        "batch_call_mode": batch_call_mode,
        **_catalog_task_grouping_meta(grouping_key),
    }


def _admin_dispatch_task_key_catalog() -> dict[str, dict]:
    """Live Admin picker catalog: agent_task ∪ TASK_CONFIG ∪ dispatch orphans, alpha by task_key."""
    membership: set[str] = set(get_task_keys())
    for row in database.list_candidate_tasks():
        tk = (row.get("task_key") or "").strip()
        if tk:
            membership.add(tk)
    for r in list_dispatch_tasks():
        k = (r.get("task_key") or "").strip()
        if k:
            membership.add(k)
    membership -= set(admin_hidden_dispatch_task_keys())
    membership -= set(DISPATCH_RETIRED_TASK_KEYS)
    return {tk: _dispatch_task_key_form_meta(tk) for tk in sorted(membership)}


@admin_bp.route("/dispatch_tasks/task_keys")
@require_admin
def dispatch_task_keys():
    """task_key → form meta for Scheduled Actions (and peer Admin pickers).

    Membership is the live union of TASK_CONFIG keys, current agent_task keys
    (including fetch_* and peers), and existing dispatch_task keys — sorted
    alphabetically by task_key via sorted(membership). Retired / admin-hidden
    keys are omitted. Grouping fields come from agent_task; no parallel
    section inventory.
    """
    return jsonify(_admin_dispatch_task_key_catalog())


@admin_bp.route("/dispatch_tasks/state_options")
@require_admin
def dispatch_task_state_options():
    return jsonify({
        "job": list(JOB_STATES.keys()),
        "company": list(COMPANY_STATES.keys()),
        "candidate": list(CANDIDATE_STATES.keys()),
        "meteorite": list(dispatch_entity_state_registry("meteorite").keys()),
    })


@admin_bp.route("/dispatch_tasks/score_floor_options")
@require_admin
def dispatch_task_score_floor_options():
    # pattern.ui.admin-endpoint — options catalog from config (AST-1278 / AST-750)
    return jsonify({"values": dispatch_score_floor_option_labels()})


@admin_bp.route("/dispatch_tasks/counts")
@require_admin
def dispatch_task_counts():
    """Per-candidate dispatch_task row counts for Manage Candidates (AST-875)."""
    return jsonify({"counts": count_dispatch_tasks_by_candidate()})


@admin_bp.route("/dispatch_tasks/set_from_template", methods=["POST"])
@require_admin
def set_dispatch_tasks_from_template():
    """Mirror config template candidate schedule onto target candidate (AST-875)."""
    data = request.get_json(force=True) or {}
    candidate_id = str(data.get("candidate_id") or "").strip()
    if not candidate_id:
        return jsonify({"error": "candidate_id is required"}), 400
    try:
        result = set_candidate_dispatch_tasks_from_template(candidate_id)
    except LookupError as exc:
        return jsonify({"error": str(exc)}), 404
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(result)


def _parse_sweep_hrs(raw: Any) -> tuple[float | None, str | None]:
    """sweep_hrs from admin JSON (AST-1830): None/"" → NULL; else a non-negative float.
    Returns (value, error); error is a 400 message. 0 is kept as 0.0 (off, same as NULL)."""
    if raw is None or (isinstance(raw, str) and raw.strip() == ""):
        return None, None
    try:
        val = float(raw)
    except (TypeError, ValueError):
        return None, "sweep_hrs must be a non-negative number"
    if val < 0:
        return None, "sweep_hrs must be a non-negative number"
    return val, None


@admin_bp.route("/dispatch_tasks", methods=["POST"])
@require_admin
def create_dtask():
    data = request.get_json(force=True)
    required = ("candidate_id", "task_key", "trigger_state", "min_count")
    missing = [k for k in required if k not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400
    task_key = (data.get("task_key") or "").strip()
    retired = dispatch_task_key_retired_message(task_key)
    if retired:
        return jsonify({"error": retired}), 400
    # Absent / JSON null → catalog defaults in save; non-empty must be ENTITY_TYPES.
    submitted_entity = None
    if "entity_type" in data and data.get("entity_type") is not None:
        raw_et = str(data.get("entity_type") or "").strip()
        if raw_et == "":
            return jsonify({"error": "entity_type must be non-empty when provided"}), 400
        if raw_et not in ENTITY_TYPES:
            return jsonify({"error": f"unsupported entity_type {raw_et!r}"}), 400
        submitted_entity = raw_et
    is_scored = dispatch_claim_uses_score_floor(data.get("trigger_state"))
    raw_score_floor = data.get("score_floor", None)
    score_floor = float(raw_score_floor) if (is_scored and raw_score_floor is not None) else (1.0 if is_scored else None)
    sweep_hrs, sweep_err = _parse_sweep_hrs(data.get("sweep_hrs"))
    if sweep_err:
        return jsonify({"error": sweep_err}), 400
    if bool(data.get("auto_mode", False)):
        err = _candidate_dispatch_api_key_error(data.get("candidate_id"), task_key)
        if err:
            return jsonify({"error": err}), 400
        err = rubric_dispatch_error(data.get("candidate_id"), task_key)
        if err:
            return jsonify({"error": err}), 400
        err = _candidate_dispatch_empty_render_error(data.get("candidate_id"), task_key)
        if err:
            return jsonify({"error": err}), 400
    tk_err = _dispatch_task_key_trigger_error(
        task_key,
        data.get("trigger_state"),
        entity_type=submitted_entity,
    )
    if tk_err:
        return jsonify({"error": tk_err}), 400
    try:
        task_id = save_dispatch_task(
            candidate_id=data["candidate_id"],
            task_key=task_key,
            min_count=int(data["min_count"]),
            auto_mode=bool(data.get("auto_mode", False)),
            entity_type=submitted_entity,
            trigger_state=data.get("trigger_state"),
            batch_size=int(data["batch_size"]) if data.get("batch_size") else None,
            freq_hrs=float(data.get("freq_hrs", 0)),
            score_floor=score_floor,
            sweep_hrs=sweep_hrs,
        )
    except Exception as e:
        if "UNIQUE" in str(e):
            return jsonify({
                "error": (
                    f"Dispatch row already exists for candidate '{data['candidate_id']}', "
                    f"task_key '{task_key}', trigger_state '{data['trigger_state']}'"
                )
            }), 409
        return jsonify({"error": str(e)}), 500
    if data.get("skip_daisy_chain"):
        update_dispatch_task(task_id, skip_daisy_chain=1)
    if "batch_call_mode" in data and data.get("batch_call_mode") is not None:
        update_dispatch_task(task_id, batch_call_mode=int(bool(data["batch_call_mode"])))
    # save_dispatch_task has no max_runs param; without this, form-created rows keep the column default 1.
    if "max_runs" in data and data.get("max_runs") is not None:
        update_dispatch_task(task_id, max_runs=int(data["max_runs"]))
    _api_completed(data.get("candidate_id"), "/api/admin/dispatch_tasks", "POST", 201)
    return jsonify({"id": task_id}), 201


def _dispatch_task_key_trigger_error(
    task_key: str,
    trigger_state: str | None,
    entity_type: str | None = None,
) -> str | None:
    tk = (task_key or "").strip()
    if not tk:
        return "task_key is required"
    retired = dispatch_task_key_retired_message(tk)
    if retired:
        return retired
    # stage_email_meteorite mailbox fold is candidate-bound: empty trigger = no state gate; otherwise CANDIDATE_STATES.
    if is_meteorite_email_mailbox_task_key(tk):
        # stat.dispatch.entity-state-bound: a mailbox poller has no entity_type binding at all
        # (METEORITE_EMAIL_MAILBOX_CONFIG["entity_type"] is None) — reject any submitted value
        # here instead of letting save_dispatch_task silently discard it later.
        if entity_type is not None and str(entity_type).strip():
            return f"task_key {tk!r} does not take an entity_type (mailbox poller has no entity binding)"
        ts = (trigger_state or "").strip()
        if not ts:
            return None
        registry = dispatch_entity_state_registry("candidate")
        registry_ts = ts
        parsed = parse_dispatch_hop_label(ts)
        if parsed:
            registry_ts = parsed[0]
        if not is_registered_state(registry, registry_ts):
            return f"task_key {tk!r} (candidate) is not valid for trigger_state {ts!r}"
        return None
    # Optional override from admin form; else catalog entity for task_key.
    if entity_type is not None and str(entity_type).strip():
        et = str(entity_type).strip()
        if et not in ENTITY_TYPES:
            return f"unsupported entity_type {et!r}"
    else:
        try:
            et = _dispatch_entity_type_for_task_key(tk)
        except KeyError:
            if tk in TASK_CONFIG:
                return f"task_key {tk!r} has unsupported entity_type"
            return f"Unknown task_key: {tk!r}"
    ts = (trigger_state or "").strip()
    if not ts:
        return "trigger_state is required"
    if et not in ENTITY_TYPES:
        return f"task_key {tk!r} has unsupported entity_type {et!r}"
    try:
        registry = dispatch_entity_state_registry(et)
    except KeyError:
        return f"task_key {tk!r} has unsupported entity_type {et!r}"
    registry_ts = ts
    parsed_registry = parse_dispatch_hop_label(ts)
    if parsed_registry:
        registry_ts = parsed_registry[0]
    if not is_registered_state(registry, registry_ts):
        return f"task_key {tk!r} ({et}) is not valid for trigger_state {ts!r}"
    if is_dispatch_chain_trigger(registry_ts):
        parsed = parse_dispatch_hop_label(ts)
        if parsed and parsed[1] != tk:
            return f"task_key {tk!r} does not match hop in trigger_state {ts!r}"
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
        "min_count", "batch_size", "batch_call_mode", "auto_mode", "debug", "skip_cache",
        "skip_daisy_chain", "freq_hrs", "max_runs", "score_floor", "trigger_state", "task_key",
        "entity_type", "sweep_hrs",
    }
    updates: Dict[str, Any] = {}
    # JSON null on entity_type mirrors create — treat as omitted (Joan discuss).
    entity_in_body = "entity_type" in data and data.get("entity_type") is not None
    effective_task_key = (
        (data["task_key"] if "task_key" in data else row.get("task_key") or "")
    )
    if isinstance(effective_task_key, str):
        effective_task_key = effective_task_key.strip()
    else:
        effective_task_key = str(effective_task_key or "").strip()
    effective_trigger_state = data.get("trigger_state", row.get("trigger_state"))
    if entity_in_body:
        submitted_et = str(data.get("entity_type") or "").strip()
        if submitted_et == "":
            return jsonify({"error": "entity_type must be non-empty when provided"}), 400
        if submitted_et not in ENTITY_TYPES:
            return jsonify({"error": f"unsupported entity_type {submitted_et!r}"}), 400
        effective_entity_type = submitted_et
    elif "task_key" in data:
        try:
            effective_entity_type = dispatch_task_admin_defaults(
                effective_task_key, trigger_state=effective_trigger_state,
            )["entity_type"]
        except KeyError as exc:
            return jsonify({"error": str(exc)}), 400
    else:
        effective_entity_type = row.get("entity_type")
    if "task_key" in data or "trigger_state" in data or entity_in_body:
        tk_err = _dispatch_task_key_trigger_error(
            effective_task_key,
            effective_trigger_state,
            entity_type=effective_entity_type,
        )
        if tk_err:
            return jsonify({"error": tk_err}), 400
    if "task_key" in data:
        try:
            defaults = dispatch_task_admin_defaults(
                effective_task_key, trigger_state=effective_trigger_state,
            )
        except KeyError as exc:
            return jsonify({"error": str(exc)}), 400
        updates["task_key"] = effective_task_key
        updates["entity_type"] = effective_entity_type
        updates["batch_call_mode"] = defaults["batch_call_mode"]
    if entity_in_body:
        updates["entity_type"] = effective_entity_type
    if "task_key" in data or "trigger_state" in data or entity_in_body:
        mailbox = is_meteorite_email_mailbox_task_key(effective_task_key)
        ts_for_sort = str(effective_trigger_state or "").strip()
        if mailbox and not ts_for_sort:
            if "trigger_state" in data:
                updates["sort_by"] = None
        else:
            et_sort = (effective_entity_type or "candidate") if mailbox else effective_entity_type
            try:
                updates["sort_by"] = _dispatch_sort_by_for(
                    et_sort, effective_trigger_state,
                )
            except KeyError as exc:
                return jsonify({"error": str(exc)}), 400
    if "sweep_hrs" in data:
        sweep_hrs, sweep_err = _parse_sweep_hrs(data["sweep_hrs"])
        if sweep_err:
            return jsonify({"error": sweep_err}), 400
    trigger_state = data.get("trigger_state", row.get("trigger_state"))
    is_scored = dispatch_claim_uses_score_floor(trigger_state)
    for k in allowed:
        if k in data and k not in ("task_key", "entity_type"):
            if k in ("min_count", "batch_size", "max_runs"):
                updates[k] = int(data[k]) if data[k] is not None else None
            elif k in ("auto_mode", "debug", "skip_cache", "skip_daisy_chain", "batch_call_mode"):
                updates[k] = int(bool(data[k]))
            elif k == "freq_hrs":
                updates[k] = float(data[k])
            elif k == "trigger_state":
                updates[k] = str(data[k]) if data[k] else None
            elif k == "sweep_hrs":
                updates[k] = sweep_hrs
            elif k == "score_floor":  # pragma: no branch
                updates[k] = float(data[k]) if (is_scored and data[k] is not None) else (1.0 if is_scored else None)
    if not updates:
        return jsonify({"error": "No valid fields to update"}), 400
    if updates.get("auto_mode") == 1:
        cid = row.get("candidate_id")
        err = _candidate_dispatch_api_key_error(cid, effective_task_key)
        if err:
            return jsonify({"error": err}), 400
        err = rubric_dispatch_error(cid, effective_task_key)
        if err:
            return jsonify({"error": err}), 400
        err = _candidate_dispatch_empty_render_error(cid, effective_task_key)
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
    _api_completed(row.get("candidate_id"), f"/api/admin/dispatch_tasks/{task_id}", "PUT", 200)
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
        if task_key == "prefilter_company":
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
        # batch mode: qualify_job_listings assembles raw listings in one block
        if task_key == "qualify_job_listings":
            ids = entity_ids if entity_ids else ([entity_id] if entity_id else [])
            raw_htmls, astral_ids = [], []
            for jid in ids:
                job = database.get_job(jid)
                if job:
                    raw_listing = (job.get("job_data") or {}).get("raw_job_listing", "")
                    # Match the real assemble() in consult.py — include job_site from company
                    company = database.get_company(job.get("company", ""))
                    job_site = (company or {}).get("job_site", "") or ""
                    raw_htmls.append(f"job_site: {job_site}\nraw_job_listing: {raw_listing}")
                    astral_ids.append(jid)
            return (
                "JOB LISTINGS:\n" + "\n".join(f"{i:03d}: {item}" for i, item in enumerate(raw_htmls))
            ) if astral_ids else ""
        # batch mode: qualify_meteorite — lockstep with consult.qualify_meteorite assemble
        if task_key == "qualify_meteorite":
            ids = entity_ids if entity_ids else ([entity_id] if entity_id else [])
            jd_key = TRACKER_CONFIG["job_data_keys"]["job_description"]
            lines = []
            for jid in ids:
                job = database.get_job(jid)
                if not job:
                    continue
                lines.append(
                    f"{len(lines):03d}: job_link: {job.get('job_link') or ''}\n"
                    f"CONTENT:\n{(job.get('job_data') or {}).get(jd_key, '') or ''}"
                )
            return ("METEORITE JOBS:\n" + "\n".join(lines)) if lines else ""
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


@admin_bp.route("/adhoc/runs")
@require_admin
def adhoc_runs():
    """Import picker source: candidate-scoped agent_data batches, newest first, config-capped."""
    candidate_id = (request.args.get("candidate_id") or "").strip()
    task_key = (request.args.get("task_key") or "").strip()
    return jsonify(
        list_agent_data_runs(
            candidate_id=candidate_id or None,
            task_key=task_key or None,
            limit=UI_CONFIG["adhoc_import_runs_limit"],
            debug=ui_llm_debug(),
        )
    )


def _resolve_adhoc(body):
    """Load agent, resolve tokens, return resolved prompts + model params.
    Returns (dict, error_tuple). On success error_tuple is None."""
    agent_id = (body.get("agent_id") or "").strip()
    if not agent_id:
        return None, (jsonify({"error": "agent_id is required"}), 400)

    agent = database.get_agent(agent_id)
    if not agent:
        return None, (jsonify({"error": f"Agent not found: {agent_id}"}), 404)

    # Agent model + plain settings → server, SKU and tier (AST-1880, AST-1957); tier carries temperature, effort and provider.
    try:
        route = resolve_agent_settings((agent.get("model_id") or "").strip(), agent)
    except ValueError as e:
        return None, (jsonify({"error": str(e)}), 400)
    tier = route["tier"]
    temperature = tier["temperature"]
    max_tokens = tier["max_tokens"]

    candidate_id = (body.get("candidate_id") or "").strip()
    cd = {}
    candidate = None
    if candidate_id:
        candidate = get_candidate(candidate_id)
        if candidate:
            # AST-1014: adhoc resolve needs columns + contact.* (not raw blob only).
            cd = build_candidate_token_view(candidate)

    task_key = (body.get("task_key") or "adhoc").strip()

    # Resolve task_key_uuid for timesheet attribution (None for pure adhoc)
    agent_task_row = database.get_agent_task(task_key) if task_key != "adhoc" else None
    task_key_uuid = agent_task_row.get("task_key_uuid") if agent_task_row else None

    task_cfg = TASK_CONFIG.get(task_key, {})
    # Every task requires the candidate key (AST-1877 assert); core run_adhoc picks the route's server
    # key from this map and fails with no request when it is missing (AST-1879).
    candidate_api_keys = (candidate or {}).get("candidate_api_keys")

    jc = None
    if task_cfg.get("entity_type") == "job":
        entity_id = (body.get("entity_id") or "").strip()
        if entity_id:
            job = database.get_job(entity_id)
            if job:
                from src.core.consult import build_job_token_context

                jc = build_job_token_context(job, cd)
    _cc = _chain_context(agent, cd, task_key, jc)
    if "system_prompt" in body:
        # Editor sent the field (sibling #2): empty → agent content via resolved_task_system.
        agent_task_for_system = {"system_prompt": body.get("system_prompt") or ""}
    else:
        # Key omitted (today’s three-slot UI): keep DB task system, then agent content.
        agent_task_for_system = (
            {"system_prompt": ""} if agent_task_row is None and task_key == "adhoc" else (agent_task_row or {})
        )
    cache_a = resolve_tokens(body.get("cache_prompt", "") or "", cd, task_key, _cc, jc)
    cache_b = resolve_tokens(body.get("cache_prompt_b", "") or "", cd, task_key, _cc, jc)
    cache_c = resolve_tokens(body.get("cache_prompt_c", "") or "", cd, task_key, _cc, jc)
    cache_d = resolve_tokens(body.get("cache_prompt_d", "") or "", cd, task_key, _cc, jc)
    return {
        "system": resolved_task_system(agent, agent_task_for_system, cd, task_key, _cc, jc),
        "user": resolve_tokens(body.get("user_prompt", ""), cd, task_key, _cc, jc),
        "cache": cache_a,
        "cache_a": cache_a,
        "cache_b": cache_b,
        "cache_c": cache_c,
        "cache_d": cache_d,
        "nocache": resolve_tokens(body.get("nocache_prompt", ""), cd, task_key, _cc, jc),
        "model_code": route["sku"],
        "server_id": route["server_id"],
        "tier": tier,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "candidate_id": candidate_id or None,
        "task_key_uuid": task_key_uuid,
        "candidate_api_keys": candidate_api_keys,
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
        "cache_a": resolved["cache_a"],
        "cache_b": resolved["cache_b"],
        "cache_c": resolved["cache_c"],
        "cache_d": resolved["cache_d"],
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
            cache_content=resolved.get("cache") or None,
            cache_content_b=resolved.get("cache_b") or None,
            cache_content_c=resolved.get("cache_c") or None,
            cache_content_d=resolved.get("cache_d") or None,
            nocache_content=resolved.get("nocache") or None,
            live_content=live_content,
            response_format=task_response_format,
            model_code=resolved["model_code"],
            server_id=resolved["server_id"],
            tier=resolved["tier"],
            temperature=resolved["temperature"],
            max_tokens=resolved["max_tokens"],
            candidate_api_keys=resolved["candidate_api_keys"],
            task_key_uuid=resolved["task_key_uuid"],
            debug=ui_llm_debug(),
        ))
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

    if not result.get("success"):
        err_body = {"success": False, "error": result.get("error", "Unknown error")}
        if result.get("batch_id"):
            err_body["batch_id"] = result["batch_id"]
        return jsonify(err_body), 500

    parsed = result.get("parsed_response")
    if isinstance(parsed, dict) and "agent_payload" in parsed:
        body = parsed["agent_payload"]
    else:
        body = parsed
    response_text = _caller_response_blob(body)
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

    _api_completed(resolved["candidate_id"], "/api/admin/adhoc/test", "POST", 200)
    return jsonify({
        "success": True,
        "response_text": response_text,
        "hydrated": hydrated,
        "timesheet": timesheet,
        "batch_id": result.get("batch_id"),
    })


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


@admin_bp.route("/session_resume/parse", methods=["POST"])
@require_admin
def session_resume_parse():
    """AST-986/AST-1038: paste → simple_resume_parse (Ruth) on the selected candidate's key (AST-1880); response-only, no candidate write."""
    body = request.get_json(silent=True) or {}
    resume_text = body.get("resume_text")
    candidate_id = (body.get("candidate_id") or "").strip()
    # Core returns 400 with no request when candidate_id is missing (AST-1878).
    result_body, status = run_session_resume_parse(
        resume_text if isinstance(resume_text, str) else "",
        candidate_id=candidate_id,
        debug=ui_llm_debug(),
    )
    if status < 400:
        _api_completed(candidate_id, "/api/admin/session_resume/parse", "POST", status)
    return jsonify(result_body), status


# AST-987 session resume HTML
@admin_bp.route("/session_resume/html", methods=["POST"])
@require_admin
def session_resume_html():
    """AST-987: in-memory structure + base_resume → print HTML (no candidate bind)."""
    body = request.get_json(silent=True) or {}
    structure = body.get("resume_structure")
    content = body.get("base_resume")
    if not isinstance(structure, dict) or not isinstance(content, dict):
        return jsonify({
            "success": False,
            "error": "resume_structure and base_resume objects are required",
        }), 400
    try:
        html = build_session_base_resume(
            structure,
            content,
            debug=ui_llm_debug(),
        )
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    return Response(html, mimetype="text/html; charset=utf-8")


# AST-1024 session cover letter HTML
@admin_bp.route("/session_cover_letter/html", methods=["POST"])
@require_admin
def session_cover_letter_html():
    """AST-1024: in-memory cover fields → SomersetCover HTML (optional candidate signature image)."""
    body = request.get_json(silent=True) or {}
    if not isinstance(body, dict):
        return jsonify({"success": False, "error": "JSON object body is required"}), 400
    # Field keys from config only — do not hardcode the key list here (Joan plan-discuss round=1).
    field_defs = BUILD_CONFIG["session_cover_letter"]["fields"]
    fields = {k: body.get(k, "") for k in field_defs}
    raw_cid = body.get("candidate_id")
    candidate_id = raw_cid.strip() if isinstance(raw_cid, str) else None
    if candidate_id == "":
        candidate_id = None
    try:
        html_out = build_session_cover_letter(
            fields,
            candidate_id=candidate_id,
            debug=ui_llm_debug(),
        )
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    return Response(html_out, mimetype="text/html; charset=utf-8")



# ---------------------------------------------------------------------------
# Scheduled Queries (AST-1122)
# ---------------------------------------------------------------------------

@admin_bp.route("/scheduled_queries", methods=["GET"])
@require_admin
def list_scheduled_queries_api():
    return jsonify(database.list_scheduled_queries())


@admin_bp.route("/scheduled_queries", methods=["POST"])
@require_admin
def create_scheduled_query_api():
    body = request.get_json(silent=True) or {}
    try:
        row = database.save_scheduled_query(
            name=body.get("name") or "",
            sql_text=body.get("sql_text") or "",
            active=bool(body.get("active", False)),
            interval_hours=float(body.get("interval_hours", 24)),
            scheduled_query_id=body.get("scheduled_query_id"),
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify(row), 201


@admin_bp.route("/scheduled_queries/<scheduled_query_id>", methods=["PUT"])
@require_admin
def update_scheduled_query_api(scheduled_query_id: str):
    body = request.get_json(silent=True) or {}
    kwargs = {}
    if "name" in body:
        kwargs["name"] = body.get("name")
    if "sql_text" in body:
        kwargs["sql_text"] = body.get("sql_text")
    if "active" in body:
        kwargs["active"] = bool(body.get("active"))
    if "interval_hours" in body:
        kwargs["interval_hours"] = float(body.get("interval_hours"))
    try:
        row = database.update_scheduled_query(scheduled_query_id, **kwargs)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    if row is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(row)


@admin_bp.route("/scheduled_queries/<scheduled_query_id>", methods=["DELETE"])
@require_admin
def delete_scheduled_query_api(scheduled_query_id: str):
    ok = database.delete_scheduled_query(scheduled_query_id)
    if not ok:
        return jsonify({"error": "not found"}), 404
    return jsonify({"ok": True})


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

def _dispatch_empty_render_prompt_texts(task_key: str) -> list:
    """Raw prompt segments for empty-render gating (AST-1780 / AST-1779 order)."""
    agent_row, agent_task_row = _resolve_task_prompts(task_key)
    texts = [
        agent_task_row.get("system_prompt") or "",
        agent_task_row.get("cache_prompt") or "",
        agent_task_row.get("cache_prompt_b") or "",
        agent_task_row.get("cache_prompt_c") or "",
        agent_task_row.get("cache_prompt_d") or "",
        agent_task_row.get("nocache_prompt") or "",
        agent_task_row.get("user_prompt") or "",
    ]
    # Match resolved_task_system: agent content only when task system_prompt is blank.
    if not (agent_task_row.get("system_prompt") or "").strip():
        texts.append(agent_row.get("content") or "")
    return texts


def _evaluate_dispatch_empty_render(
    candidate_id: Optional[str], task_key: str
) -> dict:
    """Return empty_render_for_prompts result; never raises for soft misses."""
    cid = (candidate_id or "").strip()
    tk = (task_key or "").strip()
    if not cid:
        logger.warning(
            "%s | dispatch empty_render task_key=%r — no candidate_id; treating as empty_render",
            "-",
            tk,
        )
        return {"empty_render": True, "empty_tokens": []}
    cand = get_candidate(cid)
    if not cand:
        logger.warning(
            "%s | dispatch empty_render task_key=%r — candidate not found; treating as empty_render",
            cid,
            tk,
        )
        return {"empty_render": True, "empty_tokens": []}
    cd = build_candidate_token_view(cand)
    try:
        texts = _dispatch_empty_render_prompt_texts(tk)
    except ValueError:
        # No agent_task / prompts to score → intentional soft-miss pass (AST-1791);
        # silent — do not warn (AST-1794: n/a agent is not a misconfiguration).
        return {"empty_render": False, "empty_tokens": []}
    except Exception as exc:
        logger.exception(
            "%s | dispatch empty_render task_key=%r\n  %s: %s\n  Leaving empty_render true for this row",
            cid,
            tk,
            type(exc).__name__,
            exc,
        )
        return {"empty_render": True, "empty_tokens": []}
    # Rubric tokens are candidate-keyed (resolver reads cd["_astral_candidate_id"]); the
    # value is unused — only key presence opts source: rubric into scoring (AST-1779 seam).
    # Job/other entity sources stay out: job tokens alone never flip the gate (AST-1780 AC5).
    return empty_render_for_prompts(texts, cd, tk, entity_contexts={"rubric": {}})


def _candidate_dispatch_empty_render_error(
    candidate_id: Optional[str], task_key: str
) -> Optional[str]:
    """If set, return a user-facing message; AUTO/Run need non-empty candidate-scoped fills."""
    result = _evaluate_dispatch_empty_render(candidate_id, task_key)
    if not result.get("empty_render"):
        return None
    tokens = result.get("empty_tokens") or []
    if tokens:
        return (
            "Prompt tokens resolve empty for this candidate (cannot Auto/Run): "
            + ", ".join(tokens)
        )
    return (
        "Cannot Auto/Run: prompts could not be validated for empty-render "
        "on this candidate/task."
    )


def _candidate_dispatch_api_key_error(candidate_id: Optional[str], task_key: str) -> Optional[str]:
    """User-facing reason when Run/Auto can't start: the candidate lacks the key for the task agent's server."""
    if not candidate_id:
        return "This dispatch task has no candidate; set one before Run or Auto."
    cand = database.get_candidate(candidate_id)
    if not cand:
        return f"Candidate not found: {candidate_id}"
    try:
        server_id = task_llm_server_id(task_key)
    except ValueError:
        # No agent/model behind this task (table runners, notify) — no platform key to require.
        return None
    if (cand.get("candidate_api_keys") or {}).get(server_id):
        return None
    return f"Set this candidate's {get_llm_server(server_id)['label']} API key before using Run or Auto on this task."


@admin_bp.route("/dispatch_tasks/<int:task_id>/run", methods=["POST"])
@require_admin
def run_dtask(task_id):
    row = database.get_dispatch_task(task_id)
    if not row:
        return jsonify({"error": "Dispatch task not found", "started": False}), 404
    err = _candidate_dispatch_api_key_error(row.get("candidate_id"), row.get("task_key") or "")
    if err:
        return jsonify({"error": err, "started": False}), 400
    err = rubric_dispatch_error(row.get("candidate_id"), row.get("task_key") or "")
    if err:
        return jsonify({"error": err, "started": False}), 400
    err = _candidate_dispatch_empty_render_error(
        row.get("candidate_id"), row.get("task_key") or ""
    )
    if err:
        return jsonify({"error": err, "started": False}), 400
    started = run_task(task_id, ui_initiated=True)
    _api_completed(row.get("candidate_id"), f"/api/admin/dispatch_tasks/{task_id}/run", "POST", 200)
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


def _auto_thread_cap_payload() -> Dict[str, int]:
    """Effective AUTO thread cap plus config default and bounds (bounds drive the UI dropdown)."""
    return {
        "max_auto_threads": get_auto_thread_cap(),
        "default": ASTRAL_CONFIG["max_auto_threads"],
        "min": ASTRAL_CONFIG["max_auto_threads_min"],
        "max": ASTRAL_CONFIG["max_auto_threads_max"],
    }


@admin_bp.route("/scheduler/auto_thread_cap")
@require_admin
def scheduler_get_auto_thread_cap():
    return jsonify(_auto_thread_cap_payload())


@admin_bp.route("/scheduler/auto_thread_cap", methods=["POST"])
@require_admin
def scheduler_set_auto_thread_cap():
    body = request.get_json(silent=True) or {}
    try:
        set_auto_thread_cap(body.get("max_auto_threads"))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify(_auto_thread_cap_payload())


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


@admin_bp.route("/telescope", methods=["POST"])
@require_admin
def admin_telescope():
    """Operator workbench — proxy to Telescope with scrape_meta (AST-1728)."""
    body = request.get_json(silent=True) or {}
    url = (body.get("url") or "").strip()
    if not url:
        return jsonify({"error": "url required"}), 400
    response_type = (body.get("response_type") or "").strip().lower()
    if response_type not in ("text", "html"):
        return jsonify({"error": "response_type must be text or html"}), 400
    expand = body.get("expand", True)
    wait_ready = body.get("wait_ready", False)
    links = body.get("links", True)
    cull = body.get("cull", False)
    debug = body.get("debug", False)
    selector = body.get("selector")
    if selector is not None:
        selector = str(selector).strip() or None
    tag = body.get("tag")
    if tag is not None:
        tag = str(tag).strip() or None
    class_name = body.get("class_name")
    if class_name is not None:
        class_name = str(class_name).strip() or None
    element_id = body.get("id")
    if element_id is not None:
        element_id = str(element_id).strip() or None
    try:
        data = run_one_shot(
            admin_telescope_scrape(
                url,
                response_type=response_type,
                expand=bool(expand),
                wait_ready=bool(wait_ready),
                links=bool(links),
                selector=selector,
                tag=tag,
                class_name=class_name,
                id=element_id,
                cull=bool(cull),
                debug=bool(debug),
            )
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except PlaywrightInfraError as e:
        return jsonify({"error": e.failure_class, "detail": str(e)}), 502
    except Exception as e:
        return jsonify({"error": "telescope_error", "detail": str(e)}), 502
    return jsonify(data)
