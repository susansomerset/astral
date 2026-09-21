# AST-957 — Local host server doesn't load
**Component:** artifacts  
**Children:** AST-960
**Linear archived:** AST-957 2026-08-02; AST-960 2026-08-02

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-07-22 19:48 | AST-960 | docs | `af497d6a2` | docs(AST-960): plan — drop bootstrap schedulable-frozenset inventory |
| 2026-07-22 20:18 | AST-960 | code | `92b9c0ed4` | code(AST-960): delete DISPATCH_SCHEDULABLE_TASK_KEYS; scored-trigger via TASK_CONFIG |
| 2026-07-22 20:18 | AST-960 | code | `b61de9d65` | code(AST-960): form/task_keys enrich from TASK_CONFIG only |
| 2026-07-22 20:18 | AST-960 | code | `f7e3aa92d` | code(AST-960): drop bootstrap schedulable-frozenset inventory |
| 2026-07-22 20:19 | AST-960 | docs | `8a8da8aa9` | docs(AST-960): review stub after build stages |
| 2026-07-22 20:32 | AST-960 | merge-tests | `1658e323e` | merge-tests(AST-960): origin/tests 8bfe40fe1 |
| 2026-07-22 20:32 | AST-960 | test | `8bfe40fe1` | test(AST-960): drop frozenset inventory coverage; TASK_CONFIG catalog only |
| 2026-07-22 20:50 | AST-960 | docs | `c64566fe7` | docs(AST-960): Radia review — clean |
| 2026-07-22 21:01 | AST-960 | resolve | `ec30cbc2e` | resolve(AST-960): — clean |
| 2026-07-22 21:02 | AST-960 | plan | `b6352407b` | plan(AST-960): drop bootstrap schedulable-frozenset inventory |
| 2026-07-22 21:03 | AST-957 | prep-uat | `4bfa575b4` | prep-uat(AST-957): rebuild merge ticket log |
| 2026-08-02 09:37 | AST-957 | docs | `f63943442` | docs(AST-957): archive Linear issue content |
| 2026-08-02 09:37 | AST-960 | docs | `659aa0c05` | docs(AST-960): archive Linear issue content |
| 2026-08-07 04:12 | AST-960 | test | `4d4f56b47` | test(AST-1214): live Admin catalog alpha + writable helper/mailbox defaults |

_Last row is reachable from the `AST-960` grep (body reference); it is an AST-1214 test commit, not AST-960 work._

## Epic — AST-957
_Archived: 2026-08-02 · Linear URL: https://linear.app/astralcareermatch/issue/AST-957/local-host-server-doesnt-load · Status at archive: Archive · Project: Astral Artifacts · Assignee: chuckles · Priority / estimate: Urgent / — · Blocked by / blocks / related: —_

### Purpose

Local Flask will not boot because `bootstrap` still inventories `DISPATCH_SCHEDULABLE_TASK_KEYS` and requires each of those keys to resolve via `dispatch_task_admin_defaults` → `TASK_CONFIG`. AST-856 / AST-955 removed that frozenset as the **Save** membership gate and made `TASK_CONFIG` the Save/SoT rule — but the written AST-955 decision **left the frozenset intact for bootstrap / form enrichment**. That leftover parallel list is why `fetch_jd` (present on the frozenset, absent from `TASK_CONFIG`) still kills local start. This epic finishes the SoT cleanup: bootstrap must not depend on a second curated allowlist.

### Functional scope

* Stop bootstrap runtime coupling from requiring membership in / successful defaults for every key in `DISPATCH_SCHEDULABLE_TASK_KEYS`.
* Local Flask starts cleanly without adding gazer/roster keys to `TASK_CONFIG` solely to appease that leftover inventory loop.
* Retire or narrow remaining uses of `DISPATCH_SCHEDULABLE_TASK_KEYS` that reintroduce a second membership rule (bootstrap inventory; admin form enrichment only if it still treats the frozenset as a required catalog). Prefer `TASK_CONFIG` (and existing per-key helpers / request trigger) as the single membership rule — consistent with AST-856.
* Preserve AST-856 Save behavior: any registered catalog key (e.g. `check_cover_letter`) still saves when outside any former "schedulable" set.

### Boundaries

* Does **not** reverse AST-856 / AST-955 Save acceptance for registered catalog keys.
* Does **not** change gazer/roster/inflow **runtime** fetch behavior or retire/rename task keys.
* Does **not** mean "stuff `fetch_jd` into `TASK_CONFIG` so the old frozenset stays happy" — that was the wrong direction.
* Does **not** redesign Scheduled Actions UI beyond what removing the parallel inventory requires.
* Config remains source of truth (Code Rules §2.1).

### Acceptance criteria

1. Clean local Flask launch stays up — no bootstrap error about a schedulable key missing from `TASK_CONFIG`.
2. Bootstrap no longer fails because a key is in `DISPATCH_SCHEDULABLE_TASK_KEYS` but not in `TASK_CONFIG`.
3. Scheduled Actions Save for `check_cover_letter` (AST-856) still succeeds.
4. Automated coverage: boot/coupling green without requiring the gap keys (`fetch_jd`, etc.) to be forced into `TASK_CONFIG` for bootstrap's sake; AST-856 Save regression remains.

### Dependencies and blockers

* AST-856 / AST-955 (User Testing): Save gate removed; frozenset **intentionally** kept for bootstrap/form enrichment in the AST-955 plan — this epic owns finishing or reversing that leftover.
* none otherwise.

### Open questions

none.

### Schedulable list status (answer to Susan)

* AST-856 removed using `DISPATCH_SCHEDULABLE_TASK_KEYS` as the **Save** allowlist — it did **not** delete the frozenset from config.
* AST-955 plan Decision (explicit): leave the frozenset for **bootstrap inventory** and form enrichment; only stop using it as Save membership.
* So: not fully removed; **kept on purpose in that ticket's scope**. Persistence in bootstrap is exactly that scoped leftover — and yes, relative to "`TASK_CONFIG` is the only membership rule," that leftover is what we missed finishing. The crash list is still that frozenset in `src/utils/config.py`, consumed by `src/core/bootstrap.py`.

### Files to touch

| File | Why |
| -- | -- |
| `src/core/bootstrap.py` | Stop inventory loop over `DISPATCH_SCHEDULABLE_TASK_KEYS` (or replace with TASK_CONFIG-only coupling). |
| `src/utils/config.py` | Delete or narrow `DISPATCH_SCHEDULABLE_TASK_KEYS` and any helpers that still treat it as a required second catalog. |
| `src/ui/api/api_admin.py` | Form enrichment still references the frozenset — align with TASK_CONFIG-only rule. |
| `tests/component/utils/test_config.py` | Drop/adjust assertions that require schedulable frozenset ⊆ TASK_CONFIG for boot. |
| `tests/component/ui/api/test_api_admin.py` | Keep AST-856 Save regression; adjust any frozenset-inventory tests. |

### Proposed child tickets

| # | Working title | What it delivers | Agent | Sequencing |
| -- | -- | -- | -- | -- |
| 1 | Drop bootstrap schedulable-frozenset inventory | Bootstrap no longer walks `DISPATCH_SCHEDULABLE_TASK_KEYS`; local boot green; AST-856 Save unchanged; frozenset deleted or non-gating. Does not own gazer runtime fetch. | Ada | — |

Monolith check: Functional scope has 4 capabilities; one child intentional — bootstrap + frozenset retirement + AST-856 regression ship atomically for "server loads."

### Original brief

```
flask-api http://localhost:5001 (Ctrl-C to stop)
tip: vite live-reload at http://localhost:5173 — launch.sh --vite
Stytch auth configured: env=test project_id=project-test-3c7ad997-81ae-4ca1-…
Traceback (most recent call last):
  File "/Users/susan/chuckles/astral/src/core/bootstrap.py", line 38, in _validate_runtime_coupling
    dispatch_task_admin_defaults(key)
  File "/Users/susan/chuckles/astral/src/utils/config.py", line 1530, in dispatch_task_admin_defaults
    raise KeyError(f"dispatch_task_admin_defaults: unknown task_key {tk!r}")
KeyError: "dispatch_task_admin_defaults: unknown task_key 'fetch_jd'"

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/Users/susan/chuckles/astral/src/ui/server.py", line 65, in <module>
    bootstrap_runtime()
  File "/Users/susan/chuckles/astral/src/core/bootstrap.py", line 46, in bootstrap_runtime
    _validate_runtime_coupling()
  File "/Users/susan/chuckles/astral/src/core/bootstrap.py", line 40, in _validate_runtime_coupling
    raise RuntimeError(
RuntimeError: bootstrap: dispatch schedulable key 'fetch_jd' missing from TASK_CONFIG
```

#### Comments

_Chronological (source lists newest first)._

##### chuckles — 2026-07-23T00:38:42.029Z
@susan

1. Coupling direction — **(A)** register the schedulable-but-catalog-missing keys in the task catalog so one membership rule covers Save + bootstrap, or **(B)** keep them outside the catalog and restore bootstrap/admin-default resolution for schedulable-only keys without weakening AST-856 Save acceptance for catalog-only keys like `check_cover_letter`?
2. Project home — **Astral Roster**, **Astral Foundation**, or **Astral Artifacts**?

##### susan — 2026-07-23T00:43:15.260Z
@chuckles I think you're going the wrong way here. If boot is failing because it's looking for fetch_jd in a canonical config list, then that was missed from the scope of AST-856 to remove the redundant check-safes versus using the task_config array as the source of truth.

##### chuckles — 2026-07-23T00:47:36.389Z
[check-linear] Discussion — definition rewritten as AST-856 catalog SoT completion (register missed schedulable keys); waiting Todo (@susan)

_(This "register missed schedulable keys" direction is the one Susan's comment above rejects; the definition later flips to removing the bootstrap inventory instead.)_

##### susan — 2026-07-23T00:56:23.594Z
Help me understand the distinction between "schedulable" and "registered"? That sounds synonymy. Specifically, list in the issue description the files that need to be touched. _(repeated 2026-07-23T01:40:05)_

##### chuckles — 2026-07-23T02:15:16.760Z
[check-linear] Discussion — schedulable≠registered; files listed in description (@susan)

##### susan — 2026-07-23T02:19:26.476Z
@chuckles Thanks, but what list is bootstrap.py working from that it's getting the fetch* tasks?

##### chuckles — 2026-07-23T02:21:53.600Z
Bootstrap walks **`DISPATCH_SCHEDULABLE_TASK_KEYS`** from `src/utils/config.py` (imported in `bootstrap.py` → `_validate_runtime_coupling`). The `fetch_*` names come from that frozenset — not from GAZER scan. Each schedulable key not in `TASK_CONFIG` then hits `dispatch_task_admin_defaults` and blows up.

##### susan — 2026-07-23T02:30:47.343Z
@chuckles Once again, didn't we EXPLICITLY remove DISPATCH_SCHEDULABLE_TASK_KEYS as a list from config? Why would it need to persist in bootstrap? Did we miss it in the scoping of the ticket?

##### chuckles — 2026-07-23T02:32:54.373Z
AST-856 did **not** delete `DISPATCH_SCHEDULABLE_TASK_KEYS` — it stopped using it as the **Save** gate. AST-955's written Decision **kept** the frozenset for bootstrap / form enrichment. That's why bootstrap still walks it and why `fetch_jd` on that list (not in `TASK_CONFIG`) kills boot.

Relative to "TASK_CONFIG is the only membership rule," yes — finishing that leftover was out of AST-856 scope and belongs here. Definition flipped: **remove bootstrap's frozenset inventory**, not stuff `fetch_*` into `TASK_CONFIG`.

##### chuckles — 2026-07-23T02:45:02.693Z
[check-linear] Todo — frozenset still in config+bootstrap; waiting OQ1 (@susan). Confirm OQ1 (drop frozenset inventory vs register missing keys).

### Files changed (plan vs actual)

_No product commit trail on the parent — the one `prep-uat(AST-957)` commit rebuilds the merge ticket log; implementation landed via AST-960._

_Implementation detail may live in git history on `origin/dev`._

## Sub-issues

### AST-960 — Drop bootstrap schedulable-frozenset inventory
_Archived: 2026-08-02 · Linear URL: https://linear.app/astralcareermatch/issue/AST-960/drop-bootstrap-schedulable-frozenset-inventory-local-host-server · Status at archive: Archive · Project: Astral Artifacts · Assignee: ada · Priority / estimate: None / — · Blocked by / blocks / related: parent: AST-957; related: AST-856_

#### What this implements

Bootstrap no longer walks `DISPATCH_SCHEDULABLE_TASK_KEYS`; local boot is green; AST-856 Save acceptance for registered catalog keys (e.g. `check_cover_letter`) stays unchanged; the frozenset is deleted or made non-gating for membership. Does not own gazer runtime fetch.

#### Acceptance criteria

1. Clean local Flask launch stays up — no bootstrap error about a schedulable key missing from `TASK_CONFIG`.
2. Bootstrap no longer fails because a key is in `DISPATCH_SCHEDULABLE_TASK_KEYS` but not in `TASK_CONFIG`.
3. Scheduled Actions Save for `check_cover_letter` (AST-856) still succeeds.
4. Automated coverage: boot/coupling green without requiring the gap keys (`fetch_jd`, etc.) to be forced into `TASK_CONFIG` for bootstrap's sake; AST-856 Save regression remains.

#### Boundaries

* Does not reverse AST-856 / AST-955 Save acceptance for registered catalog keys.
* Does not change gazer/roster/inflow runtime fetch behavior or retire/rename task keys.
* Does not stuff `fetch_jd` into `TASK_CONFIG` solely to appease the leftover frozenset inventory.
* Does not redesign Scheduled Actions UI beyond what removing the parallel inventory requires.

#### Notes for planning

* AST-955 plan Decision left `DISPATCH_SCHEDULABLE_TASK_KEYS` for bootstrap/form enrichment; this child finishes SoT cleanup — TASK_CONFIG is the membership rule.
* Hot files: `src/core/bootstrap.py`, `src/utils/config.py`, `src/ui/api/api_admin.py` (form enrichment).
* Config as source of truth (Code Rules §2.1).

#### Root cause (verified on this branch)

1. `src/core/bootstrap.py` `_validate_runtime_coupling` loops `DISPATCH_SCHEDULABLE_TASK_KEYS` and calls `dispatch_task_admin_defaults(key)` when `key not in TASK_CONFIG`.
2. `dispatch_task_admin_defaults` (post AST-955) raises `KeyError` when `tk not in TASK_CONFIG`.
3. Live gap (schedulable ∩ ¬TASK_CONFIG): `fetch_jd`, `fetch_culture_pages`, `fetch_job_pages`, `fetch_website`, `gaze`, `inflow_discovery`, `inflow_resolve_website`, `prefilter`, `recheck_no_openings`.
4. Susan's traceback is exactly that path for `fetch_jd`.
5. AST-955 plan Decision explicitly left the frozenset for bootstrap / form enrichment; this child reverses that leftover.
6. Latent: `trigger_state_used_by_scored_dispatch_task` still iterates the frozenset and calls `dispatch_task_admin_defaults` — same KeyError on gap keys (e.g. `prefilter`). Must be rewritten when the frozenset is deleted.

#### Stage 1: Bootstrap — TASK_CONFIG coupling only

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

#### Stage 2: Admin form enrichment — no frozenset catalog

**Done when:** `GET /api/admin/dispatch_tasks/task_keys` builds its map from `get_task_keys()` + existing non-retired `list_dispatch_tasks()` rows only (no loop over `DISPATCH_SCHEDULABLE_TASK_KEYS`). `_dispatch_task_key_form_meta("grade_do")` still returns derived `entity_type` / `trigger_state` from `dispatch_task_admin_defaults`. `_dispatch_task_key_form_meta("check_cover_letter")` still returns without inventing a default trigger (KeyError from defaults → fall through to `TASK_CONFIG` fields). Module no longer imports `DISPATCH_SCHEDULABLE_TASK_KEYS`.

1. In `src/ui/api/api_admin.py`, remove `DISPATCH_SCHEDULABLE_TASK_KEYS` from the `src.utils.config` import block.
2. Rewrite `_dispatch_task_key_form_meta` enrichment (keep grouping via `dispatch_task_grouping_catalog_key` and `_catalog_task_grouping_meta` unchanged):
   - Resolve `catalog_key`, `grouping_key`, and initial `entity_type` / `trigger_state` from `TASK_CONFIG` exactly as today (before the frozenset branch).
   - **Replace** `if task_key in DISPATCH_SCHEDULABLE_TASK_KEYS: derived = dispatch_task_admin_defaults(task_key); …` with:
     - If `task_key in TASK_CONFIG`: `try: derived = dispatch_task_admin_defaults(task_key)` then set `entity_type` / `trigger_state` from `derived`; `except KeyError:` leave the already-read `TASK_CONFIG` field values (covers mid-chain keys with no default trigger, e.g. `check_cover_letter` without override).
     - If `task_key not in TASK_CONFIG`: do not call defaults (DB-only / gap keys use the field values already set — DB-row merge in `dispatch_task_keys` still supplies row entity/trigger).
3. In `dispatch_task_keys`, **delete** the merge loop:

```python
for tk in DISPATCH_SCHEDULABLE_TASK_KEYS:
    if tk not in seen:
        seen[tk] = _dispatch_task_key_form_meta(tk)
```

Keep the `get_task_keys()` loop, the `list_dispatch_tasks()` row merge, and the hidden/retired pops unchanged.

⚠️ **Decision:** Gap keys that exist only on the old frozenset (not in `TASK_CONFIG`, not on a DB row) disappear from the picker map. That is intentional — parent forbids stuffing them into `TASK_CONFIG` for catalog completeness. Existing `dispatch_task` rows for those keys still appear via the DB-row loop.

#### Stage 3: Config — delete frozenset; fix scored-trigger helper

**Done when:** `DISPATCH_SCHEDULABLE_TASK_KEYS` is gone from `src/utils/config.py` (definition and all references in `src/`). `trigger_state_used_by_scored_dispatch_task("NEW")` is `True` (via `qualify_job_listings` defaults). `trigger_state_used_by_scored_dispatch_task("PASSED_LIKE")` is `True`. `trigger_state_used_by_scored_dispatch_task("VALID_TITLE")` is `False` (qualify default trigger is `NEW`, not `VALID_TITLE`). Calling the helper does not raise `KeyError` on gap keys. `dispatch_task_admin_defaults("check_cover_letter", trigger_state="CANDIDATE_REVIEW")` still succeeds (AST-856 / AST-955 Save path unchanged).

1. In `src/utils/config.py`, **delete** the entire `DISPATCH_SCHEDULABLE_TASK_KEYS = frozenset({...})` block and its preceding comment.
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

⚠️ **Decision:** Delete the frozenset rather than leave an unused / empty constant. Ticket allows "deleted or made non-gating"; deletion removes the parallel catalog so it cannot regate bootstrap later.

#### Betty handoff note (not Ada work)

Expect Betty to adjust at Code Complete (do **not** edit these in build-child): `tests/component/core/test_bootstrap.py` (remove frozenset-missing → RuntimeError cases; drop frozenset monkeypatches); `tests/component/utils/test_config.py` (drop/rewrite `DISPATCH_SCHEDULABLE_TASK_KEYS` membership / ⊆ `TASK_CONFIG` asserts; keep AST-856 / AST-955 Save + registered-key coverage); `tests/component/ui/api/test_api_admin.py` (keep `check_cover_letter` Save regression; adjust frozenset-inventory / merge assertions); bible rows under `docs/test-bible/utils/config.md` and `docs/test-bible/ui/api/api_admin.md`.

#### Execution contract

The plan is binding. Execute stages in order. Do not add files, restore the frozenset, or put gap keys into `TASK_CONFIG`. On ambiguity or codebase drift, stop and comment the parent with the Stage N blocked template — no improvisation.

#### Self-review vs ASTRAL_CODE_RULES

| Rule | Status |
|------|--------|
| §1.3 DRY | Single membership rule (`TASK_CONFIG`); no new parallel set |
| §2.1 config SoT | Deletes second curated allowlist; derivation helpers for known dispatch keys remain in config |
| §2.4 batch | Untouched |
| §2.6 state machine | Untouched |
| §3.3 imports | Bootstrap/admin drop frozenset import; no new cross-layer imports |
| §3.5 naming | No new public names; delete one constant |
| Test-tree ban | Product files only; Betty owns test/bible AC4 |

**Self-Assessment:** Single-Component — three tightly coupled call sites (`bootstrap`, `api_admin` form meta/`task_keys`, `config` frozenset + scored-trigger helper) finishing one SoT cleanup; no dispatcher/gazer runtime redesign. Conf high — root cause and live gap list verified on this branch. Risk Medium — `trigger_state_used_by_scored_dispatch_task` and picker enrichment change behavior for gap keys, but Save (AST-856) and claim floor (`dispatch_claim_uses_score_floor`) stay on existing paths.

##### Comments

###### ada — 2026-07-23T02:48:32.464Z
**Scope:** Single-Component — bootstrap + api_admin form/`task_keys` + config frozenset deletion / scored-trigger rewrite; one SoT leftover from AST-955. **Conf:** high — live gap list verified (`fetch_jd` and 8 other frozenset keys ∉ TASK_CONFIG); Save path already TASK_CONFIG-only. **Risk:** Medium — scored-trigger helper and picker enrichment change for gap keys; claim floor + AST-856 Save untouched; Betty owns test/bible AC4.

###### joan — 2026-07-23T02:58:13.593Z
**Verdict: APPROVED** (plan-rubric). No `fix-now`. Plan faithful to AST-957 / AST-960: delete `DISPATCH_SCHEDULABLE_TASK_KEYS`, stop bootstrap inventory, align admin form/`task_keys` enrichment with `TASK_CONFIG`, rewrite `trigger_state_used_by_scored_dispatch_task` to scored `TASK_CONFIG` keys. Boundaries honored (Save path untouched; no gap-key stuffing; no gazer runtime redesign; tests/bible to Betty).

**[discuss]** Stage 2 picker — Gap keys that exist only on the old frozenset leave the picker map. Plan Decision + parent Boundaries already own this; no revise — Ada should not reintroduce a parallel catalog for catalog completeness.

**[acceptable]** AC4 automated coverage correctly deferred to Code Complete under engineer test-tree ban.

_Considered statutes:_ `astral.config.config-source-of-truth`, `astral.standards.no-hardcoded-sets`, `astral.standards.in-scope-only`, `astral.standards.dry-and-focused-functions`, `astral.layers.import-direction`, `astral.layers.ui-config-driven-business-logic`, `astral.git.engineer-test-tree-ban`, `astral.docs.features-single-file-per-ticket`, `orch.pipeline.plan-is-bible`.

###### betty — 2026-07-23T03:33:10.915Z
Narrowed runs: `tests/component/core/test_bootstrap.py`; `test_config.py::TestAst960DropSchedulableFrozensetInventory` + AST-955/796/702/719/701/874/505/506/471 dispatch-config classes; `test_api_admin.py::TestAst796FetchJdRetiredDispatchKeys` / `TestAst960TaskKeysNoFrozensetInventory` / `TestAst955AlignScheduledActionsSave`.

Broken / obsolete revised this pass: bootstrap frozenset-missing RuntimeError + monkeypatches; all `DISPATCH_SCHEDULABLE_TASK_KEYS` membership asserts; `dispatch_task_admin_defaults(<gap_key>)` without KeyError; `task_keys` frozenset merge expecting `fetch_jd` without a DB row.

Publish: `origin/sub/AST-957/AST-960-…` @ `1658e32` (`merge-tests(AST-960): origin/tests 8bfe40fe1`).

Bible shasum on publish tip: `docs/test-bible/README.md`, `docs/test-bible/core/bootstrap.md`, `docs/test-bible/ui/api/api_admin.md`, `docs/test-bible/ui/server.md`, `docs/test-bible/utils/config.md`.

###### radia — 2026-07-23T03:51:00.328Z
**Radia review — clean.** Diff: `origin/dev...origin/sub/AST-957/AST-960-…` (tip `1658e32`, incl. Betty `merge-tests`).

**What's solid:** Stages 1–3 match commits — bootstrap drops frozenset inventory loop; `api_admin` enrich/`task_keys` from `TASK_CONFIG` + defaults (no frozenset merge); `DISPATCH_SCHEDULABLE_TASK_KEYS` deleted; `trigger_state_used_by_scored_dispatch_task` walks scored `TASK_CONFIG`. Zero `DISPATCH_SCHEDULABLE_TASK_KEYS` under `src/`. Live Done-when: `NEW`/`PASSED_LIKE` True, `VALID_TITLE` False; `check_cover_letter` override intact; `fetch_jd ∉ TASK_CONFIG`.

**fix-now / discuss:** none. **Advisory:** `except KeyError: pass` in `_dispatch_task_key_form_meta` is plan-mandated mid-chain fallthrough with comment — acceptable under §5b. **Verdict:** Clean — `resolve-child` may proceed.

#### Resolution (2026-07-23, Ada)

- Radia fix-now / discuss none; advisory KeyError fallthrough left as-is (plan-mandated).
- No product delta this pass. Radia `docs(AST-960): Radia review — clean` @ `c64566f` already on publish tip via §4 merge.
- §9a dry-run vs `origin/dev` and `origin/ftr/AST-957-local-host-server-doesnt-load` before User Testing.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/core/bootstrap.py` | Remove `DISPATCH_SCHEDULABLE_TASK_KEYS` inventory loop and import; keep `TASK_CONFIG` / LLM env coupling only | `f7e3aa92d` |
| ✓ | `src/ui/api/api_admin.py` | Stop importing / iterating the frozenset in form meta and `task_keys`; enrich from `dispatch_task_admin_defaults` when the key is in `TASK_CONFIG` and defaults resolve | `b61de9d65` |
| ✓ | `src/utils/config.py` | Delete `DISPATCH_SCHEDULABLE_TASK_KEYS`; rewrite `trigger_state_used_by_scored_dispatch_task` to walk scored `TASK_CONFIG` keys | `92b9c0ed4` |
| | _tests_ | boot/coupling green without gap keys forced into `TASK_CONFIG`; AST-856 Save regression | `8bfe40fe1` — `test_bootstrap.py` / `test_config.py` / `test_api_admin.py` + `conftest.py` + test-bible (Betty) |
