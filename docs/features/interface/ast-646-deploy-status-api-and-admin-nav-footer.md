# Deploy status API and admin nav footer

**Linear:** [AST-646](https://linear.app/astralcareermatch/issue/AST-646/deploy-status-api-and-admin-nav-footer-show-environment-and-up-time-as)  
**Parent:** [AST-640](https://linear.app/astralcareermatch/issue/AST-640/show-environment-and-up-time-as-read-only-at-the-bottom-of-nav-for)  
**Publish ref:** `sub/AST-640/AST-646-deploy-status-api-and-admin-nav-footer`

Administrators need an at-a-glance deploy signal in the left nav: which environment the server is running, which commit tip is live, and how long the current process has been up. This ticket adds an admin-only `GET /api/deploy_status` endpoint (server-sourced truth) and a read-only footer pinned to the bottom of `NavigationShell`, visible only when `is_admin` is true.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `DEPLOY_STATUS_CONFIG` with allowed environment labels | utils |
| `src/utils/deploy_status.py` | New module: process boot time, git tip, env resolution, uptime formatting | utils |
| `src/ui/api/api_system.py` | Add `GET /api/deploy_status` with `@require_admin` | ui |
| `env.example` | Document `ASTRAL_DEPLOY_ENV` | docs |
| `src/ui/frontend/src/components/AdminDeployFooter.tsx` | New read-only footer component | ui |
| `src/ui/frontend/src/components/NavigationShell.tsx` | Render footer for admins; keep spacer for non-admins | ui |
| `src/ui/frontend/src/App.css` | Styles for `.nav-deploy-footer` | ui |

**QA manifest (Betty — not engineer commits):** extend `tests/component/ui/api/test_api_system.py` with `TestDeployStatus` covering: 401 without Bearer; 403 for non-admin; 200 for admin with expected JSON keys; `environment` omitted when env var unset/invalid; `uptime` format samples (`<1m`, `5m`, `1h15m`, `3d22h07m`) via monkeypatched boot time and `format_uptime_seconds`; commit fields present (monkeypatch `_git_head_info`).

## Stage 1: Deploy status helpers and config

**Done when:** `DEPLOY_STATUS_CONFIG` exists; `deploy_status.py` exports `get_deploy_status_payload()` returning a dict with resolved fields; `python -m compileall src/utils/deploy_status.py` passes; no API or UI wiring yet.

1. In `src/utils/config.py`, after `RAILWAY_CONFIG` block (~line 1952), add:
   ```python
   # ---------------------------------------------------------------------------
   # DEPLOY_STATUS_CONFIG: admin nav footer — allowed deploy environment labels.
   # Actual value read from ASTRAL_DEPLOY_ENV env var (optional; see deploy_status.py).
   # ---------------------------------------------------------------------------
   DEPLOY_STATUS_CONFIG = {
       "allowed_environments": ("local", "test", "staging", "production"),
   }
   ```
   Update the module header comment list (~lines 12–26) to include `DEPLOY_STATUS_CONFIG`.

2. Create `src/utils/deploy_status.py` with module docstring: server-side deploy status for admin nav footer (AST-646). Imports: `os`, `subprocess`, `time`; `DEPLOY_STATUS_CONFIG` from `src.utils.config`; `_PROJECT_ROOT` pattern — use `Path(__file__).resolve().parent.parent.parent` (same depth as `config.py`).

3. At module load in `deploy_status.py`, set `_PROCESS_BOOT_TIME = time.time()` (wall clock at first import of this module — one value per worker process).

4. In `deploy_status.py`, implement `format_uptime_seconds(seconds: float) -> str`:
   - If `seconds < 60`: return `"<1m"`.
   - Let `total_minutes = int(seconds // 60)`.
   - If `total_minutes < 60`: return `f"{total_minutes}m"` (no zero-padding).
   - Let `total_hours = total_minutes // 60`, `rem_minutes = total_minutes % 60`.
   - If `total_hours < 24`: return `f"{total_hours}h{rem_minutes}m"`.
   - Let `total_days = total_hours // 24`, `rem_hours = total_hours % 24`, `rem_mins = total_minutes % 60`.
   - Return `f"{total_days}d{rem_hours}h{rem_mins:02d}m"` (minutes zero-padded to two digits when days ≥ 1).

5. In `deploy_status.py`, implement `_resolve_environment() -> str | None`:
   - Read `raw = os.environ.get("ASTRAL_DEPLOY_ENV", "").strip().lower()`.
   - If `raw` is empty: return `None`.
   - If `raw` not in `DEPLOY_STATUS_CONFIG["allowed_environments"]`: return `None` (graceful omission — do not crash, do not return invalid label).
   - Return `raw`.

6. In `deploy_status.py`, implement `_git_head_info() -> tuple[str, str]` returning `(commit_short, commit_message)`:
   - `cwd = Path(__file__).resolve().parent.parent.parent` (repo root).
   - Run `git rev-parse --short=7 HEAD` with `subprocess.run(..., capture_output=True, text=True, timeout=2, cwd=cwd)`.
   - On success with returncode 0 and non-empty stdout: `commit_short = stdout.strip()`.
   - Run `git log -1 --format=%s` same way for `commit_message`.
   - On any failure (no git, not a repo, timeout): return `("unknown", "")` — never raise to caller.

7. In `deploy_status.py`, implement `get_deploy_status_payload() -> dict`:
   ```python
   uptime_seconds = max(0.0, time.time() - _PROCESS_BOOT_TIME)
   commit_short, commit_message = _git_head_info()
   payload = {
       "commit_short": commit_short,
       "commit_message": commit_message,
       "uptime": format_uptime_seconds(uptime_seconds),
       "uptime_seconds": int(uptime_seconds),
   }
   env = _resolve_environment()
   if env is not None:
       payload["environment"] = env
   return payload
   ```
   Do not include `"environment"` key when unresolved (not `null` string in JSON — omit key entirely).

⚠️ **Decision:** `ASTRAL_DEPLOY_ENV` is optional with `.get()` — unlike secrets, deploy label omission is intentional when unset (parent open-question resolution). Allowed values live in `DEPLOY_STATUS_CONFIG` per rules §2.1.

⚠️ **Decision:** Git subprocess from repo root, not `config._PROJECT_ROOT` import, to keep `deploy_status.py` self-contained and avoid circular imports.

## Stage 2: Admin deploy status API endpoint

**Done when:** `GET /api/deploy_status` returns 401 without auth, 403 for non-admin, 200 JSON for admin with shape from Stage 1; `env.example` documents the env var.

1. In `src/ui/api/api_system.py`, add import: `from ui.auth import require_auth, require_admin` (extend existing `require_auth` import line).
2. Add import: `from src.utils.deploy_status import get_deploy_status_payload`.
3. After the `/api/me` route block (~line 120), add:
   ```python
   @system_bp.route("/deploy_status")
   @require_admin
   def deploy_status():
       return jsonify(get_deploy_status_payload())
   ```
4. In `env.example`, after the `ASTRAL_ALLOWED_IPS` block (~line 20), add:
   ```
   # Deploy environment label for admin nav footer (optional).
   # When set, must be one of: local, test, staging, production.
   # When unset or invalid, admin footer shows commit + uptime only.
   ASTRAL_DEPLOY_ENV=local
   ```

## Stage 3: Admin nav footer UI

**Done when:** Signed-in admin sees a compact read-only line at the bottom of the left sidebar with environment (when present), short commit hash (tooltip = commit message), and uptime; non-admin users see no footer (existing spacer preserved); footer refetches every 30s like nav config.

1. Create `src/ui/frontend/src/components/AdminDeployFooter.tsx`:
   - Import `useEffect`, `useState` from `react`; `useAuth` from `../contexts/AuthContext`; `api` from `../lib/api`.
   - Type `DeployStatus = { environment?: string; commit_short: string; commit_message: string; uptime: string; uptime_seconds: number }`.
   - Component returns `null` when `loading` from `useAuth()` or when fetch has not succeeded yet (no error flash for non-admins — parent only mounts this for admins).
   - `useEffect`: when auth not loading, call `api("/api/deploy_status")`, parse JSON on 200, set state; on failure set `error` true. `setInterval` 30_000 ms, cleanup on unmount. Deps: `[authLoading]` from `useAuth()`.
   - Render:
     ```tsx
     <div className="nav-deploy-footer" aria-label="Deploy status">
       {status.environment != null && (
         <>
           <span className="nav-deploy-env">{status.environment}</span>
           <span className="nav-deploy-sep">·</span>
         </>
       )}
       <span className="nav-deploy-commit" title={status.commit_message || undefined}>
         {status.commit_short}
       </span>
       <span className="nav-deploy-sep">·</span>
       <span className="nav-deploy-uptime">{status.uptime}</span>
     </div>
     ```
   - On fetch error, render `<div className="nav-deploy-footer nav-deploy-footer-error">Deploy status unavailable</div>` (still pinned at bottom).
   - No buttons, links, or copy actions.

2. In `src/ui/frontend/src/components/NavigationShell.tsx`:
   - Import `AdminDeployFooter`.
   - Replace the unconditional `<span className="nav-footer-spacer" />` (~line 129) with:
     ```tsx
     {isAdmin ? <AdminDeployFooter /> : <span className="nav-footer-spacer" />}
     ```
   - Do not fetch deploy status when `!isAdmin`.

3. In `src/ui/frontend/src/App.css`, after `.nav-footer-spacer` block (~line 209), add:
   ```css
   .nav-deploy-footer {
     margin-top: auto;
     flex-shrink: 0;
     padding: 10px 12px 14px;
     border-top: 1px solid var(--border);
     font-size: 11px;
     line-height: 1.4;
     color: var(--text-muted);
     font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
   }
   .nav-deploy-footer-error {
     color: var(--danger);
   }
   .nav-deploy-env {
     color: var(--text-secondary);
     text-transform: lowercase;
   }
   .nav-deploy-sep {
     margin: 0 4px;
     opacity: 0.6;
   }
   .nav-deploy-commit {
     color: var(--text-secondary);
     cursor: default;
   }
   .nav-deploy-uptime {
     color: var(--text-muted);
   }
   ```

⚠️ **Decision:** Periodic 30s re-fetch (same interval as `nav_config`) instead of client-side uptime ticking — keeps all uptime formatting on the server per Interface dumb-frontend rule; no duplicated format logic in React.

⚠️ **Decision:** `margin-top: auto` on `.nav-deploy-footer` pins the strip to the sidebar bottom without the 80px spacer; non-admins keep `.nav-footer-spacer` so layout is unchanged for them.

## Self-Assessment

**Scope:** `Single-Component` — one new utils module, one system API route, one small React component, and sidebar CSS; no core, data, or dispatch changes.

**Conf:** `high` — follows existing `@require_admin` / `isAdmin` patterns from AST-611; uptime rules and env-var graceful omission are fully specified in AST-640/646; git subprocess fallback is a known pattern.

**Risk:** `low` — read-only admin-only display; wrong label or uptime is confusing but does not affect dispatch, data integrity, or non-admin UX.

## Rules self-review

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Uptime formatting and deploy resolution centralized in `deploy_status.py`; API and UI consume one payload builder. |
| §2.1 config | Allowed environment set in `DEPLOY_STATUS_CONFIG`; optional deploy label from env var per ticket (not a secret). |
| §2.4 batch | N/A — no batch processing. |
| §2.6 state machine | N/A. |
| §3.3 imports | `deploy_status.py` in utils; `api_system.py` imports utils only; frontend uses `api()` helper. |
| §3.5 naming | `get_deploy_status_payload`, `AdminDeployFooter`, `ASTRAL_DEPLOY_ENV` match existing conventions. |

## Execution contract (for the developer agent)

- Execute stages in order. **Stop** on ambiguity — comment on **AST-640** parent with 🛑 template from **plan-child**.
- Blocking questions → comment on **AST-640** parent with 🛑 format from **plan-child**.

## Review stub (Katherine / build)

**Publish ref:** `origin/sub/AST-640/AST-646-deploy-status-api-and-admin-nav-footer`  
**Product commits:** `7810b2ac` (deploy status helpers + config), `3ef85eae` (admin API endpoint), `71ecb534` (admin nav footer UI)

## Review

**Diff:** `origin/dev...origin/sub/AST-640/AST-646-deploy-status-api-and-admin-nav-footer` @ `1647c04e`  
**Reviewed:** 2026-06-14

### What's solid

| Area | Notes |
|------|-------|
| Plan fidelity | Stages 1–3 match spec: `DEPLOY_STATUS_CONFIG` + `deploy_status.py` payload builder; `GET /api/deploy_status` with `@require_admin`; `AdminDeployFooter` + `isAdmin` gate in `NavigationShell`; `env.example` documents `ASTRAL_DEPLOY_ENV`. |
| Acceptance criteria | Betty manifest covers 401/403/200, environment omission, uptime format samples (`<1m`, `5m`, `1h15m`, `3d22h07m`), admin vs non-admin footer visibility, error state. |
| §2.1 config | Allowed environment set in `DEPLOY_STATUS_CONFIG`; optional deploy label via `os.environ.get` documented in plan (intentional omission, not a secret). |
| §3.3 layers | `deploy_status.py` in utils (config only); `api_system.py` imports utils; frontend renders API fields via `api()` — dumb-frontend rule satisfied. |
| §3.5 naming | `get_deploy_status_payload`, `AdminDeployFooter`, `ASTRAL_DEPLOY_ENV` align with conventions. |
| Admin gating | API `@require_admin` (401 via `@require_auth`, 403 non-admin) + UI mount only when `isAdmin` — consistent with AST-611 patterns. |
| Scope | Self-assessment `scope-Single-Component` / `conf-high` / `risk-low` matches diff footprint; no sibling scope bleed. |

### Issues

| Severity | Location | Note |
| --- | --- | --- |
| advisory | `deploy_status.py` `_git_head_info()` | Two `git` subprocess calls per `/api/deploy_status` request (30s admin poll). Low traffic; acceptable. Optional future cache if Railway latency matters — not blocking. |
| advisory | `deploy_status.py` L61–62 | Graceful `("unknown", "")` on git failure is intentional per plan (Railway image may lack `.git`); not a §D2 silent-failure violation — bounded read-only display. |

### Recommended actions

| Priority | Action |
|----------|--------|
| resolve-child | None required — proceed to §9a / User Testing. |
| UAT | Confirm `ASTRAL_DEPLOY_ENV` on Railway staging/production; verify admin footer after deploy restart (AC6). |

**Verdict:** Approve for `resolve-child` — no fix-now or discuss items.
