"""Component tests for src/ui/server.py (AST-394)."""

from __future__ import annotations

from flask.testing import FlaskClient


class TestServeReact:
    def test_serves_index_for_allowed_ip(self, server_client: FlaskClient) -> None:
        resp = server_client.get("/")
        assert resp.status_code == 200
        assert b"ok" in resp.data

    def test_blocks_disallowed_ip(self, server_client: FlaskClient, monkeypatch) -> None:
        import ui.server as server_mod

        monkeypatch.setattr(server_mod, "is_ip_allowed", lambda: False)
        resp = server_client.get("/")
        assert resp.status_code == 403
        assert b"Astral" in resp.data

    def test_serves_static_asset_when_path_exists(self, server_client: FlaskClient, monkeypatch) -> None:
        import ui.server as server_mod

        (server_mod._DIST / "asset.txt").write_text("asset", encoding="utf-8")
        resp = server_client.get("/asset.txt")
        assert resp.status_code == 200
        assert resp.data == b"asset"
