<!-- linear-archive: AST-344 archived 2026-06-03 -->

## Linear archive (AST-344)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-344/error-alerts  
**Status at archive:** Done  
**Project:** Astral Monitor  
**Assignee:** susan  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

When a task has been autorun and results in >0 total results and >0 errors, send an email to the ASTRAL_SUPPORT email address, defaulting to 'susan+astral@susansomerset.com' with the execution summary in the title and the log content for that execution in the email body.

### Comments

_No comments._

---

# AST-344: Error Alerts

## Plan

Send an email to the `ASTRAL_SUPPORT` address whenever an AUTO-mode dispatch task completes with `total_processed > 0` and `total_errors > 0`. Dispatcher delegates to a new `monitor.py` core module; monitor calls `gmail.py` in external to send. The stub structure of `monitor.py` allows future escalation logic (log scanning, daily summaries) to be added without touching the dispatcher.

---

### Step 1 — `src/external/gmail.py` (NEW)

New external-layer module. External layer owns all I/O; sending email is I/O.

**Function:**
```python
def send_email(to: str, subject: str, body: str) -> bool
```

- Builds `google.oauth2.credentials.Credentials` from env vars already in `.env` / Railway:
  - `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN`, `GOOGLE_TOKEN_URI`
- Constructs a `googleapiclient` Gmail API service (`gmail`, `v1`).
- Builds a `MIMEText` message (plain text), base64-encodes it, sends via `service.users().messages().send(userId="me", body=...)`.
- Returns `True` on success, `False` on failure. Does not log — returns status for the caller to decide. Never raises.
- No file-based token storage needed — refresh token in env obtains access tokens at runtime.

All four required libs (`google-auth`, `google-auth-oauthlib`, `google-auth-httplib2`, `google-api-python-client`) are already in `requirements.txt`.

---

### Step 2 — `src/core/monitor.py` (NEW)

New core-layer module. Owns the business logic of what constitutes a notifiable condition and how to act on it. Stub structure allows future monitoring features (log scanning, escalation, daily summaries) without touching the dispatcher.

**Public function:**
```python
def auto_run_error(task_key: str, batch_id: str, accumulated: dict, final_status: str) -> None
```

- Fetches log entries via `database.list_log_entries(batch_id=batch_id)` (logs are flushed before this is called).
- Reverses to chronological order (DB returns newest-first).
- Formats subject: `[Astral] {task_key} {final_status}: {total_errors} error(s) / {total_processed} processed | {batch_id}`
- Formats body: one line per log entry as `{created_at}  [{level}]  {message}`.
- Reads `to` address from `ASTRAL_CONFIG["support_email"]`.
- Calls `send_email(to, subject, body)` from `src.external.gmail`.
- Logs outcome via its own module logger (core layer logs ✓).

---

### Step 3 — `src/utils/config.py` (MODIFIED)

Add `support_email` to `ASTRAL_CONFIG` in the `# --- Dispatcher ---` block:

```python
"support_email": os.environ.get("ASTRAL_SUPPORT", "susan+astral@susansomerset.com"),
```

`ASTRAL_CONFIG` is the single source of truth for behavioral values (§2.1). Env var with a default is the established pattern.

---

### Step 4 — `src/core/dispatcher.py` (MODIFIED)

**4a. Import** `monitor` from `src.core` at the top (intra-core import ✓).

**4b. Call site** in `_dispatch_one()`, after the `finally` block (after `flush_log_buffer()` and `log_batch_id.set(None)`):

```python
# Delegate to monitor for AUTO runs that produced results with errors
if (not is_click
        and accumulated.get("total_processed", 0) > 0
        and accumulated.get("total_errors", 0) > 0):
    monitor.auto_run_error(task_key, batch_id, accumulated, final_status)
```

Alert fires after the ledger is written and logs are flushed. A failure inside `monitor.auto_run_error` must not propagate — monitor wraps its own call to gmail.

---

### Files Changed

| File | Action | What |
|------|--------|------|
| `src/external/gmail.py` | CREATE | Gmail API email sender (`send_email`) |
| `src/core/monitor.py` | CREATE | Monitoring module stub; `auto_run_error` for autorun error alerts |
| `src/utils/config.py` | MODIFY | Add `support_email` to `ASTRAL_CONFIG` |
| `src/core/dispatcher.py` | MODIFY | Import `monitor`; call `monitor.auto_run_error()` after AUTO runs with errors |
| `docs/features/monitor/project_description.md` | CREATE | Project description |
| `docs/features/monitor/ast-344-error-alerts.md` | CREATE | This doc |

---

## Code Rules Review

| Rule | Check |
|------|-------|
| **Layer rules §3.3** | `gmail.py` in `src/external/` (I/O). `monitor.py` in `src/core/` → imports external and data ✓. `dispatcher.py` (core) → imports core ✓. No upward imports. |
| **Config as source of truth §2.1** | `support_email` lives in `ASTRAL_CONFIG`, read from env with default. No hardcoded email anywhere. |
| **Logging §1.5** | `gmail.py` returns `False` silently (external does not log). `monitor.py` (core) logs outcome via its own logger. Clean layer boundary. |
| **DRY §1.3** | Alert logic in `monitor.auto_run_error`; dispatcher has one 3-line call site. |
| **In-file organization §1.3** | `monitor.py` is a new file — public function first, helpers below. |
| **No heuristics / limits** | No truncation, no depth limits. All log entries for the batch included in email body. |
| **Error handling** | `gmail.send_email` catches and returns `False`. `monitor.auto_run_error` catches any exception from gmail and logs it — never raises to dispatcher. |

---

## Review

**Commit:** `d4802f1`
**Branch:** `dev`
**Reviewed:** April 17, 2026

---

## What's Solid

- **Plan fidelity is exact.** Every step — gmail.py, monitor.py, config, dispatcher call site — matches the spec with no additions or omissions.
- **Layer ownership is clean.** `gmail.py` in `external/` owns the I/O, `monitor.py` in `core/` owns the business logic decision. No upward imports.
- **Dispatcher call site placement is correct.** The alert fires after `flush_log_buffer()` and `log_batch_id.set(None)` (both in the `finally` block), so logs are guaranteed to be in the DB before `list_log_entries()` queries them. The `batch_id` is passed directly, not read from the context var — so clearing `log_batch_id` first is safe.
- **Never-raises contract is solid.** `gmail.py` swallows all exceptions and returns `False`; `monitor.auto_run_error` wraps everything in a try/except and logs — the dispatcher is fully shielded.
- **Email body is complete and un-truncated.** All log entries for the batch, chronological, no limits. Matches the spec.
- **`ASTRAL_CODE_RULES.md` updated correctly** — new files listed in the directory tree, `External` and `Core` layer descriptions updated to mention Gmail and monitor.

---

## Issues

### Issue 1 — `ASTRAL_SUPPORT` not documented in `.env` ⚠️ required

The `.env` file documents every other env var but has no entry for `ASTRAL_SUPPORT`. `GMAIL_USER` is documented there; `ASTRAL_SUPPORT` is not. The config default (`susan+astral@susansomerset.com`) makes it work in dev, but if this is ever deployed to a new environment or the target address needs to change on Railway, there's nothing in `.env` pointing at this lever.

**Recommendation:** Add a commented entry to `.env`:
```
# Alert recipient for AUTO task error notifications (core/monitor.py)
# ASTRAL_SUPPORT=susan+astral@susansomerset.com
```

---

### Issue 2 — Double fallback for `support_email` in `monitor.py` 🔧 fix now

```python
# monitor.py line 34
to = ASTRAL_CONFIG.get("support_email", "susan+astral@susansomerset.com")
```

`ASTRAL_CONFIG` is a plain dict and `support_email` is always present (config.py sets it unconditionally via `os.environ.get(..., default)`). The `.get(..., fallback)` here is dead code — it can never fire. This also violates the single-source-of-truth rule: the email address now lives in two places (config.py and monitor.py).

**Fix:** `to = ASTRAL_CONFIG["support_email"]` — config already guarantees it exists.

---

### Issue 3 — `"me"` is not a valid From address fallback ℹ️ advisory

```python
# gmail.py line 35
msg["from"] = os.environ.get("GMAIL_USER", "me")
```

`"me"` as a fallback is not a valid email address. Gmail would likely reject or mangle it. `GMAIL_USER` is in `.env` and documented in the module docstring as required, so this probably never fires — but the fallback is misleading. A `None` or an empty string would at least make it obvious something's misconfigured. Low risk in practice.

---

### Issue 4 — Lazy imports in `gmail.py` ℹ️ advisory

The `google` imports are inside the function body rather than at module level. This means import errors (e.g., missing packages) won't surface until `send_email()` is first called — likely at runtime during an error alert. The plan doesn't call this out. It works, but it hides dependency issues at startup rather than surfacing them at import time. Not blocking, just a style choice worth noting.

---

## Recommended Actions

| # | Severity | Action | Susan's take |
|---|----------|--------|--------------|
| 1 | Discuss | Add `ASTRAL_SUPPORT` to `.env` with a comment so it's discoverable | Nope. config.py only. DRY |
| 2 | Fix now | Replace `ASTRAL_CONFIG.get("support_email", "susan+...")` with `ASTRAL_CONFIG["support_email"]` in `monitor.py` | YES, do not hardcode a default. crash out if the support email is missing |
| 3 | Advisory | Consider raising or returning `None` instead of `"me"` as the `GMAIL_USER` fallback | This is where silent fails would be soooo bad. Be loud if there's an issue here. Validate that the variable is present when when the server starts. |
| 4 | Advisory | Optionally promote `google` imports to module level in `gmail.py` for earlier failure detection | Sure? |

---

## Resolution

- **Issue 1** (ASTRAL_SUPPORT in .env): Deferred — Susan confirmed support_email is a plain config literal, not an env var. DRY; config.py is the one and only home.
- **Issue 2** (double fallback in monitor.py): Fixed — `to = ASTRAL_CONFIG["support_email"]` with no `.get()` fallback. Config guarantees it exists.
- **Issue 3** ("me" fallback in gmail.py): Fixed — module-level startup validation raises `RuntimeError` at import time if any required env var is missing. `_GMAIL_USER = os.environ["GMAIL_USER"]` with no fallback; used directly in `send_email`.
- **Issue 4** (lazy Google imports): Fixed — `google.oauth2.credentials.Credentials` and `googleapiclient.discovery.build` promoted to module-level imports. Missing packages now surface at startup.
