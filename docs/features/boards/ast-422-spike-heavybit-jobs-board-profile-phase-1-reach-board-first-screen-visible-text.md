# Spike: Heavybit Jobs board profile Phase 1 — reach board, first-screen visible text

- **Linear:** [AST-422](https://linear.app/astralcareermatch/issue/AST-422/spike-heavybit-jobs-board-profile-phase-1-reach-board-first-screen)
- **Parent:** [AST-413](https://linear.app/astralcareermatch/issue/AST-413/spike-heavybit-jobs-board-profile-playwright-phased)
- **Feature ref:** `ftr/AST-422`

## Summary

**Phase 1** spike: open **`https://www.heavybit.com/jobs`**, dismiss consent if present, capture first-screen **`visible.txt`**, optional **`a11y.json`**, **`meta.json`**. No widget inventory, search, or profile draft. Output under **`debug/spikes/AST-422/`** per §3.6.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `scripts/spikes/heavybit_board_phase1_reach.py` | New CLI (mirror `a16z_board_phase1_reach.py`) | scripts |

**Not committed:** `debug/spikes/AST-422/*`

## Stage 1: Reach script

**Done when:** `python3 scripts/spikes/heavybit_board_phase1_reach.py` writes three files under default out dir.

1. Create `scripts/spikes/heavybit_board_phase1_reach.py`:
   - Copy structure from `a16z_board_phase1_reach.py` (consent dismiss, networkidle, timeouts from ASTRAL_CODE_RULES §1.4 pattern).
   - `DEFAULT_URL = "https://www.heavybit.com/jobs"`
   - `--out-dir` default: **`debug/spikes/AST-422/`**
   - `--headed` optional.
   - Write `meta.json` (url, timestamps, playwright version, consent_dismissal strategy, body text length).
   - Write `visible.txt` from `document.body.innerText` or main landmark (same strategy as a16z: prefer densest job region if detectable on first paint — if none, full body).
   - Optional `a11y.json` snapshot (same as a16z phase1).

2. `PYTHONPATH=.` and `ASTRAL_DB_DIR` bootstrap like other spike scripts.

## Stage 2: Run + Linear handoff

**Done when:** Local run succeeds; **Code Complete** comment lists paths; Linear attachments (not GitHub blob links).

3. Run script; attach `visible.txt` + `meta.json` on **AST-422**.

## Execution contract

- No `src/` product changes.
- No `BOARD_CONFIG`.

## Self-Assessment

### Scope

**Single-Component** — one spike script.

### Conf

**Medium** — Heavybit DOM/consent unknown until first run.

### Risk

**low** — local `debug/` only.

## Self-review vs ASTRAL_CODE_RULES

- §3.6: `debug/spikes/AST-422/` only.
- §1.3: scripts/spikes only.

## Review

**Built by:** Hedy
**Branch:** `ftr/AST-422`
**Commits:** `a2a9e06d`
