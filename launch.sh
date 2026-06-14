#!/usr/bin/env zsh
# launch.sh — Flask + Vite dev servers in macOS Terminal tabs.
#
#   zsh -l ~/chuckles/astral/launch.sh          # both (default)
#   zsh -l ~/chuckles/astral/launch.sh --flask  # flask only
#   zsh -l ~/chuckles/astral/launch.sh --vite   # vite only
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

typeset USE_TABS=1
[[ "${1:-}" == "--windows" ]] && { USE_TABS=0; shift; }

run_flask() {
  _ensure_python_deps
  cd "${WORKDIR}/src/ui"
  print -u2 "flask-api http://localhost:5001 (Ctrl-C to stop)"
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

_open_tab_cmd() {
  local cmd="$1"
  osascript - "$cmd" <<'APPLESCRIPT'
on run argv
  set cmd to item 1 of argv
  tell application "Terminal"
    activate
    tell application "System Events" to keystroke "t" using command down
    delay 0.2
    do script cmd in selected tab of front window
  end tell
end run
APPLESCRIPT
}

_spawn_tab() {
  local subcmd="$1"
  local label="$2"
  local cmd="$(_tab_cmd "$subcmd")"
  if (( USE_TABS )); then
    if ! _open_tab_cmd "$cmd" 2>/dev/null; then
      print -u2 "tab spawn failed (${label}) — enable Terminal in Accessibility"
      _open_window_cmd "$cmd"
    fi
  else
    _open_window_cmd "$cmd"
  fi
}

_launch_tabs() {
  _open_window_cmd "$(_tab_cmd --flask)"
  _spawn_tab --vite vite
  print -u2 "launched flask + vite in Terminal"
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
