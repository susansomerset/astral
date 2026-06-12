# -*- coding: utf-8 -*-
"""Small outbound reachability helpers (stdlib only — no Playwright)."""

import urllib.error
import urllib.request

from src.utils.config import ASTRAL_CONFIG


def check_internet_reachable() -> bool:
    """True if an HTTPS GET to ``dispatch_network_check_url`` completes with a non-5xx code."""
    url = (ASTRAL_CONFIG.get("dispatch_network_check_url") or "").strip()
    if not url:
        return False
    timeout = int(ASTRAL_CONFIG.get("dispatch_network_check_timeout_seconds") or 30)
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "AstralDispatchConnectivity/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
            code = resp.getcode()
            # Read a byte so TLS + response headers are exercised; avoid buffering large bodies.
            resp.read(1)
    except (urllib.error.URLError, OSError, ValueError, TypeError):
        return False
    if code is None or code >= 500:
        return False
    return True
