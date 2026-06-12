# Spike: Heavybit Jobs board profile Phase 3 — search, visible results + parse instructions

- **Linear:** [AST-424](https://linear.app/astralcareermatch/issue/AST-424/spike-heavybit-jobs-board-profile-phase-3-search-visible-results-parse)
- **Parent:** [AST-413](https://linear.app/astralcareermatch/issue/AST-413/spike-heavybit-jobs-board-profile-playwright-phased)
- **Feature ref:** `ftr/AST-424`
- **Blocked by:** [AST-423](https://linear.app/astralcareermatch/issue/AST-423) — Susan gate unless waived

## Summary

One honest parameterized search on Heavybit jobs using **widget ids from Phase 2**; write **`debug/spikes/AST-424/results_visible.txt`**, **`board_results_parse_instructions.json`**, **`meta.json`**.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `scripts/spikes/heavybit_board_phase3_search_and_parse_spec.py` | New CLI | scripts |

## Stage 1: Search + parse spec script

**Done when:** All three files exist under `debug/spikes/AST-424/`.

1. Create `scripts/spikes/heavybit_board_phase3_search_and_parse_spec.py`:
   - `--widgets-json` required (default `debug/spikes/AST-423/widgets.json` if exists).
   - `--out-dir` default: **`debug/spikes/AST-424/`**
   - `--url` default `https://www.heavybit.com/jobs`; allow `https://www.heavybit.com/jobs?query=US` when meta documents alternate entry.
   - Load widgets; map search actions to **Heavybit** control ids discovered in Phase 2 (not hard-coded a16z `w-00002` unless ids match by coincidence).
   - Apply one representative search (title + at least one filter Susan agreed in Phase 2 comment — if none, use title-only and note in `meta.json`).
   - Capture results region via JS (densest job-card root — document `results_region_strategy` in meta).
   - Write `board_results_parse_instructions.json` with keys: `container`, `job_tag`, `job_link`, `title`, `company`, `posted`, `notes` (selectors verified against this run's DOM).

2. `meta.json` must include: `filters_applied`, `job_cards_visible`, `networkidle_errors[]`, `widgets_json` path, `entry_url` used.

## Stage 2: Run + handoff

**Done when:** Linear attachments for parse spec + results snippet.

3. Run after **AST-423** gate; attach key files on **AST-424**.

## Execution contract

- No `board_profile_draft.json` (**AST-425**).
- No SQLite / ingest.

## Self-Assessment

### Scope

**Single-Component** — one script.

### Conf

**Medium** — widget ids and selectors are board-specific.

### Risk

**Medium** — wrong selectors poison Phase 4; meta must record card counts.

## Self-review vs ASTRAL_CODE_RULES

- §3.6: `debug/spikes/AST-424/`.
