---
id: pattern.config.config-block
name: Config block as source of truth
status: approved
proposed_in: AST-913
approved_by: Archie
approved_at: "2026-07-24"
canonical_refs:
  - path: src/utils/config.py
    symbol: TASK_CONFIG
  - path: docs/ASTRAL_CODE_RULES.md
    symbol: "§2.1"
related_statutes:
  - astral.config.config-source-of-truth
  - astral.standards.no-hardcoded-sets
supersedes: null
superseded_by: null
---

# Problem

New behavior-driving values and task definitions get scattered as magic sets and literals across layers.

# Solution shape

Add or extend a named block in `src/utils/config.py` (e.g. `TASK_CONFIG`, state registries). Secrets and env-specific values stay in `os.environ`. Callers read config — do not redefine the set inline. Point at `canonical_refs` — do not paste large code into this catalog entry.

## When not to use

- Putting secrets in config literals.
- Inventing a second source of truth in UI/React.
- Env `.get()` fallbacks for required secrets.
