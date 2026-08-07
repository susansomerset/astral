"""Surfer extension API (AST-1236 pacing config; later Surfer routes may join)."""

from flask import Blueprint, jsonify

from ui.auth import require_auth
from src.utils.config import SURFER_PACING_CONFIG

surfer_bp = Blueprint("surfer", __name__, url_prefix="/api/surfer")


@surfer_bp.route("/pacing_config", methods=["GET"])
@require_auth
def pacing_config():
    # Return a plain dict copy so callers cannot mutate the config module.
    return jsonify({
        "dwell_center_seconds": SURFER_PACING_CONFIG["dwell_center_seconds"],
        "dwell_spread_seconds": SURFER_PACING_CONFIG["dwell_spread_seconds"],
        "max_tabs": SURFER_PACING_CONFIG["max_tabs"],
        "mv3_idle_ceiling_seconds": SURFER_PACING_CONFIG["mv3_idle_ceiling_seconds"],
    })
