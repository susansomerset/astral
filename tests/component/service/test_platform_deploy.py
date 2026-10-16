"""AST-2255 — root platform image does not declare secret ARG/ENV names."""

from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]

_SECRET_NAMES = (
    "ANTHROPIC_API_KEY",
    "ASTRAL_ENCRYPTION_KEY",
    "DEEPSEEK_API_KEY",
    "GOOGLE_CLIENT_SECRET",
    "GOOGLE_CSE_API_KEY",
    "GOOGLE_REFRESH_TOKEN",
    "SLACK_BOT_TOKEN",
    "SLACK_SIGNING_SECRET",
    "STYTCH_SECRET",
    "TELESCOPE_BEARER_TOKEN",
)


def _arg_env_names(text: str) -> list[str]:
    names: list[str] = []
    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        head, _, rest = stripped.partition(" ")
        if head.upper() not in {"ARG", "ENV"}:
            continue
        names.append(rest.split("=", 1)[0].split()[0])
    return names


class TestPlatformRailwayToml:
    def test_dockerfile_builder(self) -> None:
        text = (_REPO / "railway.toml").read_text(encoding="utf-8")
        assert 'builder = "DOCKERFILE"' in text
        assert 'dockerfilePath = "Dockerfile"' in text


class TestPlatformDockerfile:
    def test_no_secret_arg_or_env(self) -> None:
        path = _REPO / "Dockerfile"
        assert path.is_file(), "missing root Dockerfile — sync ftr product (AST-2254)"
        declared = [name for name in _arg_env_names(path.read_text(encoding="utf-8")) if name in _SECRET_NAMES]
        assert declared == []
