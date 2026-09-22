"""Telescope service constants — keep in sync with platform TELESCOPE_CONFIG.

Mirror: src/utils/config.py → TELESCOPE_CONFIG["request_timeout_seconds"]
Import fence forbids reading src/ from service/telescope/.
Secrets (bearer token) stay in env via settings.py.
"""

REQUEST_TIMEOUT_SECONDS = 120

# Scrape retries after Playwright/page flake (initial attempt + 3 retries).
SCRAPE_RETRY_COUNT = 3
SCRAPE_RETRY_BASE_DELAY_SECONDS = 2.0

# Pooled mode (AST-1725): W Firefox processes, fresh context per HTTP call.
BROWSER_PER_REQUEST = False
BROWSER_POOL_SIZE = 10
MAX_CONTEXTS_PER_BROWSER = 20
RECYCLE_AFTER_N = 50

PORT = 8080
LOG_LEVEL = "INFO"

PAGE_GOTO_TIMEOUT_MS = 30_000
LAUNCH_TIMEOUT_MS = 60_000
LAUNCH_MAX_ATTEMPTS = 3
LAUNCH_RETRY_DELAY_SECONDS = 2.0

VIEWPORT = {"width": 1280, "height": 2000}
FIREFOX_USER_PREFS = {"security.sandbox.content.level": 0}

WAIT_READY_MAX_MS = 20_000
WAIT_READY_POLL_MS = 500
WAIT_READY_STABILITY_POLLS = 2
WAIT_READY_MIN_CHARS = 400
