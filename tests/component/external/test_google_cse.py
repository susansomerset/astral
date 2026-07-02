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
    google_cse_mod._last_cse_request_at = None
    yield  # type: ignore[misc]
    google_cse_mod._last_cse_request_at = None


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

    def test_is_rate_limit_response_http_429(self) -> None:
        assert google_cse_mod._is_rate_limit_response(429, None) is True

    def test_is_rate_limit_response_json_envelope(self) -> None:
        parsed = {"error": {"code": 429, "errors": [{"reason": "rateLimitExceeded"}]}}
        assert google_cse_mod._is_rate_limit_response(200, parsed) is True

    def test_is_rate_limit_response_quota_403_not_rate_limit(self) -> None:
        parsed = {"error": {"message": "quota", "code": 403}}
        assert google_cse_mod._is_rate_limit_response(200, parsed) is False


# --- AST-837: inter-query pacing + rate-limit pause/retry ---
class TestGoogleCseAst837PacingAndRateLimit:
    def test_inter_query_delay_sleeps_before_second_request(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setitem(google_cse_mod.GOOGLE_CSE_CONFIG, "inter_query_delay_sec", 2.0)
        monkeypatch.setitem(google_cse_mod.GOOGLE_CSE_CONFIG, "rate_limit_max_retries", 0)
        payload = {"items": [{"title": "A", "link": "https://a", "snippet": "s"}]}
        rsp = _fake_response(True, payload=payload)
        monkeypatch.setattr(google_cse_mod.requests, "get", MagicMock(return_value=rsp))
        monotonic_values = [100.0, 100.0, 100.5, 100.5, 100.5, 101.0, 101.0]
        monotonic = iter(monotonic_values)

        def _monotonic() -> float:
            try:
                return next(monotonic)
            except StopIteration:
                return monotonic_values[-1]

        monkeypatch.setattr(google_cse_mod.time, "monotonic", _monotonic)
        sleeps: list[float] = []
        monkeypatch.setattr(google_cse_mod.time, "sleep", lambda sec: sleeps.append(sec))
        google_cse_mod._last_cse_request_at = 100.0
        google_cse_mod.search_google_cse("q1")
        google_cse_mod.search_google_cse("q2")
        assert sleeps[-1] == pytest.approx(1.5, abs=0.01)

    def test_inter_query_delay_zero_skips_sleep(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setitem(google_cse_mod.GOOGLE_CSE_CONFIG, "inter_query_delay_sec", 0)
        payload = {"items": [{"title": "A", "link": "https://a", "snippet": "s"}]}
        rsp = _fake_response(True, payload=payload)
        monkeypatch.setattr(google_cse_mod.requests, "get", MagicMock(return_value=rsp))
        google_cse_mod._last_cse_request_at = 1.0
        sleeps: list[float] = []
        monkeypatch.setattr(google_cse_mod.time, "sleep", lambda sec: sleeps.append(sec))
        google_cse_mod.search_google_cse("q1")
        google_cse_mod.search_google_cse("q2")
        assert sleeps == []

    def test_rate_limit_429_retries_then_succeeds(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setitem(google_cse_mod.GOOGLE_CSE_CONFIG, "inter_query_delay_sec", 0)
        monkeypatch.setitem(google_cse_mod.GOOGLE_CSE_CONFIG, "rate_limit_max_retries", 1)
        monkeypatch.setitem(google_cse_mod.GOOGLE_CSE_CONFIG, "rate_limit_pause_sec", 65)
        fail_rsp = _fake_response(False, status=429, raw_text="rate limited")
        ok_payload = {"items": [{"title": "A", "link": "https://a", "snippet": ""}]}
        ok_rsp = _fake_response(True, payload=ok_payload)
        get = MagicMock(side_effect=[fail_rsp, ok_rsp])
        monkeypatch.setattr(google_cse_mod.requests, "get", get)
        sleeps: list[float] = []
        monkeypatch.setattr(google_cse_mod.time, "sleep", lambda sec: sleeps.append(sec))
        monkeypatch.setattr(google_cse_mod.time, "monotonic", MagicMock(return_value=0.0))
        out = google_cse_mod.search_google_cse("q")
        assert out == [{"title": "A", "url": "https://a", "snippet": ""}]
        assert get.call_count == 2
        assert sleeps == [65.0]

    def test_rate_limit_exhausted_raises_runtime_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setitem(google_cse_mod.GOOGLE_CSE_CONFIG, "inter_query_delay_sec", 0)
        monkeypatch.setitem(google_cse_mod.GOOGLE_CSE_CONFIG, "rate_limit_max_retries", 1)
        fail_rsp = _fake_response(False, status=429, raw_text="still limited")
        get = MagicMock(return_value=fail_rsp)
        monkeypatch.setattr(google_cse_mod.requests, "get", get)
        monkeypatch.setattr(google_cse_mod.time, "sleep", MagicMock())
        monkeypatch.setattr(google_cse_mod.time, "monotonic", MagicMock(return_value=0.0))
        with pytest.raises(RuntimeError, match=r"Google CSE HTTP 429"):
            google_cse_mod.search_google_cse("q")
        assert get.call_count == 2

    def test_rate_limit_json_envelope_retries(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setitem(google_cse_mod.GOOGLE_CSE_CONFIG, "inter_query_delay_sec", 0)
        monkeypatch.setitem(google_cse_mod.GOOGLE_CSE_CONFIG, "rate_limit_max_retries", 1)
        monkeypatch.setitem(google_cse_mod.GOOGLE_CSE_CONFIG, "rate_limit_pause_sec", 10)
        limited = {
            "error": {
                "code": 429,
                "errors": [{"reason": "rateLimitExceeded"}],
                "message": "Rate Limit Exceeded",
            }
        }
        limited_rsp = _fake_response(True, payload=limited)
        ok_payload = {"items": [{"title": "B", "link": "https://b", "snippet": ""}]}
        ok_rsp = _fake_response(True, payload=ok_payload)
        get = MagicMock(side_effect=[limited_rsp, ok_rsp])
        monkeypatch.setattr(google_cse_mod.requests, "get", get)
        monkeypatch.setattr(google_cse_mod.time, "sleep", MagicMock())
        monkeypatch.setattr(google_cse_mod.time, "monotonic", MagicMock(return_value=0.0))
        out = google_cse_mod.search_google_cse("q")
        assert out[0]["url"] == "https://b"
        assert get.call_count == 2

    def test_pace_detail_receives_pacing_and_retry_messages(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setitem(google_cse_mod.GOOGLE_CSE_CONFIG, "inter_query_delay_sec", 1.0)
        monkeypatch.setitem(google_cse_mod.GOOGLE_CSE_CONFIG, "rate_limit_max_retries", 0)
        payload = {"items": [{"title": "A", "link": "https://a", "snippet": ""}]}
        rsp = _fake_response(True, payload=payload)
        monkeypatch.setattr(google_cse_mod.requests, "get", MagicMock(return_value=rsp))
        monotonic = iter([0.0, 0.2, 1.0])
        monkeypatch.setattr(google_cse_mod.time, "monotonic", lambda: next(monotonic))
        monkeypatch.setattr(google_cse_mod.time, "sleep", MagicMock())
        google_cse_mod._last_cse_request_at = 0.0
        messages: list[str] = []
        google_cse_mod.search_google_cse("q", pace_detail=messages.append)
        assert any("pacing: sleeping" in line for line in messages)
