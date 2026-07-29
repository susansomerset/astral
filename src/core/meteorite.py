"""
Meteorite placeholder company ensure (AST-1041).

Lazy-insert meteorite-<candidate_id> from METEORITE_CONFIG. No job create (AST-1042).
No email ingest. Leave-in-place — callers must not delete these rows on candidate exit.
"""

from __future__ import annotations

from typing import Any

from src.data.database import get_company, save_company
from src.utils.config import METEORITE_CONFIG
from src.utils.logging import get_logger


def ensure_meteorite_company(candidate_id: str, *, debug: bool = False) -> dict[str, Any]:
    """Ensure meteorite-<candidate_id> exists in IGNORE. Idempotent.

    Returns:
      {"short_name": str, "inserted": bool, "company": dict}
    """
    candidate_id = (candidate_id or "").strip()
    if not candidate_id:
        raise ValueError("candidate_id is required")

    short_name = METEORITE_CONFIG["short_name_template"].format(candidate_id=candidate_id)
    log = get_logger(__name__)
    log.set_debug_flag(debug)

    existing = get_company(short_name)
    if existing is not None:
        if debug:
            log.debug_index(
                func="meteorite.ensure_meteorite_company",
                index=1,
                total=1,
                identifier=short_name,
                outcome="already-present",
            )
            log.debug_detail(f"candidate_id={candidate_id}")
        return {"short_name": short_name, "inserted": False, "company": existing}

    save_company(
        short_name=short_name,
        state=METEORITE_CONFIG["company_state"],
        company_name=METEORITE_CONFIG["company_name"],
        company_data=dict(METEORITE_CONFIG["company_data"]),
        candidate_id=candidate_id,
    )
    row = get_company(short_name)
    if row is None:
        raise RuntimeError(f"meteorite company missing after save: {short_name}")
    if debug:
        log.debug_index(
            func="meteorite.ensure_meteorite_company",
            index=1,
            total=1,
            identifier=short_name,
            outcome="inserted",
        )
        log.debug_detail(f"candidate_id={candidate_id}")
    return {"short_name": short_name, "inserted": True, "company": row}
