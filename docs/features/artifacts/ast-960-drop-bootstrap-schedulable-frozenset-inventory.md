<!-- linear-archive: AST-960 archived 2026-08-02 -->

## Linear archive (AST-960)

**Archived:** 2026-08-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-960/drop-bootstrap-schedulable-frozenset-inventory-local-host-server  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-957 — Local host server doesn't load  
**Blocked by / blocks / related:** parent: AST-957; related: AST-856

### Description

## What this implements

Bootstrap no longer walks `DISPATCH_SCHEDULABLE_TASK_KEYS`; local boot is green; [AST-856](https://linear.app/astralcareermatch/issue/AST-856/check-cover-letter-not-recognized-as-a-valid-task-key) Save acceptance for registered catalog keys (e.g. `check_cover_letter`) stays unchanged; the frozenset is deleted or made non-gating for membership. Does not own gazer runtime fetch.

## Acceptance criteria

1. Clean local Flask launch stays up — no bootstrap error about a schedulable key missing from `TASK_CONFIG`.
2. Bootstrap no longer fails because a key is in `DISPATCH_SCHEDULABLE_TASK_KEYS` but not in `TASK_CONFIG`.
3. Scheduled Actions Save for `check_cover_letter` ([AST-856](https://linear.app/astralcareermatch/issue/AST-856/check-cover-letter-not-recognized-as-a-valid-task-key)) still succeeds.
4. Automated coverage: boot/coupling green without requiring the gap keys (`fetch_jd`, etc.) to be forced into `TASK_CONFIG` for bootstrap’s sake; [AST-856](https://linear.app/astralcareermatch/issue/AST-856/check-cover-letter-not-recognized-as-a-valid-task-key) Save regression remains.

## Boundaries

* Does not reverse [AST-856](https://linear.app/astralcareermatch/issue/AST-856/check-cover-letter-not-recognized-as-a-valid-task-key) / [AST-955](https://linear.app/astralcareermatch/issue/AST-955/align-scheduled-actions-save-with-task-key-picker-check-cover-letter) Save acceptance for registered catalog keys.
* Does not change gazer/roster/inflow runtime fetch behavior or retire/rename task keys.
* Does not stuff `fetch_jd` into `TASK_CONFIG` solely to appease the leftover frozenset inventory.
* Does not redesign Scheduled Actions UI beyond what removing the parallel inventory requires.

## Notes for planning

* [AST-955](https://linear.app/astralcareermatch/issue/AST-955/align-scheduled-actions-save-with-task-key-picker-check-cover-letter) plan Decision left `DISPATCH_SCHEDULABLE_TASK_KEYS` for bootstrap/form enrichment; this child finishes SoT cleanup — TASK_CONFIG is the membership rule.
* Hot files: `src/core/bootstrap.py`, `src/utils/config.py`, `src/ui/api/api_admin.py` (form enrichment).
* Config as source of truth (Code Rules §2.1).

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-957-local-host-server-doesnt-load`, child `sub/AST-957/<child-segment>`. Created at dispatch-parent. Publish to `origin/<sub-ref>` only.

### Comments

#### chuckles — 2026-07-23T04:02:24.259Z
[merge-child] blocked: missing plan(AST-960): on origin/sub/AST-957/AST-960-drop-bootstrap-schedulable-frozenset-inventory

Plan landed as `docs(AST-960): plan — …`; validate-sub-log requires `plan(AST-960):`. Add a `plan(AST-960):` commit on the publish ref (empty commit OK if plan doc already present) and push. Stay User Testing.

@Ada Lovelace

— Chuckles

#### radia — 2026-07-23T03:51:00.328Z
### Radia review — AST-960

**Diff:** `origin/dev...origin/sub/AST-957/AST-960-drop-bootstrap-schedulable-frozenset-inventory` (tip `c64566f`).

**Doc:** [Radia review — clean](https://github.com/susansomerset/astral/blob/c64566fe70545437ac3ebe291f9fc72144eb7c51/docs/features/artifacts/ast-960-drop-bootstrap-schedulable-frozenset-inventory.md)

**What’s solid:** Stages 1–3 match plan — bootstrap no longer inventories `DISPATCH_SCHEDULABLE_TASK_KEYS`; admin form/`task_keys` enrich from `TASK_CONFIG` + defaults only; frozenset deleted; scored-trigger helper walks scored `TASK_CONFIG`. Zero `DISPATCH_SCHEDULABLE_TASK_KEYS` under `src/`. Live Done-when: `NEW`/`PASSED_LIKE` True, `VALID_TITLE` False; `check_cover_letter` override intact; `fetch_jd ∉ TASK_CONFIG`.

**fix-now:** none

**discuss:** none

**Advisory:** `except KeyError: pass` in `_dispatch_task_key_form_meta` is plan-mandated mid-chain fallthrough with comment — acceptable under §5b.

#### betty — 2026-07-23T03:33:10.915Z
1. `./scripts/testing/run_component_tests.sh tests/component/core/test_bootstrap.py -q`
2. `./scripts/testing/run_component_tests.sh tests/component/utils/test_config.py::TestAst960DropSchedulableFrozensetInventory tests/component/utils/test_config.py::TestAst955RegisteredKeyDispatchAdminDefaults tests/component/utils/test_config.py::TestAst796FetchJdSchedulableCutover tests/component/utils/test_config.py::TestAst702PrefilterBatchConfig tests/component/utils/test_config.py::TestAst719FetchJobPagesConfig tests/component/utils/test_config.py::TestAst701FetchWebsiteConfig tests/component/utils/test_config.py::TestAst874FetchCulturePagesConfig tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig tests/component/utils/test_config.py::TestAst506InflowResolveConfig tests/component/utils/test_config.py::TestAst471DispatchConfigHelpers -q`
3. `./scripts/testing/run_component_tests.sh tests/component/ui/api/test_api_admin.py::TestAst796FetchJdRetiredDispatchKeys tests/component/ui/api/test_api_admin.py::TestAst960TaskKeysNoFrozensetInventory tests/component/ui/api/test_api_admin.py::TestAst955AlignScheduledActionsSave -q`

Broken / obsolete revised this pass: bootstrap frozenset-missing RuntimeError + monkeypatches; all `DISPATCH_SCHEDULABLE_TASK_KEYS` membership asserts; `dispatch_task_admin_defaults(<gap_key>)` without KeyError; `task_keys` frozenset merge expecting `fetch_jd` without a DB row.

`origin/sub/AST-957/AST-960-drop-bootstrap-schedulable-frozenset-inventory` @ `1658e32` (`merge-tests(AST-960): origin/tests 8bfe40fe1c6bc045d34e1fdbd5a05eaf716ef6a4`)

Bible shasum on publish tip:
- `docs/test-bible/README.md` `dbd34c82053978997ccd7bb1fea3c5e675f26e68544eb9141ff91ed610d6abfa`
- `docs/test-bible/core/bootstrap.md` `c25f4acda7191b90fc7a8db75bb884f112f143fbd53a952e01847b36123502a3`
- `docs/test-bible/ui/api/api_admin.md` `9017b9e1066e1df84b1d3eaa3f2c3f210d3074549056a6f1ce9602d8d10f2eec`
- `docs/test-bible/ui/server.md` `cbb938aaa118bea62f0a3067b9211e80639bffca38cecb767f3da5e0d1571819`
- `docs/test-bible/utils/config.md` `532b0c8839f2fd0c2b9ee04743568169dbf206b6fd9ed904c0170746ce5e882a`

— Betty

#### joan — 2026-07-23T02:58:13.593Z
**Verdict: APPROVED**

No `fix-now` findings. Plan is faithful to AST-957 / AST-960: delete `DISPATCH_SCHEDULABLE_TASK_KEYS`, stop bootstrap inventory over it, align admin form/`task_keys` enrichment with `TASK_CONFIG`, rewrite `trigger_state_used_by_scored_dispatch_task` to scored `TASK_CONFIG` keys. Boundaries honored (Save path untouched; no gap-key stuffing; no gazer runtime redesign; tests/bible left to Betty). Layer table and §2.1 SoT cleanup check out against live call sites. Self-assessment (Single-Component / high / Medium) matches the three coupled consumers and the latent scored-trigger KeyError on gap keys.

**[discuss]** — Stage 2 picker — Gap keys that exist only on the old frozenset (not in `TASK_CONFIG`, not on a DB row) leave the picker map. Plan Decision + parent Boundaries already own this; no revise needed — Ada should not reintroduce a parallel catalog for catalog completeness.

**[acceptable]** — AC4 / Betty handoff note — Automated coverage correctly deferred to Code Complete under engineer test-tree ban; parent Files-to-touch test rows are Betty’s, not Ada’s build scope.

## Considered and excluded
**Considered:** `astral.config.config-source-of-truth` — deletes second membership allowlist; TASK_CONFIG becomes sole catalog rule. `astral.standards.no-hardcoded-sets` — removes curated frozenset inventory used as required catalog. `astral.standards.in-scope-only` — stages stay on bootstrap / api_admin / config only. `astral.standards.dry-and-focused-functions` — single membership path, no replacement parallel set. `astral.layers.import-direction` — core/ui/utils edits respect import direction. `astral.layers.ui-config-driven-business-logic` — form enrichment stays in api_admin, config-driven. `astral.git.engineer-test-tree-ban` — product-only Files Changed; tests/bible to Betty. `orch.roles.betty-owns-test-tree` — AC4 handoff note correct. `astral.docs.features-single-file-per-ticket` — plan at docs/features/artifacts/ast-960-….md. `orch.pipeline.plan-is-bible` — execution contract present.

**Excluded:** `orch.git.*` — no topology/publish work in this child. `astral.batch.*` — no claim/process/release changes. `astral.state.*` — no state-transition redesign. `astral.agent.*` — no do_task / grade-vector work. `astral.patterns.coat-check-never-store-empty` — N/A. `astral.ui.frontend-file-placement` — no frontend files. `astral.patterns.require-auth-on-protected-endpoints` — auth surface unchanged. `orch.roles.chuckles-never-ticket-assignee` — orchestration role, not plan content.

context_tokens≈33500
— Joan

#### ada — 2026-07-23T02:48:32.464Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-957/AST-960-drop-bootstrap-schedulable-frozenset-inventory/docs/features/artifacts/ast-960-drop-bootstrap-schedulable-frozenset-inventory.md

**Scope:** Single-Component — bootstrap + api_admin form/`task_keys` + config frozenset deletion / scored-trigger rewrite; one SoT leftover from AST-955.

**Conf:** high — live gap list verified (`fetch_jd` and 8 other frozenset keys ∉ TASK_CONFIG); Save path already TASK_CONFIG-only.

**Risk:** Medium — scored-trigger helper and picker enrichment change for gap keys; claim floor + AST-856 Save untouched; Betty owns test/bible AC4.

---

# AST-960 — Drop bootstrap schedulable-frozenset inventory (Local host server doesn't load)

- **Linear:** [AST-960](https://linear.app/astralcareermatch/issue/AST-960/drop-bootstrap-schedulable-frozenset-inventory-local-host-server)
- **Parent:** [AST-957](https://linear.app/astralcareermatch/issue/AST-957/local-host-server-doesnt-load)
- **Publish ref:** `origin/sub/AST-957/AST-960-drop-bootstrap-schedulable-frozenset-inventory`

Local Flask dies at `bootstrap_runtime()` because `_validate_runtime_coupling` still walks `DISPATCH_SCHEDULABLE_TASK_KEYS` and requires each key to resolve via `dispatch_task_admin_defaults` → `TASK_CONFIG`. After AST-955, defaults membership is `TASK_CONFIG` only, but the frozenset still lists gazer/roster/inflow keys (`fetch_jd`, `prefilter`, `gaze`, …) that are **not** in `TASK_CONFIG` — so boot raises `RuntimeError: bootstrap: dispatch schedulable key 'fetch_jd' missing from TASK_CONFIG`. This ticket finishes the SoT cleanup AST-955 deferred: delete the parallel inventory and stop treating it as a required catalog for bootstrap or form enrichment.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/bootstrap.py` | Remove `DISPATCH_SCHEDULABLE_TASK_KEYS` inventory loop and import; keep `TASK_CONFIG` / LLM env coupling only | core |
| `src/ui/api/api_admin.py` | Stop importing / iterating the frozenset in form meta and `task_keys`; enrich from `dispatch_task_admin_defaults` when the key is in `TASK_CONFIG` and defaults resolve | ui |
| `src/utils/config.py` | Delete `DISPATCH_SCHEDULABLE_TASK_KEYS`; rewrite `trigger_state_used_by_scored_dispatch_task` to walk scored `TASK_CONFIG` keys (not the frozenset) | utils |

**Out of scope (do not touch):** `tests/` / `docs/test-bible/**` (Betty owns AC4 coverage at Code Complete); stuffing `fetch_jd` / other gap keys into `TASK_CONFIG`; gazer/roster/inflow **runtime** fetch behavior; Save path / `_dispatch_task_key_trigger_error` / `save_dispatch_task` (AST-856 / AST-955 already use registered-key membership); frontend picker UI redesign; `DISPATCH_RETIRED_TASK_KEYS`; `_DISPATCH_COMPANY_ENTITY_TASK_KEYS` / per-key trigger branches used only as derivation helpers.

## Root cause (verified on this branch)

1. `src/core/bootstrap.py` `_validate_runtime_coupling` loops `DISPATCH_SCHEDULABLE_TASK_KEYS` and calls `dispatch_task_admin_defaults(key)` when `key not in TASK_CONFIG`.
2. `dispatch_task_admin_defaults` (post AST-955) raises `KeyError` when `tk not in TASK_CONFIG`.
3. Live gap (schedulable ∩ ¬TASK_CONFIG): `fetch_jd`, `fetch_culture_pages`, `fetch_job_pages`, `fetch_website`, `gaze`, `inflow_discovery`, `inflow_resolve_website`, `prefilter`, `recheck_no_openings`.
4. Susan’s traceback is exactly that path for `fetch_jd`.
5. AST-955 plan Decision explicitly left the frozenset for bootstrap / form enrichment; this child reverses that leftover.
6. Latent: `trigger_state_used_by_scored_dispatch_task` still iterates the frozenset and calls `dispatch_task_admin_defaults` — same KeyError on gap keys (e.g. `prefilter`). Must be rewritten when the frozenset is deleted.

## Stage 1: Bootstrap — TASK_CONFIG coupling only

**Done when:** `_validate_runtime_coupling()` no longer imports or references `DISPATCH_SCHEDULABLE_TASK_KEYS`. With a normal local `TASK_CONFIG` and valid LLM env, calling `_validate_runtime_coupling()` does not raise about `fetch_jd` (or any other gap key). Empty `get_task_keys()` and orphan-key-vs-`TASK_CONFIG` failures still raise as today.

1. In `src/core/bootstrap.py`, remove `DISPATCH_SCHEDULABLE_TASK_KEYS` and `dispatch_task_admin_defaults` from the `src.utils.config` import list (keep `TASK_CONFIG`, `get_task_keys`, `validate_llm_provider_environment`).
2. In `_validate_runtime_coupling`, **delete** the entire second loop:

```python
for key in DISPATCH_SCHEDULABLE_TASK_KEYS:
    if key in TASK_CONFIG:
        continue
    try:
        dispatch_task_admin_defaults(key)
    except KeyError as exc:
        raise RuntimeError(
            f"bootstrap: dispatch schedulable key {key!r} missing from TASK_CONFIG"
        ) from exc
```

Leave the LLM env check and the `get_task_keys()` / `TASK_CONFIG` membership loop unchanged. Do not add replacement inventory over any other set.

⚠️ **Decision:** Do **not** add gap keys to `TASK_CONFIG` to keep the old inventory green. Parent forbids that direction; membership for registered tasks is `TASK_CONFIG` alone.

## Stage 2: Admin form enrichment — no frozenset catalog

**Done when:** `GET /api/admin/dispatch_tasks/task_keys` builds its map from `get_task_keys()` + existing non-retired `list_dispatch_tasks()` rows only (no loop over `DISPATCH_SCHEDULABLE_TASK_KEYS`). `_dispatch_task_key_form_meta("grade_do")` still returns derived `entity_type` / `trigger_state` from `dispatch_task_admin_defaults`. `_dispatch_task_key_form_meta("check_cover_letter")` still returns without inventing a default trigger (KeyError from defaults → fall through to `TASK_CONFIG` fields). Module no longer imports `DISPATCH_SCHEDULABLE_TASK_KEYS`.

1. In `src/ui/api/api_admin.py`, remove `DISPATCH_SCHEDULABLE_TASK_KEYS` from the `src.utils.config` import block.
2. Rewrite `_dispatch_task_key_form_meta` enrichment as follows (keep grouping via `dispatch_task_grouping_catalog_key` and `_catalog_task_grouping_meta` unchanged):
   - Resolve `catalog_key`, `grouping_key`, and initial `entity_type` / `trigger_state` from `TASK_CONFIG` exactly as today (before the frozenset branch).
   - **Replace** `if task_key in DISPATCH_SCHEDULABLE_TASK_KEYS: derived = dispatch_task_admin_defaults(task_key); …` with:
     - If `task_key in TASK_CONFIG`:
       - `try: derived = dispatch_task_admin_defaults(task_key)` then set `entity_type` / `trigger_state` from `derived`.
       - `except KeyError:` leave the already-read `TASK_CONFIG` field values (covers mid-chain keys with no default trigger, e.g. `check_cover_letter` without override).
     - If `task_key not in TASK_CONFIG`: do not call defaults (DB-only / gap keys use the field values already set, which may be empty — DB-row merge in `dispatch_task_keys` still supplies row entity/trigger).
3. In `dispatch_task_keys`, **delete** the merge loop:

```python
for tk in DISPATCH_SCHEDULABLE_TASK_KEYS:
    if tk not in seen:
        seen[tk] = _dispatch_task_key_form_meta(tk)
```

Keep the `get_task_keys()` loop, the `list_dispatch_tasks()` row merge, and the hidden/retired pops unchanged.

⚠️ **Decision:** Gap keys that exist only on the old frozenset (not in `TASK_CONFIG`, not on a DB row) disappear from the picker map. That is intentional — parent forbids stuffing them into `TASK_CONFIG` for catalog completeness. Existing `dispatch_task` rows for those keys still appear via the DB-row loop.

## Stage 3: Config — delete frozenset; fix scored-trigger helper

**Done when:** `DISPATCH_SCHEDULABLE_TASK_KEYS` is gone from `src/utils/config.py` (definition and all references in `src/`). `trigger_state_used_by_scored_dispatch_task("NEW")` is `True` (via `qualify_job_listings` defaults). `trigger_state_used_by_scored_dispatch_task("PASSED_LIKE")` is `True`. `trigger_state_used_by_scored_dispatch_task("VALID_TITLE")` is `False` (qualify default trigger is `NEW`, not `VALID_TITLE`). Calling the helper does not raise `KeyError` on gap keys. `dispatch_task_admin_defaults("check_cover_letter", trigger_state="CANDIDATE_REVIEW")` still succeeds (AST-856 / AST-955 Save path unchanged).

1. In `src/utils/config.py`, **delete** the entire `DISPATCH_SCHEDULABLE_TASK_KEYS = frozenset({...})` block and its preceding comment (`# task_key values that may appear on dispatch_task rows …`).
2. Rewrite `trigger_state_used_by_scored_dispatch_task` so the frozenset loop is gone. Keep the `None` / blank / `*_RETRY` early returns and the final `_TRANSITION_STATES_USED_BY_SCORED_TASKS` fallback. Replace the middle loop with:

```python
for dk, tc in TASK_CONFIG.items():
    if not tc.get("scored"):
        continue
    try:
        defaults = dispatch_task_admin_defaults(dk)
    except KeyError:
        continue
    if defaults["trigger_state"] == ts:
        return True
```

Do **not** change `dispatch_claim_uses_score_floor`, `_TRANSITION_STATES_USED_BY_SCORED_TASKS`, or `dispatch_task_admin_defaults` membership (already `TASK_CONFIG`).

3. Grep `src/` for `DISPATCH_SCHEDULABLE_TASK_KEYS` — zero hits after Stages 1–3. Do not edit `tests/` or bible if grep finds them there (Betty).

⚠️ **Decision:** Delete the frozenset rather than leave an unused / empty constant. Ticket allows “deleted or made non-gating”; deletion removes the parallel catalog so it cannot regate bootstrap later.

## Betty handoff note (not Ada work)

Expect Betty to adjust at Code Complete (do **not** edit these in build-child):

- `tests/component/core/test_bootstrap.py` — remove cases that assert frozenset-missing → RuntimeError; drop monkeypatches of `DISPATCH_SCHEDULABLE_TASK_KEYS`.
- `tests/component/utils/test_config.py` — drop / rewrite assertions that require `DISPATCH_SCHEDULABLE_TASK_KEYS` membership or frozenset ⊆ `TASK_CONFIG`; keep AST-856 / AST-955 Save + `dispatch_task_admin_defaults` registered-key coverage.
- `tests/component/ui/api/test_api_admin.py` — keep `check_cover_letter` Save regression; adjust any frozenset-inventory / merge assertions.
- Bible rows under `docs/test-bible/utils/config.md` and `docs/test-bible/ui/api/api_admin.md` that still describe frozenset as bootstrap inventory.

## Execution contract

The plan is binding. Execute stages in order. Do not add files, restore the frozenset, or put gap keys into `TASK_CONFIG`. On ambiguity or codebase drift, stop and comment the parent with the Stage N blocked template — no improvisation.

## Self-Assessment

**Scope:** Single-Component — three tightly coupled call sites (`bootstrap`, `api_admin` form meta/`task_keys`, `config` frozenset + scored-trigger helper) finishing one SoT cleanup; no dispatcher/gazer runtime redesign.

**Conf:** high — root cause and live gap list verified on this branch; AST-955 already moved Save membership to `TASK_CONFIG`; this plan only removes the leftover inventory consumers and the constant.

**Risk:** Medium — `trigger_state_used_by_scored_dispatch_task` and picker enrichment change behavior for gap keys, but Save (AST-856) and claim floor (`dispatch_claim_uses_score_floor`) stay on existing paths; wrong rewrite could mis-label scored triggers until Betty’s suite catches it.

## Self-review vs ASTRAL_CODE_RULES

| Rule | Status |
|------|--------|
| §1.3 DRY | Single membership rule (`TASK_CONFIG`); no new parallel set |
| §2.1 config SoT | Deletes second curated allowlist; derivation helpers for known dispatch keys remain in config |
| §2.4 batch | Untouched |
| §2.6 state machine | Untouched |
| §3.3 imports | Bootstrap/admin drop frozenset import; no new cross-layer imports |
| §3.5 naming | No new public names; delete one constant |
| Test-tree ban | Product files only; Betty owns test/bible AC4 |

## Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-957/AST-960-drop-bootstrap-schedulable-frozenset-inventory`  
**Tip:** `92b9c0e`

**Stages delivered:**
- Stage 1 — `f7e3aa9` — bootstrap drops `DISPATCH_SCHEDULABLE_TASK_KEYS` inventory loop
- Stage 2 — `b61de9d` — `api_admin` form/`task_keys` enrich from `TASK_CONFIG` + defaults; no frozenset merge
- Stage 3 — `92b9c0e` — delete `DISPATCH_SCHEDULABLE_TASK_KEYS`; `trigger_state_used_by_scored_dispatch_task` walks scored `TASK_CONFIG`

**Betty:** test/bible AC4 per plan handoff note (not in this build).

## Radia review (2026-07-23)

**Diff:** `origin/dev...origin/sub/AST-957/AST-960-drop-bootstrap-schedulable-frozenset-inventory` (tip `1658e32` incl. Betty `merge-tests` / `test()`).

### What’s solid

| Area | Notes |
| --- | --- |
| Plan fidelity | Stages 1–3 match commits: bootstrap drops frozenset inventory loop; `api_admin` enrich/`task_keys` from `TASK_CONFIG` + defaults (no frozenset merge); `DISPATCH_SCHEDULABLE_TASK_KEYS` deleted; `trigger_state_used_by_scored_dispatch_task` walks scored `TASK_CONFIG`. |
| SoT / §2.1 | Zero `DISPATCH_SCHEDULABLE_TASK_KEYS` under `src/`. Gap keys stay out of `TASK_CONFIG`. Save / `dispatch_task_admin_defaults` membership unchanged. |
| Done-when checks | Live: `trigger_state_used_by_scored_dispatch_task("NEW")` / `("PASSED_LIKE")` True; `("VALID_TITLE")` False; `check_cover_letter` override still works; `fetch_jd ∉ TASK_CONFIG`. |
| Boundaries | No gazer/roster runtime redesign; Betty test/bible AC4 in tip as expected at Tests Passed. Scope matches Self-Assessment (Single-Component). |
| Rubric | §5a: `except KeyError: pass` in form meta has plan-mandated comment (mid-chain fallthrough) — acceptable §5b. §5f/§5g N/A. |

### Issues

None (**fix-now** / **discuss**).

### Recommended actions

| Severity | Item |
| --- | --- |
| — | None |

**Verdict:** Clean — `resolve-child` may proceed (no product fixes required beyond this `docs()` commit).

## Resolution

**Resolved:** 2026-07-23 (Ada)

- Radia **fix-now:** none · **discuss:** none · advisory KeyError fallthrough left as-is (plan-mandated).
- No product delta this pass. Radia `docs(AST-960): Radia review — clean` @ `c64566f` already on publish tip via §4 merge.
- §9a dry-run vs `origin/dev` and `origin/ftr/AST-957-local-host-server-doesnt-load` before User Testing.
