"""Telescope service constants — keep in sync with platform TELESCOPE_CONFIG.

Mirror: src/utils/config.py → TELESCOPE_CONFIG (max_attempts, job_deadline_seconds)
Import fence forbids reading src/ from service/telescope/.
Secrets (database URL) stay in env via settings.py.
"""

# Scrape budget only — starts once the job has its page (not queue wait or Firefox launch).
REQUEST_TIMEOUT_SECONDS = 120

# Retries are queue re-deliveries: the platform sets max_attempts per job; a failed
# attempt goes back to the queue after base * 2**(attempt-1) seconds.
SCRAPE_RETRY_BASE_DELAY_SECONDS = 2.0
# Timeouts are expensive — only this many attempts end in a timeout before the job fails.
TIMEOUT_MAX_ATTEMPTS = 2

# Queue worker (Postgres-backed). WORKER_CONCURRENCY = scrapes in flight per replica,
# i.e. max live contexts in its one Firefox — the only concurrency knob (must fit the
# replica's memory limit). Scale out by adding replicas.
WORKER_CONCURRENCY = 20
QUEUE_POLL_SECONDS = 2.0
LEASE_SECONDS = 60
HEARTBEAT_SECONDS = 15
MAINTENANCE_SECONDS = 30
JOB_RETENTION_HOURS = 24
WORKER_STALE_SECONDS = 60
SHUTDOWN_GRACE_SECONDS = 25
# Serverless: after this long with nothing queued, running or in flight, the process
# drops its Postgres connections and Firefox so Railway can put it to sleep. The
# platform wakes it with GET $TELESCOPE_BASE_URL/wake when it enqueues work.
IDLE_SLEEP_SECONDS = 300
DB_POOL_MAX_SIZE = 5

# One Firefox per process, a fresh context per job. After this many jobs a new
# Firefox takes over and the old one closes once its last job finishes.
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
