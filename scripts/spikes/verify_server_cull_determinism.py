#!/usr/bin/env python3
"""Offline server-cull determinism + href-set checks (AST-1232).

Usage (from repo root):
    PYTHONPATH=. .venv/bin/python scripts/spikes/verify_server_cull_determinism.py
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.external.playwright import _cull_html  # noqa: E402
from src.utils.html_cull_parity import (  # noqa: E402
    assert_html_cull_anchor_config,
    culled_html_equivalent,
    extract_anchor_hrefs,
)


def _default_captures_dir() -> Path:
    local = ROOT / "debug" / "spikes" / "AST-1194" / "captures"
    if local.is_dir():
        return local
    astral_main = os.environ.get("ASTRAL_MAIN")
    if astral_main:
        return Path(astral_main) / "debug" / "spikes" / "AST-1194" / "captures"
    return local


def _is_search_capture(html_path: Path) -> bool:
    if "search" in html_path.name.lower():
        return True
    meta = html_path.with_name(html_path.stem + ".meta.json")
    if not meta.exists():
        alt = html_path.with_suffix(".meta.json")
        meta = alt if alt.exists() else meta
    if not meta.exists():
        return False
    try:
        data = json.loads(meta.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    for key in ("label", "kind", "pageType"):
        val = data.get(key)
        if isinstance(val, str) and val.strip().lower() == "search":
            return True
    return False


def _check_synthetics() -> list[dict]:
    rows = []

    # Neutral search-like: job links not under banner patterns.
    neutral = (
        "<!DOCTYPE html><html><body>"
        '<div class="results"><a href="/jobs/123">Engineer</a>'
        '<a href="/jobs/456">Manager</a></div>'
        "<script>evil()</script></body></html>"
    )
    c1 = _cull_html(neutral)
    c2 = _cull_html(neutral)
    det_ok = c1 == c2
    href_ok = extract_anchor_hrefs(neutral) == extract_anchor_hrefs(c1)
    rows.append(
        {
            "check": "synthetic_determinism",
            "pass": det_ok and href_ok,
            "determinism": det_ok,
            "href_set_equal": href_ok,
            "hrefs": extract_anchor_hrefs(c1),
        }
    )

    # Banner still strips: wrapper tag must be div (allowed) so sweep sees it.
    banner = (
        "<!DOCTYPE html><html><body>"
        '<div class="cookie-banner"><a href="/jobs/999">x</a></div>'
        '<div class="results"><a href="/jobs/123">Engineer</a></div>'
        "</body></html>"
    )
    culled_banner = _cull_html(banner)
    hrefs = extract_anchor_hrefs(culled_banner)
    banner_ok = "/jobs/999" not in hrefs and "/jobs/123" in hrefs
    rows.append(
        {
            "check": "synthetic_banner_strips",
            "pass": banner_ok,
            "hrefs": hrefs,
        }
    )

    # Normalize sanity: attribute order only.
    left = '<div class="b" id="a"><a href="/x">Hi</a></div>'
    right = '<div id="a" class="b"><a href="/x">Hi</a></div>'
    rows.append(
        {
            "check": "normalize_attr_order",
            "pass": culled_html_equivalent(left, right),
        }
    )
    return rows


def _check_captures(captures_dir: Path) -> tuple[list[dict], list[Path]]:
    rows = []
    html_files = sorted(
        p for p in captures_dir.glob("*.html") if not p.name.startswith("_")
    )
    search_files = [p for p in html_files if _is_search_capture(p)]
    for path in html_files:
        raw = path.read_text(encoding="utf-8", errors="replace")
        raw_bytes = len(raw.encode("utf-8"))
        c1 = _cull_html(raw)
        c2 = _cull_html(raw)
        culled_bytes = len(c1.encode("utf-8"))
        det_ok = c1 == c2
        href_ok = extract_anchor_hrefs(raw) == extract_anchor_hrefs(c1)
        rows.append(
            {
                "check": "capture",
                "file": path.name,
                "is_search": path in search_files,
                "pass": det_ok and href_ok,
                "determinism": det_ok,
                "href_set_equal": href_ok,
                "raw_bytes": raw_bytes,
                "culled_bytes": culled_bytes,
                "hrefs_raw": extract_anchor_hrefs(raw),
                "hrefs_culled": extract_anchor_hrefs(c1),
            }
        )
    return rows, search_files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--captures-dir",
        type=Path,
        default=None,
        help="AST-1194 captures directory",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "debug" / "spikes" / "AST-1232",
        help="Report output directory (gitignored under debug/)",
    )
    args = parser.parse_args()
    captures_dir = (args.captures_dir or _default_captures_dir()).resolve()
    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    report: dict = {
        "captures_dir": str(captures_dir),
        "checks": [],
        "search_capture_count": 0,
        "blocked": None,
    }

    try:
        assert_html_cull_anchor_config()
        report["checks"].append({"check": "assert_html_cull_anchor_config", "pass": True})
    except ValueError as exc:
        report["checks"].append(
            {"check": "assert_html_cull_anchor_config", "pass": False, "error": str(exc)}
        )
        (out_dir / "verify_report.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    report["checks"].extend(_check_synthetics())
    synth_failed = [
        c
        for c in report["checks"]
        if not c.get("pass")
        and c.get("check")
        in (
            "assert_html_cull_anchor_config",
            "synthetic_determinism",
            "synthetic_banner_strips",
            "normalize_attr_order",
        )
    ]
    if synth_failed:
        (out_dir / "verify_report.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
        print(f"FAIL: {len(synth_failed)} synthetic/config check(s)", file=sys.stderr)
        for row in synth_failed:
            print(f"  - {row}", file=sys.stderr)
        return 1

    search_files: list[Path] = []
    if captures_dir.is_dir():
        capture_rows, search_files = _check_captures(captures_dir)
        report["checks"].extend(capture_rows)
        report["search_capture_count"] = len(search_files)
    else:
        report["checks"].append(
            {
                "check": "captures_dir_exists",
                "pass": False,
                "path": str(captures_dir),
            }
        )

    if report["search_capture_count"] == 0:
        report["blocked"] = "no_search_captures"
        (out_dir / "verify_report.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
        print(
            f"BLOCKED: no search-labelled captures in {captures_dir}",
            file=sys.stderr,
        )
        return 2

    failed = [c for c in report["checks"] if not c.get("pass")]
    (out_dir / "verify_report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    if failed:
        print(f"FAIL: {len(failed)} check(s)", file=sys.stderr)
        for row in failed:
            print(f"  - {row}", file=sys.stderr)
        return 1

    print(f"OK: wrote {out_dir / 'verify_report.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
