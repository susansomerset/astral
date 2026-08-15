# AST-1386 — Three-segment admin nav (Group admin in the UI into three segments)

**Linear:** [AST-1386](https://linear.app/astralcareermatch/issue/AST-1386/three-segment-admin-nav-group-admin-in-the-ui-into-three-segments)  
**Parent:** [AST-1370](https://linear.app/astralcareermatch/issue/AST-1370/group-admin-in-the-ui-into-three-segments)  
**Publish ref:** `sub/AST-1370/AST-1386-three-segment-admin-nav`

The left-nav Admin section is one undifferentiated list. This ticket replaces that single `NAV_CONFIG` group with three admin-only segments — **Operations**, **Admin**, **Tools** — using Susan’s membership, order, and paste labels, and replaces the hard-coded non-admin omit of the literal label `"Admin"` with a config-driven `admin_only` flag so Operations/Tools cannot leak to non-admins. Routes, pages, and shell chrome stay unchanged; the frontend keeps rendering whatever `/api/nav_config` returns.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Document optional group `admin_only`; replace the single Admin `NAV_CONFIG` group with Operations / Admin / Tools (membership, order, paste labels); add `nav_admin_only_group_labels()` | utils |
| `src/ui/api/api_system.py` | Import `nav_admin_only_group_labels`; change `_nav_config_for_user` non-admin filter to omit every group whose label is in that set | ui |

No React files, `routes.tsx`, admin pages, auth, shell CSS, or test-tree edits. Betty owns any test updates that assert the old single Admin group or `label != "Admin"` omit.

## Stage 1: Regroup NAV_CONFIG and config-driven non-admin omit

**Done when:** An admin `/api/nav_config` response contains exactly three admin-facing groups labeled **Operations**, **Admin**, and **Tools** (in that order after Jobs / Companies / Artifacts / Candidate), with the item lists and paths below and paste labels **Resume Paste** / **Cover Letter Paste** on the existing paste paths; a non-admin response contains none of those three group labels; Jobs / Companies / Artifacts / Candidate groups are unchanged for the same candidate state; `NavigationShell` / routes / pages are untouched.

1. In `src/utils/config.py`, in the `NAV_CONFIG` header comment block (the block immediately above `NAV_CONFIG = [` that already documents optional group `visible` and item `enabled`), add one bullet after the `visible` paragraph:

   ```
   Optional group-level "admin_only": True. When True, /api/nav_config omits
   the group for non-admin users (resolved via nav_admin_only_group_labels).
   Omit the key (or False) = visible to every authenticated user subject to
   other gates.
   ```

   Do not rewrite the existing `visible` / `enabled` paragraphs.

2. In `src/utils/config.py`, replace the single trailing Admin group in `NAV_CONFIG` (the dict whose `"label"` is `"Admin"` and whose `items` currently list all admin screens) with **three** consecutive groups in this exact order, immediately after the Candidate group. Keep Jobs / Companies / Artifacts / Candidate groups byte-for-byte unchanged.

   **Operations** — `"label": "Operations"`, `"admin_only": True`, `items` in this order (paths unchanged from today’s Admin entries):

   | label | path |
   |-------|------|
   | Scheduled Actions | `/admin/scheduled_actions` |
   | Execution History | `/admin/performance_monitor` |
   | Vector Feedback | `/admin/vector_feedback` |
   | Manage Email | `/admin/manage_email` |
   | Manage Slack | `/admin/manage_slack` |
   | Manage Candidates | `/admin/manage_candidates` |

   **Admin** — `"label": "Admin"`, `"admin_only": True`, `items` in this order:

   | label | path |
   |-------|------|
   | Manage Agents | `/admin/agent_prompts` |
   | Manage Tasks | `/admin/task_prompts` |
   | Scheduled Queries | `/admin/scheduled_queries` |
   | Agent Timesheets | `/admin/agent_timesheets` |

   **Tools** — `"label": "Tools"`, `"admin_only": True`, `items` in this order:

   | label | path |
   |-------|------|
   | Data Management | `/admin/data_management` |
   | Agent Ad Hoc | `/admin/anthropic_ad_hoc` |
   | Cost Reconciliation | `/admin/cost_reconciliation` |
   | Resume Paste | `/admin/session_resume_paste` |
   | Cover Letter Paste | `/admin/session_cover_letter` |

   ⚠️ **Decision:** Paste nav labels become **Resume Paste** and **Cover Letter Paste** per parent Functional scope; destinations stay `/admin/session_resume_paste` and `/admin/session_cover_letter`. Do not rename routes or page titles in this ticket.

   ⚠️ **Decision:** Use group-level `"admin_only": True` on each of the three segments (derived by a helper) rather than a parallel hard-coded frozenset of three label strings in the API — satisfies `astral.standards.no-hardcoded-sets` and `astral.config.config-source-of-truth`. Do not put admin-only membership in React.

3. In `src/utils/config.py`, immediately after the `NAV_CONFIG = [ ... ]` closing `]`, add:

   ```python
   def nav_admin_only_group_labels() -> frozenset[str]:
       """Sidebar group labels omitted from /api/nav_config for non-admins (AST-1386)."""
       return frozenset(
           group["label"] for group in NAV_CONFIG if group.get("admin_only")
       )
   ```

   Truthy `admin_only` is enough (same style as other optional NAV_CONFIG keys). Do not add a second parallel list of label literals anywhere else.

4. In `src/ui/api/api_system.py`, add `nav_admin_only_group_labels` to the existing `from src.utils.config import (...)` list (alphabetically or next to `NAV_CONFIG` — match the file’s current import grouping; do not invent a new import style).

5. In `src/ui/api/api_system.py`, replace `_nav_config_for_user` so non-admins omit every admin-only group by config, not by the literal string `"Admin"`:

   ```python
   def _nav_config_for_user(candidate_state: str, candidate_id: Optional[str]) -> list:
       nav = _resolve_nav(candidate_state, candidate_id)
       if g.user.get("is_admin"):
           return nav
       admin_labels = nav_admin_only_group_labels()
       return [group for group in nav if group.get("label") not in admin_labels]
   ```

   Do not change `_resolve_nav` (it must continue to emit only `label` + `items` (+ optional `count` / `enabled` on items) — do **not** pass `admin_only` through to the JSON response). Do not change `nav_config` route auth, candidate_state resolution, or badge count helpers.

6. Do **not** edit `src/ui/frontend/src/components/NavigationShell.tsx`, `App.css`, `routes.tsx`, any `Admin*.tsx` page, `AdminRoute`, or auth helpers. Shell expand/collapse already keys off group `label` strings from the API; new group labels appear automatically.

7. Do **not** edit `tests/` or the test bible. Existing component tests that assert a single Admin group or `label != "Admin"` for non-admins will need Betty’s qa-child pass after Code Complete.

## Estimate

Confirm Chuckles estimate: 3 — agree
