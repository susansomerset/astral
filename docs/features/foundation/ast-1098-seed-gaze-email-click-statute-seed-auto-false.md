# Seed gaze_email CLICK + statute seed-auto-false

**Linear:** [AST-1098](https://linear.app/astralcareermatch/issue/AST-1098/seed-gaze-email-click-statute-seed-auto-false-gnarly-looking-deploy)  
**Parent:** [AST-1093](https://linear.app/astralcareermatch/issue/AST-1093) — Gnarly looking deploy logs on railway  
**Publish ref:** `sub/AST-1093/AST-1098-seed-gaze-email-click-statute-seed-auto-false`

Correct the AST-1088 seed that set the shared null-candidate `gaze_email` `dispatch_task` to AUTO-on (every-tick scheduler claim → Gmail `invalid_scope` log spam). Config + provision seed CLICK; boot reconcile flips an already-stuck AUTO shared row back to CLICK; land Archie-approved canon statute `astral.dispatch.seed-auto-false`. Does not own Gmail scopes, Railway severity cosmetics, or meteorite/gaze runner logic.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `GAZE_EMAIL_CONFIG["auto_mode"]` → `False`; assert False; assert other in-tree seed catalogs stay False | utils |
| `src/core/dispatcher.py` | `ensure_gaze_email_dispatch_task`: on existing shared row with AUTO on, `update_dispatch_task(..., auto_mode=False)`; return `reconciled` | core |
| `canon/statutes/astral/dispatch/astral.dispatch.seed-auto-false.md` | New active scoped statute (SCHEMA + AUTHORING) | docs/canon |
| `canon/statutes/README.md` | Add statute to harvested corpus table; bump active count | docs/canon |
| `canon/statutes/HARVEST.md` | Add crosswalk row for the new statute; bump counts | docs/canon |

## Stage 1: Config seed CLICK

**Done when:** `GAZE_EMAIL_CONFIG["auto_mode"]` is `False` with a module assert; the only former `True` product seed for dispatch AUTO in `config.py` is corrected; meteorite + candidate-stage seed catalogs remain `False` (asserted).

1. In `src/utils/config.py`, in `GAZE_EMAIL_CONFIG`, change `"auto_mode": True` to `"auto_mode": False`. Update the nearby comment so it states seed is CLICK (AST-1098 / parent seed law), not AUTO.
2. Immediately after the existing `GAZE_EMAIL_CONFIG` asserts, add:
   - `assert GAZE_EMAIL_CONFIG["auto_mode"] is False`
3. Immediately after that (same stage), add asserts that every entry in `METEORITE_DISPATCH_TASKS` has `auto_mode` falsy, and every entry in `CANDIDATE_STAGE_DISPATCH.values()` that has an `"auto_mode"` key has it falsy. Do **not** change those catalogs’ values unless an assert fails (on tip they are already `False`).
4. Do **not** change `TASK_CONFIG["gaze_email"]` shape, admin-defaults special-case, Gmail scopes, or runner keys.

⚠️ **Decision:** AC4 is satisfied by (a) flipping the sole `True` seed (`GAZE_EMAIL_CONFIG`) and (b) locking meteorite/stage seed catalogs with asserts — not by inventing a runtime scanner over every `save_dispatch_task` call site. Admin UI create can still accept AUTO when an operator sets it (AC6 / Boundaries).

## Stage 2: Provision reconcile shared gaze_email → CLICK

**Done when:** Fresh insert of the null-candidate `gaze_email` row uses `GAZE_EMAIL_CONFIG["auto_mode"]` (False). If that shared row already exists with AUTO on, `ensure_gaze_email_dispatch_task` (via `provision_gaze_email_dispatch_task` / `start_scheduler`) forces `auto_mode=False` through `database.update_dispatch_task` and reports `reconciled: 1`. No other `dispatch_task` rows are rewritten.

1. In `src/core/dispatcher.py`, in `ensure_gaze_email_dispatch_task`, when the shared null-candidate row for `GAZE_EMAIL_CONFIG["task_key"]` is found:
   - If `bool(existing.get("auto_mode"))` is true: call `database.update_dispatch_task(int(existing["id"]), auto_mode=False)` (use the same `database` import style already used for `save_dispatch_task` in this function).
   - Return dict shape extended with `"reconciled": 1` (and keep `added: 0`, `skipped: 1` or set `skipped: 0` — pick one consistent convention: **`added: 0`, `skipped: 0`, `reconciled: 1`, `skipped_missing_config: 0`, `id`: existing id** when a flip occurred; when already CLICK: **`added: 0`, `skipped: 1`, `reconciled: 0`, …**).
   - When inserting a new row, keep `auto_mode=bool(GAZE_EMAIL_CONFIG["auto_mode"])` and include `"reconciled": 0` on the success return.
   - When `skipped_missing_config`, include `"reconciled": 0`.
2. Do **not** change `get_due_tasks`, `_dispatch_one`, `run_gaze_email`, admin PATCH semantics, or meteorite/stage ensure loops.
3. Do **not** reconcile any candidate-scoped `gaze_email` rows (there should be none for this task); match only `task_key == tk` and null/blank `candidate_id` as today.

⚠️ **Decision:** Reconcile runs on every ensure/provision for this **shared** row only. That clears bad-seed AUTO at boot (AC3). Operator AUTO after boot lasts until the next provision/boot; no sticky “Susan toggled” flag (Boundaries: do not rewrite every historical row; no new pattern). AC6 (flip AUTO + Run in CLICK) remains admin/UI + existing dispatch paths — out of this ticket’s code changes beyond not removing those capabilities.

## Stage 3: Canon statute `astral.dispatch.seed-auto-false`

**Done when:** Active statute file exists at the SCHEMA path; README harvested table + HARVEST crosswalk list it; id is `astral.dispatch.seed-auto-false`.

1. Create directory `canon/statutes/astral/dispatch/` if missing.
2. Create `canon/statutes/astral/dispatch/astral.dispatch.seed-auto-false.md` with YAML frontmatter (all SCHEMA keys, no extras):

```yaml
---
id: astral.dispatch.seed-auto-false
title: Seeded dispatch tasks are auto=false
tier: scoped
checkable: judgment
status: active
applies_when:
  layers: ["core", "utils"]
  paths: ["src/core/dispatcher.py", "src/utils/config.py"]
  change_types: ["add", "modify"]
source_docs:
  - docs/features/foundation/ast-1098-seed-gaze-email-click-statute-seed-auto-false.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-31"
---
```

3. Body sections in SCHEMA order:

   - `# Statement` — Product seed/provision paths that insert or reconcile `dispatch_task` rows must leave `auto_mode` false (CLICK). Operators may turn AUTO on later via Task Dispatcher; seed paths must not write Auto true.
   - `## Rationale` — AUTO-true seeds (e.g. shared `gaze_email`) cause every-tick scheduler claims; failures then drown deploy logs. Seed law is CLICK; AUTO is an operator choice after seed.
   - `## Examples` / `### Conforming` — `GAZE_EMAIL_CONFIG["auto_mode"]` false; `ensure_gaze_email_dispatch_task` inserts/reconciles CLICK; meteorite/stage seed catalogs seed false.
   - `### Violating` — Config or ensure path inserts a new `dispatch_task` with `auto_mode` true; provision skips correcting a shared bad-seed AUTO-on `gaze_email` row.
   - Optional `## Notes` — Admin create/PATCH may still set AUTO true after seed (not a seed path). Does not require rewriting every historical row beyond shared `gaze_email` reconcile. Archie approved id on parent AST-1093 (2026-07-31).

4. In `canon/statutes/README.md`, add a harvested-corpus table row for this statute (alphabetically near other `astral.dispatch.*` / after `astral.debug.*` as fits the existing table order) and bump the active-statute count text from **56** to **57**.
5. In `canon/statutes/HARVEST.md`, add one crosswalk row, e.g. `| create (AST-1098) | \`astral.dispatch.seed-auto-false\` | scoped | judgment | AST-1093 / AST-1098 | \`astral/dispatch/astral.dispatch.seed-auto-false.md\` |`, and update the **Counts** line to include this create (56→57 active mappings).

⚠️ **Decision:** Domain folder is `dispatch` (new under `astral/`) — matches id `astral.dispatch.seed-auto-false` per AUTHORING. `approved_by: Archie` / `approved_at: 2026-07-31` per parent Architectural definition (Archie approved via comment 2026-07-31) and AUTHORING lifecycle.

## Execution contract

- Stages in order; one commit per stage on the epic worktree sub branch; publish to `origin/<publish-ref>` after each stage per build-child.
- No files outside the Files Changed table.
- Ambiguity or codebase drift → stop and comment on **parent** AST-1093 with the Stage N blocked template.
- Leave Gmail scopes, Railway log severity, `gaze_email` runner, Ruth parse, and Manage Email UI untouched.

## Self-Assessment

**Scope:** `Single-Component` — config seed literal + one ensure reconcile path + one new statute (+ README/HARVEST register). No schema migration, no UI, no Gmail/external.

**Conf:** `high` — flip known `True` seed; `update_dispatch_task` already whitelists `auto_mode`; statute shape copies SCHEMA exemplars; Archie already named the id.

**Risk:** `Medium` — wrong reconcile could fight operator AUTO across every boot for this shared row (documented Decision); forgetting README/HARVEST register leaves Joan/Radia corpus incomplete; touching other provision loops would expand epic Boundaries.

## Self-review vs ASTRAL_CODE_RULES

- **§2.1 / config-source-of-truth / pattern.config.config-block:** `auto_mode` default stays in `GAZE_EMAIL_CONFIG`; ensure reads config.
- **§1.4 / no-hardcoded-sets:** Desired CLICK comes from config bool, not a stray `False` literal beside an unrelated key (insert still uses `bool(GAZE_EMAIL_CONFIG["auto_mode"])`; reconcile writes `False` only to enforce seed law matching config — acceptable because config assert requires False).
- **§3.3 imports:** core→data for `update_dispatch_task` already established; no new layer violations.
- **in-scope-only:** No Gmail remint, no Railway severity, no runner/Ruth/UI redesign.
- **Statute AUTHORING:** active + Archie approved; no draft status in-repo.
- **No conflict requiring conf-!!-NONE.**

## Review

**Publish ref:** `origin/sub/AST-1093/AST-1098-seed-gaze-email-click-statute-seed-auto-false`
**Tip:** `927ce685`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `c9ed3be6` | GAZE_EMAIL_CONFIG seed auto_mode CLICK |
| 2 | `93538a82` | reconcile shared gaze_email AUTO to CLICK |
| 3 | `927ce685` | statute astral.dispatch.seed-auto-false + register |

## Review (Radia — code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1098
**Publish ref tip (at review):** `2230461251bf6e1991a3b57254c15f6012ddec85`
**Overall:** CLEAN

### What’s solid

- Stages 1–3 match plan: `GAZE_EMAIL_CONFIG["auto_mode"]=False` + seed catalog asserts; ensure insert from config + reconcile stuck AUTO→CLICK; statute `astral.dispatch.seed-auto-false` with Archie approval + README/HARVEST 57.
- Betty `test` + one `merge-tests(AST-1098)` SHA on the sub.

### Issues

**discuss (straggler):** Joan Excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`; tip three-dot includes `docs/features/**` + Betty test-tree so sweep scores them in-scope (all still **conforms**).

**advisory:** Joan’s boot-reconcile tradeoff (operator AUTO on shared `gaze_email` does not survive next ensure) is intentional per plan Decision. Provision INFO log still omits `reconciled=` (return shape has it).

### Recommended actions

None for fix-now.

### Statutes checked (summary)

57 active statutes swept vs `origin/dev...origin/sub/AST-1093/AST-1098-…`. No violates. Full table in Linear review comment.

## Resolution

**Date:** 2026-07-31  
**Publish tip before resolve:** `d89d0793` (`docs(AST-1098): Radia review — CLEAN with Joan straggler discuss`)

Radia overall **CLEAN** — no fix-now product or plan-doc edits.

| Finding | Disposition |
|---------|-------------|
| discuss (Joan Excluded stragglers on three-dot tip) | Accepted as non-blocking; statutes still **conforms**; no product change |
| advisory (boot-reconcile clears operator AUTO; provision INFO omits `reconciled=`) | Accepted — boot-reconcile matches plan Decision / AC3; log field optional, not fix-now |

No product commits on this resolve pass. Merge of `origin/dev` kept Betty AST-1098 test tip (engineer hook excludes foreign test-tree paths from the merge commit).
