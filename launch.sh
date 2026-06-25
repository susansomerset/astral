#!/usr/bin/env zsh
# launch.sh — Flask + Vite dev servers in macOS Terminal tabs.
#
#   zsh -l ~/chuckles/astral/launch.sh          # both (default): two new tabs in this window
#   zsh -l ~/chuckles/astral/launch.sh --flask  # flask only (this tab)
#   zsh -l ~/chuckles/astral/launch.sh --vite   # vite only (this tab)
#   zsh -l ~/chuckles/astral/launch.sh --windows  # separate windows instead of tabs
#
# Run separately from wake-up-chuck (Linear watchers / tmux chuck session).

emulate -L zsh
setopt errexit nounset pipefail

WORKDIR="${0:A:h}"
SCRIPT_PATH="${WORKDIR}/launch.sh"
FRONTEND_DIR="${WORKDIR}/src/ui/frontend"

_ensure_python_deps() {
  cd "${WORKDIR}"
  if [[ ! -f .venv/bin/activate ]]; then
    print -u2 "missing ${WORKDIR}/.venv — run scripts/setup_dev.sh"
    exit 1
  fi
  source .venv/bin/activate
  if ! python -c "import stytch" 2>/dev/null; then
    print -u2 "installing python deps (missing stytch)..."
    pip install -r requirements.txt
  fi
}

_ensure_frontend_deps() {
  cd "${FRONTEND_DIR}"
  if [[ ! -d node_modules/@stytch/react ]]; then
    print -u2 "installing frontend deps (missing node_modules/@stytch/react)..."
    npm install --include=dev
  fi
}

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

typeset USE_TABS=1
[[ "${1:-}" == "--windows" ]] && { USE_TABS=0; shift; }

run_flask() {
  _ensure_python_deps
  _ensure_frontend_build
  cd "${WORKDIR}/src/ui"
  print -u2 "flask-api http://localhost:5001 (Ctrl-C to stop)"
  print -u2 "tip: vite live-reload at http://localhost:5173 — launch.sh --vite"
  exec python server.py
}

run_vite() {
  _ensure_frontend_deps
  cd "${FRONTEND_DIR}"
  print -u2 "vite-dev http://localhost:5173 (Ctrl-C to stop)"
  exec npm run dev
}

_tab_cmd() {
  local subcmd="$1"
  print -r -- "zsh -l ${(q)SCRIPT_PATH} ${(q)subcmd}"
}

_open_window_cmd() {
  local cmd="$1"
  osascript - "$cmd" <<'APPLESCRIPT'
on run argv
  set cmd to item 1 of argv
  tell application "Terminal"
    activate
    do script cmd
  end tell
end run
APPLESCRIPT
}

_open_tabs_in_front_window() {
  local flask_cmd="$(_tab_cmd --flask)"
  local vite_cmd="$(_tab_cmd --vite)"
  osascript - "$flask_cmd" "$vite_cmd" <<'APPLESCRIPT'
on run argv
  set flaskCmd to item 1 of argv
  set viteCmd to item 2 of argv
  tell application "Terminal"
    set w to front window
    do script flaskCmd in w
    do script viteCmd in w
    activate
  end tell
end run
APPLESCRIPT
}

_launch_tabs() {
  if (( USE_TABS )); then
    if ! _open_tabs_in_front_window 2>/dev/null; then
      print -u2 "tab spawn failed — falling back to separate windows"
      _open_window_cmd "$(_tab_cmd --flask)"
      _open_window_cmd "$(_tab_cmd --vite)"
    fi
  else
    _open_window_cmd "$(_tab_cmd --flask)"
    _open_window_cmd "$(_tab_cmd --vite)"
  fi
  print -u2 "launched flask + vite in Terminal (two tabs in this window)"
  print -u2 "Linear watchers: zsh -l ~/.cursor/skills/wake-up-chuck.sh"
}

case "${1:-}" in
  --flask) run_flask ;;
  --vite)  run_vite ;;
  --tabs|'') _launch_tabs ;;
  *)
    print -u2 "usage: $0 [--windows] [--flask | --vite | --tabs]"
    exit 2
    ;;
esac
