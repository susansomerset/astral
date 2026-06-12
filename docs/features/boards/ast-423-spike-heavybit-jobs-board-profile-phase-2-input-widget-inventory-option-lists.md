# Spike: Heavybit Jobs board profile Phase 2 — input widget inventory + option lists

- **Linear:** [AST-423](https://linear.app/astralcareermatch/issue/AST-423/spike-heavybit-jobs-board-profile-phase-2-input-widget-inventory)
- **Parent:** [AST-413](https://linear.app/astralcareermatch/issue/AST-413/spike-heavybit-jobs-board-profile-playwright-phased)
- **Feature ref:** `ftr/AST-423`
- **Blocked by:** [AST-422](https://linear.app/astralcareermatch/issue/AST-422) — Susan gate (**Review Posted** / **User Testing** / **Done**) unless waived in comment on **AST-423**

## Summary

Inventory **all input-related controls** on Heavybit jobs; capture **`controls[]`**, **`block_tray_option_lists`**, **`inline_tray_option_lists`** into **`debug/spikes/AST-423/widgets.json`**. Real page labels only — no fabricated Astral parameter names.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `scripts/spikes/heavybit_board_phase2_widget_inventory.py` | New CLI; fork a16z patterns where DOM matches | scripts |

## Stage 1: Widget inventory script

**Done when:** `widgets.json` validates against shape produced by a16z Phase 2 (same top-level keys).

1. Create `scripts/spikes/heavybit_board_phase2_widget_inventory.py`:
   - `DEFAULT_URL = "https://www.heavybit.com/jobs"`
   - `--out` default: **`debug/spikes/AST-423/widgets.json`**
   - Reuse collectors from `a16z_board_phase2_widget_inventory.py` where selectors apply (`block-tray-toggle`, `inline-tray-toggle`, `button.select-option`, typeahead, select-pill, salary panel).
   - **Heavybit-specific:** add `_COLLECT_JS` / tray extract adjustments only where Phase 1 `visible.txt` shows different class names — document each override in script header comment.
   - Assign stable `w-00001` … ids after dedupe (same algorithm as a16z).
   - Emit `linear_id: "AST-423"`, `target_url`, `generated_at_utc`, `consent_dismissal`, `controls`, `dedupe_notes`, `block_tray_option_lists`, `inline_tray_option_lists`.

2. Open each filter tray and inline menu; capture **verbatim** option labels (no trimming in Phase 2 — trimming is Phase 4 assembler job per **AST-414** v3).

## Stage 2: Run + handoff

**Done when:** `widgets.json` attached on Linear at Code Complete.

3. Run after **AST-422** gate; attach `widgets.json` on **AST-423**.

## Execution contract

- No search/parse (**AST-424**).
- No profile draft (**AST-425**).

## Self-Assessment

### Scope

**Single-Component** — one script.

### Conf

**Medium** — DOM may differ from a16z; expect Heavybit-only selector tweaks.

### Risk

**low** — local spike output.

## Self-review vs ASTRAL_CODE_RULES

- §3.6: output path `debug/spikes/AST-423/`.
