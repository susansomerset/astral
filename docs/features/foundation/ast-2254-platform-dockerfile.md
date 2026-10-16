# AST-2254 — platform Dockerfile

No ancestor feature doc. These are the plan-fix sections for the orphaned-bug fix child. Neither AST-2254 nor AST-2249 names a Canon Scope list.

## Bug: AST-2254 — platform image secrets in Docker ARG/ENV

### As-is

The platform Railway service builds with Nixpacks (`railway.toml` `builder = "NIXPACKS"`, `buildCommand = "bash scripts/build_railway.sh"`). Nixpacks writes a Dockerfile that is not in the repo: one `ARG` (cited line 13) and one `ENV` (line 14) for every service variable whose name looks like a secret (`ANTHROPIC_API_KEY`, `ASTRAL_ENCRYPTION_KEY`, `DEEPSEEK_API_KEY`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_CSE_API_KEY`, `GOOGLE_REFRESH_TOKEN`, `SLACK_BOT_TOKEN`, `SLACK_SIGNING_SECRET`, `STYTCH_SECRET`, `TELESCOPE_BEARER_TOKEN`). Docker's build check `SecretsUsedInArgOrEnv` warns on each, because `ENV` stores the value in the image config. That generated file also references `$NIXPACKS_PATH` on line 23 before the variable is defined (`UndefinedVar`). Nothing committed contains those lines. `scripts/build_railway.sh` only runs `pip install -r requirements.txt` and `cd src/ui/frontend && npm install --include=dev && npm run build`.

### To-be

The platform image is built from a root `Dockerfile`. That file does not declare those ten names as `ARG` or `ENV`, so the secret-in-ARG/ENV warnings stop and the values are not stored in the image config. The `$NIXPACKS_PATH` line is not part of the build. Railway still injects the same variables into the running container. `[deploy] startCommand` stays `python scripts/start_server.py`.

### Repro

On the platform Railway service (root `railway.toml`, not `service/telescope/` and not `railway-cron.toml`):

1. `builder = "NIXPACKS"` and `buildCommand = "bash scripts/build_railway.sh"`.
2. Service variables include the ten names above.
3. A deploy runs Nixpacks, which emits a Dockerfile outside the repo. Docker's build check then reports `SecretsUsedInArgOrEnv` once per name for `ARG` at line 13 and once per name for `ENV` at line 14, plus `UndefinedVar` for `$NIXPACKS_PATH` at line 23. The pasted Railway log on AST-2249 is that report.

There is no committed fixture. The generated file's shape is one `ARG` instruction listing those names and one `ENV` instruction assigning each from its `ARG`, then a later line that expands `$NIXPACKS_PATH`.

### Root cause

The platform service has no repo Dockerfile, so Railway's Nixpacks builder is what produces the image. Nixpacks materializes secret-looking service variables as both `ARG` and `ENV` in that generated file, and it references `$NIXPACKS_PATH` before defining it. `ENV` keeps the values in the image config, which is what `SecretsUsedInArgOrEnv` flags.

### Proposed change

**Base image (this pass's call).** Final stage `python:3.12-slim-bookworm`. The repo's dev pin and the live Nixpacks venv are Python 3.12 (`scripts/setup_dev.sh`, `/opt/venv/lib/python3.12`). Node is not in that image. The frontend lockfile requires Node `^20.19.0 || ^22.12.0 || >=24`, so copy the Node 22 toolchain from `node:22-bookworm-slim` (same Debian release). Do not use Debian's `nodejs` package, a third-party Python+Node image, or a Node-only final stage.

**`Dockerfile` (new, repo root).** No `ENV` instruction anywhere. No `ARG` whose name is one of the ten secrets. No `CMD` (Railway `startCommand` stays the process start). Full file:

```dockerfile
FROM node:22-bookworm-slim AS nodebin

FROM python:3.12-slim-bookworm

COPY --from=nodebin /usr/local/bin/node /usr/local/bin/node
COPY --from=nodebin /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -sf ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
 && ln -sf ../lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx

WORKDIR /app
COPY . .

# Vite inlines these during `npm run build` inside scripts/build_railway.sh.
# Railway only passes a service variable into a Dockerfile build when the
# stage declares a matching ARG. ARG is not persisted as image ENV.
# VITE_STYTCH_PUBLIC_TOKEN is absent from the AST-2249 warning list
# (Docker's check allowlists names containing "public").
ARG VITE_STYTCH_PUBLIC_TOKEN
ARG VITE_STYTCH_REDIRECT_URL

RUN bash scripts/build_railway.sh
```

Do not add `build-essential` or other compilers in this pass. `requirements.txt` is installed from published wheels on CPython 3.12. If `pip install` fails for lack of a wheel or a shared library, stop and comment on AST-2254 — do not invent an apt line.

**`railway.toml`.** Change only `[build]` `builder` and add `dockerfilePath`. Leave `buildCommand` (the Dockerfile builder does not run it; the `RUN` above does). Leave `[deploy]` untouched.

```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"
buildCommand = "bash scripts/build_railway.sh"

[deploy]
startCommand = "python scripts/start_server.py"
```

Do not edit `scripts/build_railway.sh`, `scripts/start_server.py`, `nixpacks.toml`, `railway-cron.toml`, or `service/telescope/**`.

### Blast radius

- Root `railway.toml` is the platform service only. `service/telescope/railway.toml` and `service/telescope/Dockerfile` are a different image and stay on their current builder.
- `railway-cron.toml` is still `builder = "NIXPACKS"`. It is outside AST-2254 scope. Secret warnings on that cron service, if any, remain.
- `nixpacks.toml` (`providers = ["python", "node"]`) stays in the repo and is unused by the platform service once `builder = "DOCKERFILE"`.
- `scripts/build_railway.sh` is unchanged, so the image still pip-installs root `requirements.txt` and builds `src/ui/frontend` with `npm install --include=dev`. Runtime keys are read from the container environment (`scripts/start_server.py` uses `PORT` and `RAILWAY_CONFIG`), which Railway injects at start without a Dockerfile `ENV`.
- No product tests assert Nixpacks or a root Dockerfile. `docs/test-bible/**` is not this pass.

### What must still hold

- The ten secret names never appear as `ARG` or `ENV` in the root `Dockerfile`.
- `scripts/build_railway.sh` remains the build body: `pip install -r requirements.txt`, then `npm install --include=dev && npm run build` in `src/ui/frontend`.
- Process start remains `python scripts/start_server.py` via `[deploy] startCommand`, which execs gunicorn from `RAILWAY_CONFIG` (`src/utils/config.py`).
- Railway runtime injection of the same service variables is unchanged. The Dockerfile does not need to declare them for the running container.
- `VITE_STYTCH_PUBLIC_TOKEN` and `VITE_STYTCH_REDIRECT_URL` are still visible to `npm run build`, because Vite inlines `import.meta.env.VITE_STYTCH_PUBLIC_TOKEN` (`src/ui/frontend/src/lib/stytchClient.ts`) and `VITE_STYTCH_REDIRECT_URL` (`src/ui/frontend/src/lib/stytchRedirect.ts`).
- Telescope image files and `railway-cron.toml` are unchanged.
