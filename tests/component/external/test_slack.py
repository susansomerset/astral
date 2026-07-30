"""Component tests for src/external/slack.py (AST-1069)."""

from __future__ import annotations

import hashlib
import hmac
import time
from unittest.mock import MagicMock

import pytest

from src.external import slack as slack_mod
from src.utils.config import CONTACT_CONFIG


def _sign(secret: str, timestamp: str, body: bytes) -> str:
    base = f"v0:{timestamp}:".encode("utf-8") + body
    return "v0=" + hmac.new(secret.encode("utf-8"), base, hashlib.sha256).hexdigest()


# Branches: good/bad/stale signature; challenge parse; post_message gated + HTTP.
class TestAst1069ExternalSlack:
    def test_verify_signature_ok_and_rejects(self) -> None:
        secret = "s3cret"
        body = b'{"ok":true}'
        ts = str(int(time.time()))
        assert slack_mod.verify_slack_signature(
            signing_secret=secret,
            timestamp=ts,
            body=body,
            signature=_sign(secret, ts, body),
        )
        assert not slack_mod.verify_slack_signature(
            signing_secret=secret,
            timestamp=ts,
            body=body,
            signature="v0=deadbeef",
        )
        # Stale timestamp (>60s).
        old = str(int(time.time()) - 120)
        assert not slack_mod.verify_slack_signature(
            signing_secret=secret,
            timestamp=old,
            body=body,
            signature=_sign(secret, old, body),
        )

    def test_parse_url_verification(self) -> None:
        assert slack_mod.parse_url_verification({"type": "url_verification", "challenge": "abc"}) == "abc"
        assert slack_mod.parse_url_verification({"type": "event_callback"}) is None
        assert slack_mod.parse_url_verification({"type": "url_verification", "challenge": 1}) is None

    def test_post_message_requires_gate_and_posts(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("ASTRAL_ALLOW_LIVE_EXTERNAL_IO", raising=False)
        with pytest.raises(Exception):
            slack_mod.post_message(channel="C1", text="hi")

        monkeypatch.setenv("ASTRAL_ALLOW_LIVE_EXTERNAL_IO", "1")
        monkeypatch.setenv(CONTACT_CONFIG["bot_token_env"], "xoxb-test")
        resp = MagicMock()
        resp.raise_for_status = MagicMock()
        resp.json = MagicMock(return_value={"ok": True, "ts": "1.2"})
        post = MagicMock(return_value=resp)
        monkeypatch.setattr(slack_mod.requests, "post", post)
        out = slack_mod.post_message(channel="C1", text="hi", thread_ts="1.0")
        assert out == {"ok": True, "ts": "1.2"}
        assert post.call_args.kwargs["json"]["thread_ts"] == "1.0"
        assert "Bearer xoxb-test" in post.call_args.kwargs["headers"]["Authorization"]
