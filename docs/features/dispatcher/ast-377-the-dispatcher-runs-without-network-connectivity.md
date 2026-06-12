<!-- linear-archive: AST-377 archived 2026-06-03 -->

## Linear archive (AST-377)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-377/the-dispatcher-runs-without-network-connectivity  
**Status at archive:** Done  
**Project:** Astral Dispatcher  
**Assignee:** betty  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Almost all of the tasks dispatched require internet connectivity.

Let's create a util function for "check_network" to return true if it can navigate to anthropic.com.

### Comments

#### susan — 2026-05-04T20:38:52.092Z
Review feedback resolved. Branch `chuckles/ast-377-the-dispatcher-runs-without-network-connectivity` is ready for testing. Commit: `5cc6b3e0`

— Betty

#### susan — 2026-05-04T20:19:49.847Z
**Review posted — Radia**

Summary: **0** fix-now, **0** discuss, **2** advisory (sync `urllib` blocks the asyncio loop for up to the configured timeout — expected per plan; `.cursor/skills/check-linear/SKILL.md` is on the branch outside the plan’s file table).

Diff reviewed: **`origin/dev`…feature branch** (merge-base `50aed96`). Owner label → **Hedy** (dispatcher surface; build signed **Chuckles** in thread). Conf / Risk / Scope preserved.

**Combined doc:**  
https://github.com/susansomerset/astral/blob/e14157df4cdd6f778444873d8325665229565712/docs/features/dispatcher/ast-377-the-dispatcher-runs-without-network-connectivity.md

— Radia

#### susan — 2026-05-04T20:16:14.518Z
Built by Chuckles.

**Branch:** `chuckles/ast-377-the-dispatcher-runs-without-network-connectivity`
**Commits:** `3ce9323` (feat — `ASTRAL_CONFIG` probe URL/timeout, `src/utils/network.check_internet_reachable`, gate at top of `_run_unified` before claims), `284773d` (plan review stub).

Offline: scheduler warning `[task_key/batch_id] dispatch skipped: network unreachable`, zeros returned, no `get_new_*_batch`.

#### susan — 2026-05-04T20:15:16.216Z
Label review (build agent):

Conf: agree — current conf-Medium fits first outbound gate + prod firewall/URL assumptions.
Risk: agree — current risk-Medium fits false negative/positive tradeoffs called out in the plan.
Scope: agree — current scope-minor fits three small touch points (config, one util, one gate).

Proceeding with implementation.

— Chuckles

#### susan — 2026-05-04T19:58:07.821Z
Nope.  I specifically want this to be a network check at the top of a dispatch run, not to go as deep as having playwright confirm validation.  I may have over-specified the success criteria here, but the point is that we want to have confirmation that we can reach the internet before we claim a batch.

#### susan — 2026-05-04T19:55:50.130Z
**Plan doc (execution bible):** `docs/features/dispatcher/ast-377-the-dispatcher-runs-without-network-connectivity.md` on branch `chuckles/ast-377-the-dispatcher-runs-without-network-connectivity` (GitHub link attached).

**Self-assessment (labels):**
- **Scope — minor:** Three files (`config.py`, `playwright.py`, `dispatcher.py`); one probe + one gate.
- **Conf — Medium:** First network gate on dispatch; Playwright `goto` success criteria and timeout must match ops reality.
- **Risk — Medium:** False negatives stall AUTO; false positives waste work — mitigated with config literals + clear skip logs.

Queue: **Betty** retained. Ready for plan review → **b-build-linear** after approval.

---

# AST-377 — The dispatcher runs without network connectivity

**Linear:** [AST-377](https://linear.app/astralcareermatch/issue/AST-377/the-dispatcher-runs-without-network-connectivity)  
**Branch:** `<agent>/ast-377-the-dispatcher-runs-without-network-connectivity`

Almost all dispatched work needs outbound network (Playwright, Anthropic, etc.). Today the scheduler and admin “Run” can start tasks while the host has no usable connectivity, producing noisy failures and wasted ledger rows. This plan adds a **lightweight internet reachability check** (stdlib HTTP, not Playwright) at the **top of each batch** in `_run_unified`, **before** any `get_new_*_batch` claim, so we never claim entities when we already know we cannot reach the internet.

**Latest Linear direction (Susan, AST-377):** A **network** check at the top of the dispatch path that leads to a claim — **not** Playwright-as-validator. Over-specific success criteria are dropped in favor of one question: **can we reach the internet before we claim a batch?** In code, that is the first thing `_run_unified` does, ahead of `get_new_job_batch` / `get_new_company_batch`.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|--------|
| `src/utils/config.py` | Under `ASTRAL_CONFIG`, add literals: `dispatch_network_check_url` (e.g. `https://www.anthropic.com/`) and `dispatch_network_check_timeout_seconds` (integer seconds, reasonable default e.g. 30). | utils |
| `src/utils/network.py` | New module with **public** sync function `check_internet_reachable() -> bool`: read URL + timeout from `ASTRAL_CONFIG`; use stdlib only (`urllib.request` with explicit timeout, or `http.client` + TLS — **pick one** and keep it minimal). Treat successful connection + HTTP response start (e.g. any 2xx/3xx or readable status line) as `True`; timeouts, DNS failures, connection refused, SSL errors, and 5xx as `False`. No INFO spam; optional single WARNING on failure only if useful (call site may log instead). | utils |
| `src/core/dispatcher.py` | At the **very start** of `async def _run_unified` (after any trivial locals / before importing consult or calling `get_new_job_batch` / `get_new_company_batch`): if not `check_internet_reachable()`, log one scheduler warning with `task_key` from `task` and `batch_id` from `log_batch_id.get()` if available, then `return dict(_SUMMARY_ZERO)` immediately — **no claim**, no `clear_*_batch` needed. If online, existing flow unchanged. | core |

No Playwright in this feature. No new database tables, no admin UI, no `CONSULT_CONFIG` / `dispatch_task` schema changes.

---

## Stage 1: Config literals

**Done when:** `ASTRAL_CONFIG` contains the two keys; `python3 -m py_compile src/utils/config.py` passes.

1. In `src/utils/config.py`, inside the `ASTRAL_CONFIG` dict (near existing `dispatch_timeout_seconds` / tick settings), add:
   - `dispatch_network_check_url`: string `https://www.anthropic.com/` (or the exact URL Susan prefers; must be a **literal** in config, not `os.environ`).
   - `dispatch_network_check_timeout_seconds`: integer (e.g. `30`).

⚠️ **Decision:** Use **HTTPS** canonical site URL as the probe target (matches ticket wording “anthropic.com”); no separate env var per project rules for non-secret defaults.

---

## Stage 2: Stdlib reachability probe

**Done when:** `check_internet_reachable` exists in `src/utils/network.py`, returns bool, reads only `ASTRAL_CONFIG`; `python3 -m py_compile` passes for that file; no dependency on `src.external`.

1. Add `src/utils/network.py` with `def check_internet_reachable() -> bool`.
2. Implementation constraints:
   - Import `ASTRAL_CONFIG` from `src.utils.config` (same pattern as other utils modules that read config).
   - Use a short GET or HEAD with socket-level timeout from config seconds; close the response promptly so we do not buffer large bodies.
   - Return `False` on any exception path; return `True` only when the remote is clearly reachable (HTTP layer success — do not require Playwright or browser TLS stack parity).
3. **Blocking note:** `_run_unified` is async; calling sync `urllib` blocks the event loop for up to the timeout. Acceptable for a bounded small timeout; if we later need non-blocking I/O, wrap in `asyncio.to_thread` in dispatcher only (not required for first ship unless profiling says otherwise).

⚠️ **Decision:** Probe is **HTTP/TLS via stdlib**, not browser navigation — fast, confirms “internet before claim,” and avoids over-specifying success criteria through Playwright.

---

## Stage 3: Dispatcher gate (before claim)

**Done when:** Offline runs produce **no** `get_new_*_batch` calls and no `clear_*_batch` for that attempt; `_dispatch_one` ledger / `finally` behavior unchanged for runs that **do** enter `_run_unified` (including zero-entity returns after a successful check).

1. In `src/core/dispatcher.py`, import `check_internet_reachable` from `src.utils.network` (core may import utils).
2. At the **first executable lines** of `_run_unified` after the docstring (before `from src.core import consult` and before any batch claim):
   - If not `check_internet_reachable()`: `_sched_log.warning` (or project-standard scheduler logger) with `task.get("task_key")`, optional `log_batch_id.get()`, fixed short message (`"dispatch skipped: network unreachable"` or similar). `return dict(_SUMMARY_ZERO)`.
3. Do not move the gate to `_dispatch_one` only — Susan wants confirmation **before we claim a batch**; `_run_unified` is the single choke point for claims.

⚠️ **Decision:** Ledger rows created in `_dispatch_one` before `_run_unified` may still exist for a run that skips inside `_run_unified`; that run completes with zero counts and **COMPLETED** as today — operators use log line + zeros to see “skipped — no network” without FAILED noise.

---

## Self-Assessment

**Scope:** `minor` — Three files (one small new module), one probe, one gate; no schema or UI.

**Conf:** `Medium` — First time we gate on network; URL must be reachable from prod (firewall allowlist).

**Risk:** `Medium` — False negatives stall AUTO; false positives still waste some work until real I/O fails — mitigated with config literals + clear logs. Stdlib TLS/DNS differs slightly from Firefox stack; acceptable tradeoff per product direction (light check, not browser validation).

---

## Self-review (ASTRAL_CODE_RULES)

- **§1.3 / DRY:** Single `check_internet_reachable`; dispatcher does not duplicate HTTP logic.
- **§2.1:** URL and timeout are **literals in `ASTRAL_CONFIG`**, not env splits.
- **§2.4:** No entity claim when offline — requirement satisfied at `_run_unified` entry.
- **§2.6:** No state machine edits.
- **§3.3:** `dispatcher` (core) imports `utils.network`; `network` imports only `utils.config` — no layer violation.
- **§3.5:** Public function name `check_internet_reachable` is descriptive.

No conflicts flagged.

---

## Execution contract (summary)

The build agent executes stages 1→2→3 in order, one commit per stage on the feature branch, then hands off per **b-build-linear**. Any ambiguity → Linear comment on AST-377 and stop.

---

## Revisions

| Date | Source | Change |
|------|--------|--------|
| 2026-05-04 | Linear (Susan): AST-377 comment | Replaced Playwright `goto` probe with **stdlib HTTP** reachability check; gate moved to **top of `_run_unified`** so we confirm internet **before** `get_new_*_batch` claim, not a deep browser validation. |
| 2026-05-04 | Betty (`f-resolve-linear`) | Removed repo-bundled **`1-check-linear`** skill (then under **`.cursor/skills/`** in-tree) from this branch per Radia review — dispatcher PR diff vs `dev` only; no change to the network gate implementation. |
| 2026-05-04 | Betty | Rebased onto then-current `origin/dev`; branch history squashed to **`f00f7c2d`** — same four-file net diff vs `dev` as before (no `.cursor` changes vs `dev`; `1-check-linear` stays on `dev`). |

---

## Review

**Branch:** `<agent>/ast-377-the-dispatcher-runs-without-network-connectivity`  
**Diff reviewed (Radia):** `origin/dev`…feature tip at merge-base `50aed96` (pre-rebase).  
**Implementation commit:** `f00f7c2d` — rebased single commit on current `dev`; gate code matches Radia-reviewed `3ce9323a`.  
**Reviewed:** 2026-05-04 — Radia (`e-review-linear`). Doc-only follow-ups may land in later commits on this branch.

### What's solid

- **Plan fidelity:** `ASTRAL_CONFIG` literals for URL + timeout; **`src/utils/network.check_internet_reachable`** uses stdlib only (`urllib`) and imports **`config` only** (§3.3); gate at top of **`_run_unified`** before consult imports / **`get_new_*_batch`** (§2.4 — no claim when offline).
- **Semantics:** Treats non-5xx HTTP as success after reading one byte (TLS + headers exercised); failures return **`False`** without noisy logging in utils (dispatcher owns the skip warning).
- **Operator signal:** `_sched_log.warning` includes `task_key` and `log_batch_id` placeholder; early **`return dict(_SUMMARY_ZERO)`** matches the plan’s “zeros, no claim” story.

### Issues

| Severity | Topic | Notes |
|----------|--------|--------|
| — | — | No fix-now items. |
| — | — | No discuss items. |
| Advisory | **Blocking `urllib` inside `async def _run_unified`** | Acceptable per plan for bounded timeout; worth a later **`asyncio.to_thread`** pass only if profiling shows event-loop stalls under many concurrent AUTO threads. |
| Advisory | **In-repo `1-check-linear` skill on the branch** | **Resolved:** file removed from this branch so the PR vs `dev` stays scoped to AST-377; user-local skills now live only under **`~/.cursor/skills/`** (not the repo). |

### Recommended actions

| Priority | Action | Owner |
|----------|--------|-------|
| Advisory | Skill file scope: dropped `1-check-linear` from branch (see **Resolution**). | Betty |
| Advisory | After first prod deploy, confirm firewall allowlist permits the chosen Anthropic URL from Railway egress. | Ops |

---

## Resolution

**Date:** 2026-05-04 — Betty (`f-resolve-linear`)

- **Fix-now / discuss:** None in Radia’s review; **no code changes** to `dispatcher.py` / `network.py` / `config.py`.
- **Advisory — sync `urllib` in `_run_unified`:** Left as-is (bounded timeout; `asyncio.to_thread` only if profiling warrants).
- **Advisory — `1-check-linear` skill:** Removed from this branch so merge vs `dev` does not widen the AST-377 PR with agent workflow files.
- **Build:** Compile + lint run clean before commit (see repo commands in this commit’s message context).

