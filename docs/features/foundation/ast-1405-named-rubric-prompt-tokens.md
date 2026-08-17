# AST-1405 — Named rubric prompt tokens

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1405/named-rubric-prompt-tokens-reintroduce-the-specific-rubric-tokens
**Parent:** [AST-1404](https://linear.app/astralcareermatch/issue/AST-1404/reintroduce-the-specific-rubric-tokens) — Reintroduce the specific rubric tokens
**Publish ref:** `sub/AST-1404/AST-1405-named-rubric-prompt-tokens`

Register five named prompt tokens on the existing `TOKEN_SOURCES` registry, pin each to a fixed rubric owner, and resolve them through the same `rubric_criteria_for_token` / `_value_to_str` path `{$RUBRIC_VECTORS}` already uses. Pickers already list `TOKEN_SOURCES` keys — no UI list. `{$RUBRIC_VECTORS}` stays task-derived. Seed prompt bodies are not rewritten.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add five `TOKEN_SOURCES` rows with `source: rubric` + `owner_task_key` pin; teach `resolve_tokens` rubric branch to honor the pin and to silence missing-candidate warnings for pinned names (AST-1396 contract) | utils |

**Out of scope (do not touch):**

| File / area | Why |
|-------------|-----|
| `data/admin/agent_task.json` / seed prompt bodies | Ticket + parent: tokens become available; Susan inserts them |
| Frontend pickers (`TokenTextarea`, Manage Agents / Manage Tasks pages) | `/agents/meta/tokens` → `get_manage_agents_tokens()`; `/tasks/meta/tokens` → `get_tokens()` — both already derive from `TOKEN_SOURCES` |
| `src/core/candidate.py` `rubric_criteria_for_token` / `rubric_criteria_for_task` | Existing current-vector read path; named tokens call it with a pinned owner |
| `src/core/agent.py` `do_task` assembly | Substitution already goes through `resolve_tokens` |
| Rubric storage, craft, scoring, Artifacts, vector-feedback injection | Parent boundaries |
| `JOB_TOKEN_CONFIG` / `ANALYSIS_*` tokens | Different surface (job-scoped consult analysis text) |
| `tests/` / bible | Betty. Existing `TestAst723RubricVectorsToken.test_legacy_per_artifact_rubric_tokens_removed` currently asserts `GET_RUBRIC` / `DO_RUBRIC` / `LIKE_RUBRIC` are **absent** — that assertion is invalidated by this ticket; Betty revises it. Engineer does not patch tests. |

## Owner pins (authoritative)

Pin values are existing consumer `task_key`s from `RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY` — do not invent new owner strings, do not pin craft_* keys, do not pin meteorite or job-list owners.

| Token name | `owner_task_key` | Artifact key (do not put this on the registry row) |
|------------|------------------|-----------------------------------------------------|
| `GET_RUBRIC` | `grade_get` | `get_rubric` |
| `DO_RUBRIC` | `grade_do` | `do_rubric` |
| `LIKE_RUBRIC` | `grade_like` | `like_rubric` |
| `JD_RUBRIC` | `evaluate_jd` | `jobdesc_rubric` — **not** `evaluate_meteorite` / `meteorite_jobdesc_rubric` |
| `PREFILTER_RUBRIC` | `prefilter_company` | `company_prefilter` — new name; do **not** also register `COMPANY_PREFILTER` |

Do **not** register: `JOBLIST_RUBRIC`, `COMPANY_PREFILTER`, `JOBDESC_RUBRIC`.

`RUBRIC_VECTORS` stays `{"source": "rubric"}` with **no** `owner_task_key` — owner remains `rubric_owner_task_key(task_key)` (running-task owner).

⚠️ **Decision:** Spec pin key is `owner_task_key` (not `rubric_owner_task_key`). `rubric_owner_task_key` is already the function that maps a *running* task to its owner. The registry field is a fixed pin, not that lookup. Rejected: a second dict of named tokens outside `TOKEN_SOURCES` (would violate `astral.standards.no-hardcoded-sets` / config-as-source-of-truth). Rejected: `source: "named_rubric"` (parent: small extension of existing `source: rubric`, no new catalog shape).

## Stages

### Stage 1: Register pins and resolve them

**Done when:** `get_tokens()` and `get_manage_agents_tokens()` include the five names and exclude the three forbidden legacy names; `resolve_tokens("{$GET_RUBRIC}", cd, "grade_like")` with a candidate that has GET vectors substitutes GET (not LIKE); `{$RUBRIC_VECTORS}` on `grade_like` still substitutes LIKE; Ad Hoc-style `resolve_tokens("{$GET_RUBRIC}", {}, "adhoc")` returns `""` and does not log a missing-candidate / unresolved warning.

1. In `src/utils/config.py` `TOKEN_SOURCES`, immediately after the `RUBRIC_VECTORS` row, insert these five entries (keep `RUBRIC_VECTORS` itself unchanged except the comment on that row may stay). Do not reorder other keys.

```python
    # Resolved from rubric_vector rows for active task owner (AST-723).
    "RUBRIC_VECTORS":       {"source": "rubric"},
    # AST-1405: named pins — same serialize path as RUBRIC_VECTORS; owner is the pin, not the running task.
    "GET_RUBRIC":           {"source": "rubric", "owner_task_key": "grade_get"},
    "DO_RUBRIC":            {"source": "rubric", "owner_task_key": "grade_do"},
    "LIKE_RUBRIC":          {"source": "rubric", "owner_task_key": "grade_like"},
    "JD_RUBRIC":            {"source": "rubric", "owner_task_key": "evaluate_jd"},
    "PREFILTER_RUBRIC":     {"source": "rubric", "owner_task_key": "prefilter_company"},
```

2. In the same file, the `TOKEN_SOURCES` block header currently says adding a new token is one registry entry with no code change. After this stage, that remains true for a *sixth* named rubric token (add a row with `source: rubric` + `owner_task_key`). Leave the header; do not add a parallel named-token list.

3. In `resolve_tokens` `_replace`, replace **only** the `if spec["source"] == "rubric":` branch. Keep the late import of `rubric_criteria_for_token` (existing utils → core cycle break). Exact replacement:

```python
        if spec["source"] == "rubric":
            from src.core.candidate import rubric_criteria_for_token

            pinned = spec.get("owner_task_key")
            owner = pinned or rubric_owner_task_key(task_key)
            if not owner:
                _log.warning("Token {$%s} unresolved — task %r has no rubric owner", name, task_key)
                return ""
            cid = (candidate_data or {}).get("_astral_candidate_id") or ""
            if not cid:
                # AST-1405 / AST-1396: pinned names with no candidate in context (cd == {})
                # are expected empty — do not spam missing-id warnings. Unpinned
                # RUBRIC_VECTORS keeps the existing missing-id warning.
                if pinned and not candidate_data:
                    return ""
                _log.warning("Token {$%s} unresolved — missing candidate id (task=%s)", name, task_key)
                return ""
            return _value_to_str(rubric_criteria_for_token(cid, owner))
```

4. Do **not** change the candidate / config / output_type / chain / job / pronoun branches. Do **not** add a `warn_empty` kwarg. Do **not** skip substitution (leaving `{$GET_RUBRIC}` literal would flip `_enrich_tasks` `task_ready` via leftover-`{$…}` regex — same AST-1396 constraint).

5. Do **not** warn when a candidate is present and the pinned rubric list is empty — `_value_to_str([])` already returns `""`; `RUBRIC_VECTORS` already behaves that way. AC2 forbids an empty stub **when vectors exist**, not when they do not.

⚠️ **Decision:** Silence the missing-cid warning for **pinned** names only, and only when `candidate_data` is falsy (`{}` from `_enrich_tasks("")` and `_resolve_adhoc` with no candidate). Truthy token views that lack `_astral_candidate_id` still warn. `{$RUBRIC_VECTORS}` warning behavior is unchanged (AC4). Rejected: silencing all rubric warnings; rejected: gating on missing cid alone without the `pinned` check (would quiet `RUBRIC_VECTORS` on Ad Hoc load of owner tasks).

6. Hand-verify (no test-tree edits) after the change, from the epic worktree:

```bash
python3 - <<'PY'
from src.utils.config import TOKEN_SOURCES, get_tokens, get_manage_agents_tokens, resolve_tokens, rubric_owner_task_key

named = ("GET_RUBRIC", "DO_RUBRIC", "LIKE_RUBRIC", "JD_RUBRIC", "PREFILTER_RUBRIC")
forbidden = ("JOBLIST_RUBRIC", "COMPANY_PREFILTER", "JOBDESC_RUBRIC")
for n in named:
    assert TOKEN_SOURCES[n]["source"] == "rubric"
    assert TOKEN_SOURCES[n]["owner_task_key"]
    assert n in get_tokens()
    assert n in get_manage_agents_tokens()
for n in forbidden:
    assert n not in TOKEN_SOURCES
assert TOKEN_SOURCES["RUBRIC_VECTORS"] == {"source": "rubric"}
assert rubric_owner_task_key("grade_like") == "grade_like"
# Pin independence: named GET owner is grade_get even when the running task is LIKE.
assert TOKEN_SOURCES["GET_RUBRIC"]["owner_task_key"] == "grade_get"
# No-candidate silence: empty cd, pinned name → empty string (warnings checked by not exploding).
assert resolve_tokens("{$GET_RUBRIC}", {}, "adhoc") == ""
assert resolve_tokens("{$RUBRIC_VECTORS}", {}, "adhoc") == ""
print("ast-1405 registry ok")
PY
```

If any assert fails, **stop** and comment on **parent AST-1404** with the Stage-blocked format — do not invent a second registry or change picker APIs.

## Execution contract

The plan is binding. The agent:

- Executes steps in order within a stage, and stages in order across the plan.
- Does not skip, reorder, combine, or expand steps.
- Does not add files, modules, configs, or dependencies that aren't in the plan.
- When a step is ambiguous, contradicts another step, references something that doesn't exist, or fails when executed literally — **stops, comments on the Linear parent issue, and waits.** No fix-on-the-fly.
- Completes the stage on the epic worktree, commits, and publishes to `origin/sub/AST-1404/AST-1405-named-rubric-prompt-tokens`.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1405
**Overall:** APPROVED
**Publish ref:** `sub/AST-1404/AST-1405-named-rubric-prompt-tokens` @ `ba66a4c7d1cf73960035e77553483bfde6fc8834`

## Traceability
AC1–6 → Stage 1 (`TOKEN_SOURCES` five pinned `source: rubric` rows + `resolve_tokens` rubric-branch pin/`owner_task_key` + AST-1396 silence for falsy `candidate_data` only).

## Findings

### acceptable
- **Location:** Stage 1 hand-verify snippet  
  **Finding:** Inline assert block checks registry membership and no-candidate silence but not live `resolve_tokens(..., cd, "grade_like")` pin-independence with a populated candidate.  
  **Recommendation:** Engineer may run the Stage “Done when” REPL check before publish; not a plan gap — implementation steps are exact.

- **Location:** Plan doc (no formal self-assessment block)  
  **Finding:** No conf/risk axes section; scope is single-file `utils` registry extension with explicit decisions and out-of-scope table.  
  **Recommendation:** Acceptable for estimate 3; no `!!-NONE` escalation trigger.

**Considered (in-session):** Universal orch.* pipeline/git/roles statutes — all `conforms` (plan-only pass; engineer assignee restored after approval). Scoped: `astral.config.config-source-of-truth`, `astral.standards.no-hardcoded-sets`, `astral.standards.in-scope-only`, `astral.standards.utils-data-late-import-only` — `conforms` (names/pins in `TOKEN_SOURCES`; explicit boundaries; preserves late `rubric_criteria_for_token` import). `astral.layers.ui-config-driven-business-logic` — `conforms` (pickers already derive from registry via `get_tokens` / `get_manage_agents_tokens`; no parallel UI list). Parent-cited `astral.agent.do-task-delegation` — `conforms` by boundary (no `core/` edits; substitution stays on existing `resolve_tokens` / `do_task` path). Remaining scoped astral.* corpus — excluded (layer/path/change_type mismatch on `utils`-only footprint) or `conforms` where considered. Pattern `pattern.config.config-block` — matches solution shape.

context_tokens≈18500

## Review (build stub)

**Publish ref:** `origin/sub/AST-1404/AST-1405-named-rubric-prompt-tokens`

| Stage | Commit | Summary |
|-------|--------|---------|
| plan | `ba66a4c7` | Plan doc |
| Joan | `f58ea6b7` | validate APPROVED |
| 1 | `310f5e72` | Five named `TOKEN_SOURCES` pins; `resolve_tokens` honors pin and AST-1396 silence |

**Built:** `src/utils/config.py` only.
**Tip:** `310f5e72` (product); this stub follows on the same publish ref.
