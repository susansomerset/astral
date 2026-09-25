#!/usr/bin/env zsh
# Flask API on http://localhost:5001 — run in its own Terminal tab.
emulate -L zsh
exec zsh -l "${0:A:h}/launch.sh" --flask
