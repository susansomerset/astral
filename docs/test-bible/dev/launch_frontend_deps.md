# Launch Frontend Deps

**Test module:** `tests/component/dev/test_launch_frontend_deps.py`

### AST-614 · AST-609

`launch.sh --vite` auto-runs `npm install --include=dev` when `node_modules/@stytch/react` missing.

| Area | Source | Component tests |
| --- | --- | --- |
| Vite path deps install | `launch.sh` (`_ensure_frontend_deps`, `run_vite`) | `TestLaunchFrontendDeps` |

### AST-758 · AST-744

Susan UAT: local `dev` pull updated TSX but Flask `:5001` served stale gitignored `frontend/dist/`. Auto-rebuild stale/missing dist on `launch.sh --flask` only (Vite path unchanged).

| Area | Source | Component tests |
| --- | --- | --- |
| Flask path dist rebuild | `launch.sh` (`_ensure_frontend_build`, `run_flask`) | `TestLaunchFrontendBuild::{test_run_flask_rebuilds_when_dist_older_than_src,test_run_flask_skips_build_when_dist_is_fresh}` |

**AST-758** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/dev/test_launch_frontend_deps.py::TestLaunchFrontendBuild \
  -q
```

**Manual UAT (Susan):** On local `dev` after `git pull`, run `zsh launch.sh --flask` without manual `npm run build`; open `:5001` → Scheduled Actions → confirm AST-746 column layout (no Candidate/Task gap; Entity does not overlay State).
