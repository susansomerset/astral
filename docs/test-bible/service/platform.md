# Platform Railway image (`Dockerfile`, root `railway.toml`)

**Test module:** `tests/component/service/test_platform_deploy.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `Dockerfile` + root `railway.toml` | `tests/component/service/test_platform_deploy.py` | no |

---

### AST-2255 · AST-2249 (platform Dockerfile secret ARG/ENV)

**Scope:** root `railway.toml` uses the Dockerfile builder; root `Dockerfile` does not declare the ten secret names from the AST-2249 report as `ARG` or `ENV`.

| Area | Component tests |
| --- | --- |
| Builder switch | `test_platform_deploy.py::TestPlatformRailwayToml::test_dockerfile_builder` |
| Secret names absent from `ARG`/`ENV` instructions | `test_platform_deploy.py::TestPlatformDockerfile::test_no_secret_arg_or_env` |

**AST-2255** narrowed run:

```bash
./scripts/testing/run_component_tests.sh tests/component/service/test_platform_deploy.py -q
```

**Pass criterion:** pytest green on that path.

**Out of scope:** live Railway deploy, `railway-cron.toml`, `service/telescope/**`, editing the Dockerfile or root `railway.toml` (AST-2254).

## QA test manifest

1. **bug-repro:** `tests/component/service/test_platform_deploy.py::TestPlatformRailwayToml::test_dockerfile_builder` — red on `1fe4515c2` (`builder = "NIXPACKS"`, no `dockerfilePath`).
2. **bug-repro:** `tests/component/service/test_platform_deploy.py::TestPlatformDockerfile::test_no_secret_arg_or_env` — red on `1fe4515c2` (no root `Dockerfile`). Green on this sub once AST-2254's files are present; the absence check ignores comment text and allows `ARG VITE_STYTCH_PUBLIC_TOKEN` / `ARG VITE_STYTCH_REDIRECT_URL`.

```bash
./scripts/testing/run_component_tests.sh tests/component/service/test_platform_deploy.py -q
```

**Bible shasum (after publish):** `git show origin/sub/AST-2249/AST-2255-platform-dockerfile-tests:docs/test-bible/service/platform.md | shasum`
