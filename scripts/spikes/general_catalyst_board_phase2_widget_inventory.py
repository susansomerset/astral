#!/usr/bin/env python3
"""
AST-431 Phase 2: first-screen input-related controls on general_catalyst.com/jobs → widgets.json.

Fork of a16z Phase 2 collectors (`block-tray-toggle`, inline trays, typeahead, select-pill, salary panel).
General Catalyst-specific selector overrides go in script header only if Phase 1 `visible.txt` diverges.

Usage (repo root, PYTHONPATH=.):
  python3 scripts/spikes/general_catalyst_board_phase2_widget_inventory.py [--headed] [--url URL] [--out PATH]
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

if "ASTRAL_DB_DIR" not in os.environ:
    os.environ["ASTRAL_DB_DIR"] = str(_ROOT / "data")

from playwright.async_api import Page

from src.external.playwright import create_browser_context

DEFAULT_URL = "https://jobs.generalcatalyst.com/jobs"
NAV_TIMEOUT_MS = 120_000
POST_LOAD_WAIT_MS = 2_000
CONSENT_ROLE_TIMEOUT_MS = 4_000
CONSENT_LOCATOR_TIMEOUT_MS = 3_000
DEDUPE_BBOX_TOL_PX = 3
# a16z jobs board: typeahead trays need focus cleared + time before suggestions render.
TRAY_OPEN_WAIT_MS = 1_200

# Spike-only panel-ish labels (plan §3); not promoted to config until board profile exists.
_PANEL_NAME_RE = re.compile(
    r"filter|roles|location|departments|skills|posted|remote",
    re.I,
)


async def _dismiss_consent(page: Page) -> Optional[str]:
    """Same ordered strategy as Phase 1 (AST-430); duplicated here to stay under DRY extract threshold."""
    try:
        loc = page.get_by_role(
            "button", name=re.compile(r"accept|agree|ok|allow", re.I)
        )
        if await loc.count() > 0:
            await loc.first.click(timeout=CONSENT_ROLE_TIMEOUT_MS)
            await page.wait_for_timeout(400)
            return "get_by_role_button_regex"
    except Exception:
        pass
    for sel in ('[id*="cookie" i] button', '[class*="consent" i] button'):
        try:
            lo = page.locator(sel).first
            if await lo.is_visible(timeout=1_500):
                await lo.click(timeout=CONSENT_LOCATOR_TIMEOUT_MS)
                await page.wait_for_timeout(400)
                return sel
        except Exception:
            continue
    return None


# a16z-specific: `button.block-tray-toggle` filter trays (Roles, Skills, …). Not a generic crawler.
_TRAY_PANEL_EXTRACT_JS = r"""
() => {
  const ta = document.querySelector('.typeahead-container-open');
  if (ta) {
    const items = [];
    for (const o of ta.querySelectorAll('[role="option"]')) {
      const r = o.getBoundingClientRect();
      if (r.width < 1 || r.height < 1) continue;
      items.push((o.innerText || o.textContent || '').trim());
    }
    if (items.length) return { pattern: 'typeahead', items };
  }
  const pillRoot = document.querySelector('.select-pill-options');
  if (pillRoot) {
    const items = [];
    pillRoot.querySelectorAll('.select-pill-option').forEach((p) => {
      items.push({
        value: p.getAttribute('data-pill-value') || '',
        label: (p.innerText || p.textContent || '').trim(),
      });
    });
    if (items.length) return { pattern: 'select_pill', items };
  }
  const sal = document.querySelector('.salary-input-tray');
  if (sal) {
    return {
      pattern: 'salary_range_slider',
      items: [],
      panel_inner_text: (sal.innerText || sal.textContent || '').trim(),
    };
  }
  return { pattern: 'unknown', items: [], parse_note: 'no recognized tray body' };
}
"""


async def _blur_and_close_trays(page: Page) -> None:
    """Move focus off tray inputs so the next `block-tray-toggle` click is not intercepted."""
    try:
        await page.locator("h1").first.click(timeout=5_000)
    except Exception:
        pass
    for _ in range(8):
        await page.keyboard.press("Escape")
        await page.wait_for_timeout(120)
    await page.wait_for_timeout(300)


async def _collect_block_tray_option_lists(page: Page) -> List[Dict[str, Any]]:
    """
    Open each `button.block-tray-toggle` on general_catalyst.com/jobs and read whatever option UI appears.
    Patterns: React typeahead suggestions, company-stage pills, salary range panel (no discrete list).
    """
    loc = page.locator("button.block-tray-toggle")
    n = await loc.count()
    out: List[Dict[str, Any]] = []
    for i in range(n):
        await _blur_and_close_trays(page)
        btn = loc.nth(i)
        label = (await btn.inner_text()).strip()
        await btn.click(timeout=8_000)
        await page.wait_for_timeout(TRAY_OPEN_WAIT_MS)
        chunk = await page.evaluate(_TRAY_PANEL_EXTRACT_JS)
        row: Dict[str, Any] = {
            "tray_index": i,
            "toggle_visible_label": label,
            "pattern": chunk.get("pattern"),
            "items": chunk.get("items") or [],
        }
        if chunk.get("parse_note"):
            row["parse_note"] = chunk["parse_note"]
        if chunk.get("panel_inner_text") is not None:
            row["panel_inner_text"] = chunk["panel_inner_text"]
        out.append(row)
    return out


_INLINE_TRAY_OPTIONS_JS = r"""
() => {
  const items = [];
  for (const b of document.querySelectorAll('button.select-option')) {
    const t = (b.innerText || b.textContent || '').trim();
    if (t) items.push(t);
  }
  return items;
}
"""


async def _collect_inline_tray_option_lists(
    page: Page, controls: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Open each inline-tray control (All jobs, Anytime, …) and list `button.select-option` rows."""
    out: List[Dict[str, Any]] = []
    for c in controls:
        if "inline-tray-toggle" not in (c.get("css_path_hint") or ""):
            continue
        an = (c.get("accessible_name") or "").strip()
        label = an.split("\n")[0].strip() if an else (c.get("visible_text") or "").split("\n")[0].strip()
        if not label:
            continue
        await _blur_and_close_trays(page)
        try:
            await page.get_by_role("button", name=label).click(timeout=8_000)
        except Exception as exc:
            out.append(
                {
                    "widget_id": c.get("id"),
                    "toggle_label": label,
                    "pattern": "select_option",
                    "items": [],
                    "parse_note": f"could not open tray: {exc!r}",
                }
            )
            continue
        await page.wait_for_timeout(TRAY_OPEN_WAIT_MS)
        items = await page.evaluate(_INLINE_TRAY_OPTIONS_JS)
        out.append(
            {
                "widget_id": c.get("id"),
                "toggle_label": label,
                "pattern": "select_option",
                "items": items,
            }
        )
    return out


_COLLECT_JS = r"""
(panelPat) => {
  const panelRe = new RegExp(panelPat, 'i');
  const sel = [
    'input', 'textarea', 'select', 'button',
    '[role="textbox"]', '[role="combobox"]', '[role="listbox"]',
    '[role="button"]', '[role="switch"]', '[role="checkbox"]', '[role="radio"]',
    '[contenteditable="true"]',
  ].join(', ');
  const nodes = Array.from(document.querySelectorAll(sel));

  function ariaHiddenSelf(el) {
    return el && el.getAttribute('aria-hidden') === 'true';
  }

  function visible(el) {
    if (!el || ariaHiddenSelf(el)) return false;
    const cs = window.getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') return false;
    const op = parseFloat(cs.opacity || '1');
    if (op === 0) return false;
    const r = el.getBoundingClientRect();
    if (r.width < 1 || r.height < 1) return false;
    return true;
  }

  function accName(el) {
    const al = el.getAttribute('aria-label');
    if (al && al.trim()) return al.trim();
    const lb = el.getAttribute('aria-labelledby');
    if (lb) {
      let t = '';
      for (const piece of lb.trim().split(/\s+/)) {
        if (!piece) continue;
        const node = document.getElementById(piece);
        if (node) t += (node.innerText || node.textContent || '') + ' ';
      }
      if (t.trim()) return t.trim();
    }
    const id = el.getAttribute('id');
    if (id && typeof CSS !== 'undefined' && CSS.escape) {
      try {
        const lab = document.querySelector('label[for="' + CSS.escape(id) + '"]');
        if (lab) return (lab.innerText || lab.textContent || '').trim();
      } catch (e) { /* ignore */ }
    }
    const ph = el.getAttribute('placeholder');
    if (ph && ph.trim()) return ph.trim();
    const title = el.getAttribute('title');
    if (title && title.trim()) return title.trim();
    const nm = el.getAttribute('name');
    if (nm && nm.trim()) return nm.trim();
    const tag = el.tagName;
    const typ = (el.getAttribute('type') || '').toLowerCase();
    if (tag === 'BUTTON' || (tag === 'INPUT' && /^(button|submit|reset)$/i.test(typ)))
      return (el.innerText || el.textContent || '').trim();
    return '';
  }

  function visibleText(el) {
    if (typeof el.innerText === 'string' && el.innerText.length) return el.innerText;
    return (el.textContent || '') || '';
  }

  function bbox(el) {
    const r = el.getBoundingClientRect();
    return {
      x: Math.round(r.x),
      y: Math.round(r.y),
      width: Math.round(r.width),
      height: Math.round(r.height),
    };
  }

  function cssHint(el) {
    const id = el.getAttribute('id');
    if (id) return '#' + id;
    const cls = (el.getAttribute('class') || '').trim().split(/\s+/).filter(Boolean)[0];
    if (cls) return el.tagName.toLowerCase() + '.' + cls;
    return null;
  }

  const out = [];
  const seen = new Set();
  for (const el of nodes) {
    if (!visible(el)) continue;
    let key = el.tagName + '|' + (el.getAttribute('type') || '') + '|' + (el.getAttribute('id') || '');
    if (el.tagName === 'INPUT' || el.tagName === 'BUTTON')
      key += '|' + bbox(el).x + ',' + bbox(el).y;
    else key += '|' + bbox(el).x + ',' + bbox(el).y + ',' + bbox(el).width + ',' + bbox(el).height;
    if (seen.has(key)) continue;
    seen.add(key);

    const tag = el.tagName;
    const inputType = el.getAttribute('type') || '';
    const roleAttr = el.getAttribute('role');
    const multiple = tag === 'SELECT' ? !!el.multiple : false;
    const selectSize = tag === 'SELECT' ? (el.size || 0) : 0;
    const contentEditable = el.getAttribute('contenteditable');
    const nameStr = accName(el);
    const vtext = visibleText(el);
    const panelish =
      tag === 'BUTTON' &&
      (el.getAttribute('aria-expanded') != null ||
        el.getAttribute('aria-haspopup') != null ||
        panelRe.test(nameStr) ||
        panelRe.test(vtext));

    out.push({
      tag,
      inputType,
      roleAttr,
      multiple,
      selectSize,
      contentEditable,
      accessible_name: nameStr,
      visible_text: vtext,
      bounding_box: bbox(el),
      css_path_hint: cssHint(el),
      panelish_button: !!panelish,
    });
  }
  return out;
}
"""


def _infer_kind(row: Dict[str, Any]) -> str:
    tag = (row.get("tag") or "").upper()
    typ = (row.get("inputType") or "").lower()
    r = (row.get("roleAttr") or "").lower()
    ce = (row.get("contentEditable") or "").lower() == "true"

    if r == "textbox" or ce:
        return "textbox"
    if r == "combobox":
        return "combobox"
    if r == "listbox":
        return "listbox"
    if r == "button":
        return "button"
    if r == "switch":
        return "other"
    if r == "checkbox":
        return "checkbox"
    if r == "radio":
        return "radio"

    if tag == "TEXTAREA" or (tag == "INPUT" and typ in ("text", "search", "email", "url", "tel", "password", "number")):
        return "textbox"
    if tag == "INPUT" and typ == "checkbox":
        return "checkbox"
    if tag == "INPUT" and typ == "radio":
        return "radio"
    if tag == "INPUT" and typ in ("button", "submit", "reset", "image"):
        return "button"
    if tag == "INPUT":
        return "textbox"
    if tag == "SELECT":
        if row.get("multiple") or int(row.get("selectSize") or 0) > 1:
            return "listbox"
        return "combobox"
    if tag == "BUTTON":
        return "button"
    return "other"


def _infer_aria_role(row: Dict[str, Any], kind: str) -> Optional[str]:
    if row.get("roleAttr"):
        return str(row["roleAttr"])
    if kind == "textbox":
        return "textbox"
    if kind == "combobox":
        return "combobox"
    if kind == "listbox":
        return "listbox"
    if kind == "button":
        return "button"
    if kind == "checkbox":
        return "checkbox"
    if kind == "radio":
        return "radio"
    return None


def _locator_playwright(row: Dict[str, Any], kind: str) -> str:
    name = row.get("accessible_name") or ""
    vtext = (row.get("visible_text") or "").strip().split("\n")[0].strip()
    label = name or vtext
    esc = json.dumps(label)
    hint = row.get("css_path_hint")

    if kind == "button":
        if label:
            return f"page.get_by_role('button', name={esc})"
        if hint:
            return f"page.locator({json.dumps(hint)})"
        return "page.get_by_role('button').nth(/* refine */)"
    if kind == "checkbox":
        return f"page.get_by_role('checkbox', name={esc})" if label else "page.locator('input[type=\"checkbox\"]')"
    if kind == "radio":
        return f"page.get_by_role('radio', name={esc})" if label else "page.locator('input[type=\"radio\"]')"
    if kind in ("textbox", "combobox", "listbox"):
        if row.get("tag") == "SELECT":
            return f"page.locator('select').filter(has_text={esc})" if label else "page.locator('select')"
        ph = row.get("accessible_name") or ""
        if ph and row.get("tag") == "INPUT":
            return f"page.get_by_placeholder({json.dumps(ph)})"
        return f"page.get_by_role('{kind}', name={esc})" if label else f"page.get_by_role('{kind}')"
    if hint:
        return f"page.locator({json.dumps(hint)})"
    return "page.locator('/* kind=other: refine manually */')"


def _bbox_tuple(b: Optional[Dict[str, Any]]) -> Optional[Tuple[int, int, int, int]]:
    if not b or not isinstance(b, dict):
        return None
    try:
        return (
            int(b["x"]),
            int(b["y"]),
            int(b["width"]),
            int(b["height"]),
        )
    except (KeyError, TypeError, ValueError):
        return None


def _bbox_close(
    a: Tuple[int, int, int, int], b: Tuple[int, int, int, int], tol: int = DEDUPE_BBOX_TOL_PX
) -> bool:
    return all(abs(a[i] - b[i]) <= tol for i in range(4))


def _dedupe(rows: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Dedupe by (accessible_name, kind, bbox) with bbox tolerance; keep first occurrence."""
    kept: List[Dict[str, Any]] = []
    notes: List[Dict[str, Any]] = []
    for r in rows:
        bb = _bbox_tuple(r.get("bounding_box"))
        name = r.get("accessible_name") or ""
        kind = r["kind"]
        dup_idx: Optional[int] = None
        for i, ex in enumerate(kept):
            if (ex.get("accessible_name") or "") != name or ex["kind"] != kind:
                continue
            eb = _bbox_tuple(ex.get("bounding_box"))
            if bb is None or eb is None:
                if bb == eb:
                    dup_idx = i
                    break
            elif _bbox_close(bb, eb):
                dup_idx = i
                break
        if dup_idx is not None:
            notes.append(
                {
                    "reason": "same_accessible_name_kind_and_near_bbox",
                    "kept_control_index": dup_idx,
                    "dropped_css_path_hint": r.get("css_path_hint"),
                    "dropped_bounding_box": r.get("bounding_box"),
                }
            )
            continue
        kept.append(r)
    return kept, notes


async def _run(url: str, out_path: Path, headed: bool) -> None:
    raw_rows: List[Dict[str, Any]] = []
    consent: Optional[str] = None
    block_tray_option_lists: List[Dict[str, Any]] = []
    inline_tray_option_lists: List[Dict[str, Any]] = []
    async with create_browser_context(headless=not headed) as ctx:
        page = await ctx.new_page()
        await page.goto(url, wait_until="networkidle", timeout=NAV_TIMEOUT_MS)
        await page.wait_for_timeout(POST_LOAD_WAIT_MS)
        consent = await _dismiss_consent(page)
        await page.wait_for_timeout(400)
        raw_rows = await page.evaluate(_COLLECT_JS, _PANEL_NAME_RE.pattern)
        block_tray_option_lists = await _collect_block_tray_option_lists(page)

        controls: List[Dict[str, Any]] = []
        for row in raw_rows:
            kind = _infer_kind(row)
            row["kind"] = kind
            row["aria_role"] = _infer_aria_role(row, kind)
            row["locator_playwright"] = _locator_playwright(row, kind)
            controls.append(
                {
                    "kind": kind,
                    "aria_role": row["aria_role"],
                    "accessible_name": row.get("accessible_name") or "",
                    "visible_text": row.get("visible_text") or "",
                    "locator_playwright": row["locator_playwright"],
                    "css_path_hint": row.get("css_path_hint"),
                    "bounding_box": row.get("bounding_box"),
                    "_dedupe_key_bbox": row.get("bounding_box"),
                    "_dedupe_name": row.get("accessible_name") or "",
                }
            )

        deduped, dedupe_notes = _dedupe(controls)
        for c in deduped:
            c.pop("_dedupe_key_bbox", None)
            c.pop("_dedupe_name", None)

        for i, c in enumerate(deduped, start=1):
            c["id"] = f"w-{i:05d}"

        inline_tray_option_lists = await _collect_inline_tray_option_lists(page, deduped)

    payload: Dict[str, Any] = {
        "linear_id": "AST-431",
        "target_url": url,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "consent_dismissal": consent,
        "controls": deduped,
        "dedupe_notes": dedupe_notes,
        "block_tray_option_lists": block_tray_option_lists,
        "inline_tray_option_lists": inline_tray_option_lists,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = out_path.with_suffix(out_path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(out_path)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--url", default=DEFAULT_URL)
    p.add_argument(
        "--out",
        default=str(_ROOT / "debug/spikes/AST-431/widgets.json"),
        help="Output path for widgets.json",
    )
    p.add_argument("--headed", action="store_true")
    args = p.parse_args()
    asyncio.run(_run(args.url, Path(args.out), bool(args.headed)))


if __name__ == "__main__":
    main()
