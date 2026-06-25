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
