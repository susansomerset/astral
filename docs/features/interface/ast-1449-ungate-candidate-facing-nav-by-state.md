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

## Joan validate

[plan-rubric]
revision: 1
**Rubric:** plan-rubric
**Ticket:** AST-1449
**Overall:** APPROVED
**Publish-ref tip:** `1e9e21b5b93bfb9d62cf144f4d6ef076cafc6470`

## Traceability
AC1–5 → Stage 1 (drop Jobs/Companies/Artifacts `"visible"`; delete `_resolve_nav` group skip; keep Applied/Responded `"enabled": False` and `_nav_config_for_user` admin omit; Code Rules §2.1 NAV_CONFIG bullet rewritten). Parent chrome ACs → N/A — “Does not own the read-only candidate-state line under the picker (sibling #2).”

## Findings
- **acceptable** — Stage 1 Decision: with no `candidate_id`, candidate-facing groups will still appear (old `visible` skip used `candidate_state=""`). Parent AC is selected-candidate membership; the plan does not invent a new empty-selection hide.

R1–R5 pass. Definition fidelity holds: group-level state hide gone, stubs and admin omit stay, enablement stays in `/api/nav_config`, no React hide, no chrome line. `pattern.config.config-block` + `astral.config.config-source-of-truth` / `astral.layers.ui-config-driven-business-logic` / `astral.standards.no-hardcoded-sets` match (edit NAV_CONFIG + resolver; no React allowlist). Estimate 3 — agree is honest.

context_tokens≈42000

## Radia review

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1449
**Publish ref:** `96253abf5430ebef404f3998a3c6ba38d7573791` (`origin/sub/AST-1444/AST-1449-ungate-candidate-facing-nav-by-state`)
**Overall:** CLEAN

### Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | Betty `merge-tests` on publish ref; component + integration deltas on sub tip |
| `orch.git.commit-vocabulary` | universal | conforms | `code` / `docs` / `test` / `merge-tests` vocabulary on sub history |
| `orch.git.flow-direction-inviolable` | universal | conforms | Product on `sub/*`; tests via Betty merge onto same publish ref |
| `orch.git.ftr-sub-topology` | universal | conforms | Child work on `sub/AST-1444/AST-1449-…` |
| `orch.git.merge-on-checkout` | universal | conforms | `origin/dev` merged before product land; no rebase onto dev |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | No cherry-pick / force-push pattern on this child |
| `orch.git.no-dev-agent-branches` | universal | conforms | No `ada/` / agent dev branches |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | Epic worktree `astral-AST-1444` |
| `orch.git.three-permanent-branches` | universal | conforms | Sub publish ref only |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | Ungate scope matches parent AST-1444 definition |
| `orch.pipeline.plan-is-bible` | universal | conforms | Stage 1 matches plan Files Changed + boundaries |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Single-child review; no queue bleed |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Spawn at Tests Passed; review-child only |
| `orch.roles.archie-approves-statutes` | universal | conforms | No canon statute edits on diff |
| `orch.roles.betty-owns-test-tree` | universal | conforms | Test/bible revisions on Betty merge-tests SHA |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | Assignee Ada through pipeline |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Engineer product commit; Betty owns test tree |
| `orch.roles.pre-commit-path-bans` | universal | conforms | No banned-path violations on product commit |
| `astral.agent.confidence-bounds` | scoped | not-applicable | no `src/core/**` diff paths |
| `astral.agent.do-task-delegation` | scoped | not-applicable | no `src/core/**` diff paths |
| `astral.agent.grade-vector-validation` | scoped | not-applicable | no `src/core/**` diff paths |
| `astral.batch.batch-id-first` | scoped | not-applicable | no `src/data/**` / batch claim paths |
| `astral.batch.batch-id-format` | scoped | not-applicable | no `src/core/**` / `src/data/**` diff |
| `astral.batch.claim-process-release` | scoped | not-applicable | no batch claim/release paths |
| `astral.batch.entity-agent-responses-latest-only` | scoped | not-applicable | no `src/core/**` / `src/data/**` diff |
| `astral.config.config-source-of-truth` | scoped | conforms | NAV membership change in `NAV_CONFIG`; resolver in API |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | conforms | No new secret/env reads in nav change |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | no `debug/**` / artifacts-dir paths in diff |
| `astral.debug.spikes-under-debug-dir` | scoped | not-applicable | no `debug/**` paths in diff |
| `astral.dispatch.seed-auto-false` | scoped | not-applicable | `dispatcher.py` / seed paths not in diff |
| `astral.dispatch.run-next-is-chain-authority` | scoped | not-applicable | no `src/core/**` diff paths |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | Single `ast-1449-…md` issue doc |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty delta is tests + bible only |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | Engineer product commit excludes `tests/`; Betty owns test merge |
| `astral.layers.core-vs-external-bright-line` | scoped | not-applicable | no `src/core/**` / `src/external/**` diff |
| `astral.layers.import-direction` | scoped | conforms | `api_system.py` imports core + utils only (existing pattern) |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | no `scripts/**` diff paths |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | Group hide removed from config/API; no React nav gates added |
| `astral.idioms.coat-check-never-store-empty` | scoped | not-applicable | no `src/core/**` diff |
| `astral.idioms.render-verdict-orchestrates-consult` | scoped | not-applicable | no `src/core/**` diff |
| `astral.idioms.require-auth-on-protected-endpoints` | scoped | conforms | `/api/nav_config` still `@require_auth` |
| `astral.seed.agent-tables-in-repo-json` | scoped | not-applicable | seed/admin-json paths not in diff |
| `astral.seed.archie-catalog-wins` | scoped | not-applicable | dispatcher/config seed paths not in diff |
| `astral.seed.boot-only-not-hot-path` | scoped | not-applicable | no boot/migration hot-path edits |
| `astral.seed.define-approved` | scoped | not-applicable | no seed invention in diff |
| `astral.seed.operator-rows-stay-deleted` | scoped | not-applicable | no dispatcher/data seed paths |
| `astral.seed.other-via-coverage-join` | scoped | not-applicable | no dispatcher/data seed paths |
| `astral.standards.data-raises-caller-logs` | scoped | conforms | No new data-layer logging |
| `astral.standards.database-header-inventory` | scoped | not-applicable | no `src/data/**` diff |
| `astral.standards.debug-contract-gated` | scoped | conforms | No new debug-contract emission |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | Deletes dead `visible_gate` branch; no sprawl |
| `astral.standards.in-scope-only` | scoped | conforms | NAV_CONFIG + resolver + CODE_RULES only; no React/chrome |
| `astral.standards.logging-via-utils` | scoped | conforms | Existing `get_logger` usage unchanged |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | No ticket-id symbols in product code |
| `astral.standards.no-cross-contamination` | scoped | conforms | Layered imports only |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | State lists stay in `CANDIDATE_STATES`; group `visible` keys removed |
| `astral.standards.public-then-helpers` | scoped | conforms | `_resolve_nav` edit is localized |
| `astral.standards.utils-data-late-import-only` | scoped | not-applicable | no `src/utils/**` late-import pattern change |
| `astral.state.core-decides-transitions` | scoped | not-applicable | no core/data transition edits |
| `astral.state.job-prior-states-enforced` | scoped | not-applicable | no job prior-state paths |
| `astral.state.no-daisy-chain-in-run` | scoped | not-applicable | no `src/core/**` diff |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | no `src/ui/frontend/**` product diff |
| `astral.ui.naming-conventions` | scoped | conforms | No new React routes or misnamed UI files |
| `astral.ui.single-gunicorn-worker` | scoped | conforms | No worker / gunicorn change |

### Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| `pattern.config.config-block` | conforms | NAV membership edited in `NAV_CONFIG`; item `enabled` resolved in `api_system.py`; CODE_RULES §2.1 bullet aligned |

### Plan adherence

Stage 1 landed as specified: Jobs / Companies / Artifacts group `"visible"` keys removed from `NAV_CONFIG`; `_resolve_nav` no longer skips groups on `visible`; docstring updated; Applied / Responded `"enabled": False` preserved; `_nav_config_for_user` admin omit unchanged; `docs/ASTRAL_CODE_RULES.md` §2.1 NAV_CONFIG bullet rewritten. No `NavigationShell.tsx`, routes, or AST-1450 chrome. Betty manifest covers early-state HTTP response, resolver stubs, config `visible` absence, and integration `NEW_CANDIDATE` groups. Estimate **3** still honest.

**Cross-ticket:** No AST-1450 picker-state line or frontend chrome in this publish ref’s product delta.

**Joan straggler:** Plan-rubric attached (APPROVED); no Excluded statute list — no straggler rows.

### Findings

#### advisory

- **Empty `candidate_id` behavior (plan Decision, Joan acceptable):** With no `candidate_id`, `nav_config()` uses `candidate_state=""` and still returns Jobs / Companies / Artifacts / Candidate (counts empty). Parent AC targets *selected* early-state candidates; this is intentional per plan — confirm in UAT if operators ever hit nav without a selection.

#### fix-now

(none)

#### discuss

(none)

### What’s solid

- Group-level state hide fully removed from config and resolver — no dead `visible_gate` path left in `api_system.py`.
- Item-level `enabled` and `admin_only` omit paths unchanged; Applied / Responded remain disabled stubs.
- Config comments + CODE_RULES teach the new contract (“group-level `visible` is not used”).
- Component + integration tests flip from “Jobs absent at NEW_CANDIDATE” to “candidate-facing groups present.”

context_tokens≈52000

## Review (build)

**Built:** `origin/sub/AST-1444/AST-1449-ungate-candidate-facing-nav-by-state` @ `5c7fd0f8f142c596a5e07889d4aa0159bc0d86f3`

Stage 1: dropped Jobs/Companies/Artifacts group `"visible"`; `_resolve_nav` no longer skips groups on that key; Code Rules §2.1 NAV_CONFIG bullet matches. Tests deferred to Betty.
