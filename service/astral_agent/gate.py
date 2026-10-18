"""The gate — decides when a waiting job may start (U1 holding area).

Same interface in astral-agent and Telescope (U6 will merge them into service/common);
only the gate differs. The worker asks `admit` while jobs are waiting, and re-asks on
every claim, every finish, and every ADMIT_INTERVAL_SECONDS.
"""

from __future__ import annotations

from typing import Protocol


class Gate(Protocol):
    def admit(self, running: int) -> bool:
        """True = start one waiting job now. A True answer uses up that admission."""


class AdmitAll:
    """Step 3: no limit. Step 6 replaces this with the limit learned from 429/529."""

    def admit(self, running: int) -> bool:
        return True
