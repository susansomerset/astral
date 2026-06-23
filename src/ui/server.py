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
_FRONTEND_SRC = Path(__file__).parent / "frontend" / "src"

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


def _warn_stale_frontend_dist() -> None:
    """Local dev: Flask :5001 serves dist/; git pull does not rebuild it."""
    dist_index = _DIST / "index.html"
    if not _FRONTEND_SRC.is_dir():
        return
    src_files = [
        p for p in _FRONTEND_SRC.rglob("*")
        if p.suffix in (".ts", ".tsx") and p.is_file()
    ]
    if not src_files:
        return
    if not dist_index.is_file():
        print(
            "WARNING: frontend/dist missing — UI on :5001 will 404 or be stale; "
            "run: cd src/ui/frontend && npm run build (or use http://localhost:5173)",
            file=sys.stderr,
        )
        return
    dist_mtime = dist_index.stat().st_mtime
    newest_src = max(p.stat().st_mtime for p in src_files)
    if newest_src > dist_mtime:
        print(
            "WARNING: frontend/dist older than src/ — :5001 serves stale UI; "
            "rebuild (npm run build) or use http://localhost:5173 (vite)",
            file=sys.stderr,
        )


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_react(path):
    """Catch-all: serve React static assets (auth enforced on /api/* routes)."""
    if (_DIST / path).is_file():
        return send_from_directory(_DIST, path)
    return send_from_directory(_DIST, "index.html")


if __name__ == "__main__":  # pragma: no cover
    _warn_stale_frontend_dist()
    app.run(debug=True, port=5001)
