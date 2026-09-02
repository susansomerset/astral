# -*- coding: utf-8 -*-
"""Read-only accessors over ARTIFACT_CATALOG (AST-1573 / patt.artifact.manage-catalog).

Callers resolve artifact keys here — do not scrape config.ARTIFACT_CATALOG internals.
No I/O.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from src.utils.config import ARTIFACT_CATALOG


def get_catalog_entry(artifact_type: str) -> Optional[Dict[str, Any]]:
    """Return the catalog metadata dict for ``artifact_type``, or None if unregistered."""
    if not isinstance(artifact_type, str) or not artifact_type.strip():
        return None
    entry = ARTIFACT_CATALOG.get(artifact_type.strip())
    return dict(entry) if entry is not None else None


def require_catalog_entry(artifact_type: str) -> Dict[str, Any]:
    """Return catalog metadata for ``artifact_type``; raise ValueError if unknown/blank."""
    if not isinstance(artifact_type, str) or not artifact_type.strip():
        raise ValueError(f"unknown artifact type: {artifact_type!r}")
    key = artifact_type.strip()
    entry = ARTIFACT_CATALOG.get(key)
    if entry is None:
        raise ValueError(f"unknown artifact type: {key!r}")
    return dict(entry)


def is_candidate_scoped(artifact_type: str) -> bool:
    """True when the registered key is candidate-scoped; unknown keys raise via require."""
    return bool(require_catalog_entry(artifact_type)["candidate_scoped"])
