<!-- linear-archive: AST-1195 archived 2026-08-14 -->

## Linear archive (AST-1195)

**Archived:** 2026-08-14  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1195/schema-nulls-bot-blocked-replaces-jd-scrape-fail-bot-errors-for  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1188 — Errors for qualify_meteorite dispatch task  
**Blocked by / blocks / related:** parent: AST-1188; blocks: AST-1197

### Description

## What this implements

Allow null/omit `job_link`/`job_title` on `qualify_meteorite` schema; rename/replace `JD_SCRAPE_FAIL_BOT` → **BOT_BLOCKED** universally in job state registry + skipped UI labels/sections (all prior consumers of the old id). Does not own Ruth prompt text or consult apply (siblings).

## In scope

- [X] `astral.config.config-source-of-truth` — state id + schema `required` flags live in `TASK_CONFIG` / `JOB_STATES` / `GAZER_CONFIG` (config-block surface)
- [X] `astral.state.job-prior-states-enforced` — `BOT_BLOCKED` priors include `PASSED_JOBLIST` + `METEORITE_NEW`; `PASSED_JOBLIST` re-entry list updated
- [X] `astral.standards.no-hardcoded-sets` — gazer bot map points at registry state name; no inline alternate bot ids
- [X] `astral.agent.do-task-delegation` — schema change only so `do_task` validation does not abort the chunk (no new core→external wiring)

## Considered but excluded

- [X] `astral.standards.debug-contract-gated` — Style D per-job debug is AST-1197 (`consult` apply), not this child
- [X] `astral.batch.claim-process-release` / `astral.state.core-decides-transitions` — claim/apply transitions are AST-1197
- [X] `agent_task` / Ruth prompt authoring — AST-1196
- [X] Live DB rewrite of rows still stored as `JD_SCRAPE_FAIL_BOT` — ops/UAT follow-up if staging has orphans; not a `src/` consumer
- [X] `tests/` / bible — Betty after Code Complete

## Acceptance criteria

1. [x] Mixed chunk with some null `job_link`/`job_title` and some full http extracts: good rows **QUALIFY**; others follow synthesize/subject/fail/bot rules; chunk does **not** all-ERROR. (schema portion: null/omit must not abort `do_task`.)
2. [x] Cloudflare / challenge JD body → **BOT_BLOCKED** (not **METEORITE_QUALIFIED**). (registry/UI portion.)
3. [x] `JD_SCRAPE_FAIL_BOT` is gone from config/UI; **BOT_BLOCKED** is the universal bot-block state for jobs that need humans.

## Boundaries

- [X] Does not own `agent_task` authoring or consult assemble/apply.

## Notes for planning

Universal rename — touch every consumer of `JD_SCRAPE_FAIL_BOT` under `src/`.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1188-errors-for-qualify-meteorite-dispatch-task`, child `sub/AST-1188/AST-1195-schema-nulls-bot-blocked`. Created at dispatch-parent.

### Comments

#### chuckles — 2026-08-05T23:56:05.632Z
[merge-child] blocked: git pull merge on sub — use: git fetch && git merge origin/ftr/<parent-segment>

`validate-sub-log` failed on `origin/sub/AST-1188/AST-1195-schema-nulls-bot-blocked`. Pull-merge subjects (must not be on sub):
- `Merge remote-tracking branch 'origin/sub/AST-1188/AST-1195-schema-nulls-bot-blocked' into sub/AST-1188/AST-1195-schema-nulls-bot-blocked` (`559bc524`, `4ac09966`)
- `Merge remote-tracking branch 'origin/dev' into sub/AST-1188/AST-1195-schema-nulls-bot-blocked` (`36c5c71e`)

@Ada Lovelace — republish a linear history on this publish ref (stack on `origin/ftr/AST-1188-errors-for-qualify-meteorite-dispatch-task`, no `Merge remote-tracking branch`, keep plan/code/merge-tests/test/docs/resolve for AST-1195). Then Chuckles retries merge-child.

— Chuckles

#### radia — 2026-08-05T23:53:38.083Z
[code-rubric] revision=1

**Rubric:** code-rubric.v1
**Ticket:** AST-1195
**Publish ref:** `0049210f` (`origin/sub/AST-1188/AST-1195-schema-nulls-bot-blocked`)
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

#### betty — 2026-08-05T23:40:08.714Z
Tests Ready — run on `origin/sub/AST-1188/AST-1195-schema-nulls-bot-blocked` @ `1e2e0539` (`merge-tests(AST-1195): origin/tests 6a84c0b809af2b50dbfffbeacc9e8ea5a6bc1c95`).

**Manifest**
1. `tests/component/utils/test_config.py::TestAst1195SchemaNullsAndBotBlocked` — `job_link`/`job_title` optional + omit/null validation; `BOT_BLOCKED` registry / skipped UI / gazer error_states
2. `tests/component/utils/test_config.py::TestAst1127QualifyMeteoriteCompanyJobIdOptional` — revised (siblings stay required via `jd_text`)
3. `tests/component/utils/test_config.py::TestAst1060QualifyMeteoriteConfig` — revised (`job_title`/`job_link` required False)
4. `tests/component/utils/test_config.py::TestAst1156SkippedBulkRetryMap` — map completeness + priors still cover `BOT_BLOCKED`
5. `tests/component/core/test_gazer.py::TestAst1195BotBlockedErrorState` — `_JD_ERROR_STATES["bot"] == "BOT_BLOCKED"`
6. Frontend fixture consumers (no new page cases):
   `cd src/ui/frontend && npx vitest run ../../../tests/component/frontend/contexts/test_StateUiContext.test.tsx ../../../tests/component/frontend/pages/test_JobsSkipped.test.tsx`

**Narrowed pytest**
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1195SchemaNullsAndBotBlocked \
  tests/component/utils/test_config.py::TestAst1127QualifyMeteoriteCompanyJobIdOptional \
  tests/component/utils/test_config.py::TestAst1060QualifyMeteoriteConfig \
  tests/component/utils/test_config.py::TestAst1156SkippedBulkRetryMap \
  tests/component/core/test_gazer.py::TestAst1195BotBlockedErrorState \
  -q
```

**Bible shasums** (`origin/sub/…`)
- `docs/test-bible/utils/config.md` `aa29b79e5ed3eebbde65ce7013ddea8890cc76b0`
- `docs/test-bible/core/gazer.md` `be645d3c3d47ee66dadc6f0371b998fa75d766fb`
- `docs/test-bible/frontend/pages.md` `7677f6df5ab004ccb2f32d53a48c8e8958e27544`

**Broken / revised this pass:** AST-1060/1127 required-True asserts on `job_title`/`job_link`; fixture `JD_SCRAPE_FAIL_BOT` → `BOT_BLOCKED`.

**Integration:** none revised.

— Betty

#### ada — 2026-08-05T23:33:16.895Z
[check-linear] Plan patched for discuss 1–3 @ `origin/sub/AST-1188/AST-1195-schema-nulls-bot-blocked` (Revision 1).

- Bulk-retry Decision now includes `startswith("METEORITE_")` identity loss + UAT follow-up note (no meteorite-only bot state; return path = new ticket if Archie wants it).
- Dropped explicit `JOBS_SKIPPED_SECTION_LABELS` step (title-case fallback already yields `Bot Blocked`).
- Stage 2 Done-when leans on the `rg` empty-gate; removed import-assert language.

Status stays Plan Approved.

#### joan — 2026-08-05T23:31:53.139Z
[plan-rubric] revision=1

**Rubric:** plan-rubric.v1
**Ticket:** AST-1195
**Overall:** APPROVED
**Publish ref tip:** `origin/sub/AST-1188/AST-1195-schema-nulls-bot-blocked` @ `c7d40ad5`

## Traceability

AC1→S1 (schema portion: null/omit must not abort `do_task`); AC2→S2 steps 1–7 (registry + gazer map + skipped UI manifests); AC3→S2 steps 1–8 (rename plus the empty-`rg` gate). No unmapped AC, no orphan stages. Parent AC1/AC4/AC5/AC7/AC8 remainder is N/A–boundary for this child ("Does not own `agent_task` authoring or consult assemble/apply" — AST-1196 / AST-1197).

**Considered:** full active corpus swept (65 leaves — 18 universal + 38 scoped considered, 9 scoped excluded on layer/path predicates); all considered statutes score `conforms`. Recorded in-session per R7.

## Verification notes

I checked the two things that decide this plan, because both are the kind that look fine on paper and fail in the tree.

**The schema premise holds for the observed payload — including explicit `null`.** This mattered: the parent Purpose says Ruth returned JSON `null`, not that she omitted the keys, and `required: False` only helps if the validator tolerates a present-but-null value. `_validate_schema_object_fields` (`src/core/agent.py:1556-1563`) does `val = obj.get(field_name)`, then `if required and val is None` → error, then `if val is None: continue` — so once `required` is `False`, a literal `null` and an omitted key both skip the type check and pass. Confirmed the current values are `required: True` (`src/utils/config.py:506-507`), which is exactly why the whole chunk aborted, and that the `company_job_id` anchor assert the plan appends to really exists (`config.py:973`, AST-1127). Stage 1 is correct as written.

**The rename sweep is genuinely complete.** For a universal rename the only real risk is a missed consumer, so I enumerated them rather than trusting the list: under `src/` the old id appears exactly six times in `config.py` — `GAZER_CONFIG["fetch_jd"]["error_states"]` (1956), `PASSED_JOBLIST` priors (2177), the `JOB_STATES` key (2183), `SKIPPED_STATES` (3029), `JOBS_SKIPPED_SECTION_ORDER` (3138), `JOBS_SKIPPED_BULK_RETRY_TO_STATE` (3270) — plus `gazer.py:90`. Every one has a matching plan step, and no frontend source references the id. I also checked for the silent-failure mode a rename invites: nothing anywhere does `startswith("JD_SCRAPE_FAIL")`, so renaming the bot variant cannot quietly drop it out of a computed scrape-fail class.

**Priors match the meteorite track.** `METEORITE_NEW` is the qualify claim state (`JOB_STATES:2224`) and both sibling outcomes `METEORITE_FAILED_QUALIFY` / `METEORITE_ERROR_QUALIFY` list `METEORITE_NEW` as prior, so `BOT_BLOCKED ← [PASSED_JOBLIST, METEORITE_NEW]` is the right shape for AST-1197 to transition a challenge JD without a meteorite-only bot state.

## Findings

**1. `discuss` — a meteorite job parked on `BOT_BLOCKED` loses its state-based track identity, and the plan only discloses half of that.** `consult.py:85` decides meteorite-ness by prefix (`_entity_state_is_meteorite` → `startswith("METEORITE_")`), and `BOT_BLOCKED` has no prefix by design. Combined with the retry map you already flagged, a meteorite row blocked by Cloudflare has exactly one automated exit — bulk-retry to `PASSED_JOBLIST`, i.e. the roster scrape flow, not the meteorite track. Two mitigations worth knowing: `is_meteorite_company` (`src/core/meteorite.py:23`) still recovers identity from the company, and `consult.py:1561` already special-cases meteorite companies in a claim path, so a future return path is feasible without a new state. I am **not** asking you to build one — parent Boundaries explicitly forbid inventing a meteorite-only bot state, so the universal id is the locked design and this consequence follows from it. Please add the prefix-test half to the existing bulk-retry Decision so the tradeoff is visible, and let Archie confirm at UAT whether a meteorite return path is wanted (that would be a new ticket, not a widening of this child).

**2. `discuss` — Stage 2 step 5's explicit label is a no-op.** `build_state_ui_manifest()` computes `JOBS_SKIPPED_SECTION_LABELS.get(s, s.replace("_", " ").title())` (`config.py:3291`), and the fallback for `BOT_BLOCKED` is already the byte-identical `"Bot Blocked"`. Adding the entry changes nothing, diverges from the sibling scrape-fail states that deliberately rely on the fallback, and adds a second place to edit later. Drop the step, or keep it and say why (e.g. you want the human string pinned independently of the id).

**3. `discuss` — the Done-when overstates the import-time safety net.** "`build_state_ui_manifest()` still asserts cleanly on import" is not a rename guard: the asserts in that function cover candidate gen-states, company bulk targets, and `grade_field` keys — none covers `SKIPPED_STATES`, `JOBS_SKIPPED_SECTION_ORDER`, or `JOBS_SKIPPED_BULK_RETRY_TO_STATE`. Worse, `skipped_order` *filters* with `if s in JOB_STATES` (`config.py:3289`), so a half-finished rename silently drops the section from the UI instead of failing loudly. Your step 8 (`rg JD_SCRAPE_FAIL_BOT src/` returns nothing) is the actual gate — lean on it and downgrade the assert language so a later reader does not trust a check that is not there.

**4. `acceptable`** — `tests/component/frontend/fixtures/stateUiManifestFixture.ts` pins the old id in both `section_order` and `bulk_retry`. Correctly out of scope for you (`orch.roles.betty-owns-test-tree`), and step 8's carve-out for `tests/` is right — but that fixture will go red, which is expected qa-child work at Tests Ready rather than engineer drift.

**5. `acceptable`** — The no-live-row-migration decision is honest and correctly scoped. Worth noting the user-visible shape: because the skipped manifest filters on registry membership, any staging row still on `JD_SCRAPE_FAIL_BOT` becomes invisible in Jobs Skipped rather than mislabeled. That is the right thing to eyeball during UAT.

Self-assessment is accurate. `Conf: high` is earned here — unlike a plan that asserts a mechanism, this one names a precedent (AST-1127 `company_job_id`) that I could verify, and the consumer set is finite and enumerated. `Risk: Medium` correctly identifies missed-consumer and wrong-priors as the two failure modes; both came back clean on inspection.

context_tokens≈128000

— Joan

#### ada — 2026-08-05T23:27:24.552Z
Plan published on `origin/sub/AST-1188/AST-1195-schema-nulls-bot-blocked` @ `c7d40ad5`.

**Plan:** https://github.com/susansomerset/astral/blob/sub/AST-1188/AST-1195-schema-nulls-bot-blocked/docs/features/meteorite/ast-1195-schema-nulls-bot-blocked.md

**Self-assessment**
- **Scope:** Single-Component — `qualify_meteorite` schema `required: False` for `job_link`/`job_title` in `config.py`, plus universal `JD_SCRAPE_FAIL_BOT` → `BOT_BLOCKED` across `JOB_STATES` / gazer / skipped UI manifests (`gazer.py` one-line map).
- **Conf:** high — same `required: False` pattern as AST-1127 `company_job_id`; rename consumers under `src/` are enumerated and finite.
- **Risk:** Medium — missed consumer or wrong priors could strand bot-blocked jobs or leave a dead state id; no consult apply in this child.

**Decisions locked in plan:** `BOT_BLOCKED` priors = `PASSED_JOBLIST` + `METEORITE_NEW`; skipped bulk-retry stays `PASSED_JOBLIST`; no live-row DB migration.

---

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

## Resolution

**Date:** 2026-08-05
**Review:** Radia `[code-rubric] revision=1` — **Overall: CLEAN** @ `0049210f` (`origin/sub/AST-1188/AST-1195-schema-nulls-bot-blocked`).

| Item | Action |
|------|--------|
| fix-now | none |
| discuss | none |
| advisory — `pattern.*` citation slip in Linear description | Corrected description In scope / Considered but excluded to active `astral.*` ids (`astral.config.config-source-of-truth` already listed; `pattern.batch…` → `astral.batch.claim-process-release` as excluded sibling statute). No product code change. |

No product or plan-stage rewrites required. Ship as built.
