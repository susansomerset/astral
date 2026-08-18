<!-- linear-archive: AST-1214 archived 2026-08-17 -->

## Linear archive (AST-1214)

**Archived:** 2026-08-17  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1214/admin-catalogapi-hardcode-audit-alphabetical-task-key-lists-ui  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1185 — UI groupings/sequences + alphabetical task key/alias dropdowns (data-driven)  
**Blocked by / blocks / related:** parent: AST-1185; related: AST-1182; blocks: AST-1215

### Description

## What this implements

Owns the inventory and fix on Admin API / enrichment paths that feed grouping metadata and task-key catalogs: remove extraneous hard-coded task lists/sequences on those paths, ensure dropdown consumers get a live catalog sorted alphabetically by task key covering all agent_task keys (including fetch_* and peers; aliases included when present). Does **not** own React section rendering or dropdown UX polish (sibling UI child). Does **not** implement alias resolve (AST-1184) or seed Gaze/Meteorite sections (AST-1183).

## Acceptance criteria

- [X] Every in-scope Admin task-key dropdown lists catalog keys alphabetically by task key; after AST-1184 lands, alias keys appear in that same alphabetical list as first-class options.
- [X] Touched Admin API paths related to this epic contain no hard-coded task-key membership lists or hard-coded section/sequence inventories that restate grouping already on agent_task / config catalogs.
- [X] Changing a row’s grouping metadata (or adding an alias catalog key) changes what operators see on those surfaces without a parallel frontend constant edit for membership or dropdown order.

## Boundaries

Does not own React section rendering or dropdown UX (sibling). Does not implement master_task_key / alias resolve (AST-1184) or Gaze/Meteorite seed (AST-1183).

## In scope

- [X] `pattern.ui.admin-endpoint` — thin `@require_admin` catalog endpoint; React consumes resolved payload
- [X] `pattern.config.config-block` — form + write defaults via `_dispatch_*` / extended `dispatch_task_admin_defaults` (gap keys first-class); no inline Admin sets
- [X] `astral.layers.ui-config-driven-business-logic` — membership + alphabetical order + write acceptance resolved in Admin API/config before React
- [X] `astral.standards.no-hardcoded-sets` — live `agent_task` ∪ `TASK_CONFIG` ∪ dispatch orphans; no new gap-key frozenset
- [X] `astral.config.config-source-of-truth` — entity/trigger defaults from config helpers; grouping from `agent_task`
- [X] `astral.patterns.require-auth-on-protected-endpoints` — keep `@require_admin` on `dispatch_tasks/task_keys` and mutate routes
- [X] `orch.pipeline.plan-is-bible` — picker membership aligned with POST/PUT acceptance (no filled-form-then-400)

## Considered but excluded

- [X] `astral.ui.frontend-file-placement` — React pages owned by AST-1215
- [X] `astral.seed.agent-tables-in-repo-json` — seed membership owned by AST-1183 / AST-1184 children
- [X] `astral.layers.import-direction` — no new cross-layer imports; continue existing `api_admin` → `database` catalog reads only
- [X] Jobs UI section configs (`JOBS_*_UI_SECTIONS`, etc.) — non-Admin product surfaces; out of epic default Admin-only scope
- [X] `GET /api/admin/vector_feedback/task_keys` rubric-owner filter — intentional subset, not full catalog

## Notes for planning

Product calls (AST-1214 plan): (1) operators may schedule the seven helper-resolvable gazer/roster/inflow hops — reverse AST-960 picker **and** defaults/write gates. (2) Archie/Chuckles: **no hiding** `parse_meteorite_email` — not a separate gap key; fold Admin contract into `meteorite_email` / `catch_meteorite_email` (candidate; Avail=Gmail ping); AST-1182 may absorb seed rename. Sort by task_key string. Catalog includes all agent_task keys including fetch_*.

## Git branch (authoritative)

Parent `ftr/AST-1185-ui-groupingssequences-alphabetical-task-keyalias-dropdowns`; child `sub/AST-1185/AST-1214-admin-catalog-api-hardcode-audit-alphabetical-task-key-lists`.

### Comments

#### chuckles — 2026-08-07T11:24:31.306Z
[merge-child] blocked: sub not stacked on ftr after refresh-ftr + hygiene absorb of sync-child pull-merge markers (4a9d33a3, 11ab829d). validate-sub-log now OK.

@Ada Lovelace — merge-resume: in epic worktree, merge `origin/ftr/AST-1185-ui-groupingssequences-alphabetical-task-keyalias-dropdowns` into the publish ref with subject `merge-resume(AST-1214): stack after ftr hygiene`, push to origin/sub (no force-push). Chuckles will re-run merge-child.

— Chuckles

#### radia — 2026-08-07T11:20:33.442Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1214
**Publish ref:** `b0f123604b73ee9edb643c477275260942b58470` (tip `b0f12360`; doc append at `4dcf7879`)
**Overall:** CLEAN

## Plan adherence

- Stage 1 (`_admin_dispatch_task_key_catalog`, live union + `sorted(membership)`, `dispatch_task_keys()` thinned to `jsonify(...)`) matches plan verbatim.
- Stage 2 (form-meta gate widen, `_dispatch_task_key_trigger_error` precedence flip, meteorite mailbox carve-out ordering in `dispatch_task_admin_defaults`, both `list_dtasks` Avail sites) matches the plan's own code snippets almost line-for-line.
- No hardcoded `parse_meteorite_email` literal anywhere in `api_admin.py` — fold routes entirely through `is_meteorite_email_mailbox_task_key` / `METEORITE_EMAIL_PARSE_CONFIG`, honoring the Archie "no hiding" product call. `admin_hidden_dispatch_task_keys()` confirmed empty (no `hidden_dispatch_task_keys` in `ADMIN_CONFIG`).
- Self-Assessment (`Single-Component` / `high` conf) holds: no React, no AST-1182 seed rename, no `tests/` edits by the engineer.

**Findings:** none (fix-now/discuss).

**Full active-set sweep:** all 63 `status: active` statutes scored in-session (18 universal, 45 scoped) — zero `violates`, zero `needs-discussion`. Git-role separation verified from commit log: `9d2e7629` (engineer, `src/` only) → `4d4f56b4` (Betty, `tests/`+`docs/test-bible/**` only) → single `b0f12360` merge-tests commit. `python3 -m py_compile` clean on both touched files at tip. Two plan-excluded ids (`astral.seed.agent-tables-in-repo-json`, `astral.layers.import-direction`) predicate-match on path but score `conforms` on inspection (no repo-JSON/bootstrap content, no new cross-layer imports) — consistent with the plan's own exclusion rationale, not a straggler. No Joan plan-rubric verdict attachment found on this ticket (only Betty's QA manifest comment) — noting `no plan-rubric verdict attached` per C4; not a block.

**Pattern conformance:** `pattern.ui.admin-endpoint` — conforms. `pattern.config.config-block` — conforms.

## Frame diff

(none — ticket description/AC unchanged; findings are diff-only)

context_tokens≈68000

— Radia

#### betty — 2026-08-07T11:12:35.560Z
## QA test manifest — AST-1214

**Publish:** `origin/sub/AST-1185/AST-1214-admin-catalog-api-hardcode-audit-alphabetical-task-key-lists` @ `b0f12360`
**Betty delivery:** `merge-tests(AST-1214): origin/tests 4d4f56b472397759e6bed3cc00ff6ac0ea7eeee5`

### Classification
1. **Existing (revised):** AST-960 gap-absent picker/defaults + inflow_discovery Unknown → flipped for live agent_task ∪ helper-resolvable + mailbox fold.
2. **Broken / obsolete (revised this pass):** `test_dispatch_task_keys_omits_fetch_jd_gap_excludes_retired`, `test_gap_key_absent_without_db_row`, KeyError expects on helper-resolvable / prefilter / inflow_resolve defaults, inflow_discovery Unknown in AST-804.
3. **Gaps (added):** alphabetical raw keys; mailbox null-only + craft unsupported wording; POST `fetch_jd` + `parse_meteorite_email`; mailbox Avail without gaze_email row; `TestAst1214DispatchAdminDefaultsWidened`.

**Integration:** no existing scenarios assert Admin `task_keys` membership / mailbox Avail — none revised.

### Manifest (test-child)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_admin.py::TestAst796FetchJdRetiredDispatchKeys \
  tests/component/ui/api/test_api_admin.py::TestAst960TaskKeysNoFrozensetInventory \
  tests/component/ui/api/test_api_admin.py::TestAst804CandidateDispatchAdminValidation::test_dispatch_task_key_trigger_error_candidate_paths \
  tests/component/ui/api/test_api_admin.py::TestAst1214AdminCatalogAlphabeticalWritable \
  tests/component/utils/test_config.py::TestAst796FetchJdSchedulableCutover::test_fetch_jd_gazer_hop_not_task_config_catalog \
  tests/component/utils/test_config.py::TestAst702PrefilterBatchConfig::test_prefilter_dispatch_batch_mode_and_defaults \
  tests/component/utils/test_config.py::TestAst719FetchJobPagesConfig::test_dispatch_registry_and_pjl_data_keys \
  tests/component/utils/test_config.py::TestAst701FetchWebsiteConfig::test_dispatch_registry_and_homepage_text_key \
  tests/component/utils/test_config.py::TestAst874FetchCulturePagesConfig::test_gazer_and_dispatch_registry \
  tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig::test_inflow_discovery_dispatch_admin_defaults \
  tests/component/utils/test_config.py::TestAst506InflowResolveConfig::test_inflow_resolve_website_dispatch_admin_defaults \
  tests/component/utils/test_config.py::TestAst1089ParseMeteoriteEmailConfig \
  tests/component/utils/test_config.py::TestAst1214DispatchAdminDefaultsWidened \
  -q
```

**Pass criterion:** pytest green on manifest — not zero-arg harness / branch-lock gate.

### Bible shasum (on publish tip)
- `docs/test-bible/ui/api/api_admin.md` — `19dc04005034a16d87853ea6f750b3759b681260`
- `docs/test-bible/utils/config.md` — `9e09669e2563a2c06534bfa456c3f33f7ad0b306`

— Betty

#### ada — 2026-08-07T11:07:06.967Z
[build-child] Stage 3 audit + Betty contract

`origin/sub/AST-1185/AST-1214-admin-catalog-api-hardcode-audit-alphabetical-task-key-lists` @ `9d2e7629` (product) / tip `23d1ee81` (review stub).

**Audit:** `api_admin.py` + `config.py` — no new task-key membership/section frozensets; mailbox fold via `METEORITE_EMAIL_PARSE_CONFIG` + `is_meteorite_email_mailbox_task_key`; catalog = `get_task_keys()` ∪ `list_candidate_tasks()` ∪ `list_dispatch_tasks()` minus hidden/retired via `sorted(membership)`. No `ADMIN_CONFIG` hide of `parse_meteorite_email`. `list_dtasks` / `list_tasks` grouping unchanged except Avail inbox predicate widen.

**Betty contract:**

**A. Picker (`test_api_admin.py`):** Flip `test_dispatch_task_keys_omits_fetch_jd_gap_excludes_retired` and `test_gap_key_absent_without_db_row`. Expect eight agent_task-only keys present: `fetch_culture_pages`, `fetch_jd`, `fetch_job_pages`, `fetch_website`, `gaze`, `inflow_discovery`, `parse_meteorite_email`, `recheck_no_openings`. Stay absent: `prefilter`, `inflow_resolve_website`.

**B. Validator:** Flip `test_dispatch_task_key_trigger_error_candidate_paths` for `inflow_discovery` → accept. `_dispatch_task_key_trigger_error("parse_meteorite_email", None|"")` → `None`; non-empty trigger for `parse_meteorite_email` / `meteorite_email` / `gaze_email` rejects (mailbox null-only). Form meta `parse_meteorite_email` → `entity_type: "candidate"`.

**C. Config (`test_config.py`):** Flip KeyError for `fetch_jd`, `fetch_job_pages`, `fetch_website`, `fetch_culture_pages`, `inflow_discovery`; `prefilter` / `inflow_resolve_website` → defaults dicts. Add mailbox defaults for `parse_meteorite_email` and `meteorite_email` (`entity_type=candidate`, null trigger/sort, `batch_call_mode=0`).

**D. Keepers:** `unsupported entity_type` for craft_* etc.; other `task_keys` endpoint tests.

**E. Harness:** patch `list_candidate_tasks`; raw-body alphabetical keys; POST `fetch_jd` + POST `parse_meteorite_email` (null trigger); optional `/adhoc/entities` 200; Avail covers both `need_gaze_counts` and per-row stamp for mailbox keys without requiring a `gaze_email` row.

#### joan — 2026-08-07T11:02:28.591Z
[plan-rubric] revision=1

**Rubric:** plan-rubric.v1
**Ticket:** AST-1214
**Overall:** APPROVED
**Publish ref tip:** `sub/AST-1185/AST-1214-admin-catalog-api-hardcode-audit-alphabetical-task-key-lists` @ `be63bc84`

## Traceability

AC1→S1–S2; AC2→S1.4, S3; AC3→S1–S2. No orphan stages. Files Changed still `ui` + `utils`, so the scoped statute match is unchanged from revision 1. The Avail work in S2.5 traces to the child's **Notes for planning** product call (2) — "Avail=Gmail ping" — rather than to a numbered AC; citing that here so it does not read as scope creep at code review.

**Considered:** `astral.standards.no-hardcoded-sets`, `astral.config.config-source-of-truth`, `astral.layers.ui-config-driven-business-logic`, `astral.patterns.require-auth-on-protected-endpoints`, `astral.layers.import-direction`, `astral.standards.utils-data-late-import-only`, `astral.standards.dry-and-focused-functions`, `astral.standards.public-then-helpers`, `astral.config.pass-threshold-vs-score-floor`, `astral.dispatch.seed-auto-false`, `astral.seed.archie-catalog-wins`, `astral.standards.in-scope-only`, `orch.pipeline.plan-is-bible` — all `conforms` (verdicts + considered-and-excluded scored in-session per R7 slim).

## All three green-lit edits applied, and re-verified against the merged tip

This tip also merged `origin/dev`, which touched `api_admin.py` (+63), `config.py` (+197), `test_config.py` (+213) and rewrote 118 lines of `agent_task.json` — so I re-ran the whole verification rather than only diffing the plan:

**Edit 1 — form-meta gate.** `if task_key in TASK_CONFIG or is_meteorite_email_mailbox_task_key(task_key):`, and you went one better than I asked by normalizing `derived["entity_type"] or ""` and the `None` trigger. I traced all three branches and they are complete and non-overlapping: `TASK_CONFIG` keys unchanged, mailbox keys reach the carve-out, and the seven helper-resolvable keys still fall through to the `_dispatch_*` fallback because they match neither predicate. `gaze_email` is unaffected — its carve-out returns `entity_type: None`, which normalized to `""` before and still does.

**Edit 2 — both Avail sites**, named with line numbers that are still exact after the merge: `need_gaze_counts` at `api_admin.py:863–867` and the per-row stamp at `:886`. Neither existing Avail test breaks, because `TestAst1106…` and `TestAst1135ListDtasksGazeAvail` use only `gaze_email` and `scan_jobs` rows, so `bound.assert_called_once_with()` still holds. Betty item E now asks for the case that would have caught the original gap — mailbox Avail non-zero with no `gaze_email` row present.

**Edit 3 — mailbox trigger null-only**, with a real error string instead of the `...` placeholder. This also changes `gaze_email`: an empty trigger flips from `trigger_state is required` to accepted, and a non-empty one flips from `unsupported entity_type` to the mailbox message. I checked — no test calls `_dispatch_task_key_trigger_error` with `gaze_email` and no test POSTs it through the API, so nothing is silently invalidated, and Betty B already names the non-empty rejection for all three keys.

**Post-merge re-verification:**

- Membership recomputed: still exactly the **eight** — `fetch_culture_pages`, `fetch_jd`, `fetch_job_pages`, `fetch_website`, `gaze`, `inflow_discovery`, `parse_meteorite_email`, `recheck_no_openings`. 52 `agent_task` rows, 47 `TASK_CONFIG` keys (the merge dropped two, neither plan-relevant), hidden list empty, `gaze_email` still the only `dispatch_task` row. Aliases `meteorite_grade_do` / `meteorite_grade_get` present.
- All nine keys still resolve entity / trigger / `sort_by` / `batch_call_mode` identically, and `grade_do` still resolves — so the Stage 2 statement-ordering swap still preserves `trigger_state is required`.
- All eleven Betty-cited tests still exist verbatim in both files after the `test_config.py` churn.
- `METEORITE_EMAIL_PARSE_CONFIG` is still `{task_key, parse_modes}` with `meteorite_email` still in `TASK_CONFIG`, so the added fold fields keep the module-level asserts and `TestAst1089ParseMeteoriteEmailConfig` green.
- Every anchor line the plan cites is still accurate at this tip: `:863–867`, `:886`, `:935`, `:1062`.

## Findings

### nit — duplicated Done-when bullet

Stage 2's first Done-when bullet is repeated byte-for-byte on lines 82 and 83 of the plan doc — an artifact of the revision-4 edit. No effect on meaning; clean it up whenever the doc is next touched, no re-publish needed on my account.

### acceptable — the unschedulable-wording class is now thirteen keys, not fourteen

For Betty's benefit only: `craft_get_rubric` gained a resolvable entity type in the `origin/dev` merge, so the `unsupported entity_type` class is `bootstrap_candidate_context`, `contact_estelle_turn`, `craft_company_search_terms`, six `craft_*` rubric keys, `craft_resume_base`, `simple_resume_parse`, `gaze_email`, `meteorite_email` — thirteen. That is a dev change, not a plan change, and the plan wisely says "e.g. craft_*" rather than pinning a count. Nobody should go hunting for a fourteenth.

## Verdict

No `fix-now` findings. Self-assessment is honest — `Single-Component` is fair for two files in one Admin surface, `high` conf is backed by named mechanisms rather than hand-waving, and `Medium` risk correctly flags that this schedules gazer/inflow hops and the meteorite mailbox under the pre-rename `parse_meteorite_email` name. R1–R6 pass; R7 satisfied by this comment. Status → **Plan Approved**.

Four rounds is more than I like to spend, and the plan is materially better for it — the write path, the Betty invalidation set, and the eighth key were all real defects that would have cost a build each.

— Joan

context_tokens≈145000

#### ada — 2026-08-07T10:58:37.105Z
[plan-discuss] reply

Archie/Susan green-light applied (round count reset). Plan @ `be63bc84` on `origin/sub/AST-1185/AST-1214-admin-catalog-api-hardcode-audit-alphabetical-task-key-lists`.

https://github.com/susansomerset/astral/blob/sub/AST-1185/AST-1214-admin-catalog-api-hardcode-audit-alphabetical-task-key-lists/docs/features/meteorite/ast-1214-admin-catalog-api-hardcode-audit-alphabetical-task-key-lists.md

**Three edits:**
1. `_dispatch_task_key_form_meta` gate is now `task_key in TASK_CONFIG or is_meteorite_email_mailbox_task_key(task_key)` so mailbox carve-out fills form meta (`entity_type: candidate`).
2. Stage 2 step 5 names both Avail sites — `api_admin.py` ~863–867 (`need_gaze_counts`) and ~886 (per-row stamp).
3. Mailbox `trigger_state` **null-only** — non-empty rejected for gaze_email + meteorite mailbox keys.

Status left **Plan Discuss** for Joan re-validate. Do not move to Plan Approved.

#### chuckles — 2026-08-07T10:55:54.086Z
[datt] Archie green-light on Joan escalate (reset round count): apply all 3 plan edits — (1) form-meta gate admits `is_meteorite_email_mailbox_task_key`, (2) step 5 names both Avail sites `:863–867` and `:886`, (3) mailbox trigger-null only (reject non-empty). Then re-validate.

— Chuckles

#### susan — 2026-08-07T06:09:04.332Z
All 3 edits approved.  Please reset your round count.

#### joan — 2026-08-07T05:52:34.127Z
[plan-discuss] escalate
[plan-rubric] revision=1

**Rubric:** plan-rubric.v1
**Ticket:** AST-1214
**Overall:** ESCALATE (past Plan Discuss cap — one mechanical fix-now, no product question left)
**Publish ref tip:** `sub/AST-1185/AST-1214-admin-catalog-api-hardcode-audit-alphabetical-task-key-lists` @ `876fdba4`

## Traceability

AC1→S1–S2; AC2→S1.4, S3; AC3→S1–S2. No orphan stages. Files Changed still `ui` + `utils`, so the scoped statute match is unchanged from revision 1.

**Considered:** `astral.standards.no-hardcoded-sets`, `astral.config.config-source-of-truth`, `astral.layers.ui-config-driven-business-logic`, `astral.patterns.require-auth-on-protected-endpoints`, `astral.layers.import-direction`, `astral.standards.utils-data-late-import-only`, `astral.standards.dry-and-focused-functions`, `astral.standards.public-then-helpers`, `astral.config.pass-threshold-vs-score-floor`, `astral.dispatch.seed-auto-false`, `astral.seed.archie-catalog-wins`, `astral.standards.in-scope-only`, `orch.pipeline.plan-is-bible` (verdicts + considered-and-excluded scored in-session per R7 slim).

## Escalate finding is closed; the fold is the right mechanism

Revision 3 lands Archie's call correctly, and I re-verified it against `876fdba4` — which matters, because this tip also merged `origin/dev` and rewrote `data/admin/agent_task.json`:

- **Membership recomputed post-merge:** still exactly the eight the plan names — `fetch_culture_pages`, `fetch_jd`, `fetch_job_pages`, `fetch_website`, `gaze`, `inflow_discovery`, `parse_meteorite_email`, `recheck_no_openings` (52 `agent_task` rows, 49 `TASK_CONFIG` keys, hidden list empty). Aliases `meteorite_grade_do` / `meteorite_grade_get` are in the catalog. The seed still carries `parse_meteorite_email` and no `catch_meteorite_email`, so leaving the rename to AST-1182 is correct.
- **Every fold anchor exists and is already imported** in `api_admin.py`: `GAZE_EMAIL_CONFIG` (line 70), `CANDIDATE_STATES` (62), `count_inbox_bound_by_candidate` (25). No new import beyond `is_meteorite_email_mailbox_task_key`.
- **The config additions are safe.** `METEORITE_EMAIL_PARSE_CONFIG` is `{task_key, parse_modes}` today; adding `legacy_agent_task_key` / `admin_entity_type` keeps both module-level asserts at `config.py:2488–2489` true, and keeps all of `TestAst1089ParseMeteoriteEmailConfig` green — including `assert "parse_meteorite_email" not in TASK_CONFIG` and the `pytest.raises(KeyError)` on `_dispatch_trigger_state_for_task_key("meteorite_email")`, since the plan touches `dispatch_task_admin_defaults` and not that helper.
- **Betty's config coverage is complete this time.** I swept every `dispatch_task_admin_defaults` call site in both test files rather than spot-checking: the retired-key loop (`test_config.py:616`) and `not_a_registered_task_key` (`:641`) still raise, and nothing else in either file reaches the mailbox keys. No omission.
- **POST 201 for `parse_meteorite_email` is reachable.** `create_dtask`'s required-field check only tests key *presence*, so `trigger_state: null` passes it; `save_dispatch_task` then calls `dispatch_task_admin_defaults`, which the carve-out satisfies, and inserts candidate / NULL / NULL / 0 — the gaze_email row shape.
- `trigger_state_used_by_scored_dispatch_task` is unaffected (`meteorite_email` is `scored: False`, so the loop skips it).

## Findings

### fix-now — Stage 2's own Done-when for form meta cannot be reached by Stage 2's steps

The Done-when requires, for `parse_meteorite_email`, that "form meta shows `entity_type: "candidate"`". The steps do not produce that.

`_dispatch_task_key_form_meta` (`api_admin.py:935`) gates its only call to `dispatch_task_admin_defaults` on `if task_key in TASK_CONFIG:`. `parse_meteorite_email` is not in `TASK_CONFIG` — that is the whole premise of the fold — so the mailbox carve-out added in step 4 is never consulted for it. Step 1's fallback is unchanged from revision 2 and reaches only `_dispatch_entity_type_for_task_key` / `_dispatch_trigger_state_for_task_key`, both of which raise `KeyError` for this key. The `except KeyError: pass` leaves `entity_type` at `""`, so the endpoint publishes the eighth key with an empty entity type.

So the executor either follows the steps and fails their own Done-when, or invents the missing edit. It is one clause — the gate needs to read `if task_key in TASK_CONFIG or is_meteorite_email_mailbox_task_key(task_key):` — but `orch.pipeline.plan-is-bible` means the plan has to say it, and this is the third revision where a Save-path detail was left to inference.

Note the consequence is milder than the escalate finding: Save still succeeds, because step 2's validator branch matches on the mailbox helper and not on form meta. The operator gets a working row with a blank entity field in the form, not a 400.

### discuss — the Avail snapshot gate is a second site, and step 5 only names the first

Step 5 says to extend the gaze_email Avail branch. There are two coupled sites in `list_dtasks`, and it addresses one:

- `api_admin.py:863–867` — `need_gaze_counts` decides whether `count_inbox_bound_by_candidate()` runs at all, matching `task_key == gaze_tk`.
- `api_admin.py:886` — the per-row stamp, same match.

If only line 886 gains the mailbox helper, `bound_counts` stays `{}` whenever no candidate-bound gaze_email row is present, and every meteorite mailbox row silently stamps Avail 0. Today the only `dispatch_task` row on this tip is `gaze_email`, so a test written with the default fixture would pass while the real behavior is wrong the moment that row is absent or unbound. Betty item E ("Avail > 0 when inbox binds exist") would not catch it either. Naming both line numbers in step 5 costs one line.

### discuss — accepting a non-empty trigger on a mailbox key invents a row shape that has never existed

Step 2 resolves the snippet's `...` as: empty trigger accepted, non-empty must be in `CANDIDATE_STATES`. That second half is the questionable half. The carve-out in step 4 returns `trigger_state: None` and `sort_by: None` unconditionally, but `save_dispatch_task` only substitutes its default when the caller's value is blank — so an operator who supplies `ACTIVE_SEARCH` gets a row with a real trigger_state and a null `sort_by`, on a task `TestAst1089ParseMeteoriteEmailConfig` documents as "not a dispatch claim task".

I checked that this does not crash: both `ORDER BY {sort_by}` builders are guarded by `if sort_by and sort_by in …` with a fallback. I did **not** trace the full claim path, so I am not asserting the runtime would actually claim it — only that the plan creates the state and says nothing about it. The simpler shape is to reject non-empty triggers for mailbox keys outright, which matches gaze_email and removes the question. Your call, but it should be one of the two.

## Why this is @susan again rather than round 3

The cap was already consumed by rounds 1 and 2, so `validate-plan` §8 routes any further REVISE here. I want to be clear that this is **not** a second deadlock: the product decision you and Archie made is applied correctly and I have no quarrel with it. What is left is one contradiction between Stage 2's steps and Stage 2's own Done-when, plus two one-line specificity gaps. If you green-light the three edits below, the plan is approvable as-is and I will flip it on the next pass:

1. `_dispatch_task_key_form_meta` gate also admits `is_meteorite_email_mailbox_task_key(task_key)`.
2. Step 5 names both `api_admin.py:863–867` and `:886`.
3. Step 2 picks one shape for mailbox trigger_state — my recommendation is trigger-null only, matching gaze_email.

— Joan

context_tokens≈105000

#### ada — 2026-08-07T05:25:22.440Z
[plan-discuss] round=3 reply

Plan revised @ `876fdba4` on `origin/sub/AST-1185/AST-1214-admin-catalog-api-hardcode-audit-alphabetical-task-key-lists`.

https://github.com/susansomerset/astral/blob/sub/AST-1185/AST-1214-admin-catalog-api-hardcode-audit-alphabetical-task-key-lists/docs/features/meteorite/ast-1214-admin-catalog-api-hardcode-audit-alphabetical-task-key-lists.md

**Archie/Chuckles product call applied:** **No hiding** — will not put `parse_meteorite_email` in `ADMIN_CONFIG` hidden keys. Not treated as an eighth gazer/inflow gap key.

**Disposition:** Misnamed meteorite mailbox identity (seed still `parse_meteorite_email`; config `meteorite_email`). Stage 2 folds Admin defaults/validator/Avail onto `METEORITE_EMAIL_PARSE_CONFIG` (`legacy_agent_task_key` + `admin_entity_type: candidate`, Gmail ping Avail via gaze_email inbox bind counts). Seed rename to `catch_meteorite_email` / full fold left to **AST-1182**.

**Membership:** Corrected to **eight** agent_task-only keys (seven helper-resolvable + `parse_meteorite_email`). Betty A–E updated accordingly.

Rejected Joan escalate options 1 (hide) and 3 (ship 400).

Status left **Plan Discuss** for Joan re-validate.

#### chuckles — 2026-08-07T05:16:40.237Z
[check-linear] Archie product call (parent AST-1185): **no hiding**. Do not treat `parse_meteorite_email` as an eighth gap key to hide/filter/400. It is misnamed — fold into `meteorite_email` / rename to `catch_meteorite_email` (candidate entity; Avail = Gmail inbox ping; FOR-candidate messages → Ruth). Revise plan accordingly (AST-1182 rename scope may absorb). Plan Discuss → Ada.

— Chuckles

#### joan — 2026-08-07T01:32:31.525Z
[plan-discuss] escalate
[plan-rubric] revision=1

**Rubric:** plan-rubric.v1
**Ticket:** AST-1214
**Overall:** ESCALATE (Plan Discuss cap — round 2 complete, one new fix-now)
**Publish ref tip:** `sub/AST-1185/AST-1214-admin-catalog-api-hardcode-audit-alphabetical-task-key-lists` @ `8c44b490`

## Traceability

AC1→S1–S2; AC2→S1.4, S3; AC3→S1–S2. No orphan stages. Files Changed unchanged from revision 1 (`ui` + `utils`), so the scoped statute match is unchanged.

**Considered:** `astral.standards.no-hardcoded-sets`, `astral.config.config-source-of-truth`, `astral.layers.ui-config-driven-business-logic`, `astral.patterns.require-auth-on-protected-endpoints`, `astral.layers.import-direction`, `astral.standards.utils-data-late-import-only`, `astral.standards.dry-and-focused-functions`, `astral.standards.public-then-helpers`, `astral.config.pass-threshold-vs-score-floor`, `astral.dispatch.seed-auto-false`, `astral.seed.archie-catalog-wins`, `astral.standards.in-scope-only`, `orch.pipeline.plan-is-bible` (verdicts + considered-and-excluded scored in-session per R7 slim).

## Round-2 findings: all closed

Revision 2 answers every one, and I executed the anchors against this tip rather than taking them on faith:

- **Betty breadth.** All ten cited tests exist verbatim — the two picker tests, `TestAst804CandidateDispatchAdminValidation::test_dispatch_task_key_trigger_error_candidate_paths`, and all seven `test_config.py` classes including the `prefilter` / `inflow_resolve_website` pair now correctly billed as *succeeding* rather than raising.
- **Product call named.** Section "Product call — scheduling gazer / roster / inflow runtime hops" states the call, the parent-AC basis, the rejected picker-yes/writer-no shape, and the override path. That satisfies `orch.pipeline.plan-is-bible`.
- **Write path executes.** All nine keys resolve end-to-end through the exact expression Stage 2 step 3 writes, `batch_call_mode` included: `fetch_culture_pages` job/PASSED_GET/latest_score/0 · `fetch_jd` job/PASSED_JOBLIST/updated_at/0 · `fetch_job_pages` company/PREFILTER_PASSED/updated_at/0 · `fetch_website` company/WEBSITE_FOUND/updated_at/0 · `gaze` company/WATCH/last_scan_at/0 · `inflow_discovery` candidate/ACTIVE_SEARCH/updated_at/0 · `recheck_no_openings` company/NO_OPENINGS/last_scan_at/0 · `prefilter` company/HOMEPAGE_READY/updated_at/1 · `inflow_resolve_website` company/NEW/updated_at/0. None is retired or admin-hidden.
- **Wording preserved.** Exactly fourteen `TASK_CONFIG` keys fail entity resolve (`gaze_email`, `meteorite_email`, the seven `craft_*`, `bootstrap_candidate_context`, `simple_resume_parse`, `contact_estelle_turn`, `craft_company_search_terms`, `craft_resume_base`); Stage 2 step 2's `if tk in TASK_CONFIG` branch keeps `unsupported entity_type` for all of them.
- **Ordering swap is safe.** Stage 2 step 2 moves entity resolution ahead of the `trigger_state is required` check. The only test asserting that message uses `grade_do`, whose entity resolves to `job`, so it still returns `trigger_state is required`; and `test_helper_unknown_task_key_wording` uses `not_a_registered_task_key`, which is outside `TASK_CONFIG` and so still yields `Unknown task_key`. Neither regresses.
- **Side effects documented.** Schema-ensure backfill, `/adhoc/entities` 404→200, and the intentional writer>picker asymmetry are all written down.

## Findings

### fix-now — the picker gains an **eighth** agent_task-only key, and that one dead-ends on Save

My round-1 and round-2 comments both said "exactly seven", and the plan's Audit findings section adopted that as a do-not-re-litigate fact. It is eight. Computing the Stage 1 helper's membership directly against live catalogs on this tip:

`agent_task` (52 current rows) − `TASK_CONFIG` (49 keys) − `admin_hidden_dispatch_task_keys()` (empty) − `DISPATCH_RETIRED_TASK_KEYS` = **`fetch_culture_pages`, `fetch_jd`, `fetch_job_pages`, `fetch_website`, `gaze`, `inflow_discovery`, `parse_meteorite_email`, `recheck_no_openings`**

`parse_meteorite_email` (agent `college_intern_ruth`) is the miss, and it is the one key of the eight that the product call does not rescue:

- It is **not** in `TASK_CONFIG` — the registered sibling is `meteorite_email`, because the rename is [AST-1182](https://linear.app/astralcareermatch/issue/AST-1182/rename-task-to-meteorite-email-ai-payload-as-visible-textlinks), an explicit parent Boundary.
- Both helpers raise: `dispatch entity_type: no rule for task_key 'parse_meteorite_email'`, same for trigger_state.
- It is not retired, not admin-hidden, and has no `dispatch_task` row (the only row on this tip is `gaze_email`), so it is **not** in the picker today. Stage 1 adds it.

So after Stage 1 the operator sees it; Stage 2 step 1's fallback leaves `entity_type` and `trigger_state` empty because both helpers `KeyError`; and Stage 2 step 2 returns `Unknown task_key: 'parse_meteorite_email'`, because it is outside `TASK_CONFIG` and therefore falls to the else branch. That is a filled-form-then-400 — the exact defect round 1 opened on, surviving for one key because the seven-key list it was measured against was wrong. No test catches it: `test_gap_key_absent_without_db_row` asserts the nine keys from the AST-960 era and never names this one.

Stage 1's Done-when and the Betty contract both enumerate seven, so as written the executor ships the dead end silently.

### Why this is @susan's call and not another round

This completes round 2, so a third REVISE would open `round=3` — `validate-plan` §6 sends it here instead. The fix is small, but choosing *which* fix is a product decision that runs straight into a parent Boundary, so I am not picking for you:

1. **Hide it via config** — add `parse_meteorite_email` to the `ADMIN_CONFIG` hidden dispatch keys. Uses the config-backed visibility mechanism the plan already honors, adds no hardcoded set to `api_admin.py`, and the key is headed for rename/retirement under AST-1182 anyway. My preference, and the smallest diff.
2. **Filter the picker to helper-resolvable agent_task keys** — data-driven and self-maintaining for future gap keys, but it softens the child AC wording "covering all `agent_task` keys" into "all schedulable `agent_task` keys", which is a real (if minor) AC edit.
3. **Ship it and document the 400** — cheapest, but it is the round-1 shape the plan already rejected on the merits, now applied to one key instead of seven.

Option 1 or 2 needs Stage 1's Done-when corrected from seven to the eight-key computation with the disposition named, and one Betty absence assertion so it cannot silently return. Everything else in revision 2 is sound and does not need to move.

### discuss — `meteorite_email` is already an unschedulable picker option today

Not this ticket's doing and not blocking: `meteorite_email` is a `TASK_CONFIG` key whose entity never resolves, so it sits in the picker today and 400s with `unsupported entity_type`. The plan's decision to preserve that wording keeps the behavior exactly as-is, which is correct for `astral.standards.in-scope-only`. Worth knowing only because it means the Meteorite email identity is operator-visible and unschedulable under *both* of its names until AST-1182 lands.

— Joan

context_tokens≈64000

#### ada — 2026-08-07T01:27:05.742Z
[plan-discuss] round=2 reply

Plan revised @ `8c44b490` on `origin/sub/AST-1185/AST-1214-admin-catalog-api-hardcode-audit-alphabetical-task-key-lists`.

https://github.com/susansomerset/astral/blob/sub/AST-1185/AST-1214-admin-catalog-api-hardcode-audit-alphabetical-task-key-lists/docs/features/meteorite/ast-1214-admin-catalog-api-hardcode-audit-alphabetical-task-key-lists.md

**Product call (named):** Operators **may** schedule the seven agent_task-only gazer/roster/inflow hops (`fetch_culture_pages`, `fetch_jd`, `fetch_job_pages`, `fetch_website`, `gaze`, `inflow_discovery`, `recheck_no_openings`). Reverses AST-960 picker **and** defaults/write gates together. Rejected picker-yes/writer-no. Not escalated — call is explicit in the plan for Archie override only if needed.

**Betty breadth:** Stage 3 contract now covers (A) the two picker presence tests, (B) `test_dispatch_task_key_trigger_error_candidate_paths` (`inflow_discovery` → accept, not `Unknown task_key`), (C) `test_config.py` KeyError flips for `fetch_jd` / `fetch_job_pages` / `fetch_website` / `fetch_culture_pages` / `inflow_discovery`, plus `prefilter` / `inflow_resolve_website` now expecting defaults dicts, (D) keepers including `unsupported entity_type` wording, (E) harness + write-path + optional `/adhoc/entities` 404→200.

**Other discuss items:** Documented schema-ensure backfill + Ad-hoc entities side effects; preserved known-but-unschedulable `unsupported entity_type` branch; noted writer>picker for non-agent_task helper keys as intentional.

Status left **Plan Discuss** for Joan re-validate.

#### joan — 2026-08-07T01:24:42.332Z
[plan-discuss] round=2 concern
[plan-rubric] revision=1

**Rubric:** plan-rubric.v1
**Ticket:** AST-1214
**Overall:** REVISE
**Publish ref tip:** `sub/AST-1185/AST-1214-admin-catalog-api-hardcode-audit-alphabetical-task-key-lists` @ `e780fb10`

## Traceability

AC1→S1–S2; AC2→S1.4, S3; AC3→S1–S2. Files Changed now spans layers `ui` + `utils`; re-matched scoped statutes for `src/utils/config.py`.

**Considered:** `astral.standards.no-hardcoded-sets`, `astral.config.config-source-of-truth`, `astral.layers.ui-config-driven-business-logic`, `astral.patterns.require-auth-on-protected-endpoints`, `astral.layers.import-direction`, `astral.standards.utils-data-late-import-only`, `astral.standards.dry-and-focused-functions`, `astral.standards.public-then-helpers`, `astral.config.pass-threshold-vs-score-floor`, `astral.dispatch.seed-auto-false`, `astral.seed.archie-catalog-wins`, `astral.standards.in-scope-only`, `orch.pipeline.plan-is-bible` (verdicts + considered-and-excluded scored in-session per R7 slim).

## Round-1 findings: all four closed

The write-path contradiction is resolved by the right mechanism. I executed the helpers against this tip to confirm it works for every one of the seven — entity type, trigger state, registry membership, and `sort_by` all resolve, and none is a chain trigger:

`fetch_culture_pages` job/PASSED_GET/latest_score · `fetch_jd` job/PASSED_JOBLIST/updated_at · `fetch_job_pages` company/PREFILTER_PASSED/updated_at · `fetch_website` company/WEBSITE_FOUND/updated_at · `gaze` company/WATCH/last_scan_at · `inflow_discovery` candidate/ACTIVE_SEARCH/updated_at · `recheck_no_openings` company/NO_OPENINGS/last_scan_at

Also verified: `dispatch_task_admin_defaults(task_key, trigger_state=None)` really does take that second parameter, so the Stage 2 step 3 snippet is valid; the anchors (retired check, then the `tk not in TASK_CONFIG` raise at `config.py:3043`) match; `_dispatch_batch_call_mode_for` and `_dispatch_sort_by_for` exist as written; and the `config.py:3103` scored-trigger loop iterates `TASK_CONFIG.items()` only, so it is unaffected.

## Findings

### fix-now — Stage 2 reverses seven documented AST-960 gates and invalidates a second test file the Betty contract does not name

`tests/component/utils/test_config.py` asserts `pytest.raises(KeyError, match="unknown task_key")` on `dispatch_task_admin_defaults` for exactly the keys Stage 2 step 3 enables, each with an explicit `# AST-960: <key> is gazer/roster/inflow runtime — not TASK_CONFIG catalog` comment:

| Class :: test | Key |
|---|---|
| `TestAst796FetchJdSchedulableCutover::test_fetch_jd_gazer_hop_not_task_config_catalog` | `fetch_jd` |
| `TestAst702PrefilterBatchConfig::test_prefilter_dispatch_batch_mode_and_defaults` | `prefilter` |
| `TestAst719FetchJobPagesConfig::test_dispatch_registry_and_pjl_data_keys` | `fetch_job_pages` |
| `TestAst701FetchWebsiteConfig::test_dispatch_registry_and_homepage_text_key` | `fetch_website` |
| `TestAst874FetchCulturePagesConfig::test_gazer_and_dispatch_registry` | `fetch_culture_pages` |
| `TestAst505InflowDiscoveryConfig::test_inflow_discovery_dispatch_admin_defaults` | `inflow_discovery` |
| `TestAst506InflowResolveConfig::test_inflow_resolve_website_dispatch_admin_defaults` | `inflow_resolve_website` |

And one more in the Admin file: `tests/component/ui/api/test_api_admin.py:1036`, `TestAst804CandidateDispatchAdminValidation::test_dispatch_task_key_trigger_error_candidate_paths`, asserts `_dispatch_task_key_trigger_error("inflow_discovery", "ACTIVE_SEARCH")` contains `Unknown task_key` — after Stage 2 step 2 it returns `None`, because `candidate` / `ACTIVE_SEARCH` is a valid registry pair. Its comment also reads "inflow_discovery is runtime-only".

So the Stage 3 Betty contract — which bills itself as exact, two tests in one file, "other twelve keep passing" — understates the invalidation by eight assertions across eight classes in two files. My round-1 count of twelve was scoped to endpoint callers of `dispatch_tasks/task_keys`, which was accurate for the round-1 plan; Stage 2 now edits the helper and the config function directly, which reaches tests that count never covered.

The deeper half: your `⚠️ Decision` reverses the AST-960 **picker** rule, which the parent AC backs. It does not address reversing the AST-960 **defaults gate**, and those seven sites describe these keys as gazer / roster / inflow *runtime* hops rather than operator-schedulable tasks. "Operators may now create dispatch rows for gazer and inflow runtime hops" is a product decision that deserves to be named in the plan (and may be Archie's call). If the answer turns out to be picker-yes / writer-no, that is a legitimate shape too — but then Stage 2's Done-when has to change, since it currently requires POST `fetch_jd` to return 201.

### discuss — the config helper has four call sites; the plan declares one

Files Changed says the `config.py` change "unblocks `save_dispatch_task` + PUT form-meta path". Two other callers change behavior:

- `_ensure_dispatch_task_schema` (`src/data/database.py:6498`) currently does `except KeyError: continue`, so gap-key `dispatch_task` rows keep their NULL `entity_type` / `trigger_state` / `sort_by` / `batch_call_mode`. After the change that loop backfills them on the next schema ensure. Latent today (no gap-key row can be created through the API) and correct once rows exist — but it is an automatic write to `dispatch_task`.
- `get_dispatch_row_or_seed_preview_meta` (`src/data/database.py:7054`) stops returning `None`, which flows through `api_admin.get_dispatch_task_by_key` (line 101) into `_build_adhoc_live_content` and `/adhoc/entities` (line 1263). The Ad-hoc Prompt Workbench populates its task select from `/api/admin/tasks`, which already lists all `agent_task` rows, so those seven keys are already selectable there and `/adhoc/entities` 404s on them today. Your change fixes an existing dead end — good, but it changes a 404 contract on a surface the parent epic scopes out ("grouping and dropdown paths"). One line each keeps Radia from reading it as scope creep (`astral.standards.in-scope-only`) and tells Betty the 404 is now a 200.

### discuss — message regression for registered-but-unschedulable keys

Replacing the `tk not in TASK_CONFIG` gate with helper-first acceptance means the fourteen `TASK_CONFIG` keys whose entity type never resolves — `gaze_email`, `meteorite_email`, the seven `craft_*` rubric tasks, `bootstrap_candidate_context`, `simple_resume_parse`, `contact_estelle_turn`, `craft_resume_base` — flip from `task_key 'X' has unsupported entity_type` to `Unknown task_key: 'X'`. That is misleading: the key is known, it just is not schedulable, and `test_helper_unknown_task_key_wording` shows the wording distinction is deliberate. Keeping a known-but-unschedulable branch for `tk in TASK_CONFIG` costs two lines.

### discuss — writer ends up slightly more permissive than the picker

After Stage 2, `prefilter` and `inflow_resolve_website` pass the writer gate (their entity types resolve) but never appear in the picker, since neither is a `TASK_CONFIG` or `agent_task` key on this tip. That is the reverse of the round-1 asymmetry and probably harmless — both are real roster hops — but worth one line so it reads as intentional rather than accidental.

## Round cap

This completes round 2. Per `validate-plan` §6, another REVISE would hit the Plan Discuss cap and escalate to @susan, so if the fix-now involves a product decision about scheduling runtime hops, raise it now rather than absorbing it into a third revision.

— Joan

context_tokens≈128000

#### ada — 2026-08-07T01:17:14.056Z
[plan-discuss] round=1 reply

Plan revised @ `e780fb10` on `origin/sub/AST-1185/AST-1214-admin-catalog-api-hardcode-audit-alphabetical-task-key-lists`.

https://github.com/susansomerset/astral/blob/sub/AST-1185/AST-1214-admin-catalog-api-hardcode-audit-alphabetical-task-key-lists/docs/features/meteorite/ast-1214-admin-catalog-api-hardcode-audit-alphabetical-task-key-lists.md

**fix-now (picker vs writer):** Chose first-class writable gap keys (not display-only). Stage 2 now aligns `_dispatch_task_key_trigger_error` + `dispatch_task_admin_defaults` with the same `_dispatch_*` helpers as form meta, so POST/PUT/`save_dispatch_task` accept helper-resolvable agent_task-only keys. `config.py` added to Files Changed.

**discuss (gap list):** Done-when pinned to the exact seven agent_task-only keys (`fetch_culture_pages`, `fetch_jd`, `fetch_job_pages`, `fetch_website`, `gaze`, `inflow_discovery`, `recheck_no_openings`). Dropped `prefilter` / `inflow_resolve_website` (not agent_task on this tip). Betty contract names the exact two failing tests + patch/`list_candidate_tasks` + raw-body alpha assertion + write-path coverage.

**discuss (alpha premise):** Corrected — Flask `jsonify` already sorts; plan still requires `sorted(membership)` as the explicit contract, not sibling reliance on the provider default.

**nit:** Betty note to patch `admin_mod.database.list_candidate_tasks` for determinism.

Status left **Plan Discuss** for Joan re-validate.

#### joan — 2026-08-07T01:12:31.080Z
[plan-discuss] round=1 concern
[plan-rubric] revision=1

**Rubric:** plan-rubric.v1
**Ticket:** AST-1214
**Overall:** REVISE
**Publish ref tip:** `sub/AST-1185/AST-1214-admin-catalog-api-hardcode-audit-alphabetical-task-key-lists` @ `2aa29ef2`

## Traceability

AC1→S1–S2; AC2→S1.4, S3; AC3→S1–S2. No orphan stages. Blockers AST-1183 / AST-1184 both User Testing — dependency gate satisfied, alias keys `meteorite_grade_do` / `meteorite_grade_get` are already live `TASK_CONFIG` entries on this tip.

**Considered:** `astral.standards.no-hardcoded-sets`, `astral.config.config-source-of-truth`, `astral.layers.ui-config-driven-business-logic`, `astral.patterns.require-auth-on-protected-endpoints`, `astral.layers.import-direction`, `astral.standards.in-scope-only`, `orch.pipeline.plan-is-bible` (verdicts + considered-and-excluded scored in-session per R7 slim).

## Findings

### fix-now — Stage 1 widens the picker to 7 keys the same module's writer rejects

`_dispatch_task_key_trigger_error` (`src/ui/api/api_admin.py:1062`) returns 400 `Unknown task_key: …` for any `task_key` not in `TASK_CONFIG`, and it gates both POST `/dispatch_tasks` (line 1029) and PUT `/dispatch_tasks/<id>` (line ~1106).

Exactly seven keys join the picker from `database.list_candidate_tasks()`: `fetch_culture_pages`, `fetch_jd`, `fetch_job_pages`, `fetch_website`, `gaze`, `inflow_discovery`, `recheck_no_openings`. **All seven are absent from `TASK_CONFIG`**, so every new option 400s on Save. Worse, Stage 2 makes them look fully usable — `_dispatch_entity_type_for_task_key` / `_dispatch_trigger_state_for_task_key` resolve all seven (job, job, company, company, company, candidate, company; `PASSED_JOBLIST`, `PASSED_GET`, GAZER states[0], `WEBSITE_FOUND`, `WATCH`, inflow discovery state, `NO_OPENINGS`) — so the operator gets a fully populated form that fails on submit. That is very likely why AST-960 omitted gap keys in the first place; the test comment at `test_dispatch_task_keys_omits_fetch_jd_gap_excludes_retired` says as much.

The validator lives in the file this plan owns, so it is not a sibling's problem, and the plan takes no position on it. That is an undocumented contradiction for the executor (`orch.pipeline.plan-is-bible`) and an operator-visible regression against the parent AC wording "first-class options". Your call which way to resolve — extend `_dispatch_task_key_trigger_error` to accept catalog keys whose entity/trigger derive from the same `_dispatch_*` helpers Stage 2 already uses, or declare gap keys display-only for this ticket and document the 400 as known/deferred — but the plan needs to say which.

### discuss — gap-key list is off by two, and "etc." can be closed exactly

`prefilter` and `inflow_resolve_website` are **not** `agent_task` keys on this tip (the roster ships `prefilter_company`, which is already in `TASK_CONFIG`), so two of the nine keys asserted absent by `test_gap_key_absent_without_db_row` will stay absent after the change. Stage 1's Done-when lists `prefilter` among the keys the payload will include — it will not appear. The "when those rows exist" qualifier keeps the gate technically satisfiable, but Betty will read that list as the contract and flip all nine.

On the invalidation set: only `TestAst796FetchJdRetiredDispatchKeys::test_dispatch_task_keys_omits_fetch_jd_gap_excludes_retired` and `TestAst960TaskKeysNoFrozensetInventory::test_gap_key_absent_without_db_row` actually break. The other twelve endpoint tests in `tests/component/ui/api/test_api_admin.py` keep passing — including `test_ast485_dispatch_task_keys_roster_seeds_minus_locate_template`, because neither `locate_job_page` nor `find_job_page` is in `data/admin/agent_task.json`. Pinning the exact pair plus the exact seven-key list turns "etc." into a script Betty can execute.

### discuss — alphabetical order is already true; the premise misattributes it

Flask 3.0.0's `DefaultJSONProvider.sort_keys` defaults to `True` and nothing in `src/ui` overrides it, so `jsonify` already emits this payload with keys sorted. The pre-plan claim that the endpoint "does not guarantee alphabetical JSON key order" is inaccurate, and the AST-1215 note ("may drop redundant `.sort()` once API order is alpha") leans a sibling's behavior on a Flask provider default rather than on your `sorted()`. Keep `sorted(membership)` — it is the right hygiene — but correct the premise and give Betty a raw-body key-order assertion so the guarantee is tested rather than inherited.

### nit — new DB read is unpatched in the component tier

`tests/conftest.py` points `ASTRAL_DB_DIR` at repo `data/`, so adding `database.list_candidate_tasks()` makes endpoint membership depend on live DB state across the fourteen tests that today patch only `admin_mod.list_dispatch_tasks`. Worth telling Betty to patch `admin_mod.database.list_candidate_tasks` for determinism.

## Verified sound

- `database.get_agent_task` does **not** alias-resolve, so alias rows keep their own grouping metadata — Stage 2 note 3 is accurate and the parent's "alias grouping independent of master" contract holds.
- `dispatch_task_key_is_scored` is safe for non-`TASK_CONFIG` keys (returns `False`), so no crash on the widened set.
- `_dispatch_trigger_state_for_task_key` is not yet imported in `api_admin.py` (only `_dispatch_entity_type_for_task_key`, line 75) — Stage 1 step 1 is correct, and both helpers raise `KeyError`, matching Stage 2's `except KeyError`.
- Step 4's explicit no-frozenset instruction satisfies `astral.standards.no-hardcoded-sets`; `@require_admin` is retained.

— Joan

context_tokens≈96000

#### ada — 2026-08-07T01:04:38.042Z
Plan published on `origin/sub/AST-1185/AST-1214-admin-catalog-api-hardcode-audit-alphabetical-task-key-lists` @ `2aa29ef2`.

https://github.com/susansomerset/astral/blob/sub/AST-1185/AST-1214-admin-catalog-api-hardcode-audit-alphabetical-task-key-lists/docs/features/meteorite/ast-1214-admin-catalog-api-hardcode-audit-alphabetical-task-key-lists.md

**Scope:** Single-Component — `src/ui/api/api_admin.py` only; expand `dispatch_tasks/task_keys` to live `agent_task` ∪ `TASK_CONFIG` ∪ dispatch orphans, alphabetical by `task_key`, with form-meta fallback via existing `_dispatch_*` helpers for gap keys (reverses AST-960 picker omission).

**Conf:** high — helpers and `list_candidate_tasks` already exist; old gap-absent tests document the contract to flip for Betty.

**Risk:** Medium — widens operator-visible picker options and will fail AST-960 gap-absent assertions until Betty revises at Code Complete; React remains AST-1215.

---

# Admin catalog/API hardcode audit + alphabetical task_key lists

**Linear:** [AST-1214](https://linear.app/astralcareermatch/issue/AST-1214/admin-catalogapi-hardcode-audit-alphabetical-task-key-lists-ui)  
**Parent:** [AST-1185](https://linear.app/astralcareermatch/issue/AST-1185/ui-groupingssequences-alphabetical-task-keyalias-dropdowns-data-driven)  
**Publish ref:** `sub/AST-1185/AST-1214-admin-catalog-api-hardcode-audit-alphabetical-task-key-lists`

Admin operators need Scheduled Actions (and peer Admin surfaces that consume the same catalog) to offer a **live** task-key picker that includes every current `agent_task` identity — including `fetch_*` and other agent_task-only peers, plus alias keys such as `meteorite_grade_do` / `meteorite_grade_get` — sorted **alphabetically by `task_key` string**, with grouping metadata still read from `agent_task` (not parallel phase/seq inventories). Today `GET /api/admin/dispatch_tasks/task_keys` is built from `get_task_keys()` (`TASK_CONFIG` insertion order) plus orphan `dispatch_task` rows, which intentionally omits agent_task-only keys (AST-960). Flask’s `jsonify` already emits sorted object keys by default; this ticket still builds membership with `sorted()` so alphabetical order is an explicit contract, not only a provider default. Catalog keys must be **writable** as first-class options (POST/PUT must not 400 after the form meta fills). This ticket owns that Admin API / config-defaults contract only; React section rendering and dropdown polish stay on AST-1215.

### Product call — scheduling gazer / roster / inflow runtime hops

**Call (this ticket):** Operators **may** create and update Scheduled Actions `dispatch_task` rows for the seven agent_task-only keys that resolve via `_dispatch_*` helpers: `fetch_culture_pages`, `fetch_jd`, `fetch_job_pages`, `fetch_website`, `gaze`, `inflow_discovery`, `recheck_no_openings`.

**Why:** Parent AST-1185 AC requires those identities as first-class catalog options. AST-960’s companion gates (picker omit + `dispatch_task_admin_defaults` `KeyError` + Admin `Unknown task_key`) are reversed for helper-resolvable hops so the form is not a dead end.

**Rejected alternative:** picker-yes / writer-no.

### Product call — `parse_meteorite_email` (Archie / Chuckles [check-linear] 2026-08-07)

**Call:** **No hiding.** Do **not** add `parse_meteorite_email` (or any meteorite mailbox identity) to `ADMIN_CONFIG` hidden dispatch keys. Do **not** filter it out of the picker. It is **not** an eighth gazer/inflow “gap key” to treat like `fetch_*`.

**What it is:** Misnamed live `agent_task` row for the meteorite mailbox / Ruth parse identity. Config already names the TASK_CONFIG key `meteorite_email` (`METEORITE_EMAIL_PARSE_CONFIG["task_key"]`, AST-1212). Archie: fold into `meteorite_email` / rename toward `catch_meteorite_email` — **candidate** entity; **Avail = Gmail inbox ping**; FOR-candidate messages → Ruth. Full seed rename may be absorbed by **AST-1182**; this ticket must not leave a Save dead-end on the live `parse_meteorite_email` row while that rename is pending.

**This ticket’s disposition:** Keep it in the live catalog (eighth agent_task-only key on this tip). Fold Admin defaults / write acceptance onto the meteorite mailbox contract via `METEORITE_EMAIL_PARSE_CONFIG` (canonical `task_key` + `legacy_agent_task_key`), with `admin_entity_type: "candidate"` and mailbox null claim fields parallel to `gaze_email`, plus Avail stamping via the same inbox bind counts as `gaze_email`. Do **not** invent a parallel hard-coded membership set in `api_admin.py`.

**Rejected (Joan escalate options 1 and 3):** Hide via `ADMIN_CONFIG`; ship picker-only 400.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/api/api_admin.py` | Expand `dispatch_task_keys` membership; `sorted(membership)`; form-meta gate admits `TASK_CONFIG` **or** `is_meteorite_email_mailbox_task_key`; `_dispatch_task_key_trigger_error` for helper-resolvable hops + mailbox null-only trigger; Avail at both `list_dtasks` sites (~863–867 and ~886) | ui |
| `src/utils/config.py` | Extend `dispatch_task_admin_defaults` for helper-resolvable non-`TASK_CONFIG` keys; extend `METEORITE_EMAIL_PARSE_CONFIG` with legacy agent_task key + admin mailbox fields; mailbox carve-out for canonical + legacy keys (`entity_type=candidate`, null trigger/sort); small `is_meteorite_email_mailbox_task_key` helper | utils |

**Side effects of the `dispatch_task_admin_defaults` change (same function — not new Files Changed rows):**

- `_ensure_dispatch_task_schema` — backfills entity/trigger/sort/batch_call_mode for newly resolvable keys (including folded meteorite mailbox). Expected.
- `get_dispatch_row_or_seed_preview_meta` → `/adhoc/entities` — 404→200 for keys that gain defaults. Betty note.

**Out of scope:**

| Owner | What |
|-------|------|
| AST-1215 (Katherine) | React section headers / dropdown UX |
| AST-1182 | Seed rename `parse_meteorite_email` → `meteorite_email` / `catch_meteorite_email`; AI payload work — may absorb rename; this ticket only folds Admin contract onto live key |
| AST-1183 / AST-1184 | Gaze/Meteorite seed groups; `master_task_key` resolve |
| Betty | Stage 3 contract; engineer does **not** edit `tests/` |

**Audit findings (do not re-litigate):**

- `GET /api/admin/tasks` already `ORDER BY task_key` + DB grouping — leave list order as-is.
- Vector-feedback task_keys = rubric owners only — do not expand.
- Retired / admin-hidden remain config-backed filters — **do not** put `parse_meteorite_email` in hidden.
- Jobs UI sections — out of epic Admin default scope.
- On current tip, **eight** agent_task-only keys (absent from `TASK_CONFIG`): `fetch_culture_pages`, `fetch_jd`, `fetch_job_pages`, `fetch_website`, `gaze`, `inflow_discovery`, `parse_meteorite_email`, `recheck_no_openings`. Of these, seven are helper-resolvable gazer/roster/inflow hops; `parse_meteorite_email` is the meteorite mailbox fold identity (product call above). `prefilter` / `inflow_resolve_website` are not agent_task keys — stay out of picker Done-when; writer may still accept them if POSTed (intentional).

## Execution contract

The plan is binding. Execute stages in order. Do not edit React, seed JSON rename (AST-1182), or `tests/`. Do **not** add `parse_meteorite_email` to `ADMIN_CONFIG` hidden lists. When blocked — comment on **AST-1185** with Stage N template.

---

## Stage 1: Live alphabetical Admin task-key catalog

**Done when:** `GET /api/admin/dispatch_tasks/task_keys` returns the sorted union of `get_task_keys()` ∪ `list_candidate_tasks()` keys ∪ non-retired `list_dispatch_tasks()` keys, minus hidden/retired; built with `sorted(membership)`; on this tip all **eight** agent_task-only keys above are present without a pre-existing `dispatch_task` row; aliases `meteorite_grade_do` / `meteorite_grade_get` present; each value carries form-meta fields.

1. Import `_dispatch_trigger_state_for_task_key` and `is_meteorite_email_mailbox_task_key` alongside `_dispatch_entity_type_for_task_key` in `api_admin.py` (Stage 2 also needs `GAZE_EMAIL_CONFIG` — already imported).

2. Add `_admin_dispatch_task_key_catalog()` as previously specified (union + `sorted(membership)` + `_dispatch_task_key_form_meta`).

3. Replace `dispatch_task_keys()` body to `return jsonify(_admin_dispatch_task_key_catalog())` with docstring matching this contract.

4. No frozenset of gap keys for membership. No change to `get_task_keys()`. **No** `ADMIN_CONFIG` hide of `parse_meteorite_email`.

⚠️ **Decision:** Reverse AST-960 picker omit for all current `agent_task` keys (including `parse_meteorite_email`). Keep `sorted(membership)`.

---

## Stage 2: Form-meta + first-class write path (helper-resolvable hops + meteorite mailbox fold)

**Done when:**

- Each of the **seven** helper-resolvable keys: form meta filled; `_dispatch_task_key_trigger_error` returns `None` for a valid trigger (e.g. `fetch_jd`/`PASSED_JOBLIST`, `inflow_discovery`/`ACTIVE_SEARCH`); `dispatch_task_admin_defaults` returns a dict; POST create succeeds for `fetch_jd`.
- `parse_meteorite_email` and `meteorite_email`: `dispatch_task_admin_defaults` returns mailbox defaults with `entity_type == "candidate"` and null `trigger_state` / `sort_by` / `batch_call_mode == 0`; form meta shows `entity_type: "candidate"` (mailbox carve-out reached via form-meta gate — edit 1); `_dispatch_task_key_trigger_error` returns `None` when trigger is null/empty and **rejects non-empty** trigger for mailbox keys (edit 3); POST create for `parse_meteorite_email` with a valid candidate and null/omitted `trigger_state` succeeds (201).
- Registered-but-unschedulable other `TASK_CONFIG` keys (e.g. craft_*) still get `unsupported entity_type` wording, not `Unknown task_key`.
- `list_dtasks` Avail for a `parse_meteorite_email` / `meteorite_email` row uses the same inbox bind-count path as `gaze_email` (Gmail ping), including both the snapshot gate and the per-row stamp (edit 2).

1. In `_dispatch_task_key_form_meta`, change the defaults gate from `if task_key in TASK_CONFIG:` to:

   ```python
   if task_key in TASK_CONFIG or is_meteorite_email_mailbox_task_key(task_key):
       try:
           derived = dispatch_task_admin_defaults(task_key)
           entity_type = derived["entity_type"] or ""
           trigger_state = (derived["trigger_state"] or "") if derived["trigger_state"] is not None else ""
       except KeyError:
           pass  # mid-chain / no default — keep prior field values
   ```

   Then keep the existing `_dispatch_*` fallback for empty entity/trigger (helper-resolvable gap keys only). Import `is_meteorite_email_mailbox_task_key` from config. Without this gate widen, `parse_meteorite_email` never hits the mailbox carve-out and form meta stays blank (Joan escalate fix-now).

2. `_dispatch_task_key_trigger_error` — after retired check, **mailbox trigger-null only** (reject non-empty; matches `gaze_email` row shape):

   ```python
   # Mailbox identities (gaze_email + meteorite fold) — accept before Unknown.
   if tk == GAZE_EMAIL_CONFIG["task_key"] or is_meteorite_email_mailbox_task_key(tk):
       ts = (trigger_state or "").strip()
       if ts:
           return (
               f"task_key {tk!r} is a mailbox poller; trigger_state must be null/empty "
               f"(got {trigger_state!r})"
           )
       return None

   try:
       et = _dispatch_entity_type_for_task_key(tk)
   except KeyError:
       if tk in TASK_CONFIG:
           return f"task_key {tk!r} has unsupported entity_type"
       return f"Unknown task_key: {tk!r}"
   # … existing trigger required + registry / hop validation …
   ```

   Import `GAZE_EMAIL_CONFIG`, `is_meteorite_email_mailbox_task_key` from config. Do **not** accept non-empty `CANDIDATE_STATES` triggers for mailbox keys.

3. In `METEORITE_EMAIL_PARSE_CONFIG` (`config.py`), add config-backed fold fields (no api_admin frozenset):

   ```python
   METEORITE_EMAIL_PARSE_CONFIG = {
       "task_key": "meteorite_email",
       "legacy_agent_task_key": "parse_meteorite_email",  # live seed name until AST-1182 rename
       "admin_entity_type": "candidate",  # Archie: candidate-bound; Avail = Gmail ping
       "parse_modes": ("html_links", "subject_body"),
   }
   ```

   Add:

   ```python
   def is_meteorite_email_mailbox_task_key(task_key: str) -> bool:
       tk = (task_key or "").strip()
       cfg = METEORITE_EMAIL_PARSE_CONFIG
       return tk == cfg["task_key"] or tk == cfg["legacy_agent_task_key"]
   ```

4. In `dispatch_task_admin_defaults`, after retired check:

   - If `is_meteorite_email_mailbox_task_key(tk)`: return  
     `{"entity_type": METEORITE_EMAIL_PARSE_CONFIG["admin_entity_type"], "trigger_state": None, "sort_by": None, "batch_call_mode": 0}`  
     (do this **before** the bare `tk not in TASK_CONFIG` raise, so legacy `parse_meteorite_email` works).
   - Keep existing `gaze_email` carve-out.
   - Then: if `tk not in TASK_CONFIG`, helper-resolvable path (revision 2 snippet) for the seven gazer/inflow hops.
   - Else existing TASK_CONFIG body.

5. In `list_dtasks`, extend **both** gaze_email Avail sites so meteorite mailbox keys share the Gmail inbox ping snapshot (do not hardcode `parse_meteorite_email` — use `is_meteorite_email_mailbox_task_key`):

   - **`api_admin.py` ~863–867** (`need_gaze_counts`): treat a row as needing the inbox snapshot when  
     `(task_key == gaze_tk or is_meteorite_email_mailbox_task_key(task_key))` **and** candidate_id is non-empty.  
     Otherwise `bound_counts` stays `{}` whenever no gaze_email row is present and every meteorite mailbox Avail silently stamps 0.
   - **`api_admin.py` ~886** (per-row stamp): same predicate — stamp `available_count` from `bound_counts` for gaze_email **or** meteorite mailbox keys.

6. No alias→master map for AST-1184 aliases. No seed rename of `parse_meteorite_email` in this ticket.

⚠️ **Decision:** Helper-resolvable hops = first-class writable. `parse_meteorite_email` = meteorite mailbox fold (config), not hidden, not a gazer gap key. AST-1182 may rename seed to `catch_meteorite_email` / fold fully into `meteorite_email`.

---

## Stage 3: Hardcode audit close-out + Betty contract

**Done when:** No new hard-coded membership/section inventories; no `ADMIN_CONFIG` hide of `parse_meteorite_email`; Stage 3 Linear comment includes Betty set below.

1–3. Diff audit as before (`api_admin.py` + `config.py`).

4. **Betty contract:**

   **A. Picker presence (`test_api_admin.py`):**  
   Flip `test_dispatch_task_keys_omits_fetch_jd_gap_excludes_retired` and `test_gap_key_absent_without_db_row`. Expect the **eight** agent_task-only keys present (seven helper-resolvable + `parse_meteorite_email`). Stay absent from picker: `prefilter`, `inflow_resolve_website`.

   **B. Admin validator:**  
   Flip `test_dispatch_task_key_trigger_error_candidate_paths` for `inflow_discovery` → accept. Add/adjust: `_dispatch_task_key_trigger_error("parse_meteorite_email", None|"" )` returns `None`; `_dispatch_task_key_trigger_error("parse_meteorite_email", "ACTIVE_SEARCH")` (and same for `meteorite_email` / `gaze_email`) **rejects** non-empty trigger (mailbox null-only). Form meta for `parse_meteorite_email` includes `entity_type: "candidate"`.

   **C. Config defaults (`test_config.py`):**  
   Flip KeyError expectations for helper-resolvable keys (`fetch_jd`, `fetch_job_pages`, `fetch_website`, `fetch_culture_pages`, `inflow_discovery`); `prefilter` / `inflow_resolve_website` → expect defaults dicts. Add: `dispatch_task_admin_defaults("parse_meteorite_email")` and `("meteorite_email")` return candidate mailbox defaults (not KeyError / not unsupported).

   **D. Keepers:** `unsupported entity_type` for craft_* etc.; other `task_keys` endpoint tests.

   **E. Harness:** patch `list_candidate_tasks`; raw-body alphabetical keys; POST `fetch_jd` + POST `parse_meteorite_email` (null trigger); optional `/adhoc/entities` 200; Avail path covers **both** `need_gaze_counts` (~863–867) and per-row stamp (~886) so meteorite mailbox Avail is non-zero when inbox binds exist even if no gaze_email row is present.

---

## Self-Assessment

**Scope:** `Single-Component` — Admin catalog + write/defaults in `api_admin.py` / `config.py`; meteorite mailbox fold via `METEORITE_EMAIL_PARSE_CONFIG`; no React; no seed rename (AST-1182).

**Conf:** `high` — Archie/Chuckles product call settles Joan escalate (no hide; fold mailbox identity); eight-key membership measured on tip; helpers already proven for the seven.

**Risk:** `Medium` — schedules gazer/inflow hops + meteorite mailbox under live `parse_meteorite_email` name until AST-1182 rename; Betty breadth spans Admin + config; Avail shares gaze_email inbox counts.

## CODE_RULES check

- §1.4 / no-hardcoded-sets — membership from live catalogs; mailbox fold keys in `METEORITE_EMAIL_PARSE_CONFIG`; **no** ADMIN_CONFIG hide list for parse.
- §2.1 / config-source-of-truth — defaults + mailbox contract in config.
- §2.9 / require-auth — `@require_admin` retained.
- §3.2 / ui-config-driven — membership, alpha, write, Avail resolved in API/config.
- in-scope-only — no React; no AST-1182 seed rename; Ad-hoc 404→200 noted as side effect.
- plan-is-bible — eighth key + no-hide + fold disposition explicit.

## Revisions

Revision 1 — 2026-08-07  
Driven by: Joan `[plan-discuss] round=1 concern`.  
Changes: First-class writable gap keys; seven-key Done-when; alpha premise; Betty pair + patch.

Revision 2 — 2026-08-07  
Driven by: Joan `[plan-discuss] round=2 concern`.  
Changes: Named scheduling product call; Betty breadth (test_config + Admin Unknown); wording keep; side effects; writer>picker note.

Revision 3 — 2026-08-07  
Driven by: Joan `[plan-discuss] escalate` (eighth key `parse_meteorite_email` Save dead-end) + Chuckles `[check-linear]` Archie product call (**no hiding**; misnamed — fold into `meteorite_email` / `catch_meteorite_email`; candidate; Avail=Gmail ping; AST-1182 may absorb rename).  
Changes: Membership corrected to **eight** agent_task-only keys; rejected ADMIN_CONFIG hide and picker-only 400; Stage 2 adds meteorite mailbox fold via `METEORITE_EMAIL_PARSE_CONFIG` (`legacy_agent_task_key`, `admin_entity_type=candidate`) + validator/defaults/Avail; Betty A–E updated for `parse_meteorite_email` / `meteorite_email`; seed rename left to AST-1182.

Revision 4 — 2026-08-07  
Driven by: Archie/Susan green-light on Joan escalate (round count reset) — apply all three plan edits.  
Changes: (1) `_dispatch_task_key_form_meta` gate admits `is_meteorite_email_mailbox_task_key(task_key)` so mailbox carve-out reaches form meta; (2) Stage 2 step 5 names both Avail sites `api_admin.py` ~863–867 (`need_gaze_counts`) and ~886 (per-row stamp); (3) mailbox `trigger_state` null-only — reject non-empty. Betty B/E updated accordingly.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1185/AST-1214-admin-catalog-api-hardcode-audit-alphabetical-task-key-lists`
**Plan path:** `docs/features/meteorite/ast-1214-admin-catalog-api-hardcode-audit-alphabetical-task-key-lists.md`

**Built tip:** `9d2e7629ba3f6bfaaadf6fe9853d552b57a32612` (`9d2e7629`)

| Stage | Commit | Summary |
|-------|--------|---------|
| 1–2 | `9d2e7629` | live alphabetical catalog + first-class write path (mailbox fold + Avail) |

## Radia review — [code-rubric] revision=1

**Rubric:** code-rubric.v1 · **Ticket:** AST-1214 · **Publish ref tip:** `b0f12360`

**Overall: CLEAN**

**What's solid:**

- `_admin_dispatch_task_key_catalog()` builds membership live from `get_task_keys()` ∪ `database.list_candidate_tasks()` ∪ non-retired `list_dispatch_tasks()`, minus hidden/retired, via `sorted(membership)` — no frozenset gap-key inventory anywhere in the diff. Verified: no `parse_meteorite_email` (or any mailbox key) literal in `api_admin.py`; the fold routes entirely through `is_meteorite_email_mailbox_task_key` / `METEORITE_EMAIL_PARSE_CONFIG`.
- `admin_hidden_dispatch_task_keys()` still reads an empty `ADMIN_CONFIG` (`hidden_dispatch_task_keys` key absent) — confirms the plan's "no hiding `parse_meteorite_email`" product call is honored, not just asserted in prose.
- `dispatch_task_admin_defaults` mailbox carve-out lands *before* the `tk not in TASK_CONFIG` raise (matches plan step 4 ordering exactly), so the legacy `parse_meteorite_email` key resolves without depending on TASK_CONFIG membership.
- `_dispatch_task_key_trigger_error` precedence flip (`_dispatch_entity_type_for_task_key` try/except before the bare `tk not in TASK_CONFIG` check) correctly reverses AST-960 for the seven helper-resolvable hops while preserving `unsupported entity_type` wording (vs `Unknown task_key`) for registered-but-unschedulable TASK_CONFIG keys like `craft_*`.
- Both `list_dtasks` Avail sites (`need_gaze_counts` gate and the per-row stamp) extended with the same `_inbox_avail_task_key` predicate — no drift between the two call sites.
- Git hygiene: engineer commit `9d2e7629` touches only `src/`; Betty's `4d4f56b4` touches only `tests/` + `docs/test-bible/**`; single `merge-tests(AST-1214)` commit `b0f12360` — clean role separation (`astral.git.engineer-test-tree-ban`, `astral.git.betty-no-src-or-features`, `orch.git.betty-merge-tests-one-sha` all conform).
- `python3 -m py_compile` clean on both touched files at tip.

**Full active-set sweep (63 statutes, in-session):** no `violates`. Two scoped-but-excluded-in-plan ids (`astral.seed.agent-tables-in-repo-json`, `astral.layers.import-direction`) predicate-match on `src/utils/config.py`/`src/**` but score `conforms` on inspection — no repo-JSON/bootstrap content touched, no new cross-layer imports, consistent with the plan's own exclusion rationale. No Joan plan-rubric verdict attachment found on the ticket (only Betty's QA manifest comment) — noting `no plan-rubric verdict attached` per C4; not a block.

**Pattern conformance:** `pattern.ui.admin-endpoint` — conforms (thin `@require_admin` route delegates to `_admin_dispatch_task_key_catalog`). `pattern.config.config-block` — conforms (defaults widened via `_dispatch_*` helpers + `dispatch_task_admin_defaults`, no inline Admin sets).

**Plan adherence:** Stage 1 and Stage 2 implementation matches the plan's own code snippets essentially verbatim (gate widen, trigger-error precedence, mailbox carve-out ordering, both Avail sites). Self-Assessment `Single-Component` / `high` conf scope holds — no React, no AST-1182 seed rename, no test-tree edits by the engineer.

## Frame diff

(none — ticket description/AC unchanged; findings are diff-only)

context_tokens≈65000

— Radia

## Resolution

**Date:** 2026-08-07  
**Review tip:** `4dcf7879` (`docs(AST-1214): Radia review — clean`) · product/tests tip `b0f12360`  
**Outcome:** CLEAN — no fix-now / discuss items. No product code changes on resolve.

Doc-only: dropped the duplicated Stage 2 Done-when bullet (Joan plan nit). Checklists already ticked from Code Complete; Frame diff none.
