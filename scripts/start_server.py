#!/usr/bin/env python3
"""Start the Astral web server. Reads deployment config from RAILWAY_CONFIG."""

import os
import sys
from pathlib import Path

root = Path(__file__).parent.parent
sys.path.insert(0, str(root))

from src.utils.config import RAILWAY_CONFIG

# Playwright browsers installed to a fixed path during build
if RAILWAY_CONFIG.get("playwright_browsers_path"):
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = RAILWAY_CONFIG["playwright_browsers_path"]

# Disable Firefox content sandbox — required in Railway/Docker containers where
# user namespace creation (CanCreateUserNamespace) is blocked by the host seccomp policy.
os.environ["MOZ_DISABLE_CONTENT_SANDBOX"] = "1"

os.chdir(root / "src" / "ui")
os.execvp("gunicorn", [
    "gunicorn", "server:app",
    "--bind", f"0.0.0.0:{os.environ['PORT']}",
    "--timeout", str(RAILWAY_CONFIG["timeout"]),
    "--workers", str(RAILWAY_CONFIG["workers"]),
])
