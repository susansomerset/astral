#!/usr/bin/env python3
"""
AST-425 Phase 4: assemble board_profile_draft.json from Phase 1–3 spike artifacts (stdlib only).

Usage (repo root):
  python3 scripts/spikes/heavybit_board_phase4_emit_profile_draft.py
  python3 scripts/spikes/heavybit_board_phase4_emit_profile_draft.py --mirror-inputs
  python3 scripts/spikes/heavybit_board_phase4_emit_profile_draft.py \\
    --phase1-dir artifacts/heavybit/phase1/run \\
    --widgets-json artifacts/heavybit/phase2/widgets.json \\
    --phase3-dir artifacts/heavybit/phase3/run
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_ROOT = Path(__file__).resolve().parent.parent.parent

DEFAULT_OUT = _ROOT / "debug/spikes/AST-425/board_profile_draft.json"
BOARD_KEY = "heavybit"
ENTRY_URL = "https://www.heavybit.com/jobs"
LABEL = "Heavybit Jobs"

SCHEMA_VERSION = "3"

# Filter/search surfaces only — not chrome (header, pagination).
_SEARCHABLE_INTERACTIONS = frozenset({"text_entry", "block_tray", "inline_tray"})

# Search order documented in --help; first existing path wins.
PHASE1_CANDIDATES = [
    _ROOT / "debug/spikes/AST-422",
    _ROOT / "debug/spikes/AST-422/phase1/run",
    _ROOT / "debug/spikes/heavybit/phase1/run",
]

WIDGETS_CANDIDATES = [
    _ROOT / "debug/spikes/AST-423/widgets.json",
    _ROOT / "debug/spikes/heavybit/phase2/widgets.json",
]

PHASE3_CANDIDATES = [
    _ROOT / "debug/spikes/AST-424",
    _ROOT / "debug/spikes/AST-424/phase3/run",
    _ROOT / "debug/spikes/heavybit/phase3/run",
]

LEGACY_PHASE1 = _ROOT / "artifacts/heavybit/phase1/run"
LEGACY_WIDGETS = _ROOT / "artifacts/heavybit/phase2/widgets.json"
LEGACY_PHASE3 = _ROOT / "artifacts/heavybit/phase3/run"
OLDER_ROOT = _ROOT / "debug/spikes/older/heavybit"


def _first_existing_file(candidates: List[Path], name: str) -> Optional[Path]:
    for base in candidates:
        p = base / name if base.is_dir() else base
        if p.is_file():
            return p
        if base.is_dir():
            nested = base / name
            if nested.is_file():
                return nested
    return None


def _resolve_phase1_dir(explicit: Optional[Path], use_legacy: bool) -> Optional[Path]:
    if explicit is not None:
        return explicit if explicit.is_dir() else None
    for c in PHASE1_CANDIDATES:
        if c.is_dir() and (c / "meta.json").is_file():
            return c
    if use_legacy and LEGACY_PHASE1.is_dir():
        return LEGACY_PHASE1
    older = OLDER_ROOT / "phase1/run"
    if use_legacy and older.is_dir():
        return older
    return None


def _resolve_widgets(explicit: Optional[Path], use_legacy: bool) -> Optional[Path]:
    if explicit is not None:
        return explicit if explicit.is_file() else None
    for c in WIDGETS_CANDIDATES:
        if c.is_file():
            return c
    if use_legacy and LEGACY_WIDGETS.is_file():
        return LEGACY_WIDGETS
    older = OLDER_ROOT / "phase2/widgets.json"
    if use_legacy and older.is_file():
        return older
    return None


def _resolve_phase3_dir(explicit: Optional[Path], use_legacy: bool) -> Optional[Path]:
    if explicit is not None:
        return explicit if explicit.is_dir() else None
    for c in PHASE3_CANDIDATES:
        if c.is_dir() and (c / "board_results_parse_instructions.json").is_file():
            return c
    if use_legacy and LEGACY_PHASE3.is_dir():
        return LEGACY_PHASE3
    older = OLDER_ROOT / "phase3/run"
    if use_legacy and older.is_dir():
        return older
    return None


def _gap(gid: str, severity: str, message: str) -> Dict[str, str]:
    return {"id": gid, "severity": severity, "message": message}


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _display_label(row: Dict[str, Any]) -> str:
    an = (row.get("accessible_name") or "").strip()
    if an:
        return an.split("\n")[0].strip()
    vt = (row.get("visible_text") or "").strip()
    if vt:
        return vt.split("\n")[0].strip()
    return str(row.get("id") or "")


def _subtitle(row: Dict[str, Any]) -> str:
    an = (row.get("accessible_name") or "").strip()
    parts = [p.strip() for p in an.split("\n") if p.strip()]
    if len(parts) > 1:
        return parts[1]
    vt = (row.get("visible_text") or "").strip()
    parts = [p.strip() for p in vt.split("\n") if p.strip()]
    return parts[1] if len(parts) > 1 else ""


def _tray_match_keys(raw: str) -> List[str]:
    raw = raw.strip()
    if not raw:
        return []
    keys = [raw, raw.split("\n")[0].strip()]
    return list(dict.fromkeys(k for k in keys if k))


def _index_block_trays(widgets: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Map tray toggle label (full or first line) → block_tray_option_lists row."""
    out: Dict[str, Dict[str, Any]] = {}
    for row in widgets.get("block_tray_option_lists") or []:
        label = (row.get("toggle_visible_label") or "").strip()
        for key in _tray_match_keys(label):
            out[key] = row
    return out


def _index_inline_trays(widgets: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for row in widgets.get("inline_tray_option_lists") or []:
        wid = row.get("widget_id")
        if wid:
            out[str(wid)] = row
    return out


# a16z typeahead suggestions append a live job count (Engineer4701 → Engineer).
_TYPEAHEAD_JOB_COUNT_SUFFIX = re.compile(r"\d+$")


def _strip_typeahead_job_count(raw: str) -> str:
    s = raw.strip()
    if not s:
        return s
    return _TYPEAHEAD_JOB_COUNT_SUFFIX.sub("", s).rstrip()


def _normalize_lookup_options(pattern: str, items: List[Any]) -> List[Dict[str, Any]]:
    options: List[Dict[str, Any]] = []
    if pattern == "select_pill":
        for o in items:
            if isinstance(o, dict):
                options.append(
                    {"value": o.get("value"), "label": o.get("label") or o.get("value")}
                )
        return options
    seen: set = set()
    for o in items:
        if isinstance(o, str) and o.strip():
            s = o.strip()
            label = _strip_typeahead_job_count(s) if pattern == "typeahead" else s
            if label in seen:
                continue
            seen.add(label)
            options.append({"value": label, "label": label})
    return options


def _lookup_from_tray_row(tray: Dict[str, Any]) -> Dict[str, Any]:
    pattern = str(tray.get("pattern") or "unknown")
    lookup: Dict[str, Any] = {
        "pattern": pattern,
        "options": _normalize_lookup_options(pattern, tray.get("items") or []),
    }
    if tray.get("panel_inner_text"):
        lookup["panel_inner_text"] = tray["panel_inner_text"]
    if tray.get("parse_note"):
        lookup["parse_note"] = tray["parse_note"]
    return lookup


def _interaction_kind(control: Dict[str, Any], has_lookup: bool) -> str:
    hint = control.get("css_path_hint") or ""
    kind = control.get("kind") or ""
    if kind == "textbox":
        return "text_entry"
    if "inline-tray-toggle" in hint:
        return "inline_tray"
    if "block-tray-toggle" in hint:
        return "block_tray"
    return str(kind) if kind else "control"


def _resolve_lookup(
    control: Dict[str, Any],
    block_by_label: Dict[str, Dict[str, Any]],
    inline_by_wid: Dict[str, Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    wid = str(control.get("id") or "")
    if wid in inline_by_wid:
        return _lookup_from_tray_row(inline_by_wid[wid])
    hint = control.get("css_path_hint") or ""
    if "block-tray-toggle" not in hint:
        if control.get("kind") == "textbox":
            return {"pattern": "free_text", "options": []}
        return None
    for field in ("accessible_name", "visible_text"):
        for key in _tray_match_keys(control.get(field) or ""):
            if key in block_by_label:
                return _lookup_from_tray_row(block_by_label[key])
    return None


def _build_widgets_nested(widgets_doc: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Widget id → control + nested label + lookup options (mechanical join from Phase 2)."""
    block_by_label = _index_block_trays(widgets_doc)
    inline_by_wid = _index_inline_trays(widgets_doc)
    nested: Dict[str, Dict[str, Any]] = {}
    for c in widgets_doc.get("controls") or []:
        wid = c.get("id")
        if not wid:
            continue
        sid = str(wid)
        lookup = _resolve_lookup(c, block_by_label, inline_by_wid)
        entry: Dict[str, Any] = {
            "id": sid,
            "label": _display_label(c),
            "subtitle": _subtitle(c),
            "kind": c.get("kind"),
            "interaction": _interaction_kind(c, lookup is not None),
            "locator_playwright": c.get("locator_playwright"),
            "css_path_hint": c.get("css_path_hint"),
        }
        if lookup is not None:
            entry["lookup"] = lookup
        nested[sid] = entry
    return nested


def _build_search_keys(widgets_nested: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Page-label-keyed search map (not Astral-canonical keys).
    Keys come from on-board labels: Search by title, Location, Anytime, …
    """
    out: Dict[str, Dict[str, Any]] = {}
    for wid in sorted(widgets_nested.keys()):
        row = widgets_nested[wid]
        if row.get("interaction") not in _SEARCHABLE_INTERACTIONS:
            continue
        label = (row.get("label") or "").strip() or wid
        key = label
        if key in out:
            key = f"{label} ({wid})"
        lookup = row.get("lookup") or {}
        entry: Dict[str, Any] = {
            "widget_id": wid,
            "options": list(lookup.get("options") or []),
            "locator_playwright": row.get("locator_playwright"),
        }
        pattern = lookup.get("pattern")
        if pattern:
            entry["lookup_pattern"] = pattern
        if lookup.get("panel_inner_text"):
            entry["panel_inner_text"] = lookup["panel_inner_text"]
        subtitle = row.get("subtitle")
        if subtitle:
            entry["subtitle"] = subtitle
        out[key] = entry
    return out


def _reach_profile(meta: Dict[str, Any]) -> Dict[str, Any]:
    keys = (
        "url",
        "finished_at_utc",
        "consent_dismissal",
        "job_cards_visible",
        "results_region_strategy",
        "job_link_count_results_region",
    )
    return {k: meta[k] for k in keys if k in meta}


def _widget_inventory_summary(widgets: Dict[str, Any]) -> Dict[str, int]:
    controls = widgets.get("controls") or []
    block_trays = len(widgets.get("block_tray_option_lists") or [])
    inline_trays = len(widgets.get("inline_tray_option_lists") or [])
    return {
        "control_count": len(controls),
        "block_tray_option_list_count": block_trays,
        "inline_tray_option_list_count": inline_trays,
    }


def _gaps_for_search_keys(
    search_keys: Dict[str, Dict[str, Any]], widgets_nested: Dict[str, Dict[str, Any]]
) -> List[Dict[str, str]]:
    gaps: List[Dict[str, str]] = []
    for label, entry in search_keys.items():
        wid = entry.get("widget_id")
        row = widgets_nested.get(str(wid or ""))
        if not row:
            gaps.append(
                _gap(
                    f"search_key_orphan_{wid}",
                    "error",
                    f"search_keys[{label!r}] points at missing widget {wid!r}",
                )
            )
            continue
        interaction = row.get("interaction")
        if interaction in ("block_tray", "inline_tray") and not entry.get("options"):
            if not entry.get("panel_inner_text"):
                gaps.append(
                    _gap(
                        f"search_key_empty_options_{wid}",
                        "warn",
                        f"search_keys[{label!r}] has no options; re-run Phase 2",
                    )
                )
    return gaps


def assemble(
    phase1_dir: Path,
    widgets_path: Path,
    phase3_dir: Path,
    *,
    mirror_inputs: bool,
    out_path: Path,
) -> Tuple[Dict[str, Any], List[Dict[str, str]], int]:
    gaps: List[Dict[str, str]] = []

    p1_meta = phase1_dir / "meta.json"
    p1_visible = phase1_dir / "visible.txt"
    p3_parse = phase3_dir / "board_results_parse_instructions.json"
    p3_meta = phase3_dir / "meta.json"

    for label, p in (
        ("phase1_meta", p1_meta),
        ("phase1_visible", p1_visible),
        ("phase3_parse", p3_parse),
    ):
        if not p.is_file():
            gaps.append(_gap(label, "error", f"Missing required file: {p}"))

    if gaps:
        return {}, gaps, 1

    meta1 = _load_json(p1_meta)
    widgets = _load_json(widgets_path)
    parse_instructions = _load_json(p3_parse)
    meta3 = _load_json(p3_meta) if p3_meta.is_file() else {}

    widgets_nested = _build_widgets_nested(widgets)
    search_keys = _build_search_keys(widgets_nested)
    gaps.extend(_gaps_for_search_keys(search_keys, widgets_nested))
    if not widgets.get("inline_tray_option_lists"):
        gaps.append(
            _gap(
                "inline_tray_option_lists_missing",
                "warn",
                "widgets.json has no inline_tray_option_lists; re-run a16z_board_phase2_widget_inventory.py",
            )
        )

    if mirror_inputs:
        inputs_dir = out_path.parent / "inputs"
        inputs_dir.mkdir(parents=True, exist_ok=True)
        for src in (p1_meta, p1_visible, widgets_path, p3_parse, p3_meta):
            if src.is_file():
                shutil.copy2(src, inputs_dir / src.name)

    spike_notes_parts: List[str] = []
    if meta3.get("job_cards_visible") == 0:
        spike_notes_parts.append("Phase 3 run reported zero job cards after filters.")
    draft: Dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "board_key": BOARD_KEY,
        "label": LABEL,
        "entry_url": ENTRY_URL,
        "widgets": widgets_nested,
        "search_keys": search_keys,
        "parse_instructions": parse_instructions,
        "scrape_mode": "interactive",
        "spike_notes": " ".join(spike_notes_parts) if spike_notes_parts else "",
        "assembled_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_artifacts": {
            "AST-422": {
                "phase1_dir": str(phase1_dir.resolve()),
                "meta.json": str(p1_meta.resolve()),
                "visible.txt": str(p1_visible.resolve()),
            },
            "AST-423": {"widgets.json": str(widgets_path.resolve())},
            "AST-424": {
                "phase3_dir": str(phase3_dir.resolve()),
                "board_results_parse_instructions.json": str(p3_parse.resolve()),
                "meta.json": str(p3_meta.resolve()) if p3_meta.is_file() else None,
            },
        },
        "reach_profile": _reach_profile(meta1 if isinstance(meta1, dict) else {}),
        "widget_inventory_summary": _widget_inventory_summary(widgets),
        "gaps": gaps,
    }
    exit_code = 1 if any(g.get("severity") == "error" for g in gaps) else 0
    return draft, gaps, exit_code


def main() -> None:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Input search order (first existing wins unless overridden):\n"
            "  Phase 1: debug/spikes/AST-422/, AST-422/phase1/run/, heavybit/phase1/run/\n"
            "  Phase 2: debug/spikes/AST-423/widgets.json, heavybit/phase2/widgets.json\n"
            "  Phase 3: debug/spikes/AST-424/, AST-424/phase3/run/, heavybit/phase3/run/\n"
            "  --allow-legacy-paths: also artifacts/heavybit/… and debug/spikes/older/heavybit/…\n"
            "New output must use debug/spikes/AST-425/ (not artifacts/ or heavybit/phase4)."
        ),
    )
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    p.add_argument("--phase1-dir", type=Path, default=None)
    p.add_argument("--widgets-json", type=Path, default=None)
    p.add_argument("--phase3-dir", type=Path, default=None)
    p.add_argument(
        "--allow-legacy-paths",
        action="store_true",
        help="Search artifacts/heavybit/ and debug/spikes/older/ after defaults",
    )
    p.add_argument(
        "--mirror-inputs",
        action="store_true",
        help="Copy resolved inputs to debug/spikes/AST-425/inputs/",
    )
    args = p.parse_args()

    phase1 = _resolve_phase1_dir(args.phase1_dir, args.allow_legacy_paths)
    widgets = _resolve_widgets(args.widgets_json, args.allow_legacy_paths)
    phase3 = _resolve_phase3_dir(args.phase3_dir, args.allow_legacy_paths)

    gaps: List[Dict[str, str]] = []
    if phase1 is None:
        gaps.append(
            _gap(
                "phase1_missing",
                "error",
                "Phase 1 dir not found; re-run a16z_board_phase1_reach.py --out-dir debug/spikes/AST-422/ "
                "or pass --phase1-dir",
            )
        )
    if widgets is None:
        gaps.append(
            _gap(
                "widgets_missing",
                "error",
                "widgets.json not found; re-run phase2 with --out debug/spikes/AST-423/widgets.json "
                "or pass --widgets-json",
            )
        )
    if phase3 is None:
        gaps.append(
            _gap(
                "phase3_missing",
                "error",
                "Phase 3 dir not found; re-run phase3 with --out-dir debug/spikes/AST-424/ "
                "or pass --phase3-dir",
            )
        )

    if gaps:
        draft = {
            "schema_version": SCHEMA_VERSION,
            "board_key": BOARD_KEY,
            "gaps": gaps,
            "assembled_at_utc": datetime.now(timezone.utc).isoformat(),
        }
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(draft, ensure_ascii=False, indent=2), encoding="utf-8")
        for g in gaps:
            print(f"GAP [{g['severity']}] {g['id']}: {g['message']}", file=sys.stderr)
        sys.exit(1)

    draft, asm_gaps, code = assemble(
        phase1,
        widgets,
        phase3,
        mirror_inputs=bool(args.mirror_inputs),
        out_path=args.out,
    )
    draft["gaps"] = asm_gaps
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(draft, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {args.out}")
    if code != 0:
        for g in asm_gaps:
            print(f"GAP [{g['severity']}] {g['id']}: {g['message']}", file=sys.stderr)
    sys.exit(code)


if __name__ == "__main__":
    main()
