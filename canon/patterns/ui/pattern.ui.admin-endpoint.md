---
id: pattern.ui.admin-endpoint
name: Admin endpoint conventions
status: approved
proposed_in: AST-913
approved_by: Archie
approved_at: "2026-07-24"
canonical_refs:
  - path: src/ui/api/api_admin.py
    symbol: admin_config
  - path: src/ui/auth.py
    symbol: require_auth
  - path: docs/ASTRAL_CODE_RULES.md
    symbol: "§2.9"
related_statutes:
  - astral.patterns.require-auth-on-protected-endpoints
  - astral.layers.ui-config-driven-business-logic
supersedes: null
superseded_by: null
---

# Problem

New admin HTTP surfaces need a consistent auth and thin-API shape without burying business rules in React.

# Solution shape

Add routes on the admin blueprint with `@require_auth`. Keep business rules config-driven and resolved in the API layer; React renders the resolved response. Point at `canonical_refs` — do not paste large code into this catalog entry.

## When not to use

- Open admin mutators without auth.
- Putting eligibility or state rules only in the frontend.
- Calling data or external from ui.
