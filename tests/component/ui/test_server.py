"""Component tests for src/ui/server.py (AST-394)."""

from __future__ import annotations

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
