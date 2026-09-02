# -*- coding: utf-8 -*-
"""ARTIFACT_CATALOG helpers + base_resume data-layer scaffold (AST-1573)."""

from __future__ import annotations

import pytest

# Reuse data-layer real-SQLite fixture for the catalog → save/get scaffold.
pytest_plugins = ["tests.component.data.conftest"]

from src.utils import artifact_catalog as catalog
from src.utils.config import ARTIFACT_CATALOG


# Branches: pilot lookup metadata; soft get vs require fail-fast; unknown/blank;
# shallow-copy isolation; catalog-derived save_artifact → get_current_artifact.
class TestAst1573ArtifactCatalog:
    def test_pilot_entry_lookup_and_scope(self) -> None:
        assert set(ARTIFACT_CATALOG.keys()) == {"base_resume"}
        soft = catalog.get_catalog_entry("base_resume")
        assert soft is not None
        required = catalog.require_catalog_entry("base_resume")
        assert required == soft
        assert required["entity_type"] == "candidate"
        assert required["candidate_scoped"] is True
        assert required["body_shape"] == "resume_content"
        assert required["ingestion_owner"] == "candidate"
        assert catalog.is_candidate_scoped("base_resume") is True
        # Whitespace around a known key still resolves.
        assert catalog.require_catalog_entry("  base_resume  ")["entity_type"] == "candidate"

    def test_unknown_and_blank_fail_fast(self) -> None:
        assert catalog.get_catalog_entry("not_a_real_artifact") is None
        assert catalog.get_catalog_entry("") is None
        assert catalog.get_catalog_entry("   ") is None
        assert catalog.get_catalog_entry(None) is None  # type: ignore[arg-type]

        with pytest.raises(ValueError, match="unknown artifact type") as req_exc:
            catalog.require_catalog_entry("not_a_real_artifact")
        assert "not_a_real_artifact" in str(req_exc.value)

        with pytest.raises(ValueError, match="unknown artifact type"):
            catalog.require_catalog_entry("")
        with pytest.raises(ValueError, match="unknown artifact type"):
            catalog.is_candidate_scoped("not_a_real_artifact")

    def test_require_returns_shallow_copy(self) -> None:
        entry = catalog.require_catalog_entry("base_resume")
        entry["entity_type"] = "mutated"
        assert ARTIFACT_CATALOG["base_resume"]["entity_type"] == "candidate"
        assert catalog.require_catalog_entry("base_resume")["entity_type"] == "candidate"

    def test_catalog_identity_save_get_round_trip(self, sqlite_in_memory) -> None:
        # Catalog supplies entity_type — do not hardcode a parallel (entity, type) tuple.
        entry = catalog.require_catalog_entry("base_resume")
        artifact_type = "base_resume"
        payload = {"professional_summary": "catalog scaffold", "experience": []}
        uid = sqlite_in_memory.save_artifact(
            entry["entity_type"],
            "cand-ast-1573",
            artifact_type,
            payload,
        )
        assert uid
        row = sqlite_in_memory.get_current_artifact(
            entry["entity_type"],
            "cand-ast-1573",
            artifact_type,
        )
        assert row is not None
        assert row["artifact_uuid"] == uid
        assert row["artifact_type"] == "base_resume"
        assert row["entity_type"] == "candidate"
        assert row["artifact_data"] == payload
        assert row["current"] == 1
