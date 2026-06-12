"""One-time auth provider wiring (AST-611). Core may import external."""

from src.external import stytch
from src.utils.auth import register_token_authenticator

__all__ = ["wire_stytch_token_authenticator"]


def wire_stytch_token_authenticator() -> None:
    register_token_authenticator(stytch.authenticate_session_jwt)
