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
