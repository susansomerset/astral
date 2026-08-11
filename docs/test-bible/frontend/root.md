# App and routes

**Test tree:** `tests/component/root/`

## Coverage map

Vitest tests live under **`tests/component/frontend/`** (mirror `components/`, `pages/`, `contexts/`, `lib/`, and higher-level **`test_App`** / **`test_routes`** as needed).

There is **no** per-source-file branch-lock table (**§6b**). Prefer adding or extending tests beside the modules they guard. Coverage artifacts land in **`tests/.coverage/frontend/`** when `./scripts/testing/run_component_tests.sh` runs the Vitest **coverage** target.

| Ticket | Behavior | Sources | Manifest |
| --- | --- | --- | --- |
| **AST-1300** | Approved `pattern.ui.shared-button-roles` + `pattern.ui.icon-control`; unused `.btn` / `.icon-control` in `App.css` | `src/ui/frontend/src/App.css`, `canon/patterns/ui/pattern.ui.shared-button-roles.md`, `canon/patterns/ui/pattern.ui.icon-control.md`, `canon/patterns/README.md`, `canon/patterns/HARVEST.md` | docs-acceptance (grep/read) — no pytest; call-site remediations are **AST-1301** / **AST-1302** |

---

### AST-1300 · AST-1166 (codify button + icon-control patterns)

**Canon + unused shared CSS.** Live edits on **`origin/sub/AST-1166/AST-1300-codify-button-icon-control-patterns`**: `canon/patterns/ui/pattern.ui.shared-button-roles.md` + `canon/patterns/ui/pattern.ui.icon-control.md` (`status: approved`, `proposed_in: AST-1166`, `approved_by: Archie`); `canon/patterns/README.md` / `HARVEST.md` index rows; `src/ui/frontend/src/App.css` TOC **14–15** plus `.btn` / `.btn.primary` / `.btn.secondary` / `.btn.danger` / `.btn.primary.in-flight` / `.icon-control`. No TSX call-site remediations (siblings **AST-1301** / **AST-1302**). Leftover families (`modal-btn`, `dep-btn`, `job-list-icon-btn`, `list-page-bulk-btn`, …) stay until those siblings retire them.

**No new component or integration tests.** §6c N/A (no page / filter UX). Existing **AST-645** `.in-flight` wiring tests stay valid for leftover families — not in this manifest. Integration scenarios do not assert button-class catalogs — no drift.

**`test-child`:** docs-acceptance (grep/read on publish tip) — no pytest / zero-arg harness / branch-lock gate.

1. **Patterns approved** — both files `status: approved`, `approved_by: Archie`, `proposed_in: AST-1166`; `canonical_refs` point at `src/ui/frontend/src/App.css` symbols `.btn.primary` / `.btn.secondary` / `.btn.danger` / `.btn.primary.in-flight` and `.icon-control`.
2. **Catalog indexes** — README harvested-corpus rows list both ids as `approved`; HARVEST has supporting-package + Crosswalk `create (AST-1300)` rows (no define-parent AC cite-map rows).
3. **App.css contract** — TOC lines `14. Shared button roles` / `15. Icon control`; selectors above exist; `.btn.primary` uses `var(--cta-green)`; `.btn.primary.in-flight` uses `var(--accent-gold)`; `.btn.danger` uses `var(--danger)` + `#fff`; leftover `.modal-btn` / `.dep-btn` / `.job-list-icon-btn` / `.list-page-bulk-btn` still present.
4. **Scope gate** — no TSX `className` uses catalog `btn primary|secondary|danger` or `icon-control`; no `Button.tsx` / `IconControl.tsx`.

---

### AST-649 · AST-648 (historical — SUNSET AST-757)

**Historical (AST-649):** Candidate **Board Searches** nav/route/page retired; **`gaze_board`** hidden from Admin Scheduled Actions APIs. Backend boards module and **`/api/boards`** removed **AST-765**; schema dropped **AST-766**. No active boards manifest. See **`docs/ASTRAL_CODE_RULES.md` §3.7**.
