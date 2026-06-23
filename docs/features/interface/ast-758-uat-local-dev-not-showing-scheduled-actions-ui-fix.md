# AST-758 — UAT: local dev branch not showing scheduled actions UI fix

**Linear:** [AST-758 — UAT: local dev branch not showing scheduled actions UI fix (Remove column gap in scheduled_actions)](https://linear.app/astralcareermatch/issue/AST-758/uat-local-dev-branch-not-showing-scheduled-actions-ui-fix-remove-column)  
**Parent:** AST-744 (AC reference only — inline in ticket Description)  
**Publish ref:** `origin/sub/AST-744/AST-758-uat-local-dev-not-showing-scheduled-actions-ui-fix`

## Summary

Susan UAT (2026-06-23): after pulling local `dev`, the **Scheduled Actions** column-gap fix from **AST-746** is not visible. Investigation shows **AST-746 product code is already on `origin/dev`** (`AdminScheduledActions.tsx` byte-identical to `origin/sub/AST-744/AST-746-fix-scheduled-actions-table-column-gap`). Root cause is **local serving path**, not a bad merge: Flask on `:5001` serves **`src/ui/frontend/dist/`** (gitignored, built once by `setup_dev.sh`); `git pull` updates **TSX source only**, so `:5001` keeps serving a **stale bundle** unless the developer rebuilds or uses Vite on `:5173`. This UAT bug rebuilds `dist/` automatically when stale before Flask starts (`launch.sh --flask`) and prints a clear stderr warning from `server.py` when debug Flask starts with stale/missing dist. **No AST-746 product changes** unless Stage 1 reproves a regression.

**Builds on:** [AST-746 plan](ast-746-fix-scheduled-actions-table-column-gap.md) — local-dev delivery gap only.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `launch.sh` | Add `_ensure_frontend_build()`; call from `run_flask` before `exec python server.py` | scripts |
| `src/ui/server.py` | Debug `__main__` startup: warn when `dist/index.html` missing or older than newest `frontend/src/**/*.{ts,tsx}` | ui |

**QA manifest (Betty — not engineer commits):** none required unless Betty chooses a smoke script; manual UAT is the pass criterion below.

**Out of scope:** `AdminScheduledActions.tsx` / AST-746 sticky logic; `prep-uat` / merge-parent; Railway staging; changing Vite proxy config; auto-starting Vite from Flask.

---

## Stage 1: Confirm landing — no product change unless regression

**Done when:** Written confirmation in this plan's execution (Linear comment only if regression found) that `origin/dev` contains AST-746 fix; if diff non-empty, stop and escalate on AST-758 — do not proceed to Stage 2.

1. On epic worktree after `git fetch origin`:
   ```bash
   git diff origin/sub/AST-744/AST-746-fix-scheduled-actions-table-column-gap origin/dev -- \
     src/ui/frontend/src/pages/AdminScheduledActions.tsx
   ```
   **Expected:** empty diff (zero lines). AST-746 `code()` commit `8c0e7c4` is on `origin/dev` history for this file.

2. Grep `origin/dev:src/ui/frontend/src/pages/AdminScheduledActions.tsx` for markers: `predecessorsReady`, `resolvedOpenSection === sec.sectionKey ? (` — both must be present.

3. If either check fails, **stop** — post on AST-758: `🛑 Stage 1 blocked: AST-746 fix not on origin/dev` with diff summary; do **not** edit product under AST-758.

4. If checks pass, proceed to Stage 2. **Do not** modify `AdminScheduledActions.tsx` in this ticket.

---

## Stage 2: Auto-rebuild stale dist in `launch.sh --flask`

**Done when:** Running `zsh launch.sh --flask` after pulling TSX changes triggers `npm run build` when `dist/index.html` is missing or any `src/ui/frontend/src/**/*.{ts,tsx}` is newer than `dist/index.html`; when dist is fresh, no build runs.

1. In `launch.sh`, after `_ensure_frontend_deps` definition (~line 37), add:

   ```zsh
   _ensure_frontend_build() {
     _ensure_frontend_deps
     cd "${FRONTEND_DIR}"
     local dist_index="dist/index.html"
     if [[ ! -f "$dist_index" ]] \
       || find src -type f \( -name '*.tsx' -o -name '*.ts' \) -newer "$dist_index" -print -quit | grep -q .; then
       print -u2 "frontend dist stale or missing — running npm run build..."
       npm run build
     fi
   }
   ```

2. In `run_flask()` (~line 42), call `_ensure_frontend_build` after `_ensure_python_deps` and before `cd "${WORKDIR}/src/ui"`:
   ```zsh
   run_flask() {
     _ensure_python_deps
     _ensure_frontend_build
     cd "${WORKDIR}/src/ui"
     print -u2 "flask-api http://localhost:5001 (Ctrl-C to stop)"
     print -u2 "tip: vite live-reload at http://localhost:5173 — launch.sh --vite"
     exec python server.py
   }
   ```

3. Do **not** call `_ensure_frontend_build` from `run_vite` (Vite serves source directly).

⚠️ **Decision:** Rebuild only on `--flask` path — matches Susan's repro (`launch.sh` / Flask `:5001`) without slowing Vite-only dev. `find -newer` works on Linux and macOS; no cross-platform `stat` parsing.

**Ritual:** `code(AST-758): rebuild stale frontend dist before flask dev start`

---

## Stage 3: Stale-dist warning in `server.py` debug startup

**Done when:** `python server.py` in debug mode prints a one-line stderr warning when dist is missing or older than source; no warning when dist is fresh; `python3 -m py_compile src/ui/server.py` passes.

1. At top of `src/ui/server.py`, ensure `import sys` is present (add if missing).

2. After `_DIST = Path(__file__).parent / "frontend" / "dist"` (~line 22), add:

   ```python
   _FRONTEND_SRC = Path(__file__).parent / "frontend" / "src"


   def _warn_stale_frontend_dist() -> None:
       """Local dev: Flask :5001 serves dist/; git pull does not rebuild it."""
       dist_index = _DIST / "index.html"
       if not _FRONTEND_SRC.is_dir():
           return
       src_files = [
           p for p in _FRONTEND_SRC.rglob("*")
           if p.suffix in (".ts", ".tsx") and p.is_file()
       ]
       if not src_files:
           return
       if not dist_index.is_file():
           print(
               "WARNING: frontend/dist missing — UI on :5001 will 404 or be stale; "
               "run: cd src/ui/frontend && npm run build (or use http://localhost:5173)",
               file=sys.stderr,
           )
           return
       dist_mtime = dist_index.stat().st_mtime
       newest_src = max(p.stat().st_mtime for p in src_files)
       if newest_src > dist_mtime:
           print(
               "WARNING: frontend/dist older than src/ — :5001 serves stale UI; "
               "rebuild (npm run build) or use http://localhost:5173 (vite)",
               file=sys.stderr,
           )
   ```

3. In `if __name__ == "__main__":` block (~line 71), call `_warn_stale_frontend_dist()` before `app.run(...)`:
   ```python
   if __name__ == "__main__":  # pragma: no cover
       _warn_stale_frontend_dist()
       app.run(debug=True, port=5001)
   ```

4. Do **not** invoke `_warn_stale_frontend_dist` at import time (gunicorn/Railway must stay silent).

**Ritual:** `code(AST-758): warn when flask debug serves stale frontend dist`

---

## Stage 4: Manual verification (required before resolve)

**Done when:** Susan repro steps pass on local `dev` worktree using `:5001` after one `git pull` **without** manual `npm run build`.

1. In main `astral` worktree on `dev`: `git fetch origin && git checkout dev && git merge origin/dev`.
2. Touch is **not** required if AST-746 source already present; optionally `touch src/ui/frontend/src/pages/AdminScheduledActions.tsx` to simulate post-pull stale dist.
3. Run `zsh launch.sh --flask` (or `cd src/ui && python server.py` after deleting `dist/index.html` to confirm warning).
4. Open `http://localhost:5001` → Admin → Scheduled Actions → expand a phase with rows.
5. Confirm: no Candidate/Task gap; Entity does not overlay State (AST-744 AC).
6. Optional: run `launch.sh --vite`, confirm `:5173` also shows fix (regression guard).

---

## Self-Assessment

**Scope:** `minor` — Two local-dev delivery files (`launch.sh`, `server.py`); no AST-746 product revert.

**Conf:** `high` — `origin/dev` already contains fix; stale `dist/` explains repro; auto-build + warning matches existing Flask/Vite split documented in `setup_dev.sh`.

**Risk:** `low` — Extra `npm run build` only when dist missing/stale on `--flask`; production gunicorn unchanged; worst case is longer local Flask startup after large frontend pulls.

---

## Code Rules self-review

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Single `_ensure_frontend_build` in launch.sh; server warning is complementary (direct `python server.py` bypass). |
| §2.1 Config | No config changes. |
| §3.3 Imports | `server.py` stays ui layer; pathlib + sys only. |
| §3.5 Naming | `_ensure_frontend_build`, `_warn_stale_frontend_dist` match existing `_ensure_*` pattern in launch.sh. |

No conflicts requiring `conf-!!-NONE`.

---

## Review (build)

**Branch:** `origin/sub/AST-744/AST-758-uat-local-dev-not-showing-scheduled-actions-ui-fix`  
**Tip:** `674012e`  
**Built:** Stage 1 confirmed AST-746 on `origin/dev` (empty diff). Stage 2 — `_ensure_frontend_build` in `launch.sh --flask`. Stage 3 — `_warn_stale_frontend_dist` in `server.py` debug startup.

**Out of build scope:** Stage 4 Susan manual UAT on `:5001` after pull without manual rebuild.

---

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-744/AST-758-uat-local-dev-not-showing-scheduled-actions-ui-fix` · tip **`d440264`**

### What's solid

| Area | Notes |
|------|-------|
| Plan fidelity | Stage 1 confirmed (empty diff vs AST-746 publish ref; markers on `origin/dev`). Stages 2–3 match plan verbatim: `_ensure_frontend_build` on `--flask` only, `_warn_stale_frontend_dist` gated to `__main__` (gunicorn silent). |
| Scope boundary | No `AdminScheduledActions.tsx` / AST-746 product changes — delivery-path fix only. |
| §3.3 layer | `server.py` adds pathlib/sys only; no cross-layer imports. |
| §1.3 DRY | launch.sh auto-build + server warning complement each other (covers `python server.py` bypass). |
| Tests | `TestLaunchFrontendBuild` exercises stale vs fresh dist; `TestWarnStaleFrontendDist` covers missing/stale/fresh stderr paths. Test-bible manifests aligned. |

### Issues

| Severity | Item | Location |
|----------|------|----------|
| — | **No fix-now.** | — |

### Recommended actions

| Action | Owner |
|--------|-------|
| **resolve-child** — no code changes required from review. | Katherine |
| **discuss (optional hygiene):** `TestWarnStaleFrontendDist` mutates `ui.server._FRONTEND_SRC` / `_DIST` module globals without restore — fine while this class is last in the module; consider `monkeypatch` teardown if more server tests land below it. | Katherine (optional) |
| Susan Stage 4 manual UAT: `git pull` → `zsh launch.sh --flask` without manual rebuild → `:5001` Scheduled Actions shows AST-746 layout. | Susan |
