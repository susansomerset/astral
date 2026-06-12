# -*- coding: utf-8 -*-
"""Core-owned persistence for API cost / timesheet rows (data layer write path).

External `anthropic.send_to_anthropic` stays utils-only; core passes this as
`record_timesheet` so inline token accounting still lands immediately after each call.
"""

from typing import Any

from src.data.database import _add_timesheet_entry


def record_timesheet_entry(**kwargs: Any) -> None:
    _add_timesheet_entry(**kwargs)
