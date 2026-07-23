# AST-958 — Todo-grab requires assignee Chuckles

- **Linear:** [AST-958](https://linear.app/astralcareermatch/issue/AST-958/todo-grab-requires-assignee-chuckles-agent-roles-joan-reborn-as)
- **Parent:** [AST-910](https://linear.app/astralcareermatch/issue/AST-910/agent-roles-joan-reborn-as-statute-validator-archie-identity)
- **Publish ref:** `origin/sub/AST-910/AST-958-todo-grab-assignee-chuckles`
- **Summary:** Close the Todo-only auto-claim loop: datt watcher and related skill/docs must grab a parent for dispatch only when status is **Todo** and assignee is already **Chuckles** (Susan sets both). Never auto-assign Chuckles from Todo alone or from Todo + Susan assignee. Independent of Joan / Archie children.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `~/team-chuckles/skills/rollcall/watch_linear.py` | Datt Todo silo + fetch + prepare gate: require Chuckles assignee; remove Todo auto-assign | watcher-runtime |
| `~/team-chuckles/skills/rollcall/WAKE_CHEATSHEET.md` | Datt row: Todo + assignee Chuckles only (no Susan→Chuckles auto-claim) | docs |
| `~/team-chuckles/docs/linear-state-consumers.md` | Todo parent enter/gates: Susan sets Todo **and** assignee Chuckles | docs |
| `~/team-chuckles/skills/do-all-the-things/SKILL.md` | Chat identity gate: Todo dispatch only when assignee Chuckles (align with cron) | skill |
| `docs/features/team-chuckles/ast-958-todo-grab-assignee-chuckles.md` | This plan (astral publish ref) | astral docs |

**Commit homes:** watcher + skill + team-chuckles docs land on **`team-chuckles`** `main`. Plan doc only on this astral **`sub/*`** ref (same pattern as AST-930 / AST-923).

**Exempt / out of scope:**

- Joan persona (**AST-919**), Archie identity table (**AST-922**).
- Astral product `src/`, `tests/`, bible.
- **wrap** PR Ready auto-assign path (`require_susan_pr_ready_transition` / `_wrap_prepare_pr_ready_parent`) — leave unchanged; this ticket is Todo-grab only.
- **fix** / **check** / **define** watcher rules (no Todo auto-claim).
- `dispatch-parent` gate already requires assignee Chuckles — do **not** rewrite that skill; only touch it if a grep proves a contradictory Todo-only claim (then stop and comment on AST-910).

## Stage 1: Inventory the Todo auto-claim surfaces (read-only confirm)

**Done when:** Builder has listed every live path that can spawn datt / dispatch on parent **Todo** without already having assignee Chuckles, and confirmed the Stage 2 edit list matches that inventory (no silent extra files).

1. From `~/team-chuckles`, run and keep the hit list for Stage 2:

```bash
rg -n 'require_susan_todo_transition|_datt_prepare_todo_parent|_susan_status_approved|_prepare_susan_status_parent|state_linear\.pop\("assignee"|if state == "Todo"' skills/rollcall/watch_linear.py
rg -n 'Todo.*Chuckles|assignee Chuckles|auto.?assign|Susan signal|already Todo' skills/rollcall/WAKE_CHEATSHEET.md docs/linear-state-consumers.md skills/do-all-the-things/SKILL.md
```

2. Confirm these **current** behaviors (as of plan time) are the bug class:

| Location | Bug behavior |
|----------|--------------|
| `_issue_in_silo` `rule_name == "datt"` + `state == "Todo"` | Returns `True` with **no** assignee check |
| `_fetch_state_prompt_issues` when `need_datt_todo` + `state == "Todo"` | `state_linear.pop("assignee", None)` — fetches **all** Todo parents |
| `_susan_status_approved` fallback + `_datt_prepare_todo_parent` → `_prepare_susan_status_parent` | On approved Todo, **auto-assigns Chuckles** if assignee is Susan (or already Chuckles) |
| Module docstring for `require_susan_todo_transition` | Documents “Susan/Chuckles assignee; assigns Chuckles” |

3. Confirm **already correct** (no code change required unless Stage 1 grep finds contradiction):

| Location | Correct behavior |
|----------|------------------|
| `do-all-the-things` cron + §1 Cron line | Todo **and** assignee Chuckles |
| `do-all-the-things` §2 dispatch | `If parent Todo and assignee Chuckles` |
| `dispatch-parent` When to run / §2a | Todo + assignee Chuckles; stop otherwise |
| `define-parent` | Stays Discussion until Susan sets Todo + Chuckles for dispatch |

⚠️ **Decision:** Fix **datt Todo only** inside `watch_linear.py`. Do **not** change `_wrap_prepare_pr_ready_parent` or wrap’s use of `_prepare_susan_status_parent` in this ticket. Prefer a **datt-specific** prepare function rewrite over adding flags to the shared wrap helper.

## Stage 2: Harden `watch_linear.py` datt Todo gate

**Done when:** A parent in **Todo** with assignee Susan (or unassigned / engineer) is never assigned Chuckles and never spawned by datt; a parent in **Todo** with assignee Chuckles still matches and can spawn; **In Progress** + Chuckles resume path unchanged; wrap PR Ready path byte-identical in behavior.

1. In `~/team-chuckles/skills/rollcall/watch_linear.py`, update the module docstring bullet for `require_susan_todo_transition` to:

   > datt Todo: spawn only when status is Todo **and** assignee is already Chuckles (Susan set both). Never auto-assign Chuckles from Todo alone.

2. In `_issue_in_silo`, change the datt Todo branch from `return True` to:

```python
if state == "Todo":
    return _is_chuckles_assignee(issue)
```

   Keep the In Progress branch as `_is_chuckles_assignee(issue)`.

3. In `_fetch_state_prompt_issues`, when `need_datt_todo` is true, **do not** strip assignee for Todo. Set assignee filter to Chuckles for **both** Todo and In Progress:

```python
if need_datt_todo:
    state_linear["assignee"] = "me"
```

   Delete the `if state == "Todo": state_linear.pop("assignee", None)` / `elif state == "In Progress": …` split for this flag.

4. Replace the body of `_datt_prepare_todo_parent` so it **does not** call `_prepare_susan_status_parent` and **never** calls `_linear_assign_issue`. Binding behavior:

```python
def _datt_prepare_todo_parent(
    token: str, issue: dict[str, Any], susan_email: str, chuckles: dict[str, str]
) -> tuple[bool, str]:
    """Todo grab: Susan already set assignee Chuckles. No auto-assign."""
    del token, susan_email, chuckles  # signature kept for call-site compatibility
    if _state_name(issue) != "Todo":
        return False, ""
    if not _is_chuckles_assignee(issue):
        return False, ""  # silent skip — not Susan's Chuckles-assignee signal
    return True, ""
```

   ⚠️ **Decision:** Drop the Susan status-history requirement for datt Todo. Assigneeship **Chuckles** while status **Todo** is the sole auto-claim signal (matches parent AC and original brief). History-based auto-assign was the loop fuel when Linear omitted transitions.

5. Leave `_prepare_susan_status_parent`, `_susan_status_approved`, and `_wrap_prepare_pr_ready_parent` **unchanged** so wrap keeps its existing PR Ready behavior.

6. Keep the call site that invokes `_datt_prepare_todo_parent` when `need_datt_todo and state == Todo` (defense in depth after the assignee=me fetch). If `chuckles_user = _viewer_user(token)` becomes unused for Todo-only after the rewrite, still pass `chuckles_user` into the function to avoid drive-by call-site churn — or simplify the call to drop unused viewer fetch **only if** Todo is the sole consumer of `chuckles_user` in that loop branch and wrap still fetches its own. Prefer smallest diff: keep fetching `chuckles_user` when `need_datt_todo` if the existing structure still needs it for nothing—if Todo prepare no longer uses it and wrap is a separate `need_wrap_pr` branch, remove the Todo-only `_viewer_user` fetch when it becomes dead code in that block.

7. Do **not** change `watch_rules/datt.json` flags (`require_susan_todo_transition: true` stays) — the flag still means “run the datt Todo prepare gate”; only gate semantics change. Optionally tighten the Todo prompt string to say “Todo + assignee Chuckles only” in one short clause — allowed, not required.

## Stage 3: Align skill + cheatsheet + state-consumer docs

**Done when:** Grep for the old Todo auto-claim phrasing returns no live instructions; datt / do-all-the-things prose matches Stage 2.

1. In `~/team-chuckles/skills/rollcall/WAKE_CHEATSHEET.md`, replace the **datt** watcher-ownership row so Todo is described as:

   > **Todo** parent + assignee **Chuckles** (Susan set both) → dispatch; **In Progress** + Chuckles → resume

   Remove wording that Susan Todo transition **or** Todo+Susan assignee causes an assign-to-Chuckles grab.

2. In `~/team-chuckles/docs/linear-state-consumers.md` § Todo:

   - **Enter (parent):** Susan moves approved parent to **Todo** **and** assigns **Chuckles** → `[datt]` / `do-all-the-things` / `dispatch-parent`.
   - **Gates:** note that `watch_linear` datt Todo requires assignee Chuckles (no auto-assign).

3. In `~/team-chuckles/skills/do-all-the-things/SKILL.md` §1 **Chat** bullet, change:

   - From: `else if **Todo** → dispatch (§2)`
   - To: `else if **Todo** and assignee **Chuckles** → dispatch (§2); else if **Todo** and assignee ≠ Chuckles → **stop** (no auto-assign, no comment spam)`

   Cron line already correct — leave it. §2 already gates on Chuckles — leave the dispatch sentence; do not duplicate a novel gate elsewhere.

4. From `~/team-chuckles`, verify:

```bash
rg -n 'assigns Chuckles|Susan/Chuckles assignee|Todo \(Susan → Todo\)|already Todo \+ Susan' \
  skills/rollcall/watch_linear.py \
  skills/rollcall/WAKE_CHEATSHEET.md \
  docs/linear-state-consumers.md \
  skills/do-all-the-things/SKILL.md
```

   Allowed leftovers: historical notes clearly marked obsolete (prefer zero). Wrap’s “assigns Chuckles” for PR Ready may remain in the module docstring for `require_susan_pr_ready_transition` only.

## Stage 4: team-chuckles commit + host note

**Done when:** Stage 2–3 edits are committed on `team-chuckles` `main` and pushed to `origin/main`; Linear Code Complete comment (later, build-child) can name the SHA; plan remains the only astral-sub commit for this ticket’s plan phase.

1. In `~/team-chuckles` (do not touch unrelated dirty files — commit **only** the Stage 2–3 paths listed in Files Changed):

```bash
git add \
  skills/rollcall/watch_linear.py \
  skills/rollcall/WAKE_CHEATSHEET.md \
  docs/linear-state-consumers.md \
  skills/do-all-the-things/SKILL.md
git commit -m "$(cat <<'EOF'
code(AST-958): Todo-grab requires assignee Chuckles (no auto-assign)

EOF
)"
git push origin HEAD:main
```

2. Note for operators: datt watcher loads `watch_linear.py` from the rollcall path used by `wake-up-chuck*.sh` / tmux `chuck` session. After push, restart the datt pane (or full `wake-up-chuck`) on the chuckles host so the running process picks up the file — commit alone does not reload an already-running Python process.

3. Do **not** commit astral product code. Do **not** push `origin/dev`.

## Execution contract

- Execute stages in order; do not expand into wrap / Joan / Archie / product `src/`.
- If Stage 1 inventory finds another Todo auto-claim path not listed in Files Changed, **stop** and comment on **AST-910** with the Stage N blocked format — do not silently add files.
- If `dispatch-parent` is found to contradict Todo+Chuckles, stop and escalate — do not “fix” it under this ticket without plan revision.
- team-chuckles edits commit there; astral publish ref gets plan (and later review stubs) only.

## Self-Assessment

**Scope:** `Single-Component` — team-chuckles datt Todo claim path (`watch_linear.py` + aligned skill/docs); no astral product runtime.

**Conf:** `high` — bug loci are concrete (`_issue_in_silo` Todo `return True`, assignee pop, `_datt_prepare_todo_parent` → auto-assign); AC and parent brief name the exact contract (Todo **and** assignee Chuckles).

**Risk:** `Medium` — wrong gate would stall legitimate Susan→dispatch until assignee is Chuckles (fail-closed, acceptable) or, if under-fixed, leave the re-grab loop; wrap left untouched to avoid collateral finish-up breakage.

## Self-review vs ASTRAL_CODE_RULES

- §1.1 in-scope only: Todo-grab surfaces listed above — satisfied; wrap/Joan/Archie excluded.
- §1.3 DRY: datt-specific prepare rewrite avoids overloading wrap’s shared helper with a Todo-only flag — intentional duplication of a tiny gate vs shared mutation.
- No config / batch / state-machine / import-layer product changes — N/A for astral `src/`.
- Docs: plan under `docs/features/team-chuckles/` — satisfied.
- No conflict with `orch.roles.chuckles-never-ticket-assignee` as child assignee law — this ticket changes **when** Chuckles may be auto-claimed onto **parents** for dispatch, not engineer child assignee rules.

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-910/AST-958-todo-grab-assignee-chuckles` @ `19be0ab`  
**Live:** `team-chuckles` `main` @ `c417fc0`

### What’s solid

- Stage 2 gates land exactly as planned: `_issue_in_silo` Todo → `_is_chuckles_assignee`; fetch keeps `assignee: "me"` for Todo + In Progress; `_datt_prepare_todo_parent` no longer calls `_prepare_susan_status_parent` / never auto-assigns; docstring updated.
- Stage 3: WAKE ownership row, consumers Todo enter/gates, datt Chat bullet aligned; Stage 3 old-phrasing greps empty; wrap PR Ready path untouched; `py_compile` clean.
- Boundaries held (Joan / Archie / product `src/` out); Self-Assessment **Single-Component** matches; fail-closed on Todo≠Chuckles is the intended risk tradeoff.
- Astral tip is plan (+ Betty bible entry) only — correct commit-home split.

### Issues

| Severity | Item |
|----------|------|
| **advisory** | `WAKE_CHEATSHEET.md` short wake-tag row still says `` `**Todo** → dispatch` `` without “+ assignee Chuckles”; the ownership table row (Stage 3 target) is correct. Optional one-line tighten. |
| **advisory** | Ops: restart datt watcher pane on chuckles host so running Python loads `watch_linear.py` (Betty + build stub already note this). |

### Recommended actions

| Action | Owner |
|--------|-------|
| Optional WAKE short-tag wording | Engineer / Chuckles if desired |
| Restart datt pane after land | Ops / Chuckles |

**fix-now:** none.  
**ASTRAL_CODE_RULES:** §1.1 / §1.3 (datt-specific prepare vs wrap helper) satisfied; product layers N/A.

## Resolution

**Date:** 2026-07-23  
**Review tip:** Radia `docs(AST-958): Radia review — clean` @ `fb188ac` on `origin/sub/AST-910/AST-958-todo-grab-assignee-chuckles`. Live code remains `team-chuckles@c417fc0` (+ advisory doc follow-up below).

| Severity | Disposition |
|----------|-------------|
| **fix-now** | none — no product changes |
| **advisory** WAKE short wake-tag row | Addressed — `[datt]` row now **Todo** + assignee **Chuckles** → dispatch (`team-chuckles` commit after resolve) |
| **advisory** restart datt pane | Ops note only — not code; still required on chuckles host after land |

No discuss items. No test-tree changes.
