---
id: pattern.dispatch.score-floor
name: dispatch_task.score_floor as sole numeric floor
status: approved
proposed_in: AST-1275
approved_by: Archie
approved_at: "2026-08-08"
canonical_refs:
  - path: src/utils/config.py
    symbol: effective_dispatch_score_floor
  - path: src/utils/config.py
    symbol: DISPATCH_SCORE_FLOOR_VALUES
  - path: src/core/consult.py
    symbol: _dispatch_score_floor_for_task
  - path: docs/ASTRAL_CODE_RULES.md
    symbol: "§2.1"
related_statutes:
  - astral.config.config-source-of-truth
  - astral.standards.no-hardcoded-sets
  - astral.idioms.render-verdict-orchestrates-consult
supersedes: null
superseded_by: null
---

# Problem

Scored consult / prefilter hops need one numeric floor for eligibility and post-run pass vs soft-fail. A parallel `TASK_CONFIG` threshold (`pass_threshold`) drifts from the candidate’s `dispatch_task` row and reintroduces magic floors.

# Solution shape

Treat `dispatch_task.score_floor` on the candidate’s matching row as the **sole** numeric floor for a scored step:

- **Claim / count eligibility** and **scored soft-fail after the run** both read that row value (via `effective_dispatch_score_floor` / `_dispatch_score_floor_for_task` — pointers in `canonical_refs`).
- Explicit `0` / `0.0` is valid and means no numeric soft-fail / no claim exclusion by floor.
- `NULL` / missing normalizes to `1.0` for those paths (existing claim rule; same helper for verdict).
- Do **not** put a numeric floor on `TASK_CONFIG`. Do **not** invent a coding statute for this concept — pattern only.
- Dealbreaker (F-with-confidence) and technical-error fail paths stay outside the numeric floor.
- Admin Score Floor options come from config (`DISPATCH_SCORE_FLOOR_VALUES` / labels API), including `0`.

Point at `canonical_refs` — do not paste large code into this catalog entry.

## When not to use

- Non-scored hops that do not consult `latest_score` / soft-fail math.
- Resurrecting `pass_threshold` (or any synonym) on `TASK_CONFIG` as a second floor.
- Turning this package into a coding statute under `canon/statutes/**`.

## Notes

Proposed in parent AST-1275 architectural definition; Archie approved `pattern.dispatch.score-floor` on AST-1281 (2026-08-08); runtime landed by AST-1277 / admin `0` by AST-1278; catalog + Code Rules by AST-1279. Retires the teaching of `astral.config.pass-threshold-vs-score-floor`.
