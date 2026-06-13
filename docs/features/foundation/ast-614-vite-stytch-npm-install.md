# AST-614 — UAT: Local Vite dev fails — @stytch/react not installed (Use stytch for user authentication)

- **Linear (this ticket):** [AST-614](https://linear.app/astralcareermatch/issue/AST-614/uat-local-vite-dev-fails-stytchreact-not-installed-use-stytch-for-user)
- **Parent:** [AST-609](https://linear.app/astralcareermatch/issue/AST-609/use-stytch-for-user-authentication)
- **Publish ref:** `origin/sub/AST-609/AST-614-vite-stytch-npm-install`
- **Triggered by:** [AST-612](https://linear.app/astralcareermatch/issue/AST-612/react-stytch-login-and-admin-ui-gating-use-stytch-for-user) adding `@stytch/react` to `package.json` without a local install path when skipping `scripts/setup_dev.sh`

## Summary

After AST-612 merged, `launch.sh --vite` runs `npm run dev` in `src/ui/frontend/` without ensuring `node_modules` exists. Fresh clones or pulls that skip `scripts/setup_dev.sh` hit `Failed to resolve import "@stytch/react"`. This ticket adds a minimal guard in `launch.sh` so Vite dev auto-runs `npm install --include=dev` when frontend deps are missing (using `@stytch/react` as the sentinel for AST-612+). No Stytch UX, redirect URL, or backend auth changes.

## Layer contract (mandatory)

| Layer | This ticket | Import rule |
|-------|-------------|-------------|
| `launch.sh` | Auto-install frontend deps before `npm run dev` | repo-root dev script |
| `scripts/setup_dev.sh` | **Read-only** — already runs `npm install` in step 5 | do not refactor into shared library |
| `src/ui/frontend/*`, Flask, Stytch Python | **Read-only** — AST-610/611/612/613 | do not modify |

⚠️ **Decision:** Fix **`launch.sh` only** — `setup_dev.sh` already installs frontend deps on full setup; duplicating logic there adds no value. Susan's repro skips setup, not setup's npm step.

⚠️ **Decision:** Sentinel check **`node_modules/@stytch/react`** (not bare `node_modules/`). Catches the reported failure and future "pulled package.json but never re-ran npm install" without running `npm install` on every Vite start when deps are healthy.

⚠️ **Decision:** Use **`npm install --include=dev`** — matches `scripts/setup_dev.sh` (line 71) and `scripts/build_railway.sh` (line 6). Do not add `npm ci` or a new install script.

## Out of scope (explicit)

| Item | Owner |
|------|-------|
| Stytch login UX, redirect URLs | **AST-612** / **AST-613** |
| Flask auth, `@require_auth`, admin API | **AST-610** / **AST-611** |
| `tests/` or `docs/ASTRAL_TEST_BIBLE.md` commits | **Betty** (`qa-child`) — engineer hook blocks |
| New standalone install script | — (ticket boundary) |

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `launch.sh` | Add `_ensure_frontend_deps`; call from `run_vite` before `npm run dev` | dev script |

## Stage 1: Auto-install frontend deps in `launch.sh`

**Done when:** With `src/ui/frontend/node_modules` removed (or `@stytch/react` missing), `zsh launch.sh --vite` prints an install notice, runs `npm install --include=dev`, then starts Vite without `@stytch/react` import errors; with deps present, no install runs and startup is unchanged.

1. In `launch.sh`, after the `WORKDIR` / `SCRIPT_PATH` setup (before `run_flask`), add:

```zsh
FRONTEND_DIR="${WORKDIR}/src/ui/frontend"

_ensure_frontend_deps() {
  cd "${FRONTEND_DIR}"
  if [[ ! -d node_modules/@stytch/react ]]; then
    print -u2 "installing frontend deps (missing node_modules/@stytch/react)..."
    npm install --include=dev
  fi
}
```

2. In `run_vite()`, replace the body so it calls the guard before dev:

```zsh
run_vite() {
  _ensure_frontend_deps
  cd "${FRONTEND_DIR}"
  print -u2 "vite-dev http://localhost:5173 (Ctrl-C to stop)"
  exec npm run dev
}
```

(Remove the old inline `cd "${WORKDIR}/src/ui/frontend"` — `FRONTEND_DIR` is canonical.)

3. **Manual verify** (engineer, before Code Complete):

```bash
rm -rf src/ui/frontend/node_modules
zsh launch.sh --vite
# Expect: install message, then Vite on :5173; browser loads Login without import error
```

4. **Regression:** With `node_modules` intact, `zsh launch.sh --vite` must **not** print the install message.

⚠️ **Decision:** No `setup_dev.sh` edit — full setup path already correct; ticket asks for `launch.sh --vite` ergonomics after pull-without-setup.

## Stage 2: Close ticket

**Done when:** Stage 1 committed and published; engineer moves AST-614 to **Code Complete** (assignee stays Katherine).

1. Commit message: `fix(AST-614): auto-install frontend deps in launch.sh --vite`
2. Move **AST-614** to **Code Complete**.

## Self-Assessment

**Scope:** `minor` — Only `launch.sh` is touched; no application layers.

**Conf:** `high` — Same `npm install --include=dev` pattern as existing setup and Railway build scripts; sentinel matches the reported missing package.

**Risk:** `low` — Guard runs only when `@stytch/react` is absent; no change to production build path or runtime auth.

## ASTRAL_CODE_RULES self-review

| Rule | Applicability |
|------|----------------|
| §1.3 DRY | No new shared module; one small guard mirrors existing npm invocations in `setup_dev.sh` / `build_railway.sh` — acceptable for repo-root script. |
| §2.1 config | N/A — no config changes. |
| §3.3 imports | N/A — shell only. |
| §3.5 naming | `_ensure_frontend_deps` follows existing `launch.sh` private-function style (`_tab_cmd`, `_spawn_tab`). |

No conflicts — plan is implementable as written.
