"""Telescope service settings — secrets from env; tunables from telescope_config."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List

from telescope_config import (
    BROWSER_PER_REQUEST,
    BROWSER_POOL_SIZE,
    FIREFOX_USER_PREFS,
    LAUNCH_MAX_ATTEMPTS,
    LAUNCH_RETRY_DELAY_SECONDS,
    LAUNCH_TIMEOUT_MS,
    LOG_LEVEL,
    MAX_CONTEXTS_PER_BROWSER,
    PAGE_GOTO_TIMEOUT_MS,
    PORT,
    RECYCLE_AFTER_N,
    REQUEST_TIMEOUT_SECONDS,
    SCRAPE_RETRY_BASE_DELAY_SECONDS,
    SCRAPE_RETRY_COUNT,
    VIEWPORT,
    WAIT_READY_MAX_MS,
    WAIT_READY_MIN_CHARS,
    WAIT_READY_POLL_MS,
    WAIT_READY_STABILITY_POLLS,
)


@dataclass(frozen=True)
class Settings:
    bearer_token: str
    browser_per_request: bool
    browser_pool_size: int
    max_contexts_per_browser: int
    request_timeout_seconds: float
    scrape_retry_count: int
    scrape_retry_base_delay_seconds: float
    recycle_after_n: int
    port: int
    log_level: str
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
        browser_per_request=bool(BROWSER_PER_REQUEST),
        browser_pool_size=BROWSER_POOL_SIZE,
        max_contexts_per_browser=MAX_CONTEXTS_PER_BROWSER,
        request_timeout_seconds=float(REQUEST_TIMEOUT_SECONDS),
        scrape_retry_count=SCRAPE_RETRY_COUNT,
        scrape_retry_base_delay_seconds=SCRAPE_RETRY_BASE_DELAY_SECONDS,
        recycle_after_n=RECYCLE_AFTER_N,
        port=PORT,
        log_level=LOG_LEVEL,
        page_goto_timeout_ms=PAGE_GOTO_TIMEOUT_MS,
        launch_timeout_ms=LAUNCH_TIMEOUT_MS,
        launch_max_attempts=LAUNCH_MAX_ATTEMPTS,
        launch_retry_delay_seconds=LAUNCH_RETRY_DELAY_SECONDS,
        viewport=dict(VIEWPORT),
        firefox_user_prefs=dict(FIREFOX_USER_PREFS),
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
        wait_ready_max_ms=WAIT_READY_MAX_MS,
        wait_ready_poll_ms=WAIT_READY_POLL_MS,
        wait_ready_stability_polls=WAIT_READY_STABILITY_POLLS,
        wait_ready_min_chars=WAIT_READY_MIN_CHARS,
    )


settings = load_settings()
