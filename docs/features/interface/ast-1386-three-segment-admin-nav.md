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

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1386
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1370/AST-1386-three-segment-admin-nav` @ `08df6c51`

## Traceability
AC1–AC5 → Stage 1 (`NAV_CONFIG` three-segment regroup with paste labels; `admin_only` + `nav_admin_only_group_labels()`; `_nav_config_for_user` config-driven omit; explicit no-touch on shell, routes, pages, auth, and non-admin candidate groups)

## Findings

### discuss — Stage 1 step 1 (NAV_CONFIG header comment)
**Location:** Plan Stage 1 step 1  
**Finding:** Step 1 says the block “immediately above `NAV_CONFIG = [`” documents `visible` / `enabled`, but in the current tree those paragraphs live earlier (~4515–4519); the preamble directly above the array (~4615–4621) is SYNC / endpoint prose only.  
**Recommendation:** Point implementers at the existing `visible` / `enabled` comment block (~4515), not the SYNC preamble — cosmetic doc placement only; no product risk.

context_tokens≈42000

## Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-1370/AST-1386-three-segment-admin-nav`
**Product commits:** `6f6cc620` (NAV_CONFIG Operations/Admin/Tools + `nav_admin_only_group_labels`; `_nav_config_for_user` config-driven omit)


## Radia review — AST-1386

`[code-rubric] revision=2`
**Rubric:** code-rubric.v2  
**Ticket:** AST-1386  
**Publish ref:** `origin/sub/AST-1370/AST-1386-three-segment-admin-nav` @ `34a3307e`  
**Overall:** CLEAN

**Diff baseline:** `origin/dev...origin/sub/AST-1370/AST-1386-three-segment-admin-nav` (8 files, +318/−29). Product commit `6f6cc620` touches only `src/utils/config.py` + `src/ui/api/api_system.py`; Betty merge `92733b1d` lands tests + bible.

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | no `core` layer in diff |
| astral.agent.do-task-delegation | scoped | not-applicable | no `core` layer in diff |
| astral.agent.grade-vector-validation | scoped | not-applicable | no `core` layer in diff |
| astral.batch.batch-id-first | scoped | not-applicable | no `core`/`data` in diff |
| astral.batch.batch-id-format | scoped | not-applicable | no `core`/`data` in diff |
| astral.batch.claim-process-release | scoped | not-applicable | no `core`/`data` in diff |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | no `core`/`data` in diff |
| astral.config.config-source-of-truth | scoped | conforms | NAV_CONFIG + helper stay centralized in config.py |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | no secrets/env lookups added |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | hook paths unchanged |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | hook paths unchanged |
| astral.dispatch.seed-auto-false | scoped | not-applicable | no dispatch layer in diff |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | no dispatch layer in diff |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single issue doc on publish tip |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty owns test/bible edits on merge |
| astral.git.engineer-test-tree-ban | scoped | conforms | engineer commit `6f6cc620` is src-only |
| astral.layers.core-vs-external-bright-line | scoped | conforms | utils/ui only; no layer bleed |
| astral.layers.import-direction | scoped | conforms | api_system imports utils.config only |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no `scripts/**` in diff |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | admin nav resolved server-side from NAV_CONFIG |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | no `core` in diff |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | no `core` in diff |
| astral.idioms.require-auth-on-protected-endpoints | scoped | conforms | `/api/nav_config` still `@require_auth`; route untouched |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | no seed/boot paths |
| astral.seed.archie-catalog-wins | scoped | not-applicable | no seed paths |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | no seed paths |
| astral.seed.define-approved | scoped | not-applicable | no seed paths |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | no seed paths |
| astral.seed.other-via-coverage-join | scoped | not-applicable | no seed paths |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | no `data` layer |
| astral.standards.database-header-inventory | scoped | not-applicable | no DB/migrations |
| astral.standards.debug-contract-gated | scoped | not-applicable | no debug emission |
| astral.standards.dry-and-focused-functions | scoped | conforms | small focused helper; no duplication |
| astral.standards.in-scope-only | scoped | conforms | no shell/React/routes/pages touched |
| astral.standards.logging-via-utils | scoped | not-applicable | no logging changes |
| astral.standards.names-not-ticket-ids | scoped | conforms | descriptive `nav_admin_only_group_labels()` |
| astral.standards.no-cross-contamination | scoped | conforms | nav-only change set |
| astral.standards.no-hardcoded-sets | scoped | conforms | replaced literal `"Admin"` omit with config-derived labels |
| astral.standards.public-then-helpers | scoped | conforms | helper follows NAV_CONFIG constant |
| astral.standards.utils-data-late-import-only | scoped | conforms | no new utils→data imports |
| astral.state.core-decides-transitions | scoped | not-applicable | no state machine changes |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no state machine changes |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no dispatch/run changes |
| astral.ui.frontend-file-placement | scoped | not-applicable | no `src/ui/frontend/**` |
| astral.ui.naming-conventions | scoped | not-applicable | no frontend source files |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no worker/deploy changes |
| orch.git.betty-merge-tests-one-sha | universal | conforms | `merge-tests(AST-1386)` at publish tip |
| orch.git.commit-vocabulary | universal | conforms | `code` / `docs` / `merge-tests` vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | sub branch; no reverse flow |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1370/AST-1386-…` |
| orch.git.merge-on-checkout | universal | conforms | no checkout violation in diff |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | clean three-dot range |
| orch.git.no-dev-agent-branches | universal | conforms | standard sub topology |
| orch.git.one-epic-worktree-per-parent | universal | conforms | AST-1370 worktree pattern |
| orch.git.three-permanent-branches | universal | conforms | dev/sub/tests only |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | paste labels per parent scope |
| orch.pipeline.plan-is-bible | universal | conforms | implementation matches Stage 1 |
| orch.pipeline.project-scoped-queues | universal | conforms | ticket isolated to nav regroup |
| orch.pipeline.status-gates-skill-entry | universal | conforms | reviewed at Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | no statute edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty revised tests + bible |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Ada remains assignee |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada assignee through review |
| orch.roles.pre-commit-path-bans | universal | conforms | engineer src-only product commit |

**Active corpus:** 64 harvested rows scored (README claims 65; `SCHEMA.md` frontmatter match is harness metadata, not a scored statute).

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| none cited | — | plan cites statutes, not catalog patterns |

## Plan adherence

Stage 1 delivered cleanly against Joan APPROVED plan (`08df6c51`):

- Single Admin `NAV_CONFIG` group → **Operations** / **Admin** / **Tools** with correct membership, order, `admin_only: True`, and paste labels **Resume Paste** / **Cover Letter Paste** (paths unchanged).
- `admin_only` documented in the existing `visible`/`enabled` comment block (~4515) — Joan’s cosmetic placement note is resolved.
- `nav_admin_only_group_labels()` added; `_nav_config_for_user` uses config-driven omit.
- `_resolve_nav` still emits only `label` + `items` (+ item fields); `admin_only` does not leak to JSON (verified in product code + `test_nav_config_three_admin_segments_for_admin`).
- Jobs / Companies / Artifacts / Candidate groups unchanged; no React, routes, pages, shell, or auth edits.
- Estimate **3** matches footprint (config regroup + thin API filter).
- Betty manifest covers three-segment order, paste labels, non-admin omit, and revised AST-1025/AST-1033 anchors.

**Joan straggler:** Joan verdict attached; no Excluded-statute list → no straggler rows.

## Findings

### advisory — stale `nav:expanded` localStorage key
**Location:** `NavigationShell.tsx` (`NAV_STORAGE_KEY` / `loadExpanded`) — unchanged, downstream UX  
**Finding:** Users who previously expanded the monolithic **Admin** group may retain `"Admin"` in `localStorage` while the API now returns **Operations** / **Admin** / **Tools** as separate groups. Expand state may not carry over.  
**Recommendation:** UAT note for Susan — not a code fix for AST-1386.

### advisory — API test duplicates admin label set
**Location:** `tests/component/ui/api/test_api_system.py` — `test_nav_config_omits_admin_group_for_non_admin`  
**Finding:** Hardcodes `{"Operations", "Admin", "Tools"}` while `TestAst1386ThreeSegmentAdminNav` already asserts `nav_admin_only_group_labels()`. Minor drift risk if a fourth `admin_only` group is added later.  
**Recommendation:** Betty optional follow-up — import helper in API test; not blocking.

### advisory — frontend page mock still uses single Admin group
**Location:** `tests/component/frontend/pages/test_AdminAgentTimesheets.test.tsx` (~203)  
**Finding:** Nav mock is still one **Admin** group; sufficient for click-away test but no longer mirrors live three-segment shape.  
**Recommendation:** Betty optional realism refresh on a future pass; not blocking.

## What’s solid

- Config-driven omit replaces the brittle `label != "Admin"` filter — exactly the `no-hardcoded-sets` / `config-source-of-truth` intent from the plan.
- Layer hygiene: UI API imports one new utils helper; no frontend business-logic duplication.
- Test + bible coverage aligns with manifest; engineer stayed out of the test tree on the product commit.

## Frame diff

- **Before:** One trailing **Admin** nav group; non-admins filtered by literal `"Admin"` label.
- **After:** Three trailing admin-only groups (**Operations** → **Admin** → **Tools**); non-admins filtered via `nav_admin_only_group_labels()`; paste nav labels renamed; all admin paths preserved; shell renders API groups unchanged.

## Notes

- `no plan-rubric Excluded list` in Joan attachment — straggler check N/A.
- Parent AST-1370 may have sibling tickets for shell chrome / visual grouping; this child correctly limits to config + API filter per plan.

**C7:** Complete — recommend **Review Posted** → User Testing (PROCEED path).

context_tokens≈55000
