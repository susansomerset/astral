# AST-2255 — platform Dockerfile test gap

No ancestor feature doc. These are the plan-fix sections for Betty's TESTS: REVISE gap child. Neither AST-2255 nor AST-2249 names a Canon Scope list. Product files from AST-2254 are already on this branch (`ftr/AST-2249-key-storage-warnings`). This ticket does not edit them.

## Bug: AST-2255 — platform Dockerfile secret ARG/ENV coverage

### As-is

Root `railway.toml` is `builder = "DOCKERFILE"` with `dockerfilePath = "Dockerfile"`, and the root `Dockerfile` does not declare the ten secret names from the AST-2249 report as `ARG` or `ENV`. Nothing in `tests/component/` or `docs/test-bible/` asserts that. `tests/component/service/test_telescope_deploy_ci.py` reads `service/telescope/railway.toml` only.

### To-be

`tests/component/service/test_platform_deploy.py` reads the root `railway.toml` and root `Dockerfile` as text and asserts the builder switch plus the absence of those secret `ARG`/`ENV` declarations. `docs/test-bible/service/platform.md` names those test nodes and the narrowed run. Against this branch the test is green: the product fix is already in the tree.

### Repro

Fixture is the two files, not a database row.

Secret names from the AST-2249 report, each warned once as `ARG` and once as `ENV`:

`ANTHROPIC_API_KEY`, `ASTRAL_ENCRYPTION_KEY`, `DEEPSEEK_API_KEY`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_CSE_API_KEY`, `GOOGLE_REFRESH_TOKEN`, `SLACK_BOT_TOKEN`, `SLACK_SIGNING_SECRET`, `STYTCH_SECRET`, `TELESCOPE_BEARER_TOKEN`.

Pre-fix shape (not this branch): root `railway.toml` has `builder = "NIXPACKS"` and there is no root `Dockerfile`. This branch's shape is the fixed files. The new test asserts the fixed shape. It is not a red-first repro against `origin/ftr/AST-2249-key-storage-warnings`.

### Root cause

AST-2254 changed only `Dockerfile` and `railway.toml`. Betty's board note was missing coverage: no component node and no bible entry for that pair. The telescope deploy test is a different service file.

### Proposed change

Add the two scoped files. Do not edit `Dockerfile`, `railway.toml`, `railway-cron.toml`, `service/telescope/**`, `docs/test-bible/service/telescope.md`, or `docs/test-bible/README.md` (the README already links the `service/` directory).

**`tests/component/service/test_platform_deploy.py`** — new. Repo root is `Path(__file__).resolve().parents[3]`, same depth as `test_telescope_deploy_ci.py`. Ignore blank lines and lines whose strip starts with `#`, then treat a line as an `ARG` or `ENV` instruction only when the first token is `ARG` or `ENV`. The name is the first token after that keyword, with anything from `=` onward removed. Comment text in the current Dockerfile mentions the words ARG and ENV; a whole-file substring check would fail on those comments. Do not flag `ARG VITE_STYTCH_PUBLIC_TOKEN` or `ARG VITE_STYTCH_REDIRECT_URL`.

```python
"""AST-2255 — root platform image does not declare secret ARG/ENV names."""

from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]

_SECRET_NAMES = (
    "ANTHROPIC_API_KEY",
    "ASTRAL_ENCRYPTION_KEY",
    "DEEPSEEK_API_KEY",
    "GOOGLE_CLIENT_SECRET",
    "GOOGLE_CSE_API_KEY",
    "GOOGLE_REFRESH_TOKEN",
    "SLACK_BOT_TOKEN",
    "SLACK_SIGNING_SECRET",
    "STYTCH_SECRET",
    "TELESCOPE_BEARER_TOKEN",
)


def _arg_env_names(text: str) -> list[str]:
    names: list[str] = []
    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        head, _, rest = stripped.partition(" ")
        if head.upper() not in {"ARG", "ENV"}:
            continue
        names.append(rest.split("=", 1)[0].split()[0])
    return names


class TestPlatformRailwayToml:
    def test_dockerfile_builder(self) -> None:
        text = (_REPO / "railway.toml").read_text(encoding="utf-8")
        assert 'builder = "DOCKERFILE"' in text
        assert 'dockerfilePath = "Dockerfile"' in text


class TestPlatformDockerfile:
    def test_no_secret_arg_or_env(self) -> None:
        path = _REPO / "Dockerfile"
        assert path.is_file(), "missing root Dockerfile — sync ftr product (AST-2254)"
        declared = [name for name in _arg_env_names(path.read_text(encoding="utf-8")) if name in _SECRET_NAMES]
        assert declared == []
```

Nodes:

- `tests/component/service/test_platform_deploy.py::TestPlatformRailwayToml::test_dockerfile_builder`
- `tests/component/service/test_platform_deploy.py::TestPlatformDockerfile::test_no_secret_arg_or_env`

**`docs/test-bible/service/platform.md`** — new, same role as the AST-1727 section of `docs/test-bible/service/telescope.md`. Contents:

- Title: platform Railway image (`Dockerfile`, root `railway.toml`).
- Test module: `tests/component/service/test_platform_deploy.py`.
- One coverage row: source `Dockerfile` + root `railway.toml`, test file `tests/component/service/test_platform_deploy.py`, branch lock `no`.
- Section heading `### AST-2255 · AST-2249 (platform Dockerfile secret ARG/ENV)`.
- Table: builder switch → `TestPlatformRailwayToml::test_dockerfile_builder`; secret names absent from `ARG`/`ENV` instructions → `TestPlatformDockerfile::test_no_secret_arg_or_env`.
- Narrowed run:

```bash
./scripts/testing/run_component_tests.sh tests/component/service/test_platform_deploy.py -q
```

- Pass criterion: pytest green on that path.
- Out of scope: live Railway deploy, `railway-cron.toml`, `service/telescope/**`, editing the Dockerfile or root `railway.toml` (AST-2254).

### Blast radius

- New test module beside `test_telescope_deploy_ci.py`. That module's `railway_toml` fixture is `telescope_root / "railway.toml"`. This test reads `_REPO / "railway.toml"` and `_REPO / "Dockerfile"` only.
- `docs/test-bible/service/platform.md` is a new page. `telescope.md` stays the telescope map.
- No `src/` change. No change to AST-2254's `Dockerfile` or `railway.toml`.
- `railway-cron.toml` stays `NIXPACKS` and is not asserted here.

### What must still hold

- Root `Dockerfile` and root `railway.toml` bytes stay as AST-2254 left them. This ticket only adds the test and the bible page.
- `ARG VITE_STYTCH_PUBLIC_TOKEN` and `ARG VITE_STYTCH_REDIRECT_URL` remain legal. The absence check is the ten secret names, not every `ARG`.
- `[deploy] startCommand = "python scripts/start_server.py"` stays. This test does not assert it and must not require it to move into a `CMD`.
- Telescope deploy tests and `docs/test-bible/service/telescope.md` stay unchanged.
