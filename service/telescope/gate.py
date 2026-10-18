"""The gate — decides when a waiting job may start (U1 holding area).

Same interface in astral-agent and Telescope (U6 will merge them into service/common);
only the gate differs. The worker asks `admit` while jobs are waiting, and re-asks on
every claim, every finish, and every ADMIT_INTERVAL_SECONDS.

Telescope's gate is memory headroom: start a Firefox context only while the container's
working set is below the cutoff, read live from cgroup v2.
"""

from __future__ import annotations

import time
from typing import Protocol


class Gate(Protocol):
    def admit(self, running: int) -> bool:
        """True = start one waiting job now. A True answer uses up that admission."""


class MemoryGate:
    def __init__(
        self,
        cutoff_percent: float,
        interval_seconds: float,
        *,
        cgroup_dir: str = "/sys/fs/cgroup",
    ) -> None:
        self._cutoff = cutoff_percent
        self._interval = interval_seconds
        self._dir = cgroup_dir
        self._last = float("-inf")  # monotonic time of the last admission
        # Fail loud at startup: a container without a readable limit would run ungated.
        try:
            self.used_percent()
        except Exception as exc:
            raise RuntimeError(
                f"cgroup v2 memory not readable under {cgroup_dir} "
                f"(need memory.max as a number, memory.current, memory.stat inactive_file): "
                f"{type(exc).__name__}: {exc}"
            ) from exc

    def _read(self, name: str) -> str:
        with open(f"{self._dir}/{name}", encoding="ascii") as f:
            return f.read()

    def used_percent(self) -> float:
        """Working set (memory.current minus inactive_file) as a share of memory.max.

        inactive_file is reclaimable page cache; memory.current alone sits near the limit
        on any container that has read a lot of files. Both files are read on every call,
        so a live resize of the container limit is picked up.
        """
        limit = self._read("memory.max").strip()
        if limit == "max":
            raise ValueError("memory.max is 'max' (no container limit)")
        inactive = next(
            (
                int(line.split()[1])
                for line in self._read("memory.stat").splitlines()
                if line.startswith("inactive_file ")
            ),
            None,
        )
        if inactive is None:
            raise ValueError("memory.stat has no inactive_file line")
        working_set = max(0, int(self._read("memory.current")) - inactive)
        return working_set / int(limit) * 100

    def admit(self, running: int) -> bool:
        # Nothing running -> always admit one, so a high reading can never strand the line.
        if running:
            if time.monotonic() - self._last < self._interval:
                return False
            if self.used_percent() >= self._cutoff:
                return False
        self._last = time.monotonic()
        return True
