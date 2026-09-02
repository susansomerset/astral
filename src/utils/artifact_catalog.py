# -*- coding: utf-8 -*-
"""Read-only accessors over ARTIFACT_CONFIG (AST-1573 / AST-1575 / patt.artifact.manage-catalog).

Callers resolve hierarchical catalog keys here — do not scrape config.ARTIFACT_CONFIG
internals. No I/O.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from src.utils.config import ARTIFACT_CONFIG


def get_catalog_entry(catalog_key: str) -> Optional[Dict[str, Any]]:
    """Return metadata for hierarchical ``catalog_key``, or None if unregistered."""
    if not isinstance(catalog_key, str) or not catalog_key.strip():
        return None
    entry = ARTIFACT_CONFIG.get(catalog_key.strip())
    return dict(entry) if entry is not None else None


def require_catalog_entry(catalog_key: str) -> Dict[str, Any]:
    """Return metadata for ``catalog_key``; raise ValueError if unknown/blank."""
    if not isinstance(catalog_key, str) or not catalog_key.strip():
        raise ValueError(f"unknown catalog key: {catalog_key!r}")
    key = catalog_key.strip()
    entry = ARTIFACT_CONFIG.get(key)
    if entry is None:
        raise ValueError(f"unknown catalog key: {key!r}")
    return dict(entry)


def is_candidate_scoped(catalog_key: str) -> bool:
    """True when the registered key is candidate-scoped; unknown keys raise via require."""
    return bool(require_catalog_entry(catalog_key)["candidate_scoped"])
