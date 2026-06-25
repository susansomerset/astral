# AST-668 — Headless Ubuntu server setup script (HP ProDesk home box)

<!-- linear-archive: AST-668 archived 2026-06-23 -->

## Linear archive (AST-668)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-668/headless-ubuntu-server-setup-script-hp-prodesk-home-box  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** susan  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Infrastructure task (outside normal dispatch workflow): Susan's HP ProDesk 400 G5 running Ubuntu Server 24.04 LTS on the LAN for continuous Astral.

Deliverable: `scripts/setup-server.sh` — idempotent install from a fresh clone over SSH.

Not in scope for the script: GitHub auth, `.env` secrets, Stytch dashboard URLs, systemd/reverse-proxy/TLS, DB migration from Railway.

### Comments

#### chuckles — 2026-06-15T13:43:51.917Z
@susan — decisions recorded and implemented on branch `chuckles/ast-668-headless-ubuntu-server-setup-script-hp-prodesk-home-box`.

| # | Your call | Done |
|---|-----------|------|
| 1 | `~/chuckles` | Default in `paths.sh` + docs |
| 2 | DB in repo `data/` | Documented; `link_one` symlinks unchanged |
| 3 | MCP | **Copy Mac `~/.cursor/mcp.json`** via `scp` — same `npx` + env keys work on Ubuntu |
| 4 | systemd wake on boot | **`scripts/install-systemd-wake.sh`** + `--detached` / `--stop` on Linux wake script |

**#5 — GitHub remote (what I meant):** Your Mac `team-chuckles` folder had no `origin` URL — git didn't know *where on GitHub* to push this repo. That's not the ProDesk SSH key; it's one-time on whichever machine pushes:

```bash
git remote add origin git@github.com:susansomerset/team-chuckles.git
git push -u origin <branch>
```

`git clone` on ProDesk sets `origin` automatically.

**ProDesk boot sequence (after secrets):**
1. `bash ~/chuckles/team-chuckles/scripts/install-systemd-wake.sh`
2. `systemctl --user start team-chuckles-wake`
3. `tmux attach -t chuck` to watch

— Chuckles

#### chuckles — 2026-06-15T08:00:27.975Z
## Ubuntu port — team-chuckles (AST-668)

Branch: `chuckles/ast-668-headless-ubuntu-server-setup-script-hp-prodesk-home-box`

### Delivered

1. **`scripts/setup-server.sh`** — idempotent Ubuntu 24.04 setup (apt, Cursor Agent CLI, clone repos, `install.sh`, Python venv + Playwright Firefox, frontend build). No secrets.
2. **Path portability** — `skills/rollcall/paths.sh` exports `CHUCKLES_ROOT`, `ASTRAL_MAIN`, `ASTRAL_REPO`, `ASTRAL_TESTS`, `TEAM_CHUCKLES_ROOT`. Watch rules use `$ASTRAL_MAIN`; `watch_linear.py` resolves env. Grep-clean: no `/Users/susan` left.
3. **Linux wake** — `skills/wake-up-chuck-linux.sh` + `wake-up-chuck-common.sh` (bash, tmux-only, loads `~/.config/team-chuckles/env` + `~/.bashrc`). `wake_multiplex.py` honors `WAKE_SHELL`.
4. **`docs/UBUNTU_SETUP.md`** — MCP template, secrets, `.env` symlink pattern, manual steps.
5. **README** — ProDesk = wake host; Mac = Susan UAT only.

Prior astral `scripts/setup-server.sh` on `chuckles/setup-server` — **ignore**; canonical script is in **team-chuckles**.

### Manual steps on ProDesk

1. SSH deploy key → GitHub
2. `bash ~/chuckles/team-chuckles/scripts/setup-server.sh` (or clone first)
3. Fill `~/.config/team-chuckles/env` (`LINEAR_KEY_*`, `CURSOR_API_KEY`)
4. Symlink/copy `astral/.env` from `env.example`
5. `agent login` or `CURSOR_API_KEY`
6. Copy/adapt `~/.cursor/mcp.json` (Linear personas + GitHub)
7. Wake: `bash -l ~/chuckles/team-chuckles/skills/wake-up-chuck-linux.sh`

Full detail: `docs/UBUNTU_SETUP.md`

### Open decisions @susan

1. **`CHUCKLES_ROOT` default `~/chuckles`** — OK on Ubuntu?
2. **`ASTRAL_DB_DIR`** — under repo `~/chuckles/astral/data` or separate mount?
3. **MCP config** — copy Mac `~/.cursor/mcp.json` wholesale vs per-server doc in UBUNTU_SETUP?
4. **systemd unit** for wake-on-boot vs manual tmux?
5. **team-chuckles `origin`** — repo may have no remote yet; confirm before PR:
   `git remote add origin git@github.com:susansomerset/team-chuckles.git`

— Chuckles

#### chuckles — 2026-06-15T07:41:52.537Z
@Susan — `scripts/setup-server.sh` is on branch **`chuckles/setup-server`** (commit `e7b02deb`). Idempotent Ubuntu 24.04 install over SSH with sudo.

## What the script does

1. **apt** — git, tmux, python3 + venv + pip, nodejs + npm (NodeSource 20.x if distro Node < 18), build-essential/libssl/libffi
2. **Assumes repo already cloned** at the path you run from (derives root from `scripts/setup-server.sh`); does **not** clone or pull
3. **`.venv`** + `pip install -r requirements.txt`
4. **Playwright** — `PLAYWRIGHT_BROWSERS_PATH=<repo>/.browsers` + `playwright install --with-deps firefox` (matches `scripts/build_railway.sh`)
5. **Frontend** — `npm install --include=dev && npm run build` in `src/ui/frontend` (production path per ASTRAL_CODE_RULES §3.5)
6. Creates **`data/`** (or `$ASTRAL_DB_DIR` if you export it when invoking) — reminds you to set runtime env in `.env`

## How to run on the box

```bash
git clone <your-remote> ~/astral   # manual — script skips this
cp env.example ~/astral/.env         # manual — fill secrets + VITE_* BEFORE build
ssh user@prodesk 'cd ~/astral && sudo bash scripts/setup-server.sh'
```

Then start (same as Railway):
```bash
source .venv/bin/activate
export PORT=8080 ASTRAL_DB_DIR=~/astral/data
python scripts/start_server.py
```

(`start_server.py` sets `MOZ_DISABLE_CONTENT_SANDBOX=1` and reads `RAILWAY_CONFIG` from `config.py`.)

## Manual / out of scope (script prints these too)

- GitHub SSH key or PAT for clone/pull
- `.env` from `env.example` — all secrets
- **Stytch Dashboard** redirect URLs for the ProDesk hostname
- systemd unit, nginx/caddy, TLS
- Copying `astral.db` from Railway or Mac
- Firewall / LAN routing

## Decisions for you

1. **Repo path on the box** — `~/astral` OK, or prefer `/opt/astral`?
2. **`ASTRAL_DB_DIR`** — keep under repo (`~/astral/data`) or separate mount (e.g. `/var/lib/astral`)?
3. **`PORT`** — default 8080 in the script notes; want 80 behind a proxy instead?
4. **Branch to track** — `dev`, `main`, or pin a release tag on the home server?
5. **`VITE_STYTCH_REDIRECT_URL`** — what is the LAN URL Susan will open in the browser? (Must match Stytch allowlist exactly; re-run frontend build after setting `.env`.)
6. **Continuous run** — tmux (documented) vs follow-up **systemd unit** — want me to add `scripts/astral.service` example in a second pass?
7. **Merge path** — merge `chuckles/setup-server` → `dev` via PR, or you want this on the box before it lands on `dev`?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
