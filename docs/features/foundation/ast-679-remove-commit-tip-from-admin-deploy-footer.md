# Remove commit tip from admin deploy footer

**Linear:** [AST-679](https://linear.app/astralcareermatch/issue/AST-679/remove-commit-tip-from-admin-deploy-footer-drop-sha-tip-from-nav)  
**Parent:** [AST-658](https://linear.app/astralcareermatch/issue/AST-658/drop-sha-tip-from-nav-display)  
**Publish ref:** `sub/AST-658/AST-679-remove-commit-tip-from-admin-deploy-footer`

Railway deploy images lack a `.git` tree, so the admin nav footer often shows a meaningless commit hash (`unknown`) or runs useless git subprocesses. This ticket removes commit tip fields from `GET /api/deploy_status` and from `AdminDeployFooter`. The footer shows only deploy environment (when configured) and server uptime — same admin gating, refresh interval, and uptime formatting as AST-640/AST-646.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/deploy_status.py` | Remove `_git_head_info`, git subprocess, commit keys from payload | utils |
| `src/ui/frontend/src/components/AdminDeployFooter.tsx` | Remove commit display and type fields | ui |
| `src/ui/frontend/src/App.css` | Remove obsolete `.nav-deploy-commit` rule | ui |
| `tests/component/utils/test_deploy_status.py` | Drop commit assertions; remove `_git_head_info` mocks | tests |
| `tests/component/ui/api/test_api_system.py` | Update `TestDeployStatus` expected JSON (no commit keys) | tests |
| `tests/component/frontend/components/test_AdminDeployFooter.test.tsx` | Assert env + uptime only; no commit text/tooltip | tests |
| `tests/component/frontend/components/test_NavigationShell.test.tsx` | Remove commit from deploy_status mocks and assertions | tests |

**QA manifest (Betty — not engineer commits):** Betty may update `docs/test-bible/**` manifests after tests land; engineer does not commit test-bible files (pre-commit hook).

## Stage 1: Backend — slim deploy status payload

**Done when:** `get_deploy_status_payload()` returns only `uptime`, `uptime_seconds`, and optional `environment`; no git subprocess runs; backend component tests pass; `python -m compileall src/utils/deploy_status.py` succeeds.

1. In `src/utils/deploy_status.py`, delete the entire `_git_head_info()` function (lines 50–73).
2. In the same file, remove unused imports: `subprocess`, `Path`, and the `_REPO_ROOT` constant (only used for git cwd).
3. In `get_deploy_status_payload()`, remove the `commit_short, commit_message = _git_head_info()` line and remove `"commit_short"` and `"commit_message"` from the `payload` dict. The function must return exactly:
   ```python
   payload = {
       "uptime": format_uptime_seconds(uptime_seconds),
       "uptime_seconds": int(uptime_seconds),
   }
   ```
   plus optional `"environment"` when `_resolve_environment()` is not `None` (same omission rule as today — no key when unset).
4. Do **not** change `format_uptime_seconds`, `_resolve_environment`, `get_deploy_label`, `is_local_deploy_env`, or `ui_llm_debug`.
5. Do **not** change `src/ui/api/api_system.py` — it already returns `jsonify(get_deploy_status_payload())`; shape change is sufficient.

6. In `tests/component/utils/test_deploy_status.py`, class `TestGetDeployStatusPayload`:
   - In `test_includes_commit_and_uptime_without_environment`, rename to `test_includes_uptime_without_environment`.
   - Remove `monkeypatch.setattr(ds, "_git_head_info", ...)`.
   - Remove assertions on `commit_short` and `commit_message`.
   - Keep assertions: `uptime == "<1m"`, `uptime_seconds == 45`, `"environment" not in payload`.
7. In the same class, `test_includes_environment_when_set`:
   - Remove `_git_head_info` monkeypatch.
   - Assert `environment == "staging"`, `uptime == "1h1m"`; do not assert commit fields.
8. In `tests/component/ui/api/test_api_system.py`, class `TestDeployStatus`:
   - In `test_admin_returns_payload`, remove `commit_short` and `commit_message` from `expected` dict.
   - In `test_admin_omits_environment_when_unset`, remove commit keys from `payload` dict.
   - In `test_admin_uptime_format_samples_via_payload_builder`, remove `monkeypatch.setattr(ds_mod, "_git_head_info", ...)` line (no longer needed).

⚠️ **Decision:** Remove commit fields from the API entirely (not optional/null) so Railway never runs git and clients cannot accidentally render stale commit data. Uniform omission on all deploy targets matches parent AC.

## Stage 2: Frontend — footer UI and component tests

**Done when:** Admin footer shows environment (when present) and uptime only; no commit hash, tooltip, or separator before uptime when commit is gone; non-admin behavior unchanged; frontend component tests pass; `npm run build` in `src/ui/frontend` succeeds.

1. In `src/ui/frontend/src/components/AdminDeployFooter.tsx`, update type `DeployStatus`:
   - Remove `commit_short: string` and `commit_message: string`.
   - Keep `environment?: string`, `uptime: string`, `uptime_seconds: number`.
2. In the success render branch, remove the commit `<span className="nav-deploy-commit">` block and the `<span className="nav-deploy-sep">` that immediately follows it (the sep between commit and uptime).
   - When `environment` is set: render `env · uptime` (env span, sep, uptime span) — same as today minus commit.
   - When `environment` is unset: render only the uptime span (no leading sep).
3. Do **not** change the 30s poll interval, error branch, or `authLoading` early return.
4. In `src/ui/frontend/src/App.css`, delete the `.nav-deploy-commit { ... }` rule block (lines 231–234). Leave `.nav-deploy-footer`, `.nav-deploy-env`, `.nav-deploy-sep`, `.nav-deploy-uptime` unchanged.

5. In `tests/component/frontend/components/test_AdminDeployFooter.test.tsx`:
   - Rename first test to `renders environment and uptime when deploy_status succeeds`.
   - Remove `commit_short` and `commit_message` from mock JSON for `/api/deploy_status`.
   - Remove `expect(screen.getByText("abc1234"))...` assertion.
   - Keep `local`, `5m` assertions.
   - In `omits environment label when API payload has no environment`, remove commit fields from mock; change `waitFor` to expect `screen.getByText("<1m")` instead of `deadbeef`.
6. In `tests/component/frontend/components/test_NavigationShell.test.tsx`:
   - In the admin nav test mock for `/api/deploy_status`, remove `commit_short` and `commit_message`.
   - Remove `expect(screen.getByText("abc1234")).toBeInTheDocument()`.
   - In the loading/error test mock, remove commit fields from deploy_status JSON.

## Execution contract (for the developer agent)

The plan is binding. Execute stages in order. One commit per stage on the active sub branch, then publish to `origin/sub/AST-658/AST-679-remove-commit-tip-from-admin-deploy-footer`. Do not add Railway links, PR numbers, build IDs, Performance Monitor changes, `/health` changes, admin gating changes, or footer refresh interval changes.

## Self-Assessment

**Scope:** `Single-Component` — One cohesive admin deploy readout across `deploy_status.py`, `AdminDeployFooter`, CSS, and matching component tests; no other modules consume commit fields from this API.

**Conf:** `high` — Straight removal of AST-646 commit tip code; uptime and environment behavior stay as shipped; tests and mocks are enumerated.

**Risk:** `low` — Wrong change would only affect admin-only nav footer display and its API; non-admin layout and core app paths are untouched.

## Self-Review (ASTRAL_CODE_RULES)

| Rule area | Assessment |
|-----------|------------|
| §1.3 DRY | Removing dead git helper and CSS avoids duplicate/stale paths; no new duplication. |
| §2.1 config | No new config; env resolution unchanged. |
| §2.4 batch | N/A |
| §2.6 state machine | N/A |
| §3.3 imports | Stage 1 removes unused `subprocess` and `Path` after deleting git code. |
| §3.5 naming | Existing names retained; only commit-specific names removed. |

No conflicts requiring `conf-!!-NONE`.

## Review (build)

**Branch:** `sub/AST-658/AST-679-remove-commit-tip-from-admin-deploy-footer`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `74df6a58` | Backend: remove commit fields from deploy status payload |
| 2 | `b2a99973` | Frontend: remove commit tip from admin deploy footer UI |

**Tip:** `b2a99973`

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-658/AST-679-remove-commit-tip-from-admin-deploy-footer` (tip `9846f148`)

### What's solid

- `deploy_status.py`: `_git_head_info`, git subprocess, and commit keys removed; payload is `uptime`, `uptime_seconds`, optional `environment` only — matches plan Stage 1 and parent AC.
- `AdminDeployFooter.tsx` + `App.css`: commit span/tooltip and `.nav-deploy-commit` removed; env · uptime layout preserved; poll interval and error branch unchanged.
- Plan-enumerated component tests and Betty bible rows (`deploy_status.md`, `components.md`) align with the slimmer API shape.
- No remaining `commit_short` / `commit_message` references under `src/`. Layer imports and logging rules unchanged (§3.3, §1.5 N/A).

### Issues

| Severity | Location | Issue |
|----------|----------|-------|
| fix-now | branch commit `a0e02d28` | **Cross-ticket scope:** AST-676 craft-rubric test + bible additions (`test_agent.py`, `test_config.py`, `docs/test-bible/core/agent.md`, `docs/test-bible/utils/config.md`) landed on this AST-658 child ref. AST-676 parent is AST-655 (User Testing on Ada). Revert `a0e02d28` on this sub branch or ensure those files exist only on the AST-676 publish ref before `merge-parent`. |
| advisory | — | AST-676 hunks are additive tests/docs only; they do not block AST-679 functional AC but pollute the child diff. |

### Recommended actions

| Action | Owner |
|--------|-------|
| Revert `a0e02d28` on `sub/AST-658/AST-679-remove-commit-tip-from-admin-deploy-footer` and republish (or confirm AST-676 branch already carries equivalent commits) | Katherine |
| No product-code changes required for AST-679 scope | — |
