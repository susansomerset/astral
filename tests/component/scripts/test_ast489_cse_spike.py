"""AST-2253: the CSE spike takes --api-key and --cx and does not read GOOGLE_CSE_*."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_PATH = Path(__file__).resolve().parents[3] / "scripts/spikes/ast489_google_cse_company_search_spike.py"


def _load():
    spec = importlib.util.spec_from_file_location("ast489_cse_spike", _PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_missing_flags_exit_from_argparse() -> None:
    mod = _load()
    with pytest.raises(SystemExit):
        mod.parse_args([])


def test_flags_reach_search_and_hits_print(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    mod = _load()
    seen: dict[str, str] = {}

    def fake(query, *, api_key, cx, max_results, site_filters, days):
        seen["api_key"] = api_key
        seen["cx"] = cx
        return {"hits": [{"title": "T", "url": "https://u.example", "snippet": "s"}]}

    monkeypatch.setattr(mod, "search_google_cse", fake)
    mod.run_search(query="q", api_key="sk-spike", cx="cx-spike", site_filters=(), max_results=1)
    assert seen == {"api_key": "sk-spike", "cx": "cx-spike"}
    assert "https://u.example" in capsys.readouterr().out
    source = _PATH.read_text()
    assert "GOOGLE_CSE_API_KEY" not in source
    assert "GOOGLE_CSE_ID" not in source
