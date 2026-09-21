#!/usr/bin/env python3
"""Start the Astral web server. Reads deployment config from RAILWAY_CONFIG."""

import os
import sys
from pathlib import Path

root = Path(__file__).parent.parent
sys.path.insert(0, str(root))

from src.utils.config import RAILWAY_CONFIG

os.chdir(root / "src" / "ui")
os.execvp("gunicorn", [
    "gunicorn", "server:app",
    "--bind", f"0.0.0.0:{os.environ['PORT']}",
    "--timeout", str(RAILWAY_CONFIG["timeout"]),
    "--workers", str(RAILWAY_CONFIG["workers"]),
])
