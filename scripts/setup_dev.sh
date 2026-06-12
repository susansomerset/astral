#!/usr/bin/env bash
# Astral dev environment setup — assumes a clean Mac with nothing installed.
# Run from the repo root: bash scripts/setup_dev.sh
set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo ""
echo "=== Astral Dev Setup ==="
echo "Repo: $REPO_ROOT"
echo ""

# ---------------------------------------------------------------------------
# 1. Homebrew (installs Xcode Command Line Tools as a side effect)
# ---------------------------------------------------------------------------
if ! command -v brew &>/dev/null; then
  echo "[1/5] Installing Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  # Add brew to PATH for the rest of this script (Apple Silicon path)
  if [ -f /opt/homebrew/bin/brew ]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
  fi
else
  echo "[1/5] Homebrew already installed — skipping"
fi

# ---------------------------------------------------------------------------
# 2. Python 3.12 (always install via brew — system Python may be too old)
# ---------------------------------------------------------------------------
if ! /opt/homebrew/bin/python3.12 --version &>/dev/null 2>&1; then
  echo "[2/5] Installing Python 3.12 via Homebrew..."
  /opt/homebrew/bin/brew install python@3.12
else
  echo "[2/5] Python 3.12 already installed ($(/opt/homebrew/bin/python3.12 --version)) — skipping"
fi
PYTHON=/opt/homebrew/bin/python3.12

# ---------------------------------------------------------------------------
# 3. Node / npm
# ---------------------------------------------------------------------------
if ! /opt/homebrew/bin/node --version &>/dev/null 2>&1; then
  echo "[3/5] Installing Node.js..."
  /opt/homebrew/bin/brew install node
else
  echo "[3/5] Node already installed ($(/opt/homebrew/bin/node --version)) — skipping"
fi

# ---------------------------------------------------------------------------
# 4. Virtualenv + Python dependencies + Playwright browsers
# ---------------------------------------------------------------------------
VENV="$REPO_ROOT/.venv"
if [ ! -d "$VENV" ]; then
  echo "[4/5] Creating virtualenv at .venv..."
  $PYTHON -m venv "$VENV"
else
  echo "[4/5] Virtualenv already exists — skipping creation"
fi

echo "      Installing Python packages into .venv..."
"$VENV/bin/pip" install -r requirements.txt

echo "      Installing Playwright browsers (Firefox)..."
"$VENV/bin/python" -m playwright install firefox

# ---------------------------------------------------------------------------
# 5. Frontend (npm install + build)
# ---------------------------------------------------------------------------
echo "[5/5] Installing frontend dependencies and building..."
cd src/ui/frontend
/opt/homebrew/bin/npm install --include=dev
/opt/homebrew/bin/npm run build
cd "$REPO_ROOT"

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------
echo ""
echo "=== Setup complete ==="
echo ""
echo "To start the dev servers, activate the virtualenv first:"
echo "  source .venv/bin/activate"
echo ""
echo "  Terminal 1 — Flask API:    cd src/ui && python server.py"
echo "  Terminal 2 — Vite dev:     cd src/ui/frontend && npm run dev"
echo ""
# Persist Homebrew to ~/.zshrc if not already there
ZSHRC="$HOME/.zshrc"
if ! grep -q 'brew shellenv' "$ZSHRC" 2>/dev/null; then
  echo '' >> "$ZSHRC"
  echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> "$ZSHRC"
  echo "Added Homebrew to ~/.zshrc"
fi

echo ""
echo "Run this to apply PATH changes to your current terminal:"
echo '  source ~/.zshrc'
echo ""
