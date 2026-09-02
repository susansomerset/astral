# -*- coding: utf-8 -*-
"""ARTIFACT_CONFIG helpers + hierarchical pilot key scaffold (AST-1573 / AST-1575)."""

from __future__ import annotations

import pytest

# Reuse data-layer real-SQLite fixture for the catalog → save/get scaffold.
pytest_plugins = ["tests.component.data.conftest"]

from src.utils import artifact_catalog as catalog
from src.utils import config as cfg

# Hierarchical pilot key (AST-1575); leaf segment is the artifacts-table natural key.
_PILOT_KEY = "candidate.artifacts.base_resume"
_LEAF_TYPE = _PILOT_KEY.rsplit(".", 1)[-1]


def _artifact_config():
    """Resolve ARTIFACT_CONFIG — ImportError/AttributeError = pre-AST-1575 tree."""
    return cfg.ARTIFACT_CONFIG


# Branches: pilot lookup metadata; soft get vs require fail-fast; unknown/blank/flat;
# shallow-copy isolation; catalog-derived save_artifact → get_current_artifact.
class TestAst1573ArtifactCatalog:
    def test_pilot_entry_lookup_and_scope(self) -> None:
        ARTIFACT_CONFIG = _artifact_config()
        assert set(ARTIFACT_CONFIG.keys()) == {_PILOT_KEY}
        soft = catalog.get_catalog_entry(_PILOT_KEY)
        assert soft is not None
        required = catalog.require_catalog_entry(_PILOT_KEY)
        assert required == soft
        assert required["entity_type"] == "candidate"
        assert required["candidate_scoped"] is True
        assert required["body_shape"] == "resume_content"
        assert required["ingestion_owner"] == "candidate"
        assert catalog.is_candidate_scoped(_PILOT_KEY) is True
        # Whitespace around a known hierarchical key still resolves.
        assert catalog.require_catalog_entry(f"  {_PILOT_KEY}  ")["entity_type"] == "candidate"

    def test_unknown_blank_and_flat_key_fail_fast(self) -> None:
        assert catalog.get_catalog_entry("not_a_real_artifact") is None
        assert catalog.get_catalog_entry("") is None
        assert catalog.get_catalog_entry("   ") is None
        assert catalog.get_catalog_entry(None) is None  # type: ignore[arg-type]
        # Flat leaf must not alias as a catalog key (AST-1575).
        assert catalog.get_catalog_entry("base_resume") is None

        with pytest.raises(ValueError, match="unknown catalog key") as req_exc:
            catalog.require_catalog_entry("not_a_real_artifact")
        assert "not_a_real_artifact" in str(req_exc.value)

        with pytest.raises(ValueError, match="unknown catalog key"):
            catalog.require_catalog_entry("")
        with pytest.raises(ValueError, match="unknown catalog key"):
            catalog.is_candidate_scoped("not_a_real_artifact")
        with pytest.raises(ValueError, match="unknown catalog key"):
            catalog.require_catalog_entry("base_resume")

    def test_require_returns_shallow_copy(self) -> None:
        ARTIFACT_CONFIG = _artifact_config()
        entry = catalog.require_catalog_entry(_PILOT_KEY)
        entry["entity_type"] = "mutated"
        assert ARTIFACT_CONFIG[_PILOT_KEY]["entity_type"] == "candidate"
        assert catalog.require_catalog_entry(_PILOT_KEY)["entity_type"] == "candidate"

    def test_catalog_identity_save_get_round_trip(self, sqlite_in_memory) -> None:
        # Catalog supplies entity_type; leaf of hierarchical key is artifact_type.
        entry = catalog.require_catalog_entry(_PILOT_KEY)
        artifact_type = _LEAF_TYPE
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


class TestAst1575ArtifactConfigRename:
    """[bug-repro] AST-1575 — ARTIFACT_CONFIG + hierarchical key must exist; flat CATALOG gone."""

    def test_artifact_config_symbol_and_hierarchical_pilot(self) -> None:
        # Repro: pre-fix tree exposes ARTIFACT_CATALOG only; ARTIFACT_CONFIG missing.
        assert hasattr(cfg, "ARTIFACT_CONFIG"), "ARTIFACT_CONFIG missing (still ARTIFACT_CATALOG?)"
        assert not hasattr(cfg, "ARTIFACT_CATALOG"), "ARTIFACT_CATALOG must be removed"
        ARTIFACT_CONFIG = cfg.ARTIFACT_CONFIG
        assert set(ARTIFACT_CONFIG.keys()) == {"candidate.artifacts.base_resume"}
        entry = catalog.require_catalog_entry("candidate.artifacts.base_resume")
        assert entry["entity_type"] == "candidate"
        # Flat key must not resolve once hierarchical SoT lands.
        assert catalog.get_catalog_entry("base_resume") is None
        with pytest.raises(ValueError, match="unknown catalog key"):
            catalog.require_catalog_entry("base_resume")
