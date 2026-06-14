"""board_search DDL + REST (AST-458) + workflow `state` ACTIVE|INACTIVE|ERROR (AST-471) + gaze `last_scan_at` cadence (AST-482)."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict

_SRC = Path(__file__).resolve().parents[4] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import pytest
from flask import Flask
from flask.testing import FlaskClient

from src.core import boards as boards_mod
from src.utils.config import BOARD_SEARCH_STATES


# Entry netloc boards.example matches deeplink URLs in these tests (see DEMO_BOARD).
AUTH_HEADERS = {"Authorization": "Bearer test-token"}

DEMO_BOARD: Dict[str, object] = {
    "tst": {
        "label": "Test board",
        "entry_url": "https://boards.example/start",
        "adopted": True,
        "craft_task_key": "craft_board_search_criteria",
        "scrape_mode": "deep_link",
        "parse_instructions": {"job_title": "h2", "job_link": "http"},
        "criteria_param_map": {},
        "title_patterns": [],
    },
}


@pytest.fixture
def board_search_http_client(seeded_db, monkeypatch: pytest.MonkeyPatch) -> FlaskClient:
    """Real SQLite candidate `cand-1` + boards REST blueprint."""
    from src.utils import auth as utils_auth

    utils_auth._authenticate = None

    def _mock(token: str) -> dict:
        if token == "test-token":
            return {"user_id": "susan", "name": "Susan", "email": "susan@susansomerset.com"}
        raise ValueError("invalid token")

    utils_auth.register_token_authenticator(_mock)
    monkeypatch.setattr(boards_mod, "BOARD_CONFIG", DEMO_BOARD)
    monkeypatch.setattr("src.data.database.DB_PATH", seeded_db.DB_PATH)

    app = Flask(__name__)
    from ui.api.api_boards import boards_bp

    app.register_blueprint(boards_bp)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestBoardDeeplinkNormalize:
    """Direct coverage of normalization helper (fingerprints duplicates)."""

    def test_sorts_query_params_and_lowercases_scheme_host(self) -> None:
        u = boards_mod._normalize_board_deeplink_url("HTTPS://Boards.EXAMPLE/job?z=9&a=1&a=2")
        assert u == "https://boards.example/job?a=1&a=2&z=9"

    def test_root_path_normalizes_slash(self) -> None:
        u = boards_mod._normalize_board_deeplink_url("https://boards.example")
        assert u == "https://boards.example/"

    def test_rejects_missing_scheme(self) -> None:
        with pytest.raises(ValueError, match="scheme"):
            boards_mod._normalize_board_deeplink_url("//boards.example/x")

    def test_rejects_blank(self) -> None:
        with pytest.raises(ValueError, match="required"):
            boards_mod._normalize_board_deeplink_url("   ")


class TestBoardSearchRestAst458:
    def test_list_requires_candidate_id(self, board_search_http_client: FlaskClient) -> None:
        r = board_search_http_client.get("/api/boards/searches", headers=AUTH_HEADERS)
        assert r.status_code == 400

    def test_post_criteria_mode_round_trip(self, board_search_http_client: FlaskClient) -> None:
        resp = board_search_http_client.post(
            "/api/boards/searches",
            headers=AUTH_HEADERS,
            json={
                "candidate_id": "cand-1",
                "board_key": "tst",
                "label": "One",
                "criteria": {"title_query": "dev"},
            },
        )
        assert resp.status_code == 201
        body = resp.get_json()
        assert body["mode"] == "criteria"
        assert body.get("state") == BOARD_SEARCH_STATES[0]
        assert body["deeplink_url"] is None
        assert body["criteria"]["title_query"] == "dev"

        bid = body["board_search_id"]
        listing = board_search_http_client.get(
            "/api/boards/searches",
            headers=AUTH_HEADERS,
            query_string={"candidate_id": "cand-1"},
        )
        ids = [x["board_search_id"] for x in listing.get_json()]
        assert bid in ids

        got = board_search_http_client.get(f"/api/boards/searches/{bid}", headers=AUTH_HEADERS)
        assert got.status_code == 200
        assert got.get_json()["label"] == "One"

    def test_post_duplicate_criteria_rejected_with_409(self, board_search_http_client: FlaskClient) -> None:
        base = {"candidate_id": "cand-1", "board_key": "tst", "label": "Dup", "criteria": {"same": True}}
        assert board_search_http_client.post("/api/boards/searches", headers=AUTH_HEADERS, json=base).status_code == 201
        r2 = board_search_http_client.post("/api/boards/searches", headers=AUTH_HEADERS, json=dict(base, label="Other"))
        assert r2.status_code == 409
        assert "duplicate" in r2.get_json()["error"].lower()

    def test_duplicate_ignores_key_order_in_criteria_json(self, board_search_http_client: FlaskClient) -> None:
        ok = board_search_http_client.post(
            "/api/boards/searches",
            headers=AUTH_HEADERS,
            json={
                "candidate_id": "cand-1",
                "board_key": "tst",
                "label": "order-a",
                "criteria": {"y": 1, "z": 2},
            },
        )
        assert ok.status_code == 201
        conflict = board_search_http_client.post(
            "/api/boards/searches",
            headers=AUTH_HEADERS,
            json={
                "candidate_id": "cand-1",
                "board_key": "tst",
                "label": "order-b",
                "criteria": {"z": 2, "y": 1},
            },
        )
        assert conflict.status_code == 409

    def test_post_deeplink_matching_domain_returns_201(self, board_search_http_client: FlaskClient) -> None:
        resp = board_search_http_client.post(
            "/api/boards/searches",
            headers=AUTH_HEADERS,
            json={
                "candidate_id": "cand-1",
                "board_key": "tst",
                "label": "Deep",
                "mode": "deeplink",
                "deeplink_url": "https://boards.example/results?view=all",
            },
        )
        assert resp.status_code == 201
        body = resp.get_json()
        assert body["mode"] == "deeplink"
        assert body["criteria"] == {}
        assert body["deeplink_url"].startswith("https://boards.example/")

    def test_deeplink_duplicate_after_query_normalize(self, board_search_http_client: FlaskClient) -> None:
        payload = {
            "candidate_id": "cand-1",
            "board_key": "tst",
            "label": "q1",
            "mode": "deeplink",
            "deeplink_url": "https://boards.example/results?b=2&a=1",
        }
        assert board_search_http_client.post("/api/boards/searches", headers=AUTH_HEADERS, json=payload).status_code == 201
        dup = board_search_http_client.post(
            "/api/boards/searches",
            headers=AUTH_HEADERS,
            json=dict(payload, label="q2", deeplink_url="https://boards.example/results?a=1&b=2"),
        )
        assert dup.status_code == 409

    def test_wrong_domain_deeplink_400(self, board_search_http_client: FlaskClient) -> None:
        r = board_search_http_client.post(
            "/api/boards/searches",
            headers=AUTH_HEADERS,
            json={
                "candidate_id": "cand-1",
                "board_key": "tst",
                "label": "wrong",
                "mode": "deeplink",
                "deeplink_url": "https://evil.example/board",
            },
        )
        assert r.status_code == 400

    def test_post_rejects_credentials_in_body(self, board_search_http_client: FlaskClient) -> None:
        r = board_search_http_client.post(
            "/api/boards/searches",
            headers=AUTH_HEADERS,
            json={
                "candidate_id": "cand-1",
                "board_key": "tst",
                "label": "bad",
                "criteria": {"token": "nope"},
            },
        )
        assert r.status_code == 400

    def test_post_rejects_legacy_enabled_field(self, board_search_http_client: FlaskClient) -> None:
        r = board_search_http_client.post(
            "/api/boards/searches",
            headers=AUTH_HEADERS,
            json={
                "candidate_id": "cand-1",
                "board_key": "tst",
                "label": "legacy",
                "criteria": {},
                "enabled": True,
            },
        )
        assert r.status_code == 400
        assert "enabled" in r.get_json()["error"].lower()

    def test_patch_state_inactive_then_mode_switch_to_criteria(self, board_search_http_client: FlaskClient) -> None:
        cre = board_search_http_client.post(
            "/api/boards/searches",
            headers=AUTH_HEADERS,
            json={
                "candidate_id": "cand-1",
                "board_key": "tst",
                "label": "Switch",
                "mode": "deeplink",
                "deeplink_url": "https://boards.example/original",
            },
        )
        assert cre.status_code == 201
        bid = cre.get_json()["board_search_id"]

        p1 = board_search_http_client.patch(
            f"/api/boards/searches/{bid}",
            headers=AUTH_HEADERS,
            json={"state": BOARD_SEARCH_STATES[1]},
        )
        assert p1.status_code == 200
        assert p1.get_json().get("state") == BOARD_SEARCH_STATES[1]

        p2 = board_search_http_client.patch(
            f"/api/boards/searches/{bid}",
            headers=AUTH_HEADERS,
            json={
                "mode": "criteria",
                "criteria": {"title_query": "x"},
            },
        )
        assert p2.status_code == 200
        out = p2.get_json()
        assert out["mode"] == "criteria"
        assert out["deeplink_url"] is None


class TestClaimBoardSearchSqlShape:
    """Sanity-check claim SQL selects ACTIVE rows with clear batch_id only (§2.4 AST-471)."""

    def test_claim_returns_empty_when_none_active(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_candidate("cand-claim", state="NEW", candidate_data={})
        claimed = db.claim_board_search_batch("batch-z", limit=5, candidate_id="cand-claim")
        assert claimed == []

    def test_claim_skips_inactive_only_active_claimed(self, sqlite_in_memory) -> None:
        import json

        db = sqlite_in_memory
        db.save_candidate("cand-claim", state="NEW", candidate_data={})
        act, inactive, _err = BOARD_SEARCH_STATES
        crit = json.dumps({"k": True})
        db.save_board_search_row("bs-act", "cand-claim", "tst", "A", crit, state=act)
        db.save_board_search_row("bs-off", "cand-claim", "tst", "B", crit, state=inactive)
        claimed = db.claim_board_search_batch("batch-z", limit=5, candidate_id="cand-claim")
        assert [r["board_search_id"] for r in claimed] == ["bs-act"]


class TestBoardSearchLastScanCadenceAst482:
    """`claim_board_search_batch` staleness gate + `count_eligible_for_dispatch_task` parity (AST-482)."""

    @staticmethod
    def _prime_active(db: object, cid: str, bs_id: str) -> None:
        import json

        act = BOARD_SEARCH_STATES[0]
        crit = json.dumps({"z": True})
        db.save_board_search_row(bs_id, cid, "tst", bs_id, crit, state=act)

    def _exec(self, db: object, sql: str, params: tuple = ()) -> None:
        conn = db._get_connection()
        try:
            conn.execute(sql, params)
            conn.commit()
        finally:
            conn.close()

    def test_claim_skips_fresh_last_scan_within_interval(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_candidate("cand-fresh", state="NEW", candidate_data={})
        self._prime_active(db, "cand-fresh", "bs-fresh")
        # Scanned within the last hour — stale gate at 24h should exclude this row from claim.
        self._exec(
            db,
            "UPDATE board_search SET last_scan_at = datetime('now', '-30 minutes') WHERE board_search_id = ?",
            ("bs-fresh",),
        )
        claimed = db.claim_board_search_batch(
            "b1", limit=10, candidate_id="cand-fresh", scan_interval_hours=24.0
        )
        assert claimed == []

    def test_claim_includes_null_and_stale_last_scan(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_candidate("cand-two", state="NEW", candidate_data={})
        self._prime_active(db, "cand-two", "bs-null")
        self._prime_active(db, "cand-two", "bs-stale")
        self._exec(
            db,
            "UPDATE board_search SET last_scan_at = datetime('now', '-48 hours') WHERE board_search_id = ?",
            ("bs-stale",),
        )
        claimed = db.claim_board_search_batch(
            "b2", limit=10, candidate_id="cand-two", scan_interval_hours=24.0, sort_by="last_scan_at"
        )
        assert {r["board_search_id"] for r in claimed} == {"bs-null", "bs-stale"}

    def test_count_eligible_matches_claim_predicate(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        cid = "cand-par"
        db.save_candidate(cid, state="NEW", candidate_data={})
        self._prime_active(db, cid, "p-null")
        self._prime_active(db, cid, "p-stale")
        self._prime_active(db, cid, "p-fresh")
        self._exec(
            db,
            """UPDATE board_search SET last_scan_at = datetime('now', '-96 hours')
               WHERE board_search_id = ?""",
            ("p-stale",),
        )
        self._exec(
            db,
            "UPDATE board_search SET last_scan_at = datetime('now', '-30 minutes') WHERE board_search_id = ?",
            ("p-fresh",),
        )

        task = {
            "entity_type": "board_search",
            "trigger_state": "ACTIVE",
            "candidate_id": cid,
            "task_key": "gaze_board",
            "freq_hrs": 0,
        }
        n = db.count_eligible_for_dispatch_task(task)
        assert n == 2

        ids = {
            r["board_search_id"]
            for r in db.claim_board_search_batch("b-par", limit=99, candidate_id=cid, scan_interval_hours=24.0)
        }
        assert ids == {"p-null", "p-stale"}

    def test_freq_hours_override_matches_count(self, sqlite_in_memory) -> None:
        """dispatch_task.freq_hrs > 0 tightens staleness alongside count_eligible (AST-482)."""
        db = sqlite_in_memory
        cid = "cand-fr"
        db.save_candidate(cid, state="NEW", candidate_data={})
        self._prime_active(db, cid, "fq-a")
        # 30 minutes ago: stale vs 24h default, fresh vs 1h freq override.
        self._exec(
            db,
            "UPDATE board_search SET last_scan_at = datetime('now', '-30 minutes') WHERE board_search_id = ?",
            ("fq-a",),
        )

        task = {
            "entity_type": "board_search",
            "trigger_state": "ACTIVE",
            "candidate_id": cid,
            "task_key": "gaze_board",
            "freq_hrs": 1,
        }
        assert db.count_eligible_for_dispatch_task(task) == 0
        assert db.claim_board_search_batch(
            "b-fq",
            limit=10,
            candidate_id=cid,
            scan_interval_hours=1.0,
        ) == []

        # Clearing scan time restores eligibility while still using the tightened override.
        self._exec(db, "UPDATE board_search SET last_scan_at = NULL WHERE board_search_id = ?", ("fq-a",))
        assert db.count_eligible_for_dispatch_task(task) == 1
