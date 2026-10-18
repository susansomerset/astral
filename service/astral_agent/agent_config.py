"""Astral-agent service tunables — no src/ imports (import fence)."""

# No worker cap: every claimable job is held (leased + heartbeated) and the gate admits
# it (today: everything; step 6 adds the learned per-batch limit).
# Gap the gate loop waits before re-asking the gate while jobs are still waiting.
ADMIT_INTERVAL_SECONDS = 0.1
QUEUE_POLL_SECONDS = 2.0
LEASE_SECONDS = 300
HEARTBEAT_SECONDS = 30
MAINTENANCE_SECONDS = 30
JOB_RETENTION_HOURS = 24
WORKER_STALE_SECONDS = 90
SHUTDOWN_GRACE_SECONDS = 25
# Serverless: drop PG when idle; platform wakes via GET /wake.
IDLE_SLEEP_SECONDS = 300
DB_POOL_MAX_SIZE = 5
PORT = 8080
LOG_LEVEL = "INFO"
