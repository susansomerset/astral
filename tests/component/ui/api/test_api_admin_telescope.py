"""AST-1728 bug-repro — admin Telescope API / nav / drop-in helper (pre-fix red)."""

from __future__ import annotations

from pathlib import Path

import pytest
from flask.testing import FlaskClient


_REPO = Path(__file__).resolve().parents[4]


class TestAst1728AdminTelescopeRepro:
    """Board REVISE: POST /api/admin/telescope + admin_telescope_scrape + nav + page."""

    def test_admin_telescope_page_module_exists(self) -> None:
        path = _REPO / "src" / "ui" / "frontend" / "src" / "pages" / "AdminTelescope.tsx"
        assert path.is_file(), (
            "AST-1728: missing AdminTelescope.tsx — admin workbench page not landed"
        )

    def test_routes_register_admin_telescope(self) -> None:
        routes = (_REPO / "src" / "ui" / "frontend" / "src" / "routes.tsx").read_text(
            encoding="utf-8"
        )
        assert "admin/telescope" in routes, (
            "AST-1728: routes.tsx must register path admin/telescope"
        )
        assert "AdminTelescope" in routes

    def test_nav_tools_includes_telescope(self) -> None:
        from src.utils import config as cfg

        tools = next(g for g in cfg.NAV_CONFIG if g.get("label") == "Tools")
        labels = [item.get("label") for item in tools.get("items") or []]
        assert "Telescope" in labels, (
            "AST-1728: NAV_CONFIG Tools must include Telescope → /admin/telescope"
        )
        path = next(
            item["path"]
            for item in tools["items"]
            if item.get("label") == "Telescope"
        )
        assert path == "/admin/telescope"

    def test_admin_telescope_scrape_helper_exists(self) -> None:
        from src.external import telescope as tel

        assert hasattr(tel, "admin_telescope_scrape"), (
            "AST-1728: src.external.telescope.admin_telescope_scrape missing"
        )

    def test_post_api_admin_telescope_route_exists(
        self, admin_client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        resp = admin_client.post(
            "/api/admin/telescope",
            headers=auth_headers,
            json={
                "url": "https://example.com",
                "response_type": "text",
            },
        )
        # Pre-fix: unknown route → 404. Post-fix: not 404 (200/400/502 ok).
        assert resp.status_code != 404, (
            "AST-1728: POST /api/admin/telescope must be registered"
        )
