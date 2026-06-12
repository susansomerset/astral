import os
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("ASTRAL_DB_DIR", str(_ROOT / "data"))
Path(os.environ["ASTRAL_DB_DIR"]).mkdir(parents=True, exist_ok=True)
