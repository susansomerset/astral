# AST-1449 — Ungate candidate-facing nav by state

**Linear:** [AST-1449](https://linear.app/astralcareermatch/issue/AST-1449/ungate-candidate-facing-nav-by-state-remove-navigation-filter-for)  
**Parent:** [AST-1444](https://linear.app/astralcareermatch/issue/AST-1444/remove-navigation-filter-for-selected-candidate)  
**Publish ref:** `sub/AST-1444/AST-1449-ungate-candidate-facing-nav-by-state`

Operators lose whole left-nav groups when the selected candidate has not reached a pipeline state (Artifacts wait on `RESUME_READY`; Jobs and Companies wait on `ACTIVE_SEARCH`). This ticket removes those group-level candidate-state membership gates so every selected candidate gets the same candidate-facing list (Jobs, Companies, Artifacts, Candidate). Admin-only omit and permanently disabled stubs stay. Item enablement still resolves in `/api/nav_config`, not in React. This ticket does not add the read-only state line under the picker (sibling AST-1450).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Drop group-level `"visible"` from Jobs, Companies, and Artifacts; rewrite the NAV_CONFIG contract comments so they no longer describe group-level candidate-state hide | utils |
| `src/ui/api/api_system.py` | Stop skipping groups on `group["visible"]`; keep item-level `enabled` resolution and `_nav_config_for_user` admin omit | ui |
| `docs/ASTRAL_CODE_RULES.md` | Rewrite the §2.1 **NAV_CONFIG** bullet so it matches the product after the gate removal | docs |

Do not edit `NavigationShell.tsx`, `routes.tsx`, destination pages, job/company count helpers, `admin_only` grouping, or AST-1450 chrome. Do not edit `tests/` or `docs/test-bible/**` (Betty).

## Stage 1: Drop group-level nav hide; keep enablement and admin omit

**Done when:** `GET /api/nav_config?candidate_id=<id>` for a candidate in `NEW_CANDIDATE` (or any other selected state before `RESUME_READY` / `ACTIVE_SEARCH`) returns groups labeled Jobs, Companies, Artifacts, and Candidate; Applied and Responded appear with `"enabled": false`; a non-admin response still omits Operations, Admin, and Tools; no React file in this ticket’s Files Changed is modified.

1. In `src/utils/config.py`, replace the NAV_CONFIG header comment block that currently sits above `ADMIN_CONFIG` (the block starting `# NAV_CONFIG: UI navigation structure` through the `enabled` paragraph) with:

   ```
   # NAV_CONFIG: UI navigation structure. Grouped sidebar sections with labels
   # and route paths. Served to React frontend via /api/nav_config.
   #
   # Optional group-level "admin_only": True. When True, /api/nav_config omits
   # the group for non-admin users (resolved via nav_admin_only_group_labels).
   # Omit the key (or False) = visible to every authenticated user.
   #
   # Optional item-level "enabled": a CANDIDATE_STATES key (disabled unless at
   # or past that state) or False (permanently disabled stub). Omit = always enabled.
   #
   # Group-level candidate-state "visible" is not a NAV_CONFIG key. Do not add it.
   ```

   Leave the `ADMIN_CONFIG` comment that follows (`# ADMIN_CONFIG: Frontend-facing admin UI configuration…`) unchanged.

2. In `src/utils/config.py`, replace the comment immediately above `NAV_CONFIG = [` (the block starting `# The /api/nav_config endpoint in system.py resolves these against the`) with:

   ```
   # The /api/nav_config endpoint in api_system.py resolves item-level enabled
   # gates against the selected candidate's state and omits admin_only groups
   # for non-admins before serving. The frontend renders the resolved response
   # with no additional visibility logic.
   #
   # SYNC: Every path here must have a matching route in src/ui/frontend/src/routes.tsx.
   #       If you add/remove/rename a nav item, update routes.tsx to match.
   ```

3. In `src/utils/config.py` `NAV_CONFIG`, delete the `"visible"` key from these three groups only — do not change labels, item lists, paths, or `"enabled": False` on Applied / Responded:

   - Jobs: remove `"visible": "ACTIVE_SEARCH",`
   - Companies: remove `"visible": "ACTIVE_SEARCH",`
   - Artifacts: remove `"visible": "RESUME_READY",`

   Candidate stays without a group gate. Operations / Admin / Tools keep `"admin_only": True` only.

   ⚠️ **Decision:** Remove the group-level `visible` key and stop honoring it in the API, rather than leaving a dead skip that would hide groups again if a key were re-added. Membership is always the NAV_CONFIG list (minus admin_only for non-admins). Remaining state gating is item `enabled` only.

   ⚠️ **Decision:** Do not add a “hide candidate-facing groups when no candidate is selected” substitute. With `candidate_id` absent, `_resolve_nav` currently uses `candidate_state=""` which made `visible` skip Jobs/Companies/Artifacts; after this change those groups still appear (counts stay empty because `_get_*_counts(None)` returns `{}`). Parent AC is about selected candidates; this ticket does not invent a new empty-selection hide.

4. In `src/ui/api/api_system.py`, change `_resolve_nav` as follows:

   - Update the docstring from `Walk NAV_CONFIG and resolve visible/enabled gates against candidate_state.` to `Walk NAV_CONFIG and resolve item-level enabled gates against candidate_state.`
   - Delete the three lines that skip groups on `visible`:

     ```
     visible_gate = group.get("visible")
     if isinstance(visible_gate, str) and not _is_at_or_past(candidate_state, visible_gate):
         continue
     ```

   Keep the rest of the loop: `enabled_gate is False` → `enabled = False`; `isinstance(enabled_gate, str)` → `_is_at_or_past`; else `enabled = True`; attach `count` when present; append every group. Do not change `_progress_rank`, `_is_at_or_past`, `_get_company_counts`, `_get_job_counts`, `_nav_config_for_user`, or `nav_config()`.

5. In `docs/ASTRAL_CODE_RULES.md` §2.1 Config blocks, replace the **NAV_CONFIG** bullet (the single bullet that currently says groups may declare `visible`) with exactly:

   ```
   - **NAV_CONFIG**: UI navigation structure — sidebar groups, labels, and route paths. Groups may declare `admin_only: True` (omitted for non-admins via `nav_admin_only_group_labels`). Items may declare `enabled` as a `CANDIDATE_STATES` key (disabled unless at or past that state) or `False` (permanently disabled stub). Omit `enabled` = always enabled. Group-level candidate-state `visible` is not used. The `/api/nav_config` endpoint in `api_system.py` resolves item `enabled` against the selected candidate's state and omits `admin_only` groups for non-admins before serving. The frontend renders the resolved structure with no additional visibility logic.
   ```

   Do not edit other §2.1 bullets. Do not invent a new statute id. Do not edit `docs/features/interface/project_description.md` in this ticket.

6. Do not touch `src/ui/frontend/src/components/NavigationShell.tsx`. It already maps `navGroups` from `/api/nav_config` with no client-side state hide. Do not enable Applied or Responded. Do not empty-state-fix Jobs, Companies, Artifacts, or Candidate pages.

## Estimate

Confirm Chuckles estimate: 3 — agree
