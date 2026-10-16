# AST-2230 — Stage-gated nav regroup

- **Linear:** [AST-2230](https://linear.app/astralcareermatch/issue/AST-2230)
- **Parent:** [AST-2225](https://linear.app/astralcareermatch/issue/AST-2225) — Revise candidate ui and candidate states
- **Publish ref:** `origin/sub/AST-2225/AST-2230-stage-gated-nav`

After AST-2228’s stage vocabulary, restructure candidate-facing `NAV_CONFIG` into stage-gated groups (Candidate / Criteria / Company / Job Opportunities), drop unlisted items, rename labels only (paths stay), drive item `enabled` from registry stage, attach recent-expand + Profile attention flags on `/api/nav_config`, and SYNC `routes.tsx` + the Jobs home redirect group-label constant — so the shell (#4) can render a progressive menu without owning the config map.

## Explicit scope gate

Ticket **## Scope** names only:

- `src/utils/config.py` — `NAV_CONFIG` + recent-expand defaults (**not** `CANDIDATE_STATES` vocabulary)
- `src/ui/api/api_system.py` — stage gates + attention/recent flags + admin/non-admin nav contract
- `src/ui/frontend/src/routes.tsx` — SYNC with remaining `NAV_CONFIG` paths/labels
- `src/ui/frontend/src/components/JobsHomeRedirect.tsx` — group-label constant Jobs → Job Opportunities only
- `src/core/candidate.py` — `_artifacts_nav_label_for_path` / craft hop label walk only (stop filtering by dissolved Artifacts group; **not** vocabulary or readiness)

Every Files Changed row and every stage step below stays inside that list. No `NavigationShell.tsx` / `App.css` (#4), no readiness/advance (#2), no `CANDIDATE_STATES` stage bands (#1).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Rewrite candidate-facing `NAV_CONFIG` groups/items; item `enabled` = min stage int; drop unlisted items; label renames; `NAV_GROUP_RECENT_DEFAULTS` (or equivalent) per-group recent rules; update header comments | utils |
| `src/ui/api/api_system.py` | Resolve `enabled` via `candidate_stage` vs min stage; stage-0 omit candidate-facing groups; attach group `recent` + Profile `attention`; keep admin_only filter + badge counts for remaining paths | ui |
| `src/ui/frontend/src/routes.tsx` | SYNC comments + page `title` props for renamed Job Opportunities labels; mark dropped sidebar paths deeplink-only (routes stay) | ui |
| `src/ui/frontend/src/components/JobsHomeRedirect.tsx` | `JOBS_NAV_GROUP_LABEL = "Job Opportunities"` only | ui |
| `src/core/candidate.py` | `_artifacts_nav_label_for_path`: walk every `NAV_CONFIG` group for path→label (no `label == "Artifacts"` filter) | core |

## Canon (this ticket)

Read in full (named on the ticket):

- `astral.dispatch.entity-state-bound` → `canon/directives/active/stat.dispatch.entity-state-bound.md` — nav may gate UI on stage integers; do **not** invent stage-integer `trigger_state`s or dispatch claims.
- `stat.logging.info.api` → `canon/directives/active/stat.logging.info.api.md` — `GET /api/nav_config` is idempotent state return → **no** progress `logger.info`.

All other ids: id-only.

## Prerequisite (build, not this ticket’s Scope)

- **AST-2228 on tip:** `candidate_stage`, every live `CANDIDATE_STATES` entry has `"stage"`, `PROFILE_READY` / `CONTEXT_READY` registered. `from src.utils.config import CANDIDATE_STATES` must succeed.
- **If import asserts fail** (e.g. a resume-chain `ERROR_*` missing `"stage"` after `origin/dev` merge): that is **#1 vocabulary** — stop and comment on **AST-2225** / AST-2228; **do not** edit `CANDIDATE_STATES` stage keys under AST-2230.
- **AST-2229 `incomplete_profile`:** preferred on tip for Profile `attention`. If the symbol is missing at build, set `attention: false` always and do **not** reimplement profile completeness in `api_system.py` (still #2’s function). Leave a one-line Linear comment on AST-2230 noting the soft dependency.

## Locked nav map (paths stay; labels + min stage)

Order of **groups** and **items** must match exactly (AC 5–7 + parent brief).

**Candidate**

| Label | Path | Min stage |
|-------|------|-----------|
| Profile | `/candidate/profile` | 1 |
| Bio Summary | `/candidate/bio_summary` | 2 |
| Back Story | `/candidate/backstory` | 2 |
| Ideal Day | `/candidate/ideal_day` | 2 |
| Strengths | `/candidate/strengths` | 2 |
| Priorities | `/candidate/priorities` | 2 |
| Dealbreakers | `/candidate/deal_breakers` | 2 |
| Writing Preferences | `/candidate/writing_preferences` | 2 |
| Base Resume | `/artifacts/base_resume_content` | 3 |

**Criteria** (all min stage 4 — AC 7)

| Label | Path | Min stage |
|-------|------|-----------|
| Job Listing Qualify Criteria | `/artifacts/job_list_criteria` | 4 |
| Meteorite Qualify Criteria | `/artifacts/meteorite_criteria` | 4 |
| Job Description Criteria | `/artifacts/job_description_criteria` | 4 |
| Do the Job Criteria | `/artifacts/do_job_criteria` | 4 |
| Get the Job Criteria | `/artifacts/get_job_criteria` | 4 |
| Like the Job Criteria | `/artifacts/like_job_criteria` | 4 |

**Company**

| Label | Path | Min stage |
|-------|------|-----------|
| Company Discovery Terms | `/artifacts/company_search_terms` | 4 |
| Company Gazing Criteria | `/artifacts/company_watch_criteria` | 4 |
| Gaze Roster | `/companies/watch_list` | 5 |
| Ignore List | `/companies/ignored` | 5 |

**Job Opportunities**

| Label | Path | Min stage |
|-------|------|-----------|
| Meteorites | `/jobs/meteorites` | 5 |
| Recommendations | `/jobs/review` | 5 |
| Ready to Apply | `/jobs/ready` | 5 |
| Submitted Applications | `/jobs/applied` | 5 |
| Skipped | `/jobs/skipped` | 5 |

**Drop from candidate-facing nav** (AC 6 — labels must not appear for non-admin): Intake, Surfer, Surfer Consent, Watch History, New List, Inactive List, Processing, Review, plus any other current item not in the tables above (e.g. Companies → Meteorite list). Admin-only groups (Operations / Admin / Tools) unchanged and still omitted for non-admins.

## Stage 1: `NAV_CONFIG` + recent-expand defaults (`config.py`)

**Done when:** Non-admin-facing group labels in `NAV_CONFIG` are exactly Candidate, Criteria, Company, Job Opportunities in that order; every remaining item matches the locked map (label, path, min-stage `enabled`); dropped labels absent; admin groups untouched; a config block defines per-group recent defaults readable by `api_system`.

1. In `src/utils/config.py`, replace the four candidate-facing `NAV_CONFIG` groups (Jobs / Companies / Artifacts / Candidate) with the four groups in **Locked nav map**, in that order. Keep Operations / Admin / Tools blocks byte-stable aside from any comment that still describes the old four-group world.
2. For each item, set `"enabled"` to the **integer** min stage from the map (not a `CANDIDATE_STATES` key string, not `False` stubs). Omit `"enabled"` only if the item is always on — there are no always-on candidate-facing items in this map; every row has a floor.
3. Update the `NAV_CONFIG` header comments: item-level `"enabled"` is a minimum **stage** int (or legacy `False` stub); resolution is in `api_system.py` via `candidate_stage`. Remove wording that says enabled gates are `CANDIDATE_STATES` keys / progress_rank.
4. Add a sibling config dict immediately above or below `NAV_CONFIG`, name **`NAV_GROUP_RECENT_DEFAULTS`**, keyed by group label:

   ```python
   NAV_GROUP_RECENT_DEFAULTS = {
       "Candidate": {"when": "incomplete_profile"},
       "Criteria": {"when": "never"},
       "Company": {"when": "any_item_count"},
       "Job Opportunities": {"when": "any_item_count"},
   }
   ```

   ⚠️ **Decision:** Defaults match parent Functional scope examples (Candidate when Profile incomplete; Company / Job Opportunities when any item badge count > 0; Criteria never auto-recent). Admin groups are omitted from this dict (never auto-expanded by this API). Shell (#4) still owns collapse chrome; this ticket only defines knobs + API `recent` flags.
5. Do **not** edit `CANDIDATE_STATES`, `SEARCH_ENTITY_CONFIG` labels, or `CRAFT_ARTIFACTS_CHAIN_TASK_TO_NAV_PATH` (paths unchanged).

## Stage 2: `/api/nav_config` stage gates + flags (`api_system.py`)

**Done when:** Non-admin payload group labels are exactly the four names in order (AC 5); dropped labels absent (AC 6); at candidate stage &lt; 4 every Criteria item is present with `"enabled": false` (AC 7); each returned candidate-facing group carries boolean `"recent"` per config; Profile item carries boolean `"attention"`; stage 0 omits the four candidate-facing groups; admin_only filter unchanged; GET emits no progress info log.

1. Import `candidate_stage` from `src.core.candidate`. Import `NAV_GROUP_RECENT_DEFAULTS` from config. Prefer `from src.core.candidate import incomplete_profile` when the symbol exists (see Prerequisite soft-dep).
2. Replace `_progress_rank` / `_is_at_or_past` usage inside `_resolve_nav` (and delete those helpers if nothing else in this file calls them) with stage compare:

   - Resolve `stage = candidate_stage(candidate_state)` when `candidate_state` is non-empty and registered; on empty/unknown state treat stage as **0** (no usable candidate-facing menu).
   - For each item: if `enabled` is `False` → disabled; if `enabled` is `int` → `enabled_flag = stage >= enabled`; if key omitted → `True` (admin stubs only).
3. **Stage 0:** when `stage == 0`, do not append Candidate / Criteria / Company / Job Opportunities groups to the resolved list (admin groups still resolved for admins). ⚠️ **Decision:** Omit groups rather than emit all-disabled — matches brief “unless DELETED or INACTIVE” and leaves #4’s stage-0 chrome as defense in depth if an empty list reaches the shell.
4. Preserve badge `count` attachment for paths still present (`_get_company_counts` / `_get_job_counts`). It is fine if those helpers still compute counts for dropped paths — unused keys are ignored. Do not expand Scope to delete dead count keys unless a one-liner is free; prefer leave helpers alone.
5. After building each candidate-facing group’s items, set `group["recent"]` from `NAV_GROUP_RECENT_DEFAULTS[label]["when"]`:

   | `when` | `recent` true when |
   |--------|-------------------|
   | `incomplete_profile` | `incomplete_profile(candidate_id)` is True (else False if symbol/candidate missing) |
   | `any_item_count` | any item in that group has `count` present and `count > 0` |
   | `never` | always False |

6. On the Profile item only (`path == "/candidate/profile"`), set `"attention": bool` to the same incomplete-profile signal (False when soft-dep missing). Do not add `attention` to other items.
7. Keep `_nav_config_for_user` admin_only filtering via `nav_admin_only_group_labels()` unchanged in behavior (labels still drawn from `admin_only: True` groups).
8. Keep response shape a **JSON array of groups** (extra keys on groups/items are additive). Do **not** wrap in `{groups: ...}` — `JobsHomeRedirect` and current shell parse an array.
9. Do **not** add `logger.info` on `GET /nav_config` (`stat.logging.info.api`).
10. Do **not** change dispatch, claim helpers, or any `trigger_state` (`astral.dispatch.entity-state-bound`).

## Stage 3: routes SYNC + home redirect + hop-label walk

**Done when:** `routes.tsx` titles/comments match remaining nav labels; dropped sidebar routes are documented deeplink-only; home redirect looks up Job Opportunities; craft hop labels resolve paths under Criteria/Company/Candidate without requiring an Artifacts group.

1. In `src/ui/frontend/src/routes.tsx`:
   - Update the SYNC header comment: every **sidebar** path must match `NAV_CONFIG`; paths removed from nav (Intake, Surfer, Processing, New List, …) remain as **deeplink-only** routes (same pattern as `search` / `jobs/detail/:jobId`) — do **not** delete those route entries.
   - Update Job Opportunities page `title` props to the new labels: Ready → `Ready to Apply`, Review → `Recommendations` (paths unchanged). Leave component imports as-is.
2. In `src/ui/frontend/src/components/JobsHomeRedirect.tsx`, change only:

   ```ts
   const JOBS_NAV_GROUP_LABEL = "Job Opportunities"
   ```

   Update the adjacent comment to name Job Opportunities. No other logic changes.
3. In `src/core/candidate.py`, edit `_artifacts_nav_label_for_path` so it walks **every** `NAV_CONFIG` section’s items for a matching `path` and returns that item’s `label`. Remove the `section.get("label") != "Artifacts"` continue. Docstring: path→label across all nav groups (Artifacts group dissolved). Do not change `requested_artifacts_chain_hop_labels` beyond what the helper fix implies. Do not touch `candidate_stage`, migration, or readiness symbols.

## Execution contract

- Stages 1–3 in order; one product commit per stage on the epic worktree; publish each to `origin/sub/AST-2225/AST-2230-stage-gated-nav`.
- Do not add files outside **Files Changed**. Do not touch `tests/` / bible (Betty).
- When a step is ambiguous or the tip lacks #1 stage vocabulary → stop, comment on parent AST-2225 (vocabulary) or AST-2230 (this plan), wait.

## Estimate

Confirm Chuckles estimate: 3 — agree
