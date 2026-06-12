"""Component tests for agent_data table cluster (AST-392)."""

from __future__ import annotations

import pytest


class TestSaveAgentData:
    def test_rejects_invalid_block_type(self, sqlite_in_memory) -> None:
        with pytest.raises(ValueError, match="Invalid block_type"):
            sqlite_in_memory.save_agent_data(
                "id-1",
                "company",
                "qualify_job_listings",
                "batch-1",
                "NOT_A_BLOCK",
                "payload",
            )

    def test_saves_and_reads_batch_blocks(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        assert db.save_agent_data("id-1", "company", "qualify_job_listings", "batch-1", "RESPONSE", "payload") is True
        rows = db.get_agent_data_by_batch("batch-1", block_type="RESPONSE")
        assert len(rows) == 1
        assert rows[0]["block_data"] == "payload"
