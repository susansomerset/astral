"""
Contact: Slack foundation + CONTACT_CONFIG skills ACL (Astral Contact / AST-1066).

Siblings extend: Events ingress (AST-1069), Manage Slack listen UI (AST-1067),
resolve/PROSPECT (AST-1068), conversation context (AST-1070).
AST-1071: ACL-gated entity-save skill runners (no Slack HTTP).
Estelle conversational turn loop lives on AST-1046 — not here.
"""

from typing import Any, Dict, List, Tuple

from src.core.candidate import get_candidate, save_candidate_data
from src.utils.config import CONTACT_CONFIG
from src.utils.logging import get_logger, truncate_debug_content

logger = get_logger(__name__)


def slack_listen_enabled() -> bool:
    """Return CONTACT_CONFIG listen flag (default False until Manage Slack flips it)."""
    return bool(CONTACT_CONFIG["listen_enabled"])


def contact_skills() -> Dict[str, Any]:
    """Shallow copy of CONTACT_CONFIG['skills'] ACL map."""
    return dict(CONTACT_CONFIG["skills"])


def contact_skill_keys() -> Tuple[str, ...]:
    """Ordered tuple of allowlisted Contact skill keys."""
    return tuple(CONTACT_CONFIG["skills"].keys())


def slack_env_names() -> Dict[str, str]:
    """Map logical secret → environ variable name (values never returned)."""
    return {
        "bot_token": str(CONTACT_CONFIG["bot_token_env"]),
        "signing_secret": str(CONTACT_CONFIG["signing_secret_env"]),
    }


def non_production_reply_prefix(environment: str) -> str:
    """Format CONTACT_CONFIG non-production reply prefix (AST-1067 applies when listen on)."""
    env = (environment or "").strip()
    return str(CONTACT_CONFIG["non_production_reply_prefix_template"]).format(
        environment=env
    )


def contact_skill_meta(skill_key: str) -> Dict[str, Any]:
    """Return a shallow copy of one skill ACL entry, or raise ValueError if unknown."""
    key = (skill_key or "").strip()
    if key not in CONTACT_CONFIG["skills"]:
        raise ValueError(f"unknown contact skill: {key!r}")
    meta = dict(CONTACT_CONFIG["skills"][key])
    meta["allowed_paths"] = tuple(meta["allowed_paths"])
    return meta


def run_contact_skill(
    skill_key: str,
    *,
    astral_candidate_id: str,
    fields: Dict[str, Any],
    debug: bool = False,
) -> Dict[str, Any]:
    """ACL-gated entity save for Contact. Writes only allowlisted candidate_data paths."""
    if debug:
        logger.set_debug_flag(True)

    cid = (astral_candidate_id or "").strip()
    if not cid:
        raise ValueError("astral_candidate_id is required")

    key = (skill_key or "").strip()
    meta = contact_skill_meta(key)
    if meta.get("write") is not True:
        raise ValueError(f"contact skill is not a write skill: {key!r}")
    if not isinstance(fields, dict):
        raise ValueError("fields must be a dict")

    allowed = set(meta["allowed_paths"])
    for path, value in fields.items():
        if path not in allowed:
            raise ValueError(f"path not allowlisted for skill {key!r}: {path!r}")
        if value is not None and not isinstance(value, str):
            raise ValueError(f"field {path!r} must be a string or null")

    row = get_candidate(cid)
    if not row:
        raise ValueError(f"candidate not found: {cid}")

    if debug:
        logger.debug_index(
            func="run_contact_skill",
            index=1,
            total=2,
            identifier=cid[:80],
            outcome="found",
        )
        logger.debug_detail(f"skill_key={key}")
        for path, value in fields.items():
            if value is None:
                continue
            for line in truncate_debug_content(str(value)):
                logger.debug_detail(f"{path}={line}")

    merge_dict: Dict[str, Any] = {}
    paths_written: List[str] = []
    for path, value in fields.items():
        if value is None:
            continue
        _deep_merge(merge_dict, _nest_dotted_path(path, value))
        paths_written.append(path)

    if merge_dict:
        save_candidate_data(cid, merge_dict)

    paths_written = sorted(paths_written)
    if debug:
        logger.debug_index(
            func="run_contact_skill",
            index=2,
            total=2,
            identifier=cid[:80],
            outcome="recorded",
        )
        logger.debug_detail(f"paths_written={','.join(paths_written)}")

    return {
        "ok": True,
        "skill_key": key,
        "astral_candidate_id": cid,
        "paths_written": paths_written,
    }


def _nest_dotted_path(path: str, value: Any) -> Dict[str, Any]:
    """Turn 'a.b.c' + value into {'a': {'b': {'c': value}}}."""
    parts = path.split(".")
    out: Any = value
    for part in reversed(parts):
        out = {part: out}
    return out


def _deep_merge(dst: Dict[str, Any], src: Dict[str, Any]) -> Dict[str, Any]:
    """Merge src into dst in place; dict values recurse. Return dst."""
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            _deep_merge(dst[k], v)
        else:
            dst[k] = v
    return dst
