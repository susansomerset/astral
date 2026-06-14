# AST-651 — UAT: show raw ASTRAL_DEPLOY_ENV without allowlist validation

**Linear:** [AST-651 — UAT: show raw ASTRAL_DEPLOY_ENV without allowlist validation](https://linear.app/astralcareermatch/issue/AST-651/uat-show-raw-astral-deploy-env-without-allowlist-validation)  
**Parent:** [AST-640 — Show environment and up time as read-only at the bottom of nav for admin view only](https://linear.app/astralcareermatch/issue/AST-640/show-environment-and-up-time-as-read-only-at-the-bottom-of-nav-for) (AC reference only)  
**Publish ref:** `origin/sub/AST-640/AST-651-uat-show-raw-astral-deploy-env-without-allowlist-validation` (origin only)

## Summary

AST-646 added admin deploy footer environment labels gated by `DEPLOY_STATUS_CONFIG["allowed_environments"]`. Susan deploys to region-specific labels (e.g. `eu-west`) outside that fixed set; when `ASTRAL_DEPLOY_ENV` is set to any non-empty string, the footer must show that text. When unset or whitespace-only, omit the environment label (commit + uptime only). This UAT bug removes allowlist validation and dead config; no UI, auth, uptime, or commit changes.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/deploy_status.py` | `_resolve_environment`: return stripped raw env text; drop allowlist check and `DEPLOY_STATUS_CONFIG` import | utils |
| `src/utils/config.py` | Remove `DEPLOY_STATUS_CONFIG` block and module header reference | utils |
| `env.example` | Document that any non-empty `ASTRAL_DEPLOY_ENV` displays; remove allowlist wording | docs |
| `tests/component/utils/test_deploy_status.py` | Replace invalid→None test with arbitrary label test (Betty manifest — engineer runs in test-child) | test |

**Verify only (no change expected):**

| File | Role |
|------|------|
| `src/ui/api/api_system.py` | Already returns `get_deploy_status_payload()` JSON |
| `src/ui/frontend/src/components/AdminDeployFooter.tsx` | Already renders `status.environment` when present |
| `tests/component/ui/api/test_api_system.py` | Mocks payload builder; no allowlist logic in API layer |
| `tests/component/frontend/components/test_AdminDeployFooter.test.tsx` | Renders whatever API returns |

**Out of scope:** commit hash/tooltip, uptime formatting, admin-only gating, 30s poll, `@require_admin`, new env vars.

---

## Stage 1: Remove allowlist from environment resolution

**Done when:** Any non-empty `ASTRAL_DEPLOY_ENV` (after strip) appears in `get_deploy_status_payload()["environment"]`; unset/whitespace-only omits the key; `python3 -m py_compile src/utils/deploy_status.py` passes.

1. In `src/utils/deploy_status.py`, remove the import line:
   ```python
   from src.utils.config import DEPLOY_STATUS_CONFIG
   ```

2. Replace `_resolve_environment()` body with:
   ```python
   def _resolve_environment() -> str | None:
       raw = os.environ.get("ASTRAL_DEPLOY_ENV", "").strip()
       if not raw:
           return None
       return raw
   ```
   ⚠️ **Decision:** Use `.strip()` only — no `.lower()` — so the footer shows the operator's label as set (supports `eu-west`, `EU-WEST`, etc.). Empty after strip still omits the label (unchanged graceful behavior).

3. Do **not** change `format_uptime_seconds`, `_git_head_info`, or `get_deploy_status_payload` structure beyond what falls out of step 2.

4. `python3 -m py_compile src/utils/deploy_status.py`

**Ritual:** `code(AST-651): return raw ASTRAL_DEPLOY_ENV without allowlist`

---

## Stage 2: Remove dead deploy-status config and update env.example

**Done when:** `DEPLOY_STATUS_CONFIG` is gone from `config.py`; `env.example` no longer references the old four-value allowlist.

1. In `src/utils/config.py`, delete the entire `DEPLOY_STATUS_CONFIG` block (~lines 1955–1961) including its section comment.

2. In the module header comment list (~line 27), remove the line referencing `DEPLOY_STATUS_CONFIG`.

3. In `env.example`, replace the deploy env comment block (~lines 22–24) with:
   ```
   # Deploy environment label for admin nav footer (optional).
   # When set to any non-empty string, admin footer shows that text as the environment label.
   # When unset or empty, admin footer shows commit + uptime only.
   ASTRAL_DEPLOY_ENV=local
   ```

4. `python3 -m py_compile src/utils/config.py`

**Ritual:** `code(AST-651): drop DEPLOY_STATUS_CONFIG and update env.example`

---

## Stage 3: Component tests (Betty manifest / test-child)

**Done when:** `tests/component/utils/test_deploy_status.py` proves arbitrary env labels resolve and whitespace-only still omits environment.

Betty adds to **Tests Ready** manifest. If omitted, engineer adds only:

1. In `tests/component/utils/test_deploy_status.py`, inside `TestResolveEnvironment`:
   - Rename **`test_invalid_returns_none`** → **`test_non_allowlisted_value_returns_raw`**
   - Change setup: `monkeypatch.setenv("ASTRAL_DEPLOY_ENV", "eu-west")`
   - Assert: `assert ds._resolve_environment() == "eu-west"`

2. Add **`test_whitespace_only_returns_none`**:
   - `monkeypatch.setenv("ASTRAL_DEPLOY_ENV", "   ")`
   - Assert: `assert ds._resolve_environment() is None`

3. Keep **`test_valid_local`** unchanged (still passes with raw resolver).

4. Re-run `tests/component/utils/test_deploy_status.py`.

**Ritual:** `test(AST-651): deploy env accepts any non-empty ASTRAL_DEPLOY_ENV`

---

## Execution contract reminders

- Do **not** edit `AdminDeployFooter.tsx` or API routes — payload change alone fixes UAT repro.
- Do **not** edit `tests/` or `docs/ASTRAL_TEST_BIBLE.md` in **build-child** — Betty owns manifest; engineer runs tests in **test-child**.
- Blocking ambiguity → `🛑` comment on **AST-640** parent.

---

## Self-Assessment

**Scope:** `minor` — Three small edits in utils/docs plus targeted test renames in one component test file.

**Conf:** `high` — UAT repro maps directly to `_resolve_environment()` allowlist guard at `deploy_status.py` L34–35; removal is a one-function change with existing test harness.

**Risk:** `low` — Display-only admin footer label; wrong change would omit or mislabel environment text but would not affect auth, persistence, or dispatch.

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Resolution stays in `_resolve_environment()`; API and UI unchanged |
| §2.1 config | Removes unused `DEPLOY_STATUS_CONFIG`; deploy label remains optional env var per ticket (not a secret) |
| §2.4 batch | N/A |
| §2.6 state machine | N/A |
| §3.3 imports | Drops config import from `deploy_status.py`; no layer violations |
| §3.5 naming | No new public symbols |

No conflicts requiring `conf-!!-NONE`.

---

## Review

**Built:** `code(AST-651): return raw ASTRAL_DEPLOY_ENV without allowlist` → `code(AST-651): drop DEPLOY_STATUS_CONFIG and update env.example`  
**Branch:** `origin/sub/AST-640/AST-651-uat-show-raw-astral-deploy-env-without-allowlist-validation` @ `e22f56f7`

---

## Resolution

**Date:** 2026-06-14  
**Radia review:** fix-now none; discuss none; advisory only (AST-646 plan doc still mentions allowlist — historical, not blocking).

**Outcome:** No product changes from review. Shipped as built @ `37443bba` (`7d5c5aeb` + `e22f56f7` product, `37443bba` Betty tests). §9a dry-run clean vs `origin/dev` and `origin/ftr/AST-640`.

**UAT verify:** Set `ASTRAL_DEPLOY_ENV=eu-west` (or any non-empty label), restart, sign in as admin — footer shows raw label plus commit and uptime.
