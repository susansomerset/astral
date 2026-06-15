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

from src.core.auth_bootstrap import wire_stytch_token_authenticator

_DIST = Path(__file__).parent / "frontend" / "dist"

app = Flask(__name__, static_folder=None)

wire_stytch_token_authenticator()

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

# --- Runtime bootstrap (validation → agent_task sync → scheduler) ---
from src.core.bootstrap import bootstrap_runtime  # noqa: E402

bootstrap_runtime()

# --- Serve React app ---


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_react(path):
    """Catch-all: serve React static assets (auth enforced on /api/* routes)."""
    if (_DIST / path).is_file():
        return send_from_directory(_DIST, path)
    return send_from_directory(_DIST, "index.html")


if __name__ == "__main__":  # pragma: no cover
    app.run(debug=True, port=5001)
