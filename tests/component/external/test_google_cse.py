"""Component tests for src/external/google_cse.py (AST-489)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from src.external import google_cse as google_cse_mod


def _fake_response(ok: bool, *, status: int = 200, payload: object | None = None, raw_text: str = "") -> MagicMock:
    """Build a minimal requests.Response-shaped mock."""

    rsp = MagicMock()
    rsp.ok = ok
    rsp.status_code = status
    if raw_text:
        rsp.text = raw_text
    elif payload is Ellipsis:
        rsp.text = "<<<invalid>>>"
    else:
        rsp.text = json.dumps(payload) if payload is not None else "{}"
    if payload is Ellipsis:

        def _bad_json():  # noqa: ANN001
            raise ValueError("not json")

        rsp.json.side_effect = _bad_json
    elif isinstance(payload, Exception):
        rsp.json.side_effect = payload
    else:
        rsp.json.return_value = payload
    return rsp


@pytest.fixture(autouse=True)
def google_cse_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GOOGLE_CSE_API_KEY", "fake-key")
    monkeypatch.setenv("GOOGLE_CSE_ID", "fake-cx")


# --- search_google_cse: credentials / query ---
class TestGoogleCseSearchGoogleCse:
    def test_missing_api_key_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("GOOGLE_CSE_API_KEY", raising=False)
        with pytest.raises(RuntimeError, match="missing environment variable 'GOOGLE_CSE_API_KEY'"):
            google_cse_mod.search_google_cse("test")

    def test_missing_cx_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("GOOGLE_CSE_ID", raising=False)
        with pytest.raises(RuntimeError, match="missing environment variable 'GOOGLE_CSE_ID'"):
            google_cse_mod.search_google_cse("test")

    def test_blank_query_raises(self) -> None:
        with pytest.raises(ValueError, match="empty query"):
            google_cse_mod.search_google_cse("   ")

    def test_days_must_be_positive(self) -> None:
        with pytest.raises(ValueError, match="days must be a positive integer"):
            google_cse_mod.search_google_cse("q", days=0)

    def test_date_restrict_passed_when_days_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        payload = {"items": [{"title": "A", "link": "https://a", "snippet": "s"}]}
        rsp = _fake_response(True, payload=payload)
        get = MagicMock(return_value=rsp)
        monkeypatch.setattr(google_cse_mod.requests, "get", get)
        google_cse_mod.search_google_cse("q", days=30)
        assert get.call_args.kwargs["params"]["dateRestrict"] == "d30"

    def test_http_error_includes_body_snippet(self, monkeypatch: pytest.MonkeyPatch) -> None:
        body = "x" * 600
        rsp = _fake_response(False, status=500, raw_text=body)
        monkeypatch.setattr(google_cse_mod.requests, "get", MagicMock(return_value=rsp))
        with pytest.raises(RuntimeError, match=r"Google CSE HTTP 500"):
            google_cse_mod.search_google_cse("q")

    def test_non_json_body_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        rsp = _fake_response(True, payload=Ellipsis)
        monkeypatch.setattr(google_cse_mod.requests, "get", MagicMock(return_value=rsp))
        with pytest.raises(RuntimeError, match="not valid JSON"):
            google_cse_mod.search_google_cse("q")

    def test_json_root_not_object_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        rsp = _fake_response(True, payload=[])
        monkeypatch.setattr(google_cse_mod.requests, "get", MagicMock(return_value=rsp))
        with pytest.raises(RuntimeError, match="not an object"):
            google_cse_mod.search_google_cse("q")

    def test_api_error_object_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        rsp = _fake_response(True, payload={"error": {"message": "quota", "code": 403}})
        monkeypatch.setattr(google_cse_mod.requests, "get", MagicMock(return_value=rsp))
        with pytest.raises(RuntimeError, match="Google CSE API error: quota"):
            google_cse_mod.search_google_cse("q")

    def test_items_not_list_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        rsp = _fake_response(True, payload={"items": {}})
        monkeypatch.setattr(google_cse_mod.requests, "get", MagicMock(return_value=rsp))
        with pytest.raises(RuntimeError, match="'items' is not a list"):
            google_cse_mod.search_google_cse("q")

    def test_items_none_normalized_to_empty_then_done(self, monkeypatch: pytest.MonkeyPatch) -> None:
        rsp = _fake_response(True, payload={"items": None})
        get = MagicMock(return_value=rsp)
        monkeypatch.setattr(google_cse_mod.requests, "get", get)
        assert google_cse_mod.search_google_cse("q") == []
        get.assert_called_once()

    def test_success_one_page_with_filters(self, monkeypatch: pytest.MonkeyPatch) -> None:
        payload = {
            "items": [
                {"title": "A", "link": "https://a", "snippet": "sa"},
                {"title": 42, "link": None, "snippet": [1, 2]},
            ]
        }
        rsp = _fake_response(True, payload=payload)
        get = MagicMock(return_value=rsp)
        monkeypatch.setattr(google_cse_mod.requests, "get", get)
        out = google_cse_mod.search_google_cse(
            " base ",
            max_results=5,
            site_filters=(" linkedin.com ", "", 99, "crunchbase.com"),
        )
        assert len(out) == 2
        assert out[0] == {"title": "A", "url": "https://a", "snippet": "sa"}
        assert out[1] == {"title": "", "url": "", "snippet": ""}
        call_kw = get.call_args.kwargs
        assert call_kw["params"]["q"] == "base (site:linkedin.com OR site:crunchbase.com)"
        assert call_kw["params"]["num"] == 5

    def test_max_results_zero_fetches_next_page(self, monkeypatch: pytest.MonkeyPatch) -> None:
        page1 = {
            "items": [{"title": "1", "link": "u1", "snippet": "s"}],
            "queries": {"nextPage": [{"startIndex": 11}]},
        }
        page2 = {"items": [{"title": "2", "link": "u2", "snippet": "s2"}]}
        get = MagicMock(side_effect=[_fake_response(True, payload=page1), _fake_response(True, payload=page2)])
        monkeypatch.setattr(google_cse_mod.requests, "get", get)
        out = google_cse_mod.search_google_cse("q", max_results=0)
        assert [h["title"] for h in out] == ["1", "2"]
        assert get.call_count == 2

    def test_duplicate_next_start_breaks(self, monkeypatch: pytest.MonkeyPatch) -> None:
        page = {
            "items": [{"title": "1", "link": "u", "snippet": ""}],
            "queries": {"nextPage": [{"startIndex": 1}]},
        }
        rsp = _fake_response(True, payload=page)
        get = MagicMock(return_value=rsp)
        monkeypatch.setattr(google_cse_mod.requests, "get", get)
        out = google_cse_mod.search_google_cse("q", max_results=0)
        assert len(out) == 1
        get.assert_called_once()

    def test_next_start_invalid_int_skips_pagination(self, monkeypatch: pytest.MonkeyPatch) -> None:
        page = {
            "items": [{"title": "x", "link": "u", "snippet": ""}],
            "queries": {"nextPage": [{"startIndex": "nope"}]},
        }
        rsp = _fake_response(True, payload=page)
        get = MagicMock(return_value=rsp)
        monkeypatch.setattr(google_cse_mod.requests, "get", get)
        google_cse_mod.search_google_cse("q", max_results=0)
        get.assert_called_once()


# --- helpers (unit-level) ---
class TestGoogleCseHelpers:
    def test_item_to_hit_non_dict(self) -> None:
        assert google_cse_mod._item_to_hit("x") == {"title": "", "url": "", "snippet": ""}

    def test_truncate_body_long(self) -> None:
        long = "a" * 600
        assert google_cse_mod._truncate_body(long).endswith("…")
        assert len(google_cse_mod._truncate_body(long)) == 501

    def test_next_start_index_malformed_queries(self) -> None:
        assert google_cse_mod._next_start_index({}) is None
        assert google_cse_mod._next_start_index({"queries": []}) is None  # type: ignore[arg-type]
        assert google_cse_mod._next_start_index({"queries": {"nextPage": "bad"}}) is None
        assert google_cse_mod._next_start_index({"queries": {"nextPage": [{}]}}) is None
