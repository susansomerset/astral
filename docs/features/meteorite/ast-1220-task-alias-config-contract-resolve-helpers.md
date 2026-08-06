# AST-1220 — Task alias config contract + resolve helpers

**Linear:** [AST-1220](https://linear.app/astralcareermatch/issue/AST-1220/task-alias-config-contract-resolve-helpers-task-config-aliases-via)
**Parent:** [AST-1184](https://linear.app/astralcareermatch/issue/AST-1184/task-config-aliases-via-master-task-key) — Task config aliases via master_task_key
**Publish ref:** `origin/sub/AST-1184/AST-1220-task-alias-config-contract-resolve-helpers`

Owns the general **task-alias** contract in `TASK_CONFIG`: any entry may declare `master_task_key` pointing at a live non-alias master; module-load validation rejects missing masters and alias chains; resolve helpers return the master for prompt/content lookup (or the key unchanged when not an alias). Ships first-consumer alias entries `meteorite_grade_do` → `grade_do` and `meteorite_grade_get` → `grade_get` with their own meteorite pass/fail/error (and related scored orchestration), and clears Do/Get entries from `METEORITE_GDL_OUTCOME_BY_TASK` so that overlay is no longer the source of those outcomes. Does **not** rewire consult/agent call sites (**AST-1221**) or seed/retarget meteorite dispatch / `agent_task` rows (**AST-1222**).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `master_task_key` contract + resolve helpers + load-time asserts (incl. alias outcomes ∈ `JOB_STATES`); add `meteorite_grade_do` / `meteorite_grade_get` `TASK_CONFIG` aliases with meteorite outcomes + field-driven `trigger_state`; empty `METEORITE_GDL_OUTCOME_BY_TASK`; add alias keys to `_DISPATCH_BATCH_CALL_MODE_ONE` | utils |

**No changes expected:** `src/core/consult.py`, `src/core/agent.py`, `src/core/dispatcher.py`, `data/admin/agent_task.json`, `METEORITE_DISPATCH_TASKS` / `SEED_CONFIG` meteorite SQL (still `grade_do` / `grade_get` until **AST-1222**), frontend, `tests/` / bible (Betty after Code Complete).

## Stage 1: Resolve helpers + alias validation + retire Do/Get overlay source

**Done when:** `resolve_task_key_for_content` / `is_task_alias` exist and behave as specified; load-time asserts reject missing masters and alias chains, and (once aliases exist) require job-entity alias `pass_state` / `fail_state` / `error_state` ∈ `JOB_STATES`; `METEORITE_GDL_OUTCOME_BY_TASK` is an empty dict (no `grade_do` / `grade_get` overlay entries); `python3 -m py_compile src/utils/config.py` succeeds (repo venv: `~/astral/.venv/bin/python`).

1. In `src/utils/config.py`, immediately after `get_task_keys` (near other TASK_CONFIG helpers ~line 1017), add:

```python
def is_task_alias(task_key: str) -> bool:
    """True when TASK_CONFIG[task_key] declares a non-empty master_task_key."""
    tk = (task_key or "").strip()
    master = (TASK_CONFIG.get(tk) or {}).get("master_task_key")
    return isinstance(master, str) and bool(master.strip())


def resolve_task_key_for_content(task_key: str) -> str:
    """Return master_task_key for prompt/content lookup; unchanged when not an alias.

    Field-driven only — no one-off meteorite (or other) alias maps.
    """
    tk = (task_key or "").strip()
    master = (TASK_CONFIG.get(tk) or {}).get("master_task_key")
    if isinstance(master, str) and master.strip():
        return master.strip()
    return tk
```

⚠️ **Decision — helper names `is_task_alias` / `resolve_task_key_for_content`:** Matches parent language (alias → master for prompt/content). Do **not** invent a parallel dict keyed by meteorite names. Callers in **AST-1221** import these from config.

⚠️ **Decision — non-aliases omit `master_task_key`:** Do not set `master_task_key: None` on every existing entry. Absence means “not an alias.”

2. Near the existing module-load `TASK_CONFIG` asserts (the loop that validates `task_type` ~line 5047), add an alias-contract assert loop **after** that loop (same region — still import-time):

```python
for _alias_key, _alias_cfg in TASK_CONFIG.items():
    _master_raw = (_alias_cfg or {}).get("master_task_key")
    if _master_raw is None:
        continue
    assert isinstance(_master_raw, str) and _master_raw.strip(), (
        f"TASK_CONFIG[{_alias_key!r}].master_task_key must be a non-empty str when present"
    )
    _master_key = _master_raw.strip()
    assert _master_key != _alias_key, (
        f"TASK_CONFIG[{_alias_key!r}] cannot set master_task_key to itself"
    )
    assert _master_key in TASK_CONFIG, (
        f"TASK_CONFIG[{_alias_key!r}].master_task_key={_master_key!r} is not a live TASK_CONFIG key"
    )
    _master_cfg = TASK_CONFIG[_master_key] or {}
    assert not (
        isinstance(_master_cfg.get("master_task_key"), str)
        and str(_master_cfg.get("master_task_key")).strip()
    ), (
        f"alias chain forbidden: {_alias_key!r} -> {_master_key!r} is itself an alias"
    )
    # Restore the invariant formerly guarded by METEORITE_GDL_OUTCOME_BY_TASK
    # value ∈ JOB_STATES (that assert is vacuous once the overlay is {}).
    if (_alias_cfg or {}).get("entity_type") == "job":
        for _outcome_key in ("pass_state", "fail_state", "error_state"):
            _outcome = (_alias_cfg or {}).get(_outcome_key)
            if isinstance(_outcome, str) and _outcome.strip():
                assert _outcome.strip() in JOB_STATES, (
                    f"TASK_CONFIG[{_alias_key!r}].{_outcome_key}={_outcome!r} "
                    f"is not a JOB_STATES key"
                )
```

⚠️ **Decision — alias outcome ∈ `JOB_STATES` in this loop:** Emptying the overlay removes the only module-load check that those meteorite Do/Get strings were registered states. There is no generic TASK_CONFIG pass/fail/error → `JOB_STATES` assert elsewhere. Require it for job-entity aliases here so a typo cannot ship silently.

3. Replace the live Do/Get overlay body of `METEORITE_GDL_OUTCOME_BY_TASK` with an empty dict and rewrite the preceding comments to state:

- Meteorite Do/Get outcomes now live on alias `TASK_CONFIG` entries (`meteorite_grade_do` / `meteorite_grade_get`) — **AST-1220**.
- `consult._consult_orchestration_for_entity` may still import this name until **AST-1221** removes the overlay read path.
- Do **not** delete the symbol in this ticket (keeps import stable for the sibling).

Final shape:

```python
# AST-1220: Do/Get meteorite outcomes moved onto alias TASK_CONFIG entries
# (meteorite_grade_do / meteorite_grade_get). Overlay no longer supplies those
# outcomes. Empty dict kept until AST-1221 removes consult's overlay read.
METEORITE_GDL_OUTCOME_BY_TASK = {}
```

Keep the existing asserts that iterate `METEORITE_GDL_OUTCOME_BY_TASK.values()` (they remain valid on `{}`). Keep `assert all(e["trigger_state"] in JOB_STATES for e in METEORITE_DISPATCH_TASKS)`.

⚠️ **Decision — empty overlay now, do not leave dual source:** Parent AC requires the overlay no longer supply Do/Get outcomes. Leaving `grade_do` / `grade_get` overlay entries alongside alias pass/fail would violate `astral.standards.no-hardcoded-sets` (two sources). Intermediate gap until **AST-1221**/**AST-1222**: meteorite jobs still claimed under shared `grade_do` / `grade_get` will use classic Gaze pass/fail from `TASK_CONFIG` (no overlay) and may trip `prior_states` in `transition_job_state`. That is accepted epic sequencing — do **not** rewire consult here to paper over it.

**QA note (ftr-internal):** Do **not** exercise meteorite Do/Get on a tree that has only AST-1220 merged — wait for AST-1221 + AST-1222 (or full ftr rollup) before that path is operator-safe.

4. Verify Stage 1 (no alias entries required yet for this gate):

```bash
~/astral/.venv/bin/python -c "
from src.utils import config as c
assert c.METEORITE_GDL_OUTCOME_BY_TASK == {}
assert c.resolve_task_key_for_content('grade_do') == 'grade_do'
assert c.is_task_alias('grade_do') is False
assert c.resolve_task_key_for_content('no_such') == 'no_such'
"
~/astral/.venv/bin/python -m py_compile src/utils/config.py
```

**Ritual:** `code(AST-1220): task-alias resolve helpers + empty Do/Get overlay`

## Stage 2: First-consumer alias entries + admin dispatch defaults

**Done when:** `meteorite_grade_do` / `meteorite_grade_get` exist in `TASK_CONFIG` with `master_task_key` → `grade_do` / `grade_get`, meteorite pass/fail/error matching the former overlay, field-driven `trigger_state` `METEORITE_PASSED_JD` / `METEORITE_PASSED_DO`, and related scored orchestration; `dispatch_task_admin_defaults` resolves those triggers via `TASK_CONFIG[…]["trigger_state"]` (no new `_dispatch_trigger_state_for_task_key` branches); `METEORITE_DISPATCH_TASKS` still uses `grade_do` / `grade_get`; helpers resolve the new keys to their masters; import-time asserts pass.

1. In `TASK_CONFIG`, immediately after the `"grade_get"` block (before `"grade_like"`), insert:

```python
    # AST-1184 / AST-1220: meteorite Do/Get aliases — prompts/content from master via
    # master_task_key; own meteorite pass/fail/error (replaces METEORITE_GDL_OUTCOME_BY_TASK).
    # agent_task seed + METEORITE_DISPATCH_TASKS retarget are AST-1222; consult resolve is AST-1221.
    "meteorite_grade_do": {
        "master_task_key": "grade_do",
        "scored": True,
        "grades_key": "do_grades",
        "rubric_artifact": "do_rubric",
        "response_format": "json",
        "output_type": "grades_encoded_notes",
        "response_schema": {
            "jobs": {
                "type": "list",
                "required": True,
                "items_schema": _ENCODED_CONSULT_JOB_ITEM_SCHEMA,
            },
        },
        "fallback_batch_size": 10,
        "pass_state": "METEORITE_PASSED_DO",
        "fail_state": "METEORITE_FAILED_DO",
        "error_state": "METEORITE_FAILED_TECHNICAL_DO",
        "save_prefix": "do",
        "pass_threshold": 6.0,
        "grading_mode": "scored",
        "context_format": "meteorite_grade_do_{index}",
        "entity_type": "job",
        "requires_candidate_key": True,
        "trigger_state": "METEORITE_PASSED_JD",
    },
    "meteorite_grade_get": {
        "master_task_key": "grade_get",
        "scored": True,
        "grades_key": "get_grades",
        "rubric_artifact": "get_rubric",
        "response_format": "json",
        "output_type": "grades_encoded_notes",
        "response_schema": {
            "jobs": {
                "type": "list",
                "required": True,
                "items_schema": _ENCODED_CONSULT_JOB_ITEM_SCHEMA,
            },
        },
        "fallback_batch_size": 10,
        "pass_state": "METEORITE_PASSED_GET",
        "fail_state": "METEORITE_FAILED_GET",
        "error_state": "METEORITE_FAILED_TECHNICAL_GET",
        "save_prefix": "get",
        "pass_threshold": 6.0,
        "grading_mode": "scored",
        "context_format": "meteorite_grade_get_{index}",
        "entity_type": "job",
        "requires_candidate_key": True,
        "trigger_state": "METEORITE_PASSED_DO",
    },
```

⚠️ **Decision — duplicate scored schema fields on the alias, omit `agent_task`:** Alias owns orchestration + scoring shape so `TASK_CONFIG[alias]` is self-sufficient for pass/fail math once **AST-1221** routes by alias key. Prompt identity is **not** declared here (`agent_task` omitted) — content lookup uses `resolve_task_key_for_content` → master; **AST-1222** seeds grouping-only `agent_task` rows. Do **not** copy master's Gaze pass/fail (`PASSED_DO` etc.) onto the alias.

⚠️ **Decision — field-driven `trigger_state` on aliases, no new helper branches:** Set `"trigger_state": "METEORITE_PASSED_JD"` / `"METEORITE_PASSED_DO"` on the alias entries. `_dispatch_trigger_state_for_task_key` already falls through to `TASK_CONFIG[key]["trigger_state"]` when no per-key branch matches (`config.py` ~2878–2880); `api_admin._dispatch_task_key_form_meta` uses the same field. Do **not** add `if task_key == "meteorite_grade_do"` branches — that would be a meteorite-only inline rule contradicting field-driven resolve / `astral.standards.no-hardcoded-sets`. (AST-1055’s `meteorite_like` helper branch is a pre-existing pattern, not a binding precedent for new aliases.)

⚠️ **Decision — place aliases after `grade_get`, not after `meteorite_like`:** Masters must exist before alias keys in the literal dict so a human reading the file sees master → alias adjacency; load-time assert already requires masters present regardless of order.

⚠️ **Decision — expected `_TRANSITION_STATES_USED_BY_SCORED_TASKS` delta (benign):** Adding two `scored: True` aliases injects `METEORITE_FAILED_DO`, `METEORITE_FAILED_TECHNICAL_DO`, `METEORITE_FAILED_GET`, `METEORITE_FAILED_TECHNICAL_GET` into `_TRANSITION_STATES_USED_BY_SCORED_TASKS` (via `_task_config_transition_strings` on pass/fail/error). That flips `dispatch_claim_uses_score_floor` / admin `is_scored` defaults for those four states. Symmetric with classic `FAILED_DO` already in the set via `grade_do`; no `METEORITE_DISPATCH_TASKS` row claims a FAILED trigger. Pass outcomes (`METEORITE_PASSED_DO` / `METEORITE_PASSED_GET`) were already reachable via the former overlay / other scored meteorite tasks. Do **not** point any alias `not_ready_state` at its own claim trigger (see `evaluate_meteorite` comment ~615–623). Side-effect check: `_task_config_transition_strings` does **not** read `trigger_state`; both alias triggers are already in `PASSED_SCORE_GATED_STATES` and `JOB_STATES`, so `_dispatch_sort_by_for` / `dispatch_task_admin_defaults` resolve unchanged.

2. In `_DISPATCH_BATCH_CALL_MODE_ONE`, add `"meteorite_grade_do"` and `"meteorite_grade_get"` next to `"grade_do", "grade_get"` (same frozenset — batch_call_mode 1).

Do **not** change `METEORITE_DISPATCH_TASKS` (still `task_key: "grade_do"` / `"grade_get"`). Do **not** edit `SEED_CONFIG` meteorite INSERT strings. Do **not** add hardcoded frozenset entries for entity_type — aliases carry `"entity_type": "job"` so `_dispatch_entity_type_for_task_key` resolves via `TASK_CONFIG`. Do **not** edit `_dispatch_trigger_state_for_task_key` for these keys.

3. Verify Stage 2:

```bash
~/astral/.venv/bin/python -c "
from src.utils import config as c

assert c.is_task_alias('meteorite_grade_do') is True
assert c.is_task_alias('meteorite_grade_get') is True
assert c.resolve_task_key_for_content('meteorite_grade_do') == 'grade_do'
assert c.resolve_task_key_for_content('meteorite_grade_get') == 'grade_get'
assert c.resolve_task_key_for_content('grade_do') == 'grade_do'

do = c.TASK_CONFIG['meteorite_grade_do']
assert do['master_task_key'] == 'grade_do'
assert do['pass_state'] == 'METEORITE_PASSED_DO'
assert do['fail_state'] == 'METEORITE_FAILED_DO'
assert do['error_state'] == 'METEORITE_FAILED_TECHNICAL_DO'
assert do['trigger_state'] == 'METEORITE_PASSED_JD'
assert 'agent_task' not in do

get = c.TASK_CONFIG['meteorite_grade_get']
assert get['master_task_key'] == 'grade_get'
assert get['pass_state'] == 'METEORITE_PASSED_GET'
assert get['fail_state'] == 'METEORITE_FAILED_GET'
assert get['error_state'] == 'METEORITE_FAILED_TECHNICAL_GET'
assert get['trigger_state'] == 'METEORITE_PASSED_DO'
assert 'agent_task' not in get

assert c.METEORITE_GDL_OUTCOME_BY_TASK == {}
assert c.METEORITE_GDL_OUTCOME_BY_TASK.get('grade_do') is None

# Field-driven path — not a new per-key branch (masters still use helper branches + trigger_state None).
assert c.TASK_CONFIG['grade_do'].get('trigger_state') is None
assert c._dispatch_trigger_state_for_task_key('meteorite_grade_do') == 'METEORITE_PASSED_JD'
assert c._dispatch_trigger_state_for_task_key('meteorite_grade_get') == 'METEORITE_PASSED_DO'
d_do = c.dispatch_task_admin_defaults('meteorite_grade_do')
assert d_do['trigger_state'] == 'METEORITE_PASSED_JD'
assert d_do['entity_type'] == 'job'
assert d_do['batch_call_mode'] == 1
# Derived-set delta: alias fail/error strings now in scored transition set.
for st in (
    'METEORITE_FAILED_DO', 'METEORITE_FAILED_TECHNICAL_DO',
    'METEORITE_FAILED_GET', 'METEORITE_FAILED_TECHNICAL_GET',
):
    assert st in c._TRANSITION_STATES_USED_BY_SCORED_TASKS
    assert c.dispatch_claim_uses_score_floor(st) is True

assert all(
    e['task_key'] in ('grade_do', 'grade_get') or e['task_key'] not in (
        'meteorite_grade_do', 'meteorite_grade_get'
    )
    for e in c.METEORITE_DISPATCH_TASKS
)
# Explicit: Do/Get meteorite dispatch rows still shared keys until AST-1222
by = {(e['task_key'], e['trigger_state']): e for e in c.METEORITE_DISPATCH_TASKS}
assert ('grade_do', 'METEORITE_PASSED_JD') in by
assert ('grade_get', 'METEORITE_PASSED_DO') in by
assert ('meteorite_grade_do', 'METEORITE_PASSED_JD') not in by
"
~/astral/.venv/bin/python -m py_compile src/utils/config.py
```

**Ritual:** `code(AST-1220): meteorite_grade_do/get alias TASK_CONFIG + batch-mode`

## Self-Assessment

**Scope:** Single-Component — only `src/utils/config.py` (utils config contract + first-consumer alias literals + batch-mode frozenset).

**Conf:** high — field-driven `master_task_key` + `trigger_state`, load-time master/chain/outcome asserts, and scored twin field shape are concrete; Joan round-1 gaps (helper branches, vacuous overlay assert, derived-set silence) are closed in-plan.

**Risk:** Medium — emptying `METEORITE_GDL_OUTCOME_BY_TASK` before **AST-1221**/**AST-1222** land means in-flight meteorite Do/Get still keyed as `grade_do`/`grade_get` temporarily use classic Gaze outcomes; wrong alias pass/fail strings would mis-route meteorite state once siblings wire aliases (mitigated by new `JOB_STATES` asserts).

## Code rules check

- §1.3 DRY — one resolve helper, no per-pair maps; admin trigger via existing `TASK_CONFIG.trigger_state` fallback, not new branches.
- §1.4 / `astral.standards.no-hardcoded-sets` — alias links are `master_task_key` fields, not a meteorite-only dict; overlay emptied rather than dual-sourced; no meteorite-only `_dispatch_trigger_state_for_task_key` branches.
- §2.1 config source of truth — contract and first consumers live in `TASK_CONFIG`.
- §3.3 imports — utils only; no core/UI edits on this ticket.
- §3.5 naming — domain keys `meteorite_grade_do` / `meteorite_grade_get` (not ticket ids).
- Out of scope honored — no consult overlay retirement call-site (**AST-1221**), no seed/dispatch retarget (**AST-1222**), no UI audit (**AST-1185**).

## Revisions

### Revision 1 — 2026-08-06

Driven by: Joan `[plan-discuss] round=1 concern` (plan-rubric.v1 REVISE @ tip `f9d5f6d3`).

Changes:

- **fix-now:** Alias entries set field-driven `trigger_state` (`METEORITE_PASSED_JD` / `METEORITE_PASSED_DO`); deleted Stage 2 step that added `_dispatch_trigger_state_for_task_key` per-key branches.
- **discuss:** Extended Stage 1 alias-contract assert loop so job-entity aliases require `pass_state` / `fail_state` / `error_state` ∈ `JOB_STATES` (restores invariant lost when overlay empties).
- **discuss:** Documented expected `_TRANSITION_STATES_USED_BY_SCORED_TASKS` / `dispatch_claim_uses_score_floor` delta for the four meteorite FAILED_* strings; verify script asserts membership.
- **acceptable (carried):** QA note — do not exercise meteorite Do/Get on a tree with only AST-1220 merged.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1184/AST-1220-task-alias-config-contract-resolve-helpers`
**Plan path:** `docs/features/meteorite/ast-1220-task-alias-config-contract-resolve-helpers.md`

**Built tip:** `739bc8476c788578e29773341eca21521118169b` (`739bc847`)

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `5c7a567f` | task-alias resolve helpers + empty Do/Get overlay |
| 2 | `739bc847` | meteorite_grade_do/get alias TASK_CONFIG + batch-mode |

## Radia review — [code-rubric] revision=1

**Rubric:** code-rubric.v1 · **Publish ref tip:** `aa820952`

**Overall: CLEAN**

**What's solid:**

- Diff footprint is exactly the plan's single-row Files Changed table (`src/utils/config.py`) plus Betty's separate `merge-tests` commit (`docs/test-bible/**`, `tests/**`) — no scope creep, no consult/agent/dispatcher/seed touch (siblings AST-1221/AST-1222 honored).
- `is_task_alias` / `resolve_task_key_for_content` are field-driven, no meteorite-only link map; both closed Joan round-1 fix-now items verified live at tip: alias `trigger_state` is a literal field (no `_dispatch_trigger_state_for_task_key` per-key branches), and the Stage 1 assert loop requires job-entity alias `pass_state`/`fail_state`/`error_state` ∈ `JOB_STATES`.
- `METEORITE_GDL_OUTCOME_BY_TASK` emptied cleanly (single source of truth restored — outcomes live only on the alias entries); symbol kept per plan for AST-1221's import.
- No new imports added anywhere in the diff — layer import direction / no-cross-contamination hold trivially.
- Helpers placed with the other `TASK_CONFIG` accessor functions (public-then-helpers intact); alias entries inserted after `grade_get` per plan (masters-before-aliases readability, load-time assert enforces it regardless of order).
- `_DISPATCH_BATCH_CALL_MODE_ONE` extension reuses the existing frozenset pattern rather than inventing a new one; no run_next chain-membership shadow list introduced (`astral.dispatch.run-next-is-chain-authority` doesn't apply here — batch_call_mode, not hop succession).
- Commit hygiene: two `code(AST-1220)` commits touch only `src/utils/config.py`; Betty's `test(AST-1220)` + `merge-tests(AST-1220)` touch only `tests/`/`docs/test-bible/**` — `astral.git.engineer-test-tree-ban` and `astral.git.betty-no-src-or-features` both hold.
- `python3 -m py_compile src/utils/config.py` clean at tip.
- Full active-set sweep (65 active statutes: 18 universal + 47 scoped-applicable against this diff's `{utils, docs}` layers / `docs/features`, `docs/test-bible`, `src/utils/config.py`, `tests/**` paths) — zero `violates`, zero `needs-discussion`.

**Advisory (not fix-now, carried from Joan's plan-rubric):** alias entries duplicate scoring/schema fields (`response_schema`, `grades_key`, `rubric_artifact`, `output_type`, `context_format`, `fallback_batch_size`, `pass_threshold`) alongside the master instead of resolving them through `resolve_task_key_for_content`. Parent AC requires alias-owned orchestration so this is accepted, not reopened — flagging only as a live handoff note for AST-1221 to decide which fields route through the resolver vs. stay alias-local.

**Pattern conformance:** `pattern.config.config-block` — conforms (contract + first-consumer literals live in `TASK_CONFIG`, canonical_refs intact). `pattern.config.task-alias` — proposed, correctly unauthored (Archie approval is the parent's define-approved gate, not this child).

**Plan adherence:** Both stages match the plan's binding code blocks verbatim, including the Revision 1 fixes (field-driven `trigger_state`, `JOB_STATES` assert extension, documented `_TRANSITION_STATES_USED_BY_SCORED_TASKS` delta) that closed Joan's round-1 findings.

## Frame diff

(none — ticket description/AC unchanged; no findings to fold in)

context_tokens≈62000

— Radia
