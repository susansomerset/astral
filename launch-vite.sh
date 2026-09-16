#!/usr/bin/env zsh
# Vite dev on http://localhost:5173 — run in its own Terminal tab.
emulate -L zsh
exec zsh -l "${0:A:h}/launch.sh" --vite
