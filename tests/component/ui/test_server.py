"""Component tests for src/ui/server.py (AST-394)."""

from __future__ import annotations

import os
import time

import pytest
from flask.testing import FlaskClient


class TestServeReact:
    def test_serves_index_for_allowed_ip(self, server_client: FlaskClient) -> None:
        resp = server_client.get("/")
        assert resp.status_code == 200
        assert b"ok" in resp.data

    def test_serves_index_when_ip_allowlist_restricted(
        self, server_client: FlaskClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """AST-611: SPA no longer IP-gated; auth enforced on /api/* only."""
        import ui.auth as auth_mod

        auth_mod._ALLOWED_IPS = set()
        monkeypatch.setenv("ASTRAL_ALLOWED_IPS", "203.0.113.1")
        resp = server_client.get("/", environ_base={"REMOTE_ADDR": "198.51.100.2"})
        assert resp.status_code == 200
        assert b"ok" in resp.data

    def test_serves_static_asset_when_path_exists(self, server_client: FlaskClient, monkeypatch) -> None:
        import ui.server as server_mod

        (server_mod._DIST / "asset.txt").write_text("asset", encoding="utf-8")
        resp = server_client.get("/asset.txt")
        assert resp.status_code == 200
        assert resp.data == b"asset"


class TestWarnStaleFrontendDist:
    def test_warns_when_dist_missing(self, tmp_path, capsys: pytest.CaptureFixture[str]) -> None:
        import ui.server as server_mod

        src = tmp_path / "src"
        src.mkdir()
        (src / "App.tsx").write_text("x", encoding="utf-8")
        dist = tmp_path / "dist"
        dist.mkdir()
        server_mod._FRONTEND_SRC = src
        server_mod._DIST = dist
        server_mod._warn_stale_frontend_dist()
        err = capsys.readouterr().err
        assert "frontend/dist missing" in err

    def test_warns_when_src_newer_than_dist(self, tmp_path, capsys: pytest.CaptureFixture[str]) -> None:
        import ui.server as server_mod

        src = tmp_path / "src"
        src.mkdir()
        tsx = src / "App.tsx"
        tsx.write_text("x", encoding="utf-8")
        dist = tmp_path / "dist"
        dist.mkdir()
        dist_index = dist / "index.html"
        dist_index.write_text("old", encoding="utf-8")
        now = time.time()
        os.utime(dist_index, (now - 120, now - 120))
        os.utime(tsx, (now, now))
        server_mod._FRONTEND_SRC = src
        server_mod._DIST = dist
        server_mod._warn_stale_frontend_dist()
        err = capsys.readouterr().err
        assert "frontend/dist older than src/" in err

    def test_silent_when_dist_is_fresh(self, tmp_path, capsys: pytest.CaptureFixture[str]) -> None:
        import ui.server as server_mod

        src = tmp_path / "src"
        src.mkdir()
        tsx = src / "App.tsx"
        tsx.write_text("x", encoding="utf-8")
        dist = tmp_path / "dist"
        dist.mkdir()
        dist_index = dist / "index.html"
        dist_index.write_text("ok", encoding="utf-8")
        now = time.time()
        os.utime(tsx, (now - 120, now - 120))
        os.utime(dist_index, (now, now))
        server_mod._FRONTEND_SRC = src
        server_mod._DIST = dist
        server_mod._warn_stale_frontend_dist()
        assert capsys.readouterr().err == ""


def _vite_proxies(text: str, prefix: str) -> bool:
    target = "http://localhost:5001"
    return f"'{prefix}': '{target}'" in text or f'"{prefix}": "{target}"' in text


class TestAst1117CandidateSpaGuard:
    """AST-1117 / AST-1435: print-HTML prefixes JSON-404; candidate SPA paths get index.html."""

    def test_candidate_backstory_serves_index(self, server_client: FlaskClient) -> None:
        # AST-1435 [bug-repro]: document GET of a candidate SPA route must not be JSON 404.
        resp = server_client.get("/candidate/backstory")
        assert resp.status_code == 200
        assert b"ok" in resp.data
        assert not resp.is_json

    def test_candidate_prefix_spa_routes_serve_index(self, server_client: FlaskClient) -> None:
        resp = server_client.get("/candidate/not-a-real-html-route")
        assert resp.status_code == 200
        assert b"ok" in resp.data

    def test_candidate_exact_path_serves_index(self, server_client: FlaskClient) -> None:
        resp = server_client.get("/candidate")
        assert resp.status_code == 200
        assert b"ok" in resp.data

    def test_unmatched_print_resume_prefix_returns_404_json(
        self, server_client: FlaskClient
    ) -> None:
        # Blueprint owns /candidate/resume/base and /candidate/resume/<job_id> only.
        resp = server_client.get("/candidate/resume")
        assert resp.status_code == 404
        assert resp.get_json() == {"error": "Not found"}

    def test_unmatched_print_cover_prefix_returns_404_json(
        self, server_client: FlaskClient
    ) -> None:
        resp = server_client.get("/candidate/cover")
        assert resp.status_code == 404
        assert resp.get_json() == {"error": "Not found"}

    def test_non_candidate_spa_fallback_still_serves_index(
        self, server_client: FlaskClient
    ) -> None:
        resp = server_client.get("/jobs/recommended")
        assert resp.status_code == 200
        assert b"ok" in resp.data


class TestAst1117ViteCandidateProxy:
    """AST-1117 / AST-1435: Vite proxies print HTML prefixes only — not candidate SPA routes."""

    def test_vite_config_proxies_print_html_not_candidate_spa(self) -> None:
        from pathlib import Path

        text = (
            Path(__file__).resolve().parents[3]
            / "src/ui/frontend/vite.config.ts"
        ).read_text(encoding="utf-8")
        assert _vite_proxies(text, "/api")
        assert _vite_proxies(text, "/candidate/resume")
        assert _vite_proxies(text, "/candidate/cover")
        # Blanket /candidate would steal SPA routes (backstory, profile, …) from Vite.
        assert not _vite_proxies(text, "/candidate")
