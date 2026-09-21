"""Bearer auth — Railway probes must send TELESCOPE_BEARER_TOKEN (AST-1727)."""

from __future__ import annotations

import hmac
from typing import Annotated, Optional

from fastapi import Header, HTTPException

from settings import settings


async def require_bearer(
    authorization: Annotated[Optional[str], Header()] = None,
) -> None:
    expected = settings.bearer_token or ""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="unauthorized")
    got = authorization[len("Bearer ") :]
    # compare_digest requires equal-length strings
    if not expected or len(got) != len(expected) or not hmac.compare_digest(got, expected):
        raise HTTPException(status_code=401, detail="unauthorized")
