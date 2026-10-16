"""Component tests for src/ui/api/api_meteorite.py (AST-1042 → AST-1471 land shape)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from flask.testing import FlaskClient

from ui.api import api_meteorite as meteorite_api
from src.utils.config import METEORITE_CONFIG


def _land_ok(**overrides):
    base = {
        "outcome": METEORITE_CONFIG["land_outcome_created"],
        "outcomes": [{"outcome": METEORITE_CONFIG["land_outcome_created"], "astral_job_id": "j1"}],
        "company": "meteorite-cand-1",
        "company_inserted": True,
        "error": None,
    }
    base.update(overrides)
    return base


def _patch_land(monkeypatch: pytest.MonkeyPatch, result=None, *, side_effect=None):
    """land_meteorite is async; asyncio.run awaits it inside the route."""

    if side_effect is not None:

        async def _boom(*_a, **_k):
            raise side_effect

        monkeypatch.setattr(meteorite_api, "land_meteorite", _boom)
        return

    payload = result if result is not None else _land_ok()

    async def _land(*_a, **_k):
        return payload

    monkeypatch.setattr(meteorite_api, "land_meteorite", _land)


# Branches: legacy /jobs alias → land shape (AST-1471 retarget of AST-1042).
class TestAst1042MeteoriteCreateApi:
    def test_create_ok(
        self, meteorite_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _patch_land(monkeypatch)
        resp = meteorite_client.post(
            "/api/candidates/cand-1/meteorite/jobs",
            headers=auth_headers,
            json={"html_body": "<p>hi</p>"},
        )
        assert resp.status_code == 201
        body = resp.get_json()
        assert body["outcome"] == METEORITE_CONFIG["land_outcome_created"]
        assert body["company"] == "meteorite-cand-1"
        assert body["company_inserted"] is True
        assert body["outcomes"][0]["astral_job_id"] == "j1"

    def test_create_validation_400(
        self, meteorite_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _patch_land(
            monkeypatch,
            side_effect=ValueError("scraps must be a list or None"),
        )
        resp = meteorite_client.post(
            "/api/candidates/cand-1/meteorite/jobs",
            headers=auth_headers,
            json={"scraps": "bad"},
        )
        assert resp.status_code == 400
        assert resp.get_json() == {"error": "scraps must be a list or None"}

    def test_create_candidate_missing_404(
        self, meteorite_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _patch_land(
            monkeypatch,
            _land_ok(
                outcome=METEORITE_CONFIG["land_outcome_error"],
                outcomes=[],
                company=None,
                company_inserted=False,
                error="candidate not found: nope",
            ),
        )
        resp = meteorite_client.post(
            "/api/candidates/nope/meteorite/jobs",
            headers=auth_headers,
            json={"html_body": "<p>x</p>"},
        )
        assert resp.status_code == 404
        body = resp.get_json()
        assert body["outcome"] == METEORITE_CONFIG["land_outcome_error"]
        assert body["error"] == "candidate not found: nope"

    def test_create_upstream_502(
        self, meteorite_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _patch_land(monkeypatch, side_effect=RuntimeError("db down"))
        warn = MagicMock()
        monkeypatch.setattr(meteorite_api.logger, "warning", warn)
        resp = meteorite_client.post(
            "/api/candidates/cand-1/meteorite/jobs",
            headers=auth_headers,
            json={"html_body": "<p>x</p>"},
        )
        assert resp.status_code == 502
        assert resp.get_json() == {"error": "db down"}
        warn.assert_called_once()

    def test_requires_auth(self, meteorite_client: FlaskClient) -> None:
        assert (
            meteorite_client.post(
                "/api/candidates/cand-1/meteorite/jobs",
                json={"html_body": "<p>x</p>"},
            ).status_code
            == 401
        )

    def test_non_admin_allowed(
        self,
        meteorite_client: FlaskClient,
        non_admin_headers: dict[str, str],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        _patch_land(monkeypatch, _land_ok(company_inserted=False))
        resp = meteorite_client.post(
            "/api/candidates/cand-1/meteorite/jobs",
            headers=non_admin_headers,
            json={"html_body": "<p>x</p>"},
        )
        assert resp.status_code == 201


# Branches: /land created/skip/supersede/error; payload scraps; auth (AST-1471).
class TestAst1471MeteoriteLandApi:
    def test_land_created_201(
        self, meteorite_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        seen: dict = {}

        async def _land(cid, **kwargs):
            seen["cid"] = cid
            seen["kwargs"] = kwargs
            return _land_ok()

        monkeypatch.setattr(meteorite_api, "land_meteorite", _land)
        resp = meteorite_client.post(
            "/api/candidates/cand-1/meteorite/land",
            headers=auth_headers,
            json={
                "scraps": [{"text": "JD text", "job_link": "https://x.example/j"}],
                "debug": True,
            },
        )
        assert resp.status_code == 201
        assert seen["cid"] == "cand-1"
        assert seen["kwargs"]["debug"] is True
        assert seen["kwargs"]["scraps"][0]["job_link"] == "https://x.example/j"
        body = resp.get_json()
        assert set(body) >= {"outcome", "outcomes", "company", "company_inserted", "error"}
        assert body["outcome"] == METEORITE_CONFIG["land_outcome_created"]

    def test_land_duplicate_skip_200(
        self, meteorite_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _patch_land(
            monkeypatch,
            _land_ok(
                outcome=METEORITE_CONFIG["land_outcome_duplicate_skip"],
                outcomes=[{
                    "outcome": METEORITE_CONFIG["land_outcome_duplicate_skip"],
                    "astral_job_id": "exist",
                }],
                company_inserted=False,
            ),
        )
        resp = meteorite_client.post(
            "/api/candidates/cand-1/meteorite/land",
            headers=auth_headers,
            json={"text": "again"},
        )
        assert resp.status_code == 200
        assert resp.get_json()["outcome"] == METEORITE_CONFIG["land_outcome_duplicate_skip"]

    def test_land_superseded_200(
        self, meteorite_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _patch_land(
            monkeypatch,
            _land_ok(outcome=METEORITE_CONFIG["land_outcome_superseded"]),
        )
        resp = meteorite_client.post(
            "/api/candidates/cand-1/meteorite/land",
            headers=auth_headers,
            json={"text": "promo"},
        )
        assert resp.status_code == 200
        assert resp.get_json()["outcome"] == METEORITE_CONFIG["land_outcome_superseded"]

    def test_land_error_400(
        self, meteorite_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _patch_land(
            monkeypatch,
            _land_ok(
                outcome=METEORITE_CONFIG["land_outcome_error"],
                outcomes=[],
                error="scraps required (link and/or text)",
                company=None,
                company_inserted=False,
            ),
        )
        resp = meteorite_client.post(
            "/api/candidates/cand-1/meteorite/land",
            headers=auth_headers,
            json={},
        )
        assert resp.status_code == 400
        assert "scraps required" in (resp.get_json().get("error") or "")

    def test_land_requires_auth(self, meteorite_client: FlaskClient) -> None:
        assert (
            meteorite_client.post(
                "/api/candidates/cand-1/meteorite/land",
                json={"text": "x"},
            ).status_code
            == 401
        )


# Branches: list/detail GET; empty honesty; field projection; 404/500; auth; no info log (AST-1748).
class TestAst1748MeteoriteListDetailApi:
    def _row(self, **overrides):
        base = {
            "id": 7,
            "candidate_id": "cand-A",
            "source_kind": "email",
            "source_id": "mid-1",
            "source_ref": None,
            "state": "READY",
            "content": '{"title": "X"}',
            "classify_outcome": "link",
            "link": "not-http",
            "electronic_contact": None,
            "job_title": "Engineer",
            "employer_name": "Acme",
            "astral_job_id": "job-99",
            "error": None,
            "created_at": "2024-01-01T00:00:00+00:00",
            "updated_at": "2024-01-02T00:00:00+00:00",
            "state_changed_at": "2024-01-03T00:00:00+00:00",
            "estelle_notified_at": None,
        }
        base.update(overrides)
        return base

    def test_list_scopes_candidate_and_returns_columns(
        self, meteorite_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import JOBS_METEORITES_LIST_COLUMNS

        seen: dict = {}

        def _list(cid: str):
            seen["cid"] = cid
            return [self._row(candidate_id=cid, id=1), self._row(candidate_id=cid, id=2, content="heavy")]

        monkeypatch.setattr(meteorite_api, "list_meteorites_for_candidate", _list)
        info = MagicMock()
        monkeypatch.setattr(meteorite_api.logger, "info", info)
        resp = meteorite_client.get("/api/candidates/cand-A/meteorites", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.get_json()
        assert seen["cid"] == "cand-A"
        assert body["columns"] == list(JOBS_METEORITES_LIST_COLUMNS)
        assert [m["id"] for m in body["meteorites"]] == [1, 2]
        assert all(m["candidate_id"] == "cand-A" for m in body["meteorites"])
        # List projection omits heavy content
        assert "content" not in body["meteorites"][0]
        assert body["meteorites"][0]["link"] == "not-http"
        assert body["meteorites"][0]["astral_job_id"] == "job-99"
        info.assert_not_called()

    def test_list_projects_landed_job_state_ast1974(
        self, meteorite_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # AST-1974: Meteorites list carries the landed job's current state (null when unlanded).
        rows = [self._row(id=1, job_state="RECOMMENDED"), self._row(id=2, astral_job_id=None, job_state=None)]
        monkeypatch.setattr(meteorite_api, "list_meteorites_for_candidate", lambda _cid: rows)
        body = meteorite_client.get("/api/candidates/cand-A/meteorites", headers=auth_headers).get_json()
        assert [m["job_state"] for m in body["meteorites"]] == ["RECOMMENDED", None]
        assert "job_state" in meteorite_api._LIST_KEYS

    def test_list_projects_landed_job_created_at_ast1980(
        self, meteorite_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # AST-1980 AC 6 / AC 9: list carries job_created_at (null when unlanded) beside the row's own created_at;
        # the success path logs nothing.
        rows = [
            self._row(id=1, job_created_at="2025-06-01T12:00:00+00:00"),
            self._row(id=2, astral_job_id=None, job_created_at=None),
        ]
        monkeypatch.setattr(meteorite_api, "list_meteorites_for_candidate", lambda _cid: rows)
        log = MagicMock()
        monkeypatch.setattr(meteorite_api, "logger", log)
        body = meteorite_client.get("/api/candidates/cand-A/meteorites", headers=auth_headers).get_json()
        assert [m["job_created_at"] for m in body["meteorites"]] == ["2025-06-01T12:00:00+00:00", None]
        assert [m["created_at"] for m in body["meteorites"]] == ["2024-01-01T00:00:00+00:00"] * 2
        assert "job_created_at" in meteorite_api._LIST_KEYS
        for level in ("info", "warning", "error", "exception"):
            getattr(log, level).assert_not_called()

    def test_list_empty_honesty(
        self, meteorite_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(meteorite_api, "list_meteorites_for_candidate", lambda _cid: [])
        resp = meteorite_client.get("/api/candidates/cand-empty/meteorites", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["meteorites"] == []
        assert "columns" in body

    def test_list_requires_auth(self, meteorite_client: FlaskClient) -> None:
        assert meteorite_client.get("/api/candidates/cand-A/meteorites").status_code == 401

    def test_list_500_logs_exception(
        self, meteorite_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            meteorite_api,
            "list_meteorites_for_candidate",
            MagicMock(side_effect=RuntimeError("db down")),
        )
        exc = MagicMock()
        monkeypatch.setattr(meteorite_api.logger, "exception", exc)
        resp = meteorite_client.get("/api/candidates/cand-A/meteorites", headers=auth_headers)
        assert resp.status_code == 500
        assert resp.get_json() == {"error": "meteorite list failed"}
        exc.assert_called_once()

    def test_detail_returns_content_metadata_and_stored_link(
        self, meteorite_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import JOBS_METEORITES_MODAL_SECTIONS

        row = self._row(link="ftp://weird", astral_job_id="")
        monkeypatch.setattr(meteorite_api, "get_meteorite", lambda _mid: row)
        info = MagicMock()
        monkeypatch.setattr(meteorite_api.logger, "info", info)
        resp = meteorite_client.get("/api/meteorites/7", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["sections"] == list(JOBS_METEORITES_MODAL_SECTIONS)
        m = body["meteorite"]
        assert m["content"] == row["content"]
        assert m["state"] == "READY"
        assert m["created_at"] and m["updated_at"] and m["state_changed_at"]
        assert m["link"] == "ftp://weird"  # stored as-is; UI http(s)-gates
        assert m["astral_job_id"] == ""  # blank returned so UI can gate
        assert m["id"] == 7
        assert m["source_kind"] == "email"
        assert m["source_id"] == "mid-1"
        assert m["classify_outcome"] == "link"
        info.assert_not_called()

    def test_detail_404(
        self, meteorite_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(meteorite_api, "get_meteorite", lambda _mid: None)
        exc = MagicMock()
        monkeypatch.setattr(meteorite_api.logger, "exception", exc)
        resp = meteorite_client.get("/api/meteorites/404", headers=auth_headers)
        assert resp.status_code == 404
        assert resp.get_json() == {"error": "meteorite not found"}
        exc.assert_not_called()

    def test_detail_requires_auth(self, meteorite_client: FlaskClient) -> None:
        assert meteorite_client.get("/api/meteorites/7").status_code == 401

    def test_detail_500_logs_exception(
        self, meteorite_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            meteorite_api,
            "get_meteorite",
            MagicMock(side_effect=RuntimeError("db down")),
        )
        exc = MagicMock()
        monkeypatch.setattr(meteorite_api.logger, "exception", exc)
        resp = meteorite_client.get("/api/meteorites/7", headers=auth_headers)
        assert resp.status_code == 500
        assert resp.get_json() == {"error": "meteorite detail failed"}
        exc.assert_called_once()


# Branches: detail edit envelope; PUT map; completing info on 200 only (AST-2223).
class TestAst2223CandidateMeteoriteEditApi:
    """AST-2223: GET edit envelope + PUT candidate overwrite."""

    def _insert(self, db, cid: str, **fields: object) -> int:
        row_id = db.insert_meteorite_rows(
            [
                {
                    "candidate_id": cid,
                    "source_kind": "email",
                    "source_id": fields.get("source_id") or f"mid-{cid}",
                    "content": fields.get("content") or ("seed " + ("x" * 40)),
                    "state": str(fields.get("state") or "READY"),
                }
            ]
        )[0]
        extra = {
            k: fields[k]
            for k in ("content", "link", "job_title", "employer_name", "error", "electronic_contact")
            if k in fields and fields[k] is not None
        }
        state = fields.get("state")
        if state and state != "NEW":
            db.update_meteorite(row_id, state=str(state), **extra)
        elif extra:
            db.update_meteorite(row_id, **extra)
        return row_id

    def _body(self, **overrides) -> dict:
        from src.utils.config import CANDIDATE_METEORITE_EDIT_CONFIG, METEORITE_CONFIG

        col = METEORITE_CONFIG["electronic_contact_column"]
        base = {
            "state": CANDIDATE_METEORITE_EDIT_CONFIG["default_save_state"],
            "content": "API edited JD " + ("y" * 40),
            "link": "https://api.example/j",
            "job_title": "API Title",
            "employer_name": "API Co",
            col: "api@example.com",
        }
        base.update(overrides)
        return base

    def test_detail_envelope_from_config(
        self, meteorite_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import CANDIDATE_METEORITE_EDIT_CONFIG

        row = {
            "id": 7,
            "candidate_id": "cand-A",
            "source_kind": "email",
            "source_id": "mid-1",
            "source_ref": None,
            "state": "READY",
            "content": "body",
            "classify_outcome": None,
            "link": None,
            "electronic_contact": None,
            "job_title": None,
            "employer_name": None,
            "astral_job_id": None,
            "error": None,
            "created_at": "2024-01-01T00:00:00+00:00",
            "updated_at": "2024-01-02T00:00:00+00:00",
            "state_changed_at": "2024-01-03T00:00:00+00:00",
            "estelle_notified_at": None,
        }
        monkeypatch.setattr(meteorite_api, "get_meteorite", lambda _mid: row)
        info = MagicMock()
        monkeypatch.setattr(meteorite_api.logger, "info", info)
        resp = meteorite_client.get("/api/meteorites/7", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["editable"] is True
        assert body["editable_fields"] == list(CANDIDATE_METEORITE_EDIT_CONFIG["editable_fields"])
        assert body["state_options"] == list(CANDIDATE_METEORITE_EDIT_CONFIG["state_options"])
        assert body["default_save_state"] == "CHECK_UNIQUE"
        info.assert_not_called()

        monkeypatch.setattr(meteorite_api, "get_meteorite", lambda _mid: {**row, "state": "LANDED"})
        landed = meteorite_client.get("/api/meteorites/7", headers=auth_headers).get_json()
        assert landed["editable"] is False
        assert landed["default_save_state"] == "CHECK_UNIQUE"

    def test_put_default_and_pick_list_state_persist(
        self,
        meteorite_client: FlaskClient,
        auth_headers: dict[str, str],
        seeded_db,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from src.core import meteorite as core_mod

        stage = MagicMock()
        do_task = MagicMock()
        monkeypatch.setattr(core_mod, "stage_meteorite", stage)
        monkeypatch.setattr("src.core.agent.do_task", do_task)
        if hasattr(core_mod, "run_scrape_meteorite"):
            monkeypatch.setattr(core_mod, "run_scrape_meteorite", MagicMock())
        monkeypatch.setattr(core_mod, "get_visible_text", MagicMock())

        mid = self._insert(seeded_db, "cand-1", state="READY", content="old " + ("z" * 40))
        info = MagicMock()
        monkeypatch.setattr(meteorite_api.logger, "info", info)

        resp = meteorite_client.put(
            f"/api/meteorites/{mid}", headers=auth_headers, json=self._body(state="CHECK_UNIQUE")
        )
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["meteorite"]["state"] == "CHECK_UNIQUE"
        assert seeded_db.get_meteorite(mid)["state"] == "CHECK_UNIQUE"
        assert body["editable"] is True
        assert body["default_save_state"] == "CHECK_UNIQUE"
        info.assert_called_once()
        assert info.call_args[0][0] == "%s | api %s completed: PUT %s"
        assert info.call_args[0][1] == "cand-1"
        assert info.call_args[0][2] == f"/api/meteorites/{mid}"
        assert info.call_args[0][3] == 200
        stage.assert_not_called()
        do_task.assert_not_called()

        info.reset_mock()
        resp2 = meteorite_client.put(
            f"/api/meteorites/{mid}",
            headers=auth_headers,
            json=self._body(state="READY", content="Second API edit " + ("w" * 40)),
        )
        assert resp2.status_code == 200
        assert seeded_db.get_meteorite(mid)["state"] == "READY"
        info.assert_called_once()

    def test_put_all_fields_and_error_clear(
        self, meteorite_client: FlaskClient, auth_headers: dict[str, str], seeded_db
    ) -> None:
        from src.utils.config import METEORITE_CONFIG

        col = METEORITE_CONFIG["electronic_contact_column"]
        mid = self._insert(
            seeded_db,
            "cand-1",
            state="READY",
            content="old " + ("a" * 40),
            error="prior",
            link="https://old",
            job_title="Old",
            employer_name="OldCo",
            electronic_contact="old@ex.com",
        )
        resp = meteorite_client.put(
            f"/api/meteorites/{mid}",
            headers=auth_headers,
            json=self._body(
                state="CHECK_UNIQUE",
                content="  New content " + ("b" * 40) + "  ",
                link="  https://new  ",
                job_title="  NT  ",
                employer_name="  NC  ",
                **{col: "  n@ex.com  "},
            ),
        )
        assert resp.status_code == 200
        row = seeded_db.get_meteorite(mid)
        assert row["content"] == "New content " + ("b" * 40)
        assert row["link"] == "https://new"
        assert row["job_title"] == "NT"
        assert row["employer_name"] == "NC"
        assert row[col] == "n@ex.com"
        assert not row.get("error")

        mid2 = self._insert(
            seeded_db, "cand-1", state="READY", content="same " + ("c" * 40), error="keep",
            source_id="mid-same-state",
        )
        resp2 = meteorite_client.put(
            f"/api/meteorites/{mid2}",
            headers=auth_headers,
            json=self._body(state="READY", content="same " + ("c" * 40)),
        )
        assert resp2.status_code == 200
        assert seeded_db.get_meteorite(mid2)["error"] == "keep"

    def test_put_refuse_gates(
        self, meteorite_client: FlaskClient, auth_headers: dict[str, str], seeded_db
    ) -> None:
        mid = self._insert(seeded_db, "cand-1", state="READY", content="gate " + ("d" * 40))

        bad = self._body()
        bad["candidate_id"] = "nope"
        r = meteorite_client.put(f"/api/meteorites/{mid}", headers=auth_headers, json=bad)
        assert r.status_code == 400
        assert r.get_json() == {"error": "one or more fields are not editable"}
        assert seeded_db.get_meteorite(mid)["content"].startswith("gate ")

        landed = self._insert(
            seeded_db, "cand-1", state="LANDED", content="landed " + ("e" * 40), source_id="mid-landed"
        )
        r2 = meteorite_client.put(f"/api/meteorites/{landed}", headers=auth_headers, json=self._body())
        assert r2.status_code == 409
        assert "landed" in r2.get_json()["error"]

        r3 = meteorite_client.put(
            f"/api/meteorites/{mid}", headers=auth_headers, json=self._body(state="LANDED")
        )
        assert r3.status_code == 400
        assert "pick-list" in r3.get_json()["error"]

        # Dedicated candidate so claim cannot steal the gate row above.
        seeded_db.save_candidate("cand-claim", state="NEW_CANDIDATE", candidate_data={"name": "C"})
        held = self._insert(
            seeded_db, "cand-claim", state="READY", content="claimed " + ("f" * 40), source_id="mid-claim"
        )
        assert seeded_db.claim_meteorite_batch(
            "api-claim-2223", "READY", 1, candidate_id="cand-claim"
        ) == 1
        before = dict(seeded_db.get_meteorite(held))
        r4 = meteorite_client.put(f"/api/meteorites/{held}", headers=auth_headers, json=self._body())
        assert r4.status_code == 409
        assert "claimed" in r4.get_json()["error"]
        assert seeded_db.get_meteorite(held)["content"] == before["content"]

        free = self._insert(
            seeded_db, "cand-1", state="NEW", content="free " + ("g" * 40), source_id="mid-free"
        )
        r5 = meteorite_client.put(
            f"/api/meteorites/{free}", headers=auth_headers, json=self._body(content="   ")
        )
        assert r5.status_code == 400
        assert "empty" in r5.get_json()["error"]
        assert seeded_db.get_meteorite(free)["content"].startswith("free ")

        r6 = meteorite_client.put("/api/meteorites/999999", headers=auth_headers, json=self._body())
        assert r6.status_code == 404

    def test_put_requires_auth(self, meteorite_client: FlaskClient, seeded_db) -> None:
        mid = self._insert(seeded_db, "cand-1", state="READY", content="auth " + ("h" * 40))
        assert meteorite_client.put(f"/api/meteorites/{mid}", json=self._body()).status_code == 401

    def test_put_non_json_400(
        self, meteorite_client: FlaskClient, auth_headers: dict[str, str], seeded_db
    ) -> None:
        mid = self._insert(seeded_db, "cand-1", state="READY", content="json " + ("i" * 40))
        resp = meteorite_client.put(
            f"/api/meteorites/{mid}",
            headers={**auth_headers, "Content-Type": "application/json"},
            data="not-json",
        )
        assert resp.status_code == 400
        assert resp.get_json() == {"error": "JSON object required"}
