"""Telescope service settings — env + local constants. Never import src."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List

from telescope_config import REQUEST_TIMEOUT_SECONDS


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    return int(raw)


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    return float(raw)


@dataclass(frozen=True)
class Settings:
    bearer_token: str
    request_timeout_seconds: float
    recycle_after_n: int
    port: int
    page_goto_timeout_ms: int
    launch_timeout_ms: int
    launch_max_attempts: int
    launch_retry_delay_seconds: float
    viewport: Dict[str, int]
    firefox_user_prefs: Dict[str, int]
    cookie_dismiss_selectors: List[str]
    cookie_fuzzy_accept_keywords: List[str]
    wait_ready_max_ms: int
    wait_ready_poll_ms: int
    wait_ready_stability_polls: int
    wait_ready_min_chars: int
    # Fuzzy dismiss container id/class substrings (platform html_cull banner_patterns copy)
    cookie_banner_patterns: List[str] = field(
        default_factory=lambda: [
            "cookie",
            "consent",
            "banner",
            "modal",
            "newsletter",
            "subscribe",
            "chat",
            "intercom",
        ]
    )


def load_settings() -> Settings:
    return Settings(
        bearer_token=os.environ.get("TELESCOPE_BEARER_TOKEN", ""),
        request_timeout_seconds=float(REQUEST_TIMEOUT_SECONDS),
        recycle_after_n=_env_int("TELESCOPE_RECYCLE_AFTER_N", 50),
        port=_env_int("TELESCOPE_PORT", 8080),
        page_goto_timeout_ms=_env_int("TELESCOPE_PAGE_GOTO_TIMEOUT_MS", 30_000),
        launch_timeout_ms=_env_int("TELESCOPE_LAUNCH_TIMEOUT_MS", 60_000),
        launch_max_attempts=3,
        launch_retry_delay_seconds=2.0,
        viewport={"width": 1280, "height": 2000},
        firefox_user_prefs={"security.sandbox.content.level": 0},
        # Duplicated from platform ASTRAL_CONFIG — import fence forbids src/
        cookie_dismiss_selectors=[
            'button:has-text("Accept All")',
            'button:has-text("Allow All")',
            'button:has-text("Accept")',
            'button:has-text("I Accept")',
            'button:has-text("Agree")',
            'button:has-text("Confirm")',
            '[id*="accept-all"]',
            '[id*="cookie-accept"]',
            '[class*="accept-all"]',
            'button[id*="cookie"]',
            'button[class*="cookie"]',
        ],
        cookie_fuzzy_accept_keywords=[
            "accept",
            "allow",
            "agree",
            "confirm",
            "ok",
            "got it",
        ],
        wait_ready_max_ms=20_000,
        wait_ready_poll_ms=500,
        wait_ready_stability_polls=2,
        wait_ready_min_chars=400,
    )


settings = load_settings()
