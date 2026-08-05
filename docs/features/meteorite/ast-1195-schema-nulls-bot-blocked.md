# AST-1195 — Schema nulls + BOT_BLOCKED replaces JD_SCRAPE_FAIL_BOT

**Linear:** [AST-1195](https://linear.app/astralcareermatch/issue/AST-1195/schema-nulls-bot-blocked-replaces-jd-scrape-fail-bot-errors-for)
**Parent:** [AST-1188](https://linear.app/astralcareermatch/issue/AST-1188/errors-for-qualify-meteorite-dispatch-task) — Errors for qualify_meteorite dispatch task
**Publish ref:** `origin/sub/AST-1188/AST-1195-schema-nulls-bot-blocked`

Allow null/omit `job_link` / `job_title` on the `qualify_meteorite` response schema so one weak Ruth row cannot abort `do_task` for the whole chunk, and rename job state `JD_SCRAPE_FAIL_BOT` → **`BOT_BLOCKED`** everywhere that state id is consumed (registry, gazer error map, skipped UI manifests). Does **not** own `agent_task` prompt text (AST-1196) or consult assemble/apply / Style D (AST-1197).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `qualify_meteorite` schema: `job_link` / `job_title` → `required: False`; rename `JD_SCRAPE_FAIL_BOT` → `BOT_BLOCKED` in `JOB_STATES`, `GAZER_CONFIG`, `SKIPPED_STATES`, skipped UI order/bulk-retry; expand `BOT_BLOCKED` priors for meteorite entry | utils |
| `src/core/gazer.py` | `_JD_ERROR_STATES["bot"]` → `"BOT_BLOCKED"` | core |

No `consult.py` apply, no `agent_task` / `data/admin` prompt edits, no frontend TS (manifest is config-driven), no `tests/` / bible (Betty after Code Complete).

## Stage 1: Schema — null/omit `job_link` / `job_title` on `qualify_meteorite`

**Done when:** Importing `config` succeeds; `_validate_response_schema` accepts a `qualify_meteorite` payload where a jobs item omits or nulls `job_link` and/or `job_title` (other required fields present); a jobs item that still omits a still-required field (e.g. `astral_job_id` or `jd_text`) still fails validation. No product apply logic changes.

1. In `src/utils/config.py` `TASK_CONFIG["qualify_meteorite"]["response_schema"]["jobs"]["items_schema"]`, change:

```python
"job_title":       {"type": "str", "required": False},  # AST-1195: omit/null must not abort do_task
"job_link":        {"type": "str", "required": False},  # AST-1195: omit/null must not abort do_task
```

Keep `astral_job_id` and `jd_text` **`required: True`**. Keep `company_job_id` **`required: False`** (AST-1127 unchanged).

2. Immediately after the existing module-level assert on `company_job_id` required False (near the end of `TASK_CONFIG`), add matching asserts:

```python
assert TASK_CONFIG["qualify_meteorite"]["response_schema"]["jobs"]["items_schema"]["job_link"]["required"] is False
assert TASK_CONFIG["qualify_meteorite"]["response_schema"]["jobs"]["items_schema"]["job_title"]["required"] is False
```

⚠️ **Decision — schema only, apply stays sibling:** Null/omit must pass `_validate_response_schema` so `do_task` does not batch-ERROR the chunk. Per-row QUALIFY / FAIL / BOT / synthesize rules remain AST-1197 (`consult` apply) and AST-1196 (`agent_task` instructions). This stage does not teach Ruth to synthesize links or change transitions.

## Stage 2: Universal `JD_SCRAPE_FAIL_BOT` → `BOT_BLOCKED`

**Done when:** `rg JD_SCRAPE_FAIL_BOT src/` returns no matches; `BOT_BLOCKED` is a `JOB_STATES` key enterable from `PASSED_JOBLIST` and `METEORITE_NEW`; gazer bot classification targets `BOT_BLOCKED`; Jobs Skipped section order + bulk-retry map include `BOT_BLOCKED` and not `JD_SCRAPE_FAIL_BOT`. (Do **not** treat `build_state_ui_manifest()` import asserts as a rename guard — those asserts do not cover skipped-order / bulk-retry completeness, and `skipped_order` filters with `if s in JOB_STATES`, so a half-finished rename silently drops the section.)

1. In `src/utils/config.py` `JOB_STATES`:

- Replace the key `"JD_SCRAPE_FAIL_BOT"` with `"BOT_BLOCKED"`.
- Set `"BOT_BLOCKED": {"prior_states": ["PASSED_JOBLIST", "METEORITE_NEW"]}`.
- In `"PASSED_JOBLIST"` `prior_states`, replace the string `"JD_SCRAPE_FAIL_BOT"` with `"BOT_BLOCKED"` (same list position among the other `JD_SCRAPE_FAIL_*` siblings).

⚠️ **Decision — dual prior for universal bot state:** Parent requires one human-facing bot state for roster scrape **and** meteorite qualify challenge pages. `PASSED_JOBLIST` preserves gazer `fetch_jd` entry; `METEORITE_NEW` lets AST-1197 transition challenge JD bodies without inventing a meteorite-only bot state.

2. In `GAZER_CONFIG["fetch_jd"]["error_states"]`, replace `"JD_SCRAPE_FAIL_BOT"` with `"BOT_BLOCKED"` (keep cookie/missing/closed ids unchanged).

3. In `SKIPPED_STATES`, replace `"JD_SCRAPE_FAIL_BOT"` with `"BOT_BLOCKED"`.

4. In `JOBS_SKIPPED_SECTION_ORDER`, replace `"JD_SCRAPE_FAIL_BOT"` with `"BOT_BLOCKED"` (same position in the scrape-fail cluster).

5. In `JOBS_SKIPPED_BULK_RETRY_TO_STATE`, replace the key `"JD_SCRAPE_FAIL_BOT"` with `"BOT_BLOCKED"`, value still `"PASSED_JOBLIST"`.

⚠️ **Decision — bulk-retry target stays `PASSED_JOBLIST` (and state-prefix identity is lost):** Preserves existing roster scrape retry. A single static map cannot dual-target `METEORITE_NEW` for meteorite-origin rows; context-aware skipped retry is out of scope for this child (parent AC is rename + registry/UI, not dual-origin retry). Additionally, `consult._entity_state_is_meteorite` keys on `state.startswith("METEORITE_")` — once a meteorite job lands on `BOT_BLOCKED`, that prefix test is false by design (universal id, not a meteorite-only bot state). Automated exit from Jobs Skipped is then bulk-retry → `PASSED_JOBLIST` (roster track), not meteorite re-qualify; company-based `is_meteorite_company` can still recover identity for a future return path, but that path is a new ticket if Archie wants it at UAT — not a widening of this child.

6. In `src/core/gazer.py` `_JD_ERROR_STATES`, set `"bot": "BOT_BLOCKED"`. Update the adjacent comment so it no longer implies every value is still named `JD_SCRAPE_FAIL_*` (bot is now `BOT_BLOCKED`; cookie/missing/closed stay `JD_SCRAPE_FAIL_*`).

7. Verify with a workspace search that **no** remaining `JD_SCRAPE_FAIL_BOT` string exists under `src/`. Do **not** edit `tests/`, `docs/test-bible/**`, or historical plan docs under `docs/features/**` that mention the old id (Betty / history). Do **not** add a DB row rewrite for jobs already stored as `JD_SCRAPE_FAIL_BOT`. Do **not** add an explicit `JOBS_SKIPPED_SECTION_LABELS["BOT_BLOCKED"]` entry — `build_state_ui_manifest` already falls back to `s.replace("_", " ").title()` → `"Bot Blocked"`, matching scrape-fail siblings that omit the label dict.

⚠️ **Decision — no live-row migration:** Product stores job `state` as a free string. This child renames the registry and all `src/` consumers; it does not ship an `UPDATE jobs SET state=…` migration. If staging still has rows on the old id, they fall out of `SKIPPED_STATES` (invisible in Jobs Skipped, not mislabeled) until manually/ops-remapped — call out on Linear if that appears during UAT.

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; publish each to `origin/sub/AST-1188/AST-1195-schema-nulls-bot-blocked`.
- Do not edit `consult.py` apply, `data/admin/agent_task.json`, frontend TS, or `tests/`.
- If a step is ambiguous or the codebase has drifted — stop and comment on **parent** AST-1188 with the standard blocked format.

## Revisions

Revision 1 — 2026-08-05
Driven by: Joan `[plan-rubric] revision=1` discuss findings 1–3 (APPROVED tip `c7d40ad5`)
Changes: Expanded bulk-retry Decision with `startswith("METEORITE_")` identity loss; dropped no-op `JOBS_SKIPPED_SECTION_LABELS` step; Done-when leans on `rg` gate, not import asserts.

## Self-Assessment

**Scope:** `Single-Component` — config schema + job-state registry/UI manifests in `config.py`, plus one gazer error-map string in `gazer.py`.

**Conf:** `high` — mirrors AST-1127 `required: False` schema pattern and a straight string rename across known `src/` consumers.

**Risk:** `Medium` — wrong prior_states or a missed consumer would strand bot-blocked jobs or leave `JD_SCRAPE_FAIL_BOT` as a dead id; does not rewrite consult apply.

## Code-rules check

- §1.3 DRY / focused: rename in place; no new helpers.
- §1.4 / `astral.standards.no-hardcoded-sets`: state id lives in `JOB_STATES` / config lists; gazer map points at the config state name.
- §2.1 / `astral.config.config-source-of-truth`: schema knobs and state registry stay in `config.py`.
- §2.6 / `astral.state.job-prior-states-enforced`: `BOT_BLOCKED` priors list both legal entry states; `PASSED_JOBLIST` re-entry list updated.
- §3.3 imports: no new cross-layer imports.
- Out of scope here: `astral.standards.debug-contract-gated` (AST-1197), agent_task authoring (AST-1196).

## Review (build stub)

**Publish ref:** `origin/sub/AST-1188/AST-1195-schema-nulls-bot-blocked`
**Plan path:** `docs/features/meteorite/ast-1195-schema-nulls-bot-blocked.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `1986578e` | `qualify_meteorite` schema: `job_link` / `job_title` `required: False` + asserts |
| 2 | `1db73b8b` | `JD_SCRAPE_FAIL_BOT` → `BOT_BLOCKED` in config registry/UI + gazer map |

**Tip:** `e01bafce9a74cdf3d7226800070de09db8084140` on `origin/sub/AST-1188/AST-1195-schema-nulls-bot-blocked`

### code-rubric.v1 verdict

[code-rubric] revision=1

**Rubric:** code-rubric.v1
**Ticket:** AST-1195
**Publish ref:** `1e2e0539` (`origin/sub/AST-1188/AST-1195-schema-nulls-bot-blocked`)
**Overall:** CLEAN

Full active corpus (65 leaves — 18 universal + 47 scoped) swept in-session against this ticket's own footprint: `git diff origin/ftr/AST-1188-errors-for-qualify-meteorite-dispatch-task...origin/sub/AST-1188/AST-1195-schema-nulls-bot-blocked` (diff layers `{core, utils, docs}`; paths `src/core/gazer.py`, `src/utils/config.py`, `docs/features/meteorite/ast-1195-schema-nulls-bot-blocked.md`, `docs/test-bible/{core/gazer.md, frontend/pages.md, utils/config.md}`, `tests/component/{core/test_gazer.py, frontend/fixtures/stateUiManifestFixture.ts, utils/test_config.py}`; change_types `{add, modify}`). 6 scoped statutes score `not-applicable` on this footprint (no `src/ui/**`, `src/data/**`, `scripts/**`, or `artifacts/**` paths touched — `astral.ui.frontend-file-placement`, `astral.ui.naming-conventions`, `astral.patterns.require-auth-on-protected-endpoints`, `astral.standards.database-header-inventory`, `astral.layers.scripts-exempt-from-layer-rules`, `astral.debug.no-repo-root-artifacts-dir`); the remaining 41 scoped + all 18 universal score `conforms`. No violations, no stragglers.

## Plan adherence

Matches the plan's two-file Files Changed table exactly: `config.py` (`qualify_meteorite` schema `job_link`/`job_title` → `required: False` + asserts; universal `JD_SCRAPE_FAIL_BOT` → `BOT_BLOCKED` across `JOB_STATES`, `GAZER_CONFIG`, `SKIPPED_STATES`, skipped section order + bulk-retry) and `gazer.py` (`_JD_ERROR_STATES["bot"]`). `rg JD_SCRAPE_FAIL_BOT src/` returns zero hits at the sub tip — Stage 2's real Done-when gate (not the import-assert language Joan flagged as a false safety net) passes. `BOT_BLOCKED` priors are exactly `[PASSED_JOBLIST, METEORITE_NEW]`, matching the meteorite claim state Joan verified against. Her three plan-time `discuss` findings — bulk-retry prefix-loss disclosure, the no-op `JOBS_SKIPPED_SECTION_LABELS` step, and the overstated import-assert safety net — are all visibly resolved in the plan's Revision 1, not just claimed as resolved.

**Pattern conformance:** `astral.config.config-source-of-truth`, `astral.state.job-prior-states-enforced`, `astral.standards.no-hardcoded-sets`, `astral.agent.do-task-delegation` (cited In scope) all `conforms` via the full sweep. `astral.standards.debug-contract-gated` / `astral.state.core-decides-transitions` (cited Considered but excluded) also score `conforms` here — untouched by this diff, correctly deferred to AST-1197 / AST-1196. **Advisory (not fix-now/discuss):** the ticket description's `pattern.config.config-block` and `pattern.batch.entity-claim-process-release` aren't ids in the active corpus — there is no `pattern.*` namespace, only `astral.*` / `orch.*`; likely meant `astral.config.config-source-of-truth` and `astral.batch.claim-process-release`. Citation slip only, not a code issue.

**Cross-ticket note (not a finding):** this branch inherited `test(AST-1189)` / `test(AST-1190)` / `test(AST-1192)` / `test(AST-1193)` via `merge-tests` — none of those siblings' `src/` changes land here, only their test-bible/test-tree lineage (same stacked-sibling pattern already disclosed on AST-1193's own review).

**What's solid:** coverage lands exactly on the schema + registry surface — `TestAst1195SchemaNullsAndBotBlocked` exercises the omit/null path through `_validate_response_schema` directly (not just the schema flags) and pins the manifest's title-case fallback label (`"Bot Blocked"`) byte-for-byte, closing the loop Joan's discuss #2 raised at plan time.

## Frame diff

(none) — implementation matches the plan doc's Files Changed / Stage 1 / Stage 2 as written; no adds or moves applied to this description.

context_tokens≈95000

— Radia
