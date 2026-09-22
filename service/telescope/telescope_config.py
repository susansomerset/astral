"""Telescope service constants — keep in sync with platform TELESCOPE_CONFIG.

Mirror: src/utils/config.py → TELESCOPE_CONFIG["request_timeout_seconds"]
Import fence forbids reading src/ from service/telescope/.
"""

REQUEST_TIMEOUT_SECONDS = 120

# Science experiment: launch + tear down a full Firefox process per HTTP scrape.
# False = AST-1725 pooled browser (one Firefox per replica, fresh context per call).
BROWSER_PER_REQUEST = True
