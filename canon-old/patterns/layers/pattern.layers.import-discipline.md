---
id: pattern.layers.import-discipline
name: Layer import and I/O discipline
status: approved
proposed_in: AST-913
approved_by: Archie
approved_at: "2026-07-24"
canonical_refs:
  - path: docs/ASTRAL_CODE_RULES.md
    symbol: "§3.3"
  - path: docs/ASTRAL_CODE_RULES.md
    symbol: "§2.5"
related_statutes:
  - astral.layers.import-direction
  - astral.layers.core-vs-external-bright-line
supersedes: null
superseded_by: null
---

# Problem

Cross-layer imports and I/O ownership blur, creating cycles and untestable core.

# Solution shape

Honor the import direction table (ui→core/utils; core→data/external/utils; external/data→utils; utils pure except the logging late-import carve-out). External owns I/O; core owns orchestration. Point at `canonical_refs` — do not paste large code into this catalog entry.

## When not to use

- ui importing data or external.
- utils importing core.
- Copying the logging `utils→data` late-import elsewhere.
