<!-- linear-archive: AST-747 archived 2026-06-23 -->

## Linear archive (AST-747)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-747/config-schedulable-keys-retire-consult-aliases-task-keys-vs-dispatch  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-736 — Task keys vs. dispatch task keys  
**Blocked by / blocks / related:** parent: AST-736; blocks: AST-749; blocks: AST-748

### Description

## What this implements

Retire `consult_do`, `consult_get`, and `consult_like` from the schedulable dispatch vocabulary and collapse the consult→grade alias map in config so `DISPATCH_SCHEDULABLE_TASK_KEYS`, dispatch admin defaults, batch-call-mode grouping, and scored-trigger helpers use `grade_do`, `grade_get`, and `grade_like` — the same strings as `TASK_CONFIG` and Manage Tasks. Hard cutover: no read-time alias acceptance in config validation paths.

## Acceptance criteria

5. Admin API rejects new saves using retired `consult_*` keys with a clear validation error; no read-time alias accepts them post-cutover; `GET /api/admin/dispatch_tasks/task_keys` lists `grade_*` with correct phase/seq/trigger defaults.
6. `ASTRAL_CODE_RULES` dispatch pipeline table and test bible consult/dispatch sections reference `grade_*` only for those steps (no operator-facing `consult_*` schedulable names).

## Boundaries

* Does **not** implement the DB row rename or consult/dispatcher runtime paths — sibling **Hedy** ticket.
* Does **not** change Scheduled Actions React UI — sibling **Katherine** ticket.
* Does **not** rename `TASK_CONFIG` entry contents or grading semantics.

## Notes for planning

* Primary: `src/utils/config.py` — `DISPATCH_SCHEDULABLE_TASK_KEYS`, `_CONSULT_TASK_TO_AGENT_TASK`, `resolve_dispatch_task_config_key`, `_dispatch_trigger_state_for_task_key`, `_DISPATCH_BATCH_CALL_MODE_ONE`, `dispatch_task_admin_defaults`, `dispatch_task_key_is_scored`.
* Secondary: `src/ui/api/api_admin.py` if task_keys defaults must change with config (coordinate with Katherine if split is awkward).
* Docs: `docs/ASTRAL_CODE_RULES.md`, `docs/ASTRAL_TEST_BIBLE.md` / test-bible consult sections.

## Git branch (authoritative)

Per **orientation** § Branch law: parent `ftr/ast-736-task-keys-vs-dispatch-task-keys`, child `sub/AST-736/AST-737-config-schedulable-keys-retire-consult-aliases`. Created at dispatch-parent.

### Comments

#### chuckles — 2026-06-23T19:25:33.416Z
[check-linear]

Cleared **[qa-handoff]** (Radia fix-now #2): **`docs/ASTRAL_TEST_BIBLE.md`** Stage 3 items 4–5 on publish ref — **`grade_like`** schedulable hop (~§7.13y) and **`grade_do`** / identity-only **`resolve_dispatch_task_config_key`** note (~§7.13zz AST-654 test-child note).

**Publish:** `origin/sub/AST-736/AST-747-config-schedulable-keys-retire-consult-aliases` @ `e64fda3` (`merge-tests(AST-747): origin/tests 8664ce5`)

**Monolith shasum:** `docs/ASTRAL_TEST_BIBLE.md` → verify on tip after merge.

Ada — re-run **resolve-child** §9a + manifest; bootstrap/`catalog_key` fix already @ `c2cdaa3`.

— Betty

#### ada — 2026-06-23T19:24:25.983Z
[qa-handoff]

Radia fix-now #2 — engineer hook blocks `docs/ASTRAL_TEST_BIBLE.md`. Product resolve landed @ `c2cdaa3` (bootstrap + `catalog_key` trim). Manifest 16/16 green.

**Please update monolith on publish ref per plan Stage 3 items 4–5:**
- ~L370: schedulable hop **`consult_like`** → **`grade_like`** (dispatch vocabulary)
- ~L1839: example **`consult_do`** → **`grade_do`**; replace alias-resolution sentence with identity-only resolver / direct `TASK_CONFIG` membership note

Reassign Ada when done; stay **Review Posted** until bible lands, then Ada re-runs resolve → **User Testing**.

@Betty White

#### radia — 2026-06-23T19:23:00.558Z
## Radia review (AST-747)

**Diff:** `origin/dev...origin/sub/AST-736/AST-747-config-schedulable-keys-retire-consult-aliases` @ `733e036`
**Doc:** `docs/features/foundation/ast-747-config-schedulable-keys-retire-consult-aliases.md` (Review Radia section)

**AST-747 commits:** `e0c9e27`, `627a5f9`, `6eb729e`, `5467924`. Publish ref rolls up sibling qa (**AST-745/746/751**) — not AST-747 scope on Ada commits.

### What's solid

- Stage 1 config cutover: `DISPATCH_RETIRED_TASK_KEYS`, `dispatch_task_key_retired_message`, `grade_*` schedulable/batch frozensets, alias map removed, identity resolver, trigger/entity/scored helpers updated.
- Admin `POST /api/admin/dispatch_tasks` rejects retired `consult_*` with operator message before save.
- `ASTRAL_CODE_RULES.md` §2.6–2.7 + pipeline table use `grade_*`; §2.6.2 example corrected for `grade_do` / `PASSED_JD` → `PASSED_DO`.
- Betty manifest covers retired-key guard, `grade_do` defaults, `task_keys` grouping on catalog row.

### fix-now

1. **Plan Stage 2 incomplete — bootstrap validation** (`src/core/bootstrap.py` L33–36): `_validate_runtime_coupling()` still uses alias-era `resolved = resolve_dispatch_task_config_key(key)` branch. Plan requires `if key in TASK_CONFIG: continue` and drop unused import. Harmless while resolver is identity; stale vs cutover contract (§2.1).

2. **Plan Stage 3 incomplete — `ASTRAL_TEST_BIBLE.md`**: dispatch vocabulary still references `consult_do` / alias resolution (~L1839) and **`consult_like`** schedulable hop (~L370). Plan items 4–5 not in engineer commits.

### discuss

- `_dispatch_task_key_form_meta` still calls `resolve_dispatch_task_config_key` for `catalog_key`; plan asked for trim-only. Behavior identical — inline during resolve-child or defer to **AST-748**?

### advisory

- Three-dot diff includes **AST-745** (`database.py`), **AST-746/751** (`AdminScheduledActions.tsx`) from sibling qa merges — expected epic rollup, not boundary violation on AST-747 commits.
- **AST-748** still required for runtime consult/dispatcher cutover.

#### chuckles — 2026-06-18T22:55:28.385Z
## QA test manifest (AST-747)

**Publish:** `origin/sub/AST-736/AST-747-config-schedulable-keys-retire-consult-aliases` @ `5467924`

**Scope:** Config/admin cutover — schedulable `grade_*`, retired `consult_*`, identity `resolve_dispatch_task_config_key`. **AST-748** owns `consult.py` / `dispatcher.py` runtime; do **not** expect zero-arg harness or full `test_consult.py` green on this tip alone.

**Bible shasum (`origin/sub/…`):**
- `docs/test-bible/utils/config.md` → `4a26ccf7607967d479f60a5aef47140bdd787411044fabbb0090c9207f34aeaa`
- `docs/test-bible/ui/server.md` → `96fe59b18b32b39c0fe97965638ee404896c806b7d9df1d56ca678bbed947ec4`
- `docs/test-bible/ui/api/api_admin.md` → `e031db46a62adff6eaaee3080a550ff7fb78c040b92d57001c5c1f97159f3e5e`

**Manifest (test-child) — narrowed; pass = pytest green, not zero-arg harness:**

1. **Config schedulable / retired keys** — `tests/component/utils/test_config.py::TestAst471DispatchConfigHelpers`.

2. **Admin `task_keys` grouping on `grade_do`** — `tests/component/ui/api/test_api_admin.py::TestAst739DispatchTaskKeysGrouping`.

3. **Admin POST rejects retired `consult_do`** — `tests/component/ui/api/test_api_admin.py::TestDispatchTasks::test_create_dispatch_task_rejects_retired_consult_key`.

4. **Schedulable derivation regression** — `tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_ast549_task_keys_config_derivation_authoritative`.

5. **Scored-trigger helper** — `tests/component/ui/api/test_api_admin.py::TestAdhocHelpers::test_trigger_state_helpers`.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst471DispatchConfigHelpers \
  tests/component/ui/api/test_api_admin.py::TestAst739DispatchTaskKeysGrouping \
  tests/component/ui/api/test_api_admin.py::TestDispatchTasks::test_create_dispatch_task_rejects_retired_consult_key \
  tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_ast549_task_keys_config_derivation_authoritative \
  tests/component/ui/api/test_api_admin.py::TestAdhocHelpers::test_trigger_state_helpers \
  -q
```

**Broken / obsolete (revised this pass):** `TestAst471DispatchConfigHelpers` alias-map assertions; `TestAst739DispatchTaskKeysGrouping` / `test_ast549_*` — `consult_do` → `grade_do` catalog grouping.

**Out of manifest (AST-748):** `tests/component/core/test_consult.py`, `tests/component/core/test_dispatcher.py` consult `dispatch_task_key="consult_*"` routing.

— Betty

#### ada — 2026-06-18T22:49:13.128Z
Plan: [`docs/features/foundation/ast-747-config-schedulable-keys-retire-consult-aliases.md`](https://github.com/susansomerset/astral/blob/sub/AST-736/AST-747-config-schedulable-keys-retire-consult-aliases/docs/features/foundation/ast-747-config-schedulable-keys-retire-consult-aliases.md)

**Self-assessment**
- **Scope:** Single-Component — config schedulable frozensets + alias removal, bootstrap validation loop, admin API retired-key guard, operator docs.
- **Conf:** high — `grade_*` already in `TASK_CONFIG`; work is explicit key substitution and deleting `_CONSULT_TASK_TO_AGENT_TASK`.
- **Risk:** Medium — admin metadata/validation wrong until AST-748/749 land; runtime consult/dispatcher untouched in this ticket.

Three stages: (1) config cutover, (2) bootstrap + admin API, (3) ASTRAL_CODE_RULES + test bible schedulable vocabulary. Siblings AST-748 (DB + runtime) and AST-749 (React) stay out of scope.

#### ada — 2026-06-18T22:48:55.032Z
**Plan:** https://github.com/susansomerset/astral/blob/sub/AST-736/AST-747-config-schedulable-keys-retire-consult-aliases/docs/features/foundation/ast-747-config-schedulable-keys-retire-consult-aliases.md

Three stages: (1) config — swap schedulable frozensets to `grade_*`, add `DISPATCH_RETIRED_TASK_KEYS`, identity `resolve_dispatch_task_config_key`; (2) admin API — 400 on create with retired `consult_*`; (3) `ASTRAL_CODE_RULES` pipeline table + §2.7 wording. Runtime/DB/UI out of scope (AST-748/749). Test-bible AC #6 → Betty manifest.

**Self-assessment**
- **Scope:** Single-Component — config schedulable vocabulary + narrow admin validation + rules doc.
- **Conf:** high — same AST-549 defaults pattern; rename three keys and delete three-entry alias map.
- **Risk:** Medium — config cutover needs AST-748 before full test green; wrong trigger pairing would mis-label admin defaults for graded consult hops only.

---

# AST-747 — Config schedulable keys retire consult aliases

- **Linear (this ticket):** [AST-747](https://linear.app/astralcareermatch/issue/AST-747/config-schedulable-keys-retire-consult-aliases-task-keys-vs-dispatch)
- **Parent:** [AST-736](https://linear.app/astralcareermatch/issue/AST-736/task-keys-vs-dispatch-task-keys)
- **Publish ref:** `origin/sub/AST-736/AST-747-config-schedulable-keys-retire-consult-aliases`

## Summary

Retire `consult_do`, `consult_get`, and `consult_like` from the schedulable dispatch vocabulary in `src/utils/config.py` and admin validation paths. Promote `grade_do`, `grade_get`, and `grade_like` as the sole schedulable keys for those pipeline hops — the same strings already used in `TASK_CONFIG` and Manage Tasks. Remove the consult→grade alias map so config derivation, batch-call-mode grouping, scored-trigger helpers, and `GET /api/admin/dispatch_tasks/task_keys` never resolve a parallel dispatch-only name. Hard cutover in config/admin: retired keys are rejected on new saves; no read-time alias acceptance.

**Sibling scope (do not implement here):** DB row rename and consult/dispatcher runtime paths (**AST-748**, Hedy); Scheduled Actions React UI (**AST-749**, Katherine).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Replace `consult_*` with `grade_*` in schedulable/batch frozensets; add `DISPATCH_RETIRED_TASK_KEYS` + `dispatch_task_key_retired_message`; remove `_CONSULT_TASK_TO_AGENT_TASK`; identity `resolve_dispatch_task_config_key`; update trigger/entity helpers | utils |
| `src/core/bootstrap.py` | Tighten schedulable-key validation now that graded keys are direct `TASK_CONFIG` members | core |
| `src/ui/api/api_admin.py` | Reject retired `consult_*` on dispatch create; ensure `task_keys` metadata uses `grade_*` without alias resolution | ui |
| `docs/ASTRAL_CODE_RULES.md` | Dispatch pipeline table + §2.7 alias wording → `grade_*` | docs |
| `docs/ASTRAL_TEST_BIBLE.md` | Schedulable-key / dispatch admin notes → `grade_*` | docs |
| `docs/test-bible/utils/config.md` | Schedulable hop name → `grade_like` where describing dispatch vocabulary | docs |
| `docs/test-bible/ui/server.md` | `DISPATCH_SCHEDULABLE_TASK_KEYS` example + alias note → `grade_*` / no alias | docs |

**Out of scope (sibling tickets — do not touch):**

| Ticket | Owner | Scope |
|--------|-------|-------|
| AST-748 | Hedy | DB row rename migration; `consult.py` / `dispatcher.py` runtime cutover |
| AST-749 | Katherine | Scheduled Actions React UI; dispatch modals |

**QA manifest (Betty — not engineer commits):** Update `tests/component/utils/test_config.py` schedulable-key assertions; `tests/component/ui/api/test_api_admin.py` task_keys derivation tests; `docs/test-bible/core/consult.md`, `docs/test-bible/core/dispatcher.md` runtime wording when **AST-748** lands.

## Prerequisite (build gate — not a commit stage)

**Done when:** Epic worktree is on `sub/AST-736/AST-747-config-schedulable-keys-retire-consult-aliases` with `origin/dev` and `origin/ftr/ast-736-task-keys-vs-dispatch-task-keys` merged.

⚠️ **Decision:** **test-child** green on the full component manifest requires **AST-748** runtime changes — removing the config alias breaks `consult.run_consult_task` paths that still pass `consult_*` until Hedy lands. Ada completes **code()** for config + admin + rules only; do not patch `src/core/consult.py` or `src/core/dispatcher.py` in this ticket.

## Stage 1: Config — schedulable keys, retired keys, collapse alias map

**Done when:** `grep consult_do src/utils/config.py` returns no schedulable/alias references (JOB_STATES comments may still mention consult outcomes); `dispatch_task_admin_defaults("grade_do")` returns `entity_type=job`, `trigger_state=PASSED_JD`, `batch_call_mode=1`; `dispatch_task_admin_defaults("consult_do")` raises with a retired-key message; `resolve_dispatch_task_config_key("grade_do")` returns `"grade_do"`.

1. In `src/utils/config.py`, add module-level frozenset immediately above `DISPATCH_SCHEDULABLE_TASK_KEYS`:

```python
DISPATCH_RETIRED_TASK_KEYS = frozenset({
    "consult_do", "consult_get", "consult_like",
})
```

2. Add public helper (same file, near `dispatch_task_admin_defaults`):

```python
_RETIRED_DISPATCH_TASK_KEY_REPLACEMENTS = {
    "consult_do": "grade_do",
    "consult_get": "grade_get",
    "consult_like": "grade_like",
}

def dispatch_task_key_retired_message(task_key: str) -> str | None:
    """Return operator-facing error text when task_key is retired, else None."""
```

When `task_key.strip()` is in `DISPATCH_RETIRED_TASK_KEYS`, return exactly:
`f"task_key {tk!r} is retired; use {_RETIRED_DISPATCH_TASK_KEY_REPLACEMENTS[tk]!r}"`.

3. In `DISPATCH_SCHEDULABLE_TASK_KEYS`, remove `"consult_do"`, `"consult_get"`, `"consult_like"`. Add `"grade_do"`, `"grade_get"`, `"grade_like"`. Keep `"analysis_upshot"` and all other existing keys unchanged.

4. In `_DISPATCH_BATCH_CALL_MODE_ONE`, replace `"consult_do"`, `"consult_get"`, `"consult_like"` with `"grade_do"`, `"grade_get"`, `"grade_like"`.

5. Delete dict `_CONSULT_TASK_TO_AGENT_TASK` entirely.

6. Replace `resolve_dispatch_task_config_key` body with identity only:

```python
def resolve_dispatch_task_config_key(task_key: str) -> str:
    """Return task_key unchanged — dispatch and TASK_CONFIG share one string (AST-736)."""
    return (task_key or "").strip()
```

Do **not** map retired keys to replacements in this function.

7. In `_dispatch_trigger_state_for_task_key`, replace the three `consult_*` branches with `grade_do` → `PASSED_JD`, `grade_get` → `PASSED_DO`, `grade_like` → `PASSED_GET`.

8. In `_dispatch_entity_type_for_task_key`, replace the hardcoded tuple `"consult_do", "consult_get", "consult_like"` with `"grade_do", "grade_get", "grade_like"`.

9. In `dispatch_task_admin_defaults`, as the **first** statement after normalizing `tk`:

```python
    retired = dispatch_task_key_retired_message(tk)
    if retired:
        raise KeyError(retired)
```

Keep existing `DISPATCH_SCHEDULABLE_TASK_KEYS` membership check unchanged after the retired guard.

10. Simplify `dispatch_task_key_is_scored`:

```python
def dispatch_task_key_is_scored(task_key: str) -> bool:
    tk = (task_key or "").strip()
    return bool((TASK_CONFIG.get(tk) or {}).get("scored"))
```

11. Grep `src/utils/config.py` for remaining `consult_do`, `consult_get`, `consult_like` — only JOB_STATES / comment references to consult **outcomes** may remain.

⚠️ **Decision:** Keep `resolve_dispatch_task_config_key` as a named identity function — **AST-748** still imports it from `consult.py` / `bootstrap.py`; removing the symbol would break the tree before runtime cutover.

## Stage 2: Bootstrap + Admin API — validation and task_keys metadata

**Done when:** Server bootstrap passes with new schedulable set; `POST /api/admin/dispatch_tasks` with `task_key: "consult_do"` returns HTTP 400 with body containing `retired` and `grade_do`; `GET /api/admin/dispatch_tasks/task_keys` includes `grade_do` / `grade_get` / `grade_like` with correct trigger defaults and `is_scored: true`.

1. In `src/core/bootstrap.py`, in `_validate_runtime_coupling()`, replace the schedulable loop body with:

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

Remove the `resolved = resolve_dispatch_task_config_key(key)` branch. Remove `resolve_dispatch_task_config_key` from imports if unused.

2. In `src/ui/api/api_admin.py`, add import: `dispatch_task_key_retired_message` from `src.utils.config`.

3. In `create_dtask()`, immediately after the required-field check and **before** `save_dispatch_task`:

```python
    retired = dispatch_task_key_retired_message(data.get("task_key", ""))
    if retired:
        return jsonify({"error": retired}), 400
```

4. In `_dispatch_task_key_form_meta`, set `catalog_key = (task_key or "").strip()` instead of `resolve_dispatch_task_config_key(task_key)`. Remove `resolve_dispatch_task_config_key` from imports if unused elsewhere.

5. Update the adhoc live-content comment near line 973 from `consult_do/get/like` to `grade_do/get/like`.

6. Grep `src/ui/api/api_admin.py` for `consult_do`, `consult_get`, `consult_like` — zero remaining references.

⚠️ **Decision:** Do **not** add retired-key validation to `PUT /api/admin/dispatch_tasks/<id>` — updates cannot change `task_key`; migration of existing rows is **AST-748**.

## Stage 3: Documentation — operator-facing vocabulary

**Done when:** `grep consult_do docs/ASTRAL_CODE_RULES.md` returns zero matches; schedulable dispatch vocabulary in listed test-bible files uses `grade_*`.

1. In `docs/ASTRAL_CODE_RULES.md` §3.3 dispatch pipeline table (~lines 373–375), rename rows to `grade_do`, `grade_get`, `grade_like` (keep PW/AI/DB columns unchanged).

2. In §2.6 Jobs example (~line 195), change to **`grade_do`** dispatch task.

3. In §2.7 step 1 (~line 209), replace alias wording with: resolve orchestration via **`TASK_CONFIG[task_type]`** — dispatch `task_key` and catalog key are the same string for graded consult steps.

4. In `docs/ASTRAL_TEST_BIBLE.md` (~line 370), rename schedulable hop **`consult_like`** → **`grade_like`** where describing dispatch vocabulary.

5. In `docs/ASTRAL_TEST_BIBLE.md` (~line 1839), replace `consult_do` example and alias sentence with `grade_do` / identity-only resolver note.

6. In `docs/test-bible/utils/config.md` (~line 38) and `docs/test-bible/ui/server.md` (~line 29), update schedulable-key examples to `grade_*`.

## Execution contract

Binding per **plan-child**: stages **1 → 2 → 3** in order; **one commit per stage** on epic worktree during **build-child**, publish each to **`origin/sub/AST-736/AST-747-config-schedulable-keys-retire-consult-aliases`**. Do not edit `tests/` or `src/core/consult.py`, `src/core/dispatcher.py`, `src/data/database.py`. On ambiguity — **`🛑 Stage N blocked`** on **AST-736** parent; stop.

## Self-Assessment

**Scope:** `Single-Component` — primarily `src/utils/config.py` schedulable vocabulary and alias removal, with bootstrap validation, admin API guard, and rules-doc updates.

**Conf:** `high` — AST-549 established the `dispatch_task_admin_defaults` pattern; this ticket renames three frozenset members and removes a three-entry alias dict.

**Risk:** `Medium` — config-only cutover breaks runtime consult routing until **AST-748** merges; incorrect schedulable/trigger pairing would mis-label admin defaults for the three graded consult hops.

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Status |
|------|--------|
| §1.3 DRY | Retiring alias map removes duplicate vocabulary. |
| §2.1 config | Schedulable keys remain explicit frozenset; retired keys fail loudly. |
| §2.4 batch | `batch_call_mode` frozenset updated in same edit as schedulable keys. |
| §2.6 state machine | Trigger states unchanged; only task_key strings change. |
| §3.3 imports | Utils-only in Stage 1; ui imports one config helper in Stage 2. |
| §3.5 naming | `grade_*` matches existing `TASK_CONFIG` index. |

No conflicts requiring `!!-NONE`.

## Integration notes (for build-child / siblings)

- **AST-748** must land before Susan can run migrated `grade_*` rows end-to-end.
- **Betty** updates component tests referencing `consult_do` in `task_keys` metadata — do not edit tests in this ticket.
- **`resolve_dispatch_task_config_key`** remains imported by `consult.py` until **AST-748** removes those call sites.

## Review (build)

| Field | Value |
|-------|-------|
| Build date | 2026-06-18 |
| Publish ref | `origin/sub/AST-736/AST-747-config-schedulable-keys-retire-consult-aliases` @ `5467924` |
| Commits | `e0c9e27` config · `627a5f9` admin API · `6eb729e` rules doc · `5467924` test (Betty) |

---

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-736/AST-747-config-schedulable-keys-retire-consult-aliases` · tip **`5467924`**

**AST-747 product commits:** `e0c9e27`, `627a5f9`, `6eb729e`, `5467924`. Publish ref also rolls up sibling qa merges (**AST-745**, **AST-746**, **AST-751**) — not attributed to this ticket (§5d boundary clean on Ada commits).

### What's solid

| Area | Notes |
|------|-------|
| Plan Stage 1 | `DISPATCH_RETIRED_TASK_KEYS`, `dispatch_task_key_retired_message` (exact operator text), `grade_*` in schedulable + batch frozensets, alias map removed, identity `resolve_dispatch_task_config_key`, trigger/entity helpers and `dispatch_task_key_is_scored` updated. |
| Plan Stage 2 (partial) | `create_dtask` rejects retired `consult_*` before save; adhoc comment uses `grade_*`. |
| Plan Stage 3 (partial) | `docs/ASTRAL_CODE_RULES.md` §2.6–2.7 + pipeline table use `grade_*`; §2.6.2 example corrected (`grade_do` on `PASSED_JD` → `PASSED_DO`). |
| §2.1 config | Retired keys fail loudly via `KeyError` / HTTP 400; schedulable vocabulary single-sourced in frozensets. |
| §3.3 layer | Utils + one config helper import in `api_admin`; no cross-layer violations in AST-747 commits. |
| Tests | Betty manifest: retired-key guard, `grade_do` schedulable defaults, `task_keys` grouping on catalog `grade_do`, bible blocks in `utils/config`, `ui/api`, `ui/server`. |

### Issues

| Severity | Item | Location |
|----------|------|----------|
| **fix-now** | **Plan Stage 2 incomplete** — `_validate_runtime_coupling()` still uses alias-era `resolved = resolve_dispatch_task_config_key(key)` branch. Plan requires direct `if key in TASK_CONFIG: continue` loop and dropping unused import. Harmless while resolver is identity, but stale and contradicts cutover contract. | `src/core/bootstrap.py` L33–36 |
| **fix-now** | **Plan Stage 3 incomplete** — `docs/ASTRAL_TEST_BIBLE.md` still documents dispatch vocabulary as `consult_do` / alias resolution (~L1839) and **`consult_like`** as schedulable hop name (~L370). Plan Stage 3 items 4–5 not landed in engineer commits. | `docs/ASTRAL_TEST_BIBLE.md` |
| **discuss** | `_dispatch_task_key_form_meta` still calls `resolve_dispatch_task_config_key` for `catalog_key`; plan Stage 2 item 4 asked for `(task_key or "").strip()`. Behavior identical today — defer cleanup to **resolve-child** or **AST-748** when call sites drop? | `src/ui/api/api_admin.py` L765 |
| **advisory** | Publish-ref three-dot diff includes **AST-745** (`database.py`), **AST-746/751** (`AdminScheduledActions.tsx`) from sibling qa merges — expected epic rollup, not AST-747 smuggling. | branch composition |

### Recommended actions

| Action | Owner |
|--------|-------|
| **resolve-child:** tighten `bootstrap.py` schedulable validation per plan Stage 2; update `ASTRAL_TEST_BIBLE.md` dispatch vocabulary (~L370, ~L1839) per plan Stage 3. | Ada |

## Resolution

| Field | Value |
|-------|-------|
| Date | 2026-06-23 |
| Publish ref | `origin/sub/AST-736/AST-747-config-schedulable-keys-retire-consult-aliases` |

### fix-now — bootstrap (closed)

**`src/core/bootstrap.py`:** `_validate_runtime_coupling()` schedulable loop now uses `if key in TASK_CONFIG: continue` only; dropped `resolve_dispatch_task_config_key` import (Radia review §Issues fix-now #1).

### fix-now — discuss (closed)

**`src/ui/api/api_admin.py`:** `_dispatch_task_key_form_meta` sets `catalog_key = (task_key or "").strip()`; removed unused `resolve_dispatch_task_config_key` import (Radia discuss item).

### fix-now — `ASTRAL_TEST_BIBLE.md` (closed @ `e64fda3`)

Betty **`merge-tests(AST-747)`** — §7.13y **`grade_like`** schedulable hop; §7.13zz AST-654 test-child note uses **`grade_do`** / identity-only **`resolve_dispatch_task_config_key()`** (Radia fix-now #2).

### Outcome

All **fix-now** and **discuss** items closed. Ready for **User Testing**.
