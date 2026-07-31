# AST-807 — UAT: AST-799 missing from deploy tooltip after prep-uat (record-landed-parent python)

<!-- linear-archive: AST-807 archived 2026-07-22 -->

## Linear archive (AST-807)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-807/uat-ast-799-missing-from-deploy-tooltip-after-prep-uat-record-landed  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-799 — Over-validation on entity type for candidate  
**Blocked by / blocks / related:** parent: AST-799

### Description

## What failed

After AST-799 prep-uat, Susan reports the parent does not appear in the admin deploy environment label tooltip list of merged UAT tickets (same class as AST-788 / AST-801): *"I don't see this in the list of UAT tickets that have been merged."*

`prep-uat-land.sh` pushed `origin/dev` with the AST-799 ftr merge, but `record-landed-parent.sh` then failed running `rebuild_merge_ticket_log.py` with `ModuleNotFoundError: dotenv` because it invoked system `python3` instead of the repo `.venv`. The merge ticket log on `origin/dev` was never rebuilt to include **AST-799**.

## Expected

After prep-uat completes for AST-799, `data/merge_ticket_log.json` on `origin/dev` includes **AST-799** (AST-800 rebuild semantics), and hovering the deploy env label lists AST-799 among User Testing parents whose ftr is on dev.

## Repro

1. Land AST-799 via prep-uat (`ftr/AST-799-dispatch-task-entity-type-validation` merged to `origin/dev`).
2. Open Admin (local dev or staging with `LINEAR_API_KEY` set).
3. Hover the deploy environment label footer tooltip.
4. **AST-799** is missing from the merge ticket list.

## Parent AC (quoted inline)

> **Scheduled Actions edit path:** From Admin → Scheduled Actions, an existing **inflow_discovery** row can be edited and saved without error when values match config defaults.

(Ship visibility: Susan must be able to confirm AST-799 is on the integration line via the deploy tooltip UAT list — prep-uat record step must not fail silently after dev push.)

## Boundaries

* Does **not** change AST-804 dispatch validation product code.
* Does **not** redesign tooltip UX (AST-691/798).
* Does **not** alter AST-800 rebuild algorithm — only ensure prep-uat record step can run it reliably.

### Comments

#### betty — 2026-06-25T17:28:18.500Z
## QA test manifest (Tests Ready)

1. **Pytest (required):**
```bash
.venv/bin/python -m pytest \
  tests/component/scripts/test_rebuild_merge_ticket_log.py \
  tests/component/scripts/test_record_landed_parent.py \
  -q
```

**Coverage map (AST-807):**
- **`TestRecordLandedParentShell::test_record_landed_parent_uses_venv_python`** — shell resolves `${ASTRAL_PYTHON:-$REPO_ROOT/.venv/bin/python}`; no bare `python3 "$REBUILD"`
- **`TestRecordLandedParent::test_record_landed_parent_blocks_without_venv`** — missing venv → `BLOCKED` with `setup_dev.sh` hint before rebuild

**Regression (same module):** AST-805 `--landing-parent` flag + temp-repo rebuild commit; AST-800 rebuild-not-append wiring; `test_record_landed_parent_honors_astral_python_override`; `test_record_landed_parent_missing_rebuild_script_blocks`.

**Bible shasum (origin/sub/AST-799/AST-807-uat-prep-uat-merge-ticket-log-rebuild-uses-venv):**
- docs/test-bible/dev/record_landed_parent.md — 73b38be09240d76f190859368b099c2b3518d9c17ddc2579244b25d420ae331f

**Publish:** origin/sub/AST-799/AST-807-uat-prep-uat-merge-ticket-log-rebuild-uses-venv @ fed45c7 (merge-tests(AST-807): origin/tests d65cdf1)

#### chuckles — 2026-06-25T17:23:25.999Z
**validate-plan: APPROVED**

Plan is focused: venv Python in `record-landed-parent.sh` only, matches `run_component_tests.sh` pattern, BLOCKED on missing venv. Betty manifest documented in Stage 2.

— Chuckles

#### ada — 2026-06-25T17:10:11.987Z
Plan: [ast-807-uat-ast-799-missing-from-deploy-tooltip-after-prep-uat-record-landed-parent-python.md](https://github.com/susansomerset/astral/blob/sub/AST-799/AST-807-uat-prep-uat-merge-ticket-log-rebuild-uses-venv/docs/features/foundation/ast-807-uat-ast-799-missing-from-deploy-tooltip-after-prep-uat-record-landed-parent-python.md)

**Self-assessment**
- **Scope:** minor — `record-landed-parent.sh` only; resolve Python via `ASTRAL_PYTHON` / `.venv/bin/python` instead of system `python3`.
- **Conf:** high — `ModuleNotFoundError: dotenv` on bare `python3` is the confirmed root cause; matches `run_component_tests.sh` venv pattern.
- **Risk:** low — prep-uat record path only; `BLOCKED` if venv missing prevents silent log skip.

Two stages: (1) venv interpreter in shell + manual rebuild verify, (2) Betty bible rows for static venv guard. No rebuild algorithm or **AST-804** changes.

---

_Implementation detail may live in git history on `origin/dev`._
