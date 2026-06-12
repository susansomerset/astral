#!/usr/bin/env python3
"""
Astral Interface - Flask API server.

Serves the React frontend (built static files from frontend/dist/) and
API routes under /api/. Imports core + utils only.
API routes are organized in ui/api/ using Flask Blueprints.
"""

import sys
from pathlib import Path

# Repo root (for `from src...`) and `src/` (for `from ui...` — package lives at src/ui/).
_repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_repo_root))
sys.path.insert(0, str(_repo_root / "src"))

from flask import Flask, send_from_directory

from ui.auth import is_ip_allowed

_DIST = Path(__file__).parent / "frontend" / "dist"

app = Flask(__name__, static_folder=None)


# --- Register Blueprints ---

from ui.api.api_system import system_bp  # noqa: E402
app.register_blueprint(system_bp)

from ui.api.api_candidate import candidate_bp  # noqa: E402
app.register_blueprint(candidate_bp)

from ui.api.api_intake import intake_bp  # noqa: E402
app.register_blueprint(intake_bp)

from ui.api.api_admin import admin_bp  # noqa: E402
app.register_blueprint(admin_bp)

from ui.api.api_companies import companies_bp  # noqa: E402
app.register_blueprint(companies_bp)

from ui.api.api_jobs import jobs_bp  # noqa: E402
app.register_blueprint(jobs_bp)

from ui.api.api_boards import boards_bp  # noqa: E402
app.register_blueprint(boards_bp)

from ui.api.api_resume_html import resume_html_bp  # noqa: E402
app.register_blueprint(resume_html_bp)

# --- Sync agent_task rows at startup ---
# B2: UI layer normally avoids `src.data`; this path stays until AST-383 moves
# startup sync behind `core.bootstrap` (see plan AST-385 / AST-383).
from src.utils.config import get_task_keys, validate_llm_provider_environment  # noqa: E402

validate_llm_provider_environment()

from src.data import database  # noqa: E402

database.sync_agent_tasks(get_task_keys())

# --- Start dispatch scheduler ---
from src.core.dispatcher import start_scheduler  # noqa: E402
start_scheduler()

# --- Serve React app ---

_BLOCKED_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Astral</title>
<style>
  body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;
       font-family:system-ui,sans-serif;background:#0d1117;color:#c9d1d9}
  .card{text-align:center;padding:3rem}
  h1{font-size:1.6rem;margin-bottom:.5rem}
  p{color:#8b949e}
  a{color:#58a6ff}
</style></head><body>
<div class="card">
  <h1>Astral</h1>
  <p>Contact <a href="mailto:susan@susansomerset.com">susan@susansomerset.com</a> for access.</p>
</div></body></html>"""


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_react(path):
    """Catch-all: serve React app if IP allowed, otherwise show contact page."""
    if not is_ip_allowed():
        return _BLOCKED_HTML, 403
    if (_DIST / path).is_file():
        return send_from_directory(_DIST, path)
    return send_from_directory(_DIST, "index.html")


if __name__ == "__main__":  # pragma: no cover
    app.run(debug=True, port=5001)
