# Spike: Heavybit Jobs board profile Phase 4 — board_profile_draft.json (spike only)

- **Linear:** [AST-425](https://linear.app/astralcareermatch/issue/AST-425/spike-heavybit-jobs-board-profile-phase-4-board-profile-draftjson)
- **Parent:** [AST-413](https://linear.app/astralcareermatch/issue/AST-413/spike-heavybit-jobs-board-profile-playwright-phased)
- **Feature ref:** `ftr/AST-425`
- **Blocked by:** [AST-424](https://linear.app/astralcareermatch/issue/AST-424) — Susan gate unless waived
- **Canonical JSON shape:** [AST-414](https://linear.app/astralcareermatch/issue/AST-414) attachment **`board_profile_draft.json` schema v3** (Susan-approved 2026-05-17)

## Summary

Stdlib assembler reads Heavybit Phase 1–3 artifacts and writes **`debug/spikes/AST-425/board_profile_draft.json`** using **schema v3**: nested **`widgets`** (by `w-*` id), page-label-keyed **`search_keys`** (no Astral-canonical keys like `title_query`), plus **`parse_instructions`**. No `BOARD_CONFIG` / product code.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `scripts/spikes/heavybit_board_phase4_emit_profile_draft.py` | Assembler (fork `a16z_board_phase4_emit_profile_draft.py` constants) | scripts |
| `docs/features/boards/ast-425-spike-heavybit-jobs-board-profile-phase-4-board-profile-draftjson-spike-only.md` | This plan only | docs |

## Stage 1: Schema v3 (normative)

**Done when:** Table below matches assembler output.

| Key | Type | Notes |
|-----|------|--------|
| `schema_version` | string | `"3"` |
| `board_key` | string | `heavybit` |
| `label` | string | e.g. `Heavybit Jobs` |
| `entry_url` | string | `https://www.heavybit.com/jobs` |
| `widgets` | object | Keys = `w-00001` … full control + nested `lookup` |
| `search_keys` | object | Keys = **on-page labels** (`Location`, `Anytime`, …) → `{widget_id, options[], locator_playwright, lookup_pattern?, subtitle?}` |
| `parse_instructions` | object | Verbatim Phase 3 JSON |
| `scrape_mode` | string | `interactive` or `deep_link` per spike finding |
| `spike_notes` | string | Gaps, zero-card runs |
| `assembled_at_utc`, `source_artifacts`, `reach_profile`, `widget_inventory_summary`, `gaps` | enrichment | Same pattern as **AST-414** |

**`widgets[id].lookup`:** `pattern` + `options[]` as `{value, label}`; typeahead options trimmed in assembler (`Engineer4701` → `Engineer`) via trailing-digit strip **only when `pattern == "typeahead"`**.

**Forbidden in draft:** top-level `title_query` / `work_mode` / `criteria_param_map` / `astral_search_key` — promotion to Astral names is **AST-415** / Susan, not this spike.

## Stage 2: Assembler script

**Done when:** `python3 scripts/spikes/heavybit_board_phase4_emit_profile_draft.py --mirror-inputs` writes draft.

1. Create `scripts/spikes/heavybit_board_phase4_emit_profile_draft.py`:
   - Fork logic from `a16z_board_phase4_emit_profile_draft.py` (shared helpers acceptable in follow-on refactor; **this ticket** may duplicate minimally to avoid cross-ticket coupling).
   - Constants: `BOARD_KEY = "heavybit"`, `LABEL = "Heavybit Jobs"`, `ENTRY_URL = "https://www.heavybit.com/jobs"`.
   - Defaults: `debug/spikes/AST-422/`, `AST-423/widgets.json`, `AST-424/`; `--allow-legacy-paths` off by default.
   - `--out` default: **`debug/spikes/AST-425/board_profile_draft.json`**
   - `--mirror-inputs` → `debug/spikes/AST-425/inputs/`
   - Mechanical join: block trays by toggle label; inline trays by `widget_id`; build `search_keys` from interactions `text_entry | block_tray | inline_tray` only.

## Stage 3: Run + Linear handoff

**Done when:** Code Complete + attachment.

2. Re-run Phase 1–3 into `debug/spikes/AST-NNN/` if inputs missing.
3. Run assembler; attach `board_profile_draft.json` on **AST-425** (Linear upload, not GitHub link to gitignored path).

## Execution contract

- No `src/utils/config.py` / `BOARD_CONFIG`.
- No committed spike markdown except this plan on `ftr/AST-425`.

## Self-Assessment

### Scope

**Single-Component** — one assembler script + plan.

### Conf

**Medium** — depends on Phase 1–3 paths; schema copied from **AST-414** v3.

### Risk

**low** — local JSON only.

## Self-review vs ASTRAL_CODE_RULES

- §3.6: all R&D under `debug/spikes/AST-425/`.
- §1.3: `scripts/spikes/` only.
