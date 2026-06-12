#!/usr/bin/env bash
pip install -r requirements.txt
# Install Playwright browsers to a fixed path so build and runtime agree
export PLAYWRIGHT_BROWSERS_PATH="$PWD/.browsers"
playwright install --with-deps firefox
cd src/ui/frontend && npm install --include=dev && npm run build
